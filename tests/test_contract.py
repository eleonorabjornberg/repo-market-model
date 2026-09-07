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

The two label tests in `StressLabelContractTests` are likewise specs rather than tests
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

`ForecastInterfaceTests` at the bottom is what that mechanism produced. It was
`TargetSchemaTests`, a single `expectedFailure` checking `hasattr(baseline,
"fit")` and two siblings; `repo_model.baseline` grew the fitted interface, the
tripwire went to unexpected success -- a red build -- and it was replaced with
the conformance assertions it stood in for. No `expectedFailure` remains in this
file. That is the mechanism finishing, not the mechanism being switched off: the
next absent interface gets a new tripwire, and the rule for reading a red one is
unchanged. "An interface landed, go write the real test", never "the interface
is correct".

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

Mutation record, the forecast interface. Three mutations were planted against
`ForecastInterfaceTests` and `test_baseline.FittedPersistenceTests`, in a copy
of the tree under `$HOME`, run with `-B` and `PYTHONDONTWRITEBYTECODE=1` after
an unmutated control (370 tests, OK) and with `__pycache__` cleared each time:

  * Separately fitted `predict_stress`. Not a broken one -- a well-calibrated
    unconditional classifier on the `stress_gt_*` label columns, returning the
    rate at which the *training spreads* exceeded each tau. It is monotone in
    tau by construction, lands in [0, 1], has one entry per declared tau, and
    saturates correctly outside the training range. Fails exactly one test:
    `test_predict_stress_agrees_with_the_quantiles_predict_reports`. Every
    other assertion in the class stays green, which is the finding rather than
    a gap -- the shape checks cannot see where a number came from, and a
    one-test kill is the evidence that the agreement test is carrying the
    contract's "not a separately fitted classifier" on its own. Had the answer
    been "none", the agreement test would not have been doing its job; had it
    been "all of them", the mutation would have been a broken classifier rather
    than a plausible one, and would have proved nothing.
  * Cutoff dropped from the fitted object. `fit` keeps its eligibility guard,
    so the leak that raises still raises; what is lost is the object's ability
    to say afterwards what it was allowed to see, and `trained_beyond` degrades
    to a constant `False`. Fails two, both by `AttributeError` on `cutoff`:
    `test_a_fitted_model_carries_the_cutoff_it_was_fitted_at` and
    `test_the_backtest_reports_the_fitted_model_and_does_not_re_derive_quantiles`.
    The second is the one worth noting -- the backtest is what makes the cutoff
    load-bearing rather than decorative, because a reported run that cannot
    name its own cutoff cannot be audited at all.
  * `QUANTILE_LEVELS` disturbed in a scratch copy of `contract.py`, in the two
    ways that matter, because they fail differently:

      - Reordered to `(0.95, 0.25, 0.50, 0.75, 0.05)`: 16 errors and 1 failure.
        `metrics._validate_levels` raises `MetricError` from `FittedPersistence.
        __init__`, so every path that fits a model errors out, including the
        backtest and both `FuturePerturbationTests`. The suite does not merely
        notice; it cannot construct a model at all.
      - Truncated to `(0.05, 0.25, 0.50)`: 2 failures, and the interesting
        result. `test_predict_returns_one_quantile_per_declared_level` stays
        green, correctly -- it reads the declaration, and three levels really
        are what was declared. What goes red is
        `test_the_interval_probability_is_read_from_the_declared_levels`, since
        the outermost pair now spans 0.45 rather than 0.90, plus the
        transform-isolation guard whose upper bound became the median. A
        truncation is only visible where a number was reconciled against the
        grid, which is the argument for reconciling the interval against it
        rather than restating it.

