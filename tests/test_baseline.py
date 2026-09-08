import inspect
import json
import math
import sys
import unittest
from datetime import date, time, timedelta
from functools import partial
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from repo_model import baseline
from repo_model.baseline import (
    INTERVAL_PROBABILITY,
    ExceedanceCurves,
    FittedArx,
    FittedPersistence,
    Forecast,
    MissingRegressorError,
    SingularDesignError,
    _dot,
    _feature_index,
    _least_squares,
    _quantile,
    arx_exceedance,
    climatology_exceedance,
    fit,
    fit_arx,
    rolling_persistence_backtest,
)
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
        resolves to. That the *real* registry refuses to price those sources at
        all is a separate fact, pinned by
        `test_the_real_registry_refuses_every_feature_set_that_reads_iorb`.
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

    def test_the_real_registry_refuses_every_feature_set_that_reads_iorb(self):
        """The `snapshot_retrieved_at` guard, firing for the first time.

        `iorb` is required, `spread_bps` is computed from it, and every model
        here reads `spread_bps` -- so every feature set resolves to
        `fred_macro_latest_vintage`, whose basis is `snapshot_retrieved_at`. The
        contract says such a source contributes no purge and MUST NOT be mapped
        to zero, and `max_release_lag_days` raises unless every row carries
        `available_at`. `DailyObservation` carries no `available_at`, so it
        raises.

        **This is a correct guard firing, not a bug**, and it is pinned here
        rather than worked around: the resolution is a Track A question about
        `available_at` on the daily panel, and this test is what will go red on
        the day that question is answered -- which is the right alarm, because
        every benchmark number in the project changes that day.
        """

        rows = self.sample()
        real = json.loads(REAL_REGISTRY.read_text(encoding="utf-8"))
        with self.assertRaises(RegistryContractError) as caught:
            rolling_persistence_backtest(
                rows,
                features=FEATURES,
                registry=real,
                decision_time=DECISION_TIME,
                minimum_history=self.MINIMUM_HISTORY,
            )
        self.assertIn("fred_macro_latest_vintage", str(caught.exception))
        self.assertIn("available_at", str(caught.exception))

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


if __name__ == "__main__":
    unittest.main()
