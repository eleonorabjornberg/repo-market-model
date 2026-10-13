"""A time-varying satiation level for the reserve-demand terms (#587, ruling on #569): `repo_model.satiation`.

The structural (#542), projected-reserves (#545) and combined (#563) models place reserves on a demand curve whose
kink is the fixed 0.12. Two ways to set the level from past data only are measured: a rolling low quantile of the
as-of reserves ratio (`rolling`), and a kink fitted on each refit's training pairs (`fitted`). What is covered:

* `QuantileTests`, `HingeTests` -- the arithmetic.
* `RollingLevelTests` -- the rolling level is the declared quantile of the trailing window, the fixed 0.12 until
  the declared minimum, absent when the row has no ratio, and **reads no row after its own** (the criterion).
* `FitLevelTests` -- the fitted kink recovers a planted one, and falls back to 0.12 on too few pairs or a wrong slope.
* `BuildTests` and `NoFutureTests` -- the panel column on a panel read through the as-of rule, and the guard that
  refuses a level built from a later row.
* `DesignTests` -- the structural design under each form: `fixed` is the model as scored, `rolling` reads the level
  column, `fitted` returns a raw row that `finish` completes at the refit's level.
* `DeclarationTests` -- `metadata/satiation_587.json`, the source entry and the judge's candidate files say what the
  module computes, and the column is off in the published feature map.
* `PredictorTests` -- the three models under each form, under the fold loop's guards: a fitted level at a refit is
  unmoved by rows after that refit's training end.

**Recorded mutations** (disposable copy of the tree, `/opt/rmm-venv`, `PYTHONDONTWRITEBYTECODE=1`, the killing test run
alone, each confirmed applied by `grep` and restored before the next):

1. `rolling_level`: replace `ratios[max(0, i - window + 1): i + 1]` by `ratios[max(0, i - window + 1): i + 2]`. The
   level at row `i` then reads row `i + 1`'s ratio; `RollingLevelTests.test_a_later_ratio_does_not_move_an_earlier_level`
   fails with `AssertionError: 0.1302 != 9.0` (two other `RollingLevelTests` fail too).
2. `structural_exceedance.fit_predict` (fitted form): replace `fit_level([x[1] for x in xs], spreads)` by
   `fit_level([x[1] for x in xs] + [x[1] for x in served], list(spreads) + [0.0] * len(served))`. The refit's level then
   reads the rows it forecasts, which are after its training end;
   `PredictorTests.test_a_fitted_level_is_unmoved_by_rows_after_the_training_end` fails with `AssertionError: 0.1425 != 0.14`.
3. `check_no_future`: replace `if (have is None) != (want is None) or (have is not None and abs(have - want) > 1e-12):` by
   `if False:`. A level that differs from the cut panel's is no longer refused;
   `NoFutureTests.test_a_level_that_differs_from_the_cut_panels_is_refused` fails with `AssertionError: LookAheadError not raised`.
4. (#626) `structural_exceedance.fit_predict` (the same line, now reached by `kinked_fitted` through `design.level_source`): the
   same replacement as 2. `PredictorTests.test_a_kinked_fitted_level_is_unmoved_by_rows_after_the_training_end` fails with
   `AssertionError: 0.1425 != 0.14`.

The kinked elasticity of #626 is covered by `DesignTests` (`test_the_kinked_elasticity_is_flat_above_the_level_and_exponential_below_it`,
`test_kinked_forms_read_what_their_level_source_reads`, `test_a_constant_level_changes_the_kinked_columns`) and by
`PredictorTests.test_a_fitted_level_changes_the_kinked_forecasts_and_not_the_unkinked_ones`; `metadata/kinked_626.json` by
`tests/test_kinked_626.py`.
"""

from __future__ import annotations

import importlib.util
import json
import os
import unittest
from datetime import date, time, timedelta
from pathlib import Path
from types import MappingProxyType
from unittest import mock

from repo_model import contract, measurement_fields, net_settlement as ns, projected_reserves as pr, satiation as sat, scarcity
from repo_model import structural_liquidity as sl
from repo_model.asof import InformationRule
from repo_model.data import CALENDAR_COLUMN_RULES, DailyObservation, next_business_day
from repo_model.evaluation_splits import load_split_declaration
from repo_model.splits import LookAheadError

