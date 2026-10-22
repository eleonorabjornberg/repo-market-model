"""Walk-forward recalibration of the predictive quantiles (#1133; H5 step 3, development tier).

`metadata/walk_calibration_1133.json` is the declaration; this module is its arithmetic. The base is a model's walk of
23-quantile laws, one per decision day and lead (#941's scaled mean reversion). Three arms correct it, each re-estimated at
a refit from past cells only:

- **(a) pooled.** For lead `h` and grid level `p`, the score of a past cell is `(y - q_p) / w`, where `w` is the cell's own
  90% width `max(q_95 - q_05, WIDTH_FLOOR)`. The correction is the split-conformal quantile of the scores at level `p`
  (`conformal_quantile`), and the corrected quantile is `q_p + w * correction_p`. It can move a level either way.
- **(b) by state.** The same, on the past cells whose anchor row had the same value of the as-of floor flag as the
  decision day's anchor (`floor_flag`); the pooled correction while the state holds fewer than `MIN_STATE_CELLS` cells at
  that lead.
- **(c) (b) with the upper tail widened separately.** Levels at or above `TAIL_FROM` take a multiplicative correction
  about the median instead: `q_50 + lambda_p * (q_p - q_50)`, where `lambda_p` is the conformal quantile at level `p` of
  `(y - q_50) / max(q_p - q_50, TAIL_DENOMINATOR_FLOOR)` over the same cells. `lambda_p` is not capped at 1, so the tail
  can widen as well as narrow (avenue #809).

A corrected law is sorted, so no quantile crosses. A cell enters a calibration only when its target row is at or before the
anchor of the refit's decision day, the last row public at the decision instant; `calibration_cells` filters on it and
`protocol_benchmarks._require_public` restates it, raising `LookAheadError`. The flag at a row reads that row and the 59
before it, and the ON RRP offering rate in force on each, which is an announced rate read from its effective date
(`rrp_rates`). Stdlib only.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from . import protocol_benchmarks as pb
from .data import DailyObservation
from .scoring_protocol import GRID, HORIZONS
from .splits import LookAheadError

#: Decision days of past cells a calibration reads (two years of business days, the base model's training window).
WINDOW_DAYS = 504
#: A calibration of a lead with fewer past cells than this is not made, and the decision day is not forecast.
MIN_CELLS = 250
#: A state with fewer past cells at a lead than this takes the pooled correction.
MIN_STATE_CELLS = 100
#: Decision days between refits of the calibration: the project's cadence.
REFIT_EVERY = 21
#: The floor of the width that normalises a score, in bp.
WIDTH_FLOOR = 1.0
#: Levels at or above this take the multiplicative correction in arm (c).
TAIL_FROM = 0.90
#: The floor of the distance from the median that normalises a tail score, in bp.
TAIL_DENOMINATOR_FLOOR = 0.25
#: Grid positions of the interval ends and the median.
LOW, HIGH, MEDIAN = GRID.index(0.05), GRID.index(0.95), GRID.index(0.5)
TAIL_INDICES: Tuple[int, ...] = tuple(i for i, level in enumerate(GRID) if level >= TAIL_FROM)
ARMS: Tuple[str, ...] = ("pooled", "state", "state_tail")

#: The as-of floor flag (Lens B of #958, as #966 specifies it): the trailing median of SOFR less the ON RRP offering rate.
FLAG_WINDOW = 60
FLAG_MIN_ROWS = 40
FLAG_MAX_BP = 1.0


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
    """A past forecast with its outcome: the base law, the outcome, and the flag state of its anchor row."""

    quantiles: Sequence[float]
    outcome: float
    state: Optional[bool]


@dataclass(frozen=True)
class Correction:
    """Per-level corrections of one lead: additive in units of the cell's width, and tail multipliers by grid index."""

    offsets: Tuple[float, ...]
    multipliers: Mapping[int, float]
    cells: int


def fit_correction(cells: Sequence[Cell]) -> Correction:
    """The arm (a) offsets and the arm (c) tail multipliers of `cells`."""

    offsets = []
    for i, level in enumerate(GRID):
        offsets.append(conformal_quantile([(c.outcome - c.quantiles[i]) / width(c.quantiles) for c in cells], level))
    multipliers = {}
    for i in TAIL_INDICES:
        ratios = [
            (c.outcome - c.quantiles[MEDIAN]) / max(c.quantiles[i] - c.quantiles[MEDIAN], TAIL_DENOMINATOR_FLOOR)
            for c in cells
        ]
        multipliers[i] = max(0.0, conformal_quantile(ratios, GRID[i]))
    return Correction(tuple(offsets), multipliers, len(cells))


