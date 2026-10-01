"""#27: the pressure-probability benchmarks, and the splits every result carries.

Directive 03 (`docs/pivot/directives/03-rescore-publish.md`) and
`docs/decisions/pressure-probability.md`: every pressure probability is compared,
paired and with a stationary-bootstrap interval, against two benchmarks --
calendar-type climatology and a persistence-logistic model -- and every result is
split by regime and by pressure-day type. Neither benchmark existed, nor did any
split.

Written first and watched failing on `origin/main` (`cd3915f`): the module failed to
import, `ImportError: cannot import name 'month_end' from 'repo_model.data'`, and
once `data.month_end` and `strata` existed, on `ImportError: cannot import name
'calendar_climatology_exceedance' from 'repo_model.baseline'`.

The panels here are weekday panels in 2025-26 read under the tracked registry,
as in `tests/test_asof.py`, so every as-of read is the one the published runs make.
"""

from __future__ import annotations

import json
import math
import tempfile
import unittest
from datetime import date, time, timedelta
from pathlib import Path

from repo_model import strata
from repo_model.asof import InformationRule
from repo_model.baseline import (
    ExceedanceCurves,
    backtest_document,
    calendar_climatology_exceedance,
    climatology_exceedance,
    exceedance_backtest_document,
    fit,
    fit_penalised_logistic,
    paired_comparison_document,
    paired_model_comparison,
    persistence_logistic_exceedance,
    rolling_exceedance_backtest,
    rolling_persistence_backtest,
)
from repo_model.data import DailyObservation, month_end

from test_baseline import EXCEEDANCE_TAUS, ExceedancePredictorConformance

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "metadata" / "sources.json"
THRESHOLDS_PATH = ROOT / "metadata" / "stress_thresholds.json"
REGISTRY = json.loads(REGISTRY_PATH.read_text())
DECISION = time(16, 0)


def weekdays(start, count):
    out, when = [], start
    while len(out) < count:
        if when.weekday() < 5:
            out.append(when)
        when += timedelta(days=1)
    return out


def pressure_panel(count=140, start=date(2025, 9, 1), seed=20261001):
    """Weekday rows whose spread jumps on month-ends and drifts with its own past.

    The spread is persistent (an AR term) and rises on the last business day of
    each month, so both benchmarks have something to find: persistence-logistic
    the autocorrelation, the calendar climatology the month-end bump. Coupon
    settlements fall on the 15th and the last day of each month's grid.
    """

    rows, state, spread = [], seed, 0.0
    for when in weekdays(start, count):
        state = (1103515245 * state + 12345) % (2 ** 31)
        shock = ((state % 1000) / 1000.0 - 0.5) * 6.0
        spread = 0.6 * spread + shock + (12.0 if month_end(when) else 0.0)
        rows.append(
            DailyObservation(
                when,
                {
                    "sofr": 4.0 + spread / 100.0,
                    "iorb": 4.0,
                    "sofr_volume": 2000.0 + state % 500,
                    "treasury_settlement_coupons": 30.0 if when.day == 15 else 0.0,
                },
            )
        )
    return rows


class MonthEndTests(unittest.TestCase):
    def test_the_last_business_day_of_the_month_by_the_holiday_table(self):
        self.assertEqual(month_end(date(2021, 5, 28)), 1.0)  # 31 May: Memorial Day
        self.assertEqual(month_end(date(2021, 5, 31)), 0.0)
        self.assertEqual(month_end(date(2019, 8, 30)), 1.0)  # 31 Aug: Saturday
        self.assertEqual(month_end(date(2019, 8, 29)), 0.0)
        self.assertEqual(month_end(date(2026, 1, 30)), 1.0)

    def test_a_month_outside_the_table_is_refused(self):
        with self.assertRaises(ValueError):
            month_end(date(2010, 1, 29))


