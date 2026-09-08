"""Leakage-safe baselines and rolling-origin evaluation.

The forecast interface `AGENT_CONTRACT.md` declares --

    fit(train_frame)            -> fitted model carrying its cutoff
    predict(feature_row)        -> quantile vector at contract.QUANTILE_LEVELS
    predict_stress(feature_row) -> exceedance vector aligned to the declared taus_bp

-- has three implementers here, which is the point of the second one and, in a
different way, of the third.

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

`FittedThreshold` is the two-regime ARX, and the fourth benchmark `PLAN.md`
Phase 2 names. It is not a third variation on "read some columns, compute a
number": every model above reads a covariate to *compute* a value, and this one
reads a covariate to *choose a model*. That is a new way for a variable to enter
a forecast, and it is the first thing to test whether the machinery built around
`features_read` was a rule or a habit. The purge is sized over a declared
feature set before anything is fitted and the fitted model is checked against
that declaration afterwards; a threshold model that consulted `on_rrp` to pick
its regime and did not report reading it would have had its gap computed
correctly over the wrong sources, in the flattering direction. So the threshold
variable goes through the same lock as any other read, and `features_read`
carries it. Nothing in the lock needed changing to accommodate it, which is the
result worth having.

`FittedForecastModel` is the shape all three satisfy. It stays in this module rather
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

The exceedance interface
------------------------

`ExceedancePredictor` is the second interface this module declares, and it is
the knowledge holdout's: `event_eval.evaluate_event_window` calls one of these
and scores what comes back. It has two implementers here, for the same reason
the forecast interface needed a second one.

`climatology_exceedance` is the unconditional baseline a Brier skill score is
measured against. `arx_exceedance` is the conditional side of that comparison,
and its curve is `FittedArx.predict_stress` -- the empirical residual law the
ARX already fits, read once per feature row. Until the interface carried rows
rather than one series of values no covariate could reach a model through it,
so the climatology was the only thing the knowledge holdout could score and the
skill score had nothing to be measured against.

That alias was declared twice before this block, here and as
`event_eval.FitPredict`. It is declared once now, here, and the evaluator
imports it -- so `baseline` still does not depend on the evaluator it feeds.
"""

from __future__ import annotations

import hashlib
import math
from bisect import bisect_right
from dataclasses import dataclass
from datetime import date, time, timedelta
from pathlib import Path
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
from .metrics import (
    _validate_levels,
    crps_from_quantiles,
    pinball_loss,
    stationary_bootstrap_interval,
)
from .registry import max_release_lag_days
from .splits import (
    LookAheadError,
    clears_purge,
    ensure_strictly_ascending,
    rolling_origin,
)


@dataclass(frozen=True)
class ExceedanceCurves:
    """What an exceedance predictor returns: the curves, and what it read.

    `curves[day][tau]` is `P(value > taus[tau])` on the scored day at `day`,
    aligned to the feature rows the evaluator handed over and to the tau family
    it declared.

    `features_read` is the same question `FittedForecastModel.features_read`
    answers on the rolling path, in the same panel vocabulary, and it is here
    for the same reason. `event_eval` sizes its purge from a declared feature
    set before anything is fitted; a predictor whose model read a column outside
    that set was purged over the wrong sources, and the error is in the
    flattering direction. A declaration nothing checks is a comment, so the
    interface carries the answer rather than leaving the evaluator to infer it
    from the shape of a callable it cannot see inside.

    It is the predictor's own account of itself, exactly as on the rolling path:
    a predictor that under-reported what it read would defeat the check. That is
    the same trust `_check_fitter_stayed_inside` already places in
    `features_read`, and it is why `FittedArx` derives that tuple from
    `design_names` rather than assembling a second one by hand.
    """

    curves: Tuple[Tuple[float, ...], ...]
    features_read: Tuple[str, ...]


