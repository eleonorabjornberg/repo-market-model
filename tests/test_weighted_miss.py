"""Weighted miss criteria for the pressure judge (#454): near-miss false alarms count less.

`docs/decisions/weighted-miss.md` records Eleonora's adoption of the rule (#464, 9 October 2026; put in force by #472).
`metadata/weighted_miss.json` declares the weights and the switch (`in_force`, true). The judge's default counts the
weighted false alarms; `--rule unweighted` counts a false alarm as 1, and these tests pin both.

**Recorded mutations** (CLAUDE.md: each new leakage guard carries one that kills it).

* The distance to the nearest pressure day is read on days whose outcome was known at the refit's first decision
  instant only. `false_alarm_weights` refuses a pressure day after `known_through`. Mutation 1: in
  `pressure_judge.false_alarm_weights`, replace `if late:` with `if False:`; the failing tests were
  `test_a_pressure_day_after_the_known_instant_is_refused` and
  `test_a_non_pressure_day_after_the_known_instant_is_refused_too`, which raised `AssertionError`
  (`LookAheadError not raised`).
* The cut-off rule hands `false_alarm_weights` the training window's days alone. Mutation 2: in
  `pressure_judge.choose_cutoffs`, replace `for k in window]` with `for k in range(len(forecast.dates))]` in the
  `false_alarm_weights(...)` call (positions and outcomes of every scored day, including those after the training
  end); six tests in `ChooseCutoffsTests` and `JudgeTests` errored, among them
  `test_a_pressure_day_after_the_training_end_does_not_lower_a_weight` and
  `test_the_cutoff_weights_read_the_training_window_only`, with `LookAheadError` (the guard sees days after
  `known_through`).
"""

from __future__ import annotations

import json
import math
import unittest
from dataclasses import replace
from pathlib import Path

from repo_model import pressure_judge as pj
from repo_model.splits import LookAheadError

from test_pressure_judge import Series, _load, _weekdays

REPO = Path(__file__).resolve().parents[1]
WEIGHTED = REPO / "metadata" / "weighted_miss.json"


def _rule(applied=True):
    """The adopted weights: 0.25 within 2 trading days, 0.5 within 5, else 1."""

    return pj.WeightedMiss(
        path="test", sha256="rule", in_force=False, applied=applied,
        bands=((2, 0.25), (5, 0.5)), beyond=1.0,
    )


class RuleTests(unittest.TestCase):
    def test_the_adopted_weights_by_distance(self):
        rule = _rule()
        got = {d: pj.miss_weight(rule, d) for d in (1, 2, 3, 4, 5, 6, 20)}
        self.assertEqual(got, {1: 0.25, 2: 0.25, 3: 0.5, 4: 0.5, 5: 0.5, 6: 1.0, 20: 1.0})

    def test_no_pressure_day_in_reach_weighs_one(self):
        self.assertEqual(pj.miss_weight(_rule(), None), 1.0)

    def test_distance_zero_is_not_a_false_alarm(self):
        with self.assertRaises(ValueError):
            pj.miss_weight(_rule(), 0)

    def test_the_declaration_file_has_the_adopted_weights_and_the_switch_on(self):
        rule = pj.load_weighted_miss(WEIGHTED)
        self.assertTrue(rule.in_force)
        self.assertTrue(rule.applied)  # the judge's default (`--rule declared`) counts the weighted false alarms
        self.assertEqual(rule.bands, ((2, 0.25), (5, 0.5)))
        self.assertEqual(rule.beyond, 1.0)

    def test_the_unweighted_rule_stays_available_on_request(self):
        rule = pj.load_weighted_miss(WEIGHTED, applied=False)
        self.assertTrue(rule.in_force)  # the declaration is unchanged
        self.assertFalse(rule.applied)  # this run counts every false alarm as 1

    def test_one_declaration_serves_both_thresholds(self):
        # The weights apply at +5 and +10 bp: the judge reads one rule at every threshold it scores.
        declaration = pj.load_declaration()
        self.assertEqual(declaration.thresholds, (5.0, 10.0))
        self.assertTrue(pj.load_weighted_miss(WEIGHTED).applied)

    def test_a_malformed_rule_does_not_load(self):
        document = json.loads(WEIGHTED.read_text())
        for change in (
            {"weights": [{"distance_at_most": 5, "weight": 0.5}, {"distance_at_most": 2, "weight": 0.25}]},
            {"weights": [{"distance_at_most": 2, "weight": 1.5}]},
            {"beyond": 0.0},
            {"in_force": "no"},
        ):
            path = _write_rule({**document, **change})
            with self.subTest(change=change), self.assertRaises(ValueError):
                pj.load_weighted_miss(path)


