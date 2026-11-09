"""The quarter-end band diagnosis of (s3c-ann-net) (#1533): `scripts/qe_diagnosis_1533.py`.

The tests fix the arithmetic on hand cases: which pool members set a tail (they reproduce `protocol_benchmarks.empirical_quantiles` exactly),
the quarter-end event of a day, the leave-one-event-out range, the stationary resample, the count of distinct events, the paired path
steps, and the guard that the regenerated walk is the 1363 walk.

Recorded mutation (the guard this script adds, that a regenerated walk equals the 1363 walk, so the study reads the same forecasts):

* `verify_walk`, the test `if digest != declared["sha256"]:` replaced by `if False:`: `test_a_walk_that_differs_from_the_1363_walk_is_refused`
  fails with `AssertionError` (`ValueError not raised`); restored, it passes.
* `wrap_walk`, the line `return result` replaced by `return None`: `test_the_wrapper_returns_the_walk_unchanged` fails with `AssertionError`
  (`None is not <the walk>`); restored, it passes.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import random
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("qe_diagnosis_1533_script", REPO / "scripts" / "qe_diagnosis_1533.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model import protocol_benchmarks as pb, scoring_protocol as sp  # noqa: E402


class SupportTests(unittest.TestCase):
    def test_the_setters_reproduce_the_interpolated_quantile(self):
        rng = random.Random(7)
        for n in (2, 5, 37, 100, 1001, 1500):
            pool = [rng.gauss(0, 1) for _ in range(n)]
            ordered = sorted(pool)
            expected = dict(zip(sp.GRID, pb.empirical_quantiles(ordered)))
            for tau in (0.01, 0.05, 0.95, 0.99):
                low, weight = script.support_position(n, tau)
                value = ordered[low] if not weight else ordered[low] + weight * (ordered[low + 1] - ordered[low])
                self.assertEqual(value, expected[tau])

    def test_a_whole_position_has_one_setter_and_a_fraction_two(self):
        self.assertEqual(script.setter_ranks(101, 0.05), (5,))  # position 5.0 exactly
        self.assertEqual(script.setter_ranks(100, 0.05), (4, 5))  # position 4.95
        self.assertEqual(script.neighbour_ranks(100, 0.05), (3, 6))

    def test_the_tail_zone_is_the_members_beyond_the_quantile(self):
        self.assertEqual(script.zone_ranks(100, 0.05), range(0, 5))  # ranks 0..4 are below q05
        self.assertEqual(script.zone_ranks(100, 0.95), range(95, 100))  # ranks 95..99 are above the position 94.05
        self.assertEqual(script.zone_ranks(101, 0.95), range(96, 101))  # position 95.0: 96.. are strictly beyond

    def test_ranks_order_ties_by_position(self):
        self.assertEqual(script.rank_order([3.0, 1.0, 1.0, 2.0]), [1, 2, 3, 0])


class EventTests(unittest.TestCase):
    def test_the_two_turn_days_of_a_quarter_end_are_one_event(self):
        # 2021-03-31 (Wed) and 2021-04-01 (Thu) are the last business day of March and the first of April.
        self.assertEqual(script.quarter_end_event(date(2021, 3, 31)), "2021-03")
        self.assertEqual(script.quarter_end_event(date(2021, 4, 1)), "2021-03")
        # the year end crosses the year
        self.assertEqual(script.quarter_end_event(date(2020, 12, 31)), "2020-12")
        self.assertEqual(script.quarter_end_event(date(2021, 1, 4)), "2020-12")

    def test_other_days_are_not_in_an_event(self):
        self.assertIsNone(script.quarter_end_event(date(2021, 5, 14)))
        self.assertIsNone(script.quarter_end_event(date(2021, 4, 30)))  # a month-end turn that is not a quarter-end

    def test_distinct_events_chain_nearby_days(self):
        rows = [10, 11, 13, 40, 90, 95, 99]
        self.assertEqual(script.distinct_clusters(rows, gap=5, events=[None] * 7), 3)
        # members of one quarter-end event count once, however far apart their rows are
        self.assertEqual(script.distinct_clusters([10, 300], gap=5, events=["2021-03", "2021-03"]), 1)
        self.assertEqual(script.distinct_clusters([10, 300], gap=5, events=["2021-03", "2021-06"]), 2)
        self.assertEqual(script.distinct_clusters([], gap=5, events=[]), 0)


class InfluenceTests(unittest.TestCase):
    def test_the_leave_one_out_range_names_the_events(self):
        cells = [("a", 1.0), ("a", 1.0), ("b", 0.0), ("c", 0.0), ("c", 0.0), ("c", 0.0)]

        def mean(sub):
            return sum(v for _e, v in sub) / len(sub)

        out = script.leave_one_out(cells, key=lambda c: c[0], statistic=mean)
        self.assertAlmostEqual(out["full"], 2 / 6)
        self.assertAlmostEqual(out["min"], 0.0)  # leaving a out
        self.assertEqual(out["min_event"], "a")
        self.assertAlmostEqual(out["max"], 2 / 3)  # leaving c out
        self.assertEqual(out["max_event"], "c")
        self.assertEqual(out["events"], 3)

    def test_the_greedy_drop_removes_the_most_influential_first(self):
        cells = [("a", 1.0)] * 2 + [("b", 0.8)] * 2 + [("c", 0.0)] * 2 + [("d", 0.1)] * 2

        def mean(sub):
            return sum(v for _e, v in sub) / len(sub)

        drops = script.greedy_drop(cells, key=lambda c: c[0], statistic=mean, count=2)
        self.assertEqual([d["event"] for d in drops], ["a", "b"])
        self.assertAlmostEqual(drops[0]["value"], (1.6 + 0.2) / 6)

    def test_the_cluster_bootstrap_resamples_whole_events(self):
        cells = [("a", 1.0)] * 5 + [("b", 0.0)] * 5
        lo, hi = script.event_interval(cells, key=lambda c: c[0], statistic=lambda s: sum(v for _e, v in s) / len(s), reps=300, seed=3)
        # only the four mixes of two whole events are possible: 0, 0.5, 0.5, 1
        self.assertEqual((lo, hi), (0.0, 1.0))


class BootstrapTests(unittest.TestCase):
    def test_the_stationary_indices_are_in_range_and_wrap(self):
        rng = random.Random(1)
        idx = script.stationary_indices(50, 10.0, rng)
        self.assertEqual(len(idx), 50)
        self.assertTrue(all(0 <= i < 50 for i in idx))
        runs = sum(1 for a, b in zip(idx, idx[1:]) if b == (a + 1) % 50)
        self.assertGreater(runs, 20)  # blocks of mean length 10: most steps continue a block

    def test_a_block_of_one_is_the_iid_bootstrap(self):
        rng = random.Random(1)
        idx = script.stationary_indices(2000, 1.0, rng)
        runs = sum(1 for a, b in zip(idx, idx[1:]) if b == (a + 1) % 2000)
        self.assertLess(runs, 20)

    def test_the_tail_interval_brackets_the_estimate_and_is_wider_in_the_tail(self):
        rng = random.Random(5)
        pool = [rng.gauss(0, 1) for _ in range(800)]
        out = script.pool_tail_intervals(pool, (0.25, 0.5, 0.99), block=10.0, reps=200, seed=1533)
        for tau in (0.25, 0.5, 0.99):
            estimate, lo, hi = out[tau]
            self.assertLessEqual(lo, estimate)
            self.assertLessEqual(estimate, hi)
        width = {tau: out[tau][2] - out[tau][1] for tau in out}
        self.assertGreater(width[0.99], width[0.5])

    def test_the_same_seed_gives_the_same_interval(self):
        pool = [float(i % 17) + (i % 5) / 7 for i in range(300)]
        a = script.pool_tail_intervals(pool, (0.05, 0.95), block=10.0, reps=50, seed=1533)
        b = script.pool_tail_intervals(pool, (0.05, 0.95), block=10.0, reps=50, seed=1533)
        self.assertEqual(a, b)


class PathTests(unittest.TestCase):
    def test_a_step_is_new_when_the_information_read_changes(self):
        self.assertTrue(script.information_changed({"settlement_coupon": 0, "net": 0.0}, {"settlement_coupon": 1, "net": 12.0}))
        self.assertFalse(script.information_changed({"settlement_coupon": 1, "net": 12.0}, {"settlement_coupon": 1, "net": 12.0}))

    def test_the_sign_and_size_kept_reading(self):
        self.assertTrue(script.misplaced(4.0, 3.5))
        self.assertFalse(script.misplaced(4.0, 2.0))  # the size fell below 80 per cent
        self.assertFalse(script.misplaced(4.0, -4.0))  # the sign flipped
        self.assertFalse(script.misplaced(0.0, 0.0))


class WalkGuardTests(unittest.TestCase):
    def _file(self, payload: bytes) -> Path:
        directory = Path(tempfile.mkdtemp())
        path = directory / "development.json"
        path.write_bytes(payload)
        return path

    def test_a_walk_that_matches_the_1363_walk_passes(self):
        payload = b'{"refits":2}\n'
        path = self._file(payload)
        record = {"walk_files": {"development": {"sha256": hashlib.sha256(payload).hexdigest(), "refits": 2}}}
        script.verify_walk(path, "development", record, refits=2)

    def test_a_walk_that_differs_from_the_1363_walk_is_refused(self):
        path = self._file(b'{"refits":2}\n')
        record = {"walk_files": {"development": {"sha256": "0" * 64, "refits": 2}}}
        with self.assertRaises(ValueError):
            script.verify_walk(path, "development", record, refits=2)

    def test_a_different_refit_count_is_refused(self):
        payload = b"x"
        path = self._file(payload)
        record = {"walk_files": {"development": {"sha256": hashlib.sha256(payload).hexdigest(), "refits": 89}}}
        with self.assertRaises(ValueError):
            script.verify_walk(path, "development", record, refits=88)

    def test_the_wrapper_returns_the_walk_unchanged(self):
        sentinel = object()
        seen = []
        wrapped = script.wrap_walk(lambda *a, **k: sentinel, seen)
        self.assertIs(wrapped(1, 2, x=3), sentinel)
        self.assertEqual(len(seen), 1)
        self.assertIs(seen[0][0], sentinel)
        self.assertEqual(seen[0][1], (1, 2))
        self.assertEqual(seen[0][2], {"x": 3})

    def test_the_declaration_is_committed_json_with_the_declared_block_length(self):
        declared = json.loads((REPO / "metadata" / "qe_diagnosis_1533.json").read_text(encoding="utf-8"))
        self.assertEqual(declared["item_2_tail_support"]["bootstrap"]["block_length_declared_here_before_any_number"], script.BLOCK)
        self.assertEqual(declared["item_2_tail_support"]["bootstrap"]["resamples"], script.POOL_REPS)
        self.assertEqual(tuple(declared["definitions"]["tails"]), script.TAILS)


class RecordedResultTests(unittest.TestCase):
    """The committed result reads the 1363 walk and is internally consistent."""

    @classmethod
    def setUpClass(cls):
        cls.result = json.loads((REPO / "docs" / "research" / "qe-diagnosis-1533" / "result.json").read_text(encoding="utf-8"))
        cls.record = json.loads((REPO / "docs" / "research" / "candidate-calibration-1363" / "result.json").read_text(encoding="utf-8"))

    def test_the_walks_are_the_1363_walks(self):
        for window, entry in self.result["walk_files"].items():
            self.assertEqual(entry["sha256"], self.record["walk_files"][window]["sha256"])
            self.assertEqual(entry["refits"], self.record["walk_files"][window]["refits"])

    def test_the_event_table_adds_up_to_the_group(self):
        for window in self.result["windows"].values():
            item = window["item1"]
            self.assertEqual(sum(e["n"] for e in item["events_table"]), item["cells_in_group"])
            self.assertEqual(len(item["events_table"]), item["events"])

    def test_the_leave_one_out_range_brackets_the_full_figure(self):
        for window in self.result["windows"].values():
            for entry in window["item1"]["leave_one_out_group"]["pooled"].values():
                if isinstance(entry, dict):
                    self.assertLessEqual(entry["min"], entry["full"] + 1e-9)
                    self.assertLessEqual(entry["full"], entry["max"] + 1e-9)

    def test_every_tail_row_has_setters_of_the_interpolated_ranks(self):
        rows = json.loads((REPO / "docs" / "research" / "qe-diagnosis-1533" / "tail-support.json").read_text(encoding="utf-8"))
        for row in rows["development"][:400]:
            self.assertEqual(len(row["setters"]), len(script.setter_ranks(row["pool"], row["tau"])))
            self.assertEqual([m["rank"] for m in row["setters"]], list(script.setter_ranks(row["pool"], row["tau"])))
            self.assertLessEqual(row["ci"][0], row["quantile"] + 1e-6)


if __name__ == "__main__":
    unittest.main()
