"""Leakage-safe baselines and rolling-origin evaluation."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, List, Sequence

from .data import DailyObservation


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
