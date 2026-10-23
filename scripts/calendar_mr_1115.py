"""Calendar and FOMC effects as additive terms on scaled mean reversion, scored (#1115; H5 step 3, calendar first).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every
choice is in `metadata/calendar_mr_1115.json`, which this script refuses to read unless it is committed and unchanged. The arms are
`repo_model.spread_mr_calendar` (a: #941's variant; b: plus location terms; c: plus scale terms; d: c without FOMC and IORB), scored
with the scorer of scoring protocol v1 (`repo_model.scoring_protocol`) against each other, B1, B1' (#960), B2, `spread_mr_ctx` (#761)
and, when their walks are supplied, `gbm_funding` and `gbm_funding_cal_aligned`, with the studentized stationary bootstrap of ruling 1.
Scored decision days are those whose five targets are on or before 2025-12-31; no later day is read and no locked day is scored
(`docs/decisions/lockbox.md`). Nothing here is a verdict (scoring protocol v1, #640).

The mean-reversion walks are fast (minutes). The comparison with the gradient-boosted models needs their walks, which are long
runs and come from Eleonora's Mac (`.claude/skills/long-run`); `score` scores what exists and says what it left out. Commands, from
a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    # optional: WALKS/gbm_funding_h<h>.json (scripts/spread_distribution_634.py walk) and
    #           WALKS/gbm_funding_cal_aligned_h<h>.json (scripts/aligned_calendar_1027.py walk), all five leads of each
    PYTHONPATH=src python3 scripts/calendar_mr_1115.py score --panel PUB.csv [--walks WALKS] \\
        --output docs/research/calendar-mr-1115/result.json
    PYTHONPATH=src python3 scripts/calendar_mr_1115.py page \\
        --score docs/research/calendar-mr-1115/result.json --output docs/research/calendar-mr-1115-result.md

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


from repo_model import announced_iorb, b1_calendar as b1c, lockbox, metrics  # noqa: E402
from repo_model import protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model import spread_mean_reversion as smr, spread_mr_calendar as cal, spread_mr_variants as var  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.splits import SplitError  # noqa: E402

s686 = _load("spread_mean_reversion_686")
s761 = _load("spread_mr_variants_761")
b949 = _load("block_length_949")

DECLARATION = REPO / "metadata" / "calendar_mr_1115.json"
IORB_TABLE = REPO / "tests" / "fixtures" / "snapshots" / "fed-iorb-announcements" / "iorb_changes.csv"
SPLITS = s686.SPLITS
SOURCES = s686.SOURCES
SEED = 1115
LAST_DAY = s686.LAST_DAY
DECISION_TIME = s686.DECISION_TIME
MIN_GROUP_DAYS = s686.MIN_GROUP_DAYS
GBM = "gbm_funding"
GBM_CAL = "gbm_funding_cal_aligned"
GBMS = (GBM, GBM_CAL)
B1P = "B1_prime"
CTX = "spread_mr_ctx"
A = cal.ARM_A
ARMS = cal.ARM_NAMES
BENCHMARKS = ("B1", B1P, "B2", CTX)
MODELS = BENCHMARKS + ARMS
METRICS = (("grid_crps", sp.grid_crps), ("upper_tail_twcrps", sp.upper_tail_twcrps))
METRIC_NAMES = tuple(m for m, _ in METRICS)
REGIMES = ["2018-19", "2020", "2021-23", "2024", "2025-26"]
#: The target-day types of the issue, in its order; the groups overlap and `ordinary` is none of them.
DAY_TYPES = ("month_end", "quarter_end", "tax_date", "settlement", "fomc_day", "iorb_window", "dom_19_23", "post_month_end_window")
ORDINARY = "ordinary"
Q95 = sp.GRID.index(0.95)
MEDIAN = sp.GRID.index(0.5)
CELL_BLOCK = 5.0 * sp.BLOCK_LENGTH
FLAG_BLOCK = 10.0


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


# -- the frame -------------------------------------------------------------------------------------------------------


def day_labels(frame, table: cal.TermTable) -> Dict[date, List[str]]:
    """Each target day's types (a day can carry several), `ordinary` when it carries none."""

    out: Dict[date, List[str]] = {}
    for day in sorted({frame.target(d, h) for d in frame.days for h in sp.HORIZONS}):
        row = frame.position[day]
        flags = table.day_types(row)
        flags["settlement"] = int(bool(flags["settlement_coupon"] or flags["settlement_bill"]))
        kinds = [k for k in DAY_TYPES if flags[k]]
        out[day] = kinds or [ORDINARY]
    return out


