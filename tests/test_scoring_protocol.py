"""The scorer of scoring protocol v1, piece by piece (#655).

The synthetic suite (`test_scoring_protocol_synthetic.py`) checks that the scorer ranks
forecasts of known quality. This module checks each piece against an independent reading of
`docs/decisions/scoring-protocol.md`: the scores, the lockbox, the missing-data rule, the
first-published outcome, the bootstrap, Diebold-Mariano, the spending function and the
verdict.
"""

from __future__ import annotations

import math
import random
import unittest
from unittest import mock
from datetime import date, datetime, timedelta, timezone
from statistics import NormalDist

from repo_model import scoring_protocol as sp
from repo_model.data import PointInTimeObservation
from repo_model.metrics import pinball_loss, stationary_bootstrap_indices
from repo_model.splits import LookAheadError

NORMAL = NormalDist()


def weekdays(start, count):
    out, day = [], start
    while len(out) < count:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


def flat(value):
    return [float(value)] * len(sp.GRID)


def spread(centre, width=1.0):
    return [centre + width * NORMAL.inv_cdf(level) for level in sp.GRID]


class ScoreTests(unittest.TestCase):
    def test_grid_crps_is_twice_the_mean_pinball_loss(self):
        quantiles = spread(1.0, 2.0)
        expected = 2.0 * sum(pinball_loss(l, q, 3.5) for l, q in zip(sp.GRID, quantiles)) / 23
        self.assertAlmostEqual(sp.grid_crps(quantiles, 3.5), expected)

    def test_the_grid_is_symmetric_so_a_point_mass_scores_its_absolute_error(self):
        self.assertAlmostEqual(sum(sp.GRID) / len(sp.GRID), 0.5)
        self.assertAlmostEqual(sp.grid_crps(flat(1.0), 4.0), 3.0)

    def test_crossing_or_short_forecasts_are_refused(self):
        with self.assertRaises(ValueError):
            sp.grid_crps(list(reversed(spread(0.0))), 0.0)
        with self.assertRaises(sp.ProtocolError):
            sp.grid_crps(spread(0.0)[:5], 0.0)
        with self.assertRaises(sp.ProtocolError):
            sp.grid_crps(spread(0.0), math.nan)

    def test_twcrps_ignores_everything_below_zero(self):
        """Weight 1{z > 0}: a forecast and outcome wholly below zero score 0."""

        self.assertEqual(sp.upper_tail_twcrps(spread(-20.0), -15.0), 0.0)
        # Only the part above zero counts: moving the lower quantiles changes nothing.
        upper = spread(1.0, 3.0)
        lowered = [min(q, 0.0) - 5.0 if q < 0 else q for q in upper]
        self.assertEqual(sp.upper_tail_twcrps(upper, 2.0), sp.upper_tail_twcrps(lowered, 2.0))

    def test_twcrps_matches_the_threshold_integral(self):
        """The chaining form equals integral 1{z > 0} (F(z) - 1{y <= z})^2 dz for a step CDF.

        The grid CRPS of a quantile vector is the CRPS of nothing in particular, so the check is
        done where the two coincide exactly: a two-point forecast.
        """

        # Every quantile at -1 or at 3 (lower half at -1, upper at 3).
        quantiles = [-1.0 if level < 0.5 else 3.0 for level in sp.GRID]
        y = 1.0
        mapped = [max(q, 0.0) for q in quantiles]
        self.assertAlmostEqual(sp.upper_tail_twcrps(quantiles, y), sp.grid_crps(mapped, y))
        self.assertLess(sp.upper_tail_twcrps(quantiles, y), sp.grid_crps(quantiles, y))


