"""H1 and H5 step 5 (#961): the coverage gate, shown on a simulated world with known dynamics.

The protocol selects by grid CRPS alone. CRPS rewards sharpness, so a narrower, mis-calibrated forecast can outscore a
calibrated one that knows less. The script builds a two-regime AR(1) world, ranks a field of forecasters by the current
rule, and applies a declared gate (Kupiec at q05 and q95, Christoffersen independence at q95, the 98% band) by lead and
regime. These tests pin the pieces on cases whose answers are known: the ideal forecaster's variance, the hit
construction at the tails, a gate decision on hand-made hit sequences (a pooled pass never covers for a failing regime),
and the demonstration the directive asks for. The script changes no decided value and adds no leakage, availability or
staleness guard, so there is no recorded mutation.
"""

import importlib.util
import math
import random
import unittest
from pathlib import Path

from repo_model import scoring_protocol as sp

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


script = load("coverage_gate_961")


class TestWorld(unittest.TestCase):
    def test_regimes_alternate_in_declared_blocks_calm_first(self):
        sigma = script.sigma_schedule(1000)
        self.assertEqual(set(sigma[:250]), {script.SIGMA_CALM})
        self.assertEqual(set(sigma[250:500]), {script.SIGMA_STRESS})
        self.assertEqual(sigma[500], script.SIGMA_CALM)
        self.assertEqual(script.regime_of(sigma[300]), "stress")

    def test_ideal_variance_is_the_sum_of_decayed_innovation_variances(self):
        sigma = [1.0, 2.0, 3.0, 4.0]
        mean, sd = script.FORECASTERS["ideal"](10.0, 0, 3, sigma)
        self.assertAlmostEqual(mean, script.PHI**3 * 10.0)
        expected = script.PHI**4 * 4.0 + script.PHI**2 * 9.0 + 16.0
        self.assertAlmostEqual(sd**2, expected, places=12)

    def test_the_world_is_reproducible_from_its_seed(self):
        a = script.simulate(50, seed=7)
        b = script.simulate(50, seed=7)
        self.assertEqual(a, b)
        self.assertNotEqual(a, script.simulate(50, seed=8))


class TestGateOnKnownHits(unittest.TestCase):
    def cells(self, miss_rate, n=2000, seed=1):
        rng = random.Random(seed)
        return [1 if rng.random() < miss_rate else 0 for _ in range(n)]

    def test_calibrated_hits_pass_a_cell(self):
        result = script.gate_cell(self.cells(0.05), self.cells(0.05, seed=2), self.cells(0.02, seed=3), lead=1)
        self.assertTrue(result["pass"])

    def test_an_excess_of_misses_fails_kupiec(self):
        result = script.gate_cell(self.cells(0.12), self.cells(0.05, seed=2), self.cells(0.02, seed=3), lead=1)
        self.assertFalse(result["tests"]["kupiec_q05"]["pass"])
        self.assertFalse(result["pass"])

    def test_clustered_q95_misses_fail_independence_while_kupiec_passes(self):
        # 5% of days miss, but in runs of five: the hit rate is right and the days are not independent
        hits = ([1] * 5 + [0] * 95) * 20
        result = script.gate_cell(self.cells(0.05), hits, self.cells(0.02, seed=3), lead=1)
        self.assertTrue(result["tests"]["kupiec_q95"]["pass"])
        self.assertFalse(result["tests"]["independence_q95"]["pass"])

    def test_the_98_band_must_lie_within_declared_limits(self):
        wide = script.gate_cell(self.cells(0.05), self.cells(0.05, seed=2), self.cells(0.0, seed=3), lead=1)
        self.assertFalse(wide["tests"]["band_98"]["pass"])  # coverage 1.0 above 0.995
        narrow = script.gate_cell(self.cells(0.05), self.cells(0.05, seed=2), self.cells(0.06, seed=3), lead=1)
        self.assertFalse(narrow["tests"]["band_98"]["pass"])  # coverage 0.94 below 0.95

    def test_thinning_at_lead_h_keeps_every_hth_day(self):
        hits = list(range(20))
        self.assertEqual(script.thin(hits, 1), hits)
        self.assertEqual(script.thin(hits, 5), [0, 5, 10, 15])

    def test_a_pooled_pass_does_not_cover_a_failing_regime(self):
        passing = {"pass": True}
        failing = {"pass": False}
        self.assertFalse(script.overall_pass({("calm", 1): passing, ("stress", 1): failing}))
        self.assertTrue(script.overall_pass({("calm", 1): passing, ("stress", 1): passing}))

    def test_hit_sequences_use_the_required_rule_argument(self):
        with self.assertRaises(TypeError):
            script.hit_sequence([1.0], [0.5])


class TestDemonstration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.demo = script.demonstrate(days=script.DEMO_DAYS, seed=script.SEED, draws=300)

    def test_the_under_dispersed_forecast_outscores_the_calibrated_ones_on_crps(self):
        crps = self.demo["mean_crps"]
        for calibrated in ("persistence", "climatology"):
            self.assertLess(crps["under_0.5"], crps[calibrated])

    def test_the_current_rule_picks_the_under_dispersed_forecast_without_the_ideal(self):
        field = {k: v for k, v in self.demo["mean_crps"].items() if k != "ideal"}
        self.assertEqual(min(field, key=field.get), "under_0.75")
        self.assertLess(self.demo["mean_crps"]["ideal"], self.demo["mean_crps"]["under_0.75"])

    def test_the_gate_rejects_the_under_dispersed_forecast_and_fails_the_ideal_in_fewer_cells(self):
        gate = self.demo["gate"]
        for name in ("under_0.5", "under_0.75"):
            self.assertFalse(gate[name]["pass"])
            self.assertGreater(len(gate[name]["failing_cells"]), len(gate["ideal"]["failing_cells"]))

    def test_thinning_kupiec_changes_only_the_kupiec_tests(self):
        hits = [1 if (i * 7) % 20 == 0 else 0 for i in range(2000)]
        plain = script.gate_cell(hits, hits, [0] * 2000, lead=4)
        thinned = script.gate_cell(hits, hits, [0] * 2000, lead=4, thin_kupiec=True)
        self.assertEqual(plain["tests"]["independence_q95"], thinned["tests"]["independence_q95"])
        self.assertEqual(plain["tests"]["band_98"], thinned["tests"]["band_98"])
        self.assertNotEqual(plain["tests"]["kupiec_q95"]["p"], thinned["tests"]["kupiec_q95"]["p"])

    def test_pooled_forecasters_fail_by_regime(self):
        for name in ("pooled", "persistence", "climatology"):
            self.assertFalse(self.demo["gate"][name]["pass"], name)


class TestSize(unittest.TestCase):
    def test_a_calibrated_forecast_is_failed_more_often_than_1_percent_by_the_declared_gate(self):
        size = script.size_study(paths=12, days=1000)
        self.assertGreater(size["declared"]["fail_share"], 0.05)


if __name__ == "__main__":
    unittest.main()
