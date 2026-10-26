"""Why (s3) wins: the ridge and the Huber fit apart, the settlement's size, and #1153's v4 on (s3), scored (#1172; H5 step 3).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every
choice is in `metadata/s3_decomposition_1172.json`, which this script refuses to read unless it is committed and unchanged. The arms are
`repo_model.spread_mr_state_calendar`'s ((s1) terms in standardised units; (r1) (s1) with the ridge of 5 alone; (r2) (s1) with the Huber
fit alone; (s3) both; (r3) (s3) with the announced size of the coupon and bill settlements times the scarcity state in place of the 0/1
flags) and `repo_model.spread_mr_s3_v4` ((v4) miss feedback and a calendar-type scale factor, #1153, on (s3)), scored with the scorer of
scoring protocol v1 (`repo_model.scoring_protocol`) against (s3), (a), B1, B1' (#960) and B2 and, when its walks are supplied,
`gbm_funding`, with the studentized stationary bootstrap of ruling 1 (read on the bound on mean d, her #1009 ruling, with the skill
interval beside), the Politis-White block beside it, the scaled score of #967 beside the raw one, and the q95 exceedance and band
coverage under both hit rules. Scored decision days are those whose five targets are on or before 2025-12-31; no later day is read and
no locked day is scored (`docs/decisions/lockbox.md`). Nothing here is a verdict (scoring protocol v1, #640).

It reuses the helpers of `scripts/calendar_mr_1115.py` and `scripts/state_calendar_1145.py` (the frame, the cells, the groups, the
state, the walk reader). The scarcity state is read from the measurement panel built from tracked fixtures only, no network.

The walks take minutes; the paired tests are the long part (about 40 minutes on 4 cores, as #1145), so the run is a cloud run. The
comparison with `gbm_funding` needs its walks, which come from Eleonora's Mac (`.claude/skills/long-run`) and are not run first.
Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    # optional: WALKS/gbm_funding_h<h>.json (scripts/spread_distribution_634.py walk), all five leads
    PYTHONPATH=src python3 scripts/s3_decomposition_1172.py score --panel PUB.csv [--walks WALKS] \\
        --output docs/research/s3-decomposition-1172/result.json
    PYTHONPATH=src python3 scripts/s3_decomposition_1172.py page \\
        --score docs/research/s3-decomposition-1172/result.json --output docs/research/s3-decomposition-1172-result.md

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


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


from repo_model import announced_iorb, b1_calendar as b1c, metrics  # noqa: E402
from repo_model import protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model import spread_mr_calendar as cal, spread_mr_s3_v4 as v4m, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.splits import SplitError  # noqa: E402

c = _load("calendar_mr_1115")
s686, s761, b949 = c.s686, c.s761, c.b949
s967 = _load("scaled_score_967")
sv = _load("scarcity_validation")
d1145 = _load("state_calendar_1145")

DECLARATION = REPO / "metadata" / "s3_decomposition_1172.json"
SEED = 1172
LAST_DAY = c.LAST_DAY
DECISION_TIME = c.DECISION_TIME
MIN_GROUP_DAYS = c.MIN_GROUP_DAYS
GBM = "gbm_funding"
GBMS = (GBM,)
B1P = c.B1P
A = sc.ARM_A
S1, R1, R2, S3, R3 = (arm.name for arm in sc.DECOMPOSITION)
V4 = v4m.ARM_NAME
#: The arms scored against the references, (a) first; (v4) is not a `spread_mr_state_calendar` arm.
ARMS = (A,) + tuple(arm.name for arm in sc.DECOMPOSITION) + (V4,)
BENCHMARKS = ("B1", B1P, "B2")
MODELS = BENCHMARKS + ARMS
#: Each arm differs from the reference named here by one thing: what the pair isolates.
ISOLATES = {R1: (S1, "the ridge of 5"), R2: (S1, "the Huber fit"), S3: (S1, "both"), R3: (S3, "the settlement size times the state"),
            V4: (S3, "the miss and calendar-type scale factors")}
METRIC_NAMES = c.METRIC_NAMES
REGIMES = c.REGIMES
DAY_TYPES = c.DAY_TYPES
ORDINARY = c.ORDINARY
MEDIAN = c.MEDIAN
SCALED = "scaled_grid_crps"
#: The kill rule of the issue: (r1) and (r2) each recover less than this share of (s3)'s gain over (a).
KILL_SHARE = 0.5
#: The calibration measures of a cell: the q95 exceedance under both hit rules and the 50% and 90% bands, closed and open.
RATES = ("hit_above", "hit_at_or_above", "b50_closed", "b50_open", "b90_closed", "b90_open")
Q95 = c.Q95


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


# -- the state -------------------------------------------------------------------------------------------------------


def decision_states(registry_path: Path) -> Dict[date, Optional[float]]:
    """The scarcity state a decision on each panel day could read, keyed by the DECISION day (`state_calendar_1145.decision_states`)."""

    return d1145.decision_states(registry_path)


# -- the frame -------------------------------------------------------------------------------------------------------


def build_frame(panel, splits, registry, table, states, sizes, first: Optional[date] = None):
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
    mine = sc.walk(panel, candidate_days, table, states, sc.DECOMPOSITION, sizes=sizes, **settings)
    layered = v4m.walk(panel, mine, S3, table, **settings)
    arm_names = (A,) + tuple(arm.name for arm in sc.DECOMPOSITION)
    days = [d for d in candidate_days if d in b1 and all(d in mine.forecasts[a] for a in arm_names) and d in layered.forecasts]
    frame.days = days
    frame.forecasts = {"B1": b1, B1P: b1p, "B2": b2, **{a: mine.forecasts[a] for a in arm_names}, V4: layered.forecasts}
    for name in list(frame.forecasts):
        frame.forecasts[name] = {d: frame.forecasts[name][d] for d in days}
    unknown = sum(1 for d in days if mine.detail[d]["state"] is None)
    notes = {
        "decision_days_offered": len(candidate_days), "candidate_skipped_for_history": len(mine.skipped),
        "v4_skipped": [d.isoformat() for d in layered.skipped],
        "benchmark_missing": [d.isoformat() for d in dropped], "scored_decision_days": len(days),
        "first": days[0].isoformat(), "last": days[-1].isoformat(),
        "last_target": frame.target(days[-1], max(sp.HORIZONS)).isoformat(), "refits": len(mine.fits),
        "decisions_with_unknown_state": unknown,
    }
    return frame, notes, mine, layered


# -- the cells -------------------------------------------------------------------------------------------------------


def cell_table(frame, forecasts: Mapping[date, Mapping[int, Sequence[float]]]) -> Dict[str, Dict[Tuple[date, int], float]]:
    """Both scores and the calibration hits of every (decision day, lead) cell of `forecasts` (`state_calendar_1145.cell_table`)."""

    return d1145.cell_table(frame, forecasts)


def scaled_series(frame, cells, pool, scales, position) -> Dict[date, float]:
    """The scaled score of #967 of each decision day that has a scale (`state_calendar_1145.scaled_series`)."""

    return d1145.scaled_series(frame, cells, pool, scales, position)


