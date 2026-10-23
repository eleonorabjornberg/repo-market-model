"""Scaling the H5 candidate by SOFR's in-panel dispersion (#1175; H5 step 3, avenue #1166 option 1).

`metadata/sofr_dispersion_1175.json` is the declaration; `repo_model.spread_mr_dispersion` is its arithmetic. What these tests
pin: the dispersion ratio (today's width over its trailing median) on hand cases, with the neutral value where the window is
short or a percentile is missing; the factor and its cap; the fitted slope on planted data (recovered, zero where the dispersion
carries nothing, zero with too few pairs); that a ratio of one everywhere leaves (s3) of #1145 unchanged; that arm (d3) moves
only the upper half of the law; that the percentile columns are read as of the decision instant (the rows of a window never pass
the anchor, and a field published later than the anchor's spread is refused); and that a future percentile or spread moves no
forecast.

Recorded mutations (each applied to the tree, the named test run, and reverted):

* `rows_read`: `range(max(0, row - WINDOW + 1), row + 1)` replaced with `range(max(0, row - WINDOW + 1), row + 2)`, so the window
  reads the row after the one asked for. `test_the_window_of_a_row_never_passes_the_row` failed with `AssertionError`
  (`True is not false`), and the walk's own guard tripped: `WalkTests.setUpClass` raised `LookAheadError` ("reads 2024-06-03, after
  2024-05-31").
* `require_available`: `if read.row < anchor:` replaced with `if read.row < anchor - 1:`, so a percentile published one row after
  the anchor's spread is admitted. `test_a_percentile_published_after_the_anchors_spread_is_refused` failed with
  `AssertionError` (`LookAheadError` not raised).
"""

from __future__ import annotations

import copy
import dataclasses
import unittest
from datetime import date

from repo_model import spread_mr_dispersion as dsp
from repo_model import spread_mr_calendar as cal
from repo_model import spread_mr_state_calendar as sc
from repo_model.splits import LookAheadError

import test_protocol_benchmarks as tpb
import test_spread_mr_state_calendar as tsc

PANEL = tpb.published_panel()["rows"]
SETTINGS = dict(registry=tpb.REGISTRY, decision_time=tpb.DECISION, splits=tpb.SPLITS)
NONE = {name: 0 for name in cal.ALL_TERMS}
TABLE_ALL = tsc.TABLE_ALL


def index_of(day: str) -> int:
    return next(i for i, row in enumerate(PANEL) if row.date.isoformat() == day)


class RatioTests(unittest.TestCase):

    def test_the_ratio_is_the_width_over_the_median_of_the_window(self):
        series = [4.0] * 30 + [8.0]
        self.assertEqual(dsp.ratio_at(series, 30), 2.0)
        self.assertEqual(dsp.ratio_at(series, 29), 1.0)

    def test_a_short_window_or_a_missing_value_reads_as_neutral(self):
        self.assertEqual(dsp.ratio_at([4.0] * (dsp.MIN_ROWS - 2) + [40.0], dsp.MIN_ROWS - 2), 1.0)
        series = [4.0] * 30 + [None]
        self.assertEqual(dsp.ratio_at(series, 30), 1.0)

    def test_a_missing_value_inside_the_window_is_left_out_of_the_median(self):
        series = [4.0] * 15 + [None] * 5 + [4.0] * 10 + [12.0]
        self.assertEqual(dsp.ratio_at(series, 30), 3.0)

    def test_the_median_has_a_floor_and_the_ratio_a_cap(self):
        series = [0.0] * 30 + [3.0]
        self.assertEqual(dsp.ratio_at(series, 30), dsp.X_CAP)
        self.assertEqual(dsp.ratio_at([0.0] * 31, 30), 0.0)
        self.assertEqual(dsp.ratio_at([1.0] * 30 + [1.0], 30), 1.0 / 1.0)
        self.assertEqual(dsp.ratio_at([0.1] * 30 + [0.4], 30), 0.4 / dsp.MEDIAN_FLOOR_BP)

    def test_the_window_of_a_row_never_passes_the_row(self):
        for row in (0, 5, 70, 500):
            self.assertFalse(any(j > row for j in dsp.rows_read(row)), row)
        self.assertEqual(max(dsp.rows_read(70)), 70)

    def test_the_numerators_are_the_width_and_the_upper_half_in_bp(self):
        values = {"sofr": 4.30, "sofr_p25": 4.28, "sofr_p75": 4.35}
        row = PANEL[0].__class__(PANEL[0].date, values)
        self.assertAlmostEqual(dsp.numerator_bp(row, "iqr"), 7.0)
        self.assertAlmostEqual(dsp.numerator_bp(row, "upper"), 5.0)
        gone = PANEL[0].__class__(PANEL[0].date, dict(values, sofr_p75=None))
        self.assertIsNone(dsp.numerator_bp(gone, "iqr"))
        self.assertIsNone(dsp.numerator_bp(gone, "upper"))


