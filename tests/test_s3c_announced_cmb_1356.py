"""The cash management bill term of (s3c-ann-net-cmb): the CMB leg split out of the bill leg, read from the announcement (#1356; H5 step 3, avenue
#1306; her ruling of 2 November 2026).

`repo_model.s3c_announced.AnnouncedNetExCmbSizeTable` is #1273's announced net with the cash management bills' offerings taken out of the net bill
(net bill ex-CMB), and `AnnouncedCmbTerms` serves the CMB term itself, at every lead, as an extra term of the state-calendar fit
(`spread_mr_state_calendar.CMB_EXTRAS`, read through `walk`'s `iorb` argument): `cmb_flag` (1 when the CMBs settling on the target day that had been
announced by the decision instant offer more than zero) or `cmb_size` (their offering, USD 100 bn). Neither is read by a published declaration or
record.

What these tests pin: the split is exact (net bill ex-CMB plus the announced CMB offering is the net bill of (s3c-ann-net) wherever the bill class
is counted); a CMB announced after the decision instant is not counted and does not make the bill class partly announced (#738); a CMB announced by
the instant is counted even when the regular bills of the day are not yet announced (the declared gate); a training figure and a forecast figure are
the same function of the same announcements; `read` refuses, with `LookAheadError`, a figure that counts a CMB announced after the decision, and,
with `StaleReadError`, one that leaves an announced CMB out; the ex-CMB net is refused when it is not the one announced at the instant; the arms are
(s3c-ann-net) with the one extra term; a CMB term enters the fit beside the sized settlement terms, and a one-step fit still raises.

Recorded mutation (leakage, #1356): in `s3c_announced.AnnouncedCmbTerms.at`, the CMB amount read from `self._counted(lead, row)` was changed to
`self._counted(0, row)` (the figure read at the target day's own instant, when every CMB announced by the target day is counted).
`CmbReadTests.test_a_cmb_announced_after_the_decision_is_not_read` then failed with `LookAheadError` (the read of the lead-3 forecast counted a CMB
announced after its decision; the guard in `read` refused it); restored, it passes.
"""

from __future__ import annotations

import dataclasses
import sys
import unittest
from datetime import datetime, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model import net_settlement as ns, s3c_announced, s3c_net  # noqa: E402
from repo_model import spread_mr_calendar as cal, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.asof import StaleReadError  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

import test_s3c_announced as base  # noqa: E402

DAYS = base.DAYS
NOON = time(12, 0)
TARGET = DAYS[9]


def bill(announced, offering, *, cmb, maturing=20.0):
    return ns.Auction(TARGET, "Bill", True, offering, maturing, 0.0, datetime.combine(announced, NOON), None, cmb)


def coupon(announced, offering=40.0, maturing=25.0):
    return ns.Auction(TARGET, "Note", False, offering, maturing, 0.0, datetime.combine(announced, NOON), None)


def tables(auctions, names=sc.CMB_EXTRAS):
    rows = base.panel()
    ex = s3c_announced.AnnouncedNetExCmbSizeTable(rows, auctions)
    terms = s3c_announced.AnnouncedCmbTerms(rows, auctions, names)
    return ex, terms


class SplitTests(unittest.TestCase):
    """The CMB leg is split out of the bill leg without changing the sum."""

    def test_the_two_legs_sum_to_the_net_bill_of_s3c_ann_net(self):
        auctions = [bill(DAYS[5], 30.0, cmb=False), bill(DAYS[6], 60.0, cmb=True), coupon(DAYS[5])]
        instant = datetime.combine(DAYS[7], time(18, 0))
        whole = s3c_net.net_by_term(auctions, instant)
        ex = s3c_announced.net_by_term_ex_cmb(auctions, instant)
        self.assertAlmostEqual(whole["settlement_bill"], 30.0 + 60.0 - 20.0)
        self.assertAlmostEqual(ex["settlement_bill"], 30.0 - 20.0)
        self.assertAlmostEqual(ex["settlement_bill"] + s3c_announced.cmb_offering(auctions, instant), whole["settlement_bill"])
        self.assertEqual(ex["settlement_coupon"], whole["settlement_coupon"])

    def test_a_cmb_announced_after_the_instant_is_neither_counted_nor_makes_the_class_partly_announced(self):
        auctions = [bill(DAYS[5], 30.0, cmb=False), bill(DAYS[8], 60.0, cmb=True)]
        instant = datetime.combine(DAYS[7], time(18, 0))
        self.assertEqual(s3c_announced.cmb_offering(auctions, instant), 0.0)
        self.assertAlmostEqual(s3c_announced.net_by_term_ex_cmb(auctions, instant)["settlement_bill"], 10.0)

    def test_a_cmb_is_counted_while_the_regular_bills_are_not_yet_announced(self):
        auctions = [bill(DAYS[8], 30.0, cmb=False), bill(DAYS[5], 60.0, cmb=True)]
        instant = datetime.combine(DAYS[7], time(18, 0))
        self.assertEqual(s3c_net.net_by_term(auctions, instant)["settlement_bill"], 0.0)  # the class is partly announced: (s3c-ann-net) reads 0
        self.assertEqual(s3c_announced.net_by_term_ex_cmb(auctions, instant)["settlement_bill"], 0.0)
        self.assertEqual(s3c_announced.cmb_offering(auctions, instant), 60.0)

    def test_a_coupon_is_not_a_cmb(self):
        instant = datetime.combine(DAYS[7], time(18, 0))
        self.assertEqual(s3c_announced.cmb_offering([coupon(DAYS[5])], instant), 0.0)


