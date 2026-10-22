"""Walk-forward recalibration of the predictive quantiles (#1133; H5 step 3, development tier).

`metadata/walk_calibration_1133.json` is the declaration; this module is its arithmetic. The base is a model's walk of
23-quantile laws, one per decision day and lead (#941's scaled mean reversion). One arm corrects it, re-estimated at a
refit from past cells only (arms (b) and (c), by the floor flag and with the upper tail widened, were dropped by Eleonora's
ruling of 22 October 2026 on #1142):

- **(a) pooled.** For lead `h` and grid level `p`, the score of a past cell is `(y - q_p) / w`, where `w` is the cell's own
  90% width `max(q_95 - q_05, WIDTH_FLOOR)`. The correction is the split-conformal quantile of the scores at level `p`
  (`conformal_quantile`), and the corrected quantile is `q_p + w * correction_p`. It can move a level either way.

A corrected law is sorted, so no quantile crosses. A cell enters a calibration only when its target row is at or before the
anchor of the refit's decision day, the last row public at the decision instant; `calibration_cells` filters on it and
`protocol_benchmarks._require_public` restates it, raising `LookAheadError`. Stdlib only.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from . import protocol_benchmarks as pb
from .scoring_protocol import GRID, HORIZONS

#: Decision days of past cells a calibration reads (two years of business days, the base model's training window).
WINDOW_DAYS = 504
#: A calibration of a lead with fewer past cells than this is not made, and the decision day is not forecast.
MIN_CELLS = 250
#: Decision days between refits of the calibration: the project's cadence.
REFIT_EVERY = 21
#: The floor of the width that normalises a score, in bp.
WIDTH_FLOOR = 1.0
#: Grid positions of the interval ends and the median.
LOW, HIGH, MEDIAN = GRID.index(0.05), GRID.index(0.95), GRID.index(0.5)
ARMS: Tuple[str, ...] = ("pooled",)


def width(quantiles: Sequence[float]) -> float:
    """The normaliser of a cell: its 90% width, floored."""

    return max(quantiles[HIGH] - quantiles[LOW], WIDTH_FLOOR)


def conformal_quantile(scores: Sequence[float], level: float) -> float:
    """The split-conformal quantile of `scores` at `level`: the `ceil(level * (n + 1))`-th smallest, clamped to `1..n`."""

    if not scores:
        raise ValueError("a conformal quantile needs at least one score")
    ordered = sorted(scores)
    k = min(len(ordered), max(1, math.ceil(level * (len(ordered) + 1))))
    return ordered[k - 1]


@dataclass(frozen=True)
class Cell:
    """A past forecast with its outcome: the base law and the outcome."""

    quantiles: Sequence[float]
    outcome: float


@dataclass(frozen=True)
class Correction:
    """Per-level corrections of one lead, additive in units of the cell's width."""

    offsets: Tuple[float, ...]
    cells: int


def fit_correction(cells: Sequence[Cell]) -> Correction:
    """The arm (a) offsets of `cells`."""

    offsets = [
        conformal_quantile([(c.outcome - c.quantiles[i]) / width(c.quantiles) for c in cells], level)
        for i, level in enumerate(GRID)
    ]
    return Correction(tuple(offsets), len(cells))


def apply(quantiles: Sequence[float], correction: Correction) -> List[float]:
    """The corrected law: the additive shift at every level. The result is sorted, so it never crosses."""

    w = width(quantiles)
    return sorted(q + w * o for q, o in zip(quantiles, correction.offsets))


# -- the walk ------------------------------------------------------------------------------------------------------


def calibration_cells(
    days: Sequence[date],
    forecasts: Mapping[date, Mapping[int, Sequence[float]]],
    position: Mapping[date, int],
    spreads: Sequence[float],
    dates: Sequence[date],
    *,
    before: date,
    anchor: int,
    lead: int,
) -> List[Cell]:
    """The cells of `lead` a refit on decision day `before` with last public row `anchor` may read.

    A cell is a decision day in the trailing `WINDOW_DAYS` days before `before` whose target row (its row plus `lead`) is
    at or before `anchor`.

    Mutation record: see `tests/test_walk_calibration.py` (`CellTests.test_a_target_after_the_anchor_is_never_read`).

    Raises:
        LookAheadError: a selected target row is after `anchor` (`protocol_benchmarks._require_public`).
    """

    earlier = [d for d in days if d < before][-WINDOW_DAYS:]
    chosen = [d for d in earlier if position[d] + lead <= anchor]
    pb._require_public([position[d] + lead for d in chosen], anchor, dates, f"the calibration of lead {lead} on {before}")
    return [Cell(forecasts[d][lead], spreads[position[d] + lead]) for d in chosen]


@dataclass(frozen=True)
class Refit:
    """What a refit kept: per lead the correction."""

    day: date
    pooled: Mapping[int, Correction]


def refit(
    day: date,
    anchor: int,
    days: Sequence[date],
    forecasts: Mapping[date, Mapping[int, Sequence[float]]],
    position: Mapping[date, int],
    spreads: Sequence[float],
    dates: Sequence[date],
) -> Optional[Refit]:
    """The corrections as of decision day `day`, or `None` while a lead has fewer than `MIN_CELLS` past cells."""

    pooled: Dict[int, Correction] = {}
    for h in HORIZONS:
        cells = calibration_cells(days, forecasts, position, spreads, dates, before=day, anchor=anchor, lead=h)
        if len(cells) < MIN_CELLS:
            return None
        pooled[h] = fit_correction(cells)
    return Refit(day, pooled)


def correct(base: Mapping[int, Sequence[float]], fit_: Refit) -> Dict[int, List[float]]:
    """The decision day's corrected laws, from `fit_`."""

    return {h: apply(base[h], fit_.pooled[h]) for h in HORIZONS}


def walk(
    days: Sequence[date],
    forecasts: Mapping[date, Mapping[int, Sequence[float]]],
    anchors: Mapping[date, int],
    position: Mapping[date, int],
    spreads: Sequence[float],
    dates: Sequence[date],
    *,
    refit_every: int = REFIT_EVERY,
) -> Tuple[Dict[date, Dict[int, List[float]]], Dict[date, Refit], List[date]]:
    """The pooled arm on every decision day of `days` that has a calibration.

    Returns `(laws, refits, uncalibrated)`: `laws[day][lead]`, the refits by day, and the days before enough past cells
    existed. The calibration is refitted on the first calibrated day and every `refit_every` decision days after, and read
    unchanged in between.
    """

    if refit_every < 1:
        raise ValueError(f"refit_every must be at least 1, got {refit_every}")
    laws: Dict[date, Dict[int, List[float]]] = {}
    refits: Dict[date, Refit] = {}
    uncalibrated: List[date] = []
    current: Optional[Refit] = None
    since = 0
    for day in days:
        if current is None or since >= refit_every:
            made = refit(day, anchors[day], days, forecasts, position, spreads, dates)
            if made is not None:
                current, since = made, 0
                refits[day] = made
        if current is None:
            uncalibrated.append(day)
            continue
        since += 1
        laws[day] = correct(forecasts[day], current)
    return laws, refits, uncalibrated
