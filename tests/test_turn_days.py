"""H5 (#959): the turn-day labels are functions of the date and the market holiday table alone.

The declaration is `metadata/turn_day_labels_959.json`. Each label is tested before the measurement runs: the business-day
rolls (a month ending on a weekend or a holiday, a quarter ending on Good Friday, a year ending on a Monday), the
precedence between labels, the penultimate and run-up days returned to ordinary, and the refusal of a month the holiday
table does not cover. No source, publication time or revision is read, so no leakage guard is added and no mutation is
recorded.
"""

import unittest
from datetime import date

from repo_model import turn_days as td
from repo_model.data import MONTH_END_BUSINESS_DAYS


def kind(day, tax=False):
    return td.turn_day_type(day, tax_date=tax)


class TestTurnDays(unittest.TestCase):
    def test_a_month_turn_is_the_last_business_day_and_the_first_of_the_next(self):
        self.assertEqual(td.turn_days_of_month(2019, 5), (date(2019, 5, 31), date(2019, 6, 3)))
        self.assertEqual(kind(date(2019, 5, 31)), "turn")
        self.assertEqual(kind(date(2019, 6, 3)), "turn")

    def test_a_month_ending_on_a_weekend_or_holiday_rolls_back_and_the_next_rolls_past_the_holiday(self):
        # 2019-08-31 was a Saturday and 2019-09-02 Labor Day
        self.assertEqual(td.turn_days_of_month(2019, 8), (date(2019, 8, 30), date(2019, 9, 3)))
        self.assertEqual(kind(date(2019, 9, 2)), "ordinary")

    def test_the_quarter_end_turn_is_the_quarters_last_business_day_and_the_first_after(self):
        self.assertEqual(kind(date(2019, 3, 29)), "quarter_end_turn")  # 2019-03-31 was a Sunday
        self.assertEqual(kind(date(2019, 4, 1)), "quarter_end_turn")
        self.assertEqual(kind(date(2024, 3, 28)), "quarter_end_turn")  # Good Friday 2024-03-29, no publication
        self.assertEqual(kind(date(2024, 4, 1)), "quarter_end_turn")
        self.assertEqual(kind(date(2019, 6, 28)), "quarter_end_turn")
        self.assertEqual(kind(date(2019, 7, 1)), "quarter_end_turn")

    def test_the_year_end_is_the_last_business_day_of_december_and_the_first_of_january(self):
        self.assertEqual(kind(date(2018, 12, 31)), "year_end")
        self.assertEqual(kind(date(2019, 1, 2)), "year_end")  # 2019-01-01 is a holiday
        self.assertEqual(kind(date(2021, 12, 31)), "year_end")
        self.assertEqual(kind(date(2022, 1, 3)), "year_end")  # 2022-01-01 was a Saturday

    def test_the_penultimate_and_run_up_days_return_to_ordinary(self):
        for day in (date(2019, 5, 30), date(2019, 5, 29), date(2019, 3, 28), date(2019, 3, 27), date(2018, 12, 28)):
            self.assertEqual(kind(day), "ordinary", day)
        # the repo's month-end reading calls the penultimate day month-end; the new label does not
        from repo_model.data import in_last_business_days_of_month

        self.assertEqual(MONTH_END_BUSINESS_DAYS, 2)
        self.assertTrue(in_last_business_days_of_month(date(2019, 5, 30)))

    def test_the_second_day_after_the_turn_is_ordinary(self):
        self.assertEqual(kind(date(2019, 6, 4)), "ordinary")
        self.assertEqual(kind(date(2019, 4, 2)), "ordinary")

    def test_a_turn_day_outranks_the_tax_date_and_the_tax_date_outranks_ordinary(self):
        self.assertEqual(kind(date(2019, 5, 31), tax=True), "turn")
        self.assertEqual(kind(date(2019, 5, 15), tax=True), "tax_date")
        self.assertEqual(kind(date(2019, 5, 15), tax=False), "ordinary")

    def test_26_december_is_its_own_flag_and_pools_as_ordinary(self):
        self.assertTrue(td.december_26(date(2018, 12, 26)))
        self.assertFalse(td.december_26(date(2018, 12, 27)))
        self.assertFalse(td.december_26(date(2019, 1, 26)))
        self.assertEqual(kind(date(2018, 12, 26)), "ordinary")

    def test_penultimate_days_are_each_months_second_last_business_day(self):
        self.assertTrue(td.penultimate_day(date(2019, 5, 30)))
        self.assertTrue(td.penultimate_day(date(2019, 3, 28)))
        self.assertFalse(td.penultimate_day(date(2019, 5, 31)))
        self.assertFalse(td.penultimate_day(date(2019, 5, 29)))
        self.assertTrue(td.penultimate_day(date(2019, 8, 29)))  # 2019-08-30 is the last business day

    def test_a_month_the_holiday_table_does_not_cover_is_refused(self):
        with self.assertRaises(ValueError):
            kind(date(2031, 1, 2))
        with self.assertRaises(ValueError):
            td.turn_days_of_month(2030, 12)  # its next month's first business day is past the table

    def test_the_relabelled_splits_read_the_calendar_columns_like_the_declared_ones(self):
        values = {"quarter_end": 0.0, "days_to_month_end": 3.0, "tax_date": 0.0}

        class Base:
            def day_type(self, values):
                if values.get("tax_date") is None:
                    raise ValueError("no column")
                return "ordinary"

        relabelled = td.TurnLabels(Base())
        self.assertEqual(relabelled.reporting_day_type(date(2019, 5, 31), values), "turn")
        self.assertEqual(relabelled.reporting_day_type(date(2019, 5, 30), values), "ordinary")
        with self.assertRaises(ValueError):
            relabelled.reporting_day_type(date(2019, 5, 31), {})

    def test_the_level_set_excludes_only_turn_days(self):
        values = {"tax_date": 1.0}

        class Base:
            def day_type(self, values):
                return "ordinary"

        only = td.TurnLabels(Base(), keep_tax_date=False)
        self.assertEqual(only.reporting_day_type(date(2019, 5, 15), values), "ordinary")
        self.assertEqual(only.reporting_day_type(date(2019, 5, 31), values), "turn")


if __name__ == "__main__":
    unittest.main()
