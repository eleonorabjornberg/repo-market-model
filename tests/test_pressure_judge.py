"""The pressure-day judge (#375): the declared bar, applied to walk-forward probabilities.

`pressure_judge.judge` reads a declaration (`metadata/pressure_judge.json`), the
shared grid and each candidate's probabilities at +5 and +10 bp, and returns the
evidence of Eleonora's replacement bar (#375, 7 October 2026): tier 1 (onset
warning), tier 2 (risky dates, reported), tier 3 (no crying wolf), tier 4
(continuation, reported), tier 5 (week-ahead window) and the pass rule. These
tests build small synthetic series so each rule has a known answer.

**Recorded mutations** (CLAUDE.md: each new leakage guard carries one that kills it).

* `Declaration.cutoff` refuses a cut-off the declaration does not carry, and a
  requested cut-off that differs from the declared one. Mutation 1: in
  `pressure_judge.Declaration.cutoff`, replace the `raise ValueError(...)` for a
  missing cut-off with `return 0.5`; the failing test was
  `test_refuses_a_cutoff_that_is_not_declared`, which raised `AssertionError`
  (`ValueError not raised`). Mutation 2: replace
  `if requested is not None and float(requested) != float(declared):` with
  `if False:`; the failing test was
  `test_refuses_a_requested_cutoff_that_differs_from_the_declared_one`, also
  `AssertionError` (`ValueError not raised`).
* `require_scored_days` refuses a day the lockbox holds.
  Mutation: delete the `lockbox.require_unlocked(...)` call in
  `pressure_judge.require_scored_days`. The failing tests were
  `test_refuses_a_day_in_a_locked_tier` and
  `test_judge_refuses_a_grid_with_a_locked_day`, which raised `AssertionError`
  (`LookAheadError not raised`).
* `require_scored_days` refuses a development day after the declared last
  scored day, even in a tier that is open. Mutation: replace
  `elif day > declaration.last_day:` with `elif False:` in
  `pressure_judge.require_scored_days`. The failing test was
  `test_refuses_a_day_after_the_declared_last_scored_day`, which raised
  `AssertionError` (`LookAheadError not raised`).
* `require_scored_days` refuses, in the single look, a day outside the declared
  confirmation window (a development day, or one past the window). Mutation:
  replace `if not declaration.confirmation_first <= day <= declaration.confirmation_last:`
  with `if False:`. The failing tests were
  `test_the_look_refuses_a_development_day` and
  `test_the_look_refuses_a_day_past_the_window`, which raised `AssertionError`
  (`LookAheadError not raised`).
* The look scores only candidates the declaration names for it. Mutation: in
  `pressure_judge._check_forecasts`, replace
  `and forecast.name not in declaration.confirmation_candidates` with
  `and False`. The failing test was
  `test_the_look_refuses_a_candidate_not_named_for_it`, which raised
  `AssertionError` (`ValueError not raised`).
"""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model import pressure_judge as pj
from repo_model.splits import LookAheadError


def _weekdays(count, start=date(2019, 1, 1)):
    days, day = [], start
    while len(days) < count:
        if day.weekday() < 5:
            days.append(day)
        day += timedelta(days=1)
    return days


def _declaration(**overrides):
    document = {
        "status": "test",
        "scoring": {"last_day": "2025-12-31"},
        "confirmation": {"first": "2026-01-01", "last": "2026-09-03", "candidates": ["sharp"]},
        "thresholds_bp": [5, 10],
        "primary_threshold_bp": 5,
        "horizons": [1, 2],
        "bootstrap": {"level": 0.9, "replications": 200, "block_length": 5, "seed": 375},
        "tiers": {
            "onset_warning": {
                "lead_at_least": 1, "recall_at_least": 0.5, "false_alarms_per_onset_at_most": 2.0,
                "far_lead_at_least": 2, "far_recall_at_least": 0.3,
            },
            "risky_dates": {"scarcity_state_at_least": 2, "lead": 2, "auroc_at_least": 0.75},
            "no_crying_wolf": {
                "abundant_scarcity_state": 0, "abundant_regime": "b",
                "flags_per_year_at_most": 21, "business_days_per_year": 252,
            },
            "week_ahead": {"days": 2, "combine": "independence"},
        },
        "early_warning": {"usefulness_preference": 0.5},
        "groupings": ["regime", "day_type"],
        "benchmarks": {"climatology": "calendar_climatology", "persistence": "persistence_logistic"},
        "candidates": {
            "calendar_climatology": {
                "role": "benchmark", "features": ["day_type"], "calibration": "none",
                "cutoffs": {"5": 0.2, "10": 0.2},
            },
            "persistence_logistic": {
                "role": "benchmark", "features": ["spread_bps"], "calibration": "none",
                "cutoffs": {"5": 0.2, "10": 0.2},
            },
            "sharp": {
                "role": "candidate", "features": ["x"], "calibration": "none",
                "cutoffs": {"5": 0.5, "10": 0.5},
            },
            "published": {
                "role": "baseline", "features": ["x"], "calibration": "none",
                "cutoffs": {"5": 0.5, "10": 0.5},
            },
        },
    }
    document.update(overrides)
    return document


