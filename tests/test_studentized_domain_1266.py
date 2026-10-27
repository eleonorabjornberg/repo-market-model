"""The studentized domain interval of a non-contiguous day-type group (#1266; H5 step 3 reporting, H1 scorer).

Written first, and watched fail (`ImportError: cannot import name 'studentized_domain_estimates'`). #1228 resampled the whole aligned
series and took the mean over the resampled days of the group, as a percentile interval. This adds the studentization the pooled
test has: each resample's group mean is divided by its own HAC standard error, and a bound is the group mean less a quantile of those
t-draws times the HAC standard error of the original series. The standard error of a mean over a subset of the days is the delta
method on the whole-series frame: with `I_t` the indicator that the day at position `t` of the resample is in the group, `K = sum I_t`
and `m` the group mean, the series `u_t = I_t (d_t - m)` has the Newey-West (Bartlett, lag 10) long-run variance `V`, and
`se = sqrt(V / n) * n / K`. These tests pin:

* the draws are the pooled test's (`random.Random(seed)` through `stationary_bootstrap_indices`), checked against a naive loop that
  builds the resampled sequence and its long-run variance by hand;
* a group of every day is the pooled test: the interval equals `scoring_protocol.paired_tests`' studentized interval to rounding;
* the point estimate is the group mean; a resample that draws no day of the group is not dropped (the group is recorded unavailable
  with the reason); a resample whose long-run variance is not positive is dropped and counted, as #1239 does for the pooled test;
* on a synthetic AR(1) series with group days 60 apart the coverage of the one-sided 95% lower bound is measured beside the current
  and the percentile-domain intervals.

Mutation 1 (the studentization must use each resample's own standard error): in `domain_intervals.studentized_domain_estimates`,
replacing the resample's `se` in `t = (mean - point) / se` by the original series' standard error made
`test_a_group_of_every_day_is_the_pooled_test` fail with `AssertionError: 0.2578... != 0.2510... within 9 places` (and the definition test with `AssertionError`).

Mutation 2 (a resample with no day of the group must not be dropped): replacing the `if drawn == 0:` branch that records the group
as unavailable by `continue` made `test_a_resample_without_a_group_day_is_unavailable_not_dropped` fail with `AssertionError`
(`'interval_unavailable' not found in {'count': 8, ..., 'interval': {...}}`).
"""

from __future__ import annotations

import importlib.util
import math
import random
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import scoring_protocol as sp
from repo_model.domain_intervals import domain_estimates, studentized_domain_estimates
from repo_model.metrics import MetricError, _quantile, stationary_bootstrap_indices

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("spread_mr_variants_761", ROOT / "scripts" / "spread_mr_variants_761.py")
s761 = importlib.util.module_from_spec(_spec)
sys.modules["spread_mr_variants_761"] = s761
_spec.loader.exec_module(s761)

SETTINGS = dict(block_length=10, seed=1266, replications=300, level=0.90)


def ar1(n, phi, mean, seed):
    rng = random.Random(seed)
    x, out = 0.0, []
    for _ in range(n):
        x = phi * x + rng.gauss(0.0, 1.0)
        out.append(mean + x)
    return out


def lrv(u, lag):
    """Bartlett long-run variance by hand: the sum of the weighted autocovariances over n."""

    n = len(u)
    mean = sum(u) / n
    c = [x - mean for x in u]
    total = sum(x * x for x in c)
    for k in range(1, lag + 1):
        total += 2.0 * (1.0 - k / (lag + 1.0)) * sum(c[t] * c[t - k] for t in range(k, n))
    return total / n


def naive(series, members, n, block_length, seed, replications, level, lag=10):
    """The studentized domain interval by the definition, with explicit loops."""

    member = set(members)

    def stat(order):
        sub = [series[i] for i in order if i in member]
        m = sum(sub) / len(sub)
        u = [(series[i] - m) if i in member else 0.0 for i in order]
        return m, math.sqrt(lrv(u, lag) / n) * n / len(sub)

    point, se = stat(list(range(n)))
    rng = random.Random(seed)
    t = []
    for _ in range(replications):
        order = stationary_bootstrap_indices(n, block_length, rng)
        m, s = stat(order)
        t.append((m - point) / s)
    t.sort()
    tail = (1.0 - level) / 2.0
    return point - _quantile(t, 1.0 - tail) * se, point - _quantile(t, tail) * se, point, se


