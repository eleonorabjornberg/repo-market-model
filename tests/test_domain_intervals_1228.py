"""The domain estimate of a non-contiguous day-type group (#1228; H5 step 3 reporting, H1 scorer).

Written first, and watched fail (`ImportError: cannot import name 'domain_estimates'`). The finding (#1221): the H5 pages' day-type
intervals pass the group's own days to `scoring_protocol.paired_tests`, which sorts them into one short series and draws blocks of
mean length 10 over its positions, so a block can join days that are months apart. `evaluation_splits` says to resample the whole
aligned series and take the mean over the resampled days that belong to the group. These tests pin that path:

* the point estimate is the group mean, and the interval is the percentile interval of the group mean over whole-series resamples,
  the same draws as `split_summary` and as the pooled test (same block, seed and draw count);
* a resample that draws no day of the group raises (`MetricError` from `domain_interval`) and the split records "unavailable"
  with the reason, for that group only;
* on a synthetic AR(1) series with group days 60 apart, the coverage of the domain one-sided bound against the known mean is
  measured beside the current subsequence interval's coverage (`spread_mr_variants_761.run_pairs`).

Mutation (recorded, guard: a resample with no day of the group must not be dropped): in `domain_intervals.domain_estimates`,
replacing the `if drawn == 0:` branch that records the group as unavailable by `continue` (drop the resample) made
`test_a_resample_without_a_group_day_raises_and_the_split_is_unavailable` fail with `AssertionError: MetricError not raised`.
"""

from __future__ import annotations

import importlib.util
import random
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import scoring_protocol as sp
from repo_model.domain_intervals import domain_estimates, domain_interval
from repo_model.evaluation_splits import split_summary
from repo_model.metrics import MetricError

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("spread_mr_variants_761", ROOT / "scripts" / "spread_mr_variants_761.py")
s761 = importlib.util.module_from_spec(_spec)
sys.modules["spread_mr_variants_761"] = s761
_spec.loader.exec_module(s761)

SETTINGS = dict(block_length=10, seed=1228, replications=400, level=0.90)


def ar1(n, phi, mean, seed):
    rng = random.Random(seed)
    x, out = 0.0, []
    for _ in range(n):
        x = phi * x + rng.gauss(0.0, 1.0)
        out.append(mean + x)
    return out


class DomainPointAndInterval(unittest.TestCase):

    def test_the_point_estimate_is_the_group_mean_and_the_interval_brackets_it(self):
        values = ar1(600, 0.5, 0.3, 1)
        members = tuple(range(5, 600, 60))
        entry = domain_estimates({"g": (values, members)}, 600, **SETTINGS)["g"]
        self.assertEqual(entry["count"], len(members))
        self.assertAlmostEqual(entry["mean"], sum(values[i] for i in members) / len(members), places=12)
        self.assertLess(entry["interval"]["lower"], entry["mean"])
        self.assertGreater(entry["interval"]["upper"], entry["mean"])

    def test_it_is_the_interval_split_summary_gives_on_the_same_draws(self):
        values = ar1(500, 0.4, 0.0, 2)
        members = tuple(range(3, 500, 25))
        labels = ["g" if i in set(members) else "rest" for i in range(500)]
        old = split_summary(labels, values, ("g", "rest"), **SETTINGS)["g"]
        new = domain_estimates({"g": (values, members)}, 500, **SETTINGS)["g"]
        self.assertAlmostEqual(new["interval"]["lower"], old["interval"]["lower"], places=9)
        self.assertAlmostEqual(new["interval"]["upper"], old["interval"]["upper"], places=9)
        self.assertEqual(domain_interval(values, members, 500, **SETTINGS), (new["interval"]["lower"], new["interval"]["upper"]))

    def test_groups_may_overlap_and_share_one_stream(self):
        values = ar1(400, 0.3, 0.0, 3)
        a, b = tuple(range(0, 400, 20)), tuple(range(0, 400, 40))
        both = domain_estimates({"a": (values, a), "b": (values, b)}, 400, **SETTINGS)
        alone = domain_estimates({"b": (values, b)}, 400, **SETTINGS)
        self.assertEqual(both["b"], alone["b"])

    def test_a_resample_without_a_group_day_raises_and_the_split_is_unavailable(self):
        values = ar1(300, 0.3, 0.0, 4)
        lonely = (150,)
        with self.assertRaises(MetricError):
            domain_interval(values, lonely, 300, **{**SETTINGS, "block_length": 1, "replications": 2000})
        out = domain_estimates({"lonely": (values, lonely), "wide": (values, tuple(range(0, 300, 10)))}, 300,
                               **{**SETTINGS, "block_length": 1, "replications": 2000})
        self.assertIn("interval_unavailable", out["lonely"])
        self.assertNotIn("interval", out["lonely"])
        self.assertIn("no day of the group", out["lonely"]["interval_unavailable"])
        self.assertEqual(out["lonely"]["mean"], values[150])
        self.assertIn("interval", out["wide"])  # the other group is unaffected
        self.assertEqual(domain_estimates({"none": (values, ())}, 300, **SETTINGS)["none"], {"count": 0})

    def test_bad_input_is_refused(self):
        with self.assertRaises(ValueError):
            domain_estimates({"g": ([1.0, 2.0], (5,))}, 2, **SETTINGS)
        with self.assertRaises(ValueError):
            domain_estimates({"g": ([1.0, 2.0, 3.0], (0,))}, 2, **SETTINGS)