def apply(quantiles: Sequence[float], correction: Correction, *, tail: bool) -> List[float]:
    """The corrected law: the additive shift at every level, or (with `tail`) the multiplicative one from `TAIL_FROM` up.

    The result is sorted, so it never crosses.
    """

    w = width(quantiles)
    out = [q + w * o for q, o in zip(quantiles, correction.offsets)]
    if tail:
        centre = quantiles[MEDIAN]
        for i, factor in correction.multipliers.items():
            out[i] = centre + factor * (quantiles[i] - centre)
    return sorted(out)


# -- the as-of floor flag ------------------------------------------------------------------------------------------


def rrp_rates(entries: Sequence[Mapping[str, object]], days: Sequence[date]) -> List[Optional[float]]:
    """The ON RRP offering rate in percent in force on each of `days`, or `None` before the first entry.

    An entry applies from its effective date, and only once announced: the latest entry with both dates at or before the
    day. The rate series is not ingested here; it is read from `metadata/policy_events.json` (announcement-dated, #376).
    """

    rates = sorted(
        (
            (date.fromisoformat(str(e["effective_date"])), date.fromisoformat(str(e["announced_date"])),
             float(e["details"]["offering_rate_percent"]))
            for e in entries if e.get("kind") == "on_rrp" and "offering_rate_percent" in e.get("details", {})
        )
    )
    out: List[Optional[float]] = []
    for day in days:
        rate = None
        for effective, announced, value in rates:
            if effective <= day and announced <= day:
                rate = value
        out.append(rate)
    return out


def floor_flag(panel: Sequence[DailyObservation], entries: Sequence[Mapping[str, object]]) -> List[Optional[bool]]:
    """The flag at each row: the trailing `FLAG_WINDOW`-row median of SOFR less the ON RRP rate is at most `FLAG_MAX_BP`.

    `None` where fewer than `FLAG_MIN_ROWS` rows (with a rate in force) end at the row. Row `r` reads rows `r - 59 .. r`
    only. Pending #966, which specifies this flag and is not on main; see the pull request that closes #1133.
    """

    rates = rrp_rates(entries, [row.date for row in panel])
    gaps: List[Optional[float]] = [
        None if rate is None else 100.0 * (float(row.values["sofr"]) - rate) for row, rate in zip(panel, rates)
    ]
    out: List[Optional[bool]] = []
    for r in range(len(panel)):
        window = [g for g in gaps[max(0, r - FLAG_WINDOW + 1): r + 1] if g is not None]
        out.append(None if len(window) < FLAG_MIN_ROWS else statistics.median(window) <= FLAG_MAX_BP)
    return out


def check_flag_as_of(
    panel: Sequence[DailyObservation], entries: Sequence[Mapping[str, object]], flags: Sequence[Optional[bool]], row: int
) -> None:
    """Rebuild the flag from the panel cut at `row` and require it to equal `flags[row]`.

    Mutation record: see `tests/test_walk_calibration.py` (`FlagTests.test_a_flag_that_reads_a_later_row_is_refused`).

    Raises:
        LookAheadError: the cut panel gives a different flag, so `flags[row]` read a row after `row`.
    """

    rebuilt = floor_flag(panel[: row + 1], entries)[row]
    if rebuilt != flags[row]:
        raise LookAheadError(
            f"the floor flag on {panel[row].date} is {flags[row]} from the whole panel and {rebuilt} from the panel cut "
            f"there: it reads a later row"
        )


# -- the walk ------------------------------------------------------------------------------------------------------


def calibration_cells(
    days: Sequence[date],
    forecasts: Mapping[date, Mapping[int, Sequence[float]]],
    anchors: Mapping[date, int],
    position: Mapping[date, int],
    spreads: Sequence[float],
    flags: Sequence[Optional[bool]],
    dates: Sequence[date],
    *,
    before: date,
    anchor: int,
    lead: int,
) -> List[Cell]:
    """The cells of `lead` a refit on decision day `before` with last public row `anchor` may read.

    A cell is a decision day in the trailing `WINDOW_DAYS` days before `before` whose target row (its row plus `lead`) is
    at or before `anchor`. Its state is the flag at the cell's own anchor.

    Mutation record: see `tests/test_walk_calibration.py` (`CellTests.test_a_target_after_the_anchor_is_never_read`).

    Raises:
        LookAheadError: a selected target row is after `anchor` (`protocol_benchmarks._require_public`).
    """

    earlier = [d for d in days if d < before][-WINDOW_DAYS:]
    chosen = [d for d in earlier if position[d] + lead <= anchor]
    pb._require_public([position[d] + lead for d in chosen], anchor, dates, f"the calibration of lead {lead} on {before}")
    return [Cell(forecasts[d][lead], spreads[position[d] + lead], flags[anchors[d]]) for d in chosen]


