"""The helpers of `scripts/s3_iorbs_1227.py` (#1227; H5 step 3, development tier).

Written first, against the declaration. It adds no reader of its own: the scored days pass `spread_mean_reversion_686.require_scored_days`
(its recorded mutation is in `test_spread_mean_reversion_686_script`), the availability of the two IORB terms and its recorded mutation
are in `test_spread_mr_s3_iorbs`, and the readings are #1196's (`test_s3_terms_1196_script`). What these tests pin: that the declaration
names the arm the module has and the same terms; that the pair plan names B1, B1', B2, (a) and, for the arm, (s3); that the counts of the
IORB changes (29, 6 technical) come from the announcement table and the column; that the page says what the ruling requires (the count
is small, the arm counts toward the variant count, adoption is hers, development data not a verdict, Lens C's caveat, the IORB-window
rows named, a marked question with a default); and a small run of `score` and `page` end to end on a late subset of the fixture panel.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

from repo_model import announced_iorb
from repo_model import scoring_protocol as sp
from repo_model import spread_mr_state_calendar as sc

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("s3_iorbs_1227", ROOT / "scripts" / "s3_iorbs_1227.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["s3_iorbs_1227"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)


class PlanTests(unittest.TestCase):

    def test_the_pair_plan_names_b1_prime_beside_b1_and_s3_for_the_arm_only(self):
        plan = script.pair_plan(script.S3I)
        for name in ("B1", "B1_prime", "B2", sc.ARM_A, script.S3):
            self.assertIn(name, plan, name)
        self.assertNotIn(script.S3, script.pair_plan(script.S3))
        self.assertIn(sc.ARM_A, script.pair_plan(script.S3))
        self.assertEqual(script.pair_plan(sc.ARM_A), ["B1", "B1_prime", "B2"])

    def test_the_models_are_the_three_references_and_the_three_arms(self):
        self.assertEqual(script.ARMS, (sc.ARM_A, "sc_s3_robust", "sc_s3_iorbs"))
        self.assertEqual(script.MODELS, ("B1", "B1_prime", "B2") + script.ARMS)
        self.assertEqual(script.SEED, 1227)


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_the_arm_and_terms_the_module_has(self):
        declaration = json.loads(script.DECLARATION.read_text(encoding="utf-8"))
        self.assertEqual(script.committed_declaration()["issue"], 1227)
        self.assertEqual([a["name"] for a in declaration["arms"]], [sc.ARM_A] + [a.name for a in sc.S3_IORBS_ARMS])
        for entry in declaration["arms"][1:]:
            arm = sc.ALL_ARMS[entry["name"]]
            self.assertEqual(entry["location_terms"], list(arm.location), arm.name)
            self.assertEqual(entry["extra_terms"], list(arm.extra), arm.name)
            self.assertEqual((entry["ridge"], entry["robust"]), (sc.ridge_of(arm), arm.robust), arm.name)
        self.assertEqual(declaration["limits"]["arms"], 1)
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(declaration["scoring"]["paired"].count("seed 1227"), 1)
        self.assertEqual(declaration["amendments"], [])

    def test_the_six_technical_changes_the_declaration_lists_are_the_tables(self):
        declaration = json.loads(script.DECLARATION.read_text(encoding="utf-8"))
        changes = [a for a in announced_iorb.load_announcements(script.c.IORB_TABLE) if a.kind == "change"]
        listed = sorted(a.effective.isoformat() for a in changes if sc.technical(a.change_bps))
        self.assertEqual(len(listed), 6)
        for day in listed:
            self.assertIn(day, declaration["terms"]["iorb_technical"])
        self.assertEqual(len(changes), 29)


class CountsTests(unittest.TestCase):

    def test_the_counts_are_the_announcement_tables_and_the_column_misses_the_sunday_cut(self):
        import test_spread_mr_state_calendar as base

        counts = script.iorb_counts(base.ANNOUNCEMENTS, sc.IorbTable(base.PANEL, base.ANNOUNCEMENTS), base.PANEL, script.load_split_declaration(script.c.SPLITS))
        self.assertEqual((counts["changes"], counts["technical"]), (29, 6))
        self.assertIn("2020-03-16", counts["not_in_column"])
        self.assertEqual(counts["in_column"] + len(counts["not_in_column"]), 29)
        self.assertEqual(sum(v["changes"] for v in counts["by_regime"].values()), 29)
        self.assertEqual(sum(v["technical"] for v in counts["by_regime"].values()), 6)
        self.assertGreaterEqual(counts["by_regime"]["2018-19"]["technical"], 3)  # "most of the six fall in 2018-19"


class CommittedRecordTests(unittest.TestCase):
    """The tracked record of the declared run, and the page generated from it."""

    RECORD = ROOT / "docs" / "research" / "s3-iorbs-1227" / "result.json"
    PAGE = ROOT / "docs" / "research" / "s3-iorbs-1227-result.md"

    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"), script.render(record))

    def test_the_record_is_the_declared_full_run_not_a_subset(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8"))
        self.assertIsNone(record["subset_from"])
        self.assertEqual((record["seed"], record["draws"]), (script.SEED, sp.DRAWS))
        self.assertEqual(record["declaration"], "metadata/s3_iorbs_1227.json")
        self.assertEqual(record["models"], list(script.MODELS))
        self.assertLessEqual(record["notes"]["last_target"], script.LAST_DAY.isoformat())
        self.assertIn(record["panel_sha256"], json.dumps(manifest))
        self.assertEqual((record["iorb"]["changes"], record["iorb"]["technical"]), (29, 6))

    def test_arm_a_and_s3_reproduce_the_figures_of_1196_on_the_same_days(self):
        """(a) and (s3) are the same code on the same panel and days as #1196's run, so their pooled means agree with its record."""

        other = ROOT / "docs" / "research" / "s3-terms-1196" / "result.json"
        mine = json.loads(self.RECORD.read_text(encoding="utf-8"))["groups"]["pooled"]["all decision days"]
        theirs = json.loads(other.read_text(encoding="utf-8"))["groups"]["pooled"]["all decision days"]
        for metric in script.METRIC_NAMES:
            for name in (sc.ARM_A, script.S3, "B1", "B1_prime", "B2"):
                self.assertAlmostEqual(mine[metric]["means"][name], theirs[metric]["means"][name], places=9, msg=(metric, name))


