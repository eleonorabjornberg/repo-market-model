"""State-scaled calendar effects on scaled mean reversion, scored (#1145; H5 step 3, the fix of #1115).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every
choice is in `metadata/state_calendar_1145.json`, which this script refuses to read unless it is committed and unchanged. The arms
are `repo_model.spread_mr_state_calendar` ((a) #941's variant; (s1) terms in standardised units; (s2) (s1) and each term times the
as-of scarcity state; (s3) (s1) with a Huber fit and a heavier ridge; (s4) (s1) with the FOMC and IORB terms), scored with the
scorer of scoring protocol v1 (`repo_model.scoring_protocol`) against (a), B1, B1' (#960), B2, `spread_mr_ctx` (#761) and, when
its walks are supplied, `gbm_funding`, with the studentized stationary bootstrap of ruling 1, the Politis-White block beside it,
the scaled score of #967 beside the raw one, and the q95 exceedance and band coverage under both hit rules. Scored decision days
are those whose five targets are on or before 2025-12-31; no later day is read and no locked day is scored
(`docs/decisions/lockbox.md`). Nothing here is a verdict (scoring protocol v1, #640).

It reuses the helpers of `scripts/calendar_mr_1115.py` (the frame, the cells, the groups, the walk reader) and adds the scarcity
state, which is read from the measurement panel built from tracked fixtures only (`scripts/scarcity_validation.py`), no network.

The walks are fast (minutes); the paired tests are the long part (about an hour on 4 cores, as #1115). The comparison with
`gbm_funding` needs its walks, which come from Eleonora's Mac (`.claude/skills/long-run`); `score` scores what exists and says
what it left out. Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    # optional: WALKS/gbm_funding_h<h>.json (scripts/spread_distribution_634.py walk), all five leads
    PYTHONPATH=src python3 scripts/state_calendar_1145.py score --panel PUB.csv [--walks WALKS] \\
        --output docs/research/state-calendar-1145/result.json
    PYTHONPATH=src python3 scripts/state_calendar_1145.py page \\
        --score docs/research/state-calendar-1145/result.json --output docs/research/state-calendar-1145-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import multiprocessing
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


from repo_model import announced_iorb, b1_calendar as b1c, metrics  # noqa: E402
from repo_model import protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model import spread_mr_calendar as cal, spread_mr_state_calendar as sc, spread_mr_variants as var  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.scarcity import measurement_declaration, own_leg_states  # noqa: E402
from repo_model.splits import SplitError  # noqa: E402

c = _load("calendar_mr_1115")
s686, s761, b949 = c.s686, c.s761, c.b949
s967 = _load("scaled_score_967")
sv = _load("scarcity_validation")

DECLARATION = REPO / "metadata" / "state_calendar_1145.json"
SEED = 1145
LAST_DAY = c.LAST_DAY
DECISION_TIME = c.DECISION_TIME
MIN_GROUP_DAYS = c.MIN_GROUP_DAYS
GBM = "gbm_funding"
GBMS = (GBM,)
B1P = c.B1P
CTX = c.CTX
A = sc.ARM_A
S1, S2, S3, S4 = (arm.name for arm in sc.ARMS)
ARMS = sc.ARM_NAMES
BENCHMARKS = c.BENCHMARKS
MODELS = BENCHMARKS + ARMS
METRIC_NAMES = c.METRIC_NAMES
REGIMES = c.REGIMES
DAY_TYPES = c.DAY_TYPES
ORDINARY = c.ORDINARY
MEDIAN = c.MEDIAN
SCALED = "scaled_grid_crps"
STATE_MINIMUM_HISTORY = 20
#: The calibration measures of a cell: the q95 exceedance under both hit rules and the 50% and 90% bands, closed and open.
RATES = ("hit_above", "hit_at_or_above", "b50_closed", "b50_open", "b90_closed", "b90_open")
BANDS = {"b50": (sp.GRID.index(0.25), sp.GRID.index(0.75)), "b90": (sp.GRID.index(0.05), sp.GRID.index(0.95))}
Q95 = c.Q95


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


# -- the state -------------------------------------------------------------------------------------------------------


def decision_states(registry_path: Path) -> Dict[date, Optional[float]]:
    """The scarcity state a decision on each panel day could read, keyed by the DECISION day.

    The own-leg grid at horizon 1 is keyed by the scored day, which is the next panel day; so `states[panel[i].date]` is
    `grid[panel[i + 1].date]` (`metadata/state_calendar_1145.json`, `state`). The measurement panel is built from tracked fixtures
    only, and its dates are checked against the published panel's by `scarcity_validation.build_measurement_panel`.
    """

    with measurement_declaration(), tempfile.TemporaryDirectory() as tmp:
        build, _digest, registry, decision = sv.build_measurement_panel(registry_path, Path(tmp))
        scored = own_leg_states(
            build.observations, registry=registry, decision_time=decision, minimum_history=STATE_MINIMUM_HISTORY, horizon=1,
            end=LAST_DAY,
        )
        dates = [row.date for row in build.observations]
    grid = {entry.day: entry.state for entry in scored}
    return {dates[i]: grid.get(dates[i + 1]) for i in range(len(dates) - 1)}


# -- the frame -------------------------------------------------------------------------------------------------------


def build_frame(panel, splits, registry, table, states, first: Optional[date] = None):
    """The decision days with a forecast of every model, whose five targets are scored days.

    `first` starts the walk later than the declared study does; it exists for the test of this script, and the declared run never
    passes it.
    """

    frame = s686.Frame(panel, splits, registry, None)
    candidate_days = [
        day for i, day in enumerate(frame.dates)
        if i + max(sp.HORIZONS) < len(panel) and frame.dates[i + max(sp.HORIZONS)] <= LAST_DAY and (first is None or day >= first)
    ]
    s686.require_scored_days(candidate_days, LAST_DAY)
    settings = dict(registry=registry, decision_time=DECISION_TIME, splits=splits)
    b1, b1p, b2, dropped = {}, {}, {}, []
    for day in candidate_days:
        index = frame.position[day]
        try:
            one = pb.b1_forecast(panel, index, registry=registry, decision_time=DECISION_TIME)
            prime = b1c.b1_calendar_forecast(panel, index, **settings)
            two = pb.b2_forecast(panel, index, **settings)
        except (sp.ProtocolError, SplitError):
            dropped.append(day)
            continue
        b1[day], b1p[day], b2[day] = one, prime, two
    mine = sc.walk(panel, candidate_days, table, states, **settings)
    ctx = var.walk(panel, candidate_days, b2=b2, **settings)
    days = [d for d in candidate_days if d in b1 and all(d in mine.forecasts[a] for a in ARMS) and d in ctx.forecasts[CTX]]
    frame.days = days
    frame.forecasts = {"B1": b1, B1P: b1p, "B2": b2, CTX: ctx.forecasts[CTX], **{a: mine.forecasts[a] for a in ARMS}}
    for name in list(frame.forecasts):
        frame.forecasts[name] = {d: frame.forecasts[name][d] for d in days}
    unknown = sum(1 for d in days if mine.detail[d]["state"] is None)
    notes = {
        "decision_days_offered": len(candidate_days), "candidate_skipped_for_history": len(mine.skipped),
        "benchmark_missing": [d.isoformat() for d in dropped], "scored_decision_days": len(days),
        "first": days[0].isoformat(), "last": days[-1].isoformat(),
        "last_target": frame.target(days[-1], max(sp.HORIZONS)).isoformat(), "refits": len(mine.fits),
        "decisions_with_unknown_state": unknown,
    }
    return frame, notes, mine


# -- the cells -------------------------------------------------------------------------------------------------------


def cell_table(frame, forecasts: Mapping[date, Mapping[int, Sequence[float]]]) -> Dict[str, Dict[Tuple[date, int], float]]:
    """Both scores and the calibration hits of every (decision day, lead) cell of `forecasts`, after the scored days are checked."""

    days = sorted(forecasts)
    cells = {(d, h): frame.target(d, h) for d in days for h in sp.HORIZONS}
    s686.require_scored_days(set(d for d, _ in cells) | set(cells.values()), LAST_DAY)
    out: Dict[str, Dict[Tuple[date, int], float]] = {m: {} for m in METRIC_NAMES + RATES}
    for (d, h), t in cells.items():
        q, y = forecasts[d][h], frame.outcome[t]
        out["grid_crps"][(d, h)] = sp.grid_crps(q, y)
        out["upper_tail_twcrps"][(d, h)] = sp.upper_tail_twcrps(q, y)
        out["hit_above"][(d, h)] = 1.0 if y > q[Q95] else 0.0
        out["hit_at_or_above"][(d, h)] = 1.0 if y >= q[Q95] else 0.0
        for name, (lo, hi) in BANDS.items():
            out[f"{name}_closed"][(d, h)] = 1.0 if q[lo] <= y <= q[hi] else 0.0
            out[f"{name}_open"][(d, h)] = 1.0 if q[lo] < y < q[hi] else 0.0
    return out


def scaled_series(frame, cells: Mapping[str, Mapping[Tuple[date, int], float]], pool, scales, position) -> Dict[date, float]:
    """The scaled score of #967 of each decision day that has a scale: its cells over the scale of the target's reporting type."""

    out = {}
    for d in frame.days:
        i = position.get(d)
        if i is None or scales[i] is None:
            continue
        out[d] = s967.scaled_day([cells["grid_crps"][(d, h)] for h in sp.HORIZONS], pool.kinds[i], scales[i])
    return out