class DayScoreTests(unittest.TestCase):
    def setUp(self):
        self.calendar = weekdays(date(2019, 1, 2), 12)
        self.outcomes = {day: float(i) for i, day in enumerate(self.calendar)}

    def forecast(self, centre=0.0):
        return {h: flat(centre) for h in sp.HORIZONS}

    def test_a_day_scores_the_mean_over_its_five_leads(self):
        decision = self.calendar[2]
        scores = sp.day_scores({decision: self.forecast(0.0)}, self.outcomes, self.calendar)
        expected = sum(abs(2.0 + h) for h in sp.HORIZONS) / 5.0
        self.assertAlmostEqual(scores[decision], expected)

    def test_leads_count_calendar_days_not_dates(self):
        """Friday's lead 1 is Monday."""

        friday = next(day for day in self.calendar if day.weekday() == 4)
        index = self.calendar.index(friday)
        forecasts = {friday: {h: flat(self.outcomes[self.calendar[index + h]]) for h in sp.HORIZONS}}
        self.assertEqual(sp.day_scores(forecasts, self.outcomes, self.calendar), {friday: 0.0})

    def test_a_target_with_no_published_outcome_is_dropped_for_every_forecast(self):
        decision = self.calendar[2]
        outcomes = dict(self.outcomes)
        outcomes[self.calendar[4]] = None  # lead 2
        scores = sp.day_scores({decision: self.forecast(0.0)}, outcomes, self.calendar)
        expected = sum(abs(2.0 + h) for h in (1, 3, 4, 5)) / 4.0
        self.assertAlmostEqual(scores[decision], expected)

    def test_a_decision_day_with_no_outcome_on_any_lead_is_dropped(self):
        decision = self.calendar[2]
        outcomes = {day: None for day in self.calendar}
        self.assertEqual(sp.day_scores({decision: self.forecast()}, outcomes, self.calendar), {})

    def test_a_missing_lead_is_refused_before_filling(self):
        decision = self.calendar[2]
        partial = {h: flat(0.0) for h in (1, 2, 3, 4)}
        with self.assertRaises(sp.ProtocolError):
            sp.day_scores({decision: partial}, self.outcomes, self.calendar)

    def test_a_lead_past_the_calendar_is_refused(self):
        with self.assertRaises(sp.ProtocolError):
            sp.day_scores({self.calendar[-2]: self.forecast()}, self.outcomes, self.calendar)


class LockboxTests(unittest.TestCase):
    """The scorer reads no locked day (`metadata/lockbox.json`, the tracked declaration)."""

    def test_a_target_in_the_blind_tier_is_refused(self):
        """A decision day whose lead 5 lands on 2026-09-04, the blind tier's first day.

        Mutation record: deleting the `lockbox.require_unlocked(...)` call in
        `scoring_protocol.day_scores` makes this test fail with `AssertionError`
        ("LookAheadError not raised"); restored, it passes.
        """

        calendar = weekdays(date(2026, 8, 24), 15)
        decision = calendar[calendar.index(date(2026, 9, 4)) - 5]
        outcomes = {day: 0.0 for day in calendar}
        forecasts = {decision: {h: flat(0.0) for h in sp.HORIZONS}}
        with self.assertRaises(LookAheadError) as caught:
            sp.day_scores(forecasts, outcomes, calendar)
        self.assertIn("2026-09-04", str(caught.exception))

    def test_the_day_before_the_blind_tier_is_scored(self):
        calendar = weekdays(date(2026, 8, 24), 15)
        decision = calendar[calendar.index(date(2026, 9, 3)) - 5]
        outcomes = {day: 0.0 for day in calendar}
        forecasts = {decision: {h: flat(0.0) for h in sp.HORIZONS}}
        self.assertEqual(sp.day_scores(forecasts, outcomes, calendar), {decision: 0.0})

    def test_a_target_without_an_outcome_is_not_read_so_is_not_refused(self):
        """Only days that are scored are checked: an unpublished target is not read."""

        calendar = weekdays(date(2026, 8, 24), 15)
        decision = calendar[calendar.index(date(2026, 9, 4)) - 5]
        outcomes = {day: (0.0 if day < date(2026, 9, 4) else None) for day in calendar}
        forecasts = {decision: {h: flat(0.0) for h in sp.HORIZONS}}
        self.assertEqual(sp.day_scores(forecasts, outcomes, calendar), {decision: 0.0})


