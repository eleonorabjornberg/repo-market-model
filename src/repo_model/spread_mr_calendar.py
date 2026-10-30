"""Calendar and FOMC effects as additive terms on volatility-scaled mean reversion, read at the target day (#1115; H5 step 3).

`metadata/calendar_mr_1115.json` is the declaration; this module is its arithmetic. The base is `repo_model.spread_mr_fhs`'s
declared variant `spread_mr_fhs_mad20_f0.5` (#941), unchanged: `level + phi^k (last - level) + scale(anchor) * z_h`, with `z_h`
the quantiles of the raw residuals divided by the scale at each pair's own origin. Three arms add declared terms to it:

* (b) additive terms in the conditional location;
* (c) the same terms, and additive terms in the scale;
* (d) arm (c) without the FOMC and IORB terms.

**A term** is a 0/1 flag of the *target* row: month-end, quarter-end, tax date, a coupon or bill settlement (lead 1 only), the
19th to 23rd of the month, the IORB-change window (the day the change takes effect and the two panel days after it) and an FOMC
meeting day. Its effect is estimated per lead by ridge least squares on the base model's direct pairs, jointly with the other
terms, and re-estimated at every refit; a pair's flags are read from its own target row, the row they are served from (`asof`
rule 2), never from its origin.

**Read at the target day.** The columns come from `target_day_columns.TARGET_DAY_COLUMNS` or are declared scheduled fields, or a
function of the target row's own date (`dom_19_23`). A scheduled field of the row `r` is public at the decision instant only if
the panel day before `r` is at or before the decision day; `readable_offsets` and `TermTable.read` apply that rule, and
`require_public` raises `LookAheadError` otherwise (a settlement at lead 2 or more; the IORB window's day of change at lead 2 or
more). `fit_calendar_terms` is decorated with `one_step_guard.guard_one_step_fit`: on direct pairs it needs no allow-list entry; a
one-step fit of the same columns raises `ValueError`.

Stdlib only.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, time
from typing import Dict, Iterable, List, Mapping, NamedTuple, Optional, Sequence, Tuple

from .decision_instant import DECISION_TIME
from . import announced_iorb, derived_features, fomc_calendar
from . import protocol_benchmarks as pb
from . import spread_mean_reversion as smr
from . import spread_mr_fhs as fhs
from .data import DailyObservation, in_last_business_days_of_month
from .evaluation_splits import SplitDeclaration
from .one_step_guard import guard_one_step_fit
from .scoring_protocol import HORIZONS, ProtocolError
from .splits import LookAheadError, SplitError

#: The L2 penalty on every term coefficient, in pseudo-days (none on the intercept).
RIDGE = 1.0
#: A term enters a lead's fit only if this many training pairs carry its flag.
MIN_FLAGGED = 3
#: The floor of a row's scale multiplier.
M_MIN = 0.25
#: The base: #941's declared variant.
BASE_VARIANT = fhs.VARIANTS[0]
TRAINING_PAIRS = ("direct", "one_step")


@dataclass(frozen=True)
class Term:
    """One declared term: its name, the panel columns it reads, whether the field is scheduled, and the rows it reads.

    `span` are the offsets `j` such that the flag of target row `T` reads row `T - j` (0 for a flag of the row itself; the IORB
    window reads the day of the change and the two rows after it, so `(0, 1, 2)`).
    """

    name: str
    reads: Tuple[str, ...]
    scheduled: bool
    span: Tuple[int, ...]


TERMS: Tuple[Term, ...] = (
    Term("month_end", ("days_to_month_end",), False, (0,)),
    Term("quarter_end", ("quarter_end",), False, (0,)),
    Term("tax_date", ("tax_date",), False, (0,)),
    Term("settlement_coupon", ("treasury_settlement_coupons",), True, (0,)),
    Term("settlement_bill", ("treasury_settlement_bills",), True, (0,)),
    Term("dom_19_23", (), False, (0,)),
    Term("iorb_window", ("iorb_announced_change_bps",), True, (0, 1, 2)),
    Term("fomc_day", ("fomc_meeting_day",), False, (0,)),
    Term("post_month_end_window", (), False, (0,)),
)
TERM = {term.name: term for term in TERMS}
ALL_TERMS: Tuple[str, ...] = tuple(term.name for term in TERMS)
NO_FOMC_IORB: Tuple[str, ...] = tuple(name for name in ALL_TERMS if name not in ("iorb_window", "fomc_day"))


@dataclass(frozen=True)
class Arm:
    name: str
    role: str
    location: Tuple[str, ...]
    scale: Tuple[str, ...]


ARM_A = "mr_cal_a_base"
ARMS: Tuple[Arm, ...] = (
    Arm("mr_cal_b_location", "(b) base plus location terms", ALL_TERMS, ()),
    Arm("mr_cal_c_location_scale", "(c) base plus location and scale terms", ALL_TERMS, ALL_TERMS),
    Arm("mr_cal_d_no_fomc_iorb", "(d) arm (c) without the FOMC and IORB terms", NO_FOMC_IORB, NO_FOMC_IORB),
)
ARM_NAMES: Tuple[str, ...] = (ARM_A,) + tuple(arm.name for arm in ARMS)


# -- what a decision can read ---------------------------------------------------------------------------------------------


def readable_offsets(term: Term, lead: int) -> Tuple[int, ...]:
    """The offsets `j` of `term.span` the decision `lead` rows before the target can read.

    A calendar column or a function of the date is known whenever it is read. A scheduled field of row `r` is public at 15:00 or
    18:00 (the decision instant, `repo_model.decision_instant`) on the panel day before `r` (`metadata/sources.json`, `scheduled_availability`), so a decision on row `T - lead` reads
    row `r = T - j` only if `r - 1 <= T - lead`, that is `j >= lead - 1`.

    Mutation record: see `tests/test_spread_mr_calendar.py` (`readable_offsets`).
    """

    return tuple(j for j in term.span if not term.scheduled or j >= lead - 1)


def available(term: Term, lead: int) -> bool:
    return bool(readable_offsets(term, lead))


def target_row(decision_index: int, lead: int) -> int:
    """The row a lead-`lead` forecast of the decision on row `decision_index` is about: the one every term is read from.

    Mutation record: see `tests/test_spread_mr_calendar.py` (`target_row`).
    """

    return decision_index + lead


def require_public(term: Term, rows: Iterable[int], decision_index: int, dates: Sequence[date]) -> None:
    """Every row a scheduled `term` reads is public at the decision on row `decision_index`.

    Raises:
        LookAheadError: a scheduled field of a row whose publication instant (the panel day before it) is after the decision day.
    """

    if not term.scheduled:
        return
    for row in sorted(rows):
        if row - 1 > decision_index:
            raise LookAheadError(
                f"term {term.name!r} reads {', '.join(term.reads)} of {dates[row]}, public only on {dates[row - 1]}, "
                f"after the decision day {dates[decision_index]}"
            )


class TermTable:
    """Every term's flag at every row, at each lead: the target row's own columns, read as of the decision `lead` rows before."""

    def __init__(
        self,
        panel: Sequence[DailyObservation],
        announcements: Sequence[announced_iorb.IorbAnnouncement],
        calendar: Optional[Sequence[fomc_calendar.Meeting]] = None,
        *,
        decision_time: time = DECISION_TIME,
    ):
        self.dates = [row.date for row in panel]
        n = len(panel)

        def column(name: str) -> List[float]:
            return [float(row.values.get(name) or 0.0) for row in panel]

        base = {
            # the month's last two business days on the market calendar: the reporting day type's definition (a calendar column
            # `days_to_month_end` counts calendar days and is 0 only when the month ends on a weekday)
            "month_end": [1 if in_last_business_days_of_month(row.date) else 0 for row in panel],
            "quarter_end": [1 if value > 0 else 0 for value in column("quarter_end")],
            "tax_date": [1 if value > 0 else 0 for value in column("tax_date")],
            "settlement_coupon": [1 if value > 0 else 0 for value in column("treasury_settlement_coupons")],
            "settlement_bill": [1 if value > 0 else 0 for value in column("treasury_settlement_bills")],
            "dom_19_23": [1 if 19 <= day.day <= 23 else 0 for day in self.dates],
            "post_month_end_window": [1 if derived_features.bday_of_month(day) <= 3 else 0 for day in self.dates],
        }
        changes = [
            0.0 if values[announced_iorb.ANNOUNCED_CHANGE] is None else values[announced_iorb.ANNOUNCED_CHANGE]
            for values in announced_iorb.announced_iorb_features(self.dates, announcements, decision_time=decision_time)
        ]
        meetings = fomc_calendar.load_calendar() if calendar is None else calendar
        self._flags: Dict[Tuple[str, int], List[Optional[int]]] = {}
        for lead in HORIZONS:
            fomc = fomc_calendar.add_columns(panel, meetings, horizon=lead, decision_time=decision_time)
            for term in TERMS:
                offsets = readable_offsets(term, lead)
                if not offsets:
                    self._flags[(term.name, lead)] = [None] * n
                elif term.name == "iorb_window":
                    self._flags[(term.name, lead)] = [
                        1 if any(row - j >= 0 and changes[row - j] != 0.0 for j in offsets) else 0 for row in range(n)
                    ]
                elif term.name == "fomc_day":
                    self._flags[(term.name, lead)] = [1 if row.values["fomc_meeting_day"] else 0 for row in fomc]
                else:
                    self._flags[(term.name, lead)] = list(base[term.name])

    def flag(self, term: str, lead: int, row: int) -> Optional[int]:
        """The flag of `term` at target row `row` for a lead-`lead` decision; `None` where the term is not readable at that lead."""

        return self._flags[(term, lead)][row]

    def flags_at(self, lead: int, row: int) -> Dict[str, int]:
        """The flags of the terms readable at `lead`, at row `row` (a training row: public by construction)."""

        return {t.name: self._flags[(t.name, lead)][row] for t in TERMS if available(t, lead)}

    def read(self, lead: int, decision_index: int) -> Dict[str, int]:
        """The flags a forecast of the decision on row `decision_index` at `lead` reads, from the target row.

        Raises:
            LookAheadError: a scheduled field of a row that is not public at the decision (`require_public`).
        """

        row = target_row(decision_index, lead)
        out = {}
        for term in TERMS:
            offsets = readable_offsets(term, lead)
            if not offsets:
                continue
            require_public(term, [row - j for j in offsets], decision_index, self.dates)
            out[term.name] = self._flags[(term.name, lead)][row]
        return out

    def day_types(self, row: int) -> Dict[str, int]:
        """Every term's flag at `row` as the best-informed reading allows (lead 1), for grouping a scored day by its type."""

        return {t.name: (self._flags[(t.name, 1)][row] or 0) for t in TERMS}


