"""Mean reversion with volatility-scaled residuals, scored (filtered historical simulation; #941, avenue #836; H5 step 3).

A development study, never a verdict. It writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.
Every choice is in `metadata/fhs_scale_941.json`, which this script refuses to read unless it is committed and unchanged.
The variants are `repo_model.spread_mr_fhs`, on the base model `repo_model.spread_mean_reversion` (#686). They are scored
with the scorer of scoring protocol v1 (`repo_model.scoring_protocol`) against unscaled mean reversion, B1 and B2
(`repo_model.protocol_benchmarks`), with the studentized stationary bootstrap of ruling 1 (#739). Scored decision days are
those whose five targets are on or before 2025-12-31; no later day is read and no locked day is scored
(`docs/decisions/lockbox.md`). Nothing here is a verdict (scoring protocol v1, #640).

Measures: grid CRPS and upper-tail twCRPS (by lead and pooled), the Brier score and the reliability slope of P(spread > tau)
at tau = 0, 5 and 10 bp, and the coverage of the 90% and 50% intervals; split by regime and pressure-day type (2021-23 and
quarter-ends called out) and pooled. Then the by-lead hit sequences of q90, q95 and q99 with Kupiec's unconditional
coverage test and Christoffersen's independence and conditional coverage tests (`repo_model.coverage_tests`, #993), for
`gbm_funding` (when its walks are supplied) and for unscaled mean reversion, B1, B2 and each variant. The hit rule
("y > q" or "y >= q") is Eleonora's open question: both are reported.

This is a long run (the walks of `gbm_funding` at five leads, then the scoring). It runs on Eleonora's Mac, not in a cloud
session (`.claude/skills/long-run`). Commands, from a clone of the branch:

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs \\
        --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
    for h in 1 2 3 4 5; do OMP_NUM_THREADS=1 PYTHONPATH=src python3 scripts/spread_distribution_634.py walk \\
        --variant gbm_funding --horizon $h --published PUB.csv --panel PUB.csv --output WALKS/gbm_funding_h$h.json; done
    PYTHONPATH=src python3 scripts/fhs_scale_941.py score --panel PUB.csv --walks WALKS \\
        --output docs/research/fhs-scale-941/result.json
    PYTHONPATH=src python3 scripts/fhs_scale_941.py page \\
        --score docs/research/fhs-scale-941/result.json --output docs/research/fhs-scale-941-result.md

`score` scores every piece that exists: a `gbm_funding` lead without its walk file is left out of the hit sequences, and
without `--walks` the `gbm_funding` rows are absent (the rest of the study does not need them). Stdlib only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import multiprocessing
import random
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


from repo_model import coverage_tests as ct  # noqa: E402
from repo_model import lockbox, metrics  # noqa: E402
from repo_model import protocol_benchmarks as pb, reliability_regimes as rr, scoring_protocol as sp  # noqa: E402
from repo_model import spread_mean_reversion as smr, spread_mr_fhs as fhs  # noqa: E402
from repo_model.baseline import panel_sha256  # noqa: E402
from repo_model.data import exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.splits import SplitError  # noqa: E402

s686 = _load("spread_mean_reversion_686")
s761 = _load("spread_mr_variants_761")

DECLARATION = REPO / "metadata" / "fhs_scale_941.json"
SPLITS = s686.SPLITS
SOURCES = s686.SOURCES
SEED = 941
LAST_DAY = s686.LAST_DAY
DECISION_TIME = s686.DECISION_TIME
MIN_GROUP_DAYS = s686.MIN_GROUP_DAYS
TAUS: Tuple[float, ...] = (0.0, 5.0, 10.0)
HIT_LEVELS: Tuple[float, ...] = (0.90, 0.95, 0.99)
GBM = "gbm_funding"
REFERENCE = fhs.REFERENCE
BENCHMARKS: Tuple[str, ...] = ("B1", "B2")
VARIANT_NAMES: Tuple[str, ...] = tuple(v.name for v in fhs.VARIANTS)
CANDIDATES: Tuple[str, ...] = (REFERENCE,) + VARIANT_NAMES
MODELS: Tuple[str, ...] = BENCHMARKS + CANDIDATES
SCORE_METRICS: Tuple[str, ...] = ("grid_crps", "upper_tail_twcrps") + tuple(f"brier_{tau:g}" for tau in TAUS)
COVERAGE_METRICS: Tuple[str, ...] = ("coverage_90", "coverage_50")
#: Grid indices of the interval ends.
IDX = {level: sp.GRID.index(level) for level in (0.05, 0.25, 0.75, 0.95)}
#: A cell sequence holds five leads per decision day, so ten business days is fifty cells.
CELL_BLOCK = 5.0 * sp.BLOCK_LENGTH


# -- the declaration -----------------------------------------------------------------------------------------------


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    return s686.committed_declaration(path)


# -- the frame -----------------------------------------------------------------------------------------------------


def build_frame(panel, splits, registry, declaration, first: Optional[date] = None):
    """The decision days with a forecast of every model, whose five targets are scored days.

    `first` starts the walk later than the declared study does; it exists for the test of this script and the declared
    run never passes it.
    """

    frame = s686.Frame(panel, splits, registry, declaration)
    candidate_days = [
        day for i, day in enumerate(frame.dates)
        if i + max(sp.HORIZONS) < len(panel) and frame.dates[i + max(sp.HORIZONS)] <= LAST_DAY
        and (first is None or day >= first)
    ]
    s686.require_scored_days(candidate_days, LAST_DAY)
    walk = fhs.walk(panel, candidate_days, fhs.VARIANTS, **frame.settings)
    b1, b2, dropped = {}, {}, []
    for day in walk.forecasts[REFERENCE]:
        index = frame.position[day]
        try:
            b1[day] = pb.b1_forecast(panel, index, registry=registry, decision_time=DECISION_TIME)
            b2[day] = pb.b2_forecast(panel, index, registry=registry, decision_time=DECISION_TIME, splits=splits)
        except (sp.ProtocolError, SplitError):
            dropped.append(day)
    days = [day for day in walk.forecasts[REFERENCE] if day in b1]
    frame.days = days
    frame.forecasts = {"B1": b1, "B2": b2}
    for name in CANDIDATES:
        frame.forecasts[name] = {day: walk.forecasts[name][day] for day in days}
    notes = {
        "decision_days_offered": len(candidate_days),
        "candidate_skipped_for_history": len(walk.skipped),
        "benchmark_missing": [d.isoformat() for d in dropped],
        "scored_decision_days": len(days),
        "first": days[0].isoformat(), "last": days[-1].isoformat(),
        "last_target": frame.target(days[-1], max(sp.HORIZONS)).isoformat(),
        "refits": len(walk.fits),
    }
    return frame, notes, walk


# -- the cells -----------------------------------------------------------------------------------------------------


def cell_values(frame, model: str) -> Tuple[Dict[str, Dict[Tuple[date, int], float]], Dict[float, Dict[Tuple[date, int], Tuple[float, float]]]]:
    """Every measure of every (decision day, lead) cell of `model`, and its tail probabilities with their events.

    Returns `(values, tails)`: `values[metric][(day, lead)]` for `SCORE_METRICS` and `COVERAGE_METRICS`, and
    `tails[tau][(day, lead)] = (P(spread > tau), event)`.
    """

    cells = {(d, h): frame.target(d, h) for d in frame.days for h in sp.HORIZONS}
    s686.require_scored_days(set(d for d, _ in cells) | set(cells.values()), LAST_DAY)
    forecasts = frame.forecasts[model]
    values: Dict[str, Dict[Tuple[date, int], float]] = {m: {} for m in SCORE_METRICS + COVERAGE_METRICS}
    tails: Dict[float, Dict[Tuple[date, int], Tuple[float, float]]] = {tau: {} for tau in TAUS}
    for (d, h), t in cells.items():
        q, y = forecasts[d][h], frame.outcome[t]
        values["grid_crps"][(d, h)] = sp.grid_crps(q, y)
        values["upper_tail_twcrps"][(d, h)] = sp.upper_tail_twcrps(q, y)
        for tau in TAUS:
            p, e = smr.exceedance(q, tau), 1.0 if exceeds_bp(y, tau) else 0.0
            tails[tau][(d, h)] = (p, e)
            values[f"brier_{tau:g}"][(d, h)] = (p - e) ** 2
        values["coverage_90"][(d, h)] = 1.0 if q[IDX[0.05]] <= y <= q[IDX[0.95]] else 0.0
        values["coverage_50"][(d, h)] = 1.0 if q[IDX[0.25]] <= y <= q[IDX[0.75]] else 0.0
    return values, tails


def groups_of(frame) -> List[Tuple[str, str, str, List[date]]]:
    """`(split, label, grain, members)`: pooled, by lead, by regime and by pressure-day type of the target day."""

    out: List[Tuple[str, str, str, List[date]]] = [("pooled", "all decision days", "decision", list(frame.days))]
    for h in sp.HORIZONS:
        out.append(("lead", f"h={h}", f"lead{h}", list(frame.days)))
    targets = sorted({frame.target(d, h) for d in frame.days for h in sp.HORIZONS})
    for split, label_of in (("regime", frame.regime), ("pressure_day_type", frame.day_type)):
        by_label: Dict[str, List[date]] = {}
        for t in targets:
            by_label.setdefault(label_of(t), []).append(t)
        for label, members in by_label.items():
            out.append((split, label, "target", members))
    return out


def series_of(frame, cells: Mapping[str, Mapping[Tuple[date, int], float]], grain: str) -> Dict[date, float]:
    if grain == "decision":
        return s686.by_decision(cells)
    if grain == "target":
        return s686.by_target(frame, cells)
    return s686.by_lead(cells, int(grain[4:]))


# -- the tests, in parallel ----------------------------------------------------------------------------------------

_STATE: Dict = {}


def mean_interval(values: Sequence[float], *, seed: int, reps: int) -> List[float]:
    """The 90% stationary-bootstrap percentile interval of the mean of an ordered series."""

    n = len(values)
    return list(metrics.stationary_bootstrap_interval(
        lambda idx: sum(values[i] for i in idx) / len(idx), n, block_length=sp.BLOCK_LENGTH, seed=seed, replications=reps))


def difference_interval(a: Sequence[float], b: Sequence[float], *, seed: int, reps: int) -> List[float]:
    """The same interval for mean(a - b), the two series resampled together."""

    n = len(a)
    return list(metrics.stationary_bootstrap_interval(
        lambda idx: sum(a[i] - b[i] for i in idx) / len(idx), n, block_length=sp.BLOCK_LENGTH, seed=seed, replications=reps))


def _pairs_task(job):
    split, label, grain, metric, candidate, members = job
    series = _STATE["series"][(grain, metric)]
    names = list(BENCHMARKS) + ([REFERENCE] if candidate != REFERENCE else [])
    return (split, label, metric, candidate), s761.run_pairs(
        {n: series[n] for n in names}, series[candidate], members, seed=SEED, draws=_STATE["draws"])


def _coverage_task(job):
    split, label, grain, metric, members = job
    series = _STATE["series"][(grain, metric)]
    ordered = sorted(members)
    reps = _STATE["reps"]
    out = {}
    for model in CANDIDATES:
        values = [series[model][d] for d in ordered]
        entry = {"mean": sum(values) / len(values), "interval": mean_interval(values, seed=SEED, reps=reps)}
        if model != REFERENCE:
            ref = [series[REFERENCE][d] for d in ordered]
            entry["difference_from_reference"] = sum(a - b for a, b in zip(values, ref)) / len(values)
            entry["difference_interval"] = difference_interval(values, ref, seed=SEED, reps=reps)
        out[model] = entry
    for model in BENCHMARKS:
        values = [series[model][d] for d in ordered]
        out[model] = {"mean": sum(values) / len(values), "interval": mean_interval(values, seed=SEED, reps=reps)}
    return (split, label, metric), out


def _slope_task(job):
    split, label, tau, cell_keys = job
    tails = _STATE["tails"]
    reps = _STATE["slope_reps"]
    keys = sorted(cell_keys)
    data = {m: ([tails[m][tau][k][0] for k in keys], [int(tails[m][tau][k][1]) for k in keys]) for m in MODELS}
    n = len(keys)
    out = {}
    points = {}
    for m, (p, e) in data.items():
        line = rr.fit(p, e)
        points[m] = line
        out[m] = {"cells": n, "events": sum(e), "predicted": sum(p) / n, "realised": sum(e) / n,
                  "slope": None if line is None else line.slope, "intercept": None if line is None else line.intercept}
    rng = random.Random(SEED)
    slopes: Dict[str, List[float]] = {m: [] for m in MODELS}
    diffs: Dict[str, List[float]] = {m: [] for m in MODELS if m != REFERENCE}
    undefined = {m: 0 for m in MODELS}
    if sum(data[REFERENCE][1]) >= 5 and n - sum(data[REFERENCE][1]) >= 5:
        for _ in range(reps):
            idx = metrics.stationary_bootstrap_indices(n, CELL_BLOCK, rng)
            drawn = {}
            for m, (p, e) in data.items():
                line = rr.fit([p[i] for i in idx], [e[i] for i in idx])
                if line is None:
                    undefined[m] += 1
                else:
                    slopes[m].append(line.slope)
                    drawn[m] = line.slope
            for m in diffs:
                if m in drawn and REFERENCE in drawn:
                    diffs[m].append(drawn[m] - drawn[REFERENCE])
        for m in MODELS:
            if undefined[m] <= rr.MAX_UNDEFINED_SHARE * reps and slopes[m]:
                ordered = sorted(slopes[m])
                out[m]["slope_interval"] = [metrics._quantile(ordered, 0.05), metrics._quantile(ordered, 0.95)]
        for m, values in diffs.items():
            if undefined[m] <= rr.MAX_UNDEFINED_SHARE * reps and undefined[REFERENCE] <= rr.MAX_UNDEFINED_SHARE * reps and values:
                ordered = sorted(values)
                out[m]["slope_difference_interval"] = [metrics._quantile(ordered, 0.05), metrics._quantile(ordered, 0.95)]
                if points[m] is not None and points[REFERENCE] is not None:
                    out[m]["slope_difference"] = points[m].slope - points[REFERENCE].slope
    return (split, label, tau), out


def _dispatch(job):
    kind, payload = job
    return kind, {"pairs": _pairs_task, "coverage": _coverage_task, "slope": _slope_task}[kind](payload)


def run_jobs(jobs, workers: int):
    context = multiprocessing.get_context("fork")
    with context.Pool(workers) as pool:
        return pool.map(_dispatch, jobs, chunksize=1)


# -- the hit sequences ---------------------------------------------------------------------------------------------


def read_gbm(directory: Optional[Path]) -> Dict[int, Dict[date, List[float]]]:
    """`gbm_funding`'s walks that exist in `directory`, `{lead: {target day: 23 quantiles}}`; a missing lead is left out."""

    out: Dict[int, Dict[date, List[float]]] = {}
    if directory is None:
        return out
    for h in sp.HORIZONS:
        path = directory / f"{GBM}_h{h}.json"
        if not path.exists():
            continue
        document = json.loads(path.read_text(encoding="utf-8"))
        if document["horizon"] != h or document["variant"] != GBM:
            raise ValueError(f"{path.name} is not the walk of {GBM} at lead {h}")
        if len(document["levels"]) != len(sp.GRID):
            raise ValueError(f"{path.name} carries {len(document['levels'])} levels, not the grid's {len(sp.GRID)}")
        out[h] = {
            date.fromisoformat(day): [float(v) for v in q]
            for day, q in document["laws"].items() if q is not None and date.fromisoformat(day) <= LAST_DAY
        }
    return out


