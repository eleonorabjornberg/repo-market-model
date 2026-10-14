"""H1 step 3: the benchmarks of scoring protocol v1 on a simulated panel with known dynamics (#762).

`test_protocol_benchmarks.py` reproduces B1 and B2 "by hand" on the published panel, but its
hand computation restates the definition, and `test_scoring_protocol_synthetic.py` never calls
`repo_model.protocol_benchmarks` (finding #744). Here the benchmarks run on a panel simulated
from a declared process (`benchmark_simulation`: an AR(1) spread plus calendar spikes, rows on
the market calendar, the registry's own availability), so a slip inside a benchmark that moves
what it forecasts fails a test whose expected value is known from the process.

**The alignment asserted** (scoring protocol §4 and ruling 6 of #741):

- the anchor is the last public row, the row before the decision day;
- B1 at lead h adds the empirical distribution of h-row changes to the anchor's spread;
- B2 for a target is the empirical distribution of the trailing year's spreads on days of the
  target's own type, the type being the simulator's label of that row.

A degenerate process (a ramp, whose every h-row change is exactly h steps; levels that depend
only on the day type) gives each of these a closed form, so the quantiles are asserted
exactly, at every one of the 23 levels. The AR(1) process gives the same alignment on a
spread that varies, against an independent selection of rows.

**What is measured and not asserted** is the central 90% coverage of each benchmark against
the known truth (`CoverageReportTests` only checks the measurement, on the ideal forecast
whose coverage is 0.90 by construction). The figures and their Monte Carlo intervals are in
`docs/research/benchmark-simulation-762.md`.

Mutation records (each applied alone to `src/repo_model/protocol_benchmarks.py` or
`src/repo_model/richer_targets.py`, the test run, and the line restored):

1. `protocol_benchmarks.b1_forecast`: `panel[s].spread_bps - panel[s - h].spread_bps` replaced by
   `panel[s].spread_bps - panel[s - h - 1].spread_bps` (changes over h + 1 rows). Failed with
   `AssertionError` (a quantile differing from the expected value "within 9 places"):
   `RampTests.test_b1_is_the_anchor_plus_h_steps_at_every_level`,
   `RampTests.test_the_anchor_is_the_row_before_the_decision_day_after_a_weekend_and_a_holiday`,
   `AutoregressiveTests.test_b1_is_the_anchor_plus_the_trailing_two_years_h_row_changes` and
   `CoverageReportTests.test_richer_targets_b1_is_the_same_distribution_as_b1`.
2. `protocol_benchmarks._anchor`: `anchors.add(info.anchor)` replaced by
   `anchors.add(info.anchor + 1)` (the anchor one row late, so B1 starts from the decision
   day's own spread). Failed with `AssertionError`: the same four tests. Neither mutation
   raised `LookAheadError`, since `_require_public` is handed the shifted anchor too.
3. `richer_targets.b1_quantiles`: `values[s] - values[s - h]` replaced by
   `values[s] - values[s - h - 1]`. Failed with `AssertionError`:
   `RampTests.test_richer_targets_b1_adds_h_steps_to_the_anchor` and
   `CoverageReportTests.test_richer_targets_b1_is_the_same_distribution_as_b1`.
"""

from __future__ import annotations

import unittest
from datetime import date

import benchmark_simulation as sim
from repo_model import protocol_benchmarks as pb
from repo_model import richer_targets as rt
from repo_model import scoring_protocol as sp

REGISTRY, SPLITS, DECISION = sim.REGISTRY, sim.SPLITS, sim.DECISION
MEDIAN = sp.GRID.index(0.5)


def decision_rows(rows, step=11):
    """Decision rows with two years behind them and five rows ahead, every `step`-th."""

    first = next(i for i, row in enumerate(rows) if row.date >= date(2020, 1, 2))
    return range(first, len(rows) - 5, step)


class RampTests(unittest.TestCase):
    """On a ramp every h-row change is h steps exactly, so B1 has one value per lead."""

    STEP = 0.1

    @classmethod
    def setUpClass(cls):
        cls.panel = sim.ramp_panel(step=cls.STEP)

    def test_b1_is_the_anchor_plus_h_steps_at_every_level(self):
        for t in decision_rows(self.panel):
            got = pb.b1_forecast(self.panel, t, registry=REGISTRY, decision_time=DECISION)
            anchor = t - 1
            for h in sp.HORIZONS:
                with self.subTest(day=self.panel[t].date, lead=h):
                    expected = self.panel[anchor].spread_bps + self.STEP * h
                    self.assertEqual(len(got[h]), len(sp.GRID))
                    for value in got[h]:
                        self.assertAlmostEqual(value, expected, places=9)

    def test_the_anchor_is_the_row_before_the_decision_day_after_a_weekend_and_a_holiday(self):
        rows = self.panel
        for day in (date(2020, 1, 6), date(2020, 1, 21), date(2020, 7, 6), date(2021, 4, 5)):
            t = [row.date for row in rows].index(day)
            got = pb.b1_forecast(rows, t, registry=REGISTRY, decision_time=DECISION)
            with self.subTest(day=day):
                self.assertLess(rows[t - 1].date, day)
                self.assertAlmostEqual(got[1][MEDIAN], rows[t - 1].spread_bps + self.STEP, places=9)

    def test_richer_targets_b1_adds_h_steps_to_the_anchor(self):
        values = [row.spread_bps for row in self.panel]
        dates = [row.date for row in self.panel]
        for t in decision_rows(self.panel):
            first = sim.first_row_after(dates, sim.years_back(dates[t], 2))
            for h in sp.HORIZONS:
                with self.subTest(day=dates[t], lead=h):
                    got = rt.b1_quantiles(values, dates, t - 1, h, first=first)
                    for value in got:
                        self.assertAlmostEqual(value, values[t - 1] + self.STEP * h, places=9)


