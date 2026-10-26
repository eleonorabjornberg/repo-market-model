"""`scripts/s3_2026_check_1222.py` (#1229; H5 step 3, avenue #1222): (s3) on the 2026 development days, with #845's table.

Written first, against the declaration. The model is (s3) of #1145 and (a) of #941, unchanged; the lockbox is checked by
`spread_mean_reversion_686.require_scored_days` (its recorded mutation is in `test_spread_mean_reversion_686_script`). What these tests
pin: that the declaration names what the module has; that the scored span is the 2026 development days (the guard this study adds
refuses a decision day with a target before 2026-01-02 and one with a target after 2026-09-03); #845's decomposition on hand cases and
the minimum of three pressure days; the pair plan, the coverage blocks and the groups; that the page says what the ruling requires
(a check, not evidence for a verdict or a choice; the current method for the day-type intervals, #1221 open; the provisional mark); and
a small run of `score` and `page` end to end, with the walk started late, on the fixture panel.
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
from repo_model import spread_mr_state_calendar as sc
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("s3_2026_check_1222", ROOT / "scripts" / "s3_2026_check_1222.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["s3_2026_check_1222"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)


def law(centre: float, spread: float = 0.5):
    """A 23-quantile law that rises from centre - spread * 11 to centre + spread * 11."""

    return [centre + spread * (i - 11) for i in range(len(sp.GRID))]


def row_(day, outcome, centre_a, centre_s):
    q = {script.A: law(centre_a), script.S3: law(centre_s)}
    return {"day": day, "outcome": outcome, "event": outcome > 5.0,
            "p": {name: script.smr.exceedance(values, script.TAU) for name, values in q.items()}, "q": q}


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_what_the_module_has(self):
        declaration = script.committed_declaration()
        self.assertEqual((declaration["issue"], declaration["avenue"]), (1229, 1222))
        self.assertEqual(declaration["scored_days"]["last_target_day"], script.LAST_DAY.isoformat())
        self.assertEqual(declaration["scored_days"]["first_target_day"], script.FIRST_TARGET.isoformat())
        self.assertEqual(script.LAST_DAY, date(2026, 9, 3))
        self.assertEqual(script.FIRST_TARGET, date(2026, 1, 2))
        self.assertEqual(script.TABLE_FIRST.isoformat(), "2025-12-12")
        self.assertEqual(declaration["limits"]["arms"], 0)
        # One amendment, made at review: the `arms` block the declarations test reads. It adds no arm and no number.
        self.assertEqual(len(declaration["amendments"]), 1)
        self.assertIn("`arms` block", declaration["amendments"][0]["added"])
        self.assertEqual(len(declaration["arms"]), 5)
        self.assertIn(script.S3, [a["name"] for a in declaration["arms"]])
        self.assertIn("seed 1222", declaration["report"]["3_scores"]["paired"])
        self.assertEqual(script.SEED, 1222)
        self.assertEqual(declaration["report"]["1_calibration_in_the_large"]["minimum"].count("3 pressure days"), 1)

    def test_the_model_is_s3_of_1145_and_the_comparator_is_a(self):
        self.assertEqual(script.S3, "sc_s3_robust")
        self.assertEqual(script.A, sc.ARM_A)
        arm = sc.ARMS[2]
        self.assertEqual((arm.robust, arm.interact, sc.ridge_of(arm)), (True, False, 5.0))
        self.assertEqual(script.ARMS, (script.A, script.S3))
        self.assertEqual(script.BENCHMARKS, ("B1", "B1_prime", "B2"))

    def test_the_two_windows_of_the_table_are_the_stretch_of_845_and_the_scored_days(self):
        names = [w[0] for w in script.WINDOWS]
        self.assertEqual(names, ["after_purchases_2025_26", "scored_days_2026"])
        stretch = json.loads((ROOT / "metadata" / "exploration_845.json").read_text(encoding="utf-8"))["stretches"]["after_purchases_2025_26"]
        self.assertEqual(script.WINDOWS[0][1].isoformat(), stretch["first_target_day"])
        self.assertEqual(script.WINDOWS[0][2].isoformat(), stretch["last_target_day"])
        self.assertEqual(script.WINDOWS[1][1], script.FIRST_TARGET)


class SpanTests(unittest.TestCase):

    def test_a_decision_day_with_a_target_before_2026_is_refused(self):
        """Mutation (recorded): replacing `if first < FIRST_TARGET:` with `if first < FIRST_TARGET - timedelta(days=30):` made this fail
        with AssertionError (LookAheadError not raised); restored, it passes."""

        ok = {date(2025, 12, 31): date(2026, 1, 2)}
        script.require_span(ok, {date(2025, 12, 31): date(2026, 1, 8)})
        with self.assertRaises(LookAheadError):
            script.require_span({date(2025, 12, 30): date(2025, 12, 31)}, {date(2025, 12, 30): date(2026, 1, 7)})

    def test_a_decision_day_with_a_target_after_the_last_day_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.require_span({date(2026, 9, 3): date(2026, 9, 4)}, {date(2026, 9, 3): date(2026, 9, 10)})
        script.require_span({date(2026, 8, 27): date(2026, 8, 28)}, {date(2026, 8, 27): date(2026, 9, 3)})

    def test_the_lockbox_still_refuses_a_day_after_the_last_day(self):
        with self.assertRaises(LookAheadError):
            script.s686.require_scored_days([date(2026, 9, 4)], script.LAST_DAY)


class TableTests(unittest.TestCase):
    """#845's decomposition on hand cases, and the minimum of three pressure days."""

    def test_the_error_is_the_level_part_plus_the_residual_pool_part(self):
        rows = [row_(date(2026, 1, 5 + i), 0.5 + 0.1 * i, 0.0, 0.0) for i in range(10)] + [row_(date(2026, 2, 2), 8.0, 0.0, 0.5)]
        cell = script.large_cell(rows, draws=50)
        self.assertEqual((cell["cells"], cell["pressure_days"]), (11, 1))
        self.assertAlmostEqual(cell["realised"], 1 / 11)
        for name in script.ARMS:
            e = cell["models"][name]
            self.assertAlmostEqual(e["error"], e["level"] + e["pool"], places=12)
            self.assertAlmostEqual(e["error"], e["mean_p"] - cell["realised"], places=12)
            self.assertLessEqual(e["error_interval"][0], e["error_interval"][1])

    def test_a_cell_under_the_minimum_keeps_its_counts_only(self):
        rows = [row_(date(2026, 1, 5 + i), 1.0, 0.0, 0.0) for i in range(6)] + [row_(date(2026, 2, 2), 8.0, 0.0, 0.0), row_(date(2026, 2, 3), 9.0, 0.0, 0.0)]
        cell = script.large_cell(rows, draws=20)
        self.assertEqual(cell["pressure_days"], 2)
        self.assertTrue(script.d845.under_minimum(cell["pressure_days"]))
        kept = script.d845.tracked_cell(cell, withheld=True)
        self.assertEqual(kept, {"cells": 8, "pressure_days": 2, "withheld": True})
        three = script.large_cell(rows + [row_(date(2026, 2, 4), 7.0, 0.0, 0.0)], draws=20)
        self.assertFalse(script.d845.under_minimum(three["pressure_days"]))

    def test_the_event_is_a_whole_basis_point_strictly_above_5(self):
        self.assertFalse(script.exceeds_bp(5.0, script.TAU))
        self.assertTrue(script.exceeds_bp(6.0, script.TAU))
        self.assertEqual(script.TAU, 5.0)

    def test_an_empty_cell_has_no_figures(self):
        self.assertEqual(script.large_cell([], draws=10), {"cells": 0, "pressure_days": 0})


