"""The size terms of (s3c-ann-flagnet) and (s3c-ann-gross): the announced net and the announced gross coupon offering, as extra terms of the
state-calendar fit (#1321; H5 step 3; her ruling of 30 October 2026 on avenue #1318, ledger item 81).

`repo_model.s3c_announced.AnnouncedSizeTerms` is a new read path. It serves, at every lead, the announced gross coupon offering of the target day
(`gross_coupon`, USD 100 bn) and #1273's announced net (`net_coupon`, `net_bill`, USD 100 bn), each as the decision `lead` rows before could read
it. It is the table `spread_mr_state_calendar.walk` calls through its `iorb` argument (`at`, `read`). `spread_mr_state_calendar.SIZE_EXTRAS` are the
names the fit accepts as extra terms. The published declaration, the live record and (s3c)'s table do not read it.

What these tests pin: the size at a lead is the announced offering at the decision instant (an auction announced after the decision is not counted;
one announced on the decision day at 12:00 is, at the 18:00 decision of `repo_model.decision_instant`); a training figure and a forecast figure are
the same function of the same announcements; `read` refuses, with `LookAheadError`, a figure that counts an auction announced after the decision,
and, with `StaleReadError`, one that leaves an announced auction out; the net extras are #1273's net over USD 100 bn; the fit takes a size term beside
a flag (pool and shift both use it) and in place of one, and a one-step fit still raises; and the arms are (s3) with the named change only.

Recorded mutation (leakage, #1321): in `s3c_announced.AnnouncedSizeTerms.at`, the gross coupon amount read from
`self.terms._counted(lead, row)` was changed to `self.terms._counted(0, row)` (the figure read at the target day's own instant, when every
auction announced by the target day is counted). `SizeReadTests.test_an_auction_announced_after_the_decision_is_not_read` then failed with
`LookAheadError` (the read of the lead-3 forecast counted an auction announced after its decision; the guard in `read` refused it); restored, it
passes.
"""

from __future__ import annotations

import dataclasses
import sys
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model import net_settlement as ns, s3c_announced, settlement_dating as sd  # noqa: E402
from repo_model import spread_mr_calendar as cal, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.asof import StaleReadError  # noqa: E402
from repo_model.data import DailyObservation  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

import test_s3c_announced as base  # noqa: E402

DAYS = base.DAYS
NOON = time(12, 0)


def sizes_table(found, auctions, coupon_on=(), names=sc.SIZE_EXTRAS):
    rows = base.panel(coupon_on=coupon_on)
    terms = s3c_announced.AnnouncedTermTable(rows, [], found, calendar=[])
    net = s3c_announced.AnnouncedNetSizeTable(rows, auctions)
    return s3c_announced.AnnouncedSizeTerms(terms, net, names)


class SizeValueTests(unittest.TestCase):

    def setUp(self):
        self.target = DAYS[9]
        # A 40 bn coupon announced on DAYS[5], a 10 bn one announced on DAYS[7]; both settle on the target.
        self.found = base.results(base.record(DAYS[5], self.target), base.record(DAYS[7], self.target, amount="10000000000"))
        self.auctions = [ns.Auction(self.target, "Note", False, 40.0, 25.0, 0.0, datetime.combine(DAYS[5], NOON), None)]
        self.table = sizes_table(self.found, self.auctions, coupon_on={self.target})

    def test_the_gross_coupon_is_the_announced_offering_in_units_of_100_bn(self):
        got = {h: round(self.table.at(h, 9)[sc.GROSS_COUPON], 6) for h in (1, 2, 3, 4, 5)}
        # DAYS[7]'s announcement is public from the decision of DAYS[7] (lead 2), DAYS[5]'s from the decision of DAYS[5] (lead 4).
        self.assertEqual(got, {1: 0.5, 2: 0.5, 3: 0.4, 4: 0.4, 5: 0.0})

    def test_the_net_extras_are_the_net_of_1273_in_units_of_100_bn(self):
        at = self.table.at(4, 9)
        self.assertAlmostEqual(at[sc.NET_COUPON], 0.15)
        self.assertEqual(at[sc.NET_BILL], 0.0)

    def test_a_subset_of_names_serves_only_those(self):
        only = sizes_table(self.found, self.auctions, names=(sc.GROSS_COUPON,))
        self.assertEqual(set(only.at(3, 9)), {sc.GROSS_COUPON})
        with self.assertRaises(ValueError):
            sizes_table(self.found, self.auctions, names=("settlement_coupon",))

    def test_a_row_without_a_decision_row_reads_zero_gross(self):
        early = sizes_table(base.results(base.record(DAYS[0], DAYS[2])), [], names=(sc.GROSS_COUPON,))
        self.assertEqual(early.at(5, 2), {sc.GROSS_COUPON: 0.0})


