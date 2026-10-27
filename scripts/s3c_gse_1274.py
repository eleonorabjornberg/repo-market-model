"""(s3c-gse): (s3c) with the GSE cash cycle as a ramp from the 19th to the 25th, scored against (s3c), (s3), B1, B1' and B2 (#1274; H5 step 3;
ledger item 66 on #1116).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every choice is in
`metadata/s3c_gse_1274.json`, which this script refuses to read unless it is committed and unchanged. The arm is `repo_model.s3c_gse`:
(s3) of #1145 (`repo_model.spread_mr_state_calendar.ARMS[2]`) walked on a term table whose `dom_19_23` slot holds the ramp (0 before the 19th
and after the 25th, (d - 18) / 7 from the 19th to the 25th, read from the target row's own date), then capped at the Standing Repo Facility line
where `repo_model.s3c_candidate` caps (s3). The frames, the benchmarks, (s3) and (s3c) are #1255's, built by its `build` as it stands: the
development window of #1145 and #1241 (targets to 2025-12-31) and the 2026 development days of #1229 and #1252 (targets 2026-01-02 to
2026-09-03, the near-blind tier open since GO #151). The blind tier and every lockbox day are refused by the frames' guards.

(s3) is walked twice more here, once on the ramp table and once on the base table, over every decision day from the start of the panel to the
last with five targets on or before 2026-09-03 (the schedule of the frames' own walks, of which each window's is a prefix). The base walk must
equal the frames' (s3) cell for cell on every scored decision day, or no record is written: that shows the ramp walk is the frames' walk with
one column changed. The base walk also gives the flat term's fitted effect for the comparison.

It measures the arm on grid CRPS averaged over h = 1..5 (primary), upper-tail twCRPS (key secondary) and the Brier score of P(> +5 bp)
(`docs/decisions/pressure-probability.md`), on scoring protocol v1's studentized stationary bootstrap read on the bound on mean d (her #1009
ruling) with the skill interval beside; split by lead, by regime (development window) or target month (2026), by pressure-day type, and by
the days the changed term is non-zero (target days from the 19th to the 25th) against the others; reports the 90% band's coverage beside
(s3c)'s; and reports the fitted effect of the changed term in bp, by regime.

The walks take minutes and the paired tests are the longer part, so the run is a cloud run unless the measured time says otherwise.
Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/s3c_gse_1274.py score --panel PUB.csv --output docs/research/s3c-gse-1274/result.json
    PYTHONPATH=src python3 scripts/s3c_gse_1274.py page \\
        --score docs/research/s3c-gse-1274/result.json --output docs/research/s3c-gse-1274-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import multiprocessing
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load(name: str, alias: Optional[str] = None):
    """Load `scripts/<name>.py` as a module registered under `alias` (default `name`)."""

    alias = alias or name
    spec = importlib.util.spec_from_file_location(alias, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


from repo_model import announced_iorb, data, metrics, policy_events, s3c_candidate, s3c_gse, turn_days  # noqa: E402
from repo_model import scoring_protocol as sp, spread_mean_reversion as smr, spread_mr_calendar as cal  # noqa: E402
from repo_model import spread_mr_state_calendar as sc  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.exploration import EXPLORATORY_END, require_exploratory_window  # noqa: E402

#: #1255's script (and through it #1241's and #1229's), loaded under an alias of its own so that the pickling of the worker pool's tasks does
#: not meet another test module's copy.
m1255 = _load("s3c_candidate_1255", "s3c_candidate_1255_in_1274")
k, d1222 = m1255.k, m1255.d1222
c, s686, s761, load_daily_panel = k.c, k.s686, k.s761, m1255.load_daily_panel

DECLARATION = REPO / "metadata" / "s3c_gse_1274.json"
RECORD_1255 = REPO / "docs" / "research" / "s3c-candidate-1255" / "result.json"
SEED = 1274
LAST_DAY = EXPLORATORY_END
WINDOWS = m1255.WINDOWS
S3, S3C, S3CG = k.S3, m1255.S3C, "sc_s3c_gse"
B1P = k.B1P
BENCHMARKS = ("B1", B1P, "B2")
MODELS = BENCHMARKS + (S3, S3C, S3CG)
#: What (s3c-gse) is tested against, (s3c) first.
REFERENCES = (S3C, S3) + BENCHMARKS
LABELS = {"B1": "B1", B1P: "B1' (#960)", "B2": "B2", S3: "(s3)", S3C: "(s3c)", S3CG: "(s3c-gse)"}
METRIC_NAMES = ("grid_crps", "upper_tail_twcrps", "brier_gt5")
METRIC_TITLES = {"grid_crps": "grid CRPS", "upper_tail_twcrps": "upper-tail twCRPS", "brier_gt5": "Brier P(> +5 bp)"}
TAU = 5.0
RATE = "b90_closed"
BAND = sp.GRID.index(0.05), sp.GRID.index(0.95)
COVERAGE_MODELS = (S3CG, S3C, S3)
MIN_GROUP_DAYS = k.MIN_GROUP_DAYS
BLOCK = float(sp.BLOCK_LENGTH)
CELL_BLOCK = d1222.CELL_BLOCK
S3_ARM = sc.ARMS[2]
TERM = s3c_gse.REPLACED_TERM
WINDOW_TITLES = {"development": "The development window (targets up to 2025-12-31; #1145, #1241)",
                 "2026": "The 2026 development days (targets 2026-01-02 to 2026-09-03; #1229, #1252)"}
RAMP_SPLIT = "ramp_day"
RAMP_DAYS, OTHER_DAYS = "target days 19th to 25th (the ramp is non-zero)", "other target days"


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


# -- the walks ---------------------------------------------------------------------------------------------------------------


def candidate_days(panel, dates: Sequence[date], first: Optional[date]) -> List[date]:
    """Every decision day with five rows after it whose fifth target is on or before `LAST_DAY` (and on or after `first`): the days the
    frames' own walks start from, to the last day any of them scores.

    Raises:
        LookAheadError: a day is after `LAST_DAY` or in a locked tier.
    """

    days = [day for i, day in enumerate(dates)
            if i + max(sp.HORIZONS) < len(panel) and dates[i + max(sp.HORIZONS)] <= LAST_DAY and (first is None or day >= first)]
    s686.require_scored_days(days, LAST_DAY)
    return days


def walk_s3(panel, days: Sequence[date], table, splits, registry) -> sc.Walk:
    """(s3) walked over `days` on `table`: the walk of the frames, refit every 21 decision days, direct pairs."""

    return sc.walk(panel, days, table, {}, (S3_ARM,), registry=registry, decision_time=k.DECISION_TIME, splits=splits)


def same_as_frame(frame, walk: sc.Walk) -> int:
    """The count of scored decision days on which the base-table walk's (s3) is the frame's, cell for cell.

    Raises:
        ValueError: a scored decision day has no forecast in the walk, or a cell differs.
    """

    for d in frame.days:
        mine = walk.forecasts[S3].get(d)
        if mine is None:
            raise ValueError(f"the walk has no (s3) forecast for the scored decision day {d}")
        if {h: list(q) for h, q in mine.items()} != {h: list(q) for h, q in frame.forecasts[S3][d].items()}:
            raise ValueError(f"the walk's (s3) differs from the frame's on the decision day {d}")
    return len(frame.days)


def gse_forecasts(frame, walk: sc.Walk, register: Sequence[policy_events.PolicyEntry]):
    """(s3) on the ramp table, and the same capped as (s3c) caps: `(s3 on the ramp, (s3c-gse))` by decision day and lead.

    Raises:
        ValueError: a scored decision day has no forecast in the ramp walk.
    """

    ramped, capped = {}, {}
    for d in frame.days:
        mine = walk.forecasts[S3].get(d)
        if mine is None:
            raise ValueError(f"the ramp walk has no (s3) forecast for the scored decision day {d}")
        ramped[d] = {h: list(q) for h, q in mine.items()}
        capped[d] = {h: s3c_candidate.capped_quantiles(q, register, k.decision_instant(d), frame.target(d, h)) for h, q in mine.items()}
    return ramped, capped


# -- the cells ---------------------------------------------------------------------------------------------------------------


def probability(q: Sequence[float], tau: float) -> float:
    """P(spread > tau) as `spread_mean_reversion.exceedance` reads it off the 23 quantiles: 1 - F(floor(tau) + 0.5)."""

    return smr.exceedance(q, tau)


def cell_table(frame, forecasts: Mapping[date, Mapping[int, Sequence[float]]]) -> Dict[str, Dict[Tuple[date, int], float]]:
    """The three scores and the 90% band's hit of every (decision day, lead) cell of `forecasts`, after the days are checked. The Brier cell is
    `(P(> tau) - 1{y > tau})^2` with the event strict and on whole basis points (`data.exceeds_bp`)."""

    days = sorted(forecasts)
    cells = {(d, h): frame.target(d, h) for d in days for h in sp.HORIZONS}
    s686.require_scored_days(set(d for d, _ in cells) | set(cells.values()), LAST_DAY)
    out: Dict[str, Dict[Tuple[date, int], float]] = {m: {} for m in METRIC_NAMES + (RATE,)}
    lo, hi = BAND
    for (d, h), t in cells.items():
        q, y = forecasts[d][h], frame.outcome[t]
        out["grid_crps"][(d, h)] = sp.grid_crps(q, y)
        out["upper_tail_twcrps"][(d, h)] = sp.upper_tail_twcrps(q, y)
        out["brier_gt5"][(d, h)] = (probability(q, TAU) - (1.0 if data.exceeds_bp(y, TAU) else 0.0)) ** 2
        out[RATE][(d, h)] = 1.0 if q[lo] <= y <= q[hi] else 0.0
    return out


def in_ramp(t: date) -> bool:
    """Whether the changed term is non-zero on target day `t`."""

    return s3c_gse.ramp(t) > 0.0


def groups_of(frame, window: str) -> List[Tuple[str, str, str, List[date]]]:
    """`(split, label, grain, members)`: pooled; by lead; by regime (development window) or target month (2026); by pressure-day type of
    the target day; and the target days on which the changed term is non-zero against the others."""

    out: List[Tuple[str, str, str, List[date]]] = [("pooled", "all decision days", "decision", list(frame.days))]
    for h in sp.HORIZONS:
        out.append(("lead", f"h={h}", f"lead{h}", list(frame.days)))
    targets = sorted({frame.target(d, h) for d in frame.days for h in sp.HORIZONS})
    out.append((RAMP_SPLIT, RAMP_DAYS, "target", [t for t in targets if in_ramp(t)]))
    out.append((RAMP_SPLIT, OTHER_DAYS, "target", [t for t in targets if not in_ramp(t)]))
    by_type: Dict[str, List[date]] = {}
    by_regime: Dict[str, List[date]] = {}
    by_month: Dict[str, List[date]] = {}
    for t in targets:
        by_type.setdefault(frame.day_type(t), []).append(t)
        by_regime.setdefault(frame.regime(t), []).append(t)
        by_month.setdefault(t.strftime("%Y-%m"), []).append(t)
    if window == "development":
        out += [("regime", label, "target", by_regime[label]) for label in c.REGIMES if label in by_regime]
    else:
        out += [("month", label, "target", by_month[label]) for label in sorted(by_month)]
    out += [("pressure_day_type", label, "target", by_type[label]) for label in sorted(by_type)]
    return out


def coverage_groups(frame, keys: Sequence[Tuple[date, int]]) -> Dict[str, List[Tuple[date, int]]]:
    """The cells of each coverage group in date order: pooled, and by lead."""

    ordered = sorted(keys, key=lambda x: (frame.target(*x), x[1]))
    out = {"pooled": ordered}
    for h in sp.HORIZONS:
        out[f"h={h}"] = [x for x in ordered if x[1] == h]
    return out


def block_of(group: str) -> float:
    """The mean block of a coverage group's interval, in cells."""

    return d1222.LEAD_BLOCK if group.startswith("h=") else CELL_BLOCK


