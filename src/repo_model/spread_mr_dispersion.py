"""Scaling (s3), the H5 candidate when this study ran, by SOFR's in-panel dispersion (#1175; H5 step 3, avenue #1166 option 1; development tier).

`metadata/sofr_dispersion_1175.json` is the declaration; this module is its arithmetic. The base is (s3) of #1145 (since #1259 the H5 candidate is (s3c), which caps (s3); this study's base stays (s3))
(`repo_model.spread_mr_state_calendar`, the Huber fit with state-scaled calendar terms on #941's scaled mean reversion), unchanged:
`centre + scale(anchor) * (shift + z)`, with `z` the pool of the standardised residuals after the terms. An arm multiplies the
scale by a factor read from SOFR's own dispersion as of the anchor row, which the panel already holds (`sofr_p25`, `sofr_p75`;
the 11 September data decision keeps the tail percentiles p1 and p99 out and this reads neither):

* (d1) the width `p75 - p25`, in bp;
* (d2) the upper half `p75 - SOFR`, in bp (Lens D);
* (d3) (d1) with the factor on the upper half of the law only.

**The ratio** at a row is its numerator over the median of the numerators of the `WINDOW` rows ending at it (rows with a missing
percentile left out; neutral, 1, with fewer than `MIN_ROWS`), the median floored at `MEDIAN_FLOOR_BP`, the ratio capped at `X_CAP`.
**The factor** is `clip(1 + gamma * (ratio - 1), F_MIN, F_MAX)`. **Gamma** is fitted at every refit and lead, walk-forward on the
training pairs: with `e` a pair's standardised residual after the terms, the least-squares slope of `|e|` on `ratio - 1` over its
intercept at ratio 1, kept between 0 and `GAMMA_MAX`, and 0 with fewer than `MIN_PAIRS` pairs or no spread in the ratio. (d1) and
(d2) then refit the terms and the pool on the residuals standardised by `scale * factor` of each pair's own origin (filtered
historical simulation as the base); (d3) keeps (s3)'s terms and divides only the positive residuals by their factor, and the
forecast multiplies only the positive pool values by the anchor's factor.

**As-of.** The ratio at a row reads `rows_read(row)`, all at or before it; `fit` and `forecast` require every row read to be
public at the decision instant (`protocol_benchmarks._require_public` raises `LookAheadError`), and `require_available` runs the
information-set rule (`asof.InformationRule`) on `sofr_p25` and `sofr_p75` for every lead and raises `LookAheadError` when a
percentile of the anchor row was not yet public although the anchor's spread was. The calendar terms are those of (s3): read at
the target day on direct pairs (`spread_mr_state_calendar.fit_state_terms` is `one_step_guard`-guarded).

Stdlib only.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, replace
from datetime import date, time
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from . import protocol_benchmarks as pb
from . import spread_mean_reversion as smr
from . import spread_mr_calendar as cal
from . import spread_mr_fhs as fhs
from . import spread_mr_state_calendar as sc
from .asof import InformationRule
from .data import DailyObservation
from .evaluation_splits import SplitDeclaration
from .scoring_protocol import HORIZONS, ProtocolError
from .splits import LookAheadError, SplitError

#: Rows of the trailing window whose median the ratio is taken against, ending at the row.
WINDOW = 60
#: The fewest rows with a value the window needs; with fewer the ratio is neutral (1).
MIN_ROWS = 20
#: The median is never taken below this many bp (a flat floor period has a median of zero).
MEDIAN_FLOOR_BP = 0.5
#: The ratio is capped here.
X_CAP = 4.0
#: The factor is kept between these.
F_MIN = 0.5
F_MAX = 2.0
#: The slope of the factor is kept between 0 and this.
GAMMA_MAX = 2.0
#: The fewest training pairs a slope is fitted on.
MIN_PAIRS = 60
FEATURES = ("sofr_p25", "sofr_p75")
ARM_A = sc.ARM_A
#: (s3) of #1145, the base: Huber fit, ridge 5, standardised units.
BASE_ARM = sc.ARMS[2]


@dataclass(frozen=True)
class DispArm:
    """One declared arm: the numerator of the ratio and whether the factor is applied to the upper half of the law only."""

    name: str
    role: str
    numerator: str
    upper_only: bool


ARMS: Tuple[DispArm, ...] = (
    DispArm("d1_iqr", "(d1) the width p75 - p25 relative to its trailing median", "iqr", False),
    DispArm("d2_upper_half", "(d2) p75 - SOFR relative to its trailing median", "upper", False),
    DispArm("d3_iqr_upper_tail", "(d3) (d1) with the factor on the upper tail only", "iqr", True),
)
MODEL_NAMES: Tuple[str, ...] = (ARM_A, BASE_ARM.name) + tuple(a.name for a in ARMS)


# Lockbox classification (#1058): tests/test_lockbox.py reads these literals from this file's syntax tree.
LOCKBOX_READS = {
    "require_available": (
        "not_entry",
        "checks that the anchor row's percentiles were public at the decision instant (the as-of rule); "
        "scores nothing; the days `scripts/sofr_dispersion_1175.py` scores end on 2025-12-31 and go "
        "through the scorer of scoring protocol v1, which refuses a locked day",
    ),
}

# -- the ratio ----------------------------------------------------------------------------------------------------------------


def numerator_bp(row: DailyObservation, kind: str) -> Optional[float]:
    """The width (`iqr`) or the upper half (`upper`) of SOFR's distribution on `row`, in bp; `None` when a percentile is missing."""

    v = row.values
    if v.get("sofr_p25") is None or v.get("sofr_p75") is None or v.get("sofr") is None:
        return None
    if kind == "iqr":
        return 100.0 * (float(v["sofr_p75"]) - float(v["sofr_p25"]))
    if kind == "upper":
        return 100.0 * (float(v["sofr_p75"]) - float(v["sofr"]))
    raise ValueError(f"the numerator is 'iqr' or 'upper', got {kind!r}")


