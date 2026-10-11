"""Reserves projected to the scored day (#545, track S2 of #374): `repo_model.projected_reserves`.

The latest as-of reserve level is rolled forward to the scored day through every flow public at the
decision, placed on the SR 1019 demand curve, and fed to a logistic. What is covered:

* `FlowTests` -- the arithmetic of the roll-forward: the Treasury account and the facility gain what
  reserves lose, the ON RRP balance absorbs a net drain before reserves do, a net paydown raises
  reserves, and the distance and change columns are the declared percentage points of bank assets.
* `TaxRuleTests` -- an expected tax receipt is the previous year's rise on the same position of the
  same month's window, less that day's settlement, floored at zero, and nothing off a tax date.
* `AheadColumnTests` -- the announced net settlement of the next k business days counts an auction
  only from its announcement.
* `BuildTests` -- the columns on a panel read through the as-of rule: the reserve level is the
  Wednesday level the rule reads, and the columns are the roll-forward of it.
* `NoFutureTests` -- a column that depends on a row after its own decision is refused.
* `DeclarationTests` -- `metadata/projected_reserves.json`, the source registry entry and the judge's
  candidate files say what the module computes.
* `CombinedRowTests` -- the combined row keeps the passer's forecast on a risk date, as #539's hurdle does, and
  serves the model elsewhere.
* `PredictorTests` -- the logistic on the projected columns under the fold loop's guards finds pressure
  planted at a projected shortfall, and forecasts every day.

**Recorded mutations** (disposable copy of the tree, `/opt/rmm-venv`, `PYTHONDONTWRITEBYTECODE=1`, the
killing test run alone, each confirmed applied by `grep` and restored before the next):

1. `build_row`: replace `rows[i].values.get(f"net_settlement_ahead_{h}d")` by
   `rows[min(i + 1, len(rows) - 1)].values.get(f"net_settlement_ahead_{h}d")`. The column then reads
   the next row's announcements; `NoFutureTests.test_the_columns_pass_when_they_use_nothing_later`
   fails with `LookAheadError: proj_reserves_h4 on 2023-04-14 is 2974.0, but the panel cut at that row
   gives 2978.0` and `test_a_later_rows_values_do_not_move_an_earlier_column` with `AssertionError`.
2. `known_auctions` use in `ahead_columns`: replace `ns.net_for_day(by_day.get(day, ()), instant)`
   by `ns.net_for_day(by_day.get(day, ()), datetime.max)`. An auction announced after the instant is
   counted; `AheadColumnTests.test_an_auction_counts_only_from_its_announcement` fails with
   `AssertionError: 30.0 != 0.0` (the figure as announced at the instant).
"""

from __future__ import annotations

import importlib.util
import json
import os
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path
from types import MappingProxyType
from unittest import mock

from repo_model import contract, measurement_fields, net_settlement as ns, projected_reserves as pr, scarcity
from repo_model.asof import InformationRule
from repo_model.data import CALENDAR_COLUMN_RULES, DailyObservation, corporate_tax_deadline, next_business_day
from repo_model.evaluation_splits import load_split_declaration
from repo_model.splits import LookAheadError

REPO = Path(__file__).resolve().parents[1]
SPLITS = load_split_declaration(REPO / "metadata" / "evaluation_splits.json")
REQUIRE_ML = "REPO_MODEL_REQUIRE_ML"


class FlowTests(unittest.TestCase):
    def test_a_net_drain_is_absorbed_by_the_facility_first(self):
        self.assertEqual(pr.reserve_change(100.0, 30.0), -70.0)
        self.assertEqual(pr.reserve_change(100.0, 250.0), 0.0)

    def test_a_net_paydown_raises_reserves(self):
        self.assertEqual(pr.reserve_change(-40.0, 500.0), 40.0)

    def test_the_roll_forward_is_the_liability_identity(self):
        # R_O = 3000; the TGA has risen 50 and the facility has fallen 20 since O; 10 more settled after the
        # TGA's read row; 80 is announced ahead and the facility holds 30.
        level = pr.roll_forward(3000.0, tga_change=50.0, rrp_change=-20.0, gap_settlement=10.0, flow_ahead=80.0, rrp_level=30.0)
        self.assertAlmostEqual(level, 3000.0 - 50.0 + 20.0 - 10.0 - 50.0)

    def test_distance_and_change_are_percentage_points_of_bank_assets(self):
        dist, change = pr.distance_and_change(projected=3120.0, start=3400.0, bank_assets=26000.0)
        self.assertAlmostEqual(dist, 100.0 * (3120.0 / 26000.0 - pr.SATIATION))
        self.assertAlmostEqual(change, 100.0 * (3120.0 - 3400.0) / 26000.0)

    def test_satiation_is_the_lower_end_of_the_scarcity_band(self):
        self.assertEqual(pr.SATIATION, scarcity.SATIATION_BAND[0])


