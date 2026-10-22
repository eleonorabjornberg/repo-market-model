"""A faster-reacting scale for scaled mean reversion (#1153; H5 step 3, fix of the clustered misses, development tier).

`metadata/faster_scale_1153.json` is the declaration; this module is its arithmetic. The base is `repo_model.spread_mr_fhs`'s
declared variant `spread_mr_fhs_mad20_f0.5` (#941, arm (a) of #1115), unchanged: `level + phi^k (last - level) + scale(anchor) * z_h`,
with `z_h` the quantiles of the raw residuals divided by the scale at each pair's own origin. Filtered historical simulation
stays; an arm changes only the scale, or what multiplies it:

* (v1) a faster robust scale: the MAD over 5 days, over 10 days, and the mean of the 5- and 20-day MAD scales;
* (v2) an EWMA of the absolute daily spread changes, rescaled to a standard deviation (half-lives 3, 5 and 10 rows), and an
  asymmetric version in which an upward change weighs `1 + ASYM` and a downward one `1 - ASYM`;
* (v3) miss feedback: after the anchor row was outside the 90% band the model gave it, the scale is multiplied by a factor fitted at
  each refit (the ratio of the median absolute standardised residual of pairs whose origin followed a miss to that of pairs
  whose origin did not, never below 1), and the pool is the residuals of pairs that did not follow a miss;
* (v4) one of the above plus a factor on the scale read at the target day's calendar type (quarter-end, tax date, month-end turn,
  coupon settlement), fitted per lead on the direct pairs.

**As-of.** The scale at a row reads `scale_rows(row, scale)`, all at or before the row; `fit` and `forecast` require every row read,
for each origin and for the anchor, to be public at the decision instant (`protocol_benchmarks._require_public` raises
`LookAheadError` otherwise). Yesterday's miss is the anchor row's: its band is the model's own one-lead band, centred on the
row `1 + lag` before it and scaled by the scale there, and it reads no row after the anchor.

**Read at the target day.** The calendar type of a target row comes from `spread_mr_calendar.TermTable`: its columns are served
from the target row (`asof` rule 2) and a scheduled field (a coupon settlement) is read only where the as-of rule admits it (lead 1);
`fit_type_factors` is decorated with `one_step_guard.guard_one_step_fit` and trains on direct pairs only.

Stdlib only.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from datetime import date, time
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from . import protocol_benchmarks as pb
from . import spread_mean_reversion as smr
from . import spread_mr_calendar as cal
from . import spread_mr_fhs as fhs
from .data import DailyObservation
from .evaluation_splits import SplitDeclaration
from .one_step_guard import guard_one_step_fit
from .scoring_protocol import GRID, HORIZONS, ProtocolError
from .splits import LookAheadError, SplitError

MAD_CONSTANT = fhs.MAD_CONSTANT
#: The mean absolute value of a standard normal is `sqrt(2 / pi)`: this makes the EWMA of absolute changes an sd.
SQRT_HALF_PI = math.sqrt(math.pi / 2.0)
#: The floor of every scale, in bp: the base's.
FLOOR = 0.5
#: The changes an EWMA scale reads, newest first (the truncation of its geometric weights).
EWMA_ROWS = 60
#: An upward change weighs `1 + ASYM`, a downward one `1 - ASYM`, in the asymmetric EWMA.
ASYM = 0.5
#: A miss factor is fitted only if this many pairs followed a miss and as many did not.
MISS_MIN = 20
#: The 90% band whose miss is fed back, as grid levels.
BAND = (0.05, 0.95)
#: Pseudo-pairs in the shrinkage of a calendar-type factor toward 1: `1 + n / (n + CAL_K) * (ratio - 1)`.
CAL_K = 10.0
#: The calendar types, in priority order: a row carrying several is the first of them.
CAL_TYPES: Tuple[str, ...] = ("quarter_end", "tax_date", "month_end", "settlement_coupon")
KINDS: Tuple[str, ...] = ("mad", "blend", "ewma")


@dataclass(frozen=True)
class Scale:
    """One declared scale: the kind, its windows (MAD, blend) or half-life and rows (EWMA), and the floor in bp."""

    name: str
    kind: str
    windows: Tuple[int, ...] = ()
    half_life: float = 0.0
    asym: float = 0.0
    rows: int = 0
    floor: float = FLOOR

    def __post_init__(self) -> None:
        if self.kind not in KINDS:
            raise ValueError(f"the scale kind must be one of {KINDS}, got {self.kind!r}")
        if self.kind in ("mad", "blend"):
            if len(self.windows) != (1 if self.kind == "mad" else 2) or any(w < 2 for w in self.windows):
                raise ValueError(f"a {self.kind} scale needs {1 if self.kind == 'mad' else 2} window(s) of at least 2 rows, got {self.windows!r}")
        else:
            if not self.half_life > 0.0 or self.rows < 1 or not 0.0 <= self.asym < 1.0:
                raise ValueError("an ewma scale needs a positive half-life, at least one row and an asymmetry in [0, 1)")
        if not self.floor > 0.0:
            raise ValueError(f"the scale floor must be positive, got {self.floor!r}")

    @property
    def reach(self) -> int:
        """How many rows before a row its scale reads."""

        return self.rows if self.kind == "ewma" else max(self.windows)


def scale_rows(row: int, scale: Scale) -> range:
    """The panel rows the scale at `row` reads: the `reach + 1` rows ending at `row`. None is after `row`.

    Mutation record: see `tests/test_spread_mr_scale.py` (`scale_rows`).
    """

    return range(row - scale.reach, row + 1)


def _mad(spreads: Sequence[float], row: int, window: int) -> float:
    changes = [spreads[j + 1] - spreads[j] for j in range(row - window, row)]
    return MAD_CONSTANT * statistics.median(abs(c) for c in changes)


def _ewma(spreads: Sequence[float], row: int, scale: Scale) -> float:
    decay = 0.5 ** (1.0 / scale.half_life)
    numerator = denominator = 0.0
    for k in range(scale.rows):
        change = spreads[row - k] - spreads[row - k - 1]
        weight = decay**k
        side = 1.0 + scale.asym if change > 0.0 else 1.0 - scale.asym
        numerator += weight * side * abs(change)
        denominator += weight
    return SQRT_HALF_PI * numerator / denominator


class ScaleSeries:
    """The scale of one kind at the rows of a spread series; a row reads only `scale_rows`."""

    def __init__(self, spreads: Sequence[float], scale: Scale):
        self._spreads = spreads
        self.scale = scale
        self._cache: Dict[int, Optional[float]] = {}

    def at(self, row: int) -> Optional[float]:
        """The scale at `row` in bp, or `None` when fewer than `reach + 1` rows end at it."""

        if row in self._cache:
            return self._cache[row]
        scale = self.scale
        if row - scale.reach < 0:
            value = None
        else:
            if scale.kind == "mad":
                estimate = _mad(self._spreads, row, scale.windows[0])
            elif scale.kind == "blend":
                estimate = sum(_mad(self._spreads, row, w) for w in scale.windows) / len(scale.windows)
            else:
                estimate = _ewma(self._spreads, row, scale)
            value = max(scale.floor, estimate)
        self._cache[row] = value
        return value


#: #941's scale, the base (a).
BASE_SCALE = Scale("mad20", "mad", windows=(20,))


@dataclass(frozen=True)
class Arm:
    """One declared arm: a scale, and whether it feeds back yesterday's miss and reads the target day's calendar type."""

    name: str
    scale: Scale
    miss: bool = False
    calendar: bool = False


#: The arms of (v1) to (v3), in full (`metadata/faster_scale_1153.json`, `arms.listed_in_full`).
ARMS: Tuple[Arm, ...] = (
    Arm("v1_mad5", Scale("mad5", "mad", windows=(5,))),
    Arm("v1_mad10", Scale("mad10", "mad", windows=(10,))),
    Arm("v1_blend5_20", Scale("blend5_20", "blend", windows=(5, 20))),
    Arm("v2_ewma_hl3", Scale("ewma_hl3", "ewma", half_life=3.0, rows=EWMA_ROWS)),
    Arm("v2_ewma_hl5", Scale("ewma_hl5", "ewma", half_life=5.0, rows=EWMA_ROWS)),
    Arm("v2_ewma_hl10", Scale("ewma_hl10", "ewma", half_life=10.0, rows=EWMA_ROWS)),
    Arm("v2_ewma_hl5_asym", Scale("ewma_hl5_asym", "ewma", half_life=5.0, asym=ASYM, rows=EWMA_ROWS)),
    Arm("v3_miss", BASE_SCALE, miss=True),
)


def with_calendar(arm: Arm) -> Arm:
    """(v4): `arm` and a factor on its scale read at the target day's calendar type."""

    return Arm(f"v4_{arm.name}_cal", arm.scale, miss=arm.miss, calendar=True)