# -- the estimation ---------------------------------------------------------------------------------------------------------


class PairRow(NamedTuple):
    """One training pair: its raw residual (bp), the scale at its origin, and the flags of the readable terms."""

    raw: float
    scale: float
    flags: Mapping[str, int]


def solve_ridge(rows: Sequence[Sequence[float]], y: Sequence[float], ridge: float) -> List[float]:
    """The coefficients of `y` on `rows` (the first column is the intercept) by least squares with an L2 penalty `ridge` on every
    other coefficient.

    Raises:
        ValueError: no rows, ragged rows, or a singular system.
    """

    if not rows or len(rows) != len(y):
        raise ValueError("solve_ridge needs as many targets as rows, and at least one")
    p = len(rows[0])
    if any(len(r) != p for r in rows):
        raise ValueError("the rows of the design differ in length")
    a = [[0.0] * (p + 1) for _ in range(p)]
    for r, target in zip(rows, y):
        for i in range(p):
            ri = r[i]
            if ri == 0.0:
                continue
            for j in range(p):
                a[i][j] += ri * r[j]
            a[i][p] += ri * target
    for i in range(1, p):
        a[i][i] += ridge
    for col in range(p):
        pivot = max(range(col, p), key=lambda i: abs(a[i][col]))
        if abs(a[pivot][col]) < 1e-12:
            raise ValueError("the normal equations are singular")
        a[col], a[pivot] = a[pivot], a[col]
        for i in range(col + 1, p):
            factor = a[i][col] / a[col][col]
            if factor:
                for j in range(col, p + 1):
                    a[i][j] -= factor * a[col][j]
    out = [0.0] * p
    for i in range(p - 1, -1, -1):
        out[i] = (a[i][p] - sum(a[i][j] * out[j] for j in range(i + 1, p))) / a[i][i]
    return out


