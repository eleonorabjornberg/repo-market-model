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
"""

from __future__ import annotations

import json
import unittest
from datetime import date
from pathlib import Path

from repo_model.metrics import crps_from_quantiles

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


if __name__ == "__main__":
    unittest.main()
