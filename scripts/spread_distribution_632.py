"""Forecast the spread, then apply the +5 bp threshold (#632): scoring and report.

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.
Every choice is in `metadata/spread_distribution_632.json`, which this script refuses to read unless it is committed and
unchanged, and in the two candidate files in `metadata/pressure_judge/candidates/`. The model is
`ml.pressure_spread_distribution_exceedance`: gradient-boosted quantiles of `spread_bps` at a declared grid, read as
P(spread > tau). Scored days are 2018-06-29 to 2025-12-31; no day of the 2026 tiers is read (`docs/decisions/lockbox.md`;
`require_unlocked`). A pass is not a confirmation (ruling on #567).

    # AUG2.csv, AUG2D.csv, OUT/{bench,risk,ql,both,dist,iorb}_h?.json: the commands of scripts/satiation_distance_598.py,
    # scripts/iorb_every_day_579.py and scripts/every_day_conditioning_601.py (cap), at h = 1 to 5
    for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/spread_distribution_632.py run --panel AUG2D.csv --published PUBLISHED.csv \\
        --horizon $h --output OUT/sd_h$h.json
    for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/spread_distribution_632.py refs --both OUT/both_h$h.json --dist OUT/dist_h$h.json \\
        --cap OUT/cap_h$h.json --output OUT/refs_h$h.json
    # step 1, before any judge score: the distribution against as-of persistence and the published distribution
    PYTHONPATH=src python3 scripts/spread_distribution_632.py distribution --panel PUBLISHED.csv 'OUT/sd_h{h}.json' \\
        --output OUT/distribution.json --markdown OUT/distribution.md
    for r in weighted unweighted: PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule $r \\
        --output OUT/judge_$r.json --markdown OUT/judge_$r.md OUT/bench_h?.json OUT/risk_h?.json OUT/ql_h?.json OUT/refs_h?.json OUT/sd_h?.json
    PYTHONPATH=src python3 scripts/spread_distribution_632.py compare --panel PUBLISHED.csv --bench 'OUT/bench_h{h}.json' \\
        --risk 'OUT/risk_h{h}.json' --reference 'OUT/ql_h{h}.json' --parents 'OUT/refs_h{h}.json' --rows 'OUT/sd_h{h}.json' \\
        --output OUT/compare.json --markdown OUT/compare.md
    PYTHONPATH=src python3 scripts/spread_distribution_632.py ordinary --panel PUBLISHED.csv --bench 'OUT/bench_h{h}.json' \\
        --risk 'OUT/risk_h{h}.json' --reference 'OUT/ql_h{h}.json' --parents 'OUT/refs_h{h}.json' --rows 'OUT/sd_h{h}.json' --output OUT/ordinary.json
    PYTHONPATH=src python3 scripts/spread_distribution_632.py report --compare OUT/compare.json --distribution OUT/distribution.json \\
        --ordinary OUT/ordinary.json --output OUT/report.md

`run` scores the two variants of the declaration, walk-forward at +5 and +10 bp on the shared fold grid, and keeps each day's
fitted quantiles. `refs` merges the references into one file per lead: the passer, the row of #598 and #606, and the row of
#601 that passes tier 1 under the weighted rule. `distribution` is step 1. `compare` is the judge's own cut-offs and tiers
under the weighted rule in force, onset recall by calendar year, Brier score, predicted against realised rate by regime and
day type, each variant paired with its references by regime and pressure-day type, and the onsets it gains and loses. `ordinary`
is the AUROC and the reliability slope and intercept (#616) on the days whose pressure-day type is ordinary.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from datetime import date, time
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import metrics, ml, pressure_judge as pj  # noqa: E402
from repo_model.baseline import panel_sha256, rolling_exceedance_backtest  # noqa: E402
from repo_model.contract import QUANTILE_LEVELS  # noqa: E402
from repo_model.data import audit_panel, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

DECLARATION = REPO / "metadata" / "spread_distribution_632.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
PUBLISHED_DISTRIBUTION = REPO / "docs" / "runs" / "published_distribution_daily_h{h}.json"
SEED = 632
BLOCK = 10
COVERAGE_MASSES = (0.5, 0.9)
REPLICATIONS = 2000
LEVEL = 0.90
PASSER = "risk_gbm+settle+h41"
BEST = PASSER + "+dist_roll"
CAP = "risk_gbm+every_day+gate+settle+h41+iorb+tailcap75"
ROWS_FROM = {BEST: "dist", CAP: "cap"}


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


sd = _load("satiation_distance_598")
cm, ann, rds, fa, s587 = sd.cm, sd.ann, sd.rds, sd.fa, sd.s587


# -- the declaration -----------------------------------------------------------------------------------------------


def declared_document() -> dict:
    return rds.committed_declaration(DECLARATION)


def all_rows() -> List[str]:
    document = declared_document()
    return list(document["rows"]["controls"]) + list(document["rows"]["new"])


def variant_rows() -> List[str]:
    return list(declared_document()["rows"]["new"])


def paired_with_model(name: str) -> List[str]:
    """The references a variant is paired with (the declaration's `rows.pairs`); a control has none."""

    return list(declared_document()["rows"]["pairs"].get(name, []))


def require_declared_variants(document: Mapping) -> Dict[str, dict]:
    """The variants that are run: those not marked `run: false`, and at most three."""

    variants = {name: spec for name, spec in document["variants"].items() if spec.get("run", True)}
    if len(variants) > 3:
        raise ValueError(f"at most 3 variants are declared (#632), found {len(variants)}")
    return variants


# -- the statistics ------------------------------------------------------------------------------------------------


def quantile_at(quantiles: Sequence[float], grid: Sequence[float], level: float) -> float:
    """A fitted law's quantile at `level`: the inverse of `ml.exceedance_from_quantiles`' linear law.

    The law is linear between the fitted quantiles and continues at the outer segments' slopes to probability 0 and 1.
    """

    if not 0.0 < level < 1.0:
        raise ValueError(f"a quantile level is in (0, 1), got {level}")
    if len(quantiles) != len(grid) or len(grid) < 2:
        raise ValueError("a law needs one quantile per grid level and at least two levels")
    knots = [float(q) + 1e-6 * k for k, q in enumerate(quantiles)]
    low = (knots[1] - knots[0]) / (grid[1] - grid[0])
    high = (knots[-1] - knots[-2]) / (grid[-1] - grid[-2])
    edges = [knots[0] - grid[0] * low] + knots + [knots[-1] + (1.0 - grid[-1]) * high]
    levels = [0.0] + [float(g) for g in grid] + [1.0]
    for k in range(1, len(levels)):
        if level <= levels[k]:
            span = levels[k] - levels[k - 1]
            return edges[k - 1] + (edges[k] - edges[k - 1]) * (level - levels[k - 1]) / span
    return edges[-1]


def pinballs(levels: Sequence[float], predicted: Sequence[float], observed: float) -> List[float]:
    return [metrics.pinball_loss(level, value, observed) for level, value in zip(levels, predicted)]


def crps_contract(levels: Sequence[float], predicted: Sequence[float], observed: float) -> float:
    """CRPS in basis points on the contract's fixed grid (`metrics.crps_from_quantiles`)."""

    return metrics.crps_from_quantiles(levels, sorted(predicted), observed)


def auroc(probabilities: Sequence[float], outcomes: Sequence[int]) -> Optional[float]:
    """The area under the ROC curve, ties counted half; `None` when one class is absent."""

    if len(probabilities) != len(outcomes):
        raise ValueError("probabilities and outcomes differ in length")
    positives = sum(1 for y in outcomes if y)
    negatives = len(outcomes) - positives
    if positives == 0 or negatives == 0:
        return None
    order = sorted(range(len(probabilities)), key=lambda k: probabilities[k])
    rank_sum = 0.0
    start = 0
    while start < len(order):
        end = start
        while end + 1 < len(order) and probabilities[order[end + 1]] == probabilities[order[start]]:
            end += 1
        average = (start + end) / 2.0 + 1.0
        rank_sum += average * sum(1 for k in order[start:end + 1] if outcomes[k])
        start = end + 1
    return (rank_sum - positives * (positives + 1) / 2.0) / (positives * negatives)


def _sigmoid(x: float) -> float:
    x = max(-40.0, min(40.0, x))
    return 1.0 / (1.0 + math.exp(-x))


def reliability(probabilities: Sequence[float], outcomes: Sequence[int], clip: float = 1e-6) -> Optional[Tuple[float, float]]:
    """The slope and intercept of the logistic fit of the outcome on logit(p), `(slope, intercept)`.

    A perfectly reliable forecast has slope 1 and intercept 0 (Cox 1958; the calibration slope and intercept of
    Van Calster et al.). `p` is clipped to `[clip, 1 - clip]`. `None` when the forecast is constant or one class is
    absent: the slope is undefined. Fitted by Newton's method with a ridge of 1e-8 for stability.
    """

    if len(probabilities) != len(outcomes):
        raise ValueError("probabilities and outcomes differ in length")
    if len(set(probabilities)) < 2 or len(set(outcomes)) < 2:
        return None
    z = [math.log(min(1 - clip, max(clip, p)) / (1 - min(1 - clip, max(clip, p)))) for p in probabilities]
    a, b = 0.0, 1.0
    for _ in range(50):
        g0 = g1 = h00 = h01 = h11 = 0.0
        for zi, yi in zip(z, outcomes):
            mu = _sigmoid(a + b * zi)
            w = mu * (1.0 - mu)
            g0 += yi - mu
            g1 += (yi - mu) * zi
            h00 += w
            h01 += w * zi
            h11 += w * zi * zi
        h00 += 1e-8
        h11 += 1e-8
        det = h00 * h11 - h01 * h01
        if abs(det) < 1e-18:
            return None
        da = (h11 * g0 - h01 * g1) / det
        db = (h00 * g1 - h01 * g0) / det
        step = max(abs(da), abs(db))
        if step > 5.0:  # damp a runaway step (near-separated data)
            da, db = da * 5.0 / step, db * 5.0 / step
        a, b = a + da, b + db
        if abs(da) + abs(db) < 1e-9:
            break
    if not (math.isfinite(a) and math.isfinite(b)) or abs(a) > 50 or abs(b) > 50:
        return None
    return b, a


def interval(statistic, n: int, seed: int) -> Optional[Tuple[float, float]]:
    """A 90% stationary-bootstrap interval of a statistic of resampled indices; `None` if it is undefined on a resample."""

    try:
        return metrics.stationary_bootstrap_interval(
            statistic, n, block_length=BLOCK, seed=seed, replications=REPLICATIONS, level=LEVEL
        )
    except metrics.MetricError:
        return None


# -- run -----------------------------------------------------------------------------------------------------------


def run_command(args) -> int:
    declared = declared_document()
    h = args.horizon
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    variants = require_declared_variants(declared)
    scoring = declared["scoring"]
    last = date.fromisoformat(scoring["last_day"])
    require_unlocked([last], where="spread_distribution_632")
    sd.rolling_constants()
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    registry = sd.measurement_fields.load_registry()
    taus = tuple(float(t) for t in declared["thresholds_bp"])
    minimum = scoring["minimum_history"]
    judge_commit = sd._load("pressure_judge").require_committed_declaration(pj.DEFAULT_DECLARATION)
    timed_rows, timed_registry = ann.arm_inputs("both", rows, registry, h)
    features = sd.variant_features(BEST, h)
    forecasts: Dict[str, dict] = {}
    settings: Dict[str, dict] = {}
    laws: Dict[str, dict] = {}
    for name, spec in variants.items():
        record: list = []
        predictor = ml.pressure_spread_distribution_exceedance(
            features, splits, minimum_history=minimum, structure=spec["structure"], record=record
        )
        with sd.switched_on(), sd.h41_release.release_dating():
            report = rolling_exceedance_backtest(
                timed_rows, predictor=predictor, model_name=name, features=features, registry=timed_registry,
                decision_time=time.fromisoformat(scoring["decision_time"]), taus=taus, minimum_history=minimum,
                refit_every=scoring["refit_every"], end=last, horizon=h,
            )
        days = [fold.scored_date.isoformat() for fold in report.folds]
        if len(record) != len(days):
            raise SystemExit(f"{name}: {len(record)} laws recorded for {len(days)} scored days")
        forecasts[name] = rds.column(report)
        settings[name] = fa._settings(report)
        laws[name] = {
            day: {"part": part, "quantiles": list(quantiles) if quantiles is not None else None}
            for day, (part, quantiles) in zip(days, record)
        }
        print(json.dumps({"horizon": h, "row": name, "done": True}), flush=True)
    document = {
        "horizon": h,
        "panel_sha256": panel_sha256(args.published),
        "scratch_panel_sha256": panel_sha256(args.panel),
        "declaration": declared,
        "judge_commit": judge_commit,
        "declarations": settings,
        "forecasts": forecasts,
    }
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    laws_path = args.output.with_name(args.output.stem + "_laws.json")
    laws_path.write_text(
        json.dumps({"horizon": h, "quantile_grid": declared["model"]["quantile_grid"], "laws": laws}, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"horizon": h, "output": str(args.output), "laws": str(laws_path)}))
    return 0


