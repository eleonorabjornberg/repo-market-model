"""The cash management bill term of (s3c-ann-net-cmb): the bill leg of (s3c-ann-net) split into regular bills and cash management bills, each read
from the auction announcement (#1356; H5 step 3; her ruling of 2 November 2026 on avenue #1306).

`repo_model.s3c_cmb` is a new read path. `CmbSizeTable` serves, at leads 2 to 5, the signed net of the regular bills in place of the bill net
of (s3c-ann-net), and `CmbTerms` the cash management bill term beside it, as a 0/1 flag (`cmb_flag`) or as a size (`cmb_net`, USD 100 bn); at
lead 1 it is (s3c-ann-net)'s table exactly and serves no cash management bill term. Each figure counts an auction only when its announcement is at
or before the decision instant; the `prior_day_only` reading counts a cash management bill only when it was announced before the decision day
(finding #1301: the release time of a bill announced "for immediate release" is not verifiable). The split is exact: the regular bill net and
the cash management bill net add up to the bill net of `net_settlement.net_for_day`, at every instant.

What these tests pin: that sum; the value of each leg on a hand case; the instant of every figure (an auction announced after the decision is
not read, one announced on the decision day at 12:00 is, at the 18:00 decision, and not under `prior_day_only`); a training figure and a forecast
figure are the same function; `read` refuses, with `LookAheadError`, a figure that counts an announcement made after the decision, and, with
`StaleReadError`, a flag that leaves out an announced cash management bill; lead 1 is (s3c-ann-net)'s; the fit takes the cash management bill
term beside the sized settlement terms; and the arms are (s3c-ann-net) with the named change only.

Recorded mutation (leakage, #1356): in `s3c_cmb.CmbSizeTable._split`, the decision instant
`datetime.combine(self.dates[decision_row], self._time)` was changed to `datetime.combine(self.dates[target_row], self._time)` (the figure read at
the target day's own instant, when every auction announced by the target day is counted).
`ReadGuardTests.test_an_auction_announced_after_the_decision_is_not_read` then failed with `LookAheadError` (the read of the lead-3 forecast
counted a cash management bill announced after its decision; the guard in `CmbTerms.read` refused it); restored, it passes.
"""

from __future__ import annotations

import dataclasses
import sys
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model import net_settlement as ns, s3c_announced, s3c_cmb, s3c_net  # noqa: E402
from repo_model import spread_mr_calendar as cal, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.asof import StaleReadError  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

import test_s3c_announced as base  # noqa: E402

DAYS = base.DAYS
NOON = time(12, 0)
TARGET = DAYS[9]


def auction(announced, *, offering, cmb=False, maturing=50.0, bill=True, settles=TARGET):
    return ns.Auction(settles, "Bill" if bill else "Note", bill, offering, maturing, 0.0, datetime.combine(announced, NOON), None, cmb)


def tables(auctions, **kw):
    rows = base.panel()
    size = s3c_cmb.CmbSizeTable(rows, auctions, **kw)
    return size, s3c_cmb.CmbTerms(size)


