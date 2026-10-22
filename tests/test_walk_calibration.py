"""Walk-forward recalibration of predictive quantiles (#1133; `repo_model.walk_calibration`).

Hand cases for the arithmetic (the conformal rank, the additive and the tail correction, the monotone result), and the
guards the module adds. Written before the module; with the module absent the import fails with `ModuleNotFoundError`.

**Recorded mutations (#1133).** Each line is the mutation, the test that fails under it and the exception it raised; with
the line restored the tests pass.

- `calibration_cells`: replacing `if position[d] + lead <= anchor` with `if position[d] + lead <= anchor + 5` makes
  `CellTests.test_a_target_after_the_anchor_is_never_read` and `WalkTests.test_an_outcome_after_the_anchor_changes_nothing`
  fail with `LookAheadError` (raised by `protocol_benchmarks._require_public` inside `calibration_cells`); with the line
  restored they pass. Three more tests of `CellTests` and the class setup of `WalkTests` error the same way.
- `floor_flag`: replacing `gaps[max(0, r - FLAG_WINDOW + 1): r + 1]` with `gaps[max(0, r - FLAG_WINDOW + 1): r + 6]` makes
  `FlagTests.test_the_flag_reads_no_later_row` fail with `AssertionError` (`None != True : row 34`: the flag of the cut panel
  differs from the whole panel's), and two other `FlagTests` fail with `AssertionError` too.
- `check_flag_as_of`: replacing `if rebuilt != flags[row]:` with `if False:` makes
  `FlagTests.test_a_flag_that_reads_a_later_row_is_refused` fail with `AssertionError` (`LookAheadError not raised`).
"""

from __future__ import annotations

import random
import unittest
from datetime import date, timedelta

from repo_model import scoring_protocol as sp
from repo_model import walk_calibration as wc
from repo_model.data import DailyObservation
from repo_model.splits import LookAheadError

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
        return [wc.Cell(standard_law(), outcome, None) for _ in range(n)]

    def test_the_width_is_floored(self):
        self.assertAlmostEqual(wc.width(standard_law()), 3.6, places=9)
        self.assertEqual(wc.width([0.0] * len(sp.GRID)), wc.WIDTH_FLOOR)

    def test_a_constant_outcome_collapses_the_law_onto_it(self):
        fit = wc.fit_correction(self.cells(0.0))
        corrected = wc.apply(standard_law(), fit, tail=False)
        for value in corrected:
            self.assertAlmostEqual(value, 0.0, places=9)

    def test_a_shift_is_in_units_of_the_cells_width(self):
        fit = wc.fit_correction(self.cells(3.6))  # every outcome one width above the median
        corrected = wc.apply(standard_law(), fit, tail=False)
        for value in corrected:
            self.assertAlmostEqual(value, 3.6, places=9)

    def test_the_tail_multiplier_can_exceed_one(self):
        fit = wc.fit_correction(self.cells(10.0))
        i = sp.GRID.index(0.9)
        self.assertAlmostEqual(fit.multipliers[i], 10.0 / 1.6, places=9)  # q90 sits 1.6 above the median of 0
        self.assertGreater(fit.multipliers[i], 1.0)
        corrected = wc.apply(standard_law(), fit, tail=True)
        self.assertAlmostEqual(corrected[i], 10.0, places=9)

    def test_the_tail_arm_leaves_the_body_to_the_additive_correction(self):
        fit = wc.fit_correction(self.cells(10.0))
        additive = wc.apply(standard_law(), fit, tail=False)
        tail = wc.apply(standard_law(), fit, tail=True)
        for i, level in enumerate(sp.GRID):
            if level < wc.TAIL_FROM:
                self.assertEqual(additive[i], tail[i])

    def test_a_crossing_correction_is_sorted(self):
        offsets = tuple(-float(i) for i in range(len(sp.GRID)))
        corrected = wc.apply(standard_law(), wc.Correction(offsets, {}, 1), tail=False)
        self.assertEqual(corrected, sorted(corrected))

    def test_the_multiplier_is_not_negative(self):
        fit = wc.fit_correction(self.cells(-50.0))
        self.assertTrue(all(m >= 0.0 for m in fit.multipliers.values()))

    def test_an_unknown_arm_is_refused(self):
        with self.assertRaises(ValueError):
            wc.correct({h: standard_law() for h in sp.HORIZONS}, None, None, "nonsense")


