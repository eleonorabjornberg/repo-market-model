import hashlib
from dataclasses import replace
from datetime import date, datetime, time, timedelta, timezone
import gzip
import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from repo_model.data import load_point_in_time_panel
from repo_model.ingest import (
    ArchiveRecord,
    SnapshotArtifact,
    _decode_transport,
    _sec_nmfp_rows,
    fetch_sec_nmfp_archives,
    load_sec_nmfp_archive_manifest,
    nmfp_schema_refusals,
    write_sec_nmfp_archive_manifest,
    build_point_in_time_snapshot,
    parse_snapshots,
    fetch_fred_macro,
    fetch_nyfed_reference_rate,
    fetch_sec_nmfp,
    fetch_treasury_auctions,
    load_snapshot_manifest,
    observations_from_snapshots,
)
from zoneinfo import ZoneInfo


REPO_ROOT = Path(__file__).parents[1]
SOURCE_REGISTRY = REPO_ROOT / "metadata" / "sources.json"


def registry_with_nmfp_coverage_floor(directory: Path, floor: int) -> Path:
    """The real registry with only `sec_nmfp`'s declared coverage floor changed.

    A fixture cross-section is a handful of rows, so exercising the production
    floor of 200 reporting series would mean fabricating a universe before any
    assertion could be made. Overriding the single number keeps every other
    declaration -- `entity_unit` above all -- exactly the shape the adapter reads
    in production, so a registry that drifts still breaks these tests.
    """

    registry = json.loads(SOURCE_REGISTRY.read_text(encoding="utf-8"))
    registry["sec_nmfp"]["cross_section"]["minimum_reporting_entities"] = floor
    path = directory / "sources.json"
    path.write_text(json.dumps(registry, indent=2, sort_keys=True), encoding="utf-8")
    return path


def nmfp_archive(submissions) -> bytes:
    """Build a minimal but structurally faithful Form N-MFP flat-file ZIP.

    `submissions` is a sequence of dicts with `accession`, `series`, `report`
    and optional `net_assets` (USD, not billions), `filing` (the DD-MON-YYYY
    filing date, defaulting to the report date), `submission_type` (defaulting
    to `N-MFP3`) and `flows`, a sequence of
    `(flow_date, subscriptions, redemptions)`. The tables carry the same column
    names and the same DD-MON-YYYY dates as the SEC extract, so a fixture cannot
    pass by agreeing with the parser about a format the source does not use.
    """

    submission_rows = [
        "ACCESSION_NUMBER\tFILING_DATE\tSUBMISSIONTYPE\tSERIESID\tREPORTDATE"
    ]
    series_rows = [
        "ACCESSION_NUMBER\tCASH\tTOTALVALUEPORTFOLIOSECURITIES\t"
        "TOTALVALUEOTHERASSETS\tTOTALVALUELIABILITIES\tNETASSETOFSERIES"
    ]
    flow_rows = [
        "ACCESSION_NUMBER\tDAILYGROSSSUBSCRIPTIONS\tDAILYGROSSREDEMPTIONS\t"
        "DAILYSHAREHOLDERFLOWDATE"
    ]
    holding_rows = [
        "ACCESSION_NUMBER\tINVESTMENTCATEGORY\tINCLUDINGVALUEOFANYSPONSORSUPP\t"
        "NAMEOFISSUER\tTITLEOFISSUER\tBRIEFDESCRIPTION"
    ]
    for entry in submissions:
        submission_rows.append(
            f"{entry['accession']}\t{entry.get('filing', entry['report'])}\t"
            f"{entry.get('submission_type', 'N-MFP3')}\t"
            f"{entry['series']}\t{entry['report']}"
        )
        net = entry.get("net_assets", 1_000_000_000)
        # cash + portfolio + other == liabilities + net assets, to the dollar.
        series_rows.append(f"{entry['accession']}\t0\t{net}\t0\t0\t{net}")
        for flow_date, subscriptions, redemptions in entry.get("flows", ()):
            flow_rows.append(
                f"{entry['accession']}\t{subscriptions}\t{redemptions}\t{flow_date}"
            )
        # Every holdings series is populated for every filer, so that any
        # missingness the quality report shows can only come from the coverage
        # floor and not from a series the fixture never supplied.
        holding_rows.append(
            f"{entry['accession']}\tU.S. Treasury Debt\t{net // 2}\t"
            "United States Treasury\tBill\t"
        )
        holding_rows.append(
            f"{entry['accession']}\tU.S. Treasury Repurchase Agreement\t{net // 4}\t"
            "Federal Reserve Bank of New York\tReverse repo\t"
        )

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("NMFP_SUBMISSION.tsv", "\n".join(submission_rows) + "\n")
        archive.writestr("NMFP_SERIESLEVELINFO.tsv", "\n".join(series_rows) + "\n")
        archive.writestr(
            "NMFP_DLYSHAREHOLDERFLOWREPORT.tsv", "\n".join(flow_rows) + "\n"
        )
        archive.writestr(
            "NMFP_SCHPORTFOLIOSECURITIES.tsv", "\n".join(holding_rows) + "\n"
        )
    return buffer.getvalue()


class IngestTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.output_root = Path(self.directory.name)

    def test_nyfed_snapshots_are_checksummed(self):
        payloads = {
            "rate": b'{"refRates":[{"effectiveDate":"2026-01-02","percentRate":4.31}]}',
            "volume": b'{"refRates":[{"effectiveDate":"2026-01-02","volumeInBillions":2000}]}',
        }

        def downloader(url: str) -> bytes:
            return payloads["volume" if "type=volume" in url else "rate"]

        artifacts = fetch_nyfed_reference_rate(
            self.output_root, "sofr", "2026-01-01", "2026-01-03", downloader
        )
        self.assertEqual(len(artifacts), 2)
        for artifact in artifacts:
            self.assertTrue(artifact.path.exists())
            self.assertEqual(hashlib.sha256(artifact.path.read_bytes()).hexdigest(), artifact.sha256)
            manifest = json.loads(
                artifact.path.with_suffix(artifact.path.suffix + ".manifest.json").read_text()
            )
            self.assertEqual(manifest["sha256"], artifact.sha256)
            restored = load_snapshot_manifest(
                artifact.path.with_suffix(artifact.path.suffix + ".manifest.json")
            )
            self.assertEqual(restored, artifact)

    def test_fred_rejects_non_csv_response(self):
        with self.assertRaisesRegex(ValueError, "expected CSV"):
            fetch_fred_macro(self.output_root, lambda _: b"not,data\n")

    def test_fred_accepts_and_preserves_zip_snapshot(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("fredgraph.csv", "observation_date,IORB\n2026-01-01,4.30\n")
        artifacts = fetch_fred_macro(self.output_root, lambda _: buffer.getvalue())
        self.assertEqual(artifacts[0].path.suffix, ".zip")
        self.assertEqual(artifacts[0].path.read_bytes(), buffer.getvalue())

    def test_download_decodes_gzip_by_magic_bytes(self):
        payload = b"observation_date,IORB\n2026-01-01,4.30\n"
        self.assertEqual(_decode_transport(gzip.compress(payload)), payload)

    def test_treasury_adapter_validates_and_preserves_json(self):
        payload = b'{"data":[{"issue_date":"2026-01-05"}]}'
        artifacts = fetch_treasury_auctions(
            self.output_root,
            "2026-01-01",
            "2026-01-31",
            lambda url: payload,
        )
        self.assertEqual(artifacts[0].source_id, "treasury_auctions")
        self.assertEqual(artifacts[0].path.read_bytes(), payload)

    def test_sec_adapter_requires_an_official_flat_file_zip(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("FUND.tsv", "ACCESSION_NUMBER\tTOTAL_ASSETS\n")
        artifacts = fetch_sec_nmfp(
            self.output_root,
            "https://www.sec.gov/files/dera/data/form-n-mfp-data-sets/2026-01.zip",
            lambda url: buffer.getvalue(),
        )
        self.assertEqual(artifacts[0].source_id, "sec_nmfp")

    def test_sec_live_download_requires_a_contact_identity(self):
        with self.assertRaisesRegex(ValueError, "contact_email"):
            fetch_sec_nmfp(
                self.output_root,
                "https://www.sec.gov/files/dera/data/form-n-mfp-data-sets/example.zip",
            )

    def test_first_point_in_time_snapshot_combines_nyfed_and_fred(self):
        nyfed_payload = (
            b'{"refRates":[{"effectiveDate":"2026-01-02",'
            b'"percentRate":4.31,"percentPercentile1":"NA",'
            b'"percentPercentile25":4.30}]}'
        )
        nyfed = fetch_nyfed_reference_rate(
            self.output_root, "sofr", "2026-01-01", "2026-01-03",
            lambda url: (
                b'{"refRates":[{"effectiveDate":"2026-01-02",'
                b'"volumeInBillions":2000}]}'
                if "type=volume" in url else nyfed_payload
            ),
        )
        fred = fetch_fred_macro(
            self.output_root,
            lambda url: b"observation_date,IORB\n2026-01-02,4.30\n",
        )
        panel_path = self.output_root / "processed" / "panel.csv"
        panel = build_point_in_time_snapshot(
            [*nyfed, *fred],
            panel_path,
            created_at=datetime(2026, 1, 6, tzinfo=timezone.utc),
        )
        rows = load_point_in_time_panel(panel_path)
        self.assertEqual(
            {row.series_id for row in rows},
            {"SOFR", "SOFR_p25", "SOFR_volume", "IORB"},
        )
        self.assertEqual(panel.row_count, 4)
        manifest = json.loads(
            panel_path.with_suffix(".csv.manifest.json").read_text()
        )
        self.assertEqual(manifest["sha256"], hashlib.sha256(panel_path.read_bytes()).hexdigest())
        quality_path = Path(manifest["quality_report_path"])
        self.assertTrue(quality_path.exists())
        self.assertEqual(
            manifest["quality_report_sha256"],
            hashlib.sha256(quality_path.read_bytes()).hexdigest(),
        )
        self.assertEqual(json.loads(quality_path.read_text())["rows"], 4)

    def test_legacy_snapshot_source_ids_remain_parseable(self):
        nyfed = fetch_nyfed_reference_rate(
            self.output_root,
            "sofr",
            "2026-01-01",
            "2026-01-03",
            lambda url: (
                b'{"refRates":[{"effectiveDate":"2026-01-02",'
                b'"volumeInBillions":2000}]}'
                if "type=volume" in url
                else b'{"refRates":[{"effectiveDate":"2026-01-02",'
                b'"percentRate":4.31}]}'
            ),
        )
        fred = fetch_fred_macro(
            self.output_root,
            lambda url: b"observation_date,IORB\n2026-01-02,4.30\n",
        )
        legacy = [
            replace(
                artifact,
                source_id=(
                    "nyfed-sofr-volume"
                    if "type=volume" in artifact.url
                    else "nyfed-sofr-rate"
                ),
            )
            for artifact in nyfed
        ] + [replace(fred[0], source_id="fred-macro-latest-vintage")]

        rows = observations_from_snapshots(legacy)

        self.assertEqual(
            {row.series_id for row in rows},
            {"SOFR", "SOFR_volume", "IORB"},
        )

    def test_panel_builder_rejects_a_tampered_raw_snapshot(self):
        artifacts = fetch_fred_macro(
            self.output_root,
            lambda url: b"observation_date,IORB\n2026-01-02,4.30\n",
        )
        artifacts[0].path.write_bytes(b"tampered")
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            build_point_in_time_snapshot(artifacts, self.output_root / "panel.csv")

    def test_treasury_panel_rows_aggregate_settlements_in_billions(self):
        payload = json.dumps(
            {
                "data": [
                    {
                        "issue_date": "2026-01-15",
                        "record_date": "2026-01-10",
                        "offering_amt": "50000000000",
                    },
                    {
                        "issue_date": "2026-01-15",
                        "record_date": "2026-01-10",
                        "offering_amt": "25000000000",
                    },
                ]
            }
        ).encode()
        artifacts = fetch_treasury_auctions(
            self.output_root, "2026-01-01", "2026-01-31", lambda url: payload
        )
        panel_path = self.output_root / "treasury.csv"
        build_point_in_time_snapshot(artifacts, panel_path)
        rows = load_point_in_time_panel(panel_path)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].series_id, "treasury_settlement")
        self.assertEqual(rows[0].value, 75.0)
        self.assertLess(rows[0].available_at.date(), rows[0].ref_date)

    def test_changed_snapshot_appends_revision_but_unchanged_value_does_not(self):
        first = fetch_fred_macro(
            self.output_root,
            lambda url: b"observation_date,IORB\n2026-01-02,4.30\n",
        )[0]
        unchanged = fetch_fred_macro(
            self.output_root,
            lambda url: b"observation_date,IORB\n2026-01-02,4.30\n",
        )[0]
        revised = fetch_fred_macro(
            self.output_root,
            lambda url: b"observation_date,IORB\n2026-01-02,4.31\n",
        )[0]
        panel_path = self.output_root / "revisions.csv"
        build_point_in_time_snapshot([first, unchanged, revised], panel_path)
        rows = load_point_in_time_panel(panel_path)
        self.assertEqual([row.value for row in rows], [4.30, 4.31])
        self.assertLess(rows[0].available_at, rows[1].available_at)

    def test_nmfp_snapshot_builds_aggregate_balances_flows_and_holdings(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr(
                "NMFP_SUBMISSION.tsv",
                "ACCESSION_NUMBER\tFILING_DATE\tSUBMISSIONTYPE\tSERIESID\t"
                "REPORTDATE\nA1\t07-AUG-2026\tN-MFP3\tS1\t31-JUL-2026\n",
            )
            archive.writestr(
                "NMFP_SERIESLEVELINFO.tsv",
                "ACCESSION_NUMBER\tCASH\tTOTALVALUEPORTFOLIOSECURITIES\t"
                "TOTALVALUEOTHERASSETS\tTOTALVALUELIABILITIES\tNETASSETOFSERIES\n"
                "A1\t1000000000\t4000000000\t1000000000\t1000000000\t5000000000\n",
            )
            archive.writestr(
                "NMFP_DLYSHAREHOLDERFLOWREPORT.tsv",
                "ACCESSION_NUMBER\tDAILYGROSSSUBSCRIPTIONS\tDAILYGROSSREDEMPTIONS\t"
                "DAILYSHAREHOLDERFLOWDATE\nA1\t300000000\t100000000\t31-JUL-2026\n",
            )
            archive.writestr(
                "NMFP_SCHPORTFOLIOSECURITIES.tsv",
                "ACCESSION_NUMBER\tINVESTMENTCATEGORY\tINCLUDINGVALUEOFANYSPONSORSUPP\t"
                "NAMEOFISSUER\tTITLEOFISSUER\tBRIEFDESCRIPTION\n"
                "A1\tU.S. Treasury Debt\t500000000\tTreasury\tBill\t\n"
                "A1\tU.S. Treasury Repurchase Agreement, if collateralized only by U.S. "
                "Treasuries (including Strips) and cash\t200000000\tFederal Reserve Bank "
                "of New York\tReverse repo\t\n",
            )
        artifact = fetch_sec_nmfp(
            self.output_root,
            "https://www.sec.gov/files/dera/data/form-n-mfp-data-sets/test.zip",
            lambda url: buffer.getvalue(),
        )[0]
        panel_path = self.output_root / "nmfp.csv"
        # One filer is below the production coverage floor, and rightly so. This
        # test is about the arithmetic of the aggregation, so it declares a floor
        # its own cross-section meets; the floor itself is exercised in
        # CrossSectionCoverageTests.
        build_point_in_time_snapshot(
            [artifact],
            panel_path,
            registry_path=registry_with_nmfp_coverage_floor(self.output_root, 1),
        )
        values = {row.series_id: row.value for row in load_point_in_time_panel(panel_path)}
        self.assertEqual(values["mmf_net_assets"], 5.0)
        self.assertEqual(values["mmf_net_flow"], 0.2)
        self.assertEqual(values["mmf_treasury_holdings"], 0.5)
        self.assertEqual(values["mmf_repo_holdings"], 0.2)
        self.assertEqual(values["mmf_on_rrp"], 0.2)



class NMFPSchemaGuardTests(unittest.TestCase):
    """The N-MFP parser must fail closed when a required column drifts.

    Mutation record
    ---------------
    Run in a disposable copy with the full 401-test suite, `-B`, and
    `PYTHONDONTWRITEBYTECODE=1`; the unmutated control was OK.

    | Mutation                                             | Result    |
    |------------------------------------------------------|-----------|
    | Disable the required-header comparison.              | 1 failure |
    | Require only `ACCESSION_NUMBER` in the series table. | 1 failure |

    In both cases this class's acceptance test was the failure: the renamed
    balance columns reached the parser without raising `ValueError`.
    """

    def setUp(self):
        self.artifact = SnapshotArtifact(
            source_id="sec_nmfp",
            url="https://www.sec.gov/files/dera/data/form-n-mfp-data-sets/fixture.zip",
            path=Path("unused.zip"),
            retrieved_at="2026-08-01T00:00:00+00:00",
            sha256="0" * 64,
            byte_count=1,
        )

    def test_renamed_series_balance_columns_are_rejected_before_parsing(self):
        source = nmfp_archive(
            (
                {
                    "accession": "A1",
                    "series": "S1",
                    "report": "31-JUL-2026",
                },
            )
        )
        rewritten = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(source)) as original:
            with zipfile.ZipFile(rewritten, "w") as archive:
                for name in original.namelist():
                    payload = original.read(name)
                    if name == "NMFP_SERIESLEVELINFO.tsv":
                        text = payload.decode("utf-8")
                        header, rows = text.split("\n", 1)
                        for column in (
                            "CASH",
                            "TOTALVALUEPORTFOLIOSECURITIES",
                            "TOTALVALUEOTHERASSETS",
                            "TOTALVALUELIABILITIES",
                            "NETASSETOFSERIES",
                        ):
                            header = header.replace(column, f"{column}_RENAMED")
                        payload = f"{header}\n{rows}".encode("utf-8")
                    archive.writestr(name, payload)

        with self.assertRaisesRegex(
            ValueError,
            r"NMFP_SERIESLEVELINFO\.tsv lacks required columns "
            r"CASH, NETASSETOFSERIES, TOTALVALUELIABILITIES, "
            r"TOTALVALUEOTHERASSETS, TOTALVALUEPORTFOLIOSECURITIES$",
        ):
            _sec_nmfp_rows(self.artifact, rewritten.getvalue())


