"""The spread distribution under scoring protocol v1 (#634, H5): walks, scoring and report.

A scratch measurement, not a record: it writes JSON and Markdown to the paths it is given and nothing into `docs/runs/`.
Every choice is in `metadata/spread_distribution_634.json`, which this script refuses to read unless it is committed and
unchanged. Scored decision days end where their fifth target day is on or before 2025-12-31 (`docs/decisions/lockbox.md`;
`require_unlocked`, and the scorer's own guard). Development days give a score and an interval, never a verdict
(scoring protocol v1, #640).

    PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUBLISHED.csv \\
        --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
    PYTHONPATH=src python3 scripts/tax_date_market_days.py scripts/pressure_v1_1.py panel --output AUG.csv
    PYTHONPATH=src python3 scripts/tax_date_market_days.py scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
    PYTHONPATH=src python3 scripts/tax_date_market_days.py scripts/satiation_distance_598.py panel --panel AUG2.csv --output AUG2D.csv
    for h in 1 2 3 4 5: for v in published gbm_funding a_published_new b_gbm_new c_two_part_new:
        PYTHONPATH=src python3 scripts/spread_distribution_634.py walk --variant $v --horizon $h --published PUBLISHED.csv \\
            --panel AUG2D.csv --output OUT/${v}_h$h.json
    for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/spread_distribution_634.py exceedance --horizon $h \\
        --published PUBLISHED.csv --output OUT/exceed_h$h.json
    PYTHONPATH=src python3 scripts/spread_distribution_634.py score --published PUBLISHED.csv --walks OUT --output OUT/score.json
    PYTHONPATH=src python3 scripts/spread_distribution_634.py report --score OUT/score.json --output OUT/report.md

`walk` fits a variant walk-forward on the shared fold grid and keeps each scored day's quantiles. A walk at lead h scores
target day s from the information public h business days earlier (`asof.InformationRule(horizon=h)`), so the five leads of
one decision day d are the walks' laws for the targets d + 1 .. d + 5. `score` assembles them (`lead_forecasts`), adds the
benchmarks of protocol section 4, scores every decision day with `scoring_protocol.day_scores` and pairs each candidate with
each benchmark with `scoring_protocol.paired_tests`.
"""

from __future__ import annotations

import argparse
import functools
import importlib.util
import json
import math
import subprocess
import sys
from datetime import date, time
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from repo_model import metrics, ml, protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402
from repo_model.asof import InformationRule, fold_grid, refit_blocks, require_refit_every  # noqa: E402
from repo_model.baseline import (  # noqa: E402
    _AsOfFold,
    _at_decision,
    _check_decision_relative_availability,
    _check_fitter_stayed_inside,
    _fit_at_origin,
    _model_settings,
    _reads_information,
    _resolve_fields,
    _with_online_settings,
    calendar_climatology_exceedance,
    panel_sha256,
    persistence_logistic_exceedance,
    rolling_exceedance_backtest,
)
from repo_model.data import audit_panel, exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import load_split_declaration  # noqa: E402
from repo_model.lockbox import require_unlocked  # noqa: E402

DECLARATION = REPO / "metadata" / "spread_distribution_634.json"
SPLITS = REPO / "metadata" / "evaluation_splits.json"
SOURCES = REPO / "metadata" / "sources.json"
PUBLISHED_DAILY = REPO / "docs" / "runs" / "published_distribution_daily_h{h}.json"
LAST_TARGET = date(2025, 12, 31)
SEED = 634
DECISION = time(16, 0)
HORIZONS = sp.HORIZONS
GRID = sp.GRID
#: the fixed grid of `contract.QUANTILE_LEVELS`, on which pinball loss, the median and the coverages are reported.
REPORT_LEVELS = (0.05, 0.25, 0.5, 0.75, 0.95)
THRESHOLDS_BP = (0.0, 2.0, 5.0, 10.0)
VARIANTS = ("a_published_new", "b_gbm_new", "c_two_part_new")
CONTROLS = ("published", "gbm_funding")
BASE = ("reserve_balances", "sofr_p25", "sofr_p75", "sofr_volume", "spread_bps", "tbill_13w", "tbill_4w", "tga", "treasury_settlement")
NEW_COLUMNS = (
    "tax_date",
    "reserve_scarcity_state",
    "iorb_announced_change_bps",
    "iorb_days_to_announced_change",
    "satiation_dist_roll",
    "sofr_p99_iorb_bps",
)
#: variant (c): the risk-date part is #632's (the inputs of `risk_gbm+settle+h41+dist_roll`) plus the announced IORB change.
TWO_PART_EXTRA = ("iorb_announced_change_bps",)
TWO_PART_EVERY_DAY = ml.EVERY_DAY_COMPONENT_INPUTS + ("satiation_dist_roll", "iorb_announced_change_bps", "reserve_scarcity_state")


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_script", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_script"] = module
    spec.loader.exec_module(module)
    return module


# -- the declaration -----------------------------------------------------------------------------------------------


