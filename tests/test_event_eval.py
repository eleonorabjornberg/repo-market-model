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

Mutation record, the conditional exceedance block (8 September 2026). The
evaluator's gap is derived now, so the `purge=0` subtests above are gone --
`max_release_lag_days` refuses a zero maximum and an unpurged knowledge holdout
is no longer expressible through the declared path. Two of the ten kills the
`clears_purge` mutation produced were those subtests, so that mutation would now
kill eight rather than ten; the eight are the assertion failures, and the
boundary is still what they are about. `WindowGuardTests` drives
`_assert_window_is_clean` with a bare integer and is untouched by the
derivation, which is where the `purge=0` shape still gets exercised.

Four mutations, each against a copy of the tree under `$HOME` carrying `data/`,
`.github/` and `metadata/`, `-B` with `PYTHONDONTWRITEBYTECODE=1` and
`__pycache__` cleared, control green before each:

  * **The covariate never reaches the design.** `FittedArx.design_row` reads the
    declared regressor off the feature row and then discards it for the fitted
    imputation, so the covariate arrives through the signature and not at the
    model. Kills 2: `test_the_arx_is_scored_on_the_knowledge_holdout_window`
    here, and `FittedArxTests::test_an_unobserved_regressor_is_never_coerced_to_zero`
    in `tests/test_baseline.py`. The acceptance test dies on the clause that is
    the criterion -- the curve goes flat -- which is what
    `FEATURE_ROW_PLATEAU` exists to make possible. Two variants of the same
    idea were run and both kill it too: the predictor reading `feature_rows[0]`
    for every day (3 kills), and the evaluator handing every day the first
    day's feature row (8 kills, six of them in `FeatureRowTests`).

  * **The declaration check downgraded to a no-op.** Kills exactly 1:
    `test_a_predictor_that_reads_outside_the_declaration_is_refused`. One kill
    is the honest number -- the check has one job and nothing else observes it
    -- and the test asserts on the journal as well as the exception, so a guard
    that stopped raising would still fail on a line claiming a window was scored
    under a gap sized over the wrong sources.

  * **The gap taken from a constant instead of derived.** Kills 10, across
    `DerivedGapTests`, `PurgeBoundaryTests` and
    `tests/test_cli_eval.py::test_both_commands_report_the_features_and_the_sources_they_derived`.
    The last is the one worth having: it fails on the CLI reporting a gap that
    does not follow from what it was asked for, which is the damage, rather than
    on the derivation being absent.

  * **The boring one.** The climatology's curve, checked for having not moved.
    Run two ways. As a code mutation -- the denominator changed to `n + 2`, the
    Laplace correction `climatology_exceedance` refuses at length -- it kills 2:
    `ClimatologyExceedanceTests::test_the_curve_is_the_fraction_of_training_spreads_strictly_above_tau`
    and `test_the_climatology_curve_is_flat_across_the_same_window`. As the
    check the widening actually needed, the pre-block `climatology_exceedance`
    was loaded from the previous commit and called with the old four-argument
    convention on the same training rows: the curves are equal, element for
    element, on every scored day. The widening is additive for the implementer
    that already existed.
