"""The extreme-value tail (#383, track E of #374): `ml.fit_censored_gpd` and `ml.pressure_tail_exceedance`.

`P(spread > tau) = P(spread > u) * S(tau - u)`: a logistic body for the exceedance
of the declared threshold `u` and a generalised Pareto survival for the excess,
its scale log-linear in the reserve-scarcity state and the pressure-day type,
fitted by maximum likelihood to the basis-point-rounded excesses. What is covered:

* `FitTests` -- the estimator on simulated data (standard-library `random`):
  it recovers a constant shape and scale, finds a scale that differs by group,
  keeps the shape inside `GPD_SHAPE_BOUNDS`, falls back to an exponential below
  `minimum_excesses`, fits nothing and gives probability 0 with no excess, and
  refuses a bin below 1. The interval censoring is checked against the closed
  form of one bin.
* `PredictorTests` -- the predictor under the fold loop's guards, on a panel
  whose pressure falls on month and quarter ends: the curve is nested in tau,
  larger on a scheduled day, refused without the rule or at a tau not above
  `u`, and the per-fold record carries what the diagnostics read.

The leakage and availability guards the predictor relies on (the as-of rule's
information set and `_served_tga_change`) are `ml._pressure_pairs`' own, covered
in `tests/test_ml.py`; this model adds none of its own to the information set.

**Recorded mutations** (disposable copy of the tree, `/opt/rmm-venv`,
`PYTHONDONTWRITEBYTECODE=1`, the killing test run alone, each mutation confirmed
applied by `grep` and restored before the next). They are on the likelihood and
the forecast's reading of it, which the tests below pin:

1. `fit_censored_gpd`: `lower, upper = k - 1.0, k` -> `lower, upper = k, k + 1.0`
   (the bin moved up a basis point). `FitTests.test_the_bin_is_the_interval_below_the_excess`
   fails (`AssertionError: 1.4427 not less than 0.2`: the bin-1 exponential scale is no longer driven to the floor).
2. `pressure_tail_exceedance.fit_predict`: `tail.survival(float(tau) - threshold_bp, ...)`
   -> `tail.survival(float(tau) - threshold_bp - 1.0, ...)`.
   `PredictorTests.test_the_forecast_is_the_body_times_the_survival_at_tau_minus_u`
   fails (`AssertionError`: 0.000445 != 0.000334, a forecast read one basis point too far down the tail).
3. `fit_censored_gpd`: `0.5 * float(_expit(theta[1 + width]))` -> `float(_expit(theta[1 + width]))`
   (the shape bound doubled). `FitTests.test_the_shape_stays_inside_its_bounds` fails
   (`AssertionError: 0.866 not less than or equal to 0.5`).
"""

from __future__ import annotations

import importlib.util
import json
import math
import os
import random
import unittest
from datetime import date, time
from pathlib import Path

from repo_model.asof import InformationRule
from repo_model.data import CALENDAR_COLUMN_RULES, DailyObservation, next_business_day
from repo_model.evaluation_splits import load_split_declaration

REPO = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((REPO / "metadata" / "sources.json").read_text())
SPLITS = load_split_declaration(REPO / "metadata" / "evaluation_splits.json")
FEATURES = (
    "spread_bps", "days_to_month_end", "quarter_end", "tax_date", "reserve_balances", "tga",
)
REQUIRE_ML = "REPO_MODEL_REQUIRE_ML"
U = 2.0


def _require_extra(case: unittest.TestCase) -> None:
    ok = all(importlib.util.find_spec(name) is not None for name in ("numpy", "sklearn"))
    if ok:
        return
    if os.environ.get(REQUIRE_ML):
        case.fail(f"{REQUIRE_ML} is set but the optional 'ml' extra is not importable")
    case.skipTest("the optional 'ml' extra is not installed")


def _gpd_bins(rng, count, sigma, shape):
    """Rounded GPD excesses over `u + 0.5`, as the bins `k - u` (at least 1)."""

    out = []
    while len(out) < count:
        v = rng.random()
        z = sigma * (v ** -shape - 1.0) / shape if shape > 0 else -sigma * math.log(v)
        out.append(max(1, int(math.floor(z)) + 1))
    return out


