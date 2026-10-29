"""Miss feedback and a calendar-type scale factor (v4 of #1153) on (s3) of #1145 (#1172; H5 step 3).

`metadata/s3_decomposition_1172.json` is the declaration; this module is its arithmetic. (s3) is the base of (s3c) (`repo_model.s3c_candidate`), which was the H5 candidate from #1259 and is the base of (s3c-ann-net), the H5 candidate since #1310 (`repo_model.s3c_announced`); here it is the base of this study. (s3) is `repo_model.spread_mr_state_calendar`'s
robust arm: `level + phi^k (last - level) + scale(anchor) * (shift + z_h)`, with `shift` the location terms in scale units and `z_h` the
quantiles of the residual they leave. #1153's v4 is `repo_model.spread_mr_scale`'s arm of that name, a faster-reacting *scale*: after
the anchor row was outside the 90% band the model gave it, the scale is multiplied by a factor fitted at each refit, and it is
multiplied by a factor read at the target day's calendar type. Here both act on the dispersion of (s3) only:

    q = centre + scale(anchor) * (shift + factor * z_h),   factor = type_factor(target row) * miss_factor (after a miss)

the location terms of (s3) stay as they are, and the pool is the residual of (s3) divided by the type factor of each pair's own target
row and without the pairs that followed a miss. The factors, the thresholds and the cap are `repo_model.spread_mr_scale`'s, used
unchanged; the miss rule is the same one (the closed 90% band of the one-lead forecast, centred `1 + lag` rows before the row, which
here includes (s3)'s shift for that row), and it reads no row after the anchor.

**Read at the target day.** The type of a target row comes from `spread_mr_calendar.TermTable`: its columns are served from the target
row (`asof` rule 2) and a scheduled field (a coupon settlement) is read only where the as-of rule admits it (lead 1);
`spread_mr_scale.fit_type_factors` is decorated with `one_step_guard.guard_one_step_fit` and trains on direct pairs only.

Stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from . import protocol_benchmarks as pb
from . import spread_mean_reversion as smr
from . import spread_mr_calendar as cal
from . import spread_mr_fhs as fhs
from . import spread_mr_scale as scale_mod
from . import spread_mr_state_calendar as sc
from .data import DailyObservation
from .evaluation_splits import SplitDeclaration
from .scoring_protocol import GRID, HORIZONS
from .splits import LookAheadError, SplitError

ARM_NAME = "sc_s3_v4"
BASE_VARIANT = sc.BASE_VARIANT


def missed_anchor(
    spreads: Sequence[float], row: int, *, k0: int, phi: float, level: float, source_scale: float, shift: float, factor: float,
    band: Tuple[float, float],
) -> bool:
    """Whether the spread at `row` was outside the closed band of the one-lead forecast made from `row - k0`.

    The band is `centre + source_scale * (shift + factor * band)`, with `centre = level + phi^k0 (spread[source] - level)` and `level`
    the ordinary level at the source row. `row` is the row judged (an origin of a training pair, or the anchor of the decision); the
    source is `k0 = 1 + lag` rows before it, so the outcome never enters its own band.

    Mutation record: see `tests/test_spread_mr_s3_decomposition.py` (`missed_anchor`).
    """

    source = row - k0
    centre = level + phi**k0 * (spreads[source] - level)
    return scale_mod.missed_at(
        spreads, row, centre=centre, scale=source_scale, lo=shift + factor * band[0], hi=shift + factor * band[1]
    )


@dataclass(frozen=True)
class V4Fit:
    """What a refit keeps: the standardised quantiles per lead, the miss and type factors, the band whose miss is fed back."""

    standardised: Mapping[int, Sequence[float]]
    miss_factor: Mapping[int, float]
    type_factor: Mapping[int, Mapping[str, float]]
    band: Tuple[float, float]
    after_miss: Mapping[int, int]
    pairs: Mapping[int, int]


def _check_arm(estimates: Mapping[int, sc.StateEstimate]) -> None:
    for estimate in estimates.values():
        if estimate.slope or estimate.sized:
            raise ValueError("v4 is declared for an arm with no state and no sizes (s3): its band would need the decision's state")


def _source_miss(
    panel_spreads: Sequence[float], row: int, *, k0: int, base: smr.Fit, levels: Sequence[Optional[float]],
    reader: fhs.ScaleReader, shift: float, factor: float, band: Tuple[float, float],
) -> Optional[bool]:
    """`missed_anchor` for `row`, or `None` when the source row has no level or no scale."""

    source = row - k0
    if source < 0 or levels[source] is None:
        return None
    scale = reader.at(source)
    if scale is None:
        return None
    return missed_anchor(
        panel_spreads, row, k0=k0, phi=base.phi, level=levels[source], source_scale=scale, shift=shift, factor=factor, band=band
    )


def fit_v4(
    panel: Sequence[DailyObservation],
    decision_index: int,
    estimates: Mapping[int, sc.StateEstimate],
    table: cal.TermTable,
    base: smr.Fit,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    levels: Sequence[Optional[float]],
) -> V4Fit:
    """The type factors, the miss factors and the pools of v4 from (s3)'s estimates as of the decision on `decision_index`.

    The pairs, their rows and their residuals are those of (s3)'s fit (`StateEstimate.origins`, `.targets`, `.residuals`).

    Raises:
        ValueError: an estimate with a state slope or sizes, or the one-step guard of `fit_type_factors`.
        LookAheadError: a row a scale reads is after the anchor.
    """

    _check_arm(estimates)
    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    lag = decision_index - anchor
    k0 = 1 + lag
    dates = [row.date for row in panel]
    spreads = [row.spread_bps for row in panel[: anchor + 1]]
    origins = sorted({o for h in HORIZONS for o in estimates[h].origins})
    read = {
        j for o in origins if o - k0 - BASE_VARIANT.window >= 0 for j in fhs.scale_rows(o - k0, BASE_VARIANT.window)
    }
    pb._require_public(read, anchor, dates, f"the scale behind the miss band of v4 for {dates[decision_index]}")
    reader = fhs.ScaleReader(spreads, BASE_VARIANT)
    z: Dict[int, List[float]] = {}
    factors: Dict[int, Dict[str, float]] = {}
    for h in HORIZONS:
        estimate = estimates[h]
        kinds = [scale_mod.type_of(table.flags_at(h, target)) for target in estimate.targets]
        factors[h] = scale_mod.fit_type_factors(
            list(zip(estimate.residuals, kinds)), regressors=scale_mod.regressors_at(h), training_pairs="direct"
        )
        z[h] = [e / factors[h].get(t, 1.0) for e, t in zip(estimate.residuals, kinds)]
    one = pb.empirical_quantiles(sorted(z[1]))
    band = (one[GRID.index(scale_mod.BAND[0])], one[GRID.index(scale_mod.BAND[1])])
    standardised: Dict[int, Sequence[float]] = {}
    miss_factors: Dict[int, float] = {}
    after: Dict[int, int] = {}
    for h in HORIZONS:
        flags = []
        for origin in estimates[h].origins:
            row_flags = table.flags_at(1, origin)
            shift = sc.standardised_shift(estimates[1], row_flags, None)
            type_factor = factors[1].get(scale_mod.type_of(row_flags), 1.0)
            flags.append(bool(_source_miss(
                spreads, origin, k0=k0, base=base, levels=levels, reader=reader, shift=shift, factor=type_factor, band=band)))
        pool, factor = scale_mod.split_pool(z[h], flags)
        standardised[h] = pb.empirical_quantiles(sorted(pool))
        miss_factors[h] = factor
        after[h] = sum(flags)
    return V4Fit(standardised, miss_factors, factors, band, after, {h: estimates[h].pairs for h in HORIZONS})


def forecast_v4(
    panel: Sequence[DailyObservation],
    decision_index: int,
    fit_: V4Fit,
    estimates: Mapping[int, sc.StateEstimate],
    table: cal.TermTable,
    base: smr.Fit,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    levels: Sequence[Optional[float]],
) -> Dict[int, List[float]]:
    """The decision day's forecast from `fit_` and `estimates` (possibly an older fit): `last`, `level`, `k`, the scale, yesterday's
    miss and the target rows' flags are read afresh.

    Raises:
        InsufficientHistory: the anchor has no level or no scale.
        LookAheadError: a row the scale at the anchor reads, or a scheduled field of a target row, is not public.
    """

    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    level_at = levels[anchor]
    if level_at is None:
        raise smr.InsufficientHistory(f"{panel[decision_index].date}: fewer than {smr.LEVEL_DAYS} ordinary days before the anchor")
    dates = [row.date for row in panel]
    lag = decision_index - anchor
    k0 = 1 + lag
    window = BASE_VARIANT.window
    if anchor - window >= 0:
        rows = set(fhs.scale_rows(anchor, window))
        if anchor - k0 - window >= 0:
            rows |= set(fhs.scale_rows(anchor - k0, window))
        pb._require_public(rows, anchor, dates, f"the scale of v4 at the anchor of {dates[decision_index]}")
    spreads = [row.spread_bps for row in panel[: anchor + 1]]
    reader = fhs.ScaleReader(spreads, BASE_VARIANT)
    scale = reader.at(anchor)
    if scale is None:
        raise smr.InsufficientHistory(f"{dates[decision_index]}: fewer than {window + 1} rows before the anchor")
    anchor_flags = table.flags_at(1, anchor)
    missed = bool(_source_miss(
        spreads, anchor, k0=k0, base=base, levels=levels, reader=reader,
        shift=sc.standardised_shift(estimates[1], anchor_flags, None),
        factor=fit_.type_factor[1].get(scale_mod.type_of(anchor_flags), 1.0), band=fit_.band))
    last = spreads[anchor]
    out: Dict[int, List[float]] = {}
    for h in HORIZONS:
        flags = table.read(h, decision_index)
        factor = fit_.type_factor[h].get(scale_mod.type_of(flags), 1.0)
        if missed:
            factor *= fit_.miss_factor[h]
        shift = sc.standardised_shift(estimates[h], flags, None)
        centre = level_at + base.phi ** (h + lag) * (last - level_at)
        out[h] = [centre + scale * (shift + factor * value) for value in fit_.standardised[h]]
    return out


@dataclass(frozen=True)
class Walk:
    #: Decision day -> lead -> 23 quantiles.
    forecasts: Dict[date, Dict[int, List[float]]]
    #: Refit day -> the fit.
    fits: Dict[date, V4Fit]
    skipped: Tuple[date, ...]


def walk(
    panel: Sequence[DailyObservation],
    mine: sc.Walk,
    arm_name: str,
    table: cal.TermTable,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
) -> Walk:
    """v4 on the arm `arm_name` of `mine` (a walk of `spread_mr_state_calendar`), on the days that arm forecast, with the same refits.

    A day on which v4 has no forecast is skipped; the caller scores the days every model has.
    """

    arm = sc.ALL_ARMS[arm_name]
    if arm.interact or arm.sized:
        raise ValueError(f"v4 is declared for an arm with no state and no sizes (s3), not {arm_name}")
    position = {row.date: index for index, row in enumerate(panel)}
    levels = smr.ordinary_levels(panel, splits)
    settings = dict(registry=registry, decision_time=decision_time, levels=levels)
    refit_of = {fit_.fitted_on: day for day, fit_ in mine.fits.items()}
    forecasts: Dict[date, Dict[int, List[float]]] = {}
    fits: Dict[date, V4Fit] = {}
    skipped: List[date] = []
    for day in sorted(mine.forecasts[arm_name]):
        refit_day = refit_of[mine.fit_used[day]]
        estimates = mine.estimates[refit_day][arm_name]
        base = mine.fits[refit_day]
        try:
            if refit_day not in fits:
                fits[refit_day] = fit_v4(panel, position[refit_day], estimates, table, base, **settings)
            forecasts[day] = forecast_v4(panel, position[day], fits[refit_day], estimates, table, base, **settings)
        except smr.InsufficientHistory:
            skipped.append(day)
        except LookAheadError:
            raise  # a guard trip is never "no public row yet"
        except SplitError:
            skipped.append(day)
    return Walk(forecasts, fits, tuple(skipped))
