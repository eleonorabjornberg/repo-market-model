import inspect
import sys
import unittest
from datetime import date, timedelta
from functools import partial
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from repo_model.baseline import (
    INTERVAL_PROBABILITY,
    FittedArx,
    FittedPersistence,
    MissingRegressorError,
    SingularDesignError,
    _dot,
    _least_squares,
    _quantile,
    fit,
    fit_arx,
    rolling_persistence_backtest,
)
from repo_model.contract import QUANTILE_LEVELS
from repo_model.data import DailyObservation, load_daily_panel

SAMPLE_PANEL = Path(__file__).parents[1] / "data" / "sample" / "daily_market.csv"

#: The regressor set every ARX in this module is fitted on, named once. Two
#: columns that actually move on the sample panel; `quarter_end` is constant and
#: `mmf_assets` is empty throughout, and both are refused rather than fitted --
#: see `FittedArxTests.test_a_degenerate_regressor_set_is_refused_not_approximated`.
REGRESSORS = ("sofr_volume", "on_rrp")


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
        report = rolling_persistence_backtest(rows, minimum_history=10)
        self.assertEqual(len(report.forecasts), 20)
        self.assertAlmostEqual(report.mae_bps, 1.0)
        self.assertTrue(0.0 <= report.interval_coverage <= 1.0)

    def test_requires_history(self):
        rows = [
            DailyObservation(date(2026, 1, 1), {"sofr": 4.31, "iorb": 4.30}),
            DailyObservation(date(2026, 1, 2), {"sofr": 4.32, "iorb": 4.30}),
        ]
        with self.assertRaisesRegex(ValueError, "not enough"):
            rolling_persistence_backtest(rows, minimum_history=2)


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
        report = rolling_persistence_backtest(rows, minimum_history=self.MINIMUM_HISTORY)

        # The run reports the model it finished on, and that model can say what
        # it was fitted at. A report that cannot name its own cutoff is the
        # thing "every fitted object carries the cutoff" exists to prevent.
        self.assertIsInstance(report.model, FittedPersistence)
        self.assertEqual(report.model.cutoff, rows[-2].date)

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
        default = rolling_persistence_backtest(rows, minimum_history=self.MINIMUM_HISTORY)
        restated = rolling_persistence_backtest(
            rows, minimum_history=self.MINIMUM_HISTORY, interval_probability=0.90
        )
        self.assertEqual(list(default.forecasts), list(restated.forecasts))

        # An interval the declared levels do not produce is refused rather than
        # honoured. Honouring it would put the reported coverage and the
        # reported interval out of step, silently.
        with self.assertRaisesRegex(ValueError, "declared levels"):
            rolling_persistence_backtest(
                rows, minimum_history=self.MINIMUM_HISTORY, interval_probability=0.50
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
        report = rolling_persistence_backtest(
            rows, minimum_history=self.MINIMUM_HISTORY, fit_model=fitter
        )

        self.assertIsInstance(report.model, FittedArx)
        self.assertEqual(report.model.regressors, REGRESSORS)
        self.assertEqual(report.model.cutoff, rows[-2].date)

        for position, forecast in enumerate(report.forecasts):
            index = self.MINIMUM_HISTORY + position
            model = fit_arx(
                rows[:index], REGRESSORS, minimum_history=self.MINIMUM_HISTORY
            )
            quantiles = model.predict(rows[index - 1])
            self.assertEqual(
                forecast.predicted_bps, model.point_forecast(rows[index - 1])
            )
            self.assertEqual(forecast.lower_bps, quantiles[0])
            self.assertEqual(forecast.upper_bps, quantiles[-1])
            self.assertEqual(forecast.actual_bps, rows[index].spread_bps)

        # The point forecast is the ARX's regression mean, not the last observed
        # spread. A backtest that read the centre off the feature row would
        # report persistence's point rule beside the ARX's intervals, and the
        # MAE would be persistence's however the model was fitted.
        persistence = rolling_persistence_backtest(
            rows, minimum_history=self.MINIMUM_HISTORY
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
        default = rolling_persistence_backtest(rows, minimum_history=self.MINIMUM_HISTORY)
        explicit = rolling_persistence_backtest(
            rows, minimum_history=self.MINIMUM_HISTORY, fit_model=fit
        )

        self.assertIsInstance(default.model, FittedPersistence)
        self.assertEqual(list(default.forecasts), list(explicit.forecasts))
        self.assertEqual(default.mae_bps, explicit.mae_bps)
        self.assertEqual(default.interval_coverage, explicit.interval_coverage)

        # The persistence point rule is still the last observed spread, read off
        # the model rather than off the feature row but identical to it.
        for position, forecast in enumerate(default.forecasts):
            index = self.MINIMUM_HISTORY + position
            self.assertEqual(forecast.predicted_bps, rows[index - 1].spread_bps)

        self.assertEqual(len(default.forecasts), 15)
        self.assertAlmostEqual(default.mae_bps, 13.0 / 15.0, places=12)
        self.assertAlmostEqual(default.interval_coverage, 11.0 / 15.0, places=12)


if __name__ == "__main__":
    unittest.main()
