"""Pressure model v2's interior calibration (#244).

`repo_model.interior` is standard library only, so this module runs in the
core job.

* `CandidateDeclarationTests`: the candidates are declared in code before any
  scoring, at most four, on the conformal PID's existing constants.
* `OrderingGuardTests`: an issued vector keeps q05 <= q25 <= q50 <= q75 <= q95,
  and a vector that does not is refused with `ValueError`.
* `InteriorObservabilityGuardTests`: a label moves an interior tracker only
  once it was public at the decision instant of the band being issued.
* `InteriorCalibrationTests`: what each candidate does to v1's interior, and
  that it never moves v1's outer quantiles.
* `FoldInteriorTests`: v2 inside a fold loop, on top of v1's online
  calibration, which it leaves exactly as it was.
"""

from __future__ import annotations

import math
import random
import unittest
from datetime import date, timedelta

from repo_model import interior, recalibration
from repo_model.metrics import crps_from_quantiles
from repo_model.splits import LookAheadError

LEVELS = (0.05, 0.25, 0.5, 0.75, 0.95)


def days_of(vectors, *, start=date(2021, 1, 4), lag=2):
    """One `OnlineDay` per vector, each anchored `lag` business days before itself."""

    dates = []
    when = start
    while len(dates) < len(vectors) + lag:
        if when.weekday() < 5:
            dates.append(when)
        when += timedelta(days=1)
    return [
        recalibration.OnlineDay(
            scored_date=dates[position + lag], anchor=dates[position],
            vector=tuple(vector), calendar=(),
        )
        for position, vector in enumerate(vectors)
    ]


def narrow_high(count, *, seed=20261006):
    """v1-like vectors whose interior is too narrow and centred too high, with outcomes.

    Outcomes are N(0, 2): the true quartiles are about -1.35 and +1.35 and the
    5th and 95th about -3.29 and +3.29. The vectors' outer pair is right; their
    interior is a 0.6 bp band about +0.8.
    """

    rng = random.Random(seed)
    vector = (-3.29, 0.5, 0.8, 1.1, 3.29)
    return [vector] * count, [rng.gauss(0.0, 2.0) for _ in range(count)]


def coverage(vectors, actuals):
    return sum(v[1] <= y <= v[3] for v, y in zip(vectors, actuals)) / len(actuals)


class CandidateDeclarationTests(unittest.TestCase):
    """The candidate set is fixed in code before any fold is scored (#244, Do 1)."""

    def test_at_most_four_named_candidates(self):
        self.assertLessEqual(len(interior.CANDIDATES), 4)
        self.assertGreaterEqual(len(interior.CANDIDATES), 1)
        names = [candidate.name for candidate in interior.CANDIDATES]
        self.assertEqual(len(set(names)), len(names))
        for candidate in interior.CANDIDATES:
            self.assertIn(candidate.kind, interior.KINDS)

    def test_the_constants_are_the_pid_grids_own(self):
        for candidate in interior.CANDIDATES:
            self.assertIn(candidate.step, recalibration.PID_GRID_STEPS)
            self.assertIn(candidate.integrator_gain, recalibration.PID_GRID_INTEGRATOR_GAINS)
            self.assertIn(candidate.saturation, recalibration.PID_GRID_SATURATIONS)

    def test_the_suggested_candidates_are_declared(self):
        kinds = {(c.kind, c.integrator_gain > 0) for c in interior.CANDIDATES}
        self.assertIn(("per_level", False), kinds)
        self.assertIn(("shift_scale", False), kinds)
        self.assertIn(("per_level", True), kinds)
        self.assertLess(interior.FALLBACK, len(interior.CANDIDATES))

    def test_the_declaration_names_every_constant(self):
        declared = interior.declaration()
        self.assertEqual([c["name"] for c in declared["candidates"]],
                         [c.name for c in interior.CANDIDATES])
        for key in ("PID_STEP_WINDOW", "PID_SCALE_FLOOR", "PID_TANGENT_LIMIT"):
            self.assertIn(key, declared["fixed_constants"])
        self.assertEqual(declared["fallback"], interior.CANDIDATES[interior.FALLBACK].name)


