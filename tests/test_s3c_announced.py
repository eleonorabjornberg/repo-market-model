"""(s3c-ann) and (s3c-ann-net): the settlement terms of (s3c) read at leads 2 to 5 from the auction announcement (#1288; H5 step 3, ledger item 71
on #1116).

`repo_model.s3c_announced` supplies two new read paths. `AnnouncedTermTable` gives the two settlement flags at every lead: at lead `h` the flag
of target day `T` is 1 when the coupon (bill) auctions settling on `T` that had been announced by the 16:00 decision of `T - h` offer more than
zero (`metadata/settlement_announcement_dating.json`, read with `repo_model.settlement_dating`). `AnnouncedNetSizeTable` gives #1273's net
settlement at every lead on the same terms. Neither is read by a published record: the published declaration still refuses a settlement column
beyond lead 1, and so does (s3c)'s own table.

What these tests pin: that the flag at a lead is the announced offering at the decision instant (an auction announced after the decision is not
counted; one announced on the decision day at 12:00 is); that lead 1 is the panel's flag as (s3c) reads it; that a leg alone can be admitted; that
a training figure and a forecast figure are the same function of the same announcements; that `read` refuses, with `LookAheadError`, a figure that
counts an auction announced after the decision, and, with `StaleReadError`, one that leaves an announced auction out; that the net at a lead is the
net announced at the decision (a class announced in part reads 0); that the arms are (s3) and (s3-net) with nothing else changed; that a term
enters the fit at a lead it could not before; that a one-step fit of the settlement columns still raises `ValueError`; and that the published
`asof` rule, the live record's feature list and (s3c)'s own table still refuse a settlement beyond lead 1.

Recorded mutation (leakage, #1288): in `s3c_announced.AnnouncedTermTable._counted`, `instant = datetime.combine(self.dates[row - lead], self._time)`
was changed to `instant = datetime.combine(self.dates[row], self._time)` (the figure read at the target day's own instant, when everything
announced by the target day is counted). `ReadAtTheDecisionTests.test_an_auction_announced_after_the_decision_is_not_read` then failed with
`LookAheadError` (the read of the lead-3 forecast counted an auction announced after its decision; the guard in `read` refused it); restored, it
passes. Second mutation (the net's decision row): in `s3c_announced.AnnouncedNetSizeTable.sizes_at`, `self._value(row - lead, row)` was changed to
`self._value(row, row)`; `AnnouncedNetTests.test_an_auction_announced_after_the_decision_is_not_read` then failed with `LookAheadError` (the figure
read differed from the net announced at the decision).
"""

from __future__ import annotations

import dataclasses
import importlib.util
import json
import sys
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model import net_settlement as ns, s3c_announced, s3c_net, settlement_dating as sd  # noqa: E402
from repo_model import spread_mr_calendar as cal, spread_mr_state_calendar as sc  # noqa: E402
from repo_model.asof import InformationRule, StaleReadError  # noqa: E402
from repo_model.data import DailyObservation  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

NOON = time(12, 0)
ANNOUNCEMENT = ROOT / "metadata" / "settlement_announcement_dating.json"
REGISTRY = json.loads((ROOT / "metadata" / "sources.json").read_text(encoding="utf-8"))
DECLARATION = sd.load_result_dating(ANNOUNCEMENT)
LEADS = (1, 2, 3, 4, 5)


def business_days(first, n):
    day, out = first, []
    while len(out) < n:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


DAYS = business_days(date(2026, 3, 2), 16)


def panel(coupon_on=(), bill_on=()):
    return [
        DailyObservation(d, {
            "treasury_settlement_coupons": 40.0 if d in coupon_on else 0.0,
            "treasury_settlement_bills": 60.0 if d in bill_on else 0.0,
            "iorb_announced_change_bps": None,
        })
        for d in DAYS
    ]


def record(announced, settles, *, kind="Note", amount="40000000000"):
    return {
        "announcemt_date": announced.isoformat(), "auction_date": announced.isoformat(), "issue_date": settles.isoformat(),
        "security_type": kind, "offering_amt": amount, "total_accepted": "null", "closing_time_comp": "01:00 PM",
    }


