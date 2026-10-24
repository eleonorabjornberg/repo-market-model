"""The helpers of `scripts/s3_decomposition_1172.py` (#1172; H5 step 3, development tier).

Written first, against the declaration. It adds no reader of its own: the scored days pass `spread_mean_reversion_686.require_scored_days`
(its recorded mutation is in `test_spread_mean_reversion_686_script`), the state and term guards are recorded in
`test_spread_mr_state_calendar`, and the size and v4 guards in `test_spread_mr_s3_decomposition`. What these tests pin: that the
declaration names the arms the modules have; that a reading is taken from the mean-d bound and the skill interval's reading is kept
beside it; the kill rule's arithmetic; the pair plan; and a small run of `score` and `page` end to end on a late subset of the fixture
panel, with and without synthetic walks of `gbm_funding`.
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

import legacy_day_types

# this module reproduces legacy figures: the pre-#1135 day types (see tests/legacy_day_types.py)
setUpModule, tearDownModule = legacy_day_types.setUpModule, legacy_day_types.tearDownModule

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("s3_decomposition_1172", ROOT / "scripts" / "s3_decomposition_1172.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["s3_decomposition_1172"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)


def row(skill_low, skill_high, d_low, d_high):
    return {"skill": 0.01, "skill_interval": [skill_low, skill_high], "difference": 0.01, "difference_interval": [d_low, d_high]}


class ReadingTests(unittest.TestCase):

    def test_a_reading_is_taken_from_the_mean_d_bound_not_the_skill_interval(self):
        self.assertEqual(script.verdict(row(0.01, 0.05, 0.001, 0.05)), "gain")
        self.assertEqual(script.verdict(row(0.01, 0.05, -0.001, 0.05)), "undecided")  # the skill interval would read a gain
        self.assertEqual(script.skill_verdict(row(0.01, 0.05, -0.001, 0.05)), "gain")
        self.assertEqual(script.verdict(row(-0.05, 0.01, -0.05, -0.001)), "loss")
        self.assertEqual(script.verdict(row(-0.05, -0.01, -0.05, 0.001)), "undecided")
        self.assertEqual(script.verdict(None), "undecided")
        self.assertEqual(script.verdict({"undefined": "x"}), "undecided")

    def test_a_cell_shows_the_skill_interval_and_the_mean_d_bound(self):
        text = script._fmt(row(0.01, 0.05, 0.001, 0.05))
        self.assertIn("[+1.0%, +5.0%]", text)
        self.assertIn("d +0.010 [+0.001, +0.050]", text)

    def test_the_pair_plan_names_b1_prime_beside_b1_and_the_arm_each_differs_from(self):
        for arm in (script.R1, script.R2, script.R3, script.V4, script.S1):
            plan = script.pair_plan(arm, ("gbm_funding",))
            for name in ("B1", "B1_prime", "B2", sc.ARM_A, script.S3, "gbm_funding"):
                self.assertIn(name, plan, (arm, name))
        for arm in (script.R1, script.R2):
            self.assertIn(script.S1, script.pair_plan(arm, ()))
        self.assertNotIn(script.S3, script.pair_plan(script.S3, ()))
        self.assertIn(script.S1, script.pair_plan(script.S3, ()))
        self.assertNotIn(sc.ARM_A, script.pair_plan(sc.ARM_A, ()))
        self.assertNotIn("gbm_funding", script.pair_plan(script.R3, ()))

    def test_the_politis_white_block_is_against_a_and_against_s3_for_the_arms_off_the_corners(self):
        self.assertEqual(script.block_plan(sc.ARM_A), [])
        self.assertEqual(script.block_plan(script.S3), [sc.ARM_A])
        self.assertEqual(script.block_plan(script.S1), [sc.ARM_A])
        for arm in (script.R1, script.R2, script.R3, script.V4):
            self.assertEqual(script.block_plan(arm), [sc.ARM_A, script.S3])


class KillRuleTests(unittest.TestCase):

    def pooled(self, a, s3, r1, r2, r3=1.5, v4=1.5):
        means = {sc.ARM_A: a, script.S3: s3, script.R1: r1, script.R2: r2, script.R3: r3, script.V4: v4}
        return {m: {"means": means} for m in script.METRIC_NAMES}

    def test_the_share_recovered_is_the_gain_of_the_arm_over_the_gain_of_s3(self):
        out = script.recovery(self.pooled(2.0, 1.6, 1.9, 1.7))
        grid = out["metrics"]["grid_crps"]
        self.assertAlmostEqual(grid["gain_of_s3"], 0.4)
        self.assertAlmostEqual(grid[script.R1], 0.25)
        self.assertAlmostEqual(grid[script.R2], 0.75)

    def test_the_kill_is_met_only_when_both_recover_less_than_half(self):
        self.assertTrue(script.recovery(self.pooled(2.0, 1.6, 1.9, 1.85))["met"])
        self.assertFalse(script.recovery(self.pooled(2.0, 1.6, 1.9, 1.7))["met"])
        self.assertFalse(script.recovery(self.pooled(2.0, 1.6, 1.7, 1.7))["met"])
        self.assertFalse(script.recovery(self.pooled(2.0, 1.6, 1.8, 1.8))["met"])  # exactly half is not less than half

    def test_with_no_gain_of_s3_the_share_is_undefined_and_the_kill_is_not_met(self):
        out = script.recovery(self.pooled(1.6, 2.0, 1.9, 1.85))
        self.assertIsNone(out["metrics"]["grid_crps"][script.R1])
        self.assertFalse(out["met"])


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_the_arms_the_modules_have(self):
        declaration = json.loads(script.DECLARATION.read_text(encoding="utf-8"))
        self.assertEqual(script.committed_declaration()["issue"], 1172)
        self.assertEqual([a["name"] for a in declaration["arms"]], [sc.ARM_A] + [a.name for a in sc.DECOMPOSITION] + [script.V4])
        for entry in declaration["arms"][1:-1]:
            arm = sc.ALL_ARMS[entry["name"]]
            self.assertEqual(entry["location_terms"], list(arm.location), arm.name)
            self.assertEqual((entry["ridge"], entry["robust"], entry["sized"]), (sc.ridge_of(arm), arm.robust, arm.sized), arm.name)
        self.assertEqual(declaration["arms"][-1]["location_terms"], list(sc.ARMS[2].location))
        self.assertEqual(declaration["limits"]["arms"], len(declaration["arms"]) - 1)  # (a) is the comparator
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(declaration["scoring"]["paired"].count("seed 1172"), 1)
        self.assertEqual(script.SEED, 1172)
        self.assertEqual(declaration["kill_rule"]["reading"].count("< 0.5"), 2)
        self.assertEqual(script.KILL_SHARE, 0.5)

    def test_no_arm_has_the_fomc_or_iorb_terms(self):
        for arm in sc.DECOMPOSITION:
            self.assertFalse({"fomc_day", "iorb_window"} & set(arm.location), arm.name)
            self.assertEqual(arm.location, cal.NO_FOMC_IORB)


class EndToEndTests(unittest.TestCase):
    """`score` and `page` on the last months of the fixture panel, with few resamples: the shape, not the figures."""

    FIRST = "2025-06-02"

    @classmethod
    def setUpClass(cls):
        sys.modules["s3_decomposition_1172"] = script  # another test module may have re-registered the name (pickling by module name)
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

    def test_every_arm_is_scored_against_the_references_and_the_arm_it_isolates(self):
        cell = self.result["groups"]["pooled"]["all decision days"]["grid_crps"]
        self.assertEqual(sorted(cell["vs"]), sorted(script.ARMS))
        for arm in script.ARMS:
            for name in ("B1", "B1_prime", "B2", "gbm_funding"):
                self.assertIn(name, cell["vs"][arm], (arm, name))
        for arm in script.ARMS:
            if arm != sc.ARM_A:
                self.assertIn(sc.ARM_A, cell["vs"][arm], arm)
            if arm not in (sc.ARM_A, script.S3):
                self.assertIn(script.S3, cell["vs"][arm], arm)
        for arm in (script.R1, script.R2, script.S3):
            self.assertIn(script.S1, cell["vs"][arm])
        self.assertEqual(sorted(cell["means"]), sorted(script.MODELS + script.GBMS))

    def test_the_rows_carry_the_mean_d_interval_beside_the_skill_interval(self):
        cell = self.result["groups"]["pooled"]["all decision days"]["grid_crps"]
        one = cell["vs"][script.R1][sc.ARM_A]
        self.assertIn("skill_interval", one)
        self.assertIn("difference_interval", one)

    def test_without_walks_the_gbm_rows_are_absent_and_the_page_says_so(self):
        cell = self.without["groups"]["pooled"]["all decision days"]["grid_crps"]
        self.assertNotIn("gbm_funding", cell["vs"][script.S3])
        self.assertEqual(self.without["gbm"], [])
        text = self.bare_page.read_text(encoding="utf-8")
        self.assertIn("were not supplied", text)
        self.assertIn("stays on Eleonora's Mac", text)

    def test_the_splits_the_directive_names_are_all_there(self):
        groups = self.result["groups"]
        self.assertIn("pooled", groups)
        self.assertEqual(sorted(groups["lead"]), [f"h={h}" for h in sp.HORIZONS])
        self.assertIn("2025-26", groups["regime"])
        for label in ("dom_19_23", "ordinary", "calendar_days"):
            self.assertIn(label, groups["target_day_type"])

    def test_the_scaled_score_is_beside_the_raw_one_pooled_and_by_regime(self):
        pooled = self.result["groups"]["scaled"]["all decision days"][script.SCALED]
        self.assertEqual(sorted(pooled["vs"]), sorted(script.ARMS))
        self.assertIn("2025-26", self.result["groups"]["scaled"])
        self.assertIn("The scaled score beside the raw one", self.page.read_text(encoding="utf-8"))

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
        self.assertEqual(sorted(pooled[script.R3]), sorted([sc.ARM_A, script.S3]))
        self.assertEqual(sorted(pooled[script.S3]), [sc.ARM_A])
        self.assertIn("at_block", pooled[script.R3][sc.ARM_A])

    def test_the_effect_of_each_term_is_in_bp_and_in_scale_units_by_regime(self):
        effects = self.result["term_effect_intervals"]
        self.assertEqual(sorted(effects), sorted(a.name for a in sc.DECOMPOSITION))
        some = effects[script.S3]["month_end"]["2025-26"]
        for quantity in ("bp", "std", "miss"):
            self.assertIn(quantity, some)
        sized = effects[script.R3].get("settlement_coupon", {})
        for cell in sized.values():
            self.assertIn("bp", cell)

    def test_the_kill_rule_is_computed_and_the_page_states_it(self):
        recovery = self.result["recovery"]
        self.assertIn("met", recovery)
        self.assertEqual(sorted(recovery["metrics"]), list(script.METRIC_NAMES))
        text = self.page.read_text(encoding="utf-8")
        self.assertIn("## The kill rule", text)
        self.assertIn("Lens C", text)
        self.assertIn("mean d", text)

    def test_v4_is_scored_on_the_days_every_model_has_and_its_factors_are_recorded(self):
        self.assertTrue(self.result["v4_fits"])
        self.assertEqual(self.result["notes"]["v4_skipped"], [])
        self.assertIn("## (v4) on (s3): what the factors were", self.page.read_text(encoding="utf-8"))

    def test_no_day_after_the_last_scored_day_is_read(self):
        self.assertLessEqual(self.result["notes"]["last_target"], script.LAST_DAY.isoformat())
        self.assertEqual(self.result["subset_from"], self.FIRST)

    def test_the_page_ends_with_the_marked_question_its_options_and_a_default(self):
        text = self.page.read_text(encoding="utf-8")
        self.assertIn("B1' (#960)", text)
        tail = text[text.index("## Question for Eleonora"):]
        self.assertIn("Nothing is adopted here and no claim changes", tail)
        for option in ("1. **Keep (s3)", "2. **Replace (s3)", "3. **Ask for a further step"):
            self.assertIn(option, tail)
        self.assertIn("(default)", tail)
        self.assertEqual(text.count("## Question for Eleonora"), 1)
        self.assertTrue(tail.rstrip().splitlines()[-1].startswith("3."))
        self.assertIn("development data, not a verdict", text.lower())


if __name__ == "__main__":
    unittest.main()
