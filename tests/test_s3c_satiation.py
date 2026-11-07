"""The satiation distance as an extra term of (s3c-ann-net) (#1507; H5 step 2 follow-up, development tier).

`repo_model.s3c_satiation.SatiationTable` serves `satiation_dist_roll` / `satiation_hinge_roll` (#598) to `spread_mr_state_calendar` as the extra terms
`satiation_dist` / `satiation_hinge`, in percentage points. Pinned on hand cases: the value a training pair reads is the column at its decision row
(`target row - lead`, the direct pair); a forecast reads the column at its own decision row whatever the lead; a hole serves nothing to a forecast and is
an error for a training pair; the units; **no later row moves a value served to an earlier decision** (the criterion: perturb every row after the decision
and the served value is unchanged); the fit enters the new names as the extras it already reads (they are in `EXTRA_TERMS`, so the pool is the residual
after the term) and a fit with the term recovers a known slope.

**Recorded mutation** (7 November 2026), in `SatiationTable.read` (a forecast reads its own decision row): the line

    value = self._value(decision_index)

was changed to `value = self._value(decision_index + lead)` (the value at the target row). `FutureTests.test_a_later_row_does_not_move_a_served_value`
then failed with `AssertionError: {'satiation_dist': 3.0} != {'satiation_dist': 900.0}` (the served value moved when rows after the decision row changed), and
`AlignmentTests.test_a_forecast_reads_its_own_decision_rows_value` with `AssertionError: {'satiation_dist': 3.0} != {'satiation_dist': 2.0}`; restored, they pass. The column's own no-look-ahead guard (`satiation.check_distance_no_future`) and its mutations are #598's
(`tests/test_satiation_distance.py`).
"""

from __future__ import annotations

import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model import s3c_satiation, satiation, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.data import DailyObservation  # noqa: E402


def rows(dist, hinge=None):
    """Panel rows from `dist` (ratio units; `None` is a hole), `hinge` in percentage points."""

    hinge = [None if d is None else max(0.0, -100.0 * d) for d in dist] if hinge is None else hinge
    day, out = date(2026, 3, 2), []
    for d, h in zip(dist, hinge):
        while day.weekday() >= 5:
            day += timedelta(days=1)
        out.append(DailyObservation(day, {satiation.DISTANCE_COLUMN: d, satiation.HINGE_COLUMN: h}))
        day += timedelta(days=1)
    return out


class AlignmentTests(unittest.TestCase):
    def test_a_training_pair_reads_the_decision_row_lead_rows_before_its_target(self):
        t = s3c_satiation.SatiationTable(rows([0.01, 0.02, 0.03, 0.04, 0.05]), sc.SATIATION_DIST)
        self.assertEqual(t.at(2, 4), {sc.SATIATION_DIST: 3.0})
        self.assertEqual(t.at(1, 4), {sc.SATIATION_DIST: 4.0})

    def test_a_forecast_reads_its_own_decision_rows_value(self):
        t = s3c_satiation.SatiationTable(rows([0.01, 0.02, 0.03, 0.04, 0.05]), sc.SATIATION_DIST)
        for lead in (1, 3, 5):
            self.assertEqual(t.read(lead, 1), {sc.SATIATION_DIST: 2.0})

    def test_the_distance_is_in_percentage_points_and_the_hinge_already_is(self):
        d = s3c_satiation.SatiationTable(rows([-0.015], [1.5]), sc.SATIATION_DIST)
        h = s3c_satiation.SatiationTable(rows([-0.015], [1.5]), sc.SATIATION_HINGE)
        self.assertAlmostEqual(d.read(1, 0)[sc.SATIATION_DIST], -1.5)
        self.assertAlmostEqual(h.read(1, 0)[sc.SATIATION_HINGE], 1.5)

    def test_a_hole_serves_nothing_to_a_forecast_and_is_an_error_for_a_training_pair(self):
        t = s3c_satiation.SatiationTable(rows([None, 0.02, 0.03]), sc.SATIATION_DIST)
        self.assertEqual(t.read(2, 0), {})
        self.assertEqual(t.read(2, 9), {})
        with self.assertRaises(ValueError):
            t.at(2, 2)
        with self.assertRaises(ValueError):
            t.at(1, -5)

    def test_an_unknown_term_is_refused(self):
        with self.assertRaises(ValueError):
            s3c_satiation.SatiationTable(rows([0.01]), "h9_forecast")

    def test_a_merged_table_serves_the_union_of_its_terms(self):
        r = rows([0.01, -0.02, 0.03])
        m = s3c_satiation.MergedTable(
            s3c_satiation.SatiationTable(r, sc.SATIATION_DIST), s3c_satiation.SatiationTable(r, sc.SATIATION_HINGE))
        self.assertEqual(set(m.read(1, 1)), {sc.SATIATION_DIST, sc.SATIATION_HINGE})
        self.assertEqual(set(m.at(1, 2)), {sc.SATIATION_DIST, sc.SATIATION_HINGE})
        with self.assertRaises(ValueError):
            s3c_satiation.MergedTable()


