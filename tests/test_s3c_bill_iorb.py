"""The 4-week bill rate less IORB of the previous business day, as an extra term of (s3c-ann-net) (#1346; H5 step 3, ledger item 97).

`repo_model.s3c_bill_iorb.BillLessIorbTable` is a new read path. For the decision on panel row `d` it serves `(tbill_4w - iorb) x 100 / 10`
(units of 10 bp) read from row `d - 1`, the same figure at every lead; a training pair with target row `T` at lead `h` reads the figure of its
own decision, row `T - h - 1`. It is the table `spread_mr_state_calendar.walk` calls through its `iorb` argument (`at`, `read`), and the term
is `spread_mr_state_calendar.BILL_LESS_IORB`. The published declaration, the live record and (s3c)'s table do not read it.

What these tests pin: the figure is the bill rate less IORB of the row before the decision, in units of 10 bp, and is the same at every lead;
a training figure and a forecast figure are the same function of the same rows; the row the figure is read from is the previous business day
and equals the row `asof.InformationRule` reads for `tbill_4w` and `iorb` at the 16:00 decision of the published records (so the arm is valid
at 16:00 as well as at the 18:00 of `repo_model.decision_instant`, and is not the same-day row that 18:00 would admit for `tbill_4w`);
`read` refuses, with `LookAheadError`, a figure read from the decision day's own row or later, and, with `StaleReadError`, one read from an
older row than the previous business day; a row with no previous row reads nothing; the term enters the fit beside the net terms and
shifts the pool and the forecast; a one-step fit still raises `ValueError`; and the arm is (s3c-ann-net) with the one term only.

Recorded mutation (leakage, #1346): in `s3c_bill_iorb.BillLessIorbTable.source_row`, `return row - lead - 1` was changed to
`return row - lead` (the decision day's own row, the same-day rate that #1334 questions). `ReadTests.test_the_decision_days_own_row_is_not_read`
then failed with `LookAheadError` (the guard in `read` refused a figure read from the decision day's row); restored, it passes. Second
mutation (staleness): the same line changed to `return row - lead - 2` made `ReadTests.test_an_older_row_than_the_previous_business_day_is_refused`
fail with `StaleReadError`.
"""

from __future__ import annotations

import csv
import dataclasses
import json
import sys
import unittest
from datetime import date, time, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model import s3c_announced, s3c_bill_iorb as sb  # noqa: E402
from repo_model import spread_mr_calendar as cal, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.asof import InformationRule, StaleReadError  # noqa: E402
from repo_model.data import DailyObservation  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

REGISTRY = json.loads((ROOT / "metadata" / "sources.json").read_text(encoding="utf-8"))
LEADS = (1, 2, 3, 4, 5)


def business_days(first, n):
    day, out = first, []
    while len(out) < n:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


DAYS = business_days(date(2026, 3, 2), 16)
#: Row i has a bill rate of 4.00 + 0.10 i percent and IORB of 3.90 percent, so the gap is (10 + 10 i) bp, i.e. 1 + i units of 10 bp.
BILLS = [4.00 + 0.10 * i for i in range(len(DAYS))]
IORB = 3.90


def panel():
    return [DailyObservation(d, {"tbill_4w": BILLS[i], "iorb": IORB}) for i, d in enumerate(DAYS)]


def unit(i):
    return round((BILLS[i] - IORB) * 100.0 / 10.0, 9)


