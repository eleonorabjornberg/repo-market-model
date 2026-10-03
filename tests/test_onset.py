"""Onset scoring (#139): day groups, the as-of leap targets, their baselines.

`repo_model.onset`, and its wiring into `exceedance-backtest` and `compare`.
"""

from __future__ import annotations

import contextlib
import io
import json
import math
import tempfile
import unittest
from datetime import date, time, timedelta
from pathlib import Path
from unittest import mock

from repo_model import cli, onset
from repo_model.asof import TARGET, InformationRule, fold_grid
from repo_model.data import DailyObservation, load_daily_panel
from repo_model.evaluation_splits import load_split_declaration
from repo_model.splits import LookAheadError

from test_benchmarks import BenchmarkCommandTests
from lockbox_support import setUpModule, tearDownModule  # noqa: F401  (synthetic 2026 panels)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "metadata" / "sources.json").read_text())
SPLITS = ROOT / "metadata" / "evaluation_splits.json"
DECISION = time(16, 0)


def row(when, spread_bps, **values):
    """A panel row whose SOFR sits `spread_bps` above an IORB of 4.30."""

    columns = {"sofr": round(4.30 + spread_bps / 100.0, 6), "iorb": 4.30}
    columns.update(values)
    return DailyObservation(when, columns)


def weekdays(start, count):
    out, when = [], start
    while len(out) < count:
        if when.weekday() < 5:
            out.append(when)
        when += timedelta(days=1)
    return out


_PANEL = {}


def published_panel():
    """The published panel, built once from the tracked fixtures (no network)."""

    if "rows" not in _PANEL:
        manifest = json.loads(
            (ROOT / "metadata" / "funding_panel_manifest.json").read_text(encoding="utf-8")
        )
        directory = tempfile.mkdtemp()
        output = Path(directory) / "panel.csv"
        argv = [
            "build",
            "--raw-root", str(ROOT / "tests" / "fixtures" / "snapshots" / "funding_inputs"),
            "--output", str(output),
            "--build-cutoff", manifest["build_cutoff"],
            "--decision-time", manifest["decision_time"],
        ]
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(argv)
        if code != 0:
            raise RuntimeError(err.getvalue())
        _PANEL["rows"] = load_daily_panel(output)
    return _PANEL["rows"]


class OnsetDefinitionTests(unittest.TestCase):
    """The onset day of #139, as a constant, on whole basis points."""

    def test_the_definition_is_a_constant(self):
        self.assertEqual(onset.ONSET_THRESHOLD_BP, 5)
        self.assertEqual(onset.ONSET_CALM_DAYS, 5)
        self.assertEqual(onset.ONSET_LEAD_DAYS, 5)

    def test_the_first_day_above_five_after_five_calm_days_is_an_onset(self):
        days = weekdays(date(2024, 1, 2), 12)
        spreads = [0, 1, 5, 5, 2, 6, 8, 3, 1, 0, 2, 7]
        flags = onset.onset_flags([row(d, s) for d, s in zip(days, spreads)])
        # Day 5 has only five panel days before it, all calm: an onset. Day 6
        # follows an elevated day. Day 11 follows days 6..10, of which 6 is
        # above +5: not five calm days.
        self.assertEqual([i for i, flag in enumerate(flags) if flag], [5])
        spreads[6] = 4
        flags = onset.onset_flags([row(d, s) for d, s in zip(days, spreads)])
        self.assertEqual([i for i, flag in enumerate(flags) if flag], [5, 11])

    def test_a_day_on_the_threshold_is_not_above_it(self):
        """2018-07-03: SOFR 2.00, IORB 1.95 is +5 bp in whole bp, not above (#155)."""

        days = weekdays(date(2018, 6, 26), 6)
        rows = [DailyObservation(d, {"sofr": 1.95, "iorb": 1.95}) for d in days[:5]]
        rows.append(DailyObservation(days[5], {"sofr": 2.00, "iorb": 1.95}))
        self.assertGreater(rows[-1].spread_bps, 5.0)  # the float is 5.000000000000004
        self.assertFalse(onset.onset_flags(rows)[-1])

    def test_a_scheduled_pressure_day_is_a_declared_type_or_a_coupon_settlement(self):
        declaration = load_split_declaration(SPLITS)
        calendar = {"quarter_end": 0, "tax_date": 0, "days_to_month_end": 10}
        ordinary = row(date(2024, 5, 8), 0, **calendar)
        coupon = row(date(2024, 5, 15), 0, treasury_settlement_coupons=70.0, **calendar)
        month_end = row(date(2024, 5, 30), 0, **{**calendar, "days_to_month_end": 1})
        self.assertFalse(onset.scheduled_pressure(ordinary, declaration))
        self.assertTrue(onset.scheduled_pressure(coupon, declaration))
        self.assertTrue(onset.scheduled_pressure(month_end, declaration))


