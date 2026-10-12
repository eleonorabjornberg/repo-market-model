"""What separates the every-day part's onset warnings from its false alarms (#601, step 1): the declaration, the readers and the interval.

Recorded mutations, 12 October 2026, in a disposable copy of `scripts/every_day_separation_601.py`:
1. in `change_over`, the guard call `_read_up_to(position, limit)` deleted (a change may now be formed at a row after the decision's anchor).
   `test_a_change_is_never_formed_at_a_row_after_the_anchor` then fails with `AssertionError: LookAheadError not raised`.
2. in `change_over`, the line `_read_up_to(position, limit)` kept but `limit` replaced by `len(values)` at the call (the guard compares against the
   whole series, not the anchor). The same test fails with `AssertionError: LookAheadError not raised`.
3. in `rows_to_next_risk_date`, the guard call `_calendar_columns_only(columns)` deleted (a count that reads a column that is not a calendar
   column). `test_the_days_to_the_next_risk_date_read_calendar_columns_only` then fails with `AssertionError: LookAheadError not raised`.
4. in `rows_to_next_risk_date`, the loop start `decision + 1` replaced by `decision` (a decision day that is itself a risk date counts as 0 rows away,
   a day that has already been served). `test_the_count_starts_after_the_decision_row` then fails with `AssertionError: 0 != 3`.
"""

import importlib.util
import json
import random
import sys
import unittest
from pathlib import Path

from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
DECLARED = json.loads((ROOT / "metadata" / "every_day_separation_601.json").read_text())


