"""Derived features and lagged pressure (#631): `repo_model.derived_features`.

What is covered:

* `CausalViewTests` -- a reader sees a series only up to its own row; a later index is a `LookAheadError`.
* `ReaderTests` -- the arithmetic of each reader on a series worked by hand: realised volatility, the above-median run, the days
  since the last pressure day (outcomes counted only from their own row), lags, and the range statistics.
* `CalendarTests` -- day of the month, and the position in the maintenance period.
* `BuildTests` -- no later row moves an earlier value; a column that reads a later row is refused by `check_columns_causal`.

**Recorded mutations** (disposable copy of the tree, `/opt/rmm-venv`, `PYTHONDONTWRITEBYTECODE=1`, the killing test run alone, each
confirmed applied by `grep` and restored before the next):

1. `Causal.__getitem__`: replace `if index > self.end:` by `if False:`. A reader can read a later row;
   `CausalViewTests.test_a_later_row_is_refused` fails with `AssertionError: LookAheadError not raised`.
2. `check_columns_causal`: replace `if (have is None) != (want is None) or (have is not None and abs(have - want) > 1e-12):` by
   `if False:`. A column built from a later row is no longer refused;
   `BuildTests.test_a_column_that_reads_a_later_row_is_refused` fails with `AssertionError: LookAheadError not raised`.
3. `days_since_pressure`: replace `for i in range(view.end, -1, -1):` by `for i in range(view.end + 1, -1, -1):`. The reader asks the
   view for the row after its own, and the view refuses; `ReaderTests.test_days_since_pressure_counts_only_outcomes_up_to_the_row`
   errors with `LookAheadError`.
"""

from __future__ import annotations

import math
import unittest
from datetime import date, timedelta

from repo_model import derived_features as df
from repo_model.data import DailyObservation
from repo_model.splits import LookAheadError


def _rows(spreads_bp, start=date(2024, 1, 2)):
    rows = []
    for k, s in enumerate(spreads_bp):
        rows.append(DailyObservation(start + timedelta(days=k), {"sofr": 5.0 + s / 100.0, "iorb": 5.0, "tgcr": 5.0 + k / 1000.0}))
    return rows


class CausalViewTests(unittest.TestCase):
    def test_a_later_row_is_refused(self):
        view = df.Causal([1.0, 2.0, 3.0, 4.0], 2)
        self.assertEqual(view[2], 3.0)
        with self.assertRaises(LookAheadError):
            view[3]

    def test_last_needs_a_full_window_without_holes(self):
        self.assertEqual(df.Causal([1.0, 2.0, 3.0], 2).last(3), [1.0, 2.0, 3.0])
        self.assertIsNone(df.Causal([1.0, 2.0, 3.0], 2).last(4))
        self.assertIsNone(df.Causal([1.0, None, 3.0], 2).last(3))


