"""The H5 milestone marks after Eleonora's ruling on #1354 Q3, option 2 (#1484).

H5.M2 and H5.M4 stay marked and each carries a caveat that the result rests on a provisional model, citing its
register row. H5.M5a is marked on the validation report rewritten for (s3c-ann-net) (#1442, merged as #1452), not on
the report for the older candidate (#846).
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKS = json.loads((ROOT / "docs/research/milestones.json").read_text(encoding="utf-8"))["milestones"]


class MilestoneMarks1484(unittest.TestCase):
    def test_m2_and_m4_stay_marked_with_a_caveat_citing_the_register_row(self):
        for key, row in (("H5.M2", "row 2"), ("H5.M4", "row 5")):
            self.assertIn(key, MARKS)
            caveat = MARKS[key].get("caveat", "")
            self.assertIn("provisional", caveat, key)
            self.assertIn("provisional-calendar-register.md", caveat, key)
            self.assertIn(row, caveat, key)

    def test_m5a_rests_on_the_rewritten_report_not_the_older_candidate_s(self):
        self.assertEqual(MARKS["H5.M5a"]["pr"], "eleonorabjornberg/repo-market-model#1452")
        self.assertEqual(MARKS["H5.M5a"]["evidence"], "docs/model/validation.md")


if __name__ == "__main__":
    unittest.main()
