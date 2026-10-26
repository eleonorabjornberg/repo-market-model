"""Mean reversion with volatility-scaled residuals (filtered historical simulation; #941, H5 step 3, development tier).

`metadata/fhs_scale_941.json` is the declaration; `repo_model.spread_mr_fhs` is its arithmetic. What these tests pin: the
scale on hand cases (median absolute change, the floor, the standard deviation), that the scale at a row reads only rows
at or before it, that the pool is standardised at each pair's own origin and rescaled at the anchor, that the scaled
pool reduces to the unscaled one when the scale is constant, that a future spread moves no forecast, and that the walk
refits as the base model does.

Recorded mutation (the new availability guard; run on `test_a_future_spread_moves_no_forecast`, then restored):

* `scale_rows`: `range(row - window, row + 1)` replaced with `range(row - window + 1, row + 2)`, so the scale at the anchor
  reads the row after it, which was not public at the decision instant. `test_a_future_spread_moves_no_forecast` errored with
  `LookAheadError` ("the scale of spread_mr_fhs_mad20_f0.5 for 2022-03-07 reads 2022-03-07, after 2022-03-04, the last row
  public at the decision instant", raised by `protocol_benchmarks._require_public`); restored, it passes.
  `test_a_scale_that_reads_a_row_after_the_anchor_is_refused` patches `scale_rows` with that same mutated range, so it
  pins the guard's response to a patched reader and cannot itself tell the source mutation.

Recorded mutation (standardised at the pair's own origin, not at the anchor; run on
`test_the_pool_is_standardised_at_each_pairs_own_origin`, then restored):

* `fit`: `scale = reader.at(origin)` replaced with `scale = reader.at(anchor)`. The test failed with `AssertionError`
  ("-13.34 != -4.0 within 9 places": the standardised quantiles differed from the hand reading); restored, it passes.
"""

from __future__ import annotations

import dataclasses
import json
import math
import statistics
import unittest
import unittest.mock
from pathlib import Path

from repo_model import protocol_benchmarks as pb
from repo_model import scoring_protocol as sp
from repo_model import spread_mean_reversion as smr
from repo_model import spread_mr_fhs as fhs
from repo_model.splits import LookAheadError

import test_protocol_benchmarks as tpb

ROOT = Path(__file__).resolve().parent.parent


def panel_and_settings():
    panel = tpb.published_panel()["rows"]
    return panel, dict(registry=tpb.REGISTRY, decision_time=tpb.DECISION, splits=tpb.SPLITS)


def decision_index(panel, day):
    return next(i for i, row in enumerate(panel) if row.date.isoformat() == day)


def with_spread(row, spread_bps):
    values = dict(row.values)
    values["sofr"] = float(values["iorb"]) + spread_bps / 100.0
    return dataclasses.replace(row, values=values)


class ScaleTests(unittest.TestCase):

    SPREADS = [0.0, 1.0, 1.0, 4.0, 2.0, 2.0, 2.5, 10.0]

    def reader(self, estimator="mad", window=4, floor=0.5):
        return fhs.ScaleReader(self.SPREADS, fhs.Variant("v", estimator, window, floor))

    def test_the_median_absolute_change_over_the_window_is_scaled_by_1_4826(self):
        # row 5: window 4 reads rows 1..5, changes 0, 3, -2, 0: |.| = 0, 3, 2, 0, median 1.0
        self.assertAlmostEqual(self.reader().at(5), 1.4826 * 1.0)

    def test_the_standard_deviation_variant_uses_the_sample_sd_of_the_same_changes(self):
        self.assertAlmostEqual(self.reader("sd").at(5), statistics.stdev([0.0, 3.0, -2.0, 0.0]))

    def test_the_floor_binds_when_the_window_is_calm(self):
        # row 2: window 4 would need row -2; use window 2: rows 0..2, changes 1, 0, median 0.5 -> 0.7413
        self.assertAlmostEqual(self.reader(window=2, floor=0.5).at(2), 1.4826 * 0.5)
        # row 5 with window 2: rows 3..5, changes -2... use a calm stretch
        calm = fhs.ScaleReader([5.0] * 10, fhs.Variant("v", "mad", 4, 0.5))
        self.assertEqual(calm.at(6), 0.5)
        self.assertEqual(fhs.ScaleReader([5.0] * 10, fhs.Variant("v", "mad", 4, 1.0)).at(6), 1.0)

    def test_a_row_without_a_full_window_has_no_scale(self):
        self.assertIsNone(self.reader(window=4).at(3))
        self.assertIsNotNone(self.reader(window=4).at(4))

    def test_the_scale_reads_rows_up_to_its_own_and_no_further(self):
        self.assertEqual(list(fhs.scale_rows(10, 4)), [6, 7, 8, 9, 10])

    def test_the_scale_at_a_row_ignores_every_later_spread(self):
        later = list(self.SPREADS)
        later[6] = 99.0
        later[7] = -99.0
        a = fhs.ScaleReader(self.SPREADS, fhs.Variant("v", "mad", 4, 0.5)).at(5)
        b = fhs.ScaleReader(later, fhs.Variant("v", "mad", 4, 0.5)).at(5)
        self.assertEqual(a, b)

    def test_an_estimator_that_is_not_declared_is_refused(self):
        with self.assertRaises(ValueError):
            fhs.Variant("v", "iqr", 20, 0.5)

    def test_a_window_below_two_or_a_floor_that_is_not_positive_is_refused(self):
        with self.assertRaises(ValueError):
            fhs.Variant("v", "mad", 1, 0.5)
        with self.assertRaises(ValueError):
            fhs.Variant("v", "mad", 20, 0.0)


class DeclarationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.declaration = json.loads((ROOT / "metadata" / "fhs_scale_941.json").read_text(encoding="utf-8"))

    def test_the_declared_variants_are_the_module_s(self):
        listed = self.declaration["variants"]["listed_in_full"]
        self.assertEqual(len(listed), self.declaration["variants"]["count"])
        self.assertEqual(
            [(v["name"], v["estimator"], v["window_rows"], v["floor_bp"]) for v in listed],
            [(v.name, v.estimator, v.window, v.floor) for v in fhs.VARIANTS],
        )

    def test_the_declared_constants_are_the_module_s(self):
        scale = self.declaration["scale"]
        self.assertEqual(scale["window_rows"], 20)
        self.assertEqual(scale["floor_bp"], 0.5)
        self.assertEqual(fhs.MAD_CONSTANT, 1.4826)

    def test_the_declaration_ends_where_the_scoring_does(self):
        self.assertEqual(self.declaration["limits"]["last_day"], "2025-12-31")


class FitTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = panel_and_settings()
        cls.t = decision_index(cls.panel, "2022-03-07")
        cls.anchor = pb._anchor(cls.panel, cls.t, cls.settings["registry"], cls.settings["decision_time"])
        cls.variant = fhs.VARIANTS[0]

    def test_the_pool_is_standardised_at_each_pairs_own_origin(self):
        levels = smr.ordinary_levels(self.panel, self.settings["splits"])
        base = smr.fit(self.panel, self.t, **self.settings, levels=levels)
        fitted = fhs.fit(self.panel, self.t, [self.variant], base=base, **self.settings, levels=levels)
        rows = smr.training_rows(self.panel, self.t, self.anchor, lag=self.t - self.anchor, levels=levels)
        spreads = [row.spread_bps for row in self.panel]
        reader = fhs.ScaleReader(spreads, self.variant)
        for h in sp.HORIZONS:
            k = h + (self.t - self.anchor)
            pool = []
            for origin, target in rows[h]:
                scale = reader.at(origin)
                if scale is None:
                    continue
                raw = (spreads[target] - levels[origin]) - base.phi**k * (spreads[origin] - levels[origin])
                pool.append(raw / scale)
            expected = pb.empirical_quantiles(sorted(pool))
            got = fitted[self.variant.name].standardised[h]
            self.assertEqual(len(got), len(sp.GRID))
            for a, b in zip(got, expected):
                self.assertAlmostEqual(a, b, places=9)

    def test_the_forecast_rescales_the_pool_by_the_scale_at_the_anchor(self):
        levels = smr.ordinary_levels(self.panel, self.settings["splits"])
        base = smr.fit(self.panel, self.t, **self.settings, levels=levels)
        fitted = fhs.fit(self.panel, self.t, [self.variant], base=base, **self.settings, levels=levels)
        out = fhs.forecast(self.panel, self.t, fitted[self.variant.name], base, self.variant, **self.settings, levels=levels)
        scale = fhs.ScaleReader([row.spread_bps for row in self.panel], self.variant).at(self.anchor)
        lag = self.t - self.anchor
        for h in sp.HORIZONS:
            centre = levels[self.anchor] + base.phi ** (h + lag) * (self.panel[self.anchor].spread_bps - levels[self.anchor])
            for q, std in zip(out[h], fitted[self.variant.name].standardised[h]):
                self.assertAlmostEqual(q, centre + scale * std, places=9)

    def test_a_constant_scale_gives_the_unscaled_forecast(self):
        # a floor far above every scale makes the scale the floor everywhere: standardise then rescale is the identity
        flat = fhs.Variant("flat", "mad", 20, 1000.0)
        levels = smr.ordinary_levels(self.panel, self.settings["splits"])
        base = smr.fit(self.panel, self.t, **self.settings, levels=levels)
        fitted = fhs.fit(self.panel, self.t, [flat], base=base, **self.settings, levels=levels)
        scaled = fhs.forecast(self.panel, self.t, fitted["flat"], base, flat, **self.settings, levels=levels)
        plain = smr.forecast(self.panel, self.t, base, **self.settings, levels=levels)
        for h in sp.HORIZONS:
            for a, b in zip(scaled[h], plain[h]):
                self.assertAlmostEqual(a, b, places=7)

    def test_a_calm_anchor_narrows_and_a_wild_anchor_widens_the_forecast(self):
        calm = [with_spread(row, 1.0) if self.t - 40 <= i <= self.anchor else row for i, row in enumerate(self.panel)]
        wild = [
            with_spread(row, 1.0 + (-1) ** i * 12.0) if self.t - 40 <= i <= self.anchor else row
            for i, row in enumerate(self.panel)
        ]

        def width(panel):
            levels = smr.ordinary_levels(panel, self.settings["splits"])
            base = smr.fit(panel, self.t, **self.settings, levels=levels)
            fitted = fhs.fit(panel, self.t, [self.variant], base=base, **self.settings, levels=levels)
            out = fhs.forecast(panel, self.t, fitted[self.variant.name], base, self.variant, **self.settings, levels=levels)
            return out[1][-1] - out[1][0]

        self.assertLess(width(calm), width(wild))

    def test_a_future_spread_moves_no_forecast(self):
        shocked = list(self.panel)
        for i in range(self.anchor + 1, len(shocked)):
            shocked[i] = with_spread(shocked[i], 250.0 + i)

        def forecast(panel):
            levels = smr.ordinary_levels(panel, self.settings["splits"])
            base = smr.fit(panel, self.t, **self.settings, levels=levels)
            fitted = fhs.fit(panel, self.t, [self.variant], base=base, **self.settings, levels=levels)
            return fhs.forecast(panel, self.t, fitted[self.variant.name], base, self.variant, **self.settings, levels=levels)

        self.assertEqual(forecast(self.panel), forecast(shocked))

    def test_the_anchor_spread_moves_the_forecast(self):
        shocked = list(self.panel)
        shocked[self.anchor] = with_spread(shocked[self.anchor], self.panel[self.anchor].spread_bps + 30.0)

        def forecast(panel):
            levels = smr.ordinary_levels(panel, self.settings["splits"])
            base = smr.fit(panel, self.t, **self.settings, levels=levels)
            fitted = fhs.fit(panel, self.t, [self.variant], base=base, **self.settings, levels=levels)
            return fhs.forecast(panel, self.t, fitted[self.variant.name], base, self.variant, **self.settings, levels=levels)

        self.assertNotEqual(forecast(self.panel)[1], forecast(shocked)[1])

    def test_a_scale_that_reads_a_row_after_the_anchor_is_refused(self):
        with unittest.mock.patch.object(fhs, "scale_rows", lambda row, window: range(row - window + 1, row + 2)):
            with self.assertRaises(LookAheadError):
                fhs.fit(self.panel, self.t, [self.variant], **self.settings)

    def test_a_forecast_with_too_little_history_is_refused(self):
        with self.assertRaises(smr.InsufficientHistory):
            fhs.fit(self.panel, 20, [self.variant], **self.settings)


class WalkTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.panel, cls.settings = panel_and_settings()
        cls.days = [row.date for row in cls.panel if row.date.isoformat() >= "2021-01-04"][:50]
        cls.walk = fhs.walk(cls.panel, cls.days, fhs.VARIANTS, **cls.settings)

    def test_the_reference_is_the_base_walk_exactly(self):
        base = smr.walk(self.panel, self.days, **self.settings)
        self.assertEqual(self.walk.forecasts[fhs.REFERENCE], base.forecasts)

    def test_every_variant_has_every_day_five_leads_of_the_grid(self):
        for variant in fhs.VARIANTS:
            forecasts = self.walk.forecasts[variant.name]
            self.assertEqual(set(forecasts), set(self.walk.forecasts[fhs.REFERENCE]))
            for leads in forecasts.values():
                self.assertEqual(set(leads), set(sp.HORIZONS))
                for quantiles in leads.values():
                    self.assertEqual(len(quantiles), len(sp.GRID))
                    self.assertEqual(quantiles, sorted(quantiles))

    def test_the_fit_is_renewed_on_the_first_day_and_every_21st(self):
        self.assertEqual(sorted(self.walk.fits), [self.days[0], self.days[21], self.days[42]])

    def test_the_variants_differ_from_the_reference(self):
        day = self.days[10]
        self.assertNotEqual(self.walk.forecasts[fhs.VARIANTS[0].name][day][1], self.walk.forecasts[fhs.REFERENCE][day][1])

    def test_a_guard_trip_before_the_first_fit_is_raised_not_skipped(self):
        def tripped(*args, **kwargs):
            raise LookAheadError("a read after the decision instant")

        with unittest.mock.patch.object(smr, "fit", tripped):
            with self.assertRaises(LookAheadError):
                fhs.walk(self.panel, self.days[:3], fhs.VARIANTS, **self.settings)

    def test_early_days_without_history_are_listed_not_forecast(self):
        early = fhs.walk(self.panel, [row.date for row in self.panel[:30]], fhs.VARIANTS, **self.settings)
        self.assertEqual(early.forecasts[fhs.REFERENCE], {})
        self.assertEqual(len(early.skipped), 30)


if __name__ == "__main__":
    unittest.main()
