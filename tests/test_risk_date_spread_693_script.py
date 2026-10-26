"""The helpers of `scripts/risk_date_spread_693.py` (#693; H6 step 1, development tier).

Written after the script, which is measurement code; its one guard, `require_scored_days`, has a recorded mutation:
replacing `if day > last:` with `if day > last + timedelta(days=400):` made
`ScopeTests.test_a_day_after_the_declared_end_is_refused` fail with `AssertionError` ("LookAheadError not raised");
restored, it passes.
"""

from __future__ import annotations

import importlib.util
import json
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import risk_date_spread as rds
from repo_model import scoring_protocol as sp
from repo_model.splits import LookAheadError

import test_protocol_benchmarks as tpb

import legacy_day_types

# this module reproduces legacy figures: the pre-#1135 day types (see tests/legacy_day_types.py)
setUpModule, tearDownModule = legacy_day_types.setUpModule, legacy_day_types.tearDownModule

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("risk_date_spread_693", ROOT / "scripts" / "risk_date_spread_693.py")
script = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(script)


class ScopeTests(unittest.TestCase):

    def test_a_day_after_the_declared_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.require_scored_days([date(2025, 12, 31), date(2026, 1, 2)])

    def test_the_declared_last_day_is_scored(self):
        script.require_scored_days([date(2025, 12, 31)])

    def test_a_locked_day_is_refused_even_when_the_end_is_moved(self):
        with self.assertRaises(LookAheadError):
            script.require_scored_days([date(2026, 9, 4)], last=date(2027, 1, 1))

    def test_the_declaration_ends_where_the_script_does(self):
        declaration = json.loads((ROOT / "metadata" / "risk_date_spread_693.json").read_text())
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(declaration["scoring"]["interval"].count("seed 693"), 1)
        self.assertEqual(script.SEED, 693)


class DeclarationTests(unittest.TestCase):

    def test_the_declared_counts_are_the_panels(self):
        panel = tpb.published_panel()["rows"]
        table = script.risk_counts(panel, tpb.SPLITS)
        declared = json.loads((ROOT / "metadata" / "risk_date_spread_693.json").read_text())
        counts = {k: v for k, v in declared["day_set"]["counts_per_year_to_2025-12-31"].items() if k != "note"}
        self.assertEqual(table, counts)

    def test_the_declared_types_are_the_modules(self):
        panel = tpb.published_panel()["rows"]
        self.assertEqual(set(script.risk_counts(panel, tpb.SPLITS)["total"]), set(rds.RISK_TYPES) | {"not_a_risk_date"})

    def test_the_declared_minimum_cell_and_window_are_the_modules(self):
        declared = json.loads((ROOT / "metadata" / "risk_date_spread_693.json").read_text())
        text = declared["candidates"]["type_state"]["definition"]
        self.assertIn(f"fewer than {rds.MIN_CELL} days", text)
        self.assertIn("two years", text)


class ScoreTests(unittest.TestCase):

    def test_mae_is_the_absolute_error_of_the_median(self):
        quantiles = [float(i) for i in range(len(sp.GRID))]
        self.assertEqual(script.mae_score(quantiles, 14.0), 3.0)
        self.assertEqual(script.mae_score(quantiles, 9.0), 2.0)

    def test_a_perfect_median_scores_zero(self):
        self.assertEqual(script.mae_score([5.0] * len(sp.GRID), 5.0), 0.0)


class KillRuleTests(unittest.TestCase):

    def row(self, low):
        return {"skill": 0.1, "skill_interval": [low, 0.2]}

    def primary(self, crps_b1, crps_cal, mae_b1, mae_cal, other=-0.1):
        def vs(candidate_values):
            return {c: {"B1": self.row(v[0]), "calendar": self.row(v[1])} for c, v in candidate_values.items()}
        both = {script.A: (crps_b1, crps_cal), script.C: (other, other)}
        mae = {script.A: (mae_b1, mae_cal), script.C: (other, other)}
        return {"grid_crps": {"vs": vs(both)}, "mae": {"vs": vs(mae)}}

    def test_skill_against_both_benchmarks_on_one_metric_keeps_it_alive(self):
        out = script.kill_rule(self.primary(0.05, 0.03, -0.1, -0.1))
        self.assertFalse(out["killed"])
        self.assertEqual(out["against_both"], [script.A])

    def test_skill_against_one_benchmark_only_kills_on_the_declared_reading(self):
        out = script.kill_rule(self.primary(0.05, -0.02, -0.1, -0.1))
        self.assertTrue(out["killed"])
        self.assertFalse(out["killed_on_the_weaker_reading"])
        self.assertEqual(out["against_at_least_one"], [script.A])

    def test_no_skill_anywhere_kills_on_both_readings(self):
        out = script.kill_rule(self.primary(-0.05, -0.02, -0.1, -0.1))
        self.assertTrue(out["killed"])
        self.assertTrue(out["killed_on_the_weaker_reading"])

    def test_skill_split_across_metrics_is_not_skill_against_both(self):
        # CRPS skill against B1 only, MAE skill against the calendar only: neither metric clears both benchmarks
        out = script.kill_rule(self.primary(0.05, -0.02, -0.1, 0.04))
        self.assertTrue(out["killed"])

    def test_an_undefined_skill_is_no_skill(self):
        row = {"undefined": "benchmark scores zero"}
        self.assertFalse(script.has_skill(row))

    def test_an_interval_that_touches_zero_is_no_skill(self):
        self.assertFalse(script.has_skill(self.row(0.0)))
        self.assertTrue(script.has_skill(self.row(0.001)))


class ReportTests(unittest.TestCase):

    def test_verdict_words_name_the_candidate_with_skill(self):
        result = {"kill_rule": {"killed": False, "killed_on_the_weaker_reading": False, "against_both": [script.C],
                                "against_at_least_one": [script.C]}}
        self.assertIn(script.LABEL[script.C], script.verdict_words(result))
        self.assertIn("Not killed", script.verdict_words(result))

    def test_verdict_words_say_killed_when_nothing_has_skill(self):
        result = {"kill_rule": {"killed": True, "killed_on_the_weaker_reading": True, "against_both": [], "against_at_least_one": []}}
        self.assertIn("Killed on both readings", script.verdict_words(result))


if __name__ == "__main__":
    unittest.main()