class OrderingGuardTests(unittest.TestCase):
    """q05 <= q25 <= q50 <= q75 <= q95, enforced by `ValueError` (#244, Do 1).

    Red first: written before `repo_model.interior` existed; the module failed
    to import (`ImportError`).

    Mutation record. In a disposable copy of the tree under /tmp,
    `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`, CPython 3.11, this class run
    alone; unmutated control green; the mutation confirmed applied by `diff`
    against the tree:

    1. `require_ordered`'s guard, `if any(low > high for low, high in
       zip(values, values[1:])):`, mutated to `if False:`. Killed:
       `test_an_unordered_vector_is_refused` failed with
       `AssertionError: ValueError not raised`.
    """

    def test_an_unordered_vector_is_refused(self):
        with self.assertRaises(ValueError):
            interior.require_ordered((0.0, 2.0, 1.0, 3.0, 4.0))
        with self.assertRaises(ValueError):
            interior.require_ordered((0.0, 1.0, 2.0, 3.0, -1.0))

    def test_a_non_finite_vector_is_refused(self):
        with self.assertRaises(ValueError):
            interior.require_ordered((0.0, 1.0, math.nan, 3.0, 4.0))

    def test_an_ordered_vector_passes_unchanged(self):
        vector = (-1.0, 0.0, 0.0, 1.0, 1.0)
        self.assertEqual(interior.require_ordered(vector), vector)

    def test_every_issued_band_is_ordered_even_when_the_trackers_run_away(self):
        # Outcomes far below the whole band drive every interior level down,
        # past v1's q05: the issued interior stops at q05, and stays ordered.
        vectors = [(-1.0, -0.5, 0.0, 0.5, 1.0)] * 200
        actuals = [-40.0] * 100 + [40.0] * 100
        for candidate in interior.CANDIDATES:
            bands = interior.interior_walk(days_of(vectors), actuals, candidate)
            for band, vector in zip(bands, vectors):
                interior.require_ordered(band)
                self.assertEqual((band[0], band[-1]), (vector[0], vector[-1]))


class InteriorObservabilityGuardTests(unittest.TestCase):
    """A label updates an interior tracker only once public at the decision (#244, Do 2).

    The same rule `PidState.observe` enforces for v1's outer pair: a scored
    day's label is observable at a decision whose anchor is on or after it.
    `InteriorState.observe` refuses any other with `LookAheadError`, and
    `OnlineInterior` holds each label back until it qualifies.

    Red first: written before `repo_model.interior` existed; the module failed
    to import (`ImportError`).

    Mutation record. In a disposable copy of the tree under /tmp,
    `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`, CPython 3.11, this class run
    alone; unmutated control green; the mutation confirmed applied by `diff`
    against the tree:

    1. `InteriorState.observe`'s guard, `if day.scored_date > decision.anchor:`,
       mutated to `if day.scored_date > decision.scored_date:` (a label is
       taken as observable on any day before the one being forecast). Killed:
       `test_a_label_not_observable_at_the_decision_is_refused` failed with
       `AssertionError: LookAheadError not raised`.
    """

    def test_a_label_not_observable_at_the_decision_is_refused(self):
        vectors, _ = narrow_high(10)
        days = days_of(vectors)
        for candidate in interior.CANDIDATES:
            state = interior.InteriorState(candidate)
            decision = days[5]
            unobservable = days[4]
            self.assertGreater(unobservable.scored_date, decision.anchor)
            band = state.band(unobservable)
            with self.assertRaises(LookAheadError) as caught:
                state.observe(unobservable, band, 0.0, decision)
            self.assertIn(str(unobservable.scored_date), str(caught.exception))
            observable = days[3]
            self.assertEqual(observable.scored_date, decision.anchor)
            state.observe(observable, state.band(observable), 0.0, decision)

    def test_labels_are_observed_once_in_date_order(self):
        vectors, _ = narrow_high(10)
        days = days_of(vectors)
        state = interior.InteriorState(interior.CANDIDATES[0])
        state.observe(days[3], state.band(days[3]), 0.0, days[6])
        with self.assertRaises(ValueError):
            state.observe(days[2], state.band(days[2]), 0.0, days[6])
        with self.assertRaises(ValueError):
            state.observe(days[3], state.band(days[3]), 0.0, days[6])

    def test_no_band_moves_with_a_label_its_decision_could_not_see(self):
        count = 120
        vectors, actuals = narrow_high(count)
        days = days_of(vectors)
        for candidate in interior.CANDIDATES:
            bands = interior.interior_walk(days, actuals, candidate)
            for target in (30, 60, 119):
                for changed in range(target - 1, count):
                    if days[changed].scored_date <= days[target].anchor:
                        continue
                    moved = list(actuals)
                    moved[changed] += 50.0
                    again = interior.interior_walk(days, moved, candidate)
                    self.assertEqual(again[target], bands[target], (candidate.name, target, changed))

    def test_an_observable_label_does_move_the_band(self):
        count = 60
        vectors, actuals = narrow_high(count)
        days = days_of(vectors)
        for candidate in interior.CANDIDATES:
            bands = interior.interior_walk(days, actuals, candidate)
            target = 40
            changed = target - 2
            self.assertEqual(days[changed].scored_date, days[target].anchor)
            # Moved to the other side of every level it was issued, so each
            # tracker sees a different miss.
            moved = list(actuals)
            moved[changed] = -50.0 if actuals[changed] > bands[changed][2] else 50.0
            again = interior.interior_walk(days, moved, candidate)
            self.assertNotEqual(again[target], bands[target], candidate.name)

    def test_an_unanchored_or_out_of_order_day_is_refused(self):
        vectors, _ = narrow_high(5)
        days = days_of(vectors)
        bad = days[0]._replace(anchor=days[0].scored_date)
        with self.assertRaises(LookAheadError):
            interior.interior_walk([bad], [0.0], interior.CANDIDATES[0])
        with self.assertRaises(ValueError):
            interior.interior_walk([days[1], days[0]], [0.0, 0.0], interior.CANDIDATES[0])
        with self.assertRaises(ValueError):
            interior.interior_walk(days, [0.0], interior.CANDIDATES[0])