class StudentizedDomain(unittest.TestCase):

    def setUp(self):
        self.n = 240
        self.series = ar1(self.n, 0.4, 0.3, 7)
        self.members = list(range(5, self.n, 24))
        self.eight = list(range(5, self.n, 30))

    def test_it_is_the_definition_on_the_pooled_tests_draws(self):
        out = studentized_domain_estimates({"g": (self.series, self.members)}, self.n, **SETTINGS)["g"]
        lower, upper, point, se = naive(self.series, self.members, self.n, 10, 1266, 300, 0.90)
        self.assertAlmostEqual(out["mean"], point, places=12)
        self.assertAlmostEqual(out["standard_error"], se, places=10)
        self.assertAlmostEqual(out["interval"]["lower"], lower, places=9)
        self.assertAlmostEqual(out["interval"]["upper"], upper, places=9)
        self.assertEqual((out["count"], out["dropped_resamples"]), (len(self.members), 0))

    def test_a_group_of_every_day_is_the_pooled_test(self):
        days = [date(2020, 1, 1) + timedelta(days=i) for i in range(self.n)]
        bench = {day: 5.0 for day in days}
        cand = {day: 5.0 - self.series[i] for i, day in enumerate(days)}
        test = sp.paired_tests([(bench, cand)], seed=1266, draws=300, with_skill=False)[0]
        pooled = s761.studentized_interval(test.mean_difference, test.standard_error, test.t_draws)
        out = studentized_domain_estimates({"all": (self.series, list(range(self.n)))}, self.n, **SETTINGS)["all"]
        self.assertAlmostEqual(out["interval"]["lower"], pooled[0], places=9)
        self.assertAlmostEqual(out["interval"]["upper"], pooled[1], places=9)

    def test_the_draws_are_the_percentile_domain_draws(self):
        # the same stream: the percentile interval of #1228 on these cells is unchanged by asking for both
        before = domain_estimates({"g": (self.series, self.members)}, self.n, **SETTINGS)["g"]
        studentized_domain_estimates({"g": (self.series, self.members)}, self.n, **SETTINGS)
        again = domain_estimates({"g": (self.series, self.members)}, self.n, **SETTINGS)["g"]
        self.assertEqual(before, again)

    def test_groups_share_one_stream_and_do_not_depend_on_each_other(self):
        other = list(range(3, self.n, 11))
        both = studentized_domain_estimates({"a": (self.series, self.members), "b": (self.series, other)}, self.n, **SETTINGS)
        alone = studentized_domain_estimates({"b": (self.series, other)}, self.n, **SETTINGS)
        self.assertEqual(both["b"], alone["b"])

    def test_a_resample_without_a_group_day_is_unavailable_not_dropped(self):
        out = studentized_domain_estimates({"g": (self.series, self.eight)}, self.n, block_length=1, seed=1266, replications=1500, level=0.90)["g"]
        self.assertIn("interval_unavailable", out)
        self.assertNotIn("interval", out)
        self.assertIn("no day of the group", out["interval_unavailable"])

    def test_a_group_without_long_run_variance_is_unavailable(self):
        flat = [1.0] * self.n
        out = studentized_domain_estimates({"g": (flat, self.members)}, self.n, **SETTINGS)["g"]
        self.assertIn("no long-run variance", out["interval_unavailable"])
        one = studentized_domain_estimates({"g": (self.series, [100])}, self.n, **SETTINGS)["g"]
        self.assertIn("no long-run variance", one["interval_unavailable"])

    def test_a_resample_without_variance_is_dropped_and_counted(self):
        # an eight-day group: some resamples draw a single group day (one value, so u = 0 and no variance): they are dropped and
        # counted (seed 1267: 9 of 1500; seed 1266 draws no group day at all in one resample, which is the test above)
        out = studentized_domain_estimates({"g": (self.series, self.eight)}, self.n, block_length=1, seed=1267, replications=1500, level=0.90)["g"]
        self.assertGreater(out["dropped_resamples"], 0)
        self.assertEqual(out["draws"], 1500)
        self.assertIn("interval", out)

    def test_bad_input_is_refused(self):
        with self.assertRaises(ValueError):
            studentized_domain_estimates({"g": (self.series[:-1], self.members)}, self.n, **SETTINGS)
        with self.assertRaises(ValueError):
            studentized_domain_estimates({"g": (self.series, [self.n])}, self.n, **SETTINGS)
        with self.assertRaises(ValueError):
            studentized_domain_estimates({"g": (self.series, self.members)}, 10, **SETTINGS)
        with self.assertRaises(MetricError):
            studentized_domain_estimates({"g": (self.series, self.members)}, self.n, **{**SETTINGS, "seed": None})
        with self.assertRaises(MetricError):
            studentized_domain_estimates({"g": (self.series, self.members)}, self.n, **{**SETTINGS, "level": 1.0})


class CoverageBesideTheOthers(unittest.TestCase):
    """AR(1) daily differences with a known mean; the group is every 60th day. The one-sided 95% lower bound should lie below the
    known mean in about 95% of series. The current subsequence interval and the percentile domain interval are measured on the same
    series and reported, not asserted against."""

    REPS, N, SPACING, MEAN, PHI, DRAWS = 300, 1200, 60, 0.4, 0.6, 300

    def coverage(self):
        days = [date(2018, 1, 1) + timedelta(days=i) for i in range(self.N)]
        group = days[7::self.SPACING]
        positions = list(range(7, self.N, self.SPACING))
        hits = {"current": 0, "percentile": 0, "studentized": 0}
        for rep in range(self.REPS):
            d = ar1(self.N, self.PHI, self.MEAN, 5000 + rep)
            bench = {day: 10.0 for day in days}
            cand = {day: 10.0 - d[i] for i, day in enumerate(days)}
            kw = dict(block_length=sp.BLOCK_LENGTH, seed=1266, replications=self.DRAWS, level=0.90)
            hits["percentile"] += domain_estimates({"g": (d, positions)}, self.N, **kw)["g"]["interval"]["lower"] <= self.MEAN
            hits["studentized"] += studentized_domain_estimates({"g": (d, positions)}, self.N, **kw)["g"]["interval"]["lower"] <= self.MEAN
            old = s761.run_pairs({"B": bench}, cand, group, seed=1266, draws=self.DRAWS)["B"]
            hits["current"] += old["difference_interval"][0] <= self.MEAN
        return {k: v / self.REPS for k, v in hits.items()}

    def test_the_studentized_bound_covers_the_known_mean_near_its_level(self):
        rates = self.coverage()
        print("\ncoverage of the one-sided 95% lower bound on the known mean: " + ", ".join(f"{k} {v:.3f}" for k, v in rates.items()))
        self.assertGreaterEqual(rates["studentized"], 0.88)


if __name__ == "__main__":
    unittest.main()
