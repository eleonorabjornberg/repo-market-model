"""Recalibrating a pressure probability, walk-forward: the bake-off (#138).

A pressure probability can rank pressure days well and still be miscalibrated,
and recalibration is the cheapest Brier gain. With 70-160 positive days the
literature finds isotonic recalibration overfits and 2-3-parameter curves hold
up better (van der Laan & Alaa 2024; Johansson et al., PMLR v152). This module
fits four recalibrators on the same raw forecasts and leaves the choice to the
evidence:

* `isotonic`, **the control**: the CORP isotonic fit of outcomes on forecasts
  (`metrics._recalibrate`, the fit every published reliability diagram is
  drawn with), read as a right-continuous step function (`metrics._step_lookup`).
  It is **not** the published recalibration: `corp_isotonic` in an exceedance
  record is the method name of the reliability curve, a diagnostic drawn after
  scoring, and no published forecast is passed through it (#211);
* `platt`: a one-variable logistic of the outcome on `logit(p)`, exactly
  `pressure.RECALIBRATION`'s curve. **This is the recalibration pressure model v1
  is published with** (`PUBLISHED`); the published `exceedance_gbm` is not
  recalibrated at all;
* `beta`: beta calibration (Kull, Silva Filho and Flach, 2017), a logistic of
  the outcome on `ln p` and `-ln(1 - p)` with both shape slopes held
  non-negative: a negative one is dropped and the curve refitted without it, as
  the paper does;
* `platt_recency`: Platt with exponential recency weights, half-life
  `RECENCY_HALF_LIFE_DAYS` scored days, declared before any scoring and not
  tuned.

**Venn-Abers is a check, not a candidate** (`venn_abers`): the inductive
Venn-Abers pair `[p0, p1]` of each forecast (Vovk and Petej, 2014), the
isotonic fit with the day added once as a non-event and once as an event. A
wide interval marks where the calibration data are too thin to trust any
recalibrator.

**Walk-forward.** A refit block is the run of scored days that share a
training frame; its last training label is `train_end`. Each block's forecasts
are mapped through a curve fitted on the pairs `(forecast, outcome)` of every
earlier scored day at or before `train_end`, so no curve sees an outcome that
was not observable when the block's model was fitted. `fit` refuses any later
pair with `LookAheadError`. Until those pairs number `MINIMUM_PAIRS` and hold
`MINIMUM_EVENTS` events (and at least one non-event), every method is the
identity, `pressure.RECALIBRATION`'s gate, so all four start on the same day.

Every constant here was declared before any scoring and none was searched.
Standard library only, like the rest of `src/` outside `ml.py`: beta
calibration is a three-parameter logistic, solved here as the other logistics
in `src/` are, so it needs no package.
"""

from __future__ import annotations

import math
from datetime import date
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from .baseline import _logistic_fit, _sigmoid
from .metrics import (
    MetricError,
    _recalibrate,
    _step_lookup,
    corp_decomposition,
    stationary_bootstrap_interval,
)
from .splits import LookAheadError

__all__ = [
    "CALIBRATORS",
    "CONTROL",
    "PUBLISHED",
    "MINIMUM_EVENTS",
    "MINIMUM_PAIRS",
    "PROBABILITY_FLOOR",
    "RECENCY_HALF_LIFE_DAYS",
    "beta_parameters",
    "blocks",
    "declaration",
    "fit",
    "monotone_curves",
    "past_positions",
    "venn_abers",
    "walk_forward",
]

CALIBRATORS = ("isotonic", "platt", "beta", "platt_recency")
#: The control every candidate is paired against (#138).
CONTROL = "isotonic"
#: The calibrator the published pressure model v1 uses (`pressure.RECALIBRATION`,
#: `platt_out_of_fold`). A candidate beating it beats what is published (#211).
PUBLISHED = "platt"

#: `pressure.RECALIBRATION`'s gate, for every method: identity until the past
#: pairs number this many...
MINIMUM_PAIRS = 250
#: ...and hold this many events.
MINIMUM_EVENTS = 5
#: `logit` and `ln` read a probability clipped to [floor, 1 - floor].
PROBABILITY_FLOOR = 1e-6

