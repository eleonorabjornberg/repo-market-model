"""H5 step 6 (#1030): the per-episode stress replay reads the published model from a committed record, and no locked day.

The replay is development data and a read of tracked records: no model is refitted. These tests pin the episode list,
the lockbox cut (no day after 2025-12-31), the level lookup, the band summary on hand cases, and that every published
number in the result is the number in `docs/runs/published_distribution_daily_h1.json`. B1, B2 and B1' are zero-parameter
functions of the panel (no record holds their daily quantiles); the test pins that they are the protocol's own functions
and that each is a legal forecast (sorted quantiles) on every replayed day.

Recorded mutation (2026-10-21, a lockbox guard): in `scripts/episode_replay_1030.py`, `episode_days` was changed to keep
days up to `date(2026, 12, 31)` instead of `LAST_DAY`; `test_no_locked_day_is_replayed` raised AssertionError (the 2026
days of the panel were in the 2025 turn's window). Reverted.
"""

import importlib.util
import json
import unittest
from datetime import date, timedelta
from pathlib import Path

from panel_cache import published_build

import legacy_day_types

# this module reproduces legacy figures: the pre-#1135 day types (see tests/legacy_day_types.py)
setUpModule, tearDownModule = legacy_day_types.setUpModule, legacy_day_types.tearDownModule

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("episode_replay_1030_script", ROOT / "scripts" / "episode_replay_1030.py")
er = importlib.util.module_from_spec(spec)
spec.loader.exec_module(er)

RECORD = ROOT / "docs" / "runs" / "published_distribution_daily_h1.json"


def weekdays(first, last):
    out, day = [], first
    while day <= last:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


class TestEpisodeList(unittest.TestCase):
    def test_the_episodes_are_the_directives(self):
        names = [name for name, _, _ in er.EPISODES]
        self.assertEqual(names, ["2018 year-end turn", "September 2019", "March 2020", "2024 year-end turn", "2025 year-end turn"])
        windows = {name: (first, last) for name, first, last in er.EPISODES}
        self.assertEqual(windows["September 2019"], (date(2019, 9, 16), date(2019, 9, 18)))
        self.assertEqual(windows["March 2020"], (date(2020, 3, 11), date(2020, 3, 17)))

    def test_no_locked_day_is_replayed(self):
        days = er.episode_days(weekdays(date(2018, 12, 1), date(2026, 3, 1)))
        replayed = [d for window in days.values() for d in window]
        self.assertTrue(replayed)
        self.assertLessEqual(max(replayed), date(2025, 12, 31))
        self.assertLess(max(replayed), date(2026, 1, 1))
        self.assertEqual(days["2025 year-end turn"][-1], date(2025, 12, 31))

    def test_only_panel_days_inside_a_window_are_kept(self):
        days = er.episode_days([date(2019, 9, 13), date(2019, 9, 16), date(2019, 9, 18), date(2019, 9, 19)])
        self.assertEqual(days["September 2019"], [date(2019, 9, 16), date(2019, 9, 18)])
        self.assertEqual(days["March 2020"], [])


class TestLevels(unittest.TestCase):
    def test_a_level_is_read_exactly(self):
        self.assertEqual(er.levels_at([0.05, 0.25, 0.5, 0.75, 0.95], [1, 2, 3, 4, 5]), [1, 3, 5])

    def test_a_missing_level_is_refused(self):
        with self.assertRaises(ValueError):
            er.levels_at([0.1, 0.5, 0.9], [1, 2, 3])

    def test_unequal_lengths_are_refused(self):
        with self.assertRaises(ValueError):
            er.levels_at([0.05, 0.5, 0.95], [1, 2])


class TestBandSummary(unittest.TestCase):
    def rows(self, items):
        base = date(2019, 9, 16)
        return [{"date": (base + timedelta(days=i)).isoformat(), "print_bp": p, "q05": lo, "q50": mid, "q95": hi}
                for i, (p, lo, mid, hi) in enumerate(items)]

    def test_misses_are_counted_above_q95_and_below_q05(self):
        s = er.band_summary(self.rows([(33, 0, 5, 14), (315, 2, 6, 12), (45, 2, 10, 33), (-3, 0, 3, 9)]))
        self.assertEqual(s["days"], 4)
        self.assertEqual(s["above_q95"], 3)
        self.assertEqual(s["below_q05"], 1)

    def test_a_print_on_the_edge_is_inside(self):
        s = er.band_summary(self.rows([(14, 0, 5, 14), (0, 0, 5, 14)]))
        self.assertEqual((s["above_q95"], s["below_q05"]), (0, 0))

    def test_the_band_after_the_first_miss(self):
        s = er.band_summary(self.rows([(33, 0, 5, 14), (315, 2, 6, 12), (45, 2, 10, 33)]))
        self.assertEqual(s["first_miss"], "2019-09-16")
        self.assertEqual(s["width_first_day"], 14)
        self.assertEqual(s["width_after_first_miss"], [10, 31])
        self.assertTrue(s["widened_after_first_miss"])

    def test_no_miss_no_widening_claim(self):
        s = er.band_summary(self.rows([(5, 0, 5, 14), (6, 0, 5, 14)]))
        self.assertIsNone(s["first_miss"])
        self.assertEqual(s["width_after_first_miss"], [])
        self.assertIsNone(s["widened_after_first_miss"])


