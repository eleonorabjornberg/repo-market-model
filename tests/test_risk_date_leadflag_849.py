"""The helpers of `scripts/risk_date_leadflag_849.py` (#849; H6 step 1 re-read, development tier).

Written after the script, which is measurement code; it adds no guard of its own (the lead-flag guard,
`risk_date_spread.require_settlement_public`, has its recorded mutation in `tests/test_risk_date_spread.py`). What these tests
pin: the old reading the control restores differs from the corrected one exactly where a settlement is not yet public, the
swap is undone, the comparison of two JSON trees, and the declaration's last day.
"""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

from repo_model import risk_date_spread as rds
from repo_model import scoring_protocol as sp

import test_protocol_benchmarks as tpb
from test_risk_date_spread import panel_and_settings, settlement_only_targets

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("risk_date_leadflag_849", ROOT / "scripts" / "risk_date_leadflag_849.py")
script = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(script)


class ReadingTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = panel_and_settings()

    def kinds(self, i, h):
        clock = dict(registry=tpb.REGISTRY, decision_time=tpb.DECISION, splits=tpb.SPLITS)
        return (
            script.old_target_risk_type(self.panel, i, h, **clock),
            rds.target_risk_type(self.panel, i, h, **clock),
        )

    def test_the_old_reading_types_a_settlement_at_every_lead(self):
        for i, h in settlement_only_targets(self.panel, sp.HORIZONS)[:30]:
            old, new = self.kinds(i, h)
            with self.subTest(decision=self.panel[i].date, lead=h):
                self.assertEqual(old, "settlement")
                self.assertEqual(new, "settlement" if h == 1 else None)

    def test_the_two_readings_agree_on_a_calendar_type(self):
        agreed = 0
        for i in range(600, 700):
            for h in sp.HORIZONS:
                old, new = self.kinds(i, h)
                if old != "settlement":
                    agreed += 1
                    self.assertEqual(old, new)
        self.assertTrue(agreed)

    def test_the_swap_is_undone(self):
        kept = rds.target_risk_type
        with script.reading(script.old_target_risk_type):
            self.assertIs(rds.target_risk_type, script.old_target_risk_type)
        self.assertIs(rds.target_risk_type, kept)
        with self.assertRaises(RuntimeError):
            with script.reading(script.old_target_risk_type):
                raise RuntimeError
        self.assertIs(rds.target_risk_type, kept)


class DifferenceTests(unittest.TestCase):

    def test_identical_trees_differ_by_zero(self):
        tree = {"a": [1.0, {"b": 2}], "c": "x"}
        self.assertEqual(script.max_difference(tree, json.loads(json.dumps(tree))), 0.0)

    def test_the_largest_numeric_difference_is_returned(self):
        self.assertAlmostEqual(script.max_difference({"a": [1.0, 2.0], "b": 5}, {"a": [1.5, 2.0], "b": 4}), 1.0)

    def test_a_changed_string_or_shape_has_no_difference_to_report(self):
        self.assertIsNone(script.max_difference({"a": "x"}, {"a": "y"}))
        self.assertIsNone(script.max_difference({"a": [1, 2]}, {"a": [1]}))

    def test_two_undefined_rows_agree_whatever_their_reasons_say(self):
        self.assertEqual(script.max_difference({"r": {"undefined": "a"}}, {"r": {"undefined": "b"}}), 0.0)
        self.assertIsNone(script.max_difference({"r": {"undefined": "a"}}, {"r": {"skill": 1.0}}))

    def test_a_changed_flag_is_not_a_zero_difference(self):
        self.assertIsNone(script.max_difference({"killed": True}, {"killed": False}))


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_ends_where_the_script_ends(self):
        declaration = json.loads((ROOT / "metadata" / "risk_date_leadflag_849.json").read_text())
        self.assertEqual(declaration["limits"]["last_day"], script.s693.LAST_DAY.isoformat())
        self.assertEqual(declaration["issue"], 849)


if __name__ == "__main__":
    unittest.main()
