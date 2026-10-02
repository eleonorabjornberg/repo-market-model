"""The calibration re-diagnosis's two challengers to CV+ (#116).

`repo_model.recalibration` is standard library only, so this module runs in the
core job. The CV+ pieces both challengers start from are `ml`'s and are tested
in `tests/test_ml.py::RecalibrationPartsTests`.

* `ObservabilityGuardTests`: the online method updates only on labels
  observable at the decision instant of the band it is about to issue.
* `ScorecasterCalendarTests`: the scorecaster's settlement indicator is read
  only when its declared availability precedes the decision instant.
* `ConformalPidTests`: what conformal PID does with what it may read.
* `GroupConditionalEdgesTests`: Mondrian CV+ over calendar type x regime, and
  its declared fallback.
* `PidGridTests`: the conformal PID constants' search grid, declared before
  any scoring (#125), and #122's constants as one of its points.
"""

from __future__ import annotations

import math
import random
import unittest
from datetime import date, time, timedelta

from repo_model import ml, recalibration
from repo_model.asof import InformationRule
from repo_model.data import DailyObservation
from repo_model.evaluation_splits import load_split_declaration
from repo_model.ingest import load_source_registry
from repo_model.splits import LookAheadError

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEVELS = (0.05, 0.25, 0.5, 0.75, 0.95)


def online_days(count, *, start=date(2021, 1, 4), lag=2, width=1.0, calendar=None):
    """`count` business days, each anchored `lag` rows before itself.

    The base vector is a fixed band `[-width, +width]` about zero, so every
    score is `|y| - width`. `calendar(position)` gives the scorecaster
    indicators, all zero by default.
    """

    dates = []
    when = start
    while len(dates) < count + lag:
        if when.weekday() < 5:
            dates.append(when)
        when += timedelta(days=1)
    vector = (-width, -width / 2.0, 0.0, width / 2.0, width)
    return [
        recalibration.OnlineDay(
            scored_date=dates[position + lag],
            anchor=dates[position],
            vector=vector,
            calendar=(0, 0, 0, 0) if calendar is None else calendar(position),
        )
        for position in range(count)
    ]


def gaussian_actuals(count, sd, seed=20261002):
    rng = random.Random(seed)
    return [rng.gauss(0.0, sd) for _ in range(count)]


class ObservabilityGuardTests(unittest.TestCase):
    """The online method's label-observability guard (#116, item 5).

    A band issued at a decision instant may be moved only by labels observable
    at that instant: a scored day's label is observable when the day is on or
    before the decision's anchor (`ScoredFold.feature_date`, the latest row
    whose target was observable). `PidState.observe` refuses any other with
    `LookAheadError`, and `conformal_pid` reveals a label only when it is.

    Red first: written before `repo_model.recalibration` existed; the module
    failed to import (`ImportError`).

    Mutation record. In a disposable copy of the tree under /tmp (checked to
    resolve to the copy's `src/`), `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`,
    CPython 3.11, this class run alone; unmutated control green; the mutation
    confirmed applied by `diff` against the tree:

    1. `PidState.observe`'s guard, `if day.scored_date > decision.anchor:`,
       mutated to `if day.scored_date > decision.scored_date:` (a label is
       taken as observable on any day before the one being forecast). Killed:
       `test_a_label_not_observable_at_the_decision_is_refused` failed with
       `AssertionError: LookAheadError not raised`.
    """

    def test_a_label_not_observable_at_the_decision_is_refused(self):
        days = online_days(10)
        state = recalibration.PidState(LEVELS)
        decision = days[5]
        # Day 4 is scored on the day before day 5's scored day: one row after
        # day 5's anchor, so its label was not public at day 5's decision.
        unobservable = days[4]
        self.assertGreater(unobservable.scored_date, decision.anchor)
        band = state.band(unobservable)
        with self.assertRaises(LookAheadError) as caught:
            state.observe(unobservable, band, 0.0, decision)
        self.assertIn(str(unobservable.scored_date), str(caught.exception))
        # The latest observable one is accepted.
        observable = days[3]
        self.assertEqual(observable.scored_date, decision.anchor)
        state.observe(observable, state.band(observable), 0.0, decision)

    def test_no_band_moves_with_a_label_its_decision_could_not_see(self):
        count = 120
        days = online_days(count)
        actuals = gaussian_actuals(count, 2.0)
        bands = recalibration.conformal_pid(days, actuals, LEVELS)
        for target in (30, 60, 119):
            for changed in range(target - 1, count):
                if days[changed].scored_date <= days[target].anchor:
                    continue
                moved = list(actuals)
                moved[changed] += 50.0
                again = recalibration.conformal_pid(days, moved, LEVELS)
                self.assertEqual(
                    again[target], bands[target],
                    msg=f"day {target}'s band moved with day {changed}'s label",
                )

    def test_an_observable_label_does_move_the_band(self):
        count = 60
        days = online_days(count)
        actuals = gaussian_actuals(count, 2.0)
        bands = recalibration.conformal_pid(days, actuals, LEVELS)
        target = 40
        changed = target - 2
        self.assertEqual(days[changed].scored_date, days[target].anchor)
        moved = list(actuals)
        moved[changed] += 50.0
        again = recalibration.conformal_pid(days, moved, LEVELS)
        self.assertNotEqual(again[target], bands[target])

    def test_out_of_order_or_unanchored_days_are_refused(self):
        days = online_days(5)
        with self.assertRaises(ValueError):
            recalibration.conformal_pid([days[1], days[0]], [0.0, 0.0], LEVELS)
        bad = days[0]._replace(anchor=days[0].scored_date)
        with self.assertRaises(LookAheadError):
            recalibration.conformal_pid([bad], [0.0], LEVELS)
        with self.assertRaises(ValueError):
            recalibration.conformal_pid(days, [0.0], LEVELS)


