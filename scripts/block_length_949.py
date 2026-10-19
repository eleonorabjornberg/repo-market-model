#!/usr/bin/env python3
"""H1 step 3 (#949): does the protocol's mean block of 10 suit H5's paired CRPS loss differentials?

A report that changes nothing: `scoring_protocol.BLOCK_LENGTH` stays 10 and so does `docs/decisions/scoring-protocol.md`
section 5. Development days only (no day after 2025-12-31, no lockbox day), from the walks of `gbm_funding`; nothing is
refitted here beyond the walks `run` reads.

For d_t = S(B) - S(`gbm_funding`), with B = B1 and with B = B2, on the days the walks cover, it measures
- the autocorrelation function of d_t at lags 1-10, at each lead h = 1-5 and for the lead-averaged d_t (the series the
  protocol tests);
- the Politis-White automatic block length for the stationary bootstrap (Politis and White 2004, with the correction of
  Patton, Politis and White 2009), for the same series;
- the paired interval, from `scoring_protocol.paired_tests`, at mean block 5, 10 and 20.
Pooled, by regime and by the reporting day type of the decision day. The ACF and the block length are read on series that
are consecutive days: pooled, and by regime. A day type's days are not consecutive, so for them only the interval is given.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    for h in 1 2 3 4 5: OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/spread_distribution_634.py walk \\
        --variant gbm_funding --horizon $h --published PUB.csv --panel PUB.csv --output OUT/gbm_funding_h$h.json
    PYTHONPATH=src python3 scripts/block_length_949.py run --published PUB.csv --walks OUT --output OUT/block.json
    python3 scripts/block_length_949.py report OUT/block.json
    python3 scripts/block_length_949.py check

`run` writes the record; `report` copies it to `docs/research/block-length-949/result.json` and writes the page
`docs/research/block-length-949-result.md`; `check` fails when the page is not what the record gives. The walks are
`gbm_funding`'s, as #922's: a decision day is scored when its five targets are in the walks and its fifth target is on or
before 2025-12-31; a missing forecast is B1's (section 11).
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import date
from pathlib import Path
from typing import Dict, List, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import lockbox, protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402

RESEARCH = REPO / "docs" / "research"
RECORD = RESEARCH / "block-length-949" / "result.json"
PAGE = RESEARCH / "block-length-949-result.md"
B2_LEG_RECORD = RESEARCH / "b2-leg-size-922" / "result.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
SOURCES = REPO / "metadata" / "sources.json"
PROTOCOL_BLOCK = 10
BLOCKS = (5, 10, 20)
LAGS = 10
LEADS = sp.HORIZONS
COMPARISONS = ("B1", "B2")
DEVELOPMENT_FIRST = date(2018, 6, 29)
WALKS_LAST = date(2025, 12, 31)
SEED = 1
HEADLINE_DRAWS = 10_000
SPLIT_DRAWS = 4_000
MINIMUM_DAYS = 60
#: The reproduction check: S(B2) - S(gbm_funding), lead-averaged, over the same days, is #922's recorded mean.
REPRODUCTION_TOLERANCE = 1e-9


def _load(name):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


# -- the two new pieces -----------------------------------------------------------------------------------------------


def acf(values: Sequence[float], max_lag: int) -> List[float]:
    """The sample autocorrelations rho(1) ... rho(max_lag) of `values`, about their mean."""

    n = len(values)
    if n <= max_lag + 1:
        raise ValueError(f"a series of {n} values has no autocorrelation to lag {max_lag}")
    mean = sum(values) / n
    centred = [v - mean for v in values]
    gamma0 = sum(c * c for c in centred) / n
    if gamma0 == 0.0:
        raise ValueError("a constant series has no autocorrelation")
    return [sum(centred[i] * centred[i + k] for i in range(n - k)) / n / gamma0 for k in range(1, max_lag + 1)]


def politis_white(values: Sequence[float]) -> float:
    """The automatic mean block length of the stationary bootstrap for the mean of `values`.

    Politis and White (2004), with the correction of Patton, Politis and White (2009): the lag window is flat-topped,
    lambda(t) = 1 for |t| <= 1/2 and 2 (1 - |t|) up to 1; the truncation M is twice the first lag after which K_N
    autocorrelations are all inside the band c * sqrt(log10(N) / N), c = 2, capped at ceil(sqrt(N)) + K_N; and
    b = (2 G^2 / D)^(1/3) N^(1/3) with G = sum lambda(k/M) |k| gamma(k) and D = 2 g(0)^2, g(0) = sum lambda(k/M) gamma(k).
    """

    n = len(values)
    if n < 20:
        raise ValueError(f"a series of {n} values is too short for an automatic block length")
    k_n = max(5, int(math.ceil(math.sqrt(math.log10(n)))))
    m_max = int(math.ceil(math.sqrt(n))) + k_n
    rho = acf(values, m_max + k_n)
    band = 2.0 * math.sqrt(math.log10(n) / n)
    m_hat = 0
    for m in range(0, m_max + 1):
        window = rho[m:m + k_n]  # rho(m + 1) ... rho(m + k_n)
        if all(abs(r) < band for r in window):
            m_hat = m
            break
    else:
        m_hat = m_max
    big_m = min(2 * max(m_hat, 1), m_max)
    mean = sum(values) / n
    centred = [v - mean for v in values]
    gamma0 = sum(c * c for c in centred) / n

    def lam(t: float) -> float:
        t = abs(t)
        return 1.0 if t <= 0.5 else (2.0 * (1.0 - t) if t <= 1.0 else 0.0)

    g0, big_g = gamma0, 0.0
    for k in range(1, big_m + 1):
        weight = lam(k / big_m)
        gamma_k = rho[k - 1] * gamma0
        g0 += 2.0 * weight * gamma_k
        big_g += 2.0 * weight * k * gamma_k
    d_sb = 2.0 * g0 * g0
    if d_sb <= 0.0:
        return 1.0
    return max(1.0, (2.0 * big_g * big_g / d_sb) ** (1.0 / 3.0) * n ** (1.0 / 3.0))


# -- the data -----------------------------------------------------------------------------------------------------------


def panel_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def series(published: Path, walks: Path):
    """{comparison: {lead or 'avg': {day: d}}}, the decision days with their regime and day type, and the walk's missing count."""

    from repo_model.data import audit_panel, load_daily_panel
    from repo_model.evaluation_splits import load_split_declaration

    sd = _load("spread_distribution_634")
    rows = load_daily_panel(published)
    audit_panel(rows)
    calendar = [row.date for row in rows]
    position = {day: i for i, day in enumerate(calendar)}
    outcomes = {row.date: row.spread_bps for row in rows}
    row_of = {row.date: row for row in rows}
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    splits = load_split_declaration(SPLITS)
    settings = {"registry": registry, "decision_time": sd.DECISION}
    laws, covered = sd.lead_forecasts(sd.load_laws(walks, "gbm_funding"), calendar)
    days = [d for d in covered if d >= DEVELOPMENT_FIRST and calendar[position[d] + 5] <= WALKS_LAST]
    targets = {d: {h: calendar[position[d] + h] for h in LEADS} for d in days}
    lockbox.require_unlocked(set(days) | {t for per in targets.values() for t in per.values()}, where="block_length_949")
    b1 = pb.forecasts(pb.b1_forecast, rows, days, **settings)
    b2 = pb.forecasts(pb.b2_forecast, rows, days, splits=splits, **settings)
    filled = sp.fill_missing({d: laws[d] for d in days}, b1, days)
    models = {"B1": b1, "B2": b2, "gbm_funding": filled.forecasts}
    cells: Dict[str, Dict[int, Dict[date, float]]] = {}
    for name, forecasts in models.items():
        cells[name] = {h: {d: sp.grid_crps(forecasts[d][h], outcomes[targets[d][h]]) for d in days
                           if outcomes.get(targets[d][h]) is not None} for h in LEADS}
    averaged = {name: sp.day_scores(models[name], outcomes, calendar) for name in models}
    out: Dict[str, Dict[str, Dict[date, float]]] = {}
    for b in COMPARISONS:
        out[b] = {}
        for h in LEADS:
            common = [d for d in days if d in cells[b][h] and d in cells["gbm_funding"][h]]
            out[b][str(h)] = {d: cells[b][h][d] - cells["gbm_funding"][h][d] for d in common}
        out[b]["avg"] = {d: averaged[b][d] - averaged["gbm_funding"][d] for d in days if d in averaged[b] and d in averaged["gbm_funding"]}
    meta = {
        "regime": {d: splits.regime(d) for d in days},
        "kind": {d: splits.reporting_day_type(d, row_of[d].values) for d in days},
        "regimes": list(splits.regime_labels),
        "missing": {"days": len(filled.missing_days), "share": filled.missing_share},
        "days": days,
    }
    return out, meta


