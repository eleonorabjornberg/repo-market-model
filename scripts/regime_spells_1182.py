"""The H5 candidate with calm and stress spells, scored (#1182; H5 step 3, fix: clustered misses).

A development study, never a verdict. It writes JSON, Markdown and one SVG to the paths it is given and nothing into `docs/runs/`.
Every choice is in `metadata/regime_spells_1182.json`, which this script refuses to read unless it is committed and unchanged.
The base is (s3) of #1145 (`repo_model.spread_mr_state_calendar`), the comparator beside it is (a), #941's variant
(`repo_model.spread_mr_fhs`); the arms (m1) (the observable episode state, memory 3 and 5 rows), (m2) (a two-state Markov-switching
scale) and (m3) ((m2) with a calendar-driven entry to stress) are `repo_model.spread_mr_regime`. They are scored with the scorer of
scoring protocol v1 (`repo_model.scoring_protocol`) against (s3), (a), B1 with B1' beside it and B2 (`repo_model.protocol_benchmarks`,
`repo_model.b1_calendar`), on the studentized stationary bootstrap of ruling 1 (#739), the skill interval with the studentized
interval of mean(d) beside it and the reading on that bound (#1009), the Politis-White block beside the block of 10 and the scaled
score of #967 beside the raw one. Scored decision days are those whose five targets are on or before 2025-12-31; no later day is read
and no locked day is scored (`docs/decisions/lockbox.md`).

The headline is the clustering of the misses, as #1153 and #1175: coverage of the 50, 80, 90 and 98% bands, the exceedances of q05,
q95, q01 and q99, Kupiec's test, Christoffersen's independence and conditional coverage tests per lead under the strict rule
(`above`), the at-or-beyond rule (`at_or_above`) and the randomised tie rule of #1156 (`randomised`), and the length of the runs of
misses, against (s3). The forecast is 23 quantiles of a continuous law, so the tie probability at each is 0 and the randomised rule
coincides with `above`; the page says so. The filtered stress probability of (m2) and (m3) is drawn over the scored decision days.

The helpers of `scripts/faster_scale_1153.py` (the cells, the runs, the kill assessment) are used unchanged except the kill rule, which
is this issue's. Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/regime_spells_1182.py score --panel PUB.csv \\
        --output docs/research/regime-spells-1182/result.json
    PYTHONPATH=src python3 scripts/regime_spells_1182.py page \\
        --score docs/research/regime-spells-1182/result.json --output docs/research/regime-spells-1182-result.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import multiprocessing
import random
import sys
import xml.sax.saxutils
from datetime import date
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))


def _load(name: str):
    loaded = sys.modules.get(name)
    if loaded is not None and Path(getattr(loaded, "__file__", "")) == REPO / "scripts" / f"{name}.py":
        return loaded
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


from repo_model import announced_iorb, b1_calendar as b1c  # noqa: E402
from repo_model import coverage_tests as ct  # noqa: E402
from repo_model import protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model import spread_mr_calendar as cal, spread_mr_regime as rg  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.splits import SplitError  # noqa: E402

f1153 = _load("faster_scale_1153")
s686, s761, s967, f941, b949, w1133 = f1153.s686, f1153.s761, f1153.s967, f1153.f941, f1153.b949, f1153.w1133

DECLARATION = REPO / "metadata" / "regime_spells_1182.json"
IORB_TABLE = f1153.IORB_TABLE
SEED = 1182
LAST_DAY = s686.LAST_DAY
DECISION_TIME = s686.DECISION_TIME
MIN_GROUP_DAYS = s686.MIN_GROUP_DAYS
A = rg.ARM_A
S3 = rg.BASE_ARM.name
ARMS: Tuple[str, ...] = tuple(a.name for a in rg.ARMS)
M2, M3 = "m2_markov", "m3_markov_calendar"
BENCHMARKS: Tuple[str, ...] = f1153.BENCHMARKS
#: What each candidate is paired against, besides the benchmarks.
COMPARATORS: Tuple[str, ...] = (S3, A)
METRICS = f1153.METRICS
COVERAGE_METRICS = f1153.COVERAGE_METRICS
BANDS = f1153.BANDS
REGIME_ORDER, DAYTYPE_ORDER = f1153.REGIME_ORDER, f1153.DAYTYPE_ORDER
SPLIT_TITLES, METRIC_TITLES = f1153.SPLIT_TITLES, f1153.METRIC_TITLES
OFF_ZERO = f1153.OFF_ZERO
#: The hit rules: coverage_tests' two deterministic ones, then the randomised tie rule of #1156.
RULES: Tuple[str, ...] = tuple(ct.HIT_RULES) + ("randomised",)
#: The kill rule's: an arm cuts the mean run when it falls below this share of (s3)'s.
RUN_CUT = 0.15
LABELS: Dict[str, str] = {
    "B1": "B1", "B1p": "B1' (#960)", "B2": "B2", A: "(a) #941 mad20", S3: "(s3) base (#1145)",
    "m1_episode_k3": "(m1) episode, last 3 rows", "m1_episode_k5": "(m1) episode, last 5 rows",
    M2: "(m2) Markov-switching scale", M3: "(m3) (m2) with calendar entry",
}
LENS_C = ("Lens C's caveat (#958, #1009): the lag-10 HAC standard error behind a studentized interval is understated by about 2x "
          "after 2020, so an interval after 2020 is narrower than it should be.")


def label_of(model: str) -> str:
    return LABELS.get(model, model)


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


def constants_agree(declaration: Mapping) -> List[str]:
    """The names of the declared constants that differ from the module's (empty when they agree)."""

    declared = declaration["arms"]["constants"]
    actual = {
        "episode_memory": list(rg.K_EPISODE), "min_state_pool": rg.MIN_STATE_POOL, "band": list(rg.BAND),
        "entry_terms": list(rg.ENTRY_TERMS), "em_iterations": rg.EM_ITERATIONS, "em_tolerance": rg.EM_TOLERANCE,
        "min_observations": rg.MIN_OBSERVATIONS, "sigma_start": list(rg.SIGMA_START), "sigma_floor": rg.SIGMA_FLOOR,
        "entry_start": rg.ENTRY_START, "stay_start": rg.STAY_START, "p_min": rg.P_MIN, "slope_ridge": rg.SLOPE_RIDGE,
        "newton_steps": rg.NEWTON_STEPS, "coefficient_limit": rg.COEFFICIENT_LIMIT, "min_scale_ratio": rg.MIN_SCALE_RATIO,
        "ridge": rg.sc.ROBUST_RIDGE, "huber_k": rg.sc.HUBER_K,
    }
    return sorted(k for k in set(declared) | set(actual) if declared.get(k) != actual.get(k))