def committed_declaration(path: Path = DECLARATION) -> dict:
    """The declaration, refused unless it is committed and unchanged since `HEAD`."""

    relative = str(path.resolve().relative_to(REPO))
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", relative], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    if dirty:
        raise SystemExit(f"{relative} is not committed ({dirty}); a declaration is made before any score")
    document = json.loads(path.read_text(encoding="utf-8"))
    if tuple(document["protocol"]["grid"]) != GRID:
        raise SystemExit("the declared grid is not the protocol's")
    if len(document["variants"]) - 1 > 3:  # the "count" entry is not a variant
        raise SystemExit("at most 3 variants are declared (#634)")
    return document


# -- the pure parts ------------------------------------------------------------------------------------------------


def refuse_locked(days: Sequence[date]) -> None:
    """Refuse a run that would score a day of a locked tier (`docs/decisions/lockbox.md`): raises `LookAheadError`."""

    require_unlocked(list(days), where="spread_distribution_634")


def on_grid(quantiles: Sequence[float], levels: Sequence[float], grid: Sequence[float] = GRID) -> List[float]:
    """A law forecast at `levels`, put on `grid` by the linear law of the gbm exceedance (#632).

    Linear between the fitted quantiles and continued at the outer segments' slopes to probability 0 and 1
    (`spread_distribution_632.quantile_at`, the inverse of `ml.exceedance_from_quantiles`). A reading, not a decision
    (the declaration's `questions`). At the levels it was fitted at, the law returns the fitted quantiles.
    """

    spread = _load("spread_distribution_632")
    out = [spread.quantile_at(quantiles, levels, float(level)) for level in grid]
    return sorted(out)


def lead_forecasts(
    laws: Mapping[int, Mapping[date, Optional[Sequence[float]]]], calendar: Sequence[date]
) -> Tuple[Dict[date, Dict[int, Optional[List[float]]]], List[date]]:
    """Per-lead walks (`laws[h][target day]`) as decision-day forecasts (`out[d][h]`), and the scored decision days.

    A walk at lead h scores target `s` from the decision made h business days before it, so decision day `d` has the
    lead-h law of target `calendar[position(d) + h]`. A decision day is scored when all five targets are in their
    walks (`None` is a missing forecast, to be filled by B1; absent is not scored). A target not on the calendar is an
    error.
    """

    position = {day: index for index, day in enumerate(calendar)}
    candidates: Optional[set] = None
    for h in HORIZONS:
        days = set()
        for target in laws[h]:
            if target not in position:
                raise ValueError(f"target day {target} is not on the scoring calendar")
            if position[target] - h < 0:
                raise ValueError(f"lead {h} target {target} has no decision day on the calendar")
            days.add(calendar[position[target] - h])
        candidates = days if candidates is None else candidates & days
    decision_days = sorted(candidates or ())
    out: Dict[date, Dict[int, Optional[List[float]]]] = {}
    for day in decision_days:
        out[day] = {}
        for h in HORIZONS:
            law = laws[h][calendar[position[day] + h]]
            out[day][h] = None if law is None else [float(v) for v in law]
    return out, decision_days


def cell_scores(
    forecasts: Mapping[date, Mapping[int, Sequence[float]]],
    outcomes: Mapping[date, Optional[float]],
    calendar: Sequence[date],
    score,
) -> Dict[Tuple[date, int], float]:
    """The score of each (decision day, lead) whose target has an outcome: the cells `day_scores` averages."""

    position = {day: index for index, day in enumerate(calendar)}
    out = {}
    for decision, leads in forecasts.items():
        for h in HORIZONS:
            target = calendar[position[decision] + h]
            if outcomes.get(target) is not None:
                out[(decision, h)] = score(leads[h], outcomes[target])
    return out


def day_means(
    cells: Mapping[Tuple[date, int], float],
    include,
) -> Dict[date, float]:
    """A decision day's mean over its leads whose cell `include(decision, h)` admits; days with none are absent."""

    sums: Dict[date, List[float]] = {}
    for (decision, h), value in cells.items():
        if include(decision, h):
            sums.setdefault(decision, []).append(value)
    return {day: sum(values) / len(values) for day, values in sums.items()}


def pinball(level: float, predicted: float, observed: float) -> float:
    return metrics.pinball_loss(level, predicted, observed)


def level_value(quantiles: Sequence[float], level: float) -> float:
    return quantiles[GRID.index(level)]


def brier(probability: float, happened: bool) -> float:
    return (probability - (1.0 if happened else 0.0)) ** 2


def exceedance(quantiles: Sequence[float], threshold: float) -> float:
    """P(spread > threshold bp) read off a 23-level law (`ml.exceedance_from_quantiles`, the whole-basis-point event)."""

    return float(ml.exceedance_from_quantiles(list(quantiles), list(GRID), (threshold,))[0])


# -- the walks -----------------------------------------------------------------------------------------------------