class ArchiveManifestTests(unittest.TestCase):
    """The declared archive set, and the fetch that reads it.

    `data/raw/` is gitignored, so the bytes that make up `sec_nmfp` are not in
    the repository and a fresh checkout has no way to know how much history is
    supposed to exist. The manifest is that record. It also has to distinguish
    three states that all look like an absent file: never declared, declared but
    not fetched here, and fetched and refused.
    """

    SEC_URL = "https://www.sec.gov/files/dera/data/form-n-mfp-data-sets/"

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.output_root = Path(self.directory.name)
        self.readable = nmfp_archive(
            (
                {
                    "accession": "0000000000-26-000001",
                    "series": "S000000001",
                    "report": "31-JUL-2026",
                },
            )
        )
        # The same archive with one required table removed -- the shape every
        # Form N-MFP set published before the daily shareholder-flow report
        # existed actually has.
        stripped = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(self.readable)) as original:
            with zipfile.ZipFile(stripped, "w") as archive:
                for name in original.namelist():
                    if name == "NMFP_DLYSHAREHOLDERFLOWREPORT.tsv":
                        continue
                    archive.writestr(name, original.read(name))
        self.unreadable = stripped.getvalue()

    def _serve(self, payloads):
        calls = []

        def downloader(url):
            calls.append(url)
            return payloads[url]

        return downloader, calls

    def test_an_archive_the_parser_cannot_read_never_reaches_the_raw_tree(self):
        url = f"{self.SEC_URL}old.zip"
        downloader, calls = self._serve({url: self.unreadable})
        updated = fetch_sec_nmfp_archives(
            self.output_root,
            [ArchiveRecord(url=url)],
            downloader=downloader,
            pause_seconds=0,
        )
        self.assertEqual(calls, [url])
        self.assertEqual(
            updated[0].refusals,
            ("lacks required table NMFP_DLYSHAREHOLDERFLOWREPORT.tsv",),
        )
        self.assertFalse(updated[0].admitted)
        # Everything under data/raw/ is panel input by construction. An archive
        # the parser refuses is not panel input, so it is recorded and not
        # written: leaving it there and filtering later is the same claim made
        # in a place nothing reads.
        self.assertEqual(list((self.output_root / "sec_nmfp").glob("*.zip")), [])
        self.assertNotEqual(updated[0].sha256, "")

    def test_a_recorded_archive_is_not_downloaded_twice(self):
        readable_url = f"{self.SEC_URL}new.zip"
        refused_url = f"{self.SEC_URL}old.zip"
        payloads = {readable_url: self.readable, refused_url: self.unreadable}
        downloader, calls = self._serve(payloads)
        records = [ArchiveRecord(url=readable_url), ArchiveRecord(url=refused_url)]
        first = fetch_sec_nmfp_archives(
            self.output_root, records, downloader=downloader, pause_seconds=0
        )
        self.assertCountEqual(calls, [readable_url, refused_url])
        self.assertTrue(first[0].admitted)
        self.assertFalse(first[1].admitted)

        # Re-running fetches nothing: the readable archive is already on disk
        # under its recorded digest, and the refused one has a verdict already
        # written down. Re-downloading a hundred archives to re-derive a recorded
        # refusal is not politeness.
        again_downloader, again_calls = self._serve(payloads)
        second = fetch_sec_nmfp_archives(
            self.output_root, first, downloader=again_downloader, pause_seconds=0
        )
        self.assertEqual(again_calls, [])
        self.assertEqual(second, first)
        self.assertEqual(
            len(list((self.output_root / "sec_nmfp").glob("*.zip"))), 1
        )

        # recheck re-earns both verdicts against the bytes.
        recheck_downloader, recheck_calls = self._serve(payloads)
        fetch_sec_nmfp_archives(
            self.output_root,
            first,
            downloader=recheck_downloader,
            recheck=True,
            pause_seconds=0,
        )
        self.assertCountEqual(recheck_calls, [readable_url, refused_url])

    def test_a_changed_digest_is_a_changed_source_and_raises(self):
        url = f"{self.SEC_URL}new.zip"
        downloader, _calls = self._serve({url: self.readable})
        record = ArchiveRecord(url=url, sha256="0" * 64, byte_count=1)
        with self.assertRaisesRegex(ValueError, r"no longer matches its recorded digest"):
            fetch_sec_nmfp_archives(
                self.output_root, [record], downloader=downloader, pause_seconds=0
            )

    def test_the_manifest_round_trips_and_rejects_an_empty_declaration(self):
        path = self.output_root / "archives.json"
        records = (
            ArchiveRecord(
                url=f"{self.SEC_URL}b.zip",
                sha256="b" * 64,
                byte_count=2,
                first_retrieved_at="2026-09-07T00:00:00+00:00",
            ),
            ArchiveRecord(
                url=f"{self.SEC_URL}a.zip",
                sha256="a" * 64,
                byte_count=1,
                first_retrieved_at="2026-09-07T00:00:00+00:00",
                refusals=("lacks required table NMFP_DLYSHAREHOLDERFLOWREPORT.tsv",),
            ),
        )
        write_sec_nmfp_archive_manifest(records, path)
        loaded = load_sec_nmfp_archive_manifest(path)
        self.assertEqual([item.url for item in loaded], sorted(item.url for item in records))
        self.assertEqual([item.admitted for item in loaded], [False, True])

        # A declared set of nothing is not a source with no history; it is a
        # source nobody has described, and must not read as the former.
        empty = self.output_root / "empty.json"
        empty.write_text(json.dumps({"archives": []}), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, r"declares no archives"):
            load_sec_nmfp_archive_manifest(empty)

    def test_the_committed_manifest_describes_the_declared_history(self):
        records = load_sec_nmfp_archive_manifest()
        self.assertTrue(
            all(record.url.startswith("https://www.sec.gov/") for record in records)
        )
        # Every entry has been fetched at least once, so no entry is in the
        # "declared but never looked at" state that would make its refusal list
        # meaningless.
        self.assertEqual([r.url for r in records if not r.sha256], [])
        admitted = [record for record in records if record.admitted]
        self.assertGreater(
            len(admitted),
            0,
            "the declared archive set admits nothing, so the source has no history",
        )
        refused = [record for record in records if record.refusals]
        self.assertGreater(
            len(refused),
            0,
            "no declared archive is refused, so this record is not distinguishing "
            "the schema eras the backfill found",
        )

    def test_the_refusal_report_names_every_problem_not_just_the_first(self):
        rewritten = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(self.readable)) as original:
            with zipfile.ZipFile(rewritten, "w") as archive:
                for name in original.namelist():
                    if name == "NMFP_DLYSHAREHOLDERFLOWREPORT.tsv":
                        continue
                    payload = original.read(name)
                    if name == "NMFP_SUBMISSION.tsv":
                        header, rows = payload.decode("utf-8").split("\n", 1)
                        payload = f"{header.replace('FILING_DATE', 'FILED')}\n{rows}".encode()
                    archive.writestr(name, payload)
        # `_nmfp_table` stops at the first problem, which is right for a parse.
        # A verdict recorded in the manifest has to name all of them: an archive
        # from a schema nobody here has seen should be describable in one pass.
        self.assertEqual(
            nmfp_schema_refusals(rewritten.getvalue()),
            (
                "lacks required table NMFP_DLYSHAREHOLDERFLOWREPORT.tsv",
                "NMFP_SUBMISSION.tsv lacks required columns FILING_DATE",
            ),
        )

    def test_a_response_that_is_not_a_zip_is_refused_rather_than_crashing(self):
        self.assertEqual(
            nmfp_schema_refusals(b"<html>rate limited</html>"),
            ("not a valid ZIP archive",),
        )


