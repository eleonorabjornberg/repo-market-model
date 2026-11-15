"""`repo_model.event_conditional` and `scripts/qe_event_model_1548.py` (#1548; H5 step 3, development tier): the candidate (s3c-ann-net) with an
event-conditional residual distribution on quarter-end target days only.

Written first, against `metadata/qe_event_model_1548.json`. What these tests pin: the quantile-by-quantile shrinkage `pool' = (1 - w) pool + w event`,
`w = n / (n + k)`, on hand cases; that the event pool is the empirical distribution of the training residuals whose target is in the event set (and
of no other) and carries the event's location shift; the fallback (fewer than the minimum of pairs: the candidate's pool, exactly); that the result
never crosses; that the declaration's `k`, event set and seed are the script's and the module's; the leakage guard (a training target after the
anchor is refused); and the claim of the directive, that every forecast of a target day outside the event set is the candidate's, bit for bit.

Recorded mutations (the guards of this study, #1548), each run on this module and restored:

* in `repo_model.event_conditional.event_pool`, the check `if target > anchor:` was changed to `if target > anchor + 400:`.
  `LeakageTests.test_a_training_target_after_the_anchor_is_refused` then failed with `AssertionError` (`LookAheadError` not raised).
* in `qe_event_model_1548.outside_group_identical`, the condition `if label in GROUP_TYPES:` was changed to `if True:`.
  `IdenticalOutsideTheEventSetTests.test_a_changed_cell_outside_the_event_set_is_refused` then failed with `AssertionError` (`ValueError` not
  raised: the changed ordinary-day cell went through unseen); the count test failed too.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace

from repo_model import event_conditional as ec
from repo_model import protocol_benchmarks as pb
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("qe_event_model_1548", ROOT / "scripts" / "qe_event_model_1548.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["qe_event_model_1548"] = script
_spec.loader.exec_module(script)

QE, YE, ORD = "quarter_end_turn", "year_end", "ordinary"
ORDINARY_Z = [(j - 50) / 25.0 for j in range(101)]  # symmetric about 0, spread about 2


def estimate(residuals, targets):
    return SimpleNamespace(residuals=tuple(residuals), targets=tuple(targets), pool=pb.empirical_quantiles(sorted(residuals)))


def mixed(event_values, n_ordinary=100):
    """An estimate whose first rows are event targets with `event_values` and whose later rows are ordinary targets."""

    ordinary = [ORDINARY_Z[(i * 7) % len(ORDINARY_Z)] for i in range(n_ordinary)]
    z = list(event_values) + ordinary
    labels = {i: QE for i in range(len(event_values))}
    labels.update({len(event_values) + i: ORD for i in range(n_ordinary)})
    return estimate(z, range(len(z))), labels, len(z) - 1


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_what_the_module_and_script_have(self):
        d = script.committed_declaration()
        self.assertEqual(d["issue"], 1548)
        self.assertEqual(script.SEED, 1548)
        self.assertEqual(d["scoring"]["seed"], script.SEED)
        self.assertEqual(d["form"]["k"], script.K)
        self.assertEqual(tuple(d["group"]["types"]), ec.EVENT_TYPES)
        self.assertEqual(d["form"]["minimum_rows"], ec.MIN_ROWS)
        self.assertEqual(d["amendments"], [])
        self.assertEqual([a["name"] for a in d["arms"]], [script.ANNNET, script.ARM])
        self.assertTrue(d["form"]["k_reason"])
        self.assertTrue(d["form"]["fallback_for_thin_events"])
        self.assertIn("18:00", d["decision_instant"])
        self.assertEqual(d["limits"]["last_day"], script.LAST_DAY.isoformat())

    def test_the_cleared_register_row_names_the_declaration(self):
        row = json.loads((ROOT / "metadata" / "provisional" / "cleared" / "qe_event_model_1548.json").read_text(encoding="utf-8"))
        self.assertEqual(row["declaration"], "metadata/qe_event_model_1548.json")
        self.assertEqual(row["script"], "scripts/qe_event_model_1548.py")
        self.assertEqual(row["pairing"], "direct")


class EventPoolTests(unittest.TestCase):

    def test_the_pool_moves_each_level_part_of_the_way_to_the_events(self):
        event = [3.0 + 0.1 * i for i in range(20)]  # twenty event residuals, all above the ordinary ones
        est, labels, anchor = mixed(event)
        r = ec.event_pool(est, labels, anchor, k=20)
        self.assertEqual(r["n"], 20)
        self.assertEqual(r["w"], 0.5)
        target = pb.empirical_quantiles(sorted(event))
        for p, e, got in zip(est.pool, target, r["pool"]):
            self.assertAlmostEqual(got, 0.5 * p + 0.5 * e)

    def test_the_event_pool_is_the_events_alone_and_carries_their_location(self):
        event = [5.0] * 20
        est, labels, anchor = mixed(event)
        r = ec.event_pool(est, labels, anchor, k=0)
        self.assertEqual(r["w"], 1.0)
        self.assertEqual(r["pool"], [5.0] * 23)
        self.assertEqual(r["event_pool"], [5.0] * 23)

    def test_both_event_types_are_one_set_and_other_types_are_not_in_it(self):
        z = [4.0] * 10 + [8.0] * 10 + [0.0] * 10
        labels = {i: (QE if i < 10 else YE if i < 20 else "turn") for i in range(30)}
        r = ec.event_pool(estimate(z, range(30)), labels, anchor=29, k=20)
        self.assertEqual(r["n"], 20)
        self.assertEqual(r["event_pool"][0], 4.0)
        self.assertEqual(r["event_pool"][-1], 8.0)

    def test_a_thin_event_set_is_the_candidates_pool_exactly(self):
        est, labels, anchor = mixed([9.0] * (ec.MIN_ROWS - 1))
        r = ec.event_pool(est, labels, anchor, k=20)
        self.assertEqual(r["n"], ec.MIN_ROWS - 1)
        self.assertEqual(r["w"], 0.0)
        self.assertEqual(r["pool"], list(est.pool))
        self.assertIsNone(r["event_pool"])

    def test_the_minimum_itself_is_enough(self):
        est, labels, anchor = mixed([9.0] * ec.MIN_ROWS)
        r = ec.event_pool(est, labels, anchor, k=20)
        self.assertGreater(r["w"], 0.0)
        self.assertNotEqual(r["pool"], list(est.pool))

    def test_the_result_never_crosses(self):
        event = [-4.0, 7.0, 0.5, 2.5, 1.0, 9.0, -1.0, 3.0, 3.0, 6.0, 0.0, 12.0]
        est, labels, anchor = mixed(event)
        for k in (0, 5, 20, 80):
            pool = ec.event_pool(est, labels, anchor, k=k)["pool"]
            self.assertEqual(pool, sorted(pool))
            self.assertEqual(len(pool), 23)

    def test_a_negative_constant_is_a_data_error(self):
        est, labels, anchor = mixed([1.0] * 20)
        with self.assertRaises(ValueError):
            ec.event_pool(est, labels, anchor, k=-1)

    def test_a_target_without_a_label_or_with_an_unknown_one_is_a_data_error(self):
        est, labels, anchor = mixed([1.0] * 20)
        with self.assertRaises(ValueError):
            ec.event_pool(est, {k: v for k, v in labels.items() if k != 3}, anchor, k=20)
        with self.assertRaises(ValueError):
            ec.event_pool(est, {**labels, 3: "holiday"}, anchor, k=20)

    def test_residuals_and_targets_must_pair_up(self):
        with self.assertRaises(ValueError):
            ec.event_pool(SimpleNamespace(residuals=(1.0, 2.0), targets=(0,), pool=[0.0] * 23), {0: QE}, 0, k=20)


class LeakageTests(unittest.TestCase):

    def test_a_training_target_after_the_anchor_is_refused(self):
        est, labels, anchor = mixed([2.0] * 20)
        with self.assertRaises(LookAheadError):
            ec.event_pool(est, labels, anchor - 1, k=20)

    def test_a_target_at_the_anchor_is_public(self):
        est, labels, anchor = mixed([2.0] * 20)
        ec.event_pool(est, labels, anchor, k=20)


class ConditionedQuantilesTests(unittest.TestCase):

    def test_the_quantiles_move_by_the_scale_times_the_pool_change(self):
        pool = [float(j) for j in range(23)]
        new = [p + 0.5 for p in pool]
        q = [10.0 + 2.0 * (1.0 + p) for p in pool]  # centre 10, scale 2, shift 1
        out = ec.conditioned_quantiles(q, pool, new, scale=2.0)
        for a, b in zip(q, out):
            self.assertAlmostEqual(b - a, 1.0)

    def test_an_unchanged_pool_is_the_candidates_list_exactly(self):
        pool = [0.1 * j for j in range(23)]
        q = [3.0 + 1.7 * (0.2 + p) for p in pool]
        self.assertEqual(ec.conditioned_quantiles(q, pool, list(pool), scale=1.7), q)

    def test_a_pool_of_the_wrong_length_is_a_data_error(self):
        with self.assertRaises(ValueError):
            ec.conditioned_quantiles([0.0] * 23, [0.0] * 23, [0.0] * 22, scale=1.0)


class IdenticalOutsideTheEventSetTests(unittest.TestCase):

    def setUp(self):
        self.days = [date(2025, 3, 3), date(2025, 3, 4)]
        self.position = {d: i for i, d in enumerate(self.days)}
        # decision day 0 aims at rows 1..5, decision day 1 at rows 2..6
        self.labels = {1: ORD, 2: QE, 3: ORD, 4: ORD, 5: ORD, 6: ORD}
        base = [float(j) for j in range(23)]
        self.candidate = {d: {h: list(base) for h in script.LEADS} for d in self.days}
        self.arm = {d: {h: list(base) for h in script.LEADS} for d in self.days}

    def test_a_group_cell_may_change_and_is_counted(self):
        self.arm[self.days[0]][2][0] = -9.0  # row 2, the quarter-end turn
        counts = script.outside_group_identical(self.candidate, self.arm, self.labels, self.position, self.days)
        self.assertEqual(counts["group_cells"], 2)
        self.assertEqual(counts["group_cells_changed"], 1)
        self.assertEqual(counts["other_cells"], 8)

    def test_a_changed_cell_outside_the_event_set_is_refused(self):
        self.arm[self.days[0]][1][0] = -1.0
        with self.assertRaises(ValueError):
            script.outside_group_identical(self.candidate, self.arm, self.labels, self.position, self.days)


if __name__ == "__main__":
    unittest.main()