class ConformalPidTests(unittest.TestCase):
    """Conformal PID (Angelopoulos, Barber and Bates, 2023) on synthetic streams."""

    def coverage(self, bands, actuals):
        return sum(b.vector[0] <= y <= b.vector[-1] for b, y in zip(bands, actuals)) / len(actuals)

    def test_long_run_coverage_tracks_the_nominal_band_from_a_wrong_base(self):
        count = 3000
        for width, sd in ((0.5, 3.0), (8.0, 3.0)):
            with self.subTest(width=width, sd=sd):
                days = online_days(count, width=width)
                actuals = gaussian_actuals(count, sd)
                bands = recalibration.conformal_pid(days, actuals, LEVELS)
                base = sum(-width <= y <= width for y in actuals) / count
                self.assertGreater(abs(base - 0.9), 0.05, "the base must be wrong")
                self.assertAlmostEqual(self.coverage(bands, actuals), 0.9, delta=0.02)

    def test_the_scorecaster_lifts_the_band_on_calendar_days(self):
        """A mean scorecaster: it lifts flagged days' cover, without a promise per day type."""

        count = 1500
        rng = random.Random(7)
        actuals = [
            rng.gauss(0.0, 6.0 if position % 20 == 0 else 1.0) for position in range(count)
        ]
        late = [i for i in range(500, count) if i % 20 == 0]
        runs = {}
        for name, calendar in (
            ("with", lambda position: (1 if position % 20 == 0 else 0, 0, 0, 0)),
            ("without", lambda position: (0, 0, 0, 0)),
        ):
            days = online_days(count, calendar=calendar)
            runs[name] = recalibration.conformal_pid(days, actuals, LEVELS)
        bands = runs["with"]
        on = [bands[i].scorecast for i in late]
        off = [bands[i].scorecast for i in range(500, count) if i % 20 != 0]
        self.assertGreater(sum(on) / len(on), sum(off) / len(off) + 3.0)
        cover = {
            name: sum(b[i].vector[0] <= actuals[i] <= b[i].vector[-1] for i in late) / len(late)
            for name, b in runs.items()
        }
        self.assertGreater(cover["with"], cover["without"] + 0.3)

    def test_no_scorecast_before_the_declared_minimum(self):
        days = online_days(40, calendar=lambda position: (position % 2, 0, 0, 0))
        actuals = gaussian_actuals(40, 2.0)
        bands = recalibration.conformal_pid(days, actuals, LEVELS)
        for band in bands:
            if band.observed < recalibration.SCORECASTER_MINIMUM:
                self.assertEqual(band.scorecast, 0.0)
        self.assertEqual(bands[0].observed, 0)
        self.assertEqual(bands[0].vector, days[0].vector)

    def test_the_band_keeps_the_interior_and_stays_ordered(self):
        days = online_days(300, width=8.0)
        actuals = gaussian_actuals(300, 0.5)
        bands = recalibration.conformal_pid(days, actuals, LEVELS)
        for day, band in zip(days, bands):
            self.assertEqual(band.vector[1:-1], day.vector[1:-1])
            self.assertEqual(list(band.vector), sorted(band.vector))


