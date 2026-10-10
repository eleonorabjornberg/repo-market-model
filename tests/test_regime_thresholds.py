"""Regime-specific warning thresholds (#461): the declaration and its candidate files.

The cut-off function is tested in `test_pressure_judge.ScarceCutoffTests`, with its recorded mutation. Here:
the declaration (`metadata/regime_thresholds.json`) names the six best rows of Table 1 of the re-judge, the
state threshold is the one the directive gives, and every row has a candidate file of its own for the variant.
"""

import importlib.util
import json
import unittest
from pathlib import Path

from repo_model import pressure_judge as pj

ROOT = Path(__file__).resolve().parents[1]
DECLARED = json.loads((ROOT / "metadata" / "regime_thresholds.json").read_text())
CANDIDATES = ROOT / "metadata" / "pressure_judge" / "candidates"


def _script():
    spec = importlib.util.spec_from_file_location("regime_thresholds_script", ROOT / "scripts" / "regime_thresholds.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DeclarationTests(unittest.TestCase):
    def test_the_rows_are_the_six_best_of_table_one(self):
        self.assertEqual(DECLARED["rows"]["chosen"], _script().best_rows(6))

    def test_the_six_rows_are_the_five_of_the_false_alarm_study_and_one_more(self):
        five = json.loads((ROOT / "metadata" / "onset_diagnostics.json").read_text())["false_alarms"]["rows"]["chosen"]
        self.assertEqual(sorted(DECLARED["rows"]["chosen"][:5]), sorted(five))
        self.assertEqual(DECLARED["rows"]["chosen"][5], "scarcity_logistic")

    def test_the_state_threshold_is_two_and_the_window_is_the_judges(self):
        self.assertEqual(DECLARED["scarce_cutoff"]["scarcity_state_at_least"], 2)
        judge = json.loads((ROOT / "metadata" / "pressure_judge.json").read_text())
        self.assertEqual(DECLARED["scoring"]["last_day"], judge["scoring"]["last_day"])
        self.assertEqual(DECLARED["scoring"]["last_day"], "2025-12-31")

    def test_every_row_and_its_variant_is_a_declared_candidate(self):
        declaration = pj.load_declaration()
        for name in DECLARED["rows"]["chosen"]:
            self.assertIn(name, declaration.candidates)
            variant = name + DECLARED["rows"]["variant_suffix"]
            self.assertIn(variant, declaration.candidates)
            self.assertEqual(declaration.candidates[variant]["derived_from"], name)
            self.assertTrue((CANDIDATES / f"{variant}.json").is_file())

    def test_the_variants_are_not_named_for_the_confirmation_look(self):
        declaration = pj.load_declaration()
        for name in DECLARED["rows"]["chosen"]:
            self.assertNotIn(name + DECLARED["rows"]["variant_suffix"], declaration.confirmation_candidates)


if __name__ == "__main__":
    unittest.main()


class RuleSwitchTests(unittest.TestCase):
    def test_score_takes_the_weighted_miss_switch_and_refuses_another_value(self):
        script = _script()
        base = ["score", "--panel", "p.csv", "--bench", "b{h}", "--row", "x=y{h}", "--output", "o.json"]
        with self.assertRaises(SystemExit) as raised:
            script.main(base + ["--rule", "sometimes"])
        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
