"""(s3c-carry): (s3c) with a month-end carryover term sized to the spike, on business days 1 and 2 of the month (#1275; H5 step 3).

Eleonora, 27 October 2026 (chat, relayed; ledger item 67 on #1116): queue four arms on (s3c), one of them the carryover sized to the
spike. (s3c) is (s3) of #1145 (`repo_model.spread_mr_state_calendar`, arm `sc_s3_robust`: calendar terms in standardised units, Huber
fit, ridge 5) with its quantiles clipped at the SRF line from full allotment (`repo_model.s3c_candidate`). This module adds one term to
(s3)'s fit and leaves every other term, the fit and the cap as they are; `post_month_end_window` stays and the new term sits beside it.

**The term.** On a target row that is business day 1 or 2 of its month (`derived_features.bday_of_month`, the position `post_month_end_window` counts),
the column is `DECAY[bday] * spike`, with `DECAY = {1: 1.0, 2: 0.5}` (declared before any score, not tuned), and 0 on every other row.
The spike is `max(0, spread[E] - level[E])` in bp: `E` is the last panel row of the month before the target's, `spread[E]` its
SOFR - IORB, and `level[E]` the model's level there (`spread_mean_reversion.ordinary_levels`: the median of the last 10 ordinary days at or
before `E`). In the fit the column is divided by the scale at the pair's origin, as the target is, so its coefficient is a carryover
fraction and its effect in bp is `coefficient * DECAY * spike`; a forecast adds exactly that to every quantile, beside the shift and the
pool of the fit. It enters a lead's fit when at least `MIN_FLAGGED` training pairs have a positive column, and the intercept is dropped
(the pool keeps the ordinary-day centre), as the flag terms do.

**Information set.** The spread of `E` is read only if it was public at the decision instant, that is, if `E` is at or before the
decision's anchor (the last public row, `protocol_benchmarks._anchor`); a training pair reads it only if `E` is at or before the pair's
own origin, the anchor of the decision it stands for. When it was not, the column is 0, not a stale month-end: no earlier spike is read
in its place. `spike` raises `LookAheadError` for a row after the anchor, so a caller that skips the availability rule fails loudly. On
the panel's dating (SOFR of a day is public the next morning, so the anchor is the day before the decision day) the column can be non-zero
only where `E` is at or before the decision day less one, which is business day 2 at lead 1; the pages say so.

**Direct pairs.** The column is a function of the target row's own date and of rows at or before the anchor, so a training pair reads it at
its target row (`training_pairs="direct"`); `fit_carry_terms` is decorated with `one_step_guard.guard_one_step_fit`, with no allow-list
entry. It fits nothing else: where the column is not active the estimate is `spread_mr_state_calendar.fit_state_terms`' on the same pairs,
element for element.

Stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from . import derived_features
from . import protocol_benchmarks as pb
from . import spread_mean_reversion as smr
from . import spread_mr_calendar as cal
from . import spread_mr_fhs as fhs
from . import spread_mr_state_calendar as sc
from .data import DailyObservation
from .evaluation_splits import SplitDeclaration
from .one_step_guard import guard_one_step_fit
from .scoring_protocol import HORIZONS, ProtocolError
from .splits import LookAheadError, SplitError

__all__ = [
    "ARM", "CARRY", "DECAY", "CarryEstimate", "CarryWalk", "business_day", "carry_value", "fit_carry_terms", "forecast_leads", "month_end_row", "spike_bp", "walk",
]

#: The name of the term in `StateEstimate.flagged`.
CARRY = "carry"
#: The decay on business day 1 and 2 of the month, declared before any score and not tuned.
DECAY: Mapping[int, float] = {1: 1.0, 2: 0.5}
#: (s3)'s arm, whose terms, fit and ridge the new term joins.
ARM = sc.ARMS[2]


def business_day(day: date) -> int:
    """The market business day of the month of `day`: 1 for the first weekday that is not in the market holiday table
    (`derived_features.bday_of_month`, the position `post_month_end_window` counts)."""

    return int(derived_features.bday_of_month(day))


def month_end_row(dates: Sequence[date], row: int) -> Optional[int]:
    """The last panel row of the month before the month of `row`, or `None` when the panel has no earlier month."""

    month = (dates[row].year, dates[row].month)
    first = row
    while first - 1 >= 0 and (dates[first - 1].year, dates[first - 1].month) == month:
        first -= 1
    return first - 1 if first >= 1 else None


def spike_bp(
    panel: Sequence[DailyObservation], levels: Sequence[Optional[float]], row: int, anchor: int
) -> float:
    """The spike of the month-end row `row` in bp, `max(0, SOFR - IORB - level)`, as read by a decision whose last public row is `anchor`.

    0 where the level is not yet defined (fewer than `LEVEL_DAYS` ordinary days).

    Raises:
        LookAheadError: `row` is after `anchor`: its spread is not public at the decision instant.

    Mutation record: see `tests/test_s3c_carry.py` (`spike_bp`).
    """

    pb._require_public([row], anchor, [r.date for r in panel], "the month-end spike")
    level = levels[row]
    if level is None:
        return 0.0
    return max(0.0, panel[row].spread_bps - level)


def carry_value(
    panel: Sequence[DailyObservation], levels: Sequence[Optional[float]], row: int, anchor: int
) -> float:
    """The column of the term at target row `row` for a decision whose last public row is `anchor`, in bp.

    `DECAY[bday] * spike` on business day 1 or 2; 0 on any other row, where there is no earlier month, where the month-end spread was not
    public at the decision (`E` after `anchor`), or where the level is not defined.

    Mutation record: see `tests/test_s3c_carry.py` (`carry_value`).
    """

    dates = [r.date for r in panel]
    decay = DECAY.get(business_day(dates[row]), 0.0)
    if decay == 0.0:
        return 0.0
    end = month_end_row(dates, row)
    if end is None or end > anchor:
        return 0.0
    return decay * spike_bp(panel, levels, end, anchor)


@dataclass(frozen=True)
class CarryEstimate:
    """One lead's estimate: (s3)'s kind of estimate (`state`, whose pool is the pool after the carry term too) and the carry coefficient.

    `coefficient` is 0 and `active` False where the term did not enter; `state` is then what `fit_state_terms` returns on the same pairs.
    """

    state: sc.StateEstimate
    coefficient: float
    active: bool
    #: Training pairs whose carry column is positive.
    carry_pairs: int


@guard_one_step_fit
def fit_carry_terms(
    pairs: Sequence[sc.StatePair],
    carry: Sequence[float],
    *,
    regressors: Sequence[str],
    terms: Sequence[str],
    training_pairs: str,
    min_flagged: int = sc.MIN_FLAGGED,
    ridge: float = sc.ROBUST_RIDGE,
    baseline: Optional[sc.StateEstimate] = None,
) -> CarryEstimate:
    """(s3)'s Huber fit of one lead with the carry column added, in standardised units.

    `carry[i]` is the column of pair `i` in bp (`carry_value` at its target row, read as of its origin); the fit divides it by the pair's
    scale. The term enters when at least `min_flagged` pairs have a positive column; otherwise the estimate is
    `fit_state_terms`' (or `baseline`, the same call made by the caller, which must have been made on these pairs).

    Raises:
        ValueError: `training_pairs` is not `'direct'`, or one carry value per pair is not given.
        InsufficientHistory: there is no pair.
    """

    if training_pairs != "direct":
        raise ValueError(f"fit_carry_terms trains on direct pairs only, got training_pairs={training_pairs!r}")
    if len(carry) != len(pairs):
        raise ValueError("fit_carry_terms needs one carry value per pair")
    count = sum(1 for x in carry if x > 0.0)
    if count < min_flagged:
        base = baseline or sc.fit_state_terms(
            pairs, regressors=regressors, terms=terms, interact=False, robust=True, training_pairs="direct", ridge=ridge)
        return CarryEstimate(base, 0.0, False, count)
    active, counts = sc._entering(terms, pairs, min_flagged)
    target = [p.raw / p.scale for p in pairs]
    column = [x / p.scale for x, p in zip(carry, pairs)]
    design = [[1.0] + [float(p.flags[name]) for name in active] + [x] for p, x in zip(pairs, column)]
    coefficients, iterations = sc.huber(design, target, ridge)
    effect = dict(zip(active, coefficients[1 : 1 + len(active)]))
    coefficient = coefficients[-1]
    pool = [
        y - sum(effect[name] * float(p.flags[name]) for name in effect) - coefficient * x
        for p, y, x in zip(pairs, target, column)
    ]
    counts[CARRY] = count
    state = sc.StateEstimate(
        active, effect, {}, counts, tuple(pb.empirical_quantiles(sorted(pool))), len(pairs), sum(1 for p in pairs if p.state is None),
        iterations, False, tuple(p.origin for p in pairs), tuple(p.target for p in pairs), tuple(pool), 0,
    )
    return CarryEstimate(state, coefficient, True, count)


def forecast_leads(
    estimates: Mapping[int, CarryEstimate],
    quantiles: Mapping[int, Sequence[float]],
    values: Mapping[int, float],
) -> Dict[int, List[float]]:
    """Each lead's quantiles with the carry effect added: `quantiles` are `sc.forecast`'s from the estimates' `state`, `values` the leads'
    `carry_value`s. The effect is `coefficient * value` in bp, added to every quantile (0 where the term is not active)."""

    return {h: [q + estimates[h].coefficient * values[h] for q in quantiles[h]] for h in quantiles}


# -- the walk ---------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class CarryWalk:
    #: Decision day -> lead -> 23 quantiles of (s3-carry) (before the SRF cap), and (s3)'s own, from the same walk.
    forecasts: Dict[date, Dict[int, List[float]]]
    s3: Dict[date, Dict[int, List[float]]]
    #: Decision day -> lead -> the carry column read (bp).
    values: Dict[date, Dict[int, float]]
    #: Refit day -> lead -> the estimate.
    estimates: Dict[date, Dict[int, CarryEstimate]]
    #: Decision day -> the refit day whose estimates it used.
    fit_used: Dict[date, date]
    skipped: Tuple[date, ...]


def refit(
    panel: Sequence[DailyObservation],
    decision_index: int,
    table: cal.TermTable,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    levels: Sequence[Optional[float]],
    base: smr.Fit,
    training_pairs: str = "direct",
) -> Tuple[Dict[int, CarryEstimate], Dict[int, sc.StateEstimate]]:
    """The carry arm's estimate at each lead, and (s3)'s, as of the decision on row `decision_index`, on the base model's training pairs.

    Mirrors `spread_mr_state_calendar.refit` for (s3) (the same pairs, the same scale, the same terms) and reads the carry column at each
    pair's target row as of its origin.

    Raises:
        InsufficientHistory: the base fit's, or a lead with no pair that has a scale.
        LookAheadError: a row the scale or the spike reads is after the anchor.
        ValueError: the one-step guard (`fit_carry_terms`).
    """

    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    lag = decision_index - anchor
    rows = smr.training_rows(panel, decision_index, anchor, lag=lag, levels=levels)
    dates = [row.date for row in panel]
    spreads = [row.spread_bps for row in panel[: anchor + 1]]
    origins = sorted({origin for h in HORIZONS for origin, _ in rows[h]} | {anchor})
    variant = sc.BASE_VARIANT
    read = {j for origin in origins if origin - variant.window >= 0 for j in fhs.scale_rows(origin, variant.window)}
    pb._require_public(read, anchor, dates, f"the scale of {variant.name} for {dates[decision_index]}")
    reader = fhs.ScaleReader(spreads, variant)
    mine: Dict[int, CarryEstimate] = {}
    s3: Dict[int, sc.StateEstimate] = {}
    for h in HORIZONS:
        k = h + lag
        pairs: List[sc.StatePair] = []
        carry: List[float] = []
        for origin, target in rows[h]:
            scale = reader.at(origin)
            if scale is None:
                continue
            raw = (spreads[target] - levels[origin]) - base.phi**k * (spreads[origin] - levels[origin])
            flags_row = target if training_pairs == "direct" else origin
            pairs.append(sc.StatePair(raw, scale, table.flags_at(h, flags_row), None, {}, origin, target, {}, False))
            carry.append(carry_value(panel, levels, target, origin))
        if not pairs:
            raise smr.InsufficientHistory(f"{dates[decision_index]}: no training pair of lead {h} has a scale")
        regressors = cal.regressors_of(ARM, h)
        s3[h] = sc.fit_state_terms(
            pairs, regressors=regressors, terms=ARM.location, interact=False, robust=True, training_pairs=training_pairs,
            ridge=ARM.ridge)
        mine[h] = fit_carry_terms(
            pairs, carry, regressors=regressors, terms=ARM.location, training_pairs=training_pairs, baseline=s3[h])
    return mine, s3


def walk(
    panel: Sequence[DailyObservation],
    decision_days: Iterable[date],
    table: cal.TermTable,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    refit_every: int = smr.REFIT_EVERY,
    training_pairs: str = "direct",
) -> CarryWalk:
    """(s3) and (s3-carry) on `decision_days`, refitting as `spread_mr_state_calendar.walk` does (a day with no forecast is skipped and
    does not count toward the next refit), so that (s3) here is that walk's (s3) forecast for forecast.

    The carry column of a forecast is read at the target row as of the decision's anchor.
    """

    if refit_every < 1:
        raise ValueError(f"refit_every must be at least 1, got {refit_every}")
    position = {row.date: index for index, row in enumerate(panel)}
    levels = smr.ordinary_levels(panel, splits)
    settings = dict(registry=registry, decision_time=decision_time, splits=splits, levels=levels)
    forecasts: Dict[date, Dict[int, List[float]]] = {}
    s3_out: Dict[date, Dict[int, List[float]]] = {}
    values: Dict[date, Dict[int, float]] = {}
    estimates: Dict[date, Dict[int, CarryEstimate]] = {}
    fit_used: Dict[date, date] = {}
    skipped: List[date] = []
    current: Optional[smr.Fit] = None
    mine_now: Dict[int, CarryEstimate] = {}
    s3_now: Dict[int, sc.StateEstimate] = {}
    refit_day: Optional[date] = None
    since = 0
    for day in decision_days:
        if day not in position:
            raise ProtocolError(f"decision day {day} is not a panel day")
        index = position[day]
        try:
            if current is None or since >= refit_every:
                base = smr.fit(panel, index, **settings)
                fhs.fit(panel, index, [sc.BASE_VARIANT], base=base, **settings)  # the walk's own refit can skip the day: so does this
                mine_now, s3_now = refit(
                    panel, index, table, registry=registry, decision_time=decision_time, levels=levels, base=base,
                    training_pairs=training_pairs)
                current, refit_day = base, day
                estimates[day] = mine_now
                since = 0
            anchor = pb._anchor(panel, index, registry, decision_time)
            read = {h: carry_value(panel, levels, index + h, anchor) for h in HORIZONS}
            fcfg = dict(registry=registry, decision_time=decision_time, levels=levels, base=current)
            theirs, _ = sc.forecast(
                panel, index, {ARM.name: s3_now}, table, {}, (ARM,), **fcfg)
            ours, _ = sc.forecast(
                panel, index, {ARM.name: {h: e.state for h, e in mine_now.items()}}, table, {}, (ARM,), **fcfg)
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
        fit_used[day] = refit_day
        since += 1
        s3_out[day] = theirs[ARM.name]
        forecasts[day] = forecast_leads(mine_now, ours[ARM.name], read)
        values[day] = read
    return CarryWalk(forecasts, s3_out, values, estimates, fit_used, tuple(skipped))
