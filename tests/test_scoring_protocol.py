"""The scorer of scoring protocol v1, piece by piece (#655).

The synthetic suite (`test_scoring_protocol_synthetic.py`) checks that the scorer ranks
forecasts of known quality. This module checks each piece against an independent reading of
`docs/decisions/scoring-protocol.md`: the scores, the lockbox, the missing-data rule, the
first-published outcome, the bootstrap, Diebold-Mariano, the spending function and the
verdict.
"""

from __future__ import annotations

import json
import math
import random
import unittest
from unittest import mock
from pathlib import Path
from datetime import date, datetime, timedelta, timezone
from statistics import NormalDist

from repo_model import scoring_protocol as sp
from repo_model.data import PointInTimeObservation
from repo_model.metrics import pinball_loss, stationary_bootstrap_indices
from repo_model.splits import LookAheadError

NORMAL = NormalDist()
ROOT = Path(__file__).resolve().parents[1]


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

    def test_the_percentile_draws_are_kept_for_their_readers(self):
        """`mean_difference_draws` and `skill_draws` are the sorted resampled mean(d) and skill on the same
        resamples: scripts on main (#686, #639) read them for their reported intervals."""

        test = sp.paired_test(self.bench, self.cand, seed=7, draws=50)
        rng = random.Random(7)
        n = len(self.d)
        means, skills = [], []
        for _ in range(50):
            indices = stationary_bootstrap_indices(n, 10, rng)
            dm = sum(self.d[i] for i in indices) / n
            bm = sum(self.b[i] for i in indices) / n
            means.append(dm)
            skills.append(dm / bm)
        for got, want in zip(test.mean_difference_draws, sorted(means)):
            self.assertAlmostEqual(got, want, places=10)
        for got, want in zip(test.skill_draws, sorted(skills)):
            self.assertAlmostEqual(got, want, places=10)

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

