"""The knowledge holdout: crises stripped from training entirely.

`AGENT_CONTRACT.md`, "Two holdout roles", separates two things that one word
for both would conflate, and requires that they stay separate in code and in
reporting:

1. **Scoring holdout** -- crisis dates excluded from the headline metric but
   available for training once they are in the past. This is the deployable
   model, and it is produced by `repo_model.splits.rolling_origin`.
2. **Knowledge holdout** -- crises stripped from training entirely, scored once
   per window. An extrapolation check, reported separately and never averaged
   into the main table. This module produces it, and produces nothing else.

The contract adds that the knowledge holdout is "produced by event_eval, not by
a splitter flag", and the reason is the shape of a rolling-origin fold rather
than a preference about where code lives. The training window expands, so by
the time a later fold scores March 2020 it has already trained on September
2019, and the score answers "can this model forecast a repo spike having seen
one" rather than "having seen a calm history". Those are different claims. The
first is the scoring holdout's and is the honest one to deploy on; the second
is the knowledge holdout's, and no configuration of an expanding splitter
produces it.

So this is an evaluator, not a splitter mode. It trains strictly on rows that
precede the event by more than the purge gap, scores the knowledge-holdout
window once, and records that it did.

What this module scores, and what it is conditioned on
-----------------------------------------------------

`ExceedancePredictor` is `repo_model.baseline`'s, imported. It used to be
declared here as well, as `FitPredict` -- two identical `Callable` aliases in
two modules, which is two vocabularies for one thing. It is declared once now,
beside the models that implement it, and this module imports the alias, the
`ExceedanceCurves` it returns, and the two guards both evaluation paths share.
That is the only thing this module knows about `baseline`: the predictor is
still a parameter, and no model is named here.

The old shape passed one series of values, so **no covariate could reach a
model through it**. The only predictor expressible was one conditioning on
nothing, which is the climatology -- and a climatology is the baseline a Brier
skill score is measured *against*, so the one evaluation this repository was
designed around had nothing on the other side of the comparison. The shape now
carries `DailyObservation` rows, which is what a covariate travels in.

Widening it opens a door for covariates, which is the door the purged backtest
built a lock for one level up: a covariate that reaches a model without being
declared means the gap was sized over the wrong sources, computed correctly and
in the flattering direction. So this module derives its gap from a declared
feature set exactly as `rolling_persistence_backtest` does, and checks the
predictor's `features_read` against that declaration after the fit, through
`baseline._check_fitter_stayed_inside` -- the same guard, imported, not a second
one.

The evaluator also chooses the feature rows, one per scored day, by the as-of
rule (`asof.InformationRule.observation`): each declared field at its latest
value observable at that day's decision instant. A predictor handed the panel could read the scored day itself; a
predictor handed only the last training row could not produce a curve that
moves, and a curve that cannot move is indistinguishable from the climatology's.
The training boundary and the conditioning boundary are different questions --
the first is sized against `window.start` and the second against each scored day
-- and they are asked separately here.

Relationship to `repo_model.splits`
-----------------------------------

The training boundary is the as-of rule's label observability
(`repo_model.asof`), the same rule the rolling paths use, imported, not
restated. `LookAheadError` is likewise the splitter's, so a leak raises the same type
whichever evaluation path found it, and for the same reason it is a raise and
never an `assert`: `python -O` strips asserts, and a guard that vanishes under
an optimisation flag is not a guard.

What this module deliberately does not own
------------------------------------------

The stress label. `AGENT_CONTRACT.md`, "Ownership", puts "the label column and
its point-in-time rule" with the data layer, and `CLAUDE.md` puts it outside
Track B in as many words. A `trailing_percentile` lived here for one commit,
implementing the contract's secondary trailing-window rule so that the label at
an event boundary could be shown to use pre-event rows only. It was a second
implementation of a Track A rule, which is prohibited even as a stopgap and for
a good reason -- two implementations of a point-in-time rule agree until they
do not, and the disagreement surfaces as a scoring result nobody can explain.
It was deleted, and the property it demonstrated now lives as
`tests/test_contract.py::TargetSchemaTests::test_the_stress_label_is_point_in_time_and_never_full_sample`,
an `expectedFailure` spec Track A must satisfy.

What this module deliberately does not compute
----------------------------------------------

No Brier score, no reliability curve, no aggregate skill number of any kind.
The contract is explicit -- "Event windows get the exceedance curve and
realized path. No aggregate Brier or reliability number on a single event
window" -- and the arithmetic behind that ruling is that a knowledge-holdout
window is on the order of ten stressed days. A calibration statistic
over ten points is dominated by its own sampling error, and reporting one
invites exactly the comparison it cannot support -- across events, across model
versions, across reruns -- while looking like evidence. It would also be the
exact conflation the two-role split exists to prevent: a number from here,
formatted like a number from the scoring holdout, averaged into the main table
by whoever reads the two as the same kind of thing. What the report carries is
the predicted exceedance curve over the tau family for each scored day and
the realized path beside it. That is an extrapolation check: did the predictive
distribution put weight where the event actually went. Reading it takes a human
looking at a curve, which is the honest cost of a ten-day sample.

The metrics in `repo_model.metrics` are the scoring holdout's. If a metric is
wanted for knowledge-holdout windows later it belongs to a pooled evaluation
over many windows, declared in advance, not to this function.

Run-once discipline
-------------------

A knowledge-holdout window is scored once per window. The contract's open
decision asks how many times that is in practice and who authorises it. This module cannot answer that, and does not try to enforce
an answer it was not given: `journal_path` is required, every evaluation
appends a record, and the journal is append-only. Reruns are therefore visible
-- a second record for the same window is a fact in the file, timestamped, with
the git rev and a hash of the model config that produced it. Whether a second
run was permitted is a question for the human reading that file, not a rule
this code invents.
"""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple

from .baseline import (
    KNOWLEDGE_HOLDOUT,
    SCORING_HOLDOUT,
    ExceedancePredictor,
    _check_decision_relative_availability,
    _check_fitter_stayed_inside,
    _check_history_ends,
    _ml_libraries,
    _reads_histories,
    _reads_information,
    _resolve_fields,
    _validate_prediction,
    _validate_taus,
)
from .asof import InformationRule, information_summary
from .contract import (
    EVENT_WINDOW_KEYS,
    event_window_digest,
    validate_event_windows_document,
)
from .data import DailyObservation
from .splits import (
    LookAheadError,
    SplitError,
    ensure_strictly_ascending,
)


__all__ = [
    "KNOWLEDGE_HOLDOUT",
    "SCORING_HOLDOUT",
    "EvaluationRecord",
    "EventWindow",
    "EventWindowReport",
    "LookAheadError",
    "SplitError",
    "append_record",
    "config_digest",
    "evaluate_event_window",
    "load_event_windows",
    "load_events_file",
    "read_journal",
]


# The two holdout roles are `baseline.SCORING_HOLDOUT` and
# `baseline.KNOWLEDGE_HOLDOUT`, imported above and re-exported in `__all__` so
# that every existing importer of this module is unaffected. They moved when
# the rolling exceedance path arrived and became the first producer of the
# other role: two modules each spelling one half of a two-valued distinction is
# how the halves come to disagree, and `baseline` is the module this one
# already imports from rather than the reverse. `SCORING_HOLDOUT` is still
# unused *here*, and now for a stated reason rather than for want of a second
# path: this module produces knowledge holdouts and only those.




@dataclass(frozen=True)
class EventWindow:
    """One declared knowledge-holdout window.

    Comes from metadata, never from code. The contract: "Event window
    boundaries are frozen in versioned, checksummed metadata/events.json ...
    Boundaries are never constants in evaluator code -- moving a window edge is
    the realistic cherry-pick, not swapping window type."
    """

    name: str
    start: date
    end: date
    checksum: str

    def __post_init__(self) -> None:
        """Reject a window that is not pinned, at construction.

        `evaluate_event_window` takes one of these rather than loose dates
        precisely so that the checks live here: the type is then the guarantee,
        and there is no argument list in which a caller can supply boundaries
        without also supplying the checksum that says which declaration they
        came from. `load_event_windows` validates the same things earlier and
        with the position in the file in the message; this is the backstop for
        a window built by hand.
        """

        for field, value in (("start", self.start), ("end", self.end)):
            if not isinstance(value, date) or isinstance(value, datetime):
                raise SplitError(f"window {field} must be a date, got {value!r}")
        if not str(self.name).strip():
            raise SplitError("window has no name")
        if self.end < self.start:
            raise SplitError(
                f"window {self.name!r} ends {self.end} before it starts {self.start}"
            )
        if not str(self.checksum).strip():
            raise SplitError(
                f"window {self.name!r} has no checksum; an unpinned window cannot "
                "be shown to be the window that was declared, and scoring one "
                "spends a single-evaluation budget on nothing in particular"
            )