# -- the tests, in parallel ------------------------------------------------------------------------------------------

_STATE: Dict = {}


def pair_plan(candidate: str, have: Sequence[str]) -> List[str]:
    """What a candidate is tested against: B1, B1' and B2, (a), (s3) for every arm but (a) and (s3), the arm it differs from by one
    thing (`ISOLATES`), and gbm."""

    names = list(BENCHMARKS)
    if candidate != A:
        names.append(A)
    if candidate not in (A, S3):
        names.append(S3)
    if candidate in ISOLATES and ISOLATES[candidate][0] not in names:
        names.append(ISOLATES[candidate][0])
    names += [g for g in GBMS if g in have]
    return names


def block_plan(candidate: str) -> List[str]:
    """What the Politis-White block is reported against: (a) for every arm, and (s3) for the arms that are not (s3)'s corners."""

    if candidate == A:
        return []
    return [A] + ([S3] if candidate not in (S1, S3) else [])


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
    """The Politis-White block of the paired loss differential of an arm against each reference of `block_plan`, and the pooled
    interval at that block."""

    split, label, grain, metric, candidate, members = job
    series = _STATE["series"][(grain, metric)]
    ordered = sorted(members)
    out: Dict[str, Optional[dict]] = {}
    for reference in block_plan(candidate):
        d = [series[reference][x] - series[candidate][x] for x in ordered]
        try:
            block = b949.politis_white(d)
        except ValueError:
            out[reference] = None
            continue
        entry = {"block": block, "days": len(ordered)}
        if split == "pooled":
            at = max(1, round(block))
            test = sp.paired_tests([({x: series[reference][x] for x in ordered}, {x: series[candidate][x] for x in ordered})],
                                   seed=SEED, draws=_STATE["draws"], block_length=float(at))[0]
            entry["at_block"] = at
            entry["row"] = s761.paired_row(test)
        out[reference] = entry
    return (split, label, metric, candidate), out


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


