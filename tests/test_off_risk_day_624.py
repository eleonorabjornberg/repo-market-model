"""Skill on the days that are not risk dates (#624), step 1: the declaration, the climatology and the readers.

Recorded mutations, 12 October 2026, in a disposable copy of `scripts/off_risk_day_624.py`:
1. in `climatology_column`, `pc.past_positions(scored, train_ends, start)` replaced by `range(stop)` (a block's rate is read from days whose
   outcome was not observable at its fit, among them the block's own). `test_a_block_reads_only_outcomes_observable_at_its_fit` then errors
   with `repo_model.splits.LookAheadError` (raised by `group_calibration.fit_floor`, which refuses a pair of a day after the fit).
2. in `climatology_column`, the `if off_risk[i]` filter on the past removed (a risk date's outcome enters the rate of the days that are not risk
   dates). `test_the_rate_is_taken_over_days_that_are_not_risk_dates` then fails with `AssertionError: 0.25 != 0.0`.
3. in `climatology_column`, `if off_risk[index]` on the block's days removed (a risk date is given the rate). `test_a_risk_date_has_no_climatology`
   then fails with `AssertionError: 0.5 is not None`.

Step 2 (the day-level model), same protocol:
4. in `walk_forward_day_model`, `pc.past_positions(scored, train_ends, start)` replaced by `range(stop)` (a block trains on days whose outcome was not
   observable at its fit, among them its own). `test_a_block_is_fitted_on_the_observable_past_only` then errors with
   `repo_model.splits.LookAheadError` (raised by `require_observable_pairs`).
5. in `combine`, the refusal of a non-zero forecast of the row on a day that is not a risk date deleted.
   `test_a_non_zero_forecast_off_the_risk_dates_is_a_defect` then fails with `AssertionError: ValueError not raised`.
6. in `design_rows`, the earlier read `reads[k - CHANGE_DAYS]` replaced by `reads[min(k + 1, len(reads) - 1)]` (the change is formed against the next
   scored day's read, a later decision). `test_the_change_is_the_read_less_the_read_five_scored_days_earlier` then fails with
   `AssertionError: -1.0 != 5.0`.
7. in `trailing_rate_column`, `pc.past_positions(scored, train_ends, start)` replaced by `range(stop)` (a block's rate is read from days whose outcome
   was not observable at its fit). `test_the_rate_reads_only_outcomes_observable_at_the_fit` and the other trailing-rate tests then error with
   `repo_model.splits.LookAheadError` (raised by `require_observable_pairs`).
"""

import importlib.util
import json
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
DECLARED = json.loads((ROOT / "metadata" / "off_risk_day_624_step1.json").read_text())