def results(*records):
    return sd.auction_results(list(records), DECLARATION)


def table(rows, found, **kw):
    return s3c_announced.AnnouncedTermTable(rows, [], found, calendar=[], **kw)


class AnnouncedFlagTests(unittest.TestCase):

    def setUp(self):
        self.target = DAYS[9]
        # A coupon announced on DAYS[5] (12:00) settling on DAYS[9]; a bill announced on DAYS[8] settling the same day.
        self.found = results(record(DAYS[5], self.target), record(DAYS[8], self.target, kind="Bill", amount="60000000000"))
        self.table = table(panel(coupon_on={self.target}, bill_on={self.target}), self.found)

    def flags(self, lead):
        return self.table.flags_at(lead, 9)

    def test_the_coupon_flag_is_one_from_the_decision_after_the_announcement(self):
        # The decision of lead h is on DAYS[9 - h]; the coupon was announced on DAYS[5] at 12:00, so it is public from the 16:00 decision of DAYS[5].
        self.assertEqual({h: self.flags(h)["settlement_coupon"] for h in LEADS}, {1: 1, 2: 1, 3: 1, 4: 1, 5: 0})

    def test_the_bill_flag_waits_for_its_own_announcement(self):
        self.assertEqual({h: self.flags(h)["settlement_bill"] for h in LEADS}, {1: 1, 2: 0, 3: 0, 4: 0, 5: 0})

    def test_the_flags_are_there_at_every_lead_with_the_other_terms(self):
        for lead in LEADS:
            names = set(self.flags(lead))
            self.assertTrue({"settlement_coupon", "settlement_bill"} <= names, lead)
            self.assertTrue({"month_end", "quarter_end", "tax_date", "dom_19_23"} <= names, lead)

    def test_lead_1_is_the_panels_flag_as_s3c_reads_it(self):
        stock = cal.TermTable(panel(coupon_on={self.target}, bill_on={self.target}), [], [])
        self.assertEqual(self.table.flags_at(1, 9), stock.flags_at(1, 9))
        for row in range(len(DAYS)):
            self.assertEqual(self.table.flags_at(1, row), stock.flags_at(1, row), row)

    def test_the_stock_table_has_no_settlement_flag_beyond_lead_1(self):
        stock = cal.TermTable(panel(coupon_on={self.target}), [], [])
        for lead in (2, 3, 4, 5):
            self.assertNotIn("settlement_coupon", stock.flags_at(lead, 9))
            self.assertNotIn("settlement_bill", stock.flags_at(lead, 9))

    def test_a_leg_alone_can_be_admitted(self):
        coupon = table(panel(coupon_on={self.target}), self.found, legs=("settlement_coupon",))
        self.assertEqual(coupon.flags_at(3, 9)["settlement_coupon"], 1)
        self.assertNotIn("settlement_bill", coupon.flags_at(3, 9))
        self.assertIn("settlement_bill", coupon.flags_at(1, 9))
        bill = table(panel(bill_on={self.target}), self.found, legs=("settlement_bill",))
        self.assertNotIn("settlement_coupon", bill.flags_at(3, 9))
        self.assertEqual(bill.flags_at(2, 9)["settlement_bill"], 0)
        self.assertEqual(bill.flags_at(1, 9)["settlement_bill"], 1)

    def test_an_unknown_leg_is_refused(self):
        with self.assertRaises(ValueError):
            table(panel(), self.found, legs=("month_end",))

    def test_a_row_without_a_decision_row_reads_zero(self):
        early = table(panel(coupon_on={DAYS[2]}), results(record(DAYS[0], DAYS[2])))
        self.assertEqual(early.flags_at(5, 2)["settlement_coupon"], 0)


