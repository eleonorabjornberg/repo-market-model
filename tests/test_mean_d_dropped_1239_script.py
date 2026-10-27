"""`scripts/mean_d_dropped_1239.py` (#1239): the comparison of a re-score with the committed rows, on hand cases."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("mean_d_dropped_1239", ROOT / "scripts" / "mean_d_dropped_1239.py")
script = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(script)

BOUND = {"days": 30, "difference": 0.1, "difference_interval": [0.0, 0.2], "skill": None}
NONE = {"days": 30, "undefined": "a resampled difference has no long-run variance; it cannot be studentized"}
GAINED = {"days": 30, "difference": 0.05, "difference_interval": [-0.1, 0.2], "dropped_resamples": 7, "draws": 100}


class CompareTests(unittest.TestCase):

    def old(self):
        return {"seed": 1, "n": 3, "groups": {"a": {"vs": {"x": dict(BOUND), "y": dict(NONE), "z": dict(NONE)}}}}

    def test_a_no_reading_row_that_gains_a_bound_is_listed_with_its_count(self):
        new = self.old()
        new["groups"]["a"]["vs"]["y"] = dict(GAINED)
        new["groups"]["a"]["vs"]["z"] = dict(NONE, undefined="every one of the 100 resamples has no long-run variance")
        r = script.compare(self.old(), new)
        self.assertEqual([g["path"] for g in r["gained"]], ["groups/a/vs/y"])
        self.assertEqual((r["gained"][0]["dropped_resamples"], r["gained"][0]["draws"]), (7, 100))
        self.assertEqual([g["path"] for g in r["still_no_reading"]], ["groups/a/vs/z"])
        self.assertEqual((r["unchanged_with_bound"], r["moved_with_bound"], r["other_differences"]), (1, [], []))

    def test_a_row_defined_without_dropping_is_not_counted_as_dropped(self):
        new = self.old()
        new["groups"]["a"]["vs"]["y"] = dict(BOUND)
        r = script.compare(self.old(), new)
        self.assertEqual((r["gained"], [g["path"] for g in r["defined_without_dropping"]]), ([], ["groups/a/vs/y"]))

    def test_a_row_with_a_bound_that_moves_is_reported(self):
        """A row with a bound before must be unchanged to the last digit; one that moved is listed."""

        new = self.old()
        new["groups"]["a"]["vs"]["x"] = dict(BOUND, difference_interval=[0.0, 0.2000001])
        r = script.compare(self.old(), new)
        self.assertEqual(r["moved_with_bound"], ["groups/a/vs/x"])
        self.assertEqual(r["unchanged_with_bound"], 0)

    def test_a_difference_outside_the_rows_is_reported(self):
        new = self.old()
        new["n"] = 4
        self.assertEqual(script.compare(self.old(), new)["other_differences"], ["n"])

    def test_the_page_prints_the_count_beside_the_bound_and_reads_nothing(self):
        new = self.old()
        new["groups"]["a"]["vs"]["y"] = dict(GAINED)
        study = script.compare(self.old(), new)
        study.update({"baseline": "committed", "seed": 1226, "draws": 100, "panel_sha256": "ab" * 32})
        page = script.render({"issue": 1239, "studies": {"1226": study}})
        self.assertIn("7 of 100 (7.0%)", page)
        self.assertIn("+0.0500 [-0.1000, +0.2000]", page)
        for word in ("**gain**", "**loss**", "undecided"):
            self.assertNotIn(word, page)


class CommittedScoreTests(unittest.TestCase):

    def test_the_committed_files_are_read_by_the_walker(self):
        for study, path in script.SOURCES.items():
            rows = dict(script.walk(json.loads(path.read_text(encoding="utf-8"))))
            self.assertTrue(rows, study)
            self.assertTrue(any("undefined" in row for row in rows.values()), study)


if __name__ == "__main__":
    unittest.main()
