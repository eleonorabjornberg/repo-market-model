"""Skill on the days that are not risk dates (#624), step 1: the declaration, the climatology and the readers.

Recorded mutations, 12 October 2026, in a disposable copy of `scripts/off_risk_day_624.py`:
1. in `climatology_column`, `pc.past_positions(scored, train_ends, start)` replaced by `range(stop)` (a block's rate is read from days whose
   outcome was not observable at its fit, among them the block's own). `test_a_block_reads_only_outcomes_observable_at_its_fit` then errors
   with `repo_model.splits.LookAheadError` (raised by `group_calibration.fit_floor`, which refuses a pair of a day after the fit).
2. in `climatology_column`, the `if off_risk[i]` filter on the past removed (a risk date's outcome enters the rate of the days that are not risk
   dates). `test_the_rate_is_taken_over_days_that_are_not_risk_dates` then fails with `AssertionError: 0.25 != 0.0`.
3. in `climatology_column`, `if off_risk[index]` on the block's days removed (a risk date is given the rate). `test_a_risk_date_has_no_climatology`
   then fails with `AssertionError: 0.5 is not None`.
"""

import importlib.util
import json
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
DECLARED = json.loads((ROOT / "metadata" / "off_risk_day_624_step1.json").read_text())


def _script():
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("off_risk_day_624_script", ROOT / "scripts" / "off_risk_day_624.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["off_risk_day_624_script"] = module
    spec.loader.exec_module(module)
    return module


SCRIPT = _script()


class DeclarationTests(unittest.TestCase):
    def test_the_scoring_ends_before_the_lockbox_and_nothing_is_published(self):
        self.assertLess(DECLARED["scoring"]["last_day"], "2026-01-01")
        self.assertEqual(DECLARED["published"], "nothing")

    def test_the_interval_is_the_judges(self):
        judge = json.loads((ROOT / "metadata" / "pressure_judge.json").read_text())["bootstrap"]
        for key in ("level", "block_length", "replications"):
            self.assertEqual(DECLARED["bootstrap"][key], judge[key])
        self.assertEqual(DECLARED["bootstrap"]["seed"], 624)

    def test_the_rows_are_the_ones_the_directive_names(self):
        self.assertEqual(set(DECLARED["rows"]), set(SCRIPT.ROWS))
        self.assertEqual(SCRIPT.TAU, DECLARED["scoring"]["primary_threshold_bp"])

    def test_the_declared_clip_is_the_scripts(self):
        self.assertIn("1e-4", DECLARED["statistics"]["clip"])
        self.assertEqual(SCRIPT.RELIABILITY_FLOOR, 1e-4)


def days(n, start=date(2018, 1, 1)):
    return [start + timedelta(days=k) for k in range(n)]


class ClimatologyTests(unittest.TestCase):
    def test_a_block_reads_only_outcomes_observable_at_its_fit(self):
        scored = days(8)
        # the second block (days 4 to 7) is fitted at the end of day 1: only days 0 and 1 are observable to it
        train_ends = [scored[0]] * 4 + [scored[1]] * 4
        outcomes = [0, 0, 1, 1, 1, 1, 1, 1]
        column = SCRIPT.climatology_column(outcomes, scored, train_ends, [True] * 8, minimum_pairs=2)
        # the first block has nothing before it; the second sees days 0 and 1 only (the two earlier days 2 and 3 are not observable)
        self.assertEqual(column[:4], [None] * 4)
        self.assertEqual(column[4:], [0.0] * 4)

    def test_the_rate_is_taken_over_days_that_are_not_risk_dates(self):
        scored = days(8)
        train_ends = [scored[0]] * 4 + [scored[3]] * 4
        outcomes = [1, 0, 0, 0, 0, 0, 0, 0]
        off_risk = [False, True, True, True, True, True, True, True]
        column = SCRIPT.climatology_column(outcomes, scored, train_ends, off_risk, minimum_pairs=2)
        self.assertEqual(column[4], 0.0)
        # with the risk date counted the rate would be 0.25
        again = SCRIPT.climatology_column(outcomes, scored, train_ends, [True] * 8, minimum_pairs=2)
        self.assertEqual(again[4], 0.25)

    def test_a_risk_date_has_no_climatology(self):
        scored = days(8)
        train_ends = [scored[0]] * 4 + [scored[3]] * 4
        outcomes = [0, 1, 0, 1, 0, 0, 0, 0]
        off_risk = [True] * 4 + [False] + [True] * 3
        column = SCRIPT.climatology_column(outcomes, scored, train_ends, off_risk, minimum_pairs=2)
        self.assertIsNone(column[4])
        self.assertEqual(column[5], 0.5)

    def test_none_while_too_few_earlier_days_exist(self):
        scored = days(6)
        column = SCRIPT.climatology_column([0, 1, 0, 0, 0, 0], scored, [scored[2]] * 6, [True] * 6, minimum_pairs=60)
        self.assertEqual(column, [None] * 6)

    def test_columns_of_different_lengths_are_refused(self):
        with self.assertRaises(ValueError):
            SCRIPT.climatology_column([0, 1], days(3), days(3), [True] * 3)

    def test_the_fit_refuses_a_pair_after_it(self):
        with self.assertRaises(LookAheadError):
            SCRIPT.gc.fit_floor([(date(2018, 1, 5), 0.0, 1, "")], date(2018, 1, 1), minimum_pairs=1)


class StatisticTests(unittest.TestCase):
    def test_the_brier_skill_is_zero_at_the_reference_and_one_when_perfect(self):
        y = [0, 1, 0, 1]
        ref = [0.5] * 4
        self.assertAlmostEqual(SCRIPT.brier_skill(ref, y, ref), 0.0)
        self.assertAlmostEqual(SCRIPT.brier_skill([0.0, 1.0, 0.0, 1.0], y, ref), 1.0)

    def test_the_brier_skill_is_none_without_days_or_against_a_perfect_reference(self):
        self.assertIsNone(SCRIPT.brier_skill([], [], []))
        self.assertIsNone(SCRIPT.brier_skill([0.5], [1], [1.0]))

    def test_a_calibrated_forecast_has_intercept_zero_and_slope_one(self):
        p = [0.2] * 100 + [0.6] * 100
        y = [1] * 20 + [0] * 80 + [1] * 60 + [0] * 40
        intercept, slope = SCRIPT.reliability(p, y)
        self.assertAlmostEqual(intercept, 0.0, places=6)
        self.assertAlmostEqual(slope, 1.0, places=6)

    def test_a_forecast_that_ranks_nothing_has_slope_zero(self):
        p = [0.2] * 100 + [0.6] * 100
        y = [1] * 40 + [0] * 60 + [1] * 40 + [0] * 60
        intercept, slope = SCRIPT.reliability(p, y)
        self.assertAlmostEqual(slope, 0.0, places=6)

    def test_the_reliability_fit_is_none_when_it_is_undefined(self):
        self.assertIsNone(SCRIPT.reliability([0.3, 0.3], [0, 1]))
        self.assertIsNone(SCRIPT.reliability([0.2, 0.6], [0, 0]))
        self.assertIsNone(SCRIPT.reliability([], []))

    def test_the_cell_counts_the_pressure_days_on_a_zero_forecast(self):
        p = [0.0, 0.0, 0.3, 0.3]
        y = [1, 0, 1, 0]
        cell = SCRIPT.cell_statistics(p, y, [0.5, 0.5, 0.5, 0.5])
        self.assertEqual(cell["days"], 4)
        self.assertEqual(cell["pressure_days"], 2)
        self.assertEqual(cell["positive_days"], 2)
        self.assertEqual(cell["pressure_days_on_zero"], 1)
        self.assertAlmostEqual(cell["auroc"], 0.5)

    def test_the_skill_is_taken_only_where_the_climatology_exists(self):
        cell = SCRIPT.cell_statistics([0.5, 0.5, 0.5], [0, 1, 0], [None, 0.5, 0.5])
        self.assertEqual(cell["skill_days"], 2)
        self.assertAlmostEqual(cell["brier_skill"], 0.0)


class IntervalTests(unittest.TestCase):
    def setUp(self):
        n = 200
        self.y = [1 if (k % 5 == 0 or k % 7 == 3) else 0 for k in range(n)]
        self.p = [0.6 if (k % 5 == 0 or k % 11 == 0) else 0.1 for k in range(n)]
        self.ref = [0.2] * n
        self.cells = {"all": list(range(n)), "first half": list(range(n // 2)), "none": []}

    def run_it(self, **kw):
        base = dict(seed=624, replications=60, block_length=10, level=0.9)
        base.update(kw)
        return SCRIPT.intervals(self.cells, self.p, self.y, self.ref, **base)

    def test_the_interval_of_a_good_ranker_sits_above_chance(self):
        result = self.run_it()
        self.assertGreater(result["all"]["auroc"]["lower"], 0.5)
        self.assertGreater(result["all"]["brier_skill"]["lower"], 0.0)

    def test_the_same_seed_gives_the_same_interval(self):
        self.assertEqual(self.run_it(), self.run_it())
        self.assertNotEqual(self.run_it(), self.run_it(seed=7))

    def test_an_empty_cell_has_no_interval(self):
        self.assertIsNone(self.run_it()["none"]["auroc"])

    def test_a_draw_without_a_class_is_left_out_and_counted(self):
        result = self.run_it(replications=40, block_length=1)
        entry = result["first half"]["auroc"]
        self.assertEqual(entry["draws"] + entry["left_out"], 40)

    def test_the_reliability_is_bootstrapped_for_the_named_cells_only(self):
        result = self.run_it(reliability_cells=("all",))
        self.assertIsNotNone(result["all"]["slope"])
        self.assertIsNone(result["first half"]["slope"])


if __name__ == "__main__":
    unittest.main()
