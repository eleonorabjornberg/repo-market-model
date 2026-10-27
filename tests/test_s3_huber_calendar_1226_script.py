"""The helpers of `scripts/s3_huber_calendar_1226.py` (#1226; H5 step 3 fix, development tier).

Written first, against the declaration. It adds no reader of its own: the scored days pass `spread_mean_reversion_686.require_scored_days`
(its recorded mutation is in `test_spread_mean_reversion_686_script`), the calendar-row guard is recorded in
`test_spread_mr_s3_huber_calendar`, and the arms' settings are pinned there. What these tests pin: that the declaration names the arms
the module has and their settings; that a reading is taken from the mean-d bound and the skill interval's reading is kept beside it;
the pair plan; that the page says what the ruling requires (a further look after (s3) was chosen, the variant count, Lens C's caveat,
FOMC, IORB-window and quarter-end days named, the ordinary-day reading beside every calendar-day row, the day-type method labelled, a
marked question with a default); and a small run of `score` and `page` end to end on a late subset of the fixture panel, with and
without synthetic walks of `gbm_funding`.
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
_spec = importlib.util.spec_from_file_location("s3_huber_calendar_1226", ROOT / "scripts" / "s3_huber_calendar_1226.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["s3_huber_calendar_1226"] = script  # the script's worker pool pickles its functions by module name
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

    def test_a_row_without_a_mean_d_bound_has_no_reading_not_undecided(self):
        """#1215. Mutation (recorded): returning "undecided" for an undefined row in `verdict` made this fail with
        AssertionError ('undecided' != '**no reading** ...') and the tally test below fail on the count of `no reading`."""

        undefined = {"undefined": "the daily difference has no long-run variance; it cannot be studentized", "days": 20}
        words = "**no reading** (mean-d bound not computed: the daily difference has no long-run variance; it cannot be studentized)"
        self.assertEqual(script.verdict(undefined), words)
        self.assertEqual(script.reading_words(undefined), words)
        self.assertEqual(script._bold(script.reading_words(undefined)), words)
        self.assertEqual(script._bold("gain"), "**gain**")
        self.assertEqual(script.verdict(None), "undecided")

    def test_a_mean_d_only_row_reads_on_the_bound_and_says_skill_is_undefined(self):
        only = {"skill": None, "skill_interval": None, "skill_undefined": "x", "difference": 0.01, "difference_interval": [0.001, 0.05]}
        self.assertEqual(script.verdict(only), "gain")
        self.assertEqual(script.skill_verdict(only), "skill undefined")
        self.assertEqual(script.reading_words(only), "gain (skill interval: skill undefined)")
        self.assertIn("skill undefined", script._fmt(only))

    def test_the_regime_tally_keeps_no_reading_apart_from_undecided(self):
        undefined = {"undefined": "x", "days": 5}
        regimes = list(script.REGIMES)
        groups = {"regime": {regimes[0]: {"grid_crps": {"vs": {"arm": {"ref": undefined}}}},
                             regimes[1]: {"grid_crps": {"vs": {"arm": {"ref": row(-1, 1, -0.1, 0.1)}}}}}}
        count = script.tally({"groups": groups}, "arm", "ref")
        self.assertEqual((count["no reading"], count["undecided"], count["gain"], count["loss"]), (1, 1, 0, 0))

    def test_a_cell_shows_the_skill_interval_and_the_mean_d_bound(self):
        text = script._fmt(row(0.01, 0.05, 0.001, 0.05))
        self.assertIn("[+1.0%, +5.0%]", text)
        self.assertIn("d +0.010 [+0.001, +0.050]", text)

    def test_the_pair_plan_names_b1_prime_beside_b1_and_s3_for_the_two_arms(self):
        for arm in (script.H1, script.H2):
            plan = script.pair_plan(arm, ("gbm_funding",))
            for name in ("B1", "B1_prime", "B2", sc.ARM_A, script.S3, "gbm_funding"):
                self.assertIn(name, plan, (arm, name))
        self.assertNotIn(script.S3, script.pair_plan(script.S3, ()))
        self.assertIn(sc.ARM_A, script.pair_plan(script.S3, ()))
        self.assertNotIn(sc.ARM_A, script.pair_plan(sc.ARM_A, ()))
        self.assertNotIn("gbm_funding", script.pair_plan(script.H1, ()))

    def test_the_politis_white_block_is_against_a_and_against_s3_for_the_two_arms(self):
        self.assertEqual(script.block_plan(sc.ARM_A), [])
        self.assertEqual(script.block_plan(script.S3), [sc.ARM_A])
        for arm in (script.H1, script.H2):
            self.assertEqual(script.block_plan(arm), [sc.ARM_A, script.S3])


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_the_arms_the_module_has(self):
        declaration = json.loads(script.DECLARATION.read_text(encoding="utf-8"))
        self.assertEqual(script.committed_declaration()["issue"], 1226)
        self.assertEqual([a["name"] for a in declaration["arms"]], [sc.ARM_A] + [a.name for a in sc.HW_ARMS])
        for entry in declaration["arms"][1:]:
            arm = sc.ALL_ARMS[entry["name"]]
            self.assertEqual(entry["location_terms"], list(arm.location), arm.name)
            self.assertEqual((entry["ridge"], entry["robust"], entry["interact"]), (sc.ridge_of(arm), arm.robust, arm.interact), arm.name)
        self.assertEqual(declaration["limits"]["arms"], len(declaration["arms"]) - 2)  # (a) and (s3) are the comparators
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(declaration["scoring"]["paired"].count("seed 1226"), 1)
        self.assertEqual(script.SEED, 1226)
        by_name = {a["name"]: a for a in declaration["arms"]}
        self.assertEqual(by_name[sc.HW1.name]["calendar_k"], "full weight")
        self.assertEqual(by_name[sc.HW2.name]["calendar_k"], sc.CALENDAR_K)
        self.assertEqual(declaration["amendments"], [])

    def test_both_arms_are_s3_with_the_calendar_threshold_and_nothing_else(self):
        s3 = sc.ARMS[2]
        for arm in (sc.HW1, sc.HW2):
            self.assertTrue(arm.robust)
            self.assertEqual((sc.ridge_of(arm), arm.interact, arm.location, arm.sized), (5.0, False, s3.location, False))
        self.assertEqual((sc.HW1.calendar_k, sc.HW2.calendar_k), (sc.FULL_WEIGHT, sc.CALENDAR_K))

    def test_the_named_splits_are_the_2020_regime_and_the_fomc_iorb_window_and_quarter_end_days(self):
        self.assertEqual(script.AIMED, (("regime", "2020"), ("target_day_type", "fomc_day"), ("target_day_type", "iorb_window"),
                                        ("target_day_type", "quarter_end")))
        for label in script.CALENDAR_TYPES:
            self.assertTrue(label in script.DAY_TYPES or label == "calendar_days", label)


class CommittedRecordTests(unittest.TestCase):
    """The tracked record of the declared run, and the page generated from it."""

    RECORD = ROOT / "docs" / "research" / "s3-huber-calendar-1226" / "result.json"
    PAGE = ROOT / "docs" / "research" / "s3-huber-calendar-1226-result.md"

    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"), script.render(record))

    def test_the_record_is_the_declared_full_run_not_a_subset(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8"))
        self.assertIsNone(record["subset_from"])
        self.assertEqual((record["seed"], record["draws"]), (script.SEED, sp.DRAWS))
        self.assertEqual(record["declaration"], "metadata/s3_huber_calendar_1226.json")
        self.assertEqual(record["models"], list(script.MODELS))
        self.assertLessEqual(record["notes"]["last_target"], script.LAST_DAY.isoformat())
        self.assertEqual(record["gbm"], [])
        self.assertIn(record["panel_sha256"], json.dumps(manifest))


class EndToEndTests(unittest.TestCase):
    """`score` and `page` on the last months of the fixture panel, with few resamples: the shape, not the figures."""

    FIRST = "2025-06-02"

    @classmethod
    def setUpClass(cls):
        sys.modules["s3_huber_calendar_1226"] = script  # another test module may have re-registered the name (pickling by module name)
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
        for arm in (script.H1, script.H2):
            self.assertIn(script.S3, cell["vs"][arm], arm)
        self.assertEqual(sorted(cell["means"]), sorted(script.MODELS + script.GBMS))

    def test_the_rows_carry_the_mean_d_interval_beside_the_skill_interval(self):
        cell = self.result["groups"]["pooled"]["all decision days"]["grid_crps"]
        one = cell["vs"][script.H1][script.S3]
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
        # declared run has 118 and 78 of them (metadata/s3_huber_calendar_1226.json)
        for label in ("fomc_day", "iorb_window"):
            self.assertIn(label, script.DAY_TYPES)
            self.assertTrue(label in groups["target_day_type"] or f"target_day_type/{label}" in self.result["skipped_groups"], label)
        self.assertIn("fomc_day", self.result["q95_by_day_type"])
        self.assertIn("iorb_window", self.result["q95_by_day_type"])

    def test_the_scaled_score_is_not_scored_and_the_page_says_why(self):
        self.assertNotIn("scaled", self.result["groups"])
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
        self.assertEqual(sorted(pooled[script.H1]), sorted([sc.ARM_A, script.S3]))
        self.assertEqual(sorted(pooled[script.S3]), [sc.ARM_A])
        self.assertIn("at_block", pooled[script.H2][sc.ARM_A])

    def test_the_effect_of_each_term_is_in_bp_and_in_scale_units_by_regime_and_the_calendar_arm_has_fomc(self):
        effects = self.result["term_effect_intervals"]
        self.assertEqual(sorted(effects), sorted(a.name for a in sc.HW_ARMS))
        for quantity in ("bp", "std", "miss"):
            self.assertIn(quantity, effects[script.S3]["month_end"]["2025-26"])
        self.assertIn("fomc_day", self.result["term_effects"][script.H2])
        self.assertNotIn("state_slopes", self.result)

    def test_no_arm_has_a_term_the_screen_does_not_declare(self):
        counts = self.result["refit_term_counts"]
        for arm in (script.S3, script.H1, script.H2):
            for term in ("fomc_day", "iorb_window"):
                self.assertEqual(counts[arm][term], [0] * len(sp.HORIZONS), (arm, term))

    def test_the_calendar_share_is_recorded_for_the_two_arms_only(self):
        shares = self.result["calendar_pairs"]
        self.assertEqual(sorted(shares), sorted([script.H1, script.H2]))
        for entry in shares.values():
            self.assertTrue(0.0 < entry["mean_share"] < 1.0)
        self.assertEqual(shares[script.H1]["mean_share"], shares[script.H2]["mean_share"])

    def test_the_aimed_rows_are_the_2020_regime_and_the_fomc_days_for_s3_and_the_two_arms(self):
        rows = script.aimed_rows(self.result)
        for r in rows:
            self.assertIn((r["split"], r["group"]), script.AIMED)
            self.assertIn(r["arm"], (script.S3, script.H1, script.H2))
        self.assertEqual(len(rows), 3 * len([1 for s, l in script.AIMED if l in self.result["groups"].get(s, {})]))

    def test_every_calendar_day_row_has_the_ordinary_day_reading_beside_it(self):
        text = self.page.read_text(encoding="utf-8")
        section = text[text.index("## Calendar-day types beside ordinary days"):]
        section = section[:section.index("\n## ", 5)]
        self.assertIn("same, ordinary days", section)
        rows = [line for line in section.splitlines() if line.startswith("| ") and not line.startswith("| target-day") and "---" not in line]
        self.assertTrue(rows)
        for line in rows:
            self.assertEqual(line.count("|"), 10, line)  # nine cells; the ordinary-day cells are filled for every row that has a reading
        arms = {sc.ALL_ARMS[a].role if a != script.S3 else script.LABELS[script.S3] for a in (script.S3, script.H1, script.H2)}
        self.assertTrue(all(any(a in line for a in arms) for line in rows))

    def test_the_page_states_what_the_ruling_requires(self):
        text = self.page.read_text(encoding="utf-8")
        for needle in ("further look at 2018-2025 after (s3) was chosen", "#1187", "Lens C", "mean d", "B1' (#960)",
                       "Politis-White", "fomc_day", "iorb_window", "quarter_end", "## Aimed at (s3)'s upper-tail losses",
                       "variant count", "#1221", "current method", "without an ordinary-day loss", "Development data, not a verdict".lower()):
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
