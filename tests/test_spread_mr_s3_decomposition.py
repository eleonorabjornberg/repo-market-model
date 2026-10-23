"""The arms that take (s3) of #1145 apart (#1172; H5 step 3), and the miss and calendar-type scale factors of #1153 on (s3).

`metadata/s3_decomposition_1172.json` is the declaration; `repo_model.spread_mr_state_calendar` (the ridge and the Huber fit apart, the
settlement size times the scarcity state) and `repo_model.spread_mr_s3_v4` (v4 of #1153 on (s3)) are its arithmetic. What these tests
pin: that the ridge of 5 alone and the Huber fit alone are the two halves of (s3) and that (s3) is both; that a settlement size enters
as `size / 100 * state`, is zero on the floor, and is read only where the as-of rule admits it (lead 1); that a size is read from the
target row and a perturbation of any later row moves no forecast; that v4 on (s3) is (s3) exactly when it has no miss to feed back and
no type to scale, that a miss is judged against the band the model gave the anchor row and no later row, and that the factors are
fitted on direct pairs.

Recorded mutations (each applied to the tree, the named test run, and reverted):

* `SizeTable.read`: `if not cal.available(term, lead): continue` replaced with `if False: continue` and `cal.readable_offsets(term, lead)`
  with `term.span`, so a settlement size is read at lead 2 as if it were public. `test_a_size_is_not_read_beyond_lead_1` failed with `LookAheadError` (the settlement of the
  target row is public only on the panel day before it, after the decision day).
* `missed_anchor`: `source = row - k0` replaced with `source = row - k0 + 1`, so the band the anchor row is judged against is centred
  on the row one step later than the one the model forecast it from. `test_a_jump_at_the_anchor_is_a_miss_of_the_band_it_was_given`
  failed with `AssertionError` (`False is not true`: a band centred a row late contains the jump).
"""

from __future__ import annotations

import dataclasses
import unittest
from datetime import date
from unittest import mock

from repo_model import spread_mr_calendar as cal
from repo_model import spread_mr_fhs as fhs
from repo_model import spread_mr_s3_v4 as v4
from repo_model import spread_mr_scale as scale_mod
from repo_model import spread_mr_state_calendar as sc
from repo_model.splits import LookAheadError

import test_protocol_benchmarks as tpb
from test_spread_mr_state_calendar import ANNOUNCEMENTS, NONE, PANEL, SETTINGS, TABLE_ALL, index_of, planted, states_of

SIZES = sc.SizeTable(PANEL)
S1, S3 = sc.ARMS[0], sc.ARMS[2]


def fit(pairs, *, arm, terms=("quarter_end",), regressors=("quarter_end",)):
    return sc.fit_state_terms(
        pairs, regressors=regressors, terms=terms, interact=arm.interact, robust=arm.robust, ridge=arm.ridge, sized=arm.sized,
        training_pairs="direct",
    )


class DeclaredArmsTests(unittest.TestCase):

    def test_the_four_corners_of_the_decomposition_and_the_sized_arm(self):
        r1, r2, r3 = sc.R1, sc.R2, sc.R3
        self.assertEqual([a.name for a in sc.DECOMPOSITION], [S1.name, r1.name, r2.name, S3.name, r3.name])
        self.assertEqual([(sc.ridge_of(a), a.robust) for a in sc.DECOMPOSITION],
                         [(1.0, False), (5.0, False), (1.0, True), (5.0, True), (5.0, True)])
        self.assertEqual([a.sized for a in sc.DECOMPOSITION], [False, False, False, False, True])
        self.assertTrue(all(not a.interact and a.location == cal.NO_FOMC_IORB for a in sc.DECOMPOSITION))

    def test_the_arms_of_1145_are_unchanged(self):
        self.assertEqual([(sc.ridge_of(a), a.robust, a.interact, a.sized) for a in sc.ARMS],
                         [(1.0, False, False, False), (1.0, False, True, False), (5.0, True, False, False), (1.0, False, False, False)])


