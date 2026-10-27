"""Persistence with partial mean reversion toward a local level (#686; H5, development tier).

The model is declared in `metadata/spread_distribution_686.json`: the quantiles of the spread h days on are
`level + phi^k * (last - level) + eps`, with `last` the spread of the last public row, `level` the median of the
last 10 ordinary days at or before it, `phi` fitted on a grid and `eps` the empirical residual quantiles, both on
the trailing two years of pairs whose target was public at the decision instant. Stdlib only.

What these tests pin: the arithmetic on synthetic pairs, the definition of the level against a hand reading of the
published panel, the as-of guard (a training row after the anchor is refused, and a change to every spread after
the anchor moves no forecast), the refit cadence, and the whole-basis-point tail reading.

Recorded mutation (the new leakage guard; run on `test_a_future_spread_moves_no_forecast` and
`test_the_training_window_stops_at_the_anchor`, then restored):

* `training_rows`: `range(max(first, k), anchor + 1)` over the target rows replaced with `range(max(first, k), anchor + 2)`, so a pair
  whose target is the row after the anchor, which was not public at the decision instant, is trained on. Both tests failed with
  `LookAheadError` ("... reads ..., after ..., the last row public at the decision instant", raised by
  `protocol_benchmarks._require_public`); restored, both pass.

Recorded mutation (a guard trip at the start of a walk, code review): `walk`'s `except LookAheadError: raise` removed, so
the `except SplitError` branch skips the day while no fit exists yet. `test_a_guard_trip_before_the_first_fit_is_raised_not_skipped`
failed with `AssertionError: LookAheadError not raised`; restored, it passes.
"""

from __future__ import annotations

import dataclasses
import math
import unittest
import unittest.mock

from repo_model import protocol_benchmarks as pb
from repo_model import scoring_protocol as sp
from repo_model import spread_mean_reversion as smr
from repo_model.splits import LookAheadError

import test_protocol_benchmarks as tpb

import legacy_day_types

# this module reproduces legacy figures: the pre-#1135 day types (see tests/legacy_day_types.py)
setUpModule, tearDownModule = legacy_day_types.setUpModule, legacy_day_types.tearDownModule


def panel_and_settings():
    panel = tpb.published_panel()["rows"]
    return panel, dict(registry=tpb.REGISTRY, decision_time=tpb.DECISION, splits=tpb.SPLITS)


def decision_index(panel, day):
    return next(i for i, row in enumerate(panel) if row.date.isoformat() == day)


def with_spread(row, spread_bps):
    values = dict(row.values)
    values["sofr"] = float(values["iorb"]) + spread_bps / 100.0
    return dataclasses.replace(row, values=values)


class FitPhiTests(unittest.TestCase):

    def test_a_noise_free_reverting_series_recovers_phi(self):
        pairs = [(k, x, 0.8**k * x) for k in (1, 2, 3, 4, 5) for x in (-6.0, -1.0, 2.0, 9.0)]
        self.assertEqual(smr.fit_phi(pairs), 0.8)

    def test_a_series_that_returns_to_the_level_at_once_has_phi_zero(self):
        pairs = [(k, x, 0.0) for k in (1, 2, 3) for x in (-4.0, 5.0)]
        self.assertEqual(smr.fit_phi(pairs), 0.0)

    def test_a_random_walk_around_the_level_has_phi_one(self):
        pairs = [(k, x, x) for k in (1, 2) for x in (-4.0, 5.0, 11.0)]
        self.assertEqual(smr.fit_phi(pairs), 1.0)

    def test_a_tie_takes_the_smaller_phi(self):
        # Every deviation is zero: every phi fits, and the smallest wins.
        self.assertEqual(smr.fit_phi([(1, 0.0, 0.0), (2, 0.0, 0.0)]), 0.0)

    def test_no_pairs_is_refused(self):
        with self.assertRaises(ValueError):
            smr.fit_phi([])


