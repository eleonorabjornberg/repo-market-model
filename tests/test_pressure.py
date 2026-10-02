"""Pressure model v1's evidence: recalibration, onsets, lead time, scorecard (#114).

`repo_model.pressure` turns `rolling_exceedance_backtest` reports into the
evidence `docs/decisions/pressure-probability.md` asks for. These tests run on
small synthetic reports built from the real backtest, so the folds, blocks and
outcomes are the evaluator's own.
"""

from __future__ import annotations

import dataclasses
import json
import math
import unittest
from datetime import date, time, timedelta
from pathlib import Path

from repo_model import pressure
from repo_model.baseline import (
    _logistic_fit,
    _sigmoid,
    persistence_logistic_exceedance,
    rolling_exceedance_backtest,
)
from repo_model.data import DailyObservation
from repo_model.evaluation_splits import load_split_declaration

from lockbox_support import setUpModule, tearDownModule  # noqa: F401  (synthetic 2026 panels)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "metadata" / "sources.json").read_text())
SPLITS = ROOT / "metadata" / "evaluation_splits.json"


def weekday_rows(spreads, start=date(2025, 1, 6)):
    rows, when = [], start
    for spread in spreads:
        while when.weekday() >= 5:
            when += timedelta(days=1)
        rows.append(
            DailyObservation(
                when,
                {
                    "sofr": 4.0 + spread / 100.0,
                    "iorb": 4.0,
                    "days_to_month_end": 5.0,
                    "quarter_end": 0.0,
                    "tax_date": 0.0,
                },
            )
        )
        when += timedelta(days=1)
    return rows


def spreads(count=420, seed=114):
    """Runs of pressure: a spread that persists, so the logistic has signal."""

    out, state, level = [], seed, 0.0
    for _ in range(count):
        state = (1103515245 * state + 12345) % (2 ** 31)
        shock = (state % 1000) / 1000.0
        level = 0.8 * level + (12.0 if shock > 0.93 else 0.0) + (shock - 0.5) * 3.0
        out.append(round(level))
    return out


def backtest(rows, horizon=1, refit_every=21):
    return rolling_exceedance_backtest(
        rows,
        predictor=persistence_logistic_exceedance(minimum_history=40),
        model_name="persistence_logistic",
        features=("spread_bps",),
        registry=REGISTRY,
        decision_time=time(16, 0),
        taus=(5.0, 10.0),
        minimum_history=40,
        refit_every=refit_every,
        horizon=horizon,
    )


