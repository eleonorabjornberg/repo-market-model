"""The two arms that keep calendar target rows out of (s3)'s Huber downweighting (#1226; H5 step 3, fix; avenue #1213).

`metadata/s3_huber_calendar_1226.json` is the declaration; `repo_model.spread_mr_state_calendar` (`HW1`, `HW2`, `HW_ARMS`,
`calendar_row`) is its arithmetic. (s3-hw1) is (s3) with the target rows that carry a calendar type at full weight in the Huber
fit; (s3-hw2) gives those rows their own Huber threshold at `CALENDAR_K` times the ordinary one. What these tests pin: that each
arm is (s3) with one setting changed; that with no calendar row (or a calendar row inside the cut) an arm is (s3) exactly; that a
calendar outlier moves hw1 most, hw2 less and (s3) least while an ordinary outlier is downweighted alike by all three; that a
calendar row is defined by the target row alone and is refused after the anchor; that the arms of #1145, #1172 and #1196 are
unchanged; and that the one-step fit of either arm is refused by the guard of #947.

Recorded mutation (applied to the tree, the named test run, and reverted):

* `calendar_row`: `if row > anchor:` replaced with `if row > anchor + 1:`, so the flags of the row after the anchor (a target the
  fit could not have seen) are admitted as a training row's type. `test_a_row_after_the_anchor_is_refused` failed with
  `AssertionError` (`LookAheadError` not raised).
"""

from __future__ import annotations

import dataclasses
import unittest
from datetime import date

from repo_model import spread_mr_calendar as cal
from repo_model import spread_mr_state_calendar as sc
from repo_model import turn_days
from repo_model.splits import LookAheadError

from test_spread_mr_state_calendar import NONE, PANEL, SETTINGS, TABLE_ALL, index_of, states_of

S3 = sc.ARMS[2]


def fit(pairs, arm, *, terms=("quarter_end",)):
    return sc.fit_state_terms(
        pairs, regressors=terms, terms=terms, interact=arm.interact, robust=arm.robust, ridge=arm.ridge, sized=arm.sized,
        calendar_k=arm.calendar_k, training_pairs="direct",
    )


def pairs_of(*, effect=2.0, flagged=12, n=90, calendar_outlier=None, ordinary_outlier=None):
    """Pairs whose standardised residual is `effect` on a quarter-end (a calendar row) and noise otherwise.

    `calendar_outlier` replaces the residual of the first quarter-end pair, `ordinary_outlier` that of the last ordinary pair.
    """

    out = []
    for i in range(n):
        flags = dict(NONE)
        flags["quarter_end"] = 1 if i < flagged else 0
        noise = (-1.0) ** i * (0.4 + (i % 3) * 0.2)
        z = noise + (effect if flags["quarter_end"] else 0.0)
        if calendar_outlier is not None and i == 0:
            z = calendar_outlier
        if ordinary_outlier is not None and i == n - 1:
            z = ordinary_outlier
        out.append(sc.StatePair(z, 1.0, flags, None, calendar=bool(flags["quarter_end"])))
    return out


class DeclaredArmsTests(unittest.TestCase):

    def test_hw1_is_s3_with_calendar_rows_at_full_weight_and_nothing_else(self):
        self.assertEqual(sc.HW1.name, "sc_s3_hw1")
        self.assertEqual(dataclasses.replace(sc.HW1, name=S3.name, role=S3.role, calendar_k=None), S3)
        self.assertEqual(sc.HW1.calendar_k, sc.FULL_WEIGHT)
        self.assertEqual((sc.HW1.robust, sc.HW1.interact, sc.ridge_of(sc.HW1), sc.HW1.location), (True, False, 5.0, cal.NO_FOMC_IORB))

    def test_hw2_is_s3_with_its_own_calendar_threshold_and_nothing_else(self):
        self.assertEqual(sc.HW2.name, "sc_s3_hw2")
        self.assertEqual(dataclasses.replace(sc.HW2, name=S3.name, role=S3.role, calendar_k=None), S3)
        self.assertEqual(sc.HW2.calendar_k, sc.CALENDAR_K)
        self.assertEqual(sc.CALENDAR_K, 2.0)
        self.assertEqual((sc.HW2.robust, sc.HW2.interact, sc.ridge_of(sc.HW2), sc.HW2.location), (True, False, 5.0, cal.NO_FOMC_IORB))

    def test_the_screen_is_s3_then_the_two_arms_and_both_are_registered(self):
        self.assertEqual([a.name for a in sc.HW_ARMS], [S3.name, sc.HW1.name, sc.HW2.name])
        for arm in sc.HW_ARMS:
            self.assertIs(sc.ALL_ARMS[arm.name], arm)

    def test_the_arms_of_earlier_studies_are_unchanged(self):
        self.assertEqual([(sc.ridge_of(a), a.robust, a.interact, a.sized, a.calendar_k) for a in sc.ARMS],
                         [(1.0, False, False, False, None), (1.0, False, True, False, None), (5.0, True, False, False, None),
                          (1.0, False, False, False, None)])
        self.assertEqual([a.name for a in sc.DECOMPOSITION], ["sc_s1_standardised", "sc_r1_ridge5", "sc_r2_huber", "sc_s3_robust", "sc_r3_size"])
        self.assertEqual([a.name for a in sc.S3_TERMS], ["sc_s3_robust", "sc_s3_state", "sc_s3_fomc_iorb"])
        self.assertTrue(all(a.calendar_k is None for a in sc.DECOMPOSITION + sc.S3_TERMS))

    def test_a_calendar_threshold_needs_the_huber_fit(self):
        with self.assertRaisesRegex(ValueError, "Huber"):
            fit(pairs_of(), dataclasses.replace(sc.HW1, robust=False))


