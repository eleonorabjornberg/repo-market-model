"""H1 (#922): the size of the B2 leg of "Supported" is measured on S(B2) - S(candidate), with B2 the benchmark.

`scoring_protocol.verdict` passes the leg against B2 when `against_b2.lower_bound(critical) > 0`, and a
`PairedTest` against B2 has d = S(B2) - S(candidate) (`sp.paired_test`'s orientation). The script draws windows from
that series, centred, and counts those whose studentized mean is above the critical value. These tests read the
orientation from `sp.paired_test` and require the script to change no decided value.

Recorded mutation (2026-10-19): in `scripts/b2_leg_size_922.py`, `leg_differences` returned
`[c - b for b, c in zip(b2, candidate)]` (the reversed sign) instead of `[b - c ...]`;
`test_leg_differences_follow_the_orientation_the_test_applies` raised AssertionError (the mean was minus the
test's). Not a leakage guard.
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
spec = importlib.util.spec_from_file_location("b2_leg_size_922", ROOT / "scripts" / "b2_leg_size_922.py")
script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script)


def scores(seed, shift=0.0, days=400):
    rng = random.Random(seed)
    return [1.0 + shift + rng.random() * rng.random() for _ in range(days)]


def as_dict(values):
    return {date(2001, 1, 1) + timedelta(days=i): v for i, v in enumerate(values)}


class TestB2LegSize(unittest.TestCase):
    def test_leg_differences_follow_the_orientation_the_test_applies(self):
        b2, candidate = scores(1, shift=0.4), scores(2)
        test = sp.paired_test(as_dict(b2), as_dict(candidate), seed=1, draws=50, with_skill=True)
        mean = sum(script.leg_differences(b2, candidate)) / len(b2)
        self.assertAlmostEqual(mean, test.mean_difference)

    def test_share_above_counts_windows_strictly_above(self):
        self.assertEqual(script.share_above([-1.0, 0.0, 1.0, 2.0], 1.0), 0.25)
        self.assertEqual(script.share_above([], 1.0), 0.0)

    def test_the_size_is_a_share_of_the_centred_windows(self):
        # a candidate that equals B2 up to noise has no skill: its windows are centred, so the share is near nominal
        b2 = scores(3)
        noise = random.Random(4)
        candidate = [x + noise.gauss(0, 0.05) for x in b2]
        size = script.leg_size(script.leg_differences(b2, candidate), days=125, critical=[1.645], windows=400, seed=1)
        self.assertLess(size[0], 0.2)

    def test_no_decided_value_moves(self):
        self.assertEqual(sp.CRITICAL_VALUES, CRITICAL_BEFORE)
        self.assertEqual(sp.FUTILITY_CRITICAL_VALUES, FUTILITY_BEFORE)


if __name__ == "__main__":
    unittest.main()
