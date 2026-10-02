#!/usr/bin/env python3
"""Conformal PID's constants by nested walk-forward selection (#125).

One gbm backtest under the declaration given (the published funding
declaration, calibrated by `cross_conformal`), through
`baseline.rolling_persistence_backtest` and so on its one fold grid, with its
lockbox guard and as-of reads, recorded as `calibration_rediagnosis.py` records
it (#116). On its uncalibrated vectors, conformal PID is run once at every
point of the declared grid (`recalibration.PID_GRID`); each run's band on a day
uses only the labels observable at that day's decision. Then:

* `nested_pid` -- the headline. At each refit of the backtest's grid (every
  `--refit-every` scored days) the constants for the coming block are those
  with the least pooled CRPS over the scored days whose labels were observable
  at the refit (`recalibration.nested_selection`). With none, #122's.
* `fixed_pid` -- the control: #122's constants (`recalibration.DECLARED_PID`)
  throughout. It is #116's `online_pid` band.
* `cv_plus` -- the published calibration, rebuilt from its parts and checked
  bit for bit against the band the backtest reported.

Each is scored on every day of the grid, paired: CRPS, coverage of the
0.05-0.95 band and its gap from 0.90, band width, and the exceedance Brier at
each `--tau`, by regime and by calendar day type, with stationary bootstrap
intervals (`evaluation_splits.split_summary`). CRPS and Brier are also
reported as paired differences `other - nested_pid`: positive means the nested
scheme scores better.

Two secondary tables, labelled as such in the report:

* `split_sample` -- one fixed point chosen by pooled CRPS on the scored days
  from the window's start to `SPLIT_SELECTION_LAST`, scored on the days from
  `SPLIT_EVALUATION_FIRST` on, beside the nested scheme, #122's constants and
  CV+ on the same days. A robustness check, never the selection.
* `full_grid` -- every grid point on the whole window. Descriptive, not for
  selection.

Writes one JSON document to `--report`, or to standard output.

    PYTHONPATH=src python3 scripts/pid_constant_selection.py --panel PANEL \\
        --registry metadata/sources.json --splits metadata/evaluation_splits.json \\
        --decision-time 16:00 --minimum-history 61 --refit-every 21 \\
        --calibration-folds 5 --feature spread_bps --feature ... --end 2025-12-31
"""

from __future__ import annotations

import argparse
import functools
import json
import sys
from datetime import date, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from calibration_rediagnosis import _recording_fitter, _summaries  # noqa: E402
from repo_model import recalibration  # noqa: E402
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.baseline import (  # noqa: E402
    _maximum_horizon_overlap,
    panel_sha256,
    rolling_persistence_backtest,
)
from repo_model.data import load_daily_panel  # noqa: E402
from repo_model.evaluation_splits import (  # noqa: E402
    DAY_TYPES,
    load_split_declaration,
)
from repo_model.ingest import load_source_registry  # noqa: E402
from repo_model.metrics import crps_from_quantiles  # noqa: E402

METHODS = ("nested_pid", "fixed_pid", "cv_plus")
NOMINAL = 0.90

#: The split-sample check's selection window ends here, and its evaluation
#: window starts on the next day (#125, item 3).
SPLIT_SELECTION_LAST = date(2022, 12, 31)
SPLIT_EVALUATION_FIRST = date(2023, 1, 1)


def _constants(point):
    return dict(point._asdict())