# -- the fitted effect of the changed term -----------------------------------------------------------------------------------


def fit_day(walk: sc.Walk, d: date) -> date:
    """The refit day whose estimate the decision on `d` used: the latest refit on or before it."""

    return max(r for r in walk.estimates if r <= d)


def effect_cells(frame, walk: sc.Walk, value) -> Dict[str, Dict[str, dict]]:
    """The changed term's fitted effect in bp, by regime of the target day and by lead.

    A cell (decision day `d`, lead `h`) has the effect of the fit in use, in scale units, times the scale at the decision's anchor: the bp shift
    on a day the term is 1 (the 25th for the ramp, any day of the 19th to 23rd for the flat flag). `value(t)` is the term's value on target day
    `t`. For each regime and lead, and over the leads (`all`): the cells, the cells whose fit holds the term, the mean bp per unit of the term over
    all cells, the cells whose target carries the term, and the mean shift actually applied on those (effect x scale x value).
    """

    keys = lambda h: ("all", str(h))  # noqa: E731
    out: Dict[str, Dict[str, dict]] = {}
    for d in frame.days:
        estimates = walk.estimates[fit_day(walk, d)][S3_ARM.name]
        scale = walk.detail[d]["scale"]
        for h in sp.HORIZONS:
            t = frame.target(d, h)
            e = estimates[h].effect.get(TERM)
            std = 0.0 if e is None else e
            v = value(t)
            for regime in (frame.regime(t), "all regimes"):
                for lead in keys(h):
                    cell = out.setdefault(regime, {}).setdefault(lead, {"cells": 0, "with_term": 0, "sum_bp_per_unit": 0.0, "carry": 0, "sum_applied_bp": 0.0})
                    cell["cells"] += 1
                    cell["with_term"] += 0 if e is None else 1
                    cell["sum_bp_per_unit"] += std * scale
                    if v > 0.0:
                        cell["carry"] += 1
                        cell["sum_applied_bp"] += std * scale * v
    for regime in out.values():
        for cell in regime.values():
            cell["mean_bp_per_unit"] = cell["sum_bp_per_unit"] / cell["cells"]
            cell["mean_applied_bp"] = cell["sum_applied_bp"] / cell["carry"] if cell["carry"] else None
    return out


