"""Track B's command-line surface: the model and evaluation subcommands.

Owned by **Track B (model and evaluation)**. The ownership gate fails a
`feature/data-layer` branch that touches this file.

`src/repo_model/cli.py` is a dispatcher that names no command. To add one, add
it here: build the subparser and call `set_defaults(handler=...)` on it. Nothing
outside this file changes -- not the dispatcher, not the contract, not the gate.
A handler takes the parsed namespace and returns an exit code; it may raise
`OSError` or any `ValueError` subclass (`SplitError` is one) and the dispatcher
will print it and exit 2.

`event-holdout` lives here, added without touching `cli.py`, which is the
property "Decided: who owns the CLI" was written to get.

Reading Track A's modules from here is fine and expected -- `load_daily_panel`
is imported, not edited. Only writes are gated.

Stdlib only, by contract.
"""

from __future__ import annotations

import argparse
import functools
import json
from dataclasses import dataclass
from datetime import time
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Optional, Tuple, Union

from .baseline import (
    ExceedancePredictor,
    FittedForecastModel,
    ModelFitter,
    arx_exceedance,
    backtest_document,
    climatology_exceedance,
    COMPARISON_LOSSES,
    DEFAULT_COMPARISON_LOSS,
    comparison_seed,
    exceedance_backtest_document,
    fit,
    fit_arx,
    fit_rolling_residual_law,
    fit_threshold,
    paired_comparison_document,
    paired_model_comparison,
    panel_sha256,
    rolling_exceedance_backtest,
    rolling_persistence_backtest,
    threshold_exceedance,
)
from .contract import sources_for_features
from .data import audit_panel, load_daily_panel, load_stress_thresholds
from .event_eval import evaluate_event_window, load_events_file
from .splits import SplitError

#: The autoregressive term every conditional model here carries, and the one
#: column a caller declares that is **not** an exogenous regressor.
#:
#: `fit_arx` and `fit_threshold` build their design as
#: `("intercept", "spread_bps") + regressors`, so the fitter supplies this
#: column itself. It is still declared through `--feature` -- the model reads
#: it, the purge must cover its sources, and `climatology_exceedance` reads
#: nothing else -- but handing it back as a regressor would put the same column
#: in the design twice and the fit would be refused as singular.
#:
#: Named here rather than spelled at the call site, and pinned against
#: `FittedArx.design_names` by
#: `tests/test_cli_eval.py::ModelSelectorTests::test_the_autoregressive_term_is_the_one_the_fitter_supplies`,
#: so a rename in `baseline` fails a test rather than quietly making every
#: conditional run singular.
_AUTOREGRESSIVE_TERM = "spread_bps"


@dataclass(frozen=True)
class _DeferredFactory:
    """A factory in `repo_model.ml`, named rather than imported.

    `tests/test_dependency_boundary.py` fails this module for a *module-level*
    `from .ml import ...`: the core must import on an interpreter that has no
    `ml` extra, and `import repo_model.cli` would otherwise pull the boundary
    module in at import time. But `--model gbm` still has to reach the real
    function object, because
    `tests/test_baseline.py::ExceedancePredictorCoverageTests::test_every_exceedance_predictor_is_reachable_by_name_from_the_cli`
    compares the mapping's factories to the discovered ones **by identity** --
    a wrapper that merely calls through would be a second object and would read
    as an unreachable implementer.

    So the entry names the attribute and resolves it inside a function. What is
    deferred is the *import*, not the identity: `resolve` returns
    `repo_model.ml`'s own function, so the mapping and the walk end at one
    object. `repo_model.ml` itself imports on an interpreter without the extra
    -- that is what its own boundary test requires of it -- so resolving costs
    nothing until a fit is actually run.

    **Both mappings reach `repo_model.ml` through this one class.** `--model
    gbm` on the exceedance path names `gbm_exceedance` here and `--model-a/-b
    gbm` on the continuous path names `fit_gradient_boosted_quantiles`; a
    second deferral mechanism written for the second mapping would be a second
    answer to when the extra is imported and what happens when it is absent,
    and the two would agree until one of them was edited. The refusal a caller
    without the extra sees is therefore the same one on both paths:
    `ml.MissingMLExtraError`, raised from inside the fit, which is a
    `ValueError` and so is printed by the dispatcher as exit 2 rather than
    surfacing as an `ImportError` traceback.
    """

    attribute: str

    def resolve(self) -> Callable[..., Any]:
        from . import ml

        return getattr(ml, self.attribute)


@dataclass(frozen=True)
class _ModelChoice:
    """One `--model` name, and how the predictor behind it is constructed.

    The four factories have different signatures --
    `climatology_exceedance(minimum_history)`,
    `arx_exceedance(regressors, minimum_history)`,
    `threshold_exceedance(regressors, threshold_variable, minimum_history)`,
    `gbm_exceedance(regressors, minimum_history)` -- so the mapping has to carry
    construction and cannot be a name-to-callable table.

    `factory` is the `baseline` (or `ml`) factory itself, and `build` is handed
    that same object rather than closing over one of its own. The two therefore
    cannot name different models: `tests/test_baseline.py`'s
    `ExceedancePredictorCoverageTests` reads `factory` to assert every
    discovered implementer is reachable from here, and a `build` free to call
    something else would make that assertion a statement about a field nobody
    runs.

    `declared` is the field and `factory` is the property, because one entry --
    the one in `repo_model.ml` -- may not be imported at module level; see
    `_DeferredFactory`. Every other entry stores the function directly and the
    property hands it straight back.
    """

    declared: Union[Callable[..., ExceedancePredictor], _DeferredFactory]
    build: Callable[..., ExceedancePredictor]
    needs_regime_variable: bool

    @property
    def factory(self) -> Callable[..., ExceedancePredictor]:
        if isinstance(self.declared, _DeferredFactory):
            return self.declared.resolve()
        return self.declared

    @property
    def needs_ml_extra(self) -> bool:
        """Does running this name require the optional `ml` extra?

        Read by `tests/test_cli_eval.py`, which runs every selectable name end
        to end and must skip the one name that cannot run on a core checkout.
        Derived from how the entry is declared rather than written down beside
        it: a second list of which models need the extra would be updated in
        the same commit that added the model it was meant to cover.
        """

        return isinstance(self.declared, _DeferredFactory)

    def construct(
        self,
        *,
        regressors: Tuple[str, ...],
        regime_variable: Optional[str],
        minimum_history: int,
    ) -> ExceedancePredictor:
        return self.build(self.factory, regressors, regime_variable, minimum_history)


