"""The reserves ratio R and the scarcity state S as extra terms of (s3c-ann-net) (#1526; H7 step 2, H7f, development tier).

`repo_model.s3c_rs` builds two panel columns from the three legs of the scarcity state, each leg read through the as-of rule at its own latest public
row (`scarcity.own_leg_states`'s read, #586): `rs_reserves_ratio` (R, `scarcity.reserves_ratio` of the reserve balances over the H.8 bank total assets) and
`rs_scarcity_state` (S, `scarcity.reserve_scarcity_state`, 0 to 3, from R and the ON RRP buffer). `RSTable` serves them to `spread_mr_state_calendar` as the
extra terms `rs_ratio` (percentage points) and `rs_state` (S over 3, the level `spread_mr_state_calendar.level` gives). Pinned on hand cases:

* `BuildTests`: R is the ratio the rule reads, S is the state formed from the three legs' own reads, a day after the last scored day has no value, and
  **no later row moves an earlier value** (the criterion);
* `LegTests`: a leg read at a row public after the decision instant is refused (`LookAheadError`), and a hole in a leg is no value;
* `NoFutureTests`: the guard that refuses a column built from a row after its own decision;
* `TableTests`: the alignment of a training pair (the decision row `target row - lead`) and of a forecast (its own decision row, whatever the lead), the
  units, holes, and that no later row moves a served value;
* `FitTests`: the names are extra terms of the fit, which recovers a known slope on each.

**Recorded mutations** (9 November 2026, disposable copy of the tree, `PYTHONDONTWRITEBYTECODE=1`, the killing test run alone, restored before the
next):

1. `build_rs_columns`: the line `ratio, state = values[i]` was changed to `ratio, state = values[min(i + 1, len(values) - 1)]` (each row reads the next
   row's legs). `NoFutureTests.test_the_columns_pass_when_they_use_nothing_later` raised `LookAheadError: rs_reserves_ratio on 2023-03-13 is
   0.14800000000000002, but the panel cut at that row gives 0.10600000000000001; the column depended on a later row`, and
   `BuildTests.test_a_day_after_the_last_scored_day_has_no_value` failed with `AssertionError: unexpectedly None`.
2. `check_rs_no_future`: the comparison `if (have is None) != (want is None) or (have is not None and abs(have - want) > 1e-12):` was changed to
   `if False:`. `NoFutureTests.test_a_column_that_differs_from_the_cut_panels_is_refused` and `test_a_column_built_from_a_later_row_is_refused` failed
   with `AssertionError: LookAheadError not raised`.
3. `read_legs`: the call `_require_public(info)` was replaced by `pass`. `LegTests.test_a_leg_read_after_the_decision_instant_is_refused` failed with
   `AssertionError: LookAheadError not raised`.
4. `RSTable.read`: `value = self._value(decision_index)` was changed to `value = self._value(decision_index + lead)` (the value at the target row).
   `TableTests.test_a_later_row_does_not_move_a_served_value` failed with `AssertionError: {'rs_ratio': 12.0} != {'rs_ratio': 900.0}` (the served value
   moved when rows after the decision row changed), and `TableTests.test_a_forecast_reads_its_own_decision_rows_value` with
   `AssertionError: 12.0 != 11.0 within 7 places`.

Each mutation was restored after its run and the module passes all tests.
"""

from __future__ import annotations

import sys
import unittest
from datetime import date, time, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model import s3c_rs, scarcity, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.asof import InformationRule  # noqa: E402
from repo_model.data import DailyObservation  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

from test_satiation import _Measured  # noqa: E402

LAST = date(2025, 12, 31)


class _RS(_Measured):
    def rule(self):
        return InformationRule(self.registry, s3c_rs.LEGS, decision_time=time(16, 0), horizon=1)

    def built_rs(self, rows=None):
        return s3c_rs.build_rs_columns(self.rows if rows is None else rows, self.rule(), last_day=LAST)


