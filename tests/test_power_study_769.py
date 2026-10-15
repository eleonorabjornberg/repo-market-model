"""Power study of the test in force (#769): `scripts/power_study_769.py`, rule `docs/research/power-study-769.md`.

The study's result is `docs/research/power-study-769/result.json`; `check` refuses it if it was made under another text
of the rule or other critical values than `scoring_protocol`'s. Not a leakage guard (it reads series the other studies
already build), so no recorded mutation is required.
"""

import importlib.util
import random
import unittest
from pathlib import Path

from repo_model import scoring_protocol as sp

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("power_study_769_script", ROOT / "scripts" / "power_study_769.py")
ps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ps)


def series(n=400, seed=3):
    rng = random.Random(seed)
    s1 = [1.0 + rng.random() for _ in range(n)]
    s2 = [1.0 + rng.random() for _ in range(n)]
    return s1, s2


class TestInForce(unittest.TestCase):
    def test_critical_values_are_the_protocols_own(self):
        self.assertEqual(ps.critical_values(), {n: sp.CRITICAL_VALUES[sp.GRID_COMPARISON][n] for n in (125, 250)})

    def test_a_huge_true_skill_is_always_detected_and_a_null_rarely(self):
        s1, s2 = series()
        big = ps.detections(s1, s2, delta=0.9, noise=0.0, generator="circular", paths=20, seed=1)
        self.assertEqual(big["gated"]["250"], 1.0)
        null = ps.detections(s1, s2, delta=0.0, noise=1.0, generator="circular", paths=60, seed=1)
        self.assertLess(null["ungated"]["250"], 0.3)

    def test_gated_never_exceeds_ungated(self):
        s1, s2 = series()
        got = ps.detections(s1, s2, delta=0.03, noise=1.0, generator="stationary", paths=40, seed=2)
        for n in ("125", "250"):
            self.assertLessEqual(got["gated"][n], got["ungated"][n])

    def test_days_needed(self):
        self.assertEqual(ps.days_needed({"125": 0.8, "250": 0.9}), 125)
        self.assertEqual(ps.days_needed({"125": 0.1, "250": 0.85}), 250)
        self.assertIsNone(ps.days_needed({"125": 0.1, "250": 0.5}))


if __name__ == "__main__":
    unittest.main()