#: `--model NAME` -> the predictor it names. **One mapping, in one place.**
#:
#: Every `ExceedancePredictor` in `baseline` is required to appear here, and
#: that requirement is enforced by extending the guard that already discovers
#: them -- `tests/test_baseline.py::ExceedancePredictorCoverageTests` -- rather
#: than by a second guard beside it. A fifth implementer the command line
#: cannot run then fails an existing test instead of going unnoticed.
MODEL_FACTORIES = MappingProxyType(
    {
        "climatology": _ModelChoice(
            declared=climatology_exceedance,
            build=lambda factory, regressors, regime, minimum_history: factory(
                minimum_history=minimum_history
            ),
            needs_regime_variable=False,
        ),
        "arx": _ModelChoice(
            declared=arx_exceedance,
            build=lambda factory, regressors, regime, minimum_history: factory(
                regressors, minimum_history=minimum_history
            ),
            needs_regime_variable=False,
        ),
        "threshold": _ModelChoice(
            declared=threshold_exceedance,
            build=lambda factory, regressors, regime, minimum_history: factory(
                regressors, regime, minimum_history=minimum_history
            ),
            needs_regime_variable=True,
        ),
        # The one entry the core cannot import; see `_DeferredFactory`. Its
        # construction signature is the ARX's -- regressors plus a minimum
        # history -- because it reads the same declared feature set: the
        # autoregressive term the fitter supplies itself, plus whatever
        # `--feature` named.
        "gbm": _ModelChoice(
            declared=_DeferredFactory("gbm_exceedance"),
            build=lambda factory, regressors, regime, minimum_history: factory(
                regressors, minimum_history=minimum_history
            ),
            needs_regime_variable=False,
        ),
    }
)


def _model_names() -> str:
    """The selectable names, for a help string and for a refusal message."""

    return ", ".join(sorted(MODEL_FACTORIES))


def _select_model(args: argparse.Namespace) -> Tuple[str, ExceedancePredictor]:
    """Resolve `--model` to a constructed predictor, or refuse before anything runs.

    **A selector that falls back instead of refusing is the failure this
    function exists to prevent.** `--model arx` misspelled, or a name the
    mapping does not know, resolving to the climatology and running to
    completion produces real curves, a real journal record and a real hash with
    the word `climatology` in it -- and a reader comparing that record to the
    ARX's is comparing the baseline to itself. Every number is correct; the only
    thing wrong is which model produced them, and nothing in the artifact
    disagrees. So an unknown name raises here, naming the value and the names
    that exist, and it raises before the panel is read so that no journal record
    can be written for a run that was refused.

    **The regressors are the declaration, minus what the fitter supplies
    itself.** `sorted(args.feature)` is what sizes the purge and what
    `evaluate_event_window` checks `ExceedanceCurves.features_read` against, so
    the regressors are taken *from* it rather than declared beside it: what the
    predictor is handed and what the run declared are then the same set by
    construction, and there is no second list that could disagree with the
    first. `_AUTOREGRESSIVE_TERM` comes out because the fitter puts it in the
    design itself, and the regime variable comes out because it is not a term.

    **The regime variable must be one of `--feature`, and this refuses it here
    rather than leaving it to the guard downstream.** `event_eval` would catch
    it -- `_check_fitter_stayed_inside` raises `LookAheadError` when
    `features_read` exceeds the declaration, and a threshold model reports its
    regime variable -- and that guard is correct and stays. But a CLI that
    relies on a downstream guard to validate its own arguments is a CLI that
    will stop doing so the moment the call site moves, and the message a caller
    gets should name the column and the flag they typed rather than describe a
    fitted model.

    Returns:
        `(name, fit_predict)`, where `name` is the string the caller passed.
        It is not re-derived from the factory: the journal records what was
        asked for, and a name reconstructed from the object would agree with
        the request only for as long as the mapping is a bijection.
    """

    name = args.model
    choice = MODEL_FACTORIES.get(name)
    if choice is None:
        raise SplitError(
            f"unknown --model {name!r}; this command can run {_model_names()}. "
            "There is no default: the default would be the climatology, which "
            "is the reference a skill score is measured against, so a run "
            "meaning to score a conditional model would publish the baseline's "
            "numbers under that model's name"
        )

    regressors, regime_variable = _regressors_and_regime(
        args, name, choice.needs_regime_variable
    )
    return name, choice.construct(
        regressors=regressors,
        regime_variable=regime_variable,
        minimum_history=args.minimum_history,
    )


def _regressors_and_regime(
    args: argparse.Namespace,
    name: str,
    needs_regime_variable: bool,
    *,
    side: str = "",
) -> Tuple[Tuple[str, ...], Optional[str]]:
    """Split `--feature` into regressors and a regime variable, or refuse.

    Shared by both selectors, because the rules are one rule and not two. The
    *mappings* are deliberately separate -- a `ModelFitter` is not an
    `ExceedancePredictor`, and one table for both interfaces would be a lie
    about the types -- but how `--feature` is divided, and when
    `--regime-variable` is required or refused, is a property of the
    declaration rather than of either interface. Written twice it would be two
    statements of the same rule that agree until one of them is edited, which
    is the failure a second name-to-model mapping would be.

    Every message names `--model {name}` rather than a model class, so a caller
    reads back the flag they typed.

    `side` is the suffix the flags carry on the command being served -- `""` on
    the three single-model commands, `"-a"` and `"-b"` on `compare`, which
    declares each model separately. It is a label on the messages and nothing
    else: the rule this function applies does not vary by side, and a second
    copy of it that happened to spell its flags differently is exactly what
    sharing this function prevents.
    """

    declared = tuple(sorted(args.feature))
    regime_variable = args.regime_variable

    if needs_regime_variable:
        if regime_variable is None:
            raise SplitError(
                f"--model{side} {name} reads a regime variable off each row to choose "
                "which of two fitted relationships produces the centre, and "
                f"--regime-variable{side} names no column. It is required and "
                "undefaulted for the reason the column is: it does not merely "
                "contribute a term, it chooses the model"
            )
        if regime_variable not in declared:
            raise SplitError(
                f"--regime-variable{side} {regime_variable} is not one of the declared "
                f"features {list(declared)}. The purge is sized over the "
                "declaration before anything is fitted, so a regime variable "
                "outside it would have its release lag missing from the gap -- "
                f"declare it with --feature{side} {regime_variable} rather than "
                "reading a column the run did not declare"
            )
    elif regime_variable is not None:
        raise SplitError(
            f"--regime-variable{side} {regime_variable} was given, but "
            f"--model{side} {name} "
            "reads no regime variable. A flag that is accepted and ignored is "
            "read by the next person as a setting that took effect"
        )

    regressors = tuple(
        column
        for column in declared
        if column != _AUTOREGRESSIVE_TERM and column != regime_variable
    )
    return regressors, regime_variable


