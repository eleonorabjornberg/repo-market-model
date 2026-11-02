"""The release-time check of #1301 (read for #1310): parsing, counting and the committed record. No network.

`scripts/announcement_release_times_1301.py fetch` needs treasurydirect.gov and pdftotext; everything here runs on fixture text and on the
committed record `metadata/announcement_release_times_1301.json`, whose summary must be what its own stated times give on the tracked snapshot.
"""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "announcement_release_times_1301.py"
RECORD = REPO / "metadata" / "announcement_release_times_1301.json"


def _script():
    spec = importlib.util.spec_from_file_location("announcement_release_times_1301", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


art = _script()


def _record(name, kind="Bill", cmb="No", announced="2026-01-05", issued="2026-01-12"):
    return {"pdf_filenm_announcemt": name, "security_type": kind, "cash_management_bill_cmb": cmb, "announcemt_date": announced, "issue_date": issued}


class ParseTests(unittest.TestCase):
    def test_a_stated_time_is_read_on_a_24_hour_clock(self):
        self.assertEqual(art.parse_release("   Embargoed Until 11:00 A.M.   CONTACT"), "11:00")
        self.assertEqual(art.parse_release("Embargoed Until 04:15 P.M."), "16:15")
        self.assertEqual(art.parse_release("Embargoed Until 12:50 P.M."), "12:50")
        self.assertEqual(art.parse_release("Embargoed Until 12:05 A.M."), "00:05")

    def test_a_colon_after_until_and_no_periods_are_read(self):
        self.assertEqual(art.parse_release("Embargoed Until: 9:30 AM"), "09:30")

    def test_for_immediate_release_is_its_own_class_and_no_text_is_unreadable(self):
        self.assertEqual(art.parse_release("FOR IMMEDIATE RELEASE\nJune 11, 2020"), art.IMMEDIATE)
        self.assertEqual(art.parse_release("a page with no release line"), art.UNREADABLE)


class SummaryTests(unittest.TestCase):
    RECORDS = [
        _record("A_1.pdf"),
        _record("A_2.pdf", cmb="Yes"),
        _record("A_3.pdf", kind="Note", announced="2019-08-15", issued="2019-08-30"),
        _record("A_4.pdf", announced="2018-12-04", issued="2018-12-11"),
        _record("A_5.pdf", cmb="Yes"),
    ]
    STATED = {"A_1.pdf": "11:00", "A_2.pdf": "11:00", "A_3.pdf": "16:15", "A_4.pdf": "13:30", "A_5.pdf": art.IMMEDIATE}

    def test_counts_by_time_and_class_and_the_late_ones_are_listed(self):
        out = art.summarise(self.RECORDS, self.STATED)
        self.assertEqual(out["by_stated_time_and_class"]["11:00"], {"bills": 1, "cash_management_bills": 1})
        self.assertEqual([r["file"] for r in out["after_decision_16_00"]], ["A_3.pdf"])
        self.assertEqual(out["after_decision_16_00"][0]["weekdays_to_settlement"], 11)
        self.assertEqual([r["file"] for r in out["after_declared_12_00_to_decision_16_00"]], ["A_4.pdf"])
        self.assertEqual(out["for_immediate_release"], {"total": 1, "by_class": {"cash_management_bills": 1}})

    def test_a_file_with_no_stated_time_is_refused(self):
        with self.assertRaises(ValueError):
            art.summarise(self.RECORDS, {"A_1.pdf": "11:00"})


class CommittedRecordTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads(RECORD.read_text(encoding="utf-8"))
        self.records = art.load_records()

    def test_the_summary_is_what_the_stated_times_give_on_the_tracked_snapshot(self):
        self.assertEqual(art.summarise(self.records, self.record["stated"]), self.record["summary"])

    def test_every_announcement_file_is_covered_and_none_failed(self):
        self.assertEqual(set(self.record["stated"]), {r["pdf_filenm_announcemt"] for r in self.records})
        self.assertEqual(self.record["failed"], {})
        self.assertNotIn(art.UNREADABLE, self.record["stated"].values())

    def test_the_one_after_the_decision_is_the_2019_coupon(self):
        late = self.record["summary"]["after_decision_16_00"]
        self.assertEqual([r["file"] for r in late], ["A_20190815_3.pdf"])
        self.assertEqual(late[0]["stated"], "16:15")


if __name__ == "__main__":
    unittest.main()
