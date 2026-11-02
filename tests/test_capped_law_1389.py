"""The law the capped candidate emits, and the two coherent rules (#1389): `repo_model.capped_law`.

The tests fix the arithmetic on synthetic quantile vectors (the 23 levels of `scoring_protocol.GRID`), the cases the design note
`docs/research/cap-tail-rule-1389-design.md` walks through:

* the status quo (the flag off) is `spread_mean_reversion.exceedance` on the capped vector, bit for bit, whatever the vector, with and
  without a line (`ml.exceedance_from_quantiles` too, where numpy is installed): no published figure moves;
* the status quo is incoherent when the cap binds: one binding knot leaves a probability of about 0.0025 above the line, several binding
  knots leave none (the review's example, q97.5 = 9 and q99 = 10);
* option (a), a bounded law with an atom at the line: the uncapped law clipped at the line, P(> line) = 0, the atom the mass the
  uncapped law had above the line, the quantiles the capped vector, the probabilities below the line the uncapped law's own;
* option (b), the capped percentiles with an unbounded completion: the atom is the mass between the first capped level and q99, the
  1% above q99 runs on above the line at the slope of the last open segment, and the number of binding knots no longer decides it;
* the randomized PIT of every law lies in the interval the law gives the outcome's whole basis point, and is uniform where the
  cumulative distribution is continuous;
* the flag: an unknown rule is a `ValueError`; the default is the status quo.

Recorded mutations (this module adds no leakage, availability or staleness guard; these two kill its rule arithmetic). The test file was
written before the module (the first run against no module: `ImportError`), and both mutations were applied and restored:

* `_open_tail_points`, the atom's top `Point(ceiling, GRID[-1])` replaced by `Point(ceiling, GRID[first])` (the mass between the first
  capped level and q99 has no home): `OpenTailTests.test_several_binding_knots_leave_an_atom_and_one_percent_above` fails with
  `AssertionError` (`0.0 != 0.08999999999999997` at the atom's mass), and `test_quantiles_are_the_capped_vector` and
  `CommonTests.test_the_grid_scores_do_not_depend_on_the_rule` fail with it (`10.5 != 10.0`);
* `_bounded_points`, `points.append(Point(ceiling, below))` replaced by `points.append(Point(ceiling, 1.0))` (the uncapped law's mass below the
  line is lost, so there is no atom): `BoundedTests.test_the_atom_is_the_mass_the_uncapped_law_had_above_the_line` fails with `AssertionError`
  (`0.0 != 0.4500005999494`), and four more tests in `BoundedTests` and `CommonTests` fail with it.
"""

from __future__ import annotations

import math
import random
import unittest

from repo_model import capped_law as cl
from repo_model import spread_mean_reversion as smr
from repo_model.scoring_protocol import GRID

try:  # pragma: no cover - depends on the environment
    import numpy  # noqa: F401
    from repo_model import ml
    HAVE_NUMPY = True
except Exception:  # pragma: no cover
    HAVE_NUMPY = False


def ramp(start: float, step: float) -> list:
    return [start + step * i for i in range(len(GRID))]


def one_knot() -> list:
    """The review's example: once capped at 10 bp, q97.5 = 9 and q99 = 10 (q99 was 30 before)."""

    u = ramp(-4.0, 0.6)
    u[-2], u[-1] = 9.0, 30.0
    return u


def many_knots() -> list:
    """Four upper levels (0.9, 0.95, 0.975, 0.99) at or over the line: all four are 10 once capped. The last open segment runs from
    (5.0, 0.85) to (10.0, 0.9): 100 bp per unit of probability."""

    u = ramp(-4.0, 0.5)
    u[-4:] = [11.0, 20.0, 25.0, 40.0]
    return u


class StatusQuoTests(unittest.TestCase):
    def test_the_law_reads_the_same_as_the_function(self):
        rng = random.Random(11)
        for _ in range(50):
            u = sorted(rng.uniform(-6, 40) for _ in GRID)
            law = cl.emitted_law(u, 10.0, "status_quo")
            for tau in (0.0, 5.0, 10.0):
                self.assertAlmostEqual(law.survival(math.floor(tau) + 0.5), cl.exceedance(u, 10.0, tau), places=12)

    def test_the_flag_is_off_by_default(self):
        self.assertEqual(cl.DEFAULT_RULE, "status_quo")
        self.assertEqual(cl.RULES, ("status_quo", "atom_at_line", "open_tail"))

    def test_it_is_the_published_reading_of_the_capped_vector(self):
        rng = random.Random(1389)
        for _ in range(200):
            u = sorted(rng.uniform(-6, 40) for _ in GRID)
            line = rng.choice([None, 10.0, 7.0])
            capped = cl.cap(u, line)
            for tau in (-3.0, 0.0, 2.0, 5.0, 8.0, 10.0, 12.0, 25.0):
                self.assertEqual(cl.exceedance(u, line, tau), smr.exceedance(capped, tau))

    @unittest.skipUnless(HAVE_NUMPY, "numpy not installed")
    def test_it_is_the_ml_reading_too(self):
        rng = random.Random(7)
        for _ in range(50):
            u = sorted(rng.uniform(-6, 40) for _ in GRID)
            capped = cl.cap(u, 10.0)
            expected = ml.exceedance_from_quantiles(capped, GRID, (5.0, 10.0))
            self.assertEqual((cl.exceedance(u, 10.0, 5.0), cl.exceedance(u, 10.0, 10.0)), expected)

    def test_one_binding_knot_leaves_a_probability_above_the_line(self):
        u = one_knot()
        self.assertEqual(cl.cap(u, 10.0)[-2:], [9.0, 10.0])
        self.assertAlmostEqual(cl.exceedance(u, 10.0, 10.0), 0.0025, places=4)

    def test_several_binding_knots_collapse_the_probability(self):
        u = many_knots()
        capped = cl.cap(u, 10.0)
        self.assertEqual(capped[-4:], [10.0] * 4)
        self.assertLess(cl.exceedance(u, 10.0, 10.0), 1e-6)

    def test_the_two_cases_disagree_on_the_same_line(self):
        self.assertGreater(cl.exceedance(one_knot(), 10.0, 10.0), 1000 * cl.exceedance(many_knots(), 10.0, 10.0))


