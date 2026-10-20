"""H5 step 2 / H6 step 1 (#965): 15 October as a declared alternative tax date, a function of the date alone.

The declaration is `metadata/tax_date_october_965.json`. The window is the 15th of October rolled forward off weekends and
District of Columbia holidays (the rule of `data.corporate_tax_deadline`) and the two market days after it (the rule of
`data.tax_date_market_days`); the control is the 15th of the months the published column leaves alone, rolled and counted on
the market calendar. Each is tested before the measurement runs: the weekend rolls, the October windows of the panel's
years, the months outside the rule, the precedence of the published types, and the refusal of a year the market holiday
table does not cover. No source, publication time or revision is read, so no leakage guard is added and no mutation is
recorded here (the script's scope guard has its own, in `test_tax_date_october_965_script.py`).
"""

import unittest
from datetime import date

from repo_model import data
from repo_model import tax_date_october as tdo


class Base:
    """A stand-in for the declared `SplitDeclaration`: only the types that matter here."""

    def reporting_day_type(self, when, values):
        return values.get("_kind", "ordinary")


def window(year):
    return [d for d in (date(year, 10, n) for n in range(1, 32)) if tdo.october_window(d)]


class OctoberWindowTests(unittest.TestCase):
    def test_a_weekday_fifteenth_opens_a_three_day_window(self):
        self.assertEqual(window(2019), [date(2019, 10, 15), date(2019, 10, 16), date(2019, 10, 17)])  # a Tuesday
        self.assertEqual(window(2018), [date(2018, 10, 15), date(2018, 10, 16), date(2018, 10, 17)])  # a Monday
        self.assertEqual(window(2025), [date(2025, 10, 15), date(2025, 10, 16), date(2025, 10, 17)])  # a Wednesday

    def test_a_fifteenth_on_a_weekend_rolls_forward_to_the_monday(self):
        self.assertEqual(window(2023), [date(2023, 10, 16), date(2023, 10, 17), date(2023, 10, 18)])  # a Sunday
        self.assertEqual(window(2022), [date(2022, 10, 17), date(2022, 10, 18), date(2022, 10, 19)])  # a Saturday

    def test_the_deadline_is_the_corporate_rule_and_not_a_tax_month_of_the_published_column(self):
        self.assertEqual(tdo.october_deadline(2022), date(2022, 10, 17))
        self.assertEqual(data.tax_date(date(2019, 10, 15)), 0.0)
        self.assertEqual(data.tax_date_market_days(date(2019, 10, 15)), 0.0)
        self.assertEqual(tdo.october_tax_date(date(2019, 10, 15)), 1.0)

    def test_other_days_and_months_are_outside_it(self):
        self.assertEqual(tdo.october_window(date(2019, 10, 14)), False)
        self.assertEqual(tdo.october_window(date(2019, 10, 18)), False)
        self.assertEqual(tdo.october_window(date(2019, 9, 16)), False)
        self.assertEqual(tdo.october_window(date(2019, 11, 15)), False)

    def test_the_dc_rule_and_the_market_rule_agree_on_the_fifteenth_of_october_in_every_year_of_the_table(self):
        # the directive rolls by the DC rule; the market rule is the control's. They differ only where one calendar has
        # a holiday the other does not on or after the 15th; Columbus Day (8-14 October) never reaches it.
        for year in range(2018, 2031):
            day = date(year, 10, 15)
            while not data._is_market_business_day(day):
                day = day.replace(day=day.day + 1)
            self.assertEqual(tdo.october_deadline(year), day, year)

    def test_a_year_the_holiday_table_does_not_cover_is_refused(self):
        with self.assertRaises(ValueError):
            tdo.october_window(date(2031, 10, 15))

    def test_the_published_columns_are_untouched_in_the_panels_years(self):
        for year in range(2018, 2026):
            for day in window(year):
                self.assertEqual(data.tax_date(day), 0.0, day)
                self.assertEqual(data.CALENDAR_COLUMN_RULES["tax_date"], data.tax_date)


class ControlWindowTests(unittest.TestCase):
    def test_the_control_is_the_fifteenth_rolled_on_the_market_calendar_plus_two_market_days(self):
        self.assertTrue(tdo.control_window(date(2019, 11, 15)))
        self.assertTrue(tdo.control_window(date(2019, 11, 18)))
        self.assertTrue(tdo.control_window(date(2019, 11, 19)))
        self.assertFalse(tdo.control_window(date(2019, 11, 20)))
        self.assertFalse(tdo.control_window(date(2019, 11, 14)))

    def test_a_fifteenth_on_a_market_holiday_rolls_past_it(self):
        # 2021-02-15 was Presidents Day (no SOFR); 2018-01-15 was Martin Luther King Jr. Day
        self.assertEqual(tdo.control_deadline(2021, 2), date(2021, 2, 16))
        self.assertEqual(tdo.control_deadline(2018, 1), date(2018, 1, 16))
        self.assertTrue(tdo.control_window(date(2021, 2, 18)))
        self.assertFalse(tdo.control_window(date(2021, 2, 19)))

    def test_the_months_the_published_column_or_the_alternative_already_holds_are_not_in_the_control(self):
        for month in (4, 6, 9, 10, 12):
            self.assertFalse(any(tdo.control_window(date(2019, month, n)) for n in range(1, 29)), month)

    def test_the_control_months_are_the_other_seven(self):
        self.assertEqual(tdo.CONTROL_MONTHS, (1, 2, 3, 5, 7, 8, 11))


class AlternativeLabelsTests(unittest.TestCase):
    def labels(self, which="october"):
        return tdo.AlternativeLabels(Base(), which=which)

    def test_an_ordinary_day_in_the_october_window_is_a_tax_date(self):
        self.assertEqual(self.labels().reporting_day_type(date(2019, 10, 16), {}), "tax_date")
        self.assertEqual(self.labels().reporting_day_type(date(2019, 10, 22), {}), "ordinary")

    def test_the_published_types_keep_their_precedence(self):
        for kind in ("quarter_end", "month_end", "tax_date"):
            self.assertEqual(self.labels().reporting_day_type(date(2019, 10, 16), {"_kind": kind}), kind)

    def test_the_control_relabels_only_its_own_days(self):
        control = self.labels("control")
        self.assertEqual(control.reporting_day_type(date(2019, 11, 15), {}), "tax_date")
        self.assertEqual(control.reporting_day_type(date(2019, 10, 15), {}), "ordinary")
        self.assertEqual(self.labels("october").reporting_day_type(date(2019, 11, 15), {}), "ordinary")

    def test_an_unknown_alternative_is_refused(self):
        with self.assertRaises(ValueError):
            tdo.AlternativeLabels(Base(), which="november")


class CalendarFlagTests(unittest.TestCase):
    def test_the_ranker_flag_adds_the_window_and_changes_nothing_else(self):
        self.assertEqual(tdo.extra_risk_flag(date(2019, 10, 15), "october"), True)
        self.assertEqual(tdo.extra_risk_flag(date(2019, 10, 18), "october"), False)
        self.assertEqual(tdo.extra_risk_flag(date(2019, 11, 15), "october"), False)
        self.assertEqual(tdo.extra_risk_flag(date(2019, 11, 15), "control"), True)


if __name__ == "__main__":
    unittest.main()