class SplitTests(unittest.TestCase):
    """The regular bills and the cash management bills add up to the bill net, whatever is announced."""

    def setUp(self):
        # A 60 bn regular bill announced on DAYS[4] and a 30 bn cash management bill on DAYS[7], both settling on TARGET; 50 bn of bills mature.
        self.auctions = [auction(DAYS[4], offering=60.0), auction(DAYS[7], offering=30.0, cmb=True)]

    def test_the_split_adds_up_to_the_bill_net_at_every_instant(self):
        for day in DAYS:
            instant = datetime.combine(day, time(18, 0))
            regular, cmb_net = s3c_cmb.split_bill_net(self.auctions, instant)
            self.assertAlmostEqual(regular + cmb_net, s3c_net.net_by_term(self.auctions, instant)["settlement_bill"])

    def test_the_legs_on_a_hand_case(self):
        after = datetime.combine(DAYS[7], time(18, 0))
        regular, cmb_net = s3c_cmb.split_bill_net(self.auctions, after)
        self.assertAlmostEqual(regular, 10.0)   # 60 regular less the 50 maturing
        self.assertAlmostEqual(cmb_net, 30.0)   # the cash management bill's offering
        before = datetime.combine(DAYS[6], time(18, 0))
        self.assertEqual(s3c_cmb.split_bill_net(self.auctions, before), (10.0, 0.0))

    def test_an_unannounced_cash_management_bill_does_not_make_the_class_partly_announced(self):
        before = datetime.combine(DAYS[6], time(18, 0))
        self.assertAlmostEqual(s3c_cmb.split_bill_net(self.auctions, before)[0], 10.0)

    def test_a_class_partly_announced_reads_zero_in_both_legs(self):
        auctions = self.auctions + [auction(DAYS[8], offering=20.0)]
        instant = datetime.combine(DAYS[7], time(18, 0))
        self.assertEqual(s3c_cmb.split_bill_net(auctions, instant), (0.0, 0.0))

    def test_a_day_with_only_cash_management_bills_puts_its_whole_net_in_the_cash_management_term(self):
        only = [auction(DAYS[7], offering=30.0, cmb=True, maturing=0.0)]
        self.assertEqual(s3c_cmb.split_bill_net(only, datetime.combine(DAYS[7], time(18, 0))), (0.0, 30.0))

    def test_the_prior_day_reading_ignores_a_cash_management_bill_announced_on_the_decision_day(self):
        same_day = datetime.combine(DAYS[7], time(18, 0))
        self.assertEqual(s3c_cmb.split_bill_net(self.auctions, same_day, prior_day_only=True), (10.0, 0.0))
        next_day = datetime.combine(DAYS[8], time(18, 0))
        self.assertEqual(s3c_cmb.split_bill_net(self.auctions, next_day, prior_day_only=True), (10.0, 30.0))


class ValueTests(unittest.TestCase):

    def setUp(self):
        self.auctions = [auction(DAYS[4], offering=60.0), auction(DAYS[7], offering=30.0, cmb=True),
                         auction(DAYS[2], offering=40.0, bill=False, maturing=25.0)]
        self.size, self.terms = tables(self.auctions)

    def test_the_sized_terms_at_leads_2_to_5_are_the_regular_bill_net_and_the_coupon_net(self):
        got = self.size.sizes_at(2, 9)   # the decision of DAYS[7] reads all three
        self.assertAlmostEqual(got["settlement_bill"], 10.0)
        self.assertAlmostEqual(got["settlement_coupon"], 15.0)

    def test_the_flag_is_one_from_the_decision_after_the_announcement(self):
        self.assertEqual({h: self.terms.at(h, 9)[sc.CMB_FLAG] for h in (2, 3, 4, 5)}, {2: 1, 3: 0, 4: 0, 5: 0})

    def test_the_size_is_in_units_of_100_bn(self):
        both = s3c_cmb.CmbTerms(self.size, (sc.CMB_FLAG, sc.CMB_NET))
        self.assertAlmostEqual(both.at(2, 9)[sc.CMB_NET], 0.30)
        self.assertEqual(both.at(3, 9), {sc.CMB_FLAG: 0, sc.CMB_NET: 0.0})

    def test_lead_1_is_the_net_arms_table_and_serves_no_cash_management_term(self):
        plain = s3c_announced.AnnouncedNetSizeTable(base.panel(), self.auctions)
        self.assertEqual(self.size.sizes_at(1, 9), plain.sizes_at(1, 9))
        self.assertEqual(self.size.sizes_at(1, 9)["settlement_bill"], 40.0)   # the cash management bill is still in the bill net
        self.assertEqual(self.terms.at(1, 9), {})
        self.assertEqual(self.terms.read(1, 8), {})

    def test_a_subset_of_names_serves_only_those(self):
        with self.assertRaises(ValueError):
            s3c_cmb.CmbTerms(self.size, ("net_coupon",))
        self.assertEqual(set(s3c_cmb.CmbTerms(self.size, (sc.CMB_NET,)).at(2, 9)), {sc.CMB_NET})

    def test_the_announcement_on_the_decision_day_is_public_at_the_decision_unless_the_reading_is_prior_day(self):
        self.assertEqual(self.terms.read(2, 7)[sc.CMB_FLAG], 1)
        _, strict = tables(self.auctions, prior_day_only=True)
        self.assertEqual(strict.read(2, 7)[sc.CMB_FLAG], 0)
        far = [auction(DAYS[3], offering=30.0, cmb=True)]
        _, strict_far = tables(far, prior_day_only=True)
        self.assertEqual(strict_far.read(3, 6)[sc.CMB_FLAG], 1)   # announced on DAYS[3], read on the decision of DAYS[6]
        self.assertEqual(strict_far.read(5, 4)[sc.CMB_FLAG], 1)   # announced the day before the decision of DAYS[4]

    def test_a_training_pair_and_a_forecast_read_the_same_figure(self):
        for lead in (2, 3, 4, 5):
            self.assertEqual(self.terms.at(lead, 9), self.terms.read(lead, 9 - lead))
            self.assertEqual(self.size.sizes_at(lead, 9), self.size.read(lead, 9 - lead))