def build_frame(panel, splits, registry, table, first: Optional[date] = None):
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
    mine = cal.walk(panel, candidate_days, table, **settings)
    ctx = var.walk(panel, candidate_days, b2=b2, **settings)
    days = [d for d in candidate_days if d in b1 and all(d in mine.forecasts[a] for a in ARMS) and d in ctx.forecasts[CTX]]
    frame.days = days
    frame.forecasts = {"B1": b1, B1P: b1p, "B2": b2, CTX: ctx.forecasts[CTX], **{a: mine.forecasts[a] for a in ARMS}}
    for name in list(frame.forecasts):
        frame.forecasts[name] = {d: frame.forecasts[name][d] for d in days}
    notes = {
        "decision_days_offered": len(candidate_days), "candidate_skipped_for_history": len(mine.skipped),
        "benchmark_missing": [d.isoformat() for d in dropped], "scored_decision_days": len(days),
        "first": days[0].isoformat(), "last": days[-1].isoformat(),
        "last_target": frame.target(days[-1], max(sp.HORIZONS)).isoformat(), "refits": len(mine.fits),
    }
    return frame, notes, mine


def load_gbm(walks: Optional[Path], published_sha: str, frame, name: str) -> Optional[Dict[date, Dict[int, List[float]]]]:
    """A gradient-boosted model's forecast on each decision day its five walks cover, a missing lead standing in as B1 (#634).

    Returns `None` when the walks are not supplied. A partly present set of leads is an error, never a silent drop.

    Raises:
        ValueError: some but not all leads are present, or a walk was made from another published panel.
        LookAheadError: a scored day is in a locked tier.
    """

    if walks is None:
        return None
    present = [h for h in sp.HORIZONS if (walks / f"{name}_h{h}.json").is_file()]
    if not present:
        return None
    if len(present) != len(sp.HORIZONS):
        raise ValueError(f"{name} has walks for leads {present} only; walk every lead or none")
    sd = _load("spread_distribution_634")
    for h in sp.HORIZONS:
        document = json.loads((walks / f"{name}_h{h}.json").read_text(encoding="utf-8"))
        if document.get("panel_sha256") != published_sha:
            raise ValueError(f"{name}_h{h}.json was walked from panel {document.get('panel_sha256')}, not {published_sha}")
    decisions, walked = sd.lead_forecasts(sd.load_laws(walks, name), frame.dates)
    usable = [d for d in walked if frame.target(d, max(sp.HORIZONS)) <= LAST_DAY and d in frame.forecasts["B1"]]
    sd.refuse_locked(usable + [frame.target(d, h) for d in usable for h in sp.HORIZONS])
    return sp.fill_missing({d: decisions[d] for d in usable}, {d: frame.forecasts["B1"][d] for d in usable}, usable).forecasts


# -- the cells -------------------------------------------------------------------------------------------------------


def cell_table(frame, forecasts: Mapping[date, Mapping[int, Sequence[float]]]) -> Dict[str, Dict[Tuple[date, int], float]]:
    """Both scores, and the two q95 hits, of every (decision day, lead) cell of `forecasts`, after the scored days are checked."""

    days = sorted(forecasts)
    cells = {(d, h): frame.target(d, h) for d in days for h in sp.HORIZONS}
    s686.require_scored_days(set(d for d, _ in cells) | set(cells.values()), LAST_DAY)
    out: Dict[str, Dict[Tuple[date, int], float]] = {m: {} for m in METRIC_NAMES + ("hit_above", "hit_at_or_above")}
    for (d, h), t in cells.items():
        q, y = forecasts[d][h], frame.outcome[t]
        out["grid_crps"][(d, h)] = sp.grid_crps(q, y)
        out["upper_tail_twcrps"][(d, h)] = sp.upper_tail_twcrps(q, y)
        out["hit_above"][(d, h)] = 1.0 if y > q[Q95] else 0.0
        out["hit_at_or_above"][(d, h)] = 1.0 if y >= q[Q95] else 0.0
    return out


