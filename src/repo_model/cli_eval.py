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
import json
from dataclasses import dataclass
from datetime import time
from pathlib import Path
from types import MappingProxyType
from typing import Callable, Optional, Tuple

from .baseline import (
    ExceedancePredictor,
    arx_exceedance,
    backtest_document,
    climatology_exceedance,
    exceedance_backtest_document,
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
class _ModelChoice:
    """One `--model` name, and how the predictor behind it is constructed.

    The three factories have different signatures --
    `climatology_exceedance(minimum_history)`,
    `arx_exceedance(regressors, minimum_history)`,
    `threshold_exceedance(regressors, threshold_variable, minimum_history)` --
    so the mapping has to carry construction and cannot be a name-to-callable
    table.

    `factory` is the `baseline` factory itself, and `build` is handed that same
    object rather than closing over one of its own. The two therefore cannot
    name different models: `tests/test_baseline.py`'s
    `ExceedancePredictorCoverageTests` reads `factory` to assert every
    discovered implementer is reachable from here, and a `build` free to call
    something else would make that assertion a statement about a field nobody
    runs.
    """

    factory: Callable[..., ExceedancePredictor]
    build: Callable[..., ExceedancePredictor]
    needs_regime_variable: bool

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
#: than by a second guard beside it. A fourth implementer the command line
#: cannot run then fails an existing test instead of going unnoticed.
MODEL_FACTORIES = MappingProxyType(
    {
        "climatology": _ModelChoice(
            factory=climatology_exceedance,
            build=lambda factory, regressors, regime, minimum_history: factory(
                minimum_history=minimum_history
            ),
            needs_regime_variable=False,
        ),
        "arx": _ModelChoice(
            factory=arx_exceedance,
            build=lambda factory, regressors, regime, minimum_history: factory(
                regressors, minimum_history=minimum_history
            ),
            needs_regime_variable=False,
        ),
        "threshold": _ModelChoice(
            factory=threshold_exceedance,
            build=lambda factory, regressors, regime, minimum_history: factory(
                regressors, regime, minimum_history=minimum_history
            ),
            needs_regime_variable=True,
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

    declared = tuple(sorted(args.feature))
    regime_variable = args.regime_variable

    if choice.needs_regime_variable:
        if regime_variable is None:
            raise SplitError(
                f"--model {name} reads a regime variable off each row to choose "
                "which of two fitted relationships produces the centre, and "
                "--regime-variable names no column. It is required and "
                "undefaulted for the reason the column is: it does not merely "
                "contribute a term, it chooses the model"
            )
        if regime_variable not in declared:
            raise SplitError(
                f"--regime-variable {regime_variable} is not one of the declared "
                f"features {list(declared)}. The purge is sized over the "
                "declaration before anything is fitted, so a regime variable "
                "outside it would have its release lag missing from the gap -- "
                f"declare it with --feature {regime_variable} rather than "
                "reading a column the run did not declare"
            )
    elif regime_variable is not None:
        raise SplitError(
            f"--regime-variable {regime_variable} was given, but --model {name} "
            "reads no regime variable. A flag that is accepted and ignored is "
            "read by the next person as a setting that took effect"
        )

    regressors = tuple(
        column
        for column in declared
        if column != _AUTOREGRESSIVE_TERM and column != regime_variable
    )
    return name, choice.construct(
        regressors=regressors,
        regime_variable=regime_variable,
        minimum_history=args.minimum_history,
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

    rows = load_daily_panel(args.path)
    audit_panel(rows)
    report = rolling_persistence_backtest(
        rows,
        features=args.feature,
        registry=_registry(args),
        decision_time=time.fromisoformat(args.decision_time),
        minimum_history=args.minimum_history,
    )

    document = backtest_document(report, panel_path=args.path)
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

    document = exceedance_backtest_document(report, panel_path=args.panel)
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
        "--report",
        type=Path,
        required=True,
        metavar="PATH",
        help="where to write the JSON benchmark record; required, because a "
        "run whose figures exist only in a terminal is what this command was "
        "changed to stop",
    )
    # No --purge and no --source. See _backtest.
    backtest.set_defaults(handler=_backtest)

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
        help="the panel column a two-regime model reads to choose a regime; "
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
        help="the panel column a two-regime model reads to choose a regime; "
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
