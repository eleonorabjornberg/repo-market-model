#!/usr/bin/env python3
"""H1 step 3 and H6 step 1 (#963): critical values on contiguous post-2020 windows, event strata and a fixed-b statistic.

A report that changes nothing: `scoring_protocol.CRITICAL_VALUES` and `docs/decisions/scoring-protocol.md` are only read.
Everything it computes is declared in `metadata/contiguous_calibration_963.json`, which `run` refuses to read unless it is
committed and unchanged. Development days only (decision days from 2020-04-03 whose fifth target is on or before
2025-12-31, no lockbox day), from the day scores of B1, B2, `spread_mr_ctx` and `gbm_funding`.

For d = S(B1) - S(candidate), candidate in {B2, `spread_mr_ctx`, `gbm_funding`}, it
- recomputes the critical value c at 125, 250 and 500 days on every contiguous window of the series (no wrap) and, beside
  it, on the stationary-10 and circular-10 generators of #886 and `scoring_protocol.window_t_statistics`, with the size
  of the value in force and the number of non-overlapping windows the series holds;
- restricts the H5 metric to risk-date targets (month-end, quarter-end, tax date, coupon settlement), paired against B1 and
  B2, with the ACF of d between consecutive events and the events per year;
- computes a fixed-b statistic on the last 2 years beside the Newey-West (lag 10) one, and the size of each on the
  contiguous 500-day windows.

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    for h in 1 2 3 4 5: OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/spread_distribution_634.py walk \\
        --variant gbm_funding --horizon $h --published PUB.csv --panel PUB.csv --output OUT/gbm_funding_h$h.json
    PYTHONPATH=src python3 scripts/contiguous_calibration_963.py run --published PUB.csv --walks OUT --output OUT/result.json
    python3 scripts/contiguous_calibration_963.py report OUT/result.json
    python3 scripts/contiguous_calibration_963.py check

`run` writes the record; `report` copies it to `docs/research/contiguous-calibration-963/result.json` and writes the page
`docs/research/contiguous-calibration-963-result.md` from it alone; `check` fails when the page is not what the record gives.
Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import random
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import lockbox, protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model import spread_mr_variants as var  # noqa: E402
# Defined in src so a spawn pool can import the scaled-score workers that read them (#1090).
from repo_model.scaled_score_workers import contiguous_window_statistics, stationary_windows  # noqa: E402,F401

RESEARCH = REPO / "docs" / "research"
DECLARATION = REPO / "metadata" / "contiguous_calibration_963.json"
RECORD = RESEARCH / "contiguous-calibration-963" / "result.json"
PAGE = RESEARCH / "contiguous-calibration-963-result.md"
B2_LEG_RECORD = RESEARCH / "b2-leg-size-922" / "result.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
SOURCES = REPO / "metadata" / "sources.json"

POST_2020_FIRST = date(2020, 4, 3)
DEVELOPMENT_FIRST = date(2018, 6, 29)
LAST_TARGET = date(2025, 12, 31)
WINDOW_DAYS = (125, 250, 500)
CANDIDATES = ("B2", "spread_mr_ctx", "gbm_funding")
GENERATORS = ("contiguous", "stationary_10", "circular_10")
WINDOWS = 20_000
LEVEL = 0.05
SEED = 1
#: The critical values in force for the grid comparison; 500 days has none and is read at the 250-day value.
IN_FORCE = {125: 3.419438620805254, 250: 2.425730476113518, 500: 2.425730476113518}
SURVIVES_BELOW, FAILS_ABOVE = 3.0, 4.0
FIXED_B = 0.1
FIXED_B_DAYS = 500
FIXED_B_DRAWS = 20_000
NORMAL_ONE_SIDED_95 = 1.6448536269514722
STRATA = ("month_end", "quarter_end", "tax_date", "coupon_settlement")
MINIMUM_EVENTS = 30
EVENT_BLOCK = 3.0
EVENT_LAG = 3
EVENT_DRAWS = 10_000
EVENT_ACF_LAGS = 3
REPRODUCTION_TOLERANCE = 1e-9


def _load(name):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


# -- the new pieces -------------------------------------------------------------------------------------------------------


def effective_windows(n: int, days: int) -> float:
    """The non-overlapping windows of `days` days that `n` days hold."""

    return n / days


def fixed_b_statistic(values: Sequence[float], *, b: float = FIXED_B, centre: float = 0.0) -> float:
    """`(mean(values) - centre)` over the Bartlett standard error of bandwidth `M = b * T` (lag `M - 1`).

    Raises:
        ValueError: the bandwidth is below 2 or reaches the sample size.
    """

    n = len(values)
    m = int(round(b * n))
    if m < 2 or m > n:
        raise ValueError(f"a bandwidth of {m} days (b = {b}, T = {n}) is outside [2, T]")
    variance = sp._long_run_variance(list(values), m - 1)
    if variance <= 0.0:
        raise ValueError("the values have no long-run variance")
    return (sum(values) / n - centre) / math.sqrt(variance / n)


def fixed_b_critical_value(*, days: int = FIXED_B_DAYS, b: float = FIXED_B, draws: int = FIXED_B_DRAWS, seed: int = SEED) -> float:
    """The 0.95 quantile of the fixed-b statistic on `draws` independent N(0, 1) series of `days` days."""

    rng = random.Random(seed)
    stats = sorted(fixed_b_statistic([rng.gauss(0.0, 1.0) for _ in range(days)], b=b) for _ in range(draws))
    return sp._quantile(stats, 1.0 - LEVEL)


def events_per_year(events: Sequence[date]) -> float:
    ordered = sorted(events)
    return len(ordered) / ((ordered[-1] - ordered[0]).days / 365.25)


def share_above(ordered: Sequence[float], value: float) -> float:
    return sum(1 for x in ordered if x > value) / len(ordered)


def generator_statistics(series: Sequence[float], days: int, generator: str) -> List[float]:
    if generator == "contiguous":
        return contiguous_window_statistics(series, days=days)
    if generator == "stationary_10":
        with stationary_windows():
            return sp.window_t_statistics(series, days=days, windows=WINDOWS, seed=SEED, block=sp.BLOCK_LENGTH)
    if generator == "circular_10":
        return sp.window_t_statistics(series, days=days, windows=WINDOWS, seed=SEED, block=sp.WINDOW_BLOCK)
    raise ValueError(f"unknown generator {generator}")


def _calibration_job(job):
    candidate, days, generator, series = job
    ordered = generator_statistics(series, days, generator)
    c = sp._bound(ordered, 1.0 - LEVEL, len(ordered))
    return (candidate, days, generator), {
        "windows": len(ordered), "c": c, "size_in_force": share_above(ordered, IN_FORCE[days]),
        "effective_windows": effective_windows(len(series), days),
    }


# -- the data ---------------------------------------------------------------------------------------------------------------


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True,
                           check=True).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(published: Path, walks: Path):
    """Cell scores and day scores of B1, B2, `spread_mr_ctx` and `gbm_funding`, on the days all have a forecast."""

    from repo_model.data import audit_panel, load_daily_panel
    from repo_model.evaluation_splits import load_split_declaration
    from repo_model.splits import SplitError

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
    gbm_days = [d for d in covered if d >= DEVELOPMENT_FIRST and calendar[position[d] + 5] <= LAST_TARGET]
    b1 = pb.forecasts(pb.b1_forecast, rows, gbm_days, **settings)
    b2 = pb.forecasts(pb.b2_forecast, rows, gbm_days, splits=splits, **settings)
    gbm = sp.fill_missing({d: laws[d] for d in gbm_days}, b1, gbm_days).forecasts

    # spread_mr_ctx, walked as #761 walks it: every decision day whose fifth target is scored, B2 where it exists
    all_days = [d for i, d in enumerate(calendar) if i + 5 < len(rows) and calendar[i + 5] <= LAST_TARGET]
    b2_all = {}
    for day in all_days:
        try:
            b2_all[day] = pb.b2_forecast(rows, position[day], splits=splits, **settings)
        except (sp.ProtocolError, SplitError):
            pass
    walk = var.walk(rows, all_days, b2=b2_all, splits=splits, **settings)
    ctx = walk.forecasts["spread_mr_ctx"]

    days = [d for d in gbm_days if d in ctx and d in b2]
    targets = {d: {h: calendar[position[d] + h] for h in sp.HORIZONS} for d in days}
    lockbox.require_unlocked(set(days) | {t for per in targets.values() for t in per.values()}, where="contiguous_calibration_963")
    models = {"B1": b1, "B2": b2, "spread_mr_ctx": ctx, "gbm_funding": gbm}
    cells = {name: sd.cell_scores({d: f[d] for d in days}, outcomes, calendar, sp.grid_crps) for name, f in models.items()}
    day_score = {name: sp.day_scores({d: f[d] for d in days}, outcomes, calendar) for name, f in models.items()}
    repro = {name: sp.day_scores(f, outcomes, calendar) for name, f in (("B2", b2), ("gbm_funding", gbm))}
    return {"repro": repro, "rows": rows, "calendar": calendar, "position": position, "row_of": row_of, "splits": splits, "days": days,
            "cells": cells, "day_score": day_score, "outcomes": outcomes, "gbm_days": gbm_days}


def d_series(data, candidate, first: date = POST_2020_FIRST):
    """`{decision day: S(B1) - S(candidate)}` from `first`."""

    b, c = data["day_score"]["B1"], data["day_score"][candidate]
    return {d: b[d] - c[d] for d in data["days"] if d >= first and d in b and d in c}


def target_scores(data, name):
    """`{target day: mean over leads 1-5 of the cells that target}` where all five leads are in `data`."""

    pos, cal, cells = data["position"], data["calendar"], data["cells"][name]
    out = {}
    for target in cal:
        parts = []
        for h in sp.HORIZONS:
            i = pos[target] - h
            if i < 0 or (cal[i], h) not in cells:
                parts = None
                break
            parts.append(cells[(cal[i], h)])
        if parts and cal[pos[target] - 5] >= POST_2020_FIRST:
            out[target] = sum(parts) / 5
    return out


def acf(values: Sequence[float], max_lag: int) -> List[float]:
    return _load("block_length_949").acf(values, max_lag)


def stratum_members(data, stratum: str, targets) -> List[date]:
    splits, row_of = data["splits"], data["row_of"]
    out = []
    for t in sorted(targets):
        row = row_of[t]
        if stratum == "coupon_settlement":
            hit = float(row.values.get("treasury_settlement_coupons") or 0.0) > 0.0
        else:
            hit = splits.reporting_day_type(t, row.values) == stratum
        if hit:
            out.append(t)
    return out


def _event_job(job):
    key, events, bench, cand = job
    (test,) = sp.paired_tests([(bench, cand)], seed=SEED, draws=EVENT_DRAWS, block_length=EVENT_BLOCK, hac_lag=EVENT_LAG,
                              with_skill=False)
    d = [bench[e] - cand[e] for e in events]
    return key, {"n": len(events), "events_per_year": events_per_year(events), "mean_d": test.mean_difference,
                 "lower_95": test.lower_mean_difference(0.05), "upper_95": test.lower_mean_difference(0.95),
                 "dm": test.dm_statistic, "acf": acf(d, EVENT_ACF_LAGS)}


# -- the run ----------------------------------------------------------------------------------------------------------------


def run_command(args) -> int:
    declaration = committed_declaration()
    data = build(args.published, args.walks)
    record: Dict[str, object] = {
        "declaration_sha256": sha256(DECLARATION), "panel_sha256": sha256(args.published), "seed": SEED, "level": LEVEL,
        "windows": WINDOWS, "window_days": list(WINDOW_DAYS), "in_force": {str(k): v for k, v in IN_FORCE.items()},
        "post_2020_first": POST_2020_FIRST.isoformat(), "b1_prime": declaration["series"]["b1_prime"],
    }
    # the reproduction of #922: S(B2) - S(gbm_funding) over the walk's days equals its recorded mean
    recorded = json.loads(B2_LEG_RECORD.read_text(encoding="utf-8"))["cells"]["gbm_funding|full|250"]
    b2s, gs = data["repro"]["B2"], data["repro"]["gbm_funding"]
    both = [d for d in data["gbm_days"] if d in b2s and d in gs]
    mean = sum(b2s[d] - gs[d] for d in both) / len(both)
    record["reproduces_922"] = {"recomputed": mean, "recorded": recorded["mean_d"], "days": len(both), "recorded_days": recorded["series_days"]}
    if len(both) != recorded["series_days"] or abs(mean - recorded["mean_d"]) > REPRODUCTION_TOLERANCE:
        raise ValueError(f"mean S(B2) - S(gbm_funding) is {mean} over {len(both)} days here and {recorded['mean_d']} over "
                         f"{recorded['series_days']} in #922's record")

    series = {c: d_series(data, c) for c in CANDIDATES}
    days = sorted(series[CANDIDATES[0]])
    if any(sorted(s) != days for s in series.values()):
        raise ValueError("the three series do not cover the same days")
    record["series"] = {"days": len(days), "first": days[0].isoformat(), "last": days[-1].isoformat()}
    values = {c: [series[c][d] for d in days] for c in CANDIDATES}
    pw = _load("block_length_949").politis_white
    record["own_d"] = {c: {"mean": sum(v) / len(v), "acf": acf(v, 5), "politis_white": pw(v)} for c, v in values.items()}

    jobs = [(c, n, g, values[c]) for c in CANDIDATES for n in WINDOW_DAYS for g in GENERATORS]
    calibration: Dict[str, Dict] = {}
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for (c, n, g), cell in pool.map(_calibration_job, jobs):
            calibration.setdefault(c, {}).setdefault(str(n), {})[g] = cell
    record["calibration"] = calibration

    targets = {name: target_scores(data, name) for name in ("B1", "B2", "spread_mr_ctx", "gbm_funding")}
    common = sorted(set.intersection(*(set(t) for t in targets.values())))
    event_jobs, strata = [], {}
    for stratum in STRATA:
        events = stratum_members(data, stratum, common)
        strata[stratum] = {"n": len(events), "events_per_year": events_per_year(events) if len(events) > 1 else None}
        if len(events) < MINIMUM_EVENTS:
            strata[stratum]["thin"] = True
            continue
        for cand, bench in (("B2", "B1"), ("spread_mr_ctx", "B1"), ("spread_mr_ctx", "B2"), ("gbm_funding", "B1"), ("gbm_funding", "B2")):
            event_jobs.append(((stratum, f"{cand} vs {bench}"), events, {e: targets[bench][e] for e in events},
                               {e: targets[cand][e] for e in events}))
    pairs: Dict[str, Dict] = {s: {} for s in STRATA}
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for (stratum, label), row in pool.map(_event_job, event_jobs):
            pairs[stratum][label] = row
    record["strata"] = {"target_days": len(common), "events": strata, "pairs": pairs}

    critical = fixed_b_critical_value()
    fixed: Dict[str, Dict] = {"b": FIXED_B, "days": FIXED_B_DAYS, "critical_value": critical, "normal": NORMAL_ONE_SIDED_95,
                              "candidates": {}}
    for c in CANDIDATES:
        v = values[c]
        last = v[-FIXED_B_DAYS:]
        windows = [v[s:s + FIXED_B_DAYS] for s in range(len(v) - FIXED_B_DAYS + 1)]
        centre = sum(v) / len(v)
        nw = sorted(((sum(w) / len(w) - centre) / sp._standard_error(w, sp.HAC_LAG, "a window")) for w in windows)
        fb = sorted(fixed_b_statistic(w, centre=centre) for w in windows)
        fixed["candidates"][c] = {
            "last_mean": sum(last) / len(last), "last_nw10": (sum(last) / len(last)) / sp._standard_error(last, sp.HAC_LAG, "the last window"),
            "last_fixed_b": fixed_b_statistic(last), "windows": len(windows),
            "size_nw10_normal": share_above(nw, NORMAL_ONE_SIDED_95), "size_fixed_b": share_above(fb, critical),
        }
    record["fixed_b"] = fixed
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "days": len(days)}))
    return 0


# -- the report -------------------------------------------------------------------------------------------------------------


def f(value, digits=2, sign=False):
    if value is None:
        return "n/a"
    return f"{value:{'+' if sign else ''}.{digits}f}"


def pct(value):
    return "n/a" if value is None else f"{100 * value:.1f}%"


def render(record) -> str:
    cal, own, fb = record["calibration"], record["own_d"], record["fixed_b"]
    n = record["series"]["days"]
    L = [
        "# Critical values on contiguous post-2020 windows, event strata and a fixed-b statistic (#963, H1 step 3 and H6 step 1)", "",
        "**Development data, not a verdict.** A report that changes nothing: `scoring_protocol.CRITICAL_VALUES` and "
        "`docs/decisions/scoring-protocol.md` are only read. No day after 2025-12-31 and no lockbox day is scored. Everything is "
        "declared in `metadata/contiguous_calibration_963.json` before any score and read from "
        "`docs/research/contiguous-calibration-963/result.json` by `scripts/contiguous_calibration_963.py report`.", "",
        "## Questions for Eleonora (marked)", "",
        "1. **Does the 250-day confirmation window stay?** The reading rules below are Lens C's, declared as stated; the design is hers.",
        "2. **Should H6 be registered ahead of H5?** The event-strata table gives how many events a year each stratum holds and what the "
        "candidates do on them; whether H6 moves ahead of H5 is hers.",
        "3. **Should the window lengthen** (the 500-day rows)? The same.", "",
        "## Series", "",
        f"d = S(B1) - S(candidate), lead-averaged grid CRPS, {n} decision days {record['series']['first']} to {record['series']['last']} "
        f"(the days all four forecasts cover; from {record['post_2020_first']}). {record['b1_prime']}. Reproduction: mean S(B2) - "
        f"S(`gbm_funding`) over the walk's {record['reproduces_922']['days']} days is {record['reproduces_922']['recomputed']:.6f}, and "
        f"#922's record gives {record['reproduces_922']['recorded']:.6f} over {record['reproduces_922']['recorded_days']}.", "",
        "| candidate | mean d | rho(1) | rho(5) | Politis-White block |", "|---|---|---|---|---|",
    ]
    for c in CANDIDATES:
        o = own[c]
        L.append(f"| {c} | {f(o['mean'], 3)} | {f(o['acf'][0])} | {f(o['acf'][4])} | {f(o['politis_white'], 1)} |")
    L += ["", "## 1. Critical values by generator", "",
          f"c is the {1 - record['level']:.2f} quantile of the window statistics: the bound `mean - c * se` covers the series' mean on 95% of the "
          "generator's windows. Size is the share of the generator's windows above the value in force (125 days: "
          f"{record['in_force']['125']:.3f}; 250 days: {record['in_force']['250']:.3f}; 500 days has none and is read at the 250-day value). "
          "Non-overlapping is n / days, the windows the series holds without overlap; the windows of a persistent series overlap "
          "in information, so it is an upper count of independent ones.", "",
          "| candidate | days | non-overlapping | c contiguous | c stationary-10 | c circular-10 | size contiguous | size stationary-10 | size circular-10 |",
          "|---|---|---|---|---|---|---|---|---|"]
    for c in CANDIDATES:
        for days in map(str, record["window_days"]):
            row = cal[c][days]
            L.append(f"| {c} | {days} | {f(row['contiguous']['effective_windows'], 1)} | "
                     + " | ".join(f(row[g]["c"], 2) for g in GENERATORS) + " | "
                     + " | ".join(pct(row[g]["size_in_force"]) for g in GENERATORS) + " |")
    L += ["", "### Reading rules (declared)", ""]
    for c in CANDIDATES:
        c250 = cal[c]["250"]["contiguous"]["c"]
        if c250 < SURVIVES_BELOW:
            verdict = f"below {SURVIVES_BELOW}: the 250-day design survives"
        elif c250 > FAILS_ABOVE:
            verdict = f"above {FAILS_ABOVE}: no 250-day pooled test can confirm anything short of a 20-30% skill"
        else:
            verdict = f"between {SURVIVES_BELOW} and {FAILS_ABOVE}: neither rule applies"
        L.append(f"- `{c}`: the contiguous-window c at 250 days is {c250:.2f}, {verdict}.")
    L += ["", "## 2. Event strata (H6 step 1)", "",
          "The H5 metric (grid CRPS, mean over leads 1-5 of the cells that target a day) on targets that are risk dates, d = S(benchmark) - "
          f"S(candidate), paired by `scoring_protocol.paired_tests` (stationary bootstrap, mean block 3 events, HAC lag 3, one-sided 95% bounds "
          f"[lower, upper] of mean d). The target days are {record['strata']['target_days']} post-2020 days with all five leads. Month-end is "
          "the month's last two business days and holds the turn of the month; #959's turn label has not merged, so the current one is used. "
          "The ACF is of d between consecutive events of the stratum, in date order.", "",
          "| stratum | events | per year |", "|---|---|---|"]
    for s in STRATA:
        e = record["strata"]["events"][s]
        L.append(f"| {s} | {e['n']} | {f(e['events_per_year'], 1)}{' (thin: not tested)' if e.get('thin') else ''} |")
    L += ["", "| stratum | pair | events | mean d | [lower, upper] | rho(1) | rho(2) | rho(3) |", "|---|---|---|---|---|---|---|---|"]
    for s in STRATA:
        for label, p in record["strata"]["pairs"][s].items():
            L.append(f"| {s} | {label} | {p['n']} | {f(p['mean_d'], 3, True)} | [{p['lower_95']:+.3f}, {p['upper_95']:+.3f}] | "
                     + " | ".join(f(a) for a in p["acf"]) + " |")
    L += ["", "## 3. A fixed-b statistic", "",
          f"The mean of d over a window of {fb['days']} days over its Bartlett standard error of bandwidth b * T, b = {fb['b']} (M = "
          f"{int(round(fb['b'] * fb['days']))}), against the fixed-b critical value {fb['critical_value']:.3f} (the 0.95 quantile on independent noise), beside the "
          f"Newey-West (lag 10) statistic against the normal {fb['normal']:.3f}. The last window is the series' last {fb['days']} days. Size is the share "
          "of the series' contiguous windows of that length, centred at the series' mean, above the value.", "",
          "| candidate | mean d, last 2 years | NW(10) t | fixed-b t | size NW(10) vs normal | size fixed-b |", "|---|---|---|---|---|---|"]
    for c in CANDIDATES:
        r = fb["candidates"][c]
        L.append(f"| {c} | {f(r['last_mean'], 3, True)} | {f(r['last_nw10'])} | {f(r['last_fixed_b'])} | {pct(r['size_nw10_normal'])} | {pct(r['size_fixed_b'])} |")
    L += ["", "## Limits", "",
          "The proxy and the series differ (Lens C's proxy was B1/B2; these are `gbm_funding`'s, `spread_mr_ctx`'s and B2's own d). The series are "
          "development data seen before the declaration. Contiguous windows overlap heavily, so a quantile of them rests on a handful of "
          "independent stretches; the non-overlapping count says how few. Nothing here is registered or changed.", ""]
    return "\n".join(L)


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


from repo_model import turn_days  # noqa: E402


@turn_days.with_legacy_flag
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