class EmpiricalCalibrationTests(unittest.TestCase):
    """The critical value calibrated on the development history (ruling of 13 October 2026, PR #695,
    comment 6149326627; a protocol change under §13).

    For a series d and a window length n, windows of n days are drawn from d by circular blocks of
    10 consecutive days at uniform random starts. Each window's studentized mean
    `t = (mean_w - mean(d)) / se_w` (Newey-West, lag 10) is computed, and the critical value at
    level a is the `1 - a` quantile of those t. The bound `mean - c * se` then covers mean(d) on a
    `1 - a` share of the windows.
    """

    def setUp(self):
        rng = random.Random(8)
        self.series = [rng.gauss(0, 1) + (8.0 if rng.random() < 0.01 else 0.0) for _ in range(400)]

    def naive_t(self, n, windows, seed):
        rng = random.Random(seed)
        mean = sum(self.series) / len(self.series)
        out = []
        for _ in range(windows):
            x = []
            while len(x) < n:
                start = rng.randrange(len(self.series))
                x.extend(self.series[(start + k) % len(self.series)] for k in range(10))
            x = x[:n]
            out.append((sum(x) / n - mean) / math.sqrt(hac_variance(x) / n))
        return sorted(out)

    def test_the_window_statistics_match_a_direct_computation(self):
        got = sp.window_t_statistics(self.series, days=60, windows=50, seed=3)
        for a, b in zip(got, self.naive_t(60, 50, 3)):
            self.assertAlmostEqual(a, b, places=9)

    def test_the_critical_value_is_the_quantile(self):
        ordered = self.naive_t(60, 400, 3)
        self.assertAlmostEqual(
            sp.calibrate_critical_value(self.series, days=60, level=0.05, windows=400, seed=3),
            CalibrationTests.quantile(ordered, 0.95),
            places=9,
        )

    def test_a_level_the_windows_cannot_resolve_is_refused(self):
        with self.assertRaises(sp.UnresolvedLevel):
            sp.calibrate_critical_value(self.series, days=60, level=0.001, windows=400, seed=3)

    def test_the_bound_at_a_critical_value(self):
        days = weekdays(date(2015, 1, 2), 100)
        rng = random.Random(1)
        b = {day: 1 + rng.random() for day in days}
        c = {day: 0.9 + rng.random() for day in days}
        test = sp.paired_test(b, c, seed=1, draws=20)
        self.assertAlmostEqual(test.lower_bound(2.5), test.mean_difference - 2.5 * test.standard_error)

    def test_each_comparison_has_its_own_recorded_values(self):
        """Q-E (b), Eleonora's ruling on PR #695 (comment 6159852603): each comparison is read at its own
        calibrated value, not the largest across them. `CRITICAL_VALUES` keys the values by comparison,
        as `scripts/protocol_coverage.py calibrate` recorded them; look 1 has none (Q-B)."""

        record = json.loads((ROOT / "docs" / "research" / "protocol-calibration" / "result.json").read_text())
        self.assertEqual(set(sp.CRITICAL_VALUES), {sp.GRID_COMPARISON, sp.FIVE_LEVEL_COMPARISON})
        for comparison, values in sp.CRITICAL_VALUES.items():
            self.assertIsNone(values[sp.CHECKPOINTS[0]])
            for n in sp.CHECKPOINTS[1:]:
                with self.subTest(comparison=comparison, days=n):
                    self.assertEqual(values[n], record["critical_values"][comparison][str(n)])
                    self.assertIn(str(n), record["null_false_detection_full_history"][comparison])

    def test_the_futility_values_are_the_recorded_calibration(self):
        record = json.loads((ROOT / "docs" / "research" / "protocol-calibration" / "result.json").read_text())
        self.assertEqual(sp.FUTILITY_LEVEL, 0.05)
        for n in sp.CHECKPOINTS:
            with self.subTest(days=n):
                self.assertEqual(
                    sp.FUTILITY_CRITICAL_VALUES[sp.GRID_COMPARISON][n],
                    record["futility_critical_values"][sp.GRID_COMPARISON][str(n)],
                )

    def test_the_skill_window_statistics_match_a_direct_computation(self):
        rng = random.Random(6)
        bench = [2.0 + rng.random() for _ in range(300)]
        diff = [0.1 + 0.3 * rng.gauss(0, 1) for _ in range(300)]
        truth = sum(diff) / sum(bench)
        got = sp.window_skill_t_statistics(bench, diff, days=60, windows=40, seed=4)
        rng = random.Random(4)
        want = []
        for _ in range(40):
            starts = []
            while len(starts) * 10 < 60:
                starts.append(rng.randrange(300))
            index = [(s + k) % 300 for s in starts for k in range(10)][:60]
            b = [bench[i] for i in index]
            d = [diff[i] for i in index]
            skill = sum(d) / sum(b)
            z = [x - skill * y for x, y in zip(d, b)]
            se = math.sqrt(hac_variance(z) / 60) / (sum(b) / 60)
            want.append((skill - truth) / se)
        for a, b in zip(got, sorted(want)):
            self.assertAlmostEqual(a, b, places=9)

    def test_the_upper_skill_bound_at_a_critical_value(self):
        days = weekdays(date(2015, 1, 2), 100)
        rng = random.Random(1)
        b = {day: 1 + rng.random() for day in days}
        c = {day: 0.9 + rng.random() for day in days}
        test = sp.paired_test(b, c, seed=1, draws=20)
        self.assertAlmostEqual(test.upper_skill_bound(1.7), test.skill + 1.7 * test.skill_standard_error)


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
    """Verdicts read each comparison's own calibrated values (Eleonora's ruling on PR #695, comment
    6159852603): the efficacy bound at `CRITICAL_VALUES[GRID_COMPARISON]`, futility one-sided at 0.05 at
    every look (non-binding) at `FUTILITY_CRITICAL_VALUES[GRID_COMPARISON]`, and look 1 futility only."""

    def setUp(self):
        rng = random.Random(9)
        self.days = weekdays(date(2015, 1, 2), 250)

        def scores(level, noise=0.05):
            return {day: level + noise * rng.gauss(0, 1) for day in self.days}

        self.b1, self.b2 = scores(1.0), scores(1.2)
        self.strong, self.weak = scores(0.80), scores(0.9999)

    def test_from_scores(self):
        tests = sp.paired_tests(
            [(self.b1, self.strong), (self.b2, self.strong), (self.b1, self.weak), (self.b2, self.weak)],
            seed=1, draws=200,
        )
        self.assertEqual(sp.verdict(tests[0], tests[1], look=3), sp.SUPPORTED)
        self.assertEqual(sp.verdict(tests[2], tests[3], look=3), sp.KILLED)

    def test_the_verdict_reads_the_grid_comparisons_value(self):
        """Supported under a small value for the grid comparison and not under one that puts the bound
        below zero; the five-level comparison's value is not read."""

        tests = sp.paired_tests([(self.b1, self.strong), (self.b2, self.strong)], seed=1, draws=200)
        t_stat = min(t.mean_difference / t.standard_error for t in tests)
        grid = dict(sp.CRITICAL_VALUES[sp.GRID_COMPARISON])
        with mock.patch.dict(sp.CRITICAL_VALUES, {sp.GRID_COMPARISON: {**grid, 250: t_stat * 0.9},
                                                  sp.FIVE_LEVEL_COMPARISON: {60: None, 125: 1e9, 250: 1e9}}):
            self.assertEqual(sp.verdict(tests[0], tests[1], look=3), sp.SUPPORTED)
        with mock.patch.dict(sp.CRITICAL_VALUES, {sp.GRID_COMPARISON: {**grid, 250: t_stat * 1.1}}):
            self.assertNotEqual(sp.verdict(tests[0], tests[1], look=3), sp.SUPPORTED)

    def test_each_leg_reads_its_own_critical_value(self):
        """#929 (finding #913): the leg against B1 reads `CRITICAL_VALUES`, the leg against B2 reads
        `B2_LEG_CRITICAL_VALUES` when one is declared for the look, and otherwise the same value (so nothing moves
        until a ruling declares one). A value that puts the B2 bound below zero stops "Supported" although the B1 leg
        passes, and the reverse.

        Recorded mutation (2026-10-19): in `scoring_protocol.verdict`, `against_b2.lower_bound(b2_critical)` read
        `against_b2.lower_bound(critical)` again (the old single value); this test failed with AttributeError on
        `sp.B2_LEG_CRITICAL_VALUES` on main and, with the attribute present, with AssertionError at the
        high-B2-value case. Not a leakage guard."""

        tests = sp.paired_tests([(self.b1, self.strong), (self.b2, self.strong)], seed=1, draws=200)
        t_b1, t_b2 = (t.mean_difference / t.standard_error for t in tests)
        grid = dict(sp.CRITICAL_VALUES[sp.GRID_COMPARISON])
        low = {**grid, 250: min(t_b1, t_b2) * 0.9}
        with mock.patch.dict(sp.CRITICAL_VALUES, {sp.GRID_COMPARISON: low}):
            self.assertEqual(sp.verdict(tests[0], tests[1], look=3), sp.SUPPORTED)
            with mock.patch.dict(sp.B2_LEG_CRITICAL_VALUES, {sp.GRID_COMPARISON: {**low, 250: t_b2 * 1.1}}):
                self.assertNotEqual(sp.verdict(tests[0], tests[1], look=3), sp.SUPPORTED)
            with mock.patch.dict(sp.B2_LEG_CRITICAL_VALUES, {sp.GRID_COMPARISON: {**low, 250: t_b2 * 0.9}}):
                self.assertEqual(sp.verdict(tests[0], tests[1], look=3), sp.SUPPORTED)
        with mock.patch.dict(sp.CRITICAL_VALUES, {sp.GRID_COMPARISON: {**grid, 250: t_b1 * 1.1}}):
            with mock.patch.dict(sp.B2_LEG_CRITICAL_VALUES, {sp.GRID_COMPARISON: {**grid, 250: t_b2 * 0.9}}):
                self.assertNotEqual(sp.verdict(tests[0], tests[1], look=3), sp.SUPPORTED)

    def test_no_per_leg_value_is_in_force_yet(self):
        """#929 draws the amendment; the values are applied only after Eleonora merges the record."""

        self.assertEqual(sp.B2_LEG_CRITICAL_VALUES, {})

    def test_the_first_look_checks_futility_only(self):
        days = weekdays(date(2015, 1, 2), 60)
        rng = random.Random(2)
        b = {day: 1 + 0.05 * rng.random() for day in days}
        strong = {day: 0.5 + 0.05 * rng.random() for day in days}
        weak = {day: b[day] + 0.001 * rng.gauss(0, 1) for day in days}
        tests = sp.paired_tests([(b, strong), (b, strong), (b, weak), (b, weak)], seed=1, draws=100)
        self.assertEqual(sp.verdict(tests[0], tests[1], look=1), sp.INCONCLUSIVE)
        self.assertEqual(sp.verdict(tests[2], tests[3], look=1), sp.KILLED)

    def test_futility_reads_the_calibrated_upper_bound(self):
        tests = sp.paired_tests([(self.b1, self.weak), (self.b2, self.weak)], seed=1, draws=200)
        upper = tests[0].upper_skill_bound(sp.FUTILITY_CRITICAL_VALUES[sp.GRID_COMPARISON][250])
        self.assertLess(upper, sp.MME)
        futility = dict(sp.FUTILITY_CRITICAL_VALUES[sp.GRID_COMPARISON])
        needed = (sp.MME - tests[0].skill) / tests[0].skill_standard_error
        with mock.patch.dict(sp.FUTILITY_CRITICAL_VALUES, {sp.GRID_COMPARISON: {**futility, 250: needed * 1.01}}):
            self.assertEqual(sp.verdict(tests[0], tests[1], look=3), sp.NOT_SHOWN)

    def test_only_the_protocols_futility_level_is_read(self):
        tests = sp.paired_tests([(self.b1, self.weak), (self.b2, self.weak)], seed=1, draws=200)
        self.assertEqual(sp.verdict(tests[0], tests[1], look=3, futility_level=0.05), sp.KILLED)
        with self.assertRaises(sp.ProtocolError):
            sp.verdict(tests[0], tests[1], look=3, futility_level=0.10)

    def test_a_test_off_the_checkpoint_is_refused(self):
        days = weekdays(date(2015, 1, 2), 100)
        b = {day: 1.0 + 0.01 * i for i, day in enumerate(days)}
        c = {day: 0.9 + 0.02 * (i % 3) for i, day in enumerate(days)}
        tests = sp.paired_tests([(b, c), (b, c)], seed=1, draws=100)
        with self.assertRaises(sp.ProtocolError):
            sp.verdict(tests[0], tests[1], look=3)


