"""`repo_model.day_type_scale.group_multiplier` and `scripts/qe_shrunk_scale_1531.py` (#1531; H5 step 3, development tier): the candidate (s3c-ann-net)
with a shrunk residual multiplier on quarter-end target days only.

Written first, against `metadata/qe_shrunk_scale_1531.json`. What these tests pin: the shrinkage weight `w = n / (n + k)` and `m = 1 + w (m_raw - 1)` on
hand cases; that `m_raw` is #1402's root-mean-square ratio of the group's training residuals to all of them about the pool's median, 1 below the
minimum of rows, clamped to the bounds; that the declaration's `k`, group and seed are the script's and the module's; the leakage guard (a training
target after the anchor is refused); and the claim of the directive, that every forecast of a target day outside the group is the candidate's, bit for
bit (the check the walk runs, `outside_group_identical`, and a rescale of a day with a mixed group); and the event-cluster bootstrap.

Recorded mutations (the guards of this study, #1531), each run on this module and restored:

* in `repo_model.day_type_scale.group_multiplier`, the check `if target > anchor:` was changed to `if target > anchor + 400:`.
  `LeakageTests.test_a_training_target_after_the_anchor_is_refused` then failed with `AssertionError` (`LookAheadError` not raised).
* in `qe_shrunk_scale_1531.outside_group_identical`, the condition `if label in GROUP_TYPES:` was changed to `if True:`.
  `IdenticalOutsideTheGroupTests.test_a_changed_cell_outside_the_group_is_refused` then failed with `AssertionError` (`ValueError` not raised: the
  changed ordinary-day cell went through unseen); the count test failed too.
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace

from repo_model import day_type_scale as dts
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("qe_shrunk_scale_1531", ROOT / "scripts" / "qe_shrunk_scale_1531.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["qe_shrunk_scale_1531"] = script
_spec.loader.exec_module(script)

POOL = [(j - 11) / 10.0 for j in range(23)]  # symmetric, median 0.0
QE, ORD = "quarter_end_turn", "ordinary"


def estimate(residuals, targets, pool=POOL):
    return SimpleNamespace(residuals=tuple(residuals), targets=tuple(targets), pool=list(pool))


def labels_of(n_group, n_other, group_label=QE):
    out = {i: group_label for i in range(n_group)}
    out.update({n_group + i: ORD for i in range(n_other)})
    return out


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_what_the_module_and_script_have(self):
        d = script.committed_declaration()
        self.assertEqual(d["issue"], 1531)
        self.assertEqual(script.SEED, 1531)
        self.assertEqual(d["scoring"]["seed"], script.SEED)
        self.assertEqual(d["form"]["k"], script.K)
        self.assertEqual(tuple(d["group"]["types"]), dts.GROUP_TYPES)
        self.assertEqual(tuple(d["form"]["bounds"]), dts.BOUNDS)
        self.assertEqual(d["form"]["minimum_rows"], dts.MIN_ROWS)
        self.assertEqual(d["amendments"], [])
        self.assertEqual([a["name"] for a in d["arms"]], [script.ANNNET, script.ARM])
        self.assertTrue(d["form"]["k_reason"])
        self.assertIn("18:00", d["decision_instant"])
        self.assertEqual(d["limits"]["last_day"], script.LAST_DAY.isoformat())

    def test_the_cleared_register_row_names_the_declaration(self):
        row = json.loads((ROOT / "metadata" / "provisional" / "cleared" / "qe_shrunk_scale_1531.json").read_text(encoding="utf-8"))
        self.assertEqual(row["declaration"], "metadata/qe_shrunk_scale_1531.json")
        self.assertEqual(row["script"], "scripts/qe_shrunk_scale_1531.py")
        self.assertEqual(row["pairing"], "direct")


class ShrinkageTests(unittest.TestCase):

    def test_the_weight_is_n_over_n_plus_k(self):
        self.assertEqual(dts.shrink_weight(20, 20), 0.5)
        self.assertEqual(dts.shrink_weight(60, 20), 0.75)
        self.assertEqual(dts.shrink_weight(0, 20), 0.0)
        self.assertEqual(dts.shrink_weight(5, 0), 1.0)

    def test_a_negative_count_or_constant_is_a_data_error(self):
        with self.assertRaises(ValueError):
            dts.shrink_weight(-1, 20)
        with self.assertRaises(ValueError):
            dts.shrink_weight(10, -1)

    def test_the_multiplier_moves_part_of_the_way_from_one(self):
        self.assertAlmostEqual(dts.shrunk(2.0, 20, 20), 1.5)
        self.assertAlmostEqual(dts.shrunk(0.5, 60, 20), 0.625)
        self.assertEqual(dts.shrunk(3.0, 0, 20), 1.0)
        self.assertEqual(dts.shrunk(1.0, 50, 20), 1.0)


class GroupMultiplierTests(unittest.TestCase):

    def test_m_raw_is_the_group_rms_ratio_and_m_is_shrunk(self):
        # 20 group rows at +-2, 20 other rows at +-1: mean square all = (20*4 + 20*1)/40 = 2.5; group 4
        z = [2.0, -2.0] * 10 + [1.0, -1.0] * 10
        r = dts.group_multiplier(estimate(z, range(40)), labels_of(20, 20), anchor=39, k=20)
        self.assertAlmostEqual(r["m_raw"], math.sqrt(4.0 / 2.5))
        self.assertEqual(r["n"], 20)
        self.assertEqual(r["w"], 0.5)
        self.assertAlmostEqual(r["m"], 1.0 + 0.5 * (math.sqrt(4.0 / 2.5) - 1.0))

    def test_both_group_types_are_one_set_and_other_types_are_not_in_it(self):
        z = [2.0, -2.0] * 10 + [1.0, -1.0] * 10
        labels = {i: (QE if i % 2 else "year_end") for i in range(20)}
        labels.update({20 + i: "turn" for i in range(20)})  # a non-group calendar type
        r = dts.group_multiplier(estimate(z, range(40)), labels, anchor=39, k=20)
        self.assertEqual(r["n"], 20)

    def test_the_ratio_is_about_the_pools_median(self):
        pool = [v + 5.0 for v in POOL]
        z = [7.0, 3.0] * 10 + [6.0, 4.0] * 10
        r = dts.group_multiplier(estimate(z, range(40), pool), labels_of(20, 20), anchor=39, k=0)
        self.assertAlmostEqual(r["m"], math.sqrt(4.0 / 2.5))

    def test_fewer_than_the_minimum_rows_reads_one_but_counts_them(self):
        z = [3.0, -3.0] * 4 + [1.0, -1.0] * 16
        r = dts.group_multiplier(estimate(z, range(40)), labels_of(8, 32), anchor=39, k=20)
        self.assertEqual((r["m_raw"], r["m"]), (1.0, 1.0))
        self.assertEqual(r["n"], 8)

    def test_m_raw_is_clamped_to_the_bounds_before_shrinking(self):
        z = [30.0, -30.0] * 5 + [0.001, -0.001] * 95
        r = dts.group_multiplier(estimate(z, range(200)), labels_of(10, 190), anchor=199, k=10)
        self.assertEqual(r["m_raw"], dts.BOUNDS[1])
        self.assertAlmostEqual(r["m"], 1.0 + 0.5 * (dts.BOUNDS[1] - 1.0))
        low = [0.01, -0.01] * 5 + [3.0, -3.0] * 20
        r = dts.group_multiplier(estimate(low, range(50)), labels_of(10, 40), anchor=49, k=10)
        self.assertEqual(r["m_raw"], dts.BOUNDS[0])

    def test_a_refit_with_no_spread_reads_one(self):
        r = dts.group_multiplier(estimate([0.0] * 40, range(40)), labels_of(20, 20), anchor=39, k=20)
        self.assertEqual(r["m"], 1.0)

    def test_a_label_outside_the_five_is_a_data_error(self):
        labels = labels_of(20, 20)
        labels[3] = "bank_holiday"
        with self.assertRaises(ValueError):
            dts.group_multiplier(estimate([1.0] * 40, range(40)), labels, anchor=39, k=20)

    def test_a_target_without_a_label_is_a_data_error(self):
        with self.assertRaises(ValueError):
            dts.group_multiplier(estimate([1.0] * 40, range(40)), labels_of(20, 10), anchor=39, k=20)


class LeakageTests(unittest.TestCase):

    def test_a_training_target_after_the_anchor_is_refused(self):
        z = [2.0, -2.0] * 10 + [1.0, -1.0] * 10
        with self.assertRaises(LookAheadError):
            dts.group_multiplier(estimate(z, range(40)), labels_of(20, 20), anchor=38, k=20)

    def test_the_last_public_target_is_accepted(self):
        z = [2.0, -2.0] * 10 + [1.0, -1.0] * 10
        dts.group_multiplier(estimate(z, range(40)), labels_of(20, 20), anchor=39, k=20)


class IdenticalOutsideTheGroupTests(unittest.TestCase):
    """The claim of the directive: on a target day outside the group, every quantile equals the candidate's."""

    def setUp(self):
        self.pool = POOL
        self.q = [0.5 + 2.0 * (v + 0.3) for v in POOL]  # centre + scale * (shift + pool_j), scale 2, shift 0.3, centre 0.5
        self.est = SimpleNamespace(pool=self.pool)

    def test_a_rescale_changes_the_group_day_and_leaves_the_others_as_they_are(self):
        forecast = {1: list(self.q), 2: list(self.q)}
        out = dts.rescale_day(forecast, {1: self.est, 2: self.est}, {1: {QE: 1.5, ORD: 1.0}, 2: {QE: 1.5, ORD: 1.0}}, {1: ORD, 2: QE}, 2.0)
        self.assertEqual(out[1], self.q)
        self.assertNotEqual(out[2], self.q)
        self.assertEqual(out[2][11], self.q[11])  # the median does not move

    def test_the_group_multipliers_are_one_outside_the_group(self):
        by_type = script.multipliers_by_type(1.7)
        self.assertEqual(by_type[QE], 1.7)
        self.assertEqual(by_type["year_end"], 1.7)
        for t in dts.TYPES:
            if t not in dts.GROUP_TYPES:
                self.assertEqual(by_type[t], 1.0)

    def test_an_identical_walk_passes_and_counts_the_group_cells(self):
        days = [date(2020, 1, 6), date(2020, 1, 7)]
        labels = {i: ORD for i in range(20)}
        labels[3] = QE
        position = {d: i for i, d in enumerate(days)}
        candidate = {d: {h: list(self.q) for h in range(1, 6)} for d in days}
        arm = {d: {h: list(self.q) for h in range(1, 6)} for d in days}
        arm[days[0]][3] = [v + 1.0 for v in self.q]  # target row 0 + 3 = 3, in the group
        counts = script.outside_group_identical(candidate, arm, labels, position, days)
        self.assertEqual(counts, {"group_cells": 2, "group_cells_changed": 1, "other_cells": 8})

    def test_a_changed_cell_outside_the_group_is_refused(self):
        days = [date(2020, 1, 6)]
        labels = {i: ORD for i in range(20)}
        labels[3] = QE
        position = {days[0]: 0}
        candidate = {days[0]: {h: list(self.q) for h in range(1, 6)}}
        arm = {days[0]: {h: list(self.q) for h in range(1, 6)}}
        arm[days[0]][2] = [v + 1e-12 for v in self.q]  # target row 2 is ordinary
        with self.assertRaises(ValueError):
            script.outside_group_identical(candidate, arm, labels, position, days)


