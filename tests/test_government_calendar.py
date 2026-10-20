"""The OFR's cleared-repo series are dated by the days the government is open (#1016, of finding #1003).

The OFR's data-release page says "Releases are not published on government holidays and data for affected days are
instead published on the next day the government is open". `ofr_stfm_repo_cleared` counts its one-day lag on the panel's
rows, which are SOFR publication days, so on a statutory holiday the market opened (`statutory_days_the_market_opened` in
`metadata/market_holidays.json`: 2021-06-18, 2021-12-31, 2023-11-10) the value dated the day before was read at 15:00 on the
holiday, three days before the OFR published it. `government_calendar.government_open_dating()` counts the lag on panel rows
the government is open; a source opts in with `government_open_days_only`. `asof.py` is frozen by the final-test
pre-registration, so the rule is swapped for the run, as `h41_release.release_dating()` does.

The executive-order closures that were market days (2020-12-24, 2024-12-24, 2025-01-09, 2025-12-24, 2025-12-26) are not
counted: whether they are "government holidays" is Eleonora's question (#1016, criterion 3), and a test here pins that they
read as before.

Written red first: before `repo_model.government_calendar` existed, this module failed to import.

Recorded mutation (CLAUDE.md), 20 October 2026, in a disposable copy: `src/repo_model/government_calendar.py`,
`if row_date in closed: continue` (the line that does not count a closed panel row toward the lag) deleted. The
2021-06-18 decision (scored 2021-06-21) then reads the value dated 2021-06-17 again, and
`test_the_decision_after_a_closed_market_day_does_not_see_the_previous_days_value` fails with `AssertionError`
(`datetime.date(2021, 6, 17) != datetime.date(2021, 6, 16)`); `test_the_guard_refuses_the_value_the_unadjusted_rule_reads`
fails with `AssertionError: LookAheadError not raised`, and `test_the_lag_counts_open_rows_and_runs_off_the_panel_as_never`
with `AssertionError` (2021-12-31 15:00 instead of 2022-01-03 15:00).
"""

from __future__ import annotations

import unittest
from datetime import date, time, timedelta
from types import MappingProxyType
from unittest import mock

from repo_model import asof, baseline, contract, data, dvp_segment, government_calendar, measurement_fields
from repo_model.asof import InformationRule
from repo_model.splits import LookAheadError

FEATURES = ("spread_bps", "ofr_dvp_rate_1d")
CLEARED = dvp_segment.OFR_CLEARED_SOURCE_ID


def market_days(first: date, last: date):
    """Weekdays between the two dates the New York Fed publishes SOFR: the panel's rows."""

    closed = data.market_holidays().closed
    out, day = [], first
    while day <= last:
        if day.weekday() < 5 and day not in closed:
            out.append(day)
        day += timedelta(days=1)
    return out