def coverage_row(sequence: Sequence[int], p: float, *, independence: bool) -> dict:
    """Kupiec, and (where the days are consecutive) Christoffersen independence and conditional coverage."""

    kupiec = ct.kupiec(sequence, p)
    row = {"n": kupiec.n, "hits": kupiec.hits, "rate": kupiec.hits / kupiec.n,
           "kupiec": {"statistic": kupiec.statistic, "p_value": kupiec.p_value}, "independence": None, "conditional": None}
    if independence:
        ind = ct.christoffersen_independence(sequence)
        cc = ct.christoffersen_conditional_coverage(sequence, p)
        row["independence"] = {"statistic": ind.statistic, "p_value": ind.p_value}
        row["conditional"] = {"statistic": cc.statistic, "p_value": cc.p_value}
    return row


def hit_tables(frame, gbm: Mapping[int, Mapping[date, Sequence[float]]]) -> dict:
    """Per model, hit rule, level and lead, the three coverage tests, pooled, by regime and by pressure-day type.

    When `gbm` holds a lead, every model is read on the decision days whose target has a `gbm_funding` law at that lead.
    A regime is a run of consecutive days, so it gets all three tests; the days of a pressure-day type are not
    consecutive, so it gets Kupiec's only. A group of fewer than `MIN_GROUP_DAYS` days is not tested.
    """

    laws = {name: frame.forecasts[name] for name in MODELS}
    out: dict = {"levels": list(HIT_LEVELS), "rules": list(ct.HIT_RULES), "gbm_leads": sorted(gbm), "rows": {}}
    for h in sp.HORIZONS:
        days = [d for d in frame.days if h not in gbm or frame.target(d, h) in gbm[h]]
        targets = [frame.target(d, h) for d in days]
        outcomes = [frame.outcome[t] for t in targets]
        source = dict(laws)
        if h in gbm:
            source[GBM] = {d: {h: gbm[h][frame.target(d, h)]} for d in days}
        for name, by_day in source.items():
            for level in HIT_LEVELS:
                column = sp.GRID.index(level)
                quantiles = [by_day[d][h][column] for d in days]
                for rule in ct.HIT_RULES:
                    sequence = ct.hit_sequence(outcomes, quantiles, rule=rule)
                    p = 1.0 - level
                    cell: dict = {}
                    if len(sequence) >= MIN_GROUP_DAYS:
                        cell["pooled"] = coverage_row(sequence, p, independence=True)
                    for split, label_of, independence in (("regime", frame.regime, True), ("pressure_day_type", frame.day_type, False)):
                        members: Dict[str, List[int]] = {}
                        for i, t in enumerate(targets):
                            members.setdefault(label_of(t), []).append(i)
                        for label, rows in sorted(members.items()):
                            if len(rows) >= MIN_GROUP_DAYS:
                                cell[f"{split}/{label}"] = coverage_row([sequence[i] for i in rows], p, independence=independence)
                    out["rows"].setdefault(name, {}).setdefault(rule, {}).setdefault(f"q{round(level * 100)}", {})[f"h={h}"] = cell
    return out