class ValueTests(unittest.TestCase):

    def setUp(self):
        self.table = sb.BillLessIorbTable(panel())

    def test_the_term_is_the_gap_of_the_row_before_the_decision_in_units_of_10_bp(self):
        # Target row 9 at lead 3: the decision is on row 6, whose previous business day is row 5.
        got = self.table.at(3, 9)
        self.assertEqual(set(got), {sc.BILL_LESS_IORB})
        self.assertAlmostEqual(got[sc.BILL_LESS_IORB], unit(5))
        self.assertAlmostEqual(got[sc.BILL_LESS_IORB], 6.0)

    def test_the_figure_of_a_decision_is_the_same_at_every_lead(self):
        for decision in (4, 7):
            figures = {round(self.table.at(h, decision + h)[sc.BILL_LESS_IORB], 9) for h in LEADS}
            self.assertEqual(figures, {round(unit(decision - 1), 9)})

    def test_a_row_with_no_previous_row_reads_nothing(self):
        self.assertEqual(self.table.at(1, 1), {})
        self.assertEqual(self.table.at(5, 5), {})
        self.assertNotEqual(self.table.at(5, 6), {})

    def test_the_unit_is_10_bp(self):
        self.assertEqual(sb.UNIT_BPS, 10.0)

    def test_a_missing_rate_is_a_data_error(self):
        rows = panel()
        rows[5] = DailyObservation(DAYS[5], {"tbill_4w": None, "iorb": IORB})
        with self.assertRaises(ValueError):
            sb.BillLessIorbTable(rows).at(3, 9)

    def test_the_source_row_is_the_previous_business_day_of_the_decision(self):
        self.assertEqual([self.table.source_row(h, 9) for h in LEADS], [7, 6, 5, 4, 3])
        self.assertEqual([self.table.source_row(h, 9) + 1 for h in LEADS], [9 - h for h in LEADS])


class ReadTests(unittest.TestCase):
    """A forecast reads the figure of its own decision, and refuses one that is not."""

    def setUp(self):
        self.table = sb.BillLessIorbTable(panel())

    def test_a_training_pair_and_a_forecast_read_the_same_figure(self):
        for lead in LEADS:
            self.assertEqual(self.table.at(lead, 9), self.table.read(lead, 9 - lead))

    def test_the_decision_days_own_row_is_not_read(self):
        # Recorded mutation: see the module docstring (`BillLessIorbTable.source_row`).
        for lead in LEADS:
            served = self.table.read(lead, 8 - lead)[sc.BILL_LESS_IORB]
            self.assertAlmostEqual(served, unit(8 - lead - 1))
            self.assertNotAlmostEqual(served, unit(8 - lead))

    def test_a_figure_read_from_the_decision_row_is_refused(self):
        self.table.source_row = lambda lead, row: row - lead  # the same-day rate
        with self.assertRaises(LookAheadError):
            self.table.read(3, 6)

    def test_a_figure_read_from_a_later_row_is_refused(self):
        self.table.source_row = lambda lead, row: row - lead + 1
        with self.assertRaises(LookAheadError):
            self.table.read(2, 6)

    def test_an_older_row_than_the_previous_business_day_is_refused(self):
        self.table.source_row = lambda lead, row: row - lead - 2
        with self.assertRaises(StaleReadError):
            self.table.read(3, 6)

    def test_a_decision_with_no_previous_row_reads_nothing(self):
        self.assertEqual(self.table.read(3, 0), {})


class InformationSetTests(unittest.TestCase):
    """The source row is the one the published information rule reads at the 16:00 decision, with the real registry."""

    def rows(self):
        # The registry-driven rule needs only dates; business days are enough.
        return [d for d in business_days(date(2026, 3, 2), 40)]

    def test_the_source_row_is_the_row_the_16_00_rule_reads_for_the_bill_rate_and_iorb(self):
        dates = self.rows()
        table = sb.BillLessIorbTable([DailyObservation(d, {"tbill_4w": 4.0, "iorb": 3.9}) for d in dates])
        rule = InformationRule(REGISTRY, ("tbill_4w", "iorb"), decision_time=time(16, 0), horizon=1)
        for scored in range(10, 30):
            info = rule.information_set(dates, scored)
            read = {r.feature: r.row for r in info.reads}
            # The scored row is the target of lead 1 of the decision on row scored - 1; its figure comes from the row before that.
            self.assertEqual(table.source_row(1, scored), read["tbill_4w"])
            self.assertEqual(table.source_row(1, scored), read["iorb"])

    def test_the_18_00_rule_would_read_the_same_day_rate_and_the_arm_does_not(self):
        dates = self.rows()
        table = sb.BillLessIorbTable([DailyObservation(d, {"tbill_4w": 4.0, "iorb": 3.9}) for d in dates])
        rule = InformationRule(REGISTRY, ("tbill_4w",), decision_time=time(18, 0), horizon=1)
        for scored in range(10, 30):
            row = {r.feature: r.row for r in rule.information_set(dates, scored).reads}["tbill_4w"]
            self.assertEqual(row, scored - 1)
            self.assertEqual(table.source_row(1, scored), row - 1)


