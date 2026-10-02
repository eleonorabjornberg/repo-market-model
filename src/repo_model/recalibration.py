"""Two challengers to the published band calibration, CV+ (#116).

Eleonora's ruling of 2 October 2026 asks for calibration to be re-diagnosed on
the as-of design before any calibration verdict is repeated: the published
funding declaration's gbm, calibrated by cross-conformal (CV+, the control),
against an online conformal method and a group-conditional one, on one fold
grid. Both challengers start from what one CV+ backtest already produces, so
the three are paired by construction: the full fit's uncalibrated quantile
vector, and CV+'s held-out terms (`ml.FittedGradientBoostedQuantiles.
cross_conformal_parts`). This module is the arithmetic each challenger adds,
and is standard library only; `scripts/calibration_rediagnosis.py` runs the
backtest and scores the three.

**Online: conformal PID** (Angelopoulos, Barber and Bates, "Conformal PID
Control for Time Series Prediction", NeurIPS 2023). The scored days are a
sequence. Each day's band is the uncalibrated vector with its outer two levels
moved out by `q_t` (in by a negative one, stopping at the neighbour, as
`ml._banded` does), where

    q_t = tracker + r(E, n) + scorecast

* the **tracker** is quantile tracking, the paper's "P" part: each observed
  label moves it by `eta * (err - alpha)`, `err` 1 when the label fell outside
  the band issued for it and `alpha` the band's declared miss rate (0.10). The
  step `eta` is `PID_STEP` times the range of the last `PID_STEP_WINDOW`
  observed scores, the paper's proportional learning rate, floored at
  `PID_SCALE_FLOOR`;
* `r(E, n)` is the paper's saturating integrator over the summed coverage
  error `E = sum(err - alpha)` of the `n` observed labels:
  `PID_INTEGRATOR_GAIN * B * tan(E log(n + 1) / (PID_SATURATION (n + 1)))`,
  with `B` the same score range. The tangent's argument is clipped to
  `+-PID_TANGENT_LIMIT`, where the paper lets it reach infinity: an infinite
  band has no CRPS. A clipped day is reported (`OnlineBand.saturated`);
* the **scorecast** is the paper's "D" part, a scorecaster forecasting the
  day's score: here a least-squares fit of the observed scores
  `max(Q_lo - y, y - Q_hi)` on an intercept and the scored day's calendar
  (`SCORECASTER_INDICATORS`: month end, quarter end, tax date, coupon
  settlement), refitted as labels arrive. It is zero until
  `SCORECASTER_MINIMUM` labels are observed, and an indicator enters the fit
  only once `SCORECASTER_INDICATOR_MINIMUM` observed days carry it and as many
  do not.

**Label observability.** The band for a scored day is issued at that day's
decision instant, and a label moves the state only once it is observable
there: a scored day's label is observable at a decision whose anchor (the
fold's `feature_date`, the latest row whose target was observable) is on or
after it. `PidState.observe` refuses any other label with `LookAheadError`,
and `conformal_pid` holds each label back until it qualifies. At
`--minimum-history 61` the first scored day's state is empty: the first bands
are the uncalibrated ones, and the burn-in is part of what is scored.

**Group-conditional: Mondrian CV+** (Vovk, Gammerman and Shafer, *Algorithmic
Learning in a Random World*, 2005, ch. 4, Mondrian conformal predictors;
applied to CV+, Barber, Candes, Ramdas and Tibshirani, 2021). CV+'s edges are
order statistics of `Q_lo_-k(i)(x) - s_i` and `Q_hi_-k(i)(x) + s_i` over the
held-out rows `i`. Here they are taken over the held-out rows in the scored
day's own group, calendar type x regime (`metadata/evaluation_splits.json`), at
the same ranks. A group with fewer than `ml._minimum_calibration_rows` terms,
the least at which both ranks exist, has no finite band; it falls back to the
scored day's calendar type across regimes, and then to every term, which is
CV+ itself. The level used is reported per day.

**In a fold loop: `FoldPid`** (#124). Eleonora's ruling on #123 makes
conformal PID, with the calendar scorecaster and exactly these constants, the
published funding declaration's calibration (`--calibration conformal_pid`).
The fold loops issue one band per scored day, in date order, and learn a day's
label only after it is scored; `FoldPid` is the method in that shape. It reads
the block's uncalibrated fit at each scored day (a gbm fitted with calibration
`none`, whose vector and residual range are the CV+ fit's own before its edges
move), issues the band through `OnlinePid`, the same steps `conformal_pid`
takes, and is told the label once the day is scored. Its declaration is
`settings`: the method's name and every constant below.

Every constant here was declared before any fold was scored with it, and none
was searched.

**The search grid (#125).** #122 scored conformal PID at the constants above,
chosen by its session and never searched. Eleonora's ruling of 2 October 2026
asks for them to be re-examined by nested walk-forward selection, from a grid
declared in code before any scoring and never widened after. `PidConstants`
names the four that are searched, each by its role in Angelopoulos, Barber and
Bates (2023):

* `step`, the **P** part: quantile tracking's learning rate, `eta / B`. Larger
  steps react faster to a run of misses and wander more on calm days.
  Grid: `PID_GRID_STEPS`, 0.01, 0.05 (#122) and 0.2.
* `integrator_gain` and `saturation`, the **I** part: the saturating
  integrator `K_I * B * tan(E log(n + 1) / (C_sat (n + 1)))` over the summed
  coverage error `E`. The gain `K_I` sets how far a long-run coverage error
  moves the band; `C_sat` how soon the tangent saturates (a larger `C_sat`
  acts later). Grid: `PID_GRID_INTEGRATOR_GAINS`, 0 (no integrator), 0.1
  (#122) and 0.5; `PID_GRID_SATURATIONS`, 1 (#122) and 5. With a zero gain the
  saturation is moot, so those points appear once, at the first saturation.
* `scorecaster_minimum`, the **D** part: the scorecaster forecasting the day's
  score from its calendar, here the number of observed labels before it is
  fitted at all. Grid: `PID_GRID_SCORECASTER_MINIMUMS`, `None` (no
  scorecaster), 20 (#122) and 60.

`PID_GRID` is their product, 45 points, #122's (`DECLARED_PID`) among them.
`nested_selection` chooses among them at each refit from the days scored
before it (`select_constants` is the guard). The rest of the method is held at #122's values and not searched:
`PID_STEP_WINDOW`, `PID_SCALE_FLOOR`, `PID_TANGENT_LIMIT`,
`SCORECASTER_INDICATOR_MINIMUM` and `SCORECASTER_INDICATORS`.
"""

