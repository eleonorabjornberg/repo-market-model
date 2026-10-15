"""`scripts/richer_targets_639.py` keeps the percentile figures it was committed with (#655, #639).

PR #695 replaced the protocol's percentile bootstrap bound with the studentized one, so
`PairedTest.lower_mean_difference()` and `p_value` changed meaning under #639's script. Its committed
figures were made on the percentile bootstrap of PR #660: the one-sided 95% lower bound was the 5%
quantile of the resampled mean differences, and the p-value the share of them at or below zero. The
script is pinned to those, so a rerun of #639 reproduces its figures.
"""

from __future__ import annotations

import importlib.util
import random
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import scoring_protocol as sp
from repo_model.metrics import _quantile

ROOT = Path(__file__).resolve().parents[1]


def _script():
    spec = importlib.util.spec_from_file_location("richer_targets_639_test", ROOT / "scripts" / "richer_targets_639.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PercentileFiguresTests(unittest.TestCase):
    def test_the_skill_cell_reads_the_percentile_bound_and_p_value(self):
        script = _script()
        rng = random.Random(3)
        days = [date(2019, 1, 1) + timedelta(days=k) for k in range(80)]
        b2 = [2.0 + rng.random() for _ in days]
        b1 = [x - 0.05 + 0.3 * rng.gauss(0, 1) for x in b2]
        cell = script._skill_cell(b1, b2, days, seed=7)
        test = sp.paired_test(dict(zip(days, b2)), dict(zip(days, b1)), seed=7)
        self.assertEqual(cell["lower_mean_difference"], _quantile(test.mean_difference_draws, 0.05))
        self.assertEqual(
            cell["p_value"], sum(1 for value in test.mean_difference_draws if value <= 0.0) / test.draws
        )
        self.assertNotEqual(cell["lower_mean_difference"], test.lower_mean_difference())


if __name__ == "__main__":
    unittest.main()
