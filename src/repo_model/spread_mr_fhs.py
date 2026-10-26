"""Mean reversion with volatility-scaled residuals: filtered historical simulation (#941, avenue #836; H5 step 3, development tier).

`metadata/fhs_scale_941.json` is the declaration; this module is its arithmetic. The base is
`repo_model.spread_mean_reversion` (#686), unchanged: `level + phi^k * (last - level) + eps_h`. A variant changes only the
residual pool `eps_h`:

- each training residual is divided by the scale at its own origin row, `scale(o)`;
- the standardised pool's 23 empirical quantiles are kept;
- the forecast multiplies them by the scale at the anchor, `scale(anchor)`, the last row public at the decision instant.

`scale(r)` is `max(floor, 1.4826 * median(|change|))` (estimator `mad`) or `max(floor, sd(change))` (estimator `sd`, the
declaration's one named sensitivity) over the `window` daily spread changes ending at row `r`. It reads the rows
`scale_rows(r, window)`, all at or before `r`; `fit` requires every row read, for every origin and for the anchor, to be
public at the decision instant (`protocol_benchmarks._require_public` raises `LookAheadError` otherwise). `phi`, the
level, the training pairs and the refit cadence (every 21 decision days) are the base model's. No regime label and no
other column is an input. Stdlib only.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from datetime import date, time
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from . import protocol_benchmarks as pb
from . import spread_mean_reversion as smr
from .data import DailyObservation
from .evaluation_splits import SplitDeclaration
from .scoring_protocol import HORIZONS, ProtocolError
from .splits import LookAheadError, SplitError

#: The consistency constant that makes the median absolute change an estimate of a normal standard deviation.
MAD_CONSTANT = 1.4826
ESTIMATORS: Tuple[str, ...] = ("mad", "sd")
#: The name of the unscaled base model in a walk's forecasts.
REFERENCE = "spread_mr_level10"


@dataclass(frozen=True)
class Variant:
    """One declared variant: the scale estimator, the window in panel rows and the floor in bp."""

    name: str
    estimator: str
    window: int
    floor: float

    def __post_init__(self) -> None:
        if self.estimator not in ESTIMATORS:
            raise ValueError(f"the scale estimator must be one of {ESTIMATORS}, got {self.estimator!r}")
        if not isinstance(self.window, int) or self.window < 2:
            raise ValueError(f"the scale window must be at least 2 rows, got {self.window!r}")
        if not self.floor > 0.0:
            raise ValueError(f"the scale floor must be positive, got {self.floor!r}")


#: The declared variants, in full (`metadata/fhs_scale_941.json`, `variants.listed_in_full`).
VARIANTS: Tuple[Variant, ...] = (
    Variant("spread_mr_fhs_mad20_f0.5", "mad", 20, 0.5),
    Variant("spread_mr_fhs_mad10_f0.5", "mad", 10, 0.5),
    Variant("spread_mr_fhs_mad40_f0.5", "mad", 40, 0.5),
    Variant("spread_mr_fhs_mad20_f0.25", "mad", 20, 0.25),
    Variant("spread_mr_fhs_mad20_f1.0", "mad", 20, 1.0),
    Variant("spread_mr_fhs_sd20_f0.5", "sd", 20, 0.5),
)


def scale_rows(row: int, window: int) -> range:
    """The panel rows the scale at `row` reads: the `window + 1` rows ending at `row`, whose consecutive differences are
    the `window` daily changes. None is after `row`.

    Mutation record: see `tests/test_spread_mr_fhs.py` (`scale_rows`).
    """

    return range(row - window, row + 1)


class ScaleReader:
    """The scale of one variant at the rows of a spread series; a row reads only `scale_rows`."""

    def __init__(self, spreads: Sequence[float], variant: Variant):
        self._spreads = spreads
        self.variant = variant
        self._cache: Dict[int, Optional[float]] = {}

    def at(self, row: int) -> Optional[float]:
        """The scale at `row` in bp, or `None` when fewer than `window + 1` rows end at it."""

        if row in self._cache:
            return self._cache[row]
        variant = self.variant
        rows = scale_rows(row, variant.window)
        if rows.start < 0:
            value = None
        else:
            window = [self._spreads[j] for j in rows]
            changes = [b - a for a, b in zip(window, window[1:])]
            if variant.estimator == "mad":
                estimate = MAD_CONSTANT * statistics.median(abs(c) for c in changes)
            else:
                estimate = statistics.stdev(changes)
            value = max(variant.floor, estimate)
        self._cache[row] = value
        return value


@dataclass(frozen=True)
class ScaledFit:
    """What a refit keeps per variant: the standardised residual quantiles per lead and the pairs behind them."""

    standardised: Mapping[int, Sequence[float]]
    pairs: Mapping[int, int]
    #: Pairs left out because their origin has no scale (too few rows before it).
    left_out: Mapping[int, int]


def fit(
    panel: Sequence[DailyObservation],
    decision_index: int,
    variants: Sequence[Variant],
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    levels: Optional[Sequence[Optional[float]]] = None,
    base: Optional[smr.Fit] = None,
) -> Dict[str, ScaledFit]:
    """The standardised pools of `variants` as of the decision on row `decision_index`.

    `phi` and the training pairs are the base fit's (`spread_mean_reversion.fit` runs the information-set guards and
    refuses a training row after the anchor). A pair's raw residual is the base model's, divided by the scale at the
    pair's own origin.

    Raises:
        InsufficientHistory: the base fit's, or no pair of a lead has a scale.
        LookAheadError: a row the scale reads is after the anchor.
    """

    levels = smr.ordinary_levels(panel, splits) if levels is None else levels
    base = (
        smr.fit(panel, decision_index, registry=registry, decision_time=decision_time, splits=splits, levels=levels)
        if base is None
        else base
    )
    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    lag = decision_index - anchor
    rows = smr.training_rows(panel, decision_index, anchor, lag=lag, levels=levels)
    dates = [row.date for row in panel]
    spreads = [row.spread_bps for row in panel[: anchor + 1]]
    origins = sorted({origin for h in HORIZONS for origin, _ in rows[h]} | {anchor})
    out: Dict[str, ScaledFit] = {}
    for variant in variants:
        read = {j for origin in origins if origin - variant.window >= 0 for j in scale_rows(origin, variant.window)}
        pb._require_public(read, anchor, dates, f"the scale of {variant.name} for {dates[decision_index]}")
        reader = ScaleReader(spreads, variant)
        standardised: Dict[int, List[float]] = {}
        sizes: Dict[int, int] = {}
        dropped: Dict[int, int] = {}
        for h in HORIZONS:
            k = h + lag
            pool = []
            for origin, target in rows[h]:
                scale = reader.at(origin)
                if scale is None:
                    continue
                raw = (spreads[target] - levels[origin]) - base.phi**k * (spreads[origin] - levels[origin])
                pool.append(raw / scale)
            if not pool:
                raise smr.InsufficientHistory(f"{dates[decision_index]}: no training pair of lead {h} has a scale")
            standardised[h] = pb.empirical_quantiles(sorted(pool))
            sizes[h] = len(pool)
            dropped[h] = len(rows[h]) - len(pool)
        out[variant.name] = ScaledFit(standardised, sizes, dropped)
    return out


def forecast(
    panel: Sequence[DailyObservation],
    decision_index: int,
    fit_: ScaledFit,
    base: smr.Fit,
    variant: Variant,
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    levels: Optional[Sequence[Optional[float]]] = None,
) -> Dict[int, List[float]]:
    """The decision day's forecast from `fit_` (possibly an older fit): `last`, `level`, `k` and the scale read afresh.

    Raises:
        InsufficientHistory: the anchor has no level or no scale.
        LookAheadError: a row the scale at the anchor reads is after the anchor.
    """

    levels = smr.ordinary_levels(panel, splits) if levels is None else levels
    anchor = pb._anchor(panel, decision_index, registry, decision_time)
    level = levels[anchor]
    if level is None:
        raise smr.InsufficientHistory(
            f"{panel[decision_index].date}: fewer than {smr.LEVEL_DAYS} ordinary days before the anchor"
        )
    dates = [row.date for row in panel]
    if anchor - variant.window >= 0:
        pb._require_public(
            scale_rows(anchor, variant.window), anchor, dates, f"the scale of {variant.name} at the anchor of {dates[decision_index]}"
        )
    scale = ScaleReader([row.spread_bps for row in panel[: anchor + 1]], variant).at(anchor)
    if scale is None:
        raise smr.InsufficientHistory(f"{dates[decision_index]}: fewer than {variant.window + 1} rows before the anchor")
    lag = decision_index - anchor
    last = panel[anchor].spread_bps
    out = {}
    for h in HORIZONS:
        centre = level + base.phi ** (h + lag) * (last - level)
        out[h] = [centre + scale * value for value in fit_.standardised[h]]
    return out


@dataclass(frozen=True)
class Walk:
    #: Name -> decision day -> lead -> 23 quantiles; `REFERENCE` is the base model's own walk.
    forecasts: Dict[str, Dict[date, Dict[int, List[float]]]]
    #: Decision day -> the day of the fit it was forecast with.
    fit_used: Dict[date, date]
    #: Refit day -> the base fit.
    fits: Dict[date, smr.Fit]
    #: Refit day -> variant name -> the scaled fit.
    scaled_fits: Dict[date, Dict[str, ScaledFit]]
    skipped: Tuple[date, ...]


def walk(
    panel: Sequence[DailyObservation],
    decision_days: Iterable[date],
    variants: Sequence[Variant],
    *,
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    splits: SplitDeclaration,
    refit_every: int = smr.REFIT_EVERY,
) -> Walk:
    """The base model and every variant on `decision_days`, refitting as `spread_mean_reversion.walk` does.

    The base model's forecasts are `spread_mean_reversion.walk`'s exactly. A day on which the base model or any variant
    has no forecast is skipped for all, so the models are compared on the same days.
    """

    if refit_every < 1:
        raise ValueError(f"refit_every must be at least 1, got {refit_every}")
    position = {row.date: index for index, row in enumerate(panel)}
    levels = smr.ordinary_levels(panel, splits)
    settings = dict(registry=registry, decision_time=decision_time, splits=splits, levels=levels)
    forecasts: Dict[str, Dict[date, Dict[int, List[float]]]] = {REFERENCE: {}, **{v.name: {} for v in variants}}
    fit_used: Dict[date, date] = {}
    fits: Dict[date, smr.Fit] = {}
    scaled_fits: Dict[date, Dict[str, ScaledFit]] = {}
    skipped: List[date] = []
    current: Optional[smr.Fit] = None
    current_scaled: Dict[str, ScaledFit] = {}
    since = 0
    for day in decision_days:
        if day not in position:
            raise ProtocolError(f"decision day {day} is not a panel day")
        index = position[day]
        try:
            if current is None or since >= refit_every:
                refit = smr.fit(panel, index, **settings)
                refit_scaled = fit(panel, index, variants, base=refit, **settings)
                current, current_scaled = refit, refit_scaled
                fits[day], scaled_fits[day] = current, current_scaled
                since = 0
            today = {REFERENCE: smr.forecast(panel, index, current, **settings)}
            for variant in variants:
                today[variant.name] = forecast(panel, index, current_scaled[variant.name], current, variant, **settings)
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
    return Walk(forecasts, fit_used, fits, scaled_fits, tuple(skipped))
