"""The helpers of `scripts/coverage_size_1156.py` (#1156; H1 and H5 step 5, development tier).

The study measures the family-wise size of the coverage requirement of draft amendment 4 (#1130) under three hit rules,
on calibrated forecasters of a whole-bp target. It adds no guard of its own: the lockbox refusal, the thinning and the
requirement are `scoring_protocol.coverage_cells` and `enforce_coverage_requirement`, tested in
`test_scoring_protocol_coverage_requirement` and `test_coverage_randomised_1156`. What these tests pin: the discrete
quantile and its tie probability make the forecaster exactly calibrated for the randomised rule (analytically, not by
simulation); the world is whole-bp and seeded; the script reads the cells through `coverage_cells`; the flag is patched
on only inside the call and is False afterwards; the interval and the naming rule on hand cases; and that the committed
page is what the committed record gives.
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
import unittest
from pathlib import Path
from statistics import NormalDist

from repo_model import scoring_protocol as sp

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("coverage_size_1156", ROOT / "scripts" / "coverage_size_1156.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["coverage_size_1156"] = script  # the script's worker pool pickles its functions by module name
_spec.loader.exec_module(script)

N = NormalDist()


class QuantileTests(unittest.TestCase):
    def test_the_quantile_is_the_smallest_integer_with_enough_mass(self):
        for m in (-1.3, 0.0, 0.4, 2.7):
            for s in (0.5, 1.0, 2.2):
                for level in (0.01, 0.05, 0.95, 0.99):
                    q, below, at = script.discrete_quantile(m, s, level)
                    self.assertEqual(q, int(q))
                    self.assertLess(below, level)
                    self.assertGreaterEqual(at, level)
                    self.assertAlmostEqual(at, N.cdf((q + 0.5 - m) / s))
                    self.assertAlmostEqual(below, N.cdf((q - 0.5 - m) / s))

    def test_the_randomised_hit_probability_is_exactly_the_tail_level(self):
        # Analytic: P(hit) = P(beyond q) + p_tie * P(Y = q) must equal the tail probability at every level.
        for m in (-1.3, 0.0, 0.4, 2.7):
            for s in (0.5, 1.0, 2.2):
                for level in (0.01, 0.05, 0.95, 0.99):
                    q, below, at = script.discrete_quantile(m, s, level)
                    upper = level > 0.5
                    tail = 1.0 - level if upper else level
                    p = script.tie_probability(below, at, level)
                    beyond = (1.0 - at) if upper else below
                    self.assertAlmostEqual(beyond + p * (at - below), tail, places=9)

    def test_the_deterministic_rules_bracket_the_tail_level(self):
        q, below, at = script.discrete_quantile(0.0, 0.8, 0.95)
        self.assertLessEqual(1.0 - at, 0.05)
        self.assertGreaterEqual(1.0 - below, 0.05)
        self.assertGreater(at - below, 0.05)  # a real mass point: strict and tie_counts are both mis-sized


class WorldTests(unittest.TestCase):
    def test_the_target_is_whole_bp_and_the_quantiles_are_integers(self):
        world = script.simulate(7, narrow=1.0, days=60)
        self.assertTrue(all(y == int(y) for y in world["outcomes"].values()))
        for day, leads in world["forecasts"].items():
            for h, quantiles in leads.items():
                for level in sp.COVERAGE_LEVELS:
                    self.assertEqual(quantiles[sp.GRID.index(level)], int(quantiles[sp.GRID.index(level)]))

    def test_a_seed_gives_the_same_world_and_another_seed_a_different_one(self):
        a = script.simulate(7, narrow=1.0, days=60)
        b = script.simulate(7, narrow=1.0, days=60)
        c = script.simulate(8, narrow=1.0, days=60)
        self.assertEqual(a["outcomes"], b["outcomes"])
        self.assertNotEqual(a["outcomes"], c["outcomes"])

    def test_the_narrow_forecaster_shares_the_outcomes_and_has_tighter_quantiles(self):
        wide = script.simulate(7, narrow=1.0, days=60)
        thin = script.simulate(7, narrow=0.5, days=60)
        self.assertEqual(wide["outcomes"], thin["outcomes"])
        day = sorted(wide["forecasts"])[10]
        i95, i05 = sp.GRID.index(0.95), sp.GRID.index(0.05)
        self.assertLess(
            thin["forecasts"][day][5][i95] - thin["forecasts"][day][5][i05],
            wide["forecasts"][day][5][i95] - wide["forecasts"][day][5][i05],
        )

    def test_the_regimes_follow_the_declared_blocks(self):
        world = script.simulate(7, narrow=1.0, days=2000)
        labels = [world["regimes"][day] for day in sorted(world["regimes"])]
        self.assertEqual(labels[0], "calm")
        self.assertEqual(labels[799], "calm")
        self.assertEqual(labels[800], "stress")
        self.assertEqual(labels[1199], "stress")
        self.assertEqual(labels[1200], "ordinary")
        self.assertEqual(labels[-1], "ordinary")

    def test_the_calendar_is_on_development_days(self):
        world = script.simulate(7, narrow=1.0, days=2000)
        self.assertLess(max(world["calendar"]).year, 2020)


class PathTests(unittest.TestCase):
    def test_a_path_reports_each_rule_overall_and_by_lead_and_leaves_the_flag_off(self):
        out = script.path_report(3, narrow=1.0, days=300)
        self.assertEqual(set(out["fails"]), {"strict", "tie_counts", "randomised"})
        for rule, row in out["fails"].items():
            self.assertEqual(set(row), {"all", "1", "2", "3", "4", "5"})
            self.assertTrue(all(isinstance(v, bool) for v in row.values()))
        self.assertFalse(sp.COVERAGE_REQUIREMENT_IN_FORCE)

    def test_the_flag_is_restored_even_when_the_requirement_raises(self):
        script.path_report(3, narrow=0.4, days=300)
        self.assertFalse(sp.COVERAGE_REQUIREMENT_IN_FORCE)

    def test_a_grossly_narrow_forecaster_fails_every_rule(self):
        out = script.path_report(3, narrow=0.4, days=600)
        self.assertTrue(all(row["all"] for row in out["fails"].values()))

    def test_the_hit_rates_at_lead_one_order_the_rules(self):
        # strict <= randomised <= tie_counts at each level, since a tie is a hit under none, some or all draws.
        out = script.path_report(5, narrow=1.0, days=1000)
        for level in ("0.05", "0.95", "0.01", "0.99"):
            s, r, t = (out["hits"][rule][level] for rule in ("strict", "randomised", "tie_counts"))
            self.assertLessEqual(s[0], r[0])
            self.assertLessEqual(r[0], t[0])
            self.assertEqual(s[1], t[1])

    def test_a_path_is_reproducible(self):
        self.assertEqual(script.path_report(4, narrow=1.0, days=200), script.path_report(4, narrow=1.0, days=200))


class SummaryTests(unittest.TestCase):
    def test_wilson_on_hand_cases(self):
        lo, hi = script.wilson(0, 100)
        self.assertEqual(lo, 0.0)
        self.assertAlmostEqual(hi, 0.0370, places=3)
        lo, hi = script.wilson(50, 100)
        self.assertAlmostEqual(lo, 0.4038, places=3)
        self.assertAlmostEqual(hi, 0.5962, places=3)

    def test_a_rule_is_named_when_its_size_is_at_most_five_percent(self):
        size = {
            "strict": {"all": {"fails": 5, "paths": 100}},
            "tie_counts": {"all": {"fails": 60, "paths": 100}},
            "randomised": {"all": {"fails": 6, "paths": 100}},
        }
        self.assertEqual(script.rules_named(size), ["strict"])

    def test_nothing_is_named_when_every_rule_fails_too_often(self):
        size = {r: {"all": {"fails": 30, "paths": 100}} for r in ("strict", "tie_counts", "randomised")}
        self.assertEqual(script.rules_named(size), [])

    def test_the_declaration_is_the_scripts(self):
        decl = json.loads((ROOT / "metadata" / "coverage_size_1156.json").read_text(encoding="utf-8"))
        self.assertEqual(decl["directive"], 1156)
        self.assertEqual(decl["design"]["family"], "holm")
        self.assertEqual(decl["design"]["alpha"], 0.05)
        self.assertEqual(decl["design"]["method"], "thinned")
        self.assertEqual(tuple(decl["design"]["levels"]), sp.COVERAGE_LEVELS)
        self.assertEqual(sum(r["days"] for r in decl["world"]["regimes"]), decl["world"]["days"])
        self.assertEqual(script.DECLARATION["size"]["paths"], decl["size"]["paths"])


class PageTests(unittest.TestCase):
    RESULT = ROOT / "docs" / "research" / "coverage-size-1156" / "result.json"
    PAGE = ROOT / "docs" / "research" / "coverage-size-1156-result.md"

    def test_the_committed_page_is_what_the_committed_record_gives(self):
        if not self.RESULT.exists():
            self.skipTest("the record is not committed yet")
        record = json.loads(self.RESULT.read_text(encoding="utf-8"))
        self.assertEqual(script.render(record), self.PAGE.read_text(encoding="utf-8"))

    def test_the_record_keeps_the_requirement_off_and_names_its_rule_from_its_own_sizes(self):
        if not self.RESULT.exists():
            self.skipTest("the record is not committed yet")
        record = json.loads(self.RESULT.read_text(encoding="utf-8"))
        self.assertFalse(record["flag_in_tree"])
        self.assertEqual(record["rules_named"], script.rules_named(record["size"]))
        self.assertEqual(set(record["size"]), {"strict", "tie_counts", "randomised"})


if __name__ == "__main__":
    unittest.main()
