"""The three scripts' `reliability` helpers are thin wrappers on `repo_model.reliability_regimes.fit` (#725, finding from #683).

Nothing here is a leakage guard, so no mutation record is required. The scripts differed in clipping, ridge, damping and the order of the
`(slope, intercept)` pair; the shared fit is the one definition, and each script keeps only its own return order.
"""

import importlib.util
import math
import random
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from repo_model import reliability_regimes  # noqa: E402


def _script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


OFF_RISK = _script("off_risk_day_624")
KINKED = _script("kinked_626")
SPREAD = _script("spread_distribution_632")


def _samples():
    rng = random.Random(725)
    for n, scale, shift in ((60, 1.0, 0.0), (250, 2.0, 0.5), (500, 0.4, -1.0), (2000, 1.0, 0.0)):
        z = [rng.uniform(-6.0, 1.0) for _ in range(n)]
        y = [1 if rng.random() < 1.0 / (1.0 + math.exp(-(scale * v + shift))) else 0 for v in z]
        yield [1.0 / (1.0 + math.exp(-v)) for v in z], y


class SharedReliabilityTests(unittest.TestCase):
    def test_each_script_returns_the_shared_fit_in_its_own_order(self):
        for p, y in _samples():
            shared = reliability_regimes.fit(p, y)
            self.assertIsNotNone(shared)
            self.assertEqual(OFF_RISK.reliability(p, y), (shared.intercept, shared.slope))
            self.assertEqual(KINKED.reliability(p, y), (shared.intercept, shared.slope))
            self.assertEqual(SPREAD.reliability(p, y), (shared.slope, shared.intercept))

    def test_an_unidentified_fit_is_none_in_all_three(self):
        for p, y in (([0.2, 0.2, 0.2, 0.2], [0, 1, 0, 1]), ([0.1, 0.2, 0.3], [0, 0, 0]), ([0.1, 0.2, 0.3], [1, 1, 1]), ([], [])):
            self.assertIsNone(OFF_RISK.reliability(p, y))
            self.assertIsNone(KINKED.reliability(p, y))
            self.assertIsNone(SPREAD.reliability(p, y))


if __name__ == "__main__":
    unittest.main()
