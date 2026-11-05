"""`scripts/split_test_trade_1456.py` (#1456): the days the split test-trade rule reclassifies, on the tracked snapshots."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("split_test_trade_1456_script", ROOT / "scripts" / "split_test_trade_1456.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)


class ReclassifiedTests(unittest.TestCase):
    def test_all_thirteen_ten_zero_ten_days_are_reclassified(self):
        ops = script.reclassified()
        ten = [o["date"] for o in ops if o["ten_zero_ten"]]
        self.assertEqual(len(ten), 13)
        self.assertIn("2024-09-16", ten)
        self.assertIn("2026-07-27", ten)

    def test_the_other_equal_splits_are_listed_apart(self):
        other = [o["date"] for o in script.reclassified() if not o["ten_zero_ten"]]
        self.assertEqual(
            other,
            ["2022-10-19", "2024-09-23", "2025-03-25", "2025-09-22", "2026-03-19", "2026-05-26", "2026-09-03"],
        )

    def test_the_srf_total_moves_on_exactly_the_reclassified_dates(self):
        old, new = script.srf_totals(rule=False), script.srf_totals(rule=True)
        moved = sorted(d.isoformat() for d in set(old) | set(new) if old.get(d) != new.get(d))
        self.assertEqual(moved, sorted(o["date"] for o in script.reclassified()))
        for day in set(old) | set(new):
            if day.isoformat() in moved:
                self.assertEqual(new[day], 0.0)


if __name__ == "__main__":
    unittest.main()
