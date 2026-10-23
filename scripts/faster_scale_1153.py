"""A faster-reacting scale against the clustered misses of the scaled mean reversion, scored (#1153; H5 step 3, fix).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.
Every choice is in `metadata/faster_scale_1153.json`, which this script refuses to read unless it is committed and unchanged.
The base (a) is #941's `spread_mr_fhs_mad20_f0.5`, arm (a) of #1115 (`repo_model.spread_mr_fhs`); the arms are
`repo_model.spread_mr_scale` (v1 a faster MAD and a blend, v2 an EWMA scale and an asymmetric one, v3 miss feedback, v4 the best of
those with a factor read at the target day's calendar type). They are scored with the scorer of scoring protocol v1
(`repo_model.scoring_protocol`) against (a), B1 with B1' beside it and B2 (`repo_model.protocol_benchmarks`,
`repo_model.b1_calendar`), on the studentized stationary bootstrap of ruling 1 (#739), with the Politis-White block beside the block of
10 and the scaled score of #967 beside the raw one. Scored decision days are those whose five targets are on or before 2025-12-31;
no later day is read and no locked day is scored (`docs/decisions/lockbox.md`).

The headline of this fix is the clustering of the misses: the coverage of the 50, 80, 90 and 98% bands, the exceedances of q05, q95, q01
and q99, Kupiec's test, Christoffersen's independence and conditional coverage tests per lead under both hit rules (pooled and by regime),
and the length of the runs of misses (`repo_model.coverage_tests`). The hit rule is Eleonora's open question (#993): both are reported.

The walks are arithmetic on the panel. `gbm_funding` is compared only when its five walks are supplied (`--walks`, a long run for
Eleonora's Mac, `.claude/skills/long-run`). Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    # optional: WALKS/gbm_funding_h<h>.json (scripts/spread_distribution_634.py walk), all five leads
    PYTHONPATH=src python3 scripts/faster_scale_1153.py score --panel PUB.csv [--walks WALKS] \\
        --output docs/research/faster-scale-1153/result.json
    PYTHONPATH=src python3 scripts/faster_scale_1153.py page \\
        --score docs/research/faster-scale-1153/result.json --output docs/research/faster-scale-1153-result.md

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
    loaded = sys.modules.get(name)
    if loaded is not None and Path(getattr(loaded, "__file__", "")) == REPO / "scripts" / f"{name}.py":
        return loaded  # a worker pool pickles functions by module name: keep the object another loader registered
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


from repo_model import announced_iorb, b1_calendar as b1c  # noqa: E402
from repo_model import coverage_tests as ct  # noqa: E402
from repo_model import protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model import spread_mr_calendar as cal, spread_mr_scale as sc  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.splits import SplitError  # noqa: E402

s686 = _load("spread_mean_reversion_686")
s761 = _load("spread_mr_variants_761")
s967 = _load("scaled_score_967")
f941 = _load("fhs_scale_941")
b949 = _load("block_length_949")
w1133 = _load("walk_calibration_1133")
c1115 = _load("calendar_mr_1115")

DECLARATION = REPO / "metadata" / "faster_scale_1153.json"
IORB_TABLE = REPO / "tests" / "fixtures" / "snapshots" / "fed-iorb-announcements" / "iorb_changes.csv"
SEED = 1153
LAST_DAY = s686.LAST_DAY
DECISION_TIME = s686.DECISION_TIME
MIN_GROUP_DAYS = s686.MIN_GROUP_DAYS
BASE = "spread_mr_fhs_mad20_f0.5"
GBM = "gbm_funding"
BENCHMARKS: Tuple[str, ...] = ("B1", "B1p", "B2")
EARLY_ARMS: Tuple[str, ...] = tuple(arm.name for arm in sc.ARMS)
METRICS: Tuple[str, ...] = ("grid_crps", "upper_tail_twcrps", "scaled_grid_crps")
BANDS = w1133.BANDS
COVERAGE_METRICS: Tuple[str, ...] = w1133.COVERAGE_METRICS
TAILS = w1133.TAILS
REGIME_ORDER = w1133.REGIME_ORDER
DAYTYPE_ORDER = w1133.DAYTYPE_ORDER
SPLIT_TITLES = w1133.SPLIT_TITLES
METRIC_TITLES = w1133.METRIC_TITLES
#: Per lead, the sequences whose runs are counted.
RUN_KINDS: Tuple[str, ...] = ("band90", "q95")
#: A p-value that prints as 0.000 at three places is below this.
OFF_ZERO = 0.0005
#: The eligibility of an arm for v4: its pooled mean grid CRPS at most this far above (a)'s.
ELIGIBLE_SLACK = 1.01
LABELS: Dict[str, str] = {
    "B1": "B1", "B1p": "B1' (#960)", "B2": "B2", GBM: "gbm_funding (#634)", BASE: "(a) base (#941 mad20)",
    "v1_mad5": "v1 MAD 5 days", "v1_mad10": "v1 MAD 10 days", "v1_blend5_20": "v1 blend of 5- and 20-day MAD",
    "v2_ewma_hl3": "v2 EWMA half-life 3", "v2_ewma_hl5": "v2 EWMA half-life 5", "v2_ewma_hl10": "v2 EWMA half-life 10",
    "v2_ewma_hl5_asym": "v2 EWMA half-life 5, asymmetric", "v3_miss": "v3 miss feedback",
}


def label_of(model: str) -> str:
    if model in LABELS:
        return LABELS[model]
    if model.startswith("v4_"):
        return f"v4 {LABELS.get(model[3:-4], model[3:-4])} + calendar type"
    return model


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


# -- the runs -----------------------------------------------------------------------------------------------------------


def runs_of(sequence: Sequence[int]) -> Dict[str, int]:
    """The runs of consecutive hits in a 0/1 sequence: how many, how many hits, the longest."""

    runs = hits = longest = current = 0
    for h in sequence:
        if h:
            hits += 1
            current += 1
            if current == 1:
                runs += 1
            longest = max(longest, current)
        else:
            current = 0
    return {"runs": runs, "hits": hits, "longest": longest}


def pooled_runs(per_lead: Sequence[Mapping[str, int]]) -> Dict[str, float]:
    """The five leads' runs together: total runs and hits, the mean run (`None` with no run) and the longest."""

    runs = sum(r["runs"] for r in per_lead)
    hits = sum(r["hits"] for r in per_lead)
    return {"runs": runs, "hits": hits, "mean": hits / runs if runs else None, "longest": max((r["longest"] for r in per_lead), default=0)}