def refit_effects(walk: sc.Walk) -> dict:
    """The term's coefficient (scale units) and the sum of its values over the training pairs, at each refit and lead."""

    days = sorted(walk.estimates)
    return {"refit_days": [d.isoformat() for d in days],
            "effect": {str(h): [walk.estimates[d][S3_ARM.name][h].effect.get(TERM) for d in days] for h in sp.HORIZONS},
            "sum_of_term": {str(h): [walk.estimates[d][S3_ARM.name][h].flagged.get(TERM) for d in days] for h in sp.HORIZONS}}


# -- the tests, in parallel --------------------------------------------------------------------------------------------------

_STATE: Dict = {}


def plan(candidate: str) -> List[str]:
    """What an arm is tested against: only (s3c-gse) is a candidate here."""

    return list(REFERENCES) if candidate == S3CG else []


def _identical(series, candidate: str, reference: str, members: Sequence[date]) -> bool:
    return all(series[candidate][d] == series[reference][d] for d in members)


def unstudentized(series, candidate: str, reference: str, members: Sequence[date]) -> dict:
    """Mean d and its 90% stationary-bootstrap percentile interval, for a group whose studentized bound cannot be computed. Not the protocol's
    interval; no reading is taken from it. `d = S(reference) - S(candidate)`, positive favours the candidate."""

    d = [series[reference][x] - series[candidate][x] for x in sorted(members)]
    low, high = metrics.stationary_bootstrap_interval(
        lambda idx: sum(d[i] for i in idx) / len(idx), len(d), block_length=BLOCK, seed=SEED, replications=_STATE["reps"])
    return {"mean_d": sum(d) / len(d), "interval": [low, high], "days": len(d)}