class EventClusterTests(unittest.TestCase):

    def test_an_event_is_the_quarter_end_the_target_belongs_to(self):
        self.assertEqual(script.event_of(date(2019, 3, 29)), "2019-03")
        self.assertEqual(script.event_of(date(2019, 4, 1)), "2019-03")

    def test_a_day_outside_a_turn_has_no_event(self):
        self.assertIsNone(script.event_of(date(2019, 3, 13)))

    def test_events_are_resampled_whole(self):
        # three events with 2 cells each, all hits in one: every resample is a mean of whole events (0, 1/3, 2/3 or 1 hits per cell on average)
        sums = [[2.0], [0.0], [0.0]]
        counts = [2, 2, 2]
        low, high = script.cluster_interval(sums, counts, reps=500, seed=1531)[0]
        self.assertGreaterEqual(low, 0.0)
        self.assertLessEqual(high, 1.0)
        self.assertLess(low, high)

    def test_the_interval_of_identical_events_is_a_point(self):
        sums, counts = [[1.0, 4.0]] * 5, [2] * 5
        out = script.cluster_interval(sums, counts, reps=200, seed=1531)
        self.assertEqual(out, [(0.5, 0.5), (2.0, 2.0)])

    def test_the_same_seed_gives_the_same_interval(self):
        sums, counts = [[1.0], [3.0], [0.0], [2.0]], [2, 2, 2, 2]
        self.assertEqual(script.cluster_interval(sums, counts, reps=300, seed=7), script.cluster_interval(sums, counts, reps=300, seed=7))