class PlanTests(unittest.TestCase):

    def test_the_pair_plan_names_b1_prime_beside_b1_and_a_for_s3_only(self):
        self.assertEqual(script.pair_plan(script.A), ["B1", "B1_prime", "B2"])
        self.assertEqual(script.pair_plan(script.S3), ["B1", "B1_prime", "B2", script.A])

    def test_the_coverage_blocks_are_ten_for_one_lead_and_fifty_for_several(self):
        self.assertEqual(script.block_of("h=3"), 10.0)
        self.assertEqual(script.block_of("pooled"), 50.0)
        self.assertEqual(script.block_of("2026-03"), 50.0)

    def test_the_month_is_the_calendar_month(self):
        self.assertEqual(script.month_of(date(2026, 3, 31)), "2026-03")


class CommittedRecordTests(unittest.TestCase):
    """The tracked record of the declared run, and the page generated from it."""

    RECORD = ROOT / "docs" / "research" / "s3-2026-check-1222" / "result.json"
    PAGE = ROOT / "docs" / "research" / "s3-2026-check-1222-result.md"

    def test_the_tracked_page_is_what_the_script_renders_from_the_tracked_record(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        self.assertEqual(self.PAGE.read_text(encoding="utf-8"), script.render(record))

    def test_the_record_is_the_declared_full_run_on_the_published_panel(self):
        record = json.loads(self.RECORD.read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8"))
        self.assertIsNone(record["subset_from"])
        self.assertEqual((record["seed"], record["draws"]), (script.SEED, sp.DRAWS))
        self.assertEqual(record["declaration"], "metadata/s3_2026_check_1222.json")
        self.assertEqual(record["models"], list(script.MODELS))
        self.assertGreaterEqual(record["notes"]["first_target"], script.FIRST_TARGET.isoformat())
        self.assertLessEqual(record["notes"]["last_target"], script.LAST_DAY.isoformat())
        self.assertIn(record["panel_sha256"], json.dumps(manifest))

    def test_the_page_says_what_the_ruling_requires(self):
        text = self.PAGE.read_text(encoding="utf-8")
        for phrase in ("already seen by #845 and by the #151 final test", "a check, not evidence for a verdict or a choice",
                       "carry the provisional", "current method", "#1221", "Lens C", "mean-d bound", "Panel digest"):
            self.assertIn(phrase, text)
        self.assertNotIn("GO #", text)


class EndToEndTests(unittest.TestCase):
    """`score` and `page` with the walk started late on the fixture panel, with few resamples: the shape, not the figures."""

    FIRST = "2025-06-02"

    @classmethod
    def setUpClass(cls):
        sys.modules["s3_2026_check_1222"] = script  # another test module may have re-registered the name (pickling by module name)
        import panel_cache

        cls.panel_path = Path(panel_cache.published_build()["path"])
        cls.tmp = tempfile.TemporaryDirectory()
        base = Path(cls.tmp.name)
        cls.output, cls.page, cls.withheld = base / "result.json", base / "page.md", base / "withheld.json"
        script.main(["score", "--panel", str(cls.panel_path), "--output", str(cls.output), "--withheld", str(cls.withheld),
                     "--draws", "20", "--reps", "5", "--workers", "2", "--first", cls.FIRST])
        script.main(["page", "--score", str(cls.output), "--output", str(cls.page)])
        cls.result = json.loads(cls.output.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_only_the_2026_development_days_are_scored(self):
        n = self.result["notes"]
        self.assertGreaterEqual(n["first_target"], "2026-01-02")
        self.assertLessEqual(n["last_target"], "2026-09-03")
        self.assertEqual(n["first"], "2025-12-31")

    def test_every_model_is_scored_and_s3_is_tested_against_a_and_the_benchmarks(self):
        cell = self.result["groups"]["pooled"]["all decision days"]["grid_crps"]
        self.assertEqual(sorted(cell["means"]), sorted(script.MODELS))
        self.assertEqual(sorted(cell["vs"][script.S3]), sorted(["B1", "B1_prime", "B2", script.A]))
        self.assertEqual(sorted(cell["vs"][script.A]), sorted(["B1", "B1_prime", "B2"]))
        one = cell["vs"][script.S3]["B1"]
        self.assertIn("skill_interval", one)
        self.assertIn("difference_interval", one)

    def test_the_groups_are_pooled_lead_month_and_day_type_with_no_regime(self):
        groups = self.result["groups"]
        self.assertEqual(sorted(groups["lead"]), [f"h={h}" for h in sp.HORIZONS])
        self.assertNotIn("regime", groups)
        self.assertIn("month", groups)
        self.assertIn("2026-03", groups["month"])
        for label in ("ordinary", "calendar_days"):
            self.assertIn(label, groups["target_day_type"])

    def test_the_table_of_845_has_both_windows_and_every_lead(self):
        large = self.result["calibration_in_the_large"]
        self.assertEqual(sorted(large), ["after_purchases_2025_26", "scored_days_2026"])
        for body in large.values():
            self.assertEqual(sorted(body["leads"]), [str(h) for h in sp.HORIZONS])
        wide, narrow = (large[w]["leads"]["1"] for w in ("after_purchases_2025_26", "scored_days_2026"))
        self.assertGreaterEqual(wide["cells"], narrow["cells"])

    def test_a_cell_under_the_minimum_is_counts_only_and_its_figures_are_in_the_withheld_file_alone(self):
        withheld = json.loads(self.withheld.read_text(encoding="utf-8"))["withheld_cells"]
        for window, body in self.result["calibration_in_the_large"].items():
            for h, cell in body["leads"].items():
                if cell["pressure_days"] < script.d845.MINIMUM_PRESSURE_DAYS:
                    self.assertEqual(sorted(cell), ["cells", "pressure_days", "withheld"], (window, h))
                    if cell["cells"]:
                        self.assertIn("models", withheld[window][h])
                else:
                    self.assertIn("models", cell)

    def test_the_coverage_is_pooled_by_lead_and_by_month_for_every_model_under_both_band_rules(self):
        cover = self.result["coverage"]
        for group in ["pooled"] + [f"h={h}" for h in sp.HORIZONS] + list(self.result["month_counts"]):
            self.assertIn(group, cover)
        for model in script.MODELS:
            for rule in script.RATES:
                e = cover["pooled"][model][rule]
                self.assertTrue(0.0 <= e["rate"] <= 1.0)
                self.assertLessEqual(e["interval"][0], e["interval"][1])

    def test_the_page_says_what_it_is(self):
        text = self.page.read_text(encoding="utf-8")
        self.assertIn("a check, not evidence for a verdict or a choice", text)
        self.assertIn("1. Calibration in the large", text)
        self.assertIn("2. Coverage of the central bands", text)
        self.assertIn("3. Grid CRPS and upper-tail twCRPS, paired", text)


if __name__ == "__main__":
    unittest.main()
