"""A Treasury settlement dated from its auction result, measured and off (#175).

`metadata/settlement_result_dating.json` declares it; `repo_model.settlement_dating`
implements it. No published declaration reads either.
"""

from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from repo_model import settlement_dating as sd  # noqa: E402
from repo_model.asof import InformationRule, StaleReadError  # noqa: E402
from repo_model.data import DailyObservation, load_daily_panel  # noqa: E402
from repo_model.ingest import load_source_registry  # noqa: E402
from repo_model.splits import LookAheadError  # noqa: E402

DECLARATION = ROOT / "metadata" / "settlement_result_dating.json"
REGISTRY = ROOT / "metadata" / "sources.json"
SNAPSHOT = (
    ROOT / "tests" / "fixtures" / "snapshots" / "funding_inputs" / "treasury_auctions"
    / "20260914T051023Z_722359ea9bc7.json"
)


def weekdays(start, count):
    out, when = [], start
    while len(out) < count:
        if when.weekday() < 5:
            out.append(when)
        when += timedelta(days=1)
    return out


def record(auction, issue, kind="Note", amount="40000000000", accepted="40000000000", closing="01:00 PM"):
    return {
        "auction_date": auction.isoformat(), "issue_date": issue.isoformat(),
        "security_type": kind, "offering_amt": amount, "total_accepted": accepted,
        "closing_time_comp": closing,
    }


