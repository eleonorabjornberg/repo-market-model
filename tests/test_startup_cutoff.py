"""The start-up cut-off of the pressure-day judge (#584): a measurement, not a rule in force.

`choose_cutoffs` flags nothing for a refit block whose training window holds no onset (the cut-off is infinite). A
`StartupRule` replaces that infinite cut-off, for those blocks alone, with a rule declared in advance. Without one
(the default) nothing moves.
"""

from __future__ import annotations

import math
import unittest
from datetime import timedelta

import repo_model.pressure_judge as pj
from repo_model.splits import LookAheadError

from test_pressure_judge import Series, _load


def _series(pressure=(), onsets=()):
    """60 days, refit every 20: block 0 has no training window, block 1 trains on days 0 to 18, block 2 on days 0 to 38."""

    series = Series(count=60)
    series.y5 = tuple(1 if k in pressure else 0 for k in range(60))
    series.y10 = tuple(0 for _ in range(60))
    grid = pj.Grid(
        horizon=1,
        dates=series.dates,
        outcomes={5.0: series.y5, 10.0: series.y10},
        groups=series.groups,
        onset=tuple(1 if k in onsets else 0 for k in range(60)),
        onsets={5.0: tuple(1 if k in onsets else 0 for k in range(60)), 10.0: (0,) * 60},
    )
    forecast = series.forecast("model", 1, [1.0 if k in pressure else 0.0 for k in range(60)], [0.0] * 60)
    return series, grid, forecast


def _cutoffs(series, grid, forecast, startup=None, tau=5.0):
    kwargs = {} if startup is None else {"startup": startup}
    (chosen,) = pj.choose_cutoffs(_load(), {1: grid}, [forecast], series.dates, **kwargs)
    return chosen.cutoffs[tau]


class TheDefaultMovesNothing(unittest.TestCase):
    def test_no_startup_rule_is_the_judge_as_it_is(self):
        series, grid, forecast = _series(pressure={30}, onsets={30})
        plain = _cutoffs(series, grid, forecast)
        self.assertTrue(all(math.isinf(c) for c in plain[:40]))
        self.assertEqual(plain[40:], (1.0,) * 20)


class FixedProbabilityTests(unittest.TestCase):
    rule = pj.StartupRule("fixed_probability", 0.2)

    def test_it_replaces_an_infinite_cutoff_only_while_the_window_holds_no_onset(self):
        series, grid, forecast = _series(pressure={30}, onsets={30})
        got = _cutoffs(series, grid, forecast, self.rule)
        # Blocks 0 and 1 (days 0 to 39) have no onset in their window: the fixed probability.
        self.assertEqual(got[:40], (0.2,) * 40)
        # Block 2 reads the onset of day 30: the declared rule of the judge takes over.
        self.assertEqual(got[40:], (1.0,) * 20)

    def test_it_reads_no_outcome(self):
        a = _cutoffs(*_series(pressure={30}, onsets={30}), self.rule)
        b = _cutoffs(*_series(pressure={5, 6, 50}, onsets={50}), self.rule)
        self.assertEqual(a[:40], b[:40])
        self.assertEqual(a[:40], (0.2,) * 40)

    def test_a_window_with_an_onset_and_no_cutoff_within_the_limit_is_not_a_startup_case(self):
        # One onset at day 10, reached only after 3 false alarms (probabilities above it): over the limit of 2.
        series, grid, forecast = _series(pressure={10}, onsets={10})
        probabilities = [0.0] * 60
        probabilities[10] = 0.5
        for k in (3, 4, 5):
            probabilities[k] = 0.9
        forecast = series.forecast("model", 1, probabilities, [0.0] * 60)
        got = _cutoffs(series, grid, forecast, self.rule)
        self.assertEqual(got[:20], (0.2,) * 20)
        self.assertTrue(all(math.isinf(c) for c in got[20:]))

    def test_the_other_threshold_is_treated_alike(self):
        series, grid, forecast = _series(pressure={30}, onsets={30})
        # The grid has no +10 bp pressure day, so no window ever holds an onset at that threshold.
        got = _cutoffs(series, grid, forecast, self.rule, tau=10.0)
        self.assertEqual(got, (0.2,) * 60)


class ClimatologyRateTests(unittest.TestCase):
    rule = pj.StartupRule("climatology_rate")

    def test_the_cutoff_is_the_pressure_day_rate_of_the_training_window(self):
        # Three pressure days in days 5 to 7, none of them an onset: block 1 trains on days 0 to 18.
        series, grid, forecast = _series(pressure={5, 6, 7})
        got = _cutoffs(series, grid, forecast, self.rule)
        self.assertTrue(math.isinf(got[0]), "block 0 has no training window: nothing to match")
        self.assertAlmostEqual(got[20], 3 / 19)
        self.assertAlmostEqual(got[40], 3 / 39)

    def test_a_window_with_no_pressure_day_flags_nothing(self):
        series, grid, forecast = _series()
        self.assertTrue(all(math.isinf(c) for c in _cutoffs(series, grid, forecast, self.rule)))

    def test_it_defers_to_the_judge_once_the_window_holds_an_onset(self):
        series, grid, forecast = _series(pressure={5, 30}, onsets={30})
        got = _cutoffs(series, grid, forecast, self.rule)
        self.assertAlmostEqual(got[20], 1 / 19)
        self.assertEqual(got[40:], (1.0,) * 20)


class TheRuleIsChecked(unittest.TestCase):
    def test_an_unknown_kind_is_refused(self):
        with self.assertRaises(ValueError):
            pj.StartupRule("median")

    def test_a_fixed_probability_needs_a_value_in_the_unit_interval(self):
        for bad in (None, 0.0, -0.1, 1.5, True):
            with self.assertRaises(ValueError, msg=repr(bad)):
                pj.StartupRule("fixed_probability", bad)

    def test_a_climatology_rate_takes_no_value(self):
        with self.assertRaises(ValueError):
            pj.StartupRule("climatology_rate", 0.2)


class TheWindowIsTrainingDataOnly(unittest.TestCase):
    def test_a_day_after_the_training_end_is_refused(self):
        """Guard: the climatology rate is read from days known at the refit, never from a later one.

        Recorded mutation: delete the `_require_training_only(days, training_end)` call in `startup_cutoff`; the
        test then fails with `AssertionError: LookAheadError not raised`.
        """

        series = Series(count=10)
        days = list(series.dates)
        with self.assertRaises(LookAheadError):
            pj.startup_cutoff(
                pj.StartupRule("climatology_rate"),
                days=days,
                pressure=[0] * 10,
                training_end=days[4],
            )

    def test_a_window_with_days_and_no_training_end_is_refused(self):
        series = Series(count=3)
        with self.assertRaises(LookAheadError):
            pj.startup_cutoff(
                pj.StartupRule("climatology_rate"), days=list(series.dates), pressure=[0, 0, 0], training_end=None
            )

    def test_an_empty_window_has_nothing_to_match(self):
        self.assertTrue(
            math.isinf(pj.startup_cutoff(pj.StartupRule("climatology_rate"), days=[], pressure=[], training_end=None))
        )
        self.assertEqual(
            pj.startup_cutoff(pj.StartupRule("fixed_probability", 0.2), days=[], pressure=[], training_end=None), 0.2
        )


if __name__ == "__main__":
    unittest.main()