class SizeReadTests(unittest.TestCase):
    """A forecast reads the size as of its own decision, and refuses one that is not."""

    def setUp(self):
        self.target = DAYS[9]
        self.late = base.results(base.record(DAYS[7], self.target))
        self.table = sizes_table(self.late, [], coupon_on={self.target}, names=(sc.GROSS_COUPON,))

    def test_an_auction_announced_after_the_decision_is_not_read(self):
        # Recorded mutation: see the module docstring (`AnnouncedSizeTerms.at`).
        self.assertEqual(self.table.read(3, 6)[sc.GROSS_COUPON], 0.0)
        self.assertAlmostEqual(self.table.read(2, 7)[sc.GROSS_COUPON], 0.4)

    def test_the_announcement_on_the_decision_day_is_public_at_the_decision(self):
        self.assertAlmostEqual(self.table.read(1, 8)[sc.GROSS_COUPON], 0.4)

    def test_a_training_pair_and_a_forecast_read_the_same_figure(self):
        for lead in (1, 2, 3, 4, 5):
            self.assertEqual(self.table.at(lead, 9), self.table.read(lead, 9 - lead))

    def test_a_figure_that_counts_an_auction_announced_after_the_decision_is_refused(self):
        self.table.terms._counted_cache[(3, 9)] = {"settlement_coupon": (self.late[0],), "settlement_bill": ()}
        with self.assertRaises(LookAheadError):
            self.table.read(3, 6)

    def test_a_figure_that_leaves_out_an_announced_auction_is_refused(self):
        self.table.terms._counted_cache[(2, 9)] = {"settlement_coupon": (), "settlement_bill": ()}
        with self.assertRaises(StaleReadError):
            self.table.read(2, 7)

    def test_the_net_is_refused_when_it_is_not_the_one_announced_at_the_decision(self):
        auction = ns.Auction(self.target, "Note", False, 40.0, 25.0, 0.0, datetime.combine(DAYS[7], NOON), None)
        table = sizes_table(self.late, [auction], names=(sc.NET_COUPON,))
        table.net._cache[(6, 9)] = dict(table.net._value(9, 9))
        with self.assertRaises(LookAheadError):
            table.read(3, 6)