class ForecastArithmeticTests(unittest.TestCase):

    def test_the_forecast_is_the_reverted_deviation_plus_the_residual_quantiles(self):
        residual = [float(i) for i in range(len(sp.GRID))]
        fit = smr.Fit(phi=0.5, residuals={h: residual for h in sp.HORIZONS}, pairs={h: 100 for h in sp.HORIZONS},
                      fitted_on=None)
        out = smr.quantiles_from(fit, last=10.0, level=2.0, lag=1)
        for h in sp.HORIZONS:
            shift = 2.0 + 0.5 ** (h + 1) * (10.0 - 2.0)
            self.assertEqual(out[h], [shift + r for r in residual])

    def test_the_quantiles_do_not_cross(self):
        panel, settings = panel_and_settings()
        fit = smr.fit(panel, decision_index(panel, "2022-03-07"), **settings)
        for h in sp.HORIZONS:
            self.assertEqual(fit.residuals[h], sorted(fit.residuals[h]))
            self.assertEqual(len(fit.residuals[h]), len(sp.GRID))


class LevelTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = panel_and_settings()
        cls.levels = smr.ordinary_levels(cls.panel, tpb.SPLITS)

    def hand_level(self, row):
        """The median of the last ten ordinary spreads at or before `row`, read without the module."""
        ordinary = [
            self.panel[i].spread_bps
            for i in range(row + 1)
            if tpb.SPLITS.reporting_day_type(self.panel[i].date, self.panel[i].values) == "ordinary"
        ][-10:]
        ordinary.sort()
        return (ordinary[4] + ordinary[5]) / 2.0

    def test_the_level_is_the_median_of_the_last_ten_ordinary_days(self):
        for day in ("2018-09-17", "2020-02-26", "2022-03-07", "2025-10-08"):
            row = decision_index(self.panel, day)
            with self.subTest(day=day):
                self.assertAlmostEqual(self.levels[row], self.hand_level(row), places=9)

    def test_there_is_no_level_before_ten_ordinary_days(self):
        self.assertIsNone(self.levels[0])
        self.assertIsNotNone(self.levels[40])

    def test_a_non_ordinary_day_does_not_enter_the_level(self):
        month_end = next(
            i for i, row in enumerate(self.panel)
            if i > 50 and tpb.SPLITS.reporting_day_type(row.date, row.values) == "quarter_end"
        )
        shocked = list(self.panel)
        shocked[month_end] = with_spread(shocked[month_end], 400.0)
        self.assertEqual(smr.ordinary_levels(shocked, tpb.SPLITS)[month_end + 3], self.levels[month_end + 3])


class AsOfTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = panel_and_settings()

    def anchor(self, t):
        return pb._anchor(self.panel, t, self.settings["registry"], self.settings["decision_time"])

    def test_a_future_spread_moves_no_forecast(self):
        t = decision_index(self.panel, "2022-03-07")
        anchor = self.anchor(t)
        shocked = list(self.panel)
        for i in range(anchor + 1, len(shocked)):
            shocked[i] = with_spread(shocked[i], 250.0 + i)
        base = smr.forecast(self.panel, t, smr.fit(self.panel, t, **self.settings), **self.settings)
        moved = smr.forecast(shocked, t, smr.fit(shocked, t, **self.settings), **self.settings)
        self.assertEqual(base, moved)

    def test_the_anchor_spread_does_move_the_forecast(self):
        t = decision_index(self.panel, "2022-03-07")
        anchor = self.anchor(t)
        shocked = list(self.panel)
        shocked[anchor] = with_spread(shocked[anchor], self.panel[anchor].spread_bps + 30.0)
        base = smr.forecast(self.panel, t, smr.fit(self.panel, t, **self.settings), **self.settings)
        moved = smr.forecast(shocked, t, smr.fit(shocked, t, **self.settings), **self.settings)
        self.assertNotEqual(base[1], moved[1])

    def test_the_training_window_stops_at_the_anchor(self):
        t = decision_index(self.panel, "2022-03-07")
        anchor = self.anchor(t)
        rows = smr.training_rows(self.panel, t, anchor, lag=t - anchor, levels=smr.ordinary_levels(self.panel, tpb.SPLITS))
        self.assertTrue(rows)
        self.assertLessEqual(max(target for lead in rows.values() for _, target in lead), anchor)

    def test_a_forecast_needs_the_target_rows_in_the_panel(self):
        with self.assertRaises(sp.ProtocolError):
            smr.fit(self.panel[:-1], len(self.panel) - 2, **self.settings)

    def test_a_forecast_with_too_little_history_is_refused(self):
        with self.assertRaises(smr.InsufficientHistory):
            smr.fit(self.panel, 20, **self.settings)


class WalkTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = panel_and_settings()
        days = [row.date for row in cls.panel if row.date.isoformat() >= "2021-01-04"][:50]
        cls.days = days
        cls.walk = smr.walk(cls.panel, days, **cls.settings)

    def test_the_fit_is_renewed_on_the_first_day_and_every_21st(self):
        fitted = sorted(self.walk.fits)
        self.assertEqual(fitted, [self.days[0], self.days[21], self.days[42]])

    def test_between_refits_the_fit_is_kept_and_the_inputs_are_read_afresh(self):
        a, b = self.days[3], self.days[4]
        self.assertEqual(self.walk.fit_used[a], self.walk.fit_used[b])
        self.assertNotEqual(self.walk.forecasts[a][1], self.walk.forecasts[b][1])

    def test_every_day_has_five_leads_of_the_grid(self):
        for forecast in self.walk.forecasts.values():
            self.assertEqual(set(forecast), set(sp.HORIZONS))
            for quantiles in forecast.values():
                self.assertEqual(len(quantiles), len(sp.GRID))

    def test_early_days_without_history_are_listed_not_forecast(self):
        early = smr.walk(self.panel, [row.date for row in self.panel[:30]], **self.settings)
        self.assertEqual(early.forecasts, {})
        self.assertEqual(len(early.skipped), 30)

    def test_a_guard_trip_before_the_first_fit_is_raised_not_skipped(self):
        def tripped(*args, **kwargs):
            raise LookAheadError("a read after the decision instant")

        with unittest.mock.patch.object(smr, "fit", tripped):
            with self.assertRaises(LookAheadError):
                smr.walk(self.panel, self.days[:3], **self.settings)


class ExceedanceTests(unittest.TestCase):
    """P(spread > tau) as `ml.exceedance_from_quantiles` reads it: `1 - F(floor(tau) + 0.5)`, F linear, with the
    outer segments continued to 0 and 1. Hand values for a law that is uniform on the grid."""

    LAW = [float(i) for i in range(len(sp.GRID))]

    def test_it_is_linear_between_two_quantiles(self):
        # knots 4.0 (level 0.35) and 5.0 (level 0.4 ... check by the grid): F(5.5) lies between levels of 5.0, 6.0
        grid = sp.GRID
        low, high = 5, 6
        expected = 1.0 - (grid[low] + 0.5 * (grid[high] - grid[low]))
        self.assertAlmostEqual(smr.exceedance(self.LAW, 5.0), expected, places=5)

    def test_it_reaches_one_below_and_zero_above_the_law(self):
        self.assertAlmostEqual(smr.exceedance([v - 100 for v in self.LAW], 5.0), 0.0, places=6)
        self.assertAlmostEqual(smr.exceedance([v + 100 for v in self.LAW], 5.0), 1.0, places=6)

    def test_it_is_non_increasing_in_tau(self):
        curve = [smr.exceedance(self.LAW, tau) for tau in range(-5, 30)]
        self.assertEqual(curve, sorted(curve, reverse=True))

    def test_the_event_is_strict_on_whole_basis_points(self):
        # tau = 5 is read at 5.5: a spread of 5 bp is not above it
        self.assertEqual(smr.exceedance(self.LAW, 5.0), smr.exceedance(self.LAW, 5.4))
        self.assertGreater(smr.exceedance(self.LAW, 4.0), smr.exceedance(self.LAW, 5.0))

    def test_ties_are_nudged_not_divided_by(self):
        value = smr.exceedance([1.0] * len(sp.GRID), 5.0)
        self.assertTrue(math.isfinite(value))
        self.assertEqual(value, 0.0)


if __name__ == "__main__":
    unittest.main()
