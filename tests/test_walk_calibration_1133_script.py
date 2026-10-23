"""The helpers of `scripts/walk_calibration_1133.py` (#1133; H5 step 3, development tier).

Written after the script, which is measurement code. It adds no reader of its own: the scored days pass
`spread_mean_reversion_686.require_scored_days` (its recorded mutation is in `test_spread_mean_reversion_686_script`), the
calibration guards are recorded in `test_walk_calibration`. What these tests pin: the exceedance and band-miss sequences on
hand cases under both hit rules (the lower tail is the mirror of the upper), the nominal rates, the declaration's names
against the script's, and that the committed page is what the committed record gives.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

from repo_model import scoring_protocol as sp
from repo_model import walk_calibration as wc

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("walk_calibration_1133", ROOT / "scripts" / "walk_calibration_1133.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["walk_calibration_1133"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)


def flat_law(low, high):
    """A law whose q01..q05 sit at `low` and q95..q99 at `high`, the body between them."""

    law = []
    for level in sp.GRID:
        law.append(low if level <= 0.05 else high if level >= 0.95 else (low + high) / 2.0)
    return law


class LoaderTests(unittest.TestCase):

    def test_a_script_another_module_registered_is_not_replaced(self):
        """A shard that loads the 941 script first must keep its object, or its worker pool cannot pickle."""

        registered = sys.modules.get("fhs_scale_941")
        if registered is None:
            self.skipTest("fhs_scale_941 not loaded")
        self.assertIs(script._load("fhs_scale_941"), registered)
        self.assertIs(sys.modules["fhs_scale_941"], registered)


class SequenceTests(unittest.TestCase):

    outcomes = [-5.0, -2.0, 0.0, 2.0, 5.0, 9.0]
    laws = [flat_law(-2.0, 2.0)] * 6

    def test_the_upper_tail_under_both_rules(self):
        self.assertEqual(script.hit_sequence(self.outcomes, self.laws, "q95", "above"), [0, 0, 0, 0, 1, 1])
        self.assertEqual(script.hit_sequence(self.outcomes, self.laws, "q95", "at_or_above"), [0, 0, 0, 1, 1, 1])

    def test_the_lower_tail_is_the_mirror(self):
        self.assertEqual(script.hit_sequence(self.outcomes, self.laws, "q05", "above"), [1, 0, 0, 0, 0, 0])
        self.assertEqual(script.hit_sequence(self.outcomes, self.laws, "q05", "at_or_above"), [1, 1, 0, 0, 0, 0])

    def test_a_band_is_missed_outside_it(self):
        # closed band [-2, 2]: -5, 5 and 9 are outside; open band (-2, 2): -2 and 2 are outside as well
        self.assertEqual(script.hit_sequence(self.outcomes, self.laws, "band90", "above"), [1, 0, 0, 0, 1, 1])
        self.assertEqual(script.hit_sequence(self.outcomes, self.laws, "band90", "at_or_above"), [1, 1, 0, 1, 1, 1])

    def test_the_nominal_rates(self):
        nominal = script.kinds_and_p()
        self.assertAlmostEqual(nominal["q95"], 0.05)
        self.assertAlmostEqual(nominal["q99"], 0.01)
        self.assertAlmostEqual(nominal["q05"], 0.05)
        self.assertAlmostEqual(nominal["q01"], 0.01)
        self.assertAlmostEqual(nominal["band50"], 0.50)
        self.assertAlmostEqual(nominal["band98"], 0.02)


class DeclarationTests(unittest.TestCase):

    declaration = json.loads((ROOT / "metadata" / "walk_calibration_1133.json").read_text(encoding="utf-8"))

    def test_the_arms_and_the_constants_are_the_declared_ones(self):
        arms = self.declaration["calibration"]["arms"]
        self.assertEqual(set(arms), set(wc.ARMS))
        self.assertEqual(wc.WINDOW_DAYS, 504)
        self.assertEqual(set(self.declaration["variants"]), set(wc.ARMS))
        self.assertEqual((wc.MIN_CELLS, wc.REFIT_EVERY, wc.WIDTH_FLOOR), (250, 21, 1.0))
        self.assertTrue(self.declaration["base"]["name"].startswith(script.BASE))
        self.assertEqual([a["date"] for a in self.declaration["amendments"]], ["2026-10-22"])  # the ruling on #1142
        self.assertEqual(self.declaration["scoring"]["paired"].count("seed 1133"), 1)
        self.assertEqual(script.SEED, 1133)

    def test_every_band_is_on_the_grid(self):
        for lo, hi in script.BANDS.values():
            self.assertIn(lo, sp.GRID)
            self.assertIn(hi, sp.GRID)


class PageTests(unittest.TestCase):

    def test_the_committed_page_is_what_the_committed_record_gives(self):
        record = ROOT / "docs" / "research" / "walk-calibration-1133" / "result.json"
        page = ROOT / "docs" / "research" / "walk-calibration-1133-result.md"
        if not record.exists():
            self.skipTest("the record is not committed yet")
        self.assertEqual(script.render(json.loads(record.read_text(encoding="utf-8"))), page.read_text(encoding="utf-8"))

    def test_the_record_is_labelled_development(self):
        record = ROOT / "docs" / "research" / "walk-calibration-1133" / "result.json"
        if not record.exists():
            self.skipTest("the record is not committed yet")
        data = json.loads(record.read_text(encoding="utf-8"))
        self.assertEqual(data["label"], "development, not a verdict")
        self.assertLessEqual(data["notes"]["last_target"], "2025-12-31")


if __name__ == "__main__":
    unittest.main()
