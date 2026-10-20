"""SOFR first prints in the live log (#940; scoring protocol §6 and §11: "the outcome is the first published value").

The New York Fed publishes SOFR at about 08:00 ET on the next business day and may revise it at about 14:30 ET that
day. `repo_model.sofr_first_print` keeps the first release of each day, apart from any revision: the API payload as
fetched, the retrieval time, its SHA-256, the publication time and IORB's first-public source.

**Recorded mutation** (20 October 2026), in `check_first_print`: the line

    if retrieved >= revision:

(a record fetched at or after the revision instant) was changed to `if False:`. `LateFetchTests.test_a_fetch_at_the_
revision_instant_is_refused` and `test_a_fetch_after_the_revision_instant_is_refused` then failed with
`AssertionError: LookAheadError not raised`. The second guard, in the same function, `if indicator:` (a payload whose
row for the day carries a revision indicator) was changed to `if False:`: `RevisionKnownTests.test_a_revised_row_is_
refused` failed with `AssertionError: LookAheadError not raised`.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from repo_model import sofr_first_print as fp
from repo_model.splits import LookAheadError

EFFECTIVE = date(2026, 10, 16)  # a Friday: published 08:00 ET on Monday 2026-10-19
EASTERN_UTC_OFFSET = timedelta(hours=-4)  # EDT on those days


def _payload(effective=EFFECTIVE, rate=3.88, indicator="", extra=()):
    rows = [
        {
            "effectiveDate": effective.isoformat(),
            "type": "SOFR",
            "percentRate": rate,
            "percentPercentile1": 3.84,
            "percentPercentile25": 3.85,
            "percentPercentile75": 3.93,
            "percentPercentile99": 3.95,
            "revisionIndicator": indicator,
        }
    ]
    rows.extend(extra)
    return json.dumps({"refRates": rows}).encode("utf-8")


def _utc(local_hour, local_minute=0, day=date(2026, 10, 19)):
    """An aware UTC instant for a wall-clock time in ET on `day` (EDT)."""

    naive = datetime(day.year, day.month, day.day, local_hour, local_minute)
    return (naive - EASTERN_UTC_OFFSET).replace(tzinfo=timezone.utc)


IORB = {
    "source": "fed-iorb-announcements",
    "rate_percent": 3.9,
    "effective_date": "2026-09-17",
    "announced_at": "2026-09-16T14:00",
    "implementation_note_url": "https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a1.htm",
    "table_sha256": "0" * 64,
}


def _record(retrieved=None, payload=None, effective=EFFECTIVE):
    return fp.first_print_record(
        payload if payload is not None else _payload(effective=effective),
        url="https://markets.newyorkfed.org/api/rates/secured/sofr/search.json?startDate=2026-10-16&endDate=2026-10-16&type=rate",
        retrieved_at=retrieved if retrieved is not None else _utc(8, 20),
        effective=effective,
        iorb=IORB,
    )


class InstantsTests(unittest.TestCase):
    def test_publication_is_the_next_business_day_at_eight(self):
        self.assertEqual(fp.publication_instant(EFFECTIVE), datetime(2026, 10, 19, 8, 0))

    def test_a_holiday_pushes_publication_to_the_next_business_day(self):
        # Friday 2026-11-27 -> Monday 2026-11-30; Wednesday 2026-11-25 -> Friday 2026-11-27 is not a holiday,
        # but Thursday 2026-11-26 (Thanksgiving) is closed, so Wednesday publishes on Friday.
        self.assertEqual(fp.publication_instant(date(2026, 11, 25)), datetime(2026, 11, 27, 8, 0))

    def test_revision_is_the_same_day_at_half_past_two(self):
        self.assertEqual(fp.revision_instant(EFFECTIVE), datetime(2026, 10, 19, 14, 30))


class RecordTests(unittest.TestCase):
    def test_the_record_carries_the_payload_the_hash_the_times_and_the_iorb_source(self):
        payload = _payload()
        record = _record(payload=payload)
        self.assertEqual(record["effective_date"], "2026-10-16")
        self.assertEqual(record["sha256"], hashlib.sha256(payload).hexdigest())
        self.assertEqual(record["payload"], payload.decode("utf-8"))
        self.assertEqual(record["sofr_percent"], 3.88)
        self.assertEqual(record["revision_indicator"], "")
        self.assertEqual(record["publication_instant"], "2026-10-19T08:00:00-04:00")
        self.assertEqual(record["revision_instant"], "2026-10-19T14:30:00-04:00")
        self.assertEqual(record["retrieved_at"], "2026-10-19T12:20:00+00:00")
        self.assertEqual(record["iorb"], IORB)
        fp.check_first_print(record)

    def test_a_payload_without_the_day_is_malformed(self):
        with self.assertRaises(ValueError):
            _record(payload=_payload(effective=date(2026, 10, 15)))

    def test_a_non_numeric_rate_is_malformed(self):
        with self.assertRaises(ValueError):
            _record(payload=_payload(rate="n/a"))

    def test_a_naive_retrieval_time_is_malformed(self):
        with self.assertRaises(ValueError):
            _record(retrieved=datetime(2026, 10, 19, 8, 20))

    def test_a_tampered_payload_fails_its_hash(self):
        record = _record()
        record["payload"] = record["payload"].replace("3.88", "3.89")
        with self.assertRaises(ValueError):
            fp.check_first_print(record)

    def test_a_missing_key_is_malformed(self):
        record = _record()
        del record["iorb"]
        with self.assertRaises(ValueError):
            fp.check_first_print(record)

    def test_the_iorb_source_must_name_its_note(self):
        record = _record()
        record["iorb"] = {"source": "fed-iorb-announcements"}
        with self.assertRaises(ValueError):
            fp.check_first_print(record)

    def test_a_fetch_before_publication_is_malformed(self):
        with self.assertRaises(ValueError):
            _record(retrieved=_utc(7, 30))


class LateFetchTests(unittest.TestCase):
    def test_a_fetch_just_before_the_revision_instant_is_a_first_print(self):
        fp.check_first_print(_record(retrieved=_utc(14, 29)))

    def test_a_fetch_at_the_revision_instant_is_refused(self):
        with self.assertRaises(LookAheadError):
            _record(retrieved=_utc(14, 30))

    def test_a_fetch_after_the_revision_instant_is_refused(self):
        with self.assertRaises(LookAheadError):
            _record(retrieved=_utc(17, 30))

    def test_a_stored_record_is_checked_again_on_read(self):
        record = _record()
        record["retrieved_at"] = "2026-10-19T19:00:00+00:00"  # 15:00 ET
        with self.assertRaises(LookAheadError):
            fp.check_first_print(record)


class RevisionKnownTests(unittest.TestCase):
    def test_a_revised_row_is_refused(self):
        with self.assertRaises(LookAheadError):
            _record(payload=_payload(indicator="R"))

    def test_a_blank_indicator_passes(self):
        _record(payload=_payload(indicator="  "))


class WriteOnceTests(unittest.TestCase):
    def test_a_day_is_written_once_and_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = _record()
            path = fp.write_first_print(Path(tmp), first)
            self.assertEqual(path, Path(tmp) / "sofr" / "2026-10-16.json")
            before = path.read_bytes()
            second = _record(retrieved=_utc(9, 0))
            with self.assertRaises(ValueError):
                fp.write_first_print(Path(tmp), second)
            self.assertEqual(path.read_bytes(), before)

    def test_a_late_record_is_not_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            record = _record()
            record["retrieved_at"] = "2026-10-19T20:00:00+00:00"
            with self.assertRaises(LookAheadError):
                fp.write_first_print(Path(tmp), record)
            self.assertFalse((Path(tmp) / "sofr").exists())

    def test_read_all_returns_the_written_days(self):
        with tempfile.TemporaryDirectory() as tmp:
            fp.write_first_print(Path(tmp), _record())
            self.assertEqual([r["effective_date"] for r in fp.read_all(Path(tmp))], ["2026-10-16"])


class TargetDayTests(unittest.TestCase):
    def test_after_eight_on_a_business_day_the_target_is_the_previous_business_day(self):
        self.assertEqual(fp.latest_published(_utc(9, 0, date(2026, 10, 19))), date(2026, 10, 16))
        self.assertEqual(fp.latest_published(_utc(9, 0, date(2026, 10, 20))), date(2026, 10, 19))

    def test_before_eight_nothing_new_is_published_yet(self):
        self.assertIsNone(fp.latest_published(_utc(7, 0, date(2026, 10, 20))))

    def test_a_weekend_publishes_nothing(self):
        self.assertIsNone(fp.latest_published(_utc(10, 0, date(2026, 10, 17))))

    def test_a_holiday_publishes_nothing(self):
        self.assertIsNone(fp.latest_published(_utc(10, 0, date(2026, 11, 26))))

    def test_after_the_revision_window_the_day_is_still_named_but_cannot_be_captured(self):
        # latest_published names the day; the capture guard then refuses a fetch after 14:30.
        self.assertEqual(fp.latest_published(_utc(16, 0, date(2026, 10, 19))), date(2026, 10, 16))


class IorbSourceTests(unittest.TestCase):
    def test_the_rate_in_force_and_its_note(self):
        source = fp.iorb_source(date(2026, 10, 16))
        self.assertEqual(source["rate_percent"], 3.9)
        self.assertEqual(source["effective_date"], "2026-09-17")
        self.assertTrue(source["implementation_note_url"].startswith("https://www.federalreserve.gov/"))
        self.assertEqual(len(source["table_sha256"]), 64)

    def test_a_day_before_the_table_is_refused(self):
        with self.assertRaises(ValueError):
            fp.iorb_source(date(2018, 3, 1))


def _script():
    import importlib.util

    path = Path(__file__).resolve().parents[1] / "scripts" / "sofr_first_print.py"
    spec = importlib.util.spec_from_file_location("sofr_first_print_script", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CaptureScriptTests(unittest.TestCase):
    """`scripts/sofr_first_print.py capture`, with the fetch replaced by a fixed response."""

    def setUp(self):
        self.script = _script()
        self.urls = []

    def _download(self, url):
        self.urls.append(url)
        if "type=rate" in url:
            return _payload()
        return json.dumps({"refRates": [{"effectiveDate": "2026-10-16", "type": "SOFR", "volumeInBillions": 2000}]}).encode()

    def test_capture_writes_the_days_first_print(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.script.capture(Path(tmp), _utc(8, 15), self._download, clock=lambda: _utc(8, 15))
            record = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(record["effective_date"], "2026-10-16")
            self.assertEqual(record["retrieved_at"], "2026-10-19T12:15:00+00:00")
            self.assertIn("type=rate", record["url"])
            self.assertIn("startDate=2026-10-16&endDate=2026-10-16", record["url"])

    def test_a_captured_day_is_not_fetched_again(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.script.capture(Path(tmp), _utc(8, 15), self._download, clock=lambda: _utc(8, 15))
            fetched = len(self.urls)
            again = self.script.capture(Path(tmp), _utc(9, 0), self._download, clock=lambda: _utc(9, 0))
            self.assertIsNone(again)
            self.assertEqual(len(self.urls), fetched)

    def test_nothing_is_fetched_before_publication(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(self.script.capture(Path(tmp), _utc(7, 0), self._download, clock=lambda: _utc(7, 0)))
            self.assertEqual(self.urls, [])

    def test_a_response_that_arrives_after_the_revision_instant_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(LookAheadError):
                self.script.capture(Path(tmp), _utc(8, 15), self._download, clock=lambda: _utc(15, 0))
            self.assertFalse((Path(tmp) / "sofr").exists())

    def test_the_record_written_verifies(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.script.capture(Path(tmp), _utc(8, 15), self._download, clock=lambda: _utc(8, 15))
            self.assertEqual(self.script.verify(Path(tmp)), 0)


class RevisionReportTests(unittest.TestCase):
    """`scripts/sofr_revisions_940.py`: the committed page and data are what the script writes from the tracked inputs."""

    def setUp(self):
        import importlib.util

        path = Path(__file__).resolve().parents[1] / "scripts" / "sofr_revisions_940.py"
        spec = importlib.util.spec_from_file_location("sofr_revisions_940_script", path)
        self.script = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.script)

    def test_the_committed_report_is_current(self):
        self.assertEqual(self.script.main(["--check"]), 0)

    def test_no_row_is_flagged_so_nothing_is_called_a_first_print(self):
        result = self.script.build()
        self.assertEqual(result["dates_flagged_revised"], [])
        self.assertFalse(result["first_prints_recoverable"])
        self.assertEqual(result["vintage"], "current vintage")

    def test_nothing_after_the_lockbox_edge_is_counted(self):
        self.assertEqual(self.script.build()["window"]["last"], "2025-12-31")


if __name__ == "__main__":
    unittest.main()