def rows_read(row: int) -> range:
    """The panel rows the ratio at `row` reads: the `WINDOW` rows ending at it. None is after `row`.

    Mutation record: see `tests/test_spread_mr_dispersion.py` (`rows_read`).
    """

    return range(max(0, row - WINDOW + 1), row + 1)


def ratio_at(series: Sequence[Optional[float]], row: int) -> float:
    """The numerator at `row` over the median of the window's, floored and capped; 1 when the window or the value is missing."""

    if series[row] is None:
        return 1.0
    window = [series[j] for j in rows_read(row) if j < len(series) and series[j] is not None]
    if len(window) < MIN_ROWS:
        return 1.0
    return min(X_CAP, max(0.0, series[row]) / max(MEDIAN_FLOOR_BP, statistics.median(window)))


def factor(ratio: float, gamma: float) -> float:
    """The multiplier on the scale: `1 + gamma * (ratio - 1)`, kept between `F_MIN` and `F_MAX`."""

    return min(F_MAX, max(F_MIN, 1.0 + gamma * (ratio - 1.0)))


def fit_gamma(ratios: Sequence[float], residuals: Sequence[float], *, upper_only: bool) -> float:
    """The slope of the factor: the least-squares slope of `|e|` on `ratio - 1` over its intercept at ratio 1, between 0 and
    `GAMMA_MAX`; 0 with fewer than `MIN_PAIRS` pairs (only the positive residuals when `upper_only`), no spread in the ratio, or a
    non-positive intercept."""

    pairs = [(x - 1.0, abs(e)) for x, e in zip(ratios, residuals) if not upper_only or e > 0.0]
    if len(pairs) < MIN_PAIRS:
        return 0.0
    mx = statistics.fmean(p[0] for p in pairs)
    my = statistics.fmean(p[1] for p in pairs)
    sxx = sum((x - mx) ** 2 for x, _ in pairs)
    if not sxx > 1e-12:
        return 0.0
    slope = sum((x - mx) * (y - my) for x, y in pairs) / sxx
    intercept = my - slope * mx
    if not intercept > 0.0:
        return 0.0
    return min(GAMMA_MAX, max(0.0, slope / intercept))


# -- the as-of check ----------------------------------------------------------------------------------------------------------


