"""Pressure model v1 (#114): recalibration, lead time and the scorecard.

`docs/decisions/pressure-probability.md` has every candidate pressure
probability scored on one fold grid, against calendar-type climatology and the
persistence-logistic benchmark, paired, with a stationary-bootstrap interval,
split by regime and pressure-day type, by Brier with its decomposition, CORP
reliability, precision-recall and lead time. The runs themselves are
`baseline.rolling_exceedance_backtest`'s, one per candidate and horizon; this
module turns their reports into that evidence and computes nothing a report
does not carry.

* **Recalibration** (`recalibrated`) is out of fold: each refit block's
  forecasts are mapped through a Platt curve fitted on the candidate's own
  earlier forecasts whose outcomes were observable when the block was fitted.
  It never reads a block's own outcomes.
* **Lead time** (`lead_times`) is how many business days ahead a candidate
  flagged a pressure onset: the longest horizon whose forecast of the onset
  day reached an alarm level.

Scratch measurement: nothing here writes a record into `docs/runs/`.
Standard library only, like the rest of `src/` outside `ml.py`.
"""

from __future__ import annotations

import dataclasses
import math
from datetime import date
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from .baseline import (
    ExceedanceBacktestReport,
    _logistic_fit,
    _sigmoid,
    benchmark_comparison_document,
)
from .data import DailyObservation, exceeds_bp
from .splits import LookAheadError
from .metrics import (
    MetricError,
    average_precision,
    corp_decomposition,
    corp_reliability_curve,
)

__all__ = [
    "ALARM_LEVELS",
    "ONSET_QUIET_DAYS",
    "ONLINE_RECALIBRATION",
    "RECALIBRATION",
    "lead_times",
    "online_recalibrated",
    "onsets",
    "recalibrated",
    "scorecard",
]

#: The out-of-fold recalibration, declared once and named in every result.
RECALIBRATION = {
    "method": "platt_out_of_fold",
    "description": (
        "a one-variable logistic of the outcome on logit(p), fitted per threshold at each "
        "refit block on the candidate's own earlier forecasts whose scored day is at or "
        "before the block's last training label, then applied to the block's forecasts; "
        "identity until those pairs number minimum_pairs and hold minimum_events events"
    ),
    "minimum_pairs": 250,
    "minimum_events": 5,
    "probability_floor": 1e-6,
}

#: The probabilities at which a forecast counts as an alarm, for lead time and
#: for the precision and recall reported beside average precision.
ALARM_LEVELS = (0.2, 0.5)

#: An onset is an event day with no event on the panel days before it, back
#: this many rows: the first day of a pressure episode.
ONSET_QUIET_DAYS = 5


def _logit(probability: float) -> float:
    floor = RECALIBRATION["probability_floor"]
    p = min(1.0 - floor, max(floor, probability))
    return math.log(p / (1.0 - p))


def recalibrated(report: ExceedanceBacktestReport) -> ExceedanceBacktestReport:
    """`report` with every forecast recalibrated out of fold (`RECALIBRATION`).

    A refit block is the run of folds that share a training frame; its last
    label is `train_end`. A block's forecasts are mapped through a Platt curve
    fitted on the pairs `(forecast, outcome)` of every earlier scored day at or
    before that date, so no forecast is recalibrated with an outcome that was
    not observable when its model was fitted. Each threshold is recalibrated on
    its own, and the curve is then made non-increasing in tau by a running
    minimum, as every predictor's is.
    """

    count = len(report.folds)
    columns: List[List[float]] = [[0.0] * count for _ in report.taus]
    for position in range(len(report.taus)):
        forecast, _, outcomes = report.at_tau(position)
        start = 0
        while start < count:
            end_label = report.folds[start].train_end
            stop = start
            while stop < count and report.folds[stop].train_end == end_label:
                stop += 1
            past = [
                index for index in range(start) if report.folds[index].scored_date <= end_label
            ]
            events = sum(outcomes[index] for index in past)
            if (
                len(past) >= RECALIBRATION["minimum_pairs"]
                and RECALIBRATION["minimum_events"] <= events < len(past)
            ):
                b0, b1 = _logistic_fit(
                    [_logit(forecast[index]) for index in past],
                    [outcomes[index] for index in past],
                )
                for index in range(start, stop):
                    columns[position][index] = _sigmoid(b0 + b1 * _logit(forecast[index]))
            else:
                for index in range(start, stop):
                    columns[position][index] = forecast[index]
            start = stop
    curves = []
    for day in range(count):
        curve: List[float] = []
        for position in range(len(report.taus)):
            value = columns[position][day]
            curve.append(value if not curve else min(curve[-1], value))
        curves.append(tuple(curve))
    return dataclasses.replace(
        report, forecast=tuple(curves), model_name=f"{report.model_name}+recalibrated"
    )


