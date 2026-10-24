"""Calm and stress spells on the H5 candidate (#1182; H5 step 3, fix: clustered misses).

`metadata/regime_spells_1182.json` is the declaration; `repo_model.spread_mr_regime` is its arithmetic. What these tests pin: the
episode state (a miss on any of the last k rows, never a later row) and the pools it picks (the full pool where a state has fewer
than 60 origins); the Hamilton filter on a hand case, and that a future residual moves no filtered probability; that EM recovers a
planted two-state chain, never lowers the likelihood, and with no calendar flags is the (m2) fit; that a planted calendar-driven
entry is recovered and read from the day entered, never one row off; that a scheduled flag is read only where `asof` rule 2
admits it; the weighted mixture of the pool (a single state returns `empirical_quantiles` exactly); that an arm whose two scales are
equal is (s3); that a one-step fit of the calendar columns is refused by the guard of #947; and that no arm's forecast moves with a
spread after the anchor.

Recorded mutations (each applied to the tree, the named test run, and reverted):

* `episode_rows`: `range(max(0, row - k + 1), row + 1)` replaced with `range(max(0, row - k + 1), row + 2)`, so the episode flag
  at a row reads the next row's miss. `test_the_episode_window_never_passes_the_row` failed with `AssertionError`
  (`True is not false`), and `test_a_miss_after_the_row_does_not_make_an_episode` with `AssertionError` (`1 != 0`).
* `Track._require_read`: `if row >= self.next:` replaced with `if row > self.next:`, so the filtered probability of the first row
  not yet read is served. `test_a_row_not_yet_read_is_refused` failed with `AssertionError` (`LookAheadError` not raised).
* `Track.collect`: `while self.next <= upto:` replaced with `while self.next <= upto + 1:`, so the track reads the residual of the
  row after the anchor. `WalkTests.setUpClass` raised `LookAheadError` ("the one-step residual of row ... is asked for beyond the
  last public row").
* `entry_flags`: `row - 1 > decision_row` replaced with `row - 1 > decision_row + 1`, so a coupon settlement two days ahead is
  read as if public. `test_a_scheduled_flag_is_read_only_where_it_is_public` failed with `AssertionError` (`1.0 != 0.0`).
* `Source.x`: `entry_flags(self.table, j, j - 1)` replaced with `entry_flags(self.table, j - 1, j - 1)`, so the flags of the day
  before the one entered are read (the #914 class). `test_the_entry_flags_are_those_of_the_day_entered` failed with
  `AssertionError` (`0.0 != 1.0`).
* `fit_regimes`: delete the `@guard_one_step_fit` line. `test_a_one_step_fit_of_the_calendar_columns_is_refused_by_the_guard`
  failed with `AssertionError` (the `ValueError` raised was the function's own "direct pairs only", not the guard's message naming
  the column).
"""

from __future__ import annotations

import dataclasses
import math
import random
import unittest
from datetime import date

from repo_model import protocol_benchmarks as pb
from repo_model import spread_mr_calendar as cal
from repo_model import spread_mr_regime as rg
from repo_model import spread_mr_state_calendar as sc
from repo_model.splits import LookAheadError

import test_protocol_benchmarks as tpb
from test_spread_mr_state_calendar import PANEL, SETTINGS, TABLE_ALL, index_of

WIDTH = len(rg.ENTRY_TERMS)
NO_X = (0.0,) * WIDTH


def params(sigma=(1.0, 3.0), p01=0.1, stay=0.8, slopes=(0.0,) * WIDTH):
    return rg.Params(sigma, math.log(p01 / (1.0 - p01)), tuple(slopes), stay, 0.0, 0, False)


def simulate(n, *, sigma=(0.6, 2.5), p01=0.04, stay=0.92, flagged=None, seed=7):
    """A planted chain: the residuals, the true states and the entry flags (`flagged` is the entry probability on a flagged day)."""

    rng = random.Random(seed)
    z, states, xs = [], [], []
    state = 0
    for t in range(n):
        x = list(NO_X)
        if flagged is not None and t % 20 == 0:
            x[1] = 1.0
        enter = flagged if (flagged is not None and x[1]) else p01
        state = (1 if rng.random() < stay else 0) if state else (1 if rng.random() < enter else 0)
        z.append(rng.gauss(0.0, sigma[state]))
        states.append(state)
        xs.append(x)
    return z, states, xs