class OverlappingArchiveTests(unittest.TestCase):
    """Two archives carrying one report date must not double count it.

    `_sec_nmfp_rows` adds every accession's values together, which is what
    aggregating a cross-section means -- across series. Across a series and its
    own amendment it is a double count: `N-MFP3/A` is a second accession
    restating the first, and the restated balance sheet gets booked on top of the
    one it replaces. On a single archive this never happened, because a bulk
    extract covers a filing window and an amendment falls in a later window than
    its original. Backfilling makes overlap the normal case: a quarterly set and
    the monthly sets after it carry the same report month, and stragglers and
    amendments arrive in adjacent archives.

    The composition of the two mechanisms is what is under test here. Within an
    archive, `_resolve_nmfp_submissions` keeps the latest filing per (series,
    report date). Across archives, the revision logic in `parse_snapshots`
    appends a changed value as a new vintage rather than adding it. Neither half
    is sufficient alone and neither had ever been exercised.

    Mutation record
    ---------------
    Filled in below after the mutation run.
    """

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.output_root = Path(self.directory.name)
        # Three series file for one report month. The floor is set to their
        # count, so both cross-sections are admitted and the test is about
        # arithmetic rather than about coverage.
        self.registry_path = registry_with_nmfp_coverage_floor(self.output_root, 3)

    #: Three series file for one report month.
    #:
    #: `S000000001` files once and is the control.
    #: `S000000002` is amended in the later archive, a month after the fact --
    #:   the ordinary case, and the one that decides original versus amendment.
    #: `S000000003` files twice on the same day, so filing date cannot separate
    #:   them and the accession tie-break is the only thing that does. Without it
    #:   the winner is whichever row the archive happened to list first.
    ORIGINALS = (
        ("0000000000-23-000001", "S000000001", "10-FEB-2023", "N-MFP3", 1),
        ("0000000000-23-000002", "S000000002", "10-FEB-2023", "N-MFP3", 2),
        ("0000000000-23-000003", "S000000003", "10-FEB-2023", "N-MFP3", 3),
        ("0000000000-23-000009", "S000000003", "10-FEB-2023", "N-MFP3", 30),
    )
    #: Filed a month later, restating `S000000002` tenfold.
    AMENDMENT = ("0000000000-23-000099", "S000000002", "15-MAR-2023", "N-MFP3/A", 20)

    @staticmethod
    def _submissions(entries):
        return [
            {
                "accession": accession,
                "series": series,
                "report": "31-JAN-2023",
                "filing": filing,
                "submission_type": submission_type,
                "net_assets": billions * 1_000_000_000,
            }
            for accession, series, filing, submission_type, billions in entries
        ]

    def _archive(self, name, entries, retrieved_at):
        artifact = fetch_sec_nmfp(
            self.output_root / name,
            f"https://www.sec.gov/files/dera/data/form-n-mfp-data-sets/{name}.zip",
            lambda url: nmfp_archive(self._submissions(entries)),
        )[0]
        # Retrieval order is what orders vintages, and two fetches in one test run
        # are microseconds apart. Declaring the timestamps keeps the assertion
        # about the adapter rather than about clock resolution.
        return replace(artifact, retrieved_at=retrieved_at)

    @staticmethod
    def _latest_vintages(rows):
        latest = {}
        for row in rows:
            key = (row.series_id, row.ref_date)
            previous = latest.get(key)
            if previous is None or row.available_at > previous.available_at:
                latest[key] = row
        return latest

    def test_overlapping_archives_do_not_double_count_a_report_date(self):
        quarterly = self._archive(
            "quarterly", self.ORIGINALS, "2026-03-01T00:00:00+00:00"
        )
        monthly = self._archive(
            "monthly",
            self.ORIGINALS + (self.AMENDMENT,),
            "2026-04-01T00:00:00+00:00",
        )

        parsed = parse_snapshots(
            [quarterly, monthly], registry_path=self.registry_path
        )
        ref_date = date(2023, 1, 31)
        rows = [row for row in parsed.rows if row.ref_date == ref_date]

        # No series is observed twice with one availability timestamp. A sum
        # across archives is otherwise indistinguishable from a single value.
        stamped = [(row.series_id, row.available_at) for row in rows]
        self.assertCountEqual(stamped, set(stamped))

        latest = self._latest_vintages(rows)
        net_assets = latest[("mmf_net_assets", ref_date)]
        # 1 + 20 + 30. Every wrong rule lands somewhere else and is named here so
        # a future reader can tell which one broke:
        #   56.0  no supersession -- every accession added
        #    6.0  earliest filing wins -- the amendment discarded
        #   24.0  no accession tie-break -- S000000003's first-listed row wins
        self.assertEqual(net_assets.value, 51.0)
        monthly_available = datetime(2026, 4, 1, tzinfo=timezone.utc)
        self.assertEqual(net_assets.available_at, monthly_available)
        self.assertEqual(net_assets.vintage_id, "2026-04-01T00:00:00+00:00")

        # The earlier archive stays in the panel as the earlier vintage, so the
        # correction is attributable rather than silent. 1 + 2 + 30.
        first = min(
            (row for row in rows if row.series_id == "mmf_net_assets"),
            key=lambda row: row.available_at,
        )
        self.assertEqual(first.value, 33.0)
        self.assertEqual(first.available_at, datetime(2026, 3, 1, tzinfo=timezone.utc))
        self.assertLess(first.available_at, monthly_available)

        # Every derived series resolves the same way, not just the balance-sheet
        # total: the fixture gives each filer treasuries of half its net assets
        # and a Federal Reserve repo of a quarter.
        self.assertEqual(latest[("mmf_treasury_holdings", ref_date)].value, 25.5)
        self.assertEqual(latest[("mmf_repo_holdings", ref_date)].value, 12.75)
        self.assertEqual(latest[("mmf_on_rrp", ref_date)].value, 12.75)

        # Superseded submissions leave the values but stay in the corroborating
        # record: three reporting series either way, four submissions then five.
        coverage = [item for item in parsed.coverage if item.ref_date == ref_date]
        self.assertEqual([item.entity_count for item in coverage], [3, 3])
        self.assertEqual(
            [dict(item.submission_types) for item in coverage],
            [{"N-MFP3": 4}, {"N-MFP3": 4, "N-MFP3/A": 1}],
        )


