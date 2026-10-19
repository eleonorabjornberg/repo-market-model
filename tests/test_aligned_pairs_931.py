"""The aligned-pairs arm (`scripts/aligned_pairs_931.py`, #931): what the arm trains `treasury_settlement` from, and what serving reads.

Recorded mutations:

* `require_study_window`, the line `if late:` changed to `if False:`:
  `StudyWindowTests.test_a_day_after_the_study_end_is_refused` fails with `AssertionError` (`LookAheadError not raised`).
* `align_field`, the line `values[field] = rows[position + 1].values.get(field)` changed to `rows[position].values.get(field)`
  (the one-step read, the very defect under test): `AlignTests.test_row_p_trains_the_value_of_the_target_row` fails with `AssertionError`.
"""

from __future__ import annotations

import importlib.util
import inspect
import json
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("aligned_pairs_931_script", REPO / "scripts" / "aligned_pairs_931.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model.asof import InformationRule  # noqa: E402
from repo_model.data import DailyObservation  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402


class StudyWindowTests(unittest.TestCase):
    def test_a_day_after_the_study_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.require_study_window([date(2025, 12, 31), date(2026, 1, 2)])
        script.require_study_window([date(2025, 12, 30), date(2025, 12, 31)])


def frame(settlements):
    return [
        DailyObservation(date=date(2024, 1, 1 + i), values={"treasury_settlement": s, "tga": 100.0 + i, "sofr_p25": 5.0})
        for i, s in enumerate(settlements)
    ]


class AlignTests(unittest.TestCase):
    def test_row_p_trains_the_value_of_the_target_row(self):
        original = frame([10.0, 20.0, 30.0, 40.0])
        aligned = script.align_field(original)
        # the one-step pair (p, p + 1) takes row p's features: the field it carries is the target's (row p + 1)
        for p in range(3):
            self.assertEqual(aligned[p].values["treasury_settlement"], original[p + 1].values["treasury_settlement"])

    def test_nothing_else_moves(self):
        original = frame([10.0, 20.0, 30.0])
        aligned = script.align_field(original)
        self.assertEqual([r.date for r in aligned], [r.date for r in original])
        for before, after in zip(original, aligned):
            for name in ("tga", "sofr_p25"):
                self.assertEqual(before.values[name], after.values[name])

    def test_the_last_row_has_no_successor_and_is_a_hole_not_a_value_of_the_wrong_day(self):
        aligned = script.align_field(frame([10.0, 20.0, 30.0]))
        self.assertIsNone(aligned[-1].values["treasury_settlement"])

    def test_the_input_frame_is_not_changed(self):
        original = frame([10.0, 20.0, 30.0])
        script.align_field(original)
        self.assertEqual([r.values["treasury_settlement"] for r in original], [10.0, 20.0, 30.0])

    def test_trained_row_is_the_target_row_when_aligned_and_the_origin_row_otherwise(self):
        days = [date(2024, 1, d) for d in (1, 2, 3, 4)]
        self.assertEqual(script.trained_row(days, 1, aligned=False), days[1])
        self.assertEqual(script.trained_row(days, 1, aligned=True), days[2])


class ServingTests(unittest.TestCase):
    def test_serving_reads_the_field_from_the_targets_own_row_at_lead_1(self):
        registry = json.loads(script.SOURCES.read_text(encoding="utf-8"))
        features = ("treasury_settlement", "tga", "spread_bps")
        days = [date(2019, 9, 16) + timedelta(days=i) for i in range(0, 40)]
        days = [d for d in days if d.weekday() < 5]
        rule = InformationRule(registry, features, decision_time=script._load("spread_distribution_634").DECISION, horizon=1)
        target = days.index(date(2019, 9, 30))
        self.assertEqual(script.served_row(rule, days, target), date(2019, 9, 30))
        # and the aligned arm trains the pair whose target is that row from that same row; the one-step pair does not
        self.assertEqual(script.trained_row(days, target - 1, aligned=True), date(2019, 9, 30))
        self.assertNotEqual(script.trained_row(days, target - 1, aligned=False), date(2019, 9, 30))


class ArmTests(unittest.TestCase):
    def test_the_target_is_not_its_own_regressor(self):
        self.assertEqual(script.regressors(("a", "treasury_settlement", "spread_bps")), ("a", "treasury_settlement"))

    def test_the_fit_does_not_name_information_so_the_pairs_stay_one_step(self):
        fit = script.aligned_fit(("treasury_settlement", "spread_bps"))
        self.assertNotIn("information", inspect.signature(fit).parameters)

    def test_an_arm_without_the_field_is_refused(self):
        with self.assertRaises(ValueError):
            script.aligned_fit(("tga", "spread_bps"))


class SplitTests(unittest.TestCase):
    def test_a_coupon_settlement_on_an_ordinary_day_is_a_mid_month_coupon_date(self):
        self.assertEqual(script.day_type("ordinary", {"treasury_settlement_coupons": 60.0}), "mid_month_coupon")
        self.assertEqual(script.day_type("ordinary", {"treasury_settlement_coupons": 0.0}), "ordinary")
        self.assertEqual(script.day_type("ordinary", {}), "ordinary")
        self.assertEqual(script.day_type("month_end", {"treasury_settlement_coupons": 60.0}), "month_end")


class DeclarationTests(unittest.TestCase):
    def test_the_declaration_names_the_arm_and_the_ruled_exclusion(self):
        document = json.loads(script.DECLARATION.read_text(encoding="utf-8"))
        self.assertEqual(document["issue"], 931)
        self.assertEqual(set(document["arms"]), {"gbm_funding_aligned"})
        self.assertIn("2019-09-18", json.dumps(document["locate"]))
        self.assertEqual(script.EXCLUDED_DAY, date(2019, 9, 18))


if __name__ == "__main__":
    unittest.main()