from __future__ import annotations

import math
from collections import deque
from datetime import date, datetime
from itertools import product
from typing import Deque, List, NamedTuple, Optional, Sequence, Tuple

from .asof import InformationRule
from .contract import QUANTILE_LEVELS, field_sources_for_features
from .data import DailyObservation
from .splits import LookAheadError

#: The scorecaster's calendar, in column order after the intercept.
SCORECASTER_INDICATORS = ("month_end", "quarter_end", "tax_date", "coupon_settlement")

#: The panel column the coupon settlement indicator is read off: the scored
#: day's coupon settlement, in USD billions, a scheduled field.
SETTLEMENT_COLUMN = "treasury_settlement_coupons"

#: `eta / B`: the tracker's step as a share of the recent score range.
PID_STEP = 0.05

#: How many of the latest observed scores the range `B` is taken over.
PID_STEP_WINDOW = 100

#: The least `B`, in basis points: the spread is quoted to one basis point.
PID_SCALE_FLOOR = 1.0

#: The integrator's gain, as a multiple of `B`.
PID_INTEGRATOR_GAIN = 0.1

#: The integrator's saturation constant `C_sat`.
PID_SATURATION = 1.0

#: The largest tangent argument the integrator takes; `tan(1.5)` is about 14.
PID_TANGENT_LIMIT = 1.5

#: Observed labels before the scorecaster is fitted at all.
SCORECASTER_MINIMUM = 20

#: Observed days with, and without, an indicator before it enters the fit.
SCORECASTER_INDICATOR_MINIMUM = 5


class PidConstants(NamedTuple):
    """The constants of conformal PID that #125 searches.

    `step` is `eta / B` (P), `integrator_gain` and `saturation` are `K_I` and
    `C_sat` (I), and `scorecaster_minimum` the observed labels before the
    scorecaster is fitted, `None` for no scorecaster (D).
    """

    step: float
    integrator_gain: float
    saturation: float
    scorecaster_minimum: Optional[int]


#: #122's constants, the control: the point every other is compared with.
DECLARED_PID = PidConstants(
    PID_STEP, PID_INTEGRATOR_GAIN, PID_SATURATION, SCORECASTER_MINIMUM
)

#: The search grid's values per constant, declared before any scoring (#125).
PID_GRID_STEPS = (0.01, 0.05, 0.2)
PID_GRID_INTEGRATOR_GAINS = (0.0, 0.1, 0.5)
PID_GRID_SATURATIONS = (1.0, 5.0)
PID_GRID_SCORECASTER_MINIMUMS: Tuple[Optional[int], ...] = (None, 20, 60)

#: The search grid: the product of the values above, without the duplicates a
#: zero integrator gain makes of the saturation.
PID_GRID: Tuple[PidConstants, ...] = tuple(
    PidConstants(step, gain, saturation, minimum)
    for step, gain, saturation, minimum in product(
        PID_GRID_STEPS,
        PID_GRID_INTEGRATOR_GAINS,
        PID_GRID_SATURATIONS,
        PID_GRID_SCORECASTER_MINIMUMS,
    )
    if gain != 0.0 or saturation == PID_GRID_SATURATIONS[0]
)