class CrossSectionCoverageTests(unittest.TestCase):
    """The declared coverage floor on a cross-sectional source.

    `sec_nmfp` aggregates every REPORT_DATE in a quarterly bulk extract as though
    each were a complete monthly cross-section. It is not: the extract carries
    one complete month plus amendment and straggler filings for adjacent months.
    Nothing caught it. Every row is present, so missingness reporting is silent,
    and the assets-to-liabilities identity reconciles on a 0.02% sample of a
    market exactly as well as on the whole of it.

    So the guard counts reporting entities, which is the one quantity that
    separates the two cases and is not itself under suspicion. A cross-section
    below the floor declared in `metadata/sources.json` is excluded from the
    panel and recorded in the quality report, under its own key: an exclusion
    folded into missingness would be a third thing this repo cannot tell apart
    from the first two.

    Mutation record
    ---------------
    Run in a copy under $HOME with `data/` copied alongside, `-B` and
    PYTHONDONTWRITEBYTECODE=1, `__pycache__` cleared before each run, against an
    unmutated control of 371 tests, OK, 1 expected failure.

    | Mutation                                                | Result       |
    |---------------------------------------------------------|--------------|
    | Floor comparison disabled: the count is computed and the | 4 failures   |
    | result discarded, so every cross-section is admitted.    |              |
    | `minimum_reporting_entities` lowered 200 -> 1 in          | 1 failure    |
    | `metadata/sources.json`, admitting the 1-series April.   |              |
    | Rows filtered on their own `ref_date` instead of on the  | 1 failure,   |
    | cross-section they were filed under.                     | 1 error      |

    Which tests fired, and why the split matters:

    1. All four acceptance tests -- both here and both in
       `RealSnapshotCoverageTests`. This is the mutation the guard exists for and
       every anchor sees it.
    2. Only
       `RealSnapshotCoverageTests::test_the_current_snapshot_contains_cross_sections_that_must_be_excluded`,
       which is the point of that test. Both tests in this class declare their
       own floor, so no fixture here can see a wrong number in the real
       registry; only the real extract can.
    3. Only the two tests in this class -- the real-snapshot pair stays green,
       because in the 2026-07 extract no straggler filing reports a flow date
       inside the admitted month, so `ref_date` and cross-section happen to
       agree. The fixture puts A4's flow row on 2 July precisely to break that
       coincidence. This is the mirror of case 2: real data anchors the declared
       number, a fixture reaches a structural case the real data does not
       currently contain, and neither substitutes for the other.

    The first mutation also caught a defect in the first draft of this guard
    rather than in the mutant: keying the aggregation by cross-section split
    contributions that the adapter had previously summed, so two admitted
    cross-sections reporting the same shareholder-flow date reached the revision
    logic as two vintages of one cell sharing one availability timestamp, and
    were rejected as unorderable. `parse_snapshots` now re-merges admitted
    contributions, which restores the pre-existing meaning of an admitted cell.
    """

    #: Three admitted filers and one straggler, against a declared floor of 3.
    #: The straggler's flow row is dated inside the *admitted* month, so a guard
    #: that excluded by `ref_date` rather than by cross-section would leave it in.
    SUBMISSIONS = (
        {
            "accession": "A1",
            "series": "S1",
            "report": "31-JUL-2026",
            "net_assets": 3_000_000_000,
            "flows": (("02-JUL-2026", 100_000_000, 40_000_000),),
        },
        {
            "accession": "A2",
            "series": "S2",
            "report": "31-JUL-2026",
            "net_assets": 2_000_000_000,
            "flows": (("02-JUL-2026", 200_000_000, 60_000_000),),
        },
        {
            "accession": "A3",
            "series": "S3",
            "report": "31-JUL-2026",
            "net_assets": 5_000_000_000,
            "flows": (("02-JUL-2026", 300_000_000, 100_000_000),),
        },
        {
            "accession": "A4",
            "series": "S4",
            "report": "30-JUN-2026",
            "net_assets": 1_000_000_000,
            "flows": (("02-JUL-2026", 900_000_000, 500_000_000),),
        },
    )

    FLOOR = 3
    ADMITTED = date(2026, 7, 31)
    EXCLUDED = date(2026, 6, 30)

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.output_root = Path(self.directory.name)
        self.artifact = fetch_sec_nmfp(
            self.output_root,
            "https://www.sec.gov/files/dera/data/form-n-mfp-data-sets/fixture.zip",
            lambda url: nmfp_archive(self.SUBMISSIONS),
        )[0]
        self.registry_path = registry_with_nmfp_coverage_floor(
            self.output_root, self.FLOOR
        )
        self.registry = json.loads(self.registry_path.read_text(encoding="utf-8"))

    def test_a_cross_section_below_the_declared_floor_is_excluded(self):
        parsed = parse_snapshots([self.artifact], registry=self.registry)

        coverage = {item.ref_date: item for item in parsed.coverage}
        self.assertEqual(sorted(coverage), [self.EXCLUDED, self.ADMITTED])
        self.assertEqual(coverage[self.ADMITTED].entity_count, 3)
        self.assertEqual(coverage[self.EXCLUDED].entity_count, 1)
        self.assertTrue(coverage[self.ADMITTED].admitted)
        self.assertFalse(coverage[self.EXCLUDED].admitted)
        self.assertEqual(coverage[self.EXCLUDED].declared_floor, self.FLOOR)
        self.assertEqual(coverage[self.EXCLUDED].entity_unit, "series_id")

        net_assets = {
            row.ref_date: row.value
            for row in parsed.rows
            if row.series_id == "mmf_net_assets"
        }
        self.assertEqual(
            sorted(net_assets),
            [self.ADMITTED],
            msg="the under-covered cross-section is still in the panel",
        )
        self.assertAlmostEqual(net_assets[self.ADMITTED], 10.0)

        # The straggler's flow row is dated 2 July, inside the admitted month.
        # Only the three admitted filers may contribute to it: 0.6 gross
        # subscriptions, not the 1.5 that including A4 would give.
        subscriptions = {
            row.ref_date: row.value
            for row in parsed.rows
            if row.series_id == "mmf_gross_subscriptions"
        }
        self.assertEqual(sorted(subscriptions), [date(2026, 7, 2)])
        self.assertAlmostEqual(
            subscriptions[date(2026, 7, 2)],
            0.6,
            msg="a row was admitted on its own ref_date rather than on the "
            "coverage of the cross-section it was filed under",
        )

    def test_an_excluded_cross_section_is_recorded_and_distinguishable_from_missingness(self):
        panel_path = self.output_root / "panel.csv"
        build_point_in_time_snapshot(
            [self.artifact], panel_path, registry_path=self.registry_path
        )
        report = json.loads(
            panel_path.with_suffix(panel_path.suffix + ".quality.json").read_text(
                encoding="utf-8"
            )
        )

        excluded = report["excluded_cross_sections"]
        self.assertEqual(
            [item["ref_date"] for item in excluded], [self.EXCLUDED.isoformat()]
        )
        record = excluded[0]
        self.assertEqual(record["source_id"], "sec_nmfp")
        self.assertEqual(record["entity_unit"], "series_id")
        self.assertEqual(record["entity_count"], 1)
        self.assertEqual(record["declared_floor"], self.FLOOR)
        self.assertGreater(record["rows"], 0)
        self.assertIn("coverage floor", record["reason"])

        # The distinguishing property, and the reason the record is a separate
        # key rather than a warning or a missingness count: a reader must be able
        # to tell "we declined to admit this cross-section" from "this
        # cross-section had gaps". Nothing here is missing -- every row the
        # source published for June is present in the extract and was dropped on
        # purpose -- so no series may report a missing reference date for it.
        self.assertEqual(report["missing_series"], {})
        for series_id, quality in report["series"].items():
            self.assertEqual(
                quality["missing_reference_dates"],
                0,
                msg=f"{series_id} reports the excluded cross-section as missingness",
            )
        self.assertNotIn(
            self.EXCLUDED.isoformat(),
            json.dumps(report["series"]),
            msg="the excluded reference date is reported as series coverage",
        )
        self.assertEqual(report["warnings"], [])