# -- the report ----------------------------------------------------------------------------------------------------


def score(args) -> int:
    declaration = committed_declaration()
    panel_path = Path(args.panel)
    panel = load_daily_panel(panel_path)
    splits = load_split_declaration(SPLITS)
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    frame, notes, walk = build_frame(panel, splits, registry, declaration, args.first)
    days = frame.days

    base = smr.walk(panel, list(walk.forecasts[REFERENCE]), registry=registry, decision_time=DECISION_TIME, splits=splits)
    if any(base.forecasts[d] != frame.forecasts[REFERENCE][d] for d in days):
        raise SystemExit("the reference differs from spread_mean_reversion.walk")

    cells: Dict[str, Dict[str, Dict]] = {}
    tails: Dict[str, Dict] = {}
    for model in MODELS:
        cells[model], tails[model] = cell_values(frame, model)
    for model in MODELS:
        official = sp.day_scores(frame.forecasts[model], frame.outcome, frame.dates, score=sp.grid_crps)
        mine = s686.by_decision(cells[model]["grid_crps"])
        if set(official) != set(mine) or any(abs(official[d] - mine[d]) > 1e-9 for d in mine):
            raise SystemExit(f"grid CRPS of {model}: the cell means differ from scoring_protocol.day_scores")

    groups = groups_of(frame)
    series: Dict[Tuple[str, str], Dict[str, Dict[date, float]]] = {}
    for _split, _label, grain, _members in groups:
        for metric in SCORE_METRICS + COVERAGE_METRICS:
            if (grain, metric) not in series:
                series[(grain, metric)] = {m: series_of(frame, cells[m][metric], grain) for m in MODELS}
    _STATE.update(series=series, draws=args.draws, reps=args.reps, tails=tails, slope_reps=args.slope_reps)

    jobs, skipped = [], {}
    slope_groups: Dict[Tuple[str, str], set] = {("pooled", "all cells"): {(d, h) for d in days for h in sp.HORIZONS}}
    for split, label, grain, members in groups:
        if len(members) < MIN_GROUP_DAYS:
            skipped[f"{split}/{label}"] = len(members)
            continue
        for metric in SCORE_METRICS:
            for candidate in CANDIDATES:
                jobs.append(("pairs", (split, label, grain, metric, candidate, tuple(members))))
        for metric in COVERAGE_METRICS:
            jobs.append(("coverage", (split, label, grain, metric, tuple(members))))
        if split in ("regime", "pressure_day_type"):
            member_set = set(members)
            slope_groups[(split, label)] = {(d, h) for d in days for h in sp.HORIZONS if frame.target(d, h) in member_set}
    for (split, label), keys in slope_groups.items():
        for tau in TAUS:
            jobs.append(("slope", (split, label, tau, tuple(sorted(keys)))))
    done = run_jobs(jobs, args.workers)

    by_key: Dict[Tuple[str, str], Tuple[str, List[date]]] = {(s_, l_): (g, m) for s_, l_, g, m in groups}
    result: dict = {
        "issue": 941, "declaration": str(DECLARATION.relative_to(REPO)), "panel_sha256": panel_sha256(panel_path),
        "subset_from": None if args.first is None else args.first.isoformat(),
        "label": "development, not a verdict", "seed": SEED, "draws": args.draws, "reps": args.reps,
        "slope_reps": args.slope_reps, "notes": notes, "models": list(MODELS), "variants": [
            {"name": v.name, "estimator": v.estimator, "window_rows": v.window, "floor_bp": v.floor} for v in fhs.VARIANTS],
        "refits": [{"fitted_on": day.isoformat(), "phi": fit.phi,
                    "pairs_left_out": {name: {str(h): walk.scaled_fits[day][name].left_out[h] for h in sp.HORIZONS}
                                       for name in VARIANT_NAMES}} for day, fit in sorted(walk.fits.items())],
        "groups": {}, "calibration": {}, "skipped_groups": skipped,
    }
    for kind, (ident, payload) in done:
        if kind == "slope":
            split, label, tau = ident
            result["calibration"].setdefault(f"{tau:g}", {}).setdefault(split, {})[label] = payload
            continue
        split, label, metric = ident[:3]
        entry = result["groups"].setdefault(split, {}).setdefault(label, {"days": len(by_key[(split, label)][1])})
        if kind == "pairs":
            entry.setdefault(metric, {"means": {}, "vs": {}})["vs"][ident[3]] = payload
        else:
            entry[metric] = payload
    for split, labels in result["groups"].items():
        for label, entry in labels.items():
            grain, members = by_key[(split, label)]
            for metric in SCORE_METRICS:
                ser = series[(grain, metric)]
                entry[metric]["means"] = {m: sum(ser[m][d] for d in members) / len(members) for m in MODELS}
    result["hits"] = hit_tables(frame, read_gbm(Path(args.walks) if args.walks else None))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


