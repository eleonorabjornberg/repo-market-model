"""Leakage-safe baselines and rolling-origin evaluation.

The forecast interface `AGENT_CONTRACT.md` declares --

    fit(train_frame)            -> fitted model carrying its cutoff
    predict(feature_row)        -> quantile vector at contract.QUANTILE_LEVELS
    predict_stress(feature_row) -> exceedance vector aligned to the declared taus_bp

-- has several implementers here, which is the point of the second one and, in
a different way, of the third. Not counted: this sentence read "three" until
`FittedRollingResidualLaw` arrived and made it four, and
`tests/test_contract.py::ForecastInterfaceCoverageTests` discovers the
implementations rather than reading a list.

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
`features` set, resolves it through `contract.field_sources_for_features` to
`(source, field)` pairs, and sizes the gap with `registry.max_release_lag_days`
over exactly those fields -- `_derive_purge`, which the event path calls too.
Over fields rather than sources because a source is too coarse a thing to
price: one source carries an administered rate that is never revised beside
weeklies that are, and priced as a source neither of them can be priced. That
closes the question the purge block left open -- the number was required, and
nothing checked that whoever produced it covered what the model reads -- and it
is the first time this seam has been answered rather than routed around. The
declaration is verified against the first fitted model, because a declaration
nothing checks is a comment.

The exceedance interface
------------------------

`ExceedancePredictor` is the second interface this module declares, and it is
the knowledge holdout's: `event_eval.evaluate_event_window` calls one of these
and scores what comes back. It has three implementers here, for the same reason
the forecast interface needed a second one.

`climatology_exceedance` is the unconditional baseline a Brier skill score is
measured against. `arx_exceedance` is the conditional side of that comparison,
and its curve is `FittedArx.predict_stress` -- the empirical residual law the
ARX already fits, read once per feature row. Until the interface carried rows
rather than one series of values no covariate could reach a model through it,
so the climatology was the only thing the knowledge holdout could score and the
skill score had nothing to be measured against.

`threshold_exceedance` is the third, and it is here because the first two move
their curves for one reason and it moves its own for two. The ARX's curve
responds to a covariate smoothly, through the design row. A threshold model's
covariate also decides **which fitted relationship is in force**: two feature
rows straddling the fitted cutoff and differing in nothing else get different
centres and therefore different exceedance probabilities, discontinuously.
`FittedThreshold.features_read` already reports the regime variable, so the
knowledge-holdout path sizes its gap over that column's fields too -- which is
the read this implementer exists to put through `event_eval`'s declaration
check, the second and last path on which it had never been checked.

That alias was declared twice before this block, here and as
`event_eval.FitPredict`. It is declared once now, here, and the evaluator
imports it -- so `baseline` still does not depend on the evaluator it feeds.

Two evaluators, two holdouts
----------------------------

`rolling_exceedance_backtest` is the second consumer of `ExceedancePredictor`
and the first place the contract's headline metric can be computed. Until it
landed, `metrics.brier_skill_score`, `corp_decomposition`,
`corp_reliability_curve`, `log_score` and `threshold_weighted_crps` were
implemented, unit-tested, and called by nothing in `src/repo_model/` outside
`metrics.py` -- not because anyone forgot, but because the only evaluator that
consumed an exceedance curve was `event_eval`, where `AGENT_CONTRACT.md`
forbids an aggregate. The headline number was not merely unpublished; it had
nowhere to be computed.

The two paths are the contract's two holdout roles and they are not variants of
each other. `event_eval` produces the knowledge holdout: crises stripped from
training entirely, scored once per window, reported as a curve and a realized
path and never averaged into the main table. `rolling_exceedance_backtest`
produces the scoring holdout: an expanding rolling origin over the whole panel,
where a crisis date is available for training once it is in the past. The
aggregate belongs on the second and nowhere else, and
`ExceedanceBacktestReport.holdout_role` puts that on the artifact so the
distinction survives into the file rather than living only in these paragraphs.

What the two exceedance evaluators share, they share by import, which is the
only form of sharing that cannot drift: `_derive_purge`, `_feature_index`,
`_check_fitter_stayed_inside`, `_validate_taus` and `_validate_prediction`. The
last two moved here from `event_eval` when the second consumer arrived, for the
reason `ExceedancePredictor` itself lives here -- what a predictor may return
is a property of the interface, and the interface is declared in this module.

`rolling_persistence_backtest` is deliberately *not* generalised to cover it.
The two score different interfaces returning different things -- a quantile
vector at `QUANTILE_LEVELS` against a realized value, versus an exceedance
curve over the declared tau family against a realized 0/1 at each tau -- and a
parameter that switched between two return types would be two functions wearing
one name. They share the splitter, the gap, the feature-row rule and the fold
record, and those are exactly the parts that must not disagree.
"""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
from bisect import bisect_right
from dataclasses import dataclass, field
from datetime import date, time, timedelta
from pathlib import Path
from types import MappingProxyType
from typing import (
    Any,
    Callable,
    Iterable,
    List,
    Mapping,
    NamedTuple,
    Optional,
    Protocol,
    Sequence,
    Tuple,
)