#: The exceedance-predictor interface, declared once and in one place.
#:
#: `event_eval.FitPredict` was an identical `Callable` alias in the evaluator
#: and this was a restatement of it -- two vocabularies for one thing, and a
#: seam nobody declared. The alias lives here, with the models whose shape it
#: describes, and `event_eval` imports it: `baseline` still does not depend on
#: the evaluator it feeds, and there is no longer a second copy to drift.
#:
#: `fit_predict(train_rows, feature_rows, taus) -> ExceedanceCurves`. One curve
#: per feature row. The feature rows are chosen by the evaluator -- the last row
#: that cleared the purge gap before each scored day, by `_feature_index`, the
#: same rule the rolling path uses -- so a predictor cannot pick its own
#: conditioning set and cannot reach a row it was not allowed to see.
#:
#: The rows are `DailyObservation`, not a date-and-value pair, because that is
#: what carries a covariate. The narrower shape this replaces passed one series
#: of values, so the only thing expressible through it was a predictor
#: conditioning on nothing -- which is the climatology, which is the baseline a
#: skill score is measured against. There was nothing on the other side of the
#: comparison.
ExceedancePredictor = Callable[
    [Sequence[DailyObservation], Sequence[DailyObservation], Sequence[float]],
    ExceedanceCurves,
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


class DegenerateRegimeError(ValueError):
    """A threshold leaves one regime with too few rows to fit.

    Raised rather than collapsed to a single-regime fit. A threshold model that
    quietly becomes an ARX still calls itself a threshold model, still reports a
    `threshold` and a `regime`, and its numbers get attributed to a regime
    structure that was never estimated -- which is the worst of the available
    outcomes, because the failure is invisible in the output. Refusing puts the
    frame in front of the caller, who can widen the window, declare a different
    threshold, or conclude that this window has no second regime in it.

    The minimum is not a taste: it is `len(design_names) + 2` rows in each
    regime, the same count `fit_arx` demands of a whole window, and it comes
    from the leave-one-out law. A regime with `columns + 2` design rows has
    `columns + 1` left when one is held out, which is one degree of freedom; at
    `columns` the held-out fit interpolates its rows exactly and every residual
    in that regime is zero, so the pooled law is quietly diluted by a block of
    zeros. Below that the regime's design is not even identified.

    A `ValueError` subclass so the CLI dispatcher's `(OSError, ValueError)`
    already covers it without naming a new type.
    """


class UnobservedThresholdError(ValueError):
    """The threshold variable is present on a row but carries no observation.

    Distinct from the column being absent, which is `MissingRegressorError`, and
    distinct in the way AGENT_CONTRACT.md test 5 requires an absent key and a
    `None` to stay distinct: two different facts, two different types.

    Unlike a regressor, an unobserved threshold variable is **not imputed**. A
    regressor's fitted mean enters a sum and moves the forecast by a coefficient
    times a number; a threshold variable's imputed mean would choose a *model*.
    Every gap row would be assigned to whichever regime the training mean falls
    in, uniformly and silently, and the regime counts a reader checks would
    include rows whose regime was never observed. Refusing is the only reading
    that does not invent an assignment.
    """


#: The two regimes, in the order every report and every coefficient mapping
#: lists them. Named once and iterated rather than written out at each use, so
#: that "there are exactly two" is a single statement a reader can check and not
#: a pattern spread across a fit, a split and a repr.
REGIMES = ("low", "high")


@dataclass(frozen=True)
class Forecast:
    actual_bps: float
    predicted_bps: float
    lower_bps: float
    upper_bps: float
    #: The full predictive quantile vector the model returned, at
    #: `BacktestReport.quantile_levels`. `lower_bps` and `upper_bps` are its
    #: outermost pair and are kept because every existing consumer reads them
    #: by name; the vector is carried because a quantile loss cannot be
    #: computed from an interval. Defaulted empty so the longhand
    #: reconstruction in `tests/test_baseline.py` -- which reproduces the
    #: unpurged walk as it stood, and must not be edited to track this file --
    #: still constructs.
    quantiles_bps: Tuple[float, ...] = ()


@dataclass(frozen=True)
class ScoredFold:
    """One origin of the rolling backtest, as dates rather than as indices.

    The indices `rolling_origin` yields are positions in a list that only the
    run holds. A published report has to say *when* the training frame ended
    and *which* day was scored, in the panel's own vocabulary, or a reader
    cannot check the gap against the calendar.

    `feature_date` is the row the forecast was conditioned on -- the last day
    the forecaster was allowed to have seen. It is carried beside `train_end`
    because under a purge they are the same date and under a bug they are not,
    and beside `scored_date` because `scored_date - feature_date` is the gap
    made visible on a single row. The event path already reports a feature date
    per scored day for exactly this reason; the rolling path did not, and its
    report is the one this project publishes.
    """

    train_start: date
    train_end: date
    train_rows: int
    feature_date: date
    scored_date: date


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
    #: The remaining conditions the numbers were produced under. `decision_time`
    #: is half of what sized the gap -- `max_release_lag_days` takes it and a
    #: registry, and the same registry at a different decision time gives a
    #: different number -- so a report carrying the gap without it carries half
    #: the derivation. `minimum_history` set the first origin and the shortest
    #: frame any fit was allowed.
    #:
    #: Both are `None` on a report that was not built by
    #: `rolling_persistence_backtest`, because a report that cannot say what it
    #: ran under must not claim a default. See `backtest_document`: a field it
    #: cannot compute is absent from the artifact, never defaulted into it.
    decision_time: Optional[time] = None
    minimum_history: Optional[int] = None
    #: The panel this run consumed, as the run measured it. The bytes and the
    #: path are the caller's to supply -- this function is handed rows, not a
    #: file -- but the extent is a fact about what was actually scored, and a
    #: digest without it identifies a file rather than a run.
    panel_rows: Optional[int] = None
    panel_first_date: Optional[date] = None
    panel_last_date: Optional[date] = None
    #: The scored origins, earliest first, one per entry of `forecasts`.
    folds: Tuple[ScoredFold, ...] = ()
    #: The quantile grid the fitted models reported, and the mean pinball loss
    #: at each level of it, positionally aligned. Two parallel tuples rather
    #: than a mapping because the alignment is the thing a reader must be able
    #: to check, and a mapping built at this depth would hide a mislabelling
    #: one call earlier than the place it can still be caught.
    #:
    #: `crps_bps` is the mean of `metrics.crps_from_quantiles` over the scored
    #: days. It is a function of the same pinball losses -- twice their mean --
    #: and is reported anyway because it is the number the contract's Metrics
    #: section names, and computing it by calling the metric rather than by
    #: doubling an average here is what keeps that identity checkable rather
    #: than assumed.
    quantile_levels: Tuple[float, ...] = ()
    pinball_loss: Tuple[float, ...] = ()
    crps_bps: Optional[float] = None


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


class FittedThreshold:
    """A two-regime ARX, fitted: one coefficient vector per regime, one law.

    The fourth benchmark `PLAN.md` Phase 2 names, and the first model here in
    which a covariate does something other than contribute a term. The point
    forecast for the day after a feature row is

        b0[r] + b1[r] * spread_bps(row) + sum_j c_j[r] * x_j(row)

    where `r` is `"low"` if the threshold variable on that row is at or below
    the fitted threshold and `"high"` if it is above. Both regimes are fitted by
    least squares on the training frame's own one-step-ahead pairs, restricted
    to the origin rows that fall in that regime.

    **The threshold variable is read, so it is reported.** `features_read`
    carries it alongside the autoregressive term and the regressors, and there
    is no exemption for "it only picks the regime". The purge is sized over the
    sources of the declared feature set before anything is fitted, and
    `rolling_persistence_backtest` checks the first fitted model against that
    declaration; a threshold model that consulted `on_rrp` to choose a regime
    and did not report `on_rrp` would have had its gap computed over the wrong
    sources -- correctly, and in the flattering direction, which is the shape
    this repository keeps finding one level at a time.

    **One residual law, pooled across regimes.** `FittedForecastModel.residuals`
    is the single sample "both outputs read", and `predict` and `predict_stress`
    are two views of it; a per-regime law would make `residuals` a claim
    `predict` does not honour and would break the agreement between the quantiles
    and the exceedance that the contract's Target requires. So the regimes
    differ in the conditional mean and share the dispersion around it. That is a
    real limitation -- a stressed regime plausibly has wider residuals than a
    calm one, and this model cannot say so -- and it is stated here rather than
    discovered from the intervals. Widening the interface to a per-regime law is
    a contract question, not a refactor.

    Fitted state, all of it set in `fit_threshold` and nowhere else:

    * `threshold_variable` -- the panel column the regime is read off.
    * `threshold` -- the value separating the regimes.
    * `threshold_estimated` -- whether that value was searched for on the
      training frame (`True`) or handed over by the caller (`False`). Carried
      because "fitted on the training rows" and "declared by the caller" are
      different provenances for the same number and a reader of a report cannot
      otherwise tell which one produced it.
    * `regressors` -- the ordered exogenous names, as `FittedArx` carries them.
    * `imputations` -- the training-window mean of each regressor's observed
      values, over the origin rows of the **whole** window rather than per
      regime. Per-regime means would be a second fitted transform whose own
      inputs depend on the threshold, and the regime with fewer rows would get
      the noisier imputation exactly where it can least afford one.
    * `coefficients` -- `{"low": (...), "high": (...)}`, each ordered to match
      `design_names`.
    * `regime_rows` -- how many design rows each regime was fitted on. Reported
      so "two regimes" is checkable rather than asserted.
    * `_residuals` -- the sorted pooled leave-one-out residual vector.
    * `cutoff` -- the last date the training frame was allowed to contain, with
      the same meaning and the same `trained_beyond` question as the others.

    A feature row missing a declared regressor raises `MissingRegressorError`; a
    feature row carrying one as `None` gets the fitted mean. A feature row
    missing the threshold variable raises `MissingRegressorError` too, and one
    carrying it as `None` raises `UnobservedThresholdError` rather than being
    imputed -- see that class for why the two cases part company here.
    """

    __slots__ = (
        "_residuals",
        "coefficients",
        "cutoff",
        "imputations",
        "levels",
        "regime_rows",
        "regressors",
        "threshold",
        "threshold_estimated",
        "threshold_variable",
    )

    def __init__(
        self,
        coefficients: Mapping[str, Sequence[float]],
        regressors: Sequence[str],
        threshold_variable: str,
        threshold: float,
        threshold_estimated: bool,
        imputations: Mapping[str, float],
        residuals: Sequence[float],
        regime_rows: Mapping[str, int],
        cutoff: date,
        levels: Sequence[float] = QUANTILE_LEVELS,
    ) -> None:
        self.regressors: Tuple[str, ...] = tuple(regressors)
        self.threshold_variable: str = str(threshold_variable)
        self.threshold: float = float(threshold)
        self.threshold_estimated: bool = bool(threshold_estimated)
        self.coefficients: Mapping[str, Tuple[float, ...]] = MappingProxyType(
            {
                regime: tuple(float(c) for c in coefficients[regime])
                for regime in REGIMES
            }
        )
        #: Read-only for the reason `FittedArx.imputations` is: a fitted
        #: transform retuned after the fact puts the reported coefficients and
        #: the imputation that produced them out of step with no diff to show.
        self.imputations: Mapping[str, float] = MappingProxyType(
            {name: float(imputations[name]) for name in self.regressors}
        )
        self.regime_rows: Mapping[str, int] = MappingProxyType(
            {regime: int(regime_rows[regime]) for regime in REGIMES}
        )
        self._residuals: Tuple[float, ...] = tuple(sorted(float(r) for r in residuals))
        self.cutoff: date = cutoff
        self.levels: Tuple[float, ...] = _validate_levels(levels)

    def __repr__(self) -> str:  # pragma: no cover - diagnostic only
        return (
            f"FittedThreshold(cutoff={self.cutoff.isoformat()}, "
            f"threshold={self.threshold_variable}<={self.threshold!r}, "
            f"regime_rows={dict(self.regime_rows)}, "
            f"residuals={len(self._residuals)})"
        )

    @property
    def design_names(self) -> Tuple[str, ...]:
        """The coefficient order, named. `coefficients[r][i]` multiplies `[i]`.

        The same order in both regimes, so the two vectors are comparable term
        by term. A regime with its own design would be two models sharing a
        name.
        """

        return ("intercept", "spread_bps") + self.regressors

    @property
    def residuals(self) -> Tuple[float, ...]:
        """The pooled leave-one-out residual sample, ascending."""

        return self._residuals

    @property
    def features_read(self) -> Tuple[str, ...]:
        """`spread_bps`, the declared regressors, and the threshold variable.

        Derived from `design_names` exactly as `FittedArx.features_read` is,
        with the threshold variable appended when the design does not already
        carry it -- a column may legitimately be both a regressor and the
        regime selector, and reporting it twice would be a claim about
        multiplicity that `_check_fitter_stayed_inside` does not read and a
        reader would.

        The threshold variable is in this tuple because the model reads it off
        the feature row. That it is read to choose a model rather than to
        compute a term makes no difference to the purge: the value still has to
        have been published by the time the forecast was made, and its source's
        release lag still has to be in the gap. This is the one line in the
        class that the whole block is about.

        The intercept is dropped for the reason `FittedArx` drops it: it is the
        constant 1.0 and not read off the row at all.
        """

        read = tuple(name for name in self.design_names if name != "intercept")
        if self.threshold_variable in read:
            return read
        return read + (self.threshold_variable,)

    def trained_beyond(self, feature_row: DailyObservation) -> bool:
        """Was this model fitted on rows dated after `feature_row`?

        Same question, same answer, same reason as the other two.
        """

        return feature_row.date < self.cutoff

    def regime_for(self, feature_row: DailyObservation) -> str:
        """`"low"` or `"high"`: which model this row selects, and why.

        Public because it is half of the auditable account of a threshold
        forecast -- `design_row` says which numbers went in, this says which
        coefficient vector they were multiplied by, and a forecast is not
        reproducible from the first alone.

        The comparison is `<=` for `"low"` and `>` for `"high"`, matching the
        split the fit used, so a row sitting exactly on the threshold is scored
        by the regime it was fitted into rather than by the other one.

        Raises:
            MissingRegressorError: if the row does not carry the column.
            UnobservedThresholdError: if it carries it as `None`.
        """

        observed = _raw_regressor(feature_row, self.threshold_variable, "feature row")
        if observed is None:
            raise UnobservedThresholdError(
                f"feature row for {feature_row.date} carries "
                f"{self.threshold_variable!r} as None; the regime is a choice "
                f"between two fitted models and an imputed mean would make it "
                f"silently, putting every unobserved row in whichever regime the "
                f"training mean falls in. A regressor is imputed because it "
                f"enters a sum; a threshold variable selects the sum"
            )
        return "low" if observed <= self.threshold else "high"

    def design_row(self, feature_row: DailyObservation) -> Tuple[float, ...]:
        """The feature row as this model reads it, in `design_names` order.

        Identical to `FittedArx.design_row`, and deliberately so: the regimes
        differ in their coefficients, not in what they read. Raises
        `MissingRegressorError` if the row does not carry a declared regressor.
        """

        values = [1.0, feature_row.spread_bps]
        for name in self.regressors:
            observed = _raw_regressor(feature_row, name, "feature row")
            values.append(self.imputations[name] if observed is None else observed)
        return tuple(values)

    def point_forecast(self, feature_row: DailyObservation) -> float:
        """The conditional mean of the regime this row falls in."""

        return _dot(self.coefficients[self.regime_for(feature_row)], self.design_row(feature_row))

    def predict(self, feature_row: DailyObservation) -> Tuple[float, ...]:
        """One predicted spread quantile per declared level, in declared order.

        The regime's point forecast shifted by the pooled residual quantile at
        each level. Ascending, because `levels` is ascending and `_quantile` is
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

        The third model to reach this derivation unchanged, over its own
        residual vector. `_exceedance_from_residuals` inverts `_quantile`, so
        `predict_stress` evaluated at `predict`'s `Q(q)` returns `1 - q` here
        for the same reason it does for the other two -- and that a regime
        model needed no new code for it is further evidence the derivation
        belongs to the interface rather than to any implementation.

        Not a classifier fitted on the `stress_gt_*` label columns. Nothing in
        this object was fitted to a label, the threshold included: the grid
        search below minimises squared error on the spread, never a label.
        """

        family = _validate_taus_bp(
            load_stress_thresholds()["taus_bp"] if taus is None else taus
        )
        anchor = self.point_forecast(feature_row)
        return tuple(
            _exceedance_from_residuals(self._residuals, tau - anchor) for tau in family
        )


def _threshold_value(row: DailyObservation, name: str, where: str) -> float:
    """The threshold variable on `row`, refusing an unobserved one.

    `_raw_regressor` for the absent-key and non-finite halves, so those two
    paths raise exactly what every other read of a panel column raises, and
    then a refusal rather than an imputation for `None`. See
    `UnobservedThresholdError` for why this is the one column that is not
    imputed.
    """

    observed = _raw_regressor(row, name, where)
    if observed is None:
        raise UnobservedThresholdError(
            f"{where} for {row.date} carries {name!r} as None; a regime is a "
            f"choice between two fitted models and cannot be made from an "
            f"unobserved value. Fit on a window that observes the threshold "
            f"variable, or declare one this window observes"
        )
    return observed


def _regime_split(
    design: Sequence[Sequence[float]],
    targets: Sequence[float],
    selectors: Sequence[float],
    threshold: float,
) -> Mapping[str, Tuple[List[Sequence[float]], List[float]]]:
    """The design rows and targets of each regime at `threshold`, in row order.

    `"low"` is `selector <= threshold`, `"high"` is `selector > threshold`. The
    boundary is closed on the low side, and `FittedThreshold.regime_for` makes
    the same comparison, so a row sitting exactly on the threshold is scored by
    the regime it was fitted into rather than by the other one.
    """

    parts: Mapping[str, Tuple[List[Sequence[float]], List[float]]] = {
        regime: ([], []) for regime in REGIMES
    }
    for row, target, selector in zip(design, targets, selectors):
        regime = "low" if selector <= threshold else "high"
        parts[regime][0].append(row)
        parts[regime][1].append(target)
    return parts


def _fit_regimes(
    design: Sequence[Sequence[float]],
    targets: Sequence[float],
    selectors: Sequence[float],
    threshold: float,
    minimum_rows: int,
) -> Tuple[Mapping[str, Tuple[float, ...]], Mapping[str, int], float]:
    """Both regimes at `threshold`: coefficients, row counts, in-sample SSE.

    The one place a threshold becomes a pair of fitted regimes. The grid search
    calls it once per candidate and `fit_threshold` calls it once more on the
    value it chose, so the fit the search scored and the fit the model carries
    are the same computation rather than two that agree today.

    Raises:
        DegenerateRegimeError: if either regime holds fewer than
            `minimum_rows` design rows.
        SingularDesignError: if either regime's design does not identify its
            coefficients on its own rows.
    """

    parts = _regime_split(design, targets, selectors, threshold)
    counts = {regime: len(parts[regime][1]) for regime in REGIMES}
    thin = sorted(regime for regime in REGIMES if counts[regime] < minimum_rows)
    if thin:
        raise DegenerateRegimeError(
            f"threshold {threshold!r} on the declared variable splits the window "
            f"into low={counts['low']} and high={counts['high']} design rows, and "
            f"regime(s) {thin} hold fewer than the {minimum_rows} a regime needs. "
            f"A threshold model that fell back to a single regime here would "
            f"still report itself as a threshold model, and its numbers would be "
            f"attributed to a regime structure that was never estimated"
        )

    coefficients = {}
    total = 0.0
    for regime in REGIMES:
        regime_design, regime_targets = parts[regime]
        fitted = _least_squares(regime_design, regime_targets)
        coefficients[regime] = fitted
        total += sum(
            (target - _dot(fitted, row)) ** 2
            for row, target in zip(regime_design, regime_targets)
        )
    return coefficients, counts, total


def _choose_threshold(
    design: Sequence[Sequence[float]],
    targets: Sequence[float],
    selectors: Sequence[float],
    minimum_rows: int,
) -> float:
    """The candidate threshold minimising in-sample squared error, or a refusal.

    **The candidates are the training frame's own observed values** of the
    threshold variable, at the origin rows the design was built from -- the
    largest excluded, since nothing is above it and the high regime would be
    empty. Nothing outside the frame the caller handed over is consulted, which
    is the whole discipline of this function: a threshold chosen by looking at
    the series the model will later be scored on is the leak this repository
    exists to detect, wearing the hat of a hyperparameter.

    **Why a grid search over observed values.** The sum of squares as a function
    of the threshold is a step function -- it changes only when a row crosses
    from one regime to the other -- so it has no derivative to follow and the
    observed values are not a sample of the candidates but *all* of them. Every
    distinct split of these rows is reachable from some value in this list, and
    the search is therefore exhaustive rather than approximate. That is the
    standard construction for a threshold regression (Hansen's conditional
    least squares), and the alternatives are worse here: a fixed grid of round
    numbers would miss splits the data actually admits and would import a scale
    nobody declared, and an optimiser would spend iterations on a function whose
    every level set is already enumerated.

    **Ties break to the smallest candidate.** Two thresholds producing exactly
    the same partition produce exactly the same error, and the run has to be
    reproducible; the smallest is chosen because `min` over an ascending list
    with a strict comparison is the rule a reader can check.

    **A candidate that cannot be fitted is not a candidate.** Degenerate splits
    and rank-deficient regimes are skipped during the search. That is not the
    fallback item 4 of this block's brief prohibits: the result is still two
    fitted regimes, and if *no* candidate admits two the search raises rather
    than returning one.

    Raises:
        DegenerateRegimeError: if no candidate value splits the window into two
            fittable regimes. The window has no second regime in it at this
            variable, and saying so is the only honest answer.
    """

    candidates = sorted({float(value) for value in selectors})[:-1]
    best_threshold = None
    best_error = math.inf
    for candidate in candidates:
        try:
            _, _, error = _fit_regimes(
                design, targets, selectors, candidate, minimum_rows
            )
        except (DegenerateRegimeError, SingularDesignError):
            continue
        if error < best_error:
            best_error = error
            best_threshold = candidate
    if best_threshold is None:
        raise DegenerateRegimeError(
            f"no value among the {len(candidates)} candidate thresholds this "
            f"window offers splits it into two regimes of at least "
            f"{minimum_rows} fittable design rows each. There is no two-regime "
            f"model to estimate here: fit on more history, declare a different "
            f"threshold variable, or use the ARX, which is what a single regime "
            f"is"
        )
    return best_threshold


def fit_threshold(
    train_frame: Sequence[DailyObservation],
    regressors: Sequence[str],
    threshold_variable: str,
    threshold: Optional[float] = None,
    cutoff: Optional[date] = None,
    minimum_history: int = 20,
    levels: Sequence[float] = QUANTILE_LEVELS,
) -> FittedThreshold:
    """Fit the two-regime ARX on `train_frame` and return the fitted model.

    The design is the frame's own one-step-ahead pairs, exactly as `fit_arx`
    builds them, and then split in two: origin row `i` goes to the regime its
    `threshold_variable` value selects, and each regime gets its own least
    squares over its own rows.

    **Everything is fitted on `train_frame` and nothing else** -- the
    imputations, the threshold, the regime assignment and the residual law. The
    threshold in particular: `_choose_threshold` searches the candidate values
    these origin rows carry, and is handed nothing wider. A caller that wants a
    threshold from elsewhere passes it explicitly, and the fitted model records
    that it was declared rather than estimated.

    **The residual law is leave-one-out within regime, pooled.** For each
    regime, `_leave_one_out_residuals` refits on that regime's other rows and
    scores the held-out one, so no residual was minimised by the coefficients
    that produced it -- the same reason `fit_arx` gives, and the more pressing
    here because two regimes over one window means twice the coefficients and
    twice the in-sample narrowing.

    The threshold is **held fixed across the leave-one-out folds**; only the
    regime coefficients are refit. That is the same treatment `fit_arx` gives
    its imputation means, which are also fitted on the whole window and held
    while the coefficients move, and it is a stated approximation rather than a
    silent one: a residual scored under a threshold that saw its own row is
    optimistic by however much that one row moved the search. Re-estimating the
    threshold inside every fold is the exact construction, and it costs a full
    grid search per row per origin -- on a rolling backtest that is the square
    of the panel length in solves, which is why it is not the default. If a
    reported interval ever turns on this, the exact version is the drop-in and
    the difference is the thing to report.

    Args:
        train_frame: the training rows, strictly ascending by date.
        regressors: the ordered exogenous regressor names. **Required, with no
            default**, for the reason `fit_arx` refuses one.
        threshold_variable: the panel column the regime is read off. Required
            and undefaulted for the same reason and more sharply: this column
            does not merely contribute a term, it chooses the model, and a
            default would be a silent claim about which column a regime is
            allowed to be a function of. It may also appear in `regressors` --
            a variable can both shift the level and switch the relationship --
            and `features_read` reports it once either way.
        threshold: the value separating the regimes. `None`, the default,
            estimates it from `train_frame` by `_choose_threshold`. A number is
            honoured as declared and recorded as declared; it is not checked
            against the frame's own optimum, because a caller who declares a
            threshold is stating a prior and not asking for one.
        cutoff: the last date the model was allowed to see. Defaults to the
            frame's own last date.
        minimum_history: the shortest frame that may produce a fitted law.
        levels: the quantile grid, defaulting to the declared one.

    Returns:
        A `FittedThreshold` carrying both coefficient vectors, its threshold and
        how that threshold was arrived at, its regime row counts, its fitted
        imputation means, its pooled leave-one-out residuals and its cutoff.

    Raises:
        LookAheadError: if any training row is dated after `cutoff`.
        SplitError: if the frame is not strictly ascending by date.
        MissingRegressorError: if a training row does not carry a declared
            regressor or the threshold variable.
        UnobservedThresholdError: if a training origin row carries the threshold
            variable as `None`. Not imputed; see the class.
        DegenerateRegimeError: if the declared threshold, or every candidate
            when one is estimated, leaves a regime too thin to fit. A refusal,
            never a fallback to a single regime.
        SingularDesignError: if a regime's declared regressors do not identify
            separate coefficients on that regime's rows. A real property of the
            split -- a column can move over a window and be constant inside one
            regime of it -- and refusing names the regime.
        ValueError: for the shapes `fit_arx` refuses -- no regressors, a
            duplicate, too short a frame, a regressor unobserved throughout --
            and if `threshold` is declared non-finite.
    """

    names = tuple(str(name) for name in regressors)
    if not names:
        raise ValueError(
            "no regressors declared; a two-regime model with no exogenous term "
            "is a threshold AR, and an empty list is how a caller omits the "
            "decision rather than makes it. Name the regressors"
        )
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise ValueError(
            f"regressors declared more than once: {duplicates}; a duplicated "
            f"column makes a regime's design rank deficient and its two "
            f"coefficients meaningless individually"
        )
    selector_name = str(threshold_variable)
    if not selector_name:
        raise ValueError(
            "no threshold variable declared; a regime read off nothing is not a "
            "regime, and this model's whole claim is that a covariate chooses "
            "the relationship"
        )
    if threshold is not None:
        threshold = float(threshold)
        if not math.isfinite(threshold):
            raise ValueError(
                f"declared threshold is not finite: {threshold!r}; every row "
                f"would fall on one side of it and the split would be degenerate "
                f"by construction"
            )

    rows = list(train_frame)
    if len(rows) < minimum_history:
        raise ValueError(
            f"threshold arx needs at least {minimum_history} training rows, got "
            f"{len(rows)}; two coefficient vectors and a residual law from fewer "
            f"is not a fitted model"
        )

    dates = [row.date for row in rows]
    ensure_strictly_ascending(dates, label="training frame dates")

    declared_cutoff = dates[-1] if cutoff is None else cutoff
    if dates[-1] > declared_cutoff:
        raise LookAheadError(
            f"training frame reaches {dates[-1]}, past its cutoff "
            f"{declared_cutoff}; a fitted model may not contain a row it was not "
            f"allowed to see"
        )

    # The origins: every row with a successor in the frame. The imputations, the
    # threshold and the regime assignment are all fitted on these and nothing
    # else, which is what contract test 3 means by "recomputed on a training
    # window alone" -- and here it covers a parameter that selects a model
    # rather than merely scaling a column.
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
                f"window ({origins[0].date}..{origins[-1].date}); there is "
                f"nothing to fit an imputation from, and filling it with 0.0 "
                f"would be the coercion contract test 5 prohibits"
            )
        imputations[name] = sum(seen) / len(seen)

    design: List[Sequence[float]] = []
    targets: List[float] = []
    selectors: List[float] = []
    for index in range(1, len(rows)):
        origin = rows[index - 1]
        row = [1.0, origin.spread_bps]
        for name in names:
            value = _raw_regressor(origin, name, "training row")
            row.append(imputations[name] if value is None else value)
        design.append(tuple(row))
        targets.append(rows[index].spread_bps)
        selectors.append(_threshold_value(origin, selector_name, "training row"))

    # The minimum per regime, derived rather than chosen. `fit_arx` demands
    # `columns + 2` design rows of a whole window so that a leave-one-out fold
    # keeps a degree of freedom; a regime is fitted by the same least squares
    # and scored by the same leave-one-out law, so it needs the same count of
    # its own rows. At `columns + 1` a held-out fold has exactly as many rows as
    # coefficients and interpolates them, which would fill the pooled law with a
    # block of zeros and narrow every reported interval.
    columns = len(names) + 2
    minimum_rows = columns + 2
    if len(design) < 2 * minimum_rows:
        raise ValueError(
            f"{len(design)} design rows against {columns} coefficients in each of "
            f"two regimes; a two-regime leave-one-out fit needs at least "
            f"{2 * minimum_rows}. Declare fewer regressors or fit on more history"
        )

    estimated = threshold is None
    chosen = (
        _choose_threshold(design, targets, selectors, minimum_rows)
        if estimated
        else threshold
    )
    coefficients, counts, _ = _fit_regimes(
        design, targets, selectors, chosen, minimum_rows
    )

    parts = _regime_split(design, targets, selectors, chosen)
    residuals: List[float] = []
    for regime in REGIMES:
        regime_design, regime_targets = parts[regime]
        try:
            residuals.extend(
                _leave_one_out_residuals(regime_design, regime_targets)
            )
        except SingularDesignError as error:
            raise SingularDesignError(
                f"the {regime!r} regime's design is rank deficient with one of "
                f"its {len(regime_targets)} rows held out, though it is "
                f"identified on all of them; one row is carrying a coefficient "
                f"inside that regime. Declare fewer regressors or fit on more "
                f"history"
            ) from error

    return FittedThreshold(
        coefficients,
        names,
        selector_name,
        chosen,
        estimated,
        imputations,
        residuals,
        counts,
        declared_cutoff,
        levels,
    )


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
    features_read: Sequence[str],
    features: Tuple[str, ...],
    sources: Tuple[str, ...],
    purge: int,
) -> None:
    """Raise unless the fitted model read only what the caller declared.

    The purge was sized from `features`, before this model existed. If the
    fitter read a column outside that set, the gap protecting the reported
    numbers was computed over the wrong sources -- and the error is in the
    flattering direction, because the undeclared column is the one whose release
    lag was never taken into the maximum.

    `LookAheadError`, not `ValueError`: this is a leakage condition, and it is
    the same condition `_feature_index` raises for one level down. Not an
    `assert`, because `python -O` strips asserts and this guard has to survive
    the way the numbers are actually produced.

    Set containment, not order or multiplicity: a model may read fewer columns
    than were declared. Declaring more than the fitter uses purges more than the
    evidence requires, which costs training rows and is visible in the report --
    conservative and legible, so it is not refused here.

    Takes the tuple rather than the fitted model, so that **both** evaluation
    paths reach this one guard. `rolling_persistence_backtest` passes
    `fitted.features_read`; `event_eval.evaluate_event_window` passes
    `ExceedanceCurves.features_read`, which is the same claim made by a
    predictor whose fitted model the evaluator never holds. A second copy of
    this comparison in the evaluator would be a second implementation of the
    rule that sizes the gap, and two implementations of that agree until they
    do not.
    """

    exceeded = tuple(
        name for name in features_read if name not in frozenset(features)
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
    folds: List[ScoredFold] = []
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
            _check_fitter_stayed_inside(
                fitted.features_read, declared, sources, purge
            )
        model = fitted
        feature_row = rows[_feature_index(dates, train_indices, index, purge)]
        quantiles = model.predict(feature_row)
        folds.append(
            ScoredFold(
                train_start=rows[train_indices[0]].date,
                train_end=rows[train_indices[-1]].date,
                train_rows=len(train_indices),
                feature_date=feature_row.date,
                scored_date=rows[index].date,
            )
        )
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
                quantiles_bps=tuple(quantiles),
            )
        )

    mae = sum(abs(item.actual_bps - item.predicted_bps) for item in forecasts) / len(forecasts)
    coverage = sum(
        item.lower_bps <= item.actual_bps <= item.upper_bps for item in forecasts
    ) / len(forecasts)

    # The grid the losses are labelled with is read off the model that produced
    # the vectors, not restated from the contract -- a label taken from
    # anywhere but the thing it labels can be wrong while looking right, which
    # is the whole subject of this function. The equality is then *checked*
    # against the declaration, because the point of a fixed grid is that a
    # pinball loss from one model is comparable to a pinball loss from another,
    # and a model quantiling at levels of its own would publish a number under
    # a heading it does not belong to.
    levels = tuple(model.levels)
    if levels != tuple(QUANTILE_LEVELS):
        raise ValueError(
            f"the fitted model reports quantile levels {levels}, but the "
            f"contract fixes them at {tuple(QUANTILE_LEVELS)}; losses at a "
            "private grid are not comparable across models and would be "
            "published under headings they do not belong to"
        )
    losses = tuple(
        sum(
            pinball_loss(level, item.quantiles_bps[position], item.actual_bps)
            for item in forecasts
        )
        / len(forecasts)
        for position, level in enumerate(levels)
    )
    crps = sum(
        crps_from_quantiles(levels, item.quantiles_bps, item.actual_bps)
        for item in forecasts
    ) / len(forecasts)

    return BacktestReport(
        forecasts,
        mae,
        coverage,
        model,
        declared,
        sources,
        purge,
        decision_time=decision_time,
        minimum_history=minimum_history,
        panel_rows=len(rows),
        panel_first_date=rows[0].date,
        panel_last_date=rows[-1].date,
        folds=tuple(folds),
        quantile_levels=levels,
        pinball_loss=losses,
        crps_bps=crps,
    )


