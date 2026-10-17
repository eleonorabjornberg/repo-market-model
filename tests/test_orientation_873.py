"""H1 step 4 (#873): a critical or futility value is calibrated in the orientation the protocol applies.

`scoring_protocol` applies d = S(benchmark) - S(candidate), positive favouring the candidate, with B1 as the
benchmark in every comparison the verdict reads (§5). The calibrated values of PR #695 were computed on
S(B2) - S(B1), B2 playing the benchmark (#830). These tests read the orientation from `sp.paired_test` itself,
not from a constant, and require `scripts/protocol_coverage.py` to calibrate on what that orientation gives.

Recorded mutation (2026-10-17): in `scripts/protocol_coverage.py`, `candidate_differences` returned
`[c - b for b, c in zip(bench, candidate)]` (the reversed sign) instead of `[b - c ...]`;
`test_differences_follow_the_orientation_the_test_applies` raised AssertionError (the mean was minus the test's),
and so did the two tests that build the calibration series on it. Not a leakage guard.
"""

import importlib.util
import json
import random
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import scoring_protocol as sp

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("protocol_coverage_for_873", ROOT / "scripts" / "protocol_coverage.py")
pc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pc)

DAYS = 400


def scores(seed, shift=0.0):
    rng = random.Random(seed)
    return [1.0 + shift + rng.random() * rng.random() for _ in range(DAYS)]


def as_dict(values):
    return {date(2001, 1, 1) + timedelta(days=i): v for i, v in enumerate(values)}


class TestOrientation(unittest.TestCase):
    def setUp(self):
        self.b1 = scores(1, shift=0.4)
        self.b2 = scores(2)
        self.b3 = scores(3, shift=-0.1)

    def paired(self, bench, candidate):
        return sp.paired_test(as_dict(bench), as_dict(candidate), seed=1, draws=50, with_skill=True)

    def test_differences_follow_the_orientation_the_test_applies(self):
        test = self.paired(self.b1, self.b2)
        series = pc.candidate_differences(self.b1, self.b2)
        self.assertAlmostEqual(sum(series) / len(series), test.mean_difference, places=12)
        self.assertGreater(test.mean_difference, 0.0)

    def test_the_calibration_series_are_benchmark_minus_candidate(self):
        series = pc.calibration_series((self.b1, self.b2), (self.b1, self.b3))
        for comparison, candidate in ((sp.GRID_COMPARISON, self.b2), (sp.FIVE_LEVEL_COMPARISON, self.b3)):
            test = self.paired(self.b1, candidate)
            self.assertAlmostEqual(sum(series[comparison]) / DAYS, test.mean_difference, places=12)

    def test_the_futility_inputs_give_the_skill_the_test_computes(self):
        bench, differences = pc.futility_inputs(self.b1, self.b2)
        self.assertEqual(bench, self.b1)
        test = self.paired(self.b1, self.b2)
        self.assertAlmostEqual(sum(differences) / sum(bench), test.skill, places=12)

    def test_the_orientation_is_not_symmetric(self):
        """The skew of d is what makes the orientation matter: the reversed series has other quantiles."""

        forward = pc.candidate_differences(self.b1, self.b2)
        reverse = [-v for v in forward]
        a = sp.calibrate_critical_value(forward, days=125, level=0.05, windows=300, seed=1)
        b = sp.calibrate_critical_value(reverse, days=125, level=0.05, windows=300, seed=1)
        self.assertNotAlmostEqual(a, b, places=3)


class TestTheDraftRecord(unittest.TestCase):
    """`docs/research/protocol-calibration-873/result.json` is the scratch result the amendment draft carries."""

    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(pc.CALIBRATION_873.read_text(encoding="utf-8"))

    def test_the_record_names_the_orientation_and_the_windows_of_the_original(self):
        original = json.loads(pc.CALIBRATION.read_text(encoding="utf-8"))
        self.assertEqual(self.record["orientation"], "d = S(benchmark) - S(candidate), benchmark B1")
        for key in ("windows", "futility_windows", "window_block", "seed", "nominal_levels"):
            self.assertEqual(self.record[key], original[key], key)

    def test_the_new_values_are_the_previously_recorded_reversed_diagnostics(self):
        """The reversed series of the original record is the candidate orientation: same series, windows, seed."""

        original = json.loads(pc.CALIBRATION.read_text(encoding="utf-8"))
        grid = self.record["comparison_critical_values"][sp.GRID_COMPARISON]
        five = self.record["comparison_critical_values"][sp.FIVE_LEVEL_COMPARISON]
        for n in ("125", "250"):
            self.assertEqual(grid[n], original["critical_values"]["B1-B2 (reversed, diagnostic)"][n])
            self.assertEqual(five[n], original["critical_values"]["B1-B3 (reversed, diagnostic)"][n])
        self.assertIsNone(grid["60"])

    def test_the_in_force_values_are_untouched_until_the_amendment_is_merged(self):
        original = json.loads(pc.CALIBRATION.read_text(encoding="utf-8"))
        for comparison in (sp.GRID_COMPARISON, sp.FIVE_LEVEL_COMPARISON):
            for n in (125, 250):
                self.assertEqual(sp.CRITICAL_VALUES[comparison][n], original["comparison_critical_values"][comparison][str(n)])


if __name__ == "__main__":
    unittest.main()