def timeline(n=N_ROWS):
    dates = business_days(n + 8)
    spreads = [float(i % 7) for i in range(len(dates))]
    days = dates[:n]
    position = {d: i for i, d in enumerate(dates)}
    anchors = {d: max(position[d] - 1, 0) for d in days}
    flags = [None] * len(dates)
    forecasts = {d: {h: standard_law() for h in sp.HORIZONS} for d in days}
    return dates, spreads, days, position, anchors, flags, forecasts


class CellTests(unittest.TestCase):

    def test_a_target_after_the_anchor_is_never_read(self):
        dates, spreads, days, position, anchors, flags, forecasts = timeline()
        before = days[30]
        anchor = anchors[before]  # row 29
        for lead in sp.HORIZONS:
            cells = wc.calibration_cells(days, forecasts, anchors, position, spreads, flags, dates,
                                         before=before, anchor=anchor, lead=lead)
            # the decision days d < before whose row + lead is at most 29
            self.assertEqual(len(cells), anchor - lead + 1)
            self.assertEqual([c.outcome for c in cells], [spreads[i + lead] for i in range(anchor - lead + 1)])

    def test_the_window_is_the_trailing_days(self):
        dates, spreads, days, position, anchors, flags, forecasts = timeline()
        old = wc.WINDOW_DAYS
        try:
            wc.WINDOW_DAYS = 10
            cells = wc.calibration_cells(days, forecasts, anchors, position, spreads, flags, dates,
                                         before=days[30], anchor=anchors[days[30]], lead=1)
        finally:
            wc.WINDOW_DAYS = old
        # the ten days before day 30 are 20..29; those with row + 1 <= 29 are 20..28
        self.assertEqual([c.outcome for c in cells], [spreads[i + 1] for i in range(20, 29)])

    def test_the_state_is_the_flag_at_the_cells_own_anchor(self):
        dates, spreads, days, position, anchors, flags, forecasts = timeline()
        flags = [i % 2 == 0 for i in range(len(dates))]
        cells = wc.calibration_cells(days, forecasts, anchors, position, spreads, flags, dates,
                                     before=days[30], anchor=anchors[days[30]], lead=1)
        self.assertEqual([c.state for c in cells], [flags[max(i - 1, 0)] for i in range(0, 29)])


