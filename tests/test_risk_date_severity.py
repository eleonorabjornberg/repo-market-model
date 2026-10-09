"""The risk-date severity model's declaration (#428) agrees with the judge's and with its script."""

import importlib.util
import json
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECLARED = json.loads((ROOT / "metadata" / "risk_date_severity.json").read_text())
JUDGE = json.loads((ROOT / "metadata" / "pressure_judge.json").read_text())


def _script():
    import sys

    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("risk_date_severity_script", ROOT / "scripts" / "risk_date_severity.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RiskDateDeclarationTests(unittest.TestCase):
    def test_every_candidate_is_declared_to_the_judge(self):
        for name in DECLARED["candidates"]:
            entry = JUDGE["candidates"][name]
            self.assertEqual(entry["role"], "candidate")
            self.assertEqual(entry["track"], "V (#428)")

    def test_the_judge_lists_the_features_the_script_reads_at_horizon_one(self):
        script = _script()
        for name, spec in DECLARED["candidates"].items():
            read = script.features_at_horizon(DECLARED, spec, 1)
            self.assertEqual(list(read), JUDGE["candidates"][name]["features"])

    def test_the_settlement_columns_leave_at_horizon_two_or_more(self):
        script = _script()
        for spec in DECLARED["candidates"].values():
            for column in script.SETTLEMENT_COLUMNS:
                self.assertIn(column, script.features_at_horizon(DECLARED, spec, 1))
                for h in range(2, 6):
                    self.assertNotIn(column, script.features_at_horizon(DECLARED, spec, h))

    def test_every_new_input_candidate_has_a_twin_without_the_new_inputs(self):
        script = _script()
        for name, spec in DECLARED["candidates"].items():
            if "new" in spec["inputs"]:
                twin = DECLARED["candidates"][name + script.TWIN_SUFFIX]
                self.assertEqual(twin["kind"], spec["kind"])
                self.assertEqual(twin["inputs"], ["base"])

    def test_the_scoring_window_ends_before_the_lockbox(self):
        self.assertEqual(DECLARED["scoring"]["last_day"], JUDGE["scoring"]["last_day"])
        self.assertEqual(DECLARED["horizons"], JUDGE["horizons"])
        self.assertEqual(DECLARED["thresholds_bp"], JUDGE["thresholds_bp"])

    def test_every_estimator_is_one_the_model_offers(self):
        import sys

        sys.path.insert(0, str(ROOT / "src"))
        from repo_model import ml

        for spec in DECLARED["candidates"].values():
            self.assertIn(spec["kind"], ml.RISK_DATE_KINDS)


class RiskDateRuleTests(unittest.TestCase):
    """The script's report reads the risk dates by the rule the model serves (`ml._RiskDateDesign.member`)."""

    def test_the_report_and_the_model_agree_on_which_days_are_risk_dates(self):
        script = _script()
        from repo_model import ml
        from repo_model.data import DailyObservation
        from repo_model.evaluation_splits import load_split_declaration

        splits = load_split_declaration(ROOT / "metadata" / "evaluation_splits.json")
        calendar = ("spread_bps", "days_to_month_end", "quarter_end", "tax_date")
        plain = ml._RiskDateDesign(calendar, splits)
        with_coupons = ml._RiskDateDesign(calendar + ("treasury_settlement_coupons",), splits)
        for quarter_end in (0.0, 1.0):
            for tax_date in (0.0, 1.0):
                for to_month_end in (0.0, 1.0, 12.0):
                    for coupons in (0.0, 35.0):
                        values = {
                            "sofr": 5.1,
                            "iorb": 5.0,
                            "quarter_end": quarter_end,
                            "tax_date": tax_date,
                            "days_to_month_end": to_month_end,
                            "treasury_settlement_coupons": coupons,
                        }
                        observation = DailyObservation(date(2024, 3, 12), values)
                        self.assertEqual(script.is_risk_date(splits, values, 2), plain.member(observation))
                        self.assertEqual(script.is_risk_date(splits, values, 1), with_coupons.member(observation))


if __name__ == "__main__":
    unittest.main()