@dataclass(frozen=True)
class EvaluationRecord:
    """Provenance for one scoring of one window. Append-only, never amended.

    `holdout_role` is on the record because the contract requires the two roles
    stay distinct "in code or in reporting", and the journal is reporting. A
    reader of the file should not have to know which module wrote a line to
    know whether the number beside it may be averaged into the main table.

    `ml_libraries` is the numpy and scikit-learn versions the window's fit was
    made with, read off the `ExceedanceCurves` that fit returned by
    `baseline._ml_libraries` -- the reader the rolling records use -- and never
    off the environment. A line from a fit that reached no third-party library
    has no such key: absent, not `null`, for the reason `_run_provenance` gives
    on the rolling path. The versions are **not** in `config_sha256`. The hash
    identifies the scoring configuration, and a rerun under a newer
    scikit-learn is a rerun of the same configuration, which is the thing the
    journal exists to show rather than to disguise as a different run.
    """

    evaluated_at: str
    git_rev: str
    config_sha256: str
    holdout_role: str
    window_name: str
    window_checksum: str
    window_start: str
    window_end: str
    #: The information rule the window was scored under. `"as_of"` since the
    #: as-of rule replaced the purge; journal lines written before it carry a
    #: `purge_days` instead.
    information_rule: str
    train_rows: int
    scored_rows: int
    ml_libraries: Optional[Mapping[str, str]] = None

    def as_json_line(self) -> str:
        line = dict(self.__dict__)
        if self.ml_libraries is None:
            del line["ml_libraries"]
        else:
            line["ml_libraries"] = dict(self.ml_libraries)
        return json.dumps(line, sort_keys=True)


@dataclass(frozen=True)
class EventWindowReport:
    """The result of scoring one knowledge-holdout window exactly once.

    Carries the exceedance curve and the realized path, and nothing that
    aggregates them. See the module docstring for why.
    """

    window: EventWindow
    #: The feature set the caller declared, and the two facts derived from it:
    #: the sources those features draw on and the gap those sources produced.
    #: Carried for the reason `BacktestReport` carries the same three -- a
    #: reporter that re-derived them would be a second derivation of the number
    #: that shaped the run, and the two could agree today and drift later.
    features: Tuple[str, ...]
    sources: Tuple[str, ...]
    #: The `(source_id, field)` pairs the declaration reads. The rolling
    #: path's report carries the same, from the same `_resolve_fields` call.
    field_sources: Tuple[Tuple[str, str], ...]
    #: The per-feature staleness summary over the window's scored days.
    information: Mapping[str, Any]
    train_rows: int
    last_train_date: date
    taus: Tuple[float, ...]
    scored_dates: Tuple[date, ...]
    realized: Tuple[float, ...]
    #: `exceedance[day][tau]` is the predicted `P(value > taus[tau])`.
    exceedance: Tuple[Tuple[float, ...], ...]
    #: `feature_dates[day]` is the anchor of the as-of observation the
    #: predictor read to produce `exceedance[day]`: the latest row whose
    #: target was observable at that scored day's decision instant. Reported because it is the other half of what makes a
    #: curve auditable -- a reader who can see the curve but not what it was
    #: conditioned on cannot tell a forecast from a hindsight.
    feature_dates: Tuple[date, ...]
    record: EvaluationRecord


# --------------------------------------------------------------------------
# Declared windows
# --------------------------------------------------------------------------