def gauss_pool(n, seed):
    rng = random.Random(seed)
    return sorted(rng.gauss(0.0, 1.0) for _ in range(n))


class EpisodeTests(unittest.TestCase):

    def test_the_episode_window_never_passes_the_row(self):
        for row in (0, 2, 40, 900):
            for k in rg.K_EPISODE:
                self.assertFalse(any(j > row for j in rg.episode_rows(row, k)), (row, k))
        self.assertEqual(list(rg.episode_rows(10, 3)), [8, 9, 10])
        self.assertEqual(list(rg.episode_rows(1, 5)), [0, 1])

    def test_a_miss_in_the_last_k_rows_makes_an_episode(self):
        misses = {10: 1}
        self.assertEqual([rg.episode_flag(misses, r, 3) for r in (9, 10, 11, 12, 13)], [0, 1, 1, 1, 0])
        self.assertEqual([rg.episode_flag(misses, r, 5) for r in (13, 14, 15)], [1, 1, 0])

    def test_a_miss_after_the_row_does_not_make_an_episode(self):
        self.assertEqual(rg.episode_flag({11: 1, 12: 1}, 10, 3), 0)

    def test_the_memory_is_at_least_one_row(self):
        with self.assertRaises(ValueError):
            rg.episode_rows(5, 0)

    def test_the_band_is_the_5th_and_95th_percentile_and_a_miss_is_strictly_outside(self):
        zs = [float(v) for v in range(-50, 51)]
        lo, hi = rg.band_of(zs)
        self.assertAlmostEqual(lo, -45.0)
        self.assertAlmostEqual(hi, 45.0)
        self.assertEqual([rg.is_miss(v, (lo, hi)) for v in (-46.0, -45.0, 0.0, 45.0, 45.5, None)], [1, 0, 0, 0, 1, 0])

    def test_a_state_with_fewer_than_sixty_origins_has_no_pool_of_its_own(self):
        residuals = [float(i) for i in range(200)]
        flags = [1 if i < rg.MIN_STATE_POOL - 1 else 0 for i in range(200)]
        self.assertIsNone(rg.state_pool(residuals, flags, 1))
        flags[rg.MIN_STATE_POOL - 1] = 1
        self.assertEqual(rg.state_pool(residuals, flags, 1), residuals[: rg.MIN_STATE_POOL])
        self.assertEqual(len(rg.state_pool(residuals, flags, 0)), 200 - rg.MIN_STATE_POOL)

    def estimate(self, pool):
        return sc.StateEstimate((), {}, {}, {}, pb.empirical_quantiles(sorted(pool)), len(pool), 0, 0)

    def test_the_forecast_takes_the_pool_of_its_own_state_or_the_full_pool(self):
        rng = random.Random(1)
        calm = tuple(sorted(rng.gauss(0, 1) for _ in range(100)))
        episode = tuple(sorted(rng.gauss(0, 3) for _ in range(100)))
        lead = rg.EpisodeLead(self.estimate(list(calm) + list(episode)), calm, episode, 100, 100)
        kw = dict(centre=5.0, scale=2.0, flags={})
        quiet = rg.episode_quantiles(lead, in_episode=0, **kw)
        loud = rg.episode_quantiles(lead, in_episode=1, **kw)
        self.assertEqual(quiet, [5.0 + 2.0 * v for v in pb.empirical_quantiles(list(calm))])
        self.assertEqual(loud, [5.0 + 2.0 * v for v in pb.empirical_quantiles(list(episode))])
        self.assertGreater(loud[-1] - loud[0], quiet[-1] - quiet[0])
        short = dataclasses.replace(lead, episode=None)
        self.assertEqual(rg.episode_quantiles(short, in_episode=1, **kw), [5.0 + 2.0 * v for v in lead.estimate.pool])


