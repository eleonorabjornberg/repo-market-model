"""The randomised PIT for a whole-basis-point outcome (#1072, H5 step 3): `scripts/integer_pit_1072.py`.

The outcome is a whole number of basis points. The PIT of #970 draws inside the bracket of grid levels around the outcome `y`, so it differs from the
midpoint PIT only when a quantile ties `y` exactly (finding #1069). The proper randomised PIT for an integer-valued outcome (Czado, Gneiting and Held,
2009) treats the law as a forecast of the rounded value and draws uniformly in `(F(y - 1/2), F(y + 1/2))`. The tests below pin the law's distribution
function read off the 23 quantiles, the draw, and the case of finding #1069: a law narrower than one basis point lying entirely in `(y, y + 1/2]`, to
which the version of #970 gives a PIT of about 0 and the proper one a uniform draw.

Recorded mutations (the guards this script adds):

* `refuse_locked`, the call `require_unlocked(list(days), ...)` replaced by `return`: `test_a_locked_day_is_refused` fails with `AssertionError`
  (`LookAheadError not raised`).
* `integer_pit_bounds`, the upper end `cdf(law, outcome + 0.5)` replaced by `cdf(law, outcome)` (the bin's upper edge moved to the integer itself):
  `test_a_law_narrower_than_a_basis_point_inside_the_rounded_bin_is_uniform` fails with `AssertionError` (`Tuples differ: (0.0, 0.0) != (0.0, 1.0)`: the
  bounds come out `(0, 0)` instead of `(0, 1)`).
* `read_share` is the reading rule of #970 reused unchanged; its tests are `test_the_reading_rule_is_970s`.
"""

from __future__ import annotations

