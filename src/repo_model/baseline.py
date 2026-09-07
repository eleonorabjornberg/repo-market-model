"""Leakage-safe baselines and rolling-origin evaluation.

The forecast interface `AGENT_CONTRACT.md` declares --

    fit(train_frame)            -> fitted model carrying its cutoff
    predict(feature_row)        -> quantile vector at contract.QUANTILE_LEVELS
    predict_stress(feature_row) -> exceedance vector aligned to the declared taus_bp

-- has two implementers here, which is the point of the second one.

`FittedPersistence` is the persistence-plus-empirical-residual baseline. It
reads exactly one thing from a feature row, `spread_bps`, and fits nothing but a
residual vector.

`FittedArx` is the first challenger: an autoregressive term plus caller-declared
exogenous regressors, least squares by normal equations, with a predictive
distribution taken from leave-one-out residuals. It exists to convert the
interface from a description of `FittedPersistence` into a constraint. Three
things only a second implementer can establish are established by it: that a
model reading more of `values` than `spread_bps` can go through `fit`; that
`_exceedance_from_residuals` derives stress from *an* empirical residual law
rather than from persistence's in particular; and that a fitted transform with
real parameters -- here the imputation means -- is confined to `fit`, which
contract test 3 had nothing to bite on while persistence was the only model.

`FittedForecastModel` is the shape both satisfy. It stays in this module rather
than moving to `contract.py`: the rule at AGENT_CONTRACT.md's "The shape is
executable, and owned by neither track" is for shapes shared *by both tracks*,
and Track A fits no models. If Track A ever needs to import it, that is a
contract question and not a refactor.

`rolling_persistence_backtest` takes the fitting call as an argument and
defaults to persistence, so it scores the interface rather than one member of
it. The name is unchanged because it is the name the last block's merge record
and the existing assertions refer to; "persistence" in it now names the default,
not the only option.

It also takes its folds from `repo_model.splits.rolling_origin` rather than
walking the index itself, which is what makes the purge gap reach the benchmark
numbers at all. Until it did, `rolling_origin` was fully implemented, fully
tested, carried the project's only purge boundary -- and nothing in the model
path called it, so its guards had never guarded a reported number. The feature
row follows from the fold rather than from the calendar: see `_feature_index`.

The gap itself is no longer anybody's to type. The backtest takes a declared
`features` set, resolves it through `contract.sources_for_features`, and sizes
the gap with `registry.max_release_lag_days` over exactly those sources. That
closes the question the purge block left open -- the number was required, and
nothing checked that whoever produced it covered what the model reads -- and it
is the first time this seam has been answered rather than routed around. The
declaration is verified against the first fitted model, because a declaration
nothing checks is a comment.
"""

from __future__ import annotations

import math
from bisect import bisect_right
from dataclasses import dataclass
from datetime import date, time
from types import MappingProxyType
from typing import (
    Callable,
    Iterable,
    List,
    Mapping,
    Optional,
    Protocol,
    Sequence,
    Tuple,
)

from .contract import QUANTILE_LEVELS, sources_for_features
from .data import DailyObservation, load_stress_thresholds
from .metrics import _validate_levels
from .registry import max_release_lag_days
from .splits import (
    LookAheadError,
    clears_purge,
    ensure_strictly_ascending,
    rolling_origin,
)


#: `event_eval.FitPredict`, restated as a type alias rather than imported, so
#: `baseline` does not depend on the evaluator it feeds. The evaluator validates
#: the shape at the boundary; this is documentation with a name.
ExceedancePredictor = Callable[
    [Sequence[date], Sequence[float], Sequence[date], Sequence[float]],
    Sequence[Sequence[float]],
]


class FittedForecastModel(Protocol):
    """What `fit` returns and what every consumer of a fitted model may assume.

    The contract writes the forecast interface as three calls and says "every
    fitted object carries the cutoff it was fitted at". This is that sentence,
    executable. It is a `typing.Protocol` rather than a base class on purpose:
    the models here share an interface and no implementation, and a shared base
    would invite one model's incidental shape to become the other's inheritance.

    `predict_stress` takes `taus` so the derivation can be checked at the levels
    `predict` reports -- see `FittedPersistence.predict_stress` -- and defaults
    to the declared `taus_bp` family. `trained_beyond` is here because a fitted
    model that cannot answer "were you fitted past this row?" cannot be audited
    for look-ahead by anything downstream of the fit.

    Structural, not nominal: nothing declares that it implements this, and
    `tests/test_contract.py::ForecastInterfaceCoverageTests` discovers the
    implementations in this module rather than reading a list.
    """

    cutoff: date
    levels: Tuple[float, ...]

    @property
    def residuals(self) -> Tuple[float, ...]:
        """The fitted residual sample, ascending; the law both outputs read."""

    @property
    def features_read(self) -> Tuple[str, ...]:
        """The panel columns this fitted model reads off a feature row.

        The model's own account of itself, in the panel's vocabulary. It exists
        so `rolling_persistence_backtest` can check a fitted model against the
        feature set the purge was sized from without asking what a source is,
        and without matching on regressor names -- which is the derivation the
        feature-to-source map was declared to avoid.

        In model vocabulary, not source vocabulary: a fitted model does not know
        that `iorb` arrives from `fred_macro_latest_vintage`, and it must not
        have to. `contract.sources_for_features` is the only thing that makes
        that step, and it makes it once, before the first fold.

        Every column the model reads, not only the ones it was told about.
        Persistence was never *given* a feature set and still reads
        `spread_bps`; an ARX reads its autoregressive term as well as its
        declared regressors. A model that answered with only what it was handed
        would let the undeclared half through, which is the check inverted.
        """

    def trained_beyond(self, feature_row: DailyObservation) -> bool: ...

    def point_forecast(self, feature_row: DailyObservation) -> float:
        """The model's own point rule for the day after `feature_row`.

        Named separately from `predict` because the two answer different
        questions and only one of them is the same across models: `predict`
        returns the declared quantile grid, while this is whatever the model
        says the centre is -- the last observed spread for persistence, a
        regression mean for the ARX. A backtest that read the centre off the
        feature row instead would score every model on persistence's point rule
        while reporting its intervals.
        """

    def predict(self, feature_row: DailyObservation) -> Tuple[float, ...]: ...

    def predict_stress(
        self,
        feature_row: DailyObservation,
        taus: Optional[Sequence[float]] = None,
    ) -> Tuple[float, ...]: ...


