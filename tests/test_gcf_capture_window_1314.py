"""The DTCC GCF capture window runs to the 18:00 ET decision instant, and a value posted before it is the same day's (#1314; #1312).

DTCC posts the day's index at about 16:00 to 16:05 ET (#1280), after the old 16:00 decision instant and before the new 18:00 one
(`repo_model.decision_instant`). `tests/test_gcf_index_capture.py` pins the window's edges; this module pins what the move is for:

* a run at 16:05 ET, which the 16:00 window refused, fetches the day and keeps the value as `captured` (same-day), and a reader at the
  18:00 decision reads it;
* a record that states the earlier 16:00 instant stays a record of that instant (`legacy_decision_instant`), read against the instant it
  declares and not rewritten;
* the schedules that call the script cover 15:30 to 18:00 ET in both EDT and EST: the UTC span the private repository's cron must
  contain is derived here from the module's own instants, for one summer and one winter day.

**Recorded mutation** (30 October 2026), in `repo_model.gcf_index.plan`: the line

    if local <= decision_instant(today):

was changed to `if local <= legacy_decision_instant(today):` (the window ends at 16:00 again).
`WindowMovedTests.test_a_run_at_sixteen_oh_five_fetches_and_keeps_the_day` failed with
`AssertionError: 'late' != 'fetch'`, and `WindowMovedTests.test_a_value_posted_at_sixteen_thirty_is_kept_and_read_by_the_decision`
raised `ValueError: a fetch that was not after the decision instant is not a late fetch`.
"""

from __future__ import annotations

import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from repo_model import decision_instant as di
from repo_model import gcf_index as gi
from repo_model.splits import LookAheadError

from test_gcf_index_capture import DAY, URL, _csv, _record, _script, _utc

WINTER = date(2026, 11, 2)  # a Monday, EST (daylight time ended on 1 November 2026)


def _utc_of(day: date, hour: int, minute: int = 0) -> datetime:
    """An aware UTC instant for an ET wall-clock time on `day`, through the module's own zone."""

    return datetime(day.year, day.month, day.day, hour, minute, tzinfo=gi.EASTERN).astimezone(timezone.utc)


class WindowMovedTests(unittest.TestCase):
    def test_the_window_end_is_the_declared_decision_instant(self):
        self.assertEqual(gi.decision_instant(DAY).timetz().replace(tzinfo=None), di.DECISION_TIME)
        self.assertEqual(di.DECISION_TIME.isoformat(timespec="minutes"), "18:00")

    def test_a_run_at_sixteen_oh_five_fetches_and_keeps_the_day(self):
        self.assertEqual(gi.plan(_utc(16, 5), already=set()).action, "fetch")
        self.assertEqual(gi.plan(_utc(17, 59), already=set()).action, "fetch")

    def test_a_value_posted_at_sixteen_thirty_is_kept_and_read_by_the_decision(self):
        script = _script()
        with tempfile.TemporaryDirectory() as root:
            outcome = script.capture(Path(root), _utc(16, 30), lambda url: _csv(), clock=lambda: _utc(16, 30))
            self.assertEqual(outcome, "captured")
            value = gi.read_value(root, DAY, as_of=gi.decision_instant(DAY))
            self.assertEqual(value["treasury_rate_percent"], 3.946)
            self.assertEqual(value["effective_date"], "2026-10-26")
            self.assertEqual(value["fetched_at_utc"], "2026-10-26T20:30:00+00:00")

    def test_a_value_posted_before_the_decision_is_not_read_by_an_earlier_reader(self):
        with tempfile.TemporaryDirectory() as root:
            gi.write_record(root, _record(fetched=_utc(16, 30)))
            with self.assertRaises(LookAheadError):
                gi.read_value(root, DAY, as_of=_utc(16, 29))

    def test_a_fetch_after_eighteen_hundred_is_still_a_missed_day(self):
        script = _script()
        with tempfile.TemporaryDirectory() as root:
            outcome = script.capture(Path(root), _utc(18, 5), lambda url: _csv(), clock=lambda: _utc(18, 5))
            self.assertEqual(outcome, "missed")
            self.assertIsNone(gi.read_value(root, DAY, as_of=_utc(18, 30)))


class EarlierInstantTests(unittest.TestCase):
    def test_the_earlier_instant_is_sixteen_hundred_and_is_kept_for_the_records_that_state_it(self):
        self.assertEqual(gi.legacy_decision_instant(DAY).isoformat(), "2026-10-26T16:00:00-04:00")
        self.assertEqual(gi.legacy_decision_instant(DAY) + timedelta(hours=2), gi.decision_instant(DAY))


class ScheduleCoverageTests(unittest.TestCase):
    """The UTC span a schedule must cover so that every run the script wants (15:30 to 18:00 ET) happens, summer and winter."""

    @staticmethod
    def _span(day: date):
        return gi.window_start(day).astimezone(timezone.utc), gi.decision_instant(day).astimezone(timezone.utc)

    def test_the_span_is_nineteen_thirty_to_twenty_two_in_summer_and_twenty_thirty_to_twenty_three_in_winter(self):
        start, end = self._span(DAY)
        self.assertEqual((start.hour, start.minute, end.hour, end.minute), (19, 30, 22, 0))
        start, end = self._span(WINTER)
        self.assertEqual((start.hour, start.minute, end.hour, end.minute), (20, 30, 23, 0))

    def test_one_fixed_utc_schedule_covers_both_seasons_from_twenty_hundred_to_twenty_three_hundred(self):
        # The private repository's cron lists UTC hours. 16:00 to 18:00 ET (the posting window proper, DTCC posts at about 16:00)
        # is 20:00 to 22:00 UTC in EDT and 21:00 to 23:00 UTC in EST: the union is 20:00 to 23:00 UTC.
        summer = (_utc_of(DAY, 16), _utc_of(DAY, 18))
        winter = (_utc_of(WINTER, 16), _utc_of(WINTER, 18))
        self.assertEqual((summer[0].hour, summer[1].hour), (20, 22))
        self.assertEqual((winter[0].hour, winter[1].hour), (21, 23))
        union = (min(summer[0].hour, winter[0].hour), max(summer[1].hour, winter[1].hour))
        self.assertEqual(union, (20, 23))


if __name__ == "__main__":
    unittest.main()