# -- the tests, in parallel ------------------------------------------------------------------------------------------

_STATE: Dict = {}


def pair_plan(candidate: str, have: Sequence[str]) -> List[str]:
    """What a candidate is tested against: the four references, (a), (s1) for the arms that differ from it by one thing, gbm."""

    names = list(BENCHMARKS)
    if candidate != A:
        names.append(A)
    if candidate in (S2, S3, S4):
        names.append(S1)
    names += [g for g in GBMS if g in have]
    return names


def _pairs_task(job):
    split, label, grain, metric, candidate, members = job
    series = _STATE["series"][(grain, metric)]
    out: Dict[str, dict] = {}
    for name in pair_plan(candidate, _STATE["gbm_have"]):
        days = [d for d in members if d in series[name]] if name in GBMS or grain == "scaled" else list(members)
        if len(days) < MIN_GROUP_DAYS:
            continue
        out[name] = s761.run_pairs({name: series[name]}, series[candidate], days, seed=SEED, draws=_STATE["draws"])[name]
    return (split, label, metric, candidate), out


def _block_task(job):
    """The Politis-White block of the paired loss differential of an arm against (a), and the pooled interval at that block."""

    split, label, grain, metric, candidate, members = job
    series = _STATE["series"][(grain, metric)]
    ordered = sorted(members)
    d = [series[A][x] - series[candidate][x] for x in ordered]
    try:
        block = b949.politis_white(d)
    except ValueError:
        return (split, label, metric, candidate), None
    entry = {"block": block, "days": len(ordered)}
    if split == "pooled":
        at = max(1, round(block))
        test = sp.paired_tests([({x: series[A][x] for x in ordered}, {x: series[candidate][x] for x in ordered})], seed=SEED,
                               draws=_STATE["draws"], block_length=float(at))[0]
        entry["at_block"] = at
        entry["row"] = s761.paired_row(test)
    return (split, label, metric, candidate), entry


