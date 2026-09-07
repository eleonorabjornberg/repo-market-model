"""Contract tests from AGENT_CONTRACT.md.

Owned by neither track. Both tracks run this before every commit; it fails the
build rather than warning.

The contract describes a long point-in-time panel (`series_id`, `ref_date`,
`available_at`, `vintage_id`, `source_sha`) and a `fit`/`predict` forecast
interface. `repo_model.data` now implements the canonical long-form loader, but
the legacy baseline still consumes a wide daily frame keyed on `date`, and
`repo_model.baseline` exposes a streaming backtest instead of a fitted object.
Tests 1-3 and 5 for that legacy path therefore use the strongest available
stand-ins:

  * `available_at` is taken to equal `date` (zero release lag) only in the
    legacy wide-path tests. Separate conformance tests exercise the real
    point-in-time fields and cutoff behavior.
  * "refit and re-predict" is the backtest re-run over a perturbed panel.
  * the only learned transform in the codebase today is the residual quantile
    that sets the prediction interval, so that is what test 3 isolates.
  * structural-zero semantics have not yet been reviewed source by source, so
    test 5 remains a stand-in for those sources: it checks only the half the
    loader is capable of, that missing is never coerced to 0.0 and a real 0.0
    survives as one.

Contract test 4 (identity preservation) cannot reconcile panel snapshots until
the point-in-time panel lands. The registry half is enforceable now: every
source must make explicit identity and structural-zero declarations, and every
declared accounting identity must name its terms and tolerance.

`AGENT_CONTRACT.md`, "Two holdout roles", names two and keeps them distinct.
`rolling_origin` produces the **scoring holdout**; `repo_model.event_eval`
produces the **knowledge holdout**, on a separate path, because the splitter's
training window expands and a late fold would train on an earlier stress episode
before scoring a later one. Their tests are in `tests/test_splits.py` and
`tests/test_event_eval.py`; what is here is the one declaration neither can
make -- the windows themselves, which belong in `metadata/events.json`. The
fixture-level spec Track A codes that file against is
`tests/test_events_metadata.py`.

The two label tests in `TargetSchemaTests` are likewise specs rather than tests
of existing code. The stress label column and its point-in-time rule are Track
A's, per `AGENT_CONTRACT.md` "Ownership" and `CLAUDE.md`; a `trailing_percentile`
in `repo_model.event_eval` briefly implemented the trailing rule and was deleted
as a second implementation of a Track A rule, with its behaviour preserved here
as a requirement on Track A rather than as model-eval code.

`SplitterPurgeTests` is not a stand-in. `repo_model.splits.rolling_origin`
exists, so the splitter half of the contract is tested against the real thing:
the purge gap, the no-look-ahead invariant, and fold ordering. It replaces the
`expectedFailure` placeholder that used to sit in `TargetSchemaTests`, which
went to unexpected-success -- a red build -- the moment the module landed. That
is the mechanism working, not a bug. The gap is still passed in by hand,
because the registry declares no `release_lag` for the splitter to read.

`TargetSchemaTests` at the bottom holds the tests the contract actually asks
for, written against the target interfaces and marked `expectedFailure`. They
are executable specification, not decoration: `unittest` reports an unexpected
success as a build failure, so the day a track implements one of these
interfaces the suite goes red and forces the stand-ins above to be rewritten
against the real thing rather than extended around it.

Mutation record. Two leaks were planted in `rolling_persistence_backtest` and
the suite run against each, on the sample panel, stdlib only:

  * Full-sample quantile: the interval fitted on residuals from the whole
    panel instead of the expanding window. Fails five tests -- the truncation
    test, both `FuturePerturbationTests` behavioural tests, and both
    `TransformIsolationTests`. The perturbation-visibility guard stays green,
    which is correct; it is not a leakage test.
  * Residual ordering: `residuals.append` moved above the interval
    computation, so a forecast's own realized residual enters its own
    quantile. Fails the sweep, the T+1 test, and the transform test.

One further leak was planted in `repo_model.splits`, against the splitter
tests:

  * Permissive gap boundary: `bisect_left` to `bisect_right` in `_train_end`,
    which keeps a training row whose value first becomes observable exactly as
    the test block opens -- a one-day off-by-one, and the smallest leak the
    module can have. Fails 15 tests: 10 assertion failures and 5 errors.

    The split between the two is the point of separating `_folds_unchecked`
    from the guard. The content tests run on the unchecked generator, so they
    report the defect as data -- the reference-oracle comparison prints the
    survivor set that changed, `((..., 10, 11), (13,))` against the correct
    `((..., 10), (13,))`, one row too many on the training side. The 5 errors
    are the three contract purge tests and the two `rolling_origin` cases,
    which run the guarded public path and so raise `LookAheadError` before any
    assertion is reached ("training ends 2026-01-21 and testing opens
    2026-01-23, which is inside the 2-day purge gap"). Failures say what is
    wrong; the errors say the shipped path refuses to emit it.

    `FoldShapeTests` stays green throughout, correctly: a gap one day too small
    changes no block boundary, only which rows survive behind it.

    Run again under `python3 -O`, the same mutation gives byte-identical
    output -- 10 failures, 5 errors. That is what the raise buys. Rebuilding
    the gap check in `_assert_no_look_ahead` as `assert cond, msg` and running
    the same mutation under `-O`, the splitter emits five folds with no error
    at all, the smallest gap two days against a two-day purge: a leaky fold
    handed to the caller silently. Under `-O` the assert form is not a weaker
    guard, it is no guard. The content tests still catch this particular
    mutation either way, which is exactly why the comparison was run on the
    guard directly rather than through the suite.

A fourth, on the strict purge boundary shared by the splitter and the event
evaluator, is recorded in `tests/test_event_eval.py` beside the tests that
catch it, along with two on the window-pinning guards.

Mutation record, the label spec. An `expectedFailure` is only worth having if
it discriminates, so `test_the_stress_label_is_point_in_time_and_never_full_
sample` was run against four stand-in implementations of
`repo_model.data.stress_label_threshold`, injected at runtime rather than
written to Track A's module:

  * Correct trailing rule, plus declared threshold metadata: both label tests
    go to unexpected success -- a red build, which is the intended handoff
    signal and not a defect.
  * Full-sample percentile, the rule the contract prohibits by name: stays an
    expected failure. Caught by assertion 2.
  * Off-by-one including the current row -- the subtle version, where the
    label on the first day of a knowledge-holdout window is informed by that
    day: stays an expected failure. Caught by assertion 1. This is the one
    worth having, because it is the mistake an implementation makes by
    accident rather than by choice.
  * Correct rule but no threshold metadata: the label test succeeds
    unexpectedly while the tau-declaration test stays failing, so the two
    tests are independent rather than one test in two pieces.

The spec therefore accepts exactly the implementations the contract describes
and rejects both leak shapes. It says nothing about whether fixed-bp labels are
computed correctly, only that a trailing threshold does not reach forward; the
primary fixed-bp rule has no leak of this class to have.

Neither of the first two runs is a claim about the whole contract -- both leaks
live in the interval, the only learned parameter here. A leak in a future point
forecast or in the loader is not covered by any of the three.
"""

