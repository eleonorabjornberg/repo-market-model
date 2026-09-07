"""Tests for `repo_model.event_eval`.

This module produces the **knowledge holdout** of `AGENT_CONTRACT.md`, "Two
holdout roles" -- crises stripped from training entirely, scored once per
window, reported separately and never averaged into the main table. The
**scoring holdout**, which keeps crisis dates out of the headline metric but
lets them train once they are past, is `repo_model.splits.rolling_origin` and
is tested in `tests/test_splits.py`.

The knowledge holdout needs its own evaluator because the rolling-origin window
expands: by the time a late fold scores one stress episode it has trained on
every earlier one. So the thing worth testing hardest is the boundary -- that
the training set stops where it is supposed to, that the scored rows are exactly
the declared window, and that the window scored is the one that was declared.

The label at the event edge is *not* tested here. It was, against a
`trailing_percentile` in `repo_model.event_eval`, until that turned out to be a
second implementation of a Track A rule -- `AGENT_CONTRACT.md`, "Ownership",
gives the data layer "the label column and its point-in-time rule". The
implementation is deleted and the property it demonstrated now lives in
`tests/test_contract.py::TargetSchemaTests`, as an `expectedFailure` Track A
codes against.

Mutation record. The strict comparison in `splits.clears_purge` was flipped
from `<` to `<=` -- a one-day loosening, the smallest change the boundary
admits -- and the suite run against it, stdlib only, under `-B` with
`PYTHONDONTWRITEBYTECODE=1` and `__pycache__` cleared:

  * 10 tests fail, 8 as assertion failures and 2 as errors, all of them in this
    file. `test_a_row_exactly_purge_days_before_the_window_is_excluded` reports
    it directly: "2026-01-30 not less than 2026-01-30", the Friday exactly
    three days before a Monday window opening, admitted to the training set by
    a boundary that should have excluded it. The two errors are the `purge=0`
    subtests, where `<=` lets a row dated on `event_start` itself into training
    while it is also being scored, and the window guard raises "a row is both
    trained on and scored" before any assertion runs.

  * `tests/test_splits.py` stays entirely green -- 35 tests, no failures. That
    is not a gap in those tests; it is what the splitter does. `rolling_origin`
    finds its training prefix with `bisect` and only *states* the boundary
    through `clears_purge` in its guard, so loosening the comparison leaves its
    folds untouched and merely stops the guard objecting. Tightening it would
    surface there instead, as a guard firing on folds `_train_end` still
    builds. These tests are what stands behind the comparison in the direction
    the splitter cannot see.

Mutation record, the window-pinning guards (`UnpinnedWindowTests`). Two leaks
planted, each the smallest change that reopens the hole the guard closes. Both
runs stdlib only, under `-B` with `PYTHONDONTWRITEBYTECODE=1` and `__pycache__`
cleared:

  * `EventWindow.__post_init__`, checksum check disabled -- an unpinned window
    becomes constructible again. Fails 3 tests. Two are the direct
    "SplitError not raised" on the empty and whitespace checksums. The third is
    `test_no_journal_line_can_carry_an_empty_checksum`, and it is the one worth
    having: it fails on the *contents of the journal*, reporting a line written
    for a window that cannot be shown to be the one declared. That is the
    damage, as opposed to the missing exception. The test was rewritten to
    attempt the scoring and tolerate the refusal precisely so it would carry
    that power -- as first written it only asserted over well-formed runs and
    stayed green under this mutation.

  * The `isinstance(window, EventWindow)` check in `evaluate_event_window`
    removed. Fails 1 test, as an error rather than a failure: a bare
    `(start, end)` tuple gets past the gate and dies later on `window.start`.
    The error is the right shape -- nothing scored, nothing journalled -- but
    the annotation alone is not a guard, and the check is what turns a later
    `AttributeError` into a refusal at the boundary.

Neither mutation touches the purge boundary, so the whole of
`PurgeBoundaryTests` stays green under both. That is correct and worth stating:
these guards are about *which* window is scored, not about where training stops.

Mutation record, checksum verification (`ChecksumVerificationTests` and
`load_events_file`). Two leaks planted, both stdlib only, run under `-B` with
`PYTHONDONTWRITEBYTECODE=1` against a copy of the tree with `__pycache__`
cleared, each copy given a control run first. `src/repo_model/contract.py` is
`HUMAN_ONLY` in the ownership gate, so the mutation that touches it was applied
to a scratch copy outside the worktree and never to the file itself:

  * The comparison in `load_event_windows` disabled -- the digest still
    computed and its result discarded, which is precisely the shape the guard
    had before this block: a checksum required and never checked. Fails 11
    across 6 test methods. Four are the direct refusals here. The other two are
    in `tests/test_events_metadata_spec.py::ConsumerCompatibilityTests`, and
    they are the ones worth having: they fail on the loader and the validator
    disagreeing about the same document, rather than on a missing exception.
    That disagreement is the damage -- a file that passes review here and blows
    up at evaluation time, or worse, the reverse.

  * `sort_keys=True` dropped from `event_window_digest`'s `json.dumps`. The
    three keys are inserted as name, start, end, which is not their sorted
    order, so the canonical form changes and with it every digest. Fails 3, all
    in `tests/test_events_metadata_spec.py::DeclaredFileTests`, all against the
    real `metadata/events.json`.

    Nothing in *this* file fails under it, and that is the finding rather than a
    gap. Every fixture here seals itself by calling `event_window_digest`, so a
    change to the rule moves the fixture and the expectation together and these
    tests stay green by construction. What they test is the wiring -- that the
    loader calls that function and refuses what disagrees with it -- and the
    wiring is exactly what the first mutation kills and the second leaves
    intact. The rule itself is pinned by the one document whose checksums were
    computed without reference to it, which is Track A's file. A suite made only
    of self-sealing fixtures could not tell the declared digest from any other
    function of the same three fields; `DeclaredFileTests` is what stands behind
    the rule, and it is not a formality.

The runs say nothing about the exceedance report or the journal's append-only
behaviour; no mutation was planted in either.
"""