"""

import inspect
import json
import math
import sys
import tempfile
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from repo_model import contract, event_eval
from repo_model.baseline import (
    ExceedanceCurves,
    arx_exceedance,
    climatology_exceedance,
    threshold_exceedance,
)
from repo_model.contract import UndeclaredFeatureError, event_window_digest
from repo_model.data import DailyObservation
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
from repo_model.registry import RegistryContractError

# The registry fixture, imported rather than copied. `tests/test_baseline.py`
# already declares "a registry that prices the sources this feature set uses at
# exactly `purge` days", and the gap is now derived on this path too, so this
# file needs the same fixture for the same reason. A third copy would be a third
# thing to keep in step with `max_release_lag_days`, and the copies would agree
# until one of them did not.
from test_baseline import (
    DECISION_TIME,
    THRESHOLD_VARIABLE,
    declared_registry,
    mixed_registry,
)


# The exceedance family declared in AGENT_CONTRACT.md, "Decided: stress target
# and event holdouts". The evaluator takes it as an argument rather than naming
# it, for the same reason it takes the windows as an argument; this is the
# fixture, not the declaration.
TAUS = (5.0, 10.0, 20.0, 50.0)

#: The covariate the widened interface exists to carry, and the feature set that
#: declares it. `spread_bps` is in the declaration because every model here reads
#: its own autoregressive term; a declaration that omitted it would be refused,
#: which is the check working rather than a fixture bug.
COVARIATE = "on_rrp"
FEATURES = ("spread_bps", COVARIATE)


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
EVENT_START = date(2026, 2, 2)
EVENT_END = date(2026, 2, 6)

#: The three rows that are ever read as a feature row for a day in the window at
#: `purge=3`: the last training row (2026-01-29), the row inside the gap ahead
#: of the window (2026-01-30), and the window's own first day (2026-02-02).
#:
#: **Their spreads are equal and their covariate is not**, and that is the whole
#: construction. On this panel a model that reads only `spread_bps` produces the
#: same curve on every scored day, and a model that reads `on_rrp` does not. So
#: "the curve moves across scored days" is a statement about the covariate
#: reaching the model, rather than about conditioning in general -- and the
#: acceptance test can be the mutation target it is supposed to be instead of
#: passing on an ARX whose covariate was dropped.
FEATURE_ROW_PLATEAU = (18, 19, 20)
PLATEAU_SPREAD_BPS = 21.0


def _spread_bps(index):
    if index in FEATURE_ROW_PLATEAU:
        return PLATEAU_SPREAD_BPS
    return 18.0 + 5.0 * math.sin(index * 0.9) + 0.25 * index


def _covariate(index):
    """Deliberately not collinear with the spread: a singular design is refused."""

    return 300.0 + 50.0 * math.cos(index * 0.41)


def panel_row(index, when, **overrides):
    """One `DailyObservation` whose `spread_bps` is `_spread_bps(index)`.

    `iorb` is pinned at zero and `sofr` carries the whole spread, so the target
    is exactly the number this fixture names rather than the number a rounding
    of `100 * (sofr - iorb)` happens to produce.
    """

    values = {
        "sofr": _spread_bps(index) / 100.0,
        "iorb": 0.0,
        COVARIATE: _covariate(index),
    }
    values.update(overrides)
    return DailyObservation(when, values)


PANEL_ROWS = [panel_row(index, when) for index, when in enumerate(PANEL_DATES)]

#: Read off the rows rather than declared beside them. A parallel list would be
#: a second statement of the target, and `100 * (sofr - iorb)` is not exact.
PANEL_VALUES = [row.spread_bps for row in PANEL_ROWS]


def flat_predictor(probabilities=(0.9, 0.7, 0.4, 0.1), features_read=("spread_bps",)):
    """A `fit_predict` that ignores its inputs and returns a fixed curve."""

    def fit_predict(train_rows, feature_rows, taus):
        return ExceedanceCurves(
            tuple(tuple(probabilities) for _ in feature_rows), tuple(features_read)
        )

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

        `purge=` is likewise a convenience and no longer an argument of the
        function: the gap is derived from the declared feature set, so a test
        that wants a known gap declares a registry that produces it. Same move
        `tests/test_baseline.py` made when the rolling path's gap became
        derived, and `declared_registry` is that file's fixture, imported.
        Tests that are *about* the derivation pass `registry=` themselves.
        """

        kwargs = dict(
            observations=PANEL_ROWS,
            fit_predict=flat_predictor(),
            purge=3,
            features=FEATURES,
            decision_time=DECISION_TIME,
            taus=TAUS,
            model_config={"model": "persistence", "seed": 0},
            journal_path=self.journal,
        )
        kwargs.update(overrides)
        purge = kwargs.pop("purge")
        kwargs.setdefault("registry", declared_registry(purge, kwargs["features"]))
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
            kwargs.pop("observations"),
            kwargs.pop("fit_predict"),
            kwargs.pop("window"),
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
        """Gap 0 is absent because it is no longer expressible; see below.

        `max_release_lag_days` refuses to return zero, so a declared registry
        cannot produce an unpurged run. The two rows the old `0` and `1` cases
        pinned were the same row, so nothing this test could distinguish was
        lost with it -- but the `purge=0` subtests were two of the ten failures
        the `clears_purge` mutation produced, and that is recorded below rather
        than left to be noticed.
        """

        expected = {
            1: date(2026, 1, 30),
            2: date(2026, 1, 30),
            3: date(2026, 1, 29),
            4: date(2026, 1, 28),
            5: date(2026, 1, 27),
        }
        for purge, last_train in expected.items():
            with self.subTest(purge=purge):
                self.assertEqual(self.evaluate(purge=purge).last_train_date, last_train)

    def test_every_training_row_clears_the_gap_independently(self):
        """Recomputed here with a day count, not the module's comparison."""

        for purge in (1, 2, 3, 5):
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

        def spy(train_rows, feature_rows, taus):
            seen["train"] = tuple(row.date for row in train_rows)
            seen["feature"] = tuple(row.date for row in feature_rows)
            return ExceedanceCurves(
                tuple((0.9, 0.7, 0.4, 0.1) for _ in feature_rows), ("spread_bps",)
            )

        report = self.evaluate(fit_predict=spy, purge=3)
        self.assertGreater((EVENT_START - max(seen["train"])).days, 3)
        self.assertTrue(all(when < EVENT_START for when in seen["train"]))
        self.assertFalse(set(seen["train"]) & set(report.scored_dates))
        # The feature rows are a different question and get a different answer:
        # 2026-01-30 sits inside the gap ahead of the window and never trains,
        # and it is still the last row publishable before 2026-02-03.
        self.assertIn(date(2026, 1, 30), seen["feature"])
        self.assertNotIn(date(2026, 1, 30), seen["train"])

    def test_the_gap_is_derived_and_cannot_be_supplied(self):
        """There is no `purge` argument, and zero is not expressible.

        The flag would be reached for at exactly the moment it must not be --
        when the training set that cleared the gap turned out to be short -- and
        the row it would admit is a row published after the window opened. The
        second half is `max_release_lag_days` refusing a zero maximum, which
        this path now inherits along with the derivation.
        """

        self.assertNotIn("purge", inspect.signature(evaluate_event_window).parameters)

        unpurged = {
            source: {
                "release_lag": {
                    "basis": "record_date",
                    "unit": "calendar_days",
                    "days": 0,
                    "available_time": "00:00",
                    "timezone": "America/New_York",
                }
            }
            for source in contract.sources_for_features(FEATURES)
        }
        with self.assertRaisesRegex(RegistryContractError, "nonzero purge"):
            self.evaluate(registry=unpurged)

    def test_an_unclassifiable_feature_is_refused_before_any_row_is_selected(self):
        with self.assertRaises(UndeclaredFeatureError):
            self.evaluate(features=("spread_bps", "not_a_column"))
        self.assertEqual(read_journal(self.journal), ())

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
                "features",
                "sources",
                "field_sources",
                "purge_days",
                "train_rows",
                "last_train_date",
                "taus",
                "scored_dates",
                "realized",
                "exceedance",
                "feature_dates",
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

        def short(train_rows, feature_rows, taus):
            return ExceedanceCurves(((0.9, 0.7, 0.4, 0.1),), ("spread_bps",))

        with self.assertRaisesRegex(SplitError, "returned 1 rows"):
            self.evaluate(fit_predict=short)

    def test_a_predictor_that_returns_bare_curves_is_refused(self):
        """The account of what was read is part of the return, not optional.

        A predictor that returned only curves would make no claim about the
        columns it read, and the declaration check would then have nothing to
        compare against and would pass by default -- the gap sized over a
        feature set nobody verified, which is the hazard the widening opened.
        """

        def bare(train_rows, feature_rows, taus):
            return [(0.9, 0.7, 0.4, 0.1) for _ in feature_rows]

        with self.assertRaisesRegex(SplitError, "must return an ExceedanceCurves"):
            self.evaluate(fit_predict=bare)

    def test_taus_must_be_a_strictly_ascending_non_empty_family(self):
        with self.assertRaisesRegex(SplitError, "at least one threshold"):
            self.evaluate(taus=())
        with self.assertRaisesRegex(SplitError, "strictly ascending"):
            self.evaluate(taus=(10.0, 5.0))


