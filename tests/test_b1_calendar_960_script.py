"""The helpers of `scripts/b1_calendar_960.py` (#960; H5 step 5, H1 step 3, development tier).

Written after the script, which is measurement code. It adds no reader of its own: B1' is tested in `test_b1_calendar_960`
(with the recorded mutation of its as-of guard), the scored days pass `spread_mean_reversion_686.require_scored_days` and
`lockbox.require_unlocked` (their mutations are recorded in `test_spread_mean_reversion_686_script`), and the gbm walks'
locked-day refusal is `spread_distribution_634.refuse_locked`. Pinned here: the declaration agrees with the script
(seed, last day, pairs, the MME), the two reading rules say what the declaration says, and walks made from another panel
are refused.
"""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from repo_model import scoring_protocol as sp

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("b1_calendar_960", ROOT / "scripts" / "b1_calendar_960.py")
script = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(script)


def row(skill, low, high):
    return {"days": 100, "skill": skill, "skill_interval": [low, high]}


class DeclarationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.declaration = json.loads((ROOT / "metadata" / "b1_calendar_960.json").read_text())

    def test_the_declared_pairs_are_the_scripts(self):
        self.assertEqual([tuple(p) for p in self.declaration["pairs"]], list(script.PAIRS))

    def test_the_declared_seed_and_last_day_are_the_scripts(self):
        self.assertIn(f"seed {script.SEED}", self.declaration["scoring"]["interval"])
        self.assertEqual(self.declaration["limits"]["last_day"], script.LAST_DAY.isoformat())

    def test_the_declared_pool_floor_is_the_modules(self):
        from repo_model import spread_mr_variants as var
        self.assertIn("fewer than 30", self.declaration["b1_prime"]["pool"])
        self.assertEqual(var.POOL_MIN, 30)

    def test_the_declared_mme_is_three_percent(self):
        self.assertIn("below 3%", self.declaration["reading_rules"]["mme_reachable"])
        self.assertEqual(script.MME, 0.03)


class ReadingRuleTests(unittest.TestCase):
    def test_a_lower_bound_below_zero_says_the_gbm_is_not_shown_to_carry_anything(self):
        text = script.reading_rules({"gbm_vs_ctx_ordinary": row(0.01, -0.02, 0.04)})[0]
        self.assertIn("not shown to carry anything beyond the transparent model", text)

    def test_a_lower_bound_above_zero_does_not(self):
        text = script.reading_rules({"gbm_vs_ctx_ordinary": row(0.05, 0.01, 0.09)})[0]
        self.assertNotIn("not shown", text)
        self.assertIn("not below 0", text)

    def test_a_pooled_skill_below_three_percent_over_b1_prime_says_the_mme_is_not_reachable(self):
        text = script.reading_rules({"gbm_vs_b1p_pooled": row(0.029, 0.0, 0.05)})[1]
        self.assertIn("not reachable", text)

    def test_a_pooled_skill_of_three_percent_or_more_does_not(self):
        text = script.reading_rules({"gbm_vs_b1p_pooled": row(0.03, 0.0, 0.05)})[1]
        self.assertNotIn("not reachable", text)

    def test_absent_walks_are_said_not_scored(self):
        rules = script.reading_rules({})
        self.assertTrue(all("not scored" in r for r in rules))

    def test_an_undefined_row_is_said_undefined(self):
        rules = script.reading_rules({"gbm_vs_ctx_ordinary": {"undefined": "no variance"}, "gbm_vs_b1p_pooled": {"undefined": "zero"}})
        self.assertTrue(all("undefined" in r for r in rules))


class WalkTests(unittest.TestCase):
    def test_walks_made_from_another_panel_are_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            for h in sp.HORIZONS:
                (Path(directory) / f"gbm_funding_h{h}.json").write_text(json.dumps(
                    {"horizon": h, "variant": "gbm_funding", "levels": list(sp.GRID), "laws": {}, "panel_sha256": "0" * 64}))
            with self.assertRaises(ValueError):
                script.load_gbm(Path(directory), "1" * 64, None)


if __name__ == "__main__":
    unittest.main()
