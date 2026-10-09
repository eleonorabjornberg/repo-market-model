"""Net Treasury cash settlement, read as announced (#426, track N of #374).

`repo_model.net_settlement` builds, per panel day, the cash a settlement day drains:
the announced public offering minus the announced publicly held maturing amount,
from Fiscal Data auction records, each read as of the announcement.

Recorded mutations (CLAUDE.md), 8 October 2026, each applied in a disposable copy:

* `src/repo_model/net_settlement.py`, `known_auctions`, the condition
  `auction.announced_at <= instant` mutated to `True` (an auction announced after the
  decision instant becomes visible). Killed by
  `AnnouncementTests.test_an_auction_announced_after_the_instant_is_invisible`
  (`AssertionError: 10.0 != 0.0`), `AnnouncementTests.test_the_window_reaches_past_the_last_panel_row`
  (`AssertionError`) and `GuardTests.test_a_column_counting_an_unannounced_auction_is_refused`
  (`AssertionError: LookAheadError not raised`).
* `src/repo_model/net_settlement.py`, `check_known_columns`, the `any(...)` test that raises
  `LookAheadError` deleted, so a column counting an unannounced auction falls to the
  stale branch. `GuardTests.test_a_column_counting_an_unannounced_auction_is_refused`
  then fails with `StaleReadError` (the wrong type, an error rather than a pass).
* `src/repo_model/net_settlement.py`, `check_known_columns`, `raise StaleReadError(` preceded by
  `continue`. `GuardTests.test_a_column_leaving_out_an_announced_auction_is_refused`
  then fails with `AssertionError: StaleReadError not raised`.
"""

from __future__ import annotations

import json
import unittest
from datetime import date, datetime
from pathlib import Path

from repo_model import net_settlement as ns
from repo_model.asof import StaleReadError
from repo_model.data import DailyObservation
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
DECLARATION = ns.load_declaration(ROOT / "metadata" / "net_settlement.json")
SNAPSHOT = ROOT / "tests" / "fixtures" / "snapshots" / "net_settlement_inputs" / "treasury_auctions"


def record(
    kind="Bill",
    offering=50e9,
    maturing="40000000000",
    announced="2026-01-05",
    auctioned="2026-01-07",
    settles="2026-01-09",
    accepted="51000000000",
    soma="1000000000",
    term="4-Week",
    cmb="No",
):
    return {
        "security_type": kind,
        "security_term": term,
        "offering_amt": str(int(offering)),
        "est_pub_held_mat_by_type_amt": maturing,
        "announcemt_date": announced,
        "auction_date": auctioned,
        "issue_date": settles,
        "total_accepted": accepted,
        "soma_accepted": soma,
        "cash_management_bill_cmb": cmb,
        "closing_time_comp": "11:30 AM",
    }


def rows(*days):
    return [DailyObservation(date.fromisoformat(day), {}) for day in days]


# Mon 2026-01-05 .. Fri 2026-01-16 (2026-01-09 is a Friday, settlement day).
DAYS = (
    "2026-01-05", "2026-01-06", "2026-01-07", "2026-01-08", "2026-01-09",
    "2026-01-12", "2026-01-13", "2026-01-14", "2026-01-15", "2026-01-16",
)


class DeclarationTests(unittest.TestCase):
    def test_the_declaration_loads_and_names_the_columns(self):
        self.assertEqual(ns.COLUMNS, tuple(DECLARATION["columns"]))
        self.assertEqual(DECLARATION["scoring"]["last_day"], "2025-12-31")

    def test_a_declaration_missing_a_key_is_refused(self):
        broken = dict(DECLARATION)
        del broken["announcement_time"]
        path = Path(self.id() + ".json")
        path.write_text(json.dumps(broken))
        self.addCleanup(path.unlink)
        with self.assertRaises(ValueError):
            ns.load_declaration(path)


