"""Settlements dated from the auction announcement, and the H.4.1 read per release (#541).

Eleonora's ruling of 10 October 2026 (relayed by the orchestrating session on #541): (1) a Treasury
settlement is dated from the auction announcement, not the auction result; (2) the H.4.1 is read per
release, at the release's own publication instant, not five calendar days after the Wednesday.

Both are measurement declarations, off in every published declaration: `metadata/sources.json` is
frozen by the final-test pre-registration (bytes), so the published registry is not touched. A scoring
script builds a registry variant from the declaration, as `settlement_dating.result_dated_registry`
does for #175.
"""

from __future__ import annotations

import json
import sys
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model import asof, h41_release as h41  # noqa: E402
from repo_model import settlement_dating as sd  # noqa: E402
from repo_model.asof import InformationRule, StaleReadError  # noqa: E402
from repo_model.data import DailyObservation  # noqa: E402
from repo_model.ingest import load_source_registry  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

ANNOUNCEMENT = ROOT / "metadata" / "settlement_announcement_dating.json"
H41 = ROOT / "metadata" / "h41_release_dating.json"
REGISTRY = ROOT / "metadata" / "sources.json"


def weekdays(start, count):
    out, when = [], start
    while len(out) < count:
        if when.weekday() < 5:
            out.append(when)
        when += timedelta(days=1)
    return out


def record(announced, auction, issue, kind="Note", amount="40000000000"):
    return {
        "announcemt_date": announced.isoformat(), "auction_date": auction.isoformat(),
        "issue_date": issue.isoformat(), "security_type": kind, "offering_amt": amount,
        "total_accepted": "null", "closing_time_comp": "01:00 PM",
    }


