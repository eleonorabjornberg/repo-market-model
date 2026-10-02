"""The pressure-probability benchmarks, and the declared evaluation splits.

`docs/decisions/pressure-probability.md` fixes two benchmarks every candidate
pressure probability is compared against: a calendar-type climatology and a
persistence-logistic model. Directive 03 (#27) scores them, pairs every
candidate against both, and splits every result by regime and by pressure-day
type (`metadata/evaluation_splits.json`).

Both benchmarks are `ExceedancePredictor`s, so each runs the conformance suite
in `tests/test_baseline.py`; the classes here add what is particular to each.
"""

from __future__ import annotations

import contextlib
import csv
import io
import json
import math
import tempfile
import unittest
from datetime import date, time, timedelta
from pathlib import Path

from repo_model import cli
from repo_model.asof import InformationRule
from repo_model.baseline import (
    calendar_climatology_exceedance,
    persistence_logistic_exceedance,
)
from repo_model.data import DailyObservation
from repo_model.evaluation_splits import (
    SplitDeclaration,
    load_split_declaration,
    split_summary,
)

from test_baseline import EXCEEDANCE_TAUS, ExceedancePredictorConformance, regressor_frame
from lockbox_support import setUpModule, tearDownModule  # noqa: F401  (synthetic 2026 panels)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "metadata" / "sources.json").read_text())
REGISTRY_PATH = ROOT / "metadata" / "sources.json"
SPLITS = ROOT / "metadata" / "evaluation_splits.json"
THRESHOLDS = ROOT / "metadata" / "stress_thresholds.json"
DECISION = time(16, 0)


def splits():
    return load_split_declaration(SPLITS)


def with_calendar(rows):
    """`rows` with calendar columns that cycle through every pressure-day type."""

    out = []
    for index, row in enumerate(rows):
        values = dict(row.values)
        values["quarter_end"] = 1.0 if index % 11 == 10 else 0.0
        values["days_to_month_end"] = float(index % 7)
        values["tax_date"] = 1.0 if index % 5 == 0 else 0.0
        out.append(DailyObservation(row.date, values))
    return out


def weekdays(start, count):
    out, when = [], start
    while len(out) < count:
        if when.weekday() < 5:
            out.append(when)
        when += timedelta(days=1)
    return out


def spread_rows(spreads, start=date(2025, 1, 6)):
    """Weekday rows carrying `spreads` (bp) over a flat IORB."""

    return [
        DailyObservation(when, {"sofr": 4.0 + spread / 100.0, "iorb": 4.0})
        for when, spread in zip(weekdays(start, len(spreads)), spreads)
    ]


def reference_logistic(xs, ys, iterations=200000, rate=1e-3):
    """An independent fit of the same objective, by plain gradient descent.

    The objective `persistence_logistic_exceedance` documents: the log loss
    summed over the pairs, plus half the squared slope (scikit-learn's default
    `C=1`), the intercept unpenalised. Gradient descent rather than Newton, so
    agreement is between two algorithms and not one restated.
    """

    mean = sum(xs) / len(xs)
    b0, b1 = 0.0, 0.0
    for _ in range(iterations):
        g0 = g1 = 0.0
        for x, y in zip(xs, ys):
            z = b0 + b1 * x
            p = 1.0 / (1.0 + math.exp(-z)) if z >= 0 else math.exp(z) / (1.0 + math.exp(z))
            g0 += p - y
            g1 += (p - y) * x
        g1 += b1
        b0 -= rate * g0
        b1 -= rate * g1 / max(1.0, abs(mean))
    return b0, b1


class PersistenceLogisticConformanceTests(ExceedancePredictorConformance, unittest.TestCase):
    """The conformance suite against `persistence_logistic_exceedance`.

    The predictor pairs each training label with the spread public at that
    label's own decision instant, so it needs the run's as-of rule; the
    evaluators hand it over (`baseline._reads_information`). Here the rule is
    bound for the mixin's direct calls.
    """

    IMPLEMENTATION = staticmethod(persistence_logistic_exceedance)

    def make_predictor(self):
        predictor = persistence_logistic_exceedance(minimum_history=self.MINIMUM_HISTORY)
        rule = InformationRule(REGISTRY, ("spread_bps",), decision_time=DECISION)

        def bound(train_rows, feature_rows, taus):
            return predictor(train_rows, feature_rows, taus, information=rule)

        return bound


