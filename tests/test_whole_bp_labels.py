"""A day exactly on a threshold is not above it (#155).

`docs/decisions/pressure-probability.md` ("The event is strictly greater
than"): both rates are quoted in whole basis points and the event is strictly
greater, so a day on tau is not a pressure day. `DailyObservation.spread_bps`
is `(sofr - iorb) * 100` in binary floating point, and 2018-07-03 (SOFR 2.00,
IORB 1.95) comes out as 5.000000000000004. Every comparison of a spread with a
threshold reads the spread rounded to the whole basis point first.

Written red first: on main, every test below except the helper's own failed
on its assertion (the day on +5 bp was labelled, counted or flagged as above
it); the helper's failed on import.
"""

from __future__ import annotations

import json
import unittest
from datetime import date, time, timedelta
from pathlib import Path

from repo_model import pressure, scarcity, tail_diagnostics
from repo_model.baseline import (
    calendar_climatology_exceedance,
    climatology_exceedance,
    persistence_logistic_exceedance,
    rolling_exceedance_backtest,
)
from repo_model.data import DailyObservation, fixed_bp_stress_label_columns
from repo_model.effr_history import HistoryRow, episodes
from repo_model.evaluation_splits import load_split_declaration

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "metadata" / "sources.json").read_text())
SPLITS = ROOT / "metadata" / "evaluation_splits.json"

#: SOFR and IORB legs, as published, for a spread of 0, exactly +5 and +6 bp.
LEGS = {0: (1.95, 1.95), 5: (2.00, 1.95), 6: (2.01, 1.95)}


def row(when, spread):
    sofr, iorb = LEGS[spread]
    return DailyObservation(
        when,
        {
            "sofr": sofr,
            "iorb": iorb,
            "days_to_month_end": 5.0,
            "quarter_end": 0.0,
            "tax_date": 0.0,
        },
    )


def weekday_rows(spreads, start=date(2018, 4, 2)):
    rows, when = [], start
    for spread in spreads:
        while when.weekday() >= 5:
            when += timedelta(days=1)
        rows.append(row(when, spread))
        when += timedelta(days=1)
    return rows


def backtest(rows):
    return rolling_exceedance_backtest(
        rows,
        predictor=persistence_logistic_exceedance(minimum_history=40),
        model_name="persistence_logistic",
        features=("spread_bps",),
        registry=REGISTRY,
        decision_time=time(16, 0),
        taus=(5.0, 10.0),
        minimum_history=40,
        refit_every=21,
    )


ON_TAU = row(date(2018, 7, 3), 5)
ABOVE_TAU = row(date(2018, 7, 5), 6)


class PreconditionTests(unittest.TestCase):
    def test_the_float_spread_on_the_threshold_is_above_it(self):
        """Without this the other tests would pass for the wrong reason."""

        self.assertGreater(ON_TAU.spread_bps, 5.0)
        self.assertEqual(ON_TAU.spread_bps, 5.000000000000004)


class HelperTests(unittest.TestCase):
    def test_a_day_on_tau_is_not_above_it_and_a_day_past_it_is(self):
        from repo_model.data import exceeds_bp

        self.assertFalse(exceeds_bp(ON_TAU.spread_bps, 5.0))
        self.assertTrue(exceeds_bp(ABOVE_TAU.spread_bps, 5.0))
        self.assertFalse(exceeds_bp(4.999999999999998, 5.0))
        self.assertTrue(exceeds_bp(5.0000001, 4.0))


class LabelTests(unittest.TestCase):
    def test_the_stress_columns(self):
        labels = fixed_bp_stress_label_columns([ON_TAU.spread_bps, ABOVE_TAU.spread_bps])
        self.assertEqual(labels[0]["stress_gt_5bp"], 0)
        self.assertEqual(labels[1]["stress_gt_5bp"], 1)

    def test_the_backtest_outcomes(self):
        """2018-07-03-style days labelled 0 at +5 bp; +6 bp days labelled 1."""

        report = backtest(weekday_rows([0, 0, 5, 6, 0, 5, 0, 6, 6, 0] * 8))
        by_value = {}
        for realized, outcome in zip(report.realized_bps, report.outcomes):
            by_value.setdefault(round(realized), set()).add(outcome)
        self.assertEqual(by_value[5], {(0, 0)})
        self.assertEqual(by_value[6], {(1, 0)})
        self.assertEqual(by_value[0], {(0, 0)})


    def test_the_event_list_lists_no_day_on_tau(self):
        """#130's event list reads the outcomes: no +5 bp day is an event."""

        from repo_model.baseline import exceedance_event_list

        report = backtest(weekday_rows([0, 0, 5, 6, 0, 5, 0, 6, 6, 0] * 8))
        events = exceedance_event_list(report, (), 0, lead_days=0)
        self.assertTrue(events)
        self.assertEqual({round(event["realized_bps"]) for event in events}, {6})


