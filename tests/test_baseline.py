"""Tests for `repo_model.baseline`.

The purged rolling-origin benchmark, the models it scores, and the artifact it
publishes. The splitter itself is `tests/test_splits.py`; the knowledge-holdout
evaluator that shares this module's gap derivation is `tests/test_event_eval.py`.

The field-priced purge (8 September 2026)
-----------------------------------------

`test_two_features_on_one_source_price_differently` is this block's whole
claim and its only acceptance criterion. Before it, both evaluation paths
resolved a feature set to **source IDs** and priced the gap over those. A
source is too coarse a thing to price: `fred_macro_latest_vintage` carries
`IORB`, an administered rate that is never revised, beside H.4.1 weeklies that
are, under one source-level `release_lag` of basis `snapshot_retrieved_at`.
Priced by the source, every field of it was unpriceable -- and since
`spread_bps` is computed from `iorb`, so was the target. That is why nothing in
this repository had ever been measured on data it fetched.

Both paths now resolve through `contract.field_sources_for_features` and hand
`registry.max_release_lag_days` the `(source_id, field)` pairs, through one
function -- `baseline._derive_purge` -- which `event_eval` imports rather than
restates, as it already does for `_check_fitter_stayed_inside`.

**The real-registry purge.** The first figure in this project's life that did
not come from a fixture, quoted from the artifact rather than the console:

    backtest data/sample/daily_market.csv --minimum-history 10
      --registry metadata/sources.json --feature spread_bps
      --decision-time 16:30 --report <under $HOME>

  * `derived.purge_days`: **6**
  * `derived.fields`: `fred_macro_latest_vintage.IORB`, `nyfed_sofr.SOFR`
  * `derived.sources`: `fred_macro_latest_vintage`, `nyfed_sofr`
  * `folds.count`: **12**; first origin scored `2026-01-22` from a feature row
    of `2026-01-15`, last origin scored `2026-02-06` from `2026-01-30`
  * `metrics.mae_bps` 2.083333333333348, `metrics.interval_coverage` 0.5

The six days come from `nyfed_sofr.SOFR`, not from `IORB`, which prices at two:
the gap is a maximum and SOFR's `worst_case_calendar_days` is the larger. The
console summary and the artifact agree on every one of these; they are checked
against each other by
`tests/test_cli_eval.py::RealRegistryTests::test_the_backtest_runs_on_the_real_registry_over_declared_fields`.

**The panel is still the synthetic one.** Twenty-five hand-written rows. The
gap is now derived from the shipped registry; the numbers it produces are not
yet a measurement of anything. Two things surfaced by the published-benchmark
block are visible in the figures above and neither is this block's: the
interval is badly calibrated (coverage 0.5 against a declared 0.9) and
`contract.INTERVAL_PROBABILITY` is a binary-float artefact reading
`0.8999999999999999`. Nothing here was moved in either direction.

Mutation record, the field-priced purge
---------------------------------------

Run against a copy of the tree under `$HOME` -- never the mount -- carrying
`data/`, `metadata/`, `.github/` and the top-level documents, with
`__pycache__` cleared, stdlib only, under `-B` with `PYTHONDONTWRITEBYTECODE=1`.
Unmutated control first: green, zero `expectedFailure`. The
same control after each mutation was reverted.

  1. **The acceptance mutation.** `_derive_purge` passes `sources` to
     `max_release_lag_days` instead of `field_sources` -- the source-level
     fallback for every field, which is what both paths did before this block.
     Kills 3:

       * `test_two_features_on_one_source_price_differently` (this file) --
         errors on the priced half, before the refused half is reached:
         `spread_bps` no longer resolves, because its `IORB` is priced by
         `fred_macro_latest_vintage`'s snapshot basis again. Both feature sets
         refuse, the "opposite verdicts" the test is named for collapse into
         one verdict, and the test dies. **The criterion and the mutation do
         not come apart:** the test the brief names is the test the mutation
         kills, and it dies for the reason the mutation was planted.
       * `tests/test_event_eval.py::DerivedGapTests::test_the_real_registry_refuses_this_path_too_for_the_same_field`
         -- the event path's half of the same fact, killed the same way.
       * `tests/test_cli_eval.py::RealRegistryTests::test_the_backtest_runs_on_the_real_registry_over_declared_fields`
         -- exit 2 where 0 was expected. The command-level statement that the
         shipped registry now runs.

     Nothing else in the suite notices, which is correct: every other registry
     in the suite is a fixture that declares no fields, and on such a registry
     the two derivations agree by construction.

  2. **The two derivations drifting apart.** `evaluate_event_window` left on
     `contract.sources_for_features` and `max_release_lag_days` over source IDs
     while `rolling_persistence_backtest` moves to fields. Kills 1:
     `tests/test_event_eval.py::DerivedGapTests::test_the_real_registry_refuses_this_path_too_for_the_same_field`,
     on its second half -- the event path refuses a `spread_bps` the rolling
     path prices, against the same registry, in the same run.

     One kill is thin for the failure this block is one step away from, and it
     is thin for a structural reason worth stating: the two paths call one
     function, so the drift cannot be expressed without first duplicating the
     call, and the mutation had to write that duplicate before it could plant
     the divergence. The single test that catches it is the only one in the
     suite that asserts a *priced* result on the event path against the real
     registry; every other event-path test uses a fixture registry, where the
     two derivations agree.

  3. **An undeclared field silently priced at zero.** `_derive_purge` catches
     `RegistryContractError`, keeps only the pairs the registry declares a
     `field_release_lags` entry for, and prices those -- falling to `0` when
     none survive. The shape the brief forbids: the refusal softened into a
     smaller gap. Kills 5:

       * `test_two_features_on_one_source_price_differently` and
         `test_the_real_registry_still_refuses_a_field_with_no_revision_policy`
         (this file) -- `WRESBAL` and `WTREGEN` priced instead of refused.
       * `tests/test_cli_eval.py::RealRegistryTests::test_the_backtest_refuses_a_real_field_with_no_revision_policy`
         -- exit 0, and a report file published for a run whose gap was sized
         over a field nobody declared.
       * `tests/test_event_eval.py::DerivedGapTests::test_the_real_registry_refuses_this_path_too_for_the_same_field`.
       * `tests/test_event_eval.py::PurgeBoundaryTests::test_the_gap_is_derived_and_cannot_be_supplied`
         -- the one worth having, and the only kill here that is not about the
         real registry. It fails on a *fixture* registry, on the "a derived
         purge cannot be zero" invariant, which is the general statement this
         mutation violates and the reason the narrowing is safe.

  4. **The boring one: the fixture-registry numbers.** Not a mutation of the
     code but of the tree -- `git archive HEAD` (`8a18155`, before this block)
     against the working tree, both running `backtest` on
     `data/sample/daily_market.csv` at `--minimum-history 10` against a
     hand-written registry declaring six `record_date` days for
     `fred_macro_latest_vintage` and `nyfed_sofr` and **no**
     `field_release_lags`.

     Every number is bit-identical. `metrics` compares equal as a whole, and so
     do `folds`, `panel` and `declaration`: `mae_bps` 2.083333333333348,
     `interval_coverage` 0.5, `crps_bps` 1.8028333333333422, the pinball losses
     at all five declared levels, `block_length` 5, `seed` 2071980500,
     `purge_days` 6, twelve folds. The only difference anywhere in the artifact
     is the additive `derived.fields` key, and in the console summary the
     matching `fields` key. That is the whole intended effect of this block on
     a registry that declares no fields: the gap comes from somewhere else and
     arrives at the same value, and nothing downstream of it moves.

     The conformance suites still run once per implementer on both
     interfaces, counted rather than diffed: the same counts before and
     after this block. The absolute numbers that stood here were cut in
     block 9 -- `tests/test_contract.py` had grown well past the one
     recorded, so the figure read as a present-tense fact and was wrong.

No mutation was planted in the ARX, the threshold model, the bootstrap or the
quantile machinery; the runs say nothing about them.
"""

import contextlib
import hashlib
import importlib
import inspect
import json
import math
import subprocess
import sys
import tempfile
import textwrap
import unittest
from datetime import date, time, timedelta
from functools import partial
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

import repo_model
from repo_model import baseline, cli_eval, event_eval
from repo_model.baseline import (
    INTERVAL_PROBABILITY,
    BacktestReport,
    DegenerateRegimeError,
    ExceedanceCurves,
    FittedArx,
    FittedPersistence,
    FittedRollingResidualLaw,
    FittedThreshold,
    Forecast,
    MissingRegressorError,
    ProvenanceMismatchError,
    ScoredFold,
    SingularDesignError,
    UnobservedThresholdError,
    _dot,
    _feature_index,
    _least_squares,
    _quantile,
    arx_exceedance,
    backtest_document,
    calibration_from_document,
    climatology_exceedance,
    exceedance_backtest_document,
    fit,
    comparison_seed,
    fit_arx,
    fit_rolling_residual_law,
    fit_threshold,
    interval_calibration,
    paired_comparison_document,
    paired_model_comparison,
    rolling_exceedance_backtest,
    rolling_persistence_backtest,
    threshold_exceedance,
    twcrps_weights,
)
from repo_model.metrics import MetricError, brier_skill_score, crps_from_quantiles
from repo_model.contract import (
    QUANTILE_LEVELS,
    UndeclaredFeatureError,
    sources_for_features,
)
from repo_model.data import DailyObservation, load_daily_panel
from repo_model.registry import RegistryContractError
from repo_model.splits import LookAheadError, SplitError, rolling_origin

# The package walk `ForecastInterfaceCoverageTests` already discovers through,
# imported rather than written a second time: two walks would be two definitions
# of "every module of the package", and the one that drifted would be the one
# nobody was reading. `tests/test_contract.py` imports no test module, so this
# direction is acyclic, and a test module importing another is how
# `tests/test_event_eval.py` already reaches this one's fixtures.
from test_contract import _package_modules

SAMPLE_PANEL = Path(__file__).parents[1] / "data" / "sample" / "daily_market.csv"

#: The regressor set every ARX in this module is fitted on, named once. Two
#: columns that actually move on the sample panel; `quarter_end` is constant and
#: `mmf_assets` is empty throughout, and both are refused rather than fitted --
#: see `FittedArxTests.test_a_degenerate_regressor_set_is_refused_not_approximated`.
REGRESSORS = ("sofr_volume", "on_rrp")

#: The feature set a persistence backtest declares: the one column
#: `FittedPersistence.features_read` reports. Named once, because it is the
#: declaration the derived purge is computed from in most of this file.
FEATURES = ("spread_bps",)

#: What an ARX on `REGRESSORS` declares. `spread_bps` is in it because the ARX
#: reads its own autoregressive term, and a declaration that omitted it would be
#: refused by the check `_check_fitter_stayed_inside` performs -- which is the
#: check working, not a fixture bug.
ARX_FEATURES = FEATURES + REGRESSORS

#: Required by `max_release_lag_days` and undefaulted there, so stated here.
#: Any time works for `declared_registry`, whose `available_time` is midnight;
#: the value is pinned so a reader can see the gap does not depend on it.
DECISION_TIME = time(16, 0)

REAL_REGISTRY = Path(__file__).parents[1] / "metadata" / "sources.json"

#: The declaration files a published record must identify by digest. Named
#: beside `REAL_REGISTRY` because the record's claim about them is the same
#: claim -- the bytes this run read -- and neither is parsed to make it.
REAL_THRESHOLDS = Path(__file__).parents[1] / "metadata" / "stress_thresholds.json"


def declared_registry(purge, features=FEATURES):
    """A registry declaring exactly `purge` days for every source `features` uses.

    A **fixture**, not a copy of `metadata/sources.json`, and it does not claim
    to describe any real source. Its whole content is "these sources cost this
    many days", which is what the model layer needs and all it may know: the
    conversion from structured provenance to a scalar belongs to Track A and is
    tested against the real registry in `tests/test_registry_interface.py`.

    It exists because the gap is no longer typed at the call site. Tests about
    something *other* than the derivation -- ordering, interval width, whether
    the default fitter is persistence -- still need a known gap, and the honest
    way to pin one is now to declare a registry that produces it rather than to
    pass an integer the function no longer accepts.

    `record_date` with `available_time` at midnight makes the contribution
    exactly `days`, with no dependence on `DECISION_TIME`: the arithmetic
    `max_release_lag_days` performs is Track A's to test, and a fixture that
    leaned on it would be this file restating it.

    `purge` must be at least 1. `max_release_lag_days` refuses to return zero --
    "selected sources must produce a nonzero purge" -- so an unpurged backtest
    is no longer expressible through the declared path at all. That is the
    intended consequence of deriving the gap and it is why the reproduction
    test below pins the purge block's six-day numbers rather than its zero-day
    ones.
    """

    if purge < 1:
        raise ValueError(
            "max_release_lag_days cannot produce a gap below 1; an unpurged "
            "backtest is not expressible once the gap is derived"
        )
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


def at_gap(rows, *, purge, features=FEATURES, **kwargs):
    """`rolling_persistence_backtest` at a pinned gap, for tests about other things.

    The gap reaches the run the only way it now can: through a declared feature
    set and a registry that prices it. Tests that are *about* the derivation
    call `rolling_persistence_backtest` directly, so that what they exercise is
    visible in the test rather than hidden behind this.
    """

    return rolling_persistence_backtest(
        rows,
        features=features,
        registry=declared_registry(purge, features),
        decision_time=DECISION_TIME,
        **kwargs,
    )


def regressor_frame(count=40, seed=20260909, unobserved=()):
    """A panel with distinct spreads and two moving exogenous columns.

    Generated rather than stored, for the reason `distinct_residual_frame` in
    `test_contract.py` gives: the property under test is a property of the
    numbers. `unobserved` names row indices where `on_rrp` is carried as `None`
    -- present in the mapping, with no observation -- which is the case
    AGENT_CONTRACT.md test 5 says must stay distinguishable from an absent key.

    `on_rrp` is centred near 100 and `sofr_volume` near 2200 on purpose: a
    fitted imputation mean far from zero is what lets
    `test_an_unobserved_regressor_is_never_coerced_to_zero` tell imputation and
    coercion apart at all.
    """

    rows = []
    state = seed
    for index in range(count):
        state = (1103515245 * state + 12345) % (2 ** 31)
        on_rrp = None if index in unobserved else 90.0 + (state % 211) / 10.0
        rows.append(
            DailyObservation(
                date(2026, 1, 1) + timedelta(days=index),
                {
                    "sofr": 4.30 + 0.0001 * (state % 9973),
                    "iorb": 4.30,
                    "sofr_volume": 2100.0 + (state % 1301) / 3.0,
                    "on_rrp": on_rrp,
                },
            )
        )
    return rows


def design_and_targets(rows, regressors, imputations):
    """The one-step-ahead design `fit_arx` builds, rebuilt here independently.

    Written out longhand so the tests below compare the model against the
    definition rather than against a helper the model also calls.
    """

    design = []
    targets = []
    for index in range(1, len(rows)):
        origin = rows[index - 1]
        row = [1.0, origin.spread_bps]
        for name in regressors:
            raw = origin.values[name]
            row.append(imputations[name] if raw is None else float(raw))
        design.append(row)
        targets.append(rows[index].spread_bps)
    return design, targets


def window_means(rows, regressors):
    """The training-window mean of each regressor's observed values.

    Over the *origin* rows -- everything but the last, because the last row of a
    training frame is a target and never a feature. That distinction is the
    whole of contract test 3 here: a mean taken over one row more is a mean
    taken over a row the transform was not entitled to see.
    """

    means = {}
    for name in regressors:
        seen = [
            float(row.values[name])
            for row in rows[:-1]
            if row.values[name] is not None
        ]
        means[name] = sum(seen) / len(seen)
    return means


class BaselineTests(unittest.TestCase):
    def test_rolling_backtest_is_time_ordered(self):
        start = date(2026, 1, 1)
        rows = [
            DailyObservation(
                start + timedelta(days=index),
                {"sofr": 4.30 + index / 100.0, "iorb": 4.30},
            )
            for index in range(30)
        ]
        report = at_gap(rows, purge=1, minimum_history=10)
        # One origin fewer than the unpurged walk, and the error doubles: the
        # spread rises 1bp a day and the forecaster is now two days back rather
        # than one. Both numbers are consequences of the gap, not of the frame.
        self.assertEqual(len(report.forecasts), 19)
        self.assertAlmostEqual(report.mae_bps, 2.0)
        self.assertTrue(0.0 <= report.interval_coverage <= 1.0)

    def test_requires_history(self):
        rows = [
            DailyObservation(date(2026, 1, 1), {"sofr": 4.31, "iorb": 4.30}),
            DailyObservation(date(2026, 1, 2), {"sofr": 4.32, "iorb": 4.30}),
        ]
        with self.assertRaisesRegex(ValueError, "not enough"):
            at_gap(rows, purge=1, minimum_history=2)


class FittedPersistenceTests(unittest.TestCase):
    """The backtest is a consumer of the fitted interface, not a parallel copy.

    `rolling_persistence_backtest` used to derive its own residual quantiles
    inline, from its own restated `interval_probability`. Both numbers now have
    exactly one origin -- the fitted model and `contract.QUANTILE_LEVELS` -- and
    these tests exist to keep it that way. A second derivation reintroduced here
    would agree with the first on the day it was written and be free to drift
    afterwards, which is how the repository ended up with an interval
    probability that nobody had reconciled against the quantile grid.
    """

    MINIMUM_HISTORY = 10

    def panel(self, count=30):
        return [
            DailyObservation(
                date(2026, 1, 1) + timedelta(days=index),
                {"sofr": 4.30 + index / 100.0, "iorb": 4.30},
            )
            for index in range(count)
        ]

    def test_the_backtest_reports_the_fitted_model_and_does_not_re_derive_quantiles(self):
        rows = self.panel()
        report = at_gap(
            rows, purge=1, minimum_history=self.MINIMUM_HISTORY
        )

        # The run reports the model it finished on, and that model can say what
        # it was fitted at. A report that cannot name its own cutoff is the
        # thing "every fitted object carries the cutoff" exists to prevent.
        self.assertIsInstance(report.model, FittedPersistence)
        # The last fold's training end, enumerated independently. Under a gap
        # this is no longer `rows[-2]`, and a literal index here would be this
        # test restating the splitter's arithmetic instead of checking against
        # it.
        last_train, _ = list(
            rolling_origin([row.date for row in rows], self.MINIMUM_HISTORY, 1, 1)
        )[-1]
        self.assertEqual(report.model.cutoff, rows[last_train[-1]].date)

        # Every reported interval is the fitted model's own quantile vector at
        # the outermost declared levels -- refit independently here, so this
        # compares the backtest against the interface rather than against
        # itself.
        for position, forecast in enumerate(report.forecasts):
            index = self.MINIMUM_HISTORY + position
            model = fit(rows[:index], minimum_history=self.MINIMUM_HISTORY)
            quantiles = model.predict(rows[index - 1])

            self.assertEqual(model.cutoff, rows[index - 1].date)
            self.assertEqual(forecast.predicted_bps, rows[index - 1].spread_bps)
            self.assertEqual(forecast.lower_bps, quantiles[0])
            self.assertEqual(forecast.upper_bps, quantiles[-1])
            self.assertEqual(len(quantiles), len(QUANTILE_LEVELS))

    def test_the_interval_probability_is_read_from_the_declared_levels(self):
        rows = self.panel()

        # The interval is the span of the outermost declared pair. It is derived
        # from the grid, not restated beside it.
        self.assertEqual(
            INTERVAL_PROBABILITY, QUANTILE_LEVELS[-1] - QUANTILE_LEVELS[0]
        )
        self.assertAlmostEqual(INTERVAL_PROBABILITY, 0.90, places=12)

        # The default reads the declaration, and stating the same interval
        # explicitly changes nothing.
        default = at_gap(
            rows, purge=1, minimum_history=self.MINIMUM_HISTORY
        )
        restated = at_gap(
            rows,
            purge=1,
            minimum_history=self.MINIMUM_HISTORY,
            interval_probability=0.90,
        )
        self.assertEqual(list(default.forecasts), list(restated.forecasts))

        # An interval the declared levels do not produce is refused rather than
        # honoured. Honouring it would put the reported coverage and the
        # reported interval out of step, silently.
        with self.assertRaisesRegex(ValueError, "declared levels"):
            at_gap(
                rows,
                purge=1,
                minimum_history=self.MINIMUM_HISTORY,
                interval_probability=0.50,
            )


#: A spread path in basis points whose one-step residuals are **large early and
#: small late**, so that the trailing window and the largest residuals are
#: disjoint sets. Declared as the residual sequence and accumulated, because the
#: residuals are the thing under test and a path written directly would leave a
#: reader differencing it by hand to see the property.
#:
#: Twenty-one residuals of 25..45 bp, then eight of alternating sign and single
#: digits. Not monotone in time, which the acceptance criterion requires: a
#: monotone sequence makes "the last eight" and "the eight largest" the same
#: eight, and the mutation this block records would survive.
NON_MONOTONE_RESIDUALS_BPS = (
    tuple(float(step) for step in range(25, 46))
    + (1.0, -2.0, 3.0, -1.0, 2.0, -3.0, 4.0, -4.0)
)

#: How many trailing residuals the law is read from, in this file. Small enough
#: that the windowed law is entirely inside the small-residual tail above and
#: the full-sample law is not.
RESIDUAL_WINDOW = 8


def non_monotone_frame():
    """Rows whose one-step residuals are `NON_MONOTONE_RESIDUALS_BPS`, in order.

    The spread is carried the way every other fixture here carries it -- as
    `sofr` against a constant `iorb`, so `DailyObservation.spread_bps` computes
    it rather than the fixture asserting it -- and the residual sequence is
    accumulated into the path. The oracle below differences `spread_bps` back
    out, so the two meet on the same floats and the comparison can be exact.
    """

    spread = 0.0
    rows = [
        DailyObservation(
            date(2026, 1, 1), {"sofr": 4.30 + spread / 10000.0, "iorb": 4.30}
        )
    ]
    for step, residual in enumerate(NON_MONOTONE_RESIDUALS_BPS, start=1):
        spread += residual
        rows.append(
            DailyObservation(
                date(2026, 1, 1) + timedelta(days=step),
                {"sofr": 4.30 + spread / 10000.0, "iorb": 4.30},
            )
        )
    return rows


def oracle_trailing_residuals(rows, window):
    """The last `window` one-step residuals of `rows`, in time order.

    **The oracle, and it shares no code path with `baseline`.** It differences
    consecutive `spread_bps` in this file and slices the tail of the result. That
    is the whole of what `fit_rolling_residual_law` is supposed to do, written
    out independently, which is the only way a test of it is evidence: reusing
    `FittedPersistence.residuals` and slicing *that* is the mutation this
    block's record names, and an oracle built the same way would agree with a
    wrong implementation.

    Returned in time order, unsorted. The fitted object sorts what it is handed
    -- every model in `baseline` does, because `_quantile` reads order
    statistics -- so callers compare against `sorted(...)` of this. The ordering
    is kept here so that a reader can see the selection was made in time.
    """

    residuals = [
        rows[index].spread_bps - rows[index - 1].spread_bps
        for index in range(1, len(rows))
    ]
    return tuple(residuals[-window:])


class RollingResidualLawTests(unittest.TestCase):
    """`fit_rolling_residual_law`: persistence's centre, a trailing-window law.

    `PLAN.md` Phase 2 lists "rolling mean/quantiles" among four benchmarks and
    no rolling anything existed. This is the quantile half, built against a
    measured finding rather than a list: persistence wins on accuracy and
    **under-covers its nominal 90% interval**, and the interval is the residual
    law, so the law is what a challenger changes. Nothing here changes the point
    forecast; a challenger that moved both would leave the coverage finding
    unattributable to either change.

    `window` is required and undefaulted. Not a style preference: a default
    would be a decision nobody made about how much history the published
    interval is a statement about, and it would be the decision most likely to
    be made by whoever typed the command last. Nothing in this model chooses it
    from data either -- a window selected by scoring candidate lengths is a
    hyperparameter fitted outside `fit`, which the contract forbids in those
    words, and neither track can see the frozen panel to pick one honestly.

    Acceptance criterion and mutation record, the trailing-window law
    ------------------------------------------------------------------

    Acceptance criterion, which is also the mutation target:
    `test_the_residual_law_is_the_trailing_window_ending_at_the_cutoff`.

    Run in a disposable copy of the tree under `$HOME`, never in the mount,
    carrying `data/`, `.github/`, `.claude/`, `metadata/`, `.gitignore`, the root
    Markdown and `docs/PROJECT_STATUS.md`, with `PYTHONDONTWRITEBYTECODE=1`
    under `python3 -B`. Unmutated control green before and after, zero
    `expectedFailure`. Python 3.9.6.

      1. **The acceptance mutation -- the sorted vector, tailed.**
         `fit_rolling_residual_law` builds a `FittedPersistence` over the whole
         frame and hands `FittedRollingResidualLaw` the tail of *its*
         `residuals`, which is the sorted vector. The result is the `window`
         largest residuals: a set of real residuals, of the right length, biased
         upward, and producing a perfectly plausible interval that is not a
         trailing window of anything.

         Kills exactly 1, `AssertionError`:
         `test_the_residual_law_is_the_trailing_window_ending_at_the_cutoff`.
         On the fixture above the two sets are disjoint, so the comparison
         against the oracle fails on the first level it reports.
         `test_the_fixture_would_catch_a_law_read_from_the_largest_residuals`
         passes under the mutation -- it is a statement about the fixture, not
         about the code -- which is what makes it a fixture guard rather than a
         second acceptance test. **The criterion and the mutation do not come
         apart:** the test the brief names is the test that dies, and it dies
         because the selection was made after the sort.

         Nothing in the conformance suite notices, and that is correct rather
         than a gap: the `window` largest residuals are still a residual sample,
         still ascending, still the one law both outputs read, so every
         interface assertion holds over them. An interface cannot see which rows
         a law was read from, which is why this criterion is here and not in
         `tests/test_contract.py`.

      2. **The window silently truncated to the frame.** `fit_rolling_residual_law`
         returns `ordered[-requested:]` with the length refusal removed, so a
         window longer than the history yields the whole sample -- this model
         collapsed into persistence while still reporting itself as a
         challenger, and still carrying the `window` it did not honour.
         Kills 1, `AssertionError`:
         `test_a_window_longer_than_the_history_is_refused_not_truncated`.

      3. **`window` given a default of 20.** The signature alone, nothing else
         touched. Kills 1, `TypeError` absent where one was expected:
         `test_the_window_is_required_and_undefaulted`. Worth recording because
         it is the mutation a reader expects to be caught by more than one test
         and is not: every other test in this file passes a window explicitly,
         so a default changes nothing for any of them. A required argument is
         only required where something demands the refusal.

    **One existing mutation re-run**, because this block edited `_select_fitter`
    and `_FitterChoice`, which the selector's own record names: "the selector
    resolves every name to the default persistence fitter". It still kills, and
    it now kills 3 rather than the 1 its record states --
    `ContinuousModelSelectorTests.test_the_record_names_the_model_that_produced_the_forecasts`,
    the new `test_the_windowed_model_is_reachable_by_name_and_the_record_says_so`
    beside it, and
    `PairedComparisonCommandTests.test_the_record_carries_the_comparison_the_declaration_describes`,
    which did not exist when that record was written. The guard was strengthened
    rather than blunted; the count in the other record is stale and is that
    record's to correct, not this one's.
    """

    MINIMUM_HISTORY = 10

    def setUp(self):
        self.rows = non_monotone_frame()

    def test_the_residual_law_is_the_trailing_window_ending_at_the_cutoff(self):
        """The acceptance criterion: the law is the last `window` residuals.

        Against `oracle_trailing_residuals`, which differences `spread_bps` in
        this file and takes the tail. The fitted vector is ascending -- the
        interface declares that and both outputs depend on it -- so the oracle's
        time-ordered tail is sorted for the comparison. Sorting *after*
        selecting is the whole content of this model, and sorting before it is
        mutation 1.
        """

        fitted = fit_rolling_residual_law(
            self.rows, RESIDUAL_WINDOW, minimum_history=self.MINIMUM_HISTORY
        )

        expected = oracle_trailing_residuals(self.rows, RESIDUAL_WINDOW)
        self.assertEqual(len(expected), RESIDUAL_WINDOW)
        self.assertEqual(fitted.residuals, tuple(sorted(expected)))
        self.assertEqual(fitted.window, RESIDUAL_WINDOW)
        self.assertEqual(fitted.cutoff, self.rows[-1].date)

        # And on a frame that ends before a declared cutoff, the law is that
        # frame's trailing window: there are no rows between its end and the
        # cutoff, so "ending at the cutoff" can mean nothing else. The cutoff is
        # still the declared one, because what the model was allowed to see and
        # what it happened to read are different facts.
        shorter = self.rows[:-4]
        earlier = fit_rolling_residual_law(
            shorter,
            RESIDUAL_WINDOW,
            cutoff=self.rows[-1].date,
            minimum_history=self.MINIMUM_HISTORY,
        )
        self.assertEqual(
            earlier.residuals,
            tuple(sorted(oracle_trailing_residuals(shorter, RESIDUAL_WINDOW))),
        )
        self.assertEqual(earlier.cutoff, self.rows[-1].date)
        self.assertNotEqual(earlier.residuals, fitted.residuals)

    def test_the_fixture_would_catch_a_law_read_from_the_largest_residuals(self):
        """Guards the criterion above: the two candidate laws must differ here.

        On a frame whose residuals rise monotonically the trailing window *is*
        the largest residuals, and the acceptance test passes over a
        sorted-then-tailed implementation while asserting an equality that looks
        decisive. This asserts the fixture has the property that makes the
        comparison evidence -- the same role
        `test_the_frame_this_class_relies_on_has_no_tied_residuals` plays for the
        exceedance round trip in `tests/test_contract.py`.
        """

        every = [
            self.rows[index].spread_bps - self.rows[index - 1].spread_bps
            for index in range(1, len(self.rows))
        ]
        trailing = oracle_trailing_residuals(self.rows, RESIDUAL_WINDOW)
        largest = tuple(sorted(every)[-RESIDUAL_WINDOW:])

        self.assertGreater(len(every), RESIDUAL_WINDOW)
        self.assertNotEqual(tuple(sorted(trailing)), largest)
        # Disjoint, not merely unequal: every residual the windowed law reads is
        # outside the eight largest, so the mutation cannot pass by overlapping.
        self.assertEqual(set(trailing) & set(largest), set())
        # And not monotone in time, which is what the criterion names.
        self.assertNotEqual(every, sorted(every))

    def test_the_window_is_required_and_undefaulted(self):
        """No default, for the reason `--model` has none: nobody made the choice.

        The refusal is `TypeError` from the call itself rather than a validation
        error inside the body, because the argument is positional and required in
        the signature. Checked by calling rather than by reading
        `inspect.signature`, so that a default added anywhere in the chain fails
        here -- a signature assertion passes over a wrapper that supplies one.
        """

        with self.assertRaises(TypeError):
            fit_rolling_residual_law(
                self.rows, minimum_history=self.MINIMUM_HISTORY
            )

    def test_a_window_longer_than_the_history_is_refused_not_truncated(self):
        """A window the frame cannot fill is an error, not the full sample.

        Truncating is the dangerous answer: the law becomes persistence's,
        identical to the benchmark this model is a challenger to, while the
        fitted object still reports the window it did not use and the record
        still carries the challenger's name. Both sides of a published
        comparison would then be persistence, and the difference would be zero
        for a reason no field of the record discloses.
        """

        residual_count = len(self.rows) - 1

        with self.assertRaisesRegex(ValueError, "exceeds"):
            fit_rolling_residual_law(
                self.rows, residual_count + 1, minimum_history=self.MINIMUM_HISTORY
            )

        # The largest window the frame *can* fill is the full sample, and that
        # is allowed: it is persistence's law, honestly reached, and refusing it
        # would make the boundary a guess rather than the count of residuals.
        whole = fit_rolling_residual_law(
            self.rows, residual_count, minimum_history=self.MINIMUM_HISTORY
        )
        persistence = fit(self.rows, minimum_history=self.MINIMUM_HISTORY)
        self.assertEqual(whole.residuals, persistence.residuals)

    def test_a_one_residual_law_is_refused(self):
        """Below two residuals every declared level reports the same number.

        `_quantile` over a single value is constant in its probability, so
        `predict` would return five copies of one number and the reported
        interval would have width zero -- a coverage figure of 0.0 or 1.0 that
        is an artefact of the window and reads as a finding about the model.
        """

        with self.assertRaisesRegex(ValueError, "at least 2"):
            fit_rolling_residual_law(
                self.rows, 1, minimum_history=self.MINIMUM_HISTORY
            )

    def test_the_windowed_model_is_not_a_persistence_model(self):
        """Distinct classes, not a subclass, and the reason is load-bearing.

        Three tests in this file assert `isinstance(report.model,
        FittedPersistence)` to pin that the default fitter is the benchmark
        rather than a challenger. A subclass of `FittedPersistence` satisfies
        all three while being a different model, so the blunting would land on
        exactly the assertions that keep a challenger from being published under
        the baseline's name. This states the separation so that introducing the
        inheritance fails a test instead of quietly weakening three.
        """

        fitted = fit_rolling_residual_law(
            self.rows, RESIDUAL_WINDOW, minimum_history=self.MINIMUM_HISTORY
        )

        self.assertIsInstance(fitted, FittedRollingResidualLaw)
        self.assertNotIsInstance(fitted, FittedPersistence)
        self.assertFalse(issubclass(FittedRollingResidualLaw, FittedPersistence))
        # It reads what persistence reads, so it is purged over the same
        # sources: the window narrows which rows the law came from, never which
        # columns the model touches.
        self.assertEqual(
            fitted.features_read,
            fit(self.rows, minimum_history=self.MINIMUM_HISTORY).features_read,
        )
        # And the centre is persistence's, unchanged.
        self.assertEqual(
            fitted.point_forecast(self.rows[-1]), self.rows[-1].spread_bps
        )

    def test_the_backtest_runs_it_and_reports_a_windowed_model(self):
        """It is a `ModelFitter`, so the rolling backtest can score it.

        Through a `functools.partial` over `window`, which is the shape
        `baseline.ModelFitter`'s docstring names and the shape
        `cli_eval.FITTER_FACTORIES` builds. The assertion is that the run
        finishes, reports a windowed model, and that the model's law is the
        window's -- not that its numbers beat persistence's, which is scored on
        the frozen panel and is not this block's.
        """

        report = at_gap(
            self.rows,
            purge=1,
            minimum_history=self.MINIMUM_HISTORY,
            fit_model=partial(fit_rolling_residual_law, window=RESIDUAL_WINDOW),
        )

        self.assertIsInstance(report.model, FittedRollingResidualLaw)
        self.assertEqual(report.model.window, RESIDUAL_WINDOW)
        self.assertEqual(len(report.model.residuals), RESIDUAL_WINDOW)
        self.assertGreater(len(report.forecasts), 0)