# -- the selection of v4 and the kill rule -----------------------------------------------------------------------------


def select_v4(stats: Mapping[str, Mapping[str, float]], base_crps: float) -> str:
    """The arm of v1 to v3 that v4 builds on, by the declared rule (`metadata/faster_scale_1153.json`, `v4_selection_rule`).

    `stats[arm]` has `crps` (pooled mean grid CRPS) and `mean_run` (the 90% band's mean miss run, closed rule, pooled over leads).
    Eligible arms have `crps <= ELIGIBLE_SLACK * base_crps`; the winner is the eligible arm with the shortest mean run, ties to the
    lower CRPS, then the declared order; with none eligible, the lowest CRPS.
    """

    order = {name: i for i, name in enumerate(EARLY_ARMS)}
    eligible = [a for a in stats if stats[a]["crps"] <= ELIGIBLE_SLACK * base_crps]
    if eligible:
        return min(eligible, key=lambda a: (stats[a]["mean_run"], stats[a]["crps"], order.get(a, len(order))))
    return min(stats, key=lambda a: (stats[a]["crps"], order.get(a, len(order))))


def kill_assessment(hits: Mapping, models: Sequence[str], base: str) -> dict:
    """For every model but the base: the leads whose pooled independence p of the 90% band's misses is off 0.000 under each rule, and
    the pooled mean and longest run against the base's. `met` is the declared kill rule: no model off 0.000 at any lead and none with a
    shorter mean run (closed rule)."""

    out: dict = {"models": {}, "off_zero_threshold": OFF_ZERO}
    for model in models:
        entry: dict = {"off_zero_leads": {}, "runs": {}}
        for rule in hits["rules"]:
            leads = []
            for h in sp.HORIZONS:
                cell = hits["rows"][model][rule]["band90"].get(f"h={h}", {}).get("pooled")
                if cell and cell["independence"] and cell["independence"]["p_value"] >= OFF_ZERO:
                    leads.append(h)
            entry["off_zero_leads"][rule] = leads
            entry["runs"][rule] = pooled_runs([hits["rows"][model][rule]["band90"][f"h={h}"]["runs"] for h in sp.HORIZONS])
        out["models"][model] = entry
    arms = [m for m in models if m != base]
    base_mean = out["models"][base]["runs"]["above"]["mean"]
    off = [m for m in arms if any(out["models"][m]["off_zero_leads"].values())]
    shorter = [m for m in arms if out["models"][m]["runs"]["above"]["mean"] is not None and base_mean is not None
               and out["models"][m]["runs"]["above"]["mean"] < base_mean]
    out.update({"base_mean_run": base_mean, "arms_off_zero": off, "arms_shorter_runs": shorter, "met": not off and not shorter})
    return out


# -- the frame ----------------------------------------------------------------------------------------------------------