class HuberWeightingTests(unittest.TestCase):

    def test_with_no_calendar_outlier_each_arm_is_s3_exactly(self):
        pairs = pairs_of(effect=0.5)
        base = fit(pairs, S3)
        for arm in (sc.HW1, sc.HW2):
            other = fit(pairs, arm)
            self.assertEqual(other.effect, base.effect, arm.name)
            self.assertEqual(other.pool, base.pool, arm.name)

    def test_with_no_calendar_row_each_arm_is_s3_exactly_even_with_an_ordinary_outlier(self):
        pairs = [p._replace(calendar=False) for p in pairs_of(ordinary_outlier=60.0)]
        base = fit(pairs, S3)
        for arm in (sc.HW1, sc.HW2):
            self.assertEqual(fit(pairs, arm).effect, base.effect, arm.name)

    def test_a_calendar_outlier_moves_hw1_most_then_hw2_then_s3(self):
        pairs = pairs_of(effect=0.0, calendar_outlier=40.0)
        s3, hw2, hw1 = fit(pairs, S3).effect["quarter_end"], fit(pairs, sc.HW2).effect["quarter_end"], fit(pairs, sc.HW1).effect["quarter_end"]
        self.assertGreater(hw1, hw2)
        self.assertGreater(hw2, s3)
        self.assertGreater(s3, 0.0)

    def test_an_ordinary_outlier_is_downweighted_by_every_arm_and_alike(self):
        pairs = pairs_of(effect=0.0, ordinary_outlier=60.0)
        base = fit(pairs, S3)
        for arm in (sc.HW1, sc.HW2):
            self.assertAlmostEqual(fit(pairs, arm).effect["quarter_end"], base.effect["quarter_end"], places=6, msg=arm.name)
        least_squares = fit(pairs, dataclasses.replace(S3, robust=False, calendar_k=None))
        self.assertLess(abs(base.pool[-1]), abs(least_squares.pool[-1]) + 1e-9)

    def test_a_calendar_row_keeps_full_weight_under_hw1_however_large_its_residual(self):
        rows = [[1.0], [1.0], [1.0], [1.0], [1.0], [1.0]]
        y = [0.0, 0.1, -0.1, 0.05, -0.05, 100.0]
        plain, _ = sc.huber(rows, y, 0.0)
        full, _ = sc.huber(rows, y, 0.0, multipliers=[1.0] * 5 + [sc.FULL_WEIGHT])
        self.assertLess(plain[0], 1.0)  # the outlier is downweighted in (s3)
        self.assertGreater(full[0], 10 * plain[0])  # at full weight it pulls the intercept toward itself
        self.assertEqual(sc.huber(rows, y, 0.0, multipliers=[1.0] * 6), (plain, sc.huber(rows, y, 0.0)[1]))

    def test_multipliers_of_one_are_the_huber_fit_of_s3(self):
        rows = [[1.0, float(i % 2)] for i in range(30)]
        y = [(-1.0) ** i + (3.0 if i % 2 else 0.0) + (25.0 if i == 4 else 0.0) for i in range(30)]
        self.assertEqual(sc.huber(rows, y, 1.0), sc.huber(rows, y, 1.0, multipliers=[1.0] * 30))

    def test_one_multiplier_per_row(self):
        with self.assertRaises(ValueError):
            sc.huber([[1.0], [1.0]], [0.0, 1.0], 0.0, multipliers=[1.0])


