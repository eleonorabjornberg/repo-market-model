"""The unused-input refit (#477, track U of #374): what is declared, before any score.

No availability or staleness guard is added by this directive: every column is read through the
as-of rule at the lag its own source declares, and those guards are tested where the columns are
(`test_net_settlement`, `test_policy_features`, `test_fed_liquidity`, `test_asof`). These tests pin
the declaration: each candidate is its passer plus exactly one declared group, every column is
collected and off in the published feature map, and nothing is named for the confirmation look.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model import contract, pressure_judge as pj  # noqa: E402

spec = importlib.util.spec_from_file_location("unused_inputs", ROOT / "scripts" / "unused_inputs.py")
script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script)

DECLARED = json.loads((ROOT / "metadata" / "unused_inputs.json").read_text(encoding="utf-8"))
RISK = json.loads((ROOT / "metadata" / "risk_date_severity.json").read_text(encoding="utf-8"))


class DeclarationTests(unittest.TestCase):
    def test_fifteen_candidates_are_five_passers_times_three_groups(self):
        self.assertEqual(len(DECLARED["candidates"]), 15)
        self.assertEqual({e["group"] for e in DECLARED["candidates"].values()}, set(DECLARED["groups"]))
        self.assertEqual(
            {e["passer"] for e in DECLARED["candidates"].values()},
            {"risk_gbm", "risk_gbm_base", "risk_logistic", "risk_logistic_base", "risk_quantile_skewt_base"},
        )

    def test_each_candidate_is_its_passer_plus_its_group_at_every_horizon(self):
        for name, entry in DECLARED["candidates"].items():
            for horizon in DECLARED["horizons"]:
                passer = script.candidate_features(DECLARED, RISK, entry["passer"], horizon)
                got = script.candidate_features(DECLARED, RISK, name, horizon)
                self.assertEqual(got[: len(passer)], passer, (name, horizon))
                self.assertEqual(list(got[len(passer):]), DECLARED["groups"][entry["group"]]["columns"], (name, horizon))

    def test_the_candidate_files_match_the_declaration(self):
        declaration = pj.load_declaration()
        for name, entry in DECLARED["candidates"].items():
            filed = declaration.candidates[name]
            self.assertEqual(filed["role"], "candidate")
            self.assertEqual(filed["control"], entry["passer"])
            self.assertEqual(
                list(filed["features"]),
                list(script.candidate_features(DECLARED, RISK, name, 1)),
                name,
            )

    def test_every_group_column_is_collected_and_off_in_the_published_feature_map(self):
        collected = script.all_column_fields()
        for group in DECLARED["groups"].values():
            for column in group["columns"]:
                if column == "dealer_treasury_position":
                    self.assertIn(column, contract.FEATURE_FIELDS)
                    continue
                self.assertIn(column, collected, column)
                self.assertNotIn(column, contract.FEATURE_FIELDS, column)

    def test_the_left_out_columns_are_not_in_any_group(self):
        used = {c for g in DECLARED["groups"].values() for c in g["columns"]}
        self.assertEqual(set(DECLARED["groups"]["dealer"]["left_out"]) - {"why"}, {"ofr_tri_rate", "ofr_gcf_rate"})
        self.assertFalse(used & {"ofr_tri_rate", "ofr_gcf_rate"})

    def test_no_candidate_is_named_for_the_confirmation_look(self):
        declaration = pj.load_declaration()
        self.assertFalse(set(DECLARED["candidates"]) & set(declaration.confirmation_candidates))

    def test_the_scored_days_stop_before_the_locked_tiers(self):
        self.assertEqual(DECLARED["scoring"]["last_day"], "2025-12-31")

    def test_the_inventory_lists_every_group_column(self):
        text = script.inventory_markdown(DECLARED)
        for group in DECLARED["groups"].values():
            for column in group["columns"]:
                self.assertIn(f"`{column}`", text)


if __name__ == "__main__":
    unittest.main()
