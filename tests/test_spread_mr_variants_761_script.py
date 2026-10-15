"""The helpers of `scripts/spread_mr_variants_761.py` (#761; H5 step 2, development tier).

Written after the script, which is measurement code. It adds no reader of its own: the scored days pass
`spread_mean_reversion_686.require_scored_days` (its recorded mutation is in `test_spread_mean_reversion_686_script`),
the scarcity states come from the judge's existing reader at the declared last day, and the context guard and the weight
guard are recorded in `test_spread_mr_variants`.
"""

from __future__ import annotations

import importlib.util
import json
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import scoring_protocol as sp
from repo_model import spread_mr_variants as var
from repo_model.metrics import _quantile
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("spread_mr_variants_761", ROOT / "scripts" / "spread_mr_variants_761.py")
script = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(script)


class DeclarationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.declaration = json.loads((ROOT / "metadata" / "spread_distribution_761.json").read_text())

    def test_the_declared_variants_are_the_module_s(self):
        self.assertEqual(tuple(self.declaration["variants"]), var.NAMES)
        self.assertEqual(self.declaration["limits"]["max_variants"], len(self.declaration["variants"]))

    def test_the_declaration_ends_where_the_script_does(self):
        self.assertEqual(self.declaration["limits"]["last_day"], script.LAST_DAY.isoformat())

    def test_the_declared_seed_is_the_scripts(self):
        self.assertIn(f"seed {script.SEED}", self.declaration["scoring"]["interval"])

    def test_the_declared_constants_are_the_module_s(self):
        text = json.dumps(self.declaration)
        self.assertIn("fewer than 30 values", text)
        self.assertEqual(var.POOL_MIN, 30)
        self.assertIn("last 250 decision days", text)
        self.assertEqual(var.TRAIL_DAYS, 250)
        self.assertIn("fewer than 60 such days: w = 0.5", text)
        self.assertEqual((var.MIN_TRAIL, var.DEFAULT_WEIGHT), (60, 0.5))

    def test_a_day_after_the_declared_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.s686.require_scored_days([date(2025, 12, 31), date(2026, 1, 2)], script.LAST_DAY)


class StatisticsTests(unittest.TestCase):

    def days(self, n):
        start = date(2020, 1, 1)
        return [start + timedelta(days=i) for i in range(n)]

    def test_the_interval_is_the_point_less_the_studentized_quantiles(self):
        draws = [float(i) / 10.0 for i in range(-50, 51)]
        got = script.studentized_interval(2.0, 0.5, draws)
        self.assertAlmostEqual(got[0], 2.0 - 0.5 * _quantile(draws, 0.95))
        self.assertAlmostEqual(got[1], 2.0 - 0.5 * _quantile(draws, 0.05))
        self.assertLess(got[0], got[1])

    def test_a_better_candidate_has_positive_skill_and_an_interval_above_zero(self):
        days = self.days(120)
        bench = {d: 2.0 + 0.1 * (i % 5) for i, d in enumerate(days)}
        cand = {d: v - 0.5 - 0.05 * (i % 3) for i, (d, v) in enumerate(bench.items())}
        row = script.run_pairs({"B": bench}, cand, days, draws=400)["B"]
        self.assertGreater(row["skill"], 0.0)
        self.assertGreater(row["skill_interval"][0], 0.0)
        self.assertGreater(row["difference_interval"][0], 0.0)

    def test_the_interval_is_the_studentized_one_not_the_percentile_one(self):
        days = self.days(120)
        bench = {d: 2.0 + 0.1 * (i % 5) + (3.0 if i % 40 == 0 else 0.0) for i, d in enumerate(days)}
        cand = {d: v - 0.2 - 0.3 * (i % 7 == 0) for i, (d, v) in enumerate(bench.items())}
        test = sp.paired_tests([(bench, cand)], seed=1, draws=400)[0]
        row = script.paired_row(test)
        percentile = [_quantile(test.skill_draws, 0.05), _quantile(test.skill_draws, 0.95)]
        self.assertNotEqual(row["skill_interval"], percentile)
        self.assertEqual(row["skill_interval"], script.studentized_interval(test.skill, test.skill_standard_error, test.skill_t_draws))

    def test_a_benchmark_that_scores_zero_is_undefined_not_a_crash(self):
        days = self.days(40)
        row = script.run_pairs({"B": {d: 0.0 for d in days}}, {d: 0.0 for d in days}, days, draws=50)["B"]
        self.assertIn("undefined", row)
        self.assertEqual(script.skill_text(row), "undefined")

    def test_a_row_excludes_zero_only_when_its_whole_interval_is_on_one_side(self):
        self.assertTrue(script.excludes_zero({"skill_interval": [0.01, 0.2]}))
        self.assertTrue(script.excludes_zero({"skill_interval": [-0.2, -0.01]}))
        self.assertFalse(script.excludes_zero({"skill_interval": [-0.01, 0.2]}))
        self.assertFalse(script.excludes_zero({"undefined": "x"}))

    def test_the_five_levels_are_in_the_grid(self):
        self.assertEqual([sp.GRID[i] for i in script.FIVE_AT], list(script.FIVE))


class ModelListTests(unittest.TestCase):

    def test_the_scored_models_are_the_benchmarks_the_references_and_the_variants(self):
        self.assertEqual(script.MODELS[:4], ("B1", "B2", script.B1RC, var.REFERENCE))
        self.assertEqual(script.MODELS[4:], var.NAMES)
        self.assertEqual(script.CANDIDATES, (var.REFERENCE, script.B1RC) + var.NAMES)

    def test_a_group_below_the_minimum_is_not_tested(self):
        self.assertEqual(script.MIN_GROUP_DAYS, 20)


if __name__ == "__main__":
    unittest.main()