class RecordTests(unittest.TestCase):
    def test_amounts_are_in_billions_and_a_null_maturing_figure_is_none(self):
        (a,) = ns.auction_records([record(maturing="null")], DECLARATION)
        self.assertEqual(a.offering, 50.0)
        self.assertIsNone(a.maturing)
        self.assertEqual(a.soma, 1.0)
        self.assertEqual(a.kind, "Bill")
        self.assertEqual(a.announced_at, datetime(2026, 1, 5, 12, 0))
        self.assertEqual(a.result_at, datetime(2026, 1, 7, 15, 0))

    def test_an_auction_not_yet_held_has_no_result_instant_and_no_soma(self):
        (a,) = ns.auction_records([record(accepted="null", soma="null")], DECLARATION)
        self.assertIsNone(a.result_at)
        self.assertIsNone(a.soma)

    def test_an_auction_announced_after_it_was_held_is_refused(self):
        with self.assertRaises(ValueError):
            ns.auction_records([record(announced="2026-01-08")], DECLARATION)

    def test_an_auction_announced_after_it_settles_is_refused(self):
        with self.assertRaises(ValueError):
            ns.auction_records([record(announced="2026-01-12", auctioned="2026-01-12")], DECLARATION)

    def test_a_record_missing_a_field_is_refused(self):
        bad = record()
        del bad["offering_amt"]
        with self.assertRaises(ValueError):
            ns.auction_records([bad], DECLARATION)


class AnnouncementTests(unittest.TestCase):
    """A day's net is the announced offering less the announced maturing amount, per security type."""

    def columns(self, records, day="2026-01-09", panel=DAYS):
        auctions = ns.auction_records(records, DECLARATION)
        built = ns.with_net_settlement(rows(*panel), auctions, DECLARATION)
        return {r.date.isoformat(): r.values for r in built}[day]

    def test_net_is_offering_minus_maturing_once_per_type(self):
        # two bills of one issue date share one maturing figure (40) and are counted once.
        records = [record(offering=50e9), record(offering=40e9, term="8-Week")]
        values = self.columns(records, day="2026-01-09")
        self.assertAlmostEqual(values["net_settlement"], 50.0 + 40.0 - 40.0)
        self.assertAlmostEqual(values["net_settlement_bills"], 50.0)

    def test_coupons_and_bills_have_their_own_maturing_figure(self):
        records = [
            record(offering=50e9, maturing="40000000000"),
            record(kind="Note", offering=60e9, maturing="25000000000", term="2-Year"),
        ]
        values = self.columns(records)
        self.assertAlmostEqual(values["net_settlement"], (50 - 40) + (60 - 25))
        self.assertAlmostEqual(values["net_settlement_bills"], 50 - 40)

    def test_a_group_with_no_maturing_figure_reads_zero_maturing(self):
        values = self.columns([record(offering=30e9, maturing="null", kind="CMB", cmb="Yes")])
        self.assertAlmostEqual(values["net_settlement"], 30.0)

    def test_an_auction_announced_after_the_instant_is_invisible(self):
        # announced Wednesday 2026-01-07: absent from the Tuesday 2026-01-06 row, present on the Wednesday row.
        records = [record(announced="2026-01-07", auctioned="2026-01-07")]
        auctions = ns.auction_records(records, DECLARATION)
        built = {r.date.isoformat(): r.values for r in ns.with_net_settlement(rows(*DAYS), auctions, DECLARATION)}
        self.assertEqual(built["2026-01-06"]["net_settlement_due_5d"], 0.0)
        self.assertAlmostEqual(built["2026-01-07"]["net_settlement_due_5d"], 10.0)

    def test_the_maturing_figure_of_a_later_announced_auction_is_not_read_early(self):
        # the first auction carries no figure; the second, announced two days later, carries 40.
        records = [
            record(offering=50e9, maturing="null", announced="2026-01-05"),
            record(offering=40e9, maturing="40000000000", announced="2026-01-07", term="8-Week"),
        ]
        auctions = ns.auction_records(records, DECLARATION)
        built = {r.date.isoformat(): r.values for r in ns.with_net_settlement(rows(*DAYS), auctions, DECLARATION)}
        self.assertAlmostEqual(built["2026-01-06"]["net_settlement_due_5d"], 50.0)
        self.assertAlmostEqual(built["2026-01-07"]["net_settlement_due_5d"], 50.0 + 40.0 - 40.0)

    def test_the_window_is_the_next_five_business_days_and_excludes_the_day_itself(self):
        # settles Friday 2026-01-09; on Friday it is the day itself, not "due" in the next five.
        records = [record()]
        auctions = ns.auction_records(records, DECLARATION)
        built = {r.date.isoformat(): r.values for r in ns.with_net_settlement(rows(*DAYS), auctions, DECLARATION)}
        self.assertAlmostEqual(built["2026-01-09"]["net_settlement"], 10.0)
        self.assertEqual(built["2026-01-09"]["net_settlement_due_5d"], 0.0)
        self.assertAlmostEqual(built["2026-01-05"]["net_settlement_due_5d"], 10.0)  # 4 business days ahead
        self.assertEqual(built["2026-01-05"]["net_settlement"], 0.0)

    def test_a_settlement_six_business_days_ahead_is_outside_the_window(self):
        records = [record(settles="2026-01-14", announced="2026-01-05", auctioned="2026-01-12")]
        auctions = ns.auction_records(records, DECLARATION)
        built = {r.date.isoformat(): r.values for r in ns.with_net_settlement(rows(*DAYS), auctions, DECLARATION)}
        self.assertEqual(built["2026-01-06"]["net_settlement_due_5d"], 0.0)  # Jan 14 is the 6th business day after Jan 6
        self.assertEqual(built["2026-01-07"]["net_settlement_due_5d"], 10.0)  # and the 5th after Jan 7

    def test_the_window_reaches_past_the_last_panel_row(self):
        records = [record(settles="2026-01-20", announced="2026-01-15", auctioned="2026-01-15")]
        auctions = ns.auction_records(records, DECLARATION)
        built = {r.date.isoformat(): r.values for r in ns.with_net_settlement(rows(*DAYS), auctions, DECLARATION)}
        self.assertAlmostEqual(built["2026-01-14"]["net_settlement_due_5d"], 0.0)
        self.assertAlmostEqual(built["2026-01-15"]["net_settlement_due_5d"], 10.0)
        self.assertAlmostEqual(built["2026-01-16"]["net_settlement_due_5d"], 10.0)