class OnlineDay(NamedTuple):
    """One scored day as the online method sees it before its label.

    `vector` is the uncalibrated quantile vector issued for the day; `anchor`
    the latest panel day whose label was observable at its decision instant;
    `calendar` the scorecaster's indicators for `scored_date`
    (`scorecaster_calendar`).
    """

    scored_date: date
    anchor: date
    vector: Tuple[float, ...]
    calendar: Tuple[int, ...]


class OnlineBand(NamedTuple):
    """The band conformal PID issued for one day, and what it was made of."""

    vector: Tuple[float, ...]
    quantile: float
    scorecast: float
    observed: int
    saturated: bool


def _banded(vector: Sequence[float], lower: float, upper: float) -> Tuple[float, ...]:
    from . import ml

    return ml._banded(vector, lower, upper)


def _miss_rate(levels: Sequence[float]) -> float:
    from . import ml

    return float(1 - ml._band_probability(levels))


def _score(vector: Sequence[float], actual: float) -> float:
    return max(vector[0] - actual, actual - vector[-1])


def _solve(gram: List[List[float]], moment: List[float]) -> Optional[Tuple[float, ...]]:
    """Gaussian elimination with partial pivoting; `None` when singular."""

    size = len(moment)
    matrix = [list(row) + [value] for row, value in zip(gram, moment)]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(matrix[row][column]))
        if abs(matrix[pivot][column]) < 1e-9:
            return None
        matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
        for row in range(column + 1, size):
            factor = matrix[row][column] / matrix[column][column]
            for entry in range(column, size + 1):
                matrix[row][entry] -= factor * matrix[column][entry]
    solution = [0.0] * size
    for row in range(size - 1, -1, -1):
        total = matrix[row][size] - sum(
            matrix[row][entry] * solution[entry] for entry in range(row + 1, size)
        )
        solution[row] = total / matrix[row][row]
    return tuple(solution)


class PidState:
    """Conformal PID's state: what the labels observed so far have taught it."""

    def __init__(self, levels: Sequence[float], constants: PidConstants = DECLARED_PID) -> None:
        self.constants = constants
        self.alpha = _miss_rate(levels)
        self.tracker = 0.0
        self.error_sum = 0.0
        self.observed = 0
        self.last_observed: Optional[date] = None
        self.recent: Deque[float] = deque(maxlen=PID_STEP_WINDOW)
        width = 1 + len(SCORECASTER_INDICATORS)
        self.gram = [[0.0] * width for _ in range(width)]
        self.moment = [0.0] * width
        self.flagged = [0] * len(SCORECASTER_INDICATORS)
        self._coefficients: Optional[Tuple[Tuple[int, ...], Tuple[float, ...]]] = None

    def _scale(self) -> float:
        spread = max(self.recent) - min(self.recent) if len(self.recent) >= 2 else 0.0
        return max(spread, PID_SCALE_FLOOR)

    def _integrator(self) -> Tuple[float, bool]:
        if not self.observed:
            return 0.0, False
        n = self.observed
        argument = self.error_sum * math.log(n + 1) / (self.constants.saturation * (n + 1))
        saturated = abs(argument) > PID_TANGENT_LIMIT
        argument = max(-PID_TANGENT_LIMIT, min(PID_TANGENT_LIMIT, argument))
        return self.constants.integrator_gain * self._scale() * math.tan(argument), saturated

    def _fit(self) -> Tuple[Tuple[int, ...], Tuple[float, ...]]:
        if self._coefficients is None:
            active = [0] + [
                1 + position
                for position, count in enumerate(self.flagged)
                if SCORECASTER_INDICATOR_MINIMUM <= count <= self.observed - SCORECASTER_INDICATOR_MINIMUM
            ]
            while True:
                solution = _solve(
                    [[self.gram[i][j] for j in active] for i in active],
                    [self.moment[i] for i in active],
                )
                if solution is not None:
                    break
                active.pop()
            self._coefficients = (tuple(active), solution)
        return self._coefficients

    def scorecast(self, calendar: Sequence[int]) -> float:
        minimum = self.constants.scorecaster_minimum
        if minimum is None or self.observed < minimum:
            return 0.0
        active, coefficients = self._fit()
        row = (1,) + tuple(calendar)
        return sum(coefficient * row[column] for column, coefficient in zip(active, coefficients))

    def band(self, day: OnlineDay) -> OnlineBand:
        """The band issued for `day` from the labels observed so far."""

        if len(day.calendar) != len(SCORECASTER_INDICATORS):
            raise ValueError(
                f"{day.scored_date}: {len(day.calendar)} calendar indicators, "
                f"expected {len(SCORECASTER_INDICATORS)} ({SCORECASTER_INDICATORS})"
            )
        integrator, saturated = self._integrator()
        scorecast = self.scorecast(day.calendar)
        quantile = self.tracker + integrator + scorecast
        vector = _banded(day.vector, day.vector[0] - quantile, day.vector[-1] + quantile)
        return OnlineBand(vector, quantile, scorecast, self.observed, saturated)

    def observe(
        self, day: OnlineDay, band: OnlineBand, actual: float, decision: OnlineDay
    ) -> None:
        """Update on `day`'s label, as seen at `decision`'s decision instant.

        Raises:
            LookAheadError: if `day`'s label was not observable at that
                instant: `day` is scored after `decision`'s anchor.
            ValueError: if labels are observed out of date order or twice.
        """

        if day.scored_date > decision.anchor:
            raise LookAheadError(
                f"the label of {day.scored_date} is not observable at the decision "
                f"for {decision.scored_date}, whose latest observable label is "
                f"{decision.anchor}; an online calibration may update only on "
                f"labels public at the instant its band is issued"
            )
        if self.last_observed is not None and day.scored_date <= self.last_observed:
            raise ValueError(
                f"the label of {day.scored_date} is observed after that of "
                f"{self.last_observed}; labels are observed once, in date order"
            )
        score = _score(day.vector, actual)
        miss = 0.0 if band.vector[0] <= actual <= band.vector[-1] else 1.0
        self.tracker += self.constants.step * self._scale() * (miss - self.alpha)
        self.error_sum += miss - self.alpha
        self.observed += 1
        self.last_observed = day.scored_date
        self.recent.append(score)
        row = (1,) + tuple(day.calendar)
        for i, left in enumerate(row):
            self.moment[i] += left * score
            for j, right in enumerate(row):
                self.gram[i][j] += left * right
        for position, flag in enumerate(day.calendar):
            self.flagged[position] += 1 if flag else 0
        self._coefficients = None


