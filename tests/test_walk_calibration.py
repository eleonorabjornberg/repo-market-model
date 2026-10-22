"""Walk-forward recalibration of predictive quantiles (#1133; `repo_model.walk_calibration`).

Hand cases for the arithmetic (the conformal rank, the additive correction, the monotone result), and the
guards the module adds. Written before the module; with the module absent the import fails with `ModuleNotFoundError`.

**Recorded mutations (#1133).** Each line is the mutation, the test that fails under it and the exception it raised; with
the line restored the tests pass.

- `calibration_cells`: replacing `if position[d] + lead <= anchor` with `if position[d] + lead <= anchor + 5` makes
  `CellTests.test_a_target_after_the_anchor_is_never_read` and `WalkTests.test_an_outcome_after_the_anchor_changes_nothing`
  fail with `LookAheadError` (raised by `protocol_benchmarks._require_public` inside `calibration_cells`); with the line
  restored they pass. Three more tests of `CellTests` and the class setup of `WalkTests` error the same way.
"""

from __future__ import annotations

import random
import unittest
from datetime import date, timedelta

from repo_model import scoring_protocol as sp
from repo_model import walk_calibration as wc

START = date(2020, 1, 6)
N_ROWS = 40


def business_days(n, start=START):
    out, day = [], start
    while len(out) < n:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


def standard_law():
    """A sorted law with q05 = -1.8 and q95 = +1.8 (width 3.6)."""

    return [4.0 * (level - 0.5) for level in sp.GRID]


class ConformalTests(unittest.TestCase):

    def test_the_rank_is_ceil_level_times_n_plus_one(self):
        scores = [float(i) for i in range(1, 10)]  # n = 9
        self.assertEqual(wc.conformal_quantile(scores, 0.5), 5.0)  # ceil(0.5 * 10) = 5
        self.assertEqual(wc.conformal_quantile(scores, 0.9), 9.0)  # ceil(9.0) = 9
        self.assertEqual(wc.conformal_quantile(scores, 0.99), 9.0)  # 10 clamped to n
        self.assertEqual(wc.conformal_quantile(scores, 0.01), 1.0)  # 1

    def test_the_order_of_the_scores_does_not_matter(self):
        self.assertEqual(wc.conformal_quantile([3.0, 1.0, 2.0], 0.5), 2.0)

    def test_no_scores_is_refused(self):
        with self.assertRaises(ValueError):
            wc.conformal_quantile([], 0.5)


class CorrectionTests(unittest.TestCase):

    def cells(self, outcome, n=20):
        return [wc.Cell(standard_law(), outcome) for _ in range(n)]

    def test_the_width_is_floored(self):
        self.assertAlmostEqual(wc.width(standard_law()), 3.6, places=9)
        self.assertEqual(wc.width([0.0] * len(sp.GRID)), wc.WIDTH_FLOOR)

    def test_a_constant_outcome_collapses_the_law_onto_it(self):
        fit = wc.fit_correction(self.cells(0.0))
        corrected = wc.apply(standard_law(), fit)
        for value in corrected:
            self.assertAlmostEqual(value, 0.0, places=9)

    def test_a_shift_is_in_units_of_the_cells_width(self):
        fit = wc.fit_correction(self.cells(3.6))  # every outcome one width above the median
        corrected = wc.apply(standard_law(), fit)
        for value in corrected:
            self.assertAlmostEqual(value, 3.6, places=9)

    def test_a_crossing_correction_is_sorted(self):
        offsets = tuple(-float(i) for i in range(len(sp.GRID)))
        corrected = wc.apply(standard_law(), wc.Correction(offsets, 1))
        self.assertEqual(corrected, sorted(corrected))


def timeline(n=N_ROWS):
    dates = business_days(n + 8)
    spreads = [float(i % 7) for i in range(len(dates))]
    days = dates[:n]
    position = {d: i for i, d in enumerate(dates)}
    anchors = {d: max(position[d] - 1, 0) for d in days}
    forecasts = {d: {h: standard_law() for h in sp.HORIZONS} for d in days}
    return dates, spreads, days, position, anchors, forecasts