import inspect
import json
import sys
import tempfile
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from repo_model import contract, event_eval
from repo_model.contract import event_window_digest
from repo_model.event_eval import (
    KNOWLEDGE_HOLDOUT,
    SCORING_HOLDOUT,
    EventWindow,
    EventWindowReport,
    LookAheadError,
    SplitError,
    _assert_window_is_clean,
    append_record,
    config_digest,
    evaluate_event_window,
    load_event_windows,
    load_events_file,
    read_journal,
)


# The exceedance family declared in AGENT_CONTRACT.md, "Decided: stress target
# and event holdouts". The evaluator takes it as an argument rather than naming
# it, for the same reason it takes the windows as an argument; this is the
# fixture, not the declaration.
TAUS = (5.0, 10.0, 20.0, 50.0)


def business_days(start, count):
    days = []
    cursor = start
    while len(days) < count:
        if cursor.weekday() < 5:
            days.append(cursor)
        cursor += timedelta(days=1)
    return days


# A panel running into 2026-02-02, a Monday. 2026-01-30 is the Friday exactly
# three calendar days before it, which is the row a `<` boundary excludes at
# purge=3 and a `<=` boundary would let through.
PANEL_DATES = business_days(date(2026, 1, 5), 30)
PANEL_VALUES = [10.0 + index for index in range(len(PANEL_DATES))]
EVENT_START = date(2026, 2, 2)
EVENT_END = date(2026, 2, 6)


def flat_predictor(probabilities=(0.9, 0.7, 0.4, 0.1)):
    """A `fit_predict` that ignores its inputs and returns a fixed curve."""

    def fit_predict(train_dates, train_values, test_dates, taus):
        return [tuple(probabilities) for _ in test_dates]

    return fit_predict


class EvaluatorHarness(unittest.TestCase):
    """Shared setup: a temp journal, and a helper that runs one evaluation."""

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.journal = Path(directory.name) / "events.jsonl"

    def evaluate(self, **overrides):
        """Run one evaluation, with `event_start`/`event_end` as conveniences.

        The evaluator takes an `EventWindow`; this helper assembles one so that
        a test which only cares about the boundary does not have to. Tests that
        care about the window *type* pass `window=` directly.
        """

        kwargs = dict(
            dates=PANEL_DATES,
            y=PANEL_VALUES,
            fit_predict=flat_predictor(),
            purge=3,
            taus=TAUS,
            model_config={"model": "persistence", "seed": 0},
            journal_path=self.journal,
        )
        kwargs.update(overrides)
        if "window" not in kwargs:
            # The checksum defaults to the digest of the boundaries actually
            # used, not to a placeholder. `"abc123"` was a window that could
            # not exist in a declared file, and a fixture that could not
            # survive `load_event_windows` is a fixture testing a shape the
            # loader no longer accepts.
            name = overrides.get("window_name", "feb-2026")
            start = overrides.pop("event_start", EVENT_START)
            end = overrides.pop("event_end", EVENT_END)
            kwargs["window"] = EventWindow(
                name,
                start,
                end,
                overrides.get(
                    "window_checksum",
                    event_window_digest(name, start.isoformat(), end.isoformat()),
                ),
            )
        for consumed in ("event_start", "event_end", "window_name", "window_checksum"):
            kwargs.pop(consumed, None)
        positional = (
            kwargs.pop("dates"),
            kwargs.pop("y"),
            kwargs.pop("fit_predict"),
            kwargs.pop("window"),
            kwargs.pop("purge"),
        )
        return evaluate_event_window(*positional, **kwargs)


