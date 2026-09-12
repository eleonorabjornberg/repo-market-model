"""Gradient-boosted conditional quantiles: the `ml` extra's one module.

Owned by **Track B (model and evaluation)**. This is the *only* module in the
package allowed to reach numpy or scikit-learn, and it may reach them only from
inside the functions that use them --- `AGENT_CONTRACT.md`'s working rules and
`tests/test_dependency_boundary.py`, which fails this file for a module-level
`import sklearn`. The rule is not stylistic: `repo_model`'s two conformance
walks (`tests/test_contract.py::ForecastInterfaceCoverageTests` and
`tests/test_baseline.py::ExceedancePredictorCoverageTests`) import every module
of this package, so a module-level optional import would turn the *core* suite
red on every checkout without the extra rather than skipping one test file.

What is here is one model in two shapes, the two shapes this repository already
has interfaces for:

* `FittedGradientBoostedQuantiles` / `fit_gradient_boosted_quantiles` --- the
  forecast interface (`baseline.FittedForecastModel`).
* `gbm_exceedance` --- the exceedance interface
  (`baseline.ExceedancePredictor`), derived from the same fitted quantiles and
  not fitted apart from them.

**One fit per contract level.** `HistGradientBoostingRegressor(loss="quantile",
quantile=level)` is fitted once for each level in `contract.QUANTILE_LEVELS`,
on the one-step-ahead design `fit_arx` builds --- last observed spread plus the
declared regressors --- minus the intercept, which a tree ensemble does not
need and cannot use. The design, the imputation of an unobserved regressor by
its training-window mean, and the refusal to coerce an absent column to `0.0`
are `fit_arx`'s and are reached through `baseline`'s own helpers rather than
restated here: two spellings of one design is how two models stop being
comparable.

**The two traps this model has, named.**

*Quantile crossing.* Five independent fits are not constrained to be ordered,
and on a small or heteroscedastic window they are not: the 0.25 fit can land
above the 0.50 fit on a particular row. Reported as-is, that is a predictive
distribution whose CDF decreases, and every consumer downstream --- the
`P(Y > tau)` monotonicity `event_eval` checks, CRPS, the interval coverage
statistic --- reads it as a broken law. **The rearrangement used here is
sorting**, which for a finite level grid is exactly the rearrangement of
Chernozhukov, Fernandez-Val and Galichon: the sorted vector is a valid quantile
function, and it is never further from the true quantile curve than the crossed
one it replaces. It is applied in `_rearranged`, which is the single place a
predicted vector is produced, so `predict`, `point_forecast`, the fitted
residual sample and `predict_stress` all read the *same* rearranged vector and
cannot disagree about it.

*Non-determinism.* `HistGradientBoostingRegressor`'s `early_stopping` default is
`"auto"`, which turns early stopping **on** above 10 000 rows and then draws an
internal validation split; with no `random_state` that split moves between fits
and two fits of the same model on the same rows return different numbers. A
published record produced that way cannot be re-scored. Both are therefore set
explicitly here --- `early_stopping=False` and a fixed `random_state` --- rather
than left at a default that changes behaviour with the size of the panel.

**The band's calibration, opt-in (B22).** Every level is fitted in-sample, and a
boosted quantile fit is tight on the rows it was fitted on, so the outer
`0.05`-`0.95` band under-covers out of sample: the published backtest at
`--minimum-history 61` puts its nominal 90% at well under that. `calibration=
"conformal"` is conformalized quantile regression (Romano, Patterson and Candes,
2019), done causally inside the one training frame a fold hands over:

* the frame is split by date. The most recent `calibration_share` of its rows
  are **calibration rows**; the **fit rows** are the earlier rows that clear the
  registry-derived purge gap before the first calibration row, by
  `splits.clears_purge` -- the splitter's own comparison, so no fit row's value,
  and so no fit row's target, is one the forecaster could not have had when the
  calibration slice opens;
* every level is fitted on the fit rows **only**, and never refitted on the
  union afterwards: a refit scores the calibration rows with a model that has
  seen them, which is the in-sample residual tail again and voids the
  finite-sample guarantee;
* each calibration row is scored `s = max(Q_lo - y, y - Q_hi)` off the
  rearranged vector, its feature row chosen by `baseline._feature_index` -- the
  rule a scored day's feature row is chosen by, so a calibration score is at the
  horizon the backtest scores at -- and the `ceil((1 - alpha)(n + 1))`-th
  smallest score is the **widening**, with `1 - alpha` the declared band's own
  span. `Q_lo` moves down and `Q_hi` up by it, and it may be negative. The
  interior levels are untouched; an outer level that a negative widening would
  carry past its neighbour stops at the neighbour, so the vector stays
  non-decreasing; and the two outer knots `predict_stress` reads move with the
  band.

`calibration="none"` is the default and is the model every published record was
produced with: no split, no widening, and no float operation on a reported
vector that the uncalibrated model did not already perform.

**Cross-conformal, opt-in (B25).** Split-conformal pays for its band with a
quarter of the frame and the purge: every level, the median and so the CRPS are
fitted on the rows that are left. `calibration="cross_conformal"` is CV+
(Barber, Candes, Ramdas and Tibshirani, 2021) applied to conformalized quantile
regression, done causally inside the one training frame a fold hands over:

* **the reported vector is the full fit's.** Every level is fitted on all of
  the frame's rows exactly as `none` fits them, and the interior levels are
  reported as `none` reports them, bit for bit;
* the frame is split, **by date and never shuffled**, into `calibration_folds`
  contiguous blocks. Each block's **excluding model** is fitted on the other
  blocks' rows less every row inside the registry-derived purge gap on either
  side of it, by `splits.clears_purge` in both directions: a row before the
  block trains only if it clears the gap before the block opens, a row after it
  only if the block's last row clears the gap before that row. A design pair
  trains only if its origin and its target both do, so no pair's target is a
  held-out row or a purged one. The rows it may not train on are **holes** to
  it -- a lag or a GARCH variance that would read one is missing, by the rules
  below -- so an excluding model reads nothing of its block through a feature
  either;
* each held-out row is scored `s = max(Q_lo - y, y - Q_hi)` by its own block's
  excluding model, from the feature row `baseline._feature_index` chooses for
  it, as a calibration row is under `conformal`. A held-out row with no such
  feature row inside the frame -- the frame's first rows, within the gap of its
  start, or before a lag has rows to read -- has no forecast to score and is
  not scored;
* a forecast's band is CV+'s: with `alpha = 1 - (Q_hi level - Q_lo level)` and
  `n` scores, the lower edge is the `floor(alpha (n + 1))`-th smallest of
  `Q_lo_-k(i)(x) - s_i` and the upper the `ceil((1 - alpha)(n + 1))`-th
  smallest of `Q_hi_-k(i)(x) + s_i`, every excluding model read at the
  forecast's own feature row. The full fit's outer levels move to those edges
  by `_calibrated`'s neighbour rule, and the tail knots `predict_stress` reads
  move with them.

Runtime is the full fit plus one fit per block, and every forecast reads each
excluding model once more.

**Lagged spread changes, opt-in (B23).** `spread_change_lags=k` adds `k`
regressors, `spread_change_lag_1` .. `spread_change_lag_k`: the change in
`spread_bps` between consecutive rows, the `j`-th ending `j - 1` rows before the
feature row, so lag 1 is the feature row's spread minus the row before it.

* **Where the prior rows come from.** The forecast interface hands a model one
  feature row, so the rows before it are the training frame's own: the fitted
  model keeps each frame row's date and spread, and reads a feature row's lags
  back by that row's *position* in the frame. The frame is what the fold loop
  handed over, already purged, and the feature row the loop chooses is always
  its last row -- so no row after the feature date is reachable from here at
  all, and a feature row the frame does not carry is refused rather than
  looked up somewhere else.
* **Inside the design, the same rule.** A training row's lags end at that row,
  never at its target: the change *into* the day being forecast is lag 0, and
  it is the target minus the autoregressive term. A calibration row's lags end
  at the feature row `baseline._feature_index` chose for it. One helper,
  `_spread_changes`, reads every one of them.
* **By row, not by calendar day.** A Monday's lag 1 is Friday's change, not a
  Sunday nobody observed.
* **A hole is missing, not bridged.** A row whose `sofr` or `iorb` is `None` has
  no spread, so every change touching it is missing and gets its fitted
  imputation, exactly as a declared regressor carried as `None` does. It is
  never differenced against the last observed row before it.
* **The first `k` rows of a frame start changes and are not design rows.** Their
  lags would reach before the frame, which is not a hole but no data, and
  imputing it would put a column of training means in every fit.

**A GARCH(1,1) variance, opt-in (B24).** `volatility_feature="garch11"` adds one
regressor, `garch11_variance`: the one-step conditional variance of the spread
change, fitted inside the one training frame a fold hands over.

* **The fit.** The innovations are the daily spread changes between consecutive
  fit rows, by row and taken as zero-mean. `f_p`, the variance of the change
  into row `p + 1` forecast at row `p`, is `omega + alpha * e_p + beta *
  f_(p-1)`, where `e_p` is the squared change into row `p` -- or `f_(p-1)`, its
  expectation, where that change touches a hole, and on the frame's first row,
  which has no change into it. `f_(-1)` is the mean squared observed change of
  the fit rows. `(omega, alpha, beta)` maximise the Gaussian quasi-likelihood of
  the fit rows' changes subject to `omega > 0`, `alpha, beta >= 0` and
  `alpha + beta < 1`, by a Nelder-Mead search written here in the standard
  library: the `ml` extra is numpy and scikit-learn, and an optimiser package
  is a dependency this block does not add.
* **Per fold, on the fit rows only.** Nothing is fitted on the panel: the
  fitter is handed one fold's frame and fits there, so two folds with different
  training ends fit different parameters. Under `calibration="conformal"` the
  parameters come from the fit rows alone, and the calibration rows are
  *filtered* with them -- the recursion run on through those rows -- never
  refitted on themselves.
* **The feature at row `t` is `f_t`.** It reads changes at or before `t`, and
  forecasts the change into `t + 1`: for a training row that is the change
  into its target, and it is never an input. A calibration row's variance is
  its feature row's; a forecast's is the feature row's, filtered through the
  fitted frame's own rows by position, the lag columns' rule.
* **Refused, never flattened.** Fewer than `GARCH_MINIMUM_CHANGES` observed
  changes among the fit rows, and a search that does not converge -- including
  a frame whose every observed change is zero, where omega runs to 0 and there
  is no maximum -- raise `ValueError`. A constant-variance column in their
  place would be a feature that says nothing, published under a declaration
  that says it was read.

Absent is the default and is today's gbm, bit for bit.

**An ARX one-step forecast, opt-in (B26).** `arx_feature="declared"` adds one
regressor, `arx_forecast`: the point forecast of `baseline.fit_arx` -- the
repository's one ARX fitter, the model `--model arx` runs -- fitted on gbm's
own declared regressors, exactly the columns `--model arx` gets from the same
`--feature` flags. `declared` is the only value: no new column enters a
declaration, and the purge is already sized over every column the ARX reads.

* **Per fold, on the fit rows only.** The ARX is fitted inside the one training
  frame a fold hands over, on the rows the gbm's own estimators are fitted on:
  the frame under `none`, the fit rows under `conformal`. Two folds with
  different training ends fit two ARXs; nothing is fitted on the panel.
* **The feature at row `t` is the ARX's forecast from `t`.** `FittedArx.
  point_forecast` reads row `t`'s spread and declared regressors and nothing
  else, so the column reads no row after `t`; for a training row that means its
  successor, its target, is never an input. What a training row does share
  with its target is the coefficients, fitted on pairs that include it -- the
  in-sample property the GARCH parameters and every imputation mean here
  already have. A calibration row's forecast is its feature row's, from the fit
  rows' ARX, never refitted; so is a forecast's.
* **Under `cross_conformal`**, each block's excluding model fits its own ARX on
  the one-step pairs whose two rows it may train on -- every pair outside its
  block and the purge gaps around it -- through `fit_arx`'s `origins`, so no
  pair spans the block. Its training rows, its held-out scores and its read of
  a forecast all use that ARX; the full fit's is never lent to it.
* **Refused, never substituted.** The ARX's own refusals are its own: too few
  rows for `fit_arx`'s default minimum, a singular design, a regressor
  unobserved on every row. They propagate as `fit_arx` raises them, and a
  forecast column is never filled in when the fit fails. Integration order
  `d = 0`: the target is a spread level, and the ARX is fitted on levels.

Absent is the default and is today's gbm, bit for bit.

Stdlib plus the `ml` extra, inside functions.
"""