def _write(document):
    handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    handle.write(json.dumps(document))
    handle.close()
    return Path(handle.name)


def _load(**overrides):
    return pj.load_declaration(_write(_declaration(**overrides)))


class Series:
    """A 400-day series: a pressure day every 20th day, each an onset; flat climatology.

    The first 200 days are scarcity state 0, the rest state 2. Regime "a" is
    2019, regime "b" the rest. Every 10th day is a scheduled risk date.
    """

    def __init__(self, count=400, start=date(2019, 1, 1)):
        self.dates = tuple(_weekdays(count, start))
        self.y5 = tuple(1 if k % 20 == 19 else 0 for k in range(count))
        self.y10 = tuple(1 if k % 40 == 39 else 0 for k in range(count))
        self.groups = {
            "regime": tuple("a" if d.year == 2019 else "b" for d in self.dates),
            "day_type": tuple("quarter_end" if k % 10 == 9 else "ordinary" for k in range(count)),
            "scarcity_state": tuple("0" if k < 200 else "2" for k in range(count)),
            "risk_date": tuple("1" if k % 10 == 9 else "0" for k in range(count)),
        }

    def grid(self, horizon):
        return pj.Grid(
            horizon=horizon,
            dates=self.dates,
            outcomes={5.0: self.y5, 10.0: self.y10},
            groups=self.groups,
            onset=self.y5,
        )

    def forecast(self, name, horizon, p5, p10=None):
        return pj.Forecast(
            name=name, horizon=horizon, dates=self.dates,
            probabilities={5.0: tuple(p5), 10.0: tuple(p10 if p10 is not None else p5)},
        )

    def perfect(self, horizon, name="sharp"):
        return self.forecast(
            name, horizon,
            [1.0 if y else 0.0 for y in self.y5],
            [1.0 if y else 0.0 for y in self.y10],
        )

    def flat(self, name, horizon, level):
        return self.forecast(name, horizon, [level] * len(self.dates))

    def everything(self, candidate):
        grids = {h: self.grid(h) for h in (1, 2)}
        forecasts = []
        for h in (1, 2):
            forecasts.append(self.flat("calendar_climatology", h, 0.1))
            forecasts.append(self.flat("persistence_logistic", h, 0.1))
            forecasts.append(candidate(h))
        return grids, forecasts

    def judged(self, candidate, **options):
        grids, forecasts = self.everything(candidate)
        return pj.judge(_load(), grids, forecasts, calendar=self.dates, **options)