def _script():
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("every_day_separation_601_script", ROOT / "scripts" / "every_day_separation_601.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["every_day_separation_601_script"] = module
    spec.loader.exec_module(module)
    return module


SCRIPT = _script()


class DeclarationTests(unittest.TestCase):
    def test_the_declaration_is_what_the_script_declares(self):
        self.assertEqual(SCRIPT.declaration_document(), DECLARED)

    def test_every_input_is_named_by_the_directive(self):
        self.assertEqual(
            set(DECLARED["input_families"]),
            {"tail_spread", "satiation_distance", "reserve_trend", "days_to_risk_date", "tga_path", "percentile_dispersion"},
        )
        for family, names in DECLARED["input_families"].items():
            for name in names:
                self.assertIn(name, DECLARED["inputs"])

    def test_the_tail_spread_change_is_read_over_1_5_and_10_market_days(self):
        self.assertEqual(
            [name for name in DECLARED["inputs"] if name.startswith("tail_spread_change")],
            ["tail_spread_change_1", "tail_spread_change_5", "tail_spread_change_10"],
        )

    def test_the_scoring_ends_before_the_lockbox_and_nothing_is_published(self):
        self.assertLess(DECLARED["scoring"]["last_day"], "2026-01-01")
        self.assertIn("nothing", DECLARED["published"])

    def test_the_interval_is_the_judges(self):
        judge = json.loads((ROOT / "metadata" / "pressure_judge.json").read_text())["bootstrap"]
        self.assertEqual(DECLARED["bootstrap"]["level"], judge["level"])
        self.assertEqual(DECLARED["bootstrap"]["block_length"], judge["block_length"])
        self.assertEqual(DECLARED["bootstrap"]["replications"], judge["replications"])


class ReadTests(unittest.TestCase):
    def test_the_latest_public_row_is_the_last_one_that_is_not_a_hole(self):
        self.assertEqual(SCRIPT.latest_public([1.0, 2.0, None, None]), 1)
        self.assertEqual(SCRIPT.latest_public([None, None]), None)

    def test_a_change_is_the_latest_public_value_less_the_value_k_rows_earlier(self):
        values = [1.0, 2.0, 4.0, 7.0, None]
        self.assertEqual(SCRIPT.change_over(values, 1, limit=4), 3.0)
        self.assertEqual(SCRIPT.change_over(values, 3, limit=4), 6.0)

    def test_a_change_is_a_hole_when_either_end_is_one(self):
        self.assertIsNone(SCRIPT.change_over([None, 2.0, 4.0], 2, limit=2))
        self.assertIsNone(SCRIPT.change_over([1.0, 2.0], 5, limit=1))

    def test_a_change_is_never_formed_at_a_row_after_the_anchor(self):
        values = [1.0, 2.0, 4.0, 7.0]
        with self.assertRaises(LookAheadError):
            SCRIPT.change_over(values, 1, limit=2)
        self.assertEqual(SCRIPT.change_over(values, 1, limit=3), 3.0)

    def test_the_days_to_the_next_risk_date_read_calendar_columns_only(self):
        with self.assertRaises(LookAheadError):
            SCRIPT.rows_to_next_risk_date(["ordinary", "month_end"], 0, columns=("quarter_end", "treasury_settlement_coupons"))
        self.assertEqual(SCRIPT.rows_to_next_risk_date(["ordinary", "month_end"], 0, columns=SCRIPT.CALENDAR_COLUMNS), 1)

    def test_the_count_starts_after_the_decision_row(self):
        types = ["month_end", "ordinary", "ordinary", "tax_date"]
        self.assertEqual(SCRIPT.rows_to_next_risk_date(types, 0, columns=SCRIPT.CALENDAR_COLUMNS), 3)
        self.assertEqual(SCRIPT.rows_to_next_risk_date(types, 1, columns=SCRIPT.CALENDAR_COLUMNS), 2)

    def test_no_later_risk_date_on_the_panel_is_a_hole(self):
        self.assertIsNone(SCRIPT.rows_to_next_risk_date(["ordinary", "ordinary"], 0, columns=SCRIPT.CALENDAR_COLUMNS))

    def test_dispersion_is_the_gap_between_the_extreme_percentiles(self):
        self.assertEqual(SCRIPT.dispersion(5.0, 2.5), 2.5)
        self.assertIsNone(SCRIPT.dispersion(None, 2.5))


class SeparationTests(unittest.TestCase):
    def test_a_perfectly_separating_input_has_auroc_one_and_a_reversed_one_zero(self):
        out = SCRIPT.separation([5.0, 6.0], [1.0, 2.0, 3.0, 4.0], seed=1, replications=50, block_length=3, level=0.9)
        self.assertEqual(out["auroc"], 1.0)
        out = SCRIPT.separation([0.0], [1.0, 2.0], seed=1, replications=50, block_length=3, level=0.9)
        self.assertEqual(out["auroc"], 0.0)

    def test_an_uninformative_input_has_auroc_one_half(self):
        out = SCRIPT.separation([1.0, 2.0], [1.0, 2.0], seed=1, replications=50, block_length=1, level=0.9)
        self.assertEqual(out["auroc"], 0.5)

    def test_the_interval_is_reproducible_and_contains_the_estimate_for_a_clear_case(self):
        a = SCRIPT.separation([4.0, 5.0, 6.0, 7.0], [float(x) for x in range(1, 40)], seed=7, replications=200, block_length=5, level=0.9)
        b = SCRIPT.separation([4.0, 5.0, 6.0, 7.0], [float(x) for x in range(1, 40)], seed=7, replications=200, block_length=5, level=0.9)
        self.assertEqual(a, b)
        self.assertLessEqual(a["interval"][0], a["auroc"])
        self.assertGreaterEqual(a["interval"][1], a["auroc"])

    def test_two_groups_are_resampled_apart_and_never_pooled(self):
        rng = random.Random(3)
        onset, alarm = SCRIPT.resample_groups(2, 9, block_length=4, rng=rng)
        self.assertEqual(len(onset), 2)
        self.assertEqual(len(alarm), 9)
        self.assertTrue(all(0 <= i < 2 for i in onset))
        self.assertTrue(all(0 <= i < 9 for i in alarm))

    def test_a_group_with_no_values_is_reported_as_undefined_not_as_one_half(self):
        out = SCRIPT.separation([], [1.0, 2.0], seed=1, replications=10, block_length=3, level=0.9)
        self.assertIsNone(out["auroc"])
        self.assertIsNone(out["interval"])

    def test_holes_are_dropped_and_counted(self):
        out = SCRIPT.separation([5.0, None], [1.0, None, 2.0], seed=1, replications=20, block_length=2, level=0.9)
        self.assertEqual((out["onset_n"], out["alarm_n"]), (1, 2))
        self.assertEqual((out["onset_holes"], out["alarm_holes"]), (1, 1))

    def test_an_interval_that_excludes_one_half_is_called_a_separation(self):
        self.assertTrue(SCRIPT.separates({"interval": (0.6, 0.9)}))
        self.assertTrue(SCRIPT.separates({"interval": (0.1, 0.4)}))
        self.assertFalse(SCRIPT.separates({"interval": (0.3, 0.8)}))
        self.assertFalse(SCRIPT.separates({"interval": None}))


class MinimumTests(unittest.TestCase):
    def test_a_cell_with_fewer_than_the_declared_minimum_of_onset_warnings_never_separates(self):
        self.assertEqual(DECLARED["minimum_onset_warnings"], SCRIPT.MINIMUM_ONSET_WARNINGS)
        few = {"interval": (0.01, 0.07), "onset_n": SCRIPT.MINIMUM_ONSET_WARNINGS - 1}
        enough = {"interval": (0.01, 0.07), "onset_n": SCRIPT.MINIMUM_ONSET_WARNINGS}
        self.assertFalse(SCRIPT.separates(few))
        self.assertTrue(SCRIPT.separates(enough))

    def test_an_input_triggers_step_2_only_if_it_separates_in_both_looks_in_the_same_direction(self):
        pooled = {
            "a": {"interval": (0.1, 0.4), "onset_n": 5},
            "b": {"interval": (0.1, 0.4), "onset_n": 5},
            "c": {"interval": (0.6, 0.9), "onset_n": 5},
            "d": {"interval": (0.6, 0.9), "onset_n": 5},
        }
        same = {
            "a": {"interval": (0.1, 0.45), "onset_n": 5},
            "b": {"interval": (0.2, 0.6), "onset_n": 5},
            "c": {"interval": (0.1, 0.4), "onset_n": 5},
            "d": {"interval": (0.55, 0.8), "onset_n": 5},
        }
        self.assertEqual(SCRIPT.triggering_inputs(pooled, same), {"a": "lower", "d": "higher"})


class UnitTests(unittest.TestCase):
    def test_an_every_day_flag_is_a_flag_at_a_lead_where_the_day_is_not_a_risk_date(self):
        self.assertEqual(SCRIPT.every_day_leads([1, 2, 5], [2]), [1, 5])
        self.assertEqual(SCRIPT.every_day_leads([2], [2]), [])

    def test_the_decision_lead_of_a_day_is_the_farthest_lead_that_flags_it(self):
        self.assertEqual(SCRIPT.decision_lead([1, 3, 5]), 5)

    def test_units_are_split_into_onset_warnings_and_false_alarms_and_the_rest_is_counted(self):
        days = [
            {"date": "2019-01-01", "onset": True, "pressure_day": True, "flagged_at": [1], "risk_date_at": []},
            {"date": "2019-01-02", "onset": False, "pressure_day": False, "flagged_at": [2], "risk_date_at": []},
            {"date": "2019-01-03", "onset": False, "pressure_day": True, "flagged_at": [2], "risk_date_at": []},
            {"date": "2019-01-04", "onset": False, "pressure_day": False, "flagged_at": [2], "risk_date_at": [2]},
            {"date": "2019-01-05", "onset": True, "pressure_day": True, "flagged_at": [2], "risk_date_at": [2]},
            {"date": "2019-01-06", "onset": False, "pressure_day": False, "flagged_at": [], "risk_date_at": []},
        ]
        out = SCRIPT.split_units(days)
        self.assertEqual([u["date"] for u in out["onset_warnings"]], ["2019-01-01"])
        self.assertEqual([u["date"] for u in out["false_alarms"]], ["2019-01-02"])
        self.assertEqual(out["flagged_pressure_days_not_onsets"], 1)
        self.assertEqual(out["onsets_warned_by_the_risk_date_part_only"], 1)
        self.assertEqual(out["risk_date_false_alarms"], 1)


if __name__ == "__main__":
    unittest.main()