from .contract import (
    DERIVED_FEATURES,
    QUANTILE_LEVELS,
    field_sources_for_features,
)
from .data import DailyObservation, load_stress_thresholds
from .metrics import (
    CorpDecomposition,
    MetricError,
    ReliabilityCurve,
    _validate_levels,
    brier_score,
    brier_skill_score,
    corp_decomposition,
    corp_reliability_curve,
    crps_from_quantiles,
    log_score,
    pinball_loss,
    stationary_bootstrap_interval,
    threshold_weighted_crps,
)
from .registry import RegistryContractError, max_release_lag_days
from .splits import (
    LookAheadError,
    SplitError,
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


#: The two holdout roles from `AGENT_CONTRACT.md`, "Two holdout roles". They
#: are constants rather than bare strings at the call site so that no artifact
#: can record a role nobody declared, and so that a grep for either name finds
#: every place the distinction is made.
#:
#: They live here rather than in `event_eval` because there are now two
#: evaluation paths and they produce different roles: `event_eval` produces the
#: knowledge holdout, `rolling_exceedance_backtest` below produces the scoring
#: one. A two-valued distinction spelled in the module that produces one of the
#: values is a distinction whose halves can drift, and `event_eval` already
#: imports from here -- the same reasoning, and the same direction, as
#: `ExceedancePredictor` itself. `event_eval` re-exports both, so every
#: existing importer is unaffected.
#:
#: The contract's rule that separates them is not a naming convention: the
#: knowledge holdout is "reported separately and never averaged into the main
#: table", so an artifact that carries an aggregate has to be able to say which
#: table it is.
SCORING_HOLDOUT = "scoring"
KNOWLEDGE_HOLDOUT = "knowledge"


def _validate_taus(taus: Sequence[float]) -> Tuple[float, ...]:
    """The declared exceedance family, checked: non-empty, strictly ascending, finite.

    Moved here from `event_eval` when the rolling exceedance path arrived and
    needed the same check. Both paths consume the same declared tau family from
    `data.load_stress_thresholds`, and the brief for that block names the
    failure directly: a path that reads the family once and indexes it twice
    can disagree with itself. Two validators would be two readings of one
    declaration, which is the same failure one level up.
    """

    family = tuple(float(tau) for tau in taus)
    if not family:
        raise SplitError("taus must declare at least one threshold")
    for index in range(1, len(family)):
        if family[index] <= family[index - 1]:
            raise SplitError("taus must be strictly ascending")
    if not all(math.isfinite(tau) for tau in family):
        raise SplitError("taus must be finite")
    return family


def _validate_prediction(
    prediction: Any,
    scored_rows: int,
    taus: Tuple[float, ...],
) -> Tuple[Tuple[float, ...], ...]:
    """The curves, checked; the `features_read` claim is checked by its guard.

    Takes an `ExceedanceCurves` rather than a bare sequence, and says so: a
    predictor that returned only curves would be one that made no claim about
    what it read, and the declaration check downstream would then have nothing
    to compare against and would pass by default.

    Moved here from `event_eval` alongside `_validate_taus`, and for the same
    reason: what an `ExceedancePredictor` may return is a property of the
    interface, which is declared in this module, and both evaluators now hold
    predictions to it. The knowledge holdout checks a window's worth of days at
    once and the rolling path checks one day per fold; that is the only
    difference, and it is the argument.
    """

    if not isinstance(prediction, ExceedanceCurves):
        raise SplitError(
            f"fit_predict must return an ExceedanceCurves, got "
            f"{type(prediction).__name__}; the curves alone carry no account of "
            f"what the model read, and the declared feature set is checked "
            f"against that account"
        )
    rows = list(prediction.curves)
    if len(rows) != scored_rows:
        raise SplitError(f"fit_predict returned {len(rows)} rows for {scored_rows} days")
    checked = []
    for day, row in enumerate(rows):
        curve = tuple(float(p) for p in row)
        if len(curve) != len(taus):
            raise SplitError(
                f"day {day}: {len(curve)} probabilities for {len(taus)} taus"
            )
        for position, probability in enumerate(curve):
            if not math.isfinite(probability) or not 0.0 <= probability <= 1.0:
                raise SplitError(
                    f"day {day}, tau {taus[position]}: {probability} is not a probability"
                )
        # P(Y > tau) cannot rise as tau rises. A model that says otherwise is
        # broken, and averaging over it would hide that.
        for position in range(1, len(curve)):
            if curve[position] > curve[position - 1]:
                raise SplitError(
                    f"day {day}: exceedance rises from tau {taus[position - 1]} "
                    f"to {taus[position]} ({curve[position - 1]} -> {curve[position]})"
                )
        checked.append(curve)
    return tuple(checked)


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
    implementations by walking the package rather than reading a list.
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
        that `iorb` arrives from `fred_macro_latest_vintage`'s `IORB` field,
        and it must not have to. `contract.field_sources_for_features` is the
        only thing that makes that step, and it makes it once, before the first
        fold.

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


class ProvenanceMismatchError(ValueError):
    """A build manifest beside the panel does not describe the panel scored.

    `REPRODUCIBILITY.md`'s "Requirements for a reportable experiment" asks a
    run record to identify "the point-in-time panel build". The build manifest
    `data.write_daily_panel` leaves beside a panel is that identification, and
    a record that embeds one has told its reader the numbers above it were
    computed on the build the manifest describes.

    Raised rather than warned about, and rather than resolved by omitting the
    section. Publishing a manifest beside a panel it does not describe is worse
    than publishing no provenance at all: no provenance makes a reader ask, and
    wrong provenance makes a reader believe. The refusal leaves no artifact on
    disk, because both commands write only after the document is built.

    A `ValueError` subclass so the CLI dispatcher's `(OSError, ValueError)`
    already covers it without naming a new type -- exit 2, message, no file --
    which is the same shape every other refusal on this path has.
    """


class IncomparablePurgeError(ValueError):
    """Two models in one comparison derived different purge gaps.

    The paired difference this module reports is a difference *per origin*, and
    an origin set is a function of the gap: `rolling_origin` builds the folds
    from `min_train`, the step and the purge, so two declarations that price
    different gaps produce two different fold sequences over the same panel.
    Subtracting one model's loss series from the other's would then subtract
    losses computed on different days, in different numbers, and call the
    result a difference between models.

    Nothing downstream could see it. Both series are real losses from real
    fits, the arithmetic is correct, and the mean of the subtraction is a
    finite number the interval will happily be computed around -- the same
    shape as a gap computed correctly over the wrong sources, one level up.

    **This is the one comparability question the single fold loop does not
    settle.** Everything else is settled by construction: one loop, one purge,
    one feature row per origin, both models fitted on the same training rows
    and scored on the same day. The gap is the exception because it is derived
    from the *declaration* before the loop exists, so it has to be checked
    before the loop is built rather than observed inside it.

    Raised, never asserted, and never resolved by taking the wider of the two:
    a comparison run under a gap neither declaration asked for is a third run
    that nobody requested, and its numbers would be attributed to two models
    that were never scored that way.

    A `ValueError` subclass, so the CLI dispatcher already turns it into exit 2
    with a message and no artifact -- the shape every other refusal here has.
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
    #: `cli_eval` prints them straight off the report for that reason, these
    #: three and `field_sources` below.
    features: Tuple[str, ...] = ()
    sources: Tuple[str, ...] = ()
    #: The `(source_id, field)` pairs the gap was actually sized over, beside
    #: the source IDs projected from them. Both are carried, and the pairs are
    #: the finer fact: one source can supply a field that prices and a field
    #: that is refused, so `sources` alone no longer says what was priced.
    #: Sized over fields since the field-priced-purge block; before it, a
    #: source-level `release_lag` stood in for every field of a source and the
    #: target variable was unpriceable because one of them was.
    field_sources: Tuple[Tuple[str, str], ...] = ()
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


class FittedRollingResidualLaw:
    """Persistence's point rule with its residual law cut to a trailing window.

    `PLAN.md` Phase 2 lists "rolling mean/quantiles" among the four benchmarks
    and no rolling anything existed. This is the quantile half of that line, and
    it is aimed at the one thing persistence is measurably bad at: it wins on
    accuracy and **under-covers its own nominal interval**, so the interval is
    what a challenger has to fix, and the interval is the residual law.

    The point forecast is `FittedPersistence`'s, unchanged -- the last observed
    spread. What differs is the sample the predictive distribution is read off:
    the **last `window` one-step residuals before the cutoff, in time order**,
    rather than every residual in the training frame. A frame of `n` rows
    carries `n - 1` one-step residuals and this law is the final `window` of
    them. Under an expanding training window persistence's law grows at every
    origin and so averages over regimes it has left; this one does not.

    Fitted state is the residual vector, the cutoff and `window`. `window` is
    carried for the reason `FittedArx.regressors` is: a fitted object that
    cannot say which law it used cannot be audited, and a trailing-window law
    and a full-sample law fitted on a short frame are otherwise the same object.

    **Not a subclass of `FittedPersistence`**, though the point rule is
    identical and inheritance would save a dozen lines. Three tests in
    `tests/test_baseline.py` assert `isinstance(report.model, FittedPersistence)`
    to pin that the default fitter is the benchmark and not a challenger; a
    subclass satisfies all three, so the blunting would land on exactly the
    assertions that keep a challenger from being published as the baseline.
    `FittedForecastModel`'s own docstring gives the general form of the argument
    -- the models here share an interface and no implementation.

    **`window` is declared, never chosen from data.** There is no search over
    window lengths and no default. A length picked by scoring windows against
    the panel is a hyperparameter fitted outside `fit`, which the contract
    forbids in those words, and neither track can see the panel to pick one
    honestly in any case.

    Raises: see `fit_rolling_residual_law`, which is the only thing that builds
    one of these.
    """

    __slots__ = ("_residuals", "cutoff", "levels", "window")

    def __init__(
        self,
        residuals: Sequence[float],
        cutoff: date,
        window: int,
        levels: Sequence[float] = QUANTILE_LEVELS,
    ) -> None:
        #: Sorted here, as in every other fitted model in this module, because
        #: `_quantile` and `_exceedance_from_residuals` read order statistics and
        #: the inversion between them is only exact over one ordering. The
        #: **selection** of which residuals these are happened before this call,
        #: in time order, in `fit_rolling_residual_law`. Sorting and selecting
        #: are two steps and their order is the whole content of this model:
        #: sorting first and taking the tail yields the `window` largest
        #: residuals, which is a plausible-looking sample, biased upward, and
        #: not a trailing window of anything.
        self._residuals: Tuple[float, ...] = tuple(sorted(float(r) for r in residuals))
        self.cutoff: date = cutoff
        self.window: int = int(window)
        self.levels: Tuple[float, ...] = _validate_levels(levels)

    def __repr__(self) -> str:  # pragma: no cover - diagnostic only
        return (
            f"FittedRollingResidualLaw(cutoff={self.cutoff.isoformat()}, "
            f"window={self.window}, residuals={len(self._residuals)})"
        )

    @property
    def residuals(self) -> Tuple[float, ...]:
        """The fitted residual sample, ascending. A copy-free read-only view."""

        return self._residuals

    @property
    def features_read(self) -> Tuple[str, ...]:
        """`spread_bps`, and nothing else.

        The same claim `FittedPersistence.features_read` makes, and true for the
        same reason: the point rule reads the spread and the law is built from
        differences of it. Narrowing the law to a trailing window changes how
        many rows are read, never which columns, so the purge this model is
        sized against is persistence's purge.
        """

        return ("spread_bps",)

    def trained_beyond(self, feature_row: DailyObservation) -> bool:
        """Was this model fitted on rows dated after `feature_row`?

        Same question, same answer, same reason as `FittedPersistence`. The
        window narrows which rows the *law* came from and does not move the
        cutoff: a model whose residuals all predate the feature row can still
        have been fitted on a frame that did not, and the cutoff is what says so.
        """

        return feature_row.date < self.cutoff

    def point_forecast(self, feature_row: DailyObservation) -> float:
        """The last observed spread. Persistence's point rule, by construction.

        This model is the residual law and nothing else; if this returned
        anything other than the spread it would be a different challenger and
        the interval finding it was built for would no longer be what moved.
        """

        return feature_row.spread_bps

    def predict(self, feature_row: DailyObservation) -> Tuple[float, ...]:
        """One predicted spread quantile per declared level, in declared order.

        The persistence point forecast shifted by the windowed residual quantile
        at each level, through the same `_quantile` every other model here reads
        its grid with.
        """

        anchor = self.point_forecast(feature_row)
        return tuple(anchor + _quantile(self._residuals, level) for level in self.levels)

    def predict_stress(
        self,
        feature_row: DailyObservation,
        taus: Optional[Sequence[float]] = None,
    ) -> Tuple[float, ...]:
        """`P(spread > tau)` per tau, derived from the law `predict` reports.

        The same derivation as the other three models, over this model's own
        residual vector: `_exceedance_from_residuals` inverts `_quantile`, so
        `predict_stress` at `predict`'s `Q(q)` returns `1 - q` here too. Nothing
        in this object was fitted to a label, and the windowing happens before
        either output exists rather than between them -- a law that `predict`
        and `predict_stress` disagreed about would be two laws.
        """

        family = _validate_taus_bp(
            load_stress_thresholds()["taus_bp"] if taus is None else taus
        )
        anchor = self.point_forecast(feature_row)
        return tuple(
            _exceedance_from_residuals(self._residuals, tau - anchor) for tau in family
        )


def fit_rolling_residual_law(
    train_frame: Sequence[DailyObservation],
    window: int,
    cutoff: Optional[date] = None,
    minimum_history: int = 20,
    levels: Sequence[float] = QUANTILE_LEVELS,
) -> FittedRollingResidualLaw:
    """Fit the trailing-window residual law on `train_frame`.

    The one-step residuals are formed in the frame's own order, and the law is
    the **last `window` of them**, the ones nearest the cutoff. The selection is
    made here, on the time-ordered sequence, before anything is sorted: the
    fitted object sorts what it is handed, so a caller that handed it a sorted
    vector's tail would be handing over the `window` largest residuals under
    this function's name.

    Args:
        train_frame: the training rows, strictly ascending by date. Residuals
            are the one-step differences within this frame and nothing else,
            exactly as in `fit`.
        window: how many trailing residuals the law is read from. **Required,
            with no default**, for the reason `fit_arx` refuses a default
            regressor list and `--model` refuses a default model: a default is a
            decision nobody made, and this one decides how much history the
            reported interval is a statement about. It must be at least 2 -- a
            one-residual law makes `_quantile` constant and every declared level
            the same number -- and no larger than the residuals the frame
            carries, which is `len(train_frame) - 1`.
        cutoff: the last date the model was allowed to see. Defaults to the
            frame's own last date, and is checked against it rather than
            trusted, as in `fit`.
        minimum_history: the shortest frame that may produce a fitted law.
            Checked against the frame, not against `window`: the two are
            different statements, and the backtest passes this at every origin.
        levels: the quantile grid, defaulting to the declared one.

    Returns:
        A `FittedRollingResidualLaw` carrying the trailing residuals, the
        cutoff and the window it used.

    Raises:
        LookAheadError: if any training row is dated after `cutoff`.
        SplitError: if the frame is not strictly ascending by date.
        ValueError: if the frame is shorter than `minimum_history`, if `window`
            is below 2, or if `window` exceeds the residuals the frame carries.
            A window longer than the history is not silently truncated to the
            full sample: that is this model collapsing back into persistence
            while still being reported as a challenger.
    """

    requested = int(window)
    if requested < 2:
        raise ValueError(
            f"window must be at least 2, got {requested}; a law read from one "
            f"residual is a point mass and every declared quantile level would "
            f"report the same number"
        )

    rows = list(train_frame)
    if len(rows) < minimum_history:
        raise ValueError(
            f"rolling residual law needs at least {minimum_history} training "
            f"rows, got {len(rows)}; a residual quantile from fewer is not a "
            f"fitted law"
        )

    dates = [row.date for row in rows]
    ensure_strictly_ascending(dates, label="training frame dates")

    declared = dates[-1] if cutoff is None else cutoff
    if dates[-1] > declared:
        raise LookAheadError(
            f"training frame reaches {dates[-1]}, past its cutoff {declared}; "
            f"a fitted model may not contain a row it was not allowed to see"
        )

    # In time order, and kept that way until the slice below has been taken.
    ordered = [
        rows[index].spread_bps - rows[index - 1].spread_bps
        for index in range(1, len(rows))
    ]
    if requested > len(ordered):
        raise ValueError(
            f"window {requested} exceeds the {len(ordered)} one-step residuals "
            f"a {len(rows)}-row frame carries; truncating it to the frame would "
            f"make this the persistence law under another model's name, which "
            f"is the comparison this model exists to be one side of"
        )

    return FittedRollingResidualLaw(
        ordered[-requested:], declared, requested, levels
    )


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


#: Why an absent column is not an unobserved one, in the words that fit the
#: read. The two differ in what happens to a gap: a regressor's is imputed from
#: the fitted training-window mean, a threshold variable's is refused outright
#: (`UnobservedThresholdError`). One sentence covering both would be wrong
#: about one of them, and this message is where a reader of a traceback learns
#: which read they are looking at.
_IMPUTED_CONTRAST = (
    "An absent column is not an unobserved value: an unobserved value arrives "
    "as None and is imputed from the fitted training-window mean, and treating "
    "a missing column as one would forecast from a number the row never "
    "contained"
)
_REFUSED_CONTRAST = (
    "An absent column is not an unobserved value: an unobserved value arrives "
    "as None and is refused rather than imputed, and treating a missing column "
    "as one would file this row under whichever regime the absence fell in"
)


def _raw_regressor(
    row: DailyObservation,
    name: str,
    where: str,
    role: str = "a declared regressor",
    contrast: str = _IMPUTED_CONTRAST,
) -> Optional[float]:
    """The column as the row carries it: a float, or `None`.

    Absent key and `None` are returned as different things -- a raise and a
    `None` -- because they are different facts. See `MissingRegressorError`.

    `role` and `contrast` say what the model read the column **as**. The
    message used to assert that "the model was fitted on that regressor"
    whatever the read was, and that is false of a threshold variable -- nothing
    is fitted on it; it selects which fit applies -- and false again of `sofr`,
    which a `spread_bps` regime reads without the model declaring it as a
    regressor at all. A message naming the wrong read sends the reader to the
    wrong flag.
    """

    try:
        raw = row.values[name]
    except KeyError:
        raise MissingRegressorError(
            f"{where} for {row.date} carries no {name!r}; the model reads it as "
            f"{role} and cannot find it here. {contrast}"
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

    * `threshold_variable` -- what the regime is read off: a panel column, or
      `spread_bps`, which is not one. `DailyObservation` computes the spread
      from `sofr` and `iorb` and no ingest writes a `spread_bps` key, so a
      regime read off the autoregressive term -- a SETAR -- reaches it through
      the property and refuses on either component. `_threshold_value` is where
      that fork lives; see `SPREAD_VARIABLE`.
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
        reader would. A `spread_bps` regime is always that case, since the
        design carries the spread as its autoregressive term whatever the
        regime is read off; the tuple is unchanged by declaring it.

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

        The read itself is `_threshold_value`, the one the fit uses, so a
        regime variable the fit could read is one the forecast can read and the
        two refuse the same rows for the same reasons. For `spread_bps` that
        read is of `sofr` and `iorb`.

        Raises:
            MissingRegressorError: if the row does not carry the column, or,
                for `spread_bps`, either component of it. The message names the
                column that is absent.
            UnobservedThresholdError: if it carries it as `None`, or, for
                `spread_bps`, either component as `None`.
        """

        observed = _threshold_value(
            feature_row, self.threshold_variable, "feature row"
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


#: The one regime variable that is not a panel column. `DailyObservation`
#: computes it from `sofr` and `iorb`; `row.values` has never carried a
#: `spread_bps` key and no ingest writes one. A regime read off the
#: autoregressive term is a SETAR, which is what the user specified, and
#: reading it by name off the mapping raised `MissingRegressorError` on the
#: first training row of every such fit.
SPREAD_VARIABLE = "spread_bps"

#: What it is made of, taken from the contract's own decomposition rather than
#: restated here. `contract.DERIVED_FEATURES` is out of both tracks' reach, and
#: that is the point: the purge resolves `spread_bps` to these two fields to
#: price the gap, and this regime read resolves it to the same two to read the
#: value. A local literal would let the two drift, and the drift would be
#: invisible -- the model would keep fitting while the gap was priced over
#: columns it no longer read.
SPREAD_COMPONENTS = DERIVED_FEATURES[SPREAD_VARIABLE]


def _unobserved_threshold(
    row: DailyObservation, name: str, where: str, variable: str
) -> UnobservedThresholdError:
    """The refusal, in one place, for the fit and the forecast alike.

    `name` is the column that is unobserved and `variable` the regime variable
    it makes unreadable; they are the same string except for `spread_bps`,
    where a gap in `sofr` or `iorb` is what makes the spread unobserved and
    naming only the spread would send the reader looking for a column the panel
    does not have.

    One message for both reads, distinguished by `where`. Fitting and
    forecasting refuse the same fact for the same reason, and two texts for it
    were two things to keep true.
    """

    subject = (
        f"{name!r} as None"
        if name == variable
        else f"{name!r} as None, so its {variable!r} is unobserved"
    )
    return UnobservedThresholdError(
        f"{where} for {row.date} carries {subject}; a regime is a choice "
        f"between two fitted models and cannot be made from an unobserved "
        f"value. A regressor is imputed because it enters a sum; a threshold "
        f"variable selects the sum, and an imputed mean would put every "
        f"unobserved row in whichever regime the training mean falls in, "
        f"silently and uniformly. Fit on a window that observes the threshold "
        f"variable, or declare one this window observes"
    )


def _spread_threshold_value(row: DailyObservation, where: str) -> float:
    """`row.spread_bps`, with the absent and unobserved cases refused first.

    The number comes off the property, so a regime read off the spread uses the
    same arithmetic as the target and the autoregressive term. A local
    `100.0 * (sofr - iorb)` here would be a second definition of the spread,
    free to disagree with `DailyObservation`'s and answering to no test that
    compares them.

    The property cannot be the whole read, though: it raises `KeyError` on an
    absent component and `TypeError` on an unobserved one, and this module owes
    its callers `MissingRegressorError` naming the component that is missing and
    `UnobservedThresholdError` for a gap. So each component goes through
    `_raw_regressor` first and the property is called only once both are known
    to be observed finite floats.
    """

    for component in SPREAD_COMPONENTS:
        observed = _raw_regressor(
            row,
            component,
            where,
            role=f"a component of the {SPREAD_VARIABLE!r} regime variable",
            contrast=_REFUSED_CONTRAST,
        )
        if observed is None:
            raise _unobserved_threshold(row, component, where, SPREAD_VARIABLE)
    return row.spread_bps


def _threshold_value(row: DailyObservation, name: str, where: str) -> float:
    """The threshold variable on `row`, refusing an unobserved one.

    `_raw_regressor` for the absent-key and non-finite halves, so those two
    paths raise exactly what every other read of a panel column raises, and
    then a refusal rather than an imputation for `None`. See
    `UnobservedThresholdError` for why this is the one column that is not
    imputed.

    `spread_bps` is dispatched away because it is not a panel column at all;
    see `SPREAD_VARIABLE`. Every other regime variable is a column and is read
    as one.
    """

    if name == SPREAD_VARIABLE:
        return _spread_threshold_value(row, where)
    observed = _raw_regressor(
        row,
        name,
        where,
        role="the threshold variable",
        contrast=_REFUSED_CONTRAST,
    )
    if observed is None:
        raise _unobserved_threshold(row, name, where, name)
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
        threshold_variable: what the regime is read off -- a panel column, or
            `spread_bps`, which is computed from `sofr` and `iorb` rather than
            carried (see `SPREAD_VARIABLE`). Required and undefaulted for the
            reason `regressors` is and more sharply: it does not merely
            contribute a term, it chooses the model, and a default would be a
            silent claim about what a regime is allowed to be a function of. It
            may also appear in `regressors` -- a variable can both shift the
            level and switch the relationship -- and `spread_bps` always does,
            since it is the autoregressive term; `features_read` reports it
            once either way.
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


def _derive_purge(
    registry: Mapping[str, Mapping[str, object]],
    features: Tuple[str, ...],
    *,
    decision_time: time,
) -> Tuple[Tuple[Tuple[str, str], ...], Tuple[str, ...], int]:
    """Resolve a declared feature set to fields, and price the gap over those.

    The one derivation both evaluation paths use. `rolling_persistence_backtest`
    and `event_eval.evaluate_event_window` call this and nothing else; a second
    copy of these three lines is a second answer to "what sized the gap", and
    two answers agree until they do not. `_check_fitter_stayed_inside` already
    lives here for that reason and is imported by the event path rather than
    restated.

    **Fields, not sources.** `contract.field_sources_for_features` resolves the
    declaration to `(source_id, field)` pairs and `registry.max_release_lag_days`
    prices each pair by the field's own declared lag where the source carries
    one. A source is too coarse a thing to price: `fred_macro_latest_vintage`
    carries an administered rate that is never revised beside H.4.1 weeklies
    that are, under one source-level `release_lag` of basis
    `snapshot_retrieved_at`. Priced by the source, every field of it is
    unpriceable and `iorb` -- and therefore `spread_bps`, and therefore the
    target -- goes with them. Priced by the field, `IORB` resolves on its
    declared record-date lag and the weeklies stay refused, which is the
    correct pair of answers rather than one answer applied twice.

    The source IDs are still returned, projected from the pairs rather than
    resolved a second time through `contract.sources_for_features`. They are
    what `BacktestReport.sources`, `EventWindowReport.sources` and
    `_check_fitter_stayed_inside` have always carried, and a second resolution
    is the drift this function exists to prevent. `sources_for_features` is
    left in place and still called by `cli_eval` for the event journal's hash,
    which must not move on a registry that declares no fields.

    **The refusal narrows; it does not disappear.** A field with no declared
    revision policy on a `snapshot_retrieved_at` source is still refused, and
    the refusal is Track A's -- `RegistryContractError` with Track A's message,
    which names the source. This adds the fields the gap was being sized over
    and nothing else: the registry's message cannot name the field, because a
    field it has no declaration for never reaches the branch that appends one,
    and a reader told only "fred_macro_latest_vintage" cannot tell a refused
    `WRESBAL` from a refused `IORB`. Softening it -- an exemption for the event
    path, a snapshot basis mapped to zero, a `revision_policy` invented here --
    is not available: a derived purge still cannot be zero, and the field
    declaration is a decision about the world and the human's to make.

    Args:
        registry: the parsed source registry.
        features: the declared feature set, already a tuple.
        decision_time: when the forecast is made.

    Returns:
        `(field_sources, sources, purge)` -- the `(source_id, field)` pairs the
        gap was sized over, the source IDs projected from them, and the gap.

    Raises:
        UndeclaredFeatureError: `features` names a column
            `contract.field_sources_for_features` cannot classify, or one
            declared to have no ingesting source.
        RegistryContractError: the derived fields cannot support a safe bound.
    """

    field_sources = field_sources_for_features(features)
    sources = tuple(sorted({source for source, _field in field_sources}))
    try:
        purge = max_release_lag_days(
            registry, field_sources, decision_time=decision_time
        )
    except RegistryContractError as exc:
        raise RegistryContractError(
            f"{exc} -- sizing the gap over "
            f"{', '.join(f'{s}.{f}' for s, f in field_sources)}, the fields the "
            f"declared feature set {list(features)} reads"
        ) from exc
    return field_sources, sources, purge


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
    calls `_derive_purge`, which resolves
    `contract.field_sources_for_features(features)` to `(source, field)` pairs
    and takes `registry.max_release_lag_days(...)` over those fields, then
    builds folds -- the order `cli_eval` already used on the event path. The
    event path calls the same `_derive_purge`, so the two cannot drift. There
    is no `purge` argument. Who computed the number was the open question the purge left
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
            `contract.field_sources_for_features` cannot classify, or one it
            declares to have no ingesting source. Raised before any fold is
            built, since a feature set that cannot be resolved has no gap and
            therefore no backtest.
        RegistryContractError: if the derived fields cannot support a safe
            bound -- an unknown source, an unusable `release_lag`, or a field
            of a `snapshot_retrieved_at` source that declares no revision
            policy and whose rows carry no `available_at`. Track A's refusal,
            with Track A's message; `_derive_purge` adds the fields the gap was
            being sized over and softens nothing. A field of a snapshot source
            that declares its own lag prices on it, and one that does not stays
            refused -- the same source, both answers.
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
    field_sources, sources, purge = _derive_purge(
        registry, declared, decision_time=decision_time
    )

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
        field_sources,
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

    return _seed_from(
        (
            panel_sha256,
            ",".join(sorted(report.features)),
            str(report.purge_days),
            "" if report.decision_time is None else report.decision_time.isoformat(),
        )
    )


def _seed_from(parts: Sequence[str]) -> int:
    """A non-negative 31-bit seed from a run's identity, as `\x00`-joined text.

    Extracted from `_report_seed` when the exceedance artifact arrived and
    needed a seed of its own. The *material* differs between the two artifacts
    and should -- they identify different runs -- but the digest that turns
    material into a seed must not, or two artifacts that agree about what they
    scored could still disagree about how a seed is derived from it. The
    continuous path's material is unchanged, so every interval it has ever
    reported is unchanged with it.
    """

    material = "\x00".join(parts)
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


@dataclass(frozen=True)
class IntervalCalibration:
    """A run's realized interval coverage, beside the probability it declared.

    **A dataclass and not a tuple, unlike `mae_bootstrap_interval`.** That
    function returns three values and a reader can hold three positions in
    their head. This one carries more, and a tuple of them is a shape where a
    caller who transposes `seed` and `replications` gets no error and a
    different interval. `PairedComparisonReport` made the same call for the
    same reason.

    **Every field is required**, for `PairedComparisonReport`'s reason:
    nothing constructs this by hand. It exists only as
    `interval_calibration`'s return value, and an optional field here would be
    a place a calibration statement could quietly fail to say what it was run
    at.
    """

    #: The mean of the coverage indicator series -- the fraction of scored
    #: origins whose actual fell inside its own interval. Computed from the
    #: same series the interval below is resampled from, deliberately, rather
    #: than read off `report.interval_coverage`: a centre and an interval
    #: derived from two different places can agree today and drift later, and
    #: the identity that the interval surrounds *this* number is the one thing
    #: a reader of a calibration statement must not have to take on trust.
    #: `rolling_persistence_backtest` computes the same mean from the same
    #: forecasts, so the two agree by construction on any report it produced.
    realized_coverage: float
    #: The probability the run's own declared quantile grid spans, from
    #: `report.quantile_levels` -- the outermost declared pair -- and not from
    #: the module constant and not from a literal. See `interval_calibration`.
    declared_probability: float
    #: The interval on `realized_coverage`, and the resample structure behind
    #: it. The block length is carried beside the endpoints for
    #: `mae_bootstrap_interval`'s reason -- an interval whose resample
    #: structure is unstated cannot be reproduced -- and it matters more here:
    #: a block length of 1 *is* the independence assumption, and a reader who
    #: cannot see the block length cannot tell which of the two was run.
    coverage_interval: Tuple[float, float]
    block_length: int
    seed: int
    replications: int
    level: float
    #: The indicator series itself, in origin order -- the thing the interval
    #: above is a resample of. Carried on the object because the interval is a
    #: function of the *arrangement* and not of the mean and the length: a block
    #: resample of 1685 ones and 395 zeros depends on where the zeros are, and
    #: where the zeros are is exactly what clustering of coverage failures is.
    #: An object that reported the endpoints without the series would be a
    #: calibration statement nobody downstream could reproduce, which is the
    #: defect `docs/runs/persistence_funding.json` was found to have. See
    #: `_calibration_document`, which publishes it, and
    #: `calibration_from_document`, which resamples it back.
    coverage_series: Tuple[float, ...]


def interval_calibration(
    report: BacktestReport, *, seed: int, block_length: Optional[int] = None
) -> IntervalCalibration:
    """Relate a run's realized interval coverage to the probability it declared.

    `PLAN.md`'s Phase 2 exit criterion is two clauses -- a model that beats
    persistence out of sample *and remains calibrated in the tails*.
    `paired_model_comparison` instruments the first. Until this function the
    second had nothing at all: `docs/runs/persistence_funding.json` carries
    `interval_coverage` and `interval_probability` adjacent in one object, over
    2080 folds, and **no code in this repository related them.** Nothing
    subtracted, compared, or put an interval on the difference, so a reader was
    left to do the arithmetic unaided and then to guess whether the gap was
    sampling noise at that fold count or the benchmark's intervals being wrong.

    The quantity is the **coverage indicator series**: one value per scored
    origin, `1` if `lower_bps <= actual_bps <= upper_bps` and `0` otherwise,
    read off `report.forecasts`, which already carries all three per origin.
    Its mean is what the backtest publishes as `interval_coverage`.

    **It is a bootstrap and not a binomial, and the reason is
    `paired_model_comparison`'s reason.** A binomial or normal-approximation
    interval on a proportion assumes the origins are independent. They are not:
    the folds overlap in horizon -- that is the whole argument behind
    `_maximum_horizon_overlap` -- so an independence-assuming interval here
    would be too narrow for the same structural reason that resampling two
    models apart was too narrow there. Every interval this project reports
    comes through `metrics.stationary_bootstrap_interval`, and this one does
    too.

    **The declared probability comes from the report, not from a literal and
    not from the module constant.** `INTERVAL_PROBABILITY` is derived from
    `contract.QUANTILE_LEVELS`, which is what *this checkout* declares; a
    report is a record of what *a run* declared. They are equal for every
    report `rolling_persistence_backtest` produced, because that function
    refuses a model whose levels disagree with the contract -- but reading the
    report keeps the statement true across a change to the grid, and a
    calibration statement that hard-codes `0.90` is a transcribed number in the
    one place it must not be.

    A report that cannot say which levels it ran at is **refused rather than
    defaulted** to the contract's, for `backtest_document`'s reason: a field
    that cannot be computed is absent, never assumed.

    Args:
        report: a report from `rolling_persistence_backtest`, or any report
            carrying forecasts and the quantile grid they were drawn at.
        seed: required, as the metric requires it. See `_report_seed`.
        block_length: mean block length. `None`, the default, measures it off
            the report's own folds via `_maximum_horizon_overlap`, exactly as
            `mae_bootstrap_interval` does.

    Returns:
        An `IntervalCalibration`.

    Raises:
        ValueError: if the report carries no forecasts, or fewer than two
            quantile levels, from which no declared probability can be formed.
    """

    forecasts = list(report.forecasts)
    if not forecasts:
        raise ValueError("a report with no forecasts has no coverage to calibrate")
    levels = tuple(report.quantile_levels)
    if len(levels) < 2:
        raise ValueError(
            f"the report declares {len(levels)} quantile level(s), so it states "
            "no interval and no probability for one to span; a calibration "
            "statement cannot be formed from it, and substituting the "
            "contract's grid would report a declaration the run did not make"
        )
    declared = levels[-1] - levels[0]
    block = (
        _maximum_horizon_overlap(report.folds)
        if block_length is None
        else int(block_length)
    )
    covered = _coverage_indicators(forecasts)

    lower, upper = stationary_bootstrap_interval(
        _coverage_statistic(covered),
        len(covered),
        block_length=block,
        seed=seed,
        replications=BOOTSTRAP_REPLICATIONS,
        level=BOOTSTRAP_LEVEL,
    )
    return IntervalCalibration(
        realized_coverage=sum(covered) / len(covered),
        declared_probability=declared,
        coverage_interval=(lower, upper),
        block_length=block,
        seed=seed,
        replications=BOOTSTRAP_REPLICATIONS,
        level=BOOTSTRAP_LEVEL,
        coverage_series=tuple(covered),
    )


#: How `_calibration_document` writes the coverage indicator series into a
#: record: `[value, length]` pairs in origin order, value first. Named once and
#: carried in the record beside the pairs, so a reader meets the encoding
#: stated rather than inferred from the data -- a list of two-element arrays is
#: also what a summarised series would look like, and the two must not be
#: guessable apart.
_COVERAGE_SERIES_ENCODING = "run_length"


def _coverage_indicators(forecasts: Sequence[Forecast]) -> List[float]:
    """The coverage indicator series: `1.0` where the actual fell in its interval.

    One value per scored origin, in origin order. Extracted from
    `interval_calibration` when `_calibration_document` needed the same series
    to publish, and extracted rather than duplicated for the reason the class
    docstring gives about the centre and the interval: two derivations of the
    series a record is asked to reproduce can agree today and drift later, and
    the record would then publish an arrangement that is not the one its
    endpoints came from.

    **The bounds are closed on both sides, deliberately.** That is the
    definition `rolling_persistence_backtest` computed the published
    `interval_coverage` under, so a strict indicator here would calibrate a
    different quantity than the one being calibrated. See
    `IntervalCalibrationTests`' mutation 6, which is the mutation that found
    this was unguarded.

    Floats, not bools: `stationary_bootstrap_interval` refuses a non-finite
    statistic and a mean over ints would still be a float, but the series is
    what a reader is being asked to believe is resampled, and `1.0`/`0.0` is
    the series the mean is of.
    """

    return [
        1.0 if item.lower_bps <= item.actual_bps <= item.upper_bps else 0.0
        for item in forecasts
    ]


#: The repository whose commit a record names. Resolved from this module's own
#: location rather than from the process's working directory: the commit a
#: record must identify is the one the *code that ran* was read from, and a
#: caller may invoke the CLI from anywhere.
_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

#: The suffix `data.write_daily_panel` appends to a panel path when it writes
#: the build manifest beside it. Named once, here, rather than spelled at the
#: one place that looks for the file, so that the reader and the writer can be
#: checked against each other by eye. It is a string and not an import:
#: `data.py` is Track A's, this module reads one JSON file, and that is the
#: whole dependency.
_BUILD_MANIFEST_SUFFIX = ".manifest.json"

#: The manifest fields a record can check against the panel it actually scored,
#: as `(manifest key, record key)`. Three of extent, and they are checked on
#: every manifest whether or not it also carries a digest: extent is the
#: cheaper claim and it is the one a partial rebuild breaks first. Both keys of
#: each pair are already computed -- the manifest claims one side and the
#: emitted `panel` object carries the other -- so the comparison derives
#: nothing new. See `_bind_build_manifest`.
_MANIFEST_EXTENT = (
    ("row_count", "row_count"),
    ("start_date", "first_date"),
    ("end_date", "last_date"),
)

#: The identity claim, as `(manifest key, record key)` like the extent pairs
#: above, and kept apart from them because it is **optional on the manifest
#: side**. `write_daily_panel` records a top-level `sha256` of the panel it
#: describes; a manifest written before it did carries none, and there is one
#: such manifest published in `docs/runs/`. Optional on the manifest, required
#: on the record: a manifest that claims a digest and a report that cannot
#: produce one to compare it against is a check that cannot be made, not a
#: check that passed.
_MANIFEST_DIGEST = ("sha256", "sha256")

#: What `panel.build_manifest_binding` says the binding was, and what it was
#: not. Stated in the artifact rather than left to a reader who finds a
#: manifest embedded beside a digest and assumes the two were checked against
#: each other.
_EXTENT_BINDING_NOTE = (
    "this manifest carries no digest of the panel it describes, so this binds "
    "it to the panel by extent and not by bytes: a manifest is a claim about a "
    "path, and the bytes under that path may have changed since it was written"
)

#: The same field when the manifest does carry a digest. Said in the artifact
#: for the same reason the sentence above is: the two bindings are different
#: strengths of evidence and a reader must not have to infer which one a
#: record was given from the presence of a key.
_DIGEST_BINDING_NOTE = (
    "this manifest carries a digest of the panel it describes and it is the "
    "digest of the bytes this run scored, so the manifest is bound to the "
    "panel by bytes; the extent is checked beside it and agrees"
)


def _file_identity(path: Path) -> dict:
    """A file this run read, as path and digest -- the shape `panel` uses.

    `REPRODUCIBILITY.md` asks a reportable record to identify "the
    source-registry and stress-threshold versions". Neither file carries a
    version field, and a digest is the version of a file that carries none: it
    changes exactly when the bytes change and it cannot be typed wrong. Path
    and digest come from one read, so the record cannot name one file and hash
    another -- the same reason the panel's own digest is taken here rather than
    handed in.
    """

    return {
        "path": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def _git_output(*arguments: str) -> str:
    """One `git` invocation at the repository root, as text."""

    completed = subprocess.run(
        ("git", *arguments),
        cwd=_REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return completed.stdout


def _code_provenance() -> Optional[dict]:
    """The commit the code was read from, and two facts about its tree.

    `REPRODUCIBILITY.md` asks first for "the Git commit". A commit id alone is
    not that answer: read from a modified working tree it names code that did
    not run, and it names it in the most convincing possible form. So the tree
    is checked in the same breath and the answer is carried whichever way it
    came out -- `tree_modified` is present and `False` on a clean tree, because
    a reader must be able to tell "checked, and clean" from "not checked", and
    an omitted field cannot say the first.

    That standard is about **code**, and until 9 September this function did not
    hold itself to it. `git status --porcelain` reports untracked files with
    `??`, and any output at all was read as a modified tree -- so a record
    written into `docs/runs/` made the *next* record report a modified tree, and
    only the first record produced in a clean checkout could ever report
    `False`. The two records published on 9 September say so: produced minutes
    apart from one commit with no code changed between them, they disagree,
    because by the time the second ran the first was sitting untracked beside
    it. A guard that fires on everything is a guard that fires on nothing, and
    the record that carries `tree_modified` because somebody really did run from
    an edited tree would have been drowned by its own siblings.

    So the question is split and both halves are kept:

      * `tree_modified` answers the code question and counts tracked
        modifications only -- `--untracked-files=no`.
      * `untracked_files_present` reports the rest, because untracked files are
        real and suppressing them would be a loosening rather than a scoping. A
        boolean, deliberately: a file list would put a developer's scratch
        filenames into a published record and would change size with the
        working directory.

    Both come from `git` and neither knows the name of any directory. A
    provenance field that special-cased `docs/runs/` would lie the first time a
    record was written somewhere else.

    Returns `None` when git is absent or the command fails, and the section is
    then absent from the record entirely, by the rule the rest of this document
    follows: a field this cannot compute is omitted rather than filled with a
    stand-in.
    """

    try:
        commit = _git_output("rev-parse", "HEAD").strip()
        status = _git_output("status", "--porcelain", "--untracked-files=no")
        untracked = _git_output("ls-files", "--others", "--exclude-standard")
    except (OSError, subprocess.SubprocessError):
        return None
    if not commit:
        return None
    return {
        "commit": commit,
        "tree_modified": bool(status.strip()),
        "untracked_files_present": bool(untracked.strip()),
    }


def _bind_build_manifest(panel: dict, manifest: dict) -> dict:
    """Check a build manifest against the panel that was scored, or refuse.

    A manifest records `"path": str(path)`, so a manifest found beside a panel
    is at minimum a claim about a *name*, and the bytes under that name may
    have changed since. Binding on the path alone is therefore no check at all:
    it is green on every well-formed input, including a manifest carried over
    from an entirely different build.

    **Two strengths of evidence, and the binding names which one it had.**

    Extent, always. `row_count`, `start_date` and `end_date` against the
    emitted panel's `row_count`, `first_date` and `last_date`. Neither side is
    a new derivation: the manifest claims one and the run that produced the
    record computed the other.

    Identity, when the manifest carries it. `write_daily_panel` now records a
    top-level `sha256` of the panel it describes -- the gap this function's
    docstring used to call Track A's to close, closed in their A6 -- and where
    it is present it is compared against the record's own `panel["sha256"]`,
    the digest of the bytes this run actually read. Extent is still checked
    beside it, so a digest binding is strictly the stronger of the two and
    never the narrower.

    The comparison is against the **record's** digest and not a fresh hash of
    the path. Re-hashing here would read the file a second time, and a binder
    whose two reads straddle a rewrite would compare a manifest against bytes
    that were never scored -- reintroducing, one level down, exactly the
    path-is-not-bytes decay this function exists to refuse.

    A manifest with no `sha256` binds by extent as before and the returned
    note says that is what happened, so a reader can tell a record that was
    checked by bytes from one that could not be.

    Returns:
        The `build_manifest_binding` object: `kind` -- `"digest"` when the
        digests were compared and `"extent"` when the manifest offered none --
        the record keys `compared`, and the `note` that says what was not
        checked.

    Raises:
        ProvenanceMismatchError: if any compared pair disagrees; if the
            manifest omits one of the extent fields or the record omits its
            counterpart; or if the manifest claims a digest and the record
            carries none to compare it against. A record that cannot bind a
            manifest it found must not publish it, and must not quietly drop
            it either.
    """

    compared = []
    for manifest_key, record_key in _MANIFEST_EXTENT:
        if manifest_key not in manifest:
            raise ProvenanceMismatchError(
                f"the build manifest beside {panel['path']} carries no "
                f"{manifest_key!r}, so the record cannot bind it to the panel "
                "it scored; a manifest that cannot be checked must not be "
                "published as provenance"
            )
        if record_key not in panel:
            raise ProvenanceMismatchError(
                f"a build manifest was found beside {panel['path']} but this "
                f"report does not carry the panel's {record_key!r}, so the "
                "manifest cannot be bound to what was scored; a manifest that "
                "cannot be checked must not be published as provenance"
            )
        claimed = manifest[manifest_key]
        scored = panel[record_key]
        if claimed != scored:
            raise ProvenanceMismatchError(
                f"the build manifest beside {panel['path']} describes a panel "
                f"with {manifest_key}={claimed!r}, but the panel this run "
                f"scored has {record_key}={scored!r}; the manifest does not "
                "describe the scored panel and publishing it would attribute "
                "these numbers to a build that did not produce them"
            )
        compared.append(record_key)

    manifest_key, record_key = _MANIFEST_DIGEST
    if manifest_key not in manifest:
        return {
            "kind": "extent",
            "compared": compared,
            "note": _EXTENT_BINDING_NOTE,
        }

    if record_key not in panel:
        raise ProvenanceMismatchError(
            f"the build manifest beside {panel['path']} carries a "
            f"{manifest_key!r} of the panel it describes, but this report does "
            f"not carry the scored panel's {record_key!r}, so the two digests "
            "cannot be compared; a manifest that cannot be checked must not be "
            "published as provenance"
        )
    claimed = manifest[manifest_key]
    scored = panel[record_key]
    if claimed != scored:
        raise ProvenanceMismatchError(
            f"the build manifest beside {panel['path']} describes a panel with "
            f"{manifest_key}={claimed!r}, but the panel this run scored has "
            f"{record_key}={scored!r}; the manifest describes different bytes "
            "and publishing it would attribute these numbers to a build that "
            "did not produce them"
        )
    compared.append(record_key)

    return {"kind": "digest", "compared": compared, "note": _DIGEST_BINDING_NOTE}


def _run_provenance(
    panel: dict,
    panel_path: Path,
    *,
    registry_path: Path,
    thresholds_path: Optional[Path],
) -> dict:
    """What produced the inputs, for both records, from one place.

    `REPRODUCIBILITY.md`'s "Requirements for a reportable experiment" lists
    eight things a run record must identify. `backtest_document` and
    `exceedance_backtest_document` between them already satisfy the feature set
    and decision cutoff, the model configuration and seed, and the
    rolling-origin split and registry-derived purge gap. Of the rest they
    carried the panel file's path and digest and nothing else: not the raw
    snapshots it was built from, not when those were retrieved, not which
    registry priced the gap, not which threshold file defined the exceedance,
    not the commit whose code produced any of it.

    None of that was unrecorded. `data.write_daily_panel` writes every built
    panel with a `<panel>.manifest.json` beside it, carrying the build cutoff,
    the decision time, the extent, the built and refused columns, the holes,
    `source_shas` -- the raw snapshot digests -- and, since Track A's A6, a
    top-level `sha256` of the panel itself. Nothing read it. A manifest nobody
    reads is a file, not a record, and this function is the line that crosses
    the gap.

    **One builder, two documents.** Both records grow the same section from
    here rather than each spelling it. Two evaluators now publish records, and
    a shape written out in each is a shape whose halves drift the first time
    one of them gains a field -- the reason `_validate_taus` and `_seed_from`
    were factored rather than copied.

    **The manifest is carried whole.** Parsed and embedded under
    `panel.build_manifest` exactly as it is: no field selected, none renamed,
    none re-derived. The manifest's schema is Track A's, and a record that
    re-typed it would be a second copy of a schema that is not this module's --
    the two agreeing today and drifting the moment a field is added there.
    Carrying it whole is also how this record gains every future field for
    free.

    **When there is no manifest the section is absent** -- not `null`, not an
    empty object, not a `"none"` string. A fixture panel has no build behind it
    and a record that says so by omission is honest; one that says so with a
    stand-in invites a reader to think the field was computed. That is the rule
    `backtest_document` already follows for `decision_time` and
    `minimum_history` and it does not change here.

    Args:
        panel: the record's `panel` object, already carrying path, digest and
            -- when the report knows them -- the extent. The digest is what a
            manifest's own `sha256` is bound against, which is why it is taken
            once by the caller and read here rather than recomputed.
            **Grown in place**
            with `build_manifest` and `build_manifest_binding` when a manifest
            is found, because a manifest describes the panel and belongs under
            it, while the code and the input digests describe the run.
        panel_path: the panel file as the caller named it. The manifest's name
            is derived from it rather than typed, so it follows the panel.
        registry_path: the source registry this run actually read.
        thresholds_path: the stress-threshold declaration this run actually
            read, or `None` on a path that reads none. The continuous benchmark
            takes no `--thresholds` and passing a stand-in for one it never
            opened would be exactly the invented field this record refuses
            elsewhere.

    Returns:
        The `provenance` section: the code the run was read from, and the
        digests of the declaration files it read.

    Raises:
        ProvenanceMismatchError: via `_bind_build_manifest`, when a manifest
            beside the panel does not describe the panel that was scored --
            by digest where the manifest carries one, by extent otherwise --
            or when it carries a claim this record has nothing to check
            against.
    """

    manifest_path = Path(str(panel_path) + _BUILD_MANIFEST_SUFFIX)
    if manifest_path.exists():
        # Parse and bind before either lands in the record. A malformed
        # manifest raises out of `json.loads` rather than being skipped: it is
        # a manifest that exists and cannot be read, which is a different fact
        # from there being none, and the CLI dispatcher already turns a
        # `ValueError` into a refusal with no artifact written.
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        binding = _bind_build_manifest(panel, manifest)
        panel["build_manifest"] = manifest
        panel["build_manifest_binding"] = binding

    inputs = {"source_registry": _file_identity(registry_path)}
    if thresholds_path is not None:
        inputs["stress_thresholds"] = _file_identity(thresholds_path)

    provenance: dict = {"inputs": inputs}
    code = _code_provenance()
    if code is not None:
        provenance["code"] = code
    return provenance


def _coverage_statistic(series: Sequence[float]) -> Callable[[Sequence[int]], float]:
    """The statistic `stationary_bootstrap_interval` resamples: the series mean.

    A factory rather than two closures, because `interval_calibration` builds
    this from a run's forecasts and `calibration_from_document` builds it from a
    published record, and the whole point of the second is that it reproduces
    the first *to the endpoint*. Two textually identical closures reproduce each
    other until one is touched; one function cannot come apart from itself.
    """

    def coverage(indices: Sequence[int]) -> float:
        return sum(series[i] for i in indices) / len(indices)

    return coverage


def _encode_indicator_runs(series: Sequence[float]) -> List[List[int]]:
    """A 0/1 series as `[value, length]` pairs in origin order.

    **Run-length and not one entry per origin, and the cost is stated rather
    than assumed.** The series is one bit per scored origin -- 2080 of them for
    the published persistence run -- and three shapes were available: the raw
    list, these pairs, or a summary. A summary is refused by the criterion this
    encoding exists to satisfy: the mean and the length do not determine the
    series, so a record carrying them cannot be resampled and a record that
    said it could would make a stronger claim than the current one and be no
    more true.

    Between the other two, the pairs win on the thing a calibration statement is
    *about*, and **not** on size. A raw list of 2080 zeros and ones is a wall a
    reader scrolls past; the pairs show, in the JSON, runs of covered origins
    broken by bursts of failures -- which is the clustering, the property that
    makes this interval wider than a binomial one, and the property the
    bracketing finding could previously only reason about from outside.

    **The size argument is weaker than it looks and the measurement is here
    rather than an assurance.** At 2080 origins and 395 failures, the raw list
    is 6,240 bytes of JSON and these pairs are:

        one contiguous block of failures        3 runs         30 bytes
        forty clustered bursts                 81 runs        690 bytes
        uniformly random positions            642 runs      5,185 bytes
        failures evenly spread as singletons   790 runs      6,322 bytes
        alternating at every origin          2,080 runs     16,640 bytes

    So it is a large win on a clustered series, a small one on a random series,
    and a *loss* on the last two -- the second of which is 2.7x the raw list.
    That case is a coverage series with no clustering whatever, which is not
    what a horizon-overlapping benchmark produces, but it is not ruled out and
    the encoding is chosen with it in view: the bound is `2 * n` integers, about
    16 KB at 2080 origins, against the 1.5 MB the exceedance record already
    spends on reliability curves. The shape is bounded by measurement, not small
    by assumption. `CalibrationDocumentTests` holds the bound as an assertion.

    Raises:
        ValueError: on any value that is not `0.0` or `1.0`. The encoding is
            defined on an indicator series and silently rounding anything else
            would publish an arrangement the run did not produce.
    """

    runs: List[List[int]] = []
    for position, value in enumerate(series):
        if value not in (0.0, 1.0):
            raise ValueError(
                f"the coverage indicator at origin {position} is {value!r}, and "
                "a run-length encoding is defined on an indicator series; a "
                "record built from anything else would publish an arrangement "
                "the run did not produce"
            )
        bit = int(value)
        if runs and runs[-1][0] == bit:
            runs[-1][1] += 1
        else:
            runs.append([bit, 1])
    return runs


def _decode_indicator_runs(runs: Sequence[Sequence[int]], length: int) -> List[float]:
    """`[value, length]` pairs back to the 0/1 series, checked against `length`.

    The declared length is redundant with the pairs -- they sum to it -- and it
    is carried and compared for exactly that reason: a truncated or hand-edited
    `runs` array decodes into a shorter series perfectly happily, and a shorter
    series resamples to a different interval with no sign that anything is
    wrong. Redundancy that is checked is a guard; redundancy that is not is a
    second place to be wrong.

    Raises:
        ValueError: on a malformed pair, a non-positive run length, a value
            other than 0 or 1, an empty series, or a total that disagrees with
            `length`.
    """

    series: List[float] = []
    for position, run in enumerate(runs):
        pair = tuple(run)
        if len(pair) != 2:
            raise ValueError(
                f"run {position} carries {len(pair)} value(s); a run-length pair "
                "is [value, length]"
            )
        bit, count = pair
        if bit not in (0, 1):
            raise ValueError(f"run {position} carries value {bit!r}, not 0 or 1")
        if not isinstance(count, int) or count < 1:
            raise ValueError(
                f"run {position} declares length {count!r}; a run spans at least "
                "one origin"
            )
        series.extend([float(bit)] * count)
    if not series:
        raise ValueError(
            "the record encodes an empty coverage series, so it states no "
            "arrangement for an interval to be a resample of"
        )
    if len(series) != length:
        raise ValueError(
            f"the record's runs decode to {len(series)} origins and it declares "
            f"{length}; one of the two has been edited and the interval is a "
            "resample of neither"
        )
    return series


def _calibration_document(calibration: IntervalCalibration) -> dict:
    """A calibration statement a reader can recompute, not merely read.

    **The six-field version is the trap and it is already disproved.** A record
    carrying `realized_coverage`, `declared_probability`, `block_length`,
    `seed`, `replications` and the fold count is exactly what
    `docs/runs/persistence_funding.json` carries today plus labels, and
    `IntervalCalibrationTests` recorded why that is not reproducible: the
    interval is a resample of the indicator *series*, the mean and the length do
    not determine the series, and the arrangement is the clustering the
    statement is about. So the series is here, run-length encoded -- see
    `_encode_indicator_runs` for the shape and its cost -- and
    `calibration_from_document` resamples it back.

    `coverage_interval` is published beside the series and is never an input to
    that reader. The record states the endpoints so a human can read them, and
    the reader derives them again from the series so that agreeing is a fact
    rather than a definition.
    """

    lower, upper = calibration.coverage_interval
    return {
        "realized_coverage": calibration.realized_coverage,
        "declared_probability": calibration.declared_probability,
        "coverage_interval": {
            "lower": lower,
            "upper": upper,
            "level": calibration.level,
            "method": "stationary_bootstrap",
            "block_length": calibration.block_length,
            "replications": calibration.replications,
            "seed": calibration.seed,
        },
        "coverage_series": {
            "encoding": _COVERAGE_SERIES_ENCODING,
            "length": len(calibration.coverage_series),
            "runs": _encode_indicator_runs(calibration.coverage_series),
        },
    }


def _required(container: Mapping[str, Any], key: str, where: str) -> Any:
    """One field of a record, or a `ValueError` naming what is missing and where.

    A record is read by whoever holds the file, often long after the run, and
    `KeyError: 'runs'` does not tell them which object was short of it.
    """

    if key not in container:
        raise ValueError(
            f"the record's {where} carries no {key!r}, so no calibration "
            "statement can be recomputed from it"
        )
    return container[key]


def calibration_from_document(document: Mapping[str, Any]) -> IntervalCalibration:
    """Recompute a run's coverage calibration from its published record alone.

    The inverse of `_calibration_document`, and the reason that function
    publishes a series. No report, no panel and no forecasts are in scope: the
    only input is a `dict` parsed from a `docs/runs/*.json` file, and what comes
    back is the same `IntervalCalibration` the run produced -- the same centre,
    the same endpoints, the same resample structure.

    **What is recomputed and what is read.** `realized_coverage` and
    `coverage_interval` are *recomputed*, from the decoded series, at the
    resample parameters the record declares. The record's own `coverage_interval`
    is deliberately not read: a reader that returned the stated endpoints would
    make this function a field census dressed as a round trip, and the
    criterion is that the record *reproduces* its statement.
    `declared_probability` is read, because it is a declaration a run made and
    not a quantity a series determines -- see `interval_calibration`, which
    refuses to substitute the contract's grid for the same reason.

    Args:
        document: a record as `backtest_document` shaped it, parsed from JSON.

    Returns:
        An `IntervalCalibration` equal to the run's own, at the same seed.

    Raises:
        ValueError: if the record carries no calibration statement, states an
            encoding this does not implement, or encodes a series that
            disagrees with the length it declares. A record that cannot be
            resampled is refused rather than answered from its summary fields:
            an interval returned from a mean and a length would be a number
            nobody computed, which is the decay this whole document exists to
            refuse.
    """

    metrics = _required(document, "metrics", "top level")
    statement = _required(metrics, "interval_calibration", "metrics")
    series_object = _required(statement, "coverage_series", "interval_calibration")
    interval = _required(statement, "coverage_interval", "interval_calibration")

    encoding = _required(series_object, "encoding", "coverage_series")
    if encoding != _COVERAGE_SERIES_ENCODING:
        raise ValueError(
            f"the record encodes its coverage series as {encoding!r}; this "
            f"reader implements {_COVERAGE_SERIES_ENCODING!r} and will not "
            "guess at another encoding of a series an interval depends on"
        )
    series = _decode_indicator_runs(
        _required(series_object, "runs", "coverage_series"),
        _required(series_object, "length", "coverage_series"),
    )

    block_length = _required(interval, "block_length", "coverage_interval")
    seed = _required(interval, "seed", "coverage_interval")
    replications = _required(interval, "replications", "coverage_interval")
    level = _required(interval, "level", "coverage_interval")

    lower, upper = stationary_bootstrap_interval(
        _coverage_statistic(series),
        len(series),
        block_length=block_length,
        seed=seed,
        replications=replications,
        level=level,
    )
    return IntervalCalibration(
        realized_coverage=sum(series) / len(series),
        declared_probability=_required(
            statement, "declared_probability", "interval_calibration"
        ),
        coverage_interval=(lower, upper),
        block_length=block_length,
        seed=seed,
        replications=replications,
        level=level,
        coverage_series=tuple(series),
    )


def backtest_document(
    report: BacktestReport, *, panel_path: Path, registry_path: Path, model: str
) -> dict:
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

    * `declaration` -- the model, the feature set, the decision time, the
      minimum history. The two things the caller chose, plus the two settings
      that shape what follows from them. Everything else in the run is a
      consequence of these. `model` is the name the caller selected and never a
      re-derivation from `report.model`: this function is handed a fitted
      object, several fitters produce the same class, and a name reconstructed
      from one would agree with the request only for as long as that mapping
      stayed a bijection. It is the field a reader compares two artifacts by,
      and until `backtest` grew `--model` there was only one model to name, so
      the document did not carry it -- which is why the sibling record's
      docstring says this path "reports none".
    * `derived` -- the `(source, field)` pairs the features resolved to, the
      sources projected from them, and the gap those fields produced. Never
      supplied and never re-derived here: read off the report, because a
      document that recomputed them would be a second derivation of the number
      that shaped the run, and the two can agree today and drift later. The
      fields are here because the gap is priced per field: a reader given only
      `fred_macro_latest_vintage` cannot tell which of its eight fields the
      number came from, and on that source the answer differs by field.
    * `panel` -- path, `sha256`, row count, first and last date. The path says
      which file was named and the digest says which bytes answered to that
      name; a report carrying only the path is a claim about a file that may
      since have changed, which is the same decay as a typed number. The extent
      says what was actually scored, since a digest identifies a file and not a
      run. `build_manifest` is the build behind those bytes when there is one:
      see `_run_provenance`, which is where both records grow it.
    * `provenance` -- the commit the code was read from and whether that tree
      was modified, and the digest of every declaration file the run opened.
      `REPRODUCIBILITY.md` requires both of a reportable result and this
      document carried neither.
    * `folds` -- the count, and the first and last origin in full. Enough for a
      reader to check the gap against a calendar on the two folds where an
      off-by-one would show, without the artifact growing with the panel.
    * `metrics` -- the numbers, unrounded. Rounding belongs to whoever displays
      them; an artifact that rounded would publish a figure nobody computed and
      would make two runs that genuinely differ look identical.
      `interval_calibration` is the one field here that carries more than a
      number: it relates the realized coverage to the probability the run
      declared, and it carries the indicator series that relation's interval is
      a resample of, so the statement can be recomputed from this file with no
      panel and no forecasts. See `_calibration_document` for the shape and
      `calibration_from_document` for the reader that closes the loop. It is
      absent from a run that declared no quantile grid, by the rule above.

    What is deliberately *not* here: any aggregate over event windows (those
    are the event path's and the contract forbids aggregating a single window),
    and any per-forecast dump. The second is a real omission and worth the
    note: the pinball losses cannot be recomputed from this file alone. They
    can be recomputed from the panel, which the file identifies by digest,
    which is what makes the digest load-bearing rather than decorative.

    **The interval on coverage is the exception, and it is a narrow one.** It
    is recomputable from the file because the record carries the coverage
    indicator series -- one bit per origin, run-length encoded -- and one bit
    per origin is not a forecast row. `PairedComparisonTests` records keeping
    intermediates off a publication as a deliberate decision and that decision
    stands: nothing here publishes a prediction, a quantile or an actual. What
    is published is whether each origin's actual fell inside its own interval,
    which is the whole of what a coverage statement is over.

    Args:
        report: a report from `rolling_persistence_backtest`.
        panel_path: the panel file as the caller named it. Read here, once, for
            its bytes -- the digest and the path come from the same read, so
            the artifact cannot name one file and hash another.
        registry_path: the source registry the run actually read. Required and
            undefaulted, for the reason `--model` has no default: a default
            here is a run that meant to publish a reportable record and
            published one missing its provenance, with every other field
            correct.
        model: what to record as having produced these numbers -- the name the
            caller selected, not a re-derivation. Required and undefaulted by
            the same argument, and here it is the sharpest instance of it: the
            default a convenience would pick is `persistence`, and persistence
            is the benchmark `PLAN.md`'s Phase 2 exit criterion asks every
            other model to beat. A run meaning to publish an ARX would publish
            the baseline's numbers under the ARX's name in a record whose every
            other field is correct.

    Returns:
        A JSON-serialisable dict. The caller writes it; this shapes it.

    Raises:
        ValueError: when `model` is not a non-empty string.
        ProvenanceMismatchError: when a build manifest beside the panel does
            not describe the panel that was scored.
    """

    # Before the panel is read and before anything is resampled, so a record
    # that could not say what produced it leaves no file behind. The same
    # refusal, with the same reasoning, as `rolling_exceedance_backtest`'s on
    # `model_name`.
    if not isinstance(model, str) or not model:
        raise ValueError(
            f"model must be a non-empty string, got {model!r}; an artifact that "
            "cannot say which model produced it cannot be compared to one that "
            "can"
        )

    digest = hashlib.sha256(panel_path.read_bytes()).hexdigest()
    seed = _report_seed(report, digest)
    lower, upper, block = mae_bootstrap_interval(report, seed=seed)

    declaration: dict = {"model": model, "features": sorted(report.features)}
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

    # After the extent, because the binding compares against it, and before
    # anything is returned, because a manifest that does not describe this
    # panel must leave no document behind to be written.
    provenance = _run_provenance(
        panel, panel_path, registry_path=registry_path, thresholds_path=None
    )

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
    # The calibration statement, and it is omitted rather than defaulted when
    # the run cannot state one: `interval_calibration` refuses a report with no
    # forecasts and a report that declares fewer than two quantile levels,
    # because the probability a calibration is against is the run's declaration
    # and not this checkout's grid. That refusal is the right one and it must
    # not become this function's, so the condition is asked here -- an absent
    # field makes a reader ask and a defaulted one makes them believe.
    #
    # The block length is handed in rather than measured again. It is the same
    # `_maximum_horizon_overlap` over the same folds either way, and one
    # measurement means the record cannot state two different block lengths for
    # two intervals over one run's origins.
    if report.forecasts and len(report.quantile_levels) > 1:
        metrics["interval_calibration"] = _calibration_document(
            interval_calibration(report, seed=seed, block_length=block)
        )
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
            # The pairs the gap was sized over, as `source.field` strings. A
            # report that named only the sources would be a report an auditor
            # cannot check: two fields of one source can carry different lags,
            # and one of them can be refused while the other prices. JSON has
            # no tuple, and a two-element array per pair reads worse in a diff
            # than the dotted form the registry's own refusal already uses.
            "fields": [f"{source}.{field}" for source, field in sorted(report.field_sources)],
            "purge_days": report.purge_days,
        },
        "panel": panel,
        "provenance": provenance,
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


# --------------------------------------------------------------------------
# Comparison: two models at the same origins, one resample, one difference
# --------------------------------------------------------------------------

#: The loss the paired difference is taken over by default, named once and
#: published in the record. Absolute error per scored origin, so its mean over
#: the origins is exactly `BacktestReport.mae_bps` for each side -- which is the
#: quantity `PLAN.md`'s Phase 2 exit criterion phrases *"beats persistence out
#: of sample"* on, and the one `mae_bootstrap_interval` already puts an interval
#: around for a single model.
COMPARISON_LOSS = "absolute_error_bps"

#: The distributional loss, published under the name `BacktestReport` already
#: reports the same metric under. One spelling for one metric: `backtest` and
#: `compare` must not be able to disagree about what CRPS is, and the way they
#: are made unable to is that both of them call `metrics.crps_from_quantiles`
#: on the contract's fixed grid and both of them label the result `crps_bps`.
CRPS_COMPARISON_LOSS = "crps_bps"


def _absolute_error_at(
    fitted: FittedForecastModel, feature_row: DailyObservation, actual: float
) -> float:
    """One origin's absolute error, from the model's own point rule.

    The loss `paired_model_comparison` has always taken, moved behind the
    selector unchanged so that the default path is the same arithmetic in the
    same order and every record already published keeps its numbers.
    """

    return abs(actual - fitted.point_forecast(feature_row))


def _crps_at(
    fitted: FittedForecastModel, feature_row: DailyObservation, actual: float
) -> float:
    """One origin's CRPS, from the model's own **quantile vector**.

    `fitted.predict`, not `fitted.point_forecast`. A point mass's CRPS is
    exactly its absolute error -- `2 * mean pinball` over any grid collapses to
    `|actual - point|` when every level predicts the same number -- so a CRPS
    path handed a degenerate vector returns the absolute-error series again and
    reports a difference of zero between two models whose laws differ. That
    failure is indistinguishable from a correct implementation finding no
    difference, which is why it is the mutation recorded against
    `PairedComparisonTests`.

    The grid is read off the model that produced the vector and then checked
    against the declaration, exactly as `rolling_persistence_backtest` reads and
    checks it: a label taken from anywhere but the thing it labels can be wrong
    while looking right, and a model quantiling at a private grid would publish
    a loss under a heading it does not belong to.
    """

    levels = tuple(fitted.levels)
    if levels != tuple(QUANTILE_LEVELS):
        raise ValueError(
            f"the fitted model reports quantile levels {levels}, but the "
            f"contract fixes them at {tuple(QUANTILE_LEVELS)}; a CRPS at a "
            "private grid is not comparable across models and the paired "
            "difference between two such grids is not a difference at all"
        )
    return crps_from_quantiles(levels, fitted.predict(feature_row), actual)


class _ComparisonLoss(NamedTuple):
    """What one selectable paired loss is: a name, a heading, and a scorer.

    Three facts about one loss held in one place, because they are three things
    a record has to agree with itself about. `name` is what the record's `loss`
    field and its sign convention say; `statistic` is the heading each side's
    mean is published under -- `mae_bps` for the absolute error, `crps_bps` for
    the CRPS -- and `at_origin` is what actually scored it. Split across
    parallel dicts these could drift into a record whose stated loss and whose
    published mean were two different quantities, each internally correct.
    """

    name: str
    statistic: str
    at_origin: Callable[[FittedForecastModel, DailyObservation, float], float]


#: The selectable paired losses, keyed by what the caller and `--loss` spell.
#:
#: **Absolute error is the default and stays the default.** Every published
#: `compare` command and every record under `docs/runs/` was produced without
#: this argument existing, and a default that moved would silently restate what
#: those records mean rather than adding to what a new one can say.
#:
#: **Why CRPS is the second entry and coverage is not.** Coverage is not a
#: loss: an interval from minus infinity to plus infinity covers every origin,
#: so a paired coverage difference rewards the model that says least. CRPS is
#: proper, it reads the whole predictive law rather than its centre, and it
#: reduces to absolute error for a point mass -- so the two entries here are
#: the same functional evaluated on progressively more of the forecast, not two
#: unrelated numbers. Pinball at one declared level and the interval score are
#: defensible additions and are not in this dict yet.
COMPARISON_LOSSES: Mapping[str, _ComparisonLoss] = MappingProxyType(
    {
        "absolute-error": _ComparisonLoss(
            COMPARISON_LOSS, "mae", _absolute_error_at
        ),
        "crps": _ComparisonLoss(CRPS_COMPARISON_LOSS, "crps", _crps_at),
    }
)

#: The loss a comparison takes when the caller does not choose one. See above:
#: this value is load-bearing for every record already published.
DEFAULT_COMPARISON_LOSS = "absolute-error"


def _select_comparison_loss(loss: str) -> _ComparisonLoss:
    """The named loss, or a refusal naming what is available.

    Refused rather than defaulted. A comparison asked for a loss this module
    does not implement and given the absolute error instead would publish a
    record whose `loss` field is correct and whose numbers answer a question
    nobody asked.
    """

    try:
        return COMPARISON_LOSSES[loss]
    except KeyError:
        raise ValueError(
            f"unknown paired loss {loss!r}; this module implements "
            + ", ".join(repr(name) for name in sorted(COMPARISON_LOSSES))
        ) from None


def _sign_convention(model_a: str, model_b: str, loss_name: str) -> str:
    """Which model is subtracted from which, as a sentence naming both.

    A signed difference with no statement of direction is a number a reader
    gets backwards half the time, and the half that reads it backwards reads it
    as the opposite conclusion. So the convention is rendered from the two
    names the run was given and carried in the artifact, not only in a
    docstring -- a docstring is not shipped with the record and the record is
    what a later reader has.

    Rendered with the `model_a=` / `model_b=` labels rather than with the bare
    names, so the sentence stays unambiguous when a run compares two models
    that happen to share a name -- which is the climatology-against-itself
    sanity check, on this path, and a run worth being able to make.

    `loss_name` is the third thing the sentence has to say, and it is passed in
    rather than read off `COMPARISON_LOSS` because the loss is now selectable.
    A difference is a difference *of something*: two records reporting `-1.38`
    under one convention sentence, one of them a gap in absolute error and the
    other a gap in CRPS, would be two incomparable numbers that a reader has no
    way to tell apart. Required and undefaulted for that reason -- a defaulted
    name here would label a CRPS comparison as an absolute-error one on the
    single path where nobody would look.
    """

    return (
        f"difference = {loss_name}(model_a={model_a}) - "
        f"{loss_name}(model_b={model_b}) at each scored origin; a "
        f"positive mean difference means model_a={model_a} carried the larger "
        f"loss over these origins, so model_b={model_b} was the more accurate "
        "of the two on them"
    )


@dataclass(frozen=True)
class PairedComparisonReport:
    """Two models scored at one set of origins, and the interval on their gap.

    **Every field is required.** `BacktestReport` defaults most of its fields
    because tests construct one by hand to exercise a reporter, and a report
    that cannot say what it ran under must not claim a default. Nothing
    constructs this by hand: it exists only as `paired_model_comparison`'s
    return value, every field is computed in the run that emits it, and an
    optional field here would be a place a comparison could quietly fail to say
    which models it compared.

    `losses_a`, `losses_b` and `differences` are carried at per-origin
    granularity, positionally aligned with `folds`, because the pairing is the
    property the whole block exists for and a reader of the *object* has to be
    able to check it. They are deliberately **not** published: see
    `paired_comparison_document`.
    """

    #: The names the caller selected, in the order the sign convention reads.
    model_a: str
    model_b: str
    #: Each model's own declared feature set. Two declarations, not one: the
    #: models being compared are usually declared over different columns -- an
    #: ARX reads regressors persistence does not -- and forcing one declaration
    #: would either over-purge the simpler model or leave the richer one's
    #: columns unpriced.
    features_a: Tuple[str, ...]
    features_b: Tuple[str, ...]
    #: What each declaration resolved to, read off `_derive_purge` rather than
    #: re-resolved by whoever prints them, for the reason `BacktestReport`
    #: carries the same pair.
    sources_a: Tuple[str, ...]
    sources_b: Tuple[str, ...]
    field_sources_a: Tuple[Tuple[str, str], ...]
    field_sources_b: Tuple[Tuple[str, str], ...]
    #: The gap both declarations produced. One number, because a comparison in
    #: which they differed is refused before the folds are built -- see
    #: `IncomparablePurgeError`.
    purge_days: int
    #: Which paired loss was taken, as the caller spelled it -- a key of
    #: `COMPARISON_LOSSES`, not the published name. `loss_name` and
    #: `loss_statistic` below render the two published spellings from it, so
    #: the record has one source for what it scored rather than three fields
    #: that can disagree.
    loss: str
    #: One loss per scored origin, per model, and their difference. Aligned
    #: with `folds` by construction: they are appended inside one loop. Under
    #: `loss`, whichever that is: these are absolute errors on the default path
    #: and per-origin CRPS on the other, and nothing here is specific to
    #: either.
    losses_a: Tuple[float, ...]
    losses_b: Tuple[float, ...]
    differences: Tuple[float, ...]
    #: The statistic, and each side's own mean loss beside it. The two means
    #: are reported because a difference without its levels is a number a
    #: reader cannot place -- half a basis point between two models at four is
    #: not half a basis point between two models at forty.
    #:
    #: Named `mean_loss_*` and not `mae_*`: under `--loss crps` these are mean
    #: CRPS, and a field called `mae` carrying a CRPS is a number that reads
    #: correctly and means something else. On the default path the value is
    #: unchanged and is still exactly `BacktestReport.mae_bps` for that side.
    mean_difference_bps: float
    mean_loss_a_bps: float
    mean_loss_b_bps: float
    #: The interval on `mean_difference_bps`, and the resample structure that
    #: produced it. The block length is carried beside the endpoints because an
    #: interval whose resample structure is unstated cannot be reproduced, and
    #: this one is measured off the run's own fold horizons rather than
    #: declared.
    difference_interval: Tuple[float, float]
    block_length: int
    seed: int
    replications: int
    level: float
    #: The sentence `_sign_convention` rendered, held here so the console and
    #: the artifact read one string rather than each composing their own.
    sign_convention: str
    #: The origins, earliest first, one per entry of `differences`. One
    #: sequence and not two: both models were scored on these.
    folds: Tuple[ScoredFold, ...]
    decision_time: time
    minimum_history: int
    panel_rows: int
    panel_first_date: date
    panel_last_date: date

    @property
    def loss_name(self) -> str:
        """The published name of the loss: what `loss` means to a reader.

        Derived rather than stored, so the record's `loss` field, its sign
        convention sentence and the heading its two means are published under
        cannot come apart -- they are three renderings of one selection.
        """

        return COMPARISON_LOSSES[self.loss].name

    @property
    def loss_statistic(self) -> str:
        """The heading each side's mean loss is published under.

        `mae` for the absolute error, `crps` for CRPS. The document and the
        console each append their own suffix; both read this.
        """

        return COMPARISON_LOSSES[self.loss].statistic


def paired_model_comparison(
    observations: Iterable[DailyObservation],
    *,
    model_a: str,
    fit_a: ModelFitter,
    features_a: Sequence[str],
    model_b: str,
    fit_b: ModelFitter,
    features_b: Sequence[str],
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    seed: int,
    minimum_history: int = 20,
    loss: str = DEFAULT_COMPARISON_LOSS,
) -> PairedComparisonReport:
    """Score two continuous models at the same origins and interval the gap.

    `PLAN.md` Phase 2 exits on *"a model that beats persistence out of
    sample"*. That is a comparison, and until this function the repository had
    no way to make one: `mae_bootstrap_interval` names the hazard in its own
    docstring -- a single MAE "invites a reader to believe that a difference
    between two models is real" -- and what a reader does with two of those is
    check whether the intervals overlap, which answers a different question and
    answers it wrongly in both directions. Overlapping intervals routinely
    contain a real difference, and separated ones can be produced by a shared
    shock that cancels in the difference.

    The quantity is the **paired per-origin difference**, and the interval
    comes from resampling origins once and applying that one draw to both
    models. The exceedance path already has this property --
    `brier_skill_score` is a ratio against a reference refitted on each fold,
    and its bootstrap applies one index draw to the model and the reference
    together -- and this is the continuous path's version of it.

    **The pairing is by construction, and that is the design.** One run, one
    fold loop, both models fitted on each fold's training rows and scored on
    that fold's origin. The two loss series are then the same length, in the
    same order, over the same days, and nothing has to be checked afterwards
    because nothing could have differed. Two existing report files cannot be
    made to yield this: they carry metrics rather than per-origin losses, and
    deliberately so.

    **The one thing the loop does not settle is the gap**, because the gap is
    derived from each declaration before any fold exists. Two declarations that
    price different gaps do not share an origin set at all, so they are refused
    here rather than reconciled -- see `IncomparablePurgeError`.

    **There is no second bootstrap.** `metrics.stationary_bootstrap_interval`
    is the one this project has, per the contract, and the statistic handed to
    it indexes the *difference* series. Bootstrapping the two models separately
    and differencing endpoints is the defect the acceptance test in
    `tests/test_baseline.py::PairedComparisonTests` is shaped to catch.

    **`mae_bootstrap_interval` is untouched.** The single-model interval keeps
    exactly the meaning it has; this stands beside it.

    **The loss is selectable, because a point loss cannot see a law.** The
    first thing this function was asked to score was persistence against the
    trailing-window residual law, which is persistence's point rule with a
    different predictive distribution around it. Under absolute error the two
    are the same model: every paired difference is exactly `0.0` and the
    interval is `[0.0, 0.0]`, which is not a null result but a blind
    instrument -- `backtest` already tells them apart, because its `crps_bps`
    reads the whole law. So `--loss crps` scores each side's **quantile
    vector** through `metrics.crps_from_quantiles` on the contract's fixed
    grid, which is the same call `rolling_persistence_backtest` makes, so the
    two commands cannot disagree about what CRPS is.

    Coverage would have been the other candidate and is not a loss: an interval
    from minus infinity to plus infinity covers every origin, so a paired
    coverage difference is maximised by the model that says least. See
    `COMPARISON_LOSSES`.

    **Everything else is loss-agnostic.** One fold loop, one resample draw
    through one differenced series, one gap refusal. The loss decides what
    number each origin contributes and nothing else, which is why the seed does
    not carry it: the resample is a draw of *origins*, the origins are the same
    under either loss, and two records over the same origins sharing one draw
    is a property rather than a collision.

    Args:
        observations: the panel, ascending by date.
        model_a: the name recorded for the first model. Required and
            undefaulted for the reason `backtest_document`'s `model` is: a
            comparison whose sides cannot be named is a signed number with
            nothing to attach either end of it to.
        fit_a: the first model's fitting call, `(train_frame,
            minimum_history=...) -> fitted model`.
        features_a: the first model's declared feature set, which sizes its
            gap. Required, keyword-only and undefaulted for the reason
            `rolling_persistence_backtest`'s is.
        model_b, fit_b, features_b: the same three for the second model. The
            subtraction runs a minus b; see `_sign_convention`.
        registry: the parsed source registry, for `max_release_lag_days`. One
            registry, because a comparison priced by two registries is a
            comparison of two runs again.
        decision_time: when the forecast is made. One value, for the same
            reason: the gap is a function of it, and two decision times are two
            different runs.
        seed: required, as `stationary_bootstrap_interval` requires it and for
            the same reason -- an interval that cannot be reproduced cannot be
            checked. `comparison_seed` derives one from the run's identity;
            a literal here would make every comparison in the project draw the
            same resample sequence regardless of what it scored.
        minimum_history: the first origin scored and the shortest training
            frame either fit is allowed. One value, so the two models see the
            same rows.
        loss: which paired loss to take, a key of `COMPARISON_LOSSES`.
            Defaults to `DEFAULT_COMPARISON_LOSS`, the absolute error, so every
            caller written before this argument existed and every record under
            `docs/runs/` keeps its numbers and its meaning.

    Returns:
        A `PairedComparisonReport`.

    Raises:
        IncomparablePurgeError: the two declarations derived different gaps, so
            there is no shared origin set to pair on.
        ValueError: the panel is too short for `minimum_history`, `loss` names
            a loss this module does not implement, or -- under `crps` -- a
            fitted model reports a quantile grid other than the declared one.
        SplitError: as `rolling_origin` raises -- a panel whose dates repeat or
            go backwards, or a gap that leaves no origin with `minimum_history`
            training rows behind it.
        LookAheadError: a fold's feature row does not clear the gap, or either
            fitted model reads a column outside its own declaration. The second
            is checked per side, against that side's declaration, because each
            side's gap was sized from its own.
        UndeclaredFeatureError: either declaration names a column
            `contract.field_sources_for_features` cannot classify.
        RegistryContractError: either declaration's fields cannot support a
            safe bound. Track A's refusal, with Track A's message.
    """

    # Before the gap derivation and before the panel, for the same reason the
    # gap refusal comes first: a run that names a loss this module cannot take
    # must not fit anything.
    selected = _select_comparison_loss(loss)

    declared_a: Tuple[str, ...] = tuple(features_a)
    declared_b: Tuple[str, ...] = tuple(features_b)

    # Before the panel is walked and before a single fold: two declarations
    # that price different gaps have no shared origin set, so there is nothing
    # for the rest of this function to pair.
    field_sources_a, sources_a, purge_a = _derive_purge(
        registry, declared_a, decision_time=decision_time
    )
    field_sources_b, sources_b, purge_b = _derive_purge(
        registry, declared_b, decision_time=decision_time
    )
    if purge_a != purge_b:
        raise IncomparablePurgeError(
            f"model_a={model_a} declares {list(declared_a)}, which prices a "
            f"{purge_a}-day purge gap, and model_b={model_b} declares "
            f"{list(declared_b)}, which prices a {purge_b}-day gap. The gap "
            "builds the folds, so these two models would be scored at "
            "different origins and their losses are not paired -- the "
            "difference between them would be a difference between two runs, "
            "which is what this function exists instead of. Declare feature "
            "sets that price the same gap, or run them as two backtests and "
            "report them as two backtests"
        )
    purge = purge_a

    rows = list(observations)
    if len(rows) <= minimum_history:
        raise ValueError("not enough observations for requested minimum history")

    dates = [row.date for row in rows]
    folds: List[ScoredFold] = []
    losses_a: List[float] = []
    losses_b: List[float] = []
    differences: List[float] = []
    checked = False

    # `step=1`, the origin-by-origin shape `rolling_persistence_backtest` has,
    # and one loop rather than two calls to it: the whole property this
    # function delivers is that the two models were scored on the same days, in
    # the same order, and a second call could only be checked for that
    # afterwards rather than made to hold.
    for train_indices, test_indices in rolling_origin(
        dates, minimum_history, 1, purge
    ):
        index = test_indices[0]
        train_frame = [rows[i] for i in train_indices]
        fitted_a = fit_a(train_frame, minimum_history=minimum_history)
        fitted_b = fit_b(train_frame, minimum_history=minimum_history)
        if not checked:
            # After the first fit and only the first, as the single-model path
            # does, and once per side against that side's own declaration: the
            # gap each model was purged under was sized from its own features,
            # so checking either against the other's would be checking the
            # wrong claim.
            _check_fitter_stayed_inside(
                fitted_a.features_read, declared_a, sources_a, purge
            )
            _check_fitter_stayed_inside(
                fitted_b.features_read, declared_b, sources_b, purge
            )
            checked = True

        feature_row = rows[_feature_index(dates, train_indices, index, purge)]
        actual = rows[index].spread_bps
        # The selected loss, applied to each side's own fitted model. Both
        # sides go through the same callable, so a loss that read one model
        # differently from the other is not expressible here.
        loss_a = selected.at_origin(fitted_a, feature_row, actual)
        loss_b = selected.at_origin(fitted_b, feature_row, actual)
        losses_a.append(loss_a)
        losses_b.append(loss_b)
        differences.append(loss_a - loss_b)
        folds.append(
            ScoredFold(
                train_start=rows[train_indices[0]].date,
                train_end=rows[train_indices[-1]].date,
                train_rows=len(train_indices),
                feature_date=feature_row.date,
                scored_date=rows[index].date,
            )
        )

    count = len(differences)
    block = _maximum_horizon_overlap(folds)

    def paired_difference(indices: Sequence[int]) -> float:
        """The mean paired difference over one resample of the origins.

        Indexes `differences`, which is the whole point: one draw of origins
        reaches both models through the series that was already differenced
        origin by origin. There is no way to write this that resamples the two
        models apart, because by the time this is called they are one series.
        """

        return sum(differences[i] for i in indices) / len(indices)

    lower, upper = stationary_bootstrap_interval(
        paired_difference,
        count,
        block_length=block,
        seed=seed,
        replications=BOOTSTRAP_REPLICATIONS,
        level=BOOTSTRAP_LEVEL,
    )

    return PairedComparisonReport(
        model_a=model_a,
        model_b=model_b,
        features_a=declared_a,
        features_b=declared_b,
        sources_a=sources_a,
        sources_b=sources_b,
        field_sources_a=field_sources_a,
        field_sources_b=field_sources_b,
        purge_days=purge,
        loss=loss,
        losses_a=tuple(losses_a),
        losses_b=tuple(losses_b),
        differences=tuple(differences),
        mean_difference_bps=sum(differences) / count,
        mean_loss_a_bps=sum(losses_a) / count,
        mean_loss_b_bps=sum(losses_b) / count,
        difference_interval=(lower, upper),
        block_length=block,
        seed=seed,
        replications=BOOTSTRAP_REPLICATIONS,
        level=BOOTSTRAP_LEVEL,
        sign_convention=_sign_convention(model_a, model_b, selected.name),
        folds=tuple(folds),
        decision_time=decision_time,
        minimum_history=minimum_history,
        panel_rows=len(rows),
        panel_first_date=rows[0].date,
        panel_last_date=rows[-1].date,
    )


def panel_sha256(panel_path: Path) -> str:
    """The digest of the panel bytes a run scored.

    One spelling, because the comparison path needs the digest twice and for
    two different purposes: `comparison_seed` derives the resample stream from
    it before the run starts, and `paired_comparison_document` publishes it
    after. Two spellings of the same hash is two places one number comes from,
    and the failure mode is a record whose published digest and whose seed
    material identify different bytes -- which no field of the record could
    disagree about, because each half would be internally correct.

    The CLI never hashes anything itself for the same reason it never derives a
    purge: what identifies the run belongs with the code that produces the run.
    """

    return hashlib.sha256(panel_path.read_bytes()).hexdigest()


def comparison_seed(
    panel_sha256: str,
    *,
    model_a: str,
    features_a: Sequence[str],
    model_b: str,
    features_b: Sequence[str],
    decision_time: time,
) -> int:
    """A reproducible bootstrap seed for a comparison, from what it compares.

    `_report_seed`'s counterpart, and it goes through `_seed_from` for the
    reason that function's docstring gives: the *material* differs between
    artifacts and should, but the digest that turns material into a seed must
    not, or two records that agree about what they scored could still disagree
    about how a seed was derived from it.

    The material is the run's declaration -- the panel bytes, both model names
    and both feature sets in the order the sign convention reads them, and the
    decision time. Not the derived gap: it is a function of the feature sets,
    the registry and the decision time, so including it would add nothing a
    reader could not already recompute, and it is not known until the run has
    started while this must be known before it.

    Order-sensitive, and deliberately: `a` against `b` and `b` against `a` are
    the same comparison with the sign flipped, they publish different records,
    and two records that differ in what they report should not silently share a
    resample stream.
    """

    return _seed_from(
        (
            panel_sha256,
            model_a,
            ",".join(sorted(features_a)),
            model_b,
            ",".join(sorted(features_b)),
            decision_time.isoformat(),
        )
    )


def paired_comparison_document(
    comparison: PairedComparisonReport, *, panel_path: Path, registry_path: Path
) -> dict:
    """The comparison as a publishable record: both sides, and the direction.

    `backtest_document`'s counterpart, and the same four questions shape it --
    what was declared, what that derived, what was scored, what came out --
    with each of the first two answered twice because there are two models.
    Nothing is defaulted: a field this cannot compute is absent rather than
    present with a stand-in, which is the rule the sibling record follows and
    the reason `PairedComparisonReport` has no optional fields to omit.

    **`comparison.sign_convention` is published.** A record carrying a signed
    difference and no statement of which model was subtracted from which is a
    record half its readers will read as the opposite result. The sentence
    names both models rather than referring to "the first" and "the second",
    because a reader who has to count fields to resolve a pronoun will
    sometimes count wrong.

    **The per-origin losses are not published, and that is a decision rather
    than an omission.** They exist on the report, where the pairing can be
    checked by whatever holds it, and they stay off the artifact for the reason
    `backtest_document` publishes no per-forecast dump: the record is a
    publication and not an intermediate. Publishing them would also invite
    exactly the workflow this function was written to replace -- two files
    differenced after the fact -- with the difference that it would look
    supported.

    Args:
        comparison: a report from `paired_model_comparison`.
        panel_path: the panel file as the caller named it. Read here, once, for
            its bytes, so the artifact cannot name one file and hash another.
        registry_path: the source registry the run actually read. Required and
            undefaulted, as it is on the sibling record.

    Returns:
        A JSON-serialisable dict. The caller writes it; this shapes it.

    Raises:
        ProvenanceMismatchError: when a build manifest beside the panel does
            not describe the panel that was scored.
    """

    digest = panel_sha256(panel_path)

    panel: dict = {
        "path": str(panel_path),
        "sha256": digest,
        "row_count": comparison.panel_rows,
        "first_date": comparison.panel_first_date.isoformat(),
        "last_date": comparison.panel_last_date.isoformat(),
    }
    # After the extent, because the binding compares against it, and before
    # anything is returned, because a manifest that does not describe this
    # panel must leave no document behind to be written.
    provenance = _run_provenance(
        panel, panel_path, registry_path=registry_path, thresholds_path=None
    )

    folds: dict = {"count": len(comparison.folds)}
    if comparison.folds:
        folds["first"] = _fold_document(comparison.folds[0])
        folds["last"] = _fold_document(comparison.folds[-1])

    return {
        "declaration": {
            "model_a": {
                "model": comparison.model_a,
                "features": sorted(comparison.features_a),
            },
            "model_b": {
                "model": comparison.model_b,
                "features": sorted(comparison.features_b),
            },
            "decision_time": comparison.decision_time.isoformat(
                timespec="minutes"
            ),
            "minimum_history": comparison.minimum_history,
        },
        "derived": {
            "model_a": {
                "sources": sorted(comparison.sources_a),
                "fields": [
                    f"{source}.{field}"
                    for source, field in sorted(comparison.field_sources_a)
                ],
            },
            "model_b": {
                "sources": sorted(comparison.sources_b),
                "fields": [
                    f"{source}.{field}"
                    for source, field in sorted(comparison.field_sources_b)
                ],
            },
            # One number, for both sides. A comparison in which the two
            # declarations priced different gaps never reaches this function.
            "purge_days": comparison.purge_days,
        },
        "panel": panel,
        "provenance": provenance,
        "folds": folds,
        "comparison": {
            # What was scored, read off the run rather than restated from a
            # module constant: the loss is selectable and a record that named
            # one loss while carrying another would be wrong in the one field a
            # reader uses to interpret every other one.
            "loss": comparison.loss_name,
            "sign_convention": comparison.sign_convention,
            "origin_count": len(comparison.differences),
            # Each side's mean, under the heading its loss earns -- `mae_bps`
            # for the absolute error, `crps_bps` for CRPS. Not one fixed key:
            # a mean CRPS published as `mae_bps` is a number that parses, reads
            # correctly and means something else, and the sibling `backtest`
            # record already spells both headings this way.
            "model_a": {
                "model": comparison.model_a,
                f"{comparison.loss_statistic}_bps": comparison.mean_loss_a_bps,
            },
            "model_b": {
                "model": comparison.model_b,
                f"{comparison.loss_statistic}_bps": comparison.mean_loss_b_bps,
            },
            "mean_difference_bps": comparison.mean_difference_bps,
            "mean_difference_interval": {
                "lower": comparison.difference_interval[0],
                "upper": comparison.difference_interval[1],
                "level": comparison.level,
                "method": "stationary_bootstrap",
                # Measured off this run's own fold horizons, which both models
                # share, so the dependence the gap creates is carried by the
                # resample that reports it.
                "block_length": comparison.block_length,
                "replications": comparison.replications,
                "seed": comparison.seed,
            },
        },
    }


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


def threshold_exceedance(
    regressors: Sequence[str],
    threshold_variable: str,
    minimum_history: int = 20,
) -> ExceedancePredictor:
    """Conditional exceedance from the two-regime ARX's own fitted law.

    The third implementer of `ExceedancePredictor`, and the first whose curve
    moves for two reasons rather than one. `arx_exceedance`'s curve responds to
    a covariate through the design row -- smoothly, because the design row moves
    smoothly. This one's covariate does that *and* selects which of two fitted
    relationships produces the centre, so two feature rows on opposite sides of
    the fitted cutoff get different curves however little else separates them.
    Nothing in `event_eval` had ever scored a predictor that does that.

    **What the block is actually about is the declaration, not the curve.**
    `da78dea` put the regime variable through the *rolling* path's lock: it is
    in `FittedThreshold.features_read`, so `_derive_purge` sizes the gap over
    its fields and `_check_fitter_stayed_inside` refuses a fitter that exceeds
    the declaration. The knowledge holdout is a second path with its own
    declaration check, reached through `ExceedanceCurves.features_read` rather
    than through a fitted model the evaluator never holds, and the regime
    variable had never been through it. The failure that was still available is
    the one four blocks have closed one level at a time: a predictor that
    consults the regime variable to pick a regime, reports only its regressors,
    and gets a gap sized over the wrong fields -- correct arithmetic, wrong set,
    flattering direction.

    `fit_threshold` is fitted on the training rows the evaluator hands over,
    which is everything that cleared the purge gap ahead of the window and
    nothing from inside it, and the fitted model is then read once per feature
    row. Everything fitted is fitted there: the imputations, the threshold, the
    regime assignment and the residual law.

    **`features_read` comes off the fitted model**, exactly as
    `arx_exceedance`'s does. That is where the regime variable is already
    correctly reported -- once, even when it is also a regressor -- and reading
    it a second time here would be a second answer to what the model read.

    **Nothing is re-derived.** The curve is `FittedThreshold.predict_stress`,
    which is `_exceedance_from_residuals` over the pooled leave-one-out law that
    model already fits: no Gaussian, no parametric family, no smoothing and no
    Laplace correction. Above the fitted support a zero stays a zero, for the
    reason `climatology_exceedance` gives at length. Building the curve here
    from the residual vector directly would agree with the model about the
    centre and disagree with it across the cutoff, because the centre is the
    only place the regime enters -- which is precisely the difference this
    implementer exists to score.

    **One law, pooled across regimes.** That is `FittedThreshold`'s decision and
    not one this function may revisit: `FittedForecastModel.residuals` is the
    single sample both outputs read, and a per-regime law would make `predict`
    and `predict_stress` disagree. The regime dependence scored here enters
    through the centre, not the spread.

    Args:
        regressors: the ordered exogenous regressor names, as `fit_threshold`
            takes them. **Required, with no default**, for the reason `fit_arx`
            and `arx_exceedance` refuse one: a default would be a silent
            assumption about which columns a model is entitled to read.
        threshold_variable: what the regime is read off -- a panel column, or
            `spread_bps`, which is computed rather than carried. Required and
            undefaulted for the same reason and more sharply, the one
            `fit_threshold` gives: it does not merely contribute a term, it
            chooses the model.
        minimum_history: the shortest training frame that may produce a fitted
            law. Passed to `fit_threshold`, which raises below it.

    Returns:
        A `fit_predict` callable suitable for `event_eval.evaluate_event_window`.

    Raises:
        ValueError, MissingRegressorError, SingularDesignError,
        UnobservedThresholdError, DegenerateRegimeError, LookAheadError: at call
            time, whatever `fit_threshold` raises on the training frame it is
            given -- the degenerate-split refusal included. They are not caught
            and re-wrapped: a refusal to fit is the fitter's statement about the
            frame, and a wrapper would put a second vocabulary between it and
            the caller. A window with no second regime in it is a fact about the
            window, and the honest report of it is the refusal.
    """

    declared = tuple(str(name) for name in regressors)
    selector = str(threshold_variable)

    def fit_predict(
        train_rows: Sequence[DailyObservation],
        feature_rows: Sequence[DailyObservation],
        taus: Sequence[float],
    ) -> ExceedanceCurves:
        model = fit_threshold(
            train_rows, declared, selector, minimum_history=minimum_history
        )
        return ExceedanceCurves(
            tuple(model.predict_stress(row, taus) for row in feature_rows),
            model.features_read,
        )

    return fit_predict


# --------------------------------------------------------------------------
# The probabilistic target: pooled rolling-origin exceedance evaluation
# --------------------------------------------------------------------------
#
# `AGENT_CONTRACT.md`, "Metrics", names the headline: "Brier skill score
# against climatology, plus Murphy decomposition, so reliability is reported
# separately from resolution. Raw Brier is retained only to satisfy the stated
# commitment; it is not the headline."
#
# Every one of those metrics was implemented in `metrics.py` and called by
# nothing outside `tests/`. The reason was structural rather than an oversight:
# `rolling_persistence_backtest` scores a `FittedForecastModel` and reports MAE,
# interval coverage, pinball loss and CRPS -- continuous-target numbers -- while
# exceedance probabilities come only from an `ExceedancePredictor`, and the only
# evaluator consuming one was `event_eval`, where the contract forbids an
# aggregate. So the headline number was not merely unpublished. There was
# nowhere to compute it.
#
# **Which holdout this is, and why it matters here more than usual.** The
# contract's "Two holdout roles" separates the scoring holdout -- crisis dates
# excluded from the headline metric but available for training once past,
# produced by `rolling_origin` -- from the knowledge holdout, produced by
# `event_eval` and "reported separately and never averaged into the main
# table". This path is the first, and it is the only one an aggregate belongs
# on. The same Metrics section: "Event windows get the exceedance curve and
# realized path. No aggregate Brier or reliability number on a single event
# window." Nothing here reaches into `event_eval`, and `event_eval` gained no
# aggregate for this block. `ExceedanceBacktestReport.holdout_role` is on the
# artifact so a reader of the file, and not only a reader of this comment, can
# tell which table it belongs to.
#
# **Why this is not a flag on `rolling_persistence_backtest`.** The two score
# different interfaces returning different things: one asks a fitted model for
# a quantile vector at `QUANTILE_LEVELS` and scores it against a realized
# value, the other asks a predictor for an exceedance curve over the declared
# tau family and scores it against a realized 0/1 at each tau. They share the
# splitter, the gap derivation, the feature-row rule, the fitter-declaration
# check and the fold record -- and all five are shared by import, which is the
# form of sharing that cannot drift. What they do not share is a return type,
# and a parameter that switched between two return types would be two functions
# wearing one name.


def twcrps_weights(taus: Sequence[float]) -> Tuple[float, ...]:
    """The threshold weighting, derived from the declared family rather than typed.

    `metrics.threshold_weighted_crps` requires weights and refuses to default
    them, because an unweighted score is `crps_on_grid` and has its own name.
    So this path has to declare a weighting, and a declaration is a choice --
    which makes *where the numbers come from* the question, not what they are.

    `w(tau) = tau / max(tau)`: linear in the threshold, normalised at the top of
    the declared grid. It is derived from the family the run was handed, so a
    change to `metadata/stress_thresholds.json` moves it and there is no
    constant here to go stale against that file. Four numbers typed beside the
    four declared taus would be the same weighting today and a silent
    disagreement the day the family changed.

    It weights toward the upper tau, which is what the contract asks for in
    naming twCRPS at all: the interesting failure is a model comfortable
    everywhere and wrong at 50bp. The normalisation does not affect a
    comparison between models on one grid -- it is a common factor -- and it is
    applied so the published number is on a stated scale rather than on the
    scale of whatever units the thresholds happen to be in.

    Raises:
        SplitError: if the top of the grid is not strictly positive. The
            declared family is `{5, 10, 20, 50}` bp and a family that reached
            zero or below would make this weighting meaningless rather than
            merely different, and silently substituting another one is how a
            score gets published under a heading it does not belong to.
    """

    family = _validate_taus(taus)
    top = family[-1]
    if top <= 0.0:
        raise SplitError(
            f"the declared tau family tops out at {top}, so a weighting linear "
            "in tau cannot be normalised; twCRPS weights are derived from the "
            "family and there is no fallback to substitute"
        )
    return tuple(tau / top for tau in family)


@dataclass(frozen=True)
class TauMetrics:
    """The contract's metric set at one threshold, over the pooled scored days.

    One of these per declared tau. Everything is `Optional` that can genuinely
    fail to exist on real data, and each absence is paired with an entry in
    `unavailable` saying why -- the artifact then omits the field and carries
    the reason, so a reader asks rather than believes. `backtest_document`
    already established "a field it cannot compute is absent rather than
    defaulted"; the reason is the half that document could not supply, because
    a missing MAE means the run failed while a missing skill score at 50bp
    means the reference was right about every scored day, which is a result.

    `reference_brier` is the denominator of the skill score, published beside
    it. A skill score is a ratio and a ratio whose denominator is not reported
    cannot be checked -- and on this path the denominator is the whole subject
    of the block, since it is refitted fold by fold.
    """

    tau_bp: float
    scored_days: int
    positives: int
    base_rate: float
    #: Retained because the contract commits to retaining it, and reported as
    #: such. Not the headline: at these base rates it is dominated by the base
    #: rate and two models with very different discrimination look alike.
    brier: float
    reference_brier: float
    brier_skill_score: Optional[float] = None
    #: Murphy/CORP: reliability and resolution reported separately, bin-free.
    #: Fixed-bin ECE is prohibited at these base rates and none is computed.
    decomposition: Optional[CorpDecomposition] = None
    log_score: Optional[float] = None
    #: A `field(default_factory=...)`, not a bare `MappingProxyType({})`.
    #: A mappingproxy sets `__hash__ = None`, and Python 3.11's dataclasses
    #: reads that as a mutable default and refuses the class outright, so
    #: `baseline.py` failed to import and took the seven modules that import it
    #: with it. 3.12 narrowed the check to list/dict/set, which is why only
    #: 3.11 tripped. The factory keeps the immutability: a plain `{}` default
    #: would trade an import error on one interpreter for a mutable default on
    #: a frozen dataclass on all of them.
    unavailable: Mapping[str, str] = field(
        default_factory=lambda: MappingProxyType({})
    )


@dataclass(frozen=True)
class ExceedanceBacktestReport:
    """A pooled rolling-origin exceedance evaluation, and what produced it.

    The three aligned tables -- `forecast`, `reference`, `outcomes` -- are
    day-major and tau-minor, one row per scored day in fold order, and they are
    aligned by construction rather than by convention: each row of `forecast`
    and `reference` came back from `_validate_prediction` against `taus`, and
    each row of `outcomes` was built from `taus` in the same pass. `_at_tau`
    projects a column out of all three at once, which is the one place a tau
    position is read and therefore the one place it could be read wrongly.

    `reference` is the climatology's own curve, per fold. It is carried rather
    than collapsed to a number because it is not a number: refitted at every
    origin, it is a series, and a report holding one value would have thrown
    away the fact the block is about.
    """

    #: Which of the contract's two holdouts produced these numbers. Always
    #: `SCORING_HOLDOUT` here, and recorded rather than assumed: the knowledge
    #: holdout is "reported separately and never averaged into the main table",
    #: and a table that cannot say which one it is invites exactly that average.
    holdout_role: str
    #: The `--model` name the caller selected, carried through rather than
    #: reconstructed from the predictor. The same reasoning `_event_holdout`
    #: gives for `model_config["model"]`: this is the request, and a name
    #: recovered from a callable would agree with the request only for as long
    #: as the mapping stayed a bijection.
    model_name: str
    features: Tuple[str, ...]
    sources: Tuple[str, ...]
    field_sources: Tuple[Tuple[str, str], ...]
    purge_days: int
    decision_time: Optional[time]
    minimum_history: Optional[int]
    panel_rows: Optional[int]
    panel_first_date: Optional[date]
    panel_last_date: Optional[date]
    folds: Tuple[ScoredFold, ...]
    taus: Tuple[float, ...]
    scored_dates: Tuple[date, ...]
    realized_bps: Tuple[float, ...]
    forecast: Tuple[Tuple[float, ...], ...]
    reference: Tuple[Tuple[float, ...], ...]
    outcomes: Tuple[Tuple[int, ...], ...]
    metrics: Tuple[TauMetrics, ...]
    twcrps_weights: Tuple[float, ...]
    twcrps: Optional[float] = None
    twcrps_unavailable: Optional[str] = None

    def at_tau(self, position: int):
        """The three aligned columns at one tau position, projected together."""

        return _at_tau(self.forecast, self.reference, self.outcomes, position)


def _at_tau(forecast, reference, outcomes, position: int):
    """The three aligned tables' columns at one tau position, read together.

    **The single place a tau index is applied.** The tables are day-major and
    tau-minor and all three were built against one validated family, so the
    only remaining way to score a curve against the wrong threshold is to
    project one of them at a different position from the others -- and that is
    now one expression rather than a possibility spread over the file. A path
    that reads the declared family once and indexes it twice can disagree with
    itself, and the disagreement is invisible: every number stays in range and
    the artifact still writes.
    """

    return (
        tuple(day[position] for day in forecast),
        tuple(day[position] for day in reference),
        tuple(day[position] for day in outcomes),
    )


def _tau_metrics(tau: float, columns) -> TauMetrics:
    """The contract's metric set at one threshold, with its absences named."""

    predicted, referenced, realized = columns
    unavailable: dict = {}

    skill: Optional[float]
    try:
        # The reference is the per-fold climatology, passed as the series it
        # is. Collapsing it to its mean here would be the single-reference
        # construction wearing the per-fold one's name.
        skill = brier_skill_score(predicted, realized, climatology=referenced)
    except MetricError as exc:
        skill = None
        unavailable["brier_skill_score"] = str(exc)

    decomposition: Optional[CorpDecomposition]
    try:
        decomposition = corp_decomposition(predicted, realized)
    except MetricError as exc:
        decomposition = None
        unavailable["decomposition"] = str(exc)

    # `log_score` returns `inf` when the forecast put probability 0 on
    # something that happened, deliberately and without clipping. That is a
    # result, and it is the one this evaluator most wants to be able to state
    # -- but `json.dumps` writes it as `Infinity`, which no strict JSON reader
    # accepts, so the artifact would be unparseable rather than informative.
    # Reported as an absence with the reason spelled out: the number is
    # unrepresentable, not uncomputed, and the distinction survives into the
    # file.
    score = log_score(predicted, realized)
    if math.isinf(score):
        unavailable["log_score"] = (
            "the forecast assigned probability 0 to an event that occurred, so "
            "the mean negative log likelihood is infinite. It is not clipped: "
            "a clip replaces an infinite loss with a finite one chosen by "
            "whoever picked the clip, and hides the failure worth seeing"
        )
        reported_score = None
    else:
        reported_score = score

    return TauMetrics(
        tau_bp=float(tau),
        scored_days=len(realized),
        positives=sum(realized),
        base_rate=sum(realized) / len(realized),
        brier=brier_score(predicted, realized),
        reference_brier=brier_score(referenced, realized),
        brier_skill_score=skill,
        decomposition=decomposition,
        log_score=reported_score,
        unavailable=MappingProxyType(dict(unavailable)),
    )


def rolling_exceedance_backtest(
    observations: Iterable[DailyObservation],
    *,
    predictor: ExceedancePredictor,
    model_name: str,
    features: Sequence[str],
    registry: Mapping[str, Mapping[str, object]],
    decision_time: time,
    taus: Sequence[float],
    minimum_history: int = 20,
) -> ExceedanceBacktestReport:
    """Refit at every purged rolling origin, score the next day, pool, then score.

    The scoring holdout for the probabilistic target. Folds come from
    `repo_model.splits.rolling_origin` at `step=1` behind a gap derived from the
    declared feature set through `_derive_purge` -- the same splitter, the same
    derivation and the same feature row as `rolling_persistence_backtest`, all
    by import. At each origin the predictor is fitted on the training rows that
    cleared the gap and asked for one exceedance curve on the last row it was
    allowed to have seen. The curves are pooled across origins and the contract's
    metric set is computed once, over the pool.

    **The climatology is refitted on every fold, on that fold's training rows.**
    This is the whole block, so it is stated rather than left to the loop below
    to imply. A skill score is a ratio against a reference, and the reference is
    a fitted object with a training set. Fit it once over all rows and it has
    seen the scored days: the reference is better than it could have been in
    production, the ratio is *understated*, and the error is in the
    conservative direction, which is why nobody catches it. Fit it once over
    the first fold's training rows and reuse it and the reference decays as the
    window advances while the scored model is refitted, so the skill score
    climbs for no reason but the asymmetry. Either way the arithmetic is right
    and the comparison is not between two things measured the same way. So the
    reference is constructed once and *called* inside the loop, exactly as the
    scored model is, on exactly the rows the scored model got.

    **The reference is the climatology and is not a parameter.** The contract
    says "Brier skill score against climatology"; a reference argument would
    let a run publish a ratio against something else under a heading that says
    climatology, which is the same failure `--model` having no default was
    written to prevent, one level in. `climatology_exceedance` is constructed
    here, at the caller's `minimum_history`, so the reference and the scored
    model are refused on the same short frames rather than one surviving the
    other.

    **What is pooled, and what is not.** Every fold `rolling_origin` yields
    over the panel it was handed. Event windows are not excluded and not
    included: this function knows nothing about them, because the scoring
    holdout is defined by crisis dates being *available for training once they
    are in the past*, which is what an expanding rolling origin does by
    construction. The knowledge holdout is `event_eval`'s, is scored once per
    window, and is never averaged into this table. Nothing here reads
    `metadata/events.json` and nothing here should.

    Args:
        observations: the panel, ascending by date.
        predictor: the `ExceedancePredictor` being scored. Called once per
            fold with that fold's training rows, one feature row, and the
            declared tau family.
        model_name: what to record as having produced these numbers. Required
            and undefaulted: an artifact that named no model, or named one it
            reconstructed, is an artifact a reader cannot compare to another.
        features: the panel columns the predictor is declared to read.
            **Required, keyword-only, with no default**, exactly as on the
            other two paths. The sources follow from it and the gap from the
            sources; nothing about the gap is set by hand.
        registry: the parsed source registry, for `max_release_lag_days`.
        decision_time: when the forecast is made. Required and undefaulted
            there, so required and undefaulted here.
        taus: the declared exceedance family, from
            `data.load_stress_thresholds`. Not defaulted and not spelled in
            this module: the family is `AGENT_CONTRACT.md`'s and Track A's file
            carries it.
        minimum_history: the first origin scored and the shortest training
            frame any fit is allowed, for the scored model and the reference
            alike.

    Raises:
        ValueError: if the panel is too short for `minimum_history`, or
            `model_name` is empty.
        SplitError: on a malformed panel, tau family or prediction, or when the
            gap leaves no origin with `minimum_history` training rows behind
            it.
        LookAheadError: if a fold's feature row does not clear the gap, or if
            the predictor -- or the reference -- reports reading a column
            outside `features`. Both are checked, because both are fitted on
            the training rows and both reads had to be covered by the gap.
        UndeclaredFeatureError: if `features` names a column
            `contract.field_sources_for_features` cannot classify.
        RegistryContractError: if the derived fields cannot support a safe
            bound. Track A's refusal, with Track A's message.
    """

    # Before anything else, and before a single fold: an unresolvable feature
    # set has no gap, so it has no backtest.
    declared: Tuple[str, ...] = tuple(features)
    field_sources, sources, purge = _derive_purge(
        registry, declared, decision_time=decision_time
    )

    if not isinstance(model_name, str) or not model_name:
        raise ValueError(
            f"model_name must be a non-empty string, got {model_name!r}; an "
            "artifact that cannot say which model produced it cannot be "
            "compared to one that can"
        )

    rows = list(observations)
    if len(rows) <= minimum_history:
        raise ValueError("not enough observations for requested minimum history")
    tau_family = _validate_taus(taus)
    weights = twcrps_weights(tau_family)

    # Constructed once, called per fold. Constructing it inside the loop would
    # be identical in effect -- these factories close over nothing but their
    # arguments -- and would read as though the *factory* were the thing being
    # refitted, which is not where the fitting happens.
    reference_predictor = climatology_exceedance(minimum_history=minimum_history)

    dates = [row.date for row in rows]
    folds: List[ScoredFold] = []
    scored_dates: List[date] = []
    realized_bps: List[float] = []
    forecast: List[Tuple[float, ...]] = []
    reference: List[Tuple[float, ...]] = []
    checked = False

    for train_indices, test_indices in rolling_origin(
        dates, minimum_history, 1, purge
    ):
        index = test_indices[0]
        train_rows = tuple(rows[i] for i in train_indices)
        feature_row = rows[_feature_index(dates, train_indices, index, purge)]
        conditioning = (feature_row,)

        predicted = predictor(train_rows, conditioning, tau_family)
        # Refitted here, on this fold's training rows, from the same call the
        # scored model got. Hoisting this one line out of the loop is the
        # mutation `tests/test_baseline.py::RollingExceedanceTests` is planted
        # against, and it is the only line whose position is the subject of a
        # test rather than its behaviour.
        referenced = reference_predictor(train_rows, conditioning, tau_family)

        if not checked:
            # After the first fit, and only the first: the predictor is the
            # same callable at every origin, so a model that stayed inside the
            # declaration here stays inside it at every later one. The
            # reference is checked too -- it is fitted on the same rows and its
            # read had to be covered by the same gap, and a reference nobody
            # checked is a second way for the declaration to be wrong.
            _check_fitter_stayed_inside(
                predicted.features_read, declared, sources, purge
            )
            _check_fitter_stayed_inside(
                referenced.features_read, declared, sources, purge
            )
            checked = True

        forecast.append(_validate_prediction(predicted, 1, tau_family)[0])
        reference.append(_validate_prediction(referenced, 1, tau_family)[0])
        folds.append(
            ScoredFold(
                train_start=rows[train_indices[0]].date,
                train_end=rows[train_indices[-1]].date,
                train_rows=len(train_indices),
                feature_date=feature_row.date,
                scored_date=rows[index].date,
            )
        )
        scored_dates.append(rows[index].date)
        realized_bps.append(rows[index].spread_bps)

    # Strictly greater, matching the contract's `P(spread > tau)`, the
    # `stress_gt_*` label columns and `climatology_exceedance`'s own count.
    # Built from `tau_family` in the same order the curves were produced at, so
    # a curve and the outcome it is scored against cannot come from two
    # different readings of the declaration.
    outcomes = tuple(
        tuple(1 if value > tau else 0 for tau in tau_family)
        for value in realized_bps
    )

    metrics = tuple(
        _tau_metrics(tau, _at_tau(forecast, reference, outcomes, position))
        for position, tau in enumerate(tau_family)
    )

    # twCRPS is over the whole grid on each scored day, not per tau, so it is
    # one number for the run rather than a column of the table above. It needs
    # at least two thresholds to integrate between; a one-tau family is a legal
    # declaration and produces no integral, which is an absence with a reason
    # rather than a refusal of the whole run.
    twcrps: Optional[float] = None
    twcrps_unavailable: Optional[str] = None
    try:
        twcrps = sum(
            threshold_weighted_crps(tau_family, curve, value, weights)
            for curve, value in zip(forecast, realized_bps)
        ) / len(forecast)
    except MetricError as exc:
        twcrps_unavailable = str(exc)

    return ExceedanceBacktestReport(
        holdout_role=SCORING_HOLDOUT,
        model_name=model_name,
        features=declared,
        sources=sources,
        field_sources=field_sources,
        purge_days=purge,
        decision_time=decision_time,
        minimum_history=minimum_history,
        panel_rows=len(rows),
        panel_first_date=rows[0].date,
        panel_last_date=rows[-1].date,
        folds=tuple(folds),
        taus=tau_family,
        scored_dates=tuple(scored_dates),
        realized_bps=tuple(realized_bps),
        forecast=tuple(forecast),
        reference=tuple(reference),
        outcomes=outcomes,
        metrics=metrics,
        twcrps_weights=weights,
        twcrps=twcrps,
        twcrps_unavailable=twcrps_unavailable,
    )


def _exceedance_seed(
    report: ExceedanceBacktestReport, panel_sha256: str, tau: Optional[float] = None
) -> int:
    """A reproducible bootstrap seed, derived from what the run was.

    `_report_seed`'s reasoning, one artifact over, and it shares that
    function's digest rather than restating it: a literal would satisfy the
    signature while making every run in the project draw the same resample
    sequence regardless of what it scored, and nothing in either artifact is
    typed.

    Two things are in the material that are not in `_report_seed`'s. The model
    name, because this path scores a model the caller chose and two models on
    one panel are not one run. And `tau` when a per-threshold interval is being
    drawn, so the four bands in an artifact are four resample streams rather
    than one stream reported four times -- a band that shared a stream with the
    band above it would understate how much the two differ, and it would do so
    invisibly.
    """

    return _seed_from(
        (
            panel_sha256,
            report.model_name,
            ",".join(sorted(report.features)),
            str(report.purge_days),
            "" if report.decision_time is None else report.decision_time.isoformat(),
            ",".join(f"{value:g}" for value in report.taus),
            "" if tau is None else f"{tau:g}",
        )
    )


def _decomposition_document(decomposition: CorpDecomposition) -> dict:
    """CORP's MCB and DSC, with the identity a reader can check it against.

    `identity_residual` is published rather than asserted here for the reason
    `CorpDecomposition` exposes it at all: `score = reliability - resolution +
    uncertainty` is the property the decomposition is *for*, and a file that
    claimed it without carrying the residual would be asking to be believed.
    """

    return {
        "score": decomposition.score,
        "reliability": decomposition.reliability,
        "resolution": decomposition.resolution,
        "uncertainty": decomposition.uncertainty,
        "base_rate": decomposition.base_rate,
        "n": decomposition.n,
        "identity_residual": decomposition.identity_residual(),
    }


def _reliability_document(curve: ReliabilityCurve, *, seed: int, block: int) -> dict:
    """The CORP reliability curve as its step function, with the band.

    **Deduplicated to distinct forecast values, which is lossless.** The curve
    comes back with one entry per scored row, and rows carrying the same
    forecast are pooled before the isotonic fit -- so they share a recalibrated
    value by construction, and the band at them is read off the replicate
    curves by a step lookup at the same `x` and is therefore identical too.
    Writing each repeated value once is the same step function in fewer bytes,
    not a summary of it.

    It still grows with the number of *distinct* forecasts, and that is a
    property of the model rather than of the panel: a climatology contributes
    one point however long the run, a conditional model roughly one per scored
    day. `backtest_document` refuses a per-forecast dump for a reason that does
    not apply here -- the reliability curve is the diagnostic the contract
    asks for, and there is no scalar it can be reduced to. A fixed-bin ECE is
    exactly that scalar and it is prohibited at these base rates.
    """

    points = []
    for position in range(curve.n):
        x = curve.forecast[position]
        if points and points[-1]["forecast"] == x:
            continue
        point = {"forecast": x, "recalibrated": curve.recalibrated[position]}
        if curve.lower:
            point["lower"] = curve.lower[position]
            point["upper"] = curve.upper[position]
        points.append(point)
    return {
        "method": "corp_isotonic",
        "n": curve.n,
        "band": {
            "level": BOOTSTRAP_LEVEL,
            "method": "stationary_bootstrap",
            "block_length": block,
            "replications": BOOTSTRAP_REPLICATIONS,
            "seed": seed,
        },
        "points": points,
    }


def _tau_document(
    report: ExceedanceBacktestReport,
    position: int,
    metrics: TauMetrics,
    *,
    panel_sha256: str,
    block: int,
) -> dict:
    """One threshold's row of the published table, absences and all."""

    predicted, referenced, realized = report.at_tau(position)
    seed = _exceedance_seed(report, panel_sha256, metrics.tau_bp)
    unavailable = dict(metrics.unavailable)

    document: dict = {
        "tau_bp": metrics.tau_bp,
        "scored_days": metrics.scored_days,
        "positives": metrics.positives,
        "base_rate": metrics.base_rate,
        "brier": metrics.brier,
        "reference_brier": metrics.reference_brier,
    }

    if metrics.brier_skill_score is not None:
        document["brier_skill_score"] = metrics.brier_skill_score
        # The interval resamples the day indices, so the forecast, the
        # per-fold reference and the outcome for a day move together. Resampled
        # apart they would break the pairing every score here is computed from.
        def skill(indices: Sequence[int]) -> float:
            return brier_skill_score(
                [predicted[i] for i in indices],
                [realized[i] for i in indices],
                climatology=[referenced[i] for i in indices],
            )

        try:
            lower, upper = stationary_bootstrap_interval(
                skill,
                len(realized),
                block_length=block,
                seed=seed,
                replications=BOOTSTRAP_REPLICATIONS,
                level=BOOTSTRAP_LEVEL,
            )
        except MetricError as exc:
            unavailable["brier_skill_score_interval"] = str(exc)
        else:
            document["brier_skill_score_interval"] = {
                "lower": lower,
                "upper": upper,
                "level": BOOTSTRAP_LEVEL,
                "method": "stationary_bootstrap",
                "block_length": block,
                "replications": BOOTSTRAP_REPLICATIONS,
                "seed": seed,
            }

    if metrics.decomposition is not None:
        document["decomposition"] = _decomposition_document(metrics.decomposition)

    if metrics.log_score is not None:
        document["log_score"] = metrics.log_score

    try:
        curve = corp_reliability_curve(
            predicted,
            realized,
            block_length=block,
            replications=BOOTSTRAP_REPLICATIONS,
            level=BOOTSTRAP_LEVEL,
            seed=seed,
        )
    except MetricError as exc:
        unavailable["reliability_curve"] = str(exc)
    else:
        document["reliability_curve"] = _reliability_document(
            curve, seed=seed, block=block
        )

    if unavailable:
        # Absent *and* accounted for. `backtest_document` omits what it cannot
        # compute so a reader asks rather than believes; on this path the
        # question has a standing answer worth carrying, because the common
        # case is not a broken run but a threshold no scored day crossed.
        document["unavailable"] = dict(sorted(unavailable.items()))
    return document


def exceedance_backtest_document(
    report: ExceedanceBacktestReport,
    *,
    panel_path: Path,
    registry_path: Path,
    thresholds_path: Path,
) -> dict:
    """The pooled exceedance evaluation as a publishable record.

    `backtest_document` is the model and the four sections are its:
    `declaration` is what the caller chose, `derived` is what that produced,
    `panel` and `folds` are what was scored, `metrics` is what came out. Every
    value is computed in the run that emits it, nothing is rounded, and a field
    that cannot be computed is absent rather than defaulted -- with, on this
    path, the reason recorded beside it under `unavailable`.

    **What this one carries that the continuous artifact does not.**

    * `holdout_role`. The contract keeps two holdouts apart and says the
      knowledge holdout is "never averaged into the main table". This file is
      the main table, and a file that cannot say so is one somebody will
      eventually average an event window into.
    `declaration.model` **is no longer one of them.** It was, for as long as
    the continuous path named its model by the fitter the caller passed and
    reported none. `backtest` has grown `--model` since, and both records now
    carry the selected name by the same argument -- it is the thing a reader
    compares two artifacts by, and a record that cannot say what produced it
    cannot be compared to one that can.

    * `declaration.taus_bp` and `declaration.twcrps_weights`. The tau family is
      Track A's declaration and this run consumed a particular version of it;
      the weights are derived from that family by `twcrps_weights` and are
      published because a weighted score whose weights are unstated cannot be
      compared to another one. `provenance.inputs.stress_thresholds` is the
      digest of the file that family was read from, which is the version of a
      declaration that carries no version field.
    * `metrics.by_tau`. One row per threshold, keyed by the tau. The contract's
      metric set is per-threshold except twCRPS, which integrates across the
      grid and is therefore one number for the run.

    **What is deliberately not here.** No aggregate over any event window: those
    are `event_eval`'s, are scored once per window, and the contract forbids an
    aggregate on one. No precision-recall curve either, and that omission is
    worth naming rather than leaving to be noticed -- the contract's Metrics
    section calls for "Precision-recall, not ROC", `metrics.py` implements both
    `precision_recall_curve` and `average_precision`, and neither is called
    here. They are a discrimination diagnostic rather than part of the skill
    decomposition this block was for, and adding them would be a second block's
    worth of decisions about how to publish a curve.

    Args:
        report: a report from `rolling_exceedance_backtest`.
        panel_path: the panel file as the caller named it. Read here, once, for
            its bytes -- the digest and the path come from the same read, so
            the artifact cannot name one file and hash another.
        registry_path: the source registry the run actually read.
        thresholds_path: the stress-threshold declaration the run actually
            read. Both are required and undefaulted, for the reason `--model`
            has no default: a default here is a run that meant to publish a
            reportable record and published one missing its provenance, with
            every other field correct.

    Returns:
        A JSON-serialisable dict. The caller writes it; this shapes it.

    Raises:
        ProvenanceMismatchError: when a build manifest beside the panel does
            not describe the panel that was scored.
    """

    digest = hashlib.sha256(panel_path.read_bytes()).hexdigest()
    # Measured off this run's own fold horizons, by the same function the
    # continuous artifact uses. A wider gap widens the blocks, which is the
    # dependence the gap creates being carried by the resample that reports it.
    block = _maximum_horizon_overlap(report.folds)

    declaration: dict = {
        "model": report.model_name,
        "features": sorted(report.features),
        "taus_bp": list(report.taus),
        "twcrps_weights": list(report.twcrps_weights),
    }
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

    # The same section the continuous record grows, from the same builder and
    # at the same point in the shaping: after the extent the binding compares
    # against, before anything a caller could write.
    provenance = _run_provenance(
        panel,
        panel_path,
        registry_path=registry_path,
        thresholds_path=thresholds_path,
    )

    folds: dict = {"count": len(report.folds)}
    if report.folds:
        folds["first"] = _fold_document(report.folds[0])
        folds["last"] = _fold_document(report.folds[-1])

    metrics: dict = {
        "scored_days": len(report.scored_dates),
        "reference": "climatology_exceedance, refitted on each fold's training rows",
        "by_tau": {
            _tau_key(metric.tau_bp): _tau_document(
                report, position, metric, panel_sha256=digest, block=block
            )
            for position, metric in enumerate(report.metrics)
        },
    }
    if report.twcrps is not None:
        metrics["threshold_weighted_crps"] = report.twcrps
    if report.twcrps_unavailable is not None:
        metrics["unavailable"] = {
            "threshold_weighted_crps": report.twcrps_unavailable
        }

    return {
        "holdout_role": report.holdout_role,
        "declaration": declaration,
        "derived": {
            "sources": sorted(report.sources),
            "fields": [
                f"{source}.{field}" for source, field in sorted(report.field_sources)
            ],
            "purge_days": report.purge_days,
        },
        "panel": panel,
        "provenance": provenance,
        "folds": folds,
        "metrics": metrics,
    }


def _tau_key(tau: float) -> str:
    """A JSON object key for a threshold, stable across runs.

    `_level_key`'s reasoning for a different grid: `repr` of a float is stable
    in Python but is not a promise about a file format, and `5` and `5.0` would
    be two keys for one threshold. `%g` gives the declared family the reading
    `5 10 20 50` that `metadata/stress_thresholds.json` uses, so a reader
    diffing two artifacts is diffing values. Fixed width is wrong here -- the
    family spans an order of magnitude and `50.00` reads as a precision the
    declaration does not claim.
    """

    return f"{float(tau):g}"
