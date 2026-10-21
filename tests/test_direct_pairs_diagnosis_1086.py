"""The 2021-23 diagnosis of the direct-pairs variant (`scripts/direct_pairs_diagnosis_1086.py`, #1086, H5 step 3): the arithmetic on hand cases.

The study reads walks and a panel; what is pinned here is the arithmetic that turns them into the page's figures, and the two guards the script adds:
it reads no day after 2025-12-31 and no locked day.

* `level_losses` splits `scoring_protocol.grid_crps` into the 23 levels' shares, so the shares of a cell sum to the cell's score.
* `decompose` reports the excess loss (candidate minus reference) by lead, by target day type and by level, and by band of levels; a sum over bands is the
  sum over levels, which is the sum over leads weighted by their days.
* `effective_sample` is n (1 - r) / (1 + r) for the lag-1 autocorrelation r of the target series, floored at r = 0.
* `training_summary` counts the floor-regime pairs of a training set and divides them by the leaf size.

Recorded mutations:

* `require_study_window`, the line `if late:` changed to `if False:`: `StudyWindowTests.test_a_day_after_the_study_end_is_refused` fails with
  `AssertionError` (`LookAheadError not raised`).
* `level_losses`, the divisor `len(GRID)` changed to `(len(GRID) - 1)`: `LevelLossTests.test_the_levels_sum_to_the_grid_crps` fails with
  `AssertionError` (`2.2795 != 2.1804 within 9 places`: the levels no longer sum to `sp.grid_crps`).
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("direct_pairs_diagnosis_1086_script", REPO / "scripts" / "direct_pairs_diagnosis_1086.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

GRID = sp.GRID


def law(centre, width):
    """A 23-quantile law, ascending, centred on `centre`."""

    return [centre + width * (level - 0.5) for level in GRID]


class StudyWindowTests(unittest.TestCase):
    def test_a_day_after_the_study_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.require_study_window([date(2026, 1, 2)])

    def test_the_last_study_day_is_read(self):
        script.require_study_window([date(2025, 12, 31)])


class LevelLossTests(unittest.TestCase):
    def test_the_levels_sum_to_the_grid_crps(self):
        for centre, width, observed in ((0.0, 4.0, 3.0), (-10.0, 1.0, -9.0), (5.0, 30.0, -20.0)):
            q = law(centre, width)
            self.assertAlmostEqual(sum(script.level_losses(q, observed)), sp.grid_crps(q, observed), places=9)

    def test_a_level_is_twice_its_pinball_over_the_grid_size(self):
        q = law(0.0, 2.0)
        losses = script.level_losses(q, 10.0)
        # the median is below the outcome: pinball(0.5) = 0.5 * (10 - q50)
        self.assertAlmostEqual(losses[GRID.index(0.5)], 2.0 * 0.5 * (10.0 - q[GRID.index(0.5)]) / len(GRID))

    def test_the_wrong_number_of_quantiles_is_refused(self):
        with self.assertRaises(ValueError):
            script.level_losses([0.0, 1.0], 0.0)


class BandTests(unittest.TestCase):
    def test_every_level_is_in_one_band_and_the_bands_are_declared(self):
        names = {script.band_of(level) for level in GRID}
        self.assertEqual(names, set(script.BANDS))
        self.assertEqual(script.band_of(0.01), "lower_tail")
        self.assertEqual(script.band_of(0.10), "lower_tail")
        self.assertEqual(script.band_of(0.25), "centre")
        self.assertEqual(script.band_of(0.75), "centre")
        self.assertEqual(script.band_of(0.90), "upper_tail")
        self.assertEqual(script.band_of(0.15), "lower_shoulder")
        self.assertEqual(script.band_of(0.85), "upper_shoulder")


class DecomposeTests(unittest.TestCase):
    def rows(self):
        wide, narrow = law(0.0, 20.0), law(0.0, 2.0)
        return [
            script.Cell(lead=1, kind="ordinary", reference=narrow, candidate=wide, observed=0.0),
            script.Cell(lead=1, kind="month_end", reference=narrow, candidate=wide, observed=1.0),
            script.Cell(lead=2, kind="ordinary", reference=narrow, candidate=narrow, observed=0.0),
        ]

    def test_an_identical_forecast_has_no_excess(self):
        out = script.decompose(self.rows())
        self.assertEqual(out["lead 2"]["total"], 0.0)
        self.assertEqual(out["lead 2"]["by_level"], [0.0] * len(GRID))

    def test_the_total_is_the_mean_difference_of_the_grid_crps(self):
        cells = self.rows()
        out = script.decompose(cells)
        expected = sum(sp.grid_crps(c.candidate, c.observed) - sp.grid_crps(c.reference, c.observed) for c in cells[:2]) / 2
        self.assertAlmostEqual(out["lead 1"]["total"], expected, places=9)
        self.assertEqual(out["lead 1"]["days"], 2)

    def test_the_bands_sum_to_the_total_and_the_levels_to_the_total(self):
        out = script.decompose(self.rows())
        for group in out.values():
            self.assertAlmostEqual(sum(group["by_level"]), group["total"], places=9)
            self.assertAlmostEqual(sum(group["by_band"].values()), group["total"], places=9)

    def test_a_wider_candidate_loses_in_the_tails_on_a_centred_outcome(self):
        group = script.decompose(self.rows())["lead 1"]
        self.assertGreater(group["by_band"]["lower_tail"], 0.0)
        self.assertGreater(group["by_band"]["upper_tail"], 0.0)

    def test_groups_are_by_lead_by_kind_and_all(self):
        out = script.decompose(self.rows())
        self.assertEqual(set(out), {"all", "lead 1", "lead 2", "ordinary", "month_end"})
        self.assertEqual(out["all"]["days"], 3)

    def test_an_empty_input_is_refused(self):
        with self.assertRaises(ValueError):
            script.decompose([])


class EffectiveSampleTests(unittest.TestCase):
    def test_a_constant_series_has_no_autocorrelation_and_keeps_its_size(self):
        self.assertEqual(script.lag1_autocorrelation([3.0] * 10), 0.0)
        self.assertEqual(script.effective_sample([3.0] * 10), 10.0)

    def test_an_alternating_series_is_not_inflated(self):
        series = [1.0, -1.0] * 10
        self.assertLess(script.lag1_autocorrelation(series), 0.0)
        self.assertEqual(script.effective_sample(series), 20.0)

    def test_a_trend_has_a_small_effective_sample(self):
        series = [float(i) for i in range(100)]
        r = script.lag1_autocorrelation(series)
        self.assertAlmostEqual(script.effective_sample(series), 100 * (1 - r) / (1 + r), places=9)
        self.assertLess(script.effective_sample(series), 5.0)

    def test_hand_case(self):
        # mean 2, deviations -1, 0, 1: sum of lag products 0, sum of squares 2, so r = 0
        self.assertEqual(script.lag1_autocorrelation([1.0, 2.0, 3.0]), 0.0)
        # deviations 1, 1, -1, -1 around 0: products 1, -1, 1 = 1; squares 4; r = 0.25
        self.assertAlmostEqual(script.lag1_autocorrelation([1.0, 1.0, -1.0, -1.0]), 0.25)

    def test_fewer_than_two_values_are_refused(self):
        with self.assertRaises(ValueError):
            script.effective_sample([1.0])


class TrainingSummaryTests(unittest.TestCase):
    def test_counts_variances_and_leaf_ratios(self):
        targets = [-10.0, -10.0, -12.0, -8.0, 5.0, 5.0]
        anchors = [-10.0, -10.0, -10.0, -12.0, -8.0, 5.0]
        floor = [True, True, True, True, False, False]
        out = script.training_summary(targets, anchors, floor)
        self.assertEqual(out["pairs"], 6)
        self.assertEqual(out["floor_pairs"], 4)
        self.assertAlmostEqual(out["floor_pairs_per_leaf_5"], 4 / 5)
        self.assertAlmostEqual(out["floor_pairs_per_leaf_20"], 4 / 20)
        mean = sum(targets) / 6
        self.assertAlmostEqual(out["target_variance"], sum((t - mean) ** 2 for t in targets) / 6)
        changes = [0.0, 0.0, -2.0, 4.0, 13.0, 0.0]
        cm = sum(changes) / 6
        self.assertAlmostEqual(out["change_variance"], sum((c - cm) ** 2 for c in changes) / 6)
        self.assertEqual(out["distinct_targets"], 4)
        self.assertEqual(out["floor_target_variance"], 2.0)  # -10, -10, -12, -8: mean -10, squares 0 0 4 4 over 4

    def test_the_inputs_must_line_up(self):
        with self.assertRaises(ValueError):
            script.training_summary([1.0, 2.0], [1.0], [True, True])


if __name__ == "__main__":
    unittest.main()