class FilterTests(unittest.TestCase):

    def test_the_hamilton_step_on_a_hand_case(self):
        # prior stress 0.1 from calm; likelihoods at z = 0 are 1/1 and 1/3
        got = rg.filter_step(0.0, 0.0, None, params(sigma=(1.0, 3.0), p01=0.1, stay=0.8))
        self.assertAlmostEqual(got, (0.1 / 3.0) / (0.1 / 3.0 + 0.9), places=12)

    def test_a_large_residual_moves_the_probability_to_stress_and_a_small_one_to_calm(self):
        p = params()
        self.assertGreater(rg.filter_step(0.1, 9.0, None, p), 0.99)
        self.assertLess(rg.filter_step(0.9, 0.0, None, p), 0.5)
        self.assertAlmostEqual(rg.filter_step(0.3, None, None, p), 0.7 * 0.1 + 0.3 * 0.8)

    def test_an_extreme_residual_does_not_underflow(self):
        self.assertAlmostEqual(rg.filter_step(0.0, 1e4, None, params()), 1.0)

    def test_the_probability_after_a_row_reads_no_later_residual(self):
        z, _, _ = simulate(300)
        full = rg.filter_series(z, None, params())
        for t in (0, 5, 120, 299):
            self.assertEqual(rg.filter_series(z[: t + 1], None, params())[-1], full[t])
        other = z[:150] + [50.0] * 150
        self.assertEqual(rg.filter_series(other, None, params())[:150], full[:150])

    def test_the_stress_probability_after_steps_follows_the_chain(self):
        p = params(p01=0.1, stay=0.8)
        self.assertAlmostEqual(rg.stress_after(0.0, [None], p), 0.1)
        self.assertAlmostEqual(rg.stress_after(0.0, [None, None], p), 0.9 * 0.1 + 0.1 * 0.8)
        self.assertAlmostEqual(rg.stress_after(1.0, [], p), 1.0)
        loaded = params(p01=0.1, slopes=(0.0, 3.0, 0.0, 0.0))
        self.assertGreater(rg.stress_after(0.0, [(0.0, 1.0, 0.0, 0.0)], loaded), rg.stress_after(0.0, [NO_X], loaded))


