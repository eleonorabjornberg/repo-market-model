"""`scripts/desk_test_marks_933.py` (#933): the take-up figures under the Desk-test marks, on the tracked snapshots."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("desk_test_marks_933_script", ROOT / "scripts" / "desk_test_marks_933.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)


class MarkedWithoutNoteTests(unittest.TestCase):
    def test_the_six_operations_of_the_finding_are_listed(self):
        rows = script.marked_without_note()
        self.assertEqual(
            [(r["date"], r["operation_id"]) for r in rows],
            [
                ("2020-06-17", "RP 061720 99"),
                ("2020-10-07", "RP 100720 99"),
                ("2021-05-26", "RP 052621 99"),
                ("2023-03-08", "RP 030823 1"),
                ("2023-05-23", "RP 052323 99"),
                ("2024-09-24", "RP 092424 1"),
            ],
        )

    def test_the_note_only_reading_is_the_rule_before_the_change(self):
        self.assertTrue(script._note_only({"note": "This is a Small Value Exercise"}))
        self.assertFalse(script._note_only({"operationType": "Repo", "operationId": "RP 100720 99", "note": ""}))

    def test_the_split_pattern_is_counted_not_dropped(self):
        days = script.split_pattern()
        self.assertEqual(len(days), 13)
        self.assertIn("2024-09-16", days)

    def test_the_srf_total_moves_on_the_id_99_overnight_operation_only(self):
        old, new = script.srf_totals(marks=False), script.srf_totals(marks=True)
        moved = sorted(d.isoformat() for d in set(old) | set(new) if old.get(d) != new.get(d))
        self.assertEqual(moved, ["2023-05-23"])
        self.assertEqual(new[next(d for d in new if d.isoformat() == "2023-05-23")], 0.0)


if __name__ == "__main__":
    unittest.main()
