"""Calendar target rows at full weight in (s3)'s Huber fit, scored (#1226; H5 step 3 fix, avenue #1213).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`. Every
choice is in `metadata/s3_huber_calendar_1226.json`, which this script refuses to read unless it is committed and unchanged. The arms
are `repo_model.spread_mr_state_calendar`'s: (s3) of #1145 (#941's scaled mean reversion with calendar terms in standardised units, a
Huber fit, ridge 5), the comparator; (s3-hw1), (s3) with the target rows that carry a calendar type at full weight in the Huber fit
(Huber downweighting on ordinary target rows only); and (s3-hw2), (s3) with those rows' Huber threshold at `CALENDAR_K` (2) times the
ordinary one. Terms, ridge, direct pairs and the turn record in force are (s3)'s. They are scored with the scorer of scoring protocol
v1 (`repo_model.scoring_protocol`) against (s3), (a), B1, B1' (#960) and B2 and, when its walks are supplied, `gbm_funding`, with the
studentized stationary bootstrap of ruling 1 (read on the bound on mean d, her #1009 ruling, with the skill interval beside), the
Politis-White block beside it, and the q95 exceedance and band coverage under both hit rules. The day-type intervals keep the current
method (the days of a type, scattered, resampled in date order as if consecutive), which #1221 questions and #1228 measures; the page
labels them so. The scaled score of #967 is not scored (see #1196's declaration, amendment 1). Scored decision days are those whose
five targets are on or before 2025-12-31; no later day is read and no locked day is scored (`docs/decisions/lockbox.md`). Nothing
here is a verdict (scoring protocol v1, #640).

It reuses the helpers of `scripts/calendar_mr_1115.py`, `scripts/state_calendar_1145.py`, `scripts/s3_decomposition_1172.py` and
`scripts/s3_terms_1196.py` (the frame, the cells, the groups, the readings). The scarcity state is read from the measurement panel
built from tracked fixtures only, no network; no arm of this study uses it, the walk only records it.

The walks take minutes; the paired tests are the long part (about 40 minutes on 4 cores, as #1196), so the run is a cloud run. The
comparison with `gbm_funding` needs its walks, which come from Eleonora's Mac (`.claude/skills/long-run`) and are not run first.
Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    # optional: WALKS/gbm_funding_h<h>.json (scripts/spread_distribution_634.py walk), all five leads
    PYTHONPATH=src python3 scripts/s3_huber_calendar_1226.py score --panel PUB.csv [--walks WALKS] \\
        --output docs/research/s3-huber-calendar-1226/result.json
    PYTHONPATH=src python3 scripts/s3_huber_calendar_1226.py page \\
        --score docs/research/s3-huber-calendar-1226/result.json --output docs/research/s3-huber-calendar-1226-result.md

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
from repo_model import spread_mr_calendar as cal, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.splits import SplitError  # noqa: E402

c = _load("calendar_mr_1115")
s686, s761, b949 = c.s686, c.s761, c.b949
sv = _load("scarcity_validation")
d1145 = _load("state_calendar_1145")
d1172 = _load("s3_decomposition_1172")
m1167 = _load("mean_d_reading_1167")
d1196 = _load("s3_terms_1196")

DECLARATION = REPO / "metadata" / "s3_huber_calendar_1226.json"
SEED = 1226
LAST_DAY = c.LAST_DAY
DECISION_TIME = c.DECISION_TIME
MIN_GROUP_DAYS = c.MIN_GROUP_DAYS
GBM = "gbm_funding"
GBMS = (GBM,)
B1P = c.B1P
A = sc.ARM_A
S3, H1, H2 = (arm.name for arm in sc.HW_ARMS)
#: The arms scored against the references, (a) first.
ARMS = (A, S3, H1, H2)
BENCHMARKS = ("B1", B1P, "B2")
MODELS = BENCHMARKS + ARMS
#: Each new arm differs from (s3) by one thing: what the pair isolates.
ISOLATES = {H1: (S3, "calendar target rows at full weight in the Huber fit"),
            H2: (S3, "the calendar rows' own Huber threshold at 2 times the ordinary one")}
METRIC_NAMES = c.METRIC_NAMES
REGIMES = c.REGIMES
DAY_TYPES = c.DAY_TYPES
ORDINARY = c.ORDINARY
MEDIAN = c.MEDIAN
#: The splits the directive names: the two (s3) loses on the upper tail on the mean-d bound (#1187), the 2020 regime and the FOMC
#: target days, and the IORB-window and quarter-end target days that #1215 made readable.
AIMED = (("regime", "2020"), ("target_day_type", "fomc_day"), ("target_day_type", "iorb_window"), ("target_day_type", "quarter_end"))
#: The calendar target-day types of the report, each read beside the ordinary-day reading of the same arm and reference.
CALENDAR_TYPES = ("month_end", "quarter_end", "tax_date", "settlement", "fomc_day", "iorb_window", "dom_19_23", "post_month_end_window",
                  "calendar_days")
#: The calibration measures of a cell: the q95 exceedance under both hit rules and the 50% and 90% bands, closed and open.
RATES = ("hit_above", "hit_at_or_above", "b50_closed", "b50_open", "b90_closed", "b90_open")
Q95 = c.Q95



verdict = d1196.verdict
skill_verdict = d1196.skill_verdict
_fmt = d1172._fmt
tally = d1196.tally


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


# -- the state -------------------------------------------------------------------------------------------------------


def decision_states(registry_path: Path) -> Dict[date, Optional[float]]:
    """The scarcity state a decision on each panel day could read, keyed by the DECISION day (`state_calendar_1145.decision_states`)."""

    return d1145.decision_states(registry_path)


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
    mine = sc.walk(panel, candidate_days, table, states, sc.HW_ARMS, **settings)
    days = [d for d in candidate_days if d in b1 and all(d in mine.forecasts[a] for a in ARMS)]
    frame.days = days
    frame.forecasts = {"B1": b1, B1P: b1p, "B2": b2, **{a: mine.forecasts[a] for a in ARMS}}
    for name in list(frame.forecasts):
        frame.forecasts[name] = {d: frame.forecasts[name][d] for d in days}
    notes = {
        "decision_days_offered": len(candidate_days), "candidate_skipped_for_history": len(mine.skipped),
        "benchmark_missing": [d.isoformat() for d in dropped], "scored_decision_days": len(days),
        "first": days[0].isoformat(), "last": days[-1].isoformat(),
        "last_target": frame.target(days[-1], max(sp.HORIZONS)).isoformat(), "refits": len(mine.fits),
    }
    return frame, notes, mine


# -- the cells -------------------------------------------------------------------------------------------------------


def cell_table(frame, forecasts: Mapping[date, Mapping[int, Sequence[float]]]) -> Dict[str, Dict[Tuple[date, int], float]]:
    """Both scores and the calibration hits of every (decision day, lead) cell of `forecasts` (`state_calendar_1145.cell_table`)."""

    return d1145.cell_table(frame, forecasts)


# -- the tests, in parallel ------------------------------------------------------------------------------------------

_STATE: Dict = {}


def pair_plan(candidate: str, have: Sequence[str]) -> List[str]:
    """What a candidate is tested against: B1, B1' and B2, (a) for every arm but (a), (s3) for the two arms that add to it, and gbm."""

    names = list(BENCHMARKS)
    if candidate != A:
        names.append(A)
    if candidate in ISOLATES:
        names.append(ISOLATES[candidate][0])
    names += [g for g in GBMS if g in have]
    return names