def load_event_windows(payload: Any) -> Tuple[EventWindow, ...]:
    """Parse already-loaded event metadata into windows, verifying each digest.

    Takes the decoded object, not a path. `metadata/events.json` is Track A's
    file, and hard-coding its location here would make this module wrong the
    moment the file moves, and would let a test pass against a fixture that no
    longer resembles the real thing. `load_events_file` is the path-taking
    entry point, and the path is *its* caller's argument for the same reason.

    Every field is required, and the `checksum` is checked rather than merely
    demanded. Requiring the key detects an author who forgot it and nothing
    else: a window whose `start` moved and whose digest did not still loaded
    and still scored, which is the edit `AGENT_CONTRACT.md`, "Decided: the
    event-window checksum", says the checksum exists to catch. The digest is
    `repo_model.contract.event_window_digest`, imported rather than restated --
    a second correct reading of a shared shape is the collision that decision
    was written to end, and it agrees until it does not.

    The digest is computed over the ISO strings **as written**, never over the
    parsed dates: what is hashed has to be what the file carries, without a
    parse step in between that could normalise one and not the other.
    """

    if isinstance(payload, Mapping):
        entries = payload.get("windows")
        if entries is None:
            raise SplitError("event metadata has no 'windows' key")
    else:
        entries = payload
    if not isinstance(entries, (list, tuple)) or not entries:
        raise SplitError("event metadata declares no windows")

    windows = []
    seen = set()
    for position, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            raise SplitError(f"window {position} is not an object")
        missing = [key for key in EVENT_WINDOW_KEYS if key not in entry]
        if missing:
            raise SplitError(f"window {position} is missing {', '.join(missing)}")
        try:
            start = date.fromisoformat(str(entry["start"]))
            end = date.fromisoformat(str(entry["end"]))
        except ValueError as exc:
            raise SplitError(f"window {position} has a non-ISO date") from exc
        if end < start:
            raise SplitError(f"window {entry['name']!r} ends {end} before it starts {start}")
        name = str(entry["name"])
        if name in seen:
            raise SplitError(f"duplicate window name {name!r}")
        seen.add(name)

        checksum = str(entry["checksum"])
        for key in ("name", "start", "end"):
            if not isinstance(entry[key], str):
                raise SplitError(
                    f"window {name!r} has a non-string {key}: {entry[key]!r}; the "
                    "digest is taken over the strings the file carries, so a "
                    "value that was not written as one cannot be verified"
                )
        expected = event_window_digest(entry["name"], entry["start"], entry["end"])
        if checksum != expected:
            raise SplitError(
                f"window {name!r} checksum {checksum!r} does not match its "
                f"boundaries; expected {expected!r}. Either an edge moved "
                "without the digest being recomputed, or the digest is not "
                "event_window_digest(name, start, end)"
            )

        windows.append(EventWindow(name, start, end, checksum))
    return tuple(windows)


def load_events_file(path: Path) -> Tuple[EventWindow, ...]:
    """Read one declared event-window file and return its windows.

    `path` is the caller's argument and has no default. `metadata/events.json`
    is Track A's file; model-eval naming its location would be model-eval
    deciding Track A's layout, which is the reason `load_event_windows` takes a
    payload rather than a path in the first place. That reasoning did not
    expire when the file became real -- it is exactly then that a hard-coded
    location starts being obeyed.

    The document is checked against `contract.validate_event_windows_document`,
    which reports every fault at once rather than raising on the first, so a
    malformed file is fixed in one pass instead of one key per run. If anything
    is wrong the raise names all of it; the per-window digest is then verified
    again by `load_event_windows`, which is not redundant -- the bare-list form
    reaches that check without passing through this function at all.

    Raises:
        SplitError: the document does not conform, in any respect.
    """

    location = Path(path)
    payload = json.loads(location.read_text(encoding="utf-8"))
    problems = validate_event_windows_document(payload)
    if problems:
        raise SplitError(
            f"{location} does not conform to the event-window contract:\n  - "
            + "\n  - ".join(problems)
        )
    return load_event_windows(payload)


# --------------------------------------------------------------------------
# Evaluation
# --------------------------------------------------------------------------