class FitTests(unittest.TestCase):

    def fit(self, z, xs=None, **kw):
        regressors = () if xs is None else rg.ENTRY_REGRESSORS
        return rg.fit_regimes(z, xs, regressors=regressors, training_pairs="direct", **kw)

    def test_em_recovers_a_planted_chain(self):
        z, _, _ = simulate(4000)
        got = self.fit(z)
        self.assertFalse(got.degenerate)
        self.assertTrue(0.5 < got.sigma[0] < 0.72, got.sigma)
        self.assertTrue(2.0 < got.sigma[1] < 3.1, got.sigma)
        self.assertTrue(0.85 < got.stay < 0.97, got.stay)
        self.assertTrue(0.02 < rg.entry_prob(got, None) < 0.08, rg.entry_prob(got, None))
        self.assertEqual(got.slopes, (0.0,) * WIDTH)

    def test_em_never_lowers_the_likelihood(self):
        z, _, _ = simulate(1500)
        trace = []
        self.fit(z, trace=trace)
        self.assertGreater(len(trace), 3)
        # the first state's prior is the chain's stationary share, which the M-step does not maximise: a rise to within 1e-3
        self.assertTrue(all(b >= a - 1e-3 for a, b in zip(trace, trace[1:])), trace)
        self.assertGreater(trace[-1], trace[0] + 50.0)

    def test_a_planted_calendar_entry_is_recovered_on_the_flag_that_drives_it(self):
        z, _, xs = simulate(6000, flagged=0.6, p01=0.01)
        got = self.fit(z, xs)
        self.assertGreater(got.slopes[1], 1.5, got.slopes)
        self.assertTrue(all(abs(got.slopes[i]) < 1.0 for i in (0, 2, 3)), got.slopes)
        self.assertGreater(rg.entry_prob(got, (0.0, 1.0, 0.0, 0.0)), 5 * rg.entry_prob(got, None))

    def test_with_no_flag_the_calendar_fit_is_the_constant_entry_fit(self):
        z, _, _ = simulate(1500)
        plain = self.fit(z)
        flat = self.fit(z, [NO_X] * len(z))
        self.assertAlmostEqual(plain.intercept, flat.intercept, places=5)
        self.assertEqual(flat.slopes, (0.0,) * WIDTH)
        self.assertAlmostEqual(plain.sigma[1], flat.sigma[1], places=6)
        self.assertAlmostEqual(plain.stay, flat.stay, places=6)

    def test_a_series_with_one_scale_is_degenerate(self):
        got = self.fit([1.0 if i % 3 else -1.0 for i in range(800)])
        self.assertTrue(got.degenerate)
        self.assertEqual(got.sigma[0], got.sigma[1])

    def test_a_short_series_is_degenerate(self):
        got = self.fit([0.1 * (i % 7 - 3) for i in range(rg.MIN_OBSERVATIONS - 1)])
        self.assertTrue(got.degenerate)

    def test_missing_residuals_are_skipped_not_zero(self):
        z, _, _ = simulate(3000)
        holes = [None if i % 11 == 0 else v for i, v in enumerate(z)]
        got = self.fit(holes)
        self.assertTrue(0.45 < got.sigma[0] < 0.8, got.sigma)
        self.assertTrue(1.9 < got.sigma[1] < 3.3, got.sigma)

    def test_the_flags_must_match_the_residuals(self):
        with self.assertRaises(ValueError):
            self.fit([0.0] * 200, [NO_X] * 199)

    def test_a_one_step_fit_of_the_calendar_columns_is_refused_by_the_guard(self):
        z, _, xs = simulate(300)
        with self.assertRaisesRegex(ValueError, "one-step pairs"):
            rg.fit_regimes(z, xs, regressors=rg.ENTRY_REGRESSORS, training_pairs="one_step")
        self.assertIsNotNone(rg.fit_regimes(z, xs, regressors=rg.ENTRY_REGRESSORS, training_pairs="direct"))

    def test_a_chain_with_no_calendar_column_has_nothing_to_refuse_but_still_trains_direct(self):
        with self.assertRaisesRegex(ValueError, "direct pairs only"):
            rg.fit_regimes([0.0] * 300, None, regressors=(), training_pairs="one_step")


class MixtureTests(unittest.TestCase):

    POOL = gauss_pool(173, 5)

    def test_a_single_state_is_empirical_quantiles_scaled(self):
        for stress, sigma in ((0.0, 2.0), (1.0, 5.0)):
            got = rg.mixture_quantiles(self.POOL, (2.0, 5.0), stress)
            want = [sigma * q for q in pb.empirical_quantiles(self.POOL)]
            for a, b in zip(got, want):
                self.assertAlmostEqual(a, b, places=12)

    def test_equal_scales_return_the_pool_whatever_the_probability(self):
        want = pb.empirical_quantiles(self.POOL)
        for stress in (0.0, 0.3, 0.77, 1.0):
            for a, b in zip(rg.mixture_quantiles(self.POOL, (1.0, 1.0), stress), want):
                self.assertAlmostEqual(a, b, places=9)

    def test_nearly_equal_scales_are_nearly_the_pool(self):
        want = pb.empirical_quantiles(self.POOL)
        for a, b in zip(rg.mixture_quantiles(self.POOL, (1.0, 1.0001), 0.5), want):
            self.assertAlmostEqual(a, b, places=3)

    def test_the_mixture_is_ordered_and_widens_with_the_stress_probability(self):
        widths = []
        for stress in (0.0, 0.25, 0.5, 0.75, 1.0):
            q = rg.mixture_quantiles(self.POOL, (1.0, 3.0), stress)
            self.assertEqual(len(q), 23)
            self.assertEqual(q, sorted(q))
            widths.append(q[-1] - q[0])
        self.assertEqual(widths, sorted(widths))
        self.assertLess(widths[0], widths[-1])

    def test_the_median_of_a_symmetric_pool_stays_put(self):
        pool = sorted([-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0])
        q = rg.mixture_quantiles(pool, (1.0, 4.0), 0.4)
        self.assertAlmostEqual(q[11], 0.0, places=9)

    def test_a_probability_outside_the_unit_interval_or_an_empty_pool_is_refused(self):
        with self.assertRaises(ValueError):
            rg.mixture_quantiles(self.POOL, (1.0, 2.0), 1.2)
        with self.assertRaises(ValueError):
            rg.mixture_quantiles([], (1.0, 2.0), 0.5)

    def test_the_markov_forecast_with_equal_scales_is_the_pool_of_s3(self):
        rng = random.Random(9)
        pool = [rng.gauss(0, 1) for _ in range(150)]
        est = sc.StateEstimate((), {}, {}, {}, pb.empirical_quantiles(sorted(pool)), 150, 0, 0)
        lead = rg.MarkovLead(est, tuple(sorted(pool)), 1)
        same = rg.markov_quantiles(lead, params(sigma=(1.0, 1.0)), centre=3.0, scale=2.0, flags={}, stress=0.4)
        for a, b in zip(same, (3.0 + 2.0 * v for v in est.pool)):
            self.assertAlmostEqual(a, b, places=9)


