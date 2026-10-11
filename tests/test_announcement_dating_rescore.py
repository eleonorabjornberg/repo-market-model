"""The re-score of #541 reads each arm's inputs as declared, and agrees with the model's risk-date rule.

`scripts/announcement_dating_rescore.py` scores the five risk-date passers and their `+gate` rows under the
published declaration and under settlements dated from the announcement, the H.4.1 read per release, and both
(`metadata/announcement_dating.json`). The dating itself is tested in `test_announcement_dating.py`.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

DECLARED = json.loads((ROOT / "metadata" / "announcement_dating.json").read_text())
PARENTS = json.loads((ROOT / "metadata" / "risk_date_severity.json").read_text())
CANDIDATES = ROOT / "metadata" / "pressure_judge" / "candidates"


def _script():
    spec = importlib.util.spec_from_file_location("announcement_dating_rescore_script", ROOT / "scripts" / "announcement_dating_rescore.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DeclarationTests(unittest.TestCase):
    def test_every_row_the_script_scores_is_a_declared_judge_candidate(self):
        script = _script()
        for model in script.MODELS:
            for arm in script.ARMS:
                for name in script.names(model, arm):
                    self.assertTrue((CANDIDATES / f"{name}.json").exists(), name)
                    entry = json.loads((CANDIDATES / f"{name}.json").read_text())
                    self.assertEqual(entry["role"], "candidate")

    def test_the_models_and_scoring_are_the_severity_declarations(self):
        script = _script()
        self.assertEqual(sorted(DECLARED["models"]), sorted(script.MODELS))
        for name in script.MODELS:
            self.assertEqual(DECLARED["models"][name], PARENTS["candidates"][name])
        self.assertEqual(DECLARED["scoring"], PARENTS["scoring"])
        self.assertEqual(DECLARED["scoring"]["last_day"], "2025-12-31")

    def test_the_published_arm_is_the_control_and_changes_nothing(self):
        script = _script()
        self.assertEqual(script.ARMS["published"], (False, False, ""))

    def test_the_seven_coupon_onsets_are_those_of_the_desk_standard_page(self):
        script = _script()
        page = (ROOT / "docs" / "pivot" / "desk-standard-result.md").read_text()
        for day in script.COUPON_ONSETS:
            self.assertIn(day, page)
        self.assertEqual(len(script.COUPON_ONSETS), 7)


class ArmInputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from repo_model import cli, measurement_fields
        from repo_model.data import load_daily_panel

        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text())
        with tempfile.TemporaryDirectory() as directory:
            panel = Path(directory) / "panel.csv"
            with contextlib.redirect_stdout(io.StringIO()):
                code = cli.main([
                    "build", "--raw-root", str(ROOT / "tests/fixtures/snapshots/funding_inputs"),
                    "--output", str(panel), "--build-cutoff", manifest["build_cutoff"],
                    "--decision-time", manifest["decision_time"],
                ])
            assert code == 0, code
            cls.rows = load_daily_panel(panel)
        cls.registry = measurement_fields.load_registry()
        cls.script = _script()

    def test_the_published_arm_reads_the_rows_and_registry_unchanged(self):
        rows, registry = self.script.arm_inputs("published", self.rows, self.registry, 3)
        self.assertIs(rows, self.rows)
        self.assertEqual(json.dumps(registry, sort_keys=True, default=str), json.dumps(dict(self.registry), sort_keys=True, default=str))

    def test_the_settle_arm_dates_the_columns_at_the_horizon_and_is_checked(self):
        for horizon in (2, 3, 4, 5):
            with self.subTest(horizon=horizon):
                rows, registry = self.script.arm_inputs("settle", self.rows, self.registry, horizon)
                block = registry["treasury_auctions"]["scheduled_availability"]
                self.assertEqual((block["days"], block["available_time"]), (horizon, "12:00"))
                self.assertNotIn("release_calendar", registry["fred_macro_latest_vintage"])
                self.assertEqual(len(rows), len(self.rows))

    def test_at_horizon_one_the_settle_arm_reads_the_published_columns(self):
        rows, _registry = self.script.arm_inputs("settle", self.rows, self.registry, 1)
        for old, new in zip(self.rows[1:], rows[1:]):
            for column in ("treasury_settlement", "treasury_settlement_bills", "treasury_settlement_coupons"):
                a, b = old.values.get(column), new.values[column]
                self.assertEqual(a is None, b is None, (old.date, column))
                if a is not None:
                    self.assertAlmostEqual(a, b, places=9, msg=str(old.date))

    def test_the_h41_arm_changes_the_registry_and_not_the_rows(self):
        rows, registry = self.script.arm_inputs("h41", self.rows, self.registry, 2)
        self.assertIs(rows, self.rows)
        self.assertEqual(registry["fred_macro_latest_vintage"]["release_calendar"]["available_time"], "16:30")
        self.assertEqual(registry["treasury_auctions"]["scheduled_availability"]["days"], 1)

    def test_the_settle_arm_keeps_the_settlement_features_at_every_horizon(self):
        script = self.script
        spec = PARENTS["candidates"]["risk_gbm"]
        for horizon in (1, 2, 5):
            with self.subTest(horizon=horizon):
                kept = script.features_for(PARENTS, spec, horizon, True)
                self.assertIn("treasury_settlement_coupons", kept)
                dropped = script.features_for(PARENTS, spec, horizon, False)
                self.assertEqual("treasury_settlement_coupons" in dropped, horizon == 1)

    def test_the_risk_flag_agrees_with_the_model_rule(self):
        from repo_model import ml
        from repo_model.data import DailyObservation
        from repo_model.evaluation_splits import load_split_declaration

        splits = load_split_declaration(ROOT / "metadata" / "evaluation_splits.json")
        calendar = ("spread_bps", "days_to_month_end", "quarter_end", "tax_date")
        plain = ml._RiskDateDesign(calendar, splits)
        with_coupons = ml._RiskDateDesign(calendar + ("treasury_settlement_coupons",), splits)
        for quarter_end in (0.0, 1.0):
            for tax_date in (0.0, 1.0):
                for to_month_end in (0.0, 12.0):
                    for coupons in (0.0, 35.0):
                        values = {"sofr": 5.1, "iorb": 5.0, "quarter_end": quarter_end, "tax_date": tax_date,
                                  "days_to_month_end": to_month_end, "treasury_settlement_coupons": coupons}
                        observation = DailyObservation(date(2024, 3, 12), values)
                        self.assertEqual(self.script.risk_flag(splits, values, False), plain.member(observation))
                        self.assertEqual(self.script.risk_flag(splits, values, True), with_coupons.member(observation))


if __name__ == "__main__":
    unittest.main()
