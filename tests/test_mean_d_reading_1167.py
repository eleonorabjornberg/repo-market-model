"""H1/H5 reporting (#1167): the pages of #941, #1115, #1133 and #1153 read the studentized bound on mean d, not the skill interval.

Her ruling on #1009 (comment 6291059408, 20 October 2026): development pages report both the skill interval and the studentized
mean-d bound, and read the mean-d bound; each page states Lens C's caveat. This module pins four things: the readings in
`scripts/walk_calibration_1133.py` and `scripts/faster_scale_1153.py` follow the mean-d bound, while `metadata/walk_calibration_1133.json`
and `metadata/faster_scale_1153.json` stay as declared before scoring; the original committed pages are still what the scripts give under
`reading="skill"`; `scripts/mean_d_reading_1167.py` reads every paired row of the four committed records without a re-run; and the
tracked new pages and record are what that script writes.

Red on main: `scripts/mean_d_reading_1167.py` does not exist there, `verdict` of the 1133 and 1153 scripts delegates to #941's
skill-interval reading, and `render` takes no `reading` argument.

Recorded mutation (2026-10-23), for `scripts/mean_d_reading_1167.py` `verdict_words`: replacing
`low, high = row["difference_interval"]` with `low, high = row["skill_interval"]` made
`test_the_reading_follows_the_mean_d_bound` fail with AssertionError ('undecided' != 'loss'), and
`test_the_four_records_change_where_the_finding_says` fail with AssertionError (the counts of changed readings were 0).
Restored, both pass. For the 1133 script's `verdict`: replacing `row["difference_interval"]` with `row["skill_interval"]` made
`test_the_scripts_read_the_mean_d_bound` fail with AssertionError ('undecided' != 'loss'). Restored, it passes.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, file):
    if name in sys.modules:  # a worker pool pickles the 1133 and 1153 functions by module name: keep the object another module registered
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


script = load("mean_d_reading_1167", "mean_d_reading_1167.py")
s1133 = load("walk_calibration_1133", "walk_calibration_1133.py")
s1153 = load("faster_scale_1153", "faster_scale_1153.py")
s941 = load("fhs_scale_941", "fhs_scale_941.py")

# #1133, calibrated (a) against the uncalibrated base, 2020: skill [-5.3%, +0.4%] covers zero, d [-0.036, -0.002] bp is below it
DISAGREE = {"skill_interval": [-0.053, 0.004], "difference_interval": [-0.036, -0.002], "difference": -0.02}
LOSS_ON_SKILL = {"skill_interval": [-0.2, -0.01], "difference_interval": [-0.3, 0.1], "difference": -0.1}


def record(key):
    return json.loads(script.SOURCES[key].read_text(encoding="utf-8"))


class ReadingTests(unittest.TestCase):

    def test_the_reading_follows_the_mean_d_bound(self):
        self.assertEqual(script.verdict_words(DISAGREE), "loss")
        self.assertEqual(script.verdict_words(LOSS_ON_SKILL), "undecided")
        self.assertEqual(script.verdict_words({"skill_interval": [-0.1, 0.1], "difference_interval": [0.01, 0.2]}), "gain")
        self.assertEqual(script.verdict_words({"undefined": "x"}), "**no reading** (mean-d bound not computed: x)")  # #1215
        self.assertEqual(script.skill_words(DISAGREE), "undecided")
        self.assertEqual(script.skill_words(LOSS_ON_SKILL), "loss")

    def test_the_scripts_read_the_mean_d_bound(self):
        for module in (s1133, s1153):
            self.assertEqual(module.verdict(DISAGREE), "loss", module.__name__)
            self.assertEqual(module.verdict(LOSS_ON_SKILL), "undecided", module.__name__)
            self.assertEqual(module.verdict({"difference_interval": [0.01, 0.2], "skill_interval": [-0.1, 0.1]}), "gain")
            self.assertEqual(module.verdict({"undefined": "no variance"}), "undecided")
            self.assertEqual(module.skill_verdict(DISAGREE), "undecided", module.__name__)
            self.assertEqual(module.skill_verdict(LOSS_ON_SKILL), "loss", module.__name__)

    def test_the_originals_of_941_and_1115_stand(self):
        self.assertEqual(s941.verdict(DISAGREE), "undecided")  # #941's page is not regenerated: its reading is the one it was written with

    def test_the_declarations_stay_as_declared_before_scoring(self):
        # Eleonora's ruling on the PR (comment 6370129841, option 1): only the scripts and the new pages carry the #1009 rule.
        for name in ("walk_calibration_1133", "faster_scale_1153"):
            declaration = json.loads((ROOT / "metadata" / f"{name}.json").read_text(encoding="utf-8"))
            self.assertNotIn("2026-10-23", [a["date"] for a in declaration["amendments"]], name)
            self.assertNotIn("studentized one-sided bound on mean d", declaration["reading"]["rules"][0], name)


class OriginalPageTests(unittest.TestCase):

    def test_the_committed_pages_of_1133_and_1153_are_what_the_skill_reading_gives(self):
        for module, key in ((s1133, "1133"), (s1153, "1153")):
            data = json.loads(script.SOURCES[key].read_text(encoding="utf-8"))
            page = script.ORIGINALS_DIR / script.ORIGINALS[key]
            self.assertEqual(module.render(data, reading="skill"), page.read_text(encoding="utf-8"), key)

    def test_a_render_that_reads_the_mean_d_bound_says_so_and_states_the_caveat(self):
        for module, key in ((s1133, "1133"), (s1153, "1153")):
            data = json.loads(script.SOURCES[key].read_text(encoding="utf-8"))
            page = module.render(data)
            self.assertIn("studentized bound on mean d", page, key)
            self.assertIn("understated about 2×", page, key)
            self.assertNotEqual(page, module.render(data, reading="skill"), key)


class RecordTests(unittest.TestCase):

    def test_every_paired_row_is_read_with_both_intervals(self):
        for key in script.SOURCES:
            rows = script.collect(record(key))
            self.assertTrue(rows, key)
            for row in rows:
                self.assertEqual(row["reading"], script.verdict_words(row["row"]))
                self.assertEqual(row["skill_reading"], script.skill_words(row["row"]))
                self.assertEqual(row["changed"], row["reading"] != row["skill_reading"])

    def test_the_four_records_change_where_the_finding_says(self):
        """Finding #1163: paired cells 1180, 1190, 287 and 1422, of which 115, 131, 49 and 156 read on the other side of zero."""

        expected = {"941": (1180, 115), "1115": (1190, 131), "1133": (287, 49), "1153": (1422, 156)}
        for key, (rows, changed) in expected.items():
            found = script.collect(record(key))
            self.assertEqual((len(found), sum(r["changed"] for r in found)), (rows, changed), key)

    def test_the_headline_readings_of_1133_move_as_the_finding_says(self):
        data = record("1133")
        arm = s1133.ARM_KEYS[s1133.wc.ARMS[0]]

        def reads(split, label):
            row = data["groups"][split][label]["grid_crps"]["vs"][arm][s1133.BASE]
            return script.verdict_words(row), script.skill_words(row)

        for label in ("2020", "2024", "2025-26"):
            self.assertEqual(reads("regime", label), ("loss", "undecided"), label)
        for label in ("quarter_end", "tax_date"):
            self.assertEqual(reads("pressure_day_type", label), ("undecided", "gain"), label)

    def test_the_headline_readings_of_1153_and_1115_move_as_the_finding_says(self):
        data = record("1153")
        tax = data["groups"]["pressure_day_type"]["tax_date"]["grid_crps"]["vs"]
        self.assertEqual((script.verdict_words(tax["v3_miss"][s1153.BASE]),
                          script.skill_words(tax["v3_miss"][s1153.BASE])), ("gain", "undecided"))
        data = record("1115")
        row = data["groups"]["regime"]["2020"]["grid_crps"]["vs"]["mr_cal_c_location_scale"]["B1"]
        self.assertEqual((script.verdict_words(row), script.skill_words(row)), ("loss", "undecided"))

    def test_a_row_where_the_two_intervals_agree_in_side_is_not_changed(self):
        rec = {"groups": {"pooled": {"all decision days": {"grid_crps": {"vs": {"cand": {"B1": {
            "days": 9, "difference": 0.1, "skill": 0.1, "skill_interval": [0.02, 0.2], "difference_interval": [0.01, 0.2]}}}}}}}}
        (row,) = script.collect(rec)
        self.assertFalse(row["changed"])
        self.assertEqual(row["reading"], "gain")

    def test_a_row_the_scorer_left_undefined_is_not_collected(self):
        rec = {"groups": {"pooled": {"all decision days": {"grid_crps": {"vs": {"cand": {"B1": {"undefined": "no variance"}}}}}}}}
        self.assertEqual(script.collect(rec), [])


class PageTests(unittest.TestCase):

    def test_each_page_shows_both_intervals_the_caveat_and_every_changed_reading(self):
        for key in script.SOURCES:
            data = record(key)
            page = script.render(key, data)
            self.assertIn("understated about 2×", page, key)
            self.assertIn("optimistic", page, key)
            self.assertIn("skill [90%]", page, key)
            self.assertIn("mean d [90%]", page, key)
            self.assertIn("## Readings that change", page, key)
            rows = script.collect(data)
            changed = [r for r in rows if r["changed"]]
            self.assertEqual(page.count("**(was "), 0, key)
            self.assertEqual(page.split("## Readings that change", 1)[1].split("## All paired rows", 1)[0].count("\n| "), len(changed) + 1, key)  # rows and the header; the separator starts "|-"

    def test_the_tracked_pages_and_record_are_what_the_script_writes(self):
        self.assertEqual(script.main(["check"]), 0)

    def test_no_original_page_is_among_the_files_written(self):
        for key, page in script.PAGES.items():
            self.assertNotEqual(page.name, script.ORIGINALS[key])
            self.assertTrue(page.name.endswith("-mean-d-1167-result.md"))


if __name__ == "__main__":
    unittest.main()
