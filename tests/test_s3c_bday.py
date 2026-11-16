"""Business-day 1, 2 and 3 columns after a month-end, as extra terms of (s3c-ann-net) (#1631; H5 step 4, development arm; avenue #1627).

`repo_model.s3c_bday.BdayTable` is a new read path. For the decision on panel row `d` it serves, at lead `h`, the columns of the TARGET row `d + h`: a 0/1
flag per business day 1, 2 and 3 of the month (`derived_features.bday_of_month`), the six of those crossed with the kind of the month-end before (the target
falls in January, April, July or October: 'quarter'), and the single `bday_le3` flag that the candidate's own `post_month_end_window` term carries (the
control). It is the table `spread_mr_state_calendar.walk` calls through its `iorb` argument (`at` for a training pair, `read` for a forecast); the terms are
the `BDAY_EXTRAS`, `QUARTER_EXTRAS` and `CONTROL_EXTRAS` of that module. Each is a function of the target row's own date, so it is always public.

What these tests pin: the columns on hand-picked days (business day 1 to 3, the day after, a quarter and a non-quarter month); the table reads the target row of
the decision, never the origin row (the one-step read of the #914 class), and a training pair reads the columns of its own target row; a decision whose target
row is not in the panel is refused; the terms enter the fit as extras and leave the pool as the term-free residual; a term carried by fewer than three pairs
stays out; a one-step fit still raises `ValueError`; the control column in the place of the candidate's flag gives the candidate's effect and pool; and each arm
is (s3c-ann-net) with `post_month_end_window` replaced by its columns, nothing else changed.

Recorded mutation (calendar at the target day, #1631): in `s3c_bday.BdayTable.read`, `row = cal.target_row(decision_index, lead)` was changed to
`row = decision_index` (the origin row, a one-step read). `ReadTests.test_a_forecast_reads_the_columns_of_the_target_row` then failed with `AssertionError`
(the decision on 2026-10-30 at lead 1 read the columns of 2026-10-30, all zero, not business day 1 of November); restored, it passes. Second mutation
(the same read in training): in `BdayTable.at`, `row` was replaced by `row - lead`; `ReadTests.test_a_training_pair_reads_the_columns_of_its_own_target_row`
failed with `AssertionError`.
"""

from __future__ import annotations

import dataclasses
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model import s3c_announced, s3c_bday as sb  # noqa: E402
from repo_model import spread_mr_calendar as cal, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.data import DailyObservation  # noqa: E402


def business_days(first, n):
    day, out = first, []
    while len(out) < n:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


#: 2026-10-26 to 2026-11-10: November opens on Monday the 2nd (business day 1), the 3rd and the 4th are business days 2 and 3, the 5th is day 4.
DAYS = business_days(date(2026, 10, 26), 12)
ROW = {d: i for i, d in enumerate(DAYS)}


def panel():
    return [DailyObservation(d, {}) for d in DAYS]


class ColumnTests(unittest.TestCase):

    def test_business_day_1_to_3_of_a_month(self):
        for d, name in ((date(2026, 11, 2), "bday_1"), (date(2026, 11, 3), "bday_2"), (date(2026, 11, 4), "bday_3")):
            got = sb.columns_of(d)
            self.assertEqual(got[name], 1, d)
            self.assertEqual(sum(got[n] for n in sb.BDAY_EXTRAS), 1, d)
            self.assertEqual(got[sb.CONTROL], 1, d)
        later = sb.columns_of(date(2026, 11, 5))
        self.assertEqual(sum(later[n] for n in sb.BDAY_EXTRAS), 0)
        self.assertEqual(later[sb.CONTROL], 0)

    def test_one_column_per_day_and_none_after_business_day_3(self):
        got = sb.columns_of(date(2026, 11, 3))
        self.assertEqual(got["bday_1"], 0)
        self.assertEqual(got["bday_2"], 1)
        self.assertEqual(got["bday_3"], 0)

    def test_the_kind_is_the_month_of_the_target(self):
        quarter, other = sb.columns_of(date(2026, 10, 1)), sb.columns_of(date(2026, 11, 2))
        self.assertEqual((quarter["bday_1_quarter"], quarter["bday_1_other"]), (1, 0))
        self.assertEqual((other["bday_1_quarter"], other["bday_1_other"]), (0, 1))
        for month, kind in ((1, "quarter"), (4, "quarter"), (7, "quarter"), (10, "quarter"), (2, "other"), (11, "other"), (12, "other")):
            first = date(2026, month, 1)
            while first.weekday() >= 5 or sb.derived_features.bday_of_month(first) != 1:
                first += timedelta(days=1)
            self.assertEqual(sb.columns_of(first)[f"bday_1_{kind}"], 1, first)

    def test_a_crossed_column_is_the_business_day_column_in_its_kind(self):
        for d in DAYS:
            c = sb.columns_of(d)
            for b in (1, 2, 3):
                self.assertEqual(c[f"bday_{b}"], c[f"bday_{b}_quarter"] + c[f"bday_{b}_other"])

    def test_the_names_are_declared(self):
        self.assertEqual(sb.BDAY_EXTRAS, ("bday_1", "bday_2", "bday_3"))
        self.assertEqual(sb.QUARTER_EXTRAS, tuple(f"bday_{b}_{k}" for k in ("quarter", "other") for b in (1, 2, 3)))
        self.assertEqual(sb.CONTROL_EXTRAS, ("bday_le3",))
        self.assertEqual(sc.BDAY_EXTRAS, sb.BDAY_EXTRAS + sb.QUARTER_EXTRAS + sb.CONTROL_EXTRAS)
        self.assertTrue(set(sc.BDAY_EXTRAS) <= set(sc.EXTRA_TERMS))
        self.assertEqual(len(set(sc.EXTRA_TERMS)), len(sc.EXTRA_TERMS))


