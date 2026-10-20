"""Kupiec and Christoffersen coverage tests, stdlib only (#993; groundwork for #941, #961).

Sources for the formulas the worked values come from: Kupiec (1995), "Techniques for verifying the accuracy of
risk measurement models", Journal of Derivatives 3(2), the proportion-of-failures likelihood ratio; Christoffersen
(1998), "Evaluating interval forecasts", International Economic Review 39(4), the independence and conditional
coverage likelihood ratios. Each worked value below is the closed form written out term by term from those formulas
(`math.log` of the counts), not read back from the module, and was cross-checked once against
`scipy.stats.chi2.sf` outside the suite (scipy is not a dependency of this tree).

The hit definition on a whole-bp target is the project's open question: `hit_sequence` has no default for it, and
a test pins that it raises `TypeError` when the rule is left out.
"""

import math
import random
import unittest

from repo_model import coverage_tests as ct


def _ll(zeros, ones, p):
    """Bernoulli log-likelihood with the convention 0 * ln 0 = 0."""

    out = 0.0
    if zeros:
        out += zeros * math.log(1 - p)
    if ones:
        out += ones * math.log(p)
    return out


class ChiSquareSurvival(unittest.TestCase):
    def test_one_degree_of_freedom_known_quantiles(self):
        # chi2(1): P(X > 3.841458820694124) = 0.05, P(X > 6.634896601021213) = 0.01.
        self.assertAlmostEqual(ct.chi2_sf(3.841458820694124, 1), 0.05, places=9)
        self.assertAlmostEqual(ct.chi2_sf(6.634896601021213, 1), 0.01, places=9)

    def test_two_degrees_of_freedom_is_exponential(self):
        # chi2(2): P(X > x) = exp(-x / 2); the 5% point is 2 ln 20.
        self.assertAlmostEqual(ct.chi2_sf(2 * math.log(20), 2), 0.05, places=12)

    def test_zero_statistic_has_p_value_one(self):
        self.assertEqual(ct.chi2_sf(0.0, 1), 1.0)
        self.assertEqual(ct.chi2_sf(0.0, 2), 1.0)

    def test_unsupported_degrees_of_freedom_and_negative_statistic_raise(self):
        with self.assertRaises(ValueError):
            ct.chi2_sf(1.0, 3)
        with self.assertRaises(ValueError):
            ct.chi2_sf(-0.1, 1)


class Kupiec(unittest.TestCase):
    def test_no_hits_closed_form(self):
        # N = 100, x = 0, p = 0.05: LR = -2 * 100 * ln(0.95) (the unrestricted likelihood is 1).
        res = ct.kupiec([0] * 100, 0.05)
        want = -2 * 100 * math.log(0.95)
        self.assertAlmostEqual(res.statistic, want, places=12)
        self.assertAlmostEqual(res.p_value, math.erfc(math.sqrt(want / 2)), places=12)
        self.assertEqual((res.n, res.hits), (100, 0))

    def test_all_hits_closed_form(self):
        res = ct.kupiec([1] * 20, 0.1)
        self.assertAlmostEqual(res.statistic, -2 * 20 * math.log(0.1), places=12)

    def test_hit_rate_equal_to_nominal_gives_zero(self):
        res = ct.kupiec([1] * 5 + [0] * 95, 0.05)
        self.assertAlmostEqual(res.statistic, 0.0, places=12)
        self.assertAlmostEqual(res.p_value, 1.0, places=12)

    def test_textbook_form_with_hits(self):
        # N = 250, x = 7, p = 0.01: LR = -2 [ln L(p) - ln L(x / N)].
        res = ct.kupiec([1] * 7 + [0] * 243, 0.01)
        pi = 7 / 250
        want = -2 * (_ll(243, 7, 0.01) - _ll(243, 7, pi))
        self.assertAlmostEqual(res.statistic, want, places=12)
        self.assertAlmostEqual(res.p_value, math.erfc(math.sqrt(want / 2)), places=12)
        self.assertTrue(0.01 < res.p_value < 0.05)

    def test_order_of_the_hits_does_not_matter(self):
        a = ct.kupiec([1, 0, 0, 1, 0, 0, 0, 0, 0, 0], 0.1)
        b = ct.kupiec([0, 0, 0, 0, 0, 0, 0, 0, 1, 1], 0.1)
        self.assertEqual(a.statistic, b.statistic)

    def test_data_guards(self):
        for bad in ([], [0, 2], [0, 1.5], ["a"], [True, None]):
            with self.assertRaises(ValueError):
                ct.kupiec(bad, 0.05)
        for p in (0.0, 1.0, -0.1, 1.5, float("nan")):
            with self.assertRaises(ValueError):
                ct.kupiec([0, 1], p)

    def test_size_is_near_nominal_under_independent_bernoulli(self):
        rng = random.Random(993)
        reps, n, p = 2000, 500, 0.1
        rejected = sum(
            ct.kupiec([int(rng.random() < p) for _ in range(n)], p).p_value < 0.05 for _ in range(reps))
        self.assertAlmostEqual(rejected / reps, 0.05, delta=0.02)

    def test_power_against_wrong_rate(self):
        rng = random.Random(7)
        hits = [int(rng.random() < 0.2) for _ in range(500)]
        self.assertLess(ct.kupiec(hits, 0.1).p_value, 0.001)