class FittedArxTests(unittest.TestCase):
    """The second implementer, and the four things only a second one can prove.

    `FittedPersistence` reads exactly one field of a feature row and fits
    nothing but a residual vector. While it was the only model, "the forecast
    interface" and "what FittedPersistence does" were the same sentence, and
    four of its properties were untested because nothing could distinguish them
    from the interface: that a model may read more of `values`; that a declared
    regressor set is fitted state; that a fitted transform is confined to `fit`;
    and that an unobserved value is neither refused nor zeroed. Each test below
    is one of those.
    """

    MINIMUM_HISTORY = 20

    def setUp(self):
        self.rows = regressor_frame()
        self.train = self.rows[:-1]
        self.feature_row = self.rows[-2]
        self.model = fit_arx(
            self.train, REGRESSORS, minimum_history=self.MINIMUM_HISTORY
        )

    def test_the_fitted_model_carries_the_regressors_it_was_fitted_on(self):
        """A model that cannot say what it read cannot be audited.

        The names are ordered and they line up with the coefficients, so a
        reader can say which number multiplies which column. Persistence never
        had to answer this -- it reads `spread_bps` and nothing else -- and the
        moment there are two models it is the question that decides whether a
        comparison between them is a comparison at all: two ARXs scored on
        quietly different regressor sets are two different models wearing one
        name.
        """

        self.assertEqual(self.model.regressors, REGRESSORS)
        self.assertEqual(
            self.model.design_names, ("intercept", "spread_bps") + REGRESSORS
        )
        self.assertEqual(len(self.model.coefficients), len(self.model.design_names))

        # It is the caller's declaration that is carried, not a house set: a
        # different declaration produces a differently shaped fitted object.
        one = fit_arx(self.train, ("on_rrp",), minimum_history=self.MINIMUM_HISTORY)
        self.assertEqual(one.regressors, ("on_rrp",))
        self.assertEqual(len(one.coefficients), 3)
        self.assertNotEqual(one.coefficients, self.model.coefficients)

    def test_the_fitting_call_declares_no_default_regressor_set(self):
        """`regressors` is required, for the reason `purge` is required.

        `rolling_origin` refuses a default `purge` and `max_release_lag_days`
        refuses a default `decision_time`, both because the default would be a
        silent assumption presented as a setting. Nothing in this repository
        declares which columns a model may rely on -- `REQUIRED_FIELDS`
        guarantees three, and every other column is `Optional[float]` and may be
        absent from the mapping entirely -- so a default here would be this
        module inventing the answer to a contract question. Checked on the
        signature, because the way this regresses is somebody adding
        `regressors=SOMETHING` for convenience.
        """

        parameter = inspect.signature(fit_arx).parameters["regressors"]
        self.assertIs(
            parameter.default,
            inspect.Parameter.empty,
            msg=(
                "fit_arx grew a default regressor set; nothing in this "
                "repository declares which columns a model may rely on, so the "
                "default would be an undeclared feature-set decision made here"
            ),
        )
        with self.assertRaises(TypeError):
            fit_arx(self.train, minimum_history=self.MINIMUM_HISTORY)
        with self.assertRaisesRegex(ValueError, "no regressors declared"):
            fit_arx(self.train, (), minimum_history=self.MINIMUM_HISTORY)

    def test_a_feature_row_missing_a_declared_regressor_is_refused(self):
        """An absent column is refused; it is not read as an unobserved value.

        `values` is a `Mapping[str, Optional[float]]`. A missing regressor
        arrives as a `KeyError` and a present-but-unobserved one arrives as
        `None`, and AGENT_CONTRACT.md test 5 requires the two stay
        distinguishable "at every stage". The boundary is where that is cheapest
        to enforce and hardest to notice missing: a model that quietly imputed
        an absent column would forecast from a number the row never contained,
        and would report it beside columns the row did contain.
        """

        stripped = DailyObservation(
            self.feature_row.date,
            {"sofr": self.feature_row.values["sofr"], "iorb": 4.30},
        )
        with self.assertRaises(MissingRegressorError) as caught:
            self.model.predict(stripped)
        self.assertIn("sofr_volume", str(caught.exception))
        with self.assertRaises(MissingRegressorError):
            self.model.predict_stress(stripped)
        with self.assertRaises(MissingRegressorError):
            self.model.point_forecast(stripped)

        # And it is refused rather than approximated: the fitted imputation
        # exists and is deliberately not used here.
        self.assertIn("sofr_volume", self.model.imputations)

        # The same refusal at fit time, on a training row rather than a feature
        # row -- a frame the model cannot read is not a frame it may fit on.
        broken = list(self.train)
        broken[3] = DailyObservation(broken[3].date, {"sofr": 4.31, "iorb": 4.30})
        with self.assertRaises(MissingRegressorError):
            fit_arx(broken, REGRESSORS, minimum_history=self.MINIMUM_HISTORY)

    def test_an_unobserved_regressor_is_never_coerced_to_zero(self):
        """`None` becomes the fitted imputation, and `0.0` stays `0.0`.

        The coercion AGENT_CONTRACT.md test 5 prohibits has an obvious form at
        the loader and a nearly invisible one here: a `None` written into a
        design matrix as `0.0` is arithmetically indistinguishable from a real
        observation of zero, and no downstream check can recover the difference.
        So the two are compared directly -- a row carrying `None` and a row
        carrying `0.0` must not produce the same forecast, and the `None` row
        must produce exactly the forecast the fitted mean produces.
        """

        mean = self.model.imputations["on_rrp"]
        self.assertGreater(
            mean,
            1.0,
            msg="fixture must fit a mean far from zero or this test cannot bite",
        )

        base = dict(self.feature_row.values)
        unobserved = DailyObservation(self.feature_row.date, {**base, "on_rrp": None})
        zeroed = DailyObservation(self.feature_row.date, {**base, "on_rrp": 0.0})
        imputed = DailyObservation(self.feature_row.date, {**base, "on_rrp": mean})

        self.assertEqual(
            self.model.design_row(unobserved), self.model.design_row(imputed)
        )
        self.assertNotEqual(
            self.model.design_row(unobserved), self.model.design_row(zeroed)
        )
        self.assertEqual(self.model.predict(unobserved), self.model.predict(imputed))
        self.assertNotEqual(self.model.predict(unobserved), self.model.predict(zeroed))
        self.assertNotEqual(
            self.model.predict_stress(unobserved), self.model.predict_stress(zeroed)
        )

        # A real zero survives as one rather than being read as absent: the
        # other half of test 5, on the same boundary.
        self.assertEqual(self.model.design_row(zeroed)[-1], 0.0)

        # And the same on the fit side: a training frame with an unobserved cell
        # fits, and fits to the mean of what was observed rather than to a
        # sample with a zero in it.
        gapped = regressor_frame(unobserved=(4, 11))
        model = fit_arx(gapped, REGRESSORS, minimum_history=self.MINIMUM_HISTORY)
        self.assertAlmostEqual(
            model.imputations["on_rrp"],
            window_means(gapped, REGRESSORS)["on_rrp"],
            places=12,
        )
        self.assertGreater(model.imputations["on_rrp"], 1.0)

    def test_the_imputation_is_fitted_state_and_cannot_be_retuned_after_the_fit(self):
        """"Any transform with learned parameters is fitted inside `fit`."

        Carried as a read-only mapping, so a caller cannot move a fitted
        parameter after the coefficients that depend on it are fixed. That would
        leave the reported coefficients and the transform that produced them out
        of step with nothing in a diff to show for it.
        """

        self.assertEqual(set(self.model.imputations), set(REGRESSORS))
        with self.assertRaises(TypeError):
            self.model.imputations["on_rrp"] = 0.0

    def test_the_residual_law_excludes_residuals_the_coefficients_were_fitted_to(self):
        """The reported law is leave-one-out, and demonstrably not in-sample.

        An ARX picks its coefficients to make its in-sample residuals small, so
        quantiles read off them describe the fit's interpolation of its own
        training rows rather than the width of a forecast. Reporting interval
        coverage from that law would make the model look better calibrated the
        more regressors it declared.

        Two assertions, and the second is the one that would fail under the
        other choice in section 2 of this block: every reported residual is
        reproduced by an independent refit that excluded exactly the row it
        scores, and the reported law is *not* the in-sample law.
        """

        rows = self.train
        imputations = window_means(rows, REGRESSORS)
        design, targets = design_and_targets(rows, REGRESSORS, imputations)

        expected = []
        for index in range(len(design)):
            kept_design = design[:index] + design[index + 1 :]
            kept_targets = targets[:index] + targets[index + 1 :]
            coefficients = _least_squares(kept_design, kept_targets)
            expected.append(targets[index] - _dot(coefficients, design[index]))

        reported = list(self.model.residuals)
        self.assertEqual(len(reported), len(expected))
        for left, right in zip(reported, sorted(expected)):
            self.assertAlmostEqual(left, right, places=9)

        in_sample = sorted(
            target - _dot(self.model.coefficients, row)
            for row, target in zip(design, targets)
        )
        if all(abs(a - b) <= 1e-9 for a, b in zip(reported, in_sample)):
            self.fail(
                "the reported residual law is the in-sample law; every residual "
                "in it was minimised by the coefficients that produced it"
            )

    def test_the_reported_interval_is_wider_than_the_in_sample_law_would_give(self):
        """The direction of the bias, asserted rather than asserted about.

        In-sample residuals are too small by construction, so an interval read
        off them is too narrow. This is the quantitative form of the test above:
        it fails if the model ever switches to the in-sample law, and it states
        which way the error would go if it did.
        """

        imputations = window_means(self.train, REGRESSORS)
        design, targets = design_and_targets(self.train, REGRESSORS, imputations)
        in_sample = [
            target - _dot(self.model.coefficients, row)
            for row, target in zip(design, targets)
        ]
        lower, upper = QUANTILE_LEVELS[0], QUANTILE_LEVELS[-1]

        residuals = list(self.model.residuals)
        reported_width = _quantile(residuals, upper) - _quantile(residuals, lower)
        in_sample_width = _quantile(in_sample, upper) - _quantile(in_sample, lower)
        self.assertGreater(
            reported_width,
            in_sample_width,
            msg=(
                "the leave-one-out interval is no wider than the in-sample one; "
                "either the law is in-sample after all, or this fixture cannot "
                "show the narrowing the choice exists to avoid"
            ),
        )

    def test_a_degenerate_regressor_set_is_refused_not_approximated(self):
        """No unique solution means no coefficient, not an arbitrary one.

        Both refusals are live on the checked-in sample panel, which is why they
        are tested against it rather than against a constructed case:
        `quarter_end` is constant throughout and so is collinear with the
        intercept, and `mmf_assets` is one of three columns that are empty in
        every row, so no imputation can be fitted from it. Filling either with a
        number would be inventing one.
        """

        rows = load_daily_panel(SAMPLE_PANEL)
        with self.assertRaises(SingularDesignError):
            fit_arx(rows, ("quarter_end",), minimum_history=10)
        with self.assertRaisesRegex(ValueError, "unobserved on every row"):
            fit_arx(rows, ("mmf_assets",), minimum_history=10)
        with self.assertRaisesRegex(ValueError, "more than once"):
            fit_arx(rows, ("on_rrp", "on_rrp"), minimum_history=10)


class RollingBacktestTests(unittest.TestCase):
    """The backtest scores the interface, not persistence.

    Last block made `rolling_persistence_backtest` a consumer of the fitted
    interface rather than an inline computation. It still hard-coded `fit`, so
    it was a consumer of *persistence*. The fitting call is now an argument, and
    these two tests are the pair that keeps that real: one that the argument is
    obeyed, one that the default is unchanged.
    """

    MINIMUM_HISTORY = 10

    def sample(self):
        return load_daily_panel(SAMPLE_PANEL)

    def test_the_backtest_scores_whichever_model_it_is_given(self):
        """Given an ARX fitter, every reported number is the ARX's own.

        Not merely "the numbers differ" -- a backtest that ignored its argument
        and perturbed something else would pass that. Each forecast is compared
        against a model refit independently here at the same origin, so the
        report is checked against the interface rather than against itself.
        """

        rows = self.sample()
        fitter = partial(fit_arx, regressors=REGRESSORS)
        report = at_gap(
            rows,
            purge=1,
            features=ARX_FEATURES,
            minimum_history=self.MINIMUM_HISTORY,
            fit_model=fitter,
        )

        self.assertIsInstance(report.model, FittedArx)
        self.assertEqual(report.model.regressors, REGRESSORS)
        last_train, _ = list(
            rolling_origin([row.date for row in rows], self.MINIMUM_HISTORY, 1, 1)
        )[-1]
        self.assertEqual(report.model.cutoff, rows[last_train[-1]].date)

        # Refit independently at each fold, on the fold's own training rows and
        # its own feature row. Under a gap neither is `rows[:index]` and
        # `rows[index - 1]` any more, and holding on to that arithmetic would
        # compare the purged backtest against an unpurged expectation.
        folds = list(
            rolling_origin([row.date for row in rows], self.MINIMUM_HISTORY, 1, 1)
        )
        for forecast, (train_indices, test_indices) in zip(report.forecasts, folds):
            model = fit_arx(
                [rows[i] for i in train_indices],
                REGRESSORS,
                minimum_history=self.MINIMUM_HISTORY,
            )
            feature_row = rows[train_indices[-1]]
            quantiles = model.predict(feature_row)
            self.assertEqual(
                forecast.predicted_bps, model.point_forecast(feature_row)
            )
            self.assertEqual(forecast.lower_bps, quantiles[0])
            self.assertEqual(forecast.upper_bps, quantiles[-1])
            self.assertEqual(
                forecast.actual_bps, rows[test_indices[0]].spread_bps
            )

        # The point forecast is the ARX's regression mean, not the last observed
        # spread. A backtest that read the centre off the feature row would
        # report persistence's point rule beside the ARX's intervals, and the
        # MAE would be persistence's however the model was fitted.
        persistence = at_gap(
            rows, purge=1, minimum_history=self.MINIMUM_HISTORY
        )
        self.assertNotEqual(
            [f.predicted_bps for f in report.forecasts],
            [f.predicted_bps for f in persistence.forecasts],
        )
        self.assertNotAlmostEqual(report.mae_bps, persistence.mae_bps, places=6)

    def test_persistence_remains_the_default_with_unchanged_numbers(self):
        """Generalising the backtest moved no number it already reported.

        The default is persistence's `fit`, stating it explicitly changes
        nothing, and the two numbers this function reports on the checked-in
        sample are pinned. A generalisation that is also a rewrite would show up
        here rather than in a merge.
        """

        rows = self.sample()
        default = at_gap(
            rows, purge=1, minimum_history=self.MINIMUM_HISTORY
        )
        explicit = at_gap(
            rows, purge=1, minimum_history=self.MINIMUM_HISTORY, fit_model=fit
        )

        self.assertIsInstance(default.model, FittedPersistence)
        self.assertEqual(list(default.forecasts), list(explicit.forecasts))
        self.assertEqual(default.mae_bps, explicit.mae_bps)
        self.assertEqual(default.interval_coverage, explicit.interval_coverage)

        # The persistence point rule is still the last observed spread, read off
        # the model rather than off the feature row but identical to it.
        folds = list(
            rolling_origin([row.date for row in rows], self.MINIMUM_HISTORY, 1, 1)
        )
        for forecast, (train_indices, _) in zip(default.forecasts, folds):
            # The last row that cleared the gap, which under a purge is not the
            # day before the scored day. Taken from the fold rather than from
            # `position` arithmetic, for the reason the cutoff check above is.
            self.assertEqual(
                forecast.predicted_bps, rows[train_indices[-1]].spread_bps
            )

        # Pinned at the smallest expressible gap. The numbers moved from the
        # unpurged 15/13/11 when the gap stopped being typeable as zero; what
        # this test asserts -- that the default fitter is persistence and that
        # generalising the backtest moved nothing on its own -- is unchanged.
        self.assertEqual(len(default.forecasts), 14)
        self.assertAlmostEqual(default.mae_bps, 22.0 / 14.0, places=12)
        self.assertAlmostEqual(default.interval_coverage, 8.0 / 14.0, places=12)


def unpurged_reference(rows, minimum_history, fitter):
    """The index walk `rolling_persistence_backtest` used before it was purged.

    Written out longhand rather than imported, for the reason
    `design_and_targets` above is: a reproduction test that called the code it
    is checking would reproduce whatever that code now does. This is the loop
    as it stood at `c05d250` -- training frame `rows[:index]`, feature row
    `rows[index - 1]`, one scored row per origin -- and it is the definition
    every MAE and coverage number this project has reported was produced from.
    """

    forecasts = []
    for index in range(minimum_history, len(rows)):
        model = fitter(rows[:index], minimum_history=minimum_history)
        feature_row = rows[index - 1]
        quantiles = model.predict(feature_row)
        forecasts.append(
            Forecast(
                actual_bps=rows[index].spread_bps,
                predicted_bps=model.point_forecast(feature_row),
                lower_bps=quantiles[0],
                upper_bps=quantiles[-1],
            )
        )
    mae = sum(abs(f.actual_bps - f.predicted_bps) for f in forecasts) / len(forecasts)
    coverage = sum(
        f.lower_bps <= f.actual_bps <= f.upper_bps for f in forecasts
    ) / len(forecasts)
    return forecasts, mae, coverage


class PurgedBacktestTests(unittest.TestCase):
    """The rolling backtest is a caller of `rolling_origin`, and the gap bites.

    Before this block the benchmark walked the index itself: the training frame
    ended on the calendar day before the scored day and the feature row was that
    same day. `rolling_origin` was fully implemented, fully tested, carried the
    project's only purge boundary -- and nothing in the model path called it, so
    every reported MAE and coverage number came from an unpurged walk while a
    purge existed one module over. A check anchored to nothing cannot fail.

    Mutations are recorded in `docs/block-2026-09-10-purged-backtest/RECORD.md`
    with the named test each one killed.
    """

    MINIMUM_HISTORY = 10

    #: Large enough on this panel that the feature row moves and origins are
    #: lost, small enough that folds remain. Not the registry's number -- the
    #: registry is the CLI's business, and a number written here would be this
    #: file restating `metadata/sources.json`.
    PURGE = 6

    def sample(self):
        return load_daily_panel(SAMPLE_PANEL)

    def fitters(self):
        return (
            ("persistence", None, fit),
            ("arx", partial(fit_arx, regressors=REGRESSORS), partial(fit_arx, regressors=REGRESSORS)),
        )

    def test_the_backtest_derives_its_purge_from_the_declared_feature_set(self):
        """This block's spine, and the successor to the `purge=0` reproduction.

        The purge block checked that at `purge=0` nothing moved against a
        hand-rolled unpurged walk. That check is no longer expressible: the gap
        is derived now, and `max_release_lag_days` refuses to return zero, so
        there is no declared feature set that reproduces an unpurged walk. The
        equivalent claim at this level is that **deriving** the six-day gap
        reproduces, exactly, every number the purge block reported when six was
        typed at the call site.

        Exactly, not nearly: if the derivation changed the numbers, then it
        changed something it was not asked to change, and this block's effect on
        the benchmark could not be told apart from that change.

        The registry here declares six days for the sources `spread_bps`
        resolves to, and declares no fields -- so this number is exactly as
        blind to the field-priced-purge block as it was to the source-priced
        one, which is what makes it the control. What the *real* registry does
        with those fields is a separate fact, pinned by
        `test_two_features_on_one_source_price_differently`.
        """

        rows = self.sample()
        derived = rolling_persistence_backtest(
            rows,
            features=FEATURES,
            registry=declared_registry(self.PURGE, FEATURES),
            decision_time=DECISION_TIME,
            minimum_history=self.MINIMUM_HISTORY,
        )

        self.assertEqual(derived.purge_days, self.PURGE)
        self.assertEqual(derived.features, FEATURES)

        # The numbers the purge block reported at a typed `purge=6`.
        self.assertEqual(len(derived.forecasts), 12)
        self.assertAlmostEqual(derived.mae_bps, 25.0 / 12.0, places=12)
        self.assertAlmostEqual(derived.interval_coverage, 6.0 / 12.0, places=12)

    def test_the_purge_is_derived_for_whichever_model_it_is_given(self):
        """Both implementers, not persistence alone.

        The derivation is a property of the backtest, not of the model it was
        handed, so an ARX declaring its own wider feature set must get its gap
        the same way -- and the report must say so. A backtest that derived the
        gap only on the default path would pass every persistence test here and
        leave the ARX purged by whatever the last caller happened to pass.
        """

        rows = self.sample()
        for name, features, fit_model in (
            ("persistence", FEATURES, None),
            ("arx", ARX_FEATURES, partial(fit_arx, regressors=REGRESSORS)),
        ):
            with self.subTest(model=name):
                report = rolling_persistence_backtest(
                    rows,
                    features=features,
                    registry=declared_registry(self.PURGE, features),
                    decision_time=DECISION_TIME,
                    minimum_history=self.MINIMUM_HISTORY,
                    fit_model=fit_model,
                )
                self.assertEqual(report.purge_days, self.PURGE)
                self.assertEqual(report.features, features)
                self.assertEqual(
                    report.sources, sources_for_features(features)
                )
                # The gap reached the folds, not just the report.
                self.assertEqual(len(report.forecasts), 12)

    def test_the_backtest_takes_its_folds_from_rolling_origin(self):
        """One forecast per fold, in fold order, fitted on the fold's own rows.

        The mutation this is aimed at is the quiet one: a `purge` argument
        accepted and then not passed on, so the folds are built at zero. The
        report still comes out, the intervals still look reasonable, and only a
        comparison against independently enumerated folds says otherwise.
        """

        rows = self.sample()
        dates = [row.date for row in rows]
        folds = list(rolling_origin(dates, self.MINIMUM_HISTORY, 1, self.PURGE))

        report = at_gap(
            rows, purge=self.PURGE, minimum_history=self.MINIMUM_HISTORY
        )

        self.assertEqual(len(report.forecasts), len(folds))
        # The gap costs origins on a 25-row panel, and the point of the test is
        # that it does: a run whose fold count matched the unpurged one would
        # mean the purge reached nothing.
        unpurged = at_gap(
            rows, purge=1, minimum_history=self.MINIMUM_HISTORY
        )
        self.assertLess(len(report.forecasts), len(unpurged.forecasts))

        for forecast, (train_indices, test_indices) in zip(report.forecasts, folds):
            self.assertEqual(len(test_indices), 1)
            scored = test_indices[0]
            model = fit(
                [rows[i] for i in train_indices],
                minimum_history=self.MINIMUM_HISTORY,
            )
            quantiles = model.predict(rows[train_indices[-1]])

            self.assertEqual(forecast.actual_bps, rows[scored].spread_bps)
            self.assertEqual(forecast.lower_bps, quantiles[0])
            self.assertEqual(forecast.upper_bps, quantiles[-1])
            # The fitted cutoff is the last row that cleared the gap, not the
            # day before the scored day.
            self.assertEqual(model.cutoff, dates[train_indices[-1]])
            self.assertLess(model.cutoff, dates[scored - 1])

    def test_the_feature_row_is_the_last_row_that_cleared_the_purge(self):
        """The leak the purge does not otherwise cover, and it is silent.

        Purging the training frame and then reading the feature row off
        `rows[scored - 1]` drops rows from the fit while feeding the model the
        one row that matters most -- for persistence, the only row it reads. The
        numbers still come out and the intervals still look reasonable. So this
        asserts the identity directly, and separately asserts that on this panel
        the two candidate rows actually differ, without which the first
        assertion would hold under the leak too.
        """

        rows = self.sample()
        dates = [row.date for row in rows]
        folds = list(rolling_origin(dates, self.MINIMUM_HISTORY, 1, self.PURGE))
        report = at_gap(
            rows, purge=self.PURGE, minimum_history=self.MINIMUM_HISTORY
        )

        moved = 0
        for forecast, (train_indices, test_indices) in zip(report.forecasts, folds):
            scored = test_indices[0]
            allowed = rows[train_indices[-1]]
            yesterday = rows[scored - 1]
            # Persistence's point rule is the feature row's spread, so the
            # reported centre names which row was read.
            self.assertEqual(forecast.predicted_bps, allowed.spread_bps)
            if allowed.spread_bps != yesterday.spread_bps:
                moved += 1
        self.assertGreater(
            moved,
            0,
            msg=(
                "on this panel the purged feature row and the day before the "
                "scored day carry the same spread everywhere, so this test "
                "cannot tell the two apart"
            ),
        )

        # And the selection itself, against a fold it is not entitled to trust.
        # `rolling_origin` would never yield this one -- the prefix runs one row
        # past the gap -- which is the point: the backtest states the boundary
        # rather than inheriting it, so a relaxed comparison here is visible.
        scored = dates.index(date(2026, 1, 22))
        inside = dates.index(date(2026, 1, 16))  # 01-16 + 6 == 01-22, exactly
        self.assertEqual(
            _feature_index(dates, tuple(range(inside + 1)), scored, self.PURGE),
            inside - 1,
            msg=(
                "the row whose date plus the gap lands exactly on the scored "
                "day was accepted; the boundary is strict, and a `<=` here is "
                "a row published the morning the window opened"
            ),
        )

        # No row clears, so there is no feature row. It raises rather than
        # falling back to one that does not clear -- and raises, never asserts,
        # because `python -O` strips asserts.
        with self.assertRaises(LookAheadError):
            _feature_index(dates, (0, 1), 2, 365)

    def test_the_declared_feature_set_has_no_default(self):
        """`features` is required and keyword-only, and `purge` is gone.

        Checked on the signature as well as behaviourally, because the way this
        regresses is somebody adding `features=("spread_bps",)` for convenience
        at a call site that has grown tiresome to update. A default here is
        worse than the `purge=0` default it replaced: `purge=0` at least
        announced itself as a gap of zero, whereas a defaulted feature set
        produces a *plausible* gap, derived by the right function from the wrong
        declaration, and no behavioural test would object because every number
        would look ordinary.

        `purge` is asserted absent rather than merely undefaulted. Leaving it
        accepted "for the conservative case" would restore the exact hole this
        block closed: a caller could then declare one feature set and purge over
        another, which is the thing that has no symptom.
        """

        parameters = inspect.signature(rolling_persistence_backtest).parameters
        self.assertNotIn(
            "purge",
            parameters,
            msg="the hand-set gap is back; a caller can declare one feature set "
            "and purge over another again",
        )

        for name in ("features", "registry", "decision_time"):
            with self.subTest(parameter=name):
                parameter = parameters[name]
                self.assertIs(
                    parameter.default,
                    inspect.Parameter.empty,
                    msg=f"{name} grew a default; it is a silent claim about "
                    f"which sources the model draws on",
                )
                self.assertIs(parameter.kind, inspect.Parameter.KEYWORD_ONLY)

        rows = self.sample()
        with self.assertRaises(TypeError):
            rolling_persistence_backtest(rows, minimum_history=self.MINIMUM_HISTORY)

    def test_an_undeclared_feature_raises_before_any_fold_is_built(self):
        """An unresolvable declaration has no gap, so it has no backtest.

        Both shapes `contract.sources_for_features` refuses: a name nobody
        classified, and a name declared to have no ingesting source. Neither may
        resolve to an empty source set, because an empty set is a zero-day gap
        arriving as a silence.

        "Before any fold" is asserted with a fitter that fails if it is ever
        called. A backtest that resolved the feature set late would still raise,
        and would still look correct from the outside, while having built folds
        against a gap it had not computed yet.
        """

        rows = self.sample()

        def never(*args, **kwargs):
            raise AssertionError("a fold was built before the feature set resolved")

        for feature in ("no_such_column", "dealer_treasury_position"):
            with self.subTest(feature=feature):
                with self.assertRaises(UndeclaredFeatureError):
                    rolling_persistence_backtest(
                        rows,
                        features=(feature,),
                        registry=declared_registry(self.PURGE),
                        decision_time=DECISION_TIME,
                        minimum_history=self.MINIMUM_HISTORY,
                        fit_model=never,
                    )

    def test_a_fitter_that_reads_outside_the_declared_feature_set_raises_lookahead(self):
        """The declaration was what the gap was computed from, so exceeding it leaks.

        `LookAheadError`, not `ValueError`: the reported numbers were produced
        under a gap that never saw the undeclared column's release lag, and the
        error is in the direction that flatters the model. The message has to
        name the offending columns, because "your fitter exceeded its
        declaration" is unactionable without them.
        """

        rows = self.sample()
        with self.assertRaises(LookAheadError) as caught:
            rolling_persistence_backtest(
                rows,
                features=FEATURES,
                registry=declared_registry(self.PURGE, FEATURES),
                decision_time=DECISION_TIME,
                minimum_history=self.MINIMUM_HISTORY,
                fit_model=partial(fit_arx, regressors=REGRESSORS),
            )
        for name in REGRESSORS:
            self.assertIn(name, str(caught.exception))

        # Declaring the columns it reads is what makes the same run legal.
        report = rolling_persistence_backtest(
            rows,
            features=ARX_FEATURES,
            registry=declared_registry(self.PURGE, ARX_FEATURES),
            decision_time=DECISION_TIME,
            minimum_history=self.MINIMUM_HISTORY,
            fit_model=partial(fit_arx, regressors=REGRESSORS),
        )
        self.assertIsInstance(report.model, FittedArx)

        # Declaring more than the fitter reads is conservative, not refused: it
        # purges more than the evidence requires, which is visible in the report
        # rather than silent.
        wider = ARX_FEATURES + ("tgcr",)
        generous = rolling_persistence_backtest(
            rows,
            features=wider,
            registry=declared_registry(self.PURGE, wider),
            decision_time=DECISION_TIME,
            minimum_history=self.MINIMUM_HISTORY,
        )
        self.assertEqual(generous.features, wider)

    def test_spread_bps_pulls_in_both_of_its_constituent_sources(self):
        """A derived feature draws on whatever its constituents draw on.

        `spread_bps` is `sofr` minus `iorb` and they arrive from different
        sources, so a backtest declaring it must be purged over both. This is
        the case where sizing the gap over "the obvious source" is most
        tempting and least visible: `nyfed_sofr` alone gives a number, and the
        number looks like a purge.

        Asserted through the backtest's own report rather than against
        `contract.FEATURE_SOURCES` restated here -- a second copy of the map in
        a fixture is the thing this block exists to end.
        """

        rows = self.sample()
        report = rolling_persistence_backtest(
            rows,
            features=FEATURES,
            registry=declared_registry(self.PURGE, FEATURES),
            decision_time=DECISION_TIME,
            minimum_history=self.MINIMUM_HISTORY,
        )
        self.assertEqual(len(report.sources), 2)
        self.assertEqual(report.sources, sources_for_features(FEATURES))

    def test_the_derived_source_set_is_the_feature_set_not_the_whole_registry(self):
        """"The maximum over the sources the feature set uses", asserted.

        Taking the maximum over the whole registry purges more than the evidence
        requires and silently destroys training rows, which reads as a weak model
        rather than as a configuration mistake. The registry here prices one
        source far above the rest; a backtest ranging over all of it would pick
        that number up, and a backtest ranging over the declaration would not.
        """

        rows = self.sample()
        registry = declared_registry(self.PURGE, FEATURES)
        registry["nyfed_tgcr"] = {
            "release_lag": {
                "basis": "record_date",
                "unit": "calendar_days",
                "days": 90,
                "available_time": "00:00",
                "timezone": "America/New_York",
            }
        }

        report = rolling_persistence_backtest(
            rows,
            features=FEATURES,
            registry=registry,
            decision_time=DECISION_TIME,
            minimum_history=self.MINIMUM_HISTORY,
        )
        self.assertEqual(report.purge_days, self.PURGE)
        self.assertNotIn("nyfed_tgcr", report.sources)

    def test_two_features_on_one_source_price_differently(self):
        """The acceptance criterion of the field-priced-purge block.

        Against the **real** `metadata/sources.json`, and only against it: the
        fixture registries in this file declare no fields, so nothing in them
        can tell a field-priced gap from a source-priced one.

        `spread_bps` reads `fred_macro_latest_vintage.IORB`, which declares its
        own `record_date` lag with a `revision_policy` and three ALFRED
        vintages behind it, and it prices. Add `reserve_balances`, which reads
        `fred_macro_latest_vintage.WRESBAL` -- an H.4.1 weekly on the *same
        source*, declaring no revision policy -- and the run is refused, by
        name. The declaration is what changed; the source is not.

        Both feature sets read `iorb`, because `spread_bps` is computed from
        it and the persistence model reads `spread_bps`: a declaration of
        `("iorb",)` alone is refused by `_check_fitter_stayed_inside` before it
        reaches a fold. So the pair below differs in exactly one field.

        **Same source, opposite verdicts.** That is the entire content of "the
        release lag is a property of a field", and no source-level
        implementation can produce it: priced by the source, both feature sets
        inherit that source's `snapshot_retrieved_at` basis and both refuse.
        Before this block that is exactly what happened, and it is why nothing
        in this repository had ever been measured on data it fetched -- the
        target reads `iorb`, so the target was unpriceable because a weekly
        that shares its source is.

        The refusal narrows here; it does not disappear. `WRESBAL` stays
        refused, and it stays refused for the right reason: the resolution is a
        declaration about the world, which is the human's to make in a file
        neither track may edit. What this test forbids is the shortcut -- a
        snapshot basis mapped to zero, an exemption, or a `revision_policy`
        invented on this side to unblock a number.
        """

        rows = self.sample()
        real = json.loads(REAL_REGISTRY.read_text(encoding="utf-8"))

        priced = rolling_persistence_backtest(
            rows,
            features=("spread_bps",),
            registry=real,
            decision_time=DECISION_TIME,
            minimum_history=self.MINIMUM_HISTORY,
        )
        self.assertEqual(
            priced.field_sources,
            (
                # `iorb` is spliced: IOER before 2021-07-29, IORB after. The
                # purge is sized over every field the column reads, so both
                # appear here. They declare the same lag, so the gap is
                # unchanged -- but the field list is the thing under test.
                ("fred_macro_latest_vintage", "IOER"),
                ("fred_macro_latest_vintage", "IORB"),
                ("nyfed_sofr", "SOFR"),
            ),
        )
        self.assertGreater(priced.purge_days, 0)

        with self.assertRaises(RegistryContractError) as caught:
            rolling_persistence_backtest(
                rows,
                features=("spread_bps", "reserve_balances"),
                registry=real,
                decision_time=DECISION_TIME,
                minimum_history=self.MINIMUM_HISTORY,
            )
        message = str(caught.exception)
        # Named to the field, not to the source and not to the registry. A
        # reader told only `fred_macro_latest_vintage` cannot tell a refused
        # `WRESBAL` from a refused `IORB`, and on this source those are
        # different answers.
        self.assertIn("fred_macro_latest_vintage", message)
        self.assertIn("WRESBAL", message)
        self.assertIn("available_at", message)
        # And the source it refused is a source it just priced. Without this
        # the test would also pass against two unrelated sources, which is the
        # fact that was already true and is not what this block established.
        self.assertIn(
            "fred_macro_latest_vintage",
            {source for source, _field in priced.field_sources},
        )

    def test_the_real_registry_still_refuses_a_field_with_no_revision_policy(self):
        """The narrowed `snapshot_retrieved_at` guard.

        **What this test asserted before this block.** That *every* feature set
        reading `iorb` was refused against the real registry -- which was every
        honest feature set, since `spread_bps` is computed from `iorb` and every
        model here reads `spread_bps`. The source's basis is
        `snapshot_retrieved_at`, the contract forbids mapping that to zero, and
        `max_release_lag_days` raises unless every row carries `available_at`;
        `DailyObservation` carries none.

        **What it asserts now.** That the refusal survives for a field with no
        declared revision policy. `spread_bps` no longer refuses -- `IORB` and
        `SOFR` both declare, so it prices at six days, which
        `test_two_features_on_one_source_price_differently` and the
        real-registry purge in this module's docstring record. `tga` reads
        `fred_macro_latest_vintage.WTREGEN`, an H.4.1 weekly that declares
        nothing, and it still raises. The claim narrowed from "the source" to
        "a field of it", and the guard is the same guard.

        **Still a correct guard firing, not a bug.** The resolution is still a
        Track A and human question -- either `available_at` on the daily panel
        or a declared `field_release_lags` entry for the weeklies -- and this
        test still goes red on the day it is answered, which is still the right
        alarm.
        """

        rows = self.sample()
        real = json.loads(REAL_REGISTRY.read_text(encoding="utf-8"))
        with self.assertRaises(RegistryContractError) as caught:
            rolling_persistence_backtest(
                rows,
                features=("spread_bps", "tga"),
                registry=real,
                decision_time=DECISION_TIME,
                minimum_history=self.MINIMUM_HISTORY,
            )
        message = str(caught.exception)
        self.assertIn("fred_macro_latest_vintage", message)
        self.assertIn("WTREGEN", message)
        self.assertIn("available_at", message)

    def test_a_purge_that_leaves_too_little_history_raises_rather_than_shrinking_min_train(self):
        """The refusal is the feature. Recovering a fold by relaxing is not.

        A gap wide enough to starve the first origin is exactly when shrinking
        `min_train` is tempting, and a run that shrank it would report a number
        produced by a rule nobody declared, under the `minimum_history` the
        caller asked for.
        """

        rows = self.sample()
        with self.assertRaises(SplitError) as caught:
            at_gap(rows, purge=10, minimum_history=20)
        message = str(caught.exception)
        self.assertIn("20 training rows", message)
        self.assertIn("10-day purge gap", message)

        # Same panel, same `minimum_history`, a gap it can carry: the refusal
        # above is about the gap, not about the panel being short.
        report = at_gap(rows, purge=1, minimum_history=20)
        self.assertEqual(len(report.forecasts), 5)

    def test_the_purged_backtest_scores_whichever_model_it_is_given(self):
        """Both implementers go through the purged path, on their own numbers.

        The generalisation the last block bought has to survive this one. Each
        forecast is compared against a model refit independently at the same
        fold, so the report is checked against the interface rather than against
        itself, and the two models are checked to disagree -- a purged backtest
        that quietly scored persistence whatever it was handed would pass every
        shape assertion here.
        """

        rows = self.sample()
        dates = [row.date for row in rows]
        folds = list(rolling_origin(dates, self.MINIMUM_HISTORY, 1, self.PURGE))
        fitter = partial(fit_arx, regressors=REGRESSORS)

        report = at_gap(
            rows,
            purge=self.PURGE,
            features=ARX_FEATURES,
            minimum_history=self.MINIMUM_HISTORY,
            fit_model=fitter,
        )
        self.assertIsInstance(report.model, FittedArx)
        self.assertEqual(report.model.regressors, REGRESSORS)
        self.assertEqual(len(report.forecasts), len(folds))

        for forecast, (train_indices, test_indices) in zip(report.forecasts, folds):
            train_frame = [rows[i] for i in train_indices]
            model = fit_arx(
                train_frame, REGRESSORS, minimum_history=self.MINIMUM_HISTORY
            )
            feature_row = rows[train_indices[-1]]
            quantiles = model.predict(feature_row)
            self.assertEqual(forecast.predicted_bps, model.point_forecast(feature_row))
            self.assertEqual(forecast.lower_bps, quantiles[0])
            self.assertEqual(forecast.upper_bps, quantiles[-1])
            self.assertEqual(forecast.actual_bps, rows[test_indices[0]].spread_bps)
            self.assertEqual(model.cutoff, dates[train_indices[-1]])

        persistence = at_gap(
            rows, purge=self.PURGE, minimum_history=self.MINIMUM_HISTORY
        )
        self.assertIsInstance(persistence.model, FittedPersistence)
        self.assertNotEqual(
            [f.predicted_bps for f in report.forecasts],
            [f.predicted_bps for f in persistence.forecasts],
        )

    def test_the_purge_moves_the_reported_numbers_and_the_move_is_kept(self):
        """Purging changes the benchmark, and the changed benchmark is the one.

        `AGENT_CONTRACT.md` working rules: a model that does not beat
        persistence is reported as such and kept. The same applies to a purge
        that makes the numbers worse, and on this panel it does. Pinned so that
        a later change which quietly narrows the gap has to move these numbers
        and say why; the before/after table and the synthetic caveat are in
        `docs/block-2026-09-10-purged-backtest/RECORD.md`.
        """

        rows = self.sample()
        before = at_gap(
            rows, purge=1, minimum_history=self.MINIMUM_HISTORY
        )
        after = at_gap(
            rows, purge=self.PURGE, minimum_history=self.MINIMUM_HISTORY
        )

        # "Before" is now the *smallest expressible* gap rather than no gap:
        # `max_release_lag_days` refuses to return zero, so a one-day gap is as
        # close to unpurged as a derived backtest can get. The comparison the
        # test makes is unchanged; only the left-hand column moved, and it moved
        # because the gap is derived now.
        self.assertEqual(len(before.forecasts), 14)
        self.assertEqual(len(after.forecasts), 12)
        self.assertAlmostEqual(before.mae_bps, 22.0 / 14.0, places=12)
        self.assertAlmostEqual(after.mae_bps, 25.0 / 12.0, places=12)
        self.assertAlmostEqual(before.interval_coverage, 8.0 / 14.0, places=12)
        self.assertAlmostEqual(after.interval_coverage, 0.5, places=12)
        self.assertGreater(after.mae_bps, before.mae_bps)


