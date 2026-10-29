"""The scoring of (s3) against `gbm_funding` on her Mac walks (#1197; H5 step 3, development tier).

Written first, against the directive. The script adds no reader of the panel of its own: the scored days pass
`spread_mean_reversion_686.require_scored_days` (its recorded mutation is in `test_spread_mean_reversion_686_script`), the walks
pass `calendar_mr_1115.load_gbm` (which refuses a partly present set of leads and a walk made from another panel), and the arms are
those of the committed declaration `metadata/state_calendar_1145.json`. What these tests pin: that the script stops, with its message,
when the walks are not on the machine (it never rebuilds them); that the three models are scored on the same days, which are the days
the walks cover (a comparison on different days is not a paired test); the comparisons the directive names, read on the mean-d bound
beside the skill interval, with Lens C's caveat on the page; and a small run of `score`, `page` and `log` end to end on a late subset
of the fixture panel with synthetic walks (the shape, not the figures).

Recorded mutations (applied to the tree, the named test run, and reverted):

* `common_days`: the body `return [d for d in days if d in walked]` replaced with `return list(days)`, so a comparison would score the
  days the walks do not cover (where `fill_missing` would stand B1 in for `gbm_funding`).
  `test_the_models_are_scored_on_the_days_the_walks_cover` failed with `AssertionError` ("Lists differ": the days outside the walks were in the scored days).
* `require_walks`: the `if not walks.is_dir():` refusal removed (the check fell through to the lead files), so a missing directory
  would be reported as a partial set. `test_a_missing_walks_directory_stops_with_its_message` failed with `AssertionError`
  (`'does not exist' not found in 'STOP: ... lacks gbm_funding_h1.json, ...'`).
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

from repo_model import scoring_protocol as sp

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("s3_vs_gbm_1197", ROOT / "scripts" / "s3_vs_gbm_1197.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["s3_vs_gbm_1197"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)


class GuardTests(unittest.TestCase):
    def test_a_missing_walks_directory_stops_with_its_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "WALKS"
            with self.assertRaises(SystemExit) as caught:
                script.require_walks(missing)
        self.assertIn(str(missing), str(caught.exception))
        self.assertIn("does not exist", str(caught.exception))

    def test_a_partly_present_set_of_leads_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            walks = Path(tmp)
            (walks / "gbm_funding_h1.json").write_text("{}", encoding="utf-8")
            with self.assertRaises(SystemExit) as caught:
                script.require_walks(walks)
        self.assertIn("gbm_funding_h2.json", str(caught.exception))

    def test_a_complete_set_of_leads_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            walks = Path(tmp)
            for h in sp.HORIZONS:
                (walks / f"gbm_funding_h{h}.json").write_text("{}", encoding="utf-8")
            self.assertEqual(script.require_walks(walks), walks)

    def test_the_models_are_scored_on_the_days_the_walks_cover(self):
        days = [date(2025, 6, d) for d in (2, 3, 4, 5, 6)]
        walked = {days[1]: 1, days[3]: 2}
        self.assertEqual(script.common_days(days, walked), [days[1], days[3]])
        self.assertNotIn(days[0], script.common_days(days, walked))

    def test_the_reading_is_the_mean_d_bound_not_the_skill_interval(self):
        row = {"skill": 0.01, "skill_interval": [0.001, 0.02], "difference": 0.01, "difference_interval": [-0.002, 0.02]}
        self.assertEqual(script.reading(row), "undecided")  # the mean-d bound crosses zero
        self.assertEqual(script.skill_reading(row), "gain")
        undefined = {"undefined": "no variance"}
        self.assertTrue(script.reading(undefined).startswith("**no reading**"))  # #1215's words, not "undecided"
        self.assertEqual(script.bold_reading(undefined), script.reading(undefined))  # not bolded twice
        self.assertEqual(script.bold_reading(row), "**undecided**")

    def test_the_comparisons_are_the_ones_the_directive_names(self):
        self.assertEqual(script.HEADLINE, [(script.S3, script.GBM), (script.A, script.GBM), (script.S3, script.A)])
        for candidate in (script.S3, script.A, script.GBM):
            for reference in ("B1", script.B1P):
                self.assertIn((candidate, reference), script.COMPARISONS)


class EndToEndTests(unittest.TestCase):
    """`score`, `page` and `log` on the last months of the fixture panel, with few resamples: the shape, not the figures."""

    FIRST = "2025-06-02"
    WALK_FROM, WALK_TO = date(2025, 7, 1), date(2025, 12, 31)

    @classmethod
    def setUpClass(cls):
        import panel_cache
        from repo_model.baseline import panel_sha256
        from repo_model.data import load_daily_panel

        cls.panel_path = Path(panel_cache.published_build()["path"])
        cls.tmp = tempfile.TemporaryDirectory()
        base = Path(cls.tmp.name)
        cls.walks = base / "walks"
        cls.walks.mkdir()
        sha = panel_sha256(cls.panel_path)
        panel = load_daily_panel(cls.panel_path)
        cls.walked = [row.date for row in panel if cls.WALK_FROM <= row.date <= cls.WALK_TO]
        for h in sp.HORIZONS:
            laws = {day.isoformat(): [1.0 + 0.2 * i for i in range(len(sp.GRID))] for day in cls.walked}
            (cls.walks / f"gbm_funding_h{h}.json").write_text(json.dumps(
                {"variant": "gbm_funding", "horizon": h, "levels": list(sp.GRID), "panel_sha256": sha, "laws": laws}), encoding="utf-8")
        cls.output, cls.page, cls.log = base / "result.json", base / "page.md", base / "2025-12-31-model-01197-H5-step3.md"
        script.main(["score", "--panel", str(cls.panel_path), "--walks", str(cls.walks), "--output", str(cls.output),
                     "--draws", "20", "--reps", "5", "--workers", "2", "--first", cls.FIRST])
        script.main(["page", "--score", str(cls.output), "--output", str(cls.page)])
        script.main(["log", "--score", str(cls.output), "--output", str(cls.log), "--date", "2025-12-31"])
        cls.result = json.loads(cls.output.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_the_scored_days_are_the_days_the_walks_cover(self):
        notes = self.result["notes"]
        self.assertGreater(notes["scored_decision_days"], 0)
        # a walk's laws are keyed by the target day, so a decision day is covered from a few days before the first law
        self.assertGreater(notes["first"], self.FIRST)
        self.assertLessEqual(notes["last_target"], self.WALK_TO.isoformat())
        self.assertGreater(notes["days_without_a_walk"], 0)
        self.assertGreater(notes["decision_days_in_frame"], notes["scored_decision_days"])
        self.assertEqual(self.result["subset_from"], self.FIRST)

    def test_all_three_models_have_a_mean_on_the_same_days(self):
        cell = self.result["groups"]["pooled"]["all decision days"]["grid_crps"]
        self.assertEqual(sorted(cell["means"]), sorted(["B1", script.B1P, script.A, script.S3, script.GBM]))
        for pair in ((script.S3, script.GBM), (script.A, script.GBM), (script.S3, script.A)):
            row = cell["vs"][pair[0]][pair[1]]
            self.assertEqual(row["days"], self.result["notes"]["scored_decision_days"])

    def test_the_comparisons_carry_both_intervals_and_the_splits(self):
        groups = self.result["groups"]
        self.assertIn("pooled", groups)
        self.assertEqual(sorted(groups["lead"]), [f"h={h}" for h in sp.HORIZONS])
        self.assertIn("2025-26", groups["regime"])
        for label in ("ordinary", "calendar_days"):
            self.assertIn(label, groups["target_day_type"])
        for metric in ("grid_crps", "upper_tail_twcrps"):
            row = groups["pooled"]["all decision days"][metric]["vs"][script.S3][script.GBM]
            if "undefined" not in row:
                self.assertEqual(len(row["skill_interval"]), 2)
                self.assertEqual(len(row["difference_interval"]), 2)

    def test_the_politis_white_block_is_beside_the_protocol_block(self):
        pw = self.result["politis_white"]["pooled"]["all decision days"]["grid_crps"]
        self.assertEqual(sorted(pw), sorted(f"{c}|{r}" for c, r in script.HEADLINE))

    def test_the_calibration_is_pooled_and_by_regime_for_the_three_models_and_b1(self):
        self.assertIn("pooled/all cells", self.result["q95"])
        for model in ("B1", script.A, script.S3, script.GBM):
            entry = self.result["q95"]["pooled/all cells"][model]
            for rule in script.RATES:
                self.assertTrue(0.0 <= entry[rule]["rate"] <= 1.0, (model, rule))

    def test_the_page_states_lens_c_and_reads_the_mean_d_bound(self):
        text = self.page.read_text(encoding="utf-8")
        self.assertIn("Lens C", text)
        self.assertIn("mean-d bound", text)
        self.assertIn("development data, not a verdict", text.lower())
        self.assertIn("(s3)", text)
        self.assertIn("gbm_funding", text)
        self.assertIn("## Question for Eleonora", text)
        self.assertIn("(default)", text)

    def test_the_log_entry_passes_the_log_check(self):
        done = subprocess.run([sys.executable, "-B", str(ROOT / "scripts" / "check_research_log.py"), "check-block", str(self.log)],
                              capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        text = self.log.read_text(encoding="utf-8")
        self.assertIn("- Directive: #1197", text)
        self.assertIn("[H5] step 3", text)

    def test_no_day_after_the_last_scored_day_is_read(self):
        self.assertLessEqual(self.result["notes"]["last_target"], script.LAST_DAY.isoformat())


if __name__ == "__main__":
    unittest.main()
