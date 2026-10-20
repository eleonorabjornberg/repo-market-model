"""The FOMC meeting calendar, read at the target day only when it was public (#1038).

`metadata/fomc_calendar.json` is built from the Board's own pages by `scripts/build_fomc_calendar.py`;
`repo_model.fomc_calendar` turns it into `fomc_meeting_day` and `fomc_days_to_next_meeting` for a target day,
read at the decision instant (rule 2 of `asof.py`). Off in every published declaration.

Mutation record
---------------
Run in a scratch copy of the tree, with the mutated line confirmed applied by grep and restored before the next.

1. `visible_at`: `meeting.public_at <= as_of` mutated to `True` (every meeting visible whatever its schedule's
   publication). Ten tests fail: eight with `LookAheadError` from the
   explicit `require_public` loop in `fomc_feature_values` (for example
   `test_both_days_of_a_meeting_are_meeting_days`,
   `test_an_announcement_after_the_decision_instant_changes_nothing`), two with `AssertionError`
   (`test_a_meeting_is_invisible_before_its_schedules_release_and_visible_from_it`,
   `test_an_unscheduled_meeting_is_public_from_its_own_announcement_only`).
2. `require_public`: `if meeting.public_at > as_of:` mutated to `if meeting.public_at.date() > as_of.date():` (the
   guard compares days, not instants). Two tests fail with `AssertionError: LookAheadError not
   raised` (`test_the_guard_compares_instants_not_days`,
   `test_a_meeting_is_invisible_before_its_schedules_release_and_visible_from_it`).
3. `visible_at`: the cancellation clause `meeting.cancelled_at is None or meeting.cancelled_at > as_of` mutated to
   `meeting.cancelled_at is None` (a cancelled meeting is never dropped). Three tests fail with `AssertionError`
   (`test_a_cancelled_meeting_stops_being_visible_from_its_cancellation`,
   `test_the_cancelled_meeting_is_a_meeting_day_until_its_cancellation_is_public`,
   `test_rows_are_read_at_the_decision_instant_of_the_day_horizon_days_before`).
"""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from datetime import date, datetime, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model import contract, fomc_calendar as fc, measurement_fields  # noqa: E402
from repo_model.data import DailyObservation  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

PATH = ROOT / "metadata" / "fomc_calendar.json"
DOCUMENT = json.loads(PATH.read_text(encoding="utf-8"))


def at(day: str, clock: str = "16:00") -> datetime:
    return datetime.combine(date.fromisoformat(day), time.fromisoformat(clock))


def meeting(calendar, start: str):
    return next(m for m in calendar if m.start == date.fromisoformat(start))