class ConditionalExceedanceTests(EvaluatorHarness):
    """A declared covariate reaching a model on the knowledge holdout.

    Before this block `FitPredict` passed one series of values, so nothing
    conditional could be scored here at all. The only expressible predictor was
    one conditioning on nothing -- the climatology -- and a climatology is what
    a Brier skill score is measured *against*, so the one evaluation this
    repository was designed around had nothing on the other side of the
    comparison.

    The fixture is built so that the two facts below are about the covariate and
    not about conditioning in general: at `purge=3` exactly three rows are ever
    read as a feature row for a day in this window, and `FEATURE_ROW_PLATEAU`
    gives all three the same `spread_bps` and different `on_rrp`. A model that
    reads only the spread produces one curve on every scored day here. A model
    that reads the covariate does not.
    """

    ARX_MINIMUM_HISTORY = 10

    def arx_report(self, **overrides):
        kwargs = dict(
            fit_predict=arx_exceedance(
                (COVARIATE,), minimum_history=self.ARX_MINIMUM_HISTORY
            ),
            features=FEATURES,
            model_config={"model": "arx", "regressors": [COVARIATE]},
        )
        kwargs.update(overrides)
        return self.evaluate(**kwargs)

    def test_the_arx_is_scored_on_the_knowledge_holdout_window(self):
        """The block's acceptance criterion, and its own mutation target.

        An ARX declaring a covariate, fitted on rows that all cleared the purge
        gap ahead of a declared `EventWindow`, producing an exceedance curve per
        scored day -- **and the curve moves across scored days**. That last
        clause is the criterion. A widening that plumbed the covariate through
        the signature without the model ever reading it would produce a flat
        curve, pass every weaker assertion here, and be indistinguishable from
        the climatology.

        The premise that makes this the mutation target is asserted first rather
        than left in a comment: the distinct feature rows carry equal spreads.
        Without it "the curve moves" would also be satisfied by an autoregressive
        model with no covariate at all, and the test would not detect the one
        change it exists to detect.
        """

        report = self.arx_report()

        # The premise. The rows the curves are conditioned on differ only in the
        # covariate, so movement can come from nowhere else.
        feature_rows = {when: PANEL_ROWS[PANEL_DATES.index(when)]
                        for when in report.feature_dates}
        self.assertGreater(len(feature_rows), 1, msg="one feature row cannot move")
        self.assertEqual(
            {row.spread_bps for row in feature_rows.values()},
            {PLATEAU_SPREAD_BPS},
        )
        self.assertEqual(
            len({row.values[COVARIATE] for row in feature_rows.values()}),
            len(feature_rows),
        )

        # Scored: one curve per day in the declared window, over the declared
        # taus, and every day of the window is there.
        self.assertEqual(
            list(report.scored_dates),
            [when for when in PANEL_DATES if EVENT_START <= when <= EVENT_END],
        )
        self.assertEqual(len(report.exceedance), len(report.scored_dates))
        for curve in report.exceedance:
            self.assertEqual(len(curve), len(TAUS))

        # Knowledge holdout: nothing in or near the window trained.
        self.assertGreater((EVENT_START - report.last_train_date).days, report.purge_days)
        self.assertEqual(report.record.holdout_role, KNOWLEDGE_HOLDOUT)

        # The criterion.
        self.assertGreater(
            len(set(report.exceedance)),
            1,
            msg="the ARX's curve is the same on every scored day; the covariate "
            "reached the signature and not the model, which is the climatology "
            "wearing a second name",
        )

    def test_the_climatology_curve_is_flat_across_the_same_window(self):
        """The other half of the pair, and mutation 4's target.

        Both facts together are what say the widening carries information rather
        than shape: the conditional model's curve moves and the unconditional
        one's does not, on one window, at one gap. The numbers are pinned
        against an independent count so that "unchanged by the widening" is
        checkable rather than asserted.
        """

        report = self.evaluate(
            fit_predict=climatology_exceedance(
                minimum_history=self.ARX_MINIMUM_HISTORY
            ),
            model_config={"model": "climatology"},
        )
        self.assertEqual(len(set(report.exceedance)), 1)

        history = [
            row.spread_bps
            for row in PANEL_ROWS
            if row.date <= report.last_train_date
        ]
        self.assertEqual(len(history), report.train_rows)
        self.assertEqual(
            report.exceedance[0],
            tuple(
                sum(1 for value in history if value > tau) / len(history)
                for tau in TAUS
            ),
        )

    def test_a_predictor_that_reads_outside_the_declaration_is_refused(self):
        """The lock on the door the widening opened.

        A covariate that reaches a model without being declared means the gap
        was sized over the wrong sources -- computed correctly, in the
        flattering direction, because the undeclared column's release lag was
        never in the maximum. The check is `baseline._check_fitter_stayed_inside`
        and it is the rolling path's, imported rather than restated.

        Nothing is journalled: the refusal comes before the record, so a run
        that was purged against the wrong sources leaves no line claiming a
        single-evaluation budget was spent on it.
        """

        with self.assertRaises(LookAheadError) as caught:
            self.arx_report(features=("spread_bps",))
        self.assertIn(COVARIATE, str(caught.exception))
        self.assertEqual(read_journal(self.journal), ())

    def test_declaring_more_than_the_predictor_reads_is_allowed(self):
        """Conservative and legible, so it is not refused.

        Declaring a column the model never reads purges more than the evidence
        requires; it costs training rows and it is visible in the report. The
        containment is one-directional on purpose.
        """

        report = self.evaluate(
            fit_predict=climatology_exceedance(
                minimum_history=self.ARX_MINIMUM_HISTORY
            ),
            features=FEATURES,
        )
        self.assertEqual(report.features, FEATURES)


