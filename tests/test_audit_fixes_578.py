"""The before-and-after report of the re-score after the audit's construction fixes (#578): `scripts/audit_fixes_578.py`.

The report reads result documents of the judge's shape. These tests build two small documents, one per side of the
change, and check what the page says: both sides of each row, the weighted count beside the flat one, the years with
2018, 2020 and 2024 called out, and a verdict that moved named at the head.
"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _script():
    spec = importlib.util.spec_from_file_location("audit_fixes_578_script", ROOT / "scripts" / "audit_fixes_578.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


S = _script()


def document(flagged, tier1, weighted_fa=1.5):
    near = {
        "onsets": 26, "onsets_flagged": flagged, "recall": {"mean": flagged / 26, "interval": {"lower": 0.1, "upper": 0.6}},
        "worst_weighted_false_alarms_per_onset": weighted_fa, "worst_false_alarms_per_onset": 3.2,
    }
    table = (
        "Table 1.\n\n| model | onsets flagged | recall [90%] | clim | fa | tier 3 | regimes | tier 5 | pass | scarce |\n"
        "|---|---|---|---|---|---|---|---|---|---|\n"
        "| m | 5 of 26 | 0.2 | 0.1 | 3.20 flat | 0.5 / 0.0 | 2 of 4 | yes, no | fail | fail |\n"
    )
    return {
        "judge": {"weighted": {"m": {
            "onset_warning": {"lead_at_least_1": near, "lead_at_least_3": dict(near)},
            "verdict": {
                "tier_1_onset_warning": tier1, "tier_3_no_crying_wolf": False, "tier_5_week_ahead": True, "passes": False,
            },
        }}},
        "readings": {"weighted": {"m": {"b1": {"1": {"onsets_flagged": flagged, "false_alarms_per_onset_weighted": 0.5, "passes": tier1}}}}},
        "judge_tables": {"weighted": table},
        "by_year": {"m": {"2018": [4, 0], "2019": [13, flagged], "2020": [2, 1]}},
    }


class ReportTests(unittest.TestCase):
    def test_a_row_is_summarised_from_the_weighted_judge_and_its_table(self):
        s = S.summary(document(7, True), "m")
        self.assertEqual((s["flagged"], s["onsets"]), (7, 26))
        self.assertEqual(s["weighted_fa"], 1.5)
        self.assertEqual(s["flat_fa"], 3.2)
        self.assertEqual(s["tier3_flags"], "0.5 / 0.0")
        self.assertEqual(s["tier5_cell"], "yes, no")
        self.assertEqual(s["years"]["2018"], [4, 0])

    def test_a_row_the_document_lacks_is_none(self):
        self.assertIsNone(S.summary(document(7, True), "other"))

    def test_both_sides_are_printed_and_the_called_out_years_are_bold(self):
        before, after = {"m": S.summary(document(5, False), "m")}, {"m": S.summary(document(9, True), "m")}
        text = "\n".join(S.tier_table(before, after, ["m"]) + S.year_table(before, after, ["m"]))
        self.assertIn("| m | before | 5 of 26", text)
        self.assertIn("|  | after | 9 of 26", text)
        self.assertIn("1.50 (3.20)", text)
        self.assertIn("**2018**", text)
        self.assertIn("**2020**", text)
        self.assertNotIn("**2019**", text)

    def test_a_verdict_that_moves_is_named_and_one_that_does_not_is_not(self):
        before, after = {"m": S.summary(document(5, False), "m")}, {"m": S.summary(document(9, True), "m")}
        moved = S.changed_verdicts("Title", before, after, ["m"])
        self.assertEqual(moved, ["- Title: `m`: tier 1 no to yes"])
        self.assertEqual(S.changed_verdicts("Title", before, before, ["m"]), [])


if __name__ == "__main__":
    unittest.main()
