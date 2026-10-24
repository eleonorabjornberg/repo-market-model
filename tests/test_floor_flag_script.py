"""The scoring script of #966 (H5 step 3): the flag's windows, the declared kill rules and the page.

`scripts/floor_flag_966.py` scores the arms of `repo_model.floor_flag`; the arithmetic is tested in `test_floor_flag.py`.
What these tests pin: the runs of the flag the page reports; the two kill rules read the interval the declaration names
(arm (ii): the interval covers 0 or lies below it on the 2024-26 days; arm (iii): the upper bound is below 0); a record
without walks says arm (iii) was not run; the page is what the committed record gives; the declaration is the file the
script reads and it is committed unchanged before the score (`committed_declaration`).

Since the amendment of 22 October 2026 (arms (iv) and (v) on #941's scaled mean reversion): kill rule (iv) is arm (ii)'s
rule on the scaled model's own pool, kill rule (v) is arm (iii)'s on the scaled model, pooled, and the page reads the
scaled arms first.

Recorded mutation (2026-10-19): in `scripts/floor_flag_966.py`, `kill_ii` returned `killed = hi <= 0.0` instead of
`lo <= 0.0` (the upper bound instead of the lower); `test_arm_ii_is_killed_when_the_interval_covers_zero` raised
AssertionError (False is not true). Not a leakage guard.
"""

import importlib.util
import json
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("floor_flag_966", ROOT / "scripts" / "floor_flag_966.py")
script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script)


class Row:
    def __init__(self, day):
        self.date = day


def test_row(skill, lo, hi):
    return {"skill": skill, "skill_interval": [lo, hi], "days": 100, "benchmark_mean": 1.0, "candidate_mean": 0.9,
            "difference": 0.1, "difference_interval": [0.0, 0.2], "dm_statistic": 1.0, "dm_p_value": 0.1}


def record(ii=(0.02, -0.01, 0.05), iii=None, iv=(0.02, 0.01, 0.05), v=(0.02, 0.01, 0.05)):
    cell = lambda row: {"means": {}, "vs": {}, "row": row}
    fhs_arms = (script.FHS, script.ff.ARM_FHS, script.ff.ARM_TWO_FHS)
    main_pooled = {m: {"means": {k: 1.0 for k in ("B1", "B2", script.BASE, script.ff.ARM_B1, script.ff.ARM_MR) + fhs_arms},
                       "vs": {c: {"B1": test_row(0.01, 0.0, 0.02), "B2": test_row(0.01, 0.0, 0.02), script.BASE: test_row(*ii),
                                  script.FHS: test_row(*v)}
                              for c in (script.BASE, script.ff.ARM_B1, script.ff.ARM_MR) + fhs_arms}}
                   for m in ("grid_crps", "upper_tail_twcrps")}
    window = {m: {"means": dict(main_pooled[m]["means"]),
                  "vs": {script.ff.ARM_MR: {script.BASE: test_row(*ii)}, script.ff.ARM_FHS: {script.FHS: test_row(*iv)}}}
              for m in main_pooled}
    out = {
        "declaration": "metadata/floor_flag_966.json", "draws": 10, "seed": 966, "panel_sha256": "0" * 64,
        "notes": {"scored_decision_days": 10, "first": "2018-07-19", "last": "2025-12-23", "last_target": "2025-12-31",
                  "candidate_skipped_for_history": 1, "benchmark_missing": [], "refits": 1,
                  "own_pool_share": {"on": [1] * 5, "off": [1] * 5},
                  "scaled_own_pool_share": {"on": [1] * 5, "off": [1] * 5}},
        "flag": {"windows": [["2021-04-21", "2023-12-08"]], "rows_on": 5, "rows_off": 5, "rows_undefined": 1,
                 "anchor_state_by_regime": {"2021-23": {"days": 10, "on": 6, "off": 4, "undefined": 0}}},
        "main": {"days": 10, "skipped_groups": {}, "groups": {"pooled": {"all decision days": {"days": 10, **main_pooled}},
                                                                "window": {"2024-26": {"days": 10, **window}}}},
    }
    if iii is not None:
        pooled = {m: {"means": {k: 1.0 for k in ("B1", "B2", script.GBM, script.FLAG_GBM)},
                      "vs": {c: {"B1": test_row(0.01, 0.0, 0.02), "B2": test_row(0.01, 0.0, 0.02), script.GBM: test_row(*iii)}
                             for c in (script.GBM, script.FLAG_GBM)}} for m in ("grid_crps", "upper_tail_twcrps")}
        out["walks_notes"] = {"walk_days": 10, "first": "2018-07-19", "last": "2025-12-23", "missing_days": 0,
                              "missing_share": 0.0, "flag_on_days": 5, "flag_state_days": {}}
        out["walks"] = {"days": 10, "skipped_groups": {}, "groups": {"pooled": {"all decision days": {"days": 10, **pooled}}}}
    return out