#: The recency weight's half-life, in scored days: two years of business days.
#: Declared before any scoring and not tuned (#138). The weights are scaled to
#: average 1, so the logistic's slope penalty bears on them as on Platt's.
RECENCY_HALF_LIFE_DAYS = 504


def declaration() -> dict:
    """Every constant the bake-off ran with, as a result names them."""

    return {
        "calibrators": list(CALIBRATORS),
        "control": CONTROL,
        "minimum_pairs": MINIMUM_PAIRS,
        "minimum_events": MINIMUM_EVENTS,
        "probability_floor": PROBABILITY_FLOOR,
        "recency_half_life_scored_days": RECENCY_HALF_LIFE_DAYS,
        "fitting": (
            "walk-forward: each refit block's forecasts are mapped through a curve fitted on "
            "the forecast's own earlier pairs whose scored day is at or before the block's last "
            "training label; identity until those pairs number minimum_pairs and hold "
            "minimum_events events"
        ),
        "venn_abers": "inductive Venn-Abers [p0, p1] on the same pairs; a check, not a candidate",
    }


def _clip(probability: float) -> float:
    return min(1.0 - PROBABILITY_FLOOR, max(PROBABILITY_FLOOR, float(probability)))


def _logit(probability: float) -> float:
    p = _clip(probability)
    return math.log(p / (1.0 - p))


# --------------------------------------------------------------------------
# The curves
# --------------------------------------------------------------------------


def _isotonic(pairs: Sequence[Tuple[float, int]]) -> Callable[[float], float]:
    xs = [p for p, _ in pairs]
    fitted = _recalibrate(xs, [y for _, y in pairs])
    order = sorted(range(len(xs)), key=lambda index: xs[index])
    keys = [xs[index] for index in order]
    values = [fitted[index] for index in order]
    return lambda p: _step_lookup(keys, values, p)


def _platt(pairs: Sequence[Tuple[float, int]]) -> Callable[[float], float]:
    b0, b1 = _logistic_fit([_logit(p) for p, _ in pairs], [y for _, y in pairs])
    return lambda p: _sigmoid(b0 + b1 * _logit(p))


def _weighted_logistic(
    xs: Sequence[float], ys: Sequence[int], ws: Sequence[float]
) -> Tuple[float, float]:
    """`baseline._logistic_fit`'s objective with each pair's log loss weighted."""

    def objective(b0: float, b1: float) -> float:
        total = 0.5 * b1 * b1
        for x, y, w in zip(xs, ys, ws):
            z = b0 + b1 * x
            total += w * ((z if z > 0 else 0.0) + math.log1p(math.exp(-abs(z))) - y * z)
        return total

    b0, b1 = 0.0, 0.0
    current = objective(b0, b1)
    for _ in range(200):
        g0 = g1 = h00 = h01 = h11 = 0.0
        for x, y, w in zip(xs, ys, ws):
            p = _sigmoid(b0 + b1 * x)
            v = w * p * (1.0 - p)
            g0 += w * (p - y)
            g1 += w * (p - y) * x
            h00 += v
            h01 += v * x
            h11 += v * x * x
        g1 += b1
        h11 += 1.0
        determinant = h00 * h11 - h01 * h01
        if determinant <= 0.0:
            break
        d0 = (h11 * g0 - h01 * g1) / determinant
        d1 = (h00 * g1 - h01 * g0) / determinant
        step = 1.0
        while step > 1e-10:
            trial = objective(b0 - step * d0, b1 - step * d1)
            if trial <= current:
                break
            step /= 2.0
        else:
            break
        b0, b1, current = b0 - step * d0, b1 - step * d1, trial
        if max(abs(step * d0), abs(step * d1)) < 1e-12:
            break
    return b0, b1


