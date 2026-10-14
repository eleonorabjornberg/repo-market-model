"""The mean-reversion variants of #761 (H5 step 2; development tier): context-pooled residuals and the B2 average.

The variants are declared in `metadata/spread_distribution_761.json`; `repo_model.spread_mr_variants` is their
arithmetic. Stdlib only. What these tests pin: the context of a target day (a risk day; an ordinary day after one; an
ordinary day after an ordinary day) and that it is read from the calendar columns alone; the pools and their fallback;
the weight grid, its choice on trailing scored days that were public at the refit, and its defaults; the quantile
average; the as-of guard (a change to every spread after the anchor moves no forecast of any variant); the recentred B1
of #741 that serves as a reference row.

Recorded mutations (the new leakage guards; each run on the tests named, then restored):

* `CalendarView.__getitem__`: `if column not in CALENDAR_COLUMNS:` replaced with `if False:`, so a context could read the
  spread of a target row. `CalendarViewTests.test_a_column_that_is_not_a_calendar_column_is_refused` failed with
  `AssertionError` ("LookAheadError not raised"); restored, it passes. (No context reads such a column, so the other
  tests did not notice: `ContextTests.test_a_context_reads_no_column_but_the_calendar` passed under this mutation.)
* `choose_weight`: `if index + max(HORIZONS) <= anchor` replaced with `if index + max(HORIZONS) <= anchor + 1`, so a
  trailing day whose last target is the row after the anchor, not public at the decision instant, is scored.
  `WeightTests.test_a_trailing_day_with_a_target_after_the_anchor_is_not_scored` and
  `AsOfTests.test_a_future_spread_moves_no_forecast` both errored with `LookAheadError` ("... reads ..., after ..., the last
  row public at the decision instant", raised by `protocol_benchmarks._require_public`); restored, both pass.
"""

from __future__ import annotations

import dataclasses
import unittest
from datetime import date

from repo_model import protocol_benchmarks as pb
from repo_model import scoring_protocol as sp
from repo_model import spread_mean_reversion as smr
from repo_model import spread_mr_variants as var
from repo_model.splits import LookAheadError

import test_protocol_benchmarks as tpb


def panel_and_settings():
    panel = tpb.published_panel()["rows"]
    return panel, dict(registry=tpb.REGISTRY, decision_time=tpb.DECISION, splits=tpb.SPLITS)


def index_of(panel, day):
    return next(i for i, row in enumerate(panel) if row.date.isoformat() == day)


def with_spread(row, spread_bps):
    values = dict(row.values)
    values["sofr"] = float(values["iorb"]) + spread_bps / 100.0
    return dataclasses.replace(row, values=values)


def with_values(row, **changes):
    values = dict(row.values)
    values.update(changes)
    return dataclasses.replace(row, values=values)


class CalendarViewTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = panel_and_settings()

    def test_the_calendar_columns_are_readable(self):
        view = var.calendar_view(self.panel[100])
        for column in var.CALENDAR_COLUMNS:
            self.assertEqual(view[column], self.panel[100].values[column])

    def test_a_column_that_is_not_a_calendar_column_is_refused(self):
        view = var.calendar_view(self.panel[100])
        for column in ("sofr", "iorb", "reserve_balances", "tgcr"):
            with self.assertRaises(LookAheadError):
                view[column]
            with self.assertRaises(LookAheadError):
                view.get(column)

    def test_the_view_has_only_the_calendar_columns(self):
        self.assertEqual(set(var.calendar_view(self.panel[100])), set(var.CALENDAR_COLUMNS))


class ContextTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = panel_and_settings()
        cls.splits = cls.settings["splits"]
        cls.kinds = [var.target_context(cls.panel, i, cls.splits) for i in range(1, len(cls.panel))]

    def test_every_row_has_one_of_the_three_contexts(self):
        self.assertEqual(set(self.kinds), set(var.CONTEXTS))

    def test_a_coupon_settlement_makes_an_ordinary_day_a_risk_day(self):
        coupon = next(
            i for i in range(5, len(self.panel))
            if self.splits.reporting_day_type(self.panel[i].date, self.panel[i].values) == "ordinary"
            and float(self.panel[i].values["treasury_settlement_coupons"]) > 0.0
        )
        self.assertTrue(var.is_risk_day(self.panel[coupon], self.splits))
        self.assertEqual(var.target_context(self.panel, coupon, self.splits), "risk_day")

    def test_a_non_ordinary_day_is_a_risk_day(self):
        quarter_end = next(i for i in range(5, len(self.panel)) if float(self.panel[i].values["quarter_end"]) == 1.0)
        self.assertEqual(var.target_context(self.panel, quarter_end, self.splits), "risk_day")

    def test_the_day_after_a_risk_day_is_ordinary_after_risk_when_it_is_ordinary(self):
        found = 0
        for i in range(2, len(self.panel)):
            if var.is_risk_day(self.panel[i - 1], self.splits) and not var.is_risk_day(self.panel[i], self.splits):
                self.assertEqual(var.target_context(self.panel, i, self.splits), "ordinary_after_risk")
                found += 1
        self.assertGreater(found, 50)

    def test_an_ordinary_day_after_an_ordinary_day_is_calm(self):
        found = 0
        for i in range(2, len(self.panel)):
            if not var.is_risk_day(self.panel[i - 1], self.splits) and not var.is_risk_day(self.panel[i], self.splits):
                self.assertEqual(var.target_context(self.panel, i, self.splits), "ordinary_after_ordinary")
                found += 1
        self.assertGreater(found, 500)

    def test_the_first_row_has_no_context(self):
        with self.assertRaises(ValueError):
            var.target_context(self.panel, 0, self.splits)

    def test_a_context_reads_no_column_but_the_calendar(self):
        shocked = [with_values(row, sofr=99.0, iorb=1.0, tgcr=50.0, reserve_balances=-5.0) for row in self.panel]
        self.assertEqual(
            self.kinds, [var.target_context(shocked, i, self.splits) for i in range(1, len(shocked))]
        )


class PoolTests(unittest.TestCase):

    def test_a_pool_of_enough_values_is_used(self):
        pools = {"risk_day": [float(v) for v in range(40)]}
        got = var.context_quantiles(pools, "risk_day", fallback=[9.0] * len(sp.GRID))
        self.assertEqual(got, pb.empirical_quantiles(sorted(pools["risk_day"])))

    def test_a_thin_pool_falls_back_to_the_pooled_residuals(self):
        pools = {"risk_day": [float(v) for v in range(var.POOL_MIN - 1)]}
        fallback = [float(i) for i in range(len(sp.GRID))]
        self.assertEqual(var.context_quantiles(pools, "risk_day", fallback=fallback), fallback)

    def test_a_missing_pool_falls_back(self):
        fallback = [float(i) for i in range(len(sp.GRID))]
        self.assertEqual(var.context_quantiles({}, "risk_day", fallback=fallback), fallback)

    def test_the_pool_at_the_minimum_is_used(self):
        pools = {"risk_day": [float(v) for v in range(var.POOL_MIN)]}
        fallback = [100.0] * len(sp.GRID)
        self.assertNotEqual(var.context_quantiles(pools, "risk_day", fallback=fallback), fallback)


class ContextFitTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = panel_and_settings()
        cls.t = index_of(cls.panel, "2022-03-07")
        cls.base = smr.fit(cls.panel, cls.t, **cls.settings)
        cls.cfit = var.context_fit(cls.panel, cls.t, **cls.settings)

    def test_phi_and_the_pooled_residuals_are_the_base_fit(self):
        self.assertEqual(self.cfit.base.phi, self.base.phi)
        self.assertEqual(self.cfit.base.residuals, self.base.residuals)

    def test_the_pools_partition_each_lead_s_pairs(self):
        for h in sp.HORIZONS:
            self.assertEqual(sum(self.cfit.sizes[h].values()), self.base.pairs[h])

    def test_a_context_forecast_differs_from_the_pooled_one_where_a_pool_is_used(self):
        mr = smr.forecast(self.panel, self.t, self.base, **self.settings)
        ctx = var.context_forecast(self.panel, self.t, self.cfit, **self.settings)
        self.assertNotEqual(mr, ctx)
        for h in sp.HORIZONS:
            self.assertEqual(len(ctx[h]), len(sp.GRID))
            self.assertEqual(ctx[h], sorted(ctx[h]))

    def test_with_no_pool_big_enough_the_forecast_is_the_base_forecast(self):
        original = var.POOL_MIN
        var.POOL_MIN = 10 ** 9
        try:
            ctx = var.context_forecast(self.panel, self.t, var.context_fit(self.panel, self.t, **self.settings), **self.settings)
        finally:
            var.POOL_MIN = original
        self.assertEqual(ctx, smr.forecast(self.panel, self.t, self.base, **self.settings))


class BlendTests(unittest.TestCase):

    def setUp(self):
        self.a = {h: [float(i + h) for i in range(len(sp.GRID))] for h in sp.HORIZONS}
        self.b = {h: [2.0 * i - h for i in range(len(sp.GRID))] for h in sp.HORIZONS}

    def test_the_weight_one_is_the_first_leg_and_zero_the_second(self):
        self.assertEqual(var.blend(self.a, self.b, 1.0), self.a)
        self.assertEqual(var.blend(self.a, self.b, 0.0), self.b)

    def test_the_average_is_level_by_level(self):
        got = var.blend(self.a, self.b, 0.3)
        for h in sp.HORIZONS:
            for i in range(len(sp.GRID)):
                self.assertAlmostEqual(got[h][i], 0.3 * self.a[h][i] + 0.7 * self.b[h][i])

    def test_the_average_of_two_non_decreasing_laws_does_not_cross(self):
        for w in var.WEIGHT_GRID:
            for q in var.blend(self.a, self.b, w).values():
                self.assertEqual(q, sorted(q))

    def test_a_weight_off_the_grid_is_refused(self):
        with self.assertRaises(ValueError):
            var.blend(self.a, self.b, 0.37)


class WeightTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = panel_and_settings()
        cls.anchor = 400
        cls.dates = [row.date for row in cls.panel]

    def exact(self, index, shift=0.0):
        """A forecast that puts the realised spread at every level, shifted by `shift`."""

        return {h: [self.panel[index + h].spread_bps + shift] * len(sp.GRID) for h in sp.HORIZONS}

    def history(self, count, leg_shift, b2_shift):
        days = range(self.anchor - 5 - count + 1, self.anchor - 5 + 1)
        return ({i: self.exact(i, leg_shift) for i in days}, {i: self.exact(i, b2_shift) for i in days})

    def test_the_grid_is_zero_to_one_in_tenths(self):
        self.assertEqual(var.WEIGHT_GRID, tuple(k / 10.0 for k in range(11)))

    def test_a_better_leg_gets_the_whole_weight(self):
        leg, b2 = self.history(80, 0.0, 6.0)
        self.assertEqual(var.choose_weight(self.panel, self.anchor, leg, b2), 1.0)

    def test_a_better_b2_gets_the_whole_weight(self):
        leg, b2 = self.history(80, 6.0, 0.0)
        self.assertEqual(var.choose_weight(self.panel, self.anchor, leg, b2), 0.0)

    def test_offsetting_errors_pick_the_middle(self):
        leg, b2 = self.history(80, 3.0, -3.0)
        self.assertAlmostEqual(var.choose_weight(self.panel, self.anchor, leg, b2), 0.5)

    def test_a_tie_takes_the_larger_weight(self):
        leg, b2 = self.history(80, 0.0, 0.0)
        self.assertEqual(var.choose_weight(self.panel, self.anchor, leg, b2), 1.0)

    def test_too_few_trailing_days_give_the_default(self):
        leg, b2 = self.history(var.MIN_TRAIL - 1, 0.0, 6.0)
        self.assertEqual(var.choose_weight(self.panel, self.anchor, leg, b2), var.DEFAULT_WEIGHT)

    def test_only_the_last_trailing_days_count(self):
        # The oldest 100 days favour B2, the latest TRAIL_DAYS favour the leg: the weight follows the latest.
        count = var.TRAIL_DAYS + 100
        days = range(self.anchor - 5 - count + 1, self.anchor - 5 + 1)
        cut = self.anchor - 5 - var.TRAIL_DAYS
        leg = {i: self.exact(i, 6.0 if i <= cut else 0.0) for i in days}
        b2 = {i: self.exact(i, 0.0 if i <= cut else 6.0) for i in days}
        self.assertEqual(var.choose_weight(self.panel, self.anchor, leg, b2), 1.0)

    def test_a_day_without_b2_is_not_scored(self):
        leg, b2 = self.history(80, 0.0, 6.0)
        gap = sorted(b2)[10:20]
        for i in gap:
            del b2[i]
        self.assertEqual(var.choose_weight(self.panel, self.anchor, leg, b2), 1.0)

    def test_a_trailing_day_with_a_target_after_the_anchor_is_not_scored(self):
        # Day anchor - 4 has its last target (5 rows on) at anchor + 1: not public at the decision instant. It is left
        # out, however well it would have scored B2; the guard behind the filter raises if it is ever let in.
        leg, b2 = self.history(80, 0.0, 6.0)
        before = var.choose_weight(self.panel, self.anchor, leg, b2)
        late = self.anchor - 4
        leg[late], b2[late] = self.exact(late, 40.0), self.exact(late, 0.0)
        self.assertEqual(var.choose_weight(self.panel, self.anchor, leg, b2), before)


class AsOfTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = panel_and_settings()
        cls.days = [row.date for row in cls.panel if row.date.isoformat() >= "2021-01-04"][:130]
        cls.b2 = {d: pb.b2_forecast(cls.panel, index_of(cls.panel, d.isoformat()), **cls.settings) for d in cls.days}

    def anchor(self, panel, t):
        return pb._anchor(panel, t, self.settings["registry"], self.settings["decision_time"])

    def test_a_future_spread_moves_no_forecast(self):
        last = self.days[-1]
        t = index_of(self.panel, last.isoformat())
        anchor = self.anchor(self.panel, t)
        shocked = list(self.panel)
        for i in range(anchor + 1, len(shocked)):
            shocked[i] = with_spread(shocked[i], 250.0 + i)
        base = var.walk(self.panel, self.days, b2=self.b2, **self.settings)
        moved = var.walk(shocked, self.days, b2=self.b2, **self.settings)
        # Only the last decision day's forecast can see rows after the anchor, so only it is compared on the shocked
        # rows; the earlier days' anchors are earlier still.
        for name in var.NAMES:
            self.assertEqual(base.forecasts[name][last], moved.forecasts[name][last])
        self.assertEqual(base.weights, moved.weights)


class WalkTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = panel_and_settings()
        cls.days = [row.date for row in cls.panel if row.date.isoformat() >= "2021-01-04"][:130]
        cls.b2 = {d: pb.b2_forecast(cls.panel, index_of(cls.panel, d.isoformat()), **cls.settings) for d in cls.days}
        cls.walk = var.walk(cls.panel, cls.days, b2=cls.b2, **cls.settings)
        cls.mr = smr.walk(cls.panel, cls.days, **cls.settings)

    def test_the_variants_are_the_declared_three(self):
        self.assertEqual(var.NAMES, ("spread_mr_ctx", "spread_mr_b2", "spread_mr_ctx_b2"))
        self.assertEqual(set(self.walk.forecasts), set(var.NAMES) | {var.REFERENCE})

    def test_the_reference_is_spread_mr_level10_exactly(self):
        self.assertEqual(self.walk.forecasts[var.REFERENCE], self.mr.forecasts)

    def test_the_fit_is_renewed_on_the_first_day_and_every_21st(self):
        self.assertEqual(sorted(self.walk.weights), [self.days[0], self.days[21], self.days[42], self.days[63], self.days[84], self.days[105], self.days[126]])

    def test_the_first_weights_are_the_default_and_later_ones_are_chosen(self):
        first = self.walk.weights[self.days[0]]
        self.assertEqual(first, {"spread_mr_b2": var.DEFAULT_WEIGHT, "spread_mr_ctx_b2": var.DEFAULT_WEIGHT})
        later = self.walk.weights[self.days[126]]
        for w in later.values():
            self.assertIn(w, var.WEIGHT_GRID)

    def test_the_b2_average_uses_the_weight_of_its_refit(self):
        day = self.days[30]
        w = self.walk.weights[self.walk.fit_used[day]]["spread_mr_b2"]
        expected = var.blend(self.mr.forecasts[day], self.b2[day], w)
        self.assertEqual(self.walk.forecasts["spread_mr_b2"][day], expected)

    def test_every_forecast_is_five_leads_of_the_grid_without_crossing(self):
        for name, forecasts in self.walk.forecasts.items():
            for forecast in forecasts.values():
                self.assertEqual(set(forecast), set(sp.HORIZONS))
                for q in forecast.values():
                    self.assertEqual(len(q), len(sp.GRID))
                    self.assertEqual(q, sorted(q), name)

    def test_a_day_without_b2_has_no_blend_but_keeps_the_context_forecast(self):
        b2 = dict(self.b2)
        gone = self.days[40]
        del b2[gone]
        walk = var.walk(self.panel, self.days[:60], b2=b2, **self.settings)
        self.assertNotIn(gone, walk.forecasts["spread_mr_b2"])
        self.assertNotIn(gone, walk.forecasts["spread_mr_ctx_b2"])
        self.assertIn(gone, walk.forecasts["spread_mr_ctx"])
        self.assertIn(gone, walk.forecasts[var.REFERENCE])


