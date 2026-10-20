"""The randomised PIT beside the midpoint PIT (#970, H5 step 3): `scripts/randomised_pit_970.py`.

A whole-bp target has many ties, so the midpoint PIT of #707 puts a perfect forecast's cells at the bracket midpoints and
its share at or below 0.10 is not 0.10. The randomised PIT (Czado, Gneiting and Held, 2009) draws the value uniformly
inside the cell's level bracket and is uniform for a perfect forecast. The tests below fix the bracket, the draw and the
reading, and show both on a simulated perfect forecast of an integer outcome.

Recorded mutations (the guards this script adds):

* `refuse_locked`, the call `require_unlocked(list(days), ...)` replaced by `return`: `test_a_locked_day_is_refused`
  fails with `AssertionError` (`LookAheadError not raised`).
* `randomised_pit`, `lo + rng.random() * (hi - lo)` replaced by `(lo + hi) / 2.0` (the midpoint again):
  `test_a_perfect_forecast_of_an_integer_outcome_is_uniform_when_randomised` fails with `AssertionError` (`0.0 != 0.1 within 0.02 delta`: the
  share at or below 0.10 is 0 at the midpoints).
"""

from __future__ import annotations

import importlib.util
import random
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("randomised_pit_970_script", REPO / "scripts" / "randomised_pit_970.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

GRID = sp.GRID


def integer_law(probabilities):
    """The 23 quantiles of a law on the integers 0, 1, 2, ... with these probabilities."""

    out, cumulative = [], []
    total = 0.0
    for p in probabilities:
        total += p
        cumulative.append(total)
    for level in GRID:
        k = next(i for i, c in enumerate(cumulative) if c >= level - 1e-12)
        out.append(float(k))
    return out


class BracketTests(unittest.TestCase):
    def test_a_bracket_without_a_tie_is_the_midpoint_pits_bracket(self):
        law = [float(i) for i in range(len(GRID))]  # strictly increasing
        lo, hi = script.pit_bracket(law, 10.5)
        self.assertEqual((lo, hi), (GRID[10], GRID[11]))
        self.assertEqual((lo + hi) / 2.0, script.pit(law, 10.5))

    def test_a_tie_spans_the_levels_around_the_tied_ones(self):
        law = [0.0] * 5 + [1.0] * 13 + [2.0] * 5
        lo, hi = script.pit_bracket(law, 1.0)
        self.assertEqual((lo, hi), (GRID[4], GRID[18]))

    def test_an_outcome_beyond_the_grid_is_bracketed_by_the_ends(self):
        law = [float(i) for i in range(len(GRID))]
        self.assertEqual(script.pit_bracket(law, -5.0), (0.0, GRID[0]))
        self.assertEqual(script.pit_bracket(law, 99.0), (GRID[-1], 1.0))


class RandomisedTests(unittest.TestCase):
    def test_the_draw_lies_in_the_bracket_and_is_repeatable(self):
        law = [0.0] * 5 + [1.0] * 13 + [2.0] * 5
        draws = [script.randomised_pit(law, 1.0, random.Random(7)) for _ in range(2)]
        self.assertEqual(draws[0], draws[1])
        lo, hi = script.pit_bracket(law, 1.0)
        self.assertTrue(lo <= draws[0] <= hi)

    def test_a_perfect_forecast_of_an_integer_outcome_is_uniform_when_randomised(self):
        probabilities = [0.55, 0.25, 0.12, 0.05, 0.03]
        law = integer_law(probabilities)
        rng = random.Random(970)
        outcomes = rng.choices(range(len(probabilities)), weights=probabilities, k=20000)
        draw = random.Random(1)
        randomised = [script.randomised_pit(law, float(y), draw) for y in outcomes]
        midpoint = [script.pit(law, float(y)) for y in outcomes]
        low = sum(1 for p in randomised if p <= 0.10) / len(randomised)
        self.assertAlmostEqual(low, 0.10, delta=0.02)
        self.assertGreater(abs(sum(1 for p in midpoint if p <= 0.10) / len(midpoint) - 0.10), 0.05)

    def test_the_shares_are_the_six_bins_and_sum_to_one(self):
        calendar = [date(2024, 1, 1) + timedelta(days=i) for i in range(400)]
        law = integer_law([0.55, 0.25, 0.12, 0.05, 0.03])
        outcomes = random.Random(3).choices(range(5), weights=[0.55, 0.25, 0.12, 0.05, 0.03], k=399)
        cells = [script.Cell(calendar[i], calendar[i + 1], law, law, float(outcomes[i])) for i in range(399)]
        result = script.pit_shares(cells, seed=970)
        self.assertEqual(result["n"], 399)
        for key in ("midpoint", "randomised"):
            self.assertAlmostEqual(sum(result[key]), 1.0)
            self.assertEqual(len(result[key]), 6)
        self.assertEqual(result, script.pit_shares(cells, seed=970))


class GuardTests(unittest.TestCase):
    def test_a_locked_day_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.refuse_locked([date(2026, 9, 10)])

    def test_the_study_ends_on_the_last_day_before_the_lockbox(self):
        self.assertEqual(script.LAST_TARGET, date(2025, 12, 31))


if __name__ == "__main__":
    unittest.main()