class PurgeBoundaryTests(EvaluatorHarness):
    """Where the training set stops. The comparison is strict."""

    def test_a_row_exactly_purge_days_before_the_window_is_excluded(self):
        """The `<` in `clears_purge`, stated as a fact about one row.

        2026-01-30 plus three days is 2026-02-02, the day the window opens. A
        value published exactly as the window opens is not in hand beforehand,
        so the row must not train. A `<=` boundary keeps it and this fails.
        """

        report = self.evaluate(purge=3)
        self.assertLess(report.last_train_date, date(2026, 1, 30))
        self.assertEqual(report.last_train_date, date(2026, 1, 29))

    def test_the_boundary_moves_with_the_gap(self):
        expected = {
            0: date(2026, 1, 30),
            1: date(2026, 1, 30),
            2: date(2026, 1, 30),
            3: date(2026, 1, 29),
            4: date(2026, 1, 28),
        }
        for purge, last_train in expected.items():
            with self.subTest(purge=purge):
                self.assertEqual(self.evaluate(purge=purge).last_train_date, last_train)

    def test_every_training_row_clears_the_gap_independently(self):
        """Recomputed here with a day count, not the module's comparison."""

        for purge in (0, 2, 3, 5):
            with self.subTest(purge=purge):
                report = self.evaluate(purge=purge)
                self.assertGreater((EVENT_START - report.last_train_date).days, purge)

    def test_training_rows_are_counted_and_all_precede_the_window(self):
        report = self.evaluate(purge=3)
        expected = [
            when for when in PANEL_DATES if (EVENT_START - when).days > 3
        ]
        self.assertEqual(report.train_rows, len(expected))
        self.assertLess(report.last_train_date, EVENT_START)

    def test_the_model_never_sees_a_row_from_inside_the_gap(self):
        seen = {}

        def spy(train_dates, train_values, test_dates, taus):
            seen["train"] = tuple(train_dates)
            seen["test"] = tuple(test_dates)
            return [(0.9, 0.7, 0.4, 0.1) for _ in test_dates]

        self.evaluate(fit_predict=spy, purge=3)
        self.assertGreater((EVENT_START - max(seen["train"])).days, 3)
        self.assertTrue(all(when < EVENT_START for when in seen["train"]))
        self.assertFalse(set(seen["train"]) & set(seen["test"]))

    def test_purge_is_required_and_validated(self):
        for bad in (None, 2.0, True, -1):
            with self.subTest(purge=bad):
                with self.assertRaises(SplitError):
                    self.evaluate(purge=bad)

    def test_a_gap_that_leaves_no_training_row_raises(self):
        with self.assertRaisesRegex(SplitError, "no training row clears"):
            self.evaluate(purge=3650)


class ScoredWindowTests(EvaluatorHarness):
    """One fold, one score, exactly the declared rows."""

    def test_scored_rows_are_exactly_the_window_inclusive(self):
        report = self.evaluate()
        expected = [w for w in PANEL_DATES if EVENT_START <= w <= EVENT_END]
        self.assertEqual(list(report.scored_dates), expected)
        self.assertEqual(report.scored_dates[0], EVENT_START)
        self.assertIn(EVENT_END, report.scored_dates)

    def test_the_realized_path_is_the_panel_values_for_those_rows(self):
        report = self.evaluate()
        lookup = dict(zip(PANEL_DATES, PANEL_VALUES))
        self.assertEqual(
            list(report.realized), [lookup[when] for when in report.scored_dates]
        )

    def test_a_single_day_window_is_allowed(self):
        report = self.evaluate(event_start=EVENT_START, event_end=EVENT_START)
        self.assertEqual(len(report.scored_dates), 1)

    def test_a_window_with_no_observations_raises(self):
        with self.assertRaisesRegex(SplitError, "no observation falls in"):
            self.evaluate(event_start=date(2026, 2, 7), event_end=date(2026, 2, 8))

    def test_a_backwards_window_raises(self):
        with self.assertRaisesRegex(SplitError, "ends .* before it starts"):
            self.evaluate(event_start=EVENT_END, event_end=EVENT_START)


class WindowGuardTests(unittest.TestCase):
    """The guard, driven directly with windows the evaluator cannot build."""

    def test_a_training_row_inside_the_gap_raises(self):
        dates = PANEL_DATES
        train = [i for i, w in enumerate(dates) if w <= date(2026, 1, 30)]
        scored = [i for i, w in enumerate(dates) if EVENT_START <= w <= EVENT_END]
        with self.assertRaisesRegex(LookAheadError, "inside the 3-day purge gap"):
            _assert_window_is_clean(dates, train, scored, EVENT_START, EVENT_END, 3)

    def test_a_row_both_trained_on_and_scored_raises(self):
        dates = PANEL_DATES
        scored = [i for i, w in enumerate(dates) if EVENT_START <= w <= EVENT_END]
        train = [i for i, w in enumerate(dates) if w < date(2026, 1, 28)] + [scored[0]]
        with self.assertRaisesRegex(LookAheadError, "both trained on and scored"):
            _assert_window_is_clean(dates, train, scored, EVENT_START, EVENT_END, 3)

    def test_a_scored_row_outside_the_window_raises(self):
        dates = PANEL_DATES
        train = [i for i, w in enumerate(dates) if w < date(2026, 1, 28)]
        scored = [i for i, w in enumerate(dates) if EVENT_START <= w <= EVENT_END]
        with self.assertRaisesRegex(LookAheadError, "scored but outside the window"):
            _assert_window_is_clean(
                dates, train, scored, EVENT_START, date(2026, 2, 4), 3
            )

    def test_non_contiguous_scored_rows_raise(self):
        dates = PANEL_DATES
        train = [i for i, w in enumerate(dates) if w < date(2026, 1, 28)]
        scored = [i for i, w in enumerate(dates) if EVENT_START <= w <= EVENT_END]
        with self.assertRaisesRegex(LookAheadError, "not contiguous"):
            _assert_window_is_clean(
                dates, train, scored[:1] + scored[2:], EVENT_START, EVENT_END, 3
            )

    def test_a_clean_window_passes(self):
        dates = PANEL_DATES
        train = [i for i, w in enumerate(dates) if (EVENT_START - w).days > 3]
        scored = [i for i, w in enumerate(dates) if EVENT_START <= w <= EVENT_END]
        _assert_window_is_clean(dates, train, scored, EVENT_START, EVENT_END, 3)