class OnlinePid:
    """Conformal PID one day at a time: issue a day's band, later learn its label.

    The steps `conformal_pid` takes for each day, held between calls so a fold
    loop can take them as it scores: before a day's band is issued, every
    earlier day whose label is observable at its decision (scored on or before
    its anchor) is observed, in date order.
    """

    def __init__(self, levels: Sequence[float], constants: PidConstants = DECLARED_PID) -> None:
        self.state = PidState(levels, constants)
        self._pending: Deque[Tuple[OnlineDay, OnlineBand, float]] = deque()
        self._last: Optional[OnlineDay] = None

    def issue(self, day: OnlineDay) -> OnlineBand:
        """`day`'s band, from the labels observable at its decision.

        Raises:
            LookAheadError: if `day` is anchored on or after its own scored
                date, which would make its own label observable before its
                band is issued.
            ValueError: if `day` is not after the last day issued, or its
                anchor moves back.
        """

        if day.anchor >= day.scored_date:
            raise LookAheadError(
                f"{day.scored_date} is anchored at {day.anchor}: its own label "
                f"would be observable before its band is issued"
            )
        last = self._last
        if last is not None and (
            day.scored_date <= last.scored_date or day.anchor < last.anchor
        ):
            raise ValueError(
                f"days must be in scored-date order with anchors that do not move "
                f"back: {last.scored_date} (anchor {last.anchor}) is followed by "
                f"{day.scored_date} (anchor {day.anchor})"
            )
        while self._pending and self._pending[0][0].scored_date <= day.anchor:
            earlier, issued, label = self._pending.popleft()
            self.state.observe(earlier, issued, label, day)
        band = self.state.band(day)
        self._last = day
        return band

    def record(self, day: OnlineDay, band: OnlineBand, actual: float) -> None:
        """`day`'s label, held until a later decision can observe it."""

        self._pending.append((day, band, float(actual)))


def conformal_pid(
    days: Sequence[OnlineDay],
    actuals: Sequence[float],
    levels: Sequence[float],
    constants: PidConstants = DECLARED_PID,
) -> Tuple[OnlineBand, ...]:
    """Conformal PID's band for every day, each from the labels its decision saw.

    `days` and `actuals` are aligned, in scored-date order. Before each day's
    band is issued, every earlier day whose label is observable at its
    decision (scored on or before its anchor) is observed, in date order.
    `constants` defaults to #122's.
    decision (scored on or before its anchor) is observed, in date order
    (`OnlinePid`).

    Raises:
        ValueError: on misaligned inputs, days out of order, or anchors that
            move backwards.
        LookAheadError: if a day is anchored on or after its own scored date,
            which would make its own label observable before it is issued.
    """

    if len(days) != len(actuals):
        raise ValueError(f"{len(days)} days for {len(actuals)} labels; they are aligned")
    for earlier, later in zip(days, days[1:]):
        if later.scored_date <= earlier.scored_date or later.anchor < earlier.anchor:
            raise ValueError(
                f"days must be in scored-date order with anchors that do not move "
                f"back: {earlier.scored_date} (anchor {earlier.anchor}) is followed by "
                f"{later.scored_date} (anchor {later.anchor})"
            )
    for day in days:
        if day.anchor >= day.scored_date:
            raise LookAheadError(
                f"{day.scored_date} is anchored at {day.anchor}: its own label "
                f"would be observable before its band is issued"
            )
    online = OnlinePid(levels, constants)
    bands: List[OnlineBand] = []
    for day, actual in zip(days, actuals):
        band = online.issue(day)
        bands.append(band)
        online.record(day, band, actual)
    return tuple(bands)