class ReaderTests(unittest.TestCase):
    def test_realised_vol_is_the_sample_sd_of_one_day_changes(self):
        values = [0.0, 1.0, 3.0, 2.0]  # changes 1, 2, -1
        mean = 2.0 / 3.0
        want = math.sqrt(sum((c - mean) ** 2 for c in (1.0, 2.0, -1.0)) / 2)
        self.assertAlmostEqual(df.realised_vol(df.Causal(values, 3), 3), want)
        self.assertIsNone(df.realised_vol(df.Causal(values, 3), 4))

    def test_above_median_run_counts_back_from_this_row(self):
        values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]  # median of the last 7 is 4; the last three are above it
        self.assertEqual(df.above_median_run(df.Causal(values, 6), 7, 3), 3.0)
        self.assertEqual(df.above_median_run(df.Causal([7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0], 6), 7, 3), 0.0)
        self.assertIsNone(df.above_median_run(df.Causal(values, 1), 7, 3))

    def test_days_since_pressure_counts_only_outcomes_up_to_the_row(self):
        values = [0.0, 6.0, 0.0, 0.0, 9.0]  # +5 bp is strictly exceeded on rows 1 and 4
        self.assertIsNone(df.days_since_pressure(df.Causal(values, 0), 5.0))
        self.assertEqual(df.days_since_pressure(df.Causal(values, 1), 5.0), 0.0)
        self.assertEqual(df.days_since_pressure(df.Causal(values, 3), 5.0), 2.0)
        # a day exactly on the threshold is not a pressure day
        self.assertIsNone(df.days_since_pressure(df.Causal([5.0, 5.0], 1), 5.0))

    def test_change_is_the_value_less_the_earlier_one(self):
        view = df.Causal([1.0, 2.0, 4.0, 7.0], 3)
        self.assertEqual(df.change(view, 2), 5.0)
        self.assertIsNone(df.change(view, 4))
        self.assertIsNone(df.change(df.Causal([1.0, None, 4.0], 2), 1))

    def test_lag_and_range_statistics(self):
        view = df.Causal([1.0, 2.0, 4.0, 3.0], 3)
        self.assertEqual(df.lagged(view, 0), 3.0)
        self.assertEqual(df.lagged(view, 2), 2.0)
        self.assertIsNone(df.lagged(view, 4))
        stats = df.range_stats(view, 4, scale=100.0)
        self.assertAlmostEqual(stats["min_dist"], 200.0)
        self.assertAlmostEqual(stats["max_dist"], 100.0)
        mean, sd = 2.5, math.sqrt(sum((v - 2.5) ** 2 for v in (1, 2, 4, 3)) / 3)
        self.assertAlmostEqual(stats["z"], (3.0 - mean) / sd)
        self.assertIsNone(df.range_stats(df.Causal([2.0, 2.0, 2.0], 2), 3)["z"])


class CalendarTests(unittest.TestCase):
    def test_business_day_of_month(self):
        self.assertEqual(df.bday_of_month(date(2024, 1, 2)), 1.0)  # 1 January is a holiday
        self.assertEqual(df.bday_of_month(date(2024, 2, 1)), 1.0)
        self.assertEqual(df.bday_of_month(date(2024, 2, 5)), 3.0)

    def test_maintenance_period_day(self):
        self.assertEqual(df.maint_period_day(date(2019, 4, 25)), 0.0)  # a Thursday
        self.assertEqual(df.maint_period_day(date(2019, 5, 8)), 13.0)  # the Wednesday that ends it
        self.assertEqual(df.maint_period_day(date(2019, 5, 9)), 0.0)
        self.assertEqual(df.maint_period_day(date(2018, 4, 12)), 0.0)  # whole periods before the anchor


class BuildTests(unittest.TestCase):
    SPEC_ARGS = dict(
        rates=("tgcr",), windows=(3,), median_window=5, median_minimum=3, vol_days=(2,), lags=(1, 2), threshold_bp=5.0
    )

    def setUp(self):
        self.rows = _rows([1.0, 2.0, 9.0, 3.0, 8.0, 1.0, 0.0, 6.0, 2.0, 2.0])
        self.spec = df.columns_for(**self.SPEC_ARGS)

    def test_no_later_row_moves_an_earlier_value(self):
        whole = df.build_columns(self.rows, self.spec)
        for i in (3, 5, 8):
            cut = df.build_columns(self.rows[: i + 1], self.spec)
            for name in self.spec:
                self.assertEqual(whole[name][i], cut[name][i], name)
        df.check_columns_causal(self.rows, self.spec, whole, indices=range(len(self.rows)))

    def test_pressure_columns_read_the_spread_of_their_own_rows(self):
        built = df.build_columns(self.rows, self.spec)
        self.assertEqual(built["pressure_last"][2], 1.0)
        self.assertEqual(built["pressure_lag1"][3], 1.0)
        self.assertEqual(built["pressure_lag2"][4], 1.0)
        self.assertIsNone(built["pressure_lag2"][1])
        self.assertAlmostEqual(built["spread_lag1"][4], self.rows[3].spread_bps)

    def test_a_column_that_reads_a_later_row_is_refused(self):
        spec = dict(self.spec)
        # a planted look-ahead that bypasses the view: it reads the next row of the series it was handed
        spec["leak"] = ("spread_bps", lambda view: view._values[min(view.end + 1, len(view._values) - 1)])
        built = df.build_columns(self.rows, spec)
        with self.assertRaises(LookAheadError):
            df.check_columns_causal(self.rows, spec, built, indices=range(len(self.rows)))


if __name__ == "__main__":
    unittest.main()