REPO = Path(__file__).resolve().parents[1]
SPLITS = load_split_declaration(REPO / "metadata" / "evaluation_splits.json")
DECLARATION = REPO / "metadata" / "satiation_587.json"
REQUIRE_ML = "REPO_MODEL_REQUIRE_ML"


class QuantileTests(unittest.TestCase):
    def test_linear_interpolation_between_order_statistics(self):
        self.assertAlmostEqual(sat.quantile([4.0, 1.0, 3.0, 2.0], 0.0), 1.0)
        self.assertAlmostEqual(sat.quantile([4.0, 1.0, 3.0, 2.0], 1.0), 4.0)
        self.assertAlmostEqual(sat.quantile([4.0, 1.0, 3.0, 2.0], 0.5), 2.5)
        self.assertAlmostEqual(sat.quantile([1.0, 2.0, 3.0, 4.0, 5.0], 0.1), 1.4)

    def test_an_empty_sample_or_a_bad_level_is_refused(self):
        with self.assertRaises(ValueError):
            sat.quantile([], 0.5)
        with self.assertRaises(ValueError):
            sat.quantile([1.0], 1.5)


class HingeTests(unittest.TestCase):
    def test_zero_at_and_above_the_level_and_percentage_points_below(self):
        self.assertEqual(sat.hinge(0.12, 0.12), 0.0)
        self.assertEqual(sat.hinge(0.15, 0.12), 0.0)
        self.assertAlmostEqual(sat.hinge(0.10, 0.12), 2.0)

    def test_the_fixed_level_is_the_published_bands_lower_end(self):
        self.assertEqual(sat.FIXED, scarcity.SATIATION_BAND[0])


class RollingLevelTests(unittest.TestCase):
    def ratios(self, n=200):
        return [0.10 + 0.0002 * k for k in range(n)]

    def test_the_level_is_the_declared_quantile_of_the_trailing_window(self):
        ratios = self.ratios()
        level = sat.rolling_level(ratios, 150, q=0.1, window=100, minimum=63)
        self.assertAlmostEqual(level, sat.quantile(ratios[51:151], 0.1))

    def test_the_window_is_the_rows_up_to_and_including_the_decision(self):
        ratios = self.ratios()
        self.assertAlmostEqual(sat.rolling_level(ratios, 99, q=0.0, window=100, minimum=63), ratios[0])
        self.assertAlmostEqual(sat.rolling_level(ratios, 100, q=0.0, window=100, minimum=63), ratios[1])

    def test_the_fixed_level_until_the_minimum_exists(self):
        ratios = self.ratios()
        self.assertEqual(sat.rolling_level(ratios, 61, minimum=63), sat.FIXED)
        self.assertNotEqual(sat.rolling_level(ratios, 62, minimum=63), sat.FIXED)

    def test_a_hole_in_the_window_is_skipped_and_a_hole_at_the_row_is_no_level(self):
        ratios = self.ratios()
        ratios[100] = None
        self.assertIsNotNone(sat.rolling_level(ratios, 120))
        self.assertIsNone(sat.rolling_level(ratios, 100))

    def test_a_later_ratio_does_not_move_an_earlier_level(self):
        ratios = self.ratios()
        changed = ratios[:151] + [9.0] * 49
        for q in (0.0, 0.1, 0.5, 1.0):
            self.assertEqual(
                sat.rolling_level(ratios, 150, q=q, window=100), sat.rolling_level(changed, 150, q=q, window=100)
            )


class FitLevelTests(unittest.TestCase):
    def pairs(self, kink=0.11, n=400, noise=0.0):
        ratios = [0.09 + 0.06 * ((k * 37) % 100) / 100.0 for k in range(n)]
        spreads = [-1.0 + 400.0 * max(0.0, kink - r) + noise * (((k * 53) % 7) - 3) for k, r in enumerate(ratios)]
        return ratios, spreads

    def test_a_planted_kink_is_recovered(self):
        ratios, spreads = self.pairs(0.11)
        level, record = sat.fit_level(ratios, spreads)
        self.assertTrue(record["fitted"])
        self.assertAlmostEqual(level, 0.11, places=3)
        self.assertGreater(record["slope"], 0.0)

    def test_the_kink_moves_with_the_data(self):
        low = sat.fit_level(*self.pairs(0.10))[0]
        high = sat.fit_level(*self.pairs(0.13))[0]
        self.assertLess(low, high)

    def test_too_few_pairs_is_the_fixed_level(self):
        ratios, spreads = self.pairs(0.11, n=sat.KINK_MINIMUM_PAIRS - 1)
        level, record = sat.fit_level(ratios, spreads)
        self.assertEqual(level, sat.FIXED)
        self.assertFalse(record["fitted"])

    def test_spreads_that_fall_as_reserves_fall_give_the_fixed_level(self):
        ratios, spreads = self.pairs(0.11)
        level, record = sat.fit_level(ratios, [-s for s in spreads])
        self.assertEqual(level, sat.FIXED)
        self.assertFalse(record["fitted"])

    def test_one_spread_per_ratio(self):
        with self.assertRaises(ValueError):
            sat.fit_level([0.1, 0.2], [1.0])


