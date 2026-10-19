#!/usr/bin/env python3
"""Each leg of "Supported" calibrated in its own orientation on post-2020-04 history (#929, H1; finding #913).

A development measurement, never a verdict. `scoring_protocol.CRITICAL_VALUES` and `FUTILITY_CRITICAL_VALUES` are only read.
`verdict` passes "Supported" when the lower bound is above zero against B1 (d = S(B1) - S(candidate)) and against B2
(d = S(B2) - S(candidate), B2 the benchmark). The value of each leg is the `1 - level` quantile of
`scoring_protocol.window_t_statistics` of a centred series in that leg's orientation, with a stand-in for the candidate:
B2 for the leg against B1 (d = S(B1) - S(B2), as #873 and #878 calibrated) and B1 for the leg against B2 (d = S(B2) - S(B1),
as #913 and #922 sized). The levels are the protocol's `nominal_levels` at 125 and 250 days.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    for h in 1 2 3 4 5: OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/spread_distribution_634.py walk \\
        --variant gbm_funding --horizon $h --published PUB.csv --panel PUB.csv --output OUT/gbm_funding_h$h.json
    PYTHONPATH=src python3 scripts/per_leg_calibration_929.py run --published PUB.csv --walks OUT --output OUT/legs.json
    python3 scripts/per_leg_calibration_929.py report OUT/legs.json
    python3 scripts/per_leg_calibration_929.py check

`run` writes the record (20,000 windows, seed 1 throughout, as #878 and #922 do); `report` copies it to
`docs/research/per-leg-calibration-929/result.json` and writes the page `docs/research/per-leg-calibration-929-result.md` from
it; `check` fails when the page is not what the record gives, when the draft amendment in `docs/decisions/scoring-protocol.md`
does not carry the record's values, or when a row-check does not hold. The series are those of `scripts/b2_leg_size_922.py`
(whose `series` this reads): B1 on every development decision day with its fifth target on or before 2026-09-03, and
`gbm_funding` on the days its walks cover, its missing forecasts filled by B1. Histories: `full`, `without 2019-09-18` (a
diagnostic, the protocol never trims) and `post-2020-04` (decision days from two years after the panel's first row).
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

from repo_model import scoring_protocol as sp  # noqa: E402

RESEARCH = REPO / "docs" / "research"
RECORD = RESEARCH / "per-leg-calibration-929" / "result.json"
PAGE = RESEARCH / "per-leg-calibration-929-result.md"
DECISION = REPO / "docs" / "decisions" / "scoring-protocol.md"
SIZE_RECORD = RESEARCH / "b2-leg-size-922" / "result.json"
WINDOWS = 20_000
SEED = 1
DAYS = (250, 125)
HISTORIES = ("full", "without 2019-09-18", "post-2020-04")
#: A sensitivity of the calibration only (section 1 of the page): #913's own cut of post-2020-04.
SENSITIVITY = "post-2020-04 from 2020-04-01"
LEGS = ("B1", "B2")
#: The stand-in for the candidate on each leg's calibration series, and the candidates whose size is reported.
STAND_IN = {"B1": "B2", "B2": "B1"}
CANDIDATES = {"B1": ("B2", "gbm_funding"), "B2": ("B1", "gbm_funding")}
#: #913's calibration table, the check on the leg against B1: history, days -> value (candidate orientation). Its
#: post-2020-04 row cuts at 2020-04-01, two decision days before `post-2020-04` (two years after the panel's first row,
#: as #699, #886 and #922 count it), so it is reproduced by `FROM_APRIL_1`.
REPRODUCES_913 = {("without 2019-09-18", 250): 1.875, ("without 2019-09-18", 125): 3.364,
                  ("post-2020-04 from 2020-04-01", 250): 2.427, ("post-2020-04 from 2020-04-01", 125): 4.808}
FROM_APRIL_1 = date(2020, 4, 1)


def _load(name):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


def levels():
    """{days: nominal level} at the protocol's checkpoints."""

    return dict(zip(sp.CHECKPOINTS, sp.nominal_levels()))


