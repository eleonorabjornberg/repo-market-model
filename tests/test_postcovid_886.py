"""H1 step 5 (#886): the critical and futility values are calibrated on post-2020 stationary-bootstrap paths.

`scripts/postcovid_886.py` calibrates on the post-2020 days only, with windows drawn by the stationary bootstrap of the
power study (mean block `scoring_protocol.BLOCK_LENGTH`), in the orientation the test applies, d = S(B1) - S(candidate)
(#830, #873). These tests pin the generator and the orientation; they do not read a result.

Recorded mutation (2026-10-17): in `scripts/postcovid_886.py`, `stationary_window_indices` returned
`sp._window_indices(size, days, rng, block)` (the protocol's circular blocks) instead of
`stationary_bootstrap_indices(size, block, rng)[:days]`; `test_the_windows_are_stationary_bootstrap_paths` raised
AssertionError (2 distinct run lengths, not more than 5: the fixed block repeats) and
`test_the_calibrated_value_depends_on_the_generator` raised RecursionError (the patched function called itself). Not a leakage guard.
"""

import importlib.util
import json
import random
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import scoring_protocol as sp

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("postcovid_886_script", ROOT / "scripts" / "postcovid_886.py")
pc6 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pc6)


def skewed(seed, n=400):
    rng = random.Random(seed)
    return [1.0 + rng.random() * rng.random() for _ in range(n)]


def calendar(n=400):
    return [date(2020, 3, 1) + timedelta(days=i) for i in range(n)]


class TestTheHistory(unittest.TestCase):
    def test_only_days_from_april_2020_are_kept_and_order_is_preserved(self):
        days = [date(2020, 3, 30) + timedelta(days=i) for i in range(10)]
        kept_days, kept = pc6.post_2020(days, list(range(10)))
        self.assertEqual(kept_days[0], date(2020, 4, 3))
        self.assertEqual(kept, [4, 5, 6, 7, 8, 9])

    def test_a_length_mismatch_is_refused(self):
        with self.assertRaises(ValueError):
            pc6.post_2020([date(2021, 1, 1)], [1.0, 2.0])


class TestTheGenerator(unittest.TestCase):
    def test_the_windows_are_stationary_bootstrap_paths(self):
        """A stationary path restarts at geometric lengths, so its runs of consecutive days are not all one length."""

        rng = random.Random(5)
        runs = set()
        for _ in range(200):
            index = pc6.stationary_window_indices(400, 250, rng, sp.WINDOW_BLOCK)
            self.assertEqual(len(index), 250)
            length = 1
            for a, b in zip(index, index[1:]):
                if b == (a + 1) % 400:
                    length += 1
                else:
                    runs.add(length)
                    length = 1
        self.assertGreater(len(runs), 5)
        self.assertNotEqual(runs, {sp.WINDOW_BLOCK})

    def test_the_generator_is_applied_only_inside_the_context(self):
        before = sp._window_indices
        with pc6.stationary_windows():
            self.assertIsNot(sp._window_indices, before)
        self.assertIs(sp._window_indices, before)

    def test_the_context_restores_the_generator_after_an_error(self):
        before = sp._window_indices
        with self.assertRaises(RuntimeError):
            with pc6.stationary_windows():
                raise RuntimeError("boom")
        self.assertIs(sp._window_indices, before)

    def test_the_calibrated_value_depends_on_the_generator(self):
        series = [a - b for a, b in zip(skewed(1), skewed(2))]
        circular = sp.calibrate_critical_value(series, days=125, level=0.05, windows=400, seed=1)
        with pc6.stationary_windows():
            stationary = sp.calibrate_critical_value(series, days=125, level=0.05, windows=400, seed=1)
        self.assertNotAlmostEqual(circular, stationary, places=6)


