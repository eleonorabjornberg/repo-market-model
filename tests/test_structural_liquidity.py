"""The structural liquidity model (#542, track S of #374): `repo_model.structural_liquidity`.

The pressure-day probability is a logistic of the expected spread move, built from a mechanism
written down before any score: the reserve-demand elasticity at the current reserve level times
the drain the ON RRP balance has not absorbed, plus the as-of spread. Six coefficients are fitted.
What is covered:

* `FormTests` -- the functional form, standard library only: the elasticity is the exponential
  reserve demand curve (1 at satiation, decreasing in reserves), the buffer absorbs the drain one
  for one, and a negative net settlement drains nothing.
* `RidgeLogisticTests` -- the estimator recovers the sign of a planted effect, is deterministic and
  is shrunk by its penalty.
* `DesignTests` -- the six columns, the drain column by horizon, the calendar terms from the split
  declaration, and the refusal of an unobserved input.
* `DeclarationTests` -- `metadata/structural_liquidity.json` and the judge's candidate files say
  what the module computes.
* `PredictorTests` -- the fitted predictor under the fold loop's guards, on a panel whose pressure
  follows elasticity x shortfall: it finds the pressure days, forecasts every day, and records six
  coefficients per refit with the signs the mechanism says.

**Recorded mutations** (disposable copy of the tree, `/opt/rmm-venv`, `PYTHONDONTWRITEBYTECODE=1`,
the killing test run alone, each confirmed applied by `grep` and restored before the next):

1. `StructuralDesign._value`: replace `if value is None or not math.isfinite(float(value)):` by
   `if False:`. An unobserved input is no longer refused as one; `float(None)` raises `TypeError`
   and `DesignTests.test_an_unobserved_input_is_refused` fails (an error, no `ValueError`).
2. `structural_exceedance.fit_predict`: replace `if information is None:` by `if False:`. A call
   without the as-of rule is no longer refused where it is made; it fails later with
   `AttributeError: 'NoneType' object has no attribute 'horizon'` and
   `PredictorTests.test_the_model_is_refused_without_the_rule` fails (no `ValueError`).
"""

from __future__ import annotations

import importlib.util
import json
import math
import os
import unittest
from datetime import date, time, timedelta
from pathlib import Path
from types import MappingProxyType
from unittest import mock

from repo_model import contract, measurement_fields, net_settlement as ns, projected_reserves as pr, scarcity, structural_liquidity as sl
from repo_model.asof import InformationRule
from repo_model.data import CALENDAR_COLUMN_RULES, DailyObservation, next_business_day
from repo_model.evaluation_splits import load_split_declaration

REPO = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((REPO / "metadata" / "sources.json").read_text())
SPLITS = load_split_declaration(REPO / "metadata" / "evaluation_splits.json")
REQUIRE_ML = "REPO_MODEL_REQUIRE_ML"


def _values(**kw):
    base = {
        "sofr": 4.0, "iorb": 4.0, "reserve_balances": 3200.0, "bank_total_assets": 26000.0, "on_rrp": 50.0,
        "tga": 700.0, "net_settlement": 80.0, "net_settlement_ahead_1d": 30.0 + 80.0, "net_settlement_due_5d": 150.0,
        "net_settlement_ahead_2d": 125.0, "net_settlement_ahead_3d": 200.0, "net_settlement_ahead_4d": 260.0,
        "net_settlement_ahead_5d": 330.0, "days_to_month_end": 12.0, "quarter_end": 0.0, "tax_date": 0.0,
    }
    base.update(kw)
    return base


def _obs(**kw):
    return DailyObservation(date(2024, 3, 12), _values(**kw))


class FormTests(unittest.TestCase):
    def test_the_elasticity_is_one_at_satiation_and_falls_with_reserves(self):
        self.assertAlmostEqual(sl.elasticity(sl.SATIATION), 1.0, places=12)
        ratios = [0.09, 0.10, 0.11, 0.12, 0.13, 0.15]
        values = [sl.elasticity(r) for r in ratios]
        self.assertEqual(values, sorted(values, reverse=True))
        self.assertAlmostEqual(sl.elasticity(sl.SATIATION - sl.LENGTH), math.e, places=12)

    def test_the_buffer_absorbs_the_drain_one_for_one(self):
        self.assertEqual(sl.shortfall(80.0, 50.0), 30.0)
        self.assertEqual(sl.shortfall(80.0, 200.0), 0.0)

    def test_a_negative_net_settlement_drains_nothing(self):
        self.assertEqual(sl.shortfall(-40.0, 0.0), 0.0)


