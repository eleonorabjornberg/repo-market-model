"""`scripts/family_ablation_1483.py` (#1483; H5 step 2, milestone H5.M3, development tier): the family-by-family ablation on (s3c-ann-net).

Written first, against the declaration. What these tests pin: that the declaration names what the module has (seed, models, arms, rows, the last day, no
amendment) and that the cleared register row exists; that each arm is the candidate with exactly one change (a drop arm lacks only the settlement term(s)
it names, the IORB arm adds only `iorb_window` and the IORB extras, none of them touches the fit's other settings, so a row is the family and nothing
else); the plan of paired tests (the model that reads the family against the one that does not); the refusal to walk at another instant; the re-used
rows (they exist in the tracked records, name the right arms and are read from the pooled group of both windows); the page (one row per family, the
marked questions with numbered options and one default each); a small run of `score`, `assemble` and `page` end to end on the fixture panel; and that
the tracked page is what the script renders from the tracked record.

No new reader and no new guard: every arm is a `dataclasses.replace` of an existing arm and reads an existing table (`AnnouncedNetSizeTable`,
`AnnouncedTermTable`, `IorbTable`), whose leakage tests and mutations are those of #1288, #1273 and #1227. The one check of this study is the instant
of the walk.

Recorded mutation (the check of this study, #1483): in `family_ablation_1483.walks_of`, the guard `if k.DECISION_TIME != DECISION_TIME:` was changed to
`if False:`. `WalkTests.test_a_walk_not_at_the_declared_instant_is_refused` then failed with `AttributeError` (with the guard gone the call went on and
met the `None` frame the test passes; `ValueError` was not raised); restored, it passes.
"""

from __future__ import annotations

import dataclasses
import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import time
from pathlib import Path