class CalendarClimatologyConformanceTests(ExceedancePredictorConformance, unittest.TestCase):
    """The conformance suite against `calendar_climatology_exceedance`."""

    IMPLEMENTATION = staticmethod(calendar_climatology_exceedance)

    def frame(self):
        return with_calendar(regressor_frame())

    def make_predictor(self):
        return calendar_climatology_exceedance(
            splits(), minimum_history=self.MINIMUM_HISTORY
        )


class PersistenceLogisticTests(unittest.TestCase):
    """A one-variable logistic on the latest public spread, refitted per block."""

    def rule(self):
        return InformationRule(REGISTRY, ("spread_bps",), decision_time=DECISION)

    def spreads(self):
        # Runs of five high and five low spreads, so the spread two rows back
        # predicts the label without separating it perfectly.
        pattern = [0, 1, 0, 6, 0, 9, 8, 9, 3, 9, 1, 0, 2, 0, 1, 8, 9, 6, 9, 8]
        return [float(value) for value in pattern * 3]

    def test_each_label_is_paired_with_the_spread_public_at_its_own_decision(self):
        """Under the tracked registry SOFR is public two rows before the label.

        The pairs are (spread at row t-2, spread at row t > tau), not t-1 (which
        is not yet public at t's 16:00 decision on t-1) and not t-3 (which is
        stale). The fit must equal an independent fit on exactly those pairs.
        """

        rows = spread_rows(self.spreads())
        train, feature = rows[:-1], rows[-1:]
        rule = self.rule()
        dates = [row.date for row in train]
        self.assertEqual(
            [rule.anchor(dates, t) for t in range(2, len(train))],
            [t - 2 for t in range(2, len(train))],
        )

        tau = 5.0
        xs = [train[t - 2].spread_bps for t in range(2, len(train))]
        ys = [1.0 if train[t].spread_bps > tau else 0.0 for t in range(2, len(train))]
        b0, b1 = reference_logistic(xs, ys)
        x = feature[0].spread_bps
        expected = 1.0 / (1.0 + math.exp(-(b0 + b1 * x)))

        predictor = persistence_logistic_exceedance(minimum_history=20)
        got = predictor(train, feature, (tau,), information=rule).curves[0][0]
        self.assertAlmostEqual(got, expected, places=5)

        # And the t-1 pairing gives a different number, so the test can tell.
        xs_wrong = [train[t - 1].spread_bps for t in range(2, len(train))]
        w0, w1 = reference_logistic(xs_wrong, ys)
        wrong = 1.0 / (1.0 + math.exp(-(w0 + w1 * x)))
        self.assertGreater(abs(wrong - expected), 1e-3)

    def test_the_probability_rises_with_the_latest_spread(self):
        rows = spread_rows(self.spreads())
        train = rows[:-2]
        low = DailyObservation(rows[-1].date, {"sofr": 4.0, "iorb": 4.0})
        high = DailyObservation(rows[-1].date, {"sofr": 4.09, "iorb": 4.0})
        predictor = persistence_logistic_exceedance(minimum_history=20)
        curves = predictor(train, (low, high), (5.0,), information=self.rule()).curves
        self.assertLess(curves[0][0], curves[1][0])

    def test_it_reads_the_spread_and_nothing_else(self):
        rows = spread_rows(self.spreads())
        predictor = persistence_logistic_exceedance(minimum_history=20)
        result = predictor(rows[:-1], rows[-1:], EXCEEDANCE_TAUS, information=self.rule())
        self.assertEqual(result.features_read, ("spread_bps",))

    def test_without_the_as_of_rule_it_refuses(self):
        """No silent fallback to a positional pairing the rule did not choose."""

        rows = spread_rows(self.spreads())
        predictor = persistence_logistic_exceedance(minimum_history=20)
        with self.assertRaises(ValueError):
            predictor(rows[:-1], rows[-1:], EXCEEDANCE_TAUS)

    def test_the_evaluators_hand_it_the_rule(self):
        from repo_model.baseline import _reads_information

        self.assertTrue(_reads_information(persistence_logistic_exceedance(minimum_history=20)))