class ScriptTests(unittest.TestCase):

    def test_on_windows_are_the_runs_of_consecutive_rows(self):
        panel = [Row(date(2021, 1, d)) for d in range(1, 9)]
        flags = [None, True, True, False, True, True, True, False]
        self.assertEqual(script.on_windows(panel, flags), [("2021-01-02", "2021-01-03"), ("2021-01-05", "2021-01-07")])
        self.assertEqual(script.on_windows(panel, [True] * 8), [("2021-01-01", "2021-01-08")])

    def test_arm_ii_is_killed_when_the_interval_covers_zero(self):
        self.assertTrue(script.kill_ii(record(ii=(0.02, -0.01, 0.05)))["killed"])
        self.assertTrue(script.kill_ii(record(ii=(-0.05, -0.08, -0.01)))["killed"])
        self.assertFalse(script.kill_ii(record(ii=(0.03, 0.01, 0.05)))["killed"])

    def test_arm_iii_is_killed_only_when_the_upper_bound_is_below_zero(self):
        self.assertIsNone(script.kill_iii(record()))
        self.assertTrue(script.kill_iii(record(iii=(-0.05, -0.09, -0.01)))["killed"])
        self.assertFalse(script.kill_iii(record(iii=(-0.01, -0.05, 0.03)))["killed"])
        self.assertFalse(script.kill_iii(record(iii=(0.02, 0.01, 0.04)))["killed"])

    def test_a_record_without_walks_says_arm_iii_was_not_run(self):
        page = script.render(record())
        self.assertIn("**not run**", page)
        self.assertIn("Not run in this record", page)
        self.assertIn("not a verdict", page)

    def test_a_record_with_walks_reports_the_two_kill_rules(self):
        page = script.render(record(iii=(-0.05, -0.09, -0.01)))
        self.assertIn("Kill rule met", page)
        self.assertNotIn("Not run in this record", page)

    def test_arm_iv_is_killed_when_the_interval_covers_zero(self):
        self.assertTrue(script.kill_iv(record(iv=(0.02, -0.01, 0.05)))["killed"])
        self.assertTrue(script.kill_iv(record(iv=(-0.05, -0.08, -0.01)))["killed"])
        self.assertFalse(script.kill_iv(record(iv=(0.03, 0.01, 0.05)))["killed"])

    def test_arm_v_is_killed_only_when_the_upper_bound_is_below_zero(self):
        self.assertTrue(script.kill_v(record(v=(-0.05, -0.09, -0.01)))["killed"])
        self.assertFalse(script.kill_v(record(v=(-0.01, -0.05, 0.03)))["killed"])
        self.assertFalse(script.kill_v(record(v=(0.02, 0.01, 0.04)))["killed"])

    def test_the_page_reports_the_scaled_arms_and_their_kill_rules(self):
        page = script.render(record(iv=(0.03, 0.01, 0.05), v=(-0.05, -0.09, -0.01)))
        self.assertIn("(iv)", page)
        self.assertIn("(v)", page)
        self.assertIn("scaled mean reversion", page)
        self.assertLess(page.index("Arms (iv) and (v)"), page.index("Arms (i) and (ii)"))
        self.assertIn("Kill rule (v) met", page)

    def test_the_window_labels_split_at_2024(self):
        self.assertEqual(script.window_label(date(2023, 12, 29)), "2021-23")
        self.assertEqual(script.window_label(date(2024, 1, 2)), "2024-26")

    def test_the_declaration_is_the_file_the_script_reads(self):
        document = json.loads(script.DECLARATION.read_text(encoding="utf-8"))
        self.assertEqual(document["issue"], 966)
        self.assertEqual(set(document["arms"]), {"flag_b1", "flag_mr", "flag_gbm", "flag_fhs", "two_part_fhs"})
        self.assertEqual(script.SEED, 966)
        self.assertIn("rule_iv", document["kill"])
        self.assertIn("rule_v", document["kill"])
        self.assertEqual(script.FHS, "spread_mr_fhs_mad20_f0.5")
        self.assertIn(script.FHS, document["references"])