def refs_command(args) -> int:
    """The references as one file at a lead: the passer's `both` run, the best row of `dist`, and the +tailcap75 row of `cap`."""

    both, dist, cap = (json.loads(Path(p).read_text()) for p in (args.both, args.dist, args.cap))
    for other in (dist, cap):
        if other["horizon"] != both["horizon"] or other["panel_sha256"] != both["panel_sha256"]:
            raise SystemExit("the reference files differ in horizon or panel")
    out = dict(both)
    out["forecasts"] = dict(both["forecasts"])
    for name, source in ((BEST, dist), (CAP, cap)):
        if name not in source["forecasts"]:
            raise SystemExit(f"{name!r} is not in the {ROWS_FROM[name]} file")
        out["forecasts"][name] = source["forecasts"][name]
    out["declarations"] = {**both.get("declarations", {}), **{n: s.get("declarations", {}).get(n, {}) for n, s in ((BEST, dist), (CAP, cap))}}
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "rows": sorted(out["forecasts"])}))
    return 0


# -- step 1: the distribution --------------------------------------------------------------------------------------


def persistence_walk(rows, horizon: int, end: date):
    """As-of persistence's quantile vector on every scored day at `horizon`, walked on the panel cut at `end`.

    The frozen CRPS test's side a (`live_record._compare_sides`), run by `final_test_opening.distribution_walk`; the panel
    is cut at the last scored day first, so no locked day is on the grid (`require_unlocked` inside the walk).
    """

    opening = _load("final_test_opening")
    live = _load("live_record")
    opening.live_record = live
    sides, args = live._compare_sides(horizon)
    name, fit, features, online = sides["persistence"]
    kept = [row for row in rows if row.date <= end]
    registry = json.loads((REPO / "metadata" / "sources.json").read_text())
    walk, levels, _settings = opening.distribution_walk(
        kept, fit=fit, features=features, online_calibration=online, registry=registry, horizon=horizon,
        minimum_history=args.minimum_history, refit_every=args.refit_every,
    )
    return {kept[index].date.isoformat(): vector for index, vector in walk}, levels


