#!/usr/bin/env python3
"""The size of the B2 leg of "Supported", for B1 and for `gbm_funding` (#922, H1; finding #913).

A development measurement, never a verdict, and no decided value moves: `scoring_protocol.CRITICAL_VALUES`,
`scoring_protocol.py` and `docs/decisions/scoring-protocol.md` are only read. `verdict` passes the leg against B2 when
`against_b2.lower_bound(critical) > 0`; that test has d = S(B2) - S(candidate). When the candidate's true skill against
B2 is zero, the share of windows that pass is the leg's size. It is the share of
`scoring_protocol.window_t_statistics` of the centred d above the critical value, as #913 counted it.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    for h in 1 2 3 4 5: OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/spread_distribution_634.py walk \\
        --variant gbm_funding --horizon $h --published PUB.csv --panel PUB.csv --output OUT/gbm_funding_h$h.json
    PYTHONPATH=src python3 scripts/b2_leg_size_922.py run --published PUB.csv --walks OUT --output OUT/size.json
    python3 scripts/b2_leg_size_922.py report OUT/size.json
    python3 scripts/b2_leg_size_922.py check

`run` writes the record; `report` copies it to `docs/research/b2-leg-size-922/result.json` and writes the page
`docs/research/b2-leg-size-922-result.md` from it; `check` fails when the page is not what the record gives.
The candidate series: `B1` on every development decision day with its fifth target on or before 2026-09-03 (the
series of #913), `B1 (walk days)` on the days `gbm_funding`'s walks cover (fifth target on or before 2025-12-31), and
`gbm_funding` on those days, its missing forecasts filled by B1 as the protocol does. Histories: `full`, `without
2019-09-18` (the one day with d = +290.7 in #913's orientation; a diagnostic, the protocol never trims) and
`post-2020-04` (decision days from two years after the panel's first row, as #699 and `protocol_coverage.py`). No day after
2025-12-31 is scored for `gbm_funding`; the B1 series of #913 runs to 2026-09-03 as #913's does.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402

RESEARCH = REPO / "docs" / "research"
RECORD = RESEARCH / "b2-leg-size-922" / "result.json"
PAGE = RESEARCH / "b2-leg-size-922-result.md"
AMENDED_RECORD = RESEARCH / "protocol-calibration-873" / "result.json"
WINDOWS = 20_000
SEED = 1
DAYS = (250, 125)
DEVELOPMENT_FIRST = date(2018, 6, 29)
DEVELOPMENT_LAST = date(2026, 9, 3)
WALKS_LAST = date(2025, 12, 31)
EXCLUDED_DAY = date(2019, 9, 18)
HISTORIES = ("full", "without 2019-09-18", "post-2020-04")
CANDIDATES = ("B1", "B1 (walk days)", "gbm_funding")
#: #913's table, the check on row (a): history, days -> (amended, earlier) size.
REPRODUCES = {("full", 250): (0.245, 0.0485), ("full", 125): (0.031, 0.0055), ("without 2019-09-18", 250): (0.130, 0.016)}


def _load(name):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


def leg_differences(b2, candidate):
    """d_t = S(B2) - S(candidate): the orientation of `PairedTest` against B2, positive favouring the candidate."""

    return [b - c for b, c in zip(b2, candidate)]


def share_above(sorted_statistics, critical):
    """The share of the statistics strictly above `critical` (the windows whose lower bound is above zero)."""

    if not sorted_statistics:
        return 0.0
    return sum(1 for t in sorted_statistics if t > critical) / len(sorted_statistics)


def leg_size(differences, *, days, critical, windows, seed):
    """The share of windows of `days` days of the centred `differences` above each value of `critical`."""

    statistics = sp.window_t_statistics(differences, days=days, windows=windows, seed=seed)
    return [share_above(statistics, value) for value in critical]


def critical_values():
    """(amended, earlier) value per window length: the amended from the #873 record, the earlier from the protocol."""

    amended = json.loads(AMENDED_RECORD.read_text(encoding="utf-8"))["comparison_critical_values"]["B2-B1"]
    return ({n: amended[str(n)] for n in DAYS}, {n: sp.CRITICAL_VALUES[sp.GRID_COMPARISON][n] for n in DAYS})


