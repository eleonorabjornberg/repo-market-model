"""(s3c-t): (s3c) with the cap off on turn days (#1265; H5 step 3, her ruling of 27 October 2026 on #1261 and #1264).

`repo_model.s3c_turn_cap` is (s3c) (`repo_model.s3c_candidate`) with one difference: on a target day whose reporting type is a turn
(`year_end`, `quarter_end_turn` or `turn`, the day types in force) the quantiles are not clipped at the facility line, so they are (s3)'s
element for element. On every other day it is (s3c), cap and all. The type is a function of the target date and the market holiday
table, like the calendar columns, so it is known at the decision instant. A label that is not one of the labels in force (the legacy
`month_end` and `quarter_end`, or anything else) is refused with `ValueError`, never read as "not a turn".

What these tests pin: the turn labels are exactly `turn_days.TURN_LABELS`; a turn day at full allotment is (s3)'s quantiles, a copy; a
non-turn day at full allotment is clipped at the line, as (s3c) clips it; a day before full allotment is (s3)'s whatever its type; the
real register and the real day types around the year end (26 December is not a turn, the last business day is `year_end`); the refusal of
an unknown label; the margin is (s3c)'s.

Recorded mutation (data guard, #1265): in `s3c_turn_cap.is_turn`, the `if day_type not in turn_days.LABELS: raise ValueError(...)`
check was deleted. `LabelTests.test_a_label_that_is_not_in_force_is_refused` then failed with `AssertionError` (`ValueError` not raised
for `month_end`); restored, it passes. Second mutation (the rule itself): `return day_type in turn_days.TURN_LABELS` was changed to
`day_type not in turn_days.TURN_LABELS`; `TurnDayTests.test_a_turn_day_at_full_allotment_is_s3_itself` then failed with `AssertionError`.
"""

from __future__ import annotations

import sys
import unittest
from datetime import date, datetime, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model import policy_events as pe, s3c_candidate, s3c_turn_cap as tc, turn_days  # noqa: E402

REGISTER = pe.load_register()
Q = [float(x) for x in range(-2, 21)]  # 23 ordered values from -2 to 20 bp; the line at full allotment is 10 bp above IORB or lower


def decision(day):
    return datetime.combine(day, time(16, 0))


class TurnDayTests(unittest.TestCase):

    def test_the_turn_labels_are_the_ones_in_force(self):
        self.assertEqual(tc.TURN_LABELS, turn_days.TURN_LABELS)
        self.assertEqual(tc.TURN_LABELS, {"year_end", "quarter_end_turn", "turn"})

    def test_a_turn_day_at_full_allotment_is_s3_itself(self):
        target = date(2025, 12, 31)
        self.assertIsNotNone(s3c_candidate.cap_line(REGISTER, decision(date(2025, 12, 30)), target))
        out = tc.capped_quantiles(Q, REGISTER, decision(date(2025, 12, 30)), target, "year_end")
        self.assertEqual(out, Q)
        self.assertIsNot(out, Q)

    def test_each_turn_label_is_uncapped(self):
        for label in ("year_end", "quarter_end_turn", "turn"):
            self.assertEqual(tc.capped_quantiles(Q, REGISTER, decision(date(2026, 3, 2)), date(2026, 3, 3), label), Q, label)

    def test_a_day_that_is_not_a_turn_at_full_allotment_is_capped_as_s3c_caps_it(self):
        target = date(2026, 3, 3)
        for label in ("tax_date", "ordinary"):
            out = tc.capped_quantiles(Q, REGISTER, decision(date(2026, 3, 2)), target, label)
            self.assertEqual(out, s3c_candidate.capped_quantiles(Q, REGISTER, decision(date(2026, 3, 2)), target))
            self.assertLess(max(out), max(Q))
            self.assertEqual(out, sorted(out))

    def test_before_full_allotment_it_is_s3_whatever_the_label(self):
        for label in turn_days.LABELS:
            self.assertEqual(tc.capped_quantiles(Q, REGISTER, decision(date(2025, 11, 25)), date(2025, 11, 26), label), Q, label)

    def test_the_real_day_types_of_late_december_2025_are_read_not_written(self):
        # 26 December is `ordinary` (its own flag, pooled as ordinary); the last business day is `year_end`.
        self.assertTrue(tc.is_turn(turn_days.turn_day_type(date(2025, 12, 31), tax_date=False)))
        self.assertFalse(tc.is_turn(turn_days.turn_day_type(date(2025, 12, 26), tax_date=False)))


class LabelTests(unittest.TestCase):

    def test_a_label_that_is_not_in_force_is_refused(self):
        for label in ("month_end", "quarter_end", "", "Year_End", "december_26"):
            with self.assertRaises(ValueError, msg=label):
                tc.capped_quantiles(Q, REGISTER, decision(date(2026, 3, 2)), date(2026, 3, 3), label)

    def test_the_margin_is_the_one_s3c_declared(self):
        self.assertEqual(tc.MARGIN_BP, s3c_candidate.MARGIN_BP)


if __name__ == "__main__":
    unittest.main()
