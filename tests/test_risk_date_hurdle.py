"""The hurdle variants (#539) agree with their declaration, and the script's log-loss pairing is what it says.

The causal guard is in `test_ml.RiskDateHurdleTests` (the calibrator fits on earlier pairs only, a risk date keeps the
parent's forecast, a missing input drops out of the design); this file checks the declaration and the pairing.
"""

import importlib.util
import json
import math
import sys
import unittest
from pathlib import Path

from repo_model import ml
from repo_model import pressure_judge as pj

ROOT = Path(__file__).resolve().parents[1]
DECLARED = json.loads((ROOT / "metadata" / "risk_date_hurdle.json").read_text())
PARENTS = json.loads((ROOT / "metadata" / "risk_date_severity.json").read_text())
JUDGE_CANDIDATES = dict(pj.load_declaration().candidates)


def _script():
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("risk_date_hurdle_script", ROOT / "scripts" / "risk_date_hurdle.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SCRIPT = _script()


class DeclarationTests(unittest.TestCase):
    def test_the_declaration_is_what_the_script_declares(self):
        self.assertEqual(SCRIPT.declaration_document(PARENTS), DECLARED)

    def test_at_most_four_variants_and_they_are_the_models(self):
        self.assertLessEqual(len(DECLARED["variants"]), 4)
        self.assertEqual(set(DECLARED["variants"]), set(ml.HURDLE_VARIANTS))

    def test_the_hazard_reads_the_signal_that_ranks_the_missed_years_best(self):
        for spec in DECLARED["variants"].values():
            self.assertIn("sofr_p99_iorb_bps", spec["inputs"])
            self.assertIn("sofr_p75_iorb_bps", spec["inputs"])

    def test_the_regime_labels_drawn_after_the_fact_are_not_an_input(self):
        for spec in DECLARED["variants"].values():
            self.assertNotIn("regime", spec["inputs"])

    def test_the_parents_are_the_five_risk_date_passers_and_unchanged(self):
        for name, spec in DECLARED["parents"].items():
            self.assertEqual(spec, PARENTS["candidates"][name])
        self.assertEqual(len(DECLARED["parents"]), 5)

    def test_every_variant_is_a_judge_candidate_with_its_parents_features(self):
        for parent in DECLARED["parents"]:
            for variant in DECLARED["variants"]:
                entry = JUDGE_CANDIDATES[parent + variant]
                self.assertEqual(entry["role"], "candidate")
                self.assertEqual(entry["parent"], parent)
                self.assertEqual(entry["features"], JUDGE_CANDIDATES[parent]["features"])

    def test_the_scoring_window_ends_before_the_lockbox(self):
        self.assertLess(DECLARED["scoring"]["last_day"], "2026-01-01")

    def test_nothing_is_published(self):
        self.assertIn("nothing", DECLARED["published"])


class LogLossTests(unittest.TestCase):
    def test_the_pairing_is_the_reference_loss_minus_the_variants_inside_the_cell(self):
        outcomes = [1, 0, 1]
        variant = [0.5, 0.2, 0.9]
        parent = [0.0, 0.0, 0.5]
        inside, difference = SCRIPT.log_loss_vectors(variant, parent, outcomes, {0, 1}, 1e-6)
        self.assertEqual(inside, [1.0, 1.0, 0.0])
        self.assertAlmostEqual(difference[0], -math.log(1e-6) + math.log(0.5))
        self.assertAlmostEqual(difference[1], -math.log(1.0 - 1e-6) + math.log(0.8))
        self.assertEqual(difference[2], 0.0)

    def test_a_parents_exact_zero_on_a_pressure_day_costs_the_floor(self):
        _inside, difference = SCRIPT.log_loss_vectors([1.0], [0.0], [1], {0}, 1e-6)
        self.assertAlmostEqual(difference[0], -math.log(1e-6) + math.log(1.0 - 1e-6))


if __name__ == "__main__":
    unittest.main()
