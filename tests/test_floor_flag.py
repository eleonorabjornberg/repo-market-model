"""The floor flag and the pools it splits (#966; H5 step 3, 2021-23 and the residual pools; development tier).

The flag, the arms (three declared first, two added on 22 October 2026 on #941's scaled mean reversion) and their minimums are declared in `metadata/floor_flag_966.json`; `repo_model.floor_flag` is their
arithmetic. Stdlib only. What these tests pin: the ON RRP rate in force on a row is the one announced by the row's
decision instant and effective by its date (a retroactive entry is not read, a limit-only entry does not reset the rate);
the flag is on when the median of the last 60 spreads to the floor is at most 1 bp, off above, and undefined under 40
defined rows; a flag is as-of, and `check_no_future` refuses one that is not; arm (i) restricts B1's changes to the origins
with the anchor's flag and falls back to B1 under 60 changes or with no flag; arm (ii) does the same to the mean-reversion
residuals of the training pairs; arm (iii) takes B1's law when the flag is on; a change to every spread after the anchor
moves no forecast of any arm.

Recorded mutations (the new leakage guards; each run on the tests named, then restored):

* `flags`: `spreads[max(0, i - WINDOW + 1): i + 1]` replaced with `spreads[max(0, i - WINDOW + 1): i + 2]`, so a row's flag
  reads the next row's spread. `FlagTests.test_a_flag_reads_no_row_after_its_own` failed with `LookAheadError` ("the floor
  flag on ... is ..., but the panel cut at that row gives ...; the flag depended on a later row", raised by
  `check_no_future`); restored, it passes. (`test_undefined_under_forty_defined_rows` and
  `test_rows_before_the_first_rate_are_undefined` failed with `AssertionError` too.)
* `check_no_future`: `if built[i] != again:` replaced with `if False:`, so a flag that read a later row passes.
  `FlagTests.test_a_flag_that_read_the_next_row_is_refused` failed with `AssertionError` ("LookAheadError not raised");
  restored, it passes.
* `rrp_rate_percent`: `known_entries(register, datetime.combine(day, decision_time))` replaced with `register`, so an
  entry announced after the row's decision instant but effective by its date sets the rate.
  `RateTests.test_a_retroactive_entry_is_not_read` failed with `AssertionError` (2.0 != 1.0); restored, it passes.
* `flag_scaled_fit` (arm (iv), added 22 October 2026): `state = row_flags[origin]` replaced with `state = row_flags[target]`,
  so a training pair is pooled by the flag at its target row, which is after its origin. `ArmTests.test_arm_four_pools_the_standardised_residuals_by_the_origins_flag` failed with `AssertionError` (the state's 23 standardised quantiles differ from the ones built from the origins' flags); restored, it passes. (The scale's own as-of guard is `spread_mr_fhs`'s, recorded in `tests/test_spread_mr_fhs.py`; `AsOfTests.test_a_future_spread_moves_no_forecast` runs the walk with the variant.)
"""

from __future__ import annotations

import dataclasses
import unittest
from datetime import date, datetime, time, timedelta

from repo_model import floor_flag as ff
from repo_model import protocol_benchmarks as pb
from repo_model import spread_mean_reversion as smr
from repo_model import spread_mr_fhs as fhs
from repo_model.data import DailyObservation
from repo_model.policy_events import PolicyEntry
from repo_model.scoring_protocol import HORIZONS
from repo_model.splits import LookAheadError

import test_protocol_benchmarks as tpb

DECISION = time(16, 0)


def entry(entry_id, announced, effective, rate, *, kind="on_rrp", clock=time(14, 0)):
    details = {"offering_rate_percent": rate} if rate is not None else {"per_counterparty_limit_bn": 80}
    return PolicyEntry(
        entry_id, kind, "change", entry_id, datetime.combine(announced, clock), "stated", effective, "https://example.org",
        True, details,
    )


def synthetic_panel(spreads_to_floor, *, start=date(2021, 1, 4), rate=0.0):
    """Weekday rows with SOFR = the floor rate + the given spread (bp)."""

    rows, day = [], start
    for value in spreads_to_floor:
        while day.weekday() >= 5:
            day += timedelta(days=1)
        rows.append(DailyObservation(day, {"sofr": rate + value / 100.0, "iorb": rate + 0.15}))
        day += timedelta(days=1)
    return rows


REGISTER = (entry("a", date(2020, 12, 1), date(2020, 12, 2), 0.0),)


