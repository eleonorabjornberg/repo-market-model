"""H5's calibration after reserve-management purchases (#845): the parts of `scripts/calibration_reserve_mgmt_845.py` that decide which days and cells enter a figure.

The script reads the walks of #634, the mean-reversion laws of #686 and #761 and `persistence_logistic`, to the last
development day (`repo_model.exploration.EXPLORATORY_END`), and reports mean P(spread > +5 bp) against the realised share for
two stretches. These tests pin the helpers: the last day is the exploratory end and no later day is accepted, a cell belongs
to a stretch by its target day, the error splits exactly into a level part and a residual-pool part, a (stretch, lead) cell
under Eleonora's minimum of three pressure days keeps only its counts on the page, and the bootstrap is the stationary one.

Recorded mutation for the new guard (the last day of a walk is checked by `repo_model.exploration.panel_end`): replacing
`return panel_end(value, EXPLORATORY_END, where=WHERE)` in `scripts/calibration_reserve_mgmt_845.py:last_day` with
`return date.fromisoformat(value) if value else EXPLORATORY_END` makes
`LastDayTests.test_a_day_after_the_exploratory_end_is_refused` fail with `AssertionError: LookAheadError not raised`;
restored, it passes.
"""

from __future__ import annotations

import importlib.util
import random
import sys
import unittest
from datetime import date
from pathlib import Path

from repo_model.exploration import EXPLORATORY_END
from repo_model.splits import LookAheadError

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "calibration_reserve_mgmt_845.py"


