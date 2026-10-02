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
The rest of the method is held at #122's values and not searched:
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
from .contract import field_sources_for_features
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
    state = PidState(levels, constants)
    pending: Deque[Tuple[OnlineDay, OnlineBand, float]] = deque()
    bands: List[OnlineBand] = []
    for day, actual in zip(days, actuals):
        while pending and pending[0][0].scored_date <= day.anchor:
            earlier, issued, label = pending.popleft()
            state.observe(earlier, issued, label, day)
        band = state.band(day)
        bands.append(band)
        pending.append((day, band, float(actual)))
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
