"""The new point-in-time sources and the measurement fields built from them (#377)."""

from __future__ import annotations

import hashlib
import json
import statistics
import tempfile
import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path
from types import MappingProxyType
from unittest import mock
from zoneinfo import ZoneInfo

from repo_model import contract, early_warning, ingest, measurement_fields
from repo_model.asof import InformationRule
from repo_model.data import DailyObservation, next_business_day
from repo_model.ingest import SnapshotArtifact, load_snapshot_manifest, parse_snapshots
from repo_model.splits import LookAheadError

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "metadata" / "sources.json").read_text())
SNAPSHOTS = ROOT / "tests" / "fixtures" / "snapshots"
NEW_YORK = ZoneInfo("America/New_York")

OLD = "Federal Reserve Account"
MID = "Treasury General Account (TGA)"
NEW = "Treasury General Account (TGA) Closing Balance"


def line(day, name, open_bal="0", close_bal="null"):
    return {
        "record_date": day,
        "account_type": name,
        "open_today_bal": open_bal,
        "close_today_bal": close_bal,
    }


def response(*lines):
    return json.dumps({"data": list(lines), "meta": {"count": len(lines), "total-count": len(lines)}}).encode()


def artifact_for(payload, retrieved="2026-10-08T02:29:56+00:00"):
    directory = tempfile.TemporaryDirectory()
    path = Path(directory.name) / "dts.json"
    path.write_bytes(payload)
    return directory, SnapshotArtifact(
        source_id=ingest.TREASURY_DTS_TGA_SOURCE_ID,
        path=path,
        retrieved_at=retrieved,
        sha256=hashlib.sha256(payload).hexdigest(),
        url=ingest.TREASURY_DTS_TGA_URL,
        byte_count=len(payload),
    )


class DtsParserTests(unittest.TestCase):
    """`_treasury_dts_tga_rows`: three eras of the statement's closing-balance line.

    Recorded mutation (CLAUDE.md), 8 October 2026, in a disposable copy:
    `src/repo_model/ingest.py`, `_treasury_dts_tga_rows`, `_next_business_day(ref_date, 1)`
    mutated to `_next_business_day(ref_date, 0)` (a balance public at 16:30 on its own
    date, before the statement is published). `test_a_balance_is_available_on_the_next_business_day`
    then fails with `AssertionError` (the Friday 2026-01-16 balance is declared available
    at 2026-01-16 16:30, not 2026-01-20 16:30).
    """

    def rows(self, *lines):
        directory, artifact = artifact_for(response(*lines))
        self.addCleanup(directory.cleanup)
        return {row.ref_date: row for row in ingest._treasury_dts_tga_rows(artifact, artifact.path.read_bytes())}

    def test_each_era_reads_its_own_column_in_billions(self):
        rows = self.rows(
            line("2018-03-01", OLD, "1", "5448"),
            line("2021-12-01", MID, "213153", "159148"),
            line("2022-04-18", NEW, "841253", "null"),
        )
        self.assertEqual(rows[date(2018, 3, 1)].value, 5.448)
        self.assertEqual(rows[date(2021, 12, 1)].value, 159.148)
        self.assertEqual(rows[date(2022, 4, 18)].value, 841.253)
        self.assertEqual({row.series_id for row in rows.values()}, {"TGA_CLOSE"})

    def test_a_balance_is_available_on_the_next_business_day(self):
        # Friday 2026-01-16; Monday the 19th is a market holiday.
        rows = self.rows(line("2026-01-16", MID, "1", "2"), line("2026-01-21", MID, "1", "2"))
        self.assertEqual(
            rows[date(2026, 1, 16)].available_at, datetime(2026, 1, 20, 16, 30, tzinfo=NEW_YORK)
        )
        self.assertEqual(
            rows[date(2026, 1, 21)].available_at, datetime(2026, 1, 22, 16, 30, tzinfo=NEW_YORK)
        )

    def test_availability_is_capped_at_the_retrieval(self):
        directory, artifact = artifact_for(
            response(line("2026-10-06", NEW, "885414")), retrieved="2026-10-07T12:00:00+00:00"
        )
        self.addCleanup(directory.cleanup)
        (row,) = ingest._treasury_dts_tga_rows(artifact, artifact.path.read_bytes())
        self.assertEqual(row.available_at, datetime(2026, 10, 7, 12, 0, tzinfo=ZoneInfo("UTC")))

    def test_two_closing_balances_on_a_date_are_refused(self):
        with self.assertRaises(ValueError):
            self.rows(line("2022-04-18", NEW, "1"), line("2022-04-18", OLD, "1", "2"))

    def test_another_line_is_refused(self):
        with self.assertRaises(ValueError):
            self.rows(line("2022-04-18", "Total TGA Deposits (Table II)", "1"))

    def test_a_non_numeric_balance_is_refused(self):
        with self.assertRaises(ValueError):
            self.rows(line("2022-04-18", NEW, "null"))

    def test_a_truncated_page_is_refused(self):
        payload = json.dumps(
            {"data": [line("2022-04-18", NEW, "1")], "meta": {"count": 1, "total-count": 2}}
        ).encode()
        directory, artifact = artifact_for(payload)
        self.addCleanup(directory.cleanup)
        with self.assertRaises(ValueError):
            ingest._treasury_dts_tga_rows(artifact, payload)

    def test_the_snapshot_dispatch_reaches_the_adapter(self):
        directory, artifact = artifact_for(response(line("2022-04-18", NEW, "841253")))
        self.addCleanup(directory.cleanup)
        parsed = parse_snapshots([artifact])
        self.assertEqual([row.value for row in parsed.rows], [841.253])