class PoolTests(unittest.TestCase):

    def test_the_pool_is_divided_by_the_scale_of_the_state_at_each_target(self):
        source = FakeSource(lambda j: 0.0, 40)
        track = rg.Track(5)
        track.collect(source, 40)
        p = params(sigma=(1.0, 4.0))
        track.calibrate((-1.0, 1.0), {"m2_markov": (p, False)}, source)
        track.filters["m2_markov"].f.update({20: 1.0, 21: 0.0})
        est = sc.StateEstimate((), {}, {}, {}, [0.0] * 23, 2, 0, 0, False, (18, 19), (20, 21), (8.0, 8.0))
        lead = rg._markov_lead(est, "m2_markov", track, p, 2)
        self.assertEqual(lead.pool, (2.0, 8.0))

    def test_a_target_after_the_last_row_read_is_refused(self):
        source = FakeSource(lambda j: 0.0, 40)
        track = rg.Track(5)
        track.collect(source, 30)
        track.calibrate((-1.0, 1.0), {"m2_markov": (params(), False)}, source)
        est = sc.StateEstimate((), {}, {}, {}, [0.0] * 23, 1, 0, 0, False, (30,), (32,), (1.0,))
        with self.assertRaises(LookAheadError):
            rg._markov_lead(est, "m2_markov", track, params(), 2)


class FakeSource:
    """A source whose residual of row `j` is `rule(j)`, for a track without a panel."""

    def __init__(self, rule, last):
        self.rule, self.last = rule, last

    def z(self, j):
        if j > self.last:
            raise LookAheadError(f"row {j} is after the last public row {self.last}")
        return self.rule(j)

    def x(self, j):
        return list(NO_X)