class BoundedTests(unittest.TestCase):
    """(a): the uncapped law clipped at the line."""

    def setUp(self):
        self.u = ramp(-2.0, 1.0)  # q at level 0.99 is 20
        self.line = 10.0

    def test_nothing_is_above_the_line(self):
        for tau in (10.0, 11.0, 30.0):
            self.assertEqual(cl.exceedance(self.u, self.line, tau, rule="atom_at_line"), 0.0)

    def test_below_the_line_it_is_the_uncapped_law(self):
        for tau in (-1.0, 0.0, 5.0, 9.0):
            self.assertEqual(cl.exceedance(self.u, self.line, tau, rule="atom_at_line"), smr.exceedance(self.u, tau))

    def test_the_atom_is_the_mass_the_uncapped_law_had_above_the_line(self):
        law = cl.emitted_law(self.u, self.line, "atom_at_line")
        uncapped = cl.emitted_law(self.u, None, "status_quo")
        mass_above = uncapped.survival(self.line + 1e-9)
        self.assertGreater(mass_above, 0.1)
        self.assertAlmostEqual(law.atom_at(self.line), mass_above, places=6)
        self.assertAlmostEqual(law.cdf_left(self.line), 1.0 - mass_above, places=6)
        self.assertEqual(law.cdf(self.line), 1.0)

    def test_the_quantiles_are_the_capped_vector(self):
        law = cl.emitted_law(self.u, self.line, "atom_at_line")
        for level, value in zip(GRID, cl.cap(self.u, self.line)):
            self.assertAlmostEqual(law.quantile(level), value, places=4)

    def test_a_cap_that_does_not_bind_still_bounds_the_completion(self):
        u = ramp(-6.0, 0.2)
        u[-1] = 1.0  # q99 = 1.0 under the line at 2.0, but its completion runs on to about 2.7
        self.assertEqual(cl.cap(u, 2.0), u)
        law = cl.emitted_law(u, 2.0, "atom_at_line")
        self.assertEqual(law.cdf(2.0), 1.0)
        self.assertGreater(law.atom_at(2.0), 0.0)
        self.assertGreater(cl.emitted_law(u, None, "atom_at_line").survival(2.0), 0.0)

    def test_no_line_is_the_uncapped_law(self):
        for tau in (0.0, 5.0, 12.0):
            self.assertEqual(cl.exceedance(self.u, None, tau, rule="atom_at_line"), smr.exceedance(self.u, tau))


class OpenTailTests(unittest.TestCase):
    """(b): the capped percentiles with an unbounded completion."""

    def test_without_a_binding_knot_it_is_the_status_quo(self):
        u = ramp(-6.0, 0.4)
        for tau in (-2.0, 0.0, 1.0, 3.0, 8.0, 10.0):
            self.assertAlmostEqual(cl.exceedance(u, 10.0, tau, rule="open_tail"), cl.exceedance(u, 10.0, tau), places=5)

    def test_one_binding_knot_is_the_status_quo(self):
        u = one_knot()
        self.assertAlmostEqual(cl.exceedance(u, 10.0, 10.0, rule="open_tail"), cl.exceedance(u, 10.0, 10.0), places=6)
        self.assertAlmostEqual(cl.exceedance(u, 10.0, 10.0, rule="open_tail"), 0.0025, places=4)

    def test_several_binding_knots_leave_an_atom_and_one_percent_above(self):
        u = many_knots()
        k = next(i for i, v in enumerate(cl.cap(u, 10.0)) if v >= 10.0)
        self.assertEqual(GRID[k], 0.9)
        law = cl.emitted_law(u, 10.0, "open_tail")
        self.assertAlmostEqual(law.atom_at(10.0), GRID[-1] - GRID[k], places=9)
        self.assertAlmostEqual(law.survival(10.0), 1.0 - GRID[-1], places=9)
        # the 1% runs on 1 bp above the line at 100 bp per unit: P(> 10 bp), cut at 10.5, is half of it
        self.assertAlmostEqual(cl.exceedance(u, 10.0, 10.0, rule="open_tail"), 0.005, places=9)
        self.assertLess(cl.exceedance(u, 10.0, 10.0), 1e-6)  # where the status quo leaves none

    def test_the_tail_runs_on_at_the_slope_of_the_last_open_segment(self):
        u = many_knots()
        capped = cl.cap(u, 10.0)
        k = next(i for i, v in enumerate(capped) if v >= 10.0)
        slope = (10.0 - capped[k - 1]) / (GRID[k] - GRID[k - 1])
        law = cl.emitted_law(u, 10.0, "open_tail")
        self.assertAlmostEqual(law.quantile(1.0), 10.0 + (1.0 - GRID[-1]) * slope, places=9)

    def test_every_knot_binding_has_no_open_segment_and_is_bounded(self):
        u = [20.0 + i for i in range(len(GRID))]
        law = cl.emitted_law(u, 10.0, "open_tail")
        self.assertEqual(law.survival(10.0), 0.0)
        self.assertEqual(cl.OPEN_TAIL_NO_SLOPE, "bounded")

    def test_quantiles_are_the_capped_vector(self):
        u = many_knots()
        law = cl.emitted_law(u, 10.0, "open_tail")
        for level, value in zip(GRID, cl.cap(u, 10.0)):
            self.assertAlmostEqual(law.quantile(level), value, places=9)