class B3ReportTests(unittest.TestCase):
    """#939 (ruling on #768, option a, 19 October 2026): "improves on what we have", a win over B3, is a reported
    comparison only. `report` prints the candidate against B3 on its own five levels, with its bound at
    `CRITICAL_VALUES[FIVE_LEVEL_COMPARISON]`, beside the verdict. It carries no efficacy or futility rule:
    the verdict never reads it."""

    def setUp(self):
        rng = random.Random(9)
        self.days = weekdays(date(2015, 1, 2), 250)

        def scores(level, noise=0.05):
            return {day: level + noise * rng.gauss(0, 1) for day in self.days}

        self.b1, self.b2, self.b3 = scores(1.0), scores(1.2), scores(0.95)
        self.strong, self.weak = scores(0.80), scores(0.9999)
        self.five_strong, self.five_weak = scores(0.70), scores(1.2)

    def paired(self, candidate, five):
        b1, b2, b3 = sp.paired_tests(
            [(self.b1, candidate), (self.b2, candidate), (self.b3, five)], seed=1, draws=200
        )
        return b1, b2, b3

    def test_the_output_prints_the_b3_comparison_and_its_bound_beside_the_verdict(self):
        b1, b2, b3 = self.paired(self.strong, self.five_strong)
        out = sp.report(b1, b2, b3, look=3)
        text = str(out)
        self.assertEqual(out.verdict, sp.SUPPORTED)
        self.assertIn(sp.SUPPORTED, text)
        self.assertIn("B3", text)
        self.assertIn("reported comparison, no rule", text)
        critical = sp.CRITICAL_VALUES[sp.FIVE_LEVEL_COMPARISON][250]
        self.assertEqual(out.b3.critical_value, critical)
        self.assertAlmostEqual(out.b3.lower_bound, b3.lower_bound(critical))
        self.assertAlmostEqual(out.b3.mean_difference, b3.mean_difference)
        self.assertIn(f"{b3.lower_bound(critical):.4f}", text)
        self.assertLess(text.index(sp.SUPPORTED), text.index("reported comparison, no rule"))

    def test_the_first_look_has_no_bound_to_print(self):
        """Look 1 has no efficacy value (Q-B), so the B3 line carries its mean and no bound."""

        days = weekdays(date(2015, 1, 2), 60)
        rng = random.Random(3)
        b = {day: 1 + 0.05 * rng.random() for day in days}
        c = {day: 0.9 + 0.05 * rng.random() for day in days}
        b1, b2, b3 = sp.paired_tests([(b, c), (b, c), (b, c)], seed=1, draws=100)
        out = sp.report(b1, b2, b3, look=1)
        self.assertIsNone(out.b3.critical_value)
        self.assertIsNone(out.b3.lower_bound)
        self.assertIn("no bound at look 1", str(out))

    def test_the_verdict_never_reads_the_b3_comparison(self):
        """The same verdict on every fixture whatever B3 shows, at any five-level value, and `verdict` has no
        B3 input and does not name the five-level comparison."""

        import inspect

        for candidate, expected in ((self.strong, sp.SUPPORTED), (self.weak, sp.KILLED)):
            alone = sp.verdict(*self.paired(candidate, self.five_strong)[:2], look=3)
            self.assertEqual(alone, expected)
            for five in (self.five_strong, self.five_weak):
                for value in (1e-9, 1e9):
                    with mock.patch.dict(sp.CRITICAL_VALUES, {sp.FIVE_LEVEL_COMPARISON: {60: None, 125: value, 250: value}}):
                        b1, b2, b3 = self.paired(candidate, five)
                        self.assertEqual(sp.report(b1, b2, b3, look=3).verdict, expected)
                        self.assertEqual(sp.verdict(b1, b2, look=3), expected)
        self.assertEqual(list(inspect.signature(sp.verdict).parameters)[:2], ["against_b1", "against_b2"])
        self.assertNotIn("b3", inspect.signature(sp.verdict).parameters)
        self.assertNotIn("FIVE_LEVEL_COMPARISON", inspect.getsource(sp.verdict))

    def test_a_b3_test_on_other_days_is_refused(self):
        b1, b2, b3 = self.paired(self.strong, self.five_strong)
        short = weekdays(date(2015, 1, 2), 125)
        other = {day: 1.0 + 0.01 * (i % 7) for i, day in enumerate(short)}
        cand = {day: 0.9 + 0.01 * (i % 5) for i, day in enumerate(short)}
        wrong = sp.paired_test(other, cand, seed=1, draws=100)
        with self.assertRaises(sp.ProtocolError):
            sp.report(b1, b2, wrong, look=3)


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