class FutureTests(unittest.TestCase):
    def test_a_later_row_does_not_move_a_served_value(self):
        base = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06]
        moved = base[:2] + [9.0] * 4  # every row after the decision row 1 is different
        for term in sc.SATIATION_EXTRAS:
            a = s3c_satiation.SatiationTable(rows(base), term)
            b = s3c_satiation.SatiationTable(rows(moved), term)
            for lead in (1, 2, 3, 4, 5):
                self.assertEqual(a.read(lead, 1), b.read(lead, 1))

    def test_a_training_pair_reads_nothing_after_its_target(self):
        t = s3c_satiation.SatiationTable(rows([0.01, 0.02, 0.03, 0.04]), sc.SATIATION_DIST)
        # the pair with target row 2 at lead 1 has its decision on row 1: row 2 and 3 are not read
        self.assertEqual(t.at(1, 2), {sc.SATIATION_DIST: 2.0})
        self.assertEqual(t.at(1, 2), s3c_satiation.SatiationTable(rows([0.01, 0.02, 7.0, 7.0]), sc.SATIATION_DIST).at(1, 2))


class FitTests(unittest.TestCase):
    def pairs(self, n=120, slope=0.5):
        xs = [float(i % 7) - 3.0 for i in range(n)]
        return [sc.StatePair(slope * x + 0.01 * ((-1) ** i), 1.0, {}, None, {}, i, i + 1, {sc.SATIATION_DIST: x}) for i, x in enumerate(xs)]

    def fit(self, pairs):
        return sc.fit_state_terms(pairs, regressors=(), terms=(), interact=False, robust=True, training_pairs="direct", extra=(sc.SATIATION_DIST,))

    def test_the_names_are_extra_terms_of_the_fit(self):
        self.assertTrue(set(sc.SATIATION_EXTRAS) <= set(sc.EXTRA_TERMS))
        self.assertEqual(sc.SATIATION_EXTRAS, (sc.SATIATION_DIST, sc.SATIATION_HINGE))

    def test_the_fit_recovers_a_known_slope_and_the_forecast_applies_it(self):
        estimate = self.fit(self.pairs())
        self.assertIn(sc.SATIATION_DIST, estimate.effect)
        self.assertAlmostEqual(estimate.effect[sc.SATIATION_DIST], 0.5, delta=0.05)
        shift = sc.standardised_shift(estimate, {}, None, None, {sc.SATIATION_DIST: 2.0})
        self.assertAlmostEqual(shift, 2.0 * estimate.effect[sc.SATIATION_DIST], places=9)
        self.assertEqual(sc.standardised_shift(estimate, {}, None, None, {}), 0.0)

    def test_the_pool_is_the_residual_after_the_term(self):
        estimate = self.fit(self.pairs())
        self.assertLess(max(abs(v) for v in estimate.pool), 0.5)  # without the term the residuals would be about +-1.5

    def test_a_term_the_arm_does_not_name_is_not_fitted(self):
        pairs = [sc.StatePair(p.raw, 1.0, {}, None, {}, p.origin, p.target, {**p.extras, sc.SATIATION_HINGE: 1.0}) for p in self.pairs()]
        estimate = self.fit(pairs)
        self.assertNotIn(sc.SATIATION_HINGE, estimate.effect)


if __name__ == "__main__":
    unittest.main()