def scorecaster_calendar(
    rows: Sequence[DailyObservation],
    rule: InformationRule,
    scored_index: int,
    splits,
    dates: Optional[Sequence[date]] = None,
) -> Tuple[int, ...]:
    """The scorecaster's indicators for `rows[scored_index]`, read at its decision.

    Month end is `days_to_month_end` within the split declaration's month-end
    window; quarter end and tax date are their calendar flags. Coupon
    settlement is `treasury_settlement_coupons > 0`, read only when its
    declared availability for the scored row is at or before the scored day's
    decision instant.

    Raises:
        LookAheadError: the settlement was not yet announced at the decision.
        ValueError: a calendar column or the settlement is missing; a hole is
            not read as zero.
    """

    if dates is None:
        dates = [row.date for row in rows]
    values = rows[scored_index].values
    read = {}
    for column in ("days_to_month_end", "quarter_end", "tax_date", SETTLEMENT_COLUMN):
        value = values.get(column)
        if value is None or not math.isfinite(float(value)):
            raise ValueError(
                f"{dates[scored_index]} carries no {column!r}; the scorecaster's "
                f"calendar is read, never assumed"
            )
        read[column] = float(value)
    decision: datetime = rule.decision_instant(dates, scored_index)
    available = rule.availability(
        dates, field_sources_for_features((SETTLEMENT_COLUMN,)), scored_index
    )
    if available > decision:
        raise LookAheadError(
            f"the coupon settlement for {dates[scored_index]} is declared "
            f"observable at {available}, after the {decision} decision"
        )
    return (
        1 if read["days_to_month_end"] <= splits.month_end_window else 0,
        1 if read["quarter_end"] == 1.0 else 0,
        1 if read["tax_date"] == 1.0 else 0,
        1 if read[SETTLEMENT_COLUMN] > 0.0 else 0,
    )


def group_conditional_edges(
    lows: Sequence[float],
    highs: Sequence[float],
    groups: Sequence[Tuple[str, str]],
    target: Tuple[str, str],
    levels: Sequence[float],
) -> Tuple[float, float, str]:
    """Mondrian CV+'s edges for a day in group `target`, and the level used.

    `lows[i]`, `highs[i]` are CV+'s terms for held-out row `i` at the day's
    feature row, and `groups[i]` its `(calendar type, regime)`. The level is
    `"cell"` (the day's own group), `"day_type"` (its calendar type in every
    regime) or `"pooled"` (CV+), the first with enough terms for both ranks.

    Raises:
        ValueError: on misaligned inputs, or too few terms even pooled.
    """

    from . import ml

    if not len(lows) == len(highs) == len(groups):
        raise ValueError(
            f"{len(lows)} lows, {len(highs)} highs and {len(groups)} groups; "
            f"they are aligned by held-out row"
        )
    minimum = ml._minimum_calibration_rows(levels)
    for level, member in (
        ("cell", lambda group: group == target),
        ("day_type", lambda group: group[0] == target[0]),
        ("pooled", lambda group: True),
    ):
        chosen = [i for i, group in enumerate(groups) if member(group)]
        if len(chosen) >= minimum:
            lower, upper = ml._cross_conformal_edges(
                [lows[i] for i in chosen], [highs[i] for i in chosen], levels
            )
            return lower, upper, level
    raise ValueError(
        f"{len(lows)} held-out terms, fewer than the {minimum} a band needs"
    )


class SelectedBlock(NamedTuple):
    """One refit block of nested selection: when it starts, and what it chose.

    `anchor` is the refit's latest observable label; `past_days` the scored
    days the choice was made on; `chosen` the index of the candidate used for
    every day of the block.
    """

    first_scored: date
    anchor: date
    past_days: int
    chosen: int


class NestedSelection(NamedTuple):
    """The candidate used on each scored day, and the choice made at each refit."""

    per_day: Tuple[int, ...]
    blocks: Tuple[SelectedBlock, ...]