def _weighted_platt(
    pairs: Sequence[Tuple[float, int]], *, half_life: float = RECENCY_HALF_LIFE_DAYS
) -> Callable[[float], float]:
    """Platt with weight `0.5 ** (age / half_life)`, age in scored days from the latest pair."""

    count = len(pairs)
    raw = [0.5 ** ((count - 1 - k) / half_life) for k in range(count)]
    scale = count / sum(raw)
    b0, b1 = _weighted_logistic(
        [_logit(p) for p, _ in pairs], [y for _, y in pairs], [w * scale for w in raw]
    )
    return lambda p: _sigmoid(b0 + b1 * _logit(p))


def beta_parameters(pairs: Sequence[Tuple[float, int]]) -> Tuple[float, float, float]:
    """Beta calibration's `(a, b, c)`: `P = sigmoid(a ln p - b ln(1 - p) + c)`, `a, b >= 0`.

    Fitted as a two-variable logistic on `(ln p, -ln(1 - p))` with
    `onset._logistic2`'s objective (`baseline._logistic_fit`'s, two slopes). A
    negative slope is dropped and the other refitted alone (Kull et al., 2017,
    section 3.3); if that one is negative too, the curve is the base rate.
    """

    from .onset import _logistic2

    xs = [(math.log(_clip(p)), -math.log(1.0 - _clip(p))) for p, _ in pairs]
    ys = [y for _, y in pairs]
    c, a, b = _logistic2(xs, ys)
    if a >= 0.0 and b >= 0.0:
        return a, b, c
    if a < 0.0:
        c, b = _logistic_fit([x2 for _, x2 in xs], ys)
        a = 0.0
    else:
        c, a = _logistic_fit([x1 for x1, _ in xs], ys)
        b = 0.0
    if a < 0.0 or b < 0.0:
        rate = sum(ys) / len(ys)
        return 0.0, 0.0, math.log(rate / (1.0 - rate))
    return a, b, c


def _beta(pairs: Sequence[Tuple[float, int]]) -> Callable[[float], float]:
    a, b, c = beta_parameters(pairs)
    return lambda p: _sigmoid(a * math.log(_clip(p)) - b * math.log(1.0 - _clip(p)) + c)


_FITTERS = {
    "isotonic": _isotonic,
    "platt": _platt,
    "beta": _beta,
    "platt_recency": _weighted_platt,
}


def fit(
    method: str, pairs: Sequence[Tuple[date, float, int]], fitted_at: date
) -> Callable[[float], float]:
    """The `method` curve fitted on `pairs`, `(scored day, forecast, outcome)` in date order.

    Raises:
        LookAheadError: if any pair's scored day is after `fitted_at`: its
            outcome was not observable when the curve was fitted.
        ValueError: for a method that is not in `CALIBRATORS`.
    """

    if method not in _FITTERS:
        raise ValueError(f"unknown recalibrator {method!r}; expected one of {CALIBRATORS}")
    late = [when for when, _, _ in pairs if when > fitted_at]
    if late:
        raise LookAheadError(
            f"a {method} curve fitted at {fitted_at} was handed the outcome of {late[0]}, "
            f"after its fitting date"
        )
    return _FITTERS[method]([(float(p), int(y)) for _, p, y in pairs])


# --------------------------------------------------------------------------
# Walk-forward
# --------------------------------------------------------------------------


def blocks(
    scored_dates: Sequence[date], train_ends: Sequence[date]
) -> List[Tuple[int, int, date]]:
    """`(start, stop, train_end)` per refit block: the runs of one training frame."""

    out: List[Tuple[int, int, date]] = []
    start = 0
    while start < len(scored_dates):
        stop = start
        while stop < len(scored_dates) and train_ends[stop] == train_ends[start]:
            stop += 1
        out.append((start, stop, train_ends[start]))
        start = stop
    return out


def past_positions(
    scored_dates: Sequence[date], train_ends: Sequence[date], start: int
) -> List[int]:
    """The earlier scored days whose outcome was observable at block `start`'s fit."""

    end = train_ends[start]
    return [index for index in range(start) if scored_dates[index] <= end]


def _ready(outcomes: Sequence[int], past: Sequence[int]) -> bool:
    events = sum(outcomes[index] for index in past)
    return len(past) >= MINIMUM_PAIRS and MINIMUM_EVENTS <= events < len(past)