class CalendarClimatologyTests(unittest.TestCase):
    """The base rate among training days of the scored day's pressure-day type."""

    def test_the_curve_is_the_rate_among_training_days_of_the_same_type(self):
        rows = with_calendar(regressor_frame(count=60))
        train, feature = rows[:-5], rows[-5:]
        declaration = splits()
        predictor = calendar_climatology_exceedance(declaration, minimum_history=20)
        result = predictor(train, feature, EXCEEDANCE_TAUS)
        for row, curve in zip(feature, result.curves):
            kind = declaration.day_type(row.values)
            same = [r.spread_bps for r in train if declaration.day_type(r.values) == kind]
            self.assertTrue(same)
            expected = tuple(
                sum(1 for value in same if round(value) > tau) / len(same)
                for tau in EXCEEDANCE_TAUS
            )
            self.assertEqual(curve, expected)

    def test_a_type_with_no_training_day_falls_back_to_the_pooled_rate(self):
        rows = with_calendar(regressor_frame(count=40))
        train = [
            DailyObservation(r.date, dict(r.values, quarter_end=0.0)) for r in rows[:-1]
        ]
        feature = [DailyObservation(rows[-1].date, dict(rows[-1].values, quarter_end=1.0))]
        predictor = calendar_climatology_exceedance(splits(), minimum_history=20)
        curve = predictor(train, feature, EXCEEDANCE_TAUS).curves[0]
        pooled = tuple(
            # Whole basis points (#155): a spread on tau is not above it.
            sum(1 for r in train if round(r.spread_bps) > tau) / len(train)
            for tau in EXCEEDANCE_TAUS
        )
        self.assertEqual(curve, pooled)

    def test_it_reads_the_spread_and_the_calendar_columns(self):
        rows = with_calendar(regressor_frame())
        predictor = calendar_climatology_exceedance(splits(), minimum_history=20)
        result = predictor(rows[:-1], rows[-1:], EXCEEDANCE_TAUS)
        self.assertEqual(
            result.features_read,
            ("spread_bps", "days_to_month_end", "quarter_end", "tax_date"),
        )