class ReadTests(unittest.TestCase):

    def setUp(self):
        self.table = sb.BdayTable(panel())

    def test_a_forecast_reads_the_columns_of_the_target_row(self):
        decision = ROW[date(2026, 10, 30)]
        for lead, name in ((1, "bday_1"), (2, "bday_2"), (3, "bday_3")):
            got = self.table.read(lead, decision)
            self.assertEqual(got[name], 1, (lead, got))
            self.assertEqual(sum(got[n] for n in sb.BDAY_EXTRAS), 1)
        self.assertEqual(sum(self.table.read(4, decision)[n] for n in sb.BDAY_EXTRAS), 0)

    def test_a_training_pair_reads_the_columns_of_its_own_target_row(self):
        got = self.table.at(2, ROW[date(2026, 11, 3)])
        self.assertEqual(got["bday_2"], 1)
        self.assertEqual(got["bday_1"], 0)

    def test_a_training_and_a_forecast_column_are_the_same_function_of_the_target_row(self):
        for decision in range(len(DAYS) - 5):
            for lead in (1, 2, 3, 4, 5):
                self.assertEqual(self.table.read(lead, decision), self.table.at(lead, decision + lead))

    def test_every_lead_serves_every_column(self):
        for lead in (1, 2, 3, 4, 5):
            self.assertEqual(set(self.table.at(lead, 6)), set(sc.BDAY_EXTRAS))

    def test_a_decision_with_no_target_row_is_refused(self):
        with self.assertRaises(ValueError):
            self.table.read(3, len(DAYS) - 2)


