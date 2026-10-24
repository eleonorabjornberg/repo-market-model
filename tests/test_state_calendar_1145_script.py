"""The helpers of `scripts/state_calendar_1145.py` (#1145; H5 step 3 fix, development tier).

Written first, against the declaration. It adds no reader of its own: the scored days pass
`spread_mean_reversion_686.require_scored_days` (its recorded mutation is in `test_spread_mean_reversion_686_script`), and the
state and term guards are recorded in `test_spread_mr_state_calendar`. What these tests pin: that the declaration names the arms and
terms the module has; that the scarcity state is keyed by the DECISION day (the target-day grid shifted one panel day), which is the
one place this script could read it one row off; the reading rule; the pair plan; and a small run of `score` and `page` end to end on
a late subset of the fixture panel, with and without synthetic walks of `gbm_funding`.

Recorded mutation (applied to the tree, the named test run, and reverted):

* #1194, `verdict`: `row["difference_interval"]` replaced with `row["skill_interval"]` made
  `test_a_gain_needs_the_mean_d_bound_above_zero_and_a_loss_below` fail with `AssertionError` ('undecided' != 'gain').
  Red on main before the change: `verdict` was the skill-interval reading and `render` took no `reading` argument.
* `decision_states`: `grid.get(dates[i + 1])` replaced with `grid.get(dates[i])`, so a decision reads the state of the day it is
  made rather than the state it could read (the target-day grid unshifted, the #914 class for the state).
  `test_the_state_is_keyed_by_the_decision_day` and `test_no_state_is_read_beyond_the_last_scored_day` failed with
  `AssertionError` (`None != 2.0` on 2018-05-01: the state of a decision day was the grid's value at the day itself, not at the
  next panel day).
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
_spec = importlib.util.spec_from_file_location("state_calendar_1145", ROOT / "scripts" / "state_calendar_1145.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["state_calendar_1145"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)


class ReadingTests(unittest.TestCase):

    def test_a_gain_needs_the_mean_d_bound_above_zero_and_a_loss_below(self):
        """#1194: the reading is the studentized bound on mean d (her ruling on #1009), not the skill interval."""

        self.assertEqual(script.verdict({"skill_interval": [-0.01, 0.05], "difference_interval": [0.01, 0.05]}), "gain")
        self.assertEqual(script.verdict({"skill_interval": [-0.05, 0.01], "difference_interval": [-0.05, -0.01]}), "loss")
        self.assertEqual(script.verdict({"skill_interval": [0.01, 0.05], "difference_interval": [-0.01, 0.05]}), "undecided")
        self.assertEqual(script.verdict({"skill_interval": [-0.05, -0.01], "difference_interval": [-0.05, 0.01]}), "undecided")
        self.assertEqual(script.verdict({"undefined": "no variance"}), "undecided")
        self.assertEqual(script.verdict(None), "undecided")

    def test_the_skill_reading_is_kept_for_the_first_page(self):
        row = {"skill_interval": [0.01, 0.05], "difference_interval": [-0.01, 0.05]}
        self.assertEqual(script.skill_verdict(row), "gain")
        self.assertEqual(script.skill_verdict({"skill_interval": [-0.05, -0.01], "difference_interval": [-0.05, 0.01]}), "loss")
        self.assertEqual(script.skill_verdict({"skill_interval": [-0.01, 0.05]}), "undecided")
        self.assertEqual(script.skill_verdict(None), "undecided")

    def test_the_committed_first_page_is_what_the_skill_reading_gives_and_the_mean_d_render_says_so(self):
        record = json.loads((ROOT / "docs" / "research" / "state-calendar-1145" / "result.json").read_text(encoding="utf-8"))
        first = (ROOT / "docs" / "research" / "state-calendar-1145-result.md").read_text(encoding="utf-8")
        self.assertEqual(script.render(record, reading="skill"), first)
        page = script.render(record)
        self.assertNotEqual(page, first)
        self.assertIn("studentized bound on mean d", page)
        self.assertIn("understated about 2×", page)

    def test_the_pair_plan_names_b1_prime_beside_b1_and_the_arm_each_differs_from(self):
        for arm in (script.S2, script.S3, script.S4):
            plan = script.pair_plan(arm, ("gbm_funding",))
            for name in ("B1", "B1_prime", "B2", "spread_mr_ctx", sc.ARM_A, script.S1, "gbm_funding"):
                self.assertIn(name, plan, (arm, name))
        self.assertNotIn(script.S1, script.pair_plan(script.S1, ()))
        self.assertNotIn(sc.ARM_A, script.pair_plan(sc.ARM_A, ()))
        self.assertNotIn("gbm_funding", script.pair_plan(script.S2, ()))


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_the_arms_and_terms_the_module_has(self):
        declaration = json.loads(script.DECLARATION.read_text(encoding="utf-8"))
        self.assertEqual(script.committed_declaration()["issue"], 1145)
        self.assertEqual([a["name"] for a in declaration["arms"]], list(sc.ARM_NAMES))
        self.assertEqual([t["name"] for t in declaration["terms"]["listed_in_full"]], list(cal.ALL_TERMS))
        for arm in declaration["arms"][1:]:
            module_arm = next(a for a in sc.ARMS if a.name == arm["name"])
            self.assertEqual(arm["location_terms"], list(module_arm.location))
            self.assertEqual((arm["interact"], arm["robust"]), (module_arm.interact, module_arm.robust))
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(declaration["estimation"]["pairs"][:6], "direct")
        self.assertEqual(declaration["scoring"]["paired"].count("seed 1145"), 1)
        self.assertEqual(script.SEED, 1145)

    def test_the_fomc_and_iorb_terms_are_in_the_separate_arm_only(self):
        for arm in sc.ARMS:
            has = {"fomc_day", "iorb_window"} & set(arm.location)
            self.assertEqual(bool(has), arm.name == script.S4, arm.name)


class StateKeyTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        import tempfile as _t
        from repo_model.scarcity import measurement_declaration, own_leg_states

        cls.states = script.decision_states(script.c.SOURCES)
        with measurement_declaration(), _t.TemporaryDirectory() as tmp:
            build, _digest, registry, decision = script.sv.build_measurement_panel(script.c.SOURCES, Path(tmp))
            cls.grid = {e.day: e.state for e in own_leg_states(
                build.observations, registry=registry, decision_time=decision, minimum_history=script.STATE_MINIMUM_HISTORY,
                horizon=1, end=script.LAST_DAY)}
            cls.dates = [row.date for row in build.observations]

    def test_the_state_is_keyed_by_the_decision_day(self):
        checked = 0
        for i in range(len(self.dates) - 1):
            day, scored = self.dates[i], self.dates[i + 1]
            if scored in self.grid:
                self.assertEqual(self.states[day], self.grid[scored], day)
                checked += 1
        self.assertGreater(checked, 1500)
        self.assertNotEqual(sum(1 for d in self.dates[:-1] if self.states[d] != self.grid.get(d)), 0)  # not the unshifted grid

    def test_no_state_is_read_beyond_the_last_scored_day(self):
        late = [d for d in self.states if d >= script.LAST_DAY]
        self.assertEqual([d for d in late if self.states[d] is not None], [])

    def test_the_states_are_the_four_levels_of_the_declaration(self):
        self.assertEqual({v for v in self.states.values() if v is not None} - {0.0, 1.0, 2.0, 3.0}, set())
        self.assertTrue(any(v is None for v in self.states.values()))  # the first weeks, before the legs allow a read


