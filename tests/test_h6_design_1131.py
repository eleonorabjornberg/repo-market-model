"""H6 step 2 (#1131): the registration design's strata and the power on contiguous windows of events.

The arithmetic is checked on series with known answers: the contiguous windows of events and their statistic, the critical
value as the 0.95 quantile of the null windows, power as the share of windows above it once the mean is shifted to a skill,
and the number of events in a window of calendar years.

Two readings of the calendar are availability guards, and each has a recorded mutation.

1. `bill_threshold` reads only the rows strictly before the target (the size of a bill settlement is a stand-in rule that
   must be public at the decision). Mutation: replacing `rows[max(0, index - TRAILING_ROWS):index]` with
   `rows[max(0, index - TRAILING_ROWS):index + 1]` makes `BillThresholdTests.test_the_target_row_and_later_rows_are_not_read`
   fail with `AssertionError` (the threshold moved with the target's own settlement); restored, it passes.
2. `visible_meetings` keeps a meeting only if it was public at the instant. Mutation: replacing
   `fomc_calendar.visible_at(m, as_of)` with `True` makes `FomcMembershipTests.test_a_meeting_not_yet_public_is_not_a_member`
   fail with `AssertionError` (4 October 2019, made public on 11 October, was a member at the lead-5 instant); restored,
   it passes.
"""

import importlib.util
import unittest
from datetime import date, datetime
from pathlib import Path

from repo_model import fomc_calendar as fc
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


script = load("h6_design_1131")


class BillThresholdTests(unittest.TestCase):
    def rows(self, amounts):
        return [{"treasury_settlement_bills": a} for a in amounts]

    def test_the_upper_quartile_of_the_positive_settlements_before_the_target(self):
        rows = self.rows([0.0, 100.0, 200.0, 300.0, 400.0, 0.0, 999.0])
        # the four positive amounts before index 5 are 100..400; the 75th percentile is 325 by linear interpolation
        self.assertAlmostEqual(script.bill_threshold(rows, 5), 325.0)

    def test_the_target_row_and_later_rows_are_not_read(self):
        base = [0.0, 100.0, 200.0, 300.0, 400.0, 150.0, 150.0]
        moved = base[:5] + [10_000.0, 10_000.0]
        self.assertEqual(script.bill_threshold(self.rows(base), 5), script.bill_threshold(self.rows(moved), 5))

    def test_no_positive_settlement_before_the_target_has_no_threshold(self):
        self.assertIsNone(script.bill_threshold(self.rows([0.0, 0.0, 5.0]), 2))

    def test_only_the_trailing_rows_are_read(self):
        amounts = [1000.0] * 5 + [10.0] * script.TRAILING_ROWS + [0.0]
        self.assertAlmostEqual(script.bill_threshold(self.rows(amounts), len(amounts) - 1), 10.0)


class FomcMembershipTests(unittest.TestCase):
    def meetings(self):
        return (
            fc.Meeting("a", "scheduled", date(2021, 1, 26), date(2021, 1, 27), datetime(2020, 1, 1), None, "u"),
            fc.Meeting("b", "unscheduled", date(2019, 10, 4), date(2019, 10, 4), datetime(2019, 10, 11, 9, 0), None, "u"),
        )

    def test_a_scheduled_meeting_is_a_member_on_both_days(self):
        days, _ = script.fomc_days(self.meetings(), datetime(2021, 1, 20, 16, 0))
        self.assertEqual(days, {date(2021, 1, 26), date(2021, 1, 27)})

    def test_a_meeting_not_yet_public_is_not_a_member(self):
        days, _ = script.fomc_days(self.meetings(), datetime(2019, 10, 3, 16, 0))
        self.assertNotIn(date(2019, 10, 4), days)

    def test_the_window_is_the_two_business_days_after_the_last_day(self):
        _, window = script.fomc_days(self.meetings(), datetime(2021, 1, 20, 16, 0))
        self.assertEqual(window, {date(2021, 1, 28), date(2021, 1, 29)})

    def test_an_instant_before_the_first_schedule_raises(self):
        with self.assertRaises(ValueError):
            script.fomc_days(self.meetings(), datetime(2010, 1, 1, 16, 0))