# -- the pieces ---------------------------------------------------------------------------------------------------------------


def missed_at(spreads: Sequence[float], row: int, *, centre: float, scale: float, lo: float, hi: float) -> bool:
    """Whether the spread at `row` is outside the closed band `[centre + scale * lo, centre + scale * hi]`.

    Mutation record: see `tests/test_spread_mr_scale.py` (`missed_at`).
    """

    y = spreads[row]
    return y < centre + scale * lo or y > centre + scale * hi


def split_pool(z: Sequence[float], missed: Sequence[bool]) -> Tuple[List[float], float]:
    """The pool to take quantiles of and the miss factor: the pairs that did not follow a miss, and the ratio of the median
    absolute standardised residuals after a miss to that after none (at least 1), when each side has `MISS_MIN` pairs; else the
    whole pool and 1.
    """

    after = [e for e, m in zip(z, missed) if m]
    clear = [e for e, m in zip(z, missed) if not m]
    if len(after) < MISS_MIN or len(clear) < MISS_MIN:
        return list(z), 1.0
    return clear, miss_factor(after, clear)


def miss_factor(after: Sequence[float], clear: Sequence[float]) -> float:
    """The widening after a miss: the ratio of median absolute standardised residuals, never below 1; 1 with too few pairs."""

    if len(after) < MISS_MIN or len(clear) < MISS_MIN:
        return 1.0
    denominator = statistics.median(abs(e) for e in clear)
    if not denominator > 0.0:
        return 1.0
    return max(1.0, statistics.median(abs(e) for e in after) / denominator)