def evaluate_event_window(
    observations: Sequence[DailyObservation],
    fit_predict: ExceedancePredictor,
    window: EventWindow,
    *,
    features: Sequence[str],
    registry: Mapping[str, Mapping[str, Any]],
    decision_time: time,
    taus: Sequence[float],
    model_config: Mapping[str, Any],
    journal_path: Path,
) -> EventWindowReport:
    """Score one knowledge-holdout window: train strictly before it, once.

    The training set is the as-of rule's frame at the decision instant before
    the window's first scored day -- every label observable then, with each
    declared column a hole where its value was not yet public -- and nothing
    else. The event is stripped from training rather than merely withheld from
    the headline metric, which is what makes this the knowledge holdout and
    not the scoring one.

    **The rule is the rolling paths' rule.** `asof.InformationRule`, built
    from the declared feature set, the registry and the decision time; there
    is no gap argument, and nothing here reads a `release_lag` itself. Every
    scored day's reads are checked both ways (`InformationRule.check`) and per
    read by `baseline._check_decision_relative_availability`.

    **Declaration, then verification.** The predictor reports
    `ExceedanceCurves.features_read` after the fit and it is checked against
    the declaration by `baseline._check_fitter_stayed_inside`, the guard the
    rolling path uses. A predictor that exceeded the declaration raises
    `LookAheadError`.

    **What the predictor is conditioned on.** For each scored day the
    evaluator builds that day's as-of observation itself: each declared field
    at its latest value observable at the day's own decision instant, and
    scheduled inputs at the day. A row inside the window is therefore readable
    as a feature for a later day in it, once public, and never as a training
    row. That is what an extrapolation check is: a model that never saw a
    crisis, forecasting through one on the information a forecaster would
    actually have held. Passing the feature rows rather than letting the
    predictor choose is the guard: a predictor handed the panel could read the
    scored day itself.

    Args:
        observations: the panel, strictly ascending and unique by date. The
            target is `row.spread_bps`, the target the rolling paths score.
        fit_predict: an `ExceedancePredictor`, called once with the training
            rows, the feature rows and `taus` -- with `information=` the run's
            rule when its signature names that parameter, by
            `baseline._reads_information`, and with `histories=` each day's
            as-of history when it names that one, by
            `baseline._reads_histories`. Returns `ExceedanceCurves`.
        window: the declared knowledge-holdout window, inclusive at both ends,
            as an `EventWindow` from `load_event_windows`, so no unpinned
            window can be scored.
        features: the panel columns the predictor is declared to read.
            **Required, keyword-only, with no default**, exactly as on the
            rolling path.
        registry: the parsed source registry; every read's availability is
            its declaration.
        decision_time: when the forecast is made. Required and undefaulted.
        taus: the exceedance family, strictly ascending.
        model_config: hashed into the evaluation record, so a rerun with
            different settings is distinguishable from a repeat of the same one.
            The library versions a fit reports are recorded beside the hash,
            never inside it; see `EvaluationRecord`.
        journal_path: append-only provenance log. Required.

    Raises:
        SplitError: malformed panel, window, taus or predictions, or a window
            with no observable label before it.
        LookAheadError: a read is newer than its decision instant, the
            training set reaches past the window's first anchor or into the
            window, the scored rows are not exactly the declared window, or
            the predictor read a column outside `features`, or a positional
            read ends after its day's anchor.
        StaleReadError: a read is older than the latest admissible value, or
            a positional read ends before its day's anchor.
        UndeclaredFeatureError: `features` names a column
            `contract.field_sources_for_features` cannot classify, or one
            declared to have no ingesting source. Raised before any row is
            selected.
        RegistryContractError: a declared field has no availability the rule
            can read.
    """

    # Before any row is selected: an unresolvable feature set has no
    # information set, so it has no evaluation.
    declared: Tuple[str, ...] = tuple(features)
    field_sources, sources = _resolve_fields(declared)
    rule = InformationRule(registry, declared, decision_time=decision_time)

    rows = list(observations)
    ordered_dates, values = _validate_panel(rows)
    tau_family = _validate_taus(taus)
    if not isinstance(window, EventWindow):
        raise SplitError(
            f"window must be an EventWindow from load_event_windows, got "
            f"{type(window).__name__}"
        )
    event_start, event_end = window.start, window.end

    scored_index = [
        i for i, when in enumerate(ordered_dates) if event_start <= when <= event_end
    ]
    if not scored_index:
        raise SplitError(f"no observation falls in {event_start}..{event_end}")
    if scored_index[0] < 1:
        raise SplitError(
            f"the window opens on the panel's first row, {ordered_dates[0]}, so "
            f"there is no decision instant before it to train at"
        )

    # One information set per scored day, each checked both ways. The training
    # frame is the one at the window's first decision instant: every label
    # observable before the window opened, and nothing else.
    infos = [rule.information_set(ordered_dates, index) for index in scored_index]
    for info in infos:
        rule.check(ordered_dates, info)
        for read in info.reads:
            _check_decision_relative_availability(
                registry,
                read.fields,
                ordered_dates,
                read.row,
                info.scored_index,
                decision_time=decision_time,
            )
    train_rows = tuple(rule.frame(rows, infos[0]))
    train_index = list(range(len(train_rows)))
    if not train_index:
        raise SplitError(
            f"no training label is observable at the decision before {event_start}"
        )

    _assert_window_is_clean(
        ordered_dates, train_index, scored_index, event_start, event_end, infos[0].anchor
    )

    # One feature row per scored day, chosen here and not by the predictor: the
    # day's as-of observation. A day late in the window may read a row from
    # earlier in the window, and never one unobservable at its own decision.
    feature_index = [info.anchor for info in infos]
    _assert_feature_rows_precede_their_days(ordered_dates, feature_index, scored_index)
    feature_rows = tuple(rule.observation(rows, info) for info in infos)

    # A predictor that names `information` -- `ml.gbm_exceedance`, whose
    # calibration scores held-out rows as forecasts -- is handed the run's
    # rule. One that names `histories` -- `ml.gbm_exceedance` again, whose
    # lags, GARCH variance and trailing scale are read by position -- is handed
    # each day's own as-of history, the frame at that day's decision ending at
    # its anchor (#57), as the rolling paths do. The training rows stay the
    # first day's frame. Every other predictor is called exactly as it always
    # was.
    keywords: Dict[str, Any] = {}
    if _reads_information(fit_predict):
        keywords["information"] = rule
    if _reads_histories(fit_predict):
        keywords["histories"] = tuple(rule.frame(rows, info) for info in infos)
    prediction = fit_predict(train_rows, feature_rows, tau_family, **keywords)
    exceedance = _validate_prediction(prediction, len(scored_index), tau_family)
    # Each day's positional read ends at that day's anchor: before it is stale,
    # after it is look-ahead (`baseline._check_history_end`).
    _check_history_ends(prediction, rows, infos)
    _check_fitter_stayed_inside(prediction.features_read, declared, sources)

    record = EvaluationRecord(
        evaluated_at=datetime.now(timezone.utc).isoformat(),
        git_rev=_git_rev(),
        config_sha256=config_digest(model_config),
        holdout_role=KNOWLEDGE_HOLDOUT,
        window_name=window.name,
        window_checksum=window.checksum,
        window_start=event_start.isoformat(),
        window_end=event_end.isoformat(),
        information_rule="as_of",
        train_rows=len(train_index),
        scored_rows=len(scored_index),
        ml_libraries=_ml_libraries(prediction),
    )
    append_record(journal_path, record)

    return EventWindowReport(
        window=window,
        features=declared,
        sources=sources,
        field_sources=field_sources,
        information=information_summary(rule, infos),
        train_rows=len(train_index),
        last_train_date=ordered_dates[train_index[-1]],
        taus=tau_family,
        scored_dates=tuple(ordered_dates[i] for i in scored_index),
        realized=tuple(values[i] for i in scored_index),
        exceedance=exceedance,
        feature_dates=tuple(ordered_dates[i] for i in feature_index),
        record=record,
    )


