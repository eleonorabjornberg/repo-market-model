"""A faster-reacting scale on scaled mean reversion (#1153; H5 step 3, fix of the clustered misses, development tier).

`metadata/faster_scale_1153.json` is the declaration; `repo_model.spread_mr_scale` is its arithmetic. What these tests pin: each
scale on hand cases (MAD over 5 or 10 days, the blend of the 5- and 20-day scales, the EWMA and its asymmetric version, the floor);
that the scale at a row reads only rows at or before it; that the arm with #941's scale reproduces #941's variant exactly; that a
future spread moves no forecast of any arm; that yesterday's realised miss is read from the anchor and the rows before it, never
after; the miss factor and the target-day type factors on hand cases; that a settlement is not a type where the as-of rule refuses
it; and that a one-step fit of the calendar columns is refused by `one_step_guard`.

Recorded mutations (each applied to the tree, the named test run, and restored):

* `scale_rows`: `range(row - scale.reach, row + 1)` replaced with `range(row - scale.reach + 1, row + 2)`, so the scale at the
  anchor reads the row after it, which was not public at the decision instant. `test_a_future_spread_moves_no_forecast` errored
  with `LookAheadError` (raised by `protocol_benchmarks._require_public`: the scale reads a row after the last one public at the
  decision instant); restored, it passes.
* `missed_at`: the spread compared with the band, `spreads[row]`, replaced with `spreads[row + 1]`, so yesterday's miss reads
  the day after the anchor. `test_a_future_spread_moves_no_forecast` errored with `IndexError` for the two arms with miss feedback
  (`v3_miss`, `v4_v3_miss_cal`): the spreads handed to the fit end at the anchor, so a read past it has nothing to read; the
  other arms passed, as they should. Restored, it passes.
* `fit_type_factors`: delete the `@guard_one_step_fit` line. `test_a_one_step_fit_of_a_calendar_column_is_refused_by_the_guard`
  failed with `AssertionError` (the `ValueError` raised was the function's own "direct pairs only", not the guard's message naming
  the column); restored, it passes.
* All three were run with the first run of the file failing for want of the module (`ImportError`, test written first).
"""

from __future__ import annotations

import dataclasses
import math
import statistics
import unittest
import unittest.mock
from pathlib import Path

from repo_model import announced_iorb
from repo_model import spread_mean_reversion as smr
from repo_model import spread_mr_calendar as cal
from repo_model import spread_mr_fhs as fhs
from repo_model import spread_mr_scale as sc
from repo_model.splits import LookAheadError

import test_protocol_benchmarks as tpb

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / "tests" / "fixtures" / "snapshots" / "fed-iorb-announcements" / "iorb_changes.csv"
SETTINGS = dict(registry=tpb.REGISTRY, decision_time=tpb.DECISION, splits=tpb.SPLITS)
SPREADS = [0.0, 1.0, 1.0, 4.0, 2.0, 2.0, 2.5, 10.0]
HALF_PI = math.sqrt(math.pi / 2.0)


def with_spread(row, spread_bps):
    values = dict(row.values)
    values["sofr"] = float(values["iorb"]) + spread_bps / 100.0
    return dataclasses.replace(row, values=values)