class DeclarationTests(unittest.TestCase):
    def test_a_valid_declaration_loads_with_its_digest(self):
        declaration = _load()
        self.assertEqual(declaration.horizons, (1, 2))
        self.assertEqual(len(declaration.sha256), 64)
        self.assertEqual(declaration.cutoff("sharp", 5.0, 1), 0.5)
        self.assertEqual(declaration.week_days, 2)

    def test_refuses_a_cutoff_that_is_not_declared(self):
        declaration = _load()
        with self.assertRaises(ValueError):
            declaration.cutoff("sharp", 20.0, 1)
        with self.assertRaises(ValueError):
            declaration.cutoff("not_declared", 5.0, 1)

    def test_refuses_a_requested_cutoff_that_differs_from_the_declared_one(self):
        declaration = _load()
        self.assertEqual(declaration.cutoff("sharp", 5.0, 1, requested=0.5), 0.5)
        with self.assertRaises(ValueError):
            declaration.cutoff("sharp", 5.0, 1, requested=0.3)

    def test_a_candidate_with_no_cutoff_for_a_threshold_does_not_load(self):
        document = _declaration()
        del document["candidates"]["sharp"]["cutoffs"]["10"]
        with self.assertRaises(ValueError):
            pj.load_declaration(_write(document))

    def test_a_cutoff_must_be_a_probability(self):
        for bad in (0.0, 1.0, 1.5, True, "0.5"):
            document = _declaration()
            document["candidates"]["sharp"]["cutoffs"]["5"] = bad
            with self.assertRaises(ValueError, msg=repr(bad)):
                pj.load_declaration(_write(document))

    def test_a_per_horizon_cutoff_must_cover_every_horizon(self):
        document = _declaration()
        document["candidates"]["sharp"]["cutoffs"]["5"] = {"1": 0.4}
        with self.assertRaises(ValueError):
            pj.load_declaration(_write(document))
        document["candidates"]["sharp"]["cutoffs"]["5"] = {"1": 0.4, "2": 0.3}
        declaration = pj.load_declaration(_write(document))
        self.assertEqual(declaration.cutoff("sharp", 5.0, 2), 0.3)

    def test_the_benchmarks_must_be_declared_candidates(self):
        document = _declaration()
        document["benchmarks"]["climatology"] = "missing"
        with self.assertRaises(ValueError):
            pj.load_declaration(_write(document))

    def test_the_confirmation_window_must_follow_the_scored_days(self):
        with self.assertRaises(ValueError):
            _load(confirmation={"first": "2025-12-31", "last": "2026-09-03", "candidates": []})

    def test_the_look_may_name_only_declared_candidates(self):
        with self.assertRaises(ValueError):
            _load(confirmation={"first": "2026-01-01", "last": "2026-09-03", "candidates": ["nobody"]})
        with self.assertRaises(ValueError):
            _load(confirmation={"first": "2026-01-01", "last": "2026-09-03", "candidates": ["published"]})

    def test_the_tier_leads_must_be_judged_horizons_and_cover_the_week(self):
        document = _declaration()
        document["tiers"]["risky_dates"]["lead"] = 5
        with self.assertRaises(ValueError):
            pj.load_declaration(_write(document))
        document = _declaration()
        document["tiers"]["week_ahead"]["days"] = 3
        with self.assertRaises(ValueError):
            pj.load_declaration(_write(document))
        document = _declaration()
        document["tiers"]["week_ahead"]["combine"] = "mean"
        with self.assertRaises(ValueError):
            pj.load_declaration(_write(document))

    def test_the_tracked_declaration_loads(self):
        declaration = pj.load_declaration()
        self.assertEqual(declaration.last_day, date(2025, 12, 31))
        self.assertEqual(declaration.confirmation_first, date(2026, 1, 1))
        self.assertEqual(declaration.confirmation_last, date(2026, 9, 3))
        self.assertEqual(declaration.onset_recall_at_least, 0.5)
        self.assertEqual(declaration.onset_false_alarms_at_most, 2.0)
        self.assertEqual(declaration.flags_per_year_at_most, 21)
        self.assertEqual(declaration.week_days, 5)
        self.assertIn(declaration.climatology, declaration.candidates)


