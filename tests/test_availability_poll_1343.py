"""The availability poll (#1343): when it fetches, what it records, that it never touches the network here.

No test fetches: every poll takes a fake fetcher. Window mutation (20 Nov 2026, not a leakage guard, recorded for the
reviewer): in `sources_due`, `WINDOW_START <= local.time() <= WINDOW_END` changed to `WINDOW_START <= local.time()`
made `test_nothing_after_18_30_et` fail with `AssertionError: () != ('treasury_bill_rates',)`.
"""

from __future__ import annotations

import json
import re
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from repo_model import availability_poll as ap

ROOT = Path(__file__).resolve().parents[1]
UTC = timezone.utc
EST, EDT = timezone(timedelta(hours=-5)), timezone(timedelta(hours=-4))
CSV = b"Date,4 Mo\n10/30/2026,3.5\n10/29/2026,3.6\n"


def at(y, m, d, h, mi, tz):
    return datetime(y, m, d, h, mi, tzinfo=tz)


def fake(status=200, body=CSV, error=None):
    calls = []

    def fetcher(url):
        calls.append(url)
        return status, body, error

    fetcher.calls = calls
    return fetcher


class WindowTests(unittest.TestCase):
    def test_edt_window_is_16_00_to_18_30_et(self):
        self.assertEqual(ap.sources_due(at(2026, 10, 14, 16, 0, EDT)), (ap.TREASURY,))  # Wednesday
        self.assertEqual(ap.sources_due(at(2026, 10, 14, 18, 30, EDT)), (ap.TREASURY,))
        self.assertEqual(ap.sources_due(at(2026, 10, 14, 15, 50, EDT)), ())

    def test_est_window_is_the_same_et_clock(self):
        self.assertEqual(ap.sources_due(at(2026, 11, 18, 21, 0, UTC)), (ap.TREASURY,))  # 16:00 EST
        self.assertEqual(ap.sources_due(at(2026, 11, 18, 23, 30, UTC)), (ap.TREASURY,))  # 18:30 EST
        self.assertEqual(ap.sources_due(at(2026, 11, 18, 20, 50, UTC)), ())  # 15:50 EST

    def test_nothing_after_18_30_et(self):
        self.assertEqual(ap.sources_due(at(2026, 10, 14, 18, 40, EDT)), ())
        self.assertEqual(ap.sources_due(at(2026, 11, 18, 23, 40, UTC)), ())

    def test_thursday_adds_the_fr2004_page(self):
        self.assertEqual(ap.sources_due(at(2026, 10, 15, 17, 0, EDT)), (ap.TREASURY, ap.FR2004))

    def test_weekend_and_holiday_poll_nothing(self):
        self.assertEqual(ap.sources_due(at(2026, 10, 17, 17, 0, EDT)), ())  # Saturday
        self.assertEqual(ap.sources_due(at(2026, 11, 26, 17, 0, EST)), ())  # Thanksgiving, a Thursday

    def test_a_naive_instant_is_refused(self):
        with self.assertRaises(ValueError):
            ap.sources_due(datetime(2026, 10, 14, 17, 0))

    def test_the_cron_covers_the_window_in_both_zones(self):
        text = (ROOT / ".github" / "workflows" / "availability-poll.yml").read_text(encoding="utf-8")
        self.assertIn('cron: "*/10 20-23 * * 1-5"', text)  # 20:00-23:50 UTC covers 16:00 EDT-18:30 EDT and EST
        self.assertIn("availability_poll.py capture", text)
        self.assertIn("contents: write", text)


class RecordTests(unittest.TestCase):
    NOW = at(2026, 10, 30, 17, 10, EDT)

    def record(self, source=ap.TREASURY, **kw):
        return ap.poll_record(source, self.NOW, fake(**kw), clock=lambda: self.NOW)

    def test_treasury_record_has_status_latest_date_and_hash(self):
        rec = self.record()
        self.assertEqual((rec["status"], rec["latest_date"], rec["et_date"]), (200, "2026-10-30", "2026-10-30"))
        self.assertRegex(rec["sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(rec["fetched_at"], "2026-10-30T21:10:00+00:00")
        self.assertIn("daily_treasury_bill_rates", rec["url"])
        self.assertIn("/2026/all", rec["url"])
        ap.check_record(rec)

    def test_hash_changes_with_content(self):
        other = self.record(body=CSV + b"10/31/2026,3.4\n")
        self.assertNotEqual(other["sha256"], self.record()["sha256"])
        self.assertEqual(other["latest_date"], "2026-10-31")

    def test_fr2004_page_latest_date_in_any_form(self):
        page = b"<p>As of October 14, 2026</p><td>10/21/2026</td><i>2026-10-07</i>"
        self.assertEqual(ap.latest_date(ap.FR2004, page), date(2026, 10, 21))
        self.assertIsNone(ap.latest_date(ap.FR2004, b"no dates"))

    def test_http_error_is_a_record_without_a_date(self):
        rec = self.record(status=503, body=b"<html>down</html>", error="HTTP 503")
        self.assertEqual((rec["status"], rec["latest_date"], rec["error"]), (503, None, "HTTP 503"))
        ap.check_record(rec)

    def test_no_connection_is_a_record(self):
        rec = self.record(status=None, body=b"", error="URLError: down")
        self.assertIsNone(rec["status"])
        ap.check_record(rec)

    def test_fetch_time_is_never_before_the_poll_instant(self):
        rec = ap.poll_record(ap.TREASURY, self.NOW, fake(), clock=lambda: self.NOW - timedelta(minutes=1))
        self.assertEqual(rec["fetched_at"], self.NOW.astimezone(UTC).isoformat())

    def test_malformed_records_are_refused(self):
        rec = self.record()
        for bad in ({**rec, "source": "x"}, {**rec, "sha256": "zz"}, {**rec, "fetched_at": "2026-10-30T17:00:00"},
                    {k: v for k, v in rec.items() if k != "error"}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                ap.check_record(bad)

    def test_write_is_add_only_and_round_trips(self):
        rec = self.record()
        with tempfile.TemporaryDirectory() as tmp:
            path = ap.write_record(Path(tmp), rec)
            self.assertEqual(json.loads(path.read_text()), rec)
            with self.assertRaises(ValueError):
                ap.write_record(Path(tmp), rec)
            self.assertEqual(ap.read_all(Path(tmp)), [rec])


class CaptureScriptTests(unittest.TestCase):
    def setUp(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("availability_poll_script", ROOT / "scripts" / "availability_poll.py")
        self.script = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.script)

    def test_outside_the_window_nothing_is_fetched(self):
        fetcher = fake()
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self.script.capture(Path(tmp), at(2026, 10, 14, 12, 0, EDT), fetcher), [])
            self.assertEqual(list(Path(tmp).iterdir()), [])
        self.assertEqual(fetcher.calls, [])

    def test_a_thursday_poll_writes_one_file_per_source(self):
        now = at(2026, 10, 15, 17, 0, EDT)
        fetcher = fake()
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.script.capture(Path(tmp), now, fetcher, clock=lambda: now)
            self.assertEqual(len(paths), 2)
            self.assertEqual(len(fetcher.calls), 2)
            self.assertEqual({r["source"] for r in ap.read_all(Path(tmp))}, set(ap.SOURCES))


if __name__ == "__main__":
    unittest.main()