class AnnouncementDatingTests(unittest.TestCase):
    """A settlement is public from its auction announcement, and not before (ruling 1).

    A coupon settlement announced before the decision instant and settling within the horizon is
    known at `h >= 2`, so the risk-date calendar marks it. `check_known_columns` holds a column to
    the announcement in both directions: counting an auction not yet announced raises
    `LookAheadError`, and leaving out one that was raises `StaleReadError`.

    Red first: written before `metadata/settlement_announcement_dating.json` existed
    (`FileNotFoundError` in `setUp`).

    Mutation record. In a `git archive` copy of the tree under /tmp, CPython 3.11
    (`/opt/rmm-venv`), this class run alone, unmutated control green. In `known_amount`, the guard
    `and result.public_at <= instant` was mutated to `and result.public_at is not None` (every
    announcement on file treated as public at any instant). The target was found once before the
    change and was gone after. Killed, 5 failures, all
    `AssertionError`: `test_an_announcement_after_the_decision_is_invisible` (`40.0 != 0.0`),
    `test_reading_an_unannounced_settlement_raises` (`LookAheadError not raised`),
    `test_leaving_out_an_announced_settlement_raises` (`StaleReadError not raised`),
    `test_a_partly_announced_day_counts_only_the_announced_part` (`(50.0, 10.0) != (40.0, 0.0)`) and
    `test_the_known_coupon_settlement_is_a_risk_date_at_two_or_more` (`True is not false`).
    """

    def setUp(self):
        self.declaration = sd.load_result_dating(ANNOUNCEMENT)
        self.dates = weekdays(date(2024, 4, 1), 9)
        # A coupon announced on dates[1], auctioned on dates[3], settles on dates[7]:
        # public from dates[1] at the declared instant, six panel days ahead of dates[7].
        self.records = [record(self.dates[1], self.dates[3], self.dates[7])]
        self.results = sd.auction_results(self.records, self.declaration)
        self.rows = [
            DailyObservation(day, {
                "sofr": 5.31, "iorb": 5.40,
                "treasury_settlement": 40.0 if day == self.dates[7] else 0.0,
                "treasury_settlement_bills": 0.0,
                "treasury_settlement_coupons": 40.0 if day == self.dates[7] else 0.0,
                "treasury_settlement_soma": 0.0,
            })
            for day in self.dates
        ]

    def known(self, horizon):
        return sd.known_columns(self.rows, self.results, horizon, self.declaration)

    def test_the_declaration_is_dated_from_the_announcement(self):
        self.assertEqual(self.declaration["basis"], "auction_announcement")
        self.assertEqual(self.declaration["announcement_date_field"], "announcemt_date")
        self.assertIn("off", self.declaration["status"])

    def test_a_coupon_settlement_announced_before_the_decision_is_known_at_two_or_more(self):
        for horizon in (2, 3, 4, 5):
            with self.subTest(horizon=horizon):
                row = self.known(horizon)[7].values
                self.assertEqual(row["treasury_settlement"], 40.0)
                self.assertEqual(row["treasury_settlement_coupons"], 40.0)

    def test_an_announcement_after_the_decision_is_invisible(self):
        # dates[1] is announced; a decision on dates[0] is before it (h = 7), one on dates[1] is not (h = 6).
        self.assertEqual(self.known(7)[7].values["treasury_settlement_coupons"], 0.0)
        self.assertEqual(self.known(6)[7].values["treasury_settlement_coupons"], 40.0)

    def test_the_result_does_not_date_it(self):
        # The auction is on dates[3]; under the result dating this would be invisible at h = 5 (decision dates[2]).
        self.assertEqual(self.known(5)[7].values["treasury_settlement_coupons"], 40.0)

    def test_reading_an_unannounced_settlement_raises(self):
        with self.assertRaises(LookAheadError):
            sd.check_known_columns(self.rows, self.results, 7, self.declaration)
        sd.check_known_columns(self.known(7), self.results, 7, self.declaration)

    def test_leaving_out_an_announced_settlement_raises(self):
        with self.assertRaises(StaleReadError):
            sd.check_known_columns(self.known(7), self.results, 6, self.declaration)
        sd.check_known_columns(self.known(6), self.results, 6, self.declaration)

    def test_an_announcement_with_no_result_yet_is_still_public(self):
        # `total_accepted` is the string 'null' for an auction not yet held: the announcement stands.
        self.assertIsNotNone(self.results[0].public_at)

    def test_a_partly_announced_day_counts_only_the_announced_part(self):
        records = self.records + [record(self.dates[5], self.dates[6], self.dates[7], kind="Bill", amount="10000000000")]
        results = sd.auction_results(records, self.declaration)
        row = sd.known_columns(self.rows, results, 3, self.declaration)[7].values
        self.assertEqual((row["treasury_settlement"], row["treasury_settlement_bills"]), (40.0, 0.0))
        row = sd.known_columns(self.rows, results, 2, self.declaration)[7].values
        self.assertEqual((row["treasury_settlement"], row["treasury_settlement_bills"]), (50.0, 10.0))

    def test_an_announcement_after_its_auction_is_refused(self):
        with self.assertRaises(ValueError) as caught:
            sd.auction_results([record(self.dates[4], self.dates[3], self.dates[7])], self.declaration)
        self.assertIn("announced", str(caught.exception))

    def test_a_record_without_an_announcement_date_is_refused(self):
        bad = record(self.dates[1], self.dates[3], self.dates[7])
        del bad["announcemt_date"]
        with self.assertRaises(ValueError):
            sd.auction_results([bad], self.declaration)

    def test_the_known_coupon_settlement_is_a_risk_date_at_two_or_more(self):
        from repo_model import ml
        from repo_model.evaluation_splits import load_split_declaration

        splits = load_split_declaration(ROOT / "metadata" / "evaluation_splits.json")
        calendar = ("spread_bps", "days_to_month_end", "quarter_end", "tax_date")
        design = ml._RiskDateDesign(calendar + ("treasury_settlement_coupons",), splits)
        ordinary = {"quarter_end": 0.0, "tax_date": 0.0, "days_to_month_end": 12.0}
        for horizon in (2, 3, 4, 5):
            with self.subTest(horizon=horizon):
                row = self.known(horizon)[7]
                values = {**row.values, **ordinary}
                self.assertTrue(design.member(DailyObservation(row.date, values)))
        # The day the announcement has not happened by: not a risk date.
        row = self.known(7)[7]
        self.assertFalse(design.member(DailyObservation(row.date, {**row.values, **ordinary})))

    def test_the_registry_variant_dates_the_columns_at_the_horizon(self):
        registry = load_source_registry(REGISTRY)
        for horizon in (1, 2, 5):
            with self.subTest(horizon=horizon):
                variant = sd.result_dated_registry(registry, self.declaration, horizon)
                block = variant["treasury_auctions"]["scheduled_availability"]
                self.assertEqual((block["days"], block["available_time"]),
                                 (horizon, self.declaration["available_time"]))
                rule = InformationRule(variant, ("spread_bps", "treasury_settlement"),
                                       decision_time=time(16, 0), horizon=horizon)
                info = rule.information_set(self.dates, 7)
                rule.check(self.dates, info)
                read = {r.feature: r for r in info.reads}["treasury_settlement"]
                self.assertEqual(read.row, 7)
                self.assertEqual(read.available_at,
                                 datetime.combine(self.dates[7 - horizon], time.fromisoformat(self.declaration["available_time"])))

    def test_the_published_registry_is_not_touched(self):
        registry = load_source_registry(REGISTRY)
        before = json.dumps(registry, sort_keys=True, default=str)
        sd.result_dated_registry(registry, self.declaration, 3)
        self.assertEqual(json.dumps(registry, sort_keys=True, default=str), before)
        block = registry["treasury_auctions"]["scheduled_availability"]
        self.assertEqual((block["days"], block["available_time"]), (1, "15:00"))