from __future__ import annotations

import math
from bisect import bisect_left, bisect_right
from datetime import date
from fractions import Fraction
from types import MappingProxyType
from typing import Any, List, Mapping, Optional, Sequence, Tuple

from .baseline import (
    SPREAD_COMPONENTS,
    ExceedanceCurves,
    ExceedancePredictor,
    FittedArx,
    _feature_index,
    _raw_regressor,
    _validate_taus_bp,
    fit_arx,
)
from .contract import QUANTILE_LEVELS
from .data import DailyObservation, load_stress_thresholds
from .metrics import _validate_levels
from .splits import (
    LookAheadError,
    clears_purge,
    ensure_strictly_ascending,
    require_purge_days,
)

__all__ = [
    "ARX_FEATURES",
    "CALIBRATIONS",
    "DEFAULT_CALIBRATION_FOLDS",
    "DEFAULT_CALIBRATION_SHARE",
    "GARCH_MINIMUM_CHANGES",
    "VOLATILITY_FEATURES",
    "MissingMLExtraError",
    "FittedGradientBoostedQuantiles",
    "fit_gradient_boosted_quantiles",
    "gbm_exceedance",
]

#: The level the point forecast is read at. The contract grid carries it, and a
#: grid that does not is refused rather than given a made-up centre: with an
#: even number of levels there is no middle entry of the rearranged vector, and
#: averaging the two straddling it would report a centre that no fit produced.
_MEDIAN_LEVEL = 0.50

#: The seed every fit uses unless a caller names another. The *value* is
#: arbitrary; that it is fixed is not. See the module docstring on early
#: stopping: an unseeded fit above 10 000 rows is not reproducible, and the
#: published records this repository keeps are re-scored against their own
#: figures by `tests/test_generated_results.py`.
DEFAULT_RANDOM_STATE = 0


#: How much of a row's own declared band is used as a tail when the fitted
#: residual range is narrower than that band. A fifth on each side puts the
#: outer knots one declared level-step beyond the 0.05 and 0.95 knots at
#: constant density, which is the least the knot set can be widened by and
#: still be increasing.
_TAIL_SHARE = 0.2

#: The tail width when a row's band has zero width --- every fit agreeing to
#: the last bit. Positive so the knot set is still increasing; small enough
#: that it is not a distribution anybody would read as informative.
_MINIMUM_TAIL = 1e-9

#: The band calibrations a fit can be asked for. `none` first: it is the
#: default, and the model every published record was produced with. See the
#: module docstring for `conformal` and `cross_conformal`.
CALIBRATIONS = ("none", "conformal", "cross_conformal")

#: The share of a training frame held out as calibration rows when
#: `calibration="conformal"` names none. A quarter: at `--minimum-history 61`
#: the first fold still has more calibration rows than the conformal quantile
#: needs to be finite, and three quarters of the frame are left to fit on.
DEFAULT_CALIBRATION_SHARE = 0.25

#: The contiguous date blocks `calibration="cross_conformal"` splits a training
#: frame into when it names none. Five: each excluding model is fitted on four
#: fifths of the frame less the purge, and a forecast costs five more reads.
DEFAULT_CALIBRATION_FOLDS = 5

#: The volatility features gbm can be built with. See the module docstring.
VOLATILITY_FEATURES = ("garch11",)

#: The design name of the `garch11` column.
_GARCH_COLUMN = "garch11_variance"

#: The ARX features gbm can be built with. See the module docstring: the ARX is
#: fitted on the model's own declared regressors, and nothing else is offered.
ARX_FEATURES = ("declared",)

#: The design name of the ARX forecast column.
_ARX_COLUMN = "arx_forecast"

#: The fewest observed spread changes among a frame's fit rows a GARCH(1,1) is
#: fitted from: ten per fitted parameter. Below it the three parameters are
#: pinned by a handful of squared changes and the search converges to whichever
#: of them was largest. At `--minimum-history 61` under `--calibration
#: conformal` and a six-day gap the first fold's fit rows still carry more.
GARCH_MINIMUM_CHANGES = 30

#: The Nelder-Mead iteration cap. A search still moving after this many steps
#: is refused, not read off where it stopped.
_GARCH_MAX_ITERATIONS = 2000

#: Convergence: the simplex's criterion values agree to this share of the best
#: one, and its vertices to this much in `(log(omega / f_-1), alpha, beta)`.
_GARCH_TOLERANCE = 1e-8


def _band_probability(levels: Sequence[float]) -> Fraction:
    """The declared band's span, exactly: `Fraction` of the outer two levels.

    Exact because it feeds a ceiling. `0.95 - 0.05` is `0.8999999999999999` in
    floating point, and a rank computed as `ceil(q * (n + 1))` from a `q` one
    representable step off can land one position away from the rank the
    guarantee is stated for.
    """

    return Fraction(repr(float(levels[-1]))) - Fraction(repr(float(levels[0])))


def _minimum_calibration_rows(levels: Sequence[float]) -> int:
    """The fewest calibration scores at which the conformal quantile is finite.

    The rank is `ceil(q (n + 1))` for band probability `q`, and it names a
    score only while it is at most `n`, which holds exactly when
    `n >= q / (1 - q)`. Nine for the declared `0.05`-`0.95` band. Below it the
    honest widening is infinite, and a finite one would be a band claiming a
    coverage its calibration cannot support.
    """

    q = _band_probability(levels)
    return math.ceil(q / (1 - q))


def _spread_change_names(lags: int) -> Tuple[str, ...]:
    """The lag columns' design names, in lag order: lag 1 first."""

    return tuple(f"spread_change_lag_{lag}" for lag in range(1, lags + 1))


def _observed_spread(row: DailyObservation, label: str) -> Optional[float]:
    """`row.spread_bps`, or `None` where either leg of it is a hole.

    A leg absent from the row is `_raw_regressor`'s refusal, as it is for every
    other column this model reads; a leg carried as `None` makes the spread
    unobserved, and that is a missing change, not a zero and not yesterday's.
    """

    for component in SPREAD_COMPONENTS:
        observed = _raw_regressor(
            row,
            component,
            label,
            role="a leg of the spread whose lagged changes this model reads",
        )
        if observed is None:
            return None
    return float(row.spread_bps)


def _spread_changes(
    spreads: Sequence[Optional[float]], position: int, lags: int, label: str
) -> List[Optional[float]]:
    """The `lags` spread changes ending at `spreads[position]`, lag 1 first.

    Lag `j` is `spreads[position - j + 1] - spreads[position - j]`: by row, and
    never reaching past `position`. A change with a hole at either end is
    `None`. Every lag this model reads -- a training row's, a calibration
    row's, a forecast's -- comes through here.
    """

    if position < lags:
        raise ValueError(
            f"the lagged spread changes of the {label} need {lags} rows before "
            f"it and its frame has {position}; a lag reaching before the "
            f"frame's first row has no row to read, and a negative position "
            f"would wrap to the frame's latest rows and read them as its oldest"
        )
    changes: List[Optional[float]] = []
    for lag in range(1, lags + 1):
        later = spreads[position - lag + 1]
        earlier = spreads[position - lag]
        changes.append(None if later is None or earlier is None else later - earlier)
    return changes


def _squared_changes(spreads: Sequence[Optional[float]]) -> List[Optional[float]]:
    """The squared change into each row, `None` at the first row and at a hole."""

    squares: List[Optional[float]] = [None]
    for earlier, later in zip(spreads[:-1], spreads[1:]):
        if later is None or earlier is None:
            squares.append(None)
        else:
            change = later - earlier
            squares.append(change * change)
    return squares


def _garch_variances(
    squares: Sequence[Optional[float]],
    parameters: Tuple[float, float, float],
    initial: float,
) -> List[float]:
    """`f_p` for every row `p`: the variance of the change into row `p + 1`.

    `f_p = omega + alpha * e_p + beta * f_(p-1)`, with `e_p` row `p`'s own
    squared change, or `f_(p-1)` where it has none, and `f_(-1) = initial`. By
    construction `f_p` reads `squares[: p + 1]` and nothing after: the one
    recursion the fit's likelihood, the training design, the calibration rows
    and a forecast all read.
    """

    omega, alpha, beta = parameters
    variances: List[float] = []
    previous = initial
    for square in squares:
        shock = previous if square is None else square
        previous = omega + alpha * shock + beta * previous
        variances.append(previous)
    return variances


def _garch_criterion(
    squares: Sequence[Optional[float]],
    parameters: Tuple[float, float, float],
    initial: float,
) -> float:
    """Twice the negative Gaussian quasi-log-likelihood, constants dropped.

    Each observed change into row `p + 1` is scored against `f_p`, the variance
    forecast at the row before it.
    """

    total = 0.0
    variances = _garch_variances(squares, parameters, initial)
    for variance, square in zip(variances, squares[1:]):
        if square is not None:
            total += math.log(variance) + square / variance
    return total