import inspect
import json
import re
import sys
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from repo_model.baseline import _quantile, rolling_persistence_backtest
from repo_model.contract import validate_release_lag
from repo_model.data import (
    DailyObservation,
    DataContractError,
    audit_panel,
    load_daily_panel,
    load_point_in_time_panel,
    load_stress_thresholds,
    stress_label_threshold,
)
from repo_model.event_eval import load_event_windows
from repo_model.splits import rolling_origin


REPO_ROOT = Path(__file__).parents[1]
SAMPLE_PANEL = REPO_ROOT / "data" / "sample" / "daily_market.csv"
SOURCE_REGISTRY = REPO_ROOT / "metadata" / "sources.json"

MINIMUM_HISTORY = 10
INTERVAL_PROBABILITY = 0.90


def load_sample():
    rows = load_daily_panel(SAMPLE_PANEL)
    audit_panel(rows)  # sortedness and uniqueness are preconditions for the as-of rule
    return rows


def perturb_after(rows, cutoff_index, shock_bps=250.0):
    """Return a copy of the panel with every row after `cutoff_index` moved.

    Only fields dated strictly after the cutoff change, so any forecast made at
    or before the cutoff must be unaffected by this.
    """

    perturbed = []
    for index, row in enumerate(rows):
        values = dict(row.values)
        if index > cutoff_index:
            values["sofr"] = float(values["sofr"]) + shock_bps / 100.0
            for field in ("sofr_volume", "reserve_balances", "on_rrp", "tga"):
                if values.get(field) is not None:
                    values[field] = float(values[field]) * 3.0 + 1.0
        perturbed.append(DailyObservation(row.date, values))
    return perturbed


