"""The pressure-day judge (#375): the declared bar, applied to walk-forward probabilities.

`pressure_judge.judge` reads a declaration (`metadata/pressure_judge.json`), the
shared grid and each candidate's probabilities at +5 and +10 bp, and returns the
bar of #374: recall of at least 70% of the +5 bp days, no more than one false
alarm per true day at the declared cut-off, and a win over calendar-type
climatology at the same recall (paired, 90% stationary bootstrap, Brier and
precision). These tests build small synthetic series so each rule has a known answer.

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
* `require_scored_days` refuses a day after the declared last scored day, even
  in a tier that is open. Mutation: replace `if day > declaration.last_day:` with
  `if False:` in `pressure_judge.require_scored_days`. The failing test was
  `test_refuses_a_day_after_the_declared_last_scored_day`, which raised
  `AssertionError` (`LookAheadError not raised`).
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
        "thresholds_bp": [5, 10],
        "primary_threshold_bp": 5,
        "horizons": [1, 2],
        "pass_horizons": [1, 2],
        "bar": {
            "recall_at_least": 0.7,
            "false_alarms_per_true_at_most": 1.0,
            "level": 0.9,
            "replications": 200,
            "block_length": 5,
            "seed": 375,
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
    """A 400-day series: pressure on every 10th day, climatology flat, a sharp candidate."""

    def __init__(self, count=400, start=date(2019, 1, 1)):
        self.dates = tuple(_weekdays(count, start))
        self.y5 = tuple(1 if k % 10 == 9 else 0 for k in range(count))
        self.y10 = tuple(1 if k % 20 == 19 else 0 for k in range(count))
        self.groups = {
            "regime": tuple("a" if d.year == 2019 else "b" for d in self.dates),
            "day_type": tuple("quarter_end" if k % 10 == 9 else "ordinary" for k, d in enumerate(self.dates)),
        }

    def grid(self, horizon):
        return pj.Grid(
            horizon=horizon,
            dates=self.dates,
            outcomes={5.0: self.y5, 10.0: self.y10},
            groups=self.groups,
            onsets=tuple(d for d, y in zip(self.dates, self.y5) if y),
        )

    def forecast(self, name, horizon, p5, p10=None):
        return pj.Forecast(
            name=name, horizon=horizon, dates=self.dates,
            probabilities={5.0: tuple(p5), 10.0: tuple(p10 if p10 is not None else p5)},
        )

    def perfect(self, horizon, name="sharp"):
        return self.forecast(
            name, horizon,
            [0.9 if y else 0.02 for y in self.y5],
            [0.9 if y else 0.02 for y in self.y10],
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


class DeclarationTests(unittest.TestCase):
    def test_a_valid_declaration_loads_with_its_digest(self):
        declaration = _load()
        self.assertEqual(declaration.horizons, (1, 2))
        self.assertEqual(len(declaration.sha256), 64)
        self.assertEqual(declaration.cutoff("sharp", 5.0, 1), 0.5)

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

    def test_the_tracked_declaration_loads(self):
        declaration = pj.load_declaration()
        self.assertEqual(declaration.last_day, date(2025, 12, 31))
        self.assertIn(declaration.climatology, declaration.candidates)


class GuardTests(unittest.TestCase):
    def test_refuses_a_day_in_a_locked_tier(self):
        # The declared last day is moved past the lockbox's blind tier so only
        # the lockbox can refuse the scored day.
        declaration = _load(scoring={"last_day": "2027-12-31"})
        with self.assertRaises(LookAheadError):
            pj.require_scored_days(declaration, [date(2026, 9, 4)], where="test")

    def test_refuses_a_day_after_the_declared_last_scored_day(self):
        # 2026-02-02 is in the near-blind tier, which is open: only the judge's
        # own declared last day refuses it (#374 scores before 2026-01-01).
        declaration = _load()
        with self.assertRaises(LookAheadError):
            pj.require_scored_days(declaration, [date(2026, 2, 2)], where="test")
        pj.require_scored_days(declaration, [date(2025, 12, 31)], where="test")

    def test_judge_refuses_a_grid_with_a_locked_day(self):
        series = Series(count=40, start=date(2026, 8, 20))
        declaration = _load(scoring={"last_day": "2027-12-31"})
        grids = {h: series.grid(h) for h in (1, 2)}
        forecasts = [
            series.flat(name, h, 0.1)
            for h in (1, 2)
            for name in ("calendar_climatology", "persistence_logistic", "sharp")
        ]
        with self.assertRaises(LookAheadError):
            pj.judge(declaration, grids, forecasts)

    def test_refuses_a_candidate_that_is_not_declared(self):
        series = Series()
        declaration = _load()
        grids, forecasts = series.everything(lambda h: series.perfect(h, name="undeclared"))
        with self.assertRaises(ValueError):
            pj.judge(declaration, grids, forecasts)

    def test_refuses_forecasts_on_other_days_than_the_grid(self):
        series = Series()
        declaration = _load()
        grids, forecasts = series.everything(lambda h: series.perfect(h))
        shifted = forecasts[-1]
        forecasts[-1] = pj.Forecast(
            name=shifted.name, horizon=shifted.horizon,
            dates=shifted.dates[1:] + (shifted.dates[-1] + timedelta(days=3),),
            probabilities=shifted.probabilities,
        )
        with self.assertRaises(ValueError):
            pj.judge(declaration, grids, forecasts)

    def test_refuses_a_probability_outside_zero_one(self):
        series = Series()
        declaration = _load()
        grids, forecasts = series.everything(
            lambda h: series.forecast("sharp", h, [1.2] + [0.1] * (len(series.dates) - 1))
        )
        with self.assertRaises(ValueError):
            pj.judge(declaration, grids, forecasts)

    def test_refuses_a_grid_missing_a_declared_grouping(self):
        series = Series()
        declaration = _load()
        grids, forecasts = series.everything(lambda h: series.perfect(h))
        bare = pj.Grid(
            horizon=1, dates=series.dates, outcomes={5.0: series.y5, 10.0: series.y10},
            groups={"regime": series.groups["regime"]}, onsets=(),
        )
        grids[1] = bare
        with self.assertRaises(ValueError):
            pj.judge(declaration, grids, forecasts)

    def test_refuses_a_run_without_the_declared_climatology(self):
        series = Series()
        declaration = _load()
        grids, forecasts = series.everything(lambda h: series.perfect(h))
        forecasts = [f for f in forecasts if f.name != "calendar_climatology"]
        with self.assertRaises(ValueError):
            pj.judge(declaration, grids, forecasts)


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

    def test_matched_recall_weights_reach_the_target_recall_exactly(self):
        p = [0.9, 0.8, 0.8, 0.8, 0.1, 0.1]
        y = [1, 1, 0, 1, 0, 1]
        weights = pj.matched_recall_weights(p, y, 0.5)
        recall = sum(w * t for w, t in zip(weights, y)) / sum(y)
        self.assertAlmostEqual(recall, 0.5)
        self.assertEqual(weights[0], 1.0)
        self.assertEqual(weights[4], 0.0)
        # The tied group at 0.8 (2 events of 3 days) is flagged in part.
        self.assertTrue(0.0 < weights[1] < 1.0)
        self.assertEqual(weights[1], weights[2])

    def test_a_flat_forecast_is_matched_by_flagging_every_day_in_proportion(self):
        weights = pj.matched_recall_weights([0.1] * 10, [1, 0] * 5, 0.6)
        self.assertTrue(all(abs(w - 0.6) < 1e-12 for w in weights))


class BarTests(unittest.TestCase):
    def test_a_sharp_candidate_passes_the_bar_against_flat_climatology(self):
        series = Series()
        grids, forecasts = series.everything(lambda h: series.perfect(h))
        result = pj.judge(_load(), grids, forecasts)
        row = result["candidates"]["sharp"]["horizons"]["1"]["5"]
        self.assertEqual(row["flags"]["recall"], 1.0)
        self.assertEqual(row["flags"]["precision"], 1.0)
        self.assertEqual(row["flags"]["false_alarms_per_true"], 0.0)
        self.assertTrue(row["bar"]["recall"])
        self.assertTrue(row["bar"]["false_alarms"])
        self.assertTrue(row["bar"]["beats_climatology_brier"])
        self.assertTrue(row["bar"]["beats_climatology_precision"])
        self.assertTrue(row["bar"]["passes"])
        self.assertTrue(result["candidates"]["sharp"]["verdict"]["passes"])
        self.assertEqual(row["auroc"], 1.0)
        self.assertEqual(row["usefulness"]["relative"], 1.0)

    def test_the_cutoff_is_read_from_the_declaration_not_the_scored_days(self):
        series = Series()
        # Probabilities of 0.4 on events: the declared 0.5 flags nothing.
        weak = lambda h: series.forecast(
            "sharp", h, [0.4 if y else 0.02 for y in series.y5]
        )
        grids, forecasts = series.everything(weak)
        row = pj.judge(_load(), grids, forecasts)["candidates"]["sharp"]["horizons"]["1"]["5"]
        self.assertEqual(row["cutoff"], 0.5)
        self.assertEqual(row["flags"]["alarms"], 0)
        self.assertEqual(row["flags"]["recall"], 0.0)
        self.assertFalse(row["bar"]["passes"])
        # The same forecasts under a declared cut-off of 0.3 would flag every event.
        row = pj.judge(
            _load(candidates={**_declaration()["candidates"], "sharp": {
                "role": "candidate", "features": ["x"], "calibration": "none",
                "cutoffs": {"5": 0.3, "10": 0.3}}}),
            grids, forecasts,
        )["candidates"]["sharp"]["horizons"]["1"]["5"]
        self.assertEqual(row["flags"]["recall"], 1.0)

    def test_too_many_false_alarms_fail_the_bar(self):
        series = Series()
        noisy = lambda h: series.forecast(
            "sharp", h, [0.9 if (y or k % 10 in (3, 4, 5)) else 0.02 for k, y in enumerate(series.y5)]
        )
        grids, forecasts = series.everything(noisy)
        row = pj.judge(_load(), grids, forecasts)["candidates"]["sharp"]["horizons"]["1"]["5"]
        self.assertEqual(row["flags"]["recall"], 1.0)
        self.assertAlmostEqual(row["flags"]["false_alarms_per_true"], 3.0)
        self.assertFalse(row["bar"]["false_alarms"])
        self.assertFalse(row["bar"]["passes"])

    def test_a_candidate_that_only_matches_climatology_fails(self):
        series = Series()
        grids, forecasts = series.everything(lambda h: series.flat("sharp", h, 0.1))
        row = pj.judge(_load(), grids, forecasts)["candidates"]["sharp"]["horizons"]["1"]["5"]
        self.assertFalse(row["bar"]["beats_climatology_brier"])
        self.assertFalse(row["bar"]["passes"])

    def test_the_verdict_needs_every_declared_horizon(self):
        series = Series()
        grids, forecasts = series.everything(
            lambda h: series.perfect(h) if h == 1 else series.flat("sharp", h, 0.1)
        )
        verdict = pj.judge(_load(), grids, forecasts)["candidates"]["sharp"]["verdict"]
        self.assertTrue(verdict["by_horizon"]["1"])
        self.assertFalse(verdict["by_horizon"]["2"])
        self.assertFalse(verdict["passes"])

    def test_splits_by_every_declared_grouping_and_the_holdouts(self):
        series = Series()
        grids, forecasts = series.everything(lambda h: series.perfect(h))
        holdouts = {"window": (series.dates[100], series.dates[130])}
        result = pj.judge(_load(), grids, forecasts, holdouts=holdouts)
        row = result["candidates"]["sharp"]["horizons"]["1"]["5"]
        self.assertEqual(set(row["splits"]), {"regime", "day_type"})
        self.assertEqual(set(row["splits"]["regime"]), {"a", "b"})
        cell = row["splits"]["regime"]["a"]
        self.assertEqual(cell["flags"]["recall"], 1.0)
        self.assertIn("brier_difference", cell)
        held = result["candidates"]["sharp"]["horizons"]["1"]["5"]["holdouts"]["window"]
        self.assertEqual(held["days"], 31)
        self.assertEqual(held["flags"]["recall"], 1.0)

    def test_lead_time_is_the_longest_horizon_that_flagged_the_onset(self):
        series = Series()
        # Flags the onset at h = 1 only.
        def candidate(h):
            return series.perfect(h) if h == 1 else series.flat("sharp", h, 0.02)
        grids, forecasts = series.everything(candidate)
        lead = pj.judge(_load(), grids, forecasts)["candidates"]["sharp"]["lead_time"]
        self.assertEqual(lead["onsets"], 40)
        self.assertEqual(lead["flagged"], 40)
        self.assertEqual(lead["mean_lead_days"], 1.0)

    def test_the_benchmarks_are_judged_too(self):
        series = Series()
        grids, forecasts = series.everything(lambda h: series.perfect(h))
        result = pj.judge(_load(), grids, forecasts)
        self.assertIn("calendar_climatology", result["candidates"])
        self.assertIn("persistence_logistic", result["candidates"])
        self.assertEqual(result["candidates"]["calendar_climatology"]["role"], "benchmark")
        self.assertFalse(result["candidates"]["calendar_climatology"]["verdict"]["passes"])

    def test_the_result_carries_the_declaration_digest(self):
        series = Series()
        grids, forecasts = series.everything(lambda h: series.perfect(h))
        declaration = _load()
        result = pj.judge(declaration, grids, forecasts)
        self.assertEqual(result["declaration"]["sha256"], declaration.sha256)
        self.assertEqual(result["declaration"]["last_scored_day"], "2025-12-31")


if __name__ == "__main__":
    unittest.main()
