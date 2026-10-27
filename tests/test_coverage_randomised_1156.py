"""The randomised tie rule in `coverage_cells` and the tie probability helper (#1156; H1 and H5 step 5).

Draft amendment 4 (#1130) reports two deterministic hit rules. Eleonora's ruling of 22 October 2026 (#1137, answer 4)
adds a third, the randomised tie rule, as an inert reporting option: `coverage_cells` reports it only when the caller
supplies the tie probabilities and the draws, and `enforce_coverage_requirement` stays off while
`COVERAGE_REQUIREMENT_IN_FORCE` is False. This module pins: that nothing changes when the caller supplies neither; the
tie probability of a discrete forecast; the randomised cells on hand cases in both tails; the refusals.

**Recorded mutation (lower tail).** In `coverage_cells`, replacing the randomised lower-tail call
`randomised_hit_sequence([-y for y in ys], [-q for q in qs], ps, us)` with `randomised_hit_sequence(ys, qs, ps, us)`
fails `RandomisedCellTests.test_beyond_the_quantile_is_a_hit_in_each_tail_whatever_the_draw` with `AssertionError`.
**Recorded mutation (tie probability).** In `tie_hit_probability`, returning `need` without the division by the mass
fails `TieProbabilityTests.test_the_lower_tail_probability_mirrors_it` with `AssertionError: 0.05 != 0.5`.
**Recorded mutation (pairing).** Replacing the condition `(tie_probabilities is None) != (draws is None)` in
`coverage_cells` with `False` fails `RandomisedCellTests.test_probabilities_and_draws_come_together` with `TypeError`.
"""

from __future__ import annotations

import random
import unittest
from datetime import date
from unittest import mock

from repo_model import coverage_tests as ct
from repo_model import scoring_protocol as sp

from test_scoring_protocol_coverage_requirement import business_days, cell, flat_quantiles, world


def tied_world(n, outcome):
    """Flat q05/q95 at -4.5/+4.5, outcomes from `outcome(day)`; tie probabilities 0.5 and draws from a seeded stream."""

    calendar = business_days(n + 6)
    forecasts = {day: {h: flat_quantiles() for h in sp.HORIZONS} for day in calendar[:n]}
    outcomes = {day: outcome(day) for day in calendar}
    labels = {day: "all" for day in calendar[:n]}
    return forecasts, outcomes, calendar, labels


def fill(forecasts, value, draw):
    return {
        day: {h: [value] * len(sp.GRID) for h in sp.HORIZONS} if draw is None else {h: [draw] * len(sp.GRID) for h in sp.HORIZONS}
        for day in forecasts
    }


class TieProbabilityTests(unittest.TestCase):
    def test_the_upper_tail_probability_is_the_part_of_the_mass_that_fills_the_tail(self):
        # Y uniform on 0..9, q95 = 9 (F(8) = 0.9 < 0.95 <= F(9) = 1): P(Y > 9) = 0, P(Y = 9) = 0.1, needs 0.05.
        self.assertAlmostEqual(ct.tie_hit_probability(0.9, 1.0, 0.05, upper=True), 0.5)

    def test_the_lower_tail_probability_mirrors_it(self):
        # Y uniform on 0..9, q05 = 0 (F(-) = 0 < 0.05 <= F(0) = 0.1): needs 0.05 of the 0.1 at 0.
        self.assertAlmostEqual(ct.tie_hit_probability(0.0, 0.1, 0.05, upper=False), 0.5)

    def test_the_probability_makes_the_hit_rate_exact(self):
        rng = random.Random(5)
        n = 60000
        y = [rng.randint(0, 9) for _ in range(n)]
        u = [rng.random() for _ in range(n)]
        p = ct.tie_hit_probability(0.9, 1.0, 0.05, upper=True)
        hits = ct.randomised_hit_sequence(y, [9] * n, [p] * n, u)
        self.assertAlmostEqual(sum(hits) / n, 0.05, delta=0.004)

    def test_a_quantile_with_no_mass_point_has_no_tie(self):
        # A continuous forecast: F(q-) = F(q) = level, so there is no mass at q.
        self.assertEqual(ct.tie_hit_probability(0.95, 0.95, 0.05, upper=True), 0.0)

    def test_malformed_input_raises(self):
        with self.assertRaises(ValueError):
            ct.tie_hit_probability(0.9, 0.8, 0.05, upper=True)
        with self.assertRaises(ValueError):
            ct.tie_hit_probability(0.9, 1.0, 1.5, upper=True)
        with self.assertRaises(ValueError):
            ct.tie_hit_probability(0.9, 1.0, 0.05, upper="up")