# -- the page ------------------------------------------------------------------------------------------------------

LABELS = {"B1": "B1", "B2": "B2", REFERENCE: "mean reversion, unscaled (#686)"}
LABELS.update({v.name: f"{v.estimator} window {v.window} floor {v.floor:g}" for v in fhs.VARIANTS})
LABELS[GBM] = "gbm_funding"
REGIME_ORDER = ["2018-19", "2020", "2021-23", "2024", "2025-26"]
DAYTYPE_ORDER = ["quarter_end", "month_end", "tax_date", "ordinary"]
SPLIT_TITLES = {"regime": "regime (target day)", "pressure_day_type": "pressure-day type (target day)"}
METRIC_TITLES = {"grid_crps": "grid CRPS", "upper_tail_twcrps": "upper-tail twCRPS"}


def _ordered(split: str, labels) -> List[str]:
    order = {"regime": REGIME_ORDER, "pressure_day_type": DAYTYPE_ORDER}.get(split, [])
    return [l for l in order if l in labels] + sorted(l for l in labels if l not in order)


def verdict(row: dict) -> str:
    """The declared reading of one skill row against unscaled mean reversion: gain, loss or undecided."""

    if "undefined" in row:
        return "undecided"
    lo, hi = row["skill_interval"]
    return "gain" if lo > 0.0 else "loss" if hi < 0.0 else "undecided"