# --------------------------------------------------------------------------
# Publication: the backtest as a machine-readable artifact
# --------------------------------------------------------------------------

#: Coverage of the sampling interval reported beside the headline MAE.
#:
#: **Not read from `QUANTILE_LEVELS`,** although the span of the declared grid
#: happens to be this same 0.90. The two numbers mean different things: the
#: declared grid spans a *predictive* interval, a claim about where tomorrow's
#: spread falls, while this is a *sampling* interval, a claim about how far the
#: MAE would move if the same procedure were run on another draw of the same
#: process. Deriving one from the other would tie two unrelated quantities
#: together, and the day somebody widened the predictive grid to 0.99 the
#: bootstrap would silently follow it.
BOOTSTRAP_LEVEL = 0.90

#: Replications behind the interval. Enough that the 5th and 95th percentiles
#: of the resample distribution are not themselves noisy at the fold counts
#: this backtest produces, and cheap enough at those counts that the report is
#: not something a reader waits for. Recorded in the artifact rather than left
#: implicit: an interval whose replication count is unknown cannot be compared
#: to another one.
BOOTSTRAP_REPLICATIONS = 2000


def _maximum_horizon_overlap(folds: Sequence[ScoredFold]) -> int:
    """How many scored days share a forecast horizon at the busiest point.

    Each fold's forecast reaches from the day after its feature row to the day
    it scores. Two folds whose horizons overlap share innovations, so their
    errors are dependent, and the bootstrap has to resample them in blocks long
    enough to carry that dependence -- the standard result that overlapping
    h-step forecast errors are MA(h-1).

    **Measured off the folds, not computed from the purge.** The gap is in
    calendar days and the panel is in rows; a weekend inside a six-day gap
    means the horizon spans seven calendar days but only five panel rows, and
    a block length of `purge + 1` would be a number from the wrong vocabulary
    that looks about right. Sweeping the fold horizons answers the question
    that was actually being asked, in the units the resample runs in, and it
    answers it from this run rather than from a rule of thumb.

    Returns at least 1: a block length below 1 is undefined, and 1 is the iid
    bootstrap, which is the correct resample when no two horizons overlap --
    the unpurged case, where each error is one step over disjoint days.
    """

    if not folds:
        return 1
    events: List[Tuple[date, int]] = []
    for fold in folds:
        # Covered days are (feature_date, scored_date]: the horizon opens the
        # day after the last row the forecaster could see and closes on the day
        # it is scored on.
        events.append((fold.feature_date + timedelta(days=1), 1))
        events.append((fold.scored_date + timedelta(days=1), -1))
    # `-1` sorts before `+1` at a shared date, which is what closes a horizon
    # on the first day it no longer covers before opening one that starts there.
    events.sort()
    live = 0
    busiest = 0
    for _, delta in events:
        live += delta
        busiest = max(busiest, live)
    return max(1, busiest)