def panel_days(start, end, skip=()):
    out, when = [], start
    while when <= end:
        if when.weekday() < 5 and when not in skip:
            out.append(when)
        when += timedelta(days=1)
    return out


class H41ReleaseTests(unittest.TestCase):
    """The H.4.1 is read per release, at the release's own publication instant (ruling 2).

    A Wednesday level is public at the print, Thursday 16:30 New York time or the actual date when a
    holiday moves it. A forecast reads it from the first decision at or after that instant: the next
    market day's, not before. The staleness guard still holds: a read older than the latest
    admissible value raises `StaleReadError`, and one newer than the decision `LookAheadError`.

    Red first: written before `repo_model.h41_release` existed (`ImportError`).

    Mutation record. In a `git archive` copy of the tree under /tmp, CPython 3.11
    (`/opt/rmm-venv`), this class run alone, unmutated control green. In `h41_release.release_instant`, the
    declared print time `time.fromisoformat(str(calendar["available_time"]))` was mutated to
    `time.fromisoformat("00:00")` (a Wednesday level treated as public at midnight on its release
    day). The target was found once before the change and was gone after. Killed, 5 failures, all
    `AssertionError`: `test_a_wednesday_level_is_readable_on_the_next_market_days_decision` (`datetime(2024, 3,
    7, 0, 0) != datetime(2024, 3, 7, 16, 30)`), `test_a_wednesday_level_is_not_readable_before_its_print`
    (`date(2024, 3, 6) != date(2024, 2, 28)`), `test_a_holiday_moves_the_print_to_the_actual_date`,
    `test_a_weekly_value_is_dated_by_its_observation_not_its_carry` and `test_the_leakage_guard_still_holds`
    (`LookAheadError not raised`).
    """

    def setUp(self):
        patch = h41.release_dating()
        patch.__enter__()
        self.addCleanup(patch.__exit__, None, None, None)
        self.declaration = h41.load_release_dating(H41)
        self.registry = h41.release_dated_registry(load_source_registry(REGISTRY), self.declaration)
        # An ordinary week: Wednesday 2024-03-06 is printed on Thursday 2024-03-07 at 16:30.
        self.dates = panel_days(date(2024, 2, 26), date(2024, 3, 22))

    def rule(self, horizon=1):
        return InformationRule(self.registry, ("spread_bps", "reserve_balances"),
                               decision_time=time(16, 0), horizon=horizon)

    def read(self, rule, dates, when):
        info = rule.information_set(dates, dates.index(when))
        rule.check(dates, info)
        return {r.feature: r for r in info.reads}["reserve_balances"]

    def test_the_declaration_is_off_and_names_the_print(self):
        self.assertIn("off", self.declaration["status"])
        self.assertEqual(self.declaration["available_time"], "16:30")
        self.assertEqual(self.declaration["offset_days"], 1)
        self.assertEqual(sorted(self.declaration["fields"]), ["WLRRAOL", "WRESBAL", "WTREGEN"])

    @staticmethod
    def level(read, dates):
        """The Wednesday whose level the read row carries."""

        row = dates[read.row]
        return row - timedelta(days=(row.weekday() - 2) % 7)

    def test_a_wednesday_level_is_readable_on_the_next_market_days_decision(self):
        # The print is Thursday 2024-03-07 16:30; the first decision at or after it is Friday 03-08 16:00,
        # which forecasts Monday 03-11.
        read = self.read(self.rule(), self.dates, date(2024, 3, 11))
        self.assertEqual(self.level(read, self.dates), date(2024, 3, 6))
        self.assertEqual(read.available_at, datetime(2024, 3, 7, 16, 30))

    def test_a_wednesday_level_is_not_readable_before_its_print(self):
        # Thursday 03-07 16:00 is half an hour before the print: the forecast of Friday 03-08 reads last week's.
        read = self.read(self.rule(), self.dates, date(2024, 3, 8))
        self.assertEqual(self.level(read, self.dates), date(2024, 2, 28))
        self.assertEqual(read.available_at, datetime(2024, 2, 29, 16, 30))

    def test_the_published_declaration_reads_the_same_level_two_panel_days_later(self):
        published = InformationRule(load_source_registry(REGISTRY), ("spread_bps", "reserve_balances"),
                                    decision_time=time(16, 0), horizon=1)
        for scored, wednesday in ((date(2024, 3, 11), date(2024, 2, 28)), (date(2024, 3, 12), date(2024, 2, 28)),
                                  (date(2024, 3, 13), date(2024, 3, 6))):
            read = self.read(published, self.dates, scored)
            self.assertEqual(self.level(read, self.dates), wednesday, scored)

    def test_a_holiday_moves_the_print_to_the_actual_date(self):
        # Thanksgiving 2024: the week of Wednesday 11-27 is printed on Friday 11-29 (the Board's archive),
        # not on Thursday 11-28.
        dates = panel_days(date(2024, 11, 18), date(2024, 12, 6), skip=(date(2024, 11, 28),))
        rule = self.rule()
        read = self.read(rule, dates, date(2024, 12, 2))  # decision Friday 11-29 16:00, before the 16:30 print
        self.assertEqual(self.level(read, dates), date(2024, 11, 20))
        self.assertEqual(read.available_at, datetime(2024, 11, 21, 16, 30))
        read = self.read(rule, dates, date(2024, 12, 3))  # decision Monday 12-02
        self.assertEqual(self.level(read, dates), date(2024, 11, 27))
        self.assertEqual(read.available_at, datetime(2024, 11, 29, 16, 30))

    def test_a_weekly_value_is_dated_by_its_observation_not_its_carry(self):
        # Every panel row carrying the 03-06 level is available at the one print instant.
        calendar = self.registry["fred_macro_latest_vintage"]["release_calendar"]
        for row in (date(2024, 3, 6), date(2024, 3, 8), date(2024, 3, 12)):
            when = asof.declared_availability(self.registry, "fred_macro_latest_vintage", "WRESBAL",
                                                  [row], 0)
            self.assertEqual(when, datetime(2024, 3, 7, 16, 30), row)
        self.assertEqual(calendar["available_time"], "16:30")

    def test_the_staleness_guard_still_holds(self):
        rule, dates = self.rule(), self.dates
        scored = dates.index(date(2024, 3, 11))
        info = rule.information_set(dates, scored)
        index = [r.feature for r in info.reads].index("reserve_balances")
        old = dates.index(date(2024, 3, 7))  # the Thursday row: not yet printed at that row's own decision
        reads = list(info.reads)
        # a read of last week's level while this week's was public
        reads[index] = reads[index]._replace(row=dates.index(date(2024, 3, 5)))
        with self.assertRaises(StaleReadError):
            rule.check(dates, info._replace(reads=tuple(reads)))
        self.assertLess(old, scored)

    def test_the_leakage_guard_still_holds(self):
        rule, dates = self.rule(), self.dates
        scored = dates.index(date(2024, 3, 8))  # decision Thursday 03-07 16:00, before the print
        info = rule.information_set(dates, scored)
        index = [r.feature for r in info.reads].index("reserve_balances")
        reads = list(info.reads)
        reads[index] = reads[index]._replace(row=dates.index(date(2024, 3, 7)))  # the row carrying the new level
        with self.assertRaises(LookAheadError):
            rule.check(dates, info._replace(reads=tuple(reads)))

    def test_every_exception_is_a_later_weekday_than_the_default(self):
        for wednesday, published in self.declaration["exceptions"].items():
            observed, printed = date.fromisoformat(wednesday), date.fromisoformat(published)
            self.assertEqual(observed.weekday(), 2, wednesday)
            self.assertLess(printed.weekday(), 5, published)
            self.assertGreater(printed, observed + timedelta(days=self.declaration["offset_days"]), wednesday)

    def test_the_as_of_rule_is_restored_on_the_way_out(self):
        patched = asof.declared_availability
        with h41.release_dating():
            pass  # nested: restores the patched functions of setUp, not the originals
        self.assertIs(asof.declared_availability, patched)
        with self.assertRaises(RuntimeError), h41.release_dating():
            raise RuntimeError("raised inside")
        self.assertIs(asof.declared_availability, patched)

    def test_the_decision_relative_guard_reads_the_same_instants(self):
        from repo_model import baseline

        self.assertIs(baseline._declared_availability, asof.declared_availability)

    def test_a_registry_with_no_calendar_is_read_as_before(self):
        published = load_source_registry(REGISTRY)
        dates = self.dates
        moment = asof.declared_availability(published, "fred_macro_latest_vintage", "WRESBAL", dates, 5)
        self.assertEqual(moment, datetime.combine(dates[5] + timedelta(days=5), time(16, 30)))

    def test_the_published_registry_is_not_touched(self):
        registry = load_source_registry(REGISTRY)
        before = json.dumps(registry, sort_keys=True, default=str)
        h41.release_dated_registry(registry, self.declaration)
        self.assertEqual(json.dumps(registry, sort_keys=True, default=str), before)
        self.assertNotIn("release_calendar", registry["fred_macro_latest_vintage"])
        self.assertEqual(registry["fred_macro_latest_vintage"]["field_release_lags"]["WRESBAL"]["days"], 5)

    def test_only_the_declared_fields_move(self):
        base = load_source_registry(REGISTRY)["fred_macro_latest_vintage"]
        variant = self.registry["fred_macro_latest_vintage"]
        self.assertEqual(variant["field_release_lags"], base["field_release_lags"])
        self.assertEqual(variant["release_calendar"]["fields"], ["WLRRAOL", "WRESBAL", "WTREGEN"])