class MissingDataTests(unittest.TestCase):
    def setUp(self):
        self.days = weekdays(date(2019, 1, 2), 40)
        self.b1 = {day: {h: flat(-1.0) for h in sp.HORIZONS} for day in self.days}
        self.full = {day: {h: flat(1.0) for h in sp.HORIZONS} for day in self.days}

    def test_a_missing_forecast_is_scored_as_b1s_and_counted(self):
        candidate = dict(self.full)
        del candidate[self.days[3]]
        filled = sp.fill_missing(candidate, self.b1, self.days)
        self.assertEqual(filled.forecasts[self.days[3]], self.b1[self.days[3]])
        self.assertEqual(filled.missing_days, (self.days[3],))
        self.assertAlmostEqual(filled.missing_share, 1 / 40)

    def test_only_the_missing_lead_is_replaced(self):
        candidate = {day: dict(leads) for day, leads in self.full.items()}
        candidate[self.days[5]][3] = None
        filled = sp.fill_missing(candidate, self.b1, self.days)
        self.assertEqual(filled.forecasts[self.days[5]][3], flat(-1.0))
        self.assertEqual(filled.forecasts[self.days[5]][2], flat(1.0))
        self.assertEqual(filled.missing_days, (self.days[5],))

    def test_five_percent_missing_stands_and_more_voids(self):
        candidate = dict(self.full)
        for day in self.days[:2]:  # 2 of 40 = 5%
            del candidate[day]
        self.assertAlmostEqual(sp.fill_missing(candidate, self.b1, self.days).missing_share, 0.05)
        del candidate[self.days[2]]  # 3 of 40 = 7.5%
        with self.assertRaises(sp.RegistrationVoid):
            sp.fill_missing(candidate, self.b1, self.days)

    def test_b1_must_be_there_to_stand_in(self):
        candidate = dict(self.full)
        del candidate[self.days[0]]
        b1 = dict(self.b1)
        del b1[self.days[0]]
        with self.assertRaises(sp.ProtocolError):
            sp.fill_missing(candidate, b1, self.days)


class FirstPublishedTests(unittest.TestCase):
    def observation(self, day, hour, value, series="sofr"):
        return PointInTimeObservation(
            series_id=series,
            ref_date=day,
            available_at=datetime(2019, 1, 3, hour, tzinfo=timezone.utc),
            value=value,
            vintage_id=f"v{hour}",
            source_sha="0" * 64,
        )

    def test_the_earliest_vintage_wins(self):
        day = date(2019, 1, 2)
        rows = [self.observation(day, 15, 2.41), self.observation(day, 13, 2.40), self.observation(day, 13, 9.0, "iorb")]
        self.assertEqual(sp.first_published(rows, "sofr"), {day: 2.40})

    def test_two_first_values_are_refused(self):
        day = date(2019, 1, 2)
        with self.assertRaises(sp.ProtocolError):
            sp.first_published([self.observation(day, 13, 2.40), self.observation(day, 13, 2.41)], "sofr")


def hac_variance(values, lag=10):
    """The Newey-West (Bartlett) long-run variance, written out term by term."""

    n = len(values)
    mean = sum(values) / n
    c = [v - mean for v in values]
    gamma = [sum(c[t] * c[t - k] for t in range(k, n)) / n for k in range(lag + 1)]
    return gamma[0] + 2 * sum((1 - k / (lag + 1)) * gamma[k] for k in range(1, lag + 1))


