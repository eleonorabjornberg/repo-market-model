"""The per-tail calendar-flag diagnostic of (s3c-ann-net) (#1547): `scripts/calendar_tail_diagnostic_1547.py`.

The tests fix the arithmetic on hand cases: which group a target day belongs to, how a tail is called too thin, too wide or in line, how the
width, shape and location readings follow from the declared rule, how the supported arm follows from the regimes, and the guard that the
quarter-end reference reproduces #1533's section 2b figures, so the study reads the same forecasts and the same statistic.

Recorded mutation (the guard this script adds, `check_reproduction`):

* `check_reproduction`, the test `if abs(mine - theirs) > tolerance:` replaced by `if False:`:
  `test_a_reference_that_differs_from_1533_is_refused` fails with `AssertionError` (`ValueError not raised`); restored, it passes.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("calendar_tail_diagnostic_1547_script", REPO / "scripts" / "calendar_tail_diagnostic_1547.py")
script = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = script
spec.loader.exec_module(script)


def interval(lo, hi):
    return [lo, hi]


class GroupTests(unittest.TestCase):
    def test_a_day_with_two_flags_is_in_both_groups(self):
        names = script.groups_of(["coupon_settlement", "dom_19_23"], "ordinary")
        self.assertEqual(names, ["dom_19_23", "coupon_settlement"])

    def test_no_flag_needs_no_flag_and_no_pressure_type(self):
        self.assertEqual(script.groups_of(["ordinary"], "ordinary"), ["no_flag"])
        self.assertEqual(script.groups_of(["ordinary"], "turn"), [])

    def test_the_quarter_end_flag_is_its_own_group(self):
        self.assertIn("quarter_end_flag", script.groups_of(["quarter_end", "month_end"], "quarter_end_turn"))


class ReadingTests(unittest.TestCase):
    def stats(self, r05, r95, shift=(-0.1, 0.1), diff=(-0.5, 0.5)):
        return {"ratio": {"0.05": r05, "0.95": r95}, "median_z": [0.0] + list(shift), "diff95": [0.0] + list(diff), "reported": ["0.05", "0.95"]}

    def test_a_tail_is_off_only_when_its_interval_excludes_one(self):
        self.assertEqual(script.tail_call([1.5, 2.0, 3.0]), "too thin")
        self.assertEqual(script.tail_call([0.2, 0.4, 0.8]), "too wide")
        self.assertEqual(script.tail_call([1.1, 0.7, 1.6]), "in line")

    def test_both_tails_too_wide_with_a_common_ratio_is_width(self):
        s = self.stats([0.5, 0.2, 0.8], [0.6, 0.3, 0.9])
        self.assertEqual(script.reading(s)["labels"], ["width"])

    def test_sides_that_differ_is_shape_even_when_both_are_off(self):
        s = self.stats([0.5, 0.2, 0.8], [2.0, 1.5, 3.0], diff=(0.5, 2.0))
        self.assertEqual(script.reading(s)["labels"], ["shape"])

    def test_one_tail_off_and_the_difference_open_is_not_separable_from_width(self):
        s = self.stats([1.0, 0.8, 1.2], [2.0, 1.5, 3.0], diff=(-0.2, 2.0))
        self.assertEqual(script.reading(s)["labels"], ["one tail off, not separable from width"])

    def test_a_shift_interval_excluding_zero_is_location_beside_the_rest(self):
        s = self.stats([1.0, 0.8, 1.2], [1.0, 0.8, 1.2], shift=(0.1, 0.4))
        self.assertEqual(script.reading(s)["labels"], ["location"])
        s = self.stats([0.5, 0.2, 0.8], [0.6, 0.3, 0.9], shift=(0.1, 0.4))
        self.assertEqual(script.reading(s)["labels"], ["width", "location"])

    def test_nothing_off_is_in_line(self):
        self.assertEqual(script.reading(self.stats([1.0, 0.8, 1.2], [1.0, 0.8, 1.2]))["labels"], ["in line"])


class ArmTests(unittest.TestCase):
    def test_a_majority_of_regimes_on_the_same_side_supports_it(self):
        self.assertTrue(script.majority_agrees([0.5, 0.6, 1.4], 1.0, -1, 30, [40, 40, 40]))
        self.assertFalse(script.majority_agrees([0.5, 1.6, 1.4], 1.0, -1, 30, [40, 40, 40]))

    def test_a_regime_with_too_few_cells_does_not_vote(self):
        self.assertTrue(script.majority_agrees([0.5, 1.6, 1.4], 1.0, -1, 30, [40, 10, 10]))

    def test_no_regime_with_enough_cells_means_no_support(self):
        self.assertFalse(script.majority_agrees([0.5], 1.0, -1, 30, [10]))


class ReproductionTests(unittest.TestCase):
    def test_a_reference_that_differs_from_1533_is_refused(self):
        mine = {"median_z": 0.19, "ratio": {"0.95": 3.14}}
        theirs = {"median_z": 0.19, "ratio": {"0.95": 3.15}}
        with self.assertRaises(ValueError):
            script.check_reproduction(mine, theirs)
        script.check_reproduction(mine, {"median_z": 0.19, "ratio": {"0.95": 3.14}})


class BootstrapTests(unittest.TestCase):
    def test_the_same_seed_gives_the_same_draws(self):
        cells = [{"t": f"2020-01-{1 + i // 5:02d}", "y": float(i % 7) - 3, "raw": [i * 0.0 + k for k in range(23)], "vec": [0.0] * 16,
                  "event": None, "regime": "r", "h": 1 + i % 5} for i in range(60)]
        a = script.bootstrap(cells, reps=20, seed=5, clustered=False)
        b = script.bootstrap(cells, reps=20, seed=5, clustered=False)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
