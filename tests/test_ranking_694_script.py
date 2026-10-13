"""The helpers of `scripts/ranking_694.py` (#694; H8, development tier).

Written after the script, which is measurement code; its guards are in `repo_model.ranking` (tests/test_ranking.py).
"""

from __future__ import annotations

import importlib.util
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("ranking_694", ROOT / "scripts" / "ranking_694.py")
script = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(script)


class PairedTests(unittest.TestCase):

    def days(self, n):
        start = date(2020, 1, 1)
        return [start + timedelta(days=i) for i in range(n)]

    def test_a_better_ranker_has_a_positive_gain_in_the_metric(self):
        days = self.days(80)
        bench = {d: 0.2 + 0.05 * (i % 4) for i, d in enumerate(days)}
        cand = {d: v + 0.1 for d, v in bench.items()}
        row = script.paired({"B": bench}, cand, days, draws=300)["B"]
        self.assertAlmostEqual(row["gain"], 0.1)
        self.assertAlmostEqual(row["candidate_mean"] - row["benchmark_mean"], 0.1)
        self.assertGreater(row["gain_interval"][0], 0.0)

    def test_the_interval_is_the_5th_and_95th_percentile(self):
        self.assertEqual(script.interval([float(i) for i in range(101)]), [5.0, 95.0])

    def test_a_perfect_benchmark_has_no_skill_to_divide_by(self):
        days = self.days(40)
        row = script.paired({"B": {d: 1.0 for d in days}}, {d: 0.5 for d in days}, days, draws=50)["B"]
        self.assertIn("undefined", row)


if __name__ == "__main__":
    unittest.main()