def _validate_panel(
    rows: Sequence[DailyObservation],
) -> Tuple[Tuple[date, ...], Tuple[float, ...]]:
    """The panel's dates and its target, or a `SplitError` naming the fault.

    Returns both rather than checking in place, so the target is read once. It
    is `row.spread_bps`, the same target the rolling path scores; the evaluator
    used to take a parallel `y` sequence, and "the dates and the values disagree
    about their length" was a fault it had to check for. One panel cannot
    disagree with itself, so that check is gone rather than relaxed.

    `spread_bps` is computed from `sofr` and `iorb`, so a row missing either
    raises where a row carrying a string used to. Both are refused, and the
    message names the row's date rather than its position: a panel is read by
    date and a position is a number the reader has to count to.
    """

    ordered = list(rows)
    if not ordered:
        raise SplitError("cannot evaluate an empty panel")
    dates = []
    values = []
    for position, row in enumerate(ordered):
        when = getattr(row, "date", None)
        if not isinstance(when, date) or isinstance(when, datetime):
            raise SplitError(f"row {position} carries no date: {row!r}")
        try:
            value = float(row.spread_bps)
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            raise SplitError(f"row {when} has no readable spread: {exc}") from exc
        if not math.isfinite(value):
            raise SplitError(f"row {when} has a non-finite spread")
        dates.append(when)
        values.append(value)
    ensure_strictly_ascending(dates)
    return tuple(dates), tuple(values)


