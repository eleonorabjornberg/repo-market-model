"""The availability poll's catch-up run and its missed-day file (#1441, from finding #1435).

A run after the 18:30 ET window records the first `latest_date` it sees, marked `catch_up`, with its true fetch
time. It bounds the posting time from above and is never an in-window sample. A business day with no in-window
record is a missed day and must be on `metadata/availability_missed_days.json`. No test fetches: every poll takes a
fake fetcher.

Mutations (4 Nov 2026; availability bookkeeping, recorded for the reviewer):
* in `capture`, writing the late record with `kind=IN_WINDOW` instead of `CATCH_UP` made
  `test_a_run_after_the_window_writes_a_catch_up_record` fail with `AssertionError: Lists differ: ['in_window'] != ['catch_up']`.
* in `unlisted_misses`, `if r["kind"] == IN_WINDOW` changed to `if r` (any record counts as in-window) made
  `test_a_catch_up_only_day_is_still_missed` fail with `AssertionError: Lists differ: [] != [datetime.date(2026, 11, 3)]`.
"""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from repo_model import availability_poll as ap

ROOT = Path(__file__).resolve().parents[1]
UTC = timezone.utc
EST, EDT = timezone(timedelta(hours=-5)), timezone(timedelta(hours=-4))
CSV = b"Date,4 Mo\n11/03/2026,3.5\n11/02/2026,3.6\n"
LIST = ROOT / "metadata" / "availability_missed_days.json"


def at(y, m, d, h, mi, tz):
    return datetime(y, m, d, h, mi, tzinfo=tz)


def fake(status=200, body=CSV):
    calls = []

    def fetcher(url):
        calls.append(url)
        return status, body, None

    fetcher.calls = calls
    return fetcher