#: The exogenous regressor a threshold model in this module is fitted on, and
#: the column its regime is read off. **Deliberately disjoint.** `tgcr` is not a
#: regressor, so the only reason it is read at all is to choose a regime -- which
#: is the read this block exists to put through the purge, and it would be
#: invisible if the regime variable were also a term in the design.
THRESHOLD_REGRESSORS = ("sofr_volume",)
THRESHOLD_VARIABLE = "tgcr"

#: What a threshold model on the pair above declares, and the same set with the
#: regime variable left out. `UNDECLARED_THRESHOLD_FEATURES` is a *wrong*
#: declaration and is named so the acceptance test can show the two runs side by
#: side rather than inlining a tuple that looks like a typo.
THRESHOLD_FEATURES = FEATURES + THRESHOLD_REGRESSORS + (THRESHOLD_VARIABLE,)
UNDECLARED_THRESHOLD_FEATURES = FEATURES + THRESHOLD_REGRESSORS


def regime_frame(count=40, seed=20260909):
    """`regressor_frame` plus a `tgcr` column, for the two-regime model.

    `tgcr` is added rather than reused from `regressor_frame` because the regime
    variable has to resolve to a source **neither** `spread_bps` nor
    `sofr_volume` draws on: `on_rrp` and `iorb` share
    `fred_macro_latest_vintage`, so a regime read off `on_rrp` would widen the
    declared feature set without widening the source set, and the acceptance
    test's second half -- that the derived purge reflects the regime variable's
    source -- would assert nothing. `tgcr` resolves to `nyfed_tgcr`, which
    appears in the sources only when the regime variable is declared.

    The values move over a range wide enough that a split exists and narrow
    enough that both regimes stay populated on every fold of a rolling backtest.
    """

    rows = []
    state = seed
    for base in regressor_frame(count, seed):
        state = (1103515245 * state + 12345) % (2 ** 31)
        values = dict(base.values)
        values[THRESHOLD_VARIABLE] = 4.28 + (state % 97) / 1000.0
        rows.append(DailyObservation(base.date, values))
    return rows


def mixed_registry(base_purge, regime_purge):
    """A registry pricing the regime variable's source apart from the others.

    Two numbers rather than `declared_registry`'s one, because the acceptance
    test's claim is that declaring the regime variable *changes the gap*. Under
    a uniform registry it could not: every source would cost the same and the
    derived purge would be the same number whether `tgcr` was declared or not,
    so the test would pass while demonstrating nothing.
    """

    registry = declared_registry(base_purge, UNDECLARED_THRESHOLD_FEATURES)
    registry.update(declared_registry(regime_purge, (THRESHOLD_VARIABLE,)))
    return registry


def _at_or_below(values, threshold):
    """How many of `values` the low regime takes at `threshold`.

    The same `<=` the fit and the forecast both use. Written here so the two
    tests that need a threshold with a known regime size can find one by
    counting; indexing into the sorted values would assume they are distinct,
    and `regime_frame`'s are not.
    """

    return sum(1 for value in values if value <= threshold)



class FittedThresholdTests(unittest.TestCase):
    """The two-regime ARX: `PLAN.md` Phase 2's fourth benchmark.

    Three of the four benchmarks that document names existed -- last
    observation, rolling mean/quantiles, AR/ARX -- and this is the fourth. It is
    also the only one that can express the claim the whole project rests on:
    that the repo market has regimes, and that behaviour inside a stressed one
    is not the calm relationship extrapolated.

    What makes it worth a block of its own is not the arithmetic. Every model in
    `baseline` before it reads a covariate to **compute a value**; this one
    reads a covariate to **choose a model**, and that is a way for a variable to
    enter a forecast that none of the machinery built around `features_read` had
    ever seen. The purge is sized over a declared feature set before anything is
    fitted, and the first fitted model is checked against that declaration; a
    threshold model that consulted `tgcr` to pick its regime and did not report
    reading it would have had its gap computed correctly, over the wrong
    sources, in the flattering direction. The lock already existed. What this
    block establishes is that the threshold variable goes through it.

    ------------------------------------------------------------------
    How the threshold is chosen, and why that construction
    ------------------------------------------------------------------

    `fit_threshold` estimates the threshold by conditional least squares: the
    candidates are the distinct values the **training frame's own origin rows**
    carry for the threshold variable, the largest dropped because nothing lies
    above it, and the one minimising the pooled in-sample squared error of the
    two regimes wins. Ties break to the smallest candidate, so the run is
    reproducible.

    The alternatives were considered and are worse here:

    * **A fixed grid of round numbers** would import a scale nobody declared and
      would miss splits the data admits. The sum of squares changes only when a
      row crosses the boundary, so the observed values are not a sample of the
      candidate set -- they *are* the candidate set, and searching them is
      exhaustive rather than approximate.
    * **A numerical optimiser** would spend iterations on a step function whose
      every level set is already enumerated.
    * **A threshold read off the whole panel** -- the tempting one, and the leak
      this repository exists to detect wearing a different hat. A threshold is a
      fitted parameter, and a fitted parameter chosen by looking at rows the
      model will later be scored on is look-ahead however defensible the
      arithmetic around it is.
    * **A threshold declared by the caller** is supported and recorded as
      declared (`threshold_estimated is False`), because a caller stating a
      prior is a different act from a caller asking for one and a report that
      could not tell them apart would be reporting two things under one name.

    ------------------------------------------------------------------
    The minimum rows per regime, and where the number comes from
    ------------------------------------------------------------------

    `len(design_names) + 2` design rows in **each** regime: with `k` regressors
    that is `k + 4`. It is not chosen, it is inherited. `fit_arx` demands
    `columns + 2` rows of a whole window so that a leave-one-out fold keeps one
    degree of freedom; a regime is fitted by the same least squares and scored
    by the same leave-one-out law over its own rows, so it needs the same count
    of them. At `columns + 1` a held-out fold has exactly as many rows as
    coefficients, interpolates them exactly, and contributes a block of zeros to
    the pooled residual law -- which would narrow every reported interval for a
    reason that has nothing to do with forecasting. Below that the regime's
    design is not identified at all.

    A split that cannot meet it is refused, never collapsed to one regime. See
    `test_a_degenerate_split_is_refused_rather_than_collapsed_to_one_regime`.

    ------------------------------------------------------------------
    Mutation record
    ------------------------------------------------------------------

    Five leaks planted -- the four this block's brief names, and one extra
    because the second of them turned out to be inert and the reason is worth
    the extra run. Every run stdlib only, on a copy of the tree under `$HOME`
    rather than on the mount, with `data/`, `.github/`, `metadata/`,
    `.gitignore`, the root Markdown and `docs/PROJECT_STATUS.md` copied too
    (`tests/test_docs_freshness.py` reads those, and their absence is two kills
    that look real and are not), `__pycache__` cleared, `-B` with
    `PYTHONDONTWRITEBYTECODE=1`. An unmutated control ran first and the suite
    was green again after every revert. The kills below are **every** test each
    mutation killed, not a selection.

    1. **The acceptance mutation.** `FittedThreshold.features_read` returns the
       design columns alone, dropping the threshold variable -- the model still
       fits, still forecasts, still reports a regime and a threshold, and the
       only thing that changes is what it says it read.

       Kills 2 tests, both here:

       * `test_the_threshold_variable_is_purged_like_any_other_read`, on
         `LookAheadError not raised`. That is this block's acceptance criterion
         and its mutation target, and they are deliberately the same test: the
         criterion *is* that dropping the declaration stops the raise. They have
         not come apart.
       * `test_the_threshold_variable_is_reported_even_though_it_is_no_regressor`,
         on `('spread_bps', 'sofr_volume') != ('spread_bps', 'sofr_volume',
         'tgcr')`. The shape check, one level below the consequence.

       Nothing else in the suite notices, and that is the fact worth recording.
       A model that reads a column to choose its own structure and does not
       report the read is invisible to every other guard in this repository --
       the fit succeeds, the forecasts are finite, the intervals cover, and the
       reported `purge_days` is a number computed correctly over a source set
       missing `nyfed_tgcr`. Two tests stand between that and a published
       benchmark, and only the first of them is about a number.

    2. **The threshold estimated over every row supplied to the module** rather
       than the training frame's origins alone: one line appending the final
       row's threshold value to `selectors`. The final row is a target and never
       a feature, so no design row reads it; `zip` in `_regime_split` truncates,
       so the split is unaffected and the *only* effect is that the row's value
       joins the candidate set.

       **Kills nothing. The mutation is inert, and provably so.** A candidate
       threshold matters only through the partition it induces. A value strictly
       inside the origins' range induces a partition already reachable from some
       origin value, scores exactly the same error, and loses the tie to the
       smaller candidate; a value below the smallest or above the largest
       induces an empty regime and is skipped as degenerate. So the final row's
       value cannot change the answer whatever it is -- checked directly, with
       the fixture's last row moved to 99.0, far outside the 4.28..4.376 the
       origins occupy: the fitted threshold, the regime counts and both
       coefficient vectors came back identical.

       Recorded as a surviving mutation rather than quietly replaced. It says
       something real: the `[:-1]` in `_choose_threshold` and the tie-break to
       the smallest candidate together make the search insensitive to a row
       outside the design, which is a property worth knowing and not one the
       code claims anywhere else.
       `test_the_threshold_is_estimated_from_the_origin_rows_alone` is green
       under it, and is honest about that -- what it pins is invariance to the
       excluded row, which mutation 2b below does break.

    2b. **The same leak in the direction that bites**: the regime of design row
       `i` chosen by `rows[index]`, the row being predicted, rather than by
       `origin`. One token. This is the one-step look-ahead the purge machinery
       exists for, arriving one level in -- the regime assignment of a training
       row made from a value that row's forecaster had not seen.

       Kills 2 tests, both here:
       `test_the_threshold_is_estimated_from_the_origin_rows_alone`, on the
       regime counts moving (`{'low': 34, 'high': 5}` against `{'low': 33,
       'high': 6}`) when the excluded final row is perturbed -- under the
       mutation that row *is* read, so the perturbation lands; and
       `test_the_residual_law_is_leave_one_out_within_each_regime`, which
       rebuilds the split longhand from the origin rows and gets a different
       residual vector. The second is the stronger of the two: it fails on the
       law the intervals are read off, not on a count.

    3. **A degenerate split allowed to fall back to a single regime.** Two edits,
       because half a fallback is only a crash: the `thin` check in
       `_fit_regimes` returns the populated regime's coefficients for both
       regimes instead of raising, and the residual loop in `fit_threshold`
       skips a regime too thin to leave one out. Together they produce the
       dangerous shape -- a working model that reports itself as a
       `FittedThreshold`, carries a threshold and a `regime_rows` of
       `{'low': 0, 'high': 39}`, and is an ARX.

       Kills 8, across 5 test methods, all here:

       * `test_a_degenerate_split_is_refused_rather_than_collapsed_to_one_regime`
         -- all three subtests, `DegenerateRegimeError not raised` for a
         threshold below every observed value, above every observed value, and
         inside the range but too thin.
       * `test_a_regime_thin_enough_to_break_the_leave_one_out_law_is_refused`,
         same message at the boundary.
       * `test_an_estimated_threshold_produces_two_populated_regimes`, on
         `3 not greater than or equal to 5 : high regime is thin` -- the search
         now prefers a candidate that leaves three rows on one side, because an
         effectively unconstrained fit has no more error than the best genuine
         two-regime split.
       * `test_one_pooled_law_because_the_interface_declares_one`, on
         `36 != 39`: three residuals silently absent from the law the intervals
         are read off.
       * `test_the_point_forecast_is_a_step_function_of_the_regime_variable`, on
         the two regimes returning `37.618084442911695` from the same design
         row.
       * `test_the_residual_law_is_leave_one_out_within_each_regime`, as an
         error rather than a failure.

       The last two are the ones worth having. The three direct refusals fail on
       a missing exception; those fail on **a fitted model whose numbers would
       have been published** -- a threshold model whose regimes agree everywhere
       and whose residual law is three rows short of the window it claims.

       `test_a_window_with_no_two_regime_split_refuses_rather_than_returning_one`
       stays green, and that is correct rather than a gap: when the threshold
       variable never moves, *both* regimes are thin at every candidate, the
       fallback has no populated regime to fall back to, and the refusal stands.
       The fallback is dangerous exactly when one side survives.

    4. **The boring one.** `FittedThreshold.regime_for` flipped from `<=` to
       `<`, the smallest change the regime boundary admits, moving rows sitting
       exactly on the threshold out of the regime they were fitted into.

       Kills 2 tests, both here:
       `test_a_row_exactly_on_the_threshold_is_scored_by_the_regime_it_was_fitted_into`
       and `test_the_point_forecast_is_a_step_function_of_the_regime_variable`,
       both on `'high' != 'low'`.

       **Persistence's and the ARX's numbers do not move**, which is what this
       mutation was planted to establish. Every pinned figure stays green:
       `RollingBacktestTests.test_persistence_remains_the_default_with_unchanged_numbers`,
       `PurgedBacktestTests.test_the_purge_changes_the_reported_numbers_and_the_change_is_reported`,
       and `test_the_arx_reports_the_numbers_it_reported_before_a_third_model_existed`
       below. So does the whole of `tests/test_contract.py`, the threshold
       conformance case included. That is not luck and not a gap there: the fit
       splits through `_regime_split`, which this mutation does not touch, so
       the fitted model is identical either way, and the conformance case
       predicts on one feature row whose `on_rrp` is 93.8 against a fitted
       threshold of 95.4. Only a row *on* the boundary can see the change, which
       is why the boundary test lives here, with a fixture that is checked for
       having such a row rather than assumed to. This block added a model. It
       moved nothing.
    """

    MINIMUM_HISTORY = 20

    #: The gap the sources of `spread_bps` and `sofr_volume` produce, and the
    #: larger one `nyfed_tgcr` produces. Two different numbers so that declaring
    #: the regime variable visibly changes the derived purge.
    BASE_PURGE = 1
    REGIME_PURGE = 4

    def frame(self):
        return regime_frame()

    def fit(self, rows=None, **kwargs):
        """`fit_threshold` on the regime frame, with this module's declarations."""

        return fit_threshold(
            self.frame() if rows is None else rows,
            THRESHOLD_REGRESSORS,
            THRESHOLD_VARIABLE,
            minimum_history=self.MINIMUM_HISTORY,
            **kwargs,
        )

    def fitter(self):
        """The fitting call `rolling_persistence_backtest` takes."""

        return partial(
            fit_threshold,
            regressors=THRESHOLD_REGRESSORS,
            threshold_variable=THRESHOLD_VARIABLE,
        )

    # ------------------------------------------------------------------
    # The acceptance criterion
    # ------------------------------------------------------------------

    def test_the_threshold_variable_is_purged_like_any_other_read(self):
        """A regime is a read. It goes through the lock, or the gap is wrong.

        This block's acceptance criterion and its acceptance mutation, and they
        are the same test on purpose: the criterion is that dropping the
        threshold variable from `features_read` stops the raise, and the
        mutation is dropping it. A second test asserting the same thing from the
        other side would be the same assertion twice.

        Three claims, in the order the failure would happen in:

        1. A threshold model whose regime variable is outside the declared
           feature set is refused by the backtest, with `LookAheadError` naming
           the column. `tgcr` is read on every fold to choose which of two
           fitted regimes produces the point forecast, and it is not a regressor
           -- the *only* reason it is read is the regime, which is exactly the
           read a model could plausibly argue its way out of declaring.
        2. Declaring it makes the identical run succeed.
        3. The derived purge then reflects that column's source. This is the
           damage the raise prevents: `nyfed_tgcr` is absent from the source set
           of the undeclared run, so its release lag was never in the maximum,
           and the numbers would have been produced under a four-day gap's worth
           of information at a one-day gap's cost. In the flattering direction,
           as always.

        The registry prices `nyfed_tgcr` apart from the rest for claim 3 to be
        able to fail; under a uniform registry the two runs would report the
        same `purge_days` and the assertion would hold for the wrong reason.
        """

        rows = self.frame()
        registry = mixed_registry(self.BASE_PURGE, self.REGIME_PURGE)

        with self.assertRaises(LookAheadError) as caught:
            rolling_persistence_backtest(
                rows,
                features=UNDECLARED_THRESHOLD_FEATURES,
                registry=registry,
                decision_time=DECISION_TIME,
                minimum_history=self.MINIMUM_HISTORY,
                fit_model=self.fitter(),
            )
        self.assertIn(THRESHOLD_VARIABLE, str(caught.exception))

        report = rolling_persistence_backtest(
            rows,
            features=THRESHOLD_FEATURES,
            registry=registry,
            decision_time=DECISION_TIME,
            minimum_history=self.MINIMUM_HISTORY,
            fit_model=self.fitter(),
        )
        self.assertIsInstance(report.model, FittedThreshold)
        self.assertIn(THRESHOLD_VARIABLE, report.model.features_read)

        # The source the regime variable brought in, and the gap it produced.
        # Both read off the report rather than recomputed here: a second
        # derivation in a test is the thing this repository keeps deleting.
        regime_source, = sources_for_features((THRESHOLD_VARIABLE,))
        self.assertIn(regime_source, report.sources)
        self.assertNotIn(
            regime_source, sources_for_features(UNDECLARED_THRESHOLD_FEATURES)
        )
        self.assertEqual(report.purge_days, self.REGIME_PURGE)
        self.assertGreater(self.REGIME_PURGE, self.BASE_PURGE)

    # ------------------------------------------------------------------
    # What the model reads, and what it says it reads
    # ------------------------------------------------------------------

    def test_the_threshold_variable_is_reported_even_though_it_is_no_regressor(self):
        """`features_read` is what the model read, not what it was handed.

        `tgcr` appears in no design column and multiplies no coefficient. It is
        read once per row, to pick a coefficient vector. The tuple says so.
        """

        model = self.fit()
        self.assertEqual(
            model.features_read,
            FEATURES + THRESHOLD_REGRESSORS + (THRESHOLD_VARIABLE,),
        )
        self.assertNotIn(THRESHOLD_VARIABLE, model.design_names)
        # And in panel vocabulary, so the gap can be sized from it.
        sources_for_features(model.features_read)

    def test_a_regime_variable_that_is_also_a_regressor_is_reported_once(self):
        """A column may shift the level and switch the relationship.

        Reporting it twice would be a claim about multiplicity that
        `_check_fitter_stayed_inside` does not read -- it compares sets -- and
        that a human reader of a report would.
        """

        model = fit_threshold(
            self.frame(),
            ("sofr_volume", "on_rrp"),
            "on_rrp",
            minimum_history=self.MINIMUM_HISTORY,
        )
        read = model.features_read
        self.assertEqual(read.count("on_rrp"), 1)
        self.assertEqual(sorted(read), sorted(set(read)))
        self.assertEqual(read, ("spread_bps", "sofr_volume", "on_rrp"))

    # ------------------------------------------------------------------
    # Where the threshold comes from
    # ------------------------------------------------------------------

    def test_the_threshold_is_estimated_from_the_origin_rows_alone(self):
        """Nothing outside the design's own rows may reach the search.

        The last row of a training frame is a **target** and never a feature: no
        design row reads it, so nothing fitted here may depend on it. The test
        moves that row's threshold value far outside the range the rest of the
        window occupies and asserts the fitted threshold, the regime counts,
        both coefficient vectors and the residual law come back bit-identical.

        What this does and does not catch, because the mutation record turns on
        it. It is **green** under a search whose candidate set is widened to
        include the final row's value: a candidate matters only through the
        partition it induces, and a value inside the origins' range induces a
        partition already reachable from an origin value and loses the tie,
        while one outside it makes a regime empty and is skipped. So that
        mutation is inert rather than undetected. It **fails** under the leak
        that direction actually admits -- the regime of design row `i` read off
        `rows[i]` rather than off the origin -- because then the final row is
        genuinely read and the perturbation lands on the split. Mutations 2 and
        2b in the class docstring are those two runs.
        """

        rows = self.frame()
        perturbed = list(rows)
        tail = dict(perturbed[-1].values)
        tail[THRESHOLD_VARIABLE] = 99.0
        perturbed[-1] = DailyObservation(perturbed[-1].date, tail)

        base = self.fit(rows)
        after = self.fit(perturbed)

        self.assertTrue(base.threshold_estimated)
        self.assertEqual(base.threshold, after.threshold)
        self.assertEqual(dict(base.regime_rows), dict(after.regime_rows))
        for regime in ("low", "high"):
            self.assertEqual(base.coefficients[regime], after.coefficients[regime])
        self.assertEqual(base.residuals, after.residuals)

        # And the chosen value is one the origin rows actually carry.
        candidates = {row.values[THRESHOLD_VARIABLE] for row in rows[:-1]}
        self.assertIn(base.threshold, candidates)

    def test_a_declared_threshold_is_honoured_and_recorded_as_declared(self):
        """A caller stating a prior and a caller asking for one are different acts.

        A report that could not tell them apart would present a number the
        caller supplied and a number the frame produced under one name, and the
        first is not evidence about the frame at all.
        """

        rows = self.frame()
        estimated = self.fit(rows)
        declared = self.fit(rows, threshold=4.33)

        self.assertTrue(estimated.threshold_estimated)
        self.assertFalse(declared.threshold_estimated)
        self.assertEqual(declared.threshold, 4.33)

        # Declared, not checked against the frame's own optimum: a caller who
        # declares a threshold is not asking whether it was the best one.
        self.assertNotEqual(declared.threshold, estimated.threshold)

    def test_an_estimated_threshold_produces_two_populated_regimes(self):
        """Two regimes, both fitted, both above the minimum. Not asserted -- counted.

        `regime_rows` is on the fitted model so that "there are two regimes" is
        checkable from the outside rather than being a property of the name.
        """

        model = self.fit()
        minimum = len(model.design_names) + 2
        self.assertEqual(sorted(model.regime_rows), ["high", "low"])
        for regime, count in model.regime_rows.items():
            self.assertGreaterEqual(count, minimum, msg=f"{regime} regime is thin")
        self.assertEqual(
            sum(model.regime_rows.values()), len(self.frame()) - 1
        )
        # Two vectors, and they are not the same vector: a regime structure that
        # fitted the same coefficients twice would be an ARX with extra steps.
        self.assertNotEqual(model.coefficients["low"], model.coefficients["high"])

    # ------------------------------------------------------------------
    # A degenerate split is a refusal
    # ------------------------------------------------------------------

    def test_a_degenerate_split_is_refused_rather_than_collapsed_to_one_regime(self):
        """A one-regime fit wearing a threshold model's name is the worst outcome.

        Worse than a crash, because it is invisible: the numbers come out, the
        report says `FittedThreshold`, and a reader attributes them to a regime
        structure that was never estimated. So it raises, and the message says
        how many rows each side got and how many a regime needs.

        Three thresholds, covering the shapes a degenerate split takes: below
        everything, above everything, and inside the range but leaving one side
        under the minimum.
        """

        rows = self.frame()
        observed = sorted(row.values[THRESHOLD_VARIABLE] for row in rows[:-1])
        minimum = len(THRESHOLD_REGRESSORS) + 4

        cases = {
            "below every observed value": observed[0] - 1.0,
            "above every observed value": observed[-1] + 1.0,
            # The largest value that still leaves the low regime short of the
            # minimum, so the split exists and is merely too thin. Derived by
            # counting rather than by indexing into `observed`: the fixture's
            # values repeat, so the k-th distinct value does not put k + 1 rows
            # below it and an index would silently name a legal threshold.
            "inside the range but too thin": max(
                value
                for value in set(observed)
                if 0 < _at_or_below(observed, value) < minimum
            ),
        }
        for label, threshold in cases.items():
            with self.subTest(threshold=label):
                with self.assertRaises(DegenerateRegimeError) as caught:
                    self.fit(rows, threshold=threshold)
                message = str(caught.exception)
                self.assertIn(str(minimum), message)
                self.assertIn("regime", message)

        # A `ValueError`, so the CLI dispatcher's `(OSError, ValueError)` covers
        # it without naming a new type.
        self.assertTrue(issubclass(DegenerateRegimeError, ValueError))

    def test_a_window_with_no_two_regime_split_refuses_rather_than_returning_one(self):
        """When the search finds nothing, it says so instead of fitting an ARX.

        A window whose threshold variable never moves has no split in it at all:
        every candidate puts every row on one side. The honest answer is that
        there is no two-regime model to estimate here, and the message says what
        to do instead.
        """

        rows = []
        for row in self.frame():
            values = dict(row.values)
            values[THRESHOLD_VARIABLE] = 4.30
            rows.append(DailyObservation(row.date, values))

        with self.assertRaises(DegenerateRegimeError) as caught:
            self.fit(rows)
        self.assertIn("two regimes", str(caught.exception))

    def test_a_regime_thin_enough_to_break_the_leave_one_out_law_is_refused(self):
        """The minimum is the leave-one-out minimum, not a round number.

        `len(design_names) + 2` in each regime: at one fewer, a held-out fold
        has exactly as many rows as coefficients, interpolates them, and
        contributes an exact zero to the pooled residual law. A model that
        accepted it would report intervals narrowed by a block of zeros that
        describe nothing.

        Asserted at the boundary rather than in the abstract: the minimum passes
        and one row fewer raises.
        """

        rows = self.frame()
        observed = sorted(row.values[THRESHOLD_VARIABLE] for row in rows[:-1])
        minimum = len(THRESHOLD_REGRESSORS) + 4

        # The boundary, both sides of it, found by counting rows rather than by
        # indexing: the fixture's values repeat, so the k-th distinct value does
        # not put k + 1 rows at or below it.
        passes = min(
            value
            for value in set(observed)
            if _at_or_below(observed, value) >= minimum
        )
        raises = max(
            value
            for value in set(observed)
            if 0 < _at_or_below(observed, value) < minimum
        )
        self.assertLess(raises, passes)

        model = self.fit(rows, threshold=passes)
        self.assertGreaterEqual(model.regime_rows["low"], minimum)
        self.assertEqual(len(model.residuals), len(rows) - 1)

        with self.assertRaises(DegenerateRegimeError):
            self.fit(rows, threshold=raises)

    # ------------------------------------------------------------------
    # Reading the regime off a row
    # ------------------------------------------------------------------

    def test_a_row_exactly_on_the_threshold_is_scored_by_the_regime_it_was_fitted_into(self):
        """The boundary is closed on the low side, in the fit and in the forecast.

        One comparison, stated twice and required to agree: `_regime_split` puts
        `selector <= threshold` in `"low"`, and `regime_for` must do the same.
        If they disagreed, a row on the boundary would be fitted into one regime
        and scored by the other's coefficients -- a forecast produced by a model
        that was never fitted on rows like it, and nothing else in the suite
        would notice.
        """

        rows = self.frame()
        model = self.fit(rows)
        on_boundary = [
            row
            for row in rows[:-1]
            if row.values[THRESHOLD_VARIABLE] == model.threshold
        ]
        self.assertTrue(on_boundary, msg="the fixture offers no boundary row")

        for row in on_boundary:
            self.assertEqual(model.regime_for(row), "low")
            self.assertEqual(
                model.point_forecast(row),
                _dot(model.coefficients["low"], model.design_row(row)),
            )

        # And a row just above it is the other regime, so the comparison is a
        # boundary rather than a constant.
        above = min(
            (
                row
                for row in rows[:-1]
                if row.values[THRESHOLD_VARIABLE] > model.threshold
            ),
            key=lambda row: row.values[THRESHOLD_VARIABLE],
        )
        self.assertEqual(model.regime_for(above), "high")

    def test_the_point_forecast_is_a_step_function_of_the_regime_variable(self):
        """Two regimes means two relationships, and the model has to show it.

        The same design row scored under each regime gives two different
        numbers, which is the entire content of "a regime is a read that chooses
        a model". A threshold model whose regimes agreed everywhere would be an
        ARX reporting a threshold.
        """

        rows = self.frame()
        model = self.fit(rows)
        row = rows[-2]

        low = dict(row.values)
        low[THRESHOLD_VARIABLE] = model.threshold
        high = dict(row.values)
        high[THRESHOLD_VARIABLE] = model.threshold + 1.0

        low_row = DailyObservation(row.date, low)
        high_row = DailyObservation(row.date, high)

        self.assertEqual(model.regime_for(low_row), "low")
        self.assertEqual(model.regime_for(high_row), "high")
        self.assertEqual(model.design_row(low_row), model.design_row(high_row))
        self.assertNotAlmostEqual(
            model.point_forecast(low_row),
            model.point_forecast(high_row),
            places=9,
            msg=(
                "the two regimes produce the same forecast from the same design "
                "row; nothing was switched"
            ),
        )

    def test_an_unobserved_threshold_variable_is_refused_not_imputed(self):
        """A regressor's gap is imputed; a regime's gap cannot be.

        An imputed mean enters a regressor's sum and moves the forecast by a
        coefficient times a number. An imputed mean on the threshold variable
        would choose a *model*, putting every unobserved row in whichever regime
        the training mean falls in, silently and uniformly -- and the regime
        counts a reader checks would include rows whose regime was never
        observed.

        Absent and unobserved stay distinguishable, as contract test 5 requires:
        different types, `MissingRegressorError` and `UnobservedThresholdError`.
        """

        rows = self.frame()
        model = self.fit(rows)

        unobserved = dict(rows[-2].values)
        unobserved[THRESHOLD_VARIABLE] = None
        with self.assertRaises(UnobservedThresholdError):
            model.regime_for(DailyObservation(rows[-2].date, unobserved))

        absent = {
            name: value
            for name, value in rows[-2].values.items()
            if name != THRESHOLD_VARIABLE
        }
        with self.assertRaises(MissingRegressorError):
            model.regime_for(DailyObservation(rows[-2].date, absent))

        self.assertFalse(
            issubclass(UnobservedThresholdError, MissingRegressorError)
        )
        self.assertFalse(
            issubclass(MissingRegressorError, UnobservedThresholdError)
        )

        # At fit time too: an origin row with no observation is not imputed into
        # a regime either.
        broken = list(rows)
        gap = dict(broken[3].values)
        gap[THRESHOLD_VARIABLE] = None
        broken[3] = DailyObservation(broken[3].date, gap)
        with self.assertRaises(UnobservedThresholdError):
            self.fit(broken)

    # ------------------------------------------------------------------
    # The residual law
    # ------------------------------------------------------------------

    def test_the_residual_law_is_leave_one_out_within_each_regime(self):
        """No residual was minimised by the coefficients that produced it.

        The concern `fit_arx` documents, doubled: two regimes over one window
        means twice the coefficients and twice the in-sample narrowing, so an
        in-sample law here would be more flattering than it was there.

        Rebuilt longhand from the split rather than compared against the
        module's own helper, so the test checks the definition rather than the
        implementation agreeing with itself.
        """

        rows = self.frame()
        model = self.fit(rows)

        imputations = window_means(rows, THRESHOLD_REGRESSORS)
        design, targets = design_and_targets(rows, THRESHOLD_REGRESSORS, imputations)
        selectors = [row.values[THRESHOLD_VARIABLE] for row in rows[:-1]]

        expected = []
        for regime, keep in (("low", True), ("high", False)):
            block = [
                (row, target)
                for row, target, selector in zip(design, targets, selectors)
                if (selector <= model.threshold) is keep
            ]
            for index in range(len(block)):
                reduced = block[:index] + block[index + 1 :]
                coefficients = _least_squares(
                    [row for row, _ in reduced], [target for _, target in reduced]
                )
                expected.append(block[index][1] - _dot(coefficients, block[index][0]))

        self.assertEqual(model.residuals, tuple(sorted(expected)))

    def test_one_pooled_law_because_the_interface_declares_one(self):
        """`residuals` is the sample both outputs read, so there is one of it.

        A per-regime law would make `residuals` a claim `predict` does not
        honour, and the agreement between the quantiles and the exceedance --
        the assertion that separates a derived stress number from a separately
        fitted one -- would have nothing to stand on. The regimes differ in the
        conditional mean and share the dispersion, and that limitation is real
        and stated rather than discovered from the intervals.
        """

        model = self.fit()
        anchor = model.point_forecast(self.frame()[-2])
        quantiles = model.predict(self.frame()[-2])

        self.assertEqual(len(model.residuals), sum(model.regime_rows.values()))
        self.assertEqual(list(model.residuals), sorted(model.residuals))
        for level, quantile in zip(QUANTILE_LEVELS, quantiles):
            self.assertAlmostEqual(
                quantile, anchor + _quantile(model.residuals, level), places=12
            )

    # ------------------------------------------------------------------
    # Nothing else moved
    # ------------------------------------------------------------------

    def test_the_arx_reports_the_numbers_it_reported_before_a_third_model_existed(self):
        """This block adds a model. It does not touch the others.

        Persistence's numbers are already pinned, in
        `RollingBacktestTests.test_persistence_remains_the_default_with_unchanged_numbers`
        and `PurgedBacktestTests.test_the_purge_changes_the_reported_numbers_and_the_change_is_reported`.
        The ARX's were only ever pinned relative to persistence's, which a change
        that moved both would satisfy. They are absolute here, at the two gaps
        the rest of this file uses, so that "the numbers did not move" is a
        claim a run can refute rather than a sentence in a commit message.
        """

        rows = load_daily_panel(SAMPLE_PANEL)
        arx = partial(fit_arx, regressors=REGRESSORS)

        near = at_gap(
            rows, purge=1, features=ARX_FEATURES, minimum_history=10, fit_model=arx
        )
        self.assertEqual(len(near.forecasts), 14)
        self.assertAlmostEqual(near.mae_bps, 1.9142198265530637, places=12)
        self.assertAlmostEqual(near.interval_coverage, 4.0 / 7.0, places=12)

        far = at_gap(
            rows, purge=6, features=ARX_FEATURES, minimum_history=10, fit_model=arx
        )
        self.assertEqual(len(far.forecasts), 12)
        self.assertAlmostEqual(far.mae_bps, 2.086429950395829, places=12)
        self.assertAlmostEqual(far.interval_coverage, 0.5, places=12)


