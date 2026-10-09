"""The stacked ensemble of the track forecasts (#410, track X of #374): `repo_model.stacking`.

What is covered:

* `FitTests` -- the logistic stack's fit, standard library only: it recovers a
  planted weighting, the penalty pulls towards the equal-weight pool, and a
  member that is only noise gets a small weight.
* `WindowTests` -- the training window of a refit: only earlier blocks, only
  days whose outcome was public at the block's first decision instant
  (`LookAheadError` otherwise), and the equal-weight fallback when the window is
  short or lacks one outcome class.
* `StackTests` -- the walk-forward stack: a forecast on a block reads no
  outcome of that block or of a day after the training end, and the declaration
  on disk is the one the code reads.

**Recorded mutations** (disposable copy of the tree, `PYTHONDONTWRITEBYTECODE=1`,
`test_stacking` run alone, each mutation confirmed applied by `grep` and restored
before the next):

1. `require_known`: change `if training_end is None or days[k] > training_end` to
   `if training_end is None` (the guard no longer compares a window day with the
   training end). `WindowTests.test_a_day_after_the_training_end_is_refused`
   fails: `AssertionError: LookAheadError not raised`.
2. `training_end_of`: change `position[days[start]] - horizon - 1` to
   `position[days[start]] - horizon` (the outcome of the day before the block is
   treated as public, though SOFR for a day is published the morning after).
   Three tests fail, among them
   `WindowTests.test_the_last_known_day_leaves_a_gap_of_the_horizon_plus_one`
   and `StackTests.test_the_probabilities_of_the_days_inside_the_gap_are_not_read`.
3. `training_window`: delete the filter `and days[k] <= training_end` from the
   list comprehension, so the window is every earlier-block day. The guard
   `require_known` then raises `LookAheadError` on the first refit whose window
   holds a day inside the gap, and four tests error with it (`StackTests` and
   `WindowTests.test_the_window_holds_only_earlier_blocks_days`). The filter and
   the guard each catch a window that is too wide; this records that the guard
   stands on its own when the filter is gone.
"""

from __future__ import annotations

import json
import math
import random
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import stacking as st
from repo_model.splits import LookAheadError

REPO = Path(__file__).resolve().parents[1]


def _logit(p):
    return math.log(p / (1.0 - p))


def _sigmoid(z):
    return 1.0 / (1.0 + math.exp(-z))


def _business_days(count, start=date(2020, 1, 6)):
    out, day = [], start
    while len(out) < count:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


class FitTests(unittest.TestCase):
    def test_it_recovers_a_planted_weighting(self):
        rng = random.Random(1)
        rows, y = [], []
        for _ in range(4000):
            a, b = rng.uniform(-3, 1), rng.uniform(-3, 1)
            rows.append((a, b))
            y.append(1 if rng.random() < _sigmoid(-0.5 + 1.5 * a + 0.0 * b) else 0)
        intercept, weights = st.fit_logit_stack(rows, y, ridge=0.0)
        self.assertAlmostEqual(weights[0], 1.5, delta=0.25)
        self.assertAlmostEqual(weights[1], 0.0, delta=0.25)
        self.assertAlmostEqual(intercept, -0.5, delta=0.3)

    def test_the_penalty_pulls_towards_the_equal_weight_pool(self):
        rng = random.Random(2)
        rows = [(rng.uniform(-3, 1), rng.uniform(-3, 1)) for _ in range(300)]
        y = [1 if rng.random() < _sigmoid(2.0 * a) else 0 for a, _ in rows]
        _, loose = st.fit_logit_stack(rows, y, ridge=0.0)
        _, tight = st.fit_logit_stack(rows, y, ridge=1e6)
        for weight in tight:
            self.assertAlmostEqual(weight, 0.5, delta=1e-3)
        self.assertGreater(abs(loose[0] - 0.5), abs(tight[0] - 0.5))

    def test_a_row_of_the_wrong_width_is_refused(self):
        with self.assertRaises(ValueError):
            st.fit_logit_stack([(0.0, 0.0), (1.0,)], [0, 1], ridge=1.0)
        with self.assertRaises(ValueError):
            st.fit_logit_stack([(0.0, 0.0)], [0, 1], ridge=1.0)

    def test_the_logit_is_clipped(self):
        self.assertAlmostEqual(st.clipped_logit(0.0, 1e-4), _logit(1e-4))
        self.assertAlmostEqual(st.clipped_logit(1.0, 1e-4), _logit(1 - 1e-4))
        self.assertAlmostEqual(st.clipped_logit(0.5, 1e-4), 0.0)


class WindowTests(unittest.TestCase):
    def setUp(self):
        self.calendar = _business_days(200)
        self.days = tuple(self.calendar[10:190])

    def test_the_window_holds_only_earlier_blocks_days(self):
        window = st.training_window(self.days, self.calendar, start=42, horizon=1)
        self.assertTrue(all(k < 42 for k in window))
        self.assertEqual(window[-1] if window else None, 40)

    def test_the_last_known_day_leaves_a_gap_of_the_horizon_plus_one(self):
        for horizon in (1, 3, 5):
            window = st.training_window(self.days, self.calendar, start=63, horizon=horizon)
            position = {day: k for k, day in enumerate(self.calendar)}
            first = position[self.days[63]]
            self.assertEqual(position[self.days[window[-1]]], first - horizon - 1)

    def test_a_day_after_the_training_end_is_refused(self):
        with self.assertRaises(LookAheadError):
            st.require_known(self.days, [5, 41], training_end=self.days[20])

    def test_the_first_block_has_no_window(self):
        self.assertEqual(st.training_window(self.days, self.calendar, start=0, horizon=1), [])

    def test_a_short_window_or_one_class_falls_back_to_equal_weights(self):
        fb = st.Fallback(minimum_days=126, minimum_each_class=5)
        self.assertTrue(fb.applies(days=100, positives=20))
        self.assertTrue(fb.applies(days=300, positives=4))
        self.assertTrue(fb.applies(days=300, positives=297))
        self.assertFalse(fb.applies(days=300, positives=20))