def require_available(
    panel: Sequence[DailyObservation], decision_index: int, anchor: int, *, registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
) -> None:
    """The percentiles of the anchor row are public at the decision instant, at every lead.

    Runs the information-set rule of `sofr_p25` and `sofr_p75` (both guards) and raises when the latest row whose percentiles were
    public is before the anchor, the last row whose spread was: reading the anchor's percentiles would be reading a value not yet
    published.

    Raises:
        LookAheadError: a percentile of the anchor row was not public at the decision instant.

    Mutation record: see `tests/test_spread_mr_dispersion.py` (`require_available`).
    """

    dates = [row.date for row in panel]
    for h in HORIZONS:
        rule = InformationRule(registry, FEATURES, decision_time=decision_time, horizon=h)
        info = rule.information_set(dates, decision_index + h)
        rule.check(dates, info)
        for read in info.reads:
            if read.feature in FEATURES and read.row < anchor:
                raise LookAheadError(
                    f"{read.feature!r} of {dates[anchor]} was not public at the decision of {dates[decision_index]} (the latest row "
                    f"public is {dates[read.row]}), so the dispersion at the anchor cannot be read"
                )


class Series:
    """The ratio of one numerator at the rows of a panel; a row reads only `rows_read`."""

    def __init__(self, panel: Sequence[DailyObservation], kind: str):
        self._values = [numerator_bp(row, kind) for row in panel]
        self._cache: Dict[int, float] = {}

    def at(self, row: int) -> float:
        if row not in self._cache:
            self._cache[row] = ratio_at(self._values, row)
        return self._cache[row]


# -- the fit ------------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class LeadFit:
    """What a refit keeps for one arm and lead: the slope, the estimate (terms and the pool) and the ratios' mean."""

    gamma: float
    estimate: sc.StateEstimate
    upper_only: bool
    mean_ratio: float


def _residual(pair: sc.StatePair, estimate: sc.StateEstimate) -> float:
    return pair.raw / pair.scale - sum(estimate.effect[n] * pair.flags[n] for n in estimate.effect)


def fit_lead(
    pairs: Sequence[sc.StatePair], ratios: Sequence[float], arm: DispArm, *, regressors: Sequence[str],
    training_pairs: str = "direct",
) -> LeadFit:
    """The arm's slope, terms and pool at one lead on the direct pairs `pairs`, whose origins have the ratios `ratios`.

    The terms are fitted as (s3) fits them (Huber, ridge 5); the slope is then read from their residuals; (d1) and (d2) refit the
    terms and the pool on the residuals standardised by the pair's own `scale * factor`, (d3) keeps (s3)'s terms and divides the
    positive residuals by their factor.
    """

    def terms(rows: Sequence[sc.StatePair]) -> sc.StateEstimate:
        return sc.fit_state_terms(
            rows, regressors=regressors, terms=BASE_ARM.location, interact=False, robust=BASE_ARM.robust,
            training_pairs=training_pairs,
        )

    first = terms(pairs)
    mean_ratio = statistics.fmean(ratios) if ratios else 1.0
    residuals = [_residual(p, first) for p in pairs]
    gamma = fit_gamma(ratios, residuals, upper_only=arm.upper_only)
    if arm.upper_only:
        if gamma == 0.0:
            return LeadFit(0.0, first, True, mean_ratio)
        scaled = [e / factor(x, gamma) if e > 0.0 else e for e, x in zip(residuals, ratios)]
        return LeadFit(gamma, replace(first, pool=pb.empirical_quantiles(sorted(scaled))), True, mean_ratio)
    rescaled = [sc.StatePair(p.raw, p.scale * factor(x, gamma), p.flags, None) for p, x in zip(pairs, ratios)]
    return LeadFit(gamma, terms(rescaled), False, mean_ratio)


def lead_quantiles(fit_: LeadFit, arm: DispArm, *, centre: float, scale: float, flags: Mapping[str, int], ratio: float) -> List[float]:
    """The 23 quantiles: `centre + scale * (shift + pool)` with the scale times the factor of `ratio`, or, for the upper-tail arm,
    only the positive pool values times it."""

    f = factor(ratio, fit_.gamma)
    shift = sc.standardised_shift(fit_.estimate, flags, None)
    if arm.upper_only:
        return [centre + scale * (shift + (v * f if v > 0.0 else v)) for v in fit_.estimate.pool]
    return [centre + scale * f * (shift + v) for v in fit_.estimate.pool]


