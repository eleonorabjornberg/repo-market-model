"""H1, check 2: the protocol's interval, checked for coverage on resampled real series (#655).

The directive asks that interval coverage be checked by simulation on resampled real series,
and be at its nominal rate within simulation error. **It is not**, under either interval: the
plain percentile bootstrap first implemented (PR #660, about 80%), or the studentized stationary
bootstrap Eleonora ruled for on 13 October 2026 (PR #660, comment 6145669436), which this module
now checks. Her ruling holds registration until #656's power study confirms coverage.

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
run time in bounds: the coverage of a bound moves little with the draw count once it is in the
thousands (the pull request reports a run at 10,000).

**The control.** The same simulation on iid standard normal days, where the only error is the
bootstrap's own.

**What it found** (on the seeds below; the pull request reports longer runs):
- the control covers at about its nominal rate, a little under it, as a block bootstrap does
  on 250 days;
- the real series covers well below it, better than the percentile bootstrap did and still
  short. The real `d` has a heavy left tail (one day in September 2019 alone is about forty
  standard deviations from the mean); a 250-day draw that misses such days has a mean above the
  truth, and studentizing by that draw's own standard error does not bring the tail back.
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
        test = sp.paired_test(benchmark, candidate, seed=replication, draws=DRAWS, with_skill=False)
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


class CalibrationTests(unittest.TestCase):
    """The double-bootstrap calibration (ruling of 13 October 2026, PR #695) on one real window.

    It does not repair coverage on the real series, and the pull request reports why: a
    250-day window that misses the series' tail days is resampled into a world that lacks them
    too, so the calibration learns from a lighter tail than the truth has. On the small runs the
    pull request reports, the calibrated bound covers no more often than the studentized one,
    and on about a fifth of windows (100 inner draws) the calibrated level hits the prepivots'
    ceiling and is refused. This test records the calibration on one window at small counts, so
    a change to the calibration is seen; the counts are far below the protocol's.
    """

    def test_one_window_is_recorded(self):
        real = real_differences()
        rng = random.Random(42)
        window = []
        while len(window) < DAYS:
            start = rng.randrange(len(real))
            window.extend(real[(start + k) % len(real)] for k in range(GENERATOR_BLOCK))
        window = window[:DAYS]
        days = [date(2001, 1, 1) + timedelta(days=k) for k in range(DAYS)]
        test = sp.paired_test(
            {day: 10.0 for day in days},
            {day: 10.0 - value for day, value in zip(days, window)},
            seed=42, draws=200, inner_draws=100, with_skill=False,
        )
        self.assertAlmostEqual(test.calibrated_level(0.05), 0.07, places=9)


class EmpiricalCalibrationCoverageTests(unittest.TestCase):
    """H1 check 2 under the empirically calibrated critical value (ruling of 13 October 2026, PR #695,
    comment 6149326627).

    The critical value is calibrated on one set of resampled 250-day windows and its coverage is
    measured on a fresh set (another seed), so the check is out of sample. The bound covers when the
    window's studentized mean is at or below the critical value. Check 2 passes when coverage is at
    least 0.95 on the real series and the iid control still passes.
    """

    WINDOWS = 20_000
    #: Three binomial standard errors at the nominal rate, for these windows.
    WINDOW_TOLERANCE = 3.0 * math.sqrt(0.95 * 0.05 / 20_000)

    @classmethod
    def setUpClass(cls):
        cls.real = real_differences()
        noise = random.Random(5)
        cls.control = [noise.gauss(0.0, 1.0) for _ in cls.real]

    def coverage(self, series, critical_value):
        t = sp.window_t_statistics(series, days=DAYS, windows=self.WINDOWS, seed=2)
        return sum(1 for value in t if value <= critical_value) / len(t)

    def test_the_real_series_own_calibration_covers_out_of_sample(self):
        c = sp.calibrate_critical_value(self.real, days=DAYS, level=LEVEL, windows=self.WINDOWS, seed=1)
        self.assertAlmostEqual(self.coverage(self.real, c), 1.0 - LEVEL, delta=self.WINDOW_TOLERANCE)

    def test_check_2_passes_at_the_protocols_value(self):
        c = sp.CRITICAL_VALUES[DAYS]
        self.assertGreaterEqual(self.coverage(self.real, c), 1.0 - LEVEL)
        self.assertGreaterEqual(self.coverage(self.control, c), 1.0 - LEVEL)

    def test_the_control_calibrates_to_its_nominal_rate(self):
        c = sp.calibrate_critical_value(self.control, days=DAYS, level=LEVEL, windows=self.WINDOWS, seed=1)
        self.assertAlmostEqual(self.coverage(self.control, c), 1.0 - LEVEL, delta=self.WINDOW_TOLERANCE)
        self.assertAlmostEqual(c, sp._NORMAL.inv_cdf(1.0 - LEVEL), delta=0.1)


#: The coverage measured on the seeds above under the studentized bootstrap, 13 October 2026
#: (0.81 under the percentile bootstrap it replaced).
RECORDED_REAL_COVERAGE = 0.8533


if __name__ == "__main__":
    unittest.main()