def _interval_task(job):
    kind, key, values, block = job
    n = len(values)
    low, high = metrics.stationary_bootstrap_interval(
        lambda idx: sum(values[i] for i in idx) / len(idx), n, block_length=block, seed=SEED, replications=_STATE["reps"])
    return (kind, key), [low, high]


def _dispatch(job):
    kind, payload = job
    if kind == "pairs":
        return kind, _pairs_task(payload)
    if kind == "block":
        return kind, _block_task(payload)
    return kind, _interval_task(payload)


def run_jobs(jobs, workers: int):
    with multiprocessing.get_context("fork").Pool(workers) as pool:
        return pool.map(_dispatch, jobs, chunksize=1)


# -- the term effects ------------------------------------------------------------------------------------------------


def term_effects(frame, table: cal.TermTable, mine: sc.Walk) -> dict:
    """Per arm and term: for each flagged target day, the effect in bp and in scale units in force, and what (a) missed.

    For each flagged target day T (the term's flag at the lead's reading), the mean over the leads that forecast T of
    `scale(anchor) * (beta_j + gamma_j * s)` (bp) and `beta_j + gamma_j * s` (scale units) at the refit the forecast used (0 where
    the term was absent from it), and of the outcome less arm (a)'s median. Returned in date order for the intervals.
    """

    out: dict = {}
    for arm in sc.ARMS:
        per_term: Dict[str, Dict[date, Dict[str, List[float]]]] = {t: {} for t in cal.ALL_TERMS}
        for d in frame.days:
            used = mine.fit_used[d]
            detail = mine.detail[d]
            s_now = detail["state"] if arm.interact else None
            for h in sp.HORIZONS:
                t = frame.target(d, h)
                row = frame.position[t]
                estimate = mine.estimates[used][arm.name][h]
                median = frame.forecasts[A][d][h][MEDIAN]
                for term in cal.ALL_TERMS:
                    if table.flag(term, h, row):
                        cell = per_term[term].setdefault(t, {"bp": [], "std": [], "miss": []})
                        std = estimate.effect.get(term, 0.0) + estimate.slope.get(term, 0.0) * (0.0 if s_now is None else s_now)
                        cell["std"].append(std)
                        cell["bp"].append(detail["scale"] * std)
                        cell["miss"].append(frame.outcome[t] - median)
        out[arm.name] = {
            term: {t.isoformat(): {k: sum(v) / len(v) for k, v in cell.items()} for t, cell in sorted(days.items())}
            for term, days in per_term.items()
        }
    return out


def effect_intervals(effects: dict, frame, workers: int, reps: int) -> dict:
    """Per arm, term, regime and quantity: the mean over the flagged target days and its 90% interval (`>= 5` days)."""

    out: dict = {}
    jobs = []
    _STATE["reps"] = reps
    for arm, terms in effects.items():
        for term, days in terms.items():
            by_regime: Dict[str, List[str]] = {}
            for day in days:
                by_regime.setdefault(frame.regime(date.fromisoformat(day)), []).append(day)
            for regime, members in by_regime.items():
                cell = out.setdefault(arm, {}).setdefault(term, {}).setdefault(regime, {"days": len(members)})
                for quantity in ("bp", "std", "miss"):
                    values = [days[d][quantity] for d in sorted(members)]
                    cell[quantity] = {"mean": sum(values) / len(values), "interval": None}
                    if len(values) >= 5:
                        jobs.append(("interval", (quantity, (arm, term, regime), values, c.FLAG_BLOCK)))
    for _kind, ((quantity, (arm, term, regime)), interval) in run_jobs(jobs, workers):
        out[arm][term][regime][quantity]["interval"] = interval
    return out


# -- the score -------------------------------------------------------------------------------------------------------


