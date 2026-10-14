"""`scripts/backfill_spread_633.py` keeps the percentile figures it was committed with (#655, #633).

As for #639's script (`test_richer_targets_639_script.py`): PR #695 made `PairedTest.lower_mean_difference()`
and `p_value` the studentized ones, and #633's committed figures were made on the percentile bootstrap
of PR #660 (the 5% quantile of the resampled mean differences, and the share of them at or below zero).
The script is pinned to those, so a rerun of #633 reproduces its figures.
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
    spec = importlib.util.spec_from_file_location("backfill_spread_633_test", ROOT / "scripts" / "backfill_spread_633.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PercentileFiguresTests(unittest.TestCase):
    def test_the_paired_cell_reads_the_percentile_bound_and_p_value(self):
        script = _script()
        rng = random.Random(3)
        days = [date(2019, 1, 1) + timedelta(days=k) for k in range(80)]
        bench = {day: 2.0 + rng.random() for day in days}
        cand = {day: bench[day] - 0.05 + 0.3 * rng.gauss(0, 1) for day in days}
        test = sp.paired_test(bench, cand, seed=7, draws=1000)
        cell = script.paired_cell(test)
        self.assertEqual(cell["lower_95_one_sided"], _quantile(test.mean_difference_draws, 0.05))
        self.assertEqual(cell["p_value"], sum(1 for v in test.mean_difference_draws if v <= 0.0) / test.draws)
        self.assertNotEqual(cell["lower_95_one_sided"], test.lower_mean_difference())


if __name__ == "__main__":
    unittest.main()