def term_effects(frame, table: cal.TermTable, sizes: sc.SizeTable, mine: sc.Walk) -> dict:
    """Per arm and term: for each flagged target day, the effect in bp and in scale units in force, and what (a) missed.

    For each flagged target day T (the term's flag at the lead's reading), the mean over the leads that forecast T of
    `scale(anchor) * x_j * beta_j` (bp) and `x_j * beta_j` (scale units) at the refit the forecast used (0 where the term was absent
    from it), with `x_j` the term's 0/1 flag, or for a sized settlement term of (r3) `size / 100 * state`, and of the outcome less
    arm (a)'s median. Returned in date order for the intervals. (v4) has no term of its own: it is (s3)'s terms with a scale factor.
    """

    out: dict = {}
    for arm in sc.DECOMPOSITION:
        per_term: Dict[str, Dict[date, Dict[str, List[float]]]] = {t: {} for t in cal.ALL_TERMS}
        for d in frame.days:
            used = mine.fit_used[d]
            detail = mine.detail[d]
            s_now = detail["state"] if (arm.interact or arm.sized) else None
            for h in sp.HORIZONS:
                t = frame.target(d, h)
                row = frame.position[t]
                estimate = mine.estimates[used][arm.name][h]
                median = frame.forecasts[A][d][h][MEDIAN]
                for term in cal.ALL_TERMS:
                    if table.flag(term, h, row):
                        cell = per_term[term].setdefault(t, {"bp": [], "std": [], "miss": []})
                        x = sc.regressor(term, {term: 1}, sizes.sizes_at(h, row) if arm.sized else {}, s_now, arm.sized)
                        std = (estimate.effect.get(term, 0.0) * x
                               + estimate.slope.get(term, 0.0) * (0.0 if s_now is None else s_now))
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
    sizes = sc.SizeTable(panel)
    frame, notes, mine, layered = build_frame(panel, splits, registry, table, states, sizes, args.first)
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
        "issue": 1172, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha,
        "subset_from": None if args.first is None else args.first.isoformat(), "label": "development, not a verdict",
        "seed": SEED, "draws": args.draws, "reps": args.reps, "notes": notes, "models": list(MODELS), "gbm": sorted(gbm_frames),
        "arms": [{"name": a.name, "role": a.role, "location": list(a.location), "interact": a.interact, "robust": a.robust,
                  "ridge": sc.ridge_of(a), "sized": a.sized} for a in sc.DECOMPOSITION],
        "v4": {"name": V4, "on": S3, "role": LABELS[V4]},
        "refits": [{"fitted_on": day.isoformat(), "phi": fit.phi} for day, fit in sorted(mine.fits.items())],
        "groups": {}, "skipped_groups": skipped, "politis_white": {}, "q95": {},
        "reading_rules": declaration["reading_rules"],
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
    result["term_effects"] = term_effects(frame, table, sizes, mine)
    result["term_effect_intervals"] = effect_intervals(result["term_effects"], frame, args.workers, args.reps)
    result["day_type_counts"] = {k: sum(1 for t in labels if k in labels[t]) for k in DAY_TYPES + (ORDINARY,)}
    result["refit_term_counts"] = {
        arm.name: {term: [sum(1 for est in mine.estimates.values() if term in est[arm.name][h].effect) for h in sp.HORIZONS]
                   for term in cal.ALL_TERMS}
        for arm in sc.DECOMPOSITION
    }
    result["refit_total"] = len(mine.estimates)
    result["robust_fits"] = {}
    for name in (R2, S3, R3):
        passes = [est[name][h].iterations for est in mine.estimates.values() for h in sp.HORIZONS]
        result["robust_fits"][name] = {"fits": len(passes), "capped": sum(1 for x in passes if x >= sc.MAX_ITERATIONS),
                                       "cap": sc.MAX_ITERATIONS, "mean_passes": sum(passes) / len(passes)}
    result["v4_fits"] = [
        {"fitted_on": day.isoformat(), "band": list(f.band), "miss_factor": {str(h): f.miss_factor[h] for h in sp.HORIZONS},
         "after_miss": {str(h): f.after_miss[h] for h in sp.HORIZONS}, "pairs": {str(h): f.pairs[h] for h in sp.HORIZONS},
         "type_factor": {str(h): dict(f.type_factor[h]) for h in sp.HORIZONS}}
        for day, f in sorted(layered.fits.items())
    ]
    result["recovery"] = recovery(result["groups"]["pooled"]["all decision days"])
    states_scored = [mine.detail[d]["state"] for d in days]
    result["state_mix"] = {str(level): sum(1 for s in states_scored if s is not None and abs(s - level / 3.0) < 1e-9) for level in range(4)}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def recovery(pooled: dict) -> dict:
    """The declared kill rule: the share of (s3)'s gain over (a) that each of (r1) and (r2) recovers, pooled, on the mean score over
    leads 1 to 5 (grid CRPS and twCRPS). `recovered = (mean(a) - mean(arm)) / (mean(a) - mean(s3))`; undefined when (s3) has no gain.
    The kill is met when (r1) and (r2) each recover less than `KILL_SHARE` on the grid CRPS."""

    out: dict = {"share": KILL_SHARE, "metrics": {}}
    for metric in METRIC_NAMES:
        means = pooled[metric]["means"]
        gain = means[A] - means[S3]
        entry = {"gain_of_s3": gain}
        for name in (R1, R2, R3, V4):
            entry[name] = None if not gain > 0.0 else (means[A] - means[name]) / gain
        out["metrics"][metric] = entry
    grid = out["metrics"]["grid_crps"]
    out["met"] = bool(grid["gain_of_s3"] > 0.0 and grid[R1] < KILL_SHARE and grid[R2] < KILL_SHARE)
    return out


