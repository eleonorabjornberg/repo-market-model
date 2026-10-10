"""The every-day and early-fit variants (#506) agree with their parents, the judge and the script."""

import importlib.util
import json
import sys
import unittest
from pathlib import Path

from repo_model import ml
from repo_model import pressure_judge as pj

ROOT = Path(__file__).resolve().parents[1]
DECLARED = json.loads((ROOT / "metadata" / "risk_date_every_day.json").read_text())
PARENTS = json.loads((ROOT / "metadata" / "risk_date_severity.json").read_text())
JUDGE_CANDIDATES = dict(pj.load_declaration().candidates)


def _script():
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("risk_date_every_day_script", ROOT / "scripts" / "risk_date_every_day.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RiskDateEveryDayDeclarationTests(unittest.TestCase):
    def test_the_declaration_is_what_the_script_declares(self):
        self.assertEqual(_script().declaration_document(PARENTS), DECLARED)

    def test_the_parents_are_the_five_risk_date_passers_and_unchanged(self):
        self.assertEqual(
            set(DECLARED["parents"]),
            {"risk_gbm", "risk_gbm_base", "risk_logistic", "risk_logistic_base", "risk_quantile_skewt_base"},
        )
        for name, spec in DECLARED["parents"].items():
            self.assertEqual(spec, PARENTS["candidates"][name])

    def test_every_variant_is_a_judge_candidate_that_reads_its_parents_features_and_the_component(self):
        script = _script()
        for parent in DECLARED["parents"]:
            base = JUDGE_CANDIDATES[parent]["features"]
            for suffix, (every_day, _early) in script.VARIANTS.items():
                entry = JUDGE_CANDIDATES[parent + suffix]
                self.assertEqual(entry["role"], "candidate")
                self.assertEqual(entry["parent"], parent)
                extra = [n for n in ml.EVERY_DAY_COMPONENT_INPUTS if n not in base] if every_day else []
                self.assertEqual(entry["features"], base + extra)

    def test_the_declared_minimum_and_inputs_are_the_modules(self):
        self.assertEqual(DECLARED["early_fit"]["minimum_pairs"], ml.EARLY_FIT_MINIMUM_PAIRS)
        self.assertEqual(DECLARED["early_fit"]["prior_weight"], ml.EARLY_FIT_PRIOR_WEIGHT)
        self.assertEqual(DECLARED["every_day_component"]["inputs"], list(ml.EVERY_DAY_COMPONENT_INPUTS))

    def test_the_scoring_window_ends_before_the_lockbox(self):
        self.assertLess(DECLARED["scoring"]["last_day"], "2026-01-01")

    def test_nothing_is_published(self):
        self.assertIn("nothing", DECLARED["published"])
        self.assertNotIn("sofr_p99_iorb_bps", json.loads((ROOT / "metadata" / "pressure_judge.json").read_text()).get("features", []))


if __name__ == "__main__":
    unittest.main()
