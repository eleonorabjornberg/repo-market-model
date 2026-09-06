import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from repo_model.baseline import rolling_persistence_backtest
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


if __name__ == "__main__":
    unittest.main()