class RandomisedCellTests(unittest.TestCase):
    def test_without_probabilities_the_cells_are_what_they_were(self):
        forecasts, outcomes, calendar, labels = world(n=120, seed=2)
        cells = sp.coverage_cells(forecasts, outcomes, calendar, labels, method="thinned")
        self.assertEqual({c.rule for c in cells}, {"strict", "tie_counts"})
        self.assertEqual(len(cells), 4 * 5 * 2)

    def test_the_randomised_rule_is_a_third_set_of_cells_between_the_two(self):
        forecasts, outcomes, calendar, labels = tied_world(300, lambda day: 4.5 if day.day % 3 == 0 else 0.0)
        ties = fill(forecasts, 0.5, None)
        draws = fill(forecasts, 0.0, 0.25)  # every draw is below 0.5: every tie is a hit
        cells = sp.coverage_cells(
            forecasts, outcomes, calendar, labels, method="thinned", tie_probabilities=ties, draws=draws
        )
        self.assertEqual({c.rule for c in cells}, {"strict", "tie_counts", "randomised"})
        strict = cell(cells, level=0.95, lead=1, regime="all", rule="strict")
        weak = cell(cells, level=0.95, lead=1, regime="all", rule="tie_counts")
        mixed = cell(cells, level=0.95, lead=1, regime="all", rule="randomised")
        self.assertEqual(strict.hits, 0)
        self.assertGreater(weak.hits, 0)
        self.assertEqual(mixed.hits, weak.hits)
        self.assertEqual(mixed.n, weak.n)

    def test_a_draw_at_or_above_the_probability_is_not_a_hit(self):
        forecasts, outcomes, calendar, labels = tied_world(300, lambda day: 4.5)
        ties = fill(forecasts, 0.5, None)
        draws = fill(forecasts, 0.0, 0.75)
        cells = sp.coverage_cells(
            forecasts, outcomes, calendar, labels, method="thinned", tie_probabilities=ties, draws=draws
        )
        self.assertEqual(cell(cells, level=0.95, lead=1, regime="all", rule="randomised").hits, 0)

    def test_a_lower_level_ties_are_hit_below(self):
        # Outcomes at the q05 (-4.5), tie probability 1: a tie is a hit at the lower level; at the upper level it is
        # strictly below q95 and no hit.
        forecasts, outcomes, calendar, labels = tied_world(300, lambda day: -4.5)
        ties = fill(forecasts, 1.0, None)
        draws = fill(forecasts, 0.0, 0.0)
        cells = sp.coverage_cells(
            forecasts, outcomes, calendar, labels, method="thinned", tie_probabilities=ties, draws=draws
        )
        self.assertEqual(cell(cells, level=0.05, lead=1, regime="all", rule="randomised").hits, 300)
        self.assertEqual(cell(cells, level=0.95, lead=1, regime="all", rule="randomised").hits, 0)
        self.assertEqual(cell(cells, level=0.05, lead=1, regime="all", rule="strict").hits, 0)

    def test_beyond_the_quantile_is_a_hit_in_each_tail_whatever_the_draw(self):
        forecasts, outcomes, calendar, labels = tied_world(300, lambda day: -9.0)
        ties = fill(forecasts, 0.0, None)
        draws = fill(forecasts, 0.0, 0.99)
        cells = sp.coverage_cells(
            forecasts, outcomes, calendar, labels, method="thinned", tie_probabilities=ties, draws=draws
        )
        self.assertEqual(cell(cells, level=0.05, lead=1, regime="all", rule="randomised").hits, 300)
        self.assertEqual(cell(cells, level=0.95, lead=1, regime="all", rule="randomised").hits, 0)

    def test_probabilities_and_draws_come_together(self):
        forecasts, outcomes, calendar, labels = world(n=30)
        with self.assertRaises(sp.ProtocolError):
            sp.coverage_cells(
                forecasts, outcomes, calendar, labels, method="thinned", tie_probabilities=fill(forecasts, 0.5, None)
            )
        with self.assertRaises(sp.ProtocolError):
            sp.coverage_cells(forecasts, outcomes, calendar, labels, method="thinned", draws=fill(forecasts, 0.0, 0.1))

    def test_a_day_without_a_probability_is_refused(self):
        forecasts, outcomes, calendar, labels = world(n=30)
        ties = fill(forecasts, 0.5, None)
        ties.pop(calendar[4])
        with self.assertRaises(sp.ProtocolError):
            sp.coverage_cells(
                forecasts, outcomes, calendar, labels, method="thinned",
                tie_probabilities=ties, draws=fill(forecasts, 0.0, 0.1),
            )

    def test_a_probability_outside_zero_one_is_refused(self):
        forecasts, outcomes, calendar, labels = world(n=30)
        with self.assertRaises(ValueError):
            sp.coverage_cells(
                forecasts, outcomes, calendar, labels, method="thinned",
                tie_probabilities=fill(forecasts, 1.5, None), draws=fill(forecasts, 0.0, 0.1),
            )


class EnforceStaysInertTests(unittest.TestCase):
    def cells(self):
        forecasts, outcomes, calendar, labels = tied_world(300, lambda day: 4.9)
        return sp.coverage_cells(
            forecasts, outcomes, calendar, labels, method="thinned",
            tie_probabilities=fill(forecasts, 0.5, None), draws=fill(forecasts, 0.0, 0.1),
        )

    def test_the_flag_is_still_off(self):
        self.assertFalse(sp.COVERAGE_REQUIREMENT_IN_FORCE)

    def test_the_randomised_rule_is_accepted_by_the_requirement_and_inert_while_off(self):
        self.assertEqual(sp.enforce_coverage_requirement(self.cells(), alpha=0.05, family="holm", rule="randomised"), [])

    def test_once_on_it_reads_the_randomised_cells_only(self):
        cells = self.cells()
        with mock.patch.object(sp, "COVERAGE_REQUIREMENT_IN_FORCE", True):
            with self.assertRaises(sp.CoverageRequirementFailed):
                sp.enforce_coverage_requirement(cells, alpha=0.05, family="holm", rule="randomised")
            # With no randomised cells in the list the rule reads nothing and cannot fail.
            kept = [c for c in cells if c.rule != "randomised"]
            self.assertEqual(sp.enforce_coverage_requirement(kept, alpha=0.05, family="holm", rule="randomised"), [])

    def test_an_unknown_rule_is_still_refused(self):
        with self.assertRaises(sp.ProtocolError):
            sp.enforce_coverage_requirement([], alpha=0.05, family="holm", rule="other")


if __name__ == "__main__":
    unittest.main()
