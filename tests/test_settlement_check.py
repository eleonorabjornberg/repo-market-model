"""The settlement driver against Eleonora's pattern (#339): the 15th, month-end, Thursday and Tuesday bills.

`scripts/settlement_check.py` compares the published panel's settlement columns with the pattern she ruled on
(3-, 10- and 30-year settle on the 15th or the next business day; 2-, 5- and 7-year on the last day of the month;
bills mostly on Thursdays, some on Tuesdays), drawn from the tracked Treasury auction snapshot. The tests here
pin the finding: every date of the pattern is flagged, and the check reads nothing after 2025-12-31.

Recorded mutation for the read guard (the lockbox, `docs/decisions/lockbox.md`): in `check`, the `days` filter
`FIRST <= ... <= LAST` was changed to `FIRST <= ...`; `test_no_day_after_the_last_read_day_is_read` then failed
with `AssertionError` (a 2026 date in the output). Restored.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location("settlement_check_under_test",
                                                  ROOT / "scripts" / "settlement_check.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sc = _load()


def _record(issue: str, term: str, kind: str = "Note", floating: str = "No", tips: str = "No") -> dict:
    return {"issue_date": issue, "security_type": kind, "security_term": term, "floating_rate": floating,
            "inflation_index_security": tips, "announcemt_date": "2018-01-01"}


def _panel(start: date, end: date, coupons: set, bills: set) -> list:
    rows, day = [], start
    while day <= end:
        if day.weekday() < 5:
            rows.append({"date": day.isoformat(),
                         "treasury_settlement_coupons": "10" if day in coupons else "0",
                         "treasury_settlement_bills": "10" if day in bills else "0"})
        day += timedelta(days=1)
    return rows


class KindTest(unittest.TestCase):
    def test_names_follow_the_ruling(self):
        self.assertEqual(sc.kind(_record("2019-01-15", "3-Year")), "mid_month")
        self.assertEqual(sc.kind(_record("2019-01-15", "9-Year 11-Month")), "mid_month")
        self.assertEqual(sc.kind(_record("2019-01-31", "5-Year")), "month_end")
        self.assertEqual(sc.kind(_record("2019-01-31", "1-Year 11-Month", floating="Yes")), "other")
        self.assertEqual(sc.kind(_record("2019-01-31", "5-Year", tips="Yes")), "other")
        self.assertEqual(sc.kind(_record("2019-01-15", "20-Year", kind="Bond")), "other")


class CheckTest(unittest.TestCase):
    def test_a_missed_pattern_date_is_reported(self):
        panel = _panel(date(2018, 4, 3), date(2018, 6, 29), coupons={date(2018, 4, 16)}, bills=set())
        out = sc.check(panel, [])
        self.assertIn("2018-04-16", out["pattern_dates"])  # 15 April 2018 is a Sunday
        self.assertIn("2018-04-30", out["pattern_dates_not_flagged"])
        self.assertNotIn("2018-04-16", out["pattern_dates_not_flagged"])

    def test_no_day_after_the_last_read_day_is_read(self):
        panel = _panel(date(2025, 11, 3), date(2026, 2, 27), coupons={date(2026, 1, 15), date(2025, 12, 31)},
                       bills={date(2026, 1, 15)})
        auctions = [_record("2026-01-15", "3-Year"), _record("2025-12-31", "5-Year")]
        out = sc.check(panel, auctions)
        everything = json.dumps(out)
        self.assertNotIn("2026-", everything)


class PublishedPanelTest(unittest.TestCase):
    """The published panel, rebuilt from the tracked fixtures, against the tracked snapshot."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        panel = Path(cls.tmp.name) / "funding_panel.csv"
        subprocess.run(
            [sys.executable, "-m", "repo_model.cli", "build", "--raw-root",
             str(ROOT / "tests/fixtures/snapshots/funding_inputs"), "--output", str(panel),
             "--build-cutoff", "2026-09-08T21:31:42+00:00", "--decision-time", "16:00:00"],
            check=True, capture_output=True, env={"PYTHONPATH": str(ROOT / "src"), "PATH": "/usr/bin:/bin"})
        with panel.open(newline="") as handle:
            rows = [r for r in csv.DictReader(handle) if date.fromisoformat(r["date"]) <= sc.LAST]
        cls.out = sc.check(rows, json.loads(sc.AUCTIONS.read_text())["data"])

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_every_date_of_the_pattern_is_flagged(self):
        self.assertEqual(self.out["pattern_dates_not_flagged"], [])
        self.assertEqual(self.out["pattern_dates_flagged"], len(self.out["pattern_dates"]))

    def test_every_flag_is_a_settlement_the_snapshot_carries(self):
        self.assertEqual(self.out["flagged_without_a_coupon_issue_in_snapshot"], [])

    def test_no_issue_is_announced_after_it_settles(self):
        self.assertEqual(self.out["issue_dates_announced_on_or_after_the_issue_date"], [])

    def test_bills_settle_on_thursdays_and_tuesdays(self):
        weekdays = self.out["bills"]["flagged_by_weekday"]
        self.assertGreater(weekdays["Thu"], weekdays.get("Fri", 0) + weekdays.get("Mon", 0) + weekdays.get("Wed", 0))
        self.assertGreater(weekdays["Tue"], 100)
        self.assertEqual(self.out["bills"]["thursdays_and_tuesdays_since_the_first_without_bills"], [])


if __name__ == "__main__":
    unittest.main()