def median_abs_error(levels: Sequence[float], predicted: Sequence[float], observed: float) -> float:
    """The absolute error of the median (the contract's level 0.5), in basis points."""

    return abs(predicted[list(levels).index(0.5)] - observed)


def central_hit(levels: Sequence[float], predicted: Sequence[float], observed: float, mass: float) -> float:
    """1.0 when `observed` lies inside the central interval of probability `mass` (levels (1-mass)/2 and (1+mass)/2), else 0.0."""

    ordered = list(levels)
    low = predicted[ordered.index(round((1.0 - mass) / 2.0, 10))]
    high = predicted[ordered.index(round((1.0 + mass) / 2.0, 10))]
    return 1.0 if min(low, high) <= observed <= max(low, high) else 0.0


def published_quantiles(horizon: int, end: date) -> Tuple[Dict[str, List[float]], List[float]]:
    """The published distribution's daily quantiles at `horizon`, days on or before `end` only."""

    document = json.loads(Path(str(PUBLISHED_DISTRIBUTION).format(h=horizon)).read_text())
    kept = {entry["date"]: entry["quantiles_bps"] for entry in document["days"] if date.fromisoformat(entry["date"]) <= end}
    return kept, list(document["levels"])


def paired_losses(variant: Sequence[float], bench: Sequence[float], groups: Mapping[str, Sequence[str]], seed: int) -> dict:
    """The paired difference, benchmark minus variant (positive: the variant is better), pooled and by group."""

    if len(variant) != len(bench):
        raise ValueError("the two loss series differ in length")
    return cells_by_group([b - v for v, b in zip(variant, bench)], groups, seed)