def _pairs_task(job):
    split, label, grain, metric, candidate, members = job
    series = _STATE["series"][(grain, metric)]
    out: Dict[str, dict] = {}
    for name in plan(candidate):
        days = list(members)
        if _identical(series, candidate, name, days):
            out[name] = {"identical": True, "days": len(days)}
            continue
        out[name] = s761.run_pairs({name: series[name]}, series[candidate], days, seed=SEED, draws=_STATE["draws"], mean_d_fallback=True)[name]
        if "undefined" in out[name]:
            out[name]["unstudentized"] = unstudentized(series, candidate, name, days)
    return (split, label, metric, candidate), out


def _interval_task(job):
    key, values, block = job
    n = len(values)
    low, high = metrics.stationary_bootstrap_interval(
        lambda idx: sum(values[i] for i in idx) / len(idx), n, block_length=block, seed=SEED, replications=_STATE["reps"])
    return key, [low, high]


def _dispatch(job):
    kind, payload = job
    return kind, (_pairs_task(payload) if kind == "pairs" else _interval_task(payload))


def run_jobs(jobs, workers: int):
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        return pool.map(_dispatch, jobs, chunksize=1)


# -- one window --------------------------------------------------------------------------------------------------------------


def build(window: str, panel, splits, registry, table, register, first: Optional[date]):
    """#1255's frame of a window, with the models of `MODELS`: returns `(frame, notes, mine)`; the ramp's forecasts are added by `run_window`."""

    frame, notes, mine, _cell_table, _groups = m1255.build(window, panel, splits, registry, table, register, first)
    frame.forecasts = {name: {d: frame.forecasts[name][d] for d in frame.days} for name in BENCHMARKS + (S3, S3C)}
    return frame, notes, mine


def run_window(window: str, panel, splits, registry, table, register, walks: Mapping[str, sc.Walk], args) -> dict:
    frame, notes, mine = build(window, panel, splits, registry, table, register, args.first)
    checked = same_as_frame(frame, walks["base"])
    ramped, capped = gse_forecasts(frame, walks["ramp"], register)
    frame.forecasts[S3CG] = capped
    labels = {t: frame.day_type(t) for t in {frame.target(d, h) for d in frame.days for h in sp.HORIZONS}}

    cells = {m: cell_table(frame, frame.forecasts[m]) for m in MODELS}
    for m in MODELS:
        official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")

    groups = groups_of(frame, window)
    series: Dict[Tuple[str, str], Dict[str, Dict[date, float]]] = {}
    for _s, _l, grain, _m in groups:
        for metric in METRIC_NAMES:
            if (grain, metric) not in series:
                series[(grain, metric)] = {m: c.series_of(frame, cells[m][metric], grain) for m in MODELS}
    _STATE.update(series=series, draws=args.draws, reps=args.reps)

    jobs, skipped = [], {}
    for split, label, grain, members in groups:
        if len(members) < MIN_GROUP_DAYS:
            skipped[f"{split}/{label}"] = len(members)
            continue
        for metric in METRIC_NAMES:
            jobs.append(("pairs", (split, label, grain, metric, S3CG, tuple(members))))
    cover = coverage_groups(frame, sorted(cells[S3CG][RATE]))
    for group, keys in cover.items():
        for m in COVERAGE_MODELS:
            jobs.append(("interval", ((group, m), [cells[m][RATE][x] for x in keys], block_of(group))))
    done = run_jobs(jobs, args.workers)

    by_key = {(s_, l_): (g, mem) for s_, l_, g, mem in groups}
    result: dict = {"notes": notes, "refits": len(walks["ramp"].estimates), "groups": {}, "skipped_groups": skipped, "coverage": {},
                    "walk_equals_frame_days": checked,
                    "effect": {"gse_ramp": effect_cells(frame, walks["ramp"], s3c_gse.ramp),
                               "flat_19_23": effect_cells(frame, walks["base"], lambda t: 1.0 if 19 <= t.day <= 23 else 0.0)}}
    for kind, payload in done:
        if kind == "pairs":
            (split, label, metric, candidate), out = payload
            entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(by_key[(split, label)][1])})
            entry.setdefault(metric, {"means": {}, "vs": {}})["vs"][candidate] = out
        else:
            (group, m), interval = payload
            result["coverage"].setdefault(group, {}).setdefault(m, {})["interval"] = interval
    for group, keys in cover.items():
        for m in COVERAGE_MODELS:
            values = [cells[m][RATE][x] for x in keys]
            result["coverage"][group][m].update({"rate": sum(values) / len(values), "cells": len(values)})
    for split, labels_ in result["groups"].items():
        for label, entry in labels_.items():
            grain, members = by_key[(split, label)]
            for metric in METRIC_NAMES:
                if metric in entry:
                    ser = series[(grain, metric)]
                    entry[metric]["means"] = {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS}
    result["pressure_day_type_counts"] = {x: sum(1 for v in labels.values() if v == x) for x in sorted(set(labels.values()))}
    targets = sorted(labels)
    result["target_days"] = {"all": len(targets), "ramp": sum(1 for t in targets if in_ramp(t))}
    result["positive_days_5"] = sum(1 for t in targets if data.exceeds_bp(frame.outcome[t], TAU))
    result["cells_where_gse_differs_from_s3c"] = sum(1 for d in frame.days for h in sp.HORIZONS if frame.forecasts[S3CG][d][h] != frame.forecasts[S3C][d][h])
    result["cells"] = len(frame.days) * len(sp.HORIZONS)
    # (s3c-gse) is the cap applied to the ramp walk: before full allotment it is that walk's (s3), element for element
    result["before_full_allotment_is_the_ramp_walk"] = all(
        list(capped[d][h]) == list(ramped[d][h]) for d in frame.days for h in sp.HORIZONS
        if s3c_candidate.cap_line(register, k.decision_instant(d), frame.target(d, h)) is None)
    return result


