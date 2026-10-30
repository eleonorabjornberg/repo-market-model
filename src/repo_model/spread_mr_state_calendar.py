"""State-scaled calendar effects on volatility-scaled mean reversion, read at the target day (#1145; H5 step 3, the fix of #1115).

`metadata/state_calendar_1145.json` is the declaration; this module is its arithmetic. (s3) below is the base of (s3c), which caps it at the SRF line from full allotment (`repo_model.s3c_candidate`, #1256; the H5 candidate from #1259), and so of (s3c-ann-net), which reads (s3c)'s settlement terms from the auction announcement and sizes them by net settlement (`repo_model.s3c_announced`; the H5 candidate since #1310). #1115 estimated one effect in basis points
per calendar term and applied it everywhere, so it lost where the state was quiet (2020, 2021-23) and won where it was loud. Here
the effect scales with the state. The base is `repo_model.spread_mr_fhs`'s declared variant `spread_mr_fhs_mad20_f0.5` (#941),
unchanged: `level + phi^k (last - level) + scale(anchor) * z_h`. Four arms add declared terms to it, in the model's own
standardised units (the raw residual of a pair divided by the scale at the pair's origin):

* (s1) each term's effect is a number of scale units, so the effect in bp is the term times the anchor's as-of scale and shrinks
  when the regime is quiet;
* (s2) (s1), and each term is also interacted with the as-of scarcity state (`scarcity.own_leg_states`, mapped to `state / 3`, so 0
  on the floor and 1 when reserves are scarce), the coupon and bill settlements being separate terms;
* (s3) (s1) with a Huber fit (the threshold 1.345 robust standard deviations of the current residuals, re-weighted until it stops)
  and a heavier ridge, so an outlier day (March 2020) does not set the effect and a term with few flagged days is shrunk toward 0;
* (s4) (s1) with the FOMC and IORB terms added, the separate arm of the ruling.

The arms that take (s3) apart (#1172) are (r1) (s1) with (s3)'s ridge alone, (r2) (s1) with (s3)'s Huber fit alone, and (r3) (s3)
with the announced size of the coupon and bill settlements (USD billions over `SIZE_UNIT`) times the scarcity state in place of the
0/1 flags. A size is a scheduled field of the target row: it is read at lead 1 only, where `asof` rule 2 admits it
(`SizeTable`), and the announcement dating that would admit it at leads 2 to 5 is not in force.

**A term** is a 0/1 flag of the *target* row, `spread_mr_calendar.TermTable`'s: its flag is read at the target day on direct
pairs, never from the origin, and a scheduled field is read only where `asof` rule 2 admits it. **The state** is a slow variable
of the decision, not of the target: it is the state as read at the decision instant of the pair (the legs each at their latest
public row, #586), keyed here by the *decision day* (`states[d]` is what a decision on day `d` could read). A training pair is
trained on the state of its own decision day (`pair_state`), and a forecast reads the state of its own decision day
(`read_state`), which raises `LookAheadError` for any later day. `fit_state_terms` is decorated with
`one_step_guard.guard_one_step_fit`: on direct pairs it needs no allow-list entry; a one-step fit of the same columns raises
`ValueError`.

Stdlib only.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from datetime import date, time
from typing import Dict, Iterable, List, Mapping, NamedTuple, Optional, Sequence, Tuple

from .decision_instant import DECISION_TIME
from . import announced_iorb
from . import protocol_benchmarks as pb
from . import setup_diagnostic
from . import spread_mean_reversion as smr
from . import spread_mr_calendar as cal
from . import spread_mr_fhs as fhs
from . import turn_days
from .data import DailyObservation
from .evaluation_splits import SplitDeclaration
from .one_step_guard import guard_one_step_fit
from .scoring_protocol import HORIZONS, ProtocolError
from .splits import LookAheadError, SplitError

#: The L2 penalty on every term coefficient of the least-squares arms, in pseudo-days (none on the intercept): #1115's.
RIDGE = cal.RIDGE
#: The heavier penalty of the robust arm: five pseudo-days, so a term with four flagged days keeps under half its effect.
ROBUST_RIDGE = 5.0
#: A term enters a lead's fit only if this many training pairs carry its flag: #1115's.
MIN_FLAGGED = cal.MIN_FLAGGED
#: Huber's threshold, in robust standard deviations of the current residuals (1.4826 times their median absolute deviation).
HUBER_K = 1.345
MAX_ITERATIONS = 50
TOLERANCE = 1e-8
#: The highest scarcity state; the interaction variable is `state / STATE_MAX`.
STATE_MAX = 3.0
BASE_VARIANT = cal.BASE_VARIANT
ARM_A = cal.ARM_A
#: The settlement terms whose size can stand in for the flag (#1172, (r3)).
SIZED_TERMS: Tuple[str, ...] = ("settlement_coupon", "settlement_bill")
#: A settlement size is read in units of USD 100 bn (a coupon settlement is typically 0.5 to 1.5 of them).
SIZE_UNIT = 100.0


@dataclass(frozen=True)
class StateArm:
    """One declared arm. `location` are the terms (the name matches `spread_mr_calendar.Arm` for `regressors_of`)."""

    name: str
    role: str
    location: Tuple[str, ...]
    interact: bool
    robust: bool
    #: No arm has a scale term; the field lets `spread_mr_calendar.regressors_of` read an arm of this module.
    scale: Tuple[str, ...] = ()
    #: The L2 penalty on the term coefficients, in pseudo-days; `None` is `RIDGE`, or `ROBUST_RIDGE` for a robust arm (#1145's).
    ridge: Optional[float] = None
    #: The settlement terms enter as `size / SIZE_UNIT * state` instead of as 0/1 flags (#1172, (r3)).
    sized: bool = False
    #: The terms that are not 0/1 flags of the target row: the signed announced IORB change and the technical-adjustment indicator
    #: (`IORB_EXTRAS`, #1227), read from an `IorbTable`. They enter the fit after the flag terms.
    extra: Tuple[str, ...] = ()
    #: Huber's threshold on a calendar target row, as a multiple of the ordinary threshold (#1226): `None` treats it as any row,
    #: `FULL_WEIGHT` never downweights it, `CALENDAR_K` gives it its own, wider, threshold. Needs `robust`.
    calendar_k: Optional[float] = None


def ridge_of(arm: StateArm) -> float:
    """The penalty an arm fits with."""

    if arm.ridge is not None:
        return arm.ridge
    return ROBUST_RIDGE if arm.robust else RIDGE


ARMS: Tuple[StateArm, ...] = (
    StateArm("sc_s1_standardised", "(s1) terms in standardised units", cal.NO_FOMC_IORB, False, False),
    StateArm("sc_s2_scarcity", "(s2) (s1) and each term times the scarcity state", cal.NO_FOMC_IORB, True, False),
    StateArm("sc_s3_robust", "(s3) (s1) with a Huber fit and a heavier ridge", cal.NO_FOMC_IORB, False, True),
    StateArm("sc_s4_fomc_iorb", "(s4) (s1) with the FOMC and IORB terms", cal.ALL_TERMS, False, False),
)
ARM_NAMES: Tuple[str, ...] = (ARM_A,) + tuple(arm.name for arm in ARMS)

#: The arms of #1172: (s3)'s two changes apart, and (s3) with the settlement sizes (`metadata/s3_decomposition_1172.json`).
R1 = StateArm("sc_r1_ridge5", "(r1) (s1) with the ridge of 5 alone", cal.NO_FOMC_IORB, False, False, ridge=ROBUST_RIDGE)
R2 = StateArm("sc_r2_huber", "(r2) (s1) with the Huber fit alone", cal.NO_FOMC_IORB, False, True, ridge=RIDGE)
R3 = StateArm("sc_r3_size", "(r3) (s3) with settlement size times the scarcity state", cal.NO_FOMC_IORB, False, True, sized=True)
#: (s1), (r1), (r2), (s3) and (r3): the 2 x 2 of the ridge and the Huber fit, and the sized arm.
DECOMPOSITION: Tuple[StateArm, ...] = (ARMS[0], R1, R2, ARMS[2], R3)

#: The arms of #1196: (s3)'s Huber fit and ridge of 5 with the two terms that were tried only on the least-squares fit
#: (`metadata/s3_terms_1196.json`). (s3+state) is (s3) with each term times the as-of scarcity state, as (s2); (s3+FOMC/IORB) is (s3)
#: with `fomc_day` and `iorb_window`, as (s4).
S3_STATE = StateArm("sc_s3_state", "(s3+state) (s3) and each term times the scarcity state", cal.NO_FOMC_IORB, True, True)
S3_CAL = StateArm("sc_s3_fomc_iorb", "(s3+FOMC/IORB) (s3) with the FOMC and IORB terms", cal.ALL_TERMS, False, True)
#: (s3) and the two arms that add to it.
S3_TERMS: Tuple[StateArm, ...] = (ARMS[2], S3_STATE, S3_CAL)

#: The signed announced IORB change and a technical-adjustment indicator beside `iorb_window` (#1227, `metadata/s3_iorbs_1227.json`).
IORB_UNIT_BPS = 25.0
IORB_SIGNED = "iorb_signed"
IORB_TECHNICAL = "iorb_technical"
IORB_EXTRAS: Tuple[str, ...] = (IORB_SIGNED, IORB_TECHNICAL)
#: An IORB change that is not a multiple of 25 bp is a technical adjustment: the rule of `setup_diagnostic`.
technical = setup_diagnostic.is_technical
#: (s3+IORBs): (s3), with `iorb_window` and the two terms beside it. The FOMC-day term is not added.
S3_IORBS = StateArm(
    "sc_s3_iorbs", "(s3+IORBs) (s3) with the signed announced IORB change and a technical-adjustment indicator beside iorb_window",
    tuple(n for n in cal.ALL_TERMS if n in cal.NO_FOMC_IORB or n == "iorb_window"), False, True, extra=IORB_EXTRAS,
)
#: (s3) and the arm that adds to it.
S3_IORBS_ARMS: Tuple[StateArm, ...] = (ARMS[2], S3_IORBS)

#: The arms of #1226 (`metadata/s3_huber_calendar_1226.json`): (s3) with its Huber downweighting kept off the calendar target rows.
#: (s3-hw1) never downweights a calendar row; (s3-hw2) gives those rows a Huber threshold `CALENDAR_K` times the ordinary one. The
#: terms, the ridge of 5, the direct pairs and the turn record are (s3)'s.
FULL_WEIGHT = math.inf
CALENDAR_K = 2.0
HW1 = StateArm("sc_s3_hw1", "(s3-hw1) (s3) with calendar target rows at full weight in the Huber fit", cal.NO_FOMC_IORB, False, True,
               calendar_k=FULL_WEIGHT)
HW2 = StateArm("sc_s3_hw2", "(s3-hw2) (s3) with the calendar rows' Huber threshold at 2 times the ordinary one", cal.NO_FOMC_IORB,
               False, True, calendar_k=CALENDAR_K)
#: (s3) and the two arms that change how it weights the calendar rows.
HW_ARMS: Tuple[StateArm, ...] = (ARMS[2], HW1, HW2)
#: The target-row types whose rows are calendar rows: the turn types of the record in force (`turn_days.turn_label`) and the types
#: of the directive's list. `dom_19_23` and `post_month_end_window` are terms of the fit but too broad to name a calendar row.
CALENDAR_ROW_TERMS: Tuple[str, ...] = (
    "month_end", "quarter_end", "tax_date", "settlement_coupon", "settlement_bill", "fomc_day", "iorb_window")
ALL_ARMS: Mapping[str, StateArm] = {arm.name: arm for arm in ARMS + (R1, R2, R3, S3_STATE, S3_CAL, HW1, HW2, S3_IORBS)}


def calendar_row(table: cal.TermTable, dates: Sequence[date], row: int, anchor: int) -> bool:
    """Whether training row `row` (a pair's target) carries a calendar type, read from that row alone.

    The type is the row's own turn label (`turn_days`) or one of `CALENDAR_ROW_TERMS` as `TermTable.day_types` reads it. A training
    pair's target is on or before the decision's anchor, so the row is already public; a later row is refused.

    Raises:
        LookAheadError: `row` is after `anchor`.
    """

    if row > anchor:
        raise LookAheadError(f"the type of row {row} ({dates[row]}) is read for a training pair, but the anchor is row {anchor}")
    flags = table.day_types(row)
    return any(flags[name] for name in CALENDAR_ROW_TERMS) or turn_days.turn_label(dates[row]) is not None


# -- the state, as a decision could read it ----------------------------------------------------------------------------------


def level(state: Optional[float]) -> Optional[float]:
    """The interaction variable: the scarcity state (0 abundant to 3 scarce) over 3, so 0 on the floor and 1 when scarce.

    Raises:
        ValueError: a state outside 0 to 3.
    """

    if state is None:
        return None
    if not 0.0 <= state <= STATE_MAX:
        raise ValueError(f"the scarcity state is 0 to {STATE_MAX:g}, got {state}")
    return state / STATE_MAX


def read_state(states: Mapping[date, Optional[float]], dates: Sequence[date], row: int, decision_index: int) -> Optional[float]:
    """The scarcity state of the decision on row `row`, read by the decision on row `decision_index`; `None` if not known.

    `states[d]` is the state as read at the decision instant of day `d`: each leg at its latest row public then.

    Raises:
        LookAheadError: `row` is after the decision (its state is not public at the decision instant).

    Mutation record: see `tests/test_spread_mr_state_calendar.py` (`read_state`).
    """

    if row > decision_index:
        raise LookAheadError(
            f"the scarcity state of {dates[row]} is read by the decision on {dates[decision_index]}, before it can be known"
        )
    return states.get(dates[row])


def pair_state(states: Mapping[date, Optional[float]], dates: Sequence[date], origin: int, lag: int, decision_index: int) -> Optional[float]:
    """The state a training pair with origin row `origin` is trained on: that of its own decision day, `origin + lag`.

    Mutation record: see `tests/test_spread_mr_state_calendar.py` (`pair_state`).
    """

    decision_row = origin + lag
    return read_state(states, dates, decision_row, decision_index)


# -- the estimation ---------------------------------------------------------------------------------------------------------


class SizeTable:
    """The announced size, in USD billions, of the coupon and bill settlements at every panel row (#1172).

    A size is a scheduled field of the *target* row (`treasury_settlement_coupons`, `treasury_settlement_bills`): it is public at
    15:00 on the panel day before it, so a decision reads it at lead 1 only (`spread_mr_calendar.readable_offsets`), exactly as the
    0/1 flag of the same term. The announcement dating that would admit it at leads 2 to 5 (`metadata/settlement_announcement_dating.json`)
    is not in force and is not used here.
    """

    def __init__(self, panel: Sequence[DailyObservation]):
        self.dates = [row.date for row in panel]
        self._values: Dict[str, List[float]] = {
            "settlement_coupon": [float(row.values.get("treasury_settlement_coupons") or 0.0) for row in panel],
            "settlement_bill": [float(row.values.get("treasury_settlement_bills") or 0.0) for row in panel],
        }

    def sizes_at(self, lead: int, row: int) -> Dict[str, float]:
        """The sizes of the terms readable at `lead`, at row `row` (a training row: public by construction)."""

        return {name: values[row] for name, values in self._values.items() if cal.available(cal.TERM[name], lead)}

    def read(self, lead: int, decision_index: int) -> Dict[str, float]:
        """The sizes a forecast of the decision on row `decision_index` at `lead` reads, from the target row.

        Raises:
            LookAheadError: a scheduled field of a row that is not public at the decision (`cal.require_public`).

        Mutation record: see `tests/test_spread_mr_s3_decomposition.py` (`SizeTable.read`).
        """

        row = cal.target_row(decision_index, lead)
        out = {}
        for name, values in self._values.items():
            term = cal.TERM[name]
            if not cal.available(term, lead):
                continue
            cal.require_public(term, [row - j for j in cal.readable_offsets(term, lead)], decision_index, self.dates)
            out[name] = values[row]
        return out


class IorbTable:
    """The signed announced IORB change and the technical-adjustment indicator at every panel row, as a lead can read them (#1227).

    Both are functions of `iorb_announced_change_bps`, a scheduled field of the *target* row (public on the panel day before it,
    `metadata/sources.json`, `scheduled_availability`), so they are read exactly as the flag `iorb_window` is
    (`spread_mr_calendar.readable_offsets`): the value at a target row `T` is taken over the rows `T - j` of the window the decision
    `lead` rows before can read (the day of the change and the two panel days after it, `j >= lead - 1`), summed (a window holds at
    most one change); `iorb_signed` is that sum over `IORB_UNIT_BPS` (so a 25 bp cut is -1), and `iorb_technical` is 1 where a change in
    the window is not a multiple of 25 bp (`technical`). Neither is readable at leads 4 and 5 (the same as the flag). The column is built
    on the announcement time (`announced_iorb`), so a note announced after the decision instant is never in it.
    """

    def __init__(self, panel: Sequence[DailyObservation], announcements: Sequence[announced_iorb.IorbAnnouncement], *,
                 decision_time: time = DECISION_TIME):
        self.dates = [row.date for row in panel]
        self.changes = [
            0.0 if values[announced_iorb.ANNOUNCED_CHANGE] is None else float(values[announced_iorb.ANNOUNCED_CHANGE])
            for values in announced_iorb.announced_iorb_features(self.dates, announcements, decision_time=decision_time)
        ]

    def at(self, lead: int, row: int) -> Dict[str, float]:
        """The two terms at target row `row` for a lead-`lead` decision (a training row: public by construction); `{}` where the
        window is not readable at `lead`."""

        offsets = cal.readable_offsets(cal.TERM["iorb_window"], lead)
        if not offsets:
            return {}
        moved = [self.changes[row - j] for j in offsets if row - j >= 0 and self.changes[row - j] != 0.0]
        return {
            IORB_SIGNED: sum(moved) / IORB_UNIT_BPS,
            IORB_TECHNICAL: 1.0 if any(technical(x) for x in moved) else 0.0,
        }

    def read(self, lead: int, decision_index: int) -> Dict[str, float]:
        """The terms a forecast of the decision on row `decision_index` at `lead` reads, from the target row.

        Raises:
            LookAheadError: a row of the window is not public at the decision (`cal.require_public`).

        Mutation record: see `tests/test_spread_mr_s3_iorbs.py` (`IorbTable.at`).
        """

        row = cal.target_row(decision_index, lead)
        term = cal.TERM["iorb_window"]
        offsets = cal.readable_offsets(term, lead)
        if offsets:
            cal.require_public(term, [row - j for j in offsets], decision_index, self.dates)
        return self.at(lead, row)


class StatePair(NamedTuple):
    """One training pair: its raw residual (bp), the scale at its origin, the flags of the readable terms, the state level.

    `sizes` are the settlement sizes of the target row (USD bn) where the pair has them, and `origin` and `target` its rows, kept
    for the layer of #1172 that scales the pool by a type and a miss; none of them changes an arm that reads the flags.
    """

    raw: float
    scale: float
    flags: Mapping[str, int]
    state: Optional[float]
    sizes: Mapping[str, float] = {}
    origin: int = -1
    target: int = -1
    #: The `IorbTable` terms of the target row (`IORB_EXTRAS`), where the lead can read them (#1227).
    extras: Mapping[str, float] = {}
    #: Whether the pair's target row carries a calendar type (`calendar_row`); read only by an arm with a `calendar_k` (#1226).
    calendar: bool = False


def regressor(name: str, flags: Mapping[str, int], sizes: Mapping[str, float], state: Optional[float], sized: bool) -> float:
    """The column of term `name`: its 0/1 flag, or for a sized settlement term `size / SIZE_UNIT * state` (0 where the state is
    unknown)."""

    if sized and name in SIZED_TERMS:
        return sizes.get(name, 0.0) / SIZE_UNIT * (0.0 if state is None else state)
    return float(flags[name])


def solve_weighted(rows: Sequence[Sequence[float]], y: Sequence[float], weights: Sequence[float], ridge: float) -> List[float]:
    """The weighted least-squares coefficients with an L2 penalty on every column but the first (`cal.solve_ridge` on the rows
    scaled by the square root of their weight)."""

    if len(weights) != len(rows):
        raise ValueError("solve_weighted needs one weight per row")
    root = [w**0.5 for w in weights]
    return cal.solve_ridge([[v * r for v in row] for row, r in zip(rows, root)], [v * r for v, r in zip(y, root)], ridge)


def huber(
    rows: Sequence[Sequence[float]], y: Sequence[float], ridge: float, multipliers: Optional[Sequence[float]] = None
) -> Tuple[List[float], int]:
    """The Huber fit by iteratively re-weighted least squares, and the number of iterations it took.

    `multipliers` (one per row, default 1) scale each row's threshold, `HUBER_K` robust standard deviations of all the current
    residuals: a row with `math.inf` is never downweighted (#1226).
    """

    if multipliers is not None and len(multipliers) != len(rows):
        raise ValueError("huber needs one multiplier per row")
    b = cal.solve_ridge(rows, y, ridge)
    for iteration in range(1, MAX_ITERATIONS + 1):
        residual = [target - sum(c * v for c, v in zip(b, row)) for row, target in zip(rows, y)]
        centre = statistics.median(residual)
        sigma = max(1.4826 * statistics.median([abs(r - centre) for r in residual]), 1e-6)
        cut = HUBER_K * sigma
        cuts = [cut] * len(residual) if multipliers is None else [cut * m for m in multipliers]
        weights = [1.0 if abs(r) <= c else c / abs(r) for r, c in zip(residual, cuts)]
        new = solve_weighted(rows, y, weights, ridge)
        done = max(abs(a - c) for a, c in zip(new, b)) < TOLERANCE
        b = new
        if done:
            return b, iteration
    return b, MAX_ITERATIONS


@dataclass(frozen=True)
class StateEstimate:
    """What a refit keeps for one arm and lead: the effects in standardised units, the state slopes, the pool and the counts."""

    terms: Tuple[str, ...]
    effect: Mapping[str, float]
    slope: Mapping[str, float]
    flagged: Mapping[str, int]
    pool: Sequence[float]
    pairs: int
    unknown_state: int
    iterations: int
    #: Whether the settlement terms are sizes times the state (the estimate is then read with the target row's sizes).
    sized: bool = False
    #: The origin and target rows of each pair and the residual it leaves (`z`, scale units), in the pairs' order.
    origins: Tuple[int, ...] = ()
    targets: Tuple[int, ...] = ()
    residuals: Tuple[float, ...] = ()
    #: The pairs whose target row is a calendar row (set only for an arm with a `calendar_k`, #1226).
    calendar_pairs: int = 0


def _entering(
    names: Sequence[str], pairs: Sequence[StatePair], min_flagged: int, sized: bool = False
) -> Tuple[Tuple[str, ...], Dict[str, int]]:
    counts = {
        name: sum(1 for p in pairs if regressor(name, p.flags, p.sizes, p.state, sized) > 0.0) if sized and name in SIZED_TERMS
        else sum(p.flags[name] for p in pairs)
        for name in names if pairs and name in pairs[0].flags
    }
    return tuple(n for n in cal.ALL_TERMS if n in counts and counts[n] >= min_flagged), counts


@guard_one_step_fit
def fit_state_terms(
    pairs: Sequence[StatePair],
    *,
    regressors: Sequence[str],
    terms: Sequence[str],
    interact: bool,
    robust: bool,
    training_pairs: str,
    min_flagged: int = MIN_FLAGGED,
    ridge: Optional[float] = None,
    sized: bool = False,
    extra: Sequence[str] = (),

    calendar_k: Optional[float] = None,
) -> StateEstimate:
    """The term effects, in standardised units, and the pool of one arm at one lead.

    The target is `raw / scale(origin)`. The columns are the entering terms, and with `interact` each term times the state level
    (0 where the state is unknown); the fit is ridge least squares, or Huber when `robust`, with the penalty `ridge` (`RIDGE`, or
    `ROBUST_RIDGE` for a robust fit, when `None`). With `sized` the settlement terms are `size / SIZE_UNIT * state`, and enter when
    at least `min_flagged` pairs have a positive such column. The intercept is dropped, so the pool, the quantiles of the residual
    after the terms, keeps the ordinary-day centre.

    With `extra` (#1227), the terms of `IorbTable` (`pair.extras`) enter after the flag terms when at least `min_flagged` pairs have a
    non-zero value; a pair without them (a lead that cannot read the window) drops them from the fit. They do not combine with
    `interact`.
    With `calendar_k` the Huber threshold of a pair whose `calendar` is set is `calendar_k` times the ordinary one (`FULL_WEIGHT`:
    never downweighted); it needs `robust`.

    `regressors` are the panel columns the terms read (for `one_step_guard`). `training_pairs` is required, and `'direct'` is the
    only value this fit trains on.

    Raises:
        ValueError: `training_pairs` is not `'direct'`, or `extra` with `interact`.
        InsufficientHistory: there is no pair.
    """

    if training_pairs != "direct":
        raise ValueError(f"fit_state_terms trains on direct pairs only, got training_pairs={training_pairs!r}")
    if extra and interact:
        raise ValueError("the IORB terms (extra) do not combine with the state interaction (interact)")
    if calendar_k is not None and not robust:
        raise ValueError("a calendar threshold is a setting of the Huber fit; the arm is not robust")
    if not pairs:
        raise smr.InsufficientHistory("no training pair to estimate the state-scaled calendar terms on")
    penalty = (ridge if ridge is not None else (ROBUST_RIDGE if robust else RIDGE))
    active, counts = _entering(terms, pairs, min_flagged, sized)
    counts_extra = {name: sum(1 for p in pairs if p.extras.get(name, 0.0) != 0.0) for name in extra if name in pairs[0].extras}
    counts.update(counts_extra)
    active_extra = tuple(n for n in extra if counts_extra.get(n, 0) >= min_flagged)
    target = [p.raw / p.scale for p in pairs]
    effect: Dict[str, float] = {}
    slope: Dict[str, float] = {}
    iterations = 0
    if active or active_extra:
        design = []
        for p in pairs:
            s = 0.0 if p.state is None else p.state
            row = [1.0] + [regressor(name, p.flags, p.sizes, p.state, sized) for name in active] + [p.extras[n] for n in active_extra]
            if interact:
                row += [float(p.flags[name]) * s for name in active]
            design.append(row)
        if robust:
            multipliers = None if calendar_k is None else [calendar_k if p.calendar else 1.0 for p in pairs]
            coefficients, iterations = huber(design, target, penalty, multipliers)
        else:
            coefficients = cal.solve_ridge(design, target, penalty)
        names = active + active_extra
        effect = dict(zip(names, coefficients[1 : 1 + len(names)]))
        if interact:
            slope = dict(zip(active, coefficients[1 + len(active) :]))
    pool = []
    for p, y in zip(pairs, target):
        s = 0.0 if p.state is None else p.state
        pool.append(
            y - sum(effect[n] * regressor(n, p.flags, p.sizes, p.state, sized) for n in effect if n not in IORB_EXTRAS)
            - sum(effect[n] * p.extras[n] for n in effect if n in IORB_EXTRAS)
            - sum(slope[n] * p.flags[n] * s for n in slope)
        )
    return StateEstimate(
        active + active_extra, effect, slope, counts, pb.empirical_quantiles(sorted(pool)), len(pairs),
        sum(1 for p in pairs if p.state is None), iterations, sized,
        tuple(p.origin for p in pairs), tuple(p.target for p in pairs), tuple(pool),
        sum(1 for p in pairs if p.calendar),
    )


def standardised_shift(
    estimate: StateEstimate, flags: Mapping[str, int], state: Optional[float], sizes: Optional[Mapping[str, float]] = None,
    extras: Optional[Mapping[str, float]] = None,
) -> float:
    """The location shift in scale units for a row with `flags` (and `sizes`, for a sized estimate) and the state level `state`
    (`None` reads as 0)."""

    s = 0.0 if state is None else state
    sizes = {} if sizes is None else sizes
    extras = {} if extras is None else extras
    return sum(
        effect * regressor(name, flags, sizes, state, estimate.sized) for name, effect in estimate.effect.items()
        if name not in IORB_EXTRAS
    ) + sum(effect * extras.get(name, 0.0) for name, effect in estimate.effect.items() if name in IORB_EXTRAS) + sum(g * flags[name] * s for name, g in estimate.slope.items())


def lead_quantiles(
    estimate: StateEstimate, *, centre: float, scale: float, flags: Mapping[str, int], state: Optional[float],
    sizes: Optional[Mapping[str, float]] = None, extras: Optional[Mapping[str, float]] = None,
) -> List[float]:
    """The 23 quantiles: `centre + scale * (shift + pool)`, so the effect in bp is the shift times the anchor's scale."""

    shift = standardised_shift(estimate, flags, state, sizes, extras)
    return [centre + scale * (shift + value) for value in estimate.pool]


# -- the walk ---------------------------------------------------------------------------------------------------------------


def refit(
    panel: Sequence[DailyObservation],
    decision_index: int,
    table: cal.TermTable,
    states: Mapping[date, Optional[float]],
    arms: Sequence[StateArm],
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    levels: Sequence[Optional[float]],
    base: smr.Fit,
    training_pairs: str = "direct",
    sizes: Optional[SizeTable] = None,
    iorb: Optional[IorbTable] = None,
) -> Dict[str, Dict[int, StateEstimate]]:
    """Each arm's estimate at each lead as of the decision on row `decision_index`, on the base model's training pairs.

    Raises:
        InsufficientHistory: the base fit's, or a lead with no pair that has a scale.
        LookAheadError: a row the scale reads is after the anchor, or a state is read after the decision.
        ValueError: the one-step guard (`fit_state_terms`).
    """

    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    lag = decision_index - anchor
    rows = smr.training_rows(panel, decision_index, anchor, lag=lag, levels=levels)
    dates = [row.date for row in panel]
    spreads = [row.spread_bps for row in panel[: anchor + 1]]
    origins = sorted({origin for h in HORIZONS for origin, _ in rows[h]} | {anchor})
    variant = BASE_VARIANT
    read = {j for origin in origins if origin - variant.window >= 0 for j in fhs.scale_rows(origin, variant.window)}
    pb._require_public(read, anchor, dates, f"the scale of {variant.name} for {dates[decision_index]}")
    reader = fhs.ScaleReader(spreads, variant)
    out: Dict[str, Dict[int, StateEstimate]] = {}
    typed: Dict[int, bool] = {}
    for arm in arms:
        if arm.sized and sizes is None:
            raise ValueError(f"{arm.name} reads the settlement sizes and needs the size table")
        if arm.extra and iorb is None:
            raise ValueError(f"{arm.name} reads the announced IORB change and needs the IORB table")
        per_lead: Dict[int, StateEstimate] = {}
        for h in HORIZONS:
            k = h + lag
            pairs = []
            for origin, target in rows[h]:
                scale = reader.at(origin)
                if scale is None:
                    continue
                raw = (spreads[target] - levels[origin]) - base.phi**k * (spreads[origin] - levels[origin])
                flags_row = target if training_pairs == "direct" else origin
                state = level(pair_state(states, dates, origin, lag, decision_index)) if (arm.interact or arm.sized) else None
                size = sizes.sizes_at(h, flags_row) if arm.sized else {}
                extras = iorb.at(h, flags_row) if arm.extra else {}
                if arm.calendar_k is not None and target not in typed:
                    typed[target] = calendar_row(table, dates, target, anchor)
                pairs.append(StatePair(raw, scale, table.flags_at(h, flags_row), state, size, origin, target, extras,
                                       typed.get(target, False) if arm.calendar_k is not None else False))
            if not pairs:
                raise smr.InsufficientHistory(f"{dates[decision_index]}: no training pair of lead {h} has a scale")
            per_lead[h] = fit_state_terms(
                pairs, regressors=cal.regressors_of(arm, h), terms=arm.location, interact=arm.interact, robust=arm.robust,
                training_pairs=training_pairs, ridge=arm.ridge, sized=arm.sized, extra=arm.extra,
                calendar_k=arm.calendar_k,
            )
        out[arm.name] = per_lead
    return out


def forecast(
    panel: Sequence[DailyObservation],
    decision_index: int,
    estimates: Mapping[str, Mapping[int, StateEstimate]],
    table: cal.TermTable,
    states: Mapping[date, Optional[float]],
    arms: Sequence[StateArm],
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    levels: Sequence[Optional[float]],
    base: smr.Fit,
    sizes: Optional[SizeTable] = None,
    iorb: Optional[IorbTable] = None,
) -> Tuple[Dict[str, Dict[int, List[float]]], Dict[str, object]]:
    """The arms' forecasts of the decision day from `estimates` (possibly an older fit), and the day's detail (the scale at the
    anchor and the state level): `last`, `level`, `k`, the anchor, its scale, the flags of each target row and the state of the
    decision day are read afresh.

    Raises:
        InsufficientHistory: the anchor has no level or no scale.
        LookAheadError: a row the scale at the anchor reads, a scheduled field of a target row, or a state is not public.
    """

    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    level_at = levels[anchor]
    if level_at is None:
        raise smr.InsufficientHistory(f"{panel[decision_index].date}: fewer than {smr.LEVEL_DAYS} ordinary days before the anchor")
    dates = [row.date for row in panel]
    variant = BASE_VARIANT
    if anchor - variant.window >= 0:
        pb._require_public(
            fhs.scale_rows(anchor, variant.window), anchor, dates, f"the scale of {variant.name} at the anchor of {dates[decision_index]}"
        )
    scale = fhs.ScaleReader([row.spread_bps for row in panel[: anchor + 1]], variant).at(anchor)
    if scale is None:
        raise smr.InsufficientHistory(f"{dates[decision_index]}: fewer than {variant.window + 1} rows before the anchor")
    state = level(read_state(states, dates, decision_index, decision_index))
    lag = decision_index - anchor
    last = panel[anchor].spread_bps
    out: Dict[str, Dict[int, List[float]]] = {arm.name: {} for arm in arms}
    for h in HORIZONS:
        flags = table.read(h, decision_index)
        centre = level_at + base.phi ** (h + lag) * (last - level_at)
        read_sizes = sizes.read(h, decision_index) if sizes is not None and any(a.sized for a in arms) else {}
        read_extras = iorb.read(h, decision_index) if iorb is not None and any(a.extra for a in arms) else {}
        for arm in arms:
            if arm.sized and sizes is None:
                raise ValueError(f"{arm.name} reads the settlement sizes and needs the size table")
            if arm.extra and iorb is None:
                raise ValueError(f"{arm.name} reads the announced IORB change and needs the IORB table")
            out[arm.name][h] = lead_quantiles(
                estimates[arm.name][h], centre=centre, scale=scale, flags=flags, state=state if (arm.interact or arm.sized) else None,
                sizes=read_sizes if arm.sized else None, extras=read_extras if arm.extra else None,
            )
    return out, {"scale": scale, "state": state}


@dataclass(frozen=True)
class Walk:
    #: Arm name -> decision day -> lead -> 23 quantiles; `ARM_A` is #941's variant, forecast by `spread_mr_fhs`.
    forecasts: Dict[str, Dict[date, Dict[int, List[float]]]]
    fit_used: Dict[date, date]
    #: Refit day -> the base fit.
    fits: Dict[date, smr.Fit]
    #: Refit day -> arm name -> lead -> the estimate.
    estimates: Dict[date, Dict[str, Dict[int, StateEstimate]]]
    #: Decision day -> the scale at the anchor and the state level the forecast read.
    detail: Dict[date, Dict[str, object]]
    skipped: Tuple[date, ...]


def walk(
    panel: Sequence[DailyObservation],
    decision_days: Iterable[date],
    table: cal.TermTable,
    states: Mapping[date, Optional[float]],
    arms: Sequence[StateArm] = ARMS,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    refit_every: int = smr.REFIT_EVERY,
    training_pairs: str = "direct",
    sizes: Optional[SizeTable] = None,
    iorb: Optional[IorbTable] = None,
) -> Walk:
    """Arm (a) and `arms` on `decision_days`, refitting as `spread_mr_fhs.walk` does (the base fit and #941's pool, then the terms).

    `states[d]` is the scarcity state a decision on day `d` could read. A day on which any arm has no forecast is skipped for all,
    so the arms are compared on the same days.
    """

    if refit_every < 1:
        raise ValueError(f"refit_every must be at least 1, got {refit_every}")
    position = {row.date: index for index, row in enumerate(panel)}
    levels = smr.ordinary_levels(panel, splits)
    settings = dict(registry=registry, decision_time=decision_time, splits=splits, levels=levels)
    forecasts: Dict[str, Dict[date, Dict[int, List[float]]]] = {ARM_A: {}, **{arm.name: {} for arm in arms}}
    fit_used: Dict[date, date] = {}
    fits: Dict[date, smr.Fit] = {}
    estimates: Dict[date, Dict[str, Dict[int, StateEstimate]]] = {}
    detail: Dict[date, Dict[str, object]] = {}
    skipped: List[date] = []
    current: Optional[smr.Fit] = None
    current_scaled: Optional[fhs.ScaledFit] = None
    current_estimates: Dict[str, Dict[int, StateEstimate]] = {}
    since = 0
    for day in decision_days:
        if day not in position:
            raise ProtocolError(f"decision day {day} is not a panel day")
        index = position[day]
        try:
            if current is None or since >= refit_every:
                base = smr.fit(panel, index, **settings)
                scaled = fhs.fit(panel, index, [BASE_VARIANT], base=base, **settings)[BASE_VARIANT.name]
                found = refit(
                    panel, index, table, states, arms, registry=registry, decision_time=decision_time, levels=levels, base=base,
                    training_pairs=training_pairs, sizes=sizes, iorb=iorb,
                )
                current, current_scaled, current_estimates = base, scaled, found
                fits[day], estimates[day] = base, found
                since = 0
            today = {ARM_A: fhs.forecast(panel, index, current_scaled, current, BASE_VARIANT, **settings)}
            mine, extra = forecast(
                panel, index, current_estimates, table, states, arms, registry=registry, decision_time=decision_time,
                levels=levels, base=current, sizes=sizes, iorb=iorb,
            )
            today.update(mine)
        except smr.InsufficientHistory:
            skipped.append(day)
            continue
        except LookAheadError:
            raise  # a guard trip is never "no public row yet"
        except SplitError:
            if current is not None:
                raise
            skipped.append(day)
            continue
        fit_used[day] = current.fitted_on
        detail[day] = extra
        since += 1
        for name, leads in today.items():
            forecasts[name][day] = leads
    return Walk(forecasts, fit_used, fits, estimates, detail, tuple(skipped))