class ReadGuardTests(unittest.TestCase):
    """A forecast reads the figure as of its own decision, and refuses one that is not."""

    def setUp(self):
        self.auctions = [auction(DAYS[4], offering=60.0), auction(DAYS[7], offering=30.0, cmb=True)]
        self.size, self.terms = tables(self.auctions)

    def test_an_auction_announced_after_the_decision_is_not_read(self):
        # Recorded mutation: see the module docstring (`CmbSizeTable._split`).
        self.assertEqual(self.terms.read(3, 6)[sc.CMB_FLAG], 0)
        self.assertEqual(self.size.read(3, 6)["settlement_bill"], 10.0)
        self.assertEqual(s3c_cmb.CmbTerms(self.size, (sc.CMB_NET,)).read(3, 6)[sc.CMB_NET], 0.0)

    def test_a_flag_that_counts_a_cash_management_bill_announced_after_the_decision_is_refused(self):
        self.size._split_cache[(6, 9)] = dict(self.size._split(7, 9))
        with self.assertRaises(LookAheadError):
            self.terms.read(3, 6)

    def test_a_flag_that_leaves_out_an_announced_cash_management_bill_is_refused(self):
        self.size._split_cache[(7, 9)] = dict(self.size._split(6, 9))
        with self.assertRaises(StaleReadError):
            self.terms.read(2, 7)

    def test_a_size_that_is_not_the_one_announced_is_refused(self):
        net = s3c_cmb.CmbTerms(self.size, (sc.CMB_NET,))
        self.size._split_cache[(6, 9)] = dict(self.size._split(7, 9))
        with self.assertRaises(LookAheadError):
            net.read(3, 6)

    def test_the_sized_terms_are_refused_when_they_are_not_the_ones_announced(self):
        size, _ = tables(self.auctions + [auction(DAYS[7], offering=40.0, bill=False, maturing=25.0)])
        size._split_cache[(6, 9)] = dict(size._split(7, 9))
        with self.assertRaises(LookAheadError):
            size.read(3, 6)