def _write_rule(document):
    import tempfile

    path = Path(tempfile.mkdtemp()) / "weighted_miss.json"
    path.write_text(json.dumps(document))
    return path


class WeightsTests(unittest.TestCase):
    def test_weights_follow_the_distance_to_the_nearest_known_pressure_day(self):
        positions = list(range(20))
        pressure = [1 if k == 10 else 0 for k in positions]
        got = pj.false_alarm_weights(_rule(), positions=positions, pressure=pressure, known_through=19)
        self.assertEqual(got[10], 0.0)  # a pressure day is not a false alarm
        self.assertEqual([got[k] for k in (9, 11, 8, 12)], [0.25, 0.25, 0.25, 0.25])
        self.assertEqual([got[k] for k in (7, 13, 5, 15)], [0.5, 0.5, 0.5, 0.5])
        self.assertEqual([got[k] for k in (4, 16, 0, 19)], [1.0, 1.0, 1.0, 1.0])

    def test_distance_counts_panel_positions_not_list_places(self):
        # Two scored days a week apart in the panel are 5 trading days apart, not 1.
        got = pj.false_alarm_weights(_rule(), positions=[10, 15], pressure=[1, 0], known_through=15)
        self.assertEqual(got, (0.0, 0.5))

    def test_the_nearer_pressure_day_decides(self):
        positions = list(range(12))
        pressure = [1 if k in (0, 8) else 0 for k in positions]
        got = pj.false_alarm_weights(_rule(), positions=positions, pressure=pressure, known_through=11)
        self.assertEqual(got[6], 0.25)  # 2 from day 8, 6 from day 0
        self.assertEqual(got[3], 0.5)  # 3 from day 0, 5 from day 8

    def test_no_pressure_day_at_all_weighs_every_day_one(self):
        got = pj.false_alarm_weights(_rule(), positions=[0, 1, 2], pressure=[0, 0, 0], known_through=2)
        self.assertEqual(got, (1.0, 1.0, 1.0))

    def test_a_pressure_day_after_the_known_instant_is_refused(self):
        positions = list(range(10))
        pressure = [1 if k == 9 else 0 for k in positions]
        with self.assertRaises(LookAheadError):
            pj.false_alarm_weights(_rule(), positions=positions, pressure=pressure, known_through=8)

    def test_a_non_pressure_day_after_the_known_instant_is_refused_too(self):
        with self.assertRaises(LookAheadError):
            pj.false_alarm_weights(_rule(), positions=[0, 9], pressure=[0, 0], known_through=8)

    def test_series_of_unequal_length_are_refused(self):
        with self.assertRaises(ValueError):
            pj.false_alarm_weights(_rule(), positions=[0, 1], pressure=[0], known_through=1)


class CutoffTests(unittest.TestCase):
    def test_weights_let_a_cutoff_through_that_the_flat_count_refuses(self):
        days = _weekdays(8)
        # One onset at p .5 behind three non-pressure days at .8: 3 false alarms per onset, over the limit of 2.
        p = [0.1, 0.8, 0.8, 0.8, 0.5, 0.1, 0.1, 0.1]
        pressure = [0, 0, 0, 0, 1, 0, 0, 0]
        kwargs = dict(
            days=days, probabilities=p, pressure=pressure, onset=pressure, training_end=days[-1]
        )
        self.assertEqual(pj.select_cutoff(_load(), **kwargs), math.inf)
        weights = pj.false_alarm_weights(
            _rule(), positions=list(range(8)), pressure=pressure, known_through=7
        )
        # Days 1, 2, 3 are 3, 2 and 1 days before the onset: 0.5 + 0.25 + 0.25 = 1.0 per onset.
        self.assertEqual(pj.select_cutoff(_load(), false_alarm_weights=weights, **kwargs), 0.5)

    def test_a_weight_per_day_is_needed(self):
        days = _weekdays(3)
        with self.assertRaises(ValueError):
            pj.select_cutoff(
                _load(), days=days, probabilities=[0.1] * 3, pressure=[0, 0, 1], onset=[0, 0, 1],
                training_end=days[-1], false_alarm_weights=(1.0,),
            )