# --------------------------------------------------------------------------
# The exceedance-predictor interface
# --------------------------------------------------------------------------


#: The declared family, as a fixture. The declaration is Track A's file; this is
#: four ascending numbers in the range the generated frame produces.
EXCEEDANCE_TAUS = (5.0, 10.0, 20.0, 50.0)


class ExceedancePredictorConformance:
    """What every `ExceedancePredictor` must satisfy, whatever it is.

    A mixin, subclassed once per implementer, for the reason
    `ForecastInterfaceConformance` is: an interface with one implementer is a
    description, and the check that it stays an interface is that each
    assertion runs once per implementer rather than once per file. Until
    `arx_exceedance` existed every assertion below was a statement about
    `climatology_exceedance` wearing an interface's name.

    Subclasses supply `make_predictor`. Everything else is shared, and
    `ExceedancePredictorCoverageTests` fails if an implementer arrives in any
    module of the `repo_model` package without a case here.
    """

    MINIMUM_HISTORY = 20

    def frame(self):
        return regressor_frame()

    def split(self):
        """Training rows and feature rows, the shape the evaluator hands over."""

        rows = self.frame()
        return rows[:-4], rows[-4:]

    def make_predictor(self):  # pragma: no cover - overridden
        raise NotImplementedError

    def curves(self, taus=EXCEEDANCE_TAUS):
        train, feature_rows = self.split()
        return self.make_predictor()(train, feature_rows, taus)

    def test_the_return_is_curves_plus_an_account_of_what_was_read(self):
        """Both halves, because the evaluator checks both.

        A predictor that returned bare curves would make no claim about the
        columns it read, and `event_eval` sizes its purge from a declaration it
        verifies against exactly that claim.
        """

        result = self.curves()
        self.assertIsInstance(result, ExceedanceCurves)
        self.assertIsInstance(result.features_read, tuple)
        self.assertTrue(result.features_read, msg="claimed to read nothing")
        # In panel vocabulary, and classifiable: the gap is sized over the
        # sources these resolve to, so a name `contract` cannot classify is a
        # name that contributes nothing to the purge.
        sources_for_features(result.features_read)

    def test_one_curve_per_feature_row_aligned_to_the_declared_taus(self):
        train, feature_rows = self.split()
        result = self.make_predictor()(train, feature_rows, EXCEEDANCE_TAUS)
        self.assertEqual(len(result.curves), len(feature_rows))
        for curve in result.curves:
            self.assertEqual(len(curve), len(EXCEEDANCE_TAUS))

    def test_every_value_is_a_probability(self):
        for curve in self.curves().curves:
            for position, probability in enumerate(curve):
                with self.subTest(tau=EXCEEDANCE_TAUS[position]):
                    self.assertTrue(math.isfinite(probability))
                    self.assertGreaterEqual(probability, 0.0)
                    self.assertLessEqual(probability, 1.0)

    def test_the_curve_never_rises_with_tau(self):
        """`P(Y > tau)` cannot increase as `tau` does.

        On a dense grid rather than the four declared taus: four points can be
        non-increasing while the curve between them is not. The grid spans the
        training spreads, so it covers where each implementer's mass actually
        sits.
        """

        train, feature_rows = self.split()
        spreads = [row.spread_bps for row in train]
        low, high = min(spreads) - 20.0, max(spreads) + 20.0
        grid = [low + (high - low) * step / 120.0 for step in range(121)]
        for day, curve in enumerate(
            self.make_predictor()(train, feature_rows, grid).curves
        ):
            for position in range(1, len(curve)):
                self.assertLessEqual(
                    curve[position],
                    curve[position - 1],
                    msg=f"day {day}: exceedance rises from {grid[position - 1]} "
                    f"to {grid[position]}",
                )

    def test_a_threshold_above_everything_fitted_gets_a_hard_zero(self):
        """No smoothing and no prior, on either implementer.

        `climatology_exceedance` argues this at length and the reasoning is not
        about climatologies: a model that put *no* weight where the event went
        is the most informative result the knowledge holdout can produce, and a
        Laplace correction would turn it into a small number that merely looks
        like a poor forecast. `1/(n+2)` for any plausible `n` here is far above
        zero, so a smoothed implementation cannot pass this by rounding.
        """

        train, feature_rows = self.split()
        beyond = max(row.spread_bps for row in train) + 10_000.0
        for curve in self.make_predictor()(train, feature_rows, [beyond]).curves:
            self.assertEqual(curve[0], 0.0)

    def test_a_training_frame_below_the_minimum_is_refused(self):
        """A curve from a handful of rows is not a fitted law.

        At an event boundary the training set is whatever cleared the purge gap,
        which can be very short without anything else objecting -- so the
        refusal belongs to the predictor and not to the caller who did not
        notice.
        """

        train, feature_rows = self.split()
        with self.assertRaises(ValueError):
            self.make_predictor()(
                train[: self.MINIMUM_HISTORY - 1], feature_rows, EXCEEDANCE_TAUS
            )


class ClimatologyExceedanceTests(ExceedancePredictorConformance, unittest.TestCase):
    """The conformance suite against `climatology_exceedance`."""

    IMPLEMENTATION = staticmethod(climatology_exceedance)

    def make_predictor(self):
        return climatology_exceedance(minimum_history=self.MINIMUM_HISTORY)

    def test_the_curve_is_the_same_on_every_scored_day(self):
        """Unconditional by definition, and the baseline a skill score needs.

        A climatology whose curve moved with the day would be conditioning on
        something, and then it would not be the thing the other side of the
        comparison is measured against. It reads the feature rows for their
        count and nothing else.
        """

        self.assertEqual(len(set(self.curves().curves)), 1)

    def test_it_reads_the_training_target_and_no_covariate(self):
        self.assertEqual(self.curves().features_read, ("spread_bps",))

    def test_the_curve_is_the_fraction_of_training_spreads_strictly_above_tau(self):
        """The arithmetic, restated independently of the implementation."""

        train, feature_rows = self.split()
        history = [row.spread_bps for row in train]
        expected = tuple(
            sum(1 for value in history if value > tau) / len(history)
            for tau in EXCEEDANCE_TAUS
        )
        self.assertEqual(self.curves().curves[0], expected)


class ArxExceedanceTests(ExceedancePredictorConformance, unittest.TestCase):
    """The conformance suite against `arx_exceedance`, on the same rows.

    The second implementer is what turns each assertion in the mixin from a
    description of the climatology into a constraint on the interface. Three of
    them had nothing to bite on before: the non-increasing check was a statement
    about counting values above a threshold, the hard zero was a statement about
    a training set with nothing above `tau`, and the whole suite was silent on a
    predictor that reads anything off a feature row at all.
    """

    IMPLEMENTATION = staticmethod(arx_exceedance)

    def make_predictor(self):
        return arx_exceedance(REGRESSORS, minimum_history=self.MINIMUM_HISTORY)

    def test_it_reports_the_autoregressive_term_as_well_as_its_regressors(self):
        """The half a predictor reporting only what it was handed would omit.

        `event_eval` checks this claim against the declared feature set, so a
        predictor that named only its exogenous columns would let the purge be
        sized without `spread_bps`'s sources in the maximum.
        """

        self.assertEqual(self.curves().features_read, ("spread_bps",) + REGRESSORS)

    def test_the_curve_moves_across_feature_rows(self):
        """The property the climatology cannot have, on the same fixture.

        Not an assertion about *this* model being good -- it is the assertion
        that the interface carries information rather than shape. A widening
        that plumbed a covariate through without the model reading it would
        produce a flat curve here and be indistinguishable from the baseline.
        """

        self.assertGreater(len(set(self.curves().curves)), 1)

    def test_the_law_is_the_one_the_fitted_model_already_reports(self):
        """Not a second reading of the residuals. The model's own.

        Character for character `FittedArx.predict_stress`, which is why no
        distribution is fabricated here: if this ever stops agreeing, something
        in `arx_exceedance` has started deriving a curve of its own.
        """

        train, feature_rows = self.split()
        model = fit_arx(train, REGRESSORS, minimum_history=self.MINIMUM_HISTORY)
        self.assertEqual(
            self.curves().curves,
            tuple(model.predict_stress(row, EXCEEDANCE_TAUS) for row in feature_rows),
        )

    def test_an_empty_regressor_set_is_refused(self):
        """`fit_arx` refuses one, and this does not paper over the refusal."""

        train, feature_rows = self.split()
        with self.assertRaises(ValueError):
            arx_exceedance((), minimum_history=self.MINIMUM_HISTORY)(
                train, feature_rows, EXCEEDANCE_TAUS
            )


class ThresholdExceedanceTests(ExceedancePredictorConformance, unittest.TestCase):
    """The conformance suite against `threshold_exceedance`, on regime rows.

    The third implementer, and the first whose curve moves for two reasons. The
    mixin's `regressor_frame` carries no `tgcr`, so `frame` is overridden to
    `regime_frame` -- the same fixture `FittedThresholdTests` fits on, for the
    same reason: the regime variable has to resolve to a source neither
    `spread_bps` nor the regressors draw on, or the claim that declaring it
    widens the source set asserts nothing.

    What the third implementer adds to the mixin is a predictor whose curve is
    not a continuous function of the feature row. Every inherited assertion --
    the probabilities, the non-increasing curve on a dense grid, the hard zero
    above the fitted support -- was a statement about two smooth predictors
    until now.

    This class exists because `ExceedancePredictorCoverageTests` demanded it,
    which is that guard working: it failed on the first run of the block that
    added `threshold_exceedance`, before a line of test was written, reporting
    `['threshold_exceedance'] != []`.

    The mutation record for the block that added this implementer is in
    `tests/test_event_eval.py::RegimeDeclarationTests`, with the acceptance
    criterion. Two of the four mutations are killed here and nowhere else.
    """

    IMPLEMENTATION = staticmethod(threshold_exceedance)

    def frame(self):
        return regime_frame()

    def make_predictor(self):
        return threshold_exceedance(
            THRESHOLD_REGRESSORS,
            THRESHOLD_VARIABLE,
            minimum_history=self.MINIMUM_HISTORY,
        )

    def fitted(self):
        train, _feature_rows = self.split()
        return fit_threshold(
            train,
            THRESHOLD_REGRESSORS,
            THRESHOLD_VARIABLE,
            minimum_history=self.MINIMUM_HISTORY,
        )

    def test_it_reports_the_regime_variable_as_well_as_its_regressors(self):
        """The read that is neither a term in the design nor the target.

        `event_eval` and `rolling_persistence_backtest` both check this claim
        against the declared feature set, so a predictor naming only its
        exogenous columns would let the purge be sized without the regime
        variable's fields in the maximum. `THRESHOLD_VARIABLE` is disjoint from
        `THRESHOLD_REGRESSORS` on purpose: if it were also a regressor the claim
        would be satisfied by the design alone and this would assert nothing.
        """

        self.assertEqual(
            self.curves().features_read,
            ("spread_bps",) + THRESHOLD_REGRESSORS + (THRESHOLD_VARIABLE,),
        )
        self.assertNotIn(THRESHOLD_VARIABLE, THRESHOLD_REGRESSORS)

    def test_the_law_is_the_one_the_fitted_model_already_reports(self):
        """Not a second reading of the residuals. The model's own.

        Character for character `FittedThreshold.predict_stress`. A curve built
        here from `model.residuals` directly agrees with this about the centre
        on any row in whichever regime it happened to anchor on and disagrees
        only across the cutoff -- the regime enters through the centre and
        nowhere else. `regime_frame`'s last four rows all fall in the low
        regime, so this assertion cannot see that construction and, mutated,
        does not: the kill belongs to the test below, which builds the
        straddling pair rather than hoping the frame supplies one. What this
        one holds is everything else -- a Gaussian, a smoothing, a Laplace
        correction, a second residual vector -- and it holds it exactly.
        """

        model = self.fitted()
        _train, feature_rows = self.split()
        self.assertEqual(
            self.curves().curves,
            tuple(model.predict_stress(row, EXCEEDANCE_TAUS) for row in feature_rows),
        )

    def test_the_curve_moves_across_the_fitted_cutoff(self):
        """The property neither of the other two implementers can have.

        Two feature rows identical in every column but the regime variable, one
        either side of the fitted threshold. `arx_exceedance` given this pair
        would return one curve twice: the design row is the same, so a smooth
        response to a covariate has nothing to respond to. This returns two,
        and the difference is the regime reaching the centre.

        The pair is constructed rather than found among `regime_frame`'s rows
        because the frame's last four all fall in the low regime -- which is a
        fact about the fixture and not about the model, and a test that depended
        on it would be testing the fixture. `FittedThresholdTests` builds the
        same pair one level down, against `point_forecast`; this is the same
        construction carried through to the exceedance curve, which is where
        `event_eval` reads it.
        """

        model = self.fitted()
        _train, feature_rows = self.split()
        row = feature_rows[-1]

        low = DailyObservation(
            row.date, dict(row.values, **{THRESHOLD_VARIABLE: model.threshold})
        )
        high = DailyObservation(
            row.date, dict(row.values, **{THRESHOLD_VARIABLE: model.threshold + 1.0})
        )
        self.assertEqual(model.regime_for(low), "low")
        self.assertEqual(model.regime_for(high), "high")
        self.assertEqual(model.design_row(low), model.design_row(high))

        curves = self.make_predictor()(
            self.split()[0], (low, high), EXCEEDANCE_TAUS
        ).curves
        self.assertNotEqual(
            curves[0],
            curves[1],
            msg="one design row scored under two regimes gave one curve; the "
            "regime is not reaching the centre, and a curve re-derived from "
            "the pooled residuals about a single centre would look like this",
        )

    def test_an_undeclared_regime_variable_is_not_available(self):
        """Both columns are positional and neither has a default.

        `fit_threshold` refuses a defaulted regressor set and a defaulted
        threshold variable, and a factory that supplied either would be making
        the silent assumption on the fitter's behalf one call up.
        """

        with self.assertRaises(TypeError):
            threshold_exceedance(THRESHOLD_REGRESSORS)
        with self.assertRaises(TypeError):
            threshold_exceedance()

    def test_a_window_with_no_second_regime_is_refused_not_flattened(self):
        """`fit_threshold`'s refusal, uncaught and unrewrapped.

        A constant regime variable offers no candidate that splits the window,
        and the honest answer is that there is no two-regime model to estimate
        here. A wrapper that fell back to a single regime would report itself as
        a threshold model over a regime structure that was never estimated.
        """

        train, feature_rows = self.split()
        flat = [
            DailyObservation(
                row.date, dict(row.values, **{THRESHOLD_VARIABLE: 4.30})
            )
            for row in train
        ]
        with self.assertRaises(DegenerateRegimeError):
            self.make_predictor()(flat, feature_rows, EXCEEDANCE_TAUS)


# --------------------------------------------------------------------------
# The pooled exceedance path
# --------------------------------------------------------------------------

#: The threshold this section's assertions are made at. The frame below is
#: built so that this one separates the two regimes and the three above it
#: separate nothing: every scored spread is under 10bp, so a run that scored a
#: curve against the wrong tau column is scoring against an all-zero outcome
#: series and says so.
REGIME_TAU = 5.0
EXCEEDANCE_MINIMUM_HISTORY = 20


def regime_shift_frame(count=60, seed=20260908, shift_at=30):
    """A panel that sits around 2bp and then sits around 9bp.

    Built for one property: **a later fold's training rows change the
    climatology materially.** Before the shift no training row exceeds
    `REGIME_TAU`, so the unconditional base rate is 0; by the last origin
    roughly half of them do. A reference fitted once over the whole frame lands
    near the middle and is wrong at both ends, which is what makes the two
    constructions in
    `test_the_climatology_reference_is_refitted_on_each_fold_like_the_model_it_scores`
    tell each other apart. On a stationary frame they would agree to several
    places and the acceptance test would pass under its own mutation.

    Generated rather than stored, for the reason `regressor_frame` gives: the
    property under test is a property of the numbers. The jitter is kept under
    0.2bp so it moves the spread without moving it across `REGIME_TAU`, and the
    9bp regime stays under 10bp so the declared taus above the first have no
    positives at all -- an absence the artifact has to report rather than
    default.
    """

    rows = []
    state = seed
    for index in range(count):
        state = (1103515245 * state + 12345) % (2 ** 31)
        level = 0.02 if index < shift_at else 0.09
        rows.append(
            DailyObservation(
                date(2026, 1, 1) + timedelta(days=index),
                {
                    "sofr": 4.30 + level + 0.0001 * (state % 20),
                    "iorb": 4.30,
                    "sofr_volume": 2100.0 + (state % 1301) / 3.0,
                    "on_rrp": 90.0 + (state % 211) / 10.0,
                },
            )
        )
    return rows