class CommonTests(unittest.TestCase):
    def test_the_grid_scores_do_not_depend_on_the_rule(self):
        u = many_knots()
        for rule in cl.RULES:
            law = cl.emitted_law(u, 10.0, rule)
            for level, value in zip(GRID, cl.cap(u, 10.0)):
                self.assertAlmostEqual(law.quantile(level), value, places=4, msg=rule)

    def test_probabilities_do_not_increase_with_tau(self):
        rng = random.Random(3)
        for _ in range(100):
            u = sorted(rng.uniform(-6, 40) for _ in GRID)
            for rule in cl.RULES:
                curve = [cl.exceedance(u, 10.0, tau, rule=rule) for tau in range(-8, 40)]
                self.assertTrue(all(a >= b - 1e-12 for a, b in zip(curve, curve[1:])), rule)
                self.assertTrue(all(0.0 <= v <= 1.0 for v in curve))

    def test_an_unknown_rule_is_refused(self):
        with self.assertRaises(ValueError):
            cl.exceedance(ramp(0.0, 1.0), 10.0, 5.0, rule="clip")
        with self.assertRaises(ValueError):
            cl.emitted_law(ramp(0.0, 1.0), 10.0, "clip")

    def test_a_vector_of_the_wrong_length_or_order_is_refused(self):
        with self.assertRaises(ValueError):
            cl.exceedance([0.0, 1.0], 10.0, 5.0)
        with self.assertRaises(ValueError):
            cl.exceedance(list(reversed(ramp(0.0, 1.0))), 10.0, 5.0)

    def test_a_negative_margin_is_refused(self):
        with self.assertRaises(ValueError):
            cl.cap(ramp(0.0, 1.0), 10.0, margin=-1.0)


class PitTests(unittest.TestCase):
    def test_the_pit_lies_in_the_interval_of_the_whole_basis_point(self):
        u = many_knots()
        for rule in cl.RULES:
            law = cl.emitted_law(u, 10.0, rule)
            for y in (-3.0, 4.2, 10.0, 11.0, 14.0):
                lo, hi = cl.pit_interval(law, y)
                self.assertLessEqual(lo, hi)
                for v in (0.0, 0.3, 1.0):
                    self.assertTrue(lo <= cl.randomized_pit(law, y, v) <= hi)

    def test_an_outcome_at_the_atom_gets_the_atoms_interval(self):
        u = ramp(-2.0, 1.0)
        law = cl.emitted_law(u, 10.0, "atom_at_line")
        lo, hi = cl.pit_interval(law, 10.0)
        self.assertGreaterEqual(hi - lo, law.atom_at(10.0))
        self.assertEqual(hi, 1.0)
        self.assertAlmostEqual(lo, law.cdf(9.5), places=12)

    def test_an_outcome_above_a_bounded_law_has_a_degenerate_pit_of_one(self):
        u = ramp(-2.0, 1.0)
        law = cl.emitted_law(u, 10.0, "atom_at_line")
        self.assertEqual(cl.pit_interval(law, 13.0), (1.0, 1.0))

    def test_the_pit_is_uniform_in_expectation_under_its_own_law(self):
        # draw y from the law's own whole-bp distribution; the mean of the randomized PIT is one half
        u = many_knots()
        for rule in cl.RULES:
            law = cl.emitted_law(u, 10.0, rule)
            rng = random.Random(5)
            total = 0.0
            n = 4000
            for _ in range(n):
                y = float(round(law.quantile(rng.random())))
                total += cl.randomized_pit(law, y, rng.random())
            self.assertAlmostEqual(total / n, 0.5, delta=0.03, msg=rule)


if __name__ == "__main__":
    unittest.main()