def refit(
    panel: Sequence[DailyObservation],
    decision_index: int,
    table: cal.TermTable,
    arms: Sequence[DispArm],
    series: Mapping[str, Series],
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    levels: Sequence[Optional[float]],
    base: smr.Fit,
    training_pairs: str = "direct",
) -> Dict[str, Dict[int, LeadFit]]:
    """Each arm's fit at each lead as of the decision on row `decision_index`, on the base model's training pairs.

    Raises:
        InsufficientHistory: the base fit's, or a lead with no pair that has a scale.
        LookAheadError: a row the scale or the ratio reads is after the anchor, or a percentile was not yet public.
        ValueError: the one-step guard (`spread_mr_state_calendar.fit_state_terms`).
    """

    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    lag = decision_index - anchor
    rows = smr.training_rows(panel, decision_index, anchor, lag=lag, levels=levels)
    dates = [row.date for row in panel]
    spreads = [row.spread_bps for row in panel[: anchor + 1]]
    origins = sorted({origin for h in HORIZONS for origin, _ in rows[h]} | {anchor})
    variant = sc.BASE_VARIANT
    scale_read = {j for origin in origins if origin - variant.window >= 0 for j in fhs.scale_rows(origin, variant.window)}
    pb._require_public(scale_read, anchor, dates, f"the scale of {variant.name} for {dates[decision_index]}")
    ratio_read = {j for origin in origins for j in rows_read(origin)}
    pb._require_public(ratio_read, anchor, dates, f"the dispersion ratio for {dates[decision_index]}")
    require_available(panel, decision_index, anchor, registry=registry, decision_time=decision_time)
    reader = fhs.ScaleReader(spreads, variant)
    out: Dict[str, Dict[int, LeadFit]] = {}
    for arm in arms:
        per_lead: Dict[int, LeadFit] = {}
        for h in HORIZONS:
            k = h + lag
            pairs, ratios = [], []
            for origin, target in rows[h]:
                scale = reader.at(origin)
                if scale is None:
                    continue
                raw = (spreads[target] - levels[origin]) - base.phi**k * (spreads[origin] - levels[origin])
                flags_row = target if training_pairs == "direct" else origin
                pairs.append(sc.StatePair(raw, scale, table.flags_at(h, flags_row), None))
                ratios.append(series[arm.numerator].at(origin))
            if not pairs:
                raise smr.InsufficientHistory(f"{dates[decision_index]}: no training pair of lead {h} has a scale")
            per_lead[h] = fit_lead(pairs, ratios, arm, regressors=cal.regressors_of(BASE_ARM, h), training_pairs=training_pairs)
        out[arm.name] = per_lead
    return out


def forecast(
    panel: Sequence[DailyObservation],
    decision_index: int,
    fits: Mapping[str, Mapping[int, LeadFit]],
    table: cal.TermTable,
    arms: Sequence[DispArm],
    series: Mapping[str, Series],
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    levels: Sequence[Optional[float]],
    base: smr.Fit,
) -> Tuple[Dict[str, Dict[int, List[float]]], Dict[str, object]]:
    """The arms' forecasts of the decision day from `fits` (possibly an older fit), and the day's detail (the scale at the anchor
    and each ratio): `last`, `level`, `k`, the anchor, its scale and ratio, and the flags of each target row are read afresh.

    Raises:
        InsufficientHistory: the anchor has no level or no scale.
        LookAheadError: a row the scale or the ratio at the anchor reads, a scheduled field of a target row, or a percentile is not public.
    """

    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    level_at = levels[anchor]
    if level_at is None:
        raise smr.InsufficientHistory(f"{panel[decision_index].date}: fewer than {smr.LEVEL_DAYS} ordinary days before the anchor")
    dates = [row.date for row in panel]
    variant = sc.BASE_VARIANT
    if anchor - variant.window >= 0:
        pb._require_public(
            fhs.scale_rows(anchor, variant.window), anchor, dates, f"the scale of {variant.name} at the anchor of {dates[decision_index]}"
        )
    pb._require_public(rows_read(anchor), anchor, dates, f"the dispersion ratio at the anchor of {dates[decision_index]}")
    require_available(panel, decision_index, anchor, registry=registry, decision_time=decision_time)
    scale = fhs.ScaleReader([row.spread_bps for row in panel[: anchor + 1]], variant).at(anchor)
    if scale is None:
        raise smr.InsufficientHistory(f"{dates[decision_index]}: fewer than {variant.window + 1} rows before the anchor")
    lag = decision_index - anchor
    last = panel[anchor].spread_bps
    out: Dict[str, Dict[int, List[float]]] = {arm.name: {} for arm in arms}
    for h in HORIZONS:
        flags = table.read(h, decision_index)
        centre = level_at + base.phi ** (h + lag) * (last - level_at)
        for arm in arms:
            out[arm.name][h] = lead_quantiles(
                fits[arm.name][h], arm, centre=centre, scale=scale, flags=flags, ratio=series[arm.numerator].at(anchor)
            )
    return out, {"scale": scale, **{kind: series[kind].at(anchor) for kind in series}}