def script():
    spec = importlib.util.spec_from_file_location("availability_poll_script", ROOT / "scripts" / "availability_poll.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CatchUpTests(unittest.TestCase):
    def setUp(self):
        self.script = script()

    def test_a_run_after_the_window_writes_a_catch_up_record(self):
        now = at(2026, 11, 3, 21, 32, EST)  # the 3 November run: 21:32 ET, three hours after the window
        fetcher = fake()
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.script.capture(Path(tmp), now, fetcher, clock=lambda: now)
            records = ap.read_all(Path(tmp))
        self.assertEqual(len(paths), 1)
        self.assertEqual([r["kind"] for r in records], [ap.CATCH_UP])
        self.assertEqual(records[0]["fetched_at"], "2026-11-04T02:32:00+00:00")  # its true fetch time
        self.assertEqual((records[0]["et_date"], records[0]["latest_date"]), ("2026-11-03", "2026-11-03"))

    def test_an_in_window_run_is_still_in_window(self):
        now = at(2026, 11, 3, 17, 30, EST)
        with tempfile.TemporaryDirectory() as tmp:
            self.script.capture(Path(tmp), now, fake(), clock=lambda: now)
            self.assertEqual([r["kind"] for r in ap.read_all(Path(tmp))], [ap.IN_WINDOW])

    def test_the_first_sight_only_a_second_late_run_adds_nothing(self):
        first, second = at(2026, 11, 3, 19, 0, EST), at(2026, 11, 3, 21, 32, EST)
        fetcher = fake()
        with tempfile.TemporaryDirectory() as tmp:
            self.script.capture(Path(tmp), first, fetcher, clock=lambda: first)
            self.assertEqual(self.script.capture(Path(tmp), second, fetcher, clock=lambda: second), [])
            self.assertEqual(len(ap.read_all(Path(tmp))), 1)
        self.assertEqual(len(fetcher.calls), 1)

    def test_a_day_with_an_in_window_record_needs_no_catch_up(self):
        early, late = at(2026, 11, 3, 17, 30, EST), at(2026, 11, 3, 21, 32, EST)
        fetcher = fake()
        with tempfile.TemporaryDirectory() as tmp:
            self.script.capture(Path(tmp), early, fetcher, clock=lambda: early)
            self.assertEqual(self.script.capture(Path(tmp), late, fetcher, clock=lambda: late), [])
        self.assertEqual(len(fetcher.calls), 1)

    def test_thursday_catches_up_both_sources_each_once(self):
        now = at(2026, 11, 5, 20, 0, EST)  # a Thursday
        with tempfile.TemporaryDirectory() as tmp:
            self.script.capture(Path(tmp), now, fake(), clock=lambda: now)
            records = ap.read_all(Path(tmp))
        self.assertEqual({(r["source"], r["kind"]) for r in records},
                         {(ap.TREASURY, ap.CATCH_UP), (ap.FR2004, ap.CATCH_UP)})

    def test_weekend_holiday_and_before_the_window_catch_up_nothing(self):
        for now in (at(2026, 11, 7, 21, 0, EST), at(2026, 11, 26, 21, 0, EST), at(2026, 11, 3, 12, 0, EST)):
            with self.subTest(now=now.isoformat()):
                fetcher = fake()
                with tempfile.TemporaryDirectory() as tmp:
                    self.assertEqual(self.script.capture(Path(tmp), now, fetcher), [])
                self.assertEqual(fetcher.calls, [])

    def test_a_failed_late_poll_is_a_catch_up_record_and_does_not_block_the_next(self):
        first, second = at(2026, 11, 3, 19, 0, EST), at(2026, 11, 3, 20, 0, EST)
        with tempfile.TemporaryDirectory() as tmp:
            self.script.capture(Path(tmp), first, fake(status=503, body=b""), clock=lambda: first)
            self.script.capture(Path(tmp), second, fake(), clock=lambda: second)
            records = ap.read_all(Path(tmp))
        self.assertEqual([(r["kind"], r["status"]) for r in records], [(ap.CATCH_UP, 503), (ap.CATCH_UP, 200)])

    def test_the_record_names_its_kind(self):
        rec = ap.poll_record(ap.TREASURY, at(2026, 11, 3, 17, 0, EST), fake())
        self.assertEqual(rec["kind"], ap.IN_WINDOW)
        for bad in ({**rec, "kind": "late"}, {k: v for k, v in rec.items() if k != "kind"}):
            with self.subTest(bad=bad.get("kind")), self.assertRaises(ValueError):
                ap.check_record(bad)


def rec(day, kind, source=ap.TREASURY):
    now = datetime.combine(day, datetime.min.time().replace(hour=17 if kind == ap.IN_WINDOW else 21), EST)
    return ap.poll_record(source, now, fake(), clock=lambda: now, kind=kind)


class MissedDayTests(unittest.TestCase):
    TODAY = date(2026, 11, 6)  # Friday: 3, 4 and 5 November are the days that are over

    def test_a_day_with_no_record_is_missed(self):
        records = [rec(date(2026, 11, 3), ap.IN_WINDOW), rec(date(2026, 11, 5), ap.IN_WINDOW)]
        self.assertEqual(ap.unlisted_misses(records, self.TODAY, {}), [date(2026, 11, 4)])

    def test_a_catch_up_only_day_is_still_missed(self):
        records = [rec(date(2026, 11, 3), ap.CATCH_UP), rec(date(2026, 11, 4), ap.IN_WINDOW),
                   rec(date(2026, 11, 5), ap.IN_WINDOW)]
        self.assertEqual(ap.unlisted_misses(records, self.TODAY, {}), [date(2026, 11, 3)])

    def test_a_listed_day_is_not_reported_again(self):
        listed = {date(2026, 11, 3): {"reason": "x"}}
        self.assertEqual(ap.unlisted_misses([rec(date(2026, 11, 4), ap.IN_WINDOW), rec(date(2026, 11, 5), ap.IN_WINDOW)],
                                            self.TODAY, listed), [])

    def test_today_is_not_yet_missed(self):
        self.assertEqual(ap.unlisted_misses([], date(2026, 11, 3), {}), [])

    def test_a_listed_day_with_an_in_window_record_is_refused(self):
        with self.assertRaises(ValueError):
            ap.unlisted_misses([rec(date(2026, 11, 3), ap.IN_WINDOW)], self.TODAY, {date(2026, 11, 3): {"reason": "x"}})

    def test_weekends_and_holidays_are_not_business_days_to_miss(self):
        self.assertEqual(ap.unlisted_misses([], date(2026, 11, 30), {}, first=date(2026, 11, 25)),
                         [date(2026, 11, 25), date(2026, 11, 27)])  # not 26 (Thanksgiving) or 28-29

    def test_the_three_counts_are_separate(self):
        records = [rec(date(2026, 11, 3), ap.CATCH_UP), rec(date(2026, 11, 4), ap.IN_WINDOW)]
        days = [date(2026, 11, 3), date(2026, 11, 4), date(2026, 11, 5)]
        self.assertEqual(ap.classify_days(records, days), {
            date(2026, 11, 3): "catch_up_only", date(2026, 11, 4): "in_window", date(2026, 11, 5): "no_record"})
        self.assertEqual(ap.count_days(records, days), {"in_window": 1, "catch_up_only": 1, "no_record": 1})

    def test_the_tracked_list_is_well_formed_and_starts_on_3_november(self):
        listed = ap.read_missed(LIST)
        self.assertIn(date(2026, 11, 3), listed)
        self.assertTrue(all(d >= ap.FIRST_DAY for d in listed))
        self.assertEqual(json.loads(LIST.read_text())["days"][0]["et_date"], "2026-11-03")

    def test_a_malformed_list_is_refused(self):
        good = {"et_date": "2026-11-03", "slots_scheduled": 7, "runs_started": 1, "reason": "r"}
        for days in ([{**good, "reason": " "}], [good, good], [{**good, "et_date": "2026-11-07"}],
                     [{**good, "et_date": "2026-11-02"}], [{k: v for k, v in good.items() if k != "runs_started"}]):
            with self.subTest(days=days), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "list.json"
                path.write_text(json.dumps({"description": "d", "days": days}))
                with self.assertRaises(ValueError):
                    ap.read_missed(path)

    def test_the_script_names_an_unlisted_day_and_exits_3(self):
        mod = script()
        now = at(2026, 11, 6, 9, 0, EST)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for day in (date(2026, 11, 4), date(2026, 11, 5)):
                ap.write_record(root, rec(day, ap.IN_WINDOW))
            out = root / "days.txt"
            self.assertEqual(mod.missing(root, LIST, now, out), 0)  # 3 November is on the tracked list
            self.assertEqual(out.read_text(), "")
            lonely = root / "other"
            ap.write_record(lonely, rec(date(2026, 11, 5), ap.IN_WINDOW))
            self.assertEqual(mod.missing(lonely, LIST, now, out), 3)
            self.assertEqual(out.read_text(), "2026-11-04\n")

    def test_a_checkout_without_polls_is_refused_not_read_as_all_missed(self):
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(ValueError):
            ap.unlisted_misses(ap.read_all(Path(tmp), require=True), self.TODAY, {})


class WorkflowTests(unittest.TestCase):
    def test_the_workflow_checks_for_missed_days_after_every_poll(self):
        text = (ROOT / ".github" / "workflows" / "availability-poll.yml").read_text(encoding="utf-8")
        self.assertIn("availability_poll.py missing --dir polls --list main/metadata/availability_missed_days.json", text)
        self.assertIn('cron: "*/10 20-23 * * 1-5"', text)


if __name__ == "__main__":
    unittest.main()