def against_1255(results: Mapping[str, dict]) -> dict:
    """The pooled means of (s3), (s3c), B1, B1' and B2 here against #1255's record, on each window (the same days, the same walk)."""

    out: Dict[str, dict] = {}
    if not RECORD_1255.exists():
        return out
    record = json.loads(RECORD_1255.read_text(encoding="utf-8"))["windows"]
    for window in WINDOWS:
        if window not in results:
            continue
        there = record[window]["groups"]["pooled"]["all decision days"]
        here = results[window]["groups"]["pooled"]["all decision days"]
        out[window] = {"days_here": here["days"], "days_there": there["days"], "metrics": {
            m: {x: {"here": here[m]["means"][x], "there": there[m]["means"][x], "difference": here[m]["means"][x] - there[m]["means"][x]}
                for x in (S3, S3C) + BENCHMARKS} for m in ("grid_crps", "upper_tail_twcrps")}}
    return out


def score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    published_sha = panel_sha256(panel_path)
    panel = [row for row in load_daily_panel(panel_path) if row.date <= LAST_DAY]
    require_exploratory_window([row.date for row in panel], where="scripts/s3c_gse_1274")
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    register = policy_events.load_register()
    announcements = announced_iorb.load_announcements(c.IORB_TABLE)
    table = cal.TermTable(panel, announcements, decision_time=c.DECISION_TIME)
    gse_table = s3c_gse.GseTermTable(panel, announcements, decision_time=c.DECISION_TIME)
    dates = [row.date for row in panel]
    days = candidate_days(panel, dates, args.first)
    walks = {"base": walk_s3(panel, days, table, splits, registry), "ramp": walk_s3(panel, days, gse_table, splits, registry)}
    result: dict = {
        "issue": 1274, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha,
        "subset_from": None if args.first is None else args.first.isoformat(), "label": "development, not a verdict",
        "seed": SEED, "draws": args.draws, "reps": args.reps, "models": list(MODELS), "candidate": S3CG, "margin_bp": s3c_candidate.MARGIN_BP,
        "ramp": {"first_day": s3c_gse.FIRST_DAY, "last_day": s3c_gse.LAST_DAY, "replaces": TERM},
        "walk_days": len(days), "refit_effects": {"gse_ramp": refit_effects(walks["ramp"]), "flat_19_23": refit_effects(walks["base"])},
        "windows": {}, "reading_rules": declaration["reading_rules"],
    }
    for window in WINDOWS:
        result["windows"][window] = run_window(window, panel, splits, registry, table, register, walks, args)
    result["against_1255"] = against_1255(result["windows"]) if args.first is None else {}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ----------------------------------------------------------------------------------------------------------------


def words(row: Optional[dict]) -> str:
    """The reading on the mean-d bound, in bold once; `identical` for a group the arms score alike on every day."""

    if row is not None and row.get("identical"):
        return "identical"
    text = k.reading_words(row)
    return text if text.startswith("**") else f"**{text}**"


def cell(row: Optional[dict]) -> str:
    return "n/a" if row is None else (k._fmt(row) if row.get("identical") else f"{k._fmt(row)}: {words(row)}")


def _vs(group: Mapping[str, object], metric: str, reference: str) -> Optional[dict]:
    if group is None or metric not in group:
        return None
    return group[metric]["vs"].get(S3CG, {}).get(reference)


