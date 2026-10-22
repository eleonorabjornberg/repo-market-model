"""H5 reporting (#1021): development pages read the studentized bound on mean d, not the skill interval.

The script is `scripts/mean_d_reading_1021.py`. It reads the tracked results of #959 and #965 (no re-scoring) and writes a
new page for each; the originals stand. Eleonora's ruling on #1009 (relayed 20 October 2026): report the skill interval and
the studentized mean-d bound side by side, and read the mean-d bound, as the verdict does (ruling 1/5).

Red on main: the script does not exist there, and the two original scripts' `verdict_words` read `skill_interval`
(`test_the_originals_still_read_the_skill_interval` pins that they stand).

Recorded mutation (2026-10-22), for `verdict_words`: replacing `low, high = row["difference_interval"]` with
`low, high = row["skill_interval"]` made `test_the_reading_follows_the_mean_d_bound` fail with AssertionError
('no difference' != 'candidate worse'). Restored, it passes.
"""

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


script = load("mean_d_reading_1021", "mean_d_reading_1021.py")
s959 = load("turn_day_labels_959", "turn_day_labels_959.py")
s965 = load("tax_date_october_965", "tax_date_october_965.py")

# B2's resolvable loss to B1 on tax dates (#965's result.json): d = -2.27 bp [-3.71, -1.37], skill [-119.5%, +54.0%]
DISAGREE = {"skill_interval": [-1.195, 0.540], "difference_interval": [-3.71, -1.37], "difference": -2.27}


class ReadingTests(unittest.TestCase):
    def test_the_reading_follows_the_mean_d_bound(self):
        self.assertEqual(script.verdict_words(DISAGREE), "candidate worse")
        self.assertEqual(script.verdict_words({"skill_interval": [-0.1, 0.1], "difference_interval": [0.01, 0.2]}), "candidate better")
        self.assertEqual(script.verdict_words({"skill_interval": [0.01, 0.2], "difference_interval": [-0.1, 0.1]}), "no difference")
        self.assertEqual(script.verdict_words({"undefined": "x", "difference": 0.0}), "scores identical")
        self.assertEqual(script.verdict_words({"undefined": "x", "difference": 0.3}), "undefined")

    def test_the_originals_still_read_the_skill_interval(self):
        for module in (s959, s965):
            self.assertEqual(module.verdict_words(DISAGREE), "no difference")
        self.assertEqual(script.skill_words(DISAGREE), "no difference")


class RecordTests(unittest.TestCase):
    def test_every_tested_row_of_both_pages_is_read_and_the_changes_are_exactly_the_disagreements(self):
        for key, path in script.SOURCES.items():
            record = json.loads(path.read_text(encoding="utf-8"))
            rows = script.collect(record)
            self.assertTrue(rows, key)
            for row in rows:
                self.assertEqual(row["reading"], script.verdict_words(row["row"]))
                self.assertEqual(row["changed"], row["reading"] != row["skill_reading"])
            changed = [r for r in rows if r["changed"]]
            self.assertTrue(changed, key)
            self.assertTrue(all(r["skill_reading"] != r["reading"] for r in changed))

    def test_a_row_where_the_two_intervals_agree_in_side_is_not_listed_as_changed(self):
        record = {"comparisons": {"a": {"groups": {"pooled": {"decision_days": 9, "tests": {
            "B1 -> B2": {"days": 9, "benchmark_mean": 1.0, "candidate_mean": 0.9, "difference": 0.1,
                         "skill": 0.1, "skill_interval": [0.02, 0.2], "difference_interval": [0.01, 0.2]}}}}}}}
        (row,) = script.collect(record)
        self.assertFalse(row["changed"])
        self.assertEqual(row["reading"], "candidate better")


class PageTests(unittest.TestCase):
    def test_each_page_shows_both_intervals_the_caveat_and_the_changed_rows(self):
        for key, path in script.SOURCES.items():
            record = json.loads(path.read_text(encoding="utf-8"))
            page = script.render(key, record)
            self.assertIn("understated about 2×", page)
            self.assertIn("optimistic", page)
            self.assertIn("skill [90%]", page)
            self.assertIn("mean d [90%]", page)
            self.assertIn("Rows whose reading changes", page)
            for row in script.collect(record):
                if row["changed"]:
                    self.assertIn(f"| {row['group']} |", page)

    def test_the_tracked_pages_and_record_are_what_the_script_writes(self):
        self.assertEqual(script.main(["check"]), 0)

    def test_no_original_page_is_among_the_files_written(self):
        for page in script.PAGES.values():
            self.assertNotIn(page.name, ("turn-day-labels-959-result.md", "tax-date-october-965-result.md"))


if __name__ == "__main__":
    unittest.main()