class GuardTests(unittest.TestCase):
    """`check_known_columns` refuses a column that is not what was announced by the instant."""

    def setUp(self):
        self.auctions = ns.auction_records(
            [record(announced="2026-01-07", auctioned="2026-01-07")], DECLARATION
        )
        self.good = ns.with_net_settlement(rows(*DAYS), self.auctions, DECLARATION)

    def with_value(self, day, column, value):
        out = []
        for row in self.good:
            values = dict(row.values)
            if row.date.isoformat() == day:
                values[column] = value
            out.append(DailyObservation(row.date, values))
        return out

    def test_the_built_columns_pass(self):
        ns.check_known_columns(self.good, self.auctions, DECLARATION)

    def test_a_column_counting_an_unannounced_auction_is_refused(self):
        # on 2026-01-06 the 2026-01-09 settlement was not yet announced (announced 2026-01-07).
        bad = self.with_value("2026-01-06", "net_settlement_due_5d", 10.0)
        with self.assertRaises(LookAheadError):
            ns.check_known_columns(bad, self.auctions, DECLARATION)

    def test_a_column_leaving_out_an_announced_auction_is_refused(self):
        bad = self.with_value("2026-01-08", "net_settlement_due_5d", 0.0)
        with self.assertRaises(StaleReadError):
            ns.check_known_columns(bad, self.auctions, DECLARATION)

    def test_a_hole_is_not_read(self):
        ns.check_known_columns(self.with_value("2026-01-08", "net_settlement", None), self.auctions, DECLARATION)