def mean_table(group: Mapping[str, object]) -> List[str]:
    out = ["| model | " + " | ".join(METRIC_TITLES[m] + " (mean)" for m in METRIC_NAMES) + " |", "|---|" + "---|" * len(METRIC_NAMES)]
    for m in MODELS:
        out.append(f"| {LABELS[m]} | " + " | ".join(f"{group[x]['means'][m]:.4f}" if x.startswith("brier") else f"{group[x]['means'][m]:.3f}" for x in METRIC_NAMES) + " |")
    return out


def against_table(group: Mapping[str, object]) -> List[str]:
    out = ["| (s3c-gse) against | " + " | ".join(METRIC_TITLES[m] for m in METRIC_NAMES) + " |", "|---|" + "---|" * len(METRIC_NAMES)]
    for ref in REFERENCES:
        out.append(f"| {LABELS[ref]} | " + " | ".join(cell(_vs(group, m, ref)) for m in METRIC_NAMES) + " |")
    return out


def split_table(w: Mapping[str, object], split: str, reference: str, metrics_: Sequence[str]) -> List[str]:
    labels = w["groups"].get(split, {})
    order = c.REGIMES if split == "regime" else sorted(labels)
    out = [f"| {split.replace('_', ' ')} | days | " + " | ".join(METRIC_TITLES[m] for m in metrics_) + " |", "|---|---|" + "---|" * len(metrics_)]
    for label in order:
        if label not in labels:
            continue
        g = labels[label]
        out.append(f"| {label} | {g['days']} | " + " | ".join(
            "not tested (fewer than 20 days)" if f"{split}/{label}" in w["skipped_groups"] else cell(_vs(g, m, reference)) for m in metrics_) + " |")
    return out if len(out) > 2 else []


def means_split_table(w: Mapping[str, object], split: str) -> List[str]:
    """The mean grid CRPS and Brier score of (s3), (s3c) and (s3c-gse) in each group of a split, tested or not."""

    labels = w["groups"].get(split, {})
    arms = (S3, S3C, S3CG)
    cols = [(x, m) for x in ("grid_crps", "brier_gt5") for m in arms]
    out = [f"| {split.replace('_', ' ')} | days | " + " | ".join(f"{METRIC_TITLES[x]} {LABELS[m]}" for x, m in cols) + " |", "|---|---|" + "---|" * len(cols)]
    for label in (c.REGIMES if split == "regime" else sorted(labels)):
        if label not in labels:
            continue
        g = labels[label]
        out.append(f"| {label} | {g['days']} | " + " | ".join(f"{g[x]['means'][m]:.4f}" for x, m in cols) + " |")
    return out if len(out) > 2 else []


def coverage_table(cover: Mapping[str, dict]) -> List[str]:
    out = ["| group | cells | " + " | ".join(f"{LABELS[m]} 90% band [90% interval]" for m in COVERAGE_MODELS) + " |", "|---|---|" + "---|" * len(COVERAGE_MODELS)]
    for group, models in cover.items():
        out.append(f"| {group} | {models[S3CG]['cells']:,} | " + " | ".join(
            f"{models[m]['rate']:.3f} [{models[m]['interval'][0]:.3f}, {models[m]['interval'][1]:.3f}]" for m in COVERAGE_MODELS) + " |")
    return out


def effect_table(effect: Mapping[str, dict], title: str) -> List[str]:
    """The term's fitted effect in bp by regime of the target day: bp per unit of the term (the shift on the 25th for the ramp, on any day of
    the 19th to 23rd for the flat flag) pooled over leads, the share of cells whose fit holds the term, and the mean shift applied on the
    target days that carry it."""

    out = [f"| {title}: regime of the target day | cells | fit holds the term | mean effect, bp per unit of the term | cells carrying the term | mean shift applied there, bp |",
           "|---|---|---|---|---|---|"]
    for regime in list(c.REGIMES) + ["all regimes"]:
        e = effect.get(regime, {}).get("all")
        if e is None:
            continue
        applied = "n/a" if e["mean_applied_bp"] is None else f"{e['mean_applied_bp']:+.3f}"
        out.append(f"| {regime} | {e['cells']:,} | {e['with_term'] / e['cells']:.1%} | {e['mean_bp_per_unit']:+.3f} | {e['carry']:,} | {applied} |")
    return out


def effect_by_lead(w: Mapping[str, object]) -> List[str]:
    out = ["| lead | (s3c-gse) ramp, bp per unit (the 25th) | (s3) flat 19th-23rd, bp per day |", "|---|---|---|"]
    for h in sp.HORIZONS:
        a, b = w["effect"]["gse_ramp"]["all regimes"][str(h)], w["effect"]["flat_19_23"]["all regimes"][str(h)]
        out.append(f"| h={h} | {a['mean_bp_per_unit']:+.3f} | {b['mean_bp_per_unit']:+.3f} |")
    return out


def headline(r: Mapping[str, object]) -> str:
    parts = []
    for window, text in (("2026", "On the 2026 development days"), ("development", "on the development window")):
        pooled = r["windows"].get(window, {}).get("groups", {}).get("pooled", {}).get("all decision days")
        if pooled is None:
            continue
        parts.append(f"{text}, grid CRPS, (s3c-gse) against (s3c): {cell(_vs(pooled, 'grid_crps', S3C))}; against (s3): {cell(_vs(pooled, 'grid_crps', S3))}")
    return "; ".join(parts) + "."