def residual_window(rows, forecast_index):
    """One-step residuals a forecast for `forecast_index` is entitled to see.

    Everything strictly before the forecast date, and nothing else.
    """

    return [
        rows[j].spread_bps - rows[j - 1].spread_bps
        for j in range(1, forecast_index)
    ]


class EligibilityTests(unittest.TestCase):
    """Contract test 1: no training row is dated after its window's cutoff."""

    def test_as_of_filter_reduces_to_a_prefix_only_if_dates_are_clean(self):
        """The precondition test 1 rests on.

        `available_at <= C` selects a contiguous prefix of the panel only
        because dates are strictly ascending and unique. Asserting the prefix
        property on an already-sorted panel would restate how Python slices;
        asserting that `audit_panel` rejects the two orderings that would break
        it is the part that can actually regress.
        """

        values = {"sofr": 4.31, "iorb": 4.30}
        out_of_order = [
            DailyObservation(date(2026, 1, 5), values),
            DailyObservation(date(2026, 1, 2), values),
        ]
        with self.assertRaisesRegex(DataContractError, "sorted"):
            audit_panel(out_of_order)

        duplicated = [
            DailyObservation(date(2026, 1, 2), values),
            DailyObservation(date(2026, 1, 2), values),
        ]
        with self.assertRaisesRegex(DataContractError, "duplicate"):
            audit_panel(duplicated)

    def test_truncating_at_the_cutoff_does_not_change_earlier_forecasts(self):
        """Behavioural half: a window that peeked ahead would move here.

        Forecasts produced from the panel truncated at C must be bit-identical
        to the corresponding forecasts from the full panel. If any training
        window reached past its cutoff, removing the later rows would change
        them.
        """

        rows = load_sample()
        full = rolling_persistence_backtest(
            rows,
            minimum_history=MINIMUM_HISTORY,
            interval_probability=INTERVAL_PROBABILITY,
        )

        for cutoff_position in range(MINIMUM_HISTORY, len(rows)):
            truncated = rolling_persistence_backtest(
                rows[: cutoff_position + 1],
                minimum_history=MINIMUM_HISTORY,
                interval_probability=INTERVAL_PROBABILITY,
            )
            expected = full.forecasts[: len(truncated.forecasts)]
            self.assertEqual(
                list(truncated.forecasts),
                list(expected),
                msg=(
                    f"forecasts changed when the panel was truncated at "
                    f"{rows[cutoff_position].date}"
                ),
            )