def _interval_job(job):
    """One group's paired interval at each block: (key, b, d series as (day, S(B), S(candidate)) -> row)."""

    key, draws, pairs = job
    benchmark = {day: sb for day, sb, _ in pairs}
    candidate = {day: sc for day, _, sc in pairs}
    row = {}
    for block in BLOCKS:
        (test,) = sp.paired_tests([(benchmark, candidate)], seed=SEED, draws=draws, block_length=float(block), with_skill=False)
        row[str(block)] = {"lower_95": test.lower_mean_difference(0.05), "upper_95": test.lower_mean_difference(0.95),
                           "se": test.standard_error, "mean": test.mean_difference, "dm": test.dm_statistic}
    return key, row


def run_command(args) -> int:
    d_series, meta = series(args.published, args.walks)
    sd_days = meta["days"]
    # the intervals need S(B) and S(candidate), not just d: rebuild them from d with the candidate's score as zero
    # reference (a paired test reads only the difference), so `PairedTest` sees d = S(B) - S(candidate) exactly
    record: Dict[str, object] = {
        "seed": SEED, "draws": {"headline": HEADLINE_DRAWS, "splits": SPLIT_DRAWS}, "blocks": list(BLOCKS), "lags": LAGS,
        "protocol_block": sp.BLOCK_LENGTH, "panel_sha256": panel_sha256(args.published),
        "decision_days": {"n": len(sd_days), "first": sd_days[0].isoformat(), "last": sd_days[-1].isoformat()},
        "gbm_funding_missing": meta["missing"], "regimes": meta["regimes"],
        "kinds": sorted(set(meta["kind"].values())), "comparisons": {},
    }
    recorded = json.loads(B2_LEG_RECORD.read_text(encoding="utf-8"))["cells"]["gbm_funding|full|250"]
    mean_b2 = sum(d_series["B2"]["avg"].values()) / len(d_series["B2"]["avg"])
    record["reproduces_922"] = {"recomputed": mean_b2, "recorded": recorded["mean_d"], "days": len(d_series["B2"]["avg"]),
                                "recorded_days": recorded["series_days"]}
    if abs(mean_b2 - recorded["mean_d"]) > REPRODUCTION_TOLERANCE or len(d_series["B2"]["avg"]) != recorded["series_days"]:
        raise ValueError(f"mean S(B2) - S(gbm_funding) is {mean_b2} over {len(d_series['B2']['avg'])} days here and "
                         f"{recorded['mean_d']} over {recorded['series_days']} in #922's record")
    jobs, shells = [], {}
    for b in COMPARISONS:
        for lead, d in d_series[b].items():
            days = sorted(d)
            groups = {"all": days}
            for label in meta["regimes"]:
                groups[f"regime {label}"] = [x for x in days if meta["regime"][x] == label]
            if lead == "avg":
                for kind in record["kinds"]:
                    groups[f"day type {kind}"] = [x for x in days if meta["kind"][x] == kind]
            for name, chosen in groups.items():
                entry = {"n": len(chosen)}
                if len(chosen) >= MINIMUM_DAYS and not name.startswith("day type"):
                    values = [d[x] for x in chosen]
                    entry["mean_d"] = sum(values) / len(values)
                    entry["acf"] = acf(values, LAGS)
                    entry["politis_white"] = politis_white(values)
                elif len(chosen) < MINIMUM_DAYS:
                    entry["thin"] = True
                shells[(b, lead, name)] = entry
                if len(chosen) >= MINIMUM_DAYS and lead == "avg":
                    # d = S(B) - S(candidate): carry S(B) = d and S(candidate) = 0
                    jobs.append(((b, lead, name), HEADLINE_DRAWS if name == "all" else SPLIT_DRAWS,
                                 [(x, d[x], 0.0) for x in chosen]))
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for key, row in pool.map(_interval_job, jobs):
            shells[key]["intervals"] = row
    for (b, lead, name), entry in shells.items():
        record["comparisons"].setdefault(b, {}).setdefault(lead, {})[name] = entry
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "decision_days": len(sd_days)}))
    return 0


