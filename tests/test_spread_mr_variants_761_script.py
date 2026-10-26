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

    def test_a_benchmark_that_scores_zero_keeps_its_mean_d_bound_when_asked(self):
        """#1215: with `mean_d_fallback`, a pair whose skill is undefined keeps its mean-d bound, alone on the same seed.

        Mutation (recorded): making the retry pass `with_skill=True` turned the row back to `undefined`: the first
        assertNotIn raised AssertionError ('undefined' unexpectedly found in the row); making the retry use another seed
        broke the equality with a pair run alone (AssertionError on the interval).
        """

        days = self.days(120)
        zero = {d: 0.0 for d in days}
        cand = {d: 0.3 + 0.1 * (i % 5) for i, d in enumerate(days)}
        good = {d: 2.0 + 0.1 * (i % 7) for i, d in enumerate(days)}
        plain = script.run_pairs({"Z": zero, "G": good}, cand, days, draws=200)
        self.assertIn("undefined", plain["Z"])
        self.assertIn("undefined", plain["G"])
        rows = script.run_pairs({"Z": zero, "G": good}, cand, days, draws=200, mean_d_fallback=True)
        self.assertNotIn("undefined", rows["Z"])
        self.assertIsNone(rows["Z"]["skill_interval"])
        self.assertIn("skill is undefined", rows["Z"]["skill_undefined"])
        self.assertEqual(rows["Z"]["difference_interval"], script.studentized_interval(
            *(lambda t: (t.mean_difference, t.standard_error, t.t_draws))(
                sp.paired_test(zero, cand, seed=script.SEED, draws=200, with_skill=False))))
        self.assertEqual(script.skill_text(rows["Z"]), "skill undefined")
        self.assertFalse(script.excludes_zero(rows["Z"]))
        # The other pair of the call is defined alone, so it gains its skill row; it is the row run alone.
        self.assertEqual(rows["G"], script.paired_row(sp.paired_test(good, cand, seed=script.SEED, draws=200)))

    def test_a_pair_with_no_mean_d_standard_error_stays_undefined(self):
        days = self.days(40)
        same = {d: 1.0 for d in days}
        row = script.run_pairs({"B": same}, same, days, draws=50, mean_d_fallback=True)["B"]
        self.assertIn("undefined", row)

    def _sparse_pair(self, n=60, spikes=(20,)):
        """A pair whose daily difference is zero except on a few days, so that some resamples miss every one of them."""

        days = self.days(n)
        bench = {d: 1.0 + 0.1 * (i % 3) for i, d in enumerate(days)}
        cand = {d: bench[d] - (0.5 + 0.1 * k if i in spikes else 0.0) for k, (i, d) in enumerate(zip(range(n), days))}
        return days, bench, cand

    def _constant_resamples(self, days, bench, cand, seed, draws):
        """The resamples with no long-run variance, counted independently of the script: the same stream, the same draws."""

        import random
        from repo_model.metrics import stationary_bootstrap_indices

        diff = [bench[d] - cand[d] for d in days]
        rng = random.Random(seed)
        n = len(days)
        return sum(1 for _ in range(draws)
                   if sp._long_run_variance([diff[i] for i in stationary_bootstrap_indices(n, sp.BLOCK_LENGTH, rng)], sp.HAC_LAG) <= 0.0)

    def test_a_pair_with_constant_resamples_drops_them_and_keeps_its_bound(self):
        """#1239 (her ruling, 26 Oct 2026): a resample of the daily difference with no long-run variance is dropped from the
        mean-d studentization, counted, and the bound is taken from the rest, on the same seed and the same draws.

        Mutation (recorded): replacing the `resampled_variance > 0.0` test in `mean_d_dropping_row` with `True` (keeping a
        constant resample) raised ZeroDivisionError in this test and in the every-resample-constant test.
        """

        days, bench, cand = self._sparse_pair()
        draws = 400
        want = self._constant_resamples(days, bench, cand, script.SEED, draws)
        self.assertTrue(0 < want < draws, want)
        with self.assertRaises(sp.ProtocolError):
            sp.paired_test(bench, cand, seed=script.SEED, draws=draws, with_skill=False)
        plain = script.run_pairs({"S": bench}, cand, days, draws=draws, mean_d_fallback=False)["S"]
        self.assertIn("undefined", plain)
        row = script.run_pairs({"S": bench}, cand, days, draws=draws, mean_d_fallback=True)["S"]
        self.assertNotIn("undefined", row)
        self.assertEqual(row["dropped_resamples"], want)
        self.assertEqual(row["draws"], draws)
        self.assertIsNone(row["skill_interval"])
        # The bound, rebuilt from the kept draws alone with the scorer's own pieces.
        import random
        from repo_model.metrics import stationary_bootstrap_indices

        diff = [bench[d] - cand[d] for d in days]
        n, mean = len(days), sum(diff) / len(days)
        se = (sp._long_run_variance(diff, sp.HAC_LAG) / n) ** 0.5
        rng = random.Random(script.SEED)
        t = []
        for _ in range(draws):
            r = [diff[i] for i in stationary_bootstrap_indices(n, sp.BLOCK_LENGTH, rng)]
            v = sp._long_run_variance(r, sp.HAC_LAG)
            if v > 0.0:
                t.append((sum(r) / n - mean) / (v / n) ** 0.5)
        self.assertEqual(len(t), draws - want)
        self.assertEqual(row["difference_interval"], script.studentized_interval(mean, se, sorted(t)))
        self.assertNotEqual(row["difference_interval"][0], row["difference_interval"][1])
        self.assertIn(f"{want} of {draws} resamples dropped", script.diff_text(row))

    def test_a_row_with_no_constant_resample_is_unchanged_by_the_dropping_fallback(self):
        """#1239: the dropping runs only after the earlier fallbacks fail, so a row they computed is byte for byte what it was.

        Mutation (recorded): making `run_pairs` try the dropping helper before the plain mean-d retry gave this row the keys
        `dropped_resamples` and `draws`: the assertNotIn raised AssertionError (and the #1215 test failed on its reason).
        """

        days = self.days(120)
        zero = {d: 0.0 for d in days}
        cand = {d: 0.3 + 0.1 * (i % 5) for i, d in enumerate(days)}
        row = script.run_pairs({"Z": zero}, cand, days, draws=200, mean_d_fallback=True)["Z"]
        self.assertNotIn("dropped_resamples", row)
        self.assertNotIn("draws", row)
        self.assertEqual(json.dumps(row, sort_keys=True), json.dumps(script.mean_d_row(
            sp.paired_test(zero, cand, seed=script.SEED, draws=200, with_skill=False), row["skill_undefined"]), sort_keys=True))
        self.assertNotIn("resamples dropped", script.diff_text(row))

    def test_a_series_with_no_variance_stays_without_a_reading(self):
        days = self.days(60)
        same = {d: 1.0 for d in days}
        row = script.run_pairs({"B": same}, same, days, draws=50, mean_d_fallback=True)["B"]
        self.assertIn("undefined", row)
        self.assertIn("daily difference has no long-run variance", row["undefined"])
        self.assertNotIn("dropped_resamples", row)

    def test_a_pair_whose_every_resample_is_constant_stays_without_a_reading_and_says_why(self):
        """#1239: with one draw, a seed whose single resample misses every spike leaves nothing to take the bound from."""

        days, bench, cand = self._sparse_pair()
        seed = next(s for s in range(500) if self._constant_resamples(days, bench, cand, s, 1) == 1)
        row = script.run_pairs({"S": bench}, cand, days, seed=seed, draws=1, mean_d_fallback=True)["S"]
        self.assertIn("undefined", row)
        self.assertIn("every one of the 1 resamples", row["undefined"])
        self.assertEqual(script.diff_text(row), "undefined")

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