def _panel(count=330):
    """Business days from 2023-01-03; reserves step weekly through ratios 0.10 to 0.16; assets constant."""

    days = [date(2023, 1, 3)]
    while len(days) < count:
        days.append(next_business_day(days[-1], 1))
    rows = []
    for index, day in enumerate(days):
        calendar = {n: float(rule(day)) for n, rule in CALENDAR_COLUMN_RULES.items()
                    if n in ("days_to_month_end", "quarter_end", "tax_date")}
        wednesday = day - timedelta(days=(day.weekday() - 2) % 7)
        week = (wednesday - date(2023, 1, 4)).days // 7
        ratio = 0.10 + 0.006 * ((week * 7) % 11)
        settle = 120.0 if index % 9 == 4 else 5.0 * (index % 3)
        spread = 8.0 if index % 9 == 5 else -1.0 + 0.1 * (index % 3)
        rows.append(DailyObservation(day, {
            "sofr": 4.0 + spread / 100.0, "iorb": 4.0, "sofr_volume": 2100.0 + index % 11,
            "reserve_balances": 26000.0 * ratio, "bank_total_assets": 26000.0,
            "on_rrp": 20.0 + index % 3, "tga": 700.0 + 25.0 * ((week * 7) % 5), "tga_daily": 700.0 + 2.0 * index % 40,
            "tga_daily_change": 2.0 if index % 40 else -78.0, "net_settlement": settle,
            **{f"net_settlement_ahead_{k}d": k * (5.0 + index % 7) for k in range(1, 6)},
            "net_settlement_due_5d": settle, **calendar,
        }))
    return rows


class _Measured(unittest.TestCase):
    def setUp(self):
        fields = {**measurement_fields.COLUMN_FIELDS, **ns.COLUMN_FIELDS, **pr.COLUMN_FIELDS, **sat.COLUMN_FIELDS}
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
        return InformationRule(self.registry, sat.READ_FEATURES, decision_time=time(16, 0), horizon=1)

    def built(self, rows=None):
        return sat.build_columns(
            self.rows if rows is None else rows, self.rule(), last_day=date(2025, 12, 31), q=0.1, window=100, minimum=20
        )


class BuildTests(_Measured):
    def test_the_column_is_the_quantile_of_the_ratios_the_rule_reads(self):
        ratios = sat.asof_ratios(self.rows, self.rule(), last_day=date(2025, 12, 31))
        out = self.built()
        self.assertIsNotNone(ratios[200])
        self.assertAlmostEqual(out[200].values[sat.ROLLING_COLUMN], sat.quantile([r for r in ratios[101:201] if r is not None], 0.1))

    def test_each_leg_is_read_at_its_own_latest_public_row(self):
        ratios = sat.asof_ratios(self.rows, self.rule(), last_day=date(2025, 12, 31))
        info = self.rule().information_set(pr.extended_dates([r.date for r in self.rows], 200), 201)
        read = {r.feature: r.row for r in info.reads}
        expect = self.rows[read["reserve_balances"]].values["reserve_balances"] / self.rows[read["bank_total_assets"]].values["bank_total_assets"]
        self.assertAlmostEqual(ratios[200], expect)

    def test_a_day_after_the_last_scored_day_has_no_level(self):
        out = sat.build_columns(self.rows, self.rule(), last_day=self.rows[150].date)
        self.assertIsNone(out[151].values[sat.ROLLING_COLUMN])
        self.assertIsNotNone(out[150].values[sat.ROLLING_COLUMN])

    def test_a_later_rows_values_do_not_move_an_earlier_level(self):
        full = self.built()
        changed = [DailyObservation(r.date, dict(r.values)) for r in self.rows]
        for later in changed[201:]:
            later.values["reserve_balances"] = 9999.0
        again = self.built(changed)
        self.assertEqual(full[200].values[sat.ROLLING_COLUMN], again[200].values[sat.ROLLING_COLUMN])


