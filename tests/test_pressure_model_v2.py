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
* `OuterValidationDeclarationTests`: the inner and outer blocks, the
  conditional gates and the eligibility readings, as declared before scoring.
* `RecordTests`: `docs/runs/pressure_model_v2_distribution_h1.json` against
  #247's record (v1 byte-identical on the published panel, v2 the reference
  of the chosen candidate), the published CRPS records, the declared bar and
  gate, the inner choice and the outer block.

Red first: written before `repo_model.interior` and
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

import importlib.util
import json
import math
import random
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import interior, recalibration
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
        days = [{"date": day, "anchor": anchors[day], "y": y, "issued": pid} for day, y, pid, _v2 in rows]
        expected, _ = dx.interior_tracking(days)
        self.assertEqual([v for *_, v in rows], expected)
        self.assertEqual(self.record["v2_vectors_sha256"], _sha([[d["date"], v] for d, v in zip(days, expected)]))
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