def frame_cells(frame, model: str, forecasts: Mapping) -> Dict[Tuple[date, int], Tuple[float, float]]:
    """Grid CRPS and upper-tail twCRPS of every (decision day, lead) cell of `forecasts`, after the scored days are checked."""

    cells = {(d, h): frame.target(d, h) for d in forecasts for h in sp.HORIZONS}
    s686.require_scored_days(set(d for d, _ in cells) | set(cells.values()), LAST_DAY)
    return {(d, h): (sp.grid_crps(forecasts[d][h], frame.outcome[t]), sp.upper_tail_twcrps(forecasts[d][h], frame.outcome[t]))
            for (d, h), t in cells.items()}


def build_frame(panel, splits, registry, table, first: Optional[date] = None):
    """The decision days with a forecast of (a), every arm and the benchmarks, whose five targets are scored days.

    The walk of (a) and v1 to v3 comes first, v4 is built on the arm the declared rule picks from it, and v4 is walked second.
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
    plain = sc.Arm(BASE, sc.BASE_SCALE)
    early = sc.walk(panel, [d for d in candidate_days if d in b1], [plain] + list(sc.ARMS), **settings)
    days = [d for d in candidate_days if d in b1 and all(d in early.forecasts[m] for m in (BASE,) + EARLY_ARMS)]
    frame.days = days
    frame.forecasts = {"B1": b1, "B1p": b1p, "B2": b2, **{m: early.forecasts[m] for m in (BASE,) + EARLY_ARMS}}
    stats = {}
    for arm in EARLY_ARMS:
        crps = [sp.grid_crps(early.forecasts[arm][d][h], frame.outcome[frame.target(d, h)]) for d in days for h in sp.HORIZONS]
        misses = [w1133.hit_sequence(
            [frame.outcome[frame.target(d, h)] for d in days], [early.forecasts[arm][d][h] for d in days], "band90", "above")
            for h in sp.HORIZONS]
        stats[arm] = {"crps": sum(crps) / len(crps), "mean_run": pooled_runs([runs_of(m) for m in misses])["mean"]}
    base_crps = [sp.grid_crps(early.forecasts[BASE][d][h], frame.outcome[frame.target(d, h)]) for d in days for h in sp.HORIZONS]
    base_mean = sum(base_crps) / len(base_crps)
    winner = select_v4(stats, base_mean)
    v4 = sc.with_calendar(next(a for a in sc.ARMS if a.name == winner))
    late = sc.walk(panel, days, [v4], table=table, **settings)
    days = [d for d in days if d in late.forecasts[v4.name]]
    frame.days = days
    frame.forecasts[v4.name] = late.forecasts[v4.name]
    for name in list(frame.forecasts):
        frame.forecasts[name] = {d: frame.forecasts[name][d] for d in days}
    frame.all_days = days
    notes = {
        "decision_days_offered": len(candidate_days), "candidate_skipped_for_history": len(early.skipped),
        "benchmark_missing": [d.isoformat() for d in dropped], "scored_decision_days": len(days),
        "first": days[0].isoformat(), "last": days[-1].isoformat(),
        "last_target": frame.target(days[-1], max(sp.HORIZONS)).isoformat(),
        "refits": len(early.fits), "v4_refits": len(late.fits),
    }
    selection = {"stats": stats, "base_crps": base_mean, "eligible_slack": ELIGIBLE_SLACK, "winner": winner, "v4": v4.name}
    diagnostics = {"miss": {d.isoformat(): {h: {"factor": fits["v3_miss"].miss_factor[h], "after": fits["v3_miss"].after_miss[h],
                                              "pairs": fits["v3_miss"].pairs[h]} for h in sp.HORIZONS}
                             for d, fits in early.arm_fits.items()},
                   "types": {d.isoformat(): {h: dict(fits[v4.name].type_factor[h]) for h in sp.HORIZONS}
                             for d, fits in late.arm_fits.items()}}
    return frame, notes, selection, diagnostics


def models_of(frame) -> Tuple[str, ...]:
    """The benchmarks, (a), v1 to v3 and v4, in that order."""

    return BENCHMARKS + (BASE,) + EARLY_ARMS + tuple(m for m in frame.forecasts if m.startswith("v4_"))


def candidates_of(frame) -> Tuple[str, ...]:
    return tuple(m for m in models_of(frame) if m not in BENCHMARKS)


# -- the cells ----------------------------------------------------------------------------------------------------------


def scaled_cells(frame, scores: Mapping[str, Mapping[Tuple[date, int], float]], models: Sequence[str]):
    """Each model's grid CRPS over #967's scale at the cell's decision day and target type; days without a scale are left out."""

    days = list(frame.days)
    leads = list(sp.HORIZONS)
    targets = [[frame.target(d, h) for h in leads] for d in days]
    kinds = [[frame.day_type(t) for t in row] for row in targets]
    b2 = [[scores["B2"][(d, h)] for h in leads] for d in days]
    scales = s967.trailing_scales(days, targets, kinds, b2)
    out: Dict[str, Dict[Tuple[date, int], float]] = {m: {} for m in models}
    for i, d in enumerate(days):
        scale = scales[i]
        if scale is None:
            continue
        for h in leads:
            kind = kinds[i][h - 1]
            for m in models:
                out[m][(d, h)] = scores[m][(d, h)] / scale[kind]
    return out