class ClimatologyTests(unittest.TestCase):
    """B2 reads the target's own day type, and only rows public at the decision instant."""

    @classmethod
    def setUpClass(cls):
        cls.levels = sim.ProcessSpec().levels
        cls.panel, cls.kinds = sim.level_panel(cls.levels)

    def test_b2_is_the_known_level_of_the_targets_type_at_every_level_and_lead(self):
        seen = set()
        for t in decision_rows(self.panel, step=3):
            got = pb.b2_forecast(self.panel, t, registry=REGISTRY, decision_time=DECISION, splits=SPLITS)
            for h in sp.HORIZONS:
                kind = self.kinds[t + h]
                seen.add(kind)
                with self.subTest(day=self.panel[t].date, lead=h, kind=kind):
                    for value in got[h]:
                        self.assertAlmostEqual(value, self.levels[kind], places=9)
        self.assertEqual(seen, set(self.levels))

    def test_the_simulators_labels_are_the_reporting_day_types(self):
        for row, kind in zip(self.panel, [self.kinds[i] for i in range(len(self.panel))]):
            self.assertEqual(SPLITS.reporting_day_type(row.date, row.values), kind, row.date)


class AutoregressiveTests(unittest.TestCase):
    """The same alignment on a spread that varies, against rows selected another way."""

    @classmethod
    def setUpClass(cls):
        cls.spec = sim.ProcessSpec()
        cls.sample = sim.simulate(cls.spec, seed=762)
        cls.rows = cls.sample.rows

    def test_b1_is_the_anchor_plus_the_trailing_two_years_h_row_changes(self):
        for t in decision_rows(self.rows, step=37):
            got = pb.b1_forecast(self.rows, t, registry=REGISTRY, decision_time=DECISION)
            for h in sp.HORIZONS:
                with self.subTest(day=self.rows[t].date, lead=h):
                    expected = sim.hand_b1(self.sample, t, h)
                    for value, want in zip(got[h], expected):
                        self.assertAlmostEqual(value, want, places=9)

    def test_b2_is_the_trailing_years_same_type_spreads_up_to_the_anchor(self):
        for t in decision_rows(self.rows, step=37):
            got = pb.b2_forecast(self.rows, t, registry=REGISTRY, decision_time=DECISION, splits=SPLITS)
            for h in sp.HORIZONS:
                with self.subTest(day=self.rows[t].date, lead=h):
                    expected = sim.hand_b2(self.sample, t, h)
                    for value, want in zip(got[h], expected):
                        self.assertAlmostEqual(value, want, places=9)

    def test_a_b2_window_that_took_the_decision_days_row_would_differ(self):
        """The check above can tell the anchor from the decision day: on an ordinary day ahead
        of an ordinary target, the sample with the decision day's row differs."""

        t = next(
            i for i in decision_rows(self.rows, step=1)
            if self.sample.kinds[i] == "ordinary" and self.sample.kinds[i + 1] == "ordinary"
        )
        right = sim.hand_b2(self.sample, t, 1)
        wrong = sim.hand_b2(self.sample, t, 1, last=t)
        self.assertNotEqual(right, wrong)


class CoverageReportTests(unittest.TestCase):
    """The coverage measurement itself, not the benchmarks' coverage."""

    def test_the_true_conditional_quantiles_cover_ninety_percent(self):
        spec = sim.ProcessSpec()
        sample = sim.simulate(spec, seed=1)
        for t in decision_rows(sample.rows, step=29):
            for h in sp.HORIZONS:
                quantiles = sim.true_quantiles(sample, t, h)
                with self.subTest(day=sample.rows[t].date, lead=h):
                    self.assertAlmostEqual(sim.exact_coverage(sample, t, h, quantiles), 0.90, places=9)

    def test_a_forecast_shifted_by_a_standard_deviation_covers_less(self):
        spec = sim.ProcessSpec()
        sample = sim.simulate(spec, seed=2)
        t = next(iter(decision_rows(sample.rows)))
        quantiles = [q + sim.true_sd(spec, 1) for q in sim.true_quantiles(sample, t, 1)]
        self.assertLess(sim.exact_coverage(sample, t, 1, quantiles), 0.85)

    def test_the_report_has_every_benchmark_lead_and_an_interval(self):
        report = sim.coverage_report(replicates=2, seed=3, decision_step=60)
        self.assertEqual(set(report), {"B1", "B2", "richer_targets B1"})
        for name, leads in report.items():
            self.assertEqual(set(leads), set(sp.HORIZONS), name)
            for lead, cell in leads.items():
                low, high = cell["exact_interval"]
                self.assertLessEqual(low, cell["exact"], (name, lead))
                self.assertLessEqual(cell["exact"], high, (name, lead))

    def test_richer_targets_b1_is_the_same_distribution_as_b1(self):
        spec = sim.ProcessSpec()
        sample = sim.simulate(spec, seed=4)
        dates = [row.date for row in sample.rows]
        values = [row.spread_bps for row in sample.rows]
        for t in decision_rows(sample.rows, step=97):
            b1 = pb.b1_forecast(sample.rows, t, registry=REGISTRY, decision_time=DECISION)
            first = sim.first_row_after(dates, sim.years_back(dates[t], 2))
            for h in sp.HORIZONS:
                got = rt.b1_quantiles(values, dates, t - 1, h, first=first)
                for a, b in zip(got, b1[h]):
                    self.assertAlmostEqual(a, b, places=9)


if __name__ == "__main__":
    unittest.main()