class TrainingCountTests(unittest.TestCase):
    def test_the_climatology_counts_no_day_on_tau(self):
        train = weekday_rows([5, 5, 5, 6] * 10)
        curves = climatology_exceedance(minimum_history=20)(train, train[-1:], (5.0,))
        self.assertEqual(curves.curves[0][0], 0.25)

    def test_the_calendar_climatology_counts_no_day_on_tau(self):
        train = weekday_rows([5, 5, 5, 6] * 10)
        predictor = calendar_climatology_exceedance(
            load_split_declaration(SPLITS), minimum_history=20
        )
        self.assertEqual(predictor(train, train[-1:], (5.0,)).curves[0][0], 0.25)

    def test_the_persistence_logistic_labels_no_day_on_tau(self):
        """Every training label on +5 bp or below: one label value, so a flat 0.

        The one +6 bp day is last, so no fold trains on it; it is there so the
        scored days carry a positive.
        """

        report = backtest(weekday_rows([0, 5] * 40 + [6]))
        self.assertEqual({curve[0] for curve in report.forecast}, {0.0})
        self.assertEqual({curve[0] for curve in report.reference}, {0.0})


class PressureTests(unittest.TestCase):
    def test_a_day_on_tau_is_not_an_onset(self):
        rows = weekday_rows([0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 6])
        found = pressure.onsets(rows, 5.0, [item.date for item in rows])
        self.assertEqual(found, (rows[12].date,))

    def test_a_day_on_tau_does_not_break_the_quiet_run(self):
        rows = weekday_rows([0, 0, 0, 0, 0, 5, 6])
        found = pressure.onsets(rows, 5.0, [item.date for item in rows])
        self.assertEqual(found, (rows[6].date,))


class ScarcityTests(unittest.TestCase):
    def test_the_frequency_table_counts_no_day_on_tau(self):
        scored = [
            scarcity.ScoredDay(item.date, 1.0, item.date, item.spread_bps)
            for item in weekday_rows([5, 5, 6, 0] * 5)
        ]
        table = scarcity.tabulate(scored, thresholds=(5.0,))
        self.assertEqual(table["by_state"]["1"]["gt_5bp"]["frequency"], 0.25)


class HistoryTests(unittest.TestCase):
    def test_an_episode_does_not_start_on_tau(self):
        """EFFR 2.00 against IOER 1.95 is +5 bp exactly: not above +5 bp."""

        days = [date(2015, 3, 2) + timedelta(days=offset) for offset in range(4)]
        legs = [(2.00, 1.95), (2.01, 1.95), (2.01, 1.95), (2.00, 1.95)]
        rows = [HistoryRow(when, effr, ioer, {}) for when, (effr, ioer) in zip(days, legs)]
        self.assertGreater(rows[0].spread_bps, 5.0)
        found = episodes(rows, 5.0)
        self.assertEqual(len(found), 1)
        self.assertEqual((found[0]["start"], found[0]["days"]), ("2015-03-03", 2))


class TailDiagnosticsTests(unittest.TestCase):
    def test_a_zero_forecast_on_tau_is_not_a_missed_event(self):
        account = {"state": "fitted", "xi": 0.2, "sigma": 1.0, "excesses": 40, "clamped": False}
        record = {
            "declaration": {"taus_bp": [5.0]},
            "folds": {"count": 1, "tail": [{"scored_date": "2018-07-03", **account}]},
        }
        knots = [
            {
                "scored_date": "2018-07-03",
                "tail_account": account,
                "probabilities": [0.0],
                "realized_bps": ON_TAU.spread_bps,
            }
        ]
        self.assertEqual(tail_diagnostics.zero_forecasts_on_events(record, knots)["fitted"], [])
        self.assertEqual(tail_diagnostics.brier_by_tau(record, knots), {5.0: 0.0})


if __name__ == "__main__":
    unittest.main()