class MissingRegressorError(ValueError):
    """A feature row does not carry a regressor the fitted model declared.

    Distinct from the regressor being present and unobserved. `values` is a
    `Mapping[str, Optional[float]]`, so an absent key and a `None` are two
    different facts, and AGENT_CONTRACT.md's contract test 5 requires they stay
    distinguishable "at every stage". A model that cannot read a column it was
    fitted on has been handed the wrong frame; a model handed a column with no
    observation on that day has been handed a gap, which `fit` fitted an
    imputation for. Collapsing the two -- in either direction -- is the silent
    coercion the contract prohibits.

    A `ValueError` subclass so the CLI dispatcher's `(OSError, ValueError)`
    already covers it without naming a new type.
    """


class SingularDesignError(ValueError):
    """The normal equations have no unique solution on this training window.

    Raised rather than solved approximately. A rank-deficient design means the
    declared regressors do not identify separate coefficients on this window --
    a constant column, a duplicate, an exact linear combination -- and any
    number returned would be one arbitrary point on a solution line. Reporting a
    coefficient nobody can reproduce is worse than refusing to fit.
    """


@dataclass(frozen=True)
class Forecast:
    actual_bps: float
    predicted_bps: float
    lower_bps: float
    upper_bps: float


@dataclass(frozen=True)
class BacktestReport:
    forecasts: Sequence[Forecast]
    mae_bps: float
    interval_coverage: float
    #: The model fitted at the last origin the backtest reached. Present so a
    #: reader can ask the reported run what it was fitted at, and so the
    #: interval bounds above have a named source rather than being a second
    #: derivation that happens to agree. Typed to the interface, not to
    #: persistence: the backtest scores whichever model it was given.
    model: Optional[FittedForecastModel] = None
    #: The feature set the caller declared, and the two facts derived from it:
    #: the sources those features draw on and the gap those sources produced.
    #:
    #: Carried on the report rather than recomputed by whoever prints it. A
    #: reporter that re-derived them would be a second derivation of the number
    #: that shaped the run, and the two could agree today and drift later --
    #: which is how a benchmark comes to report a `purge_days` it did not use.
    #: `cli_eval` prints these three straight off the report for that reason.
    features: Tuple[str, ...] = ()
    sources: Tuple[str, ...] = ()
    purge_days: int = 0


#: The interval `rolling_persistence_backtest` reports, derived from the
#: declared levels rather than restated beside them. The outermost declared
#: pair spans this much probability mass; a backtest that named its own number
#: would be a second declaration of the same thing, and the two could drift.
INTERVAL_PROBABILITY = QUANTILE_LEVELS[-1] - QUANTILE_LEVELS[0]


def _quantile(values: Sequence[float], probability: float) -> float:
    if not values:
        raise ValueError("quantile requires at least one value")
    ordered = sorted(values)
    position = probability * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


class FittedPersistence:
    """The persistence baseline, fitted: a point rule plus a residual law.

    The point forecast is the last observed spread. The predictive distribution
    around it is the empirical distribution of one-step residuals over the
    training frame, and every number this object reports -- quantiles and
    exceedances alike -- is read off that one law.

    Fitted state is the sorted residual vector and the cutoff. Both are set in
    `fit` and nowhere else, which is the contract's "any transform with learned
    parameters ... is fitted inside `fit` and nowhere else": there is no lazy
    re-estimation on the first `predict`, and no path that lets a later call see
    a row the cutoff excluded.

    `cutoff` is the last date the training frame was allowed to contain. It is
    carried because a fitted model that cannot say what it was allowed to see
    cannot be audited for leakage, and because `event_eval` and `rolling_origin`
    both hand out training sets whose end date is the entire point. Predicting
    from a `feature_row` dated at or before the cutoff is not automatically
    wrong -- an in-sample diagnostic is a legitimate thing to want -- so it is
    not refused here. What is refused is not being able to tell:
    `trained_beyond` answers the question directly.
    """

    __slots__ = ("_residuals", "cutoff", "levels")

    def __init__(
        self,
        residuals: Sequence[float],
        cutoff: date,
        levels: Sequence[float] = QUANTILE_LEVELS,
    ) -> None:
        #: Sorted once, at fit time. `_quantile` sorts defensively too; keeping
        #: the fitted copy ordered is what makes the exceedance inversion below
        #: read the same order statistics the quantiles come from.
        self._residuals: Tuple[float, ...] = tuple(sorted(float(r) for r in residuals))
        self.cutoff: date = cutoff
        self.levels: Tuple[float, ...] = _validate_levels(levels)

    def __repr__(self) -> str:  # pragma: no cover - diagnostic only
        return (
            f"FittedPersistence(cutoff={self.cutoff.isoformat()}, "
            f"residuals={len(self._residuals)})"
        )

    @property
    def residuals(self) -> Tuple[float, ...]:
        """The fitted residual sample, ascending. A copy-free read-only view."""

        return self._residuals

    @property
    def features_read(self) -> Tuple[str, ...]:
        """`spread_bps`, and nothing else. The persistence rule, as a claim.

        A constant, because the model is one: `point_forecast` returns
        `feature_row.spread_bps` and `predict` adds a residual quantile to it,
        and neither touches `values` again. Stated here rather than inferred by
        a caller, so that "persistence reads only the spread" stops being an
        incidental property a reader of this class might rely on and becomes
        something the class asserts and a backtest can check.
        """

        return ("spread_bps",)

    def trained_beyond(self, feature_row: DailyObservation) -> bool:
        """Was this model fitted on rows dated after `feature_row`?

        True means the predictive distribution saw the feature row's own future.
        That is look-ahead relative to this forecast origin, and a caller
        reporting such a forecast as out-of-sample is reporting a leak. The
        model states the fact and leaves the judgement to the caller, because
        the same condition is exactly what an in-sample diagnostic wants.
        """

        return feature_row.date < self.cutoff

    def point_forecast(self, feature_row: DailyObservation) -> float:
        """The last observed spread. The persistence rule, stated once.

        `predict` and `rolling_persistence_backtest` both anchor here rather
        than each writing `feature_row.spread_bps`, so the point rule and the
        quantiles around it cannot drift apart.
        """

        return feature_row.spread_bps

    def predict(self, feature_row: DailyObservation) -> Tuple[float, ...]:
        """One predicted spread quantile per declared level, in declared order.

        The persistence point forecast shifted by the fitted residual quantile
        at each level. Ascending, because `levels` is ascending and `_quantile`
        is non-decreasing in its probability.
        """

        anchor = self.point_forecast(feature_row)
        return tuple(anchor + _quantile(self._residuals, level) for level in self.levels)

    def predict_stress(
        self,
        feature_row: DailyObservation,
        taus: Optional[Sequence[float]] = None,
    ) -> Tuple[float, ...]:
        """`P(spread > tau)` per tau, derived from the distribution `predict` reports.

        Not a separately fitted classifier. `AGENT_CONTRACT.md`, Target: stress
        "is an exceedance **derived from the predictive distribution**", and the
        derivation here is literal -- this is the inverse of `predict`'s own
        quantile function over the same fitted residuals. At a declared level
        `q`, `predict_stress` evaluated at `predict`'s `Q(q)` returns `1 - q`,
        which is the property that distinguishes this implementation from a
        classifier fitted on the `stress_gt_*` label columns. A label-fitted
        classifier can be perfectly calibrated in isolation and still fail that
        equality, because nothing ties it to the quantiles.

        `taus` defaults to the `taus_bp` family declared in
        `metadata/stress_thresholds.json`, read from where Track A declared it
        rather than restated here, and the returned vector is aligned to that
        order. It is accepted as an argument so the agreement above is testable
        at the levels `predict` reports, without a second exceedance code path
        existing to test.

        Exceedance is strict `P(Y > tau)`, matching the contract's
        `P(spread > tau)` and the label columns' `stress_gt_*`.

        Raises:
            ValueError: if the tau family is empty, non-finite, or not strictly
                ascending. Non-increasing output is only meaningful against an
                increasing input, and `metrics._validate_grid` rejects the rest.
        """

        family = _validate_taus_bp(
            load_stress_thresholds()["taus_bp"] if taus is None else taus
        )
        anchor = self.point_forecast(feature_row)
        return tuple(
            _exceedance_from_residuals(self._residuals, tau - anchor) for tau in family
        )