class ExceedanceReportTests(EvaluatorHarness):
    """What the report carries, and what it deliberately does not."""

    def test_the_exceedance_curve_is_one_row_per_scored_day_per_tau(self):
        report = self.evaluate()
        self.assertEqual(report.taus, TAUS)
        self.assertEqual(len(report.exceedance), len(report.scored_dates))
        for curve in report.exceedance:
            self.assertEqual(len(curve), len(TAUS))

    def test_the_report_carries_no_aggregate_score(self):
        """Encodes the ruling: an event window gets a curve, not a number.

        Ten stressed days cannot support a Brier score or a reliability curve,
        and emitting one invites comparisons across events and reruns that it
        cannot bear. If a metric is ever added here this test should be the
        thing that argues with it.
        """

        report = self.evaluate()
        for forbidden in (
            "brier",
            "brier_score",
            "reliability",
            "calibration",
            "skill",
            "auc",
            "log_score",
            "mae",
        ):
            self.assertFalse(
                hasattr(report, forbidden),
                msg=f"report grew a {forbidden!r}; an event window cannot support one",
            )
        self.assertEqual(
            set(EventWindowReport.__dataclass_fields__),
            {
                "window",
                "purge_days",
                "train_rows",
                "last_train_date",
                "taus",
                "scored_dates",
                "realized",
                "exceedance",
                "record",
            },
        )

    def test_a_non_monotone_exceedance_curve_is_rejected(self):
        """P(Y > tau) cannot rise with tau; averaging would hide it."""

        with self.assertRaisesRegex(SplitError, "exceedance rises"):
            self.evaluate(fit_predict=flat_predictor((0.1, 0.4, 0.7, 0.9)))

    def test_predictions_outside_zero_one_are_rejected(self):
        with self.assertRaisesRegex(SplitError, "is not a probability"):
            self.evaluate(fit_predict=flat_predictor((1.4, 0.7, 0.4, 0.1)))

    def test_a_wrong_shaped_prediction_is_rejected(self):
        with self.assertRaisesRegex(SplitError, "probabilities for 4 taus"):
            self.evaluate(fit_predict=flat_predictor((0.9, 0.1)))

        def short(train_dates, train_values, test_dates, taus):
            return [(0.9, 0.7, 0.4, 0.1)]

        with self.assertRaisesRegex(SplitError, "returned 1 rows"):
            self.evaluate(fit_predict=short)

    def test_taus_must_be_a_strictly_ascending_non_empty_family(self):
        with self.assertRaisesRegex(SplitError, "at least one threshold"):
            self.evaluate(taus=())
        with self.assertRaisesRegex(SplitError, "strictly ascending"):
            self.evaluate(taus=(10.0, 5.0))