class AvailableAtDerivationTests(unittest.TestCase):
    """The adapter's `available_at` must be the registry's declaration, not a twin of it.

    `_nyfed_rows` computes `available_at` as `ref_date` plus one business day at
    15:00 America/New_York. Those three values are literals in `ingest.py`, and they
    are also `days`, `available_time` and `timezone` in `metadata/sources.json`.
    Nothing made the pair agree. Editing the registry to `days: 2` would leave the
    adapter emitting one, and every consumer of `available_at` would be reading a lag
    the registry no longer declares.

    This is the failure the contract keeps naming -- a value stated twice with nothing
    checking that the statements match -- caught here rather than at the next merge.
    The duplication is not removed; it is made detectable. Removing it means threading
    the registry into the row parsers, which changes the adapters and belongs in its
    own block.

    See `RealSnapshotPublicationGapTests` in `tests/test_data.py` for why this test,
    and not the publication-gap bound, is the one with teeth for these sources.
    """

    REGISTRY = json.loads(
        (Path(__file__).parents[1] / "metadata" / "sources.json").read_text(
            encoding="utf-8"
        )
    )

    def nyfed_snapshot(self, source_id, ref_date, retrieved):
        rate_name = source_id.split("_", 1)[1]
        payload = json.dumps(
            {
                "refRates": [
                    {
                        "effectiveDate": ref_date,
                        "percentRate": 4.31,
                        "revisionIndicator": "final",
                    }
                ]
            }
        ).encode("utf-8")
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / f"{source_id}.json"
        path.write_bytes(payload)
        return SnapshotArtifact(
            source_id=source_id,
            path=path,
            retrieved_at=retrieved,
            sha256=hashlib.sha256(payload).hexdigest(),
            url=(
                "https://markets.newyorkfed.org/api/rates/secured/"
                f"{rate_name}/search.json?type=rate"
            ),
            byte_count=len(payload),
        )

    def declared_available_at(self, lag, ref_date):
        """Recompute `available_at` from a registry declaration alone, touching no adapter code."""

        self.assertEqual(lag["basis"], "ref_date")
        self.assertEqual(lag["unit"], "business_days")
        current = ref_date
        remaining = lag["days"]
        while remaining:
            current += timedelta(days=1)
            if current.weekday() < 5:
                remaining -= 1
        return datetime.combine(
            current,
            time.fromisoformat(lag["available_time"]),
            tzinfo=ZoneInfo(lag["timezone"]),
        )

    def ref_date_sources(self):
        return sorted(
            source_id
            for source_id, source in self.REGISTRY.items()
            if source.get("release_lag", {}).get("basis") == "ref_date"
        )

    def test_every_ref_date_source_is_covered_by_this_test(self):
        """A source added to the registry without a case here would go unchecked."""

        self.assertEqual(
            self.ref_date_sources(), ["nyfed_bgcr", "nyfed_sofr", "nyfed_tgcr"]
        )

    def test_adapter_available_at_matches_the_registry_declaration(self):
        for source_id in self.ref_date_sources():
            lag = self.REGISTRY[source_id]["release_lag"]
            # A midweek date and a Friday: the Friday is the only one whose
            # calendar gap differs from its business-day lag.
            for ref_date in (date(2026, 1, 6), date(2026, 1, 9)):
                with self.subTest(source=source_id, ref_date=ref_date):
                    snapshot = self.nyfed_snapshot(
                        source_id,
                        ref_date.isoformat(),
                        # Retrieved long after, so the min() against retrieval time
                        # cannot mask a disagreement with the declaration.
                        "2026-06-01T00:00:00+00:00",
                    )
                    rows = list(observations_from_snapshots([snapshot]))
                    self.assertTrue(rows)
                    expected = self.declared_available_at(lag, ref_date)
                    for row in rows:
                        self.assertEqual(row.available_at, expected)

    def test_a_registry_lag_the_adapter_does_not_honour_is_caught(self):
        """The tripwire above is only worth having if a divergence actually fails it.

        Written because an equality assertion between two values computed the same
        way passes whatever either one says.
        """

        source_id = "nyfed_sofr"
        ref_date = date(2026, 1, 6)
        snapshot = self.nyfed_snapshot(
            source_id, ref_date.isoformat(), "2026-06-01T00:00:00+00:00"
        )
        rows = list(observations_from_snapshots([snapshot]))
        drifted = dict(self.REGISTRY[source_id]["release_lag"])
        drifted["days"] = drifted["days"] + 1
        self.assertNotEqual(
            rows[0].available_at, self.declared_available_at(drifted, ref_date)
        )

if __name__ == "__main__":
    unittest.main()
