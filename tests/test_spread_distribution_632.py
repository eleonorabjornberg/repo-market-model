"""The spread-level distribution forecast (#632): a gradient-boosted quantile regression of `spread_bps`, read as P(spread > tau).

`ml.pressure_spread_distribution_exceedance` forecasts the spread at the scored day as a distribution, one gradient-boosted
quantile regression per level of `PRESSURE_SPREAD_DISTRIBUTION_SETTINGS["quantile_grid"]`, and reads the exceedance of a
threshold off the fitted law (`1 - F(floor(tau) + 0.5)`, the whole-basis-point event). Two structures:

* `risk_date` (a): fitted and served on the risk dates only, as the risk-date passers are; a day that is not a risk date is
  exactly 0, with no law;
* `two_part` (b): the same risk-date part, and on a day that is not a risk date a second spread-level model fitted on every
  training day, on `EVERY_DAY_COMPONENT_INPUTS`: a non-zero, ranked forecast by construction.

Recorded mutations (the model reads only what the as-of rule admits and adds no guard of its own, so these are the
behaviours the measurement rests on):

* `pressure_spread_distribution_exceedance`, the crossing fix `matrix.sort(axis=1)` in `_gbm_quantile_matrix` removed (a day's
  quantiles are no longer ordered): `test_a_days_quantiles_are_ordered` fails with `AssertionError`.
* `pressure_spread_distribution_exceedance`, in the every-day branch, `if day in member_set: continue` removed (the every-day
  part overwrites the risk-date part on a risk date): `test_a_risk_date_keeps_the_risk_date_parts_forecast` fails with
  `AssertionError`.
* `pressure_spread_distribution_exceedance`, in the every-day branch, `component_xs, component_spreads` cut to the first
  `len(xs)` pairs (the every-day part is fitted on as many days as the risk-date part has):
  `test_the_every_day_part_is_fitted_on_every_training_day` fails with `AssertionError`.
"""

from __future__ import annotations

import math
import unittest
from datetime import time
from types import MappingProxyType
from unittest import mock

import test_ml
from test_ml import (
    _PRESSURE_CALENDAR,
    _PRESSURE_REGISTRY,
    _every_day_frame,
    _is_risk,
    _pressure_splits,
    require_extra,
)

from repo_model import contract, measurement_fields, ml


