"""(s3c-net): net bill and net coupon settlement in place of the gross flags (#1273; H5 step 3, ledger item 65 on #1116).

`repo_model.s3c_net` supplies the two settlement terms of (s3c-net) as the signed net of the settlements dated on the target day
(the offerings less the announced publicly held maturing amount, `repo_model.net_settlement`), each figure read at its announcement:
an auction counts only when its `announcemt_date` is on or before the decision day, and the decision is made at 16:00 on that day.
This is a new read path (`NetSizeTable`), so it has a leakage test and a recorded mutation.

What these tests pin: the net of a target day by term (bill and coupon, the sign kept when more matures than settles); that an auction
announced after the decision instant is not in the figure (a class announced only after it reads 0, as `net_settlement` reads a class not
yet announced); that the figure for a target day is the one `net_settlement.with_net_settlement` would put on the row of the day before
when everything was announced by then; that the table is readable at lead 1 only, as the gross flags are (`spread_mr_calendar.TERMS`);
that a training pair and a forecast read the same figure; the arm is (s3) with `sized=True` and nothing else changed; the constant state
that makes the sized regressor the plain signed size in units of USD 100 bn; and the effect in bp per USD 100 bn.

Recorded mutation (leakage, #1273): in `s3c_net.NetSizeTable._value`, `instant = datetime.combine(self.dates[decision_row], self._time)`
was changed to `instant = datetime.combine(self.dates[target_row], self._time)` (the figure read at the target day's own instant, as the
`net_settlement` column of that row is). `ReadAtTheDecisionTests.test_an_auction_announced_after_the_decision_is_not_read` then failed
with `AssertionError` (`40.0 != 0.0`: the bill announced on the target day was counted); restored, it passes. Second mutation (the sign):
in `s3c_net.net_by_term`, `net - bills` was changed to `abs(net - bills)`; `NetByTermTests.test_the_sign_is_kept` then failed with
`AssertionError` (`30.0 != -30.0`).
"""

from __future__ import annotations

import dataclasses
import sys
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model import net_settlement as ns, s3c_net, spread_mr_calendar as cal, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.data import DailyObservation  # noqa: E402

NOON = time(12, 0)


def business_days(first, n):
    day, out = first, []
    while len(out) < n:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


DAYS = business_days(date(2026, 3, 2), 12)
PANEL = [DailyObservation(d, {"spread_bps": 0.0}) for d in DAYS]


def auction(settles, announced, *, bill, offering, maturing, cmb=False):
    return ns.Auction(settles, "Bill" if bill else "Note", bill, offering, maturing, 0.0, datetime.combine(announced, NOON), None, cmb)


class NetByTermTests(unittest.TestCase):

    def test_bill_and_coupon_nets_are_separate(self):
        target = DAYS[5]
        both = [
            auction(target, DAYS[2], bill=True, offering=100.0, maturing=60.0),
            auction(target, DAYS[2], bill=False, offering=50.0, maturing=80.0),
        ]
        out = s3c_net.net_by_term(both, datetime.combine(DAYS[4], time(16, 0)))
        self.assertAlmostEqual(out["settlement_bill"], 40.0)
        self.assertAlmostEqual(out["settlement_coupon"], -30.0)

    def test_the_sign_is_kept(self):
        target = DAYS[5]
        more_matures = [auction(target, DAYS[2], bill=False, offering=50.0, maturing=80.0)]
        out = s3c_net.net_by_term(more_matures, datetime.combine(DAYS[4], time(16, 0)))
        self.assertAlmostEqual(out["settlement_coupon"], -30.0)
        self.assertEqual(out["settlement_bill"], 0.0)

    def test_a_day_without_auctions_is_zero(self):
        self.assertEqual(s3c_net.net_by_term([], datetime(2026, 3, 3, 16)), {"settlement_bill": 0.0, "settlement_coupon": 0.0})