def _score_rows(cell: dict) -> List[str]:
    out = []
    means = cell["means"]
    for m in BENCHMARKS:
        out.append(f"| {LABELS[m]} | {means[m]:.3f} | | | |")
    ref = cell["vs"][REFERENCE]
    out.append(f"| {LABELS[REFERENCE]} | {means[REFERENCE]:.3f} | {s761.skill_text(ref['B1'])} | {s761.skill_text(ref['B2'])} | |")
    for name in VARIANT_NAMES:
        vs = cell["vs"][name]
        out.append(f"| {LABELS[name]} | {means[name]:.3f} | {s761.skill_text(vs['B1'])} | {s761.skill_text(vs['B2'])} | "
                   f"{s761.skill_text(vs[REFERENCE])} |")
    return out


HEADER = ["| | mean | skill vs B1 [90%] | skill vs B2 [90%] | skill vs unscaled MR [90%] |", "|---|---|---|---|---|"]


def render(r: dict) -> str:
    n = r["notes"]
    pooled = r["groups"]["pooled"]["all decision days"]
    out = [
        "# Volatility-scaled residuals for mean reversion: filtered historical simulation (#941)", "",
        f"**Hypothesis and step:** H5 (primary goal), step 3, calibration of the predictive law, in particular the upper tail "
        f"(avenue #836). **{r['label'].capitalize()}**: development days to {n['last_target']}, no verdict (scoring protocol v1, "
        "#640). Any change to the candidate is Eleonora's decision. Generated by `scripts/fhs_scale_941.py page` from "
        f"`docs/research/fhs-scale-941/result.json`, not edited by hand; declared in `{r['declaration']}` before any number.", "",
        f"Panel digest `{r['panel_sha256'][:8]}…`. Studentized stationary bootstrap (ruling 1), mean block {sp.BLOCK_LENGTH} business "
        f"days, {r['draws']:,} draws, seed {r['seed']}, two-sided 90% interval; skill is `mean(d) / mean(S(benchmark))` with "
        "`d = S(benchmark) - S(candidate)`, positive favours the candidate. Calibration intervals are 90% stationary-bootstrap "
        f"percentile intervals ({r['reps']:,} resamples; {r['slope_reps']:,} for the reliability slope, over cells in blocks of "
        f"{int(CELL_BLOCK)}). Scored decision days: {n['scored_decision_days']:,} ({n['first']} to {n['last']}); the fit is "
        f"renewed {n['refits']} times.", "",
        "**What this is not.** Mean reversion and its scaled variants read no calendar column, so a result here is provisional "
        "under the calendar-first rule (`docs/research/provisional-calendar-register.md`) and closes no question in either "
        "direction. The variants are chosen after seeing 2018-2025 (avenue #836 quotes numbers from that window).", ""]
    for metric in ("grid_crps", "upper_tail_twcrps"):
        out += [f"## {METRIC_TITLES[metric]}, mean over leads 1 to 5, pooled (bp)", ""] + HEADER + _score_rows(pooled[metric]) + [""]
    out += ["## Grid CRPS and twCRPS by lead: skill of each variant over unscaled mean reversion [90%]", ""]
    for metric in ("grid_crps", "upper_tail_twcrps"):
        out += [f"{METRIC_TITLES[metric]}:", "", "| | " + " | ".join(f"h={h}" for h in sp.HORIZONS) + " |", "|---|" + "---|" * len(sp.HORIZONS)]
        for name in VARIANT_NAMES:
            out.append(f"| {LABELS[name]} | " + " | ".join(
                s761.skill_text(r["groups"]["lead"][f"h={h}"][metric]["vs"][name][REFERENCE]) for h in sp.HORIZONS) + " |")
        out.append("")
    for split in ("regime", "pressure_day_type"):
        labels = _ordered(split, r["groups"].get(split, {}))
        for metric in ("grid_crps", "upper_tail_twcrps"):
            out += [f"## {METRIC_TITLES[metric]} by {SPLIT_TITLES[split]}", ""]
            for label in labels:
                cell = r["groups"][split][label][metric]
                days = r["groups"][split][label]["days"]
                out += [f"**{label}** ({days} days)", ""] + HEADER + _score_rows(cell) + [""]
    if r["skipped_groups"]:
        out += ["Groups with fewer than %d days are listed and not tested: %s." % (
            MIN_GROUP_DAYS, ", ".join(f"{k} ({v})" for k, v in sorted(r["skipped_groups"].items()))), ""]
    out += ["## Reading under the declared rule", "",
            "A gain (loss) is a grid-CRPS skill over unscaled mean reversion whose 90% interval is above (below) zero; otherwise undecided.", ""]
    for name in VARIANT_NAMES:
        parts = []
        for split in ("pooled", "regime", "pressure_day_type"):
            for label in _ordered(split, r["groups"].get(split, {})):
                row = r["groups"][split][label]["grid_crps"]["vs"][name][REFERENCE]
                parts.append(f"{label}: {verdict(row)}")
        out.append(f"- **{LABELS[name]}**: " + "; ".join(parts) + ".")
    out.append("")
    out += ["## Exceedance calibration: P(spread > tau)", "",
            "Brier score (mean over cells, lower is better), then the reliability slope of the logistic fit of the event on logit(p) "
            "(1 for a reliable forecast) with its 90% interval and, for the variants, the slope less unscaled mean reversion's with its "
            "interval from the same resamples. A cell with no event or a constant forecast has no slope.", ""]
    for tau in sorted(r["calibration"], key=float):
        out += [f"### tau = +{tau} bp", ""]
        out += ["Brier score, skill over unscaled mean reversion [90%]:", "", "| | pooled | " + " | ".join(
            f"{l}" for sp_ in ("regime", "pressure_day_type") for l in _ordered(sp_, r["groups"].get(sp_, {}))) + " |",
            "|---|---|" + "---|" * sum(len(r["groups"].get(sp_, {})) for sp_ in ("regime", "pressure_day_type"))]
        for name in VARIANT_NAMES:
            cells = [r["groups"]["pooled"]["all decision days"][f"brier_{tau}"]["vs"][name][REFERENCE]]
            for split in ("regime", "pressure_day_type"):
                cells += [r["groups"][split][l][f"brier_{tau}"]["vs"][name][REFERENCE] for l in _ordered(split, r["groups"].get(split, {}))]
            out.append(f"| {LABELS[name]} | " + " | ".join(s761.skill_text(c) for c in cells) + " |")
        out.append("")
        slope = r["calibration"][tau]
        columns = [("pooled", "all cells")] + [(sp_, l) for sp_ in ("regime", "pressure_day_type") for l in _ordered(sp_, slope.get(sp_, {}))]
        out += ["Reliability slope [90%] (the predicted and realised shares and the intercept are in `result.json`):", "",
                "| | " + " | ".join(l for _, l in columns) + " |", "|---|" + "---|" * len(columns)]
        for m in MODELS:
            cells = []
            for split, label in columns:
                e = slope[split][label][m]
                if e["slope"] is None:
                    cells.append("undefined")
                elif "slope_interval" in e:
                    cells.append(f"{e['slope']:.2f} [{e['slope_interval'][0]:.2f}, {e['slope_interval'][1]:.2f}]")
                else:
                    cells.append(f"{e['slope']:.2f}")
            out.append(f"| {LABELS[m]} | " + " | ".join(cells) + " |")
        out.append("")
    out += ["## Interval coverage", "",
            "Share of (decision day, lead) cells whose outcome is inside the interval, closed at both ends, with a 90% interval and, for "
            "the variants, the difference from unscaled mean reversion. Nominal 0.90 and 0.50.", ""]
    for metric, title in (("coverage_90", "90% interval (q05 to q95)"), ("coverage_50", "50% interval (q25 to q75)")):
        out += [f"**{title}**", ""]
        groups = [("pooled", "all decision days")] + [(s_, l) for s_ in ("regime", "pressure_day_type") for l in _ordered(s_, r["groups"].get(s_, {}))]
        out += ["| | " + " | ".join(l for _, l in groups) + " |", "|---|" + "---|" * len(groups)]
        for m in MODELS:
            cells = []
            for split, label in groups:
                e = r["groups"][split][label][metric][m]
                cells.append(f"{e['mean']:.3f}")
            out.append(f"| {LABELS[m]} | " + " | ".join(cells) + " |")
        out.append("")
        out += ["Difference from unscaled mean reversion [90%]:", "", "| | " + " | ".join(l for _, l in groups) + " |", "|---|" + "---|" * len(groups)]
        for m in VARIANT_NAMES:
            cells = []
            for split, label in groups:
                e = r["groups"][split][label][metric][m]
                lo, hi = e["difference_interval"]
                cells.append(f"{e['difference_from_reference']:+.3f} [{lo:+.3f}, {hi:+.3f}]")
            out.append(f"| {LABELS[m]} | " + " | ".join(cells) + " |")
        out.append("")
    out += hit_section(r["hits"])
    return "\n".join(out) + "\n"


