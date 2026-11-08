"""Finding #1514 (directive #1517): each power-study set-up's size and power are stated together.

The note `docs/research/size-power-pairing-1517.md` quotes size and power for the two set-ups of #1392's full-mode study. These tests recompute
every quoted figure from `docs/research/confirmation-size-power-1392/result-full.json`, and check that the corrected page of #1506 no longer sets
the both-baselines size beside the binding-baseline power. Not a leakage guard; no mutation is recorded.
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTE = ROOT / "docs" / "research" / "size-power-pairing-1517.md"
PAGE = ROOT / "docs" / "research" / "recalibration-1482-result.md"
CELLS = json.loads((ROOT / "docs" / "research" / "confirmation-size-power-1392" / "result-full.json").read_text(encoding="utf-8"))["cells"]


def rate(group, scheme, effects, n):
    hit = [c for c in CELLS if c["group"] == group and c["scheme"] == scheme and c["n"] == n and c["ell"] == 50
           and c["flag_effect"] is None and c["effects"] == effects]
    assert len(hit) == 1, (group, scheme, effects, n)
    return round(100 * hit[0]["main"]["pass"] / hit[0]["count"], 1)


class TheNoteStatesSizeAndPowerTogether(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = NOTE.read_text(encoding="utf-8")

    def test_one_baseline_binding_set_up(self):
        self.assertEqual(rate("binding_observed", "block", [0.03, None], 500), 6.2)
        self.assertEqual(rate("binding_observed", "regime", [0.03, None], 500), 6.4)
        self.assertEqual(rate("binding_observed", "regime", [0.03, None], 250), 10.8)
        self.assertEqual(rate("binding_observed", "block", [0.1, None], 500), 34.6)
        self.assertEqual(rate("binding_observed", "regime", [0.1, None], 500), 31.6)
        for needle in ("6.2", "6.4", "10.8", "34.6", "31.6"):
            self.assertIn(needle, self.text)

    def test_both_baselines_set_up(self):
        self.assertEqual(rate("main", "block", [0.03, 0.03], 500), 0.6)
        self.assertEqual(rate("main", "regime", [0.03, 0.03], 500), 0.8)
        self.assertEqual(rate("main", "regime", [0.03, 0.03], 250), 1.4)
        self.assertEqual(rate("main", "block", [0.1, 0.1], 500), 6.6)
        self.assertEqual(rate("main", "regime", [0.1, 0.1], 500), 3.4)
        for needle in ("1.4", "6.6", "3.4"):
            self.assertIn(needle, self.text)

    def test_the_gate_reads_as_met_by_the_keep_ruling_and_nothing_is_changed(self):
        self.assertIn("500 origins", self.text)
        self.assertIn("24 months", self.text)
        self.assertIn("keep", self.text)
        self.assertIn("No threshold", self.text)


class TheCorrectedPageDoesNotMisPair(unittest.TestCase):
    def test_section_9_gives_each_set_up_its_own_size_and_power(self):
        page = PAGE.read_text(encoding="utf-8")
        section = page.split("## 9.", 1)[1]
        self.assertNotIn("At the 3% boundary the pass rate is at most 1.4%. At 10% skill", section)
        self.assertIn("6.2%", section)
        self.assertIn("size-power-pairing-1517.md", section)
        self.assertTrue(re.search(r"both baselines.*1\.4%", section, re.S))


if __name__ == "__main__":
    unittest.main()
