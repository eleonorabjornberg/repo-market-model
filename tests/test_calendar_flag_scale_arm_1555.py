"""The per-tail calendar-flag scale arm of (s3c-ann-net) (#1555): `scripts/calendar_flag_scale_arm_1555.py`.

The tests fix the arithmetic on hand cases: which arm group a target day is in (and that quarter-end days are in none), how a shrunk multiplier follows
from a ratio and the training count, how a day in two groups is scaled (the geometric mean of its flags' factors), that a scale moves one side of the
median only and is the identity at 1, and that the walk-forward fit reads only cells whose target day is before the decision day.

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
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
spec = importlib.util.spec_from_file_location("calendar_flag_scale_arm_1555_script", REPO / "scripts" / "calendar_flag_scale_arm_1555.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)

from repo_model.splits import LookAheadError  # noqa: E402


class GroupTests(unittest.TestCase):
    def test_flag_groups_overlap(self):
        self.assertEqual(script.arm_groups(["coupon_settlement", "dom_19_23"], "ordinary"), ["dom_19_23", "coupon_settlement"])

    def test_no_flag_needs_no_flag_and_no_pressure_type(self):
        self.assertEqual(script.arm_groups(["ordinary"], "ordinary"), ["no_flag"])
        self.assertEqual(script.arm_groups(["ordinary"], "turn"), [])

    def test_a_quarter_end_day_is_in_no_arm_group(self):
        self.assertEqual(script.arm_groups(["coupon_settlement", "quarter_end"], "quarter_end_turn"), [])
        self.assertEqual(script.arm_groups(["post_month_end_window"], "year_end"), [])
        self.assertEqual(script.arm_groups(["dom_19_23", "quarter_end"], "ordinary"), [])

    def test_a_flag_the_evidence_did_not_support_is_in_no_group(self):
        self.assertEqual(script.arm_groups(["fomc_day"], "ordinary"), [])


class MultiplierTests(unittest.TestCase):
    def test_shrinkage_is_n_over_n_plus_k(self):
        self.assertAlmostEqual(script.multiplier(2.0, 500, 500), 1.5)
        self.assertAlmostEqual(script.multiplier(0.5, 1500, 500), 1 + 0.75 * (0.5 - 1))

    def test_too_few_training_cells_leave_the_forecast_alone(self):
        self.assertEqual(script.multiplier(3.0, script.MIN_TRAIN - 1, 500), 1.0)

    def test_a_ratio_that_is_not_positive_leaves_the_forecast_alone(self):
        self.assertEqual(script.multiplier(0.0, 5000, 500), 1.0)
        self.assertEqual(script.multiplier(float("nan"), 5000, 500), 1.0)


class CombineTests(unittest.TestCase):
    def test_no_factor_is_one(self):
        self.assertEqual(script.combine([]), 1.0)

    def test_one_factor_is_itself(self):
        self.assertAlmostEqual(script.combine([1.67]), 1.67)

    def test_two_factors_combine_by_the_geometric_mean(self):
        self.assertAlmostEqual(script.combine([0.5, 2.0]), 1.0)
        self.assertAlmostEqual(script.combine([4.0, 1.0]), 2.0)


class ScaleTests(unittest.TestCase):
    GRID_LEN = 23

    def quantiles(self):
        return [float(i - 11) for i in range(self.GRID_LEN)]  # median (index 11 of the 23-level grid... see below) is 0

    def test_the_identity_at_one_is_the_same_numbers(self):
        q = [x * 0.37 for x in self.quantiles()]
        self.assertEqual(script.scale_quantiles(q, 1.0, 1.0), q)

    def test_one_side_moves_and_the_median_and_the_other_side_do_not(self):
        q = self.quantiles()
        mid = script.MEDIAN_INDEX
        out = script.scale_quantiles(q, 1.0, 2.0)
        self.assertEqual(out[: mid + 1], q[: mid + 1])
        for i in range(mid + 1, len(q)):
            self.assertAlmostEqual(out[i] - q[mid], 2.0 * (q[i] - q[mid]))
        out = script.scale_quantiles(q, 0.5, 1.0)
        self.assertEqual(out[mid:], q[mid:])
        for i in range(mid):
            self.assertAlmostEqual(out[i] - q[mid], 0.5 * (q[i] - q[mid]))

    def test_the_result_stays_monotone(self):
        q = self.quantiles()
        out = script.scale_quantiles(q, 1.7, 0.4)
        self.assertEqual(out, sorted(out))


def cell(d, t, h=1, y=0.0, spread=2.0):
    """A synthetic walk cell: raw quantiles on the 23-level grid, symmetric about 0, with q95 - q05 = `spread`."""

    grid = script.q.GRID
    raw = [(lvl - 0.5) * 2 * spread / 0.9 for lvl in grid]
    return {"d": d, "t": t, "h": h, "y": y, "raw": raw, "q": list(raw)}


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
        group_of = lambda c: ["dom_19_23"]  # noqa: E731
        a = script.walk_forward_factors(base, ["2020-03-01"], group_of, k=10, min_train=5)
        later = base + [cell("2020-02-27", "2020-03-01", y=50.0), cell("2020-02-28", "2020-03-02", y=50.0)]
        b = script.walk_forward_factors(later, ["2020-03-01"], group_of, k=10, min_train=5)
        self.assertEqual(a, b)

    def test_a_wide_realised_spread_widens_and_a_narrow_one_narrows(self):
        wide = [cell("2020-01-01", f"2020-02-{i:02d}", y=(5.0 if i % 2 else -5.0)) for i in range(1, 28)]
        narrow = [cell("2020-01-01", f"2020-02-{i:02d}", y=(0.1 if i % 2 else -0.1)) for i in range(1, 28)]
        group_of = lambda c: ["dom_19_23"]  # noqa: E731
        w = script.walk_forward_factors(wide, ["2020-03-01"], group_of, k=10, min_train=5)["2020-03-01"]
        n = script.walk_forward_factors(narrow, ["2020-03-01"], group_of, k=10, min_train=5)["2020-03-01"]
        self.assertGreater(w[("dom_19_23", "0.95")], 1.0)
        self.assertLess(n[("dom_19_23", "0.95")], 1.0)
        self.assertGreater(w[("dom_19_23", "0.05")], 1.0)


class OutsideTests(unittest.TestCase):
    def test_a_day_outside_the_arm_must_equal_the_candidate(self):
        q = [float(i) for i in range(23)]
        script.check_outside_identical([("2020-01-02", q, q, False)])
        with self.assertRaises(ValueError):
            script.check_outside_identical([("2020-01-02", q, [x + 1e-9 for x in q], False)])

    def test_a_day_in_the_arm_may_differ(self):
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


if __name__ == "__main__":
    unittest.main()