class RunOnceJournalTests(EvaluatorHarness):
    """Append-only provenance. Reruns are visible, not prevented."""

    def test_an_evaluation_appends_one_record(self):
        self.evaluate()
        entries = read_journal(self.journal)
        self.assertEqual(len(entries), 1)

    def test_a_rerun_appends_a_second_record_rather_than_being_blocked(self):
        self.evaluate()
        self.evaluate()
        entries = read_journal(self.journal)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["window_name"], entries[1]["window_name"])

    def test_the_record_carries_timestamp_git_rev_and_config_hash(self):
        report = self.evaluate()
        entry = read_journal(self.journal)[0]
        self.assertEqual(entry["window_name"], "feb-2026")
        self.assertEqual(
            entry["window_checksum"],
            event_window_digest(
                "feb-2026", EVENT_START.isoformat(), EVENT_END.isoformat()
            ),
        )
        self.assertEqual(entry["purge_days"], 3)
        self.assertEqual(entry["scored_rows"], len(report.scored_dates))
        self.assertEqual(entry["train_rows"], report.train_rows)
        self.assertTrue(entry["evaluated_at"].startswith("20"))
        self.assertTrue(entry["git_rev"])
        self.assertEqual(len(entry["config_sha256"]), 64)

    def test_the_record_names_the_knowledge_holdout_role(self):
        """The contract: the two roles must not be conflated "in reporting".

        The journal is reporting. Without the role on the line, a reader has to
        know which module wrote it to know whether the number beside it may be
        averaged into the main table -- and the whole point of the split is
        that one of them may not.
        """

        self.evaluate()
        entry = read_journal(self.journal)[0]
        self.assertEqual(entry["holdout_role"], KNOWLEDGE_HOLDOUT)
        self.assertEqual(entry["holdout_role"], "knowledge")
        self.assertNotEqual(KNOWLEDGE_HOLDOUT, SCORING_HOLDOUT)

    def test_the_evaluator_never_records_the_scoring_holdout_role(self):
        """This module produces one role. A scoring-holdout line here is a bug."""

        self.evaluate()
        self.evaluate(model_config={"model": "ar1"})
        for entry in read_journal(self.journal):
            self.assertNotEqual(
                entry["holdout_role"],
                SCORING_HOLDOUT,
                msg="event_eval journalled a scoring-holdout run; that role "
                "belongs to rolling_origin and the two are never averaged",
            )

    def test_a_different_config_hashes_differently(self):
        self.evaluate(model_config={"model": "persistence", "seed": 0})
        self.evaluate(model_config={"model": "persistence", "seed": 1})
        entries = read_journal(self.journal)
        self.assertNotEqual(entries[0]["config_sha256"], entries[1]["config_sha256"])

    def test_key_order_does_not_change_the_config_hash(self):
        self.assertEqual(
            config_digest({"a": 1, "b": 2}), config_digest({"b": 2, "a": 1})
        )

    def test_an_unserialisable_config_raises(self):
        with self.assertRaisesRegex(SplitError, "not JSON-serialisable"):
            self.evaluate(model_config={"fit": object()})

    def test_existing_records_are_never_rewritten(self):
        self.evaluate()
        first = self.journal.read_text(encoding="utf-8")
        self.evaluate()
        self.assertTrue(
            self.journal.read_text(encoding="utf-8").startswith(first),
            msg="the journal was rewritten rather than appended to",
        )

    def test_every_line_is_standalone_json(self):
        self.evaluate()
        self.evaluate()
        for line in self.journal.read_text(encoding="utf-8").splitlines():
            json.loads(line)

    def test_reading_a_missing_journal_returns_nothing(self):
        self.assertEqual(read_journal(self.journal.parent / "absent.jsonl"), ())


class EventWindowMetadataTests(unittest.TestCase):
    """Windows are parsed from loaded metadata, never named in code."""

    # Checksums are computed, never written by hand. `"0" * 64` and
    # `"1" * 64` were windows that could not exist in a declared file, and once
    # `load_event_windows` verifies the digest they stop being fixtures for the
    # loader and start being fixtures for a loader nobody has.
    FIXTURE = {
        "windows": [
            {
                "name": "sep-2019",
                "start": "2019-09-16",
                "end": "2019-09-20",
                "checksum": event_window_digest(
                    "sep-2019", "2019-09-16", "2019-09-20"
                ),
            },
            {
                "name": "mar-2020",
                "start": "2020-03-09",
                "end": "2020-03-20",
                "checksum": event_window_digest(
                    "mar-2020", "2020-03-09", "2020-03-20"
                ),
            },
        ]
    }

    def test_a_well_formed_fixture_parses(self):
        windows = load_event_windows(self.FIXTURE)
        self.assertEqual([w.name for w in windows], ["sep-2019", "mar-2020"])
        self.assertEqual(windows[0].start, date(2019, 9, 16))
        self.assertEqual(windows[1].end, date(2020, 3, 20))
        self.assertEqual(
            windows[0].checksum,
            event_window_digest("sep-2019", "2019-09-16", "2019-09-20"),
        )

    def test_a_bare_list_is_accepted(self):
        self.assertEqual(len(load_event_windows(self.FIXTURE["windows"])), 2)

    def test_a_window_missing_its_checksum_is_rejected(self):
        entry = dict(self.FIXTURE["windows"][0])
        del entry["checksum"]
        with self.assertRaisesRegex(SplitError, "missing checksum"):
            load_event_windows([entry])

    def test_a_window_missing_name_or_dates_is_rejected(self):
        for key in ("name", "start", "end"):
            entry = dict(self.FIXTURE["windows"][0])
            del entry[key]
            with self.subTest(missing=key):
                with self.assertRaisesRegex(SplitError, f"missing {key}"):
                    load_event_windows([entry])

    def test_a_non_iso_date_is_rejected(self):
        entry = dict(self.FIXTURE["windows"][0], start="16/09/2019")
        with self.assertRaisesRegex(SplitError, "non-ISO date"):
            load_event_windows([entry])

    def test_a_backwards_window_is_rejected(self):
        entry = dict(self.FIXTURE["windows"][0], start="2019-09-20", end="2019-09-16")
        with self.assertRaisesRegex(SplitError, "ends .* before it starts"):
            load_event_windows([entry])

    def test_duplicate_names_are_rejected(self):
        entry = self.FIXTURE["windows"][0]
        with self.assertRaisesRegex(SplitError, "duplicate window name"):
            load_event_windows([entry, dict(entry)])

    def test_empty_or_missing_declarations_are_rejected(self):
        with self.assertRaisesRegex(SplitError, "no 'windows' key"):
            load_event_windows({})
        with self.assertRaisesRegex(SplitError, "declares no windows"):
            load_event_windows([])

    def test_a_parsed_window_drives_an_evaluation(self):
        """The path from metadata to a scored window, with no path in code."""

        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        window = load_event_windows(
            [
                {
                    "name": "feb-2026",
                    "start": EVENT_START.isoformat(),
                    "end": EVENT_END.isoformat(),
                    "checksum": event_window_digest(
                        "feb-2026", EVENT_START.isoformat(), EVENT_END.isoformat()
                    ),
                }
            ]
        )[0]
        report = evaluate_event_window(
            PANEL_DATES,
            PANEL_VALUES,
            flat_predictor(),
            window,
            3,
            taus=TAUS,
            model_config={"model": "persistence"},
            journal_path=Path(directory.name) / "events.jsonl",
        )
        self.assertEqual(report.window, window)


