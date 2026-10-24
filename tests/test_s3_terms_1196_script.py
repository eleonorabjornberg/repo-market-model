"""The helpers of `scripts/s3_terms_1196.py` (#1196; H5 step 3, development tier).

Written first, against the declaration. It adds no reader of its own: the scored days pass `spread_mean_reversion_686.require_scored_days`
(its recorded mutation is in `test_spread_mean_reversion_686_script`), the state and term guards are recorded in
`test_spread_mr_state_calendar`, and the arms' settings in `test_spread_mr_s3_terms`. What these tests pin: that the declaration names
the arms the module has; that a reading is taken from the mean-d bound and the skill interval's reading is kept beside it; the pair
plan; that the page says what the ruling requires (a further look after (s3) was chosen, aimed at the 2020 and FOMC-day upper-tail
losses, Lens C's caveat, FOMC and IORB days named, a marked question with a default); and a small run of `score` and `page` end to end
on a late subset of the fixture panel, with and without synthetic walks of `gbm_funding`.
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
from repo_model import spread_mr_state_calendar as sc

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("s3_terms_1196", ROOT / "scripts" / "s3_terms_1196.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["s3_terms_1196"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)


def row(skill_low, skill_high, d_low, d_high):
    return {"skill": 0.01, "skill_interval": [skill_low, skill_high], "difference": 0.01, "difference_interval": [d_low, d_high]}


class ReadingTests(unittest.TestCase):

    def test_a_reading_is_taken_from_the_mean_d_bound_not_the_skill_interval(self):
        self.assertEqual(script.verdict(row(0.01, 0.05, 0.001, 0.05)), "gain")
        self.assertEqual(script.verdict(row(0.01, 0.05, -0.001, 0.05)), "undecided")  # the skill interval would read a gain
        self.assertEqual(script.skill_verdict(row(0.01, 0.05, -0.001, 0.05)), "gain")
        self.assertEqual(script.verdict(row(-0.05, 0.01, -0.05, -0.001)), "loss")
        self.assertEqual(script.verdict(None), "undecided")

    def test_the_words_carry_the_skill_readings_only_where_it_differs(self):
        self.assertEqual(script.reading_words(row(0.01, 0.05, 0.001, 0.05)), "gain")
        self.assertEqual(script.reading_words(row(0.01, 0.05, -0.001, 0.05)), "undecided (skill interval: gain)")

    def test_a_cell_shows_the_skill_interval_and_the_mean_d_bound(self):
        text = script._fmt(row(0.01, 0.05, 0.001, 0.05))
        self.assertIn("[+1.0%, +5.0%]", text)
        self.assertIn("d +0.010 [+0.001, +0.050]", text)

    def test_the_pair_plan_names_b1_prime_beside_b1_and_s3_for_the_two_arms(self):
        for arm in (script.S3S, script.S3C):
            plan = script.pair_plan(arm, ("gbm_funding",))
            for name in ("B1", "B1_prime", "B2", sc.ARM_A, script.S3, "gbm_funding"):
                self.assertIn(name, plan, (arm, name))
        self.assertNotIn(script.S3, script.pair_plan(script.S3, ()))
        self.assertIn(sc.ARM_A, script.pair_plan(script.S3, ()))
        self.assertNotIn(sc.ARM_A, script.pair_plan(sc.ARM_A, ()))
        self.assertNotIn("gbm_funding", script.pair_plan(script.S3S, ()))

    def test_the_politis_white_block_is_against_a_and_against_s3_for_the_two_arms(self):
        self.assertEqual(script.block_plan(sc.ARM_A), [])
        self.assertEqual(script.block_plan(script.S3), [sc.ARM_A])
        for arm in (script.S3S, script.S3C):
            self.assertEqual(script.block_plan(arm), [sc.ARM_A, script.S3])


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_the_arms_the_module_has(self):
        declaration = json.loads(script.DECLARATION.read_text(encoding="utf-8"))
        self.assertEqual(script.committed_declaration()["issue"], 1196)
        self.assertEqual([a["name"] for a in declaration["arms"]], [sc.ARM_A] + [a.name for a in sc.S3_TERMS])
        for entry in declaration["arms"][1:]:
            arm = sc.ALL_ARMS[entry["name"]]
            self.assertEqual(entry["location_terms"], list(arm.location), arm.name)
            self.assertEqual((entry["ridge"], entry["robust"], entry["interact"]), (sc.ridge_of(arm), arm.robust, arm.interact), arm.name)
        self.assertEqual(declaration["limits"]["arms"], len(declaration["arms"]) - 1)  # (a) is the comparator
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(declaration["scoring"]["paired"].count("seed 1196"), 1)
        self.assertEqual(script.SEED, 1196)

    def test_both_arms_are_robust_with_the_ridge_of_5_and_only_one_has_each_extra(self):
        for arm in (sc.S3_STATE, sc.S3_CAL):
            self.assertTrue(arm.robust)
            self.assertEqual(sc.ridge_of(arm), 5.0)
        self.assertEqual((sc.S3_STATE.interact, sc.S3_CAL.interact), (True, False))
        self.assertEqual(sc.S3_STATE.location, cal.NO_FOMC_IORB)
        self.assertEqual(sc.S3_CAL.location, cal.ALL_TERMS)

    def test_the_aimed_splits_are_the_two_upper_tail_losses_of_s3(self):
        self.assertEqual(script.AIMED, (("regime", "2020"), ("target_day_type", "fomc_day")))


class EndToEndTests(unittest.TestCase):
    """`score` and `page` on the last months of the fixture panel, with few resamples: the shape, not the figures."""

    FIRST = "2025-06-02"

    @classmethod
    def setUpClass(cls):
        sys.modules["s3_terms_1196"] = script  # another test module may have re-registered the name (pickling by module name)
        import panel_cache
        from repo_model.baseline import panel_sha256
        from repo_model.data import load_daily_panel

        cls.panel_path = Path(panel_cache.published_build()["path"])
        cls.tmp = tempfile.TemporaryDirectory()
        base = Path(cls.tmp.name)
        walks = base / "walks"
        walks.mkdir()
        sha = panel_sha256(cls.panel_path)
        panel = load_daily_panel(cls.panel_path)
        for h in sp.HORIZONS:
            laws = {row_.date.isoformat(): [1.0 + 0.2 * i for i in range(len(sp.GRID))]
                    for row_ in panel if date(2025, 5, 1) <= row_.date <= date(2025, 12, 31)}
            (walks / f"gbm_funding_h{h}.json").write_text(json.dumps(
                {"variant": "gbm_funding", "horizon": h, "levels": list(sp.GRID), "panel_sha256": sha, "laws": laws}), encoding="utf-8")
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

    def test_every_arm_is_scored_against_the_references_and_s3(self):
        cell = self.result["groups"]["pooled"]["all decision days"]["grid_crps"]
        self.assertEqual(sorted(cell["vs"]), sorted(script.ARMS))
        for arm in script.ARMS:
            for name in ("B1", "B1_prime", "B2", "gbm_funding"):
                self.assertIn(name, cell["vs"][arm], (arm, name))
            if arm != sc.ARM_A:
                self.assertIn(sc.ARM_A, cell["vs"][arm], arm)
        for arm in (script.S3S, script.S3C):
            self.assertIn(script.S3, cell["vs"][arm], arm)
        self.assertEqual(sorted(cell["means"]), sorted(script.MODELS + script.GBMS))

    def test_the_rows_carry_the_mean_d_interval_beside_the_skill_interval(self):
        cell = self.result["groups"]["pooled"]["all decision days"]["grid_crps"]
        one = cell["vs"][script.S3S][script.S3]
        self.assertIn("skill_interval", one)
        self.assertIn("difference_interval", one)

    def test_without_walks_the_gbm_rows_are_absent_and_the_page_says_so(self):
        cell = self.without["groups"]["pooled"]["all decision days"]["grid_crps"]
        self.assertNotIn("gbm_funding", cell["vs"][script.S3])
        self.assertEqual(self.without["gbm"], [])
        text = self.bare_page.read_text(encoding="utf-8")
        self.assertIn("were not supplied", text)
        self.assertIn("stays on Eleonora's Mac", text)

    def test_the_splits_the_directive_names_are_all_there_with_fomc_and_iorb_days_named(self):
        groups = self.result["groups"]
        self.assertIn("pooled", groups)
        self.assertEqual(sorted(groups["lead"]), [f"h={h}" for h in sp.HORIZONS])
        self.assertIn("2025-26", groups["regime"])
        for label in ("dom_19_23", "ordinary", "calendar_days"):
            self.assertIn(label, groups["target_day_type"])
        # the late subset has fewer than 20 FOMC or IORB-window target days, so those groups are listed and not tested here; the
        # declared run has 118 and 78 of them (metadata/s3_terms_1196.json)
        for label in ("fomc_day", "iorb_window"):
            self.assertIn(label, script.DAY_TYPES)
            self.assertTrue(label in groups["target_day_type"] or f"target_day_type/{label}" in self.result["skipped_groups"], label)
        self.assertIn("fomc_day", self.result["q95_by_day_type"])
        self.assertIn("iorb_window", self.result["q95_by_day_type"])

    def test_the_scaled_score_is_not_scored_and_the_page_says_why(self):
        self.assertNotIn("scaled", self.result["groups"])
        self.assertFalse(hasattr(script, "SCALED"))
        declaration = json.loads(script.DECLARATION.read_text(encoding="utf-8"))
        self.assertNotIn("scaled_score", declaration["scoring"])
        self.assertEqual([a["number"] for a in declaration["amendments"]], [1])
        self.assertIn("scaled score of #967 is not scored", self.page.read_text(encoding="utf-8"))

    def test_the_calibration_is_pooled_and_by_regime_for_every_model_under_both_hit_rules_and_both_bands(self):
        self.assertIn("pooled/all cells", self.result["q95"])
        self.assertIn("regime/2025-26", self.result["q95"])
        for model in script.MODELS + script.GBMS:
            entry = self.result["q95"]["pooled/all cells"][model]
            for rule in script.RATES:
                self.assertTrue(0.0 <= entry[rule]["rate"] <= 1.0, (model, rule))
                self.assertEqual(len(entry[rule]["interval"]), 2)
            self.assertLessEqual(entry["b90_open"]["rate"], entry["b90_closed"]["rate"])
            self.assertLessEqual(entry["hit_above"]["rate"], entry["hit_at_or_above"]["rate"])

    def test_the_politis_white_block_is_beside_the_protocol_block_against_a_and_s3(self):
        pooled = self.result["politis_white"]["pooled"]["all decision days"]["grid_crps"]
        self.assertEqual(sorted(pooled), sorted(a for a in script.ARMS if a != sc.ARM_A))
        self.assertEqual(sorted(pooled[script.S3S]), sorted([sc.ARM_A, script.S3]))
        self.assertEqual(sorted(pooled[script.S3]), [sc.ARM_A])
        self.assertIn("at_block", pooled[script.S3C][sc.ARM_A])

    def test_the_effect_of_each_term_is_in_bp_and_in_scale_units_by_regime_and_the_calendar_arm_has_fomc(self):
        effects = self.result["term_effect_intervals"]
        self.assertEqual(sorted(effects), sorted(a.name for a in sc.S3_TERMS))
        for quantity in ("bp", "std", "miss"):
            self.assertIn(quantity, effects[script.S3]["month_end"]["2025-26"])
        self.assertIn("fomc_day", self.result["term_effects"][script.S3C])
        self.assertEqual(sorted(self.result["state_slopes"]), sorted(cal.NO_FOMC_IORB))
        for per_lead in self.result["state_slopes"].values():
            self.assertEqual(sorted(per_lead), [str(h) for h in sp.HORIZONS])

    def test_the_slopes_are_zero_in_the_arms_with_no_interaction(self):
        counts = self.result["refit_term_counts"]
        self.assertEqual(sorted(counts[script.S3C]), sorted(cal.ALL_TERMS))
        for arm in (script.S3, script.S3S):
            for term in ("fomc_day", "iorb_window"):
                self.assertEqual(counts[arm][term], [0] * len(sp.HORIZONS), (arm, term))

    def test_the_aimed_rows_are_the_2020_regime_and_the_fomc_days_for_s3_and_the_two_arms(self):
        rows = script.aimed_rows(self.result)
        for r in rows:
            self.assertIn((r["split"], r["group"]), script.AIMED)
            self.assertIn(r["arm"], (script.S3, script.S3S, script.S3C))
        self.assertEqual(len(rows), 3 * len([1 for s, l in script.AIMED if l in self.result["groups"].get(s, {})]))

    def test_the_page_states_what_the_ruling_requires(self):
        text = self.page.read_text(encoding="utf-8")
        for needle in ("further look at 2018-2025 after (s3) was chosen", "#1187", "Lens C", "mean d", "B1' (#960)",
                       "Politis-White", "fomc_day", "iorb_window", "## Aimed at (s3)'s upper-tail losses", "Development data, not a verdict".lower()):
            self.assertIn(needle.lower(), text.lower(), needle)
        self.assertIn("understated about 2x", text)

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
        self.assertEqual(text.count("## Question for Eleonora"), 1)
        self.assertTrue(tail.rstrip().splitlines()[-1].startswith("3."))


if __name__ == "__main__":
    unittest.main()
