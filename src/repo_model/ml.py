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

Stdlib plus the `ml` extra, inside functions.
"""

from __future__ import annotations

from bisect import bisect_right
from datetime import date
from types import MappingProxyType
from typing import Any, List, Mapping, Optional, Sequence, Tuple

from .baseline import (
    ExceedanceCurves,
    ExceedancePredictor,
    _raw_regressor,
    _validate_taus_bp,
)
from .contract import QUANTILE_LEVELS
from .data import DailyObservation, load_stress_thresholds
from .metrics import _validate_levels
from .splits import LookAheadError, ensure_strictly_ascending

__all__ = [
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
    """

    __slots__ = (
        "_estimators",
        "_residuals",
        "cutoff",
        "imputations",
        "levels",
        "ml_libraries",
        "random_state",
        "regressors",
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
    ) -> None:
        self.ml_libraries: Mapping[str, str] = MappingProxyType(dict(ml_libraries))
        self.regressors: Tuple[str, ...] = tuple(regressors)
        self._estimators: Tuple[Any, ...] = tuple(estimators)
        self.imputations: Mapping[str, float] = MappingProxyType(
            {name: float(imputations[name]) for name in self.regressors}
        )
        self._residuals: Tuple[float, ...] = tuple(sorted(float(r) for r in residuals))
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
        """

        return ("spread_bps",) + self.regressors

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
        """

        return self.design_names

    def trained_beyond(self, feature_row: DailyObservation) -> bool:
        """Was this model fitted on rows dated after `feature_row`?"""

        return feature_row.date < self.cutoff

    def design_row(self, feature_row: DailyObservation) -> Tuple[float, ...]:
        """The feature row as this model reads it, in `design_names` order."""

        values = [float(feature_row.spread_bps)]
        for name in self.regressors:
            observed = _raw_regressor(feature_row, name, "feature row")
            values.append(self.imputations[name] if observed is None else observed)
        return tuple(values)

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

        Non-decreasing by construction: `_quantile_vector` sorts.
        """

        return self._quantile_vector(self.design_row(feature_row))

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
        """

        interior = self.predict(feature_row)
        anchor = interior[self.levels.index(_MEDIAN_LEVEL)]
        pad = max(_TAIL_SHARE * (interior[-1] - interior[0]), _MINIMUM_TAIL)
        bottom = anchor + self._residuals[0]
        top = anchor + self._residuals[-1]
        low = bottom if bottom < interior[0] else interior[0] - pad
        high = top if top > interior[-1] else interior[-1] + pad
        return (low,) + interior + (high,), (0.0,) + self.levels + (1.0,)

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
        """

        family = _validate_taus_bp(
            load_stress_thresholds()["taus_bp"] if taus is None else taus
        )
        values, levels = self._law(feature_row)
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


def fit_gradient_boosted_quantiles(
    train_frame: Sequence[DailyObservation],
    regressors: Sequence[str],
    cutoff: Optional[date] = None,
    minimum_history: int = 20,
    levels: Sequence[float] = QUANTILE_LEVELS,
    random_state: int = DEFAULT_RANDOM_STATE,
    min_samples_leaf: int = 20,
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

    Returns:
        A `FittedGradientBoostedQuantiles` carrying its fitted estimators, its
        regressor names, its fitted imputation means, its sorted residuals and
        its cutoff.

    Raises:
        MissingMLExtraError: if the optional `ml` extra is not installed.
        LookAheadError: if any training row is dated after `cutoff`.
        SplitError: if the frame is not strictly ascending by date.
        MissingRegressorError: if a training row does not carry a declared
            regressor.
        MetricError: if a declared level is outside `(0, 1)`, or the grid is not
            strictly ascending. `MetricError` is a `ValueError`, and the phrase
            is `metrics._validate_levels`' own: one statement of what a quantile
            level may be, not a second one here.
        ValueError: if no regressors are declared, if one is declared twice, if
            the grid does not carry `0.50`, if the frame is shorter than
            `minimum_history`, or if a regressor is unobserved on every row of
            the training window.
    """

    grid = _validate_levels(levels)
    if _MEDIAN_LEVEL not in grid:
        raise ValueError(
            f"the declared levels {list(grid)} do not carry {_MEDIAN_LEVEL}; the "
            f"point forecast is the rearranged median and there is no honest "
            f"substitute for it -- an average of the two levels straddling the "
            f"middle is a centre no fit produced"
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

    # The origins: every row that has a successor in the frame. These, and only
    # these, are what the imputation is fitted on -- contract test 3's
    # "recomputed on a training window alone", the same rows `fit_arx` uses.
    origins = rows[:-1]
    observed: Mapping[str, List[float]] = {name: [] for name in names}
    for row in origins:
        for name in names:
            value = _raw_regressor(row, name, "training row")
            if value is not None:
                observed[name].append(value)

    imputations = {}
    for name in names:
        seen = observed[name]
        if not seen:
            raise ValueError(
                f"regressor {name!r} is unobserved on every row of the training "
                f"window ({origins[0].date}..{origins[-1].date}); there is nothing "
                f"to fit an imputation from, and filling it with 0.0 would be the "
                f"coercion contract test 5 prohibits"
            )
        imputations[name] = sum(seen) / len(seen)

    design = []
    targets = []
    for index in range(1, len(rows)):
        origin = rows[index - 1]
        row = [float(origin.spread_bps)]
        for name in names:
            value = _raw_regressor(origin, name, "training row")
            row.append(imputations[name] if value is None else value)
        design.append(row)
        targets.append(float(rows[index].spread_bps))

    # Imported here rather than at the top of the function: every refusal
    # above is a statement about the arguments and is owed to a caller whether
    # or not the extra is installed.
    estimator_class = _estimator_class()
    # Read in the same breath as the class the fits are made with, so the
    # versions a record publishes are those of the modules that did the fitting.
    versions = _library_versions()

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

    # The residual sample, about this model's own rearranged median rather than
    # about the 0.50 fit: the two differ exactly on the rows where that fit
    # crossed a neighbour, and there the estimator's value is not the centre of
    # the distribution the model reports.
    centre = grid.index(_MEDIAN_LEVEL)
    residuals = [
        target - vector[centre]
        for vector, target in zip(_rearranged(estimators, design), targets)
    ]
    return FittedGradientBoostedQuantiles(
        estimators,
        names,
        imputations,
        residuals,
        declared,
        grid,
        random_state,
        ml_libraries=versions,
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