def walk(rows, *, fit, features, online_calibration, registry, horizon, minimum_history, refit_every, expected_levels):
    """`final_test_opening.distribution_walk` with the levels it expects as an argument; keeps every scored day's law.

    Returns `[(row index, quantiles)]` in fold order, the levels and the fit's settings.
    """

    declared = tuple(features)
    _field_sources, sources = _resolve_fields(declared)
    rule = InformationRule(registry, declared, decision_time=DECISION, horizon=horizon)
    refit = require_refit_every(refit_every)
    dates = [row.date for row in rows]
    grid = fold_grid(dates, registry, decision_time=DECISION, minimum_history=minimum_history, horizon=horizon)
    refuse_locked([dates[index] for index in grid])
    reads_information = _reads_information(fit)
    online = None if online_calibration is None else online_calibration(rows, rule)
    fitted, checked, settings = None, False, {}
    out = []
    levels = None
    for indices in refit_blocks(grid, refit):
        for index in indices:
            info = rule.information_set(dates, index)
            rule.check(dates, info)
            for read in info.reads:
                _check_decision_relative_availability(
                    registry, read.fields, dates, read.row, index, decision_time=DECISION, horizon=horizon
                )
            block_frame = rule.frame(rows, info) if index == indices[0] else None
            fold = _AsOfFold(index, info, block_frame, rule.observation(rows, info))
            if block_frame is not None:
                fitted = _fit_at_origin(
                    fit, block_frame, minimum_history=minimum_history, information=rule,
                    reads_information=reads_information,
                )
                if not checked:
                    _check_fitter_stayed_inside(fitted.features_read, declared, sources)
                    settings = _with_online_settings(_model_settings(fitted), online)
                    checked = True
            view = _at_decision(fitted, rows, rule, fold)
            if online is not None:
                view = online.view(view, index, fold.feature_row)
            if tuple(view.levels) != tuple(expected_levels):
                raise ValueError(f"the model reports quantile levels {tuple(view.levels)}, not {tuple(expected_levels)}")
            predicted = [float(value) for value in view.predict(fold.feature_row)]
            if online is not None:
                online.label(index, rows[index].spread_bps)
            levels = list(view.levels)
            out.append((index, predicted))
    return out, levels, settings


def published_side(horizon: int, features: Sequence[str]):
    """The published declaration's gbm side of the frozen CRPS command, built as `live_record._compare_sides` builds it, with
    `features` as its `--feature-b` list. Returns `(name, fit, features, online factory)` and the parsed arguments."""

    from repo_model.cli import build_parser
    from repo_model.cli_eval import FITTER_FACTORIES, _online_calibration, _select_fitter, _side

    live = _load("live_record")
    argv = list(live.final_test.CRPS_COMMAND)
    kept = []
    for position, part in enumerate(argv):
        if part == "--feature-b" or (position and argv[position - 1] == "--feature-b"):
            continue
        kept.append(part)
    insert = kept.index("--report")
    kept[insert:insert] = [flag for name in features for flag in ("--feature-b", name)]
    kept[kept.index("--splits") + 1] = str(SPLITS)
    kept[kept.index("--registry") + 1] = str(live.REGISTRY)
    args = build_parser().parse_args(kept)
    projected, online = _online_calibration(
        _side(args, "b"), FITTER_FACTORIES.get(args.model_b), splits=args.splits, refit_every=args.refit_every, side="-b"
    )
    name, fit = _select_fitter(projected, side="-b")
    return (name, fit, tuple(getattr(args, "feature_b")), online), args


def new_features(horizon: int) -> Tuple[str, ...]:
    return tuple(sorted(BASE + NEW_COLUMNS))


def two_part_features(horizon: int) -> Tuple[str, ...]:
    """Variant (c)'s risk-date part: #632's inputs (`risk_gbm+settle+h41+dist_roll`) and the announced IORB change."""

    spread = _load("spread_distribution_632")
    return tuple(spread.sd.variant_features(spread.BEST, horizon)) + TWO_PART_EXTRA


