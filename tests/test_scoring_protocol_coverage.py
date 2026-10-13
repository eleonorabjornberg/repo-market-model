"""H1, check 2: the protocol's interval, checked for coverage on resampled real series (#655).

The directive asks that interval coverage be checked by simulation on resampled real series,
and be at its nominal rate within simulation error. **It is not.** This module measures it
and records what it found; the pull request that closes #655 puts the result to Eleonora.

**The real series.** `d_t = S(B2) - S(B1)`, the daily grid-CRPS difference of the two
benchmarks of `protocol_benchmarks`, on every development decision day whose five targets fall
on or before 2026-09-03, on the published panel. Its mean over all those days is the truth.

**The simulation.** Each replication draws a series of `DAYS` days from the real one by
circular blocks of `GENERATOR_BLOCK` consecutive days at uniform random starts (a different
resampler from the scorer's stationary bootstrap, so the check is not the bootstrap checking
itself), runs the scorer's paired test on it, and records whether the one-sided 95% lower
bound of mean(d) is at or below the truth. Coverage is the share of replications in which it
is. `DAYS` is the last checkpoint, where the nominal level is close to 5%; the test reads the
bound at 5%. The bootstrap uses `DRAWS` draws, not the protocol's 10,000, to keep the suite's
run time in bounds: the coverage of a percentile bound moves little with the draw count once it
is in the thousands (the pull request reports a run at 10,000).

**The control.** The same simulation on iid standard normal days, where the only error is the
bootstrap's own.

**What it found** (on the seeds below; the pull request reports longer runs):
- the control covers at about its nominal rate, a little under it, as a percentile block
  bootstrap does on 250 days;
- the real series covers far below it. The real `d` has a heavy left tail (one day in
  September 2019 alone is about forty standard deviations from the mean); a 250-day draw that
  misses such days has a mean above the truth and a tight interval around it.
"""

from __future__ import annotations

import math
import random
import unittest
from datetime import date, time, timedelta

from repo_model import protocol_benchmarks as pb
from repo_model import scoring_protocol as sp

from test_protocol_benchmarks import DEVELOPMENT_FIRST, DEVELOPMENT_LAST, REGISTRY, SPLITS, published_panel

DAYS = 250
REPLICATIONS = 300
DRAWS = 1000
GENERATOR_BLOCK = 10
LEVEL = 0.05
#: Three binomial standard errors at the nominal rate.
TOLERANCE = 3.0 * math.sqrt(0.95 * 0.05 / REPLICATIONS)


def real_differences():
    rows = published_panel()["rows"]
    days = [row.date for row in rows]
    decisions = [
        day for i, day in enumerate(days)
        if DEVELOPMENT_FIRST <= day and i + 5 < len(days) and days[i + 5] <= DEVELOPMENT_LAST
    ]
    settings = {"registry": REGISTRY, "decision_time": time(16, 0)}
    b1 = pb.forecasts(pb.b1_forecast, rows, decisions, **settings)
    b2 = pb.forecasts(pb.b2_forecast, rows, decisions, splits=SPLITS, **settings)
    outcomes = {row.date: row.spread_bps for row in rows}
    s1 = sp.day_scores(b1, outcomes, days)
    s2 = sp.day_scores(b2, outcomes, days)
    return [s2[day] - s1[day] for day in sorted(s1)]


def coverage(series, seed):
    truth = sum(series) / len(series)
    rng = random.Random(seed)
    days = [date(2001, 1, 1) + timedelta(days=k) for k in range(DAYS)]
    benchmark = {day: 10.0 for day in days}
    covered = 0
    for replication in range(REPLICATIONS):
        draw = []
        while len(draw) < DAYS:
            start = rng.randrange(len(series))
            draw.extend(series[(start + k) % len(series)] for k in range(GENERATOR_BLOCK))
        candidate = {day: 10.0 - value for day, value in zip(days, draw)}
        test = sp.paired_test(benchmark, candidate, seed=replication, draws=DRAWS)
        covered += test.lower_mean_difference(LEVEL) <= truth
    return covered / REPLICATIONS


class CoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.real = real_differences()
        noise = random.Random(5)
        cls.control = [noise.gauss(0.0, 1.0) for _ in cls.real]
        cls.real_coverage = coverage(cls.real, seed=42)
        cls.control_coverage = coverage(cls.control, seed=42)

    def test_the_control_covers_at_its_nominal_rate(self):
        self.assertAlmostEqual(self.control_coverage, 1.0 - LEVEL, delta=TOLERANCE)

    def test_h1_check_2_fails_the_real_series_is_undercovered(self):
        """The recorded failure: coverage on the real series is below nominal beyond error.

        If a change to the scorer's interval moves this, the change is a protocol change
        (§13), and this test and the pull request's table move with it.
        """

        self.assertLess(self.real_coverage, 1.0 - LEVEL - TOLERANCE)
        self.assertEqual(round(self.real_coverage, 4), RECORDED_REAL_COVERAGE)

    def test_the_real_series_is_heavy_tailed(self):
        mean = sum(self.real) / len(self.real)
        sd = math.sqrt(sum((x - mean) ** 2 for x in self.real) / len(self.real))
        self.assertGreater((mean - min(self.real)) / sd, 30.0)


#: The coverage measured on the seeds above, 12 October 2026.
RECORDED_REAL_COVERAGE = 0.81


if __name__ == "__main__":
    unittest.main()