def _validate_taus_bp(taus: Sequence[float]) -> Tuple[float, ...]:
    family = tuple(float(tau) for tau in taus)
    if not family:
        raise ValueError("no stress thresholds declared")
    for position, tau in enumerate(family):
        if not math.isfinite(tau):
            raise ValueError(f"tau {position} is not finite: {tau!r}")
        if position and tau <= family[position - 1]:
            raise ValueError("stress thresholds must be strictly ascending")
    return family


def _exceedance_from_residuals(ordered: Sequence[float], residual: float) -> float:
    """`P(R > residual)` under the same interpolated law `_quantile` inverts.

    `_quantile` reads the sorted sample at position `p * (n - 1)`, interpolating
    linearly between neighbouring order statistics. This walks that map
    backwards: find where `residual` sits between two order statistics, convert
    the position back to a probability, and return the mass above it. The two
    are inverses by construction, which is what makes `predict_stress` a
    statement about `predict`'s distribution rather than a second opinion.

    Outside the fitted support the answer saturates: below the smallest residual
    everything exceeds, at or above the largest nothing does. No smoothing and
    no prior, for the reason `climatology_exceedance` gives at length -- a
    Laplace correction here would be a prior nobody declared, and it would turn
    the most informative result the evaluator can produce, a model that put no
    weight where the event went, into a small number that merely looks poor.

    Ties are the one place the inversion is approximate. A repeated residual
    makes `_quantile` constant over a range of probabilities, so it has no
    single inverse; the lower end of the range is returned, and the round trip
    through a tied value comes back at most one order statistic low. Real
    one-step residuals in basis points do not tie, and the agreement test says
    so explicitly rather than relying on it silently.
    """

    count = len(ordered)
    if count == 0:
        raise ValueError("exceedance requires at least one fitted residual")
    if count == 1:
        return 1.0 if residual < ordered[0] else 0.0
    if residual < ordered[0]:
        return 1.0
    if residual >= ordered[-1]:
        return 0.0

    upper = bisect_right(ordered, residual)
    lower = upper - 1
    span = ordered[upper] - ordered[lower]
    weight = 0.0 if span <= 0.0 else (residual - ordered[lower]) / span
    return 1.0 - (lower + weight) / (count - 1)


def fit(
    train_frame: Sequence[DailyObservation],
    cutoff: Optional[date] = None,
    minimum_history: int = 20,
    levels: Sequence[float] = QUANTILE_LEVELS,
) -> FittedPersistence:
    """Fit the persistence baseline on `train_frame` and return the fitted model.

    Args:
        train_frame: the training rows, strictly ascending by date. Residuals
            are the one-step differences within this frame and nothing else.
        cutoff: the last date the model was allowed to see. Defaults to the
            frame's own last date. Passed explicitly by callers that were handed
            a cutoff -- `rolling_origin` and `event_eval` both are -- so the
            frame can be checked against it rather than trusted.
        minimum_history: the shortest frame that may produce a fitted law. A
            residual quantile from a handful of rows is not a residual law.
        levels: the quantile grid, defaulting to the declared one. A model that
            wants different levels is a new model, not a config change; the
            argument exists so a caller can be explicit, not so the grid can be
            tuned.

    Returns:
        A `FittedPersistence` carrying its sorted residuals and its cutoff.

    Raises:
        LookAheadError: if any training row is dated after `cutoff`. That is the
            eligibility rule of contract test 1 at the model boundary, and it
            raises rather than asserts because `python -O` strips asserts and a
            leakage guard that vanishes under an optimisation flag is not one.
        SplitError: if the frame is not strictly ascending by date. Out of
            order, a "one-step residual" is a difference against an arbitrary
            other row.
        ValueError: if the frame is shorter than `minimum_history`.
    """

    rows = list(train_frame)
    if len(rows) < minimum_history:
        raise ValueError(
            f"persistence needs at least {minimum_history} training rows, got "
            f"{len(rows)}; a residual quantile from fewer is not a fitted law"
        )

    dates = [row.date for row in rows]
    ensure_strictly_ascending(dates, label="training frame dates")

    declared = dates[-1] if cutoff is None else cutoff
    if dates[-1] > declared:
        raise LookAheadError(
            f"training frame reaches {dates[-1]}, past its cutoff {declared}; "
            f"a fitted model may not contain a row it was not allowed to see"
        )

    residuals = [
        rows[index].spread_bps - rows[index - 1].spread_bps
        for index in range(1, len(rows))
    ]
    return FittedPersistence(residuals, declared, levels)