class EndToEndTests(unittest.TestCase):
    """`score` and `page` on the last months of the fixture panel, with few resamples: the shape, not the figures."""

    FIRST = "2025-06-02"

    @classmethod
    def setUpClass(cls):
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
            laws = {row.date.isoformat(): [1.0 + 0.2 * i for i in range(len(sp.GRID))]
                    for row in panel if date(2025, 5, 1) <= row.date <= date(2025, 12, 31)}
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

    def test_every_arm_is_scored_against_b1_b1_prime_b2_the_context_model_and_gbm_funding(self):
        cell = self.result["groups"]["pooled"]["all decision days"]["grid_crps"]
        self.assertEqual(sorted(cell["vs"]), sorted(sc.ARM_NAMES))
        for arm in sc.ARM_NAMES:
            for name in ("B1", "B1_prime", "B2", "spread_mr_ctx", "gbm_funding"):
                self.assertIn(name, cell["vs"][arm], (arm, name))
        for arm in (script.S2, script.S3, script.S4):
            self.assertIn(script.S1, cell["vs"][arm])
        self.assertEqual(sorted(cell["means"]), sorted(script.MODELS + script.GBMS))

    def test_without_walks_the_gbm_rows_are_absent_and_the_page_says_so(self):
        cell = self.without["groups"]["pooled"]["all decision days"]["grid_crps"]
        self.assertNotIn("gbm_funding", cell["vs"][sc.ARM_A])
        self.assertEqual(self.without["gbm"], [])
        self.assertIn("were not supplied", self.bare_page.read_text(encoding="utf-8"))

    def test_the_splits_the_directive_names_are_all_there(self):
        groups = self.result["groups"]
        self.assertIn("pooled", groups)
        self.assertEqual(sorted(groups["lead"]), [f"h={h}" for h in sp.HORIZONS])
        self.assertIn("2025-26", groups["regime"])
        for label in ("dom_19_23", "ordinary", "calendar_days"):
            self.assertIn(label, groups["target_day_type"])

    def test_the_scaled_score_is_beside_the_raw_one_pooled_and_by_regime(self):
        pooled = self.result["groups"]["scaled"]["all decision days"][script.SCALED]
        self.assertEqual(sorted(pooled["vs"]), sorted(sc.ARM_NAMES))
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
            self.assertLessEqual(entry["b50_open"]["rate"], entry["b50_closed"]["rate"])
            self.assertLessEqual(entry["b90_open"]["rate"], entry["b90_closed"]["rate"])
            self.assertLessEqual(entry["hit_above"]["rate"], entry["hit_at_or_above"]["rate"])

    def test_the_politis_white_block_is_reported_beside_the_protocol_block(self):
        pooled = self.result["politis_white"]["pooled"]["all decision days"]["grid_crps"]
        self.assertEqual(sorted(pooled), sorted(a for a in sc.ARM_NAMES if a != sc.ARM_A))
        self.assertIn("at_block", next(iter(pooled.values())))

    def test_the_effect_of_each_term_is_in_bp_and_in_scale_units_by_regime(self):
        effects = self.result["term_effect_intervals"]
        self.assertEqual(sorted(effects), sorted(a.name for a in sc.ARMS))
        some = effects[script.S2]["month_end"]["2025-26"]
        for quantity in ("bp", "std", "miss"):
            self.assertIn(quantity, some)
        for term in ("fomc_day", "iorb_window"):  # absent from (s1): no effect on the days it flags
            for cell in effects[script.S1].get(term, {}).values():
                self.assertEqual(cell["bp"]["mean"], 0.0)

    def test_no_day_after_the_last_scored_day_is_read(self):
        self.assertLessEqual(self.result["notes"]["last_target"], script.LAST_DAY.isoformat())
        self.assertEqual(self.result["subset_from"], self.FIRST)

    def test_the_page_ends_with_the_marked_question_its_options_and_a_default(self):
        text = self.page.read_text(encoding="utf-8")
        self.assertIn("B1' (#960)", text)
        tail = text[text.index("## Question for Eleonora"):]
        self.assertIn("Nothing is adopted here and no claim changes", tail)
        for option in ("1. **Keep (a)", "2. **Replace (a)", "3. **Ask for a further step"):
            self.assertIn(option, tail)
        self.assertIn("(default)", tail)
        self.assertEqual(text.count("## Question for Eleonora"), 1)
        self.assertTrue(tail.rstrip().splitlines()[-1].startswith("3."))  # the question is the last thing on the page
        self.assertIn("development data, not a verdict", text.lower())


if __name__ == "__main__":
    unittest.main()