class BootstrapTests(unittest.TestCase):
    """The studentized stationary bootstrap of mean(d) (ruling of 13 October 2026, PR #660).

    Each resample's mean is studentized by its own HAC standard error (Newey-West, lag 10):
    `t* = (mean* - mean) / se*`, and the one-sided lower bound at level `a` is
    `mean - q_{1-a}(t*) * se`, with `se` the original series' HAC standard error.
    """

    def setUp(self):
        rng = random.Random(3)
        self.days = weekdays(date(2015, 1, 2), 300)
        self.bench = {day: 2.0 + rng.random() for day in self.days}
        self.cand = {day: self.bench[day] - 0.1 + 0.3 * rng.gauss(0, 1) for day in self.days}
        self.d = [self.bench[day] - self.cand[day] for day in self.days]
        self.b = [self.bench[day] for day in self.days]

    def naive_t_draws(self, draws, seed=7):
        rng = random.Random(seed)
        n = len(self.d)
        mean = sum(self.d) / n
        out = []
        for _ in range(draws):
            indices = stationary_bootstrap_indices(n, 10, rng)
            resample = [self.d[i] for i in indices]
            out.append((sum(resample) / n - mean) / math.sqrt(hac_variance(resample) / n))
        return sorted(out)

    def test_the_studentized_draws_match_a_direct_computation(self):
        test = sp.paired_test(self.bench, self.cand, seed=7, draws=50)
        for got, want in zip(test.t_draws, self.naive_t_draws(50)):
            self.assertAlmostEqual(got, want, places=9)

    def test_the_point_values(self):
        test = sp.paired_test(self.bench, self.cand, seed=7, draws=200)
        n = len(self.d)
        self.assertAlmostEqual(test.mean_difference, sum(self.d) / n)
        self.assertAlmostEqual(test.skill, sum(self.d) / sum(self.b))
        self.assertAlmostEqual(test.standard_error, math.sqrt(hac_variance(self.d) / n))
        self.assertAlmostEqual(test.dm_statistic, test.mean_difference / test.standard_error)
        self.assertEqual(test.n, n)

    def test_the_defaults_are_the_protocols(self):
        self.assertEqual((sp.BLOCK_LENGTH, sp.DRAWS, sp.ALPHA, sp.HAC_LAG), (10, 10_000, 0.05, 10))
        self.assertEqual(sp.INTERIM_DRAWS, 100_000)
        self.assertEqual(sp.CHECKPOINTS, (60, 125, 250))

    def test_the_lower_bound_is_the_studentized_one(self):
        test = sp.paired_test(self.bench, self.cand, seed=7, draws=1000)
        ordered = self.naive_t_draws(1000)
        position = 0.95 * 999
        low, weight = int(position), position - int(position)
        quantile = ordered[low] * (1 - weight) + ordered[low + 1] * weight
        self.assertAlmostEqual(
            test.lower_mean_difference(), test.mean_difference - quantile * test.standard_error, places=9
        )

    def test_the_p_value_is_the_share_of_draws_beyond_the_observed_statistic(self):
        test = sp.paired_test(self.bench, self.cand, seed=7, draws=1000)
        observed = test.mean_difference / test.standard_error
        expected = sum(1 for t in self.naive_t_draws(1000) if t >= observed) / 1000
        self.assertAlmostEqual(test.p_value, expected)

    def test_the_skill_bound_is_studentized_on_the_linearised_series(self):
        """skill = mean(d) / mean(b); its standard error is the HAC one of d - skill * b, over mean(b)."""

        test = sp.paired_test(self.bench, self.cand, seed=7, draws=1000)
        z = [d - test.skill * b for d, b in zip(self.d, self.b)]
        n = len(z)
        se = math.sqrt(hac_variance(z) / n) / (sum(self.b) / n)
        self.assertAlmostEqual(test.skill_standard_error, se)
        self.assertGreater(test.upper_skill(), test.skill)
        self.assertAlmostEqual(
            test.upper_skill(), test.skill - sp._bound(test.skill_t_draws, 0.05, 1000) * se, places=12
        )

    def test_skill_can_be_left_out(self):
        test = sp.paired_test(self.bench, self.cand, seed=7, draws=100, with_skill=False)
        test.lower_mean_difference()
        with self.assertRaises(sp.ProtocolError):
            test.upper_skill()

    def test_a_level_finer_than_the_draws_is_refused(self):
        test = sp.paired_test(self.bench, self.cand, seed=7, draws=1000)
        with self.assertRaises(sp.UnresolvedLevel):
            test.lower_mean_difference(0.0005)
        test.lower_mean_difference(0.001)

    def test_pairs_on_different_days_are_refused(self):
        shorter = {day: value for day, value in self.cand.items() if day != self.days[0]}
        with self.assertRaises(sp.ProtocolError):
            sp.paired_test(self.bench, shorter, seed=7, draws=10)

    def test_an_unseeded_test_is_refused(self):
        with self.assertRaises(sp.ProtocolError):
            sp.paired_test(self.bench, self.cand, seed=None, draws=10)