def groups_of(frame, labels: Mapping[date, Sequence[str]]) -> List[Tuple[str, str, str, List[date]]]:
    """`(split, label, grain, members)`: pooled, by lead, by regime and by target-day type (overlapping)."""

    out: List[Tuple[str, str, str, List[date]]] = [("pooled", "all decision days", "decision", list(frame.days))]
    for h in sp.HORIZONS:
        out.append(("lead", f"h={h}", f"lead{h}", list(frame.days)))
    targets = sorted(labels)
    by_regime: Dict[str, List[date]] = {}
    by_type: Dict[str, List[date]] = {}
    for t in targets:
        by_regime.setdefault(frame.regime(t), []).append(t)
        for kind in labels[t]:
            by_type.setdefault(kind, []).append(t)
    for label in REGIMES:
        if label in by_regime:
            out.append(("regime", label, "target", by_regime[label]))
    for label in DAY_TYPES + (ORDINARY,):
        if label in by_type:
            out.append(("target_day_type", label, "target", by_type[label]))
    calendar = sorted({t for k in DAY_TYPES if k in by_type for t in by_type[k]})
    out.append(("target_day_type", "calendar_days", "target", calendar))
    return out


def series_of(frame, cells: Mapping[Tuple[date, int], float], grain: str) -> Dict[date, float]:
    if grain == "decision":
        return s686.by_decision(cells)
    if grain == "target":
        return s686.by_target(frame, cells)
    return s686.by_lead(cells, int(grain[4:]))


# -- the tests, in parallel ------------------------------------------------------------------------------------------

_STATE: Dict = {}


def pair_plan(candidate: str, have: Sequence[str]) -> List[str]:
    """The benchmarks a candidate is tested against: the four references, the arms it is compared with, and the gbm models."""

    names = list(BENCHMARKS)
    if candidate != A:
        names.append(A)
    if candidate == "mr_cal_c_location_scale":
        names += ["mr_cal_b_location", "mr_cal_d_no_fomc_iorb"]
    names += [g for g in GBMS if g in have]
    return names


def _pairs_task(job):
    split, label, grain, metric, candidate, members = job
    series = _STATE["series"][(grain, metric)]
    out: Dict[str, dict] = {}
    for name in pair_plan(candidate, _STATE["gbm_have"]):
        days = [d for d in members if d in series[name]] if name in GBMS else list(members)
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


def term_effects(frame, table: cal.TermTable, mine: cal.Walk) -> dict:
    """Per arm (b, c), term and regime: the effect in force on the flagged scored cells, per flagged target day.

    For each flagged target day T (the term's flag at the lead's reading), the mean over the leads that forecast T of the
    effect estimated at the refit the forecast used (0 where the term was absent from it), of the scale uplift, and of the
    outcome less arm (a)'s median. Returned as lists in date order for the intervals.
    """

    out: dict = {}
    for arm in (a for a in cal.ARMS if a.name != "mr_cal_d_no_fomc_iorb"):
        per_term: Dict[str, Dict[date, Dict[str, List[float]]]] = {t: {} for t in cal.ALL_TERMS}
        for d in frame.days:
            used = mine.fit_used[d]
            for h in sp.HORIZONS:
                t = frame.target(d, h)
                row = frame.position[t]
                estimate = mine.estimates[used][arm.name][h]
                median = frame.forecasts[A][d][h][MEDIAN]
                for term in cal.ALL_TERMS:
                    if table.flag(term, h, row):
                        cell = per_term[term].setdefault(t, {"effect": [], "uplift": [], "miss": [], "present": []})
                        cell["effect"].append(estimate.effect.get(term, 0.0))
                        cell["uplift"].append(estimate.uplift.get(term, 0.0))
                        cell["miss"].append(frame.outcome[t] - median)
                        cell["present"].append(1.0 if term in estimate.effect else 0.0)
        out[arm.name] = {
            term: {
                t.isoformat(): {k: sum(v) / len(v) for k, v in cell.items()} for t, cell in sorted(days.items())
            } for term, days in per_term.items()
        }
    return out


# -- the report ------------------------------------------------------------------------------------------------------