# -- the hit sequences, with the randomised tie rule ----------------------------------------------------------------------


def hit_sequence(outcomes: Sequence[float], laws: Sequence[Sequence[float]], kind: str, rule: str) -> List[int]:
    """The exceedance sequence `kind` under `rule`. The two deterministic rules are `walk_calibration_1133`'s. The randomised rule
    (#1156) counts a tie as a hit with the probability the forecast's own distribution assigns (`coverage_tests.tie_hit_probability`);
    the forecast is the 23 quantiles of a continuous law (linear between them), so P(Y < q) = P(Y <= q) = the level and the
    probability is 0: the draws are made and recorded, and no tie is ever a hit, so it is the `above` rule."""

    if rule != "randomised":
        return w1133.hit_sequence(outcomes, laws, kind, rule)
    rng = random.Random(SEED)

    def upper(level: float) -> List[int]:
        ties = [ct.tie_hit_probability(level, level, 1.0 - level, upper=True)] * len(outcomes)
        return ct.randomised_hit_sequence(outcomes, [q[sp.GRID.index(level)] for q in laws], ties, [rng.random() for _ in outcomes])

    def lower(level: float) -> List[int]:
        ties = [ct.tie_hit_probability(level, level, level, upper=False)] * len(outcomes)
        return ct.randomised_hit_sequence([-y for y in outcomes], [-q[sp.GRID.index(level)] for q in laws], ties,
                                          [rng.random() for _ in outcomes])

    for name, level, side in w1133.TAILS:
        if kind == name:
            return upper(level) if side == "upper" else lower(level)
    lo, hi = w1133.BANDS[int(kind[4:])]
    return [max(a, b) for a, b in zip(lower(lo), upper(hi))]


def hit_tables(frame, models: Sequence[str]) -> dict:
    """`faster_scale_1153.hit_tables` with the third rule: per model, kind, rule and lead, the three coverage tests, pooled, by
    regime and by pressure-day type, and the runs of the pooled sequence."""

    out: dict = {"kinds": list(w1133.kinds_and_p()), "rules": list(RULES), "rows": {}}
    nominal = w1133.kinds_and_p()
    for h in sp.HORIZONS:
        days = list(frame.days)
        targets = [frame.target(d, h) for d in days]
        outcomes = [frame.outcome[t] for t in targets]
        members_of: Dict[str, Dict[str, List[int]]] = {}
        for split, label_of_ in (("regime", frame.regime), ("pressure_day_type", frame.day_type)):
            for i, t in enumerate(targets):
                members_of.setdefault(split, {}).setdefault(label_of_(t), []).append(i)
        for model in models:
            laws = [frame.forecasts[model][d][h] for d in days]
            for kind, p in nominal.items():
                for rule in RULES:
                    sequence = hit_sequence(outcomes, laws, kind, rule)
                    cell: dict = {}
                    if len(sequence) >= MIN_GROUP_DAYS:
                        cell["pooled"] = w1133.coverage_row(sequence, p, independence=True)
                    for split, groups in members_of.items():
                        for label, rows in sorted(groups.items()):
                            if len(rows) >= MIN_GROUP_DAYS:
                                cell[f"{split}/{label}"] = w1133.coverage_row(
                                    [sequence[i] for i in rows], p, independence=split == "regime")
                    if kind in f1153.RUN_KINDS:
                        cell["runs"] = f1153.runs_of(sequence)
                    out["rows"].setdefault(model, {}).setdefault(rule, {}).setdefault(kind, {})[f"h={h}"] = cell
    return out


# -- the frame ----------------------------------------------------------------------------------------------------------