def _rows_year(year, extra=None):
    rows = {}
    day = date(year, 1, 2)
    while day.year == year:
        rows[day] = DailyObservation(day, {"tga_daily_change": 5.0, "net_settlement": 1.0})
        day = next_business_day(day, 1)
    for when, values in (extra or {}).items():
        rows[when] = DailyObservation(when, {**rows[when].values, **values})
    return rows


class TaxRuleTests(unittest.TestCase):
    def test_nothing_is_expected_off_a_tax_date(self):
        self.assertEqual(pr.expected_tax(date(2023, 6, 1), _rows_year(2022)), 0.0)

    def test_the_same_position_of_the_same_months_window_a_year_earlier(self):
        deadline_2022 = corporate_tax_deadline(2022, 6)
        second = next_business_day(deadline_2022, 1)
        by_date = _rows_year(2022, {second: {"tga_daily_change": 61.0, "net_settlement": 11.0}})
        deadline_2023 = corporate_tax_deadline(2023, 6)
        self.assertEqual(pr.expected_tax(next_business_day(deadline_2023, 1), by_date), 50.0)
        # the deadline itself is the window's first position, not the second
        self.assertEqual(pr.expected_tax(deadline_2023, by_date), 4.0)

    def test_the_receipt_is_floored_at_zero(self):
        deadline_2022 = corporate_tax_deadline(2022, 9)
        by_date = _rows_year(2022, {deadline_2022: {"tga_daily_change": -30.0, "net_settlement": 10.0}})
        self.assertEqual(pr.expected_tax(corporate_tax_deadline(2023, 9), by_date), 0.0)

    def test_no_row_a_year_earlier_is_no_receipt(self):
        self.assertEqual(pr.expected_tax(corporate_tax_deadline(2023, 4), {}), 0.0)


def _auction(settles, offering, maturing, announced, kind="Note"):
    return ns.Auction(settles, kind, False, offering, maturing, None, datetime.combine(announced, time(12, 0)), None)


class AheadColumnTests(unittest.TestCase):
    DECLARATION = {"announcement_time": "12:00"}

    def rows(self):
        days = [date(2024, 3, 11)]
        while len(days) < 10:
            days.append(next_business_day(days[-1], 1))
        return [DailyObservation(day, {}) for day in days]

    def test_the_cumulative_net_of_the_next_k_business_days(self):
        rows = self.rows()
        first, second = rows[1].date, rows[2].date
        auctions = [
            _auction(first, 100.0, 40.0, rows[0].date),
            _auction(second, 70.0, 10.0, rows[0].date),
        ]
        out = pr.ahead_columns(rows, auctions, self.DECLARATION)
        self.assertEqual(out[0].values["net_settlement_ahead_1d"], 60.0)
        self.assertEqual(out[0].values["net_settlement_ahead_2d"], 120.0)
        self.assertEqual(out[0].values["net_settlement_ahead_5d"], 120.0)

    def test_an_auction_counts_only_from_its_announcement(self):
        rows = self.rows()
        later = _auction(rows[1].date, 100.0, 70.0, rows[1].date)
        out = pr.ahead_columns(rows, [later], self.DECLARATION)
        self.assertEqual(out[0].values["net_settlement_ahead_1d"], 0.0)
        self.assertEqual(out[1].values["net_settlement_ahead_1d"], 0.0)  # row 1 looks ahead from day 2
        earlier = _auction(rows[3].date, 100.0, 70.0, rows[1].date)
        out = pr.ahead_columns(rows, [earlier], self.DECLARATION)
        self.assertEqual(out[0].values["net_settlement_ahead_3d"], 0.0)
        self.assertEqual(out[1].values["net_settlement_ahead_2d"], 30.0)