def _residual_window(
    args: argparse.Namespace,
    name: str,
    needs_window: bool,
    *,
    side: str = "",
) -> Optional[int]:
    """Resolve `--residual-window`, or refuse. `_regressors_and_regime`'s shape.

    Required for the model that reads it and refused for the models that do not,
    by the same two-sided rule `--regime-variable` follows: a missing required
    argument is a decision nobody made, and an accepted-and-ignored one is read
    by the next person as a setting that took effect.

    **Required and undefaulted, and the reason is `--model`'s own.** The window
    decides how much history the published interval is a statement about. A
    default would be that decision made by whoever wrote this line, carried into
    every record that did not override it, and indistinguishable in the artifact
    from a window somebody chose. It is also the argument a reader would most
    expect to be tuned, which is the second reason it cannot be: a window picked
    by scoring candidate lengths against the panel is a hyperparameter fitted
    outside `fit`, and the contract forbids that in those words.

    **The flag is not `--residual-window`'s obvious shorter name.**
    `event-holdout` already has a `--window NAME`, which names a declared event
    window, and two flags spelled the same across two subcommands meaning a
    crisis period in one and a count of residuals in the other is the
    same-name-different-meaning collision `AGENT_CONTRACT.md` has now recorded
    five times. The value is still `window` where the fitter receives it,
    because that is what the argument is called in `baseline`.

    Range is not checked here. `fit_rolling_residual_law` refuses a window below
    2 and one longer than the frame's residuals, and the second of those cannot
    be checked before the panel is read -- so checking the first here would put
    half the rule in each of two places.
    """

    window = args.residual_window

    if needs_window:
        if window is None:
            raise SplitError(
                f"--model{side} {name} reads its residual law from a trailing "
                f"window of the training frame, and --residual-window{side} "
                "names no length. It is required and undefaulted for the reason "
                f"--model{side} is: the window decides how much history the "
                "reported interval is a statement about, and a default would be "
                "that decision made by nobody and invisible in the record"
            )
        return int(window)

    if window is not None:
        raise SplitError(
            f"--residual-window{side} {window} was given, but --model{side} "
            f"{name} reads its residual law from the whole training frame. A "
            "flag that is accepted and ignored is read by the next person as a "
            "setting that took effect -- here, as an interval narrower than the "
            "one the record actually reports"
        )
    return None


@dataclass(frozen=True)
class _FitterChoice:
    """One `--model` name on the continuous path, and the fitter behind it.

    `_ModelChoice`'s counterpart for the other interface, and separate from it
    on purpose. `rolling_persistence_backtest` takes a `ModelFitter` --
    `(train_frame, minimum_history=...) -> FittedForecastModel` -- and
    `rolling_exceedance_backtest` takes an `ExceedancePredictor`. One table
    covering both would have to hold a value that is sometimes one and
    sometimes the other, and the type would stop saying which.

    The fitters have different signatures -- `fit(train_frame)`,
    `fit_arx(train_frame, regressors)`,
    `fit_threshold(train_frame, regressors, threshold_variable)`,
    `fit_rolling_residual_law(train_frame, window)`,
    `fit_gradient_boosted_quantiles(train_frame, regressors)` -- so `build`
    carries construction, and what it constructs is a `functools.partial`,
    which is the shape `baseline.ModelFitter`'s own docstring names.

    `factory` is the fitter itself and `build` is handed that same object
    rather than closing over one of its own, for the reason `_ModelChoice`
    gives: the two cannot then name different models.

    `declared` is the field and `factory` is the property, for the reason
    `_ModelChoice` splits the same pair: one entry lives in `repo_model.ml` and
    may not be imported at module level. Every other entry stores the function
    directly and the property hands it straight back. See `_DeferredFactory`.

    `needs_window` is `needs_regime_variable`'s counterpart for the trailing
    residual window, and it is a separate flag rather than a shared "takes an
    extra argument" because the two arguments are required of different models
    and refused of different models. One flag covering both would make
    `--regime-variable` accepted by a model that reads no regime, and a flag
    accepted and ignored is read by the next person as a setting that took
    effect.
    """

    declared: Union[Callable[..., FittedForecastModel], _DeferredFactory]
    build: Callable[..., ModelFitter]
    needs_regime_variable: bool
    needs_window: bool = False

    @property
    def factory(self) -> Callable[..., FittedForecastModel]:
        if isinstance(self.declared, _DeferredFactory):
            return self.declared.resolve()
        return self.declared

    @property
    def needs_ml_extra(self) -> bool:
        """Does running this name require the optional `ml` extra?

        `_ModelChoice.needs_ml_extra`'s counterpart, derived the same way and
        for the same reason: a second list of which models need the extra would
        be updated in the same commit that added the model it was meant to
        cover. Read by the tests that run every selectable name end to end and
        must skip the ones a core checkout cannot fit.
        """

        return isinstance(self.declared, _DeferredFactory)

    def construct(
        self,
        *,
        regressors: Tuple[str, ...],
        regime_variable: Optional[str],
        window: Optional[int] = None,
    ) -> ModelFitter:
        return self.build(self.factory, regressors, regime_variable, window)


#: `--model NAME` -> the continuous fitter it names. **One mapping, in one
#: place**, and the only thing in this repository that turns a name into a
#: `ModelFitter`. A second one would be how `backtest` and the comparison that
#: follows it come to disagree about what `arx` means while both look right.
#:
#: `minimum_history` is absent from the partials on purpose:
#: `rolling_persistence_backtest` passes it at every origin, so binding it here
#: as well would be two places one number comes from.
FITTER_FACTORIES = MappingProxyType(
    {
        "persistence": _FitterChoice(
            declared=fit,
            # Nothing to bind: `fit` already has the `ModelFitter` shape. The
            # entry exists so that persistence is a *name* a caller selects
            # rather than what happens when nobody says.
            build=lambda factory, regressors, regime, window: factory,
            needs_regime_variable=False,
        ),
        "arx": _FitterChoice(
            declared=fit_arx,
            build=lambda factory, regressors, regime, window: functools.partial(
                factory, regressors=regressors
            ),
            needs_regime_variable=False,
        ),
        "threshold": _FitterChoice(
            declared=fit_threshold,
            build=lambda factory, regressors, regime, window: functools.partial(
                factory, regressors=regressors, threshold_variable=regime
            ),
            needs_regime_variable=True,
        ),
        # Persistence's point rule with its residual law cut to a trailing
        # window. Selectable by name for the reason every other model here is:
        # a model the command line cannot construct is one only the test suite
        # can run, and this one exists to be one side of a published comparison
        # against the persistence entry two lines up.
        "rolling-residual": _FitterChoice(
            declared=fit_rolling_residual_law,
            build=lambda factory, regressors, regime, window: functools.partial(
                factory, window=window
            ),
            needs_regime_variable=False,
            needs_window=True,
        ),
        # The one entry the core cannot import, and the first model on this
        # path that is not `baseline`'s; see `_DeferredFactory`. Its
        # construction signature is the ARX's -- `regressors` bound here, and
        # `minimum_history` left for the fold loop to pass at every origin --
        # because it reads the same declared feature set: the autoregressive
        # term the fitter supplies itself, plus whatever `--feature` named.
        #
        # `fit_gradient_boosted_quantiles` is named directly rather than
        # wrapped, so what `compare` scores under `--loss crps` is the model's
        # **own** law -- `_crps_at` reads `fitted.predict`, and this model's
        # `predict` is five fits rearranged, not a median with a residual
        # sample laid around it. An adapter here that produced the second thing
        # would run, would put `gbm` in the record, and would publish a CRPS
        # that is not this model's.
        "gbm": _FitterChoice(
            declared=_DeferredFactory("fit_gradient_boosted_quantiles"),
            build=lambda factory, regressors, regime, window: functools.partial(
                factory, regressors=regressors
            ),
            needs_regime_variable=False,
        ),
    }
)


def _fitter_names() -> str:
    """The selectable continuous models, for a help string and a refusal."""

    return ", ".join(sorted(FITTER_FACTORIES))


