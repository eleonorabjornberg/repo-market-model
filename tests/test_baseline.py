import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from repo_model.baseline import (
    INTERVAL_PROBABILITY,
    FittedPersistence,
    fit,
    rolling_persistence_backtest,
)
from repo_model.contract import QUANTILE_LEVELS
from repo_model.data import DailyObservation


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


if __name__ == "__main__":
    unittest.main()