class GuardTests(unittest.TestCase):
    def test_refuses_a_day_in_a_locked_tier(self):
        # The declared last day is moved past the lockbox's blind tier so only
        # the lockbox can refuse the scored day.
        declaration = _load(
            scoring={"last_day": "2027-12-31"},
            confirmation={"first": "2028-01-01", "last": "2028-02-01", "candidates": []},
        )
        with self.assertRaises(LookAheadError):
            pj.require_scored_days(declaration, [date(2026, 9, 4)], where="test")

    def test_refuses_a_day_after_the_declared_last_scored_day(self):
        # 2026-02-02 is in the near-blind tier, which is open: only the judge's
        # own declared last day refuses it in development.
        declaration = _load()
        with self.assertRaises(LookAheadError):
            pj.require_scored_days(declaration, [date(2026, 2, 2)], where="test")
        pj.require_scored_days(declaration, [date(2025, 12, 31)], where="test")

    def test_the_look_refuses_a_development_day(self):
        declaration = _load()
        with self.assertRaises(LookAheadError):
            pj.require_scored_days(declaration, [date(2025, 12, 31)], where="test", confirmation=True)
        pj.require_scored_days(declaration, [date(2026, 2, 2)], where="test", confirmation=True)

    def test_the_look_refuses_a_day_past_the_window(self):
        declaration = _load(confirmation={"first": "2026-01-01", "last": "2026-03-31", "candidates": []})
        with self.assertRaises(LookAheadError):
            pj.require_scored_days(declaration, [date(2026, 4, 15)], where="test", confirmation=True)
        pj.require_scored_days(declaration, [date(2026, 3, 31)], where="test", confirmation=True)

    def test_judge_refuses_a_grid_with_a_locked_day(self):
        series = Series(count=40, start=date(2026, 8, 20))
        declaration = _load(
            scoring={"last_day": "2027-12-31"},
            confirmation={"first": "2028-01-01", "last": "2028-02-01", "candidates": []},
        )
        grids = {h: series.grid(h) for h in (1, 2)}
        forecasts = [
            series.flat(name, h, 0.1)
            for h in (1, 2)
            for name in ("calendar_climatology", "persistence_logistic", "sharp")
        ]
        with self.assertRaises(LookAheadError):
            pj.judge(declaration, grids, forecasts, calendar=series.dates)

    def test_the_look_refuses_a_candidate_not_named_for_it(self):
        series = Series(count=60, start=date(2026, 1, 5))
        named = _load()
        unnamed = _load(confirmation={"first": "2026-01-01", "last": "2026-09-03", "candidates": []})
        grids, forecasts = series.everything(lambda h: series.perfect(h))
        result = pj.judge(named, grids, forecasts, calendar=series.dates, confirmation=True)
        self.assertEqual(result["mode"], "confirmation")
        with self.assertRaises(ValueError):
            pj.judge(unnamed, grids, forecasts, calendar=series.dates, confirmation=True)
        # In development the same declaration scores the candidate without a list.
        development = Series()
        grids, forecasts = development.everything(lambda h: development.perfect(h))
        pj.judge(unnamed, grids, forecasts, calendar=development.dates)

    def test_refuses_a_candidate_that_is_not_declared(self):
        series = Series()
        grids, forecasts = series.everything(lambda h: series.perfect(h, name="undeclared"))
        with self.assertRaises(ValueError):
            pj.judge(_load(), grids, forecasts, calendar=series.dates)

    def test_refuses_forecasts_on_other_days_than_the_grid(self):
        series = Series()
        grids, forecasts = series.everything(lambda h: series.perfect(h))
        shifted = forecasts[-1]
        forecasts[-1] = pj.Forecast(
            name=shifted.name, horizon=shifted.horizon,
            dates=shifted.dates[1:] + (shifted.dates[-1] + timedelta(days=3),),
            probabilities=shifted.probabilities,
        )
        with self.assertRaises(ValueError):
            pj.judge(_load(), grids, forecasts, calendar=series.dates)

    def test_refuses_a_probability_outside_zero_one(self):
        series = Series()
        grids, forecasts = series.everything(
            lambda h: series.forecast("sharp", h, [1.2] + [0.1] * (len(series.dates) - 1))
        )
        with self.assertRaises(ValueError):
            pj.judge(_load(), grids, forecasts, calendar=series.dates)

    def test_refuses_a_grid_missing_a_declared_grouping(self):
        series = Series()
        grids, forecasts = series.everything(lambda h: series.perfect(h))
        for dropped in ("day_type", "risk_date"):
            groups = {k: v for k, v in series.groups.items() if k != dropped}
            grids[1] = pj.Grid(
                horizon=1, dates=series.dates, outcomes={5.0: series.y5, 10.0: series.y10},
                groups=groups, onset=series.y5,
            )
            with self.assertRaises(ValueError, msg=dropped):
                pj.judge(_load(), grids, forecasts, calendar=series.dates)

    def test_refuses_a_run_without_the_declared_climatology(self):
        series = Series()
        grids, forecasts = series.everything(lambda h: series.perfect(h))
        forecasts = [f for f in forecasts if f.name != "calendar_climatology"]
        with self.assertRaises(ValueError):
            pj.judge(_load(), grids, forecasts, calendar=series.dates)


class MetricTests(unittest.TestCase):
    def test_auroc_counts_ties_as_half(self):
        self.assertEqual(pj.auroc([0.9, 0.8, 0.1, 0.2], [1, 1, 0, 0]), 1.0)
        self.assertEqual(pj.auroc([0.5, 0.5, 0.5, 0.5], [1, 1, 0, 0]), 0.5)
        self.assertEqual(pj.auroc([0.1, 0.9], [1, 0]), 0.0)
        self.assertIsNone(pj.auroc([0.1, 0.9], [0, 0]))

    def test_usefulness_is_the_loss_saved_against_the_best_default(self):
        # theta = 0.5: loss = 0.5 FNR + 0.5 FPR; the default loss is 0.5.
        # 3 of 4 events caught, 1 of 4 non-events flagged: FNR .25, FPR .25.
        flags = [1, 1, 1, 0, 1, 0, 0, 0]
        y = [1, 1, 1, 1, 0, 0, 0, 0]
        got = pj.usefulness(flags, y, 0.5)
        self.assertAlmostEqual(got["absolute"], 0.5 - 0.25)
        self.assertAlmostEqual(got["relative"], 0.5)

    def test_matched_false_alarm_weights_reach_the_target_count_exactly(self):
        p = [0.9, 0.8, 0.8, 0.8, 0.1, 0.1]
        y = [1, 0, 0, 1, 0, 1]
        weights = pj.matched_false_alarm_weights(p, y, 1)
        raised = sum(w for w, t in zip(weights, y) if not t)
        self.assertAlmostEqual(raised, 1.0)
        self.assertEqual(weights[0], 1.0)
        self.assertEqual(weights[4], 0.0)
        # The tied group at 0.8 (2 false alarms of 3 days) is flagged in part.
        self.assertTrue(0.0 < weights[1] < 1.0)
        self.assertEqual(weights[1], weights[2])

    def test_a_pressure_day_costs_no_false_alarm(self):
        weights = pj.matched_false_alarm_weights([0.9, 0.8, 0.1], [1, 1, 0], 0)
        self.assertEqual(weights, (1.0, 1.0, 0.0))

    def test_a_flat_forecast_is_matched_by_flagging_every_day_in_proportion(self):
        weights = pj.matched_false_alarm_weights([0.1] * 10, [1, 0] * 5, 2)
        self.assertTrue(all(abs(w - 0.4) < 1e-12 for w in weights))


