"""The episode and pass sensitivity readings (#486): `scripts/episode_sensitivity.py`.

A scratch measurement that re-reads the judge's tier 1 (it moves no figure and writes nothing into `docs/runs/`). The tests
pin the pieces the readings rest on: the onset rule under another label, the episode and its largest day, the margin by
which a miss falls under its cut-off, and the refusal to read a grid whose onsets are not the declared rule's.

Recorded mutations (disposable copy of the tree, control green before and after):

* The declared label rule must reproduce the judge's own onsets. Mutation: in `episode_sensitivity.run`, replace
  `if onset_days(rows, scored, declared_is_event) != tuple(d for d, o in zip(scored, first.onset) if o):` with
  `if False:`. The failing test was `RunTests.test_a_grid_whose_onsets_are_not_the_declared_rule_is_refused`, which
  raised `AssertionError` (`ValueError not raised`).
* A margin is relative to the cut-off, and a missed onset under 10% of it is counted apart. Mutation: in
  `episode_sensitivity.margin_table`, replace `gap = (cut - p) / cut` with `gap = cut - p`. The failing test was
  `MarginTests.test_a_miss_by_more_is_counted_apart`, which raised `AssertionError` (`3 != 0`).
* The readings are built on each horizon's own days (the grids of the horizons start on different days). Mutation: in
  `episode_sensitivity.with_events`, replace `for day in grid.dates)` in the `onset=` line with
  `for day in reversed(grid.dates))`. The failing test was
  `RunTests.test_the_declared_reading_is_the_judges_own_tier_when_the_horizons_start_on_different_days`, which raised
  `AssertionError` (a dict inequality).
* The episode's largest day is by the float spread, the earliest on a tie. Mutation: in `episode_sensitivity.episodes`,
  replace `-row.date.toordinal()` with `row.date.toordinal()`. The failing test was
  `EpisodeTests.test_a_tie_is_broken_by_the_earlier_day`, which raised `AssertionError` (`'2019-01-10' != '2019-01-09'`).
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from dataclasses import replace
from datetime import date
from pathlib import Path

from repo_model import pressure, pressure_judge as pj
from repo_model.data import DailyObservation
from test_pressure_judge import Series, _declaration, _load

ROOT = Path(__file__).resolve().parents[1]


def _script():
    spec = importlib.util.spec_from_file_location("episode_sensitivity_under_test", ROOT / "scripts" / "episode_sensitivity.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["episode_sensitivity_under_test"] = module
    spec.loader.exec_module(module)
    return module


es = _script()


def rows_from(spreads_bp, start=date(2019, 1, 1)):
    from test_pressure_judge import _weekdays

    return [
        DailyObservation(day, {"sofr": 1.0 + bp / 100.0, "iorb": 1.0})
        for day, bp in zip(_weekdays(len(spreads_bp), start), spreads_bp)
    ]


class LabelTests(unittest.TestCase):
    def test_the_declared_rule_rounds_and_the_float_rule_does_not(self):
        # SOFR 2.00 less IORB 1.95 is 5.000000000000004 bp: not above +5 on whole basis points, above it as a float.
        row = DailyObservation(date(2019, 1, 1), {"sofr": 2.00, "iorb": 1.95})
        self.assertGreater(row.spread_bps, 5.0)
        rules = es.label_rules()
        self.assertFalse(rules["declared"][1](row.spread_bps))
        self.assertTrue(rules["float_5"][1](row.spread_bps))

    def test_the_declared_rule_gives_the_panels_own_onsets(self):
        spreads = [0, 0, 0, 0, 0, 0, 6, 7, 0, 0, 0, 0, 0, 0, 0, 8, 0]
        rows = rows_from(spreads)
        scored = [row.date for row in rows]
        self.assertEqual(es.onset_days(rows, scored, es.label_rules()["declared"][1]), pressure.onsets(rows, 5.0, scored))

    def test_a_lower_cut_adds_a_day_on_exactly_five(self):
        rows = rows_from([0] * 6 + [5] + [0] * 6)
        scored = [row.date for row in rows]
        rules = es.label_rules()
        self.assertEqual(es.onset_days(rows, scored, rules["declared"][1]), ())
        self.assertEqual(len(es.onset_days(rows, scored, rules["cut_4.5"][1])), 1)

    def test_the_quiet_days_are_read_off_the_panel_rows_before_the_scored_window(self):
        rows = rows_from([0, 0, 0, 0, 0, 9, 0, 0])
        scored = [row.date for row in rows[5:]]
        self.assertEqual(len(es.onset_days(rows, scored, es.label_rules()["declared"][1])), 1)


class EpisodeTests(unittest.TestCase):
    def test_an_episode_runs_to_the_next_onset_and_its_peak_is_the_largest_day(self):
        spreads = [0] * 6 + [6, 40, 7, 0, 0, 0, 0, 0, 0, 9, 8, 0]
        rows = rows_from(spreads)
        scored = [row.date for row in rows]
        found = es.episodes(rows, scored, es.label_rules()["declared"][1])
        self.assertEqual([e["onset"] for e in found], [rows[6].date.isoformat(), rows[15].date.isoformat()])
        self.assertEqual(found[0]["peak"], rows[7].date.isoformat())
        self.assertEqual(found[0]["peak_spread_bp"], 40.0)
        self.assertEqual(len(found[0]["days"]), 3)
        self.assertEqual(found[1]["peak"], rows[15].date.isoformat())

    def test_a_tie_is_broken_by_the_earlier_day(self):
        rows = rows_from([0] * 6 + [8, 8, 0])
        scored = [row.date for row in rows]
        found = es.episodes(rows, scored, es.label_rules()["declared"][1])
        self.assertEqual(found[0]["peak"], rows[6].date.isoformat())

    def test_days_after_the_last_scored_day_are_not_read(self):
        rows = rows_from([0] * 6 + [6, 0, 0, 0, 0, 0, 0, 60])
        scored = [row.date for row in rows[:10]]
        found = es.episodes(rows, scored, es.label_rules()["declared"][1])
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["peak_spread_bp"], 6.0)


class MarginTests(unittest.TestCase):
    def setUp(self):
        self.declaration = _load()
        self.series = Series(count=60)
        self.grids = {h: self.series.grid(h) for h in (1, 2)}

    def _by_name(self, p, cutoff, horizons=(1, 2)):
        count = len(self.series.dates)
        out = {}
        for h in horizons:
            forecast = self.series.forecast("sharp", h, [p] * count)
            out[h] = replace(
                forecast,
                cutoffs={5.0: (cutoff,) * count, 10.0: (cutoff,) * count},
            )
        return {"sharp": out}

    def test_a_miss_under_ten_percent_of_the_cut_off_is_counted_apart(self):
        table = es.margin_table(self.declaration, "sharp", self.grids, self._by_name(0.46, 0.5))
        onsets = sum(self.series.y5)
        cell = table["any_horizon"]["2019"]
        self.assertEqual(cell["onsets"], onsets)
        self.assertEqual(cell["missed_under_margin"], onsets)
        self.assertEqual(cell["missed_by_more"], 0)
        self.assertEqual(cell["caught"], 0)

    def test_a_miss_by_more_is_counted_apart(self):
        # 0.05 under a cut-off of 0.3 is 17% of it: by more, though under 0.10 in absolute terms.
        table = es.margin_table(self.declaration, "sharp", self.grids, self._by_name(0.25, 0.3))
        cell = table["any_horizon"]["2019"]
        self.assertEqual(cell["missed_under_margin"], 0)
        self.assertEqual(cell["missed_by_more"], sum(self.series.y5))

    def test_a_miss_at_zero_probability_is_counted(self):
        table = es.margin_table(self.declaration, "sharp", self.grids, self._by_name(0.0, 0.5))
        self.assertEqual(table["by_horizon"]["1"]["2019"]["missed_at_zero"], sum(self.series.y5))
        near = es.margin_table(self.declaration, "sharp", self.grids, self._by_name(0.46, 0.5))
        self.assertEqual(near["by_horizon"]["1"]["2019"]["missed_at_zero"], 0)

    def test_an_onset_at_the_cut_off_is_caught(self):
        table = es.margin_table(self.declaration, "sharp", self.grids, self._by_name(0.5, 0.5))
        self.assertEqual(table["any_horizon"]["2019"]["caught"], sum(self.series.y5))

    def test_a_refit_that_flags_nothing_is_a_miss_with_no_margin(self):
        table = es.margin_table(self.declaration, "sharp", self.grids, self._by_name(0.9, float("inf")))
        cell = table["by_horizon"]["1"]["2019"]
        self.assertEqual(cell["no_cutoff"], sum(self.series.y5))
        self.assertEqual(cell["missed_under_margin"] + cell["missed_by_more"], 0)

    def test_an_onset_flagged_at_one_horizon_is_caught_at_any(self):
        by_name = self._by_name(0.46, 0.5)
        count = len(self.series.dates)
        by_name["sharp"][2] = replace(by_name["sharp"][2], cutoffs={5.0: (0.4,) * count, 10.0: (0.4,) * count})
        table = es.margin_table(self.declaration, "sharp", self.grids, by_name)
        self.assertEqual(table["any_horizon"]["2019"]["caught"], sum(self.series.y5))
        self.assertEqual(table["by_horizon"]["1"]["2019"]["caught"], 0)


class RunTests(unittest.TestCase):
    def setUp(self):
        self.declaration = _load()
        self.series = Series(count=120)
        spreads = [11 if y10 else 6 if y5 else 0 for y5, y10 in zip(self.series.y5, self.series.y10)]
        self.rows = [
            DailyObservation(day, {"sofr": 1.0 + bp / 100.0, "iorb": 1.0}) for day, bp in zip(self.series.dates, spreads)
        ]
        # The series marks its first pressure day (row 4) an onset; the panel's rule needs five quiet rows first.
        found = set(pressure.onsets(self.rows, 5.0, self.series.dates))
        flags = tuple(1 if day in found else 0 for day in self.series.dates)
        self.grids = {h: replace(self.series.grid(h), onset=flags) for h in (1, 2)}
        self.onsets = sum(flags)

    def _by_name(self):
        forecasts = []
        for h in (1, 2):
            forecasts.append(self.series.perfect(h))
            forecasts.append(self.series.forecast("calendar_climatology", h, [0.05] * len(self.series.dates)))
            forecasts.append(self.series.forecast("persistence_logistic", h, [0.05] * len(self.series.dates)))
        calendar = list(self.series.dates)
        chosen = pj.choose_cutoffs(self.declaration, self.grids, forecasts, calendar)
        by_name = {}
        for forecast in chosen:
            by_name.setdefault(forecast.name, {})[forecast.horizon] = forecast
        return by_name, calendar

    def test_every_reading_is_produced_for_a_row(self):
        by_name, calendar = self._by_name()
        # Onsets of this series are 20 days apart, further than the quiet days: each is an episode of its own.
        result = es.run(self.declaration, self.rows, self.grids, by_name, calendar, names=("sharp",))
        self.assertEqual(set(result), {"scored", "rows", "events", "margins", "pairing", "labels"})
        self.assertEqual(result["events"]["counts"]["declared_onsets"], self.onsets)
        tier = result["events"]["tier_1"]["sharp"]
        self.assertEqual(set(tier), {"declared_onsets", "episode_peaks", "days_above_10bp"})
        # Each episode is one day, so its peak is its onset.
        self.assertEqual(tier["declared_onsets"]["onsets"], tier["episode_peaks"]["onsets"])
        self.assertEqual(result["labels"]["onsets"]["declared"]["added"], [])
        self.assertEqual(result["labels"]["onsets"]["declared"]["dropped"], [])

    def test_the_declared_reading_is_the_judges_own_tier_when_the_horizons_start_on_different_days(self):
        # The grid of h = 2 starts a day after h = 1's, as the fold grids do: flags are built on each grid's own days.
        first_day = self.series.dates[0]
        by_name, calendar = self._by_name()
        later = {
            name: {h: (pj.restrict_forecast(f, self.series.dates[1], self.series.dates[-1]) if h == 2 else f) for h, f in per.items()}
            for name, per in by_name.items()
        }
        grid2 = self.grids[2]
        self.grids[2] = replace(
            grid2,
            dates=grid2.dates[1:],
            outcomes={tau: v[1:] for tau, v in grid2.outcomes.items()},
            groups={k: v[1:] for k, v in grid2.groups.items()},
            onset=grid2.onset[1:],
            onsets={tau: v[1:] for tau, v in grid2.onsets.items()},
        )
        self.assertNotEqual(self.grids[1].dates[0], self.grids[2].dates[0])
        self.assertEqual(self.grids[1].dates[0], first_day)
        result = es.run(self.declaration, self.rows, self.grids, later, calendar, names=("sharp",))
        judged = es._tier_summary(pj._onset_tier(self.declaration, "sharp", 1, [1, 2], self.grids, later, calendar))
        self.assertEqual(result["events"]["tier_1"]["sharp"]["declared_onsets"], judged)
        # A label that changes nothing gives the same tier as the declared one.
        same = result["labels"]["tier_1"]["cut_5.5"]["sharp"]
        self.assertEqual(same, judged)

    def test_the_paired_and_declared_tests_are_both_reported(self):
        by_name, calendar = self._by_name()
        result = es.run(self.declaration, self.rows, self.grids, by_name, calendar, names=("sharp",))
        pairing = result["pairing"]["sharp"]
        self.assertIn("declared_test_passes", pairing)
        self.assertIn("paired_test_passes", pairing)
        self.assertEqual(
            pairing["paired_test_passes"],
            pairing["recall_difference_lower"] is not None and pairing["recall_difference_lower"] > 0.0,
        )

    def test_a_grid_whose_onsets_are_not_the_declared_rule_is_refused(self):
        by_name, calendar = self._by_name()
        flipped = {h: replace(g, onset=tuple(1 - o for o in g.onset)) for h, g in self.grids.items()}
        with self.assertRaises(ValueError):
            es.run(self.declaration, self.rows, flipped, by_name, calendar, names=("sharp",))

    def test_the_markdown_has_a_table_for_each_reading(self):
        by_name, calendar = self._by_name()
        result = es.run(self.declaration, self.rows, self.grids, by_name, calendar, names=("sharp",))
        text = es.markdown(result)
        for heading in ("Table 1.", "Table 4.", "Table 5.", "Table 6.", "Table 7."):
            self.assertIn(heading, text)


if __name__ == "__main__":
    unittest.main()