def _report_seed(report: BacktestReport, panel_sha256: str) -> int:
    """A reproducible bootstrap seed, derived from what the run was.

    `stationary_bootstrap_interval` requires a seed and says why: an interval
    that cannot be reproduced cannot be checked. A literal here would satisfy
    the signature and violate this block's one rule -- nothing in the report is
    typed -- and it would also be the wrong shape, because a single constant
    makes every run in the project draw the same resample sequence regardless
    of what it scored.

    So the seed is a digest of the run's own identity: the panel bytes, the
    declared feature set, the derived gap, and the decision time. The same run
    on the same panel reproduces the same interval exactly, a reader can
    recompute the seed from fields the artifact already carries, and two runs
    that differ in any of those respects are not silently sharing a stream.
    """

    material = "\x00".join(
        (
            panel_sha256,
            ",".join(sorted(report.features)),
            str(report.purge_days),
            "" if report.decision_time is None else report.decision_time.isoformat(),
        )
    )
    return int.from_bytes(
        hashlib.sha256(material.encode("utf-8")).digest()[:8], "big", signed=False
    ) & 0x7FFFFFFF


def mae_bootstrap_interval(
    report: BacktestReport, *, seed: int, block_length: Optional[int] = None
) -> Tuple[float, float, int]:
    """The stationary-bootstrap interval around `report.mae_bps`.

    A single MAE from a handful of folds invites a reader to believe that a
    difference between two models is real. It may not be: at fourteen origins
    the sampling error on the mean absolute error is the same order as the
    differences a benchmark is used to argue about. Reporting the interval
    beside the point estimate is the smallest honest fix, and this project
    already decided which interval: every one comes through
    `metrics.stationary_bootstrap_interval`.

    The forecasts are resampled by index, which is what keeps each scored day's
    prediction with its own outcome -- resampling the two apart would destroy
    the pairing the error is computed from and produce a narrower interval
    around a statistic nobody computed.

    Args:
        report: a report from `rolling_persistence_backtest`.
        seed: required, as the metric requires it. See `_report_seed`.
        block_length: mean block length. `None`, the default, measures it off
            the report's own folds via `_maximum_horizon_overlap`.

    Returns:
        `(lower, upper, block_length)` -- the block length included because an
        interval whose resample structure is unstated cannot be reproduced from
        the artifact, and this one is derived rather than declared.
    """

    forecasts = list(report.forecasts)
    if not forecasts:
        raise ValueError("a report with no forecasts has no interval")
    block = (
        _maximum_horizon_overlap(report.folds)
        if block_length is None
        else int(block_length)
    )
    errors = [abs(item.actual_bps - item.predicted_bps) for item in forecasts]

    def mae(indices: Sequence[int]) -> float:
        return sum(errors[i] for i in indices) / len(indices)

    lower, upper = stationary_bootstrap_interval(
        mae,
        len(errors),
        block_length=block,
        seed=seed,
        replications=BOOTSTRAP_REPLICATIONS,
        level=BOOTSTRAP_LEVEL,
    )
    return lower, upper, block