def block_plan(candidate: str) -> List[str]:
    """What the Politis-White block is reported against: (a) for every arm, and (s3) for the two arms that add to it."""

    if candidate == A:
        return []
    return [A] + ([S3] if candidate in ISOLATES else [])


def _pairs_task(job):
    split, label, grain, metric, candidate, members = job
    series = _STATE["series"][(grain, metric)]
    out: Dict[str, dict] = {}
    for name in pair_plan(candidate, _STATE["gbm_have"]):
        days = [d for d in members if d in series[name]] if name in GBMS else list(members)
        if len(days) < MIN_GROUP_DAYS:
            continue
        out[name] = s761.run_pairs({name: series[name]}, series[candidate], days, seed=SEED, draws=_STATE["draws"],
                                  mean_d_fallback=True)[name]
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


def term_effects(frame, table: cal.TermTable, mine: sc.Walk) -> dict:
    """Per arm and term: for each flagged target day, the effect in bp and in scale units in force, and what (a) missed.

    For each flagged target day T (the term's flag at the lead's reading), the mean over the leads that forecast T of
    `scale(anchor) * (beta_j + gamma_j * s)` (bp) and `beta_j + gamma_j * s` (scale units) at the refit the forecast used (0 where
    the term was absent from it; `gamma_j` is 0 where the arm has no interaction), and of the outcome less arm (a)'s median.
    Returned in date order for the intervals.
    """

    out: dict = {}
    for arm in sc.HW_ARMS:
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