class RecalibrationTests(unittest.TestCase):
    """Out of fold: a block is recalibrated only on outcomes observable at its fit."""

    @classmethod
    def setUpClass(cls):
        cls.rows = weekday_rows(spreads())
        cls.report = backtest(cls.rows, horizon=3)
        cls.recal = pressure.recalibrated(cls.report)

    def blocks(self):
        folds = self.report.folds
        starts = [i for i in range(len(folds)) if i == 0 or folds[i].train_end != folds[i - 1].train_end]
        return list(zip(starts, starts[1:] + [len(folds)]))

    def test_each_block_is_the_platt_fit_on_its_observable_past(self):
        """The recalibrated forecast is an independent Platt fit on the right pairs.

        At horizon 3 the last scored days of a block are after the next block's
        last training label, so their outcomes were not observable when it was
        fitted, and they must not train its curve.

        Written red first: with the observability filter absent, the pairs
        include those days, and the fits differ.

        Recorded mutation (CLAUDE.md), the observability filter dropped: in
        `pressure.recalibrated`, `if report.folds[index].scored_date <=
        end_label` mutated to `if True`. This test then fails, raising
        `AssertionError` (the first recalibrated block's probabilities differ
        from the fit on its observable past).
        """

        position = 0
        forecast, _, outcomes = self.report.at_tau(position)
        floor = pressure.RECALIBRATION["probability_floor"]

        def logit(p):
            p = min(1 - floor, max(floor, p))
            return math.log(p / (1 - p))

        checked = 0
        excluded_somewhere = False
        for start, stop in self.blocks():
            end_label = self.report.folds[start].train_end
            past = [i for i in range(start) if self.report.folds[i].scored_date <= end_label]
            excluded_somewhere |= len(past) < start
            events = sum(outcomes[i] for i in past)
            if len(past) < pressure.RECALIBRATION["minimum_pairs"] or not (
                pressure.RECALIBRATION["minimum_events"] <= events < len(past)
            ):
                for i in range(start, stop):
                    self.assertEqual(self.recal.forecast[i][position], forecast[i])
                continue
            b0, b1 = _logistic_fit([logit(forecast[i]) for i in past], [outcomes[i] for i in past])
            for i in range(start, stop):
                self.assertAlmostEqual(
                    self.recal.forecast[i][position], _sigmoid(b0 + b1 * logit(forecast[i])), places=12
                )
                checked += 1
        self.assertTrue(excluded_somewhere, "the fixture never leaves an unobservable outcome out")
        self.assertGreater(checked, 0, "no block was recalibrated")

    def test_the_curves_stay_non_increasing_in_tau(self):
        for curve in self.recal.forecast:
            self.assertGreaterEqual(curve[0], curve[1])

    def test_the_outcomes_and_grid_are_unchanged(self):
        self.assertEqual(self.recal.outcomes, self.report.outcomes)
        self.assertEqual(self.recal.scored_dates, self.report.scored_dates)
        self.assertTrue(self.recal.model_name.endswith("+recalibrated"))


class OnsetAndLeadTimeTests(unittest.TestCase):
    def test_an_onset_follows_quiet_days(self):
        values = [0, 0, 0, 0, 0, 0, 7, 8, 0, 9, 0, 0, 0, 0, 0, 0, 6]
        rows = weekday_rows(values)
        found = pressure.onsets(rows, 5.0, [row.date for row in rows])
        self.assertEqual(found, (rows[6].date, rows[16].date))

    def test_lead_time_is_the_longest_horizon_that_flagged(self):
        day, other = date(2025, 10, 1), date(2025, 10, 15)
        forecasts = {
            1: {day: 0.9, other: 0.1},
            2: {day: 0.6, other: 0.1},
            3: {day: 0.1, other: 0.1},
            4: {day: 0.7, other: 0.1},
            5: {day: 0.2, other: 0.1},
        }
        result = pressure.lead_times(forecasts, [day, other], 0.5)
        self.assertEqual(
            result["per_onset"],
            [{"date": "2025-10-01", "lead_days": 4}, {"date": "2025-10-15", "lead_days": 0}],
        )
        self.assertEqual(result["flagged"], 1)
        self.assertEqual(result["mean_lead_days"], 2.0)


class ScorecardTests(unittest.TestCase):
    def test_the_scorecard_pairs_every_candidate_with_every_benchmark(self):
        rows = weekday_rows(spreads())
        report = backtest(rows)
        card = pressure.scorecard(
            {"a": report, "a_recal": pressure.recalibrated(report)},
            {"persistence_logistic": report},
            rows=rows,
            declaration=load_split_declaration(SPLITS),
            panel_sha256="0" * 64,
        )
        entry = card["candidates"]["a"]
        metrics = entry["metrics"]["5"]
        self.assertAlmostEqual(
            metrics["brier"],
            metrics["decomposition"]["reliability"]
            - metrics["decomposition"]["resolution"]
            + metrics["decomposition"]["uncertainty"],
            places=12,
        )
        self.assertEqual(sum(step["days"] for step in metrics["reliability_steps"]), metrics["scored_days"])
        paired = entry["paired"]["persistence_logistic"]["by_tau"]["5"]["paired_brier_difference"]
        self.assertEqual(paired["mean"], 0.0)
        self.assertIn("by_regime", paired["splits"])
        self.assertIn("by_day_type", paired["splits"])


if __name__ == "__main__":
    unittest.main()