def build_frame(panel, splits, registry, table, first: Optional[date] = None):
    """The decision days with a forecast of (a), (s3), every arm and the benchmarks, whose five targets are scored days.

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
    walk = rg.walk(panel, [d for d in candidate_days if d in b1], table, **settings)
    days = [d for d in candidate_days if d in b1 and all(d in walk.forecasts[m] for m in rg.MODEL_NAMES)]
    frame.days = days
    frame.forecasts = {"B1": {d: b1[d] for d in days}, "B1p": {d: b1p[d] for d in days}, "B2": {d: b2[d] for d in days},
                       **{m: {d: walk.forecasts[m][d] for d in days} for m in rg.MODEL_NAMES}}
    frame.all_days = days
    notes = {
        "decision_days_offered": len(candidate_days), "candidate_skipped_for_history": len(walk.skipped),
        "benchmark_missing": [d.isoformat() for d in dropped], "scored_decision_days": len(days),
        "first": days[0].isoformat(), "last": days[-1].isoformat(),
        "last_target": frame.target(days[-1], max(sp.HORIZONS)).isoformat(), "refits": len(walk.fits),
    }
    diagnostics = chain_diagnostics(walk, days, frame)
    return frame, notes, diagnostics


def chain_diagnostics(walk, days: Sequence[date], frame) -> dict:
    """What the fits did: the chains' parameters over the refits, the episode pools, the shares of days in an episode, and the
    filtered stress probability at the anchor of each scored decision day (the path the page draws)."""

    chains: Dict[str, dict] = {}
    for name in (M2, M3):
        fits = [f.params[name] for f in walk.regimes.values()]
        chains[name] = {
            "refits": len(fits), "degenerate_share": sum(1 for p in fits if p.degenerate) / len(fits),
            "sigma_calm": [p.sigma[0] for p in fits], "sigma_stress": [p.sigma[1] for p in fits],
            "stay": [p.stay for p in fits], "entry": [rg.entry_prob(p, None) for p in fits],
            "slopes": {term: [p.slopes[i] for p in fits] for i, term in enumerate(rg.ENTRY_TERMS)},
            "iterations": [p.iterations for p in fits],
        }
    pools: Dict[str, dict] = {}
    for arm in (a for a in rg.ARMS if a.kind == "episode"):
        cells = [(h, lead) for f in walk.regimes.values() for h, lead in f.episode[arm.name].items()]
        pools[arm.name] = {
            "cells": len(cells), "episode_full_pool_share": sum(1 for _, c in cells if c.episode is None) / len(cells),
            "calm_full_pool_share": sum(1 for _, c in cells if c.calm is None) / len(cells),
            "episode_origins_median": sorted(c.n_episode for _, c in cells)[len(cells) // 2],
            "calm_origins_median": sorted(c.n_calm for _, c in cells)[len(cells) // 2],
        }
    by_regime: Dict[str, dict] = {}
    for d in days:
        label = frame.regime(frame.target(d, 1))
        entry = by_regime.setdefault(label, {"days": 0, "m1_episode_k3": 0, "m1_episode_k5": 0, "stress_above_half": {M2: 0, M3: 0},
                                             "stress_sum": {M2: 0.0, M3: 0.0}})
        entry["days"] += 1
        for key in ("m1_episode_k3", "m1_episode_k5"):
            entry[key] += int(walk.detail[d][key])
        for key in (M2, M3):
            entry["stress_above_half"][key] += int(walk.detail[d][key] > 0.5)
            entry["stress_sum"][key] += walk.detail[d][key]
    path = {"dates": [d.isoformat() for d in days], **{k: [round(walk.detail[d][k], 5) for d in days] for k in (M2, M3)},
            **{k: [int(walk.detail[d][k]) for d in days] for k in ("m1_episode_k3", "m1_episode_k5")}}
    return {"chains": chains, "pools": pools, "by_regime": by_regime, "stress_path": path}


def models_of() -> Tuple[str, ...]:
    return BENCHMARKS + (A, S3) + ARMS


def candidates_of() -> Tuple[str, ...]:
    return (A, S3) + ARMS


# -- the tests, in parallel ---------------------------------------------------------------------------------------------

_STATE: Dict = {}


def _members(series, members, models):
    return [d for d in sorted(members) if all(d in series[m] for m in models)]


def _pairs_task(job):
    split, label, grain, metric, candidate, members = job
    series = _STATE["series"][(grain, metric)]
    names = list(BENCHMARKS) + [c for c in COMPARATORS if c != candidate]
    days = _members(series, members, list(names) + [candidate])
    if len(days) < MIN_GROUP_DAYS:
        return (split, label, metric, candidate), {
            n: {"undefined": "fewer than %d days with a scale" % MIN_GROUP_DAYS, "days": len(days)} for n in names}
    return (split, label, metric, candidate), s761.run_pairs(
        {n: series[n] for n in names}, series[candidate], days, seed=SEED, draws=_STATE["draws"])


def _coverage_task(job):
    split, label, grain, metric, members = job
    series = _STATE["series"][(grain, metric)]
    models = _STATE["models"]
    ordered = _members(series, members, models)
    pooled = split == "pooled"
    out = {}
    for model in models:
        values = [series[model][d] for d in ordered]
        entry = {"mean": sum(values) / len(values)}
        if pooled:
            entry["interval"] = f941.mean_interval(values, seed=SEED, reps=_STATE["reps"])
        out[model] = entry
    return (split, label, metric), out


def _block_task(job):
    """The Politis-White block of the paired loss differential of an arm against (s3), and the pooled skill at that block."""

    split, label, grain, metric, candidate, members = job
    series = _STATE["series"][(grain, metric)]
    ordered = _members(series, members, [S3, candidate])
    d = [series[S3][x] - series[candidate][x] for x in ordered]
    try:
        block = b949.politis_white(d)
    except ValueError:
        return (split, label, metric, candidate), None
    entry = {"block": block, "days": len(ordered)}
    if split == "pooled":
        at = max(1, round(block))
        test = sp.paired_tests([({x: series[S3][x] for x in ordered}, {x: series[candidate][x] for x in ordered})], seed=SEED,
                               draws=_STATE["draws"], block_length=float(at))[0]
        entry["at_block"] = at
        entry["row"] = s761.paired_row(test)
    return (split, label, metric, candidate), entry


def _dispatch(job):
    kind, payload = job
    return kind, {"pairs": _pairs_task, "coverage": _coverage_task, "block": _block_task}[kind](payload)


def run_jobs(jobs, workers: int):
    context = multiprocessing.get_context("fork")
    with context.Pool(workers) as pool:
        return pool.map(_dispatch, jobs, chunksize=1)


# -- the kill rule, against (s3) -----------------------------------------------------------------------------------------


def kill_assessment(hits: Mapping) -> dict:
    """The declared kill rule against (s3): no arm moves the pooled independence p of the 90% band's misses off 0.000 at any lead
    (`faster_scale_1153.kill_assessment`, over every rule in `hits`), and no arm cuts the mean run (closed rule, pooled over the
    leads) by more than `RUN_CUT` of (s3)'s. `met` is both; `arms_cut_runs` are the arms that cut it by more."""

    out = f1153.kill_assessment(hits, (S3,) + ARMS, S3)
    base = out["base_mean_run"]
    cuts, over = {}, []
    for m in ARMS:
        mean = out["models"][m]["runs"]["above"]["mean"]
        cuts[m] = None if mean is None or not base else 1.0 - mean / base
        if mean is not None and base and mean < (1.0 - RUN_CUT) * base:
            over.append(m)
    out.update({"run_cut": cuts, "run_cut_threshold": RUN_CUT, "arms_cut_runs": over, "met": not out["arms_off_zero"] and not over})
    return out


# -- the report ---------------------------------------------------------------------------------------------------------