class CalibrationTests(unittest.TestCase):
    """The double (iterated) stationary bootstrap calibration of the studentized bound.

    Eleonora's ruling of 13 October 2026 (PR #695, comment 6146940245): the critical value is
    calibrated by resampling so the one-sided bound covers its nominal rate. For each outer
    resample b, `inner_draws` inner resamples are drawn from it (seeded `f"{seed}/{b}"`) and give
    the prepivot `u_b`, the share of inner t-draws at or below the outer `t*_b`. A bound at level
    `a` reads the outer t-draws at `1 - beta`, with `1 - beta` the `1 - a` quantile of the `u_b`.
    """

    def setUp(self):
        rng = random.Random(4)
        self.days = weekdays(date(2015, 1, 2), 40)
        self.bench = {day: 2.0 + rng.random() for day in self.days}
        self.cand = {day: self.bench[day] - 0.1 + 0.3 * rng.gauss(0, 1) for day in self.days}
        self.d = [self.bench[day] - self.cand[day] for day in self.days]

    def naive(self, outer, inner, seed=7):
        n = len(self.d)
        mean = sum(self.d) / n
        rng = random.Random(seed)
        t_draws, prepivots = [], []
        for b in range(outer):
            x = [self.d[i] for i in stationary_bootstrap_indices(n, 10, rng)]
            mx = sum(x) / n
            tb = (mx - mean) / math.sqrt(hac_variance(x) / n)
            t_draws.append(tb)
            inner_rng = random.Random(f"{seed}/{b}")
            below = 0
            for _ in range(inner):
                y = [x[i] for i in stationary_bootstrap_indices(n, 10, inner_rng)]
                ty = (sum(y) / n - mx) / math.sqrt(hac_variance(y) / n)
                below += ty <= tb
            prepivots.append(below / inner)
        return sorted(t_draws), sorted(prepivots)

    @staticmethod
    def quantile(ordered, p):
        x = p * (len(ordered) - 1)
        lo = int(x)
        w = x - lo
        return ordered[lo] if w == 0 else ordered[lo] * (1 - w) + ordered[lo + 1] * w

    def test_the_prepivots_match_a_direct_double_loop(self):
        test = sp.paired_test(self.bench, self.cand, seed=7, draws=30, inner_draws=20, with_skill=False)
        t_draws, prepivots = self.naive(30, 20)
        self.assertEqual(test.inner_draws, 20)
        for got, want in zip(test.prepivots, prepivots):
            self.assertAlmostEqual(got, want, places=12)
        for got, want in zip(test.t_draws, t_draws):
            self.assertAlmostEqual(got, want, places=9)

    def test_the_calibrated_bound(self):
        test = sp.paired_test(self.bench, self.cand, seed=7, draws=200, inner_draws=40, with_skill=False)
        t_draws, prepivots = self.naive(200, 40)
        level = self.quantile(prepivots, 0.95)
        expected = test.mean_difference - self.quantile(t_draws, level) * test.standard_error
        self.assertAlmostEqual(test.calibrated_level(0.05), 1.0 - level)
        self.assertAlmostEqual(test.lower_mean_difference(), expected, places=9)

    def test_the_outer_draws_are_the_uncalibrated_ones(self):
        """Calibration adds inner streams; the outer resamples, and so the t-draws, do not move."""

        plain = sp.paired_test(self.bench, self.cand, seed=7, draws=100, with_skill=False)
        calibrated = sp.paired_test(self.bench, self.cand, seed=7, draws=100, inner_draws=10, with_skill=False)
        self.assertEqual(plain.t_draws, calibrated.t_draws)
        self.assertEqual(plain.prepivots, ())
        self.assertAlmostEqual(
            plain.lower_mean_difference(),
            plain.mean_difference - sp._bound(plain.t_draws, 0.95, 100) * plain.standard_error,
        )

    def test_a_calibrated_level_at_the_prepivots_ceiling_is_refused(self):
        """When every prepivot is 1, no outer quantile below the maximum is calibrated: refused."""

        test = sp.paired_test(self.bench, self.cand, seed=7, draws=200, inner_draws=40, with_skill=False)
        with self.assertRaises(sp.UnresolvedLevel):
            test.lower_mean_difference(1e-4)

    def test_the_protocol_inner_draws(self):
        self.assertGreaterEqual(sp.INNER_DRAWS, 100)

    def test_verdict_refuses_an_uncalibrated_test(self):
        days = weekdays(date(2015, 1, 2), 250)
        rng = random.Random(9)
        b = {day: 1 + 0.05 * rng.gauss(0, 1) for day in days}
        c = {day: 0.8 + 0.05 * rng.gauss(0, 1) for day in days}
        tests = sp.paired_tests([(b, c), (b, c)], seed=1, draws=200)
        with self.assertRaises(sp.ProtocolError):
            sp.verdict(tests[0], tests[1], look=3, futility_level=0.05)


