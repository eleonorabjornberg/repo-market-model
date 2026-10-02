#!/usr/bin/env python3
"""Calibration re-diagnosis: CV+ against conformal PID and Mondrian CV+ (#116).

One gbm backtest under the declaration given (the published funding
declaration, calibrated by `cross_conformal`), through
`baseline.rolling_persistence_backtest` and so on its one fold grid, with its
lockbox guard and as-of reads. At every scored day the fitted model's
`cross_conformal_parts` are recorded, and three bands are built from them:

* `cv_plus` -- CV+, the control: the band the backtest itself reported, and
  this script refuses to go on unless the parts rebuild it bit for bit;
* `online_pid` -- conformal PID on the uncalibrated vector
  (`recalibration.conformal_pid`), each band from the labels observable at its
  own decision instant, with the calendar scorecaster;
* `group_conditional` -- Mondrian CV+ over calendar type x regime
  (`recalibration.group_conditional_edges`).

Scored on every day of the grid, paired: coverage of the 0.05-0.95 band (by
calendar type, regime, their cells and the as-of volatility tercile), band
width, CRPS and the exceedance Brier at each `--tau`, each with a stationary
bootstrap interval (`evaluation_splits.split_summary`, block length the fold
horizons' overlap). CRPS and Brier are also reported as paired differences,
`cv_plus - method`: negative means the method scores worse. Coverage is not
differenced: a wider band always covers more, so each method's coverage is
reported beside its width.

The volatility tercile is #37's: the root mean square of the 20 one-step spread
changes ending at the forecast's anchor, cut at the terciles over scored days.

Writes one JSON document to `--report`, or to standard output.

    PYTHONPATH=src python3 scripts/calibration_rediagnosis.py --panel PANEL \\
        --registry metadata/sources.json --splits metadata/evaluation_splits.json \\
        --decision-time 16:00 --minimum-history 61 --refit-every 21 \\
        --calibration-folds 5 --feature spread_bps --feature ... --end 2025-12-31
"""

from __future__ import annotations

import argparse
import functools
import json
import math
import statistics
import sys
from datetime import date, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from repo_model import recalibration  # noqa: E402
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.baseline import (  # noqa: E402
    _maximum_horizon_overlap,
    _seed_from,
    panel_sha256,
    rolling_persistence_backtest,
)
from repo_model.data import exceeds_bp, load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import (  # noqa: E402
    DAY_TYPES,
    load_split_declaration,
    split_summary,
)
from repo_model.ingest import load_source_registry  # noqa: E402
from repo_model.metrics import crps_from_quantiles  # noqa: E402

METHODS = ("cv_plus", "online_pid", "group_conditional")
TERCILES = ("calm", "mid", "stressed")
VOLATILITY_WINDOW = 20


class _Recording:
    """A fitted model that records its `cross_conformal_parts` at each `predict`.

    The backtest calls `predict` once per scored day, on the view
    `with_history` returned, so the recorded parts align with its folds.
    Everything else is the model's own.
    """

    def __init__(self, model, sink):
        self._model = model
        self._sink = sink

    def __getattr__(self, name):
        return getattr(self._model, name)

    def with_history(self, history):
        return _Recording(self._model.with_history(history), self._sink)

    def predict(self, feature_row):
        self._sink.append(self._model.cross_conformal_parts(feature_row))
        return self._model.predict(feature_row)


def _recording_fitter(fitter, sink):
    def fit(train_frame, minimum_history=20, information=None):
        return _Recording(
            fitter(train_frame, minimum_history=minimum_history, information=information),
            sink,
        )

    return fit


def _volatility(spreads, anchor):
    changes = [
        spreads[position] - spreads[position - 1]
        for position in range(anchor - VOLATILITY_WINDOW + 1, anchor + 1)
    ]
    if anchor - VOLATILITY_WINDOW < 0 or any(
        change is None or not math.isfinite(change) for change in changes
    ):
        raise ValueError(f"no {VOLATILITY_WINDOW} spread changes end at row {anchor}")
    return math.sqrt(sum(change * change for change in changes) / len(changes))


def _summaries(labels, series, order, *, block_length, seed_parts, replications):
    return split_summary(
        labels,
        series,
        order,
        block_length=block_length,
        seed=_seed_from(seed_parts),
        replications=replications,
        level=0.90,
    )