def all_cells(frame, models: Sequence[str]) -> Dict[str, Dict[str, Dict]]:
    """`cells[metric][model][(day, lead)]` for the scores, the scaled score and the band indicators."""

    cells: Dict[str, Dict[str, Dict]] = {m: {} for m in METRICS + COVERAGE_METRICS}
    for model in models:
        both = frame_cells(frame, model, frame.forecasts[model])
        cells["grid_crps"][model] = {k: v[0] for k, v in both.items()}
        cells["upper_tail_twcrps"][model] = {k: v[1] for k, v in both.items()}
        for c, (lo, hi) in BANDS.items():
            i, j = sp.GRID.index(lo), sp.GRID.index(hi)
            closed, opened = {}, {}
            for d in frame.days:
                for h in sp.HORIZONS:
                    q, y = frame.forecasts[model][d][h], frame.outcome[frame.target(d, h)]
                    closed[(d, h)] = 1.0 if q[i] <= y <= q[j] else 0.0
                    opened[(d, h)] = 1.0 if q[i] < y < q[j] else 0.0
            cells[f"cover{c}_closed"][model], cells[f"cover{c}_open"][model] = closed, opened
    scaled = scaled_cells(frame, {m: cells["grid_crps"][m] for m in models}, models)
    for model in models:
        cells["scaled_grid_crps"][model] = scaled[model]
    return cells


# -- the tests, in parallel ---------------------------------------------------------------------------------------------

_STATE: Dict = {}


def _members(series, members, models):
    return [d for d in sorted(members) if all(d in series[m] for m in models)]


def _pairs_task(job):
    split, label, grain, metric, candidate, members = job
    series = _STATE["series"][(grain, metric)]
    names = list(BENCHMARKS) + ([BASE] if candidate != BASE else [])
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
    reps = _STATE["reps"]
    pooled = split == "pooled"
    out = {}
    for model in models:
        values = [series[model][d] for d in ordered]
        entry = {"mean": sum(values) / len(values)}
        if pooled:
            entry["interval"] = f941.mean_interval(values, seed=SEED, reps=reps)
        out[model] = entry
    return (split, label, metric), out