def _solve(matrix: Sequence[Sequence[float]], rhs: Sequence[float]) -> Tuple[float, ...]:
    """Gaussian elimination with partial pivoting. Stdlib, and deliberately dull.

    Partial pivoting rather than none because the design columns here are raw
    market levels -- reserve balances in the thousands beside a spread in single
    basis points -- and without a pivot the elimination divides by whichever
    number happened to be on the diagonal.

    A pivot at or below `tolerance` is a rank-deficient system, not a small one:
    the tolerance is scaled by the largest magnitude in the matrix so it means
    the same thing whether the Gram entries are 1e0 or 1e8.

    Raises:
        SingularDesignError: if no usable pivot exists in a column.
    """

    size = len(rhs)
    augmented = [list(row) + [float(value)] for row, value in zip(matrix, rhs)]
    scale = max((abs(value) for row in matrix for value in row), default=0.0)
    tolerance = 1e-12 * max(scale, 1.0)

    for column in range(size):
        pivot_row = max(range(column, size), key=lambda r: abs(augmented[r][column]))
        if abs(augmented[pivot_row][column]) <= tolerance:
            raise SingularDesignError(
                f"the normal equations are rank deficient at column {column}: the "
                f"largest available pivot is {augmented[pivot_row][column]!r}, at or "
                f"below the scaled tolerance {tolerance!r}. The declared regressors "
                f"do not identify separate coefficients on this window -- a constant "
                f"column, a duplicate, or an exact linear combination of the others"
            )
        augmented[column], augmented[pivot_row] = augmented[pivot_row], augmented[column]
        pivot = augmented[column][column]
        for row in range(column + 1, size):
            factor = augmented[row][column] / pivot
            if factor == 0.0:
                continue
            for position in range(column, size + 1):
                augmented[row][position] -= factor * augmented[column][position]

    solution = [0.0] * size
    for row in reversed(range(size)):
        total = augmented[row][size] - sum(
            augmented[row][position] * solution[position]
            for position in range(row + 1, size)
        )
        solution[row] = total / augmented[row][row]
    return tuple(solution)


def _least_squares(
    design: Sequence[Sequence[float]], targets: Sequence[float]
) -> Tuple[float, ...]:
    """Ordinary least squares by the normal equations `(X'X) b = X'y`.

    Normal equations rather than a QR factorisation because the contract says
    stdlib and a QR written here would be a numerical library nobody asked for.
    The cost is a squared condition number, which is why `_solve` refuses a
    rank-deficient system loudly instead of returning the smaller of two
    indistinguishable answers, and why the design is left in its natural units:
    centring the columns would condition the problem better and would also map
    an imputed value onto exactly 0.0 inside the design matrix, which is the one
    place AGENT_CONTRACT.md's test 5 says a zero must never appear by accident.
    """

    columns = len(design[0])
    gram = [
        [sum(row[i] * row[j] for row in design) for j in range(columns)]
        for i in range(columns)
    ]
    moment = [
        sum(row[i] * target for row, target in zip(design, targets))
        for i in range(columns)
    ]
    return _solve(gram, moment)


def _dot(coefficients: Sequence[float], row: Sequence[float]) -> float:
    return sum(c * x for c, x in zip(coefficients, row))


def _leave_one_out_residuals(
    design: Sequence[Sequence[float]], targets: Sequence[float]
) -> List[float]:
    """Residuals from fits that never saw the row they are scored on.

    An ARX chose its coefficients to make its in-sample residuals small, so
    quantiles read off them describe how well the fit interpolated its own
    training data, not how wide next period's forecast should be. The narrowing
    grows with the number of regressors, which means the more regressors an ARX
    declares the better calibrated it appears -- a reported coverage that
    improves with model complexity for reasons that have nothing to do with
    forecasting. `METHODOLOGY.md` sec. 9 exists to keep numbers like that out of
    the record.

    So the law reported here is the leave-one-out law: for each design row, refit
    on every other row and score the held-out one. No residual in the vector was
    ever minimised by the coefficients that produced it.

    Refitting `n` times rather than using the closed form `e_i / (1 - h_ii)` --
    which is algebraically the same number -- because the two-line version is
    checkable by reading it, and the hat-matrix version needs `(X'X)^-1` and an
    argument about why `h_ii` is safely below 1. The cost is `n` small solves per
    fit; on this repository's panels that is microseconds, and if a real panel
    ever makes it matter the closed form is the drop-in.

    Raises:
        SingularDesignError: if dropping a row leaves the design rank deficient.
            That is a real property of the declared regressor set on this window
            -- one row is carrying the identification of a coefficient -- and a
            law assembled from the folds that happened to survive would be a
            quiet subsample.
    """

    residuals = []
    for index in range(len(design)):
        reduced_design = list(design[:index]) + list(design[index + 1 :])
        reduced_targets = list(targets[:index]) + list(targets[index + 1 :])
        try:
            coefficients = _least_squares(reduced_design, reduced_targets)
        except SingularDesignError as error:
            raise SingularDesignError(
                f"the design is rank deficient with row {index} held out, though "
                f"it is identified on the full window; one row is carrying a "
                f"coefficient. Declare fewer regressors or fit on more history"
            ) from error
        residuals.append(targets[index] - _dot(coefficients, design[index]))
    return residuals


def _raw_regressor(
    row: DailyObservation, name: str, where: str
) -> Optional[float]:
    """The declared regressor as the row carries it: a float, or `None`.

    Absent key and `None` are returned as different things -- a raise and a
    `None` -- because they are different facts. See `MissingRegressorError`.
    """

    try:
        raw = row.values[name]
    except KeyError:
        raise MissingRegressorError(
            f"{where} for {row.date} carries no {name!r}; the model was fitted on "
            f"that regressor and cannot read it here. An absent column is not an "
            f"unobserved value: an unobserved value arrives as None and is imputed "
            f"from the fitted training-window mean, and treating a missing column "
            f"as one would forecast from a number the row never contained"
        ) from None
    if raw is None:
        return None
    value = float(raw)
    if not math.isfinite(value):
        raise ValueError(
            f"{where} for {row.date} carries a non-finite {name!r}: {raw!r}"
        )
    return value