def rediagnose(
    rows,
    *,
    features,
    registry,
    splits,
    decision_time,
    minimum_history,
    refit_every,
    calibration_folds,
    end,
    taus,
    replications,
    seed_material,
):
    from repo_model import ml

    sink = []
    fitter = functools.partial(
        ml.fit_gradient_boosted_quantiles,
        regressors=tuple(feature for feature in features if feature != "spread_bps"),
        calibration="cross_conformal",
        calibration_folds=calibration_folds,
    )
    report = rolling_persistence_backtest(
        rows,
        features=features,
        registry=registry,
        decision_time=decision_time,
        minimum_history=minimum_history,
        fit_model=_recording_fitter(fitter, sink),
        refit_every=refit_every,
        end=end,
    )
    if len(sink) != len(report.folds):
        raise ValueError(f"{len(sink)} recorded forecasts for {len(report.folds)} folds")
    levels = tuple(report.quantile_levels)
    dates = [row.date for row in rows]
    position = {when: index for index, when in enumerate(dates)}
    spreads = [row.spread_bps for row in rows]
    groups = {
        row.date: (splits.day_type(row.values), splits.regime(row.date)) for row in rows
    }
    rule = InformationRule(registry, tuple(features), decision_time=decision_time)

    vectors = {method: [] for method in METHODS}
    laws = {method: [] for method in METHODS}
    group_levels = []
    online_days = []
    for fold, forecast, parts in zip(report.folds, report.forecasts, sink):
        lower, upper = ml._cross_conformal_edges(parts.lows, parts.highs, levels)
        control = ml._banded(parts.vector, lower, upper)
        if control != tuple(forecast.quantiles_bps):
            raise ValueError(
                f"{fold.scored_date}: CV+ rebuilt from its parts is {control}, the "
                f"backtest reported {tuple(forecast.quantiles_bps)}"
            )
        vectors["cv_plus"].append(control)
        laws["cv_plus"].append(
            ml.law_from_band(parts.vector, lower, upper, parts.residual_low, parts.residual_high, levels)
        )
        g_lower, g_upper, used = recalibration.group_conditional_edges(
            parts.lows,
            parts.highs,
            [groups[when] for when in parts.held_out_dates],
            groups[fold.scored_date],
            levels,
        )
        group_levels.append(used)
        vectors["group_conditional"].append(ml._banded(parts.vector, g_lower, g_upper))
        laws["group_conditional"].append(
            ml.law_from_band(parts.vector, g_lower, g_upper, parts.residual_low, parts.residual_high, levels)
        )
        online_days.append(
            recalibration.OnlineDay(
                scored_date=fold.scored_date,
                anchor=fold.feature_date,
                vector=parts.vector,
                calendar=recalibration.scorecaster_calendar(
                    rows, rule, position[fold.scored_date], splits, dates
                ),
            )
        )
    actuals = [forecast.actual_bps for forecast in report.forecasts]
    bands = recalibration.conformal_pid(online_days, actuals, levels)
    for day, band, parts in zip(online_days, bands, sink):
        vectors["online_pid"].append(band.vector)
        laws["online_pid"].append(
            ml.law_from_band(
                parts.vector,
                parts.vector[0] - band.quantile,
                parts.vector[-1] + band.quantile,
                parts.residual_low,
                parts.residual_high,
                levels,
            )
        )

    count = len(actuals)
    block_length = _maximum_horizon_overlap(report.folds)
    scored = [fold.scored_date for fold in report.folds]
    regime_labels = [groups[when][1] for when in scored]
    type_labels = [groups[when][0] for when in scored]
    cell_labels = [f"{groups[when][0]} x {groups[when][1]}" for when in scored]
    regimes = splits.regime_labels
    cells = tuple(f"{kind} x {regime}" for regime in regimes for kind in DAY_TYPES)
    volatility = [_volatility(spreads, position[fold.feature_date]) for fold in report.folds]
    cuts = statistics.quantiles(volatility, n=3, method="inclusive")
    tercile_labels = [
        TERCILES[0] if value <= cuts[0] else TERCILES[1] if value <= cuts[1] else TERCILES[2]
        for value in volatility
    ]
    slicings = (
        ("all", ["all"] * count, ("all",)),
        ("regime", regime_labels, regimes),
        ("day_type", type_labels, DAY_TYPES),
        ("cell", cell_labels, cells),
    )

    def summarise(series, name, with_terciles=False):
        out = {}
        for slicing, labels, order in slicings + (
            (("volatility_tercile", tercile_labels, TERCILES),) if with_terciles else ()
        ):
            out[slicing] = _summaries(
                labels,
                series,
                order,
                block_length=block_length,
                seed_parts=seed_material + [name, slicing],
                replications=replications,
            )
        return out

    methods = {}
    per_day = {}
    for method in METHODS:
        vs = vectors[method]
        covered = [1.0 if v[0] <= y <= v[-1] else 0.0 for v, y in zip(vs, actuals)]
        width = [v[-1] - v[0] for v in vs]
        crps = [crps_from_quantiles(levels, v, y) for v, y in zip(vs, actuals)]
        briers = {}
        for tau in taus:
            probabilities = [ml._exceedance_from_law(values, knots, tau) for values, knots in laws[method]]
            briers[tau] = [
                (p - (1.0 if exceeds_bp(y, tau) else 0.0)) ** 2 for p, y in zip(probabilities, actuals)
            ]
        per_day[method] = {"crps": crps, "brier": briers}
        methods[method] = {
            "misses_below": sum(1 for v, y in zip(vs, actuals) if y < v[0]),
            "misses_above": sum(1 for v, y in zip(vs, actuals) if y > v[-1]),
            "coverage": summarise(covered, f"{method}/coverage", with_terciles=True),
            "width_bps": summarise(width, f"{method}/width"),
            "crps_bps": sum(crps) / count,
            "brier": {str(tau): sum(briers[tau]) / count for tau in taus},
        }
    paired = {}
    for method in METHODS[1:]:
        entry = {
            "crps_difference_bps": summarise(
                [a - b for a, b in zip(per_day["cv_plus"]["crps"], per_day[method]["crps"])],
                f"{method}/crps_difference",
            )
        }
        for tau in taus:
            entry[f"brier_difference_{tau:g}bp"] = summarise(
                [
                    a - b
                    for a, b in zip(per_day["cv_plus"]["brier"][tau], per_day[method]["brier"][tau])
                ],
                f"{method}/brier_difference/{tau:g}",
            )
        paired[method] = entry

    return {
        "window": {"first": scored[0].isoformat(), "last": scored[-1].isoformat(), "days": count},
        "declaration": {
            "model": "gbm",
            "features": sorted(features),
            "calibration": "cross_conformal",
            "calibration_folds": calibration_folds,
            "minimum_history": minimum_history,
            "refit_every": refit_every,
            "decision_time": decision_time.isoformat(timespec="minutes"),
        },
        "control_rebuilt_bit_for_bit": True,
        "control_crps_bps": report.crps_bps,
        "ml_libraries": dict(report.ml_libraries or {}),
        "block_length": block_length,
        "replications": replications,
        "volatility_cuts_bps": cuts,
        "taus_bp": list(taus),
        "methods": methods,
        "paired_cv_plus_minus_method": paired,
        "online_pid": {
            "constants": {
                name: getattr(recalibration, name)
                for name in (
                    "PID_STEP", "PID_STEP_WINDOW", "PID_SCALE_FLOOR", "PID_INTEGRATOR_GAIN",
                    "PID_SATURATION", "PID_TANGENT_LIMIT", "SCORECASTER_MINIMUM",
                    "SCORECASTER_INDICATOR_MINIMUM",
                )
            },
            "indicators": list(recalibration.SCORECASTER_INDICATORS),
            "saturated_days": sum(band.saturated for band in bands),
            "days_before_first_label": sum(1 for band in bands if band.observed == 0),
            "mean_quantile_bps": sum(band.quantile for band in bands) / count,
        },
        "group_conditional": {
            "levels_used": {
                level: group_levels.count(level) for level in ("cell", "day_type", "pooled")
            },
        },
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--registry", type=Path, default=ROOT / "metadata" / "sources.json")
    parser.add_argument("--splits", type=Path, default=ROOT / "metadata" / "evaluation_splits.json")
    parser.add_argument("--feature", action="append", required=True)
    parser.add_argument("--decision-time", default="16:00")
    parser.add_argument("--minimum-history", type=int, required=True)
    parser.add_argument("--refit-every", type=int, required=True)
    parser.add_argument("--calibration-folds", type=int, default=5)
    parser.add_argument("--end", type=date.fromisoformat, default=None)
    parser.add_argument("--tau", type=float, action="append", default=None)
    parser.add_argument("--replications", type=int, default=2000)
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args(argv)
    features = tuple(args.feature)
    result = rediagnose(
        load_daily_panel(args.panel),
        features=features,
        registry=load_source_registry(args.registry),
        splits=load_split_declaration(args.splits),
        decision_time=time.fromisoformat(args.decision_time),
        minimum_history=args.minimum_history,
        refit_every=args.refit_every,
        calibration_folds=args.calibration_folds,
        end=args.end,
        taus=tuple(args.tau or (5.0, 10.0)),
        replications=args.replications,
        seed_material=["calibration_rediagnosis", panel_sha256(args.panel)],
    )
    result["panel_sha256"] = panel_sha256(args.panel)
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.report is None:
        print(text)
    else:
        args.report.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
