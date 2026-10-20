"""H1 step 3 and H6 step 1 (#963): the contiguous-window calibration, the fixed-b statistic and the event strata.

The new pieces are checked on series with known answers before they touch H5's data. The contiguous generator
returns one statistic per start day in [0, n - days] and none that wraps; a window's statistic is the one
`scoring_protocol.window_t_statistics` would compute for those days; on a persistent AR(1) series its 95th percentile
is above the circular-10 generator's (the point of #963); the fixed-b statistic is the mean over the Bartlett
standard error of bandwidth b * T, and on independent noise its critical value is near the t distribution's. The
script changes no decided value.

No guard is added beyond `ValueError` on input that cannot carry a window, so there is no recorded mutation.
"""

import importlib.util
import json
import math
import random
import unittest
from pathlib import Path

from repo_model import scoring_protocol as sp

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


script = load("contiguous_calibration_963")

IN_FORCE_BEFORE = {k: dict(v) for k, v in sp.CRITICAL_VALUES.items()}


def ar1(n, phi, seed):
    rng = random.Random(seed)
    x, out = 0.0, []
    for _ in range(n + 200):
        x = phi * x + rng.gauss(0.0, 1.0)
        out.append(x)
    return out[200:]


class TestContiguousWindows(unittest.TestCase):
    def test_one_statistic_per_start_without_wrap(self):
        series = ar1(400, 0.5, 1)
        stats = script.contiguous_window_statistics(series, days=250)
        self.assertEqual(len(stats), 400 - 250 + 1)
        self.assertEqual(stats, sorted(stats))

    def test_a_window_is_the_protocols_statistic_for_those_days(self):
        series = ar1(300, 0.4, 2)
        days = 125
        truth = sum(series) / len(series)
        window = series[17:17 + days]
        expected = (sum(window) / days - truth) / sp._standard_error(window, sp.HAC_LAG, "a window")
        got = script.contiguous_window_statistics(series, days=days)
        self.assertIn(min(got, key=lambda v: abs(v - expected)), got)
        self.assertAlmostEqual(min(abs(v - expected) for v in got), 0.0, places=12)

    def test_a_full_length_window_is_zero(self):
        series = ar1(250, 0.3, 3)
        self.assertAlmostEqual(script.contiguous_window_statistics(series, days=250)[0], 0.0, places=12)

    def test_persistence_makes_the_contiguous_value_larger_than_the_circular_ten(self):
        series = ar1(1600, 0.8, 4)
        contiguous = sp._bound(script.contiguous_window_statistics(series, days=250), 0.95, 1000)
        circular = sp.calibrate_critical_value(series, days=250, level=0.05, windows=4000, seed=1)
        self.assertGreater(contiguous, circular)

    def test_windows_that_cannot_carry_the_lag_or_the_series_are_refused(self):
        with self.assertRaises(ValueError):
            script.contiguous_window_statistics([0.0] * 100, days=300)
        with self.assertRaises(ValueError):
            script.contiguous_window_statistics(ar1(100, 0.1, 1), days=sp.HAC_LAG)

    def test_effective_windows_are_the_non_overlapping_count(self):
        self.assertAlmostEqual(script.effective_windows(1500, 250), 6.0)


class TestFixedB(unittest.TestCase):
    def test_it_is_the_mean_over_the_bartlett_standard_error_of_bandwidth_b_t(self):
        series = ar1(500, 0.3, 5)
        m = 50
        mean = sum(series) / 500
        se = math.sqrt(sp._long_run_variance(series, m - 1) / 500)
        self.assertAlmostEqual(script.fixed_b_statistic(series, b=0.1), mean / se, places=12)

    def test_the_centred_statistic_removes_the_mean(self):
        series = ar1(500, 0.3, 6)
        self.assertAlmostEqual(script.fixed_b_statistic(series, b=0.1, centre=sum(series) / 500), 0.0, places=12)

    def test_the_critical_value_on_noise_is_near_the_student_value_and_above_the_normal(self):
        value = script.fixed_b_critical_value(days=200, b=0.1, draws=3000, seed=1)
        self.assertGreater(value, 1.645)
        self.assertLess(value, 2.2)

    def test_a_bandwidth_below_two_is_refused(self):
        with self.assertRaises(ValueError):
            script.fixed_b_statistic(ar1(100, 0.1, 1), b=0.005)


class TestStrata(unittest.TestCase):
    def test_events_per_year(self):
        from datetime import date
        events = [date(2021, 1, 29), date(2022, 1, 31), date(2023, 1, 31)]
        self.assertAlmostEqual(script.events_per_year(events), 3 / ((date(2023, 1, 31) - date(2021, 1, 29)).days / 365.25))

    def test_the_declaration_is_the_one_the_script_runs(self):
        declaration = json.loads((ROOT / "metadata" / "contiguous_calibration_963.json").read_text(encoding="utf-8"))
        self.assertEqual(declaration["calibration"]["window_days"], list(script.WINDOW_DAYS))
        self.assertEqual(declaration["fixed_b"]["statistic"].count("b = 0.1"), 1)
        self.assertEqual(script.FIXED_B, 0.1)
        self.assertEqual(declaration["event_strata"]["minimum_events"], script.MINIMUM_EVENTS)


class TestNothingDecidedMoves(unittest.TestCase):
    def test_the_critical_values_in_force_are_unchanged(self):
        self.assertEqual(sp.CRITICAL_VALUES, IN_FORCE_BEFORE)
        self.assertEqual(script.IN_FORCE[125], 3.419438620805254)
        self.assertEqual(script.IN_FORCE[250], 2.425730476113518)
        self.assertEqual(sp.CRITICAL_VALUES[sp.GRID_COMPARISON][250], script.IN_FORCE[250])


if __name__ == "__main__":
    unittest.main()
