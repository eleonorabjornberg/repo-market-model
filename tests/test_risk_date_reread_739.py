"""The studentized re-read of H6 step 1 (`scripts/risk_date_reread_739.py`, #739; H6 step 1, development tier).

Eleonora's ruling on #739 (14 October 2026): development kill rules are read on the studentized bootstrap of protocol
ruling 1, not on the plain percentile interval of the draws. These tests pin that reading and were written first: they
failed with `FileNotFoundError` before the script existed. Recorded mutation: replacing `skill_t_draws` with
`skill_draws` in `studentized_skill_interval` (and so reading the percentile of unstudentized skill) made
`StudentizedIntervalTests.test_the_interval_is_the_studentized_one` fail with `AssertionError`; restored, it passes.
"""

from __future__ import annotations

import importlib.util
import random
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import scoring_protocol as sp

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("risk_date_reread_739", ROOT / "scripts" / "risk_date_reread_739.py")
script = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(script)


def _pair(seed: int = 5, n: int = 80, edge: float = 0.05):
    rng = random.Random(seed)
    days = [date(2024, 1, 1) + timedelta(days=i) for i in range(n)]
    bench = {d: 3.0 + rng.random() for d in days}
    cand = {d: bench[d] - edge + 0.5 * (rng.random() - 0.5) for d in days}
    return bench, cand


class StudentizedIntervalTests(unittest.TestCase):

    def setUp(self):
        bench, cand = _pair()
        (self.test,) = sp.paired_tests([(bench, cand)], seed=739, draws=400)

    def test_the_interval_is_the_studentized_one(self):
        low, high = script.studentized_skill_interval(self.test)
        t = self.test.skill_t_draws
        se = self.test.skill_standard_error
        self.assertAlmostEqual(low, self.test.skill - sp._quantile(t, 0.95) * se)
        self.assertAlmostEqual(high, self.test.skill - sp._quantile(t, 0.05) * se)
        self.assertLess(low, self.test.skill)
        self.assertGreater(high, self.test.skill)

    def test_it_differs_from_the_percentile_interval(self):
        low, _ = script.studentized_skill_interval(self.test)
        percentile = sp._quantile(self.test.skill_draws, 0.05)
        self.assertNotAlmostEqual(low, percentile)

    def test_skill_needs_the_lower_bound_above_zero(self):
        self.assertTrue(script.has_skill({"skill_interval": [0.001, 0.1]}))
        self.assertFalse(script.has_skill({"skill_interval": [-0.0066, 0.1]}))
        self.assertFalse(script.has_skill({"undefined": "x", "skill_interval": [0.1, 0.2]}))


class KillRuleTests(unittest.TestCase):

    def _vs(self, low_b1, low_cal):
        row = lambda low: {"skill_interval": [low, low + 0.1]}
        return {c: {"B1": row(low_b1), "calendar": row(low_cal)} for c in script.CANDIDATES}

    def test_a_candidate_with_skill_against_one_benchmark_only_is_killed_on_the_declared_rule(self):
        primary = {"grid_crps": {"vs": self._vs(-0.0066, 0.14)}, "mae": {"vs": self._vs(-0.03, 0.1)}}
        rule = script.kill_rule(primary)
        self.assertTrue(rule["killed"])
        self.assertFalse(rule["killed_on_the_weaker_reading"])

    def test_skill_against_both_on_one_metric_stands(self):
        primary = {"grid_crps": {"vs": self._vs(0.01, 0.14)}, "mae": {"vs": self._vs(-0.03, 0.1)}}
        self.assertFalse(script.kill_rule(primary)["killed"])


if __name__ == "__main__":
    unittest.main()