def select(
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
    groups = {
        row.date: (splits.day_type(row.values), splits.regime(row.date)) for row in rows
    }
    rule = InformationRule(registry, tuple(features), decision_time=decision_time)
    actuals = [forecast.actual_bps for forecast in report.forecasts]
    count = len(actuals)

    cv_vectors, cv_laws, online_days = [], [], []
    for fold, forecast, parts in zip(report.folds, report.forecasts, sink):
        lower, upper = ml._cross_conformal_edges(parts.lows, parts.highs, levels)
        control = ml._banded(parts.vector, lower, upper)
        if control != tuple(forecast.quantiles_bps):
            raise ValueError(
                f"{fold.scored_date}: CV+ rebuilt from its parts is {control}, the "
                f"backtest reported {tuple(forecast.quantiles_bps)}"
            )
        cv_vectors.append(control)
        cv_laws.append(
            ml.law_from_band(parts.vector, lower, upper, parts.residual_low, parts.residual_high, levels)
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

    def per_day(vectors, laws):
        crps = [crps_from_quantiles(levels, v, y) for v, y in zip(vectors, actuals)]
        briers = {}
        for tau in taus:
            probabilities = [ml._exceedance_from_law(values, knots, tau) for values, knots in laws]
            briers[tau] = [(p - (1.0 if y > tau else 0.0)) ** 2 for p, y in zip(probabilities, actuals)]
        return {
            "vectors": vectors,
            "covered": [1.0 if v[0] <= y <= v[-1] else 0.0 for v, y in zip(vectors, actuals)],
            "width": [v[-1] - v[0] for v in vectors],
            "crps": crps,
            "brier": briers,
        }

    grid = recalibration.PID_GRID
    declared = grid.index(recalibration.DECLARED_PID)
    runs = []
    saturated = []
    for point in grid:
        bands = recalibration.conformal_pid(online_days, actuals, levels, constants=point)
        saturated.append(sum(band.saturated for band in bands))
        laws = [
            ml.law_from_band(
                parts.vector,
                parts.vector[0] - band.quantile,
                parts.vector[-1] + band.quantile,
                parts.residual_low,
                parts.residual_high,
                levels,
            )
            for band, parts in zip(bands, sink)
        ]
        runs.append(per_day([band.vector for band in bands], laws))

    scored = [fold.scored_date for fold in report.folds]
    anchors = [fold.feature_date for fold in report.folds]
    losses = [tuple(run["crps"][i] for run in runs) for i in range(count)]
    nested = recalibration.nested_selection(
        scored, anchors, losses, refit_every, fallback=declared
    )

    def pick(field, chooser):
        return [runs[chooser(i)][field][i] for i in range(count)]

    def picked(chooser):
        return {
            "covered": pick("covered", chooser),
            "width": pick("width", chooser),
            "crps": pick("crps", chooser),
            "brier": {
                tau: [runs[chooser(i)]["brier"][tau][i] for i in range(count)] for tau in taus
            },
        }

    series = {
        "nested_pid": picked(lambda i: nested.per_day[i]),
        "fixed_pid": picked(lambda i: declared),
        "cv_plus": per_day(cv_vectors, cv_laws),
    }

    block_length = _maximum_horizon_overlap(report.folds)
    regime_labels = [groups[when][1] for when in scored]
    type_labels = [groups[when][0] for when in scored]
    regimes = splits.regime_labels

    def summarise(values, name, positions=None):
        chosen = range(count) if positions is None else positions
        out = {}
        for slicing, labels, order in (
            ("all", ["all"] * count, ("all",)),
            ("regime", regime_labels, regimes),
            ("day_type", type_labels, DAY_TYPES),
        ):
            out[slicing] = _summaries(
                [labels[i] for i in chosen],
                [values[i] for i in chosen],
                order,
                block_length=block_length,
                seed_parts=seed_material + [name, slicing],
                replications=replications,
            )
        return out

    def scores(data, name, positions=None):
        chosen = list(range(count) if positions is None else positions)
        n = len(chosen)
        return {
            "coverage": summarise(data["covered"], f"{name}/coverage", chosen),
            "coverage_gap_from_nominal": sum(data["covered"][i] for i in chosen) / n - NOMINAL,
            "width_bps": summarise(data["width"], f"{name}/width", chosen),
            "crps_bps": summarise(data["crps"], f"{name}/crps", chosen),
            "brier": {
                f"{tau:g}bp": summarise(data["brier"][tau], f"{name}/brier/{tau:g}", chosen)
                for tau in taus
            },
        }

    def paired(target, others, prefix, positions=None):
        out = {}
        for other in others:
            a, b = series_of[other], target
            entry = {
                "crps_difference_bps": summarise(
                    [x - y for x, y in zip(a["crps"], b["crps"])],
                    f"{prefix}/{other}/crps_difference",
                    positions,
                )
            }
            for tau in taus:
                entry[f"brier_difference_{tau:g}bp"] = summarise(
                    [x - y for x, y in zip(a["brier"][tau], b["brier"][tau])],
                    f"{prefix}/{other}/brier_difference/{tau:g}",
                    positions,
                )
            out[f"{other}_minus_{prefix}"] = entry
        return out

    series_of = dict(series)
    methods = {method: scores(series[method], method) for method in METHODS}
    headline_paired = paired(series["nested_pid"], ("fixed_pid", "cv_plus"), "nested_pid")

    # Split-sample check: one point chosen on the early days, scored on the late ones.
    early = [i for i, when in enumerate(scored) if when <= SPLIT_SELECTION_LAST]
    late = [i for i, when in enumerate(scored) if when >= SPLIT_EVALUATION_FIRST]
    split_choice, split_days = recalibration.select_constants(
        [(scored[i], losses[i]) for i in early], SPLIT_SELECTION_LAST, len(grid), fallback=declared
    )
    series_of["split_pid"] = picked(lambda i: split_choice)
    split_sample = {
        "label": "secondary: a robustness check, never the selection",
        "selection_window": {
            "first": scored[early[0]].isoformat() if early else None,
            "last": scored[early[-1]].isoformat() if early else None,
            "days": split_days,
        },
        "evaluation_window": {
            "first": scored[late[0]].isoformat() if late else None,
            "last": scored[late[-1]].isoformat() if late else None,
            "days": len(late),
        },
        "chosen": _constants(grid[split_choice]),
        "chosen_index": split_choice,
    }
    if late:
        split_sample["methods"] = {
            name: scores(series_of[name], f"split/{name}", late)
            for name in ("split_pid", "nested_pid", "fixed_pid", "cv_plus")
        }
        split_sample["paired"] = paired(
            series_of["split_pid"], ("fixed_pid", "cv_plus"), "split_pid", late
        )

    full_grid = []
    for index, (point, run) in enumerate(zip(grid, runs)):
        full_grid.append(
            {
                "index": index,
                "constants": _constants(point),
                "crps_bps": sum(run["crps"]) / count,
                "coverage": sum(run["covered"]) / count,
                "width_bps": sum(run["width"]) / count,
                "brier": {f"{tau:g}bp": sum(run["brier"][tau]) / count for tau in taus},
                "saturated_days": saturated[index],
                "nested_blocks_chosen": sum(1 for block in nested.blocks if block.chosen == index),
            }
        )

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
        "taus_bp": list(taus),
        "grid": {
            "points": len(grid),
            "declared_index": declared,
            "steps": list(recalibration.PID_GRID_STEPS),
            "integrator_gains": list(recalibration.PID_GRID_INTEGRATOR_GAINS),
            "saturations": list(recalibration.PID_GRID_SATURATIONS),
            "scorecaster_minimums": list(recalibration.PID_GRID_SCORECASTER_MINIMUMS),
        },
        "methods": methods,
        "paired_other_minus_nested": headline_paired,
        "nested_selection": [
            {
                "first_scored": block.first_scored.isoformat(),
                "anchor": block.anchor.isoformat(),
                "past_days": block.past_days,
                "chosen_index": block.chosen,
                "chosen": _constants(grid[block.chosen]),
            }
            for block in nested.blocks
        ],
        "split_sample": split_sample,
        "full_grid": {"label": "descriptive: not for selection", "points": full_grid},
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
    result = select(
        load_daily_panel(args.panel),
        features=tuple(args.feature),
        registry=load_source_registry(args.registry),
        splits=load_split_declaration(args.splits),
        decision_time=time.fromisoformat(args.decision_time),
        minimum_history=args.minimum_history,
        refit_every=args.refit_every,
        calibration_folds=args.calibration_folds,
        end=args.end,
        taus=tuple(args.tau or (5.0, 10.0)),
        replications=args.replications,
        seed_material=["pid_constant_selection", panel_sha256(args.panel)],
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