def select_constants(
    history: Sequence[Tuple[date, Sequence[float]]],
    anchor: date,
    candidates: int,
    *,
    fallback: int,
) -> Tuple[int, int]:
    """The candidate with the least pooled loss over `history`, and its length.

    `history` holds `(scored_date, losses)` for past scored days, `losses[k]`
    the loss candidate `k` scored that day. Ties go to the earlier candidate.
    With no history the choice is `fallback`.

    Raises:
        LookAheadError: a day in `history` is scored after `anchor`, so its
            label was not observable at the refit the choice is made for.
        ValueError: a day's losses are not `candidates` finite numbers.
    """

    totals = [0.0] * candidates
    for scored_date, losses in history:
        if scored_date > anchor:
            raise LookAheadError(
                f"the loss of {scored_date} is not observable at a refit whose "
                f"latest observable label is {anchor}; constants are chosen only "
                f"from days scored before the refit"
            )
        if len(losses) != candidates or not all(math.isfinite(loss) for loss in losses):
            raise ValueError(
                f"{scored_date}: losses {tuple(losses)} are not {candidates} finite numbers"
            )
        for k, loss in enumerate(losses):
            totals[k] += loss
    if not history:
        return fallback, 0
    return totals.index(min(totals)), len(history)


def nested_selection(
    scored_dates: Sequence[date],
    anchors: Sequence[date],
    losses: Sequence[Sequence[float]],
    refit_every: int,
    *,
    fallback: int,
) -> NestedSelection:
    """Nested walk-forward selection on the one fold grid.

    The scored days are cut into the backtest's refit blocks
    (`asof.refit_blocks`). At each block's refit the candidate is chosen by
    pooled loss over every scored day whose label was observable there
    (scored on or before the first row's anchor), and used for every day of
    the block. `fallback` is used while no such day exists.

    Raises:
        ValueError: on misaligned inputs.
        LookAheadError: from `select_constants`, if a later day reaches it.
    """

    from .asof import refit_blocks

    if not len(scored_dates) == len(anchors) == len(losses):
        raise ValueError(
            f"{len(scored_dates)} scored days, {len(anchors)} anchors and "
            f"{len(losses)} loss rows; they are aligned"
        )
    candidates = len(losses[0]) if losses else 0
    per_day: List[int] = [fallback] * len(scored_dates)
    blocks: List[SelectedBlock] = []
    for block in refit_blocks(range(len(scored_dates)), refit_every):
        anchor = anchors[block[0]]
        history = [
            (when, loss) for when, loss in zip(scored_dates, losses) if when <= anchor
        ]
        chosen, past = select_constants(history, anchor, candidates, fallback=fallback)
        for position in block:
            per_day[position] = chosen
        blocks.append(SelectedBlock(scored_dates[block[0]], anchor, past, chosen))
    return NestedSelection(tuple(per_day), tuple(blocks))


#: The calibrations a fold loop runs alongside an uncalibrated fit, rather
#: than a fit runs on its own training frame (`--calibration`, #124).
ONLINE_CALIBRATIONS = ("conformal_pid", "conformal_pid_nested")

#: The names of the constants conformal PID is declared with, as a record
#: names them.
_PID_CONSTANT_NAMES = (
    "PID_STEP",
    "PID_STEP_WINDOW",
    "PID_SCALE_FLOOR",
    "PID_INTEGRATOR_GAIN",
    "PID_SATURATION",
    "PID_TANGENT_LIMIT",
    "SCORECASTER_MINIMUM",
    "SCORECASTER_INDICATOR_MINIMUM",
)

#: Those of them nested selection holds fixed: the rest are `PidConstants`,
#: chosen at each refit from `PID_GRID`.
_PID_FIXED_NAMES = (
    "PID_STEP_WINDOW",
    "PID_SCALE_FLOOR",
    "PID_TANGENT_LIMIT",
    "SCORECASTER_INDICATOR_MINIMUM",
)


class _PidView:
    """The block's fit as one scored day reads it under conformal PID.

    `predict` is the issued band; everything else is the fit's own, so the
    point forecast is the uncalibrated median, which a band never moves.
    """

    def __init__(self, model, feature_date: date, vector: Tuple[float, ...]) -> None:
        self._model = model
        self._feature_date = feature_date
        self._vector = vector

    def __getattr__(self, name):
        return getattr(self._model, name)

    def predict(self, feature_row: DailyObservation) -> Tuple[float, ...]:
        if feature_row.date != self._feature_date:
            raise ValueError(
                f"this band was issued for the forecast read at {self._feature_date}, "
                f"not {feature_row.date}"
            )
        return self._vector