def type_of(flags: Mapping[str, Optional[int]]) -> Optional[str]:
    """The calendar type of a target row from the flags read for it: the first of `CAL_TYPES` that is set, else `None`."""

    for name in CAL_TYPES:
        if flags.get(name):
            return name
    return None


@guard_one_step_fit
def fit_type_factors(
    pairs: Sequence[Tuple[float, Optional[str]]], *, regressors: Sequence[str], training_pairs: str,
) -> Dict[str, float]:
    """The factor on the scale of each calendar type at one lead: `(z, type)` of the direct pairs, `z` the standardised residual.

    A type enters only if `MIN_FLAGGED` pairs carry it. Its factor is the ratio of the median absolute `z` of its pairs to that of
    the pairs of no type, shrunk toward 1 by `n / (n + CAL_K)` and floored at `spread_mr_calendar.M_MIN`. `regressors` are the panel
    columns the types read (for `one_step_guard`); `training_pairs` is required and `'direct'`, the type read from each pair's own
    target row, is the only value this fit trains on. The guard decorates this function: `'one_step'` with a calendar column raises
    `ValueError` from it.

    Raises:
        ValueError: `training_pairs` is not `'direct'`.

    Mutation record: see `tests/test_spread_mr_scale.py` (`fit_type_factors`).
    """

    if training_pairs != "direct":
        raise ValueError(f"fit_type_factors trains on direct pairs only, got training_pairs={training_pairs!r}")
    ordinary = [abs(z) for z, t in pairs if t is None]
    if not ordinary:
        return {}
    reference = statistics.median(ordinary)
    if not reference > 0.0:
        return {}
    out: Dict[str, float] = {}
    for name in CAL_TYPES:
        values = [abs(z) for z, t in pairs if t == name]
        n = len(values)
        if n < cal.MIN_FLAGGED:
            continue
        ratio = statistics.median(values) / reference
        out[name] = max(cal.M_MIN, 1.0 + n / (n + CAL_K) * (ratio - 1.0))
    return out