class RecentredB1Tests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = panel_and_settings()
        cls.splits = cls.settings["splits"]

    def anchor(self, t):
        return pb._anchor(self.panel, t, self.settings["registry"], self.settings["decision_time"])

    def test_on_an_ordinary_anchor_it_is_b1(self):
        for t in range(600, 900):
            a = self.anchor(t)
            if self.splits.reporting_day_type(self.panel[a].date, self.panel[a].values) == "ordinary":
                self.assertEqual(
                    var.b1_recentred_forecast(self.panel, t, **self.settings),
                    pb.b1_forecast(self.panel, t, registry=self.settings["registry"], decision_time=self.settings["decision_time"]),
                )
                return
        self.fail("no ordinary anchor found")

    def test_on_a_risk_anchor_it_is_centred_on_the_last_ordinary_spread(self):
        for t in range(600, 1200):
            a = self.anchor(t)
            if self.splits.reporting_day_type(self.panel[a].date, self.panel[a].values) != "ordinary":
                last = next(
                    self.panel[s].spread_bps for s in range(a, -1, -1)
                    if self.splits.reporting_day_type(self.panel[s].date, self.panel[s].values) == "ordinary"
                )
                b1 = pb.b1_forecast(self.panel, t, registry=self.settings["registry"], decision_time=self.settings["decision_time"])
                got = var.b1_recentred_forecast(self.panel, t, **self.settings)
                for h in sp.HORIZONS:
                    shift = last - self.panel[a].spread_bps
                    for x, y in zip(got[h], b1[h]):
                        self.assertAlmostEqual(x, y + shift)
                return
        self.fail("no risk anchor found")

    def test_a_spread_after_the_anchor_moves_nothing(self):
        t = 800
        a = self.anchor(t)
        shocked = list(self.panel)
        for i in range(a + 1, len(shocked)):
            shocked[i] = with_spread(shocked[i], 500.0)
        self.assertEqual(
            var.b1_recentred_forecast(self.panel, t, **self.settings),
            var.b1_recentred_forecast(shocked, t, **self.settings),
        )


if __name__ == "__main__":
    unittest.main()