class ReadAtTheDecisionTests(unittest.TestCase):
    """A forecast reads the flag as of its own decision, and refuses one that is not."""

    def setUp(self):
        self.target = DAYS[9]
        # Announced on DAYS[7], which is after the lead-3 decision (DAYS[6]) and before the lead-2 decision (DAYS[7], 16:00).
        self.late = results(record(DAYS[7], self.target))
        self.table = table(panel(coupon_on={self.target}), self.late)

    def test_an_auction_announced_after_the_decision_is_not_read(self):
        # Recorded mutation: see the module docstring (`AnnouncedTermTable._counted`).
        self.assertEqual(self.table.read(3, 6)["settlement_coupon"], 0)
        self.assertEqual(self.table.read(2, 7)["settlement_coupon"], 1)

    def test_the_announcement_on_the_decision_day_is_public_at_the_decision(self):
        self.assertEqual(self.table.read(2, 7)["settlement_coupon"], 1)
        self.assertEqual(self.table.read(1, 8)["settlement_coupon"], 1)

    def test_a_training_pair_and_a_forecast_read_the_same_figure(self):
        for lead in (2, 3, 4, 5):
            row = 9
            self.assertEqual(self.table.flags_at(lead, row)["settlement_coupon"], self.table.read(lead, row - lead)["settlement_coupon"])

    def test_the_forecast_reads_all_the_terms_the_stock_table_reads_at_lead_1(self):
        stock = cal.TermTable(panel(coupon_on={self.target}), [], [])
        self.assertEqual(self.table.read(1, 8), stock.read(1, 8))

    def test_a_figure_that_counts_an_auction_announced_after_the_decision_is_refused(self):
        # The built figure for (lead 3, row 9) is that of the decision on DAYS[6]; counting the auction announced on DAYS[7] there is look-ahead.
        late = self.late[0]
        self.table._counted_cache[(3, 9)] = {"settlement_coupon": (late,), "settlement_bill": ()}
        with self.assertRaises(LookAheadError):
            self.table.read(3, 6)

    def test_a_figure_that_leaves_out_an_announced_auction_is_refused(self):
        self.table._counted_cache[(2, 9)] = {"settlement_coupon": (), "settlement_bill": ()}
        with self.assertRaises(StaleReadError):
            self.table.read(2, 7)

    def test_a_scheduled_term_is_still_refused_when_a_stock_reader_asks_for_it(self):
        term = cal.TERM["settlement_coupon"]
        with self.assertRaises(LookAheadError):
            cal.require_public(term, [9], 7, DAYS)


class AnnouncedNetTests(unittest.TestCase):

    def setUp(self):
        self.target = DAYS[9]
        self.rows = panel()
        self.early = ns.Auction(self.target, "Note", False, 50.0, 20.0, 0.0, datetime.combine(DAYS[3], NOON), None)
        # A bill announced on DAYS[7]: public from the 16:00 decision of DAYS[7] (lead 2), not from that of DAYS[6] (lead 3).
        self.late_bill = ns.Auction(self.target, "Bill", True, 100.0, 60.0, 0.0, datetime.combine(DAYS[7], NOON), None)
        self.table = s3c_announced.AnnouncedNetSizeTable(self.rows, [self.early, self.late_bill])

    def test_an_auction_announced_after_the_decision_is_not_read(self):
        # Recorded mutation: see the module docstring (`AnnouncedNetSizeTable.sizes_at`).
        read = self.table.read(3, 6)
        self.assertEqual(read["settlement_bill"], 0.0)
        self.assertAlmostEqual(read["settlement_coupon"], 30.0)
        read = self.table.read(2, 7)
        self.assertAlmostEqual(read["settlement_bill"], 40.0)

    def test_the_figure_is_readable_at_every_lead_and_lead_1_is_the_lead_1_reader(self):
        stock = s3c_net.NetSizeTable(self.rows, [self.early, self.late_bill])
        for lead in LEADS:
            self.assertEqual(set(self.table.sizes_at(lead, 9)), set(sc.SIZED_TERMS), lead)
        self.assertEqual(self.table.sizes_at(1, 9), stock.sizes_at(1, 9))
        self.assertEqual(self.table.read(1, 8), stock.read(1, 8))
        for lead in (2, 3, 4, 5):
            self.assertEqual(stock.sizes_at(lead, 9), {})

    def test_a_class_announced_in_part_reads_zero_until_complete(self):
        first = ns.Auction(self.target, "Note", False, 50.0, 80.0, 0.0, datetime.combine(DAYS[3], NOON), None)
        second = ns.Auction(self.target, "Bond", False, 30.0, 80.0, 0.0, datetime.combine(DAYS[6], NOON), None)
        table_ = s3c_announced.AnnouncedNetSizeTable(self.rows, [first, second])
        self.assertEqual(table_.read(5, 4)["settlement_coupon"], 0.0)  # only the note announced by the decision of DAYS[4]
        self.assertAlmostEqual(table_.read(3, 6)["settlement_coupon"], 0.0)  # DAYS[6] 12:00: the bond is announced, 80 offered less 80 maturing
        self.assertAlmostEqual(table_.read(2, 7)["settlement_coupon"], 0.0)
        third = ns.Auction(self.target, "Bond", False, 70.0, 80.0, 0.0, datetime.combine(DAYS[6], NOON), None)
        table_ = s3c_announced.AnnouncedNetSizeTable(self.rows, [first, third])
        self.assertAlmostEqual(table_.read(3, 6)["settlement_coupon"], 40.0)

    def test_a_training_pair_and_a_forecast_read_the_same_figure(self):
        for lead in (2, 3, 4, 5):
            self.assertEqual(self.table.sizes_at(lead, 9), self.table.read(lead, 9 - lead))

    def test_a_figure_that_is_not_the_one_announced_at_the_decision_is_refused(self):
        other = dict(self.table._value(9, 9))
        self.table._cache[(6, 9)] = other  # the lead-3 decision's figure replaced by the target day's own
        with self.assertRaises(LookAheadError):
            self.table.read(3, 6)

    def test_a_row_before_the_panel_is_refused(self):
        with self.assertRaises(ValueError):
            self.table.sizes_at(3, 1)