def score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    panel = load_daily_panel(panel_path)
    splits = load_split_declaration(SPLITS)
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    table = cal.TermTable(panel, announced_iorb.load_announcements(IORB_TABLE), decision_time=DECISION_TIME)
    frame, notes, mine = build_frame(panel, splits, registry, table, args.first)
    published_sha = panel_sha256(panel_path)
    walks = Path(args.walks) if args.walks else None
    gbm_forecasts = {name: load_gbm(walks, published_sha, frame, name) for name in GBMS}
    gbm_forecasts = {k: v for k, v in gbm_forecasts.items() if v}
    days = frame.days
    labels = day_labels(frame, table)

    cells = {m: cell_table(frame, frame.forecasts[m]) for m in MODELS}
    gbm_frames = {}
    for name, forecasts in gbm_forecasts.items():
        gbm_frames[name] = cell_table(frame, {d: forecasts[d] for d in days if d in forecasts})
    for m in MODELS:
        official = sp.day_scores(frame.forecasts[m], frame.outcome, frame.dates, score=sp.grid_crps)
        mean = s686.by_decision(cells[m]["grid_crps"])
        if set(official) != set(mean) or any(abs(official[d] - mean[d]) > 1e-9 for d in mean):
            raise SystemExit(f"grid CRPS of {m}: the cell means differ from scoring_protocol.day_scores")

    groups = groups_of(frame, labels)
    series: Dict[Tuple[str, str], Dict[str, Dict[date, float]]] = {}
    for _s, _l, grain, _m in groups:
        for metric in METRIC_NAMES:
            if (grain, metric) not in series:
                entry = {m: series_of(frame, cells[m][metric], grain) for m in MODELS}
                for name, table_ in gbm_frames.items():
                    entry[name] = series_of(frame, table_[metric], grain)
                series[(grain, metric)] = entry
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
    # the q95 exceedance rate, pooled and by regime, with an interval over the cells in date order
    models_q = list(MODELS) + list(gbm_frames)
    rate_models = {m: (cells[m] if m in cells else gbm_frames[m]) for m in models_q}
    cell_groups: Dict[Tuple[str, str], Dict[str, List[Tuple[date, int]]]] = {}
    for m, table_ in rate_models.items():
        keys = sorted(table_["hit_above"])
        cell_groups[(m, "pooled/all cells")] = keys
        for regime in REGIMES:
            kept = [k for k in keys if frame.regime(frame.target(*k)) == regime]
            if len(kept) >= MIN_GROUP_DAYS:
                cell_groups[(m, f"regime/{regime}")] = kept
    for (m, name), keys in cell_groups.items():
        for rule in ("hit_above", "hit_at_or_above"):
            jobs.append(("interval", (rule, (m, name), [rate_models[m][rule][k] for k in keys], CELL_BLOCK)))
    done = run_jobs(jobs, args.workers)

    by_key = {(s_, l_): (g, m) for s_, l_, g, m in groups}
    result: dict = {
        "issue": 1115, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha,
        "subset_from": None if args.first is None else args.first.isoformat(), "label": "development, not a verdict",
        "seed": SEED, "draws": args.draws, "reps": args.reps, "notes": notes, "models": list(MODELS), "gbm": sorted(gbm_frames),
        "arms": [{"name": a.name, "role": a.role, "location": list(a.location), "scale": list(a.scale)} for a in cal.ARMS],
        "refits": [{"fitted_on": day.isoformat(), "phi": fit.phi} for day, fit in sorted(mine.fits.items())],
        "groups": {}, "skipped_groups": skipped, "politis_white": {}, "q95": {},
        "reading_rules": declaration["reading"]["rules"],
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
            for metric in METRIC_NAMES:
                ser = series[(grain, metric)]
                entry[metric]["means"] = {
                    m: sum(ser[m][d] for d in members if d in ser[m]) / max(1, sum(1 for d in members if d in ser[m]))
                    for m in list(MODELS) + list(gbm_frames)
                }
    for name, by_model in result["q95"].items():
        for m, rules in by_model.items():
            keys = cell_groups[(m, name)]
            for rule in rules:
                values = [rate_models[m][rule][k] for k in keys]
                rules[rule]["rate"] = sum(values) / len(values)
                rules[rule]["cells"] = len(values)
    # the rate by target-day type (no interval: the days of a type are scattered)
    result["q95_by_day_type"] = {}
    for label in DAY_TYPES + (ORDINARY,):
        result["q95_by_day_type"][label] = {}
        for m, table_ in rate_models.items():
            keys = [k for k in table_["hit_above"] if label in labels[frame.target(*k)]]
            if keys:
                result["q95_by_day_type"][label][m] = {
                    "cells": len(keys), "rate": sum(table_["hit_above"][k] for k in keys) / len(keys),
                    "rate_at_or_above": sum(table_["hit_at_or_above"][k] for k in keys) / len(keys)}
    result["term_effects"] = term_effects(frame, table, mine)
    result["term_effect_intervals"] = effect_intervals(result["term_effects"], frame, args.workers, args.reps)
    result["day_type_counts"] = {k: sum(1 for t in labels if k in labels[t]) for k in DAY_TYPES + (ORDINARY,)}
    result["refit_term_counts"] = {
        arm: {term: [sum(1 for est in mine.estimates.values() if term in est[arm][h].effect) for h in sp.HORIZONS] for term in cal.ALL_TERMS}
        for arm in ("mr_cal_b_location", "mr_cal_c_location_scale", "mr_cal_d_no_fomc_iorb")
    }
    result["refit_total"] = len(mine.estimates)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


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
                for quantity in ("effect", "uplift", "miss"):
                    values = [days[d][quantity] for d in sorted(members)]
                    cell[quantity] = {"mean": sum(values) / len(values), "interval": None}
                    if len(values) >= 5:
                        jobs.append(("interval", (quantity, (arm, term, regime), values, FLAG_BLOCK)))
    for _kind, ((quantity, (arm, term, regime)), interval) in run_jobs(jobs, workers):
        out[arm][term][regime][quantity]["interval"] = interval
    return out


# -- the page --------------------------------------------------------------------------------------------------------

LABELS = {"B1": "B1", B1P: "B1' (#960)", "B2": "B2", CTX: "spread_mr_ctx (#761)", GBM: "gbm_funding (#634)", GBM_CAL: "gbm_funding_cal_aligned (#1027)",
          A: "(a) base: #941 mad 20, floor 0.5"}
LABELS.update({a.name: a.role for a in cal.ARMS})
ORDER = list(BENCHMARKS) + list(ARMS)


def _fmt(row: Optional[dict]) -> str:
    return "–" if row is None else s761.skill_text(row)


def verdict(row: Optional[dict]) -> str:
    """The declared reading of one skill row: gain, loss or undecided."""

    if row is None or "undefined" in row:
        return "undecided"
    lo, hi = row["skill_interval"]
    return "gain" if lo > 0.0 else "loss" if hi < 0.0 else "undecided"


def model_table(r: dict, cell: dict) -> List[str]:
    """Mean score of every model in one group, and each arm's skill over B1, B1', B2, spread_mr_ctx, (a) and the gbm models."""

    gbm = [g for g in GBMS if g in r["gbm"]]
    header = ["| | mean | skill vs B1 [90%] | vs B1' | vs B2 | vs spread_mr_ctx | vs (a)" + "".join(f" | vs {g}" for g in gbm) + " |",
              "|---|---|---|---|---|---|---|" + "---|" * len(gbm)]
    out = list(header)
    means = cell["means"]
    for name in list(BENCHMARKS) + gbm:
        out.append(f"| {LABELS[name]} | {means[name]:.3f} |" + " |" * (5 + len(gbm)))
    for name in ARMS:
        vs = cell["vs"].get(name, {})
        cells = [_fmt(vs.get(b)) for b in ("B1", B1P, "B2", CTX)] + ["" if name == A else _fmt(vs.get(A))] + [_fmt(vs.get(g)) for g in gbm]
        out.append(f"| {LABELS[name]} | {means[name]:.3f} | " + " | ".join(cells) + " |")
    return out


def render(r: dict) -> str:
    n = r["notes"]
    metric_titles = {"grid_crps": "grid CRPS (23 levels)", "upper_tail_twcrps": "upper-tail twCRPS (weight 1{z > 0 bp})"}
    out = [
        "# Calendar and FOMC effects as additive terms on scaled mean reversion (#1115)", "",
        "**Hypothesis and step:** H5 (primary goal), step 3, calendar first. **Development data, not a verdict** (scoring protocol v1, #640): "
        f"days to {n['last_target']}, no lockbox day. Nothing is adopted and no claim changes. Generated by "
        f"`scripts/calendar_mr_1115.py page` from `docs/research/calendar-mr-1115/result.json`, not edited by hand; declared in "
        f"`{r['declaration']}` before any number.", "",
        f"Panel digest `{r['panel_sha256'][:8]}…`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, "
        f"{r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound); skill is "
        "`mean(d) / mean(S(benchmark))` with `d = S(benchmark) - S(candidate)`, positive favours the candidate. Scored decision days: "
        f"{n['scored_decision_days']:,} ({n['first']} to {n['last']}); the fit is renewed {n['refits']} times. B1' (Lens C's calendar-aware "
        "persistence, #960) is reported beside B1 in every table; B1 stays the protocol's benchmark.", "",
        "The arms: (a) is #941's variant, unchanged; (b) adds location terms; (c) adds location and scale terms; (d) is (c) without the FOMC "
        "and IORB terms. The terms are the flags of the target row (month-end, quarter-end, tax date, coupon and bill settlement at lead 1 "
        "only, the 19th to 23rd, the first three market days of a month, the day of an IORB change and the two days after it, an FOMC "
        "meeting day), read at the target day on direct pairs, each effect re-estimated at every refit.", ""]
    if r["gbm"]:
        out += ["The gradient-boosted comparisons use the walks supplied (" + ", ".join(r["gbm"]) + "), on the decision days both cover.", ""]
    else:
        out += ["**The gradient-boosted walks were not supplied**, so no row compares an arm with `gbm_funding` or `gbm_funding_cal_aligned`; "
                "they are long runs (`needs-mac`). The closing question is therefore not yet answerable on this page.", ""]
    for split, title in (("pooled", "Pooled"), ("lead", "By lead")):
        for label, entry in r["groups"].get(split, {}).items():
            for metric in METRIC_NAMES:
                out += [f"## {title}: {label}, {metric_titles[metric]}, mean over leads 1 to 5 (bp)" if split == "pooled"
                        else f"### {label}, {metric_titles[metric]}", ""] + model_table(r, entry[metric]) + [""]
    for split, title, order in (("regime", "regime (target day)", REGIMES),
                                ("target_day_type", "target-day type (the groups overlap)", list(DAY_TYPES) + [ORDINARY, "calendar_days"])):
        for metric in METRIC_NAMES:
            out += [f"## {metric_titles[metric]} by {title}", ""]
            for label in order:
                entry = r["groups"].get(split, {}).get(label)
                if entry is None:
                    continue
                out += [f"**{label}** ({entry['days']} days)", ""] + model_table(r, entry[metric]) + [""]
    if r["skipped_groups"]:
        out += ["Groups with fewer than %d days are listed and not tested: %s." % (
            MIN_GROUP_DAYS, ", ".join(f"{k} ({v})" for k, v in sorted(r["skipped_groups"].items()))), ""]
    out += ["## Reading under the declared rules", ""]
    for name in ("mr_cal_b_location", "mr_cal_c_location_scale", "mr_cal_d_no_fomc_iorb"):
        parts = []
        for split in ("pooled", "regime", "target_day_type"):
            for label, entry in r["groups"].get(split, {}).items():
                parts.append(f"{label}: {verdict(entry['grid_crps']['vs'].get(name, {}).get(A))}")
        out.append(f"- **{LABELS[name]}**, grid CRPS against (a): " + "; ".join(parts) + ".")
    out.append("")
    if r["gbm"]:
        for g in r["gbm"]:
            for name in ARMS:
                cal_row = r["groups"]["target_day_type"].get("calendar_days", {}).get("grid_crps", {}).get("vs", {}).get(name, {}).get(g)
                ord_row = r["groups"]["target_day_type"].get(ORDINARY, {}).get("grid_crps", {}).get("vs", {}).get(name, {}).get(g)
                if cal_row is None or ord_row is None or "undefined" in cal_row or "undefined" in ord_row:
                    continue
                beats = cal_row["skill_interval"][0] > 0.0
                loses = ord_row["skill_interval"][1] < 0.0
                out.append(f"- {LABELS[name]} {'beats' if beats else 'is not shown to beat'} {g} on calendar days "
                           f"({s761.pct(cal_row['skill'])}, lower bound {s761.pct(cal_row['skill_interval'][0])}) and "
                           f"{'loses' if loses else 'does not lose'} on ordinary days ({s761.pct(ord_row['skill'])}).")
        out.append("")
    out += ["## The Politis-White block beside the block of 10", "",
            "The automatic block length (Politis and White 2004, with the correction of Patton, Politis and White 2009) of the paired loss "
            "differential `S(a) - S(arm)`, in days, with the pooled skill over (a) at that block. Reported, never substituted for 10.", ""]
    columns = ["pooled"] + [l for l in REGIMES if l in r["politis_white"].get("regime", {})]
    for metric in METRIC_NAMES:
        out += [f"{metric_titles[metric]}:", "", "| | " + " | ".join(columns) + " | pooled skill vs (a) at that block |", "|---|" + "---|" * (len(columns) + 1)]
        for name in ("mr_cal_b_location", "mr_cal_c_location_scale", "mr_cal_d_no_fomc_iorb"):
            cells, at = [], ""
            for col in columns:
                split, label = ("pooled", "all decision days") if col == "pooled" else ("regime", col)
                e = r["politis_white"].get(split, {}).get(label, {}).get(metric, {}).get(name)
                cells.append("n/a" if not e else f"{e['block']:.1f}")
                if col == "pooled" and e and "row" in e:
                    at = f"block {e['at_block']}: {_fmt(e['row'])}"
            out.append(f"| {LABELS[name]} | " + " | ".join(cells) + f" | {at} |")
        out.append("")
    out += ["## The 95th-percentile exceedance rate against 0.05 (Eleonora, 22 October 2026, #756)", "",
            "The share of (decision day, lead) cells whose outcome is above the model's q95 (`y > q`), with a 90% stationary-bootstrap "
            "percentile interval over the cells in date order (mean block 50 cells). The nominal rate is 0.05. Whether a tie with the quantile "
            "is a hit is Eleonora's open question (#993): the rate on `y >= q` is in `result.json` and in the second table.", ""]
    names = [n for n in r["q95"]]
    for rule, title in (("hit_above", "`y > q`"), ("hit_at_or_above", "`y >= q`")):
        out += [f"Hit when {title}:", "", "| | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
        for m in list(MODELS) + list(r["gbm"]):
            cells = []
            for name in names:
                e = r["q95"][name].get(m, {}).get(rule)
                if e is None:
                    cells.append("n/a")
                else:
                    cells.append(f"{e['rate']:.3f} [{e['interval'][0]:.3f}, {e['interval'][1]:.3f}]")
            out.append(f"| {LABELS[m]} | " + " | ".join(cells) + " |")
        out.append("")
    labels = list(r["q95_by_day_type"])
    out += ["By target-day type (rate on `y > q`; no interval, the days of a type are scattered):", "", "| | " + " | ".join(labels) + " |", "|---|" + "---|" * len(labels)]
    for m in list(MODELS) + list(r["gbm"]):
        out.append(f"| {LABELS[m]} | " + " | ".join(
            f"{r['q95_by_day_type'][l][m]['rate']:.3f}" if m in r["q95_by_day_type"][l] else "n/a" for l in labels) + " |")
    out.append("")
    out += ["## The estimated effect of each term, by regime", "",
            "For each term, the effect in force on the flagged target days of the regime: the mean over the leads that forecast the day of "
            "the effect estimated at the refit the forecast used (0 where the term was absent from that refit), then the mean over the "
            "flagged days, in bp, with the 90% stationary-bootstrap percentile interval over those days in date order (mean block 10 "
            "flagged days; none under 5 days). The interval measures the spread of the estimates across refits and days, not a standard "
            "error of the effect. *Missed by (a)* is the mean outcome less arm (a)'s median on the same days, the same way.", ""]

    def cell_text(e: Optional[dict], quantity: str, scale: float = 1.0, places: int = 2) -> str:
        if e is None:
            return "–"
        q = e[quantity]
        text = f"{q['mean'] * scale:+.{places}f}"
        if q["interval"] is not None:
            text += f" [{q['interval'][0] * scale:+.{places}f}, {q['interval'][1] * scale:+.{places}f}]"
        return text + f" ({e['days']})"

    present = [l for l in REGIMES]
    for arm in ("mr_cal_b_location", "mr_cal_c_location_scale"):
        for quantity, title, scale, places in (("effect", "location effect (bp)", 1.0, 2), ("miss", "missed by (a) (bp)", 1.0, 2),
                                               ("uplift", "scale uplift (% of the ordinary scale)", 100.0, 0)):
            if quantity == "uplift" and arm != "mr_cal_c_location_scale":
                continue
            if quantity == "miss" and arm != "mr_cal_b_location":
                continue
            out += [f"**{LABELS[arm]}: {title}**; the number of flagged days is in brackets", "", "| term | " + " | ".join(present) + " |", "|---|" + "---|" * len(present)]
            for term in cal.ALL_TERMS:
                cells = [cell_text(r["term_effect_intervals"].get(arm, {}).get(term, {}).get(l), quantity, scale, places) for l in present]
                out.append(f"| {term} | " + " | ".join(cells) + " |")
            out.append("")
    out += ["Refits in which each term entered the fit (of %d refits), by lead 1 to 5, arm (b):" % r["refit_total"], "",
            "| term | " + " | ".join(f"h={h}" for h in sp.HORIZONS) + " |", "|---|" + "---|" * len(sp.HORIZONS)]
    for term, counts in r["refit_term_counts"]["mr_cal_b_location"].items():
        out.append(f"| {term} | " + " | ".join(str(c) for c in counts) + " |")
    out += ["", "## What this is not", "",
            "Development data from 2018 to 2025, split by regime and target-day type, never a verdict. The arms read the calendar at the target "
            "day on direct pairs, so their class is not provisional (`docs/research/provisional-calendar-register.md`), but the estimation "
            "choices (the ridge, the three-flag minimum, the scale floor, the three-row IORB window) are this study's own, were not tuned, and "
            "are open to Eleonora's review. #941's variant was itself chosen after seeing 2018-2025. Whether any term is adopted, and whether "
            "any arm is named a candidate, is Eleonora's decision.", ""]
    out += question(r)
    return "\n".join(out) + "\n"


def question(r: dict) -> List[str]:
    """The closing question for Eleonora (her ruling of 22 October 2026 on #1115)."""

    groups = r["groups"]
    cols = [("pooled", "all decision days", "pooled")] + [("regime", l, l) for l in REGIMES if l in groups.get("regime", {})] + [
        ("target_day_type", l, l) for l in list(DAY_TYPES) + [ORDINARY] if l in groups.get("target_day_type", {})]
    models = [g for g in GBMS if g in r["gbm"]] + [CTX, A, "mr_cal_b_location", "mr_cal_c_location_scale", "mr_cal_d_no_fomc_iorb"]
    out = ["## Question for Eleonora: `gbm_funding` or the calendar-aware scaled mean reversion?", "",
           "Your ruling of 22 October 2026 on #1115: `gbm_funding` stays the H5 candidate until this reports; you then decide between it and the "
           "calendar-aware scaled mean reversion on this evidence. **Nothing is adopted here and no claim changes.** The tables give the mean "
           "score of `gbm_funding`, `spread_mr_ctx`, #941's best variant (a) and the three calendar arms, pooled, by regime and by target-day "
           "type, for the grid CRPS and for the upper-tail twCRPS (lower is better; B1' and B1 are in the tables above)."
           + ("" if r["gbm"] else " **The `gbm_funding` rows are empty: its walks were not on the machine that scored this page.**"), ""]
    for metric, title in (("grid_crps", "Grid CRPS (bp)"), ("upper_tail_twcrps", "Upper-tail twCRPS (bp)")):
        out += [f"**{title}**", "", "| | " + " | ".join(c[2] for c in cols) + " |", "|---|" + "---|" * len(cols)]
        for m in models:
            cells = []
            for split, label, _name in cols:
                entry = groups.get(split, {}).get(label)
                cells.append("n/a" if entry is None or m not in entry[metric]["means"] else f"{entry[metric]['means'][m]:.3f}")
            out.append(f"| {LABELS[m]} | " + " | ".join(cells) + " |")
        out.append("")
    out += ["**Options** (numbered; the default applies if you have not answered by the next 5 pm batch):", "",
            "1. **Keep `gbm_funding` as the H5 candidate** (default). Nothing changes; the calendar terms stay a development result.",
            "2. **Name the calendar-aware scaled mean reversion (which arm: your choice) as the candidate to take forward**, on the evidence above. "
            "That is a decision for you and would be followed by a registration discussion; this page does not pre-empt it.",
            "3. **Ask for a further step** before deciding (for example the same arms on the 2026 development days, or a combination with "
            "`gbm_funding`).", ""]
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
    s.add_argument("--walks", help="a directory holding gbm_funding_h<lead>.json and gbm_funding_cal_aligned_h<lead>.json")
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--reps", type=int, default=2000, help="bootstrap resamples of an exceedance or effect interval")
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
