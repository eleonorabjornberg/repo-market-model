"""The drivers audit (`scripts/drivers_audit_951.py`, #951, H5 step 4 / H2): the parts that decide what is read and counted.

Recorded mutations (the two guards this script adds):

* `require_study_window`, the line `if late:` changed to `if False:`:
  `StudyWindowTests.test_a_day_after_the_study_end_is_refused` fails with `AssertionError` (`LookAheadError not raised`).
* `misaligned_columns`, the line `if pairing == ONE_STEP:` changed to `if False:`:
  `AlignmentTests.test_a_one_step_fit_trains_a_served_from_target_column_one_day_off` fails with `AssertionError` (`[] != ['quarter_end', 'tax_date']`).
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("drivers_audit_951_script", REPO / "scripts" / "drivers_audit_951.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model.splits import LookAheadError  # noqa: E402


class StudyWindowTests(unittest.TestCase):
    def test_a_day_after_the_study_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.require_study_window([date(2025, 12, 31), date(2026, 1, 2)])
        script.require_study_window([date(2025, 12, 30), date(2025, 12, 31)])


class AlignmentTests(unittest.TestCase):
    SERVED = frozenset({"quarter_end", "tax_date", "treasury_settlement"})

    def test_a_one_step_fit_trains_a_served_from_target_column_one_day_off(self):
        got = script.misaligned_columns(("tga", "quarter_end", "tax_date", "sofr_p25"), script.ONE_STEP, served_from_target=self.SERVED)
        self.assertEqual(got, ["quarter_end", "tax_date"])

    def test_a_direct_or_as_of_read_fit_is_aligned(self):
        for pairing in (script.DIRECT, script.AS_OF_READ):
            self.assertEqual(script.misaligned_columns(("quarter_end", "tax_date"), pairing, served_from_target=self.SERVED), [])

    def test_an_unknown_pairing_is_refused(self):
        with self.assertRaises(ValueError):
            script.misaligned_columns(("tga",), "two_step", served_from_target=self.SERVED)

    def test_the_served_from_target_set_is_the_calendar_and_the_scheduled_fields(self):
        sources = {
            "a": {"scheduled_availability": {"fields": ["f1", "f2"]}},
            "b": {},
            "c": {"scheduled_availability": {"fields": ["f3"]}},
        }
        got = script.served_from_target(sources, calendar=frozenset({"quarter_end"}))
        self.assertEqual(got, frozenset({"quarter_end", "f1", "f2", "f3"}))


class RareDayTests(unittest.TestCase):
    def test_counts_use_only_rows_public_at_the_anchor(self):
        flags = [False, True, False, True, True, False, True]
        self.assertEqual(script.count_in_window(flags, anchor=3), 2)
        self.assertEqual(script.count_in_window(flags, anchor=6), 4)

    def test_a_row_without_a_spread_is_not_a_training_row(self):
        flags = [True, True, True]
        spreads = [1.0, None, 2.0]
        self.assertEqual(script.count_in_window(flags, anchor=2, trainable=[s is not None for s in spreads]), 2)

    def test_a_group_can_be_split_off_alone_only_when_it_fills_a_leaf(self):
        self.assertFalse(script.can_split_alone(count=19, min_samples_leaf=20))
        self.assertTrue(script.can_split_alone(count=20, min_samples_leaf=20))
        self.assertTrue(script.can_split_alone(count=5, min_samples_leaf=5))

    def test_the_month_end_flag_is_zero_days_to_month_end(self):
        self.assertEqual(script.month_end_flags([0.0, 3.0, 0.0, None]), [True, False, True, False])


class SubsetTests(unittest.TestCase):
    def test_calendar_days_are_the_declared_kinds(self):
        self.assertEqual(
            script.calendar_subset({date(2024, 3, 29): "quarter_end", date(2024, 3, 28): "ordinary", date(2024, 4, 15): "tax_date"}),
            {date(2024, 3, 29), date(2024, 4, 15)},
        )

    def test_interval_width_is_the_span_of_the_interval(self):
        self.assertAlmostEqual(script.interval_width([-0.25, 0.75]), 1.0)
        self.assertIsNone(script.interval_width(None))


class DeclarationTests(unittest.TestCase):
    def test_every_arm_is_direct_and_the_leaves_include_one_that_can_split_rare_days(self):
        arms = script.ARMS
        self.assertTrue(all(arm["training_pairs"] == "direct" for arm in arms.values()))
        self.assertIn(5, {arm["min_samples_leaf"] for arm in arms.values()})
        self.assertIn(20, {arm["min_samples_leaf"] for arm in arms.values()})

    def test_the_key_comparison_names_declared_arms(self):
        for pair in script.KEY_COMPARISONS:
            for name in pair:
                self.assertIn(name, set(script.ARMS) | {script.CONTROL})

    def test_the_declared_calendar_inputs_are_served_from_the_target(self):
        served = script.served_from_target(script.load_sources(), calendar=script.contract_calendar())
        for column in script.CALENDAR_INPUTS:
            self.assertIn(column, served | {"net_settlement", "net_settlement_bills", "net_settlement_due_5d"})


class CommittedDeclarationTests(unittest.TestCase):
    def test_the_committed_declaration_is_what_declare_writes(self):
        import json

        committed = json.loads(script.DECLARATION.read_text(encoding="utf-8"))
        self.assertEqual(committed, json.loads(json.dumps(script.declaration_document())))

    def test_the_inventory_names_only_columns_rule_2_serves_from_the_target(self):
        import json

        served = script.served_from_target(script.load_sources(), script.contract_calendar())
        for fit in json.loads(script.AUDIT_INVENTORY.read_text(encoding="utf-8"))["fits"]:
            self.assertLessEqual(set(fit["calendar_and_scheduled_columns"]), served, fit["fit"])
            self.assertIn(fit["pairing"], script.PAIRINGS)


if __name__ == "__main__":
    unittest.main()