class RidgeAndHuberApartTests(unittest.TestCase):

    def test_the_ridge_of_5_alone_shrinks_a_thin_term_harder_than_the_ridge_of_1(self):
        pairs = planted(effect=3.0, flagged=4)
        light, heavy = fit(pairs, arm=S1), fit(pairs, arm=sc.R1)
        self.assertLess(heavy.effect["quarter_end"], light.effect["quarter_end"])
        self.assertEqual(heavy.iterations, 0)  # least squares: no Huber pass

    def test_the_ridge_of_5_alone_is_least_squares_with_that_penalty(self):
        pairs = planted(effect=3.0, flagged=10)
        design = [[1.0, float(p.flags["quarter_end"])] for p in pairs]
        expected = cal.solve_ridge(design, [p.raw / p.scale for p in pairs], 5.0)[1]
        self.assertAlmostEqual(fit(pairs, arm=sc.R1).effect["quarter_end"], expected)

    def test_the_huber_fit_alone_keeps_the_light_ridge_and_lets_an_outlier_set_less(self):
        pairs = planted(effect=2.0, outlier=60.0, flagged=14)
        robust_light, robust_heavy, ols = fit(pairs, arm=sc.R2), fit(pairs, arm=S3), fit(pairs, arm=S1)
        self.assertLess(robust_light.effect["quarter_end"], ols.effect["quarter_end"])
        self.assertGreater(robust_light.iterations, 0)
        self.assertGreater(robust_light.effect["quarter_end"], robust_heavy.effect["quarter_end"])  # the lighter ridge shrinks less

    def test_the_robust_arm_of_1145_is_both_halves(self):
        pairs = planted(effect=2.0, outlier=60.0, flagged=14)
        both = fit(pairs, arm=S3).effect["quarter_end"]
        self.assertAlmostEqual(both, fit(pairs, arm=dataclasses.replace(S3, ridge=sc.ROBUST_RIDGE)).effect["quarter_end"])
        self.assertNotAlmostEqual(both, fit(pairs, arm=sc.R1).effect["quarter_end"])
        self.assertNotAlmostEqual(both, fit(pairs, arm=sc.R2).effect["quarter_end"])


def sized_pairs(coefficient=4.0, n=90, flagged=20, state=lambda i: 1.0, size=lambda i: 150.0):
    """Pairs whose standardised residual is `coefficient * size / 100 * state` on a coupon settlement and noise otherwise."""

    out = []
    for i in range(n):
        flags = dict(NONE)
        on = i < flagged
        flags["settlement_coupon"] = 1 if on else 0
        s = state(i)
        value = size(i) if on else 0.0
        noise = (-1.0) ** i * (0.4 + (i % 3) * 0.2)
        z = noise + coefficient * value / sc.SIZE_UNIT * (0.0 if s is None else s)
        out.append(sc.StatePair(z, 1.0, flags, s, {"settlement_coupon": value, "settlement_bill": 0.0}))
    return out


class SettlementSizeTests(unittest.TestCase):

    TERMS = ("settlement_coupon",)

    def fit(self, pairs, **kw):
        return sc.fit_state_terms(
            pairs, regressors=("treasury_settlement_coupons",), terms=self.TERMS, interact=False, robust=False, ridge=0.01,
            sized=True, training_pairs="direct", **kw,
        )

    def test_a_planted_coefficient_on_size_times_state_is_recovered(self):
        estimate = self.fit(sized_pairs(coefficient=4.0, size=lambda i: 80.0 + 10.0 * (i % 8)))
        self.assertAlmostEqual(estimate.effect["settlement_coupon"], 4.0, delta=0.4)

    def test_a_bigger_settlement_moves_the_location_more_and_a_floor_state_moves_it_not_at_all(self):
        estimate = self.fit(sized_pairs(coefficient=4.0, size=lambda i: 80.0 + 10.0 * (i % 8)))
        flags = dict(NONE, settlement_coupon=1)

        def shift(size, state):
            return sc.standardised_shift(estimate, flags, state, {"settlement_coupon": size})

        self.assertAlmostEqual(shift(200.0, 1.0), 2.0 * shift(100.0, 1.0))
        self.assertAlmostEqual(shift(100.0, 0.5), 0.5 * shift(100.0, 1.0))
        self.assertEqual(shift(100.0, 0.0), 0.0)
        self.assertEqual(shift(100.0, None), 0.0)
        self.assertEqual(sc.standardised_shift(estimate, dict(NONE), 1.0, {"settlement_coupon": 0.0}), 0.0)

    def test_the_flag_arm_ignores_the_size_and_the_sized_arm_ignores_the_flag_alone(self):
        pairs = sized_pairs(coefficient=4.0)
        flag_fit = sc.fit_state_terms(pairs, regressors=("treasury_settlement_coupons",), terms=self.TERMS, interact=False,
                                      robust=False, training_pairs="direct")
        bigger = [p._replace(sizes={"settlement_coupon": 5.0 * p.sizes["settlement_coupon"], "settlement_bill": 0.0}) for p in pairs]
        again = sc.fit_state_terms(bigger, regressors=("treasury_settlement_coupons",), terms=self.TERMS, interact=False,
                                   robust=False, training_pairs="direct")
        self.assertEqual(flag_fit.effect, again.effect)
        floor = [p._replace(state=0.0) for p in pairs]
        self.assertEqual(self.fit(floor).effect, {})  # no pair carries a size on the floor: the term does not enter
        self.assertEqual(self.fit(floor).flagged["settlement_coupon"], 0)

    def test_an_unknown_state_carries_no_size_effect(self):
        pairs = sized_pairs(coefficient=4.0)
        unknown = [p._replace(state=None) for p in pairs]
        self.assertEqual(self.fit(unknown).effect, {})

    def test_the_pool_is_what_the_size_terms_leave(self):
        pairs = sized_pairs(coefficient=4.0, size=lambda i: 80.0 + 10.0 * (i % 8))
        estimate = self.fit(pairs)
        self.assertEqual(len(estimate.residuals), len(pairs))
        spread = max(estimate.residuals) - min(estimate.residuals)
        self.assertLess(spread, 2.0)  # the planted 3 to 7 scale units on the flagged pairs are gone

    def test_a_term_not_readable_at_the_lead_does_not_enter(self):
        pairs = [p._replace(flags={k: v for k, v in p.flags.items() if k != "settlement_coupon"}) for p in sized_pairs()]
        estimate = self.fit(pairs)
        self.assertEqual(estimate.effect, {})


class SizeTableTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.row = next(i for i, r in enumerate(PANEL) if i > 400 and float(r.values.get("treasury_settlement_coupons") or 0.0) > 0.0)

    def test_the_size_is_the_panel_columns_value_at_the_target_row_in_usd_billions(self):
        read = SIZES.read(1, self.row - 1)
        self.assertEqual(read["settlement_coupon"], float(PANEL[self.row].values["treasury_settlement_coupons"]))
        self.assertGreater(read["settlement_coupon"], 0.0)
        self.assertEqual(read["settlement_bill"], float(PANEL[self.row].values.get("treasury_settlement_bills") or 0.0))

    def test_the_size_agrees_with_the_flag_of_the_term_table(self):
        for row in range(300, 700):
            sized = SIZES.sizes_at(1, row)
            self.assertEqual(sized["settlement_coupon"] > 0.0, bool(TABLE_ALL.flag("settlement_coupon", 1, row)), row)
            self.assertEqual(sized["settlement_bill"] > 0.0, bool(TABLE_ALL.flag("settlement_bill", 1, row)), row)

    def test_a_size_is_not_read_beyond_lead_1(self):
        for lead in (2, 3, 4, 5):
            self.assertEqual(SIZES.read(lead, self.row - lead), {})
            self.assertEqual(SIZES.sizes_at(lead, self.row), {})

    def test_a_scheduled_size_of_a_row_not_yet_public_is_refused(self):
        with self.assertRaises(LookAheadError):
            cal.require_public(cal.TERM["settlement_coupon"], [self.row], self.row - 2, [r.date for r in PANEL])

    def test_a_later_row_moves_no_size(self):
        di = self.row - 1
        panel = list(PANEL)
        for i in range(di + 2, len(panel)):
            values = dict(panel[i].values)
            values["treasury_settlement_coupons"] = 999.0
            panel[i] = dataclasses.replace(panel[i], values=values)
        self.assertEqual(sc.SizeTable(panel).read(1, di), SIZES.read(1, di))