class CellTests(unittest.TestCase):

    def test_a_target_after_the_anchor_is_never_read(self):
        dates, spreads, days, position, anchors, forecasts = timeline()
        before = days[30]
        anchor = anchors[before]  # row 29
        for lead in sp.HORIZONS:
            cells = wc.calibration_cells(days, forecasts, position, spreads, dates,
                                         before=before, anchor=anchor, lead=lead)
            # the decision days d < before whose row + lead is at most 29
            self.assertEqual(len(cells), anchor - lead + 1)
            self.assertEqual([c.outcome for c in cells], [spreads[i + lead] for i in range(anchor - lead + 1)])

    def test_the_window_is_the_trailing_days(self):
        dates, spreads, days, position, anchors, forecasts = timeline()
        old = wc.WINDOW_DAYS
        try:
            wc.WINDOW_DAYS = 10
            cells = wc.calibration_cells(days, forecasts, position, spreads, dates,
                                         before=days[30], anchor=anchors[days[30]], lead=1)
        finally:
            wc.WINDOW_DAYS = old
        # the ten days before day 30 are 20..29; those with row + 1 <= 29 are 20..28
        self.assertEqual([c.outcome for c in cells], [spreads[i + 1] for i in range(20, 29)])


def synthetic(n_days=900, seed=7, noise=3.0, law_sd=1.0):
    rng = random.Random(seed)
    dates = business_days(n_days + 8)
    spreads = [noise * rng.gauss(0.0, 1.0) for _ in dates]
    days = dates[:n_days]
    position = {d: i for i, d in enumerate(dates)}
    anchors = {d: max(position[d] - 1, 0) for d in days}
    # a law centred on zero with sd `law_sd`: too narrow against outcomes of sd `noise`
    z = {0.01: -2.326, 0.025: -1.96, 0.05: -1.645, 0.1: -1.282, 0.15: -1.036, 0.2: -0.842, 0.25: -0.674, 0.3: -0.524,
         0.35: -0.385, 0.4: -0.253, 0.45: -0.126, 0.5: 0.0, 0.55: 0.126, 0.6: 0.253, 0.65: 0.385, 0.7: 0.524,
         0.75: 0.674, 0.8: 0.842, 0.85: 1.036, 0.9: 1.282, 0.95: 1.645, 0.975: 1.96, 0.99: 2.326}
    law = [law_sd * z[level] for level in sp.GRID]
    forecasts = {d: {h: list(law) for h in sp.HORIZONS} for d in days}
    return dates, spreads, days, position, anchors, forecasts


class WalkTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.args = synthetic()
        dates, spreads, days, position, anchors, forecasts = cls.args
        cls.laws, cls.refits, cls.uncalibrated = wc.walk(days, forecasts, anchors, position, spreads, dates)

    def test_days_wait_for_enough_past_cells(self):
        first = min(self.laws)
        days = self.args[2]
        self.assertEqual(self.uncalibrated, days[: days.index(first)])
        # lead 5 needs MIN_CELLS cells whose target is public: the anchor is one row before the day
        self.assertEqual(days.index(first), wc.MIN_CELLS + 5)

    def test_the_refits_are_every_refit_every_days(self):
        days = self.args[2]
        positions = [days.index(d) for d in sorted(self.refits)]
        self.assertTrue(all(b - a == wc.REFIT_EVERY for a, b in zip(positions, positions[1:])))

    def test_every_law_is_sorted_with_23_quantiles(self):
        for leads in self.laws.values():
            for q in leads.values():
                self.assertEqual(len(q), len(sp.GRID))
                self.assertEqual(q, sorted(q))

    def test_a_too_narrow_law_is_widened_to_its_nominal_coverage(self):
        dates, spreads, days, position, anchors, forecasts = self.args
        inside = total = base_inside = 0
        for d, leads in self.laws.items():
            for h, q in leads.items():
                y = spreads[position[d] + h]
                inside += q[wc.LOW] <= y <= q[wc.HIGH]
                base_inside += forecasts[d][h][wc.LOW] <= y <= forecasts[d][h][wc.HIGH]
                total += 1
        self.assertLess(base_inside / total, 0.6)
        self.assertGreater(inside / total, 0.86)
        self.assertLess(inside / total, 0.94)

    def test_an_outcome_after_the_anchor_changes_nothing(self):
        dates, spreads, days, position, anchors, forecasts = self.args
        day = sorted(self.refits)[3]
        row = position[day]
        changed = list(spreads)
        for j in range(row, len(changed)):  # the decision day's own row and every later one
            changed[j] += 1000.0
        # the forecasts of the days before the decision day are those of the base, which read no later row either
        laws, refits, _ = wc.walk(days[: days.index(day) + 1], forecasts, anchors, position, changed, dates)
        self.assertEqual(laws[day], self.laws[day])
        self.assertEqual(refits[day].pooled[1].offsets, self.refits[day].pooled[1].offsets)

    def test_refit_every_must_be_positive(self):
        dates, spreads, days, position, anchors, forecasts = self.args
        with self.assertRaises(ValueError):
            wc.walk(days, forecasts, anchors, position, spreads, dates, refit_every=0)


if __name__ == "__main__":
    unittest.main()
