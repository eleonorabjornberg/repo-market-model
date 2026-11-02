"""`scripts/wednesday_candidate_check_1146.py` (#1146, Eleonora's ruling of 2 November 2026; H5 step 3, development tier).

Written before the script. The ruling asks, before an arm is scored, whether (s3c-ann-net)'s forecast reads `reserve_balances` (directly or
through the scarcity state) at each lead, and on how many decision days the Wednesday level changes what it reads. This check answers it by
walking the candidate on the published panel and on the same panel with `reserve_balances` replaced by the Wednesday level, on a panel whose
rows count every lookup of the reserve column, and by comparing every quantile of every cell. What these tests pin: the trap that counts
reads of a column, the rule that turns the counts into "can see" or "cannot see", the declaration's amendment (written before any figure),
and `check` and `page` end to end on the last months of the fixture panel.

Recorded mutation (the trap this script adds, `TrappedValues.__getitem__`; the mutated line and the exception the failing test raised):

* In `TrappedValues.__getitem__`, deleting the line `self._trap.lookups += 1` (the count of a read of the guarded column) makes
  `TrapTests.test_a_read_of_the_column_is_counted_only_while_armed` fail with `AssertionError: 0 != 1` (the read was made while armed and
  nothing counted it), and `ReadsTests.test_a_model_that_reads_the_column_is_seen_to_read_it` fail with `AssertionError: False is not true`;
  restored, both pass.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model.data import DailyObservation

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("wednesday_candidate_check_1146", ROOT / "scripts" / "wednesday_candidate_check_1146.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["wednesday_candidate_check_1146"] = script
_spec.loader.exec_module(script)


def rows(n=4, start=date(2024, 1, 1)):
    return [
        DailyObservation(start + timedelta(days=i), {"sofr": 5.3, "iorb": 5.4, "reserve_balances": 3000.0 + i, "tga": 700.0 + i})
        for i in range(n)
    ]


class TrapTests(unittest.TestCase):

    def test_a_read_of_the_column_is_counted_only_while_armed(self):
        panel, trap = script.trapped_panel(rows())
        _ = panel[0].values["reserve_balances"]
        self.assertEqual(trap.lookups, 0)
        with trap.armed():
            _ = panel[0].values["reserve_balances"]
        self.assertEqual(trap.lookups, 1)
        _ = panel[1].values["reserve_balances"]
        self.assertEqual(trap.lookups, 1)

    def test_get_and_membership_count_as_reads_and_other_columns_do_not(self):
        panel, trap = script.trapped_panel(rows())
        with trap.armed():
            panel[0].values.get("reserve_balances")
            self.assertIn("reserve_balances", panel[1].values)
            panel[2].values["tga"]
            panel[2].values.get("sofr")
        self.assertEqual(trap.lookups, 2)
        self.assertEqual(trap.bulk, 0)

    def test_a_bulk_read_is_counted_apart_and_the_values_are_the_rows_own(self):
        original = rows()
        panel, trap = script.trapped_panel(original)
        with trap.armed():
            list(panel[0].values.items())
            list(panel[0].values)
        self.assertEqual(trap.lookups, 0)
        self.assertGreaterEqual(trap.bulk, 2)
        self.assertEqual([dict(r.values) for r in panel], [dict(r.values) for r in original])
        self.assertEqual([r.date for r in panel], [r.date for r in original])


class ReadsTests(unittest.TestCase):

    def test_a_model_that_reads_the_column_is_seen_to_read_it(self):
        panel, trap = script.trapped_panel(rows())
        with trap.armed():
            total = sum(r.values["reserve_balances"] for r in panel)
        self.assertGreater(total, 0)
        self.assertTrue(trap.lookups > 0)

    def test_a_model_that_reads_the_spread_alone_is_seen_not_to(self):
        panel, trap = script.trapped_panel(rows())
        with trap.armed():
            total = sum(r.values["sofr"] - r.values["iorb"] for r in panel)
        self.assertLess(total, 0)
        self.assertEqual(trap.lookups, 0)


class DecideTests(unittest.TestCase):

    def test_no_read_identical_forecasts_and_a_constant_state_is_cannot_see(self):
        self.assertEqual(script.decide(lookups=0, identical=10, cells=10, state_values=[1.0]), "cannot_see")

    def test_any_read_a_moved_cell_or_a_varying_state_is_can_see(self):
        self.assertEqual(script.decide(lookups=1, identical=10, cells=10, state_values=[1.0]), "can_see")
        self.assertEqual(script.decide(lookups=0, identical=9, cells=10, state_values=[1.0]), "can_see")
        self.assertEqual(script.decide(lookups=0, identical=10, cells=10, state_values=[0.0, 1.0]), "can_see")

    def test_no_cell_at_all_is_a_data_error(self):
        with self.assertRaises(ValueError):
            script.decide(lookups=0, identical=0, cells=0, state_values=[1.0])


class DeclarationTests(unittest.TestCase):

    def test_the_amendment_is_in_the_committed_declaration_and_declares_the_check_before_any_arm(self):
        declaration = script.w1146.committed_declaration()
        amendments = declaration["amendments"]
        entry = [a for a in amendments if a["ruling"].startswith("Eleonora, 2 November 2026")]
        self.assertEqual(len(entry), 1)
        entry = entry[0]
        self.assertEqual(entry["candidate"], "sc_s3c_ann_net")
        self.assertEqual(entry["instant"], "18:00")
        self.assertIn("arm_added_only_if", entry)
        self.assertIn("scored_before_this_amendment", entry)
        self.assertFalse(entry["scored_before_this_amendment"])
        self.assertEqual(declaration["limits"]["last_day"], "2025-12-31")


class EndToEndTests(unittest.TestCase):
    """`check` and `page` on the last months of the fixture panel: the shape, and the candidate's answer."""

    FIRST = "2025-09-02"

    @classmethod
    def setUpClass(cls):
        import panel_cache

        cls.panel_path = Path(panel_cache.published_build()["path"])
        cls.tmp = tempfile.TemporaryDirectory()
        base = Path(cls.tmp.name)
        cls.output, cls.page = base / "result.json", base / "page.md"
        script.main(["check", "--panel", str(cls.panel_path), "--first", cls.FIRST, "--output", str(cls.output)])
        script.main(["page", "--check", str(cls.output), "--output", str(cls.page)])
        cls.result = json.loads(cls.output.read_text(encoding="utf-8"))
        cls.text = cls.page.read_text(encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_the_candidate_never_looks_up_the_reserve_column_on_either_panel(self):
        for reading in ("week_average", "wednesday_level"):
            self.assertEqual(self.result["candidate"][reading]["lookups"], 0)

    def test_the_forecasts_are_identical_cell_for_cell_and_the_state_the_candidate_reads_is_one_value(self):
        same = self.result["candidate"]["compared"]
        self.assertGreater(same["cells"], 0)
        self.assertEqual(same["identical"], same["cells"])
        self.assertEqual(same["max_abs_difference"], 0.0)
        self.assertEqual(self.result["candidate"]["state_values_read"], [1.0])
        self.assertEqual(self.result["answer"], "cannot_see")

    def test_the_control_that_does_read_the_state_moves_where_the_states_differ(self):
        control = self.result["control"]
        self.assertGreater(control["cells"], 0)
        self.assertEqual(control["compared"]["cells"], control["cells"])

    def test_the_states_differ_on_a_counted_number_of_decision_days_at_each_lead(self):
        for h in ("1", "2", "3", "4", "5"):
            self.assertIn(h, self.result["decision_days_state_differs"])

    def test_no_day_after_the_last_scored_day_is_read(self):
        self.assertLessEqual(self.result["notes"]["last_target"], script.LAST_DAY.isoformat())
        self.assertEqual(self.result["subset_from"], self.FIRST)

    def test_the_page_says_it_stops_there_and_ends_with_the_marked_question(self):
        text = self.text
        self.assertIn("development data, not a verdict", text.lower())
        self.assertIn("No arm is scored", text)
        tail = text[text.index("## Question for Eleonora"):]
        self.assertEqual(text.count("## Question for Eleonora"), 1)
        for option in ("1. **", "2. **"):
            self.assertIn(option, tail)
        self.assertIn("(default)", tail)


if __name__ == "__main__":
    unittest.main()