#: The regime variable, and the feature set a threshold model on this panel
#: declares. `THRESHOLD_VARIABLE` is `tests/test_baseline.py`'s, imported for the
#: reason `declared_registry` is: it resolves to `nyfed_tgcr`, a source neither
#: `spread_bps` nor `on_rrp` draws on, so declaring it widens the *source* set
#: and not merely the feature list. A regime read off `on_rrp` would share
#: `fred_macro_latest_vintage` with `iorb` and the second half of the acceptance
#: criterion -- that the derived purge reflects the column's `(source, field)`
#: pair -- would assert nothing.
#:
#: `REGIME_REGRESSORS` is `on_rrp` and the regime variable is not, deliberately.
#: A regime variable that were also a regressor would be reported through the
#: design alone, and the read this block exists to check would be invisible.
REGIME_REGRESSORS = (COVARIATE,)
REGIME_FEATURES = FEATURES + (THRESHOLD_VARIABLE,)


def regime_panel_rows(seed=20260909):
    """`PANEL_ROWS` plus a `tgcr` column, and nothing else touched.

    Built by copying each row's values rather than by widening `panel_row`, so
    that **no number in this file moves**: the spreads are `PANEL_ROWS`'
    spreads, `on_rrp` is `PANEL_ROWS`' covariate, and the climatology and ARX
    figures the surrounding tests pin are computed from rows this function never
    sees. `regime_frame` in `tests/test_baseline.py` derives its own rows from
    `regressor_frame` the same way and for the same reason.

    The seed is that file's, and the values sit in the same narrow band, so a
    split exists on the 19 rows that clear a three-day gap ahead of this window
    and both regimes stay populated. The property that matters and is asserted
    where it is used: the three rows ever read as a feature row here do not all
    fall in one regime.
    """

    state = seed
    rows = []
    for row in PANEL_ROWS:
        state = (1103515245 * state + 12345) % (2 ** 31)
        values = dict(row.values)
        values[THRESHOLD_VARIABLE] = 4.28 + (state % 97) / 1000.0
        rows.append(DailyObservation(row.date, values))
    return rows


REGIME_PANEL_ROWS = regime_panel_rows()