class RollingExceedanceTests(unittest.TestCase):
    """The scoring holdout for the probabilistic target, and its one criterion.

    `AGENT_CONTRACT.md`'s "Metrics" names the headline -- Brier skill score
    against climatology plus a Murphy decomposition -- and `metrics.py` had
    implemented every part of it while nothing in `src/repo_model/` outside
    `metrics.py` called any of them. That was structural rather than an
    oversight: `rolling_persistence_backtest` scores a `FittedForecastModel`
    and reports continuous-target numbers, exceedance probabilities come only
    from an `ExceedancePredictor`, and the only evaluator consuming one was
    `event_eval`, where the contract forbids an aggregate. So the headline had
    nowhere to be computed, and `rolling_exceedance_backtest` is that place.

    **Where the aggregate is allowed.** On the scoring holdout, produced by
    `rolling_origin`: crisis dates excluded from the headline metric but
    available for training once they are in the past. Not on a knowledge
    holdout, where "Event windows get the exceedance curve and realized path.
    No aggregate Brier or reliability number on a single event window."
    `test_the_knowledge_holdout_path_still_carries_no_aggregate` is the
    standing guard on the second half, and it is a guard on an *absence*, so it
    reads the module rather than a result.

    Why the reference is refitted per fold
    ======================================

    A skill score is a ratio against a reference, and the reference is a fitted
    object with a training set. There are two ways to get it wrong and both
    leave every number in range:

    * **Fitted once over all rows.** The reference has then seen the scored
      days, so it is better than it could have been in production, and the
      ratio is *understated*. The error is in the conservative direction, which
      is exactly why nobody catches it.
    * **Fitted once over the first fold's rows and reused.** The reference
      decays as the window advances while the scored model is refitted, so the
      skill score climbs for no reason but the asymmetry.

    Either way the arithmetic is right and the comparison is not between two
    things measured the same way. So `climatology_exceedance` is *called*
    inside the fold loop, on the same rows and through the same interface as
    the model it is the reference for.

    Which windows the pooled set contains, and which it excludes
    ===========================================================

    Every fold `rolling_origin` yields over the panel the run was handed, and
    nothing else. Event windows are neither excluded nor specially included:
    the scoring holdout is defined by crisis dates being available for training
    *once they are in the past*, which is what an expanding rolling origin does
    by construction, and a crisis day is scored on a model that was not allowed
    to see it. What is excluded is the knowledge holdout -- crises stripped
    from training entirely and scored once per window. That is `event_eval`'s,
    it is reported separately, and no number from it reaches this table.
    `rolling_exceedance_backtest` reads no events file and must not.

    Mutation record
    ===============

    Control first, green before and after each: OK, zero `expectedFailure`.
    Stdlib only, run from a copy of the tree under `$HOME` -- never the mount --
    carrying `data/`, `.github/`, `metadata/`, `.gitignore`, the root Markdown
    and `docs/PROJECT_STATUS.md`, because `tests/test_docs_freshness.py` reads
    those and their absence is a fistful of kills that look real and are not.
    `-B` with `PYTHONDONTWRITEBYTECODE=1` and `__pycache__` cleared before each
    run.

    1. **The acceptance mutation: the climatology fitted once, outside the fold
       loop, over the whole frame.** One line moved -- the reference predictor
       called on `tuple(rows)` rather than on `train_rows`. Every fold still
       scores, every artifact still writes, the skill score is still a number
       in range. Kills 2, both `AssertionError`:

       * `test_the_climatology_reference_is_refitted_on_each_fold_like_the_model_it_scores`
         -- **the criterion and the mutation do not come apart.** It dies on
         its first assertion, comparing the reference the run scored against to
         the one this test walks the splitter to build: `[0.0, 0.0, ...]` where
         the early folds had seen nothing above 5bp, against `[0.5, 0.5, ...]`
         from a reference that had seen the whole regime shift. The reported
         skill score moves from a per-fold `0.88` to a whole-frame `-0.65`,
         which is the "understated in the conservative direction" failure with
         its sign visible.
       * `test_the_climatology_scored_against_itself_has_no_skill` -- `-0.65 !=
         0.0`. Worth having beside the criterion because it needs no fixture at
         all: when the scored model *is* the reference, skill is 0 by
         definition, and it stops being 0 the moment the two see different rows.

    2. **The purge dropped from the exceedance path only.** `rolling_origin`
       and `_feature_index` called with a literal `0` while `_derive_purge`
       still runs and `purge_days` is still reported, so the artifact claims a
       gap the run did not have. The rolling quantile path keeps its gap; this
       one loses it. Kills 3, all `AssertionError`:

       * `test_the_pooled_set_is_the_folds_the_splitter_yields_behind_the_derived_gap`
         -- on the fold-level boundary, `scored_date - feature_date >
         purge_days`. The gap the report names is not the gap the folds were
         built at.
       * `test_the_climatology_reference_is_refitted_on_each_fold_like_the_model_it_scores`
         -- collateral, and informative: the fold structure moved, so the
         reference this test rebuilds at the *reported* gap no longer matches
         the one the run used. A gap that is decorative shows up as a
         disagreement about which rows trained.
       * `tests/test_cli_eval.py::ExceedanceBacktestCommandTests::test_the_gap_follows_from_the_declared_features_and_reaches_the_numbers`
         -- the command-level half: a wider declaration no longer costs
         origins, because no declaration costs any.

    3. **The pooled outcomes taken one tau along** -- `_at_tau` projecting the
       outcome column at `position + 1` while the curve stays at `position`, so
       a curve produced at 5bp is scored against the exceedances of 10bp. The
       declared family is read once and indexed twice, and the two disagree.
       Kills 5:

       * `test_each_outcome_is_taken_at_the_threshold_its_curve_was_produced_at`
         -- `AssertionError: 0 not greater than 0`. The frame's scored spreads
         all sit under 10bp, so the shifted column has no positives at the one
         tau that should have some.
       * `test_the_climatology_reference_is_refitted_on_each_fold_like_the_model_it_scores`
         -- `AssertionError` on the outcome vector, which this test derives
         from the realized path and the threshold rather than from the
         projection. That independence is deliberate and was added after a
         first run of this mutation left the criterion green: a test that read
         its outcomes through the projection it is checking would have been
         handed the same wrong column and agreed with itself.
       * `test_the_artifact_carries_what_produced_the_numbers` and
         `tests/test_cli_eval.py::ExceedanceBacktestCommandTests::test_the_command_publishes_the_headline_metric`
         -- `KeyError: 'decomposition'`. The shifted column is one class, so
         CORP refuses it and the field is absent with its reason. The artifact
         still writes; it simply has nothing in it.
       * `test_the_reliability_band_is_reproducible_and_per_threshold` --
         `KeyError: 'reliability_curve'`, the same degeneracy one field over.

    4. **The boring one, and it was boring.** The three things this block must
       not move: the continuous-target artifact, the exceedance curves of all
       three predictors, and the six-day purge the real registry produces for
       `spread_bps`. Checked directly rather than by planting anything --
       `python3 -m repo_model backtest` run against `origin/main` and against
       this branch on the same panel, registry, decision time and minimum
       history, and the two JSON files diffed: **identical, byte for byte,
       bootstrap seed included.** The seed matters because `_report_seed` was
       refactored to share `_seed_from` with the exceedance artifact, and a
       shared digest that changed the continuous path's material would have
       moved every interval that path has ever reported. The three predictors'
       curves and `features_read` were dumped on a fixed frame in both trees
       and diffed the same way: identical. `derived.purge_days` is 6 on both.

       Mutations 1 through 3 corroborate it from the other side: across all
       three runs, **no test outside `RollingExceedanceTests` and
       `ExceedanceBacktestCommandTests` changed status.** A mutation in this
       block's code that reached the continuous path would have said so.
    """

    FEATURES = ARX_FEATURES
    TAU_FAMILY = EXCEEDANCE_TAUS
    MINIMUM_HISTORY = EXCEEDANCE_MINIMUM_HISTORY

    def setUp(self):
        self.rows = regime_shift_frame()

    def predictor(self):
        return arx_exceedance(REGRESSORS, minimum_history=self.MINIMUM_HISTORY)

    def report(self, purge=1, predictor=None, model_name="arx", features=None):
        declared = self.FEATURES if features is None else features
        return rolling_exceedance_backtest(
            self.rows,
            predictor=self.predictor() if predictor is None else predictor,
            model_name=model_name,
            features=declared,
            registry=declared_registry(purge, declared),
            decision_time=DECISION_TIME,
            taus=self.TAU_FAMILY,
            minimum_history=self.MINIMUM_HISTORY,
        )

    def per_fold_climatology(self, purge, tau):
        """The reference, rebuilt from the fold structure rather than the code.

        Walks the same splitter at the same gap and counts, for each fold, the
        training spreads strictly above `tau`. That is the definition of a
        climatology and it is written out here so the assertion below compares
        the run against the definition rather than against a helper the run
        also calls.
        """

        dates = [row.date for row in self.rows]
        reference = []
        for train_indices, _test in rolling_origin(
            dates, self.MINIMUM_HISTORY, 1, purge
        ):
            history = [self.rows[i].spread_bps for i in train_indices]
            reference.append(sum(1 for v in history if v > tau) / len(history))
        return reference

    def test_the_climatology_reference_is_refitted_on_each_fold_like_the_model_it_scores(self):
        """The acceptance criterion, and the mutation is the same test.

        Three assertions, in the order the failure would be reasoned about.

        The reference the run used is the fold-by-fold one, element for
        element. Derived here from the fold structure, never read off the
        report and never typed: a number obtained by running the code and
        pasted into a test is the failure this repository keeps finding, and it
        would pass under every mutation that changed the code and the number
        together.

        The reported skill score is the one that reference produces. That is
        the assertion the criterion is written as -- the reference could be
        carried correctly on the report and a second, single one used for the
        ratio.

        And the two constructions genuinely differ, by more than rounding. That
        is what makes the first two assertions mean anything: on a stationary
        panel a per-fold reference and a whole-frame one agree to several
        places, and every assertion above would hold under the mutation.
        """

        purge = 1
        report = self.report(purge=purge)
        position = list(report.taus).index(REGIME_TAU)
        predicted, referenced, _projected = report.at_tau(position)
        # The outcomes derived here from the realized path and the threshold,
        # not read off the projection the run scored with. Otherwise a run that
        # scored the curve against the wrong tau column would hand this test
        # the same wrong column and the comparison would agree with itself.
        realized = [1 if value > REGIME_TAU else 0 for value in report.realized_bps]
        self.assertEqual(list(_projected), realized)

        per_fold = self.per_fold_climatology(purge, REGIME_TAU)
        self.assertEqual(len(per_fold), len(realized))
        self.assertEqual(
            per_fold,
            list(referenced),
            msg="the reference the run scored against is not the fold-by-fold one",
        )

        expected = brier_skill_score(predicted, realized, climatology=per_fold)
        self.assertAlmostEqual(
            report.metrics[position].brier_skill_score, expected, places=12
        )

        # The mutation, constructed: one climatology fitted over the whole
        # frame, which is what hoisting the reference out of the fold loop
        # produces. Every fold still scores, the artifact still writes, and the
        # skill score is still a number in range -- it is simply a different
        # number, measured against a reference that had seen the scored days.
        whole_frame = sum(
            1 for row in self.rows if row.spread_bps > REGIME_TAU
        ) / len(self.rows)
        single = brier_skill_score(predicted, realized, climatology=whole_frame)
        self.assertGreater(
            abs(expected - single),
            0.01,
            msg="the two constructions agree here, so this panel cannot tell "
            "them apart and the assertions above prove nothing",
        )
        self.assertNotAlmostEqual(
            report.metrics[position].brier_skill_score, single, places=6
        )

    def test_the_reference_is_the_climatology_and_is_not_the_caller_s_to_choose(self):
        """`AGENT_CONTRACT.md` says skill *against climatology*, so it is fixed.

        A reference argument would let a run publish a ratio against something
        else under a heading that says climatology -- the failure `--model`
        having no default was written to prevent, one level in. Asserted on the
        signature, because it is an absence and no behavioural test can catch
        an argument nobody passes.
        """

        parameters = inspect.signature(rolling_exceedance_backtest).parameters
        for name in ("reference", "climatology", "reference_predictor"):
            self.assertNotIn(name, parameters)

    def test_the_pooled_set_is_the_folds_the_splitter_yields_behind_the_derived_gap(self):
        """The gap follows from `--feature` and it reaches the pooled numbers.

        Asserted as a relation between two gaps rather than against a literal.
        A wider gap costs origins, and every fold's feature row has to clear
        it -- `scored_date - feature_date > purge`, the splitter's own strict
        boundary. A path that reported a `purge_days` it did not pass to
        `rolling_origin` would hold the first assertion and fail the rest.
        """

        narrow = self.report(purge=1)
        wide = self.report(purge=6)

        self.assertEqual(narrow.purge_days, 1)
        self.assertEqual(wide.purge_days, 6)
        self.assertLess(len(wide.folds), len(narrow.folds))

        for report in (narrow, wide):
            for fold in report.folds:
                self.assertGreater(
                    (fold.scored_date - fold.feature_date).days, report.purge_days
                )
                self.assertEqual(fold.train_end, fold.feature_date)

        position = list(narrow.taus).index(REGIME_TAU)
        self.assertNotEqual(
            narrow.metrics[position].brier, wide.metrics[position].brier
        )

    def test_each_outcome_is_taken_at_the_threshold_its_curve_was_produced_at(self):
        """Curve and outcome share one reading of the declared family.

        Two facts, neither of them a restatement of the loop that builds them.
        The frame's scored spreads all sit under 10bp, so the three upper taus
        must have no positives and the lowest must have some -- a column read
        one position over collapses that. And exceedance events nest: a day
        above 20bp is above 5bp, so a day's outcome vector is non-increasing,
        which a mis-indexed column breaks whenever the day straddles two taus.
        """

        report = self.report()
        self.assertLess(max(report.realized_bps), 10.0)

        positives = {metric.tau_bp: metric.positives for metric in report.metrics}
        self.assertGreater(positives[5.0], 0)
        self.assertEqual(positives[10.0], 0)
        self.assertEqual(positives[20.0], 0)
        self.assertEqual(positives[50.0], 0)

        for day, row in zip(report.realized_bps, report.outcomes):
            for position in range(1, len(row)):
                self.assertLessEqual(
                    row[position],
                    row[position - 1],
                    msg=f"{day}bp is recorded as exceeding "
                    f"{report.taus[position]} but not {report.taus[position - 1]}",
                )

    def test_the_aggregate_is_labelled_the_scoring_holdout(self):
        """The table says which table it is, in the file and not only in prose.

        The contract keeps two holdouts apart and says the knowledge one is
        "never averaged into the main table". This artifact is the main table.
        A file that could not say so is one somebody eventually averages an
        event window into, and the label is the cheapest thing that makes the
        conflation visible in a diff.
        """

        report = self.report()
        self.assertEqual(report.holdout_role, event_eval.SCORING_HOLDOUT)
        self.assertNotEqual(event_eval.SCORING_HOLDOUT, event_eval.KNOWLEDGE_HOLDOUT)
        document = exceedance_backtest_document(
            report,
            panel_path=SAMPLE_PANEL,
            registry_path=REAL_REGISTRY,
            thresholds_path=REAL_THRESHOLDS,
        )
        self.assertEqual(document["holdout_role"], event_eval.SCORING_HOLDOUT)

    def test_the_knowledge_holdout_path_still_carries_no_aggregate(self):
        """`event_eval` gained no aggregate, and cannot have gained one quietly.

        An absence, so it is asserted against the module rather than against a
        result. `event_eval` imports no metric: an aggregate Brier, skill,
        reliability or log score on that path has to come from `metrics.py`,
        and there is no import to bring one in. And no field of
        `EventWindowReport` is named for one, which is where a number would
        have to surface to reach the CLI.

        What this does not cover, stated rather than left to be discovered: a
        future block could compute an aggregate inside `cli_eval._event_holdout`
        from the curves the report already carries. That path is guarded by
        `tests/test_cli_eval.py`, which pins what `event-holdout` prints.
        """

        source = Path(event_eval.__file__).read_text(encoding="utf-8")
        # Import statements only. The module's prose names `metrics` where it
        # explains why it holds no aggregate, and a substring check over the
        # whole file would be a guard that fires on the explanation of itself.
        importing = [
            line
            for line in source.splitlines()
            if line.split(" ")[:1] in (["import"], ["from"]) and "metrics" in line
        ]
        self.assertEqual(importing, [])

        fields = event_eval.EventWindowReport.__dataclass_fields__
        for banned in ("brier", "skill", "reliability", "decomposition", "log_score"):
            for name in fields:
                self.assertNotIn(banned, name)

    def test_a_predictor_reading_outside_the_declaration_is_refused(self):
        """The same guard the other two paths use, on this one too.

        The purge was sized from the declaration before anything was fitted, so
        a predictor reading a column outside it was purged over the wrong
        fields -- and the error is in the flattering direction, because the
        undeclared column's release lag was never taken into the maximum.
        """

        with self.assertRaises(LookAheadError):
            self.report(features=FEATURES)

    def test_the_reference_is_checked_against_the_declaration_too(self):
        """It is fitted on the same rows, so its read had to be covered too.

        `climatology_exceedance` reports `("spread_bps",)`, so a declaration
        that omits the target is refused even when the scored model would have
        been satisfied by it. Run with a predictor that reads nothing else, so
        the refusal can only be the reference's.
        """

        declared = ("on_rrp",)
        with self.assertRaises(LookAheadError) as caught:
            rolling_exceedance_backtest(
                self.rows,
                predictor=_reads_nothing_but(("on_rrp",)),
                model_name="fixture",
                features=declared,
                registry=declared_registry(1, declared),
                decision_time=DECISION_TIME,
                taus=self.TAU_FAMILY,
                minimum_history=self.MINIMUM_HISTORY,
            )
        self.assertIn("spread_bps", str(caught.exception))

    def test_the_twcrps_weights_come_from_the_declared_family(self):
        """Derived, not typed, so a change to the declaration moves them.

        Four numbers written beside the four declared taus would be the same
        weighting today and a silent disagreement the day
        `metadata/stress_thresholds.json` changed. Asserted as the relation --
        ascending, normalised at the top, and following a family this test
        invents rather than the declared one.
        """

        self.assertEqual(twcrps_weights((1.0, 2.0, 4.0)), (0.25, 0.5, 1.0))
        report = self.report()
        self.assertEqual(
            report.twcrps_weights,
            tuple(tau / report.taus[-1] for tau in report.taus),
        )
        with self.assertRaises(SplitError):
            twcrps_weights((-5.0, -1.0))

    def test_an_unrepresentable_or_degenerate_metric_is_absent_with_its_reason(self):
        """Absent rather than defaulted, and accounted for rather than silent.

        Three absences this frame actually produces, and each is a result
        rather than a failure. Above 10bp nothing was scored, so the reference
        is right about every day and the ratio has no denominator; the outcomes
        are one class, so the decomposition is degenerate and CORP says so. At
        `REGIME_TAU` the ARX puts probability 0 on days the regime shift then
        delivers, so the log score is infinite -- deliberately unclipped, and
        unrepresentable in strict JSON, which is a different thing from
        uncomputed and is recorded as such.
        """

        report = self.report()
        document = exceedance_backtest_document(
            report,
            panel_path=SAMPLE_PANEL,
            registry_path=REAL_REGISTRY,
            thresholds_path=REAL_THRESHOLDS,
        )

        high = document["metrics"]["by_tau"]["50"]
        self.assertNotIn("brier_skill_score", high)
        self.assertNotIn("decomposition", high)
        self.assertIn("brier_skill_score", high["unavailable"])
        self.assertIn("decomposition", high["unavailable"])
        # Retained because the contract commits to retaining it, and computable
        # on a sample no ratio survives.
        self.assertIn("brier", high)

        low = document["metrics"]["by_tau"]["5"]
        self.assertNotIn("log_score", low)
        self.assertIn("log_score", low["unavailable"])
        self.assertTrue(math.isinf(log_score_of(report, REGIME_TAU)))

        # Whatever else is absent, nothing is `Infinity` or `NaN`: the file has
        # to parse under a strict reader, and `json` writes both without
        # complaint.
        text = json.dumps(document)
        self.assertNotIn("Infinity", text)
        self.assertNotIn("NaN", text)

    def test_the_artifact_carries_what_produced_the_numbers(self):
        """Declaration, derivation, panel, folds, metrics -- as the continuous one does.

        The fields are asserted against the run rather than against literals:
        the panel digest against the bytes, the fold extent against the report,
        the derived gap against what the run was purged at. A document that
        recomputed any of them would be a second derivation of the number that
        shaped the run.
        """

        report = self.report()
        document = exceedance_backtest_document(
            report,
            panel_path=SAMPLE_PANEL,
            registry_path=REAL_REGISTRY,
            thresholds_path=REAL_THRESHOLDS,
        )

        self.assertEqual(document["declaration"]["model"], "arx")
        self.assertEqual(document["declaration"]["features"], sorted(self.FEATURES))
        self.assertEqual(document["declaration"]["taus_bp"], list(report.taus))
        self.assertEqual(
            document["declaration"]["twcrps_weights"], list(report.twcrps_weights)
        )
        self.assertEqual(document["declaration"]["minimum_history"], self.MINIMUM_HISTORY)
        self.assertEqual(document["declaration"]["decision_time"], "16:00")

        self.assertEqual(document["derived"]["purge_days"], report.purge_days)
        self.assertEqual(document["derived"]["sources"], sorted(report.sources))
        self.assertEqual(
            document["derived"]["fields"],
            [f"{s}.{f}" for s, f in sorted(report.field_sources)],
        )

        self.assertEqual(
            document["panel"]["sha256"],
            hashlib.sha256(SAMPLE_PANEL.read_bytes()).hexdigest(),
        )
        self.assertEqual(document["panel"]["row_count"], len(self.rows))
        self.assertEqual(document["panel"]["first_date"], self.rows[0].date.isoformat())
        self.assertEqual(document["panel"]["last_date"], self.rows[-1].date.isoformat())

        self.assertEqual(document["folds"]["count"], len(report.folds))
        self.assertEqual(
            document["folds"]["first"]["scored_date"],
            report.folds[0].scored_date.isoformat(),
        )
        self.assertEqual(
            document["folds"]["last"]["scored_date"],
            report.folds[-1].scored_date.isoformat(),
        )

        metrics = document["metrics"]
        self.assertEqual(metrics["scored_days"], len(report.scored_dates))
        self.assertEqual(sorted(metrics["by_tau"]), ["10", "20", "5", "50"])
        self.assertEqual(metrics["threshold_weighted_crps"], report.twcrps)

        scored = metrics["by_tau"]["5"]
        self.assertEqual(scored["brier_skill_score"], report.metrics[0].brier_skill_score)
        # Nothing rounded: rounding belongs to whoever displays them, and an
        # artifact that rounded would make two runs that genuinely differ look
        # identical.
        self.assertNotEqual(scored["brier"], round(scored["brier"], 4))

        decomposition = scored["decomposition"]
        self.assertAlmostEqual(decomposition["identity_residual"], 0.0, places=12)
        self.assertAlmostEqual(
            decomposition["score"],
            decomposition["reliability"]
            - decomposition["resolution"]
            + decomposition["uncertainty"],
            places=12,
        )

    def test_the_reliability_band_is_reproducible_and_per_threshold(self):
        """Every interval comes through the stationary bootstrap, seeded from the run.

        The seed is a digest of what the run was, so the same run on the same
        panel reproduces the same band exactly and a reader can recompute it
        from fields the artifact already carries. Per threshold, so the four
        bands are four resample streams: a band sharing a stream with the one
        above it would understate how much the two differ, invisibly.
        """

        report = self.report()
        first = exceedance_backtest_document(
            report,
            panel_path=SAMPLE_PANEL,
            registry_path=REAL_REGISTRY,
            thresholds_path=REAL_THRESHOLDS,
        )
        again = exceedance_backtest_document(
            report,
            panel_path=SAMPLE_PANEL,
            registry_path=REAL_REGISTRY,
            thresholds_path=REAL_THRESHOLDS,
        )
        self.assertEqual(first, again)

        curve = first["metrics"]["by_tau"]["5"]["reliability_curve"]
        self.assertEqual(curve["method"], "corp_isotonic")
        self.assertEqual(curve["band"]["method"], "stationary_bootstrap")
        # Measured off this run's own fold horizons, not computed from the gap:
        # a weekend inside a six-day gap spans seven calendar days and five
        # panel rows, and `purge + 1` would be a number from the wrong
        # vocabulary that looks about right.
        self.assertEqual(
            curve["band"]["block_length"], baseline._maximum_horizon_overlap(report.folds)
        )
        for point in curve["points"]:
            self.assertLessEqual(point["lower"], point["upper"])
            self.assertLessEqual(point["lower"], point["recalibrated"] + 1e-12)

        seeds = {
            key: row["reliability_curve"]["band"]["seed"]
            for key, row in first["metrics"]["by_tau"].items()
            if "reliability_curve" in row
        }
        self.assertEqual(len(set(seeds.values())), len(seeds))

        # A different model on the same panel is a different run and draws a
        # different stream.
        other = self.report(
            predictor=climatology_exceedance(minimum_history=self.MINIMUM_HISTORY),
            model_name="climatology",
        )
        published = exceedance_backtest_document(
            other,
            panel_path=SAMPLE_PANEL,
            registry_path=REAL_REGISTRY,
            thresholds_path=REAL_THRESHOLDS,
        )
        self.assertNotEqual(
            published["metrics"]["by_tau"]["5"]["reliability_curve"]["band"]["seed"],
            curve["band"]["seed"],
        )

    def test_the_climatology_scored_against_itself_has_no_skill(self):
        """A sanity anchor with no free parameters: skill 0, exactly.

        The scored model and the reference are then the same predictor fitted
        on the same rows at every origin, so the two Brier scores are the same
        number and the ratio is 1. It is worth pinning because it is the one
        value in this file that follows from the definition rather than from
        the data, and because it fails under any mutation that makes the
        reference and the model see different rows.
        """

        report = self.report(
            predictor=climatology_exceedance(minimum_history=self.MINIMUM_HISTORY),
            model_name="climatology",
        )
        position = list(report.taus).index(REGIME_TAU)
        self.assertEqual(report.metrics[position].brier_skill_score, 0.0)
        self.assertEqual(
            report.metrics[position].brier, report.metrics[position].reference_brier
        )


def log_score_of(report, tau):
    """The log score at `tau`, recomputed from the report's own pooled columns."""

    from repo_model.metrics import log_score

    position = list(report.taus).index(tau)
    predicted, _reference, realized = report.at_tau(position)
    return log_score(predicted, realized)


def _reads_nothing_but(features):
    """An `ExceedancePredictor` fixture that reports reading exactly `features`.

    Not a model. It exists so that
    `test_the_reference_is_checked_against_the_declaration_too` can hold the
    scored model's declaration constant and let the reference be the only
    thing that can exceed it -- with a real predictor, both claims move
    together and the test could not say which one was refused.
    """

    def fit_predict(train_rows, feature_rows, taus):
        return ExceedanceCurves(
            tuple((0.5,) * len(taus) for _ in feature_rows), tuple(features)
        )

    return fit_predict


def _returns_exceedance_predictor(function):
    """Does `function` declare an `ExceedancePredictor` as its return type?

    The marker is the declared return annotation, because that is what an author
    writes deliberately: a factory that returns an `ExceedancePredictor` and says
    so is in, and a helper that happens to return a callable is not.

    What the annotation *is* depends on a statement in the module that defines
    it. Under `from __future__ import annotations` it is the string
    `"ExceedancePredictor"`; without that import it is the object the name was
    bound to when the `def` was executed -- `baseline.ExceedancePredictor`
    itself, which is a `Callable[...]` alias and not a class. Every module of
    `repo_model` carries the future import today, so a marker that compared the
    string alone was right about every module that exists and would have been
    silently wrong about the first one that does not. That failure is the one
    walking the package was supposed to close: `ml.py` arrives with an
    exceedance factory, the walk reaches its module, the annotation is an object
    rather than a string, nothing matches, and a module the walk read produces
    exactly what a module the walk never reached produces.

    So the string is resolved through the defining module's globals and both
    branches end at the same comparison. Resolving rather than name-matching is
    also the stronger rule: a return annotation that resolves to some other type
    is not this interface, whatever it is spelled.
    """

    annotation = getattr(function, "__annotations__", {}).get("return")
    if isinstance(annotation, str):
        module = sys.modules.get(getattr(function, "__module__", None) or "")
        annotation = getattr(module, annotation, annotation)
    return annotation == baseline.ExceedancePredictor


def _exceedance_implementations(package=repo_model):
    """Exceedance-predictor factories across the `repo_model` package, by name.

    Keyed by qualified name, `module.factory`. Bare names would collide: two
    modules may define the same factory name, and the later would silently
    replace the earlier in the dict -- one implementer lost, and lost exactly
    where a second predictor of the same shape is most likely to appear.

    Discovered, not listed, for the reason `_forecast_implementations` in
    `tests/test_contract.py` is: a list that has to be kept up to date would be
    updated in the same commit that added the implementer it was meant to catch.
    Discovered from every module of the package rather than from `baseline`
    alone, for the reason that discovery walks the package: the next
    implementer was expected to arrive in `src/repo_model/ml.py`, and a factory
    there would have been outside the only module this ever read. It did, at
    block 11 -- `repo_model.ml.gbm_exceedance` -- and it was discovered with no
    change here, which is the walk doing what it was widened to do.

    A factory imported into a second module is counted once, under the module
    that defines it: `__module__` is where a function was defined, not where a
    name was bound, and `cli_eval` binds every one of these.
    """

    found = {}
    for module in _package_modules(package):
        for name, obj in vars(module).items():
            if not inspect.isfunction(obj) or obj.__module__ != module.__name__:
                continue
            if _returns_exceedance_predictor(obj):
                found[f"{module.__name__}.{name}"] = obj
    return found


def _exceedance_cases():
    """`{factory: [test case, ...]}` over every subclass of the mixin."""

    cases = {}
    pending = list(ExceedancePredictorConformance.__subclasses__())
    while pending:
        case = pending.pop()
        pending.extend(case.__subclasses__())
        if issubclass(case, unittest.TestCase):
            cases.setdefault(case.IMPLEMENTATION, []).append(case)
    return cases


class ExceedancePredictorCoverageTests(unittest.TestCase):
    """The guard that keeps the exceedance suite a conformance suite.

    The same guard `ForecastInterfaceCoverageTests` is, one interface over, and
    for the same reason: two implementers is what makes an interface a
    constraint, and three is where it quietly stops being one -- implementer
    three arrives with a bespoke test class, every test passes, and nothing says
    the shared assertions were never run against it.

    **Count the tests, not the file diff.** Nothing here asserts how many
    implementers there are; what is asserted is that the set of them and the set
    of covered ones are the same set.

    Since the holdout-model-selector block it asserts a second sameness over the
    same discovered set: every implementer is reachable **by name from the
    command line**. Conformance says a predictor obeys the interface; this says
    somebody outside the test suite can run it. Before that block only
    `climatology_exceedance` was reachable -- `_event_holdout` constructed it
    unconditionally -- so `arx_exceedance` and `threshold_exceedance` existed
    only where a test built them, and `PLAN.md`'s Phase 2 exit criterion, a
    conditional model scored against climatology, had no path. A fourth
    implementer the CLI cannot run now fails this existing guard rather than
    going unnoticed, which is the whole reason this class exists.

    Discovery reads the whole package, not `baseline` alone, and it reads the
    return annotation as a *type* rather than as a string. It did neither until
    this block, and both halves close the same door: the gradient-boosted model
    ships an exceedance factory in `src/repo_model/ml.py`, and that factory
    would have been missed twice over -- once because the discovery never
    reached the module, and once more, had only the walk been added, because
    `ml.py` need not carry `from __future__ import annotations` and its
    annotation would then be the `Callable[...]` alias rather than the string
    the marker compared. A walk that reaches a module and recognises nothing in
    it fails exactly like a walk that never reached it, and it fails while
    looking fixed. Closed before the model that would use it exists.

    Mutations, all four against
    `test_an_exceedance_factory_in_any_package_module_is_discovered`, run in a
    disposable copy under `$HOME` built from `git ls-files`, on CPython 3.9.6.
    Unmutated control green before and after; each target confirmed to appear
    exactly once before it was applied.

    ==============================  ==============  ===========================
    Mutation                        Exception       Killed
    ==============================  ==============  ===========================
    `for module in                  AssertionError  the planted factory outside
    _package_modules(package)` ->                   `baseline` is not
    `for module in [baseline]`                      discovered
    `obj.__module__ != module.      AssertionError  the module that only
    __name__` guard dropped                         imports a factory is
                                                    credited with defining it
    `found[f"{module.__name__}.     AssertionError  no qualified key exists to
    {name}"]` -> `found[name]`                      look up, and the twin has
                                                    overwritten the first: two
                                                    modules, one factory name,
                                                    one entry, one predictor
                                                    lost
    the marker back to string-only  AssertionError  the factory in the module
    (`__annotations__["return"]                     without
    == "ExceedancePredictor"`)                      `from __future__ import
                                                    annotations` is missed by a
                                                    walk that read its module
    ==============================  ==============  ===========================

    The neighbouring reachability test needed no change: it compares factory
    *objects* against `cli_eval.MODEL_FACTORIES`, so it followed the widened
    discovery on its own. Only the sentences naming `baseline` as the place
    implementers live were corrected.
    """

    #: A package planted on disk for the discovery to walk. Every module is a
    #: case: a factory outside `baseline`; a second module defining the *same
    #: factory name*; a module that only imports a `baseline` factory; and --
    #: the one a walk alone does not catch -- a module with no
    #: `from __future__ import annotations`, whose annotation is therefore the
    #: alias object and not the string. Named nothing a list would have
    #: anticipated, which is the point: it stands for the module that does not
    #: exist yet.
    PLANTED_PACKAGE = {
        "__init__.py": "",
        "river_law.py": """
            from __future__ import annotations

            from repo_model.baseline import ExceedancePredictor


            def oxbow_exceedance(minimum_history: int = 20) -> ExceedancePredictor:
                def fit_predict(train_rows, feature_rows, taus):
                    raise NotImplementedError

                return fit_predict
        """,
        "twin_law.py": """
            from __future__ import annotations

            from repo_model.baseline import ExceedancePredictor


            def oxbow_exceedance(minimum_history: int = 20) -> ExceedancePredictor:
                def fit_predict(train_rows, feature_rows, taus):
                    raise NotImplementedError

                return fit_predict
        """,
        "importer.py": """
            from repo_model.baseline import climatology_exceedance
        """,
        # No `from __future__ import annotations`, deliberately. This is what
        # `ml.py` may well look like, and the annotation below is the
        # `Callable[...]` alias itself rather than the string `baseline` yields.
        "eager_law.py": """
            from repo_model.baseline import ExceedancePredictor


            def eager_exceedance(minimum_history: int = 20) -> ExceedancePredictor:
                def fit_predict(train_rows, feature_rows, taus):
                    raise NotImplementedError

                return fit_predict
        """,
    }

    PLANTED_NAME = "oxbow_pkg"

    @contextlib.contextmanager
    def _planted_package(self):
        """`PLANTED_PACKAGE` written to a temporary directory and imported.

        A real package on a real path, not a `types.ModuleType` stand-in: what
        is under test is a `pkgutil` walk over `__path__` and an annotation
        whose form is decided by a `__future__` statement compiled into the
        module -- a hand-built module object would skip both mechanisms.
        `sys.path` and `sys.modules` are put back on the way out so the walk
        leaves no residue for the rest of the suite.
        """

        with tempfile.TemporaryDirectory() as root:
            package_dir = Path(root) / self.PLANTED_NAME
            package_dir.mkdir()
            for filename, source in self.PLANTED_PACKAGE.items():
                (package_dir / filename).write_text(textwrap.dedent(source))
            sys.path.insert(0, root)
            try:
                yield importlib.import_module(self.PLANTED_NAME)
            finally:
                sys.path.remove(root)
                for name in [
                    name
                    for name in sys.modules
                    if name == self.PLANTED_NAME
                    or name.startswith(self.PLANTED_NAME + ".")
                ]:
                    del sys.modules[name]

    def test_an_exceedance_factory_in_any_package_module_is_discovered(self):
        """A factory outside `baseline` is found -- including the annotated one.

        The door this closes: an exceedance factory defined in
        `src/repo_model/ml.py` is selectable, is scored, publishes a record, and
        never runs the conformance assertions, because the discovery that was
        supposed to demand a case for it read one module and matched one string.
        """

        with self._planted_package() as package:
            discovered = _exceedance_implementations(package)

            self.assertIn(
                "oxbow_pkg.river_law.oxbow_exceedance",
                discovered,
                msg=(
                    "an exceedance factory outside repo_model.baseline was not "
                    "discovered; the walk is still reading one module, and a "
                    "factory added in any other module of the package would "
                    "never run the conformance suite"
                ),
            )

            # The trap, and the reason the walk alone is not enough. This module
            # has no `from __future__ import annotations`, so its return
            # annotation is the ExceedancePredictor alias and not the string
            # `baseline` yields. A marker that compares the string reaches this
            # module, reads this function, and reports nothing -- indistinguish-
            # able from never having walked here at all.
            self.assertIn(
                "oxbow_pkg.eager_law.eager_exceedance",
                discovered,
                msg=(
                    "a factory in a module without `from __future__ import "
                    "annotations` was missed: its return annotation is the "
                    "ExceedancePredictor alias object, not the string, and the "
                    "marker only recognises one of the two forms"
                ),
            )

            # Two modules defining one factory name are two implementers. Keyed
            # by bare name the later would silently replace the earlier, and the
            # one lost is exactly the second predictor of the same shape.
            self.assertIn("oxbow_pkg.twin_law.oxbow_exceedance", discovered)
            self.assertIsNot(
                discovered["oxbow_pkg.river_law.oxbow_exceedance"],
                discovered["oxbow_pkg.twin_law.oxbow_exceedance"],
                msg="two modules defining one factory name collapsed to one entry",
            )

            # A factory imported into a second module is counted once, under the
            # module that defines it. The `__module__` rule, now across modules:
            # `cli_eval` imports every factory in `baseline` and the walk
            # reaches both, so a bound name would otherwise be found twice and
            # the copy would have no conformance case naming it.
            self.assertNotIn(
                "oxbow_pkg.importer.climatology_exceedance",
                discovered,
                msg=(
                    "a factory imported into a second module was counted "
                    "twice; __module__ is where a function was defined, not "
                    "where it was bound"
                ),
            )

            self.assertEqual(
                sorted(discovered),
                [
                    "oxbow_pkg.eager_law.eager_exceedance",
                    "oxbow_pkg.river_law.oxbow_exceedance",
                    "oxbow_pkg.twin_law.oxbow_exceedance",
                ],
            )

        # The anchor. The negative assertion above is satisfied by a discovery
        # that finds nothing at all, so one assertion has to be that the real
        # package still comes back populated.
        self.assertIn(
            "repo_model.baseline.climatology_exceedance",
            _exceedance_implementations(),
            msg=(
                "discovery over the real package found no climatology; a walk "
                "that finds nothing passes every negative assertion here"
            ),
        )

    def test_every_exceedance_predictor_in_the_package_runs_the_conformance_suite(
        self,
    ):
        """Renamed at block 11. `_exceedance_implementations` reads every module
        of `repo_model`, not `baseline`, from block 10 onward; `in_baseline` was
        already false when it was written and the first factory outside
        `baseline` -- `repo_model.ml.gbm_exceedance` -- is what made the wrong
        name misleading rather than merely stale. The assertions are unchanged.
        """

        implementations = _exceedance_implementations()
        self.assertIn(
            "repo_model.baseline.climatology_exceedance",
            implementations,
            msg="discovery found no climatology; the discovery is broken, not "
            "the package",
        )
        self.assertIn("repo_model.baseline.arx_exceedance", implementations)

        cases = _exceedance_cases()
        uncovered = sorted(
            name
            for name, factory in implementations.items()
            if factory not in cases
        )
        self.assertEqual(
            uncovered,
            [],
            msg=(
                f"{uncovered} return an ExceedancePredictor from a module of "
                f"the repo_model package and no conformance case runs the "
                f"interface's assertions against them. Add an "
                f"ExceedancePredictorConformance subclass rather than a bespoke "
                f"test class: a predictor with its own tests and no conformance "
                f"case is how the suite stops being one"
            ),
        )

        # And each case really runs the suite: a subclass that shadowed the
        # inherited tests away would satisfy the check above while asserting
        # nothing the interface asked for.
        declared = sorted(
            name
            for name in vars(ExceedancePredictorConformance)
            if name.startswith("test_")
        )
        self.assertGreaterEqual(len(declared), 5)
        loader = unittest.TestLoader()
        for factory, owners in cases.items():
            for case in owners:
                self.assertLessEqual(
                    set(declared),
                    set(loader.getTestCaseNames(case)),
                    msg=(
                        f"{case.__name__} covers {factory.__name__} but does not "
                        f"run every conformance test"
                    ),
                )

    def test_every_exceedance_predictor_is_reachable_by_name_from_the_cli(self):
        """One assertion further over the same discovered set: the CLI can run it.

        `cli_eval.MODEL_FACTORIES` is the single name-to-factory mapping the
        `event-holdout` command selects through. This asserts the set of
        factories it can reach equals the set discovered across the package --
        both directions, because both failures are real. An implementer missing from
        the mapping is a model nobody outside this suite can run, which is the
        state the whole exceedance interface was in until the selector landed.
        A name in the mapping that no longer names a discovered implementer is a
        `--model` value that resolves to something the conformance suite never
        ran against.

        Identity, not name: the mapping records the factory object it
        constructs through, so a `--model arx` wired to the climatology fails
        here rather than looking correct because a key was spelled right.
        """

        implementations = _exceedance_implementations()
        reachable = {choice.factory for choice in cli_eval.MODEL_FACTORIES.values()}

        unreachable = sorted(
            name
            for name, factory in implementations.items()
            if factory not in reachable
        )
        self.assertEqual(
            unreachable,
            [],
            msg=(
                f"{unreachable} return an ExceedancePredictor from a module "
                f"of the repo_model package and no --model name reaches them. A "
                f"predictor the command line cannot construct is one only this "
                f"suite can run, and the conditional models sat in exactly "
                f"that state while the evaluator ran the null model"
            ),
        )

        discovered = set(implementations.values())
        dangling = sorted(
            name
            for name, choice in cli_eval.MODEL_FACTORIES.items()
            if choice.factory not in discovered
        )
        self.assertEqual(
            dangling,
            [],
            msg=(
                f"--model {dangling} names something that is not a discovered "
                f"ExceedancePredictor in the repo_model package"
            ),
        )


