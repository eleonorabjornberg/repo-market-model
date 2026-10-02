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
* `NestedSelectionGuardTests`: the constants used for a refit block are chosen
  only from days whose labels were observable at that block's refit (#125).
* `FoldPidTests`: conformal PID inside a fold loop (#124), at #122's
  constants, as Eleonora's ruling on #123 first adopted it.
* `NestedFoldPidTests`: conformal PID with nested walk-forward selection of
  its constants inside a fold loop (#124), the published funding
  declaration's calibration since her rulings on #136 and #134.
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
from repo_model.metrics import crps_from_quantiles
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


def selection_stream(count, candidates, *, lag=1, start=date(2021, 1, 4), seed=125):
    """`count` scored business days, each anchored `lag` rows back, with random losses."""

    dates = []
    when = start
    while len(dates) < count + lag:
        if when.weekday() < 5:
            dates.append(when)
        when += timedelta(days=1)
    rng = random.Random(seed)
    losses = [tuple(rng.random() for _ in range(candidates)) for _ in range(count)]
    return dates[lag:], dates[: count], losses


class NestedSelectionGuardTests(unittest.TestCase):
    """Nested walk-forward selection reads only past scored days (#125, item 5).

    At each refit the constants for the coming block are chosen by pooled loss
    over the days scored before it, and only those whose label was observable
    at the refit's decision instant: scored on or before the block's anchor
    (the first row's `ScoredFold.feature_date`). `select_constants` refuses a
    history holding any later day with `LookAheadError`, and
    `nested_selection` hands it only days that qualify.

    Red first: written before `select_constants` and `nested_selection`
    existed; every test failed with `AttributeError`.

    Mutation record. In a disposable copy of the tree under /tmp (checked to
    resolve to the copy's `src/`), `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`,
    CPython 3.11, this class run alone; unmutated control green; the mutation
    applied, as confirmed by `diff`:
    `if scored_date > anchor:` in `select_constants` replaced by
    `if scored_date > anchor + timedelta(days=7):` (with `timedelta` added to
    the module's `datetime` import), a guard that lets through a week of
    labels not yet observable. Killed:
    `test_a_day_scored_after_the_refit_anchor_is_refused` failed with
    `AssertionError: LookAheadError not raised`.
    """

    def test_a_day_scored_after_the_refit_anchor_is_refused(self):
        anchor = date(2022, 3, 1)
        history = [(date(2022, 2, 28), (1.0, 2.0)), (date(2022, 3, 2), (2.0, 1.0))]
        with self.assertRaises(LookAheadError) as caught:
            recalibration.select_constants(history, anchor, 2, fallback=0)
        self.assertIn("2022-03-02", str(caught.exception))
        index, past = recalibration.select_constants(history[:1], anchor, 2, fallback=1)
        self.assertEqual((index, past), (0, 1))

    def test_no_choice_moves_with_a_loss_its_refit_could_not_see(self):
        scored, anchors, losses = selection_stream(200, 4)
        chosen = recalibration.nested_selection(scored, anchors, losses, 21, fallback=2)
        for block in chosen.blocks:
            first = scored.index(block.first_scored)
            perturbed = list(losses)
            for position in range(first, len(perturbed)):
                perturbed[position] = (0.0,) + (9.0,) * 3 if block.chosen else (9.0,) + (0.0,) * 3
            again = recalibration.nested_selection(scored, anchors, perturbed, 21, fallback=2)
            self.assertEqual(
                again.blocks[chosen.blocks.index(block)].chosen, block.chosen,
                f"block from {block.first_scored} moved with a later loss",
            )

    def test_the_choice_is_the_least_pooled_past_loss_and_is_used_for_its_block(self):
        scored, anchors, losses = selection_stream(100, 3)
        chosen = recalibration.nested_selection(scored, anchors, losses, 21, fallback=1)
        self.assertEqual(len(chosen.per_day), 100)
        self.assertEqual(len(chosen.blocks), 5)
        first = chosen.blocks[0]
        self.assertEqual(first.past_days, 0)
        self.assertEqual(first.chosen, 1, "no past day: the fallback")
        for block in chosen.blocks[1:]:
            past = [loss for when, loss in zip(scored, losses) if when <= block.anchor]
            self.assertEqual(block.past_days, len(past))
            means = [sum(loss[k] for loss in past) / len(past) for k in range(3)]
            self.assertEqual(block.chosen, means.index(min(means)))
            start = scored.index(block.first_scored)
            for position in range(start, min(start + 21, 100)):
                self.assertEqual(chosen.per_day[position], block.chosen)
        self.assertEqual(chosen.blocks[1].anchor, anchors[21])

    def test_ties_go_to_the_earlier_grid_point(self):
        history = [(date(2022, 1, 3), (1.0, 1.0, 1.0))]
        self.assertEqual(recalibration.select_constants(history, date(2022, 1, 3), 3, fallback=2)[0], 0)

    def test_malformed_losses_are_refused(self):
        with self.assertRaises(ValueError):
            recalibration.select_constants([(date(2022, 1, 3), (1.0,))], date(2022, 1, 3), 2, fallback=0)
        with self.assertRaises(ValueError):
            recalibration.select_constants(
                [(date(2022, 1, 3), (1.0, math.nan))], date(2022, 1, 3), 2, fallback=0
            )
        scored, anchors, losses = selection_stream(30, 2)
        with self.assertRaises(ValueError):
            recalibration.nested_selection(scored, anchors[:-1], losses, 21, fallback=0)


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



class _UncalibratedModel:
    """A fitted model's shape as `FoldPid` reads it: an uncalibrated band."""

    levels = LEVELS
    tail_fit = None

    def __init__(self, scale=1.0, settings=None):
        self.scale = scale
        self.model_settings = dict(settings or {})
        self.residuals = (-3.0 * scale, 0.0, 4.0 * scale)

    def predict(self, row):
        centre = row.spread_bps
        return tuple(centre + self.scale * offset for offset in (-1.0, -0.5, 0.0, 0.5, 1.0))

    def point_forecast(self, row):
        return row.spread_bps


class FoldPidTests(unittest.TestCase):
    """Conformal PID run inside a fold loop: `recalibration.FoldPid` (#124).

    Eleonora's ruling on #123 publishes the funding declaration's gbm with
    conformal PID and the calendar scorecaster, exactly as #122 scored it. The
    fold loops (`backtest`, `compare`, `exceedance-backtest`) issue one band
    per scored day and learn the day's label only after it is scored. Driven
    that way, `FoldPid` must issue `conformal_pid`'s bands to the bit, and its
    laws must be `ml.law_from_band` at those edges, as the re-diagnosis read
    them.

    Red first: written before `FoldPid` and `OnlinePid` existed
    (`AttributeError`).

    Mutation record. In a disposable copy of the tree under /tmp (checked to
    resolve to the copy's `src/`), `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`,
    CPython 3.11, this class run alone; unmutated control green; the mutation
    confirmed applied by `diff` against the tree:

    1. `OnlinePid.issue`'s guard, `if day.anchor >= day.scored_date:`, mutated
       to `if day.anchor > day.scored_date:` (a band issued at a decision whose
       anchor is its own scored day, so its own label was public). Killed:
       `test_a_day_anchored_on_its_own_scored_day_is_refused` failed with
       `AssertionError: LookAheadError not raised`.
    """

    LAG = 2

    def setUp(self):
        self.registry = load_source_registry(ROOT / "metadata" / "sources.json")
        self.splits = load_split_declaration(ROOT / "metadata" / "evaluation_splits.json")
        self.rule = InformationRule(self.registry, ("spread_bps",), decision_time=time(16, 0))
        rng = random.Random(124)
        self.rows = []
        when = date(2023, 1, 2)
        while len(self.rows) < 160:
            if when.weekday() < 5:
                last = date(when.year + (when.month == 12), when.month % 12 + 1, 1) - timedelta(days=1)
                spread = rng.gauss(0.0, 2.0) + (6.0 if (last - when).days < 1 else 0.0)
                self.rows.append(
                    DailyObservation(
                        when,
                        {
                            "sofr": 5.00 + spread / 100.0,
                            "iorb": 5.00,
                            "quarter_end": 1.0 if (when.month % 3 == 0 and (last - when).days < 1) else 0.0,
                            "tax_date": 1.0 if when.day == 15 else 0.0,
                            "days_to_month_end": float((last - when).days),
                            "treasury_settlement_coupons": 60.0 if when.day in (15, 30, 31) else 0.0,
                        },
                    )
                )
            when += timedelta(days=1)
        self.dates = [row.date for row in self.rows]
        self.scored = range(self.LAG + 1, len(self.rows))

    def drive(self, pid, model=None, *, laws=False):
        """Each scored day in turn: issue its band, then learn its label."""

        model = model or _UncalibratedModel()
        out = []
        for index in self.scored:
            feature_row = self.rows[index - self.LAG]
            if laws:
                vector = model.predict(feature_row)
                out.append(
                    pid.law(index, feature_row.date, vector, model.residuals[0], model.residuals[-1])
                )
            else:
                view = pid.view(model, index, feature_row)
                out.append((view.predict(feature_row), view.point_forecast(feature_row)))
            pid.label(index, self.rows[index].spread_bps)
        return out

    def reference(self, model=None):
        model = model or _UncalibratedModel()
        days = [
            recalibration.OnlineDay(
                scored_date=self.dates[index],
                anchor=self.dates[index - self.LAG],
                vector=model.predict(self.rows[index - self.LAG]),
                calendar=recalibration.scorecaster_calendar(
                    self.rows, self.rule, index, self.splits, self.dates
                ),
            )
            for index in self.scored
        ]
        actuals = [self.rows[index].spread_bps for index in self.scored]
        return days, recalibration.conformal_pid(days, actuals, LEVELS)

    def fold_pid(self):
        return recalibration.FoldPid(self.rows, self.rule, splits=self.splits)

    def test_the_fold_loop_issues_conformal_pids_bands_to_the_bit(self):
        _, bands = self.reference()
        issued = self.drive(self.fold_pid())
        self.assertEqual([vector for vector, _ in issued], [band.vector for band in bands])
        model = _UncalibratedModel()
        self.assertEqual(
            [point for _, point in issued],
            [model.point_forecast(self.rows[index - self.LAG]) for index in self.scored],
        )
        # The method moved something: it is not the uncalibrated band.
        days, _ = self.reference()
        self.assertNotEqual([day.vector for day in days], [band.vector for band in bands])

    def test_the_law_is_law_from_band_at_the_issued_edges(self):
        model = _UncalibratedModel()
        days, bands = self.reference(model)
        laws = self.drive(self.fold_pid(), model, laws=True)
        for day, band, law in zip(days, bands, laws):
            self.assertEqual(
                law,
                ml.law_from_band(
                    day.vector,
                    day.vector[0] - band.quantile,
                    day.vector[-1] + band.quantile,
                    model.residuals[0],
                    model.residuals[-1],
                    LEVELS,
                ),
            )

    def test_the_account_counts_what_the_run_did(self):
        _, bands = self.reference()
        pid = self.fold_pid()
        self.drive(pid)
        account = pid.account()
        self.assertEqual(account["days"], len(bands))
        self.assertEqual(account["days_before_first_label"], sum(1 for b in bands if b.observed == 0))
        self.assertEqual(account["saturated_days"], sum(b.saturated for b in bands))

    def test_the_settings_name_the_method_and_its_declared_constants(self):
        settings = self.fold_pid().settings
        self.assertEqual(settings["calibration"], "conformal_pid")
        constants = settings["calibration_constants"]
        self.assertEqual(constants["PID_STEP"], recalibration.PID_STEP)
        self.assertEqual(constants["SCORECASTER_INDICATORS"], list(recalibration.SCORECASTER_INDICATORS))
        self.assertEqual(
            set(constants),
            {
                "PID_STEP", "PID_STEP_WINDOW", "PID_SCALE_FLOOR", "PID_INTEGRATOR_GAIN",
                "PID_SATURATION", "PID_TANGENT_LIMIT", "SCORECASTER_MINIMUM",
                "SCORECASTER_INDICATOR_MINIMUM", "SCORECASTER_INDICATORS",
            },
        )

    def test_a_day_anchored_on_its_own_scored_day_is_refused(self):
        pid = self.fold_pid()
        index = 10
        with self.assertRaises(LookAheadError) as caught:
            pid.view(_UncalibratedModel(), index, self.rows[index])
        self.assertIn(str(self.dates[index]), str(caught.exception))

    def test_each_label_is_learned_once_after_its_own_band(self):
        pid = self.fold_pid()
        model = _UncalibratedModel()
        with self.assertRaises(ValueError):
            pid.label(10, 0.0)
        pid.view(model, 10, self.rows[8])
        with self.assertRaises(ValueError):
            pid.view(model, 11, self.rows[9])
        with self.assertRaises(ValueError):
            pid.label(11, 0.0)
        pid.label(10, 0.0)
        with self.assertRaises(ValueError):
            pid.view(model, 10, self.rows[8])

    def test_a_calibrated_or_tailed_base_is_refused(self):
        pid = self.fold_pid()
        with self.assertRaises(ValueError):
            pid.view(_UncalibratedModel(settings={"calibration": "cross_conformal"}), 10, self.rows[8])
        tailed = _UncalibratedModel()
        tailed.tail_fit = object()
        with self.assertRaises(ValueError):
            pid.view(tailed, 10, self.rows[8])


class NestedFoldPidTests(unittest.TestCase):
    """Nested-selection conformal PID inside a fold loop: `NestedFoldPid` (#124).

    Eleonora's rulings on #136 and #134 republish the funding declaration with
    conformal PID whose constants are chosen by nested walk-forward selection
    (#125, `nested_selection`), not #122's fixed ones. Driven one scored day at
    a time, as the fold loops drive it, `NestedFoldPid` must issue on every day
    the band of the grid point `nested_selection` chose for that day's refit
    block, from the same per-point `conformal_pid` runs, and must record the
    same choice at every block.

    The fixture's forecasts are anchored two rows back, so the day scored just
    before a refit is not observable at it: a selection that read every label
    learned so far, rather than those observable at the refit, is refused by
    `select_constants` (`LookAheadError`).

    Red first: written before `NestedFoldPid` existed (`AttributeError`).
    """

    LAG = FoldPidTests.LAG
    REFIT_EVERY = 20
    setUp = FoldPidTests.setUp
    drive = FoldPidTests.drive

    def fold_pid(self):
        return recalibration.NestedFoldPid(
            self.rows, self.rule, splits=self.splits, refit_every=self.REFIT_EVERY
        )

    def reference(self, model=None):
        model = model or _UncalibratedModel()
        days = [
            recalibration.OnlineDay(
                scored_date=self.dates[index],
                anchor=self.dates[index - self.LAG],
                vector=model.predict(self.rows[index - self.LAG]),
                calendar=recalibration.scorecaster_calendar(
                    self.rows, self.rule, index, self.splits, self.dates
                ),
            )
            for index in self.scored
        ]
        actuals = [self.rows[index].spread_bps for index in self.scored]
        grid = recalibration.PID_GRID
        runs = [recalibration.conformal_pid(days, actuals, LEVELS, constants=point) for point in grid]
        losses = [
            tuple(crps_from_quantiles(LEVELS, run[i].vector, actual) for run in runs)
            for i, actual in enumerate(actuals)
        ]
        nested = recalibration.nested_selection(
            [day.scored_date for day in days],
            [day.anchor for day in days],
            losses,
            self.REFIT_EVERY,
            fallback=grid.index(recalibration.DECLARED_PID),
        )
        bands = [runs[chosen][i] for i, chosen in enumerate(nested.per_day)]
        return days, bands, nested

    def test_the_fold_loop_issues_the_nested_choice_to_the_bit(self):
        _, bands, nested = self.reference()
        pid = self.fold_pid()
        issued = self.drive(pid)
        self.assertEqual([vector for vector, _ in issued], [band.vector for band in bands])
        self.assertEqual(pid.blocks, nested.blocks)
        # The selection moved off #122's point at some refit, so the test
        # tells nested selection from the fixed constants.
        declared = recalibration.PID_GRID.index(recalibration.DECLARED_PID)
        self.assertTrue(any(block.chosen != declared for block in nested.blocks))

    def test_the_law_is_law_from_band_at_the_chosen_edges(self):
        model = _UncalibratedModel()
        days, bands, _ = self.reference(model)
        laws = self.drive(self.fold_pid(), model, laws=True)
        for day, band, law in zip(days, bands, laws):
            self.assertEqual(
                law,
                ml.law_from_band(
                    day.vector,
                    day.vector[0] - band.quantile,
                    day.vector[-1] + band.quantile,
                    model.residuals[0],
                    model.residuals[-1],
                    LEVELS,
                ),
            )

    def test_the_settings_name_the_method_its_grid_and_its_selection(self):
        settings = self.fold_pid().settings
        self.assertEqual(settings["calibration"], "conformal_pid_nested")
        constants = settings["calibration_constants"]
        self.assertEqual(constants["PID_STEP_WINDOW"], recalibration.PID_STEP_WINDOW)
        self.assertNotIn("PID_STEP", constants)
        selection = settings["calibration_selection"]
        self.assertEqual(selection["refit_every"], self.REFIT_EVERY)
        self.assertEqual(selection["loss"], "crps")
        self.assertEqual(selection["points"], len(recalibration.PID_GRID))
        self.assertEqual(
            selection["fallback"], recalibration.DECLARED_PID._asdict()
        )
        self.assertEqual(selection["grid"]["steps"], list(recalibration.PID_GRID_STEPS))

    def test_each_label_is_learned_once_after_its_own_band(self):
        FoldPidTests.test_each_label_is_learned_once_after_its_own_band(self)

    def test_a_calibrated_base_is_refused(self):
        FoldPidTests.test_a_calibrated_or_tailed_base_is_refused(self)


if __name__ == "__main__":
    unittest.main()