class RegimeDeclarationTests(EvaluatorHarness):
    """A covariate that chooses the model, on the knowledge-holdout path.

    `da78dea` put the regime variable through the *rolling* path's lock. This is
    the second path, and it has its own declaration check: `event_eval` sizes
    the gap from the caller's feature set before anything is fitted and then
    verifies `ExceedanceCurves.features_read` against it, through the same
    `baseline._check_fitter_stayed_inside` the rolling path uses. Two evaluation
    paths, two checks; the regime variable had been through one of them.

    The failure that was available is the one this repository keeps finding one
    level at a time: a predictor that consults the regime variable to pick a
    regime, reports only its regressors, and gets a gap sized over the wrong
    fields. The arithmetic is right, the set is wrong, and the error is in the
    flattering direction because the undeclared column's release lag is the one
    missing from the maximum.

    The registry is `mixed_registry` rather than `declared_registry` for the
    reason that file gives: under a uniform registry every source costs the same
    and the derived purge would be the same number whether the regime variable
    was declared or not, so "the purge reflects the column" would pass while
    demonstrating nothing.

    Mutation record
    ===============

    Unmutated control first: the suite green before and after every run below --
    OK, zero `expectedFailure` -- stdlib only, run from a copy
    under `$HOME` with `data/`, `.github/`, `metadata/`, `.gitignore`, the root
    Markdown and `docs/PROJECT_STATUS.md` carried across, because
    `tests/test_docs_freshness.py` reads those and their absence is two kills
    that look real and are not. `-B` with `PYTHONDONTWRITEBYTECODE=1` and
    `__pycache__` cleared before each run.

    1. **`threshold_exceedance` reports its regressors alone.**
       `ExceedanceCurves(..., model.features_read)` became
       `ExceedanceCurves(..., declared)`, so the returned claim is
       `("on_rrp",)` and the regime variable is not in it. The predictor still
       fits, still returns a curve per scored day, and still switches regimes
       across the fitted cutoff -- only the account of what it read is short by
       the one column this block is about. **2 tests fail:**

       * `RegimeDeclarationTests::test_the_regime_variable_is_declared_on_the_holdout_path_too`
         -- `AssertionError: LookAheadError not raised`. This class's acceptance
         criterion. The undeclared run, which must be refused, completes and is
         journalled: a knowledge holdout purged over
         `spread_bps` and `on_rrp` while the model was also reading `tgcr`.
       * `tests/test_baseline.py::ThresholdExceedanceTests::test_it_reports_the_regime_variable_as_well_as_its_regressors`
         -- `AssertionError: Tuples differ: ('sofr_volume',) != ('spread_bps',
         'sofr_volume', 'tgcr')`.

       The second kill was not expected when this record was drafted, and it is
       worth saying why it happens rather than quietly counting it. That test
       reads `ExceedanceCurves.features_read` -- the predictor's claim -- and
       not `FittedThreshold.features_read`, so it sits on the same claim the
       evaluator checks, one level lower. It reports the wrong tuple; the
       acceptance test reports the *consequence*, an unrefused evaluation with
       a gap sized over the wrong fields. Nothing else in
       `tests/test_baseline.py` sees the mutation: the rolling path checks the
       fitted model's tuple, which is untouched.

    2. **The curve re-derived from the pooled residuals rather than taken from
       `FittedThreshold.predict_stress`.** `model.predict_stress(row, taus)`
       became `_exceedance_from_residuals` over `model.residuals` about a single
       regime-independent centre -- the `"low"` coefficients applied to every
       feature row's design row. The two agree exactly on any row the low regime
       would have claimed anyway and diverge across the cutoff. **1 test
       fails:**

       * `tests/test_baseline.py::ThresholdExceedanceTests::test_the_curve_moves_across_the_fitted_cutoff`
         -- `AssertionError: (0.9266951315779685, 0.9145730036194362,
         0.7952526956667105, 0.478193103494276) == (same tuple)`. One design row
         scored under two regimes gave one curve.

       **`test_the_law_is_the_one_the_fitted_model_already_reports` survives**,
       and that is the fixture finding the brief anticipated rather than a
       weakness in the test: `regime_frame`'s last four rows -- the mixin's
       feature rows -- all fall in the low regime, so anchoring every row on the
       low coefficients reproduces the model's own curves character for
       character. A frame with no two rows straddling the fitted threshold
       cannot see this mutation at all. The test that does see it is the one
       above, and it exists for this reason: it *constructs* the straddling pair
       from one row and its copy with the regime variable moved across the
       threshold, rather than hoping the frame supplies one.

       Nothing in this file fails either, for the same reason in a different
       shape: this window's feature rows do fall in both regimes, but no two of
       them differ *only* in the regime variable, so a flattened centre moves
       the numbers without moving anything `RegimeDeclarationTests` asserts.
       This class asserts the declaration; the curve's construction is
       `tests/test_baseline.py`'s to hold.

    3. **The threshold estimated over the feature rows as well as the training
       rows.** `fit_threshold(train_rows, ...)` became
       `fit_threshold(tuple(train_rows) + tuple(feature_rows), ...)`, so the
       imputations, the threshold, the regime assignment and the residual law
       are all fitted on rows from inside the window. **4 tests fail, 2 as
       errors:**

       * `RegimeDeclarationTests::test_the_regime_variable_is_declared_on_the_holdout_path_too`
         -- `repo_model.splits.SplitError: training frame dates must be strictly
         ascending and unique; 2026-01-30 at position 20 follows 2026-01-30`.
         Three of this window's five scored days read the same feature row, so
         the concatenation repeats a date and `ensure_strictly_ascending` refuses
         the frame. The leak is caught by the shape it has to take to happen
         here, which is luck rather than a guard -- worth recording as such.
       * `tests/test_baseline.py::ThresholdExceedanceTests::test_the_curve_moves_across_the_fitted_cutoff`
         -- the same `SplitError` at `2026-02-09`, from the constructed pair
         carrying its source row's date.
       * `tests/test_baseline.py::ThresholdExceedanceTests::test_the_law_is_the_one_the_fitted_model_already_reports`
         -- `AssertionError: Tuples differ`, the control fitting on the training
         rows and the mutant on four more. This is the kill that does not depend
         on a date collision, and the one that would still fire if the
         concatenation were sorted.
       * `tests/test_baseline.py::ThresholdExceedanceTests::test_a_training_frame_below_the_minimum_is_refused`
         -- `AssertionError: ValueError not raised`. Four feature rows pushed a
         19-row frame over a 20-row minimum, so a refusal that belongs to the
         predictor stopped firing because of rows it was never allowed to fit
         on.

       `test_a_window_with_no_second_regime_is_refused_not_flattened` survives:
       the four feature rows do supply a moving `tgcr`, but four rows cannot
       make a regime of the five `fit_threshold` requires, so the refusal still
       fires. The fallback the brief warns about is one row short of arriving
       through this leak, which is not a margin to rely on.

    4. **The boring one, and it is boring.** No mutation: the claim is that this
       block moved no existing number. `climatology_exceedance` and
       `arx_exceedance` were run on `PANEL_ROWS` at `purge=3` through
       `evaluate_event_window`, and the persistence benchmark and the real
       registry's derived purge through `_derive_purge`, against a pristine
       `git archive HEAD` checkout and against the working tree. The two outputs
       are **byte-identical**: the ARX's five curves, the climatology's flat
       one, `train_rows=19`, `last_train_date=2026-01-29`, and `35c3125`'s
       six-day purge over `(fred_macro_latest_vintage, IORB)` and
       `(nyfed_sofr, SOFR)` with its fold count and MAE unchanged. **0 tests
       fail.** Nothing this block adds reads `PANEL_ROWS`: `regime_panel_rows`
       copies each row and adds a column, and the registry it evaluates under is
       a different fixture.

    Why the curve comes off the fitted model
    ========================================

    `FittedThreshold.predict_stress` is `_exceedance_from_residuals` over the
    pooled leave-one-out law the model already fits, anchored on the
    **regime's** point forecast. Re-deriving it here would be a second opinion
    about one distribution, and mutation 2 shows what that second opinion costs:
    it agrees about the centre and disagrees across the cutoff, which is exactly
    the behaviour this implementer was added to score. The regime enters through
    the centre and nowhere else -- the law is one law, pooled, by
    `test_one_pooled_law_because_the_interface_declares_one` -- so a curve built
    from the residual vector without asking the model which regime it is in is
    an `arx_exceedance` wearing a threshold model's name.

    The discovery-guard gap in the brief is already closed
    =====================================================

    The brief for this block records that `tests/test_contract.py`'s
    `_forecast_implementations` has no counterpart for `ExceedancePredictor` and
    asks that one be left for its own block. That is a stale premise:
    `tests/test_baseline.py::ExceedancePredictorCoverageTests` is the
    counterpart and it landed already, discovering factories by their
    `-> ExceedancePredictor` annotation exactly as `_forecast_implementations`
    discovers implementers by subclass. It fired on the first run of this block,
    before any test was written -- `['threshold_exceedance'] != []` -- which is
    the guard doing its job and is why `ThresholdExceedanceTests` exists. No
    guard was built here; a conformance case was added because the guard that
    was already there demanded one.
    """

    MINIMUM_HISTORY = 10

    #: Two numbers, so that declaring the regime variable *changes* the gap. The
    #: base prices every source `FEATURES` resolves to; the regime price is
    #: `nyfed_tgcr`'s alone and is the larger, so the derived purge under
    #: `REGIME_FEATURES` is the regime one and under `FEATURES` is the base one.
    BASE_PURGE = 2
    REGIME_PURGE = 3

    def regime_report(self, **overrides):
        kwargs = dict(
            observations=REGIME_PANEL_ROWS,
            fit_predict=threshold_exceedance(
                REGIME_REGRESSORS,
                THRESHOLD_VARIABLE,
                minimum_history=self.MINIMUM_HISTORY,
            ),
            features=REGIME_FEATURES,
            registry=mixed_registry(self.BASE_PURGE, self.REGIME_PURGE),
            model_config={
                "model": "threshold",
                "regressors": list(REGIME_REGRESSORS),
                "threshold_variable": THRESHOLD_VARIABLE,
            },
        )
        kwargs.update(overrides)
        return self.evaluate(**kwargs)

    def test_the_regime_variable_is_declared_on_the_holdout_path_too(self):
        """The block's acceptance criterion, and its own mutation target.

        Two runs of one predictor over one panel, differing only in what the
        caller declared.

        Undeclared, the regime variable is a column the model reads and the gap
        was not sized over: refused, `LookAheadError`, naming the column. The
        refusal comes before the record, so a run purged against the wrong
        fields leaves no journal line claiming a single-evaluation budget was
        spent on it.

        Declared, the same run scores -- and the gap it scored under is the
        regime variable's. `nyfed_tgcr` is in the report's `field_sources` as
        the pair `(nyfed_tgcr, TGCR)` and projected into `sources`, and the
        purge is the larger of the two prices rather than the base one. That
        second half is why the registry is mixed: under a uniform one the number
        would be the same either way and this would assert that a column had
        been added to a tuple.

        The premises are asserted rather than left in a comment. The regime
        variable is not a regressor, so the design cannot be reporting it; and
        the two prices differ, so the purge has somewhere to move.
        """

        self.assertNotIn(THRESHOLD_VARIABLE, REGIME_REGRESSORS)
        self.assertLess(self.BASE_PURGE, self.REGIME_PURGE)

        # Undeclared: read, not declared, refused by name -- and unjournalled.
        with self.assertRaises(LookAheadError) as caught:
            self.regime_report(features=FEATURES)
        self.assertIn(THRESHOLD_VARIABLE, str(caught.exception))
        self.assertEqual(read_journal(self.journal), ())

        # Declared: the same run, scored.
        report = self.regime_report()
        self.assertEqual(report.features, REGIME_FEATURES)
        self.assertEqual(
            list(report.scored_dates),
            [when for when in PANEL_DATES if EVENT_START <= when <= EVENT_END],
        )
        self.assertEqual(len(report.exceedance), len(report.scored_dates))
        self.assertEqual(report.record.holdout_role, KNOWLEDGE_HOLDOUT)

        # Knowledge holdout: nothing in or near the window trained.
        self.assertGreater(
            (EVENT_START - report.last_train_date).days, report.purge_days
        )

        # And the gap it was scored under is the regime variable's. The pair is
        # read from `contract` rather than typed, so a change to the field a
        # column resolves to is a failure here and not a stale literal.
        regime_pairs = contract.field_sources_for_features((THRESHOLD_VARIABLE,))
        self.assertEqual(len(regime_pairs), 1)
        self.assertIn(regime_pairs[0], report.field_sources)
        self.assertIn(regime_pairs[0][0], report.sources)
        self.assertNotIn(
            regime_pairs[0],
            contract.field_sources_for_features(FEATURES),
            msg="the regime variable's field is already in the undeclared set; "
            "declaring it cannot be shown to have widened anything",
        )
        self.assertEqual(report.purge_days, self.REGIME_PURGE)