def score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    panel = load_daily_panel(panel_path)
    splits = load_split_declaration(c.SPLITS)
    registry = json.loads(c.SOURCES.read_text(encoding="utf-8"))
    table = cal.TermTable(panel, announced_iorb.load_announcements(c.IORB_TABLE), decision_time=DECISION_TIME)
    states = decision_states(c.SOURCES)
    frame, notes, mine = build_frame(panel, splits, registry, table, states, args.first)
    published_sha = panel_sha256(panel_path)
    walks = Path(args.walks) if args.walks else None
    gbm_forecasts = {name: c.load_gbm(walks, published_sha, frame, name) for name in GBMS}
    gbm_forecasts = {k: v for k, v in gbm_forecasts.items() if v}
    days = frame.days
    labels = c.day_labels(frame, table)

    cells = {m: cell_table(frame, frame.forecasts[m]) for m in MODELS}
    gbm_frames = {name: cell_table(frame, {d: forecasts[d] for d in days if d in forecasts}) for name, forecasts in gbm_forecasts.items()}
    for m in MODELS:
        official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")

    # the scaled score of #967: the scale needs B2's cells over the trailing year of the pool, which starts before the first scored day
    pool = s967.build_pool(panel, splits, registry)
    scales = s967.trailing_scales(pool.decisions, pool.targets, pool.kinds, pool.s2)
    position = {d: i for i, d in enumerate(pool.decisions)}
    scaled = {m: scaled_series(frame, cells[m], pool, scales, position) for m in MODELS}
    scaled_gbm = {name: scaled_series(frame, table_, pool, scales, position) for name, table_ in gbm_frames.items()}
    scaled_days = sorted(scaled["B1"])

    groups = c.groups_of(frame, labels)
    series: Dict[Tuple[str, str], Dict[str, Dict[date, float]]] = {}
    for _s, _l, grain, _m in groups:
        for metric in METRIC_NAMES:
            if (grain, metric) not in series:
                entry = {m: c.series_of(frame, cells[m][metric], grain) for m in MODELS}
                for name, table_ in gbm_frames.items():
                    entry[name] = c.series_of(frame, table_[metric], grain)
                series[(grain, metric)] = entry
    series[("scaled", SCALED)] = {**scaled, **scaled_gbm}
    scaled_groups: List[Tuple[str, str, str, List[date]]] = [("scaled", "all decision days", "scaled", scaled_days)]
    for label in REGIMES:
        members = [d for d in scaled_days if frame.regime(d) == label]
        if members:
            scaled_groups.append(("scaled", label, "scaled", members))
    _STATE.update(series=series, draws=args.draws, reps=args.reps, gbm_have=tuple(gbm_frames))

    jobs, skipped = [], {}
    for split, label, grain, members in groups:
        if len(members) < MIN_GROUP_DAYS:
            skipped[f"{split}/{label}"] = len(members)
            continue
        for metric in METRIC_NAMES:
            for candidate in ARMS:
                jobs.append(("pairs", (split, label, grain, metric, candidate, tuple(members))))
                if candidate != A and split in ("pooled", "regime"):
                    jobs.append(("block", (split, label, grain, metric, candidate, tuple(members))))
    for split, label, grain, members in scaled_groups:
        if len(members) < MIN_GROUP_DAYS:
            skipped[f"{split}/{label}"] = len(members)
            continue
        for candidate in ARMS:
            jobs.append(("pairs", (split, label, grain, SCALED, candidate, tuple(members))))
    # calibration: the rates, pooled and by regime, with an interval over the cells in date order
    rate_models = {m: (cells[m] if m in cells else gbm_frames[m]) for m in list(MODELS) + list(gbm_frames)}
    cell_groups: Dict[Tuple[str, str], List[Tuple[date, int]]] = {}
    for m, table_ in rate_models.items():
        keys = sorted(table_["hit_above"])
        cell_groups[(m, "pooled/all cells")] = keys
        for regime in REGIMES:
            kept = [k for k in keys if frame.regime(frame.target(*k)) == regime]
            if len(kept) >= MIN_GROUP_DAYS:
                cell_groups[(m, f"regime/{regime}")] = kept
    for (m, name), keys in cell_groups.items():
        for rule in RATES:
            jobs.append(("interval", (rule, (m, name), [rate_models[m][rule][k] for k in keys], c.CELL_BLOCK)))
    done = run_jobs(jobs, args.workers)

    by_key = {(s_, l_): (g, m) for s_, l_, g, m in groups + scaled_groups}
    result: dict = {
        "issue": 1145, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha,
        "subset_from": None if args.first is None else args.first.isoformat(), "label": "development, not a verdict",
        "seed": SEED, "draws": args.draws, "reps": args.reps, "notes": notes, "models": list(MODELS), "gbm": sorted(gbm_frames),
        "arms": [{"name": a.name, "role": a.role, "location": list(a.location), "interact": a.interact, "robust": a.robust}
                 for a in sc.ARMS],
        "refits": [{"fitted_on": day.isoformat(), "phi": fit.phi} for day, fit in sorted(mine.fits.items())],
        "groups": {}, "skipped_groups": skipped, "politis_white": {}, "q95": {},
        "reading_rules": declaration["reading"]["rules"],
        "scaled": {"first_day": scaled_days[0].isoformat(), "days": len(scaled_days)},
    }
    for kind, (ident, payload) in done:
        if kind == "pairs":
            split, label, metric, candidate = ident
            entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(by_key[(split, label)][1])})
            entry.setdefault(metric, {"means": {}, "vs": {}})["vs"][candidate] = payload
        elif kind == "block":
            split, label, metric, candidate = ident
            result["politis_white"].setdefault(split, {}).setdefault(label, {}).setdefault(metric, {})[candidate] = payload
        else:
            rule, (m, name) = ident
            result["q95"].setdefault(name, {}).setdefault(m, {})[rule] = {"interval": payload}
    for split, labels_ in result["groups"].items():
        for label, entry in labels_.items():
            grain, members = by_key[(split, label)]
            for metric in list(METRIC_NAMES) + [SCALED]:
                if metric not in entry:
                    continue
                ser = series[(grain, metric)]
                entry[metric]["means"] = {
                    m: sum(ser[m][d] for d in members if d in ser[m]) / max(1, sum(1 for d in members if d in ser[m]))
                    for m in list(MODELS) + list(gbm_frames) if m in ser
                }
    for name, by_model in result["q95"].items():
        for m, rules in by_model.items():
            keys = cell_groups[(m, name)]
            for rule in rules:
                values = [rate_models[m][rule][k] for k in keys]
                rules[rule]["rate"] = sum(values) / len(values)
                rules[rule]["cells"] = len(values)
    result["q95_by_day_type"] = {}
    for label in DAY_TYPES + (ORDINARY,):
        result["q95_by_day_type"][label] = {}
        for m, table_ in rate_models.items():
            keys = [k for k in table_["hit_above"] if label in labels[frame.target(*k)]]
            if keys:
                result["q95_by_day_type"][label][m] = {
                    "cells": len(keys), **{rule: sum(table_[rule][k] for k in keys) / len(keys) for rule in RATES}}
    result["term_effects"] = term_effects(frame, table, mine)
    result["term_effect_intervals"] = effect_intervals(result["term_effects"], frame, args.workers, args.reps)
    result["day_type_counts"] = {k: sum(1 for t in labels if k in labels[t]) for k in DAY_TYPES + (ORDINARY,)}
    result["refit_term_counts"] = {
        arm.name: {term: [sum(1 for est in mine.estimates.values() if term in est[arm.name][h].effect) for h in sp.HORIZONS]
                   for term in cal.ALL_TERMS}
        for arm in sc.ARMS
    }
    result["refit_total"] = len(mine.estimates)
    passes = [est["sc_s3_robust"][h].iterations for est in mine.estimates.values() for h in sp.HORIZONS]
    result["robust_fits"] = {"fits": len(passes), "capped": sum(1 for x in passes if x >= sc.MAX_ITERATIONS),
                             "cap": sc.MAX_ITERATIONS, "mean_passes": sum(passes) / len(passes)}
    states_scored = [mine.detail[d]["state"] for d in days]
    result["state_mix"] = {str(level): sum(1 for s in states_scored if s is not None and abs(s - level / 3.0) < 1e-9) for level in range(4)}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page --------------------------------------------------------------------------------------------------------

