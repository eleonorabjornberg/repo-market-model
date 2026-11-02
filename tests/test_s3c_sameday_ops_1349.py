"""`scripts/s3c_sameday_ops_1349.py` (#1349; H5 step 3, development tier): (s3c-ann-net-sameday), the candidate (s3c-ann-net) with the decision day's own
ON RRP and SRF take-up, scored against (s3c-ann-net) and (s3c) at the 18:00 decision instant on both windows of #1255.

Written first, against the declaration. The new read path (`repo_model.same_day_operations`) and its leakage test are in
`test_same_day_operations_1349`. What these tests pin: that the declaration names what the module has (seed, models, arm, references, the last day, no
amendment, the availability evidence file) and that the cleared register row exists; the test plan; the availability arithmetic on a hand case and
that the tracked evidence is what the script computes from the tracked snapshots; the refusal to walk at another instant; the page (the availability
section, the marked questions with numbered options and a default); a small run of `score` and `page` end to end on the fixture panel; and that the
tracked page is what the script renders from the tracked record.

Recorded mutation (the check of this study, #1349): in `s3c_sameday_ops_1349.walks_of`, the guard
`if k.DECISION_TIME != DECISION_TIME:` was changed to `if False:`. `WalkTests.test_a_walk_not_at_the_declared_instant_is_refused` then failed with
`AttributeError` (with the guard gone the call went on and met the `None` frame the test passes; `ValueError` was not raised); restored, it passes.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date, datetime, time
from pathlib import Path

from repo_model import same_day_operations as sdo
from repo_model import scoring_protocol as sp
from repo_model import spread_mr_state_calendar as sc

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("s3c_sameday_ops_1349", ROOT / "scripts" / "s3c_sameday_ops_1349.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["s3c_sameday_ops_1349"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_what_the_module_has(self):
        declaration = script.committed_declaration()
        self.assertEqual(declaration["issue"], 1349)
        self.assertEqual(script.SEED, 1349)
        self.assertIn("seed 1349", declaration["scoring"]["test"])
        self.assertEqual([c["name"] for c in declaration["candidates"]], list(script.ARMS))
        self.assertEqual([c["name"] for c in declaration["references"]], [script.S3C, script.ANNNET])
        self.assertEqual(declaration["models"], list(script.MODELS))
        self.assertEqual([a["name"] for a in declaration["arms"]], [script.S3C, script.ANNNET, *script.ARMS])
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(declaration["amendments"], [])
        self.assertEqual(declaration["arms"][-1]["margin_bp"], script.s3c_candidate.MARGIN_BP)
        self.assertIn("18:00", declaration["decision_instant"])
        self.assertTrue((ROOT / declaration["availability"]["evidence"].split(",")[0]).exists())
        self.assertEqual(sdo.SAMEDAY_ARM.name, script.SAMEDAY.replace("s3c", "s3"))  # the capped model carries the c
        self.assertEqual(script.ARMS, (script.SAMEDAY,))

    def test_the_register_row_is_cleared_and_names_the_declaration(self):
        row = json.loads((ROOT / "metadata" / "provisional" / "cleared" / "s3c_sameday_ops_1349.json").read_text(encoding="utf-8"))
        self.assertEqual(row["declaration"], "metadata/s3c_sameday_ops_1349.json")
        self.assertEqual(row["script"], "scripts/s3c_sameday_ops_1349.py")
        self.assertEqual(row["pairing"], "direct")

    def test_the_plan_tests_the_arm_against_the_candidate_and_s3c_only(self):
        self.assertEqual(script.plan(script.SAMEDAY), [script.ANNNET, script.S3C])
        self.assertEqual(script.plan(script.ANNNET), [])


class AvailabilityTests(unittest.TestCase):

    def figures(self):
        d1, d2, d3 = date(2026, 3, 2), date(2026, 3, 3), date(2026, 3, 4)
        return {d1: sdo.DayFigure(1.0, datetime(2026, 3, 2, 13, 16)), d2: sdo.DayFigure(2.0, datetime(2026, 3, 3, 17, 30)),
                d3: sdo.DayFigure(3.0, datetime(2026, 3, 9, 10, 0))}

    def test_a_date_is_public_when_its_last_write_is_at_or_before_18_00_on_its_own_day(self):
        got = script.source_availability(self.figures(), [], lambda r: False, date(2026, 9, 3))
        self.assertEqual((got["operation_dates"], got["public_by_decision"]), (3, 2))
        self.assertEqual(got["withheld"], [{"date": "2026-03-04", "last_write": "2026-03-09 10:00:00"}])
        self.assertEqual(got["public_by_16"], 1)
        self.assertEqual(got["closest_public_write"]["date"], "2026-03-03")
        self.assertAlmostEqual(got["margin_minutes_of_closest_public_write"], 30.0)

    def test_a_date_after_the_last_day_is_not_counted(self):
        got = script.source_availability(self.figures(), [], lambda r: False, date(2026, 3, 3))
        self.assertEqual(got["operation_dates"], 2)

    def test_the_close_to_write_lag_reads_the_stated_close_time(self):
        ops = [{"operationDate": "2026-03-02", "closeTime": "13:15", "lastUpdated": "2026-03-02 13:16:30", "operationType": "Reverse Repo"}]
        got = script.source_availability(self.figures(), ops, lambda r: True, date(2026, 9, 3))
        self.assertEqual(got["close_to_write_minutes"]["operations"], 1)
        self.assertAlmostEqual(got["close_to_write_minutes"]["median"], 1.5)

    def test_the_tracked_evidence_is_what_the_script_computes_from_the_tracked_snapshots(self):
        tracked = json.loads(script.AVAILABILITY.read_text(encoding="utf-8"))
        self.assertEqual(script.availability_record(), tracked)

    def test_both_sources_are_used_on_the_tracked_evidence(self):
        tracked = json.loads(script.AVAILABILITY.read_text(encoding="utf-8"))
        self.assertEqual(tracked["used"], ["on_rrp", "srf"])
        for name in ("on_rrp", "srf"):
            self.assertGreaterEqual(tracked[name]["share_public"], 0.99)
        self.assertEqual(tracked["decision_time"], "18:00")
        self.assertEqual(tracked["last_day"], script.LAST_DAY.isoformat())


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

    def test_the_questions_are_marked_numbered_and_carry_a_default(self):
        text = "\n".join(script.question())
        self.assertIn("Questions for Eleonora", text)
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
        script.main(["score", "--panel", str(cls.panel_path), "--output", str(cls.output), "--draws", "20", "--reps", "5",
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

    def test_the_arm_is_scored_against_what_the_plan_says(self):
        for w in self.result["windows"].values():
            cell = w["groups"]["pooled"]["all decision days"]["grid_crps"]
            self.assertEqual(sorted(cell["vs"][script.SAMEDAY]), sorted(script.plan(script.SAMEDAY)))
            self.assertEqual(sorted(cell["means"]), sorted(script.MODELS))

    def test_the_take_up_split_and_the_coverage_are_reported(self):
        for w in self.result["windows"].values():
            self.assertEqual(sorted(w["groups"][script.TAKE_UP]), sorted(script.TAKE_UP_LABELS))
            self.assertEqual(w["take_up"]["decision_days"], w["notes"]["scored_decision_days"])
            self.assertEqual(w["groups"][script.TAKE_UP][script.TAKE_UP_LABELS[0]]["days"], w["take_up"]["srf_days"])

    def test_the_effect_is_reported_by_lead_for_every_term(self):
        for w in self.result["windows"].values():
            self.assertEqual(sorted(w["effects"]), ["1", "2", "3", "4", "5"])
            for eff in w["effects"].values():
                for term in sdo.OPS_EXTRAS:
                    self.assertIn("mean", eff["all"][term])

    def test_the_arm_differs_from_the_candidate_only_where_a_term_enters(self):
        for w in self.result["windows"].values():
            ld = w["lead_difference"]["against_ann_net"]
            self.assertEqual(sorted(ld["differing_cells"]), ["1", "2", "3", "4", "5"])

    def test_the_page_carries_the_availability_the_arm_and_ends_with_the_marked_questions(self):
        text = self.page.read_text(encoding="utf-8")
        self.assertIn("## Availability: are the decision day's results public before 18:00?", text)
        self.assertIn("## Summary: grid CRPS of (s3c-ann-net-sameday), by lead", text)
        self.assertIn("By the decision day's own take-up", text)
        self.assertIn("## Questions for Eleonora", text)
        self.assertIn("**Options**", text)
        self.assertNotIn("GO #", text)


class CommittedRecordTests(unittest.TestCase):
    """The tracked record of the declared run, and the page generated from it."""

    RECORD = ROOT / "docs" / "research" / "s3c-sameday-ops-1349" / "result.json"
    PAGE = ROOT / "docs" / "research" / "s3c-sameday-ops-1349-result.md"

    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"), script.render(record))

    def test_the_record_is_the_declared_full_run_on_the_published_panel(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8"))
        self.assertIsNone(record["subset_from"])
        self.assertEqual((record["seed"], record["draws"], record["reps"]), (script.SEED, sp.DRAWS, script.REPS))
        self.assertEqual(record["declaration"], "metadata/s3c_sameday_ops_1349.json")
        self.assertEqual(record["models"], list(script.MODELS))
        self.assertEqual(record["decision_time"], "18:00")
        self.assertEqual(record["availability"], json.loads(script.AVAILABILITY.read_text(encoding="utf-8")))
        self.assertIn(record["panel_sha256"], json.dumps(manifest))
        for window, w in record["windows"].items():
            self.assertLessEqual(w["notes"]["last_target"], script.WINDOW_LAST[window].isoformat())
            self.assertEqual(sorted(w["lead_difference"]["ann_net_against_s3c"]["differing_cells"]), ["1", "2", "3", "4", "5"])

    def test_the_references_agree_with_the_record_of_1321(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        for window, metrics_ in record["against_1321"].items():
            for rows in metrics_.values():
                for v in rows.values():
                    self.assertLess(abs(v["difference"]), 1e-9, window)


if __name__ == "__main__":
    unittest.main()
