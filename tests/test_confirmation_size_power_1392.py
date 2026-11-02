"""The size-and-power study of the proposed H5 confirmation test (#1392): `scripts/confirmation_size_power_1392.py`.

Pinned on hand cases: the skill rescaling gives the stated skill exactly, W = 0.97 S_b - S_C has mean zero at 3% skill, the geometric blocks have the
declared mean, the regime generator draws only inside a regime's own origins, the decision rule passes a clear gain, fails a clear loss and is
inconclusive on noise around the threshold, the study is reproducible from its seed, and a loss file with an origin after the development end is refused.

Written before the script. Recorded mutation (the guard this script adds): `load_losses`, the call `require_exploratory_window(...)` replaced by `pass`:
`GuardTests.test_an_origin_after_the_development_end_is_refused` fails with `AssertionError` (`ValueError not raised`); restored, it passes.
"""

from __future__ import annotations

import importlib.util
import json
import random
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("confirmation_size_power_1392_script", REPO / "scripts" / "confirmation_size_power_1392.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)


def _noise(n, seed, scale=1.0, mean=0.0):
    rng = random.Random(seed)
    return [mean + scale * rng.gauss(0.0, 1.0) for _ in range(n)]


class ArithmeticTests(unittest.TestCase):
    def test_rescaling_gives_the_stated_skill(self):
        cand, base = [1.0, 2.0, 3.0], [2.0, 4.0, 6.0]
        factor = script.baseline_factor(sum(cand) / 3, sum(base) / 3, 0.10)
        scaled = [factor * x for x in base]
        self.assertAlmostEqual(1.0 - (sum(cand) / 3) / (sum(scaled) / 3), 0.10, places=12)

    def test_w_has_mean_zero_at_the_threshold_skill(self):
        cand, base = [1.0, 2.0, 3.0], [2.0, 4.0, 6.0]
        factor = script.baseline_factor(2.0, 4.0, script.THRESHOLD)
        w = script.w_vector(cand, [factor * x for x in base])
        self.assertAlmostEqual(sum(w) / 3, 0.0, places=12)

    def test_geometric_blocks_have_the_declared_mean(self):
        rng = random.Random(1)
        lengths = [length for _ in range(4000) for _s, length in script.segments(10_000, 50, rng)[:-1]]
        self.assertAlmostEqual(sum(lengths) / len(lengths), 50, delta=3)

    def test_a_resample_has_n_values(self):
        rng = random.Random(2)
        self.assertEqual(sum(length for _s, length in script.segments(317, 20, rng)), 317)

    def test_hac_se_of_a_constant_is_zero_and_of_noise_is_near_the_iid_value(self):
        self.assertEqual(script.hac_se([1.0] * 100, 10), 0.0)
        x = _noise(4000, 3)
        self.assertAlmostEqual(script.hac_se(x, 10), 1 / 4000 ** 0.5, delta=0.004)

    def test_regime_generator_stays_inside_the_regime_it_is_in(self):
        regimes = ["a"] * 30 + ["b"] * 30
        chain = script.regime_chain(regimes)
        rng = random.Random(4)
        picked = script.regime_sample(regimes, chain, 400, 10, rng)
        self.assertEqual(len(picked), 400)
        self.assertTrue(all(0 <= i < 60 for i in picked))
        # within a block the next origin is the successor, so a run of "a" origins is consecutive
        runs = sum(1 for x, y in zip(picked, picked[1:]) if y == x + 1)
        self.assertGreater(runs, 200)

    def test_the_chain_rows_sum_to_one_and_the_stationary_law_is_a_law(self):
        chain = script.regime_chain(["a", "a", "b", "a", "b", "b", "b", "a"])
        for row in chain["matrix"].values():
            self.assertAlmostEqual(sum(row.values()), 1.0)
        self.assertAlmostEqual(sum(chain["stationary"].values()), 1.0)


class DecisionTests(unittest.TestCase):
    def test_a_clear_gain_passes_and_a_clear_loss_fails(self):
        gain = [_noise(300, 5, 1.0, 2.0), _noise(300, 6, 1.0, 2.0)]
        loss = [_noise(300, 7, 1.0, -2.0), _noise(300, 8, 1.0, 2.0)]
        self.assertEqual(script.decide_main(gain, 50, 199, random.Random(1), lag=20), "pass")
        self.assertEqual(script.decide_main(loss, 50, 199, random.Random(1), lag=20), "fail")

    def test_noise_around_zero_is_inconclusive(self):
        w = [_noise(300, 20, 1.0, 0.0), _noise(300, 21, 1.0, 0.0)]
        self.assertEqual(script.decide_main(w, 50, 199, random.Random(1), lag=20), "inconclusive")

    def test_one_baseline_below_blocks_the_pass(self):
        w = [_noise(300, 11, 1.0, 2.0), _noise(300, 12, 1.0, 0.0)]
        self.assertNotEqual(script.decide_main(w, 50, 199, random.Random(1), lag=20), "pass")

    def test_the_gated_test_rejects_a_clear_difference_only(self):
        self.assertTrue(script.decide_gated(_noise(300, 13, 1.0, 1.0), 50, 199, random.Random(1), lag=20))
        self.assertFalse(script.decide_gated(_noise(300, 14, 1.0, 0.0), 50, 199, random.Random(1), lag=20))

    def test_a_cell_is_reproducible_from_its_seed(self):
        pool = {"cand": _noise(120, 15, 0.2, 1.0), "flag": _noise(120, 16, 0.2, 1.05), "bases": [_noise(120, 17, 0.2, 1.2), _noise(120, 18, 0.2, 1.3)],
                "regime": ["a"] * 60 + ["b"] * 60}
        spec_ = dict(scheme="block", n=100, ell=20, effects=[0.10, 0.10], flag_effect=0.02, reps=49, lag=10, gen_block=10)
        one = script.run_chunk(pool, spec_, 3, "k", 5)
        two = script.run_chunk(pool, spec_, 3, "k", 5)
        self.assertEqual(one, two)
        self.assertEqual(sum(one["main"].values()), 3)


class PoolTests(unittest.TestCase):
    def test_an_unlabelled_origin_takes_the_label_before_it(self):
        from datetime import date
        rows = [(date(2020, 1, d), label, {}) for d, label in ((1, ""), (2, "a"), (3, ""), (6, "b"))]
        self.assertEqual([r[1] for r in script._fill_regimes(rows)], ["a", "a", "a", "b"])

    def test_the_observed_cell_leaves_the_baselines_unscaled(self):
        pool = {"cand": _noise(80, 1, 0.2, 1.0), "flag": _noise(80, 2, 0.2, 1.0), "bases": [_noise(80, 3, 0.2, 1.5), _noise(80, 4, 0.2, 1.5)], "regime": ["a"] * 80}
        spec_ = dict(scheme="block", n=60, ell=20, effects=[None, None], flag_effect=None, reps=29, lag=10, gen_block=10)
        self.assertEqual(sum(script.run_chunk(pool, spec_, 2, "k", 1)["main"].values()), 2)


class DeclarationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.declaration = json.loads((REPO / "metadata" / "confirmation_size_power_1392.json").read_text(encoding="utf-8"))

    def test_the_declared_settings_are_the_scripts(self):
        self.assertEqual(self.declaration["grid"]["hac_lag"], script.HAC_LAG)
        self.assertEqual(self.declaration["seed"], script.SEED)
        self.assertEqual(script.THRESHOLD, 0.03)
        self.assertEqual([a["date"] for a in self.declaration["amendments"]], ["2026-11-02"])

    def test_every_mode_names_only_declared_groups_and_the_full_mode_adds_the_sensitivities(self):
        groups = {c["group"] for c in script.cells_of(self.declaration)}
        for mode in self.declaration["modes"].values():
            self.assertTrue(set(mode["groups"]) <= groups)
        self.assertEqual(set(self.declaration["modes"]["full"]["groups"]), groups)
        self.assertNotIn("sensitivity", self.declaration["modes"]["reduced"]["groups"])

    def test_cell_keys_are_unique_and_the_lengths_are_the_declared_ones(self):
        cells = script.cells_of(self.declaration)
        self.assertEqual(len({c["key"] for c in cells}), len(cells))
        self.assertEqual({c["n"] for c in cells if not c["group"].startswith("extension")}, {250, 500, 750})


class PageTests(unittest.TestCase):
    def _result(self, groups):
        declaration = json.loads((REPO / "metadata" / "confirmation_size_power_1392.json").read_text(encoding="utf-8"))
        cells = []
        for cell in script.cells_of(declaration):
            if cell["group"] not in groups:
                continue
            count = 100
            one = dict(cell, count=count, main={"pass": 80 if cell["effects"] == [0.1, 0.1] else 5, "fail": 1, "inconclusive": count - 81})
            if cell["flag_effect"] is not None:
                one["gated"] = {"reject": 7}
                one["joint"] = {"pass_and_reject": 6}
            cells.append(one)
        return {"declaration": "metadata/confirmation_size_power_1392.json", "mode": "reduced", "M": 100, "reps": 99, "seed": 1392, "pool_origins": 10,
                "first_origin": "2018-07-19", "last_origin": "2026-08-27", "pool_means": {"candidate": 1.6}, "cells": cells}

    def test_the_page_reads_every_rate_from_the_record(self):
        text = script.render(self._result(("main", "observed", "binding", "gated", "extension")))
        self.assertIn("80.0 (4.0)", text)
        self.assertIn("5.0 (2.2)", text)
        self.assertIn("Does 500 origins reach 80% power at 10% skill?", text)
        self.assertIn("the shortest tested length at or above 80% is 250.", text)
        self.assertIn("Question 1", text)

    def test_the_sensitivity_table_appears_only_with_its_cells(self):
        self.assertNotIn("Sensitivity to the test block (pass rate", script.render(self._result(("main", "observed", "binding", "gated", "extension"))))
        self.assertIn("Sensitivity to the test block (pass rate", script.render(self._result(("main", "observed", "binding", "gated", "extension", "sensitivity"))))


class GuardTests(unittest.TestCase):
    def test_an_origin_after_the_development_end_is_refused(self):
        bad = {"windows": {"development": {"origins": ["2026-09-04"], "regime": ["x"], "scores": {"candidate": [1.0], "flag": [1.0], "B1p*": [1.0], "B2": [1.0], "B1": [1.0]}}}}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "losses.json"
            path.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaises(ValueError):
                script.load_losses(path)


if __name__ == "__main__":
    unittest.main()