def _module():
    spec = importlib.util.spec_from_file_location("calibration_reserve_mgmt_845_script", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _law(centre: float, half_width: float = 2.0):
    """A 23-level law, evenly spread about `centre`."""

    from repo_model.scoring_protocol import GRID

    return [centre + half_width * (2.0 * level - 1.0) for level in GRID]


class LastDayTests(unittest.TestCase):
    def test_the_default_is_the_exploratory_end(self):
        self.assertEqual(_module().last_day(None), EXPLORATORY_END)

    def test_an_earlier_day_is_kept(self):
        self.assertEqual(_module().last_day("2026-06-30"), date(2026, 6, 30))

    def test_a_day_after_the_exploratory_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            _module().last_day("2026-09-04")


class StretchTests(unittest.TestCase):
    def test_a_target_day_belongs_to_a_stretch_by_its_own_date_inclusive(self):
        module = _module()
        first, last = date(2019, 10, 15), date(2020, 2, 28)
        self.assertTrue(module.in_stretch(first, first, last))
        self.assertTrue(module.in_stretch(last, first, last))
        self.assertFalse(module.in_stretch(date(2019, 10, 14), first, last))
        self.assertFalse(module.in_stretch(date(2020, 2, 29), first, last))

    def test_the_declared_stretches_end_at_or_before_the_exploratory_end_and_the_earlier_one_before_qe(self):
        module = _module()
        for name, (first, last) in module.stretches().items():
            self.assertLessEqual(last, EXPLORATORY_END, name)
        self.assertLess(module.stretches()["earlier_case_2019_20"][1], date(2020, 3, 1))


class DecompositionTests(unittest.TestCase):
    def test_the_two_parts_add_to_the_error_exactly(self):
        module = _module()
        laws = [_law(c) for c in (0.5, 1.0, 3.0, 4.5)]
        outcomes = [0.0, 1.0, 2.0, 0.5]
        parts = module.decompose(laws, outcomes)
        self.assertAlmostEqual(parts["level"] + parts["pool"], parts["error"], places=12)
        self.assertAlmostEqual(parts["error"], parts["mean_p"] - parts["realised"], places=12)

    def test_a_law_centred_on_the_outcomes_has_no_level_part(self):
        module = _module()
        outcomes = [1.0, 2.0, 3.0]
        laws = [_law(value) for value in outcomes]
        parts = module.decompose(laws, outcomes)
        self.assertAlmostEqual(parts["delta"], 0.0, places=12)
        self.assertAlmostEqual(parts["level"], 0.0, places=12)

    def test_a_centre_too_high_gives_a_positive_level_part_and_the_delta_moves_it_down(self):
        module = _module()
        outcomes = [0.0, 0.0, 0.0, 0.0]
        laws = [_law(4.0, 3.0) for _ in outcomes]
        parts = module.decompose(laws, outcomes)
        self.assertLess(parts["delta"], 0.0)
        self.assertGreater(parts["level"], 0.0)
        self.assertAlmostEqual(parts["centred_mean_p"], parts["mean_p"] - parts["level"], places=12)

    def test_no_cells_is_a_data_error(self):
        with self.assertRaises(ValueError):
            _module().decompose([], [])


class DaySetTests(unittest.TestCase):
    class _Splits:
        def reporting_day_type(self, day, values):
            return values["type"]

    class _Row:
        def __init__(self, day, **values):
            self.date, self.values = day, values

    def test_a_coupon_day_is_ordinary_but_not_calm_and_a_risk_type_is_neither(self):
        module = _module()
        module.var.is_risk_day = lambda row, splits: row.values["type"] != "ordinary" or row.values["coupon"]
        day = date(2026, 3, 3)
        calm = module.day_set_members(self._Row(day, type="ordinary", coupon=False), self._Splits())
        coupon = module.day_set_members(self._Row(day, type="ordinary", coupon=True), self._Splits())
        risk = module.day_set_members(self._Row(day, type="quarter_end", coupon=False), self._Splits())
        self.assertEqual(calm, {"ordinary": True, "calm_ordinary": True})
        self.assertEqual(coupon, {"ordinary": True, "calm_ordinary": False})
        self.assertEqual(risk, {"ordinary": False, "calm_ordinary": False})


class MinimumTests(unittest.TestCase):
    def test_a_cell_under_three_pressure_days_is_withheld_and_one_at_three_is_not(self):
        module = _module()
        self.assertTrue(module.under_minimum(0, 3))
        self.assertTrue(module.under_minimum(2, 3))
        self.assertFalse(module.under_minimum(3, 3))

    def test_the_minimum_is_the_declared_one(self):
        import json

        declared = json.loads((REPO / "metadata" / "exploration_845.json").read_text(encoding="utf-8"))
        self.assertEqual(_module().MINIMUM_PRESSURE_DAYS, declared["ruling_710_cells"]["minimum_pressure_days"])

    def test_a_withheld_cell_keeps_only_its_counts_in_the_tracked_record(self):
        module = _module()
        full = {"cells": 130, "pressure_days": 2, "laws": {"mean_reversion": {"mean_p": 0.1, "realised": 0.02}}}
        tracked = module.tracked_cell(full, withheld=True)
        self.assertEqual(tracked, {"cells": 130, "pressure_days": 2, "withheld": True})
        self.assertEqual(module.tracked_cell(full, withheld=False), full)


class BootstrapTests(unittest.TestCase):
    def test_a_constant_series_has_a_degenerate_interval(self):
        module = _module()
        low, high = module.stationary_interval([[0.25] * 30], draws=200, seed=1)[0]
        self.assertAlmostEqual(low, 0.25)
        self.assertAlmostEqual(high, 0.25)

    def test_the_interval_brackets_the_mean_and_is_reproducible(self):
        module = _module()
        rng = random.Random(3)
        series = [rng.random() for _ in range(80)]
        first = module.stationary_interval([series], draws=500, seed=845)[0]
        again = module.stationary_interval([series], draws=500, seed=845)[0]
        self.assertEqual(first, again)
        mean = sum(series) / len(series)
        self.assertLess(first[0], mean)
        self.assertGreater(first[1], mean)

    def test_series_are_resampled_jointly(self):
        module = _module()
        series = [float(i) for i in range(40)]
        difference = [a - b for a, b in zip(series, series)]
        low, high = module.stationary_interval([series, series, difference], draws=300, seed=7)[2]
        self.assertEqual((low, high), (0.0, 0.0))

    def test_series_of_unequal_length_are_a_data_error(self):
        with self.assertRaises(ValueError):
            _module().stationary_interval([[1.0, 2.0], [1.0]], draws=10, seed=1)


if __name__ == "__main__":
    unittest.main()