def walk_forward(
    method: str,
    forecasts: Sequence[float],
    outcomes: Sequence[int],
    scored_dates: Sequence[date],
    train_ends: Sequence[date],
) -> Tuple[float, ...]:
    """Every forecast recalibrated by `method`, each block from its observable past."""

    column = [float(p) for p in forecasts]
    for start, stop, end in blocks(scored_dates, train_ends):
        past = past_positions(scored_dates, train_ends, start)
        if not _ready(outcomes, past):
            continue
        curve = fit(
            method,
            [(scored_dates[i], forecasts[i], outcomes[i]) for i in past],
            end,
        )
        for index in range(start, stop):
            column[index] = curve(forecasts[index])
    return tuple(column)


def venn_abers(
    forecasts: Sequence[float],
    outcomes: Sequence[int],
    scored_dates: Sequence[date],
    train_ends: Sequence[date],
) -> List[Optional[Tuple[float, float]]]:
    """The inductive Venn-Abers pair `(p0, p1)` per scored day; `None` before the gate.

    `p_y` is the isotonic fit, on the block's observable past pairs plus the
    day itself labelled `y`, read at the day's forecast.
    """

    out: List[Optional[Tuple[float, float]]] = [None] * len(forecasts)
    for start, stop, end in blocks(scored_dates, train_ends):
        past = past_positions(scored_dates, train_ends, start)
        if not _ready(outcomes, past):
            continue
        if any(scored_dates[i] > end for i in past):
            raise LookAheadError(f"a Venn-Abers pair at {end} read a later outcome")
        xs = [float(forecasts[i]) for i in past]
        ys = [int(outcomes[i]) for i in past]
        for index in range(start, stop):
            x = float(forecasts[index])
            pair = []
            for label in (0, 1):
                fitted = _recalibrate(xs + [x], ys + [label])
                pair.append(fitted[-1])
            out[index] = (pair[0], pair[1])
    return out


def monotone_curves(curves: Sequence[Sequence[float]]) -> List[Tuple[float, ...]]:
    """Each day's curve made non-increasing in tau by a running minimum, as `pressure.recalibrated` does."""

    out = []
    for curve in curves:
        running: List[float] = []
        for value in curve:
            running.append(value if not running else min(running[-1], value))
        out.append(tuple(running))
    return out


# --------------------------------------------------------------------------
# Scoring
# --------------------------------------------------------------------------

LEVEL = 0.90
REPLICATIONS = 2000


def _decomposition(probabilities: Sequence[float], outcomes: Sequence[int]) -> dict:
    count = len(outcomes)
    entry: dict = {
        "days": count,
        "events": sum(outcomes),
        "brier": sum((p - y) ** 2 for p, y in zip(probabilities, outcomes)) / count if count else None,
    }
    try:
        decomposition = corp_decomposition(probabilities, outcomes)
    except MetricError as exc:
        entry["unavailable"] = str(exc)
    else:
        entry["reliability"] = decomposition.reliability
        entry["resolution"] = decomposition.resolution
        entry["uncertainty"] = decomposition.uncertainty
    return entry


def _paired(
    reference: Sequence[float],
    candidate: Sequence[float],
    outcomes: Sequence[int],
    *,
    block_length: int,
    seed: int,
    splits: Optional[Any] = None,
    rows: Optional[Sequence[Any]] = None,
    scored_dates: Optional[Sequence[date]] = None,
) -> dict:
    """Brier(reference) - Brier(candidate) per day: mean, interval, splits."""

    from .baseline import split_document

    differences = [
        (r - y) ** 2 - (c - y) ** 2 for r, c, y in zip(reference, candidate, outcomes)
    ]

    def mean_of(indices: Sequence[int]) -> float:
        return sum(differences[i] for i in indices) / len(indices)

    lower, upper = stationary_bootstrap_interval(
        mean_of,
        len(differences),
        block_length=block_length,
        seed=seed,
        replications=REPLICATIONS,
        level=LEVEL,
    )
    entry: dict = {
        "mean": sum(differences) / len(differences),
        "interval": {
            "lower": lower,
            "upper": upper,
            "level": LEVEL,
            "method": "stationary_bootstrap",
            "block_length": block_length,
            "replications": REPLICATIONS,
            "seed": seed,
        },
    }
    if splits is not None:
        entry["splits"] = split_document(
            splits, rows, scored_dates, differences, block_length=block_length, seed=seed
        )
    return entry