class InteriorCalibrationTests(unittest.TestCase):
    """Each candidate on a v1-like stream whose interior is too narrow and too high."""

    def test_the_outer_pair_is_v1s_exactly(self):
        count = 300
        vectors, actuals = narrow_high(count)
        for candidate in interior.CANDIDATES:
            bands = interior.interior_walk(days_of(vectors), actuals, candidate)
            for band, vector in zip(bands, vectors):
                self.assertEqual(band[0], vector[0])
                self.assertEqual(band[-1], vector[-1])

    def test_the_first_band_is_v1s_own(self):
        vectors, actuals = narrow_high(5)
        for candidate in interior.CANDIDATES:
            bands = interior.interior_walk(days_of(vectors), actuals, candidate)
            self.assertEqual(bands[0], vectors[0])

    def test_each_candidate_moves_the_50_band_toward_half(self):
        count = 2000
        vectors, actuals = narrow_high(count)
        before = coverage(vectors, actuals)
        self.assertLess(before, 0.2)
        for candidate in interior.CANDIDATES:
            bands = interior.interior_walk(days_of(vectors), actuals, candidate)
            late = slice(count // 2, None)
            after = coverage(bands[late], actuals[late])
            self.assertGreater(after, 0.38, candidate.name)
            self.assertLess(after, 0.62, candidate.name)
            crps_v1 = sum(crps_from_quantiles(LEVELS, v, y) for v, y in zip(vectors[late], actuals[late]))
            crps_v2 = sum(crps_from_quantiles(LEVELS, v, y) for v, y in zip(bands[late], actuals[late]))
            self.assertLess(crps_v2, crps_v1, candidate.name)

    def test_a_calibrated_interior_stays_about_where_it_is(self):
        count = 2000
        rng = random.Random(7)
        vector = (-3.29, -1.35, 0.0, 1.35, 3.29)
        vectors = [vector] * count
        actuals = [rng.gauss(0.0, 2.0) for _ in range(count)]
        for candidate in interior.CANDIDATES:
            bands = interior.interior_walk(days_of(vectors), actuals, candidate)
            self.assertAlmostEqual(coverage(bands, actuals), 0.5, delta=0.06)
            centre = sum(band[2] for band in bands) / count
            self.assertAlmostEqual(centre, 0.0, delta=0.5)

    def test_an_outcome_on_an_edge_counts_half(self):
        self.assertEqual(interior.below(1.0, 1.0), 0.5)
        self.assertEqual(interior.below(0.0, 1.0), 1.0)
        self.assertEqual(interior.below(2.0, 1.0), 0.0)


class _FakePid:
    """A stand-in for v1's fold-loop calibration: it records what it is told."""

    name = "conformal_pid_nested"

    def __init__(self, dates, vectors):
        self.dates = dates
        self.vectors = vectors
        self.calls = []
        self.settings = {"calibration": self.name, "calibration_constants": {"PID_STEP_WINDOW": 100}}

    def view(self, model, index, feature_row):
        self.calls.append(("view", index, feature_row.date))
        return recalibration._PidView(model, feature_row.date, self.vectors[index])

    def label(self, index, actual):
        self.calls.append(("label", index, actual))

    def account(self):
        return {"days": len([c for c in self.calls if c[0] == "view"])}


class _Model:
    levels = LEVELS

    def predict(self, feature_row):  # pragma: no cover - the view never asks it
        raise AssertionError("the base fit is read through v1's view")


class _Row:
    def __init__(self, when):
        self.date = when


class FoldInteriorTests(unittest.TestCase):
    """v2 alongside a fold loop, on top of v1's calibration (#244, Do 5)."""

    def setup_walk(self, count=90, **kwargs):
        vectors, actuals = narrow_high(count + 2)
        days = days_of(vectors[:count])
        dates = [day.anchor for day in days[:2]] + [day.scored_date for day in days]
        rows = [_Row(when) for when in dates]
        v1_vectors = [None, None] + list(vectors[:count])
        pid = _FakePid(dates, v1_vectors)
        fold = interior.FoldInterior(rows, pid, refit_every=21, **kwargs)
        issued = []
        for position in range(count):
            index = position + 2
            view = fold.view(_Model(), index, _Row(dates[position]))
            issued.append(tuple(view.predict(_Row(dates[position]))))
            fold.label(index, actuals[position])
        return fold, pid, issued, v1_vectors, actuals[:count]

    def test_v1_is_called_exactly_as_without_v2(self):
        fold, pid, issued, v1_vectors, actuals = self.setup_walk()
        expected = []
        for position, actual in enumerate(actuals):
            index = position + 2
            expected += [("view", index, pid.dates[position]), ("label", index, actual)]
        self.assertEqual(pid.calls, expected)
        self.assertEqual(fold.settings, pid.settings)
        for day, vector in zip(fold.days, v1_vectors[2:]):
            self.assertEqual(day.v1, vector)

    def test_the_issued_band_keeps_v1s_outer_pair(self):
        fold, pid, issued, v1_vectors, _ = self.setup_walk()
        for band, vector in zip(issued, v1_vectors[2:]):
            self.assertEqual((band[0], band[-1]), (vector[0], vector[-1]))
            interior.require_ordered(band)

    def test_nested_selection_chooses_from_observable_days_only(self):
        fold, *_ = self.setup_walk()
        self.assertEqual(len(fold.blocks), math.ceil(90 / 21))
        self.assertEqual(fold.blocks[0].chosen, interior.FALLBACK)
        self.assertEqual(fold.blocks[0].past_days, 0)
        for block in fold.blocks:
            seen = sum(1 for day in fold.days if day.scored_date <= block.anchor)
            self.assertEqual(block.past_days, seen)
        for day in fold.days:
            self.assertEqual(day.chosen, [b for b in fold.blocks if b.first_scored <= day.scored_date][-1].chosen)

    def test_a_frozen_candidate_is_issued_on_every_day(self):
        frozen = len(interior.CANDIDATES) - 1
        fold, pid, issued, *_ = self.setup_walk(frozen=frozen)
        self.assertEqual(fold.blocks, ())
        for day, band in zip(fold.days, issued):
            self.assertEqual(band, day.bands[frozen])

    def test_a_label_for_another_day_is_refused(self):
        vectors, _ = narrow_high(4)
        days = days_of(vectors)
        dates = [day.anchor for day in days[:2]] + [day.scored_date for day in days]
        rows = [_Row(when) for when in dates]
        fold = interior.FoldInterior(rows, _FakePid(dates, [None, None] + vectors), refit_every=21)
        fold.view(_Model(), 2, _Row(dates[0]))
        with self.assertRaises(ValueError):
            fold.label(3, 0.0)
        with self.assertRaises(ValueError):
            fold.view(_Model(), 3, _Row(dates[1]))


if __name__ == "__main__":
    unittest.main()