#: The online recalibrations of #411, declared before any score and not tuned. Both update on one
#: resolved day at a time, in date order, and are the identity until `minimum_pairs` resolved days
#: holding `minimum_events` events (and not only events) have been seen, as `RECALIBRATION` is.
#: `online_platt` moves the intercept and slope of `sigmoid(a + b * logit p)` by a gradient step
#: of the log loss (starting from a = 0, b = 1; b is kept within `slope_bounds`). `adaptive_offset`
#: moves the intercept alone by `rate * (outcome - calibrated p)`, the update adaptive conformal
#: inference makes to its level, applied to the logit of the probability.
ONLINE_RECALIBRATION = {
    "online_platt": {"intercept_rate": 0.05, "slope_rate": 0.01, "slope_bounds": (0.2, 3.0)},
    "adaptive_offset": {"intercept_rate": 0.05},
    "minimum_pairs": 250,
    "minimum_events": 5,
    "probability_floor": 1e-6,
    "description": (
        "per threshold, a calibration map updated one resolved day at a time on the candidate's own "
        "earlier forecasts whose scored day is on or before the forecast's feature date (the latest "
        "day whose spread was public at its decision instant); never an outcome later than that"
    ),
}


def _require_resolved(pair_date: date, feature_date: date, scored_date: date) -> None:
    """Refuse to learn from an outcome that was not public at the forecast's decision instant."""

    if pair_date > feature_date:
        raise LookAheadError(
            f"an online recalibration of the forecast for {scored_date} would learn from the "
            f"outcome of {pair_date}, after its feature date {feature_date}"
        )


def online_recalibrated(report: ExceedanceBacktestReport, method: str) -> ExceedanceBacktestReport:
    """`report` with every forecast recalibrated online (`ONLINE_RECALIBRATION[method]`, #411).

    For the forecast of day i, the map has been updated on every earlier scored day whose
    date is on or before fold i's `feature_date`, in date order, each with its own forecast
    and outcome. Each threshold is recalibrated on its own and the curve is then made
    non-increasing in tau by a running minimum, as `recalibrated` does.
    """

    if method not in ("online_platt", "adaptive_offset"):
        raise ValueError(f"unknown online recalibration {method!r}")
    cfg = ONLINE_RECALIBRATION[method]
    floor = ONLINE_RECALIBRATION["probability_floor"]

    def logit(p: float) -> float:
        p = min(1.0 - floor, max(floor, p))
        return math.log(p / (1.0 - p))

    count = len(report.folds)
    dates = [fold.scored_date for fold in report.folds]
    if any(later < earlier for earlier, later in zip(dates, dates[1:])):
        raise ValueError("an online recalibration reads folds in date order")
    columns: List[List[float]] = [[0.0] * count for _ in report.taus]
    for position in range(len(report.taus)):
        forecast, _, outcomes = report.at_tau(position)
        a, b = 0.0, 1.0
        seen = events = 0
        nxt = 0
        for index in range(count):
            fold = report.folds[index]
            while nxt < index and dates[nxt] <= fold.feature_date:
                _require_resolved(dates[nxt], fold.feature_date, fold.scored_date)
                u = logit(forecast[nxt])
                err = outcomes[nxt] - _sigmoid(a + b * u)
                a += cfg["intercept_rate"] * err
                if method == "online_platt":
                    b = min(cfg["slope_bounds"][1], max(cfg["slope_bounds"][0], b + cfg["slope_rate"] * err * u))
                seen += 1
                events += outcomes[nxt]
                nxt += 1
            if (
                seen >= ONLINE_RECALIBRATION["minimum_pairs"]
                and ONLINE_RECALIBRATION["minimum_events"] <= events < seen
            ):
                columns[position][index] = _sigmoid(a + b * logit(forecast[index]))
            else:
                columns[position][index] = forecast[index]
    curves = []
    for day in range(count):
        curve: List[float] = []
        for position in range(len(report.taus)):
            value = columns[position][day]
            curve.append(value if not curve else min(curve[-1], value))
        curves.append(tuple(curve))
    return dataclasses.replace(report, forecast=tuple(curves), model_name=f"{report.model_name}+{method}")


def _reliability_steps(probabilities: Sequence[float], outcomes: Sequence[int]) -> List[dict]:
    """The CORP reliability diagram as its isotonic steps.

    Each step is a run of forecasts the PAV fit maps to one value: the range of
    forecasts in it, the recalibrated (observed) frequency, and how many days.
    """

    curve = corp_reliability_curve(probabilities, outcomes)
    steps: List[dict] = []
    for forecast, fitted in zip(curve.forecast, curve.recalibrated):
        if steps and steps[-1]["observed"] == fitted:
            steps[-1]["forecast_high"] = forecast
            steps[-1]["days"] += 1
        else:
            steps.append(
                {"forecast_low": forecast, "forecast_high": forecast, "observed": fitted, "days": 1}
            )
    return steps


