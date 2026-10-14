"""The tables of `scripts/reliability_regimes_683.py` (#683): what a reader sees when a regime has no slope.

Nothing here is a leakage guard, so no mutation record is required; the figures the script tabulates are read from tracked evidence.
"""

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _script():
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("reliability_regimes_683_script", ROOT / "scripts" / "reliability_regimes_683.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


S = _script()


def _cell(slope, pressure_days, days=100):
    return {"days": days, "pressure_days": pressure_days, "slope": slope}


class SlopeTextTests(unittest.TestCase):
    def test_a_regime_with_no_pressure_day_is_undefined_not_a_number(self):
        self.assertEqual(S._slope_text(_cell(None, 0)), "undefined")
        self.assertEqual(S._slope_text(_cell(0.7, 0)), "undefined")

    def test_a_missing_slope_with_pressure_days_is_a_dash(self):
        self.assertEqual(S._slope_text(_cell(None, 12)), "–")
        self.assertEqual(S._slope_text(None), "–")

    def test_a_near_separated_fit_is_called_unstable(self):
        self.assertEqual(S._slope_text(_cell(-99.35, 3)), "unstable")

    def test_a_cell_of_few_pressure_days_is_marked(self):
        self.assertEqual(S._slope_text(_cell(6.2, 3)), "6.20†")
        self.assertEqual(S._slope_text(_cell(0.48, 62)), "0.48")


class TrackedTextTests(unittest.TestCase):
    def test_the_pooled_column_comes_first_and_the_reading_is_restated(self):
        result = {
            "source": "x.json",
            "reading": S.READING,
            "rows": {"row": {"1": {
                "all": _cell(0.83, 82, 1469),
                "regime 2018-19": _cell(0.48, 62, 294),
                "regime 2021-23": _cell(None, 0, 586),
            }}},
        }
        text = S.tracked_text(result)
        self.assertIn("Pooled slopes mislead here", text)
        self.assertIn("| lead | all days (pooled) | regime 2018-19 | regime 2020 |", text)
        self.assertIn("| 1 | 0.83 | 0.48 | – | undefined |", text)
        self.assertIn("development, not a verdict".lower(), text.lower())


class RowCellsTests(unittest.TestCase):
    """`_run_rows` is the bootstrap of the `kinked` command, spread over processes (#753): the same cells, whatever the worker count."""

    def _jobs(self):
        import random

        rng = random.Random(7)
        days = 240
        jobs = []
        for key in ("a", "b", "c"):
            p = [min(0.95, max(0.02, rng.random() * 0.4)) for _ in range(days)]
            y = [1 if rng.random() < q * 1.2 else 0 for q in p]
            regime = ["regime 2018-19"] * 80 + ["regime 2020-24"] * 80 + ["regime 2025-26"] * 80
            state = ["scarcity state 0"] * 120 + ["scarcity state 1"] * 120
            jobs.append((key, p, y, regime, state, dict(block_length=2.0, seed=11, replications=40, level=0.9)))
        return jobs

    def test_the_cells_do_not_depend_on_the_number_of_workers(self):
        jobs = self._jobs()
        serial = S._run_rows(jobs, workers=1)
        self.assertEqual(list(serial), ["a", "b", "c"])
        self.assertEqual(serial, S._run_rows(jobs, workers=2))

    def test_each_row_has_a_pooled_cell_in_both_splits(self):
        rows = S._run_rows(self._jobs()[:1], workers=1)
        self.assertIn("pooled", rows["a"]["regime"])
        self.assertIn("pooled", rows["a"]["scarcity_state"])
        self.assertEqual(rows["a"]["regime"]["pooled"], rows["a"]["scarcity_state"]["pooled"])


if __name__ == "__main__":
    unittest.main()
