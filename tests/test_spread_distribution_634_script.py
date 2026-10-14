"""The measurement script of #634 (`scripts/spread_distribution_634.py`): the parts that decide what is scored.

Recorded mutation (the one guard this script adds; the scorer's own lockbox guard is tested with the scorer):

* `refuse_locked`, the call `require_unlocked(list(days), ...)` replaced by `return`: `test_a_locked_day_is_refused`
  fails with `AssertionError` (`LookAheadError not raised`; the blind tier is every day after 2026-09-03, `metadata/lockbox.json`).
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("spread_distribution_634_script", REPO / "scripts" / "spread_distribution_634.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model import scoring_protocol as sp  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402


def business_days(start: date, count: int):
    days, day = [], start
    while len(days) < count:
        if day.weekday() < 5:
            days.append(day)
        day += timedelta(days=1)
    return days


class LeadForecastTests(unittest.TestCase):
    def setUp(self):
        self.calendar = business_days(date(2024, 3, 1), 12)

    def laws(self, targets_by_lead):
        return {h: {self.calendar[i]: [float(h * 100 + i)] * len(sp.GRID) for i in targets_by_lead[h]} for h in sp.HORIZONS}

    def test_a_decision_day_takes_the_law_of_the_target_h_days_later(self):
        laws = self.laws({h: range(h, 12) for h in sp.HORIZONS})
        forecasts, days = script.lead_forecasts(laws, self.calendar)
        self.assertEqual(days[0], self.calendar[0])
        for h in sp.HORIZONS:
            self.assertEqual(forecasts[self.calendar[0]][h][0], h * 100 + h)
            self.assertEqual(forecasts[self.calendar[2]][h][0], h * 100 + 2 + h)

    def test_only_the_days_every_lead_covers_are_decision_days(self):
        laws = self.laws({1: range(1, 12), 2: range(2, 12), 3: range(3, 12), 4: range(4, 12), 5: range(5, 11)})
        _forecasts, days = script.lead_forecasts(laws, self.calendar)
        # lead 5 starts at target 5 (decision day 0) and ends at target 10 (decision day 5)
        self.assertEqual(days, self.calendar[0:6])

    def test_a_missing_law_is_kept_as_missing_not_dropped(self):
        laws = self.laws({h: range(h, 12) for h in sp.HORIZONS})
        laws[3][self.calendar[3]] = None
        forecasts, days = script.lead_forecasts(laws, self.calendar)
        self.assertIn(self.calendar[0], days)
        self.assertIsNone(forecasts[self.calendar[0]][3])

    def test_a_target_off_the_calendar_is_refused(self):
        laws = self.laws({h: range(h, 12) for h in sp.HORIZONS})
        laws[1][date(2030, 1, 2)] = [0.0] * len(sp.GRID)
        with self.assertRaises(ValueError):
            script.lead_forecasts(laws, self.calendar)


class ScoreCellTests(unittest.TestCase):
    def test_cells_drop_targets_without_an_outcome_and_day_means_average_the_admitted_leads(self):
        calendar = business_days(date(2024, 3, 1), 12)
        flat = [0.0] * len(sp.GRID)
        forecasts = {calendar[0]: {h: flat for h in sp.HORIZONS}}
        outcomes = {calendar[h]: float(h) for h in sp.HORIZONS}
        outcomes[calendar[3]] = None
        cells = script.cell_scores(forecasts, outcomes, calendar, sp.grid_crps)
        self.assertEqual(sorted(h for _d, h in cells), [1, 2, 4, 5])
        mean_all = script.day_means(cells, lambda d, h: True)[calendar[0]]
        self.assertAlmostEqual(mean_all, sum(cells.values()) / 4.0)
        only_even = script.day_means(cells, lambda d, h: h % 2 == 0)
        self.assertAlmostEqual(only_even[calendar[0]], (cells[(calendar[0], 2)] + cells[(calendar[0], 4)]) / 2.0)
        self.assertEqual(script.day_means(cells, lambda d, h: False), {})


class OnGridTests(unittest.TestCase):
    LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]
    LAW = [-6.0, -3.0, -1.0, 0.0, 4.0]

    def test_the_law_returns_its_own_quantiles_at_its_own_levels(self):
        out = script.on_grid(self.LAW, self.LEVELS)
        for level, value in zip(self.LEVELS, self.LAW):
            self.assertAlmostEqual(out[sp.GRID.index(level)], value, places=4)

    def test_the_result_is_on_the_protocols_grid_and_ordered_with_tails_outside_the_fitted_ones(self):
        out = script.on_grid(self.LAW, self.LEVELS)
        self.assertEqual(len(out), len(sp.GRID))
        self.assertEqual(out, sorted(out))
        self.assertLess(out[0], self.LAW[0])
        self.assertGreater(out[-1], self.LAW[-1])


class FiveLevelTests(unittest.TestCase):
    """B3 is scored on its own five levels, as a secondary benchmark (Eleonora, #660 and #700): no placement on the grid."""

    def test_a_grid_law_is_read_at_the_five_published_levels_exactly(self):
        law = [float(k) for k in range(len(sp.GRID))]
        five = script.five_levels(law)
        self.assertEqual(five, [law[sp.GRID.index(level)] for level in script.REPORT_LEVELS])

    def test_a_five_level_law_is_kept_as_it_is(self):
        law = [-6.0, -3.0, -1.0, 0.0, 4.0]
        self.assertEqual(script.five_levels(law), law)

    def test_any_other_length_is_refused(self):
        with self.assertRaises(ValueError):
            script.five_levels([0.0] * 7)

    def test_the_five_level_score_is_twice_the_mean_pinball_over_the_five_levels(self):
        law = [-6.0, -3.0, -1.0, 0.0, 4.0]
        expected = 2.0 * sum(script.pinball(level, q, 1.5) for level, q in zip(script.REPORT_LEVELS, law)) / 5.0
        self.assertAlmostEqual(script.five_crps(law, 1.5), expected)

    def test_the_five_level_upper_tail_score_floors_both_at_zero_bp(self):
        law = [-6.0, -3.0, -1.0, 0.0, 4.0]
        self.assertAlmostEqual(script.five_twcrps(law, -2.0), script.five_crps([max(q, 0.0) for q in law], 0.0))


class LockboxTests(unittest.TestCase):
    def test_a_locked_day_is_refused(self):
        with self.assertRaises(LookAheadError):
            script.refuse_locked([date(2025, 12, 31), date(2026, 9, 10)])
        script.refuse_locked([date(2025, 12, 30), date(2025, 12, 31)])


class ExceedanceTests(unittest.TestCase):
    def setUp(self):
        if importlib.util.find_spec("numpy") is None:  # pragma: no cover - the ml extra is optional
            self.skipTest("the ml extra is not installed")

    def test_a_law_wholly_below_the_threshold_has_a_small_exceedance_and_the_reading_falls_with_the_threshold(self):
        law = [-8.0 + 0.5 * k for k in range(len(sp.GRID))]
        probabilities = [script.exceedance(law, tau) for tau in script.THRESHOLDS_BP]
        self.assertEqual(probabilities, sorted(probabilities, reverse=True))
        self.assertTrue(all(0.0 <= p <= 1.0 for p in probabilities))
        self.assertEqual(script.brier(0.25, True), 0.5625)
        self.assertEqual(script.brier(0.25, False), 0.0625)


class ResumeTests(unittest.TestCase):
    """A walk takes hours; a finished one is kept, so a later run resumes from the walks already written."""

    def setUp(self):
        import tempfile

        self.tmp = Path(tempfile.mkdtemp())
        self.published = self.tmp / "published.csv"
        self.panel = self.tmp / "panel.csv"
        self.published.write_text("date,spread_bps\n", encoding="utf-8")
        self.panel.write_text("date,spread_bps,extra\n", encoding="utf-8")
        self.output = self.tmp / "b_gbm_new_h2.json"

    def tearDown(self):
        import shutil

        shutil.rmtree(self.tmp)

    def write(self, **changes):
        document = {
            "variant": "b_gbm_new",
            "horizon": 2,
            "panel_sha256": script.panel_sha256(self.published),
            "scratch_panel_sha256": script.panel_sha256(self.panel),
            "laws": {"2019-01-02": [0.0]},
        }
        document.update(changes)
        self.output.write_text(script.json.dumps(document), encoding="utf-8")

    def finished(self, variant="b_gbm_new", horizon=2):
        return script.finished_walk(self.output, variant=variant, horizon=horizon, published=self.published, panel=self.panel)

    def test_a_walk_of_the_same_variant_lead_and_panels_is_finished(self):
        self.write()
        self.assertTrue(self.finished())

    def test_no_file_or_an_unreadable_one_is_not_finished(self):
        self.assertFalse(self.finished())
        self.output.write_text('{"variant": "b_gbm', encoding="utf-8")
        self.assertFalse(self.finished())

    def test_another_variant_lead_or_panel_is_not_finished(self):
        self.write()
        self.assertFalse(self.finished(variant="c_two_part_new"))
        self.assertFalse(self.finished(horizon=3))
        self.write(panel_sha256="0" * 64)
        self.assertFalse(self.finished())
        self.write(scratch_panel_sha256="0" * 64)
        self.assertFalse(self.finished())

    def test_a_control_ignores_the_scratch_panel(self):
        self.write(variant="published", scratch_panel_sha256=None)
        self.assertTrue(self.finished(variant="published"))

    def test_the_walk_command_skips_a_finished_walk_without_reading_the_panels(self):
        self.write()
        args = script.argparse.Namespace(variant="b_gbm_new", horizon=2, published=self.published, panel=self.panel, output=self.output)
        before = self.output.read_text(encoding="utf-8")
        self.assertEqual(script.walk_command(args), 0)
        self.assertEqual(self.output.read_text(encoding="utf-8"), before)


class SummaryTests(unittest.TestCase):
    """The reported interval is the scorer's own: studentized at both ends (Eleonora's ruling on #660, item 1)."""

    def test_both_skill_bounds_are_the_studentized_ones(self):
        import random

        rng = random.Random(1)
        days = business_days(date(2020, 1, 1), 120)
        benchmark = {day: 2.0 + rng.random() for day in days}
        candidate = {day: benchmark[day] - 0.2 + 0.5 * rng.random() for day in days}
        (test,) = sp.paired_tests([(benchmark, candidate)], seed=7, draws=400)
        row = script.summarise(test)
        studentized_lower = test.skill - sp._bound(test.skill_t_draws, 1.0 - test.alpha, test.draws) * test.skill_standard_error
        self.assertAlmostEqual(row["skill_lower_95_one_sided"], studentized_lower)
        self.assertAlmostEqual(row["skill_upper_95_one_sided"], test.upper_skill())
        self.assertLess(row["skill_lower_95_one_sided"], test.skill)
        self.assertGreater(row["skill_upper_95_one_sided"], test.skill)


if __name__ == "__main__":
    unittest.main()