class SizedWalkTests(unittest.TestCase):

    DAYS = [row.date for row in PANEL if date(2024, 6, 3) <= row.date <= date(2024, 6, 14)]
    STATES = states_of(lambda i: float((i // 7) % 4))

    @classmethod
    def setUpClass(cls):
        cls.walk = sc.walk(PANEL, cls.DAYS, TABLE_ALL, cls.STATES, sc.DECOMPOSITION, sizes=SIZES, **SETTINGS)

    def test_every_arm_has_23_ordered_quantiles_at_every_lead_on_the_same_days(self):
        days = set(self.walk.forecasts[sc.ARM_A])
        self.assertTrue(days)
        for arm in sc.DECOMPOSITION:
            self.assertEqual(set(self.walk.forecasts[arm.name]), days)
            for leads in self.walk.forecasts[arm.name].values():
                for q in leads.values():
                    self.assertEqual(len(q), 23)
                    self.assertEqual(q, sorted(q))

    def test_at_leads_2_to_5_the_sized_arm_is_arm_s3_because_no_size_is_readable_there(self):
        for day, leads in self.walk.forecasts[sc.R3.name].items():
            for h in (2, 3, 4, 5):
                self.assertEqual(leads[h], self.walk.forecasts[S3.name][day][h], (day, h))

    def test_with_the_state_on_the_floor_everywhere_the_sized_arm_is_arm_s3_without_its_settlement_terms(self):
        zero = states_of(lambda i: 0.0)
        no_settlement = dataclasses.replace(S3, name="s3_no_settlement", location=tuple(t for t in S3.location if t not in sc.SIZED_TERMS))
        walk = sc.walk(PANEL, self.DAYS[:3], TABLE_ALL, zero, (no_settlement, sc.R3), sizes=SIZES, **SETTINGS)
        self.assertEqual(walk.forecasts[sc.R3.name], walk.forecasts[no_settlement.name])

    def test_a_sized_arm_without_a_size_table_is_refused(self):
        with self.assertRaisesRegex(ValueError, "size table"):
            sc.walk(PANEL, self.DAYS[:2], TABLE_ALL, self.STATES, (sc.R3,), **SETTINGS)

    def test_the_arms_that_are_not_sized_do_not_depend_on_the_size_table(self):
        again = sc.walk(PANEL, self.DAYS[:2], TABLE_ALL, self.STATES, (S1, sc.R1, sc.R2, S3), **SETTINGS)
        for arm in (S1, sc.R1, sc.R2, S3):
            for day in again.forecasts[arm.name]:
                self.assertEqual(again.forecasts[arm.name][day], self.walk.forecasts[arm.name][day], arm.name)

    def test_a_future_settlement_size_moves_no_forecast(self):
        di = index_of("2024-06-07")
        panel = list(PANEL)
        for i in range(di + 2, len(panel)):
            values = dict(panel[i].values)
            values["treasury_settlement_coupons"] = 999.0
            panel[i] = dataclasses.replace(panel[i], values=values)
        a = sc.walk(panel, [PANEL[di].date], TABLE_ALL, self.STATES, (sc.R3,), sizes=sc.SizeTable(panel), **SETTINGS)
        b = sc.walk(PANEL, [PANEL[di].date], TABLE_ALL, self.STATES, (sc.R3,), sizes=SIZES, **SETTINGS)
        self.assertEqual(a.forecasts[sc.R3.name], b.forecasts[sc.R3.name])


class MissedAnchorTests(unittest.TestCase):

    def test_a_jump_at_the_anchor_is_a_miss_of_the_band_it_was_given(self):
        spreads = [0.0] * 30 + [2.5]
        row = 30
        miss = v4.missed_anchor(spreads, row, k0=1, phi=0.5, level=0.0, source_scale=1.0, shift=0.0, factor=1.0, band=(-1.5, 1.5))
        self.assertTrue(miss)
        calm = v4.missed_anchor(spreads[:-1] + [0.4], row, k0=1, phi=0.5, level=0.0, source_scale=1.0, shift=0.0, factor=1.0,
                                band=(-1.5, 1.5))
        self.assertFalse(calm)

    def test_the_band_is_centred_on_the_model_forecast_not_on_the_level(self):
        spreads = [0.0] * 29 + [10.0, 6.0]  # persistence of 10 with phi 0.5 puts the forecast centre at 5
        self.assertFalse(v4.missed_anchor(spreads, 30, k0=1, phi=0.5, level=0.0, source_scale=1.0, shift=0.0, factor=1.0,
                                          band=(-2.0, 2.0)))
        self.assertTrue(v4.missed_anchor(spreads, 30, k0=1, phi=0.5, level=0.0, source_scale=1.0, shift=0.0, factor=1.0,
                                         band=(-0.5, 0.5)))

    def test_the_shift_and_the_factor_move_the_band(self):
        spreads = [0.0] * 30 + [3.0]
        args = dict(k0=1, phi=0.5, level=0.0, source_scale=1.0, band=(-1.0, 1.0))
        self.assertTrue(v4.missed_anchor(spreads, 30, shift=0.0, factor=1.0, **args))
        self.assertFalse(v4.missed_anchor(spreads, 30, shift=2.5, factor=1.0, **args))  # the location term expected a rise
        self.assertFalse(v4.missed_anchor(spreads, 30, shift=0.0, factor=4.0, **args))  # a wider type scale contains it


class V4Tests(unittest.TestCase):

    DAYS = [row.date for row in PANEL if date(2024, 6, 3) <= row.date <= date(2024, 6, 14)]
    STATES = states_of(lambda i: float((i // 7) % 4))

    @classmethod
    def setUpClass(cls):
        cls.mine = sc.walk(PANEL, cls.DAYS, TABLE_ALL, cls.STATES, (S3,), **SETTINGS)
        cls.v4 = v4.walk(PANEL, cls.mine, S3.name, TABLE_ALL, **SETTINGS)

    def test_the_estimates_keep_the_pairs_the_layer_needs(self):
        estimate = next(iter(self.mine.estimates.values()))[S3.name][1]
        self.assertEqual(len(estimate.origins), estimate.pairs)
        self.assertEqual(len(estimate.targets), estimate.pairs)
        self.assertEqual(len(estimate.residuals), estimate.pairs)
        self.assertTrue(all(o < t for o, t in zip(estimate.origins, estimate.targets)))

    def test_every_day_has_23_ordered_quantiles_at_every_lead(self):
        self.assertEqual(set(self.v4.forecasts), set(self.mine.forecasts[S3.name]))
        for leads in self.v4.forecasts.values():
            for q in leads.values():
                self.assertEqual(len(q), 23)
                self.assertEqual(q, sorted(q))

    def test_with_no_miss_to_feed_back_and_no_type_to_scale_v4_is_arm_s3_exactly(self):
        with mock.patch.object(scale_mod, "MISS_MIN", 10**9), mock.patch.object(scale_mod, "CAL_TYPES", ()):
            plain = v4.walk(PANEL, self.mine, S3.name, TABLE_ALL, **SETTINGS)
        self.assertEqual(plain.forecasts, self.mine.forecasts[S3.name])

    def test_v4_moves_the_location_by_arm_s3s_shift_and_scales_only_the_pool(self):
        day = self.DAYS[3]
        s3, mine = self.mine.forecasts[S3.name][day], self.v4.forecasts[day]
        for h in (1, 2, 3):
            self.assertNotEqual(mine[h], s3[h])
            median_s3, median_v4 = s3[h][11], mine[h][11]
            self.assertLess(abs(median_s3 - median_v4), 25.0)

    def test_a_future_spread_moves_no_v4_forecast(self):
        di = index_of("2024-06-07")
        panel = list(PANEL)
        for i in range(di + 1, len(panel)):
            values = dict(panel[i].values)
            values["sofr"] = float(values["iorb"]) + 40.0
            panel[i] = dataclasses.replace(panel[i], values=values)
        a_mine = sc.walk(panel, [PANEL[di].date], TABLE_ALL, self.STATES, (S3,), **SETTINGS)
        b_mine = sc.walk(PANEL, [PANEL[di].date], TABLE_ALL, self.STATES, (S3,), **SETTINGS)
        a = v4.walk(panel, a_mine, S3.name, TABLE_ALL, **SETTINGS)
        b = v4.walk(PANEL, b_mine, S3.name, TABLE_ALL, **SETTINGS)
        self.assertEqual(a.forecasts, b.forecasts)

    def test_the_type_factors_are_fitted_on_direct_pairs_and_the_guard_refuses_a_one_step_fit(self):
        with self.assertRaisesRegex(ValueError, "one-step pairs"):
            scale_mod.fit_type_factors([(1.0, None)] * 5, regressors=("quarter_end",), training_pairs="one_step")

    def test_v4_is_refused_for_an_arm_with_a_state_or_a_size(self):
        with self.assertRaisesRegex(ValueError, "no state and no sizes"):
            v4.walk(PANEL, sc.walk(PANEL, self.DAYS[:2], TABLE_ALL, self.STATES, (sc.ARMS[1],), **SETTINGS), sc.ARMS[1].name,
                    TABLE_ALL, **SETTINGS)


if __name__ == "__main__":
    unittest.main()