def score(args) -> int:
    declaration = committed_declaration()
    differ = constants_agree(declaration)
    if differ:
        raise SystemExit(f"the declared constants differ from spread_mr_regime's: {', '.join(differ)}")
    panel_path = Path(args.panel)
    panel = load_daily_panel(panel_path)
    splits = load_split_declaration(s686.SPLITS)
    registry = json.loads(s686.SOURCES.read_text(encoding="utf-8"))
    table = cal.TermTable(panel, announced_iorb.load_announcements(IORB_TABLE), decision_time=DECISION_TIME)
    frame, notes, diagnostics = build_frame(panel, splits, registry, table, args.first)
    models, candidates = models_of(), candidates_of()
    cells = f1153.all_cells(frame, models)
    groups = f941.groups_of(frame)
    series: Dict[Tuple[str, str], Dict[str, Dict[date, float]]] = {}
    for _split, _label, grain, _members_ in groups:
        for metric in METRICS + COVERAGE_METRICS:
            if (grain, metric) not in series:
                series[(grain, metric)] = {m: f941.series_of(frame, cells[metric][m], grain) for m in models}
    _STATE.update(series=series, draws=args.draws, reps=args.reps, models=models)
    jobs, skipped = [], {}
    for split, label, grain, members in groups:
        if len(members) < MIN_GROUP_DAYS:
            skipped[f"{split}/{label}"] = len(members)
            continue
        for metric in METRICS:
            if split == "lead" and metric == "scaled_grid_crps":
                continue
            for candidate in candidates:
                jobs.append(("pairs", (split, label, grain, metric, candidate, tuple(members))))
                if candidate in ARMS and split in ("pooled", "regime") and metric != "scaled_grid_crps":
                    jobs.append(("block", (split, label, grain, metric, candidate, tuple(members))))
        for metric in COVERAGE_METRICS:
            jobs.append(("coverage", (split, label, grain, metric, tuple(members))))
    done = run_jobs(jobs, args.workers)
    by_key = {(s_, l_): (g, m) for s_, l_, g, m in groups}
    result: dict = {
        "issue": 1182, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": panel_sha256(panel_path),
        "subset_from": None if args.first is None else args.first.isoformat(),
        "label": "development, not a verdict", "seed": SEED, "draws": args.draws, "reps": args.reps,
        "notes": notes, "models": list(models), "base": S3, "comparators": list(COMPARATORS), "arms": list(ARMS),
        "diagnostics": diagnostics, "episodes": declaration["figure"]["episodes"], "groups": {}, "skipped_groups": skipped, "politis_white": {},
        "randomised_tie_rule": ("implemented (coverage_tests.randomised_hit_sequence, draws seeded with %d); the forecast is 23 quantiles "
                                "of a continuous law, so the tie probability is 0 at every quantile and the rule coincides with `above`" % SEED),
    }
    for kind, (ident, payload) in done:
        split, label, metric = ident[:3]
        if kind == "block":
            result["politis_white"].setdefault(split, {}).setdefault(label, {}).setdefault(metric, {})[ident[3]] = payload
            continue
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(by_key[(split, label)][1])})
        if kind == "pairs":
            entry.setdefault(metric, {"means": {}, "vs": {}})["vs"][ident[3]] = payload
        else:
            entry[metric] = payload
    for split, labels in result["groups"].items():
        for label, entry in labels.items():
            grain, members = by_key[(split, label)]
            for metric in METRICS:
                if split == "lead" and metric == "scaled_grid_crps":
                    continue
                ser = series[(grain, metric)]
                days = _members(ser, members, models)
                entry[metric]["means"] = {m: sum(ser[m][d] for d in days) / len(days) for m in models} if days else {}
                entry[metric]["days"] = len(days)
    result["hits"] = hit_tables(frame, models)
    result["kill"] = kill_assessment(result["hits"])
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page -----------------------------------------------------------------------------------------------------------


def skill(row: Optional[dict]) -> str:
    return "n/a" if row is None else s761.skill_text(row)


def bound(row: Optional[dict]) -> str:
    """The studentized interval of mean(d) of one row."""

    return "n/a" if row is None else s761.diff_text(row)


def reading(row: Optional[dict]) -> str:
    """The reading on the mean-d bound (#1009): gain, loss or undecided."""

    if row is None or "undefined" in row:
        return "undecided"
    lo, hi = row["difference_interval"]
    return "gain" if lo > 0.0 else "loss" if hi < 0.0 else "undecided"


def _ordered(split: str, labels) -> List[str]:
    return f941._ordered(split, labels)


HEADER = ["| | mean | vs B1: skill [90%] | vs B1': skill [90%] | vs B2: skill [90%] | vs (a): skill [90%]; mean d [90%] | "
          "vs (s3): skill [90%]; mean d [90%]; reading |", "|---|---|---|---|---|---|---|"]


def _score_rows(cell: dict, r: dict) -> List[str]:
    means = cell["means"]
    if not means:
        return ["| (no day with a scale) | | | | | | |"]
    out = [f"| {label_of(m)} | {means[m]:.3f} | | | | | |" for m in BENCHMARKS]
    for m in candidates_of():
        vs = cell["vs"][m]
        cols = []
        for c in COMPARATORS:
            if c == m:
                cols.append("")
            else:
                cols.append(f"{skill(vs[c])}; {bound(vs[c])}" + ("; " + reading(vs[c]) if c == S3 else ""))
        out.append(f"| {label_of(m)} | {means[m]:.3f} | {skill(vs['B1'])} | {skill(vs['B1p'])} | {skill(vs['B2'])} | "
                   f"{cols[1]} | {cols[0]} |")
    return out


def _fmt_p(e: Optional[dict], key: str) -> str:
    return "n/a" if not e or not e.get(key) else f"{e[key]['p_value']:.3f}"