class RidgeLogisticTests(unittest.TestCase):
    def data(self):
        xs, ys = [], []
        for i in range(400):
            a = ((i * 37) % 100) / 100.0
            b = ((i * 53) % 100) / 100.0
            xs.append([a, b])
            ys.append(1 if a > 0.7 else 0)
        return xs, ys

    def test_a_planted_effect_has_its_sign(self):
        xs, ys = self.data()
        fit = sl.fit_ridge_logistic(xs, ys, c=1.0)
        self.assertGreater(fit.coefficients[1], 0.0)
        self.assertLess(abs(fit.coefficients[2]), abs(fit.coefficients[1]))

    def test_the_fit_is_deterministic_and_the_penalty_shrinks_it(self):
        xs, ys = self.data()
        a = sl.fit_ridge_logistic(xs, ys, c=1.0)
        b = sl.fit_ridge_logistic(xs, ys, c=1.0)
        self.assertEqual(a.coefficients, b.coefficients)
        tight = sl.fit_ridge_logistic(xs, ys, c=0.01)
        self.assertLess(abs(tight.coefficients[1]), abs(a.coefficients[1]))

    def test_probabilities_are_in_the_unit_interval(self):
        xs, ys = self.data()
        fit = sl.fit_ridge_logistic(xs, ys, c=1.0)
        for p in fit.predict(xs):
            self.assertTrue(0.0 < p < 1.0)


class DesignTests(unittest.TestCase):
    FEATURES = sl.features_at_horizon(1)

    def test_six_parameters(self):
        design = sl.StructuralDesign(self.FEATURES, SPLITS)
        self.assertEqual(len(design.names) + 1, 6)
        self.assertEqual(design.names[0], "spread_bps")

    def test_the_row_is_the_declared_terms(self):
        design = sl.StructuralDesign(self.FEATURES, SPLITS)
        e = sl.elasticity(3200.0 / 26000.0)
        row = design.row(_obs(), 12.0)
        self.assertAlmostEqual(row[0], 0.0)
        self.assertAlmostEqual(row[1], e * 60.0)  # the scored day's announced 110 less the 50 ON RRP, not the decision day's 80
        self.assertAlmostEqual(row[2], e * 12.0)
        self.assertEqual(row[3:], [0.0, 0.0])

    def test_a_falling_tga_adds_no_drain(self):
        design = sl.StructuralDesign(self.FEATURES, SPLITS)
        self.assertEqual(design.row(_obs(), -30.0)[2], 0.0)

    def test_calendar_terms_come_from_the_day_type(self):
        design = sl.StructuralDesign(self.FEATURES, SPLITS)
        e = sl.elasticity(3200.0 / 26000.0)
        self.assertAlmostEqual(design.row(_obs(tax_date=1.0), 0.0)[3], e)
        self.assertAlmostEqual(design.row(_obs(quarter_end=1.0), 0.0)[4], e)
        self.assertAlmostEqual(design.row(_obs(days_to_month_end=0.0), 0.0)[4], e)

    def test_the_drain_columns_follow_the_horizon(self):
        near = sl.StructuralDesign(sl.features_at_horizon(1), SPLITS)
        # #568: at h = 1 the scored day is the next row, whose settlement is public at the decision only as
        # the one-day-ahead announced net (`net_settlement` on the decision row is the decision day's own)
        self.assertEqual(near.drain_columns, ("net_settlement_ahead_1d",))
        self.assertNotIn("net_settlement", sl.features_at_horizon(1))
        # #618: at h >= 2 it is that day's own net, the cumulative column less the one before, not the five-day sum
        for horizon in range(2, 6):
            far = sl.StructuralDesign(sl.features_at_horizon(horizon), SPLITS)
            self.assertEqual(
                far.drain_columns, (f"net_settlement_ahead_{horizon}d", f"net_settlement_ahead_{horizon - 1}d")
            )
            self.assertNotIn("net_settlement_due_5d", sl.features_at_horizon(horizon))

    def test_the_scored_days_own_net_is_the_drain_at_every_horizon(self):
        e = sl.elasticity(3200.0 / 26000.0)
        # the cumulative columns of `_values` are 110, 125, 200, 260, 330: the days' own nets are 110, 15, 75, 60, 70
        for horizon, own in ((1, 110.0), (2, 15.0), (3, 75.0), (4, 60.0), (5, 70.0)):
            design = sl.StructuralDesign(sl.features_at_horizon(horizon), SPLITS)
            self.assertAlmostEqual(design.drain(_obs()), own)
            self.assertAlmostEqual(design.row(_obs(), 0.0)[1], e * max(0.0, own - 50.0))

    def test_a_scored_day_that_returns_cash_drains_nothing_whatever_the_days_before_it(self):
        # #618: the five-day sum is 150 here and would fire; the scored day's own net at h = 2 is -20
        design = sl.StructuralDesign(sl.features_at_horizon(2), SPLITS)
        row = design.row(_obs(net_settlement_ahead_1d=100.0, net_settlement_ahead_2d=80.0), 0.0)
        self.assertEqual(row[1], 0.0)

    def test_a_pair_of_drain_columns_that_is_not_adjacent_is_refused(self):
        features = [f for f in sl.features_at_horizon(1)] + ["net_settlement_ahead_3d"]
        with self.assertRaises(ValueError):
            sl.StructuralDesign(features, SPLITS)

    def test_an_unobserved_input_is_refused(self):
        design = sl.StructuralDesign(self.FEATURES, SPLITS)
        with self.assertRaises(ValueError):
            design.row(_obs(on_rrp=None), 0.0)

    def test_a_missing_declared_input_is_refused(self):
        with self.assertRaises(ValueError):
            sl.StructuralDesign(("spread_bps", "tga"), SPLITS)


