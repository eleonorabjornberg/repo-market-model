"""The settlement dating's documents say what #1301's check found (#1327, finding #1317; H5 step 3).

Four texts called the announcement dating "measured and off", said Treasury publishes no clock time, or said a cash
management bill is announced the same or the previous day. #1301 read Treasury's own announcement files
(`metadata/announcement_release_times_1301.json`) and found otherwise. These tests keep the corrected texts and the
figures they cite tied to the tracked snapshot, so they cannot drift back.

Tests written first and watched failing against the four texts as they stood on origin/main 54728b2: the stale-phrase tests
raised `AssertionError` (a phrase found), the figure tests raised `AssertionError` (a figure absent from the text).
"""

from __future__ import annotations

import json
import unittest
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "tests/fixtures/snapshots/funding_inputs/treasury_auctions/20260914T051023Z_722359ea9bc7.json"
DATING = ROOT / "metadata/settlement_announcement_dating.json"
NET = ROOT / "metadata/net_settlement.json"
INFO_SET = ROOT / "docs/decisions/information-set.md"
REGISTER = ROOT / "docs/research/provisional-calendar-register.md"
S3C = ROOT / "src/repo_model/s3c_announced.py"
EVIDENCE = ROOT / "metadata/announcement_release_times_1301.json"
PANEL_FIRST = "2018-04-03"


def _records():
    data = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else next(v for v in data.values() if isinstance(v, list))


def _weekdays(start, end):
    a, b, n = date.fromisoformat(start[:10]), date.fromisoformat(end[:10]), 0
    while a < b:
        a += timedelta(1)
        n += a.weekday() < 5
    return n


class StaleTextsTests(unittest.TestCase):
    def test_the_dating_status_no_longer_says_measured_and_off(self):
        status = json.loads(DATING.read_text(encoding="utf-8"))["status"]
        self.assertNotIn("measured and off", status)
        self.assertNotIn("no published declaration reads this file", status)

    def test_the_dating_status_says_which_declarations_read_it(self):
        status = json.loads(DATING.read_text(encoding="utf-8"))["status"]
        for needle in ("metadata/sources.json", "h = 1 only", "h = 2 to 5", "repo_model.s3c_announced", "#1327"):
            self.assertIn(needle, status)

    def test_the_not_verified_notes_are_replaced_by_the_check(self):
        for path in (DATING, NET):
            evidence = json.loads(path.read_text(encoding="utf-8"))["evidence"]
            self.assertNotIn("NOT verified", evidence, path.name)
            self.assertNotIn("Treasury publishes no clock time for an individual announcement", evidence, path.name)
            self.assertIn("metadata/announcement_release_times_1301.json", evidence, path.name)

    def test_the_2020_finding_is_stated_beside_the_evidence(self):
        for path in (DATING, NET):
            evidence = json.loads(path.read_text(encoding="utf-8"))["evidence"]
            self.assertIn("67.5%", evidence, path.name)
            self.assertIn("Table 4d", evidence, path.name)

    def test_the_decision_record_no_longer_says_no_clock_time(self):
        text = INFO_SET.read_text(encoding="utf-8")
        self.assertNotIn("Treasury publishes no clock time for an individual announcement", text)
        self.assertNotIn("Both readings are still off", text)
        self.assertIn("metadata/announcement_release_times_1301.json", text)
        self.assertIn("#1327", text)

    def test_the_register_and_the_module_no_longer_call_the_dating_measured_and_off(self):
        self.assertNotIn("settlement_announcement_dating.json, measured and off", REGISTER.read_text(encoding="utf-8"))
        module = S3C.read_text(encoding="utf-8")
        self.assertNotIn("(#541, measured and off)", module)
        self.assertNotIn("announced the same or the previous day; the 12:00 instant is\nunverified", module)


class FiguresTests(unittest.TestCase):
    """The figures the texts cite are the tree's own."""

    def test_the_stated_time_counts_match_the_1301_evidence(self):
        summary = json.loads(EVIDENCE.read_text(encoding="utf-8"))["summary"]
        evidence = json.loads(DATING.read_text(encoding="utf-8"))["evidence"]
        immediate = summary["for_immediate_release"]
        self.assertEqual(summary["files"] - immediate["total"], 3665)
        self.assertEqual(immediate["total"], 163)
        self.assertEqual(immediate["by_class"]["cash_management_bills"], 153)
        self.assertEqual(summary["by_stated_time_and_class"]["11:00"], {"bills": 2334, "cash_management_bills": 315, "notes_and_bonds": 886})
        for figure in ("3665", "163", "153", "3535"):
            self.assertIn(figure, evidence)

    def test_the_cash_management_bill_recount(self):
        panel = [r for r in _records() if r.get("cash_management_bill_cmb") == "Yes" and r["issue_date"][:10] >= PANEL_FIRST]
        days = Counter(_weekdays(r["announcemt_date"], r["issue_date"]) for r in panel)
        self.assertEqual((len(panel), days[5]), (458, 403))
        evidence = json.loads(DATING.read_text(encoding="utf-8"))["evidence"]
        self.assertIn("403 were announced five Monday-to-Friday days before settlement", evidence)
        self.assertIn("the 458 cash management bills settling inside the panel", evidence)
        self.assertIn("403 of the 458", S3C.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