def _nelder_mead(
    criterion: Any, start: Sequence[float], steps: Sequence[float]
) -> Tuple[Tuple[float, ...], bool]:
    """Minimise `criterion` from `start`; return the best vertex and convergence.

    The Lagarias et al. (1998) moves -- reflection 1, expansion 2, contraction
    and shrink 1/2 -- with ties kept in vertex order, so a search is
    deterministic. Converged when the simplex's values agree to
    `_GARCH_TOLERANCE` of the best and its vertices to `_GARCH_TOLERANCE`;
    otherwise, after `_GARCH_MAX_ITERATIONS`, not.
    """

    dimension = len(start)
    simplex = [tuple(float(value) for value in start)]
    for axis, step in enumerate(steps):
        simplex.append(
            tuple(
                value + step if index == axis else value
                for index, value in enumerate(simplex[0])
            )
        )
    values = [criterion(vertex) for vertex in simplex]

    def between(origin, target, weight):
        return tuple(o + weight * (t - o) for o, t in zip(origin, target))

    for _ in range(_GARCH_MAX_ITERATIONS):
        order = sorted(range(dimension + 1), key=values.__getitem__)
        simplex = [simplex[index] for index in order]
        values = [values[index] for index in order]
        best = simplex[0]
        if values[-1] - values[0] <= _GARCH_TOLERANCE * (1.0 + abs(values[0])) and all(
            abs(coordinate - anchor) <= _GARCH_TOLERANCE
            for vertex in simplex[1:]
            for coordinate, anchor in zip(vertex, best)
        ):
            return best, True
        centroid = tuple(
            sum(vertex[axis] for vertex in simplex[:-1]) / dimension
            for axis in range(dimension)
        )
        worst = simplex[-1]
        reflected = between(centroid, worst, -1.0)
        reflected_value = criterion(reflected)
        if reflected_value < values[0]:
            expanded = between(centroid, worst, -2.0)
            expanded_value = criterion(expanded)
            if expanded_value < reflected_value:
                simplex[-1], values[-1] = expanded, expanded_value
            else:
                simplex[-1], values[-1] = reflected, reflected_value
            continue
        if reflected_value < values[-2]:
            simplex[-1], values[-1] = reflected, reflected_value
            continue
        if reflected_value < values[-1]:
            contracted = between(centroid, reflected, 0.5)
            contracted_value = criterion(contracted)
            accepted = contracted_value <= reflected_value
        else:
            contracted = between(centroid, worst, 0.5)
            contracted_value = criterion(contracted)
            accepted = contracted_value < values[-1]
        if accepted:
            simplex[-1], values[-1] = contracted, contracted_value
            continue
        simplex = [best] + [between(best, vertex, 0.5) for vertex in simplex[1:]]
        values = [values[0]] + [criterion(vertex) for vertex in simplex[1:]]
    return simplex[0], False


def _fit_garch11(
    spreads: Sequence[Optional[float]], label: str
) -> Tuple[Tuple[float, float, float], float]:
    """`((omega, alpha, beta), f_-1)` fitted on `spreads`, or refuse.

    `spreads` are the fit rows' and nothing else; the caller filters any later
    row with what this returns. The search runs over `(log(omega / f_-1),
    alpha, beta)`, scale-free in the spread's units, from a persistent start
    `(0.05, 0.05, 0.90)`; a point outside the constraints scores infinity.
    """

    squares = _squared_changes(spreads)
    observed = [square for square in squares if square is not None]
    if len(observed) < GARCH_MINIMUM_CHANGES:
        raise ValueError(
            f"volatility_feature garch11 needs at least {GARCH_MINIMUM_CHANGES} "
            f"observed spread changes among the {label}, got {len(observed)}; "
            f"three parameters fitted from fewer are pinned by a handful of "
            f"squared changes, not estimated"
        )
    initial = sum(observed) / len(observed)
    if not initial > 0.0:
        raise ValueError(
            f"the GARCH(1,1) fit on the {label} did not converge: every one of "
            f"its {len(observed)} observed spread changes is zero, so omega runs "
            f"to 0 and the quasi-likelihood has no maximum. Refused rather than "
            f"read as a constant variance"
        )

    def criterion(point: Tuple[float, ...]) -> float:
        scale, alpha, beta = point
        if not (alpha >= 0.0 and beta >= 0.0 and alpha + beta < 1.0):
            return math.inf
        if not -700.0 < scale < 700.0:
            return math.inf
        return _garch_criterion(
            squares, (initial * math.exp(scale), alpha, beta), initial
        )

    point, converged = _nelder_mead(
        criterion, (math.log(0.05), 0.05, 0.90), (0.5, 0.05, 0.05)
    )
    if not converged:
        raise ValueError(
            f"the GARCH(1,1) fit on the {label} did not converge in "
            f"{_GARCH_MAX_ITERATIONS} Nelder-Mead iterations; refused rather "
            f"than read off where the search stopped, and never replaced by a "
            f"constant variance"
        )
    scale, alpha, beta = point
    return (initial * math.exp(scale), alpha, beta), initial


def _design(
    row: DailyObservation,
    regressors: Sequence[str],
    imputations: Mapping[str, float],
    label: str,
    changes: Sequence[Optional[float]] = (),
    variance: Optional[float] = None,
    arx: Optional[FittedArx] = None,
) -> List[float]:
    """One row as the design reads it: the spread, each regressor, each lag, the variance, the ARX.

    A regressor carried as `None` gets its fitted imputation; one missing from
    the row is `_raw_regressor`'s refusal. A missing spread change gets its
    lag's imputation, by the same rule. The GARCH variance, when there is one,
    is never missing: `_garch_variances` carries a hole forward by its
    expectation. The ARX forecast is `arx.point_forecast(row)`, off this row
    alone, under the ARX's own imputations. The one spelling the fit, the
    calibration scores and `FittedGradientBoostedQuantiles.design_row` share.
    """

    values = [float(row.spread_bps)]
    for name in regressors:
        observed = _raw_regressor(row, name, label)
        values.append(imputations[name] if observed is None else observed)
    for name, change in zip(_spread_change_names(len(changes)), changes):
        values.append(imputations[name] if change is None else change)
    if variance is not None:
        values.append(variance)
    if arx is not None:
        values.append(arx.point_forecast(row))
    return values


def _calibrated(vector: Sequence[float], widening: float) -> Tuple[float, ...]:
    """The rearranged vector with its outer two levels moved by `widening`.

    Down at the bottom, up at the top, interior untouched. A negative widening
    narrows the band, and an outer level it would carry past its neighbour
    stops at that neighbour: the vector stays non-decreasing without re-sorting,
    which would move a calibrated value onto an interior level.
    """

    return _banded(vector, vector[0] - widening, vector[-1] + widening)


def _banded(vector: Sequence[float], lower: float, upper: float) -> Tuple[float, ...]:
    """The rearranged vector with its outer two levels moved to `lower` and `upper`.

    `_calibrated`'s neighbour rule, stated once: an outer level that would pass
    its neighbour stops at it, and the interior is untouched.
    """

    values = list(vector)
    values[0] = min(lower, values[1])
    values[-1] = max(upper, values[-2])
    return tuple(values)


def _cross_conformal_edges(
    lows: Sequence[float], highs: Sequence[float], levels: Sequence[float]
) -> Tuple[float, float]:
    """CV+'s band edges from `Q_lo_-k(i)(x) - s_i` and `Q_hi_-k(i)(x) + s_i`.

    The `floor(alpha (n + 1))`-th smallest low and the `ceil((1 - alpha)(n +
    1))`-th smallest high, `alpha` exact by `_band_probability`. Both ranks name
    an entry exactly when `n >= _minimum_calibration_rows(levels)`, which the
    fitter refuses below.
    """

    q = _band_probability(levels)
    count = len(lows)
    lower = sorted(lows)[math.floor((1 - q) * (count + 1)) - 1]
    upper = sorted(highs)[math.ceil(q * (count + 1)) - 1]
    return lower, upper


class _ExcludingModel:
    """One cross-conformal block: the model fitted without it, and its scores.

    * `estimators`, `imputations`, `garch_parameters`,
      `garch_initial_variance`, `arx` --- the fit on the rows outside the block
      and its purge gaps, in `FittedGradientBoostedQuantiles`' own fields'
      meaning.
    * `held_out_start`, `held_out_end` --- the block's first and last dates.
    * `training_dates` --- every row a design pair of this fit read, as an
      origin or as a target, ascending. Carried so the purge can be checked
      against a calendar rather than taken on trust.
    * `scored_dates`, `scores` --- the held-out rows this model scored, and
      their scores, in date order.
    """

    __slots__ = (
        "arx",
        "estimators",
        "garch_initial_variance",
        "garch_parameters",
        "held_out_end",
        "held_out_start",
        "imputations",
        "scored_dates",
        "scores",
        "training_dates",
    )

    def __init__(
        self,
        *,
        estimators: Sequence[Any],
        imputations: Mapping[str, float],
        garch_parameters: Optional[Tuple[float, float, float]],
        garch_initial_variance: Optional[float],
        held_out_start: date,
        held_out_end: date,
        training_dates: Sequence[date],
        scored_dates: Sequence[date],
        scores: Sequence[float],
        arx: Optional[FittedArx] = None,
    ) -> None:
        self.arx: Optional[FittedArx] = arx
        self.estimators: Tuple[Any, ...] = tuple(estimators)
        self.imputations: Mapping[str, float] = MappingProxyType(dict(imputations))
        self.garch_parameters = garch_parameters
        self.garch_initial_variance = garch_initial_variance
        self.held_out_start: date = held_out_start
        self.held_out_end: date = held_out_end
        self.training_dates: Tuple[date, ...] = tuple(training_dates)
        self.scored_dates: Tuple[date, ...] = tuple(scored_dates)
        self.scores: Tuple[float, ...] = tuple(scores)


class MissingMLExtraError(ValueError):
    """The `ml` extra is not installed on this interpreter.

    A `ValueError` subclass, not a bare `ImportError`, because the command-line
    dispatcher catches `(OSError, ValueError)` and prints the message: a caller
    who typed `--model gbm` on a checkout without the extra should be told to
    install it and get exit 2, not a traceback from four frames down.
    """


def _estimator_class() -> Any:
    """`HistGradientBoostingRegressor`, imported here and nowhere else.

    The import lives inside a function because
    `tests/test_dependency_boundary.py` requires it to --- see the module
    docstring. It is wrapped rather than bare so the absence of the extra is a
    refusal in this repository's vocabulary instead of an `ImportError` from
    inside a fit.
    """

    try:
        from sklearn.ensemble import HistGradientBoostingRegressor
    except ImportError as error:  # pragma: no cover - exercised without the extra
        raise MissingMLExtraError(
            "the gradient-boosted quantile model needs the optional 'ml' extra "
            "(numpy and scikit-learn); install it with `pip install -e \".[ml]\"`. "
            "Every other model in this repository is standard-library only and "
            "runs without it"
        ) from error
    return HistGradientBoostingRegressor