def walk_command(args) -> int:
    declared = committed_declaration()
    h, variant = args.horizon, args.variant
    if h not in declared["horizons"]:
        raise SystemExit(f"horizon {h} is not declared")
    if variant not in VARIANTS + CONTROLS:
        raise SystemExit(f"{variant!r} is not a declared variant or control")
    require_unlocked([LAST_TARGET], where="spread_distribution_634")
    minimum = declared["scoring"]["minimum_history"]
    refit = declared["scoring"]["refit_every"]
    published = load_daily_panel(args.published)
    audit_panel(published)
    sd = _load("satiation_distance_598")
    registry_published = json.loads(SOURCES.read_text(encoding="utf-8"))
    settings = {}
    if variant in ("published", "gbm_funding"):
        rows = [row for row in published if row.date <= LAST_TARGET]
        live = _load("live_record")
        features = tuple(live.published_features(h))
        if variant == "published":
            (name, fit, feats, online), parsed = published_side(h, features)
            result, levels, settings = walk(
                rows, fit=fit, features=feats, online_calibration=online, registry=registry_published, horizon=h,
                minimum_history=minimum, refit_every=refit, expected_levels=[0.05, 0.25, 0.5, 0.75, 0.95],
            )
        else:
            fit = functools.partial(ml.fit_gradient_boosted_quantiles, regressors=tuple(f for f in features if f != "spread_bps"), levels=GRID)
            result, levels, settings = walk(
                rows, fit=fit, features=features, online_calibration=None, registry=registry_published, horizon=h,
                minimum_history=minimum, refit_every=refit, expected_levels=GRID,
            )
        laws = {rows[i].date.isoformat(): q for i, q in result}
    else:
        from repo_model import scarcity

        panel = [row for row in load_daily_panel(args.panel) if row.date <= LAST_TARGET]
        audit_panel(panel)
        registry = sd.measurement_fields.load_registry()
        timed_rows, timed_registry = sd.ann.arm_inputs("both", panel, registry, h)
        with sd.switched_on(), sd.h41_release.release_dating(), scarcity.own_leg_composition():
            if variant == "a_published_new":
                features = new_features(h)
                (name, fit, feats, online), parsed = published_side(h, features)
                result, levels, settings = walk(
                    timed_rows, fit=fit, features=feats, online_calibration=online, registry=timed_registry, horizon=h,
                    minimum_history=minimum, refit_every=refit, expected_levels=[0.05, 0.25, 0.5, 0.75, 0.95],
                )
                laws = {timed_rows[i].date.isoformat(): q for i, q in result}
            elif variant == "b_gbm_new":
                features = new_features(h)
                fit = functools.partial(ml.fit_gradient_boosted_quantiles, regressors=tuple(f for f in features if f != "spread_bps"), levels=GRID)
                result, levels, settings = walk(
                    timed_rows, fit=fit, features=features, online_calibration=None, registry=timed_registry, horizon=h,
                    minimum_history=minimum, refit_every=refit, expected_levels=GRID,
                )
                laws = {timed_rows[i].date.isoformat(): q for i, q in result}
            else:
                splits = load_split_declaration(SPLITS)
                features = two_part_features(h)
                record: list = []
                predictor = ml.pressure_spread_distribution_exceedance(
                    features, splits, minimum_history=minimum, structure="two_part", component_inputs=TWO_PART_EVERY_DAY,
                    record=record, grid=GRID,
                )
                report = rolling_exceedance_backtest(
                    timed_rows, predictor=predictor, model_name=variant, features=features, registry=timed_registry,
                    decision_time=DECISION, taus=(5.0, 10.0), minimum_history=minimum, refit_every=refit, end=LAST_TARGET,
                    horizon=h,
                )
                days = [fold.scored_date.isoformat() for fold in report.folds]
                if len(record) != len(days):
                    raise SystemExit(f"{variant}: {len(record)} laws recorded for {len(days)} scored days")
                laws = {day: (list(q) if q is not None else None) for day, (_part, q) in zip(days, record)}
                levels = list(GRID)
                settings = {"features": list(features), "every_day_inputs": list(TWO_PART_EVERY_DAY)}
    document = {
        "variant": variant,
        "horizon": h,
        "levels": levels,
        "panel_sha256": panel_sha256(args.published),
        "scratch_panel_sha256": panel_sha256(args.panel) if variant in VARIANTS else None,
        "features": list(features),
        "settings": json.loads(json.dumps(settings, default=str)),
        "laws": laws,
    }
    args.output.write_text(json.dumps(document, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"variant": variant, "horizon": h, "days": len(laws), "missing": sum(1 for v in laws.values() if v is None)}))
    return 0


def exceedance_command(args) -> int:
    """The persistence-logistic and calendar-climatology exceedance forecasts at the declared thresholds, at one lead."""

    declared = committed_declaration()
    rows = [row for row in load_daily_panel(args.published) if row.date <= LAST_TARGET]
    splits = load_split_declaration(SPLITS)
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    minimum = declared["scoring"]["minimum_history"]
    refit = declared["scoring"]["refit_every"]
    out = {}
    for name, predictor, features in (
        ("persistence_logistic", persistence_logistic_exceedance(minimum), ("spread_bps",)),
        ("calendar_climatology", calendar_climatology_exceedance(splits, minimum), ("days_to_month_end", "quarter_end", "spread_bps", "tax_date")),
    ):
        report = rolling_exceedance_backtest(
            rows, predictor=predictor, model_name=name, features=features, registry=registry, decision_time=DECISION,
            taus=THRESHOLDS_BP, minimum_history=minimum, refit_every=refit, end=LAST_TARGET, horizon=args.horizon,
        )
        out[name] = {
            f"{tau:g}": {fold.scored_date.isoformat(): curve[position] for fold, curve in zip(report.folds, report.curves)}
            for position, tau in enumerate(THRESHOLDS_BP)
        }
    document = {"horizon": args.horizon, "thresholds_bp": list(THRESHOLDS_BP), "panel_sha256": panel_sha256(args.published), "forecasts": out}
    args.output.write_text(json.dumps(document, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"horizon": args.horizon, "models": sorted(out)}))
    return 0


# -- scoring -------------------------------------------------------------------------------------------------------

BENCHMARKS = ("B1", "B2", "B3")
#: candidates tested against each benchmark; `published` is B3 itself.
CANDIDATES = ("gbm_funding",) + VARIANTS


