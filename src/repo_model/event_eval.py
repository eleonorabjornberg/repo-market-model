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
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence, Tuple

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
    "read_journal",
]


#: The two holdout roles from `AGENT_CONTRACT.md`, "Two holdout roles". They
#: are constants rather than bare strings at the call site so that the journal
#: cannot record a role nobody declared, and so that a grep for either name
#: finds every place the distinction is made. `SCORING_HOLDOUT` is defined here
#: and used nowhere in this module: this module only ever produces the other
#: one, and a role field that could only ever hold one value would not be
#: recording anything.
SCORING_HOLDOUT = "scoring"
KNOWLEDGE_HOLDOUT = "knowledge"


#: `fit_predict(train_dates, train_values, test_dates, taus)` returns one row
#: per test date, each row `P(value > tau)` aligned to `taus`.
FitPredict = Callable[
    [Sequence[date], Sequence[float], Sequence[date], Sequence[float]],
    Sequence[Sequence[float]],
]


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
    purge_days: int
    train_rows: int
    last_train_date: date
    taus: Tuple[float, ...]
    scored_dates: Tuple[date, ...]
    realized: Tuple[float, ...]
    #: `exceedance[day][tau]` is the predicted `P(value > taus[tau])`.
    exceedance: Tuple[Tuple[float, ...], ...]
    record: EvaluationRecord


# --------------------------------------------------------------------------
# Declared windows
# --------------------------------------------------------------------------


def load_event_windows(payload: Any) -> Tuple[EventWindow, ...]:
    """Parse already-loaded event metadata into windows.

    Takes the decoded object, not a path. `metadata/events.json` is Track A's
    file and does not exist yet; baking its location in here would make this
    module wrong the moment the file moves, and would let a test pass against a
    fixture that no longer resembles the real thing. The caller reads the file.

    Every field is required. A window missing its `checksum` cannot be shown to
    be the window that was declared, which is the whole point of pinning one.
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
        missing = [key for key in ("name", "start", "end", "checksum") if key not in entry]
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
        windows.append(EventWindow(name, start, end, str(entry["checksum"])))
    return tuple(windows)


# --------------------------------------------------------------------------
# Evaluation
# --------------------------------------------------------------------------


def evaluate_event_window(
    dates: Sequence[date],
    y: Sequence[float],
    fit_predict: FitPredict,
    window: EventWindow,
    purge: int,
    *,
    taus: Sequence[float],
    model_config: Mapping[str, Any],
    journal_path: Path,
) -> EventWindowReport:
    """Score one knowledge-holdout window: train strictly before it, once.

    The training set is every row that clears the purge gap ahead of
    `event_start`, and nothing else -- the event is stripped from training
    rather than merely withheld from the headline metric, which is what makes
    this the knowledge holdout and not the scoring one.

    Args:
        dates: panel dates, strictly ascending and unique.
        y: the target, aligned to `dates`.
        fit_predict: called once, with the training rows, the scored dates and
            `taus`. Returns `P(value > tau)` per scored day per tau.
        window: the declared knowledge-holdout window, inclusive at both ends.
            An `EventWindow`, not loose dates, and the reason is the checksum.
            `load_event_windows` refuses a declaration without one; taking the
            boundaries as bare arguments here reopened that hole one call
            downstream, because a caller could pass dates it had typed and the
            evaluator would score and journal them as readily as declared ones.
            There is now no argument list that scores an unpinned window: the
            only way to obtain an `EventWindow` is to have supplied a checksum,
            and the ordinary way is `load_event_windows(metadata)`.
        purge: calendar days between the last training row and `window.start`.
            Required, for the reasons in `splits.require_purge_days`.
        taus: the exceedance family, strictly ascending.
        model_config: hashed into the evaluation record, so a rerun with
            different settings is distinguishable from a repeat of the same one.
        journal_path: append-only provenance log. Required.

    Raises:
        SplitError: malformed panel, window, taus or predictions.
        LookAheadError: the training set reaches into the purge gap or the
            window, or the scored rows are not exactly the declared window.
    """

    ordered_dates = list(dates)
    values = list(y)
    _validate_panel(ordered_dates, values)
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

    predictions = fit_predict(
        tuple(ordered_dates[i] for i in train_index),
        tuple(values[i] for i in train_index),
        tuple(ordered_dates[i] for i in scored_index),
        tau_family,
    )
    exceedance = _validate_predictions(predictions, len(scored_index), tau_family)

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
        purge_days=purge,
        train_rows=len(train_index),
        last_train_date=ordered_dates[train_index[-1]],
        taus=tau_family,
        scored_dates=tuple(ordered_dates[i] for i in scored_index),
        realized=tuple(values[i] for i in scored_index),
        exceedance=exceedance,
        record=record,
    )


def _validate_panel(dates: Sequence[date], values: Sequence[float]) -> None:
    if not dates:
        raise SplitError("cannot evaluate an empty panel")
    if len(dates) != len(values):
        raise SplitError(f"{len(dates)} dates against {len(values)} values")
    ensure_strictly_ascending(dates)
    for position, value in enumerate(values):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise SplitError(f"value {position} is not numeric: {value!r}")
        if not math.isfinite(value):
            raise SplitError(f"value {position} is not finite")


def _validate_taus(taus: Sequence[float]) -> Tuple[float, ...]:
    family = tuple(float(tau) for tau in taus)
    if not family:
        raise SplitError("taus must declare at least one threshold")
    for index in range(1, len(family)):
        if family[index] <= family[index - 1]:
            raise SplitError("taus must be strictly ascending")
    if not all(math.isfinite(tau) for tau in family):
        raise SplitError("taus must be finite")
    return family


def _validate_predictions(
    predictions: Any,
    scored_rows: int,
    taus: Tuple[float, ...],
) -> Tuple[Tuple[float, ...], ...]:
    rows = list(predictions)
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
