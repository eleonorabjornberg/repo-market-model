"""`repo_model.day_type_scale` (#1402; H5 step 3, development tier): a multiplier on the candidate's residual spread per pressure-day type of the
target day.

Written first, against `metadata/day_type_scale_1402.json`. What these tests pin: the multiplier is the root-mean-square ratio of a type's training
residuals to all training residuals about the pool's median; a type with fewer than the declared minimum of rows, or a refit with no spread, reads
1; the multiplier is clamped to the declared bounds; the pooled mode gives every non-ordinary type one multiplier and leaves ordinary days at 1; a
multiplier of 1 returns the candidate's quantiles element for element and any other keeps their order and moves them away from the pool's median
in proportion; a day is rescaled lead by lead with the type of that lead's target day; a label outside the declared five is a data error; and the
leakage guard below.

Recorded mutation (the guard of this study, #1402): in `repo_model.day_type_scale.multipliers`, the check `if target > anchor:` was changed to
`if target > anchor + 400:`. `LeakageTests.test_a_training_target_after_the_anchor_is_refused` then failed with `AssertionError` (`LookAheadError`
not raised, the row after the anchor went into the ratio); restored, it passes.
"""

from __future__ import annotations

import json
import math
import unittest
from pathlib import Path
from types import SimpleNamespace

from repo_model import day_type_scale as dts
from repo_model import scoring_protocol as sp
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parent.parent
POOL = [(j - 11) / 10.0 for j in range(23)]  # symmetric, median 0.0


def estimate(residuals, targets, pool=POOL):
    return SimpleNamespace(residuals=tuple(residuals), targets=tuple(targets), pool=list(pool))


class DeclarationTests(unittest.TestCase):

    def test_the_declaration_names_what_the_module_has(self):
        declaration = json.loads((ROOT / "metadata" / "day_type_scale_1402.json").read_text(encoding="utf-8"))
        form = declaration["form"]
        self.assertEqual(declaration["issue"], 1402)
        self.assertEqual(tuple(form["types"]), dts.TYPES)
        self.assertEqual(form["minimum_rows"], dts.MIN_ROWS)
        self.assertEqual(tuple(form["bounds"]), dts.BOUNDS)
        self.assertEqual(declaration["amendments"], [])
        self.assertEqual([a["name"] for a in declaration["arms"]][1:], [dts.ARM_NAMES[m] for m in dts.MODES])


class MultiplierTests(unittest.TestCase):

    def labels(self, n_turn, n_ordinary):
        out = {i: "turn" for i in range(n_turn)}
        out.update({n_turn + i: "ordinary" for i in range(n_ordinary)})
        return out

    def test_a_type_twice_as_spread_as_the_whole_pool_reads_its_root_mean_square_ratio(self):
        # 10 turn rows at +-2, 30 ordinary rows at +-1: mean square all = (10*4 + 30*1)/40 = 1.75; turn 4; ordinary 1
        z = [2.0, -2.0] * 5 + [1.0, -1.0] * 15
        labels = self.labels(10, 30)
        m = dts.multipliers(estimate(z, range(40)), labels, anchor=39, mode="typed")
        self.assertAlmostEqual(m["turn"], math.sqrt(4.0 / 1.75))
        self.assertAlmostEqual(m["ordinary"], math.sqrt(1.0 / 1.75))
        self.assertEqual((m["tax_date"], m["year_end"], m["quarter_end_turn"]), (1.0, 1.0, 1.0))  # no rows: fallback

    def test_the_ratio_is_about_the_pools_median_not_zero(self):
        pool = [v + 5.0 for v in POOL]  # median 5.0
        z = [7.0, 3.0] * 5 + [6.0, 4.0] * 15  # about 5: turn +-2, ordinary +-1
        m = dts.multipliers(estimate(z, range(40), pool), self.labels(10, 30), anchor=39, mode="typed")
        self.assertAlmostEqual(m["turn"], math.sqrt(4.0 / 1.75))

    def test_a_type_with_fewer_than_the_minimum_rows_reads_one(self):
        z = [3.0, -3.0] * 4 + [1.0, -1.0] * 16
        m = dts.multipliers(estimate(z, range(40)), self.labels(8, 32), anchor=39, mode="typed")
        self.assertEqual(m["turn"], 1.0)
        self.assertNotEqual(m["ordinary"], 1.0)

    def test_the_minimum_is_inclusive(self):
        z = [3.0, -3.0] * 5 + [1.0, -1.0] * 15
        m = dts.multipliers(estimate(z, range(40)), self.labels(dts.MIN_ROWS, 30), anchor=39, mode="typed")
        self.assertNotEqual(m["turn"], 1.0)

    def test_the_multiplier_is_clamped_to_the_declared_bounds(self):
        z = [100.0, -100.0] * 5 + [0.01, -0.01] * 15
        m = dts.multipliers(estimate(z, range(40)), self.labels(10, 30), anchor=39, mode="typed")
        self.assertEqual(m["ordinary"], dts.BOUNDS[0])
        z = [100.0, -100.0] + [0.01, -0.01] * 19  # two turn rows of forty: the unclamped ratio is sqrt(20)
        m = dts.multipliers(estimate(z, range(40)), self.labels(2, 38), anchor=39, mode="typed", minimum=2)
        self.assertEqual(m["turn"], dts.BOUNDS[1])
        self.assertEqual(m["ordinary"], dts.BOUNDS[0])

    def test_a_pool_with_no_spread_reads_one_everywhere(self):
        m = dts.multipliers(estimate([0.0] * 40, range(40)), self.labels(10, 30), anchor=39, mode="typed")
        self.assertEqual(set(m.values()), {1.0})

    def test_pooled_mode_gives_the_non_ordinary_types_one_multiplier_and_ordinary_none(self):
        z = [2.0, -2.0] * 3 + [3.0, -3.0] * 3 + [1.0, -1.0] * 14  # 6 turn, 6 quarter_end_turn, 28 ordinary
        labels = {i: "turn" for i in range(6)}
        labels.update({6 + i: "quarter_end_turn" for i in range(6)})
        labels.update({12 + i: "ordinary" for i in range(28)})
        m = dts.multipliers(estimate(z, range(40)), labels, anchor=39, mode="pooled")
        non = (6 * 4 + 6 * 9) / 12
        everything = (6 * 4 + 6 * 9 + 28 * 1) / 40
        self.assertAlmostEqual(m["turn"], math.sqrt(non / everything))
        self.assertEqual(m["turn"], m["quarter_end_turn"])
        self.assertEqual(m["tax_date"], m["turn"])
        self.assertEqual(m["ordinary"], 1.0)

    def test_pooled_mode_counts_the_minimum_over_all_non_ordinary_rows(self):
        z = [3.0, -3.0] * 3 + [3.0, -3.0] * 3 + [1.0, -1.0] * 14
        labels = {i: "turn" for i in range(6)}
        labels.update({6 + i: "tax_date" for i in range(6)})
        labels.update({12 + i: "ordinary" for i in range(28)})
        typed = dts.multipliers(estimate(z, range(40)), labels, anchor=39, mode="typed")
        pooled = dts.multipliers(estimate(z, range(40)), labels, anchor=39, mode="pooled")
        self.assertEqual(typed["turn"], 1.0)  # 6 rows each: below the minimum
        self.assertGreater(pooled["turn"], 1.0)  # 12 together

    def test_a_label_outside_the_declared_types_is_a_data_error(self):
        labels = {i: "month_end" for i in range(40)}
        with self.assertRaises(ValueError):
            dts.multipliers(estimate([1.0, -1.0] * 20, range(40)), labels, anchor=39, mode="typed")

    def test_an_unknown_mode_is_refused(self):
        with self.assertRaises(ValueError):
            dts.multipliers(estimate([1.0], [0]), {0: "turn"}, anchor=0, mode="both")

    def test_a_row_without_a_label_is_a_data_error(self):
        with self.assertRaises(ValueError):
            dts.multipliers(estimate([1.0, -1.0], [0, 1]), {0: "turn"}, anchor=1, mode="typed")