def _panel(count=330):
    """Business days from 2023-01-03 with the columns the roll-forward reads, weekly reserves carried."""

    days = [date(2023, 1, 3)]
    while len(days) < count:
        days.append(next_business_day(days[-1], 1))
    rows = []
    for index, day in enumerate(days):
        calendar = {n: float(rule(day)) for n, rule in CALENDAR_COLUMN_RULES.items()
                    if n in ("days_to_month_end", "quarter_end", "tax_date")}
        wednesday = day - timedelta(days=(day.weekday() - 2) % 7)
        week = (wednesday - date(2023, 1, 4)).days // 7
        settle = 120.0 if index % 9 == 4 else 5.0 * (index % 3)
        spread = 8.0 if index % 9 == 5 else -1.0 + 0.1 * (index % 3)
        rows.append(DailyObservation(day, {
            "sofr": 4.0 + spread / 100.0, "iorb": 4.0, "sofr_volume": 2100.0 + index % 11,
            "reserve_balances": 3000.0 - 10.0 * (week % 4), "bank_total_assets": 26000.0,
            "on_rrp": 20.0 + index % 3, "tga": 700.0, "tga_daily": 700.0 + 2.0 * index % 40,
            "tga_daily_change": 2.0 if index % 40 else -78.0, "net_settlement": settle,
            **{f"net_settlement_ahead_{k}d": k * (5.0 + index % 7) for k in range(1, 6)}, **calendar,
        }))
    return rows


class _Measured(unittest.TestCase):
    def setUp(self):
        fields = {**measurement_fields.COLUMN_FIELDS, **ns.COLUMN_FIELDS, **pr.COLUMN_FIELDS}
        scarcity_context = scarcity.measurement_declaration()
        scarcity_context.__enter__()
        self.addCleanup(scarcity_context.__exit__, None, None, None)
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
        self.registry = measurement_fields.load_registry()
        self.rows = _panel()

    def rule(self):
        return InformationRule(self.registry, pr.READ_FEATURES, decision_time=time(16, 0), horizon=1)


class BuildTests(_Measured):
    def test_the_columns_are_the_roll_forward_of_the_reserve_level_the_rule_reads(self):
        out = pr.build_columns(self.rows, self.rule(), last_day=date(2025, 12, 31))
        rule = self.rule()
        dates = pr.extended_dates([r.date for r in self.rows], 100)
        info = rule.information_set(dates, 101)
        read = {r.feature: r.row for r in info.reads}
        start = self.rows[read["reserve_balances"]].values["reserve_balances"]
        row = out[100].values
        self.assertIsNotNone(row["proj_reserves_h1"])
        wednesday = self.rows[read["reserve_balances"]].date
        wednesday -= timedelta(days=(wednesday.weekday() - 2) % 7)
        tga_then = [r for r in self.rows if r.date <= wednesday][-1].values["tga_daily"]
        rrp_then = [r for r in self.rows if r.date <= wednesday][-1].values["on_rrp"]
        gap = sum(r.values["net_settlement"] for r in self.rows[read["tga_daily"] + 1: 101])
        expected = pr.roll_forward(
            start,
            tga_change=self.rows[read["tga_daily"]].values["tga_daily"] - tga_then,
            rrp_change=self.rows[read["on_rrp"]].values["on_rrp"] - rrp_then,
            gap_settlement=gap,
            flow_ahead=self.rows[100].values["net_settlement_ahead_1d"] + pr.window_tax(self.rows, 100, 1),
            rrp_level=self.rows[read["on_rrp"]].values["on_rrp"],
        )
        self.assertAlmostEqual(row["proj_reserves_h1"], expected)
        dist, change = pr.distance_and_change(expected, start, 26000.0)
        self.assertAlmostEqual(row["proj_dist_h1"], dist)
        self.assertAlmostEqual(row["proj_change_h1"], change)

    def test_the_reserve_level_is_the_wednesday_level_of_an_older_week(self):
        out = pr.build_columns(self.rows, self.rule(), last_day=date(2025, 12, 31))
        # The H.4.1 is published on Thursday at 16:30: a Monday decision reads the week before last's Wednesday
        # or last week's; either way the projected change from that level is never taken from a later level.
        self.assertTrue(all(abs(r.values["proj_change_h1"]) < 200 for r in out[60:200]))

    def test_a_day_after_the_last_scored_day_has_no_column(self):
        out = pr.build_columns(self.rows, self.rule(), last_day=self.rows[150].date)
        self.assertIsNone(out[151].values["proj_reserves_h1"])
        self.assertIsNotNone(out[150].values["proj_reserves_h1"])

    def test_the_columns_for_every_horizon_exist(self):
        out = pr.build_columns(self.rows, self.rule(), last_day=date(2025, 12, 31))
        for h in pr.HORIZONS:
            for name in (f"proj_reserves_h{h}", f"proj_dist_h{h}", f"proj_change_h{h}"):
                self.assertIn(name, out[100].values)
                self.assertIsNotNone(out[100].values[name], name)