class FitTests(unittest.TestCase):
    """The term enters the fit beside the net terms and shifts the forecast and the pool."""

    def pairs(self):
        out = []
        for i, target in enumerate(range(5, 17)):
            gap = float(i % 4) - 1.5
            flags = {name: 0 for name in cal.ALL_TERMS}
            out.append(sc.StatePair(3.0 * gap, 1.0, flags, None, {}, -1, -1, {sc.BILL_LESS_IORB: gap}))
        return out

    def fit(self, **kw):
        return sc.fit_state_terms(
            self.pairs(), regressors=(), terms=cal.NO_FOMC_IORB, interact=False, robust=False, training_pairs="direct",
            min_flagged=3, extra=(sc.BILL_LESS_IORB,), **kw)

    def test_the_term_enters_the_fit(self):
        estimate = self.fit()
        self.assertIn(sc.BILL_LESS_IORB, estimate.terms)
        self.assertGreater(estimate.effect[sc.BILL_LESS_IORB], 1.0)

    def test_the_pool_is_what_the_term_leaves(self):
        estimate = self.fit()
        for p, z in zip(self.pairs(), estimate.residuals):
            self.assertAlmostEqual(z, p.raw / p.scale - estimate.effect[sc.BILL_LESS_IORB] * p.extras[sc.BILL_LESS_IORB])

    def test_the_shift_is_the_effect_times_the_figure(self):
        estimate = self.fit()
        flags = {name: 0 for name in cal.ALL_TERMS}
        shift = sc.standardised_shift(estimate, flags, None, None, {sc.BILL_LESS_IORB: 2.0})
        self.assertAlmostEqual(shift, 2.0 * estimate.effect[sc.BILL_LESS_IORB])

    def test_a_term_carried_by_fewer_than_three_pairs_stays_out(self):
        pairs = [p._replace(extras={sc.BILL_LESS_IORB: 1.0 if i < 2 else 0.0}) for i, p in enumerate(self.pairs())]
        estimate = sc.fit_state_terms(
            pairs, regressors=(), terms=cal.NO_FOMC_IORB, interact=False, robust=False, training_pairs="direct", min_flagged=3,
            extra=(sc.BILL_LESS_IORB,))
        self.assertNotIn(sc.BILL_LESS_IORB, estimate.terms)

    def test_a_one_step_fit_still_raises(self):
        with self.assertRaises(ValueError):
            sc.fit_state_terms(
                self.pairs(), regressors=("tbill_4w",), terms=cal.NO_FOMC_IORB, interact=False, robust=False,
                training_pairs="one_step", extra=(sc.BILL_LESS_IORB,))

    def test_the_other_extras_are_unchanged(self):
        self.assertEqual(sc.IORB_EXTRAS, ("iorb_signed", "iorb_technical"))
        self.assertEqual(sc.SIZE_EXTRAS, ("net_coupon", "net_bill", "gross_coupon"))
        self.assertEqual(sc.PRICE_EXTRAS, (sc.BILL_LESS_IORB,))
        self.assertEqual(sc.EXTRA_TERMS, sc.IORB_EXTRAS + sc.SIZE_EXTRAS + sc.CMB_EXTRAS + sc.OPS_EXTRAS + sc.PRICE_EXTRAS)


class ArmTests(unittest.TestCase):

    def test_the_arm_is_the_candidate_with_the_one_term(self):
        arm = sb.BILL_ARM
        self.assertEqual(arm.name, "sc_s3_ann_net_bill")
        self.assertEqual(arm.extra, (sc.BILL_LESS_IORB,))
        self.assertEqual(dataclasses.replace(arm, name=s3c_announced.ANN_NET_ARM.name, role=s3c_announced.ANN_NET_ARM.role, extra=()),
                         s3c_announced.ANN_NET_ARM)

    def test_the_arm_is_sized_robust_and_direct(self):
        self.assertTrue(sb.BILL_ARM.sized)
        self.assertTrue(sb.BILL_ARM.robust)
        self.assertFalse(sb.BILL_ARM.interact)
        self.assertEqual(sb.TRAINING_PAIRS, "direct")


if __name__ == "__main__":
    unittest.main()
