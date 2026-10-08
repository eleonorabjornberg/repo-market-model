"""The published distribution with the calendar-adjusted middle band (#418), read off its record.

The record `docs/runs/published_distribution_calendar_daily_h1.json` is the published distribution at
h = 1 with `conformal_pid_calendar` (declared in #243's addendum, confirmed on 2026 in #408) applied to
the interior quantiles. These tests need no panel: they read the record, the published daily record and
the #243 and #408 records. Re-scoring from the panel is `scripts/calendar_bands_418.py score`.
"""

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "docs" / "runs"
LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _json(name):
    return json.loads((RUNS / name).read_text(encoding="utf-8"))


class CalendarBandsRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = _json("published_distribution_calendar_daily_h1.json")
        cls.published = _json("published_distribution_daily_h1.json")
        cls.mod = _load("calendar_bands_418")

    def test_same_days_and_outcomes_as_the_published_record(self):
        mine, theirs = self.record["days"], self.published["days"]
        self.assertEqual([d["date"] for d in mine], [d["date"] for d in theirs])
        self.assertEqual([d["actual_bps"] for d in mine], [d["actual_bps"] for d in theirs])

    def test_the_90_percent_edges_move_only_where_the_sort_moves_them_and_only_outward(self):
        moved = 0
        for mine, theirs in zip(self.record["days"], self.published["days"]):
            q, p = mine["quantiles_bps"], theirs["quantiles_bps"]
            self.assertEqual(q, sorted(q), mine["date"])
            self.assertLessEqual(q[0], p[0], mine["date"])
            self.assertGreaterEqual(q[4], p[4], mine["date"])
            if (q[0], q[4]) != (p[0], p[4]):
                moved += 1
        self.assertEqual(moved, self.record["outer_edge_moved_days"])
        self.assertEqual(self.record["outer_band_unchanged"], moved == 0)
        self.assertTrue(self.record["outer_edge_moves_outward_only"])

    def test_the_table_reproduces_243_and_408_exactly(self):
        dev, conf = _json("interior_calibration_243.json"), _json("interior_confirmation_408.json")
        cand = "conformal_pid_calendar"
        before_after = self.record["before_after"]
        self.assertEqual(before_after["2018-2025"]["crps_after"], dev["candidates"][cand]["crps_bps"])
        self.assertEqual(before_after["2018-2025"]["pooled_gain"], dev["candidates"][cand]["pooled_gain"])
        self.assertEqual(before_after["2026"]["crps_after"], conf["candidates"][cand]["crps_bps"])
        self.assertEqual(before_after["2026"]["pooled_gain"], conf["candidates"][cand]["pooled_gain"])
        self.assertEqual(before_after["2018-2025"]["crps_before"], dev["published"]["crps_bps"])
        self.assertEqual(before_after["2026"]["crps_before"], conf["published"]["crps_bps"])

    def test_the_stored_crps_is_the_days_crps(self):
        for key, keep in (("2018-2025", lambda d: d < "2026"), ("2026", lambda d: d >= "2026")):
            for side, days in (("crps_before", self.published["days"]), ("crps_after", self.record["days"])):
                got = self.mod.mean_crps([d for d in days if keep(d["date"])])
                self.assertAlmostEqual(got, self.record["before_after"][key][side], places=9)

    def test_the_declaration_is_the_one_scored(self):
        self.assertEqual(self.record["candidate"], "conformal_pid_calendar")
        add = ROOT / "docs/declarations/interior_calibration_243_addendum.json"
        self.assertEqual(self.record["addendum_sha256"], self.mod.sha256(add))
        self.assertEqual(self.record["settings"], json.loads(add.read_text())["candidates"]["conformal_pid_calendar"])

    def test_the_page_is_what_the_record_renders(self):
        page = (ROOT / "docs/calendar_bands_418.md").read_text(encoding="utf-8")
        self.assertEqual(page, self.mod.render(self.record))

    def test_no_day_after_the_panel_end(self):
        self.assertEqual(self.record["days"][-1]["date"], "2026-09-03")


if __name__ == "__main__":
    unittest.main()
