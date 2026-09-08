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

     The conformance suites still run once per implementer on both interfaces,
     counted rather than diffed: `tests/test_registry_interface.py` 37 tests,
     `tests/test_events_metadata_spec.py` 42, `tests/test_contract.py` 69 --
     the same three counts before and after.

No mutation was planted in the ARX, the threshold model, the bootstrap or the
quantile machinery; the runs say nothing about them.
"""

import hashlib
import inspect
import json
import math
import subprocess
import sys
import tempfile
import unittest
from datetime import date, time, timedelta
from functools import partial
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from repo_model import baseline, cli_eval, event_eval
from repo_model.baseline import (
    INTERVAL_PROBABILITY,
    BacktestReport,
    DegenerateRegimeError,
    ExceedanceCurves,
    FittedArx,
    FittedPersistence,
    FittedThreshold,
    Forecast,
    MissingRegressorError,
    ProvenanceMismatchError,
    SingularDesignError,
    UnobservedThresholdError,
    _dot,
    _feature_index,
    _least_squares,
    _quantile,
    arx_exceedance,
    backtest_document,
    climatology_exceedance,
    exceedance_backtest_document,
    fit,
    fit_arx,
    fit_threshold,
    rolling_exceedance_backtest,
    rolling_persistence_backtest,
    threshold_exceedance,
    twcrps_weights,
)
from repo_model.metrics import MetricError, brier_skill_score
from repo_model.contract import (
    QUANTILE_LEVELS,
    UndeclaredFeatureError,
    sources_for_features,
)
from repo_model.data import DailyObservation, load_daily_panel
from repo_model.registry import RegistryContractError
from repo_model.splits import LookAheadError, SplitError, rolling_origin

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
    `ExceedancePredictorCoverageTests` fails if an implementer arrives in
    `repo_model.baseline` without a case here.
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


def _exceedance_implementations():
    """Exceedance-predictor factories in `repo_model.baseline`, by name.

    Discovered, not listed, for the reason `_forecast_implementations` in
    `tests/test_contract.py` is: a list that has to be kept up to date would be
    updated in the same commit that added the implementer it was meant to catch.

    The marker is the declared return annotation. `baseline` has
    `from __future__ import annotations`, so annotations are strings and the
    comparison is against the name as written -- which is also the thing an
    author writes deliberately. A factory that returns an `ExceedancePredictor`
    and says so is in; a helper that happens to return a callable is not.
    """

    found = {}
    for name, obj in vars(baseline).items():
        if not inspect.isfunction(obj) or obj.__module__ != baseline.__name__:
            continue
        if getattr(obj, "__annotations__", {}).get("return") == "ExceedancePredictor":
            found[name] = obj
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
    """

    def test_every_exceedance_predictor_in_baseline_runs_the_conformance_suite(self):
        implementations = _exceedance_implementations()
        self.assertIn(
            "climatology_exceedance",
            implementations,
            msg="discovery found no climatology; the discovery is broken, not "
            "the module",
        )
        self.assertIn("arx_exceedance", implementations)

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
                f"{uncovered} return an ExceedancePredictor from "
                f"repo_model.baseline and no conformance case runs the "
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
        factories it can reach equals the set discovered in `baseline` -- both
        directions, because both failures are real. An implementer missing from
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
                f"{unreachable} return an ExceedancePredictor from "
                f"repo_model.baseline and no --model name reaches them. A "
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
                f"ExceedancePredictor in repo_model.baseline"
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
                    continuous, panel_path=self.panel, registry_path=self.registry
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

        Compared against `git` run from this test rather than against the
        record's own helper. Skipped where git is absent, which is the case the
        record answers by omitting the section entirely.
        """

        try:
            commit = subprocess.run(
                ("git", "rev-parse", "HEAD"),
                cwd=SAMPLE_PANEL.parents[2],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
            status = subprocess.run(
                ("git", "status", "--porcelain"),
                cwd=SAMPLE_PANEL.parents[2],
                capture_output=True,
                text=True,
                check=True,
            ).stdout
        except (OSError, subprocess.SubprocessError):  # pragma: no cover
            self.skipTest("git is not available here; the record omits the section")

        for name, build in self.builders():
            with self.subTest(document=name):
                code = build()["provenance"]["code"]
                self.assertEqual(code["commit"], commit)
                self.assertIn("tree_modified", code)
                self.assertIs(code["tree_modified"], bool(status.strip()))

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


if __name__ == "__main__":
    unittest.main()
