"""The direct-pairs twin of the published model (#450): its declaration and the script's pure parts."""

from __future__ import annotations

import importlib.util
import json
import unittest
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location("direct_pairs_twin", REPO / "scripts" / "direct_pairs_twin.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


twin = _load()


class DeclarationTest(unittest.TestCase):
    def setUp(self):
        self.declaration = json.loads((REPO / "metadata" / "direct_pairs_twin.json").read_text(encoding="utf-8"))

    def test_scores_only_unlocked_days(self):
        scoring = self.declaration["scoring"]
        self.assertEqual(scoring["first_day"], "2018-06-29")
        self.assertEqual(date.fromisoformat(scoring["last_day"]), twin.END)
        self.assertLess(twin.END, date(2026, 1, 1))

    def test_decides_nothing_and_names_the_twin(self):
        self.assertEqual(self.declaration["twin"]["name"], "published_gbm_direct")
        self.assertTrue(self.declaration["decides"].startswith("nothing"))

    def test_the_published_record_is_untouched_by_the_twin(self):
        record = json.loads((REPO / "docs" / "runs" / "published_distribution_daily_h1.json").read_text("utf-8"))
        self.assertEqual(record["decides"], "nothing")
        self.assertNotIn("published_gbm_direct", json.dumps(record))


class PureTest(unittest.TestCase):
    def test_turning_points_need_both_moves_and_opposite_signs(self):
        flags = twin.turning_points([0, 3, 0, 1, 4, 9, 2.0], 2.0)
        self.assertEqual(flags, [None, True, False, False, False, True, None])

    def test_verdict_reads_the_interval(self):
        self.assertEqual(twin.verdict({"interval": [0.1, 0.3]}), "twin better")
        self.assertEqual(twin.verdict({"interval": [-0.3, -0.1]}), "twin worse")
        self.assertEqual(twin.verdict({"interval": [-0.1, 0.3]}), "no difference")

    def test_best_lag_prefers_the_smaller_lag_in_a_tie(self):
        self.assertEqual(twin._best({1: 0.5, 2: 0.5, 3: 0.1}), 1)
        self.assertEqual(twin._best({0: None, 2: 0.7}), 2)

    def test_lag_table_aligns_the_median_with_the_earlier_actual(self):
        series = [float((i * i * 7 + 3 * i) % 11) for i in range(40)]
        positions = list(range(10, 35))
        table = twin._lag_table([series[p - 2] for p in positions], series, positions)
        self.assertAlmostEqual(table[2], 1.0)
        self.assertEqual(twin._best(table), 2)


class CutSeriesTest(unittest.TestCase):
    """The lag series stops at 2025-12-31 (#470, the locked-day read of #457).

    Recorded mutation: `cut_series` returned `[row.spread_bps for row in rows]` (the `if row.date <= END` dropped);
    `test_no_day_after_the_end_enters_the_series` then raised `AssertionError` (the lists differ: seven spreads against the four to 2025-12-31).
    """

    @staticmethod
    def rows():
        from types import SimpleNamespace
        days = [date(2025, 12, 24), date(2025, 12, 29), date(2025, 12, 30), date(2025, 12, 31),
                date(2026, 1, 2), date(2026, 1, 5), date(2026, 1, 6)]
        return [SimpleNamespace(date=d, spread_bps=float(i)) for i, d in enumerate(days)]

    def test_no_day_after_the_end_enters_the_series(self):
        rows = self.rows()
        series = twin.cut_series(rows)
        self.assertEqual(series, [0.0, 1.0, 2.0, 3.0])
        self.assertTrue(all(r.date <= twin.END for r in rows[:len(series)]))

    def test_the_last_days_have_no_lag_at_minus_three(self):
        series = twin.cut_series(self.rows())
        self.assertEqual(twin.lag_members([0, 1, 2, 3], series), [0])
        for k in twin.LAGS:
            for i in twin.lag_members([0, 1, 2, 3], series):
                self.assertLess([0, 1, 2, 3][i] - k, len(series))

    def test_the_last_scored_day_is_not_a_turning_point_by_a_2026_spread(self):
        self.assertIsNone(twin.turning_points(twin.cut_series(self.rows()), 0.5)[-1])


@unittest.skipUnless(Path("/opt/rmm-venv/bin/python").exists() or importlib.util.find_spec("sklearn"), "needs the ml extra")
class TwinSideTest(unittest.TestCase):
    def test_the_twin_differs_from_the_published_side_only_in_training_pairs(self):
        fto = twin._script("final_test_opening")
        live_record = fto._script("live_record")
        sides, _ = live_record._compare_sides(1)
        _name, _fit, features, _online, args = twin.twin_side(live_record)
        self.assertEqual(features, sides["published"][2])
        self.assertEqual(args.training_pairs_b, "direct")
        self.assertEqual(args.calibration_b, live_record.final_test.CRPS_CALIBRATION)


if __name__ == "__main__":
    unittest.main()