def load_laws(directory: Path, variant: str) -> Dict[int, Dict[date, Optional[List[float]]]]:
    """A variant's walks at the five leads as `{h: {target day: 23 quantiles or None}}`, on the protocol's grid."""

    out: Dict[int, Dict[date, Optional[List[float]]]] = {}
    for h in HORIZONS:
        document = json.loads((directory / f"{variant}_h{h}.json").read_text(encoding="utf-8"))
        if document["horizon"] != h or document["variant"] != variant:
            raise ValueError(f"{variant}_h{h}.json is not the walk of {variant} at lead {h}")
        levels = document["levels"]
        laws = {}
        for day, quantiles in document["laws"].items():
            if quantiles is None:
                laws[date.fromisoformat(day)] = None
            elif len(levels) == len(GRID):
                laws[date.fromisoformat(day)] = [float(v) for v in quantiles]
            else:
                laws[date.fromisoformat(day)] = on_grid(quantiles, levels)
        out[h] = laws
    return out


def summarise(test: "sp.PairedTest") -> dict:
    return {
        "n": test.n,
        "benchmark_mean": test.benchmark_mean,
        "mean_difference": test.mean_difference,
        "skill": test.skill,
        "mean_difference_lower_95_one_sided": test.lower_mean_difference(),
        "skill_lower_95_one_sided": sp._bound(test.skill_draws, test.alpha, test.draws),
        "skill_upper_95_one_sided": test.upper_skill(),
        "bootstrap_p": test.p_value,
        "dm_statistic": test.dm_statistic,
        "dm_p": test.dm_p_value,
    }


def restrict(scores: Mapping[date, float], days: Sequence[date]) -> Dict[date, float]:
    return {day: scores[day] for day in days}


def pair_table(
    scores: Mapping[str, Mapping[date, float]],
    pairs: Sequence[Tuple[str, str]],
    days: Sequence[date],
    draws: int,
) -> Dict[str, dict]:
    """`paired_tests` of each (benchmark, candidate) name pair on `days`; empty when the days cannot carry the lag."""

    if len(days) <= sp.HAC_LAG:
        return {}
    chosen = [(restrict(scores[b], days), restrict(scores[c], days)) for b, c in pairs]
    tests = sp.paired_tests(chosen, seed=SEED, draws=draws)
    return {f"{b} -> {c}": summarise(test) for (b, c), test in zip(pairs, tests)}


