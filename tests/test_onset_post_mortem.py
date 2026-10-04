"""The onset post-mortem (#214): `scripts/onset_post_mortem.py`.

Descriptive only: these tests check that the post-mortem reads what it says it
reads, and that it refuses a locked day. They do not test a claim, because it
makes none.

Recorded mutation (CLAUDE.md, a leakage guard's call site): deleting the line
`require_unlocked(scored_dates, where="onset_post_mortem.onset_days")` in
`onset_days` makes
`OnsetPostMortemTests.test_onset_days_refuses_a_locked_scored_day` fail with
`AssertionError: LookAheadError not raised`.
"""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import date, time
from pathlib import Path

from repo_model import onset
from repo_model.data import DailyObservation, exceeds_bp
from repo_model.evaluation_splits import load_split_declaration
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
END = date(2025, 12, 31)
LOCKED = date(2026, 1, 5)


def _script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class OnsetPostMortemTests(unittest.TestCase):
    """On the measurement panel built from tracked fixtures, as the script builds it."""

    @classmethod
    def setUpClass(cls):
        from repo_model.scarcity import measurement_declaration, with_reserve_scarcity_state

        cls.pm = _script("onset_post_mortem")
        validation = _script("scarcity_validation")
        cls.declaration = load_split_declaration(ROOT / "metadata" / "evaluation_splits.json")
        with measurement_declaration(), tempfile.TemporaryDirectory() as directory:
            build, _digest, cls.registry, cls.decision = validation.build_measurement_panel(
                ROOT / "metadata" / "sources.json", Path(directory)
            )
            cls.rows = with_reserve_scarcity_state(build.observations)
            cls.history = cls.pm.gauge_history(cls.rows, cls.registry, decision_time=cls.decision)
            cls.series = cls.pm.as_of_reads(
                cls.rows, cls.registry, decision_time=cls.decision, minimum_history=cls.history, end=END
            )
            cls.scored = sorted(
                cls.pm.as_of_reads(
                    cls.rows,
                    cls.registry,
                    decision_time=cls.decision,
                    minimum_history=cls.pm.MINIMUM_HISTORY,
                    end=END,
                )
            )

    # -- the lockbox ---------------------------------------------------------

    def test_main_refuses_an_end_in_the_locked_tier_before_anything_is_built(self):
        with self.assertRaisesRegex(LookAheadError, r"^onset_post_mortem: scored day 2026-01-05"):
            self.pm.main(["--end", LOCKED.isoformat()])

    def test_the_as_of_reads_refuse_a_locked_scored_day(self):
        from repo_model.scarcity import measurement_declaration

        with measurement_declaration(), self.assertRaisesRegex(LookAheadError, "locked"):
            self.pm.as_of_reads(
                self.rows, self.registry, decision_time=self.decision, minimum_history=61, end=LOCKED
            )

    def test_onset_days_refuses_a_locked_scored_day(self):
        locked = [row.date for row in self.rows if END < row.date <= LOCKED]
        with self.assertRaises(LookAheadError):
            self.pm.onset_days(self.rows, self.scored + locked, self.declaration)

    def test_no_scored_day_is_locked(self):
        self.assertLessEqual(self.scored[-1], END)
        self.assertLessEqual(max(self.series), END)

    # -- the onsets ----------------------------------------------------------

    def test_the_primary_onsets_are_onset_flags(self):
        days = self.pm.onset_days(self.rows, self.scored, self.declaration)
        flags = onset.onset_flags(self.rows)
        expected = [row.date for row, flag in zip(self.rows, flags) if flag and row.date in set(self.scored)]
        self.assertEqual(days[self.pm.PRIMARY], expected)
        self.assertTrue(expected)

    def test_the_descriptive_onsets_follow_one_calm_day_and_hold_the_primary_ones(self):
        days = self.pm.onset_days(self.rows, self.scored, self.declaration)
        position = {row.date: index for index, row in enumerate(self.rows)}
        for day in days[self.pm.DESCRIPTIVE]:
            index = position[day]
            with self.subTest(day=day):
                self.assertTrue(exceeds_bp(self.rows[index].spread_bps, onset.ONSET_THRESHOLD_BP))
                self.assertFalse(exceeds_bp(self.rows[index - 1].spread_bps, onset.ONSET_THRESHOLD_BP))
        self.assertLessEqual(set(days[self.pm.PRIMARY]), set(days[self.pm.DESCRIPTIVE]))

    # -- the as-of reads -----------------------------------------------------

    def test_the_scored_grid_is_the_published_records(self):
        record = json.loads((ROOT / "docs" / "runs" / "pressure_model_v1_h1.json").read_text())
        self.assertEqual(len(self.scored), record["folds"]["count"])
        self.assertEqual(self.scored[0].isoformat(), record["folds"]["first"]["scored_date"])
        self.assertEqual(self.scored[-1].isoformat(), record["folds"]["last"]["scored_date"])

    def test_the_state_is_the_one_scarcity_reads_as_of(self):
        from repo_model.scarcity import measurement_declaration, pressure_days_by_state

        with measurement_declaration():
            days = pressure_days_by_state(
                self.rows,
                registry=self.registry,
                decision_time=self.decision,
                minimum_history=61,
                end=END,
            )
        for day in days:
            read = self.series[day.day]
            self.assertEqual(read["state"], None if day.state is None else int(day.state))
            self.assertEqual(read["state_read_date"], day.read_date)
            self.assertLess(read["state_read_date"], day.day)

    def test_the_calendar_and_settlement_are_the_scored_days_own(self):
        position = {row.date: index for index, row in enumerate(self.rows)}
        for day in self.scored[::37]:
            values = self.rows[position[day]].values
            with self.subTest(day=day):
                for column in (*self.pm.CALENDAR, self.pm.COUPONS):
                    self.assertEqual(self.series[day][column], values[column])

    def test_the_gauge_series_starts_on_its_first_readable_day(self):
        first = min(self.series)
        self.assertLess(first, self.scored[0])
        self.assertGreater(self.history, 1)
        from repo_model.asof import fold_grid

        dates = [row.date for row in self.rows]
        earlier = fold_grid(
            dates, self.registry, decision_time=self.decision, minimum_history=self.history - 1, horizon=1
        )[0]
        self.assertLess(dates[earlier], first)

    # -- the lead ------------------------------------------------------------

    def test_the_lead_counts_the_run_of_states_two_and_three(self):
        days = [date(2025, 1, d) for d in range(2, 10)]
        states = [1, 2, 3, 3, None, 2, 2, 0]
        reads = {d: {"index": k, "state": s} for k, (d, s) in enumerate(zip(days, states))}
        self.assertEqual(
            self.pm.gauge_lead(days, reads, days[3]),
            {"run_start": days[1], "lead_days": 2, "censored": False},
        )
        self.assertEqual(
            self.pm.gauge_lead(days, reads, days[6]),
            {"run_start": days[5], "lead_days": 1, "censored": False},
        )
        self.assertIsNone(self.pm.gauge_lead(days, reads, days[7]))
        self.assertIsNone(self.pm.gauge_lead(days, reads, days[4]))

    def test_a_run_from_the_series_first_day_is_censored(self):
        days = [date(2025, 1, d) for d in range(2, 6)]
        reads = {d: {"index": k, "state": 2} for k, d in enumerate(days)}
        lead = self.pm.gauge_lead(days, reads, days[3])
        self.assertEqual(lead, {"run_start": days[0], "lead_days": 3, "censored": True})
        self.assertEqual(self.pm._lead_text(lead), "at least 3 days (censored at the panel start)")

    def test_an_episode_whose_gauge_turns_after_its_first_onset_says_so(self):
        days = [date(2025, 1, d) for d in range(2, 8)]
        states = [1, 1, 2, 2, 3, 3]
        reads = {d: {"index": k, "state": s} for k, (d, s) in enumerate(zip(days, states))}
        rows = [
            {"date": days[1].isoformat(), "lead": None, "state": 1},
            {"date": days[5].isoformat(), "lead": {"run_start": days[2].isoformat(), "lead_days": 3, "censored": False}, "state": 3},
        ]
        for key in ("quarter_end", "month_end", "tax_date", "coupon_settlement"):
            for row in rows:
                row[key] = False
        for row in rows:
            row["gauge_tight"] = row["state"] in (2, 3)
        episode = self.pm.summary(rows, days, reads)["episodes"]["2025"]
        self.assertEqual(episode["first_onset"], days[1].isoformat())
        self.assertEqual(episode["gauge_entered_states_2_3"], days[2].isoformat())
        self.assertTrue(episode["entered_after_the_onset"])
        self.assertIsNone(episode["lead"])

    # -- the record check ----------------------------------------------------

    def test_the_record_check_refuses_a_forecast_that_differs(self):
        record = {
            "folds": {"count": 2},
            "metrics": {
                "by_tau": {
                    "5": {"brier": 0.25 * 0.25 / 2 + 0.5 * 0.5 / 2},
                    "20": {
                        "reporting": "event_list",
                        "events": [
                            {
                                "forecasts": [
                                    {
                                        "scored_date": "2025-01-03",
                                        "probability": {self.pm.V1: 0.1, self.pm.PERSISTENCE: 0.2},
                                    }
                                ]
                            }
                        ],
                    },
                }
            },
            "benchmarks": {self.pm.PERSISTENCE: {"by_tau": {"5": {"benchmark_brier": 0.5 * 0.5}}}},
        }
        forecasts = {
            "model_name": self.pm.V1,
            "scored_dates": ["2025-01-02", "2025-01-03"],
            "outcomes": {"5": [0, 1]},
            self.pm.V1: {"5": [0.25, 0.5], "20": [0.0, 0.1]},
            self.pm.PERSISTENCE: {"5": [0.5, 0.5], "20": [0.0, 0.2]},
        }
        self.assertEqual(self.pm.check_against_record(forecasts, record)["event_list_probabilities_compared"], 2)
        forecasts[self.pm.V1]["20"][1] = 0.1000001
        with self.assertRaisesRegex(ValueError, "event-list"):
            self.pm.check_against_record(forecasts, record)
        forecasts[self.pm.V1]["20"][1] = 0.1
        forecasts[self.pm.PERSISTENCE]["5"][0] = 0.4
        with self.assertRaisesRegex(ValueError, "Brier"):
            self.pm.check_against_record(forecasts, record)


if __name__ == "__main__":
    unittest.main()