def calendar_pair_shares(mine: sc.Walk) -> dict:
    """For the arms with a calendar threshold: the mean over the refits and leads of the share of training pairs whose target row is
    a calendar row."""

    out: dict = {}
    for arm in sc.HW_ARMS:
        if arm.calendar_k is None:
            continue
        shares = []
        for per_arm in mine.estimates.values():
            for h in sp.HORIZONS:
                est = per_arm[arm.name][h]
                shares.append(est.calendar_pairs / est.pairs)
        out[arm.name] = {"mean_share": sum(shares) / len(shares), "fits": len(shares)}
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

    groups = c.groups_of(frame, labels)
    series: Dict[Tuple[str, str], Dict[str, Dict[date, float]]] = {}
    for _s, _l, grain, _m in groups:
        for metric in METRIC_NAMES:
            if (grain, metric) not in series:
                entry = {m: c.series_of(frame, cells[m][metric], grain) for m in MODELS}
                for name, table_ in gbm_frames.items():
                    entry[name] = c.series_of(frame, table_[metric], grain)
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

    by_key = {(s_, l_): (g, m) for s_, l_, g, m in groups}
    result: dict = {
        "issue": 1226, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": published_sha,
        "subset_from": None if args.first is None else args.first.isoformat(), "label": "development, not a verdict",
        "seed": SEED, "draws": args.draws, "reps": args.reps, "notes": notes, "models": list(MODELS), "gbm": sorted(gbm_frames),
        "arms": [{"name": a.name, "role": a.role, "location": list(a.location), "interact": a.interact, "robust": a.robust,
                  "ridge": sc.ridge_of(a), "calendar_k": None if a.calendar_k is None else (
                      "full weight" if a.calendar_k == sc.FULL_WEIGHT else a.calendar_k)} for a in sc.HW_ARMS],
        "refits": [{"fitted_on": day.isoformat(), "phi": fit.phi} for day, fit in sorted(mine.fits.items())],
        "groups": {}, "skipped_groups": skipped, "politis_white": {}, "q95": {},
        "reading_rules": declaration["reading_rules"],
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
        for arm in sc.HW_ARMS
    }
    result["refit_total"] = len(mine.estimates)
    result["robust_fits"] = {}
    for arm in sc.HW_ARMS:
        passes = [est[arm.name][h].iterations for est in mine.estimates.values() for h in sp.HORIZONS]
        result["robust_fits"][arm.name] = {"fits": len(passes), "capped": sum(1 for x in passes if x >= sc.MAX_ITERATIONS),
                                           "cap": sc.MAX_ITERATIONS, "mean_passes": sum(passes) / len(passes)}
    result["calendar_pairs"] = calendar_pair_shares(mine)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page --------------------------------------------------------------------------------------------------------

LABELS = {"B1": "B1", B1P: "B1' (#960)", "B2": "B2", GBM: "gbm_funding (#634)", A: "(a) base: #941 mad 20, floor 0.5"}
LABELS.update({a.name: a.role for a in sc.HW_ARMS})
LABELS[S3] = "(s3) (s1) with a Huber fit and a heavier ridge; the H5 candidate"
METRIC_TITLES = {"grid_crps": "grid CRPS (23 levels)", "upper_tail_twcrps": "upper-tail twCRPS (weight 1{z > 0 bp})"}


