"""The announcement matching of `scripts/repo_test_trades_872.py` (#872): which Fed repo operations are announced exercises.

The script changes no classification and adds no availability guard to `src/`; these tests pin what it reports.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("repo_test_trades_872_script", REPO / "scripts" / "repo_test_trades_872.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)


def operation(day, release, close, term="Overnight"):
    return {"operationDate": day, "releaseTime": release, "closeTime": close, "term": term}


class AnnouncementMatchTests(unittest.TestCase):
    def test_a_morning_exercise_inside_its_announced_window_is_matched(self):
        entry = script.announcement(operation("2025-10-08", "10:15", "10:30"))
        self.assertEqual(entry[0], "statement_251002.html")

    def test_the_regular_afternoon_operation_on_an_announced_date_is_not(self):
        self.assertIsNone(script.announcement(operation("2025-10-08", "13:30", "13:45")))

    def test_the_recurring_afternoon_trade_has_no_announcement(self):
        self.assertIsNone(script.announcement(operation("2025-07-08", "13:29", "13:45")))

    def test_a_statement_is_public_the_day_before_its_operation(self):
        entry = script.announcement(operation("2025-10-08", "10:15", "10:30"))
        self.assertTrue(script.public_before(entry, operation("2025-10-08", "10:15", "10:30")))
        self.assertFalse(script.public_before(entry, operation("2025-10-02", "10:15", "10:30")))


class SourceTests(unittest.TestCase):
    def test_the_saved_statements_match_their_checksums_and_dates(self):
        script.check_sources()

    def test_a_changed_page_is_refused(self):
        path = script.SOURCES / "statement_251002.html"
        original = path.read_bytes()
        try:
            path.write_bytes(original + b" ")
            with self.assertRaises(ValueError):
                script.check_sources()
        finally:
            path.write_bytes(original)

    def test_every_announced_exercise_in_the_snapshots_is_already_flagged_by_its_note(self):
        listed = script.listing()
        announced = [row for row in listed if row["announced"]]
        self.assertTrue(announced)
        self.assertTrue(all(row["note_says_sve"] for row in announced))
        self.assertFalse(any(row["announced"] for row in listed if row["release"] == "13:30"))


class RuleTests(unittest.TestCase):
    def test_the_rule_in_force_is_826s_whole_million_trades_up_to_seven_million_only(self):
        self.assertEqual(script._rule_current({}, 7_000_000), 0)
        self.assertEqual(script._rule_current({}, 8_000_000), 8_000_000)
        self.assertEqual(script._rule_current({}, 100_000_000), 100_000_000)
        self.assertEqual(script._rule_current({}, 7_500_000), 7_500_000)

    def test_the_superseded_floor_is_kept_for_comparison_only(self):
        self.assertEqual(script._rule_superseded_floor({}, 99_999_999), 0)
        self.assertEqual(script._rule_superseded_floor({}, 100_000_000), 100_000_000)
        self.assertEqual(script.RULES[0][1], script._rule_current)

    def test_the_announced_rule_leaves_a_not_announced_operation_to_the_rule_in_force(self):
        self.assertEqual(script._rule_announced(operation("2025-07-08", "13:29", "13:45"), 100_000_000), 100_000_000)
        self.assertEqual(script._rule_announced(operation("2025-10-08", "10:15", "10:30"), 150_000_000), 0)
        self.assertEqual(script._rule_announced(operation("2025-07-08", "13:29", "13:45"), 5_000_000), 0)


class RulingTests(unittest.TestCase):
    """The ruling of 17 October 2026 on #860 applied to the listed operations (no size cutoff in the rule)."""

    def test_the_ruling_drops_the_listed_operations_with_no_note_and_no_announcement(self):
        listed = [row for row in script.listing() if not row["announced"] and not row["note_says_sve"]]
        self.assertEqual(len(listed), 35)
        op = {"operationId": listed[0]["operationId"], "operationDate": listed[0]["date"]}
        self.assertEqual(script._rule_ruling(op, 100_000_000), 0)

    def test_the_ruling_leaves_an_operation_outside_the_list_to_the_rule_in_force(self):
        op = {"operationId": "repo-not-listed", "operationDate": "2025-07-08"}
        self.assertEqual(script._rule_ruling(op, 100_000_000), 100_000_000)
        self.assertEqual(script._rule_ruling(op, 5_000_000), 0)

    def test_the_ruling_is_the_fourth_reading_and_the_rule_in_force_stays_the_first(self):
        self.assertEqual([name for name, _rule in script.RULES][-1], "ruling of 17 Oct 2026 (listed unannounced, no note)")
        self.assertEqual(script.RULES[0][1], script._rule_current)

    def test_the_ruling_is_a_list_not_a_size_cutoff(self):
        listed = {row["operationId"] for row in script.listing() if not row["announced"] and not row["note_says_sve"]}
        self.assertEqual(script._ruling_ids(), listed)
        near = {"operationId": "repo-near-band", "operationDate": "2025-07-08"}
        self.assertEqual(script._rule_ruling(near, 101_000_000), 101_000_000)


if __name__ == "__main__":
    unittest.main()