class PressureDayTypeTests(unittest.TestCase):
    def test_the_first_applicable_type_is_taken(self):
        cases = {
            (date(2019, 9, 30), 50.0): "quarter_end",
            (date(2019, 8, 30), 50.0): "month_end",
            (date(2019, 9, 16), 50.0): "tax_window",
            (date(2019, 9, 3), 40.0): "coupon_settlement",
            (date(2019, 9, 3), 0.0): "other",
        }
        for (day, coupons), expected in cases.items():
            with self.subTest(day=day):
                self.assertEqual(strata.pressure_day_type(day, coupons), expected)

    def test_an_unknown_settlement_is_refused_not_typed_as_none(self):
        with self.assertRaises(ValueError):
            strata.pressure_day_type(date(2019, 9, 3), None)
        # A day typed before the settlement is consulted needs none.
        self.assertEqual(strata.pressure_day_type(date(2019, 9, 30), None), "quarter_end")

    def test_the_types_are_directive_06s_five(self):
        self.assertEqual(
            strata.PRESSURE_DAY_TYPES,
            ("quarter_end", "month_end", "tax_window", "coupon_settlement", "other"),
        )


class RegimeTests(unittest.TestCase):
    def test_the_provisional_periods(self):
        self.assertEqual(strata.regime(date(2019, 9, 17)), "2018-19")
        self.assertEqual(strata.regime(date(2020, 3, 16)), "2020")
        self.assertEqual(strata.regime(date(2022, 6, 1)), "2021-23")
        self.assertEqual(strata.regime(date(2024, 12, 31)), "2024")
        self.assertEqual(strata.regime(date(2026, 9, 3)), "2025-26")

    def test_a_day_outside_every_period_is_refused(self):
        with self.assertRaises(ValueError):
            strata.regime(date(2017, 12, 29))

    def test_the_periods_are_contiguous_and_ordered(self):
        for (_a, _first, last), (_b, first, _last) in zip(strata.REGIMES, strata.REGIMES[1:]):
            self.assertEqual(first, last + timedelta(days=1))


class PenalisedLogisticTests(unittest.TestCase):
    """L2 on the slope, C = 1, intercept unpenalised: scikit-learn's default.

    The scouting benchmark (`docs/pivot/scouting/lag_analyze.py`) was
    `LogisticRegression()`. The fit is checked against its optimality
    conditions rather than against scikit-learn, which `src/` may not import.
    """

    XS = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
    YS = [0, 0, 0, 1, 0, 0, 1, 1, 1, 1]

    def test_the_fit_satisfies_its_first_order_conditions(self):
        intercept, slope = fit_penalised_logistic(self.XS, self.YS)
        p = [1.0 / (1.0 + math.exp(-(intercept + slope * x))) for x in self.XS]
        self.assertAlmostEqual(sum(y - q for y, q in zip(self.YS, p)), 0.0, places=9)
        self.assertAlmostEqual(
            sum((y - q) * x for x, y, q in zip(self.XS, self.YS, p)), slope, places=9
        )

    def test_separable_data_still_gives_a_finite_fit(self):
        intercept, slope = fit_penalised_logistic([0.0, 1.0, 2.0, 3.0], [0, 0, 1, 1])
        self.assertTrue(math.isfinite(intercept) and math.isfinite(slope))
        self.assertGreater(slope, 0.0)

    def test_one_class_is_refused(self):
        with self.assertRaises(ValueError):
            fit_penalised_logistic([0.0, 1.0, 2.0], [0, 0, 0])