class AsOfJumpTests(unittest.TestCase):
    """The jump is against each forecast's as-of anchor, never the day before.

    Mutation, recorded (#139): in `onset.as_of_jump`, the line
    `anchor = rule.anchor(dates, index)` replaced by `anchor = index - 1` (the
    day before the scored day). `test_the_jump_is_against_the_as_of_anchor`
    then raised `LookAheadError` from `_require_public`: at the 16:00 decision
    the day before is not yet public. With `_require_public`'s call also
    deleted, the same test failed with `AssertionError` (61 != 60) on the anchor.
    """

    def setUp(self):
        self.rows = published_panel()
        self.dates = [r.date for r in self.rows]
        self.rule = InformationRule(REGISTRY, (TARGET,), decision_time=DECISION)

    def test_the_jump_is_against_the_as_of_anchor(self):
        grid = fold_grid(self.dates, REGISTRY, decision_time=DECISION, minimum_history=61)
        differs = 0
        for index in grid[:300]:
            jump, anchor = onset.as_of_jump(self.rows, self.rule, index, self.dates)
            self.assertEqual(anchor, self.rule.anchor(self.dates, index))
            # A daily NY Fed rate is public the next morning: the forecast made
            # at 16:00 the day before sees the spread two rows back.
            self.assertEqual(index - anchor, 2)
            self.assertEqual(
                jump,
                onset.whole_bp(self.rows[index].spread_bps)
                - onset.whole_bp(self.rows[anchor].spread_bps),
            )
            day_before = onset.whole_bp(self.rows[index].spread_bps) - onset.whole_bp(
                self.rows[index - 1].spread_bps
            )
            differs += jump != day_before
        self.assertGreater(differs, 0)

    def test_a_jump_anchored_on_a_row_not_yet_public_is_refused(self):
        index = 200
        with mock.patch.object(self.rule, "anchor", return_value=index - 1):
            with self.assertRaises(LookAheadError):
                onset.as_of_jump(self.rows, self.rule, index, self.dates)
        with mock.patch.object(self.rule, "anchor", return_value=index):
            with self.assertRaises(LookAheadError):
                onset.as_of_jump(self.rows, self.rule, index, self.dates)

    def test_a_row_with_no_decision_instant_has_no_jump(self):
        self.assertIsNone(onset.as_of_jump(self.rows, self.rule, 0, self.dates))

    def test_the_horizon_moves_the_anchor_back(self):
        rule = InformationRule(REGISTRY, (TARGET,), decision_time=DECISION, horizon=3)
        _, anchor = onset.as_of_jump(self.rows, rule, 300, self.dates)
        self.assertEqual(300 - anchor, 4)