@dataclass(frozen=True)
class Refit:
    """What a refit kept: per lead the pooled correction and one per state with enough cells."""

    day: date
    pooled: Mapping[int, Correction]
    by_state: Mapping[int, Mapping[bool, Correction]]
    state_cells: Mapping[int, Mapping[str, int]]


def refit(
    day: date,
    anchor: int,
    days: Sequence[date],
    forecasts: Mapping[date, Mapping[int, Sequence[float]]],
    anchors: Mapping[date, int],
    position: Mapping[date, int],
    spreads: Sequence[float],
    flags: Sequence[Optional[bool]],
    dates: Sequence[date],
) -> Optional[Refit]:
    """The corrections as of decision day `day`, or `None` while a lead has fewer than `MIN_CELLS` past cells."""

    pooled: Dict[int, Correction] = {}
    by_state: Dict[int, Dict[bool, Correction]] = {}
    counts: Dict[int, Dict[str, int]] = {}
    for h in HORIZONS:
        cells = calibration_cells(days, forecasts, anchors, position, spreads, flags, dates, before=day, anchor=anchor, lead=h)
        if len(cells) < MIN_CELLS:
            return None
        pooled[h] = fit_correction(cells)
        by_state[h] = {}
        counts[h] = {"pooled": len(cells)}
        for state in (True, False):
            members = [c for c in cells if c.state is state]
            counts[h][str(state).lower()] = len(members)
            if len(members) >= MIN_STATE_CELLS:
                by_state[h][state] = fit_correction(members)
    return Refit(day, pooled, by_state, counts)


def correct(
    base: Mapping[int, Sequence[float]], fit_: Refit, state: Optional[bool], arm: str
) -> Dict[int, List[float]]:
    """The decision day's corrected laws under `arm`, from `fit_` and the state of the day's anchor."""

    if arm not in ARMS:
        raise ValueError(f"arm must be one of {ARMS}, got {arm!r}")
    out = {}
    for h in HORIZONS:
        correction = fit_.pooled[h]
        if arm != "pooled" and state is not None:
            correction = fit_.by_state[h].get(state, correction)
        out[h] = apply(base[h], correction, tail=arm == "state_tail")
    return out


def walk(
    days: Sequence[date],
    forecasts: Mapping[date, Mapping[int, Sequence[float]]],
    anchors: Mapping[date, int],
    position: Mapping[date, int],
    spreads: Sequence[float],
    flags: Sequence[Optional[bool]],
    dates: Sequence[date],
    *,
    refit_every: int = REFIT_EVERY,
) -> Tuple[Dict[str, Dict[date, Dict[int, List[float]]]], Dict[date, Refit], List[date]]:
    """The three arms on every decision day of `days` that has a calibration.

    Returns `(laws, refits, uncalibrated)`: `laws[arm][day][lead]`, the refits by day, and the days before enough past cells
    existed. The calibration is refitted on the first calibrated day and every `refit_every` decision days after, and read
    unchanged in between; the state is read afresh from the flag at each day's own anchor.
    """

    if refit_every < 1:
        raise ValueError(f"refit_every must be at least 1, got {refit_every}")
    laws: Dict[str, Dict[date, Dict[int, List[float]]]] = {arm: {} for arm in ARMS}
    refits: Dict[date, Refit] = {}
    uncalibrated: List[date] = []
    current: Optional[Refit] = None
    since = 0
    for day in days:
        if current is None or since >= refit_every:
            made = refit(day, anchors[day], days, forecasts, anchors, position, spreads, flags, dates)
            if made is not None:
                current, since = made, 0
                refits[day] = made
        if current is None:
            uncalibrated.append(day)
            continue
        since += 1
        state = flags[anchors[day]]
        for arm in ARMS:
            laws[arm][day] = correct(forecasts[day], current, state, arm)
    return laws, refits, uncalibrated