class TrackTests(unittest.TestCase):

    def track(self, rule, upto, last=None):
        source = FakeSource(rule, upto if last is None else last)
        track = rg.Track(5)
        track.collect(source, upto)
        track.calibrate((-1.0, 1.0), {"m2_markov": (params(), False)}, source)
        return track, source

    def test_a_row_not_yet_read_is_refused(self):
        track, _ = self.track(lambda j: 0.0, 40)
        self.assertEqual(track.next, 41)
        for call in (lambda: track.episode(41, 3), lambda: track.stress("m2_markov", 41)):
            with self.assertRaises(LookAheadError):
                call()
        self.assertEqual(track.episode(40, 3), 0)

    def test_the_misses_and_filters_of_a_row_do_not_depend_on_later_rows(self):
        a, _ = self.track(lambda j: 5.0 if j == 20 else 0.1, 30)
        b, _ = self.track(lambda j: 5.0 if j == 20 else (9.0 if j > 25 else 0.1), 40)
        for row in range(5, 26):
            self.assertEqual(a.episode(row, 5), b.episode(row, 5), row)
            self.assertEqual(a.stress("m2_markov", row), b.stress("m2_markov", row), row)

    def test_a_miss_starts_an_episode_that_lasts_k_rows(self):
        track, _ = self.track(lambda j: 5.0 if j == 20 else 0.1, 40)
        self.assertEqual([track.episode(r, 3) for r in (19, 20, 21, 22, 23)], [0, 1, 1, 1, 0])
        self.assertEqual([track.episode(r, 5) for r in (24, 25)], [1, 0])

    def test_a_filter_advanced_later_equals_one_run_in_one_go(self):
        rule = lambda j: 4.0 if j % 9 == 0 else 0.2  # noqa: E731
        whole, _ = self.track(rule, 60)
        part, source = self.track(rule, 30)
        part.advance(source_with(rule, 60), 60)
        for row in range(5, 61):
            self.assertEqual(whole.stress("m2_markov", row), part.stress("m2_markov", row), row)
            self.assertEqual(whole.episode(row, 3), part.episode(row, 3), row)

    def test_the_stress_probability_before_the_track_is_the_stationary_share(self):
        track, _ = self.track(lambda j: 0.0, 20)
        self.assertAlmostEqual(track.stress("m2_markov", 2), rg.stationary_stress(params()))


def source_with(rule, last):
    return FakeSource(rule, last)


class CalendarTests(unittest.TestCase):

    def row_where(self, term, *, skip=60):
        return next(i for i in range(skip, len(PANEL)) if TABLE_ALL.flags_at(1, i)[term])

    def test_a_scheduled_flag_is_read_only_where_it_is_public(self):
        r = self.row_where("settlement_coupon")
        idx = rg.ENTRY_TERMS.index("settlement_coupon")
        self.assertEqual(rg.entry_flags(TABLE_ALL, r, r - 1)[idx], 1.0)
        self.assertEqual(rg.entry_flags(TABLE_ALL, r, r - 2)[idx], 0.0)
        self.assertEqual(rg.entry_flags(TABLE_ALL, r, r - 6)[idx], 0.0)

    def test_a_calendar_column_is_read_at_any_distance(self):
        r = self.row_where("quarter_end")
        idx = rg.ENTRY_TERMS.index("quarter_end")
        for gap in (1, 2, 6):
            self.assertEqual(rg.entry_flags(TABLE_ALL, r, r - gap)[idx], 1.0, gap)

    def test_the_entry_flags_are_those_of_the_day_entered(self):
        r = self.row_where("quarter_end")
        idx = rg.ENTRY_TERMS.index("quarter_end")
        source = rg.Source([0.0] * (r + 2), [None] * (r + 2), 0.5, TABLE_ALL, None)
        self.assertEqual(source.x(r)[idx], 1.0)
        self.assertEqual(source.x(r - 1)[idx], 0.0)
        self.assertEqual(source.x(r + 1)[idx], 0.0)

    def test_the_declared_terms_exist_and_the_regressors_name_their_columns(self):
        self.assertEqual(len(rg.ENTRY_TERMS), len(rg.ENTRY_REGRESSORS))
        self.assertTrue(all(name in cal.TERM for name in rg.ENTRY_TERMS))
        self.assertEqual(
            [cal.TERM[name].reads[0] for name in rg.ENTRY_TERMS], list(rg.ENTRY_REGRESSORS))


class DeclaredArmsTests(unittest.TestCase):

    def test_the_arms_are_the_declared_four(self):
        self.assertEqual([a.name for a in rg.ARMS], ["m1_episode_k3", "m1_episode_k5", "m2_markov", "m3_markov_calendar"])
        self.assertEqual([(a.kind, a.k) for a in rg.ARMS],
                         [("episode", 3), ("episode", 5), ("markov", 0), ("markov_calendar", 0)])
        self.assertEqual(rg.K_EPISODE, (3, 5))

    def test_the_base_is_arm_s3(self):
        self.assertEqual(rg.BASE_ARM, sc.ARMS[2])
        self.assertTrue(rg.BASE_ARM.robust)