class FittedArx:
    """An ARX quantile model, fitted: coefficients, imputations, a residual law.

    The point forecast for the day after a feature row is

        b0 + b1 * spread_bps(row) + sum_j c_j * x_j(row)

    over the regressors the caller declared, fitted by least squares on the
    training frame's own one-step-ahead pairs. The predictive distribution around
    it is the empirical law of the leave-one-out residuals, read at
    `contract.QUANTILE_LEVELS` exactly as persistence reads its one-step
    differences -- same declared grid, same `_quantile`, same inversion for
    stress. What differs between the two models is where the residuals come
    from, and nothing else.

    Fitted state, all of it set in `fit_arx` and nowhere else:

    * `regressors` -- the ordered names this model was fitted on. Carried
      because a model that cannot say what it read cannot be audited, and
      because two models compared on quietly different regressor sets are not
      being compared. There is no repository-wide feature-set declaration to
      read them from; the caller declares them, and the fitted object records
      the declaration. See the block record for why that is a stopgap.
    * `imputations` -- the training-window mean of each regressor's observed
      values. The only transform with learned parameters in either model, and
      therefore the first thing contract test 3 has ever had to bite on.
    * `coefficients` -- ordered to match `design_names`.
    * `_residuals` -- the sorted leave-one-out residual vector.
    * `cutoff` -- the last date the training frame was allowed to contain, with
      the same meaning and the same `trained_beyond` question as persistence.

    A feature row missing a declared regressor raises `MissingRegressorError`. A
    feature row carrying it as `None` gets the fitted mean. Neither becomes
    `0.0`.
    """

    __slots__ = (
        "_residuals",
        "coefficients",
        "cutoff",
        "imputations",
        "levels",
        "regressors",
    )

    def __init__(
        self,
        coefficients: Sequence[float],
        regressors: Sequence[str],
        imputations: Mapping[str, float],
        residuals: Sequence[float],
        cutoff: date,
        levels: Sequence[float] = QUANTILE_LEVELS,
    ) -> None:
        self.regressors: Tuple[str, ...] = tuple(regressors)
        self.coefficients: Tuple[float, ...] = tuple(float(c) for c in coefficients)
        #: Read-only so a caller cannot retune a fitted transform after the
        #: fact, which would put the reported coefficients and the imputation
        #: that produced them out of step with no diff to show for it.
        self.imputations: Mapping[str, float] = MappingProxyType(
            {name: float(imputations[name]) for name in self.regressors}
        )
        self._residuals: Tuple[float, ...] = tuple(sorted(float(r) for r in residuals))
        self.cutoff: date = cutoff
        self.levels: Tuple[float, ...] = _validate_levels(levels)

    def __repr__(self) -> str:  # pragma: no cover - diagnostic only
        return (
            f"FittedArx(cutoff={self.cutoff.isoformat()}, "
            f"regressors={list(self.regressors)}, "
            f"residuals={len(self._residuals)})"
        )

    @property
    def design_names(self) -> Tuple[str, ...]:
        """The coefficient order, named. `coefficients[i]` multiplies `[i]`."""

        return ("intercept", "spread_bps") + self.regressors

    @property
    def residuals(self) -> Tuple[float, ...]:
        """The fitted leave-one-out residual sample, ascending."""

        return self._residuals

    @property
    def features_read(self) -> Tuple[str, ...]:
        """`spread_bps` plus the declared regressors, in `design_names` order.

        Derived from `design_names` with the intercept dropped, rather than
        rebuilt from `regressors`: `design_row` reads the feature row in
        `design_names` order, so anything that column order gains this answer
        gains too. A second tuple assembled here could agree today and diverge
        the first time the design grows a term.

        The intercept is dropped because it is the one design column that is not
        read off the row -- it is the constant 1.0, and reporting it would have
        the backtest demand that a caller declare `intercept` as a feature and
        `contract.FEATURE_SOURCES` carry a source for it.
        """

        return tuple(name for name in self.design_names if name != "intercept")

    def trained_beyond(self, feature_row: DailyObservation) -> bool:
        """Was this model fitted on rows dated after `feature_row`?

        Same question, same answer, same reason as `FittedPersistence`.
        """

        return feature_row.date < self.cutoff

    def design_row(self, feature_row: DailyObservation) -> Tuple[float, ...]:
        """The feature row as this model reads it, in `design_names` order.

        Public because it is the auditable half of a forecast: it says exactly
        which numbers went into the point estimate, including which ones were
        imputed. Raises `MissingRegressorError` if the row does not carry a
        declared regressor.
        """

        values = [1.0, feature_row.spread_bps]
        for name in self.regressors:
            observed = _raw_regressor(feature_row, name, "feature row")
            values.append(self.imputations[name] if observed is None else observed)
        return tuple(values)

    def point_forecast(self, feature_row: DailyObservation) -> float:
        """The conditional mean the quantiles are centred on."""

        return _dot(self.coefficients, self.design_row(feature_row))

    def predict(self, feature_row: DailyObservation) -> Tuple[float, ...]:
        """One predicted spread quantile per declared level, in declared order.

        The point forecast shifted by the fitted residual quantile at each
        level. Ascending, because `levels` is ascending and `_quantile` is
        non-decreasing in its probability.
        """

        anchor = self.point_forecast(feature_row)
        return tuple(anchor + _quantile(self._residuals, level) for level in self.levels)

    def predict_stress(
        self,
        feature_row: DailyObservation,
        taus: Optional[Sequence[float]] = None,
    ) -> Tuple[float, ...]:
        """`P(spread > tau)` per tau, derived from the law `predict` reports.

        Character for character the same derivation as persistence, over this
        model's own residual vector: `_exceedance_from_residuals` inverts
        `_quantile`, so `predict_stress` evaluated at `predict`'s `Q(q)` returns
        `1 - q` here for the same reason it does there. That the function needed
        no change to serve a second model is the evidence that the derivation
        was a property of the interface rather than of persistence.

        Not a classifier fitted on the `stress_gt_*` label columns; nothing in
        this object was fitted to a label.
        """

        family = _validate_taus_bp(
            load_stress_thresholds()["taus_bp"] if taus is None else taus
        )
        anchor = self.point_forecast(feature_row)
        return tuple(
            _exceedance_from_residuals(self._residuals, tau - anchor) for tau in family
        )