class FitTests(unittest.TestCase):
    """The columns enter the fit as extras beside the flag terms and leave the pool as the residual."""

    def pairs(self, names=sb.BDAY_EXTRAS):
        out = []
        for i in range(24):
            b = i % 6
            extras = {n: 0.0 for n in names}
            if b < 3 and names == sb.BDAY_EXTRAS:
                extras[f"bday_{b + 1}"] = 1.0
            flags = {name: 0 for name in cal.ALL_TERMS}
            flags["post_month_end_window"] = 1 if b < 3 else 0
            extras[sb.CONTROL] = float(flags["post_month_end_window"])
            out.append(sc.StatePair(2.0 + 3.0 * b if b < 3 else 0.1 * (i % 3), 1.0, flags, None, {}, -1, -1, extras))
        return out

    def fit(self, pairs, terms, extra, **kw):
        return sc.fit_state_terms(pairs, regressors=(), terms=terms, interact=False, robust=False, training_pairs="direct", min_flagged=3, extra=extra, **kw)

    def without(self):
        return tuple(n for n in cal.NO_FOMC_IORB if n != "post_month_end_window")

    def test_each_column_enters_with_its_own_effect(self):
        estimate = self.fit(self.pairs(), self.without(), sb.BDAY_EXTRAS)
        self.assertEqual(set(sb.BDAY_EXTRAS), set(estimate.terms) & set(sb.BDAY_EXTRAS))
        self.assertLess(estimate.effect["bday_1"], estimate.effect["bday_3"])
        self.assertNotEqual(estimate.effect["bday_1"], estimate.effect["bday_2"])

    def test_the_pool_is_what_the_columns_leave(self):
        estimate = self.fit(self.pairs(), self.without(), sb.BDAY_EXTRAS)
        for p, z in zip(self.pairs(), estimate.residuals):
            self.assertAlmostEqual(z, p.raw / p.scale - sum(estimate.effect[n] * p.extras[n] for n in sb.BDAY_EXTRAS))

    def test_the_shift_is_the_effect_of_the_columns_of_the_row(self):
        estimate = self.fit(self.pairs(), self.without(), sb.BDAY_EXTRAS)
        flags = {name: 0 for name in cal.ALL_TERMS}
        shift = sc.standardised_shift(estimate, flags, None, None, {"bday_2": 1.0, "bday_1": 0.0, "bday_3": 0.0})
        self.assertAlmostEqual(shift, estimate.effect["bday_2"])

    def test_a_column_carried_by_fewer_than_three_pairs_stays_out(self):
        pairs = [p._replace(extras=dict(p.extras, bday_3=1.0 if i == 2 else 0.0)) for i, p in enumerate(self.pairs())]
        estimate = self.fit(pairs, self.without(), sb.BDAY_EXTRAS)
        self.assertNotIn("bday_3", estimate.terms)
        self.assertIn("bday_1", estimate.terms)

    def test_the_control_column_in_the_place_of_the_flag_gives_the_candidates_fit(self):
        """The check the walk repeats on every cell: `bday_le3` as an extra equals `post_month_end_window` as a flag term (same column, same ridge)."""

        pairs = self.pairs()
        flagged = sc.fit_state_terms(pairs, regressors=(), terms=cal.NO_FOMC_IORB, interact=False, robust=True, training_pairs="direct", min_flagged=3)
        extra = sc.fit_state_terms(pairs, regressors=(), terms=self.without(), interact=False, robust=True, training_pairs="direct", min_flagged=3,
                                   extra=sb.CONTROL_EXTRAS)
        self.assertAlmostEqual(flagged.effect["post_month_end_window"], extra.effect[sb.CONTROL], places=9)
        for a, b in zip(flagged.pool, extra.pool):
            self.assertAlmostEqual(a, b, places=9)

    def test_a_one_step_fit_still_raises(self):
        with self.assertRaises(ValueError):
            sc.fit_state_terms(
                self.pairs(), regressors=("treasury_settlement_coupons",), terms=self.without(), interact=False, robust=False,
                training_pairs="one_step", extra=sb.BDAY_EXTRAS)

    def test_the_arms_train_on_direct_pairs(self):
        self.assertEqual(sb.TRAINING_PAIRS, "direct")


class ArmTests(unittest.TestCase):

    def test_the_primary_arm_replaces_the_flag_by_the_three_columns(self):
        arm = sb.PRIMARY
        self.assertEqual(arm.extra, sb.BDAY_EXTRAS)
        self.assertNotIn("post_month_end_window", arm.location)
        self.assertEqual(dataclasses.replace(arm, name="x", role="x", location=s3c_announced.ANN_NET_ARM.location, extra=()),
                         dataclasses.replace(s3c_announced.ANN_NET_ARM, name="x", role="x"))
        self.assertEqual(set(arm.location) | {"post_month_end_window"}, set(s3c_announced.ANN_NET_ARM.location))

    def test_the_secondary_arm_is_the_six_crossed_columns(self):
        self.assertEqual(sb.SECONDARY.extra, sb.QUARTER_EXTRAS)
        self.assertEqual(sb.SECONDARY.location, sb.PRIMARY.location)

    def test_the_control_arm_is_the_one_column_the_candidate_has(self):
        self.assertEqual(sb.CONTROL_ARM.extra, sb.CONTROL_EXTRAS)
        self.assertEqual(sb.CONTROL_ARM.location, sb.PRIMARY.location)

    def test_the_arms_are_sized_robust_and_not_interacted(self):
        for arm in (sb.PRIMARY, sb.SECONDARY, sb.CONTROL_ARM):
            self.assertTrue(arm.sized)
            self.assertTrue(arm.robust)
            self.assertFalse(arm.interact)

    def test_the_arm_names_are_distinct_from_the_candidates(self):
        names = {sb.PRIMARY.name, sb.SECONDARY.name, sb.CONTROL_ARM.name, s3c_announced.ANN_NET_ARM.name}
        self.assertEqual(len(names), 4)


if __name__ == "__main__":
    unittest.main()