def regressors_at(lead: int) -> Tuple[str, ...]:
    """The panel columns the calendar types read at `lead` (a coupon settlement only where the as-of rule admits it)."""

    names: List[str] = []
    for name in CAL_TYPES:
        if cal.available(cal.TERM[name], lead):
            names.extend(c for c in cal.TERM[name].reads if c not in names)
    return tuple(names)


# -- the fit ------------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class ArmFit:
    """What a refit keeps per arm: the standardised quantiles per lead, the miss factor and type factors, the band, the pairs."""

    standardised: Mapping[int, Sequence[float]]
    miss_factor: Mapping[int, float]
    type_factor: Mapping[int, Mapping[str, float]]
    #: The standardised 5% and 95% points of the lead-1 pool, the band whose miss is fed back; `None` without miss feedback.
    band: Optional[Tuple[float, float]]
    pairs: Mapping[int, int]
    left_out: Mapping[int, int]
    #: Pairs per lead whose origin followed a miss.
    after_miss: Mapping[int, int]


def _anchor_miss(
    spreads: Sequence[float], row: int, *, k0: int, phi: float, levels: Sequence[Optional[float]], reader: ScaleSeries,
    band: Tuple[float, float], factor: float,
) -> Optional[bool]:
    """Whether `row` was outside the model's own one-lead band, centred `k0 = 1 + lag` rows before it; `None` when that has no level or scale."""

    source = row - k0
    if source < 0 or levels[source] is None:
        return None
    scale = reader.at(source)
    if scale is None:
        return None
    centre = levels[source] + phi**k0 * (spreads[source] - levels[source])
    return missed_at(spreads, row, centre=centre, scale=scale * factor, lo=band[0], hi=band[1])


def _tables(table: Optional[cal.TermTable], arm: Arm) -> cal.TermTable:
    if arm.calendar and table is None:
        raise ValueError(f"{arm.name} reads the target day's calendar type and needs the term table")
    return table