class DtsFetchTests(unittest.TestCase):
    def test_one_request_per_line_name_and_year(self):
        requested = []

        def downloader(url):
            requested.append(url)
            return response()

        with tempfile.TemporaryDirectory() as directory:
            artifacts = ingest.fetch_treasury_dts_tga(
                Path(directory), "2021-06-01", "2022-03-01", downloader
            )
        self.assertEqual(len(artifacts), 6)  # two years, three line names
        self.assertEqual(len(requested), 6)
        self.assertTrue(all(url.startswith(ingest.TREASURY_DTS_TGA_URL + "?") for url in requested))
        self.assertTrue(all("account_type%3Aeq%3A" in url for url in requested))
        self.assertTrue(any("record_date%3Agte%3A2021-06-01" in url for url in requested))
        self.assertTrue(any("record_date%3Alte%3A2022-03-01" in url for url in requested))

    def test_a_reversed_range_is_refused(self):
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(ValueError):
            ingest.fetch_treasury_dts_tga(Path(directory), "2022-01-01", "2021-01-01", lambda url: b"")

    def test_a_response_the_parser_refuses_is_not_saved(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                ingest.fetch_treasury_dts_tga(
                    Path(directory), "2022-01-01", "2022-12-31", lambda url: b'{"data": 5}'
                )
            self.assertEqual(list(Path(directory).rglob("*.json")), [])


class TrackedSnapshotTests(unittest.TestCase):
    """The tracked fetches of 8 October 2026 (#377)."""

    @classmethod
    def setUpClass(cls):
        def rows(directory, wanted):
            artifacts = [load_snapshot_manifest(p) for p in sorted((SNAPSHOTS / directory).rglob("*.manifest.json"))]
            return [r for r in parse_snapshots(artifacts).rows if r.series_id in wanted]

        cls.tga = {r.ref_date: r.value for r in rows("dts_inputs", {"TGA_CLOSE"})}
        cls.wtregen = {r.ref_date: r.value for r in rows("funding_inputs", {"WTREGEN"})}

    def test_every_business_day_has_one_balance(self):
        day, missing = date(2018, 1, 2), []
        last = max(self.tga)
        while day <= last:
            if day not in self.tga and day.weekday() < 5 and next_business_day(day - timedelta(days=1), 1) == day:
                missing.append(day)
            day += timedelta(days=1)
        self.assertEqual(missing, [])
        self.assertEqual(min(self.tga), date(2018, 1, 2))

    def test_the_daily_balance_is_the_weekly_average_the_h41_reports(self):
        """FRED's WTREGEN is the week's average of this balance, to a rounding."""

        def level(day):
            while day not in self.tga:
                day -= timedelta(days=1)
            return self.tga[day]

        checked = []
        for wednesday, published in self.wtregen.items():
            if wednesday < date(2018, 1, 15) or wednesday > max(self.tga):
                continue
            average = statistics.mean(level(wednesday - timedelta(days=k)) for k in range(7))
            checked.append(abs(average - published))
        self.assertGreater(len(checked), 400)
        self.assertLess(max(checked), 0.01)

    def test_the_registry_declares_every_new_series(self):
        self.assertEqual(REGISTRY["treasury_dts_tga"]["fields"], ["TGA_CLOSE"])
        for mnemonic in ingest.OFR_STFM_SEGMENT_MNEMONICS:
            self.assertIn(mnemonic, REGISTRY["ofr_stfm_repo"]["fields"])
            self.assertIn(mnemonic, REGISTRY["ofr_stfm_repo"]["field_frequencies"])
        for field in ("SOFR_p1", "SOFR_p99"):
            self.assertIn(field, REGISTRY["nyfed_sofr"]["fields"])

    def test_every_new_series_has_a_snapshot_with_its_checksum(self):
        seen = set()
        for path in (SNAPSHOTS / "ofr_inputs").rglob("*.manifest.json"):
            manifest = json.loads(path.read_text())
            data = (SNAPSHOTS / "ofr_inputs" / manifest["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), manifest["sha256"])
            seen.add(manifest["url"].rsplit("=", 1)[-1])
        self.assertTrue(set(ingest.OFR_STFM_SEGMENT_MNEMONICS) <= seen)
        for path in (SNAPSHOTS / "dts_inputs").rglob("*.manifest.json"):
            manifest = json.loads(path.read_text())
            data = (SNAPSHOTS / "dts_inputs" / manifest["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), manifest["sha256"])

    def test_sofr_percentiles_are_already_snapshotted(self):
        artifacts = [
            load_snapshot_manifest(p) for p in sorted((SNAPSHOTS / "funding_inputs" / "nyfed-sofr-rate").rglob("*.manifest.json"))
        ]
        series = {row.series_id for row in parse_snapshots(artifacts).rows}
        self.assertTrue({"SOFR_p1", "SOFR_p99"} <= series)


def row(day, **values):
    return DailyObservation(day, {"sofr_p99": 2.0, "iorb": 1.5, **values})


def weekdays(start, count):
    out, day = [], start
    while len(out) < count:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


class BuildColumnsTests(unittest.TestCase):
    def test_the_spread_is_in_basis_points_and_matches_early_warning(self):
        rows = [row(day, sofr_p99=1.5 + 0.01 * i) for i, day in enumerate(weekdays(date(2024, 1, 1), 20))]
        built = measurement_fields.build_columns(rows)
        reference = early_warning.build_columns(rows)
        for ours, theirs in zip(built, reference):
            self.assertEqual(ours.values["sofr_p99_iorb_bps"], theirs.values["sofr_p99_iorb_bps"])
        self.assertAlmostEqual(built[3].values["sofr_p99_iorb_bps"], 3.0)

    def test_the_rolling_sd_needs_fifteen_rows_and_is_the_sample_sd(self):
        days = weekdays(date(2024, 1, 1), 20)
        rows = [row(day, sofr_p99=1.5 + 0.01 * (i % 4)) for i, day in enumerate(days)]
        built = measurement_fields.build_columns(rows)
        self.assertTrue(all(b.values["sofr_p99_iorb_sd15_bps"] is None for b in built[:14]))
        window = [(r.values["sofr_p99"] - 1.5) * 100.0 for r in rows[5:20]]
        self.assertAlmostEqual(built[19].values["sofr_p99_iorb_sd15_bps"], statistics.stdev(window))

    def test_a_missing_value_in_the_window_leaves_the_sd_missing(self):
        days = weekdays(date(2024, 1, 1), 20)
        rows = [row(day, sofr_p99=None if i == 10 else 1.5 + 0.01 * i) for i, day in enumerate(days)]
        built = measurement_fields.build_columns(rows)
        self.assertIsNone(built[10].values["sofr_p99_iorb_bps"])
        self.assertIsNone(built[19].values["sofr_p99_iorb_sd15_bps"])  # window rows 5..19 holds 10
        self.assertIsNotNone(
            measurement_fields.build_columns([r for r in rows])[-1].values["sofr_p99_iorb_bps"]
        )

    def test_the_tga_change_and_its_product_with_reserves(self):
        days = weekdays(date(2024, 1, 1), 3)
        rows = [
            row(days[0], tga_daily=100.0, reserve_balances=3000.0),
            row(days[1], tga_daily=130.0, reserve_balances=3000.0),
            row(days[2], tga_daily=120.0, reserve_balances=2500.0),
        ]
        built = measurement_fields.build_columns(rows)
        self.assertIsNone(built[0].values["tga_daily_change"])
        self.assertEqual(built[1].values["tga_daily_change"], 30.0)
        self.assertEqual(built[1].values["tga_change_x_reserves"], 90.0)
        self.assertEqual(built[2].values["tga_daily_change"], -10.0)
        self.assertEqual(built[2].values["tga_change_x_reserves"], -25.0)

    def test_a_missing_balance_or_reserve_leaves_the_product_missing(self):
        days = weekdays(date(2024, 1, 1), 4)
        built = measurement_fields.build_columns(
            [
                row(days[0], tga_daily=100.0, reserve_balances=3000.0),
                row(days[1], tga_daily=None, reserve_balances=3000.0),
                row(days[2], tga_daily=120.0, reserve_balances=None),
                row(days[3], tga_daily=125.0, reserve_balances=3000.0),
            ]
        )
        self.assertIsNone(built[1].values["tga_daily_change"])
        self.assertIsNone(built[2].values["tga_daily_change"])  # the day before is missing
        self.assertIsNone(built[2].values["tga_change_x_reserves"])
        self.assertEqual(built[3].values["tga_daily_change"], 5.0)
        self.assertEqual(built[3].values["tga_change_x_reserves"], 15.0)

    def test_a_row_never_depends_on_a_later_one(self):
        days = weekdays(date(2024, 1, 1), 40)
        rows = [
            row(day, sofr_p99=1.5 + 0.013 * (i % 7), tga_daily=100.0 + (i * 17) % 23, reserve_balances=3000.0 - i)
            for i, day in enumerate(days)
        ]
        full = measurement_fields.build_columns(rows)
        for cut in (16, 25, 40):
            partial = measurement_fields.build_columns(rows[:cut])
            for ours, theirs in zip(partial, full):
                self.assertEqual(ours.values, theirs.values)


class CarryTests(unittest.TestCase):
    def rows(self, values):
        return [
            DailyObservation(day, {"sofr_p99": value})
            for day, value in zip(weekdays(date(2024, 1, 1), len(values)), values)
        ]

    def test_a_single_hole_takes_the_earlier_value_and_is_listed(self):
        filled, carried = measurement_fields.carry_one_row_holes(self.rows([1.0, None, 3.0]), ["sofr_p99"])
        self.assertEqual([r.values["sofr_p99"] for r in filled], [1.0, 1.0, 3.0])
        self.assertEqual(carried, ["2024-01-02:sofr_p99"])

    def test_a_longer_run_and_the_ends_are_left(self):
        filled, carried = measurement_fields.carry_one_row_holes(
            self.rows([None, 1.0, None, None, 2.0, None]), ["sofr_p99"]
        )
        self.assertEqual([r.values["sofr_p99"] for r in filled], [None, 1.0, None, None, 2.0, None])
        self.assertEqual(carried, [])


class OffInEveryDeclarationTests(unittest.TestCase):
    def test_no_published_feature_map_carries_a_measurement_column(self):
        for column in measurement_fields.COLUMN_FIELDS:
            if column in early_warning.COLUMN_FIELDS and column not in contract.FEATURE_FIELDS:
                continue
            self.assertNotIn(column, contract.FEATURE_FIELDS, column)

    def test_every_column_names_registered_fields(self):
        for column, pairs in measurement_fields.COLUMN_FIELDS.items():
            for source, field in pairs:
                self.assertIn(source, REGISTRY, column)
                self.assertIn(field, REGISTRY[source]["fields"], f"{column}: {source}.{field}")

    def test_the_new_source_is_declared_unmodelled(self):
        self.assertIn("treasury_dts_tga", contract.UNMODELLED_SOURCES)


def switched_on():
    fields = dict(measurement_fields.COLUMN_FIELDS)
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
    """The daily TGA is read after its statement is published, not on the day it describes (#377).

    The statement for a business day is declared available at 16:30 New York time on the next
    business day (`treasury_dts_tga.release_lag`). A forecast made at the 16:00 decision of
    Wednesday 2026-01-21 therefore cannot read Tuesday the 20th's balance (public at 16:30 that
    day), and reads Friday the 16th's, public at 16:30 on Tuesday the 20th (Monday the 19th is a
    market holiday).

    Recorded mutation (CLAUDE.md), 8 October 2026, in a disposable copy:
    `metadata/sources.json`, `treasury_dts_tga.release_lag`, `"days": 1` mutated to `"days": 0`
    (a balance public at 16:30 on its own date). `test_a_balance_published_after_the_decision_is_invisible`
    then fails with `AssertionError` (`datetime.date(2026, 1, 20) != datetime.date(2026, 1, 16)`):
    the forecast reads the balance of the day before its decision, public only afterwards.
    """

    DATES = [d for d in weekdays(date(2026, 1, 5), 40) if d != date(2026, 1, 19)]
    DECISION = time(16, 0)

    def rows(self):
        return [
            DailyObservation(
                day,
                {
                    "spread_bps": 1.0,
                    "tga_daily": 500.0 + i,
                    "tga_daily_change": 1.0,
                    "reserve_balances": 3000.0,
                    "tga_change_x_reserves": 3.0,
                },
            )
            for i, day in enumerate(self.DATES)
        ]

    def rule(self, features):
        return InformationRule(REGISTRY, tuple(features), decision_time=self.DECISION)

    def test_a_balance_published_after_the_decision_is_invisible(self):
        with switched_on():
            information = self.rule(["spread_bps", "tga_daily"])
            scored = self.DATES.index(date(2026, 1, 22))
            info = information.information_set(self.DATES, scored)
            (read,) = [r for r in info.reads if r.feature == "tga_daily"]
            self.assertEqual(self.DATES[read.row], date(2026, 1, 16))
            self.assertEqual(read.available_at, datetime(2026, 1, 20, 16, 30))
            tuesday = self.DATES.index(date(2026, 1, 20))
            self.assertGreater(
                information.availability(self.DATES, read.fields, tuesday), info.decision_instant
            )
            forced = info._replace(
                reads=tuple(r._replace(row=tuesday) if r.feature == "tga_daily" else r for r in info.reads)
            )
            with self.assertRaises(LookAheadError):
                information.check(self.DATES, forced)

    def test_every_measurement_column_passes_both_guards(self):
        with switched_on():
            information = self.rule(["spread_bps", *measurement_fields.COLUMN_FIELDS])
            for scored in range(15, len(self.DATES)):
                information.check(self.DATES, information.information_set(self.DATES, scored))

    def test_a_product_waits_for_its_slowest_field(self):
        with switched_on():
            information = self.rule(["spread_bps", "tga_daily", "tga_change_x_reserves"])
            scored = self.DATES.index(date(2026, 1, 30))
            info = information.information_set(self.DATES, scored)
            tga = [r for r in info.reads if r.feature == "tga_daily"][0]
            product = [r for r in info.reads if r.feature == "tga_change_x_reserves"][0]
            self.assertLessEqual(product.row, tga.row)


if __name__ == "__main__":
    unittest.main()
