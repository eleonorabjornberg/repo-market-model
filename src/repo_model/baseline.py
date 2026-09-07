"""Leakage-safe baselines and rolling-origin evaluation."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from typing import Callable, Iterable, List, Sequence, Tuple

from .data import DailyObservation


#: `event_eval.FitPredict`, restated as a type alias rather than imported, so
#: `baseline` does not depend on the evaluator it feeds. The evaluator validates
#: the shape at the boundary; this is documentation with a name.
ExceedancePredictor = Callable[
    [Sequence[date], Sequence[float], Sequence[date], Sequence[float]],
    Sequence[Sequence[float]],
]


@dataclass(frozen=True)
class Forecast:
    actual_bps: float
    predicted_bps: float
    lower_bps: float
    upper_bps: float


@dataclass(frozen=True)
class BacktestReport:
    forecasts: Sequence[Forecast]
    mae_bps: float
    interval_coverage: float


def _quantile(values: Sequence[float], probability: float) -> float:
    if not values:
        raise ValueError("quantile requires at least one value")
    ordered = sorted(values)
    position = probability * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def rolling_persistence_backtest(
    observations: Iterable[DailyObservation],
    minimum_history: int = 20,
    interval_probability: float = 0.90,
) -> BacktestReport:
    """Forecast tomorrow's spread as today's spread.

    Prediction intervals use only previously observed one-step residuals, ensuring
    that no future information leaks into a forecast.
    """

    rows = list(observations)
    if len(rows) <= minimum_history:
        raise ValueError("not enough observations for requested minimum history")
    alpha = (1.0 - interval_probability) / 2.0
    residuals: List[float] = []
    forecasts: List[Forecast] = []

    for index in range(1, len(rows)):
        prediction = rows[index - 1].spread_bps
        actual = rows[index].spread_bps
        if index >= minimum_history:
            lower = prediction + _quantile(residuals, alpha)
            upper = prediction + _quantile(residuals, 1.0 - alpha)
            forecasts.append(Forecast(actual, prediction, lower, upper))
        residuals.append(actual - prediction)

    mae = sum(abs(item.actual_bps - item.predicted_bps) for item in forecasts) / len(forecasts)
    coverage = sum(
        item.lower_bps <= item.actual_bps <= item.upper_bps for item in forecasts
    ) / len(forecasts)
    return BacktestReport(forecasts, mae, coverage)


def climatology_exceedance(minimum_history: int = 20) -> ExceedancePredictor:
    """Unconditional exceedance from the training distribution alone.

    The reference `AGENT_CONTRACT.md`, "Decided: stress target and event
    holdouts", names in "Metrics": "Brier skill score **against climatology**".
    A climatology is what a skill score is measured against, so it is the first
    exceedance predictor this repo needs and the only one it needs before there
    is something to compare. It is also the honest predictor for a knowledge
    holdout, where the whole question is what a model that has seen only calm
    history says about a crisis it was never shown.

    Shape is `event_eval.FitPredict`: called once with the training rows, the
    scored dates and the tau family, returning `P(value > tau)` per scored day
    per tau. `P(Y > tau)` is the fraction of training values strictly above
    `tau` -- strictly, matching the contract's `P(spread > tau)` and the label
    columns' `stress_gt_*`.

    Two properties worth stating, because both are deliberate:

    * **The curve is the same on every scored day.** A climatology is
      unconditional by definition; a predictor whose curve moved with the day
      would be conditioning on something, and then it would not be the baseline
      a skill score is measured against. `event_eval` still scores each day
      separately against its own realized value, so the report shows a flat
      predicted curve beside a path that moves, which is the comparison.

    * **No smoothing, no prior.** With no training row above 50bp the answer is
      `0.0`, and it stays `0.0` rather than being nudged to `1/(n+2)`. A
      Laplace correction here would be a prior nobody declared, and it would
      quietly convert the most informative result this evaluator can produce --
      a model that put *no* weight where the event actually went -- into a small
      number that looks like a poor forecast rather than an absent one. Scoring
      rules that cannot take a zero are the caller's problem to raise, and
      `event_eval` computes none.

    Monotonicity is automatic: `taus` arrives strictly ascending, and the count
    of values above a larger threshold cannot exceed the count above a smaller
    one, so `_validate_predictions`' non-increasing check is satisfied by
    construction rather than by rounding.

    Args:
        minimum_history: the shortest training set that may produce a curve. A
            fraction over five rows is not a climatology, and at an event
            boundary the training set is whatever survived the purge -- which
            can be very short without anything else objecting.

    Returns:
        A `fit_predict` callable suitable for `event_eval.evaluate_event_window`.

    Raises:
        ValueError: at call time, if the training set is shorter than
            `minimum_history`. A `ValueError` rather than a bespoke type so the
            CLI dispatcher's `(OSError, ValueError)` already covers it.
    """

    if minimum_history < 1:
        raise ValueError(f"minimum_history must be positive, got {minimum_history}")

    def fit_predict(
        train_dates: Sequence[date],
        train_values: Sequence[float],
        test_dates: Sequence[date],
        taus: Sequence[float],
    ) -> List[Tuple[float, ...]]:
        history = [float(value) for value in train_values]
        if len(history) < minimum_history:
            raise ValueError(
                f"climatology needs at least {minimum_history} training rows, got "
                f"{len(history)}; at an event boundary the training set is whatever "
                "cleared the purge gap, and a curve from a handful of rows is not a "
                "climatology"
            )
        denominator = float(len(history))
        curve = tuple(
            sum(1 for value in history if value > float(tau)) / denominator
            for tau in taus
        )
        return [curve for _ in test_dates]

    return fit_predict