from repo_model import s3c_announced
from repo_model import spread_mr_state_calendar as sc

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("family_ablation_1483", ROOT / "scripts" / "family_ablation_1483.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["family_ablation_1483"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)

BASE = s3c_announced.ANN_NET_ARM


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_what_the_module_has(self):
        declaration = script.committed_declaration()
        self.assertEqual(declaration["issue"], 1483)
        self.assertEqual(script.SEED, 1483)
        self.assertIn("seed 1483", declaration["scoring"]["test"])
        self.assertEqual(declaration["models"], list(script.MODELS))
        self.assertEqual([a["name"] for a in declaration["arms"]], [script.model_of(a) for a in script.WALK_ARMS])
        self.assertEqual([(r["key"], r["with"], r["without"]) for r in declaration["rows"]], [(k, w, o) for k, _f, w, o in script.ROWS])
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(declaration["amendments"], [])
        self.assertIn("18:00", declaration["decision_instant"])
        self.assertEqual(sorted(f["family"] for f in declaration["families"]), sorted(script.FAMILY_ORDER))

    def test_the_register_row_is_cleared_and_names_the_declaration(self):
        row = json.loads((ROOT / "metadata" / "provisional" / "cleared" / "family_ablation_1483.json").read_text(encoding="utf-8"))
        self.assertEqual(row["declaration"], "metadata/family_ablation_1483.json")
        self.assertEqual(row["script"], "scripts/family_ablation_1483.py")
        self.assertEqual(row["pairing"], "direct")


class ArmTests(unittest.TestCase):

    def only_differs_in(self, arm, *fields):
        """`arm` equals the candidate's arm except in `fields` (and its name and role)."""

        for f in dataclasses.fields(BASE):
            if f.name in ("name", "role") + fields:
                continue
            self.assertEqual(getattr(arm, f.name), getattr(BASE, f.name), f.name)

    def test_the_nosettle_arm_lacks_both_settlement_terms_and_nothing_else(self):
        self.assertEqual(set(BASE.location) - set(script.NOSETTLE_ARM.location), set(sc.SIZED_TERMS))
        self.assertEqual(set(script.NOSETTLE_ARM.location) - set(BASE.location), set())
        self.only_differs_in(script.NOSETTLE_ARM, "location")

    def test_a_leg_arm_lacks_that_leg_alone(self):
        self.assertEqual(set(BASE.location) - set(script.NOCOUPON_ARM.location), {"settlement_coupon"})
        self.assertEqual(set(BASE.location) - set(script.NOBILL_ARM.location), {"settlement_bill"})
        self.only_differs_in(script.NOCOUPON_ARM, "location")
        self.only_differs_in(script.NOBILL_ARM, "location")

    def test_the_iorb_arm_adds_the_window_and_the_two_extras_only(self):
        self.assertEqual(set(script.IORB_ARM.location) - set(BASE.location), {"iorb_window"})
        self.assertEqual(set(BASE.location) - set(script.IORB_ARM.location), set())
        self.assertEqual(script.IORB_ARM.extra, sc.IORB_EXTRAS)
        self.assertNotIn("fomc_day", script.IORB_ARM.location)
        self.only_differs_in(script.IORB_ARM, "location", "extra")

    def test_every_arm_fits_on_direct_pairs_under_the_candidates_estimator(self):
        for arm in script.WALK_ARMS:
            self.assertTrue(arm.robust)
            self.assertEqual(sc.ridge_of(arm), sc.ROBUST_RIDGE)
            self.assertFalse(arm.interact)
        self.assertEqual(script.WALK_ARMS[0], BASE)

    def test_the_model_names_carry_the_cap_letter_and_are_distinct(self):
        names = [script.model_of(a) for a in script.WALK_ARMS]
        self.assertEqual(len(set(names)), len(names))
        self.assertTrue(all(n.startswith("sc_s3c_") for n in names))
        self.assertEqual(script.model_of(BASE), script.ANNNET)
        self.assertEqual(script.model_of(s3c_announced.ANN_ARM), script.ANN)


class PlanTests(unittest.TestCase):

    def test_a_row_is_the_model_with_the_family_against_the_one_without(self):
        self.assertEqual(script.plan(script.ANNNET), [script.NOSETTLE, script.NOCOUPON, script.NOBILL, script.ANN])
        self.assertEqual(script.plan(script.ANN), [script.S3C])
        self.assertEqual(script.plan(script.IORBS), [script.ANNNET])
        self.assertEqual(script.plan(script.NOSETTLE), [])
        self.assertEqual(script.CANDIDATES, (script.ANNNET, script.ANN, script.IORBS))

    def test_every_row_names_models_that_are_scored(self):
        for _key, _family, with_, without in script.ROWS:
            self.assertIn(with_, script.MODELS)
            self.assertIn(without, script.MODELS)


class WalkTests(unittest.TestCase):

    def test_a_walk_not_at_the_declared_instant_is_refused(self):
        held = script.k.DECISION_TIME
        script.k.DECISION_TIME = time(16, 0)
        try:
            with self.assertRaises(ValueError):
                script.walks_of("development", None, None, None, None, None, None, None)
        finally:
            script.k.DECISION_TIME = held


class ReusedRowTests(unittest.TestCase):

    def test_the_tracked_1350_record_holds_the_rows_the_page_re_uses(self):
        record = json.loads(script.RECORD_1350.read_text(encoding="utf-8"))
        rows = script.reused_rows(record)
        self.assertEqual(sorted(rows), sorted(script.WINDOWS))
        for window, found in rows.items():
            self.assertEqual(found["scarcity_state"]["with"], script.STATE_CARRIED)
            self.assertEqual(found["scarcity_state"]["without"], script.ANNNET)
            self.assertEqual(found["h41_timing"]["with"], script.STATE_PERREL)
            self.assertEqual(found["h41_timing"]["without"], script.STATE_CARRIED)
            for key in ("scarcity_state", "h41_timing"):
                pooled = found[key]["rows"]["pooled/all decision days"]
                self.assertIn("grid_crps", pooled)
                self.assertIsNotNone(pooled["grid_crps"], f"{window}/{key}")
                self.assertIn("upper_tail_twcrps", pooled)
                self.assertTrue(any(name.startswith("regime/") for name in found[key]["rows"]))
                self.assertTrue(any(name.startswith("pressure_day_type/") for name in found[key]["rows"]))

    def test_the_candidate_of_1350_is_this_studys_candidate(self):
        record = json.loads(script.RECORD_1350.read_text(encoding="utf-8"))
        self.assertIn(script.ANNNET, record["models"])
        self.assertEqual(record["decision_time"], "18:00")
        self.assertEqual(record["panel_sha256"], json.loads(script.RECORD_1345.read_text(encoding="utf-8"))["panel_sha256"])

    def test_the_tail_row_is_the_dispersion_target_of_1345(self):
        record = json.loads(script.RECORD_1345.read_text(encoding="utf-8"))
        self.assertIn(script.TAIL_TARGET, record["targets"])
        self.assertEqual(script.reused_tail(record)["window"], "development")


class PageTests(unittest.TestCase):

    def test_the_questions_are_marked_numbered_and_carry_a_default(self):
        text = "\n".join(script.question())
        self.assertIn("Questions for Eleonora", text)
        for number in (1, 2, 3):
            self.assertIn(f"**Question {number}.", text)
        self.assertEqual(text.count("(default"), 3)
        self.assertNotIn("GO #", text)


class EndToEndTests(unittest.TestCase):
    """`score`, `assemble` and `page` with the walk started late on the fixture panel, with few resamples: the shape, not the figures."""

    FIRST = "2025-09-02"

    @classmethod
    def setUpClass(cls):
        import panel_cache

        cls.panel_path = Path(panel_cache.published_build()["path"])
        cls.tmp = tempfile.TemporaryDirectory()
        base = Path(cls.tmp.name)
        for window in script.WINDOWS:
            script.main(["score", "--panel", str(cls.panel_path), "--window", window, "--output", str(base / f"result-{window}.json"),
                         "--draws", "20", "--reps", "5", "--workers", "2", "--first", cls.FIRST])
        cls.output, cls.page = base / "result.json", base / "page.md"
        script.main(["assemble", "--input-dir", str(base), "--output", str(cls.output)])
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

    def test_every_candidate_is_scored_against_what_the_plan_says(self):
        for w in self.result["windows"].values():
            cell = w["groups"]["pooled"]["all decision days"]["grid_crps"]
            self.assertEqual(sorted(cell["means"]), sorted(script.MODELS))
            for candidate in script.CANDIDATES:
                self.assertEqual(sorted(cell["vs"][candidate]), sorted(script.plan(candidate)))

    def test_the_splits_of_the_directive_are_reported(self):
        for w in self.result["windows"].values():
            self.assertEqual(sorted(w["groups"]), sorted(script.SPLITS))

    def test_a_drop_arm_differs_from_the_candidate_only_where_a_term_enters(self):
        for w in self.result["windows"].values():
            self.assertEqual(sorted(w["differing_cells"]), sorted(script.ARMS))
            for ld in w["differing_cells"].values():
                self.assertEqual(sorted(ld["differing_cells"]), ["1", "2", "3", "4", "5"])

    def test_the_page_has_one_row_per_family_and_ends_with_the_marked_questions(self):
        text = self.page.read_text(encoding="utf-8")
        table = text.split("## The families, one row each")[1].split("\n\n")[1]
        for family in script.FAMILY_ORDER:
            self.assertIn(f"| {family} |", table)
        self.assertIn("## Questions for Eleonora", text)
        self.assertNotIn("GO #", text)


class CommittedRecordTests(unittest.TestCase):
    """The tracked record of the declared run, and the page generated from it."""

    RECORD = ROOT / "docs" / "research" / "family-ablation-1483" / "result.json"
    PAGE = ROOT / "docs" / "research" / "family-ablation-1483-result.md"

    @unittest.skipUnless(RECORD.exists(), "the declared run has not been scored yet")
    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"), script.render(record))
