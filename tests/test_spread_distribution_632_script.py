"""The scoring script of the spread-level distribution (#632): its readings, statistics and declaration.

Pure functions and the committed declaration; nothing here fits a model (that is `test_spread_distribution_632.py`).

Recorded mutation, 12 October 2026, in a disposable copy: in `scripts/spread_distribution_632.py`, `published_quantiles`, the
condition `if date.fromisoformat(entry["date"]) <= end` replaced by `if True` (the published file runs to 2026-09-03, so the
locked days are read). `PublishedDistributionTests.test_days_after_the_last_scored_day_are_not_read` then failed with
`AssertionError`.
"""

from __future__ import annotations

import importlib.util
import json
import math
import random
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _script():
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("spread_distribution_632_script", ROOT / "scripts" / "spread_distribution_632.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["spread_distribution_632_script"] = module
    spec.loader.exec_module(module)
    return module


SCRIPT = _script()
DECLARATION = json.loads((ROOT / "metadata" / "spread_distribution_632.json").read_text())


class QuantileReadingTests(unittest.TestCase):
    GRID = [0.01, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 0.99]

    def setUp(self):
        if importlib.util.find_spec("numpy") is None:  # pragma: no cover - the ml extra is optional
            self.skipTest("the ml extra is not installed")
        self.quantiles = [-4.0 + 0.8 * k for k in range(len(self.GRID))]

    def test_the_quantile_inverts_the_exceedance_reading(self):
        from repo_model import ml

        for tau in (-2.0, 0.0, 3.0, 5.0):
            exceed = ml.exceedance_from_quantiles(self.quantiles, self.GRID, [tau])[0]
            self.assertAlmostEqual(SCRIPT.quantile_at(self.quantiles, self.GRID, 1.0 - exceed), math.floor(tau) + 0.5, places=4)

    def test_the_quantile_is_the_fitted_one_on_the_grid_and_continues_past_it(self):
        self.assertAlmostEqual(SCRIPT.quantile_at(self.quantiles, self.GRID, 0.5), self.quantiles[6], places=4)
        self.assertLess(SCRIPT.quantile_at(self.quantiles, self.GRID, 0.001), self.quantiles[0])
        self.assertGreater(SCRIPT.quantile_at(self.quantiles, self.GRID, 0.999), self.quantiles[-1])

    def test_a_level_outside_the_open_interval_is_refused(self):
        for level in (0.0, 1.0, -0.1):
            with self.assertRaises(ValueError):
                SCRIPT.quantile_at(self.quantiles, self.GRID, level)

    def test_the_crps_is_twice_the_mean_pinball_loss(self):
        levels = [0.05, 0.25, 0.5, 0.75, 0.95]
        predicted = [-2.0, -1.0, 0.0, 1.5, 4.0]
        observed = 2.0
        losses = SCRIPT.pinballs(levels, predicted, observed)
        self.assertAlmostEqual(SCRIPT.crps_contract(levels, predicted, observed), 2.0 * sum(losses) / 5)


class AurocTests(unittest.TestCase):
    def test_a_perfect_ranking_is_one_and_a_reversed_one_is_zero(self):
        self.assertEqual(SCRIPT.auroc([0.1, 0.2, 0.8, 0.9], [0, 0, 1, 1]), 1.0)
        self.assertEqual(SCRIPT.auroc([0.9, 0.8, 0.2, 0.1], [0, 0, 1, 1]), 0.0)

    def test_ties_count_half(self):
        self.assertEqual(SCRIPT.auroc([0.3, 0.3, 0.3, 0.3], [0, 1, 0, 1]), 0.5)
        self.assertAlmostEqual(SCRIPT.auroc([0.1, 0.5, 0.5, 0.9], [0, 1, 0, 1]), (1 + 0.5 + 1 + 1) / 4)

    def test_one_class_is_undefined(self):
        self.assertIsNone(SCRIPT.auroc([0.1, 0.2], [0, 0]))
        self.assertIsNone(SCRIPT.auroc([0.1, 0.2], [1, 1]))

    def test_length_mismatch_is_refused(self):
        with self.assertRaises(ValueError):
            SCRIPT.auroc([0.1], [0, 1])


class ReliabilityTests(unittest.TestCase):
    def forecasts(self, shift=0.0, scale=1.0, n=6000, seed=7):
        rng = random.Random(seed)
        true = [rng.uniform(-4.0, 1.0) for _ in range(n)]
        outcomes = [1 if rng.random() < 1.0 / (1.0 + math.exp(-z)) else 0 for z in true]
        shown = [1.0 / (1.0 + math.exp(-(scale * z + shift))) for z in true]
        return shown, outcomes

    def test_a_reliable_forecast_has_slope_one_and_intercept_zero(self):
        p, y = self.forecasts()
        slope, intercept = SCRIPT.reliability(p, y)
        self.assertAlmostEqual(slope, 1.0, delta=0.12)
        self.assertAlmostEqual(intercept, 0.0, delta=0.12)

    def test_a_constant_shift_moves_the_intercept_and_leaves_the_slope(self):
        p, y = self.forecasts(shift=1.0)
        slope, intercept = SCRIPT.reliability(p, y)
        self.assertAlmostEqual(slope, 1.0, delta=0.12)
        self.assertLess(intercept, -0.7)

    def test_an_overconfident_forecast_has_slope_below_one(self):
        p, y = self.forecasts(scale=2.0)
        slope, _intercept = SCRIPT.reliability(p, y)
        self.assertLess(slope, 0.7)

    def test_a_constant_forecast_or_a_single_class_has_no_slope(self):
        self.assertIsNone(SCRIPT.reliability([0.0, 0.0, 0.0, 0.0], [0, 1, 0, 1]))
        self.assertIsNone(SCRIPT.reliability([0.1, 0.2, 0.3], [0, 0, 0]))


class PairedTests(unittest.TestCase):
    def test_the_difference_is_benchmark_minus_variant_and_split_by_group(self):
        variant = [1.0, 1.0, 2.0, 2.0]
        bench = [2.0, 2.0, 2.0, 1.0]
        groups = {"regime": ["a", "a", "b", "b"]}
        out = SCRIPT.paired_losses(variant, bench, groups, seed=1)
        self.assertAlmostEqual(out["pooled"]["mean"], (1 + 1 + 0 - 1) / 4)
        self.assertEqual(out["regime"]["a"]["days"], 2)
        self.assertAlmostEqual(out["regime"]["a"]["mean"], 1.0)
        self.assertAlmostEqual(out["regime"]["b"]["mean"], -0.5)

    def test_unequal_series_are_refused(self):
        with self.assertRaises(ValueError):
            SCRIPT.paired_losses([1.0], [1.0, 2.0], {}, seed=1)


class PublishedDistributionTests(unittest.TestCase):
    def test_days_after_the_last_scored_day_are_not_read(self):
        end = date(2025, 12, 31)
        kept, levels = SCRIPT.published_quantiles(1, end)
        self.assertEqual(levels, [0.05, 0.25, 0.5, 0.75, 0.95])
        self.assertTrue(kept)
        self.assertLessEqual(max(date.fromisoformat(d) for d in kept), end)


class DeclarationTests(unittest.TestCase):
    def test_the_variants_are_the_declared_rows_and_at_most_three(self):
        run = SCRIPT.require_declared_variants(DECLARATION)
        self.assertEqual(list(run), DECLARATION["rows"]["new"])
        self.assertLessEqual(len(DECLARATION["variants"]), 3)
        self.assertFalse(DECLARATION["variants"]["(c)"]["run"])

    def test_more_than_three_variants_are_refused(self):
        many = dict(DECLARATION)
        many["variants"] = {f"v{k}": {"structure": "risk_date"} for k in range(4)}
        with self.assertRaises(ValueError):
            SCRIPT.require_declared_variants(many)

    def test_every_new_row_has_a_candidate_file_and_both_references(self):
        for name in DECLARATION["rows"]["new"]:
            self.assertTrue((ROOT / "metadata" / "pressure_judge" / "candidates" / f"{name}.json").is_file())
            self.assertEqual(DECLARATION["rows"]["pairs"][name], [SCRIPT.BEST, SCRIPT.CAP])
        for name in DECLARATION["rows"]["controls"]:
            self.assertTrue((ROOT / "metadata" / "pressure_judge" / "candidates" / f"{name}.json").is_file() or name in ("risk_gbm+settle+h41", SCRIPT.BEST))

    def test_the_declared_model_is_the_modules(self):
        from repo_model import ml

        settings = ml.PRESSURE_SPREAD_DISTRIBUTION_SETTINGS
        model = DECLARATION["model"]
        self.assertEqual(tuple(model["quantile_grid"]), settings["quantile_grid"])
        self.assertEqual(settings["quantile_grid"], ml.PRESSURE_QUANTILE_SETTINGS["quantile_grid"])
        for key in ("learning_rate", "max_iter", "max_leaf_nodes", "min_samples_leaf"):
            self.assertEqual(settings[key], ml.PRESSURE_CLASSIFIER_SETTINGS[key])

    def test_the_scoring_window_ends_before_every_locked_day(self):
        from repo_model import lockbox

        last = date.fromisoformat(DECLARATION["scoring"]["last_day"])
        self.assertEqual(last, date(2025, 12, 31))
        lockbox.require_unlocked([last], where="test")


if __name__ == "__main__":
    unittest.main()
