"""The twin diagnosis (`scripts/twin_diagnosis_865.py`, #865): the parts that decide what is read and how an arm differs.

Recorded mutation (the one leakage guard this script adds; the scorer's own lockbox guard is tested with the scorer):

* `require_study_window`, the line `if late:` changed to `if False:`:
  `StudyWindowTests.test_a_day_after_the_study_end_is_refused` fails with `AssertionError` (`LookAheadError not raised`).
"""

from __future__ import annotations

import importlib.util
import inspect
import json
import sys
import unittest
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("twin_diagnosis_865_script", REPO / "scripts" / "twin_diagnosis_865.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model.splits import LookAheadError  # noqa: E402


class StudyWindowTests(unittest.TestCase):
    def test_a_day_after_the_study_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.require_study_window([date(2025, 12, 31), date(2026, 1, 2)])
        script.require_study_window([date(2025, 12, 30), date(2025, 12, 31)])


class ArmTests(unittest.TestCase):
    features = ("a", "b", "spread_bps")

    def test_a_training_lag_above_the_lead_is_refused(self):
        with self.assertRaises(ValueError):
            script.check_arm(lead=3, k=4)
        with self.assertRaises(ValueError):
            script.check_arm(lead=3, k=0)
        script.check_arm(lead=3, k=3)
        script.check_arm(lead=3, k=1)

    def test_the_train_k_fit_names_information_so_the_walk_hands_it_over(self):
        registry = json.loads(script.SOURCES.read_text(encoding="utf-8"))
        fit = script.train_k_fit(("sofr_p25", "spread_bps"), 1, registry=registry)
        self.assertIn("information", inspect.signature(fit).parameters)

    def test_the_target_is_not_its_own_regressor(self):
        self.assertEqual(script.regressors(self.features), ("a", "b"))

    def test_the_trim_drops_the_rows_the_twin_trains_no_pair_on(self):
        rows = list(range(30))
        self.assertEqual(script.trimmed(rows, 5), rows[8:])
        self.assertEqual(script.trimmed(rows, 1), rows[4:])

    def test_arm_names_are_the_declared_ones(self):
        self.assertEqual(script.arm_name("train_k", 3), "gbm_funding_direct_k3")
        self.assertEqual(script.arm_name("control_trim"), "gbm_funding_trim")
        with self.assertRaises(ValueError):
            script.arm_name("other")


class SplitTests(unittest.TestCase):
    def test_half_years_are_calendar_halves_of_the_decision_day(self):
        self.assertEqual(script.half_year(date(2019, 6, 30)), "2019H1")
        self.assertEqual(script.half_year(date(2019, 7, 1)), "2019H2")

    def test_the_gap_closed_is_read_only_where_the_twin_is_worse(self):
        self.assertAlmostEqual(script.gap_closed(twin_to_arm=0.03, twin_to_control=0.04), 0.75)
        self.assertIsNone(script.gap_closed(twin_to_arm=0.03, twin_to_control=-0.01))


class DeclarationTests(unittest.TestCase):
    def test_the_declaration_names_the_arms_and_the_ruled_exclusion(self):
        document = json.loads(script.DECLARATION.read_text(encoding="utf-8"))
        self.assertEqual(document["issue"], 865)
        self.assertEqual(set(document["arms"]), {"train_k", "control_trim"})
        self.assertIn("2019-09-18", json.dumps(document["locate"]))
        self.assertEqual(script.EXCLUDED_DAY, date(2019, 9, 18))


if __name__ == "__main__":
    unittest.main()
