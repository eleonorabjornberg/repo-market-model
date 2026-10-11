"""The tax-date window counts market days (#538, Eleonora's ruling of 10 October 2026 on #521).

`data.tax_date` reads 1.0 on the corporate estimated-tax deadline and the two business days after it. The
published rule counts those days with the District of Columbia's holidays removed, so DC Emancipation Day
(16 April) pushes 16 April out of the window although repo trades that day. Her ruling: the deadline stays on the
DC rule (26 USC 7503); the payment days after it are counted on the market calendar
(`metadata/market_holidays.json`). The panel's published `tax_date` column is unchanged until a publish pull
request rebuilds it; the market-day rule is `data.tax_date_market_days`, and `data.tax_window_on_market_days()` puts
it in the build for one run.

Expected windows are written from a calendar and the market holiday table, not from the code's output:

* 2019-04-15 is a Monday. DC Emancipation Day, Tuesday 2019-04-16, is a market day. The window is 15, 16, 17 April.
* 2020-04-15 is a Wednesday and 2020-04-16 a Thursday: the window is 15, 16, 17 April (the DC rule gave 15 and 17
  and 20 April).
* 2018-04-16 is a Monday and DC Emancipation Day: the deadline rolls to 17 April, a Tuesday, and the window is 17,
  18, 19 April, with or without the market rule.
* 2024-06-19 (Juneteenth, Wednesday) is closed for SOFR and a DC holiday: the window after Monday 2024-06-17 is 17,
  18, 20 June under both rules.
* 2022-04-15 is a Friday and Good Friday (closed) and Emancipation Day observed: the deadline is Monday 18 April.

Mutation record, 11 October 2026, python3 3.11, a disposable copy, `PYTHONDONTWRITEBYTECODE=1`, the killing test
run alone:

1. `tax_date_market_days`: `if _is_market_business_day(current)` -> `if _is_tax_business_day(current)` (the window
   counted on DC holidays again). Killed by `MarketWindowTests.test_the_window_counts_market_days`, AssertionError.
2. `_is_market_business_day`: `current not in holidays.closed` -> `True` (weekends only). Killed by
   `MarketWindowTests.test_a_market_holiday_in_the_window_moves_its_end`, AssertionError.
"""

import sys
import unittest
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model import data  # noqa: E402


def window(rule, year, month):
    return [day for day in (date(year, month, d) for d in range(1, 29)) if rule(day) == 1.0]


class MarketWindowTests(unittest.TestCase):
    def test_the_window_counts_market_days(self):
        """16 April 2019 is in the window, as the ruling says; the published rule leaves it out."""

        market = data.tax_date_market_days
        self.assertEqual(market(date(2019, 4, 16)), 1.0)
        self.assertEqual(data.tax_date(date(2019, 4, 16)), 0.0, "the published rule is unchanged")
        self.assertEqual(window(market, 2019, 4), [date(2019, 4, 15), date(2019, 4, 16), date(2019, 4, 17)])
        self.assertEqual(window(market, 2020, 4), [date(2020, 4, 15), date(2020, 4, 16), date(2020, 4, 17)])
        self.assertEqual(window(data.tax_date, 2020, 4), [date(2020, 4, 15), date(2020, 4, 17), date(2020, 4, 20)])

    def test_the_deadline_stays_on_the_dc_rule(self):
        market = data.tax_date_market_days
        self.assertEqual(market(date(2018, 4, 16)), 0.0)
        self.assertEqual(window(market, 2018, 4), [date(2018, 4, 17), date(2018, 4, 18), date(2018, 4, 19)])
        self.assertEqual(window(market, 2022, 4), [date(2022, 4, 18), date(2022, 4, 19), date(2022, 4, 20)])
        self.assertEqual(window(market, 2023, 4), [date(2023, 4, 18), date(2023, 4, 19), date(2023, 4, 20)])
        self.assertEqual(window(market, 2019, 9), [date(2019, 9, 16), date(2019, 9, 17), date(2019, 9, 18)])

    def test_a_market_holiday_in_the_window_moves_its_end(self):
        market = data.tax_date_market_days
        self.assertEqual(window(market, 2024, 6), [date(2024, 6, 17), date(2024, 6, 18), date(2024, 6, 20)])
        self.assertEqual(market(date(2024, 6, 19)), 0.0)

    def test_only_the_four_deadline_months_are_ever_one(self):
        market = data.tax_date_market_days
        self.assertEqual(market(date(2019, 3, 15)), 0.0)
        self.assertEqual(market(date(2019, 12, 31)), 0.0)

    def test_the_two_rules_differ_only_around_dc_emancipation_day(self):
        differing = [
            day
            for year in range(2018, 2027)
            for month in data.TAX_DEADLINE_MONTHS
            for day in (date(year, month, d) for d in range(1, 29))
            if data.tax_date(day) != data.tax_date_market_days(day)
        ]
        self.assertEqual(
            differing,
            [
                date(2019, 4, 16), date(2019, 4, 18),
                date(2020, 4, 16), date(2020, 4, 20),
                date(2021, 4, 16), date(2021, 4, 20),
                date(2024, 4, 16), date(2024, 4, 18),
                date(2025, 4, 16), date(2025, 4, 18),
                date(2026, 4, 16), date(2026, 4, 20),
            ],
        )

    def test_a_day_the_table_does_not_cover_is_refused(self):
        with self.assertRaises(ValueError):
            data.tax_date_market_days(date(2031, 4, 16))


class SwitchTests(unittest.TestCase):
    def test_the_switch_changes_the_built_column_for_one_run_only(self):
        rule = data.CALENDAR_COLUMN_RULES["tax_date"]
        with data.tax_window_on_market_days():
            self.assertEqual(data.CALENDAR_COLUMN_RULES["tax_date"](date(2019, 4, 16)), 1.0)
            self.assertEqual(data.CALENDAR_COLUMN_RULES["quarter_end"], data.quarter_end)
        self.assertIs(data.CALENDAR_COLUMN_RULES["tax_date"], rule)
        self.assertEqual(data.CALENDAR_COLUMN_RULES["tax_date"](date(2019, 4, 16)), 0.0)

    def test_a_build_inside_the_switch_reads_16_april_2019_as_a_tax_date(self):
        registry = {
            "nyfed_sofr": {
                "release_lag": {
                    "basis": "ref_date", "unit": "business_days", "days": 1, "worst_case_calendar_days": 6,
                    "available_time": "15:00", "timezone": "America/New_York", "note": "fixture",
                }
            }
        }
        observations = [
            data.PointInTimeObservation(
                series_id="SOFR", ref_date=day,
                available_at=datetime.combine(day + timedelta(days=1), time(19, 0), tzinfo=timezone.utc),
                value=2.0, vintage_id=f"v{day.isoformat()}", source_sha="a" * 64,
            )
            for day in (date(2019, 4, 15), date(2019, 4, 16), date(2019, 4, 17), date(2019, 4, 18))
        ]

        def tax_column():
            build = data.build_daily_panel(
                observations, registry, build_cutoff=datetime(2026, 3, 1, tzinfo=timezone.utc),
                decision_time=time.fromisoformat("15:00"), columns=("sofr", "tax_date"),
            )
            return [row.values["tax_date"] for row in build.observations]

        self.assertEqual(tax_column(), [1.0, 0.0, 1.0, 1.0])
        with data.tax_window_on_market_days():
            self.assertEqual(tax_column(), [1.0, 1.0, 1.0, 0.0])


if __name__ == "__main__":
    unittest.main()