class FitWithSizeTermsTests(unittest.TestCase):
    """A size term enters the fit beside a flag and in place of one, and shifts the forecast and the pool."""

    def pairs(self, lead=3, with_flag=True):
        out = []
        for target in range(5, 15):
            net = 0.5 if target % 3 == 0 else 0.0
            flags = {name: 0 for name in cal.ALL_TERMS}
            flags["settlement_coupon"] = 1 if net else 0
            out.append(sc.StatePair(4.0 * net, 1.0, flags, None, {}, -1, -1, {sc.NET_COUPON: net, sc.NET_BILL: 0.0}))
        return out

    def fit(self, **kw):
        return sc.fit_state_terms(
            self.pairs(), regressors=(), terms=kw.pop("terms", cal.NO_FOMC_IORB), interact=False, robust=False,
            training_pairs="direct", min_flagged=3, **kw)

    def test_a_size_term_enters_beside_the_flag(self):
        estimate = self.fit(extra=(sc.NET_COUPON, sc.NET_BILL))
        self.assertIn("settlement_coupon", estimate.terms)
        self.assertIn(sc.NET_COUPON, estimate.terms)
        self.assertNotIn(sc.NET_BILL, estimate.terms)  # no pair carries it

    def test_the_pool_is_what_the_flag_and_the_size_leave(self):
        estimate = self.fit(extra=(sc.NET_COUPON,))
        pairs = self.pairs()
        for p, z in zip(pairs, estimate.residuals):
            expected = p.raw / p.scale - estimate.effect["settlement_coupon"] * p.flags["settlement_coupon"] - estimate.effect[sc.NET_COUPON] * p.extras[sc.NET_COUPON]
            self.assertAlmostEqual(z, expected)

    def test_the_shift_is_the_flag_term_plus_the_size_term(self):
        estimate = self.fit(extra=(sc.NET_COUPON,))
        flags = {name: 0 for name in cal.ALL_TERMS}
        flags["settlement_coupon"] = 1
        shift = sc.standardised_shift(estimate, flags, None, None, {sc.NET_COUPON: 0.5})
        self.assertAlmostEqual(shift, estimate.effect["settlement_coupon"] + 0.5 * estimate.effect[sc.NET_COUPON])

    def test_a_size_in_place_of_a_flag(self):
        terms = tuple(t for t in cal.NO_FOMC_IORB if t != "settlement_coupon")
        estimate = self.fit(terms=terms, extra=(sc.NET_COUPON,))
        self.assertNotIn("settlement_coupon", estimate.terms)
        self.assertGreater(estimate.effect[sc.NET_COUPON], 1.0)

    def test_a_one_step_fit_still_raises(self):
        with self.assertRaises(ValueError):
            sc.fit_state_terms(
                self.pairs(), regressors=("treasury_settlement_coupons",), terms=cal.NO_FOMC_IORB, interact=False, robust=False,
                training_pairs="one_step", extra=(sc.NET_COUPON,))

    def test_the_iorb_extras_are_unchanged(self):
        self.assertEqual(sc.IORB_EXTRAS, ("iorb_signed", "iorb_technical"))
        self.assertEqual(sc.EXTRA_TERMS, sc.IORB_EXTRAS + sc.SIZE_EXTRAS)


class ArmTests(unittest.TestCase):

    def test_flagnet_is_s3_with_the_two_net_terms_beside_the_flags(self):
        arm = s3c_announced.FLAGNET_ARM
        self.assertEqual(arm.name, "sc_s3_ann_flagnet")
        self.assertEqual(arm.extra, (sc.NET_COUPON, sc.NET_BILL))
        self.assertEqual(dataclasses.replace(arm, name=sc.ARMS[2].name, role=sc.ARMS[2].role, extra=()), sc.ARMS[2])

    def test_gross_sizes_the_coupon_leg_and_flags_the_bill_leg(self):
        arm = s3c_announced.GROSS_ARM
        self.assertEqual(arm.name, "sc_s3_ann_gross")
        self.assertNotIn("settlement_coupon", arm.location)
        self.assertIn("settlement_bill", arm.location)
        self.assertEqual(arm.extra, (sc.GROSS_COUPON,))
        self.assertEqual(sc.ridge_of(arm), sc.ridge_of(sc.ARMS[2]))
        self.assertTrue(arm.robust)
        self.assertFalse(arm.sized)
        rest = tuple(t for t in sc.ARMS[2].location if t != "settlement_coupon")
        self.assertEqual(arm.location, rest)

    def test_the_arms_fit_on_direct_pairs(self):
        self.assertEqual(s3c_announced.TRAINING_PAIRS, "direct")


if __name__ == "__main__":
    unittest.main()