class SplitDeclarationTests(unittest.TestCase):
    """`metadata/evaluation_splits.json` and what is read from it."""

    def test_the_tracked_declaration_loads_and_covers_the_published_panel(self):
        declaration = splits()
        self.assertIsInstance(declaration, SplitDeclaration)
        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text())
        for key in ("start_date", "end_date"):
            declaration.regime(date.fromisoformat(manifest[key]))

    def test_day_types_follow_the_declared_precedence(self):
        declaration = splits()
        window = declaration.month_end_window
        self.assertEqual(
            declaration.day_type({"quarter_end": 1, "days_to_month_end": 0, "tax_date": 1}),
            "quarter_end",
        )
        self.assertEqual(
            declaration.day_type({"quarter_end": 0, "days_to_month_end": window, "tax_date": 1}),
            "month_end",
        )
        self.assertEqual(
            declaration.day_type({"quarter_end": 0, "days_to_month_end": window + 1, "tax_date": 1}),
            "tax_date",
        )
        self.assertEqual(
            declaration.day_type({"quarter_end": 0, "days_to_month_end": 20, "tax_date": 0}),
            "ordinary",
        )

    def test_a_missing_calendar_column_is_refused(self):
        with self.assertRaises(ValueError):
            splits().day_type({"quarter_end": 0, "tax_date": 0})

    def test_a_day_outside_every_regime_is_refused(self):
        with self.assertRaises(ValueError):
            splits().regime(date(2017, 6, 1))

    def test_overlapping_regimes_are_refused(self):
        document = json.loads(SPLITS.read_text())
        document["regimes"][1]["first"] = document["regimes"][0]["last"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "splits.json"
            path.write_text(json.dumps(document))
            with self.assertRaises(ValueError):
                load_split_declaration(path)


class SplitSummaryTests(unittest.TestCase):
    """A group mean with a domain bootstrap interval over the whole series."""

    def test_each_group_reports_its_count_and_mean(self):
        labels = ["a", "b"] * 50
        series = [1.0, 3.0] * 50
        summary = split_summary(
            labels, series, ("a", "b", "c"), block_length=3, seed=7, replications=200, level=0.9
        )
        self.assertEqual(summary["a"]["count"], 50)
        self.assertEqual(summary["a"]["mean"], 1.0)
        self.assertEqual(summary["b"]["mean"], 3.0)
        self.assertEqual(summary["a"]["interval"], {"lower": 1.0, "upper": 1.0})
        self.assertEqual(summary["c"], {"count": 0})

    def test_the_interval_brackets_the_group_mean(self):
        labels = ["a" if i % 3 else "b" for i in range(300)]
        series = [float((i * 37) % 11) for i in range(300)]
        summary = split_summary(
            labels, series, ("a", "b"), block_length=5, seed=11, replications=500, level=0.9
        )
        for group in ("a", "b"):
            entry = summary[group]
            self.assertLessEqual(entry["interval"]["lower"], entry["mean"])
            self.assertGreaterEqual(entry["interval"]["upper"], entry["mean"])

    def test_misaligned_inputs_are_refused(self):
        with self.assertRaises(ValueError):
            split_summary(["a"], [1.0, 2.0], ("a",), block_length=1, seed=1,
                          replications=10, level=0.9)


#: Columns for the command-line panel: the harness's, plus the calendar column
#: a pressure-day type needs.
PANEL_COLUMNS = (
    "date", "sofr", "iorb", "sofr_volume", "sofr_p25", "sofr_p75",
    "quarter_end", "tax_date", "days_to_month_end",
)


class BenchmarkCommandTests(unittest.TestCase):
    """`exceedance-backtest --benchmark` and `--splits`, end to end."""

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.tmp = Path(directory.name)
        self.panel = self.tmp / "panel.csv"
        days = weekdays(date(2025, 10, 6), 90)
        with self.panel.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(PANEL_COLUMNS)
            for index, when in enumerate(days):
                spread = (2.0 if index < 45 else 9.0) + ((index * 7) % 13) / 2.0
                month_end = date(when.year + (when.month == 12), when.month % 12 + 1, 1) - timedelta(days=1)
                writer.writerow([
                    when.isoformat(), round(4.30 + spread / 100.0, 6), 4.30,
                    2100 + index, 4.30, 4.32,
                    1 if when.month in (3, 6, 9, 12) and (month_end - when).days < 1 else 0,
                    1 if when.day == 15 else 0,
                    (month_end - when).days,
                ])

    def run_command(self, *extra, model="gbm", features=("spread_bps",)):
        report = self.tmp / "report.json"
        argv = [
            "exceedance-backtest",
            "--panel", str(self.panel),
            "--thresholds", str(THRESHOLDS),
            "--registry", str(REGISTRY_PATH),
            "--decision-time", "16:00",
            "--minimum-history", "30",
            "--refit-every", "5",
            "--model", model,
            "--report", str(report),
        ]
        for feature in features:
            argv += ["--feature", feature]
        argv += list(extra)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(argv)
        return code, err.getvalue(), (json.loads(report.read_text()) if code == 0 else None)

    def test_the_benchmarks_are_scored_on_the_same_grid_and_paired(self):
        code, err, record = self.run_command(
            "--benchmark", "calendar_climatology",
            "--benchmark", "persistence_logistic",
            "--splits", str(SPLITS),
            model="climatology",
        )
        self.assertEqual(code, 0, msg=err)
        benchmarks = record["benchmarks"]
        self.assertEqual(sorted(benchmarks), ["calendar_climatology", "persistence_logistic"])
        for name, entry in benchmarks.items():
            self.assertEqual(entry["scored_days"], record["metrics"]["scored_days"])
            self.assertIn("sign_convention", entry)
            for key, row in entry["by_tau"].items():
                paired = row["paired_brier_difference"]
                self.assertEqual(
                    paired["mean"], row["benchmark_brier"] - record["metrics"]["by_tau"][key]["brier"]
                )
                self.assertIn("interval", paired)
                self.assertEqual(
                    sorted(paired["splits"]["by_day_type"]),
                    sorted(["quarter_end", "month_end", "tax_date", "ordinary"]),
                )
                self.assertIn("by_regime", paired["splits"])

    def test_the_record_splits_its_own_brier_and_reports_average_precision(self):
        code, err, record = self.run_command("--splits", str(SPLITS), model="climatology")
        self.assertEqual(code, 0, msg=err)
        self.assertEqual(record["splits"]["declaration"]["sha256"], splits().sha256)
        row = record["metrics"]["by_tau"]["5"]
        self.assertIn("by_regime", row["brier_splits"])
        self.assertIn("by_day_type", row["brier_splits"])
        self.assertIn("average_precision", row)

    def test_calendar_climatology_runs_by_name_with_the_split_declaration(self):
        code, err, record = self.run_command(
            "--splits", str(SPLITS),
            model="calendar_climatology",
            features=("spread_bps", "days_to_month_end", "quarter_end", "tax_date"),
        )
        self.assertEqual(code, 0, msg=err)
        self.assertEqual(record["declaration"]["model"], "calendar_climatology")

    def test_calendar_climatology_without_the_split_declaration_is_refused(self):
        code, err, _ = self.run_command(
            model="calendar_climatology",
            features=("spread_bps", "days_to_month_end", "quarter_end", "tax_date"),
        )
        self.assertNotEqual(code, 0)
        self.assertIn("--splits", err)

    def test_persistence_logistic_runs_by_name(self):
        code, err, record = self.run_command(model="persistence_logistic")
        self.assertEqual(code, 0, msg=err)
        self.assertEqual(record["declaration"]["model"], "persistence_logistic")

    def run_continuous(self, command, *extra):
        report = self.tmp / f"{command}.json"
        argv = [command, str(self.panel), "--registry", str(REGISTRY_PATH),
                "--decision-time", "16:00", "--minimum-history", "30",
                "--refit-every", "5", "--report", str(report), "--splits", str(SPLITS),
                *extra]
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(argv)
        self.assertEqual(code, 0, msg=err.getvalue())
        return json.loads(report.read_text())

    def assert_partition(self, splits, pooled, count):
        """The group means, weighted by their counts, recover the pooled mean."""

        for key in ("by_regime", "by_day_type"):
            groups = splits[key]
            self.assertEqual(sum(entry["count"] for entry in groups.values()), count)
            total = sum(entry["count"] * entry.get("mean", 0.0) for entry in groups.values())
            self.assertAlmostEqual(total / count, pooled, places=9)

    def test_backtest_splits_its_absolute_errors(self):
        record = self.run_continuous(
            "backtest", "--model", "persistence", "--feature", "spread_bps"
        )
        self.assert_partition(
            record["metrics"]["mae_bps_splits"],
            record["metrics"]["mae_bps"],
            record["metrics"]["forecast_count"],
        )

    def test_compare_splits_its_paired_differences(self):
        record = self.run_continuous(
            "compare", "--model-a", "persistence", "--feature-a", "spread_bps",
            "--model-b", "rolling-residual", "--feature-b", "spread_bps",
            "--residual-window-b", "10", "--loss", "crps",
        )
        comparison = record["comparison"]
        self.assert_partition(
            comparison["splits"], comparison["mean_difference_bps"], comparison["origin_count"]
        )

    def test_an_unknown_benchmark_is_refused(self):
        code, err, _ = self.run_command("--benchmark", "climatology", model="climatology")
        self.assertNotEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
