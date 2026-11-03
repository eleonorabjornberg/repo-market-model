"""The end-of-day dating of the immediate-release announcements (#1367, item 5): hand cases, no walk.

The sensitivity moves only the announcement instant of the records whose file says "immediate" in
`metadata/announcement_release_times_1301.json`, to 23:59:59 on `announcemt_date`, and nothing else.
"""

from __future__ import annotations

import importlib.util
import json
import unittest
from datetime import date, datetime, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("announcement_eod_sensitivity_1367", REPO / "scripts" / "announcement_eod_sensitivity_1367.py")
eod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(eod)
from repo_model import net_settlement as ns, settlement_dating as sd  # noqa: E402


class TestImmediateSet(unittest.TestCase):
    def test_the_committed_record_names_163(self):
        record = json.loads((REPO / "metadata" / "announcement_release_times_1301.json").read_text(encoding="utf-8"))
        self.assertEqual(len(eod.immediate_files(record)), 163)

    def test_only_immediate_files_are_chosen(self):
        record = {"stated": {"A_1.pdf": "11:00", "A_2.pdf": "immediate", "A_3.pdf": "unreadable"}}
        self.assertEqual(eod.immediate_files(record), frozenset({"A_2.pdf"}))


class TestShift(unittest.TestCase):
    records = [{"pdf_filenm_announcemt": "A_1.pdf"}, {"pdf_filenm_announcemt": "A_2.pdf"}]

    def test_net_auction_moves_only_the_chosen_record(self):
        noon = datetime(2026, 1, 5, 12, 0)
        auctions = (ns.Auction(date(2026, 1, 12), "Bill", True, 1.0, 1.0, 0.0, noon, None, True),
                    ns.Auction(date(2026, 1, 12), "Bill", True, 1.0, 1.0, 0.0, noon, None, False))
        out = eod.shift_auctions(self.records, auctions, frozenset({"A_2.pdf"}))
        self.assertEqual(out[0].announced_at, noon)
        self.assertEqual(out[1].announced_at, datetime(2026, 1, 5, 23, 59, 59))
        self.assertEqual(out[1]._replace(announced_at=noon), auctions[1])

    def test_result_moves_only_the_chosen_record(self):
        noon = datetime(2026, 1, 5, 12, 0)
        results = (sd.AuctionResult(date(2026, 1, 12), "treasury_settlement_bills", 1.0, noon),
                   sd.AuctionResult(date(2026, 1, 12), "treasury_settlement_bills", 1.0, noon))
        out = eod.shift_results(self.records, results, frozenset({"A_1.pdf"}))
        self.assertEqual(out[0].public_at, datetime(2026, 1, 5, 23, 59, 59))
        self.assertEqual(out[1].public_at, noon)

    def test_a_length_mismatch_raises(self):
        with self.assertRaises(ValueError):
            eod.shift_results(self.records, (), frozenset())


if __name__ == "__main__":
    unittest.main()
