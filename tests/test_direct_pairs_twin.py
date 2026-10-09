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
