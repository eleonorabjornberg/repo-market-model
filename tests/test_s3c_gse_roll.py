"""(s3c-gse-roll): the GSE ramp with the payment-day roll when the 25th is not a business day (#1287; H5 step 3, development tier).

`repo_model.s3c_gse_roll` is `s3c_gse` with one rule added: the 25th's value (7/7) is read on the payment day, the first business day on or
after the 25th (`data.market_holidays()` and weekends), and the 25th itself reads nothing when it is not a business day. Every other day of the
ramp keeps its own date's value. What these tests pin: the payment day on hand months (a weekday 25th, a Saturday, a Sunday, Christmas on a
weekday, a Friday holiday over a long weekend, a Monday holiday); the roll on hand dates (the value on the payment day is 1 and the day before
keeps its own); that the roll equals the unrolled ramp on every month whose 25th is a business day; that the term table holds the roll in the
slot of `dom_19_23` at every lead, read from the target row, with every other term the base table's; that a one-step fit is refused; and the
count of target days the roll moves.

Recorded mutations (each applied to the tree, the named test run, and reverted):

* `payment_day`: `data.next_business_day(date(year, month, LAST_DAY) - timedelta(days=1), 1)` replaced with `date(year, month, LAST_DAY)`, so the
  payment day is always the calendar 25th and the roll does nothing. `PaymentDayTests.test_the_payment_day_on_hand_months` failed with
  `AssertionError` (2025-10-27 expected for the Saturday 25th, 2025-10-25 returned).
* `RollTermTable.__init__`: `column = [roll_ramp(day) for day in self.dates]` replaced with `[roll_ramp(self.dates[max(i - 1, 0)]) ...]`, so each
  row carries the term of the row before it (the #914 class: a calendar column served one row off).
  `TableTests.test_the_roll_is_read_from_the_target_row_at_every_lead` failed with `AssertionError`.
"""

from __future__ import annotations

import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import announced_iorb, data
from repo_model import one_step_guard as osg
from repo_model import s3c_gse as gse
from repo_model import s3c_gse_roll as roll
from repo_model import spread_mr_calendar as cal
from repo_model import spread_mr_state_calendar as sc
from repo_model.scoring_protocol import HORIZONS

import test_protocol_benchmarks as tpb

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / "tests" / "fixtures" / "snapshots" / "fed-iorb-announcements" / "iorb_changes.csv"
PANEL = tpb.published_panel()["rows"]
ANNOUNCEMENTS = announced_iorb.load_announcements(TABLE)
BASE = cal.TermTable(PANEL, ANNOUNCEMENTS)
ROLL = roll.RollTermTable(PANEL, ANNOUNCEMENTS)
SETTINGS = dict(registry=tpb.REGISTRY, decision_time=tpb.DECISION, splits=tpb.SPLITS)
DATES = [row.date for row in PANEL]


def business(day: date) -> bool:
    return day.weekday() < 5 and day not in data.market_holidays().closed


class PaymentDayTests(unittest.TestCase):

    def test_the_payment_day_on_hand_months(self):
        cases = {
            (2025, 3): date(2025, 3, 25),    # a Tuesday
            (2025, 10): date(2025, 10, 27),  # the 25th is a Saturday
            (2026, 1): date(2026, 1, 26),    # the 25th is a Sunday
            (2025, 12): date(2025, 12, 26),  # Christmas on a Thursday: the Friday is a business day
            (2024, 12): date(2024, 12, 26),  # Christmas on a Wednesday
            (2023, 12): date(2023, 12, 26),  # Christmas on a Monday
            (2021, 12): date(2021, 12, 27),  # the 25th is a Saturday
            (2022, 12): date(2022, 12, 27),  # the 25th is a Sunday and the 26th is the observed holiday
        }
        for (year, month), expected in cases.items():
            self.assertEqual(roll.payment_day(year, month), expected, (year, month))

    def test_the_payment_day_is_a_business_day_on_or_after_the_25th_and_within_four_days(self):
        for year in range(2018, 2027):
            for month in range(1, 13):
                p = roll.payment_day(year, month)
                self.assertTrue(business(p), p)
                self.assertTrue(date(year, month, 25) <= p <= date(year, month, 25) + timedelta(days=4), p)
                self.assertTrue(all(not business(date(year, month, 25) + timedelta(days=i)) for i in range((p - date(year, month, 25)).days)))

    def test_the_declared_shape(self):
        self.assertEqual((roll.FIRST_DAY, roll.LAST_DAY, roll.REPLACED_TERM), (19, 25, "dom_19_23"))
        self.assertEqual((roll.FIRST_DAY, roll.LAST_DAY, roll.REPLACED_TERM), (gse.FIRST_DAY, gse.LAST_DAY, gse.REPLACED_TERM))