class FuturePerturbationTests(unittest.TestCase):
    """Contract test 2: perturbing the future must not move a past forecast."""

    def test_forecast_for_t_plus_one_is_bit_identical_after_future_shock(self):
        rows = load_sample()
        cutoff_index = 15
        forecast_index = cutoff_index + 1
        position = forecast_index - MINIMUM_HISTORY

        baseline = rolling_persistence_backtest(
            rows,
            minimum_history=MINIMUM_HISTORY,
            interval_probability=INTERVAL_PROBABILITY,
        ).forecasts[position]
        shocked = rolling_persistence_backtest(
            perturb_after(rows, cutoff_index),
            minimum_history=MINIMUM_HISTORY,
            interval_probability=INTERVAL_PROBABILITY,
        ).forecasts[position]

        # `actual_bps` is the realized outcome at T+1 and is *expected* to move
        # with the shock. The forecast itself -- point and interval -- must not.
        self.assertEqual(shocked.predicted_bps, baseline.predicted_bps)
        self.assertEqual(shocked.lower_bps, baseline.lower_bps)
        self.assertEqual(shocked.upper_bps, baseline.upper_bps)

    def test_every_forecast_at_or_before_the_cutoff_is_bit_identical(self):
        rows = load_sample()
        baseline = rolling_persistence_backtest(
            rows,
            minimum_history=MINIMUM_HISTORY,
            interval_probability=INTERVAL_PROBABILITY,
        ).forecasts
        for cutoff_index in range(MINIMUM_HISTORY, len(rows) - 1):
            shocked = rolling_persistence_backtest(
                perturb_after(rows, cutoff_index),
                minimum_history=MINIMUM_HISTORY,
                interval_probability=INTERVAL_PROBABILITY,
            ).forecasts

            # A forecast at panel index i uses rows[0..i-1]: rows[i-1] for the
            # point, rows[0..i-1] for the residual quantile. Only `actual_bps`
            # touches rows[i]. So every forecast through index cutoff_index + 1
            # -- including the T+1 forecast the contract names -- must hold.
            #
            # The `+ 2` is load-bearing. Under the residual-ordering leak in
            # the module docstring, this sweep fails at `+ 2` (cutoff
            # 2026-01-16, forecast 1: upper 128.0 against 4.0) and passes at
            # `+ 1`, because `+ 1` stops one slot short of the T+1 forecast --
            # exactly the slot the contract names. The leak is caught by two
            # other tests either way, so `+ 2` is not the suite's only line of
            # defence; it is what makes this test carry its own weight.
            unaffected = cutoff_index - MINIMUM_HISTORY + 2
            for position in range(unaffected):
                self.assertEqual(
                    (
                        shocked[position].predicted_bps,
                        shocked[position].lower_bps,
                        shocked[position].upper_bps,
                    ),
                    (
                        baseline[position].predicted_bps,
                        baseline[position].lower_bps,
                        baseline[position].upper_bps,
                    ),
                    msg=(
                        f"forecast {position} moved when observations after "
                        f"{rows[cutoff_index].date} were perturbed"
                    ),
                )

    def test_the_perturbation_is_actually_visible_to_the_model(self):
        """Guards the two tests above from passing because nothing changed."""

        rows = load_sample()
        cutoff_index = 15
        shocked = rolling_persistence_backtest(
            perturb_after(rows, cutoff_index),
            minimum_history=MINIMUM_HISTORY,
            interval_probability=INTERVAL_PROBABILITY,
        )
        baseline = rolling_persistence_backtest(
            rows,
            minimum_history=MINIMUM_HISTORY,
            interval_probability=INTERVAL_PROBABILITY,
        )
        self.assertNotEqual(
            [item.predicted_bps for item in shocked.forecasts],
            [item.predicted_bps for item in baseline.forecasts],
            msg="future shock changed no forecast at all; the test has no power",
        )


