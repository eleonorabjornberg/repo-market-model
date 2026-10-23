"""The helpers of `scripts/faster_scale_1153.py` (#1153; H5 step 3, fix of the clustered misses, development tier).

Written after the script, which is measurement code. It adds no reader of its own: the scored days pass
`spread_mean_reversion_686.require_scored_days` (its recorded mutation is in `test_spread_mean_reversion_686_script`), and the arms'
as-of guards are recorded in `test_spread_mr_scale`. What these tests pin: the runs of misses on hand cases (the headline of this
fix), the declared rule that picks the arm v4 builds on, the declared kill rule, the comparison with `gbm_funding` on hand cases, the
declaration's names and constants against the module's, and that the committed page is what the committed record gives.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import scoring_protocol as sp
from repo_model import spread_mr_scale as sc

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("faster_scale_1153", ROOT / "scripts" / "faster_scale_1153.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["faster_scale_1153"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)


class RunTests(unittest.TestCase):

    def test_runs_of_a_sequence(self):
        self.assertEqual(script.runs_of([0, 1, 1, 0, 1, 0, 0, 1, 1, 1]), {"runs": 3, "hits": 6, "longest": 3})
        self.assertEqual(script.runs_of([0, 0, 0]), {"runs": 0, "hits": 0, "longest": 0})
        self.assertEqual(script.runs_of([1, 1, 1]), {"runs": 1, "hits": 3, "longest": 3})
        self.assertEqual(script.runs_of([]), {"runs": 0, "hits": 0, "longest": 0})

    def test_independent_looking_misses_have_runs_of_one(self):
        self.assertEqual(script.runs_of([1, 0] * 5), {"runs": 5, "hits": 5, "longest": 1})

    def test_leads_pool_by_total_hits_over_total_runs(self):
        pooled = script.pooled_runs([{"runs": 2, "hits": 6, "longest": 4}, {"runs": 3, "hits": 3, "longest": 1}])
        self.assertEqual(pooled, {"runs": 5, "hits": 9, "mean": 9 / 5, "longest": 4})
        self.assertIsNone(script.pooled_runs([{"runs": 0, "hits": 0, "longest": 0}])["mean"])


class SelectionTests(unittest.TestCase):

    def stats(self, **kw):
        return {name: {"crps": c, "mean_run": r} for name, (c, r) in kw.items()}

    def test_the_shortest_run_among_the_eligible_wins(self):
        stats = self.stats(v1_mad5=(1.50, 1.2), v1_mad10=(1.49, 1.5), v3_miss=(1.60, 1.1))
        # (a) = 1.48: 1.50 is within 1%+ of... 1.48 * 1.01 = 1.4948, so only v1_mad10 is eligible
        self.assertEqual(script.select_v4(stats, 1.48), "v1_mad10")

    def test_the_run_decides_between_eligible_arms(self):
        stats = self.stats(v1_mad5=(1.47, 1.8), v1_mad10=(1.48, 1.3), v3_miss=(1.475, 1.5))
        self.assertEqual(script.select_v4(stats, 1.48), "v1_mad10")

    def test_none_eligible_takes_the_lowest_crps(self):
        stats = self.stats(v1_mad5=(1.60, 1.1), v1_mad10=(1.55, 2.0))
        self.assertEqual(script.select_v4(stats, 1.48), "v1_mad10")

    def test_a_tie_on_run_goes_to_the_lower_crps_then_the_declared_order(self):
        stats = self.stats(v1_mad10=(1.48, 1.5), v1_mad5=(1.47, 1.5))
        self.assertEqual(script.select_v4(stats, 1.48), "v1_mad5")
        stats = self.stats(v2_ewma_hl3=(1.47, 1.5), v1_mad5=(1.47, 1.5))
        self.assertEqual(script.select_v4(stats, 1.48), "v1_mad5")


def cell(p, runs):
    return {"pooled": {"independence": {"p_value": p}}, "runs": runs}


def hits_of(rows):
    """`rows[model][rule] = (independence p per lead, runs per lead)` as the hit tables lay them out."""

    out = {"rules": ["above", "at_or_above"], "rows": {}}
    for model, by_rule in rows.items():
        for rule, (ps, runs) in by_rule.items():
            out["rows"].setdefault(model, {}).setdefault(rule, {"band90": {}})["band90"] = {
                f"h={h}": cell(ps[h - 1], runs[h - 1]) for h in sp.HORIZONS}
    return out


class KillTests(unittest.TestCase):

    long_runs = [{"runs": 5, "hits": 10, "longest": 4}] * 5
    short_runs = [{"runs": 8, "hits": 10, "longest": 2}] * 5
    zero = [0.0] * 5

    def hits(self, a, arm):
        return hits_of({"a": {r: a for r in ("above", "at_or_above")}, "arm": {r: arm for r in ("above", "at_or_above")}})

    def test_the_kill_is_met_when_nothing_moves(self):
        kill = script.kill_assessment(self.hits((self.zero, self.long_runs), (self.zero, self.long_runs)), ["a", "arm"], "a")
        self.assertTrue(kill["met"])
        self.assertEqual((kill["arms_off_zero"], kill["arms_shorter_runs"]), ([], []))

    def test_a_p_value_off_zero_at_one_lead_under_one_rule_lifts_the_kill(self):
        hits = self.hits((self.zero, self.long_runs), (self.zero, self.long_runs))
        hits["rows"]["arm"]["at_or_above"]["band90"]["h=3"]["pooled"]["independence"]["p_value"] = 0.0006
        kill = script.kill_assessment(hits, ["a", "arm"], "a")
        self.assertFalse(kill["met"])
        self.assertEqual(kill["arms_off_zero"], ["arm"])
        self.assertEqual(kill["models"]["arm"]["off_zero_leads"], {"above": [], "at_or_above": [3]})

    def test_a_p_value_below_the_threshold_is_still_zero(self):
        hits = self.hits((self.zero, self.long_runs), (self.zero, self.long_runs))
        hits["rows"]["arm"]["above"]["band90"]["h=1"]["pooled"]["independence"]["p_value"] = 0.0004
        self.assertTrue(script.kill_assessment(hits, ["a", "arm"], "a")["met"])

    def test_shorter_mean_runs_lift_the_kill(self):
        kill = script.kill_assessment(self.hits((self.zero, self.long_runs), (self.zero, self.short_runs)), ["a", "arm"], "a")
        self.assertFalse(kill["met"])
        self.assertEqual(kill["arms_shorter_runs"], ["arm"])
        self.assertAlmostEqual(kill["base_mean_run"], 2.0)

    def test_longer_runs_do_not(self):
        kill = script.kill_assessment(self.hits((self.zero, self.short_runs), (self.zero, self.long_runs)), ["a", "arm"], "a")
        self.assertTrue(kill["met"])


class FakeFrame:
    """Twenty-five consecutive days of 2022, a target `h` days on, an outcome on each."""

    def __init__(self):
        start = date(2022, 3, 1)
        self.days = [start + timedelta(days=i) for i in range(25)]
        self.outcome = {start + timedelta(days=i): float(i % 7) for i in range(40)}

    def target(self, day, lead):
        return day + timedelta(days=lead)


class GbmTests(unittest.TestCase):

    def test_each_candidate_is_tested_against_gbm_funding_on_the_days_both_cover(self):
        frame = FakeFrame()
        law = [float(i) / 10.0 for i in range(len(sp.GRID))]
        gbm = {d: {h: list(law) for h in sp.HORIZONS} for d in frame.days[:22]}
        series = {"m": {d: 1.0 + 0.01 * i for i, d in enumerate(frame.days)}}
        out = script.gbm_comparison(frame, gbm, series, ["m"], "grid_crps", draws=50)
        self.assertEqual(out["days"], 22)
        self.assertIn("m", out["vs"])
        self.assertAlmostEqual(out["vs"]["m"]["candidate_mean"], sum(1.0 + 0.01 * i for i in range(22)) / 22)

    def test_too_few_days_are_said_so(self):
        frame = FakeFrame()
        law = [0.0] * len(sp.GRID)
        out = script.gbm_comparison(frame, {frame.days[0]: {h: law for h in sp.HORIZONS}}, {"m": {}}, ["m"], "grid_crps", draws=50)
        self.assertIn("undefined", out)


class DeclarationTests(unittest.TestCase):

    declaration = json.loads((ROOT / "metadata" / "faster_scale_1153.json").read_text(encoding="utf-8"))

    def test_the_arms_are_the_declared_ones(self):
        listed = self.declaration["arms"]["listed_in_full"]
        self.assertEqual(set(listed), {"a", "v4"} | {arm.name for arm in sc.ARMS})
        self.assertEqual(script.BASE, "spread_mr_fhs_mad20_f0.5")

    def test_the_constants_are_the_declared_ones(self):
        c = self.declaration["arms"]["constants"]
        self.assertEqual(
            (sc.FLOOR, sc.EWMA_ROWS, sc.ASYM, sc.MISS_MIN, list(sc.BAND), sc.CAL_K, sc.FACTOR_CAP),
            (c["floor_bp"], c["ewma_rows"], c["asym"], c["miss_min_pairs"], c["miss_band"], c["calendar_shrinkage_k"], c["factor_cap"]))
        self.assertEqual(sc.BASE_SCALE.windows, (20,))
        self.assertEqual(script.ELIGIBLE_SLACK, 1.01)
        self.assertIn("1% above", self.declaration["arms"]["v4_selection_rule"])
        self.assertEqual(script.OFF_ZERO, 0.0005)

    def test_the_seed_and_the_amendment(self):
        self.assertEqual(script.SEED, 1153)
        self.assertEqual(self.declaration["scoring"]["paired"].count("seed 1153"), 1)
        self.assertEqual([a["date"] for a in self.declaration["amendments"]], ["2026-10-22", "2026-10-23"])  # the 23rd: the reading rule, #1167

    def test_every_band_is_on_the_grid(self):
        for lo, hi in script.BANDS.values():
            self.assertIn(lo, sp.GRID)
            self.assertIn(hi, sp.GRID)


class PageTests(unittest.TestCase):

    record = ROOT / "docs" / "research" / "faster-scale-1153" / "result.json"
    page = ROOT / "docs" / "research" / "faster-scale-1153-result.md"

    def test_the_committed_page_is_what_the_committed_record_gives(self):
        if not self.record.exists():
            self.skipTest("the record is not committed yet")
        self.assertEqual(script.render(json.loads(self.record.read_text(encoding="utf-8")), reading="skill"), self.page.read_text(encoding="utf-8"))  # the page as first written (#1167)

    def test_the_record_is_labelled_development_and_stops_at_the_last_day(self):
        if not self.record.exists():
            self.skipTest("the record is not committed yet")
        data = json.loads(self.record.read_text(encoding="utf-8"))
        self.assertEqual(data["label"], "development, not a verdict")
        self.assertLessEqual(data["notes"]["last_target"], "2025-12-31")
        self.assertIsNone(data["subset_from"])

    def test_the_arm_v4_builds_on_is_the_one_the_rule_picks_from_the_record(self):
        if not self.record.exists():
            self.skipTest("the record is not committed yet")
        data = json.loads(self.record.read_text(encoding="utf-8"))
        s = data["selection"]
        self.assertEqual(script.select_v4(s["stats"], s["base_crps"]), s["winner"])
        self.assertEqual(s["v4"], f"v4_{s['winner']}_cal")


class LoaderTests(unittest.TestCase):

    def test_a_script_another_module_registered_is_not_replaced(self):
        registered = sys.modules.get("fhs_scale_941")
        if registered is None:
            self.skipTest("fhs_scale_941 not loaded")
        self.assertIs(script._load("fhs_scale_941"), registered)


if __name__ == "__main__":
    unittest.main()