class CalendarRowTests(unittest.TestCase):

    DATES = [row.date for row in PANEL]

    def anchor(self):
        return len(PANEL) - 1

    def row_of(self, day):
        return index_of(day)

    def test_the_named_calendar_types_are_calendar_rows(self):
        # 2024-03-29 the quarter-end turn, 2024-04-15 a tax date, 2024-06-12 an FOMC day, 2024-01-31 the month-end
        for day in ("2024-03-28", "2024-04-15", "2024-06-12", "2024-01-31"):
            self.assertTrue(sc.calendar_row(TABLE_ALL, self.DATES, self.row_of(day), self.anchor()), day)

    def test_a_turn_day_of_the_record_in_force_is_a_calendar_row(self):
        day = next(d for d in self.DATES if turn_days.turn_label(d) is not None and d.year == 2023)
        row = self.DATES.index(day)
        self.assertTrue(sc.calendar_row(TABLE_ALL, self.DATES, row, self.anchor()), day)

    def test_a_plain_mid_month_day_is_not(self):
        plain = [i for i, d in enumerate(self.DATES)
                 if d.year == 2023 and 8 <= d.day <= 12 and not any(TABLE_ALL.day_types(i)[t] for t in sc.CALENDAR_ROW_TERMS)
                 and turn_days.turn_label(d) is None]
        self.assertTrue(plain)
        for row in plain[:10]:
            self.assertFalse(sc.calendar_row(TABLE_ALL, self.DATES, row, self.anchor()), self.DATES[row])

    def test_the_two_broad_windows_alone_do_not_make_a_calendar_row(self):
        self.assertNotIn("dom_19_23", sc.CALENDAR_ROW_TERMS)
        self.assertNotIn("post_month_end_window", sc.CALENDAR_ROW_TERMS)
        self.assertEqual(set(sc.CALENDAR_ROW_TERMS) - set(cal.ALL_TERMS), set())

    def test_a_row_after_the_anchor_is_refused(self):
        row = self.row_of("2024-03-28")
        with self.assertRaises(LookAheadError):
            sc.calendar_row(TABLE_ALL, self.DATES, row, row - 1)
        sc.calendar_row(TABLE_ALL, self.DATES, row, row)  # the anchor row itself is public


class WalkTests(unittest.TestCase):

    DAYS = [PANEL[index_of("2024-06-07")].date]
    STATES = states_of(lambda i: (i % 4) / 3.0)

    @classmethod
    def setUpClass(cls):
        cls.walk = sc.walk(PANEL, cls.DAYS, TABLE_ALL, cls.STATES, sc.HW_ARMS, **SETTINGS)

    def test_s3_in_the_walk_is_the_s3_of_1145(self):
        reference = sc.walk(PANEL, self.DAYS, TABLE_ALL, self.STATES, (S3,), **SETTINGS)
        self.assertEqual(self.walk.forecasts[S3.name], reference.forecasts[S3.name])
        self.assertEqual(self.walk.forecasts[sc.ARM_A], reference.forecasts[sc.ARM_A])

    def test_every_arm_has_23_ordered_quantiles_at_every_lead(self):
        for name in (sc.ARM_A, S3.name, sc.HW1.name, sc.HW2.name):
            for day, leads in self.walk.forecasts[name].items():
                self.assertEqual(sorted(leads), [1, 2, 3, 4, 5])
                for q in leads.values():
                    self.assertEqual(len(q), 23, name)
                    self.assertEqual(q, sorted(q), name)

    def test_the_arms_differ_from_s3_only_through_the_fit(self):
        # the same terms enter; the fit may differ in the coefficients, never in which terms are in it
        for estimates in self.walk.estimates.values():
            for h in (1, 2, 3, 4, 5):
                base = estimates[S3.name][h]
                for arm in (sc.HW1, sc.HW2):
                    self.assertEqual(estimates[arm.name][h].terms, base.terms, (arm.name, h))
                    self.assertEqual(estimates[arm.name][h].pairs, base.pairs, (arm.name, h))
                    self.assertEqual(estimates[arm.name][h].origins, base.origins, (arm.name, h))

    def test_hw1_gives_a_calendar_term_at_least_the_effect_s3_gives_it_on_the_planted_data(self):
        pairs = pairs_of(effect=0.0, calendar_outlier=40.0)
        self.assertGreater(fit(pairs, sc.HW1).effect["quarter_end"], fit(pairs, S3).effect["quarter_end"])

    def test_the_one_step_fit_of_either_arm_is_refused_by_the_guard(self):
        for arm in (sc.HW1, sc.HW2):
            with self.assertRaisesRegex(ValueError, "one-step pairs"):
                sc.walk(PANEL, self.DAYS, TABLE_ALL, self.STATES, (arm,), **SETTINGS, training_pairs="one_step")


if __name__ == "__main__":
    unittest.main()