def _assert_feature_rows_precede_their_days(
    dates: Sequence[date],
    feature_index: Sequence[int],
    scored_index: Sequence[int],
) -> None:
    """Every feature row's anchor is before the day it is read for.

    Each read is already checked both ways by `InformationRule.check`; this
    states the pairing, which the rule cannot: the row is checked against the
    scored day it was chosen for, not against the window opening.

    `LookAheadError`, never an `assert`: `python -O` strips asserts.
    """

    for feature, scored in zip(feature_index, scored_index):
        if feature >= scored:
            raise LookAheadError(
                f"the feature row for {dates[scored]} is {dates[feature]}, which "
                f"is not before it"
            )


def _assert_window_is_clean(
    dates: Sequence[date],
    train_index: Sequence[int],
    scored_index: Sequence[int],
    event_start: date,
    event_end: date,
    anchor: int,
) -> None:
    """Guard the window before anything is fitted against it.

    `anchor` is the latest row whose label was observable at the decision
    instant before the window's first scored day; no training row may be
    after it. Every check here is a leak if it fires, so every one raises.
    """

    if set(train_index) & set(scored_index):
        raise LookAheadError("a row is both trained on and scored")
    if train_index[-1] > anchor:
        raise LookAheadError(
            f"training ends {dates[train_index[-1]]}, after {dates[anchor]}, the "
            f"last label observable before the window opens {event_start}"
        )
    if train_index[-1] >= scored_index[0]:
        raise LookAheadError(
            f"training row {train_index[-1]} is not before scored row {scored_index[0]}"
        )
    for index in scored_index:
        if not event_start <= dates[index] <= event_end:
            raise LookAheadError(f"{dates[index]} is scored but outside the window")
    if list(scored_index) != list(range(scored_index[0], scored_index[-1] + 1)):
        raise LookAheadError("scored rows are not contiguous")


# --------------------------------------------------------------------------
# Provenance
# --------------------------------------------------------------------------


def config_digest(model_config: Mapping[str, Any]) -> str:
    """SHA-256 of the config, canonicalised so equal configs hash equally."""

    try:
        canonical = json.dumps(model_config, sort_keys=True, separators=(",", ":"))
    except TypeError as exc:
        raise SplitError(f"model_config is not JSON-serialisable: {exc}") from exc
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def append_record(journal_path: Path, record: EvaluationRecord) -> None:
    """Append one record. Never rewrites, never deduplicates.

    A rerun is meant to be visible, so a second record for the same window is
    written exactly like the first. Suppressing it here would hide the thing
    the journal exists to show.
    """

    path = Path(journal_path)
    if path.parent and not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(record.as_json_line() + "\n")


def read_journal(journal_path: Path) -> Tuple[Mapping[str, Any], ...]:
    """Every record in the journal, in the order written."""

    path = Path(journal_path)
    if not path.exists():
        return ()
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            entries.append(json.loads(line))
    return tuple(entries)


def _git_rev() -> str:
    """The current revision, or `"unknown"` off a checkout. Never raises."""

    try:
        finished = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(Path(__file__).resolve().parent),
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    if finished.returncode != 0:
        return "unknown"
    return finished.stdout.decode("utf-8", "replace").strip() or "unknown"