def _width_summary(
    pairs: Sequence[Optional[Tuple[float, float]]], scored_dates: Sequence[date]
) -> dict:
    """Venn-Abers interval width: by calendar year, and over the scored days."""

    by_year: Dict[str, List[float]] = {}
    for pair, when in zip(pairs, scored_dates):
        if pair is None:
            continue
        by_year.setdefault(str(when.year), []).append(pair[1] - pair[0])
    widths = [w for values in by_year.values() for w in values]
    return {
        "days_with_interval": len(widths),
        "first_day": next(
            (when.isoformat() for pair, when in zip(pairs, scored_dates) if pair is not None),
            None,
        ),
        "mean_width": sum(widths) / len(widths) if widths else None,
        "max_width": max(widths) if widths else None,
        "by_year": {
            year: {
                "days": len(values),
                "mean_width": sum(values) / len(values),
                "max_width": max(values),
                "share_wider_than_0.10": sum(1 for w in values if w > 0.10) / len(values),
            }
            for year, values in sorted(by_year.items())
        },
    }


def score_target(
    raw: Sequence[float],
    calibrated: Mapping[str, Sequence[float]],
    outcomes: Sequence[int],
    scored_dates: Sequence[date],
    *,
    episodes: Mapping[str, Tuple[date, date]],
    venn: Sequence[Optional[Tuple[float, float]]],
    block_length: int,
    seed: Callable[..., int],
    splits: Any,
    rows: Sequence[Any],
    benchmarks: Mapping[str, Sequence[float]] = (),
) -> dict:
    """One target's evidence: metrics, per-episode reliability, and the pairings.

    Each candidate is paired against the control, split by regime and
    pressure-day type; against Platt (the published recalibration), and
    against each benchmark, overall.
    """

    from .metrics import corp_reliability_curve

    columns = {"raw": list(raw), **{name: list(col) for name, col in calibrated.items()}}
    entry: dict = {"days": len(outcomes), "events": sum(outcomes), "methods": {}}
    for name, column in columns.items():
        metrics = _decomposition(column, outcomes)
        try:
            curve = corp_reliability_curve(column, outcomes)
        except MetricError as exc:
            metrics["reliability_steps_unavailable"] = str(exc)
        else:
            steps: List[dict] = []
            for x, fitted in zip(curve.forecast, curve.recalibrated):
                if steps and steps[-1]["observed"] == fitted:
                    steps[-1]["forecast_high"] = x
                    steps[-1]["days"] += 1
                else:
                    steps.append(
                        {"forecast_low": x, "forecast_high": x, "observed": fitted, "days": 1}
                    )
            metrics["reliability_steps"] = steps
        metrics["episodes"] = {}
        for episode, (first, last) in episodes.items():
            positions = [k for k, when in enumerate(scored_dates) if first <= when <= last]
            metrics["episodes"][episode] = _decomposition(
                [column[k] for k in positions], [outcomes[k] for k in positions]
            )
        metrics["paired"] = {}
        if name != CONTROL:
            metrics["paired"]["vs_control"] = _paired(
                columns[CONTROL], column, outcomes, block_length=block_length,
                seed=seed(name, CONTROL), splits=splits, rows=rows, scored_dates=scored_dates,
            )
        if name not in (PUBLISHED, CONTROL) and PUBLISHED in columns:
            metrics["paired"]["vs_platt"] = _paired(
                columns["platt"], column, outcomes, block_length=block_length,
                seed=seed(name, "platt"),
            )
        for bench, values in dict(benchmarks).items():
            metrics["paired"][f"vs_{bench}"] = _paired(
                values, column, outcomes, block_length=block_length, seed=seed(name, bench),
            )
        entry["methods"][name] = metrics
    entry["venn_abers"] = _width_summary(venn, scored_dates)
    return entry