def _library_versions() -> Mapping[str, str]:
    """The numpy and scikit-learn versions this process fits with.

    Read off the **imported modules' own `__version__`**, not off
    `importlib.metadata`: the metadata answers what an installer recorded in a
    `site-packages` directory, and the module answers what is actually loaded
    in this interpreter. The two agree on a clean install and disagree exactly
    when it matters -- a second copy earlier on `sys.path`, an editable build,
    a module already imported before an environment changed under it -- and a
    record's provenance is a claim about the code that fitted, which is the
    module.

    Called from `fit_gradient_boosted_quantiles` after `_estimator_class`, so
    the extra is known to be present and a caller without it has already been
    refused in this repository's vocabulary. The imports are inside the
    function for the reason every third-party import in this module is; see
    the module docstring.
    """

    import numpy
    import sklearn

    return MappingProxyType(
        {"numpy": numpy.__version__, "scikit-learn": sklearn.__version__}
    )


class FittedGradientBoostedQuantiles:
    """One gradient-boosted fit per contract level, rearranged into a law.

    Fitted state, all of it set in `fit_gradient_boosted_quantiles` and nowhere
    else:

    * `regressors` --- the ordered exogenous names this model was fitted on,
      carried for the reason `FittedArx` carries them: a model that cannot say
      what it read cannot be audited, and two models compared on quietly
      different regressor sets are not being compared.
    * `imputations` --- the training-window mean of each regressor's observed
      values, over the *origin* rows. The one transform with learned parameters,
      and the same one `fit_arx` fits.
    * `_estimators` --- one fitted estimator per entry of `levels`, in that
      order.
    * `_residuals` --- the sorted training residuals about this model's own
      rearranged median. This is the sample `predict_stress` reads for the two
      tail knots of its law; see `predict_stress`.
    * `cutoff` --- the last date the training frame was allowed to contain, with
      the same meaning and the same `trained_beyond` question as persistence.
    * `ml_libraries` --- `{"numpy": ..., "scikit-learn": ...}`, the versions
      of the modules this model was fitted with, read by `_library_versions`
      at the fit. Required and undefaulted: this is the one fitted model in the
      package that reached a third-party library, and every record a run of it
      publishes names those versions under `provenance.ml_libraries` --- see
      `baseline._ml_libraries` and `baseline._run_provenance`. A model built
      without them would publish a record that silently lost that key.
    * `calibration`, `calibration_share`, `widening` --- which band calibration
      this model was built with, the share of its frame held out for it
      (`None` under `none`), and the amount the outer two levels were moved
      by (`0.0` under `none`). See the module docstring.
    * `fit_end`, `calibration_start`, `calibration_end` --- the last row the
      estimators were fitted on, and the first and last calibration rows
      (`None` under `none`, where the fit rows are the whole frame). Carried
      so a reader can check the purge between the two slices against a
      calendar rather than take it on trust. Under `cross_conformal` the fit
      rows are the whole frame and the calibration dates are the first and
      last held-out rows scored.
    * `calibration_folds`, `calibration_blocks` --- under `cross_conformal`,
      how many blocks the frame was split into and one `_ExcludingModel` per
      block, in date order (`None` and empty otherwise).
    * `spread_change_lags`, `_history_dates`, `_history_spreads` --- how many
      lagged spread changes the design carries (`None` when it carries none),
      and the training frame's own dates and spreads, which are the only rows
      a feature row's lags are read back from. See the module docstring.
    * `volatility_feature`, `garch_parameters`, `garch_initial_variance` ---
      the volatility feature the design carries (`None` when it carries none),
      the `(omega, alpha, beta)` fitted on the fit rows, and `f_-1`, the fit
      rows' mean squared observed change the recursion starts from. A feature
      row's variance is filtered through the same frame rows its lags are read
      from.
    * `arx_feature`, `arx` --- the ARX feature the design carries (`None` when
      it carries none) and the `baseline.FittedArx` fitted on the fit rows,
      whose point forecast from a feature row is that row's column.

    **What `residuals` is here, and what it is not.** For persistence and the
    ARX the fitted residual sample *is* the whole law: `predict` is an anchor
    plus a residual quantile and `predict_stress` inverts the same sample, so
    the predictive distribution is a location shift of one fixed shape. This
    model is not that. Its band is conditional --- `predict` reads five fits, so
    the *width* of the predictive distribution moves with the feature row and
    not only its centre --- and no row-independent sample can represent a shape
    that moves. So `residuals` is what the name says and no more: the training
    residuals about the model's own centre. `predict_stress` reads it for where
    the law runs out, and reads the rearranged quantile vector for everything
    between.

    A feature row missing a declared regressor raises `MissingRegressorError`; a
    feature row carrying it as `None` gets the fitted mean. Neither becomes
    `0.0`. Both behaviours are `baseline._raw_regressor`'s, reached rather than
    reimplemented.

    `_last_law` is the one slot that is **not** fitted state and is not set by
    the fitter: it is `_shared_law`'s one-row memo, written by whichever of
    `law_knots` and `predict_stress` asks about a row first so that the other
    reads the same evaluation rather than a second one. Nothing it holds is
    reported, and clearing it at any moment changes no answer --- only how many
    times the estimators were called for that answer. See `_shared_law`.
    """

    __slots__ = (
        "_estimators",
        "_history_dates",
        "_history_spreads",
        "_last_law",
        "_residuals",
        "arx",
        "arx_feature",
        "calibration",
        "calibration_blocks",
        "calibration_end",
        "calibration_folds",
        "calibration_share",
        "calibration_start",
        "cutoff",
        "fit_end",
        "garch_initial_variance",
        "garch_parameters",
        "imputations",
        "levels",
        "ml_libraries",
        "random_state",
        "regressors",
        "spread_change_lags",
        "volatility_feature",
        "widening",
    )

    def __init__(
        self,
        estimators: Sequence[Any],
        regressors: Sequence[str],
        imputations: Mapping[str, float],
        residuals: Sequence[float],
        cutoff: date,
        levels: Sequence[float] = QUANTILE_LEVELS,
        random_state: int = DEFAULT_RANDOM_STATE,
        *,
        ml_libraries: Mapping[str, str],
        calibration: str = "none",
        calibration_share: Optional[float] = None,
        widening: float = 0.0,
        fit_end: Optional[date] = None,
        calibration_start: Optional[date] = None,
        calibration_end: Optional[date] = None,
        spread_change_lags: Optional[int] = None,
        history: Sequence[Tuple[date, Optional[float]]] = (),
        volatility_feature: Optional[str] = None,
        garch_parameters: Optional[Tuple[float, float, float]] = None,
        garch_initial_variance: Optional[float] = None,
        calibration_folds: Optional[int] = None,
        calibration_blocks: Sequence[_ExcludingModel] = (),
        arx_feature: Optional[str] = None,
        arx: Optional[FittedArx] = None,
    ) -> None:
        self.arx_feature: Optional[str] = arx_feature
        self.arx: Optional[FittedArx] = arx
        self.calibration_folds: Optional[int] = calibration_folds
        self.calibration_blocks: Tuple[_ExcludingModel, ...] = tuple(calibration_blocks)
        self.volatility_feature: Optional[str] = volatility_feature
        self.garch_parameters: Optional[Tuple[float, float, float]] = (
            None if garch_parameters is None else tuple(garch_parameters)
        )
        self.garch_initial_variance: Optional[float] = garch_initial_variance
        self.spread_change_lags: Optional[int] = spread_change_lags
        self._history_dates: Tuple[date, ...] = tuple(when for when, _ in history)
        self._history_spreads: Tuple[Optional[float], ...] = tuple(
            spread for _, spread in history
        )
        self.ml_libraries: Mapping[str, str] = MappingProxyType(dict(ml_libraries))
        self.calibration: str = calibration
        self.calibration_share: Optional[float] = calibration_share
        self.widening: float = float(widening)
        self.fit_end: date = cutoff if fit_end is None else fit_end
        self.calibration_start: Optional[date] = calibration_start
        self.calibration_end: Optional[date] = calibration_end
        self.regressors: Tuple[str, ...] = tuple(regressors)
        self._estimators: Tuple[Any, ...] = tuple(estimators)
        self.imputations: Mapping[str, float] = MappingProxyType(
            {
                name: float(imputations[name])
                for name in self.regressors
                + _spread_change_names(spread_change_lags or 0)
            }
        )
        self._residuals: Tuple[float, ...] = tuple(sorted(float(r) for r in residuals))
        self._last_law: Optional[
            Tuple[
                Tuple[date, Tuple[Tuple[str, Optional[float]], ...]],
                Tuple[Tuple[float, ...], Tuple[float, ...]],
            ]
        ] = None
        self.cutoff: date = cutoff
        self.levels: Tuple[float, ...] = _validate_levels(levels)
        self.random_state: int = int(random_state)
        if len(self._estimators) != len(self.levels):
            raise ValueError(
                f"{len(self._estimators)} fitted estimators against "
                f"{len(self.levels)} declared levels; one fit per level is what "
                f"makes the reported vector a quantile vector"
            )

    def __repr__(self) -> str:  # pragma: no cover - diagnostic only
        return (
            f"FittedGradientBoostedQuantiles(cutoff={self.cutoff.isoformat()}, "
            f"regressors={list(self.regressors)}, "
            f"residuals={len(self._residuals)})"
        )

    @property
    def design_names(self) -> Tuple[str, ...]:
        """The design column order. `design_row(row)[i]` is column `[i]`.

        No intercept: a tree ensemble has no coefficient for one, and reporting
        a column the model does not read would put `features_read` --- which is
        derived from this --- out of step with the fit.

        The lag columns come after the regressors, lag 1 first, then the GARCH
        variance, and the ARX forecast last.
        """

        return (
            ("spread_bps",)
            + self.regressors
            + _spread_change_names(self.spread_change_lags or 0)
            + ((_GARCH_COLUMN,) if self.volatility_feature is not None else ())
            + ((_ARX_COLUMN,) if self.arx_feature is not None else ())
        )

    @property
    def residuals(self) -> Tuple[float, ...]:
        """The training residuals about this model's own centre, ascending."""

        return self._residuals

    @property
    def features_read(self) -> Tuple[str, ...]:
        """Every panel column this model reads off a feature row.

        Derived from `design_names` rather than rebuilt from `regressors`, for
        the reason `FittedArx.features_read` is: `design_row` reads the row in
        `design_names` order, so anything that column order gains this answer
        gains too.

        **Except the lag columns, the GARCH variance and the ARX forecast, which
        are not panel columns.** Each is read off `spread_bps` -- the ARX
        forecast off `spread_bps` and the declared regressors -- on rows at or
        before the feature row, and every one of those is already here. Naming
        `spread_change_lag_1`, `garch11_variance` or `arx_forecast` would ask
        the purge check to find a source for a column no source ingests.
        """

        return self.design_names[: 1 + len(self.regressors)]

    @property
    def model_settings(self) -> Mapping[str, Any]:
        """The calibration settings a record names, keyed as the command line spells them.

        Read by `baseline._model_settings`, which cannot import this module and
        so cannot ask `isinstance`. Empty under `calibration="none"` -- absent,
        not `"none"` -- so a record of the uncalibrated model declares exactly
        what every gbm record published before calibration existed declares.
        `spread_change_lags`, `volatility_feature` and `arx_feature` by the
        same rule: named when set, absent when not. Each calibration names its own setting and
        only its own: `calibration_share` for `conformal`, `calibration_folds`
        for `cross_conformal`.
        """

        settings: dict = {}
        if self.calibration == "conformal":
            settings["calibration"] = self.calibration
            settings["calibration_share"] = self.calibration_share
        elif self.calibration == "cross_conformal":
            settings["calibration"] = self.calibration
            settings["calibration_folds"] = self.calibration_folds
        if self.spread_change_lags is not None:
            settings["spread_change_lags"] = self.spread_change_lags
        if self.volatility_feature is not None:
            settings["volatility_feature"] = self.volatility_feature
        if self.arx_feature is not None:
            settings["arx_feature"] = self.arx_feature
        return MappingProxyType(settings)

    def trained_beyond(self, feature_row: DailyObservation) -> bool:
        """Was this model fitted on rows dated after `feature_row`?"""

        return feature_row.date < self.cutoff

    def design_row(self, feature_row: DailyObservation) -> Tuple[float, ...]:
        """The feature row as this model reads it, in `design_names` order.

        With lags, the rows before `feature_row` are the fitted frame's, found
        by the position of `feature_row`'s date in it; the feature row's own
        spread ends lag 1. A row the frame does not carry is refused: it has no
        position in the frame, and the nearest one would hand it another row's
        lags.

        The GARCH variance by the same rule: the recursion is run with the
        fitted parameters through the frame's rows before `feature_row` and
        then `feature_row`'s own spread, and its last value is the column.

        The ARX forecast is the fitted ARX's point forecast from `feature_row`,
        which reads that row and no other.
        """

        return self._design_row(
            feature_row,
            self.imputations,
            self.garch_parameters,
            self.garch_initial_variance,
            self.arx,
        )

    def _design_row(
        self,
        feature_row: DailyObservation,
        imputations: Mapping[str, float],
        garch_parameters: Optional[Tuple[float, float, float]],
        garch_initial_variance: Optional[float],
        arx: Optional[FittedArx] = None,
    ) -> Tuple[float, ...]:
        """`design_row` under one fit's imputations, GARCH parameters and ARX.

        The full fit's, or an excluding model's: the frame's rows are the
        history either way, because a forecast's inputs are every row at or
        before its feature row, and only what a fit *learned* differs.
        """

        changes: Sequence[Optional[float]] = ()
        variance: Optional[float] = None
        lags = self.spread_change_lags
        if lags is not None or self.volatility_feature is not None:
            position = bisect_left(self._history_dates, feature_row.date)
            if (
                position == len(self._history_dates)
                or self._history_dates[position] != feature_row.date
            ):
                raise ValueError(
                    f"feature row for {feature_row.date} is not a row of the "
                    f"frame this model was fitted on "
                    f"({self._history_dates[0]}..{self._history_dates[-1]}); its "
                    f"lagged spread changes and its GARCH variance are read off "
                    f"that frame's own rows by position, and a row the frame "
                    f"does not carry has none"
                )
            spreads = self._history_spreads[:position] + (
                _observed_spread(feature_row, "feature row"),
            )
            if lags is not None:
                changes = _spread_changes(
                    spreads, position, lags, f"feature row for {feature_row.date}"
                )
            if self.volatility_feature is not None:
                variance = _garch_variances(
                    _squared_changes(spreads),
                    garch_parameters,
                    garch_initial_variance,
                )[position]
        return tuple(
            _design(
                feature_row,
                self.regressors,
                imputations,
                "feature row",
                changes,
                variance,
                arx,
            )
        )

    def _quantile_vector(self, design_row: Sequence[float]) -> Tuple[float, ...]:
        """One design row's rearranged quantile vector. See `_rearranged`."""

        return _rearranged(self._estimators, [design_row])[0]

    def point_forecast(self, feature_row: DailyObservation) -> float:
        """The rearranged median: the centre the reported quantiles agree on.

        Read out of `predict`'s own vector rather than off the `0.50` estimator
        directly. The two differ exactly when that estimator crossed one of its
        neighbours, and in that case the estimator's value is not the middle of
        the distribution this model reports.
        """

        return self.predict(feature_row)[self.levels.index(_MEDIAN_LEVEL)]

    def predict(self, feature_row: DailyObservation) -> Tuple[float, ...]:
        """One predicted spread quantile per declared level, in declared order.

        Non-decreasing by construction: `_quantile_vector` sorts, and
        `_calibrated` stops an outer level at its neighbour. A zero widening --
        every uncalibrated model -- touches nothing, so no reported value moves
        by so much as the sign of a zero.
        """

        return self._reported(feature_row)[0]

    def _reported(
        self, feature_row: DailyObservation
    ) -> Tuple[Tuple[float, ...], float, float]:
        """The reported vector, and how far its lower and upper edges were moved out.

        The full fit's rearranged vector in every case; a calibration moves only
        its two outer levels. Under `cross_conformal` the edges are CV+'s, read
        off every excluding model at this feature row.
        """

        vector = self._quantile_vector(self.design_row(feature_row))
        if self.calibration == "cross_conformal":
            lows: List[float] = []
            highs: List[float] = []
            for block in self.calibration_blocks:
                if not block.scores:
                    continue
                excluded = _rearranged(
                    block.estimators,
                    [
                        self._design_row(
                            feature_row,
                            block.imputations,
                            block.garch_parameters,
                            block.garch_initial_variance,
                            block.arx,
                        )
                    ],
                )[0]
                lows.extend(excluded[0] - score for score in block.scores)
                highs.extend(excluded[-1] + score for score in block.scores)
            lower, upper = _cross_conformal_edges(lows, highs, self.levels)
            return _banded(vector, lower, upper), vector[0] - lower, upper - vector[-1]
        if not self.widening:
            return vector, 0.0, 0.0
        return _calibrated(vector, self.widening), self.widening, self.widening

    def _law(self, feature_row: DailyObservation) -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
        """The predictive law for one row, as `(values, levels)` knots.

        `values` is strictly ascending except where two fits agree exactly, and
        `levels` runs `0.0 .. 1.0`. The interior knots are the rearranged
        quantile vector at the declared levels; the two outer knots are where
        the law runs out.

        **The outer knots are the fitted residual range about this row's
        centre.** The model's own evidence about how far the target strays from
        the centre it predicts is its training residual sample, so
        `anchor + min(residuals)` and `anchor + max(residuals)` are where its
        mass stops --- no Gaussian tail, no parametric family, no smoothing, for
        the reason `climatology_exceedance` gives at length. They are widened,
        and only widened, when a row's own declared band would otherwise escape
        them: a knot set that is not increasing is not a distribution, and a
        band wider than the residual range is the model saying this row is
        unusual, which is not something to clip away. `_TAIL_SHARE` of the
        band's own width is the width used then.

        Under a calibration the residual range moves out with the band, by the
        same widening, so the tail knots stay where the calibrated band puts the
        law's edges rather than where the in-sample fit did. Under
        `cross_conformal` each tail moves by as much as its own edge did.
        """

        interior, down, up = self._reported(feature_row)
        anchor = interior[self.levels.index(_MEDIAN_LEVEL)]
        pad = max(_TAIL_SHARE * (interior[-1] - interior[0]), _MINIMUM_TAIL)
        bottom = anchor + self._residuals[0]
        top = anchor + self._residuals[-1]
        if down or up:
            bottom -= down
            top += up
        low = bottom if bottom < interior[0] else interior[0] - pad
        high = top if top > interior[-1] else interior[-1] + pad
        return (low,) + interior + (high,), (0.0,) + self.levels + (1.0,)

    def _shared_law(
        self, feature_row: DailyObservation
    ) -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
        """`_law` for one row, evaluated **once** however many callers ask.

        Both `law_knots` and `predict_stress` come through here, and that is the
        point: a record that carries the knots beside the probabilities read off
        them has to be able to say the two came from one evaluation of one fit.
        Two evaluations of a deterministic fit agree, so nothing a caller can
        assert afterwards distinguishes "derived" from "re-derived" --- the
        distinction is in the call graph or it is nowhere, which is why it is
        built here rather than checked downstream.

        A memo of one row, keyed on the row's date and its columns, because a
        scoring job walks rows in order and asks about each one twice. The key
        is compared by value, so a row rebuilt from the same numbers hits and a
        row carrying a `NaN` column misses forever; a miss costs an extra
        evaluation and changes no answer, which is the direction a cache is
        allowed to be wrong in. A failed evaluation is not memoised: the
        refusal propagates before the slot is written.
        """

        key = (
            feature_row.date,
            tuple(sorted(feature_row.values.items(), key=lambda item: item[0])),
        )
        remembered = self._last_law
        if remembered is not None and remembered[0] == key:
            return remembered[1]
        law = self._law(feature_row)
        self._last_law = (key, law)
        return law

    def law_knots(
        self, feature_row: DailyObservation
    ) -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
        """This row's predictive law as `(values, levels)` knots.

        The law `predict_stress` inverts, handed out rather than described:
        `values` is non-decreasing and `levels` is `(0.0,) + self.levels +
        (1.0,)`, and `P(spread > tau)` for any `tau` is fixed by the pair. What
        it buys a caller is *where* a tau fell --- a tau above the top declared
        level is read inside the single segment `[Q(0.95), high]`, and a curve
        that flattens because every tau it was asked about landed in one
        straight segment looks exactly like a curve that flattened because the
        learner had nothing to say. Only the knots tell the two apart, and
        `predict_stress` returns floats and throws them away.

        The same evaluation `predict_stress` uses for that row, not a second
        one; see `_shared_law`. A feature row missing a declared regressor
        raises `MissingRegressorError` from the fit's own read of it, uncaught
        --- a caller asking where its tau fell on a row the model cannot read
        is asking the wrong question, and a knot set invented to answer it
        would be the worst possible answer.
        """

        return self._shared_law(feature_row)

    def predict_stress(
        self,
        feature_row: DailyObservation,
        taus: Optional[Sequence[float]] = None,
    ) -> Tuple[float, ...]:
        """`P(spread > tau)` per tau, read off the law `predict` reports.

        The exceedance is the *inverse of the reported quantile vector*, not a
        second opinion about it: at a declared level `q`, `predict` reports the
        quantile `Q(q)` and this places exactly `1 - q` above it, because the
        pair `(Q(q), q)` is one of the knots interpolated between. That is the
        contract's "an exceedance derived from the predictive distribution", and
        it is what `ForecastInterfaceConformance::
        test_predict_stress_agrees_with_the_quantiles_predict_reports` checks.

        Nothing here was fitted to a `stress_gt_*` label column.

        The interpolation is linear in level between neighbouring knots and
        saturates outside them --- 1.0 below the lowest, 0.0 at or above the
        highest --- which is `_exceedance_from_residuals`' convention, one level
        up: that function inverts an *empirical sample* read at positions
        `k / (n - 1)`, and this inverts a *declared grid* read at its own
        levels. The two are the same map wherever the sample and the grid agree,
        and this model's grid is the contract's rather than a sample's, so the
        inversion is written against the grid rather than routed through a
        sample that would have to be manufactured to hold it.

        Ties are the one place the inversion is approximate, exactly as there: if
        two fits agree to the last bit the knot set is flat over a range of
        levels and has no single inverse, and the higher level is returned.

        `law_knots` hands out the knots these floats were read off, from this
        same evaluation, for a caller that needs to know which segment a tau
        landed in and not only what came out.
        """

        family = _validate_taus_bp(
            load_stress_thresholds()["taus_bp"] if taus is None else taus
        )
        values, levels = self._shared_law(feature_row)
        return tuple(_exceedance_from_law(values, levels, tau) for tau in family)