class NoFutureTests(_Measured):
    """The guard that refuses a column built from a row after its own decision.

    Recorded mutation (#545): in `build_row`, `rows[i].values.get(f"net_settlement_ahead_{h}d")` ->
    `rows[min(i + 1, len(rows) - 1)].values.get(f"net_settlement_ahead_{h}d")`;
    `test_the_columns_pass_when_they_use_nothing_later` then raises `LookAheadError` and
    `test_a_later_rows_values_do_not_move_an_earlier_column` fails (`2955.0 != -7024.0`).
    """

    def test_the_columns_pass_when_they_use_nothing_later(self):
        out = pr.build_columns(self.rows, self.rule(), last_day=date(2025, 12, 31))
        pr.check_no_future(self.rows, out, self.rule(), last_day=date(2025, 12, 31), indices=range(70, 120, 7))

    def test_a_column_that_reads_a_later_row_is_refused(self):
        out = pr.build_columns(self.rows, self.rule(), last_day=date(2025, 12, 31))
        bent = [DailyObservation(r.date, dict(r.values)) for r in out]
        bent[100].values["proj_reserves_h1"] += 25.0
        with self.assertRaises(LookAheadError):
            pr.check_no_future(self.rows, bent, self.rule(), last_day=date(2025, 12, 31), indices=[100])

    def test_a_later_rows_values_do_not_move_an_earlier_column(self):
        full = pr.build_columns(self.rows, self.rule(), last_day=date(2025, 12, 31))
        changed = [DailyObservation(r.date, dict(r.values)) for r in self.rows]
        for later in changed[101:]:
            later.values["net_settlement"] = 9999.0
            later.values["tga_daily"] = 9999.0
            later.values["net_settlement_ahead_1d"] = 9999.0
        again = pr.build_columns(changed, self.rule(), last_day=date(2025, 12, 31))
        for name in pr.COLUMNS_BUILT:
            self.assertEqual(full[100].values[name], again[100].values[name], name)


class DeclarationTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads((REPO / "metadata" / "projected_reserves.json").read_text())

    def test_the_declaration_says_what_the_module_computes(self):
        self.assertEqual(self.document["projection"]["satiation"], pr.SATIATION)
        self.assertEqual(self.document["projection"]["horizons"], list(pr.HORIZONS))
        self.assertEqual(self.document["source"], pr.SOURCE_ID)
        self.assertEqual(self.document["horizons"], list(pr.HORIZONS))

    def test_the_registry_declares_the_columns_with_no_lag(self):
        registry = json.loads((REPO / "metadata" / "sources_measurement.json").read_text())
        entry = registry[pr.SOURCE_ID]
        self.assertEqual(sorted(entry["fields"]), sorted(pr.COLUMNS))
        self.assertEqual(entry["release_lag"]["days"], 0)
        self.assertEqual(sorted(pr.COLUMN_FIELDS), sorted(pr.COLUMNS))

    def test_the_columns_are_off_in_the_published_feature_map(self):
        self.assertFalse(set(pr.COLUMNS) & set(contract.FEATURE_FIELDS))

    def test_the_candidate_files_pin_the_features(self):
        base = REPO / "metadata" / "pressure_judge" / "candidates"
        entry = json.loads((base / "projected_reserves.json").read_text())
        self.assertEqual(entry["role"], "candidate")
        self.assertEqual(sorted(entry["features"]), sorted(pr.features_at_horizon(1)))
        combined = json.loads((base / "risk_gbm+projected.json").read_text())
        self.assertEqual(combined["parent"], "risk_gbm")
        self.assertIn("proj_dist_h1", combined["features"])

    def test_features_follow_the_horizon(self):
        self.assertIn("proj_dist_h4", pr.features_at_horizon(4))
        self.assertNotIn("proj_dist_h1", pr.features_at_horizon(4))
        with self.assertRaises(ValueError):
            pr.features_at_horizon(6)


