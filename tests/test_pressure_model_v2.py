"""Pressure model v2's distribution (#244): v1 unchanged, its interior tracked online.

#247's diagnosis (`docs/diagnosis-interior-calibration.md`, merged in #250)
found v1's interior too narrow, and its declared selection rule chose (i):
per-level online quantile tracking of q25, q50 and q75 on v1's unchanged trees
and nested PID. #244 built that as `repo_model.interior`. Eleonora's ruling on
PR #252 then had the choice redone on the inner block (2018-06-29 to
2022-12-31) with conditional gates, and it chose (iv): the same tracking on
trees of maximum depth 3. That is pressure model v2. These tests hold it to that:

* `ReferenceTests`: driven one day at a time, `OnlineInterior` issues the
  vectors and makes the step choices of #247's reference implementation
  (`scripts/interior_diagnosis.py`'s `interior_tracking`) to the bit.
* `ObservabilityTests`: a label updates a tracker only once it was public at
  the decision instant of the vector being issued (`LookAheadError`).
* `OrderTests`: the issued quantiles stay ordered (`ValueError`).
* `FoldLoopTests`: inside a fold loop, `NestedInteriorFoldPid`'s inner PID
  vector is `NestedFoldPid`'s to the bit (v1 is untouched), and the vector it
  issues is `OnlineInterior`'s over those PID vectors.
* `WidthReferenceTests`, `WidthObservabilityTests`: the width layer (the fix chosen on
  the inner block) issues `width_tracking`'s vectors to the bit, and a label reaches
  it only once it was public at the decision instant (`LookAheadError`).
* `FixDeclarationTests`: the diagnosis and the fix, as declared before the choice.
* `OuterValidationDeclarationTests`: the inner and outer blocks, the
  conditional gates and the eligibility readings, as declared before scoring.
* `RecordTests`: `docs/runs/pressure_model_v2_distribution_h1.json` against
  #247's record (v1 byte-identical on the published panel, v2 the reference
  of the chosen candidate), the published CRPS records, the declared bar and
  gate, the inner choice and the outer block.

Mutation record (`WidthObservabilityTests`, the width layer's label guard, which
`WidthState` inherits from `InteriorState`). Disposable copy, CPython 3.11,
`PYTHONDONTWRITEBYTECODE=1`, the class run alone, control green. In
`InteriorState.observe`, `if day.scored_date > decision.anchor:` was changed to
`if False:`, and `diff` confirmed it was applied.
`test_a_label_after_the_decision_anchor_is_refused` (of `WidthObservabilityTests`) then
failed with `AssertionError: LookAheadError not raised`. Restored, green.

Mutation record (`WidthObservabilityTests`, the width layer's issue guard). Same
copy and setup. In `OnlineInterior.issue`, `if day.anchor >= day.scored_date:` was
changed to `if day.anchor > day.scored_date:`, and `diff` confirmed it.
`test_a_width_day_anchored_on_its_own_scored_day_is_refused` then failed with
`AssertionError: LookAheadError not raised`. Restored, green.

Red first (the earlier tests): `repo_model.interior` and
`scripts/pressure_model_v2.py` existed (`ModuleNotFoundError`).

Mutation record (`ObservabilityTests`, the tracker's label guard). In a
disposable copy of the tree, CPython 3.11, `PYTHONDONTWRITEBYTECODE=1`, this
class run alone, with the unmutated control green. In `InteriorState.observe`,
`if day.scored_date > decision.anchor:` was changed to `if False:`, and `diff`
against the tree confirmed it was applied.
`test_a_label_after_the_decision_anchor_is_refused` then failed with
`AssertionError: LookAheadError not raised`. Restored, green.

Mutation record (`ObservabilityTests`, the issue guard). In
`OnlineInterior.issue`, `if day.anchor >= day.scored_date:` was changed to
`if day.anchor > day.scored_date:`, and `diff` confirmed it was applied.
`test_a_day_anchored_on_its_own_scored_day_is_refused` then failed with
`AssertionError: LookAheadError not raised`. Restored, green.

Mutation record (`OrderTests`, the ordering guard). In `require_ordered`,
`if not all(a <= b for a, b in zip(values, values[1:])):` was changed to
`if False:`, and `diff` confirmed it was applied. `test_crossed_quantiles_are_refused`
then failed with `AssertionError: ValueError not raised`. Restored, green.
"""

from __future__ import annotations

import functools
import importlib.util
import json
import math
import random
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import interior, ml, recalibration
from repo_model.contract import CALENDAR_FEATURES
from repo_model.metrics import crps_from_quantiles
from repo_model.splits import LookAheadError

from test_recalibration import FoldPidTests, _UncalibratedModel

REPO = Path(__file__).resolve().parents[1]
RECORD = REPO / "docs" / "runs" / "pressure_model_v2_distribution_h1.json"
DIAGNOSIS = REPO / "docs" / "runs" / "v1_interior_diagnosis.json"
CRPS_RECORD = REPO / "docs" / "runs" / "compare_persistence_vs_gbm_conformal_pid_nested_funding_crps.json"
FINAL = REPO / "docs" / "runs" / "final_test_near_blind.json"
LEVELS = (0.05, 0.25, 0.5, 0.75, 0.95)