def _rearranged(
    estimators: Sequence[Any], design_rows: Sequence[Sequence[float]]
) -> Tuple[Tuple[float, ...], ...]:
    """Each design row read at every level, **rearranged by sorting**.

    The single place a predicted vector is produced --- `predict`,
    `point_forecast`, the fitted residual sample and the law `predict_stress`
    inverts all come through here, so a caller cannot be shown a rearranged
    vector beside an exceedance derived from a crossed one. Written as a module
    function rather than a method because the fit needs it before there is a
    fitted object to call it on, and a second spelling of the rearrangement in
    the fitter is exactly the drift this centralisation prevents.

    One `predict` call per estimator over the whole batch rather than one per
    row per estimator: a rolling backtest refits at every origin, and the
    per-row form made the residual sample `n` times more estimator calls than
    it needs to be.
    """

    rows = [[float(value) for value in row] for row in design_rows]
    columns = [
        [float(value) for value in estimator.predict(rows)]
        for estimator in estimators
    ]
    return tuple(
        tuple(sorted(column[index] for column in columns))
        for index in range(len(rows))
    )


def _exceedance_from_law(
    values: Sequence[float], levels: Sequence[float], tau: float
) -> float:
    """`P(Y > tau)` under the piecewise-linear law `(values, levels)`.

    Walks the quantile map backwards, as `baseline._exceedance_from_residuals`
    does for an empirical sample: find the segment `tau` sits in, convert its
    position along that segment into a level, and return the mass above it.
    """

    if tau < values[0]:
        return 1.0
    if tau >= values[-1]:
        return 0.0
    lower = bisect_right(values, tau) - 1
    span = values[lower + 1] - values[lower]
    weight = 0.0 if span <= 0.0 else (tau - values[lower]) / span
    level = levels[lower] + weight * (levels[lower + 1] - levels[lower])
    return 1.0 - level