class FactorTests(unittest.TestCase):

    def test_the_factor_is_one_at_a_ratio_of_one_and_is_capped_both_ways(self):
        self.assertEqual(dsp.factor(1.0, 0.7), 1.0)
        self.assertEqual(dsp.factor(3.0, 0.5), 2.0)
        self.assertEqual(dsp.factor(4.0, 2.0), dsp.F_MAX)
        self.assertEqual(dsp.factor(0.0, 2.0), dsp.F_MIN)
        self.assertEqual(dsp.factor(2.5, 0.0), 1.0)


def planted(gamma, n=200, amplitude=1.0):
    xs, es = [], []
    for i in range(n):
        x = 0.5 + (i % 10) / 5.0
        sign = 1.0 if i % 2 else -1.0
        xs.append(x)
        es.append(sign * amplitude * (1.0 + gamma * (x - 1.0)))
    return xs, es


class SlopeTests(unittest.TestCase):

    def test_a_planted_slope_is_recovered(self):
        xs, es = planted(0.6)
        self.assertAlmostEqual(dsp.fit_gamma(xs, es, upper_only=False), 0.6, places=6)

    def test_a_flat_or_falling_relation_gives_zero(self):
        xs, es = planted(0.0)
        self.assertEqual(dsp.fit_gamma(xs, es, upper_only=False), 0.0)
        xs, es = planted(-0.3)
        self.assertEqual(dsp.fit_gamma(xs, es, upper_only=False), 0.0)

    def test_the_slope_is_capped(self):
        xs, es = planted(5.0)
        self.assertEqual(dsp.fit_gamma(xs, es, upper_only=False), dsp.GAMMA_MAX)

    def test_too_few_pairs_or_no_spread_in_the_ratio_gives_zero(self):
        xs, es = planted(0.6, n=dsp.MIN_PAIRS - 1)
        self.assertEqual(dsp.fit_gamma(xs, es, upper_only=False), 0.0)
        self.assertEqual(dsp.fit_gamma([1.0] * 100, planted(0.6, n=100)[1], upper_only=False), 0.0)

    def test_the_upper_arm_reads_only_the_positive_residuals(self):
        xs = [0.5 + (i % 10) / 5.0 for i in range(300)]
        es = [(1.0 + 0.5 * (x - 1.0)) if i % 2 else -3.0 for i, x in enumerate(xs)]
        self.assertAlmostEqual(dsp.fit_gamma(xs, es, upper_only=True), 0.5, places=6)
        self.assertEqual(dsp.fit_gamma(xs, es, upper_only=False), 0.0)


def pairs_of(n=120):
    out = []
    for i in range(n):
        flags = dict(NONE, quarter_end=1 if i < 12 else 0)
        z = (-1.0) ** i * (0.4 + (i % 3) * 0.2) + (2.0 if flags["quarter_end"] else 0.0)
        out.append(sc.StatePair(z * (1.0 + (i % 4)), 1.0 + (i % 4), flags, None))
    return out


ARM_S3 = sc.ARMS[2]


def s3_estimate(pairs):
    return sc.fit_state_terms(pairs, regressors=("quarter_end",), terms=ARM_S3.location, interact=False, robust=True,
                              training_pairs="direct")