class TestTheRecord(unittest.TestCase):
    def test_an_unsorted_record_is_refused(self):
        bad = {"levels": [0.05, 0.25, 0.5, 0.75, 0.95],
               "days": [{"date": "2019-09-16", "actual_bps": 1.0, "quantiles_bps": [3, 2, 1, 0, -1]}]}
        with self.assertRaises(ValueError):
            er.published_days(bad)

    def test_the_record_is_read_by_target_day(self):
        record = json.loads(RECORD.read_text(encoding="utf-8"))
        days = er.published_days(record)
        first = record["days"][0]
        self.assertEqual(days[date.fromisoformat(first["date"])]["print_bp"], first["actual_bps"])
        self.assertEqual(days[date.fromisoformat(first["date"])]["q50"], first["quantiles_bps"][2])


class TestTheReplay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build = published_build()
        cls.record = json.loads(RECORD.read_text(encoding="utf-8"))
        cls.result = er.replay(build["rows"], cls.record, build["path"])

    def test_every_published_number_is_the_records(self):
        published = er.published_days(self.record)
        rows = [r for episode in self.result["episodes"] for r in episode["rows"]]
        self.assertTrue(rows)
        for r in rows:
            want = published[date.fromisoformat(r["date"])]
            for key in ("q05", "q50", "q95"):
                self.assertEqual(r["published"][key], want[key])
            self.assertEqual(r["print_bp"], want["print_bp"])

    def test_the_prints_are_the_panels_spreads(self):
        spreads = {row.date.isoformat(): row.spread_bps for row in published_build()["rows"]}
        for episode in self.result["episodes"]:
            for r in episode["rows"]:
                self.assertAlmostEqual(r["print_bp"], spreads[r["date"]], places=9)

    def test_the_panel_is_the_records(self):
        self.assertEqual(self.result["panel_sha256"], self.record["panel_sha256"])

    def test_every_model_is_a_legal_forecast_on_every_day(self):
        for episode in self.result["episodes"]:
            for r in episode["rows"]:
                for name in ("published", "B1", "B2", "B1_prime"):
                    self.assertLessEqual(r[name]["q05"], r[name]["q50"])
                    self.assertLessEqual(r[name]["q50"], r[name]["q95"])

    def test_every_row_carries_its_calendar_status(self):
        self.assertIn("provisional", self.result["status"]["published"])
        for name in ("published", "B1", "B2", "B1_prime"):
            self.assertTrue(self.result["status"][name])
        # B2 and B1' read the target day's reporting type; the published model and B1 read no calendar day
        self.assertTrue(self.result["status"]["B1"].startswith("provisional"))
        self.assertTrue(self.result["status"]["B2"].startswith("not provisional"))
        self.assertTrue(self.result["status"]["B1_prime"].startswith("not provisional"))

    def test_no_locked_day_is_in_the_result(self):
        dates = [r["date"] for e in self.result["episodes"] for r in e["rows"]]
        self.assertLess(max(dates), "2026-01-01")

    def test_the_benchmarks_are_the_protocols_functions(self):
        from repo_model import protocol_benchmarks as pb
        from repo_model.scoring_protocol import GRID

        build = published_build()
        rows = build["rows"]
        position = {row.date: i for i, row in enumerate(rows)}
        r = self.result["episodes"][1]["rows"][1]  # the 2019-09-17 target day
        self.assertEqual(r["date"], "2019-09-17")
        decision = position[date(2019, 9, 17)] - 1
        b1 = pb.b1_forecast(rows, decision, registry=er.registry(), decision_time=er.DECISION_TIME)[1]
        self.assertEqual(r["B1"]["q95"], b1[GRID.index(0.95)])
        self.assertEqual(r["B1"]["q05"], b1[GRID.index(0.05)])

    def test_the_episode_summaries_follow_the_rows(self):
        for episode in self.result["episodes"]:
            for name in ("published", "B1", "B2", "B1_prime"):
                s = episode["summary"][name]
                self.assertEqual(s["days"], len(episode["rows"]))
                self.assertEqual(s["above_q95"], sum(1 for r in episode["rows"] if r["print_bp"] > r[name]["q95"]))


if __name__ == "__main__":
    unittest.main()
