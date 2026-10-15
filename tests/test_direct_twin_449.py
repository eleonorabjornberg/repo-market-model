"""The direct-pairs twin of gbm_funding (`scripts/direct_twin_449.py`, #449): the parts that decide what is read.

Recorded mutation (the one leakage guard this script adds; the scorer's own lockbox guard is tested with the scorer):

* `require_study_window`, the condition `day > LAST_TARGET` changed to `day > LAST_TARGET + timedelta(days=400)`:
  `StudyWindowTests.test_a_day_after_the_study_end_is_refused` fails with `AssertionError` (`LookAheadError not raised`,
  for 2026-01-02).
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("direct_twin_449_script", REPO / "scripts" / "direct_twin_449.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model.splits import LookAheadError  # noqa: E402


class StudyWindowTests(unittest.TestCase):
    def test_a_day_after_the_study_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.require_study_window([date(2025, 12, 31), date(2026, 1, 2)])
        script.require_study_window([date(2025, 12, 30), date(2025, 12, 31)])


class TwinTests(unittest.TestCase):
    def fit(self, **extra):
        return script.fitter(("a", "b", "spread_bps"), **extra)

    def test_the_twin_differs_from_the_control_in_training_pairs_alone(self):
        control, twin = self.fit(), self.fit(training_pairs="direct")
        self.assertEqual(control.func, twin.func)
        self.assertEqual(control.args, twin.args)
        self.assertNotIn("training_pairs", control.keywords)
        self.assertEqual(twin.keywords.pop("training_pairs"), "direct")
        self.assertEqual(control.keywords, twin.keywords)

    def test_the_target_is_not_its_own_regressor(self):
        self.assertEqual(self.fit().keywords["regressors"], ("a", "b"))

    def test_the_pairing_check_reads_the_walk_settings(self):
        script.check_pairing({"settings": {}}, {"settings": {"training_pairs": "direct"}})
        with self.assertRaises(ValueError):
            script.check_pairing({"settings": {"training_pairs": "direct"}}, {"settings": {"training_pairs": "direct"}})
        with self.assertRaises(ValueError):
            script.check_pairing({"settings": {}}, {"settings": {}})


class DaySetTests(unittest.TestCase):
    days = [date(2019, 9, 16) + timedelta(days=i) for i in range(5)]

    def test_the_excluded_day_is_removed_and_nothing_else(self):
        kept = script.without_excluded(self.days)
        self.assertNotIn(date(2019, 9, 18), kept)
        self.assertEqual(len(kept), len(self.days) - 1)
        self.assertEqual(script.without_excluded([date(2020, 1, 2)]), [date(2020, 1, 2)])

    def test_a_lead_series_holds_that_leads_cells_only(self):
        cells = {(self.days[0], 1): 1.0, (self.days[0], 2): 2.0, (self.days[1], 2): 3.0}
        self.assertEqual(script.lead_series(cells, 2), {self.days[0]: 2.0, self.days[1]: 3.0})
        self.assertEqual(script.lead_series(cells, 3), {})


class DeclarationTests(unittest.TestCase):
    def test_the_declaration_names_the_protocol_grid_and_the_ruled_exclusion(self):
        import json

        document = json.loads(script.DECLARATION.read_text(encoding="utf-8"))
        self.assertEqual(document["issue"], 449)
        self.assertIn("2019-09-18", json.dumps(document["tables"]))
        self.assertEqual(script.EXCLUDED_DAY, date(2019, 9, 18))


if __name__ == "__main__":
    unittest.main()
