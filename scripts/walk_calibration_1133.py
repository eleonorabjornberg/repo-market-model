"""Walk-forward calibration of the predictive quantiles, scored (#1133, avenue #809; H5 step 3).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.
Every choice is in `metadata/walk_calibration_1133.json`, which this script refuses to read unless it is committed and
unchanged. The base is #941's `spread_mr_fhs_mad20_f0.5` (`repo_model.spread_mr_fhs`); the one arm is
`repo_model.walk_calibration` (the pooled recalibration; the arms by the floor flag and with the tail widened, were dropped by Eleonora's ruling on #1142). It is scored
with the scorer of scoring protocol v1 (`repo_model.scoring_protocol`) against the uncalibrated base, B1 with B1' beside it,
and B2 (`repo_model.protocol_benchmarks`, `repo_model.b1_calendar`), on the studentized stationary bootstrap of ruling 1
(#739), and with the scaled score of #967 beside the raw one. Scored decision days are those whose five targets are on or
before 2025-12-31; no later day is read and no locked day is scored (`docs/decisions/lockbox.md`).

Measures: grid CRPS and upper-tail twCRPS and the scaled grid CRPS (pooled, by lead, by regime and by pressure-day type);
the coverage of the 50, 80, 90 and 98% bands; the exceedance rates of q05, q95, q01 and q99 and the misses of those bands,
by lead and regime, under both hit rules, with Kupiec's test and Christoffersen's independence and conditional coverage
tests (`repo_model.coverage_tests`). The hit rule is Eleonora's open question (#993): both are reported.

The base walk is arithmetic on the panel (the 89 refits of #941's base) and runs in minutes. Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    PYTHONPATH=src python3 scripts/walk_calibration_1133.py score --panel PUB.csv \\
        --output docs/research/walk-calibration-1133/result.json
    PYTHONPATH=src python3 scripts/walk_calibration_1133.py page \\
        --score docs/research/walk-calibration-1133/result.json --output docs/research/walk-calibration-1133-result.md

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


from repo_model import b1_calendar as b1c  # noqa: E402
from repo_model import coverage_tests as ct  # noqa: E402
from repo_model import protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model import spread_mr_fhs as fhs, walk_calibration as wc  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.splits import SplitError  # noqa: E402

s686 = _load("spread_mean_reversion_686")
s761 = _load("spread_mr_variants_761")
s967 = _load("scaled_score_967")
f941 = _load("fhs_scale_941")

DECLARATION = REPO / "metadata" / "walk_calibration_1133.json"
SEED = 1133
LAST_DAY = s686.LAST_DAY
DECISION_TIME = s686.DECISION_TIME
MIN_GROUP_DAYS = s686.MIN_GROUP_DAYS
BASE = "spread_mr_fhs_mad20_f0.5"
ARM_NAMES: Dict[str, str] = {"pooled": "calibrated (a) pooled"}
ARM_KEYS: Dict[str, str] = {arm: f"{BASE}+{arm}" for arm in wc.ARMS}
CANDIDATES: Tuple[str, ...] = (BASE,) + tuple(ARM_KEYS.values())
BENCHMARKS: Tuple[str, ...] = ("B1", "B1p", "B2")
MODELS: Tuple[str, ...] = BENCHMARKS + CANDIDATES
LABELS: Dict[str, str] = {"B1": "B1", "B1p": "B1' (#960)", "B2": "B2", BASE: "uncalibrated base (#941 mad20)"}
LABELS.update({ARM_KEYS[arm]: name for arm, name in ARM_NAMES.items()})
METRICS: Tuple[str, ...] = ("grid_crps", "upper_tail_twcrps", "scaled_grid_crps")
BANDS: Dict[int, Tuple[float, float]] = {50: (0.25, 0.75), 80: (0.10, 0.90), 90: (0.05, 0.95), 98: (0.01, 0.99)}
COVERAGE_METRICS: Tuple[str, ...] = tuple(f"cover{c}_{kind}" for c in BANDS for kind in ("closed", "open"))
#: The exceedance sequences: (name, grid level, side). A band's miss sequence is `band<c>`.
TAILS: Tuple[Tuple[str, float, str], ...] = (
    ("q95", 0.95, "upper"), ("q99", 0.99, "upper"), ("q05", 0.05, "lower"), ("q01", 0.01, "lower"))
REGIME_ORDER = ["2018-19", "2020", "2021-23", "2024", "2025-26"]
DAYTYPE_ORDER = ["quarter_end", "month_end", "tax_date", "ordinary"]
SPLIT_TITLES = {"regime": "regime (target day)", "pressure_day_type": "pressure-day type (target day)"}
METRIC_TITLES = {"grid_crps": "grid CRPS", "upper_tail_twcrps": "upper-tail twCRPS", "scaled_grid_crps": "scaled grid CRPS (#967)"}


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


# -- the frame -----------------------------------------------------------------------------------------------------


def build_frame(panel, splits, registry, declaration, first: Optional[date] = None):
    """The base's walk, the benchmarks and the pooled arm, on the decision days whose targets are scored days.

    `first` starts the walk later than the declared study does; it exists for the test of this script and the declared run
    never passes it.
    """

    frame = s686.Frame(panel, splits, registry, declaration)
    candidate_days = [
        day for i, day in enumerate(frame.dates)
        if i + max(sp.HORIZONS) < len(panel) and frame.dates[i + max(sp.HORIZONS)] <= LAST_DAY
        and (first is None or day >= first)
    ]
    s686.require_scored_days(candidate_days, LAST_DAY)
    variant = next(v for v in fhs.VARIANTS if v.name == BASE)
    walk = fhs.walk(panel, candidate_days, [variant], **frame.settings)
    b1, b1p, b2, dropped = {}, {}, {}, []
    for day in walk.forecasts[BASE]:
        index = frame.position[day]
        try:
            b1[day] = pb.b1_forecast(panel, index, registry=registry, decision_time=DECISION_TIME)
            b1p[day] = b1c.b1_calendar_forecast(panel, index, registry=registry, decision_time=DECISION_TIME, splits=splits)
            b2[day] = pb.b2_forecast(panel, index, registry=registry, decision_time=DECISION_TIME, splits=splits)
        except (sp.ProtocolError, SplitError):
            dropped.append(day)
    days = [day for day in walk.forecasts[BASE] if day in b1 and day in b1p and day in b2]
    base = {day: walk.forecasts[BASE][day] for day in days}
    anchors = {day: pb._anchor(panel, frame.position[day], registry, DECISION_TIME) for day in days}
    spreads = [row.spread_bps for row in panel]
    laws, refits, uncalibrated = wc.walk(days, base, anchors, frame.position, spreads, frame.dates)
    scored = [day for day in days if day in laws]
    frame.forecasts = {"B1": b1, "B1p": b1p, "B2": b2, BASE: base}
    for arm in wc.ARMS:
        frame.forecasts[ARM_KEYS[arm]] = laws
    frame.all_days = days
    frame.days = scored
    frame.anchors = anchors
    notes = {
        "decision_days_offered": len(candidate_days),
        "candidate_skipped_for_history": len(walk.skipped),
        "benchmark_missing": [d.isoformat() for d in dropped],
        "base_decision_days": len(days),
        "uncalibrated_decision_days": len(uncalibrated),
        "scored_decision_days": len(scored),
        "first": scored[0].isoformat(), "last": scored[-1].isoformat(),
        "last_target": frame.target(scored[-1], max(sp.HORIZONS)).isoformat(),
        "base_refits": len(walk.fits), "calibration_refits": len(refits),
    }
    return frame, notes, refits


def refit_summary(frame, refits) -> List[dict]:
    """What each refit kept, for the page: the cells and the level-0.5 and 0.95 offsets of each lead."""

    i50, i95 = wc.MEDIAN, wc.HIGH
    out = []
    for day, r in sorted(refits.items()):
        out.append({
            "day": day.isoformat(), "anchor": frame.dates[frame.anchors[day]].isoformat(),
            "by_lead": {str(h): {
                "cells": r.pooled[h].cells, "offset_q50": r.pooled[h].offsets[i50], "offset_q95": r.pooled[h].offsets[i95],
            } for h in sp.HORIZONS},
        })
    return out


# -- the cells -----------------------------------------------------------------------------------------------------


def scaled_cells(frame, scores: Mapping[str, Mapping[Tuple[date, int], float]]) -> Dict[str, Dict[Tuple[date, int], float]]:
    """Each model's grid CRPS over #967's scale at the cell's decision day and target type; days without a scale are left out.

    The scale is the trailing-year median of B2's grid CRPS by pressure-day type, read from positions up to six before the
    decision day (`scaled_score_967.trailing_scales`), over every base decision day, not only the calibrated ones.
    """

    days = list(frame.all_days)
    leads = list(sp.HORIZONS)
    targets = [[frame.target(d, h) for h in leads] for d in days]
    kinds = [[frame.day_type(t) for t in row] for row in targets]
    b2 = [[scores["B2"][(d, h)] for h in leads] for d in days]
    scales = s967.trailing_scales(days, targets, kinds, b2)
    out: Dict[str, Dict[Tuple[date, int], float]] = {m: {} for m in MODELS}
    at = {d: i for i, d in enumerate(days)}
    for d in frame.days:
        scale = scales[at[d]]
        if scale is None:
            continue
        for h in leads:
            kind = kinds[at[d]][h - 1]
            for m in MODELS:
                out[m][(d, h)] = scores[m][(d, h)] / scale[kind]
    return out


def all_cells(frame) -> Dict[str, Dict[str, Dict[Tuple[date, int], float]]]:
    """`cells[metric][model][(day, lead)]` for the scores, the scaled score and the band indicators."""

    cells: Dict[str, Dict[str, Dict]] = {m: {} for m in METRICS + COVERAGE_METRICS}
    raw: Dict[str, Dict[Tuple[date, int], float]] = {}
    scored = frame.days
    frame.days = frame.all_days  # B2's scale reads the base decision days before the first calibrated one
    try:
        for model in ("B2",):
            raw[model] = f941.cell_values(frame, model)[0]["grid_crps"]
    finally:
        frame.days = scored
    for model in MODELS:
        values = f941.cell_values(frame, model)[0]
        cells["grid_crps"][model] = values["grid_crps"]
        cells["upper_tail_twcrps"][model] = values["upper_tail_twcrps"]
        for c, (lo, hi) in BANDS.items():
            i, j = sp.GRID.index(lo), sp.GRID.index(hi)
            closed, opened = {}, {}
            for d in frame.days:
                for h in sp.HORIZONS:
                    q, y = frame.forecasts[model][d][h], frame.outcome[frame.target(d, h)]
                    closed[(d, h)] = 1.0 if q[i] <= y <= q[j] else 0.0
                    opened[(d, h)] = 1.0 if q[i] < y < q[j] else 0.0
            cells[f"cover{c}_closed"][model], cells[f"cover{c}_open"][model] = closed, opened
    scores = {m: cells["grid_crps"][m] for m in MODELS}
    scores["B2"] = {**raw["B2"], **scores["B2"]}
    scaled = scaled_cells(frame, scores)
    for model in MODELS:
        cells["scaled_grid_crps"][model] = scaled[model]
    return cells


def groups_of(frame) -> List[Tuple[str, str, str, List[date]]]:
    return f941.groups_of(frame)


# -- the tests, in parallel ----------------------------------------------------------------------------------------

_STATE: Dict = {}


def _members(series, members, models):
    return [d for d in sorted(members) if all(d in series[m] for m in models)]


def _pairs_task(job):
    split, label, grain, metric, candidate, members = job
    series = _STATE["series"][(grain, metric)]
    names = list(BENCHMARKS) + ([BASE] if candidate != BASE else [])
    days = _members(series, members, list(names) + [candidate])
    if len(days) < MIN_GROUP_DAYS:
        return (split, label, metric, candidate), {n: {"undefined": "fewer than %d days with a scale" % MIN_GROUP_DAYS, "days": len(days)} for n in names}
    return (split, label, metric, candidate), s761.run_pairs(
        {n: series[n] for n in names}, series[candidate], days, seed=SEED, draws=_STATE["draws"])


def _coverage_task(job):
    split, label, grain, metric, members = job
    series = _STATE["series"][(grain, metric)]
    ordered = _members(series, members, MODELS)
    reps = _STATE["reps"]
    out = {}
    for model in MODELS:
        values = [series[model][d] for d in ordered]
        entry = {"mean": sum(values) / len(values), "interval": f941.mean_interval(values, seed=SEED, reps=reps)}
        if model in CANDIDATES and model != BASE:
            ref = [series[BASE][d] for d in ordered]
            entry["difference_from_base"] = sum(a - b for a, b in zip(values, ref)) / len(values)
            entry["difference_interval"] = f941.difference_interval(values, ref, seed=SEED, reps=reps)
        out[model] = entry
    return (split, label, metric), out


def _dispatch(job):
    kind, payload = job
    return kind, {"pairs": _pairs_task, "coverage": _coverage_task}[kind](payload)


def run_jobs(jobs, workers: int):
    context = multiprocessing.get_context("fork")
    with context.Pool(workers) as pool:
        return pool.map(_dispatch, jobs, chunksize=1)


# -- the hit sequences ---------------------------------------------------------------------------------------------


def hit_sequence(outcomes: Sequence[float], laws: Sequence[Sequence[float]], kind: str, rule: str) -> List[int]:
    """The exceedance sequence `kind` under `rule`: a tail beyond its quantile, or an outcome outside a band.

    `rule` is `coverage_tests`' ("above": the outcome is strictly beyond the quantile; "at_or_above": it may equal it). The
    lower tail is the mirror: `y < q` or `y <= q`.
    """

    def upper(level: float) -> List[int]:
        return ct.hit_sequence(outcomes, [q[sp.GRID.index(level)] for q in laws], rule=rule)

    def lower(level: float) -> List[int]:
        return ct.hit_sequence([-y for y in outcomes], [-q[sp.GRID.index(level)] for q in laws], rule=rule)

    for name, level, side in TAILS:
        if kind == name:
            return upper(level) if side == "upper" else lower(level)
    lo, hi = BANDS[int(kind[4:])]
    return [max(a, b) for a, b in zip(lower(lo), upper(hi))]


def kinds_and_p() -> Dict[str, float]:
    out = {name: 1.0 - level if side == "upper" else level for name, level, side in TAILS}
    out.update({f"band{c}": 1.0 - c / 100.0 for c in BANDS})
    return out


def coverage_row(sequence: Sequence[int], p: float, *, independence: bool) -> dict:
    return f941.coverage_row(sequence, p, independence=independence)


def hit_tables(frame) -> dict:
    """Per model, kind, rule and lead, the three coverage tests, pooled, by regime and by pressure-day type."""

    out: dict = {"kinds": list(kinds_and_p()), "rules": list(ct.HIT_RULES), "rows": {}}
    for h in sp.HORIZONS:
        days = list(frame.days)
        targets = [frame.target(d, h) for d in days]
        outcomes = [frame.outcome[t] for t in targets]
        members_of: Dict[str, Dict[str, List[int]]] = {}
        for split, label_of in (("regime", frame.regime), ("pressure_day_type", frame.day_type)):
            for i, t in enumerate(targets):
                members_of.setdefault(split, {}).setdefault(label_of(t), []).append(i)
        for model in MODELS:
            laws = [frame.forecasts[model][d][h] for d in days]
            for kind, p in kinds_and_p().items():
                for rule in ct.HIT_RULES:
                    sequence = hit_sequence(outcomes, laws, kind, rule)
                    cell: dict = {}
                    if len(sequence) >= MIN_GROUP_DAYS:
                        cell["pooled"] = coverage_row(sequence, p, independence=True)
                    for split, groups in members_of.items():
                        for label, rows in sorted(groups.items()):
                            if len(rows) >= MIN_GROUP_DAYS:
                                cell[f"{split}/{label}"] = coverage_row(
                                    [sequence[i] for i in rows], p, independence=split == "regime")
                    out["rows"].setdefault(model, {}).setdefault(rule, {}).setdefault(kind, {})[f"h={h}"] = cell
    return out


# -- the report ----------------------------------------------------------------------------------------------------


def score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    panel = load_daily_panel(panel_path)
    splits = load_split_declaration(s686.SPLITS)
    registry = json.loads(s686.SOURCES.read_text(encoding="utf-8"))
    frame, notes, refits = build_frame(panel, splits, registry, declaration, args.first)
    cells = all_cells(frame)
    groups = groups_of(frame)
    series: Dict[Tuple[str, str], Dict[str, Dict[date, float]]] = {}
    for _split, _label, grain, _members_ in groups:
        for metric in METRICS + COVERAGE_METRICS:
            if (grain, metric) not in series:
                series[(grain, metric)] = {m: f941.series_of(frame, cells[metric][m], grain) for m in MODELS}
    _STATE.update(series=series, draws=args.draws, reps=args.reps)
    jobs, skipped = [], {}
    for split, label, grain, members in groups:
        if len(members) < MIN_GROUP_DAYS:
            skipped[f"{split}/{label}"] = len(members)
            continue
        for metric in METRICS:
            for candidate in CANDIDATES:
                jobs.append(("pairs", (split, label, grain, metric, candidate, tuple(members))))
        for metric in COVERAGE_METRICS:
            jobs.append(("coverage", (split, label, grain, metric, tuple(members))))
    done = run_jobs(jobs, args.workers)
    by_key = {(s_, l_): (g, m) for s_, l_, g, m in groups}
    result: dict = {
        "issue": 1133, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": panel_sha256(panel_path),
        "subset_from": None if args.first is None else args.first.isoformat(),
        "label": "development, not a verdict", "seed": SEED, "draws": args.draws, "reps": args.reps,
        "notes": notes, "models": list(MODELS), "base": BASE, "arms": list(ARM_KEYS.values()),
        "refits": refit_summary(frame, refits), "groups": {}, "skipped_groups": skipped,
    }
    for kind, (ident, payload) in done:
        split, label, metric = ident[:3]
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(by_key[(split, label)][1])})
        if kind == "pairs":
            entry.setdefault(metric, {"means": {}, "vs": {}})["vs"][ident[3]] = payload
        else:
            entry[metric] = payload
    for split, labels in result["groups"].items():
        for label, entry in labels.items():
            grain, members = by_key[(split, label)]
            for metric in METRICS:
                ser = series[(grain, metric)]
                days = _members(ser, members, MODELS)
                entry[metric]["means"] = {m: sum(ser[m][d] for d in days) / len(days) for m in MODELS} if days else {}
                entry[metric]["days"] = len(days)
    result["hits"] = hit_tables(frame)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------


def _ordered(split: str, labels) -> List[str]:
    return f941._ordered(split, labels)


def skill_verdict(row: dict) -> str:
    """The reading the first page was written with (before #1167): the skill interval. Kept so that page can be regenerated."""

    return f941.verdict(row)


def verdict(row: dict) -> str:
    """The declared reading of one row: the studentized one-sided bound on mean d (her ruling on #1009; #1167), not the skill interval."""

    if "undefined" in row:
        return "undecided"
    lo, hi = row["difference_interval"]
    return "gain" if lo > 0.0 else "loss" if hi < 0.0 else "undecided"


READING_RULE = {
    "mean_d": [
        "A gain (loss) is read when the lower (upper) end of the 90% studentized interval on the mean difference d is above (below) zero; "
        "otherwise undecided. The interval is the pair of one-sided 95% bounds, with d = S(the uncalibrated base) - S(candidate), positive favouring "
        "the candidate. This is the studentized bound on mean d that the protocol's verdict reads (her ruling on #1009, directive #1167); "
        "the skill interval in the tables is shown beside it and is not the reading. The mean-d bound is in `docs/research/walk-calibration-1133/result.json` and on "
        "`docs/research/walk-calibration-1133-mean-d-1167-result.md`.", "",
        "**Caveat (Lens C of the five-lens review, #958).** The lag-10 HAC standard error that studentizes the mean-d bound is "
        "understated about 2× after 2020, so the bound is optimistic there: an interval that excludes zero is narrower than it should be."],
    "skill": ["A gain (loss) is a grid-CRPS skill over the uncalibrated base whose 90% interval is above (below) zero; otherwise undecided."],
}
READERS = {"mean_d": verdict, "skill": skill_verdict}


def skill(row: Optional[dict]) -> str:
    return "n/a" if row is None else s761.skill_text(row)


def _score_rows(cell: dict) -> List[str]:
    means = cell["means"]
    if not means:
        return ["| (no day with a scale) | | | | | |"]
    out = []
    for m in BENCHMARKS:
        out.append(f"| {LABELS[m]} | {means[m]:.3f} | | | | |")
    vs = cell["vs"][BASE]
    out.append(f"| {LABELS[BASE]} | {means[BASE]:.3f} | {skill(vs['B1'])} | {skill(vs['B1p'])} | {skill(vs['B2'])} | |")
    for arm in wc.ARMS:
        name = ARM_KEYS[arm]
        vs = cell["vs"][name]
        out.append(f"| {LABELS[name]} | {means[name]:.3f} | {skill(vs['B1'])} | {skill(vs['B1p'])} | {skill(vs['B2'])} | {skill(vs[BASE])} |")
    return out


HEADER = ["| | mean | skill vs B1 [90%] | skill vs B1' [90%] | skill vs B2 [90%] | skill vs uncalibrated base [90%] |",
          "|---|---|---|---|---|---|"]


def render(r: dict, reading: str = "mean_d") -> str:
    n = r["notes"]
    pooled = r["groups"]["pooled"]["all decision days"]
    out = [
        "# Walk-forward calibration of the predictive quantiles (#1133)", "",
        f"**Hypothesis and step:** H5 (primary goal), step 3, calibration of the predictive law (avenue #809); fix 3 of the three fixes "
        f"ruled on 22 October 2026. **{r['label'].capitalize()}**: development days to {n['last_target']}, no verdict (scoring protocol v1, "
        "#640). Any change to the candidate is Eleonora's decision. Generated by `scripts/walk_calibration_1133.py page` from "
        f"`docs/research/walk-calibration-1133/result.json`, not edited by hand; declared in `{r['declaration']}` before any calibrated score.", "",
        f"Panel digest `{r['panel_sha256'][:8]}…`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business "
        f"days, {r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval; skill is `mean(d) / mean(S(benchmark))` with "
        "`d = S(benchmark) - S(candidate)`, positive favours the candidate. Coverage intervals are 90% stationary-bootstrap "
        f"percentile intervals ({r['reps']:,} resamples). Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); "
        f"the first {n['uncalibrated_decision_days']:,} of the base's {n['base_decision_days']:,} days wait for {wc.MIN_CELLS} past cells at every lead "
        f"and are scored by no row. The calibration is refitted {n['calibration_refits']} times (every {wc.REFIT_EVERY} decision days), "
        "from cells whose target is at or before the refit's anchor.", "",
        "**What this is not.** The base reads no calendar column, so every figure here is provisional under the calendar-first rule "
        "(`docs/research/provisional-calendar-register.md`) and closes no question in either direction. The calendar-aware arm of #1115 is "
        "not on main, so it is not the base. The base is #941's best variant, chosen after seeing 2018-2025. Arms (b), by the floor flag, and (c), "
        "with the upper tail widened, were dropped by Eleonora's ruling on #1142 (option 3): #966 showed the floor flag adds nothing on the "
        "scaled mean reversion. This page is the pooled arm only.", "",
        "Rows: the uncalibrated base; (a) pooled split-conformal recalibration of each level.", ""]
    for metric in METRICS:
        out += [f"## {METRIC_TITLES[metric]}, mean over leads 1 to 5, pooled", ""] + HEADER + _score_rows(pooled[metric]) + [""]
    out += ["## Skill of each row over the uncalibrated base, by lead [90%]", ""]
    for metric in ("grid_crps", "upper_tail_twcrps", "scaled_grid_crps"):
        out += [f"{METRIC_TITLES[metric]}:", "", "| | " + " | ".join(f"h={h}" for h in sp.HORIZONS) + " |", "|---|" + "---|" * len(sp.HORIZONS)]
        for arm in wc.ARMS:
            out.append(f"| {LABELS[ARM_KEYS[arm]]} | " + " | ".join(
                skill(r["groups"]["lead"][f"h={h}"][metric]["vs"][ARM_KEYS[arm]][BASE]) for h in sp.HORIZONS) + " |")
        out.append("")
    for split in ("regime", "pressure_day_type"):
        labels = _ordered(split, r["groups"].get(split, {}))
        for metric in METRICS:
            out += [f"## {METRIC_TITLES[metric]} by {SPLIT_TITLES[split]}", ""]
            for label in labels:
                cell = r["groups"][split][label][metric]
                out += [f"**{label}** ({cell.get('days', 0)} days)", ""] + HEADER + _score_rows(cell) + [""]
    if r["skipped_groups"]:
        out += ["Groups with fewer than %d days are listed and not tested: %s." % (
            MIN_GROUP_DAYS, ", ".join(f"{k} ({v})" for k, v in sorted(r["skipped_groups"].items()))), ""]
    out += ["## Reading under the declared rule", "",
            *READING_RULE[reading], ""]
    for arm in wc.ARMS:
        parts = []
        for split in ("pooled", "regime", "pressure_day_type"):
            for label in _ordered(split, r["groups"].get(split, {})):
                parts.append(f"{label}: {READERS[reading](r['groups'][split][label]['grid_crps']['vs'][ARM_KEYS[arm]][BASE])}")
        out.append(f"- **{LABELS[ARM_KEYS[arm]]}**: " + "; ".join(parts) + ".")
    out.append("")
    out += coverage_section(r)
    out += hit_section(r["hits"])
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
            for m in MODELS:
                cells = []
                for split, label in groups:
                    e = r["groups"][split][label][metric][m]
                    cells.append(f"{e['mean']:.3f}" + (f" [{e['interval'][0]:.3f}, {e['interval'][1]:.3f}]" if (split, label) == ("pooled", "all decision days") else ""))
                out.append(f"| {LABELS[m]} | " + " | ".join(cells) + " |")
            out.append("")
    return out


def hit_section(hits: dict) -> List[str]:
    out = ["## Exceedances and band misses, by lead, under both hit rules", "",
           "Each cell is the rate (nominal in the heading) with the p-values of Kupiec's unconditional coverage test, Christoffersen's "
           "independence test and his conditional coverage test (`repo_model.coverage_tests`). Upper tails: the outcome above q95 / q99; "
           "lower tails: below q05 / q01; a band miss: outside the band. Reporting only: no p-value is a gate. By regime and "
           "pressure-day type, the five leads together with Kupiec's p (the leads' sequences are not joined for the independence tests, which "
           "are per lead in `result.json`).", ""]
    nominal = kinds_and_p()
    for rule in hits["rules"]:
        words = "strictly beyond the quantile / outside the closed band" if rule == "above" else "at or beyond the quantile / outside the open band"
        for kind in hits["kinds"]:
            p = nominal[kind]
            out += [f"### {kind} (nominal {p:.2f}), rule `{rule}` ({words})", "",
                    "Pooled; rate (Kupiec p / independence p / conditional coverage p):", "",
                    "| | " + " | ".join(f"h={h}" for h in sp.HORIZONS) + " |", "|---|" + "---|" * len(sp.HORIZONS)]
            for m in MODELS:
                cells = []
                for h in sp.HORIZONS:
                    e = hits["rows"][m][rule][kind].get(f"h={h}", {}).get("pooled")
                    cells.append("n/a" if e is None else f"{e['rate']:.3f} ({e['kupiec']['p_value']:.3f} / {e['independence']['p_value']:.3f} / {e['conditional']['p_value']:.3f})")
                out.append(f"| {LABELS[m]} | " + " | ".join(cells) + " |")
            out.append("")
            for split, order in (("regime", REGIME_ORDER), ("pressure_day_type", DAYTYPE_ORDER)):
                out += [f"By {SPLIT_TITLES[split]}: rate (Kupiec p).", "",
                        "| | " + " | ".join(order) + " |", "|---|" + "---|" * len(order)]
                for m in MODELS:
                    cells = []
                    for label in order:
                        total = hit_count = 0
                        for h in sp.HORIZONS:
                            e = hits["rows"][m][rule][kind].get(f"h={h}", {}).get(f"{split}/{label}")
                            if e is not None:
                                total, hit_count = total + e["n"], hit_count + e["hits"]
                        cells.append("n/a" if not total else f"{hit_count / total:.3f} ({ct.kupiec([1] * hit_count + [0] * (total - hit_count), p).p_value:.3f})")
                    out.append(f"| {LABELS[m]} | " + " | ".join(cells) + " |")
                out.append("")
    return out


def diagnostics_section(r: dict) -> List[str]:
    refits = r["refits"]
    out = ["## What the calibration did", "",
           "The additive offsets of the pooled arm at level 0.50 and 0.95, over the refits, by lead, in units of the day's 90% width "
           "(positive moves the level up).", "",
           "| lead | cells at the last refit | offset_q50 median | offset_q95 median |", "|---|---|---|---|"]
    for h in sp.HORIZONS:
        q50 = sorted(x["by_lead"][str(h)]["offset_q50"] for x in refits)
        q95 = sorted(x["by_lead"][str(h)]["offset_q95"] for x in refits)
        mid = lambda v: v[len(v) // 2]  # noqa: E731
        out.append(f"| {h} | {refits[-1]['by_lead'][str(h)]['cells']} | {mid(q50):+.3f} | {mid(q95):+.3f} |")
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
    s = sub.add_parser("score", help="walk the base, calibrate it and score the arms")
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