# -- the page --------------------------------------------------------------------------------------------------------

LABELS = {"B1": "B1", B1P: "B1' (#960)", "B2": "B2", GBM: "gbm_funding (#634)", A: "(a) base: #941 mad 20, floor 0.5",
          V4: "(v4) miss feedback and calendar-type scale factor (#1153) on (s3)"}
LABELS.update({a.name: a.role for a in sc.DECOMPOSITION})
METRIC_TITLES = {"grid_crps": "grid CRPS (23 levels)", "upper_tail_twcrps": "upper-tail twCRPS (weight 1{z > 0 bp})",
                 SCALED: "scaled grid CRPS (#967)"}


def verdict(row: Optional[dict]) -> str:
    """The declared reading of one row: gain, loss or undecided, on the studentized bound on mean d (Eleonora's #1009 ruling): a gain
    when the lower end of the 90% interval of mean d is above zero, a loss when its upper end is below zero. The skill interval is
    reported beside it and does not decide."""

    if row is None or "undefined" in row:
        return "undecided"
    lo, hi = row["difference_interval"]
    return "gain" if lo > 0.0 else "loss" if hi < 0.0 else "undecided"


def skill_verdict(row: Optional[dict]) -> str:
    """The reading the skill interval alone would give (reported beside the mean-d reading, never instead of it)."""

    if row is None or "undefined" in row:
        return "undecided"
    lo, hi = row["skill_interval"]
    return "gain" if lo > 0.0 else "loss" if hi < 0.0 else "undecided"


def _fmt(row: Optional[dict]) -> str:
    """`skill [90%]` and, beside it, the mean-d bound: `d` in bp with its 90% interval."""

    if row is None:
        return "–"
    if "undefined" in row:
        return "undefined"
    lo, hi = row["difference_interval"]
    return f"{s761.skill_text(row)}; d {row['difference']:+.3f} [{lo:+.3f}, {hi:+.3f}]"


def model_table(r: dict, cell: dict) -> List[str]:
    """Mean score of every model in one group, and each arm's skill over B1, B1', B2, (a), (s3), the arm it differs from by one thing,
    and gbm_funding, each with the mean-d bound beside it."""

    gbm = [g for g in GBMS if g in r["gbm"]]
    out = ["| | mean | skill vs B1 [90%]; mean d (bp) [90%] | vs B1' | vs B2 | vs (a) | vs (s3) | vs the arm it isolates" + "".join(f" | vs {g}" for g in gbm) + " |",
           "|---|---|---|---|---|---|---|---|" + "---|" * len(gbm)]
    means = cell["means"]
    for name in list(BENCHMARKS) + gbm:
        if name in means:
            out.append(f"| {LABELS[name]} | {means[name]:.3f} |" + " |" * (6 + len(gbm)))
    for name in ARMS:
        vs = cell["vs"].get(name, {})
        iso = ISOLATES.get(name)
        cells = ([_fmt(vs.get(b)) for b in ("B1", B1P, "B2")] + ["" if name == A else _fmt(vs.get(A))]
                 + ["" if name in (A, S3) else _fmt(vs.get(S3))]
                 + [("" if iso is None or iso[0] == S3 else f"{_fmt(vs.get(iso[0]))} (vs (s1))")] + [_fmt(vs.get(g)) for g in gbm])
        out.append(f"| {LABELS[name]} | {means[name]:.3f} | " + " | ".join(cells) + " |")
    return out


