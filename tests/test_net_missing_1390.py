"""The net settlement reader's explicit missing state, and the two ways of reading the missing days (#1390; H5, registration design: data meaning).

`repo_model.net_settlement.net_state` says, per class (bill types, coupon types) of one settlement day read at an instant, whether the class net rests
on a missing figure: `missing_maturing` (fully announced, no maturing estimate on any announced record: `net_for_day` reads the maturing amount as 0.0),
`incomplete` (partly announced: left out, reads 0.0, #679), `unannounced` (on the published schedule, none announced yet: reads 0.0). `absent` is a
class with no auction that day and `complete` a class with a maturing estimate: both are genuine readings, a zero among them a genuine zero.
`net_for_day` is unchanged by the state (the published declaration and every existing figure stay as they are; the tests below pin the equality).

`repo_model.s3c_net_missing` serves the two readings declared in `metadata/s3c_net_missing_1390.json`: `as_now` (the existing net, `AnnouncedNetSizeTable`)
and `drop` (a class that rests on a missing state contributes 0 to the net term, and a 0/1 missingness flag `net_missing` enters beside the two net
terms). The flag and the dropped net are scheduled fields read at the decision instant, on direct pairs.

Recorded mutation (availability, #1390): in `s3c_net_missing.NetMissingTerms.at`, `self._state(row - lead, row)` was changed to
`self._state(row, row)` (the missingness read at the target day's own 18:00 instant, when later announcements have filled the class).
`NetMissingTermsTests.test_the_flag_a_forecast_reads_is_the_one_announced_at_its_decision` then raised `LookAheadError` (the guard in `read` refused the
flag, an ERROR rather than a failure), and `NetMissingTermsTests.test_a_figure_read_at_the_target_day_is_refused` failed with
`AssertionError: {'net_missing': 0.0} != {'net_missing': 1.0}`; restored, all pass.

Second recorded mutation (state classification, #1390): in `net_settlement.net_state`, `elif len(members) < len(scheduled):` was changed to
`elif False:` (a partly announced class reads as complete). `StateTests.test_a_partly_announced_class_is_incomplete` failed with
`AssertionError: 'complete' != 'incomplete'`, `StateTests.test_net_for_day_is_unchanged` with `AssertionError: Tuples differ: (15.0, 0.0, 0) != (0.0, 0.0, 0)`
and the two flag tests with `AssertionError: {'net_missing': 0.0} != {'net_missing': 1.0}`; restored, all pass.

`StateTests.test_net_for_day_is_unchanged` pins hand values that the function on origin/main (before this change) also returns.
"""

from __future__ import annotations

import sys
import unittest
from datetime import date, datetime, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model import net_settlement as ns, s3c_announced, s3c_net_missing as nm  # noqa: E402
from repo_model import spread_mr_state_calendar as sc  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

import test_s3c_announced as base  # noqa: E402

DAYS = base.DAYS
NOON = time(12, 0)
TARGET = DAYS[9]


def auction(announced, *, bill, offering=40.0, maturing=25.0, cmb=False, target=TARGET):
    return ns.Auction(target, "Bill" if bill else "Note", bill, offering, maturing, 0.0, datetime.combine(announced, NOON), None, cmb)


def at(day, hour=18):
    return datetime.combine(day, time(hour, 0))