def script():
    spec = importlib.util.spec_from_file_location("build_fomc_calendar", ROOT / "scripts" / "build_fomc_calendar.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DatingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.calendar = fc.load_calendar(PATH)

    def test_a_meeting_is_public_from_the_earliest_schedule_that_lists_it(self):
        # 29 January 2019 is the last line of the 2018 schedule (11 May 2017) and the first of the 2019 one.
        self.assertEqual(meeting(self.calendar, "2019-01-29").public_at, at("2017-05-11", "14:00"))
        self.assertEqual(meeting(self.calendar, "2019-03-19").public_at, at("2018-05-25", "12:00"))
        self.assertEqual(meeting(self.calendar, "2026-03-17").public_at, at("2024-08-09", "13:30"))

    def test_a_meeting_is_invisible_before_its_schedules_release_and_visible_from_it(self):
        march = meeting(self.calendar, "2019-03-19")
        self.assertFalse(fc.visible_at(march, at("2018-05-25", "11:59")))
        self.assertTrue(fc.visible_at(march, at("2018-05-25", "12:00")))
        with self.assertRaises(LookAheadError):
            fc.require_public(march, at("2018-05-25", "11:59"))
        self.assertIs(fc.require_public(march, at("2018-05-25", "12:00")), march)

    def test_the_guard_compares_instants_not_days(self):
        # Released at 12:00 on 25 May 2018: a decision at 09:00 that day is before it.
        with self.assertRaises(LookAheadError):
            fc.require_public(meeting(self.calendar, "2019-03-19"), at("2018-05-25", "09:00"))

    def test_an_unscheduled_meeting_is_public_from_its_own_announcement_only(self):
        october = meeting(self.calendar, "2019-10-04")
        self.assertEqual(october.kind, "unscheduled")
        self.assertEqual(october.public_at, at("2019-10-11", "11:00"))
        self.assertFalse(fc.visible_at(october, at("2019-10-10")))
        self.assertTrue(fc.visible_at(october, at("2019-10-11", "11:00")))
        march = meeting(self.calendar, "2020-03-15")
        self.assertFalse(fc.visible_at(march, at("2020-03-14")))
        with self.assertRaises(LookAheadError):
            fc.require_public(march, at("2020-03-14"))

    def test_a_cancelled_meeting_stops_being_visible_from_its_cancellation(self):
        cancelled = meeting(self.calendar, "2020-03-17")
        self.assertEqual(cancelled.cancelled_at, at("2020-03-15", "17:00"))
        self.assertTrue(fc.visible_at(cancelled, at("2020-03-13")))
        self.assertTrue(fc.visible_at(cancelled, at("2020-03-15", "16:59")))
        self.assertFalse(fc.visible_at(cancelled, at("2020-03-15", "17:00")))
        self.assertFalse(fc.visible_at(cancelled, at("2020-03-16")))

    def test_notation_votes_are_not_meetings(self):
        starts = {m.start for m in self.calendar}
        for vote in DOCUMENT["notation_votes"]:
            self.assertNotIn(date.fromisoformat(vote["date"]), starts)
        self.assertEqual(len(DOCUMENT["notation_votes"]), 5)

    def test_every_meeting_has_a_start_no_later_than_its_end_and_a_unique_id(self):
        ids = [m.id for m in self.calendar]
        self.assertEqual(len(ids), len(set(ids)))
        for m in self.calendar:
            self.assertLessEqual(m.start, m.end)
            if m.kind == "scheduled":
                self.assertLessEqual(m.public_at.date(), m.start)


class ColumnTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.calendar = fc.load_calendar(PATH)

    def values(self, target: str, as_of: datetime):
        return fc.fomc_feature_values(self.calendar, date.fromisoformat(target), as_of)

    def test_both_days_of_a_meeting_are_meeting_days(self):
        for target in ("2019-01-29", "2019-01-30"):
            self.assertEqual(self.values(target, at("2019-01-28"))["fomc_meeting_day"], 1.0)
        for target in ("2019-01-28", "2019-01-31"):
            self.assertEqual(self.values(target, at("2019-01-25"))["fomc_meeting_day"], 0.0)

    def test_days_to_the_next_meeting_count_to_its_first_day(self):
        self.assertEqual(self.values("2019-02-01", at("2019-01-31"))["fomc_days_to_next_meeting"], 46.0)
        self.assertEqual(self.values("2019-03-19", at("2019-03-18"))["fomc_days_to_next_meeting"], 0.0)
        # on the second day of a meeting the next meeting is the following one
        self.assertEqual(self.values("2019-03-20", at("2019-03-19"))["fomc_days_to_next_meeting"], 41.0)

    def test_a_meeting_whose_schedule_is_not_yet_public_is_not_counted(self):
        # 2019-03-19 first appears on 2018-05-25 at 12:00; read before it, the target is an ordinary day.
        # 2018-05-25 itself is still covered by the 2018 schedule, which stops at January 2019.
        before = self.values("2019-03-19", at("2018-05-25", "11:00"))
        after = self.values("2019-03-19", at("2018-05-25", "12:00"))
        self.assertEqual(before["fomc_meeting_day"], 0.0)
        self.assertEqual(after["fomc_meeting_day"], 1.0)

    def test_an_announcement_after_the_decision_instant_changes_nothing(self):
        as_of = at("2018-05-24")
        mutated = copy.deepcopy(DOCUMENT)
        for entry in mutated["schedule_announcements"]:
            if entry["announced_date"] > "2018-05-24":
                entry["meetings"] = [{"start": "2031-06-04", "end": "2031-06-05"}]  # nonsense nobody had seen
        mutated["cancellations"] = []  # its meeting is among those dropped
        altered = fc.parse_calendar(mutated, "mutated")
        for target in ("2018-06-12", "2018-12-19", "2019-01-29", "2019-02-14"):
            day = date.fromisoformat(target)
            self.assertEqual(fc.fomc_feature_values(self.calendar, day, as_of), fc.fomc_feature_values(altered, day, as_of))

    def test_a_calendar_that_leaks_is_refused_by_the_explicit_guard(self):
        leaky = fc.load_calendar(PATH)
        later = [m for m in leaky if m.public_at > at("2018-05-24")]
        self.assertTrue(later)
        with mock_visible_everything():
            with self.assertRaises(LookAheadError):
                fc.fomc_feature_values(leaky, date(2019, 3, 19), at("2018-05-24"))

    def test_the_cancelled_meeting_is_a_meeting_day_until_its_cancellation_is_public(self):
        self.assertEqual(self.values("2020-03-17", at("2020-03-13"))["fomc_meeting_day"], 1.0)
        self.assertEqual(self.values("2020-03-17", at("2020-03-16"))["fomc_meeting_day"], 0.0)
        self.assertEqual(self.values("2020-03-18", at("2020-03-17"))["fomc_meeting_day"], 0.0)

    def test_an_unscheduled_meeting_is_a_meeting_day_only_once_announced(self):
        self.assertEqual(self.values("2019-10-04", at("2019-10-03"))["fomc_meeting_day"], 0.0)
        # a read made after the target day is refused (the decision is never later than its target), so the
        # announced meeting is seen through the filter, as a later analysis of the day would
        self.assertTrue(fc.visible_at(meeting(self.calendar, "2019-10-04"), at("2019-10-15")))

    def test_a_decision_after_the_target_day_is_refused(self):
        with self.assertRaises(ValueError):
            self.values("2019-01-29", at("2019-01-30"))

    def test_a_decision_before_the_first_schedule_is_refused_not_read_as_empty(self):
        with self.assertRaises(ValueError):
            self.values("2017-06-01", at("2017-05-10"))

    def test_an_aware_datetime_is_refused(self):
        from datetime import timezone

        with self.assertRaises(ValueError):
            fc.fomc_feature_values(self.calendar, date(2019, 1, 29), datetime(2019, 1, 28, 16, tzinfo=timezone.utc))

    def test_days_to_next_is_never_missing(self):
        value = self.values("2027-12-20", at("2027-12-19"))["fomc_days_to_next_meeting"]
        self.assertEqual(value, 36.0)  # 25 January 2028, the last line of the 2027 release

    def test_rows_are_read_at_the_decision_instant_of_the_day_horizon_days_before(self):
        rows = [DailyObservation(date(2020, 3, d), {"x": float(d)}) for d in (12, 13, 16, 17, 18)]
        out = fc.add_columns(rows, self.calendar)
        by_day = {r.date.day: r.values["fomc_meeting_day"] for r in out}
        # read on the previous panel row's 16:00: 17 March reads 16 March 16:00, after the 15 March 17:00 cancellation
        self.assertEqual(by_day[17], 0.0)
        # 16 March reads 13 March 16:00: the meeting is still scheduled but 16 March is not a meeting day
        self.assertEqual(by_day[16], 0.0)
        later = fc.add_columns(rows, self.calendar, horizon=3)
        self.assertEqual({r.date.day: r.values["fomc_meeting_day"] for r in later}[17], 1.0)
        for row, original in zip(out, rows):
            self.assertEqual(row.values["x"], original.values["x"])
        self.assertEqual(len(rows[0].values), 1, "the input rows are not changed")

    def test_a_row_does_not_depend_on_the_rows_after_it(self):
        rows = [DailyObservation(date(2019, 1, d), {}) for d in (25, 28, 29, 30, 31)]
        whole = fc.add_columns(rows, self.calendar)
        prefix = fc.add_columns(rows[:3], self.calendar)
        self.assertEqual([r.values for r in whole[:3]], [r.values for r in prefix])


class mock_visible_everything:
    """Replace `visible_at` for a block, so the explicit guard is what must refuse a meeting not yet public."""

    def __enter__(self):
        self.saved = fc.visible_at
        fc.visible_at = lambda meeting, as_of: True
        return self

    def __exit__(self, *exc):
        fc.visible_at = self.saved


class RefusalTests(unittest.TestCase):
    def parse(self, mutate):
        document = copy.deepcopy(DOCUMENT)
        mutate(document)
        return fc.parse_calendar(document, "test")

    def test_a_meeting_that_ends_before_it_starts_is_refused(self):
        def mutate(d):
            d["schedule_announcements"][0]["meetings"][0]["end"] = "2018-01-29"

        with self.assertRaises(ValueError):
            self.parse(mutate)

    def test_one_meeting_with_two_end_dates_is_refused(self):
        def mutate(d):
            d["schedule_announcements"][1]["meetings"][0]["end"] = "2019-01-31"

        with self.assertRaises(ValueError):
            self.parse(mutate)

    def test_a_meeting_dated_before_its_announcement_is_refused(self):
        def mutate(d):
            d["schedule_announcements"][0]["announced_date"] = "2018-02-01"

        with self.assertRaises(ValueError):
            self.parse(mutate)

    def test_a_cancellation_of_an_unknown_meeting_is_refused(self):
        def mutate(d):
            d["cancellations"][0]["meeting_start"] = "2020-03-16"

        with self.assertRaises(ValueError):
            self.parse(mutate)

    def test_a_cancellation_before_the_meeting_was_public_is_refused(self):
        def mutate(d):
            d["cancellations"][0]["announced_date"] = "2019-01-01"

        with self.assertRaises(ValueError):
            self.parse(mutate)

    def test_a_source_that_is_not_https_is_refused(self):
        def mutate(d):
            d["schedule_announcements"][0]["source_url"] = "http://www.federalreserve.gov/x"

        with self.assertRaises(ValueError):
            self.parse(mutate)


class SourceTests(unittest.TestCase):
    def test_the_tracked_register_is_what_the_tracked_pages_give(self):
        self.assertEqual(script().render(), PATH.read_text(encoding="utf-8"))

    def test_every_tracked_page_matches_its_manifest(self):
        import hashlib

        manifest = json.loads((ROOT / "tests" / "fixtures" / "snapshots" / "fomc_calendar" / "manifest.json").read_text())
        for page in manifest["pages"]:
            payload = (ROOT / "tests" / "fixtures" / "snapshots" / "fomc_calendar" / page["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(payload).hexdigest(), page["sha256"], page["path"])
            self.assertEqual(len(payload), page["byte_count"], page["path"])

    def test_the_scheduled_meetings_are_the_boards_calendar_pages(self):
        module = script()
        held = {(a, b) for rows in module.calendar_page_events().values() for a, b, s in rows if s in ("held", "cancelled")}
        calendar = fc.load_calendar(PATH)
        ours = {
            (m.start, m.end)
            for m in fc.load_calendar(PATH)
            if m.kind == "scheduled" and date(2018, 1, 1) <= m.start <= date(2026, 9, 16)
        }
        self.assertTrue(ours <= held, sorted(ours - held))
        self.assertGreaterEqual(len(ours), 70)

    def test_every_column_is_a_field_of_the_declared_source(self):
        source = measurement_fields.load_registry()[fc.SOURCE_ID]
        self.assertEqual(sorted(source["fields"]), sorted(fc.COLUMNS))
        self.assertEqual(sorted(fc.COLUMN_FIELDS), sorted(fc.COLUMNS))
        for column, pairs in fc.COLUMN_FIELDS.items():
            self.assertEqual(pairs, ((fc.SOURCE_ID, column),))

    def test_the_source_is_off_in_the_published_registry_and_feature_map(self):
        published = json.loads((ROOT / "metadata" / "sources.json").read_text())
        self.assertNotIn(fc.SOURCE_ID, published)
        for column in fc.COLUMNS:
            self.assertNotIn(column, contract.FEATURE_FIELDS)

    def test_the_source_is_available_at_the_decision_instant_of_its_own_row(self):
        lag = measurement_fields.load_registry()[fc.SOURCE_ID]["release_lag"]
        self.assertEqual((lag["days"], lag["available_time"], lag["timezone"]), (0, "16:00", "America/New_York"))


if __name__ == "__main__":
    unittest.main()