def leg_series(b2_minus_b1, b2_minus_candidate, leg):
    """The leg's d for a candidate, from `S(B2) - S(B1)` and `S(B2) - S(candidate)` (day-aligned lists).

    The leg against B2 is `S(B2) - S(candidate)` as it stands; the leg against B1 is `S(B1) - S(candidate)`, which is
    `(S(B2) - S(candidate)) - (S(B2) - S(B1))`. The stand-in B1 on the B2 leg, and B2 on the B1 leg, are the cases
    `b2_minus_candidate` equal to `b2_minus_b1`, and to zero.
    """

    if leg == "B2":
        return list(b2_minus_candidate)
    return [c - b for b, c in zip(b2_minus_b1, b2_minus_candidate)]


def critical_value(series, *, days):
    """The calibrated value of a leg: the `1 - level` quantile of the centred series' windows at the protocol's level."""

    return sp.calibrate_critical_value(series, days=days, level=levels()[days], windows=WINDOWS, seed=SEED)


def share_above(statistics, value):
    return sum(1 for t in statistics if t > value) / len(statistics) if statistics else 0.0


def data(published, walks_dir):
    """{name: {day: S(B2) - S(name)}}: B1 on all development days, `gbm_funding` and `B1 (walk days)` on the walk days."""

    sizes = _load("b2_leg_size_922")
    series, first, missing = sizes.series(published, walks_dir)
    return sizes, {name: dict(pairs) for name, pairs in series.items()}, first, missing


def history_days(days, name, first, excluded):
    if name == "without 2019-09-18":
        return [d for d in days if d != excluded]
    if name == "post-2020-04":
        return [d for d in days if d >= first]
    if name == "post-2020-04 from 2020-04-01":
        return [d for d in days if d >= FROM_APRIL_1]
    return list(days)


