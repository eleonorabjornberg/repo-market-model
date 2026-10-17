"""`scripts/b1_alignment_850.py`: B1 with h-row and with h + 1-row changes, side by side (#850, H9 step 2, finding #744).

The script measures and changes nothing in `richer_targets.b1_quantiles`. These tests pin the two arms, the coverage rule and
the reading of a ranking, on a series whose answer is known.
"""

from __future__ import annotations

import importlib.util
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import richer_targets
from repo_model.scoring_protocol import GRID

ROOT = Path(__file__).resolve().parents[1]


def _script():
    spec = importlib.util.spec_from_file_location("b1_alignment_850_test", ROOT / "scripts" / "b1_alignment_850.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _weekdays(count: int):
    out, day = [], date(2019, 1, 1)
    while len(out) < count:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


class ArmTests(unittest.TestCase):
    def test_the_h_arm_is_the_shipped_b1_and_the_other_arm_uses_one_more_row(self):
        script = _script()
        dates = _weekdays(200)
        values = [float((k * k) % 17) for k in range(200)]
        anchor, lead = 150, 2
        arms = script.b1_arms(values, dates, anchor, lead, first=0)
        self.assertEqual(arms[0], richer_targets.b1_quantiles(values, dates, anchor, lead, first=0))
        self.assertEqual(arms[1], richer_targets.b1_quantiles(values, dates, anchor, lead + 1, first=0))
        self.assertNotEqual(arms[0], arms[1])

    def test_a_day_either_arm_cannot_form_is_dropped_for_both(self):
        script = _script()
        dates = _weekdays(70)
        values = [float(k % 5) for k in range(70)]
        # 60 changes of one row exist in rows 1..60 but only 59 of two rows: the h + 1 arm cannot form, so neither arm is used
        self.assertIsNotNone(richer_targets.b1_quantiles(values, dates, 60, 1, first=1))
        self.assertIsNone(script.b1_arms(values, dates, 60, 1, first=1))


class CoverageTests(unittest.TestCase):
    def test_central_interval_is_closed_at_the_fifth_and_ninety_fifth_levels(self):
        script = _script()
        quantiles = [float(k) for k in range(len(GRID))]
        low, high = quantiles[GRID.index(0.05)], quantiles[GRID.index(0.95)]
        self.assertTrue(script.covered(quantiles, low))
        self.assertTrue(script.covered(quantiles, high))
        self.assertFalse(script.covered(quantiles, low - 0.01))
        self.assertFalse(script.covered(quantiles, high + 0.01))


class RankingTests(unittest.TestCase):
    def test_ranking_is_the_sign_of_the_climatology_minus_persistence_score(self):
        script = _script()
        self.assertEqual(script.ranking(1.0, 2.0), "B1")
        self.assertEqual(script.ranking(2.0, 1.0), "B2")
        self.assertEqual(script.ranking(1.0, 1.0), "tie")

    def test_a_cell_reports_a_flip_only_when_the_two_arms_rank_differently(self):
        script = _script()
        days = [date(2019, 1, 1) + timedelta(days=k) for k in range(100)]
        cell = script.arm_cell(
            crps_h=[1.0] * 100, crps_h1=[1.5] * 100, crps_b2=[3.0] * 100,
            covered_h=[True] * 100, covered_h1=[False] * 100, days=days, seed=1, draws=50,
        )
        self.assertEqual(cell["rank_h"], "B1")
        self.assertEqual(cell["rank_h1"], "B1")
        self.assertFalse(cell["flip"])
        flipped = script.arm_cell(
            crps_h=[1.0] * 100, crps_h1=[3.5] * 100, crps_b2=[3.0] * 100,
            covered_h=[True] * 100, covered_h1=[False] * 100, days=days, seed=1, draws=50,
        )
        self.assertEqual(flipped["rank_h"], "B1")
        self.assertEqual(flipped["rank_h1"], "B2")
        self.assertTrue(flipped["flip"])
        self.assertEqual(flipped["coverage_h"], 1.0)
        self.assertEqual(flipped["coverage_h1"], 0.0)


if __name__ == "__main__":
    unittest.main()