class TierTests(unittest.TestCase):
    def test_a_sharp_candidate_passes_every_tier_of_the_pass_rule(self):
        result = Series().judged(lambda h: Series().perfect(h))
        sharp = result["candidates"]["sharp"]
        near = sharp["tiers"]["onset_warning"]["lead_at_least_1"]
        self.assertEqual(near["onsets"], 20)
        self.assertEqual(near["recall"]["mean"], 1.0)
        self.assertEqual(near["climatology_recall"], 0.0)
        self.assertEqual(near["worst_false_alarms_per_onset"], 0.0)
        self.assertTrue(all(near["criteria"].values()))
        self.assertTrue(near["passes"])
        for horizon in ("1", "2"):
            self.assertTrue(sharp["tiers"]["no_crying_wolf"][horizon]["ok"])
        week = sharp["tiers"]["week_ahead"]
        self.assertTrue(week["criteria"]["calibrated"])
        self.assertTrue(week["criteria"]["beats_climatology_brier"])
        verdict = sharp["verdict"]
        self.assertTrue(verdict["tier_1_onset_warning"])
        self.assertTrue(verdict["tier_3_no_crying_wolf"])
        self.assertTrue(verdict["tier_5_week_ahead"])
        self.assertTrue(verdict["passes"])
        row = sharp["horizons"]["1"]["5"]
        self.assertEqual(row["auroc"], 1.0)
        self.assertEqual(row["usefulness"]["relative"], 1.0)

    def test_the_cutoff_is_read_from_the_declaration_not_the_scored_days(self):
        series = Series()
        # Probabilities of 0.4 on events: the declared 0.5 flags nothing.
        weak = lambda h: series.forecast("sharp", h, [0.4 if y else 0.0 for y in series.y5])
        grids, forecasts = series.everything(weak)
        result = pj.judge(_load(), grids, forecasts, calendar=series.dates)
        sharp = result["candidates"]["sharp"]
        self.assertEqual(sharp["horizons"]["1"]["5"]["cutoff"], 0.5)
        self.assertEqual(sharp["horizons"]["1"]["5"]["flags"]["alarms"], 0)
        self.assertEqual(sharp["tiers"]["onset_warning"]["lead_at_least_1"]["recall"]["mean"], 0.0)
        self.assertFalse(sharp["verdict"]["passes"])
        # The same forecasts under a declared cut-off of 0.3 flag every onset.
        candidates = {**_declaration()["candidates"], "sharp": {
            "role": "candidate", "features": ["x"], "calibration": "none", "cutoffs": {"5": 0.3, "10": 0.3}}}
        result = pj.judge(_load(candidates=candidates), grids, forecasts, calendar=series.dates)
        self.assertEqual(result["candidates"]["sharp"]["tiers"]["onset_warning"]["lead_at_least_1"]["recall"]["mean"], 1.0)

    def test_too_many_false_alarms_fail_tier_one(self):
        series = Series()
        noisy = lambda h: series.forecast(
            "sharp", h, [1.0 if (y or k % 20 < 9) else 0.0 for k, y in enumerate(series.y5)]
        )
        near = series.judged(noisy)["candidates"]["sharp"]["tiers"]["onset_warning"]["lead_at_least_1"]
        self.assertEqual(near["recall"]["mean"], 1.0)
        self.assertAlmostEqual(near["worst_false_alarms_per_onset"], 9.0)
        self.assertFalse(near["criteria"]["false_alarms"])
        self.assertFalse(near["passes"])

    def test_a_candidate_that_only_matches_climatology_fails(self):
        series = Series()
        result = series.judged(lambda h: series.flat("sharp", h, 0.1))
        sharp = result["candidates"]["sharp"]
        self.assertFalse(sharp["tiers"]["week_ahead"]["criteria"]["beats_climatology_brier"])
        self.assertFalse(sharp["verdict"]["passes"])
        self.assertFalse(result["candidates"]["calendar_climatology"]["verdict"]["passes"])

    def test_recall_must_beat_climatology_at_the_same_false_alarm_rate(self):
        series = Series()
        grids = {h: series.grid(h) for h in (1, 2)}
        forecasts = []
        for h in (1, 2):
            # A climatology that already ranks every pressure day first catches them
            # all at zero false alarms: matching it is not enough.
            forecasts.append(series.perfect(h, name="calendar_climatology"))
            forecasts.append(series.flat("persistence_logistic", h, 0.1))
            forecasts.append(series.perfect(h))
        result = pj.judge(_load(), grids, forecasts, calendar=series.dates)
        near = result["candidates"]["sharp"]["tiers"]["onset_warning"]["lead_at_least_1"]
        self.assertEqual(near["recall"]["mean"], 1.0)
        self.assertEqual(near["climatology_recall"], 1.0)
        self.assertTrue(near["criteria"]["recall"])
        self.assertFalse(near["criteria"]["recall_above_climatology"])
        self.assertFalse(near["passes"])

    def test_the_climatology_is_matched_on_false_alarms_not_on_flags(self):
        series = Series()
        # A candidate that flags every pressure day plus 19 days in 20 raises many false
        # alarms; a flat climatology flags in proportion and so catches few onsets.
        noisy = lambda h: series.forecast("sharp", h, [1.0 if (y or k % 20 != 0) else 0.0 for k, y in enumerate(series.y5)])
        near = series.judged(noisy)["candidates"]["sharp"]["tiers"]["onset_warning"]["lead_at_least_1"]
        self.assertEqual(near["recall"]["mean"], 1.0)
        # 360 false alarms of 380 non-pressure days at each of two horizons: a flat
        # climatology that spends the same budget flags 360/380 of the onsets at each,
        # and misses one only when it misses at both.
        self.assertAlmostEqual(near["climatology_recall"], 1.0 - (20 / 380) ** 2, places=6)

    def test_lead_at_least_reads_the_longest_horizon_that_flagged_the_onset(self):
        series = Series()
        # Flags the onsets at h = 1 only: caught at lead >= 1, not at lead >= 2.
        one_day = lambda h: series.perfect(h) if h == 1 else series.flat("sharp", h, 0.0)
        tiers = series.judged(one_day)["candidates"]["sharp"]["tiers"]["onset_warning"]
        self.assertEqual(tiers["lead_at_least_1"]["recall"]["mean"], 1.0)
        self.assertEqual(tiers["lead_at_least_2"]["recall"]["mean"], 0.0)
        self.assertFalse(tiers["lead_at_least_2"]["meets_far_recall"])
        # Flags at h = 2 only: caught at lead >= 1 as well, and at lead >= 2.
        two_days = lambda h: series.perfect(h) if h == 2 else series.flat("sharp", h, 0.0)
        tiers = series.judged(two_days)["candidates"]["sharp"]["tiers"]["onset_warning"]
        self.assertEqual(tiers["lead_at_least_1"]["recall"]["mean"], 1.0)
        self.assertEqual(tiers["lead_at_least_2"]["recall"]["mean"], 1.0)
        self.assertTrue(tiers["lead_at_least_2"]["meets_far_recall"])
        self.assertTrue(tiers["lead_at_least_2"]["reported_only"])

    def test_a_flag_on_every_abundant_day_is_crying_wolf(self):
        series = Series()
        wolf = lambda h: series.forecast("sharp", h, [1.0 if k < 200 or y else 0.0 for k, y in enumerate(series.y5)])
        result = series.judged(wolf)["candidates"]["sharp"]
        tier = result["tiers"]["no_crying_wolf"]["1"]
        stretch = tier["abundant_stretches"]["scarcity_state_0"]
        self.assertEqual(stretch["days"], 200)
        self.assertGreater(stretch["flags_per_year"], 21)
        self.assertFalse(stretch["ok"])
        self.assertFalse(tier["ok"])
        self.assertFalse(result["verdict"]["tier_3_no_crying_wolf"])
        self.assertFalse(result["verdict"]["passes"])

    def test_the_alarm_rate_is_per_252_business_days(self):
        series = Series()
        result = series.judged(lambda h: series.perfect(h))["candidates"]["sharp"]
        stretch = result["tiers"]["no_crying_wolf"]["1"]["abundant_stretches"]["scarcity_state_0"]
        # Ten pressure days flagged in 200 days.
        self.assertAlmostEqual(stretch["flags_per_year"], 10 / 200 * 252)
        regime = result["tiers"]["no_crying_wolf"]["1"]["abundant_stretches"]["regime_b"]
        self.assertTrue(regime["days"] > 0)

    def test_a_miscalibrated_regime_fails_tier_three(self):
        series = Series()
        # Never flags (below the cut-off) but predicts 10% where pressure runs at 5%.
        high = lambda h: series.flat("sharp", h, 0.1)
        result = series.judged(high)["candidates"]["sharp"]
        calibrated = result["tiers"]["no_crying_wolf"]["1"]["calibrated_by_regime"]
        self.assertEqual(set(calibrated), {"a", "b"})
        self.assertFalse(calibrated["a"])
        self.assertTrue(result["tiers"]["no_crying_wolf"]["1"]["abundant_stretches"]["scarcity_state_0"]["ok"])
        self.assertFalse(result["tiers"]["no_crying_wolf"]["1"]["ok"])

    def test_tier_three_needs_every_lead(self):
        series = Series()
        wolf_at_two = lambda h: series.perfect(h) if h == 1 else series.forecast(
            "sharp", h, [1.0 if k < 200 or y else 0.0 for k, y in enumerate(series.y5)]
        )
        verdict = series.judged(wolf_at_two)["candidates"]["sharp"]["verdict"]
        self.assertTrue(verdict["tier_3_no_crying_wolf_by_horizon"]["1"])
        self.assertFalse(verdict["tier_3_no_crying_wolf_by_horizon"]["2"])
        self.assertFalse(verdict["passes"])

    def test_risky_dates_are_scored_in_scarcity_state_two_or_more(self):
        series = Series()
        risky = series.judged(lambda h: series.perfect(h))["candidates"]["sharp"]["tiers"]["risky_dates"]
        # Days 200..399 are state 2; every 10th is a risk date; half of those are pressure days.
        self.assertEqual(risky["days"], 20)
        self.assertEqual(risky["events"], 10)
        self.assertEqual(risky["auroc"], 1.0)
        self.assertEqual(risky["climatology_auroc"], 0.5)
        self.assertEqual(risky["auroc_difference"]["mean"], 0.5)
        self.assertTrue(risky["meets_auroc"])
        self.assertTrue(risky["reported_only"])

    def test_the_week_ahead_window_is_one_if_any_of_the_next_days_is_a_pressure_day(self):
        series = Series()
        week = series.judged(lambda h: series.perfect(h))["candidates"]["sharp"]["tiers"]["week_ahead"]
        # Decision days 0..397 have both targets: pressure days at 19, 39, ... flag the
        # two days before them.
        self.assertEqual(week["days"], 398)
        self.assertEqual(week["events"], 39)
        self.assertEqual(week["brier"], 0.0)
        self.assertEqual(week["combine"], "independence")

    def test_the_published_baseline_may_cover_fewer_horizons_and_cannot_then_pass(self):
        series = Series()
        grids, forecasts = series.everything(lambda h: series.perfect(h))
        forecasts.append(series.perfect(1, name="published"))
        result = pj.judge(_load(), grids, forecasts, calendar=series.dates)
        published = result["candidates"]["published"]
        self.assertEqual(published["scored_horizons"], [1])
        self.assertEqual(list(published["horizons"]), ["1"])
        self.assertIn("unavailable", published["tiers"]["week_ahead"])
        self.assertFalse(published["tiers"]["onset_warning"]["lead_at_least_1"]["complete"])
        self.assertFalse(published["verdict"]["passes"])
        self.assertEqual(published["verdict"]["not_scored"], [2])

    def test_a_candidate_that_is_not_a_baseline_must_cover_every_horizon(self):
        series = Series()
        grids, forecasts = series.everything(lambda h: series.perfect(h))
        forecasts = [f for f in forecasts if not (f.name == "sharp" and f.horizon == 2)]
        with self.assertRaises(ValueError):
            pj.judge(_load(), grids, forecasts, calendar=series.dates)

    def test_splits_by_every_declared_grouping_and_the_holdouts(self):
        series = Series()
        holdouts = {"window": (series.dates[100], series.dates[130])}
        result = series.judged(lambda h: series.perfect(h), holdouts=holdouts)
        row = result["candidates"]["sharp"]["horizons"]["1"]["5"]
        self.assertEqual(set(row["splits"]), {"regime", "day_type"})
        self.assertEqual(set(row["splits"]["regime"]), {"a", "b"})
        cell = row["splits"]["regime"]["a"]
        self.assertEqual(cell["flags"]["recall"], 1.0)
        self.assertIn("brier_difference_vs_climatology", cell)
        self.assertIn("realised_minus_predicted", cell)
        held = row["holdouts"]["window"]
        self.assertEqual(held["days"], 31)
        self.assertEqual(held["flags"]["recall"], 1.0)

    def test_the_benchmarks_are_judged_too(self):
        result = Series().judged(lambda h: Series().perfect(h))
        self.assertIn("calendar_climatology", result["candidates"])
        self.assertIn("persistence_logistic", result["candidates"])
        self.assertEqual(result["candidates"]["calendar_climatology"]["role"], "benchmark")
        self.assertFalse(result["candidates"]["calendar_climatology"]["verdict"]["passes"])

    def test_the_result_carries_the_declaration_digest(self):
        series = Series()
        grids, forecasts = series.everything(lambda h: series.perfect(h))
        declaration = _load()
        result = pj.judge(declaration, grids, forecasts, calendar=series.dates)
        self.assertEqual(result["declaration"]["sha256"], declaration.sha256)
        self.assertEqual(result["declaration"]["last_scored_day"], "2025-12-31")
        self.assertEqual(result["mode"], "development")