class DeclarationTests(unittest.TestCase):
    def test_the_declaration_says_what_the_module_computes(self):
        document = json.loads(sl.DEFAULT_DECLARATION.read_text())
        self.assertEqual(document["elasticity"]["satiation"], sl.SATIATION)
        self.assertEqual(document["elasticity"]["length"], sl.LENGTH)
        self.assertEqual(document["parameters"]["count"], 6)
        self.assertEqual(tuple(document["parameters"]["names"]), ("intercept",) + sl.COLUMN_NAMES)
        self.assertEqual(sl.SATIATION, scarcity.SATIATION_BAND[0])

    def test_the_candidate_file_pins_the_features(self):
        entry = json.loads((REPO / "metadata" / "pressure_judge" / "candidates" / "structural_liquidity.json").read_text())
        self.assertEqual(entry["role"], "candidate")
        self.assertEqual(sorted(entry["features"]), sorted(sl.features_at_horizon(1)))


def _require_extra(case):
    if all(importlib.util.find_spec(n) is not None for n in ("numpy", "sklearn")):
        return
    if os.environ.get(REQUIRE_ML):
        case.fail(f"{REQUIRE_ML} is set but the optional 'ml' extra is not importable")
    case.skipTest("the optional 'ml' extra is not installed")


def _panel(count=330):
    """Business days from 2024-01-02: pressure (+8 bp) the day after a large unbuffered settlement."""

    days = [date(2024, 1, 2)]
    while len(days) < count:
        days.append(next_business_day(days[-1], 1))
    rows = []
    for index, day in enumerate(days):
        calendar = {n: float(rule(day)) for n, rule in CALENDAR_COLUMN_RULES.items()
                    if n in ("days_to_month_end", "quarter_end", "tax_date")}
        settle = 120.0 if index % 9 == 4 else 5.0 * (index % 3)
        spread = 8.0 if index % 9 == 5 else -1.0 + 0.1 * (index % 3)
        week = index // 5
        rows.append(DailyObservation(day, {
            "sofr": 4.0 + spread / 100.0, "iorb": 4.0, "sofr_volume": 2100.0 + index % 11,
            "reserve_balances": 3000.0, "bank_total_assets": 26000.0,
            "on_rrp": 20.0, "tga": 700.0 + 25.0 * ((week * 7) % 5),
            "net_settlement": settle, "net_settlement_due_5d": settle, **calendar,
            **{f"net_settlement_ahead_{k}d": k * settle for k in range(1, 6)},
        }))
    return rows


class PredictorTests(unittest.TestCase):
    FEATURES = sl.features_at_horizon(1)

    def setUp(self):
        _require_extra(self)
        self.rows = _panel()
        fields = {**ns.COLUMN_FIELDS, **pr.COLUMN_FIELDS}
        patch = mock.patch.multiple(
            contract,
            FEATURE_FIELDS=MappingProxyType({**contract.FEATURE_FIELDS, **fields}),
            FEATURE_SOURCES=MappingProxyType({
                **contract.FEATURE_SOURCES,
                **{c: tuple(sorted({s for s, _f in pairs})) for c, pairs in fields.items()},
            }),
        )
        patch.start()
        self.addCleanup(patch.stop)

    def backtest(self, horizon=1, taus=(5.0,)):
        from repo_model.baseline import rolling_exceedance_backtest

        features = sl.features_at_horizon(horizon)
        predictor = sl.structural_exceedance(features, SPLITS, minimum_history=61)
        with scarcity.measurement_declaration():
            report = rolling_exceedance_backtest(
                self.rows, predictor=predictor, model_name="structural_liquidity", features=features,
                registry=measurement_fields.load_registry(), decision_time=time(16, 0), taus=taus, minimum_history=61,
                refit_every=21, horizon=horizon,
            )
        return report, predictor

    def test_it_forecasts_every_day_and_finds_the_planted_pressure(self):
        report, _ = self.backtest()
        self.assertTrue(report.scored_dates)
        hits = [p[0] for p, o in zip(report.forecast, report.outcomes) if o[0] == 1]
        others = [p[0] for p, o in zip(report.forecast, report.outcomes) if o[0] == 0]
        self.assertTrue(hits)
        self.assertGreater(sum(hits) / len(hits), 3 * sum(others) / len(others))
        self.assertTrue(all(0.0 < p[0] < 1.0 for p in report.forecast))

    def test_six_coefficients_per_refit_with_the_mechanisms_signs(self):
        _, predictor = self.backtest()
        self.assertTrue(predictor.fits)
        last = predictor.fits[-1]
        self.assertEqual(len(last["5"]["coefficients"]), 6)
        self.assertGreater(last["5"]["coefficients"][2], 0.0)  # e x shortfall

    def test_the_model_is_refused_without_the_rule(self):
        predictor = sl.structural_exceedance(self.FEATURES, SPLITS, minimum_history=61)
        with self.assertRaises(ValueError):
            predictor(self.rows[:100], self.rows[100:101], (5.0,), None, [self.rows[:100]])


if __name__ == "__main__":
    unittest.main()
