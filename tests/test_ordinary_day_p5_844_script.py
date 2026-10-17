"""The helpers of `scripts/ordinary_day_p5_844.py` (#844; H5 step 3, development tier).

Written after the script, which is measurement code; its one guard, `require_scored_days`, has a recorded mutation:
replacing `if day > last:` with `if day > last + timedelta(days=400):` made
`ScopeTests.test_a_day_after_the_declared_end_is_refused` fail with `AssertionError` ("LookAheadError not raised");
restored, it passes.
"""

from __future__ import annotations

import importlib.util
import json
import random
import unittest
from datetime import date
from pathlib import Path

from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("ordinary_day_p5_844", ROOT / "scripts" / "ordinary_day_p5_844.py")
script = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(script)


class ScopeTests(unittest.TestCase):

    def test_a_day_after_the_declared_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.require_scored_days([date(2025, 12, 31), date(2026, 1, 2)])

    def test_the_declared_last_day_is_scored(self):
        script.require_scored_days([date(2025, 12, 31)])

    def test_a_locked_day_is_refused_even_when_the_end_is_moved(self):
        with self.assertRaises(LookAheadError):
            script.require_scored_days([date(2026, 9, 4)], last=date(2027, 1, 1))

    def test_the_declaration_ends_where_the_script_does(self):
        declaration = json.loads((ROOT / "metadata" / "exploration_844.json").read_text())
        self.assertEqual(declaration["span"]["last_day"], script.LAST_DAY.isoformat())
        self.assertEqual(declaration["interval"]["replications"], script.REPLICATIONS)
        self.assertEqual(declaration["interval"]["block_length"], script.BLOCK)
        self.assertEqual(declaration["minimum_pressure_days"]["value"], script.MINIMUM_PRESSURE_DAYS)
        self.assertEqual(set(declaration["variants"]), set(script.MODEL_ROWS))


class AurocTests(unittest.TestCase):

    def test_a_perfect_ranking_is_one_and_a_reversed_one_zero(self):
        self.assertEqual(script.auroc([0.1, 0.2, 0.8, 0.9], [0, 0, 1, 1]), 1.0)
        self.assertEqual(script.auroc([0.9, 0.8, 0.2, 0.1], [0, 0, 1, 1]), 0.0)

    def test_ties_count_half(self):
        self.assertEqual(script.auroc([0.5, 0.5, 0.5, 0.5], [0, 1, 0, 1]), 0.5)

    def test_it_matches_the_pair_count(self):
        rng = random.Random(1)
        scores = [round(rng.random(), 1) for _ in range(60)]
        y = [1 if rng.random() < 0.3 else 0 for _ in scores]
        pairs = [(a, b) for a, ya in zip(scores, y) if ya for b, yb in zip(scores, y) if not yb]
        expected = sum(1.0 if a > b else 0.5 if a == b else 0.0 for a, b in pairs) / len(pairs)
        self.assertAlmostEqual(script.auroc(scores, y), expected, places=12)

    def test_it_is_undefined_without_both_kinds_of_day(self):
        self.assertIsNone(script.auroc([0.1, 0.2], [0, 0]))
        self.assertIsNone(script.auroc([0.1, 0.2], [1, 1]))


class CellTests(unittest.TestCase):

    def cell(self, n=300, informative=True, seed=3):
        rng = random.Random(seed)
        y = [1 if rng.random() < 0.15 else 0 for _ in range(n)]
        good = [min(0.99, max(0.01, 0.1 + 0.6 * v + 0.05 * rng.random())) for v in y]
        flat = [0.15 + 0.01 * rng.random() for _ in y]
        return y, {script.REFERENCE: flat, "row": good if informative else flat, script.RAW: [float(v) + rng.random() for v in y]}

    def test_an_informative_row_beats_the_reference_on_a_paired_interval(self):
        y, columns = self.cell()
        result = script.cell_result(columns, y, seed=1, replications=200)
        difference = result["rows"]["row"]["auroc_minus_reference"]
        self.assertGreater(difference["value"], 0.0)
        self.assertEqual(script.sign_of(difference), "above")

    def test_a_row_that_is_the_reference_has_a_zero_difference(self):
        y, columns = self.cell(informative=False)
        columns["row"] = list(columns[script.REFERENCE])
        result = script.cell_result(columns, y, seed=1, replications=100)
        self.assertEqual(result["rows"]["row"]["brier_minus_reference"]["value"], 0.0)
        self.assertEqual(result["rows"]["row"]["auroc_minus_reference"]["value"], 0.0)

    def test_fewer_than_three_pressure_days_report_no_event_metric(self):
        y, columns = self.cell(n=100)
        y = [0] * 98 + [1, 1]
        result = script.cell_result(columns, y, seed=1, replications=50)
        self.assertEqual(result["pressure_days"], 2)
        row = result["rows"]["row"]
        self.assertIsNone(row["auroc"]["value"])
        self.assertIsNone(row["slope"]["value"])
        self.assertIsNotNone(row["brier"]["value"])

    def test_the_seed_fixes_the_interval(self):
        y, columns = self.cell()
        a = script.cell_result(columns, y, seed=7, replications=60)
        b = script.cell_result(columns, y, seed=7, replications=60)
        self.assertEqual(a, b)

    def test_a_column_of_the_wrong_length_is_refused(self):
        y, columns = self.cell(n=50)
        columns["row"] = columns["row"][:-1]
        with self.assertRaises(ValueError):
            script.cell_result(columns, y, seed=1, replications=10)

    def test_the_raw_spread_has_an_auroc_and_no_calibration(self):
        y, columns = self.cell()
        row = script.cell_result(columns, y, seed=1, replications=30)["rows"][script.RAW]
        self.assertIn("auroc", row)
        self.assertNotIn("brier", row)


if __name__ == "__main__":
    unittest.main()