def backtest_document(report: BacktestReport, *, panel_path: Path) -> dict:
    """The report as a publishable record: every number, and what produced it.

    `PLAN.md` Milestone A ends with a published pinball loss and interval
    coverage, and its exit criterion says the published figures are generated
    output rather than prose. A number typed into a document is right when it
    is typed and silently wrong afterwards -- which is the failure
    `tests/test_docs_freshness.py` forbids one level down, on counts and dates,
    with nothing to point at instead. This is the instead.

    **Every value here is computed in the run that emits it.** Nothing is
    defaulted: a field this cannot compute is absent from the document rather
    than present with a stand-in, because an absent field makes a reader ask
    and a defaulted one makes them believe. `decision_time`, `minimum_history`
    and the panel extent are `Optional` on `BacktestReport` for that reason,
    and each is omitted here when it is `None`.

    **Why these fields.** A figure without the conditions it was computed under
    is not a result, and for this benchmark the conditions are exactly four
    things: what was declared, what that derived, what was scored, and what
    came out.

    * `declaration` -- the feature set, the decision time, the minimum history.
      The one thing the caller chose, plus the two settings that shape what
      follows from it. Everything else in the run is a consequence of these.
    * `derived` -- the sources the features resolved to and the gap those
      sources produced. Never supplied and never re-derived here: read off the
      report, because a document that recomputed them would be a second
      derivation of the number that shaped the run, and the two can agree today
      and drift later.
    * `panel` -- path, `sha256`, row count, first and last date. The path says
      which file was named and the digest says which bytes answered to that
      name; a report carrying only the path is a claim about a file that may
      since have changed, which is the same decay as a typed number. The extent
      says what was actually scored, since a digest identifies a file and not a
      run.
    * `folds` -- the count, and the first and last origin in full. Enough for a
      reader to check the gap against a calendar on the two folds where an
      off-by-one would show, without the artifact growing with the panel.
    * `metrics` -- the numbers, unrounded. Rounding belongs to whoever displays
      them; an artifact that rounded would publish a figure nobody computed and
      would make two runs that genuinely differ look identical.

    What is deliberately *not* here: any aggregate over event windows (those
    are the event path's and the contract forbids aggregating a single window),
    and any per-forecast dump. The second is a real omission and worth the
    note: the pinball losses cannot be recomputed from this file alone. They
    can be recomputed from the panel, which the file identifies by digest,
    which is what makes the digest load-bearing rather than decorative.

    Args:
        report: a report from `rolling_persistence_backtest`.
        panel_path: the panel file as the caller named it. Read here, once, for
            its bytes -- the digest and the path come from the same read, so
            the artifact cannot name one file and hash another.

    Returns:
        A JSON-serialisable dict. The caller writes it; this shapes it.
    """

    digest = hashlib.sha256(panel_path.read_bytes()).hexdigest()
    seed = _report_seed(report, digest)
    lower, upper, block = mae_bootstrap_interval(report, seed=seed)

    declaration: dict = {"features": sorted(report.features)}
    if report.decision_time is not None:
        declaration["decision_time"] = report.decision_time.isoformat(
            timespec="minutes"
        )
    if report.minimum_history is not None:
        declaration["minimum_history"] = report.minimum_history

    panel: dict = {"path": str(panel_path), "sha256": digest}
    if report.panel_rows is not None:
        panel["row_count"] = report.panel_rows
    if report.panel_first_date is not None:
        panel["first_date"] = report.panel_first_date.isoformat()
    if report.panel_last_date is not None:
        panel["last_date"] = report.panel_last_date.isoformat()

    folds: dict = {"count": len(report.folds)}
    if report.folds:
        folds["first"] = _fold_document(report.folds[0])
        folds["last"] = _fold_document(report.folds[-1])

    metrics: dict = {
        "forecast_count": len(report.forecasts),
        "mae_bps": report.mae_bps,
        "mae_bps_interval": {
            "lower": lower,
            "upper": upper,
            "level": BOOTSTRAP_LEVEL,
            "method": "stationary_bootstrap",
            # The block length is measured off this run's own fold horizons --
            # see `_maximum_horizon_overlap` -- so a wider gap widens the
            # blocks, which is the dependence the gap creates being carried by
            # the resample that reports it.
            "block_length": block,
            "replications": BOOTSTRAP_REPLICATIONS,
            "seed": seed,
        },
        "interval_coverage": report.interval_coverage,
        "interval_probability": INTERVAL_PROBABILITY,
    }
    if report.quantile_levels:
        # Keyed by the level, from the levels the losses were computed at. The
        # two tuples are aligned by construction in the backtest and zipped
        # once, here, so there is exactly one place a loss could acquire the
        # wrong heading.
        metrics["pinball_loss"] = {
            _level_key(level): loss
            for level, loss in zip(report.quantile_levels, report.pinball_loss)
        }
    if report.crps_bps is not None:
        metrics["crps_bps"] = report.crps_bps

    return {
        "declaration": declaration,
        "derived": {
            "sources": sorted(report.sources),
            "purge_days": report.purge_days,
        },
        "panel": panel,
        "folds": folds,
        "metrics": metrics,
    }