class StateTests(unittest.TestCase):
    def state(self, auctions, instant=None):
        return ns.net_state(auctions, instant or at(DAYS[8]))

    def test_a_class_with_a_maturing_estimate_is_complete(self):
        s = self.state([auction(DAYS[2], bill=False)])
        self.assertEqual(s.coupon.state, ns.COMPLETE)
        self.assertEqual(s.coupon.net, 15.0)
        self.assertFalse(s.missing)

    def test_a_class_with_no_auction_is_absent_and_not_missing(self):
        s = self.state([auction(DAYS[2], bill=False)])
        self.assertEqual(s.bill.state, ns.ABSENT)
        self.assertEqual(s.bill.net, 0.0)

    def test_a_fully_announced_class_with_no_maturing_figure_is_missing_maturing(self):
        s = self.state([auction(DAYS[2], bill=True, maturing=None, cmb=True)])
        self.assertEqual(s.bill.state, ns.MISSING_MATURING)
        self.assertEqual(s.bill.net, 40.0)  # the existing reading: maturing taken as 0.0
        self.assertTrue(s.missing)

    def test_a_partly_announced_class_is_incomplete(self):
        s = self.state([auction(DAYS[2], bill=False), auction(DAYS[9], bill=False)], at(DAYS[8]))
        self.assertEqual(s.coupon.state, ns.INCOMPLETE)
        self.assertEqual(s.coupon.net, 0.0)

    def test_a_scheduled_class_with_nothing_announced_is_unannounced(self):
        s = self.state([auction(DAYS[9], bill=False)], at(DAYS[8]))
        self.assertEqual(s.coupon.state, ns.UNANNOUNCED)
        self.assertEqual(s.coupon.net, 0.0)

    def test_a_cmb_announced_later_is_not_on_the_schedule_and_is_absent(self):
        s = self.state([auction(DAYS[9], bill=True, maturing=None, cmb=True)], at(DAYS[8]))
        self.assertEqual(s.bill.state, ns.ABSENT)

    def test_a_cmb_announced_later_does_not_make_a_regular_class_incomplete(self):
        s = self.state([auction(DAYS[2], bill=True), auction(DAYS[9], bill=True, maturing=None, cmb=True)], at(DAYS[8]))
        self.assertEqual(s.bill.state, ns.COMPLETE)

    def test_a_genuine_zero_is_complete_not_missing(self):
        s = self.state([auction(DAYS[2], bill=False, offering=25.0, maturing=25.0)])
        self.assertEqual(s.coupon.state, ns.COMPLETE)
        self.assertEqual(s.coupon.net, 0.0)
        self.assertFalse(s.missing)

    def test_net_for_day_is_unchanged(self):
        """Hand values of the reading before #1390: a partly announced class 0.0, a missing maturing amount 0.0, the rest offering less maturing."""

        cases = [
            ([auction(DAYS[2], bill=False), auction(DAYS[9], bill=False)], at(DAYS[8]), (0.0, 0.0, 0)),
            ([auction(DAYS[2], bill=False), auction(DAYS[9], bill=False)], at(DAYS[9]), (55.0, 0.0, 0)),
            ([auction(DAYS[2], bill=True, maturing=None, cmb=True), auction(DAYS[3], bill=False)], at(DAYS[8]), (55.0, 40.0, 1)),
            ([auction(DAYS[2], bill=True), auction(DAYS[9], bill=True, maturing=None, cmb=True), auction(DAYS[2], bill=False, maturing=None)],
             at(DAYS[8]), (55.0, 15.0, 1)),
            ([], at(DAYS[8]), (0.0, 0.0, 0)),
        ]
        for auctions, moment, expected in cases:
            self.assertEqual(ns.net_for_day(auctions, moment), expected)
            s = ns.net_state(auctions, moment)
            self.assertEqual((s.net(), s.bill.net, s.unknown), expected)

    def test_the_dropped_reading_sets_a_missing_class_to_zero(self):
        s = self.state([auction(DAYS[2], bill=True, maturing=None, cmb=True), auction(DAYS[2], bill=False)])
        self.assertEqual(s.terms(drop=False), {"settlement_bill": 40.0, "settlement_coupon": 15.0})
        self.assertEqual(s.terms(drop=True), {"settlement_bill": 0.0, "settlement_coupon": 15.0})

    def test_the_cmb_pending_count_is_hindsight_and_counts_only_later_announcements(self):
        auctions = [auction(DAYS[9], bill=True, maturing=None, cmb=True), auction(DAYS[2], bill=True, maturing=None, cmb=True)]
        self.assertEqual(ns.cmb_pending(auctions, at(DAYS[8])), 1)
        self.assertEqual(ns.cmb_pending(auctions, at(DAYS[9])), 0)