class ScaleTests(unittest.TestCase):

    def at(self, scale, row):
        return sc.ScaleSeries(SPREADS, scale).at(row)

    def test_the_mad_over_a_short_window(self):
        # row 7, window 2: changes 0.5 and 7.5, median 4.0
        self.assertAlmostEqual(self.at(sc.Scale("m2", "mad", windows=(2,), floor=0.5), 7), 1.4826 * 4.0)

    def test_the_blend_is_the_mean_of_the_two_unfloored_scales(self):
        # row 7: window 2 gives 1.4826 * 4.0, window 4 (changes -2, 0, 0.5, 7.5) gives 1.4826 * 1.25
        blend = sc.Scale("b", "blend", windows=(2, 4), floor=0.5)
        self.assertAlmostEqual(self.at(blend, 7), 0.5 * (1.4826 * 4.0 + 1.4826 * 1.25))

    def test_the_ewma_weights_recent_changes_most(self):
        # row 3, three changes, newest first: 3, 0, 1; half-life 1 so weights 1, 0.5, 0.25
        ewma = sc.Scale("e", "ewma", half_life=1.0, rows=3, floor=0.01)
        self.assertAlmostEqual(self.at(ewma, 3), HALF_PI * (1 * 3 + 0.5 * 0 + 0.25 * 1) / 1.75)

    def test_the_asymmetric_ewma_weights_an_upward_change_more(self):
        asym = sc.Scale("e", "ewma", half_life=1.0, rows=3, asym=0.5, floor=0.01)
        # row 3: both nonzero changes are upward, weight 1.5 each
        self.assertAlmostEqual(self.at(asym, 3), HALF_PI * 1.5 * (1 * 3 + 0.25 * 1) / 1.75)
        # row 4: newest first -2 (down, weight 0.5), 3 (up, 1.5), 0: 0.5 * 2 * 1 + 1.5 * 3 * 0.5
        self.assertAlmostEqual(self.at(asym, 4), HALF_PI * (0.5 * 2 * 1 + 1.5 * 3 * 0.5) / 1.75)

    def test_the_floor_binds_when_the_window_is_calm(self):
        calm = sc.ScaleSeries([5.0] * 10, sc.Scale("m", "mad", windows=(4,), floor=0.5))
        self.assertEqual(calm.at(6), 0.5)

    def test_there_is_no_scale_before_the_window_is_full(self):
        self.assertIsNone(self.at(sc.Scale("m4", "mad", windows=(4,)), 3))
        self.assertIsNone(self.at(sc.Scale("e", "ewma", half_life=1.0, rows=3), 2))

    def test_the_scale_at_a_row_reads_only_rows_up_to_it(self):
        later = list(SPREADS)
        later[7] = 500.0
        for scale in (sc.Scale("m", "mad", windows=(4,)), sc.Scale("b", "blend", windows=(2, 4)),
                      sc.Scale("e", "ewma", half_life=2.0, rows=4), sc.Scale("a", "ewma", half_life=2.0, rows=4, asym=0.5)):
            self.assertEqual(sc.ScaleSeries(SPREADS, scale).at(5), sc.ScaleSeries(later, scale).at(5))
            self.assertEqual(max(sc.scale_rows(5, scale)), 5)

    def test_the_declared_scales_are_the_issues(self):
        names = {arm.name: arm for arm in sc.ARMS}
        self.assertEqual(set(names), {
            "v1_mad5", "v1_mad10", "v1_blend5_20", "v2_ewma_hl3", "v2_ewma_hl5", "v2_ewma_hl10", "v2_ewma_hl5_asym", "v3_miss"})
        self.assertEqual(names["v1_blend5_20"].scale.windows, (5, 20))
        self.assertEqual([names[n].scale.half_life for n in ("v2_ewma_hl3", "v2_ewma_hl5", "v2_ewma_hl10")], [3.0, 5.0, 10.0])
        self.assertEqual(names["v2_ewma_hl5_asym"].scale.asym, sc.ASYM)
        self.assertTrue(names["v3_miss"].miss)
        self.assertEqual(names["v3_miss"].scale, sc.BASE_SCALE)
        self.assertEqual((sc.BASE_SCALE.kind, sc.BASE_SCALE.windows, sc.BASE_SCALE.floor), ("mad", (20,), 0.5))
        calendar = sc.with_calendar(names["v1_mad5"])
        self.assertTrue(calendar.calendar)
        self.assertEqual(calendar.scale, names["v1_mad5"].scale)

    def test_a_bad_scale_is_refused(self):
        with self.assertRaises(ValueError):
            sc.Scale("x", "median", windows=(5,))
        with self.assertRaises(ValueError):
            sc.Scale("x", "ewma", half_life=0.0, rows=5)
        with self.assertRaises(ValueError):
            sc.Scale("x", "mad", windows=(1,))