def _alarm_counts(probabilities: Sequence[float], outcomes: Sequence[int], level: float) -> dict:
    flagged = [p >= level for p in probabilities]
    hits = sum(1 for f, y in zip(flagged, outcomes) if f and y)
    raised = sum(flagged)
    events = sum(outcomes)
    return {
        "alarm_level": level,
        "alarms": raised,
        "hits": hits,
        "precision": None if raised == 0 else hits / raised,
        "recall": None if events == 0 else hits / events,
    }


def _metrics(probabilities: Sequence[float], outcomes: Sequence[int]) -> dict:
    """Brier, its CORP decomposition, the reliability steps and precision-recall."""

    count = len(outcomes)
    entry: dict = {
        "scored_days": count,
        "events": sum(outcomes),
        "base_rate": sum(outcomes) / count,
        "brier": sum((p - y) ** 2 for p, y in zip(probabilities, outcomes)) / count,
        "alarms": [_alarm_counts(probabilities, outcomes, level) for level in ALARM_LEVELS],
    }
    try:
        decomposition = corp_decomposition(probabilities, outcomes)
        entry["decomposition"] = {
            "reliability": decomposition.reliability,
            "resolution": decomposition.resolution,
            "uncertainty": decomposition.uncertainty,
        }
        entry["reliability_steps"] = _reliability_steps(probabilities, outcomes)
        entry["average_precision"] = average_precision(probabilities, outcomes)
    except MetricError as exc:
        entry["unavailable"] = str(exc)
    return entry


def onsets(
    rows: Sequence[DailyObservation], tau: float, scored: Sequence[date]
) -> Tuple[date, ...]:
    """The scored days that open a pressure episode at `tau`.

    An event day (`spread > tau`, strictly) whose `ONSET_QUIET_DAYS` panel days
    before it carry no event, read off the panel's own rows.
    """

    wanted = set(scored)
    spreads = [(row.date, float(row.spread_bps)) for row in rows]
    found = []
    for index, (when, spread) in enumerate(spreads):
        if when not in wanted or not exceeds_bp(spread, tau) or index < ONSET_QUIET_DAYS:
            continue
        if all(
            not exceeds_bp(value, tau) for _, value in spreads[index - ONSET_QUIET_DAYS : index]
        ):
            found.append(when)
    return tuple(found)


def lead_times(
    forecasts: Mapping[int, Mapping[date, float]],
    onset_days: Sequence[date],
    level: float,
) -> dict:
    """How many business days ahead each onset was flagged at `level`.

    `forecasts[h][d]` is the horizon-`h` forecast of day `d`. An onset's lead
    time is the longest horizon whose forecast of it reached `level`, and 0
    when none did (a miss). Only onsets every horizon scored are counted.
    """

    horizons = sorted(forecasts)
    per_onset = []
    for when in onset_days:
        if not all(when in forecasts[h] for h in horizons):
            continue
        flagged = [h for h in horizons if forecasts[h][when] >= level]
        per_onset.append({"date": when.isoformat(), "lead_days": max(flagged) if flagged else 0})
    leads = [entry["lead_days"] for entry in per_onset]
    return {
        "alarm_level": level,
        "onsets": len(per_onset),
        "flagged": sum(1 for lead in leads if lead > 0),
        "mean_lead_days": None if not leads else sum(leads) / len(leads),
        "per_onset": per_onset,
    }


def scorecard(
    candidates: Mapping[str, ExceedanceBacktestReport],
    benchmarks: Mapping[str, ExceedanceBacktestReport],
    *,
    rows: Sequence[DailyObservation],
    declaration: Any,
    panel_sha256: str,
) -> dict:
    """One horizon's evidence: every candidate's metrics and its paired comparisons.

    `candidates` and `benchmarks` are reports from one panel at one horizon;
    `benchmark_comparison_document` refuses any pair not on one grid.
    """

    out: Dict[str, Any] = {"candidates": {}, "benchmarks": {}}
    for name, report in benchmarks.items():
        out["benchmarks"][name] = {
            f"{tau:g}": _metrics(*_columns(report, position))
            for position, tau in enumerate(report.taus)
        }
    for name, report in candidates.items():
        entry: dict = {
            "metrics": {
                f"{tau:g}": _metrics(*_columns(report, position))
                for position, tau in enumerate(report.taus)
            },
            "paired": {},
        }
        for bench_name, bench in benchmarks.items():
            entry["paired"][bench_name] = benchmark_comparison_document(
                report, bench, panel_sha256=panel_sha256, rows=rows, declaration=declaration
            )
        out["candidates"][name] = entry
    return out


def _columns(report: ExceedanceBacktestReport, position: int) -> Tuple[Tuple[float, ...], Tuple[int, ...]]:
    forecast, _, outcomes = report.at_tau(position)
    return forecast, outcomes