class DieboldMarianoTests(unittest.TestCase):
    def test_against_a_direct_computation(self):
        rng = random.Random(5)
        d = [0.1 + rng.gauss(0, 1) for _ in range(200)]
        n, mean = len(d), sum(d) / len(d)
        c = [x - mean for x in d]
        gamma = [sum(c[t] * c[t - k] for t in range(k, n)) / n for k in range(11)]
        lrv = gamma[0] + 2 * sum((1 - k / 11) * gamma[k] for k in range(1, 11))
        statistic, p = sp.diebold_mariano(d)
        self.assertAlmostEqual(statistic, mean / math.sqrt(lrv / n))
        self.assertAlmostEqual(p, 1 - NORMAL.cdf(statistic))

    def test_identical_forecasts_are_refused(self):
        with self.assertRaises(sp.ProtocolError):
            sp.diebold_mariano([0.0] * 50)


class SpendingTests(unittest.TestCase):
    def test_all_alpha_is_spent_at_the_last_checkpoint(self):
        self.assertAlmostEqual(sp.spending(1.0), 0.05)
        self.assertLess(sp.spending(60 / 250), sp.spending(125 / 250))

    def test_the_boundaries_match_gsdesigns(self):
        """gsDesign's sfLDOF, one-sided 0.025, three equally spaced looks: 3.7103, 2.5114, 1.9930."""

        for got, want in zip(sp.boundaries((1, 2, 3), 0.025), (3.7103, 2.5114, 1.9930)):
            self.assertAlmostEqual(got, want, places=4)

    def test_the_boundaries_spend_what_they_say_by_simulation(self):
        """Under no difference, the share of paths first crossing by each look is the spend."""

        bounds = sp.boundaries()
        fractions = [c / 250 for c in sp.CHECKPOINTS]
        rng = random.Random(11)
        paths = 200_000
        crossed = [0, 0, 0]
        for _ in range(paths):
            s, previous = 0.0, 0.0
            for look, (fraction, bound) in enumerate(zip(fractions, bounds)):
                s += rng.gauss(0.0, math.sqrt(fraction - previous))
                previous = fraction
                if s / math.sqrt(fraction) >= bound:
                    for later in range(look, 3):
                        crossed[later] += 1
                    break
        for look, fraction in enumerate(fractions):
            spent = sp.spending(fraction)
            error = math.sqrt(spent * (1 - spent) / paths)
            self.assertAlmostEqual(crossed[look] / paths, spent, delta=4 * error + 1e-5)

    def test_the_nominal_levels(self):
        levels = sp.nominal_levels()
        self.assertEqual(len(levels), 3)
        self.assertLess(levels[0], levels[1])
        self.assertLess(levels[1], levels[2])
        self.assertLess(levels[2], 0.05)