class Independence(unittest.TestCase):
    def test_closed_form_from_transition_counts(self):
        # 0 0 1 1 0 1 0 0 0 1: transitions 00->3, 01->3, 10->2, 11->1.
        seq = [0, 0, 1, 1, 0, 1, 0, 0, 0, 1]
        n00, n01, n10, n11 = 3, 3, 2, 1
        self.assertEqual(ct.transition_counts(seq), (n00, n01, n10, n11))
        pi01, pi11, pi = n01 / (n00 + n01), n11 / (n10 + n11), (n01 + n11) / 9
        want = -2 * (_ll(n00 + n10, n01 + n11, pi) - _ll(n00, n01, pi01) - _ll(n10, n11, pi11))
        res = ct.christoffersen_independence(seq)
        self.assertAlmostEqual(res.statistic, want, places=12)
        self.assertAlmostEqual(res.p_value, math.erfc(math.sqrt(want / 2)), places=12)
        self.assertEqual(res.n, 10)

    def test_no_hits_no_transitions_into_one_is_degenerate_not_an_error(self):
        # Every count in the "previous day hit" row is zero and so is pi: the statistic is 0 and p is 1.
        res = ct.christoffersen_independence([0] * 30)
        self.assertEqual((res.statistic, res.p_value), (0.0, 1.0))

    def test_all_hits_is_degenerate_not_an_error(self):
        res = ct.christoffersen_independence([1] * 30)
        self.assertEqual((res.statistic, res.p_value), (0.0, 1.0))

    def test_a_single_hit_with_no_repeat(self):
        # 0 0 1 0 0: n00=2, n01=1, n10=1, n11=0. Row "after a hit" has one observation and no repeat.
        res = ct.christoffersen_independence([0, 0, 1, 0, 0])
        pi01, pi = 1 / 3, 1 / 4
        want = -2 * (_ll(3, 1, pi) - _ll(2, 1, pi01) - _ll(1, 0, 0.0))
        self.assertAlmostEqual(res.statistic, want, places=12)

    def test_needs_at_least_one_transition(self):
        with self.assertRaises(ValueError):
            ct.christoffersen_independence([1])
        with self.assertRaises(ValueError):
            ct.christoffersen_independence([])

    def test_clustered_hits_are_rejected(self):
        rng = random.Random(11)
        seq, state = [], 0
        for _ in range(1000):
            state = int(rng.random() < (0.5 if state else 0.05))
            seq.append(state)
        self.assertLess(ct.christoffersen_independence(seq).p_value, 0.001)

    def test_independent_hits_are_not_rejected_at_the_nominal_rate(self):
        rng = random.Random(993)
        reps, n, p = 2000, 500, 0.1
        rejected = sum(
            ct.christoffersen_independence([int(rng.random() < p) for _ in range(n)]).p_value < 0.05
            for _ in range(reps))
        self.assertAlmostEqual(rejected / reps, 0.05, delta=0.02)

    def test_data_guard(self):
        with self.assertRaises(ValueError):
            ct.christoffersen_independence([0, 3, 1])


class ConditionalCoverage(unittest.TestCase):
    def test_is_the_sum_of_the_two_statistics_on_two_degrees_of_freedom(self):
        seq = [0, 0, 1, 1, 0, 1, 0, 0, 0, 1]
        cc = ct.christoffersen_conditional_coverage(seq, 0.2)
        want = ct.kupiec(seq, 0.2).statistic + ct.christoffersen_independence(seq).statistic
        self.assertAlmostEqual(cc.statistic, want, places=12)
        self.assertAlmostEqual(cc.p_value, math.exp(-want / 2), places=12)

    def test_clustered_hits_at_the_right_rate_fail_conditional_coverage_not_kupiec(self):
        seq = ([1] * 5 + [0] * 45) * 4 + [0] * 800  # 20 hits in 1000, in five-day clusters
        self.assertGreater(ct.kupiec(seq, 0.02).p_value, 0.5)
        self.assertLess(ct.christoffersen_conditional_coverage(seq, 0.02).p_value, 0.001)


class HitSequence(unittest.TestCase):
    def test_the_hit_rule_is_required(self):
        with self.assertRaises(TypeError):
            ct.hit_sequence([1, 2], [1, 1])

    def test_strict_and_weak_rules_differ_on_a_tie(self):
        y, q = [3, 4, 5], [4, 4, 4]
        self.assertEqual(ct.hit_sequence(y, q, rule="above"), [0, 0, 1])
        self.assertEqual(ct.hit_sequence(y, q, rule="at_or_above"), [0, 1, 1])

    def test_unknown_rule_and_length_mismatch_raise(self):
        with self.assertRaises(ValueError):
            ct.hit_sequence([1], [1], rule="gt")
        with self.assertRaises(ValueError):
            ct.hit_sequence([1, 2], [1], rule="above")
        with self.assertRaises(ValueError):
            ct.hit_sequence([1.0, float("nan")], [1, 1], rule="above")


if __name__ == "__main__":
    unittest.main()
