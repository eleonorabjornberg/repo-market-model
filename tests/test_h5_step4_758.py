"""The H5 step 4 comparison (`scripts/h5_step4_758.py`, #758): the parts that decide what is read.

Recorded mutation (the one leakage guard this script adds; the scorer's own lockbox guard is tested with the scorer):

* `refuse_after_last_day`, the condition `day > LAST_DAY` changed to `day > LAST_DAY + timedelta(days=400)`:
  `test_a_day_after_the_last_development_day_is_refused` fails with `AssertionError` (`LookAheadError not raised`, for
  2026-01-02).
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("h5_step4_758_script", REPO / "scripts" / "h5_step4_758.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model.splits import LookAheadError  # noqa: E402


class GuardTests(unittest.TestCase):
    def test_a_day_after_the_last_development_day_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.refuse_after_last_day([date(2025, 12, 31), date(2026, 1, 2)])
        script.refuse_after_last_day([date(2025, 12, 30), date(2025, 12, 31)])


class HeadroomTests(unittest.TestCase):
    days = [date(2024, 1, 1) + timedelta(days=i) for i in range(40)]

    def scores(self, base, step=0.0):
        return {d: base + step * (i % 3) for i, d in enumerate(self.days)}

    def test_headroom_is_the_gap_of_the_two_means_over_the_benchmark_mean(self):
        b1, ceiling = self.scores(2.0), self.scores(1.0)
        candidate = {d: v + 0.2 for d, v in ceiling.items()}
        cell = script.headroom(b1, candidate, ceiling, draws=200, seed=1)
        self.assertAlmostEqual(cell["headroom"], 0.1)
        self.assertAlmostEqual(cell["interval_90"][0], 0.1)
        self.assertAlmostEqual(cell["interval_90"][1], 0.1)

    def test_a_candidate_ahead_of_the_ceiling_has_negative_headroom(self):
        b1, ceiling = self.scores(2.0), self.scores(1.5)
        candidate = {d: v - 0.1 for d, v in ceiling.items()}
        self.assertLess(script.headroom(b1, candidate, ceiling, draws=100, seed=1)["headroom"], 0.0)

    def test_the_interval_widens_when_the_gap_varies(self):
        b1 = self.scores(2.0)
        ceiling = self.scores(1.0, 0.3)
        candidate = {d: 1.0 + 0.4 * (i % 5) / 4 for i, d in enumerate(self.days)}
        cell = script.headroom(b1, candidate, ceiling, draws=300, seed=1)
        self.assertLess(cell["interval_90"][0], cell["interval_90"][1])

    def test_series_on_different_days_are_refused(self):
        b1, ceiling = self.scores(2.0), self.scores(1.0)
        candidate = dict(list(self.scores(1.2).items())[:-1])
        with self.assertRaises(ValueError):
            script.headroom(b1, candidate, ceiling, draws=10, seed=1)


class ReadingTests(unittest.TestCase):
    def cells(self, **lowers):
        return {name: {"n": 200, "headroom": 0.05, "interval_90": [low, 0.2]} for name, low in lowers.items()}

    def test_headroom_nowhere_stops(self):
        reading = script.recommend(self.cells(pooled=-0.01, **{"regime: 2021-23": 0.0}))
        self.assertEqual(reading["recommendation"], "stop at the best available candidate")
        self.assertEqual(reading["where"], [])

    def test_a_shown_split_continues_and_is_named(self):
        reading = script.recommend(self.cells(pooled=-0.01, **{"regime: 2021-23": 0.02}))
        self.assertEqual(reading["recommendation"], "continue model work")
        self.assertEqual(reading["where"], ["regime: 2021-23"])

    def test_a_thin_split_is_not_shown(self):
        cells = self.cells(pooled=-0.01, **{"regime: 2020": 0.05})
        cells["regime: 2020"]["n"] = 29
        self.assertEqual(script.recommend(cells)["recommendation"], "stop at the best available candidate")

    def test_the_pooled_cell_alone_is_enough_to_continue(self):
        reading = script.recommend(self.cells(pooled=0.01))
        self.assertEqual(reading["recommendation"], "continue model work")
        self.assertEqual(reading["where"], ["pooled"])


class ReproductionTests(unittest.TestCase):
    def test_a_rerun_that_misses_the_recorded_skill_is_refused(self):
        script.require_reproduced({"reachable gbm": 0.1921, "ceiling gbm": 0.1624}, {"reachable gbm": 0.192, "ceiling gbm": 0.162})
        with self.assertRaises(ValueError):
            script.require_reproduced({"reachable gbm": 0.1921, "ceiling gbm": 0.171}, {"reachable gbm": 0.192, "ceiling gbm": 0.162})


if __name__ == "__main__":
    unittest.main()