class ChecksumVerificationTests(unittest.TestCase):
    """The checksum is checked, not merely required.

    `AGENT_CONTRACT.md`, "Decided: the event-window checksum": "A checksum that
    is only required, never verified, is a field that looks like a guard."
    `load_event_windows` demanded a non-empty string and compared it to nothing,
    so the one edit the field exists to catch -- a boundary moved, the digest
    left alone -- produced a document that loaded and scored exactly like a
    declared one.

    The digest is `repo_model.contract.event_window_digest`, and these tests
    check that it is *that function* and not a second correct reading of the
    same rule living in `event_eval.py`. A duplicated correct implementation is
    the failure mode the move into `contract.py` was made to prevent: it agrees
    with the original until somebody edits one of them, and then the
    disagreement surfaces as a window that validates on one path and not the
    other.
    """

    NAME = "sep-2019"
    START = "2019-09-16"
    END = "2019-09-20"

    def declaration(self, **changes):
        """One well-formed window, sealed with the contract digest."""

        window = {
            "name": self.NAME,
            "start": self.START,
            "end": self.END,
            "checksum": event_window_digest(self.NAME, self.START, self.END),
        }
        window.update(changes)
        return [window]

    def test_a_window_whose_checksum_does_not_match_its_boundaries_is_rejected(self):
        """The plain case: a digest that is not the digest of anything."""

        for wrong in ("0" * 64, "1" * 64, "deadbeef", "abc123"):
            with self.subTest(checksum=wrong):
                with self.assertRaisesRegex(SplitError, "does not match its boundaries"):
                    load_event_windows(self.declaration(checksum=wrong))

    def test_moving_a_boundary_without_recomputing_the_digest_is_caught(self):
        """The cherry-pick the contract names, at the loader.

        "What is not visible is March 2020 starting a week later than it used
        to, which quietly moves the worst days out of the scored window and into
        the training set." Every one of these edits leaves a well-formed,
        parseable, non-empty-checksum document; only the comparison catches it.
        """

        for key, moved in (
            ("start", "2019-09-17"),
            ("end", "2019-09-19"),
            ("name", "sep-2019-revised"),
        ):
            with self.subTest(moved=key):
                with self.assertRaisesRegex(SplitError, "does not match its boundaries"):
                    load_event_windows(self.declaration(**{key: moved}))

    def test_resealing_the_moved_boundary_loads_and_that_is_the_honest_limit(self):
        """Recorded because it is a limit, not a gap.

        A checksum cannot detect an edit that recomputes it. What it buys is
        that the value changes, so the edit shows in a diff and disagrees with
        every journal line that scored the old window. Asserting the limit here
        keeps the guard from being read as more than it is.
        """

        moved = self.declaration(
            start="2019-09-17",
            checksum=event_window_digest(self.NAME, "2019-09-17", self.END),
        )
        self.assertEqual(load_event_windows(moved)[0].start, date(2019, 9, 17))

    def test_the_digest_is_the_contract_function_and_not_a_local_reading(self):
        """Fails on a *correct* reimplementation, not only on a wrong one.

        Two halves, because either alone is passable by the thing this block
        exists to prevent. The identity check catches a local copy under any
        name that is then used; the substitution check catches a digest inlined
        into `load_event_windows` itself, which would keep accepting a document
        sealed with the real rule while the name it is supposed to call has been
        replaced by one that disagrees with everything.
        """

        self.assertIs(
            event_eval.event_window_digest,
            contract.event_window_digest,
            msg="event_eval holds its own event_window_digest; a second correct "
            "reading of a shared shape is the collision contract.py exists to end",
        )

        sealed = self.declaration()
        with mock.patch.object(
            event_eval, "event_window_digest", lambda name, start, end: "z" * 64
        ):
            with self.assertRaises(SplitError) as caught:
                load_event_windows(sealed)
        self.assertIn(
            "z" * 64,
            str(caught.exception),
            msg="the loader did not route through event_window_digest; a digest "
            "computed inline is a duplicated reading even when it is correct",
        )

    def test_there_is_no_way_to_load_a_window_without_verifying_it(self):
        """No opt-out parameter, on either entry point.

        A `verify=False` would be a way for the one caller that matters to skip
        the guard, and the caller that matters is whichever one is in a hurry.
        The bare-list form is checked too: it is the form fixtures use, and a
        check that only the mapping form performs is a check with a documented
        bypass.
        """

        for loader in (load_event_windows, load_events_file):
            parameters = inspect.signature(loader).parameters
            with self.subTest(loader=loader.__name__):
                self.assertEqual(len(parameters), 1, msg=f"{loader.__name__} grew an argument")
                for name, parameter in parameters.items():
                    self.assertIs(
                        parameter.default,
                        inspect.Parameter.empty,
                        msg=f"{loader.__name__}({name}=...) acquired a default",
                    )

        source = inspect.getsource(event_eval)
        for opt_out in ("verify=", "check_checksum", "skip_checksum", "strict="):
            self.assertNotIn(
                opt_out,
                source,
                msg=f"{opt_out!r} in event_eval; an opt-out is a bypass with a "
                "polite name",
            )

        wrong = self.declaration(checksum="0" * 64)
        with self.assertRaisesRegex(SplitError, "does not match its boundaries"):
            load_event_windows(wrong)
        with self.assertRaisesRegex(SplitError, "does not match its boundaries"):
            load_event_windows({"version": 1, "windows": wrong})