def score_command(args) -> int:
    declared = committed_declaration()
    require_unlocked([LAST_TARGET], where="spread_distribution_634")
    draws = args.draws
    rows = load_daily_panel(args.published)
    audit_panel(rows)
    calendar = [row.date for row in rows]
    outcomes = {row.date: row.spread_bps for row in rows}
    splits = load_split_declaration(SPLITS)
    registry = json.loads(SOURCES.read_text(encoding="utf-8"))
    walks = {name: load_laws(args.walks, name) for name in CONTROLS + VARIANTS}
    decisions: Dict[str, Dict[date, Dict[int, Optional[List[float]]]]] = {}
    days_by_name = {}
    for name, laws in walks.items():
        decisions[name], days_by_name[name] = lead_forecasts(laws, calendar)
    common = sorted(set.intersection(*(set(days) for days in days_by_name.values())))
    common = [day for day in common if all(calendar[calendar.index(day) + h] <= LAST_TARGET for h in HORIZONS)]
    refuse_locked(common + [calendar[calendar.index(day) + h] for day in common for h in HORIZONS])
    if not common:
        raise SystemExit("no decision day is covered by every walk")
    b1 = pb.forecasts(pb.b1_forecast, rows, common, registry=registry, decision_time=DECISION)
    b2 = pb.forecasts(pb.b2_forecast, rows, common, registry=registry, decision_time=DECISION, splits=splits)
    forecasts: Dict[str, Dict[date, Dict[int, Sequence[float]]]] = {"B1": b1, "B2": b2}
    missing = {}
    for name in CONTROLS + VARIANTS:
        filled = sp.fill_missing({day: decisions[name][day] for day in common}, b1, common)
        label = "B3" if name == "published" else name
        forecasts[label] = filled.forecasts
        missing[label] = {"days": len(filled.missing_days), "share": filled.missing_share}
    names = ["B1", "B2", "B3", "gbm_funding", *VARIANTS]
    primary = {n: sp.day_scores(forecasts[n], outcomes, calendar) for n in names}
    secondary = {n: sp.day_scores(forecasts[n], outcomes, calendar, score=sp.upper_tail_twcrps) for n in names}
    days = sorted(primary["B1"])
    for n in names:
        if sorted(primary[n]) != days or sorted(secondary[n]) != days:
            raise SystemExit(f"{n} does not score the same decision days as B1")
    pairs = [(b, c) for c in CANDIDATES for b in BENCHMARKS] + [("B1", "B3"), ("B2", "B3")]
    ablation = [("B3", "a_published_new"), ("gbm_funding", "b_gbm_new"), ("b_gbm_new", "c_two_part_new")]
    document: dict = {
        "declaration": "metadata/spread_distribution_634.json",
        "panel_sha256": panel_sha256(args.published),
        "decision_days": {"n": len(days), "first": days[0].isoformat(), "last": days[-1].isoformat()},
        "draws": draws,
        "seed": SEED,
        "missing": missing,
        "names": names,
        "mean_primary": {n: sum(primary[n].values()) / len(days) for n in names},
        "mean_key_secondary": {n: sum(secondary[n].values()) / len(days) for n in names},
    }
    document["pooled_primary"] = pair_table(primary, pairs + ablation, days, draws)
    document["pooled_key_secondary"] = pair_table(secondary, pairs + ablation, days, draws)
    # by lead: the grid CRPS of each lead alone
    cells = {n: cell_scores(forecasts[n], outcomes, calendar, sp.grid_crps) for n in names}
    document["by_lead"] = {
        n: {str(h): sum(v for (d, hh), v in cells[n].items() if hh == h) / sum(1 for (d, hh) in cells[n] if hh == h) for h in HORIZONS}
        for n in names
    }
    # splits: regime of the decision day; pressure-day type of the target day
    by_regime: Dict[str, dict] = {}
    for label in splits.regime_labels:
        group = [day for day in days if splits.regime(day) == label]
        if len(group) > sp.HAC_LAG:
            by_regime[label] = {
                "n": len(group),
                "mean_primary": {n: sum(primary[n][d] for d in group) / len(group) for n in names},
                "tests": pair_table(primary, pairs, group, draws),
            }
    document["by_regime"] = by_regime
    position = {day: index for index, day in enumerate(calendar)}
    row_of = {row.date: row for row in rows}

    def kind_of(day: date) -> str:
        return splits.reporting_day_type(day, row_of[day].values)

    kinds = sorted({kind_of(calendar[position[d] + h]) for d in days for h in HORIZONS})
    by_type: Dict[str, dict] = {}
    for kind in kinds:
        include = lambda d, h, kind=kind: kind_of(calendar[position[d] + h]) == kind
        means = {n: day_means(cells[n], include) for n in names}
        group = sorted(set.intersection(*(set(m) for m in means.values())))
        if len(group) > sp.HAC_LAG:
            by_type[kind] = {
                "decision_days": len(group),
                "target_cells": sum(1 for d in days for h in HORIZONS if include(d, h)),
                "mean_primary": {n: sum(means[n][d] for d in group) / len(group) for n in names},
                "tests": pair_table(means, pairs, group, draws),
            }
    document["by_type"] = by_type
    # pinball at the fixed grid, MAE of the median, central coverage: pooled over cells, paired against B1 and B3
    detail: Dict[str, Dict[Tuple[date, int], Dict[str, float]]] = {n: {} for n in names}
    for n in names:
        for decision, leads in forecasts[n].items():
            for h in HORIZONS:
                y = outcomes[calendar[position[decision] + h]]
                q = leads[h]
                cell = {f"pinball_{level:g}": pinball(level, level_value(q, level), y) for level in REPORT_LEVELS}
                cell["mae_median"] = abs(level_value(q, 0.5) - y)
                cell["hit_50"] = 1.0 if level_value(q, 0.25) <= y <= level_value(q, 0.75) else 0.0
                cell["hit_90"] = 1.0 if level_value(q, 0.05) <= y <= level_value(q, 0.95) else 0.0
                detail[n][(decision, h)] = cell
    measures = [f"pinball_{level:g}" for level in REPORT_LEVELS] + ["mae_median"]
    also = {}
    for measure in measures:
        daily = {n: day_means({k: v[measure] for k, v in detail[n].items()}, lambda d, h: True) for n in names}
        also[measure] = {
            "mean": {n: sum(daily[n].values()) / len(daily[n]) for n in names},
            "tests": pair_table(daily, [(b, c) for c in CANDIDATES for b in ("B1", "B3")], days, draws),
        }
    document["also"] = also
    document["coverage"] = {
        key: {
            "pooled": {n: sum(v[key] for v in detail[n].values()) / len(detail[n]) for n in names},
            "by_regime": {
                label: {
                    n: sum(v[key] for (d, h), v in detail[n].items() if splits.regime(d) == label)
                    / max(1, sum(1 for (d, h) in detail[n] if splits.regime(d) == label))
                    for n in names
                }
                for label in by_regime
            },
        }
        for key in ("hit_50", "hit_90")
    }
    # the upper tail: Brier score of P(spread > tau), read off each law, against the exceedance benchmarks fitted at the lead
    bench_files = {h: json.loads((args.walks / f"exceed_h{h}.json").read_text(encoding="utf-8")) for h in HORIZONS}
    upper: Dict[str, dict] = {}
    for tau in THRESHOLDS_BP:
        key = f"{tau:g}"
        probability: Dict[str, Dict[Tuple[date, int], float]] = {n: {} for n in names}
        for n in names:
            for decision, leads in forecasts[n].items():
                for h in HORIZONS:
                    probability[n][(decision, h)] = exceedance(leads[h], tau)
        for model in ("persistence_logistic", "calendar_climatology"):
            probability[model] = {}
            for decision in days:
                for h in HORIZONS:
                    target = calendar[position[decision] + h].isoformat()
                    value = bench_files[h]["forecasts"][model][key].get(target)
                    if value is not None:
                        probability[model][(decision, h)] = float(value)
        every = list(names) + ["persistence_logistic", "calendar_climatology"]
        common_cells = set.intersection(*(set(probability[n]) for n in every))
        score = {
            n: {
                cell: brier(probability[n][cell], exceeds_bp(outcomes[calendar[position[cell[0]] + cell[1]]], tau))
                for cell in common_cells
            }
            for n in every
        }
        daily = {n: day_means(score[n], lambda d, h: True) for n in every}
        group = sorted(day for day in set.intersection(*(set(m) for m in daily.values())) if all((day, h) in common_cells for h in HORIZONS))
        group_daily = {n: {d: sum(score[n][(d, h)] for h in HORIZONS) / len(HORIZONS) for d in group} for n in every}
        events = sum(1 for d in group for h in HORIZONS if exceeds_bp(outcomes[calendar[position[d] + h]], tau))
        upper[key] = {
            "days": len(group),
            "event_cells": events,
            "mean_brier": {n: sum(group_daily[n].values()) / len(group) for n in every},
            "tests": pair_table(
                group_daily,
                [(b, c) for c in ("B3", "gbm_funding", *VARIANTS) for b in ("persistence_logistic", "calendar_climatology")],
                group, draws,
            )
            if events
            else {},
        }
    document["upper_tail"] = upper
    args.output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "decision_days": len(days)}))
    return 0