def _training_design(
    rows: Sequence[DailyObservation],
    dates: Sequence[date],
    spreads: Sequence[Optional[float]],
    garch_spreads: Sequence[Optional[float]],
    origins: Sequence[int],
    names: Tuple[str, ...],
    lags: int,
    volatility_feature: Optional[str],
    label: str,
    arx_feature: Optional[str] = None,
    arx_frame: Sequence[DailyObservation] = (),
    arx_origins: Optional[Sequence[int]] = None,
) -> Tuple[
    Mapping[str, float],
    Optional[Tuple[float, float, float]],
    Optional[float],
    List[List[float]],
    List[float],
    List[float],
    Optional[FittedArx],
]:
    """One fit's imputations, GARCH, ARX, design and targets, over the pairs at `origins`.

    `origins` are frame positions `p` whose one-step pair `(p, p + 1)` trains;
    every one is at least `lags`. `spreads` is what the training lags and
    variances are read off -- the frame's own, or, for an excluding model, the
    frame's with every row it may not train on made a hole -- and
    `garch_spreads` what the GARCH is fitted on. The ARX is `fit_arx` on
    `arx_frame`, at `arx_origins` when given. The one spelling the full fit,
    the split-conformal fit and every excluding model share: two spellings of
    one design is how two models stop being comparable.

    Returns `(imputations, garch_parameters, garch_initial_variance, design,
    targets, variances, arx)`, `variances` being the recursion filtered over
    `spreads` (empty without the volatility feature) and `arx` `None` without
    the ARX feature.
    """

    change_names = _spread_change_names(lags)

    # The GARCH(1,1), fitted on `garch_spreads` and nothing after them, then
    # filtered over `spreads` with those parameters: rows it did not fit on are
    # run through the recursion, never fitted on. `variances[p]` reads rows at
    # or before `p`.
    garch: Optional[Tuple[float, float, float]] = None
    initial: Optional[float] = None
    variances: List[float] = []
    if volatility_feature is not None:
        garch, initial = _fit_garch11(garch_spreads, label)
        variances = _garch_variances(_squared_changes(spreads), garch, initial)

    # The imputation is fitted on the origins and only these -- contract test
    # 3's "recomputed on a training window alone", the same rows `fit_arx` uses.
    changes = [
        _spread_changes(spreads, position, lags, f"training row for {dates[position]}")
        for position in origins
    ]
    if lags and not any(None not in row_changes for row_changes in changes):
        raise ValueError(
            f"spread_change_lags {lags} leaves no training row with every lag "
            f"defined: none of the {len(changes)} training rows of the {label} "
            f"with {lags} rows before them observes all {lags}. A lag imputed "
            f"on every design row is a column of training means, not a regressor"
        )
    observed: Mapping[str, List[float]] = {name: [] for name in names + change_names}
    for row_changes in changes:
        for name, change in zip(change_names, row_changes):
            if change is not None:
                observed[name].append(change)
    for position in origins:
        for name in names:
            value = _raw_regressor(rows[position], name, "training row")
            if value is not None:
                observed[name].append(value)

    imputations = {}
    for name in names:
        seen = observed[name]
        if not seen:
            raise ValueError(
                f"regressor {name!r} is unobserved on every row of the training "
                f"window ({dates[origins[0]]}..{dates[origins[-1]]}); there is "
                f"nothing to fit an imputation from, and filling it with 0.0 would "
                f"be the coercion contract test 5 prohibits"
            )
        imputations[name] = sum(seen) / len(seen)
    for name in change_names:
        seen = observed[name]
        imputations[name] = sum(seen) / len(seen)

    # The ARX, by `baseline.fit_arx` and no second fitter, on the declared
    # regressors and the rows this fit trains on. Its own minimum and its own
    # refusals: the defaults, not gbm's `minimum_history`, which is a statement
    # about the frame rather than about the rows the ARX is handed.
    arx: Optional[FittedArx] = None
    if arx_feature is not None:
        arx = fit_arx(arx_frame, names, origins=arx_origins)

    design = []
    targets = []
    for position, row_changes in zip(origins, changes):
        # The origin's variance and ARX forecast, `position`: the target row's
        # would read the target.
        design.append(
            _design(
                rows[position],
                names,
                imputations,
                "training row",
                row_changes,
                variances[position] if variances else None,
                arx,
            )
        )
        targets.append(float(rows[position + 1].spread_bps))
    return imputations, garch, initial, design, targets, variances, arx


def _fitted_levels(
    estimator_class: Any,
    grid: Sequence[float],
    design: Sequence[Sequence[float]],
    targets: Sequence[float],
    random_state: int,
    min_samples_leaf: int,
) -> List[Any]:
    """One estimator per level, fitted on `design` and `targets`, in level order."""

    estimators = []
    for level in grid:
        estimator = estimator_class(
            loss="quantile",
            quantile=level,
            # Both explicit, both load-bearing. See the module docstring: the
            # `"auto"` default turns early stopping on above 10 000 rows and
            # draws a validation split, so a model that is reproducible on a
            # fixture stops being reproducible on a panel.
            early_stopping=False,
            random_state=random_state,
            min_samples_leaf=min_samples_leaf,
        )
        estimator.fit(design, targets)
        estimators.append(estimator)
    return estimators