class TransformIsolationTests(unittest.TestCase):
    """Contract test 3: learned parameters come from the training window alone.

    The residual quantile that sets the prediction interval is the only
    transform with learned parameters in the codebase today.
    """

    def test_interval_matches_parameters_refit_on_the_training_window(self):
        rows = load_sample()
        alpha = (1.0 - INTERVAL_PROBABILITY) / 2.0
        report = rolling_persistence_backtest(
            rows,
            minimum_history=MINIMUM_HISTORY,
            interval_probability=INTERVAL_PROBABILITY,
        )

        for position, forecast in enumerate(report.forecasts):
            forecast_index = MINIMUM_HISTORY + position
            window = residual_window(rows, forecast_index)
            prediction = rows[forecast_index - 1].spread_bps

            self.assertEqual(forecast.predicted_bps, prediction)
            self.assertEqual(forecast.lower_bps, prediction + _quantile(window, alpha))
            self.assertEqual(
                forecast.upper_bps, prediction + _quantile(window, 1.0 - alpha)
            )

    def test_window_parameters_differ_from_full_sample_parameters(self):
        """Guards the test above: on a panel where a leak would be visible.

        The real sample is smooth enough that window-fitted and full-sample
        parameters nearly coincide, so equality alone would prove little. Shock
        the tail, and a pipeline that fit its quantile on the whole panel would
        produce a different interval for an early forecast than one that fit on
        the window. Confirm those two candidate parameters really do differ,
        then confirm the pipeline reports the window-fitted one.
        """

        rows = perturb_after(load_sample(), cutoff_index=15)
        alpha = (1.0 - INTERVAL_PROBABILITY) / 2.0
        forecast_index = MINIMUM_HISTORY + 2
        position = forecast_index - MINIMUM_HISTORY

        window = residual_window(rows, forecast_index)
        full_sample = residual_window(rows, len(rows))

        self.assertNotEqual(
            _quantile(window, 1.0 - alpha),
            _quantile(full_sample, 1.0 - alpha),
            msg="test panel cannot distinguish window fitting from full-sample fitting",
        )

        forecast = rolling_persistence_backtest(
            rows,
            minimum_history=MINIMUM_HISTORY,
            interval_probability=INTERVAL_PROBABILITY,
        ).forecasts[position]
        prediction = rows[forecast_index - 1].spread_bps
        self.assertEqual(
            forecast.upper_bps, prediction + _quantile(window, 1.0 - alpha)
        )


class StructuralZeroTests(unittest.TestCase):
    """Contract test 5: a structural zero is never confused with a missing value.

    The registry's current sources have not completed a structural-zero review,
    so this remains a stand-in for each of them. What the current loader can be
    held to is the coercion rule: an absent observation stays absent, and a
    genuine 0.0 stays 0.0, at load and through the audit.
    """

    def write_csv(self, contents):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "panel.csv"
        path.write_text(contents, encoding="utf-8")
        return path

    def test_missing_and_zero_are_distinguishable_at_load(self):
        path = self.write_csv(
            "date,sofr,iorb,on_rrp,quarter_end\n"
            "2026-01-02,4.31,4.30,,0\n"
            "2026-01-05,4.31,4.30,0,1\n"
        )
        rows = load_daily_panel(path)

        # An empty cell is an unobserved value, not a zero balance.
        self.assertIsNone(rows[0].values["on_rrp"])
        # A reported zero balance is an observation and keeps its value.
        self.assertEqual(rows[1].values["on_rrp"], 0.0)
        self.assertIsNotNone(rows[1].values["on_rrp"])

        # The same distinction on a declared zero/one flag: 0 means "not a
        # quarter end", which is data, not absence.
        self.assertEqual(rows[0].values["quarter_end"], 0.0)
        self.assertEqual(rows[1].values["quarter_end"], 1.0)

    def test_audit_counts_missing_without_counting_zero(self):
        path = self.write_csv(
            "date,sofr,iorb,on_rrp,quarter_end\n"
            "2026-01-02,4.31,4.30,,0\n"
            "2026-01-05,4.31,4.30,0,0\n"
        )
        report = audit_panel(load_daily_panel(path))

        self.assertEqual(report.missing_counts["on_rrp"], 1)
        self.assertEqual(report.missing_counts["quarter_end"], 0)
        # A structural zero is not an anomaly and must not be reported as one.
        self.assertEqual(list(report.warnings), [])

    def test_sample_panel_keeps_unobserved_columns_unobserved(self):
        rows = load_sample()
        for field in ("treasury_settlement", "dealer_treasury_position", "mmf_assets"):
            observed = [row.values[field] for row in rows]
            self.assertTrue(
                all(value is None for value in observed),
                msg=f"{field} is empty in the sample and must not become 0.0",
            )
            self.assertNotIn(0.0, observed)

    def test_zero_survives_the_spread_calculation(self):
        """A zero-valued field must not be silently dropped downstream."""

        path = self.write_csv(
            "date,sofr,iorb,on_rrp\n"
            "2026-01-02,4.30,4.30,0\n"
        )
        rows = load_daily_panel(path)
        self.assertEqual(rows[0].spread_bps, 0.0)
        self.assertEqual(rows[0].values["on_rrp"], 0.0)