class FitTests(unittest.TestCase):
    def setUp(self):
        _require_extra(self)
        from repo_model import ml

        self.ml = ml

    def test_it_recovers_a_constant_shape_and_scale(self):
        rng = random.Random(1)
        bins = _gpd_bins(rng, 4000, 4.0, 0.2)
        fit = self.ml.fit_censored_gpd([[0.0]] * len(bins), bins)
        self.assertEqual(fit.mode, "gpd")
        self.assertAlmostEqual(fit.shape, 0.2, delta=0.06)
        self.assertAlmostEqual(float(fit.sigma([[0.0]])[0]), 4.0, delta=0.5)

    def test_a_scale_that_differs_by_group_is_found(self):
        rng = random.Random(2)
        calm = _gpd_bins(rng, 1500, 2.0, 0.1)
        hot = _gpd_bins(rng, 1500, 6.0, 0.1)
        fit = self.ml.fit_censored_gpd([[0.0]] * 1500 + [[1.0]] * 1500, calm + hot)
        ratio = float(fit.sigma([[1.0]])[0] / fit.sigma([[0.0]])[0])
        self.assertAlmostEqual(ratio, 3.0, delta=0.5)

    def test_the_bin_is_the_interval_below_the_excess(self):
        # Every excess is 1 bp (the bin [0, 1)): the exponential MLE under censoring
        # has S(1) = P(Z >= 1) = 0, so the scale falls to the floor of the ridge-free
        # search, far below 1. Bins of 2 give exactly P(Z in [1, 2)) = 1 for every row,
        # so the scale sits near 1 / log(2)-ish and well above the bin-1 fit.
        ones = self.ml.fit_censored_gpd([[0.0]] * 40, [1] * 40, minimum_excesses=1000)
        twos = self.ml.fit_censored_gpd([[0.0]] * 40, [2] * 40, minimum_excesses=1000)
        self.assertEqual(ones.mode, "exponential")
        self.assertLess(float(ones.sigma([[0.0]])[0]), 0.2)
        self.assertGreater(float(twos.sigma([[0.0]])[0]), 5.0 * float(ones.sigma([[0.0]])[0]))
        # One mixed sample: its likelihood is the sum of the bin probabilities.
        bins = [1, 1, 2, 3]
        fit = self.ml.fit_censored_gpd([[0.0]] * 4, bins, minimum_excesses=1000)
        sigma = float(fit.sigma([[0.0]])[0])
        log_likelihood = sum(
            math.log(math.exp(-(k - 1) / sigma) - math.exp(-k / sigma)) for k in bins
        )
        self.assertAlmostEqual(fit.log_likelihood, log_likelihood, places=6)
        # The exponential MLE for these bins, by a grid over sigma.
        grid = [0.2 + 0.001 * i for i in range(4000)]
        best = max(
            grid,
            key=lambda s: sum(math.log(math.exp(-(k - 1) / s) - math.exp(-k / s)) for k in bins),
        )
        self.assertAlmostEqual(sigma, best, delta=0.01)

    def test_the_shape_stays_inside_its_bounds(self):
        rng = random.Random(3)
        heavy = _gpd_bins(rng, 3000, 3.0, 0.9)
        thin = _gpd_bins(rng, 3000, 3.0, 0.0)
        low, high = self.ml.GPD_SHAPE_BOUNDS
        for bins in (heavy, thin):
            fit = self.ml.fit_censored_gpd([[0.0]] * len(bins), bins)
            self.assertGreaterEqual(fit.shape, low)
            self.assertLessEqual(fit.shape, high)
        self.assertGreater(
            self.ml.fit_censored_gpd([[0.0]] * len(heavy), heavy).shape, 0.4
        )

    def test_below_the_minimum_it_is_an_exponential_and_without_excess_nothing(self):
        rng = random.Random(4)
        bins = _gpd_bins(rng, 10, 3.0, 0.2)
        fit = self.ml.fit_censored_gpd([[0.0]] * 10, bins, minimum_excesses=30)
        self.assertEqual((fit.mode, fit.shape), ("exponential", 0.0))
        none = self.ml.fit_censored_gpd([], [])
        self.assertEqual(none.mode, "none")
        self.assertEqual(float(none.survival(3.0, [[0.0, 0.0]])[0]), 0.0)

    def test_survival_is_the_closed_form_and_falls(self):
        rng = random.Random(5)
        bins = _gpd_bins(rng, 800, 3.0, 0.2)
        fit = self.ml.fit_censored_gpd([[0.0]] * 800, bins)
        sigma = float(fit.sigma([[0.0]])[0])
        for z in (1.0, 3.0, 8.0):
            expected = (1.0 + fit.shape * z / sigma) ** (-1.0 / fit.shape)
            self.assertAlmostEqual(float(fit.survival(z, [[0.0]])[0]), expected, places=9)
        values = [float(fit.survival(z, [[0.0]])[0]) for z in (0.0, 1.0, 5.0, 20.0)]
        self.assertEqual(values[0], 1.0)
        self.assertEqual(values, sorted(values, reverse=True))

    def test_a_bin_below_one_and_mismatched_rows_are_refused(self):
        with self.assertRaises(ValueError):
            self.ml.fit_censored_gpd([[0.0]], [0])
        with self.assertRaises(ValueError):
            self.ml.fit_censored_gpd([[0.0], [1.0]], [1])


def _business_days(first: date, count: int):
    out = [first]
    while len(out) < count:
        out.append(next_business_day(out[-1], 1))
    return out


