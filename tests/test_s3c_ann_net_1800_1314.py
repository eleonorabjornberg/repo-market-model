"""`scripts/s3c_ann_net_1800_1314.py` (#1314; H5 step 3, development tier): the candidate and its comparison re-made at the 18:00 decision instant.

Written first, against `metadata/s3c_ann_net_1800_1314.json`. The study re-runs #1288's and #1320's scripts unchanged at the 18:00 instant, so what it adds is
arithmetic and two guards, pinned here on hand cases: the figure-by-figure comparison of an 18:00 record with the 16:00 record at the same paths, the paired
18:00-against-16:00 row, B3 scored on its own five levels at lead 1, the refusal of a 16:00 cells file that is not the 16:00 walk of this panel, and the refusal
to make an 18:00 page at any other decision instant.

**Recorded mutation** (30 October 2026), in `require_instant` (the page says it was made at 18:00, so a run at another instant is refused): the line

    if decision_time != INSTANT_TIME:

was changed to `if False:`. `InstantTests.test_a_run_at_another_instant_is_refused` then failed with `AssertionError: ValueError not raised`; restored, it
passes. Second mutation, in `check_cells` (the 16:00 side of the paired row must be the 16:00 walk of the same panel): the line

    if doc.get("instant") != EARLIER_TEXT:

was changed to `if False:`. `CellsFileTests.test_a_file_made_at_another_instant_is_refused` then failed with `AssertionError: ValueError not raised`.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import date, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("s3c_ann_net_1800_1314", ROOT / "scripts" / "s3c_ann_net_1800_1314.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["s3c_ann_net_1800_1314"] = script
_spec.loader.exec_module(script)


class InstantTests(unittest.TestCase):
    def test_the_declared_instant_is_eighteen_hundred(self):
        self.assertEqual(script.INSTANT_TIME, time(18, 0))
        self.assertEqual(script.INSTANT_TEXT, "18:00")
        self.assertEqual(script.EARLIER_TEXT, "16:00")

    def test_the_run_at_the_declared_instant_passes(self):
        script.require_instant(time(18, 0))

    def test_a_run_at_another_instant_is_refused(self):
        with self.assertRaises(ValueError):
            script.require_instant(time(16, 0))

    def test_the_repository_reads_the_declared_instant(self):
        from repo_model import decision_instant

        script.require_instant(decision_instant.DECISION_TIME)


class CompareTests(unittest.TestCase):
    def test_numeric_leaves_are_flattened_by_path_and_booleans_and_text_are_left_out(self):
        flat = script.flatten({"a": {"b": 1, "c": [2.0, 3.0], "t": "x", "f": True}, "n": None})
        self.assertEqual(flat, {"a/b": 1.0, "a/c/0": 2.0, "a/c/1": 3.0})

    def test_equal_records_have_no_difference(self):
        r = {"a": {"b": 1.5, "c": [0.25, 0.5]}}
        out = script.compare(r, {"a": {"b": 1.5, "c": [0.25, 0.5]}})
        self.assertEqual((out["compared"], out["differ"], out["max_abs"]), (3, 0, 0.0))
        self.assertEqual(out["paths"], [])

    def test_a_difference_is_counted_and_its_path_listed(self):
        out = script.compare({"a": {"b": 1.5, "c": 2.0}}, {"a": {"b": 1.5, "c": 2.25}})
        self.assertEqual((out["compared"], out["differ"]), (2, 1))
        self.assertAlmostEqual(out["max_abs"], 0.25)
        self.assertEqual([p["path"] for p in out["paths"]], ["a/c"])
        self.assertEqual((out["paths"][0]["new"], out["paths"][0]["old"]), (2.0, 2.25))

    def test_a_difference_inside_the_tolerance_is_not_one(self):
        out = script.compare({"x": 1.0}, {"x": 1.0 + 1e-12})
        self.assertEqual(out["differ"], 0)

    def test_a_figure_in_one_record_only_is_reported_not_ignored(self):
        out = script.compare({"a": 1.0, "new": 2.0}, {"a": 1.0, "old": 3.0})
        self.assertEqual(out["only_new"], ["new"])
        self.assertEqual(out["only_old"], ["old"])
        self.assertEqual(out["compared"], 1)

    def test_a_nan_in_both_is_equal_and_in_one_is_a_difference(self):
        nan = float("nan")
        self.assertEqual(script.compare({"x": nan}, {"x": nan})["differ"], 0)
        self.assertEqual(script.compare({"x": nan}, {"x": 1.0})["differ"], 1)


def _cells(scores, panel="p"):
    """A cells file: one window, two decision days, two leads, one model, three scores per cell."""

    return {"instant": "16:00", "commit": "c", "panel_sha256": panel, "models": ["m"],
            "windows": {"w": {"cells": [[d, h, [list(s)]] for (d, h), s in scores.items()]}}}


KEYS = [("2025-01-02", 1), ("2025-01-02", 2), ("2025-01-03", 1), ("2025-01-03", 2)]


class CellsFileTests(unittest.TestCase):
    def test_a_file_of_the_16_00_walk_of_the_same_panel_passes(self):
        script.check_cells(_cells({k: (1.0, 2.0, 0.1) for k in KEYS}), "p")

    def test_a_file_made_at_another_instant_is_refused(self):
        doc = _cells({k: (1.0, 2.0, 0.1) for k in KEYS})
        doc["instant"] = "18:00"
        with self.assertRaises(ValueError):
            script.check_cells(doc, "p")

    def test_a_file_of_another_panel_is_refused(self):
        with self.assertRaises(ValueError):
            script.check_cells(_cells({k: (1.0, 2.0, 0.1) for k in KEYS}, panel="other"), "p")


class PairedTests(unittest.TestCase):
    def rows(self, old, new):
        return script.paired_cells(_cells(new)["windows"]["w"]["cells"], _cells(old)["windows"]["w"]["cells"], 0)

    def test_equal_scores_give_zero_difference_on_every_cell(self):
        same = {k: (1.0, 2.0, 0.1) for k in KEYS}
        out = script.paired_summary(self.rows(same, dict(same)))
        self.assertEqual((out["cells"], out["days"], out["differing_cells"], out["max_abs"]), (4, 2, 0, 0.0))
        for j in range(3):
            self.assertEqual(out["scores"][j]["difference"], 0.0)
            self.assertEqual(out["scores"][j]["interval"], [0.0, 0.0])
            self.assertTrue(out["scores"][j]["identical"])

    def test_the_difference_is_16_00_less_18_00_so_positive_favours_the_new_instant(self):
        old = {k: (2.0, 2.0, 0.2) for k in KEYS}
        new = {k: (1.5, 2.0, 0.2) for k in KEYS}
        out = script.paired_summary(self.rows(old, new))
        self.assertAlmostEqual(out["scores"][0]["difference"], 0.5)
        self.assertEqual(out["differing_cells"], 4)
        self.assertFalse(out["scores"][0]["identical"])
        self.assertTrue(out["scores"][1]["identical"])

    def test_the_leads_of_a_day_are_averaged_before_the_days_are_compared(self):
        old = {("2025-01-02", 1): (3.0, 0.0, 0.0), ("2025-01-02", 2): (1.0, 0.0, 0.0), ("2025-01-03", 1): (2.0, 0.0, 0.0), ("2025-01-03", 2): (2.0, 0.0, 0.0)}
        new = {k: (v[0] - 1.0, 0.0, 0.0) if k[0] == "2025-01-02" else v for k, v in old.items()}
        out = script.paired_summary(self.rows(old, new))
        self.assertEqual(out["days"], 2)
        self.assertAlmostEqual(out["scores"][0]["difference"], 0.5)  # one day moved by 1.0, the other by 0

    def test_cells_that_do_not_cover_the_same_days_and_leads_are_refused(self):
        old = {k: (1.0, 2.0, 0.1) for k in KEYS}
        new = {k: (1.0, 2.0, 0.1) for k in KEYS[:3]}
        with self.assertRaises(ValueError):
            self.rows(old, new)


class B3Tests(unittest.TestCase):
    LEVELS = (0.05, 0.25, 0.5, 0.75, 0.95)

    def grid(self, value):
        from repo_model import scoring_protocol as sp

        return [value] * len(sp.GRID)

    def test_the_candidate_is_read_at_the_five_levels_and_scored_there(self):
        from repo_model import scoring_protocol as sp

        flat = self.grid(1.0)
        s = script.five_level_score(flat, 3.0, self.LEVELS)
        self.assertAlmostEqual(s, sp.level_crps(self.LEVELS)([1.0] * 5, 3.0))
        self.assertGreater(s, 0.0)

    def test_a_perfect_five_level_forecast_scores_zero(self):
        self.assertAlmostEqual(script.five_level_score(self.grid(2.0), 2.0, self.LEVELS), 0.0)

    def test_the_published_day_must_carry_the_same_outcome(self):
        daily = {"2025-01-03": {"actual_bps": 4.0, "quantiles_bps": [1.0] * 5}}
        with self.assertRaises(ValueError):
            script.b3_score(daily, date(2025, 1, 3), 5.0, self.LEVELS)
        self.assertGreaterEqual(script.b3_score(daily, date(2025, 1, 3), 4.0, self.LEVELS), 0.0)

    def test_a_day_the_published_record_does_not_cover_is_none(self):
        self.assertIsNone(script.b3_score({}, date(2025, 1, 3), 4.0, self.LEVELS))


class PageTests(unittest.TestCase):
    def test_a_page_says_it_was_made_at_18_00_and_links_the_16_00_pages_it_replaces(self):
        head = script.banner()
        self.assertIn("18:00", head)
        for link in script.EARLIER_PAGES:
            self.assertIn(link, head)
            self.assertTrue((ROOT / "docs" / "research" / link).exists(), link)

    def test_the_two_columns_are_printed_for_a_diff_row(self):
        row = {"cells": 5, "units": 5, "grid_crps": {"mean_d": 0.1, "interval": [0.0, 0.2], "reading": "undecided", "skill": -0.01},
               "brier_gt5": {"mean_d": 0.0, "interval": None, "reading": "not read", "skill": 0.0}}
        lines = script.two_column_table({"g": row}, {"g": row}, ("grid_crps", "brier_gt5"), "group")
        self.assertEqual(len(lines), 3)
        self.assertIn("18:00", lines[0])
        self.assertIn("16:00", lines[0])
        self.assertEqual(lines[2].count("+0.100"), 2)


if __name__ == "__main__":
    unittest.main()