class PairsPath(unittest.TestCase):

    def setUp(self):
        self.days = [date(2020, 1, 1) + timedelta(days=i) for i in range(400)]
        d = ar1(400, 0.4, 0.2, 5)
        self.bench = {day: 5.0 + 0.5 * i % 3 for i, day in enumerate(self.days)}
        self.cand = {day: self.bench[day] - d[i] for i, day in enumerate(self.days)}
        self.group = self.days[10::40]

    def test_the_row_carries_the_group_mean_of_d_and_the_domain_bound(self):
        row = s761.run_domain({"B1": self.bench}, self.cand, self.group, self.days, seed=1228, draws=300)["B1"]
        mean = sum(self.bench[d] - self.cand[d] for d in self.group) / len(self.group)
        self.assertAlmostEqual(row["difference"], mean, places=12)
        self.assertEqual(row["days"], len(self.group))
        lo, hi = row["difference_interval"]
        self.assertLess(lo, row["difference"])
        self.assertGreater(hi, row["difference"])
        self.assertEqual(row["method"], "domain")

    def test_a_group_day_outside_the_series_is_refused(self):
        with self.assertRaises(ValueError):
            s761.run_domain({"B1": self.bench}, self.cand, [date(1999, 1, 1)], self.days, seed=1, draws=50)

    def test_an_unavailable_group_is_recorded_not_dropped(self):
        row = s761.run_domain({"B1": self.bench}, self.cand, [self.days[200]], self.days, seed=1228, draws=2000, block_length=1)["B1"]
        self.assertIn("undefined", row)
        self.assertIn("no day of the group", row["undefined"])


class CoverageBesideTheCurrentInterval(unittest.TestCase):
    """AR(1) daily differences with a known mean; the group is every 60th day, so its days are far apart. The one-sided 95% lower
    bound should lie below the known mean in about 95% of series. The current subsequence interval is measured on the same series
    and reported, not asserted against: its direction is not known in advance."""

    REPS, N, SPACING, MEAN, PHI, DRAWS = 400, 1200, 60, 0.4, 0.6, 400

    def coverage(self):
        days = [date(2018, 1, 1) + timedelta(days=i) for i in range(self.N)]
        group = days[7::self.SPACING]
        domain = current = 0
        for rep in range(self.REPS):
            d = ar1(self.N, self.PHI, self.MEAN, 1000 + rep)
            bench = {day: 10.0 for day in days}
            cand = {day: 10.0 - d[i] for i, day in enumerate(days)}
            row = s761.run_domain({"B": bench}, cand, group, days, seed=1228, draws=self.DRAWS)["B"]
            domain += row["difference_interval"][0] <= self.MEAN
            old = s761.run_pairs({"B": bench}, cand, group, seed=1228, draws=self.DRAWS)["B"]
            current += old["difference_interval"][0] <= self.MEAN
        return domain / self.REPS, current / self.REPS

    def test_the_domain_bound_covers_the_known_mean_near_its_level(self):
        domain, current = self.coverage()
        print(f"\ncoverage of the one-sided 95% lower bound on the known mean: domain {domain:.3f}, current subsequence {current:.3f}")
        self.assertGreaterEqual(domain, 0.88)


if __name__ == "__main__":
    unittest.main()