class FoldPid:
    """Conformal PID alongside a fold loop, over one panel and one as-of rule.

    The loop hands over each scored day once, in date order: `view` (or `law`)
    issues the day's band from the block's uncalibrated fit, and `label` tells
    it the day's realised spread after the day is scored. A label is observed
    only at a later decision whose anchor has reached its day (`OnlinePid`,
    `PidState.observe`). The scorecaster's calendar is read for the scored day
    at its decision instant (`scorecaster_calendar`), off `splits`' month-end
    window.

    Raises (from `view`, `law` and `label`):
        LookAheadError: a day anchored on or after its own scored day; a
            settlement not yet public at the decision.
        ValueError: a base fit that is calibrated or carries a tail; a band
            issued while the previous day's label is outstanding, or a label
            for a day other than the one issued.
    """

    name = "conformal_pid"

    def __init__(self, rows: Sequence[DailyObservation], rule: InformationRule, *, splits) -> None:
        self._rows = rows
        self._dates = [row.date for row in rows]
        self._rule = rule
        self._splits = splits
        self._online: Optional[OnlinePid] = None
        self._open: Optional[Tuple[int, OnlineDay, OnlineBand]] = None
        self._bands: List[OnlineBand] = []

    @property
    def settings(self) -> dict:
        """The declaration a record carries: the method and its constants."""

        constants = {name: globals()[name] for name in _PID_CONSTANT_NAMES}
        constants["SCORECASTER_INDICATORS"] = list(SCORECASTER_INDICATORS)
        return {"calibration": self.name, "calibration_constants": constants}

    def account(self) -> dict:
        """What the run did: its days, its burn-in, its clipped days, its mean `q_t`."""

        bands = self._bands
        return {
            "days": len(bands),
            "days_before_first_label": sum(1 for band in bands if band.observed == 0),
            "saturated_days": sum(1 for band in bands if band.saturated),
            "mean_quantile_bps": sum(band.quantile for band in bands) / len(bands) if bands else None,
        }

    def _issue(self, index: int, anchor: date, vector: Sequence[float], levels: Sequence[float]) -> OnlineBand:
        if self._open is not None:
            raise ValueError(
                f"the band for {self._dates[self._open[0]]} was issued and its label "
                f"not yet given; a fold loop learns each day's label before the next "
                f"day's band"
            )
        if self._online is None:
            self._online = OnlinePid(levels)
        day = OnlineDay(
            scored_date=self._dates[index],
            anchor=anchor,
            vector=tuple(vector),
            calendar=scorecaster_calendar(self._rows, self._rule, index, self._splits, self._dates),
        )
        band = self._online.issue(day)
        self._open = (index, day, band)
        self._bands.append(band)
        return band

    @staticmethod
    def _require_uncalibrated(model) -> None:
        settings = getattr(model, "model_settings", None) or {}
        if "calibration" in settings or getattr(model, "tail_fit", None) is not None:
            raise ValueError(
                f"conformal PID moves an uncalibrated band; this fit is calibrated "
                f"by {settings.get('calibration')!r}"
                f"{' and carries a tail' if getattr(model, 'tail_fit', None) is not None else ''}"
            )

    def view(self, model, index: int, feature_row: DailyObservation) -> _PidView:
        """`model` as scored day `rows[index]` reads it: the issued band, at `feature_row`."""

        self._require_uncalibrated(model)
        vector = tuple(model.predict(feature_row))
        band = self._issue(index, feature_row.date, vector, model.levels)
        return _PidView(model, feature_row.date, band.vector)

    def law(
        self,
        index: int,
        anchor: date,
        vector: Sequence[float],
        residual_low: float,
        residual_high: float,
        levels: Sequence[float] = QUANTILE_LEVELS,
    ) -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
        """The law of scored day `rows[index]`, from its uncalibrated vector.

        `ml.law_from_band` at the issued edges: the outer levels move by
        `q_t`, and each tail by as much as its edge did.
        """

        from . import ml

        vector = tuple(vector)
        band = self._issue(index, anchor, vector, levels)
        return ml.law_from_band(
            vector,
            vector[0] - band.quantile,
            vector[-1] + band.quantile,
            residual_low,
            residual_high,
            levels,
        )

    def curve(
        self,
        index: int,
        anchor: date,
        vector: Sequence[float],
        residual_low: float,
        residual_high: float,
        taus: Sequence[float],
    ) -> Tuple[float, ...]:
        """`P(spread > tau)` per tau on scored day `rows[index]`, off `law`."""

        from . import ml

        values, knots = self.law(index, anchor, vector, residual_low, residual_high)
        return tuple(ml._exceedance_from_law(values, knots, tau) for tau in taus)

    def label(self, index: int, actual: float) -> None:
        """The realised spread of scored day `rows[index]`, after it is scored."""

        if self._open is None or self._open[0] != index:
            raise ValueError(
                f"a label for {self._dates[index]} was given, but the band open is "
                f"{'none' if self._open is None else self._dates[self._open[0]]}; "
                f"a label is learned once, after its own day's band"
            )
        _, day, band = self._open
        self._online.record(day, band, actual)
        self._open = None