class TestTheOrientation(unittest.TestCase):
    def test_the_series_are_benchmark_minus_candidate_on_the_post_2020_days(self):
        days = calendar()
        b1, b2, b3 = skewed(1), skewed(2), skewed(3)
        series = pc6.calibration_series(days, (b1, b2), days, (b1, b3))
        kept = [i for i, d in enumerate(days) if d >= pc6.POST_2020_FIRST]
        for comparison, candidate in ((sp.GRID_COMPARISON, b2), (sp.FIVE_LEVEL_COMPARISON, b3)):
            self.assertEqual(series[comparison], [b1[i] - candidate[i] for i in kept])

    def test_the_orientation_is_the_one_the_test_applies(self):
        days = calendar()
        b1, b2 = skewed(1), skewed(2)
        test = sp.paired_test({d: v for d, v in zip(days, b1)}, {d: v for d, v in zip(days, b2)},
                              seed=1, draws=50, with_skill=True)
        series = pc6.calibration_series(days, (b1, b2), days, (b1, b2))[sp.GRID_COMPARISON]
        kept = [i for i, d in enumerate(days) if d >= pc6.POST_2020_FIRST]
        full = [b1[i] - b2[i] for i in range(len(days))]
        self.assertAlmostEqual(sum(full) / len(full), test.mean_difference, places=12)
        self.assertEqual(series, [full[i] for i in kept])

    def test_the_futility_inputs_are_the_benchmark_and_its_difference_on_the_same_days(self):
        days = calendar()
        b1, b2 = skewed(1), skewed(2)
        bench, differences = pc6.futility_inputs(days, (b1, b2))
        kept = [i for i, d in enumerate(days) if d >= pc6.POST_2020_FIRST]
        self.assertEqual(bench, [b1[i] for i in kept])
        self.assertEqual(differences, [b1[i] - b2[i] for i in kept])


class TestTheRecord(unittest.TestCase):
    """`docs/research/protocol-calibration-886/result.json` is a scratch result: nothing in force changes."""

    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(pc6.CALIBRATION_886.read_text(encoding="utf-8"))
        cls.draft = json.loads(pc6.CALIBRATION_873.read_text(encoding="utf-8"))

    def test_only_the_history_and_the_generator_differ_from_the_orientation_record(self):
        self.assertEqual(self.record["orientation"], self.draft["orientation"])
        for key in ("nominal_levels", "futility_windows", "seed", "futility_level"):
            self.assertEqual(self.record[key], self.draft[key], key)
        self.assertEqual(self.record["window_block"], sp.BLOCK_LENGTH)
        self.assertEqual(self.record["history_first_decision_day"], pc6.POST_2020_FIRST.isoformat())
        self.assertEqual(self.record["windows"], {"125": 20000, "250": 20000})

    def test_look_one_has_no_efficacy_value(self):
        for comparison in (sp.GRID_COMPARISON, sp.FIVE_LEVEL_COMPARISON):
            self.assertIsNone(self.record["comparison_critical_values"][comparison]["60"])

    def test_the_constants_in_force_are_untouched(self):
        original = json.loads(pc6.CALIBRATION.read_text(encoding="utf-8"))
        for comparison in (sp.GRID_COMPARISON, sp.FIVE_LEVEL_COMPARISON):
            for n in (125, 250):
                self.assertEqual(sp.CRITICAL_VALUES[comparison][n], original["comparison_critical_values"][comparison][str(n)])

    def test_the_records_and_the_page_agree(self):
        self.assertEqual(pc6.main(["check"]), 0)

    def test_the_value_in_the_draft_amendment_is_the_records(self):
        text = (ROOT / "docs" / "decisions" / "scoring-protocol.md").read_text(encoding="utf-8")
        grid = self.record["comparison_critical_values"][sp.GRID_COMPARISON]
        self.assertIn(f"| 125 | {self.draft['comparison_critical_values'][sp.GRID_COMPARISON]['125']:.3f} | {grid['125']:.3f} |", text)
        self.assertIn(f"| 250 | {self.draft['comparison_critical_values'][sp.GRID_COMPARISON]['250']:.3f} | {grid['250']:.3f} |", text)


if __name__ == "__main__":
    unittest.main()