class RateTests(unittest.TestCase):

    def test_the_rate_is_the_latest_announced_and_effective(self):
        register = (entry("a", date(2021, 1, 4), date(2021, 1, 5), 1.0), entry("b", date(2021, 3, 1), date(2021, 3, 2), 2.0))
        self.assertIsNone(ff.rrp_rate_percent(register, date(2021, 1, 5) - timedelta(days=1), DECISION))
        self.assertEqual(ff.rrp_rate_percent(register, date(2021, 1, 5), DECISION), 1.0)
        self.assertEqual(ff.rrp_rate_percent(register, date(2021, 3, 1), DECISION), 1.0)
        self.assertEqual(ff.rrp_rate_percent(register, date(2021, 3, 2), DECISION), 2.0)

    def test_a_retroactive_entry_is_not_read(self):
        # announced on the 10th after the decision instant, effective on the 10th itself
        register = (
            entry("a", date(2021, 1, 4), date(2021, 1, 5), 1.0),
            entry("b", date(2021, 3, 10), date(2021, 3, 10), 2.0, clock=time(17, 0)),
        )
        self.assertEqual(ff.rrp_rate_percent(register, date(2021, 3, 10), DECISION), 1.0)
        self.assertEqual(ff.rrp_rate_percent(register, date(2021, 3, 11), DECISION), 2.0)

    def test_a_limit_only_entry_does_not_reset_the_rate(self):
        register = (entry("a", date(2021, 1, 4), date(2021, 1, 5), 1.0), entry("b", date(2021, 2, 1), date(2021, 2, 2), None))
        self.assertEqual(ff.rrp_rate_percent(register, date(2021, 2, 3), DECISION), 1.0)

    def test_other_kinds_are_not_the_rate(self):
        register = (entry("a", date(2021, 1, 4), date(2021, 1, 5), 9.0, kind="iorb_rate"),)
        self.assertIsNone(ff.rrp_rate_percent(register, date(2021, 2, 3), DECISION))

    def test_the_real_register_gives_the_floor_in_2021_23(self):
        register = ff_register()
        self.assertEqual(ff.rrp_rate_percent(register, date(2021, 9, 1), DECISION), 0.05)
        self.assertEqual(ff.rrp_rate_percent(register, date(2023, 9, 1), DECISION), 5.30)
        self.assertIsNone(ff.rrp_rate_percent(register, date(2018, 3, 21), DECISION))


def ff_register():
    from repo_model.policy_events import load_register
    return load_register()


class FlagTests(unittest.TestCase):

    def flags(self, spreads, **kw):
        return ff.flags(synthetic_panel(spreads, **kw), REGISTER, DECISION)

    def test_on_when_the_median_is_at_most_one_bp(self):
        out = self.flags([1.0] * 80)
        self.assertTrue(all(v is True for v in out[ff.MIN_ROWS - 1:]))

    def test_off_when_the_median_is_above_one_bp(self):
        out = self.flags([1.5] * 80)
        self.assertTrue(all(v is False for v in out[ff.MIN_ROWS - 1:]))

    def test_undefined_under_forty_defined_rows(self):
        out = self.flags([0.0] * 80)
        self.assertTrue(all(v is None for v in out[: ff.MIN_ROWS - 1]))
        self.assertIs(out[ff.MIN_ROWS - 1], True)

    def test_rows_before_the_first_rate_are_undefined(self):
        register = (entry("a", date(2021, 1, 4), date(2021, 3, 1), 0.0),)
        panel = synthetic_panel([0.0] * 120)
        out = ff.flags(panel, register, DECISION)
        first = next(i for i, row in enumerate(panel) if row.date >= date(2021, 3, 1))
        self.assertTrue(all(v is None for v in out[: first + ff.MIN_ROWS - 1]))
        self.assertIs(out[first + ff.MIN_ROWS - 1], True)

    def test_the_median_flips_the_flag_at_the_thirtieth_high_row(self):
        out = self.flags([0.0] * 60 + [10.0] * 30)
        self.assertIs(out[60 + 28], True)
        self.assertIs(out[60 + 29], False)

    def test_the_boundary_is_inclusive(self):
        self.assertIs(self.flags([1.0] * 60)[-1], True)
        self.assertIs(self.flags([1.0000001] * 60)[-1], False)

    def test_a_flag_reads_no_row_after_its_own(self):
        panel = synthetic_panel([0.0] * 60 + [10.0] * 30)
        built = ff.flags(panel, REGISTER, DECISION)
        ff.check_no_future(panel, built, REGISTER, DECISION, indices=range(len(panel)))

    def test_a_flag_that_read_the_next_row_is_refused(self):
        panel = synthetic_panel([0.0] * 60 + [10.0] * 30)
        built = ff.flags(panel, REGISTER, DECISION)
        leaky = built[1:] + [built[-1]]
        with self.assertRaises(LookAheadError):
            ff.check_no_future(panel, leaky, REGISTER, DECISION, indices=range(len(panel)))