class ChooseCutoffsTests(unittest.TestCase):
    """Block 1 of a 60-day series starts at day 20; at h = 1 its training window is days 0 to 18."""

    def series(self, pressure_days):
        series = Series(count=60)
        series.y5 = tuple(1 if k in pressure_days else 0 for k in range(60))
        series.y10 = tuple(0 for _ in range(60))
        # Only day 4 is an onset; the other pressure days continue an episode.
        onset = tuple(1 if k == 4 else 0 for k in range(60))
        p = [0.0] * 60
        p[4] = 0.5
        for k in (15, 16, 17):
            p[k] = 0.8
        grid = pj.Grid(
            horizon=1, dates=series.dates, outcomes={5.0: series.y5, 10.0: series.y10},
            groups=series.groups, onset=onset, onsets={5.0: onset, 10.0: series.y10},
        )
        forecast = pj.Forecast(
            name="sharp", horizon=1, dates=series.dates, probabilities={5.0: tuple(p), 10.0: tuple([0.0] * 60)}
        )
        return series, grid, forecast

    def block_one(self, pressure_days, *, weighted):
        series, grid, forecast = self.series(pressure_days)
        declaration = replace(_load(), weighted_miss=_rule(applied=weighted))
        (chosen,) = pj.choose_cutoffs(declaration, {1: grid}, [forecast], series.dates)
        return chosen

    def test_the_flat_count_refuses_three_false_alarms_per_onset(self):
        self.assertTrue(math.isinf(self.block_one({4, 12}, weighted=False).cutoffs[5.0][20]))

    def test_the_weighted_count_takes_the_cutoff_when_the_misses_are_near_a_known_episode(self):
        # Day 12 is a known pressure day: days 15, 16, 17 are 3, 4 and 5 days from it: 3 x 0.5 = 1.5 <= 2.
        chosen = self.block_one({4, 12}, weighted=True)
        self.assertEqual(chosen.cutoffs[5.0][20], 0.5)

    def test_a_pressure_day_after_the_training_end_does_not_lower_a_weight(self):
        # Day 19 is a pressure day, but block 1's training ends on day 18: its outcome is not yet known at the
        # refit's first decision instant, so days 15 to 17 keep weight 1 and the three false alarms count 3.
        chosen = self.block_one({4, 19}, weighted=True)
        self.assertTrue(math.isinf(chosen.cutoffs[5.0][20]))

    def test_the_cutoff_weights_read_the_training_window_only(self):
        # Moving a later pressure day (after the window) changes nothing in the block's cut-off.
        a = self.block_one({4, 19}, weighted=True).cutoffs[5.0][20]
        b = self.block_one({4, 25}, weighted=True).cutoffs[5.0][20]
        self.assertEqual(a, b)

    def test_the_weighting_is_stamped_on_the_forecast(self):
        self.assertEqual(self.block_one({4, 12}, weighted=True).cutoff_weighting, "rule")
        self.assertIsNone(self.block_one({4, 12}, weighted=False).cutoff_weighting)


class JudgeTests(unittest.TestCase):
    """End to end on `Series`: a pressure day (and onset) every 20th day, k = 4, 24, ...

    The candidate flags each onset and five non-pressure days around it: k % 20 in 1, 2, 3 (3, 2 and 1 days before)
    and 5, 6 (1 and 2 days after). Flat, that is 5 false alarms per onset; weighted, 0.5 + 0.25 + 0.25 + 0.25 +
    0.25 = 1.5.
    """

    def judged(self, **options):
        series = Series()
        near = {1, 2, 3, 4, 5, 6}
        candidate = lambda h: series.forecast(
            "sharp", h, [1.0 if k % 20 in near else 0.0 for k in range(len(series.dates))]
        )
        grids, forecasts = series.everything(candidate)
        declaration = _load()
        rule = options.pop("rule", None)
        if rule is not None:
            declaration = replace(declaration, weighted_miss=rule)
        return pj.judge(declaration, grids, forecasts, calendar=series.dates)["candidates"]["sharp"]

    def near(self, sharp):
        return sharp["tiers"]["onset_warning"]["lead_at_least_1"]

    def test_with_no_rule_loaded_nothing_new_is_reported(self):
        near = self.near(self.judged())
        self.assertNotIn("weighted_false_alarms_by_horizon", near)
        self.assertNotIn("worst_weighted_false_alarms_per_onset", near)
        self.assertEqual(near["onsets_flagged"], 0)  # the flat rule mutes it: 5 false alarms per onset

    def test_a_rule_that_is_loaded_but_not_applied_reports_the_weighted_count_and_changes_nothing(self):
        flat = self.near(self.judged())
        reported = self.near(self.judged(rule=_rule(applied=False)))
        self.assertEqual(reported["onsets_flagged"], flat["onsets_flagged"])
        self.assertEqual(reported["criteria"], flat["criteria"])
        self.assertIn("weighted_false_alarms_by_horizon", reported)
        self.assertFalse(reported["weighted_miss_applied"])

    def test_the_applied_rule_flags_it_and_counts_the_weighted_misses(self):
        near = self.near(self.judged(rule=_rule(applied=True)))
        self.assertTrue(near["weighted_miss_applied"])
        self.assertEqual(near["onsets_flagged"], 19)
        # Blocks 1 to 19 flag; each has 5 false alarms (flat) of weight 1.5, over 20 onsets.
        self.assertAlmostEqual(near["worst_false_alarms_per_onset"], 95 / 20)
        self.assertAlmostEqual(near["worst_weighted_false_alarms_per_onset"], 28.5 / 20)
        self.assertTrue(near["criteria"]["false_alarms"])

    def test_the_tier_limit_is_read_on_the_weighted_count_when_applied(self):
        near = self.near(self.judged(rule=_rule(applied=True)))
        # The flat count is still reported, and is over the limit of 2; the weighted count is not.
        self.assertGreater(near["worst_false_alarms_per_onset"], 2.0)
        self.assertLessEqual(near["worst_weighted_false_alarms_per_onset"], 2.0)
        self.assertTrue(near["criteria"]["false_alarms"])