class SplitterPurgeTests(unittest.TestCase):
    """The contract's splitter interface: rolling origin, with a purge gap.

    Replaces the `expectedFailure` placeholder that used to sit in
    `TargetSchemaTests`. That placeholder tripped the moment `repo_model.splits`
    existed, which is what it was for; this is the real test it demanded.

    `purge` is a number of calendar days, because a release lag is a duration
    and the panel is business-daily -- the last row before a weekend is three
    days from the next row, the last row inside a week is one. The gap the
    splitter must clear is therefore the same in both places even though the row
    distance is not.

    The lag below is a stand-in. The registry declares no `release_lag` yet (see
    `TargetSchemaTests.test_source_registry_declares_identities_and_structural_zeros`,
    still expected to fail), so the splitter takes the gap as a required
    argument and the number here is the value this test reasons about, not a
    value read from anywhere. When the registry gains the key, this constant is
    replaced by the largest declared lag over the fields in use, and the
    splitter's caller stops passing a literal.
    """

    #: Stand-in for the longest release lag over the fields in the panel.
    LONGEST_RELEASE_LAG_DAYS = 2

    MIN_TRAIN = 10
    STEP = 3

    def setUp(self):
        self.dates = [row.date for row in load_sample()]

    def folds(self, purge):
        return list(rolling_origin(self.dates, self.MIN_TRAIN, self.STEP, purge))

    def test_the_gap_closes_a_leak_that_a_zero_gap_leaves_open(self):
        """The contract property, and the test's own power in one place.

        A value dated on the last training day is not observable until
        `release_lag` days later. If the test block opens within that window,
        the training window contains a row whose value the forecaster could not
        have had -- and worse, whose eventual revision is informed by the test
        period. With no gap the sample panel is in exactly that position on
        every fold. With the gap set to the lag, on none of them.
        """

        leaky = [
            (self.dates[train[-1]], self.dates[test[0]])
            for train, test in self.folds(purge=0)
        ]
        self.assertTrue(leaky, msg="no folds; the comparison below is vacuous")
        self.assertTrue(
            any(
                (opens - ends).days <= self.LONGEST_RELEASE_LAG_DAYS
                for ends, opens in leaky
            ),
            msg=(
                "a zero gap leaked nothing on this panel, so passing the purged "
                "case proves nothing about the purge"
            ),
        )

        for ends, opens in [
            (self.dates[train[-1]], self.dates[test[0]])
            for train, test in self.folds(purge=self.LONGEST_RELEASE_LAG_DAYS)
        ]:
            self.assertGreater(
                (opens - ends).days,
                self.LONGEST_RELEASE_LAG_DAYS,
                msg=(
                    f"training ends {ends} and testing opens {opens}, within the "
                    f"{self.LONGEST_RELEASE_LAG_DAYS}-day release lag"
                ),
            )

    def test_no_fold_trains_on_a_row_inside_its_gap(self):
        """max(train) + purge < min(test), for every fold, at every gap."""

        for purge in (0, 1, 2, 4):
            folds = self.folds(purge)
            self.assertTrue(folds, msg=f"purge={purge} produced no folds")
            for train, test in folds:
                self.assertLess(
                    self.dates[train[-1]] + timedelta(days=purge),
                    self.dates[test[0]],
                    msg=f"purge={purge}: fold trains inside its own gap",
                )
                self.assertLess(train[-1], test[0])

    def test_folds_are_in_time_order_and_test_blocks_do_not_overlap(self):
        """Rolling origin, not cross-validation: each day is scored once."""

        for purge in (0, 2):
            scored = []
            previous_open = None
            for _, test in self.folds(purge):
                opens = self.dates[test[0]]
                if previous_open is not None:
                    self.assertGreater(opens, previous_open, msg="folds are out of order")
                previous_open = opens
                scored.extend(test)
            self.assertEqual(scored, sorted(scored))
            self.assertEqual(
                len(scored), len(set(scored)), msg="an observation is scored twice"
            )

    def test_the_gap_has_no_default(self):
        """A silent default is the failure the whole splitter exists to prevent.

        Until the registry declares `release_lag`, there is no number the
        splitter could default to that is not a guess, and a guessed gap
        produces a backtest that looks fine and is not.
        """

        self.assertIs(
            inspect.signature(rolling_origin).parameters["purge"].default,
            inspect.Parameter.empty,
        )
        with self.assertRaises(TypeError):
            rolling_origin(self.dates, self.MIN_TRAIN, self.STEP)