class PersistenceLogisticExceedanceTests(ExceedancePredictorConformance, unittest.TestCase):
    """The conformance suite against `persistence_logistic_exceedance`."""

    IMPLEMENTATION = staticmethod(persistence_logistic_exceedance)
    RULE = InformationRule(REGISTRY, ("spread_bps",), decision_time=DECISION)

    def frame(self):
        return pressure_panel(count=60)

    def make_predictor(self):
        predictor = persistence_logistic_exceedance(minimum_history=self.MINIMUM_HISTORY)
        return lambda train, features, taus: predictor(
            train, features, taus, information=self.RULE
        )

    def test_it_reads_the_target_and_nothing_else(self):
        self.assertEqual(self.curves().features_read, ("spread_bps",))

    def test_each_label_is_paired_with_the_spread_its_own_decision_read(self):
        """The design is (spread at each label's anchor, label), not (row before, row).

        Under the tracked registry SOFR for day d is final at 15:00 on d + 1,
        so a decision at 16:00 on the day before a scored day reads the spread
        two panel rows back. The expected fit is rebuilt from the rule's
        anchors here and compared with the predictor's curve.
        """

        train, feature_rows = self.split()
        dates = [row.date for row in train]
        tau = EXCEEDANCE_TAUS[0]
        xs, ys = [], []
        for index in range(1, len(train)):
            anchor = self.RULE.anchor(dates, index)
            if anchor < 0:
                continue
            xs.append(train[anchor].spread_bps)
            ys.append(1 if train[index].spread_bps > tau else 0)
        self.assertTrue(all(index - self.RULE.anchor(dates, index) == 2 for index in range(5, 20)))
        intercept, slope = fit_penalised_logistic(xs, ys)
        curves = self.make_predictor()(train, feature_rows, [tau])
        for row, curve in zip(feature_rows, curves.curves):
            expected = 1.0 / (1.0 + math.exp(-(intercept + slope * row.spread_bps)))
            self.assertAlmostEqual(curve[0], expected, places=12)

    def test_the_probability_rises_with_the_spread(self):
        train, _features = self.split()
        low = DailyObservation(date(2026, 3, 2), {"sofr": 3.95, "iorb": 4.0})
        high = DailyObservation(date(2026, 3, 2), {"sofr": 4.15, "iorb": 4.0})
        curves = self.make_predictor()(train, (low, high), [5.0])
        self.assertLess(curves.curves[0][0], curves.curves[1][0])

    def test_it_is_called_with_the_runs_rule(self):
        predictor = persistence_logistic_exceedance(minimum_history=self.MINIMUM_HISTORY)
        train, feature_rows = self.split()
        with self.assertRaises(TypeError):
            predictor(train, feature_rows, EXCEEDANCE_TAUS)


