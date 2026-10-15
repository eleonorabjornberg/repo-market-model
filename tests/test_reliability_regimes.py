"""Reliability slope and intercept, pooled and within regimes (#683, finding #670).

A pooled reliability slope can read nearly calibrated while every regime inside it is badly over-spread: a regime with no pressure days
(2021-23) forecasts near 0, and adds a long, well-ordered stretch at the bottom of the curve. `repo_model.reliability_regimes` is the one
helper that returns the slope and intercept with a bootstrap interval, pooled and per regime (2018-19, 2020-24, 2025-26) and per any other
label the caller supplies (a scarcity state).

Serves H5 (calibration in 2018-19 and 2025-26) and H2. Development data only; nothing here is a verdict.

Recorded mutations, 13 October 2026, in a disposable copy of `src/repo_model/reliability_regimes.py`:
1. in `regime_of`, the 2018-19 edge `date(2019, 12, 31)` replaced by `date(2020, 12, 31)` (2020 is read as part of 2018-19).
   `test_the_regime_edges` then fails with `AssertionError: '2018-19' != '2020-24'`.
2. in `by_cell`, the per-cell fit given the pooled lists for every label (`_cell(probabilities, outcomes, **settings)`: each regime is given the
   pooled slope). `test_a_pooled_slope_can_hide_over_spread_regimes` then fails with `AssertionError: 0.7514317124571822 not greater than
   0.9514317124571823`, and two more tests fail.
Neither is a leakage guard; no mutation ritual is required for the rest.
"""

import unittest
from datetime import date

from repo_model import reliability_regimes as rr
from repo_model.metrics import MetricError


def _regime_a():
    """2018-19: over-spread. A high forecast (0.7) happens 45% of the time and a low one (0.1) 25%: the slope is well below 1."""

    p = [0.7] * 100 + [0.1] * 100
    y = [1] * 45 + [0] * 55 + [1] * 25 + [0] * 75
    return p, y


def _regime_b():
    """2021-23: no pressure day, forecasts near 0 and then a few small values, all ranked in the right order only by a margin."""

    p = [0.001] * 300 + [0.01] * 300
    y = [0] * 600
    return p, y


def _regime_c():
    """2025-26: a few events, forecasts ordered."""

    p = [0.5] * 40 + [0.05] * 160
    y = [1] * 18 + [0] * 22 + [1] * 8 + [0] * 152
    return p, y


class FitTests(unittest.TestCase):
    def test_a_calibrated_forecast_has_slope_one_and_intercept_zero(self):
        p = [0.2] * 100 + [0.6] * 100
        y = [1] * 20 + [0] * 80 + [1] * 60 + [0] * 40
        r = rr.fit(p, y)
        self.assertAlmostEqual(r.slope, 1.0, places=6)
        self.assertAlmostEqual(r.intercept, 0.0, places=6)

    def test_a_forecast_that_ranks_nothing_has_slope_zero(self):
        p = [0.2] * 100 + [0.6] * 100
        y = [1] * 40 + [0] * 60 + [1] * 40 + [0] * 60
        self.assertAlmostEqual(rr.fit(p, y).slope, 0.0, places=6)

    def test_an_over_spread_forecast_has_slope_below_one(self):
        p, y = _regime_a()
        self.assertLess(rr.fit(p, y).slope, 0.6)

    def test_a_constant_forecast_or_a_single_class_has_no_slope(self):
        self.assertIsNone(rr.fit([0.3, 0.3, 0.3], [0, 1, 0]))
        self.assertIsNone(rr.fit([0.2, 0.6], [0, 0]))
        self.assertIsNone(rr.fit([], []))

    def test_lengths_must_agree(self):
        with self.assertRaises(ValueError):
            rr.fit([0.2, 0.6], [0])

    def test_a_probability_outside_the_unit_interval_is_refused(self):
        with self.assertRaises(ValueError):
            rr.fit([0.2, 1.5], [0, 1])


class RegimeTests(unittest.TestCase):
    def test_the_regime_edges(self):
        self.assertEqual(rr.regime_of(date(2018, 6, 29)), "2018-19")
        self.assertEqual(rr.regime_of(date(2019, 12, 31)), "2018-19")
        self.assertEqual(rr.regime_of(date(2020, 1, 2)), "2020-24")
        self.assertEqual(rr.regime_of(date(2024, 12, 31)), "2020-24")
        self.assertEqual(rr.regime_of(date(2025, 1, 2)), "2025-26")
        self.assertEqual(rr.regime_of(date(2026, 9, 3)), "2025-26")

    def test_a_day_before_the_first_regime_is_refused(self):
        with self.assertRaises(ValueError):
            rr.regime_of(date(2017, 12, 29))