class BuildTests(_RS):
    def test_r_is_the_ratio_the_rule_reads_and_s_the_state_of_the_three_legs(self):
        out = self.built_rs()
        info = self.rule().information_set(s3c_rs.extended_dates([r.date for r in self.rows], 200), 201)
        read = {r.feature: r.row for r in info.reads}
        reserves = self.rows[read["reserve_balances"]].values["reserve_balances"]
        assets = self.rows[read["bank_total_assets"]].values["bank_total_assets"]
        rrp = self.rows[read["on_rrp"]].values["on_rrp"]
        self.assertAlmostEqual(out[200].values[s3c_rs.RATIO_COLUMN], scarcity.reserves_ratio(reserves, assets))
        self.assertEqual(out[200].values[s3c_rs.STATE_COLUMN], float(scarcity.reserve_scarcity_state(reserves, assets, rrp)))

    def test_the_state_is_an_integer_level_from_zero_to_three(self):
        states = {r.values[s3c_rs.STATE_COLUMN] for r in self.built_rs() if r.values[s3c_rs.STATE_COLUMN] is not None}
        self.assertTrue(states and states <= {0.0, 1.0, 2.0, 3.0})

    def test_a_day_after_the_last_scored_day_has_no_value(self):
        out = s3c_rs.build_rs_columns(self.rows, self.rule(), last_day=self.rows[150].date)
        for name in (s3c_rs.RATIO_COLUMN, s3c_rs.STATE_COLUMN):
            self.assertIsNone(out[151].values[name])
            self.assertIsNotNone(out[150].values[name])

    def test_a_later_rows_values_do_not_move_an_earlier_value(self):
        full = self.built_rs()
        changed = [DailyObservation(r.date, dict(r.values)) for r in self.rows]
        for later in changed[201:]:
            later.values["reserve_balances"] = 9999.0
            later.values["on_rrp"] = 9999.0
        again = self.built_rs(changed)
        for name in (s3c_rs.RATIO_COLUMN, s3c_rs.STATE_COLUMN):
            self.assertEqual(full[200].values[name], again[200].values[name])
        self.assertNotEqual(full[260].values[s3c_rs.RATIO_COLUMN], again[260].values[s3c_rs.RATIO_COLUMN])


class LegTests(_RS):
    def test_a_leg_read_after_the_decision_instant_is_refused(self):
        rule = self.rule()
        real = rule.information_set

        def late(dates, scored):
            info = real(dates, scored)
            reads = tuple(
                r._replace(available_at=info.decision_instant + timedelta(hours=1)) if r.feature == "on_rrp" else r for r in info.reads
            )
            return SimpleNamespace(reads=reads, decision_instant=info.decision_instant)

        with mock.patch.object(rule, "information_set", late), self.assertRaises(LookAheadError):
            s3c_rs.build_rs_columns(self.rows[:120], rule, last_day=LAST)

    def test_a_hole_in_a_leg_is_no_value_and_not_a_partial_state(self):
        holey = [DailyObservation(r.date, dict(r.values)) for r in self.rows]
        for row in holey:
            row.values["on_rrp"] = None
        out = self.built_rs(holey)
        self.assertIsNone(out[200].values[s3c_rs.STATE_COLUMN])
        self.assertIsNotNone(out[200].values[s3c_rs.RATIO_COLUMN])  # R needs two legs, S needs three


class NoFutureTests(_RS):
    def test_the_columns_pass_when_they_use_nothing_later(self):
        s3c_rs.check_rs_no_future(self.rows, self.built_rs(), self.rule(), last_day=LAST, indices=range(40, 300, 7))

    def test_a_column_that_differs_from_the_cut_panels_is_refused(self):
        bent = [DailyObservation(r.date, dict(r.values)) for r in self.built_rs()]
        bent[100].values[s3c_rs.STATE_COLUMN] = 3.0 - bent[100].values[s3c_rs.STATE_COLUMN]
        with self.assertRaises(LookAheadError):
            s3c_rs.check_rs_no_future(self.rows, bent, self.rule(), last_day=LAST, indices=[100])

    def test_a_column_built_from_a_later_row_is_refused(self):
        built = self.built_rs()
        leaked = []
        for i, row in enumerate(self.rows):
            values = dict(row.values)
            ahead = built[min(i + 1, len(built) - 1)]
            values[s3c_rs.RATIO_COLUMN] = ahead.values[s3c_rs.RATIO_COLUMN]
            values[s3c_rs.STATE_COLUMN] = ahead.values[s3c_rs.STATE_COLUMN]
            leaked.append(DailyObservation(row.date, values))
        with self.assertRaises(LookAheadError):
            s3c_rs.check_rs_no_future(self.rows, leaked, self.rule(), last_day=LAST, indices=range(40, 300, 3))


def table_rows(ratio, state):
    day, out = date(2026, 3, 2), []
    for r, s in zip(ratio, state):
        while day.weekday() >= 5:
            day += timedelta(days=1)
        out.append(DailyObservation(day, {s3c_rs.RATIO_COLUMN: r, s3c_rs.STATE_COLUMN: s}))
        day += timedelta(days=1)
    return out