class InputTests(unittest.TestCase):
    def test_forecasts_are_read_from_a_horizon_document(self):
        document = {
            "horizon": 2,
            "forecasts": {
                "m": {
                    "5": {"2019-01-03": 0.1, "2019-01-02": 0.2},
                    "10": {"2019-01-02": 0.05, "2019-01-03": 0.01},
                }
            },
        }
        (forecast,) = pj.forecasts_from_horizon_document(document)
        self.assertEqual(forecast.horizon, 2)
        self.assertEqual(forecast.dates, (date(2019, 1, 2), date(2019, 1, 3)))
        self.assertEqual(forecast.probabilities[5.0], (0.2, 0.1))
        self.assertEqual(forecast.probabilities[10.0], (0.05, 0.01))

    def test_a_report_becomes_a_forecast_at_its_own_thresholds(self):
        class Report:
            horizon = 3
            scored_dates = (date(2019, 1, 2), date(2019, 1, 3))
            taus = (5.0, 10.0)
            forecast = ((0.3, 0.1), (0.2, 0.05))

        forecast = pj.report_forecast("m", Report)
        self.assertEqual(forecast.horizon, 3)
        self.assertEqual(forecast.probabilities, {5.0: (0.3, 0.2), 10.0: (0.1, 0.05)})

    def test_a_forecast_is_cut_to_the_look_window_with_its_values_unchanged(self):
        forecast = pj.Forecast(
            name="m", horizon=1, dates=(date(2025, 12, 30), date(2026, 1, 2), date(2026, 1, 5)),
            probabilities={5.0: (0.1, 0.2, 0.3), 10.0: (0.01, 0.02, 0.03)},
        )
        cut = pj.restrict_forecast(forecast, date(2026, 1, 1), date(2026, 9, 3))
        self.assertEqual(cut.dates, (date(2026, 1, 2), date(2026, 1, 5)))
        self.assertEqual(cut.probabilities, {5.0: (0.2, 0.3), 10.0: (0.02, 0.03)})

    def test_the_grid_reads_outcomes_onsets_and_the_declared_groupings(self):
        from repo_model.data import DailyObservation
        from repo_model.evaluation_splits import load_split_declaration

        splits = load_split_declaration(Path(__file__).parents[1] / "metadata" / "evaluation_splits.json")
        # Six calm days, then +7 (an onset: nothing above +5 before it) and +8 (not one).
        spreads = [0.0] * 6 + [7.0, 8.0, 11.0]
        days = _weekdays(len(spreads), date(2019, 1, 2))
        rows = [
            DailyObservation(
                day,
                {
                    "sofr": 4.0 + value / 100.0, "iorb": 4.0, "days_to_month_end": 20.0,
                    "quarter_end": 1.0 if k == 6 else 0.0, "tax_date": 0.0,
                    "treasury_settlement_coupons": 1.0 if k == 8 else 0.0,
                },
            )
            for k, (day, value) in enumerate(zip(days, spreads))
        ]
        grid = pj.build_grid(
            _load(groupings=["regime", "scarcity_state", "day_type"]),
            1, rows, days, splits,
            scarcity_state={days[6]: 2.0, days[7]: None},
        )
        # Whole basis points, strictly above: a day on +5 is not above +5.
        self.assertEqual(grid.outcomes[5.0], (0,) * 6 + (1, 1, 1))
        self.assertEqual(grid.outcomes[10.0], (0,) * 8 + (1,))
        self.assertEqual(grid.onset, (0,) * 6 + (1, 0, 0))
        self.assertEqual(grid.groups["scarcity_state"][6:8], ("2", "unknown"))
        self.assertEqual(grid.groups["regime"], ("2018-19",) * 9)
        self.assertEqual(grid.groups["risk_date"], ("0",) * 6 + ("1", "0", "1"))
        with self.assertRaises(ValueError):
            pj.build_grid(
                _load(), 1, rows, [date(2019, 2, 7)], splits, scarcity_state={},
            )


if __name__ == "__main__":
    unittest.main()
