"""`scripts/s3c_gse_roll_1287.py` (#1287; H5 step 3, development tier): (s3c-gse-roll), the GSE ramp with the payment-day roll, scored beside
(s3c-gse) (re-run unchanged as the control), (s3c), (s3), B1, B1' and B2 on the development window and on the 2026 development days.

Written first, against the declaration. The term table is `repo_model.s3c_gse_roll` and is tested in `test_s3c_gse_roll`; the frames, the benchmarks, the
walk, the cap and the cell arithmetic are #1274's (`test_s3c_gse_1274_script`), loaded as they are. What these tests pin: that the declaration names what the
module has (seed, models, arms, candidate, no amendment); the register row; what the arm is tested against (the control first); the rolled-payment-day split
(a partition of the target days, the moved days being the payment days of the rolled months) on hand cases; the table of the moved days; the count of months the
roll moves (37 of 98, the count of #1285); the page's marked questions; a small run of `score` and `page` end to end on the fixture panel; and, once the full run is
committed, that the tracked page is what the script renders from the tracked record and that the control reproduces #1274's record.

Recorded mutation (the split of the days the roll moves, #1287): in `s3c_gse_roll_1287.is_moved`, `!=` was changed to `==`, so the split names every
unrolled day as moved and the rolled ones as other. `GroupTests.test_the_moved_days_are_the_payment_days_of_the_rolled_months` failed with `AssertionError`
(`False is not true` on 2025-12-26, a rolled payment day); restored, it passes.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

from repo_model import s3c_candidate, s3c_gse, s3c_gse_roll
from repo_model import scoring_protocol as sp

from test_s3c_gse_1274_script import Frame

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("s3c_gse_roll_1287", ROOT / "scripts" / "s3c_gse_roll_1287.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["s3c_gse_roll_1287"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_what_the_module_has(self):
        declaration = script.committed_declaration()
        self.assertEqual(declaration["issue"], 1287)
        self.assertEqual(declaration["finding"], "#1285")
        self.assertEqual(script.SEED, 1287)
        self.assertIn("seed 1287", declaration["scoring"]["test"])
        self.assertEqual(declaration["scoring"]["seed"], script.SEED)
        self.assertEqual(declaration["candidate"]["margin_bp"], s3c_candidate.MARGIN_BP)
        self.assertEqual(declaration["candidate"]["name"], script.S3CGR)
        self.assertEqual(declaration["control"]["name"], script.S3CG)
        self.assertEqual(declaration["models"], list(script.MODELS))
        self.assertEqual([w["name"] for w in declaration["frame"]["windows"]], list(script.WINDOWS))
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(declaration["amendments"], [])
        self.assertEqual([a["name"] for a in declaration["arms"]], [script.S3, script.S3C, script.S3CG, script.S3CGR])
        self.assertIn("first business day after the 25th", declaration["candidate"]["definition"])

    def test_the_cleared_register_row_exists_for_the_declaration(self):
        row = json.loads((ROOT / "metadata" / "provisional" / "cleared" / "s3c_gse_roll_1287.json").read_text(encoding="utf-8"))
        self.assertEqual((row["declaration"], row["script"], row["pairing"]), ("metadata/s3c_gse_roll_1287.json", "scripts/s3c_gse_roll_1287.py", "direct"))

    def test_only_the_arm_is_tested_and_against_the_declared_references_the_control_first(self):
        self.assertEqual(script.plan(script.S3CGR), [script.S3CG, script.S3C, script.S3, "B1", script.B1P, "B2"])
        self.assertEqual(script.plan(script.S3CG), [])

    def test_the_declaration_reads_no_outside_source(self):
        self.assertIn("no source", json.dumps(script.committed_declaration()).lower())

    def test_the_control_is_the_module_of_1274_unchanged(self):
        self.assertEqual((script.m74.S3CG, script.m74.TERM), (script.S3CG, s3c_gse.REPLACED_TERM))
        self.assertEqual(script.S3_ARM.name, "sc_s3_robust")


class MonthTests(unittest.TestCase):

    def test_the_roll_moves_the_months_of_1285(self):
        m = script.months_moved()
        self.assertEqual((m["months"], m["moved"], m["moved_development"], m["moved_2026"]), (98, 37, 33, 4))
        self.assertEqual(len(m["payment_days"]), 37)
        self.assertIn("2025-12-26", m["payment_days"])
        self.assertTrue(all(date.fromisoformat(d).day in (26, 27, 28, 29) for d in m["payment_days"]))


class GroupTests(unittest.TestCase):

    def test_the_moved_days_are_the_payment_days_of_the_rolled_months(self):
        self.assertTrue(script.is_moved(date(2025, 12, 26)))   # Christmas on a Thursday: the payment day is Friday the 26th
        self.assertTrue(script.is_moved(date(2025, 10, 27)))   # a Saturday 25th
        self.assertFalse(script.is_moved(date(2025, 10, 24)))  # the Friday before keeps its own value in both arms
        self.assertFalse(script.is_moved(date(2025, 3, 25)))   # a Tuesday 25th: both arms read 1
        self.assertFalse(script.is_moved(date(2025, 3, 26)))

    def test_the_roll_term_is_non_zero_through_the_payment_day(self):
        self.assertTrue(script.in_roll(date(2025, 10, 27)))
        self.assertFalse(script.in_roll(date(2025, 10, 28)))
        self.assertFalse(script.in_roll(date(2025, 10, 18)))

    def test_the_groups_split_the_target_days_both_ways(self):
        frame = Frame()
        everything = {frame.target(d, h) for d in frame.days for h in sp.HORIZONS}
        for window, split in (("development", "regime"), ("2026", "month")):
            groups = script.groups_of(frame, window)
            by = {(s, label): members for s, label, _g, members in groups}
            for name, a, b in ((script.MOVED_SPLIT, script.MOVED_DAYS, script.OTHER_DAYS), (script.RAMP_SPLIT, script.RAMP_DAYS, script.NON_RAMP_DAYS)):
                x, y = by[(name, a)], by[(name, b)]
                self.assertEqual(set(x) & set(y), set())
                self.assertEqual(set(x) | set(y), everything)
            moved = by[(script.MOVED_SPLIT, script.MOVED_DAYS)]
            self.assertIn(date(2025, 12, 26), moved)
            self.assertTrue(all(script.is_moved(t) for t in moved))
            self.assertIn(split, {s for s, _l, _g, _m in groups})
            self.assertEqual([s for s, _l, _g, _m in groups if s == "lead"], ["lead"] * 5)
            self.assertEqual(len([g for g in groups if g[0] == script.RAMP_SPLIT]), 2)

    def test_the_moved_rows_list_each_moved_day_with_both_terms(self):
        frame = Frame()
        targets = sorted({frame.target(d, h) for d in frame.days for h in sp.HORIZONS})
        series = {m: {t: float(i) for i, t in enumerate(targets)} for m in (script.S3, script.S3C, script.S3CG, script.S3CGR)}
        rows = script.moved_rows(frame, series)
        self.assertIn("2025-12-26", [x["date"] for x in rows])
        row = next(x for x in rows if x["date"] == "2025-12-26")
        self.assertEqual((row["control_term"], row["arm_term"]), (s3c_gse.ramp(date(2025, 12, 26)), s3c_gse_roll.roll_ramp(date(2025, 12, 26))))
        self.assertEqual((row["control_term"], row["arm_term"]), (0.0, 1.0))
        self.assertEqual(row["grid_crps"][script.S3CGR], float(targets.index(date(2025, 12, 26))))


class PageTests(unittest.TestCase):

    def test_the_questions_are_marked_numbered_and_carry_a_default(self):
        text = "\n".join(script.question())
        self.assertIn("Questions for Eleonora", text)
        self.assertIn("**Question 1.", text)
        self.assertEqual(text.count("(default)"), 1)
        for n in ("1. ", "2. ", "3. "):
            self.assertIn(n, text)
        self.assertNotIn("GO #", text)


class EndToEndTests(unittest.TestCase):
    """`score` and `page` with the walk started late on the fixture panel, with few resamples: the shape, not the figures."""

    FIRST = "2025-06-02"

    @classmethod
    def setUpClass(cls):
        import panel_cache

        cls.panel_path = Path(panel_cache.published_build()["path"])
        cls.tmp = tempfile.TemporaryDirectory()
        base = Path(cls.tmp.name)
        cls.output, cls.page = base / "result.json", base / "page.md"
        script.main(["score", "--panel", str(cls.panel_path), "--output", str(cls.output), "--draws", "20", "--reps", "5",
                     "--workers", "2", "--first", cls.FIRST])
        script.main(["page", "--score", str(cls.output), "--output", str(cls.page)])
        cls.result = json.loads(cls.output.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_both_windows_are_scored_inside_their_limits(self):
        dev, y26 = self.result["windows"]["development"]["notes"], self.result["windows"]["2026"]["notes"]
        self.assertLessEqual(dev["last_target"], "2025-12-31")
        self.assertGreaterEqual(y26["first_target"], "2026-01-02")
        self.assertLessEqual(y26["last_target"], script.LAST_DAY.isoformat())

    def test_the_arm_is_scored_against_the_six_references_on_three_metrics(self):
        for window in script.WINDOWS:
            for metric in script.METRIC_NAMES:
                cell = self.result["windows"][window]["groups"]["pooled"]["all decision days"][metric]
                self.assertEqual(sorted(cell["means"]), sorted(script.MODELS))
                self.assertEqual(sorted(cell["vs"][script.S3CGR]), sorted(script.REFERENCES))

    def test_the_walk_reproduces_the_frames_s3_and_the_splits_are_there(self):
        for window in script.WINDOWS:
            w = self.result["windows"][window]
            self.assertEqual(w["walk_equals_frame_days"], w["notes"]["scored_decision_days"])
            self.assertTrue(w["before_full_allotment_is_the_roll_walk"])
            for split in (script.MOVED_SPLIT, script.RAMP_SPLIT, "lead", "pressure_day_type"):
                self.assertIn(split, w["groups"])
            self.assertEqual(set(w["coverage"]), {"pooled"} | {f"h={h}" for h in sp.HORIZONS})
            self.assertEqual(set(w["coverage"]["pooled"]), set(script.COVERAGE_MODELS))
            self.assertEqual(set(w["effect"]), {"roll", "gse_ramp", "flat_19_23"})
            self.assertEqual(w["target_days"]["moved_by_the_roll"], len(w["moved_rows"]))
        self.assertIn("regime", self.result["windows"]["development"]["groups"])
        self.assertIn("month", self.result["windows"]["2026"]["groups"])
        self.assertEqual(self.result["months"]["moved"], 37)

    def test_the_roll_arm_differs_from_the_control_only_through_the_moved_columns(self):
        for window in script.WINDOWS:
            w = self.result["windows"][window]
            self.assertLessEqual(w["cells_where_roll_differs_from_gse"], w["cells"])
            self.assertGreaterEqual(w["moved_cells"], 0)

    def test_the_page_opens_with_the_question_and_ends_with_the_marked_questions(self):
        text = self.page.read_text(encoding="utf-8")
        self.assertTrue(text.split("\n", 2)[2].lstrip().startswith("**Does reading the ramp's peak on the payment day"))
        self.assertIn("## Questions for Eleonora", text)
        self.assertIn("**Options**", text)
        self.assertIn("compares with no outside figure", text)
        self.assertNotIn("GO #", text)


class CommittedRecordTests(unittest.TestCase):
    """The tracked record of the declared run, and the page generated from it."""

    RECORD = ROOT / "docs" / "research" / "s3c-gse-roll-1287" / "result.json"
    PAGE = ROOT / "docs" / "research" / "s3c-gse-roll-1287-result.md"

    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"), script.render(record))

    def test_the_record_is_the_declared_full_run_on_the_published_panel(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8"))
        self.assertIsNone(record["subset_from"])
        self.assertEqual((record["seed"], record["draws"]), (script.SEED, sp.DRAWS))
        self.assertEqual(record["declaration"], "metadata/s3c_gse_roll_1287.json")
        self.assertEqual(record["models"], list(script.MODELS))
        self.assertEqual(record["margin_bp"], 0.0)
        self.assertIn(record["panel_sha256"], json.dumps(manifest))
        self.assertLessEqual(record["windows"]["2026"]["notes"]["last_target"], script.LAST_DAY.isoformat())

    def test_the_control_and_the_predecessors_are_reproduced_from_1274(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertTrue(record["against_1274"])
        for window, there in record["against_1274"].items():
            for metric, rows in there["metrics"].items():
                self.assertEqual(set(rows), {script.S3, script.S3C, script.S3CG, "B1", script.B1P, "B2"})
                for model, v in rows.items():
                    self.assertAlmostEqual(v["difference"], 0.0, places=9, msg=f"{window} {metric} {model}")


if __name__ == "__main__":
    unittest.main()