class LeapThresholdTests(unittest.TestCase):
    """`J_h`, recomputed from the tracked panel by the exact rule of #139."""

    def test_percentile_is_linear_interpolation_type_7(self):
        self.assertAlmostEqual(onset.percentile([1, 2, 3, 4], 0.9), 3.7)
        self.assertAlmostEqual(onset.percentile([4, 1, 3, 2], 0.5), 2.5)
        self.assertEqual(onset.percentile([7], 0.9), 7.0)
        self.assertAlmostEqual(onset.percentile([-2, 0, 0, 1, 5], 0.9), 3.4)

    def test_the_constants_match_the_rule_on_the_tracked_panel(self):
        rows = published_panel()
        dates = [r.date for r in rows]
        grid = fold_grid(dates, REGISTRY, decision_time=DECISION, minimum_history=61)
        self.assertEqual(dates[grid[0]], onset.LEAP_WINDOW[0])
        for horizon, expected in onset.LEAP_JUMP_BP.items():
            rule = InformationRule(REGISTRY, (TARGET,), decision_time=DECISION, horizon=horizon)
            self.assertEqual(onset.leap_threshold(rows, rule, grid), expected, horizon)
        self.assertEqual(sorted(onset.LEAP_JUMP_BP), [1, 2, 3, 4, 5])

    def test_the_window_ends_before_the_lockbox(self):
        self.assertEqual(onset.LEAP_WINDOW[1], date(2025, 12, 31))


class LeapTargetTests(unittest.TestCase):
    """Leap, leap onset and pressure leap, and the level a curve is read at."""

    @classmethod
    def setUpClass(cls):
        cls.rows = published_panel()
        cls.rule = InformationRule(REGISTRY, (TARGET,), decision_time=DECISION)
        cls.targets = onset.LeapTargets(cls.rows, cls.rule, onset.LEAP_JUMP_BP[1])

    def test_the_targets_follow_their_definitions(self):
        t = self.targets
        self.assertGreater(sum(t.leap), 0)
        self.assertGreater(sum(t.leap_onset), 0)
        for index in range(len(self.rows)):
            if t.jump[index] is None:
                self.assertFalse(t.leap[index])
                continue
            self.assertEqual(t.leap[index], t.jump[index] > onset.LEAP_JUMP_BP[1])
            if t.leap_onset[index]:
                self.assertTrue(t.leap[index])
                self.assertFalse(any(t.leap[index - k] for k in range(1, 6)))
            self.assertEqual(
                t.pressure_leap[index],
                t.leap[index] and onset.whole_bp(self.rows[index].spread_bps) > 0,
            )

    def test_the_event_level_is_the_whole_bp_event(self):
        t = self.targets
        for index in range(len(self.rows)):
            if t.jump[index] is None:
                continue
            spread = onset.whole_bp(self.rows[index].spread_bps)
            self.assertEqual(spread > t.event_threshold(index, pressure=False), t.leap[index])
            self.assertEqual(
                spread > t.event_threshold(index, pressure=True), t.pressure_leap[index]
            )


