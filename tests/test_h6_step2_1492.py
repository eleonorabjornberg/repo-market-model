"""`scripts/h6_step2_1492.py` (#1492; H6 development step 2, re-run under Eleonora's ruling of 6 November 2026, development tier).

Written first, against `metadata/h6_step2_1492.json`. The run is #724's (`scripts/h6_step2_724.py`) with two things replaced: the paired test, which
now keeps the mean-d bound where skill is undefined (#1215, #1239), and the reading, which is taken from the lower end of the mean-d interval
(#1009). Pinned here on hand cases: the fallback, the reading rules, the comparison with #724's record and the refusal when a defined row moves.

**Recorded mutations** (6 November 2026).

1. In `lower_end` (every reading is taken from the mean-d interval, her ruling on #1009), the line

       return row["difference_interval"][0]

   was changed to `return row["skill_interval"][0]`. `ReadingTests.test_the_reading_is_taken_from_the_mean_d_bound` then failed with
   `AssertionError: 0.02 != -0.01`; restored, it passes.

2. In `paired` (a pair whose skill is undefined keeps its mean-d bound, #1215), the line

       test = _mean_d_alone(pair, draws)

   was changed to `raise`. `FallbackTests.test_a_row_with_skill_undefined_keeps_its_mean_d_bound` then failed with `RuntimeError: No active exception
   to reraise` (the row no longer comes back, so a bound is lost); restored, it passes.

3. In `require_defined_rows_reproduce` (a row #724 defined must come back unchanged), the line

       if _differs(old_row, new_row):

   was changed to `if False:`. `ComparisonTests.test_a_defined_row_that_moves_is_refused` then failed with `AssertionError: ValueError not raised`; restored,
   it passes.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
_spec = importlib.util.spec_from_file_location("h6_step2_1492", ROOT / "scripts" / "h6_step2_1492.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["h6_step2_1492"] = script
_spec.loader.exec_module(script)

from repo_model import scoring_protocol as sp  # noqa: E402


def row(skill_interval, difference_interval, **extra):
    out = {"events": 40, "days": 40, "skill": 0.1, "skill_interval": skill_interval, "difference": 0.01, "difference_interval": difference_interval}
    out.update(extra)
    return out


def series(n=40, start=date(2021, 1, 4)):
    return [start + timedelta(days=i) for i in range(n)]


class ReadingTests(unittest.TestCase):
    def test_the_reading_is_taken_from_the_mean_d_bound(self):
        # skill lower end above zero, mean-d lower end below it: the mean-d bound decides
        r = row([0.02, 0.2], [-0.01, 0.05])
        self.assertEqual(script.lower_end(r), -0.01)
        self.assertEqual(script.row_reading(r), "undecided")
        self.assertEqual(script.kill_reading(r, row([0.02, 0.2], [0.01, 0.05])), "no skill shown")
        self.assertEqual(script.kill_reading(row([-0.02, 0.2], [0.01, 0.05]), row([-0.02, 0.2], [0.01, 0.05])), "skill")

    def test_gain_loss_and_undecided(self):
        self.assertEqual(script.row_reading(row([0, 1], [0.01, 0.05])), "gain")
        self.assertEqual(script.row_reading(row([0, 1], [-0.05, -0.01])), "loss")
        self.assertEqual(script.row_reading(row([0, 1], [-0.05, 0.01])), "undecided")

    def test_a_row_without_a_bound_has_no_reading(self):
        self.assertEqual(script.row_reading({"events": 10, "thin": True}), "no reading")
        self.assertEqual(script.row_reading({"events": 40, "identical": True}), "no reading")
        self.assertEqual(script.row_reading({"events": 40, "undefined": "no long-run variance"}), "no reading")
        self.assertEqual(script.kill_reading({"events": 40, "undefined": "x"}, row([0, 1], [0.01, 0.05])), "undefined")

    def test_a_row_with_skill_undefined_is_read_on_its_bound(self):
        r = row(None, [0.01, 0.05], skill=None, skill_undefined="benchmark scores zero")
        self.assertEqual(script.row_reading(r), "gain")
        self.assertTrue(script.variant_adds(r))
        self.assertFalse(script.variant_adds(row([0.1, 0.2], [-0.01, 0.05])))


class FallbackTests(unittest.TestCase):
    def pair(self):
        days = series()
        # B1-like: zero on all days but one, so a resample that misses that day makes the benchmark mean zero and skill undefined
        bench = {d: 0.0 for d in days}
        bench[days[7]] = 3.0
        cand = {d: 0.01 * ((i * 7) % 5) for i, d in enumerate(days)}
        return bench, cand, days

    def test_a_row_with_skill_undefined_keeps_its_mean_d_bound(self):
        bench, cand, days = self.pair()
        pair = ({e: bench[e] for e in days}, {e: cand[e] for e in days})
        with self.assertRaises(sp.ProtocolError):
            sp.paired_tests([pair], seed=724, draws=400, block_length=script.EVENT_BLOCK, hac_lag=script.EVENT_LAG)
        out = script.paired(bench, cand, days, draws=400)
        self.assertNotIn("undefined", out)
        self.assertIsNone(out["skill"])
        self.assertIsNone(out["skill_interval"])
        self.assertTrue(out["skill_undefined"])
        lo, hi = out["difference_interval"]
        self.assertLess(lo, out["difference"])
        self.assertGreater(hi, out["difference"])
        self.assertEqual(out["events"], 40)

    def test_a_defined_row_is_what_the_pooled_call_gives(self):
        days = series()
        bench = {d: 1.0 + 0.1 * ((i * 3) % 7) for i, d in enumerate(days)}
        cand = {d: 0.9 + 0.1 * ((i * 5) % 6) for i, d in enumerate(days)}
        out = script.paired(bench, cand, days, draws=400)
        (test,) = sp.paired_tests([(bench, cand)], seed=724, draws=400, block_length=script.EVENT_BLOCK, hac_lag=script.EVENT_LAG)
        self.assertEqual(out["skill"], test.skill)
        self.assertEqual(out["difference"], test.mean_difference)
        self.assertNotIn("skill_undefined", out)

    def test_thin_and_identical_are_left_as_they_were(self):
        days = series(10)
        same = {d: 1.0 for d in days}
        self.assertEqual(script.paired(same, same, days), {"events": 10, "thin": True})
        days = series(40)
        same = {d: 1.0 for d in days}
        self.assertEqual(script.paired(same, same, days), {"events": 40, "identical": True})

    def test_a_series_with_no_long_run_variance_stays_undefined_with_the_reason(self):
        days = series(40)
        out = script.paired({d: 1.0 for d in days}, {d: 0.5 for d in days}, days, draws=100)
        self.assertIn("undefined", out)
        self.assertEqual(out["events"], 40)

    def test_dropping_row_equals_761_at_the_pooled_defaults(self):
        s761 = script._load("spread_mr_variants_761")
        days = series(60)
        bench = {d: 1.0 + 0.1 * ((i * 3) % 7) for i, d in enumerate(days)}
        cand = {d: 0.9 + 0.1 * ((i * 5) % 6) for i, d in enumerate(days)}
        mine = script.mean_d_dropping_row((bench, cand), "why", 11, 300, sp.BLOCK_LENGTH, sp.HAC_LAG)
        theirs = s761.mean_d_dropping_row((bench, cand), "why", 11, 300)
        self.assertEqual(mine, theirs)


class ComparisonTests(unittest.TestCase):
    def records(self):
        old = {"rows": {"set/u": {"grid_crps": {
            "candidate": {"B1": row([0.02, 0.2], [0.01, 0.05]), "B2": row([0.02, 0.2], [0.01, 0.05]), "B1_prime": {"undefined": "zero", "events": 40}},
            "variant": {"B1": row([0.02, 0.2], [0.01, 0.05]), "B2": row([0.02, 0.2], [0.01, 0.05]), "candidate": row([-0.02, 0.2], [0.01, 0.05])}}}}}
        new = {"rows": {"set/u": {"grid_crps": {
            "candidate": {"B1": row([0.02, 0.2], [0.01, 0.05]), "B2": row([0.02, 0.2], [0.01, 0.05]),
                          "B1_prime": row(None, [0.01, 0.05], skill=None, skill_undefined="zero")},
            "variant": {"B1": row([0.02, 0.2], [0.01, 0.05]), "B2": row([0.02, 0.2], [0.01, 0.05]), "candidate": row([-0.02, 0.2], [0.01, 0.05])}}}}}
        return old, new

    def test_the_newly_defined_row_is_listed(self):
        old, new = self.records()
        c = script.compare(old, new)
        self.assertEqual([x["key"] for x in c["newly_defined"]], [["set/u", "grid_crps", "candidate", "B1_prime"]])
        self.assertEqual(c["newly_defined"][0]["reading"], "gain")
        self.assertEqual(c["disagree"][0]["key"], ["set/u", "grid_crps", "variant", "candidate"])

    def test_a_row_whose_lower_ends_straddle_zero_is_listed_with_both_readings(self):
        old, new = self.records()
        c = script.compare(old, new)
        self.assertEqual(len(c["disagree"]), 1)
        d = c["disagree"][0]
        self.assertEqual(d["key"], ["set/u", "grid_crps", "variant", "candidate"])
        self.assertEqual((d["skill_lower"], d["mean_d_lower"]), (-0.02, 0.01))
        self.assertEqual((d["skill_reading"], d["mean_d_reading"]), ("not shown", "gain"))
        self.assertEqual(d["direction"], "gains on the mean-d bound")

    def test_a_defined_row_that_moves_is_refused(self):
        old, new = self.records()
        new["rows"]["set/u"]["grid_crps"]["candidate"]["B1"]["difference"] = 0.5
        with self.assertRaises(ValueError):
            script.require_defined_rows_reproduce(old, new)

    def test_a_row_defined_before_and_undefined_now_is_refused(self):
        old, new = self.records()
        new["rows"]["set/u"]["grid_crps"]["candidate"]["B1"] = {"undefined": "x", "events": 40}
        with self.assertRaises(ValueError):
            script.require_defined_rows_reproduce(old, new)

    def test_the_readings_that_move_are_listed(self):
        old, new = self.records()
        for rec in (old, new):
            rec["rows"]["set/u"]["upper_tail_twcrps"] = {"variant": {"candidate": row([-0.02, 0.2], [0.01, 0.05])}}
        old["rows"]["set/u"]["grid_crps"]["candidate"]["B1"] = {"undefined": "x", "events": 40}
        self.assertEqual(script.readings(old, "set/u")["kill_rule_candidate"], "undefined")
        now = script.readings(new, "set/u")
        self.assertEqual(now["kill_rule_candidate"], "skill")
        self.assertTrue(now["variant_adds_grid_crps"])
        # the same record read on the skill interval, as #724 did, does not add skill
        self.assertFalse(script.readings(new, "set/u", script.skill_lower_end)["variant_adds_grid_crps"])


if __name__ == "__main__":
    unittest.main()
