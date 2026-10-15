"""The spread distribution at the scoring protocol's grid (#634, H5): the model's `grid` option.

`ml.pressure_spread_distribution_exceedance` forecast the spread at 13 levels (#632). Scoring protocol v1 (section 3)
scores 23 levels, so the model takes the grid as an option whose default is the 13-level grid, unchanged.

Recorded mutations (the model adds no leakage guard of its own; these are the behaviours the measurement rests on):

* `_gbm_quantile_matrix`, `for level in grid:` replaced by `for level in settings["quantile_grid"]:` (the option is
  ignored): `test_the_matrix_has_one_column_per_level_of_the_grid_it_is_given` fails with `AssertionError`.
* `pressure_spread_distribution_exceedance`, `_gbm_quantile_matrix(xs, risk_spreads, served, grid)` called without the
  grid (the risk-date part ignores the option): `test_the_recorded_laws_are_on_the_grid_the_predictor_is_given` fails
  with `AssertionError`.
"""

from __future__ import annotations

import random
import unittest
from datetime import time
from types import MappingProxyType
from unittest import mock

from test_ml import (
    _PRESSURE_CALENDAR,
    _PRESSURE_REGISTRY,
    _every_day_frame,
    _is_risk,
    _pressure_splits,
    require_extra,
)

from repo_model import contract, measurement_fields, ml
from repo_model.scoring_protocol import GRID


class GridOptionTests(unittest.TestCase):
    def setUp(self):
        require_extra(self)
        self.rows = _every_day_frame()
        self.features = _PRESSURE_CALENDAR + ml.EVERY_DAY_COMPONENT_INPUTS[1:]
        self.splits = _pressure_splits()

    def predict(self, scored, structure, **options):
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

    def test_the_matrix_has_one_column_per_level_of_the_grid_it_is_given(self):
        rng = random.Random(1)
        x = [[rng.gauss(0, 1) for _ in range(3)] for _ in range(60)]
        y = [row[0] + rng.gauss(0, 1) for row in x]
        served = [[rng.gauss(0, 1) for _ in range(3)] for _ in range(5)]
        matrix = ml._gbm_quantile_matrix(x, y, served, GRID)
        self.assertEqual(matrix.shape, (5, len(GRID)))
        self.assertEqual(len(GRID), 23)
        default = ml._gbm_quantile_matrix(x, y, served)
        self.assertEqual(default.shape[1], len(ml.PRESSURE_SPREAD_DISTRIBUTION_SETTINGS["quantile_grid"]))
        for row in matrix.tolist():
            self.assertEqual(row, sorted(row))

    def test_the_recorded_laws_are_on_the_grid_the_predictor_is_given(self):
        risk = [k for k in range(90, len(self.rows) - 1) if _is_risk(self.rows[k])][0]
        ordinary = [k for k in range(90, len(self.rows) - 1) if not _is_risk(self.rows[k])][0]
        for scored in (risk, ordinary):
            _curves, record = self.predict(scored, "two_part", grid=GRID)
            part, quantiles = record[0]
            self.assertIsNotNone(part)
            self.assertEqual(len(quantiles), len(GRID))

    def test_the_default_grid_is_the_declared_one_and_the_curve_is_read_on_the_grid_given(self):
        risk = [k for k in range(90, len(self.rows) - 1) if _is_risk(self.rows[k])][0]
        _c, default = self.predict(risk, "risk_date")
        self.assertEqual(len(default[0][1]), len(ml.PRESSURE_SPREAD_DISTRIBUTION_SETTINGS["quantile_grid"]))
        curves, record = self.predict(risk, "risk_date", grid=GRID)
        expected = ml.exceedance_from_quantiles(record[0][1], GRID, (5.0, 10.0))
        self.assertEqual(tuple(curves.curves[0]), tuple(expected))

    def test_a_grid_that_is_not_strictly_inside_zero_and_one_and_ascending_is_refused(self):
        for bad in ((0.5,), (), (0.5, 0.4, 0.6), (0.0, 0.5, 1.0), (0.1, 0.1, 0.9)):
            with self.assertRaises(ValueError):
                ml.pressure_spread_distribution_exceedance(_PRESSURE_CALENDAR, self.splits, 20, grid=bad)


if __name__ == "__main__":
    unittest.main()