class RollRampTests(unittest.TestCase):

    def test_the_value_of_the_payment_day_is_one_and_the_25th_that_is_not_a_business_day_reads_nothing(self):
        # October 2025: the 25th is a Saturday, the payment day Monday the 27th
        self.assertEqual(roll.roll_ramp(date(2025, 10, 27)), 1.0)
        self.assertAlmostEqual(roll.roll_ramp(date(2025, 10, 24)), 6 / 7)  # the Friday keeps its own value
        self.assertEqual(roll.roll_ramp(date(2025, 10, 28)), 0.0)
        # December 2025: Christmas is a Thursday and the payment day Friday the 26th
        self.assertEqual(roll.roll_ramp(date(2025, 12, 26)), 1.0)
        self.assertAlmostEqual(roll.roll_ramp(date(2025, 12, 24)), 6 / 7)
        self.assertEqual(roll.roll_ramp(date(2025, 12, 29)), 0.0)
        # January 2026: Sunday 25th, Monday 26th
        self.assertEqual(roll.roll_ramp(date(2026, 1, 26)), 1.0)
        self.assertAlmostEqual(roll.roll_ramp(date(2026, 1, 23)), 5 / 7)

    def test_a_month_whose_25th_is_a_business_day_reads_the_unrolled_ramp(self):
        for day in (date(2025, 3, 18), date(2025, 3, 19), date(2025, 3, 22), date(2025, 3, 24), date(2025, 3, 25), date(2025, 3, 26), date(2025, 3, 31)):
            self.assertAlmostEqual(roll.roll_ramp(day), gse.ramp(day), msg=str(day))

    def test_the_roll_differs_from_the_ramp_only_on_the_25th_and_the_payment_day(self):
        for year in (2024, 2025, 2026):
            for month in range(1, 13):
                p = roll.payment_day(year, month)
                for d in range(1, 29):
                    day = date(year, month, d)
                    if not business(day):
                        continue
                    if p.day != 25 and day == p:
                        self.assertEqual((gse.ramp(day), roll.roll_ramp(day)), (0.0, 1.0), day)
                    else:
                        self.assertEqual(roll.roll_ramp(day), gse.ramp(day), day)

    def test_days_before_the_19th_and_after_the_payment_day_read_zero(self):
        for day in (date(2025, 10, 18), date(2025, 10, 1), date(2025, 10, 28), date(2025, 10, 31)):
            self.assertEqual(roll.roll_ramp(day), 0.0)

    def test_a_weekend_day_has_no_row_and_the_function_is_not_asked_for_it_by_the_table(self):
        self.assertTrue(all(business(d) for d in DATES))

    def test_the_count_of_months_and_target_days_the_roll_moves(self):
        months = [(y, m) for y in range(2018, 2027) for m in range(1, 13) if date(2018, 7, 1) <= date(y, m, 1) <= date(2026, 8, 1)]
        moved = [(y, m) for y, m in months if roll.payment_day(y, m).day != 25]
        self.assertEqual((len(months), len(moved)), (98, 37))  # the count of #1285
        # the days the roll moves in the panel: each of those months loses the 25th's row (none) and gains 1 on the payment day
        in_panel = [d for d in DATES if gse.ramp(d) != roll.roll_ramp(d)]
        self.assertTrue(all(d.day in (26, 27, 28) for d in in_panel))
        self.assertEqual(roll.moved_days(DATES), in_panel)


