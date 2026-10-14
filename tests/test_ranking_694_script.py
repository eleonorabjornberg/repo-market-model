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

    def test_the_block_length_is_the_one_asked_for_and_defaults_to_the_declared_20(self):
        """Directive #694, ruling of 13 October 2026, item 2: the protocol's block of 10 is reported as a sensitivity."""
        days = self.days(60)
        bench = {d: 0.3 for d in days}
        cand = {d: 0.4 + 0.01 * (i % 7) for i, d in enumerate(days)}
        seen = []
        real = script.sp.paired_tests

        def spy(*args, **kwargs):
            seen.append(kwargs["block_length"])
            return real(*args, **kwargs)

        script.sp.paired_tests = spy
        try:
            script.paired({"B": bench}, cand, days, draws=50)
            script.paired({"B": bench}, cand, days, draws=50, block=10.0)
        finally:
            script.sp.paired_tests = real
        self.assertEqual(seen, [20.0, 10.0])
        self.assertEqual(script.BLOCK, 20.0)
        self.assertEqual(script.SENSITIVITY_BLOCK, 10.0)

    def test_a_group_the_scorer_cannot_studentize_keeps_its_percentile_interval(self):
        """Main's `paired_tests` studentizes every resample and raises when one has no long-run variance (a group where
        the two rankers score alike on almost every day: a year with no pressure day, a few differing days). The gain and its
        percentile interval do not need the studentization, so they are computed from the same draws without it."""
        days = self.days(40)
        same = {d: 0.0 for d in days}
        row = script.paired({"B": same}, dict(same), days, draws=50)["B"]
        self.assertEqual(row["gain"], 0.0)
        self.assertEqual(row["gain_interval"], [0.0, 0.0])
        sparse = dict(same)
        sparse[days[3]] = 1.0
        row = script.paired({"B": same}, sparse, days, draws=400)["B"]
        self.assertAlmostEqual(row["gain"], 1.0 / 40)
        self.assertLessEqual(row["gain_interval"][0], row["gain"])
        self.assertGreaterEqual(row["gain_interval"][1], row["gain"])

    def test_the_fallback_draws_are_the_scorers_draws(self):
        days = self.days(60)
        bench = {d: 0.2 + 0.05 * (i % 4) for i, d in enumerate(days)}
        cand = {d: v + 0.1 * (i % 3) for i, (d, v) in enumerate(bench.items())}
        by_scorer = script.paired({"B": bench}, cand, days, draws=300)["B"]
        pairs = [({d: 1.0 - bench[d] for d in days}, {d: 1.0 - cand[d] for d in days})]
        by_fallback = script.percentile_gains(pairs, draws=300, block=script.BLOCK)[0]
        self.assertEqual(by_scorer["gain_interval"], script.interval(by_fallback))

    def test_the_interval_is_the_5th_and_95th_percentile(self):
        self.assertEqual(script.interval([float(i) for i in range(101)]), [5.0, 95.0])

    def test_a_perfect_benchmark_has_no_skill_to_divide_by(self):
        days = self.days(40)
        row = script.paired({"B": {d: 1.0 for d in days}}, {d: 0.5 for d in days}, days, draws=50)["B"]
        self.assertIn("undefined", row)


if __name__ == "__main__":
    unittest.main()