class EndToEndTests(unittest.TestCase):
    """`score` and `page` on the last months of the fixture panel, with few draws: the shape, not the figures."""

    FIRST = "2025-06-02"

    @classmethod
    def setUpClass(cls):
        sys.modules["s3_iorbs_1227"] = script  # another test module may have re-registered the name (pickling by module name)
        import panel_cache

        cls.panel_path = Path(panel_cache.published_build()["path"])
        cls.tmp = tempfile.TemporaryDirectory()
        base = Path(cls.tmp.name)
        cls.output, cls.page = base / "result.json", base / "page.md"
        args = ["--draws", "20", "--workers", "2", "--first", cls.FIRST, "--panel", str(cls.panel_path)]
        script.main(["score", *args, "--output", str(cls.output)])
        script.main(["page", "--score", str(cls.output), "--output", str(cls.page)])
        cls.result = json.loads(cls.output.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_the_arm_is_scored_against_the_references_and_s3(self):
        cell = self.result["groups"]["pooled"]["all decision days"]["grid_crps"]
        self.assertEqual(sorted(cell["vs"]), sorted(script.ARMS))
        for arm in script.ARMS:
            for name in ("B1", "B1_prime", "B2"):
                self.assertIn(name, cell["vs"][arm], (arm, name))
            if arm != sc.ARM_A:
                self.assertIn(sc.ARM_A, cell["vs"][arm], arm)
        self.assertIn(script.S3, cell["vs"][script.S3I])
        self.assertNotIn(script.S3, cell["vs"][script.S3])
        self.assertEqual(sorted(cell["means"]), sorted(script.MODELS))

    def test_the_rows_carry_the_mean_d_interval_beside_the_skill_interval(self):
        one = self.result["groups"]["pooled"]["all decision days"]["grid_crps"]["vs"][script.S3I][script.S3]
        self.assertIn("skill_interval", one)
        self.assertIn("difference_interval", one)

    def test_the_splits_the_directive_names_are_all_there_with_the_iorb_window_named(self):
        groups = self.result["groups"]
        self.assertEqual(sorted(groups["lead"]), [f"h={h}" for h in sp.HORIZONS])
        self.assertIn("2025-26", groups["regime"])
        for label in ("dom_19_23", "ordinary", "calendar_days"):
            self.assertIn(label, groups["target_day_type"])
        # the late subset has fewer than 20 IORB-window target days, so that group is listed and not tested here; the declared run has
        # 78 of them
        self.assertIn("iorb_window", script.DAY_TYPES)
        self.assertTrue("iorb_window" in groups["target_day_type"] or "target_day_type/iorb_window" in self.result["skipped_groups"])

    def test_the_counts_the_page_states_are_in_the_record(self):
        self.assertEqual((self.result["iorb"]["changes"], self.result["iorb"]["technical"]), (29, 6))
        text = self.page.read_text(encoding="utf-8")
        self.assertIn("There are 29 IORB changes", text)
        self.assertIn("6 of them technical", text)
        self.assertIn("The count is small", text)

    def test_the_terms_are_estimated_at_leads_1_to_3_only(self):
        for term in script.IORB_TERMS:
            self.assertEqual(sorted(self.result["entering"][term]), [str(h) for h in sp.HORIZONS])
            for h in (4, 5):
                self.assertEqual(self.result["entering"][term][str(h)]["refits_entered"], 0, (term, h))

    def test_the_window_days_carry_a_kind_and_the_shift_the_arm_added(self):
        days = self.result["window_days"]
        for day, cell in days.items():
            self.assertIn(cell["kind"], ("technical", "ordinary change"))
            self.assertLessEqual(day, script.LAST_DAY.isoformat())
            self.assertAlmostEqual(cell["total"], sum(cell[t] for t in script.IORB_TERMS), places=9)

    def test_the_page_states_what_the_ruling_requires(self):
        text = self.page.read_text(encoding="utf-8")
        for needle in ("counts toward the variant count", "Adoption is yours", "Lens C", "mean d", "B1' (#960)", "iorb_window",
                       "## The IORB-window rows", "Development data, not a verdict", "technical", "listed, not tested"):
            self.assertIn(needle.lower(), text.lower(), needle)
        self.assertIn("understated about 2x", text)
        self.assertEqual(text.count("## Question for Eleonora"), 1)

    def test_no_day_after_the_last_scored_day_is_read(self):
        self.assertLessEqual(self.result["notes"]["last_target"], script.LAST_DAY.isoformat())
        self.assertEqual(self.result["subset_from"], self.FIRST)

    def test_the_page_ends_with_the_marked_question_its_options_and_a_default(self):
        text = self.page.read_text(encoding="utf-8")
        tail = text[text.index("## Question for Eleonora"):]
        self.assertIn("Nothing is adopted here and no claim changes", tail)
        for option in ("1. **Keep (s3)", "2. **Replace (s3)", "3. **Ask for a further step"):
            self.assertIn(option, tail)
        self.assertIn("(default)", tail)
        self.assertTrue(tail.rstrip().splitlines()[-1].startswith("3."))


if __name__ == "__main__":
    unittest.main()