def _select_fitter(
    args: argparse.Namespace, *, side: str = ""
) -> Tuple[str, ModelFitter]:
    """Resolve `--model` to a constructed `ModelFitter`, or refuse first.

    `_select_model`'s counterpart on the continuous path, and the argument for
    refusing rather than falling back is the same one with more force. There
    the default a convenience would pick is the climatology, which is the
    reference a skill score is a ratio against. Here it is **persistence**,
    which is the model `PLAN.md`'s Phase 2 exit criterion names: *"a model that
    beats persistence out of sample"*. A run meaning to publish an ARX and
    getting the persistence fitter publishes the benchmark's own numbers under
    the ARX's name, in a record whose feature set, gap, folds, panel digest and
    provenance are all correct -- and the comparison block reading two such
    records would conclude that the challenger ties the baseline exactly.

    Until this block there was no flag at all and `_backtest` called the
    backtest without `fit_model`, so that failure did not need a misspelling:
    it was the only behaviour available. The flag is required and undefaulted
    so that behaviour does not survive as an unnamed path.

    Returns:
        `(name, fit_model)`, where `name` is the string the caller passed and
        is what the record will carry. Not re-derived from the fitter: several
        of these produce objects of the same class, so a name reconstructed
        from one would not identify it.
    """

    name = args.model
    choice = FITTER_FACTORIES.get(name)
    if choice is None:
        raise SplitError(
            f"unknown --model{side} {name!r}; this command can run "
            f"{_fitter_names()}. There is no default: the default would be "
            "persistence, which is the benchmark every other model here is "
            "asked to beat, so a run meaning to score a challenger would "
            "publish the benchmark's numbers under the challenger's name"
        )

    regressors, regime_variable = _regressors_and_regime(
        args, name, choice.needs_regime_variable, side=side
    )
    window = _residual_window(args, name, choice.needs_window, side=side)
    return name, choice.construct(
        regressors=regressors, regime_variable=regime_variable, window=window
    )


def _registry(args: argparse.Namespace) -> dict:
    """The parsed source registry at `--registry`. One reader, two commands."""

    return json.loads(Path(args.registry).read_text(encoding="utf-8"))


def _derived_sources(args: argparse.Namespace) -> tuple[str, ...]:
    """The sources the declared feature set draws on, for the journal hash alone.

    `contract.sources_for_features` is the only supported way from a feature set
    to source IDs, and this module makes no second attempt at the mapping. There
    is no `--source`: sources are derived, never supplied. A caller who could
    name the sources by hand could name a set that did not cover what the model
    reads, and the gap computed from it would be correct arithmetic over the
    wrong evidence -- which is the failure that survives every check the purge
    block installed, because the number itself looks fine.

    **This no longer sizes anything.** Since the field-priced-purge block the
    gap comes from `baseline._derive_purge` over `(source, field)` pairs, and
    the only remaining consumer of this is `model_config`, which is hashed into
    the event journal. It is deliberately left on the source-level resolver:
    the hash identifies a scoring run, and moving it would make every existing
    journal record look like a different run for a reason that has nothing to
    do with what was scored. `contract.sources_for_features` is the human's to
    retire once nothing calls it; this is what still calls it.
    """

    return sources_for_features(args.feature)


# There is no `_purge_days` here any more. Both evaluation paths derive the gap
# inside the function that uses it, from the feature set the caller declared, so
# this module hands over `--feature`, `--registry` and `--decision-time` and
# never holds the number. A gap computed here and passed in would be a second
# place the number could come from, and the CLI is the one place a caller would
# reach to change it.