def series(published, walks_dir):
    """{candidate: [(decision day, S(B2) - S(candidate))...]} in date order, on the days described in the docstring."""

    from repo_model.data import audit_panel, load_daily_panel
    from repo_model.evaluation_splits import load_split_declaration

    sd = _load("spread_distribution_634")
    rows = load_daily_panel(published)
    audit_panel(rows)
    calendar = [row.date for row in rows]
    position = {day: i for i, day in enumerate(calendar)}
    outcomes = {row.date: row.spread_bps for row in rows}
    registry = json.loads((REPO / "metadata" / "sources.json").read_text(encoding="utf-8"))
    splits = load_split_declaration(REPO / "metadata" / "evaluation_splits.json")
    settings = {"registry": registry, "decision_time": sd.DECISION}
    decisions = [
        day for i, day in enumerate(calendar)
        if DEVELOPMENT_FIRST <= day and i + 5 < len(calendar) and calendar[i + 5] <= DEVELOPMENT_LAST
    ]
    b1 = pb.forecasts(pb.b1_forecast, rows, decisions, **settings)
    b2 = pb.forecasts(pb.b2_forecast, rows, decisions, splits=splits, **settings)
    s1, s2 = sp.day_scores(b1, outcomes, calendar), sp.day_scores(b2, outcomes, calendar)
    laws, covered = sd.lead_forecasts(sd.load_laws(walks_dir, "gbm_funding"), calendar)
    walk_days = [d for d in covered if d in s1 and calendar[position[d] + 5] <= WALKS_LAST]
    filled = sp.fill_missing({d: laws[d] for d in walk_days}, b1, walk_days)
    s_gbm = sp.day_scores(filled.forecasts, outcomes, calendar)
    first = pb.years_before(rows[0].date, -pb.B1_YEARS)
    out = {
        "B1": [(d, s2[d] - s1[d]) for d in sorted(s1)],
        "B1 (walk days)": [(d, s2[d] - s1[d]) for d in sorted(walk_days)],
        "gbm_funding": [(d, s2[d] - s_gbm[d]) for d in sorted(walk_days)],
    }
    return out, first, {"missing_days": len(filled.missing_days), "missing_share": filled.missing_share}


def history(pairs, name, first):
    if name == "without 2019-09-18":
        return [v for d, v in pairs if d != EXCLUDED_DAY]
    if name == "post-2020-04":
        return [v for d, v in pairs if d >= first]
    return [v for _, v in pairs]