class FeatureRowTests(EvaluatorHarness):
    """Which row each scored day is forecast from, and who decides.

    The training boundary is sized against `window.start`; the conditioning
    boundary is sized against each scored day. They are different questions and
    they get different answers, and the difference is what lets a curve move at
    all. A row inside the purge gap ahead of the window never trains and can
    still be the last row publishable before a day further into the window.
    """

    def test_each_scored_day_is_forecast_from_the_last_row_that_cleared_the_gap(self):
        """Recomputed here from a day count, not from the module's comparison."""

        report = self.evaluate(purge=3)
        for scored, feature in zip(report.scored_dates, report.feature_dates):
            with self.subTest(scored=scored):
                self.assertGreater((scored - feature).days, 3)
                later = [
                    when
                    for when in PANEL_DATES
                    if when > feature and (scored - when).days > 3
                ]
                self.assertEqual(later, [], msg="a later eligible row was passed over")

    def test_a_row_inside_the_gap_never_trains_and_may_still_be_read(self):
        """2026-01-30, at `purge=3`, for a window opening 2026-02-02.

        Three calendar days before the window opens, so it does not train. Three
        calendar days before 2026-02-03 is 2026-01-31, so by 2026-02-03 it has
        been published and reading it is not look-ahead. Both facts at once, on
        one row, because a test that stated only the first would read as a
        prohibition on ever touching it.
        """

        report = self.evaluate(purge=3)
        inside_the_gap = date(2026, 1, 30)
        self.assertLess(report.last_train_date, inside_the_gap)
        self.assertIn(inside_the_gap, report.feature_dates)

    def test_a_day_late_in_the_window_may_read_an_earlier_window_day(self):
        report = self.evaluate(purge=3)
        pairs = dict(zip(report.scored_dates, report.feature_dates))
        self.assertEqual(pairs[date(2026, 2, 6)], date(2026, 2, 2))
        self.assertIn(date(2026, 2, 2), report.scored_dates)

    def test_no_scored_day_is_ever_forecast_from_itself_or_later(self):
        for purge in (1, 3, 5):
            with self.subTest(purge=purge):
                report = self.evaluate(purge=purge)
                for scored, feature in zip(report.scored_dates, report.feature_dates):
                    self.assertLess(feature, scored)

    def test_the_predictor_is_handed_the_feature_rows_and_never_the_panel(self):
        """It cannot choose its own conditioning set, so it cannot read the day.

        The rows the predictor receives are exactly the ones the report names,
        in order, and there are as many as there are scored days.
        """

        seen = {}

        def spy(train_rows, feature_rows, taus):
            seen["feature"] = tuple(row.date for row in feature_rows)
            seen["train"] = tuple(row.date for row in train_rows)
            return ExceedanceCurves(
                tuple((0.9, 0.7, 0.4, 0.1) for _ in feature_rows), ("spread_bps",)
            )

        report = self.evaluate(fit_predict=spy, purge=3)
        self.assertEqual(seen["feature"], report.feature_dates)
        self.assertEqual(len(seen["feature"]), len(report.scored_dates))
        self.assertNotIn(EVENT_END, seen["feature"])

    def test_a_feature_row_that_does_not_clear_the_gap_raises(self):
        """The guard, driven directly: `_feature_index` cannot produce this.

        It is here because a rule only one function can reach is a rule that
        stops being checked the moment a second caller appears.
        """

        scored = [i for i, w in enumerate(PANEL_DATES) if EVENT_START <= w <= EVENT_END]
        feature = [index - 1 for index in scored]
        with self.assertRaisesRegex(LookAheadError, "does not clear the 3-day"):
            event_eval._assert_feature_rows_clear_the_gap(
                PANEL_DATES, feature, scored, 3
            )

    def test_a_feature_row_at_or_after_its_scored_day_raises(self):
        scored = [i for i, w in enumerate(PANEL_DATES) if EVENT_START <= w <= EVENT_END]
        with self.assertRaisesRegex(LookAheadError, "is not before it"):
            event_eval._assert_feature_rows_clear_the_gap(
                PANEL_DATES, list(scored), scored, 3
            )