class LeadFitTests(unittest.TestCase):

    def fit(self, pairs, xs, arm):
        return dsp.fit_lead(pairs, xs, arm, regressors=("quarter_end",))

    def test_a_ratio_of_one_everywhere_is_arm_s3(self):
        pairs = pairs_of()
        s3 = s3_estimate(pairs)
        for arm in dsp.ARMS:
            got = self.fit(pairs, [1.0] * len(pairs), arm)
            self.assertEqual(got.gamma, 0.0)
            self.assertEqual(got.estimate.effect, s3.effect, arm.name)
            self.assertEqual(got.estimate.pool, s3.pool, arm.name)

    def test_a_planted_dispersion_effect_widens_the_pool_less_than_it_widens_the_scale(self):
        pairs = pairs_of(200)
        xs = [0.5 + (i % 10) / 5.0 for i in range(200)]
        wide = [sc.StatePair(p.raw * (1.0 + 0.8 * (x - 1.0)), p.scale, p.flags, None) for p, x in zip(pairs, xs)]
        got = self.fit(wide, xs, dsp.ARMS[0])
        plain = s3_estimate(wide)
        self.assertGreater(got.gamma, 0.3)
        self.assertLess(got.estimate.pool[-1] - got.estimate.pool[0], plain.pool[-1] - plain.pool[0])

    def test_the_upper_arm_keeps_the_lower_half_of_the_pool_and_shrinks_the_upper_half(self):
        pairs = pairs_of(200)
        xs = [0.5 + (i % 10) / 5.0 for i in range(200)]
        wide = [sc.StatePair(p.raw * (1.0 + 0.8 * (x - 1.0)), p.scale, p.flags, None) for p, x in zip(pairs, xs)]
        got = self.fit(wide, xs, dsp.ARMS[2])
        plain = s3_estimate(wide)
        self.assertGreater(got.gamma, 0.0)
        self.assertEqual(got.estimate.effect, plain.effect)
        self.assertEqual([a for a, b in zip(got.estimate.pool, plain.pool) if b <= 0.0 and a != b], [])
        self.assertTrue(any(a < b for a, b in zip(got.estimate.pool, plain.pool) if b > 0.0))

    def test_the_forecast_of_the_upper_arm_moves_only_the_upper_half(self):
        pairs = pairs_of(200)
        xs = [0.5 + (i % 10) / 5.0 for i in range(200)]
        wide = [sc.StatePair(p.raw * (1.0 + 0.8 * (x - 1.0)), p.scale, p.flags, None) for p, x in zip(pairs, xs)]
        fit = self.fit(wide, xs, dsp.ARMS[2])
        up = dsp.lead_quantiles(fit, dsp.ARMS[2], centre=10.0, scale=2.0, flags=NONE, ratio=3.0)
        same = dsp.lead_quantiles(fit, dsp.ARMS[2], centre=10.0, scale=2.0, flags=NONE, ratio=1.0)
        shift = 0.0
        below = [(a, b) for a, b, v in zip(up, same, fit.estimate.pool) if shift + v <= 0.0]
        above = [(a, b) for a, b, v in zip(up, same, fit.estimate.pool) if shift + v > 0.0]
        self.assertTrue(below and above)
        self.assertTrue(all(a == b for a, b in below))
        self.assertTrue(all(a > b for a, b in above))
        self.assertEqual(up, sorted(up))

    def test_the_whole_law_arm_widens_both_sides_in_a_wide_state_and_narrows_in_a_quiet_one(self):
        pairs = pairs_of(200)
        xs = [0.5 + (i % 10) / 5.0 for i in range(200)]
        wide = [sc.StatePair(p.raw * (1.0 + 0.8 * (x - 1.0)), p.scale, p.flags, None) for p, x in zip(pairs, xs)]
        fit = self.fit(wide, xs, dsp.ARMS[0])
        loud = dsp.lead_quantiles(fit, dsp.ARMS[0], centre=0.0, scale=1.0, flags=NONE, ratio=3.0)
        quiet = dsp.lead_quantiles(fit, dsp.ARMS[0], centre=0.0, scale=1.0, flags=NONE, ratio=0.5)
        self.assertGreater(loud[-1] - loud[0], quiet[-1] - quiet[0])


class DeclaredArmsTests(unittest.TestCase):

    def test_the_arms_are_the_declared_three(self):
        self.assertEqual([a.name for a in dsp.ARMS], ["d1_iqr", "d2_upper_half", "d3_iqr_upper_tail"])
        self.assertEqual([(a.numerator, a.upper_only) for a in dsp.ARMS], [("iqr", False), ("upper", False), ("iqr", True)])

    def test_the_base_terms_are_arm_s3s(self):
        self.assertEqual(dsp.BASE_ARM, sc.ARMS[2])
        self.assertTrue(dsp.BASE_ARM.robust)


class AvailabilityTests(unittest.TestCase):

    DI = index_of("2024-06-05")

    def anchor(self):
        from repo_model import protocol_benchmarks as pb
        return pb._anchor(PANEL, self.DI, tpb.REGISTRY, tpb.DECISION)

    def test_the_tracked_declaration_admits_the_anchors_percentiles(self):
        dsp.require_available(PANEL, self.DI, self.anchor(), registry=tpb.REGISTRY, decision_time=tpb.DECISION)

    def test_a_percentile_published_after_the_anchors_spread_is_refused(self):
        registry = copy.deepcopy(tpb.REGISTRY)
        registry["nyfed_sofr"]["field_release_lags"] = {
            "SOFR_p25": dict(registry["nyfed_sofr"]["release_lag"], days=2),
            "SOFR_p75": dict(registry["nyfed_sofr"]["release_lag"], days=2),
        }
        with self.assertRaises(LookAheadError):
            dsp.require_available(PANEL, self.DI, self.anchor(), registry=registry, decision_time=tpb.DECISION)