class SourceRegistryTests(unittest.TestCase):
    """Conformance tests for the machine-readable source registry."""

    def test_source_registry_declares_identities_and_structural_zeros(self):
        """Contract tests 4 and 5 require explicit, machine-readable metadata."""

        registry = json.loads(SOURCE_REGISTRY.read_text(encoding="utf-8"))
        self.assertIsInstance(registry, dict)
        self.assertTrue(registry)

        declared_identities = 0
        for source_id, source in registry.items():
            with self.subTest(source_id=source_id):
                self.assertIsInstance(source.get("identities"), list)
                self.assertIsInstance(source.get("structural_zeros"), list)
                self.assertIsInstance(source.get("structural_zeros_reviewed"), bool)
                self.assertIsInstance(source.get("reviewed_note"), str)
                self.assertTrue(source["reviewed_note"])
                if not source["structural_zeros_reviewed"]:
                    self.assertEqual(
                        source["structural_zeros"],
                        [],
                        msg=(
                            f"{source_id}: unreviewed structural-zero declarations "
                            "must not be recorded as findings"
                        ),
                    )

                # The shape of `release_lag` is the seam both tracks build
                # against, so it is checked by the shared, human-owned module
                # rather than restated here. A second copy of these rules is
                # exactly how one field came to be called `calendar` on one
                # side and `unit` on the other; see AGENT_CONTRACT.md,
                # "Decided: the `release_lag` schema".
                problems = validate_release_lag(source_id, source.get("release_lag"))
                self.assertEqual(problems, [], msg="; ".join(problems))

                self.assertIsInstance(source.get("coverage"), list)
                self.assertTrue(source["coverage"])
                self.assertTrue(all(isinstance(item, str) for item in source["coverage"]))

                machine_fields = source.get("fields")
                self.assertIsInstance(machine_fields, list)
                self.assertTrue(machine_fields)
                for field in machine_fields:
                    self.assertIsInstance(field, str)
                    self.assertRegex(field, re.compile(r"^[A-Za-z][A-Za-z0-9_]*$"))
                fields = set(machine_fields)
                for identity in source["identities"]:
                    declared_identities += 1
                    self.assertIsInstance(identity.get("name"), str)
                    self.assertTrue(identity["name"])
                    for side in ("left", "right"):
                        self.assertIsInstance(identity.get(side), list)
                        self.assertTrue(identity[side])
                        self.assertTrue(set(identity[side]).issubset(fields))
                    tolerance = identity.get("tolerance")
                    self.assertIsInstance(tolerance, dict)
                    self.assertIsInstance(tolerance.get("absolute"), (int, float))
                    self.assertGreaterEqual(tolerance["absolute"], 0)
                    self.assertIsInstance(tolerance.get("unit"), str)
                    self.assertTrue(tolerance["unit"])

                for declaration in source["structural_zeros"]:
                    self.assertIsInstance(declaration, dict)
                    self.assertIn(declaration.get("field"), fields)
                    self.assertIsInstance(declaration.get("when"), str)
                    self.assertTrue(declaration["when"])

        self.assertGreater(
            declared_identities,
            0,
            msg="registry must declare at least one testable accounting identity",
        )