class DerivedGapTests(EvaluatorHarness):
    """The gap follows from the declared feature set, and from nothing else."""

    def test_the_gap_follows_the_declaration_and_reaches_the_boundary(self):
        """Asserted as a relation between two feature sets, not against a literal.

        One registry, pricing two sources differently. Declaring the feature
        whose source costs more moves the gap, and moving the gap moves where
        training stops -- so the derivation reaches the numbers rather than only
        the report's own `purge_days` field.
        """

        registry = {
            "nyfed_sofr": self._priced(2),
            "fred_macro_latest_vintage": self._priced(2),
            "sec_nmfp": self._priced(9),
        }
        narrow = self.evaluate(features=("spread_bps",), registry=registry)
        wide = self.evaluate(
            features=("spread_bps", "mmf_assets"), registry=registry
        )

        self.assertEqual(narrow.purge_days, 2)
        self.assertEqual(wide.purge_days, 9)
        self.assertLess(wide.last_train_date, narrow.last_train_date)
        self.assertLess(wide.train_rows, narrow.train_rows)

    def test_the_report_carries_the_declaration_it_was_scored_under(self):
        report = self.evaluate(features=("spread_bps",), purge=4)
        self.assertEqual(report.features, ("spread_bps",))
        self.assertEqual(report.sources, contract.sources_for_features(("spread_bps",)))
        self.assertEqual(report.purge_days, 4)
        self.assertEqual(report.record.purge_days, 4)

    def test_the_real_registry_refuses_this_path_too_for_the_same_field(self):
        """The narrowed guard, and that the two paths narrowed together.

        **What this test asserted before this block.** That the real registry
        refused *any* feature set on this path, because `spread_bps` resolved
        to `fred_macro_latest_vintage` and that source's basis is
        `snapshot_retrieved_at` -- a basis the contract forbids mapping to
        zero, and one `max_release_lag_days` raises on unless every row carries
        `available_at`. `DailyObservation` carries none.

        **What it asserts now.** That the refusal is a fact about a field, and
        that this path refuses the same field the rolling path does. The
        harness declares `("spread_bps", "on_rrp")`, and `on_rrp` reads
        `fred_macro_latest_vintage.RRPONTSYD`, which declares no revision
        policy -- so this still raises, and now names `RRPONTSYD`. Drop
        `on_rrp` and the same registry prices the same source's `IORB`, which
        is what the rolling path's acceptance test pins; both halves are
        checked here, because the failure this block is one step away from is
        the two derivations drifting apart, and a test that only saw the
        refusal could not see the drift.

        **Still a correct guard firing, not a bug.** Before the gap became
        derived, the event path took it as an int and never touched a registry,
        so this refusal lived only in `cli_eval`; deriving it inside the
        evaluator moved it to where the two paths already agreed it belonged.
        Deriving it over fields narrows what it catches without moving where it
        lives. The resolution is still Track A's and the human's -- an
        `available_at` on the daily panel, or a declared `field_release_lags`
        entry for the H.4.1 weeklies -- and this test still goes red the day it
        is answered.

        `tests/test_baseline.py::test_two_features_on_one_source_price_differently`
        is the rolling path's half of the same fact.
        """

        real = json.loads(
            (Path(__file__).parents[1] / "metadata" / "sources.json").read_text(
                encoding="utf-8"
            )
        )
        with self.assertRaises(RegistryContractError) as caught:
            self.evaluate(registry=real)
        message = str(caught.exception)
        self.assertIn("fred_macro_latest_vintage", message)
        self.assertIn("RRPONTSYD", message)
        self.assertIn("available_at", message)
        self.assertEqual(read_journal(self.journal), ())

        # The same source, the same registry, one field fewer: it prices. This
        # is the rolling path's acceptance criterion asserted on the event
        # path, and it is here rather than in a file of its own because the two
        # derivations are now one function and a divergence would show as this
        # assertion failing while the rolling one passes.
        report = self.evaluate(features=("spread_bps",), registry=real)
        self.assertEqual(
            report.field_sources,
            (
                ("fred_macro_latest_vintage", "IORB"),
                ("nyfed_sofr", "SOFR"),
            ),
        )
        self.assertGreater(report.purge_days, 0)

    @staticmethod
    def _priced(days):
        return {
            "release_lag": {
                "basis": "record_date",
                "unit": "calendar_days",
                "days": days,
                "available_time": "00:00",
                "timezone": "America/New_York",
            }
        }


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
            PANEL_ROWS,
            flat_predictor(),
            window,
            features=FEATURES,
            registry=declared_registry(3, FEATURES),
            decision_time=DECISION_TIME,
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
                PANEL_ROWS,
                flat_predictor(),
                features=FEATURES,
                registry=declared_registry(3, FEATURES),
                decision_time=DECISION_TIME,
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
    """The panel is one sequence of rows, and its target is read off them.

    `evaluate_event_window` used to take `dates` and a parallel `y`, and one of
    the faults it checked for was the two disagreeing about their length. A
    panel of rows cannot disagree with itself, so that check is gone rather than
    relaxed: the fault is unrepresentable, which is a better answer than a
    guard. What replaces it is the fault a row can still have -- a spread that
    cannot be read, because `spread_bps` is computed from `sofr` and `iorb`.
    """

    def test_unsorted_dates_are_rejected(self):
        rows = list(PANEL_ROWS)
        rows[4], rows[5] = rows[5], rows[4]
        with self.assertRaisesRegex(SplitError, "strictly ascending"):
            self.evaluate(observations=rows)

    def test_an_empty_panel_is_rejected(self):
        with self.assertRaisesRegex(SplitError, "empty panel"):
            self.evaluate(observations=[])

    def test_a_row_with_no_readable_spread_is_rejected(self):
        """Unobserved, unreadable, and absent. All three, and all by date.

        `"4.30"` is deliberately *not* here: `DailyObservation.spread_bps` calls
        `float()`, which accepts a numeric string, so a spread arriving as text
        is not a fault this layer sees and asserting that it were would be this
        file describing a rule Track A does not have.
        """

        broken_rows = [
            panel_row(3, PANEL_DATES[3], sofr=None),
            panel_row(3, PANEL_DATES[3], iorb=None),
            panel_row(3, PANEL_DATES[3], sofr="not-a-number"),
            DailyObservation(PANEL_DATES[3], {COVARIATE: _covariate(3)}),
        ]
        for broken in broken_rows:
            with self.subTest(values=sorted(broken.values)):
                rows = list(PANEL_ROWS)
                rows[3] = broken
                with self.assertRaisesRegex(SplitError, "no readable spread"):
                    self.evaluate(observations=rows)

    def test_a_row_whose_spread_is_not_finite_is_rejected(self):
        rows = list(PANEL_ROWS)
        rows[3] = panel_row(3, PANEL_DATES[3], sofr=float("nan"))
        with self.assertRaisesRegex(SplitError, "non-finite spread"):
            self.evaluate(observations=rows)

    def test_the_evaluator_takes_no_parallel_target_sequence(self):
        """The mismatched-length fault, retired as unrepresentable.

        Stated rather than dropped silently: if a `y` argument ever comes back,
        so does the fault, and this is where that gets argued with.
        """

        parameters = inspect.signature(evaluate_event_window).parameters
        for gone in ("y", "dates", "values"):
            self.assertNotIn(gone, parameters)


if __name__ == "__main__":
    unittest.main()