class ReadAtTheDecisionTests(unittest.TestCase):

    def setUp(self):
        self.target = DAYS[5]
        self.decision_row = 4  # the day before the target
        self.early = auction(self.target, DAYS[1], bill=False, offering=50.0, maturing=20.0)
        # A bill announced on the target day itself, 12:00: public by the target's own 12:00 instant, not by the 16:00 decision of the day before.
        self.late_bill = auction(self.target, self.target, bill=True, offering=100.0, maturing=60.0)

    def test_an_auction_announced_after_the_decision_is_not_read(self):
        table = s3c_net.NetSizeTable(PANEL, [self.early, self.late_bill])
        read = table.sizes_at(1, 5)
        self.assertEqual(read["settlement_bill"], 0.0)
        self.assertAlmostEqual(read["settlement_coupon"], 30.0)

    def test_the_same_auction_is_read_once_announced(self):
        table = s3c_net.NetSizeTable(PANEL, [self.early, self.late_bill])
        # a decision on the target day's own row (lead 0 is never read; this is the row after, for a later target) -> check the helper directly
        value = table._value(5, 5)
        self.assertAlmostEqual(value["settlement_bill"], 40.0)

    def test_a_cash_management_bill_announced_later_does_not_make_the_class_partly_announced(self):
        scheduled = auction(self.target, DAYS[1], bill=True, offering=100.0, maturing=60.0)
        cmb = auction(self.target, self.target, bill=True, offering=30.0, maturing=60.0, cmb=True)
        table = s3c_net.NetSizeTable(PANEL, [scheduled, cmb])
        self.assertAlmostEqual(table.sizes_at(1, 5)["settlement_bill"], 40.0)

    def test_a_training_pair_and_a_forecast_read_the_same_figure(self):
        table = s3c_net.NetSizeTable(PANEL, [self.early, self.late_bill])
        self.assertEqual(table.sizes_at(1, 5), table.read(1, 4))

    def test_the_figure_is_the_declared_column_of_the_day_before_when_all_was_announced_by_then(self):
        declaration = {"announcement_time": "12:00"}
        auctions = [auction(self.target, DAYS[1], bill=True, offering=100.0, maturing=60.0), self.early]
        rows = ns.with_net_settlement(PANEL, auctions, declaration)
        table = s3c_net.NetSizeTable(PANEL, auctions)
        # The column of the target row is read at the target's 12:00; here every auction was announced earlier, so both readings agree.
        column = rows[5].values
        read = table.sizes_at(1, 5)
        self.assertAlmostEqual(read["settlement_bill"], column["net_settlement_bills"])
        self.assertAlmostEqual(read["settlement_bill"] + read["settlement_coupon"], column["net_settlement"])


class LeadTests(unittest.TestCase):

    def test_only_lead_one_is_readable(self):
        table = s3c_net.NetSizeTable(PANEL, [auction(DAYS[6], DAYS[0], bill=True, offering=10.0, maturing=0.0)])
        self.assertEqual(set(table.sizes_at(1, 5)), set(sc.SIZED_TERMS))
        for lead in (2, 3, 4, 5):
            self.assertEqual(table.sizes_at(lead, 5 + lead - 1), {})
            self.assertEqual(table.read(lead, 0), {})

    def test_a_row_before_the_panel_is_refused(self):
        table = s3c_net.NetSizeTable(PANEL, [])
        with self.assertRaises(ValueError):
            table.sizes_at(1, 0)


class ArmTests(unittest.TestCase):

    def test_the_arm_is_s3_with_the_sized_terms_and_nothing_else(self):
        s3 = sc.ARMS[2]
        changed = dataclasses.replace(s3, name=s3c_net.NET_ARM.name, role=s3c_net.NET_ARM.role, sized=True)
        self.assertEqual(s3c_net.NET_ARM, changed)
        self.assertEqual(s3c_net.GROSS_ARM, dataclasses.replace(s3, name=s3c_net.GROSS_ARM.name, role=s3c_net.GROSS_ARM.role, sized=True))
        self.assertTrue(s3c_net.NET_ARM.robust and not s3c_net.NET_ARM.interact)
        self.assertEqual(sc.ridge_of(s3c_net.NET_ARM), sc.ridge_of(s3))
        self.assertEqual(s3c_net.NET_ARM.location, cal.NO_FOMC_IORB)

    def test_the_constant_state_makes_the_regressor_the_signed_size_in_hundreds_of_billions(self):
        states = s3c_net.constant_states(PANEL)
        self.assertEqual(set(states), set(DAYS))
        level = sc.level(states[DAYS[0]])
        self.assertEqual(level, 1.0)
        self.assertAlmostEqual(sc.regressor("settlement_bill", {}, {"settlement_bill": -50.0}, level, True), -0.5)
        self.assertAlmostEqual(sc.regressor("settlement_coupon", {}, {"settlement_coupon": 150.0}, level, True), 1.5)

    def test_effect_in_bp_per_100_bn_is_the_standardised_effect_times_the_scale(self):
        estimate = sc.StateEstimate(("settlement_bill",), {"settlement_bill": 0.02}, {}, {}, [0.0], 1, 0, 1, True)
        out = s3c_net.bp_per_100bn(estimate, 5.0)
        self.assertEqual(set(out), {"settlement_bill"})
        self.assertAlmostEqual(out["settlement_bill"], 0.1)


if __name__ == "__main__":
    unittest.main()
