"""`scripts/s3_terms_rescore_1243.py` (#1243, #1247; H5 step 3, development tier): the stage-by-stage comparison of a re-score of
#1196's study with its committed score, on hand cases.

Written first. What these tests pin: the reading of a row is the mean-d bound's (#1172, #1215), a row with no bound reads "no
reading"; a reading that moved is classed as improved, worsened, lost or gained (a reading from no reading); a change is attributed
to the first stage at which the row's content differs from the stage before it, never to a later one; a day count that moved is
listed by lead; a difference outside the rows is reported; the stages must share the seed, the draws and the panel digest; and the
page says it supersedes #1196's, names the unattributed changes and never edits the old page.

Mutation (recorded, for the guard that refuses stages scored on different settings): replacing `!=` by `==` in `_same_setup`
made `test_stages_scored_on_other_settings_are_refused` fail with `AssertionError: "draws differs" does not match "stage s1: seed
differs from the first stage ..."` (and every test that compares equal stages raised SystemExit).
"""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("s3_terms_rescore_1243", ROOT / "scripts" / "s3_terms_rescore_1243.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["s3_terms_rescore_1243"] = script
_spec.loader.exec_module(script)

GAIN = {"days": 30, "difference": 0.1, "difference_interval": [0.01, 0.2], "skill": 0.1, "skill_interval": [0.0, 0.2]}
LOSS = {"days": 30, "difference": -0.1, "difference_interval": [-0.2, -0.01], "skill": -0.1, "skill_interval": [-0.2, 0.0]}
UNDECIDED = {"days": 30, "difference": 0.01, "difference_interval": [-0.1, 0.2], "skill": 0.0, "skill_interval": [-0.1, 0.1]}
NONE = {"days": 30, "undefined": "a resampled difference has no long-run variance; it cannot be studentized"}


def doc(rows, days=(10, 20)):
    return {"seed": 1196, "draws": 100, "panel_sha256": "ab" * 32,
            "groups": {"lead": {"h=1": {"days": days[0]}, "h=2": {"days": days[1]}},
                       "pooled": {"all decision days": {"days": 30, "grid_crps": {"vs": {"x": {"y": dict(rows[0])}}},
                                                        "upper_tail_twcrps": {"vs": {"x": {"y": dict(rows[1])}}}}}}}


def stages(*docs):
    return [(f"s{i}", f"c{i}", f"change {i}", d) for i, d in enumerate(docs)]


class ReadingTests(unittest.TestCase):

    def test_a_reading_is_taken_from_the_mean_d_bound(self):
        self.assertEqual(script.reading(GAIN), "gain")
        self.assertEqual(script.reading(LOSS), "loss")
        self.assertEqual(script.reading(UNDECIDED), "undecided")
        self.assertEqual(script.reading(NONE), "no reading")

    def test_a_move_is_classed(self):
        self.assertEqual(script.move("loss", "undecided"), "improved")
        self.assertEqual(script.move("undecided", "gain"), "improved")
        self.assertEqual(script.move("gain", "loss"), "worsened")
        self.assertEqual(script.move("gain", "no reading"), "lost its reading")
        self.assertEqual(script.move("no reading", "undecided"), "gained a reading")
        self.assertEqual(script.move("gain", "gain"), "same")


class CompareTests(unittest.TestCase):

    def test_a_change_is_attributed_to_the_first_stage_that_differs(self):
        a = doc([GAIN, LOSS])
        b = doc([UNDECIDED, LOSS])
        c = doc([UNDECIDED, LOSS])
        d = doc([UNDECIDED, NONE])
        r = script.compare(stages(a, b, c, d))
        moved = {m["path"]: m for m in r["reading_rows"]}
        first = moved["groups/pooled/all decision days/grid_crps/vs/x/y"]
        self.assertEqual(first["readings"], ["gain", "undecided", "undecided", "undecided"])
        self.assertEqual(first["changed_at"], ["s1"])
        second = moved["groups/pooled/all decision days/upper_tail_twcrps/vs/x/y"]
        self.assertEqual(second["changed_at"], ["s3"])
        self.assertEqual([t["reading_changes"] for t in r["transitions"]], [1, 0, 1])
        self.assertEqual(r["overall"]["worsened"], 1)
        self.assertEqual(r["overall"]["lost its reading"], 1)

    def test_a_row_whose_bound_moved_but_whose_reading_did_not_is_counted_not_listed(self):
        a = doc([GAIN, LOSS])
        b = copy.deepcopy(a)
        b["groups"]["pooled"]["all decision days"]["grid_crps"]["vs"]["x"]["y"]["difference_interval"] = [0.02, 0.2]
        r = script.compare(stages(a, b))
        self.assertEqual(r["reading_rows"], [])
        self.assertEqual((r["transitions"][0]["rows"], r["transitions"][0]["rows_differing"]), (2, 1))

    def test_a_day_count_that_moved_is_listed_by_lead(self):
        r = script.compare(stages(doc([GAIN, LOSS], (10, 20)), doc([GAIN, LOSS], (11, 20)), doc([GAIN, LOSS], (11, 19))))
        self.assertEqual(r["lead_days"], {"h=1": [10, 11, 11], "h=2": [20, 20, 19]})
        self.assertEqual(r["day_changes"][0]["moved"], ["groups/lead/h=1/days"])
        self.assertEqual(r["day_changes"][1]["moved"], ["groups/lead/h=2/days"])

    def test_a_row_that_gains_a_bound_by_dropping_resamples_is_counted_at_its_stage(self):
        """#1239 is the change that leaves `dropped_resamples` beside a bound; a stage's rows that carry it and did not before."""

        a = doc([NONE, LOSS])
        b = doc([dict(UNDECIDED, dropped_resamples=1, draws=100), LOSS])
        r = script.compare(stages(a, b))
        self.assertEqual(r["transitions"][0]["rows_with_dropped_resamples"], 1)
        self.assertEqual(r["transitions"][0]["rows_differing"], 1)
        self.assertEqual(script.compare(stages(b, b))["transitions"][0]["rows_with_dropped_resamples"], 0)

    def test_a_difference_outside_the_rows_is_reported_per_stage(self):
        a = doc([GAIN, LOSS])
        b = copy.deepcopy(a)
        b["extra"] = 1
        self.assertEqual(script.compare(stages(a, b))["transitions"][0]["other_differences"], ["extra only in new"])

    def test_stages_scored_on_other_settings_are_refused(self):
        a, b = doc([GAIN, LOSS]), doc([GAIN, LOSS])
        b["draws"] = 200
        with self.assertRaisesRegex(SystemExit, "draws differs"):
            script.compare(stages(a, b))
        c = doc([GAIN, LOSS])
        c["panel_sha256"] = "cd" * 32
        with self.assertRaisesRegex(SystemExit, "panel_sha256 differs"):
            script.compare(stages(a, c))


class PageTests(unittest.TestCase):

    def result(self):
        a = doc([GAIN, LOSS])
        b = doc([UNDECIDED, LOSS], (11, 20))
        out = {"issue": 1243, "base_sha": "6dd127ed", "old_page": "docs/research/s3-terms-1196-result.md"}
        out.update(script.compare(stages(a, b)))
        return out

    def test_the_section_names_what_moved_and_what_it_cannot_attribute(self):
        text = "\n".join(script.section(self.result()))
        self.assertIn("gain", text)
        self.assertIn("h=1", text)
        self.assertIn("not attributed", text)
        self.assertIn("#1198", text)
        self.assertIn("#1060", text)
        self.assertIn("#1239", text)

    def test_the_header_of_the_new_page_replaces_the_old_ones_and_says_it_supersedes(self):
        body = "# The scarcity interaction and the FOMC/IORB terms on (s3)'s robust fit (#1196)\n\nGenerated by " \
               "`scripts/s3_terms_1196.py page` from `docs/research/s3-terms-1196/result.json`, not edited by hand; declared in"
        out = script.retitle(body)
        self.assertIn("(#1243)", out.splitlines()[0])
        self.assertIn("docs/research/s3-terms-1243/result.json", out)
        self.assertIn("s3-terms-1196-result.md", out)
        with self.assertRaises(SystemExit):
            script.retitle("a page that does not have the header")

    def test_the_old_page_note_is_dated_and_names_the_base(self):
        note = script.superseded_note("6dd127ed", 1250, "b56ab27f")
        self.assertIn("Superseded on main by #1250 (finding #1243)", note)
        self.assertIn("kept as the record of what was run on b56ab27f", note)


class CommittedRecordTests(unittest.TestCase):
    """The tracked record of the re-score, and the page generated from it."""

    RECORD = ROOT / "docs" / "research" / "s3-terms-1243" / "result.json"
    PAGE = ROOT / "docs" / "research" / "s3-terms-1243-result.md"

    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"), script.page_text(record))

    def test_the_record_is_the_declared_setup_of_1196_on_the_same_panel(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        old = json.loads(script.OLD_RESULT.read_text(encoding="utf-8"))
        for key in ("seed", "draws", "panel_sha256", "declaration", "models", "arms", "reps", "refit_total"):
            self.assertEqual(record[key], old[key], key)
        self.assertIsNone(record["subset_from"])
        self.assertEqual(record["against_1196"]["stages"][0]["label"], "committed")

    def test_the_stage_before_the_changes_reproduces_the_committed_score(self):
        """The baseline stage is the tree on which the committed file is reproduced; a nonzero count here would make every later
        attribution a guess."""

        first = json.loads(self.RECORD.read_text(encoding="utf-8"))["against_1196"]["transitions"][0]
        self.assertEqual((first["rows_differing"], first["other_differences"]), (0, []))


if __name__ == "__main__":
    unittest.main()