class TableTests(unittest.TestCase):

    def test_the_roll_is_read_from_the_target_row_at_every_lead(self):
        for lead in HORIZONS:
            for di in range(40, len(PANEL) - 6, 7):
                self.assertEqual(ROLL.read(lead, di)["dom_19_23"], roll.roll_ramp(DATES[di + lead]), (lead, DATES[di]))

    def test_the_roll_is_the_same_at_every_lead(self):
        for row in range(len(PANEL)):
            self.assertEqual({ROLL.flag("dom_19_23", lead, row) for lead in HORIZONS}, {roll.roll_ramp(DATES[row])})

    def test_every_other_term_is_the_base_tables_at_every_lead_and_row(self):
        for term in cal.TERMS:
            if term.name == roll.REPLACED_TERM:
                continue
            for lead in HORIZONS:
                self.assertEqual([ROLL.flag(term.name, lead, r) for r in range(len(PANEL))],
                                 [BASE.flag(term.name, lead, r) for r in range(len(PANEL))], (term.name, lead))

    def test_the_slot_differs_from_the_unrolled_ramp_only_on_the_moved_days(self):
        plain = gse.GseTermTable(PANEL, ANNOUNCEMENTS)
        differ = [DATES[r] for r in range(len(PANEL)) if plain.flag("dom_19_23", 1, r) != ROLL.flag("dom_19_23", 1, r)]
        self.assertEqual(differ, roll.moved_days(DATES))
        self.assertTrue(differ)


S3 = sc.ARMS[2]


class WalkTests(unittest.TestCase):

    def test_the_arm_is_s3_unchanged_on_a_table_with_the_slot_replaced(self):
        self.assertEqual(S3.name, "sc_s3_robust")
        self.assertIn(roll.REPLACED_TERM, S3.location)
        self.assertEqual(sc.ridge_of(S3), 5.0)

    def test_the_one_step_walk_is_refused_and_no_allow_list_entry_is_added(self):
        day = date(2024, 6, 20)
        with self.assertRaisesRegex(ValueError, "one-step pairs"):
            sc.walk(PANEL, [day], ROLL, {}, (S3,), **SETTINGS, training_pairs="one_step")
        self.assertFalse([k for k, v in osg.ONE_STEP_ALLOW_LIST.items() if v.fitter == "fit_state_terms"])

    def test_a_forecast_moves_with_its_own_targets_value_by_the_effect_times_the_scale(self):
        day = date(2024, 6, 20)
        target = DATES.index(day) + 1
        self.assertEqual(DATES[target], date(2024, 6, 21))
        walk = sc.walk(PANEL, [day], ROLL, {}, (S3,), **SETTINGS)
        altered = roll.RollTermTable(PANEL, ANNOUNCEMENTS)
        altered._flags[("dom_19_23", 1)][target] = 0.0  # a row after the decision: no training pair reads it
        other = sc.walk(PANEL, [day], altered, {}, (S3,), **SETTINGS)
        refit_day = next(iter(walk.estimates))
        effect = walk.estimates[refit_day]["sc_s3_robust"][1].effect["dom_19_23"]
        scale = walk.detail[day]["scale"]
        a, b = walk.forecasts["sc_s3_robust"][day][1], other.forecasts["sc_s3_robust"][day][1]
        for x, y in zip(a, b):
            self.assertAlmostEqual(x - y, scale * effect * 3 / 7)
        self.assertNotEqual(effect, 0.0)


if __name__ == "__main__":
    unittest.main()