class H41CoverageTests(unittest.TestCase):
    """`release_instant` refuses a week the declaration does not cover (#576).

    The calendar assumed a Thursday print for every week not in `exceptions`, so a week past the
    declared `covers` (the week ended 31 December 2025, released Friday 2 January 2026; Thanksgiving
    week 2026) was dated one release early. Now a week whose Wednesday is outside
    `first_wednesday` .. `last_wednesday` raises `ValueError`; the two weeks the Board's pages verified
    are declared.

    Red first: written before the guard, the out-of-range weeks returned an instant and
    `ValueError not raised` failed these tests.

    Mutation record. In a `git archive` copy of the tree under /tmp, CPython 3.11 (`/opt/rmm-venv`),
    this class run alone, unmutated control green. In `h41_release.release_instant` the guard line
    `if not (first <= observed <= last):` was mutated to `if False:`. Killed:
    `test_a_week_after_the_last_declared_wednesday_is_refused`,
    `test_a_week_before_the_first_declared_wednesday_is_refused` and
    `test_thanksgiving_week_2026_is_refused_until_it_is_covered` failed with
    `AssertionError: ValueError not raised`.
    """

    def setUp(self):
        self.declaration = h41.load_release_dating(H41)
        registry = h41.release_dated_registry(load_source_registry(REGISTRY), self.declaration)
        self.calendar = registry["fred_macro_latest_vintage"]["release_calendar"]

    def test_the_week_ended_31_december_2025_is_released_on_friday_2_january(self):
        # Thursday 1 January 2026 is a federal holiday; the Board's page for it is 404.
        for row in (date(2025, 12, 31), date(2026, 1, 1), date(2026, 1, 2)):
            self.assertEqual(h41.release_instant(self.calendar, row), datetime(2026, 1, 2, 16, 30))

    def test_the_declaration_covers_exactly_as_far_as_its_evidence(self):
        self.assertEqual(self.declaration["covers"], {"first_wednesday": "2018-03-28", "last_wednesday": "2026-09-02"})

    def test_a_week_after_the_last_declared_wednesday_is_refused(self):
        with self.assertRaises(ValueError) as caught:
            h41.release_instant(self.calendar, date(2026, 9, 9))
        self.assertIn("2026-09-09", str(caught.exception))

    def test_a_week_before_the_first_declared_wednesday_is_refused(self):
        with self.assertRaises(ValueError):
            h41.release_instant(self.calendar, date(2018, 3, 27))
        h41.release_instant(self.calendar, date(2018, 3, 28))

    def test_thanksgiving_week_2026_is_refused_until_it_is_covered(self):
        self.assertEqual(self.declaration["exceptions"]["2026-11-25"], "2026-11-27")
        with self.assertRaises(ValueError):
            h41.release_instant(self.calendar, date(2026, 11, 25))

    def test_every_exception_inside_coverage_is_still_dated_as_declared(self):
        self.assertEqual(h41.release_instant(self.calendar, date(2025, 11, 26)), datetime(2025, 11, 28, 16, 30))
        self.assertEqual(h41.release_instant(self.calendar, date(2025, 12, 24)), datetime(2025, 12, 29, 16, 30))

    def test_a_declaration_without_ordered_coverage_is_refused(self):
        import tempfile

        bad = dict(self.declaration, covers={"first_wednesday": "2025-12-31", "last_wednesday": "2018-03-28"})
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "d.json"
            path.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaises(ValueError):
                h41.load_release_dating(path)