def run_command(args) -> int:
    amended, earlier = critical_values()
    data, first, missing = series(args.published, args.walks)
    out = {"windows": WINDOWS, "seed": SEED, "amended": {str(n): v for n, v in amended.items()},
           "earlier": {str(n): v for n, v in earlier.items()}, "post_2020_first_decision_day": first.isoformat(),
           "gbm_funding_missing": missing, "cells": {}}
    for candidate in CANDIDATES:
        for name in HISTORIES:
            d = [(day, v) for day, v in data[candidate]]
            values = history(d, name, first)
            for n in DAYS:
                size = leg_size(values, days=n, critical=[amended[n], earlier[n]], windows=WINDOWS, seed=SEED)
                out["cells"][f"{candidate}|{name}|{n}"] = {
                    "series_days": len(values), "mean_d": sum(values) / len(values), "amended": size[0], "earlier": size[1]}
                print(json.dumps({"cell": f"{candidate}|{name}|{n}", **out["cells"][f"{candidate}|{name}|{n}"]}), flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def se(p):
    return math.sqrt(p * (1 - p) / WINDOWS)


def pct(p):
    return f"{100 * p:.1f}% ± {196 * se(p):.1f}"


def reproduction(record):
    """Row (a) against #913's figures: each (history, days) -> (our share, #913's, within the Monte Carlo error)."""

    rows = []
    for (name, n), (amended, earlier) in REPRODUCES.items():
        cell = record["cells"][f"B1|{name}|{n}"]
        for label, ours, theirs in (("amended", cell["amended"], amended), ("earlier", cell["earlier"], earlier)):
            # #913 states no seed, so its figure is a second, independent draw of 20,000 windows: the difference of two
            # estimates has the standard error sqrt(2) times one's. It prints to three significant places (+ 0.0005).
            tolerance = 1.96 * math.sqrt(2) * se(max(ours, 1e-6)) + 0.0005
            rows.append((name, n, label, ours, theirs, abs(ours - theirs) <= tolerance))
    return rows


def render(record):
    ok = all(r[-1] for r in reproduction(record))
    lines = [
        "# The size of the B2 leg of \"Supported\" (#922, H1; finding #913)", "",
        "**Development data only; no verdict, no lockbox day scored, and no decided value moves.** `CRITICAL_VALUES`, "
        "`scoring_protocol.py` and `docs/decisions/scoring-protocol.md` are unchanged by this pull request. Every figure is "
        "read from `docs/research/b2-leg-size-922/result.json` by `scripts/b2_leg_size_922.py report`. Whether and how the "
        "critical value is recalibrated is Eleonora's (#913, ruling 5, the #878 amendment); this page gives her the number.", "",
        "## Method", "",
        f"`verdict` passes the leg against B2 when `against_b2.lower_bound(critical) > 0`, with d = S(B2) − S(candidate). With "
        f"no true skill against B2, the share of windows that pass is the leg's size. Each cell is the share of "
        f"{record['windows']:,} windows (seed {record['seed']}) of the stated length, from `scoring_protocol.window_t_statistics` "
        "of the centred d, whose studentized mean is above the value; ± is 1.96 Monte Carlo standard errors. The nominal "
        "size of the 250-day value is 4.8% and of the 125-day value 0.56%. The amended values are "
        f"{record['amended']['250']:.3f} at 250 days and {record['amended']['125']:.3f} at 125 (the record of #873); the earlier ones "
        f"{record['earlier']['250']:.3f} and {record['earlier']['125']:.3f} (the values in force). Histories: `full` (decision days "
        "from 2018-06-29), `without 2019-09-18` (a diagnostic, the protocol never trims) and `post-2020-04` (decision days "
        f"from {record['post_2020_first_decision_day']}, where every confirmation day falls). `B1` runs to 2026-09-03 as #913's "
        "does; `B1 (walk days)` and `gbm_funding` are on the days `gbm_funding`'s walks cover (fifth target on or before "
        f"2025-12-31), its missing forecasts ({record['gbm_funding_missing']['missing_days']} decision days) filled by B1.", "",
        "## 1. Row (a) reproduces #913", "",
        "#913 states no seed, so its figures are an independent draw of the same number of windows: \"within the Monte Carlo error\" "
        "is 1.96 × √2 standard errors of one estimate (plus 0.05 points for #913's rounding).", "",
        "| history | days | value | here | #913 | within the Monte Carlo error of two draws |", "|---|---|---|---|---|---|",
    ]
    for name, n, label, ours, theirs, within in reproduction(record):
        lines.append(f"| {name} | {n} | {label} | {pct(ours)} | {100 * theirs:.2f}% | {'yes' if within else 'NO'} |")
    lines += ["", "Row (a) " + ("reproduces #913's figures." if ok else "does NOT reproduce #913's figures; the rest is not to be read."), "",
              "## 2. The size of the B2 leg", "",
              "| candidate | history | days | series days | amended value | earlier value |", "|---|---|---|---|---|---|"]
    for candidate in CANDIDATES:
        for name in HISTORIES:
            for n in DAYS:
                c = record["cells"][f"{candidate}|{name}|{n}"]
                lines.append(f"| {candidate} | {name} | {n} | {c['series_days']} | {pct(c['amended'])} | {pct(c['earlier'])} |")
    gbm, b1 = record["cells"], record["cells"]
    lines += ["", "## 3. What the table shows", "",
              f"At the amended values, for a candidate with no skill against B2, the B2 leg passes in {pct(b1['B1|full|250']['amended'])} of "
              f"250-day windows when the candidate is B1 and in {pct(gbm['gbm_funding|full|250']['amended'])} when it is `gbm_funding`, "
              f"on the full history; on post-2020-04 history they are {pct(b1['B1|post-2020-04|250']['amended'])} and "
              f"{pct(gbm['gbm_funding|post-2020-04|250']['amended'])}. At the earlier values the same cells are "
              f"{pct(b1['B1|full|250']['earlier'])}, {pct(gbm['gbm_funding|full|250']['earlier'])}, "
              f"{pct(b1['B1|post-2020-04|250']['earlier'])} and {pct(gbm['gbm_funding|post-2020-04|250']['earlier'])}. "
              "The size depends on the candidate's own series of d; the two candidates' rows differ.",
              "", "Nothing here is a verdict for a hypothesis; the choice of critical value is Eleonora's (#913).", ""]
    return "\n".join(lines)


def report_command(args) -> int:
    record = json.loads(args.record.read_text(encoding="utf-8"))
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    PAGE.write_text(render(record), encoding="utf-8")
    print("wrote", PAGE)
    return 0


def check_command(_args) -> int:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    if not PAGE.exists() or PAGE.read_text(encoding="utf-8") != render(record):
        print("the page is not what the record gives; run `report`", file=sys.stderr)
        return 1
    print("ok")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--published", type=Path, required=True)
    run.add_argument("--walks", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(func=run_command)
    rep = sub.add_parser("report")
    rep.add_argument("record", type=Path)
    rep.set_defaults(func=report_command)
    sub.add_parser("check").set_defaults(func=check_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