def fit_arx(
    train_frame: Sequence[DailyObservation],
    regressors: Sequence[str],
    cutoff: Optional[date] = None,
    minimum_history: int = 20,
    levels: Sequence[float] = QUANTILE_LEVELS,
) -> FittedArx:
    """Fit the ARX on `train_frame` over `regressors` and return the fitted model.

    Args:
        train_frame: the training rows, strictly ascending by date. The design
            is this frame's own one-step-ahead pairs and nothing else: row `i`'s
            spread is regressed on row `i-1`'s spread and row `i-1`'s
            regressors, so a fit on `n` rows has `n - 1` design rows, the same
            count as persistence's `n - 1` residuals.
        regressors: the ordered exogenous regressor names, read from each
            origin row's `values`. **Required, with no default**, for the reason
            `rolling_origin` refuses a default `purge` and `max_release_lag_days`
            refuses a default `decision_time`: a default here would be a silent
            assumption about which columns a model is entitled to, and nothing in
            this repository declares that. Naming them at the call site keeps the
            assumption visible and keeps the fitted object able to report it.
        cutoff: the last date the model was allowed to see. Defaults to the
            frame's own last date.
        minimum_history: the shortest frame that may produce a fitted law.
        levels: the quantile grid, defaulting to the declared one.

    Returns:
        A `FittedArx` carrying its coefficients, its regressor names, its fitted
        imputation means, its sorted leave-one-out residuals and its cutoff.

    Raises:
        LookAheadError: if any training row is dated after `cutoff`.
        SplitError: if the frame is not strictly ascending by date.
        MissingRegressorError: if a training row does not carry a declared
            regressor.
        SingularDesignError: if the declared regressors do not identify separate
            coefficients on this window.
        ValueError: if no regressors are declared, if one is declared twice, if
            the frame is shorter than `minimum_history`, if the design has too
            few rows to leave one out, or if a regressor is unobserved on every
            row of the training window.
    """

    names = tuple(str(name) for name in regressors)
    if not names:
        raise ValueError(
            "no regressors declared; an ARX with no exogenous term is an AR, and "
            "an empty list is how a caller omits the decision rather than makes "
            "it. Name the regressors, even if the honest answer is one of them"
        )
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise ValueError(
            f"regressors declared more than once: {duplicates}; a duplicated "
            f"column makes the design rank deficient and its two coefficients "
            f"meaningless individually"
        )

    rows = list(train_frame)
    if len(rows) < minimum_history:
        raise ValueError(
            f"arx needs at least {minimum_history} training rows, got {len(rows)}; "
            f"a coefficient and a residual law from fewer is not a fitted model"
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
    # these, are the rows the transform below is fitted on -- which is what
    # contract test 3 means by "recomputed on a training window alone".
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
                f"coercion contract test 5 prohibits. Three columns of the sample "
                f"panel are empty throughout and this is what happens to them"
            )
        imputations[name] = sum(seen) / len(seen)

    design = []
    targets = []
    for index in range(1, len(rows)):
        origin = rows[index - 1]
        row = [1.0, origin.spread_bps]
        for name in names:
            value = _raw_regressor(origin, name, "training row")
            row.append(imputations[name] if value is None else value)
        design.append(row)
        targets.append(rows[index].spread_bps)

    columns = len(names) + 2
    if len(design) - 1 < columns + 1:
        raise ValueError(
            f"{len(design)} design rows against {columns} coefficients; a "
            f"leave-one-out fit needs at least {columns + 2} so every fold keeps "
            f"a degree of freedom. Declare fewer regressors or fit on more history"
        )

    coefficients = _least_squares(design, targets)
    residuals = _leave_one_out_residuals(design, targets)
    return FittedArx(coefficients, names, imputations, residuals, declared, levels)


def predict(
    model: FittedForecastModel, feature_row: DailyObservation
) -> Tuple[float, ...]:
    """`model.predict(feature_row)`, as the module-level name the contract lists.

    The contract writes the interface as three calls. The fitted object is where
    the state lives, so these two are thin and deliberately hold no logic of
    their own -- a second implementation behind the same name is precisely what
    the last block existed to prevent.

    Typed to `FittedForecastModel` rather than to `FittedPersistence`: the
    annotation used to name the only implementation there was, which is how a
    second one gets read as an exception to the interface rather than a member
    of it.
    """

    return model.predict(feature_row)


def predict_stress(
    model: FittedForecastModel,
    feature_row: DailyObservation,
    taus: Optional[Sequence[float]] = None,
) -> Tuple[float, ...]:
    """`model.predict_stress(feature_row, taus)`. See `predict` on why this is thin."""

    return model.predict_stress(feature_row, taus)


#: The fitting call `rolling_persistence_backtest` refits at every origin:
#: `(train_frame, minimum_history=...) -> fitted model`. `fit` and
#: `functools.partial(fit_arx, regressors=(...))` both have this shape, and the
#: partial is how the ARX's required regressor list reaches a backtest without
#: the backtest knowing that regressors exist.
ModelFitter = Callable[..., FittedForecastModel]


def _feature_index(
    dates: Sequence[date],
    train_indices: Sequence[int],
    scored_index: int,
    purge: int,
) -> int:
    """The last training row that cleared the purge gap before `scored_index`.

    Under a gap of zero this is the row before the scored day, which is what the
    backtest used unconditionally before it was purged. Under a gap it is often
    not: `rows[scored_index - 1]` is frequently a row published after the
    scoring window opened, and feeding it to the model is the leak the purge
    exists to stop, re-entering through the one door the purge does not cover.
    Dropping a row from the *training frame* and then reading the model's
    feature off it is not a partial purge, it is no purge at all for the term
    that dominates a persistence forecast.

    The boundary is stated through `clears_purge` rather than by taking
    `train_indices[-1]` on trust, for the reason `rolling_origin` states its own
    guard that way: `rolling_origin` builds the prefix with a `bisect`, and a
    consumer that re-derives the same answer from the same assumption cannot
    disagree with it. Scanning back through the fold's own indices against the
    authoritative comparison can, and the scan is over a prefix so the first
    index it accepts is the last eligible one.

    Raises:
        LookAheadError: if no row in `train_indices` clears the gap. Reaching
            this means the fold itself is malformed, since `rolling_origin`
            refuses to yield such a fold -- so it raises rather than asserts,
            and rather than falling back to a row that does not clear.
    """

    opens = dates[scored_index]
    for index in reversed(tuple(train_indices)):
        if clears_purge(dates[index], opens, purge):
            return index
    raise LookAheadError(
        f"no training row clears the {purge}-day purge gap before "
        f"{opens}; the fold is malformed"
    )


def _check_fitter_stayed_inside(
    model: FittedForecastModel,
    features: Tuple[str, ...],
    sources: Tuple[str, ...],
    purge: int,
) -> None:
    """Raise unless the fitted model read only what the caller declared.

    The purge was sized from `features`, before this model existed. If the
    fitter read a column outside that set, the gap protecting this backtest was
    computed over the wrong sources -- and the error is in the flattering
    direction, because the undeclared column is the one whose release lag was
    never taken into the maximum.

    `LookAheadError`, not `ValueError`: this is a leakage condition, and it is
    the same condition `_feature_index` raises for one level down. Not an
    `assert`, because `python -O` strips asserts and this guard has to survive
    the way the numbers are actually produced.

    Set containment, not order or multiplicity: a model may read fewer columns
    than were declared. Declaring more than the fitter uses purges more than the
    evidence requires, which costs training rows and is visible in the report --
    conservative and legible, so it is not refused here.
    """

    exceeded = tuple(
        name for name in model.features_read if name not in frozenset(features)
    )
    if exceeded:
        raise LookAheadError(
            f"the fitted model reads {list(exceeded)}, which the declared "
            f"feature set {list(features)} does not contain. The "
            f"{purge}-day purge was sized over {list(sources)}, the sources of "
            f"the declaration alone, so the release lag of every undeclared "
            f"column is missing from the gap and the reported numbers were "
            f"produced under too small a one. Declare the column the fitter "
            f"reads rather than widening the gap by hand"
        )