class ByCellTests(unittest.TestCase):
    def _data(self):
        pa, ya = _regime_a()
        pb, yb = _regime_b()
        pc, yc = _regime_c()
        p = pa + pb + pc
        y = ya + yb + yc
        labels = ["2018-19"] * len(pa) + ["2020-24"] * len(pb) + ["2025-26"] * len(pc)
        return p, y, labels

    def test_a_pooled_slope_can_hide_over_spread_regimes(self):
        p, y, labels = self._data()
        cells = rr.by_cell(p, y, labels, block_length=5, seed=1, replications=50)
        pooled = cells["pooled"]
        first = cells["2018-19"]
        self.assertIsNotNone(pooled.slope)
        self.assertIsNotNone(first.slope)
        self.assertGreater(pooled.slope, first.slope + 0.2)
        self.assertLess(first.slope, 0.6)

    def test_a_regime_without_events_has_no_slope_and_says_so(self):
        p, y, labels = self._data()
        cells = rr.by_cell(p, y, labels, block_length=5, seed=1, replications=50)
        quiet = cells["2020-24"]
        self.assertIsNone(quiet.slope)
        self.assertIsNone(quiet.intercept)
        self.assertEqual(quiet.events, 0)
        self.assertEqual(quiet.days, 600)

    def test_every_cell_reports_days_and_events_and_the_pooled_cell_comes_first(self):
        p, y, labels = self._data()
        cells = rr.by_cell(p, y, labels, block_length=5, seed=1, replications=50)
        self.assertEqual(list(cells)[0], "pooled")
        self.assertEqual(cells["pooled"].days, len(p))
        self.assertEqual(cells["pooled"].events, sum(y))
        self.assertEqual(sum(cells[k].days for k in cells if k != "pooled"), len(p))

    def test_the_interval_brackets_the_estimate_and_is_reproducible(self):
        p, y, labels = self._data()
        one = rr.by_cell(p, y, labels, block_length=5, seed=7, replications=100)
        two = rr.by_cell(p, y, labels, block_length=5, seed=7, replications=100)
        self.assertEqual(one, two)
        lo, hi = one["2018-19"].slope_interval
        self.assertLess(lo, one["2018-19"].slope)
        self.assertGreater(hi, one["2018-19"].slope)

    def test_a_cell_below_the_minimum_events_reports_no_interval(self):
        p, y, labels = self._data()
        cells = rr.by_cell(p, y, labels, block_length=5, seed=1, replications=50, minimum_events=100)
        self.assertIsNone(cells["2025-26"].slope_interval)
        self.assertIsNotNone(cells["2025-26"].slope)

    def test_labels_must_match_the_days(self):
        with self.assertRaises(ValueError):
            rr.by_cell([0.1, 0.2], [0, 1], ["a"], block_length=2, seed=1)

    def test_the_bootstrap_arguments_are_required(self):
        with self.assertRaises(TypeError):
            rr.by_cell([0.1, 0.2], [0, 1], ["a", "a"])
        with self.assertRaises(MetricError):
            rr.by_cell([0.1, 0.2], [0, 1], ["a", "a"], block_length=0.5, seed=1)

    def test_labels_are_sorted_and_a_figure_without_an_interval_is_marked(self):
        p, y, labels = self._data()
        cells = rr.by_cell(p, y, labels[::-1], block_length=5, seed=1, replications=50, minimum_events=100)
        self.assertEqual(list(cells), ["pooled", "2018-19", "2020-24", "2025-26"])
        text = rr.markdown_table(cells)
        self.assertIn("†", text)

    def test_the_markdown_table_names_every_cell_and_restates_the_reading(self):
        p, y, labels = self._data()
        cells = rr.by_cell(p, y, labels, block_length=5, seed=1, replications=50)
        text = rr.markdown_table(cells)
        for name in ("pooled", "2018-19", "2020-24", "2025-26"):
            self.assertIn(f"| {name} |", text)
        self.assertIn("undefined", text)


if __name__ == "__main__":
    unittest.main()
