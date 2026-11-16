"""The post-month-end location and scale terms on (s3c-ann-net) (#1615): `scripts/post_month_end_terms_1615.py`.

The tests fix the arithmetic on hand cases: which group a target day is in (business day 1 to 3, crossed with the kind of the month-end before it),
how a shrunk shift and a shrunk factor follow from a statistic and the training count, how the three arms transform a forecast (a shift moves every
quantile, a factor moves one side of the median about the shifted median, the identity at 0 and 1 is the same numbers, order is kept, the candidate's
cap is not undone), that a day outside every group is the candidate's, and that the walk-forward fit reads only cells whose target day is before the
decision day.

Recorded mutation (the as-of guard this script adds, `training_before` and `check_asof`):

* `training_before`, the test `if c["t"] < decision_day` replaced by `if c["t"] <= decision_day`:
  `test_a_cell_targeting_the_decision_day_is_not_training` fails with `LookAheadError` (raised by `check_asof` on the filtered set, which now holds a cell
  of the decision day itself); restored, it passes.
* `check_asof`, the test `if c["t"] >= decision_day:` replaced by `if False:`: `test_check_asof_refuses_a_later_cell` fails with `AssertionError`
  (`LookAheadError not raised`); restored, it passes.
"""

from __future__ import annotations

import importlib.util
import math
import sys
import unittest
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
spec = importlib.util.spec_from_file_location("post_month_end_terms_1615_script", REPO / "scripts" / "post_month_end_terms_1615.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model.splits import LookAheadError  # noqa: E402

MID = script.MEDIAN_INDEX


def cell(d, t, h=1, y=0.0, spread=2.0, shift=0.0):
    """A synthetic walk cell: raw quantiles on the 23-level grid, symmetric about `shift`, with q95 - q05 = `spread`; final equal to raw."""

    grid = script.q.GRID
    raw = [shift + (lvl - 0.5) * 2 * spread / 0.9 for lvl in grid]
    return {"d": d, "t": t, "h": h, "y": y, "raw": raw, "q": list(raw)}


class GroupTests(unittest.TestCase):
    def test_business_days_one_to_three_after_a_quarter_end_month_end(self):
        self.assertEqual(script.group_of(date(2024, 10, 1)), "bd1_quarter")
        self.assertEqual(script.group_of(date(2024, 10, 2)), "bd2_quarter")
        self.assertEqual(script.group_of(date(2024, 10, 3)), "bd3_quarter")

    def test_business_days_one_to_three_after_another_month_end(self):
        self.assertEqual(script.group_of(date(2024, 11, 1)), "bd1_other")
        self.assertEqual(script.group_of(date(2024, 11, 4)), "bd2_other")
        self.assertEqual(script.group_of(date(2024, 11, 5)), "bd3_other")

    def test_the_first_market_day_after_a_holiday_new_year_is_business_day_one(self):
        self.assertEqual(script.group_of(date(2024, 1, 2)), "bd1_quarter")

    def test_a_later_business_day_is_outside_every_group(self):
        self.assertIsNone(script.group_of(date(2024, 10, 4)))
        self.assertIsNone(script.group_of(date(2024, 11, 18)))

    def test_all_six_groups_are_declared(self):
        self.assertEqual(sorted(script.GROUPS), ["bd1_other", "bd1_quarter", "bd2_other", "bd2_quarter", "bd3_other", "bd3_quarter"])


class ShrinkageTests(unittest.TestCase):
    def test_the_shift_is_n_over_n_plus_k_times_the_median_error(self):
        self.assertAlmostEqual(script.shrunk_shift(2.0, 100, 100), 1.0)
        self.assertAlmostEqual(script.shrunk_shift(-1.2, 300, 100), -0.9)

    def test_the_factor_is_one_plus_n_over_n_plus_k_times_the_ratio_less_one(self):
        self.assertAlmostEqual(script.shrunk_factor(2.0, 100, 100), 1.5)
        self.assertAlmostEqual(script.shrunk_factor(0.5, 300, 100), 1 + 0.75 * (0.5 - 1))

    def test_too_few_training_cells_leave_the_forecast_alone(self):
        self.assertEqual(script.shrunk_shift(3.0, script.MIN_TRAIN - 1, 100), 0.0)
        self.assertEqual(script.shrunk_factor(3.0, script.MIN_TRAIN - 1, 100), 1.0)

    def test_a_statistic_that_is_not_usable_leaves_the_forecast_alone(self):
        self.assertEqual(script.shrunk_shift(float("nan"), 5000, 100), 0.0)
        self.assertEqual(script.shrunk_factor(0.0, 5000, 100), 1.0)
        self.assertEqual(script.shrunk_factor(float("nan"), 5000, 100), 1.0)
        self.assertEqual(script.shrunk_factor(-2.0, 5000, 100), 1.0)


class ApplyTests(unittest.TestCase):
    def quantiles(self):
        return [float(i - MID) for i in range(23)]

    def test_the_identity_is_the_same_numbers(self):
        q = [x * 0.37 for x in self.quantiles()]
        self.assertEqual(script.apply_terms(q, q, 0.0, 1.0, 1.0), q)

    def test_a_shift_moves_every_quantile_by_the_same_amount(self):
        q = self.quantiles()
        out = script.apply_terms(q, q, 0.75, 1.0, 1.0)
        for a, b in zip(out, q):
            self.assertAlmostEqual(a - b, 0.75)

    def test_a_factor_moves_one_side_about_the_median_and_the_median_not_at_all(self):
        q = self.quantiles()
        out = script.apply_terms(q, q, 0.0, 1.0, 2.0)
        self.assertEqual(out[: MID + 1], q[: MID + 1])
        for i in range(MID + 1, len(q)):
            self.assertAlmostEqual(out[i] - q[MID], 2.0 * (q[i] - q[MID]))
        out = script.apply_terms(q, q, 0.0, 0.5, 1.0)
        self.assertEqual(out[MID:], q[MID:])
        for i in range(MID):
            self.assertAlmostEqual(out[i] - q[MID], 0.5 * (q[i] - q[MID]))

    def test_a_shift_and_a_factor_scale_about_the_shifted_median(self):
        q = self.quantiles()
        out = script.apply_terms(q, q, 1.0, 1.0, 3.0)
        self.assertAlmostEqual(out[MID], q[MID] + 1.0)
        self.assertAlmostEqual(out[MID + 2], q[MID] + 1.0 + 3.0 * (q[MID + 2] - q[MID]))

    def test_the_result_stays_monotone(self):
        q = self.quantiles()
        out = script.apply_terms(q, q, -0.4, 1.7, 0.4)
        self.assertEqual(out, sorted(out))

    def test_the_candidates_cap_is_not_undone(self):
        raw = [float(i) for i in range(23)]
        final = [min(x, 15.0) for x in raw]  # the cap bound from level 15 up
        out = script.apply_terms(final, raw, 2.0, 1.0, 1.5)
        self.assertLessEqual(max(out), 15.0)
        self.assertEqual(out, sorted(out))

    def test_where_the_cap_did_not_bind_the_arm_is_not_capped(self):
        q = [float(i) for i in range(23)]
        out = script.apply_terms(q, q, 5.0, 1.0, 1.0)
        self.assertAlmostEqual(out[-1], 27.0)

    def test_the_arms_use_the_terms_they_declare(self):
        self.assertEqual(script.arm_terms("arm", 0.4, 0.8, 1.3), (0.4, 0.8, 1.3))
        self.assertEqual(script.arm_terms("location", 0.4, 0.8, 1.3), (0.4, 1.0, 1.0))
        self.assertEqual(script.arm_terms("scale", 0.4, 0.8, 1.3), (0.0, 0.8, 1.3))
        with self.assertRaises(ValueError):
            script.arm_terms("other", 0.0, 1.0, 1.0)


class AsOfTests(unittest.TestCase):
    def test_a_cell_targeting_the_decision_day_is_not_training(self):
        cells = [cell("2020-01-01", "2020-01-02"), cell("2020-01-02", "2020-01-03"), cell("2020-01-03", "2020-01-06")]
        got = script.training_before(cells, "2020-01-03")
        self.assertEqual([c["t"] for c in got], ["2020-01-02"])

    def test_check_asof_refuses_a_later_cell(self):
        with self.assertRaises(LookAheadError):
            script.check_asof([cell("2020-01-01", "2020-01-05")], "2020-01-03")

    def test_the_fit_does_not_read_a_cell_that_is_not_before_the_decision_day(self):
        base = [cell("2020-01-01", f"2020-02-{i:02d}", y=0.1 * (i % 7 - 3)) for i in range(1, 28)]
        group_of = lambda c: "bd1_other"  # noqa: E731
        a = script.walk_forward_terms(base, ["2020-03-01"], group_of, k=10, min_train=5)
        later = base + [cell("2020-02-27", "2020-03-01", y=50.0), cell("2020-02-28", "2020-03-02", y=50.0)]
        b = script.walk_forward_terms(later, ["2020-03-01"], group_of, k=10, min_train=5)
        self.assertEqual(a, b)


class FitTests(unittest.TestCase):
    def cells(self, y, spread=2.0, shift=0.0, n=27):
        return [cell("2020-01-01", f"2020-02-{i:02d}", y=y(i), spread=spread, shift=shift) for i in range(1, n + 1)]

    def test_an_outcome_above_the_median_gives_a_positive_shift(self):
        cells = self.cells(lambda i: 1.0)
        terms = script.walk_forward_terms(cells, ["2020-03-01"], lambda c: "bd1_other", k=10, min_train=5)["2020-03-01"]["bd1_other"]
        self.assertAlmostEqual(terms["shift"], 27 / 37 * 1.0)

    def test_an_outcome_below_the_median_gives_a_negative_shift(self):
        cells = self.cells(lambda i: -1.0)
        terms = script.walk_forward_terms(cells, ["2020-03-01"], lambda c: "bd1_other", k=10, min_train=5)["2020-03-01"]["bd1_other"]
        self.assertLess(terms["shift"], 0.0)

    def test_a_wide_realised_spread_widens_and_a_narrow_one_narrows(self):
        wide = self.cells(lambda i: 5.0 * (i - 14) / 13)
        narrow = self.cells(lambda i: 0.1 * (i - 14) / 13)
        w = script.walk_forward_terms(wide, ["2020-03-01"], lambda c: "bd1_other", k=10, min_train=5)["2020-03-01"]["bd1_other"]
        n = script.walk_forward_terms(narrow, ["2020-03-01"], lambda c: "bd1_other", k=10, min_train=5)["2020-03-01"]["bd1_other"]
        self.assertGreater(w["upper"], 1.0)
        self.assertLess(n["upper"], 1.0)
        self.assertGreater(w["lower"], 1.0)

    def test_the_scale_statistic_does_not_depend_on_the_shift(self):
        a = self.cells(lambda i: 0.4 * (i - 14) / 13)
        b = self.cells(lambda i: 0.4 * (i - 14) / 13 + 3.0)
        ta = script.walk_forward_terms(a, ["2020-03-01"], lambda c: "bd1_other", k=10, min_train=5)["2020-03-01"]["bd1_other"]
        tb = script.walk_forward_terms(b, ["2020-03-01"], lambda c: "bd1_other", k=10, min_train=5)["2020-03-01"]["bd1_other"]
        self.assertAlmostEqual(ta["upper"], tb["upper"])
        self.assertAlmostEqual(ta["lower"], tb["lower"])

    def test_a_group_with_too_few_cells_has_the_identity(self):
        cells = self.cells(lambda i: 3.0, n=3)
        terms = script.walk_forward_terms(cells, ["2020-03-01"], lambda c: "bd1_other", k=10, min_train=5)["2020-03-01"]["bd1_other"]
        self.assertEqual((terms["shift"], terms["lower"], terms["upper"]), (0.0, 1.0, 1.0))

    def test_groups_are_fitted_apart(self):
        cells = self.cells(lambda i: 1.0)
        which = lambda c: "bd1_other" if c["t"] < "2020-02-15" else "bd2_other"  # noqa: E731
        out = script.walk_forward_terms(cells, ["2020-03-01"], which, k=1, min_train=3)["2020-03-01"]
        self.assertGreater(out["bd1_other"]["n"], 0)
        self.assertGreater(out["bd2_other"]["n"], 0)
        self.assertEqual(out["bd1_other"]["n"] + out["bd2_other"]["n"], 27)
        self.assertEqual(out["bd3_other"]["n"], 0)


class OutsideTests(unittest.TestCase):
    def test_a_day_outside_the_arm_must_equal_the_candidate(self):
        q = [float(i) for i in range(23)]
        script.check_outside_identical([("2020-01-02", q, q, False)])
        with self.assertRaises(ValueError):
            script.check_outside_identical([("2020-01-02", q, [x + 1e-9 for x in q], False)])

    def test_a_day_in_a_group_may_differ(self):
        q = [float(i) for i in range(23)]
        script.check_outside_identical([("2020-01-02", q, [x * 2 for x in q], True)])


class IntervalTests(unittest.TestCase):
    def test_a_constant_series_has_a_degenerate_interval(self):
        rows = [{"t": f"2020-01-{i:02d}", "v": [1.0, 0.5]} for i in range(1, 21)]
        out = script.bootstrap_means(rows, reps=50, seed=1)
        self.assertAlmostEqual(out[0][0], 1.0)
        self.assertAlmostEqual(out[0][1], 1.0)
        self.assertAlmostEqual(out[0][2], 1.0)
        self.assertTrue(all(math.isfinite(x) for r in out for x in r))

    def test_the_reading_is_loses_at_a_non_positive_mean_and_wins_above_zero(self):
        self.assertEqual(script.verdict_of([-0.01, -0.03, 0.01]), "loses")
        self.assertEqual(script.verdict_of([0.01, -0.01, 0.03]), "undecided")
        self.assertEqual(script.verdict_of([0.02, 0.01, 0.03]), "wins")


class CapCorrectionTests(unittest.TestCase):
    """The 2026 correction (#1630): the arm re-clipped at the candidate's own line at full allotment, `s3c_candidate.cap_arm_quantiles`."""

    FULL_DAY, FULL_TARGET = "2026-03-02", "2026-03-03"

    def arms_above_the_line(self):
        raw = [10.0 + (lvl - 0.5) * 20.0 for lvl in script.q.GRID]
        return {a: script.apply_terms(raw, raw, 0.0, 1.0, 1.5) for a in script.ARMS}, raw

    def test_an_arm_cell_at_full_allotment_comes_out_at_the_line(self):
        arms, _ = self.arms_above_the_line()
        line = script.line_of(self.FULL_DAY, self.FULL_TARGET)
        self.assertIsNotNone(line)
        self.assertGreater(max(arms["arm"]), line)
        capped = script.cap_arms(arms, self.FULL_DAY, self.FULL_TARGET)
        for a in script.ARMS:
            self.assertEqual(max(capped[a]), line)
            self.assertEqual(capped[a], sorted(capped[a]))

    def test_an_arm_cell_before_full_allotment_is_the_arm_itself(self):
        arms, _ = self.arms_above_the_line()
        self.assertIsNone(script.line_of("2025-06-02", "2025-06-03"))
        self.assertEqual(script.cap_arms(arms, "2025-06-02", "2025-06-03"), arms)

    def test_a_breach_counts_cells_and_target_days_above_the_line_and_the_largest_excess(self):
        line = script.line_of(self.FULL_DAY, self.FULL_TARGET)
        low = [line - 5.0] * len(script.q.GRID)
        high = [line - 5.0] * (len(script.q.GRID) - 1) + [line + 4.0]
        higher = [line - 5.0] * (len(script.q.GRID) - 1) + [line + 12.5]
        rows = [(self.FULL_DAY, self.FULL_TARGET, 1, low), (self.FULL_DAY, self.FULL_TARGET, 2, high), (self.FULL_DAY, "2026-03-04", 3, higher),
                ("2026-03-03", "2026-03-04", 1, higher), ("2025-06-02", "2025-06-03", 1, higher)]
        out = script.breaches(rows)
        self.assertEqual(out["full_allotment_cells"], 4)
        self.assertEqual(out["cells_above_the_line"], 3)
        self.assertEqual(out["target_days_above_the_line"], ["2026-03-03", "2026-03-04"])
        self.assertAlmostEqual(out["largest_excess_bp"], 12.5)


if __name__ == "__main__":
    unittest.main()