The three together cover where the numbers come from, whether the object can be
audited, and whether the declaration is actually read. They say nothing about
whether persistence is a good forecast, which is not a property any of these
tests claims.
"""

import argparse
import ast
import importlib.util
import inspect
import json
import re
import sys
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from repo_model import cli
from repo_model.baseline import (
    INTERVAL_PROBABILITY,
    FittedPersistence,
    _quantile,
    fit,
    predict,
    predict_stress,
    rolling_persistence_backtest,
)
from repo_model.contract import QUANTILE_LEVELS, validate_release_lag
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
from repo_model.splits import LookAheadError, rolling_origin


REPO_ROOT = Path(__file__).parents[1]
SAMPLE_PANEL = REPO_ROOT / "data" / "sample" / "daily_market.csv"
SOURCE_REGISTRY = REPO_ROOT / "metadata" / "sources.json"

MINIMUM_HISTORY = 10

#: The interval bounds, read from the declared grid rather than restated. The
#: two constants below used to be `alpha = (1 - 0.90) / 2` and its complement,
#: and that restatement was never bit-equal to the declaration it stood for:
#: `(1.0 - 0.90) / 2.0` is 0.050000000000000044, not 0.05. The interval it
#: produced therefore differed from the declared one in the last two bits --
#: harmless here, and exactly the kind of quiet divergence between two copies
#: of one number that having a single declaration is meant to prevent.
LOWER_LEVEL = QUANTILE_LEVELS[0]
UPPER_LEVEL = QUANTILE_LEVELS[-1]


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
            self.assertEqual(
                forecast.lower_bps, prediction + _quantile(window, LOWER_LEVEL)
            )
            self.assertEqual(
                forecast.upper_bps, prediction + _quantile(window, UPPER_LEVEL)
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
        forecast_index = MINIMUM_HISTORY + 2
        position = forecast_index - MINIMUM_HISTORY

        window = residual_window(rows, forecast_index)
        full_sample = residual_window(rows, len(rows))

        self.assertNotEqual(
            _quantile(window, UPPER_LEVEL),
            _quantile(full_sample, UPPER_LEVEL),
            msg="test panel cannot distinguish window fitting from full-sample fitting",
        )

        forecast = rolling_persistence_backtest(
            rows,
            minimum_history=MINIMUM_HISTORY,
            interval_probability=INTERVAL_PROBABILITY,
        ).forecasts[position]
        prediction = rows[forecast_index - 1].spread_bps
        self.assertEqual(
            forecast.upper_bps, prediction + _quantile(window, UPPER_LEVEL)
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
    `SourceRegistryTests.test_source_registry_declares_identities_and_structural_zeros`,
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


def distinct_residual_frame(count=60, seed=20260908):
    """A panel whose one-step residuals are all distinct, and deterministic.

    `data/sample/daily_market.csv` moves in whole basis points, so its residuals
    repeat -- and a repeated residual makes the quantile function flat over a
    range of probabilities, which has no single inverse. The exceedance test
    below asserts an exact round trip through that function, so it needs a
    sample the function is invertible on. The frame is generated rather than
    stored because the property under test is a property of the numbers, not of
    any particular panel, and `test_the_frame_this_class_relies_on_has_no_tied_residuals`
    checks the property holds rather than assuming the generator delivered it.
    """

    rows = []
    state = seed
    for index in range(count):
        state = (1103515245 * state + 12345) % (2 ** 31)
        rows.append(
            DailyObservation(
                date(2026, 1, 1) + timedelta(days=index),
                {"sofr": 4.30 + 0.0001 * (state % 9973), "iorb": 4.30},
            )
        )
    return rows


class ForecastInterfaceTests(unittest.TestCase):
    """AGENT_CONTRACT.md, "The forecast interface", against the real thing.

    This class replaces the `expectedFailure` presence tripwire that stood here
    while `fit`/`predict`/`predict_stress` did not exist. That tripwire tested
    `hasattr` and nothing else; it went to unexpected success -- a red build --
    the moment the interface landed, which is the mechanism working. What
    follows are the conformance assertions it was a placeholder for.

    The load-bearing one is
    `test_predict_stress_agrees_with_the_quantiles_predict_reports`. The
    contract's Target says stress "is not a separately fitted rare-event
    classifier ... it is an exceedance derived from the predictive
    distribution", and that is a claim about where the numbers come from, which
    no shape check can see. A classifier fitted on the `stress_gt_*` columns
    would satisfy every other test in this class -- right length, right order,
    non-increasing, probabilities in [0, 1] -- and could be well calibrated on
    its own terms while still contradicting the quantiles reported beside it.
    The agreement test is the only one that can tell the two apart.
    """

    MINIMUM_HISTORY = 20

    def setUp(self):
        self.rows = distinct_residual_frame()
        self.train = self.rows[:-1]
        self.feature_row = self.rows[-2]
        self.model = fit(self.train, minimum_history=self.MINIMUM_HISTORY)

    def test_the_frame_this_class_relies_on_has_no_tied_residuals(self):
        """Guards the agreement test: its exactness is only claimed on this."""

        residuals = self.model.residuals
        self.assertEqual(
            len(set(residuals)),
            len(residuals),
            msg=(
                "residuals tie, so the quantile function is flat somewhere and "
                "has no single inverse; the agreement test's exact equality is "
                "not a fair demand on this sample"
            ),
        )

    def test_a_fitted_model_carries_the_cutoff_it_was_fitted_at(self):
        """"Every fitted object carries the cutoff it was fitted at."

        Fitting returns an object, not a function, and the object can say what
        it was allowed to see. Without that a forecast cannot be audited for
        leakage at all: the training frame is gone by the time anyone reads the
        prediction, and "which rows went into this" becomes unanswerable.
        """

        self.assertIsInstance(self.model, FittedPersistence)
        self.assertEqual(self.model.cutoff, self.train[-1].date)

        # An explicitly declared cutoff is honoured rather than re-derived, and
        # a frame reaching past it is a leak, not a rounding matter.
        earlier = fit(
            self.train[:-3],
            cutoff=self.train[-4].date,
            minimum_history=self.MINIMUM_HISTORY,
        )
        self.assertEqual(earlier.cutoff, self.train[-4].date)
        with self.assertRaises(LookAheadError):
            fit(
                self.train,
                cutoff=self.train[-4].date,
                minimum_history=self.MINIMUM_HISTORY,
            )

        # And the model can tell whether it was fitted past a feature row, which
        # is the question "at or before its own cutoff" is asked to answer.
        self.assertFalse(self.model.trained_beyond(self.feature_row))
        self.assertTrue(self.model.trained_beyond(self.rows[0]))

    def test_predict_returns_one_quantile_per_declared_level(self):
        """"predict(feature_row) -> quantile vector at declared levels."

        One value per `contract.QUANTILE_LEVELS`, in that order, ascending
        because the levels are. The levels come from the declaration; a model
        wanting others is a new model, not a config change.
        """

        quantiles = self.model.predict(self.feature_row)

        self.assertEqual(len(quantiles), len(QUANTILE_LEVELS))
        self.assertEqual(self.model.levels, QUANTILE_LEVELS)
        for position in range(1, len(quantiles)):
            self.assertLessEqual(
                quantiles[position - 1],
                quantiles[position],
                msg=f"quantile {position} falls below quantile {position - 1}",
            )
        # The module-level name the contract lists is the same computation, not
        # a second one that could drift from the method.
        self.assertEqual(predict(self.model, self.feature_row), quantiles)

    def test_predict_stress_returns_one_probability_per_declared_tau(self):
        """"predict_stress(feature_row) -> exceedance vector aligned to taus_bp."

        The family is read from `metadata/stress_thresholds.json`, where Track A
        declared it, and the vector is aligned to that declared order. A length
        that merely happens to match would not be alignment, so the tau count is
        taken from the file rather than written down here.
        """

        declared = tuple(float(tau) for tau in load_stress_thresholds()["taus_bp"])
        exceedance = self.model.predict_stress(self.feature_row)

        self.assertEqual(len(exceedance), len(declared))
        for position, probability in enumerate(exceedance):
            self.assertGreaterEqual(probability, 0.0, msg=f"tau {declared[position]}")
            self.assertLessEqual(probability, 1.0, msg=f"tau {declared[position]}")
        self.assertEqual(
            predict_stress(self.model, self.feature_row), exceedance
        )

    def test_predict_stress_never_rises_with_tau(self):
        """`P(Y > tau)` cannot increase as `tau` increases.

        The same invariant `event_eval._validate_predictions` enforces on any
        predictor it scores, checked here on the model itself: a violation is a
        broken distribution, and an aggregate over scored days would hide it.
        Checked on a dense grid rather than the four declared taus, because four
        points can be non-increasing while the curve between them is not.
        """

        anchor = self.feature_row.spread_bps
        grid = [anchor - 40.0 + 0.5 * step for step in range(200)]
        curve = self.model.predict_stress(self.feature_row, taus=grid)

        self.assertEqual(len(curve), len(grid))
        for position in range(1, len(curve)):
            self.assertLessEqual(
                curve[position],
                curve[position - 1],
                msg=(
                    f"exceedance rises from tau {grid[position - 1]} to "
                    f"{grid[position]}"
                ),
            )

    def test_predict_stress_agrees_with_the_quantiles_predict_reports(self):
        """Stress is derived from the predictive distribution, not fitted apart.

        At a declared level `q`, `predict` reports the quantile `Q(q)` and
        `predict_stress` must place exactly `1 - q` of its mass above it. The
        two are then demonstrably statements about one distribution.

        This is the assertion that separates a derived exceedance from a
        separately fitted one. A classifier trained on the `stress_gt_*` label
        columns has its own view of `P(Y > tau)`; nothing constrains that view
        to agree with the quantiles, so it fails here even when it is correct on
        its own terms -- which is the point, because a separately fitted stress
        model is prohibited by the contract whether or not it is any good.

        Exactness is claimed only because the residuals here do not tie; see
        `test_the_frame_this_class_relies_on_has_no_tied_residuals`.
        """

        quantiles = self.model.predict(self.feature_row)
        exceedance = self.model.predict_stress(self.feature_row, taus=quantiles)

        self.assertEqual(len(exceedance), len(QUANTILE_LEVELS))
        for level, reported in zip(QUANTILE_LEVELS, exceedance):
            self.assertAlmostEqual(
                reported,
                1.0 - level,
                places=12,
                msg=(
                    f"predict reports the {level} quantile, but predict_stress "
                    f"puts {reported} above it instead of {1.0 - level}; the two "
                    f"are not describing the same distribution"
                ),
            )

    def test_the_exceedance_is_strictly_above_the_threshold(self):
        """`P(spread > tau)`, matching the contract and the `stress_gt_*` columns.

        Above the fitted support nothing exceeds, and the answer is a hard zero
        rather than a smoothed small number -- the same refusal to invent a
        prior that `climatology_exceedance` documents.
        """

        anchor = self.feature_row.spread_bps
        far_above = anchor + max(self.model.residuals) + 1.0
        far_below = anchor + min(self.model.residuals) - 1.0

        self.assertEqual(self.model.predict_stress(self.feature_row, taus=[far_above])[0], 0.0)
        self.assertEqual(self.model.predict_stress(self.feature_row, taus=[far_below])[0], 1.0)

    def test_a_tau_family_that_is_not_ascending_is_refused(self):
        """Monotonicity in tau is only meaningful against an increasing family."""

        anchor = self.feature_row.spread_bps
        with self.assertRaises(ValueError):
            self.model.predict_stress(self.feature_row, taus=[anchor + 1.0, anchor])
        with self.assertRaises(ValueError):
            self.model.predict_stress(self.feature_row, taus=[])


def _subparsers(parser):
    """The `{name: subparser}` map behind an argparse subparsers action."""

    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return dict(action.choices)
    raise AssertionError("parser declares no subcommands")


class CommandLineOwnershipTests(unittest.TestCase):
    """The CLI seam, from AGENT_CONTRACT.md "Decided: who owns the CLI".

    `src/repo_model/cli.py` is a human-owned dispatcher and the two `cli_*.py`
    modules are track-owned. The property that closes the ownership hole is not
    that the file got assigned -- it is that **adding a subcommand never
    requires editing the human-owned file**. A docstring cannot fail a build, so
    that property is asserted here.

    The last test is the tripwire for the next `cli.py`: it fails when any
    module under `src/repo_model/` is not accounted for by the ownership lists.
    Both holes this project found -- `cli.py` and `baseline.py` -- were found by
    a person reading the gate, twice, months apart. This finds the third one on
    the branch that introduces it.
    """

    GATE = REPO_ROOT / ".github" / "check_ownership.py"

    @classmethod
    def _gate(cls):
        spec = importlib.util.spec_from_file_location("_ownership_gate", cls.GATE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_the_dispatcher_registers_no_subcommand_of_its_own(self):
        """`cli.py` must contain no `add_parser` call.

        Parsed, not grepped: the file's own docstring names `add_parser` while
        explaining this rule, and a text scan would fail on the explanation.
        """

        tree = ast.parse(Path(cli.__file__).read_text())
        offenders = [
            node.lineno
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "add_parser"
        ]
        self.assertEqual(
            offenders,
            [],
            "cli.py calls add_parser at lines "
            f"{offenders}. A subcommand registered in the dispatcher is a "
            "subcommand a track cannot add without a human edit, which is the "
            "hole the split closed.",
        )

    def test_every_registered_subcommand_declares_a_handler(self):
        """A subparser without `handler` reaches the user as exit 2, not a crash.

        The dispatcher degrades gracefully, but a missing handler is still a
        registration bug and should fail here rather than in someone's shell.
        """

        for name, subparser in _subparsers(cli.build_parser()).items():
            with self.subTest(command=name):
                self.assertIn(
                    "handler",
                    subparser._defaults,
                    f"subcommand {name!r} did not call set_defaults(handler=...)",
                )

    def test_the_split_preserved_the_three_existing_subcommands(self):
        """`audit`, `backtest` and `fetch` still exist, from the right modules.

        A refactor of a file with no test coverage is exactly where a command
        goes missing quietly.

        Loosened from an exact set to a subset when `event-holdout` was added,
        and the loosening is narrower than it sounds. The property this test was
        written for is that the split lost nothing, which a subset states
        exactly; the equality also froze the command list, so the first block to
        add a command -- the thing the whole seam exists to make easy -- failed a
        test named for preservation. What the equality was additionally buying,
        that no command appears from somewhere unaccounted for, is now asserted
        directly and over every command rather than by counting: see
        `test_every_registered_command_comes_from_a_track_module`. That is
        stronger, because it keeps holding as commands are added.
        """

        expected = {
            "audit": "repo_model.cli_data",
            "fetch": "repo_model.cli_data",
            "backtest": "repo_model.cli_eval",
        }
        registered = _subparsers(cli.build_parser())
        self.assertLessEqual(set(expected), set(registered))
        for name, module in expected.items():
            with self.subTest(command=name):
                self.assertEqual(
                    registered[name]._defaults["handler"].__module__, module
                )

    def test_every_registered_command_comes_from_a_track_module(self):
        """No command arrives from the dispatcher or from anywhere unowned.

        The half of the old equality worth keeping, stated as the property
        instead of as a count. Every subcommand -- the three the split inherited
        and every one added since -- must carry a handler defined in a
        track-owned registration module, so that adding one is always a change
        the ownership gate can see. A command handled from `cli.py` itself, or
        from a module in neither track's list, is the ownership hole reopening
        one subcommand at a time.
        """

        owned = {"repo_model.cli_data", "repo_model.cli_eval"}
        for name, parser in _subparsers(cli.build_parser()).items():
            with self.subTest(command=name):
                handler = parser._defaults.get("handler")
                self.assertIsNotNone(
                    handler, msg=f"{name!r} registered no handler"
                )
                self.assertIn(
                    handler.__module__,
                    owned,
                    msg=f"{name!r} is handled from {handler.__module__}, which is "
                    "not a track-owned registration module",
                )

    def test_the_dispatcher_names_neither_track_module_beyond_importing_it(self):
        """`cli.py` may import the registration modules and nothing more.

        It holds `REGISTRARS`, which is a list of `register` callables. If it
        starts reaching into a track module for anything else, the seam has
        started leaking track vocabulary back into the human-owned file.
        """

        tree = ast.parse(Path(cli.__file__).read_text())
        reached = {
            node.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id in ("cli_data", "cli_eval")
        }
        self.assertEqual(
            reached,
            {"register"},
            f"cli.py reaches into the track modules for {sorted(reached)}; only "
            "'register' is part of the seam.",
        )

    def test_every_source_module_is_owned_by_exactly_one_party(self):
        """No module under `src/repo_model/` belongs to nobody.

        This is the general form of the two holes already paid for. A module is
        owned if it is HUMAN_ONLY, SHARED, or forbidden to exactly one track --
        forbidden to Track B means owned by Track A, and vice versa. A module in
        none of those lists is one the gate is silent about: both tracks may
        edit it and nothing says so until the merge.
        """

        gate = self._gate()
        a_owned = set(gate.TRACKS["feature/model-eval"]["forbidden"])
        b_owned = set(gate.TRACKS["feature/data-layer"]["forbidden"])

        unowned = []
        contested = []
        for module in sorted((REPO_ROOT / "src" / "repo_model").glob("*.py")):
            path = f"src/repo_model/{module.name}"
            claims = [
                label
                for label, patterns in (
                    ("human", gate.HUMAN_ONLY),
                    ("shared", gate.SHARED),
                    ("track A", a_owned),
                    ("track B", b_owned),
                )
                if any(gate.matches(path, pattern) for pattern in patterns)
            ]
            if not claims:
                unowned.append(path)
            elif len(claims) > 1:
                contested.append(f"{path} ({', '.join(claims)})")

        self.assertEqual(
            unowned,
            [],
            f"{unowned} are in no ownership list. The gate will neither block "
            "an edit to them nor surface one for review, so both tracks can "
            "change them and nothing will say so until the merge. Assign each "
            "in .github/check_ownership.py and say so in AGENT_CONTRACT.md.",
        )
        self.assertEqual(
            contested, [], f"{contested} are claimed by more than one party."
        )


if __name__ == "__main__":
    unittest.main()
