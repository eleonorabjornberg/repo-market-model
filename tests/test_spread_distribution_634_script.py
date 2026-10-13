"""The measurement script of #634 (`scripts/spread_distribution_634.py`): the parts that decide what is scored.

Recorded mutation (the one guard this script adds; the scorer's own lockbox guard is tested with the scorer):

* `refuse_locked`, the call `require_unlocked(list(days), ...)` replaced by `return`: `test_a_locked_day_is_refused`
  fails with `AssertionError` (`LookAheadError not raised`; the blind tier is every day after 2026-09-03, `metadata/lockbox.json`).
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("spread_distribution_634_script", REPO / "scripts" / "spread_distribution_634.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402


def business_days(start: date, count: int):
    days, day = [], start
    while len(days) < count:
        if day.weekday() < 5:
            days.append(day)
        day += timedelta(days=1)
    return days


class LeadForecastTests(unittest.TestCase):
    def setUp(self):
        self.calendar = business_days(date(2024, 3, 1), 12)

    def laws(self, targets_by_lead):
        return {h: {self.calendar[i]: [float(h * 100 + i)] * len(sp.GRID) for i in targets_by_lead[h]} for h in sp.HORIZONS}

    def test_a_decision_day_takes_the_law_of_the_target_h_days_later(self):
        laws = self.laws({h: range(h, 12) for h in sp.HORIZONS})
        forecasts, days = script.lead_forecasts(laws, self.calendar)
        self.assertEqual(days[0], self.calendar[0])
        for h in sp.HORIZONS:
            self.assertEqual(forecasts[self.calendar[0]][h][0], h * 100 + h)
            self.assertEqual(forecasts[self.calendar[2]][h][0], h * 100 + 2 + h)

    def test_only_the_days_every_lead_covers_are_decision_days(self):
        laws = self.laws({1: range(1, 12), 2: range(2, 12), 3: range(3, 12), 4: range(4, 12), 5: range(5, 11)})
        _forecasts, days = script.lead_forecasts(laws, self.calendar)
        # lead 5 starts at target 5 (decision day 0) and ends at target 10 (decision day 5)
        self.assertEqual(days, self.calendar[0:6])

    def test_a_missing_law_is_kept_as_missing_not_dropped(self):
        laws = self.laws({h: range(h, 12) for h in sp.HORIZONS})
        laws[3][self.calendar[3]] = None
        forecasts, days = script.lead_forecasts(laws, self.calendar)
        self.assertIn(self.calendar[0], days)
        self.assertIsNone(forecasts[self.calendar[0]][3])

    def test_a_target_off_the_calendar_is_refused(self):
        laws = self.laws({h: range(h, 12) for h in sp.HORIZONS})
        laws[1][date(2030, 1, 2)] = [0.0] * len(sp.GRID)
        with self.assertRaises(ValueError):
            script.lead_forecasts(laws, self.calendar)


class ScoreCellTests(unittest.TestCase):
    def test_cells_drop_targets_without_an_outcome_and_day_means_average_the_admitted_leads(self):
        calendar = business_days(date(2024, 3, 1), 12)
        flat = [0.0] * len(sp.GRID)
        forecasts = {calendar[0]: {h: flat for h in sp.HORIZONS}}
        outcomes = {calendar[h]: float(h) for h in sp.HORIZONS}
        outcomes[calendar[3]] = None
        cells = script.cell_scores(forecasts, outcomes, calendar, sp.grid_crps)
        self.assertEqual(sorted(h for _d, h in cells), [1, 2, 4, 5])
        mean_all = script.day_means(cells, lambda d, h: True)[calendar[0]]
        self.assertAlmostEqual(mean_all, sum(cells.values()) / 4.0)
        only_even = script.day_means(cells, lambda d, h: h % 2 == 0)
        self.assertAlmostEqual(only_even[calendar[0]], (cells[(calendar[0], 2)] + cells[(calendar[0], 4)]) / 2.0)
        self.assertEqual(script.day_means(cells, lambda d, h: False), {})


class OnGridTests(unittest.TestCase):
    LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]
    LAW = [-6.0, -3.0, -1.0, 0.0, 4.0]

    def test_the_law_returns_its_own_quantiles_at_its_own_levels(self):
        out = script.on_grid(self.LAW, self.LEVELS)
        for level, value in zip(self.LEVELS, self.LAW):
            self.assertAlmostEqual(out[sp.GRID.index(level)], value, places=4)

    def test_the_result_is_on_the_protocols_grid_and_ordered_with_tails_outside_the_fitted_ones(self):
        out = script.on_grid(self.LAW, self.LEVELS)
        self.assertEqual(len(out), len(sp.GRID))
        self.assertEqual(out, sorted(out))
        self.assertLess(out[0], self.LAW[0])
        self.assertGreater(out[-1], self.LAW[-1])


class LockboxTests(unittest.TestCase):
    def test_a_locked_day_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.refuse_locked([date(2025, 12, 31), date(2026, 9, 10)])
        script.refuse_locked([date(2025, 12, 30), date(2025, 12, 31)])


class ExceedanceTests(unittest.TestCase):
    def test_a_law_wholly_below_the_threshold_has_a_small_exceedance_and_the_reading_falls_with_the_threshold(self):
        law = [-8.0 + 0.5 * k for k in range(len(sp.GRID))]
        probabilities = [script.exceedance(law, tau) for tau in script.THRESHOLDS_BP]
        self.assertEqual(probabilities, sorted(probabilities, reverse=True))
        self.assertTrue(all(0.0 <= p <= 1.0 for p in probabilities))
        self.assertEqual(script.brier(0.25, True), 0.5625)
        self.assertEqual(script.brier(0.25, False), 0.0625)


if __name__ == "__main__":
    unittest.main()