class WalkTests(unittest.TestCase):

    DAYS = [row.date for row in PANEL if date(2024, 6, 3) <= row.date <= date(2024, 6, 7)]

    @classmethod
    def setUpClass(cls):
        cls.walk = dsp.walk(PANEL, cls.DAYS, TABLE_ALL, **SETTINGS)
        cls.reference = sc.walk(PANEL, cls.DAYS, TABLE_ALL, {}, [dsp.BASE_ARM], **SETTINGS)

    def test_arm_a_and_arm_s3_are_the_published_walks_exactly(self):
        self.assertEqual(self.walk.forecasts[dsp.ARM_A], self.reference.forecasts[dsp.ARM_A])
        self.assertEqual(self.walk.forecasts[dsp.BASE_ARM.name], self.reference.forecasts[dsp.BASE_ARM.name])

    def test_every_model_has_23_ordered_quantiles_at_every_lead_on_the_same_days(self):
        days = set(self.walk.forecasts[dsp.ARM_A])
        self.assertTrue(days)
        for name in dsp.MODEL_NAMES:
            self.assertEqual(set(self.walk.forecasts[name]), days)
            for leads in self.walk.forecasts[name].values():
                for q in leads.values():
                    self.assertEqual(len(q), 23)
                    self.assertEqual(q, sorted(q))

    def test_a_future_percentile_moves_no_forecast(self):
        di = index_of("2024-06-07")
        panel = list(PANEL)
        for i in range(di, len(panel)):  # the row after the anchor (di - 1) onward is not public at the decision
            values = dict(panel[i].values)
            values["sofr_p75"] = float(values["sofr"]) + 0.5
            values["sofr_p25"] = float(values["sofr"]) - 0.5
            panel[i] = dataclasses.replace(panel[i], values=values)
        other = dsp.walk(panel, [PANEL[di].date], TABLE_ALL, **SETTINGS)
        base = dsp.walk(PANEL, [PANEL[di].date], TABLE_ALL, **SETTINGS)
        self.assertEqual(other.forecasts, base.forecasts)

    def test_a_past_percentile_moves_the_dispersion_arms_and_not_arm_s3(self):
        di = index_of("2024-06-07")
        anchor = di - 1
        panel = list(PANEL)
        values = dict(panel[anchor].values)
        values["sofr_p75"] = float(values["sofr"]) + 0.5
        values["sofr_p25"] = float(values["sofr"]) - 0.5
        panel[anchor] = dataclasses.replace(panel[anchor], values=values)
        other = dsp.walk(panel, [PANEL[di].date], TABLE_ALL, **SETTINGS)
        base = dsp.walk(PANEL, [PANEL[di].date], TABLE_ALL, **SETTINGS)
        self.assertEqual(other.forecasts[dsp.BASE_ARM.name], base.forecasts[dsp.BASE_ARM.name])
        self.assertNotEqual(other.forecasts["d1_iqr"], base.forecasts["d1_iqr"])

    def test_a_future_spread_moves_no_forecast(self):
        di = index_of("2024-06-07")
        panel = list(PANEL)
        for i in range(di + 1, len(panel)):
            values = dict(panel[i].values)
            values["sofr"] = float(values["iorb"]) + 40.0
            panel[i] = dataclasses.replace(panel[i], values=values)
        other = dsp.walk(panel, [PANEL[di].date], TABLE_ALL, **SETTINGS)
        base = dsp.walk(PANEL, [PANEL[di].date], TABLE_ALL, **SETTINGS)
        self.assertEqual(other.forecasts, base.forecasts)

    def test_the_one_step_walk_is_refused(self):
        with self.assertRaisesRegex(ValueError, "one-step pairs"):
            dsp.walk(PANEL, self.DAYS[:2], TABLE_ALL, **SETTINGS, training_pairs="one_step")

    def test_the_fits_are_renewed_with_the_base_model(self):
        self.assertEqual(len(self.walk.fits), 1)
        self.assertEqual(set(self.walk.leads), set(self.walk.fits))


if __name__ == "__main__":
    unittest.main()