class PidGridTests(unittest.TestCase):
    """The search grid for conformal PID's constants, declared in advance (#125).

    The grid is pinned here value by value: widening it after scoring would
    show up as a change to this test.
    """

    def test_the_declared_constants_are_122s(self):
        declared = recalibration.DECLARED_PID
        self.assertEqual(declared.step, recalibration.PID_STEP)
        self.assertEqual(declared.integrator_gain, recalibration.PID_INTEGRATOR_GAIN)
        self.assertEqual(declared.saturation, recalibration.PID_SATURATION)
        self.assertEqual(declared.scorecaster_minimum, recalibration.SCORECASTER_MINIMUM)
        self.assertEqual(declared, recalibration.PidConstants(0.05, 0.1, 1.0, 20))

    def test_the_grid_is_the_declared_one_and_holds_122s_point(self):
        self.assertEqual(recalibration.PID_GRID_STEPS, (0.01, 0.05, 0.2))
        self.assertEqual(recalibration.PID_GRID_INTEGRATOR_GAINS, (0.0, 0.1, 0.5))
        self.assertEqual(recalibration.PID_GRID_SATURATIONS, (1.0, 5.0))
        self.assertEqual(recalibration.PID_GRID_SCORECASTER_MINIMUMS, (None, 20, 60))
        grid = recalibration.PID_GRID
        self.assertIn(recalibration.DECLARED_PID, grid)
        self.assertEqual(len(set(grid)), len(grid))
        # A zero integrator gain makes the saturation moot: one point, not two.
        for point in grid:
            if point.integrator_gain == 0.0:
                self.assertEqual(point.saturation, recalibration.PID_GRID_SATURATIONS[0])
        self.assertEqual(len(grid), 3 * (1 + 2 * 2) * 3)

    def test_the_default_run_is_the_declared_point(self):
        days = online_days(400, calendar=lambda position: (int(position % 21 == 0), 0, 0, 0))
        actuals = gaussian_actuals(400, 2.0)
        self.assertEqual(
            recalibration.conformal_pid(days, actuals, LEVELS),
            recalibration.conformal_pid(
                days, actuals, LEVELS, constants=recalibration.DECLARED_PID
            ),
        )

    def test_each_part_can_be_switched_off(self):
        days = online_days(300, calendar=lambda position: (int(position % 7 == 0), 0, 0, 0))
        actuals = gaussian_actuals(300, 2.0)
        bare = recalibration.PidConstants(0.05, 0.0, 1.0, None)
        bands = recalibration.conformal_pid(days, actuals, LEVELS, constants=bare)
        state = recalibration.PidState(LEVELS, bare)
        self.assertEqual(state.constants, bare)
        for band in bands:
            self.assertEqual(band.scorecast, 0.0)
            self.assertFalse(band.saturated)
        # P alone: each observed label moves q by the step times the range.
        self.assertNotEqual(bands[-1].quantile, 0.0)

    def test_the_constants_change_the_bands(self):
        days = online_days(300)
        actuals = gaussian_actuals(300, 3.0)
        slow, fast = (
            recalibration.conformal_pid(
                days, actuals, LEVELS, constants=recalibration.PidConstants(step, 0.1, 1.0, 20)
            )
            for step in (0.01, 0.2)
        )
        self.assertNotEqual(slow[50].quantile, fast[50].quantile)


