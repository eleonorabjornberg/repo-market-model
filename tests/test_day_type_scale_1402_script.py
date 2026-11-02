"""`scripts/day_type_scale_1402.py` (#1402; H5 step 3, development tier): (s3c-ann-net-typed) and (s3c-ann-net-pooled), a residual scale per
pressure-day type of the target day, scored against the frozen candidate (s3c-ann-net) and B1'* at the 18:00 decision instant on both windows of #1255.

Written first, against the declaration. The arithmetic and the leakage guard of the multiplier are in `test_day_type_scale_1402`. What these tests pin:
that the declaration names what the script has (seed, models, arms, references, no amendment) and that the cleared register row exists; the test
plan; the pressure-day type of a panel row on dates whose type is known; the choice of the refit a forecast used; the record of the multipliers on a hand
case; that the pooled arm may not differ from the candidate on an ordinary target day; the refusal to walk at another instant; the page (the declared
reading, the marked question with numbered options and a default); a small run of `score` and `page` end to end on the fixture panel; and that the
tracked page is what the script renders from the tracked record.

Recorded mutation (the check of this study, #1402): in `day_type_scale_1402.walks_of`, the guard `if k.DECISION_TIME.isoformat(timespec="minutes") !=
"18:00":` was changed to `if False:`. `WalkTests.test_a_walk_not_at_the_declared_instant_is_refused` then failed with `AttributeError` (with the
guard gone the call went on and met the `None` frame the test passes; `ValueError` was not raised); restored, it passes.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date, time
from pathlib import Path
from types import SimpleNamespace

from repo_model import day_type_scale as dts
from repo_model import scoring_protocol as sp

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("day_type_scale_1402", ROOT / "scripts" / "day_type_scale_1402.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["day_type_scale_1402"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_what_the_script_has(self):
        declaration = script.committed_declaration()
        self.assertEqual(declaration["issue"], 1402)
        self.assertEqual(script.SEED, 1402)
        self.assertEqual(declaration["scoring"]["seed"], script.SEED)
        self.assertIn("seed 1402", declaration["scoring"]["test"])
        self.assertEqual(declaration["models"], list(script.MODELS))
        self.assertEqual([a["name"] for a in declaration["arms"]], [script.ANNNET, *script.ARMS])
        self.assertEqual([r["name"] for r in declaration["references"]], [script.ANNNET, script.B1PS])
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(declaration["amendments"], [])
        self.assertIn("18:00", declaration["decision_instant"])
        self.assertTrue(declaration["reading"]["which_reading"].startswith("BY TYPE"))

    def test_the_register_row_is_cleared_and_names_the_declaration(self):
        row = json.loads((ROOT / "metadata" / "provisional" / "cleared" / "day_type_scale_1402.json").read_text(encoding="utf-8"))
        self.assertEqual(row["declaration"], "metadata/day_type_scale_1402.json")
        self.assertEqual(row["script"], "scripts/day_type_scale_1402.py")
        self.assertEqual(row["pairing"], "direct")

    def test_the_plan_tests_each_arm_against_the_candidate_and_b1_prime_star(self):
        self.assertEqual(script.plan(script.TYPED), [script.ANNNET, script.B1PS])
        self.assertEqual(script.plan(script.POOLED), [script.ANNNET, script.B1PS])
        self.assertEqual(script.plan(script.ANNNET), [script.B1PS])
        self.assertEqual(script.plan(script.B1PS), [])


class PartsTests(unittest.TestCase):

    def test_the_refit_a_forecast_used_is_the_latest_on_or_before_it(self):
        refits = {date(2025, 1, 6): None, date(2025, 2, 5): None, date(2025, 3, 7): None}
        self.assertEqual(script.refit_for(refits, date(2025, 2, 4)), date(2025, 1, 6))
        self.assertEqual(script.refit_for(refits, date(2025, 2, 5)), date(2025, 2, 5))
        self.assertEqual(script.refit_for(refits, date(2025, 6, 1)), date(2025, 3, 7))

    def test_the_multiplier_record_counts_the_fallback_by_the_rows_the_mode_counts(self):
        one = {t: 1.0 for t in dts.TYPES}
        fitted = {date(2025, 1, 6): {h: dict(one, turn=2.0) for h in script.LEADS}, date(2025, 2, 5): {h: dict(one, turn=4.0) for h in script.LEADS}}
        few = {t: 0 for t in dts.TYPES}
        rows = {date(2025, 1, 6): {h: dict(few, turn=12, tax_date=3, ordinary=400) for h in script.LEADS},
                date(2025, 2, 5): {h: dict(few, turn=5, tax_date=3, ordinary=400) for h in script.LEADS}}
        typed = script.multiplier_record(fitted, rows, "typed")["by_lead"]["1"]
        self.assertEqual((typed["turn"]["mean"], typed["turn"]["min"], typed["turn"]["max"]), (3.0, 2.0, 4.0))
        self.assertEqual(typed["turn"]["share_fallback"], 0.5)  # 12 rows, then 5 (below the minimum of 10)
        self.assertEqual(typed["turn"]["share_at_bound"], 0.5)  # 4.0 is the upper bound
        self.assertEqual(typed["tax_date"]["share_fallback"], 1.0)
        self.assertEqual(typed["turn"]["mean_rows"], 8.5)
        pooled = script.multiplier_record(fitted, rows, "pooled")["by_lead"]["1"]
        self.assertEqual(pooled["turn"]["share_fallback"], 0.5)  # 15 non-ordinary rows, then 8 (below the minimum)
        self.assertEqual(pooled["ordinary"]["share_fallback"], 0.0)

    def test_the_non_ordinary_group_is_the_union_of_the_four_types(self):
        pressure = {date(2025, 1, 2): "ordinary", date(2025, 1, 3): "turn", date(2025, 1, 6): "tax_date", date(2025, 1, 7): "year_end"}
        split, label, grain, members = script.non_ordinary_group(pressure)
        self.assertEqual((split, grain), ("pressure_day_type", "target"))
        self.assertEqual(members, [date(2025, 1, 3), date(2025, 1, 6), date(2025, 1, 7)])
        self.assertTrue(label.startswith("non-ordinary"))


class DifferingCellsTests(unittest.TestCase):

    def frame(self, pooled_differs_on_ordinary: bool):
        day = date(2025, 1, 2)
        q = list(range(23))
        other = [x + 1.0 for x in q]
        forecasts = {
            script.ANNNET: {day: {h: q for h in script.LEADS}},
            script.TYPED: {day: {h: other for h in script.LEADS}},
            script.POOLED: {day: {h: (other if pooled_differs_on_ordinary else q) for h in script.LEADS}},
        }
        return SimpleNamespace(days=[day], position={day: 0}, forecasts=forecasts)

    def test_the_pooled_arm_may_not_differ_from_the_candidate_on_an_ordinary_target_day(self):
        labels = {h: "ordinary" for h in script.LEADS}
        with self.assertRaises(ValueError):
            script.differing_cells(self.frame(True), labels)

    def test_the_cells_are_counted_by_the_type_of_the_target(self):
        labels = {1: "ordinary", 2: "turn", 3: "turn", 4: "ordinary", 5: "tax_date"}
        got = script.differing_cells(self.frame(False), labels)
        self.assertEqual(got[script.TYPED]["turn"], {"differing": 2, "cells": 2})
        self.assertEqual(got[script.TYPED]["ordinary"], {"differing": 2, "cells": 2})
        self.assertEqual(got[script.POOLED]["ordinary"], {"differing": 0, "cells": 2})


class WalkTests(unittest.TestCase):

    def test_a_walk_not_at_the_declared_instant_is_refused(self):
        held = script.k.DECISION_TIME
        script.k.DECISION_TIME = time(16, 0)
        try:
            with self.assertRaises(ValueError):
                script.walks_of("development", None, None, None, None, None, None, None)
        finally:
            script.k.DECISION_TIME = held


class PageTests(unittest.TestCase):

    def test_the_question_is_marked_numbered_and_carries_a_default(self):
        text = "\n".join(script.question())
        self.assertIn("Question for Eleonora", text)
        self.assertIn("**Question 1.", text)
        self.assertEqual(text.count("(default)"), 1)
        self.assertIn("1. ", text)
        self.assertIn("3. ", text)
        self.assertNotIn("GO #", text)


class EndToEndTests(unittest.TestCase):
    """`score` and `page` with the walk started late on the fixture panel, with few resamples: the shape, not the figures."""

    FIRST = "2025-09-02"

    @classmethod
    def setUpClass(cls):
        import panel_cache

        cls.panel_path = Path(panel_cache.published_build()["path"])
        cls.tmp = tempfile.TemporaryDirectory()
        base = Path(cls.tmp.name)
        cls.output, cls.page = base / "result.json", base / "page.md"
        script.main(["score", "--panel", str(cls.panel_path), "--output", str(cls.output), "--draws", "20", "--reps", "5", "--permutations", "20",
                     "--workers", "2", "--first", cls.FIRST])
        script.main(["page", "--score", str(cls.output), "--output", str(cls.page)])
        cls.result = json.loads(cls.output.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_both_windows_are_scored_inside_the_limit(self):
        self.assertEqual(sorted(self.result["windows"]), sorted(script.WINDOWS))
        for window, w in self.result["windows"].items():
            self.assertLessEqual(w["notes"]["last_target"], script.WINDOW_LAST[window].isoformat())
            self.assertLessEqual(w["notes"]["last_target"], script.LAST_DAY.isoformat())
        self.assertEqual(self.result["decision_time"], "18:00")

    def test_each_model_is_scored_against_what_the_plan_says(self):
        for w in self.result["windows"].values():
            cell = w["groups"]["pooled"]["all decision days"]["grid_crps"]
            for candidate in script.ARMS + (script.ANNNET,):
                self.assertEqual(sorted(cell["vs"][candidate]), sorted(script.plan(candidate)))
            self.assertEqual(sorted(cell["means"]), sorted(script.MODELS))

    def test_the_pressure_day_types_and_their_union_are_groups(self):
        for w in self.result["windows"].values():
            groups = w["groups"]["pressure_day_type"]
            self.assertIn(script.NON_ORDINARY, groups)
            parts = sum(groups[t]["days"] for t in dts.NON_ORDINARY if t in groups)
            self.assertEqual(groups[script.NON_ORDINARY]["days"], parts)

    def test_the_pooled_arm_leaves_every_ordinary_target_cell_as_the_candidate(self):
        for w in self.result["windows"].values():
            self.assertEqual(w["differing_cells"][script.POOLED][dts.ORDINARY]["differing"], 0)

    def test_the_multipliers_are_reported_by_lead_and_type_inside_the_bounds(self):
        for w in self.result["windows"].values():
            for arm in script.ARMS:
                self.assertEqual(sorted(w["multipliers"][arm]["by_lead"]), ["1", "2", "3", "4", "5"])
                for block in w["multipliers"][arm]["by_lead"].values():
                    for t in dts.TYPES:
                        self.assertGreaterEqual(block[t]["min"], dts.BOUNDS[0] if block[t]["share_fallback"] < 1.0 else 1.0)
                        self.assertLessEqual(block[t]["max"], dts.BOUNDS[1])
            ordinary = w["multipliers"][script.POOLED]["by_lead"]["1"][dts.ORDINARY]
            self.assertEqual((ordinary["min"], ordinary["max"]), (1.0, 1.0))

    def test_the_coverage_and_the_clustering_are_reported_for_the_candidate_and_both_arms(self):
        for w in self.result["windows"].values():
            cov = w["coverage"]
            self.assertEqual(sorted(cov["models"]), sorted(script.COVERAGE_MODELS))
            labels = {(g["split"], g["label"]) for g in cov["models"][script.ANNNET]["groups"]}
            self.assertIn(("pooled", "all cells"), labels)
            self.assertTrue(any(s == "pressure_day_type" for s, _ in labels))
            self.assertTrue(any(s == "target_day_type" for s, _ in labels))
            self.assertEqual(sorted(cov["models"][script.TYPED]["clustering"]["all"]), ["1", "2", "3", "4", "5"])

    def test_the_page_carries_the_declared_reading_the_type_summary_and_ends_with_the_marked_question(self):
        text = self.page.read_text(encoding="utf-8")
        self.assertIn("**Which reading, declared in advance.** BY TYPE", text)
        self.assertIn("## Summary: by pressure-day type of the target day", text)
        self.assertIn("### The multipliers", text)
        self.assertIn("### Clustering of the band misses", text)
        self.assertIn("## Question for Eleonora", text)
        self.assertIn("**Options**", text)
        self.assertNotIn("GO #", text)


class CommittedRecordTests(unittest.TestCase):
    """The tracked record of the declared run, and the page generated from it."""

    RECORD = ROOT / "docs" / "research" / "day-type-scale-1402" / "result.json"
    PAGE = ROOT / "docs" / "research" / "day-type-scale-1402-result.md"

    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"), script.render(record))

    def test_the_record_is_the_declared_full_run_on_the_published_panel(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8"))
        self.assertIsNone(record["subset_from"])
        self.assertEqual((record["seed"], record["draws"], record["reps"], record["permutations"]),
                         (script.SEED, sp.DRAWS, script.REPS, script.m1363.PERMUTATIONS))
        self.assertEqual(record["declaration"], "metadata/day_type_scale_1402.json")
        self.assertEqual(record["models"], list(script.MODELS))
        self.assertEqual(record["decision_time"], "18:00")
        self.assertIn(record["panel_sha256"], json.dumps(manifest))
        for window, w in record["windows"].items():
            self.assertLessEqual(w["notes"]["last_target"], script.WINDOW_LAST[window].isoformat())
            self.assertEqual(w["differing_cells"][script.POOLED][dts.ORDINARY]["differing"], 0)

    def test_the_candidate_reproduces_the_record_of_1314(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        there = json.loads(script.RECORD_1314.read_text(encoding="utf-8"))["windows"]
        for window, found in record["reproduction"].items():
            theirs = there[window]["groups"]["pooled"]["all decision days"]["grid_crps"]["means"]["sc_s3c_ann_net"]
            theirs = theirs["mean"] if isinstance(theirs, dict) else theirs
            self.assertLess(abs(found["here"] - theirs), 1e-9, window)


if __name__ == "__main__":
    unittest.main()