class LeakageTests(unittest.TestCase):

    def test_a_training_target_after_the_anchor_is_refused(self):
        z = [1.0, -1.0] * 20 + [1.0]
        labels = {i: "ordinary" for i in range(41)}
        with self.assertRaises(LookAheadError):
            dts.multipliers(estimate(z, range(41)), labels, anchor=39, mode="typed")

    def test_a_target_at_the_anchor_is_allowed(self):
        z = [1.0, -1.0] * 20
        labels = {i: "ordinary" for i in range(40)}
        dts.multipliers(estimate(z, range(40)), labels, anchor=39, mode="typed")


class RescaleTests(unittest.TestCase):

    def quantiles(self, centre=0.3, shift=0.2, scale=2.0):
        return [centre + scale * (shift + v) for v in POOL]

    def test_a_multiplier_of_one_returns_the_quantiles_element_for_element(self):
        q = self.quantiles()
        self.assertEqual(dts.rescaled(q, POOL, 2.0, 1.0), q)

    def test_a_multiplier_moves_the_quantiles_from_the_pools_median_in_proportion(self):
        q = self.quantiles()
        got = dts.rescaled(q, POOL, 2.0, 1.5)
        for j, (a, b) in enumerate(zip(q, got)):
            self.assertAlmostEqual(b - a, 2.0 * 0.5 * POOL[j])
        self.assertEqual(got[sp.GRID.index(0.5)], q[sp.GRID.index(0.5)])  # the median does not move
        self.assertEqual(got, sorted(got))

    def test_the_new_spread_is_the_multiplier_times_the_old(self):
        q = self.quantiles()
        got = dts.rescaled(q, POOL, 2.0, 2.5)
        self.assertAlmostEqual(got[-1] - got[0], 2.5 * (q[-1] - q[0]))

    def test_a_day_is_rescaled_lead_by_lead_with_the_type_of_that_leads_target(self):
        forecast = {h: self.quantiles() for h in sp.HORIZONS}
        estimates = {h: estimate([], [], POOL) for h in sp.HORIZONS}
        multipliers = {h: {t: 1.0 for t in dts.TYPES} for h in sp.HORIZONS}
        multipliers[2]["turn"] = 2.0
        types = {1: "ordinary", 2: "turn", 3: "turn", 4: "ordinary", 5: "tax_date"}
        got = dts.rescale_day(forecast, estimates, multipliers, types, 2.0)
        self.assertEqual(got[1], forecast[1])
        self.assertNotEqual(got[2], forecast[2])
        self.assertEqual(got[3], forecast[3])  # a turn target at a lead whose turn multiplier is 1
        self.assertEqual(got[5], forecast[5])

    def test_the_four_unscaled_types_leave_the_forecast_unchanged_whatever_the_mode(self):
        forecast = {h: self.quantiles() for h in sp.HORIZONS}
        estimates = {h: estimate([], [], POOL) for h in sp.HORIZONS}
        ones = {h: {t: 1.0 for t in dts.TYPES} for h in sp.HORIZONS}
        types = {h: "ordinary" for h in sp.HORIZONS}
        self.assertEqual(dts.rescale_day(forecast, estimates, ones, types, 1.7), forecast)


if __name__ == "__main__":
    unittest.main()