def fit_gradient_boosted_quantiles(
    train_frame: Sequence[DailyObservation],
    regressors: Sequence[str],
    cutoff: Optional[date] = None,
    minimum_history: int = 20,
    levels: Sequence[float] = QUANTILE_LEVELS,
    random_state: int = DEFAULT_RANDOM_STATE,
    min_samples_leaf: int = 20,
    calibration: str = "none",
    calibration_share: Optional[float] = None,
    purge_days: Optional[int] = None,
    spread_change_lags: Optional[int] = None,
    volatility_feature: Optional[str] = None,
    calibration_folds: Optional[int] = None,
    arx_feature: Optional[str] = None,
) -> FittedGradientBoostedQuantiles:
    """Fit one gradient-boosted quantile regressor per level and return the model.

    Args:
        train_frame: the training rows, strictly ascending by date. The design is
            this frame's own one-step-ahead pairs and nothing else, so a fit on
            `n` rows has `n - 1` design rows --- the same count, and the same
            construction, as `fit_arx`.
        regressors: the ordered exogenous regressor names. **Required, with no
            default**, for the reason `fit_arx` refuses one: a default would be a
            silent assumption about which columns a model is entitled to read.
        cutoff: the last date the model was allowed to see. Defaults to the
            frame's own last date.
        minimum_history: the shortest frame that may produce a fitted model.
        levels: the quantile grid, defaulting to the declared one. Must contain
            `0.50`; see `_MEDIAN_LEVEL`.
        random_state: the seed handed to every fit. See `DEFAULT_RANDOM_STATE`.
        min_samples_leaf: passed straight to the estimator. Present because a
            fixture-sized frame cannot be split at scikit-learn's default at
            all, not as a tuned value --- tuning is not this block's.
        calibration: one of `CALIBRATIONS`. `"none"`, the default, fits every
            row and reports the band as fitted; `"conformal"` holds out the
            most recent rows and widens the band by their conformal score;
            `"cross_conformal"` reports the full fit and moves its band to
            CV+'s edges over `calibration_folds` purged date blocks. See the
            module docstring.
        calibration_share: the share of the frame held out as calibration rows,
            strictly inside `(0, 1)`. `None` means `DEFAULT_CALIBRATION_SHARE`
            under `conformal`, and is the only value `none` accepts: a share
            handed to a model that holds nothing out would be read as a setting
            that took effect.
        purge_days: the registry-derived gap, in calendar days, between the
            last fit row and the first calibration row -- and, under
            `cross_conformal`, on both sides of every held-out block. Passed
            by the fold loop (`baseline._fit_at_origin`), which sized it from
            the declaration, and never chosen here. Required under both
            calibrations, by `splits.require_purge_days`: a calibration split
            with a defaulted gap is the silent zero the splitter exists to
            refuse. Read by nothing under `none`, which splits nothing.
        spread_change_lags: how many lagged spread changes the design carries,
            at least 1. `None`, the default, carries none and is the model every
            published gbm record was produced with. See the module docstring.
        volatility_feature: one of `VOLATILITY_FEATURES`, or `None`, the
            default, which carries no volatility column and is the model every
            published gbm record was produced with. `"garch11"` fits a
            GARCH(1,1) on the fit rows' spread changes and adds its one-step
            conditional variance. See the module docstring.
        calibration_folds: the contiguous date blocks `cross_conformal` splits
            the frame into, an int of at least 2. `None` means
            `DEFAULT_CALIBRATION_FOLDS` under `cross_conformal`, and is the
            only value the other calibrations accept, for `calibration_share`'s
            reason; `calibration_share` is refused under `cross_conformal` by
            the same rule.
        arx_feature: one of `ARX_FEATURES`, or `None`, the default, which
            carries no ARX column and is the model every published gbm record
            was produced with. `"declared"` fits `baseline.fit_arx` on the fit
            rows over `regressors` and adds its one-step point forecast. See
            the module docstring.

    Returns:
        A `FittedGradientBoostedQuantiles` carrying its fitted estimators, its
        regressor names, its fitted imputation means, its sorted residuals, its
        cutoff, and its calibration: the settings, the widening and the dates
        of both slices.

    Raises:
        MissingMLExtraError: if the optional `ml` extra is not installed.
        LookAheadError: if any training row is dated after `cutoff`.
        SplitError: if the frame is not strictly ascending by date, or if
            `calibration="conformal"` or `"cross_conformal"` is given no
            `purge_days` (or a `purge_days` that is not a non-negative int).
        MissingRegressorError: if a training row does not carry a declared
            regressor.
        MetricError: if a declared level is outside `(0, 1)`, or the grid is not
            strictly ascending. `MetricError` is a `ValueError`, and the phrase
            is `metrics._validate_levels`' own: one statement of what a quantile
            level may be, not a second one here.
        ValueError: if no regressors are declared, if one is declared twice, if
            the grid does not carry `0.50`, if the frame is shorter than
            `minimum_history`, if a regressor is unobserved on every row of
            the training window; and, for the calibration, if `calibration`
            is not one of `CALIBRATIONS`, if `calibration_share` is outside
            `(0, 1)` or is given to `none`, if the calibration slice holds
            fewer rows than the conformal quantile needs to be finite, or if
            the purge leaves fewer than two fit rows; and, for the
            cross-conformal calibration, if `calibration_folds` is not an int
            of at least 2 or is given to another calibration, if
            `calibration_share` is given to it, if a block holds out no row or
            leaves its excluding model no training pair after the purge, or if
            fewer held-out rows are scored than CV+'s ranks need; and, for the
            lags, if
            `spread_change_lags` is not an int of at least 1, if it leaves no
            training row with every lag defined, or if a calibration row's
            feature row has fewer rows than that before it; and, for the
            volatility feature, if `volatility_feature` is not one of
            `VOLATILITY_FEATURES`, if the fit rows carry fewer than
            `GARCH_MINIMUM_CHANGES` observed spread changes, or if the GARCH
            fit does not converge; and, for the ARX feature, if `arx_feature`
            is not one of `ARX_FEATURES`. Whatever `baseline.fit_arx` raises
            on the rows it is handed -- fewer than its default minimum, a
            singular design -- propagates as it raised it.
    """

    grid = _validate_levels(levels)
    if _MEDIAN_LEVEL not in grid:
        raise ValueError(
            f"the declared levels {list(grid)} do not carry {_MEDIAN_LEVEL}; the "
            f"point forecast is the rearranged median and there is no honest "
            f"substitute for it -- an average of the two levels straddling the "
            f"middle is a centre no fit produced"
        )

    # The calibration's own arguments, before anything about the frame: each is
    # a statement about what the caller asked for, owed whether or not the
    # frame would have fitted.
    if calibration not in CALIBRATIONS:
        raise ValueError(
            f"unknown calibration {calibration!r}; this model can be built with "
            f"{', '.join(CALIBRATIONS)}. A misspelt calibration fitted as 'none' "
            f"would publish the in-sample band under a record that asked for "
            f"another"
        )
    if calibration_folds is not None and calibration != "cross_conformal":
        raise ValueError(
            f"calibration_folds {calibration_folds} was given, but calibration "
            f"{calibration!r} splits the frame into no blocks; only "
            f"'cross_conformal' does. A setting that is accepted and ignored is "
            f"read by the next person as a setting that took effect"
        )
    folds: Optional[int] = None
    if calibration == "none":
        if calibration_share is not None:
            raise ValueError(
                f"calibration_share {calibration_share} was given, but "
                f"calibration 'none' holds no rows out. A setting that is "
                f"accepted and ignored is read by the next person as a setting "
                f"that took effect"
            )
        share: Optional[float] = None
    elif calibration == "cross_conformal":
        if calibration_share is not None:
            raise ValueError(
                f"calibration_share {calibration_share} was given, but "
                f"calibration 'cross_conformal' holds out every row in turn, "
                f"not a share of them; its setting is calibration_folds. A "
                f"setting that is accepted and ignored is read by the next "
                f"person as a setting that took effect"
            )
        share = None
        folds = (
            DEFAULT_CALIBRATION_FOLDS if calibration_folds is None else calibration_folds
        )
        if isinstance(folds, bool) or not isinstance(folds, int) or folds < 2:
            raise ValueError(
                f"calibration_folds must be an int of at least 2, got {folds!r}; "
                f"one block holds out the whole frame and leaves its excluding "
                f"model nothing to fit on"
            )
        require_purge_days(purge_days)
    else:
        share = (
            DEFAULT_CALIBRATION_SHARE
            if calibration_share is None
            else calibration_share
        )
        if (
            isinstance(share, bool)
            or not isinstance(share, (int, float))
            or not 0.0 < share < 1.0
        ):
            raise ValueError(
                f"calibration_share must be a number strictly inside (0, 1), "
                f"got {share!r}; a share of 0 holds nothing out to calibrate "
                f"on, and a share of 1 leaves nothing to fit"
            )
        share = float(share)
        require_purge_days(purge_days)

    if spread_change_lags is not None and (
        isinstance(spread_change_lags, bool)
        or not isinstance(spread_change_lags, int)
        or spread_change_lags < 1
    ):
        raise ValueError(
            f"spread_change_lags must be an int of at least 1, got "
            f"{spread_change_lags!r}; lag 0 would be the change into the day "
            f"being forecast, which is the target minus the autoregressive term, "
            f"and a model with no lags is spelled by leaving the setting out"
        )
    lags = spread_change_lags or 0

    if volatility_feature is not None and volatility_feature not in VOLATILITY_FEATURES:
        raise ValueError(
            f"unknown volatility_feature {volatility_feature!r}; this model can "
            f"be built with {', '.join(VOLATILITY_FEATURES)}, or with none by "
            f"leaving the setting out. A misspelt feature fitted without one "
            f"would publish today's gbm under a declaration naming a volatility "
            f"model"
        )

    if arx_feature is not None and arx_feature not in ARX_FEATURES:
        raise ValueError(
            f"unknown arx_feature {arx_feature!r}; this model can be built with "
            f"{', '.join(ARX_FEATURES)} -- the ARX fitted on this model's own "
            f"declared regressors -- or with none by leaving the setting out. A "
            f"misspelt feature fitted without one would publish today's gbm "
            f"under a declaration naming an ARX"
        )

    names = tuple(str(name) for name in regressors)
    if not names:
        raise ValueError(
            "no regressors declared; an empty list is how a caller omits the "
            "decision rather than makes it. Name the regressors, even if the "
            "honest answer is one of them"
        )
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise ValueError(
            f"regressors declared more than once: {duplicates}; a column handed "
            f"to the ensemble twice splits on itself and its importance is "
            f"meaningless individually"
        )

    rows = list(train_frame)
    if len(rows) < minimum_history:
        raise ValueError(
            f"gbm needs at least {minimum_history} training rows, got {len(rows)}; "
            f"a boosted quantile fit from fewer is not a fitted model"
        )

    dates = [row.date for row in rows]
    ensure_strictly_ascending(dates, label="training frame dates")

    declared = dates[-1] if cutoff is None else cutoff
    if dates[-1] > declared:
        raise LookAheadError(
            f"training frame reaches {dates[-1]}, past its cutoff {declared}; "
            f"a fitted model may not contain a row it was not allowed to see"
        )

    # The calibration split, by date. The calibration rows are the most recent
    # share of the frame; the fit rows are the earlier rows that clear the purge
    # before the first of them, by the splitter's own comparison. Under `none`
    # the fit rows are the frame.
    fit_rows = rows
    calibration_rows: List[DailyObservation] = []
    if share is not None:
        count = int(Fraction(repr(share)) * len(rows))
        needed = _minimum_calibration_rows(grid)
        if count < needed:
            raise ValueError(
                f"conformal calibration needs at least {needed} calibration "
                f"rows, got {count} ({share} of {len(rows)} training rows); "
                f"below {needed} the conformal quantile of a "
                f"{float(_band_probability(grid))} band is infinite, and a "
                f"finite widening there would claim a coverage the "
                f"calibration cannot support"
            )
        first = len(rows) - count
        opens = dates[first]
        calibration_rows = rows[first:]
        fit_rows = [
            row for row in rows[:first] if clears_purge(row.date, opens, purge_days)
        ]
        if len(fit_rows) < 2:
            raise ValueError(
                f"a {purge_days}-day purge before the calibration rows opening "
                f"{opens} leaves {len(fit_rows)} fit row(s) of {len(rows)}; the "
                f"design needs at least one origin and its successor"
            )

    # Every row's spread, `None` at a hole, for the lags and the variance alone.
    # Over the whole frame, which is the only history either is ever read from;
    # the fit rows are its prefix, so a position in one is the same position in
    # the other.
    spreads = (
        [_observed_spread(row, "training row") for row in rows]
        if lags or volatility_feature is not None
        else []
    )

    # The origins: every fit row that has a successor among the fit rows, less
    # the first `lags`, whose changes would reach before the frame. The GARCH is
    # fitted on the fit rows' spreads and filtered over the whole frame, so the
    # calibration rows are run through the recursion, never fitted on.
    # The ARX is fitted on the fit rows as one frame, which is what
    # `--model arx` fits on the same rows.
    imputations, garch, initial, design, targets, variances, arx = _training_design(
        rows,
        dates,
        spreads,
        spreads[: len(fit_rows)],
        range(lags, len(fit_rows) - 1),
        names,
        lags,
        volatility_feature,
        "fit rows",
        arx_feature,
        fit_rows,
    )

    # The cross-conformal blocks, planned and designed before anything is
    # fitted: every refusal about them is a statement about the frame. Blocks
    # are contiguous runs of the frame's rows in date order, never shuffled.
    plans = []
    if folds is not None:
        bounds = [len(rows) * number // folds for number in range(folds + 1)]
        for number in range(folds):
            start, stop = bounds[number], bounds[number + 1]
            kept: List[bool] = []
            origins: List[int] = []
            if start < stop:
                opens, closes = dates[start], dates[stop - 1]
                # A row before the block trains only if it clears the gap
                # before the block opens; a row after it only if the block's
                # last row clears the gap before that row. The splitter's own
                # comparison, in both directions.
                kept = [
                    clears_purge(when, opens, purge_days)
                    if position < start
                    else position >= stop and clears_purge(closes, when, purge_days)
                    for position, when in enumerate(dates)
                ]
                # A pair trains only if its origin and its target both do.
                origins = [
                    position
                    for position in range(lags, len(rows) - 1)
                    if kept[position] and kept[position + 1]
                ]
            if not origins:
                raise ValueError(
                    f"cross-conformal block {number + 1} of {folds} holds out "
                    f"{stop - start} of {len(rows)} rows and leaves its excluding "
                    f"model {len(origins)} training pair(s) after a "
                    f"{purge_days}-day purge on both sides; a gbm fit needs its "
                    f"block to hold out at least one row, and at least one "
                    f"origin with its successor to fit on"
                )
            # The rows this model may not train on are holes to it, so no lag
            # and no variance in its design reads one.
            masked = [
                spread if keep else None for spread, keep in zip(spreads, kept)
            ]
            label = f"training rows of cross-conformal block {number + 1} of {folds}"
            # Its ARX trains on every one-step pair whose two rows it may train
            # on, from the frame's first row -- the full fit's ARX reads every
            # pair of its rows, not only those past the lags -- and never on a
            # pair that spans the block.
            arx_origins = [
                position
                for position in range(len(rows) - 1)
                if kept[position] and kept[position + 1]
            ]
            (
                block_imputations,
                block_garch,
                block_initial,
                block_design,
                block_targets,
                _,
                block_arx,
            ) = _training_design(
                rows,
                dates,
                masked,
                masked,
                origins,
                names,
                lags,
                volatility_feature,
                label,
                arx_feature,
                rows,
                arx_origins,
            )
            # Its scored rows' inputs are every row at or before their feature
            # row, as a forecast's are; only what the model learned is its own.
            filtered = (
                _garch_variances(_squared_changes(spreads), block_garch, block_initial)
                if volatility_feature is not None
                else []
            )
            held_out = []
            for index in range(start, stop):
                # No row of the frame clears the gap before this one, or its
                # feature row has too few rows before it for its lags: there is
                # no forecast of it to score.
                if not clears_purge(dates[0], dates[index], purge_days):
                    continue
                # `_feature_index` on the tail, for the reason the conformal
                # calibration rows below give.
                tail = range(max(0, index - purge_days - 1), index)
                position = _feature_index(dates, tail, index, purge_days)
                if position < lags:
                    continue
                held_out.append(
                    (
                        _design(
                            rows[position],
                            names,
                            block_imputations,
                            "held-out feature row",
                            _spread_changes(
                                spreads,
                                position,
                                lags,
                                f"held-out feature row for {dates[position]}",
                            ),
                            filtered[position] if filtered else None,
                            block_arx,
                        ),
                        float(rows[index].spread_bps),
                        dates[index],
                    )
                )
            plans.append(
                (
                    start,
                    stop,
                    origins,
                    block_imputations,
                    block_garch,
                    block_initial,
                    block_arx,
                    block_design,
                    block_targets,
                    held_out,
                )
            )
        count = sum(len(plan[-1]) for plan in plans)
        needed = _minimum_calibration_rows(grid)
        if count < needed:
            raise ValueError(
                f"cross-conformal calibration needs at least {needed} held-out "
                f"scores, got {count} over {folds} blocks of {len(rows)} training "
                f"rows; below {needed} CV+'s ranks for a "
                f"{float(_band_probability(grid))} band name no score, and a band "
                f"read off an index that wrapped would claim a coverage the "
                f"calibration cannot support"
            )

    # Imported here rather than at the top of the function: every refusal
    # above is a statement about the arguments and is owed to a caller whether
    # or not the extra is installed.
    estimator_class = _estimator_class()
    # Read in the same breath as the class the fits are made with, so the
    # versions a record publishes are those of the modules that did the fitting.
    versions = _library_versions()

    estimators = _fitted_levels(
        estimator_class, grid, design, targets, random_state, min_samples_leaf
    )

    # The residual sample, about this model's own rearranged median rather than
    # about the 0.50 fit: the two differ exactly on the rows where that fit
    # crossed a neighbour, and there the estimator's value is not the centre of
    # the distribution the model reports.
    centre = grid.index(_MEDIAN_LEVEL)
    residuals = [
        target - vector[centre]
        for vector, target in zip(_rearranged(estimators, design), targets)
    ]

    # The widening: every calibration row scored by the estimators fitted
    # above -- not refitted, and never on a fit row -- from the feature row the
    # backtest's own rule would choose for it, then the conformal rank.
    widening = 0.0
    if calibration_rows:
        first = len(rows) - len(calibration_rows)
        scored = []
        for index in range(first, len(rows)):
            # `_feature_index` scans back from the end of the indices it is
            # handed, and dates ascend strictly, so the row `purge_days + 1`
            # positions back already clears the gap: handing it only that tail
            # returns the same row as handing it the whole prefix, without a
            # frame-length copy per calibration row per fold.
            tail = range(max(0, index - purge_days - 1), index)
            position = _feature_index(dates, tail, index, purge_days)
            feature = rows[position]
            # The lags end at the feature row, never at the row being scored.
            scored.append(
                (
                    _design(
                        feature,
                        names,
                        imputations,
                        "calibration row",
                        _spread_changes(
                            spreads,
                            position,
                            lags,
                            f"calibration feature row for {dates[position]}",
                        ),
                        variances[position] if variances else None,
                        # The fit rows' ARX, never refitted on these rows.
                        arx,
                    ),
                    float(rows[index].spread_bps),
                )
            )
        vectors = _rearranged(estimators, [features for features, _ in scored])
        scores = sorted(
            max(vector[0] - target, target - vector[-1])
            for vector, (_, target) in zip(vectors, scored)
        )
        rank = math.ceil(_band_probability(grid) * (len(scores) + 1))
        widening = scores[rank - 1]

    # The excluding models: each fitted on its own design, and each held-out
    # row scored by its own block's model and no other.
    blocks = []
    for (
        start,
        stop,
        origins,
        block_imputations,
        block_garch,
        block_initial,
        block_arx,
        block_design,
        block_targets,
        held_out,
    ) in plans:
        block_estimators = _fitted_levels(
            estimator_class,
            grid,
            block_design,
            block_targets,
            random_state,
            min_samples_leaf,
        )
        vectors = (
            _rearranged(block_estimators, [features for features, _, _ in held_out])
            if held_out
            else ()
        )
        blocks.append(
            _ExcludingModel(
                estimators=block_estimators,
                imputations=block_imputations,
                garch_parameters=block_garch,
                garch_initial_variance=block_initial,
                arx=block_arx,
                held_out_start=dates[start],
                held_out_end=dates[stop - 1],
                training_dates=sorted(
                    {dates[p] for origin in origins for p in (origin, origin + 1)}
                ),
                scored_dates=[when for _, _, when in held_out],
                scores=[
                    max(vector[0] - target, target - vector[-1])
                    for vector, (_, target, _) in zip(vectors, held_out)
                ],
            )
        )
    held_out_dates = [when for block in blocks for when in block.scored_dates]
    if calibration_rows:
        calibration_start: Optional[date] = calibration_rows[0].date
        calibration_end: Optional[date] = calibration_rows[-1].date
    elif held_out_dates:
        calibration_start, calibration_end = held_out_dates[0], held_out_dates[-1]
    else:
        calibration_start = calibration_end = None

    return FittedGradientBoostedQuantiles(
        estimators,
        names,
        imputations,
        residuals,
        declared,
        grid,
        random_state,
        ml_libraries=versions,
        calibration=calibration,
        calibration_share=share,
        widening=widening,
        fit_end=fit_rows[-1].date,
        calibration_start=calibration_start,
        calibration_end=calibration_end,
        spread_change_lags=spread_change_lags,
        history=tuple(zip(dates, spreads)),
        volatility_feature=volatility_feature,
        garch_parameters=garch,
        garch_initial_variance=initial,
        calibration_folds=folds,
        calibration_blocks=blocks,
        arx_feature=arx_feature,
        arx=arx,
    )


def gbm_exceedance(
    regressors: Sequence[str],
    minimum_history: int = 20,
    random_state: int = DEFAULT_RANDOM_STATE,
    min_samples_leaf: int = 20,
) -> ExceedancePredictor:
    """Conditional exceedance from the gradient-boosted quantiles' own law.

    The fourth implementer of `ExceedancePredictor`, and the first whose
    predictive *width* moves with the feature row. `arx_exceedance`'s curve
    moves because the centre moves and the residual law is carried along
    unchanged; `threshold_exceedance` adds a second reason by switching which
    fitted relationship produces that centre. This one's band is fitted at each
    level separately, so two rows with the same centre can still get different
    curves --- which is what a conditional quantile model is for, and what
    nothing in `event_eval` had scored before.

    `fit_gradient_boosted_quantiles` is fitted on the training rows the
    evaluator hands over --- everything that cleared the purge gap ahead of the
    window and nothing from inside it --- and the fitted model is then read once
    per feature row.

    **Derived, not re-derived.** The construction is
    `FittedGradientBoostedQuantiles.predict_stress`, which is the inverse of the
    vector `predict` reports. Reading the fits a second time here would be a
    second opinion about one distribution.

    `features_read` comes off the fitted model, so it is `spread_bps` plus the
    declared regressors --- the autoregressive term included, which is the half
    a predictor reporting only what it was handed would leave out.

    Args:
        regressors: the ordered exogenous regressor names, as
            `fit_gradient_boosted_quantiles` takes them. Required, with no
            default.
        minimum_history: the shortest training frame that may produce a fitted
            model. Passed through, and refused below.
        random_state: the seed every fit uses.
        min_samples_leaf: passed through to the estimator.

    Returns:
        A `fit_predict` callable suitable for `event_eval.evaluate_event_window`
        and for `rolling_exceedance_backtest`.

    Raises:
        MissingMLExtraError, ValueError, MissingRegressorError, LookAheadError:
            at call time, whatever the fitter raises on the frame it is given.
            Not caught and re-wrapped: a refusal to fit is the fitter's
            statement about the frame.
    """

    declared = tuple(str(name) for name in regressors)

    def fit_predict(
        train_rows: Sequence[DailyObservation],
        feature_rows: Sequence[DailyObservation],
        taus: Sequence[float],
    ) -> ExceedanceCurves:
        model = fit_gradient_boosted_quantiles(
            train_rows,
            declared,
            minimum_history=minimum_history,
            random_state=random_state,
            min_samples_leaf=min_samples_leaf,
        )
        return ExceedanceCurves(
            tuple(model.predict_stress(row, taus) for row in feature_rows),
            model.features_read,
            # Off the model that produced the curves, not read again here: the
            # versions a record names are the fit's.
            ml_libraries=model.ml_libraries,
        )

    return fit_predict
