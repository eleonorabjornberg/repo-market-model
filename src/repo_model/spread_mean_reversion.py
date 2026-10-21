"""Persistence with partial mean reversion toward a local level (#686; H5, development tier).

`metadata/spread_distribution_686.json` is the declaration; this module is its arithmetic. The quantiles of the
SOFR - IORB spread in bp, h business days after a decision day, at the 23 levels of `scoring_protocol.GRID`:

    level + phi^k * (last - level) + eps_h

- `last` is the spread of the anchor row, the latest row public at the decision instant
  (`protocol_benchmarks._anchor`, which runs both guards of `InformationRule` at every lead).
- `level` is the median of the spreads of the last 10 ordinary days at or before the anchor.
- `k` is the number of panel rows from the anchor to the target, `h` plus the rows between the anchor and the
  decision day (one, when the anchor is the row before the decision day).
- `phi` is the value on a grid of 0.00 to 1.00 that minimises the squared error of the reverted deviation over the
  training pairs of all five leads; `eps_h` are the empirical quantiles of lead h's residuals.
- The training pairs are the pairs of an origin row and a target row `k` rows on, whose target falls in the two
  years before the decision day and was public at the decision instant. A row after the anchor is never read:
  `protocol_benchmarks._require_public` raises `LookAheadError` if one is.

`phi` and `eps_h` are refitted every 21 decision days; in between the last fit is kept and `last`, `level`, `k` and the
anchor are read afresh. Stdlib only.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, time
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from . import protocol_benchmarks as pb
from .data import DailyObservation
from .evaluation_splits import SplitDeclaration
from .scoring_protocol import GRID, HORIZONS, ProtocolError
from .splits import LookAheadError, SplitError

#: The level is the median of this many ordinary days.
LEVEL_DAYS = 10
#: The training window, in years before the decision day: B1's.
TRAIN_YEARS = pb.B1_YEARS
#: Phi is searched on this grid.
PHI_GRID: Tuple[float, ...] = tuple(step / 100.0 for step in range(101))
#: A decision with fewer training pairs at any lead has no forecast.
MIN_PAIRS = 60
#: Decision days between refits: the project's refit cadence (`metadata/dist_roll_606.json`).
REFIT_EVERY = 21
#: The tail event of the pressure probability, in bp.
TAIL_TAU = 5.0


class InsufficientHistory(ProtocolError):
    """Too few ordinary days or training pairs to forecast the decision day."""


@dataclass(frozen=True)
class Fit:
    """What a refit keeps: phi, the residual quantiles per lead, the pairs behind them."""

    phi: float
    residuals: Mapping[int, Sequence[float]]
    pairs: Mapping[int, int]
    fitted_on: Optional[date]


@dataclass(frozen=True)
class Walk:
    forecasts: Dict[date, Dict[int, List[float]]]
    #: Decision day -> the day of the fit it was forecast with.
    fit_used: Dict[date, date]
    fits: Dict[date, Fit]
    #: Decision days with no forecast, for want of history.
    skipped: Tuple[date, ...]


def ordinary_levels(panel: Sequence[DailyObservation], splits: SplitDeclaration) -> List[Optional[float]]:
    """The level at each row: the median of the last `LEVEL_DAYS` ordinary spreads at or before it, else `None`.

    A row's level reads only rows at or before it, so a level read at the anchor is as-of.
    """

    recent: List[float] = []
    out: List[Optional[float]] = []
    for row in panel:
        if splits.reporting_day_type(row.date, row.values) == "ordinary":
            recent.append(row.spread_bps)
            if len(recent) > LEVEL_DAYS:
                recent.pop(0)
        if len(recent) < LEVEL_DAYS:
            out.append(None)
        else:
            ordered = sorted(recent)
            mid = LEVEL_DAYS // 2
            out.append((ordered[mid - 1] + ordered[mid]) / 2.0 if LEVEL_DAYS % 2 == 0 else ordered[mid])
    return out


def fit_phi(pairs: Iterable[Tuple[int, float, float]]) -> float:
    """The phi on `PHI_GRID` that minimises the squared error of `y - phi^k * x` over `(k, x, y)` pairs.

    A tie takes the smaller phi.

    Raises:
        ValueError: no pairs.
    """

    rows = list(pairs)
    if not rows:
        raise ValueError("no training pairs to fit phi on")
    best, best_loss = PHI_GRID[0], math.inf
    for phi in PHI_GRID:
        loss = sum((y - phi**k * x) ** 2 for k, x, y in rows)
        if loss < best_loss:
            best, best_loss = phi, loss
    return best


def training_rows(
    panel: Sequence[DailyObservation],
    decision_index: int,
    anchor: int,
    *,
    lag: int,
    levels: Sequence[Optional[float]],
) -> Dict[int, List[Tuple[int, int]]]:
    """Per lead h, the (origin, target) rows of the training pairs, `k = h + lag` rows apart.

    The target is in the trailing window and at or before the anchor; the origin has a level. Every row read is
    required public (`protocol_benchmarks._require_public`).

    Raises:
        LookAheadError: a row after the anchor is among the pairs.
    """

    dates = [row.date for row in panel]
    first = pb._window_start(panel, decision_index, TRAIN_YEARS)
    out: Dict[int, List[Tuple[int, int]]] = {}
    for h in HORIZONS:
        k = h + lag
        pairs = []
        for target in range(max(first, k), anchor + 1):
            origin = target - k
            if levels[origin] is not None:
                pairs.append((origin, target))
        rows = {row for pair in pairs for row in pair}
        pb._require_public(rows, anchor, dates, f"the mean-reversion fit for {dates[decision_index]}, lead {h}")
        out[h] = pairs
    return out


def fit(
    panel: Sequence[DailyObservation],
    decision_index: int,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    levels: Optional[Sequence[Optional[float]]] = None,
) -> Fit:
    """phi and the residual quantiles per lead, as of the decision on row `decision_index`.

    Raises:
        InsufficientHistory: fewer than `MIN_PAIRS` training pairs at some lead.
        LookAheadError, StaleReadError: the information-set guards of the decision.
    """

    levels = ordinary_levels(panel, splits) if levels is None else levels
    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    lag = decision_index - anchor
    rows = training_rows(panel, decision_index, anchor, lag=lag, levels=levels)
    short = [h for h in HORIZONS if len(rows[h]) < MIN_PAIRS]
    if short:
        raise InsufficientHistory(
            f"{panel[decision_index].date}: lead {short[0]} has {len(rows[short[0]])} training pairs, "
            f"fewer than the {MIN_PAIRS} the declaration requires"
        )
    spreads = [row.spread_bps for row in panel[: anchor + 1]]
    pairs = []
    deviations: Dict[int, List[Tuple[float, float]]] = {}
    for h in HORIZONS:
        k = h + lag
        deviations[h] = [(spreads[o] - levels[o], spreads[s] - levels[o]) for o, s in rows[h]]
        pairs.extend((k, x, y) for x, y in deviations[h])
    phi = fit_phi(pairs)
    residuals = {}
    for h in HORIZONS:
        k = h + lag
        residuals[h] = pb.empirical_quantiles(sorted(y - phi**k * x for x, y in deviations[h]))
    return Fit(phi, residuals, {h: len(rows[h]) for h in HORIZONS}, panel[decision_index].date)


def quantiles_from(fit_: Fit, *, last: float, level: float, lag: int) -> Dict[int, List[float]]:
    """The 23 quantiles per lead from a fit, the last public spread, its level and the row lag."""

    out = {}
    for h in HORIZONS:
        centre = level + fit_.phi ** (h + lag) * (last - level)
        out[h] = [centre + value for value in fit_.residuals[h]]
    return out


def forecast(
    panel: Sequence[DailyObservation],
    decision_index: int,
    fit_: Fit,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    levels: Optional[Sequence[Optional[float]]] = None,
) -> Dict[int, List[float]]:
    """The decision day's forecast from `fit_` (possibly an older fit): `last`, `level` and `k` read afresh.

    Raises:
        InsufficientHistory: the anchor has no level (fewer than `LEVEL_DAYS` ordinary days before it).
    """

    levels = ordinary_levels(panel, splits) if levels is None else levels
    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    level = levels[anchor]
    if level is None:
        raise InsufficientHistory(f"{panel[decision_index].date}: fewer than {LEVEL_DAYS} ordinary days before the anchor")
    return quantiles_from(fit_, last=panel[anchor].spread_bps, level=level, lag=decision_index - anchor)


def walk(
    panel: Sequence[DailyObservation],
    decision_days: Iterable[date],
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    refit_every: int = REFIT_EVERY,
) -> Walk:
    """The forecasts of `decision_days`, refitting on the first forecast day and every `refit_every`-th after it."""

    if refit_every < 1:
        raise ValueError(f"refit_every must be at least 1, got {refit_every}")
    position = {row.date: index for index, row in enumerate(panel)}
    levels = ordinary_levels(panel, splits)
    settings = dict(registry=registry, decision_time=decision_time, splits=splits, levels=levels)
    forecasts: Dict[date, Dict[int, List[float]]] = {}
    fit_used: Dict[date, date] = {}
    fits: Dict[date, Fit] = {}
    skipped: List[date] = []
    current: Optional[Fit] = None
    since = 0
    for day in decision_days:
        if day not in position:
            raise ProtocolError(f"decision day {day} is not a panel day")
        index = position[day]
        try:
            if current is None or since >= refit_every:
                current = fit(panel, index, **settings)
                fits[day] = current
                since = 0
            forecasts[day] = forecast(panel, index, current, **settings)
        except InsufficientHistory:
            skipped.append(day)
            continue
        except LookAheadError:
            raise  # a guard trip is never "no public row yet"
        except SplitError:
            # The first rows of the panel have no public row at their decision instant; later ones must.
            if current is not None:
                raise
            skipped.append(day)
            continue
        fit_used[day] = current.fitted_on
        since += 1
    return Walk(forecasts, fit_used, fits, tuple(skipped))


def exceedance(quantiles: Sequence[float], tau: float = TAIL_TAU) -> float:
    """P(spread > tau) from one lead's 23 quantiles, as `ml.exceedance_from_quantiles` reads it.

    The curve at `tau` is `1 - F(floor(tau) + 0.5)`, the whole-basis-point event of `data.exceeds_bp`: F is linear
    between the quantiles and runs on at the outer segments' slopes to 0 and 1. Ties are nudged by one part in a
    million of a bp per level so the knots increase.
    """

    if len(quantiles) != len(GRID):
        raise ProtocolError(f"{len(quantiles)} quantiles; the grid has {len(GRID)}")
    knots = [float(value) + 1e-6 * index for index, value in enumerate(quantiles)]
    low = (knots[1] - knots[0]) / (GRID[1] - GRID[0])
    high = (knots[-1] - knots[-2]) / (GRID[-1] - GRID[-2])
    edges = [knots[0] - GRID[0] * low] + knots + [knots[-1] + (1.0 - GRID[-1]) * high]
    levels = [0.0] + list(GRID) + [1.0]
    cut = math.floor(float(tau)) + 0.5
    if cut <= edges[0]:
        below = 0.0
    elif cut >= edges[-1]:
        below = 1.0
    else:
        upper = next(i for i, edge in enumerate(edges) if edge >= cut)
        lower = upper - 1
        below = levels[lower] + (cut - edges[lower]) / (edges[upper] - edges[lower]) * (levels[upper] - levels[lower])
    return min(1.0, max(0.0, 1.0 - below))