import importlib.util
import random
import statistics
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("integer_pit_1072_script", REPO / "scripts" / "integer_pit_1072.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

GRID = sp.GRID


def normal_law(mean: float, sd: float):
    dist = statistics.NormalDist(mean, sd)
    return [dist.inv_cdf(level) for level in GRID]


class CdfTests(unittest.TestCase):
    def test_the_distribution_function_is_read_off_the_grid(self):
        law = [float(i) for i in range(len(GRID))]  # strictly increasing: quantile i is i
        self.assertEqual(script.cdf(law, -0.1), 0.0)
        self.assertEqual(script.cdf(law, 0.0), GRID[0])  # the tail mass sits at the first quantile
        self.assertAlmostEqual(script.cdf(law, 10.5), (GRID[10] + GRID[11]) / 2.0)
        self.assertEqual(script.cdf(law, 22.0), 1.0)  # and the upper tail mass at the last
        self.assertEqual(script.cdf(law, 99.0), 1.0)

    def test_a_tie_takes_the_largest_level_of_the_tied_quantiles(self):
        law = [0.0] * 5 + [1.0] * 13 + [2.0] * 5
        self.assertEqual(script.cdf(law, 0.0), GRID[4])
        self.assertEqual(script.cdf(law, 1.0), GRID[17])
        self.assertAlmostEqual(script.cdf(law, 0.999), GRID[4] + (GRID[5] - GRID[4]) * 0.999)  # and rises linearly to the next level

    def test_the_distribution_function_never_decreases(self):
        law = normal_law(0.3, 0.7)
        xs = [-3 + 0.05 * i for i in range(140)]
        values = [script.cdf(law, x) for x in xs]
        self.assertEqual(values, sorted(values))


class BoundsTests(unittest.TestCase):
    def test_a_law_narrower_than_a_basis_point_inside_the_rounded_bin_is_uniform(self):
        y = 3.0
        law = [y + 0.1 + 0.3 * i / (len(GRID) - 1) for i in range(len(GRID))]  # entirely inside (y, y + 1/2]
        self.assertEqual(script.integer_pit_bounds(law, y), (0.0, 1.0))
        draws = [script.integer_pit(law, y, random.Random(s)) for s in range(2000)]
        self.assertAlmostEqual(statistics.mean(draws), 0.5, delta=0.03)
        self.assertAlmostEqual(sum(1 for d in draws if d <= 0.10) / len(draws), 0.10, delta=0.03)

    def test_the_version_of_970_gives_that_law_a_pit_of_about_zero(self):
        y = 3.0
        law = [y + 0.1 + 0.3 * i / (len(GRID) - 1) for i in range(len(GRID))]
        old = [script.randomised_pit_970(law, y, random.Random(s)) for s in range(500)]
        self.assertLess(max(old), GRID[0])

    def test_a_wide_law_keeps_the_bounds_inside_the_unit_interval_and_ordered(self):
        law = normal_law(0.0, 5.0)
        for y in (-12.0, -3.0, 0.0, 4.0, 15.0):
            lo, hi = script.integer_pit_bounds(law, y)
            self.assertTrue(0.0 <= lo <= hi <= 1.0)


class UniformityTests(unittest.TestCase):
    def test_a_perfect_forecast_of_a_rounded_outcome_is_uniform_and_the_old_draw_is_not(self):
        mean, sd = 0.2, 0.3  # most of the mass rounds to 0; the law is far narrower than a basis point
        law = normal_law(mean, sd)
        dist = statistics.NormalDist(mean, sd)
        gen = random.Random(1072)
        outcomes = [float(round(dist.inv_cdf(min(max(gen.random(), 1e-9), 1 - 1e-9)))) for _ in range(20000)]
        proper = [script.integer_pit(law, y, gen) for y in outcomes]
        old = [script.randomised_pit_970(law, y, gen) for y in outcomes]
        low = lambda xs: sum(1 for p in xs if p <= 0.10) / len(xs)  # noqa: E731
        self.assertAlmostEqual(low(proper), 0.10, delta=0.03)
        self.assertAlmostEqual(low(proper) + (1 - sum(1 for p in proper if p <= 0.90) / len(proper)), 0.20, delta=0.05)
        self.assertGreater(abs(low(old) - 0.10), 0.05)


class SharesTests(unittest.TestCase):
    def cells(self, n=300):
        calendar = [date(2024, 1, 1) + timedelta(days=i) for i in range(n + 1)]
        law = normal_law(0.2, 0.3)
        gen = random.Random(3)
        return [script.Cell(calendar[i], calendar[i + 1], law, law, float(gen.choice([0, 0, 0, 1]))) for i in range(n)]

    def test_each_version_has_six_bins_that_sum_to_one_and_the_draw_is_repeatable(self):
        result = script.pit_shares(self.cells(), seed=1072)
        self.assertEqual(result["n"], 300)
        for key in ("midpoint", "bracket_970", "integer"):
            self.assertAlmostEqual(sum(result[key]), 1.0)
            self.assertEqual(len(result[key]), 6)
            self.assertIn(key, result["share_at_or_below_0.10"])
        self.assertEqual(result, script.pit_shares(self.cells(), seed=1072))

    def test_a_cell_without_an_outcome_is_not_scored(self):
        cells = self.cells(10)
        cells[0] = cells[0]._replace(outcome=None)
        self.assertEqual(script.pit_shares(cells, seed=1072)["n"], 9)


class CellsTests(unittest.TestCase):
    def test_h1_cells_pair_the_law_of_a_target_with_the_decision_a_business_day_before(self):
        calendar = [date(2024, 1, 2) + timedelta(days=i) for i in range(6)]
        law = normal_law(0.0, 1.0)
        laws = {calendar[2]: law, calendar[3]: None, calendar[4]: law}
        outcomes = {d: float(i) for i, d in enumerate(calendar)}
        cells = script.h1_cells(laws, calendar, outcomes)
        self.assertEqual([(c.decision, c.target, c.outcome) for c in cells], [(calendar[1], calendar[2], 2.0), (calendar[3], calendar[4], 4.0)])

    def test_a_target_not_on_the_calendar_is_an_error(self):
        calendar = [date(2024, 1, 2) + timedelta(days=i) for i in range(3)]
        with self.assertRaises(ValueError):
            script.h1_cells({date(2030, 1, 1): normal_law(0, 1)}, calendar, {})


class ReadingTests(unittest.TestCase):
    def test_the_reading_rule_is_970s(self):
        self.assertEqual(script.read_share(0.30, [0.28, 0.31]), "stands")
        self.assertEqual(script.read_share(0.12, [0.11]), "does not stand")
        self.assertEqual(script.read_share(0.30, [0.28, 0.09]), "unresolved")


class GuardTests(unittest.TestCase):
    def test_a_locked_day_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.refuse_locked([date(2026, 9, 10)])

    def test_the_study_ends_on_the_last_day_before_the_lockbox(self):
        self.assertEqual(script.LAST_TARGET, date(2025, 12, 31))


if __name__ == "__main__":
    unittest.main()
