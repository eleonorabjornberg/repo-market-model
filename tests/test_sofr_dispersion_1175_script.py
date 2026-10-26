"""The helpers of `scripts/sofr_dispersion_1175.py` (#1175; H5 step 3, SOFR's in-panel dispersion, development tier).

Written after the script, which is measurement code. The as-of guards of the arms are recorded in `test_spread_mr_dispersion`, the
scored days pass `spread_mean_reversion_686.require_scored_days` (its recorded mutation is in `test_spread_mean_reversion_686_script`),
and the runs, hit tables and kill assessment are `faster_scale_1153`'s (tested in `test_faster_scale_1153_script`). What these tests
pin: the declared kill rule with (s3) as the base, the reading on the mean-d bound (#1009) against the skill interval, the
declaration's names and constants against the module's, that the page states Lens C's caveat and that the randomised tie rule is
not available, a small end-to-end run on a late subset of days, and that the committed page is what the committed record gives.
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
from repo_model import spread_mr_dispersion as dsp

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("sofr_dispersion_1175", ROOT / "scripts" / "sofr_dispersion_1175.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["sofr_dispersion_1175"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)

DECLARATION = json.loads((ROOT / "metadata" / "sofr_dispersion_1175.json").read_text(encoding="utf-8"))


def cell(p, runs):
    return {"pooled": {"independence": {"p_value": p}}, "runs": runs}


def hits_of(rows):
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

    def hits(self, base, arm):
        rows = {script.S3: {r: base for r in ("above", "at_or_above")}}
        for name in script.ARMS:
            rows[name] = {r: arm for r in ("above", "at_or_above")}
        return hits_of(rows)

    def test_the_kill_is_met_when_nothing_moves_against_s3(self):
        kill = script.kill_assessment(self.hits((self.zero, self.long_runs), (self.zero, self.long_runs)))
        self.assertTrue(kill["met"])
        self.assertEqual((kill["arms_off_zero"], kill["arms_shorter_runs"]), ([], []))

    def test_a_p_value_off_zero_lifts_the_kill(self):
        hits = self.hits((self.zero, self.long_runs), (self.zero, self.long_runs))
        hits["rows"]["d2_upper_half"]["above"]["band90"]["h=2"]["pooled"]["independence"]["p_value"] = 0.0007
        kill = script.kill_assessment(hits)
        self.assertFalse(kill["met"])
        self.assertEqual(kill["arms_off_zero"], ["d2_upper_half"])

    def test_shorter_runs_than_s3_lift_the_kill(self):
        kill = script.kill_assessment(self.hits((self.zero, self.long_runs), (self.zero, self.short_runs)))
        self.assertFalse(kill["met"])
        self.assertEqual(kill["arms_shorter_runs"], list(script.ARMS))
        self.assertAlmostEqual(kill["base_mean_run"], 2.0)


class ReadingTests(unittest.TestCase):

    def row(self, skill, diff):
        return {"skill_interval": skill, "difference_interval": diff}

    def test_the_reading_is_the_mean_d_bound_not_the_skill_interval(self):
        self.assertEqual(script.reading(self.row([-0.01, 0.02], [0.001, 0.02])), "gain")
        self.assertEqual(script.reading(self.row([0.001, 0.02], [-0.01, 0.02])), "undecided")
        self.assertEqual(script.reading(self.row([0.001, 0.02], [-0.03, -0.001])), "loss")

    def test_an_undefined_comparison_is_undecided(self):
        self.assertEqual(script.reading({"undefined": "x"}), "undecided")
        self.assertEqual(script.reading(None), "undecided")


class DeclarationTests(unittest.TestCase):

    def test_the_constants_are_the_modules(self):
        self.assertEqual(script.constants_agree(DECLARATION), [])

    def test_a_changed_constant_is_found(self):
        changed = json.loads(json.dumps(DECLARATION))
        changed["arms"]["constants"]["factor_max"] = 3.0
        self.assertEqual(script.constants_agree(changed), ["factor_max"])

    def test_the_arms_are_the_declared_ones(self):
        self.assertEqual(set(DECLARATION["arms"]["listed_in_full"]), set(script.ARMS))
        self.assertEqual(script.models_of(), ("B1", "B1p", "B2", script.A, script.S3) + script.ARMS)

    def test_the_seed_is_declared_once(self):
        self.assertEqual(script.SEED, 1175)
        self.assertEqual(DECLARATION["scoring"]["paired"].count("seed 1175"), 1)

    def test_the_declaration_keeps_the_tail_percentiles_out(self):
        text = json.dumps(DECLARATION["input"])
        self.assertIn("p1 and p99 are not read", text)
        self.assertEqual(dsp.FEATURES, ("sofr_p25", "sofr_p75"))

    def test_every_band_is_on_the_grid(self):
        for lo, hi in script.BANDS.values():
            self.assertIn(lo, sp.GRID)
            self.assertIn(hi, sp.GRID)


class SubsetRunTests(unittest.TestCase):
    """A late subset of days end to end: the walk, the tests, the page. Not the declared run."""

    @classmethod
    def setUpClass(cls):
        import test_protocol_benchmarks as tpb

        cls.directory = tempfile.TemporaryDirectory()
        cls.out = Path(cls.directory.name) / "result.json"
        code = script.main(["score", "--panel", str(tpb.published_panel()["path"]), "--output", str(cls.out), "--first", "2025-11-03",
                            "--draws", "100", "--reps", "20", "--workers", "2"])
        assert code == 0
        cls.record = json.loads(cls.out.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def test_every_model_is_scored_on_the_same_days_and_the_record_is_labelled(self):
        r = self.record
        self.assertEqual(r["models"], list(script.models_of()))
        self.assertEqual(r["label"], "development, not a verdict")
        self.assertLessEqual(r["notes"]["last_target"], "2025-12-31")
        self.assertEqual(r["subset_from"], "2025-11-03")
        self.assertIn("not available", r["randomised_tie_rule"])
        means = r["groups"]["pooled"]["all decision days"]["grid_crps"]["means"]
        self.assertEqual(set(means), set(script.models_of()))

    def test_each_candidate_is_paired_against_the_benchmarks_and_the_other_comparator(self):
        vs = self.record["groups"]["pooled"]["all decision days"]["grid_crps"]["vs"]
        self.assertEqual(set(vs["d1_iqr"]), {"B1", "B1p", "B2", script.S3, script.A})
        self.assertEqual(set(vs[script.S3]), {"B1", "B1p", "B2", script.A})
        self.assertEqual(set(vs[script.A]), {"B1", "B1p", "B2", script.S3})

    def test_the_page_shows_the_mean_d_bound_lens_cs_caveat_and_the_missing_tie_rule(self):
        page = script.render(self.record)
        self.assertIn("mean-d bound", page)
        self.assertIn("understated by about 2x", page)
        self.assertIn("not on main", page)
        self.assertIn("Development, not a verdict", page)

    def test_the_fitted_slopes_are_within_their_cap(self):
        for arm, leads in self.record["diagnostics"]["gamma"].items():
            for values in leads.values():
                self.assertTrue(values)
                self.assertTrue(all(0.0 <= g <= dsp.GAMMA_MAX for g in values), arm)


class PageTests(unittest.TestCase):

    record = ROOT / "docs" / "research" / "sofr-dispersion-1175" / "result.json"
    page = ROOT / "docs" / "research" / "sofr-dispersion-1175-result.md"

    def test_the_committed_page_is_what_the_committed_record_gives(self):
        if not self.record.exists():
            self.skipTest("the record is not committed yet")
        self.assertEqual(script.render(json.loads(self.record.read_text(encoding="utf-8"))), self.page.read_text(encoding="utf-8"))

    def test_the_record_is_labelled_development_and_stops_at_the_last_day(self):
        if not self.record.exists():
            self.skipTest("the record is not committed yet")
        data = json.loads(self.record.read_text(encoding="utf-8"))
        self.assertEqual(data["label"], "development, not a verdict")
        self.assertLessEqual(data["notes"]["last_target"], "2025-12-31")
        self.assertIsNone(data["subset_from"])
        self.assertEqual(data["seed"], 1175)


if __name__ == "__main__":
    unittest.main()