class ReconciliationTests(unittest.TestCase):
    def test_gross_offering_by_settlement_day_sums_the_offerings(self):
        auctions = ns.auction_records(
            [record(offering=50e9), record(offering=40e9, term="8-Week"), record(kind="Note", offering=60e9)],
            DECLARATION,
        )
        gross = ns.gross_by_day(auctions)
        self.assertAlmostEqual(gross[date(2026, 1, 9)]["treasury_settlement"], 150.0)
        self.assertAlmostEqual(gross[date(2026, 1, 9)]["treasury_settlement_bills"], 90.0)
        self.assertAlmostEqual(gross[date(2026, 1, 9)]["treasury_settlement_coupons"], 60.0)


class SnapshotTests(unittest.TestCase):
    """The tracked snapshot, fetched with the repository's own code, parses under the declaration."""

    def test_the_snapshot_parses_and_every_announcement_precedes_its_settlement(self):
        manifest = next(SNAPSHOT.glob("*.manifest.json"))
        meta = json.loads(manifest.read_text())
        payload = SNAPSHOT / Path(meta["path"]).name
        auctions = ns.load_snapshot(payload, DECLARATION)
        self.assertGreater(len(auctions), 3000)
        self.assertTrue(all(a.announced_at.date() <= a.settles for a in auctions))


def _script():
    import importlib.util
    import sys

    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("net_settlement_script", ROOT / "scripts" / "net_settlement.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


JUDGE = json.loads((ROOT / "metadata" / "pressure_judge.json").read_text())


class CandidateDeclarationTests(unittest.TestCase):
    """The judge's declaration carries each candidate as the script reads it."""

    def test_both_candidates_are_declared_to_the_judge_with_their_controls(self):
        for name, spec in DECLARATION_JSON["candidates"].items():
            self.assertEqual(JUDGE["candidates"][name]["role"], "candidate")
            self.assertEqual(JUDGE["candidates"][name]["track"], "N (#426)")
            self.assertIn(spec["control"], JUDGE["candidates"])

    def test_the_judge_lists_the_features_the_script_reads(self):
        script = _script()
        self.assertEqual(
            sorted(script.hierarchical_features(1, True)),
            sorted(JUDGE["candidates"]["hierarchical_logistic_net"]["features"]),
        )
        self.assertEqual(
            list(script.onset_features(1, True)[0]), JUDGE["candidates"]["onset_logistic_net+recalibrated"]["features"]
        )

    def test_the_net_columns_stay_at_every_horizon_and_the_settlement_leaves(self):
        script = _script()
        for h in range(1, 6):
            for features in (script.hierarchical_features(h, True), script.onset_features(h, True)[0]):
                for column in ns.COLUMNS:
                    self.assertIn(column, features)
            for features in (script.hierarchical_features(h, False), script.onset_features(h, False)[0]):
                for column in ns.COLUMNS:
                    self.assertNotIn(column, features)
        self.assertNotIn("treasury_settlement", script.onset_features(2, True)[0])

    def test_the_controls_read_the_columns_of_their_own_tracks_only(self):
        script = _script()
        self.assertEqual(
            sorted(script.hierarchical_features(1, False)),
            sorted(JUDGE["candidates"]["hierarchical_logistic"]["features"]),
        )
        self.assertEqual(
            list(script.onset_features(1, False)[0]), JUDGE["candidates"]["onset_logistic+recalibrated"]["features"]
        )

    def test_the_scoring_window_ends_before_the_lockbox(self):
        self.assertEqual(DECLARATION_JSON["scoring"]["last_day"], JUDGE["scoring"]["last_day"])
        self.assertEqual(DECLARATION_JSON["thresholds_bp"], JUDGE["thresholds_bp"])

    def test_the_columns_are_off_in_the_published_feature_map(self):
        from repo_model import contract

        for column in ns.COLUMNS:
            self.assertNotIn(column, contract.FEATURE_FIELDS)


DECLARATION_JSON = json.loads((ROOT / "metadata" / "net_settlement.json").read_text())


if __name__ == "__main__":
    unittest.main()