def hit_section(hits: dict) -> List[str]:
    models = [m for m in (GBM,) + MODELS if m in hits["rows"]]
    out = ["## Hit sequences of q90, q95 and q99, by lead (ruling of 19 October 2026 on #941)", "",
           "The hit is the outcome beyond the model's quantile. **The hit rule is an open question and Eleonora's** (#993): "
           "whole-bp outcomes tie with a quantile, so \"beyond\" is `y > q` or `y >= q`, and both are reported. Each cell is the hit rate "
           "(nominal is 1 minus the level) with the p-values of Kupiec's unconditional coverage test, Christoffersen's independence test and "
           "his conditional coverage test (`repo_model.coverage_tests`). Reporting only: no p-value is a gate. "
           + ("`gbm_funding` is read at lead(s) " + ", ".join(map(str, hits["gbm_leads"])) + ", and every model on the decision days that "
              "lead has a `gbm_funding` law for." if hits["gbm_leads"] else "`gbm_funding`'s walks were not supplied, so it has no row."), ""]
    for rule in hits["rules"]:
        for level in (f"q{round(l * 100)}" for l in hits["levels"]):
            out += [f"### {level}, hit when {'y > q' if rule == 'above' else 'y >= q'}", "",
                    "Pooled; hit rate (Kupiec p / independence p / conditional coverage p):", "",
                    "| | " + " | ".join(f"h={h}" for h in sp.HORIZONS) + " |", "|---|" + "---|" * len(sp.HORIZONS)]
            for m in models:
                cells = []
                for h in sp.HORIZONS:
                    e = hits["rows"][m][rule][level].get(f"h={h}", {}).get("pooled")
                    cells.append("n/a" if e is None else f"{e['rate']:.3f} ({e['kupiec']['p_value']:.3f} / {e['independence']['p_value']:.3f} / {e['conditional']['p_value']:.3f})")
                out.append(f"| {LABELS[m]} | " + " | ".join(cells) + " |")
            out.append("")
            p = 1.0 - float(level[1:]) / 100.0
            for split, order in (("regime", REGIME_ORDER), ("pressure_day_type", DAYTYPE_ORDER)):
                out += [f"By {SPLIT_TITLES[split]}, the five leads together: hit rate (Kupiec p). The sequences of the leads are not joined "
                        "for the independence tests, which are per lead in `result.json`.", "",
                        "| | " + " | ".join(order) + " |", "|---|" + "---|" * len(order)]
                for m in models:
                    cells = []
                    for label in order:
                        n = x = 0
                        for h in sp.HORIZONS:
                            e = hits["rows"][m][rule][level].get(f"h={h}", {}).get(f"{split}/{label}")
                            if e is not None:
                                n, x = n + e["n"], x + e["hits"]
                        cells.append("n/a" if not n else f"{x / n:.3f} ({ct.kupiec([1] * x + [0] * (n - x), p).p_value:.3f})")
                    out.append(f"| {LABELS[m]} | " + " | ".join(cells) + " |")
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
    s = sub.add_parser("score", help="score the variants and the hit sequences")
    s.add_argument("--panel", required=True)
    s.add_argument("--walks", help="a directory holding gbm_funding_h<lead>.json (scripts/spread_distribution_634.py walk)")
    s.add_argument("--output", required=True)
    s.add_argument("--draws", type=int, default=sp.DRAWS)
    s.add_argument("--reps", type=int, default=2000, help="bootstrap resamples of a coverage interval")
    s.add_argument("--slope-reps", type=int, default=1000, help="bootstrap resamples of a reliability slope")
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