def tally(r: dict, arm: str, reference: str, metric: str = "grid_crps") -> Dict[str, int]:
    """The number of regimes (by target day) in which the arm's mean-d bound against `reference` reads as a gain, a loss and undecided."""

    count = {"gain": 0, "loss": 0, "undecided": 0}
    for label in REGIMES:
        entry = r["groups"].get("regime", {}).get(label)
        if entry is not None:
            count[verdict(entry[metric]["vs"].get(arm, {}).get(reference))] += 1
    return count


def _share(value: Optional[float]) -> str:
    return "n/a" if value is None else f"{100 * value:.0f}%"


def render(r: dict) -> str:
    n = r["notes"]
    pooled = r["groups"]["pooled"]["all decision days"]
    out = [
        "# Why (s3) wins: the ridge and the Huber fit apart, the settlement's size, and #1153's v4 on (s3) (#1172)", "",
        "**Hypothesis and step:** H5 (primary goal), step 3 (calendar first; refocus). **Development data, not a verdict** (scoring "
        f"protocol v1, #640): days to {n['last_target']}, no lockbox day. Nothing is adopted and no claim changes. Generated by "
        f"`scripts/s3_decomposition_1172.py page` from `docs/research/s3-decomposition-1172/result.json`, not edited by hand; declared in "
        f"`{r['declaration']}` before any number.", "",
        f"Panel digest `{r['panel_sha256'][:8]}…`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, "
        f"{r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound). Skill is "
        "`mean(d) / mean(S(benchmark))` with `d = S(benchmark) - S(candidate)`, positive favours the candidate. **Every row shows the skill "
        "interval and, beside it, the studentized interval on mean d (bp); a reading (gain, loss, undecided) is taken from the mean-d bound** "
        "(her ruling on #1009, 20 October 2026), not from the skill interval. **Caveat (Lens C, #958):** the lag-10 HAC standard error that "
        "studentizes the bound is understated about 2x after 2020, so an interval that excludes zero is narrower than it should be; a "
        f"reading here is evidence for a question. Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); the "
        f"fit is renewed {n['refits']} times. B1' (Lens C's calendar-aware persistence, #960) is reported beside B1 in every table; B1 and "
        "B2 stay the protocol's benchmarks.", "",
        "**What is taken apart.** (s3) of #1145 is #941's scaled mean reversion (a) with calendar terms in standardised units (s1), fitted "
        "by a Huber fit with a ridge of 5 pseudo-days. It beat (a) by +4.3% pooled [+1.8%, +6.4%]; #1172 asks why. **(r1)** is (s1) with "
        "the ridge of 5 alone (least squares, no Huber); **(r2)** is (s1) with the Huber fit alone (ridge 1); **(r3)** is (s3) with the "
        "announced gross size of the coupon and bill settlements, in USD 100 bn, times the scarcity state, in place of the 0/1 flags "
        "(Lens A, #958); **(v4)** is #1153's miss feedback and calendar-type scale factor on (s3), declared as a fourth arm because #1153 "
        "said it re-runs on a new base. All read the calendar at the target day on direct pairs. A settlement size is read at lead 1 only "
        "(the announcement dating that would admit it at leads 2 to 5 is not in force), so (r3) and (s3) are the same model at leads 2 to 5.", ""]
    if r["gbm"]:
        out += ["The `gbm_funding` comparison uses the walks supplied, on the decision days both cover.", ""]
    else:
        out += ["**The `gbm_funding` walks were not supplied**, so no row compares an arm with it; the comparison is a long run that stays on "
                "Eleonora's Mac (`needs-mac`, the same `score` command with `--walks`) and was not run first. #1115's figure for (a) "
                "against it is +6.8% pooled [+3.3%, +10.1%].", ""]
    rec = r["recovery"]
    grid, tw = rec["metrics"]["grid_crps"], rec["metrics"]["upper_tail_twcrps"]
    out += ["## The kill rule: do (r1) and (r2) each recover half of (s3)'s gain?", "",
            "The share of (s3)'s gain over (a) that an arm recovers is `(mean(a) - mean(arm)) / (mean(a) - mean(s3))` on the pooled mean score "
            f"over leads 1 to 5 (point estimates; the intervals of each gain are in the next table). (s3)'s gain is {grid['gain_of_s3']:+.3f} bp of "
            f"grid CRPS and {tw['gain_of_s3']:+.3f} bp of upper-tail twCRPS.", "",
            "| arm | share of (s3)'s gain recovered, grid CRPS | twCRPS |", "|---|---|---|"]
    for name in (R1, R2, R3, V4):
        out.append(f"| {LABELS[name]} | {_share(grid[name])} | {_share(tw[name])} |")
    if rec["met"]:
        out += ["", f"**The kill rule is met: (r1) and (r2) each recover less than {int(100 * rec['share'])}% of (s3)'s grid-CRPS gain over (a). "
                "The gain needs both the ridge and the Huber fit.** The decomposition stops there; (r3) and (v4) are separate questions and "
                "are reported below as declared, since they were scored in the same run.", ""]
    else:
        out += ["", f"**The kill rule is not met on the grid CRPS**: at least one of (r1) and (r2) recovers {int(100 * rec['share'])}% or more of "
                "(s3)'s gain over (a).", ""]
    out += ["## Does an arm beat (a) and does it beat (s3)?", "",
            "Skill of each arm over (a) and over (s3), pooled; each cell is the skill with its 90% interval and, after the semicolon, mean d (bp) "
            "with its 90% interval. The regimes (by target day) read as gain / loss / undecided on the mean-d bound; the last columns are the "
            "reading on ordinary days and on the calendar days against (s3). Replacing (s3) is Eleonora's decision.", "",
            "| arm | grid CRPS vs (a) | grid CRPS vs (s3) | twCRPS vs (a) | twCRPS vs (s3) | regimes vs (s3), grid CRPS (gain / loss / undecided) "
            "| ordinary days vs (s3) | calendar days vs (s3) |", "|---|---|---|---|---|---|---|---|"]
    for name in ARMS:
        if name == A:
            continue
        t = tally(r, name, S3) if name != S3 else None
        ordv = r["groups"].get("target_day_type", {}).get(ORDINARY, {}).get("grid_crps", {}).get("vs", {}).get(name, {}).get(S3)
        calv = r["groups"].get("target_day_type", {}).get("calendar_days", {}).get("grid_crps", {}).get("vs", {}).get(name, {}).get(S3)
        out.append(
            f"| {LABELS[name]} | {_fmt(pooled['grid_crps']['vs'][name].get(A))} | "
            + (_fmt(pooled['grid_crps']['vs'][name].get(S3)) if name != S3 else "") + f" | {_fmt(pooled['upper_tail_twcrps']['vs'][name].get(A))} | "
            + (_fmt(pooled['upper_tail_twcrps']['vs'][name].get(S3)) if name != S3 else "")
            + (f" | {t['gain']} / {t['loss']} / {t['undecided']} | {_fmt(ordv)} | {_fmt(calv)} |" if t else " | | | |"))
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
    out += ["## Reading under the declared rules (the mean-d bound, with the skill interval's reading beside it)", ""]
    for metric, metric_name in (("grid_crps", "grid CRPS"), ("upper_tail_twcrps", "upper-tail twCRPS")):
        if metric != "grid_crps":
            out += ["The same readings on the key secondary score, upper-tail twCRPS (#1194; the lines above read grid CRPS only):", ""]
        for name in ARMS:
            if name == A:
                continue
            for reference in ([A] if name == S3 else [A, S3]):
                parts = []
                for split in ("pooled", "regime", "target_day_type"):
                    for label, entry in r["groups"].get(split, {}).items():
                        row = entry[metric]["vs"].get(name, {}).get(reference)
                        word = verdict(row)
                        other = skill_verdict(row)
                        parts.append(f"{label}: {word}" + ("" if word == other else f" (skill interval: {other})"))
                out.append(f"- **{LABELS[name]}** against {LABELS[reference] if reference == A else '(s3)'}, {metric_name}: " + "; ".join(parts) + ".")
        out.append("")
    for name in (R1, R2, S3, R3, V4):
        other, what = ISOLATES[name]
        row = pooled["grid_crps"]["vs"][name].get(other)
        tw = pooled["upper_tail_twcrps"]["vs"][name].get(other)
        out.append(f"- {LABELS[name]} against {'(s3)' if other == S3 else '(s1)'} isolates {what}: grid CRPS {_fmt(row)}; twCRPS {_fmt(tw)}.")
    out.append("")
    out += ["## The Politis-White block beside the block of 10", "",
            "The automatic block length (Politis and White 2004, with the correction of Patton, Politis and White 2009) of the paired loss "
            "differential `S(reference) - S(arm)`, in days, with the pooled skill over the reference at that block. Reported, never "
            "substituted for 10.", ""]
    columns = ["pooled"] + [l for l in REGIMES if l in r["politis_white"].get("regime", {})]
    for metric in METRIC_NAMES:
        for reference in (A, S3):
            out += [f"{METRIC_TITLES[metric]}, against {'(a)' if reference == A else '(s3)'}:", "",
                    "| | " + " | ".join(columns) + " | pooled skill at that block |", "|---|" + "---|" * (len(columns) + 1)]
            for name in ARMS:
                if name == A or (reference == S3 and name in (S1, S3)):
                    continue
                cells, at = [], ""
                for col in columns:
                    split, label = ("pooled", "all decision days") if col == "pooled" else ("regime", col)
                    e = (r["politis_white"].get(split, {}).get(label, {}).get(metric, {}).get(name) or {}).get(reference)
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
            "`scale(anchor) * beta * x` at the refit the forecast used (0 where the term was absent from that refit), with `x` the term's 0/1 "
            "flag, or for the settlement terms of (r3) `size / 100 * state`; then the mean over the flagged days, in bp, with the 90% "
            "stationary-bootstrap percentile interval over those days in date order (mean block 10 flagged days; none under 5 days). The "
            "interval measures the spread of the estimates across refits and days, not a standard error of the effect. The number of "
            "flagged days is in brackets. (v4) has no term of its own: its terms are (s3)'s.", ""]

    def cell_text(e: Optional[dict], quantity: str, places: int = 2) -> str:
        if e is None:
            return "–"
        q = e[quantity]
        text = f"{q['mean']:+.{places}f}"
        if q["interval"] is not None:
            text += f" [{q['interval'][0]:+.{places}f}, {q['interval'][1]:+.{places}f}]"
        return text + f" ({e['days']})"

    for arm in sc.DECOMPOSITION:
        for quantity, title, places in (("bp", "effect (bp)", 2), ("std", "effect (scale units)", 3)):
            out += [f"**{LABELS[arm.name]}: {title}**", "", "| term | " + " | ".join(REGIMES) + " |", "|---|" + "---|" * len(REGIMES)]
            for term in arm.location:
                out.append(f"| {term} | " + " | ".join(
                    cell_text(r["term_effect_intervals"].get(arm.name, {}).get(term, {}).get(l), quantity, places) for l in REGIMES) + " |")
            out.append("")
    out += [f"**Missed by (a)**: the mean outcome less (a)'s median on the same flagged days, in bp", "", "| term | " + " | ".join(REGIMES) + " |",
            "|---|" + "---|" * len(REGIMES)]
    for term in sc.ARMS[0].location:
        out.append(f"| {term} | " + " | ".join(
            cell_text(r["term_effect_intervals"].get(S3, {}).get(term, {}).get(l), "miss") for l in REGIMES) + " |")
    out.append("")
    out += [f"Refits in which each term entered the fit (of {r['refit_total']} refits), by lead 1 to 5:", ""]
    for arm in sc.DECOMPOSITION:
        out += [f"{LABELS[arm.name]}:", "", "| term | " + " | ".join(f"h={h}" for h in sp.HORIZONS) + " |", "|---|" + "---|" * len(sp.HORIZONS)]
        for term, counts in r["refit_term_counts"][arm.name].items():
            if term in arm.location:
                out.append(f"| {term} | " + " | ".join(str(x) for x in counts) + " |")
        out.append("")
    mix = r["state_mix"]
    out += [f"The scarcity state of the scored decisions: abundant {mix['0']}, ample {mix['1']}, tight {mix['2']}, scarce {mix['3']}; "
            f"unknown {r['notes']['decisions_with_unknown_state']}.", ""]
    for name, info in r["robust_fits"].items():
        out.append(f"The Huber fit of {LABELS[name]} took {info['mean_passes']:.1f} iterations on average and reached its cap "
                   f"(`MAX_ITERATIONS` = {info['cap']}) without the coefficients settling to 1e-8 in {info['capped']} of {info['fits']} fits (refit by lead).")
    out.append("")
    fits = r["v4_fits"]
    if fits:
        mean_miss = {h: sum(f["miss_factor"][str(h)] for f in fits) / len(fits) for h in sp.HORIZONS}
        after = {h: sum(f["after_miss"][str(h)] / f["pairs"][str(h)] for f in fits) / len(fits) for h in sp.HORIZONS}
        out += ["## (v4) on (s3): what the factors were", "",
                f"Over the {len(fits)} refits: the mean miss factor by lead and the mean share of training pairs that followed a miss of the "
                "90% band the model gave their origin row (the pool of the arm is the pairs that did not).", "",
                "| | " + " | ".join(f"h={h}" for h in sp.HORIZONS) + " |", "|---|" + "---|" * len(sp.HORIZONS),
                "| mean miss factor | " + " | ".join(f"{mean_miss[h]:.3f}" for h in sp.HORIZONS) + " |",
                "| share of pairs after a miss | " + " | ".join(f"{100 * after[h]:.1f}%" for h in sp.HORIZONS) + " |", ""]
        kinds = sorted({k for f in fits for h in sp.HORIZONS for k in f["type_factor"][str(h)]})
        if kinds:
            out += ["Mean calendar-type factor on the scale by lead, over the refits in which the type entered (the number of such refits "
                    "in brackets):", "", "| type | " + " | ".join(f"h={h}" for h in sp.HORIZONS) + " |", "|---|" + "---|" * len(sp.HORIZONS)]
            for k in kinds:
                cells = []
                for h in sp.HORIZONS:
                    v = [f["type_factor"][str(h)][k] for f in fits if k in f["type_factor"][str(h)]]
                    cells.append("n/a" if not v else f"{sum(v) / len(v):.3f} ({len(v)})")
                out.append(f"| {k} | " + " | ".join(cells) + " |")
            out.append("")
    out += ["## What this is not", "",
            "Development data from 2018 to 2025, split by regime and target-day type, never a verdict. The arms read the calendar at the target "
            "day on direct pairs, so their class is not provisional (`docs/research/provisional-calendar-register.md`), but the choices "
            "(the size unit of USD 100 bn, the size times the state in place of the flag, (v4)'s composition with (s3)'s location terms, the "
            "ridges and Huber's threshold of (s3)) are this study's own, were not tuned, and are open to Eleonora's review. #941's variant was "
            "itself chosen after seeing 2018-2025. The settlement size is read as the published panel's column at lead 1 only; the announcement "
            "dating that would give it at leads 2 to 5 is not in force. Whether an arm replaces (s3) as the H5 candidate is her decision.", ""]
    out += question(r)
    return "\n".join(out) + "\n"