def _fold_document(fold: ScoredFold) -> dict:
    return {
        "train_start": fold.train_start.isoformat(),
        "train_end": fold.train_end.isoformat(),
        "train_rows": fold.train_rows,
        "feature_date": fold.feature_date.isoformat(),
        "scored_date": fold.scored_date.isoformat(),
    }


def _level_key(level: float) -> str:
    """A JSON object key for a quantile level, stable across runs.

    `repr` of a float is stable in Python but is not a promise about a file
    format, and `0.5` and `0.50` would be two keys for one level. Formatted to
    a fixed width instead, so the declared grid always reads `0.05 0.25 0.50
    0.75 0.95` and a reader diffing two artifacts is diffing values.
    """

    return f"{float(level):.2f}"


def climatology_exceedance(minimum_history: int = 20) -> ExceedancePredictor:
    """Unconditional exceedance from the training distribution alone.

    The reference `AGENT_CONTRACT.md`, "Decided: stress target and event
    holdouts", names in "Metrics": "Brier skill score **against climatology**".
    A climatology is what a skill score is measured against, so it is the first
    exceedance predictor this repo needs and the only one it needs before there
    is something to compare. It is also the honest predictor for a knowledge
    holdout, where the whole question is what a model that has seen only calm
    history says about a crisis it was never shown.

    Shape is `ExceedancePredictor`: called once with the training rows, the
    feature rows and the tau family, returning `P(value > tau)` per scored day
    per tau. `P(Y > tau)` is the fraction of training spreads strictly above
    `tau` -- strictly, matching the contract's `P(spread > tau)` and the label
    columns' `stress_gt_*`.

    **The feature rows are read for their count and nothing else**, which is the
    same statement as "the curve is the same on every scored day" written in the
    place a reader of the code will look. When the interface widened to carry
    covariates this predictor did not change what it reads: it reads
    `spread_bps` off the training rows, and the numbers it reported before the
    widening it reports after it, unchanged.

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
        train_rows: Sequence[DailyObservation],
        feature_rows: Sequence[DailyObservation],
        taus: Sequence[float],
    ) -> ExceedanceCurves:
        history = [float(row.spread_bps) for row in train_rows]
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
        # `("spread_bps",)` for the same reason `FittedPersistence` reports it:
        # the target is the one column this reads, and it reads it off the
        # training rows rather than off a feature row. The purge must still
        # cover its sources, so it is declared rather than reported as empty --
        # an empty claim would pass any declaration, which is the check
        # inverted.
        return ExceedanceCurves(
            tuple(curve for _ in feature_rows), ("spread_bps",)
        )

    return fit_predict


def arx_exceedance(
    regressors: Sequence[str], minimum_history: int = 20
) -> ExceedancePredictor:
    """Conditional exceedance from the ARX's own fitted residual law.

    The second implementer of `ExceedancePredictor`, and what makes it an
    interface. With only `climatology_exceedance` the knowledge holdout could
    score nothing but the unconditional baseline a skill score is measured
    against -- there was nothing on the other side of the comparison -- and this
    repository has already settled that an interface with one implementer is a
    description rather than an interface.

    `fit_arx` is fitted on the training rows the evaluator hands over, which is
    everything that cleared the purge gap ahead of the window and nothing from
    inside it, and the fitted model is then read once per feature row. **The
    curve moves across scored days**, because the design row moves; that it
    moves is the entire difference between this and the climatology, whose curve
    is flat by construction.

    **The distribution is the one the ARX already fits.** `predict_stress`
    inverts `_quantile` over the leave-one-out residuals through
    `_exceedance_from_residuals` -- no Gaussian, no fitted parametric family, no
    smoothing and no Laplace correction. Above the fitted support a zero stays a
    zero, for the reason `climatology_exceedance` gives at length: a model that
    put no weight where the event actually went is the most informative result
    this evaluator can produce, and a prior nobody declared would turn it into a
    small number that merely looks like a poor forecast.

    Nothing is re-derived here. The construction is `FittedArx.predict_stress`,
    which is the same `_exceedance_from_residuals` persistence uses; reading the
    residual law a second time in this function would be a second opinion about
    one distribution.

    `features_read` comes off the fitted model, so it is `spread_bps` plus the
    declared regressors -- the autoregressive term included, which is the half a
    predictor reporting only what it was handed would leave out.

    Args:
        regressors: the ordered exogenous regressor names, as `fit_arx` takes
            them. **Required, with no default**, for the reason `fit_arx`
            refuses one: a default would be a silent assumption about which
            columns a model is entitled to read.
        minimum_history: the shortest training frame that may produce a fitted
            law. Passed to `fit_arx`, which raises below it.

    Returns:
        A `fit_predict` callable suitable for `event_eval.evaluate_event_window`.

    Raises:
        ValueError, MissingRegressorError, SingularDesignError, LookAheadError:
            at call time, whatever `fit_arx` raises on the training frame it is
            given. They are not caught and re-wrapped here: a refusal to fit is
            the fitter's statement about the frame, and a wrapper would put a
            second vocabulary between it and the caller.
    """

    declared = tuple(str(name) for name in regressors)

    def fit_predict(
        train_rows: Sequence[DailyObservation],
        feature_rows: Sequence[DailyObservation],
        taus: Sequence[float],
    ) -> ExceedanceCurves:
        model = fit_arx(train_rows, declared, minimum_history=minimum_history)
        return ExceedanceCurves(
            tuple(model.predict_stress(row, taus) for row in feature_rows),
            model.features_read,
        )

    return fit_predict