def rolling_persistence_backtest(
    observations: Iterable[DailyObservation],
    *,
    features: Sequence[str],
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    minimum_history: int = 20,
    interval_probability: Optional[float] = None,
    fit_model: Optional[ModelFitter] = None,
) -> BacktestReport:
    """Refit at every purged rolling origin and score the next day.

    Folds come from `repo_model.splits.rolling_origin` at `step=1`, so this is
    the scoring holdout that module documents and the purge is the one boundary
    this project has. At each origin the model is fitted on the training rows
    that cleared the gap and asked for its quantiles; the reported interval is
    the outermost declared pair. Prediction intervals therefore use only the
    fitted model's own numbers over rows it was allowed to see, not a parallel
    derivation that happens to agree with it today.

    **What the purge does to persistence.** With `purge=0` the feature row is
    the day before the scored day and persistence is "yesterday's spread". With
    `purge > 0` the feature row is `_feature_index`'s -- the last day the
    forecaster was allowed to have seen -- and persistence becomes "the spread
    of the last day I was allowed to see". That is a different forecast, and a
    more honest one: at a six-day gap, yesterday's spread is a number that had
    not been published when the forecast was made. Every model here inherits the
    change, because every model reads its feature row from the same place.

    **Where the gap comes from.** The caller declares a feature set; this
    derives `contract.sources_for_features(features)`, then
    `registry.max_release_lag_days(...)` over those sources, then builds folds
    -- the order `cli_eval` already used on the event path. There is no `purge`
    argument. Who computed the number was the open question the purge left
    behind: a caller could declare an ARX on `on_rrp` and size the gap over
    `nyfed_sofr` alone, and nothing checked it, so every number that came out
    looked reasonable. That is the same silent-leak shape as `rows[index - 1]`
    under a purge, one level up -- the gap computed correctly over the wrong
    set.

    **Declaration, then verification.** The gap must be sized before the first
    fold, and the regressors are only known once a model is fitted, so this
    cannot ask an unfitted model what it reads. It does not resolve that by
    fitting a throwaway model to inspect: that fit would be on unpurged data,
    which is the leak arriving through the door built to detect it. Instead the
    declaration sizes the gap and the first fitted model is checked against the
    declaration -- see `_check_fitter_stayed_inside`. The check is cheap and it
    is the whole point: a fitter that exceeded the declaration was purged
    against the wrong sources.

    This module still does not know what a source is. It learns what a *feature
    set* is, which is its own vocabulary, and passes tuples and ints between
    `contract` and `registry`.

    The fitting call is a parameter, so this scores the forecast interface
    rather than one member of it. The name is unchanged: it is what the existing
    assertions and the last block's merge record refer to, and "persistence" in
    it now names the default rather than the only option. Renaming it is a
    follow-up, not a silent side effect of generalising it.

    Args:
        observations: the panel, ascending by date.
        features: the panel columns the model is declared to read.
            **Required, keyword-only, with no default**, for the reason
            `rolling_origin` refuses a default `purge`, `max_release_lag_days`
            refuses a default `decision_time` and `fit_arx` refuses a default
            `regressors`. A default here would be worse than any of those: it
            would be a *silent claim about which sources the model draws on*,
            and the gap derived from it would look computed while being a
            guess. The sources follow from this, and the gap follows from the
            sources; nothing about the gap is set by hand on this path.
        registry: the parsed source registry, for `max_release_lag_days`. This
            function never reads a `release_lag` itself -- a wrong conversion is
            a provenance error and belongs with Track A, per
            AGENT_CONTRACT.md's "The conversion belongs to the data layer".
        decision_time: when the forecast is made, for `max_release_lag_days`.
            Required and undefaulted there, so required and undefaulted here: a
            default would be a silent assumption about the very thing the as-of
            rule exists to make explicit, and passing one through would launder
            it.
        minimum_history: the first origin scored, and the shortest training
            frame any fit is allowed. Passed to `rolling_origin` as `min_train`,
            which counts rows *after* purging -- so a gap that leaves too little
            history raises rather than quietly scoring on a shorter frame.
        interval_probability: accepted only for callers that want to state the
            interval they expect. It is no longer an independent setting: the
            bounds come from `contract.QUANTILE_LEVELS`, and the only value
            those levels admit is `INTERVAL_PROBABILITY`. Pass `None`, the
            default, to read it from the declaration.
        fit_model: the fitting call, `(train_frame, minimum_history=...) ->
            fitted model`. `None`, the default, is persistence's `fit` and
            leaves every number this function has ever reported unchanged. Pass
            `functools.partial(fit_arx, regressors=(...))` to score the ARX. The
            point forecast reported is the fitted model's median, so a model
            whose centre is not the last observed spread is scored on its own
            centre rather than on persistence's.

    Raises:
        ValueError: if the panel is too short, or if `interval_probability`
            names an interval the declared levels do not produce. Silently
            honouring a different number would put the reported coverage and the
            reported interval out of step, which is the drift the derivation
            exists to rule out; adjusting the levels to match is a contract
            question and not this function's to answer.
        SplitError: if `purge` is not a non-negative int, if the panel's dates
            repeat or go backwards, or if the gap leaves no origin with
            `minimum_history` training rows behind it. That last one is a
            refusal on purpose: shrinking `min_train` to recover a fold would
            report a number produced by a rule nobody declared.
        LookAheadError: if a fold's feature row does not clear the gap -- a bug
            here or in the splitter, not bad input -- or if the fitted model
            reads a column outside `features`. The second is the declaration
            being wrong about the model, which means the gap was sized over the
            wrong sources; see `_check_fitter_stayed_inside`.
        UndeclaredFeatureError: if `features` names a column that
            `contract.sources_for_features` cannot classify, or one it declares
            to have no ingesting source. Raised before any fold is built, since
            a feature set that cannot be resolved has no gap and therefore no
            backtest.
        RegistryContractError: if the derived sources cannot support a safe
            bound -- an unknown source, an unusable `release_lag`, or a
            `snapshot_retrieved_at` source without `available_at` on every row.
            Passed through unchanged. It is Track A's refusal and this function
            has no standing to soften it.
    """

    if interval_probability is not None and not math.isclose(
        interval_probability, INTERVAL_PROBABILITY, rel_tol=0.0, abs_tol=1e-12
    ):
        raise ValueError(
            f"interval_probability={interval_probability} is not the interval the "
            f"declared levels produce ({INTERVAL_PROBABILITY}, the span from "
            f"{QUANTILE_LEVELS[0]} to {QUANTILE_LEVELS[-1]}); the interval is read "
            f"from contract.QUANTILE_LEVELS, not set here"
        )

    # Before anything else, and before a single fold: an unresolvable feature
    # set has no gap, so it has no backtest. Resolving first also means the
    # caller who misspells a column gets `UndeclaredFeatureError` naming the
    # column rather than a fold-shaped complaint further in.
    declared: Tuple[str, ...] = tuple(features)
    sources = sources_for_features(declared)
    purge = max_release_lag_days(registry, sources, decision_time=decision_time)

    rows = list(observations)
    if len(rows) <= minimum_history:
        raise ValueError("not enough observations for requested minimum history")

    fitter: ModelFitter = fit if fit_model is None else fit_model

    forecasts: List[Forecast] = []
    model: Optional[FittedForecastModel] = None
    dates = [row.date for row in rows]

    # `step=1` is the origin-by-origin shape this function has always had: one
    # scored row per fold, blocks tiling the tail with no remainder. It is not a
    # parameter, because a larger block would score a day on a model fitted at
    # an origin further back than the day before it, which is a different
    # backtest and would need its own reported horizon.
    for train_indices, test_indices in rolling_origin(
        dates, minimum_history, 1, purge
    ):
        index = test_indices[0]
        # The training frame is the prefix that cleared the gap, so the cutoff
        # `fit` derives from it is the last date the forecaster was allowed to
        # see -- not the day before the scored day, which under a purge is a
        # date whose value had not been published yet.
        fitted = fitter([rows[i] for i in train_indices], minimum_history=minimum_history)
        if model is None:
            # After the first fit, and only the first: the fitter is the same
            # callable at every origin, so a model that stayed inside the
            # declaration here stays inside it at every later one. Checking
            # once keeps this off the hot path without weakening it, and
            # checking *after* the fit is the only order available -- the
            # regressors do not exist before it.
            _check_fitter_stayed_inside(fitted, declared, sources, purge)
        model = fitted
        feature_row = rows[_feature_index(dates, train_indices, index, purge)]
        quantiles = model.predict(feature_row)
        forecasts.append(
            Forecast(
                actual_bps=rows[index].spread_bps,
                # The model's own point rule, not persistence's restated. For
                # persistence this is `feature_row.spread_bps` and every number
                # this function reported before the generalisation is bit-
                # identical; for the ARX it is the regression's conditional
                # mean. Reading it off the model rather than off the feature row
                # is what stops a second model being scored against the first
                # one's centre while wearing its own intervals.
                predicted_bps=model.point_forecast(feature_row),
                lower_bps=quantiles[0],
                upper_bps=quantiles[-1],
            )
        )

    mae = sum(abs(item.actual_bps - item.predicted_bps) for item in forecasts) / len(forecasts)
    coverage = sum(
        item.lower_bps <= item.actual_bps <= item.upper_bps for item in forecasts
    ) / len(forecasts)
    return BacktestReport(
        forecasts, mae, coverage, model, declared, sources, purge
    )