class ArmTests(unittest.TestCase):

    def test_the_gross_arm_is_s3_with_a_new_name_and_nothing_else(self):
        s3 = sc.ARMS[2]
        self.assertEqual(s3c_announced.ANN_ARM, dataclasses.replace(s3, name=s3c_announced.ANN_ARM.name, role=s3c_announced.ANN_ARM.role))
        self.assertEqual(s3c_announced.ANN_ARM.name, "sc_s3_ann")
        self.assertFalse(s3c_announced.ANN_ARM.sized)

    def test_the_net_arm_is_the_net_arm_of_1273_with_a_new_name(self):
        net = s3c_net.NET_ARM
        self.assertEqual(s3c_announced.ANN_NET_ARM, dataclasses.replace(net, name=s3c_announced.ANN_NET_ARM.name, role=s3c_announced.ANN_NET_ARM.role))
        self.assertTrue(s3c_announced.ANN_NET_ARM.sized)
        self.assertEqual(sc.ridge_of(s3c_announced.ANN_NET_ARM), sc.ridge_of(sc.ARMS[2]))

    def test_the_leg_arms_are_the_gross_arm_under_their_own_names(self):
        self.assertEqual(
            {s3c_announced.COUPON_ARM.name, s3c_announced.BILL_ARM.name}, {"sc_s3_ann_coupon", "sc_s3_ann_bill"})
        for arm in (s3c_announced.COUPON_ARM, s3c_announced.BILL_ARM):
            self.assertEqual(dataclasses.replace(arm, name=sc.ARMS[2].name, role=sc.ARMS[2].role), sc.ARMS[2])