def _script(name):
    spec = importlib.util.spec_from_file_location(f"v2_test_{name}", REPO / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dx = _script("interior_diagnosis")
v2 = _script("pressure_model_v2")


def _days(n, *, anchor_lag=1, seed=7):
    """Synthetic scored days in #247's walk format, with outcomes that move the trackers."""

    first = date(2020, 1, 1)
    rng = random.Random(seed)
    days = []
    for k in range(n):
        when = first + timedelta(days=k)
        centre = rng.choice((-1.0, 0.0, 0.0, 1.0))
        days.append({
            "date": when.isoformat(),
            "anchor": (first + timedelta(days=k - anchor_lag)).isoformat(),
            "y": float(rng.randint(-4, 4)) + (17.000000000000014 - 17.0 if k % 3 else 0.0),
            "issued": [centre - 4.0, centre - 1.0, centre, centre + 1.0, centre + 4.0],
        })
    return days


def _drive(days, *, refit_every):
    """`OnlineInterior` one day at a time: issue a day's vector, then record its label."""

    online = interior.OnlineInterior(LEVELS, refit_every=refit_every)
    out = []
    for d in days:
        day = interior.InteriorDay(date.fromisoformat(d["date"]), date.fromisoformat(d["anchor"]),
                                   tuple(d["issued"]))
        out.append(list(online.issue(day)))
        online.record(day, d["y"])
    return out, online


class ReferenceTests(unittest.TestCase):
    """v2 is #247's recommendation, exactly: the reference implementation's vectors and choices."""

    def test_the_vectors_and_choices_are_the_reference_s_to_the_bit(self):
        for lag, refit in ((1, 21), (3, 5), (2, 21)):
            with self.subTest(anchor_lag=lag, refit_every=refit):
                days = _days(300, anchor_lag=lag, seed=lag)
                expected, choices = dx.interior_tracking(days, refit_every=refit)
                issued, online = _drive(days, refit_every=refit)
                self.assertEqual(issued, expected)
                self.assertEqual(
                    [{"first": b.first_scored.isoformat(), "step": interior.INTERIOR_STEPS[b.chosen],
                      "observable": b.past_days} for b in online.blocks],
                    choices)
                # The choice moved off the fallback, so the test tells selection from a fixed step.
                self.assertTrue(any(c["step"] != interior.INTERIOR_FALLBACK for c in choices))

    def test_the_declared_constants_are_the_reference_s(self):
        self.assertEqual(interior.INTERIOR_STEPS, dx.TRACKING_STEPS)
        self.assertEqual(interior.INTERIOR_FALLBACK, dx.TRACKING_FALLBACK)
        self.assertEqual(interior.TIE_BPS, dx.TIE_BPS)
        self.assertEqual(interior.INTERIOR_LEVELS, tuple(LEVELS[i] for i in dx.INTERIOR))

    def test_ties_count_one_half(self):
        self.assertEqual(interior.below_half_tie(17.000000000000014, 17.0), 0.5)
        self.assertEqual(interior.below_half_tie(16.0, 17.0), 1.0)
        self.assertEqual(interior.below_half_tie(18.0, 17.0), 0.0)


KINDS = ("ordinary", "ordinary", "ordinary", "quarter_end", "tax_date", "month_end")


def _kinded_days(n, *, anchor_lag=1, seed=7):
    """`_days`, each with a pressure-day type, and the vectors the level layer would hand the width layer."""

    days = _days(n, anchor_lag=anchor_lag, seed=seed)
    rng = random.Random(seed + 100)
    for d in days:
        d["kind"] = rng.choice(KINDS)
        d["pid"] = d["issued"]
    return days


def _drive_width(days, partition, *, refit_every):
    """`OnlineWidth` one day at a time over `days`' `issued` vectors, classes by `partition`."""

    online = interior.OnlineWidth(LEVELS, refit_every=refit_every)
    out = []
    for d in days:
        kind = v2._partition_class(partition, d["kind"])
        day = interior.InteriorDay(date.fromisoformat(d["date"]), date.fromisoformat(d["anchor"]),
                                   tuple(d["issued"]), kind)
        out.append(list(online.issue(day)))
        online.record(day, d["y"])
    return out, online


class WidthReferenceTests(unittest.TestCase):
    """The width layer is `pressure_model_v2.width_tracking`'s, to the bit; the level layer is unchanged."""

    def test_the_vectors_and_choices_are_the_reference_s_to_the_bit(self):
        for lag, refit, partition in ((1, 21, "turn_vs_ordinary"), (3, 5, "by_type"), (2, 21, "pooled")):
            with self.subTest(anchor_lag=lag, refit_every=refit, partition=partition):
                days = _kinded_days(300, anchor_lag=lag, seed=lag)
                expected, choices = v2.width_tracking(days, partition, refit_every=refit)
                issued, online = _drive_width(days, partition, refit_every=refit)
                self.assertEqual(issued, expected)
                self.assertEqual(
                    [{"first": b.first_scored.isoformat(), "rate": interior.WIDTH_RATES[b.chosen],
                      "observable": b.past_days} for b in online.blocks],
                    choices)
                self.assertTrue(any(c["rate"] != interior.WIDTH_FALLBACK for c in choices))

    def test_the_level_reference_is_the_pooled_one_of_247(self):
        for lag, refit in ((1, 21), (3, 5)):
            days = _kinded_days(300, anchor_lag=lag, seed=lag)
            pooled, choices = v2.class_level_tracking(days, "pooled", refit_every=refit)
            expected, expected_choices = dx.interior_tracking(days, refit_every=refit)
            self.assertEqual(pooled, expected)
            self.assertEqual(choices, expected_choices)

    def test_the_declared_constants_are_the_script_s(self):
        self.assertEqual(interior.WIDTH_RATES, v2.WIDTH_RATES)
        self.assertEqual(interior.WIDTH_FALLBACK, v2.WIDTH_FALLBACK)
        self.assertEqual(v2.FIX_CANDIDATES[v2.CHOSEN_FIX]["partition"], "turn_vs_ordinary")
        for kind in ("quarter_end", "month_end", "tax_date", "ordinary"):
            self.assertEqual(interior.WIDTH_CLASSES[kind], v2._partition_class("turn_vs_ordinary", kind))

    def test_a_band_that_misses_widens_and_one_that_covers_narrows(self):
        state = interior.WidthState(LEVELS, 0.1)
        vector = (-4.0, -1.0, 0.0, 1.0, 4.0)
        first = interior.InteriorDay(date(2024, 1, 3), date(2024, 1, 2), vector, "turn")
        decision = interior.InteriorDay(date(2024, 1, 9), date(2024, 1, 8), vector, "turn")
        state.observe(first, vector, 9.0, decision)
        wide = state.issue(vector, "turn")
        self.assertGreater(wide[3] - wide[1], vector[3] - vector[1])
        self.assertEqual(state.issue(vector, "ordinary"), vector)
        second = interior.InteriorDay(date(2024, 1, 4), date(2024, 1, 2), vector, "ordinary")
        state.observe(second, vector, 0.0, decision)
        narrow = state.issue(vector, "ordinary")
        self.assertLess(narrow[3] - narrow[1], vector[3] - vector[1])

    def test_an_outcome_on_a_band_edge_counts_one_half(self):
        state = interior.WidthState(LEVELS, 0.1)
        vector = (-4.0, -1.0, 0.0, 1.0, 4.0)
        day = interior.InteriorDay(date(2024, 1, 3), date(2024, 1, 2), vector, "turn")
        decision = interior.InteriorDay(date(2024, 1, 9), date(2024, 1, 8), vector, "turn")
        state.observe(day, vector, 1.0 + 1e-12, decision)
        self.assertEqual(state.log_scale["turn"], 0.0)


class WidthObservabilityTests(unittest.TestCase):
    """A label reaches a width tracker only once it was public at the decision instant."""

    def test_a_label_after_the_decision_anchor_is_refused(self):
        state = interior.WidthState(LEVELS, 0.05)
        vector = (-2.0, -1.0, 0.0, 1.0, 2.0)
        early = interior.InteriorDay(date(2024, 1, 3), date(2024, 1, 2), vector, "turn")
        decision = interior.InteriorDay(date(2024, 1, 4), date(2024, 1, 2), vector, "turn")
        with self.assertRaises(LookAheadError):
            state.observe(early, state.issue(vector, "turn"), 0.0, decision)

    def test_a_width_day_anchored_on_its_own_scored_day_is_refused(self):
        online = interior.OnlineWidth(LEVELS, refit_every=21)
        with self.assertRaises(LookAheadError):
            online.issue(interior.InteriorDay(date(2024, 1, 3), date(2024, 1, 3),
                                              (-2.0, -1.0, 0.0, 1.0, 2.0), "turn"))

    def test_a_label_after_the_anchor_never_moves_a_width_vector(self):
        days = _kinded_days(160, anchor_lag=15)
        j = 140
        base, _ = _drive_width(days, "turn_vs_ordinary", refit_every=21)
        changed = [dict(d, y=1e3) if d["date"] > days[j]["anchor"] else d for d in days]
        moved, _ = _drive_width(changed, "turn_vs_ordinary", refit_every=21)
        self.assertEqual(base[: j + 1], moved[: j + 1])

    def test_every_width_vector_is_ordered(self):
        days = _kinded_days(200)
        for d in days:
            d["y"] += 6.0
        issued, _ = _drive_width(days, "turn_vs_ordinary", refit_every=21)
        for vector in issued:
            self.assertEqual(vector, sorted(vector))


class ObservabilityTests(unittest.TestCase):
    """A label reaches a tracker only once it was public at the decision instant."""

    def test_a_label_after_the_decision_anchor_is_refused(self):
        state = interior.InteriorState(LEVELS, 0.05)
        early = interior.InteriorDay(date(2024, 1, 3), date(2024, 1, 2), (-2.0, -1.0, 0.0, 1.0, 2.0))
        decision = interior.InteriorDay(date(2024, 1, 4), date(2024, 1, 2), (-2.0, -1.0, 0.0, 1.0, 2.0))
        issued = state.issue(early.vector)
        with self.assertRaises(LookAheadError):
            state.observe(early, issued, 0.0, decision)

    def test_labels_are_observed_once_in_date_order(self):
        state = interior.InteriorState(LEVELS, 0.05)
        vector = (-2.0, -1.0, 0.0, 1.0, 2.0)
        first = interior.InteriorDay(date(2024, 1, 3), date(2024, 1, 2), vector)
        decision = interior.InteriorDay(date(2024, 1, 9), date(2024, 1, 8), vector)
        state.observe(first, vector, 0.0, decision)
        with self.assertRaises(ValueError):
            state.observe(first, vector, 0.0, decision)

    def test_a_day_anchored_on_its_own_scored_day_is_refused(self):
        online = interior.OnlineInterior(LEVELS, refit_every=21)
        with self.assertRaises(LookAheadError):
            online.issue(interior.InteriorDay(date(2024, 1, 3), date(2024, 1, 3), (-2.0, -1.0, 0.0, 1.0, 2.0)))

    def test_a_label_after_the_anchor_never_moves_a_vector(self):
        days = _days(160, anchor_lag=15)
        j = 140
        base, _ = _drive(days, refit_every=21)
        changed = [dict(d, y=1e3) if d["date"] > days[j]["anchor"] else d for d in days]
        moved, _ = _drive(changed, refit_every=21)
        self.assertEqual(base[: j + 1], moved[: j + 1])


class OrderTests(unittest.TestCase):
    def test_crossed_quantiles_are_refused(self):
        with self.assertRaises(ValueError):
            interior.require_ordered((-2.0, 0.5, 0.0, 1.0, 2.0))

    def test_a_missing_quantile_is_refused(self):
        with self.assertRaises(ValueError):
            interior.require_ordered((-2.0, float("nan"), 0.0, 1.0, 2.0))

    def test_every_issued_vector_is_ordered(self):
        days = _days(200, anchor_lag=1)
        for d in days:
            d["y"] += 6.0  # a run of misses above drives q25 past q75 before the sort
        issued, _ = _drive(days, refit_every=21)
        for vector in issued:
            self.assertEqual(vector, sorted(vector))


class FoldLoopTests(unittest.TestCase):
    """Inside a fold loop: v1's PID untouched, v2's interior tracked on its output."""

    LAG = FoldPidTests.LAG
    REFIT_EVERY = 20
    setUp = FoldPidTests.setUp
    drive = FoldPidTests.drive

    def test_v1_is_untouched_and_v2_tracks_its_output(self):
        model = _UncalibratedModel()
        v1 = self.drive(recalibration.NestedFoldPid(
            self.rows, self.rule, splits=self.splits, refit_every=self.REFIT_EVERY), model)
        pid = interior.NestedInteriorFoldPid(
            self.rows, self.rule, splits=self.splits, refit_every=self.REFIT_EVERY)
        issued = self.drive(pid, model)
        self.assertEqual([tuple(d.pid) for d in pid.issued_days], [vector for vector, _ in v1])
        days = [{"date": d.scored_date.isoformat(), "anchor": d.anchor.isoformat(),
                 "y": self.rows[d.index].spread_bps, "issued": list(d.pid)} for d in pid.issued_days]
        expected, _ = dx.interior_tracking(days, refit_every=self.REFIT_EVERY)
        self.assertEqual([list(vector) for vector, _ in issued], expected)
        self.assertEqual([list(d.vector) for d in pid.issued_days], expected)
        # The point forecast stays the fit's own, as under v1.
        self.assertEqual([point for _, point in issued], [point for _, point in v1])

    def test_the_width_layer_is_the_reference_over_the_interior_layer(self):
        model = _UncalibratedModel()
        pid = interior.NestedInteriorFoldPid(
            self.rows, self.rule, splits=self.splits, refit_every=self.REFIT_EVERY, width_layer=True)
        issued = self.drive(pid, model)
        kinds = [self.splits.day_type(self.rows[d.index].values) for d in pid.issued_days]
        self.assertTrue({"ordinary", "quarter_end", "tax_date"} <= set(kinds))
        days = [{"date": d.scored_date.isoformat(), "anchor": d.anchor.isoformat(),
                 "y": self.rows[d.index].spread_bps, "issued": list(d.pid), "kind": kind}
                for d, kind in zip(pid.issued_days, kinds)]
        tracked, _ = v2.class_level_tracking(days, "pooled", refit_every=self.REFIT_EVERY)
        self.assertEqual([list(d.tracked) for d in pid.issued_days], tracked)
        expected, _ = v2.width_tracking([dict(d, issued=v) for d, v in zip(days, tracked)],
                                        "turn_vs_ordinary", refit_every=self.REFIT_EVERY)
        self.assertEqual([list(vector) for vector, _ in issued], expected)
        self.assertEqual([list(d.vector) for d in pid.issued_days], expected)
        self.assertNotEqual(expected, tracked)
        settings = pid.settings["width_calibration"]
        self.assertEqual(settings["rates"], list(interior.WIDTH_RATES))
        self.assertEqual(settings["classes"], interior.WIDTH_CLASSES)
        self.assertTrue(pid.account()["width_blocks"])

    def test_without_the_width_layer_nothing_is_added(self):
        pid = interior.NestedInteriorFoldPid(
            self.rows, self.rule, splits=self.splits, refit_every=self.REFIT_EVERY)
        self.assertNotIn("width_calibration", pid.settings)
        self.assertNotIn("width_blocks", pid.account())

    def test_the_settings_declare_v2(self):
        pid = interior.NestedInteriorFoldPid(
            self.rows, self.rule, splits=self.splits, refit_every=self.REFIT_EVERY)
        settings = pid.settings
        self.assertEqual(settings["calibration"], "conformal_pid_nested_interior")
        self.assertEqual(settings["interior_calibration"]["steps"], list(interior.INTERIOR_STEPS))
        self.assertEqual(settings["interior_calibration"]["levels"], list(interior.INTERIOR_LEVELS))

    def test_a_law_is_refused(self):
        pid = interior.NestedInteriorFoldPid(
            self.rows, self.rule, splits=self.splits, refit_every=self.REFIT_EVERY)
        with self.assertRaises(ValueError):
            pid.law(10, self.rows[8].date, (-1.0, -0.5, 0.0, 0.5, 1.0), -3.0, 4.0)


class DeclarationTests(unittest.TestCase):
    """The bar (#244) and the 2026 gate (scoping ruling on #244), as declared before scoring."""

    def test_the_bar(self):
        self.assertEqual(v2.BAR["band_50_half_edge"], [45.0, 55.0])
        self.assertEqual(v2.BAR["band_90_half_edge"], [87.0, 93.0])
        self.assertIn("upper bound", v2.BAR["crps_vs_v1"])

    def test_the_bar_applied(self):
        good = {"band_50_half_edge": 50.0, "band_90_half_edge": 90.0}
        paired = {"interval": {"lower": -0.01, "upper": 0.02}}
        self.assertTrue(all(v2.bar_verdict(good, paired).values()))
        self.assertFalse(v2.bar_verdict(dict(good, band_50_half_edge=44.9), paired)["band_50"])
        self.assertFalse(v2.bar_verdict(dict(good, band_90_half_edge=93.1), paired)["band_90"])
        self.assertFalse(v2.bar_verdict(good, {"interval": {"lower": -0.03, "upper": -0.001}})["crps_no_worse"])

    def test_the_gate_applied(self):
        coverage = {"band_50": {"lower": 44.0, "upper": 51.0}, "band_90": {"lower": 88.0, "upper": 95.0}}
        paired = {"interval": {"lower": -0.01, "upper": 0.02}}
        self.assertTrue(all(v2.gate_verdict(coverage, paired).values()))
        self.assertFalse(v2.gate_verdict(dict(coverage, band_50={"lower": 51.0, "upper": 60.0}),
                                         paired)["band_50_interval_includes_50"])
        self.assertFalse(v2.gate_verdict(dict(coverage, band_90={"lower": 80.0, "upper": 89.9}),
                                         paired)["band_90_interval_includes_90"])
        self.assertFalse(v2.gate_verdict(coverage, {"interval": {"lower": -0.1, "upper": -0.01}})
                         ["crps_not_worse_than_v1"])


def _cell_day(y, *, cells=(), q95=4.0):
    return {"y": y, "v": [-4.0, -1.0, 0.0, 1.0, q95], "cells": set(cells)}


class OuterValidationDeclarationTests(unittest.TestCase):
    """The outer-validation design (Eleonora's ruling on PR #252, amending #247), declared before scoring."""

    def test_the_blocks(self):
        self.assertEqual(v2.INNER, (date(2018, 6, 29), date(2022, 12, 31)))
        self.assertEqual(v2.OUTER, (date(2023, 1, 1), date(2025, 12, 31)))
        self.assertEqual(v2.INNER[0], v2.DECIDES[0])
        self.assertEqual(v2.OUTER[1], v2.DECIDES[1])
        self.assertEqual(v2.OUTER[0] - v2.INNER[1], timedelta(days=1))

    def test_the_gates(self):
        gates = {g["name"]: g for g in v2.CONDITIONAL_GATES["gates"]}
        self.assertEqual(v2.CONDITIONAL_GATES["minimum_days"], 20)
        self.assertEqual(gates["band_90_quarter_end"]["at_least"], 80.0)
        self.assertEqual(gates["band_90_scarce"]["at_least"], 85.0)
        self.assertEqual(gates["band_90_coupon_settlement"]["at_least"], 85.0)
        self.assertEqual(gates["above_q95_pooled"]["at_most"], 8.0)
        self.assertEqual(gates["above_q95_quarter_end"]["at_most"], 15.0)
        self.assertEqual(set(g["cell"] for g in gates.values()) - set(v2.CONDITIONAL_GATES["cells"]), set())

    def test_a_cell_under_twenty_days_is_inconclusive(self):
        days = [_cell_day(0.0) for _ in range(30)] + [_cell_day(9.0, cells=["quarter_end"]) for _ in range(19)]
        out = v2.conditional_gates(days, "v")
        self.assertEqual(out["band_90_quarter_end"]["days"], 19)
        self.assertEqual(out["band_90_quarter_end"]["verdict"], "inconclusive")
        self.assertEqual(out["above_q95_quarter_end"]["verdict"], "inconclusive")
        days.append(_cell_day(9.0, cells=["quarter_end"]))
        out = v2.conditional_gates(days, "v")
        self.assertEqual(out["band_90_quarter_end"]["verdict"], "fail")
        self.assertEqual(out["band_90_quarter_end"]["value"], 0.0)
        self.assertEqual(out["above_q95_quarter_end"]["value"], 100.0)

    def test_the_thresholds_are_inclusive_and_an_edge_counts_one_half(self):
        # 17 inside and 3 above: 85% inside, 15% above q95.
        days = [_cell_day(0.0, cells=["scarce", "quarter_end"]) for _ in range(17)]
        days += [_cell_day(9.0, cells=["scarce", "quarter_end"]) for _ in range(3)]
        out = v2.conditional_gates(days, "v")
        self.assertEqual(out["band_90_scarce"]["verdict"], "pass")
        self.assertEqual(out["above_q95_quarter_end"]["verdict"], "pass")
        self.assertEqual(out["above_q95_pooled"]["verdict"], "fail")
        # One of the three on the q95 edge instead: half inside, half above.
        days[-1] = _cell_day(4.000000000000002, cells=["scarce", "quarter_end"])
        out = v2.conditional_gates(days, "v")
        self.assertAlmostEqual(out["band_90_scarce"]["value"], 87.5)
        self.assertAlmostEqual(out["above_q95_quarter_end"]["value"], 12.5)

    def test_eligibility_under_each_reading(self):
        summary = {"coverage_half_tie": {"0.25": 25.0, "0.5": 50.0, "0.75": 75.0}, "band_90_half_edge": 90.0}
        passing = {"g": {"verdict": "pass"}, "h": {"verdict": "inconclusive"}}
        failing = dict(passing, k={"verdict": "fail"})
        self.assertTrue(v2.eligible_inner(summary, failing, reading="bar_only"))
        self.assertTrue(v2.eligible_inner(summary, passing, reading="bar_and_conditional_gates"))
        self.assertFalse(v2.eligible_inner(summary, failing, reading="bar_and_conditional_gates"))
        off = dict(summary, band_90_half_edge=86.0)
        self.assertFalse(v2.eligible_inner(off, passing, reading="bar_only"))
        with self.assertRaises(ValueError):
            v2.eligible_inner(summary, passing, reading="neither")

    def test_the_exploratory_label(self):
        self.assertEqual(v2.EXPLORATORY, "exploratory (selection-adjusted uncertainty not computed)")


class FixDeclarationTests(unittest.TestCase):
    """The diagnosis and the fix (rulings on PR #252 of 14:02 and 14:24), declared before the choice."""

    def test_the_candidates_and_their_complexity(self):
        self.assertEqual(set(v2.FIX_CANDIDATES),
                         {"iv_base", "v_level_tracking_by_type", "vi_width_pooled",
                          "vii_width_turn_vs_ordinary", "viii_width_by_type"})
        for name, spec in v2.FIX_CANDIDATES.items():
            self.assertEqual(len(spec["complexity"]), 3, name)
            if "partition" in spec:
                self.assertIn(spec["partition"], v2.FIX_PARTITIONS)
        self.assertIn(v2.CHOSEN_FIX, v2.FIX_CANDIDATES)
        self.assertEqual(v2.FIX_CANDIDATES["iv_base"]["complexity"], (2, 1, 1))

    def test_no_asymmetric_edge_rule(self):
        # Ruling item 4: an asymmetric or upper-only 5-95 edge rule would reopen interval-side-balance.md.
        # The width layer scales the 50% band about q50 symmetrically; no edge is moved on one side only.
        vector = [-4.0, -1.0, 0.0, 1.0, 4.0]
        days = [{"date": f"2020-01-{k + 1:02d}", "anchor": f"2020-01-{k:02d}", "y": 9.0, "issued": vector,
                 "kind": "quarter_end"} for k in range(1, 28)]
        out, _ = v2.width_tracking(days, "by_type", refit_every=5)
        for v in out:
            self.assertAlmostEqual(v[2] - v[0], v[4] - v[2])
            self.assertAlmostEqual(v[2] - v[1], v[3] - v[2])
        self.assertNotEqual(out[-1], vector)

    def test_partitions(self):
        self.assertEqual({v2._partition_class("pooled", k) for k in ("quarter_end", "ordinary")}, {"all"})
        self.assertEqual(v2._partition_class("turn_vs_ordinary", "tax_date"), "turn")
        self.assertEqual(v2._partition_class("turn_vs_ordinary", "ordinary"), "ordinary")
        self.assertEqual(v2._partition_class("by_type", "month_end"), "month_end")
        with self.assertRaises(ValueError):
            v2._partition_class("nope", "ordinary")

    def test_the_selection_rule(self):
        summaries = {"iv_base": {"crps": 1.85}, "vi_width_pooled": {"crps": 1.84},
                     "vii_width_turn_vs_ordinary": {"crps": 1.83}}
        excludes = {"interval": {"lower": 0.01, "upper": 0.03}}
        includes = {"interval": {"lower": -0.01, "upper": 0.03}}
        self.assertEqual(v2.select_fix(summaries, lambda n, leader: excludes)["recommended"],
                         "vii_width_turn_vs_ordinary")
        simpler = v2.select_fix(summaries, lambda n, leader: includes)
        self.assertEqual(simpler["leader"], "vii_width_turn_vs_ordinary")
        self.assertEqual(simpler["recommended"], "iv_base")
        self.assertIsNone(v2.select_fix({}, lambda n, leader: includes)["recommended"])

    def test_the_diagnosis_and_the_choice_refuse_the_outer_block(self):
        outer = [{"date": "2023-01-03", "anchor": "2022-12-30", "y": 1.0, "pid": [0.0] * 5, "kind": "ordinary",
                  "type": "ordinary", "reporting_type": "ordinary", "regime": "2021-23", "cells": set(),
                  "iv": [0.0] * 5, "v1": [0.0] * 5}]
        with self.assertRaises(ValueError):
            v2.inner_diagnosis(outer, {"iv": "iv"}, ["2021-23"])
        with self.assertRaises(ValueError):
            v2.fix_choice(outer, [], {}, [], None)

    def test_year_end_is_the_december_quarter_end(self):
        day = {"date": "2020-12-31", "type": "quarter_end", "cells": set()}
        self.assertTrue(v2._cell_members(day)["year_end"])
        self.assertTrue(v2._cell_members(dict(day, date="2020-09-30"))["quarter_end"])
        self.assertFalse(v2._cell_members(dict(day, date="2020-09-30"))["year_end"])


class QuarterEndDeclarationTests(unittest.TestCase):
    """The quarter-end location term (Eleonora's ruling on PR #252 of 6 October 2026), declared before it is scored.

    The candidates, the rule that chooses among them and the depth of v2's trees are fixed in one commit, before any
    candidate is walked. The depth is a setting of the fit (`ml.fit_gradient_boosted_quantiles(max_depth=...)`), not an
    override of the estimator class in this script.
    """

    def test_the_candidates_and_their_complexity(self):
        self.assertEqual(set(v2.QE_CANDIDATES),
                         {"base", "qe_indicator", "qe_indicator_and_month_end_countdown", "direct_pairs"})
        for name, spec in v2.QE_CANDIDATES.items():
            self.assertEqual(len(spec["complexity"]), 2, name)
            for column in spec["features"]:
                self.assertIn(column, CALENDAR_FEATURES, name)
            self.assertIn(spec["training_pairs"], (None, *ml.TRAINING_PAIRS), name)
        self.assertEqual(v2.QE_CANDIDATES["base"]["complexity"], (0, 0))
        self.assertEqual(v2.QE_CANDIDATES["base"]["features"], ())
        self.assertIsNone(v2.QE_CANDIDATES["base"]["training_pairs"])
        # Changing how the trees are trained is less simple than adding an input column.
        self.assertLess(v2.QE_CANDIDATES["qe_indicator"]["complexity"], v2.QE_CANDIDATES["direct_pairs"]["complexity"])
        self.assertLess(v2.QE_CANDIDATES["qe_indicator"]["complexity"],
                        v2.QE_CANDIDATES["qe_indicator_and_month_end_countdown"]["complexity"])

    def test_the_trees_depth_is_an_ml_setting_not_a_script_override(self):
        self.assertEqual(v2.V2_TREE_SETTINGS, {"max_depth": 3})
        base = functools.partial(ml.fit_gradient_boosted_quantiles, regressors=("tga", "sofr_volume"))
        before = ml._estimator_class
        fit, features = v2.candidate_setup(base, ("tga", "spread_bps", "sofr_volume"), "base")
        self.assertIs(ml._estimator_class, before)
        self.assertEqual(fit.keywords["max_depth"], 3)
        self.assertEqual(fit.keywords["regressors"], ("tga", "sofr_volume"))
        self.assertEqual(features, ("tga", "spread_bps", "sofr_volume"))
        self.assertNotIn("training_pairs", fit.keywords)

    def test_a_candidate_adds_exactly_what_it_declares(self):
        base = functools.partial(ml.fit_gradient_boosted_quantiles, regressors=("tga",))
        fit, features = v2.candidate_setup(base, ("tga", "spread_bps"), "qe_indicator_and_month_end_countdown")
        self.assertEqual(fit.keywords["regressors"], ("tga", "quarter_end", "days_to_month_end"))
        self.assertEqual(features, ("tga", "spread_bps", "quarter_end", "days_to_month_end"))
        fit, features = v2.candidate_setup(base, ("tga", "spread_bps"), "direct_pairs")
        self.assertEqual(fit.keywords["training_pairs"], "direct")
        self.assertEqual(features, ("tga", "spread_bps"))
        with self.assertRaises(ValueError):
            v2.candidate_setup(base, ("tga", "spread_bps"), "nope")
        with self.assertRaises(ValueError):  # a feature the published set already carries
            v2.candidate_setup(functools.partial(ml.fit_gradient_boosted_quantiles, regressors=("quarter_end",)),
                               ("quarter_end", "spread_bps"), "qe_indicator")

    def test_the_selection_rule_is_the_fixs(self):
        self.assertEqual(v2.QE_SELECTION["rule"], v2.FIX_SELECTION["rule"])
        summaries = {"base": {"crps": 1.83}, "qe_indicator": {"crps": 1.82}, "direct_pairs": {"crps": 1.81}}
        excludes = {"interval": {"lower": 0.001, "upper": 0.03}}
        includes = {"interval": {"lower": -0.01, "upper": 0.03}}
        self.assertEqual(v2.select_quarter_end(summaries, lambda n, leader: excludes)["recommended"], "direct_pairs")
        simpler = v2.select_quarter_end(summaries, lambda n, leader: includes)
        self.assertEqual(simpler["leader"], "direct_pairs")
        self.assertEqual(simpler["recommended"], "base")
        self.assertIsNone(v2.select_quarter_end({}, lambda n, leader: includes)["recommended"])

    def test_the_choice_refuses_the_outer_block(self):
        outer = [{"date": "2023-01-03", "anchor": "2022-12-30", "y": 1.0, "pid": [0.0] * 5, "kind": "ordinary"}]
        with self.assertRaises(ValueError):
            v2.quarter_end_choice({"base": outer}, [], {}, [], None)

    def test_a_cell_under_the_minimum_gets_no_interval(self):
        # Ruling item 4: under `CONDITIONAL_GATES["minimum_days"]` days a diagnostic cell carries no interval.
        vector = [-4.0, -1.0, 0.0, 1.0, 4.0]
        few = [{"date": f"2020-03-{k:02d}", "y": 0.5, "v": vector} for k in range(1, 6)]
        cell = v2._diagnostic_cell(few, "v", ("t",))
        self.assertEqual(cell["days"], 5)
        self.assertEqual(cell["band_50"]["interval"], "too few days")
        self.assertNotIn("lower", cell["band_50"])
        self.assertNotIn("lower", cell["band_90"])
        many = [dict(d, date=f"2020-04-{k:02d}") for k, d in enumerate(few * 5, 1)]
        cell = v2._diagnostic_cell(many, "v", ("t",))
        self.assertIn("lower", cell["band_50"])


def _sha(rows):
    return v2.vectors_sha256(rows)


class RecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(RECORD.read_text(encoding="utf-8"))
        cls.diagnosis = json.loads(DIAGNOSIS.read_text(encoding="utf-8"))

    def test_v1_is_byte_identical_to_its_walk_before_this_change(self):
        """v1's quantiles, walked on the published panel with this tree, are #247's to the byte."""

        before = [[day, vector] for day, _y, vector in self.diagnosis["v1_h1_per_day"]]
        self.assertEqual(self.record["v1_unchanged"]["v1_vectors_sha256"], _sha(before))
        self.assertTrue(self.record["v1_unchanged"]["identical_to_v1_interior_diagnosis"])
        self.assertEqual(self.record["panel_sha256"], self.diagnosis["panel_sha256"])

    def test_v2_is_the_reference_of_the_chosen_candidate(self):
        """v2 is (iv): #247's interior tracking applied to the PID vectors of its depth-3 trees."""

        anchors = dict(self.record["anchors"])
        rows = self.record["per_day_h1"]["rows"]
        self.assertEqual(self.record["per_day_h1"]["columns"],
                         ["date", "y", "pid_of_v2_trees", "interior_tracked", "v2"])
        days = [{"date": day, "anchor": anchors[day], "y": y, "issued": pid} for day, y, pid, _t, _v2 in rows]
        expected, _ = dx.interior_tracking(days)
        self.assertEqual([tracked for *_, tracked, _v2 in rows], expected)
        kinds = dict(self.record["width_classes_per_day"])
        widened, _ = v2.width_tracking(
            [dict(d, issued=v, kind=kinds[d["date"]]) for d, v in zip(days, expected)],
            v2.FIX_CANDIDATES[v2.CHOSEN_FIX]["partition"])
        self.assertEqual([vector for *_, vector in rows], widened)
        self.assertEqual(self.record["v2_vectors_sha256"], _sha([[d["date"], v] for d, v in zip(days, widened)]))
        self.assertEqual([[day, y] for day, y, _v in self.diagnosis["v1_h1_per_day"]],
                         [[day, y] for day, y, *_ in rows])
        self.assertTrue(self.record["v2_equals_reference"])
        self.assertEqual(v2.CHOSEN, "iv_regularised_and_tracking")
        self.assertEqual(self.record["model"]["tree_settings"], v2.V2_TREE_SETTINGS)
        self.assertEqual(dx.VARIANTS[v2.V2_TREE_VARIANT], v2.V2_TREE_SETTINGS)

    def test_v1_reproduces_the_published_crps(self):
        published = json.loads(CRPS_RECORD.read_text(encoding="utf-8"))
        final = json.loads(FINAL.read_text(encoding="utf-8"))
        expected = {e["scored_date"]: e["loss_b_bps"] for e in published["comparison"]["per_origin"]}
        expected.update({e["scored_date"]: e["loss_b_bps"] for e in final["primary"]["window_per_origin"]})
        ours = {day: crps_from_quantiles(LEVELS, vector, y)
                for day, y, vector in self.diagnosis["v1_h1_per_day"]}
        self.assertEqual(ours, expected)
        self.assertTrue(self.record["v1_unchanged"]["reproduces_published_crps"])

    def test_no_day_after_the_opened_tier(self):
        self.assertLessEqual(max(day for day, _ in self.record["anchors"]), "2026-09-03")
        self.assertEqual(self.record["windows"]["decides"]["last"], "2025-12-31")

    def test_the_verdicts_are_the_declared_rules_applied(self):
        main = self.record["window_2018_2025"]
        self.assertEqual(main["bar"], v2.bar_verdict(main["coverage"], main["crps"]["v2_vs_v1"]))
        check = self.record["check_2026"]
        self.assertEqual(check["gate"], v2.gate_verdict(check["coverage_interval"], check["crps"]["v2_vs_v1"]))
        self.assertIn("seen data, not evidence", check["label"])
        self.assertEqual(self.record["bar_declared"], v2.BAR)
        self.assertEqual(self.record["gate_declared"], v2.GATE)

    def test_the_choice_was_redone_on_the_inner_block(self):
        declared = self.record["outer_validation_declared"]
        self.assertEqual(declared["conditional_gates"], v2.CONDITIONAL_GATES)
        self.assertEqual(declared["inner_selection"], v2.INNER_SELECTION)
        self.assertIsNotNone(v2.CHOSEN)
        self.assertEqual(declared["chosen"], v2.CHOSEN)
        choice = self.record["inner_choice"]
        self.assertEqual(choice["window"], ["2018-06-29", "2022-12-31"])
        self.assertEqual(choice["selection"][v2.BINDING_READING]["recommended"], v2.CHOSEN)
        self.assertEqual(set(choice["selection"]), set(v2.READINGS))
        self.assertTrue(all(c["first"] <= "2022-12-31" for c in choice["i_step_choices_inner"]))

    def test_the_fix_was_chosen_on_the_inner_block_by_the_declared_rule(self):
        declared = self.record["outer_validation_declared"]["fix"]
        self.assertEqual(declared["chosen"], v2.CHOSEN_FIX)
        self.assertEqual(declared["candidates"], json.loads(json.dumps(v2.FIX_CANDIDATES)))
        self.assertEqual(self.record["outer_validation_declared"]["diagnosis"], v2.DIAGNOSIS)
        fix = self.record["fix_choice"]
        self.assertEqual(fix["window"], ["2018-06-29", "2022-12-31"])
        self.assertEqual(fix["selection"]["recommended"], v2.CHOSEN_FIX)
        self.assertEqual(set(fix["candidates"]), set(v2.FIX_CANDIDATES))
        # The rule applied again, to the recorded summaries: the leader has the lowest CRPS of the eligible.
        eligible = fix["selection"]["eligible"]
        leader = min(eligible, key=lambda n: (fix["candidates"][n]["inner"]["crps"],
                                              tuple(fix["candidates"][n]["complexity"]), n))
        self.assertEqual(fix["selection"]["leader"], leader)
        for name, candidate in fix["candidates"].items():
            gates = candidate["conditional_gates_inner"]
            self.assertEqual(name in eligible,
                             dx.eligible(candidate["inner"]) and not any(g["verdict"] == "fail" for g in gates.values()))
        self.assertTrue(all(n in fix["candidates"] for n in eligible))

    def test_the_diagnosis_reads_the_inner_block_only(self):
        diagnosis = self.record["inner_diagnosis"]
        self.assertEqual(diagnosis["declared"], v2.DIAGNOSIS)
        self.assertEqual(diagnosis["days"], self.record["inner_block"]["days"])
        self.assertEqual(set(diagnosis["models"]), {"v1", "iv", "fixed"})
        for model in diagnosis["models"].values():
            self.assertEqual(set(model["by_cell"]), set(v2.DIAGNOSIS["cells"]))
            self.assertEqual(model["by_cell"]["all"]["days"], diagnosis["days"])
            kinds = ("quarter_end", "tax_date", "month_end", "ordinary")
            self.assertEqual(sum(model["by_cell"][k]["days"] for k in kinds), diagnosis["days"])
            self.assertEqual(sum(c["days"] for c in model["by_regime"].values()), diagnosis["days"])
            self.assertEqual(sum(c["days"] for c in model["by_reporting_day_type"].values()), diagnosis["days"])
            self.assertLessEqual(model["by_cell"]["year_end"]["days"], model["by_cell"]["quarter_end"]["days"])
        self.assertIn("diagnostics only", v2.DIAGNOSIS["status"])

    def test_the_outer_block_was_looked_at_twice_and_says_so(self):
        first, second = self.record["outer_block_before_fix"], self.record["outer_block"]
        self.assertEqual((first["first"], first["last"]), (second["first"], second["last"]))
        self.assertIn("first look", first["label"])
        self.assertIn("second look", second["label"])
        self.assertEqual(first["coverage_v1"], second["coverage_v1"])

    def test_the_inner_and_outer_verdicts_are_the_declared_rules_applied(self):
        for name in ("inner_block", "outer_block"):
            block = self.record[name]
            with self.subTest(block=name):
                self.assertEqual(block["bar"], v2.bar_verdict(block["coverage"], block["crps"]["v2_vs_v1"]))
                for gate in block["conditional_gates"].values():
                    if gate["days"] < v2.CONDITIONAL_GATES["minimum_days"]:
                        self.assertEqual(gate["verdict"], "inconclusive")
                    elif "at_least" in gate:
                        self.assertEqual(gate["verdict"], "pass" if gate["value"] >= gate["at_least"] else "fail")
                    else:
                        self.assertEqual(gate["verdict"], "pass" if gate["value"] <= gate["at_most"] else "fail")
        self.assertEqual(self.record["outer_block"]["first"], "2023-01-03")
        self.assertEqual(self.record["inner_block"]["last"], "2022-12-30")

    def test_every_historical_edge_is_labelled_exploratory(self):
        for name in ("inner_block", "outer_block", "window_2018_2025"):
            self.assertEqual(self.record[name]["crps"]["v2_vs_v1"]["edge_label"], v2.EXPLORATORY)

    def test_crps_figures_are_finite(self):
        for window in ("window_2018_2025", "check_2026"):
            for side in ("v2_vs_v1", "v2_vs_persistence"):
                cell = self.record[window]["crps"][side]
                self.assertTrue(math.isfinite(cell["mean"]))
                self.assertLessEqual(cell["interval"]["lower"], cell["interval"]["upper"])


if __name__ == "__main__":
    unittest.main()