class ReportedBoundLabelTests(unittest.TestCase):
    """Eleonora's ruling on #737 (Q-1, 14 Oct 2026): bounds reported outside a verdict stay descriptive and
    say so. Only `verdict` reads the calibrated values."""

    def test_reported_bounds_are_labelled_not_the_verdict_bound(self):
        for method in (sp.PairedTest.lower_mean_difference, sp.PairedTest.upper_skill):
            self.assertIn("not the verdict bound", method.__doc__)

    def test_the_decision_record_status_is_in_force(self):
        text = (Path(__file__).resolve().parent.parent / "docs" / "decisions" / "scoring-protocol.md").read_text()
        status = text.split("\n\n", 2)[1]
        self.assertTrue(status.startswith("**Status: In force"), status)
        self.assertIn("13 October 2026", status)
        self.assertNotIn("DRAFT", status)


class HolmTests(unittest.TestCase):
    def test_step_down(self):
        self.assertEqual(sp.holm({"a": 0.01, "b": 0.04}), {"a": True, "b": True})
        self.assertEqual(sp.holm({"a": 0.03, "b": 0.04}), {"a": False, "b": False})
        self.assertEqual(sp.holm({"a": 0.02, "b": 0.06}), {"a": True, "b": False})


if __name__ == "__main__":
    unittest.main()