class LeapBaselineTests(unittest.TestCase):
    """Both named baselines are fitted walk-forward on observable labels only."""

    @classmethod
    def setUpClass(cls):
        rows = published_panel()
        cls.rows = rows
        cls.dates = [r.date for r in rows]
        cls.rule = InformationRule(REGISTRY, (TARGET,), decision_time=DECISION)
        cls.declaration = load_split_declaration(SPLITS)
        grid = fold_grid(cls.dates, REGISTRY, decision_time=DECISION, minimum_history=61)
        cls.scored = [cls.dates[i] for i in grid[:63]]
        # Three refit blocks of 21, each trained through its first day's anchor.
        cls.train_ends = []
        for k, index in enumerate(grid[:63]):
            first = grid[(k // 21) * 21]
            cls.train_ends.append(cls.dates[cls.rule.anchor(cls.dates, first)])

    def forecasts(self, rows):
        targets = onset.LeapTargets(rows, self.rule, onset.LEAP_JUMP_BP[1])
        return (
            onset.leap_calendar_climatology(
                targets, "leap", self.scored, self.train_ends, self.declaration
            ),
            onset.leap_persistence_logistic(targets, "leap", self.scored, self.train_ends),
        )

    def test_they_are_probabilities_refitted_per_block(self):
        climatology, logistic = self.forecasts(self.rows)
        for column in (climatology, logistic):
            self.assertEqual(len(column), 63)
            self.assertTrue(all(0.0 <= p <= 1.0 for p in column))
        self.assertGreater(len(set(logistic)), 3)

    def test_a_forecast_reads_nothing_after_its_own_anchor(self):
        """Raising every spread after a scored day's anchor moves none of its forecasts.

        The scored day's own spread and label are among the rows moved, so a
        baseline that read its outcome, or a label not yet observable, would
        move.
        """

        for k in (0, 20, 21, 40, 62):
            when, end = self.scored[k], self.train_ends[k]
            anchor = self.rule.anchor(self.dates, self.dates.index(when))
            changed = list(self.rows[: anchor + 1]) + [
                DailyObservation(r.date, {**r.values, "sofr": float(r.values["sofr"]) + 0.5})
                for r in self.rows[anchor + 1:]
            ]
            for rows in (self.rows, changed):
                targets = onset.LeapTargets(rows, self.rule, onset.LEAP_JUMP_BP[1])
                column = (
                    onset.leap_calendar_climatology(
                        targets, "leap", [when], [end], self.declaration
                    )
                    + onset.leap_persistence_logistic(targets, "leap", [when], [end])
                )
                if rows is self.rows:
                    before = column
            self.assertEqual(before, column, when)

    def test_a_fold_trained_through_its_own_day_is_refused(self):
        targets = onset.LeapTargets(self.rows, self.rule, onset.LEAP_JUMP_BP[1])
        with self.assertRaises(LookAheadError):
            onset.leap_persistence_logistic(
                targets, "leap", self.scored[:1], self.scored[:1]
            )


class PairedEvidenceTests(unittest.TestCase):
    def test_diebold_mariano_is_zero_for_a_symmetric_series(self):
        result = onset.diebold_mariano([1.0, -1.0] * 50)
        self.assertAlmostEqual(result["statistic"], 0.0)
        self.assertAlmostEqual(result["p_value"], 1.0)
        self.assertEqual(result["lag"], math.floor(4 * (100 / 100) ** (2 / 9)))

    def test_diebold_mariano_with_no_lag_is_the_plain_t_ratio(self):
        values = [0.3, -0.1, 0.4, 0.2, -0.2, 0.5, 0.1, 0.0]
        with mock.patch.object(onset.math, "floor", return_value=0):
            result = onset.diebold_mariano(values)
        n = len(values)
        mean = sum(values) / n
        variance = sum((v - mean) ** 2 for v in values) / n
        self.assertAlmostEqual(result["statistic"], mean / math.sqrt(variance / n))

    def test_a_constant_series_has_no_test(self):
        self.assertIn("unavailable", onset.diebold_mariano([0.1] * 20))

    def test_twcrps_above_five_from_quantiles(self):
        levels = (0.1, 0.5, 0.9)
        # Wholly above +5 bp: the weight is 1 everywhere it matters.
        from repo_model.metrics import crps_from_quantiles

        self.assertAlmostEqual(
            onset.twcrps_above_from_quantiles(levels, [6, 8, 12], 9.0),
            crps_from_quantiles(levels, [6, 8, 12], 9.0),
        )
        # Wholly at or below +5 bp: nothing to score.
        self.assertEqual(onset.twcrps_above_from_quantiles(levels, [-3, 0, 2], 1.0), 0.0)
        # A forecast that misses a +12 bp day scores worse than one that saw it.
        self.assertGreater(
            onset.twcrps_above_from_quantiles(levels, [-3, 0, 2], 12.0),
            onset.twcrps_above_from_quantiles(levels, [4, 9, 14], 12.0),
        )


class OnsetReportTests(unittest.TestCase):
    """The groups, the leap targets with both baselines, and twCRPS, in the records."""

    setUp = BenchmarkCommandTests.setUp
    run_command = BenchmarkCommandTests.run_command
    run_continuous = BenchmarkCommandTests.run_continuous

    def test_the_exceedance_record_carries_the_onset_view(self):
        code, err, record = self.run_command(
            "--benchmark", "persistence_logistic",
            "--benchmark", "calendar_climatology",
            "--splits", str(SPLITS),
            model="climatology",
        )
        self.assertEqual(code, 0, msg=err)
        view = record["onset"]
        self.assertEqual(sorted(view["by_tau"]), ["10", "5"])
        for entry in view["by_tau"].values():
            for group in (onset.GROUP_ALL, onset.GROUP_SCHEDULED, onset.GROUP_ONSET):
                self.assertIn(group, entry)
                self.assertEqual(
                    sorted(entry[group]["brier"]),
                    ["calendar_climatology", "climatology", "persistence_logistic",
                     "reference_climatology"],
                )
                self.assertEqual(
                    sorted(entry[group]["paired"]),
                    ["calendar_climatology", "persistence_logistic", "reference_climatology"],
                )
            all_days = entry[onset.GROUP_ALL]
            self.assertEqual(all_days["days"], record["metrics"]["scored_days"])
            self.assertIn("diebold_mariano", all_days["paired"]["persistence_logistic"])
            self.assertNotIn(
                "diebold_mariano",
                entry[onset.GROUP_SCHEDULED]["paired"]["persistence_logistic"],
            )
            self.assertEqual(len(entry["lead_time"]), entry[onset.GROUP_ONSET]["days"])
        self.assertIn("twcrps_above_5bp", view["crps"])
        self.assertIn("crps_on_grid", view["crps"])
        leap = view["leap"]
        self.assertEqual(leap["threshold_bp"], onset.LEAP_JUMP_BP[1])
        for target in ("leap", "pressure_leap"):
            entry = leap["targets"][target]
            for group in (onset.GROUP_ALL, onset.GROUP_SCHEDULED, onset.GROUP_LEAP_ONSET):
                self.assertEqual(
                    sorted(entry[group]["paired"]),
                    [onset.LEAP_CALENDAR_CLIMATOLOGY, onset.LEAP_PERSISTENCE_LOGISTIC],
                )
            self.assertIn("result", entry["verdict"])

    def test_the_onset_view_leaves_the_pooled_figures_alone(self):
        """The leap call is separate: the declared curves score as before."""

        from repo_model import baseline

        calls = []
        real = baseline.rolling_exceedance_backtest

        def without_leap(*args, **kwargs):
            calls.append(kwargs.get("leap_jump_bp"))
            kwargs["leap_jump_bp"] = None
            return real(*args, **kwargs)

        code, err, record = self.run_command(
            "--splits", str(SPLITS), model="persistence_logistic"
        )
        self.assertEqual(code, 0, msg=err)
        with mock.patch("repo_model.cli_eval.rolling_exceedance_backtest", without_leap):
            code, err, plain = self.run_command(
                "--splits", str(SPLITS), model="persistence_logistic"
            )
        self.assertEqual(code, 0, msg=err)
        self.assertEqual(calls, [onset.LEAP_JUMP_BP[1]])
        self.assertEqual(record["metrics"], plain["metrics"])
        self.assertIn("unavailable", plain["onset"]["leap"])

    def test_the_comparison_record_carries_the_onset_view(self):
        record = self.run_continuous(
            "compare", "--model-a", "persistence", "--feature-a", "spread_bps",
            "--model-b", "rolling-residual", "--feature-b", "spread_bps",
            "--residual-window-b", "10", "--loss", "crps",
        )
        view = record["onset"]
        self.assertEqual(sorted(view["by_series"]), ["loss", "twcrps_above_5bp"])
        loss = view["by_series"]["loss"][onset.GROUP_ALL]
        self.assertAlmostEqual(loss["mean"], record["comparison"]["mean_difference_bps"])
        self.assertEqual(loss["days"], record["comparison"]["origin_count"])
        self.assertIn("diebold_mariano", loss)
        for series in view["by_series"].values():
            for group in (onset.GROUP_ALL, onset.GROUP_SCHEDULED, onset.GROUP_ONSET):
                self.assertIn(group, series)


if __name__ == "__main__":
    unittest.main()