def climatology_exceedance(minimum_history: int = 20) -> ExceedancePredictor:
    """Unconditional exceedance from the training distribution alone.

    The reference `AGENT_CONTRACT.md`, "Decided: stress target and event
    holdouts", names in "Metrics": "Brier skill score **against climatology**".
    A climatology is what a skill score is measured against, so it is the first
    exceedance predictor this repo needs and the only one it needs before there
    is something to compare. It is also the honest predictor for a knowledge
    holdout, where the whole question is what a model that has seen only calm
    history says about a crisis it was never shown.

    Shape is `event_eval.FitPredict`: called once with the training rows, the
    scored dates and the tau family, returning `P(value > tau)` per scored day
    per tau. `P(Y > tau)` is the fraction of training values strictly above
    `tau` -- strictly, matching the contract's `P(spread > tau)` and the label
    columns' `stress_gt_*`.

    Two properties worth stating, because both are deliberate:

    * **The curve is the same on every scored day.** A climatology is
      unconditional by definition; a predictor whose curve moved with the day
      would be conditioning on something, and then it would not be the baseline
      a skill score is measured against. `event_eval` still scores each day
      separately against its own realized value, so the report shows a flat
      predicted curve beside a path that moves, which is the comparison.

    * **No smoothing, no prior.** With no training row above 50bp the answer is
      `0.0`, and it stays `0.0` rather than being nudged to `1/(n+2)`. A
      Laplace correction here would be a prior nobody declared, and it would
      quietly convert the most informative result this evaluator can produce --
      a model that put *no* weight where the event actually went -- into a small
      number that looks like a poor forecast rather than an absent one. Scoring
      rules that cannot take a zero are the caller's problem to raise, and
      `event_eval` computes none.

    Monotonicity is automatic: `taus` arrives strictly ascending, and the count
    of values above a larger threshold cannot exceed the count above a smaller
    one, so `_validate_predictions`' non-increasing check is satisfied by
    construction rather than by rounding.

    Args:
        minimum_history: the shortest training set that may produce a curve. A
            fraction over five rows is not a climatology, and at an event
            boundary the training set is whatever survived the purge -- which
            can be very short without anything else objecting.

    Returns:
        A `fit_predict` callable suitable for `event_eval.evaluate_event_window`.

    Raises:
        ValueError: at call time, if the training set is shorter than
            `minimum_history`. A `ValueError` rather than a bespoke type so the
            CLI dispatcher's `(OSError, ValueError)` already covers it.
    """

    if minimum_history < 1:
        raise ValueError(f"minimum_history must be positive, got {minimum_history}")

    def fit_predict(
        train_dates: Sequence[date],
        train_values: Sequence[float],
        test_dates: Sequence[date],
        taus: Sequence[float],
    ) -> List[Tuple[float, ...]]:
        history = [float(value) for value in train_values]
        if len(history) < minimum_history:
            raise ValueError(
                f"climatology needs at least {minimum_history} training rows, got "
                f"{len(history)}; at an event boundary the training set is whatever "
                "cleared the purge gap, and a curve from a handful of rows is not a "
                "climatology"
            )
        denominator = float(len(history))
        curve = tuple(
            sum(1 for value in history if value > float(tau)) / denominator
            for tau in taus
        )
        return [curve for _ in test_dates]

    return fit_predict