class ResultDatingTests(unittest.TestCase):
    """A settlement's date and amount are public from its auction result, and not before.

    For the forecast made `h` panel days before a settlement day, a settlement
    column holds the offering amounts of the auctions settling that day whose
    results were public by the declared instant on the decision day.
    `check_known_columns` holds a column to that in both directions: one that
    counts an auction whose result was not yet public raises `LookAheadError`,
    and one that leaves out an auction whose result was public raises
    `StaleReadError`.

    Red first: written before `repo_model.settlement_dating` existed
    (`ModuleNotFoundError`).

    Mutation record. In a `git archive` copy of the tree under /tmp, CPython
    3.11, this class run alone, unmutated control green. In `known_amount`, the
    guard `and result.public_at <= instant` was mutated to
    `and result.public_at is not None` (every result on file treated as public
    at any instant). The target was found once before the change and was gone
    after. Killed: `test_a_result_after_the_decision_is_invisible` and
    `test_reading_a_result_after_the_decision_raises` failed with
    `AssertionError` (the second as `LookAheadError not raised`), and
    `test_a_result_not_on_file_is_in_no_sum` failed with `AssertionError`.
    """

    def setUp(self):
        self.declaration = sd.load_result_dating(DECLARATION)
        self.dates = weekdays(date(2024, 4, 1), 8)
        # A coupon auctioned on dates[3] settles on dates[6]: public three panel days ahead.
        self.records = [record(self.dates[3], self.dates[6])]
        self.results = sd.auction_results(self.records, self.declaration)
        self.rows = [
            DailyObservation(day, {
                "sofr": 5.31, "iorb": 5.40,
                "treasury_settlement": 40.0 if day == self.dates[6] else 0.0,
                "treasury_settlement_bills": 0.0,
                "treasury_settlement_coupons": 40.0 if day == self.dates[6] else 0.0,
                "treasury_settlement_soma": 0.0,
            })
            for day in self.dates
        ]

    def known(self, horizon):
        return sd.known_columns(self.rows, self.results, horizon, self.declaration)

    def test_a_result_before_the_decision_is_read(self):
        for horizon in (1, 2, 3):
            with self.subTest(horizon=horizon):
                row = self.known(horizon)[6].values
                self.assertEqual(row["treasury_settlement"], 40.0)
                self.assertEqual(row["treasury_settlement_coupons"], 40.0)
                self.assertEqual(row["treasury_settlement_bills"], 0.0)

    def test_a_result_after_the_decision_is_invisible(self):
        for horizon in (4, 5):
            with self.subTest(horizon=horizon):
                row = self.known(horizon)[6].values
                self.assertEqual(row["treasury_settlement"], 0.0)
                self.assertEqual(row["treasury_settlement_coupons"], 0.0)

    def test_reading_a_result_after_the_decision_raises(self):
        # The published panel's own column at h = 4 counts the dates[3] result
        # for a decision on dates[2].
        with self.assertRaises(LookAheadError) as caught:
            sd.check_known_columns(self.rows, self.results, 4, self.declaration)
        self.assertIn(self.dates[6].isoformat(), str(caught.exception))
        sd.check_known_columns(self.known(4), self.results, 4, self.declaration)

    def test_leaving_out_a_public_result_raises(self):
        stale = self.known(4)
        with self.assertRaises(StaleReadError):
            sd.check_known_columns(stale, self.results, 3, self.declaration)
        sd.check_known_columns(self.known(3), self.results, 3, self.declaration)

    def test_a_result_not_on_file_is_in_no_sum(self):
        records = [record(self.dates[3], self.dates[6], accepted="null")]
        results = sd.auction_results(records, self.declaration)
        self.assertIsNone(results[0].public_at)
        for horizon in (1, 3):
            with self.subTest(horizon=horizon):
                known = sd.known_columns(self.rows, results, horizon, self.declaration)
                self.assertEqual(known[6].values["treasury_settlement"], 0.0)
                sd.check_known_columns(known, results, horizon, self.declaration)
                with self.assertRaises(LookAheadError):
                    sd.check_known_columns(self.rows, results, horizon, self.declaration)

    def test_a_day_with_no_auction_on_file_reads_zero_and_a_hole_stays_a_hole(self):
        rows = list(self.rows)
        rows[2] = DailyObservation(rows[2].date, dict(rows[2].values, treasury_settlement=None))
        known = sd.known_columns(rows, (), 2, self.declaration)
        self.assertEqual(known[6].values["treasury_settlement"], 0.0)
        self.assertIsNone(known[2].values["treasury_settlement"])
        self.assertIsNone(known[0].values["treasury_settlement"])  # no decision day 2 rows before
        self.assertIsNone(known[6].values["treasury_settlement_soma"])

    def test_a_partly_announced_day_counts_only_the_announced_part(self):
        records = self.records + [record(self.dates[5], self.dates[6], kind="Bill", amount="10000000000",
                                         accepted="10000000000", closing="11:30 AM")]
        results = sd.auction_results(records, self.declaration)
        row = sd.known_columns(self.rows, results, 2, self.declaration)[6].values
        self.assertEqual((row["treasury_settlement"], row["treasury_settlement_bills"]), (40.0, 0.0))
        row = sd.known_columns(self.rows, results, 1, self.declaration)[6].values
        self.assertEqual((row["treasury_settlement"], row["treasury_settlement_bills"]), (50.0, 10.0))

    def test_an_auction_closing_after_the_declared_instant_is_refused(self):
        with self.assertRaises(ValueError) as caught:
            sd.auction_results([record(self.dates[3], self.dates[6], closing="03:30 PM")], self.declaration)
        self.assertIn("15:00", str(caught.exception))

    def test_an_unknown_security_type_is_refused(self):
        with self.assertRaises(ValueError):
            sd.auction_results([record(self.dates[3], self.dates[6], kind="Strip")], self.declaration)

    def test_the_registry_variant_dates_the_columns_at_the_horizon(self):
        registry = load_source_registry(REGISTRY)
        for horizon in (1, 2, 5):
            with self.subTest(horizon=horizon):
                variant = sd.result_dated_registry(registry, self.declaration, horizon)
                block = variant["treasury_auctions"]["scheduled_availability"]
                self.assertEqual((block["days"], block["available_time"]), (horizon, "15:00"))
                rule = InformationRule(variant, ("spread_bps", "treasury_settlement"),
                                       decision_time=time(16, 0), horizon=horizon)
                info = rule.information_set(self.dates, 6)
                rule.check(self.dates, info)
                read = {r.feature: r for r in info.reads}["treasury_settlement"]
                self.assertEqual(read.row, 6)
                self.assertEqual(read.available_at, datetime.combine(self.dates[6 - horizon], time(15, 0)))
        published = registry["treasury_auctions"]["scheduled_availability"]
        self.assertEqual(published["days"], 1)
        self.assertEqual(
            {k: v for k, v in sd.result_dated_registry(registry, self.declaration, 1)["treasury_auctions"]
             ["scheduled_availability"].items() if k not in ("evidence", "note")},
            {k: v for k, v in published.items() if k not in ("evidence", "note")},
        )

    def test_the_published_registry_is_not_touched(self):
        registry = load_source_registry(REGISTRY)
        before = json.dumps(registry, sort_keys=True, default=str)
        sd.result_dated_registry(registry, self.declaration, 3)
        self.assertEqual(json.dumps(registry, sort_keys=True, default=str), before)


