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
import textwrap
import tempfile
import unittest
from datetime import date, datetime, time, timedelta, timezone
from functools import partial
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from repo_model import baseline, cli
from repo_model.baseline import (
    INTERVAL_PROBABILITY,
    FittedArx,
    FittedPersistence,
    FittedThreshold,
    _quantile,
    fit,
    fit_arx,
    fit_threshold,
    predict,
    predict_stress,
    rolling_persistence_backtest,
)
from repo_model.contract import (
    CALENDAR_FEATURES,
    DERIVED_FEATURES,
    FEATURE_FIELDS,
    FEATURE_SOURCES,
    QUANTILE_LEVELS,
    REVISION_POLICIES,
    UNSOURCED_FEATURES,
    UndeclaredFeatureError,
    field_sources_for_features,
    resolve_identity_tolerance,
    sources_for_features,
    validate_field_release_lag,
    validate_identity_tolerance,
    validate_registry_identity_tolerances,
    validate_release_lag,
)
from repo_model.data import (
    OPTIONAL_NUMERIC_FIELDS,
    REQUIRED_FIELDS,
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


def residual_window(rows, train_end):
    """One-step residuals a forecast trained through `train_end` may see.

    Everything strictly inside the training frame, and nothing else. Under a
    purge the frame no longer ends the day before the scored day, so the bound
    is the fold's last training index rather than the forecast index -- the same
    "everything the forecaster was allowed to have seen", stated where the gap
    has moved it to.
    """

    return [
        rows[j].spread_bps - rows[j - 1].spread_bps
        for j in range(1, train_end + 1)
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
        full = contract_backtest(
            rows,
            minimum_history=MINIMUM_HISTORY,
            interval_probability=INTERVAL_PROBABILITY,
        )

        # The sweep starts where a purged run first has a fold at all. Under a
        # gap the first origins are spent clearing it, so the shortest prefixes
        # yield nothing and `rolling_origin` refuses them -- correctly, and not
        # a fact about eligibility. `full` is unaffected; only the prefixes that
        # cannot be scored are skipped.
        shortest = MINIMUM_HISTORY + CONTRACT_PURGE + 1
        for cutoff_position in range(shortest, len(rows)):
            truncated = contract_backtest(
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

        baseline = contract_backtest(
            rows,
            minimum_history=MINIMUM_HISTORY,
            interval_probability=INTERVAL_PROBABILITY,
        ).forecasts[position]
        shocked = contract_backtest(
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
        baseline = contract_backtest(
            rows,
            minimum_history=MINIMUM_HISTORY,
            interval_probability=INTERVAL_PROBABILITY,
        ).forecasts
        for cutoff_index in range(MINIMUM_HISTORY, len(rows) - 1):
            shocked = contract_backtest(
                perturb_after(rows, cutoff_index),
                minimum_history=MINIMUM_HISTORY,
                interval_probability=INTERVAL_PROBABILITY,
            ).forecasts

            # A forecast whose fold reads no row after `cutoff_index` must be
            # bit-identical. Under a gap the fold is no longer `rows[0..i-1]`
            # with feature row `rows[i-1]`, so the bound is taken from the folds
            # themselves rather than from `cutoff_index - MINIMUM_HISTORY`.
            #
            # This is the old `cutoff_index - MINIMUM_HISTORY + 2` restated
            # against purged folds, and it still reaches the T+1 forecast the
            # contract names -- the reach the `+ 2` was load-bearing for. At a
            # gap of zero the two expressions are equal: fold `i` trained on
            # `rows[0..i-1]`, so `train[-1] <= cutoff_index` counts exactly
            # `cutoff_index - MINIMUM_HISTORY + 2` folds. Under a gap the fold
            # is the only thing that knows which rows a forecast read.
            folds = contract_folds(rows, MINIMUM_HISTORY)
            unaffected = sum(1 for train, _ in folds if train[-1] <= cutoff_index)
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

            # The other side of the same bound, and the anchor that makes the
            # oracle discriminate here. "These must not move" is a one-sided
            # claim: an implementation that trained on *fewer* rows than the
            # folds say would satisfy it for free, because fewer reads mean
            # fewer forecasts move. The bound is tight -- `unaffected` is
            # exactly the boundary, not merely a safe lower bound -- so the
            # first forecast past it must move, and saying so is what stops a
            # wrong training frame from passing as a right one.
            if unaffected < len(baseline):
                self.assertNotEqual(
                    shocked[unaffected].predicted_bps,
                    baseline[unaffected].predicted_bps,
                    msg=(
                        f"forecast {unaffected} reads a row after "
                        f"{rows[cutoff_index].date} according to its fold, but "
                        f"perturbing that row did not move it; the folds and "
                        f"the implementation disagree about what was trained on"
                    ),
                )

    def test_the_perturbation_is_actually_visible_to_the_model(self):
        """Guards the two tests above from passing because nothing changed."""

        rows = load_sample()
        cutoff_index = 15
        shocked = contract_backtest(
            perturb_after(rows, cutoff_index),
            minimum_history=MINIMUM_HISTORY,
            interval_probability=INTERVAL_PROBABILITY,
        )
        baseline = contract_backtest(
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

    This test had nothing to bite on until an ARX existed. `FittedPersistence`
    learns only a residual vector, so "fitted transform parameters are
    recomputed on a training window alone" was vacuously true of it: there is no
    transform, and the first test below is really a statement about which
    residuals the interval quantile is read from. True and worth keeping, but
    not what the contract clause is for.

    `FittedArx` fits a real transform -- one imputation mean per declared
    regressor, the value an unobserved cell is filled with -- and the second
    test is contract test 3 doing the work it was written for. A mean taken over
    the whole panel rather than the training window is the classic leak: it is
    invisible in the coefficients, it moves every forecast slightly, and it
    cannot be recovered from the output.
    """

    def test_interval_matches_parameters_refit_on_the_training_window(self):
        rows = load_sample()
        report = contract_backtest(
            rows,
            minimum_history=MINIMUM_HISTORY,
            interval_probability=INTERVAL_PROBABILITY,
        )

        for forecast, (train_indices, _) in zip(
            report.forecasts, contract_folds(rows, MINIMUM_HISTORY)
        ):
            # The last row that cleared the gap. Under a purge this is not the
            # day before the scored day, and the residual window the forecaster
            # was entitled to see ends there too.
            window = residual_window(rows, train_indices[-1])
            prediction = rows[train_indices[-1]].spread_bps

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
        # An early forecast, taken with its fold rather than by index
        # arithmetic: under a gap the third scored day is not trained through
        # `MINIMUM_HISTORY + 1`.
        position = 2
        train_indices, _ = contract_folds(rows, MINIMUM_HISTORY)[position]

        window = residual_window(rows, train_indices[-1])
        full_sample = residual_window(rows, len(rows) - 1)

        self.assertNotEqual(
            _quantile(window, UPPER_LEVEL),
            _quantile(full_sample, UPPER_LEVEL),
            msg="test panel cannot distinguish window fitting from full-sample fitting",
        )

        forecast = contract_backtest(
            rows,
            minimum_history=MINIMUM_HISTORY,
            interval_probability=INTERVAL_PROBABILITY,
        ).forecasts[position]
        prediction = rows[train_indices[-1]].spread_bps
        self.assertEqual(
            forecast.upper_bps, prediction + _quantile(window, UPPER_LEVEL)
        )

    def test_arx_imputation_parameters_come_from_the_training_window_alone(self):
        """The ARX's imputation means, refit on a window, against the pipeline.

        The contract's clause has two halves and both are checked. First, the
        parameters a standalone fit produces on a window are the training
        window's own -- computed here from the rows the transform is entitled to
        see, which is the window's *origin* rows: everything but the last, since
        the last row of a training frame is a target and never a feature.
        Second, the same window inside the full pipeline produces the same
        parameters, so nothing about running the backtest over a longer panel
        reaches back into a fit.

        The panel is shocked in its tail on purpose. On an unshocked frame the
        window mean and the full-sample mean nearly coincide, so equality would
        prove almost nothing; the assertion that the two candidate parameters
        really do differ is what makes the rest of this test evidence. Same
        structure, and the same reason, as
        `test_window_parameters_differ_from_full_sample_parameters` above.
        """

        rows = perturb_after(distinct_residual_frame(), cutoff_index=30)
        window = rows[:32]

        def observed_mean(frame, name):
            # Origin rows only: frame[:-1]. A mean over one row more is a mean
            # over a row the transform was never handed.
            seen = [
                float(row.values[name])
                for row in frame[:-1]
                if row.values[name] is not None
            ]
            return sum(seen) / len(seen)

        model = fit_arx(window, CONFORMANCE_REGRESSORS, minimum_history=20)

        for name in CONFORMANCE_REGRESSORS:
            window_mean = observed_mean(window, name)
            full_sample_mean = observed_mean(rows, name)

            self.assertNotAlmostEqual(
                window_mean,
                full_sample_mean,
                places=6,
                msg=(
                    f"test panel cannot distinguish window fitting from "
                    f"full-sample fitting for {name}"
                ),
            )
            self.assertAlmostEqual(model.imputations[name], window_mean, places=12)

        # The same window reached through the full pipeline. Under a gap the
        # backtest's last origin no longer trains on `rows[:-1]` -- it trains on
        # the last fold's own rows -- so the standalone fit is made on those.
        # The half being checked is unchanged: nothing about running the
        # backtest over a longer panel may reach back into a fit.
        report = contract_backtest(
            rows,
            minimum_history=20,
            fit_model=partial(fit_arx, regressors=CONFORMANCE_REGRESSORS),
        )
        last_train, _ = contract_folds(rows, 20)[-1]
        last_frame = [rows[i] for i in last_train]
        standalone = fit_arx(last_frame, CONFORMANCE_REGRESSORS, minimum_history=20)
        self.assertEqual(dict(report.model.imputations), dict(standalone.imputations))
        for name in CONFORMANCE_REGRESSORS:
            self.assertAlmostEqual(
                report.model.imputations[name],
                observed_mean(last_frame, name),
                places=12,
            )
        self.assertEqual(report.model.coefficients, standalone.coefficients)


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
                    # Same reasoning as `release_lag` above: the shape is a
                    # seam both tracks build against, so it is checked by the
                    # shared, human-owned module rather than restated here.
                    # The restatement this replaces also required `absolute`,
                    # which is what made an absolute-only bound the only
                    # expressible kind.
                    problems = validate_identity_tolerance(
                        source_id, identity["name"], identity.get("tolerance")
                    )
                    self.assertEqual(problems, [], msg="; ".join(problems))

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

    The frame also carries two moving exogenous columns. Persistence reads
    neither -- it reads `spread_bps` and nothing else, so every number it
    reported before they were added is unchanged -- and the ARX conformance case
    needs a frame it can be fitted on. Both models therefore run the conformance
    suite over the same rows, which is what makes "the interface generalises" a
    statement about the interface rather than about two fixtures.
    """

    rows = []
    state = seed
    for index in range(count):
        state = (1103515245 * state + 12345) % (2 ** 31)
        rows.append(
            DailyObservation(
                date(2026, 1, 1) + timedelta(days=index),
                {
                    "sofr": 4.30 + 0.0001 * (state % 9973),
                    "iorb": 4.30,
                    "sofr_volume": 2100.0 + (state % 1301) / 3.0,
                    "on_rrp": 90.0 + (state % 211) / 10.0,
                },
            )
        )
    return rows


#: The regressor set the ARX conformance case declares. Named here because
#: nothing in the repository declares a feature set and the ARX requires the
#: caller to say -- see `fit_arx`, and the block record's note on what a
#: declared feature set would have to say before this could stop being a
#: call-site constant.
CONFORMANCE_REGRESSORS = ("sofr_volume", "on_rrp")

#: What the backtests below declare, and the gap they are pinned at.
#:
#: `rolling_persistence_backtest` no longer takes a `purge`: it takes a declared
#: feature set, resolves it through `contract.sources_for_features`, and sizes
#: the gap with `registry.max_release_lag_days`. The tests in this file are
#: about eligibility, future perturbation and transform isolation rather than
#: about the derivation, so they need a *known* gap -- and the only way to state
#: one now is to declare a registry that produces it.
#:
#: **The gap is 1, not 0.** `max_release_lag_days` refuses to return zero
#: ("selected sources must produce a nonzero purge"), so an unpurged backtest is
#: no longer expressible through the declared path at all. Every assertion below
#: that used to read `rows[i - 1]` therefore reads the fold's own last training
#: row instead. That is a change in the arithmetic these tests do, not in what
#: they claim: a leak still shows up as a forecast that moved.
CONTRACT_FEATURES = ("spread_bps",) + CONFORMANCE_REGRESSORS
CONTRACT_PURGE = 1
CONTRACT_DECISION_TIME = time(16, 0)


def contract_registry(purge=CONTRACT_PURGE, features=CONTRACT_FEATURES):
    """A registry pricing every source `features` uses at exactly `purge` days.

    A fixture. It is not `metadata/sources.json` and does not describe it: the
    real registry declares `fred_macro_latest_vintage` on a
    `snapshot_retrieved_at` basis, which `max_release_lag_days` refuses to price
    without an `available_at` on every row -- so against the real file no
    feature set containing `spread_bps` runs at all. That refusal is a correct
    guard and is pinned in `tests/test_baseline.py` and `tests/test_cli_eval.py`
    rather than softened here.
    """

    return {
        source: {
            "release_lag": {
                "basis": "record_date",
                "unit": "calendar_days",
                "days": purge,
                "available_time": "00:00",
                "timezone": "America/New_York",
            }
        }
        for source in sources_for_features(features)
    }


def contract_backtest(rows, **kwargs):
    """`rolling_persistence_backtest` at `CONTRACT_PURGE`, declared honestly."""

    return rolling_persistence_backtest(
        rows,
        features=CONTRACT_FEATURES,
        registry=contract_registry(),
        decision_time=CONTRACT_DECISION_TIME,
        **kwargs,
    )


def contract_folds(rows, minimum_history, purge=CONTRACT_PURGE):
    """The folds `contract_backtest` runs over, built without the splitter.

    An oracle. Every assertion below that needs to know which rows a forecast
    was entitled to read comes through here, and none of it may pass through
    `rolling_origin`, `_folds_unchecked`, `_train_end` or `clears_purge`. The
    first version of this helper called `rolling_origin`, and the cost was
    measured rather than argued: under a mutation that shortened every training
    frame by one row, this file lost six of the seven tests that used to catch
    it. An expectation that moves with the implementation it checks cannot fail.

    So this is a brute-force walk that shares nothing with `repo_model.splits`.
    No `bisect` -- a plain scan over every earlier row. No `timedelta`; the gap
    is read as a difference in days, which is a third arithmetic form. The
    module subtracts the lag from the block's date, its docstring states the
    rule as adding the lag to the row's date, and this asks how many days apart
    the two are. All three agree only if the boundary is right.

    `purge` is a parameter so that
    `ContractFoldOracleTests.test_the_oracle_disagrees_with_a_deliberately_wrong_gap`
    can check that this construction can tell gaps apart at all. It is not an
    escape hatch: `contract_backtest` still reaches its gap through
    `contract_registry` and `max_release_lag_days`, which refuse to price zero,
    and nothing here is passed to the backtest.

    `step` is 1 because that is what `contract_backtest` runs at -- one scored
    observation per fold.

    Raises rather than returning `[]` when no fold exists. A caller that zips
    forecasts against an empty fold list would assert nothing and say so
    loudly; `tests/test_splits.py:reference_folds` can return `[]` because its
    callers assert on the emptiness, and these do not.
    """

    dates = [row.date for row in rows]

    def survivors(test_start):
        """Rows before `test_start` that are far enough back to be trainable."""

        return [
            index
            for index in range(test_start)
            if (dates[test_start] - dates[index]).days > purge
        ]

    folds = []
    started = False
    for start in range(len(dates)):
        eligible = survivors(start)
        if not started:
            if len(eligible) < minimum_history:
                continue
            started = True
        folds.append((tuple(eligible), (start,)))

    if not folds:
        raise ValueError(
            f"{len(dates)} observations yield no fold with {minimum_history} "
            f"training rows behind a {purge}-day gap; every assertion taken "
            f"from these folds would be vacuous"
        )
    return folds


class ContractFoldOracleTests(unittest.TestCase):
    """Guards `contract_folds`. An oracle nobody checks is the failure one level out.

    Five assertions in this file take the rows a forecast was entitled to read
    from `contract_folds` rather than from index arithmetic. That is only worth
    anything while the oracle can still tell a right fold from a wrong one, and
    while it is still built independently of the thing it checks. Both halves
    are checked here, because the block that produced this file exists because
    the previous version of the oracle had neither.
    """

    def test_the_oracle_disagrees_with_a_deliberately_wrong_gap(self):
        """It must be able to tell gaps apart at all.

        If `contract_folds` ignored the gap, every assertion drawn from it would
        pass just as happily against a backtest that ignored the gap too --
        which is precisely the leak the purge exists to prevent.
        """

        rows = load_sample()
        declared = contract_folds(rows, MINIMUM_HISTORY)

        self.assertNotEqual(
            declared,
            contract_folds(rows, MINIMUM_HISTORY, purge=CONTRACT_PURGE + 1),
            msg="oracle cannot see a one-day error in the gap",
        )
        self.assertNotEqual(
            declared,
            contract_folds(rows, MINIMUM_HISTORY, purge=0),
            msg="oracle cannot tell a purged backtest from an unpurged one",
        )

    def test_the_oracle_is_not_vacuous_and_covers_every_scored_forecast(self):
        """A silently empty or short fold list would make five tests pass blind.

        Three of the five zip forecasts against folds, and `zip` stops at the
        shorter argument, so an oracle that produced no folds -- or one fold
        fewer -- would not fail. It would assert nothing. Pin the count against
        the report the backtest actually produces.
        """

        rows = load_sample()
        folds = contract_folds(rows, MINIMUM_HISTORY)
        self.assertTrue(folds, msg="no folds; every assertion taken from them is vacuous")

        report = contract_backtest(
            rows,
            minimum_history=MINIMUM_HISTORY,
            interval_probability=INTERVAL_PROBABILITY,
        )
        self.assertEqual(
            len(folds),
            len(report.forecasts),
            msg=(
                "the oracle and the backtest disagree about how many days are "
                "scored; a zip over the two would silently drop the difference"
            ),
        )

        for train, test in folds:
            self.assertEqual(train, tuple(range(len(train))))
            self.assertEqual(len(test), 1)
            self.assertGreaterEqual(len(train), MINIMUM_HISTORY)

    def test_the_oracle_reaches_nothing_in_the_splitter(self):
        """The independence itself, checked statically rather than asserted.

        Every other guard here would pass just as well against an oracle that
        delegated to `rolling_origin` -- correct folds are correct folds, and
        the delegation only shows up under a mutation of the splitter, which the
        ordinary suite never runs. That is exactly how the previous version of
        this helper stayed green while six contract tests quietly stopped being
        able to fail. So this reads the oracle's own source and refuses the
        names that would put it back on the implementation's arithmetic.
        """

        forbidden = {
            "rolling_origin",
            "_folds_unchecked",
            "_train_end",
            "clears_purge",
            "bisect",
            "bisect_left",
            "timedelta",
        }
        tree = ast.parse(textwrap.dedent(inspect.getsource(contract_folds)))
        used = {
            node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
        } | {
            node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
        }
        self.assertEqual(
            used & forbidden,
            set(),
            msg=(
                "contract_folds reached back into the splitter; the expectation "
                "now moves with the implementation it is checking and this "
                "file has stopped being the line of defence"
            ),
        )


class ForecastInterfaceConformance:
    """AGENT_CONTRACT.md, "The forecast interface", against every implementer.

    These assertions were written against `FittedPersistence` concretely, when
    it was the only fitted model in the repository. That was correct then and is
    the problem now: an interface with one implementer is a description of that
    implementer, and every incidental property of `FittedPersistence` -- that it
    reads exactly `spread_bps`, that its residuals are one-step differences,
    that it fits no transform at all -- was free to be read by callers as part
    of the contract. Lifting the tests into a base that concrete cases inherit
    is what turns them from a description into a constraint. The names are
    unchanged; they are the acceptance criteria of the previous block and the
    merge record refers to them.

    They also carry their own provenance: this class replaced an
    `expectedFailure` presence tripwire that stood here while
    `fit`/`predict`/`predict_stress` did not exist. That tripwire tested
    `hasattr` and nothing else; it went to unexpected success -- a red build --
    the moment the interface landed, which is the mechanism working.

    A plain mixin rather than a `TestCase`, so `unittest` collects it through
    its concrete subclasses and does not also run it once with no model.

    Subclasses declare `MODEL_CLASS` and a `fit_model` hook. Everything else is
    shared, including the fixture: both models are fitted on the same rows, so a
    difference between the cases is a difference between the models.

    The load-bearing test is
    `test_predict_stress_agrees_with_the_quantiles_predict_reports`. The
    contract's Target says stress "is not a separately fitted rare-event
    classifier ... it is an exceedance derived from the predictive
    distribution", and that is a claim about where the numbers come from, which
    no shape check can see. A classifier fitted on the `stress_gt_*` columns
    would satisfy every other test here -- right length, right order,
    non-increasing, probabilities in [0, 1] -- and could be well calibrated on
    its own terms while still contradicting the quantiles reported beside it.
    The agreement test is the only one that can tell the two apart, and it now
    says so for both models rather than for one.
    """

    MINIMUM_HISTORY = 20

    #: The implementation this case covers. Read by
    #: `ForecastInterfaceCoverageTests`, which discovers the implementations in
    #: `baseline` and checks each one is named by some case.
    MODEL_CLASS = None

    def fit_model(self, train_frame, cutoff=None):
        """Fit `MODEL_CLASS` on `train_frame`. The one thing cases differ in."""

        raise NotImplementedError

    def setUp(self):
        self.rows = distinct_residual_frame()
        self.train = self.rows[:-1]
        self.feature_row = self.rows[-2]
        self.model = self.fit_model(self.train)

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

        self.assertIsInstance(self.model, self.MODEL_CLASS)
        self.assertEqual(self.model.cutoff, self.train[-1].date)

        # An explicitly declared cutoff is honoured rather than re-derived, and
        # a frame reaching past it is a leak, not a rounding matter.
        earlier = self.fit_model(self.train[:-3], cutoff=self.train[-4].date)
        self.assertEqual(earlier.cutoff, self.train[-4].date)
        with self.assertRaises(LookAheadError):
            self.fit_model(self.train, cutoff=self.train[-4].date)

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

        The grid is centred on the model's own point forecast, not on the
        feature row's spread: those coincide for persistence and do not for a
        regression, and a grid pinned to persistence's centre would walk off the
        support of any model whose centre sits elsewhere.
        """

        anchor = self.model.point_forecast(self.feature_row)
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

        anchor = self.model.point_forecast(self.feature_row)
        far_above = anchor + max(self.model.residuals) + 1.0
        far_below = anchor + min(self.model.residuals) - 1.0

        self.assertEqual(self.model.predict_stress(self.feature_row, taus=[far_above])[0], 0.0)
        self.assertEqual(self.model.predict_stress(self.feature_row, taus=[far_below])[0], 1.0)

    def test_a_tau_family_that_is_not_ascending_is_refused(self):
        """Monotonicity in tau is only meaningful against an increasing family."""

        anchor = self.model.point_forecast(self.feature_row)
        with self.assertRaises(ValueError):
            self.model.predict_stress(self.feature_row, taus=[anchor + 1.0, anchor])
        with self.assertRaises(ValueError):
            self.model.predict_stress(self.feature_row, taus=[])


class ForecastInterfaceTests(ForecastInterfaceConformance, unittest.TestCase):
    """The conformance suite against `FittedPersistence`."""

    MODEL_CLASS = FittedPersistence

    def fit_model(self, train_frame, cutoff=None):
        return fit(train_frame, cutoff=cutoff, minimum_history=self.MINIMUM_HISTORY)


class ArxForecastInterfaceTests(ForecastInterfaceConformance, unittest.TestCase):
    """The conformance suite against `FittedArx`, on the same rows.

    The second implementer is what converts each assertion above from a
    description of persistence into a constraint on the interface. Three of them
    had nothing to check against until this case existed:
    `test_predict_stress_agrees_with_the_quantiles_predict_reports` was a
    statement about `_exceedance_from_residuals` over one-step differences;
    `predict` returning the declared grid was a statement about one anchor plus
    a residual quantile; and the whole suite was silent on a model that reads
    more of `values` than `spread_bps`.

    The regressor set is declared at the call site because nothing in the
    repository declares one. That is a stopgap, written up in the block record
    rather than resolved here.
    """

    MODEL_CLASS = FittedArx

    def fit_model(self, train_frame, cutoff=None):
        return fit_arx(
            train_frame,
            CONFORMANCE_REGRESSORS,
            cutoff=cutoff,
            minimum_history=self.MINIMUM_HISTORY,
        )


class ThresholdForecastInterfaceTests(ForecastInterfaceConformance, unittest.TestCase):
    """The conformance suite against `FittedThreshold`, on the same rows.

    The third implementer, and the first whose covariate does something other
    than contribute a term: `on_rrp` selects which of two fitted regimes
    produces the point forecast. Every assertion in the mixin was written when
    a fitted model was one coefficient vector over one window, so what this case
    establishes is that they were assertions about the *interface* -- that
    `predict` returns the declared grid and `predict_stress` inverts it over one
    law, whichever model the row selected.

    Two of them can only be exercised by a model shaped like this.
    `test_predict_stress_never_rises_with_tau` walks a dense grid around the
    model's own centre, and this is the first centre that is a step function of
    the feature row rather than a continuous function of it; and
    `test_predict_stress_agrees_with_the_quantiles_predict_reports` is the
    reason `FittedThreshold` pools its residual law across regimes rather than
    fitting one per regime, since a per-regime law would make `residuals` a
    sample that `predict` does not read.

    `on_rrp` is the threshold variable and is already in
    `CONFORMANCE_REGRESSORS`, so this model reads exactly what the ARX case
    reads and `CONTRACT_FEATURES` is untouched. That a column may be both a
    regressor and the regime selector is deliberate -- a variable can shift the
    level and switch the relationship -- and `features_read` reports it once.
    The case where the threshold variable is *outside* the declared set is the
    acceptance criterion of this block and lives in `tests/test_baseline.py`,
    where the backtest that would be purged over the wrong sources is.

    The threshold is estimated on the training frame rather than declared here,
    so the fixture exercises the search rather than routing around it.
    """

    MODEL_CLASS = FittedThreshold

    def fit_model(self, train_frame, cutoff=None):
        return fit_threshold(
            train_frame,
            CONFORMANCE_REGRESSORS,
            "on_rrp",
            cutoff=cutoff,
            minimum_history=self.MINIMUM_HISTORY,
        )


def _forecast_implementations():
    """Fitted-model implementations in `repo_model.baseline`, by name.

    Discovered rather than listed. A class defined in `baseline` that offers
    both `predict` and `predict_stress` is a fitted model as far as the contract
    is concerned, whatever else it does. Protocols are excluded because
    `FittedForecastModel` is the shape, not an implementation of it, and classes
    merely imported into the module are excluded by `__module__` -- which is
    where a class was defined, not where it was bound.
    """

    found = {}
    for name, obj in vars(baseline).items():
        if not inspect.isclass(obj) or obj.__module__ != baseline.__name__:
            continue
        if getattr(obj, "_is_protocol", False):
            continue
        if callable(getattr(obj, "predict", None)) and callable(
            getattr(obj, "predict_stress", None)
        ):
            found[name] = obj
    return found


def _conformance_cases():
    """`{model class: [test case, ...]}` over every subclass of the mixin."""

    cases = {}
    pending = list(ForecastInterfaceConformance.__subclasses__())
    while pending:
        case = pending.pop()
        pending.extend(case.__subclasses__())
        if issubclass(case, unittest.TestCase):
            cases.setdefault(case.MODEL_CLASS, []).append(case)
    return cases


class ForecastInterfaceCoverageTests(unittest.TestCase):
    """The guard that keeps the conformance suite a conformance suite.

    Two models is what makes the interface a constraint. Three is where it stops
    being one again, quietly: model three arrives with a bespoke test class of
    its own, every test passes, and nothing anywhere says the contract's five
    assertions were never run against it. By then the suite is a conformance
    suite in name and a collection of per-model tests in fact, and the way that
    is discovered is a sixth model breaking a caller that relied on something
    only the first model ever guaranteed.

    So the implementations are discovered from the module and checked against
    the cases. Discovered, not enumerated: a list that has to be kept up to date
    is exactly the failure this test exists to prevent, and it would be updated
    in the same commit that added the model it was meant to catch.
    """

    def test_every_implementation_in_baseline_runs_the_conformance_suite(self):
        implementations = _forecast_implementations()
        self.assertIn(
            "FittedPersistence",
            implementations,
            msg="discovery found no persistence model; the discovery is broken, "
            "not the module",
        )
        self.assertIn("FittedArx", implementations)

        cases = _conformance_cases()
        uncovered = sorted(
            name
            for name, implementation in implementations.items()
            if implementation not in cases
        )
        self.assertEqual(
            uncovered,
            [],
            msg=(
                f"{uncovered} implement the forecast interface in "
                f"repo_model.baseline and no conformance case runs "
                f"AGENT_CONTRACT.md's five assertions against them. Add a "
                f"ForecastInterfaceConformance subclass rather than a bespoke "
                f"test class: a model with its own tests and no conformance case "
                f"is how the suite stops being one"
            ),
        )

        # And each case really runs the suite: a subclass that shadowed the
        # inherited tests away would otherwise satisfy the check above while
        # asserting nothing the contract asked for. The names come from the
        # mixin rather than a list here, for the same reason as above.
        declared = sorted(
            name
            for name in vars(ForecastInterfaceConformance)
            if name.startswith("test_")
        )
        self.assertGreaterEqual(len(declared), 5)
        loader = unittest.TestLoader()
        for implementation, owners in cases.items():
            for case in owners:
                self.assertLessEqual(
                    set(declared),
                    set(loader.getTestCaseNames(case)),
                    msg=(
                        f"{case.__name__} covers {implementation.__name__} but "
                        f"does not run every conformance test"
                    ),
                )


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


class FieldReleaseLagCoverageTests(unittest.TestCase):
    """The field half of the map, and the rule that lets a snapshot be priced.

    `FEATURE_FIELDS` states the source *field* each panel column draws on, so a
    release lag can be declared per field. That matters because one source can
    carry an administered rate that is never revised beside a statistical
    estimate that is revised for months: a lag declared once for the source is
    then wrong for both, and `fred_macro_latest_vintage` is exactly that source.

    The rule these tests hold in place: a field of a `snapshot_retrieved_at`
    source may be priced only if it declares `revision_policy: "never_revised"`
    with non-empty `revision_evidence`. Latest vintage stands in for a
    point-in-time record exactly when the value never moves after publication,
    and that is a claim about the world that has to be made explicitly and
    carry what establishes it -- not inferred because a number would be
    convenient.

    Mutation record, the human-side patch that introduced this class. Run in a
    copy under `$HOME` with `data/`, `.github/`, `metadata/`, `.gitignore`, the
    root Markdown and `docs/PROJECT_STATUS.md` present -- the freshness guard
    reads the last three, and their absence is two false kills. `-B` with
    `PYTHONDONTWRITEBYTECODE=1`, unmutated control green before and after.

      * `FEATURE_FIELDS["iorb"]` field renamed `IORB` -> `IORBB`. Kills two:
        `test_every_declared_feature_field_exists_in_its_source` at subtest
        `feature='iorb'`, and
        `test_the_resolved_source_ids_are_unchanged_by_the_field_map`.

      * `FEATURE_FIELDS["iorb"]` repointed at `("nyfed_sofr", "SOFR")`. Kills
        five, and the extra three are the point rather than noise: both
        real-registry refusal tests fail, because `iorb` no longer resolves to
        the snapshot source. That is the map holding the tree.

      * The snapshot revision-policy requirement in
        `validate_field_release_lag` made a no-op. Kills exactly one, its own
        test, and no other.

    Mutation record, patch 3 -- the first declared `field_release_lags` block
    (`fred_macro_latest_vintage.IORB`). The three mutations below were not
    runnable before it, and each kills exactly one test, by assertion:

      * The `field_release_lags` key `IORB` renamed `IORBB`. Kills
        `test_every_field_release_lag_names_a_declared_field` at subtest
        `(source='fred_macro_latest_vintage', field='IORBB')` -- the test that
        was vacuous until this block existed, firing for the first time.

      * `revision_policy` removed from the declared block. Kills
        `test_registry_interface.RegistryModuleTests`
        `::test_the_declared_registry_is_well_formed`.

      * `revision_evidence` emptied. Kills the same single test, the same way.

    Read the last two together, because the finding is in what did *not* fire.
    `test_a_snapshot_field_is_priceable_only_with_a_declared_revision_policy`
    and `test_a_never_revised_claim_carries_its_evidence` are the assertions
    written for exactly these two mutations, and neither one moves: they hold
    the *rule* in `validate_field_release_lag` against fixtures, and cannot see
    the real file. Only `test_the_declared_registry_is_well_formed` holds the
    declared registry to that rule, so at suite level the two mutations are
    indistinguishable. That is not a gap -- the real registry is held, once --
    but a reader who assumes the named tests are what guard the declaration
    would be wrong, and would be wrong in the direction this repository keeps
    finding.
    """

    def _registry(self):
        return json.loads(SOURCE_REGISTRY.read_text(encoding="utf-8"))

    def _snapshot_source(self, **field_block):
        """A minimal snapshot-basis source carrying one field-level block."""

        return {
            "fields": ["THING"],
            "release_lag": {
                "basis": "snapshot_retrieved_at",
                "note": "latest vintage",
            },
            "field_release_lags": {"THING": dict(field_block)},
        }

    def _priced_block(self, **overrides):
        block = {
            "basis": "record_date",
            "unit": "calendar_days",
            "days": 1,
            "available_time": "16:15",
            "timezone": "America/New_York",
            "revision_policy": "never_revised",
            "revision_evidence": "vintage comparison; see the decision record",
        }
        block.update(overrides)
        return block

    def test_every_declared_feature_field_exists_in_its_source(self):
        """The field-level version of `dealer_treasury_position`.

        A column can be declared in four places and ingested by none;
        declaration is not provenance. A field named here that the source does
        not carry would resolve to a lag nobody can look up, and would read as
        though it had one.
        """

        registry = self._registry()
        for feature, pairs in FEATURE_FIELDS.items():
            with self.subTest(feature=feature):
                self.assertTrue(pairs, msg=f"{feature!r} maps to no (source, field) pair")
                for source_id, field in pairs:
                    self.assertIn(source_id, registry)
                    self.assertIn(
                        field,
                        registry[source_id].get("fields", ()),
                        msg=(
                            f"{feature!r} maps to {source_id}.{field}, which is "
                            f"not in that source's declared fields"
                        ),
                    )

    def test_every_field_release_lag_names_a_declared_field(self):
        """A lag declared for a field the source does not carry prices nothing.

        No longer vacuous: `fred_macro_latest_vintage` declares one, and
        renaming its key kills this test and nothing else. The fixture-level
        rule test below stays, because it is what keeps this one honest on the
        day the declaration is removed again.
        """

        registry = self._registry()
        for source_id, source in registry.items():
            for field in sorted(source.get("field_release_lags", {})):
                with self.subTest(source=source_id, field=field):
                    self.assertIn(field, source.get("fields", ()))

    def test_a_snapshot_field_is_priceable_only_with_a_declared_revision_policy(self):
        """The rule itself, against a fixture, so it has teeth today."""

        source = self._snapshot_source(**self._priced_block())
        self.assertEqual(
            validate_field_release_lag(
                "src", "THING", source["field_release_lags"]["THING"],
                source["release_lag"]["basis"],
            ),
            [],
        )

        without = self._priced_block()
        del without["revision_policy"]
        problems = validate_field_release_lag(
            "src", "THING", without, "snapshot_retrieved_at"
        )
        self.assertTrue(problems)
        self.assertIn("revision_policy", " ".join(problems))

        wrong = self._priced_block(revision_policy="revised_sometimes")
        self.assertTrue(
            validate_field_release_lag("src", "THING", wrong, "snapshot_retrieved_at")
        )
        self.assertNotIn("revised_sometimes", REVISION_POLICIES)

    def test_a_never_revised_claim_carries_its_evidence(self):
        """A claim with no evidence attached is indistinguishable from a guess."""

        for evidence in ("", "   "):
            with self.subTest(evidence=evidence):
                problems = validate_field_release_lag(
                    "src",
                    "THING",
                    self._priced_block(revision_evidence=evidence),
                    "snapshot_retrieved_at",
                )
                self.assertTrue(problems)
                self.assertIn("revision_evidence", " ".join(problems))

    def test_a_revision_policy_on_a_real_basis_source_is_refused(self):
        """It licenses nothing there, and a key nobody reads is how one got missed."""

        problems = validate_field_release_lag(
            "src", "THING", self._priced_block(), "record_date"
        )
        self.assertTrue(problems)
        self.assertIn("revision_policy", " ".join(problems))

    def test_the_resolved_source_ids_are_unchanged_by_the_field_map(self):
        """`FEATURE_SOURCES` is now a projection. Pin it to longhand tuples.

        Comparing the projection against `field_sources_for_features` would
        agree by construction whatever either says -- with one derived from the
        other, there is no state of the world in which they differ. That is the
        check-anchored-to-itself shape, in the file where it has already been
        found once. So the expectation is typed out here, and it is the only
        form of this test that can fail.
        """

        self.assertEqual(
            sources_for_features(("spread_bps",)),
            ("fred_macro_latest_vintage", "nyfed_sofr"),
        )
        self.assertEqual(
            sources_for_features(("sofr_volume", "on_rrp", "quarter_end")),
            ("fred_macro_latest_vintage", "nyfed_sofr"),
        )
        self.assertEqual(
            field_sources_for_features(("spread_bps",)),
            (
                ("fred_macro_latest_vintage", "IORB"),
                ("nyfed_sofr", "SOFR"),
            ),
        )
        self.assertEqual(
            field_sources_for_features(("tga",)),
            (("fred_macro_latest_vintage", "WTREGEN"),),
        )

    def test_the_field_resolver_raises_on_the_same_names_the_source_one_does(self):
        """Two walks, one classification. They must refuse the same names."""

        for names in (("no_such_column",), ("dealer_treasury_position",)):
            with self.subTest(names=names):
                with self.assertRaises(UndeclaredFeatureError):
                    sources_for_features(names)
                with self.assertRaises(UndeclaredFeatureError):
                    field_sources_for_features(names)


class FeatureSourceMapCoverageTests(unittest.TestCase):
    """The feature-to-source map describes the tree, or it fails.

    An ownership list that is not asserted against the tree silently stops
    describing the tree; five files were unowned before the gate could prove
    its own coverage. `contract.FEATURE_SOURCES` is the same shape of hazard
    one layer along -- a hand-written correspondence that nothing forces to
    stay true -- so it ships with the assertions rather than with a comment
    asking people to keep it current.

    The map cannot be derived from `metadata/sources.json`: the registry names
    fields in source vocabulary (`SOFR`, `WTREGEN`, `mmf_net_assets`) and the
    panel names them in model vocabulary (`sofr`, `tga`, `mmf_assets`), and
    three of the correspondences are pure renames with no rule behind them.
    Deriving it would mean string matching on regressor names, which is what
    the purged-backtest block was written to avoid. So it is declared once and
    checked three ways here.
    """

    def _registry(self):
        return json.loads(SOURCE_REGISTRY.read_text(encoding="utf-8"))

    def _panel_columns(self):
        """Every column a modelling panel may carry, in model vocabulary."""

        return tuple(
            name for name in REQUIRED_FIELDS if name != "date"
        ) + tuple(OPTIONAL_NUMERIC_FIELDS)

    def test_every_mapped_source_exists_in_the_registry(self):
        """Catches a source renamed or removed on Track A's side.

        The map would otherwise keep resolving to an ID nobody ingests, and
        `max_release_lag_days` would raise `unknown source` from inside an
        evaluation run rather than here.
        """

        registry = self._registry()
        for feature, sources in FEATURE_SOURCES.items():
            with self.subTest(feature=feature):
                self.assertTrue(
                    sources,
                    msg=(
                        f"{feature!r} maps to no source; a feature that "
                        "contributes nothing to the purge belongs in "
                        "CALENDAR_FEATURES or UNSOURCED_FEATURES, where the "
                        "reason is stated, not in FEATURE_SOURCES with an "
                        "empty tuple"
                    ),
                )
                for source_id in sources:
                    self.assertIn(
                        source_id,
                        registry,
                        msg=(
                            f"{feature!r} maps to {source_id!r}, which is not "
                            "in metadata/sources.json"
                        ),
                    )

    def test_every_panel_column_is_classified_exactly_once(self):
        """The assertion that fires when someone adds a panel column.

        Every column must sit in exactly one of FEATURE_SOURCES,
        CALENDAR_FEATURES and UNSOURCED_FEATURES. Unclassified is the failure
        this test exists for; classified twice is worse, because the resolution
        order in `sources_for_features` would then decide silently which
        classification wins.
        """

        collections = {
            "FEATURE_SOURCES": set(FEATURE_SOURCES),
            "CALENDAR_FEATURES": set(CALENDAR_FEATURES),
            "UNSOURCED_FEATURES": set(UNSOURCED_FEATURES),
        }

        for column in self._panel_columns():
            holders = [
                name for name, members in collections.items() if column in members
            ]
            with self.subTest(column=column):
                self.assertEqual(
                    len(holders),
                    1,
                    msg=(
                        f"panel column {column!r} is classified in {holders} "
                        "-- it must appear in exactly one of "
                        f"{sorted(collections)}. Classify it in contract.py, "
                        "not at the call site."
                    ),
                )

        declared = set().union(*collections.values())
        strays = sorted(declared - set(self._panel_columns()) - set(DERIVED_FEATURES))
        self.assertEqual(
            strays,
            [],
            msg=(
                f"{strays} are classified in contract.py but are not panel "
                "columns and not derived features. A map that describes "
                "columns the loader cannot produce has stopped describing the "
                "tree in the other direction."
            ),
        )

    def test_a_derived_feature_declares_the_columns_its_implementation_reads(self):
        """Anchored to `data.py`, not to the declaration it is checking.

        The first version of this test asked whether resolving `spread_bps`
        included the sources of `spread_bps`'s *declared* constituents. That is
        true whatever the declaration says, so dropping `iorb` from
        DERIVED_FEATURES killed nothing -- the fifth instance of *a check
        anchored to the thing it is checking cannot fail*, found in this file
        by the mutation that was supposed to confirm it.

        The independent anchor is the implementation. `DailyObservation`
        computes the spread from `values["sofr"]` and `values["iorb"]`; the
        declaration must name exactly those. A future derived feature computed
        somewhere other than `DailyObservation` needs its own reader here
        rather than an exemption.
        """

        readers = {"spread_bps": DailyObservation.spread_bps.fget}
        self.assertEqual(
            set(DERIVED_FEATURES),
            set(readers),
            msg=(
                "a derived feature was added without an independent reader to "
                "check its declaration against; add one rather than trusting "
                "DERIVED_FEATURES to describe itself"
            ),
        )

        for feature, reader in readers.items():
            with self.subTest(feature=feature):
                tree = ast.parse(textwrap.dedent(inspect.getsource(reader)))
                read = {
                    node.slice.value
                    for node in ast.walk(tree)
                    if isinstance(node, ast.Subscript)
                    and isinstance(node.value, ast.Attribute)
                    and node.value.attr == "values"
                    and isinstance(node.slice, ast.Constant)
                    and isinstance(node.slice.value, str)
                }
                self.assertTrue(
                    read,
                    msg=(
                        f"found no panel columns in the source of {feature!r}; "
                        "the reader no longer matches the implementation and "
                        "this test has stopped checking anything"
                    ),
                )
                self.assertEqual(
                    set(DERIVED_FEATURES[feature]),
                    read,
                    msg=(
                        f"{feature!r} is declared over "
                        f"{sorted(DERIVED_FEATURES[feature])} but its "
                        f"implementation reads {sorted(read)}. A derived "
                        "feature purged against fewer columns than it reads is "
                        "purged against less evidence than it uses."
                    ),
                )

    def test_every_derived_feature_resolves_to_classified_constituents(self):
        """A derived feature cannot outlive the columns it is computed from."""

        for feature, constituents in DERIVED_FEATURES.items():
            with self.subTest(feature=feature):
                self.assertTrue(constituents)
                resolved = sources_for_features([feature])
                for constituent in constituents:
                    self.assertIn(
                        constituent,
                        set(FEATURE_SOURCES)
                        | set(CALENDAR_FEATURES)
                        | set(DERIVED_FEATURES),
                        msg=(
                            f"{feature!r} is computed from {constituent!r}, "
                            "which is not classified"
                        ),
                    )
                for constituent in constituents:
                    for source_id in FEATURE_SOURCES.get(constituent, ()):
                        self.assertIn(
                            source_id,
                            resolved,
                            msg=(
                                f"{feature!r} resolved to {resolved} and "
                                f"dropped {source_id!r}, which {constituent!r} "
                                "draws on. A derived feature that loses one of "
                                "its constituents' sources is purged against "
                                "less evidence than it uses."
                            ),
                        )

    def test_every_registry_source_reaches_at_least_one_panel_column(self):
        """Catches a source that is ingested and never modelled.

        Also catches a source whose fields were collapsed away: if
        `treasury_auctions` ever loses its one panel column, this fails rather
        than the source quietly becoming unreachable.
        """

        reached = {
            source_id
            for sources in FEATURE_SOURCES.values()
            for source_id in sources
        }
        unreached = sorted(set(self._registry()) - reached)
        self.assertEqual(
            unreached,
            [],
            msg=(
                f"{unreached} are ingested but no panel column draws on them. "
                "Either a column is missing from FEATURE_SOURCES or the source "
                "is not modelled and should be recorded as such."
            ),
        )

    def test_an_unclassified_feature_name_raises_rather_than_purging_zero(self):
        """The failure mode the map exists to prevent.

        A feature nobody classified must not resolve to an empty source set: an
        empty set is a zero-day gap, which is the leak the purge exists to
        stop, arriving as a silence rather than as an error.
        """

        with self.assertRaises(UndeclaredFeatureError):
            sources_for_features(["not_a_panel_column"])

    def test_a_declared_but_unsourced_feature_raises_with_its_reason(self):
        """`dealer_treasury_position` is declared in four places and ingested by none.

        It is in OPTIONAL_NUMERIC_FIELDS, DATA.md, the sample panel header and
        two tests, and nothing in metadata/sources.json produces it. Declaring
        a column is not the same as having provenance for it, and using one
        must say so rather than purge zero days.
        """

        for feature, reason in UNSOURCED_FEATURES.items():
            with self.subTest(feature=feature):
                self.assertTrue(reason.strip())
                with self.assertRaises(UndeclaredFeatureError) as caught:
                    sources_for_features([feature])
                self.assertIn(reason, str(caught.exception))


class IdentityToleranceTests(unittest.TestCase):
    """A tolerance may move with the scale of what it bounds. None does yet.

    This is the schema only. `sec_nmfp` bounds a scale-free identity with one
    absolute number, and that number cannot be a bound at both ends of a panel
    spanning three orders of magnitude -- it is about 35 parts per million of
    the largest cross-section observed and a quarter of the smallest. But the
    coverage floor rejects exactly the small months that make that argument,
    so post-floor one cross-section is admitted, and recalibrating a shared
    shape against a single observation is the failure the change was meant to
    prevent. `docs/DATA_QUALITY_DECISIONS.md` defers the number until at least
    three are admitted, and this class does not lift that deferral.

    What lands here is the ability to express the change when it is time:
    `relative_ppm` alongside `absolute`, with `absolute` acting as a floor
    under it, validated in `contract.py` for the same reason the `release_lag`
    schema is -- it is a shape both tracks build against, and a second copy of
    the rules is how one field came to be called `calendar` on one side and
    `unit` on the other. The restatement of these rules that used to sit in
    `test_the_declared_registry_is_well_formed` required `absolute`, which is
    what made an absolute-only bound the only expressible kind. Lifting the
    deferral is now a one-line edit to a declaration rather than a change to
    the contract, and that is the whole of what this buys.

    No test here asserts that any declared tolerance *is* relative, because
    none is, and a test asserting the absence would have to be deleted on the
    day the deferral lifts rather than passing through it.

    Mutation record, the human-side patch that introduced this class. Run in a
    copy under `$HOME` with `data/`, `.github/`, `metadata/`, `.gitignore`, the
    root Markdown and `docs/PROJECT_STATUS.md` present. `-B` with
    `PYTHONDONTWRITEBYTECODE=1`, unmutated control green before and after.

      * `resolve_identity_tolerance` returns `absolute` and ignores
        `relative_ppm`. Kills four:
        `test_the_resolved_bound_moves_with_the_scale` and
        `test_the_absolute_part_is_a_floor_and_not_a_ceiling` by assertion, and
        `test_data.PointInTimeDataContractTests`
        `::test_a_relative_tolerance_is_the_same_rule_at_every_scale` twice, at
        both scales, as `DataContractError` refusals rather than assertions --
        the whole point being that the bound collapses to a millionth of a
        billion and the identity then fails everywhere.

      * The same resolver with `min` for `max`. Kills those four and one more
        subtest of the same test, for the same reason at the other end.

      * `validate_identity_tolerance` stops requiring that a tolerance declare
        either part. Kills exactly one, its own test.

      * One expected to be boring, which was: the scale in
        `data._identity_verdict` taken from the left side alone instead of the
        larger side. It killed nothing, because every fixture in the suite had
        two sides of nearly equal magnitude and the choice was free.
        `test_the_scale_is_the_larger_side_and_not_the_left_one` was written in
        response and the mutation now kills it, and only it. A mutation that
        fires nothing is a finding about the tests.

    No mutation was run against a *declared* relative tolerance, because none
    is declared. The rules are exercised against fixtures here so that they
    are not vacuous today, and the day a declaration arrives is the day this
    record needs a fourth entry.
    """

    def _tolerance(self, **overrides):
        block = {"relative_ppm": 500, "absolute": 0.001, "unit": "USD billions"}
        block.update(overrides)
        return block

    def test_a_conforming_tolerance_has_no_problems(self):
        self.assertEqual(validate_identity_tolerance("src", "id", self._tolerance()), [])

    def test_an_absolute_only_tolerance_stays_legal(self):
        """Some identities are exact, and a tight absolute bound says so.

        Gross subscriptions less gross redemptions is net flow by definition,
        not by approximation. Forcing a relative bound onto it would be the
        schema having an opinion about the data rather than about the
        declaration.
        """

        self.assertEqual(
            validate_identity_tolerance(
                "src", "id", {"absolute": 1e-06, "unit": "USD billions"}
            ),
            [],
        )

    def test_a_tolerance_that_bounds_nothing_is_refused(self):
        problems = validate_identity_tolerance("src", "id", {"unit": "USD billions"})
        self.assertTrue(problems)
        self.assertIn("relative_ppm", " ".join(problems))

    def test_a_tolerance_must_carry_its_unit(self):
        for tolerance in ({"absolute": 0.5}, {"absolute": 0.5, "unit": "  "}):
            with self.subTest(tolerance=tolerance):
                problems = validate_identity_tolerance("src", "id", tolerance)
                self.assertTrue(problems)
                self.assertIn("unit", " ".join(problems))

    def test_unknown_keys_and_wrong_types_are_refused(self):
        cases = {
            "relative_pct": self._tolerance(relative_pct=0.05),
            "negative absolute": self._tolerance(absolute=-1.0),
            "zero relative": self._tolerance(relative_ppm=0),
            "boolean absolute": self._tolerance(absolute=True),
            "string relative": self._tolerance(relative_ppm="500"),
            "not an object": [500],
        }
        for label, tolerance in cases.items():
            with self.subTest(case=label):
                self.assertTrue(
                    validate_identity_tolerance("src", "id", tolerance),
                    msg=f"{label} was accepted",
                )

    def test_the_resolved_bound_moves_with_the_scale(self):
        """Longhand, not recomputed from the formula it is checking.

        A test that multiplies the same three numbers the implementation does
        agrees with it whatever either says. These four expectations are typed
        out, so the only way they pass is if the resolver returns them.
        """

        tolerance = self._tolerance()
        self.assertAlmostEqual(resolve_identity_tolerance(tolerance, 9000.0), 4.5)
        self.assertAlmostEqual(resolve_identity_tolerance(tolerance, 2000.0), 1.0)
        self.assertAlmostEqual(resolve_identity_tolerance(tolerance, 2.0), 0.001)
        self.assertAlmostEqual(resolve_identity_tolerance(tolerance, -9000.0), 4.5)

    def test_the_absolute_part_is_a_floor_and_not_a_ceiling(self):
        """At 2 USD billions the floor binds; at 9000 the relative part does.

        Which is the whole reason both are declared: parts per million of a
        two-billion cross-section is 1000 USD, and a rounding residual is
        larger than that without anything being wrong.
        """

        tolerance = self._tolerance()
        self.assertGreater(
            resolve_identity_tolerance(tolerance, 9000.0), tolerance["absolute"]
        )
        self.assertEqual(
            resolve_identity_tolerance(tolerance, 0.5), tolerance["absolute"]
        )

    def test_the_declared_registry_tolerances_conform(self):
        registry = json.loads(SOURCE_REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(validate_registry_identity_tolerances(registry), {})



if __name__ == "__main__":
    unittest.main()
