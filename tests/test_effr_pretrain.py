"""The pre-2018 pre-training study (#544): its declaration, its source labels and its combination rule."""

import importlib.util
import json
import sys
import unittest
from pathlib import Path

from repo_model import ml
from repo_model import pressure_judge as pj

ROOT = Path(__file__).resolve().parents[1]
DECLARED = json.loads((ROOT / "metadata" / "effr_pretrain.json").read_text())
PARENTS = json.loads((ROOT / "metadata" / "risk_date_severity.json").read_text())
JUDGE_CANDIDATES = dict(pj.load_declaration().candidates)


def _script():
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("effr_pretrain_script", ROOT / "scripts" / "effr_pretrain.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SourceThresholdTests(unittest.TestCase):
    def test_the_threshold_matches_the_event_rate(self):
        script = _script()
        source = [float(-i) for i in range(1, 11)]  # -1 .. -10 bp
        sofr = [6.0] + [0.0] * 9  # 10% above +5 bp
        self.assertEqual(script.derive_source_thresholds(source, sofr, [5.0]), {5.0: -2.0})

    def test_a_tie_goes_to_the_higher_threshold(self):
        script = _script()
        source = [float(-i) for i in range(1, 11)]
        sofr = [6.0] * 3 + [0.0] * 17  # 15%: 10% above -2, 20% above -3
        self.assertEqual(script.derive_source_thresholds(source, sofr, [5.0]), {5.0: -2.0})

    def test_each_sofr_threshold_has_its_own_source_threshold(self):
        script = _script()
        source = [float(-i) for i in range(1, 11)]
        sofr = [12.0, 12.0] + [6.0, 6.0] + [0.0] * 16  # 20% above +5, 10% above +10
        self.assertEqual(script.derive_source_thresholds(source, sofr, [5.0, 10.0]), {5.0: -3.0, 10.0: -2.0})

    def test_empty_inputs_are_refused(self):
        with self.assertRaises(ValueError):
            _script().derive_source_thresholds([], [1.0], [5.0])


class CombinationTests(unittest.TestCase):
    def test_a_risk_date_keeps_the_passer_and_any_other_day_the_component(self):
        script = _script()
        passer = {"5": {"2020-01-02": 0.4, "2020-01-03": 0.0}}
        component = {"5": {"2020-01-02": 0.1, "2020-01-03": 0.07}}
        risk = {"2020-01-02": True, "2020-01-03": False}
        got = script.combine_forecasts(passer, component, risk)
        self.assertEqual(got, {"5": {"2020-01-02": 0.4, "2020-01-03": 0.07}})

    def test_days_that_do_not_line_up_are_refused(self):
        script = _script()
        with self.assertRaises(ValueError):
            script.combine_forecasts({"5": {"a": 0.1}}, {"5": {"b": 0.1}}, {"a": True})

    def test_log_loss_is_clipped_so_an_exact_zero_is_finite(self):
        script = _script()
        self.assertAlmostEqual(script.log_loss(0.0, 1), 13.815510557964274, places=6)
        self.assertAlmostEqual(script.log_loss(1.0, 0), 13.815510557964274, places=6)


class DeclarationTests(unittest.TestCase):
    def test_the_declaration_is_what_the_script_declares(self):
        script = _script()
        thresholds = {float(k): v for k, v in DECLARED["source"]["thresholds_bp"].items()}
        self.assertEqual(script.declaration_document(PARENTS, thresholds), DECLARED)

    def test_the_declared_weight_and_variants_are_the_modules(self):
        self.assertEqual(DECLARED["variants"]["effr_pooled"]["source_weight"], ml.PRESSURE_TRANSFER_SOURCE_WEIGHT)
        self.assertEqual(
            {spec["variant"] for spec in DECLARED["variants"].values()} - {"none"}, set(ml.PRESSURE_TRANSFER_VARIANTS)
        )

    def test_every_threshold_has_a_source_threshold_below_the_sofr_one(self):
        # Fed funds traded below IOER throughout: the +5 bp event does not exist in the source.
        for tau in DECLARED["thresholds_bp"]:
            self.assertLess(DECLARED["source"]["thresholds_bp"][f"{tau:g}"], tau)
        self.assertEqual(
            sorted(DECLARED["source"]["thresholds_bp"].values()), list(DECLARED["source"]["thresholds_bp"].values())
        )

    def test_the_design_reads_no_settlement_and_nothing_built_after_2018(self):
        features = DECLARED["design"]["features"]
        self.assertFalse([f for f in features if "settlement" in f or f.startswith("sofr_") or f == "on_rrp"])

    def test_every_model_and_combined_row_is_a_judge_candidate(self):
        script = _script()
        for name in list(script.TRANSFER_MODELS) + list(script.COMBINED.values()):
            self.assertEqual(JUDGE_CANDIDATES[name]["role"], "candidate")
        for name in script.TRANSFER_MODELS:
            self.assertEqual(JUDGE_CANDIDATES[name]["features"], list(script.FEATURES))
        for name, combined in script.COMBINED.items():
            self.assertEqual(JUDGE_CANDIDATES[combined]["parent"], "risk_gbm")
            self.assertEqual(DECLARED["combined"]["rows"][combined], name)

    def test_the_candidate_files_are_what_the_script_declares(self):
        script = _script()
        for name, entry in script.candidate_entries(DECLARED).items():
            self.assertEqual(JUDGE_CANDIDATES[name], entry)

    def test_the_scoring_window_ends_before_the_lockbox(self):
        self.assertLess(DECLARED["scoring"]["last_day"], "2026-01-01")
        self.assertEqual(DECLARED["scoring"], PARENTS["scoring"])

    def test_nothing_is_published(self):
        self.assertIn("nothing", DECLARED["published"])
        self.assertIn("only the pattern transfers", DECLARED["source"]["caveat"])
        self.assertIn("never scored", DECLARED["source"]["role"] + " never scored")


if __name__ == "__main__":
    unittest.main()