def _block_task(job):
    """The Politis-White block of the paired loss differential of an arm against (a), and the pooled skill at that block."""

    split, label, grain, metric, candidate, members = job
    series = _STATE["series"][(grain, metric)]
    ordered = _members(series, members, [BASE, candidate])
    d = [series[BASE][x] - series[candidate][x] for x in ordered]
    try:
        block = b949.politis_white(d)
    except ValueError:
        return (split, label, metric, candidate), None
    entry = {"block": block, "days": len(ordered)}
    if split == "pooled":
        at = max(1, round(block))
        test = sp.paired_tests([({x: series[BASE][x] for x in ordered}, {x: series[candidate][x] for x in ordered})], seed=SEED,
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


# -- the hit sequences --------------------------------------------------------------------------------------------------


def hit_tables(frame, models: Sequence[str]) -> dict:
    """Per model, kind, rule and lead, the three coverage tests, pooled, by regime and by pressure-day type, and the runs of the
    pooled sequence (`RUN_KINDS`)."""

    out: dict = {"kinds": list(w1133.kinds_and_p()), "rules": list(ct.HIT_RULES), "rows": {}}
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
                for rule in ct.HIT_RULES:
                    sequence = w1133.hit_sequence(outcomes, laws, kind, rule)
                    cell: dict = {}
                    if len(sequence) >= MIN_GROUP_DAYS:
                        cell["pooled"] = w1133.coverage_row(sequence, p, independence=True)
                    for split, groups in members_of.items():
                        for label, rows in sorted(groups.items()):
                            if len(rows) >= MIN_GROUP_DAYS:
                                cell[f"{split}/{label}"] = w1133.coverage_row(
                                    [sequence[i] for i in rows], p, independence=split == "regime")
                    if kind in RUN_KINDS:
                        cell["runs"] = runs_of(sequence)
                    out["rows"].setdefault(model, {}).setdefault(rule, {}).setdefault(kind, {})[f"h={h}"] = cell
    return out


# -- gbm_funding --------------------------------------------------------------------------------------------------------


def gbm_comparison(frame, gbm: Mapping[date, Mapping[int, Sequence[float]]], series: Mapping[str, Mapping[date, float]],
                   candidates: Sequence[str], metric: str, *, draws: int) -> dict:
    """Each candidate's paired test against `gbm_funding` on the decision days its walks cover that the candidates score.

    `series[model]` is the candidate's per-decision-day score of `metric`. Undefined where fewer than `MIN_GROUP_DAYS` days overlap.
    """

    days = sorted(d for d in gbm if d in set(frame.days))
    if len(days) < MIN_GROUP_DAYS:
        return {"days": len(days), "undefined": "fewer than %d days covered" % MIN_GROUP_DAYS}
    cells = frame_cells(frame, GBM, {d: gbm[d] for d in days})
    column = 0 if metric == "grid_crps" else 1
    g = s686.by_decision({k: v[column] for k, v in cells.items()})
    out = {"days": len(days), "gbm_mean": sum(g[d] for d in days) / len(days), "vs": {}}
    for m in candidates:
        out["vs"][m] = s761.run_pairs({GBM: g}, series[m], days, seed=SEED, draws=draws)[GBM]
        out["vs"][m]["candidate_mean"] = sum(series[m][d] for d in days) / len(days)
    return out


# -- the report ---------------------------------------------------------------------------------------------------------


def score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    panel = load_daily_panel(panel_path)
    splits = load_split_declaration(s686.SPLITS)
    registry = json.loads(s686.SOURCES.read_text(encoding="utf-8"))
    table = cal.TermTable(panel, announced_iorb.load_announcements(IORB_TABLE), decision_time=DECISION_TIME)
    frame, notes, selection, diagnostics = build_frame(panel, splits, registry, table, args.first)
    models = models_of(frame)
    candidates = candidates_of(frame)
    cells = all_cells(frame, models)
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
                continue  # the scaled score is read pooled and by regime and day type (the cost of a lead's tests is not worth its table)
            for candidate in candidates:
                jobs.append(("pairs", (split, label, grain, metric, candidate, tuple(members))))
                if candidate != BASE and split in ("pooled", "regime") and metric != "scaled_grid_crps":
                    jobs.append(("block", (split, label, grain, metric, candidate, tuple(members))))
        for metric in COVERAGE_METRICS:
            jobs.append(("coverage", (split, label, grain, metric, tuple(members))))
    done = run_jobs(jobs, args.workers)
    by_key = {(s_, l_): (g, m) for s_, l_, g, m in groups}
    result: dict = {
        "issue": 1153, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": panel_sha256(panel_path),
        "subset_from": None if args.first is None else args.first.isoformat(),
        "label": "development, not a verdict", "seed": SEED, "draws": args.draws, "reps": args.reps,
        "notes": notes, "models": list(models), "base": BASE, "arms": [m for m in candidates if m != BASE],
        "selection": selection, "diagnostics": diagnostics, "groups": {}, "skipped_groups": skipped, "politis_white": {},
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
    result["kill"] = kill_assessment(result["hits"], candidates, BASE)
    result["gbm"] = None
    if args.walks is not None:
        gbm = c1115.load_gbm(Path(args.walks), result["panel_sha256"], frame, GBM)
        if gbm is not None:
            pooled = {metric: series[("decision", metric)] for metric in ("grid_crps", "upper_tail_twcrps")}
            result["gbm"] = {metric: gbm_comparison(frame, gbm, pooled[metric], candidates, metric, draws=args.draws)
                             for metric in pooled}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page -----------------------------------------------------------------------------------------------------------


def skill(row: Optional[dict]) -> str:
    return "n/a" if row is None else s761.skill_text(row)


def _ordered(split: str, labels) -> List[str]:
    return f941._ordered(split, labels)


def verdict(row: dict) -> str:
    return f941.verdict(row)


HEADER = ["| | mean | skill vs B1 [90%] | skill vs B1' [90%] | skill vs B2 [90%] | skill vs (a) [90%] |", "|---|---|---|---|---|---|"]


def _score_rows(cell: dict, r: dict) -> List[str]:
    means = cell["means"]
    if not means:
        return ["| (no day with a scale) | | | | | |"]
    out = [f"| {label_of(m)} | {means[m]:.3f} | | | | |" for m in BENCHMARKS]
    for m in [BASE] + r["arms"]:
        vs = cell["vs"][m]
        vs_base = "" if m == BASE else skill(vs[BASE])
        out.append(f"| {label_of(m)} | {means[m]:.3f} | {skill(vs['B1'])} | {skill(vs['B1p'])} | {skill(vs['B2'])} | {vs_base} |")
    return out


def _fmt_p(e: Optional[dict], key: str) -> str:
    return "n/a" if not e or not e.get(key) else f"{e[key]['p_value']:.3f}"


def clustering_section(r: dict) -> List[str]:
    hits, models = r["hits"], [BASE] + r["arms"]
    out = ["## The clustering of the 90% band's misses (the headline of this fix)", "",
           "Per lead, pooled over the scored days: the miss rate (nominal 0.10), then Christoffersen's independence p and the conditional "
           "coverage p. A p of 0.000 is below 0.0005. Reporting only: no p-value is a gate.", ""]
    for rule in hits["rules"]:
        words = "closed band, a miss is `y` outside `[q05, q95]`" if rule == "above" else "open band, a miss includes `y` equal to a bound"
        out += [f"Rule `{rule}` ({words}); rate (independence p / conditional coverage p):", "",
                "| | " + " | ".join(f"h={h}" for h in sp.HORIZONS) + " |", "|---|" + "---|" * len(sp.HORIZONS)]
        for m in models:
            cells = []
            for h in sp.HORIZONS:
                e = hits["rows"][m][rule]["band90"].get(f"h={h}", {}).get("pooled")
                cells.append("n/a" if e is None else f"{e['rate']:.3f} ({_fmt_p(e, 'independence')} / {_fmt_p(e, 'conditional')})")
            out.append(f"| {label_of(m)} | " + " | ".join(cells) + " |")
        out.append("")
    out += ["Independence p of the 90% band's misses within a regime (consecutive days of the regime), by lead, closed rule (`above`):", ""]
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
            band = pooled_runs([hits["rows"][m][rule]["band90"][f"h={h}"]["runs"] for h in sp.HORIZONS])
            tail = pooled_runs([hits["rows"][m][rule]["q95"][f"h={h}"]["runs"] for h in sp.HORIZONS])
            f = lambda x: "n/a" if x["mean"] is None else f"{x['mean']:.3f}"  # noqa: E731
            out.append(f"| {label_of(m)} | {band['runs']} | {f(band)} | {band['longest']} | {tail['runs']} | {f(tail)} | {tail['longest']} |")
        out.append("")
    return out


def kill_section(r: dict) -> List[str]:
    k = r["kill"]
    out = ["## Against the kill rule", "",
           "The kill rule (the issue's, read in the declaration): stop if no arm moves the independence p-value off 0.000 at any lead and no "
           f"arm shortens the miss runs. 'Off 0.000' is a pooled independence p of the 90% band of at least {k['off_zero_threshold']}, "
           "at any lead, under either hit rule; 'shortens' is a mean run (closed rule, pooled over leads) below (a)'s "
           f"({k['base_mean_run']:.3f}). The arms are provisional (the calendar-blind ones), so a kill would close no question.", "",
           "| arm | leads off 0.000, `above` | leads off 0.000, `at_or_above` | mean run, `above` (longest) | mean run, `at_or_above` (longest) |",
           "|---|---|---|---|---|"]
    for m in [BASE] + r["arms"]:
        e = k["models"][m]
        runs = {rule: e["runs"][rule] for rule in e["runs"]}
        fm = lambda x: "n/a" if x["mean"] is None else f"{x['mean']:.3f} ({x['longest']})"  # noqa: E731
        leads = {rule: (", ".join(f"h={h}" for h in e["off_zero_leads"][rule]) or "none") for rule in e["off_zero_leads"]}
        out.append(f"| {label_of(m)} | {leads['above']} | {leads['at_or_above']} | {fm(runs['above'])} | {fm(runs['at_or_above'])} |")
    out += ["", f"Arms with a lead off 0.000: {', '.join(label_of(m) for m in k['arms_off_zero']) or 'none'}. "
            f"Arms with a shorter mean run than (a): {', '.join(label_of(m) for m in k['arms_shorter_runs']) or 'none'}. "
            f"**The kill rule is {'met' if k['met'] else 'not met'}.**", ""]
    return out


def selection_section(r: dict) -> List[str]:
    s = r["selection"]
    out = ["## Which arm v4 builds on", "",
           "Chosen by the rule declared before any score: among v1 to v3, the arms whose pooled mean grid CRPS is at most "
           f"{(s['eligible_slack'] - 1) * 100:.0f}% above (a)'s ({s['base_crps']:.3f}) are eligible, and the eligible arm with the shortest "
           "mean run of the 90% band's misses (closed rule, pooled over leads) wins; none eligible, the lowest grid CRPS wins.", "",
           "| arm | pooled mean grid CRPS | eligible | mean miss run |", "|---|---|---|---|"]
    for name, st in s["stats"].items():
        out.append(f"| {label_of(name)} | {st['crps']:.3f} | {'yes' if st['crps'] <= s['eligible_slack'] * s['base_crps'] else 'no'} | "
                   f"{st['mean_run']:.3f} |")
    out += ["", f"Winner: **{label_of(s['winner'])}**; v4 is `{s['v4']}`.", ""]
    return out


def render(r: dict) -> str:
    n = r["notes"]
    pooled = r["groups"]["pooled"]["all decision days"]
    out = [
        "# A faster-reacting scale against the clustered misses (#1153)", "",
        f"**Hypothesis and step:** H5 (primary goal), step 3 (fix; refocus), the clustered misses of the scaled mean reversion. "
        f"**{r['label'].capitalize()}**: development days to {n['last_target']}, no verdict (scoring protocol v1, #640). Any change to the "
        "candidate is Eleonora's decision. Generated by `scripts/faster_scale_1153.py page` from "
        f"`docs/research/faster-scale-1153/result.json`, not edited by hand; declared in `{r['declaration']}` before any score.", "",
        f"Panel digest `{r['panel_sha256'][:8]}…`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business "
        f"days, {r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval; skill is `mean(d) / mean(S(benchmark))` with "
        "`d = S(benchmark) - S(candidate)`, positive favours the candidate. Coverage intervals are 90% stationary-bootstrap percentile "
        f"intervals ({r['reps']:,} resamples), pooled. Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); "
        "(a) and every arm are scored on the same days.", "",
        "**What this is not.** (a) and the arms v1 to v3 read no calendar column, so their figures are provisional under the calendar-first "
        "rule (`docs/research/provisional-calendar-register.md`) and close no question in either direction; v4 reads the target day's "
        "calendar type on direct pairs. The base is #941's best variant, chosen after seeing 2018-2025. #1145 (PR #1151) has not merged and "
        "no winning arm of it exists, so this runs on (a) alone. `gbm_funding` is " + (
            "compared below on the days its walks cover." if r.get("gbm") else
            "not compared here: its walks are a long run for Eleonora's Mac and were not supplied.") , ""]
    out += selection_section(r)
    out += clustering_section(r)
    out += kill_section(r)
    for metric in METRICS:
        out += [f"## {METRIC_TITLES[metric]}, mean over leads 1 to 5, pooled", ""] + HEADER + _score_rows(pooled[metric], r) + [""]
    out += ["## Skill of each arm over (a), by lead [90%]", ""]
    for metric in ("grid_crps", "upper_tail_twcrps"):
        out += [f"{METRIC_TITLES[metric]}:", "", "| | " + " | ".join(f"h={h}" for h in sp.HORIZONS) + " |", "|---|" + "---|" * len(sp.HORIZONS)]
        for m in r["arms"]:
            out.append(f"| {label_of(m)} | " + " | ".join(
                skill(r["groups"]["lead"][f"h={h}"][metric]["vs"][m][BASE]) for h in sp.HORIZONS) + " |")
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
            "A gain (loss) is a grid-CRPS skill over (a) whose 90% interval is above (below) zero; otherwise undecided.", ""]
    for m in r["arms"]:
        parts = []
        for split in ("pooled", "regime", "pressure_day_type"):
            for label in _ordered(split, r["groups"].get(split, {})):
                parts.append(f"{label}: {verdict(r['groups'][split][label]['grid_crps']['vs'][m][BASE])}")
        out.append(f"- **{label_of(m)}**: " + "; ".join(parts) + ".")
    out.append("")
    out += coverage_section(r)
    out += hit_section(r)
    out += politis_white_section(r)
    out += gbm_section(r)
    out += diagnostics_section(r)
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
    out = ["## Exceedances and band misses, by lead, under both hit rules", "",
           "Each cell is the rate (nominal in the heading) with the p-values of Kupiec's unconditional coverage test, Christoffersen's "
           "independence test and his conditional coverage test (`repo_model.coverage_tests`). Upper tails: the outcome above q95 / q99; "
           "lower tails: below q05 / q01; a band miss: outside the band. Reporting only: no p-value is a gate. By regime and "
           "pressure-day type, the five leads together with Kupiec's p; the independence tests per regime and lead are in `result.json`.", ""]
    nominal = w1133.kinds_and_p()
    for rule in hits["rules"]:
        words = "strictly beyond the quantile / outside the closed band" if rule == "above" else "at or beyond the quantile / outside the open band"
        for kind in hits["kinds"]:
            p = nominal[kind]
            out += [f"### {kind} (nominal {p:.2f}), rule `{rule}` ({words})", "",
                    "Pooled; rate (Kupiec p / independence p / conditional coverage p):", "",
                    "| | " + " | ".join(f"h={h}" for h in sp.HORIZONS) + " |", "|---|" + "---|" * len(sp.HORIZONS)]
            for m in r["models"]:
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
                for m in r["models"]:
                    cells = []
                    for label in order:
                        total = hit_count = 0
                        for h in sp.HORIZONS:
                            e = hits["rows"][m][rule][kind].get(f"h={h}", {}).get(f"{split}/{label}")
                            if e is not None:
                                total, hit_count = total + e["n"], hit_count + e["hits"]
                        cells.append("n/a" if not total else f"{hit_count / total:.3f} ({ct.kupiec([1] * hit_count + [0] * (total - hit_count), p).p_value:.3f})")
                    out.append(f"| {label_of(m)} | " + " | ".join(cells) + " |")
                out.append("")
    return out


def politis_white_section(r: dict) -> List[str]:
    out = ["## The Politis-White block beside the block of 10", "",
           "The automatic block length (Politis and White 2004, with the correction of Patton, Politis and White 2009, "
           "`scripts/block_length_949.py`) of the paired loss differential `S(a) - S(arm)`, in days, with the pooled skill over (a) at that "
           "block. Reported, never substituted for 10.", ""]
    columns = ["pooled"] + [l for l in REGIME_ORDER if l in r["politis_white"].get("regime", {})]
    for metric in ("grid_crps", "upper_tail_twcrps"):
        out += [f"{METRIC_TITLES[metric]}:", "", "| | " + " | ".join(columns) + " | pooled skill vs (a) at that block |", "|---|" + "---|" * (len(columns) + 1)]
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


def gbm_section(r: dict) -> List[str]:
    out = ["## Against gbm_funding", ""]
    if not r.get("gbm"):
        return out + ["Not scored: the five walks of `gbm_funding` (#634) are a long run for Eleonora's Mac and were not supplied "
                      "(`--walks`). The comparison runs unchanged on them; nothing else on this page depends on it.", ""]
    for metric, cell in r["gbm"].items():
        out += [f"{METRIC_TITLES[metric]}, pooled, on the {cell['days']} decision days the walks cover:", ""]
        if "undefined" in cell:
            out += [cell["undefined"], ""]
            continue
        out += [f"gbm_funding mean {cell['gbm_mean']:.3f}.", "", "| | mean | skill of gbm_funding vs the row [90%] |", "|---|---|---|"]
        for m, row in cell["vs"].items():
            out.append(f"| {label_of(m)} | {row['candidate_mean']:.3f} | {skill(row)} |")
        out.append("")
    return out


def diagnostics_section(r: dict) -> List[str]:
    d = r["diagnostics"]
    out = ["## What the fitted factors did", "",
           "Medians over the refits of the factors v3 (miss feedback) and v4 (calendar type) fitted, by lead.", ""]
    mid = lambda v: sorted(v)[len(v) // 2] if v else float("nan")  # noqa: E731
    out += ["v3: the widening after a miss (1 where fewer than 20 pairs followed a miss) and the pairs that followed a miss at the last refit.", "",
            "| lead | factor, median | pairs after a miss, last refit | pairs, last refit |", "|---|---|---|---|"]
    days = sorted(d["miss"])
    for h in sp.HORIZONS:
        f = [d["miss"][day][str(h)]["factor"] for day in days]
        out.append(f"| {h} | {mid(f):.3f} | {d['miss'][days[-1]][str(h)]['after']} | {d['miss'][days[-1]][str(h)]['pairs']} |")
    out += ["", f"v4 ({label_of(r['selection']['v4'])}): the median factor on the scale of each calendar type, by lead (`-` where the type did not enter).", "",
            "| lead | " + " | ".join(sc.CAL_TYPES) + " |", "|---|" + "---|" * len(sc.CAL_TYPES)]
    days = sorted(d["types"])
    for h in sp.HORIZONS:
        cells = []
        for t in sc.CAL_TYPES:
            v = [d["types"][day][str(h)][t] for day in days if t in d["types"][day][str(h)]]
            cells.append("-" if not v else f"{mid(v):.3f}")
        out.append(f"| {h} | " + " | ".join(cells) + " |")
    out.append("")
    return out


def page(args) -> int:
    r = json.loads(Path(args.score).read_text(encoding="utf-8"))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(render(r), encoding="utf-8")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score", help="walk (a) and the arms and score them")
    s.add_argument("--panel", required=True)
    s.add_argument("--output", required=True)
    s.add_argument("--walks", default=None, help="a directory with gbm_funding_h1..5.json (optional)")
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