def ramp_sentence(r: Mapping[str, object]) -> str:
    """Where the arm moves the score, from the ramp-day split: (s3c-gse) against (s3c) on grid CRPS and twCRPS, on the target days the changed
    term is non-zero and on the others, by window. The intervals of these groups keep the current method."""

    parts = []
    for window, text in (("2026", "the 2026 days"), ("development", "the development window")):
        groups = r["windows"].get(window, {}).get("groups", {}).get(RAMP_SPLIT)
        if not groups:
            continue
        for label, name in ((RAMP_DAYS, "on the ramp days"), (OTHER_DAYS, "on the other days")):
            g = groups[label]
            parts.append(f"{text}, {name} ({g['days']} target days): " + ", ".join(
                f"{METRIC_TITLES[m]} {cell(_vs(g, m, S3C))}" for m in ("grid_crps", "upper_tail_twcrps")))
    return ("Against (s3c), by whether the changed term is non-zero on the target day (the intervals of these groups keep the current method, "
            "#1221): " + "; ".join(parts) + ".")


def render(r: dict) -> str:
    out = [
        "# (s3c-gse): the GSE cash cycle as a ramp from the 19th to the 25th, on (s3c) (#1274)", "",
        "**Does a ramp from the 19th to the 25th of the month, in place of the flat 19th-23rd term, improve (s3c)?** " + headline(r), "", ramp_sentence(r), "",
        "**Hypothesis and step:** H5 (primary goal), step 3, an arm on the candidate (s3c); ledger item 66 on #1116. **Development data, not a verdict** "
        "(scoring protocol v1, #640). Her ruling of 27 October 2026 (chat, relayed on #1274): queue four arms on (s3c), one directive each, independent of "
        "each other; this is the GSE-cycle ramp. **(s3c) stays the candidate until she rules on the result.** Nothing is registered or published and no "
        f"claim changes. Generated by `scripts/s3c_gse_1274.py page` from `docs/research/s3c-gse-1274/result.json`, not edited by hand; declared in "
        f"`{r['declaration']}` before any score. The page cites no source for the idea beyond her ruling and compares with no outside figure.", "",
        "**The arm.** (s3c) has one flat term for the 19th to the 23rd of the month (`dom_19_23`). **(s3c-gse)** replaces it with one ramp term on the target "
        "day's calendar date: 0 before the 19th and after the 25th, and on day d from the 19th to the 25th, (d - 18) / 7 (1/7 on the 19th, 4/7 on the 22nd, "
        "1 on the 25th). The shape is declared and not tuned. It is read from the target row's own date, on direct pairs, with no other input "
        "(`repo_model.s3c_gse`); where the 25th or the days before it fall on a weekend or a holiday there is no row for them and the term is read on the "
        "business days that remain, each keeping its own date's value. Every other term, the Huber fit, the ridge of 5, the direct pairs and the cap at "
        "the line from full allotment are (s3c)'s. A ramp term enters a lead's fit by the same minimum as the flag, counted as a sum of ramp values.", "",
        f"Panel digest `{r['panel_sha256']}`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, "
        f"{r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound). Positive mean d favours "
        "(s3c-gse). **A reading (gain, loss, undecided) is taken from the mean-d bound** (her ruling on #1009), with the skill interval beside it; for a "
        "Brier score the skill is the Brier skill score. **Caveat (Lens C, #958):** the lag-10 HAC standard error that studentizes the bound is understated "
        "about 2x after 2020, so an interval that excludes zero is narrower than it should be. The intervals of a group of target days (a regime, a month, "
        "a pressure-day type, the ramp days) keep the **current method** (the group's days, scattered, resampled in date order as if consecutive), which "
        "#1221 questions and #1228 will decide; no pressure-day type is read from them. Where two arms differ on few days of a group, some resamples have "
        "no long-run variance: the bound is then not computed, the unstudentized interval of mean d is given beside it, and no reading is taken from that. "
        "Groups of fewer than 20 days are listed with their means and not tested.", "",
        "**What kind of look this is.** The 2026 days were already seen by #845, the #151 final test, #1229, #1252 and #1255. This is a check on an arm "
        "of the candidate she chose, not evidence for a verdict. Before full allotment (s3c) is (s3), so on those days (s3c-gse) differs from (s3c) "
        "only through the ramp.", ""]
    ag = r.get("against_1255")
    for window in WINDOWS:
        w = r["windows"].get(window)
        if w is None:
            continue
        n, pooled = w["notes"], w["groups"]["pooled"]["all decision days"]
        out += [f"## {WINDOW_TITLES[window]}", "",
                f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); {w['refits']} refits of (s3) on the ramp table (the walk "
                f"covers every decision day from the start of the panel). The base-table walk of (s3) equals #1255's frame cell for cell on all "
                f"{w['walk_equals_frame_days']:,} scored decision days (the script refuses to write a record otherwise). Cells where (s3c-gse) differs "
                f"from (s3c): {w['cells_where_gse_differs_from_s3c']:,} of {w['cells']:,}; cells before full allotment equal the ramp walk's (s3): "
                f"{'yes' if w['before_full_allotment_is_the_ramp_walk'] else 'NO'}. Target days: {w['target_days']['all']:,}, of which "
                f"{w['target_days']['ramp']:,} on the 19th to the 25th; target days with SOFR - IORB above +5 bp: {w['positive_days_5']}.", ""]
        if ag and window in ag:
            a = ag[window]
            out += ["Reproduction of #1255 (same frame): pooled mean difference here minus there, " + "; ".join(
                f"{METRIC_TITLES[m]}: " + ", ".join(f"{LABELS[x]} {v['difference']:+.2e}" for x, v in rows.items()) for m, rows in a["metrics"].items())
                + f" ({a['days_here']} days here, {a['days_there']} there).", ""]
        out += ["### Mean scores (pooled)", ""] + mean_table(pooled) + ["", "### (s3c-gse) against each reference (pooled)", ""] + against_table(pooled) + [""]
        out += ["### 90% band coverage beside (s3c)'s", "",
                "The share of cells in which the realised spread lies in the q05-q95 band (nominal 0.90), with the stationary-bootstrap interval of #1229 "
                "(cells in date order).", ""] + coverage_table(w["coverage"]) + [""]
        out += ["### The fitted effect of the changed term, in bp", "",
                "The coefficient of the fit in use at each decision, in scale units, times the scale at the decision's anchor, averaged over the scored "
                "(decision day, lead) cells of each regime of the target day. For the ramp, bp per unit is the shift on the 25th; the shift on the 22nd "
                "is 4/7 of it. For (s3)'s flat flag it is the shift on each day of the 19th to the 23rd. \"Fit holds the term\" is the share of cells whose "
                "fit has the term (it enters when enough training pairs carry it).", ""]
        out += effect_table(w["effect"]["gse_ramp"], "(s3c-gse) ramp") + [""] + effect_table(w["effect"]["flat_19_23"], "(s3) flat 19th-23rd") + [""]
        out += ["By lead, all regimes:", ""] + effect_by_lead(w) + [""]
        for split, title in (("ramp_day", "By the days the changed term is non-zero"), ("regime", "By regime"), ("month", "By target month"),
                             ("pressure_day_type", "By pressure-day type of the target day"), ("lead", "By lead")):
            for ref in (S3C, S3):
                table = split_table(w, split, ref, METRIC_NAMES)
                if table:
                    out += [f"### {title}: (s3c-gse) against {LABELS[ref]}", ""] + table + [""]
        for split, title in (("ramp_day", "the days the changed term is non-zero"), ("regime", "regime"), ("pressure_day_type", "pressure-day type"),
                             ("lead", "lead")):
            for ref in BENCHMARKS:
                table = split_table(w, split, ref, ("grid_crps", "upper_tail_twcrps"))
                if table:
                    out += [f"### By {title}: (s3c-gse) against {LABELS[ref]}", ""] + table + [""]
        for split, title in (("ramp_day", "the ramp days"), ("regime", "regime"), ("month", "target month"), ("pressure_day_type", "pressure-day type")):
            table = means_split_table(w, split)
            if table:
                out += [f"### Mean scores of (s3), (s3c) and (s3c-gse) by {title}", ""] + table + [""]
        if w["skipped_groups"]:
            out += ["Groups of fewer than 20 days, listed and not tested: " + ", ".join(f"{x} ({n_})" for x, n_ in sorted(w["skipped_groups"].items())) + ".", ""]
    out += question()
    return "\n".join(out).rstrip() + "\n"