@dataclass(frozen=True)
class LeadEstimate:
    """What a refit keeps for one arm and lead: the location effects (bp), the scale uplifts, the pool and the counts."""

    location: Tuple[str, ...]
    scale_terms: Tuple[str, ...]
    effect: Mapping[str, float]
    uplift: Mapping[str, float]
    flagged: Mapping[str, int]
    pool: Sequence[float]
    pairs: int
    c0: Optional[float]


def multiplier(estimate: LeadEstimate, flags: Mapping[str, int]) -> float:
    """The scale multiplier of a row: `max(M_MIN, 1 + sum_j g_j x_j)`; 1 where the arm has no scale term."""

    if not estimate.uplift:
        return 1.0
    return max(M_MIN, 1.0 + sum(g * flags[name] for name, g in estimate.uplift.items()))


def _entering(names: Sequence[str], pairs: Sequence[PairRow], min_flagged: int) -> Tuple[Tuple[str, ...], Dict[str, int]]:
    counts = {name: sum(p.flags[name] for p in pairs) for name in names if pairs and name in pairs[0].flags}
    return tuple(n for n in ALL_TERMS if n in counts and counts[n] >= min_flagged), counts


@guard_one_step_fit
def fit_calendar_terms(
    pairs: Sequence[PairRow],
    *,
    regressors: Sequence[str],
    location: Sequence[str],
    scale_terms: Sequence[str],
    training_pairs: str,
    ridge: float = RIDGE,
    min_flagged: int = MIN_FLAGGED,
) -> LeadEstimate:
    """The term effects and the standardised pool of one arm at one lead.

    `regressors` are the panel columns the terms read (for `one_step_guard`). `training_pairs` is required: `'direct'`, the
    flags of each pair read from its own target row, is the only value this fit trains on. The guard decorates this function:
    `'one_step'` with a calendar or scheduled regressor raises `ValueError` from it, and nothing is allow-listed.

    The location effects are the ridge least-squares coefficients of the raw residual on the entering terms (the intercept is
    dropped, so the pool keeps the ordinary-day centre). The pool is `(raw - sum beta_j x_j) / scale(origin)`, divided by the
    row's multiplier where the arm has scale terms (the ridge fit of `|e|` on the same flags gives `g_j = gamma_j / c0`).

    Raises:
        ValueError: `training_pairs` is not `'direct'`, or there is no pair.
    """

    if training_pairs != "direct":
        raise ValueError(f"fit_calendar_terms trains on direct pairs only, got training_pairs={training_pairs!r}")
    if not pairs:
        raise smr.InsufficientHistory("no training pair to estimate the calendar terms on")
    active, counts = _entering(location, pairs, min_flagged)
    effect: Dict[str, float] = {}
    if active:
        design = [[1.0] + [float(p.flags[name]) for name in active] for p in pairs]
        beta = solve_ridge(design, [p.raw for p in pairs], ridge)
        effect = dict(zip(active, beta[1:]))
    adjusted = [(p.raw - sum(effect[name] * p.flags[name] for name in effect)) / p.scale for p in pairs]
    uplift: Dict[str, float] = {}
    c0: Optional[float] = None
    scale_active, scale_counts = _entering(scale_terms, pairs, min_flagged) if scale_terms else ((), {})
    counts.update(scale_counts)
    if scale_active:
        design = [[1.0] + [float(p.flags[name]) for name in scale_active] for p in pairs]
        coefficients = solve_ridge(design, [abs(e) for e in adjusted], ridge)
        c0 = coefficients[0]
        uplift = {name: (g / c0 if c0 > 0.0 else 0.0) for name, g in zip(scale_active, coefficients[1:])}
    estimate = LeadEstimate(tuple(active), tuple(scale_active), effect, uplift, counts, (), len(pairs), c0)
    pool = [e / multiplier(estimate, p.flags) for e, p in zip(adjusted, pairs)]
    return LeadEstimate(
        estimate.location, estimate.scale_terms, effect, uplift, counts, pb.empirical_quantiles(sorted(pool)), len(pairs), c0
    )