class CmbValueTests(unittest.TestCase):

    def setUp(self):
        # A 30 bn regular bill announced on DAYS[8]; a 60 bn CMB announced on DAYS[4] and a 20 bn one on DAYS[7]; all settle on the target.
        self.auctions = [bill(DAYS[8], 30.0, cmb=False), bill(DAYS[4], 60.0, cmb=True), bill(DAYS[7], 20.0, cmb=True)]
        self.ex, self.terms = tables(self.auctions)

    def test_the_size_is_the_announced_cmb_offering_in_units_of_100_bn(self):
        got = {h: round(self.terms.at(h, 9)[sc.CMB_SIZE], 6) for h in (1, 2, 3, 4, 5)}
        # DAYS[7] is the decision of lead 2, DAYS[4] that of lead 5: the 20 bn CMB is public from lead 2, the 60 bn one from lead 5.
        self.assertEqual(got, {1: 0.8, 2: 0.8, 3: 0.6, 4: 0.6, 5: 0.6})

    def test_the_flag_is_one_when_a_cmb_is_announced(self):
        self.assertEqual({h: self.terms.at(h, 9)[sc.CMB_FLAG] for h in (1, 2, 3, 4, 5)}, {1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0})
        late = tables([bill(DAYS[7], 20.0, cmb=True)])[1]
        self.assertEqual({h: late.at(h, 9)[sc.CMB_FLAG] for h in (1, 2, 3)}, {1: 1.0, 2: 1.0, 3: 0.0})

    def test_the_net_bill_ex_cmb_is_in_units_of_100_bn_and_the_cmb_is_out_of_it(self):
        sizes = self.ex.sizes_at(1, 9)
        self.assertAlmostEqual(sizes["settlement_bill"], (30.0 - 20.0) / 100.0 * 100.0)  # the table serves USD bn; the arm divides by SIZE_UNIT
        self.assertEqual(sizes["settlement_coupon"], 0.0)

    def test_a_subset_of_names_serves_only_those(self):
        flag = tables(self.auctions, names=(sc.CMB_FLAG,))[1]
        self.assertEqual(set(flag.at(3, 9)), {sc.CMB_FLAG})
        with self.assertRaises(ValueError):
            tables(self.auctions, names=(sc.GROSS_COUPON,))

    def test_a_row_without_a_decision_row_reads_zero(self):
        self.assertEqual(self.terms.at(5, 2), {sc.CMB_FLAG: 0.0, sc.CMB_SIZE: 0.0})


class CmbReadTests(unittest.TestCase):
    """A forecast reads the CMB term as of its own decision, and refuses one that is not."""

    def setUp(self):
        self.late = [bill(DAYS[7], 20.0, cmb=True)]
        self.ex, self.terms = tables(self.late)

    def test_a_cmb_announced_after_the_decision_is_not_read(self):
        # Recorded mutation: see the module docstring (`AnnouncedCmbTerms.at`).
        self.assertEqual(self.terms.read(3, 6)[sc.CMB_SIZE], 0.0)
        self.assertAlmostEqual(self.terms.read(2, 7)[sc.CMB_SIZE], 0.2)

    def test_the_announcement_on_the_decision_day_is_public_at_the_decision(self):
        self.assertAlmostEqual(self.terms.read(1, 8)[sc.CMB_SIZE], 0.2)
        self.assertEqual(self.terms.read(1, 8)[sc.CMB_FLAG], 1.0)

    def test_a_training_pair_and_a_forecast_read_the_same_figure(self):
        for lead in (1, 2, 3, 4, 5):
            self.assertEqual(self.terms.at(lead, 9), self.terms.read(lead, 9 - lead))

    def test_a_figure_that_counts_a_cmb_announced_after_the_decision_is_refused(self):
        self.terms._counted_cache[(3, 9)] = tuple(self.late)
        with self.assertRaises(LookAheadError):
            self.terms.read(3, 6)

    def test_a_figure_that_leaves_out_an_announced_cmb_is_refused(self):
        self.terms._counted_cache[(2, 9)] = ()
        with self.assertRaises(StaleReadError):
            self.terms.read(2, 7)

    def test_the_net_bill_ex_cmb_is_refused_when_it_is_not_the_one_announced_at_the_decision(self):
        auctions = [bill(DAYS[7], 30.0, cmb=False)]
        ex = tables(auctions)[0]
        ex._cache[(6, 9)] = dict(ex._value(9, 9))
        with self.assertRaises(LookAheadError):
            ex.read(3, 6)

    def test_the_ex_cmb_net_reads_the_same_as_the_training_figure(self):
        auctions = [bill(DAYS[5], 30.0, cmb=False), bill(DAYS[6], 60.0, cmb=True)]
        ex = tables(auctions)[0]
        for lead in (1, 2, 3):
            self.assertEqual(ex.sizes_at(lead, 9), ex.read(lead, 9 - lead))