class GovernmentOpenDatingTests(unittest.TestCase):
    #: (government closed, market open) -> the scored day whose decision is made on it
    CASES = (
        (date(2021, 6, 18), date(2021, 6, 21), date(2021, 6, 16)),
        (date(2021, 12, 31), date(2022, 1, 3), date(2021, 12, 29)),
        (date(2023, 11, 10), date(2023, 11, 13), date(2023, 11, 8)),
    )

    def setUp(self):
        self.registry = measurement_fields.load_registry()
        fields = {**dvp_segment.COLUMN_FIELDS, **dvp_segment.CLEARED_COLUMN_FIELDS}
        switch = mock.patch.multiple(
            contract,
            FEATURE_FIELDS=MappingProxyType({**contract.FEATURE_FIELDS, **fields}),
            FEATURE_SOURCES=MappingProxyType(
                {
                    **contract.FEATURE_SOURCES,
                    **{c: tuple(sorted({s for s, _f in pairs})) for c, pairs in fields.items()},
                }
            ),
        )
        switch.start()
        self.addCleanup(switch.stop)

    def rule(self):
        return InformationRule(self.registry, FEATURES, decision_time=time(16, 0), horizon=1)

    def read_date(self, dates, scored, rule=None):
        rule = rule or self.rule()
        info = rule.information_set(dates, dates.index(scored))
        (read,) = [r for r in info.reads if r.feature == "ofr_dvp_rate_1d"]
        return rule, info, dates[read.row]

    def test_the_source_opts_in_and_no_other_source_does(self):
        self.assertTrue(self.registry[CLEARED].get(government_calendar.OPT_IN_KEY))
        others = [s for s, block in self.registry.items() if s != CLEARED and government_calendar.OPT_IN_KEY in block]
        self.assertEqual(others, [])

    def test_the_unadjusted_rule_reads_the_value_the_ofr_had_not_published(self):
        for closed, scored, _expected in self.CASES:
            dates = market_days(closed - timedelta(days=20), closed + timedelta(days=20))
            _rule, _info, read = self.read_date(dates, scored)
            self.assertEqual(read, dates[dates.index(closed) - 1], closed)

    def test_the_decision_after_a_closed_market_day_does_not_see_the_previous_days_value(self):
        for closed, scored, expected in self.CASES:
            dates = market_days(closed - timedelta(days=20), closed + timedelta(days=20))
            with government_calendar.government_open_dating():
                _rule, _info, read = self.read_date(dates, scored)
            self.assertEqual(read, expected, closed)

    def test_the_guard_refuses_the_value_the_unadjusted_rule_reads(self):
        for closed, scored, _expected in self.CASES:
            dates = market_days(closed - timedelta(days=20), closed + timedelta(days=20))
            rule, info, _read = self.read_date(dates, scored)
            with government_calendar.government_open_dating():
                with self.assertRaises(LookAheadError, msg=str(closed)):
                    rule.check(dates, info)

    def test_the_adjusted_read_passes_both_guards(self):
        for closed, scored, _expected in self.CASES:
            dates = market_days(closed - timedelta(days=20), closed + timedelta(days=20))
            with government_calendar.government_open_dating():
                rule, info, _read = self.read_date(dates, scored)
                rule.check(dates, info)

    def test_an_ordinary_day_reads_as_before(self):
        dates = market_days(date(2026, 1, 5), date(2026, 2, 6))
        _rule, _info, before = self.read_date(dates, date(2026, 1, 22))
        with government_calendar.government_open_dating():
            _rule, _info, after = self.read_date(dates, date(2026, 1, 22))
        self.assertEqual((before, after), (date(2026, 1, 20), date(2026, 1, 20)))

    def test_an_executive_order_closure_is_not_counted(self):
        """2024-12-24 was a market day and, by executive order, a day federal offices closed: a marked question (#1016, 3)."""

        dates = market_days(date(2024, 12, 2), date(2025, 1, 31))
        scored = date(2024, 12, 26)
        _rule, _info, before = self.read_date(dates, scored)
        with government_calendar.government_open_dating():
            _rule, _info, after = self.read_date(dates, scored)
        self.assertEqual(before, after)

    def test_a_source_that_does_not_opt_in_is_dated_as_before(self):
        dates = market_days(date(2021, 12, 1), date(2022, 1, 31))
        for source, field in (("ofr_stfm_repo", "REPO-DVP_AR_OO-P"), ("nyfed_sofr", "SOFR")):
            if source not in self.registry:
                continue
            before = [asof.declared_availability(self.registry, source, field, dates, p) for p in range(len(dates))]
            with government_calendar.government_open_dating():
                after = [asof.declared_availability(self.registry, source, field, dates, p) for p in range(len(dates))]
            self.assertEqual(before, after, source)

    def test_the_lag_counts_open_rows_and_runs_off_the_panel_as_never(self):
        dates = market_days(date(2021, 12, 20), date(2022, 1, 5))
        position = dates.index(date(2021, 12, 30))
        with government_calendar.government_open_dating():
            moment = asof.declared_availability(self.registry, CLEARED, "REPO-DVP_AR_OO-P", dates, position)
            last = asof.declared_availability(self.registry, CLEARED, "REPO-DVP_AR_OO-P", dates, len(dates) - 1)
        self.assertEqual((moment.date(), moment.time()), (date(2022, 1, 3), time(15, 0)))
        self.assertEqual(last, asof.NEVER_ON_THIS_PANEL)

    def test_the_swap_is_undone_on_the_way_out_even_after_a_raise(self):
        originals = (asof.declared_availability, baseline._declared_availability)
        with self.assertRaises(RuntimeError):
            with government_calendar.government_open_dating():
                self.assertIsNot(asof.declared_availability, originals[0])
                raise RuntimeError("inside")
        self.assertEqual((asof.declared_availability, baseline._declared_availability), originals)

    def test_a_table_the_panel_is_not_in_is_refused(self):
        """A date after the table's last day cannot be called open: the lag is not guessed."""

        dates = [date(2031, 1, 2), date(2031, 1, 3), date(2031, 1, 6)]
        with government_calendar.government_open_dating():
            with self.assertRaises(ValueError):
                asof.declared_availability(self.registry, CLEARED, "REPO-DVP_AR_OO-P", dates, 0)


if __name__ == "__main__":
    unittest.main()