class NoFutureTests(_Measured):
    """The guard that refuses a level built from a row after its own decision.

    Recorded mutation (#587): in `check_no_future`, the comparison `if (have is None) != (want is None) or ...` -> `if False:`;
    `test_a_level_that_differs_from_the_cut_panels_is_refused` then fails with `AssertionError: LookAheadError not raised`.
    """

    def test_the_levels_pass_when_they_use_nothing_later(self):
        sat.check_no_future(
            self.rows, self.built(), self.rule(), last_day=date(2025, 12, 31), indices=range(60, 120, 15), q=0.1, window=100, minimum=20
        )

    def test_a_level_that_differs_from_the_cut_panels_is_refused(self):
        out = self.built()
        bent = [DailyObservation(r.date, dict(r.values)) for r in out]
        bent[100].values[sat.ROLLING_COLUMN] += 0.01
        with self.assertRaises(LookAheadError):
            sat.check_no_future(
                self.rows, bent, self.rule(), last_day=date(2025, 12, 31), indices=[100], q=0.1, window=100, minimum=20
            )

    def test_a_level_built_from_a_later_row_is_refused(self):
        # a builder that carries the next row's ratio as the level: it differs from the cut panel's wherever a release lands
        ratios = sat.asof_ratios(self.rows, self.rule(), last_day=date(2025, 12, 31))
        leaked = []
        for i, row in enumerate(self.rows):
            values = dict(row.values)
            ahead = min(i + 1, len(ratios) - 1)
            values[sat.ROLLING_COLUMN] = ratios[ahead]
            leaked.append(DailyObservation(row.date, values))
        with self.assertRaises(LookAheadError):
            sat.check_no_future(
                self.rows, leaked, self.rule(), last_day=date(2025, 12, 31), indices=range(60, 200, 3), q=0.1, window=100, minimum=20
            )


def _obs(**kw):
    base = {
        "sofr": 4.0, "iorb": 4.0, "reserve_balances": 3000.0, "bank_total_assets": 26000.0, "on_rrp": 50.0,
        "tga": 700.0, "net_settlement": 80.0, "net_settlement_ahead_1d": 110.0, "net_settlement_due_5d": 150.0,
        "days_to_month_end": 12.0, "quarter_end": 0.0, "tax_date": 0.0,
    }
    base.update(kw)
    return DailyObservation(date(2024, 3, 12), base)


