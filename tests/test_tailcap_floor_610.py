"""The 2018-19 shortfall of `+tailcap75` (step 1 of #610) and the three floors on it (step 2): the later window, the floor's warm-up and the shortfall.

Step 1's readers were written before their tests (the tests passed at once; the mutation below is what shows they bite). The recent floor's
tests were written first and failed with `AttributeError` before the function existed.

Recorded mutation, 12 October 2026, in a disposable copy of `scripts/tailcap_floor_610.py`: in `_training_days_at` the comparison `day <= train_end`
replaced by `day <= train_end + timedelta(days=5)` (a refit is credited with days it was not trained on).
`FloorWarmupTests.test_a_block_counts_only_the_days_it_trained_on` then fails with `AssertionError`.

Recorded mutation, 12 October 2026, in `walk_forward_recent_floor`: the line `past = [i for i in pc.past_positions(scored_dates, train_ends, start) if off_risk[i]]`
replaced by `past = [i for i in range(start) if off_risk[i]]` (a block reads pairs whose outcome is not yet observable at its fit).
`RecentFloorTests.test_the_block_reads_only_pairs_observable_at_its_fit` then errors with `LookAheadError` raised by `group_calibration.require_observable`.
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
        self.assertEqual(len(rows) - start - 61 - 1, 100)

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


class RecentFloorTests(unittest.TestCase):
    """Variant (c): the floor is the rate over the most recent `window` earlier observable off-risk days."""

    def _case(self, outcomes, refit_every=21, first=61, off=None):
        panel = _days(len(outcomes) + first)
        scored = panel[first:]
        ends = [panel[first - 1 + (k // refit_every) * refit_every] for k in range(len(scored))]
        return scored, ends, [0.0] * len(scored), list(outcomes), off if off is not None else [True] * len(scored)

    def test_the_floor_is_the_rate_over_the_most_recent_window_only(self):
        # 120 quiet days, then 120 days all pressure: a pooled rate would be at most 0.5; the recent rate reaches 1
        scored, ends, f, y, off = self._case([0] * 120 + [1] * 120)
        column = SCRIPT.walk_forward_recent_floor(f, y, scored, ends, off, window=60)
        self.assertEqual(column[-1], 1.0)
        pooled = SCRIPT.gc.walk_forward_floor(f, y, scored, ends, off)
        self.assertLess(pooled[-1], 1.0)

    def test_nothing_is_floored_before_a_full_window_of_earlier_days(self):
        scored, ends, f, y, off = self._case([1] * 200)
        column = SCRIPT.walk_forward_recent_floor(f, y, scored, ends, off, window=60)
        self.assertEqual(column[:60], tuple([0.0] * 60))
        self.assertGreater(column[-1], 0.0)

    def test_a_risk_date_keeps_its_forecast_and_is_not_a_pair(self):
        scored, ends, f, y, off = self._case([1] * 200, off=[k % 2 == 0 for k in range(200)])
        f = [0.3] * 200
        column = SCRIPT.walk_forward_recent_floor(f, y, scored, ends, off, window=20)
        for k in range(200):
            if not off[k]:
                self.assertEqual(column[k], 0.3)

    def test_a_forecast_is_raised_never_lowered(self):
        scored, ends, f, y, off = self._case([0] * 200)
        f = [0.4] * 200
        column = SCRIPT.walk_forward_recent_floor(f, y, scored, ends, off, window=20)
        self.assertEqual(set(column), {0.4})

    def test_columns_of_different_lengths_are_refused(self):
        scored, ends, f, y, off = self._case([0] * 100)
        with self.assertRaises(ValueError):
            SCRIPT.walk_forward_recent_floor(f[:-1], y, scored, ends, off, window=20)

    def test_the_block_reads_only_pairs_observable_at_its_fit(self):
        # the outcomes of the last days before a refit are not yet observable (their labels end after the training end)
        scored, ends, f, y, off = self._case([0] * 100 + [1] * 100)
        ends = [min(end, scored[(k // 21) * 21] - timedelta(days=3)) for k, end in enumerate(ends)]
        column = SCRIPT.walk_forward_recent_floor(f, y, scored, ends, off, window=20)
        for start, stop, end in SCRIPT.pc.blocks(scored, ends):
            observable = [i for i in SCRIPT.pc.past_positions(scored, ends, start) if off[i]]
            if len(observable) >= 20:
                expected = sum(y[i] for i in observable[-20:]) / 20
                self.assertEqual(column[start], max(f[start], expected))


class DeclarationTests(unittest.TestCase):
    DECLARED = __import__("json").loads((ROOT / "metadata" / "tailcap_floor_610.json").read_text())

    def test_the_declaration_is_what_the_script_declares(self):
        self.assertEqual(SCRIPT.declaration_document(), self.DECLARED)

    def test_three_variants_on_tailcap75_and_no_more(self):
        self.assertEqual(list(self.DECLARED["variants"]), list(SCRIPT.VARIANT_NAMES.values()))
        self.assertEqual(len(self.DECLARED["variants"]), 3)
        for name in SCRIPT.VARIANT_NAMES.values():
            self.assertTrue(name.startswith(SCRIPT.BEST + "+"))

    def test_the_candidate_files_are_what_the_script_declares(self):
        candidates = ROOT / "metadata" / "pressure_judge" / "candidates"
        for name, entry in SCRIPT.candidate_entries().items():
            self.assertEqual(__import__("json").loads((candidates / f"{name}.json").read_text()), entry)
            self.assertEqual(entry["parent"], SCRIPT.BEST)

    def test_the_window_is_the_minimum_of_pairs_not_a_searched_value(self):
        self.assertEqual(self.DECLARED["constants"]["recent_window"], SCRIPT.gc.GROUP_MINIMUM_PAIRS)
        self.assertEqual(self.DECLARED["constants"]["searched"], "none")

    def test_the_scoring_ends_before_the_lockbox_and_nothing_is_published(self):
        self.assertLess(self.DECLARED["scoring"]["last_day"], "2026-01-01")
        self.assertIn("nothing", self.DECLARED["published"])

    def test_step_one_is_committed_before_the_declaration(self):
        self.assertTrue(SCRIPT.STEP_ONE.exists())


if __name__ == "__main__":
    unittest.main()