class TrackedSnapshotTests(unittest.TestCase):
    """The declaration on the tracked snapshot and the published panel.

    At h = 1 the result-dated columns are the published panel's, row for row:
    every auction settling inside the panel was held at least one panel day
    before it settled. At h = 2 the published columns are refused, because
    some auctions were held exactly one panel day ahead.
    """

    @classmethod
    def setUpClass(cls):
        from repo_model import cli

        manifest = json.loads((ROOT / "metadata" / "funding_panel_manifest.json").read_text())
        with tempfile.TemporaryDirectory() as directory:
            panel = Path(directory) / "panel.csv"
            with contextlib.redirect_stdout(io.StringIO()):
                code = cli.main([
                    "build", "--raw-root", str(ROOT / "tests/fixtures/snapshots/funding_inputs"),
                    "--output", str(panel), "--build-cutoff", manifest["build_cutoff"],
                    "--decision-time", manifest["decision_time"],
                ])
            assert code == 0, code
            cls.rows = load_daily_panel(panel)
        cls.declaration = sd.load_result_dating(DECLARATION)
        cls.results = sd.load_snapshot_results(SNAPSHOT, cls.declaration)

    def test_at_horizon_one_the_columns_are_the_published_panels(self):
        known = sd.known_columns(self.rows, self.results, 1, self.declaration)
        for column in sd.COLUMNS:
            with self.subTest(column=column):
                for old, new in zip(self.rows[1:], known[1:]):
                    a, b = old.values.get(column), new.values[column]
                    if a is None:
                        self.assertIsNone(b, old.date)
                    else:
                        self.assertAlmostEqual(a, b, places=9, msg=str(old.date))
        sd.check_known_columns(self.rows, self.results, 1, self.declaration)

    def test_at_horizon_two_the_published_columns_are_refused(self):
        with self.assertRaises(LookAheadError):
            sd.check_known_columns(self.rows, self.results, 2, self.declaration)
        for horizon in (2, 3, 4, 5):
            with self.subTest(horizon=horizon):
                known = sd.known_columns(self.rows, self.results, horizon, self.declaration)
                sd.check_known_columns(known, self.results, horizon, self.declaration)

    def test_coverage_counts_only_what_was_announced(self):
        counts = sd.coverage(self.rows, self.results, (1, 2, 3, 4, 5), self.declaration, end=date(2025, 12, 31))
        self.assertEqual(counts[1]["complete"], counts[1]["settlement_days"])
        for shorter, longer in ((1, 2), (2, 3), (3, 4), (4, 5)):
            self.assertGreaterEqual(counts[shorter]["complete"], counts[longer]["complete"])
        self.assertLess(counts[5]["complete"], counts[1]["complete"])


if __name__ == "__main__":
    unittest.main()