class TableTests(unittest.TestCase):
    RATIO = [0.10, 0.11, 0.12, 0.13, 0.14]
    STATE = [3.0, 2.0, 1.0, 0.0, 0.0]

    def table(self, term, ratio=None, state=None):
        return s3c_rs.RSTable(table_rows(self.RATIO if ratio is None else ratio, self.STATE if state is None else state), term)

    def test_a_training_pair_reads_the_decision_row_lead_rows_before_its_target(self):
        self.assertAlmostEqual(self.table(sc.RS_RATIO).at(2, 4)[sc.RS_RATIO], 12.0)
        self.assertAlmostEqual(self.table(sc.RS_RATIO).at(1, 4)[sc.RS_RATIO], 13.0)
        self.assertAlmostEqual(self.table(sc.RS_STATE).at(2, 4)[sc.RS_STATE], 1.0 / 3.0)

    def test_a_forecast_reads_its_own_decision_rows_value(self):
        for lead in (1, 3, 5):
            self.assertAlmostEqual(self.table(sc.RS_RATIO).read(lead, 1)[sc.RS_RATIO], 11.0)
            self.assertAlmostEqual(self.table(sc.RS_STATE).read(lead, 1)[sc.RS_STATE], 2.0 / 3.0)

    def test_the_units_are_percentage_points_and_a_third_of_a_state(self):
        t = self.table(sc.RS_RATIO, [0.1234], [3.0])
        self.assertAlmostEqual(t.read(1, 0)[sc.RS_RATIO], 12.34)
        self.assertAlmostEqual(self.table(sc.RS_STATE, [0.1234], [3.0]).read(1, 0)[sc.RS_STATE], sc.level(3.0))

    def test_a_hole_serves_nothing_to_a_forecast_and_is_an_error_for_a_training_pair(self):
        t = self.table(sc.RS_STATE, state=[None, 2.0, 1.0, 0.0, 0.0])
        self.assertEqual(t.read(2, 0), {})
        self.assertEqual(t.read(2, 99), {})
        with self.assertRaises(ValueError):
            t.at(2, 2)

    def test_an_unknown_term_is_refused(self):
        with self.assertRaises(ValueError):
            s3c_rs.RSTable(table_rows([0.1], [1.0]), "satiation_dist")

    def test_a_merged_table_serves_both_terms(self):
        rows = table_rows(self.RATIO, self.STATE)
        merged = s3c_rs.merged(rows)
        self.assertEqual(set(merged.read(1, 1)), {sc.RS_RATIO, sc.RS_STATE})
        self.assertEqual(set(merged.at(1, 2)), {sc.RS_RATIO, sc.RS_STATE})

    def test_a_later_row_does_not_move_a_served_value(self):
        moved_ratio = self.RATIO[:2] + [9.0] * 3
        moved_state = self.STATE[:2] + [0.0] * 3
        for term in sc.RS_EXTRAS:
            a = self.table(term)
            b = self.table(term, moved_ratio, moved_state)
            for lead in (1, 2, 3, 4, 5):
                self.assertEqual(a.read(lead, 1), b.read(lead, 1))


class FitTests(unittest.TestCase):
    def pairs(self, term, n=140, slope=0.5):
        xs = [float(i % 7) - 3.0 for i in range(n)]
        return [sc.StatePair(slope * x + 0.01 * ((-1) ** i), 1.0, {}, None, {}, i, i + 1, {term: x}) for i, x in enumerate(xs)]

    def fit(self, pairs, extra):
        return sc.fit_state_terms(pairs, regressors=(), terms=(), interact=False, robust=True, training_pairs="direct", extra=extra)

    def test_the_names_are_extra_terms_of_the_fit(self):
        self.assertEqual(sc.RS_EXTRAS, (sc.RS_RATIO, sc.RS_STATE))
        self.assertTrue(set(sc.RS_EXTRAS) <= set(sc.EXTRA_TERMS))
        self.assertEqual(len(set(sc.EXTRA_TERMS)), len(sc.EXTRA_TERMS))

    def test_the_fit_recovers_a_known_slope_for_each_term(self):
        for term in sc.RS_EXTRAS:
            estimate = self.fit(self.pairs(term), (term,))
            self.assertAlmostEqual(estimate.effect[term], 0.5, delta=0.05)
            shift = sc.standardised_shift(estimate, {}, None, None, {term: 2.0})
            self.assertAlmostEqual(shift, 2.0 * estimate.effect[term], places=9)

    def test_a_term_the_arm_does_not_name_is_not_fitted(self):
        estimate = self.fit(self.pairs(sc.RS_RATIO), (sc.RS_RATIO,))
        self.assertNotIn(sc.RS_STATE, estimate.effect)


if __name__ == "__main__":
    unittest.main()