class EventsFileTests(unittest.TestCase):
    """`load_events_file`: reads a declared file the caller names.

    The path is an argument. `metadata/events.json` is Track A's file, and
    model-eval hard-coding its location would be model-eval deciding Track A's
    layout -- the same reason `load_event_windows` takes a payload. That the
    file is now real is exactly when a baked-in default would start being obeyed
    instead of noticed.
    """

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)

    def written(self, payload):
        path = self.directory / "events.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    def conforming(self):
        return {
            "version": 1,
            "windows": [
                {
                    "name": name,
                    "start": start,
                    "end": end,
                    "checksum": event_window_digest(name, start, end),
                }
                for name, start, end in (
                    ("example-alpha", "2001-03-05", "2001-03-09"),
                    ("example-beta", "2002-11-18", "2002-11-22"),
                )
            ],
        }

    def test_the_loader_takes_a_path_and_declares_no_default(self):
        parameters = inspect.signature(load_events_file).parameters
        self.assertEqual(list(parameters), ["path"])
        self.assertIs(parameters["path"].default, inspect.Parameter.empty)
        with self.assertRaises(TypeError):
            load_events_file()

    def test_a_conforming_file_loads_into_event_windows(self):
        windows = load_events_file(self.written(self.conforming()))
        self.assertEqual(
            [w.name for w in windows], ["example-alpha", "example-beta"]
        )
        for window in windows:
            self.assertIsInstance(window, EventWindow)

    def test_a_document_failing_the_shared_validator_raises_with_every_problem_named(self):
        """One raise, every fault. Not one key per run.

        The validator returns a list precisely so a malformed file is fixed in a
        single pass, and a loader that raised on the first problem would throw
        that away at the only place it matters.
        """

        payload = self.conforming()
        del payload["version"]
        payload["windows"][0]["start"] = "2001-03-06"  # digest no longer matches
        payload["windows"][1]["end"] = "18/11/2002"

        path = self.written(payload)
        problems = contract.validate_event_windows_document(payload)
        self.assertGreaterEqual(len(problems), 3)

        with self.assertRaises(SplitError) as caught:
            load_events_file(path)
        message = str(caught.exception)
        self.assertIn(str(path), message)
        for problem in problems:
            self.assertIn(
                problem,
                message,
                msg="the raise dropped a problem the validator reported",
            )

    def test_the_file_is_validated_before_it_is_parsed(self):
        """A bare list has nowhere to carry a version, so the file form rejects it.

        `load_event_windows` accepts one -- that is the fixture form. The
        declared file is held to the document schema, and this is the difference
        between the two entry points stated rather than left to be discovered.
        """

        path = self.written(self.conforming()["windows"])
        with self.assertRaisesRegex(SplitError, "must be a JSON object"):
            load_events_file(path)

    def test_the_loader_names_no_file_of_its_own(self):
        source = inspect.getsource(load_events_file)
        self.assertNotIn(
            "events.json",
            source.split('"""')[-1],
            msg="load_events_file names a file; the path is the caller's",
        )