def lead_quantiles(estimate: LeadEstimate, *, centre: float, scale: float, flags: Mapping[str, int]) -> List[float]:
    """The 23 quantiles: `centre + sum beta_j x_j + scale * m * pool`, the order of the pool kept."""

    shift = sum(effect * flags[name] for name, effect in estimate.effect.items())
    spread = scale * multiplier(estimate, flags)
    return [centre + shift + spread * value for value in estimate.pool]


def regressors_of(arm: Arm, lead: int) -> Tuple[str, ...]:
    """The panel columns the terms of `arm` read at `lead`, for the one-step guard."""

    names = []
    for name in ALL_TERMS:
        if (name in arm.location or name in arm.scale) and available(TERM[name], lead):
            names.extend(c for c in TERM[name].reads if c not in names)
    return tuple(names)


# -- the walk ---------------------------------------------------------------------------------------------------------------


def refit(
    panel: Sequence[DailyObservation],
    decision_index: int,
    table: TermTable,
    arms: Sequence[Arm],
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    levels: Sequence[Optional[float]],
    base: smr.Fit,
    training_pairs: str = "direct",
) -> Dict[str, Dict[int, LeadEstimate]]:
    """Each arm's estimate at each lead as of the decision on row `decision_index`, on the base model's training pairs.

    A pair's flags are read at its target row on direct pairs (`training_pairs='direct'`); `'one_step'` reads the origin row's,
    the class `one_step_guard` refuses.

    Raises:
        InsufficientHistory: the base fit's, or a lead with no pair that has a scale.
        LookAheadError: a row the scale reads is after the anchor.
        ValueError: the one-step guard (`fit_calendar_terms`).
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
    out: Dict[str, Dict[int, LeadEstimate]] = {}
    for arm in arms:
        per_lead: Dict[int, LeadEstimate] = {}
        for h in HORIZONS:
            k = h + lag
            pairs = []
            for origin, target in rows[h]:
                scale = reader.at(origin)
                if scale is None:
                    continue
                raw = (spreads[target] - levels[origin]) - base.phi**k * (spreads[origin] - levels[origin])
                flags_row = target if training_pairs == "direct" else origin
                pairs.append(PairRow(raw, scale, table.flags_at(h, flags_row)))
            if not pairs:
                raise smr.InsufficientHistory(f"{dates[decision_index]}: no training pair of lead {h} has a scale")
            per_lead[h] = fit_calendar_terms(
                pairs, regressors=regressors_of(arm, h), location=arm.location, scale_terms=arm.scale,
                training_pairs=training_pairs,
            )
        out[arm.name] = per_lead
    return out


def forecast(
    panel: Sequence[DailyObservation],
    decision_index: int,
    estimates: Mapping[str, Mapping[int, LeadEstimate]],
    table: TermTable,
    arms: Sequence[Arm],
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    levels: Sequence[Optional[float]],
    base: smr.Fit,
) -> Dict[str, Dict[int, List[float]]]:
    """The arms' forecasts of the decision day from `estimates` (possibly an older fit): `last`, `level`, `k`, the scale at the
    anchor and the flags of each target row are read afresh.

    Raises:
        InsufficientHistory: the anchor has no level or no scale.
        LookAheadError: a row the scale at the anchor reads, or a scheduled field of a target row, is not public.
    """

    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    level = levels[anchor]
    if level is None:
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
    lag = decision_index - anchor
    last = panel[anchor].spread_bps
    out: Dict[str, Dict[int, List[float]]] = {arm.name: {} for arm in arms}
    for h in HORIZONS:
        flags = table.read(h, decision_index)
        centre = level + base.phi ** (h + lag) * (last - level)
        for arm in arms:
            out[arm.name][h] = lead_quantiles(estimates[arm.name][h], centre=centre, scale=scale, flags=flags)
    return out


@dataclass(frozen=True)
class Walk:
    #: Arm name -> decision day -> lead -> 23 quantiles; `ARM_A` is #941's variant, forecast by `spread_mr_fhs`.
    forecasts: Dict[str, Dict[date, Dict[int, List[float]]]]
    fit_used: Dict[date, date]
    #: Refit day -> the base fit.
    fits: Dict[date, smr.Fit]
    #: Refit day -> arm name -> lead -> the estimate.
    estimates: Dict[date, Dict[str, Dict[int, LeadEstimate]]]
    skipped: Tuple[date, ...]


def walk(
    panel: Sequence[DailyObservation],
    decision_days: Iterable[date],
    table: TermTable,
    arms: Sequence[Arm] = ARMS,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    refit_every: int = smr.REFIT_EVERY,
    training_pairs: str = "direct",
) -> Walk:
    """Arm (a) and `arms` on `decision_days`, refitting as `spread_mr_fhs.walk` does (the base fit and #941's pool, then the terms).

    A day on which any arm has no forecast is skipped for all, so the arms are compared on the same days.
    """

    if refit_every < 1:
        raise ValueError(f"refit_every must be at least 1, got {refit_every}")
    position = {row.date: index for index, row in enumerate(panel)}
    levels = smr.ordinary_levels(panel, splits)
    settings = dict(registry=registry, decision_time=decision_time, splits=splits, levels=levels)
    forecasts: Dict[str, Dict[date, Dict[int, List[float]]]] = {ARM_A: {}, **{arm.name: {} for arm in arms}}
    fit_used: Dict[date, date] = {}
    fits: Dict[date, smr.Fit] = {}
    estimates: Dict[date, Dict[str, Dict[int, LeadEstimate]]] = {}
    skipped: List[date] = []
    current: Optional[smr.Fit] = None
    current_scaled: Optional[fhs.ScaledFit] = None
    current_estimates: Dict[str, Dict[int, LeadEstimate]] = {}
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
                    panel, index, table, arms, registry=registry, decision_time=decision_time, levels=levels, base=base,
                    training_pairs=training_pairs,
                )
                current, current_scaled, current_estimates = base, scaled, found
                fits[day], estimates[day] = base, found
                since = 0
            today = {ARM_A: fhs.forecast(panel, index, current_scaled, current, BASE_VARIANT, **settings)}
            today.update(
                forecast(panel, index, current_estimates, table, arms, registry=registry, decision_time=decision_time,
                         levels=levels, base=current)
            )
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
        since += 1
        for name, leads in today.items():
            forecasts[name][day] = leads
    return Walk(forecasts, fit_used, fits, estimates, tuple(skipped))