class CalendarClimatologyExceedanceTests(ExceedancePredictorConformance, unittest.TestCase):
    """The conformance suite against `calendar_climatology_exceedance`."""

    IMPLEMENTATION = staticmethod(calendar_climatology_exceedance)

    def frame(self):
        return pressure_panel(count=60)

    def scored_dates(self, feature_rows):
        # The day each feature row forecasts: two rows on, as the as-of read is.
        rows = self.frame()
        position = {row.date: index for index, row in enumerate(rows)}
        dates = [row.date for row in rows]
        extra = weekdays(dates[-1] + timedelta(days=1), 2)
        dates += extra
        return tuple(dates[position[row.date] + 2] for row in feature_rows)

    def make_predictor(self):
        predictor = calendar_climatology_exceedance(minimum_history=self.MINIMUM_HISTORY)

        def call(train, features, taus):
            return predictor(train, features, taus, scored_dates=self.scored_dates(features))

        return call

    def test_it_reads_the_target_and_the_coupon_settlement(self):
        self.assertEqual(
            self.curves().features_read, ("spread_bps", "treasury_settlement_coupons")
        )

    def test_each_day_gets_its_types_training_frequency(self):
        train, feature_rows = self.split()
        tau = 5.0
        by_type = {}
        for row in train:
            by_type.setdefault(strata.row_day_type(row), []).append(row.spread_bps > tau)
        predictor = calendar_climatology_exceedance(minimum_history=self.MINIMUM_HISTORY)
        days = (date(2025, 11, 28), date(2025, 11, 25))  # a month-end, an ordinary day
        rows = tuple(
            DailyObservation(day, {"sofr": 4.0, "iorb": 4.0, "treasury_settlement_coupons": 0.0})
            for day in days
        )
        curves = predictor(train, rows, [tau], scored_dates=days)
        for day, curve in zip(days, curves.curves):
            kind = strata.pressure_day_type(day, 0.0)
            self.assertEqual(curve[0], sum(by_type[kind]) / len(by_type[kind]))
        self.assertGreater(curves.curves[0][0], curves.curves[1][0])

    def test_a_type_with_no_training_day_falls_back_to_the_pooled_climatology(self):
        train, _features = self.split()
        train = [row for row in train if strata.row_day_type(row) != "tax_window"]
        day = date(2025, 12, 15)  # in the tax window
        row = DailyObservation(day, {"sofr": 4.0, "iorb": 4.0, "treasury_settlement_coupons": 0.0})
        predictor = calendar_climatology_exceedance(minimum_history=self.MINIMUM_HISTORY)
        pooled = climatology_exceedance(minimum_history=self.MINIMUM_HISTORY)
        self.assertEqual(
            predictor(train, (row,), EXCEEDANCE_TAUS, scored_dates=(day,)).curves,
            pooled(train, (row,), EXCEEDANCE_TAUS).curves,
        )

    def test_the_scored_days_type_reads_the_feature_rows_settlement(self):
        """The coupon settlement is a scheduled input, read at the scored day."""

        train, _features = self.split()
        day = date(2025, 11, 25)
        settles = DailyObservation(day, {"sofr": 4.0, "iorb": 4.0, "treasury_settlement_coupons": 30.0})
        quiet = DailyObservation(day, {"sofr": 4.0, "iorb": 4.0, "treasury_settlement_coupons": 0.0})
        predictor = calendar_climatology_exceedance(minimum_history=self.MINIMUM_HISTORY)
        curves = predictor(train, (settles, quiet), [-100.0, 5.0], scored_dates=(day, day))
        coupon_days = [row for row in train if strata.row_day_type(row) == "coupon_settlement"]
        self.assertTrue(coupon_days)
        self.assertEqual(
            curves.curves[0][1],
            sum(row.spread_bps > 5.0 for row in coupon_days) / len(coupon_days),
        )

    def test_scored_dates_must_match_the_feature_rows(self):
        train, feature_rows = self.split()
        predictor = calendar_climatology_exceedance(minimum_history=self.MINIMUM_HISTORY)
        with self.assertRaises(ValueError):
            predictor(train, feature_rows, EXCEEDANCE_TAUS, scored_dates=())


