"""DTCC GCF Repo Index, forward capture (#962; H5 groundwork G3, prospective logging).

DTCC posts the day's par-weighted GCF Treasury rate and par volume at about 15:30 ET on the day itself, half an hour
before the 16:00 ET decision instant, so it is the one public repo rate for day T that exists at T's decision.
`repo_model.gcf_index` keeps one file per business day, as fetched: the response bytes, the fetch instant (UTC and ET)
and their SHA-256. A day fetched after 16:00 ET, or with no posting by then, is a missed record that holds no value.
Nothing is back-filled and no history is read as an input (#962 criterion 3).

**Recorded mutation** (27 October 2026), in `repo_model.gcf_index.check_record`: the line

    if fetched > decision:

(a captured record whose fetch instant is after the day's 16:00 ET decision instant) was changed to `if False:`.
`LateFetchTests.test_a_fetch_after_the_decision_instant_is_refused` and
`LateFetchTests.test_the_read_guard_refuses_a_value_fetched_after_the_decision_instant` then failed with
`AssertionError: LookAheadError not raised`. The read guard's own line in `read_value`, `if fetched > as_of:`, was
changed to `if False:`: `LateFetchTests.test_a_captured_record_is_refused_by_a_reader_at_an_earlier_instant` failed
with `AssertionError: LookAheadError not raised`.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from repo_model import gcf_index as gi
from repo_model.splits import LookAheadError

DAY = date(2026, 10, 26)  # a Monday, EDT
EDT = timedelta(hours=-4)


def _csv(days=((date(2026, 10, 23), 104960000000, 3.950, 71690000000, 3.936), (DAY, 136692000000, 3.967, 65840000000, 3.946)), trailer=None, eol="\r\n"):
    lines = ["Date,MBS Total PAR Value,MBS Weighted Average,Treasury Total PAR Value,Treasury Weighted Average"]
    for d, mbs_par, mbs_rate, tsy_par, tsy_rate in days:
        lines.append(f"{d.month:02d}/{d.day:02d}/{d.year},{mbs_par},  {mbs_rate:.3f},{tsy_par},  {tsy_rate:.3f} ")
    lines.append(f"TRAILER,{len(days) if trailer is None else trailer},,,,,")
    return (eol.join(lines) + eol).encode("utf-8")


def _utc(hour, minute=0, second=0, day=DAY):
    """An aware UTC instant for an ET wall-clock time on `day` (EDT)."""

    naive = datetime(day.year, day.month, day.day, hour, minute, second)
    return (naive - EDT).replace(tzinfo=timezone.utc)


URL = "https://cms-prod.dtcc.com/data/gcfindex.csv?v=1793049000000"


def _record(fetched=None, payload=None, effective=DAY):
    return gi.captured_record(
        payload if payload is not None else _csv(),
        url=URL,
        fetched_at=fetched if fetched is not None else _utc(15, 40),
        effective=effective,
    )


class ParseTests(unittest.TestCase):
    def test_a_row_is_read_with_its_padding_and_units(self):
        rows = gi.parse_csv(_csv().decode("utf-8"))
        self.assertEqual(sorted(rows), [date(2026, 10, 23), DAY])
        self.assertEqual(
            rows[DAY],
            {"mbs_par_usd": 136692000000.0, "mbs_rate_percent": 3.967, "treasury_par_usd": 65840000000.0, "treasury_rate_percent": 3.946},
        )

    def test_the_trailer_counts_the_rows(self):
        with self.assertRaises(ValueError):
            gi.parse_csv(_csv(trailer=5).decode("utf-8"))

    def test_a_missing_trailer_is_refused_as_a_truncated_file(self):
        text = _csv().decode("utf-8")
        with self.assertRaises(ValueError):
            gi.parse_csv(text[: text.rindex("TRAILER")])

    def test_an_unknown_header_is_refused(self):
        with self.assertRaises(ValueError):
            gi.parse_csv(_csv().decode("utf-8").replace("Treasury Weighted Average", "Treasury Rate"))

    def test_an_unreadable_row_is_refused(self):
        with self.assertRaises(ValueError):
            gi.parse_csv(_csv().decode("utf-8").replace("3.946", "n/a"))

    def test_a_blank_cell_is_none_not_zero(self):
        text = _csv().decode("utf-8").replace("65840000000,  3.946 ", ",  ")
        rows = gi.parse_csv(text)
        self.assertIsNone(rows[DAY]["treasury_par_usd"])
        self.assertIsNone(rows[DAY]["treasury_rate_percent"])


class InstantsTests(unittest.TestCase):
    def test_the_decision_instant_is_sixteen_hundred_eastern_on_the_day(self):
        self.assertEqual(gi.decision_instant(DAY).isoformat(), "2026-10-26T16:00:00-04:00")

    def test_the_window_opens_at_fifteen_thirty_on_the_same_day(self):
        self.assertEqual(gi.window_start(DAY).isoformat(), "2026-10-26T15:30:00-04:00")

    def test_standard_time_is_an_hour_later_in_utc(self):
        winter = date(2026, 11, 2)
        self.assertEqual(gi.decision_instant(winter).astimezone(timezone.utc).hour, 21)


class CapturedRecordTests(unittest.TestCase):
    def test_a_fetch_in_the_window_is_kept_with_its_bytes_and_both_clocks(self):
        record = _record(fetched=_utc(15, 40))
        self.assertEqual(record["status"], "captured")
        self.assertEqual(record["effective_date"], "2026-10-26")
        self.assertEqual(record["fetched_at_utc"], "2026-10-26T19:40:00+00:00")
        self.assertEqual(record["fetched_at_et"], "2026-10-26T15:40:00-04:00")
        self.assertEqual(record["sha256"], hashlib.sha256(_csv()).hexdigest())
        self.assertEqual(record["payload"], _csv().decode("utf-8"))
        self.assertEqual(record["treasury_rate_percent"], 3.946)
        self.assertEqual(record["treasury_par_usd"], 65840000000.0)

    def test_a_response_with_no_row_for_the_day_has_no_posting(self):
        with self.assertRaises(ValueError):
            _record(payload=_csv(days=((date(2026, 10, 23), 1, 3.9, 1, 3.9),)))

    def test_a_row_with_no_treasury_rate_is_no_posting(self):
        text = _csv().decode("utf-8").replace("65840000000,  3.946 ", ",  ")
        with self.assertRaises(ValueError):
            _record(payload=text.encode("utf-8"))

    def test_a_naive_fetch_time_is_refused(self):
        with self.assertRaises(ValueError):
            _record(fetched=datetime(2026, 10, 26, 15, 40))

    def test_a_fetch_before_the_window_is_refused(self):
        with self.assertRaises(ValueError):
            _record(fetched=_utc(15, 29, 59))

    def test_a_fetch_at_the_end_of_the_window_is_kept(self):
        self.assertEqual(_record(fetched=_utc(16, 0, 0))["status"], "captured")


class LateFetchTests(unittest.TestCase):
    def test_a_fetch_after_the_decision_instant_is_refused(self):
        with self.assertRaises(LookAheadError):
            _record(fetched=_utc(16, 0, 1))

    def test_a_captured_record_is_refused_by_a_reader_at_an_earlier_instant(self):
        with tempfile.TemporaryDirectory() as root:
            gi.write_record(root, _record(fetched=_utc(15, 45)))
            with self.assertRaises(LookAheadError):
                gi.read_value(root, DAY, as_of=_utc(15, 44))
            self.assertEqual(gi.read_value(root, DAY, as_of=_utc(15, 45))["treasury_rate_percent"], 3.946)

    def test_the_read_guard_refuses_a_value_fetched_after_the_decision_instant(self):
        record = _record(fetched=_utc(15, 45))
        record["fetched_at_utc"] = _utc(16, 20).isoformat()
        record["fetched_at_et"] = gi._et(_utc(16, 20)).isoformat()
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "gcf" / "2026-10-26.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(record), encoding="utf-8")
            with self.assertRaises(LookAheadError):
                gi.read_value(root, DAY, as_of=_utc(16, 30))
            with self.assertRaises(LookAheadError):
                gi.read_all(root)

    def test_the_other_clock_must_agree(self):
        record = _record()
        record["fetched_at_et"] = "2026-10-26T15:41:00-04:00"
        with self.assertRaises(ValueError):
            gi.check_record(record)


class MissedRecordTests(unittest.TestCase):
    def test_a_late_fetch_is_a_missed_record_with_no_value(self):
        record = gi.missed_record(DAY, "fetched_after_decision", fetched_at=_utc(16, 12), url=URL, payload=_csv())
        self.assertEqual(record["status"], "missed")
        self.assertNotIn("treasury_rate_percent", record)
        self.assertNotIn("payload", record)
        gi.check_record(record)

    def test_a_missed_record_is_never_a_value(self):
        with tempfile.TemporaryDirectory() as root:
            gi.write_record(root, gi.missed_record(DAY, "no_posting", fetched_at=_utc(16, 10), url=URL, payload=_csv(days=())))
            self.assertIsNone(gi.read_value(root, DAY, as_of=_utc(17)))

    def test_no_run_has_no_fetch(self):
        record = gi.missed_record(DAY, "no_run")
        self.assertIsNone(record["fetched_at_utc"])
        gi.check_record(record)

    def test_a_late_fetch_cannot_be_called_early(self):
        with self.assertRaises(ValueError):
            gi.missed_record(DAY, "fetched_after_decision", fetched_at=_utc(15, 50), url=URL, payload=_csv())

    def test_an_unknown_reason_is_refused(self):
        with self.assertRaises(ValueError):
            gi.missed_record(DAY, "tired")

    def test_a_missed_record_with_a_value_is_refused(self):
        record = gi.missed_record(DAY, "no_run")
        record["treasury_rate_percent"] = 3.9
        with self.assertRaises(ValueError):
            gi.check_record(record)


class WriteOnceTests(unittest.TestCase):
    def test_a_day_is_written_once_and_never_overwritten(self):
        with tempfile.TemporaryDirectory() as root:
            path = gi.write_record(root, _record())
            self.assertEqual(path, Path(root) / "gcf" / "2026-10-26.json")
            with self.assertRaises(ValueError):
                gi.write_record(root, _record(fetched=_utc(15, 50)))
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["fetched_at_utc"], "2026-10-26T19:40:00+00:00")

    def test_a_record_with_a_changed_payload_fails_its_hash(self):
        record = _record()
        record["payload"] = record["payload"].replace("3.946", "3.846")
        with self.assertRaises(ValueError):
            gi.check_record(record)

    def test_a_record_whose_rate_is_not_the_payloads_is_refused(self):
        record = _record()
        record["treasury_rate_percent"] = 3.9
        with self.assertRaises(ValueError):
            gi.check_record(record)

    def test_read_all_checks_each_file_and_its_name(self):
        with tempfile.TemporaryDirectory() as root:
            gi.write_record(root, _record())
            self.assertEqual(len(gi.read_all(root)), 1)
            (Path(root) / "gcf" / "2026-10-27.json").write_text(
                (Path(root) / "gcf" / "2026-10-26.json").read_text(encoding="utf-8"), encoding="utf-8"
            )
            with self.assertRaises(ValueError):
                gi.read_all(root)


class WhatToDoTests(unittest.TestCase):
    """`gi.plan`: what a run at `now` does for the day, given what is already on the branch."""

    def test_before_the_window_nothing_is_fetched(self):
        self.assertEqual(gi.plan(_utc(15, 29, 59), already=set()).action, "wait")

    def test_a_weekend_and_a_holiday_have_no_day(self):
        self.assertEqual(gi.plan(_utc(15, 40, day=date(2026, 10, 24)), already=set()).action, "none")
        self.assertEqual(gi.plan(_utc(15, 40, day=date(2026, 11, 26)), already=set()).action, "none")  # Thanksgiving

    def test_in_the_window_the_day_is_fetched(self):
        decision = gi.plan(_utc(15, 40), already=set())
        self.assertEqual((decision.action, decision.day), ("fetch", DAY))

    def test_the_last_instant_of_the_window_still_fetches(self):
        self.assertEqual(gi.plan(_utc(16, 0, 0), already=set()).action, "fetch")

    def test_a_day_already_on_the_branch_is_not_fetched_again(self):
        self.assertEqual(gi.plan(_utc(15, 40), already={DAY}).action, "done")

    def test_after_the_decision_instant_the_day_is_fetched_once_to_be_recorded_missed(self):
        decision = gi.plan(_utc(16, 0, 1), already=set())
        self.assertEqual((decision.action, decision.day), ("late", DAY))

    def test_unrecorded_earlier_business_days_are_no_run_not_back_filled(self):
        # The branch's earliest day is Wednesday the 21st; Thursday and Friday have no file; Monday is today.
        already = {date(2026, 10, 21)}
        decision = gi.plan(_utc(15, 40), already=already)
        self.assertEqual(decision.gaps, [date(2026, 10, 22), date(2026, 10, 23)])

    def test_an_empty_branch_has_no_gaps(self):
        self.assertEqual(gi.plan(_utc(15, 40), already=set()).gaps, [])


def _script():
    import importlib.util

    path = Path(__file__).resolve().parents[1] / "scripts" / "gcf_index_capture.py"
    spec = importlib.util.spec_from_file_location("gcf_index_capture_script", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CaptureScriptTests(unittest.TestCase):
    """`scripts/gcf_index_capture.py capture`, with the fetch replaced by a fixed response and a fixed clock."""

    def setUp(self):
        self.script = _script()
        self.urls = []
        self.body = _csv()

    def _download(self, url):
        self.urls.append(url)
        return self.body

    def _run(self, root, now, clock=None):
        return self.script.capture(Path(root), now, self._download, clock=lambda: clock or now)

    def test_a_posted_day_is_kept_with_a_cache_busting_url(self):
        with tempfile.TemporaryDirectory() as root:
            outcome = self._run(root, _utc(15, 40))
            self.assertEqual(outcome, "captured")
            record = json.loads((Path(root) / "gcf" / "2026-10-26.json").read_text(encoding="utf-8"))
            self.assertEqual(record["status"], "captured")
            self.assertEqual(len(self.urls), 1)
            self.assertTrue(self.urls[0].startswith(gi.CSV_URL + "?v="), self.urls[0])
            self.assertEqual(record["url"], self.urls[0])

    def test_before_the_window_nothing_is_fetched_or_written(self):
        with tempfile.TemporaryDirectory() as root:
            self.assertEqual(self._run(root, _utc(15, 0)), "wait")
            self.assertEqual(self.urls, [])
            self.assertFalse((Path(root) / "gcf").exists())

    def test_a_day_with_no_row_yet_is_tried_again_by_a_later_slot(self):
        self.body = _csv(days=((date(2026, 10, 23), 1, 3.9, 1, 3.9),))
        with tempfile.TemporaryDirectory() as root:
            self.assertEqual(self._run(root, _utc(15, 40)), "not_posted")
            self.assertFalse((Path(root) / "gcf").exists())

    def test_a_captured_day_is_never_fetched_again(self):
        with tempfile.TemporaryDirectory() as root:
            self._run(root, _utc(15, 40))
            self.assertEqual(self._run(root, _utc(15, 50)), "done")
            self.assertEqual(len(self.urls), 1)

    def test_a_late_slot_with_the_row_records_the_day_missed_and_keeps_no_value(self):
        with tempfile.TemporaryDirectory() as root:
            self.assertEqual(self._run(root, _utc(16, 35)), "missed")
            record = json.loads((Path(root) / "gcf" / "2026-10-26.json").read_text(encoding="utf-8"))
            self.assertEqual((record["status"], record["reason"]), ("missed", "fetched_after_decision"))
            self.assertNotIn("treasury_rate_percent", record)

    def test_a_slot_that_started_in_the_window_but_fetched_after_it_is_missed(self):
        with tempfile.TemporaryDirectory() as root:
            self.assertEqual(self._run(root, _utc(15, 59), clock=_utc(16, 0, 30)), "missed")
            record = json.loads((Path(root) / "gcf" / "2026-10-26.json").read_text(encoding="utf-8"))
            self.assertEqual(record["reason"], "fetched_after_decision")

    def test_a_late_slot_with_no_row_records_no_posting(self):
        self.body = _csv(days=((date(2026, 10, 23), 1, 3.9, 1, 3.9),))
        with tempfile.TemporaryDirectory() as root:
            self.assertEqual(self._run(root, _utc(17, 0)), "missed")
            record = json.loads((Path(root) / "gcf" / "2026-10-26.json").read_text(encoding="utf-8"))
            self.assertEqual((record["reason"], record["latest_row_date"]), ("no_posting", "2026-10-23"))

    def test_an_unreadable_late_response_is_recorded_not_raised(self):
        self.body = b"<html>maintenance</html>"
        with tempfile.TemporaryDirectory() as root:
            self.assertEqual(self._run(root, _utc(17, 0)), "missed")
            record = json.loads((Path(root) / "gcf" / "2026-10-26.json").read_text(encoding="utf-8"))
            self.assertEqual(record["reason"], "unreadable_response")

    def test_an_unreadable_response_in_the_window_is_a_refusal_and_writes_nothing(self):
        self.body = b"<html>maintenance</html>"
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(ValueError):
                self._run(root, _utc(15, 40))
            self.assertFalse((Path(root) / "gcf").exists())

    def test_days_nobody_fetched_are_recorded_no_run_and_never_back_filled(self):
        with tempfile.TemporaryDirectory() as root:
            gi.write_record(root, _record(effective=date(2026, 10, 21), fetched=_utc(15, 40, day=date(2026, 10, 21)),
                                          payload=_csv(days=((date(2026, 10, 21), 1, 3.9, 2, 3.9),))))
            self._run(root, _utc(15, 40))
            thursday = json.loads((Path(root) / "gcf" / "2026-10-22.json").read_text(encoding="utf-8"))
            self.assertEqual((thursday["status"], thursday["reason"], thursday["sha256"]), ("missed", "no_run", None))
            self.assertTrue((Path(root) / "gcf" / "2026-10-23.json").exists())
            self.assertEqual(len(self.urls), 1)  # one request, for today only

    def test_the_main_entry_returns_zero_for_a_wait(self):
        with tempfile.TemporaryDirectory() as root:
            self.assertEqual(self.script.main(["capture", "--out-dir", root, "--now", _utc(15, 0).isoformat()]), 0)


class DeclarationTests(unittest.TestCase):
    """The measurement declaration of `dtcc_gcf_repo_index` and the workflow's slots (#962 criterion 1)."""

    ROOT = Path(__file__).resolve().parents[1]

    def test_the_source_is_declared_at_the_reference_date_before_the_decision_and_carries_its_evidence(self):
        from repo_model import measurement_fields

        entry = measurement_fields.load_registry()["dtcc_gcf_repo_index"]
        lag = entry["release_lag"]
        self.assertEqual((lag["basis"], lag["days"], lag["unit"], lag["timezone"]), ("ref_date", 0, "business_days", "America/New_York"))
        self.assertEqual(lag["available_time"], "15:30")
        self.assertLessEqual(lag["available_time"], "16:00")
        self.assertIn("fact sheet", entry["availability_provenance"]["publication"])
        self.assertIn("NOT", entry["availability_provenance"]["note"])  # what was and was not re-read is stated

    def test_no_published_declaration_reads_it(self):
        from repo_model import contract

        published = (self.ROOT / "metadata" / "sources.json").read_text(encoding="utf-8")
        self.assertNotIn("dtcc_gcf_repo_index", published)
        self.assertNotIn("dtcc_gcf_repo_index", str(dict(contract.FEATURE_FIELDS)))

    def test_the_workflow_slots_cover_the_window_in_both_offsets_and_end_after_it(self):
        import re

        text = (self.ROOT / ".github" / "workflows" / "gcf-index-capture.yml").read_text(encoding="utf-8")
        slots = [tuple(int(x) for x in m.groups()) for m in re.finditer(r'- cron: "(\d+) (\d+) \* \* 1-5"', text)]
        self.assertTrue(slots)
        for offset, label in ((-4, "EDT"), (-5, "EST")):
            local = sorted(((h + offset) * 60 + m) for m, h in slots)
            inside = [t for t in local if 15 * 60 + 30 <= t <= 16 * 60]
            self.assertGreaterEqual(len(inside), 4, label)
            self.assertGreater(local[-1], 16 * 60, label)  # a last slot after the decision instant records the miss
        self.assertNotIn("live-log", text.split("jobs:")[1])


if __name__ == "__main__":
    unittest.main()