class WalkTests(unittest.TestCase):

    DAYS = [row.date for row in PANEL if date(2024, 6, 3) <= row.date <= date(2024, 6, 7)]

    @classmethod
    def setUpClass(cls):
        cls.walk = rg.walk(PANEL, cls.DAYS, TABLE_ALL, **SETTINGS)
        cls.reference = sc.walk(PANEL, cls.DAYS, TABLE_ALL, {}, [rg.BASE_ARM], **SETTINGS)

    def test_arm_a_and_arm_s3_are_the_published_walks_exactly(self):
        self.assertEqual(self.walk.forecasts[rg.ARM_A], self.reference.forecasts[rg.ARM_A])
        self.assertEqual(self.walk.forecasts[rg.BASE_ARM.name], self.reference.forecasts[rg.BASE_ARM.name])

    def test_every_model_has_23_ordered_quantiles_at_every_lead_on_the_same_days(self):
        days = set(self.walk.forecasts[rg.ARM_A])
        self.assertTrue(days)
        for name in rg.MODEL_NAMES:
            self.assertEqual(set(self.walk.forecasts[name]), days)
            for leads in self.walk.forecasts[name].values():
                for q in leads.values():
                    self.assertEqual(len(q), 23)
                    self.assertEqual(q, sorted(q))

    def test_the_detail_holds_the_state_each_arm_read(self):
        for day, detail in self.walk.detail.items():
            self.assertIn(detail["m1_episode_k3"], (0, 1))
            self.assertIn(detail["m1_episode_k5"], (0, 1))
            self.assertLessEqual(detail["m1_episode_k3"], detail["m1_episode_k5"])
            for name in ("m2_markov", "m3_markov_calendar"):
                self.assertTrue(0.0 <= detail[name] <= 1.0, (day, name))

    def test_a_future_spread_moves_no_forecast(self):
        di = index_of("2024-06-07")
        panel = list(PANEL)
        for i in range(di + 1, len(panel)):
            values = dict(panel[i].values)
            values["sofr"] = float(values["iorb"]) + 40.0
            panel[i] = dataclasses.replace(panel[i], values=values)
        other = rg.walk(panel, [PANEL[di].date], TABLE_ALL, **SETTINGS)
        base = rg.walk(PANEL, [PANEL[di].date], TABLE_ALL, **SETTINGS)
        self.assertEqual(other.forecasts, base.forecasts)
        self.assertEqual(other.detail, base.detail)

    def test_the_spread_at_the_anchor_moves_the_state_arms(self):
        di = index_of("2024-06-07")
        anchor = di - 1
        panel = list(PANEL)
        values = dict(panel[anchor].values)
        values["sofr"] = float(values["iorb"]) + 60.0
        panel[anchor] = dataclasses.replace(panel[anchor], values=values)
        other = rg.walk(panel, [PANEL[di].date], TABLE_ALL, **SETTINGS)
        base = rg.walk(PANEL, [PANEL[di].date], TABLE_ALL, **SETTINGS)
        for name in ("m2_markov", "m3_markov_calendar"):
            self.assertGreater(other.detail[PANEL[di].date][name], base.detail[PANEL[di].date][name])
            self.assertNotEqual(other.forecasts[name], base.forecasts[name])
        self.assertEqual(other.detail[PANEL[di].date]["m1_episode_k3"], 1)

    def test_the_one_step_walk_is_refused(self):
        with self.assertRaisesRegex(ValueError, "one-step pairs"):
            rg.walk(PANEL, self.DAYS[:2], TABLE_ALL, **SETTINGS, training_pairs="one_step")

    def test_the_fits_are_renewed_with_the_base_model(self):
        self.assertEqual(len(self.walk.fits), 1)
        self.assertEqual(set(self.walk.regimes), set(self.walk.fits))
        fitted = next(iter(self.walk.regimes.values()))
        self.assertEqual(set(fitted.params), {"m2_markov", "m3_markov_calendar"})
        self.assertLess(fitted.band[0], 0.0)
        self.assertGreater(fitted.band[1], 0.0)


if __name__ == "__main__":
    unittest.main()