class DesignTests(unittest.TestCase):
    def test_fixed_is_the_model_as_scored(self):
        features = sl.features_at_horizon(1)
        old = sl.StructuralDesign(features, SPLITS).row(_obs(), 12.0)
        self.assertEqual(old, sl.StructuralDesign(features, SPLITS, "fixed").row(_obs(), 12.0))
        e = sl.elasticity(3000.0 / 26000.0)
        self.assertAlmostEqual(old[1], e * 60.0)

    def test_rolling_reads_the_level_column(self):
        features = sl.features_at_horizon(1, "rolling")
        self.assertIn(sat.ROLLING_COLUMN, features)
        design = sl.StructuralDesign(features, SPLITS, "rolling")
        e = sl.elasticity(3000.0 / 26000.0, 0.10)
        row = design.row(_obs(**{sat.ROLLING_COLUMN: 0.10}), 12.0)
        self.assertAlmostEqual(row[1], e * 60.0)
        self.assertAlmostEqual(row[2], e * 12.0)

    def test_rolling_refuses_a_missing_level_or_an_undeclared_column(self):
        design = sl.StructuralDesign(sl.features_at_horizon(1, "rolling"), SPLITS, "rolling")
        with self.assertRaises(ValueError):
            design.row(_obs(), 12.0)
        with self.assertRaises(ValueError):
            sl.StructuralDesign(sl.features_at_horizon(1), SPLITS, "rolling")

    def test_fitted_is_raw_until_the_level_is_known(self):
        design = sl.StructuralDesign(sl.features_at_horizon(1), SPLITS, "fitted")
        raw = design.row(_obs(), 12.0)
        self.assertEqual(len(raw), len(sl.RAW_NAMES))
        self.assertAlmostEqual(raw[1], 3000.0 / 26000.0)
        done = design.finish(raw, 0.11)
        e = sl.elasticity(3000.0 / 26000.0, 0.11)
        self.assertAlmostEqual(done[1], e * 60.0)
        self.assertEqual(len(done), len(sl.COLUMN_NAMES))

    def test_a_constant_level_only_rescales_the_elasticity_columns(self):
        # e = exp(-(ratio - level) / L) = exp(-(ratio - 0.12) / L) * exp((level - 0.12) / L): one level for a whole refit
        # multiplies the four elasticity terms by one constant, which the logistic's standardisation removes. The
        # `fitted` form is therefore the same model as `fixed` for the structural terms (a finding of #587).
        design = sl.StructuralDesign(sl.features_at_horizon(1), SPLITS, "fitted")
        raws = [design.row(_obs(reserve_balances=26000.0 * r, net_settlement_ahead_1d=60.0 + 90.0 * k), 5.0 + k)
                for k, r in enumerate((0.09, 0.11, 0.13, 0.15))]
        low = [design.finish(raw, 0.10) for raw in raws]
        high = [design.finish(raw, 0.14) for raw in raws]
        factor = None
        for a, b in zip(low, high):
            for x, y in zip(a[1:3], b[1:3]):
                if x > 0.0:
                    factor = factor or y / x
                    self.assertAlmostEqual(y / x, factor, places=9)
        self.assertAlmostEqual(factor, sl.math.exp((0.14 - 0.10) / sl.LENGTH))

    def test_the_kinked_elasticity_is_flat_above_the_level_and_exponential_below_it(self):
        # #626: e = 1 at and above the level, exp((level - ratio) / L) below it (the sign of the exponent is the unkinked
        # curve's: the elasticity grows as reserves fall below satiation)
        self.assertEqual(sl.elasticity(0.15, 0.12, kinked=True), 1.0)
        self.assertEqual(sl.elasticity(0.12, 0.12, kinked=True), 1.0)
        self.assertEqual(sl.elasticity(0.30, 0.12, kinked=True), 1.0)
        self.assertAlmostEqual(sl.elasticity(0.11, 0.12, kinked=True), sl.math.e, places=12)
        self.assertAlmostEqual(sl.elasticity(0.10, 0.12, kinked=True), sl.math.exp(2.0), places=12)
        # below the level it is the unkinked curve; above it the unkinked curve is below 1 and the kinked one is 1
        self.assertAlmostEqual(sl.elasticity(0.10, 0.12, kinked=True), sl.elasticity(0.10, 0.12), places=12)
        self.assertLess(sl.elasticity(0.15, 0.12), 1.0)
        self.assertEqual(sl.elasticity(0.15, 0.12), sl.elasticity(0.15, 0.12, kinked=False))

    def test_kinked_forms_read_what_their_level_source_reads(self):
        self.assertEqual(sl.features_at_horizon(1, "kinked_fitted"), sl.features_at_horizon(1))
        self.assertEqual(sl.features_at_horizon(1, "kinked_rolling"), sl.features_at_horizon(1, "rolling"))
        design = sl.StructuralDesign(sl.features_at_horizon(1, "kinked_rolling"), SPLITS, "kinked_rolling")
        row = design.row(_obs(**{sat.ROLLING_COLUMN: 0.10}), 12.0)
        self.assertAlmostEqual(row[1], 1.0 * 60.0)  # ratio 3000 / 26000 = 0.1154 is above the level 0.10: e = 1
        low = design.row(_obs(reserve_balances=26000.0 * 0.09, **{sat.ROLLING_COLUMN: 0.10}), 12.0)
        self.assertAlmostEqual(low[1], sl.math.exp(1.0) * 60.0)
        with self.assertRaises(ValueError):
            design.row(_obs(), 12.0)
        with self.assertRaises(ValueError):
            sl.StructuralDesign(sl.features_at_horizon(1), SPLITS, "kinked_rolling")
        fitted = sl.StructuralDesign(sl.features_at_horizon(1), SPLITS, "kinked_fitted")
        raw = fitted.row(_obs(), 12.0)
        self.assertEqual(len(raw), len(sl.RAW_NAMES))
        done = fitted.finish(raw, 0.13)
        self.assertAlmostEqual(done[1], sl.elasticity(3000.0 / 26000.0, 0.13, kinked=True) * 60.0)

    def test_a_constant_level_changes_the_kinked_columns(self):
        # #626, the opposite of test_a_constant_level_only_rescales_the_elasticity_columns: with the kink, a constant level
        # no longer multiplies the elasticity terms by one constant. Rows above both levels keep e = 1 while rows between
        # them do not, so the columns' shape moves and the logistic's standardisation does not remove it.
        design = sl.StructuralDesign(sl.features_at_horizon(1), SPLITS, "kinked_fitted")
        raws = [design.row(_obs(reserve_balances=26000.0 * r, net_settlement_ahead_1d=60.0 + 90.0 * k), 5.0 + k)
                for k, r in enumerate((0.09, 0.11, 0.13, 0.15))]
        low = [design.finish(raw, 0.10)[1] for raw in raws]
        high = [design.finish(raw, 0.14)[1] for raw in raws]
        ratios = [h / l for h, l in zip(high, low)]
        self.assertGreater(max(ratios) - min(ratios), 1.0)
        # the unkinked columns of the same rows differ by one constant
        plain = sl.StructuralDesign(sl.features_at_horizon(1), SPLITS, "fitted")
        plain_ratios = [plain.finish(raw, 0.14)[1] / plain.finish(raw, 0.10)[1] for raw in raws]
        self.assertAlmostEqual(max(plain_ratios), min(plain_ratios), places=9)

    def test_an_unknown_form_is_refused(self):
        with self.assertRaises(ValueError):
            sl.StructuralDesign(sl.features_at_horizon(1), SPLITS, "kinked")
        with self.assertRaises(ValueError):
            sl.features_at_horizon(1, "kinked")


class DeclarationTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(DECLARATION.read_text())

    def test_the_declaration_says_what_the_module_computes(self):
        rolling = self.document["forms"]["rolling"]
        self.assertEqual(rolling["quantile"], sat.ROLLING_QUANTILE)
        self.assertEqual(rolling["window_rows"], sat.ROLLING_WINDOW)
        self.assertEqual(rolling["minimum_rows"], sat.ROLLING_MINIMUM)
        fitted = self.document["forms"]["fitted"]
        self.assertEqual(fitted["grid"], [min(sat.KINK_GRID), max(sat.KINK_GRID), 0.0025])
        self.assertEqual(fitted["minimum_pairs"], sat.KINK_MINIMUM_PAIRS)
        self.assertEqual(self.document["fixed_level"], sat.FIXED)
        self.assertEqual(tuple(self.document["forms_scored"]), ("rolling", "fitted"))

    def test_the_registry_declares_the_column_with_no_lag(self):
        registry = json.loads((REPO / "metadata" / "sources_measurement.json").read_text())
        entry = registry[sat.SOURCE_ID]
        self.assertEqual(entry["fields"], [sat.ROLLING_COLUMN])
        self.assertEqual(entry["release_lag"]["days"], 0)
        self.assertEqual(sorted(sat.COLUMN_FIELDS), [sat.ROLLING_COLUMN])

    def test_the_column_is_off_in_the_published_feature_map(self):
        self.assertNotIn(sat.ROLLING_COLUMN, contract.FEATURE_FIELDS)

    def test_the_candidate_files_exist_for_every_new_row(self):
        base = REPO / "metadata" / "pressure_judge" / "candidates"
        for name in self.document["rows"]["new"]:
            entry = json.loads((base / f"{name}.json").read_text())
            self.assertEqual(entry["role"], "candidate", name)
            self.assertIn("spread_bps", entry["features"], name)
        for name in self.document["rows"]["controls"]:
            self.assertTrue((base / f"{name}.json").exists(), name)

    def test_the_published_indicator_and_its_band_are_unchanged(self):
        self.assertEqual(scarcity.SATIATION_BAND, (0.12, 0.13))
        self.assertEqual(sl.SATIATION, 0.12)
        self.assertEqual(pr.SATIATION, 0.12)


def _require_extra(case):
    if all(importlib.util.find_spec(n) is not None for n in ("numpy", "sklearn")):
        return
    if os.environ.get(REQUIRE_ML):
        case.fail(f"{REQUIRE_ML} is set but the optional 'ml' extra is not importable")
    case.skipTest("the optional 'ml' extra is not installed")