def fit(
    panel: Sequence[DailyObservation],
    decision_index: int,
    arms: Sequence[Arm],
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    levels: Optional[Sequence[Optional[float]]] = None,
    base: Optional[smr.Fit] = None,
    table: Optional[cal.TermTable] = None,
) -> Dict[str, ArmFit]:
    """The pools and factors of `arms` as of the decision on row `decision_index`.

    `phi` and the training pairs are the base fit's (`spread_mean_reversion.fit` runs the information-set guards and refuses a
    training row after the anchor). A pair's raw residual is the base model's, divided by the scale at the pair's own origin, and
    by its target row's type factor where the arm has one.

    Raises:
        InsufficientHistory: the base fit's, or no pair of a lead has a scale.
        LookAheadError: a row the scale reads is after the anchor.
        ValueError: the one-step guard, or an arm with calendar types and no term table.
    """

    levels = smr.ordinary_levels(panel, splits) if levels is None else levels
    base = (
        smr.fit(panel, decision_index, registry=registry, decision_time=decision_time, splits=splits, levels=levels)
        if base is None
        else base
    )
    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    lag = decision_index - anchor
    k0 = 1 + lag
    rows = smr.training_rows(panel, decision_index, anchor, lag=lag, levels=levels)
    dates = [row.date for row in panel]
    spreads = [row.spread_bps for row in panel[: anchor + 1]]
    origins = sorted({origin for h in HORIZONS for origin, _ in rows[h]} | {anchor})
    out: Dict[str, ArmFit] = {}
    for arm in arms:
        terms = _tables(table, arm)
        reach = arm.scale.reach
        readers = sorted({o for o in origins if o - reach >= 0} | {o - k0 for o in origins if o - k0 - reach >= 0})
        read = {j for r in readers for j in scale_rows(r, arm.scale)}
        pb._require_public(read, anchor, dates, f"the scale of {arm.name} for {dates[decision_index]}")
        reader = ScaleSeries(spreads, arm.scale)
        z: Dict[int, List[float]] = {}
        origin_of: Dict[int, List[int]] = {}
        types: Dict[int, List[Optional[str]]] = {}
        factors: Dict[int, Dict[str, float]] = {}
        left_out: Dict[int, int] = {}
        for h in HORIZONS:
            k = h + lag
            raw: List[float] = []
            kept: List[int] = []
            kinds: List[Optional[str]] = []
            for origin, target in rows[h]:
                scale = reader.at(origin)
                if scale is None:
                    continue
                raw.append(((spreads[target] - levels[origin]) - base.phi**k * (spreads[origin] - levels[origin])) / scale)
                kept.append(origin)
                kinds.append(type_of(terms.flags_at(h, target)) if arm.calendar else None)
            if not raw:
                raise smr.InsufficientHistory(f"{dates[decision_index]}: no training pair of lead {h} has a scale")
            if arm.calendar:
                factors[h] = fit_type_factors(list(zip(raw, kinds)), regressors=regressors_at(h), training_pairs="direct")
                raw = [e / factors[h].get(t, 1.0) for e, t in zip(raw, kinds)]
            z[h], origin_of[h], types[h] = raw, kept, kinds
            left_out[h] = len(rows[h]) - len(raw)
        band: Optional[Tuple[float, float]] = None
        if arm.miss:
            pool_one = pb.empirical_quantiles(sorted(z[1]))
            band = (pool_one[GRID.index(BAND[0])], pool_one[GRID.index(BAND[1])])
        standardised: Dict[int, Sequence[float]] = {}
        miss_factors: Dict[int, float] = {}
        after: Dict[int, int] = {}
        for h in HORIZONS:
            pool, factor, followed = z[h], 1.0, 0
            if arm.miss:
                flags = []
                for origin in origin_of[h]:
                    tf = factors[1].get(type_of(terms.flags_at(1, origin)), 1.0) if arm.calendar else 1.0
                    flags.append(bool(_anchor_miss(
                        spreads, origin, k0=k0, phi=base.phi, levels=levels, reader=reader, band=band, factor=tf)))
                followed = sum(flags)
                pool, factor = split_pool(z[h], flags)
            standardised[h] = pb.empirical_quantiles(sorted(pool))
            miss_factors[h] = factor
            after[h] = followed
        out[arm.name] = ArmFit(standardised, miss_factors, factors, band, {h: len(z[h]) for h in HORIZONS}, left_out, after)
    return out