def clustering_section(r: dict) -> List[str]:
    hits, models = r["hits"], list(r["comparators"]) + r["arms"]
    out = ["## The clustering of the 90% band's misses (the headline of this fix)", "",
           "Per lead, pooled over the scored days: the miss rate (nominal 0.10), then Christoffersen's independence p and the conditional "
           "coverage p. A p of 0.000 is below 0.0005. Reporting only: no p-value is a gate.", ""]
    for rule in hits["rules"]:
        words = {"above": "closed band, a miss is `y` outside `[q05, q95]`",
                 "at_or_above": "open band, a miss includes `y` equal to a bound",
                 "randomised": "a tie is a hit with the forecast's own tie probability, 0 here: the same sequence as `above`"}[rule]
        out += [f"Rule `{rule}` ({words}); rate (independence p / conditional coverage p):", "",
                "| | " + " | ".join(f"h={h}" for h in sp.HORIZONS) + " |", "|---|" + "---|" * len(sp.HORIZONS)]
        for m in models:
            cells = []
            for h in sp.HORIZONS:
                e = hits["rows"][m][rule]["band90"].get(f"h={h}", {}).get("pooled")
                cells.append("n/a" if e is None else f"{e['rate']:.3f} ({_fmt_p(e, 'independence')} / {_fmt_p(e, 'conditional')})")
            out.append(f"| {label_of(m)} | " + " | ".join(cells) + " |")
        out.append("")
    out += [f"The randomised tie rule of #1156: {r['randomised_tie_rule']}.", "",
            "Independence p of the 90% band's misses within a regime (consecutive days of the regime), by lead, closed rule (`above`):", ""]
    for regime in REGIME_ORDER:
        out += [f"**{regime}**", "", "| | " + " | ".join(f"h={h}" for h in sp.HORIZONS) + " |", "|---|" + "---|" * len(sp.HORIZONS)]
        for m in models:
            out.append(f"| {label_of(m)} | " + " | ".join(
                _fmt_p(hits["rows"][m]["above"]["band90"].get(f"h={h}", {}).get(f"regime/{regime}"), "independence")
                for h in sp.HORIZONS) + " |")
        out.append("")
    out += ["### Miss runs", "",
            "A run is a block of consecutive misses in a lead's sequence of consecutive decision days. Pooled over the five leads: the number "
            "of runs, the mean run length (misses per run; about 1.11 for independent misses at a 10% rate) and the longest run, for the "
            "90% band and for q95 (above its quantile).", ""]
    for rule in hits["rules"]:
        out += [f"Rule `{rule}`:", "", "| | 90% band: runs | mean | longest | q95: runs | mean | longest |", "|---|---|---|---|---|---|---|"]
        for m in models:
            band = f1153.pooled_runs([hits["rows"][m][rule]["band90"][f"h={h}"]["runs"] for h in sp.HORIZONS])
            tail = f1153.pooled_runs([hits["rows"][m][rule]["q95"][f"h={h}"]["runs"] for h in sp.HORIZONS])
            f = lambda x: "n/a" if x["mean"] is None else f"{x['mean']:.3f}"  # noqa: E731
            out.append(f"| {label_of(m)} | {band['runs']} | {f(band)} | {band['longest']} | {tail['runs']} | {f(tail)} | {tail['longest']} |")
        out.append("")
    return out


def kill_section(r: dict) -> List[str]:
    k = r["kill"]
    out = ["## Against the kill rule", "",
           "The kill rule (the issue's, read in the declaration): if no arm moves independence off p = 0.000 at any lead, and no arm cuts the "
           f"mean run by more than {k['run_cut_threshold']:.0%}, the clustering is not a two-state phenomenon either, and the recommendation is to "
           f"report it as a known limit in the use limitation. 'Off 0.000' is a pooled independence p of the 90% band of at least "
           f"{k['off_zero_threshold']}, at any lead, under any hit rule; the cut is of the mean run (closed rule, pooled over leads) against "
           f"(s3)'s ({k['base_mean_run']:.3f}).", "",
           "| model | leads off 0.000, `above` | leads off 0.000, `at_or_above` | mean run, `above` (longest) | mean run, `at_or_above` (longest) | cut of the mean run |",
           "|---|---|---|---|---|---|"]
    for m in [S3] + r["arms"]:
        e = k["models"][m]
        fm = lambda x: "n/a" if x["mean"] is None else f"{x['mean']:.3f} ({x['longest']})"  # noqa: E731
        leads = {rule: (", ".join(f"h={h}" for h in e["off_zero_leads"][rule]) or "none") for rule in e["off_zero_leads"]}
        cut_ = k["run_cut"].get(m)
        out.append(f"| {label_of(m)} | {leads['above']} | {leads['at_or_above']} | {fm(e['runs']['above'])} | {fm(e['runs']['at_or_above'])} | "
                   f"{'' if m == S3 else 'n/a' if cut_ is None else f'{cut_:+.1%}'} |")
    out += ["", f"Arms with a lead off 0.000: {', '.join(label_of(m) for m in k['arms_off_zero']) or 'none'}. "
            f"Arms that cut the mean run by more than {k['run_cut_threshold']:.0%}: {', '.join(label_of(m) for m in k['arms_cut_runs']) or 'none'}. "
            f"**The kill rule is {'met' if k['met'] else 'not met'}.**", ""]
    if k["met"]:
        out += ["No arm moves independence off 0.000 and none cuts the mean run by more than the threshold: the clustering of the misses is not a "
                "two-state phenomenon either, on this evidence. The issue's recommendation follows: report it as a known limit in the use "
                "limitation, and do not try another arm. Whether to do so is Eleonora's decision.", ""]
    return out


def adoption_section(r: dict) -> List[str]:
    """The facts the adoption rule reads, one row per arm; the rule's judgement ('clearly towards 1.1', 'beyond the interval') is hers."""

    k = r["kill"]
    out = ["## The facts behind the adoption rule (her decision)", "",
           "The issue: an arm replaces (s3) only if independence is no longer rejected at the leads, or the mean miss run falls clearly "
           "towards 1.1, without losing CRPS beyond the interval. This page states the facts and decides nothing.", "",
           "| arm | leads off 0.000 (`above`) | mean run (`above`) | cut against (s3) | pooled grid CRPS vs (s3), mean-d bound | regimes read as a loss | day types read as a loss |",
           "|---|---|---|---|---|---|---|"]
    for m in r["arms"]:
        e = k["models"][m]
        leads = ", ".join(f"h={h}" for h in e["off_zero_leads"]["above"]) or "none"
        mean = e["runs"]["above"]["mean"]
        loss = {}
        for split in ("regime", "pressure_day_type"):
            loss[split] = [label for label in _ordered(split, r["groups"].get(split, {}))
                           if reading(r["groups"][split][label]["grid_crps"]["vs"][m][S3]) == "loss"]
        cut_ = k["run_cut"].get(m)
        out.append(f"| {label_of(m)} | {leads} | {'n/a' if mean is None else f'{mean:.3f}'} | {'n/a' if cut_ is None else f'{cut_:+.1%}'} | "
                   f"{reading(r['groups']['pooled']['all decision days']['grid_crps']['vs'][m][S3])} | "
                   f"{', '.join(loss['regime']) or 'none'} | {', '.join(loss['pressure_day_type']) or 'none'} |")
    out.append("")
    return out