class SpreadDistributionTests(unittest.TestCase):
    def setUp(self):
        require_extra(self)
        self.rows = _every_day_frame()
        self.features = _PRESSURE_CALENDAR + ml.EVERY_DAY_COMPONENT_INPUTS[1:]
        self.splits = _pressure_splits()

    def predict(self, scored, structure="risk_date", **options):
        fields = dict(measurement_fields.COLUMN_FIELDS)
        patched = mock.patch.multiple(
            contract,
            FEATURE_FIELDS=MappingProxyType({**contract.FEATURE_FIELDS, **fields}),
            FEATURE_SOURCES=MappingProxyType(
                {
                    **contract.FEATURE_SOURCES,
                    **{c: tuple(sorted({s for s, _f in pairs})) for c, pairs in fields.items()},
                }
            ),
        )
        with patched:
            rule = ml.InformationRule(_PRESSURE_REGISTRY, self.features, decision_time=time(16, 0))
            info = rule.information_set([r.date for r in self.rows], scored)
            observation = rule.observation(self.rows, info)
            record = []
            predictor = ml.pressure_spread_distribution_exceedance(
                _PRESSURE_CALENDAR, self.splits, 20, structure=structure, record=record, **options
            )
            curves = predictor(self.rows[:scored], (observation,), (5.0, 10.0), information=rule)
        return curves, record

    def days(self, risk, start=90):
        return [k for k in range(start, len(self.rows) - 1) if _is_risk(self.rows[k]) is risk]

    def test_the_exceedance_is_read_off_the_fitted_quantile_law(self):
        scored = self.days(True)[0]
        curves, record = self.predict(scored)
        part, quantiles = record[0]
        self.assertEqual(part, "risk_date")
        grid = ml.PRESSURE_SPREAD_DISTRIBUTION_SETTINGS["quantile_grid"]
        self.assertEqual(len(quantiles), len(grid))
        expected = ml.exceedance_from_quantiles(quantiles, grid, (5.0, 10.0))
        self.assertEqual(tuple(curves.curves[0]), tuple(expected))

    def test_the_reading_is_the_linear_quantile_regressions(self):
        grid = ml.PRESSURE_QUANTILE_SETTINGS["quantile_grid"]
        quantiles = [-3.0 + 0.5 * k for k in range(len(grid))]
        read = ml.exceedance_from_quantiles(quantiles, grid, (5.0, 10.0, 2.0))
        self.assertTrue(all(0.0 <= value <= 1.0 for value in read))
        self.assertGreaterEqual(read[2], read[0])
        self.assertGreaterEqual(read[0], read[1])
        # the whole-basis-point event: tau = 5 reads F(5.5); a spread on the cut is not above it
        below = ml.exceedance_from_quantiles(quantiles, grid, (5.4, 5.0))
        self.assertEqual(below[0], below[1])

    def test_a_days_quantiles_are_ordered(self):
        import numpy

        # noisy, heteroscedastic pairs: the per-level fits cross on most served rows until the crossing fix sorts them
        rng = numpy.random.default_rng(0)
        x = rng.normal(size=(60, 3))
        y = x[:, 0] + rng.normal(size=60) * (1.0 + numpy.abs(x[:, 1]))
        served = rng.normal(size=(40, 3))
        matrix = ml._gbm_quantile_matrix(x.tolist(), y.tolist(), served.tolist())
        self.assertEqual(matrix.shape, (40, len(ml.PRESSURE_SPREAD_DISTRIBUTION_SETTINGS["quantile_grid"])))
        self.assertTrue((numpy.diff(matrix, axis=1) >= 0).all())
        for scored in self.days(True)[:2]:
            quantiles = self.predict(scored)[1][0][1]
            self.assertEqual(list(quantiles), sorted(quantiles))

    def test_the_curve_is_non_increasing_in_tau_and_a_probability(self):
        for scored in self.days(True)[:4] + self.days(False)[:2]:
            for structure in ("risk_date", "two_part"):
                curve = self.predict(scored, structure)[0].curves[0]
                self.assertTrue(all(0.0 <= value <= 1.0 for value in curve))
                self.assertGreaterEqual(curve[0], curve[1])

    def test_a_day_that_is_not_a_risk_date_is_exactly_zero_in_the_risk_date_structure(self):
        scored = self.days(False)[0]
        curves, record = self.predict(scored)
        self.assertEqual(tuple(curves.curves[0]), (0.0, 0.0))
        self.assertEqual(record, [(None, None)])

    def test_the_two_part_structure_gives_a_day_that_is_not_a_risk_date_a_law(self):
        scored = self.days(False)[0]
        curves, record = self.predict(scored, "two_part")
        part, quantiles = record[0]
        self.assertEqual(part, "every_day")
        self.assertEqual(len(quantiles), len(ml.PRESSURE_SPREAD_DISTRIBUTION_SETTINGS["quantile_grid"]))
        self.assertGreater(curves.curves[0][0], 0.0)

    def test_a_risk_date_keeps_the_risk_date_parts_forecast(self):
        for scored in self.days(True)[:3]:
            one, record_one = self.predict(scored)
            two, record_two = self.predict(scored, "two_part")
            self.assertEqual(one.curves, two.curves)
            self.assertEqual(record_one, record_two)

    def test_the_every_day_part_is_fitted_on_every_training_day(self):
        scored = self.days(False)[0]
        settings = self.predict(scored, "two_part")[0].model_settings
        self.assertGreater(settings["every_day_training_pairs"], 3 * settings["risk_date_training_pairs"])

    def test_the_every_day_part_reads_the_every_day_inputs_through_the_information_rule(self):
        scored = self.days(False)[0]
        read = self.predict(scored, "two_part")[0].features_read
        self.assertTrue({"sofr_p75_iorb_bps", "sofr_p99_iorb_bps"} <= set(read))

    def test_a_day_whose_every_day_inputs_are_not_public_is_left_at_zero(self):
        scored = self.days(False)[0]
        for k in range(scored - 4, scored + 1):
            self.rows[k] = test_ml.DailyObservation(self.rows[k].date, {**self.rows[k].values, "sofr_p99_iorb_bps": None})
        curves, record = self.predict(scored, "two_part")
        self.assertEqual(tuple(curves.curves[0]), (0.0, 0.0))
        self.assertEqual(record, [(None, None)])

    def test_the_fit_does_not_depend_on_a_later_row(self):
        scored = self.days(True)[0]
        first = self.predict(scored)[0].curves
        for k in range(scored + 1, len(self.rows)):
            self.rows[k] = test_ml.DailyObservation(self.rows[k].date, {**self.rows[k].values, "spread_bps": 99.0})
        self.assertEqual(first, self.predict(scored)[0].curves)

    def test_a_risk_date_without_a_training_pair_is_refused_and_the_inputs_are_checked(self):
        predictor = ml.pressure_spread_distribution_exceedance(_PRESSURE_CALENDAR, self.splits, 20)
        with self.assertRaises(ValueError):
            predictor(self.rows[:90], (self.rows[91],), (5.0,))  # no information rule
        with self.assertRaises(ValueError):
            ml.pressure_spread_distribution_exceedance(_PRESSURE_CALENDAR, self.splits, 20, structure="nope")
        with self.assertRaises(ValueError):
            ml.pressure_spread_distribution_exceedance(_PRESSURE_CALENDAR, self.splits, 0)

    def test_the_settings_are_published_with_the_forecast(self):
        scored = self.days(True)[0]
        settings = self.predict(scored, "two_part")[0].model_settings
        self.assertEqual(settings["estimator"], "HistGradientBoostingRegressor")
        self.assertEqual(settings["loss"], "quantile")
        self.assertEqual(settings["structure"], "two_part")
        self.assertEqual(tuple(settings["quantile_grid"]), ml.PRESSURE_SPREAD_DISTRIBUTION_SETTINGS["quantile_grid"])

    def test_the_grid_reaches_the_tail_the_threshold_lives_in(self):
        grid = ml.PRESSURE_SPREAD_DISTRIBUTION_SETTINGS["quantile_grid"]
        self.assertEqual(list(grid), sorted(grid))
        self.assertGreaterEqual(grid[-1], 0.99)
        self.assertTrue(math.isclose(grid[len(grid) // 2], 0.5))


if __name__ == "__main__":
    unittest.main()
