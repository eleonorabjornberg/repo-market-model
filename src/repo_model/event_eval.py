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

The evaluator also chooses the feature rows, one per scored day, with
`baseline._feature_index`: the last panel row that clears the purge gap before
that day. A predictor handed the panel could read the scored day itself; a
predictor handed only the last training row could not produce a curve that
moves, and a curve that cannot move is indistinguishable from the climatology's.
The training boundary and the conditioning boundary are different questions --
the first is sized against `window.start` and the second against each scored day
-- and they are asked separately here.

Relationship to `repo_model.splits`
-----------------------------------

The purge boundary is `splits.clears_purge`, imported, not restated. Both
modules mean the same thing by a gap and a change to one is a change to both.
`LookAheadError` is likewise the splitter's, so a leak raises the same type
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
from typing import Any, Mapping, Sequence, Tuple

from .baseline import (
    KNOWLEDGE_HOLDOUT,
    SCORING_HOLDOUT,
    ExceedancePredictor,
    _check_fitter_stayed_inside,
    _derive_purge,
    _feature_index,
    _validate_prediction,
    _validate_taus,
)
from .contract import (
    EVENT_WINDOW_KEYS,
    event_window_digest,
    validate_event_windows_document,
)
from .data import DailyObservation
from .splits import (
    LookAheadError,
    SplitError,
    clears_purge,
    ensure_strictly_ascending,
    require_purge_days,
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
    """

    evaluated_at: str
    git_rev: str
    config_sha256: str
    holdout_role: str
    window_name: str
    window_checksum: str
    window_start: str
    window_end: str
    purge_days: int
    train_rows: int
    scored_rows: int

    def as_json_line(self) -> str:
        return json.dumps(self.__dict__, sort_keys=True)


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
    #: The `(source_id, field)` pairs the gap was sized over. The rolling
    #: path's report carries the same, from the same `_derive_purge` call, and
    #: for the same reason: one source can supply a field that prices beside a
    #: field that is refused, so the source IDs alone no longer say what the
    #: number came from.
    field_sources: Tuple[Tuple[str, str], ...]
    purge_days: int
    train_rows: int
    last_train_date: date
    taus: Tuple[float, ...]
    scored_dates: Tuple[date, ...]
    realized: Tuple[float, ...]
    #: `exceedance[day][tau]` is the predicted `P(value > taus[tau])`.
    exceedance: Tuple[Tuple[float, ...], ...]
    #: `feature_dates[day]` is the row the predictor read to produce
    #: `exceedance[day]`: the last panel row that cleared the purge gap before
    #: that scored day. Reported because it is the other half of what makes a
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

    The training set is every row that clears the purge gap ahead of
    `window.start`, and nothing else -- the event is stripped from training
    rather than merely withheld from the headline metric, which is what makes
    this the knowledge holdout and not the scoring one.

    **The gap is derived, never supplied.** The caller declares a feature set;
    this calls `baseline._derive_purge`, which resolves
    `contract.field_sources_for_features(features)` to `(source, field)` pairs
    and sizes the gap with `registry.max_release_lag_days` over exactly those
    fields, and then builds the window. The rolling path calls the same
    function -- imported, not restated, for the reason
    `_check_fitter_stayed_inside` is: two derivations of the gap agree until
    they do not, and this is the one place either path can learn what a source
    or a field is. There is no `purge` argument, for the reason
    `rolling_persistence_backtest` has none: a caller who could type the gap
    could declare an ARX on `on_rrp` and size the gap over `nyfed_sofr` alone,
    and the arithmetic would be right over the wrong evidence -- the one failure
    shape that leaves no trace, because the reported number looks reasonable.
    The two evaluation paths now take the gap from the same place *by the same
    derivation*, which was written down in `cli_eval` before it was true here.

    One consequence is intended and worth stating: `max_release_lag_days`
    refuses to return zero, so an unpurged knowledge holdout is no longer
    expressible through the declared path at all. That is the same consequence
    the rolling path accepted when its gap became derived.

    **Declaration, then verification.** The gap is sized before anything is
    fitted, so this cannot ask an unfitted predictor what it reads. The
    predictor reports `ExceedanceCurves.features_read` after the fit and it is
    checked against the declaration by `baseline._check_fitter_stayed_inside` --
    the same guard the rolling path uses, imported rather than restated, because
    two implementations of the rule that sizes the gap agree until they do not.
    A predictor that exceeded the declaration raises `LookAheadError`.

    **What the predictor is conditioned on.** For each scored day the evaluator
    picks the feature row itself, with `baseline._feature_index`: the last panel
    row that clears the purge gap before *that day*. It is not
    `train_index[-1]` for every day, and the difference is the point. The
    training boundary is sized against `window.start`, so a row inside the gap
    ahead of the window never trains; the same row can be a legitimate feature
    row for a day further into the window, because by then it had been
    published. Rows from inside the window are likewise readable as features for
    later days in it and never as training rows. That is what an extrapolation
    check is: a model that never saw a crisis, forecasting through one on the
    information a forecaster would actually have held.

    Passing the feature rows rather than letting the predictor choose is the
    guard: a predictor handed the panel could read the scored day itself.

    Args:
        observations: the panel, strictly ascending and unique by date. Rows,
            not a date-and-value pair, because a covariate travels in
            `DailyObservation.values` and could not reach a model otherwise. The
            target is `row.spread_bps`, the same target
            `rolling_persistence_backtest` scores; a second target argument
            could disagree with the panel it was aligned to, and now cannot.
        fit_predict: an `ExceedancePredictor`, called once with the training
            rows, the feature rows and `taus`. Returns `ExceedanceCurves`.
        window: the declared knowledge-holdout window, inclusive at both ends.
            An `EventWindow`, not loose dates, and the reason is the checksum.
            `load_event_windows` refuses a declaration without one; taking the
            boundaries as bare arguments here reopened that hole one call
            downstream, because a caller could pass dates it had typed and the
            evaluator would score and journal them as readily as declared ones.
            There is now no argument list that scores an unpinned window: the
            only way to obtain an `EventWindow` is to have supplied a checksum,
            and the ordinary way is `load_event_windows(metadata)`.
        features: the panel columns the predictor is declared to read.
            **Required, keyword-only, with no default**, exactly as on the
            rolling path. Everything about the gap follows from this.
        registry: the parsed source registry, for `max_release_lag_days`. This
            module never reads a `release_lag` itself -- a wrong conversion is a
            provenance error and belongs with Track A.
        decision_time: when the forecast is made, for `max_release_lag_days`.
            Required and undefaulted there, so required and undefaulted here.
        taus: the exceedance family, strictly ascending.
        model_config: hashed into the evaluation record, so a rerun with
            different settings is distinguishable from a repeat of the same one.
        journal_path: append-only provenance log. Required.

    Raises:
        SplitError: malformed panel, window, taus or predictions.
        LookAheadError: the training set reaches into the purge gap or the
            window, the scored rows are not exactly the declared window, a
            feature row does not clear the gap before the day it is read for,
            or the predictor read a column outside `features`.
        UndeclaredFeatureError: `features` names a column
            `contract.field_sources_for_features` cannot classify, or one
            declared to have no ingesting source. Raised before any row is
            selected.
        RegistryContractError: the derived fields cannot support a safe bound.
            Track A's refusal with Track A's message, which `_derive_purge`
            widens only by naming the fields the gap was being sized over.
            There is no exemption here that the rolling path does not have: a
            field with no declared revision policy on a `snapshot_retrieved_at`
            source is refused on this path too, and a derived purge still
            cannot be zero.
    """

    # Before any row is selected: an unresolvable feature set has no gap, so it
    # has no evaluation. Resolving first also means a caller who misspells a
    # column is told which column, rather than getting a window-shaped complaint
    # further in.
    declared: Tuple[str, ...] = tuple(features)
    field_sources, sources, purge = _derive_purge(
        registry, declared, decision_time=decision_time
    )

    rows = list(observations)
    ordered_dates, values = _validate_panel(rows)
    require_purge_days(purge)
    tau_family = _validate_taus(taus)
    if not isinstance(window, EventWindow):
        raise SplitError(
            f"window must be an EventWindow from load_event_windows, got "
            f"{type(window).__name__}"
        )
    event_start, event_end = window.start, window.end

    train_index = [
        i for i, when in enumerate(ordered_dates) if clears_purge(when, event_start, purge)
    ]
    scored_index = [
        i for i, when in enumerate(ordered_dates) if event_start <= when <= event_end
    ]
    if not train_index:
        raise SplitError(
            f"no training row clears a {purge}-day gap before {event_start}"
        )
    if not scored_index:
        raise SplitError(f"no observation falls in {event_start}..{event_end}")

    _assert_window_is_clean(
        ordered_dates, train_index, scored_index, event_start, event_end, purge
    )

    # One feature row per scored day, chosen here and not by the predictor. The
    # candidate set is every panel row before the scored day -- a prefix, which
    # is the shape `_feature_index` scans -- so a day late in the window may
    # read a row from earlier in the window, and never one that has not cleared
    # the gap before it.
    feature_index = [
        _feature_index(ordered_dates, range(index), index, purge)
        for index in scored_index
    ]
    _assert_feature_rows_clear_the_gap(ordered_dates, feature_index, scored_index, purge)

    prediction = fit_predict(
        tuple(rows[i] for i in train_index),
        tuple(rows[i] for i in feature_index),
        tau_family,
    )
    exceedance = _validate_prediction(prediction, len(scored_index), tau_family)
    _check_fitter_stayed_inside(
        prediction.features_read, declared, sources, purge
    )

    record = EvaluationRecord(
        evaluated_at=datetime.now(timezone.utc).isoformat(),
        git_rev=_git_rev(),
        config_sha256=config_digest(model_config),
        holdout_role=KNOWLEDGE_HOLDOUT,
        window_name=window.name,
        window_checksum=window.checksum,
        window_start=event_start.isoformat(),
        window_end=event_end.isoformat(),
        purge_days=purge,
        train_rows=len(train_index),
        scored_rows=len(scored_index),
    )
    append_record(journal_path, record)

    return EventWindowReport(
        window=window,
        features=declared,
        sources=sources,
        field_sources=field_sources,
        purge_days=purge,
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


def _assert_feature_rows_clear_the_gap(
    dates: Sequence[date],
    feature_index: Sequence[int],
    scored_index: Sequence[int],
    purge: int,
) -> None:
    """Every feature row was publishable before the day it is read for.

    `_feature_index` already states the boundary through `clears_purge`, so this
    cannot disagree with it on a run that went through that function. It is here
    because the conditioning set is the door the widened interface opened: a
    covariate reaching a model is also a covariate reaching it from the wrong
    day, and the check that it did not is worth being able to point at.

    Stated as a fact about the *pairing*, which is what `_feature_index` cannot
    say: the row is checked against the scored day it was chosen for, not
    against the window opening. A feature row may sit inside the purge gap ahead
    of `window.start`, or inside the window itself, and still be legitimate for a
    later day -- what it may never be is unpublished on the day it is read.

    `LookAheadError`, never an `assert`: `python -O` strips asserts.
    """

    for position, (feature, scored) in enumerate(zip(feature_index, scored_index)):
        if feature >= scored:
            raise LookAheadError(
                f"the feature row for {dates[scored]} is {dates[feature]}, which "
                f"is not before it"
            )
        if not clears_purge(dates[feature], dates[scored], purge):
            raise LookAheadError(
                f"scored day {position} ({dates[scored]}) is forecast from "
                f"{dates[feature]}, which does not clear the {purge}-day purge "
                f"gap before it"
            )


def _assert_window_is_clean(
    dates: Sequence[date],
    train_index: Sequence[int],
    scored_index: Sequence[int],
    event_start: date,
    event_end: date,
    purge: int,
) -> None:
    """Guard the window before anything is fitted against it.

    Same discipline as `splits._assert_no_look_ahead`: every check here is a
    leak if it fires, so every one of them raises.
    """

    if set(train_index) & set(scored_index):
        raise LookAheadError("a row is both trained on and scored")
    last_train = dates[train_index[-1]]
    if not clears_purge(last_train, event_start, purge):
        raise LookAheadError(
            f"training ends {last_train} and the window opens {event_start}, "
            f"which is inside the {purge}-day purge gap"
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