class FitWithCmbTermsTests(unittest.TestCase):
    """A CMB term enters the fit beside the sized settlement terms and shifts the forecast."""

    def pairs(self):
        out = []
        for target in range(5, 17):
            cmb = 0.6 if target % 3 == 0 else 0.0
            flags = {name: 0 for name in cal.ALL_TERMS}
            out.append(sc.StatePair(
                5.0 * cmb + 0.5 * (target % 2), 1.0, flags, 3.0, {"settlement_coupon": 20.0 * (target % 2), "settlement_bill": 5.0 * (target % 4)},
                -1, -1, {sc.CMB_SIZE: cmb, sc.CMB_FLAG: 1.0 if cmb else 0.0}))
        return out

    def fit(self, extra):
        return sc.fit_state_terms(
            self.pairs(), regressors=(), terms=cal.NO_FOMC_IORB, interact=False, robust=False, training_pairs="direct", min_flagged=3,
            sized=True, extra=extra)

    def test_the_size_enters_beside_the_sized_terms(self):
        estimate = self.fit((sc.CMB_SIZE,))
        self.assertIn(sc.CMB_SIZE, estimate.terms)
        self.assertIn("settlement_bill", estimate.terms)
        self.assertGreater(estimate.effect[sc.CMB_SIZE], 1.0)

    def test_the_flag_enters_as_an_extra_term(self):
        estimate = self.fit((sc.CMB_FLAG,))
        self.assertIn(sc.CMB_FLAG, estimate.terms)

    def test_a_term_with_fewer_than_three_pairs_does_not_enter(self):
        pairs = [p._replace(extras={sc.CMB_SIZE: 0.0, sc.CMB_FLAG: 0.0}) for p in self.pairs()]
        estimate = sc.fit_state_terms(
            pairs, regressors=(), terms=cal.NO_FOMC_IORB, interact=False, robust=False, training_pairs="direct", min_flagged=3, sized=True,
            extra=(sc.CMB_SIZE,))
        self.assertNotIn(sc.CMB_SIZE, estimate.terms)

    def test_the_shift_adds_the_cmb_term(self):
        estimate = self.fit((sc.CMB_SIZE,))
        flags = {name: 0 for name in cal.ALL_TERMS}
        without = sc.standardised_shift(estimate, flags, 3.0, {"settlement_coupon": 0.0, "settlement_bill": 0.0}, {sc.CMB_SIZE: 0.0})
        with_cmb = sc.standardised_shift(estimate, flags, 3.0, {"settlement_coupon": 0.0, "settlement_bill": 0.0}, {sc.CMB_SIZE: 0.5})
        self.assertAlmostEqual(with_cmb - without, 0.5 * estimate.effect[sc.CMB_SIZE])

    def test_a_one_step_fit_still_raises(self):
        with self.assertRaises(ValueError):
            sc.fit_state_terms(
                self.pairs(), regressors=("treasury_settlement_coupons",), terms=cal.NO_FOMC_IORB, interact=False, robust=False,
                training_pairs="one_step", sized=True, extra=(sc.CMB_SIZE,))

    def test_the_other_extras_are_unchanged(self):
        self.assertEqual(sc.IORB_EXTRAS, ("iorb_signed", "iorb_technical"))
        self.assertEqual(sc.SIZE_EXTRAS, ("net_coupon", "net_bill", "gross_coupon"))
        self.assertEqual(sc.CMB_EXTRAS, ("cmb_flag", "cmb_size"))
        self.assertEqual(sc.EXTRA_TERMS, sc.IORB_EXTRAS + sc.SIZE_EXTRAS + sc.CMB_EXTRAS + sc.OPS_EXTRAS + sc.MISSING_EXTRAS + sc.PRICE_EXTRAS + (sc.H9_FORECAST,))  # #1349 adds the take-up extras, #1390 the missingness flag, #1345 the H9 forecast


class ArmTests(unittest.TestCase):

    def test_each_form_is_s3c_ann_net_with_the_one_extra_term(self):
        for arm, extra in ((s3c_announced.CMB_FLAG_ARM, sc.CMB_FLAG), (s3c_announced.CMB_SIZE_ARM, sc.CMB_SIZE)):
            with self.subTest(arm=arm.name):
                self.assertEqual(arm.extra, (extra,))
                self.assertTrue(arm.sized)
                self.assertEqual(
                    dataclasses.replace(arm, name=s3c_announced.ANN_NET_ARM.name, role=s3c_announced.ANN_NET_ARM.role, extra=()),
                    s3c_announced.ANN_NET_ARM)

    def test_the_names_are_the_declared_ones(self):
        self.assertEqual(s3c_announced.CMB_FLAG_ARM.name, "sc_s3_ann_net_cmbf")
        self.assertEqual(s3c_announced.CMB_SIZE_ARM.name, "sc_s3_ann_net_cmbs")


if __name__ == "__main__":
    unittest.main()
