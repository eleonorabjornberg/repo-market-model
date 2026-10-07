"""The published distribution's daily forecasts at h = 1 (#246).

Eleonora's ruling of 6 October 2026 on #246: readers should see what the model
forecast each day, what actually happened, and how far off it was. No earlier
record holds the per-day quantiles, so `docs/runs/published_distribution_daily_h1.json`
keeps them: for every scored day from 2018-06-29 to 2026-09-03, the published
distribution's five quantiles at h = 1 and the actual SOFR - IORB. It is built
by `scripts/forecast_daily.py` with `final_test_opening.distribution_walk` and
`live_record._compare_sides(1)` on the published panel, and decides nothing.

These tests pin that its per-day CRPS reproduces both published series exactly
(the h = 1 CRPS record's pre-2026 losses and `final_test_near_blind.json`'s
window losses), and that no day after the panel end is in it.

#290 extends the script to `--horizon H` (2 to 5): `docs/runs/published_distribution_daily_h{H}.json`
holds the same distribution's days over the h = 1 CRPS record's window, 2018-06-29 to 2025-12-31,
and no later day. The walk runs to the panel end because its calibration state is sequential, and
its mean CRPS over the opened 2026 days must equal the final test's reported cell exactly before
anything is written.

Mutation record (disposable copy, `-B`, control green before and after):

1. `scripts/forecast_daily.py`, `reproduction_check_horizon`: `mean != cell["crps_published_bps"]`
   -> `False`, so a walk whose opened-window mean differs from the final test's cell passes.
   Kills `HorizonReproductionTests.test_a_mean_that_differs_from_the_final_tests_cell_is_refused`
   with `AssertionError` (`ValueError not raised`).
"""

from __future__ import annotations

import json
import unittest
from datetime import date
from pathlib import Path

from repo_model.metrics import crps_from_quantiles

import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "docs" / "runs"
RECORD = RUNS / "published_distribution_daily_h1.json"
CRPS_RECORD = RUNS / "compare_persistence_vs_gbm_conformal_pid_nested_funding_crps.json"
FINAL_TEST = RUNS / "final_test_near_blind.json"
PANEL_END = date(2026, 9, 3)


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class DailyRecordTests(unittest.TestCase):
    """The record: every scored day, its quantiles and the actual, nothing after the panel end."""

    @classmethod
    def setUpClass(cls):
        cls.record = _load(RECORD)

    def test_the_pre_2026_losses_reproduce_the_crps_record_exactly(self):
        expected = {entry["scored_date"]: entry["loss_b_bps"]
                    for entry in _load(CRPS_RECORD)["comparison"]["per_origin"]}
        ours = {day["date"]: crps_from_quantiles(self.record["levels"], day["quantiles_bps"],
                                                 day["actual_bps"])
                for day in self.record["days"] if day["date"] < "2026-01-01"}
        self.assertEqual(set(ours), set(expected))
        mismatched = [day for day in sorted(ours) if ours[day] != expected[day]]
        self.assertEqual(mismatched, [])

    def test_the_window_losses_reproduce_the_final_test_exactly(self):
        expected = {entry["scored_date"]: entry["loss_b_bps"]
                    for entry in _load(FINAL_TEST)["primary"]["window_per_origin"]}
        ours = {day["date"]: crps_from_quantiles(self.record["levels"], day["quantiles_bps"],
                                                 day["actual_bps"])
                for day in self.record["days"] if day["date"] >= "2026-01-01"}
        self.assertEqual(set(ours), set(expected))
        mismatched = [day for day in sorted(ours) if ours[day] != expected[day]]
        self.assertEqual(mismatched, [])

    def test_no_day_after_the_panel_end_is_in_the_record(self):
        days = [date.fromisoformat(day["date"]) for day in self.record["days"]]
        self.assertEqual(days, sorted(set(days)))
        self.assertEqual(days[0], date(2018, 6, 29))
        self.assertEqual(days[-1], PANEL_END)
        self.assertEqual(self.record["last"], PANEL_END.isoformat())

    def test_every_day_holds_five_ordered_quantiles_and_the_actual(self):
        self.assertEqual(self.record["levels"], [0.05, 0.25, 0.5, 0.75, 0.95])
        for day in self.record["days"]:
            with self.subTest(day=day["date"]):
                self.assertEqual(set(day), {"date", "quantiles_bps", "actual_bps"})
                self.assertEqual(len(day["quantiles_bps"]), 5)
                self.assertEqual(day["quantiles_bps"], sorted(day["quantiles_bps"]))
                self.assertIsInstance(day["actual_bps"], float)

    def test_the_record_is_the_published_distribution_on_the_published_panel(self):
        crps = _load(CRPS_RECORD)
        self.assertEqual(self.record["horizon"], 1)
        self.assertEqual(self.record["panel_sha256"], crps["panel"]["sha256"])
        self.assertEqual(self.record["published_record"], str(CRPS_RECORD.relative_to(ROOT)))
        self.assertEqual(self.record["decides"], "nothing")
        self.assertEqual(self.record["directive"], "#246")