class FitTests(unittest.TestCase):
    """A settlement term enters the fit at a lead the stock table did not read it at, and the fit is on direct pairs."""

    def setUp(self):
        self.target_days = {DAYS[i] for i in (6, 9, 12, 14)}
        self.rows = panel(coupon_on=self.target_days)
        self.found = results(*[record(DAYS[i - 5], DAYS[i]) for i in (6, 9, 12, 14) if i - 5 >= 0])
        self.table = table(self.rows, self.found)

    def pairs(self, lead):
        out = []
        for target in range(5, 15):
            flags = self.table.flags_at(lead, target)
            out.append(sc.StatePair(5.0 if flags["settlement_coupon"] else 0.0, 1.0, flags, None))
        return out

    def test_the_term_enters_at_lead_3_and_carries_its_effect(self):
        estimate = sc.fit_state_terms(
            self.pairs(3), regressors=("treasury_settlement_coupons",), terms=cal.NO_FOMC_IORB, interact=False, robust=False,
            training_pairs="direct", min_flagged=3)
        self.assertIn("settlement_coupon", estimate.terms)
        self.assertGreater(estimate.effect["settlement_coupon"], 1.0)

    def test_the_term_does_not_enter_at_lead_3_in_the_stock_table(self):
        stock = cal.TermTable(self.rows, [], [])
        pairs = [sc.StatePair(0.0, 1.0, stock.flags_at(3, t), None) for t in range(5, 15)]
        estimate = sc.fit_state_terms(
            pairs, regressors=(), terms=cal.NO_FOMC_IORB, interact=False, robust=False, training_pairs="direct", min_flagged=3)
        self.assertNotIn("settlement_coupon", estimate.terms)

    def test_a_one_step_fit_of_the_settlement_columns_still_raises(self):
        with self.assertRaises(ValueError):
            sc.fit_state_terms(
                self.pairs(3), regressors=("treasury_settlement_coupons",), terms=cal.NO_FOMC_IORB, interact=False, robust=False,
                training_pairs="one_step")

    def test_the_study_walks_on_direct_pairs(self):
        import inspect

        self.assertEqual(inspect.signature(sc.walk).parameters["training_pairs"].default, "direct")
        self.assertEqual(s3c_announced.TRAINING_PAIRS, "direct")


class PublishedPathsStillRefuseTests(unittest.TestCase):
    """The announcement dating is off in every published declaration: a settlement column beyond lead 1 is refused there (#541 is a measurement)."""

    def test_the_published_asof_rule_refuses_a_settlement_beyond_lead_1(self):
        dates = business_days(date(2026, 1, 5), 15)
        for column in ("treasury_settlement_coupons", "treasury_settlement_bills", "treasury_settlement"):
            rule = InformationRule(REGISTRY, ["spread_bps", column], decision_time=time(16, 0), horizon=1)
            rule.check(dates, rule.information_set(dates, 10))
            for horizon in (2, 3, 4, 5):
                rule = InformationRule(REGISTRY, ["spread_bps", column], decision_time=time(16, 0), horizon=horizon)
                with self.subTest(column=column, horizon=horizon), self.assertRaises(LookAheadError):
                    rule.check(dates, rule.information_set(dates, 10))

    def test_the_published_declaration_is_the_frozen_one(self):
        block = REGISTRY["treasury_auctions"]["scheduled_availability"]
        self.assertEqual(block["days"], 1)
        self.assertIn("treasury_settlement_coupon", block["fields"])
        self.assertIn("treasury_settlement_bill", block["fields"])
        self.assertIn("off", json.loads(ANNOUNCEMENT.read_text(encoding="utf-8"))["status"])

    def test_the_live_record_drops_the_settlement_beyond_lead_1(self):
        spec = importlib.util.spec_from_file_location("live_record_for_1288", ROOT / "scripts" / "live_record.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules["live_record_for_1288"] = module
        spec.loader.exec_module(module)
        self.assertIn("treasury_settlement", module.published_features(1))
        for horizon in (2, 3, 4, 5):
            self.assertFalse([n for n in module.published_features(horizon) if n.startswith("treasury_settlement")], horizon)

    def test_s3c_own_table_still_reads_a_settlement_at_lead_1_only(self):
        for name in ("settlement_coupon", "settlement_bill"):
            term = cal.TERM[name]
            self.assertEqual(cal.readable_offsets(term, 1), (0,))
            for lead in (2, 3, 4, 5):
                self.assertEqual(cal.readable_offsets(term, lead), ())
        stock = cal.TermTable(panel(coupon_on={DAYS[9]}), [], [])
        for lead in (2, 3, 4, 5):
            self.assertNotIn("settlement_coupon", stock.read(lead, 3))
        # The net reader of #1273 is still lead 1 only.
        net = s3c_net.NetSizeTable(panel(), [])
        self.assertEqual(net.sizes_at(2, 5), {})


if __name__ == "__main__":
    unittest.main()