def forecast(
    panel: Sequence[DailyObservation],
    decision_index: int,
    fit_: ArmFit,
    arm: Arm,
    base: smr.Fit,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    levels: Optional[Sequence[Optional[float]]] = None,
    table: Optional[cal.TermTable] = None,
) -> Dict[int, List[float]]:
    """The decision day's forecast from `fit_` (possibly an older fit): `last`, `level`, `k`, the scale, yesterday's miss and the
    target rows' types are read afresh.

    Raises:
        InsufficientHistory: the anchor has no level or no scale.
        LookAheadError: a row the scale at the anchor reads, or a scheduled field of a target row, is not public.
    """

    levels = smr.ordinary_levels(panel, splits) if levels is None else levels
    terms = _tables(table, arm)
    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    level = levels[anchor]
    if level is None:
        raise smr.InsufficientHistory(
            f"{panel[decision_index].date}: fewer than {smr.LEVEL_DAYS} ordinary days before the anchor"
        )
    dates = [row.date for row in panel]
    lag = decision_index - anchor
    k0 = 1 + lag
    reach = arm.scale.reach
    if anchor - reach >= 0:
        rows = set(scale_rows(anchor, arm.scale))
        if arm.miss and anchor - k0 - reach >= 0:
            rows |= set(scale_rows(anchor - k0, arm.scale))
        pb._require_public(rows, anchor, dates, f"the scale of {arm.name} at the anchor of {dates[decision_index]}")
    spreads = [row.spread_bps for row in panel[: anchor + 1]]
    reader = ScaleSeries(spreads, arm.scale)
    scale = reader.at(anchor)
    if scale is None:
        raise smr.InsufficientHistory(f"{dates[decision_index]}: fewer than {reach + 1} rows before the anchor")
    missed = False
    if arm.miss and fit_.band is not None:
        tf = fit_.type_factor[1].get(type_of(terms.flags_at(1, anchor)), 1.0) if arm.calendar else 1.0
        missed = bool(_anchor_miss(
            spreads, anchor, k0=k0, phi=base.phi, levels=levels, reader=reader, band=fit_.band, factor=tf))
    out: Dict[int, List[float]] = {}
    for h in HORIZONS:
        flags = terms.read(h, decision_index) if arm.calendar else {}
        factor = fit_.type_factor[h].get(type_of(flags), 1.0) if arm.calendar else 1.0
        if missed:
            factor *= fit_.miss_factor[h]
        centre = level + base.phi ** (h + lag) * (spreads[anchor] - level)
        out[h] = [centre + scale * factor * value for value in fit_.standardised[h]]
    return out


# -- the walk -----------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Walk:
    #: Arm name -> decision day -> lead -> 23 quantiles.
    forecasts: Dict[str, Dict[date, Dict[int, List[float]]]]
    #: Decision day -> the day of the fit it was forecast with.
    fit_used: Dict[date, date]
    #: Refit day -> the base fit.
    fits: Dict[date, smr.Fit]
    #: Refit day -> arm name -> the arm's fit.
    arm_fits: Dict[date, Dict[str, ArmFit]]
    skipped: Tuple[date, ...]


def walk(
    panel: Sequence[DailyObservation],
    decision_days: Iterable[date],
    arms: Sequence[Arm],
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    table: Optional[cal.TermTable] = None,
    refit_every: int = smr.REFIT_EVERY,
) -> Walk:
    """Every arm on `decision_days`, refitting as `spread_mean_reversion.walk` does.

    A day on which the base model or any arm has no forecast is skipped for all, so the arms are compared on the same days.
    """

    if refit_every < 1:
        raise ValueError(f"refit_every must be at least 1, got {refit_every}")
    position = {row.date: index for index, row in enumerate(panel)}
    levels = smr.ordinary_levels(panel, splits)
    settings = dict(registry=registry, decision_time=decision_time, splits=splits, levels=levels)
    forecasts: Dict[str, Dict[date, Dict[int, List[float]]]] = {arm.name: {} for arm in arms}
    fit_used: Dict[date, date] = {}
    fits: Dict[date, smr.Fit] = {}
    arm_fits: Dict[date, Dict[str, ArmFit]] = {}
    skipped: List[date] = []
    current: Optional[smr.Fit] = None
    current_arms: Dict[str, ArmFit] = {}
    since = 0
    for day in decision_days:
        if day not in position:
            raise ProtocolError(f"decision day {day} is not a panel day")
        index = position[day]
        try:
            if current is None or since >= refit_every:
                refit = smr.fit(panel, index, **settings)
                refit_arms = fit(panel, index, arms, base=refit, table=table, **settings)
                current, current_arms = refit, refit_arms
                fits[day], arm_fits[day] = current, current_arms
                since = 0
            today = {arm.name: forecast(panel, index, current_arms[arm.name], arm, current, table=table, **settings) for arm in arms}
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
    return Walk(forecasts, fit_used, fits, arm_fits, tuple(skipped))