class VerdictTests(unittest.TestCase):
    """Verdicts read calibrated tests. The protocol's draw counts are patched down to keep these fast."""

    def test_from_scores(self):
        rng = random.Random(9)
        days = weekdays(date(2015, 1, 2), 250)

        def scores(level, noise=0.05):
            return {day: level + noise * rng.gauss(0, 1) for day in days}

        b1, b2 = scores(1.0), scores(1.2)
        strong, weak = scores(0.80), scores(0.9999)
        with mock.patch.object(sp, "INNER_DRAWS", 20):
            tests = sp.paired_tests(
                [(b1, strong), (b2, strong), (b1, weak), (b2, weak)], seed=1, draws=500, inner_draws=20
            )
            self.assertEqual(sp.verdict(tests[0], tests[1], look=3, futility_level=0.05), sp.SUPPORTED)
            self.assertEqual(sp.verdict(tests[2], tests[3], look=3, futility_level=0.05), sp.KILLED)

    def test_the_first_look_cannot_be_calibrated(self):
        """Look 1's nominal level is about 6e-5. A prepivot is a share of the inner draws, so the
        calibrated level needs more than one prepivot in about 16,000 below 1, which no feasible
        inner count gives: the bound is refused, not read at the ceiling. A question for Eleonora."""

        days = weekdays(date(2015, 1, 2), 60)
        rng = random.Random(2)
        b = {day: 1 + rng.random() for day in days}
        c = {day: 0.5 + 0.2 * rng.random() for day in days}
        with mock.patch.object(sp, "INTERIM_DRAWS", 2000), mock.patch.object(sp, "INNER_DRAWS", 20):
            tests = sp.paired_tests([(b, c), (b, c)], seed=1, draws=2000, inner_draws=20)
            with self.assertRaises(sp.UnresolvedLevel):
                sp.verdict(tests[0], tests[1], look=1, futility_level=0.05)

    def test_an_interim_look_on_too_few_draws_is_refused(self):
        days = weekdays(date(2015, 1, 2), 60)
        rng = random.Random(2)
        b = {day: 1 + rng.random() for day in days}
        c = {day: 0.5 + 0.2 * rng.random() for day in days}
        tests = sp.paired_tests([(b, c), (b, c)], seed=1, draws=1000)
        with self.assertRaises(sp.ProtocolError):
            sp.verdict(tests[0], tests[1], look=1, futility_level=0.05)

    def test_a_test_off_the_checkpoint_is_refused(self):
        days = weekdays(date(2015, 1, 2), 100)
        b = {day: 1.0 + 0.01 * i for i, day in enumerate(days)}
        c = {day: 0.9 + 0.02 * (i % 3) for i, day in enumerate(days)}
        tests = sp.paired_tests([(b, c), (b, c)], seed=1, draws=100)
        with self.assertRaises(sp.ProtocolError):
            sp.verdict(tests[0], tests[1], look=3, futility_level=0.05)


class SecondaryLevelsTests(unittest.TestCase):
    """B3 is scored on its own five levels against the candidate's same five (ruling, PR #660)."""

    FIVE = (0.05, 0.25, 0.5, 0.75, 0.95)

    def test_the_five_levels_are_on_the_grid(self):
        for level in self.FIVE:
            self.assertIn(level, sp.GRID)

    def test_a_candidate_is_read_at_the_five_levels(self):
        quantiles = spread(0.0, 2.0)
        reduced = sp.on_levels(quantiles, self.FIVE)
        self.assertEqual(reduced, [quantiles[sp.GRID.index(level)] for level in self.FIVE])

    def test_the_five_level_score_is_twice_the_mean_pinball_loss(self):
        values = [-3.0, -1.0, 0.0, 1.0, 3.0]
        score = sp.level_crps(self.FIVE)
        expected = 2.0 * sum(pinball_loss(l, q, 0.7) for l, q in zip(self.FIVE, values)) / 5
        self.assertAlmostEqual(score(values, 0.7), expected)

    def test_levels_off_the_grid_or_short_vectors_are_refused(self):
        with self.assertRaises(sp.ProtocolError):
            sp.on_levels(spread(0.0), (0.05, 0.33))
        with self.assertRaises(sp.ProtocolError):
            sp.level_crps(self.FIVE)([0.0, 1.0], 0.0)

    def test_day_scores_take_the_five_level_score(self):
        calendar = weekdays(date(2019, 1, 2), 12)
        outcomes = {day: 0.0 for day in calendar}
        forecasts = {calendar[2]: {h: [-1.0, -0.5, 0.0, 0.5, 1.0] for h in sp.HORIZONS}}
        scores = sp.day_scores(forecasts, outcomes, calendar, score=sp.level_crps(self.FIVE))
        expected = 2.0 * sum(pinball_loss(l, q, 0.0) for l, q in zip(self.FIVE, [-1.0, -0.5, 0.0, 0.5, 1.0])) / 5
        self.assertAlmostEqual(scores[calendar[2]], expected)


class HolmTests(unittest.TestCase):
    def test_step_down(self):
        self.assertEqual(sp.holm({"a": 0.01, "b": 0.04}), {"a": True, "b": True})
        self.assertEqual(sp.holm({"a": 0.03, "b": 0.04}), {"a": False, "b": False})
        self.assertEqual(sp.holm({"a": 0.02, "b": 0.06}), {"a": True, "b": False})


if __name__ == "__main__":
    unittest.main()