LABELS = {"B1": "B1", B1P: "B1' (#960)", "B2": "B2", CTX: "spread_mr_ctx (#761)", GBM: "gbm_funding (#634)",
          A: "(a) base: #941 mad 20, floor 0.5"}
LABELS.update({a.name: a.role for a in sc.ARMS})
METRIC_TITLES = {"grid_crps": "grid CRPS (23 levels)", "upper_tail_twcrps": "upper-tail twCRPS (weight 1{z > 0 bp})",
                 SCALED: "scaled grid CRPS (#967)"}
verdict = c.verdict


def _fmt(row: Optional[dict]) -> str:
    return "–" if row is None else s761.skill_text(row)


def model_table(r: dict, cell: dict) -> List[str]:
    """Mean score of every model in one group, and each arm's skill over B1, B1', B2, spread_mr_ctx, (a), (s1) and gbm_funding."""

    gbm = [g for g in GBMS if g in r["gbm"]]
    out = ["| | mean | skill vs B1 [90%] | vs B1' | vs B2 | vs spread_mr_ctx | vs (a) | vs (s1)" + "".join(f" | vs {g}" for g in gbm) + " |",
           "|---|---|---|---|---|---|---|---|" + "---|" * len(gbm)]
    means = cell["means"]
    for name in list(BENCHMARKS) + gbm:
        if name in means:
            out.append(f"| {LABELS[name]} | {means[name]:.3f} |" + " |" * (6 + len(gbm)))
    for name in ARMS:
        vs = cell["vs"].get(name, {})
        cells = ([_fmt(vs.get(b)) for b in ("B1", B1P, "B2", CTX)] + ["" if name == A else _fmt(vs.get(A))]
                 + [_fmt(vs.get(S1)) if name in (S2, S3, S4) else ""] + [_fmt(vs.get(g)) for g in gbm])
        out.append(f"| {LABELS[name]} | {means[name]:.3f} | " + " | ".join(cells) + " |")
    return out


def tally(r: dict, arm: str, metric: str = "grid_crps") -> Dict[str, int]:
    """The number of regimes (by target day) in which the arm's skill over (a) is read as a gain, a loss and undecided."""

    count = {"gain": 0, "loss": 0, "undecided": 0}
    for label in REGIMES:
        entry = r["groups"].get("regime", {}).get(label)
        if entry is not None:
            count[verdict(entry[metric]["vs"].get(arm, {}).get(A))] += 1
    return count


