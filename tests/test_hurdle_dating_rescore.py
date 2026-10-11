"""The re-score of #556 declares what it scores, and pairs each arm with the same variant under the published declaration.

`scripts/hurdle_dating_rescore.py` scores the twenty hurdle variants of #539 under the published declaration and under
settlements dated from the announcement, the H.4.1 read per release, and both (`metadata/hurdle_dating.json`). The dating
itself is tested in `test_announcement_dating.py`; the hurdle in `test_risk_date_hurdle.py` and `test_ml.py`.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

DECLARED = json.loads((ROOT / "metadata" / "hurdle_dating.json").read_text())
HURDLE = json.loads((ROOT / "metadata" / "risk_date_hurdle.json").read_text())
CANDIDATES = ROOT / "metadata" / "pressure_judge" / "candidates"


def _script():
    spec = importlib.util.spec_from_file_location("hurdle_dating_rescore_script", ROOT / "scripts" / "hurdle_dating_rescore.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SCRIPT = _script()


class DeclarationTests(unittest.TestCase):
    def test_the_declaration_is_what_the_script_declares(self):
        self.assertEqual(SCRIPT.declaration_document(HURDLE), DECLARED)

    def test_the_parents_variants_and_scoring_are_the_hurdle_declaration(self):
        self.assertEqual(DECLARED["parents"], HURDLE["parents"])
        self.assertEqual(DECLARED["variants"], HURDLE["variants"])
        self.assertEqual(DECLARED["scoring"], HURDLE["scoring"])
        self.assertEqual(DECLARED["scoring"]["last_day"], "2025-12-31")
        self.assertEqual(len(DECLARED["parents"]) * len(DECLARED["variants"]), 20)

    def test_every_row_the_script_scores_is_a_declared_judge_candidate(self):
        for parent in SCRIPT.PARENT_NAMES:
            for variant in SCRIPT.VARIANTS:
                for arm in SCRIPT.ARMS:
                    name = SCRIPT.name_of(parent, variant, arm)
                    with self.subTest(name=name):
                        entry = json.loads((CANDIDATES / f"{name}.json").read_text())
                        self.assertEqual(entry["role"], "candidate")

    def test_the_published_arm_is_the_control_and_changes_nothing(self):
        self.assertEqual(SCRIPT.ARMS["published"], (False, False, ""))
        self.assertEqual(SCRIPT.name_of("risk_gbm", "+hurdle_platt", "published"), "risk_gbm+hurdle_platt")

    def test_each_arm_variant_is_paired_with_the_same_variant_under_the_published_declaration(self):
        pairs = SCRIPT.rows_of_pairs()
        self.assertEqual(len(pairs), 5 * 4 * 3)
        for arm, name, published in pairs:
            self.assertNotEqual(arm, "published")
            self.assertEqual(name, published + SCRIPT.ARMS[arm][2])
            self.assertIn(published.split("+hurdle")[0], SCRIPT.PARENT_NAMES)

    def test_the_arm_candidates_carry_the_dating_and_the_parents_judge_entry(self):
        for arm in ("settle", "h41", "both"):
            suffix = SCRIPT.ARMS[arm][2]
            entry = json.loads((CANDIDATES / f"risk_gbm+hurdle_state_platt{suffix}.json").read_text())
            base = json.loads((CANDIDATES / "risk_gbm+hurdle_state_platt.json").read_text())
            self.assertEqual(entry["parent"], "risk_gbm+hurdle_state_platt")
            self.assertEqual(entry["role"], base["role"])
            self.assertIn("metadata/hurdle_dating.json", entry["calibration"])
            self.assertEqual("settlement" in entry["calibration"], arm in ("settle", "both"))
            self.assertEqual("H.4.1" in entry["calibration"], arm in ("h41", "both"))


if __name__ == "__main__":
    unittest.main()