def _script():
    spec = importlib.util.spec_from_file_location("forecast_daily_h", ROOT / "scripts" / "forecast_daily.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class HorizonRecordTests(unittest.TestCase):
    """The h = 2 to 5 records (#290): the window, the levels and the panel."""

    def test_each_record_ends_inside_the_window_and_holds_ordered_quantiles(self):
        for horizon in range(2, 6):
            record = _load(RUNS / f"published_distribution_daily_h{horizon}.json")
            with self.subTest(horizon=horizon):
                dates = [day["date"] for day in record["days"]]
                self.assertEqual(dates, sorted(set(dates)))
                self.assertEqual(dates[0] >= "2018-06-29", True)
                self.assertLessEqual(dates[-1], "2025-12-31")
                self.assertEqual(record["last"], dates[-1])
                self.assertEqual(record["horizon"], horizon)
                self.assertEqual(record["levels"], [0.05, 0.25, 0.5, 0.75, 0.95])
                for day in record["days"]:
                    self.assertEqual(day["quantiles_bps"], sorted(day["quantiles_bps"]))

    def test_the_opened_window_mean_reproduces_the_final_tests_cell(self):
        final = _load(FINAL_TEST)
        for cell in final["crps_reported_only"]:
            record = _load(RUNS / f"published_distribution_daily_h{cell['horizon']}.json")
            with self.subTest(horizon=cell["horizon"]):
                self.assertEqual(record["reproduces"]["mean_crps_bps"], cell["crps_published_bps"])
                self.assertEqual(record["reproduces"]["days"], cell["days"])
                self.assertEqual(record["published_record"], cell["published_record"])


class HorizonReproductionTests(unittest.TestCase):
    def setUp(self):
        self.script = _script()
        self.levels = [0.05, 0.25, 0.5, 0.75, 0.95]
        final = _load(FINAL_TEST)
        self.cell = [c for c in final["crps_reported_only"] if c["horizon"] == 2][0]

    def _days(self, count, actual):
        return [{"date": "2026-02-%02d" % (1 + index % 27), "actual_bps": actual,
                 "quantiles_bps": [-2.0, -1.0, 0.0, 1.0, 2.0]} for index in range(count)]

    def test_a_mean_that_differs_from_the_final_tests_cell_is_refused(self):
        days = self._days(self.cell["days"], 0.0)
        with self.assertRaises(ValueError):
            self.script.reproduction_check_horizon(self.levels, days, 2)

    def test_a_day_count_that_differs_is_refused(self):
        with self.assertRaises(ValueError):
            self.script.reproduction_check_horizon(self.levels, self._days(3, 0.0), 2)


if __name__ == "__main__":
    unittest.main()