def _script():
    spec = importlib.util.spec_from_file_location("projected_reserves_script", REPO / "scripts" / "projected_reserves.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CombinedRowTests(unittest.TestCase):
    """The combined row is #539's hurdle with this model as the every-day hazard."""

    @classmethod
    def setUpClass(cls):
        cls.script = _script()

    def test_a_risk_date_is_a_non_ordinary_day_or_at_h1_a_coupon_settlement(self):
        ordinary = {"days_to_month_end": 12.0, "quarter_end": 0.0, "tax_date": 0.0, "treasury_settlement_coupons": 0.0}
        self.assertFalse(self.script.is_risk_date(ordinary, 1, SPLITS))
        self.assertTrue(self.script.is_risk_date({**ordinary, "tax_date": 1.0}, 3, SPLITS))
        coupons = {**ordinary, "treasury_settlement_coupons": 40.0}
        self.assertTrue(self.script.is_risk_date(coupons, 1, SPLITS))
        # the scored day's own settlement is not public at h >= 2, so the passer does not serve it
        self.assertFalse(self.script.is_risk_date(coupons, 2, SPLITS))

    def test_the_passers_forecast_is_kept_on_a_risk_date_even_at_zero_and_the_model_serves_the_rest(self):
        parent = {"5": {"a": 0.3, "b": 0.0, "c": 0.0}}
        mine = {"5": {"a": 0.1, "b": 0.2, "c": 0.4}}
        out = self.script.combine(parent, mine, {"a": True, "b": True, "c": False})
        self.assertEqual(out["5"], {"a": 0.3, "b": 0.0, "c": 0.4})

    def test_a_passer_forecasting_above_zero_off_a_risk_date_is_refused(self):
        with self.assertRaises(SystemExit):
            self.script.combine({"5": {"a": 0.3}}, {"5": {"a": 0.1}}, {"a": False})


def _require_extra(case):
    if all(importlib.util.find_spec(n) is not None for n in ("numpy", "sklearn")):
        return
    if os.environ.get(REQUIRE_ML):
        case.fail(f"{REQUIRE_ML} is set but the optional 'ml' extra is not importable")
    case.skipTest("the optional 'ml' extra is not installed")


class PredictorTests(_Measured):
    def setUp(self):
        _require_extra(self)
        super().setUp()
        # pressure the day after a large projected shortfall: reserves projected low
        self.rows = _panel(400)
        for index, row in enumerate(self.rows):
            if index % 9 == 4:
                row.values["net_settlement_ahead_1d"] = 400.0
            else:
                row.values["net_settlement_ahead_1d"] = 0.0
            row.values["on_rrp"] = 5.0

    def test_it_forecasts_every_day_and_finds_the_planted_pressure(self):
        from repo_model import ml
        from repo_model.baseline import rolling_exceedance_backtest

        built = pr.build_columns(self.rows, self.rule(), last_day=date(2025, 12, 31))
        features = pr.features_at_horizon(1)
        predictor = ml.pressure_logistic_exceedance(features, SPLITS, minimum_history=61)
        with scarcity.measurement_declaration():
            report = rolling_exceedance_backtest(
                built, predictor=predictor, model_name="projected_reserves", features=features,
                registry=self.registry, decision_time=time(16, 0), taus=(5.0,), minimum_history=61,
                refit_every=21, horizon=1,
            )
        self.assertTrue(report.scored_dates)
        self.assertTrue(all(0.0 < p[0] < 1.0 for p in report.forecast))


if __name__ == "__main__":
    unittest.main()
