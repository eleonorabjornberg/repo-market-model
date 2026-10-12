"""The 2018-19 shortfall of `+tailcap75`, step 1 of #610: the later window, the floor's warm-up and the shortfall.

Recorded mutation, 12 October 2026, in a disposable copy of `scripts/tailcap_floor_610.py`: in `_training_days_at` the comparison `day <= train_end`
replaced by `day <= train_end + timedelta(days=5)` (a refit is credited with days it was not trained on).
`FloorWarmupTests.test_a_block_counts_only_the_days_it_trained_on` then fails with `AssertionError`.
"""

import importlib.util
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]


def _script():
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("tailcap_floor_610_script", ROOT / "scripts" / "tailcap_floor_610.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["tailcap_floor_610_script"] = module
    spec.loader.exec_module(module)
    return module


SCRIPT = _script()


def _days(n, start=date(2018, 1, 1)):
    return [start + timedelta(days=i) for i in range(n)]


class LaterWindowTests(unittest.TestCase):
    def test_the_stretch_scores_exactly_the_requested_days_up_to_the_last_day(self):
        rows = [SimpleNamespace(date=d) for d in _days(500)]
        last = rows[-1].date
        start = SCRIPT.later_window_start(rows, 100, last, 61)
        self.assertEqual(len(rows) - start - 61, 100)

    def test_a_panel_too_short_is_refused(self):
        rows = [SimpleNamespace(date=d) for d in _days(100)]
        with self.assertRaises(ValueError):
            SCRIPT.later_window_start(rows, 100, rows[-1].date, 61)

    def test_a_last_day_that_is_not_a_row_is_refused(self):
        rows = [SimpleNamespace(date=d) for d in _days(300)]
        with self.assertRaises(ValueError):
            SCRIPT.later_window_start(rows, 100, date(2030, 1, 1), 61)

    def test_the_slice_keeps_the_header_and_the_rows_from_the_first_day(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "a.csv"
            source.write_text("date,x\n2018-01-01,1\n2018-01-02,2\n2018-01-03,3\n", encoding="utf-8")
            target = Path(tmp) / "b.csv"
            self.assertEqual(SCRIPT.slice_rows_csv(source, target, date(2018, 1, 2)), 2)
            self.assertEqual(target.read_text(encoding="utf-8"), "date,x\n2018-01-02,2\n2018-01-03,3\n")


class ShortfallTests(unittest.TestCase):
    def test_realised_minus_predicted(self):
        self.assertAlmostEqual(SCRIPT.mean_shortfall([0.1, 0.1, 0.1, 0.1], [1, 0, 0, 0]), 0.25 - 0.1)

    def test_columns_of_different_lengths_are_refused(self):
        with self.assertRaises(ValueError):
            SCRIPT.mean_shortfall([0.1], [1, 0])

    def test_the_interval_brackets_the_point(self):
        p = [0.1] * 200
        y = [1 if i % 5 == 0 else 0 for i in range(200)]
        cell = SCRIPT.shortfall_cell(p, y, block_length=5, replications=200, seed=1)
        self.assertLessEqual(cell["lower"], cell["shortfall"])
        self.assertGreaterEqual(cell["upper"], cell["shortfall"])
        self.assertEqual(cell["pressure_days"], 40)

    def test_a_difference_of_two_equal_stretches_covers_zero(self):
        a = [0.2, -0.1] * 100
        point, lower, upper = SCRIPT.difference_interval(a, list(a), block_length=4, replications=300, seed=2)
        self.assertEqual(point, 0.0)
        self.assertLessEqual(lower, 0.0)
        self.assertGreaterEqual(upper, 0.0)


class FloorWarmupTests(unittest.TestCase):
    def _case(self, n=200, refit_every=21, first=61):
        panel = _days(n + first)
        scored = panel[first:]
        train_ends = []
        for k in range(len(scored)):
            block = k // refit_every
            train_ends.append(panel[first - 1 + block * refit_every])
        outcomes = [1 if k % 10 == 0 else 0 for k in range(len(scored))]
        forecasts = [0.0] * len(scored)
        off = [True] * len(scored)
        labels = ["unknown"] * len(scored)
        return panel, scored, train_ends, forecasts, outcomes, off, labels

    def test_no_floor_until_enough_earlier_off_risk_pairs(self):
        panel, scored, ends, f, y, off, labels = self._case()
        blocks = SCRIPT.floor_warmup_blocks(scored, ends, f, y, off, labels, panel)
        self.assertIsNone(blocks[0]["pooled_floor"])
        self.assertIsNone(blocks[1]["pooled_floor"])
        later = [b for b in blocks if b["earlier_off_risk_pairs"] >= 60]
        self.assertTrue(later)
        for b in later:
            self.assertIsNotNone(b["pooled_floor"])

    def test_a_block_counts_only_the_days_it_trained_on(self):
        panel, scored, ends, f, y, off, labels = self._case()
        blocks = SCRIPT.floor_warmup_blocks(scored, ends, f, y, off, labels, panel)
        for b in blocks:
            self.assertEqual(b["training_days"], sum(1 for d in panel if d <= date.fromisoformat(b["train_end"])))
        self.assertEqual(blocks[0]["training_days"], 61)

    def test_risk_dates_are_not_pairs_of_the_floor(self):
        panel, scored, ends, f, y, off, labels = self._case()
        off = [k % 2 == 0 for k in range(len(scored))]
        blocks = SCRIPT.floor_warmup_blocks(scored, ends, f, y, off, labels, panel)
        for b in blocks:
            self.assertLessEqual(b["earlier_off_risk_pairs"], sum(off))
        self.assertEqual(sum(b["off_risk_days"] for b in blocks), sum(off))


if __name__ == "__main__":
    unittest.main()