def cells_by_group(series: Sequence[float], groups: Mapping[str, Sequence[str]], seed: int) -> dict:
    """The mean of a per-day series with its stationary-bootstrap interval, pooled and by group."""

    n = len(series)
    diff = series
    out = {"pooled": _cell(diff, range(n), n, seed)}
    for dimension, labels in groups.items():
        out[dimension] = {}
        for label in sorted(set(labels)):
            members = [k for k, x in enumerate(labels) if x == label]
            out[dimension][label] = _cell(diff, members, n, seed)
    return out


def _cell(diff: Sequence[float], members: Sequence[int], n: int, seed: int) -> dict:
    inside = set(members)
    mean = sum(diff[k] for k in members) / len(members) if members else None
    if not members:
        return {"days": 0, "mean": None, "interval": None}

    def statistic(indices):
        chosen = [diff[i] for i in indices if i in inside]
        if not chosen:
            raise metrics.MetricError("no day of the cell in the resample")
        return sum(chosen) / len(chosen)

    return {"days": len(members), "mean": mean, "interval": interval(statistic, n, seed)}


def distribution_command(args) -> int:
    declared = declared_document()
    step = declared["step_1"]
    scoring = declared["scoring"]
    end = date.fromisoformat(scoring["last_day"])
    require_unlocked([end], where="spread_distribution_632 distribution")
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    by_date = {row.date: row for row in rows}
    splits = load_split_declaration(SPLITS)
    base = pj.load_declaration()
    states_script = sd._load("pressure_judge")
    args.minimum_history = scoring["minimum_history"]
    args.refit_every = scoring["refit_every"]
    levels = list(QUANTILE_LEVELS)
    if levels != step["levels"]:
        raise SystemExit("the contract's quantile levels are not the declared ones")
    result: Dict[str, dict] = {"declaration": str(DECLARATION.relative_to(REPO)), "levels": levels, "horizons": {}}
    for h in declared["horizons"]:
        document = json.loads(Path(args.rows.format(h=h)).read_text())
        laws = json.loads(Path(args.rows.format(h=h)).with_name(Path(args.rows.format(h=h)).stem + "_laws.json").read_text())
        grid_levels = laws["quantile_grid"]
        if grid_levels != declared["model"]["quantile_grid"]:
            raise SystemExit("a law file's grid is not the declared one")
        persistence, plev = persistence_walk(rows, h, end)
        published, qlev = published_quantiles(h, end)
        if list(plev) != levels or list(qlev) != levels:
            raise SystemExit("a benchmark reports other levels than the contract's")
        cell: Dict[str, dict] = {}
        for name in variant_rows():
            day_laws = {d: e for d, e in laws["laws"][name].items() if e["quantiles"] is not None}
            days = sorted(d for d in day_laws if d in persistence and d in published)
            if not days:
                raise SystemExit(f"{name}: no scored day with a law and both benchmarks at h = {h}")
            actual = {d: float(by_date[date.fromisoformat(d)].spread_bps) for d in days}
            mine = {d: [quantile_at(day_laws[d]["quantiles"], grid_levels, p) for p in levels] for d in days}
            fine = {d: sum(pinballs(grid_levels, day_laws[d]["quantiles"], actual[d])) * 2.0 / len(grid_levels) for d in days}
            scored = [date.fromisoformat(d) for d in days]
            states = states_script._scarcity_states(h, base.last_day)
            grid = pj.build_grid(base, h, rows, scored, splits, scarcity_state=states)
            groups = {"regime": grid.groups["regime"], "day_type": grid.groups["day_type"]}
            entry = {"days": len(days), "first": days[0], "last": days[-1]}
            sides = {"variant": mine, "as_of_persistence": {d: persistence[d] for d in days}, "published_distribution": {d: published[d] for d in days}}
            for side, vectors in sides.items():
                crps = [crps_contract(levels, vectors[d], actual[d]) for d in days]
                per_level = [sum(pinballs(levels, vectors[d], actual[d])[k] for d in days) / len(days) for k in range(len(levels))]
                entry[side] = {"crps_bps": sum(crps) / len(crps), "pinball_by_level": per_level, "pinball_mean": sum(per_level) / len(per_level), "_series": crps}
            entry["variant"]["crps_bps_own_grid"] = sum(fine.values()) / len(fine)
            # MAE of the median and the 50% / 90% central coverage (ruling of 12 October on #632), on the same days and sides
            maes = {side: [median_abs_error(levels, vectors[d], actual[d]) for d in days] for side, vectors in sides.items()}
            hits = {mass: {side: [central_hit(levels, vectors[d], actual[d], mass) for d in days] for side, vectors in sides.items()} for mass in COVERAGE_MASSES}
            for side in sides:
                entry[side]["mae_median_bps"] = sum(maes[side]) / len(days)
                for mass in COVERAGE_MASSES:
                    key = f"{round(mass * 100)}"
                    entry[side]["coverage_" + key] = sum(hits[mass][side]) / len(days)
                    entry[side]["coverage_" + key + "_by_group"] = cells_by_group(hits[mass][side], groups, pj._seed(SEED, name, h, side, "rate", mass))
            entry["paired"] = {}
            entry["mae_median"] = {}
            entry["coverage_difference"] = {}
            for side in ("as_of_persistence", "published_distribution"):
                seed = pj._seed(SEED, name, h, side)
                entry["paired"][side] = paired_losses(entry["variant"]["_series"], entry[side]["_series"], groups, seed)
                entry["mae_median"][side] = paired_losses(maes["variant"], maes[side], groups, pj._seed(SEED, name, h, side, "mae"))
                for mass in COVERAGE_MASSES:
                    # the variant's hit rate minus the benchmark's: positive when the variant covers more often
                    diff = [v - b for v, b in zip(hits[mass]["variant"], hits[mass][side])]
                    entry["coverage_difference"][f"{side}:{round(mass * 100)}"] = cells_by_group(diff, groups, pj._seed(SEED, name, h, side, "cov", mass))
            for side in sides:
                entry[side].pop("_series")
            cell[name] = entry
        result["horizons"][str(h)] = cell
        print(json.dumps({"horizon": h, "done": True}), flush=True)
    result["panel_sha256"] = panel_sha256(args.panel)
    args.output.write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(distribution_text(result), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def _iv(cell: Optional[Mapping]) -> str:
    if not cell or cell.get("mean") is None:
        return "n/a"
    if not cell.get("interval"):
        return f"{cell['mean']:+.3f}"
    lower, upper = cell["interval"]
    return f"{cell['mean']:+.3f} [{lower:+.3f}, {upper:+.3f}]"


def distribution_text(result: Mapping) -> str:
    levels = result["levels"]
    out = [
        "# Step 1: the spread distribution against as-of persistence and the published distribution (#632)", "",
        "Generated by `scripts/spread_distribution_632.py distribution`; not edited by hand. CRPS and pinball loss are in basis points on the "
        "contract's five levels (" + ", ".join(f"{p:g}" for p in levels) + "), per scored day then averaged, over the days on which "
        "the variant has a law (a variant's law is read at those levels). The difference is the benchmark's CRPS minus the variant's: "
        "positive when the variant is better; 90% stationary-bootstrap intervals. Under each CRPS block, the ruling's other measures: "
        "MAE of the median and the 50% / 90% central coverage, on the same days.", "",
    ]
    for h, cell in result["horizons"].items():
        out += [f"## h = {h}", "",
                "| variant | days | CRPS: variant | as-of persistence | published | variant own 13-level grid | persistence minus variant [90%] | published minus variant [90%] |",
                "|---|---|---|---|---|---|---|---|"]
        for name, e in cell.items():
            out.append(
                f"| {name} | {e['days']} | {e['variant']['crps_bps']:.3f} | {e['as_of_persistence']['crps_bps']:.3f} | "
                f"{e['published_distribution']['crps_bps']:.3f} | {e['variant']['crps_bps_own_grid']:.3f} | "
                f"{_iv(e['paired']['as_of_persistence']['pooled'])} | {_iv(e['paired']['published_distribution']['pooled'])} |"
            )
        out += ["", "Mean pinball loss by level:", "", "| variant / side | " + " | ".join(f"{p:g}" for p in levels) + " |", "|---|" + "---|" * len(levels)]
        for name, e in cell.items():
            for side, label in (("variant", name), ("as_of_persistence", f"as-of persistence (on {name}'s days)"), ("published_distribution", f"published (on {name}'s days)")):
                out.append(f"| {label} | " + " | ".join(f"{v:.3f}" for v in e[side]["pinball_by_level"]) + " |")
        for name, e in cell.items():
            for side, title in (("as_of_persistence", "persistence"), ("published_distribution", "the published distribution")):
                out += ["", f"{name}: CRPS difference, {title} minus variant, by regime and pressure-day type:", "", "| group | days | difference [90%] |", "|---|---|---|"]
                for dimension in ("regime", "day_type"):
                    for label, c in e["paired"][side][dimension].items():
                        out.append(f"| {dimension} = {label} | {c['days']} | {_iv(c)} |")
        out += ["", "MAE of the median (bp) and central coverage, same days; MAE difference is the benchmark's minus the variant's (positive: the variant is better); "
                "coverage difference is the variant's hit rate minus the benchmark's; nominal 0.50 and 0.90; 90% stationary-bootstrap intervals:", "",
                "| variant | days | MAE: variant | persistence | published | persistence minus variant [90%] | published minus variant [90%] |",
                "|---|---|---|---|---|---|---|"]
        for name, e in cell.items():
            out.append(
                f"| {name} | {e['days']} | {e['variant']['mae_median_bps']:.3f} | {e['as_of_persistence']['mae_median_bps']:.3f} | "
                f"{e['published_distribution']['mae_median_bps']:.3f} | {_iv(e['mae_median']['as_of_persistence']['pooled'])} | "
                f"{_iv(e['mae_median']['published_distribution']['pooled'])} |"
            )
        out += ["", "| variant | days | coverage: variant 50% / 90% | persistence 50% / 90% | published 50% / 90% | variant minus persistence, 50% [90%] | 90% [90%] | variant minus published, 50% [90%] | 90% [90%] |",
                "|---|---|---|---|---|---|---|---|---|"]
        for name, e in cell.items():
            rates = " | ".join(f"{e[side]['coverage_50']:.3f} / {e[side]['coverage_90']:.3f}" for side in ("variant", "as_of_persistence", "published_distribution"))
            diffs = " | ".join(_iv(e["coverage_difference"][f"{side}:{m}"]["pooled"]) for side in ("as_of_persistence", "published_distribution") for m in (50, 90))
            out.append(f"| {name} | {e['days']} | {rates} | {diffs} |")
        for name, e in cell.items():
            for side, title in (("as_of_persistence", "persistence"), ("published_distribution", "the published distribution")):
                out += ["", f"{name}: MAE of the median, {title} minus variant, by regime and pressure-day type:", "", "| group | days | difference [90%] |", "|---|---|---|"]
                for dimension in ("regime", "day_type"):
                    for label, c in e["mae_median"][side][dimension].items():
                        out.append(f"| {dimension} = {label} | {c['days']} | {_iv(c)} |")
            out += ["", f"{name}: central coverage by regime and pressure-day type (hit rate [90%]; the variant, then as-of persistence, then the published distribution):", "",
                    "| group | days | variant 50% | persistence 50% | published 50% | variant 90% | persistence 90% | published 90% |", "|---|---|---|---|---|---|---|---|"]
            for dimension in ("regime", "day_type"):
                for label, c in e["variant"]["coverage_50_by_group"][dimension].items():
                    cols = [_rate(e[side][f"coverage_{m}_by_group"][dimension][label]) for m in (50, 90) for side in ("variant", "as_of_persistence", "published_distribution")]
                    out.append(f"| {dimension} = {label} | {c['days']} | " + " | ".join(cols) + " |")
        out.append("")
    return "\n".join(out) + "\n"


def _rate(cell: Mapping) -> str:
    if not cell or cell.get("mean") is None:
        return "n/a"
    if not cell.get("interval"):
        return f"{cell['mean']:.2f}"
    return f"{cell['mean']:.2f} [{cell['interval'][0]:.2f}, {cell['interval'][1]:.2f}]"


# -- compare -------------------------------------------------------------------------------------------------------


def compare_command(args) -> int:
    """The combined page's comparison (`combined_model_561.compare_command`) over this measurement's rows, with the
    onsets each variant gains and loses against each of its references added."""

    cm.declared_document = declared_document
    cm.all_rows = all_rows
    cm.paired_with_model = paired_with_model
    cm.DECLARATION = DECLARATION
    calls: List[tuple] = []
    original_load = cm._load

    def recording_load(name):
        module = original_load(name)
        if name == "ngboost_laplace_check":
            inner = module.only_this_row_warns

            def only_this_row_warns(days, onset, caught, others):
                calls.append((list(days), list(onset), list(caught)))
                return inner(days, onset, caught, others)

            module.only_this_row_warns = only_this_row_warns
        return module

    cm._load = recording_load
    args_markdown = args.markdown
    args.markdown = None
    try:
        status = cm.compare_command(args)
    finally:
        cm._load = original_load
        args.markdown = args_markdown
    rows_names = all_rows()
    if len(calls) != 2 * len(rows_names):
        raise SystemExit(f"expected two only-row calls per row, saw {len(calls)}")
    flags = {name: calls[2 * k] for k, name in enumerate(rows_names)}
    days = flags[rows_names[0]][0]
    onset = flags[rows_names[0]][1]
    result = json.loads(Path(args.output).read_text())
    gained_lost = {}
    for name in variant_rows():
        gained_lost[name] = {}
        for ref in paired_with_model(name) + [PASSER]:
            mine, theirs = flags[name][2], flags[ref][2]
            gained_lost[name][ref] = {
                "gained": [d.isoformat() for d, o, a, b in zip(days, onset, mine, theirs) if o and a and not b],
                "lost": [d.isoformat() for d, o, a, b in zip(days, onset, mine, theirs) if o and b and not a],
                "both": sum(1 for o, a, b in zip(onset, mine, theirs) if o and a and b),
                "onsets": int(sum(onset)),
            }
    result["gained_lost"] = gained_lost
    Path(args.output).write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(
            cm.markdown(result, declared_document(), list(result["readings"]["weighted"]), rows_names).replace(
                "# The combined model (#561)", "# Forecast the spread, then apply the +5 bp threshold (#632)", 1
            ),
            encoding="utf-8",
        )
    return status


# -- the ordinary days ---------------------------------------------------------------------------------------------


def ordinary_command(args) -> int:
    declared = declared_document()
    base = pj.load_declaration()
    rows = load_daily_panel(args.panel)
    audit_panel(rows)
    splits = load_split_declaration(SPLITS)
    judge_script = sd._load("pressure_judge")
    jr = cm._load("judge_readings")
    names = all_rows() + declared["references"]["pair_against"]
    tau = base.primary
    per_row: Dict[str, dict] = {n: {"leads": {}} for n in names}
    pooled: Dict[str, Tuple[List[float], List[int]]] = {n: ([], []) for n in names}
    for h in declared["horizons"]:
        forecasts = {}
        for label, template in (("bench", args.bench), ("risk", args.risk), ("reference", args.reference), ("parents", args.parents), ("rows", args.rows)):
            for f in pj.forecasts_from_horizon_document(jr._load(template, h)):
                if f.name in names:
                    forecasts.setdefault(f.name, f)
        missing = [n for n in names if n not in forecasts]
        if missing:
            raise SystemExit(f"h = {h}: no forecast for {missing[:3]}")
        reference = forecasts[base.climatology]
        states = judge_script._scarcity_states(h, base.last_day)
        grid = pj.build_grid(base, h, rows, reference.dates, splits, scarcity_state=states)
        ordinary = [k for k, label in enumerate(grid.groups["day_type"]) if label == "ordinary"]
        for n in names:
            f = forecasts[n]
            if f.dates != reference.dates:
                raise SystemExit(f"{n} at h = {h} is not on the shared grid")
            p = [f.probabilities[tau][k] for k in ordinary]
            y = [grid.outcomes[tau][k] for k in ordinary]
            pooled[n][0].extend(p)
            pooled[n][1].extend(y)
            entry = {"days": len(y), "events": sum(y), "constant": len(set(p)) < 2, "auroc": auroc(p, y)}
            seed = pj._seed(SEED, n, h, "ordinary")
            entry["auroc_interval"] = interval(lambda idx: _stat(auroc, p, y, idx), len(y), seed) if entry["auroc"] is not None else None
            rel = reliability(p, y)
            entry["reliability"] = None if rel is None else {"slope": rel[0], "intercept": rel[1]}
            if rel is not None:
                entry["slope_interval"] = interval(lambda idx: _stat(_slope, p, y, idx), len(y), seed + 1)
                entry["intercept_interval"] = interval(lambda idx: _stat(_intercept, p, y, idx), len(y), seed + 2)
            per_row[n]["leads"][str(h)] = entry
    for n in names:
        p, y = pooled[n]
        rel = reliability(p, y)
        per_row[n]["pooled"] = {
            "days": len(y), "events": sum(y), "auroc": auroc(p, y),
            "reliability": None if rel is None else {"slope": rel[0], "intercept": rel[1]},
        }
    out = {"declaration": str(DECLARATION.relative_to(REPO)), "threshold_bp": tau, "rows": per_row, "panel_sha256": panel_sha256(args.panel)}
    args.output.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def _stat(function, p, y, indices):
    value = function([p[i] for i in indices], [y[i] for i in indices])
    if value is None:
        raise metrics.MetricError("undefined on this resample")
    return value


def _slope(p, y):
    r = reliability(p, y)
    return None if r is None else r[0]


def _intercept(p, y):
    r = reliability(p, y)
    return None if r is None else r[1]


# -- report --------------------------------------------------------------------------------------------------------


def _ci(interval_pair, value) -> str:
    if value is None:
        return "undefined"
    if not interval_pair:
        return f"{value:.3f}"
    return f"{value:.3f} [{interval_pair[0]:.3f}, {interval_pair[1]:.3f}]"


def ordinary_text(ordinary: Mapping) -> str:
    out = [
        "## The ordinary days: AUROC and reliability of the +5 bp probability (#616)", "",
        "Days whose pressure-day type is ordinary. AUROC at each lead with a 90% stationary-bootstrap interval; the reliability slope and "
        "intercept are those of the logistic fit of the outcome on logit(p) (1 and 0 for a reliable forecast); undefined where the forecast is "
        "constant (a row that is exactly 0 on every ordinary day).", "",
        "| row | days / pressure days (h = 1) | AUROC h = 1 | h = 2 | h = 3 | h = 4 | h = 5 | AUROC pooled | slope, intercept pooled | slope [90%] h = 1 | intercept [90%] h = 1 |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for name, e in ordinary["rows"].items():
        leads = e["leads"]
        first = leads["1"]
        rel = first.get("reliability")
        pooled = e["pooled"]
        prel = pooled.get("reliability")
        out.append(
            f"| {name} | {first['days']} / {first['events']} | "
            + " | ".join(_ci(leads[str(h)].get("auroc_interval"), leads[str(h)]["auroc"]) if not leads[str(h)]["constant"] else "constant" for h in range(1, 6))
            + f" | {('%.3f' % pooled['auroc']) if pooled['auroc'] is not None else 'undefined'} | "
            + (f"{prel['slope']:.2f}, {prel['intercept']:+.2f}" if prel else "undefined")
            + " | "
            + (_ci(first.get("slope_interval"), rel["slope"]) if rel else "undefined")
            + " | "
            + (_ci(first.get("intercept_interval"), rel["intercept"]) if rel else "undefined")
            + " |"
        )
    return "\n".join(out) + "\n"


FAMILY = lambda: ("the spread-level distribution and its references", tuple(all_rows()))  # noqa: E731


def report_text(compare: dict, distribution: Optional[dict], ordinary: Optional[dict]) -> str:
    audit = s587._audit
    title, names = FAMILY()
    out: List[str] = [
        "# Forecast the spread, then apply the +5 bp threshold (#632)", "",
        "Generated by `scripts/spread_distribution_632.py report`; not edited by hand.", "",
    ]
    if distribution is not None:
        out += [distribution_text(distribution), ""]
    verdicts = compare["judge"]["weighted"]
    changed: List[str] = []
    for n in variant_rows():
        for ref in paired_with_model(n) + [PASSER]:
            b, a = verdicts[ref]["verdict"], verdicts[n]["verdict"]
            moved = [
                f"{label} {audit._yes(b[key])} to {audit._yes(a[key])}"
                for key, label in (("tier_1_onset_warning", "tier 1"), ("tier_3_no_crying_wolf", "tier 3"), ("tier_5_week_ahead", "tier 5"), ("passes", "pass"))
                if b[key] != a[key]
            ]
            if moved:
                changed.append(f"- `{n}` against `{ref}`: " + ", ".join(moved))
    out += ["## Verdicts that change against each reference (weighted rule in force)", "", *(changed or ["None: no tier or pass changes."]), ""]
    for rule, key in (("weighted rule in force", "weighted"), ("flat rule", "unweighted")):
        tables = compare["judge_tables"][key]
        out += [f"## {title}: the judge under the {rule}", ""]
        out += ["### Table 1", "", *s587.judge_table(tables, "Table 1.", names)]
        out += ["### Tier 1 at each lead alone (the judge's Table 1b)", "", *s587.judge_lead_blocks(tables, names)]
        out += ["### Share of the pressure days flagged at h = 1, by regime and pressure-day type (Table 2)", "", *s587.judge_table(tables, "Table 2.", names)]
    years = sorted({y for n in names for y in compare["by_year"].get(n, {})})
    out += ["## Onsets warned by calendar year (lead >= 1, any horizon 1 to 5; weighted rule; 2019 and 2025 in bold)", "",
            "| row | " + " | ".join(f"**{y}**" if y in ("2019", "2025") else y for y in years) + " |", "|---|" + "---|" * len(years)]
    for n in names:
        cells = compare["by_year"][n]
        out.append(f"| {n} | " + " | ".join("–" if y not in cells else f"{cells[y][1]} of {cells[y][0]}" for y in years) + " |")
    out += ["", "## Predicted against realised rate of a pressure day (+5 bp), by regime and day type, pooled over h = 1 to 5", "",
            "| row | cell | days | predicted | realised |", "|---|---|---|---|---|"]
    for n in names:
        for key, c in compare["calibration"][n].items():
            out.append(f"| {n} | {key} | {c['days']:g} | {c['predicted']:.4f} | {c['realised']:.4f} |")
    out += ["", "## Brier score at +5 bp, pooled by horizon", "", "| row | " + " | ".join(f"h = {h}" for h in range(1, 6)) + " |", "|---|" + "---|" * 5]
    for n in names:
        sc = compare["scores"][n]
        out.append(f"| {n} | " + " | ".join(f"{sc[str(h)]['brier']:.4f}" for h in range(1, 6)) + " |")
    out.append("")
    if ordinary is not None:
        out += [ordinary_text(ordinary), ""]
    for n in variant_rows():
        for ref, gl in compare["gained_lost"][n].items():
            out += [f"## {n}: onsets gained and lost against {ref}, by date (any horizon 1 to 5, lead >= 1)", "",
                    f"Warned by both: {gl['both']} of {gl['onsets']} onsets.", "",
                    f"Gained ({len(gl['gained'])}): " + (", ".join(gl["gained"]) or "none") + ".", "",
                    f"Lost ({len(gl['lost'])}): " + (", ".join(gl["lost"]) or "none") + ".", ""]
        for ref in dict.fromkeys(paired_with_model(n) + list(declared_document()["references"]["pair_against"])):
            paired = compare["paired"].get(n, {}).get(ref)
            if not paired:
                continue
            out += [f"### {n} against {ref}: Brier difference, reference minus row (positive: the row is better), 90% interval", "",
                    "| h | pooled |", "|---|---|"]
            out += [f"| {h} | {cm.lf._iv(c['pooled'])} |" for h, c in paired["brier"].items()]
            for dimension in ("regime", "day_type", "scarcity_state"):
                labels = sorted(paired["brier"]["1"].get(dimension, {}))
                if not labels:
                    continue
                out += ["", f"By {dimension}, Brier difference at h = 1 / 3 / 5:", "", f"| {dimension} | days | h = 1 | h = 3 | h = 5 |", "|---|---|---|---|---|"]
                for label in labels:
                    cells = [paired["brier"][h][dimension][label] for h in ("1", "3", "5")]
                    out.append(f"| {label} | {cells[0]['days']:g} | " + " | ".join(cm.lf._iv(c) for c in cells) + " |")
            rec = paired["recall"]
            out += ["", f"Onset recall difference, row minus {ref} (each at its own cut-offs, any horizon), pooled: {cm.lf._iv(rec['pooled'])} on {rec['pooled']['onsets']} onsets.", ""]
    return "\n".join(out) + "\n"


def report_command(args) -> int:
    compare = json.loads(Path(args.compare).read_text())
    distribution = json.loads(Path(args.distribution).read_text()) if args.distribution else None
    ordinary = json.loads(Path(args.ordinary).read_text()) if args.ordinary else None
    args.output.write_text(report_text(compare, distribution, ordinary), encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("run")
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("--published", type=Path, required=True)
    p.add_argument("--horizon", type=int, required=True)
    p.add_argument("--output", type=Path, required=True)
    p = sub.add_parser("refs")
    for name in ("both", "dist", "cap", "output"):
        p.add_argument(f"--{name}", type=Path, required=True)
    p = sub.add_parser("distribution")
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("rows", help="template of the variants' run files, with {h}")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--markdown", type=Path)
    p = sub.add_parser("compare")
    p.add_argument("--panel", type=Path, required=True)
    for name in ("bench", "risk", "reference", "parents", "rows"):
        p.add_argument(f"--{name}", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--markdown", type=Path)
    p = sub.add_parser("ordinary")
    p.add_argument("--panel", type=Path, required=True)
    for name in ("bench", "risk", "reference", "parents", "rows"):
        p.add_argument(f"--{name}", required=True)
    p.add_argument("--output", type=Path, required=True)
    p = sub.add_parser("report")
    p.add_argument("--compare", required=True)
    p.add_argument("--distribution")
    p.add_argument("--ordinary")
    p.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    return {
        "run": run_command, "refs": refs_command, "distribution": distribution_command, "compare": compare_command,
        "ordinary": ordinary_command, "report": report_command,
    }[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
