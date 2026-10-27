"""The helpers of `scripts/calendar_mr_1115.py` (#1115; H5 step 3, development tier).

Written after the script, which is measurement code. It adds no reader of its own: the scored days pass
`spread_mean_reversion_686.require_scored_days` (its recorded mutation is in `test_spread_mean_reversion_686_script`), and the
term guards are recorded in `test_spread_mr_calendar`. What these tests pin: the target-day labels, the reading rule, the
refusal of a partly present set of gradient-boosted walks or of walks from another panel, the closing question's options and
default, and a small run of `score` and `page` end to end on a late subset of the fixture panel, with and without synthetic walks
of the two gradient-boosted models.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

from repo_model import scoring_protocol as sp
from repo_model import spread_mr_calendar as cal

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("calendar_mr_1115", ROOT / "scripts" / "calendar_mr_1115.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["calendar_mr_1115"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)


class ReadingTests(unittest.TestCase):

    def test_a_gain_needs_the_interval_above_zero_and_a_loss_below(self):
        self.assertEqual(script.verdict({"skill_interval": [0.01, 0.05]}), "gain")
        self.assertEqual(script.verdict({"skill_interval": [-0.05, -0.01]}), "loss")
        self.assertEqual(script.verdict({"skill_interval": [-0.01, 0.05]}), "undecided")
        self.assertEqual(script.verdict({"undefined": "no variance"}), "undecided")
        self.assertEqual(script.verdict(None), "undecided")

    def test_the_pair_plan_names_b1_prime_beside_b1_and_the_arms_it_isolates(self):
        plan = script.pair_plan("mr_cal_c_location_scale", ("gbm_funding",))
        for name in ("B1", "B1_prime", "B2", "spread_mr_ctx", cal.ARM_A, "mr_cal_b_location", "mr_cal_d_no_fomc_iorb", "gbm_funding"):
            self.assertIn(name, plan)
        self.assertNotIn("gbm_funding_cal_aligned", plan)
        self.assertNotIn(cal.ARM_A, script.pair_plan(cal.ARM_A, ()))


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_the_arms_and_terms_the_module_has(self):
        declaration = json.loads(script.DECLARATION.read_text(encoding="utf-8"))
        self.assertEqual(script.committed_declaration()["issue"], 1115)
        self.assertEqual([a["name"] for a in declaration["arms"]], list(cal.ARM_NAMES))
        self.assertEqual([t["name"] for t in declaration["terms"]["listed_in_full"]], list(cal.ALL_TERMS))
        for arm in declaration["arms"][1:]:
            self.assertEqual(arm["location_terms"], list(next(a for a in cal.ARMS if a.name == arm["name"]).location))
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(declaration["estimation"]["pairs"][:6], "direct")


class WalkReaderTests(unittest.TestCase):

    def write(self, directory, h, name="gbm_funding", sha="abc"):
        document = {"variant": name, "horizon": h, "levels": list(sp.GRID), "panel_sha256": sha, "laws": {}}
        (directory / f"{name}_h{h}.json").write_text(json.dumps(document), encoding="utf-8")

    def test_no_walks_is_no_comparison(self):
        self.assertIsNone(script.load_gbm(None, "abc", None, "gbm_funding"))
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(script.load_gbm(Path(tmp), "abc", None, "gbm_funding"))

    def test_some_leads_but_not_all_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.write(Path(tmp), 1)
            with self.assertRaisesRegex(ValueError, "walk every lead or none"):
                script.load_gbm(Path(tmp), "abc", None, "gbm_funding")

    def test_a_walk_from_another_panel_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            for h in sp.HORIZONS:
                self.write(Path(tmp), h, sha="other")
            with self.assertRaisesRegex(ValueError, "walked from panel"):
                script.load_gbm(Path(tmp), "abc", None, "gbm_funding")


class EndToEndTests(unittest.TestCase):
    """`score` and `page` on the last months of the fixture panel, with few resamples: the shape, not the figures."""

    FIRST = "2025-06-02"

    @classmethod
    def setUpClass(cls):
        sys.modules["calendar_mr_1115"] = script  # another test module may have re-registered the name (pickling by module name)
        import panel_cache
        from repo_model.baseline import panel_sha256
        from repo_model.data import load_daily_panel

        # Another test module that loads this script under the same name (faster_scale_1153, state_calendar_1145)
        # replaces the entry at import time when both land in one shard; the pool pickles by module name.
        sys.modules["calendar_mr_1115"] = script
        cls.panel_path = Path(panel_cache.published_build()["path"])
        cls.tmp = tempfile.TemporaryDirectory()
        base = Path(cls.tmp.name)
        walks = base / "walks"
        walks.mkdir()
        sha = panel_sha256(cls.panel_path)
        panel = load_daily_panel(cls.panel_path)
        for name, offset in (("gbm_funding", 1.0), ("gbm_funding_cal_aligned", 0.5)):
            for h in sp.HORIZONS:
                laws = {row.date.isoformat(): [offset + 0.2 * i for i in range(len(sp.GRID))]
                        for row in panel if date(2025, 5, 1) <= row.date <= date(2025, 12, 31)}
                (walks / f"{name}_h{h}.json").write_text(json.dumps(
                    {"variant": name, "horizon": h, "levels": list(sp.GRID), "panel_sha256": sha, "laws": laws}), encoding="utf-8")
        cls.output, cls.page = base / "result.json", base / "page.md"
        cls.bare, cls.bare_page = base / "bare.json", base / "bare.md"
        args = ["--draws", "20", "--reps", "5", "--workers", "2", "--first", cls.FIRST, "--panel", str(cls.panel_path)]
        script.main(["score", *args, "--walks", str(walks), "--output", str(cls.output)])
        script.main(["page", "--score", str(cls.output), "--output", str(cls.page)])
        script.main(["score", *args, "--output", str(cls.bare)])
        script.main(["page", "--score", str(cls.bare), "--output", str(cls.bare_page)])
        cls.result = json.loads(cls.output.read_text(encoding="utf-8"))
        cls.without = json.loads(cls.bare.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_every_arm_is_scored_against_b1_b1_prime_b2_the_context_model_and_the_gbm_models(self):
        cell = self.result["groups"]["pooled"]["all decision days"]["grid_crps"]
        self.assertEqual(sorted(cell["vs"]), sorted(cal.ARM_NAMES))
        for arm in cal.ARM_NAMES:
            for name in ("B1", "B1_prime", "B2", "spread_mr_ctx", "gbm_funding", "gbm_funding_cal_aligned"):
                self.assertIn(name, cell["vs"][arm], (arm, name))
        self.assertEqual(sorted(cell["means"]), sorted(script.MODELS + script.GBMS))

    def test_without_walks_the_gbm_rows_are_absent_and_the_page_says_so(self):
        cell = self.without["groups"]["pooled"]["all decision days"]["grid_crps"]
        self.assertNotIn("gbm_funding", cell["vs"][cal.ARM_A])
        self.assertEqual(self.without["gbm"], [])
        self.assertIn("were not supplied", self.bare_page.read_text(encoding="utf-8"))

    def test_the_splits_the_directive_names_are_all_there(self):
        groups = self.result["groups"]
        self.assertIn("pooled", groups)
        self.assertEqual(sorted(groups["lead"]), [f"h={h}" for h in sp.HORIZONS])
        self.assertIn("2025-26", groups["regime"])
        for label in ("dom_19_23", "ordinary", "calendar_days"):
            self.assertIn(label, groups["target_day_type"])

    def test_the_q95_exceedance_check_is_pooled_and_by_regime_for_every_model(self):
        self.assertIn("pooled/all cells", self.result["q95"])
        self.assertIn("regime/2025-26", self.result["q95"])
        for model in script.MODELS + script.GBMS:
            entry = self.result["q95"]["pooled/all cells"][model]["hit_above"]
            self.assertTrue(0.0 <= entry["rate"] <= 1.0)
            self.assertEqual(len(entry["interval"]), 2)
            self.assertIn("hit_at_or_above", self.result["q95"]["pooled/all cells"][model])

    def test_the_politis_white_block_is_reported_beside_the_protocol_block(self):
        pooled = self.result["politis_white"]["pooled"]["all decision days"]["grid_crps"]
        self.assertEqual(sorted(pooled), sorted(a for a in cal.ARM_NAMES if a != cal.ARM_A))
        self.assertIn("at_block", next(iter(pooled.values())))

    def test_no_day_after_the_last_scored_day_is_read(self):
        self.assertLessEqual(self.result["notes"]["last_target"], script.LAST_DAY.isoformat())
        self.assertEqual(self.result["subset_from"], self.FIRST)

    def test_the_page_ends_with_the_marked_question_its_options_and_a_default(self):
        text = self.page.read_text(encoding="utf-8")
        self.assertIn("B1' (#960)", text)
        tail = text[text.index("## Question for Eleonora"):]
        self.assertIn("Nothing is adopted here and no claim changes", tail)
        for option in ("1. **Keep `gbm_funding`", "2. **Name the calendar-aware", "3. **Ask for a further step"):
            self.assertIn(option, tail)
        self.assertIn("(default)", tail)
        self.assertEqual(text.count("## Question for Eleonora"), 1)
        self.assertTrue(tail.rstrip().splitlines()[-1].startswith("3."))  # the question is the last thing on the page
        self.assertIn("development data, not a verdict", text.lower())


if __name__ == "__main__":
    unittest.main()