def diagnostics_section(r: dict) -> List[str]:
    d = r["diagnostics"]
    med = lambda v: sorted(v)[len(v) // 2] if v else float("nan")  # noqa: E731
    out = ["## What the fits did", "",
           "The two-state chains, fitted by EM on each refit's training window (about 90 refits): the median over the refits of the calm and "
           "stress scales of the one-step residual (the stress scale over the calm one beside), the stay probability in stress "
           "and the implied mean spell, the entry probability from calm with no calendar flag, and the share of refits whose stress scale is "
           f"not {rg.MIN_SCALE_RATIO:g} times the calm one (degenerate: that fit is (s3)).", "",
           "| chain | refits | calm scale | stress scale | ratio | stay in stress | mean stress spell (rows) | entry from calm | degenerate |",
           "|---|---|---|---|---|---|---|---|---|"]
    for name in (M2, M3):
        c = d["chains"][name]
        stay = med(c["stay"])
        out.append(f"| {label_of(name)} | {c['refits']} | {med(c['sigma_calm']):.3f} | {med(c['sigma_stress']):.3f} | "
                   f"{med(c['sigma_stress']) / med(c['sigma_calm']):.2f} | {stay:.3f} | {1.0 / (1.0 - stay):.1f} | {med(c['entry']):.3f} | "
                   f"{c['degenerate_share']:.2f} |")
    c = d["chains"][M3]
    out += ["", "The entry slopes of (m3) (log-odds of entering stress on a day with the flag, over a day without): the median over the refits "
            "and the share of refits with a positive slope.", "", "| calendar type | median slope | share positive |", "|---|---|---|"]
    for term in rg.ENTRY_TERMS:
        v = c["slopes"][term]
        out.append(f"| {term} | {med(v):+.3f} | {sum(1 for x in v if x > 0.0) / len(v):.2f} |")
    out += ["", "The pools of (m1): over the refit-by-lead cells, the share where a state had fewer than "
            f"{rg.MIN_STATE_POOL} origins and the full pool was used, and the median number of origins in each state.", "",
            "| arm | cells | episode pool: full-pool share | calm pool: full-pool share | median origins in an episode | median calm origins |",
            "|---|---|---|---|---|---|"]
    for arm, e in d["pools"].items():
        out.append(f"| {label_of(arm)} | {e['cells']} | {e['episode_full_pool_share']:.2f} | {e['calm_full_pool_share']:.2f} | "
                   f"{e['episode_origins_median']} | {e['calm_origins_median']} |")
    out += ["", "The state each arm read at the anchor on the scored decision days, by regime of the lead-1 target: the share of days in an "
            "episode ((m1)), and the share with a filtered stress probability above one half and the mean probability ((m2), (m3)).", "",
            "| regime | days | episode, 3 rows | episode, 5 rows | (m2) above 0.5 | (m2) mean | (m3) above 0.5 | (m3) mean |",
            "|---|---|---|---|---|---|---|---|"]
    for regime in REGIME_ORDER:
        e = d["by_regime"].get(regime)
        if not e:
            continue
        n = e["days"]
        out.append(f"| {regime} | {n} | {e['m1_episode_k3'] / n:.2f} | {e['m1_episode_k5'] / n:.2f} | {e['stress_above_half'][M2] / n:.2f} | "
                   f"{e['stress_sum'][M2] / n:.3f} | {e['stress_above_half'][M3] / n:.2f} | {e['stress_sum'][M3] / n:.3f} |")
    out.append("")
    return out


def stress_section(r: dict) -> List[str]:
    return ["## The filtered stress probability", "",
            "The probability of the stress state at the anchor (the last public row) of each scored decision day, from the Hamilton filter "
            "of the refit in force, for (m2) and (m3). The drawing stops at the last scored decision day: days after 2025-12-31 are not "
            "read by this study. The episodes are marked: September 2019, March 2020 (the event windows of `metadata/events.json`) and the "
            "2025 episodes the declaration lists.", "",
            "![Filtered stress probability of (m2) and (m3) over the scored decision days, with the episodes marked]"
            "(regime-spells-1182/stress_probability.svg)", ""]


def stress_figure(r: dict, episodes: Sequence[dict]) -> str:
    """The filtered stress probability of (m2) and (m3) as one SVG, a panel each, with the declared episodes shaded."""

    path = r["diagnostics"]["stress_path"]
    dates = [date.fromisoformat(x) for x in path["dates"]]
    first, last = dates[0], dates[-1]
    span = max(1, (last - first).days)
    width, left, right, top, panel, gap, bottom = 920, 56, 16, 28, 150, 46, 40
    height = top + 2 * panel + gap + bottom
    esc = xml.sax.saxutils.escape
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" '
           f'aria-label="Filtered stress probability of (m2) and (m3) from {first} to {last}" font-family="sans-serif" font-size="11">']

    def x_of(day: date) -> float:
        return left + (width - left - right) * (day - first).days / span

    for index, (name, color) in enumerate(((M2, "#2b6cb0"), (M3, "#c05621"))):
        y0 = top + index * (panel + gap)

        def y_of(p: float, y0=y0) -> float:
            return y0 + panel * (1.0 - p)

        out.append(f'<text x="{left}" y="{y0 - 10}" fill="#6b7280" font-weight="bold">{esc(label_of(name))}</text>')
        for tick in (0.0, 0.5, 1.0):
            out.append(f'<line x1="{left}" x2="{width - right}" y1="{y_of(tick):.1f}" y2="{y_of(tick):.1f}" stroke="#9ca3af" stroke-opacity="0.45"/>')
            out.append(f'<text x="{left - 6}" y="{y_of(tick) + 4:.1f}" text-anchor="end" fill="#6b7280">{tick:g}</text>')
        for ep in episodes:
            a, b = date.fromisoformat(ep["start"]), date.fromisoformat(ep["end"])
            if b < first or a > last:
                continue
            x1, x2 = x_of(max(a, first)), x_of(min(b, last))
            out.append(f'<rect x="{x1:.1f}" y="{y0}" width="{max(2.0, x2 - x1):.1f}" height="{panel}" fill="#9ca3af" fill-opacity="0.35"/>')
            if index == 0:
                out.append(f'<text x="{(x1 + x2) / 2:.1f}" y="{y0 + 12}" text-anchor="middle" fill="#6b7280">{esc(ep["label"])}</text>')
        points = " ".join(f"{x_of(d):.1f},{y_of(p):.1f}" for d, p in zip(dates, path[name]))
        out.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="1"/>')
    axis = top + 2 * panel + gap - 8
    for year in range(first.year, last.year + 1):
        day = date(year, 1, 1)
        if first <= day <= last:
            out.append(f'<text x="{x_of(day):.1f}" y="{axis + 22}" text-anchor="middle" fill="#6b7280">{year}</text>')
            out.append(f'<line x1="{x_of(day):.1f}" x2="{x_of(day):.1f}" y1="{axis}" y2="{axis + 5}" stroke="#9ca3af"/>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def coverage_section(r: dict) -> List[str]:
    out = ["## Band coverage", "",
           "Share of (decision day, lead) cells whose outcome is inside the band, with its 90% interval (pooled). Closed: `q_lo <= y <= q_hi` "
           "(the hit rule `y > q`); open: `q_lo < y < q_hi` (the rule `y >= q`). Nominal 0.50, 0.80, 0.90, 0.98. The hit rule is Eleonora's "
           "open question (#993) and both are reported.", ""]
    groups = [("pooled", "all decision days")] + [("lead", f"h={h}") for h in sp.HORIZONS] + [
        (s_, l) for s_ in ("regime", "pressure_day_type") for l in _ordered(s_, r["groups"].get(s_, {}))]
    for c in BANDS:
        for kind in ("closed", "open"):
            metric = f"cover{c}_{kind}"
            out += [f"**{c}% band, {kind}**", "", "| | " + " | ".join(l for _, l in groups) + " |", "|---|" + "---|" * len(groups)]
            for m in r["models"]:
                cells = []
                for split, label in groups:
                    e = r["groups"][split][label][metric][m]
                    cells.append(f"{e['mean']:.3f}" + (f" [{e['interval'][0]:.3f}, {e['interval'][1]:.3f}]" if "interval" in e else ""))
                out.append(f"| {label_of(m)} | " + " | ".join(cells) + " |")
            out.append("")
    return out


def hit_section(r: dict) -> List[str]:
    hits = r["hits"]
    models = list(r["comparators"]) + r["arms"]
    out = ["## Exceedances and band misses, by lead, under both hit rules", "",
           "Each cell is the rate (nominal in the heading) with the p-values of Kupiec's unconditional coverage test, Christoffersen's "
           "independence test and his conditional coverage test (`repo_model.coverage_tests`). Upper tails: the outcome above q95 / q99; "
           "lower tails: below q05 / q01; a band miss: outside the band. Reporting only: no p-value is a gate. By regime and "
           "pressure-day type, the five leads together with Kupiec's p; the independence tests per regime and lead are in `result.json`.", ""]
    nominal = w1133.kinds_and_p()
    for rule in ct.HIT_RULES:  # the randomised rule is the `above` sequence here (see the clustering section) and is in result.json
        words = "strictly beyond the quantile / outside the closed band" if rule == "above" else "at or beyond the quantile / outside the open band"
        for kind in hits["kinds"]:
            p = nominal[kind]
            out += [f"### {kind} (nominal {p:.2f}), rule `{rule}` ({words})", "",
                    "Pooled; rate (Kupiec p / independence p / conditional coverage p):", "",
                    "| | " + " | ".join(f"h={h}" for h in sp.HORIZONS) + " |", "|---|" + "---|" * len(sp.HORIZONS)]
            for m in models:
                cells = []
                for h in sp.HORIZONS:
                    e = hits["rows"][m][rule][kind].get(f"h={h}", {}).get("pooled")
                    cells.append("n/a" if e is None else
                                 f"{e['rate']:.3f} ({e['kupiec']['p_value']:.3f} / {e['independence']['p_value']:.3f} / {e['conditional']['p_value']:.3f})")
                out.append(f"| {label_of(m)} | " + " | ".join(cells) + " |")
            out.append("")
            for split, order in (("regime", REGIME_ORDER), ("pressure_day_type", DAYTYPE_ORDER)):
                out += [f"By {SPLIT_TITLES[split]}: rate (Kupiec p).", "",
                        "| | " + " | ".join(order) + " |", "|---|" + "---|" * len(order)]
                for m in models:
                    cells = []
                    for label in order:
                        total = hit_count = 0
                        for h in sp.HORIZONS:
                            e = hits["rows"][m][rule][kind].get(f"h={h}", {}).get(f"{split}/{label}")
                            if e is not None:
                                total, hit_count = total + e["n"], hit_count + e["hits"]
                        cells.append("n/a" if not total else
                                     f"{hit_count / total:.3f} ({ct.kupiec([1] * hit_count + [0] * (total - hit_count), p).p_value:.3f})")
                    out.append(f"| {label_of(m)} | " + " | ".join(cells) + " |")
                out.append("")
    return out


def politis_white_section(r: dict) -> List[str]:
    out = ["## The Politis-White block beside the block of 10", "",
           "The automatic block length (Politis and White 2004, with the correction of Patton, Politis and White 2009, "
           "`scripts/block_length_949.py`) of the paired loss differential `S(s3) - S(arm)`, in days, with the pooled skill over (s3) at that "
           "block. Reported, never substituted for 10.", ""]
    columns = ["pooled"] + [l for l in REGIME_ORDER if l in r["politis_white"].get("regime", {})]
    for metric in ("grid_crps", "upper_tail_twcrps"):
        out += [f"{METRIC_TITLES[metric]}:", "", "| | " + " | ".join(columns) + " | pooled skill vs (s3) at that block |", "|---|" + "---|" * (len(columns) + 1)]
        for m in r["arms"]:
            cells, at = [], ""
            for col in columns:
                split, label = ("pooled", "all decision days") if col == "pooled" else ("regime", col)
                e = r["politis_white"].get(split, {}).get(label, {}).get(metric, {}).get(m)
                cells.append("n/a" if not e else f"{e['block']:.1f}")
                if col == "pooled" and e and "row" in e:
                    at = f"block {e['at_block']}: {skill(e['row'])}"
            out.append(f"| {label_of(m)} | " + " | ".join(cells) + f" | {at} |")
        out.append("")
    return out


def render(r: dict) -> str:
    n = r["notes"]
    pooled = r["groups"]["pooled"]["all decision days"]
    out = [
        "# The H5 candidate with calm and stress spells (#1182)", "",
        f"**Hypothesis and step:** H5 (primary goal), step 3 (fix), the clustered misses of the scaled mean reversion, after #1153 and #1175 "
        f"(Eleonora, 24 October 2026: \"queue it\"). **{r['label'].capitalize()}**: development days to {n['last_target']}, no verdict (scoring "
        "protocol v1, #640). Any change to the candidate is Eleonora's decision. Generated by `scripts/regime_spells_1182.py page` from "
        f"`docs/research/regime-spells-1182/result.json`, not edited by hand; declared in `{r['declaration']}` before any score.", "",
        f"Panel digest `{r['panel_sha256'][:8]}…`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business "
        f"days, {r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval. Skill is `mean(d) / mean(S(comparator))` with "
        "`d = S(comparator) - S(candidate)`, positive favours the candidate; beside it the studentized interval of mean(d) itself (the "
        "mean-d bound of #1009), on which the reading is made: a gain when the interval is above zero, a loss when below, otherwise "
        f"undecided. {LENS_C} Coverage intervals are 90% stationary-bootstrap percentile intervals ({r['reps']:,} resamples), pooled. "
        f"Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); every model is scored on the same days.", "",
        "**What this is.** The base is (s3) of #1145: #941's scaled mean reversion with state-scaled calendar terms, a Huber fit and ridge "
        "5, the calendar read at the target day on direct pairs. The misses of its bands come in runs (Christoffersen independence p = 0.000 at "
        "every lead, mean run about 2.0 against 1.1 if independent), and a faster, miss-fed or dispersion-scaled band did not fix it (#1153, "
        "#1175). These arms ask whether the market moves between calm and stress spells that one law cannot represent: (m1) an observable "
        "episode state (a miss of (s3)'s own 90% band within the last 3 or 5 rows), whose own pool and scale the law takes; (m2) a two-state "
        "Markov-switching scale, fitted by EM on the training window and filtered by Hamilton's filter on public residuals only; (m3) (m2) with "
        "the entry to stress a logistic function of the calendar type of the day entered, read at that day. The terms, the centre and the "
        "refit cadence are (s3)'s. (a) is #941's variant, beside. The base was chosen after seeing 2018-2025. `gbm_funding` is not compared "
        "(its walks are a long run for Eleonora's Mac and the directive does not ask for it).", ""]
    out += kill_section(r)
    out += adoption_section(r)
    out += clustering_section(r)
    out += stress_section(r)
    for metric in METRICS:
        out += [f"## {METRIC_TITLES[metric]}, mean over leads 1 to 5, pooled", ""] + HEADER + _score_rows(pooled[metric], r) + [""]
    out += ["## Skill of each arm over (s3), by lead [90%]; mean d [90%]", ""]
    for metric in ("grid_crps", "upper_tail_twcrps"):
        out += [f"{METRIC_TITLES[metric]}:", "", "| | " + " | ".join(f"h={h}" for h in sp.HORIZONS) + " |", "|---|" + "---|" * len(sp.HORIZONS)]
        for m in r["arms"]:
            out.append(f"| {label_of(m)} | " + " | ".join(
                skill(r["groups"]["lead"][f"h={h}"][metric]["vs"][m][S3]) + "; " + bound(r["groups"]["lead"][f"h={h}"][metric]["vs"][m][S3])
                for h in sp.HORIZONS) + " |")
        out.append("")
    for split in ("regime", "pressure_day_type"):
        labels = _ordered(split, r["groups"].get(split, {}))
        for metric in METRICS:
            out += [f"## {METRIC_TITLES[metric]} by {SPLIT_TITLES[split]}", ""]
            for label in labels:
                cell = r["groups"][split][label][metric]
                out += [f"**{label}** ({cell.get('days', 0)} days)", ""] + HEADER + _score_rows(cell, r) + [""]
    if r["skipped_groups"]:
        out += ["Groups with fewer than %d days are listed and not tested: %s." % (
            MIN_GROUP_DAYS, ", ".join(f"{k} ({v})" for k, v in sorted(r["skipped_groups"].items()))), ""]
    out += ["## Reading under the declared rule", "",
            "On the grid CRPS against (s3), the mean-d bound: a gain is a studentized interval of mean(d) above zero, a loss below zero, "
            "otherwise undecided. The skill interval is shown beside and not read.", ""]
    for m in r["arms"]:
        parts = []
        for split in ("pooled", "regime", "pressure_day_type"):
            for label in _ordered(split, r["groups"].get(split, {})):
                parts.append(f"{label}: {reading(r['groups'][split][label]['grid_crps']['vs'][m][S3])}")
        out.append(f"- **{label_of(m)}**: " + "; ".join(parts) + ".")
    out.append("")
    out += diagnostics_section(r)
    out += coverage_section(r)
    out += hit_section(r)
    out += politis_white_section(r)
    return "\n".join(out) + "\n"


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    figure = Path(args.score).parent / "stress_probability.svg"
    figure.write_text(stress_figure(r, r["episodes"]), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk (a), (s3) and the arms and score them")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--reps", type=int, default=2000, help="bootstrap resamples of a coverage interval")
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