class FlagTests(unittest.TestCase):

    def panel(self, gaps, rate=1.0):
        """Rows whose SOFR less a constant 1.00% ON RRP rate is `gaps` bp."""

        dates = business_days(len(gaps))
        rows = [DailyObservation(d, {"sofr": rate + g / 100.0, "iorb": rate + 0.1}) for d, g in zip(dates, gaps)]
        entry = {"kind": "on_rrp", "action": "change", "announced_date": "2019-01-01", "effective_date": "2019-01-02",
                 "details": {"offering_rate_percent": rate}}
        return rows, [entry]

    def test_a_rate_applies_from_its_effective_and_announced_dates(self):
        entries = [
            {"kind": "on_rrp", "announced_date": "2020-01-10", "effective_date": "2020-01-13", "details": {"offering_rate_percent": 1.0}},
            {"kind": "on_rrp", "announced_date": "2020-02-03", "effective_date": "2020-02-05", "details": {"offering_rate_percent": 0.5}},
            {"kind": "iorb_rate", "announced_date": "2020-01-01", "effective_date": "2020-01-02", "details": {"rate_percent": 9.0}},
        ]
        days = [date(2020, 1, 9), date(2020, 1, 13), date(2020, 2, 4), date(2020, 2, 5)]
        self.assertEqual(wc.rrp_rates(entries, days), [None, 1.0, 1.0, 0.5])

    def test_the_flag_is_off_with_too_few_rows_and_on_at_the_floor(self):
        rows, entries = self.panel([0.0] * 80)
        flags = wc.floor_flag(rows, entries)
        self.assertTrue(all(f is None for f in flags[: wc.FLAG_MIN_ROWS - 1]))
        self.assertTrue(all(f is True for f in flags[wc.FLAG_MIN_ROWS - 1:]))

    def test_the_flag_follows_the_trailing_median(self):
        rows, entries = self.panel([0.0] * 60 + [8.0] * 60)
        flags = wc.floor_flag(rows, entries)
        self.assertTrue(flags[59])
        # the median of 60 rows passes 1 bp once 30 of them are 8 bp: rows 60..89
        self.assertEqual(flags.index(False), 89)

    def test_the_flag_reads_no_later_row(self):
        rows, entries = self.panel([0.0] * 50 + [9.0] * 50)
        full = wc.floor_flag(rows, entries)
        for r in range(len(rows)):
            self.assertEqual(wc.floor_flag(rows[: r + 1], entries)[r], full[r], f"row {r}")

    def test_the_flag_agrees_with_a_rebuild_from_the_cut_panel(self):
        rows, entries = self.panel([0.0] * 50 + [9.0] * 50)
        full = wc.floor_flag(rows, entries)
        for r in (10, 45, 60, 99):
            wc.check_flag_as_of(rows, entries, full, r)

    def test_a_flag_that_reads_a_later_row_is_refused(self):
        rows, entries = self.panel([9.0] * 49 + [0.0] * 51)
        honest = wc.floor_flag(rows, entries)
        leaky = list(honest)
        leaky[48] = True  # a flag that saw the floor days to come
        self.assertFalse(honest[48])
        with self.assertRaises(LookAheadError):
            wc.check_flag_as_of(rows, entries, leaky, 48)


def synthetic(n_days=900, seed=7, noise=3.0, law_sd=1.0):
    rng = random.Random(seed)
    dates = business_days(n_days + 8)
    spreads = [noise * rng.gauss(0.0, 1.0) for _ in dates]
    days = dates[:n_days]
    position = {d: i for i, d in enumerate(dates)}
    anchors = {d: max(position[d] - 1, 0) for d in days}
    flags = [None] * len(dates)
    # a law centred on zero with sd `law_sd`: too narrow against outcomes of sd `noise`
    z = {0.01: -2.326, 0.025: -1.96, 0.05: -1.645, 0.1: -1.282, 0.15: -1.036, 0.2: -0.842, 0.25: -0.674, 0.3: -0.524,
         0.35: -0.385, 0.4: -0.253, 0.45: -0.126, 0.5: 0.0, 0.55: 0.126, 0.6: 0.253, 0.65: 0.385, 0.7: 0.524,
         0.75: 0.674, 0.8: 0.842, 0.85: 1.036, 0.9: 1.282, 0.95: 1.645, 0.975: 1.96, 0.99: 2.326}
    law = [law_sd * z[level] for level in sp.GRID]
    forecasts = {d: {h: list(law) for h in sp.HORIZONS} for d in days}
    return dates, spreads, days, position, anchors, flags, forecasts


class WalkTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.args = synthetic()
        dates, spreads, days, position, anchors, flags, forecasts = cls.args
        cls.laws, cls.refits, cls.uncalibrated = wc.walk(days, forecasts, anchors, position, spreads, flags, dates)

    def test_days_wait_for_enough_past_cells(self):
        first = min(self.laws["pooled"])
        days = self.args[2]
        self.assertEqual(self.uncalibrated, days[: days.index(first)])
        # lead 5 needs MIN_CELLS cells whose target is public: the anchor is one row before the day
        self.assertEqual(days.index(first), wc.MIN_CELLS + 5)

    def test_the_refits_are_every_refit_every_days(self):
        days = self.args[2]
        positions = [days.index(d) for d in sorted(self.refits)]
        self.assertTrue(all(b - a == wc.REFIT_EVERY for a, b in zip(positions, positions[1:])))

    def test_every_law_is_sorted_with_23_quantiles(self):
        for arm in wc.ARMS:
            for leads in self.laws[arm].values():
                for q in leads.values():
                    self.assertEqual(len(q), len(sp.GRID))
                    self.assertEqual(q, sorted(q))

    def test_a_too_narrow_law_is_widened_to_its_nominal_coverage(self):
        dates, spreads, days, position, anchors, flags, forecasts = self.args
        for arm in ("pooled", "state", "state_tail"):
            inside = total = 0
            base_inside = 0
            for d, leads in self.laws[arm].items():
                for h, q in leads.items():
                    y = spreads[position[d] + h]
                    inside += q[wc.LOW] <= y <= q[wc.HIGH]
                    base_inside += forecasts[d][h][wc.LOW] <= y <= forecasts[d][h][wc.HIGH]
                    total += 1
            self.assertLess(base_inside / total, 0.6, arm)
            self.assertGreater(inside / total, 0.86, arm)
            self.assertLess(inside / total, 0.94, arm)

    def test_an_outcome_after_the_anchor_changes_nothing(self):
        dates, spreads, days, position, anchors, flags, forecasts = self.args
        day = sorted(self.refits)[3]
        row = position[day]
        changed = list(spreads)
        for j in range(row, len(changed)):  # the decision day's own row and every later one
            changed[j] += 1000.0
        # the forecasts of the days before the decision day are those of the base, which read no later row either
        laws, refits, _ = wc.walk(days[: days.index(day) + 1], forecasts, anchors, position, changed, flags, dates)
        for arm in wc.ARMS:
            self.assertEqual(laws[arm][day], self.laws[arm][day], arm)
        self.assertEqual(refits[day].pooled[1].offsets, self.refits[day].pooled[1].offsets)

    def test_the_state_arm_uses_the_state_it_is_in(self):
        dates, spreads, days, position, anchors, flags, forecasts = synthetic()
        # state True: outcomes of sd 3; state False: outcomes of sd 0.5 (the law's sd is 1)
        rng = random.Random(3)
        flags = [(i // 100) % 2 == 0 for i in range(len(dates))]  # blocks of 100 rows
        spreads = [(3.0 if flags[i] else 0.5) * rng.gauss(0.0, 1.0) for i in range(len(dates))]
        laws, _, _ = wc.walk(days, forecasts, anchors, position, spreads, flags, dates)

        def mean_width(arm, state):
            widths = [laws[arm][d][1][wc.HIGH] - laws[arm][d][1][wc.LOW] for d in laws[arm] if flags[anchors[d]] is state]
            return sum(widths) / len(widths)

        self.assertGreater(mean_width("state", True), 2.0 * mean_width("state", False))
        # the pooled arm cannot tell the states apart: its widths differ by far less
        self.assertLess(mean_width("pooled", True) / mean_width("pooled", False), 1.5)

    def test_a_state_with_few_cells_takes_the_pooled_correction(self):
        dates, spreads, days, position, anchors, flags, forecasts = synthetic()
        flags = [False] * len(dates)  # state True never occurs
        laws, _, _ = wc.walk(days, forecasts, anchors, position, spreads, flags, dates)
        self.assertEqual(laws["state"], laws["pooled"])

    def test_refit_every_must_be_positive(self):
        dates, spreads, days, position, anchors, flags, forecasts = self.args
        with self.assertRaises(ValueError):
            wc.walk(days, forecasts, anchors, position, spreads, flags, dates, refit_every=0)


if __name__ == "__main__":
    unittest.main()