class PredictorTests(_Measured):
    """The three models under each form, under the fold loop's guards, on a panel whose pressure follows a planted kink."""

    def setUp(self):
        _require_extra(self)
        super().setUp()
        self.rows = _panel(700)
        blocks = (0.095, 0.15, 0.105, 0.14, 0.11, 0.16, 0.10, 0.145, 0.115, 0.155, 0.1, 0.15)
        for index, row in enumerate(self.rows):
            # the reserves ratio stays in a block of 55 rows, so the as-of lag moves it by a few days only;
            # pressure every fourth day while it is below 0.12, and never otherwise
            ratio = blocks[(index // 55) % len(blocks)]
            row.values["reserve_balances"] = 26000.0 * ratio
            row.values["net_settlement_ahead_1d"] = 300.0 if index % 4 == 0 else 0.0
            row.values["on_rrp"] = 5.0
            row.values["sofr"] = 4.0 + (8.0 if (index % 4 == 1 and ratio < 0.12) else -1.0) / 100.0

    def with_column(self, rows=None):
        return sat.build_columns(
            self.rows if rows is None else rows, self.rule(), last_day=date(2025, 12, 31), q=0.1, window=100, minimum=20
        )

    def structural(self, form, rows=None):
        features = sl.features_at_horizon(1, form)
        predictor = sl.structural_exceedance(features, SPLITS, minimum_history=61, satiation=form)
        from repo_model.baseline import rolling_exceedance_backtest

        with scarcity.measurement_declaration():
            report = rolling_exceedance_backtest(
                self.with_column(rows), predictor=predictor, model_name="structural_" + form, features=features,
                registry=self.registry, decision_time=time(16, 0), taus=(5.0,), minimum_history=61, refit_every=21, horizon=1,
            )
        return report, predictor

    def test_every_form_forecasts_every_day(self):
        for form in sl.STRUCTURAL_FORMS:
            report, _ = self.structural(form)
            self.assertTrue(report.scored_dates, form)
            self.assertTrue(all(0.0 < p[0] < 1.0 for p in report.forecast), form)

    def test_a_fitted_level_is_recorded_per_refit_and_lies_on_the_grid(self):
        _report, predictor = self.structural("fitted")
        levels = [f["satiation_level"] for f in predictor.fits]
        self.assertTrue(levels)
        self.assertTrue(all(min(sat.KINK_GRID) - 1e-9 <= v <= max(sat.KINK_GRID) + 1e-9 for v in levels))
        # the planted pressure sits below 0.12 and none above 0.14: a level was fitted, not defaulted
        self.assertNotEqual(levels[-1], sat.FIXED)
        # the first refits have fewer pairs than the minimum: the fixed level
        self.assertEqual(levels[0], sat.FIXED)
        self.assertFalse(predictor.fits[0]["fitted"])
        self.assertTrue(predictor.fits[-1]["fitted"])

    def test_a_fitted_level_is_unmoved_by_rows_after_the_training_end(self):
        _report, predictor = self.structural("fitted")
        first = next(f for f in predictor.fits if f["fitted"])
        end = [r.date.isoformat() for r in self.rows].index(first["last_training_row"])
        changed = [DailyObservation(r.date, dict(r.values)) for r in self.rows]
        for later in changed[end + 1:]:
            later.values["sofr"] = 4.0 + 0.30
            later.values["reserve_balances"] = 26000.0 * 0.20
        _report2, predictor2 = self.structural("fitted", changed)
        again = next(f for f in predictor2.fits if f["last_training_row"] == first["last_training_row"])
        self.assertTrue(again["fitted"])
        self.assertEqual(first["satiation_level"], again["satiation_level"])
        self.assertEqual(first["pairs"], again["pairs"])

    def test_a_fitted_level_changes_the_kinked_forecasts_and_not_the_unkinked_ones(self):
        # #626: the same constant levels, forced at every refit. Unkinked, the forecasts agree to rounding (the finding of
        # #587); kinked, the level moves them.
        def forecasts(form, level):
            with mock.patch.object(sl, "fit_level", lambda ratios, spreads, **kw: (level, {"fitted": True, "pairs": len(ratios)})):
                report, _ = self.structural(form)
            return [p[0] for p in report.forecast]

        plain_low, plain_high = forecasts("fitted", 0.10), forecasts("fitted", 0.14)
        self.assertLess(max(abs(a - b) for a, b in zip(plain_low, plain_high)), 1e-6)
        kink_low, kink_high = forecasts("kinked_fitted", 0.10), forecasts("kinked_fitted", 0.14)
        self.assertGreater(max(abs(a - b) for a, b in zip(kink_low, kink_high)), 1e-3)

    def test_a_kinked_fitted_level_is_unmoved_by_rows_after_the_training_end(self):
        _report, predictor = self.structural("kinked_fitted")
        first = next(f for f in predictor.fits if f["fitted"])
        end = [r.date.isoformat() for r in self.rows].index(first["last_training_row"])
        changed = [DailyObservation(r.date, dict(r.values)) for r in self.rows]
        for later in changed[end + 1:]:
            later.values["sofr"] = 4.0 + 0.30
            later.values["reserve_balances"] = 26000.0 * 0.20
        _report2, predictor2 = self.structural("kinked_fitted", changed)
        again = next(f for f in predictor2.fits if f["last_training_row"] == first["last_training_row"])
        self.assertTrue(again["fitted"])
        self.assertEqual(first["satiation_level"], again["satiation_level"])

    def test_the_projected_hinge_model_under_each_form(self):
        from repo_model import ml

        for form in ("fixed_kink", "rolling", "fitted"):
            features = list(pr.features_at_horizon(1)) + ([sat.ROLLING_COLUMN] if form == "rolling" else [])
            predictor = ml.pressure_projected_hinge_exceedance(features, SPLITS, minimum_history=61, horizon=1, satiation=form)
            from repo_model.baseline import rolling_exceedance_backtest

            built = pr.build_columns(self.with_column(), self.rule_with_projection(), last_day=date(2025, 12, 31))
            with scarcity.measurement_declaration():
                report = rolling_exceedance_backtest(
                    built, predictor=predictor, model_name="projected_" + form, features=features,
                    registry=self.registry, decision_time=time(16, 0), taus=(5.0,), minimum_history=61, refit_every=21, horizon=1,
                )
            self.assertTrue(report.scored_dates, form)
            self.assertTrue(all(0.0 < p[0] < 1.0 for p in report.forecast), form)

    def rule_with_projection(self):
        return InformationRule(self.registry, pr.READ_FEATURES, decision_time=time(16, 0), horizon=1)

    def test_the_projected_hinge_keeps_the_level_after_standardisation(self):
        from repo_model import ml

        design = ml._ProjectedHingeDesign(("spread_bps", "proj_dist_h1", "proj_change_h1"), SPLITS, 1, "fixed_kink")
        above = design.row(_obs(proj_dist_h1=3.0, proj_change_h1=0.1), None)
        below = design.row(_obs(proj_dist_h1=-2.0, proj_change_h1=0.1), None)
        self.assertEqual(above[4], 0.0)
        self.assertAlmostEqual(below[4], 2.0)
        with self.assertRaises(ValueError):
            ml._ProjectedHingeDesign(("spread_bps", "proj_dist_h1", "proj_change_h1"), SPLITS, 1, "fixed")

    def test_the_combined_design_under_each_form(self):
        from repo_model import ml

        features = tuple(sl.features_at_horizon(1, "rolling")) + ("proj_dist_h1",)
        blocks = ("structural", "projected")
        obs = _obs(proj_dist_h1=-2.0, **{sat.ROLLING_COLUMN: 0.11})
        fixed = ml._CombinedDesign(features, SPLITS, blocks, "fixed").row(obs, 12.0)
        self.assertAlmostEqual(fixed[-1], -2.0)
        kink = ml._CombinedDesign(features, SPLITS, blocks, "fixed_kink").row(obs, 12.0)
        self.assertAlmostEqual(kink[-1], 2.0)
        self.assertAlmostEqual(kink[1], fixed[1])
        rolling = ml._CombinedDesign(features, SPLITS, blocks, "rolling").row(obs, 12.0)
        self.assertAlmostEqual(rolling[-1], 100.0 * (0.11 - (-2.0 / 100.0 + 0.12)))
        self.assertAlmostEqual(rolling[1], sl.elasticity(3000.0 / 26000.0, 0.11) * 60.0)
        fitted = ml._CombinedDesign(features, SPLITS, blocks, "fitted")
        raw = fitted.row(obs, 12.0)
        self.assertAlmostEqual(raw[-1], -2.0 / 100.0 + 0.12)
        done = fitted.finish(raw, 0.11)
        self.assertEqual(len(done), len(rolling))
        self.assertAlmostEqual(done[-1], 100.0 * (0.11 - (-2.0 / 100.0 + 0.12)))
        self.assertAlmostEqual(done[1], rolling[1])


if __name__ == "__main__":
    unittest.main()