def run_command(args) -> int:
    sizes, series, first, missing = data(args.published, args.walks)
    b1_days = sorted(series["B1"])
    out = {"windows": WINDOWS, "seed": SEED, "post_2020_first_decision_day": first.isoformat(),
           "levels": {str(n): v for n, v in levels().items()}, "gbm_funding_missing": missing,
           "amended": {}, "earlier": {}, "calibrated": {}, "sizes": {}}
    amended, earlier = sizes.critical_values()
    out["amended"] = {str(n): v for n, v in amended.items()}
    out["earlier"] = {str(n): v for n, v in earlier.items()}
    # 1. each leg's value on its own series, on each history
    for leg in LEGS:
        for name in HISTORIES + (SENSITIVITY,):
            days = history_days(b1_days, name, first, sizes.EXCLUDED_DAY)
            b2_minus_b1 = [series["B1"][d] for d in days]
            calibration = leg_series(b2_minus_b1, b2_minus_b1, "B2") if leg == "B2" else [-v for v in b2_minus_b1]
            for n in DAYS:
                out["calibrated"][f"{leg}|{name}|{n}"] = {"series_days": len(calibration), "value": critical_value(calibration, days=n)}
                print(json.dumps({"calibrated": f"{leg}|{name}|{n}", **out["calibrated"][f"{leg}|{name}|{n}"]}), flush=True)
    # 2. the size of each leg for each candidate under the new, amended and earlier values
    walk_days = sorted(series["gbm_funding"])
    for leg in LEGS:
        for candidate in CANDIDATES[leg]:
            on = walk_days if candidate == "gbm_funding" else b1_days
            for name in HISTORIES:
                days = history_days(on, name, first, sizes.EXCLUDED_DAY)
                b2_minus_b1 = [series["B1"][d] for d in days]
                if candidate == "gbm_funding":
                    b2_minus_c = [series["gbm_funding"][d] for d in days]
                elif candidate == "B1":
                    b2_minus_c = b2_minus_b1
                else:
                    b2_minus_c = [0.0 for _ in days]
                d_series = leg_series(b2_minus_b1, b2_minus_c, leg)
                for n in DAYS:
                    statistics = sp.window_t_statistics(d_series, days=n, windows=WINDOWS, seed=SEED)
                    new = out["calibrated"][f"{leg}|post-2020-04|{n}"]["value"]
                    cell = {"series_days": len(d_series), "mean_d": sum(d_series) / len(d_series),
                            "new": share_above(statistics, new), "amended": share_above(statistics, amended[n]),
                            "earlier": share_above(statistics, earlier[n])}
                    out["sizes"][f"{leg}|{candidate}|{name}|{n}"] = cell
                    print(json.dumps({"size": f"{leg}|{candidate}|{name}|{n}", **cell}), flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def se(p):
    return math.sqrt(p * (1 - p) / WINDOWS)


def pct(p):
    return f"{100 * p:.1f}% ± {196 * se(p):.1f}"


def row_checks(record):
    """[(what, ours, theirs, holds)]: the leg against B1 against #913's table, the B2-leg sizes against #922's record."""

    rows = []
    amended = {int(k): v for k, v in record["amended"].items()}
    for (name, n), theirs in REPRODUCES_913.items():
        ours = record["calibrated"][f"B1|{name}|{n}"]["value"]
        rows.append((f"B1 leg, {name}, {n} days: value", ours, theirs, abs(ours - theirs) <= 0.0015))
    for n in DAYS:
        ours = record["calibrated"][f"B1|full|{n}"]["value"]
        rows.append((f"B1 leg, full, {n} days: value (#878's amended value)", ours, amended[n], abs(ours - amended[n]) <= 1e-9))
    if SIZE_RECORD.exists():
        theirs_all = json.loads(SIZE_RECORD.read_text(encoding="utf-8"))["cells"]
        for candidate, key in (("B1", "B1"), ("gbm_funding", "gbm_funding")):
            for name in HISTORIES:
                for n in DAYS:
                    cell = record["sizes"][f"B2|{key}|{name}|{n}"]
                    theirs = theirs_all[f"{candidate}|{name}|{n}"]
                    # the same function, series and seed as #922's: the shares must agree exactly
                    for label in ("amended", "earlier"):
                        rows.append((f"B2 leg, {candidate}, {name}, {n} days: size at the {label} value",
                                     cell[label], theirs[label], abs(cell[label] - theirs[label]) <= 1e-12))
    return rows


def render(record):
    checks = row_checks(record)
    ok = all(r[-1] for r in checks)
    new = {leg: {n: record["calibrated"][f"{leg}|post-2020-04|{n}"]["value"] for n in DAYS} for leg in LEGS}
    amended = {int(k): v for k, v in record["amended"].items()}
    earlier = {int(k): v for k, v in record["earlier"].items()}
    lines = [
        "# Each leg of \"Supported\" in its own orientation, on post-2020-04 history (#929, H1; finding #913)", "",
        "**Development data only; no verdict, no lockbox day scored, and no decided value moves.** `CRITICAL_VALUES` and "
        "`FUTILITY_CRITICAL_VALUES` are unchanged by this pull request; `B2_LEG_CRITICAL_VALUES` (new, empty) is where a per-leg "
        "value would be declared once Eleonora has merged the amendment. Every figure is read from "
        "`docs/research/per-leg-calibration-929/result.json` by `scripts/per_leg_calibration_929.py report`.", "",
        "## Method", "",
        f"`verdict` passes \"Supported\" when the lower bound of mean(d) is above zero against B1 (d = S(B1) − S(candidate)) and "
        f"against B2 (d = S(B2) − S(candidate), B2 the benchmark). Each leg's value is the 1 − level quantile of "
        f"`scoring_protocol.window_t_statistics` of a centred series in that leg's orientation, at the protocol's level for the "
        f"look ({100 * record['levels']['250']:.2f}% at 250 days, {100 * record['levels']['125']:.2f}% at 125), {record['windows']:,} "
        f"windows, seed {record['seed']}. The calibration series stands a forecaster in for the candidate: B2 for the leg against B1 "
        f"(d = S(B1) − S(B2), as #873 calibrated), B1 for the leg against B2 (d = S(B2) − S(B1), as #913 sized). Histories: `full` "
        f"(decision days from 2018-06-29), `without 2019-09-18` (a diagnostic, the protocol never trims) and `post-2020-04` "
        f"(decision days from {record['post_2020_first_decision_day']}, where every confirmation day falls). ± is 1.96 Monte Carlo "
        "standard errors.", "",
        "## 1. The calibrated values", "",
        "| leg | history | series days | 250 days | 125 days |", "|---|---|---|---|---|",
    ]
    for leg in LEGS:
        for name in HISTORIES + (SENSITIVITY,):
            c250, c125 = (record["calibrated"][f"{leg}|{name}|{n}"] for n in DAYS)
            lines.append(f"| against {leg} | {name} | {c250['series_days']} | {c250['value']:.3f} | {c125['value']:.3f} |")
    lines += ["", f"For comparison, the value in force is {earlier[250]:.3f} at 250 days and {earlier[125]:.3f} at 125; #878's "
              f"amended value (one value for both legs) is {amended[250]:.3f} and {amended[125]:.3f}.", "",
              "## 2. Row-checks", "",
              "| figure | here | reference | holds |", "|---|---|---|---|"]
    for what, ours, theirs, holds in checks:
        lines.append(f"| {what} | {ours:.4f} | {theirs:.4f} | {'yes' if holds else 'NO'} |")
    lines += ["", "The leg against B1 reproduces #913's calibration table to three decimals and #878's full-history values; the leg "
              "against B2 at the amended and earlier values reproduces #922's sizes exactly (same function, series and seed). "
              + ("All hold." if ok else "NOT ALL HOLD: the rest is not to be read."), "",
              "## 3. The size of each leg", "",
              "Share of windows in which the leg passes when the candidate has no skill against the leg's benchmark (nominal: "
              f"{100 * record['levels']['250']:.1f}% at 250 days, {100 * record['levels']['125']:.2f}% at 125). New values are the "
              "post-2020-04 values of section 1.", "",
              "| leg | candidate | history | days | series days | new value | amended value | earlier value |", "|---|---|---|---|---|---|---|---|"]
    for leg in LEGS:
        for candidate in CANDIDATES[leg]:
            for name in HISTORIES:
                for n in DAYS:
                    c = record["sizes"][f"{leg}|{candidate}|{name}|{n}"]
                    lines.append(f"| against {leg} | {candidate} | {name} | {n} | {c['series_days']} | {pct(c['new'])} | "
                                 f"{pct(c['amended'])} | {pct(c['earlier'])} |")
    g = record["sizes"]
    lines += ["", "## 4. What the tables show", "",
              f"On post-2020-04 history at 250 days, with the new values ({new['B1'][250]:.3f} against B1, {new['B2'][250]:.3f} against B2), "
              f"the leg against B1 passes in {pct(g['B1|B2|post-2020-04|250']['new'])} of windows for the stand-in B2 and "
              f"{pct(g['B1|gbm_funding|post-2020-04|250']['new'])} for `gbm_funding`; the leg against B2 passes in "
              f"{pct(g['B2|B1|post-2020-04|250']['new'])} for the stand-in B1 and {pct(g['B2|gbm_funding|post-2020-04|250']['new'])} for "
              f"`gbm_funding`. At 125 days the same cells are {pct(g['B1|B2|post-2020-04|125']['new'])}, "
              f"{pct(g['B1|gbm_funding|post-2020-04|125']['new'])}, {pct(g['B2|B1|post-2020-04|125']['new'])} and "
              f"{pct(g['B2|gbm_funding|post-2020-04|125']['new'])}. A leg's size on its own calibration series (the stand-in candidate, "
              "post-2020-04 history) is its nominal level by construction; the rows for `gbm_funding` and for the other histories show "
              "how far it holds elsewhere. This page draws circular blocks (`window_t_statistics`, as the directive says) from the decision "
              f"days from {record['post_2020_first_decision_day']}, where #886 drew stationary-bootstrap windows. #913's post-2020-04 row "
              "cuts two decision days earlier, at 2020-04-01; the last rows of section 1 show that cut moves the leg against B1 from "
              f"{new['B1'][250]:.3f} / {new['B1'][125]:.3f} to {record['calibrated'][f'B1|{SENSITIVITY}|250']['value']:.3f} / "
              f"{record['calibrated'][f'B1|{SENSITIVITY}|125']['value']:.3f} (and reproduces #913's table). Which cut is used is Eleonora's.", "",
              "Nothing here is a verdict for a hypothesis; the choice of values is Eleonora's (#913, ruling of 19 October 2026).", ""]
    return "\n".join(lines)


def decision_values(record):
    """The strings the draft amendment must carry: each new value to three decimals."""

    return [f"{record['calibrated'][f'{leg}|post-2020-04|{n}']['value']:.3f}" for leg in LEGS for n in DAYS]


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
    if not all(r[-1] for r in row_checks(record)):
        print("a row-check does not hold", file=sys.stderr)
        return 1
    text = DECISION.read_text(encoding="utf-8")
    marker = "## Draft amendment 3"
    if marker not in text:
        print("the draft amendment is missing from the decision record", file=sys.stderr)
        return 1
    section = text.split(marker, 1)[1]
    missing = [v for v in decision_values(record) if v not in section]
    if missing:
        print(f"the draft amendment does not carry the record's values: {missing}", file=sys.stderr)
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