# -- the report -----------------------------------------------------------------------------------------------------------


def f(value, digits=2):
    return "n/a" if value is None else f"{value:.{digits}f}"


def render(record) -> str:
    comps = record["comparisons"]
    lines = [
        "# Block length and the autocorrelation of H5's loss differentials (#949, H1 step 3)", "",
        "**Development data, not a verdict.** A report that changes nothing: `scoring_protocol.BLOCK_LENGTH` stays "
        f"{record['protocol_block']} and `docs/decisions/scoring-protocol.md` section 5 is unchanged. No day after 2025-12-31 and no lockbox "
        "day is scored. Every figure is read from `docs/research/block-length-949/result.json` by `scripts/block_length_949.py report`.", "",
        "## Question for Eleonora", "",
        "**Marked question.** Should the stationary bootstrap's mean block change from 10 business days? This page reports "
        "what the loss differentials of `gbm_funding` against B1 and against B2 look like; it does not decide it. The block is "
        "hers to change (a section 13 matter).", "",
        "## Method", "",
        "d_t = S(B) - S(`gbm_funding`) on the grid CRPS, with B = B1 and with B = B2, on the "
        f"{record['decision_days']['n']} decision days {record['decision_days']['first']} to {record['decision_days']['last']} "
        "whose five targets are in `gbm_funding`'s walks and on or before 2025-12-31 (the days of #922; "
        f"{record['gbm_funding_missing']['days']} missing forecasts, filled by B1). The lead-averaged d_t is the series the protocol "
        "tests. The ACF is the sample autocorrelation; the block length is Politis and White's automatic choice for the "
        "stationary bootstrap, with the correction of Patton, Politis and White (2009); both are checked on white noise and on AR(1) series "
        "of known answer in `tests/test_block_length_949.py`. The interval is `scoring_protocol.paired_tests` (studentized "
        f"stationary bootstrap, HAC lag {record['lags']}, seed {record['seed']}, {record['draws']['headline']:,} draws pooled and "
        f"{record['draws']['splits']:,} per split), a one-sided 95% lower and upper bound of mean(d) at mean block 5, 10 and 20. "
        "Regime and day type are those of the decision day (`metadata/evaluation_splits.json`). A day type's days are not consecutive, "
        "so only its interval is given. Groups under 60 days are not tested.", "",
        "Reproduction: mean S(B2) - S(`gbm_funding`) over the same days is "
        f"{record['reproduces_922']['recomputed']:.6f} ({record['reproduces_922']['days']} days) here and "
        f"{record['reproduces_922']['recorded']:.6f} ({record['reproduces_922']['recorded_days']} days) in #922's record.", "",
    ]
    for b in COMPARISONS:
        lines += [f"## d_t = S({b}) - S(gbm_funding)", "", "### Autocorrelation and automatic block length, pooled", "",
                  "| series | days | mean d | " + " | ".join(f"rho({k})" for k in range(1, 6)) + " | rho(10) | Politis-White block |",
                  "|---|---|---|" + "---|" * 5 + "---|---|"]
        for lead in [*map(str, LEADS), "avg"]:
            e = comps[b][lead]["all"]
            lines.append(f"| {'lead-averaged' if lead == 'avg' else 'lead ' + lead} | {e['n']} | {f(e['mean_d'], 3)} | "
                         + " | ".join(f(e['acf'][k], 2) for k in range(5)) + f" | {f(e['acf'][9], 2)} | {f(e['politis_white'], 1)} |")
        lines += ["", "### By regime (lead-averaged)", "",
                  "| regime | days | rho(1) | rho(2) | rho(5) | rho(10) | Politis-White block |", "|---|---|---|---|---|---|---|"]
        for label in record["regimes"]:
            e = comps[b]["avg"][f"regime {label}"]
            if e.get("thin"):
                lines.append(f"| {label} | {e['n']} | too thin | | | | |")
            else:
                lines.append(f"| {label} | {e['n']} | {f(e['acf'][0])} | {f(e['acf'][1])} | {f(e['acf'][4])} | {f(e['acf'][9])} | {f(e['politis_white'], 1)} |")
        lines += ["", "### Paired interval by mean block (lead-averaged; one-sided 95% bounds of mean d, [lower, upper])", "",
                  "| group | days | mean d | block 5 | block 10 (protocol) | block 20 |", "|---|---|---|---|---|---|"]
        groups = ["all", *[f"regime {x}" for x in record["regimes"]], *[f"day type {k}" for k in record["kinds"]]]
        for name in groups:
            e = comps[b]["avg"][name]
            if "intervals" not in e:
                lines.append(f"| {name} | {e['n']} | too thin | | | |")
                continue
            iv = e["intervals"]
            cell = lambda k: f"[{iv[k]['lower_95']:+.3f}, {iv[k]['upper_95']:+.3f}]"  # noqa: E731
            lines.append(f"| {name} | {e['n']} | {iv['10']['mean']:+.3f} | {cell('5')} | {cell('10')} | {cell('20')} |")
        lines.append("")
    lines += ["## Reading", "", "See the pull request for the reading; this page states the figures. The block stays 10 until Eleonora decides.", ""]
    return "\n".join(lines)


def report_command(args) -> int:
    record = json.loads(args.record.read_text(encoding="utf-8"))
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    PAGE.write_text(render(record), encoding="utf-8")
    print("wrote", PAGE)
    return 0


def check_command(_args) -> int:
    if not RECORD.exists():
        print("no record yet: `run` and `report` have not been run", file=sys.stderr)
        return 1
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
    run.add_argument("--workers", type=int, default=4)
    run.set_defaults(func=run_command)
    rep = sub.add_parser("report")
    rep.add_argument("record", type=Path)
    rep.set_defaults(func=report_command)
    sub.add_parser("check").set_defaults(func=check_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