class RunProvenanceTests(unittest.TestCase):
    """What a published record says produced it, and what it refuses to say.

    `REPRODUCIBILITY.md`'s "Requirements for a reportable experiment" is this
    repository's own definition of when a number may be reported, and it lists
    eight things a run record must identify. The two records this repository
    emits satisfied the feature set and decision cutoff, the model
    configuration and seed, and the rolling-origin split and derived purge gap.
    Of the rest they carried the panel file's path and digest and nothing else.

    None of the rest was unrecorded. `data.write_daily_panel` writes every
    built panel with a `<panel>.manifest.json` beside it, carrying the build
    cutoff, the extent, the built and refused columns, the holes and
    `source_shas` -- the raw snapshot digests the panel was built from. Nothing
    read it. `grep -c manifest` returned nothing in every one of this track's
    modules. **A manifest nobody reads is a file, not a record.**

    Every fixture here is built in a temporary directory. Nothing under
    `data/raw/` or `data/processed/` is read and nothing is downloaded: the
    record's claims about a panel, a build, a registry and a threshold family
    are claims about bytes, and bytes are the one thing a test can make.

    Why the criterion is a mismatch and not a fields-are-present case
    ================================================================

    The build manifest records `"path": str(path)` and **no digest of the panel
    it describes**. So a manifest found beside a panel is a claim about a
    *name*, and the bytes under that name may have changed since -- the decay
    `backtest_document`'s own docstring rejects, in this repository, about this
    file. Binding on that path is what a reasonable person writes first and it
    is green on every well-formed input, including a manifest belonging to an
    entirely different build. A test asserting only that the section exists
    passes just as happily on provenance belonging to another panel.

    So the record binds by what the manifest does carry and the record already
    knows -- `row_count`, `start_date`, `end_date` -- and says in the artifact
    that the binding is by extent rather than by digest. The digest gap is
    `write_daily_panel`'s, it is Track A's to close, and it is reported rather
    than reached for.

    Mutation record
    ===============

    Run from a copy of the tree under `$HOME`, never the mount, with `-B` and
    `PYTHONDONTWRITEBYTECODE=1` and `__pycache__` cleared before each run --
    a stale cache has already produced one false result on this project.
    Control green before and after, zero `expectedFailure` throughout.

    **The mutation: bind on `manifest["path"]` alone.** `_bind_build_manifest`
    replaced by an equality check between the manifest's `path` and the panel
    the record names, with the extent comparison dropped. Every well-formed run
    still publishes, `panel.build_manifest` is still carried whole, and every
    other assertion in this class still holds.

    Killed, by exception type rather than by count:
    `test_a_manifest_that_does_not_describe_the_scored_panel_is_refused_rather_than_published`
    dies with `AssertionError: ProvenanceMismatchError not raised`, on each of
    the three extent fields and on both records. Its CLI counterpart in
    `tests/test_cli_eval.py`,
    `test_a_manifest_that_does_not_describe_the_panel_leaves_no_report_behind`,
    dies the same way -- the command exits 0 and writes the artifact.
    """

    #: The gap the fixture run is purged at. One day, because this class is
    #: about what a record says produced it and not about the gap; the gap has
    #: its own tests and a wider one here would only slow the fixture.
    PURGE = 1

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

        self.rows = regime_shift_frame()

        # The panel file. Written from the same rows both reports are built
        # over, so the file, the report and the manifest fixture are one story
        # rather than three. Its bytes are never parsed by a record -- they are
        # hashed -- but a fixture whose parts disagree teaches a reader the
        # wrong thing about what the record is claiming.
        self.panel = self.root / "panel.csv"
        self.panel.write_text(
            "\n".join(
                ["date,spread_bps"]
                + [
                    f"{row.date.isoformat()},{format(row.spread_bps, '.15g')}"
                    for row in self.rows
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        # The two declaration files. Neither is parsed by a record -- a record
        # identifies them by the digest of the bytes the run read -- so these
        # are as small as that claim allows. The registry the run is *given* is
        # `declared_registry`'s dict, as everywhere else in this file.
        self.registry = self.root / "sources.json"
        self.registry.write_text(
            json.dumps({"sources": {}}, indent=2) + "\n", encoding="utf-8"
        )
        self.thresholds = self.root / "stress_thresholds.json"
        self.thresholds.write_text(
            json.dumps({"taus_bp": list(EXCEEDANCE_TAUS)}, indent=2) + "\n",
            encoding="utf-8",
        )

    def manifest_path(self):
        """The name `write_daily_panel` gives the manifest, derived not typed."""

        return Path(str(self.panel) + ".manifest.json")

    def write_manifest(self, **overrides):
        """The manifest `write_daily_panel` would have left beside this panel.

        Every field is the one that writer records, in its shape: the extent as
        an integer and two ISO dates, the refusals and holes as objects, the
        snapshot digests as a list. Values are derived from the fixture, never
        read off a run. `overrides` is how a test states a disagreement, and it
        leaves `path` alone so a record binding on the path stays green.
        """

        manifest = {
            "path": str(self.panel),
            "build_cutoff": self.rows[-1].date.isoformat(),
            "decision_time": str(DECISION_TIME),
            "row_count": len(self.rows),
            "start_date": self.rows[0].date.isoformat(),
            "end_date": self.rows[-1].date.isoformat(),
            "built_columns": ["spread_bps"],
            "refused_columns": {},
            "holes": {},
            "source_shas": [hashlib.sha256(self.panel.read_bytes()).hexdigest()],
        }
        manifest.update(overrides)
        self.manifest_path().write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        return manifest

    def disagreements(self):
        """One wrong manifest field per element of the extent.

        Each derived from the fixture rather than typed, and each a value a
        real build could have produced -- an off-by-one row count, a start a
        day late, an end a day early. None of them touches `path`.
        """

        return (
            ("row_count", len(self.rows) + 1),
            ("start_date", (self.rows[0].date + timedelta(days=1)).isoformat()),
            ("end_date", (self.rows[-1].date - timedelta(days=1)).isoformat()),
        )

    def continuous_report(self):
        """A `BacktestReport` carrying the fixture's extent and little else.

        Constructed longhand, as `tests/test_cli_eval.py` does for the absent-
        conditions case: this class is about the provenance section, and a full
        rolling backtest would add a minute of fitting to say nothing more
        about it. The extent is the part the binding reads and it comes from
        the same rows the manifest fixture is derived from.
        """

        return BacktestReport(
            forecasts=[Forecast(1.0, 0.5, 0.0, 2.0, (0.0, 0.25, 0.5, 1.0, 2.0))],
            mae_bps=0.5,
            interval_coverage=1.0,
            panel_rows=len(self.rows),
            panel_first_date=self.rows[0].date,
            panel_last_date=self.rows[-1].date,
        )

    def exceedance_report(self):
        """A real pooled exceedance run over the fixture rows.

        Climatology rather than the ARX: the reference predictor is the cheap
        one and this class asserts nothing about skill.
        """

        return rolling_exceedance_backtest(
            self.rows,
            predictor=climatology_exceedance(
                minimum_history=EXCEEDANCE_MINIMUM_HISTORY
            ),
            model_name="climatology",
            features=FEATURES,
            registry=declared_registry(self.PURGE, FEATURES),
            decision_time=DECISION_TIME,
            taus=EXCEEDANCE_TAUS,
            minimum_history=EXCEEDANCE_MINIMUM_HISTORY,
        )

    def builders(self):
        """Both records this repository publishes, over the one fixture.

        Named together and asserted over together because the section under
        test is one section built in one place. A test exercising only the
        continuous record would pass on an exceedance record that grew nothing,
        which is the drift the shared builder exists to prevent.
        """

        continuous = self.continuous_report()
        exceedance = self.exceedance_report()
        self.assertEqual(exceedance.panel_rows, continuous.panel_rows)
        return (
            (
                "backtest_document",
                lambda: backtest_document(
                    continuous,
                    panel_path=self.panel,
                    registry_path=self.registry,
                    # The name is required now. These tests are about the
                    # provenance block and are indifferent to which model ran,
                    # so they name the one this fixture's report was built by.
                    model="persistence",
                ),
            ),
            (
                "exceedance_backtest_document",
                lambda: exceedance_backtest_document(
                    exceedance,
                    panel_path=self.panel,
                    registry_path=self.registry,
                    thresholds_path=self.thresholds,
                ),
            ),
        )

    def test_a_manifest_that_does_not_describe_the_scored_panel_is_refused_rather_than_published(
        self,
    ):
        """Publishing provenance that belongs to another build is refused.

        The acceptance criterion. A manifest beside the panel whose extent is
        not the scored panel's, with its `path` left correct so that a record
        binding on the name alone would publish it happily. The document call
        raises, so there is no document for a caller to write.

        The control is inside the test: the matching manifest publishes, and
        publishes under `panel.build_manifest`. Without it a binder that
        refused everything would pass.
        """

        for name, build in self.builders():
            with self.subTest(document=name):
                self.write_manifest()
                published = build()
                self.assertIn("build_manifest", published["panel"])

                for key, wrong in self.disagreements():
                    with self.subTest(field=key):
                        claimed = self.write_manifest(**{key: wrong})
                        # The manifest still names this panel. A record bound
                        # on `manifest["path"]` would find nothing wrong here,
                        # which is why the criterion is a mismatch case.
                        self.assertEqual(claimed["path"], str(self.panel))
                        self.assertNotEqual(claimed[key], published["panel"][
                            {
                                "row_count": "row_count",
                                "start_date": "first_date",
                                "end_date": "last_date",
                            }[key]
                        ])
                        with self.assertRaises(ProvenanceMismatchError):
                            build()

    def test_the_build_manifest_is_carried_whole_and_bound_by_extent(self):
        """The manifest is embedded as it is, and the binding names its limit.

        Carried rather than re-keyed: the manifest's schema is Track A's, and a
        record that selected or renamed fields would be a second copy of a
        schema this module does not own -- agreeing today, drifting the first
        time a field is added there. Carrying it whole is also how this record
        gains every future field for free, which is asserted by embedding an
        extra key the reader has never heard of and finding it in the record.
        """

        written = self.write_manifest(a_field_track_b_has_never_heard_of=True)
        for name, build in self.builders():
            with self.subTest(document=name):
                panel = build()["panel"]
                self.assertEqual(panel["build_manifest"], written)

                binding = panel["build_manifest_binding"]
                self.assertEqual(binding["kind"], "extent")
                self.assertEqual(
                    binding["compared"], ["row_count", "first_date", "last_date"]
                )
                # The record says what it did not check. A reader who finds a
                # manifest embedded beside a digest would otherwise assume the
                # two were checked against each other.
                self.assertIn("no digest", binding["note"])

                # And nothing the record already carried was weakened.
                self.assertEqual(panel["path"], str(self.panel))
                self.assertEqual(
                    panel["sha256"],
                    hashlib.sha256(self.panel.read_bytes()).hexdigest(),
                )

    def test_a_panel_with_no_build_manifest_carries_no_stand_in_for_one(self):
        """No manifest, no section. Not `null`, not `{}`, not `"none"`.

        A fixture panel has no build behind it and a record that says so by
        omission is honest; one that says so with a stand-in invites a reader
        to think the field was computed. The rule `backtest_document` already
        follows for `decision_time` and `minimum_history`, unchanged here.
        """

        self.assertFalse(self.manifest_path().exists())
        for name, build in self.builders():
            with self.subTest(document=name):
                document = build()
                self.assertNotIn("build_manifest", document["panel"])
                self.assertNotIn("build_manifest_binding", document["panel"])
                self.assertNotIn("null", json.dumps(document["panel"]))
                self.assertNotIn("null", json.dumps(document["provenance"]))

    def test_the_declaration_files_are_identified_by_the_digest_of_what_was_read(self):
        """Registry and thresholds, by path and `sha256`, as the panel is.

        `REPRODUCIBILITY.md` asks for "the source-registry and stress-threshold
        versions". Neither file carries a version field, and a digest is the
        version of a file that carries none: it changes exactly when the bytes
        change and it cannot be typed wrong. The expected digests are computed
        here from the fixture files, so this compares the record against the
        bytes rather than against a second call of the same helper.

        The continuous benchmark takes no `--thresholds` and its record says so
        by omission rather than by naming a file it never opened.
        """

        registry_digest = hashlib.sha256(self.registry.read_bytes()).hexdigest()
        thresholds_digest = hashlib.sha256(self.thresholds.read_bytes()).hexdigest()

        continuous, exceedance = (build() for _name, build in self.builders())

        for document in (continuous, exceedance):
            source_registry = document["provenance"]["inputs"]["source_registry"]
            self.assertEqual(source_registry["path"], str(self.registry))
            self.assertEqual(source_registry["sha256"], registry_digest)

        self.assertNotIn("stress_thresholds", continuous["provenance"]["inputs"])
        stress = exceedance["provenance"]["inputs"]["stress_thresholds"]
        self.assertEqual(stress["path"], str(self.thresholds))
        self.assertEqual(stress["sha256"], thresholds_digest)

        # A digest that did not come from these bytes would still be a digest.
        self.assertNotEqual(registry_digest, thresholds_digest)

    def test_the_commit_is_never_recorded_without_the_state_of_its_tree(self):
        """A commit id read from a modified tree names code that did not run.

        So the tree is checked in the same breath and the answer is carried
        whichever way it came out: `tree_modified` is present and `False` on a
        clean tree, because a reader must be able to tell "checked, and clean"
        from "not checked", and an omitted field cannot say the first.

        `tree_modified` counts **tracked** modifications, and untracked files
        are reported beside it under their own name -- see
        `RecordGitStateTests`, which owns that split and proves it on a
        purpose-built repository. This test asserts the same two fields against
        this checkout, whatever state it happens to be in: the expectations are
        derived by running `git` from the test rather than read off the
        record's own helper, and both are asserted so a checkout that is clean
        today cannot let half the pair go unchecked.

        Skipped where git is absent, which is the case the record answers by
        omitting the section entirely.
        """

        def git(*arguments):
            return subprocess.run(
                ("git", *arguments),
                cwd=SAMPLE_PANEL.parents[2],
                capture_output=True,
                text=True,
                check=True,
            ).stdout

        try:
            commit = git("rev-parse", "HEAD").strip()
            status = git("status", "--porcelain", "--untracked-files=no")
            untracked = git("ls-files", "--others", "--exclude-standard")
        except (OSError, subprocess.SubprocessError):  # pragma: no cover
            self.skipTest("git is not available here; the record omits the section")

        for name, build in self.builders():
            with self.subTest(document=name):
                code = build()["provenance"]["code"]
                self.assertEqual(code["commit"], commit)
                self.assertIn("tree_modified", code)
                self.assertIs(code["tree_modified"], bool(status.strip()))
                self.assertIn("untracked_files_present", code)
                self.assertIs(
                    code["untracked_files_present"], bool(untracked.strip())
                )

    def test_the_new_arguments_are_required_and_undefaulted(self):
        """A default here publishes a record missing its provenance.

        With every other field correct, which is the trap `--model` having no
        default was written to prevent one block ago. Read off the signatures,
        because a default is a property of the function and not of a run.
        """

        required = {
            baseline.backtest_document: ("panel_path", "registry_path"),
            baseline.exceedance_backtest_document: (
                "panel_path",
                "registry_path",
                "thresholds_path",
            ),
        }
        for function, names in required.items():
            parameters = inspect.signature(function).parameters
            for name in names:
                with self.subTest(function=function.__name__, argument=name):
                    parameter = parameters[name]
                    self.assertIs(parameter.kind, inspect.Parameter.KEYWORD_ONLY)
                    self.assertIs(parameter.default, inspect.Parameter.empty)


class RecordGitStateTests(unittest.TestCase):
    """`tree_modified` answers a question about code, not about housekeeping.

    The finding, observed rather than reasoned. The two records published on
    9 September 2026 were produced minutes apart, from `568c9ba`, in one tree,
    with nothing about the code changed between them. They disagree:

    | record                                        | `tree_modified` |
    |-----------------------------------------------|-----------------|
    | `docs/runs/persistence_funding.json`          | `false`         |
    | `docs/runs/exceedance_funding_climatology.json` | `true`        |

    What changed is that by the time the second ran, the first was sitting
    untracked beside it. `_code_provenance` asked `git status --porcelain`,
    which reports untracked files with `??`, and read any output at all as a
    modified tree -- so a record published into the repository made the *next*
    record report a modified tree, and because these records are written into
    `docs/runs/`, only the first record produced in a clean checkout could ever
    report `False`.

    The failure mode is the worse direction. A reader who sees
    `tree_modified: true` on nearly every record learns to ignore the field,
    and then the one record that carries it because somebody really did run
    from an edited working tree says nothing, because the signal has been
    drowned by its own siblings. A guard that fires on everything is a guard
    that fires on nothing -- this repository's own recurring finding, pointed
    at a field rather than at a test.

    So the question is split and both halves are kept: `tree_modified` counts
    tracked modifications only, and `untracked_files_present` reports the rest
    under a name no reader can mistake for a synonym of it. Suppressing the
    untracked signal entirely would have been a loosening rather than a
    scoping; publishing the file *names* would have put a developer's scratch
    files into a published record.

    This class builds its own git repository rather than reading this one,
    because the states it has to assert are states this checkout cannot be put
    into on demand -- and because a fixture that special-cased `docs/runs/`
    would be testing the one implementation the block forbids.

    Mutation record, the untracked sibling
    --------------------------------------

    Run in a disposable copy of the tree under `$HOME` -- never in the mount --
    carrying `data/`, `.github/`, `metadata/`, `.gitignore`, the root Markdown
    and `docs/PROJECT_STATUS.md`, with `__pycache__` cleared, stdlib only,
    under `-B` with `PYTHONDONTWRITEBYTECODE=1`. Unmutated control green before
    and after.

      * **`--untracked-files=no` dropped** from `_code_provenance`'s status
        call, restoring the behaviour that produced the two disagreeing
        records. Kills exactly 1 --
        `RecordGitStateTests::test_an_untracked_sibling_does_not_make_the_tree_modified`,
        and inside it exactly the `state='untracked sibling'` subtest:
        `AssertionError: True is not False : an untracked record beside the one
        being written is not code that did not run`. The `clean` and `tracked
        file modified` subtests stay green under it, which is what says the
        fixture isolates the untracked case rather than merely noticing that
        something moved.

        Note the shape of the control here: in the copy under `$HOME` there is
        no enclosing git repository, so `_code_provenance` returns `None` and
        `RunProvenanceTests`' checkout-reading sibling skips itself. This class
        is unaffected, because it supplies its own repository -- which is the
        argument for building one instead of reading the tree the suite is run
        from.
    """

    def _git(self, *arguments):
        subprocess.run(
            ("git", *arguments),
            cwd=self.repository,
            capture_output=True,
            text=True,
            check=True,
        )

    def setUp(self):
        try:
            subprocess.run(
                ("git", "--version"), capture_output=True, check=True
            )
        except (OSError, subprocess.SubprocessError):  # pragma: no cover
            self.skipTest("git is not available here; the record omits the section")

        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.repository = Path(directory.name).resolve()

        self._git("init", "--quiet")
        # On the repository, not on the machine: the fixture must not depend on
        # whoever's git config the suite happens to run under, and must not
        # write to it either.
        self._git("config", "user.email", "fixture@example.invalid")
        self._git("config", "user.name", "Fixture")
        self._git("config", "commit.gpgsign", "false")

        (self.repository / "tracked.txt").write_text("one\n", encoding="utf-8")
        self._git("add", "tracked.txt")
        self._git("commit", "--quiet", "-m", "one")

        # `_code_provenance` runs git at the module-level repository root.
        # Point it at the fixture for the duration of the test and put it back
        # afterwards, so a failure cannot leave the constant redirected for
        # everything that runs next.
        original = baseline._REPOSITORY_ROOT
        self.addCleanup(setattr, baseline, "_REPOSITORY_ROOT", original)
        baseline._REPOSITORY_ROOT = self.repository

    def test_an_untracked_sibling_does_not_make_the_tree_modified(self):
        """**The acceptance criterion.** Three states, and they only mean
        something together.

        A record written into the repository must not be what makes the next
        record say the tree was modified. State 2 is the finding. State 1 is
        the reason the field is present-and-`False` rather than omitted: a
        reader must be able to tell "checked, and clean" from "not checked".
        State 3 is not padding -- without it this test passes on an
        implementation that hardcodes `False`, which is the shortest wrong fix
        available and the one a hurry produces.

        The untracked file is named like a run record because that is what it
        is about: the sibling in `docs/runs/` that the second published record
        was standing next to. Nothing in the implementation may notice the
        name, and nothing here checks that it does.
        """

        head = subprocess.run(
            ("git", "rev-parse", "HEAD"),
            cwd=self.repository,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

        with self.subTest(state="clean"):
            code = baseline._code_provenance()
            self.assertEqual(code["commit"], head)
            self.assertIs(code["tree_modified"], False)
            self.assertIs(code["untracked_files_present"], False)

        (self.repository / "persistence_funding.json").write_text(
            "{}\n", encoding="utf-8"
        )

        with self.subTest(state="untracked sibling"):
            code = baseline._code_provenance()
            self.assertIs(
                code["tree_modified"],
                False,
                "an untracked record beside the one being written is not code "
                "that did not run",
            )
            self.assertIs(code["untracked_files_present"], True)

        (self.repository / "tracked.txt").write_text("two\n", encoding="utf-8")

        with self.subTest(state="tracked file modified"):
            code = baseline._code_provenance()
            self.assertIs(
                code["tree_modified"],
                True,
                "an edited tracked file is exactly what this field is for",
            )


#: The constant separating the two fitters in `PairedComparisonTests`. Small
#: beside the fixture's daily move -- see `rising_frame` -- so that every
#: per-origin error is larger than it and `|e| - |e - OFFSET_BPS|` is exactly
#: `OFFSET_BPS` at every origin rather than only at most of them.
OFFSET_BPS = 3.0

#: The gap the comparison fixtures are priced at. Any gap works; this one is
#: pinned so the reader can see the paired difference does not depend on it.
COMPARISON_PURGE = 2

#: The trailing window the residual-law side of the CRPS comparison is fitted
#: at. It has to be shorter than the residuals the *shortest* training frame
#: carries -- a 20-row frame carries 19 -- or `fit_rolling_residual_law`
#: refuses the fit; and it has to be short enough that the windowed law and the
#: expanding full-sample law are actually different samples, because a window
#: covering the whole frame is persistence's own law under a challenger's name
#: and the two sides would then agree under every loss including this one.
CRPS_COMPARISON_WINDOW = 5

#: The seed the CRPS comparison draws its resample from. A literal is right
#: here and wrong in the CLI: `comparison_seed` derives the published one from
#: the run's identity, and a test that called it would be restating that
#: derivation rather than testing the loss.
CRPS_COMPARISON_SEED = 20260910


def rising_frame(count=44, seed=20260909):
    """A panel that rises every day, by a varying amount that is never small.

    Two properties, and the test needs both.

    **Every increment is at least 25 bp**, which is far more than `OFFSET_BPS`.
    Persistence forecasts the last spread it was allowed to see, so on a rising
    panel it always under-predicts, and the error at every origin exceeds the
    offset. That is what makes `|e| - |e - c|` collapse to `c`: with `e >= c`
    the two absolute values are `e` and `e - c`, and the fixture guarantees the
    inequality rather than hoping for it.

    **The increments vary**, so the loss series itself varies across origins.
    That is not decoration. If every origin carried the same loss, the two
    models bootstrapped *independently* would still return the same endpoints,
    and the acceptance test would pass under the very mutation it exists to
    catch. The fixture has to make the losses move and the difference stand
    still.

    Values are exact in binary. `spread_bps` is `100 * (sofr - iorb)`, so
    `iorb` is zero and `sofr` is a multiple of `0.25`: the spread is then an
    exact integer number of basis points, every subtraction below is exact, and
    the test can assert equality rather than closeness. A fixture that produced
    5.0000000000000004 would force `assertAlmostEqual`, which is a weaker
    statement than the degenerate interval this test is making.
    """

    rows = []
    quarters = 0
    state = seed
    for index in range(count):
        state = (1103515245 * state + 12345) % (2 ** 31)
        quarters += 1 + (state >> 16) % 5
        rows.append(
            DailyObservation(
                date(2026, 1, 1) + timedelta(days=index),
                {"sofr": 0.25 * quarters, "iorb": 0.0},
            )
        )
    return rows


class _OffsetForecast:
    """A fitted model that is another one plus a constant on its centre.

    A test double and not a model: it exists so that two fitters can be handed
    to one comparison whose forecasts differ by a known constant on every
    origin, which is the only construction under which the paired difference
    has zero variance and the expected interval can be *derived* rather than
    read off a run.

    It delegates everything else, including `features_read`, so the offset side
    declares exactly what persistence declares and both sides price the same
    gap. A double that reported a wider feature set would be refused by
    `_check_fitter_stayed_inside`, which would be that guard working and this
    fixture being wrong.
    """

    def __init__(self, inner, offset):
        self._inner = inner
        self._offset = offset
        self.cutoff = inner.cutoff
        self.levels = inner.levels

    @property
    def residuals(self):
        return self._inner.residuals

    @property
    def features_read(self):
        return self._inner.features_read

    def trained_beyond(self, feature_row):
        return self._inner.trained_beyond(feature_row)

    def point_forecast(self, feature_row):
        return self._inner.point_forecast(feature_row) + self._offset

    def predict(self, feature_row):
        return tuple(
            value + self._offset for value in self._inner.predict(feature_row)
        )

    def predict_stress(self, feature_row, taus=None):
        return self._inner.predict_stress(feature_row, taus)


def offset_fitter(offset=OFFSET_BPS):
    """`fit`, with `offset` added to every point forecast it will make."""

    def fit_offset(train_frame, minimum_history=20):
        return _OffsetForecast(
            fit(train_frame, minimum_history=minimum_history), offset
        )

    return fit_offset


class PairedComparisonTests(unittest.TestCase):
    """A comparison is not two runs, and an interval on it is not two intervals.

    **The finding.** `PLAN.md` Phase 2 exits on *"a model that beats
    persistence out of sample"*, and until this block the repository could not
    state either half of that. `mae_bootstrap_interval` names the hazard in its
    own docstring -- a single MAE "invites a reader to believe that a
    difference between two models is real" -- and then the only thing available
    to a reader with two models was two such intervals and the overlap between
    them. Overlap answers a different question and answers it wrongly in both
    directions: overlapping intervals routinely contain a real difference, and
    separated ones can be produced by a shared shock that cancels in the
    difference.

    So `paired_model_comparison` scores both models in one fold loop, on the
    same training rows and the same origin, and puts **one** draw of indices
    through the differenced series. The exceedance path already had this
    property -- `brier_skill_score`'s bootstrap applies one draw to the model
    and its reference together -- and this is the continuous path's version.

    Decisions
    ---------

    **The pairing is by construction, not by comparison of two files.** Two
    published records carry metrics and not per-origin losses, deliberately, so
    they cannot be differenced after the fact -- and adding the losses to them
    so that they could would turn the record from a publication into an
    intermediate. One loop makes the two series the same length, in the same
    order, over the same days, and nothing has to be checked because nothing
    could have differed.

    **Two declarations, one gap.** Each model declares its own feature set,
    because an ARX reads columns persistence does not and one shared
    declaration would either over-purge the simpler model or leave the richer
    one's columns unpriced. The gap is the one thing the single loop cannot
    settle, since it is derived from each declaration before any fold exists,
    so a comparison whose sides price different gaps is refused --
    `IncomparablePurgeError`. Two gaps are two origin sets, and losses at
    different origins are not paired however carefully they are subtracted.

    **The sign convention, and why it is in the artifact.** The difference is
    `loss(model_a) - loss(model_b)` at each origin, so a positive mean means
    `model_a` carried the larger loss and `model_b` was the more accurate of
    the two. `model_a` is written first because that is the order the flags
    read and the order the sentence reads, and the sentence is rendered from
    the two names the run was given *and the loss it was taken over* and
    published in the record: *a signed difference with no statement of
    direction is a number half its readers will read as the opposite
    conclusion, and a docstring is not shipped with the record while the record
    is what a later reader has.*

    **The loss is selectable, and the reason is a reproduced finding.** On the
    sample panel, `compare --model-a persistence --model-b rolling-residual
    --residual-window-b 5` reported `mean_difference_bps` of `0.0` with a
    `[0.0, 0.0]` interval. The two models are the *same point rule* --
    `FittedRollingResidualLaw.point_forecast` returns the last observed spread,
    which is persistence's -- and differ only in the residual sample the
    predictive law is read off. A paired absolute error can only ever see the
    centre, so it reported the challenger as identical to the benchmark on
    exactly the property the challenger changes. `backtest` already separated
    the pair, through `crps_bps`. So `--loss crps` scores each side's whole
    quantile vector through `metrics.crps_from_quantiles` on the contract's
    grid -- the same call `rolling_persistence_backtest` makes, so the two
    commands cannot disagree about what CRPS is -- and `absolute-error` stays
    the default, which is what keeps every record under `docs/runs/` meaning
    what it meant.

    **Coverage was the other candidate and is not a loss.** An interval from
    minus infinity to plus infinity covers every origin, so a paired coverage
    difference is maximised by the model that says least. CRPS is proper, reads
    the whole law, and reduces to absolute error for a point mass, so the two
    entries in `baseline.COMPARISON_LOSSES` are one functional evaluated on
    progressively more of the forecast rather than two unrelated numbers.

    **The seed deliberately does not carry the loss**, though
    `comparison_seed`'s own docstring argues that two records reporting
    different things should not silently share a resample stream. Two losses
    over one declaration score *the same origins*: the bootstrap draws origin
    indices, and one draw reaching both loss series is the same property the
    pairing itself rests on. Adding the loss to the seed material would also
    change the published seed of every absolute-error record already under
    `docs/runs/`, which is a rewrite of a record of a run that happened.

    **What the interval does not license.** The record reports a difference and
    an interval around it and stops there. `REPRODUCIBILITY.md`'s
    "Interpretation boundary" is this project's standing statement on what a
    reader may conclude from that, and neither the code nor these tests say
    anything about it.

    Mutation record
    ---------------

    Disposable copy under `$HOME`, never the mount, carrying `src/`, `tests/`,
    `data/`, `.github/`, `metadata/`, `.claude/`, `.gitignore`, the root
    Markdown and `docs/PROJECT_STATUS.md`. `PYTHONDONTWRITEBYTECODE=1` and
    `python3 -B`, `__pycache__` cleared between runs, unmutated control green
    before and after each mutation. Exception types recorded, not counts.

    `.claude/` is copied because the ownership hook lives there and its test
    contributes seven errors to an otherwise green control without it. The copy
    list in `CLAUDE.md` predates the hook and does not name it; that is a
    `HUMAN_ONLY` page, so it is reported rather than edited.

    **Two more paths are missing from that list, found the same way.**
    `notebooks/` and `examples/` are read by `tests/test_generated_results.py`,
    and a copy without them fails with `FileNotFoundError:
    notebooks/01_portfolio_walkthrough.ipynb` -- a red control that looks like
    a finding and is a missing directory, which is the exact shape `.claude/`
    had. `pyproject.toml` belongs there too: the docs-freshness guard reads the
    Python version out of it. The full list this class's mutations were run
    under is `src/`, `tests/`, `data/`, `.github/`, `.claude/`, `metadata/`,
    `docs/`, `scripts/`, `notebooks/`, `examples/`, `.gitignore`,
    `pyproject.toml` and the root Markdown. Reported, not edited: `CLAUDE.md`
    is `HUMAN_ONLY`.

      1. **Each model's loss series bootstrapped with its own index draw**, and
         the point estimates and endpoints differenced afterwards --
         `stationary_bootstrap_interval` called twice, on `losses_a` and
         `losses_b`, with `seed` and `seed + 1`, returning
         `(lower_a - lower_b, upper_a - upper_b)`. This is the defect the block
         exists to prevent and it is the one a green suite hides: every other
         test in the suite stays green under it, because the models really were
         both scored at every origin and every other published field is
         correct. Kills exactly 1 --
         `test_one_resample_is_applied_to_both_models_so_a_constant_difference_has_a_degenerate_interval`,
         `AssertionError: Tuples differ: (3.0, 1.863636363636374) != (3.0,
         3.0)`. **This is the acceptance criterion and the mutation target, and
         they did not come apart.**

         The degenerate case is what makes the kill unambiguous. A numeric
         interval pinned from a run would agree with any mutation that moved
         the run and the literal together; a constant difference has zero
         variance, so *any* resample of it returns the constant, and an
         interval that is not degenerate here is an interval that resampled the
         two models apart.

         **Note which endpoint moved.** The lower endpoint came back at exactly
         `3.0` under the mutation and only the upper one moved, which is
         coincidence and not structure: two independent resamples of two loss
         series that differ by a constant can agree at one percentile and not
         at the other. Recorded because the kill would look stronger written as
         "both endpoints moved", and because a later reader tightening this
         test to assert only the lower endpoint would blunt it to nothing.

      2. **The gap refusal removed** -- `IncomparablePurgeError` never raised,
         the comparison continuing on `purge_a`. Kills exactly 2 --
         `test_two_declarations_pricing_different_gaps_are_refused` here,
         `AssertionError: IncomparablePurgeError not raised`, and
         `test_cli_eval.PairedComparisonCommandTests.test_two_declarations_pricing_different_gaps_are_refused_by_the_command`,
         `AssertionError: 0 != 2`. That second number is the finding rather
         than the test: the command **succeeds** and publishes a comparison
         record, because the `b` side is scored at the `a` side's origins and
         every loss in it is a real loss from a real fit. Nothing in the
         artifact disagrees with itself, which is why this is a refusal and not
         a warning.
      3. **The CRPS path handed a degenerate quantile vector** -- the point
         forecast repeated at every declared level, `crps_from_quantiles(levels,
         tuple(point for _ in levels), actual)` in `_crps_at` in place of
         `fitted.predict(feature_row)`. **This is the selectable-loss block's
         acceptance mutation, and its target is the acceptance test**; they did
         not come apart.

         It is the trap the whole test is shaped around, because it is the one
         wrong implementation that *looks right*. A point mass's CRPS is
         exactly its absolute error -- `2 * mean pinball` over any grid
         collapses to `|actual - point|` when every level predicts the same
         number -- so this mutation returns the absolute-error series under the
         CRPS heading, reports `0.0` again for two models sharing a point rule,
         and is indistinguishable from a correct implementation that happened
         to find no difference.

         Kills exactly 2, both `AssertionError`:
         `test_the_crps_loss_separates_models_that_share_a_point_rule`,
         `AssertionError: 0.0 == 0.0 : the two laws differ, so a proper loss
         that reads the whole forecast must separate them`; and
         `test_cli_eval.PairedComparisonCommandTests.test_the_loss_flag_reaches_the_record_and_defaults_to_the_point_loss`,
         `AssertionError: 0.0 == 0.0`. The per-origin recomputation in the
         acceptance test would have caught it too, from the other side -- it
         asserts what the loss *is* rather than that it moved -- but the
         separation assertion is reached first.

      4. **Each side's mean published under a fixed `mae_bps` heading**
         regardless of loss, `"mae_bps": comparison.mean_loss_a_bps` in
         `paired_comparison_document`. Kills 3 assertions across 2 tests, and
         the two exception types are the finding: `KeyError: 'crps_bps'` from
         `test_the_record_names_the_loss_the_difference_was_taken_over`'s
         `loss='crps'` subtest, then `AssertionError: 'mae_bps' unexpectedly
         found` from the same test, and `AssertionError: 'crps_bps' not found
         in {'mae_bps': ..., 'model': 'persistence'}` at the command layer.

         Recorded because the mutated record is *self-consistent*: its `loss`
         field says `crps_bps`, its sign convention says `crps_bps`, and the
         number beside them is a real mean CRPS. Only the heading lies, and a
         heading that names a mean absolute error while carrying a CRPS is a
         number that parses, reads correctly, and is a different quantity.

      5. **An unimplemented loss silently defaulted** --
         `COMPARISON_LOSSES.get(loss, COMPARISON_LOSSES[DEFAULT_COMPARISON_LOSS])`
         in `_select_comparison_loss`. Kills exactly 1 --
         `test_a_loss_this_module_does_not_implement_is_refused`,
         `AssertionError: ValueError not raised`. The run it enables publishes
         a record whose `loss` field is accurate and whose numbers answer a
         question nobody asked.

    """

    def _comparison(
        self,
        rows=None,
        features_b=FEATURES,
        registry=None,
        seed=20260909,
        **kwargs,
    ):
        return paired_model_comparison(
            rows if rows is not None else rising_frame(),
            model_a="persistence",
            fit_a=fit,
            features_a=FEATURES,
            model_b="persistence-plus-offset",
            fit_b=offset_fitter(),
            features_b=features_b,
            registry=registry
            if registry is not None
            else declared_registry(COMPARISON_PURGE),
            decision_time=DECISION_TIME,
            seed=seed,
            **kwargs,
        )

    def test_one_resample_is_applied_to_both_models_so_a_constant_difference_has_a_degenerate_interval(
        self,
    ):
        """The block's acceptance criterion, derived from the fixture.

        `model_b` is `model_a` plus `OFFSET_BPS` on every point forecast, and
        `rising_frame` guarantees every error exceeds the offset, so the
        per-origin loss difference is `OFFSET_BPS` at every origin. A series
        with zero variance has the same mean under every resample of it, so a
        bootstrap that applies one draw of origins to both models must return
        that constant at both endpoints. Nothing here is read off a run: the
        expected value comes from how the fixture was built.
        """

        comparison = self._comparison()

        # The fixture's own precondition, asserted rather than assumed: if the
        # losses did not move, two independently drawn resamples would agree
        # too and the assertions below would hold under the mutation they are
        # aimed at.
        self.assertGreater(
            len(set(comparison.losses_a)),
            1,
            "the fixture's losses must vary across origins, or an interval "
            "that resampled the two models apart would be degenerate as well "
            "and this test would pass on the defect it exists to catch",
        )

        self.assertEqual(
            set(comparison.differences),
            {OFFSET_BPS},
            "model_b is model_a plus a constant on a panel where the error "
            "always exceeds that constant, so every paired difference is the "
            "constant",
        )
        self.assertEqual(comparison.mean_difference_bps, OFFSET_BPS)
        self.assertEqual(
            comparison.difference_interval,
            (OFFSET_BPS, OFFSET_BPS),
            "a difference series with zero variance has the same mean under "
            "every resample of it, so one draw applied to both models collapses "
            "the interval onto the constant; an interval that is not degenerate "
            "here resampled the two models independently",
        )

    def test_the_crps_loss_separates_models_that_share_a_point_rule(self):
        """The selectable-loss block's acceptance criterion: a point loss cannot see a law.

        `persistence` and `rolling-residual` are the same point rule -- the last
        observed spread, and `FittedRollingResidualLaw.point_forecast` says so
        in those words. They differ only in the sample the predictive
        distribution is read off: every residual in the expanding frame against
        the last `CRPS_COMPARISON_WINDOW` of them. Under absolute error that
        difference is invisible, and `compare` reported it as invisible on the
        sample panel -- `mean_difference_bps` of `0.0` with a `[0.0, 0.0]`
        interval, which reads as "these models are identical" and is really
        "this instrument reads only the centre". `backtest` already separated
        the pair through `crps_bps`.

        So both halves are asserted here in one test, because the finding is
        the *pair* of them: the point loss must still report exactly zero (or
        the fixture is not two models sharing a point rule and the second half
        proves nothing), and the distributional loss must not.

        The third assertion is what makes the second one mean something.
        A point mass's CRPS **is** its absolute error, so a CRPS path that
        handed `crps_from_quantiles` a degenerate vector -- the point forecast
        repeated at every level -- would return the absolute-error series
        again, report zero again, and look like a correct implementation that
        happened to find no difference. The per-origin losses are therefore
        recomputed here from each side's own `predict` output, on the dates the
        run published, so that the test states what the loss *is* and not
        merely that it moved.
        """

        rows = rising_frame()

        def compare(loss):
            return paired_model_comparison(
                rows,
                model_a="persistence",
                fit_a=fit,
                features_a=FEATURES,
                model_b="rolling-residual",
                fit_b=partial(
                    fit_rolling_residual_law, window=CRPS_COMPARISON_WINDOW
                ),
                features_b=FEATURES,
                registry=declared_registry(COMPARISON_PURGE),
                decision_time=DECISION_TIME,
                seed=CRPS_COMPARISON_SEED,
                loss=loss,
            )

        point = compare("absolute-error")
        self.assertGreater(
            len(point.folds),
            1,
            "several origins, or a difference of zero would be one origin's "
            "coincidence rather than a property of the two point rules",
        )
        self.assertEqual(
            set(point.differences),
            {0.0},
            "the two models share a point rule, so every paired absolute-error "
            "difference is exactly zero -- this is the fixture's precondition "
            "for the assertions below, not a result",
        )
        self.assertEqual(point.mean_difference_bps, 0.0)

        law = compare("crps")
        self.assertNotEqual(
            law.mean_difference_bps,
            0.0,
            "the two laws differ, so a proper loss that reads the whole "
            "forecast must separate them; zero here is a CRPS computed from "
            "the point forecast, whose CRPS is its absolute error",
        )

        # The dates come off the published folds rather than from a second walk
        # of the splitter: what the run scored is a claim the record makes, and
        # `test_each_side_is_scored_exactly_as_the_single_model_benchmark_scores_it`
        # is what checks that claim. Here they are taken as given so that the
        # only thing this loop re-derives is the loss.
        by_date = {row.date: row for row in rows}
        for position, fold in enumerate(law.folds):
            train_frame = [
                row
                for row in rows
                if fold.train_start <= row.date <= fold.train_end
            ]
            feature_row = by_date[fold.feature_date]
            actual = by_date[fold.scored_date].spread_bps
            fitted_a = fit(train_frame)
            fitted_b = fit_rolling_residual_law(
                train_frame, window=CRPS_COMPARISON_WINDOW
            )
            with self.subTest(scored=fold.scored_date):
                self.assertEqual(
                    law.losses_a[position],
                    crps_from_quantiles(
                        QUANTILE_LEVELS, fitted_a.predict(feature_row), actual
                    ),
                )
                self.assertEqual(
                    law.losses_b[position],
                    crps_from_quantiles(
                        QUANTILE_LEVELS, fitted_b.predict(feature_row), actual
                    ),
                )

    def test_the_record_names_the_loss_the_difference_was_taken_over(self):
        """A signed difference is a difference *of something*, in the file.

        The direction was already published because a number a reader can get
        backwards is a number half its readers get backwards. The loss is the
        same argument one step out: two records reporting the same figure, one
        a gap in absolute error and the other a gap in CRPS, are incomparable,
        and nothing on the page would say so.

        `mae_bps` is checked *absent* from the CRPS record. A mean CRPS
        published under a heading that names a mean absolute error parses,
        reads correctly, and is a different quantity -- the failure the
        heading-per-loss exists to prevent.
        """

        rows = load_daily_panel(SAMPLE_PANEL)
        for loss, name, statistic in (
            ("absolute-error", baseline.COMPARISON_LOSS, "mae_bps"),
            ("crps", baseline.CRPS_COMPARISON_LOSS, "crps_bps"),
        ):
            with self.subTest(loss=loss):
                comparison = paired_model_comparison(
                    rows,
                    model_a="persistence",
                    fit_a=fit,
                    features_a=FEATURES,
                    model_b="rolling-residual",
                    fit_b=partial(
                        fit_rolling_residual_law, window=CRPS_COMPARISON_WINDOW
                    ),
                    features_b=FEATURES,
                    registry=declared_registry(COMPARISON_PURGE),
                    decision_time=DECISION_TIME,
                    seed=CRPS_COMPARISON_SEED,
                    loss=loss,
                )
                document = paired_comparison_document(
                    comparison, panel_path=SAMPLE_PANEL, registry_path=REAL_REGISTRY
                )
                published = document["comparison"]

                self.assertEqual(published["loss"], name)
                self.assertIn(name, published["sign_convention"])
                self.assertEqual(
                    published["model_a"][statistic], comparison.mean_loss_a_bps
                )
                self.assertEqual(
                    published["model_b"][statistic], comparison.mean_loss_b_bps
                )

        self.assertNotIn("mae_bps", published["model_a"])

    def test_a_loss_this_module_does_not_implement_is_refused(self):
        """Refused, not quietly defaulted, and refused before anything is fitted.

        A comparison handed an unimplemented loss and given the absolute error
        instead would publish a record whose `loss` field is accurate and whose
        numbers answer a question nobody asked. The refusal names what is
        available so the caller does not have to read this module to find out.
        """

        with self.assertRaises(ValueError) as caught:
            self._comparison(loss="coverage")

        message = str(caught.exception)
        self.assertIn("coverage", message)
        for available in baseline.COMPARISON_LOSSES:
            self.assertIn(repr(available), message)

    def test_two_declarations_pricing_different_gaps_are_refused(self):
        """Different gaps are different origins, and different origins do not pair.

        The one comparability question the single fold loop does not settle,
        because the gap is derived from the declaration before the loop exists.
        Refused before the panel is walked, so nothing is fitted and no
        artifact can be written.
        """

        registry = {
            source: {
                "release_lag": {
                    "basis": "record_date",
                    "unit": "calendar_days",
                    "days": days,
                    "available_time": "00:00",
                    "timezone": "America/New_York",
                }
            }
            for days, features in ((1, FEATURES), (6, ("treasury_settlement",)))
            for source in sources_for_features(features)
        }

        with self.assertRaises(baseline.IncomparablePurgeError) as caught:
            self._comparison(
                features_b=FEATURES + ("treasury_settlement",), registry=registry
            )

        message = str(caught.exception)
        self.assertIn("1-day", message)
        self.assertIn("6-day", message)
        self.assertIn("treasury_settlement", message)

    def test_each_side_is_scored_exactly_as_the_single_model_benchmark_scores_it(self):
        """The comparison's folds and per-model MAE are the benchmark's own.

        The pairing is worth nothing if either side is scored differently from
        the way `rolling_persistence_backtest` scores it, because then the
        difference is between one model and a variant of another. Checked
        against a separate benchmark run at the same gap, on the `a` side,
        which is the side that has one to compare against.
        """

        rows = rising_frame()
        comparison = self._comparison(rows=rows)
        benchmark = at_gap(rows, purge=COMPARISON_PURGE)

        self.assertEqual(
            [fold.scored_date for fold in comparison.folds],
            [fold.scored_date for fold in benchmark.folds],
        )
        self.assertEqual(
            [fold.feature_date for fold in comparison.folds],
            [fold.feature_date for fold in benchmark.folds],
        )
        self.assertEqual(comparison.mean_loss_a_bps, benchmark.mae_bps)

    def test_the_record_names_both_models_and_states_which_way_the_sign_runs(self):
        """A signed difference is unreadable without its direction, in the file.

        The convention is checked in the artifact rather than in a docstring,
        because the artifact is what a later reader has. The per-origin losses
        are checked *absent* for the same reason they are not published: the
        record is a publication and not an intermediate, and shipping them
        would support the after-the-fact differencing this block replaced.
        """

        comparison = self._comparison(rows=load_daily_panel(SAMPLE_PANEL))
        document = paired_comparison_document(
            comparison, panel_path=SAMPLE_PANEL, registry_path=REAL_REGISTRY
        )

        self.assertEqual(document["declaration"]["model_a"]["model"], "persistence")
        self.assertEqual(
            document["declaration"]["model_b"]["model"], "persistence-plus-offset"
        )

        convention = document["comparison"]["sign_convention"]
        self.assertIn("model_a=persistence", convention)
        self.assertIn("model_b=persistence-plus-offset", convention)
        self.assertIn(baseline.COMPARISON_LOSS, convention)

        interval = document["comparison"]["mean_difference_interval"]
        self.assertEqual(interval["block_length"], comparison.block_length)
        self.assertEqual(interval["seed"], comparison.seed)

        serialised = json.dumps(document)
        for withheld in ("losses_a", "losses_b", "differences"):
            self.assertNotIn(withheld, serialised)

    def test_the_seed_follows_the_run_rather_than_a_literal(self):
        """Two comparisons that differ in what they compare do not share a stream.

        `stationary_bootstrap_interval` requires a seed because an interval
        that cannot be reproduced cannot be checked, and a literal would
        satisfy the signature while making every comparison in the project draw
        the same resample sequence. The material is the declaration, and the
        order of the two sides is part of it: `a` against `b` and `b` against
        `a` publish different records and must not silently share a draw.
        """

        digest = "0" * 64
        forward = comparison_seed(
            digest,
            model_a="persistence",
            features_a=FEATURES,
            model_b="arx",
            features_b=ARX_FEATURES,
            decision_time=DECISION_TIME,
        )
        reversed_sides = comparison_seed(
            digest,
            model_a="arx",
            features_a=ARX_FEATURES,
            model_b="persistence",
            features_b=FEATURES,
            decision_time=DECISION_TIME,
        )
        other_panel = comparison_seed(
            "1" * 64,
            model_a="persistence",
            features_a=FEATURES,
            model_b="arx",
            features_b=ARX_FEATURES,
            decision_time=DECISION_TIME,
        )

        self.assertNotEqual(forward, reversed_sides)
        self.assertNotEqual(forward, other_panel)
        self.assertEqual(
            forward,
            comparison_seed(
                digest,
                model_a="persistence",
                features_a=FEATURES,
                model_b="arx",
                features_b=ARX_FEATURES,
                decision_time=DECISION_TIME,
            ),
        )



CALIBRATION_SEED = 20260910

#: The fixture horizon, in calendar days, and the number `_maximum_horizon_overlap`
#: must return from folds built at it. Origins step one day at a time and each
#: forecast covers `(feature_date, scored_date]`, three days, so three horizons
#: are live on the busiest day. Written here once because the acceptance test
#: asserts it: it is a property of how the fixture is built and not a number
#: read off a run.
CALIBRATION_HORIZON_DAYS = 3
CALIBRATION_BLOCK_LENGTH = 3


class IntervalCalibrationTests(unittest.TestCase):
    """Two numbers in one published object, related by no code until now.

    **The finding.** `PLAN.md`'s Phase 2 exit criterion is two clauses -- *"a
    model that beats persistence out of sample **and remains calibrated in the
    tails**"*. `PairedComparisonTests` above instruments the first.
    `docs/runs/persistence_funding.json` carries the raw material of the second
    and nothing else:

        "interval_coverage":    0.8100961538461539
        "interval_probability": 0.8999999999999999

    Adjacent keys in one object, over 2080 folds, and **no code in this
    repository subtracted, compared, or put an interval on the difference.**
    That is the defect `paired_model_comparison` closed one layer over: the
    repository published the ingredients of a comparison and left the
    comparison to the reader, and the comparison a reader makes unaided is the
    wrong one. Here the unaided reader does the subtraction in their head, gets
    nine points, and then has to guess whether nine points is sampling noise at
    that fold count or the benchmark's intervals being wrong.

    Decisions
    ---------

    **A bootstrap and not a binomial, for `paired_model_comparison`'s reason.**
    A Wald, Wilson or Clopper-Pearson interval on a proportion assumes the
    origins are independent. They are not: the folds overlap in horizon, which
    is the entire argument behind `_maximum_horizon_overlap` and the reason the
    contract fixes the stationary block bootstrap as the only interval this
    project reports. An independence-assuming interval here would be too narrow
    for the same structural reason that resampling two models apart was too
    narrow there.

    **The centre and the interval come from one series.** `realized_coverage`
    is the mean of the same indicator list the bootstrap resamples, not a read
    of `report.interval_coverage`. They are equal by construction on anything
    `rolling_persistence_backtest` produced -- it computes the same mean from
    the same forecasts -- and deriving them in two places is how a centre and
    an interval come to disagree after one of them is touched.

    **The declared probability is read off the report.** Not off
    `INTERVAL_PROBABILITY`, which is what *this checkout* declares, and not off
    a literal `0.90`, which is a transcribed number in the one place it must
    not be. A report that declares fewer than two levels is refused rather than
    handed the contract's grid, which is `backtest_document`'s rule -- a field
    that cannot be computed is absent, never assumed.

    **No verdict is asserted on the published number.** The record-reading test
    checks that both halves of the statement are present and that the statement
    can be formed from what the record carries. Whether 0.810 against 0.900 is
    a miscalibration is a research finding and it belongs in a report, not in
    an assertion this suite would then have to keep true.

    **What the record does not carry, and why this block does not add it.** The
    interval on realized coverage is a function of the *indicator series*, not
    of its mean and its length: a block resample of 1685 ones and 395 zeros
    depends on their arrangement, and the arrangement is exactly what
    clustering of coverage failures is. `docs/runs/persistence_funding.json`
    publishes `metrics.interval_coverage` and `folds.count` and no per-origin
    forecasts, so **the published record cannot reproduce its own coverage
    interval**, and the frozen panel that could is gitignored. That is reported
    rather than fixed: adding per-origin rows to the record would turn a
    publication into an intermediate, which `PairedComparisonTests` records as
    a deliberate decision, and this block may not change a published record's
    shape.

    Mutation record
    ---------------

    Disposable copy under `$HOME`, never the mount, built from `git ls-files`
    plus `.claude/`. `PYTHONDONTWRITEBYTECODE=1` and `python3 -B`,
    `__pycache__` cleared before every run, mutation reverted after each.
    Unmutated control **green before and after**: 697 tests, `OK`, zero
    `expectedFailure`. Exception types recorded, not counts. Python 3.9.6 --
    the lower of the two interpreters `pyproject.toml` admits.

    `.claude/` is copied because the ownership hook lives there and its test
    contributes seven errors to an otherwise green control without it.
    `CLAUDE.md`'s copy list predates the hook and does not name it; that page
    is `HUMAN_ONLY`, so this is reported and not edited -- the same note
    `PairedComparisonTests` carries, still outstanding.

      1. **The independence assumption, everywhere** -- `block` fixed at `1`
         rather than measured off the folds, which is a resample at block
         length 1 wearing the block bootstrap's name and is the defect this
         block exists to exclude. Kills exactly 2:

           * `test_a_fixture_covered_at_every_origin_has_a_degenerate_coverage_interval`,
             `AssertionError: 1 != 3`. **This is the acceptance criterion and
             the mutation target, and they did not come apart.**
           * `test_a_declared_block_length_overrides_the_one_measured_off_the_folds`,
             `AssertionError: (0.5, 1.0) == (0.5, 1.0)` -- the default and the
             explicit `block_length=1` call now agree, which is the same fact
             seen from the other side.

         **Note what the kill is on.** It is on the block length the object
         *reports*, not on the endpoints. At zero variance every resample
         structure returns `(1.0, 1.0)`, so the degenerate endpoints cannot see
         a block length at all -- see mutation 3, and see the "trap" note
         below. Writing this kill up as "the interval moved" would read
         stronger and be false.

      2. **A Wald interval on the proportion**, substituted for the bootstrap
         call, with the block length still measured and still reported.

         **The brief predicted this would survive the acceptance criterion, and
         it did.** At `p̂ = 1` the Wald standard error is
         `sqrt(p(1-p)/n) = 0`, so it also returns `(1.0, 1.0)`, and the
         degenerate fixture cannot tell it from the bootstrap. The criterion is
         blind to it and no assertion was added to the criterion to pretend
         otherwise.

         It is killed, twice, by other tests in this class, and the two kills
         are not worth the same:

           * `test_a_declared_block_length_overrides_the_one_measured_off_the_folds`,
             `AssertionError: (0.4981842445251663, 1.0018157554748337) ==
             (0.4981842445251663, 1.0018157554748337)`. **This kill is
             structural.** A Wald interval is not a function of the block
             length at all, so the default call and the `block_length=1` call
             return the identical interval, and that is true at every fold
             count.
           * `test_a_partly_covered_fixture_reports_the_indicator_mean_and_a_live_interval`,
             `AssertionError: 1.0018157554748337 not less than or equal to
             1.0`. **This kill is an accident of `n = 8`** and is recorded so
             nobody relies on it. The upper endpoint leaves `[0, 1]` only
             because the fixture is small; at the published run's 2080 folds
             the same substitution returns `(0.7960, 0.8242)`, entirely inside
             `[0, 1]`, and this assertion would not fire.

         **The brief's first option was checked and is unavailable.** It asks
         whether a second assertion *in the acceptance test* could separate a
         block resample from an independence assumption. It cannot, and the
         reason is the same property that makes the criterion sharp: on the
         covered-everywhere fixture `interval_calibration(report)` and
         `interval_calibration(report, block_length=1)` both return
         `(1.0, 1.0)`, so no comparison between them can distinguish anything.
         The zero-variance series is exactly the series on which every resample
         structure agrees. So the separation lives in a sibling test, on a
         fixture with variance, and **the acceptance criterion does not reach
         the Wald defect.** That is reported, not papered over.

      3. **The block length reported but not used** -- `_maximum_horizon_overlap`
         still measured and still returned on the object, while the bootstrap
         is called at `block_length=1`. The label and the arithmetic pulled
         apart. Kills exactly 1 --
         `test_a_declared_block_length_overrides_the_one_measured_off_the_folds`,
         `AssertionError: (0.5, 1.0) == (0.5, 1.0)`.

         **The acceptance criterion survives this**, for mutation 1's reason,
         and this is the sharpest statement of what the criterion does and does
         not reach: it checks that the block length was *measured*, and nothing
         in it checks that it was *used*.

      4. **The declared probability taken from `INTERVAL_PROBABILITY`** instead
         of from `report.quantile_levels` -- the module constant, which is what
         this checkout declares, standing in for what the run declared. Kills
         exactly 1 --
         `test_the_declared_probability_is_read_off_the_report_not_off_the_contract`,
         `AssertionError: 0.8999999999999999 != 0.8 within 7 places`.

      5. **The centre read off `report.interval_coverage`** instead of being
         the mean of the resampled series. **This survived the first time it
         was run**, against the seven tests this block originally added, and it
         survived for a reason worth stating: on anything
         `rolling_persistence_backtest` produced the two are equal by
         construction, so no honest fixture separates them, and the "one
         series, one derivation" decision above was a design decision the suite
         did not enforce. `test_the_centre_comes_from_the_resampled_series_not_from_the_reports_field`
         was added in response -- a hand-built report carrying a stale
         `interval_coverage` beside live forecasts -- and the mutation now
         kills exactly 1, `AssertionError: 0.0 != 1.0`.

      6. **Strict inequality on both ends of the indicator** --
         `lower < actual < upper` for `lower <= actual <= upper`. **Also
         survived the first time**, because every fixture in this class put its
         actuals strictly inside their intervals, the acceptance criterion
         most of all. That is a defect the suite would not have caught while
         the docstring claimed the closed interval, and the closed interval is
         not a preference: it is the definition
         `rolling_persistence_backtest` computed the published
         `interval_coverage` under, so a strict indicator would calibrate a
         different quantity than the one being calibrated.
         `test_an_actual_on_its_own_bound_is_covered_as_the_backtest_counts_it`
         was added, and the mutation now kills exactly 1,
         `AssertionError: 0.0 != 1.0`.

    Mutations 5 and 6 are recorded as the survivals they were, rather than
    presented as guards that were there all along.
    """

    def _forecasts(self, actuals, half_width, misses=()):
        """One `Forecast` per actual, with `half_width` either side of it.

        `misses` names positions whose actual is pushed outside its own
        interval instead. The interval is centred on the actual rather than on
        the prediction, so whether an origin is covered is a property of how
        this fixture is written and not of any fit -- which is what lets the
        acceptance test state its expected value from construction.
        """

        built = []
        for position, actual in enumerate(actuals):
            centre = actual
            lower = centre - half_width
            upper = centre + half_width
            observed = actual + 2.0 * half_width if position in misses else actual
            span = upper - lower
            built.append(
                Forecast(
                    observed,
                    centre,
                    lower,
                    upper,
                    (lower, lower + span / 4.0, centre, upper - span / 4.0, upper),
                )
            )
        return built

    def _folds(self, count, horizon_days=CALIBRATION_HORIZON_DAYS):
        start = date(2026, 3, 2)
        return tuple(
            ScoredFold(
                train_start=start,
                train_end=start + timedelta(days=index),
                train_rows=20 + index,
                feature_date=start + timedelta(days=index),
                scored_date=start + timedelta(days=index + horizon_days),
            )
            for index in range(count)
        )

    def _report(self, forecasts, levels=QUANTILE_LEVELS, horizon_days=CALIBRATION_HORIZON_DAYS):
        covered = sum(
            item.lower_bps <= item.actual_bps <= item.upper_bps for item in forecasts
        )
        return BacktestReport(
            forecasts=forecasts,
            mae_bps=sum(
                abs(item.actual_bps - item.predicted_bps) for item in forecasts
            )
            / max(1, len(forecasts)),
            interval_coverage=covered / max(1, len(forecasts)),
            folds=self._folds(len(forecasts), horizon_days),
            quantile_levels=tuple(levels),
        )

    def test_a_fixture_covered_at_every_origin_has_a_degenerate_coverage_interval(self):
        """The acceptance criterion, and the mutation target.

        Every actual falls strictly inside its own interval, so every indicator
        is `1`, the series has zero variance, **any** resample of it returns
        `1.0`, and the interval collapses to `(1.0, 1.0)` at both endpoints.
        The expected value comes from how the fixture is built and never from a
        run.

        **This is `PairedComparisonTests`' trick a second time and is not new
        here.** It is the right one for the same reason: a numeric interval
        pinned from a run agrees with any mutation that moves the run and the
        literal together, and a degenerate case does not.

        The second assertion is the block length. A resample at block length 1
        *is* the independence assumption wearing the bootstrap's name, and the
        degenerate endpoints cannot see it -- at zero variance every block
        length returns `1.0`. Three is what folds stepping one day at a time
        with three-day horizons put live at the busiest point, which is a fact
        about `_folds` above and not about any run.

        **What this criterion does not reach: see the class docstring's
        mutation 3.** A Wald interval survives both assertions.
        """

        report = self._report(self._forecasts([10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0], 5.0))

        calibration = interval_calibration(report, seed=CALIBRATION_SEED)

        self.assertEqual(calibration.realized_coverage, 1.0)
        self.assertEqual(calibration.coverage_interval, (1.0, 1.0))
        self.assertEqual(calibration.block_length, CALIBRATION_BLOCK_LENGTH)

    def test_the_declared_probability_is_read_off_the_report_not_off_the_contract(self):
        """A run at a narrower grid declares a narrower probability.

        `INTERVAL_PROBABILITY` is `0.95 - 0.05` because that is what
        `contract.QUANTILE_LEVELS` says *here*. A report is a record of what a
        run declared, and the two are the same number only for as long as
        nobody changes the grid. A report at `(0.10, ..., 0.90)` declares
        `0.80`, and a calibration statement that answered `0.90` for it would
        be comparing a realized coverage to a probability the run never
        claimed.
        """

        narrow = self._report(
            self._forecasts([10.0, 11.0, 12.0, 13.0], 5.0),
            levels=(0.10, 0.30, 0.50, 0.70, 0.90),
        )
        contractual = self._report(self._forecasts([10.0, 11.0, 12.0, 13.0], 5.0))

        self.assertAlmostEqual(
            interval_calibration(narrow, seed=CALIBRATION_SEED).declared_probability,
            0.80,
        )
        self.assertEqual(
            interval_calibration(contractual, seed=CALIBRATION_SEED).declared_probability,
            INTERVAL_PROBABILITY,
        )

    def test_a_report_declaring_no_grid_is_refused_rather_than_given_the_contracts(self):
        """`BacktestReport.quantile_levels` defaults empty; a default here would lie.

        Reports are constructed by hand elsewhere in this suite to exercise a
        reporter, and those carry no grid. Substituting `QUANTILE_LEVELS` would
        report a declaration the run did not make, so the refusal is a
        `ValueError` and not a fallback.
        """

        bare = BacktestReport(
            forecasts=self._forecasts([10.0, 11.0], 5.0),
            mae_bps=0.0,
            interval_coverage=1.0,
        )

        with self.assertRaises(ValueError):
            interval_calibration(bare, seed=CALIBRATION_SEED)

    def test_a_report_with_no_forecasts_has_no_calibration(self):
        empty = BacktestReport(
            forecasts=[],
            mae_bps=0.0,
            interval_coverage=0.0,
            quantile_levels=tuple(QUANTILE_LEVELS),
        )

        with self.assertRaises(ValueError):
            interval_calibration(empty, seed=CALIBRATION_SEED)

    def test_a_partly_covered_fixture_reports_the_indicator_mean_and_a_live_interval(self):
        """Six of eight covered: the centre is `0.75` by construction.

        The contrast with the acceptance criterion is the point. A series with
        variance produces endpoints that differ, so the degenerate case above
        is a property of the zero-variance series and not something this
        function does to every input.
        """

        report = self._report(
            self._forecasts(
                [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0], 5.0, misses=(2, 6)
            )
        )

        calibration = interval_calibration(report, seed=CALIBRATION_SEED)
        lower, upper = calibration.coverage_interval

        self.assertEqual(calibration.realized_coverage, 0.75)
        self.assertEqual(calibration.realized_coverage, report.interval_coverage)
        self.assertLess(lower, upper)
        self.assertGreaterEqual(lower, 0.0)
        self.assertLessEqual(upper, 1.0)

    def test_a_declared_block_length_overrides_the_one_measured_off_the_folds(self):
        """`mae_bootstrap_interval`'s argument, with `mae_bootstrap_interval`'s meaning.

        Carried so a caller can ask what an independence assumption would have
        produced -- block length 1 -- rather than being unable to state the
        contrast at all.
        """

        report = self._report(
            self._forecasts(
                [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0], 5.0, misses=(2, 6)
            )
        )

        self.assertEqual(
            interval_calibration(report, seed=CALIBRATION_SEED, block_length=1).block_length,
            1,
        )
        self.assertNotEqual(
            interval_calibration(report, seed=CALIBRATION_SEED, block_length=1).coverage_interval,
            interval_calibration(report, seed=CALIBRATION_SEED).coverage_interval,
        )

    def test_an_actual_on_its_own_bound_is_covered_as_the_backtest_counts_it(self):
        """`lower <= actual <= upper`, both ends closed, as `rolling_persistence_backtest` does.

        Added after mutation 6 survived: no other fixture in this class puts an
        actual *on* a bound, and the acceptance criterion is built from actuals
        strictly inside, so a strict-inequality indicator was indistinguishable
        from the closed one. The closed interval is not a preference here -- it
        is the definition the published `interval_coverage` was computed under,
        and a calibration statement counting coverage differently from the
        number it is calibrating would be relating two different quantities.
        """

        on_the_bound = [
            Forecast(5.0, 10.0, 5.0, 15.0, (5.0, 7.5, 10.0, 12.5, 15.0)),
            Forecast(15.0, 10.0, 5.0, 15.0, (5.0, 7.5, 10.0, 12.5, 15.0)),
        ]
        report = BacktestReport(
            forecasts=on_the_bound,
            mae_bps=5.0,
            interval_coverage=1.0,
            folds=self._folds(2),
            quantile_levels=tuple(QUANTILE_LEVELS),
        )

        calibration = interval_calibration(report, seed=CALIBRATION_SEED)

        self.assertEqual(calibration.realized_coverage, 1.0)
        self.assertEqual(calibration.coverage_interval, (1.0, 1.0))

    def test_the_centre_comes_from_the_resampled_series_not_from_the_reports_field(self):
        """A report whose stated coverage disagrees with its own forecasts.

        Added after mutation 5 survived. On anything
        `rolling_persistence_backtest` produced the two agree by construction,
        so no honest fixture separates them -- which is precisely why the
        decision to derive the centre from the resampled series was invisible
        to the suite. `BacktestReport` is constructed by hand elsewhere in this
        file, so a report carrying a stale `interval_coverage` beside live
        forecasts is a thing that can exist, and the calibration statement must
        describe the series its interval was drawn from.
        """

        inconsistent = BacktestReport(
            forecasts=self._forecasts([10.0, 11.0, 12.0, 13.0], 5.0),
            mae_bps=0.0,
            interval_coverage=0.0,
            folds=self._folds(4),
            quantile_levels=tuple(QUANTILE_LEVELS),
        )

        calibration = interval_calibration(inconsistent, seed=CALIBRATION_SEED)

        self.assertEqual(calibration.realized_coverage, 1.0)
        self.assertNotEqual(calibration.realized_coverage, inconsistent.interval_coverage)

    def test_the_published_persistence_record_carries_both_halves_of_the_statement(self):
        """The record is read, never written, and no verdict is asserted on it.

        `docs/runs/` holds records of runs that happened, at `568c9ba`. This
        asserts only that the two fields this block relates are both present
        and well formed, and that a calibration statement -- a realized
        coverage, a declared probability, and the fold count they are over --
        can be formed from what the record carries.

        It deliberately does **not** assert that `0.810` is below `0.900`.
        That is a research finding, it is reported in the block report, and an
        assertion here would be this suite promising to keep a measurement
        true.
        """

        record = json.loads(
            (
                Path(__file__).parents[1] / "docs" / "runs" / "persistence_funding.json"
            ).read_text(encoding="utf-8")
        )
        metrics = record["metrics"]

        self.assertIn("interval_coverage", metrics)
        self.assertIn("interval_probability", metrics)

        realized = metrics["interval_coverage"]
        declared = metrics["interval_probability"]
        origins = record["folds"]["count"]

        for value in (realized, declared):
            self.assertIsInstance(value, float)
            self.assertTrue(math.isfinite(value))
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)
        self.assertIsInstance(origins, int)
        self.assertGreater(origins, 0)

        # The fold count the statement is over is stated twice in the record
        # and the two must agree, or the statement has no unambiguous `n`.
        self.assertEqual(metrics["forecast_count"], origins)

        # What the record cannot supply: the interval. It is a function of the
        # indicator *series*, and the record publishes the series' mean and its
        # length and no per-origin rows. Asserted as the absence it is, so that
        # a later block which publishes them has to come back here and say so.
        self.assertNotIn("forecasts", record)
        self.assertEqual(set(record["folds"]), {"count", "first", "last"})


#: The origins whose actual is pushed outside its own interval in
#: `CalibrationDocumentTests`' clustered fixture, and in its scattered one. Both
#: name four of twenty-four origins, so both fixtures have the **same** realized
#: coverage, the same length and -- because the seed is derived from the panel
#: and the declaration, which they share -- the same seed. They differ in
#: nothing a summary field can see, which is the whole of what
#: `test_two_documents_agreeing_on_every_summary_field_still_state_different_intervals`
#: is for.
CLUSTERED_MISSES = (6, 7, 8, 17)
SCATTERED_MISSES = (2, 9, 15, 21)

#: How many origins those fixtures score. Twenty-four rather than eight, because
#: this class needs a coverage interval with live width -- an all-covered series
#: has zero variance and every arrangement of it resamples to the same
#: endpoints, which is the property `IntervalCalibrationTests`' acceptance
#: criterion depends on and the property this one must not have.
CALIBRATION_DOCUMENT_ORIGINS = 24


class CalibrationDocumentTests(unittest.TestCase):
    """A calibration statement a record can reproduce, and the trap it avoids.

    **The finding this block was built on, restated.** `interval_calibration`
    landed and nothing published it, and the reason given for not publishing it
    was that `docs/runs/persistence_funding.json` **cannot reproduce its own
    coverage interval**. It carries `metrics.interval_coverage` and
    `folds.count` and no per-origin anything, and a block resample of 1685 ones
    and 395 zeros depends on their *arrangement* -- which is exactly the
    clustering of coverage failures a calibration statement is about. The
    strongest statement available from the record as it stands was a bracketing
    between the scattered and contiguous arrangements, and that bracketing
    should not have had to be the strongest one available.

    `backtest_document` now carries the statement, so the *next* record is
    reproducible. This class is what says it is.

    The trap
    --------

    The cheap version of this block publishes `realized_coverage`,
    `declared_probability`, `block_length`, `seed`, `replications` and the fold
    count, and looks complete. **Those six numbers are what the record carries
    today plus labels.** A resample of them cannot be run: the mean and the
    length do not determine the series. A document carrying them and calling
    itself reproducible would make a stronger claim than the current record
    makes and be no more true.

    So the criterion is a **round trip and not a field census**:
    `calibration_from_document` never reads the endpoints the record states. It
    decodes the series, resamples it at the parameters the record declares, and
    the acceptance test asserts the result equals both the run's own
    `IntervalCalibration` and the record's stated endpoints. A reader that
    returned the stated numbers would pass a census and fail this.

    `test_two_documents_agreeing_on_every_summary_field_still_state_different_intervals`
    is the trap made executable rather than argued. Two fixtures miss at four of
    twenty-four origins, one clustered and one scattered. Every summary field
    is identical -- the same realized coverage, the same length, the same block
    length, the same seed, the same replications, the same level -- and the
    recomputed intervals are `(0.667, 0.958)` and `(0.750, 0.917)`. The
    clustered arrangement is the wider one, which is the dependence the block
    bootstrap exists to carry, and no function of the six summary fields could
    have told them apart.

    Decisions
    ---------

    **The series is carried run-length encoded, and the choice is not about
    size.** `_encode_indicator_runs` holds the measurement: at 2080 origins the
    raw list is 6,240 bytes of JSON and the pairs run from 30 bytes on one
    contiguous block of failures to 16,640 on a series alternating at every
    origin -- so the encoding is a large win when failures cluster, a small one
    at random, and a 2.7x *loss* in the pathological case. It is chosen because
    the pairs show the clustering in the JSON, which is the property the
    statement is about, and because the cost is bounded at `2 * n` integers.
    `test_the_encoded_series_is_bounded_by_two_integers_per_origin` holds that
    bound so the claim cannot decay into an assurance.

    **One bit per origin is not a forecast row.** `PairedComparisonTests`
    records keeping intermediates off a publication as a deliberate decision and
    that decision stands: nothing added here publishes a prediction, a quantile
    or an actual. What is published is whether each origin's actual fell inside
    its own interval, which is the whole of what a coverage statement is over,
    and it is the least a record can carry and still be resampled.

    **The declared length is redundant and checked anyway.** The runs sum to it,
    so it derives nothing -- and that is the reason it is compared rather than
    trusted: a truncated `runs` array decodes into a shorter series perfectly
    happily and resamples to a different interval with no sign anything is
    wrong. See `test_a_declared_length_that_disagrees_with_the_runs_is_refused`.

    **Absent rather than defaulted, on a run that declared no grid.**
    `interval_calibration` refuses a report with fewer than two quantile levels
    because the probability a coverage is calibrated against is the run's own
    declaration. That refusal must not become `backtest_document`'s, so the
    field is omitted from such a document -- `backtest_document`'s standing rule,
    and the reason `RunProvenanceTests`' hand-built report still publishes.

    What this block did **not** do
    -----------------------------

    It did not regenerate `docs/runs/persistence_funding.json`. The frozen panel
    is gitignored and not in this worktree, the existing record is a record of a
    run that happened, and `scripts/` and `README.md` are `HUMAN_ONLY`. So
    `IntervalCalibrationTests`' record-reading test still describes the
    published record correctly, including its assertion that the record carries
    no `forecasts` -- and it will keep describing it until a human re-runs the
    backtest. That is the block report's business, not an assertion's.

    Mutation record
    ---------------

    Disposable copy under `$HOME`, never the mount, built from `git ls-files`
    plus `.claude/` -- which `CLAUDE.md`'s copy list has named since `c42a86c`.
    `PYTHONDONTWRITEBYTECODE=1` and `python3 -B`, `__pycache__` cleared before
    every run, mutation reverted after each. Unmutated control **green before
    and after**: 713 tests, `OK`, zero `expectedFailure`. Exception types
    recorded, not counts. Python 3.9.6 -- the lower of the two interpreters
    `pyproject.toml` admits.

    The copy skips two tests the mount runs, because it is not a git checkout
    and the record's git-state tests say so. Skip counts vary by checkout and
    mean nothing; the zero `expectedFailure` is the load-bearing half.

      1. **The series stripped, the six summary fields left** -- the mutation
         this block's brief names, and the one the criterion exists to survive.
         `_calibration_document` returns `realized_coverage`,
         `declared_probability` and the whole `coverage_interval` object --
         endpoints, level, method, block length, replications and seed -- and no
         `coverage_series`. Every summary field a reader could want is present
         and the record is no longer reproducible.

         **Eight tests go red and only three of them are the finding.** The
         count is the reason `CLAUDE.md` asks for exception types: five of the
         eight are `KeyError: 'coverage_series'` raised by a test's own
         subscript of the document, before `calibration_from_document` is
         reached at all. Those five are the fixture noticing the field is gone,
         not a guard firing. The three that are the finding all die inside the
         reader:

           * `test_a_calibration_statement_read_back_from_the_document_reproduces_the_interval`,
             `ValueError: the record's interval_calibration carries no
             'coverage_series', so no calibration statement can be recomputed
             from it`. **This is the acceptance criterion and the mutation
             target, and they did not come apart.**
           * `test_two_documents_agreeing_on_every_summary_field_still_state_different_intervals`,
             the same `ValueError` -- and that is the right way for it to die:
             with no series there is nothing left for two documents to disagree
             about.
           * `test_a_record_whose_stated_endpoints_do_not_match_its_series_is_not_believed`,
             the same `ValueError`.

         The five incidental ones, recorded so nobody reads eight as strength:
         `test_a_declared_length_that_disagrees_with_the_runs_is_refused`,
         `test_a_document_carrying_every_summary_field_and_no_series_is_refused`,
         `test_an_encoding_this_reader_does_not_implement_is_refused_not_guessed`,
         `test_the_encoded_series_is_bounded_by_two_integers_per_origin` and
         `test_the_published_statement_shows_the_arrangement_and_not_only_its_mean`,
         each `KeyError: 'coverage_series'`.

         That the refusal is a `ValueError` rather than a wrong number is the
         point: `calibration_from_document` refuses a record it cannot resample
         rather than answering from the summary fields, because an interval
         derived from a mean and a length would be a number nobody computed.

      2. **The declared length trusted instead of compared** --
         `_decode_indicator_runs` returns the decoded series without checking it
         against `length`. Kills exactly 1,
         `test_a_declared_length_that_disagrees_with_the_runs_is_refused`,
         `AssertionError: ValueError not raised`.

         **The acceptance criterion survives this**, and it survives for a
         reason worth stating plainly: on any document this repository wrote the
         runs and the declared length always agree, so a round trip cannot see
         the check at all. The guard is reachable only from a record somebody
         edited or truncated, which is the case it exists for and not a case a
         round trip constructs.

      3. **The reader returns the record's stated endpoints** instead of
         resampling the decoded series -- `coverage_interval` read out of the
         document, the bootstrap call dropped, everything else left alone. This
         is the field census wearing the round trip's name, and it is the defect
         the criterion's *shape* was chosen to exclude.

         **It survives the acceptance criterion, and that is the sharpest thing
         in this record.** On any document `_calibration_document` wrote, the
         stated endpoints *are* the recomputed endpoints, so equality holds and
         the criterion passes a reader that recomputes nothing. Killed instead
         by exactly 1 --
         `test_a_record_whose_stated_endpoints_do_not_match_its_series_is_not_believed`,
         `AssertionError: Tuples differ: (0.1, 0.2) != (0.75,
         0.9166666666666666)` -- on a document whose stated endpoints have been
         overwritten with numbers no resample of its series produces.

         That test was written for this mutation, and the honest reading is that
         **the criterion checks that the document round-trips and nothing in it
         checks that the reader did the resampling.** Same shape as
         `IntervalCalibrationTests`' mutation 3, one layer out.

      4. **The indicator bounds opened at one end** --
         `_coverage_indicators` scoring `lower <= actual < upper` rather than
         closed on both sides. Run because this block *moved* that code: the
         list comprehension was extracted out of `interval_calibration`, and
         `IntervalCalibrationTests`' mutation 6 names it. The standing rule is
         to re-run a mutation whose fixture this block touched; a function it
         relocated is the same case.

         Kills exactly 1, in the other class --
         `test_an_actual_on_its_own_bound_is_covered_as_the_backtest_counts_it`,
         `AssertionError: 0.5 != 1.0`. The earlier record stands; the extraction
         did not blunt it.

         Nothing in `CalibrationDocumentTests` kills it, and that is expected
         rather than a gap: this class's fixtures put their actuals strictly
         inside or strictly outside their intervals, so no origin of theirs sits
         on a bound. The guard for the boundary belongs where it already is.
    """

    #: The gap this fixture's run declares. Two days, and pinned rather than
    #: defaulted only because `_report_seed` reads it: a seed derived from a
    #: field nobody stated is a seed nobody can recompute.
    PURGE = 2

    #: Half-width of every fixture interval, in basis points. The interval is
    #: centred on the *actual*, so whether an origin is covered is a property of
    #: how this fixture is written and not of any fit -- the same trick
    #: `IntervalCalibrationTests._forecasts` uses, and for the same reason.
    HALF_WIDTH = 5.0

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

        # Neither file is parsed by a record -- a record identifies them by the
        # digest of the bytes the run read -- so both are as small as that claim
        # allows. `RunProvenanceTests` makes the same argument at length.
        self.panel = self.root / "panel.csv"
        self.panel.write_text("date,spread_bps\n2026-03-02,1.0\n", encoding="utf-8")
        self.registry = self.root / "sources.json"
        self.registry.write_text(
            json.dumps({"sources": {}}, indent=2) + "\n", encoding="utf-8"
        )

    def _forecasts(self, misses):
        """One `Forecast` per origin, with `misses` pushed outside its interval."""

        built = []
        for position in range(CALIBRATION_DOCUMENT_ORIGINS):
            actual = 10.0 + position
            lower = actual - self.HALF_WIDTH
            upper = actual + self.HALF_WIDTH
            observed = (
                actual + 2.0 * self.HALF_WIDTH if position in misses else actual
            )
            span = upper - lower
            built.append(
                Forecast(
                    observed,
                    actual,
                    lower,
                    upper,
                    (lower, lower + span / 4.0, actual, upper - span / 4.0, upper),
                )
            )
        return built

    def _folds(self, count):
        start = date(2026, 3, 2)
        return tuple(
            ScoredFold(
                train_start=start,
                train_end=start + timedelta(days=index),
                train_rows=20 + index,
                feature_date=start + timedelta(days=index),
                scored_date=start
                + timedelta(days=index + CALIBRATION_HORIZON_DAYS),
            )
            for index in range(count)
        )

    def _report(self, misses, levels=QUANTILE_LEVELS):
        """A report a record can be built from, with a stated arrangement.

        Every field `backtest_document` and `_report_seed` read is present and
        derived from the fixture. `interval_coverage` is computed the way
        `rolling_persistence_backtest` computes it, so the fixture is one story
        rather than a report whose parts disagree.
        """

        forecasts = self._forecasts(misses)
        covered = sum(
            item.lower_bps <= item.actual_bps <= item.upper_bps
            for item in forecasts
        )
        return BacktestReport(
            forecasts=forecasts,
            mae_bps=sum(
                abs(item.actual_bps - item.predicted_bps) for item in forecasts
            )
            / len(forecasts),
            interval_coverage=covered / len(forecasts),
            folds=self._folds(len(forecasts)),
            quantile_levels=tuple(levels),
            features=FEATURES,
            sources=("fred_macro_latest_vintage",),
            field_sources=(("fred_macro_latest_vintage", "DGS10"),),
            purge_days=self.PURGE,
            decision_time=DECISION_TIME,
            panel_rows=len(forecasts),
            panel_first_date=date(2026, 3, 2),
            panel_last_date=date(2026, 3, 2) + timedelta(days=len(forecasts)),
        )

    def _seed(self, report):
        """The seed the record will state, derived as `backtest_document` derives it.

        Recomputed here from the panel bytes and the declaration rather than read
        back out of the document, so the reference call this class compares
        against does not take its seed from the artifact under test.
        """

        return baseline._report_seed(
            report, hashlib.sha256(self.panel.read_bytes()).hexdigest()
        )

    def _document(self, report):
        """The record, through JSON and back.

        Serialised and reparsed rather than passed as a live dict, because "a
        record can reproduce its own interval" is a claim about a *file*: a
        tuple that survives in memory and becomes a list on disk, or a float
        that does not round-trip, would be a defect this class exists to catch
        and an in-memory dict would hide it.
        """

        return json.loads(
            json.dumps(
                backtest_document(
                    report,
                    panel_path=self.panel,
                    registry_path=self.registry,
                    model="persistence",
                )
            )
        )

    def test_a_calibration_statement_read_back_from_the_document_reproduces_the_interval(
        self,
    ):
        """The acceptance criterion, and the mutation target.

        A report, its document, and then the calibration recomputed from the
        document **only** -- the report is deleted from this scope before the
        reader is called, so nothing but the parsed JSON is available to it. No
        panel is read, no forecast is in scope, and the interval comes back
        equal to the run's own to the endpoint, at the same seed.

        Three assertions, and the second is the one that makes this a round trip
        rather than a census: the recomputed endpoints equal the endpoints the
        record *states*, which the reader never read. The third pins the
        arrangement itself -- the recomputed object carries the same series, in
        the same order, which is the thing the mean and the length could not
        determine.

        **What this criterion does not reach: mutations 2 and 3 in the class
        docstring.** A reader that returned the record's stated endpoints
        survives it, because on a document this repository wrote the stated and
        the recomputed endpoints are the same numbers.
        """

        report = self._report(CLUSTERED_MISSES)
        seed = self._seed(report)
        expected = interval_calibration(report, seed=seed)
        document = self._document(report)
        stated = document["metrics"]["interval_calibration"]["coverage_interval"]

        # Nothing but `document` and `expected` survives into the recomputation.
        del report

        recomputed = calibration_from_document(document)

        self.assertEqual(recomputed, expected)
        self.assertEqual(
            recomputed.coverage_interval, (stated["lower"], stated["upper"])
        )
        self.assertEqual(
            recomputed.coverage_series,
            tuple(
                0.0 if position in CLUSTERED_MISSES else 1.0
                for position in range(CALIBRATION_DOCUMENT_ORIGINS)
            ),
        )

    def test_two_documents_agreeing_on_every_summary_field_still_state_different_intervals(
        self,
    ):
        """The trap, executable. Six summary fields cannot tell these apart.

        Four misses of twenty-four in both fixtures, clustered in one and
        scattered in the other. The realized coverage, the length, the block
        length, the seed, the replications and the level are identical -- the
        seed because it is derived from the panel and the declaration, which the
        two runs share -- and the recomputed intervals differ. The clustered
        arrangement is the wider one, which is the horizon dependence the block
        bootstrap exists to carry.

        This is why a record carrying the summary fields and calling itself
        reproducible would be making a claim no arithmetic supports.
        """

        clustered = self._document(self._report(CLUSTERED_MISSES))
        scattered = self._document(self._report(SCATTERED_MISSES))

        first = calibration_from_document(clustered)
        second = calibration_from_document(scattered)

        for name in ("realized_coverage", "block_length", "seed", "replications", "level"):
            self.assertEqual(
                getattr(first, name),
                getattr(second, name),
                msg=f"the fixtures were built to agree on {name}",
            )
        self.assertEqual(
            len(first.coverage_series), len(second.coverage_series)
        )

        self.assertNotEqual(first.coverage_series, second.coverage_series)
        self.assertNotEqual(first.coverage_interval, second.coverage_interval)
        # The clustered arrangement is the wider interval, at both ends.
        self.assertLess(first.coverage_interval[0], second.coverage_interval[0])
        self.assertGreater(first.coverage_interval[1], second.coverage_interval[1])

    def test_a_document_carrying_every_summary_field_and_no_series_is_refused(self):
        """A record that cannot be resampled is refused, not answered.

        The document with `coverage_series` removed and everything else left
        intact -- realized coverage, declared probability, both endpoints, the
        level, the method, the block length, the replications and the seed. That
        is more than `docs/runs/persistence_funding.json` carries today, and it
        is still not enough, so the reader raises rather than returning an
        interval derived from a mean and a length.
        """

        document = self._document(self._report(CLUSTERED_MISSES))
        statement = document["metrics"]["interval_calibration"]
        del statement["coverage_series"]

        self.assertIn("realized_coverage", statement)
        self.assertIn("declared_probability", statement)
        self.assertEqual(
            set(statement["coverage_interval"]),
            {
                "lower",
                "upper",
                "level",
                "method",
                "block_length",
                "replications",
                "seed",
            },
        )

        with self.assertRaises(ValueError):
            calibration_from_document(document)

    def test_a_record_whose_stated_endpoints_do_not_match_its_series_is_not_believed(
        self,
    ):
        """The reader resamples the series; it never reads the stated endpoints.

        Added in response to mutation 3, which is a reader that returns the
        record's own `lower` and `upper`. Those are overwritten here with numbers
        no resample of this series produces, and the recomputed interval is
        unmoved -- so the stated endpoints are demonstrably not an input.
        """

        document = self._document(self._report(SCATTERED_MISSES))
        honest = calibration_from_document(document).coverage_interval

        interval = document["metrics"]["interval_calibration"]["coverage_interval"]
        interval["lower"] = 0.1
        interval["upper"] = 0.2

        self.assertEqual(calibration_from_document(document).coverage_interval, honest)

    def test_a_declared_length_that_disagrees_with_the_runs_is_refused(self):
        """A truncated series decodes happily and resamples to the wrong interval.

        The last run dropped, the declared `length` left alone. Without the
        comparison the reader would return an interval over 18 origins and call
        it a statement about 24.
        """

        document = self._document(self._report(CLUSTERED_MISSES))
        series = document["metrics"]["interval_calibration"]["coverage_series"]
        self.assertEqual(series["length"], CALIBRATION_DOCUMENT_ORIGINS)
        series["runs"] = series["runs"][:-1]

        with self.assertRaises(ValueError):
            calibration_from_document(document)

    def test_an_encoding_this_reader_does_not_implement_is_refused_not_guessed(self):
        """The record names its encoding, and an unknown one stops the reader.

        A list of two-element arrays is also what a summarised series would look
        like. Guessing between them would be guessing at the arrangement an
        interval depends on, so the name is carried in the record and checked.
        """

        document = self._document(self._report(CLUSTERED_MISSES))
        series = document["metrics"]["interval_calibration"]["coverage_series"]
        self.assertEqual(series["encoding"], baseline._COVERAGE_SERIES_ENCODING)
        series["encoding"] = "sparse_failures"

        with self.assertRaises(ValueError):
            calibration_from_document(document)

    def test_the_published_statement_shows_the_arrangement_and_not_only_its_mean(self):
        """What a human opening the JSON sees: runs of coverage, broken by failures.

        The clustered fixture's twenty-four origins encode as five runs, and the
        three consecutive failures at origins 6, 7 and 8 appear as a single
        `[0, 3]`. The expected value comes from how the fixture is written and
        never from a run.
        """

        document = self._document(self._report(CLUSTERED_MISSES))
        series = document["metrics"]["interval_calibration"]["coverage_series"]

        self.assertEqual(
            series["runs"], [[1, 6], [0, 3], [1, 8], [0, 1], [1, 6]]
        )
        self.assertEqual(series["length"], CALIBRATION_DOCUMENT_ORIGINS)
        self.assertEqual(
            sum(count for _, count in series["runs"]),
            CALIBRATION_DOCUMENT_ORIGINS,
        )

    def test_the_encoded_series_is_bounded_by_two_integers_per_origin(self):
        """The size claim, as an assertion rather than an assurance.

        `_encode_indicator_runs`' docstring states the cost of this shape and
        states that its worst case -- a series alternating at every origin -- is
        one run per origin. That bound is what makes the shape safe to put in a
        record beside a 1.5 MB one, so it is held here, on the alternating series
        itself and on both fixtures.
        """

        alternating = [float(position % 2) for position in range(200)]
        runs = baseline._encode_indicator_runs(alternating)
        self.assertEqual(len(runs), len(alternating))

        for misses in (CLUSTERED_MISSES, SCATTERED_MISSES):
            series = self._document(self._report(misses))["metrics"][
                "interval_calibration"
            ]["coverage_series"]
            self.assertLessEqual(len(series["runs"]), series["length"])

    def test_a_run_that_declared_no_quantile_grid_publishes_no_calibration_statement(
        self,
    ):
        """Absent, not defaulted. `backtest_document`'s standing rule.

        `interval_calibration` refuses a report declaring fewer than two levels,
        because the probability a coverage is calibrated against is the run's own
        declaration and substituting this checkout's grid would report a claim
        the run never made. That refusal must not become `backtest_document`'s:
        a report with no grid still publishes a record, and the record simply
        does not carry a statement it cannot make.
        """

        bare = self._report(CLUSTERED_MISSES, levels=())
        document = self._document(bare)

        self.assertNotIn("interval_calibration", document["metrics"])
        self.assertIn("interval_coverage", document["metrics"])
        with self.assertRaises(ValueError):
            calibration_from_document(document)

    def test_the_record_states_one_block_length_for_both_of_its_intervals(self):
        """Two intervals over one run's origins, measured once.

        `backtest_document` hands the block length it measured for the MAE
        interval to `interval_calibration` rather than letting it measure the
        same `_maximum_horizon_overlap` over the same folds again. Two
        derivations of one number agree today and drift after one of them is
        touched, and a record stating two different block lengths for two
        resamples of the same origins would be unreadable.
        """

        document = self._document(self._report(CLUSTERED_MISSES))
        metrics = document["metrics"]

        self.assertEqual(
            metrics["interval_calibration"]["coverage_interval"]["block_length"],
            metrics["mae_bps_interval"]["block_length"],
        )
        self.assertEqual(
            metrics["interval_calibration"]["coverage_interval"]["seed"],
            metrics["mae_bps_interval"]["seed"],
        )

    def test_the_statement_relates_the_realized_coverage_to_what_the_run_declared(self):
        """Both halves in one object, and neither read off a module constant.

        The record's `interval_probability` is `INTERVAL_PROBABILITY`, which is
        what *this checkout* declares. The statement's `declared_probability` is
        read off the report's own grid. They agree here because the fixture
        declares the contract's grid, and the assertion that matters is the
        second: a run at a narrower grid states the narrower probability, which
        `IntervalCalibrationTests` covers on the object and this covers on the
        record.
        """

        document = self._document(self._report(CLUSTERED_MISSES))
        statement = document["metrics"]["interval_calibration"]

        self.assertEqual(statement["declared_probability"], INTERVAL_PROBABILITY)
        self.assertEqual(
            statement["realized_coverage"], document["metrics"]["interval_coverage"]
        )

        narrow = self._document(
            self._report(CLUSTERED_MISSES, levels=(0.10, 0.30, 0.50, 0.70, 0.90))
        )
        self.assertAlmostEqual(
            narrow["metrics"]["interval_calibration"]["declared_probability"], 0.80
        )


if __name__ == "__main__":
    unittest.main()
