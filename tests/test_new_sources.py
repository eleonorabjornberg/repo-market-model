"""New data sources for the ordinary-day gap, and the columns read from them (#630).

Four readers, all off in every published declaration and registered in
`metadata/sources_measurement.json`: the primary dealers' financing and fails
(`nyfed_pd_financing`), the Treasury's auction results (`treasury_auction_results`),
the number of counterparties in the Desk's overnight reverse repo operations
(`nyfed_on_rrp_counterparties`) and the Treasury's daily cash issues and redemptions of debt
(`treasury_dts_debt_cash`).
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import tempfile
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path
from types import MappingProxyType
from unittest import mock

from repo_model import contract, measurement_fields, new_sources
from repo_model.asof import InformationRule
from repo_model.data import WEEKLY_CARRY_MAX_STALENESS_DAYS, DailyObservation
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
PUBLISHED = json.loads((ROOT / "metadata" / "sources.json").read_text())
REGISTRY = measurement_fields.load_registry()
SNAPSHOTS = ROOT / "tests" / "fixtures" / "snapshots" / "new_sources"


def weekdays(start, count):
    out, day = [], start
    while len(out) < count:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


def pd_export(*rows):
    handle = io.StringIO()
    writer = csv.writer(handle, quoting=csv.QUOTE_ALL)
    writer.writerow(["As Of Date", "Time Series", "Value (millions)"])
    writer.writerows(rows)
    return handle.getvalue().encode()


class PrimaryDealerReaderTests(unittest.TestCase):
    def test_a_series_is_read_in_billions_and_a_suppressed_value_is_skipped(self):
        payload = pd_export(
            ("2024-05-01", "PDSORA-UTSETTOT", "2500000"),
            ("2024-05-08", "PDSORA-UTSETTOT", "*"),
            ("2024-05-01", "PDFTD-UST", "1200"),
            ("2024-05-01", "PDPOSGST-TOT", "300000"),
        )
        got = new_sources.parse_pd_export(payload)
        self.assertEqual(got["pd_repo_ust"], {date(2024, 5, 1): 2500.0})
        self.assertEqual(got["pd_fails_deliver_ust"], {date(2024, 5, 1): 1.2})
        self.assertEqual(got["pd_reverse_repo_ust"], {})

    def test_a_withheld_week_is_recorded_as_suppressed_and_is_not_a_value(self):
        payload = pd_export(
            ("2024-05-01", "PDSORA-UTSETTOT", "2500000"),
            ("2024-05-08", "PDSORA-UTSETTOT", "*"),
            ("2024-05-15", "PDSORA-UTSETTOT", "*"),
            ("2024-05-08", "PDSIRRA-UTSETTOT", "*"),
            ("2026-01-07", "PDSORA-UTSETTOT", "*"),
        )
        got = new_sources.parse_pd_suppressed(payload)
        self.assertEqual(got["pd_repo_ust"], (date(2024, 5, 8), date(2024, 5, 15)))
        self.assertEqual(got["pd_reverse_repo_ust"], (date(2024, 5, 8),))
        self.assertEqual(got["pd_fails_deliver_ust"], ())
        self.assertNotIn(date(2024, 5, 8), new_sources.parse_pd_export(payload)["pd_repo_ust"])

    def test_the_withheld_weeks_are_summarised_as_a_count_a_longest_run_and_years(self):
        weeks = [date(2022, 12, 21), date(2022, 12, 28), date(2023, 1, 4), date(2023, 3, 1)]
        self.assertEqual(
            new_sources.summarise_suppressed(weeks),
            {"count": 4, "longest_run_weeks": 3, "by_year": {2022: 2, 2023: 2}},
        )
        self.assertEqual(new_sources.summarise_suppressed(()), {"count": 0, "longest_run_weeks": 0, "by_year": {}})

    def test_no_day_after_the_end_is_read(self):
        payload = pd_export(
            ("2025-12-31", "PDSORA-UTSETTOT", "1000"),
            ("2026-01-07", "PDSORA-UTSETTOT", "2000"),
        )
        self.assertEqual(new_sources.parse_pd_export(payload)["pd_repo_ust"], {date(2025, 12, 31): 1.0})

    def test_a_response_without_the_columns_is_refused(self):
        with self.assertRaises(ValueError):
            new_sources.parse_pd_export(b'"a","b"\n"1","2"\n')


def auction(day, closing, accepted, dealers, indirect, tendered, **extra):
    record = {
        "auction_date": day,
        "closing_time_comp": closing,
        "total_accepted": str(accepted),
        "primary_dealer_accepted": str(dealers),
        "indirect_bidder_accepted": str(indirect),
        "total_tendered": str(tendered),
        "bid_to_cover_ratio": "2.5",
    }
    record.update(extra)
    return record


def auction_payload(*records):
    return json.dumps({"data": list(records), "meta": {}}).encode()


class AuctionReaderTests(unittest.TestCase):
    def test_a_day_sums_its_auctions_and_shares_are_of_the_accepted_total(self):
        payload = auction_payload(
            auction("2024-05-07", "11:30 AM", 60e9, 3e9, 30e9, 150e9),
            auction("2024-05-07", "01:00 PM", 40e9, 20e9, 10e9, 100e9),
        )
        got = new_sources.parse_auction_results(payload)
        day = date(2024, 5, 7)
        self.assertAlmostEqual(got["auc_accepted_bn"][day], 100.0)
        self.assertAlmostEqual(got["auc_dealer_share"][day], 0.23)
        self.assertAlmostEqual(got["auc_indirect_share"][day], 0.40)
        self.assertAlmostEqual(got["auc_cover"][day], 2.5)

    def test_an_auction_without_a_result_is_skipped(self):
        payload = auction_payload(
            auction("2024-05-07", "01:00 PM", 0, 0, 0, 0, bid_to_cover_ratio="null", total_accepted="null")
        )
        self.assertEqual(new_sources.parse_auction_results(payload)["auc_accepted_bn"], {})

    def test_no_day_after_the_end_is_read(self):
        payload = auction_payload(auction("2026-01-06", "01:00 PM", 10e9, 1e9, 1e9, 30e9))
        self.assertEqual(new_sources.parse_auction_results(payload)["auc_accepted_bn"], {})

    def test_a_result_after_the_afternoon_cut_is_not_public_at_the_decision(self):
        """The declared instant is 15:00 New York time on the auction day, so an auction that closes later is refused.

        Recorded mutation (CLAUDE.md), 12 October 2026, in a disposable copy:
        `src/repo_model/new_sources.py`, `require_result_public`, the line
        `if closing > AUCTION_LATEST_CLOSE:` mutated to `if False:`. This test then fails with
        `AssertionError: LookAheadError not raised`.
        """

        payload = auction_payload(auction("2024-05-07", "04:00 PM", 10e9, 1e9, 1e9, 30e9))
        with self.assertRaises(LookAheadError):
            new_sources.parse_auction_results(payload)

    def test_a_closing_time_that_cannot_be_read_is_refused(self):
        payload = auction_payload(auction("2024-05-07", "after lunch", 10e9, 1e9, 1e9, 30e9))
        with self.assertRaises(ValueError):
            new_sources.parse_auction_results(payload)


def operation(day, counterparties, updated=None, note="", kind="Reverse Repo", **extra):
    record = {
        "operationId": f"RP {day}",
        "operationDate": day,
        "operationType": kind,
        "participatingCpty": counterparties,
        "lastUpdated": updated or f"{day} 13:15:50",
        "note": note,
    }
    record.update(extra)
    return record


def operations_payload(*records):
    return json.dumps({"repo": {"operations": list(records)}}).encode()


class OnRrpCounterpartyReaderTests(unittest.TestCase):
    def test_the_count_of_counterparties_is_read_for_a_reverse_repo_operation(self):
        payload = operations_payload(
            operation("2024-05-07", 60),
            operation("2024-05-07", 9, kind="Repo"),
        )
        got = new_sources.parse_on_rrp_counterparties(payload)
        self.assertEqual(got["rrp_counterparties"], {date(2024, 5, 7): 60.0})

    def test_a_small_value_exercise_is_left_out(self):
        payload = operations_payload(
            operation("2024-10-16", 44, note="This operation is a Small Value Exercise (SVE)."),
            operation("2024-10-16", 70),
        )
        got = new_sources.parse_on_rrp_counterparties(payload)
        self.assertEqual(got["rrp_counterparties"], {date(2024, 10, 16): 70.0})

    def test_a_record_written_after_its_day_is_not_the_published_one(self):
        """A record the Desk rewrote on a later day cannot be shown to have said the same at publication.

        Recorded mutation (CLAUDE.md), 12 October 2026, in a disposable copy:
        `src/repo_model/new_sources.py`, `require_unamended`, the line
        `if written > operation_day:` mutated to `if False:`. This test then fails with
        `AssertionError: LookAheadError not raised`.
        """

        record = operation("2023-01-05", 55, updated="2023-01-13 10:00:00")
        with self.assertRaises(LookAheadError):
            new_sources.require_unamended(record)
        payload = operations_payload(record, operation("2023-01-06", 58))
        got = new_sources.parse_on_rrp_counterparties(payload)
        self.assertEqual(got["rrp_counterparties"], {date(2023, 1, 6): 58.0})
        self.assertEqual(got["amended_days"], [date(2023, 1, 5)])

    def test_the_propositions_are_never_read(self):
        payload = operations_payload(operation("2024-05-07", 60, propositions="not a list"))
        self.assertEqual(
            new_sources.parse_on_rrp_counterparties(payload)["rrp_counterparties"],
            {date(2024, 5, 7): 60.0},
        )

    def test_a_record_with_no_count_is_refused(self):
        payload = operations_payload(operation("2024-05-07", None))
        with self.assertRaises(ValueError):
            new_sources.parse_on_rrp_counterparties(payload)


def dts_line(day, name, amount):
    return {"record_date": day, "transaction_catg": name, "transaction_today_amt": str(amount)}


def dts_payload(*lines):
    return json.dumps({"data": list(lines), "meta": {"count": len(lines), "total-count": len(lines)}}).encode()


class DtsDebtCashReaderTests(unittest.TestCase):
    def test_issues_and_redemptions_are_in_billions_and_the_net_is_their_difference(self):
        payload = dts_payload(
            dts_line("2024-06-14", "Public Debt Cash Issues (Table IIIB)", 125840),
            dts_line("2024-06-14", "Public Debt Cash Redemp. (Table IIIB)", 136641),
        )
        got = new_sources.parse_dts_debt_cash([payload])
        day = date(2024, 6, 14)
        self.assertAlmostEqual(got["dts_debt_issues_bn"][day], 125.84)
        self.assertAlmostEqual(got["dts_debt_net_bn"][day], 125.84 - 136.641)

    def test_both_spellings_of_the_line_names_are_one_series(self):
        payload = dts_payload(
            dts_line("2018-06-14", "Public Debt Cash Issues (Table III-B)", 1000),
            dts_line("2018-06-14", "Public Debt Cash Redemp. (Table III-B)", 400),
        )
        got = new_sources.parse_dts_debt_cash([payload])
        self.assertAlmostEqual(got["dts_debt_net_bn"][date(2018, 6, 14)], 0.6)

    def test_a_day_with_only_one_leg_has_no_net(self):
        payload = dts_payload(dts_line("2024-06-14", "Public Debt Cash Issues (Table IIIB)", 5))
        got = new_sources.parse_dts_debt_cash([payload])
        self.assertEqual(got["dts_debt_net_bn"], {})
        self.assertIn(date(2024, 6, 14), got["dts_debt_issues_bn"])

    def test_two_values_for_one_line_and_day_are_refused(self):
        payload = dts_payload(
            dts_line("2024-06-14", "Public Debt Cash Issues (Table IIIB)", 5),
            dts_line("2024-06-14", "Public Debt Cash Issues (Table IIIB)", 6),
        )
        with self.assertRaises(ValueError):
            new_sources.parse_dts_debt_cash([payload])

    def test_no_day_after_the_end_is_read(self):
        payload = dts_payload(
            dts_line("2026-01-06", "Public Debt Cash Issues (Table IIIB)", 5),
            dts_line("2026-01-06", "Public Debt Cash Redemp. (Table IIIB)", 5),
        )
        self.assertEqual(new_sources.parse_dts_debt_cash([payload])["dts_debt_net_bn"], {})

    def test_a_truncated_page_is_refused(self):
        payload = json.dumps({"data": [], "meta": {"count": 0, "total-count": 5}}).encode()
        with self.assertRaises(ValueError):
            new_sources.parse_dts_debt_cash([payload])

    def test_one_request_per_line_name_and_year(self):
        urls = []

        def downloader(url):
            urls.append(url)
            return dts_payload()

        with tempfile.TemporaryDirectory() as directory:
            artifacts = new_sources.fetch_dts_debt_cash(Path(directory), "2023-01-01", "2024-12-31", downloader)
        self.assertEqual(len(urls), 2 * len(new_sources.DTS_LINE_NAMES))
        self.assertEqual(len(artifacts), len(urls))


class AddColumnsTests(unittest.TestCase):
    DAYS = weekdays(date(2024, 5, 1), 20)

    def rows(self):
        return [DailyObservation(day, {"spread_bps": 1.0}) for day in self.DAYS]

    def test_a_weekly_value_starts_on_the_first_panel_day_at_or_after_its_date_and_is_carried(self):
        holiday = date(2024, 5, 8)
        rows = [r for r in self.rows() if r.date != holiday]
        series = {"pd_repo_ust": {date(2024, 5, 1): 10.0, holiday: 11.0}}
        out = {r.date: r.values for r in new_sources.add_columns(rows, series)}
        self.assertEqual(out[date(2024, 5, 1)]["pd_repo_ust"], 10.0)
        self.assertEqual(out[date(2024, 5, 7)]["pd_repo_ust"], 10.0)
        self.assertEqual(out[date(2024, 5, 9)]["pd_repo_ust"], 11.0)
        self.assertEqual(out[date(2024, 5, 14)]["pd_repo_ust"], 11.0)

    def test_a_weekly_value_is_not_carried_beyond_the_declared_staleness(self):
        """A weekly value is carried for `WEEKLY_CARRY_MAX_STALENESS_DAYS` after its date and no longer.

        The bound is `data.WEEKLY_CARRY_MAX_STALENESS_DAYS` (13 days, `docs/decisions/weekly-carry.md`):
        one missed print is tolerated, two in a row leave holes.

        Recorded mutation (CLAUDE.md), 13 October 2026, in a disposable copy:
        `src/repo_model/new_sources.py`, `add_columns`, the line
        `if current is not None and current_day is not None and (day - current_day).days <=
        WEEKLY_CARRY_MAX_STALENESS_DAYS:` mutated to `if current is not None:`. This test then fails with
        `AssertionError: 10.0 is not None` (on 2024-05-15, the first day past the bound).
        """

        series = {"pd_repo_ust": {date(2024, 5, 1): 10.0}}
        out = {r.date: r.values["pd_repo_ust"] for r in new_sources.add_columns(self.rows(), series)}
        last_carried = date(2024, 5, 1) + timedelta(days=WEEKLY_CARRY_MAX_STALENESS_DAYS)
        self.assertEqual(last_carried, date(2024, 5, 14))
        self.assertEqual(out[date(2024, 5, 14)], 10.0)
        self.assertIsNone(out[date(2024, 5, 15)])
        self.assertIsNone(out[self.DAYS[-1]])

    def test_a_carry_that_starts_after_a_holiday_is_bounded_from_the_value_date(self):
        holiday = date(2024, 5, 1)
        rows = [r for r in self.rows() if r.date != holiday]
        out = {r.date: r.values["pd_repo_ust"] for r in new_sources.add_columns(rows, {"pd_repo_ust": {holiday: 10.0}})}
        self.assertEqual(out[date(2024, 5, 14)], 10.0)
        self.assertIsNone(out[date(2024, 5, 15)])

    def test_one_missed_print_is_bridged_by_the_carry(self):
        series = {"pd_repo_ust": {date(2024, 5, 1): 10.0, date(2024, 5, 15): 12.0}}
        out = {r.date: r.values["pd_repo_ust"] for r in new_sources.add_columns(self.rows(), series)}
        self.assertEqual(out[date(2024, 5, 14)], 10.0)
        self.assertEqual(out[date(2024, 5, 15)], 12.0)
        self.assertEqual(out[date(2024, 5, 28)], 12.0)

    def test_a_weekly_column_is_empty_before_its_first_value(self):
        out = {r.date: r.values for r in new_sources.add_columns(self.rows(), {"pd_repo_ust": {date(2024, 5, 8): 1.0}})}
        self.assertIsNone(out[date(2024, 5, 7)]["pd_repo_ust"])
        self.assertEqual(out[date(2024, 5, 8)]["pd_repo_ust"], 1.0)

    def test_a_daily_value_sits_on_its_own_day_and_other_days_are_empty(self):
        series = {"auc_accepted_bn": {date(2024, 5, 7): 100.0}}
        out = {r.date: r.values for r in new_sources.add_columns(self.rows(), series)}
        self.assertEqual(out[date(2024, 5, 7)]["auc_accepted_bn"], 100.0)
        self.assertIsNone(out[date(2024, 5, 8)]["auc_accepted_bn"])

    def test_a_panel_past_the_end_is_refused(self):
        """No day after 2025-12-31 is read.

        Recorded mutation (CLAUDE.md), 12 October 2026, in a disposable copy:
        `src/repo_model/new_sources.py`, `add_columns`, the line `if row.date > END:` mutated to
        `if False:`. This test then fails with `AssertionError: LookAheadError not raised`.
        """

        late = [DailyObservation(date(2026, 1, 6), {"spread_bps": 1.0})]
        with self.assertRaises(LookAheadError):
            new_sources.add_columns(late, {})

    def test_the_input_is_not_changed(self):
        rows = self.rows()
        new_sources.add_columns(rows, {"auc_accepted_bn": {self.DAYS[3]: 1.0}})
        self.assertNotIn("auc_accepted_bn", rows[3].values)


class RegistryTests(unittest.TestCase):
    def test_every_column_names_registered_fields(self):
        for column, pairs in new_sources.COLUMN_FIELDS.items():
            for source, field in pairs:
                self.assertIn(source, REGISTRY, column)
                self.assertIn(field, REGISTRY[source]["fields"], f"{column}: {source}.{field}")

    def test_the_new_sources_stay_out_of_the_frozen_registry(self):
        for source in new_sources.SOURCES:
            self.assertNotIn(source, PUBLISHED)
            self.assertNotIn(source, contract.UNMODELLED_SOURCES)
            self.assertIn(source, REGISTRY)

    def test_no_published_feature_map_carries_a_new_column(self):
        for column in new_sources.COLUMN_FIELDS:
            self.assertNotIn(column, contract.FEATURE_FIELDS, column)

    def test_each_declaration_is_a_valid_release_lag(self):
        for source in new_sources.SOURCES:
            self.assertEqual(contract.validate_release_lag(source, REGISTRY[source]["release_lag"]), [])

    def test_every_declared_field_is_a_column_or_stated(self):
        used = {pair for pairs in new_sources.COLUMN_FIELDS.values() for pair in pairs}
        for source in new_sources.SOURCES:
            for field in REGISTRY[source]["fields"]:
                self.assertIn((source, field), used, f"{source}.{field} feeds no column")


def switched_on():
    fields = dict(new_sources.COLUMN_FIELDS)
    return mock.patch.multiple(
        contract,
        FEATURE_FIELDS=MappingProxyType({**contract.FEATURE_FIELDS, **fields}),
        FEATURE_SOURCES=MappingProxyType(
            {
                **contract.FEATURE_SOURCES,
                **{c: tuple(sorted({s for s, _f in pairs})) for c, pairs in fields.items()},
            }
        ),
    )


class AsOfTests(unittest.TestCase):
    """A weekly dealer figure is read six business days after its Wednesday, not on it.

    The primary dealer figures for a Wednesday are published on the Thursday of the following week
    (`nyfed_pd_financing.release_lag`, copied from `nyfed_fr2004`). A forecast at the 16:00
    decision of Wednesday 2026-01-21 cannot read the row of Tuesday 2026-01-13 (public at 16:30 on the 21st),
    and reads the row of Monday 2026-01-12, public at 16:30 on Tuesday 2026-01-20.

    Recorded mutation (CLAUDE.md), 12 October 2026, in a disposable copy:
    `metadata/sources_measurement.json`, `nyfed_pd_financing.release_lag`, `"days": 6` mutated to
    `"days": 2`. `test_a_weekly_figure_is_read_after_its_release` then fails with `AssertionError`
    (`datetime.date(2026, 1, 16) != datetime.date(2026, 1, 12)`): the forecast reads a figure that
    is not yet public.
    """

    DATES = weekdays(date(2026, 1, 5), 40)
    DECISION = time(16, 0)

    def rows(self):
        return [
            DailyObservation(day, {"spread_bps": 1.0, **{column: 1.0 for column in new_sources.COLUMN_FIELDS}})
            for day in self.DATES
        ]

    def test_a_weekly_figure_is_read_after_its_release(self):
        with switched_on():
            rule = InformationRule(REGISTRY, ("spread_bps", "pd_repo_ust"), decision_time=self.DECISION)
            scored = self.DATES.index(date(2026, 1, 22))
            info = rule.information_set(self.DATES, scored)
            (read,) = [r for r in info.reads if r.feature == "pd_repo_ust"]
            self.assertEqual(self.DATES[read.row], date(2026, 1, 12))
            self.assertEqual(read.available_at, datetime(2026, 1, 20, 16, 30))
            late = self.DATES.index(date(2026, 1, 13))
            self.assertGreater(rule.availability(self.DATES, read.fields, late), info.decision_instant)
            forced = info._replace(
                reads=tuple(r._replace(row=late) if r.feature == "pd_repo_ust" else r for r in info.reads)
            )
            with self.assertRaises(LookAheadError):
                rule.check(self.DATES, forced)

    def test_every_new_column_passes_both_guards(self):
        with switched_on():
            rule = InformationRule(REGISTRY, ("spread_bps", *new_sources.COLUMN_FIELDS), decision_time=self.DECISION)
            for scored in range(15, len(self.DATES)):
                rule.check(self.DATES, rule.information_set(self.DATES, scored))


class TrackedSnapshotTests(unittest.TestCase):
    def test_every_tracked_snapshot_matches_its_manifest(self):
        found = sorted(SNAPSHOTS.rglob("*.manifest.json"))
        self.assertTrue(found, "no new-source snapshot is tracked")
        for manifest_path in found:
            manifest = json.loads(manifest_path.read_text())
            path = manifest_path.parent / manifest_path.name[: -len(".manifest.json")]
            digest = manifest.get("sha256", manifest.get("extract_sha256"))
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest, path.name)

    def test_the_tracked_extract_reads_to_the_declared_series(self):
        path = SNAPSHOTS / "nyfed_pd_financing" / "pd_financing_extract.csv"
        got = new_sources.parse_pd_export(path.read_bytes())
        for column, series in got.items():
            self.assertTrue(series, column)
            self.assertLessEqual(max(series), new_sources.END)
            self.assertGreaterEqual(min(series), date(2013, 4, 3))

    def test_the_tracked_dts_snapshots_read_to_both_legs(self):
        payloads = [path.read_bytes() for path in sorted((SNAPSHOTS / "treasury_dts_debt_cash").glob("*.json")) if not path.name.endswith("manifest.json")]
        got = new_sources.parse_dts_debt_cash(payloads)
        self.assertGreater(len(got["dts_debt_net_bn"]), 1000)
        self.assertLessEqual(max(got["dts_debt_net_bn"]), new_sources.END)

    def test_the_tracked_auctions_read_to_results(self):
        path = ROOT / "tests" / "fixtures" / "snapshots" / "treasury_auctions" / "auctions_2018_present.json"
        got = new_sources.parse_auction_results(path.read_bytes())
        self.assertGreater(len(got["auc_accepted_bn"]), 1000)
        for day, share in got["auc_dealer_share"].items():
            self.assertTrue(0.0 <= share <= 1.0, day)

    def test_the_tracked_on_rrp_snapshots_read_to_counts(self):
        directory = ROOT / "tests" / "fixtures" / "snapshots" / "on_rrp_inputs" / "nyfed_on_rrp"
        counts = {}
        for path in sorted(directory.glob("*.json")):
            if path.name.endswith("manifest.json"):
                continue
            counts.update(new_sources.parse_on_rrp_counterparties(path.read_bytes())["rrp_counterparties"])
        self.assertGreater(len(counts), 1000)
        self.assertLessEqual(max(counts), new_sources.END)


if __name__ == "__main__":
    unittest.main()