class RegimeSplitTests(unittest.TestCase):
    """The tier-1 evidence under the rule is split by regime: it sums to the whole."""

    def test_the_regime_split_sums_to_the_totals(self):
        judged = JudgeTests().judged(rule=_rule(applied=True))
        near = judged["tiers"]["onset_warning"]["lead_at_least_1"]
        split = near["by_regime"]
        self.assertEqual(set(split), {"a", "b"})  # `Series`: regime "a" is 2019, "b" the rest
        self.assertEqual(sum(r["onsets"] for r in split.values()), near["onsets"])
        self.assertEqual(sum(r["onsets_flagged"] for r in split.values()), near["onsets_flagged"])
        for h in ("1", "2"):
            self.assertEqual(
                sum(r["false_alarms_by_horizon"][h]["flat"] for r in split.values()),
                near["false_alarms_by_horizon"][h]["false_alarms"],
            )
            self.assertAlmostEqual(
                sum(r["false_alarms_by_horizon"][h]["weighted"] for r in split.values()),
                near["weighted_false_alarms_by_horizon"][h]["false_alarms"],
            )

    def test_no_split_without_a_rule(self):
        near = JudgeTests().judged()["tiers"]["onset_warning"]["lead_at_least_1"]
        self.assertNotIn("by_regime", near)


def _script():
    import importlib.util

    spec = importlib.util.spec_from_file_location("weighted_miss_script", REPO / "scripts" / "weighted_miss.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TableTests(unittest.TestCase):
    """`scripts/weighted_miss.py table`: one row per candidate, the two rules side by side."""

    def runs(self):
        series = Series()
        near = {1, 2, 3, 4, 5, 6}
        candidate = lambda h: series.forecast(
            "sharp", h, [1.0 if k % 20 in near else 0.0 for k in range(len(series.dates))]
        )

        def run(applied):
            grids, forecasts = series.everything(candidate)
            declaration = replace(_load(), weighted_miss=_rule(applied=applied))
            forecasts = pj.choose_cutoffs(declaration, grids, forecasts, series.dates)
            result = pj.judge(declaration, grids, forecasts, calendar=series.dates)
            return json.loads(json.dumps(result))

        return run(False), run(True)

    def test_the_table_reads_both_runs(self):
        flat, weighted = self.runs()
        text = _script().table(flat, weighted)
        row = next(line for line in text.splitlines() if line.startswith("| sharp |"))
        cells = [c.strip() for c in row.strip("|").split("|")]
        self.assertEqual(cells[1:4], ["20", "0", "19"])  # onsets; warned under the flat rule, under the weighted
        self.assertEqual(cells[6:8], ["fail", "pass"])  # tier 1 under each rule
        self.assertIn("| sharp | weighted | a |", text)  # the regime split

    def test_the_runs_must_be_given_in_order(self):
        flat, weighted = self.runs()
        with self.assertRaises(SystemExit):
            _script().table(weighted, flat)

    def test_a_confirmation_result_is_refused(self):
        flat, _ = self.runs()
        flat["mode"] = "confirmation"
        path = _write_rule(flat)
        with self.assertRaises(SystemExit):
            _script()._read(path)


class GuardTests(unittest.TestCase):
    def test_refuses_cutoffs_chosen_under_another_weighting(self):
        series = Series(count=60)
        grids = {h: series.grid(h) for h in (1, 2)}
        declaration = _load()
        forecasts = []
        for h in (1, 2):
            for name, level in (("calendar_climatology", 0.1), ("persistence_logistic", 0.1), ("sharp", 0.1)):
                forecasts.append(series.flat(name, h, level))
        flat = pj.choose_cutoffs(declaration, grids, forecasts, series.dates)
        applied = replace(declaration, weighted_miss=_rule(applied=True))
        with self.assertRaises(ValueError):
            pj.judge(applied, grids, flat, calendar=series.dates)


if __name__ == "__main__":
    unittest.main()
