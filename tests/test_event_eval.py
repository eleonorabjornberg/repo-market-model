"""Tests for `repo_model.event_eval`.

The event holdout exists because the rolling-origin window expands: by the time
a late fold scores one stress episode it has trained on every earlier one. So
the thing worth testing hardest is the boundary -- that the training set stops
where it is supposed to, that the scored rows are exactly the declared window,
and that a label computed at the event edge cannot see across it.

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

The run says nothing about the exceedance report or the journal; no mutation
was planted in either.
"""

import json
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from repo_model.event_eval import (
    EventWindowReport,
    LookAheadError,
    SplitError,
    _assert_window_is_clean,
    append_record,
    config_digest,
    evaluate_event_window,
    load_event_windows,
    read_journal,
    trailing_percentile,
    trailing_threshold_path,
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
        kwargs = dict(
            dates=PANEL_DATES,
            y=PANEL_VALUES,
            fit_predict=flat_predictor(),
            event_start=EVENT_START,
            event_end=EVENT_END,
            purge=3,
            taus=TAUS,
            model_config={"model": "persistence", "seed": 0},
            journal_path=self.journal,
            window_name="feb-2026",
            window_checksum="abc123",
        )
        kwargs.update(overrides)
        positional = (
            kwargs.pop("dates"),
            kwargs.pop("y"),
            kwargs.pop("fit_predict"),
            kwargs.pop("event_start"),
            kwargs.pop("event_end"),
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


class LabelLeakageTests(unittest.TestCase):
    """Contract test 2's shape, applied to the label at the event edge.

    A stress label defined against a trailing percentile is a learned
    parameter. If its window reaches forward -- by including the current row,
    by centring, or by being fitted on the whole series -- then the label on the
    first day of an event window is informed by the event itself, and every
    score computed against it is circular.
    """

    WINDOW = 10
    PROBABILITY = 0.9

    def setUp(self):
        self.dates = business_days(date(2026, 1, 5), 40)
        self.values = [4.30 + 0.01 * (index % 5) for index in range(len(self.dates))]
        self.event_index = 25
        self.event_start = self.dates[self.event_index]

    def shock_from(self, index, factor=50.0):
        """Every row at or after `index` moved. Earlier rows untouched."""

        return [
            value + factor if position >= index else value
            for position, value in enumerate(self.values)
        ]

    def test_the_label_at_the_event_edge_ignores_the_event_and_everything_after(self):
        before = trailing_percentile(
            self.values, self.event_index, self.WINDOW, self.PROBABILITY
        )
        after = trailing_percentile(
            self.shock_from(self.event_index),
            self.event_index,
            self.WINDOW,
            self.PROBABILITY,
        )
        self.assertEqual(
            after,
            before,
            msg="the label at event_start moved when the event window was shocked",
        )

    def test_the_current_row_is_excluded_from_its_own_threshold(self):
        """The off-by-one that would make the label see one day of the event."""

        shocked = list(self.values)
        shocked[self.event_index] += 100.0
        self.assertEqual(
            trailing_percentile(shocked, self.event_index, self.WINDOW, self.PROBABILITY),
            trailing_percentile(
                self.values, self.event_index, self.WINDOW, self.PROBABILITY
            ),
        )

    def test_the_shock_is_visible_somewhere(self):
        """Guards the two tests above from passing because nothing moved."""

        shocked = self.shock_from(self.event_index)
        later = self.event_index + self.WINDOW
        self.assertNotEqual(
            trailing_percentile(shocked, later, self.WINDOW, self.PROBABILITY),
            trailing_percentile(self.values, later, self.WINDOW, self.PROBABILITY),
            msg="the shock changed no threshold at all; the leakage tests have no power",
        )

    def test_a_full_sample_threshold_would_differ_from_the_trailing_one(self):
        """The comparison the tests above would be vacuous without.

        If a trailing threshold and a whole-series threshold coincided on this
        panel, a leaky implementation would pass by accident.
        """

        shocked = self.shock_from(self.event_index)
        trailing = trailing_percentile(
            shocked, self.event_index, self.WINDOW, self.PROBABILITY
        )
        full_sample = trailing_percentile(
            shocked, len(shocked), len(shocked), self.PROBABILITY
        )
        self.assertNotEqual(trailing, full_sample)

    def test_every_threshold_on_the_path_uses_only_earlier_rows(self):
        path = trailing_threshold_path(self.values, self.WINDOW, self.PROBABILITY)
        for offset in range(len(path)):
            index = self.WINDOW + offset
            shocked = self.shock_from(index)
            self.assertEqual(
                trailing_threshold_path(shocked, self.WINDOW, self.PROBABILITY)[offset],
                path[offset],
                msg=f"threshold at row {index} moved when row {index} onward moved",
            )

    def test_insufficient_history_raises_rather_than_shortening_the_window(self):
        with self.assertRaisesRegex(SplitError, "needs 10"):
            trailing_percentile(self.values, 5, self.WINDOW, self.PROBABILITY)

    def test_degenerate_window_and_probability_are_rejected(self):
        with self.assertRaisesRegex(SplitError, "window must be at least 1"):
            trailing_percentile(self.values, 20, 0, self.PROBABILITY)
        with self.assertRaisesRegex(SplitError, "probability must be in"):
            trailing_percentile(self.values, 20, self.WINDOW, 1.5)


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
        self.assertEqual(entry["window_checksum"], "abc123")
        self.assertEqual(entry["purge_days"], 3)
        self.assertEqual(entry["scored_rows"], len(report.scored_dates))
        self.assertEqual(entry["train_rows"], report.train_rows)
        self.assertTrue(entry["evaluated_at"].startswith("20"))
        self.assertTrue(entry["git_rev"])
        self.assertEqual(len(entry["config_sha256"]), 64)

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

    FIXTURE = {
        "windows": [
            {
                "name": "sep-2019",
                "start": "2019-09-16",
                "end": "2019-09-20",
                "checksum": "0" * 64,
            },
            {
                "name": "mar-2020",
                "start": "2020-03-09",
                "end": "2020-03-20",
                "checksum": "1" * 64,
            },
        ]
    }

    def test_a_well_formed_fixture_parses(self):
        windows = load_event_windows(self.FIXTURE)
        self.assertEqual([w.name for w in windows], ["sep-2019", "mar-2020"])
        self.assertEqual(windows[0].start, date(2019, 9, 16))
        self.assertEqual(windows[1].end, date(2020, 3, 20))
        self.assertEqual(windows[0].checksum, "0" * 64)

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
                    "checksum": "deadbeef",
                }
            ]
        )[0]
        report = evaluate_event_window(
            PANEL_DATES,
            PANEL_VALUES,
            flat_predictor(),
            window.start,
            window.end,
            3,
            taus=TAUS,
            model_config={"model": "persistence"},
            journal_path=Path(directory.name) / "events.jsonl",
            window_name=window.name,
            window_checksum=window.checksum,
        )
        self.assertEqual(report.window, window)


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