def question(r: dict) -> List[str]:
    """The closing question for Eleonora (her ruling of 23 October 2026 on #1172: an arm replaces (s3) only if it beats (s3))."""

    groups = r["groups"]
    cols = [("pooled", "all decision days", "pooled")] + [("regime", l, l) for l in REGIMES if l in groups.get("regime", {})] + [
        ("target_day_type", l, l) for l in [ORDINARY, "calendar_days"] if l in groups.get("target_day_type", {})]
    models = [GBM] * (GBM in r["gbm"]) + list(ARMS)
    out = ["## Question for Eleonora: does an arm replace (s3) as the H5 candidate?", "",
           "Your ruling of 23 October 2026 on #1172: (s3) of #1145 is the H5 candidate (nothing registered); an arm replaces (s3) only if it "
           "beats it, and that is your decision on this page's evidence. **Nothing is adopted here and no claim changes.** The tables give "
           "the mean score of (a), (s3) and the arms, pooled, by regime and by ordinary and calendar days (lower is better; B1, B1' and B2 "
           "are in the tables above)."
           + ("" if r["gbm"] else " **The `gbm_funding` rows are empty: its walks are a long run for your Mac and were not run first.**"), ""]
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
            "1. **Keep (s3) as the H5 candidate** (default). Nothing changes; the decomposition, the settlement size and (v4) stay development results.",
            "2. **Replace (s3) with one of the arms (which: your choice)**, on the evidence above. That is a decision for you and would be "
            "followed by a registration discussion; this page does not pre-empt it.",
            "3. **Ask for a further step** before deciding (for example the `gbm_funding` comparison on your Mac, or the arms on the 2026 "
            "development days).", ""]
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