# -- the walk -----------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Walk:
    #: Model name -> decision day -> lead -> 23 quantiles; `ARM_A` is #941's variant, (s3) the base, then the arms.
    forecasts: Dict[str, Dict[date, Dict[int, List[float]]]]
    fit_used: Dict[date, date]
    #: Refit day -> the base fit.
    fits: Dict[date, smr.Fit]
    #: Refit day -> arm name -> lead -> the fit.
    leads: Dict[date, Dict[str, Dict[int, LeadFit]]]
    #: Decision day -> the scale at the anchor and the two ratios the forecast read.
    detail: Dict[date, Dict[str, object]]
    skipped: Tuple[date, ...]


def walk(
    panel: Sequence[DailyObservation],
    decision_days: Iterable[date],
    table: cal.TermTable,
    arms: Sequence[DispArm] = ARMS,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    refit_every: int = smr.REFIT_EVERY,
    training_pairs: str = "direct",
) -> Walk:
    """Arm (a), (s3) and `arms` on `decision_days`, refitting as `spread_mr_state_calendar.walk` does (the base fit, #941's pool, the
    terms, then the slope). A day on which any model has no forecast is skipped for all, so they are compared on the same days.
    """

    if refit_every < 1:
        raise ValueError(f"refit_every must be at least 1, got {refit_every}")
    position = {row.date: index for index, row in enumerate(panel)}
    levels = smr.ordinary_levels(panel, splits)
    settings = dict(registry=registry, decision_time=decision_time, splits=splits, levels=levels)
    series = {kind: Series(panel, kind) for kind in ("iqr", "upper")}
    forecasts: Dict[str, Dict[date, Dict[int, List[float]]]] = {ARM_A: {}, BASE_ARM.name: {}, **{arm.name: {} for arm in arms}}
    fit_used: Dict[date, date] = {}
    fits: Dict[date, smr.Fit] = {}
    leads: Dict[date, Dict[str, Dict[int, LeadFit]]] = {}
    detail: Dict[date, Dict[str, object]] = {}
    skipped: List[date] = []
    current: Optional[smr.Fit] = None
    current_scaled: Optional[fhs.ScaledFit] = None
    current_s3: Dict[str, Dict[int, sc.StateEstimate]] = {}
    current_leads: Dict[str, Dict[int, LeadFit]] = {}
    since = 0
    for day in decision_days:
        if day not in position:
            raise ProtocolError(f"decision day {day} is not a panel day")
        index = position[day]
        try:
            if current is None or since >= refit_every:
                base = smr.fit(panel, index, **settings)
                scaled = fhs.fit(panel, index, [sc.BASE_VARIANT], base=base, **settings)[sc.BASE_VARIANT.name]
                found_s3 = sc.refit(
                    panel, index, table, {}, [BASE_ARM], registry=registry, decision_time=decision_time, levels=levels, base=base,
                    training_pairs=training_pairs,
                )
                found = refit(
                    panel, index, table, arms, series, registry=registry, decision_time=decision_time, levels=levels, base=base,
                    training_pairs=training_pairs,
                )
                current, current_scaled, current_s3, current_leads = base, scaled, found_s3, found
                fits[day], leads[day] = base, found
                since = 0
            today = {ARM_A: fhs.forecast(panel, index, current_scaled, current, sc.BASE_VARIANT, **settings)}
            mine_s3, extra = sc.forecast(
                panel, index, current_s3, table, {}, [BASE_ARM], registry=registry, decision_time=decision_time, levels=levels,
                base=current,
            )
            today.update(mine_s3)
            mine, extra_d = forecast(
                panel, index, current_leads, table, arms, series, registry=registry, decision_time=decision_time, levels=levels,
                base=current,
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
        detail[day] = {"scale": extra["scale"], "iqr": extra_d["iqr"], "upper": extra_d["upper"]}
        since += 1
        for name, quantiles in today.items():
            forecasts[name][day] = quantiles
    return Walk(forecasts, fit_used, fits, leads, detail, tuple(skipped))