class H41CalendarThrough3September2026Tests(unittest.TestCase):
    """The calendar dates every weekday of the 2026 window, and still refuses past it (#625, ruling on #614).

    #614 found `release_instant` dating 3 and refusing 172 of the weekdays 2026-01-02 to 2026-09-03
    because `covers.last_wednesday` was 2025-12-31. Extending the coverage to Wednesday 2026-09-02
    (the last H.4.1 week inside the window) is checked here against the Board's release pages,
    www.federalreserve.gov/releases/h41/<date>/, fetched 12 October 2026: the pages of all 35 Thursdays from
    2026-01-08 to 2026-09-03 exist and state those dates, so no 2026 week inside the window is an
    exception. The guard of #576 is unchanged. Rows 2026-09-04 to 2026-09-08 carry the 2 September
    level (weekly carry) and are dated by its 3 September print; the first refused row is 2026-09-09.

    Red first: against `covers.last_wednesday = 2025-12-31` these tests raised `ValueError` on 2026-01-07.

    Mutation record. In a `git archive` copy of the tree under /tmp, this class run alone, unmutated
    control green. `covers.last_wednesday` in `metadata/h41_release_dating.json` was mutated from
    `2026-09-02` back to `2025-12-31`. Killed: `test_every_weekday_of_the_window_is_dated`,
    `test_each_2026_week_is_released_on_its_thursday_except_the_declared` and
    `test_the_last_week_of_the_window_prints_on_3_september` failed with `ValueError` (the H.4.1
    week of Wednesday 2026-01-07 is outside the declared coverage).
    """

    def setUp(self):
        self.declaration = h41.load_release_dating(H41)
        registry = h41.release_dated_registry(load_source_registry(REGISTRY), self.declaration)
        self.calendar = registry["fred_macro_latest_vintage"]["release_calendar"]

    def test_every_weekday_of_the_window_is_dated(self):
        day, dated = date(2026, 1, 2), 0
        while day <= date(2026, 9, 3):
            if day.weekday() < 5:
                h41.release_instant(self.calendar, day)
                dated += 1
            day += timedelta(days=1)
        self.assertGreater(dated, 170)

    def test_each_2026_week_is_released_on_its_thursday_except_the_declared(self):
        wednesday = date(2026, 1, 7)
        while wednesday <= date(2026, 9, 2):
            expected = self.declaration["exceptions"].get(wednesday.isoformat())
            printed = date.fromisoformat(expected) if expected else wednesday + timedelta(days=1)
            self.assertEqual(h41.release_instant(self.calendar, wednesday), datetime.combine(printed, time(16, 30)))
            wednesday += timedelta(days=7)
        self.assertEqual(
            sorted(w for w in self.declaration["exceptions"] if "2026-01-02" <= w <= "2026-09-02"), []
        )

    def test_the_last_week_of_the_window_prints_on_3_september(self):
        for row in (date(2026, 9, 2), date(2026, 9, 3), date(2026, 9, 4), date(2026, 9, 8)):
            self.assertEqual(h41.release_instant(self.calendar, row), datetime(2026, 9, 3, 16, 30))

    def test_the_week_after_the_window_is_refused(self):
        for row in (date(2026, 9, 9), date(2026, 9, 10), date(2026, 12, 31)):
            with self.assertRaises(ValueError):
                h41.release_instant(self.calendar, row)

    def test_the_lockbox_is_unchanged_by_the_calendar(self):
        # metadata/lockbox.json is not touched by #625: the blind tier (from 2026-09-04) is still locked.
        from repo_model.lockbox import require_unlocked

        require_unlocked([date(2026, 9, 3)], where="h41 calendar test")
        with self.assertRaises(LookAheadError):
            require_unlocked([date(2026, 9, 4)], where="h41 calendar test")


if __name__ == "__main__":
    unittest.main()