# -- the report ----------------------------------------------------------------------------------------------------

LABELS = {
    "B1": "B1 as-of persistence",
    "B2": "B2 calendar climatology",
    "B3": "B3 published declaration",
    "gbm_funding": "gbm, published features (phase 2)",
    "a_published_new": "(a) published + new inputs",
    "b_gbm_new": "(b) gbm + new inputs",
    "c_two_part_new": "(c) two-part + new inputs",
    "persistence_logistic": "persistence-logistic",
    "calendar_climatology": "calendar climatology",
}


def fmt(value: float, digits: int = 3) -> str:
    return "n/a" if value is None or (isinstance(value, float) and math.isnan(value)) else f"{value:+.{digits}f}"


def cell(entry: Optional[dict]) -> str:
    """skill [one-sided 95% bounds] and the lower bound of mean(d): the protocol's reading, 'would pass' marks it."""

    if not entry:
        return "n/a"
    return (
        f"{entry['skill'] * 100:+.1f}% [{entry['skill_lower_95_one_sided'] * 100:+.1f}%, {entry['skill_upper_95_one_sided'] * 100:+.1f}%]"
        f" / {fmt(entry['mean_difference_lower_95_one_sided'], 3)}"
    )


def benchmark_table(tests: Mapping[str, dict], names: Sequence[str], means: Mapping[str, float]) -> List[str]:
    lines = [
        "| model | mean | vs B1 | vs B2 | vs B3 |",
        "|---|---|---|---|---|",
    ]
    for name in names:
        row = [LABELS[name], f"{means[name]:.3f}"]
        for bench in BENCHMARKS:
            row.append(cell(tests.get(f"{bench} -> {name}")) if name != bench else "-")
        lines.append("| " + " | ".join(row) + " |")
    return lines


