"""The four model-defect changes (#540): the declaration, the judge's candidate files and the script's rules."""

import importlib.util
import json
import sys
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

from repo_model import pressure_judge as pj
from repo_model.evaluation_splits import load_split_declaration
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
DECLARED = json.loads((ROOT / "metadata" / "model_defects_540.json").read_text())
PARENTS = json.loads((ROOT / "metadata" / "risk_date_severity.json").read_text())
JUDGE_CANDIDATES = dict(pj.load_declaration().candidates)
SPLITS = load_split_declaration(ROOT / "metadata" / "evaluation_splits.json")


def _script():
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("model_defects_540_script", ROOT / "scripts" / "model_defects_540.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["model_defects_540_script"] = module
    spec.loader.exec_module(module)
    return module


SCRIPT = _script()


class DeclarationTests(unittest.TestCase):
    def test_the_parents_are_the_five_risk_date_passers_and_unchanged(self):
        self.assertEqual(
            set(DECLARED["parents"]),
            {"risk_gbm", "risk_gbm_base", "risk_logistic", "risk_logistic_base", "risk_quantile_skewt_base"},
        )
        for name, spec in DECLARED["parents"].items():
            self.assertEqual(spec, PARENTS["candidates"][name])

    def test_the_scoring_window_ends_before_the_lockbox(self):
        self.assertLess(DECLARED["scoring"]["last_day"], "2026-01-01")

    def test_every_variant_of_every_parent_is_a_judge_candidate_with_the_declared_features(self):
        for parent in DECLARED["parents"]:
            base = JUDGE_CANDIDATES[parent]["features"]
            for variant, spec in DECLARED["variants"].items():
                entry = JUDGE_CANDIDATES[parent + spec["suffix"]]
                self.assertEqual(entry["role"], "candidate")
                self.assertEqual(entry["parent"], parent)
                has_iorb = "announced_iorb_input" in spec["changes"]
                self.assertEqual(entry["features"], base + (["iorb_announced_change_bps"] if has_iorb else []))

    def test_the_script_has_a_flag_set_for_every_declared_variant(self):
        self.assertEqual(set(SCRIPT.FLAGS), set(DECLARED["variants"]))
        for variant, (leaf, iorb, added) in SCRIPT.FLAGS.items():
            names = set(DECLARED["variants"][variant]["changes"])
            self.assertEqual(leaf, "early_fit_leaf_floor" in names)
            self.assertEqual(iorb, "announced_iorb_input" in names)
            self.assertEqual(added, "added_risk_dates_modelled_apart" in names)

    def test_nothing_in_the_published_declaration_moves(self):
        self.assertNotIn("iorb_announced_change_bps", json.dumps(PARENTS["features"]))


class LeafFloorTests(unittest.TestCase):
    def test_the_floor_scales_with_the_pairs_and_stops_at_the_declared_twenty(self):
        self.assertEqual([SCRIPT.leaf_floor(n) for n in (1, 3, 4, 12, 39, 40, 79, 80, 500)], [1, 1, 1, 3, 9, 10, 19, 20, 20])

    def test_a_fit_with_fewer_than_forty_pairs_is_not_a_constant_with_the_floor_and_is_without_it(self):
        import random

        rng = random.Random(3)
        xs = [[rng.random(), rng.random()] for _ in range(24)]
        spreads = [8.0 if x[0] > 0.7 else 1.0 for x in xs]
        served = [[0.1, 0.5], [0.95, 0.5]]
        taus = (5.0, 10.0)
        flat = {"taus": {}}
        scaled = {"taus": {}}
        SCRIPT.fit_group("gbm_classifier", xs, spreads, served, taus, False, flat)
        SCRIPT.fit_group("gbm_classifier", xs, spreads, served, taus, True, scaled)
        self.assertTrue(flat["taus"]["5"]["constant_on_its_training_pairs"])
        self.assertEqual(flat["taus"]["5"]["min_samples_leaf"], 20)
        self.assertFalse(scaled["taus"]["5"]["constant_on_its_training_pairs"])
        self.assertEqual(scaled["taus"]["5"]["min_samples_leaf"], 6)


class AddedRiskDateTests(unittest.TestCase):
    def values(self, day, **columns):
        base = {"days_to_month_end": 10.0, "quarter_end": 0.0, "tax_date": 0.0, "treasury_settlement": 0.0, "treasury_settlement_coupons": 0.0}
        base.update(columns)
        return base

    def test_a_declared_risk_date_is_not_an_added_one(self):
        day = date(2019, 3, 29)
        values = self.values(day, days_to_month_end=0.0, quarter_end=1.0)
        self.assertFalse(SCRIPT.added_rule(SPLITS, day, values, 1))

    def test_a_bill_settlement_day_is_added_at_horizon_one_only(self):
        day = date(2019, 5, 28)
        values = self.values(day, treasury_settlement=75.0)
        self.assertTrue(SCRIPT.added_rule(SPLITS, day, values, 1))
        self.assertFalse(SCRIPT.added_rule(SPLITS, day, values, 2))

    def test_the_fourth_last_business_day_of_a_quarter_end_month_is_not_added(self):
        # 2024-12-26 is the 4th-last business day: neither the declared window nor the business-day one reaches it
        day = date(2024, 12, 26)
        self.assertFalse(SCRIPT.added_rule(SPLITS, day, self.values(day, days_to_month_end=5.0), 2))

    def test_the_second_last_business_day_of_a_month_is_added_at_every_horizon(self):
        day = date(2018, 12, 28)  # 3 calendar days from month-end: outside day_type, inside reporting_day_type
        values = self.values(day, days_to_month_end=3.0)
        self.assertTrue(SCRIPT.added_rule(SPLITS, day, values, 2))


class LockboxGuardTests(unittest.TestCase):
    """`run` and `nowcast` refuse a scored day in a tier the lockbox has not opened.

    Recorded mutation, 11 October 2026, in a disposable copy: `scripts/model_defects_540.py`, the line
    `require_unlocked([last], where="model_defects_540")` replaced by `pass` in `run_command` and in
    `nowcast_command`. `test_run_refuses_a_locked_last_day` then errors with `FileNotFoundError` (the guard is
    skipped and the run goes on to read the panel), and `test_nowcast_refuses_a_locked_last_day` errors with
    `FileNotFoundError` the same way (the nowcast declaration loader, mocked to raise it, is reached next).
    """

    def args(self, **changes):
        import argparse

        base = dict(variant="all", horizon=1, candidate=None, declared=None, panel=ROOT / "no-such-panel.csv",
                    published=ROOT / "no-such-panel.csv", output=ROOT / "no-such-output.json")
        base.update(changes)
        return argparse.Namespace(**base)

    def test_run_refuses_a_locked_last_day(self):
        declared = json.loads(json.dumps(DECLARED))
        declared["scoring"]["last_day"] = "2026-09-10"
        with mock.patch.object(SCRIPT, "declared_document", return_value=declared):
            with self.assertRaises(LookAheadError):
                SCRIPT.run_command(self.args())

    def test_nowcast_refuses_a_locked_last_day(self):
        declared = json.loads(json.dumps(DECLARED))
        declared["scoring"]["last_day"] = "2026-09-10"
        with mock.patch.object(SCRIPT, "declared_document", return_value=declared), mock.patch.object(
            SCRIPT.nowcast, "load_declaration", side_effect=FileNotFoundError
        ):
            with self.assertRaises(LookAheadError):
                SCRIPT.nowcast_command(self.args())

    def test_the_declared_last_day_is_not_refused(self):
        with mock.patch.object(SCRIPT, "load_daily_panel", side_effect=FileNotFoundError):
            with self.assertRaises(FileNotFoundError):  # past the guard, into the panel
                SCRIPT.run_command(self.args())


if __name__ == "__main__":
    unittest.main()