class FitTests(unittest.TestCase):
    """The cash management bill term enters the fit beside the sized settlement terms."""

    def pairs(self):
        out = []
        for target in range(5, 17):
            cmb = 1 if target % 3 == 0 else 0
            sizes = {"settlement_coupon": 0.0, "settlement_bill": 0.2 if target % 2 == 0 else 0.0}
            flags = {name: 0 for name in cal.ALL_TERMS}
            out.append(sc.StatePair(3.0 * cmb + 0.5 * sizes["settlement_bill"], 1.0, flags, sc.STATE_MAX, sizes, -1, -1,
                                    {sc.CMB_FLAG: float(cmb), sc.CMB_NET: 0.3 * cmb}))
        return out

    def fit(self, extra):
        return sc.fit_state_terms(self.pairs(), regressors=(), terms=cal.NO_FOMC_IORB, interact=False, robust=False, sized=True,
                                  training_pairs="direct", min_flagged=3, extra=extra)

    def test_the_flag_enters_beside_the_sized_bill_term(self):
        estimate = self.fit((sc.CMB_FLAG,))
        self.assertIn("settlement_bill", estimate.terms)
        self.assertIn(sc.CMB_FLAG, estimate.terms)
        self.assertGreater(estimate.effect[sc.CMB_FLAG], 1.0)

    def test_the_size_enters_beside_the_sized_bill_term(self):
        self.assertIn(sc.CMB_NET, self.fit((sc.CMB_NET,)).terms)

    def test_the_shift_is_the_sized_term_plus_the_cash_management_term(self):
        estimate = self.fit((sc.CMB_FLAG,))
        flags = {name: 0 for name in cal.ALL_TERMS}
        shift = sc.standardised_shift(estimate, flags, sc.STATE_MAX, {"settlement_bill": 0.2}, {sc.CMB_FLAG: 1.0})
        sized = sc.standardised_shift(estimate, flags, sc.STATE_MAX, {"settlement_bill": 0.2}, {})
        self.assertAlmostEqual(shift - sized, estimate.effect[sc.CMB_FLAG])

    def test_a_one_step_fit_still_raises(self):
        with self.assertRaises(ValueError):
            sc.fit_state_terms(self.pairs(), regressors=("treasury_settlement_bills",), terms=cal.NO_FOMC_IORB, interact=False, robust=False,
                               sized=True, training_pairs="one_step", extra=(sc.CMB_FLAG,))

    def test_the_extras_of_existing_arms_are_unchanged(self):
        self.assertEqual(sc.IORB_EXTRAS, ("iorb_signed", "iorb_technical"))
        self.assertEqual(sc.SIZE_EXTRAS, (sc.NET_COUPON, sc.NET_BILL, sc.GROSS_COUPON))
        self.assertEqual(sc.EXTRA_TERMS, sc.IORB_EXTRAS + sc.SIZE_EXTRAS + sc.CMB_EXTRAS)


class ArmTests(unittest.TestCase):

    def check(self, arm, extra, name):
        self.assertEqual(arm.name, name)
        self.assertEqual(arm.extra, extra)
        self.assertEqual(dataclasses.replace(arm, name=s3c_announced.ANN_NET_ARM.name, role=s3c_announced.ANN_NET_ARM.role, extra=()),
                         s3c_announced.ANN_NET_ARM)
        self.assertTrue(arm.sized)

    def test_the_arms_are_the_net_arm_with_the_named_term_only(self):
        self.check(s3c_cmb.FLAG_ARM, (sc.CMB_FLAG,), "sc_s3_ann_net_cmb_flag")
        self.check(s3c_cmb.SIZE_ARM, (sc.CMB_NET,), "sc_s3_ann_net_cmb_size")
        self.check(s3c_cmb.FLAG_PRIOR_ARM, (sc.CMB_FLAG,), "sc_s3_ann_net_cmb_flag_prior")
        self.check(s3c_cmb.SIZE_PRIOR_ARM, (sc.CMB_NET,), "sc_s3_ann_net_cmb_size_prior")

    def test_the_arms_fit_on_direct_pairs(self):
        self.assertEqual(s3c_cmb.TRAINING_PAIRS, "direct")
        self.assertEqual(s3c_cmb.TRAINING_PAIRS, s3c_announced.TRAINING_PAIRS)


if __name__ == "__main__":
    unittest.main()