class ScorecasterCalendarTests(unittest.TestCase):
    """The scorecaster's calendar, read for the scored day at its decision instant.

    Month end, quarter end and tax date are calendar columns, always known. The
    coupon settlement indicator is `treasury_settlement_coupons > 0` on the
    scored day, a scheduled field: it is read only when the registry's declared
    availability for the scored row is at or before the decision instant, and
    refused with `LookAheadError` otherwise.

    Red first: written before `repo_model.recalibration` existed (`ImportError`).

    Mutation record. Same protocol as `ObservabilityGuardTests`:

    1. In `scorecaster_calendar`, the guard `if available > decision:` mutated
       to `if available > decision.replace(hour=23):` (a settlement announced
       any time on the decision day taken as public at the decision). Killed: `test_a_settlement_not_yet_announced_is_refused`
       failed with `AssertionError: LookAheadError not raised`.
    """

    def setUp(self):
        self.registry = load_source_registry(ROOT / "metadata" / "sources.json")
        self.splits = load_split_declaration(ROOT / "metadata" / "evaluation_splits.json")
        self.rows = []
        when = date(2024, 3, 25)
        while len(self.rows) < 8:
            if when.weekday() < 5:
                last = (date(when.year + (when.month == 12), when.month % 12 + 1, 1) - timedelta(days=1))
                self.rows.append(
                    DailyObservation(
                        when,
                        {
                            "sofr": 5.31, "iorb": 5.40,
                            "quarter_end": 1.0 if when == date(2024, 3, 29) else 0.0,
                            "tax_date": 1.0 if when == date(2024, 4, 1) else 0.0,
                            "days_to_month_end": float((last - when).days),
                            "treasury_settlement_coupons": 60.0 if when == date(2024, 4, 1) else 0.0,
                        },
                    )
                )
            when += timedelta(days=1)

    def rule(self, decision_time):
        return InformationRule(self.registry, ("spread_bps",), decision_time=decision_time)

    def test_the_indicators(self):
        rule = self.rule(time(16, 0))
        dates = [row.date for row in self.rows]
        read = {
            row.date: recalibration.scorecaster_calendar(self.rows, rule, index, self.splits)
            for index, row in enumerate(self.rows) if index > 0
        }
        self.assertEqual(recalibration.SCORECASTER_INDICATORS,
                         ("month_end", "quarter_end", "tax_date", "coupon_settlement"))
        self.assertEqual(read[date(2024, 3, 29)], (1, 1, 0, 0))
        self.assertEqual(read[date(2024, 4, 1)], (0, 0, 1, 1))
        self.assertEqual(read[date(2024, 4, 2)], (0, 0, 0, 0))
        self.assertEqual(read[date(2024, 3, 28)], (0, 0, 0, 0))
        self.assertEqual(len(dates), 8)

    def test_a_settlement_not_yet_announced_is_refused(self):
        # Announced at 15:00 the panel day before: a 14:00 decision is earlier.
        rule = self.rule(time(14, 0))
        index = [row.date for row in self.rows].index(date(2024, 4, 1))
        with self.assertRaises(LookAheadError) as caught:
            recalibration.scorecaster_calendar(self.rows, rule, index, self.splits)
        self.assertIn("2024-04-01", str(caught.exception))
        # At 15:00 it is public, exactly.
        recalibration.scorecaster_calendar(self.rows, self.rule(time(15, 0)), index, self.splits)

    def test_a_settlement_hole_is_refused_not_read_as_zero(self):
        rule = self.rule(time(16, 0))
        values = dict(self.rows[3].values)
        values["treasury_settlement_coupons"] = None
        rows = list(self.rows)
        rows[3] = DailyObservation(rows[3].date, values)
        with self.assertRaises(ValueError):
            recalibration.scorecaster_calendar(rows, rule, 3, self.splits)


class GroupConditionalEdgesTests(unittest.TestCase):
    """Mondrian CV+ (Vovk et al.) over calendar type x regime, with its fallback."""

    def terms(self, groups, seed=3):
        rng = random.Random(seed)
        lows = [rng.uniform(-10.0, 0.0) for _ in groups]
        highs = [rng.uniform(0.0, 10.0) for _ in groups]
        return lows, highs

    def test_a_full_cell_reads_only_its_own_terms(self):
        groups = [("month_end", "2024")] * 30 + [("ordinary", "2024")] * 200
        lows, highs = self.terms(groups)
        lower, upper, level = recalibration.group_conditional_edges(
            lows, highs, groups, ("month_end", "2024"), LEVELS
        )
        self.assertEqual(level, "cell")
        self.assertEqual(
            (lower, upper), ml._cross_conformal_edges(lows[:30], highs[:30], LEVELS)
        )

    def test_a_thin_cell_falls_back_to_its_calendar_type_then_to_the_pool(self):
        minimum = ml._minimum_calibration_rows(LEVELS)
        groups = (
            [("month_end", "2020")] * (minimum - 1)
            + [("month_end", "2024")] * 12
            + [("ordinary", "2024")] * 100
        )
        lows, highs = self.terms(groups)
        lower, upper, level = recalibration.group_conditional_edges(
            lows, highs, groups, ("month_end", "2020"), LEVELS
        )
        self.assertEqual(level, "day_type")
        count = minimum - 1 + 12
        self.assertEqual(
            (lower, upper), ml._cross_conformal_edges(lows[:count], highs[:count], LEVELS)
        )
        lower, upper, level = recalibration.group_conditional_edges(
            lows, highs, groups, ("quarter_end", "2020"), LEVELS
        )
        self.assertEqual(level, "pooled")
        self.assertEqual((lower, upper), ml._cross_conformal_edges(lows, highs, LEVELS))

    def test_the_cell_minimum_is_the_least_at_which_both_ranks_exist(self):
        minimum = ml._minimum_calibration_rows(LEVELS)
        self.assertEqual(minimum, 9)
        groups = [("tax_date", "2021-23")] * minimum + [("ordinary", "2021-23")] * 50
        lows, highs = self.terms(groups)
        *_, level = recalibration.group_conditional_edges(
            lows, highs, groups, ("tax_date", "2021-23"), LEVELS
        )
        self.assertEqual(level, "cell")

    def test_misaligned_terms_are_refused(self):
        with self.assertRaises(ValueError):
            recalibration.group_conditional_edges([0.0], [1.0, 2.0], [("a", "b")], ("a", "b"), LEVELS)


if __name__ == "__main__":
    unittest.main()
