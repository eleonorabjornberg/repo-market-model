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
    def test_every_arm_is_direct_but_the_ruled_one_step_arm_and_the_leaves_include_one_that_can_split_rare_days(self):
        arms = script.ARMS
        self.assertEqual({name for name, arm in arms.items() if arm["training_pairs"] != "direct"}, {"onestep_cal_leaf20"})
        self.assertIn(5, {arm["min_samples_leaf"] for arm in arms.values()})
        self.assertIn(20, {arm["min_samples_leaf"] for arm in arms.values()})

    def test_the_ruled_one_step_arm_is_direct_cal_leaf20_trained_on_one_step_pairs(self):
        """The amendment of Eleonora's ruling of 19 October 2026 on #951: otherwise identical to `direct_cal_leaf20`."""

        arms = script.ARMS
        self.assertEqual(arms["onestep_cal_leaf20"], {**arms["direct_cal_leaf20"], "training_pairs": script.ONE_STEP})
        self.assertEqual(script.arm_features("onestep_cal_leaf20", 1), script.arm_features("direct_cal_leaf20", 1))
        for pair in (("gbm_funding", "onestep_cal_leaf20"), ("onestep_cal_leaf20", "direct_cal_leaf20")):
            self.assertIn(pair, script.KEY_COMPARISONS)

    def test_a_one_step_arm_fits_with_training_pairs_unset(self):
        self.assertIsNone(script.arm_fit("onestep_cal_leaf20", ("on_rrp",)).keywords["training_pairs"])
        self.assertEqual(script.arm_fit("direct_cal_leaf20", ("on_rrp",)).keywords["training_pairs"], "direct")

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


class StudentizedReadingTests(unittest.TestCase):
    """#1017: verdicts read the studentized one-sided bound on mean d (ruling 1), not the percentile interval of the skill."""

    @staticmethod
    def row(interval, lower):
        return {"skill": 0.05, "skill_interval_90": interval, "mean_difference": 0.1, "mean_difference_lower_95_one_sided": lower}

    def test_the_studentized_reading_follows_the_bound_not_the_percentile_interval(self):
        row = self.row([0.01, 0.09], -0.02)
        self.assertEqual(script.percentile_side(row), "gain")
        self.assertEqual(script.studentized_side(row), "not seen")

    def test_a_positive_bound_is_a_gain_whatever_the_percentile_interval_says(self):
        row = self.row([-0.01, 0.09], 0.03)
        self.assertEqual(script.percentile_side(row), "not seen")
        self.assertEqual(script.studentized_side(row), "gain")

    def test_a_bound_of_exactly_zero_is_not_a_gain(self):
        self.assertEqual(script.studentized_side(self.row([0.01, 0.09], 0.0)), "not seen")

    def test_the_percentile_reading_has_a_harm_side_the_one_sided_bound_cannot_confirm(self):
        row = self.row([-0.09, -0.01], -0.2)
        self.assertEqual(script.percentile_side(row), "harm")
        self.assertEqual(script.studentized_side(row), "not seen")

    def test_rows_whose_side_changes_are_listed_from_the_scored_document(self):
        document = {"tables": {"pooled": {"all": {"n": 10, "tests": {
            "B1 -> a": self.row([0.01, 0.09], -0.02),
            "B1 -> b": self.row([0.01, 0.09], 0.02),
            "B1 -> c": self.row([-0.01, 0.09], 0.03),
        }}, "thin": {"n": 3}}}}
        got = script.side_changes(document)
        self.assertEqual([(g["label"], g["pair"], g["percentile"], g["studentized"]) for g in got],
                         [("all", "B1 -> a", "gain", "not seen"), ("all", "B1 -> c", "not seen", "gain")])

    def test_a_missing_bound_is_refused(self):
        with self.assertRaises(ValueError):
            script.studentized_side({"skill_interval_90": [0.0, 1.0]})


if __name__ == "__main__":
    unittest.main()
