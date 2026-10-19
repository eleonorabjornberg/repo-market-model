"""H1 (#929): each leg of "Supported" is calibrated in the orientation the test applies to it.

The leg against B1 has d = S(B1) - S(candidate) and the leg against B2 has d = S(B2) - S(candidate), B2 the benchmark
(`sp.paired_test`'s orientation). `scripts/per_leg_calibration_929.py` builds each from the day-aligned `S(B2) - S(B1)` and
`S(B2) - S(candidate)`; these tests read the orientation from `sp.paired_test` and require the script to change no decided
value. The verdict's use of a per-leg value is tested in `test_scoring_protocol.VerdictTests`.

Recorded mutation (2026-10-19): in `scripts/per_leg_calibration_929.py`, `leg_series` returned
`[b - c for b, c in zip(b2_minus_b1, b2_minus_candidate)]` (the reversed sign) for the leg against B1 instead of `[c - b ...]`;
`test_the_leg_against_b1_follows_the_orientation_the_test_applies` raised AssertionError (the mean was minus the test's).
Not a leakage guard.
"""

import copy
import importlib.util
import random
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import scoring_protocol as sp

ROOT = Path(__file__).resolve().parents[1]
CRITICAL_BEFORE = copy.deepcopy(sp.CRITICAL_VALUES)
FUTILITY_BEFORE = copy.deepcopy(sp.FUTILITY_CRITICAL_VALUES)
spec = importlib.util.spec_from_file_location("per_leg_calibration_929", ROOT / "scripts" / "per_leg_calibration_929.py")
script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script)


def scores(seed, shift=0.0, days=400):
    rng = random.Random(seed)
    return [1.0 + shift + rng.random() * rng.random() for _ in range(days)]


def as_dict(values):
    return {date(2001, 1, 1) + timedelta(days=i): v for i, v in enumerate(values)}


class TestPerLegCalibration(unittest.TestCase):
    def setUp(self):
        self.b1, self.b2, self.cand = scores(1), scores(2, shift=0.3), scores(3, shift=-0.1)
        self.b2_minus_b1 = [b - a for a, b in zip(self.b1, self.b2)]
        self.b2_minus_c = [b - c for b, c in zip(self.b2, self.cand)]

    def test_the_leg_against_b1_follows_the_orientation_the_test_applies(self):
        test = sp.paired_test(as_dict(self.b1), as_dict(self.cand), seed=1, draws=50, with_skill=True)
        d = script.leg_series(self.b2_minus_b1, self.b2_minus_c, "B1")
        self.assertAlmostEqual(sum(d) / len(d), test.mean_difference)

    def test_the_leg_against_b2_follows_the_orientation_the_test_applies(self):
        test = sp.paired_test(as_dict(self.b2), as_dict(self.cand), seed=1, draws=50, with_skill=True)
        d = script.leg_series(self.b2_minus_b1, self.b2_minus_c, "B2")
        self.assertAlmostEqual(sum(d) / len(d), test.mean_difference)

    def test_the_stand_ins_are_the_other_benchmark(self):
        # B2 standing in on the leg against B1: S(B2) - S(candidate) = 0 gives S(B1) - S(B2)
        zero = [0.0] * len(self.b1)
        self.assertEqual(script.leg_series(self.b2_minus_b1, zero, "B1"), [a - b for a, b in zip(self.b1, self.b2)])
        # B1 standing in on the leg against B2: S(B2) - S(B1)
        self.assertEqual(script.leg_series(self.b2_minus_b1, self.b2_minus_b1, "B2"), self.b2_minus_b1)

    def test_the_two_legs_differ_where_the_series_is_skewed(self):
        up = script.critical_value([-v for v in self.b2_minus_b1], days=125)
        down = script.critical_value(self.b2_minus_b1, days=125)
        self.assertNotAlmostEqual(up, down, places=3)

    def test_no_decided_value_moves(self):
        self.assertEqual(sp.CRITICAL_VALUES, CRITICAL_BEFORE)
        self.assertEqual(sp.FUTILITY_CRITICAL_VALUES, FUTILITY_BEFORE)
        self.assertEqual(sp.B2_LEG_CRITICAL_VALUES, {})


if __name__ == "__main__":
    unittest.main()