def _panel(count=900, seed=7):
    """Business days from 2022-01-03, real calendar columns.

    Ordinary days sit at -1 bp. Month ends carry a heavy-ish excess (3 bp plus a
    geometric), quarter ends a larger one, so the tail's scale has a calendar
    effect to find and there are enough excesses over u = 2 bp for a shape.
    """

    rng = random.Random(seed)
    rows = []
    for index, day in enumerate(_business_days(date(2022, 1, 3), count)):
        calendar = {
            name: float(rule(day))
            for name, rule in CALENDAR_COLUMN_RULES.items()
            if name in ("days_to_month_end", "quarter_end", "tax_date")
        }
        spread = -1.0 + 0.1 * (index % 3)
        if calendar["quarter_end"] == 1.0:
            spread = 5.0 + int(rng.expovariate(1 / 6.0))
        elif calendar["days_to_month_end"] == 0.0:
            spread = 3.0 + int(rng.expovariate(1 / 2.0))
        week = index // 5
        rows.append(
            DailyObservation(
                day,
                {
                    "sofr": 4.0 + spread / 100.0,
                    "iorb": 4.0,
                    "sofr_volume": 2100.0 + index % 11,
                    "reserve_balances": 3200.0 - 20.0 * (week % 9),
                    "tga": 700.0 + 25.0 * ((week * 7) % 5),
                    **calendar,
                },
            )
        )
    return rows


class PredictorTests(unittest.TestCase):
    def setUp(self):
        _require_extra(self)
        from repo_model import ml

        self.ml = ml
        self.rows = _panel()

    def predictor(self, record=None):
        return self.ml.pressure_tail_exceedance(
            FEATURES, SPLITS, minimum_history=61, threshold_bp=U, record=record
        )

    def run_backtest(self, horizon=1, taus=(5.0, 10.0), record=None):
        from repo_model.baseline import rolling_exceedance_backtest

        return rolling_exceedance_backtest(
            self.rows,
            predictor=self.predictor(record),
            model_name="pressure_tail",
            features=FEATURES,
            registry=REGISTRY,
            decision_time=time(16, 0),
            taus=taus,
            minimum_history=61,
            refit_every=21,
            horizon=horizon,
        )

    def test_the_curve_is_nested_and_larger_on_a_scheduled_day(self):
        report = self.run_backtest(2)
        quarter, ordinary = [], []
        for when, curve in zip(report.scored_dates, report.forecast):
            self.assertLessEqual(curve[1], curve[0])
            self.assertTrue(0.0 <= curve[1] <= curve[0] <= 1.0)
            if when > date(2023, 6, 1):
                row = next(r for r in self.rows if r.date == when)
                (quarter if row.values["quarter_end"] == 1.0 else ordinary).append(curve[0])
        self.assertGreater(min(quarter), 0.1)
        self.assertGreater(sum(quarter) / len(quarter), 5 * sum(ordinary) / len(ordinary))

    def test_the_forecast_is_the_body_times_the_survival_at_tau_minus_u(self):
        record = []
        report = self.run_backtest(1, taus=(5.0, 10.0), record=record)
        served = [item for fold in record for item in fold["served"]]
        self.assertEqual(len(served), len(report.forecast))
        fold = next(f for f in record if f["mode"] == "gpd")
        checked = 0
        for fold in record:
            if fold["mode"] != "gpd":
                continue
            for item in fold["served"]:
                index = [s["date"] for s in served].index(item["date"])
                curve = report.forecast[index]
                for tau, value in zip((5.0, 10.0), curve):
                    z = (tau - U) / item["sigma"]
                    survival = (
                        math.exp(-math.log1p(fold["shape"] * z) / fold["shape"])
                        if fold["shape"] >= 1e-8
                        else math.exp(-z)
                    )
                    self.assertAlmostEqual(value, item["body"] * survival, places=9)
                    checked += 1
        self.assertGreater(checked, 100)

    def test_the_record_carries_the_fit_summary(self):
        record = []
        self.run_backtest(1, record=record)
        self.assertTrue(record)
        modes = {fold["mode"] for fold in record}
        self.assertIn("gpd", modes)
        for fold in record:
            self.assertLessEqual(fold["train_end"], fold["served"][0]["date"])
            self.assertEqual(
                set(fold["coefficients"]), {"reserve_balances", "quarter_end", "month_end", "tax_date"}
            )

    def test_a_tau_not_above_u_is_refused(self):
        rule = InformationRule(REGISTRY, FEATURES, decision_time=time(16, 0))
        with self.assertRaisesRegex(ValueError, "not above"):
            self.predictor()(self.rows[:300], self.rows[300:301], (2.0,), information=rule)

    def test_without_the_rule_it_refuses(self):
        with self.assertRaises(ValueError):
            self.predictor()(self.rows[:300], self.rows[300:301], (5.0,))

    def test_a_design_without_reserves_or_the_calendar_is_refused(self):
        with self.assertRaises(ValueError):
            self.ml.pressure_tail_exceedance(
                ("spread_bps", "days_to_month_end", "quarter_end", "tax_date"),
                SPLITS, minimum_history=61, threshold_bp=U,
            )
        with self.assertRaises(ValueError):
            self.ml.pressure_tail_exceedance(
                ("spread_bps", "reserve_balances"), SPLITS, minimum_history=61, threshold_bp=U
            )


if __name__ == "__main__":
    unittest.main()