def render(r: dict) -> str:
    n = r["notes"]
    out = [
        "# State-scaled calendar effects on scaled mean reversion (#1145)", "",
        "**Hypothesis and step:** H5 (primary goal), step 3, calendar first (the fix of #1115). **Development data, not a verdict** (scoring "
        f"protocol v1, #640): days to {n['last_target']}, no lockbox day. Nothing is adopted and no claim changes. Generated by "
        f"`scripts/state_calendar_1145.py page` from `docs/research/state-calendar-1145/result.json`, not edited by hand; declared in "
        f"`{r['declaration']}` before any number.", "",
        f"Panel digest `{r['panel_sha256'][:8]}…`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, "
        f"{r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound); skill is "
        "`mean(d) / mean(S(benchmark))` with `d = S(benchmark) - S(candidate)`, positive favours the candidate. Scored decision days: "
        f"{n['scored_decision_days']:,} ({n['first']} to {n['last']}); the fit is renewed {n['refits']} times. B1' (Lens C's calendar-aware "
        "persistence, #960) is reported beside B1 in every table; B1 stays the protocol's benchmark.", "",
        "**Why.** #1115 estimated one effect in bp per calendar term and applied it everywhere, so it lost in 2020 and 2021-23, where the "
        "state is quiet, and won in 2024 and 2025-26. Here the effect scales with the state. The arms, all on #941's variant (a) unchanged "
        "and all reading the calendar at the target day on direct pairs: **(s1)** each term is estimated in the model's standardised units, "
        "so its effect in bp is the term times the anchor's as-of scale; **(s2)** (s1), and each term is also interacted with the as-of "
        "scarcity state (the own-leg state of #586 over 3: 0 on the floor, 1 when scarce), the coupon and bill settlements being two "
        "terms; **(s3)** (s1) with a Huber fit and a heavier ridge, so an outlier day does not set the effect and a term with few flagged "
        "days is shrunk toward 0; **(s4)** (s1) with the FOMC and IORB terms, the separate arm. The terms are #1115's, minus FOMC and IORB "
        "in (s1) to (s3): #1115 ran no per-term ablation, so no other term was shown to hurt on every reading, and none is dropped.", ""]
    if r["gbm"]:
        out += ["The `gbm_funding` comparison uses the walks supplied, on the decision days both cover.", ""]
    else:
        out += ["**The `gbm_funding` walks were not supplied**, so no row compares an arm with it; they are a long run that exists on "
                "Eleonora's Mac (`needs-mac`, the same `score` command with `--walks`). #1115's figure for (a) against it is +6.8% pooled "
                "[+3.3%, +10.1%].", ""]
    out += ["## Does an arm beat (a)?", "",
            "Skill of each arm over (a), pooled, with the 90% interval; the regimes (by target day) read as gain / loss / undecided under the "
            "declared rule (the interval excludes zero); and the reading on ordinary days and on the calendar days. Beating (a) is "
            "Eleonora's reading of this page.", "",
            "| arm | grid CRPS vs (a) | twCRPS vs (a) | regimes, grid CRPS (gain / loss / undecided) | ordinary days | calendar days | vs B1' pooled | vs B2 pooled |",
            "|---|---|---|---|---|---|---|---|"]
    pooled = r["groups"]["pooled"]["all decision days"]
    for arm in sc.ARMS:
        t = tally(r, arm.name)
        ordv = r["groups"].get("target_day_type", {}).get(ORDINARY, {}).get("grid_crps", {}).get("vs", {}).get(arm.name, {}).get(A)
        calv = r["groups"].get("target_day_type", {}).get("calendar_days", {}).get("grid_crps", {}).get("vs", {}).get(arm.name, {}).get(A)
        out.append(
            f"| {LABELS[arm.name]} | {_fmt(pooled['grid_crps']['vs'][arm.name].get(A))} | {_fmt(pooled['upper_tail_twcrps']['vs'][arm.name].get(A))} "
            f"| {t['gain']} / {t['loss']} / {t['undecided']} | {_fmt(ordv)} | {_fmt(calv)} "
            f"| {_fmt(pooled['grid_crps']['vs'][arm.name].get(B1P))} | {_fmt(pooled['grid_crps']['vs'][arm.name].get('B2'))} |")
    out.append("")
    for split, title in (("pooled", "Pooled"), ("lead", "By lead")):
        for label, entry in r["groups"].get(split, {}).items():
            for metric in METRIC_NAMES:
                out += [f"## {title}: {label}, {METRIC_TITLES[metric]}, mean over leads 1 to 5 (bp)" if split == "pooled"
                        else f"### {label}, {METRIC_TITLES[metric]}", ""] + model_table(r, entry[metric]) + [""]
    for split, title, order in (("regime", "regime (target day)", REGIMES),
                                ("target_day_type", "target-day type (the groups overlap)", list(DAY_TYPES) + [ORDINARY, "calendar_days"])):
        for metric in METRIC_NAMES:
            out += [f"## {METRIC_TITLES[metric]} by {title}", ""]
            for label in order:
                entry = r["groups"].get(split, {}).get(label)
                if entry is None:
                    continue
                out += [f"**{label}** ({entry['days']} days)", ""] + model_table(r, entry[metric]) + [""]
    if r["skipped_groups"]:
        out += ["Groups with fewer than %d days are listed and not tested: %s." % (
            MIN_GROUP_DAYS, ", ".join(f"{k} ({v})" for k, v in sorted(r["skipped_groups"].items()))), ""]
    out += ["## The scaled score beside the raw one (#967)", "",
            "Each cell of a decision day divided by the scale of its target's reporting day type (the median of B2's grid CRPS over the "
            f"trailing 252 pool positions, the last 6 left out); the first scaled day is {r['scaled']['first_day']} ({r['scaled']['days']:,} "
            "decision days). By the regime of the decision day.", ""]
    for label, entry in r["groups"].get("scaled", {}).items():
        out += [f"**{label}** ({entry['days']} days)", ""] + model_table(r, entry[SCALED]) + [""]
    out += ["## Reading under the declared rules", ""]
    for name in (S1, S2, S3, S4):
        parts = []
        for split in ("pooled", "regime", "target_day_type"):
            for label, entry in r["groups"].get(split, {}).items():
                parts.append(f"{label}: {verdict(entry['grid_crps']['vs'].get(name, {}).get(A))}")
        out.append(f"- **{LABELS[name]}**, grid CRPS against (a): " + "; ".join(parts) + ".")
    out.append("")
    for name, other, what in ((S2, S1, "the state"), (S3, S1, "the robust estimator"), (S4, S1, "the FOMC and IORB terms")):
        row = pooled["grid_crps"]["vs"][name].get(S1)
        tw = pooled["upper_tail_twcrps"]["vs"][name].get(S1)
        out.append(f"- {LABELS[name]} against (s1) isolates {what}: grid CRPS {_fmt(row)}; twCRPS {_fmt(tw)}.")
    out.append("")
    out += ["## The Politis-White block beside the block of 10", "",
            "The automatic block length (Politis and White 2004, with the correction of Patton, Politis and White 2009) of the paired loss "
            "differential `S(a) - S(arm)`, in days, with the pooled skill over (a) at that block. Reported, never substituted for 10.", ""]
    columns = ["pooled"] + [l for l in REGIMES if l in r["politis_white"].get("regime", {})]
    for metric in METRIC_NAMES:
        out += [f"{METRIC_TITLES[metric]}:", "", "| | " + " | ".join(columns) + " | pooled skill vs (a) at that block |", "|---|" + "---|" * (len(columns) + 1)]
        for name in (S1, S2, S3, S4):
            cells, at = [], ""
            for col in columns:
                split, label = ("pooled", "all decision days") if col == "pooled" else ("regime", col)
                e = r["politis_white"].get(split, {}).get(label, {}).get(metric, {}).get(name)
                cells.append("n/a" if not e else f"{e['block']:.1f}")
                if col == "pooled" and e and "row" in e:
                    at = f"block {e['at_block']}: {_fmt(e['row'])}"
            out.append(f"| {LABELS[name]} | " + " | ".join(cells) + f" | {at} |")
        out.append("")
    names = list(r["q95"])
    for rule, title in (("hit_above", "the 95th-percentile exceedance rate, hit when `y > q` (nominal 0.05)"),
                        ("hit_at_or_above", "the 95th-percentile exceedance rate, hit when `y >= q` (nominal 0.05)"),
                        ("b50_closed", "the central 50% band (q25 to q75), closed: `q25 <= y <= q75` (nominal 0.50)"),
                        ("b50_open", "the central 50% band, open: `q25 < y < q75` (nominal 0.50)"),
                        ("b90_closed", "the central 90% band (q05 to q95), closed (nominal 0.90)"),
                        ("b90_open", "the central 90% band, open (nominal 0.90)")):
        out += [f"## Calibration: {title}", "", "Share of (decision day, lead) cells, with a 90% stationary-bootstrap percentile interval over the cells in "
                "date order (mean block 50 cells).", "", "| | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
        for m in list(MODELS) + list(r["gbm"]):
            cells = []
            for name in names:
                e = r["q95"][name].get(m, {}).get(rule)
                cells.append("n/a" if e is None else f"{e['rate']:.3f} [{e['interval'][0]:.3f}, {e['interval'][1]:.3f}]")
            out.append(f"| {LABELS[m]} | " + " | ".join(cells) + " |")
        out.append("")
        if rule in ("hit_above", "b90_closed"):
            labels = list(r["q95_by_day_type"])
            out += [f"By target-day type (no interval, the days of a type are scattered):", "", "| | " + " | ".join(labels) + " |", "|---|" + "---|" * len(labels)]
            for m in list(MODELS) + list(r["gbm"]):
                out.append(f"| {LABELS[m]} | " + " | ".join(
                    f"{r['q95_by_day_type'][l][m][rule]:.3f}" if m in r["q95_by_day_type"][l] else "n/a" for l in labels) + " |")
            out.append("")
    out += ["The 95th-percentile and band rates under the other hit rule agree with these to within a tie of the outcome with a quantile; "
            "which rule counts is Eleonora's open question (#993), so both are above and in `result.json`.", ""]
    out += ["## The estimated effect of each term, by regime", "",
            "For each term, the effect in force on the flagged target days of the regime: the mean over the leads that forecast the day of "
            "`scale(anchor) * (beta + gamma * s)` at the refit the forecast used (0 where the term was absent from that refit), then the mean "
            "over the flagged days, in bp, with the 90% stationary-bootstrap percentile interval over those days in date order (mean block 10 "
            "flagged days; none under 5 days). The interval measures the spread of the estimates across refits and days, not a standard "
            "error of the effect. The number of flagged days is in brackets.", ""]

    def cell_text(e: Optional[dict], quantity: str, places: int = 2) -> str:
        if e is None:
            return "–"
        q = e[quantity]
        text = f"{q['mean']:+.{places}f}"
        if q["interval"] is not None:
            text += f" [{q['interval'][0]:+.{places}f}, {q['interval'][1]:+.{places}f}]"
        return text + f" ({e['days']})"

    for arm in sc.ARMS:
        for quantity, title, places in (("bp", "effect (bp)", 2), ("std", "effect (scale units)", 3)):
            out += [f"**{LABELS[arm.name]}: {title}**", "", "| term | " + " | ".join(REGIMES) + " |", "|---|" + "---|" * len(REGIMES)]
            terms = arm.location
            for term in terms:
                out.append(f"| {term} | " + " | ".join(
                    cell_text(r["term_effect_intervals"].get(arm.name, {}).get(term, {}).get(l), quantity, places) for l in REGIMES) + " |")
            out.append("")
    out += [f"**Missed by (a)**: the mean outcome less (a)'s median on the same flagged days, in bp", "", "| term | " + " | ".join(REGIMES) + " |",
            "|---|" + "---|" * len(REGIMES)]
    for term in cal.ALL_TERMS:
        out.append(f"| {term} | " + " | ".join(
            cell_text(r["term_effect_intervals"].get(S4, {}).get(term, {}).get(l), "miss") for l in REGIMES) + " |")
    out.append("")
    out += [f"Refits in which each term entered the fit (of {r['refit_total']} refits), by lead 1 to 5, arm (s4):", "",
            "| term | " + " | ".join(f"h={h}" for h in sp.HORIZONS) + " |", "|---|" + "---|" * len(sp.HORIZONS)]
    for term, counts in r["refit_term_counts"][S4].items():
        out.append(f"| {term} | " + " | ".join(str(x) for x in counts) + " |")
    mix = r["state_mix"]
    out += ["", f"The scarcity state of the scored decisions: abundant {mix['0']}, ample {mix['1']}, tight {mix['2']}, scarce {mix['3']}; "
            f"unknown {r['notes']['decisions_with_unknown_state']}. The Huber fit of (s3) took {r['robust_fits']['mean_passes']:.1f} passes on average "
            f"and reached its cap of {r['robust_fits']['cap']} passes (without the coefficients settling to 1e-8) in {r['robust_fits']['capped']} of "
            f"{r['robust_fits']['fits']} fits (refit by lead).", ""]
    out += ["## What this is not", "",
            "Development data from 2018 to 2025, split by regime and target-day type, never a verdict. The arms read the calendar at the target "
            "day on direct pairs, so their class is not provisional (`docs/research/provisional-calendar-register.md`), but the estimation "
            "choices (the state mapping, the ridges, Huber's threshold, the 0/1 coupon flag in place of the settlement's size) are this "
            "study's own, were not tuned, and are open to Eleonora's review. #941's variant was itself chosen after seeing 2018-2025. "
            "Whether an arm replaces (a) as the H5 candidate is her decision.", ""]
    out += question(r)
    return "\n".join(out) + "\n"


def question(r: dict) -> List[str]:
    """The closing question for Eleonora (her ruling of 22 October 2026 on #1145: an arm replaces (a) only if it beats (a))."""

    groups = r["groups"]
    cols = [("pooled", "all decision days", "pooled")] + [("regime", l, l) for l in REGIMES if l in groups.get("regime", {})] + [
        ("target_day_type", l, l) for l in [ORDINARY, "calendar_days"] if l in groups.get("target_day_type", {})]
    models = [GBM] * (GBM in r["gbm"]) + [A, S1, S2, S3, S4]
    out = ["## Question for Eleonora: does a state-scaled arm replace (a) as the H5 candidate?", "",
           "Your ruling of 22 October 2026 on #1145: an arm replaces (a), #941's scaled mean reversion, as the H5 candidate only if it beats "
           "(a); that is your decision on this page's evidence. **Nothing is adopted here and no claim changes.** The tables give the mean "
           "score of (a) and the four arms, pooled, by regime and by ordinary and calendar days (lower is better; B1, B1' and B2 are in the "
           "tables above)."
           + ("" if r["gbm"] else " **The `gbm_funding` rows are empty: its walks were not on the machine that scored this page.**"), ""]
    for metric, title in (("grid_crps", "Grid CRPS (bp)"), ("upper_tail_twcrps", "Upper-tail twCRPS (bp)")):
        out += [f"**{title}**", "", "| | " + " | ".join(col[2] for col in cols) + " |", "|---|" + "---|" * len(cols)]
        for m in models:
            cells = []
            for split, label, _name in cols:
                entry = groups.get(split, {}).get(label)
                cells.append("n/a" if entry is None or m not in entry[metric]["means"] else f"{entry[metric]['means'][m]:.3f}")
            out.append(f"| {LABELS[m]} | " + " | ".join(cells) + " |")
        out.append("")
    out += ["**Options** (numbered; the default applies if you have not answered by the next 5 pm batch):", "",
            "1. **Keep (a) as the H5 candidate** (default). Nothing changes; the state-scaled terms stay a development result.",
            "2. **Replace (a) with one of the arms (which: your choice)**, on the evidence above. That is a decision for you and would be "
            "followed by a registration discussion; this page does not pre-empt it.",
            "3. **Ask for a further step** before deciding (for example the settlement's size in place of its 0/1 flag in (s2), or the arms "
            "on the 2026 development days).", ""]
    return out


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk the arms and score them")
    s.add_argument("--panel", required=True)
    s.add_argument("--walks", help="a directory holding gbm_funding_h<lead>.json")
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--reps", type=int, default=2000, help="bootstrap resamples of a rate or effect interval")
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