class StackTests(unittest.TestCase):
    def _members(self, n, seed):
        rng = random.Random(seed)
        days = tuple(_business_days(n + 5)[5:])
        y = [1 if rng.random() < 0.15 else 0 for _ in range(n)]
        good = [min(0.95, max(0.02, 0.1 + 0.6 * v + rng.uniform(-0.05, 0.05))) for v in y]
        noise = [rng.uniform(0.02, 0.5) for _ in range(n)]
        return days, y, {"good": good, "noise": noise}

    def test_blocks_before_the_first_window_use_equal_weights(self):
        days, y, members = self._members(400, 3)
        calendar = _business_days(405)
        out = st.stack(days, calendar, members, y, horizon=1, step=21, ridge=1.0, clip=1e-4,
                       fallback=st.Fallback(126, 5))
        self.assertEqual(out.trace[0]["mode"], "equal")
        self.assertEqual(out.trace[0]["training_days"], 0)
        first = [_sigmoid(sum(_logit(members[m][k]) for m in members) / 2.0) for k in range(21)]
        for got, want in zip(out.probabilities[:21], first):
            self.assertAlmostEqual(got, want)

    def test_later_blocks_are_fitted_and_favour_the_informative_member(self):
        days, y, members = self._members(600, 4)
        calendar = _business_days(605)
        out = st.stack(days, calendar, members, y, horizon=1, step=21, ridge=1.0, clip=1e-4,
                       fallback=st.Fallback(126, 5))
        last = out.trace[-1]
        self.assertEqual(last["mode"], "fitted")
        self.assertGreater(last["weights"][0], last["weights"][1] + 0.3)

    def test_a_forecast_does_not_read_the_outcome_of_its_own_block(self):
        days, y, members = self._members(400, 5)
        calendar = _business_days(405)
        base = st.stack(days, calendar, members, y, horizon=1, step=21, ridge=1.0, clip=1e-4,
                        fallback=st.Fallback(126, 5))
        flipped = list(y)
        for k in range(210, 231):  # the outcomes of one block, and only that block
            flipped[k] = 1 - flipped[k]
        again = st.stack(days, calendar, members, flipped, horizon=1, step=21, ridge=1.0, clip=1e-4,
                         fallback=st.Fallback(126, 5))
        self.assertEqual(base.probabilities[:231], again.probabilities[:231])
        self.assertNotEqual(base.probabilities[231:], again.probabilities[231:])

    def test_the_probabilities_of_the_days_inside_the_gap_are_not_read(self):
        days, y, members = self._members(400, 6)
        calendar = _business_days(405)
        base = st.stack(days, calendar, members, y, horizon=3, step=21, ridge=1.0, clip=1e-4,
                        fallback=st.Fallback(126, 5))
        flipped = list(y)
        for k in range(207, 210):  # the last days before a block, whose outcomes are not yet public at h = 3
            flipped[k] = 1 - flipped[k]
        again = st.stack(days, calendar, members, flipped, horizon=3, step=21, ridge=1.0, clip=1e-4,
                         fallback=st.Fallback(126, 5))
        self.assertEqual(base.probabilities[210:231], again.probabilities[210:231])

    def test_members_must_share_the_days(self):
        days, y, members = self._members(100, 7)
        members["good"] = members["good"][:-1]
        with self.assertRaises(ValueError):
            st.stack(days, _business_days(105), members, y, horizon=1, step=21, ridge=1.0, clip=1e-4,
                     fallback=st.Fallback(126, 5))


class DeclarationTests(unittest.TestCase):
    def test_the_declaration_is_the_one_the_code_reads(self):
        declaration = st.load_declaration()
        document = json.loads((REPO / "metadata" / "pressure_stack.json").read_text())
        self.assertEqual(declaration.members, tuple(document["members"]))
        self.assertEqual(declaration.thresholds, (5.0, 10.0))
        self.assertEqual(declaration.step, 21)
        self.assertEqual(declaration.ridge, 1.0)
        self.assertGreaterEqual(len(declaration.members), 3)
        self.assertEqual(set(declaration.members) & {declaration.candidate, declaration.comparison}, set())

    def test_the_candidates_are_declared_to_the_judge(self):
        judge = json.loads((REPO / "metadata" / "pressure_judge.json").read_text())["candidates"]
        declaration = st.load_declaration()
        self.assertIn(declaration.candidate, judge)
        self.assertIn(declaration.comparison, judge)

    def test_a_declaration_with_a_duplicate_member_is_refused(self):
        document = json.loads((REPO / "metadata" / "pressure_stack.json").read_text())
        document["members"] = ["qrf", "qrf", "ngboost_laplace"]
        with self.assertRaises(ValueError):
            st.parse_declaration(document, "x")


if __name__ == "__main__":
    unittest.main()