class PointInTimePanelTests(unittest.TestCase):
    """Conformance tests for the canonical long-form point-in-time panel."""

    SHA = "b" * 64

    def write_panel(self, rows):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "panel.csv"
        path.write_text(
            "series_id,ref_date,available_at,value,vintage_id,source_sha\n"
            + "".join(rows),
            encoding="utf-8",
        )
        return path

    def test_panel_rows_carry_point_in_time_provenance(self):
        path = self.write_panel(
            [f"IORB,2026-01-02,2026-01-02T12:00:00Z,4.30,v1,{self.SHA}\n"]
        )
        row = load_point_in_time_panel(path)[0]

        self.assertEqual(row.series_id, "IORB")
        self.assertEqual(row.ref_date, date(2026, 1, 2))
        self.assertEqual(
            row.available_at,
            datetime(2026, 1, 2, 12, tzinfo=timezone.utc),
        )
        self.assertEqual(row.value, 4.30)
        self.assertEqual(row.vintage_id, "v1")
        self.assertEqual(row.source_sha, self.SHA)

    def test_revisions_are_appended_as_new_vintages(self):
        path = self.write_panel(
            [
                f"IORB,2026-01-02,2026-01-02T12:00:00Z,4.30,v1,{self.SHA}\n",
                f"IORB,2026-01-02,2026-01-05T12:00:00Z,4.31,v2,{self.SHA}\n",
            ]
        )

        rows = load_point_in_time_panel(path)

        self.assertEqual(len(rows), 2)
        self.assertEqual([row.vintage_id for row in rows], ["v1", "v2"])
        self.assertEqual([row.value for row in rows], [4.30, 4.31])
        early = load_point_in_time_panel(
            path,
            cutoff=datetime(2026, 1, 3, tzinfo=timezone.utc),
        )
        self.assertEqual([row.vintage_id for row in early], ["v1"])


class StressLabelContractTests(unittest.TestCase):
    """The fixed primary target and leak-free trailing secondary threshold."""

    def test_the_stress_label_is_point_in_time_and_never_full_sample(self):
        window, probability = 10, 0.9
        values = [4.30 + 0.01 * (index % 5) for index in range(40)]
        event_index = 25
        shocked = [
            value + 50.0 if position >= event_index else value
            for position, value in enumerate(values)
        ]

        self.assertEqual(
            stress_label_threshold(shocked, event_index, window, probability),
            stress_label_threshold(values, event_index, window, probability),
            msg="the trailing threshold reached into the event boundary",
        )
        self.assertNotEqual(
            stress_label_threshold(shocked, event_index, window, probability),
            stress_label_threshold(shocked, len(shocked), len(shocked), probability),
            msg="the trailing threshold is a prohibited full-sample percentile",
        )
        later = event_index + window
        self.assertNotEqual(
            stress_label_threshold(shocked, later, window, probability),
            stress_label_threshold(values, later, window, probability),
            msg="the future shock is not visible when it enters the trailing window",
        )

    def test_fixed_bp_thresholds_are_the_primary_label_and_are_declared(self):
        declared = load_stress_thresholds()

        self.assertIn("version", declared)
        self.assertEqual(tuple(declared["taus_bp"]), (5.0, 10.0, 20.0, 50.0))
        self.assertEqual(declared["primary_rule"], "fixed_bp")
        self.assertEqual(
            declared["secondary_rule"]["history"],
            "rows_strictly_before_label_row",
        )
        self.assertIs(declared["secondary_rule"]["full_sample_allowed"], False)


class TargetSchemaTests(unittest.TestCase):
    """The contract's expected-to-fail model requirements for absent interfaces.

    Every unimplemented interface here is expected to fail. When one starts
    passing, `unittest` reports an unexpected success and the build goes red --
    which is the signal to replace its tripwire with a real assertion.

    The two `hasattr` tests below are presence tripwires, not conformance
    checks: they fire on a name existing and say nothing about whether it
    behaves as the contract requires. Read a red build from either as "an
    interface landed, go write the real test", never as "the interface is
    correct".
    """

    @unittest.expectedFailure
    def test_forecast_interface_is_fit_predict_predict_stress(self):
        """Models must be fitted objects carrying their cutoff, not a function."""

        import repo_model.baseline as baseline

        for name in ("fit", "predict", "predict_stress"):
            self.assertTrue(
                hasattr(baseline, name),
                msg=f"no {name!r}; quantile levels are not yet comparable across models",
            )


if __name__ == "__main__":
    unittest.main()