def model_table(r: dict, cell: dict) -> List[str]:
    """Mean score of every model in one group, and each arm's skill over B1, B1', B2, (a), (s3) and gbm_funding, each with the
    mean-d bound beside it."""

    gbm = [g for g in GBMS if g in r["gbm"]]
    out = ["| | mean | skill vs B1 [90%]; mean d (bp) [90%] | vs B1' | vs B2 | vs (a) | vs (s3)" + "".join(f" | vs {g}" for g in gbm) + " |",
           "|---|---|---|---|---|---|---|" + "---|" * len(gbm)]
    means = cell["means"]
    for name in list(BENCHMARKS) + gbm:
        if name in means:
            out.append(f"| {LABELS[name]} | {means[name]:.3f} |" + " |" * (5 + len(gbm)))
    for name in ARMS:
        vs = cell["vs"].get(name, {})
        cells = ([_fmt(vs.get(b)) for b in ("B1", B1P, "B2")] + ["" if name == A else _fmt(vs.get(A))]
                 + ["" if name in (A, S3) else _fmt(vs.get(S3))] + [_fmt(vs.get(g)) for g in gbm])
        out.append(f"| {LABELS[name]} | {means[name]:.3f} | " + " | ".join(cells) + " |")
    return out


def reading_words(row: Optional[dict]) -> str:
    """`gain`, `loss` or `undecided` on the mean-d bound, with the skill interval's reading in brackets where it differs."""

    word, other = verdict(row), skill_verdict(row)
    if row is not None and "undefined" in row:
        return word
    return word if word == other else f"{word} (skill interval: {other})"


def _bold(words: str) -> str:
    """The reading in bold, once: a "no reading" phrase is bold already (#1215)."""

    return words if words.startswith("**") else f"**{words}**"


def aimed_rows(r: dict) -> List[dict]:
    """For the splits (s3) loses on the upper tail (`AIMED`) and each of the two arms and (s3): the day count, the mean score, and
    the reading against (a) and against (s3) on the upper-tail twCRPS and on the grid CRPS."""

    rows = []
    for split, label in AIMED:
        entry = r["groups"].get(split, {}).get(label)
        if entry is None:
            continue
        for arm in (S3, H1, H2):
            row = {"split": split, "group": label, "days": entry["days"], "arm": arm}
            for metric in METRIC_NAMES:
                vs = entry[metric]["vs"].get(arm, {})
                row[metric] = {"mean": entry[metric]["means"][arm], "vs_a": vs.get(A),
                               "vs_s3": None if arm == S3 else vs.get(S3)}
            rows.append(row)
    return rows


def _share(value: Optional[float]) -> str:
    return "n/a" if value is None else f"{100 * value:.0f}%"