def _script():
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("off_risk_day_624_script", ROOT / "scripts" / "off_risk_day_624.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["off_risk_day_624_script"] = module
    spec.loader.exec_module(module)
    return module


SCRIPT = _script()


class DeclarationTests(unittest.TestCase):
    def test_the_scoring_ends_before_the_lockbox_and_nothing_is_published(self):
        self.assertLess(DECLARED["scoring"]["last_day"], "2026-01-01")
        self.assertEqual(DECLARED["published"], "nothing")

    def test_the_interval_is_the_judges(self):
        judge = json.loads((ROOT / "metadata" / "pressure_judge.json").read_text())["bootstrap"]
        for key in ("level", "block_length", "replications"):
            self.assertEqual(DECLARED["bootstrap"][key], judge[key])
        self.assertEqual(DECLARED["bootstrap"]["seed"], 624)

    def test_the_rows_are_the_ones_the_directive_names(self):
        self.assertEqual(set(DECLARED["rows"]), set(SCRIPT.ROWS))
        self.assertEqual(SCRIPT.TAU, DECLARED["scoring"]["primary_threshold_bp"])

    def test_the_declared_clip_is_the_scripts(self):
        self.assertIn("1e-4", DECLARED["statistics"]["clip"])
        self.assertEqual(SCRIPT.RELIABILITY_FLOOR, 1e-4)


def days(n, start=date(2018, 1, 1)):
    return [start + timedelta(days=k) for k in range(n)]


class ClimatologyTests(unittest.TestCase):
    def test_a_block_reads_only_outcomes_observable_at_its_fit(self):
        scored = days(8)
        # the second block (days 4 to 7) is fitted at the end of day 1: only days 0 and 1 are observable to it
        train_ends = [scored[0]] * 4 + [scored[1]] * 4
        outcomes = [0, 0, 1, 1, 1, 1, 1, 1]
        column = SCRIPT.climatology_column(outcomes, scored, train_ends, [True] * 8, minimum_pairs=2)
        # the first block has nothing before it; the second sees days 0 and 1 only (the two earlier days 2 and 3 are not observable)
        self.assertEqual(column[:4], [None] * 4)
        self.assertEqual(column[4:], [0.0] * 4)

    def test_the_rate_is_taken_over_days_that_are_not_risk_dates(self):
        scored = days(8)
        train_ends = [scored[0]] * 4 + [scored[3]] * 4
        outcomes = [1, 0, 0, 0, 0, 0, 0, 0]
        off_risk = [False, True, True, True, True, True, True, True]
        column = SCRIPT.climatology_column(outcomes, scored, train_ends, off_risk, minimum_pairs=2)
        self.assertEqual(column[4], 0.0)
        # with the risk date counted the rate would be 0.25
        again = SCRIPT.climatology_column(outcomes, scored, train_ends, [True] * 8, minimum_pairs=2)
        self.assertEqual(again[4], 0.25)

    def test_a_risk_date_has_no_climatology(self):
        scored = days(8)
        train_ends = [scored[0]] * 4 + [scored[3]] * 4
        outcomes = [0, 1, 0, 1, 0, 0, 0, 0]
        off_risk = [True] * 4 + [False] + [True] * 3
        column = SCRIPT.climatology_column(outcomes, scored, train_ends, off_risk, minimum_pairs=2)
        self.assertIsNone(column[4])
        self.assertEqual(column[5], 0.5)

    def test_none_while_too_few_earlier_days_exist(self):
        scored = days(6)
        column = SCRIPT.climatology_column([0, 1, 0, 0, 0, 0], scored, [scored[2]] * 6, [True] * 6, minimum_pairs=60)
        self.assertEqual(column, [None] * 6)

    def test_columns_of_different_lengths_are_refused(self):
        with self.assertRaises(ValueError):
            SCRIPT.climatology_column([0, 1], days(3), days(3), [True] * 3)

    def test_the_fit_refuses_a_pair_after_it(self):
        with self.assertRaises(LookAheadError):
            SCRIPT.gc.fit_floor([(date(2018, 1, 5), 0.0, 1, "")], date(2018, 1, 1), minimum_pairs=1)


class StatisticTests(unittest.TestCase):
    def test_the_brier_skill_is_zero_at_the_reference_and_one_when_perfect(self):
        y = [0, 1, 0, 1]
        ref = [0.5] * 4
        self.assertAlmostEqual(SCRIPT.brier_skill(ref, y, ref), 0.0)
        self.assertAlmostEqual(SCRIPT.brier_skill([0.0, 1.0, 0.0, 1.0], y, ref), 1.0)

    def test_the_brier_skill_is_none_without_days_or_against_a_perfect_reference(self):
        self.assertIsNone(SCRIPT.brier_skill([], [], []))
        self.assertIsNone(SCRIPT.brier_skill([0.5], [1], [1.0]))

    def test_a_calibrated_forecast_has_intercept_zero_and_slope_one(self):
        p = [0.2] * 100 + [0.6] * 100
        y = [1] * 20 + [0] * 80 + [1] * 60 + [0] * 40
        intercept, slope = SCRIPT.reliability(p, y)
        self.assertAlmostEqual(intercept, 0.0, places=6)
        self.assertAlmostEqual(slope, 1.0, places=6)

    def test_a_forecast_that_ranks_nothing_has_slope_zero(self):
        p = [0.2] * 100 + [0.6] * 100
        y = [1] * 40 + [0] * 60 + [1] * 40 + [0] * 60
        intercept, slope = SCRIPT.reliability(p, y)
        self.assertAlmostEqual(slope, 0.0, places=6)

    def test_the_reliability_fit_is_none_when_it_is_undefined(self):
        self.assertIsNone(SCRIPT.reliability([0.3, 0.3], [0, 1]))
        self.assertIsNone(SCRIPT.reliability([0.2, 0.6], [0, 0]))
        self.assertIsNone(SCRIPT.reliability([], []))

    def test_the_cell_counts_the_pressure_days_on_a_zero_forecast(self):
        p = [0.0, 0.0, 0.3, 0.3]
        y = [1, 0, 1, 0]
        cell = SCRIPT.cell_statistics(p, y, [0.5, 0.5, 0.5, 0.5])
        self.assertEqual(cell["days"], 4)
        self.assertEqual(cell["pressure_days"], 2)
        self.assertEqual(cell["positive_days"], 2)
        self.assertEqual(cell["pressure_days_on_zero"], 1)
        self.assertAlmostEqual(cell["auroc"], 0.5)

    def test_the_skill_is_taken_only_where_the_climatology_exists(self):
        cell = SCRIPT.cell_statistics([0.5, 0.5, 0.5], [0, 1, 0], [None, 0.5, 0.5])
        self.assertEqual(cell["skill_days"], 2)
        self.assertAlmostEqual(cell["brier_skill"], 0.0)


class IntervalTests(unittest.TestCase):
    def setUp(self):
        n = 200
        self.y = [1 if (k % 5 == 0 or k % 7 == 3) else 0 for k in range(n)]
        self.p = [0.6 if (k % 5 == 0 or k % 11 == 0) else 0.1 for k in range(n)]
        self.ref = [0.2] * n
        self.cells = {"all": list(range(n)), "first half": list(range(n // 2)), "none": []}

    def run_it(self, **kw):
        base = dict(seed=624, replications=60, block_length=10, level=0.9)
        base.update(kw)
        return SCRIPT.intervals(self.cells, self.p, self.y, self.ref, **base)

    def test_the_interval_of_a_good_ranker_sits_above_chance(self):
        result = self.run_it()
        self.assertGreater(result["all"]["auroc"]["lower"], 0.5)
        self.assertGreater(result["all"]["brier_skill"]["lower"], 0.0)

    def test_the_same_seed_gives_the_same_interval(self):
        self.assertEqual(self.run_it(), self.run_it())
        self.assertNotEqual(self.run_it(), self.run_it(seed=7))

    def test_an_empty_cell_has_no_interval(self):
        self.assertIsNone(self.run_it()["none"]["auroc"])

    def test_a_draw_without_a_class_is_left_out_and_counted(self):
        result = self.run_it(replications=40, block_length=1)
        entry = result["first half"]["auroc"]
        self.assertEqual(entry["draws"] + entry["left_out"], 40)

    def test_the_reliability_is_bootstrapped_for_the_named_cells_only(self):
        result = self.run_it(reliability_cells=("all",))
        self.assertIsNotNone(result["all"]["slope"])
        self.assertIsNone(result["first half"]["slope"])


def rate_fit(kind, xs, labels, served, monotone=None):
    """A stand-in fit: the training rate of pressure days for every served row, and the number of training rows seen."""

    rate_fit.seen.append(len(xs))
    return [sum(labels) / len(labels)] * len(served)


rate_fit.seen = []


class DayModelTests(unittest.TestCase):
    """The walk-forward fit on the days that are not risk dates, with a stand-in estimator."""

    def setUp(self):
        rate_fit.seen = []
        self.scored = days(12)
        # three blocks of four days; a block is fitted at the last day of the block before it
        self.train_ends = [self.scored[0]] * 4 + [self.scored[3]] * 4 + [self.scored[7]] * 4
        self.designs = [[float(k)] for k in range(12)]
        self.outcomes = {5.0: [0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1], 10.0: [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0]}
        self.off_risk = [True] * 12

    def run_it(self, **kw):
        base = dict(kind="logistic", monotone=None, minimum_pairs=2, minimum_events=1, fit=rate_fit)
        base.update(kw)
        return SCRIPT.walk_forward_day_model(
            self.designs, self.outcomes, self.scored, self.train_ends, self.off_risk, **base
        )

    def test_a_block_is_fitted_on_the_observable_past_only(self):
        columns = self.run_it()
        # block 2 (days 4 to 7) sees days 0 to 3 only; block 3 sees days 0 to 7. At +5 bp the rates are 2/4 and 3/8.
        self.assertEqual(columns[5.0][4:8], [0.5] * 4)
        self.assertEqual(columns[5.0][8:], [3 / 8] * 4)
        self.assertEqual(columns[5.0][:4], [0.0] * 4)

    def test_a_pair_after_the_fit_is_refused(self):
        with self.assertRaises(LookAheadError):
            SCRIPT.require_observable_pairs([(self.scored[5], 0.0, 1, "")], self.scored[3])

    def test_only_days_that_are_not_risk_dates_train_and_are_served(self):
        self.off_risk = [True, True, False, True] + [True] * 8
        columns = self.run_it()
        # block 2 trains on days 0, 1 and 3 (day 2 is a risk date): rate 2/3
        self.assertAlmostEqual(columns[5.0][4], 2 / 3)
        self.assertEqual(columns[5.0][2], 0.0)

    def test_a_day_without_a_complete_design_is_not_trained_or_served(self):
        self.designs[1] = None
        self.designs[5] = None
        columns = self.run_it()
        self.assertAlmostEqual(columns[5.0][4], 1 / 3)
        self.assertEqual(columns[5.0][5], 0.0)

    def test_nothing_is_fitted_below_the_minimum_pairs_or_events(self):
        self.assertEqual(self.run_it(minimum_pairs=5)[5.0][4:8], [0.0] * 4)
        self.assertEqual(self.run_it(minimum_events=3)[5.0][4:8], [0.0] * 4)

    def test_a_threshold_with_one_class_in_training_is_left_at_zero(self):
        self.outcomes[10.0] = [0] * 12
        self.assertEqual(self.run_it()[10.0], [0.0] * 12)

    def test_the_curve_across_thresholds_is_non_increasing(self):
        self.outcomes[10.0] = [1] * 12
        columns = SCRIPT.monotone_across_thresholds(self.run_it(), (5.0, 10.0))
        for a, b in zip(columns[5.0], columns[10.0]):
            self.assertLessEqual(b, a)

    def test_the_columns_must_be_one_per_scored_day(self):
        self.designs = self.designs[:-1]
        with self.assertRaises(ValueError):
            self.run_it()


class TrailingRateTests(unittest.TestCase):
    def setUp(self):
        self.scored = days(12)
        self.train_ends = [self.scored[0]] * 4 + [self.scored[3]] * 4 + [self.scored[7]] * 4

    def test_the_rate_is_over_the_most_recent_observable_days_that_are_not_risk_dates(self):
        outcomes = [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        off_risk = [True, True, True, True] + [True] * 8
        column = SCRIPT.trailing_rate_column(outcomes, self.scored, self.train_ends, off_risk, window=3)
        # block 2 sees days 0 to 3: the last three are days 1, 2, 3 (rate 1/3); block 3 sees days 0 to 7: days 5, 6, 7 (rate 0)
        self.assertEqual(column[:4], [None] * 4)
        self.assertEqual(column[4:8], [1 / 3] * 4)
        self.assertEqual(column[8:], [0.0] * 4)

    def test_a_risk_date_is_not_one_of_the_days_the_rate_is_over(self):
        outcomes = [1, 1, 0, 0] + [0] * 8
        off_risk = [True, True, False, True] + [True] * 8
        column = SCRIPT.trailing_rate_column(outcomes, self.scored, self.train_ends, off_risk, window=3)
        self.assertEqual(column[4], 2 / 3)

    def test_nothing_is_read_until_the_window_is_full(self):
        column = SCRIPT.trailing_rate_column([0] * 12, self.scored, self.train_ends, [True] * 12, window=5)
        self.assertEqual(column[4:8], [None] * 4)
        self.assertEqual(column[8:], [0.0] * 4)

    def test_the_rate_reads_only_outcomes_observable_at_the_fit(self):
        outcomes = [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0]
        column = SCRIPT.trailing_rate_column(outcomes, self.scored, self.train_ends, [True] * 12, window=4)
        # block 3 is fitted at the end of day 7: days 4 to 7 are observable, so its rate is 1
        self.assertEqual(column[8], 1.0)
        # block 2 is fitted at the end of day 3 and block 1 had no past: day 4 is not in what block 2 read
        self.assertEqual(column[4], 0.0)


class ExtraColumnTests(unittest.TestCase):
    def setUp(self):
        rate_fit.seen = []
        self.scored = days(12)
        self.train_ends = [self.scored[0]] * 4 + [self.scored[3]] * 4 + [self.scored[7]] * 4
        self.designs = [[float(k)] for k in range(12)]
        self.outcomes = {5.0: [0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1]}
        self.seen_vectors = []

    def fit(self, kind, xs, labels, served, monotone=None):
        self.seen_vectors.append((xs, served))
        return [0.25] * len(served)

    def test_the_threshold_s_column_is_appended_to_each_design_row(self):
        extra = {5.0: [None] * 4 + [0.1 * k for k in range(8)]}
        SCRIPT.walk_forward_day_model(
            self.designs, self.outcomes, self.scored, self.train_ends, [True] * 12, kind="logistic", monotone=None,
            minimum_pairs=1, minimum_events=1, fit=self.fit, extra=extra,
        )
        # the first fit is block 2: it trains on days 0 to 3, none of which has the column, so nothing is fitted; block 3 trains on days 4 to 7
        xs, served = self.seen_vectors[0]
        self.assertEqual(xs, [[4.0, 0.0], [5.0, 0.1], [6.0, 0.2], [7.0, 0.30000000000000004]])
        self.assertEqual(served[0], [8.0, 0.4])
        self.assertEqual(len(self.seen_vectors), 1)

    def test_an_extra_column_of_the_wrong_length_is_refused(self):
        with self.assertRaises(ValueError):
            SCRIPT.walk_forward_day_model(
                self.designs, self.outcomes, self.scored, self.train_ends, [True] * 12, kind="logistic", monotone=None,
                minimum_pairs=1, minimum_events=1, fit=self.fit, extra={5.0: [0.1]},
            )


class CombineTests(unittest.TestCase):
    def test_a_risk_date_keeps_the_rows_forecast_and_the_others_take_the_models(self):
        best = {5.0: [0.4, 0.0, 0.0], 10.0: [0.2, 0.0, 0.0]}
        model = {5.0: [0.9, 0.1, 0.3], 10.0: [0.9, 0.05, 0.1]}
        got = SCRIPT.combine(best, model, [False, True, True], (5.0, 10.0))
        self.assertEqual(got[5.0], [0.4, 0.1, 0.3])
        self.assertEqual(got[10.0], [0.2, 0.05, 0.1])

    def test_a_non_zero_forecast_off_the_risk_dates_is_a_defect(self):
        with self.assertRaises(ValueError):
            SCRIPT.combine({5.0: [0.4]}, {5.0: [0.1]}, [True], (5.0,))


class DesignTests(unittest.TestCase):
    def reads(self, n=8):
        return [
            {SCRIPT.TAIL: float(10 + k), "sofr_p99": 5.0 + 0.1 * k, "sofr_p1": 4.9, SCRIPT.DISTANCE: -0.01 * k} for k in range(n)
        ]

    def test_the_change_is_the_read_less_the_read_five_scored_days_earlier(self):
        design = SCRIPT.design_rows(self.reads(), [3.0] * 8)
        self.assertIsNone(design[4])
        self.assertEqual(design[5][SCRIPT.INPUTS.index("tail_change_5")], 5.0)

    def test_the_dispersion_is_the_99th_less_the_1st_percentile(self):
        design = SCRIPT.design_rows(self.reads(), [3.0] * 8)
        self.assertAlmostEqual(design[6][SCRIPT.INPUTS.index("dispersion_p99_p1")], 0.1 * 6 + 0.1)

    def test_a_hole_in_any_input_or_an_unknown_state_leaves_the_day_out(self):
        reads = self.reads()
        reads[6][SCRIPT.DISTANCE] = None
        design = SCRIPT.design_rows(reads, [3.0] * 5 + [None, 3.0, 3.0])
        self.assertIsNone(design[5])
        self.assertIsNone(design[6])
        self.assertIsNotNone(design[7])

    def test_the_variants_build_their_columns_from_the_same_inputs(self):
        row = [10.0, 5.0, 0.2, -0.01]
        self.assertEqual(SCRIPT.variant_vector("interaction", row, 2.0), row + [2.0] + [x * 2.0 for x in row])
        self.assertEqual(SCRIPT.variant_vector("monotone", row, 2.0), row + [2.0])
        with self.assertRaises(ValueError):
            SCRIPT.variant_vector("other", row, 2.0)


@unittest.skipUnless(importlib.util.find_spec("sklearn") is not None, "needs the ml extra")
class FitTests(unittest.TestCase):
    def test_the_monotone_fit_never_lowers_the_forecast_as_the_state_rises(self):
        from repo_model import ml

        xs = [[k % 7, s] for k in range(210) for s in range(4)]
        labels = [1 if (s >= 2 and k % 3 == 0) or (s < 2 and k % 11 == 0) else 0 for k in range(210) for s in range(4)]
        served = [[3.0, s] for s in range(4)]
        out = ml.fit_off_risk_day_model("gbm_classifier", xs, labels, served, monotone=[0, 1])
        self.assertEqual(out, sorted(out))

    def test_a_fit_on_one_class_is_refused(self):
        from repo_model import ml

        with self.assertRaises(ValueError):
            ml.fit_off_risk_day_model("logistic", [[1.0], [2.0]], [0, 0], [[1.0]])
        with self.assertRaises(ValueError):
            ml.fit_off_risk_day_model("probit", [[1.0], [2.0]], [0, 1], [[1.0]])


if __name__ == "__main__":
    unittest.main()
