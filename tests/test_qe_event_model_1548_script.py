"""`scripts/qe_event_model_1548.py` end to end (#1548; H5 step 3, development tier): the event-conditional quarter-end arm beside the frozen candidate.

The arithmetic, the leakage guard and the "identical outside the event set" check are in `test_qe_event_model_1548`. What these tests pin: a small run of
`score` and `page` on the fixture panel with the walk started late and few resamples (the shape, not the figures): both windows inside the limit, every
cell outside the event set counted and identical to the candidate, the group reported by horizon and type with event counts, the references each model is
tested against, the pool record (weights between 0 and 1, event counts), the context from #1531's record; the page (the kill sentence, the number of
events and the word "small", the marked numbered questions with defaults); and that the tracked page is what the script renders from the tracked record,
which is the declared full run on the published panel and reproduces #1314.

Recorded mutation (the plan of this study, #1548): in `qe_event_model_1548.plan`, `[ANNNET] if candidate == ARM else []` was changed to
`[] if candidate == ARM else []`. `PartsTests.test_the_arm_is_tested_against_the_references_and_the_candidate` then failed with `AssertionError`
(the arm's list lacked the candidate); restored, it passes.
"""


from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

from repo_model import event_conditional as ec
from repo_model import scoring_protocol as sp

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("qe_event_model_1548", ROOT / "scripts" / "qe_event_model_1548.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["qe_event_model_1548"] = script  # the worker pool pickles the script's functions by module name
_spec.loader.exec_module(script)


class PartsTests(unittest.TestCase):

    def test_the_arm_is_tested_against_the_references_and_the_candidate(self):
        self.assertEqual(script.plan(script.ARM), ["B1", "B1_prime", "B2", script.ANNNET])
        self.assertEqual(script.plan(script.ANNNET), ["B1", "B1_prime", "B2"])

    def test_the_pool_record_summarises_the_refits(self):
        base = [float(j) for j in range(23)]
        own = [p + 2.0 for p in base]
        fitted = {date(2020, 1, 6): {h: {"n": 20, "w": 0.5, "base": base, "pool": base, "event_pool": own} for h in script.LEADS},
                  date(2020, 2, 3): {h: {"n": 4, "w": 0.0, "base": base, "pool": base, "event_pool": None} for h in script.LEADS}}
        record = ec.pool_record(fitted, script.LEADS, k=20)
        e = record["by_lead"]["1"]
        self.assertEqual(e["n"], {"mean": 12.0, "min": 4, "max": 20})
        self.assertEqual(e["w"], {"mean": 0.25, "min": 0.0, "max": 0.5})
        self.assertEqual(e["share_fallback"], 0.5)
        self.assertEqual(e["median_shift"], 2.0)
        self.assertAlmostEqual(e["span_ratio"], 1.0)

    def test_the_kill_needs_coverage_beyond_its_interval_and_no_crps_loss(self):
        def group(cov_low, crps):
            return {"pooled": {"measures": {"cover90": {"diff": 0.1, "diff_interval": [cov_low, 0.2]}, "grid_crps": {"diff": crps, "diff_interval": [crps - 1, crps + 1]}}}}
        self.assertFalse(script.kill_reading(group(0.05, -0.1))["killed"])
        self.assertTrue(script.kill_reading(group(0.0, -0.1))["killed"])
        self.assertTrue(script.kill_reading(group(0.05, 0.1))["killed"])

    def test_the_question_is_marked_numbered_and_carries_defaults(self):
        text = "\n".join(script.question())
        self.assertIn("Questions for Eleonora", text)
        self.assertIn("**Question 1.", text)
        self.assertIn("**Question 2.", text)
        self.assertIn("1. **k = 20** (default)", text)
        self.assertIn("2. **k = 10.**", text)
        self.assertIn("3. **k = 40.**", text)
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
        script.main(["score", "--panel", str(cls.panel_path), "--output", str(cls.output), "--draws", "20", "--reps", "5", "--event-reps", "20",
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
        self.assertEqual(self.result["k"], script.K)

    def test_every_cell_outside_the_group_is_counted_and_identical(self):
        for w in self.result["windows"].values():
            o = w["outside_the_group"]
            self.assertGreater(o["other_cells"], 0)
            self.assertEqual(o["group_cells"] + o["other_cells"], len(script.LEADS) * w["notes"]["scored_decision_days"])
            cell = w["groups"]["pooled"]["all decision days"]["grid_crps"]
            self.assertEqual(sorted(cell["means"]), sorted(script.MODELS))
            for candidate in (script.ARM, script.ANNNET):
                self.assertEqual(sorted(cell["vs"][candidate]), sorted(script.plan(candidate)))

    def test_the_group_is_reported_by_lead_type_and_the_1363_subset_with_events(self):
        for w in self.result["windows"].values():
            g = w["group"]
            self.assertEqual(sorted(g["by_lead"]), ["1", "2", "3", "4", "5"])
            self.assertEqual(sorted(g["by_type"]), sorted(ec.EVENT_TYPES))
            if g["pooled"] is not None:
                self.assertEqual(g["pooled"]["events"], len(g["events"]))
                self.assertEqual(sorted(g["pooled"]["measures"]), sorted(script.MEASURES))
                for m in g["pooled"]["measures"].values():
                    self.assertLessEqual(m["diff_interval"][0], m["diff"] + 1e-9)
                    self.assertGreaterEqual(m["diff_interval"][1], m["diff"] - 1e-9)

    def test_the_pools_are_shrunk_between_the_candidate_and_the_events(self):
        for w in self.result["windows"].values():
            self.assertEqual(sorted(w["pools"]["by_lead"]), ["1", "2", "3", "4", "5"])
            for e in w["pools"]["by_lead"].values():
                self.assertTrue(0.0 <= e["w"]["min"] <= e["w"]["max"] < 1.0)
                self.assertGreaterEqual(e["n"]["min"], 0)
                self.assertTrue(0.0 <= e["share_fallback"] <= 1.0)

    def test_a_subset_run_carries_no_context_since_its_cells_are_not_1531s(self):
        self.assertEqual(self.result["context_1531"], {})

    def test_the_page_carries_the_kill_the_event_count_and_ends_with_the_marked_question(self):
        text = self.page.read_text(encoding="utf-8")
        self.assertIn("**Against the declared kill:", text)
        self.assertIn("That is few, so every interval is wide.", text)
        self.assertIn("#1228 has not ruled", text)
        self.assertIn("### Coverage and tail misses on the group, candidate against arm", text)
        self.assertIn("### Against B3", text)
        self.assertIn("## Questions for Eleonora", text)
        self.assertIn("**Options**", text)
        self.assertNotIn("GO #", text)
        self.assertEqual(text.count("Closes #"), 0)


class CommittedRecordTests(unittest.TestCase):
    """The tracked record of the declared run, and the page generated from it."""

    RECORD = ROOT / "docs" / "research" / "qe-event-model-1548" / "result.json"
    PAGE = ROOT / "docs" / "research" / "qe-event-model-1548-result.md"

    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"), script.render(record))

    def test_the_record_is_the_declared_full_run_on_the_published_panel(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8"))
        self.assertIsNone(record["subset_from"])
        self.assertEqual((record["seed"], record["draws"], record["event_reps"], record["k"]), (script.SEED, sp.DRAWS, script.EVENT_REPS, script.K))
        self.assertEqual(record["declaration"], "metadata/qe_event_model_1548.json")
        self.assertEqual(record["models"], list(script.MODELS))
        self.assertIn(record["panel_sha256"], json.dumps(manifest))
        for window, w in record["windows"].items():
            self.assertLessEqual(w["notes"]["last_target"], script.WINDOW_LAST[window].isoformat())
            self.assertEqual(w["outside_the_group"]["group_cells"] + w["outside_the_group"]["other_cells"], 5 * w["notes"]["scored_decision_days"])

    def test_the_context_of_1531_is_carried_and_its_candidate_column_is_checked(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(sorted(record["context_1531"]), sorted(script.WINDOWS))
        text = self.PAGE.read_text(encoding="utf-8")
        self.assertIn("### Beside the width-only arm", text)
        there = {"development": {"events": 1, "cells": 1, "measures": {m: {"candidate": 0.5, "arm_1531": 0.4} for m in script.MEASURES}}}
        here = {"measures": {m: {"candidate": 0.6, "arm": 0.3} for m in script.MEASURES}}
        with self.assertRaises(ValueError):
            script.context_table("development", here, there["development"])

    def test_the_candidate_reproduces_the_record_of_1314(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        there = json.loads(script.RECORD_1314.read_text(encoding="utf-8"))["windows"]
        for window, found in record["reproduction"].items():
            theirs = there[window]["groups"]["pooled"]["all decision days"]["grid_crps"]["means"]["sc_s3c_ann_net"]
            theirs = theirs["mean"] if isinstance(theirs, dict) else theirs
            self.assertLess(abs(found["here"] - theirs), 1e-9, window)


if __name__ == "__main__":
    unittest.main()
