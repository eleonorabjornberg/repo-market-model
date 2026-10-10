"""The all-inputs declaration (#479) agrees with the screen, the judge and its script."""

import importlib.util
import json
import sys
import unittest
from pathlib import Path

from repo_model import pressure_judge as pj

ROOT = Path(__file__).resolve().parents[1]
DECLARED = json.loads((ROOT / "metadata" / "all_inputs.json").read_text())
SCREEN = json.loads((ROOT / "docs" / "pivot" / "evidence" / "source-screen" / "screen.json").read_text())
JUDGE_CANDIDATES = dict(pj.load_declaration().candidates)


def _script():
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("all_inputs_script", ROOT / "scripts" / "all_inputs.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AllInputsDeclarationTests(unittest.TestCase):
    def test_the_declaration_is_what_the_screen_evidence_gives(self):
        self.assertEqual(_script().declaration_document(SCREEN), DECLARED)

    def test_every_series_the_screen_reads_is_an_input_with_its_availability(self):
        series = set(SCREEN["series"])
        inputs = set(DECLARED["inputs"]["base"]) | set(DECLARED["inputs"]["optional"])
        self.assertEqual(inputs, series)
        self.assertEqual(set(DECLARED["availability"]), series)
        self.assertEqual(len(inputs), len(DECLARED["inputs"]["base"]) + len(DECLARED["inputs"]["optional"]))

    def test_no_series_is_left_out_for_its_score(self):
        # the unreadable columns of the screen are the only ones absent, and they are refused by the as-of rule
        self.assertFalse(set(SCREEN["unreadable"]) & set(DECLARED["availability"]))

    def test_the_judge_lists_the_features_the_script_reads_at_horizon_one(self):
        script = _script()
        for name in DECLARED["candidates"]:
            entry = JUDGE_CANDIDATES[name + DECLARED["judged_form"]]
            self.assertEqual(entry["role"], "candidate")
            self.assertEqual(entry["features"], list(script.features_at_horizon(DECLARED, 1)))

    def test_the_series_public_at_a_lead_of_one_leave_at_horizon_two_or_more(self):
        script = _script()
        gone = set(DECLARED["public_at_lead_one_only"])
        self.assertTrue(gone)
        for name in gone:
            self.assertIn(name, script.features_at_horizon(DECLARED, 1))
            for h in range(2, 6):
                self.assertNotIn(name, script.features_at_horizon(DECLARED, h))
        for h in range(2, 6):
            self.assertEqual(len(script.features_at_horizon(DECLARED, h)), len(script.features_at_horizon(DECLARED, 1)) - len(gone))

    def test_the_optional_columns_are_inputs_and_the_base_is_the_designs(self):
        script = _script()
        for h in range(1, 6):
            read = script.features_at_horizon(DECLARED, h)
            self.assertTrue(set(script.optional_at_horizon(DECLARED, h)) <= set(read))
            self.assertFalse(set(script.optional_at_horizon(DECLARED, h)) & set(DECLARED["inputs"]["base"]))

    def test_the_scoring_window_ends_before_the_lockbox(self):
        self.assertLess(DECLARED["scoring"]["last_day"], "2026-01-01")


if __name__ == "__main__":
    unittest.main()