class NestedFoldPid(FoldPid):
    """Conformal PID with nested walk-forward selection, alongside a fold loop.

    Every point of `PID_GRID` runs its own `OnlinePid` over every scored day,
    as `scripts/pid_constant_selection.py` runs them (#125). The band issued is
    the chosen point's. The choice is made at the first scored day of each
    block of `refit_every` scored days, the backtest's own refit blocks
    (`asof.refit_blocks`): the point with the least pooled CRPS over the scored
    days whose labels were observable at that day's anchor
    (`select_constants`, the guard), and #122's point while there are none.
    It is `nested_selection` taken one day at a time. `blocks` records the
    choices.

    Raises (besides `FoldPid`'s):
        LookAheadError: from `select_constants`, if a day scored after a
            refit's anchor reached its choice.
    """

    name = "conformal_pid_nested"

    def __init__(
        self,
        rows: Sequence[DailyObservation],
        rule: InformationRule,
        *,
        splits,
        refit_every: int,
        grid: Sequence[PidConstants] = PID_GRID,
    ) -> None:
        from .asof import require_refit_every

        super().__init__(rows, rule, splits=splits)
        self._refit_every = require_refit_every(refit_every)
        self._grid = tuple(grid)
        self._fallback = self._grid.index(DECLARED_PID)
        self._onlines: Optional[List[OnlinePid]] = None
        self._levels: Optional[Tuple[float, ...]] = None
        self._issued: Optional[Tuple[OnlineBand, ...]] = None
        self._losses: List[Tuple[date, Tuple[float, ...]]] = []
        self._chosen = self._fallback
        self.blocks: Tuple[SelectedBlock, ...] = ()

    @property
    def settings(self) -> dict:
        """The method, the constants it holds fixed, and how it chooses the rest."""

        constants = {name: globals()[name] for name in _PID_FIXED_NAMES}
        constants["SCORECASTER_INDICATORS"] = list(SCORECASTER_INDICATORS)
        return {
            "calibration": self.name,
            "calibration_constants": constants,
            "calibration_selection": {
                "method": "nested walk-forward selection (#125)",
                "loss": "crps",
                "refit_every": self._refit_every,
                "points": len(self._grid),
                "grid": {
                    "steps": list(PID_GRID_STEPS),
                    "integrator_gains": list(PID_GRID_INTEGRATOR_GAINS),
                    "saturations": list(PID_GRID_SATURATIONS),
                    "scorecaster_minimums": list(PID_GRID_SCORECASTER_MINIMUMS),
                },
                "fallback": DECLARED_PID._asdict(),
            },
        }

    def account(self) -> dict:
        """`FoldPid.account`, and the point chosen at each refit block."""

        account = super().account()
        account["blocks"] = [
            {
                "first_scored": block.first_scored.isoformat(),
                "anchor": block.anchor.isoformat(),
                "past_days": block.past_days,
                "chosen": self._grid[block.chosen]._asdict(),
            }
            for block in self.blocks
        ]
        return account

    def _issue(self, index: int, anchor: date, vector: Sequence[float], levels: Sequence[float]) -> OnlineBand:
        if self._open is not None:
            raise ValueError(
                f"the band for {self._dates[self._open[0]]} was issued and its label "
                f"not yet given; a fold loop learns each day's label before the next "
                f"day's band"
            )
        if self._onlines is None:
            self._levels = tuple(levels)
            self._onlines = [OnlinePid(levels, point) for point in self._grid]
        day = OnlineDay(
            scored_date=self._dates[index],
            anchor=anchor,
            vector=tuple(vector),
            calendar=scorecaster_calendar(self._rows, self._rule, index, self._splits, self._dates),
        )
        bands = tuple(online.issue(day) for online in self._onlines)
        if len(self._bands) % self._refit_every == 0:
            history = [(when, losses) for when, losses in self._losses if when <= anchor]
            self._chosen, past = select_constants(
                history, anchor, len(self._grid), fallback=self._fallback
            )
            self.blocks += (SelectedBlock(day.scored_date, anchor, past, self._chosen),)
        band = bands[self._chosen]
        self._open = (index, day, band)
        self._issued = bands
        self._bands.append(band)
        return band

    def label(self, index: int, actual: float) -> None:
        """The realised spread of scored day `rows[index]`, for every point."""

        from .metrics import crps_from_quantiles

        if self._open is None or self._open[0] != index:
            raise ValueError(
                f"a label for {self._dates[index]} was given, but the band open is "
                f"{'none' if self._open is None else self._dates[self._open[0]]}; "
                f"a label is learned once, after its own day's band"
            )
        _, day, _ = self._open
        losses = []
        for online, band in zip(self._onlines, self._issued):
            online.record(day, band, actual)
            losses.append(crps_from_quantiles(self._levels, band.vector, float(actual)))
        self._losses.append((day.scored_date, tuple(losses)))
        self._open = None
        self._issued = None
