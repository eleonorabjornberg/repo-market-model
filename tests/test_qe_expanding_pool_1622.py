"""`repo_model.event_conditional.older_residuals`, `expand_estimate` and `scripts/qe_expanding_pool_1622.py` (#1622; H5 step 3, development tier): the
quarter-end event pool drawn from every past turn up to the anchor, not only from the refit's two-year window.

Written first, against `metadata/qe_expanding_pool_1622.json`. What these tests pin: an older pair is standardised under the refit in force (a pair
the refit trained on gets, to 1e-12, the residual the refit stored; a changed coefficient moves an older pair's residual by the effect times its
regressor, on a hand case); the expanded estimate keeps the candidate's pool, effects and counts and only grows its residuals; the expanding pool
(arm i) counts every public quarter-end and year-end turn, the separate pools (arm ii) count year-ends apart from the other quarter-ends; the leakage
guard (a pair whose target lies after the anchor raises `LookAheadError`); that the declaration's `k`, arms, seed and event set are the script's and the
module's; and that every cell outside the event set stays the candidate's bit for bit.

Recorded mutation (the guard of this study, #1622), run on this module and restored:

* in `repo_model.event_conditional.older_residuals`, the check `if p.target > anchor or p.origin > anchor:` was changed to
  `if p.target > anchor + 400 or p.origin > anchor + 400:`. `LeakageTests.test_an_older_pair_whose_target_is_after_the_anchor_is_refused` then failed
  with `AssertionError` (`LookAheadError` not raised).
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

from repo_model import event_conditional as ec
from repo_model import one_step_guard as osg
from repo_model import spread_mr_state_calendar as sc
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("qe_expanding_pool_1622", ROOT / "scripts" / "qe_expanding_pool_1622.py")
script = importlib.util.module_from_spec(_spec)
sys.modules["qe_expanding_pool_1622"] = script
_spec.loader.exec_module(script)

QE, YE, ORD = "quarter_end_turn", "year_end", "ordinary"


def flags(i, hot=7):
    return {"quarter_end": 1 if i % hot == 0 else 0}


def pair(i, raw=None, scale=2.0, origin=None, target=None, hot=7):
    raw = (-1.0) ** i * (1.0 + (i % 3) * 0.5) + (3.0 if i % hot == 0 else 0.0) if raw is None else raw
    return sc.StatePair(raw, scale, flags(i, hot), None, {}, i if origin is None else origin, i + 1 if target is None else target, {}, False)


def fitted(n=80):
    pairs = [pair(i) for i in range(n)]
    est = sc.fit_state_terms(
        osg.stamp_pairs(pairs, direct=True), regressors=("quarter_end",), terms=("quarter_end",), interact=False, robust=False, training_pairs="direct",
        min_flagged=3)
    return pairs, est


class OlderResidualTests(unittest.TestCase):

    def test_a_pair_the_refit_trained_on_gets_the_residual_it_stored(self):
        pairs, est = fitted()
        self.assertIn("quarter_end", est.effect)
        held = ec.older_residuals(dataclass_without(est), pairs, anchor=1000)[1]
        for a, b in zip(held, est.residuals):
            self.assertAlmostEqual(a, b, places=12)

    def test_the_residual_is_the_scaled_raw_less_the_refits_own_effect(self):
        _pairs, est = fitted()
        older = [sc.StatePair(3.0, 2.0, {"quarter_end": 1}, None, {}, -9, -8, {}, False), sc.StatePair(3.0, 2.0, {"quarter_end": 0}, None, {}, -7, -6, {}, False)]
        targets, z = ec.older_residuals(est, older, anchor=10)
        self.assertEqual(targets, (-8, -6))
        self.assertAlmostEqual(z[0], 1.5 - est.effect["quarter_end"], places=12)
        self.assertAlmostEqual(z[1], 1.5, places=12)

    def test_the_sized_and_slope_terms_are_read_as_the_fit_reads_them(self):
        est = sc.StateEstimate(("settlement_coupon",), {"settlement_coupon": 0.5}, {"settlement_coupon": 0.25}, {}, [0.0], 1, 0, 0, True, (0,), (1,), (0.0,))
        p = sc.StatePair(4.0, 2.0, {"settlement_coupon": 1}, 1.0, {"settlement_coupon": 200.0}, 5, 6, {}, False)
        _t, z = ec.older_residuals(est, [p], anchor=10)
        # 4 / 2 = 2, less 0.5 * (200 / 100 * 1.0) = 1, less 0.25 * 1 * 1.0 = 0.25
        self.assertAlmostEqual(z[0], 0.75, places=12)

    def test_a_pair_the_refit_already_holds_is_refused(self):
        pairs, est = fitted()
        with self.assertRaises(ValueError):
            ec.older_residuals(est, [pairs[3]], anchor=1000)

    def test_a_pair_without_a_scale_is_refused(self):
        _pairs, est = fitted()
        with self.assertRaises(ValueError):
            ec.older_residuals(est, [pair(200, scale=0.0)], anchor=1000)


def dataclass_without(est):
    """The estimate with no pair of its own, so that its own pairs may be passed as 'older' ones to check the arithmetic."""

    import dataclasses
    return dataclasses.replace(est, origins=(), targets=(), residuals=())


class ExpandTests(unittest.TestCase):

    def test_only_the_residuals_grow(self):
        _pairs, est = fitted()
        older = [pair(i, origin=-50 + i, target=-49 + i) for i in range(5)]
        wide = ec.expand_estimate(est, older, anchor=1000)
        self.assertEqual(len(wide.residuals), len(est.residuals) + 5)
        self.assertEqual(wide.residuals[: len(est.residuals)], est.residuals)
        self.assertEqual(wide.targets[len(est.targets):], tuple(p.target for p in older))
        self.assertEqual(wide.pool, est.pool)
        self.assertEqual(wide.effect, est.effect)
        self.assertEqual(wide.pairs, est.pairs)

    def test_the_expanded_estimate_counts_every_public_turn_and_the_separate_pools_split_the_year_ends(self):
        _pairs, est = fitted()
        own_targets = set(est.targets)
        older = [pair(i, origin=-200 + i, target=-199 + i) for i in range(30)]
        wide = ec.expand_estimate(est, older, anchor=1000)
        labels = {t: ORD for t in own_targets}
        for p in older:
            labels[p.target] = QE if p.target % 3 else YE
        pooled = ec.event_pool(wide, labels, 1000, k=20.0, event=(QE, YE))
        qe_only = ec.event_pool(wide, labels, 1000, k=20.0, event=(QE,))
        ye_only = ec.event_pool(wide, labels, 1000, k=20.0, event=(YE,))
        self.assertEqual(pooled["n"], 30)
        self.assertEqual(qe_only["n"] + ye_only["n"], 30)
        self.assertGreater(ye_only["n"], 0)
        # the window alone holds none of them: the candidate's own event pool is empty, so it falls back
        self.assertEqual(ec.event_pool(est, {t: ORD for t in own_targets}, 1000, k=20.0)["n"], 0)
        self.assertEqual(pooled["w"], 30 / 50)

    def test_with_no_older_pair_the_expanded_estimate_is_the_refits(self):
        _pairs, est = fitted()
        wide = ec.expand_estimate(est, [], anchor=1000)
        self.assertEqual(wide, est)


class LeakageTests(unittest.TestCase):

    def test_an_older_pair_whose_target_is_after_the_anchor_is_refused(self):
        _pairs, est = fitted()
        with self.assertRaises(LookAheadError):
            ec.older_residuals(est, [pair(300, origin=-10, target=101)], anchor=100)
        with self.assertRaises(LookAheadError):
            ec.expand_estimate(est, [pair(300, origin=-10, target=101)], anchor=100)

    def test_an_older_pair_at_the_anchor_is_allowed_and_one_whose_origin_is_after_it_is_not(self):
        _pairs, est = fitted()
        ec.older_residuals(est, [pair(300, origin=-10, target=100)], anchor=100)
        with self.assertRaises(LookAheadError):
            ec.older_residuals(est, [pair(300, origin=101, target=100)], anchor=100)


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_what_the_module_and_script_have(self):
        d = script.committed_declaration()
        self.assertEqual(d["issue"], 1622)
        self.assertEqual(d["scoring"]["seed"], script.SEED)
        self.assertEqual(script.SEED, 1548)
        self.assertEqual(d["form"]["k"], script.K)
        self.assertEqual(d["form"]["minimum_rows"], ec.MIN_ROWS)
        self.assertEqual(tuple(d["group"]["types"]), ec.EVENT_TYPES)
        self.assertEqual(d["amendments"], [])
        self.assertEqual([a["name"] for a in d["arms"]], [script.ANNNET, script.ARM_EXPANDING, script.ARM_SEPARATE])
        self.assertEqual(d["limits"]["last_day"], script.LAST_DAY.isoformat())
        self.assertIn("18:00", d["decision_instant"])

    def test_the_kill_is_the_one_of_1548(self):
        mine = script.committed_declaration()["kill"]
        theirs = json.loads((ROOT / "metadata" / "qe_event_model_1548.json").read_text(encoding="utf-8"))["kill"]
        self.assertEqual(mine, theirs)

    def test_the_cleared_register_row_names_the_declaration(self):
        row = json.loads((ROOT / "metadata" / "provisional" / "cleared" / "qe_expanding_pool_1622.json").read_text(encoding="utf-8"))
        self.assertEqual(row["declaration"], "metadata/qe_expanding_pool_1622.json")
        self.assertEqual(row["script"], "scripts/qe_expanding_pool_1622.py")
        self.assertEqual(row["pairing"], "direct")


class ArmEventSetTests(unittest.TestCase):

    def test_the_arms_event_sets(self):
        self.assertEqual(script.event_sets(script.ARM_EXPANDING), {QE: (QE, YE), YE: (QE, YE)})
        self.assertEqual(script.event_sets(script.ARM_SEPARATE), {QE: (QE,), YE: (YE,)})
        with self.assertRaises(ValueError):
            script.event_sets("nope")


if __name__ == "__main__":
    unittest.main()