def report_command(args) -> int:
    d = json.loads(args.score.read_text(encoding="utf-8"))
    names = d["names"]
    out: List[str] = []
    w = out.append
    days = d["decision_days"]
    w(f"Decision days scored: {days['n']} ({days['first']} to {days['last']}); every target day on or before 2025-12-31. "
      f"Bootstrap: stationary, mean block 10, {d['draws']:,} draws, seed {d['seed']}, one-sided 95%.")
    w("")
    w("Reading of each cell: **skill [one-sided 95% lower bound, upper bound] / lower bound of the mean daily difference** "
      "(bp). Skill is mean(d) / mean(benchmark score), d = benchmark − candidate, positive favours the candidate. "
      "The protocol would call a candidate better only if the lower bound of the mean difference is above 0 against "
      "B1 and B2 and the skill is at least 3%; on development days this is a reading, not a verdict.")
    w("")
    w("### Table 1. Primary score: grid CRPS (bp), averaged over h = 1 to 5, pooled")
    w("")
    out.extend(benchmark_table(d["pooled_primary"], names, d["mean_primary"]))
    w("")
    w("### Table 2. Key secondary: upper-tail twCRPS (weight 1{y > 0 bp}), pooled")
    w("")
    out.extend(benchmark_table(d["pooled_key_secondary"], names, d["mean_key_secondary"]))
    w("")
    w("### Table 3. Ablation: each variant against the same model without the new inputs (primary score)")
    w("")
    w("| pair (parent → variant) | skill [bounds] / lower bound of mean(d) |")
    w("|---|---|")
    for key in ("B3 -> a_published_new", "gbm_funding -> b_gbm_new", "b_gbm_new -> c_two_part_new"):
        parent, variant = key.split(" -> ")
        w(f"| {LABELS[parent]} → {LABELS[variant]} | {cell(d['pooled_primary'].get(key))} |")
    w("")
    w("### Table 4. Grid CRPS by lead (bp)")
    w("")
    w("| model | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |")
    w("|---|---|---|---|---|---|")
    for n in names:
        w(f"| {LABELS[n]} | " + " | ".join(f"{d['by_lead'][n][str(h)]:.3f}" for h in HORIZONS) + " |")
    w("")
    w("### Table 5. By regime of the decision day (primary score)")
    w("")
    w("The regimes were drawn after the fact; no split is a pass requirement (protocol section 7).")
    w("")
    for label, group in d["by_regime"].items():
        w(f"**{label}** ({group['n']} decision days)")
        w("")
        out.extend(benchmark_table(group["tests"], names, group["mean_primary"]))
        w("")
    w("### Table 6. By pressure-day type of the target day (primary score)")
    w("")
    for kind, group in d["by_type"].items():
        w(f"**{kind}** ({group['decision_days']} decision days with such a target, {group['target_cells']} target cells)")
        w("")
        out.extend(benchmark_table(group["tests"], names, group["mean_primary"]))
        w("")
    w("### Table 7. Pinball loss at the fixed levels and MAE of the median (pooled, bp), paired against B1 and B3")
    w("")
    w("| measure | " + " | ".join(LABELS[n] for n in names) + " |")
    w("|---|" + "---|" * len(names))
    for measure, entry in d["also"].items():
        w(f"| {measure} | " + " | ".join(f"{entry['mean'][n]:.3f}" for n in names) + " |")
    w("")
    w("Paired skill against B1 / B3 (one-sided 95% lower bound of the mean difference):")
    w("")
    w("| measure | candidate | vs B1 | vs B3 |")
    w("|---|---|---|---|")
    for measure, entry in d["also"].items():
        for c in CANDIDATES:
            w(f"| {measure} | {LABELS[c]} | {cell(entry['tests'].get(f'B1 -> {c}'))} | {cell(entry['tests'].get(f'B3 -> {c}'))} |")
    w("")
    w("### Table 8. Central coverage (share of target cells inside the interval), pooled")
    w("")
    w("| level | nominal | " + " | ".join(LABELS[n] for n in names) + " |")
    w("|---|---|" + "---|" * len(names))
    for key, nominal in (("hit_50", 0.5), ("hit_90", 0.9)):
        w(f"| {key[-2:]}% | {nominal:.2f} | " + " | ".join(f"{d['coverage'][key]['pooled'][n]:.3f}" for n in names) + " |")
    w("")
    w("### Table 9. Upper tail: Brier score of P(spread > threshold), read off each distribution, against the models fitted at the threshold and lead")
    w("")
    for tau, entry in d["upper_tail"].items():
        w(f"**> {float(tau):+g} bp** ({entry['days']} decision days, {entry['event_cells']} event cells)")
        w("")
        models = list(entry["mean_brier"])
        w("| model | mean Brier | vs persistence-logistic | vs calendar climatology |")
        w("|---|---|---|---|")
        for model in models:
            row = [LABELS[model], f"{entry['mean_brier'][model]:.5f}"]
            for bench in ("persistence_logistic", "calendar_climatology"):
                row.append(cell(entry["tests"].get(f"{bench} -> {model}")) if model != bench else "-")
            w("| " + " | ".join(row) + " |")
        w("")
    w("### Missing forecasts (protocol section 11)")
    w("")
    for n, entry in d["missing"].items():
        w(f"- {LABELS[n]}: {entry['days']} decision days with at least one lead scored as B1's ({entry['share']:.2%}).")
    args.output.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output)}))
    return 0


def add_score_commands(sub) -> None:
    score = sub.add_parser("score", help="score the walks under the protocol")
    score.add_argument("--published", type=Path, required=True)
    score.add_argument("--walks", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)
    score.add_argument("--draws", type=int, default=sp.DRAWS)
    score.set_defaults(func=score_command)
    report = sub.add_parser("report", help="write the tables")
    report.add_argument("--score", type=Path, required=True)
    report.add_argument("--output", type=Path, required=True)
    report.set_defaults(func=report_command)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    walk_parser = sub.add_parser("walk", help="walk a variant forward at one lead")
    walk_parser.add_argument("--variant", required=True)
    walk_parser.add_argument("--horizon", type=int, required=True)
    walk_parser.add_argument("--published", type=Path, required=True)
    walk_parser.add_argument("--panel", type=Path, required=True)
    walk_parser.add_argument("--output", type=Path, required=True)
    walk_parser.set_defaults(func=walk_command)
    exceed = sub.add_parser("exceedance", help="the exceedance benchmarks at one lead")
    exceed.add_argument("--horizon", type=int, required=True)
    exceed.add_argument("--published", type=Path, required=True)
    exceed.add_argument("--output", type=Path, required=True)
    exceed.set_defaults(func=exceedance_command)
    add_score_commands(sub)
    args = parser.parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