def question() -> List[str]:
    return [
        "## Questions for Eleonora (marked; defaults change no claim)", "",
        "**Question 1. What follows from this result.** (s3c) stays the H5 candidate. Whether (s3c-gse) replaces it, or joins the other arms on (s3c) "
        "(#1273, #1275, #1276) in one candidate, is a choice for her, and it rests on days already seen.", "",
        "**Options** (the default applies if you have not answered by the next 5 pm batch):", "",
        "1. **(s3c) stays the candidate and nothing changes** (default).",
        "2. **Draft a directive that tests (s3c-gse) prospectively**, on the confirmation days only, under the scoring protocol.",
        "3. **Hold this result until the other three arms are in, and rule on the four together** (which combine, in what order, and on what evidence).", ""]


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


@turn_days.with_legacy_flag
def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk (s3) on the ramp table, cap it, and score (s3c-gse) on both windows")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--reps", type=int, default=2000, help="bootstrap resamples of the unstudentized and the coverage intervals")
    s.add_argument("--workers", type=int, default=4)
    s.add_argument("--first", type=date.fromisoformat, default=None,
                   help="start the walk on this day (a subset, for the script's test only; the declared run omits it)")
    s.set_defaults(func=score)
    g = sub.add_parser("page", help="write the result page from a score file")
    g.add_argument("--score", required=True)
    g.add_argument("--output", required=True)
    g.set_defaults(func=page)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