class RatesTests(unittest.TestCase):

    def test_the_cell_vector_of_a_hand_case(self):
        from repo_model import scoring_protocol as sp
        q = [float(j) for j in range(23)]
        i = {lv: sp.GRID.index(lv) for lv in (0.01, 0.05, 0.95, 0.99)}
        v = script.rate_vector(q, 11.0)
        self.assertEqual(v[:5], [1.0, 0.0, 0.0, 0.0, 0.0])
        v = script.rate_vector(q, q[i[0.95]] + 0.5)  # above q95, inside q99
        self.assertEqual((v[0], v[1], v[2]), (0.0, 0.0, 1.0))
        v = script.rate_vector(q, q[i[0.05]] - 0.5)
        self.assertEqual((v[0], v[1], v[2]), (0.0, 1.0, 0.0))
        v = script.rate_vector(q, q[i[0.99]] + 0.5)
        self.assertEqual((v[2], v[4]), (1.0, 1.0))
        v = script.rate_vector(q, q[i[0.01]] - 0.5)
        self.assertEqual((v[1], v[3]), (1.0, 1.0))

    def test_a_hit_on_the_quantile_itself_is_inside(self):
        from repo_model import scoring_protocol as sp
        q = [float(j) for j in range(23)]
        v = script.rate_vector(q, q[sp.GRID.index(0.95)])
        self.assertEqual(v[:3], [1.0, 0.0, 0.0])


if __name__ == "__main__":
    unittest.main()