class _RecordFixture:
    ROWS = pressure_panel()

    def panel_path(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "panel.csv"
        columns = ["date", "sofr", "iorb", "sofr_volume", "treasury_settlement_coupons"]
        lines = [",".join(columns)] + [
            ",".join([row.date.isoformat()] + [repr(row.values[c]) for c in columns[1:]])
            for row in self.ROWS
        ]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    def exceedance(self, predictor, name, features):
        return rolling_exceedance_backtest(
            self.ROWS,
            predictor=predictor,
            model_name=name,
            features=features,
            registry=REGISTRY,
            decision_time=DECISION,
            taus=EXCEEDANCE_TAUS,
            minimum_history=40,
            refit_every=5,
        )

    def benchmarks(self):
        return (
            self.exceedance(
                calendar_climatology_exceedance(minimum_history=40),
                "calendar-climatology",
                ("spread_bps", "treasury_settlement_coupons"),
            ),
            self.exceedance(
                persistence_logistic_exceedance(minimum_history=40),
                "persistence-logistic",
                ("spread_bps",),
            ),
        )


class ExceedanceRecordBenchmarkTests(_RecordFixture, unittest.TestCase):
    """The record pairs its model with each benchmark, pooled and split."""

    def document(self, report=None, benchmarks=None):
        report = report or self.exceedance(
            climatology_exceedance(minimum_history=40), "climatology", ("spread_bps",)
        )
        return exceedance_backtest_document(
            report,
            panel_path=self.panel_path(),
            registry_path=REGISTRY_PATH,
            thresholds_path=THRESHOLDS_PATH,
            benchmarks=self.benchmarks() if benchmarks is None else benchmarks,
        )

    def test_both_benchmarks_are_paired_at_every_threshold(self):
        document = self.document()
        self.assertEqual(
            document["declaration"]["benchmarks"],
            {
                "calendar-climatology": ["spread_bps", "treasury_settlement_coupons"],
                "persistence-logistic": ["spread_bps"],
            },
        )
        row = document["metrics"]["by_tau"]["5"]
        for name in ("calendar-climatology", "persistence-logistic"):
            entry = row["benchmarks"][name]
            self.assertEqual(entry["mean_brier_difference"], entry["brier"] - row["brier"])
            interval = entry["mean_brier_difference_interval"]
            self.assertEqual(interval["method"], "stationary_bootstrap")
            self.assertLessEqual(interval["lower"], interval["upper"])
            self.assertAlmostEqual(entry["brier_skill_score"], 1.0 - row["brier"] / entry["brier"])

    def test_the_difference_is_benchmark_minus_model_per_day(self):
        report = self.exceedance(
            climatology_exceedance(minimum_history=40), "climatology", ("spread_bps",)
        )
        benchmarks = self.benchmarks()
        document = self.document(report, benchmarks)
        model, _reference, outcomes = report.at_tau(0)
        bench, _r, _o = benchmarks[1].at_tau(0)
        expected = sum(
            (b - y) ** 2 - (m - y) ** 2 for m, b, y in zip(model, bench, outcomes)
        ) / len(outcomes)
        entry = document["metrics"]["by_tau"]["5"]["benchmarks"]["persistence-logistic"]
        self.assertAlmostEqual(entry["mean_brier_difference"], expected, places=12)

    def test_every_threshold_is_split_by_regime_and_day_type(self):
        document = self.document()
        row = document["metrics"]["by_tau"]["5"]
        self.assertEqual(set(row["by_regime"]), {"2025-26"})
        types = row["by_day_type"]
        self.assertIn("month_end", types)
        self.assertIn("other", types)
        self.assertEqual(
            sum(entry["scored_days"] for entry in types.values()), row["scored_days"]
        )
        month_end_entry = types["month_end"]
        self.assertIn("persistence-logistic", month_end_entry["benchmarks"])
        self.assertIn("mean_brier_difference", month_end_entry["benchmarks"]["persistence-logistic"])
        self.assertEqual(
            document["metrics"]["splits"], strata.split_definitions()
        )

    def test_average_precision_is_reported_beside_the_base_rate(self):
        row = self.document()["metrics"]["by_tau"]["5"]
        self.assertIn("average_precision", row)
        self.assertIn("average_precision", row["benchmarks"]["persistence-logistic"])

    def test_benchmarks_scored_on_another_grid_are_refused(self):
        report = self.exceedance(
            climatology_exceedance(minimum_history=40), "climatology", ("spread_bps",)
        )
        shorter = rolling_exceedance_backtest(
            self.ROWS[:-3],
            predictor=persistence_logistic_exceedance(minimum_history=40),
            model_name="persistence-logistic",
            features=("spread_bps",),
            registry=REGISTRY,
            decision_time=DECISION,
            taus=EXCEEDANCE_TAUS,
            minimum_history=40,
            refit_every=5,
        )
        with self.assertRaises(ValueError):
            self.document(report, (shorter,))

    def test_without_benchmarks_the_record_is_unchanged_in_shape(self):
        document = self.document(benchmarks=())
        self.assertNotIn("benchmarks", document["declaration"])
        self.assertNotIn("benchmarks", document["metrics"]["by_tau"]["5"])


class ContinuousRecordSplitTests(_RecordFixture, unittest.TestCase):
    """The distribution's records are split too, and its comparisons paired per split."""

    def test_a_backtest_reports_mae_and_crps_per_split(self):
        report = rolling_persistence_backtest(
            self.ROWS,
            features=("spread_bps",),
            registry=REGISTRY,
            decision_time=DECISION,
            minimum_history=40,
            refit_every=5,
        )
        document = backtest_document(
            report, panel_path=self.panel_path(), registry_path=REGISTRY_PATH,
            model="persistence",
        )
        metrics = document["metrics"]
        types = metrics["by_day_type"]
        self.assertEqual(sum(e["forecast_count"] for e in types.values()), metrics["forecast_count"])
        for entry in types.values():
            self.assertIn("mae_bps", entry)
            self.assertIn("crps_bps", entry)
        whole = metrics["by_regime"]["2025-26"]
        self.assertAlmostEqual(whole["mae_bps"], metrics["mae_bps"], places=12)

    def test_a_comparison_pairs_each_split_with_an_interval(self):
        comparison = paired_model_comparison(
            self.ROWS,
            model_a="persistence",
            fit_a=fit,
            features_a=("spread_bps",),
            model_b="persistence",
            fit_b=fit,
            features_b=("spread_bps",),
            registry=REGISTRY,
            decision_time=DECISION,
            seed=7,
            minimum_history=40,
            refit_every=5,
        )
        document = paired_comparison_document(
            comparison, panel_path=self.panel_path(), registry_path=REGISTRY_PATH
        )
        entry = document["comparison"]["by_day_type"]["other"]
        self.assertEqual(entry["mean_difference_bps"], 0.0)
        self.assertEqual(entry["mean_difference_interval"]["method"], "stationary_bootstrap")
        self.assertIn("by_regime", document["comparison"])


if __name__ == "__main__":
    unittest.main()


class BenchmarkCommandTests(_RecordFixture, unittest.TestCase):
    """`exceedance-backtest --benchmark`, and the calendar model's required column."""

    def run_cli(self, *extra):
        import contextlib
        import io

        from repo_model import cli

        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        report = Path(directory.name) / "record.json"
        argv = [
            "exceedance-backtest", "--panel", str(self.panel_path()),
            "--thresholds", str(THRESHOLDS_PATH), "--registry", str(REGISTRY_PATH),
            "--decision-time", "16:00", "--minimum-history", "40", "--refit-every", "5",
            "--report", str(report), *extra,
        ]
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            code = cli.main(argv)
        return code, report, err.getvalue()

    def test_the_record_pairs_the_named_benchmarks(self):
        code, report, err = self.run_cli(
            "--model", "climatology", "--feature", "spread_bps",
            "--benchmark", "persistence-logistic", "--benchmark", "calendar-climatology",
        )
        self.assertEqual(code, 0, msg=err)
        document = json.loads(report.read_text(encoding="utf-8"))
        self.assertEqual(
            sorted(document["metrics"]["by_tau"]["5"]["benchmarks"]),
            ["calendar-climatology", "persistence-logistic"],
        )

    def test_a_benchmark_cannot_be_the_model_or_unknown(self):
        for extra in (
            ("--model", "persistence-logistic", "--feature", "spread_bps",
             "--benchmark", "persistence-logistic"),
            ("--model", "climatology", "--feature", "spread_bps", "--benchmark", "oracle"),
        ):
            with self.subTest(extra=extra):
                code, report, _err = self.run_cli(*extra)
                self.assertNotEqual(code, 0)
                self.assertFalse(report.exists())

    def test_the_calendar_model_without_its_coupon_column_is_refused(self):
        code, report, err = self.run_cli(
            "--model", "calendar-climatology", "--feature", "spread_bps"
        )
        self.assertNotEqual(code, 0)
        self.assertIn("treasury_settlement_coupons", err)
        self.assertFalse(report.exists())