def _backtest(args: argparse.Namespace) -> int:
    """Run the purged rolling-origin benchmark and report what sized the gap.

    **There is no `--purge` here either.** The event path has not had one since
    it was written, and the two paths now mean the same thing by a gap and take
    the number from the same place -- which was already written down in
    `_event_holdout` and is only now true. A hand-set gap on this path would be
    reached for at exactly the moment it must not be: the purge drops training
    rows, a short panel then has fewer origins, and the flag would be right
    there.

    **And there is no `--source`.** The gap is derived from the sources, and the
    sources are derived from the declared feature set. A caller who could name
    the sources by hand could name a set that did not cover what the model
    reads; the purge would then be computed correctly over the wrong evidence,
    and nothing downstream could tell. `--feature` is the one declaration, and
    everything else follows from it.

    **There is a `--model`, and it is required.** This command used to call
    `rolling_persistence_backtest` without `fit_model`, so the only continuous
    model reachable from outside the test suite was the default persistence
    fitter -- while `baseline` had `fit_arx` and `fit_threshold` beside it and
    `PLAN.md`'s Phase 2 exit criterion asked for *"a model that beats
    persistence"*. A conditional model had no path to a published record. It
    selects through `_select_fitter`, whose mapping is the only thing here that
    turns a name into a `ModelFitter`, and the flag is undefaulted because the
    default would be the very model the comparison is against. The regressors
    come out of `--feature` rather than beside it, so what the fitter is handed
    and what the run declared are the same set by construction.

    `features`, `sources`, `fields` and `purge_days` are reported beside the
    metrics for the reason `model_config` carries them on the event path: a
    benchmark whose gap came from somewhere an auditor cannot follow is not a
    benchmark. All four are read off the report rather than recomputed here, so
    what is printed is what shaped the run. `fields` is the one the gap is
    actually sized over since the field-priced-purge block, and `sources` is
    the projection of it: on `fred_macro_latest_vintage` the source name alone
    cannot say whether the number came from a field that prices or a field
    that would have been refused.

    **`--report` is required, and that is the point of this block.** Until now
    every number this command produced existed only in a terminal: the pinball
    losses the metrics module has implemented all along were never computed by
    anything, and `PLAN.md`'s Milestone A -- which ends in a *published*
    quantile loss -- had nothing to publish into. A run that emits no artifact
    leaves a figure whose conditions are gone the moment the scrollback is, and
    the next place that figure appears is prose, which is the failure
    `tests/test_docs_freshness.py` exists to stop one level down. So the
    artifact is not an option on the benchmark; it is what running the
    benchmark means.

    The document is `baseline.backtest_document`'s, not this module's. Shaping
    it here would put the report's schema in the caller and leave the run
    unable to say what it produced -- and it is `baseline` that holds the
    folds, the levels and the losses. This function reads the panel, runs the
    backtest, writes the bytes, and prints the same summary it always printed.

    The file is written only after the run returns. A refusal -- an unpriced
    source, an undeclared feature, a starved gap -- must leave no artifact
    behind, for the same reason the existing tests assert that a refusal prints
    no benchmark: a report on disk is a claim that a benchmark ran.
    """

    # Before the panel is read, so a refused `--model` leaves no report behind
    # for the same reason a starved gap does not: a file on disk is a claim
    # that a benchmark ran.
    model_name, fit_model = _select_fitter(args)

    rows = load_daily_panel(args.path)
    audit_panel(rows)
    report = rolling_persistence_backtest(
        rows,
        features=args.feature,
        registry=_registry(args),
        decision_time=time.fromisoformat(args.decision_time),
        minimum_history=args.minimum_history,
        fit_model=fit_model,
    )

    # `--registry` is passed to the record as well as to the run: the record
    # must identify the registry version the gap was priced by, and the only
    # file that can answer is the one this command actually opened.
    # `model` is passed for the same kind of reason and is the name the caller
    # selected, travelling with the numbers that name produced.
    document = backtest_document(
        report,
        panel_path=args.path,
        registry_path=args.registry,
        model=model_name,
    )
    args.report.write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    # Unrounded in the file, rounded on the console. The two are not in tension:
    # the artifact is the record and must not publish a figure nobody computed,
    # while the console is a human reading a terminal. Both take their values
    # off the same report -- the summary below is not a second computation of
    # anything in the document.
    print(
        json.dumps(
            {
                # The one thing the console could not previously say, because
                # there was only one answer it could have given.
                "model": model_name,
                "forecast_count": len(report.forecasts),
                "mae_bps": round(report.mae_bps, 4),
                "interval_coverage": round(report.interval_coverage, 4),
                "features": sorted(report.features),
                "purge_days": report.purge_days,
                "sources": sorted(report.sources),
                # The pairs the gap was actually sized over, in the same
                # `source.field` form and from the same report field the
                # artifact's `derived.fields` is built from. The console and
                # the file must agree about what was priced, and the only way
                # they can is to read the one report rather than each deriving
                # the list.
                "fields": [
                    f"{source}.{field}" for source, field in sorted(report.field_sources)
                ],
                "minimum_history": args.minimum_history,
                "report": str(args.report),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _side(args: argparse.Namespace, side: str) -> argparse.Namespace:
    """One side of `compare`, in the shape `_select_fitter` already reads.

    `compare` declares each model separately -- `--model-a`, `--feature-a`,
    `--regime-variable-a`, `--residual-window-a`, and the same four for `b` --
    because the two models being compared are usually declared over different
    columns and one shared `--feature` would either over-purge the simpler model
    or leave the richer one's columns unpriced. The window is per side for a
    sharper version of the same reason: the comparison this model was built for
    is one window against another, or a window against the full sample, and a
    shared flag could not express either.

    This projects one side of that namespace onto the field names the existing
    selector reads, so `compare` reaches models through **the same mapping and
    the same argument rules** as `backtest` rather than through a second copy.
    That is the packet's reason for the ordering: block 3 is what makes a name
    mean a model on this path, and a comparison that resolved names itself
    would be a second answer to what `arx` means, agreeing with the first until
    it did not.

    `minimum_history` is carried across unchanged and is deliberately one
    number for both sides: two models fitted on different minimum frames are
    scored at different origins, which is the same defect the derived-gap
    refusal exists to catch, arriving through a different door.
    """

    return argparse.Namespace(
        model=getattr(args, f"model_{side}"),
        feature=getattr(args, f"feature_{side}"),
        regime_variable=getattr(args, f"regime_variable_{side}"),
        residual_window=getattr(args, f"residual_window_{side}"),
        minimum_history=args.minimum_history,
    )


def _compare(args: argparse.Namespace) -> int:
    """Score two continuous models at the same origins and publish the gap.

    **The command `PLAN.md`'s Phase 2 exit criterion needed and did not have.**
    That criterion is *"a model that beats persistence out of sample"*, which
    is a comparison; what the repository could produce was two `backtest`
    records, each carrying an MAE and an interval around it. A reader with two
    such files compares the intervals and asks whether they overlap, which is
    not the question -- and the two records cannot be made to answer the real
    one, because they carry metrics rather than per-origin losses and
    deliberately so.

    So the pairing is made by construction rather than reconstructed
    afterwards: `baseline.paired_model_comparison` runs one fold loop, fits
    both models on each fold's training rows, scores both on that fold's
    origin, and puts one resample draw through the differenced series. This
    function reads the panel, derives the seed, writes the bytes and prints a
    summary; it computes no statistic of its own.

    **Both model names are required and neither has a default,** for the reason
    `--model` is required on `backtest` with more force. There the default a
    convenience would pick is persistence, the benchmark. Here a defaulted side
    would make the *comparison* persistence-against-persistence while carrying
    the challenger's name, and the record would report a difference of zero
    with a degenerate interval -- which is exactly the shape of the
    climatology-against-itself sanity check that this project treats as
    evidence that everything is wired correctly.

    **`--report` is required**, for the reason every other command here
    requires one: a figure that exists only in a terminal is a figure whose
    conditions are gone the moment the scrollback is, and the next place it
    appears is prose.

    **There is no `--purge` and no `--source`**, on either side. Both gaps are
    derived from their own declarations, and the run is refused if they differ
    -- see `baseline.IncomparablePurgeError`. A flag that set the gap by hand
    would be reached for at exactly the moment it must not be, because the
    obvious way to make two declarations comparable is to overrule one of them.

    **`--loss` selects what the difference is a difference of, and defaults to
    the absolute error.** The first comparison this command was asked for --
    persistence against the trailing-window residual law -- reported
    `mean_difference_bps` of `0.0` with a `[0.0, 0.0]` interval, because the two
    models share a point rule and differ only in the law around it. That is not
    a null result, it is a point-only instrument reporting on a distributional
    change; `backtest` already separates the same pair through `crps_bps`. So
    `--loss crps` is available and `--loss absolute-error` remains the default,
    which is what keeps every published `compare` command and every record under
    `docs/runs/` meaning exactly what it meant before this flag existed.

    The file is written only after the run returns, so a refusal -- an unknown
    model name, mismatched gaps, a starved fold -- leaves no artifact behind.
    """

    # Before the panel is read, so a refused model name or a refused
    # regime variable leaves no report behind.
    model_a, fit_a = _select_fitter(_side(args, "a"), side="-a")
    model_b, fit_b = _select_fitter(_side(args, "b"), side="-b")

    rows = load_daily_panel(args.path)
    audit_panel(rows)

    decision_time = time.fromisoformat(args.decision_time)
    # The digest is `baseline`'s to take, and it is taken once: the seed and
    # the record's `panel.sha256` must identify the same bytes, and two
    # spellings of one hash is where they would come apart while each stayed
    # internally correct.
    seed = comparison_seed(
        panel_sha256(args.path),
        model_a=model_a,
        features_a=args.feature_a,
        model_b=model_b,
        features_b=args.feature_b,
        decision_time=decision_time,
    )

    comparison = paired_model_comparison(
        rows,
        model_a=model_a,
        fit_a=fit_a,
        features_a=args.feature_a,
        model_b=model_b,
        fit_b=fit_b,
        features_b=args.feature_b,
        registry=_registry(args),
        decision_time=decision_time,
        seed=seed,
        minimum_history=args.minimum_history,
        loss=args.loss,
    )

    document = paired_comparison_document(
        comparison, panel_path=args.path, registry_path=args.registry
    )
    args.report.write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    lower, upper = comparison.difference_interval
    # Unrounded in the file, rounded on the console, both read off the one
    # report -- the summary is not a second computation of anything above.
    # `sign_convention` is printed rather than summarised: a reader looking at
    # a signed number in a terminal needs the direction in the same breath as
    # the number, and shortening it here would be a second, weaker statement of
    # the thing the record states once.
    print(
        json.dumps(
            {
                "model_a": comparison.model_a,
                "model_b": comparison.model_b,
                "sign_convention": comparison.sign_convention,
                "origin_count": len(comparison.differences),
                # Keyed by the loss that produced them, as the record is:
                # `mae_a_bps` under the default and `crps_a_bps` under CRPS.
                # A fixed key would put a CRPS on the console under the name of
                # a mean absolute error, which is the one place a reader is
                # most likely to copy a number out of.
                f"{comparison.loss_statistic}_a_bps": round(
                    comparison.mean_loss_a_bps, 4
                ),
                f"{comparison.loss_statistic}_b_bps": round(
                    comparison.mean_loss_b_bps, 4
                ),
                "loss": comparison.loss_name,
                "mean_difference_bps": round(comparison.mean_difference_bps, 4),
                "difference_interval_bps": [round(lower, 4), round(upper, 4)],
                "interval_level": comparison.level,
                "block_length": comparison.block_length,
                "purge_days": comparison.purge_days,
                "minimum_history": args.minimum_history,
                "report": str(args.report),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _event_holdout(args: argparse.Namespace) -> int:
    """Score declared knowledge-holdout windows, once each, and report the curves.

    Every number this command needs that somebody else declared, it reads from
    where they declared it. That is the whole design, and it is the same rule
    three times:

    * **The windows** come from `event_eval.load_events_file`, whose path is
      `--events`. Boundaries are never constants in evaluator code, and a
      command that defaulted the path would be naming Track A's layout.
    * **The tau family** comes from `data.load_stress_thresholds`, whose path is
      `--thresholds`. `AGENT_CONTRACT.md` declares `{5, 10, 20, 50}` bp and
      Track A's file carries it; this module contains no tau.
    * **The purge gap** comes from `registry.max_release_lag_days` over the
      `(source, field)` pairs `contract.field_sources_for_features` derives
      from `--feature`, exactly as the rolling path sizes it -- literally the
      same `baseline._derive_purge` call. The two evaluation paths mean the same thing
      by a gap and take the number from the same place, by the same derivation
      -- and, since this block, in the same place: `evaluate_event_window`
      derives it, and this command passes the declaration rather than the gap.

    **There is no `--purge`.** A flag that set it by hand would be a way to
    shrink the gap at the one moment shrinking it is tempting -- when the
    training set that cleared it turned out to be too short -- and the row it
    would admit is a row published after the window opened.

    **And no `--source`.** The gap is a function of which sources the features
    come from, and which sources the features come from is a function of the
    features -- declared once, in `contract.FEATURE_SOURCES`, which neither
    track may edit. Naming sources by hand was the remaining way to size a gap
    that did not cover what the model reads, and it was the way that left no
    trace: the arithmetic is right, the reported number looks right, and the
    only thing wrong is the set it ranged over.

    * **The model** comes from `--model`, which is required and has no default.
      That is a fourth instance of the same rule and the sharpest one, because
      the default a convenience would pick is the climatology --
      `AGENT_CONTRACT.md`, "Metrics": "Brier skill score **against
      climatology**". A default that is the comparison baseline is precisely
      how a run meaning to score a conditional model publishes the baseline's
      numbers under that model's name, in a journal record whose every other
      field is correct. `--events` and `--thresholds` are already required with
      the reasoning "no default, it is not ours to name"; this is the same
      argument about a different kind of choice.

    **The selection happens before the panel is read.** A refused `--model`
    must leave no journal record behind, for the reason a refused backtest
    leaves no report: a record on disk is a claim that a scoring happened.

    Reruns are visible, not blocked. `event_eval` appends a record per scoring
    and refuses to deduplicate; whether a second run was authorised is a
    question for the human reading the journal, and this command does not
    invent an answer it was not given either.
    """

    model_name, fit_predict = _select_model(args)

    rows = load_daily_panel(args.panel)

    declaration = load_stress_thresholds(args.thresholds)
    taus = tuple(float(tau) for tau in declaration["taus_bp"])

    windows = load_events_file(args.events)
    if args.window:
        declared = {window.name: window for window in windows}
        unknown = [name for name in args.window if name not in declared]
        if unknown:
            raise SplitError(
                f"{args.events} declares no window named {', '.join(unknown)}; "
                f"it declares {', '.join(sorted(declared))}"
            )
        windows = tuple(declared[name] for name in args.window)

    # The gap is no longer computed here. `evaluate_event_window` derives it
    # from the declared feature set -- over `(source, field)` pairs, through
    # `baseline._derive_purge`, which the rolling path calls too -- so the
    # number in `model_config` and the number the run was purged at cannot be
    # two numbers. The sources are still derived here, and now *only* for the
    # hash: `_derived_sources` stays on `contract.sources_for_features`
    # deliberately, because the hash identifies a scoring run and moving it
    # would make every existing journal record look like a different run for a
    # reason that has nothing to do with what was scored. The pairs the gap was
    # actually sized over are reported from `report.field_sources` below.
    sources = _derived_sources(args)
    model_config = {
        # The selected name, and the one the caller passed. Not re-derived from
        # the constructed predictor: `model_config` is hashed into the
        # append-only journal, and the journal's own help string says a scoring
        # that is not recorded did not happen. A scoring recorded as a
        # different model is worse than one not recorded, because it is
        # recorded -- so this field is the request, not a reconstruction of it.
        "model": model_name,
        "minimum_history": args.minimum_history,
        "taus_bp": list(taus),
        "features": sorted(args.feature),
        "sources": sorted(sources),
    }
    if args.regime_variable is not None:
        # Only when one was declared, so a climatology run hashes to exactly
        # what it hashed to before this command could select anything -- every
        # existing journal record has to stay readable as a comparison.
        #
        # It is carried because it is the one thing a reader cannot recover
        # from the fields above: the regressors follow from `features` by the
        # rule in `_select_model`, but which declared column chooses the regime
        # does not, so two threshold runs over one feature set would otherwise
        # hash identically while fitting different models.
        model_config["regime_variable"] = args.regime_variable

    reported = []
    for window in windows:
        report = evaluate_event_window(
            rows,
            fit_predict,
            window,
            features=args.feature,
            registry=_registry(args),
            decision_time=time.fromisoformat(args.decision_time),
            taus=taus,
            model_config=model_config,
            journal_path=args.journal,
        )
        reported.append(
            {
                "window": {
                    "name": report.window.name,
                    "start": report.window.start.isoformat(),
                    "end": report.window.end.isoformat(),
                    "checksum": report.window.checksum,
                },
                "holdout_role": report.record.holdout_role,
                # Which model produced the curves below. Reported for the
                # reason `features` and `sources` are: a reader of stdout
                # should not have to open the journal -- and here they could
                # not, because the journal carries the hash of `model_config`
                # rather than `model_config` itself.
                "model": model_name,
                "purge_days": report.purge_days,
                # The declaration and what it resolved to, beside the gap they
                # produced. The journal carries them inside the hashed
                # `model_config`; a reader of stdout should not have to open the
                # journal to see which feature set this window was scored under.
                # Read off the report, as on the rolling path, so what is
                # printed is what shaped the run.
                "features": sorted(report.features),
                "sources": sorted(report.sources),
                "fields": [
                    f"{source}.{field}"
                    for source, field in sorted(report.field_sources)
                ],
                "train_rows": report.train_rows,
                "last_train_date": report.last_train_date.isoformat(),
                "taus_bp": list(report.taus),
                # The exceedance curve and the realized path, and nothing that
                # aggregates them. AGENT_CONTRACT.md, "Metrics": "Event windows
                # get the exceedance curve and realized path. No aggregate Brier
                # or reliability number on a single event window." Ten stressed
                # days cannot support a calibration statistic, and one printed
                # here would be averaged into the main table by whoever read the
                # two as the same kind of number.
                "days": [
                    {
                        "date": when.isoformat(),
                        "realized_bps": realized,
                        "exceedance": list(curve),
                        # The row the curve was conditioned on. A curve without
                        # it cannot be told from a hindsight by a reader.
                        "feature_date": feature.isoformat(),
                    }
                    for when, realized, curve, feature in zip(
                        report.scored_dates,
                        report.realized,
                        report.exceedance,
                        report.feature_dates,
                    )
                ],
            }
        )

    print(json.dumps(reported, indent=2, sort_keys=True))
    return 0


def _exceedance_backtest(args: argparse.Namespace) -> int:
    """Score an exceedance predictor at every purged rolling origin, and publish.

    The scoring holdout for the probabilistic target, and the first command
    that computes the number `AGENT_CONTRACT.md`'s "Metrics" section calls the
    headline: "Brier skill score against climatology, plus Murphy
    decomposition". Every part of that was implemented in `metrics.py` and
    called by nothing outside the test suite, because the only evaluator that
    consumed an `ExceedancePredictor` was `event-holdout` -- and there the
    contract forbids an aggregate. There was nowhere to compute it.

    **This is not `event-holdout` with a different flag, and the difference is
    the contract's, not an implementation detail.** `event-holdout` scores a
    knowledge holdout: crises stripped from training entirely, scored once per
    window, "reported separately and never averaged into the main table", and
    it prints the exceedance curve and the realized path and nothing that
    aggregates them. This command scores the scoring holdout: an expanding
    rolling origin over the whole panel, where a crisis date is available for
    training once it is in the past. That is where an aggregate belongs, and
    the artifact carries `holdout_role` so a reader of the file can tell the
    two apart without having read either docstring.

    **It selects through `_select_model`, the same mapping `event-holdout`
    uses.** Not a second name-to-factory table: two of those agree until they
    do not, and `tests/test_baseline.py::ExceedancePredictorCoverageTests`
    asserts `MODEL_FACTORIES` covers every discovered implementer -- a second
    mapping would be a set of names that guard cannot see. So `--model` is
    required here for the reason it is required there, and the reason is
    sharper on this command: the default a convenience would pick is the
    climatology, and on this path the climatology is not merely the honest
    baseline, it is *the reference the reported number is a ratio against*. A
    run that meant to score the ARX and got the climatology would publish a
    skill score of exactly zero and every other field would be correct.

    **No `--purge`, no `--source` and no `--taus`.** The first two for the
    reasons `_backtest` and `_event_holdout` give at length. The third for the
    reason `_event_holdout` gives: the tau family is `AGENT_CONTRACT.md`'s,
    `metadata/stress_thresholds.json` carries it, and this module contains no
    tau. It comes in through `--thresholds`, read once by
    `data.load_stress_thresholds` and passed once, because a path that reads
    the declaration twice can disagree with itself about which threshold a
    curve was produced at.

    **`--report` is required**, as it is on `backtest`, and here the argument
    is stronger. A skill score in a terminal is a figure whose reference,
    whose gap and whose fold count are gone the moment the scrollback is, and
    the next place such a figure appears is prose. The artifact is the
    publication; the human wires it to a page. Nothing here writes into a
    Markdown document.

    The document is `baseline.exceedance_backtest_document`'s. Shaping it here
    would put the schema in the caller and leave the run unable to say what it
    produced. The file is written only after the run returns: a refusal must
    leave no artifact behind, because a report on disk is a claim that a
    scoring happened.
    """

    model_name, predictor = _select_model(args)

    rows = load_daily_panel(args.panel)
    audit_panel(rows)

    declaration = load_stress_thresholds(args.thresholds)
    taus = tuple(float(tau) for tau in declaration["taus_bp"])

    report = rolling_exceedance_backtest(
        rows,
        predictor=predictor,
        model_name=model_name,
        features=args.feature,
        registry=_registry(args),
        decision_time=time.fromisoformat(args.decision_time),
        taus=taus,
        minimum_history=args.minimum_history,
    )

    # Both declaration files the run opened, identified in the record by the
    # digest of the bytes that were read.
    document = exceedance_backtest_document(
        report,
        panel_path=args.panel,
        registry_path=args.registry,
        thresholds_path=args.thresholds,
    )
    args.report.write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    # Unrounded in the file, rounded on the console, both off the one report --
    # the summary is not a second computation of anything in the document. The
    # skill score is printed per tau because that is the shape it has: one
    # number for the run would be an average over four thresholds nobody asked
    # for. `null` where it could not be computed, which on a short panel is the
    # common and correct answer at the upper taus.
    print(
        json.dumps(
            {
                "holdout_role": report.holdout_role,
                "model": report.model_name,
                "scored_days": len(report.scored_dates),
                "fold_count": len(report.folds),
                "brier_skill_score": {
                    f"{metric.tau_bp:g}": (
                        None
                        if metric.brier_skill_score is None
                        else round(metric.brier_skill_score, 4)
                    )
                    for metric in report.metrics
                },
                "features": sorted(report.features),
                "purge_days": report.purge_days,
                "sources": sorted(report.sources),
                "fields": [
                    f"{source}.{field}" for source, field in sorted(report.field_sources)
                ],
                "minimum_history": args.minimum_history,
                "report": str(args.report),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def register(subparsers: argparse._SubParsersAction) -> None:
    """Add the model and evaluation subcommands to the shared parser."""

    backtest = subparsers.add_parser(
        "backtest", help="run the purged rolling-origin benchmark"
    )
    backtest.add_argument("path", type=Path)
    backtest.add_argument("--minimum-history", type=int, default=20)
    backtest.add_argument("--registry", type=Path, required=True)
    backtest.add_argument(
        "--feature",
        action="append",
        required=True,
        metavar="COLUMN",
        help="a panel column the model reads, repeatable; these derive the "
        "sources, which size the purge gap",
    )
    backtest.add_argument("--decision-time", required=True, metavar="HH:MM")
    backtest.add_argument(
        "--model",
        required=True,
        metavar="NAME",
        help="which continuous model to fit at every origin, one of "
        + _fitter_names()
        + "; required with no default, because the default would be "
        "persistence and persistence is the benchmark every other model here "
        "is asked to beat",
    )
    backtest.add_argument(
        "--regime-variable",
        metavar="COLUMN",
        default=None,
        help="the column a two-regime model reads to choose a regime: a panel "
        "column, or spread_bps, which is computed from sofr and iorb; "
        "required for --model threshold, refused for the others, and it must "
        "be one of --feature",
    )
    backtest.add_argument(
        "--residual-window",
        type=int,
        metavar="N",
        default=None,
        help="how many trailing one-step residuals the fitted law is read "
        "from; required for --model rolling-residual, refused for the others. "
        "No default: it decides how much history the reported interval is a "
        "statement about. Not spelled --window, which means a declared event "
        "window on event-holdout",
    )
    backtest.add_argument(
        "--report",
        type=Path,
        required=True,
        metavar="PATH",
        help="where to write the JSON benchmark record; required, because a "
        "run whose figures exist only in a terminal is what this command was "
        "changed to stop",
    )
    # No --purge and no --source. See _backtest. `--model` carries no default
    # either, and for a reason of the same kind: see _select_fitter.
    backtest.set_defaults(handler=_backtest)

    compare = subparsers.add_parser(
        "compare",
        help="score two continuous models at the same origins and interval "
        "the paired difference",
    )
    compare.add_argument("path", type=Path)
    compare.add_argument("--minimum-history", type=int, default=20)
    compare.add_argument("--registry", type=Path, required=True)
    compare.add_argument("--decision-time", required=True, metavar="HH:MM")
    for side in ("a", "b"):
        compare.add_argument(
            f"--model-{side}",
            required=True,
            metavar="NAME",
            help=f"the {side} side of the comparison, one of "
            + _fitter_names()
            + "; required with no default, because a defaulted side would "
            "compare persistence against itself under the other model's name "
            "and report a difference of zero that looks like a clean run",
        )
        compare.add_argument(
            f"--feature-{side}",
            action="append",
            required=True,
            metavar="COLUMN",
            help=f"a panel column the {side} model reads, repeatable; these "
            "derive that side's sources, which size its purge gap. The two "
            "sides must price the same gap or the run is refused: a different "
            "gap is a different set of origins, and losses at different "
            "origins are not paired",
        )
        compare.add_argument(
            f"--regime-variable-{side}",
            metavar="COLUMN",
            default=None,
            help=f"the panel column the {side} model reads to choose a "
            f"regime; required for --model-{side} threshold, refused for the "
            f"others, and it must be one of --feature-{side}",
        )
        compare.add_argument(
            f"--residual-window-{side}",
            type=int,
            metavar="N",
            default=None,
            help=f"how many trailing one-step residuals the {side} model's "
            f"law is read from; required for --model-{side} rolling-residual, "
            f"refused for the others. Per side, because a window against the "
            f"full sample is the comparison this model exists for",
        )
    compare.add_argument(
        "--loss",
        choices=sorted(COMPARISON_LOSSES),
        default=DEFAULT_COMPARISON_LOSS,
        help="what the paired difference is a difference of. "
        "absolute-error is the default and the behaviour every published "
        "record was produced under; crps scores each side's whole quantile "
        "forecast through the same metric --model backtests report, so two "
        "models sharing a point rule and differing in their law -- "
        "persistence against rolling-residual -- are separated instead of "
        "reported as identical. Coverage is deliberately not offered: an "
        "infinitely wide interval covers every origin, so a paired coverage "
        "difference rewards the model that says least",
    )
    compare.add_argument(
        "--report",
        type=Path,
        required=True,
        metavar="PATH",
        help="where to write the JSON comparison record; required, because a "
        "signed difference whose sign convention, gap and origin count exist "
        "only in a terminal is the figure the next document carries as prose",
    )
    # No --purge and no --source, on either side. See _compare: the obvious way
    # to make two declarations comparable is to overrule one of them, and that
    # is exactly what must not be available here.
    compare.set_defaults(handler=_compare)


    exceedance = subparsers.add_parser(
        "exceedance-backtest",
        help="score an exceedance predictor at every purged rolling origin",
    )
    exceedance.add_argument("--panel", type=Path, required=True)
    exceedance.add_argument("--thresholds", type=Path, required=True)
    exceedance.add_argument("--registry", type=Path, required=True)
    exceedance.add_argument(
        "--feature",
        action="append",
        required=True,
        metavar="COLUMN",
        help="a panel column the model reads, repeatable; these derive the "
        "sources, which size the purge gap",
    )
    exceedance.add_argument("--decision-time", required=True, metavar="HH:MM")
    exceedance.add_argument(
        "--model",
        required=True,
        metavar="NAME",
        help="which exceedance predictor to score, one of "
        + _model_names()
        + "; required with no default, because the default would be the "
        "climatology and on this command the climatology is the reference the "
        "reported skill score is a ratio against",
    )
    exceedance.add_argument(
        "--regime-variable",
        metavar="COLUMN",
        default=None,
        help="the column a two-regime model reads to choose a regime: a panel "
        "column, or spread_bps, which is computed from sofr and iorb; "
        "required for --model threshold, refused for the others, and it must "
        "be one of --feature",
    )
    exceedance.add_argument("--minimum-history", type=int, default=20)
    exceedance.add_argument(
        "--report",
        type=Path,
        required=True,
        metavar="PATH",
        help="where to write the JSON evaluation record; required, because a "
        "skill score whose reference, gap and fold count exist only in a "
        "terminal is a figure the next document will carry as prose",
    )
    # No --purge, no --source and no --taus. See _exceedance_backtest.
    exceedance.set_defaults(handler=_exceedance_backtest)

    holdout = subparsers.add_parser(
        "event-holdout",
        help="score declared knowledge-holdout windows, once each",
    )
    holdout.add_argument("--panel", type=Path, required=True)
    holdout.add_argument(
        "--events",
        type=Path,
        required=True,
        help="the declared event-window file; no default, it is not ours to name",
    )
    holdout.add_argument("--thresholds", type=Path, required=True)
    holdout.add_argument("--registry", type=Path, required=True)
    holdout.add_argument(
        "--journal",
        type=Path,
        required=True,
        help="append-only provenance log; a scoring that is not recorded did not happen",
    )
    holdout.add_argument(
        "--feature",
        action="append",
        required=True,
        metavar="COLUMN",
        help="a panel column the model reads, repeatable; these derive the "
        "sources, which size the purge gap",
    )
    holdout.add_argument("--decision-time", required=True, metavar="HH:MM")
    holdout.add_argument(
        "--model",
        required=True,
        metavar="NAME",
        help="which exceedance predictor to run, one of "
        + _model_names()
        + "; required with no default, because the default would be the "
        "climatology and the climatology is the reference a skill score is "
        "measured against",
    )
    holdout.add_argument(
        "--regime-variable",
        metavar="COLUMN",
        default=None,
        help="the column a two-regime model reads to choose a regime: a panel "
        "column, or spread_bps, which is computed from sofr and iorb; "
        "required for --model threshold, refused for the others, and it must "
        "be one of --feature so that what the predictor is handed and what the "
        "run declared are the same set",
    )
    holdout.add_argument(
        "--window",
        action="append",
        metavar="NAME",
        help="score only this declared window, repeatable; default is all of them",
    )
    holdout.add_argument("--minimum-history", type=int, default=20)
    # No --purge and no --source. See _event_holdout. `--model` carries no
    # default either, and for a reason of the same kind: see _select_model.
    holdout.set_defaults(handler=_event_holdout)
