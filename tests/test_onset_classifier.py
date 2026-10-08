"""The onset classifier's declaration (#409) agrees with the judge's and with its script."""

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECLARED = json.loads((ROOT / "metadata" / "onset_classifier.json").read_text())
JUDGE = json.loads((ROOT / "metadata" / "pressure_judge.json").read_text())


def _script():
    import sys

    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("onset_classifier_script", ROOT / "scripts" / "onset_classifier.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class OnsetClassifierDeclarationTests(unittest.TestCase):
    def test_every_candidate_is_declared_to_the_judge_in_its_judged_form(self):
        for name in DECLARED["candidates"]:
            entry = JUDGE["candidates"][name + DECLARED["judged_form"]]
            self.assertEqual(entry["role"], "candidate")
            self.assertEqual(entry["track"], "O (#409)")

    def test_the_judge_lists_the_features_the_script_reads_at_horizon_one(self):
        script = _script()
        for name, spec in DECLARED["candidates"].items():
            read = script.features_at_horizon(DECLARED, spec, 1)
            self.assertEqual(list(read), JUDGE["candidates"][name + DECLARED["judged_form"]]["features"])

    def test_the_settlement_column_leaves_at_horizon_two_or_more(self):
        script = _script()
        for spec in DECLARED["candidates"].values():
            self.assertIn("treasury_settlement", script.features_at_horizon(DECLARED, spec, 1))
            for h in range(2, 6):
                self.assertNotIn("treasury_settlement", script.features_at_horizon(DECLARED, spec, h))

    def test_optional_columns_are_declared_inputs(self):
        script = _script()
        for spec in DECLARED["candidates"].values():
            read = script.features_at_horizon(DECLARED, spec, 1)
            self.assertTrue(set(spec["optional"]) <= set(read))

    def test_the_scoring_window_ends_before_the_lockbox(self):
        self.assertEqual(DECLARED["scoring"]["last_day"], JUDGE["scoring"]["last_day"])
        self.assertEqual(DECLARED["horizons"], JUDGE["horizons"])
        self.assertEqual(DECLARED["thresholds_bp"], JUDGE["thresholds_bp"])


if __name__ == "__main__":
    unittest.main()
