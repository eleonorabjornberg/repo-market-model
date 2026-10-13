"""The helpers of `scripts/spread_mean_reversion_686.py` (#686; H5, development tier).

Written after the script, which is measurement code; its one guard, `require_scored_days`, has a recorded mutation:
replacing `if day > last:` with `if day > last + timedelta(days=400):` made
`ScopeTests.test_a_day_after_the_declared_end_is_refused` fail with `AssertionError` ("LookAheadError not raised");
restored, it passes.
"""

from __future__ import annotations

import importlib.util
import json
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import scoring_protocol as sp
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("spread_mean_reversion_686", ROOT / "scripts" / "spread_mean_reversion_686.py")
script = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(script)


class ScopeTests(unittest.TestCase):

    def test_a_day_after_the_declared_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.require_scored_days([date(2025, 12, 31), date(2026, 1, 2)])

    def test_the_declared_last_day_is_scored(self):
        script.require_scored_days([date(2025, 12, 31)])

    def test_a_locked_day_is_refused_even_when_the_end_is_moved(self):
        with self.assertRaises(LookAheadError):
            script.require_scored_days([date(2026, 9, 4)], last=date(2027, 1, 1))

    def test_the_declaration_ends_where_the_script_does(self):
        declaration = json.loads((ROOT / "metadata" / "spread_distribution_686.json").read_text())
        self.assertEqual(declaration["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(declaration["limits"]["max_variants"], len(declaration["variants"]))


class StatisticsTests(unittest.TestCase):

    def days(self, n):
        start = date(2020, 1, 1)
        return [start + timedelta(days=i) for i in range(n)]

    def test_interval_is_the_5th_and_95th_percentile(self):
        draws = [float(i) for i in range(101)]
        self.assertEqual(script.interval(draws), [5.0, 95.0])

    def test_a_better_candidate_has_positive_skill(self):
        days = self.days(80)
        bench = {d: 2.0 + 0.1 * (i % 5) for i, d in enumerate(days)}
        cand = {d: v - 0.5 - 0.05 * (i % 3) for i, (d, v) in enumerate(bench.items())}
        row = script.run_pairs({"B": bench}, cand, days, draws=300)["B"]
        self.assertGreater(row["skill"], 0.0)
        self.assertGreater(row["difference"], 0.5)
        self.assertGreater(row["skill_interval"][0], 0.0)

    def test_a_benchmark_that_scores_zero_has_undefined_skill_not_a_crash(self):
        days = self.days(40)
        row = script.run_pairs({"B": {d: 0.0 for d in days}}, {d: 0.0 for d in days}, days, draws=50)["B"]
        self.assertIn("undefined", row)
        self.assertEqual(script.skill_text(row), "undefined (benchmark scores 0)")

    def test_groups_keep_each_day_once(self):
        days = self.days(6)
        labels = {d: "a" if i % 2 else "b" for i, d in enumerate(days)}
        grouped = script.group_days(days, labels)
        self.assertEqual(sorted(sum(grouped.values(), [])), days)

    def test_the_five_levels_are_in_the_grid(self):
        self.assertEqual([sp.GRID[i] for i in script.FIVE_AT], list(script.FIVE))


if __name__ == "__main__":
    unittest.main()