class MembershipTests(unittest.TestCase):
    def test_strata_are_not_exclusive(self):
        values = {"treasury_settlement_coupons": 50.0, "treasury_settlement_bills": 300.0, "tax_date": 1.0}
        got = script.membership(date(2021, 6, 15), values, fomc_meeting=True, post_fomc=False, bill_floor=200.0)
        self.assertEqual(got, {"coupon_settlement", "bill_settlement_large", "tax_date", "fomc_meeting"})

    def test_a_small_bill_settlement_is_not_a_member(self):
        values = {"treasury_settlement_coupons": 0.0, "treasury_settlement_bills": 100.0, "tax_date": 0.0}
        self.assertEqual(script.membership(date(2021, 3, 2), values, fomc_meeting=False, post_fomc=False, bill_floor=200.0), set())

    def test_the_turn_labels_name_their_strata(self):
        zero = {"treasury_settlement_coupons": 0.0, "treasury_settlement_bills": 0.0, "tax_date": 0.0}
        self.assertEqual(script.membership(date(2021, 4, 30), zero, fomc_meeting=False, post_fomc=False, bill_floor=None), {"month_end_turn"})
        self.assertEqual(script.membership(date(2021, 6, 30), zero, fomc_meeting=False, post_fomc=False, bill_floor=None),
                         {"quarter_end_turn", "quarter_and_year_end"})
        self.assertEqual(script.membership(date(2021, 12, 31), zero, fomc_meeting=False, post_fomc=False, bill_floor=None),
                         {"year_end", "quarter_and_year_end"})


class WindowTests(unittest.TestCase):
    def test_every_contiguous_window_none_wrapping(self):
        pairs = script.window_pairs([1.0, 2.0, 4.0, 3.0, 6.0, 5.0], 3, lag=1)
        self.assertEqual(len(pairs), 4)
        truth = 21.0 / 6
        self.assertAlmostEqual(pairs[0][0], (7.0 / 3) - truth)
        self.assertAlmostEqual(pairs[3][0], (14.0 / 3) - truth)

    def test_a_window_longer_than_the_series_is_refused(self):
        with self.assertRaises(ValueError):
            script.window_pairs([1.0, 2.0], 3, lag=1)

    def test_a_window_that_cannot_carry_the_lag_is_refused(self):
        with self.assertRaises(ValueError):
            script.window_pairs([1.0] * 10, 3, lag=3)

    def series(self):
        return [((i * 37) % 11 - 5.0) / 5.0 + (0.5 if (i // 7) % 2 else -0.5) for i in range(120)]

    def test_power_at_no_shift_is_at_most_the_level(self):
        pairs = script.window_pairs(self.series(), 30, lag=3)
        c = script.critical_value(pairs)
        self.assertLessEqual(script.power(pairs, c, 0.0), 0.05 + 1.0 / len(pairs))

    def test_power_rises_with_the_shift_and_reaches_one(self):
        pairs = script.window_pairs(self.series(), 30, lag=3)
        c = script.critical_value(pairs)
        values = [script.power(pairs, c, s) for s in (0.0, 0.2, 0.5, 5.0)]
        self.assertEqual(values, sorted(values))
        self.assertEqual(values[-1], 1.0)

    def test_the_critical_value_is_the_95th_percentile_of_the_null_statistics(self):
        pairs = script.window_pairs(self.series(), 30, lag=3)
        stats = sorted(dev / se for dev, se in pairs)
        c = script.critical_value(pairs)
        self.assertLessEqual(sum(1 for s in stats if s > c) / len(stats), 0.05 + 1e-12)
        self.assertGreaterEqual(sum(1 for s in stats if s >= c) / len(stats), 0.05 - 1e-12)

    def test_events_in_a_window_of_years(self):
        self.assertEqual(script.window_events(30.0, 2.0, lag=3), 60)
        self.assertEqual(script.window_events(1.0, 1.0, lag=3), 5)

    def test_events_per_year(self):
        events = [date(2021, 1, 1), date(2021, 7, 1), date(2022, 1, 1)]
        self.assertAlmostEqual(script.events_per_year(events), 3 / (365 / 365.25), places=2)


class ScopeTests(unittest.TestCase):
    def test_a_day_after_the_declared_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.require_scored_days([date(2026, 1, 5)])


if __name__ == "__main__":
    unittest.main()