class NetMissingTermsTests(unittest.TestCase):
    def tables(self, auctions):
        rows = base.panel()
        return (s3c_announced.AnnouncedNetSizeTable(rows, auctions), nm.DroppedNetSizeTable(rows, auctions), nm.NetMissingTerms(rows, auctions))

    def test_the_flag_is_one_where_a_class_rests_on_a_missing_state(self):
        _a, _d, flag = self.tables([auction(DAYS[2], bill=True, maturing=None, cmb=True)])
        self.assertEqual(flag.at(1, 9), {sc.MISSING_FLAG: 1.0})

    def test_the_flag_is_zero_for_a_complete_class_and_for_a_day_without_settlement(self):
        _a, _d, flag = self.tables([auction(DAYS[2], bill=False)])
        self.assertEqual(flag.at(1, 9), {sc.MISSING_FLAG: 0.0})
        self.assertEqual(flag.at(1, 10), {sc.MISSING_FLAG: 0.0})

    def test_the_as_now_table_is_the_published_net_and_the_dropped_table_differs_only_on_missing_classes(self):
        auctions = [auction(DAYS[2], bill=True, maturing=None, cmb=True), auction(DAYS[2], bill=False)]
        as_now, dropped, _flag = self.tables(auctions)
        self.assertEqual(as_now.sizes_at(1, 9), {"settlement_bill": 40.0, "settlement_coupon": 15.0})
        self.assertEqual(dropped.sizes_at(1, 9), {"settlement_bill": 0.0, "settlement_coupon": 15.0})

    def test_a_dropped_figure_that_is_not_the_one_announced_is_refused(self):
        _a, dropped, _f = self.tables([auction(DAYS[2], bill=True, maturing=None, cmb=True)])
        dropped._cache[(6, 9)] = {"settlement_bill": 40.0, "settlement_coupon": 0.0}
        with self.assertRaises(LookAheadError):
            dropped.read(3, 6)

    def test_a_training_pair_and_a_forecast_read_the_same_figure(self):
        auctions = [auction(DAYS[5], bill=True, maturing=None, cmb=True), auction(DAYS[2], bill=False), auction(DAYS[7], bill=False)]
        _a, dropped, flag = self.tables(auctions)
        for lead in (1, 2, 3, 4, 5):
            self.assertEqual(flag.at(lead, 9), flag.read(lead, 9 - lead))
            self.assertEqual(dropped.sizes_at(lead, 9), dropped.read(lead, 9 - lead))

    def test_a_figure_read_at_the_target_day_is_refused(self):
        # the coupon class of day 9 is announced in part at lead 3 (day 6) and in full by day 8: the flag is 1 at lead 3, 0 at lead 1
        auctions = [auction(DAYS[2], bill=False), auction(DAYS[7], bill=False)]
        _a, _d, flag = self.tables(auctions)
        self.assertEqual(flag.at(3, 9), {sc.MISSING_FLAG: 1.0})
        self.assertEqual(flag.at(1, 9), {sc.MISSING_FLAG: 0.0})
        flag._cache[(3, 9)] = {sc.MISSING_FLAG: 0.0}
        with self.assertRaises(LookAheadError):
            flag.read(3, 6)

    def test_the_flag_a_forecast_reads_is_the_one_announced_at_its_decision(self):
        auctions = [auction(DAYS[2], bill=False), auction(DAYS[7], bill=False)]
        _a, _d, flag = self.tables(auctions)
        self.assertEqual(flag.read(3, 6), {sc.MISSING_FLAG: 1.0})  # a flag built at a later instant raises LookAheadError here

    def test_the_log_row_names_the_state_of_each_class_at_the_decision(self):
        auctions = [auction(DAYS[2], bill=True, maturing=None, cmb=True), auction(DAYS[8], bill=False)]
        _a, _d, flag = self.tables(auctions)
        row = flag.log_row(2, 7)
        self.assertEqual(row["lead"], 2)
        self.assertEqual(row["decision_day"], DAYS[7].isoformat())
        self.assertEqual(row["target_day"], DAYS[9].isoformat())
        self.assertEqual(row["bill"], ns.MISSING_MATURING)
        self.assertEqual(row["coupon"], ns.UNANNOUNCED)
        self.assertEqual(row["missing"], 1)

    def test_the_arm_is_the_announced_net_arm_with_the_one_extra_term(self):
        self.assertEqual(nm.DROP_ARM.extra, (sc.MISSING_FLAG,))
        self.assertTrue(nm.DROP_ARM.sized)
        self.assertEqual(nm.DROP_ARM.location, s3c_announced.ANN_NET_ARM.location)
        self.assertIn(sc.MISSING_FLAG, sc.EXTRA_TERMS)


class PublishedPathsUnchangedTests(unittest.TestCase):
    def test_no_published_declaration_reads_the_missing_state(self):
        text = (ROOT / "metadata" / "net_settlement.json").read_text(encoding="utf-8")
        self.assertNotIn("net_missing", text)
        self.assertNotIn("net_missing", " ".join(ns.COLUMNS))


if __name__ == "__main__":
    unittest.main()