def real_panel():
    panel = tpb.published_panel()["rows"]
    return panel, dict(registry=tpb.REGISTRY, decision_time=tpb.DECISION, splits=tpb.SPLITS)


def index_of(panel, day):
    return next(i for i, row in enumerate(panel) if row.date.isoformat() == day)


def with_spread(row, spread_bps):
    values = dict(row.values)
    values["sofr"] = float(values["iorb"]) + spread_bps / 100.0
    return dataclasses.replace(row, values=values)


class ArmTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = real_panel()
        cls.t = index_of(cls.panel, "2022-06-01")
        cls.anchor = pb._anchor(cls.panel, cls.t, cls.settings["registry"], cls.settings["decision_time"])
        cls.split_settings = dict(cls.settings)
        # alternate flags by row parity: both states have well over 60 changes in a two-year window
        cls.alt = [i % 2 == 0 for i in range(len(cls.panel))]

    def b1_settings(self):
        return dict(registry=self.settings["registry"], decision_time=self.settings["decision_time"])

    def test_arm_one_restricts_b1_to_origins_with_the_anchors_flag(self):
        got = ff.flag_b1_forecast(self.panel, self.t, self.alt, **self.b1_settings())
        first = pb._window_start(self.panel, self.t, pb.B1_YEARS)
        state = self.alt[self.anchor]
        last = self.panel[self.anchor].spread_bps
        for h in HORIZONS:
            changes = sorted(
                self.panel[s].spread_bps - self.panel[s - h].spread_bps
                for s in range(max(first, h), self.anchor + 1) if self.alt[s - h] == state
            )
            self.assertGreaterEqual(len(changes), ff.MIN_POOL)
            self.assertEqual(got[h], pb.empirical_quantiles(changes, last))

    def test_arm_one_with_every_origin_in_one_state_is_b1(self):
        everything = [True] * len(self.panel)
        self.assertEqual(
            ff.flag_b1_forecast(self.panel, self.t, everything, **self.b1_settings()),
            pb.b1_forecast(self.panel, self.t, **self.b1_settings()),
        )

    def test_arm_one_falls_back_to_b1_under_sixty_changes(self):
        flags = [False] * len(self.panel)
        for s in range(self.anchor - 20, self.anchor + 1):
            flags[s] = True      # the anchor is on; only 21 origins share its state
        self.assertEqual(
            ff.flag_b1_forecast(self.panel, self.t, flags, **self.b1_settings()),
            pb.b1_forecast(self.panel, self.t, **self.b1_settings()),
        )

    def test_arm_one_with_no_flag_at_the_anchor_is_b1(self):
        flags = list(self.alt)
        flags[self.anchor] = None
        self.assertEqual(
            ff.flag_b1_forecast(self.panel, self.t, flags, **self.b1_settings()),
            pb.b1_forecast(self.panel, self.t, **self.b1_settings()),
        )

    def test_arm_two_pools_by_the_origins_flag(self):
        fit = ff.flag_fit(self.panel, self.t, self.alt, **self.settings)
        base = smr.fit(self.panel, self.t, **self.settings)
        self.assertEqual(fit.base, base)
        for h in HORIZONS:
            self.assertEqual(set(fit.own_pool[h]), {True, False})
            self.assertEqual(fit.sizes[h][True] + fit.sizes[h][False], base.pairs[h])

    def test_arm_two_with_every_origin_in_one_state_is_the_base(self):
        everything = [True] * len(self.panel)
        fit = ff.flag_fit(self.panel, self.t, everything, **self.settings)
        for h in HORIZONS:
            self.assertEqual(fit.residuals[h][True], fit.base.residuals[h])
            self.assertEqual(fit.own_pool[h], (True,))
            self.assertEqual(fit.sizes[h][False], 0)
            self.assertEqual(fit.residuals[h][False], fit.base.residuals[h])   # the empty pool falls back
        self.assertEqual(
            ff.flag_forecast(self.panel, self.t, fit, everything, **self.settings),
            smr.forecast(self.panel, self.t, fit.base, **self.settings),
        )

    def test_arm_two_with_no_flag_at_the_anchor_is_the_base(self):
        flags = list(self.alt)
        flags[self.anchor] = None
        fit = ff.flag_fit(self.panel, self.t, flags, **self.settings)
        self.assertEqual(
            ff.flag_forecast(self.panel, self.t, fit, flags, **self.settings),
            smr.forecast(self.panel, self.t, fit.base, **self.settings),
        )

    def test_a_pair_whose_origin_has_no_flag_joins_no_pool(self):
        flags = list(self.alt)
        base = smr.fit(self.panel, self.t, **self.settings)
        for s in range(0, self.anchor - 10):
            flags[s] = None
        fit = ff.flag_fit(self.panel, self.t, flags, **self.settings)
        for h in HORIZONS:
            self.assertLess(fit.sizes[h][True] + fit.sizes[h][False], base.pairs[h])

    def test_arm_four_pools_the_standardised_residuals_by_the_origins_flag(self):
        variant = fhs.VARIANTS[0]
        self.assertEqual(variant.name, ff.FHS_NAME)
        fit = ff.flag_scaled_fit(self.panel, self.t, self.alt, variant, **self.settings)
        levels = smr.ordinary_levels(self.panel, self.settings["splits"])
        rows = smr.training_rows(self.panel, self.t, self.anchor, lag=self.t - self.anchor, levels=levels)
        reader = fhs.ScaleReader([r.spread_bps for r in self.panel[: self.anchor + 1]], variant)
        for h in HORIZONS:
            k = h + self.t - self.anchor
            want = {True: [], False: []}
            for origin, target in rows[h]:
                scale = reader.at(origin)
                if scale is None:
                    continue
                raw = (self.panel[target].spread_bps - levels[origin]) - fit.base.phi**k * (self.panel[origin].spread_bps - levels[origin])
                want[self.alt[origin]].append(raw / scale)
            for state in (True, False):
                self.assertEqual(fit.sizes[h][state], len(want[state]))
                self.assertGreaterEqual(len(want[state]), ff.MIN_POOL)
                self.assertEqual(fit.standardised[h][state], pb.empirical_quantiles(sorted(want[state])))
            self.assertEqual(set(fit.own_pool[h]), {True, False})

    def test_arm_four_with_every_origin_in_one_state_is_the_scaled_model(self):
        variant = fhs.VARIANTS[0]
        everything = [True] * len(self.panel)
        fit = ff.flag_scaled_fit(self.panel, self.t, everything, variant, **self.settings)
        plain = fhs.fit(self.panel, self.t, [variant], **self.settings)[variant.name]
        for h in HORIZONS:
            self.assertEqual(fit.standardised[h][True], plain.standardised[h])
            self.assertEqual(fit.standardised[h][False], plain.standardised[h])   # the empty pool falls back
        self.assertEqual(
            ff.flag_scaled_forecast(self.panel, self.t, fit, everything, variant, **self.settings),
            fhs.forecast(self.panel, self.t, plain, fit.base, variant, **self.settings),
        )

    def test_arm_four_with_no_flag_at_the_anchor_is_the_scaled_model(self):
        variant = fhs.VARIANTS[0]
        flags = list(self.alt)
        flags[self.anchor] = None
        fit = ff.flag_scaled_fit(self.panel, self.t, flags, variant, **self.settings)
        plain = fhs.fit(self.panel, self.t, [variant], **self.settings)[variant.name]
        self.assertEqual(
            ff.flag_scaled_forecast(self.panel, self.t, fit, flags, variant, **self.settings),
            fhs.forecast(self.panel, self.t, plain, fit.base, variant, **self.settings),
        )

    def test_arm_four_uses_the_pool_of_the_anchors_state(self):
        variant = fhs.VARIANTS[0]
        fit = ff.flag_scaled_fit(self.panel, self.t, self.alt, variant, **self.settings)
        got = ff.flag_scaled_forecast(self.panel, self.t, fit, self.alt, variant, **self.settings)
        other = list(self.alt)
        other[self.anchor] = not self.alt[self.anchor]
        flipped = ff.flag_scaled_forecast(self.panel, self.t, fit, other, variant, **self.settings)
        self.assertNotEqual(got, flipped)

    def test_arm_five_is_b1_when_the_flag_is_on_and_the_scaled_model_otherwise(self):
        scaled = {h: [0.0] * 23 for h in HORIZONS}
        b1 = {h: [1.0] * 23 for h in HORIZONS}
        self.assertEqual(ff.two_part(scaled, b1, True), b1)
        self.assertEqual(ff.two_part(scaled, b1, False), scaled)

    def test_arm_three_is_b1_when_the_flag_is_on(self):
        law = {h: [0.0] * 23 for h in HORIZONS}
        b1 = {h: [1.0] * 23 for h in HORIZONS}
        self.assertEqual(ff.two_part(law, b1, True), b1)
        self.assertEqual(ff.two_part(law, b1, False), law)
        self.assertEqual(ff.two_part(law, b1, None), law)


class AsOfTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = real_panel()
        cls.register = ff_register()
        cls.days = [row.date for row in cls.panel if row.date.isoformat() >= "2021-06-01"][:60]

    def run_walk(self, panel):
        row_flags = ff.flags(panel, self.register, tpb.DECISION)
        return ff.walk(panel, self.days, row_flags, variant=fhs.VARIANTS[0], **self.settings)

    def test_the_flags_of_the_real_panel_are_as_of(self):
        built = ff.flags(self.panel, self.register, tpb.DECISION)
        ff.check_no_future(
            self.panel, built, self.register, tpb.DECISION, indices=range(1000, len(self.panel), 97)
        )

    def test_a_future_spread_moves_no_forecast(self):
        last = self.days[-1]
        t = index_of(self.panel, last.isoformat())
        anchor = pb._anchor(self.panel, t, self.settings["registry"], self.settings["decision_time"])
        shocked = list(self.panel)
        for i in range(anchor + 1, len(shocked)):
            shocked[i] = with_spread(shocked[i], 250.0 + i)
        base, moved = self.run_walk(self.panel), self.run_walk(shocked)
        for name in base.forecasts:
            self.assertEqual(base.forecasts[name][last], moved.forecasts[name][last])
        self.assertEqual(base.anchor_flag[last], moved.anchor_flag[last])


class WalkTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = real_panel()
        cls.days = [row.date for row in cls.panel if row.date.isoformat() >= "2021-06-01"][:50]
        row_flags = ff.flags(cls.panel, ff_register(), tpb.DECISION)
        cls.walk = ff.walk(cls.panel, cls.days, row_flags, variant=fhs.VARIANTS[0], **cls.settings)
        cls.plain = ff.walk(cls.panel, cls.days, row_flags, **cls.settings)
        cls.mr = smr.walk(cls.panel, cls.days, **cls.settings)
        cls.scaled = fhs.walk(cls.panel, cls.days, fhs.VARIANTS[:1], **cls.settings)

    def test_the_base_series_is_spread_mr_level10_exactly(self):
        self.assertEqual(self.walk.forecasts[ff.BASE_MR], self.mr.forecasts)

    def test_every_series_covers_the_same_days(self):
        days = set(self.walk.forecasts[ff.BASE_MR])
        self.assertEqual(set(self.walk.forecasts[ff.ARM_B1]), days)
        self.assertEqual(set(self.walk.forecasts[ff.ARM_MR]), days)

    def test_the_scaled_series_is_the_941_variant_exactly(self):
        self.assertEqual(self.walk.forecasts[ff.FHS_NAME], self.scaled.forecasts[ff.FHS_NAME])
        self.assertEqual(self.walk.forecasts[ff.BASE_MR], self.scaled.forecasts[fhs.REFERENCE])

    def test_the_scaled_arms_cover_the_same_days(self):
        days = set(self.walk.forecasts[ff.BASE_MR])
        for name in (ff.FHS_NAME, ff.ARM_FHS, ff.ARM_TWO_FHS):
            self.assertEqual(set(self.walk.forecasts[name]), days)

    def test_the_two_part_series_takes_b1_on_the_flag_and_the_scaled_model_off_it(self):
        for day, flag in self.walk.anchor_flag.items():
            law = self.walk.forecasts[ff.ARM_TWO_FHS][day]
            if flag:
                b1 = pb.b1_forecast(self.panel, next(i for i, r in enumerate(self.panel) if r.date == day),
                                    registry=self.settings["registry"], decision_time=self.settings["decision_time"])
                self.assertEqual(law, b1)
            else:
                self.assertEqual(law, self.walk.forecasts[ff.FHS_NAME][day])

    def test_without_a_variant_the_walk_is_the_declared_three_series(self):
        self.assertEqual(set(self.plain.forecasts), {ff.BASE_MR, ff.ARM_B1, ff.ARM_MR})
        for name in (ff.BASE_MR, ff.ARM_B1, ff.ARM_MR):
            self.assertEqual(self.plain.forecasts[name], self.walk.forecasts[name])

    def test_the_fit_is_renewed_on_the_first_day_and_every_21st(self):
        self.assertEqual(sorted(self.walk.fits), [self.days[0], self.days[21], self.days[42]])

    def test_quantiles_do_not_cross(self):
        for series in self.walk.forecasts.values():
            for forecast in series.values():
                for h in HORIZONS:
                    self.assertEqual(forecast[h], sorted(forecast[h]))


if __name__ == "__main__":
    unittest.main()
