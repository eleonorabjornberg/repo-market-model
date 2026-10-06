"""The reporting split's month-end is the last two business days (#278).

Eleonora's ruling of 6 October 2026 on #269, item 16, option (a): the reporting
split counts month-end as the month's last two business days on the market
calendar, not as `days_to_month_end <= 2` calendar days. The scorecaster's window
(`recalibration.py`) is part of the frozen model and is not changed.

Recorded mutation (the new guard, `data.last_business_days_of_month`): replacing
`day.weekday() < 5 and day not in holidays.closed` with `day.weekday() < 5` in the
backward walk made `test_a_month_ending_on_a_holiday_counts_back_over_it` fail with
AssertionError.
"""

from __future__ import annotations

import unittest
from datetime import date
from pathlib import Path

from repo_model import data
from repo_model.evaluation_splits import MONTH_END_RULE, load_split_declaration

ROOT = Path(__file__).resolve().parents[1]
SPLITS = load_split_declaration(ROOT / "metadata" / "evaluation_splits.json")


class LastBusinessDaysTests(unittest.TestCase):
    def test_an_ordinary_month_ends_on_its_last_two_weekdays(self):
        # 2024-04-30 was a Tuesday.
        self.assertEqual(
            data.last_business_days_of_month(2024, 4), (date(2024, 4, 29), date(2024, 4, 30))
        )

    def test_a_month_ending_on_a_weekend_counts_back_over_it(self):
        # 2024-08-31 was a Saturday: Thursday the 29th and Friday the 30th.
        self.assertEqual(
            data.last_business_days_of_month(2024, 8), (date(2024, 8, 29), date(2024, 8, 30))
        )
        # 2025-08-31 was a Sunday.
        self.assertEqual(
            data.last_business_days_of_month(2025, 8), (date(2025, 8, 28), date(2025, 8, 29))
        )

    def test_a_month_ending_on_a_holiday_counts_back_over_it(self):
        # 2024-03-29 was Good Friday (no SOFR print) and the 30th and 31st a weekend:
        # March's last two business days are Wednesday the 27th and Thursday the 28th.
        self.assertIn(date(2024, 3, 29), data.market_holidays().closed)
        self.assertEqual(
            data.last_business_days_of_month(2024, 3), (date(2024, 3, 27), date(2024, 3, 28))
        )

    def test_the_calendar_day_window_and_this_one_differ(self):
        # July 2024 ended on a Wednesday: days_to_month_end <= 2 reads Monday the 29th too.
        self.assertFalse(data.in_last_business_days_of_month(date(2024, 7, 29)))
        self.assertTrue(data.in_last_business_days_of_month(date(2024, 7, 30)))
        self.assertTrue(data.in_last_business_days_of_month(date(2024, 7, 31)))
        # August 2025 ended on a Sunday: Thursday the 28th is month-end here, and not there.
        self.assertTrue(data.in_last_business_days_of_month(date(2025, 8, 28)))
        self.assertFalse(data.in_last_business_days_of_month(date(2025, 8, 31)))

    def test_a_month_outside_the_holiday_table_is_refused(self):
        with self.assertRaises(ValueError):
            data.last_business_days_of_month(2028, 1)


class ReportingDayTypeTests(unittest.TestCase):
    def values(self, day, *, quarter_end=0, tax_date=0):
        return {
            "quarter_end": quarter_end,
            "tax_date": tax_date,
            "days_to_month_end": data.days_to_month_end(day),
        }

    def test_month_end_is_read_from_the_date_on_the_market_calendar(self):
        # August 2025 ended on a Sunday. Thursday the 28th is one of the last two
        # business days, but 3 calendar days from the month's end.
        thursday = date(2025, 8, 28)
        self.assertEqual(SPLITS.day_type(self.values(thursday)), "ordinary")
        self.assertEqual(SPLITS.reporting_day_type(thursday, self.values(thursday)), "month_end")
        # July 2024 ended on a Wednesday. Monday the 29th was month-end by calendar days.
        monday = date(2024, 7, 29)
        self.assertEqual(SPLITS.day_type(self.values(monday)), "month_end")
        self.assertEqual(SPLITS.reporting_day_type(monday, self.values(monday)), "ordinary")

    def test_precedence_is_unchanged(self):
        day = date(2024, 3, 28)
        self.assertEqual(
            SPLITS.reporting_day_type(day, self.values(day, quarter_end=1)), "quarter_end"
        )
        self.assertEqual(
            SPLITS.reporting_day_type(day, self.values(day, tax_date=1)), "month_end"
        )
        other = date(2024, 4, 15)
        self.assertEqual(
            SPLITS.reporting_day_type(other, self.values(other, tax_date=1)), "tax_date"
        )
        self.assertEqual(SPLITS.reporting_day_type(other, self.values(other)), "ordinary")

    def test_the_conditioning_day_type_is_unchanged(self):
        # `day_type` feeds the frozen model's grouping; only reporting moves.
        day = date(2024, 7, 29)
        self.assertEqual(SPLITS.day_type(self.values(day)), "month_end")


class LiveScorerTests(unittest.TestCase):
    """`scripts/live_score.py` reports by the business-day month-end, and says so.

    Recorded mutation: reverting `score_crps`'s `reporting_day_type(when, row.values)`
    to `day_type(row.values)` made `test_the_scorer_counts_month_end_in_business_days`
    fail with AssertionError (the month_end cell lost 2026-11-27).
    """

    @classmethod
    def setUpClass(cls):
        from test_live_record import _scoring_records, score

        cls.score = score
        cls.records, cls.rows = _scoring_records([0.5, 0.8, 1.0, 1.2, 1.5], [-6.0, -2.0, 1.0, 4.0, 9.0], days=40)

    def test_the_scorer_counts_month_end_in_business_days(self):
        cell = self.score.score_crps(self.records, self.rows, SPLITS, date(2027, 4, 1))["crps/h1"]
        scored = [
            date.fromisoformat(record["targets"][0]["target_date"]) for record in self.records
        ]
        by_date = {row.date: row for row in self.rows}
        expected = sum(1 for when in scored if data.in_last_business_days_of_month(when))
        calendar_days = sum(1 for when in scored if by_date[when].values["days_to_month_end"] <= 2)
        self.assertNotEqual(expected, calendar_days, "the fixture must tell the two rules apart")
        self.assertEqual(cell["by_day_type"]["month_end"]["days"], expected)

    def test_the_result_carries_the_month_end_label(self):
        result = self.score.assemble(self.records, self.rows, SPLITS, date(2027, 4, 1), previous=[])
        self.assertEqual(result["month_end_rule"], MONTH_END_RULE)


if __name__ == "__main__":
    unittest.main()