class MissTests(unittest.TestCase):

    def test_a_miss_is_an_outcome_outside_the_band(self):
        spreads = [0.0, 0.0, 6.0, 1.0]
        # the band of row 2 from row 1: centre 0, scale 2, z in [-1, 1] -> [-2, 2]
        self.assertTrue(sc.missed_at(spreads, 2, centre=0.0, scale=2.0, lo=-1.0, hi=1.0))
        self.assertFalse(sc.missed_at(spreads, 3, centre=0.0, scale=2.0, lo=-1.0, hi=1.0))
        # the edge is inside: a closed band
        self.assertFalse(sc.missed_at([0.0, 2.0], 1, centre=0.0, scale=2.0, lo=-1.0, hi=1.0))
        self.assertTrue(sc.missed_at([0.0, -2.5], 1, centre=0.0, scale=2.0, lo=-1.0, hi=1.0))

    def test_the_factor_is_the_ratio_of_mean_absolute_standardised_residuals_between_one_and_the_cap(self):
        miss = [2.0, -3.0, 4.0] * 10
        clear = [1.0, -1.0, 2.0] * 10
        self.assertAlmostEqual(sc.miss_factor(miss, clear), statistics.fmean(abs(z) for z in miss) / statistics.fmean(abs(z) for z in clear))
        self.assertEqual(sc.miss_factor(clear, miss), 1.0)  # never narrows

    def test_the_factor_is_capped_where_the_ordinary_residuals_are_nearly_zero(self):
        # a flat floor period: residuals of float noise on ordinary days, a few real ones after a miss (the case that made a ratio of medians explode)
        self.assertEqual(sc.miss_factor([2.0] * 30, [1e-12] * 30), sc.FACTOR_CAP)
        self.assertEqual(sc.miss_factor([2.0] * 30, [0.0] * 30), 1.0)  # an exactly flat pool has no ratio

    def test_too_few_misses_give_no_factor(self):
        self.assertEqual(sc.miss_factor([5.0] * (sc.MISS_MIN - 1), [1.0] * 100), 1.0)
        self.assertEqual(sc.miss_factor([5.0] * 50, [1.0] * (sc.MISS_MIN - 1)), 1.0)


class TypeTests(unittest.TestCase):

    def test_the_first_flagged_type_in_priority_order_is_the_type(self):
        self.assertEqual(sc.type_of({"quarter_end": 1, "month_end": 1, "settlement_coupon": 1}), "quarter_end")
        self.assertEqual(sc.type_of({"tax_date": 1, "month_end": 1}), "tax_date")
        self.assertEqual(sc.type_of({"month_end": 1, "settlement_coupon": 1}), "month_end")
        self.assertEqual(sc.type_of({"settlement_coupon": 1}), "settlement_coupon")
        self.assertIsNone(sc.type_of({"quarter_end": 0, "fomc_day": 1}))
        self.assertIsNone(sc.type_of({}))  # a settlement the as-of rule refuses at lead 2 is not in the flags read

    def test_a_type_factor_is_the_shrunk_ratio_to_the_ordinary_mean(self):
        pairs = [(1.0, None)] * 30 + [(3.0, "quarter_end")] * 10 + [(1.0, "month_end")] * 2
        out = sc.fit_type_factors(pairs, regressors=("quarter_end",), training_pairs="direct")
        # ratio 3, n = 10, shrink n / (n + CAL_K): 1 + 10/20 * 2
        self.assertAlmostEqual(out["quarter_end"], 1.0 + 10.0 / (10.0 + sc.CAL_K) * 2.0)
        self.assertNotIn("month_end", out)  # two flagged pairs are fewer than MIN_FLAGGED

    def test_a_type_factor_is_floored(self):
        pairs = [(4.0, None)] * 20 + [(0.0, "tax_date")] * 200
        out = sc.fit_type_factors(pairs, regressors=("tax_date",), training_pairs="direct")
        self.assertEqual(out["tax_date"], cal.M_MIN)

    def test_a_type_factor_is_capped(self):
        pairs = [(1e-12, None)] * 20 + [(5.0, "quarter_end")] * 200
        out = sc.fit_type_factors(pairs, regressors=("quarter_end",), training_pairs="direct")
        self.assertEqual(out["quarter_end"], sc.FACTOR_CAP)

    def test_a_one_step_fit_of_a_calendar_column_is_refused_by_the_guard(self):
        with self.assertRaises(ValueError) as caught:
            sc.fit_type_factors([(1.0, None)] * 5, regressors=("quarter_end",), training_pairs="one_step")
        self.assertIn("quarter_end", str(caught.exception))

    def test_an_unknown_training_pairs_value_is_refused(self):
        with self.assertRaises(ValueError):
            sc.fit_type_factors([(1.0, None)] * 5, regressors=(), training_pairs="rolling")


class PanelTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel = tpb.published_panel()["rows"]
        cls.table = cal.TermTable(cls.panel, announced_iorb.load_announcements(TABLE))
        cls.t = next(i for i, row in enumerate(cls.panel) if row.date.isoformat() == "2022-03-07")
        cls.anchor = cls.t - 1
        cls.levels = smr.ordinary_levels(cls.panel, SETTINGS["splits"])
        cls.arms = list(sc.ARMS) + [sc.with_calendar(sc.ARMS[0]), sc.with_calendar(sc.ARMS[-1])]

    def forecast_of(self, panel, arm):
        levels = smr.ordinary_levels(panel, SETTINGS["splits"])
        base = smr.fit(panel, self.t, **SETTINGS, levels=levels)
        table = cal.TermTable(panel, announced_iorb.load_announcements(TABLE))
        fitted = sc.fit(panel, self.t, [arm], base=base, table=table, **SETTINGS, levels=levels)
        return sc.forecast(panel, self.t, fitted[arm.name], arm, base, table=table, **SETTINGS, levels=levels)

    def test_the_arm_with_the_base_scale_reproduces_941s_variant(self):
        plain = sc.Arm("plain", sc.BASE_SCALE)
        mine = self.forecast_of(self.panel, plain)
        base = smr.fit(self.panel, self.t, **SETTINGS, levels=self.levels)
        variant = fhs.VARIANTS[0]
        fitted = fhs.fit(self.panel, self.t, [variant], base=base, **SETTINGS, levels=self.levels)
        theirs = fhs.forecast(self.panel, self.t, fitted[variant.name], base, variant, **SETTINGS, levels=self.levels)
        for h in theirs:
            self.assertEqual(mine[h], theirs[h])

    def test_a_future_spread_moves_no_forecast(self):
        shocked = list(self.panel)
        for i in range(self.anchor + 1, len(shocked)):
            shocked[i] = with_spread(shocked[i], 250.0 + i)
        for arm in self.arms:
            with self.subTest(arm=arm.name):
                self.assertEqual(self.forecast_of(self.panel, arm), self.forecast_of(shocked, arm))

    def test_the_anchor_spread_moves_the_forecast(self):
        shocked = list(self.panel)
        shocked[self.anchor] = with_spread(shocked[self.anchor], self.panel[self.anchor].spread_bps + 30.0)
        for arm in self.arms:
            with self.subTest(arm=arm.name):
                self.assertNotEqual(self.forecast_of(self.panel, arm)[1], self.forecast_of(shocked, arm)[1])

    def test_a_scale_that_reads_a_row_after_the_anchor_is_refused(self):
        arm = sc.ARMS[0]
        levels = self.levels
        base = smr.fit(self.panel, self.t, **SETTINGS, levels=levels)
        with unittest.mock.patch.object(sc, "scale_rows", lambda row, scale: range(row - scale.reach + 1, row + 2)):
            with self.assertRaises(LookAheadError):
                sc.fit(self.panel, self.t, [arm], base=base, **SETTINGS, levels=levels)

    def test_the_arms_differ_from_each_other_and_from_the_base(self):
        laws = {arm.name: self.forecast_of(self.panel, arm)[1] for arm in sc.ARMS}
        laws["base"] = self.forecast_of(self.panel, sc.Arm("plain", sc.BASE_SCALE))[1]
        self.assertGreater(len({tuple(law) for law in laws.values()}), 6)

    def test_a_forecast_with_too_little_history_is_refused(self):
        with self.assertRaises(smr.InsufficientHistory):
            sc.fit(self.panel, 20, [sc.ARMS[0]], table=self.table, **SETTINGS)


class WalkTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel = tpb.published_panel()["rows"]
        cls.table = cal.TermTable(cls.panel, announced_iorb.load_announcements(TABLE))
        cls.days = [row.date for row in cls.panel if row.date.isoformat() >= "2021-01-04"][:50]

    def test_the_walk_refits_every_21_decision_days_and_matches_941s_on_the_base_scale(self):
        arms = [sc.Arm("plain", sc.BASE_SCALE), sc.with_calendar(sc.ARMS[0])]
        walk = sc.walk(self.panel, self.days, arms, table=self.table, **SETTINGS)
        theirs = fhs.walk(self.panel, self.days, [fhs.VARIANTS[0]], **SETTINGS)
        self.assertEqual(len(walk.fits), 3)  # 50 days: refits on days 1, 22 and 43
        self.assertEqual(walk.forecasts["plain"], theirs.forecasts[fhs.VARIANTS[0].name])
        self.assertNotEqual(walk.forecasts[arms[1].name], walk.forecasts["plain"])


if __name__ == "__main__":
    unittest.main()