def render(r: dict) -> str:
    n = r["notes"]
    pooled = r["groups"]["pooled"]["all decision days"]
    out = [
        "# Calendar target rows at full weight in (s3)'s Huber fit (#1226)", "",
        "**Hypothesis and step:** H5 (primary goal), step 3 fix (calendar first; refocus), avenue #1213, her ruling of 26 October 2026 (ledger item 52, option 1). **Development data, not a verdict** "
        f"(scoring protocol v1, #640): days to {n['last_target']}, no lockbox day. Nothing is adopted and no claim changes. Generated by "
        f"`scripts/s3_huber_calendar_1226.py page` from `docs/research/s3-huber-calendar-1226/result.json`, not edited by hand; declared in "
        f"`{r['declaration']}` before any number.", "",
        "**What kind of look this is.** This is a further look at 2018-2025 after (s3) was chosen on the same days: (s3) was picked from "
        "#1145's arms on this data, and the two arms here are aimed at the upper-tail losses it showed on the mean-d bound, in 2020 "
        "and on FOMC target days (finding #1187; her open question before registration). The two arms count toward the variant count. "
        "A gain here is evidence for a question, with the selection noted, not a result. **An arm replaces (s3) only if it beats it "
        "without an ordinary-day loss, and that decision is Eleonora's.**", "",
        f"Panel digest `{r['panel_sha256'][:8]}…`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business days, "
        f"{r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval (the lower end is the one-sided 95% bound). Skill is "
        "`mean(d) / mean(S(benchmark))` with `d = S(benchmark) - S(candidate)`, positive favours the candidate. **Every row shows the skill "
        "interval and, beside it, the studentized interval on mean d (bp); a reading (gain, loss, undecided) is taken from the mean-d bound** "
        "(her ruling on #1009, 20 October 2026), not from the skill interval. **Caveat (Lens C, #958):** the lag-10 HAC standard error that "
        "studentizes the bound is understated about 2x after 2020, so an interval that excludes zero is narrower than it should be; a "
        f"reading here is evidence for a question. Where the benchmark scores zero on a resample, skill is undefined but the mean-d bound is still computed (#1215): the row shows \"skill undefined\" and is read on the bound. A row with no mean-d bound reads \"no reading\" with the reason, not \"undecided\". "
        f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); the "
        f"fit is renewed {n['refits']} times. B1' (Lens C's calendar-aware persistence, #960) is reported beside B1 in every table; B1 and "
        "B2 stay the protocol's benchmarks.", "",
        "**The arms.** (s3) of #1145 is #941's scaled mean reversion (a) with seven calendar terms in standardised units, a Huber fit "
        "and a ridge of 5 pseudo-days. Its Huber fit downweights every training row whose residual is beyond 1.345 robust standard "
        "deviations, calendar rows included, and the calendar rows are where the terms' effects are measured. **(s3-hw1)** is (s3) with "
        "the training pairs whose *target row* carries a calendar type at full weight (weight 1, however large the residual) and the "
        "Huber downweighting on the ordinary target rows only. **(s3-hw2)** is (s3) with the calendar rows' own Huber threshold at "
        f"k = {sc.CALENDAR_K:g} times the ordinary one ({sc.HUBER_K * sc.CALENDAR_K:.3f} robust standard deviations against {sc.HUBER_K}); "
        "k is declared, is one value and was not tuned. A *calendar row* is a target row that is a month-end, quarter-end, tax date, "
        "coupon or bill settlement, FOMC day or IORB-window day on the term table, or a turn day of the month-end record in force since "
        "#1161 (`turn_days.turn_label`); `dom_19_23` and `post_month_end_window` are terms of the fit but too broad to name a calendar row, "
        "so a row carrying only one of them is ordinary for the weights. The type is read from the target row alone, after the fact, "
        "for a row on or before the anchor (the training pairs); the forecast reads nothing new. The robust scale, the terms, the ridge "
        "of 5, direct pairs and the 21-day refit are (s3)'s. The benchmarks and the mean-reversion level read the pressure-day types of "
        "the month-end turn record in force since #1161, so (a) and (s3) are not the figures of the #1145 and #1172 pages, which were "
        "scored on the earlier labels; the arms are compared with each other here. The scaled score of #967 is not scored: its pool "
        "needs B2 on days the in-force record cannot forecast.", "",
        "**Day-type intervals.** The by-day-type intervals on this page use the current method: the days of a type, scattered across "
        "the sample, are resampled in date order as if consecutive. #1221 questions that method and #1228 measures a domain estimate "
        "beside it on #1196; #1221 has not merged, so these intervals keep the current method and are labelled as such. The quarter-end, "
        "IORB-window and FOMC rows in particular rest on it.", ""]
    if r["gbm"]:
        out += ["The `gbm_funding` comparison uses the walks supplied, on the decision days both cover.", ""]
    else:
        out += ["**The `gbm_funding` walks were not supplied**, so no row compares an arm with it; the comparison is a long run that stays on "
                "Eleonora's Mac (`needs-mac`, the same `score` command with `--walks`) and was not run first. #1115's figure for (a) "
                "against it is +6.8% pooled [+3.3%, +10.1%].", ""]
    out += ["## Does an arm beat (s3)?", "",
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
            + (f" | {t['gain']} / {t['loss']} / {t['undecided']}" + (f" / {t['no reading']} no reading" if t["no reading"] else "")
               + f" | {_fmt(ordv)} | {_fmt(calv)} |" if t else " | | | |"))
    out.append("")
    out += ["## Aimed at (s3)'s upper-tail losses: 2020, the FOMC, IORB-window and quarter-end target days", "",
            "On #1194's reading of the #1145 record (scored on the earlier pressure-day labels) (s3) loses to (a) on upper-tail twCRPS in 2020 and on FOMC target days (#1187; #1194); this run, on the labels in force, is read afresh below. The rows are "
            "those splits, for (s3) and for each arm: the mean score (bp) and the reading "
            "against (a) and against (s3), on the upper-tail twCRPS (the key secondary) and on the grid CRPS (the primary). A reading is "
            "taken from the mean-d bound; the skill interval's reading is in brackets where it differs.", "",
            "| split | days | model | twCRPS mean | twCRPS vs (a) | twCRPS vs (s3) | grid CRPS mean | grid CRPS vs (a) | grid CRPS vs (s3) |",
            "|---|---|---|---|---|---|---|---|---|"]
    for row in aimed_rows(r):
        tw, gr = row["upper_tail_twcrps"], row["grid_crps"]
        out.append(
            f"| {row['group']} | {row['days']} | {LABELS[row['arm']]} | {tw['mean']:.3f} | {_fmt(tw['vs_a'])}: {_bold(reading_words(tw['vs_a']))} "
            f"| {'' if tw['vs_s3'] is None else _fmt(tw['vs_s3']) + ': **' + reading_words(tw['vs_s3']) + '**'} | {gr['mean']:.3f} "
            f"| {_fmt(gr['vs_a'])}: {_bold(reading_words(gr['vs_a']))} "
            f"| {'' if gr['vs_s3'] is None else _fmt(gr['vs_s3']) + ': **' + reading_words(gr['vs_s3']) + '**'} |")
    out += ["## Calendar-day types beside ordinary days", "",
            "For every calendar target-day type (the groups overlap) the reading of each arm against (s3) and against (a) on the grid CRPS "
            "and the upper-tail twCRPS, with **the same arm's reading on ordinary days printed beside it**: an arm that gains on a calendar "
            "type and loses on ordinary days does not meet the adoption rule. Day-type intervals keep the current method (see above).", "",
            "| target-day type | days | arm | grid CRPS vs (s3) | same, ordinary days | twCRPS vs (s3) | same, ordinary days | "
            "grid CRPS vs (a) | same, ordinary days |", "|---|---|---|---|---|---|---|---|---|"]
    by_type = r["groups"].get("target_day_type", {})
    for label in CALENDAR_TYPES:
        entry = by_type.get(label)
        if entry is None:
            continue
        for arm in (S3, H1, H2):
            def cellv(group, metric, ref):
                row = (by_type.get(group) or {}).get(metric, {}).get("vs", {}).get(arm, {}).get(ref)
                return "n/a" if row is None else f"{_fmt(row)}: {_bold(reading_words(row))}"
            ord_ = by_type.get(ORDINARY)
            vs_s3 = lambda g, m: "" if arm == S3 else cellv(g, m, S3)
            out.append(f"| {label} | {entry['days']} | {LABELS[arm]} | {vs_s3(label, 'grid_crps')} | {vs_s3(ORDINARY, 'grid_crps')} "
                       f"| {vs_s3(label, 'upper_tail_twcrps')} | {vs_s3(ORDINARY, 'upper_tail_twcrps')} "
                       f"| {cellv(label, 'grid_crps', A)} | {cellv(ORDINARY, 'grid_crps', A)} |")
    out.append("")
    for split, title in (("pooled", "Pooled"), ("lead", "By lead")):
        for label, entry in r["groups"].get(split, {}).items():
            for metric in METRIC_NAMES:
                out += [f"## {title}: {label}, {METRIC_TITLES[metric]}, mean over leads 1 to 5 (bp)" if split == "pooled"
                        else f"### {label}, {METRIC_TITLES[metric]}", ""] + model_table(r, entry[metric]) + [""]
    for split, title, order in (("regime", "regime (target day)", REGIMES),
                                ("target_day_type", "target-day type (the groups overlap; FOMC and IORB days named)",
                                 list(DAY_TYPES) + [ORDINARY, "calendar_days"])):
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
    out += ["## Reading under the declared rules (the mean-d bound, with the skill interval's reading beside it)", ""]
    for name in (S3, H1, H2):
        for reference in ([A] if name == S3 else [A, S3]):
            parts = []
            for split in ("pooled", "regime", "target_day_type"):
                for label, entry in r["groups"].get(split, {}).items():
                    parts.append(f"{label}: {reading_words(entry['grid_crps']['vs'].get(name, {}).get(reference))}")
            out.append(f"- **{LABELS[name]}** against {'(a)' if reference == A else '(s3)'}, grid CRPS: " + "; ".join(parts) + ".")
        parts = []
        for split in ("pooled", "regime", "target_day_type"):
            for label, entry in r["groups"].get(split, {}).items():
                parts.append(f"{label}: {reading_words(entry['upper_tail_twcrps']['vs'].get(name, {}).get(S3 if name != S3 else A))}")
        out.append(f"- **{LABELS[name]}** against {'(s3)' if name != S3 else '(a)'}, upper-tail twCRPS: " + "; ".join(parts) + ".")
    out.append("")
    for name in (H1, H2):
        other, what = ISOLATES[name]
        row = pooled["grid_crps"]["vs"][name].get(other)
        tw = pooled["upper_tail_twcrps"]["vs"][name].get(other)
        out.append(f"- {LABELS[name]} against (s3) isolates {what}: grid CRPS {_fmt(row)}; twCRPS {_fmt(tw)}.")
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
                if name == A or (reference == S3 and name == S3):
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
            out += ["By target-day type (no interval, the days of a type are scattered):", "", "| | " + " | ".join(labels) + " |", "|---|" + "---|" * len(labels)]
            for m in list(MODELS) + list(r["gbm"]):
                out.append(f"| {LABELS[m]} | " + " | ".join(
                    f"{r['q95_by_day_type'][l][m][rule]:.3f}" if m in r["q95_by_day_type"][l] else "n/a" for l in labels) + " |")
            out.append("")
    out += ["The 95th-percentile and band rates under the other hit rule agree with these to within a tie of the outcome with a quantile; "
            "which rule counts is Eleonora's open question (#993), so both are above and in `result.json`.", ""]
    out += ["## The estimated effect of each term, by regime", "",
            "For each term, the effect in force on the flagged target days of the regime: the mean over the leads that forecast the day of "
            "`scale(anchor) * (beta + gamma * s)` at the refit the forecast used (0 where the term was absent from that refit; `gamma` is "
            "0 for the arms with no interaction), then the mean over the flagged days, in bp, with the 90% stationary-bootstrap percentile "
            "interval over those days in date order (mean block 10 flagged days; none under 5 days). The interval measures the spread of "
            "the estimates across refits and days, not a standard error of the effect. The number of flagged days is in brackets.", ""]

    def cell_text(e: Optional[dict], quantity: str, places: int = 2) -> str:
        if e is None:
            return "–"
        q = e[quantity]
        text = f"{q['mean']:+.{places}f}"
        if q["interval"] is not None:
            text += f" [{q['interval'][0]:+.{places}f}, {q['interval'][1]:+.{places}f}]"
        return text + f" ({e['days']})"

    for arm in sc.HW_ARMS:
        for quantity, title, places in (("bp", "effect (bp)", 2), ("std", "effect (scale units)", 3)):
            out += [f"**{LABELS[arm.name]}: {title}**", "", "| term | " + " | ".join(REGIMES) + " |", "|---|" + "---|" * len(REGIMES)]
            for term in arm.location:
                out.append(f"| {term} | " + " | ".join(
                    cell_text(r["term_effect_intervals"].get(arm.name, {}).get(term, {}).get(l), quantity, places) for l in REGIMES) + " |")
            out.append("")
    out += ["**Missed by (a)**: the mean outcome less (a)'s median on the same flagged days, in bp", "", "| term | " + " | ".join(REGIMES) + " |",
            "|---|" + "---|" * len(REGIMES)]
    for term in cal.ALL_TERMS:
        out.append(f"| {term} | " + " | ".join(
            cell_text(r["term_effect_intervals"].get(H2, {}).get(term, {}).get(l), "miss") for l in REGIMES) + " |")
    out.append("")
    out += [f"Refits in which each term entered the fit (of {r['refit_total']} refits), by lead 1 to 5:", ""]
    for arm in sc.HW_ARMS:
        out += [f"{LABELS[arm.name]}:", "", "| term | " + " | ".join(f"h={h}" for h in sp.HORIZONS) + " |", "|---|" + "---|" * len(sp.HORIZONS)]
        for term, counts in r["refit_term_counts"][arm.name].items():
            if term in arm.location:
                out.append(f"| {term} | " + " | ".join(str(x) for x in counts) + " |")
        out.append("")
    shares = r["calendar_pairs"]
    out += [f"Share of training pairs whose target row is a calendar row, mean over the {r['refit_total']} refits and the five leads: "
            + "; ".join(f"{LABELS[k]} {100 * v['mean_share']:.1f}%" for k, v in shares.items()) + ".", ""]
    for name, info in r["robust_fits"].items():
        out.append(f"The Huber fit of {LABELS[name]} took {info['mean_passes']:.1f} iterations on average and reached its cap "
                   f"(`MAX_ITERATIONS` = {info['cap']}) without the coefficients settling to 1e-8 in {info['capped']} of {info['fits']} fits (refit by lead).")
    out.append("")
    out += ["## What this is not", "",
            "Development data from 2018 to 2025, split by regime and target-day type, never a verdict. The arms read the calendar at the target "
            "day on direct pairs, so their class is not provisional (`docs/research/provisional-calendar-register.md`), but the choices "
            "(the terms, the ridge of 5 and Huber's threshold of (s3)) are #1145's and were not tuned here; the choices of this study (which "
            "rows are calendar rows, and k = 2 for (s3-hw2)) are declared in the declaration, were not tuned, and are open to Eleonora's "
            "review. #941's variant was itself chosen after seeing 2018-2025, and (s3) was chosen on the same days: this is a further look "
            "at data already used for that choice, aimed at the losses it showed. The FOMC and IORB-window days are few (the counts are in "
            "`result.json`), so the per-type intervals are wide, and they keep the current day-type method (#1221). Whether an arm "
            "replaces (s3) as the H5 candidate is her decision.", ""]
    out += question(r)
    return "\n".join(out) + "\n"


def question(r: dict) -> List[str]:
    """The closing question for Eleonora (her ruling of 26 October 2026 on #1226: an arm replaces (s3) only if it beats it without an ordinary-day loss)."""

    groups = r["groups"]
    cols = [("pooled", "all decision days", "pooled")] + [("regime", l, l) for l in REGIMES if l in groups.get("regime", {})] + [
        ("target_day_type", l, l) for l in [ORDINARY, "calendar_days", "fomc_day", "iorb_window", "quarter_end"] if l in groups.get("target_day_type", {})]
    models = [GBM] * (GBM in r["gbm"]) + list(ARMS)
    out = ["## Question for Eleonora: does an arm replace (s3) as the H5 candidate?", "",
           "Your ruling of 26 October 2026 on #1226: an arm replaces (s3) only if it beats it without an ordinary-day loss, and that is your decision on this page's "
           "evidence. **Nothing is adopted here and no claim changes.** The tables give the mean score of (a), (s3) and the two arms, "
           "pooled, by regime and by ordinary, calendar, FOMC and IORB-window days (lower is better; B1, B1' and B2 are in the tables above)."
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
            "1. **Keep (s3) as the H5 candidate** (default). Nothing changes; the two arms stay development results.",
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