class UnpinnedWindowTests(EvaluatorHarness):
    """A window that cannot be shown to be the declared one is never scored.

    `load_event_windows` has always refused a declaration with no checksum.
    The evaluator used to reopen that hole one call downstream: `window_name`
    defaulted to `"unnamed"` and `window_checksum` to `""`, so a caller could
    pass boundaries it had typed and get them scored and journalled exactly
    like declared ones -- and the journal line, which is the whole record that
    a single-evaluation budget was spent, would say the window had no name and
    no checksum without anything objecting.

    That is the cherry-pick the contract names: "moving a window edge is the
    realistic cherry-pick, not swapping window type." Taking an `EventWindow`
    closes it by construction rather than by validation, because the only way
    to hold one is to have supplied a checksum.
    """

    def test_the_signature_takes_a_window_and_offers_no_loose_boundaries(self):
        parameters = inspect.signature(evaluate_event_window).parameters
        self.assertIn("window", parameters)
        for gone in ("event_start", "event_end", "window_name", "window_checksum"):
            self.assertNotIn(
                gone,
                parameters,
                msg=f"{gone!r} is back; loose boundaries let an unpinned window "
                "be scored and journalled",
            )

    def test_no_argument_of_the_evaluator_has_a_default(self):
        """A default is how the hole appeared the first time."""

        for name, parameter in inspect.signature(evaluate_event_window).parameters.items():
            self.assertIs(
                parameter.default,
                inspect.Parameter.empty,
                msg=f"{name!r} acquired a default",
            )

    def test_a_window_with_an_empty_checksum_cannot_be_constructed(self):
        for blank in ("", "   "):
            with self.subTest(checksum=blank):
                with self.assertRaisesRegex(SplitError, "has no checksum"):
                    EventWindow("feb-2026", EVENT_START, EVENT_END, blank)

    def test_an_unnamed_window_cannot_be_constructed(self):
        with self.assertRaisesRegex(SplitError, "has no name"):
            EventWindow("", EVENT_START, EVENT_END, "abc123")

    def test_a_backwards_window_cannot_be_constructed(self):
        with self.assertRaisesRegex(SplitError, "ends .* before it starts"):
            EventWindow("feb-2026", EVENT_END, EVENT_START, "abc123")

    def test_a_datetime_is_not_accepted_where_a_date_is_declared(self):
        """`datetime` is a `date` subclass and would compare against the panel."""

        with self.assertRaisesRegex(SplitError, "must be a date"):
            EventWindow(
                "feb-2026",
                datetime(2026, 2, 2, 9, 30),
                EVENT_END,
                "abc123",
            )

    def test_loose_dates_are_refused_by_the_evaluator(self):
        """Belt and braces: the type is checked, not merely annotated."""

        with self.assertRaisesRegex(SplitError, "must be an EventWindow"):
            self.evaluate(window=(EVENT_START, EVENT_END))

    def test_omitting_the_window_is_a_type_error(self):
        with self.assertRaises(TypeError):
            evaluate_event_window(
                PANEL_DATES,
                PANEL_VALUES,
                flat_predictor(),
                taus=TAUS,
                model_config={},
                journal_path=self.journal,
            )

    def test_the_journalled_name_and_checksum_come_from_the_window(self):
        window = EventWindow("sep-2019-rehearsal", EVENT_START, EVENT_END, "f" * 64)
        self.evaluate(window=window)
        entry = read_journal(self.journal)[0]
        self.assertEqual(entry["window_name"], "sep-2019-rehearsal")
        self.assertEqual(entry["window_checksum"], "f" * 64)
        self.assertEqual(entry["window_start"], EVENT_START.isoformat())
        self.assertEqual(entry["window_end"], EVENT_END.isoformat())

    def test_no_journal_line_can_carry_an_empty_checksum(self):
        """The property the defaults used to violate, stated over the file.

        Written as an attempt rather than as an assertion about well-formed
        runs, so that it has power: it tries to score an unpinned window,
        accepts a refusal, and then requires that the journal contain no
        unpinned line either way. A guard that stops raising fails here on the
        contents of the file, not merely on a missing exception.
        """

        self.evaluate()
        for name, checksum in (("unpinned", ""), ("blank", "   ")):
            with self.subTest(checksum=checksum):
                try:
                    self.evaluate(
                        window=EventWindow(name, EVENT_START, EVENT_END, checksum)
                    )
                except SplitError:
                    pass  # the refusal is the intended path
        for entry in read_journal(self.journal):
            self.assertTrue(
                entry["window_checksum"].strip(),
                msg=f"journalled {entry['window_name']!r} with no checksum; a "
                "single-evaluation budget was spent on a window that cannot be "
                "shown to be the one that was declared",
            )
            self.assertNotEqual(entry["window_name"], "unnamed")


class PanelValidationTests(EvaluatorHarness):
    def test_unsorted_dates_are_rejected(self):
        dates = list(PANEL_DATES)
        dates[4], dates[5] = dates[5], dates[4]
        with self.assertRaisesRegex(SplitError, "strictly ascending"):
            self.evaluate(dates=dates)

    def test_mismatched_lengths_are_rejected(self):
        with self.assertRaisesRegex(SplitError, "dates against"):
            self.evaluate(y=PANEL_VALUES[:-1])

    def test_an_empty_panel_is_rejected(self):
        with self.assertRaisesRegex(SplitError, "empty panel"):
            self.evaluate(dates=[], y=[])

    def test_non_finite_and_non_numeric_values_are_rejected(self):
        values = list(PANEL_VALUES)
        values[3] = float("nan")
        with self.assertRaisesRegex(SplitError, "not finite"):
            self.evaluate(y=values)
        values[3] = "4.30"
        with self.assertRaisesRegex(SplitError, "not numeric"):
            self.evaluate(y=values)


if __name__ == "__main__":
    unittest.main()
