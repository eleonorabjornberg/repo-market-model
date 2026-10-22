"""`scripts/afternoon_test_trade_938.py` (#938): the afternoon test-trade rule's overlap and take-up figures, on the tracked snapshots."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("afternoon_test_trade_938_script", ROOT / "scripts" / "afternoon_test_trade_938.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)


class ListingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = script.listing()

    def test_the_listing_is_the_35_unnoted_operations_of_884(self):
        self.assertEqual(len(self.rows), 35)
        self.assertEqual(len({r["operation_id"] for r in self.rows}), 35)
        self.assertTrue(all(r["note"] == "" for r in self.rows))

    def test_the_rule_catches_32_and_the_desk_marks_catch_none_of_them(self):
        self.assertEqual(sum(r["caught_by_pattern"] for r in self.rows), 32)
        self.assertEqual(sum(r["caught_by_desk_marks"] for r in self.rows), 0)

    def test_the_three_it_misses(self):
        missed = sorted(r["operation_id"] for r in self.rows if not r["caught_by_pattern"])
        self.assertEqual(missed, ["RP 040826 25", "RP 043025 2", "RP 071526 25"])

    def test_the_marked_questions_are_listed(self):
        marked = script.marked_questions(self.rows)
        self.assertEqual(sorted(marked["released_1329"]), ["RP 022224 2", "RP 070825 3"])
        self.assertEqual(marked["ten_million_side_line"], ["RP 043025 2"])
        self.assertEqual(len(marked["full_allotment_no_rate"]), 8)
        self.assertEqual(marked["near_band_edge"], [])


class SrfTests(unittest.TestCase):
    def test_the_srf_total_moves_on_the_caught_overnight_dates_only(self):
        old, new = script.srf_totals(pattern=False), script.srf_totals(pattern=True)
        moved = [d for d in set(old) | set(new) if old.get(d) != new.get(d)]
        self.assertTrue(moved)
        self.assertTrue(all(new[d] <= old[d] for d in moved))


if __name__ == "__main__":
    unittest.main()
