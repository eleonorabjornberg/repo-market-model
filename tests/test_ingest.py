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
    ArchiveRefusal,
    NMFP_INVESTMENT_CATEGORY_ERAS,
    REFUSAL_ABSENT_FIELDS,
    REFUSAL_UNREADABLE,
    SnapshotArtifact,
    _decode_transport,
    _nmfp_number,
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


#: The `INVESTMENTCATEGORY` strings the fixtures file. Taken verbatim from the
#: declaration in `repo_model.ingest`, and therefore from what SEC actually
#: files, so a fixture cannot pass by agreeing with the parser about a
#: vocabulary the source does not use. Both are declared in the 2016-04..2024-05
#: and 2024-06..2026-07 eras, which is every era the fixtures date themselves
#: into.
FIXTURE_TREASURY_CATEGORY = "U.S. Treasury Debt"
FIXTURE_REPO_CATEGORY = (
    "U.S. Treasury Repurchase Agreement, if collateralized only by "
    "U.S. Treasuries (including Strips) and cash"
)


def nmfp_archive(
    submissions,
    *,
    omit=(),
    treasury_category=FIXTURE_TREASURY_CATEGORY,
    repo_category=FIXTURE_REPO_CATEGORY,
) -> bytes:
    """Build a minimal but structurally faithful Form N-MFP flat-file ZIP.

    `submissions` is a sequence of dicts with `accession`, `series`, `report`
    and optional `net_assets` (USD, not billions), `other_assets` (USD, default
    0 -- a nonzero value breaks the declared balance-sheet identity by exactly
    that amount, which is how a fixture files a cross-section that violates),
    `filing` (the DD-MON-YYYY filing date, defaulting to the report date),
    `submission_type` (defaulting to `N-MFP3`) and `flows`, a sequence of
    `(flow_date, subscriptions, redemptions)`. The tables carry the same column
    names, the same DD-MON-YYYY dates and the same INVESTMENTCATEGORY strings as
    the SEC extract, so a fixture cannot pass by agreeing with the parser about
    a format or a vocabulary the source does not use.

    `omit` names tables to leave out of the ZIP entirely, which is how the
    archives filed before 2024-06-10 are shaped: they carry no
    `NMFP_DLYSHAREHOLDERFLOWREPORT.tsv` because daily shareholder flows were not
    collected yet. It leaves the table out rather than writing an empty one --
    an empty table is a claim that nothing was reported, and these archives make
    no such claim.
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
        # cash + portfolio + other == liabilities + net assets, to the dollar,
        # unless the entry deliberately breaks it. `other_assets` is the one
        # term a submission may override, because a fixture that can only file
        # a reconciling balance sheet cannot exercise the violation verdict at
        # all -- and until `IdentityVerdictTests` there was no way to observe a
        # violated identity except by the exception it used to raise. Absent the
        # key the row is byte-for-byte what it always was, so no existing
        # fixture moves.
        other = entry.get("other_assets", 0)
        series_rows.append(f"{entry['accession']}\t0\t{net}\t{other}\t0\t{net}")
        for flow_date, subscriptions, redemptions in entry.get("flows", ()):
            flow_rows.append(
                f"{entry['accession']}\t{subscriptions}\t{redemptions}\t{flow_date}"
            )
        # Every holdings series is populated for every filer, so that any
        # missingness the quality report shows can only come from the coverage
        # floor and not from a series the fixture never supplied.
        holding_rows.append(
            f"{entry['accession']}\t{treasury_category}\t{net // 2}\t"
            "United States Treasury\tBill\t"
        )
        holding_rows.append(
            f"{entry['accession']}\t{repo_category}\t{net // 4}\t"
            "Federal Reserve Bank of New York\tReverse repo\t"
        )

    tables = {
        "NMFP_SUBMISSION.tsv": submission_rows,
        "NMFP_SERIESLEVELINFO.tsv": series_rows,
        "NMFP_DLYSHAREHOLDERFLOWREPORT.tsv": flow_rows,
        "NMFP_SCHPORTFOLIOSECURITIES.tsv": holding_rows,
    }
    unknown = frozenset(omit) - frozenset(tables)
    if unknown:
        raise AssertionError(f"fixture cannot omit tables it never writes: {unknown}")
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, rows in tables.items():
            if name in omit:
                continue
            archive.writestr(name, "\n".join(rows) + "\n")
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


class NMFPDecimalCommaTests(unittest.TestCase):
    """What `_nmfp_number` does with a decimal comma, pinned rather than fixed.

    `metadata/sources.json` records this behaviour in the `sec_nmfp`
    limitation. A claim in the registry with nothing executing it is the drift
    this repository keeps naming, so the claim and the code are asserted
    against each other here.

    The behaviour is deliberately not corrected. A locale-sniffing heuristic
    would be a silent behaviour change calibrated on data nobody has seen, and
    a differently-formatted extract should fail loudly rather than parse
    plausibly. This test exists so that a later change to `_nmfp_number` has to
    change the recorded claim with it.
    """

    def test_a_thousands_comma_is_stripped(self):
        self.assertEqual(_nmfp_number("1,234.56", "CASH"), 1234.56)

    def test_a_decimal_comma_parses_silently_and_wrong(self):
        # One digit after the comma is a factor of ten; two is a hundred.
        # Neither raises, which is the whole hazard.
        self.assertEqual(_nmfp_number("1234,5", "CASH"), 12345.0)
        self.assertEqual(_nmfp_number("1234,56", "CASH"), 123456.0)

    def test_a_european_grouped_number_parses_silently_and_wrong(self):
        # Period as the thousands separator survives the comma strip and is
        # then read as the decimal point, so the value is off by a thousand in
        # the other direction.
        self.assertEqual(_nmfp_number("1.234,56", "CASH"), 1.23456)


class ArchiveManifestTests(unittest.TestCase):
    """The declared archive set, and the fetch that reads it.

    `data/raw/` is gitignored, so the bytes that make up `sec_nmfp` are not in
    the repository and a fresh checkout has no way to know how much history is
    supposed to exist. The manifest is that record. It has to distinguish four
    states that all look like an absent file: never declared, declared but not
    fetched here, fetched and read but carrying no table for some fields, and
    fetched and unreadable. The last two were one state until refusal became
    per-table, and collapsing them says "this archive is unreadable" about a file
    whose only fault is that the data it is short of did not exist yet.
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
        # The same archive with the daily shareholder-flow table removed -- the
        # shape every Form N-MFP set published before that report existed
        # actually has. It is read, not refused: it supplies everything its other
        # tables supply and is short exactly three fields.
        self.without_flow_table = nmfp_archive(
            (
                {
                    "accession": "0000000000-26-000001",
                    "series": "S000000001",
                    "report": "31-JUL-2026",
                },
            ),
            omit=("NMFP_DLYSHAREHOLDERFLOWREPORT.tsv",),
        )
        # A table that is present with a column the adapter reads renamed. This
        # is the failure that has to refuse the whole archive: `record.get()`
        # returns None, the row is skipped, and the archive parses
        # "successfully" while contributing a partial balance sheet that
        # satisfies the identity because both sides lost the same rows.
        renamed = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(self.readable)) as original:
            with zipfile.ZipFile(renamed, "w") as archive:
                for name in original.namelist():
                    payload = original.read(name)
                    if name == "NMFP_SUBMISSION.tsv":
                        header, rows = payload.decode("utf-8").split("\n", 1)
                        payload = (
                            f"{header.replace('FILING_DATE', 'FILED')}\n{rows}"
                        ).encode()
                    archive.writestr(name, payload)
        self.unreadable = renamed.getvalue()

    def _serve(self, payloads):
        calls = []

        def downloader(url):
            calls.append(url)
            return payloads[url]

        return downloader, calls

    def test_an_archive_the_parser_cannot_read_never_reaches_the_raw_tree(self):
        url = f"{self.SEC_URL}renamed.zip"
        downloader, calls = self._serve({url: self.unreadable})
        updated = fetch_sec_nmfp_archives(
            self.output_root,
            [ArchiveRecord(url=url)],
            downloader=downloader,
            pause_seconds=0,
        )
        self.assertEqual(calls, [url])
        self.assertEqual([item.kind for item in updated[0].refusals], [REFUSAL_UNREADABLE])
        self.assertIn("FILING_DATE", updated[0].refusals[0].detail)
        self.assertFalse(updated[0].admitted)
        # Everything under data/raw/ is panel input by construction. An archive
        # the parser refuses is not panel input, so it is recorded and not
        # written: leaving it there and filtering later is the same claim made
        # in a place nothing reads.
        self.assertEqual(list((self.output_root / "sec_nmfp").glob("*.zip")), [])
        self.assertNotEqual(updated[0].sha256, "")

    def test_an_archive_missing_a_table_is_admitted_and_says_what_it_costs(self):
        """The other half of the same rule, and the reason it is not one rule.

        A missing table is loud, attributable to named fields, and its whole
        consequence is that those fields have no observation. That is a state
        the panel already represents, so the archive belongs in the raw tree
        with the cost recorded -- not on the refused pile next to files nobody
        can read.
        """

        url = f"{self.SEC_URL}old.zip"
        downloader, calls = self._serve({url: self.without_flow_table})
        updated = fetch_sec_nmfp_archives(
            self.output_root,
            [ArchiveRecord(url=url)],
            downloader=downloader,
            pause_seconds=0,
        )
        self.assertEqual(calls, [url])
        self.assertEqual(
            [item.kind for item in updated[0].refusals], [REFUSAL_ABSENT_FIELDS]
        )
        self.assertEqual(
            updated[0].refusals[0].table, "NMFP_DLYSHAREHOLDERFLOWREPORT.tsv"
        )
        self.assertEqual(
            updated[0].absent_fields,
            ("mmf_gross_redemptions", "mmf_gross_subscriptions", "mmf_net_flow"),
        )
        self.assertTrue(updated[0].admitted)
        self.assertEqual(
            len(list((self.output_root / "sec_nmfp").glob("*.zip"))),
            1,
            msg="an archive that is merely short a table was withheld from the "
            "raw tree as though it were unreadable",
        )

    def test_a_recorded_archive_is_not_downloaded_twice(self):
        readable_url = f"{self.SEC_URL}new.zip"
        refused_url = f"{self.SEC_URL}renamed.zip"
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
        # under its recorded digest, and the unreadable one has a verdict already
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

    def test_an_archive_recorded_short_a_table_is_refetched_when_its_bytes_are_gone(self):
        """The widened rule has to be able to re-earn the history it admits.

        Under the per-archive rule these 71 archives were judged, recorded and
        discarded. Their recorded verdict now says only which fields they are
        short, which is not a reason to leave them unfetched -- and skipping them
        because the `refusals` list is non-empty would mean the widening never
        reached the bytes it was written for.
        """

        url = f"{self.SEC_URL}old.zip"
        downloader, calls = self._serve({url: self.without_flow_table})
        first = fetch_sec_nmfp_archives(
            self.output_root, [ArchiveRecord(url=url)], downloader=downloader,
            pause_seconds=0,
        )
        self.assertTrue(first[0].admitted)

        for path in (self.output_root / "sec_nmfp").iterdir():
            path.unlink()
        again_downloader, again_calls = self._serve({url: self.without_flow_table})
        fetch_sec_nmfp_archives(
            self.output_root, first, downloader=again_downloader, pause_seconds=0
        )
        self.assertEqual(again_calls, [url])
        self.assertEqual(
            len(list((self.output_root / "sec_nmfp").glob("*.zip"))), 1
        )

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
                refusals=(
                    ArchiveRefusal(
                        kind=REFUSAL_UNREADABLE,
                        table="NMFP_SUBMISSION.tsv",
                        detail="NMFP_SUBMISSION.tsv lacks required columns FILING_DATE",
                    ),
                ),
            ),
            ArchiveRecord(
                url=f"{self.SEC_URL}c.zip",
                sha256="c" * 64,
                byte_count=3,
                first_retrieved_at="2026-09-07T00:00:00+00:00",
                refusals=(
                    ArchiveRefusal(
                        kind=REFUSAL_ABSENT_FIELDS,
                        table="NMFP_DLYSHAREHOLDERFLOWREPORT.tsv",
                        fields=("mmf_net_flow",),
                        detail="lacks NMFP_DLYSHAREHOLDERFLOWREPORT.tsv",
                    ),
                ),
            ),
        )
        write_sec_nmfp_archive_manifest(records, path)
        loaded = load_sec_nmfp_archive_manifest(path)
        self.assertEqual([item.url for item in loaded], sorted(item.url for item in records))
        # a.zip is unreadable; b.zip is clean; c.zip is read and short one field.
        self.assertEqual([item.admitted for item in loaded], [False, True, True])
        self.assertEqual(loaded[2].absent_fields, ("mmf_net_flow",))
        self.assertEqual(loaded[0].absent_fields, ())

        # A bare string cannot say which of the two happened, so it is not read
        # as either. Silently treating it as one would re-collapse the states
        # this record exists to separate.
        legacy = self.output_root / "legacy.json"
        legacy.write_text(
            json.dumps(
                {
                    "archives": [
                        {
                            "url": f"{self.SEC_URL}a.zip",
                            "sha256": "a" * 64,
                            "refusals": ["lacks required table X"],
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, r"must be an object naming its kind"):
            load_sec_nmfp_archive_manifest(legacy)

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
        short = [record for record in records if record.absent_fields]
        self.assertGreater(
            len(short),
            0,
            "no declared archive is recorded as short a table, so this record is "
            "not distinguishing the schema eras the backfill found",
        )
        # Every one of them is short the same three fields for the same reason:
        # the daily shareholder-flow report did not exist before 2024-06-10.
        self.assertEqual(
            {record.absent_fields for record in short},
            {("mmf_gross_redemptions", "mmf_gross_subscriptions", "mmf_net_flow")},
        )
        self.assertEqual(
            [record.url for record in records if record.unreadable],
            [],
            "a declared archive is unreadable, which is a schema change nobody "
            "has looked at rather than a table that did not exist yet",
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
        found = nmfp_schema_refusals(rewritten.getvalue())
        self.assertEqual(
            [(item.kind, item.table) for item in found],
            [
                (REFUSAL_ABSENT_FIELDS, "NMFP_DLYSHAREHOLDERFLOWREPORT.tsv"),
                (REFUSAL_UNREADABLE, "NMFP_SUBMISSION.tsv"),
            ],
        )
        self.assertIn("FILING_DATE", found[1].detail)

    def test_a_response_that_is_not_a_zip_is_refused_rather_than_crashing(self):
        found = nmfp_schema_refusals(b"<html>rate limited</html>")
        self.assertEqual(
            [(item.kind, item.detail) for item in found],
            [(REFUSAL_UNREADABLE, "not a valid ZIP archive")],
        )

    def test_an_archive_without_the_spine_table_is_unreadable_not_merely_short(self):
        """The one absent table that cannot cost only its own fields.

        `NMFP_SUBMISSION.tsv` carries no panel value. It says which series and
        which report date each accession speaks for, so without it no row in the
        archive can be placed at all -- there is no cross-section to be short of
        anything.
        """

        stripped = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(self.readable)) as original:
            with zipfile.ZipFile(stripped, "w") as archive:
                for name in original.namelist():
                    if name == "NMFP_SUBMISSION.tsv":
                        continue
                    archive.writestr(name, original.read(name))
        found = nmfp_schema_refusals(stripped.getvalue())
        self.assertEqual(
            [(item.kind, item.table) for item in found],
            [(REFUSAL_UNREADABLE, "NMFP_SUBMISSION.tsv")],
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

    The composition of the two mechanisms is what is under test here.
    `_resolve_nmfp_submissions` keeps the latest filing per (series, report
    date); the revision logic in `parse_snapshots` appends a changed value as a
    new vintage rather than adding it. Neither half is sufficient alone and
    neither had ever been exercised.

    The resolution is no longer scoped to one archive -- see
    `CrossArchiveSupersessionTests` -- and this class does not move, because
    the amendment here arrives in the later-retrieved archive and per-archive
    and assembled resolution agree on that case. What it pins is the half that
    assembly must not disturb: two archives filing into one report date still
    reach the panel as two vintages of one cross-section, so a correction stays
    attributable rather than being collapsed into a single final value.

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


class CrossArchiveSupersessionTests(unittest.TestCase):
    """A cross-section is a report date, not an archive.

    `_resolve_nmfp_submissions` used to run inside `_sec_nmfp_rows`, over one
    archive's submissions, and the coverage floor used to be applied to one
    archive's cross-section. Both were right while the repository held one
    extract. The backfill made them wrong and nothing noticed, because each
    archive on its own still looks exactly as it did.

    Two questions were being decided on that one wrong unit, and they are not
    the same question. Supersession is per `(SERIESID, REPORTDATE)` across every
    archive: an amendment routinely lands in a different archive from the filing
    it restates, and per-archive resolution cannot see the pair, so the panel
    carried the superseded original. Coverage is per `REPORTDATE` across every
    archive: the straggler cohorts an archive carries for adjacent months are
    each far below the floor, and excluding each separately discards the
    amendments along with the cohort -- which is the right verdict about a
    cross-section and the wrong one about an amendment, and is why the
    originals survived unreplaced.

    Measured on `2016-04-30` across the archives on disk: 506 submissions in 5
    archives, 413 distinct `SERIESID`, and of the 93 submissions global
    resolution supersedes, 47 are superseded by a filing in a *different*
    archive. Over the whole 97-archive set, per-archive resolution supersedes
    2192 submissions and global resolution supersedes 5095; the 2903 it cannot
    see are all cross-archive.

    These fixtures are built from in-memory archives rather than from
    `data/raw/`, so they state the structural case rather than depending on it
    still being present in a backfill. `test_global_resolution_supersedes_more_than_per_archive_resolution`
    is the one conditional test, holding the fixtures to the real archives
    where those are on disk.

    What this class deliberately does not assert: that the `2016-04-30` identity
    violation goes away. It does not. The residual is ~680 ppm before this
    change and ~680 ppm after, because the corrections fall on both sides of the
    balance-sheet identity and cancel. That is recorded in the packet as a
    hypothesis already killed, and a version of this change that *did* move the
    residual would have changed more than supersession.

    Mutation record
    ---------------
    Run in a copy under `$HOME` -- never in the mount -- with `data/`,
    `.github/`, `metadata/`, `.gitignore`, the root Markdown and
    `docs/PROJECT_STATUS.md` alongside, `__pycache__` cleared before each run,
    `-B` and PYTHONDONTWRITEBYTECODE=1. Unmutated control run twice, green both
    times, before and after: 578 tests, OK, zero expected failures. That count
    is the suite as of `d997fe7`, the tip the mutation copy was taken from;
    `feature/data-layer` was fast-forwarded onto Track B's `bb2407a` while these
    ran, which adds 31 tests in `test_baseline`, `test_cli_eval` and
    `test_metrics` and touches nothing this block does. A red run is not
    evidence the aimed-at test fired, so every kill is recorded with the
    exception it raised.

    | Mutation                                                 | Result      |
    |----------------------------------------------------------|-------------|
    | 1. Resolution moved back inside the per-archive loop:      | 4 failures  |
    |    each archive resolved alone and the kept sets unioned.  |             |
    | 2. The tie-break on equal `FILING_DATE` reversed, so the   | 2 failures  |
    |    lowest accession wins a same-day tie.                   |             |
    | 3. Assembly keyed on `(SERIESID, REPORTDATE, archive)`     | 3 failures  |
    |    instead of `(SERIESID, REPORTDATE)`.                    |             |
    | 4. The coverage floor left exactly as it is: the admission | no change   |
    |    comparison rewritten to an equivalent, the declared      |             |
    |    number and unit untouched.                              |             |

    Which tests fired, and with what:

    1. `AssertionError` on three tests here --
       `test_an_amendment_in_another_archive_supersedes_the_original` and
       `test_an_amendment_cohort_below_the_coverage_floor_still_supersedes`
       (both `26.0 != 24.0`: the superseding amendment is kept *and* the
       original it replaces, so the cross-section is booked twice for that
       series) and `test_the_tie_break_on_equal_filing_dates_is_the_accession`
       (`36.0 != 6.0`) -- plus `AssertionError` (`53.0 != 51.0`) on
       `OverlappingArchiveTests::test_overlapping_archives_do_not_double_count_a_report_date`.
       This is the mutation the block exists for and the acceptance test sees it.
    2. `AssertionError` on
       `test_the_tie_break_on_equal_filing_dates_is_the_accession`
       (`33.0 != 6.0`) and on
       `OverlappingArchiveTests::test_overlapping_archives_do_not_double_count_a_report_date`
       (`24.0 != 51.0`). The tie-break is held by two tests, in two classes, on
       two different fixtures -- so it is not untested, which was the finding
       this mutation was run to rule out.
    3. `AssertionError` on the same three tests in this class as mutation 1, with
       the same values. It does *not* kill `OverlappingArchiveTests`, and the
       reason is worth stating rather than filing as noise: that fixture is the
       only place where one accession number appears in two archives, and the
       archive map this mutation builds is last-wins, so both copies key to the
       same archive and the mutation degenerates into the correct behaviour
       there. On `data/raw/` no accession appears in more than one archive
       (checked: 0 of 93942), so the mutation is faithful where it matters. The
       acceptance test fires either way, which is what this mutation was for:
       the defect restated must not pass.
    4. Nothing changed, which is the point. This block moves supersession and
       the unit coverage is judged on; it does not move the floor. The declared
       `minimum_reporting_entities` is still 200 and `entity_unit` is still
       `series_id` in `metadata/sources.json`, which this block does not touch.
    """

    #: A report date filed into by more than one archive. Every fixture here
    #: uses one report date, because the unit under test is the report date.
    REPORT = "31-JAN-2023"
    REF_DATE = date(2023, 1, 31)

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.output_root = Path(self.directory.name)

    @staticmethod
    def _submission(accession, series, filing, billions, submission_type="N-MFP3"):
        return {
            "accession": accession,
            "series": series,
            "report": CrossArchiveSupersessionTests.REPORT,
            "filing": filing,
            "submission_type": submission_type,
            "net_assets": billions * 1_000_000_000,
        }

    def _archive(self, name, submissions, retrieved_at):
        artifact = fetch_sec_nmfp(
            self.output_root / name,
            f"https://www.sec.gov/files/dera/data/form-n-mfp-data-sets/{name}.zip",
            lambda url: nmfp_archive(submissions),
        )[0]
        # Retrieval order is what orders vintages, and two fetches in one test
        # run are microseconds apart. Declaring the timestamps keeps the
        # assertion about the adapter rather than about clock resolution.
        return replace(artifact, retrieved_at=retrieved_at)

    def _net_assets(self, parsed):
        """The latest vintage of `mmf_net_assets` on the fixture's report date."""

        rows = [
            row
            for row in parsed.rows
            if row.series_id == "mmf_net_assets" and row.ref_date == self.REF_DATE
        ]
        self.assertTrue(rows, "no mmf_net_assets row was emitted at all")
        return max(rows, key=lambda row: row.available_at).value

    def test_an_amendment_in_another_archive_supersedes_the_original(self):
        """The acceptance criterion. Fails against per-archive resolution.

        `S000000002` files an original in the archive retrieved second and an
        amendment, filed a month later, in the archive retrieved first. The
        filing dates say which is which; the archives do not. Per-archive
        resolution sees one submission in each archive, supersedes nothing, and
        the later-retrieved archive's cross-section -- carrying the *original* --
        becomes the latest vintage.
        """

        amending = self._archive(
            "amending",
            [
                self._submission("0000000000-23-000001", "S000000001", "10-FEB-2023", 1),
                self._submission(
                    "0000000000-23-000099", "S000000002", "15-MAR-2023", 20,
                    submission_type="N-MFP3/A",
                ),
                self._submission("0000000000-23-000003", "S000000003", "10-FEB-2023", 3),
            ],
            "2026-03-01T00:00:00+00:00",
        )
        original = self._archive(
            "original",
            [
                self._submission("0000000000-23-000001", "S000000001", "10-FEB-2023", 1),
                self._submission("0000000000-23-000002", "S000000002", "10-FEB-2023", 2),
                self._submission("0000000000-23-000003", "S000000003", "10-FEB-2023", 3),
            ],
            "2026-04-01T00:00:00+00:00",
        )

        parsed = parse_snapshots(
            [amending, original],
            registry_path=registry_with_nmfp_coverage_floor(self.output_root, 3),
        )

        # 1 + 20 + 3. Per-archive resolution gives 6.0: the second archive holds
        # only the original, resolves nothing, and replaces the assembled value
        # with its own. 26.0 would mean both accessions for S000000002 were
        # added rather than resolved.
        self.assertEqual(
            self._net_assets(parsed),
            24.0,
            msg="the panel carries a submission that a filing in another "
            "archive superseded",
        )

    def test_an_amendment_cohort_below_the_coverage_floor_still_supersedes(self):
        """A straggler cohort is not a cross-section, and its amendment still wins.

        The amending archive carries one submission against a floor of three. It
        is not a cross-section and must not be admitted as one -- but the
        cross-section it amends is assembled from every archive, so its
        amendment is part of that assembly and the floor never sees the cohort
        as a thing to judge.
        """

        bulk = self._archive(
            "bulk",
            [
                self._submission("0000000000-23-000001", "S000000001", "10-FEB-2023", 1),
                self._submission("0000000000-23-000002", "S000000002", "10-FEB-2023", 2),
                self._submission("0000000000-23-000003", "S000000003", "10-FEB-2023", 3),
            ],
            "2026-03-01T00:00:00+00:00",
        )
        straggler = self._archive(
            "straggler",
            [
                self._submission(
                    "0000000000-23-000099", "S000000002", "15-MAR-2023", 20,
                    submission_type="N-MFP3/A",
                )
            ],
            "2026-04-01T00:00:00+00:00",
        )

        parsed = parse_snapshots(
            [bulk, straggler],
            registry_path=registry_with_nmfp_coverage_floor(self.output_root, 3),
        )

        # 1 + 20 + 3. Per-archive: the straggler archive is a 1-series
        # cross-section, is excluded by the floor, and takes the amendment with
        # it, leaving 6.0 -- the originals standing unreplaced.
        self.assertEqual(
            self._net_assets(parsed),
            24.0,
            msg="an amendment was discarded with the straggler cohort it "
            "arrived in",
        )

        # The assembled cross-section is admitted, and it is admitted once per
        # archive that files into it rather than once per archive that happens
        # to clear the floor alone.
        coverage = [item for item in parsed.coverage if item.ref_date == self.REF_DATE]
        self.assertEqual([item.entity_count for item in coverage], [3, 3])
        self.assertTrue(all(item.admitted for item in coverage))

    def test_a_series_present_only_in_a_small_archive_joins_the_assembled_cross_section(self):
        """The series that per-archive coverage drops from the panel entirely.

        `S000000004` files in no archive but the straggler one. Judged as its own
        cross-section that archive is a 1-series cohort and is excluded, so the
        series never reaches the panel -- not as a missing value, as nothing at
        all. Judged as part of the report date it was filed under, it is one more
        series in a cross-section of four.
        """

        bulk = self._archive(
            "bulk",
            [
                self._submission("0000000000-23-000001", "S000000001", "10-FEB-2023", 1),
                self._submission("0000000000-23-000002", "S000000002", "10-FEB-2023", 2),
                self._submission("0000000000-23-000003", "S000000003", "10-FEB-2023", 3),
            ],
            "2026-03-01T00:00:00+00:00",
        )
        straggler = self._archive(
            "straggler",
            [self._submission("0000000000-23-000004", "S000000004", "20-FEB-2023", 7)],
            "2026-04-01T00:00:00+00:00",
        )

        parsed = parse_snapshots(
            [bulk, straggler],
            registry_path=registry_with_nmfp_coverage_floor(self.output_root, 3),
        )

        # 1 + 2 + 3 + 7. Per-archive gives 6.0 and the fourth series is absent
        # from the panel with nothing recording that it filed.
        self.assertEqual(
            self._net_assets(parsed),
            13.0,
            msg="a series that filed only in a small archive is missing from "
            "the assembled cross-section",
        )
        coverage = [item for item in parsed.coverage if item.ref_date == self.REF_DATE]
        self.assertEqual([item.entity_count for item in coverage], [3, 4])

    def test_the_tie_break_on_equal_filing_dates_is_the_accession(self):
        """Two filings, one day, two archives: the rule must still be total.

        `FILING_DATE` is the archive's own statement of filing order and it is
        what makes an amendment an amendment, but it does not separate two
        submissions filed the same day. Across archives the fallback cannot be
        row order in a file, because there is no one file. It is the accession.
        """

        first = self._archive(
            "first",
            [
                self._submission("0000000000-23-000001", "S000000001", "10-FEB-2023", 1),
                self._submission("0000000000-23-000002", "S000000002", "10-FEB-2023", 2),
                self._submission("0000000000-23-000050", "S000000003", "10-FEB-2023", 3),
            ],
            "2026-03-01T00:00:00+00:00",
        )
        second = self._archive(
            "second",
            [
                self._submission("0000000000-23-000040", "S000000003", "10-FEB-2023", 30)
            ],
            "2026-04-01T00:00:00+00:00",
        )

        parsed = parse_snapshots(
            [first, second],
            registry_path=registry_with_nmfp_coverage_floor(self.output_root, 3),
        )

        # 1 + 2 + 3. `...050` outranks `...040` on the same filing date, so the
        # later-retrieved archive does not win by arriving later. Reversing the
        # tie-break gives 33.0; dropping it makes the answer depend on which
        # archive was read first.
        self.assertEqual(
            self._net_assets(parsed),
            6.0,
            msg="the same-day tie-break did not decide between two archives",
        )

    def test_the_coverage_floor_still_excludes_an_assembled_straggler_month(self):
        """Assembly must not admit what the floor exists to reject.

        Making coverage a question about a report date rather than an archive is
        not the same as relaxing it. A report date that is a straggler cohort in
        every archive that carries it is still a straggler cohort assembled, and
        is still excluded.
        """

        bulk = self._archive(
            "bulk",
            [
                self._submission("0000000000-23-000001", "S000000001", "10-FEB-2023", 1),
                self._submission("0000000000-23-000002", "S000000002", "10-FEB-2023", 2),
                self._submission("0000000000-23-000003", "S000000003", "10-FEB-2023", 3),
                {
                    "accession": "0000000000-23-000004",
                    "series": "S000000004",
                    "report": "31-DEC-2022",
                    "filing": "10-FEB-2023",
                    "net_assets": 9_000_000_000,
                },
            ],
            "2026-03-01T00:00:00+00:00",
        )
        straggler = self._archive(
            "straggler",
            [
                {
                    "accession": "0000000000-23-000005",
                    "series": "S000000005",
                    "report": "31-DEC-2022",
                    "filing": "20-FEB-2023",
                    "net_assets": 8_000_000_000,
                }
            ],
            "2026-04-01T00:00:00+00:00",
        )

        parsed = parse_snapshots(
            [bulk, straggler],
            registry_path=registry_with_nmfp_coverage_floor(self.output_root, 3),
        )

        december = [
            item for item in parsed.coverage if item.ref_date == date(2022, 12, 31)
        ]
        self.assertTrue(december, "the excluded cross-section was not recorded")
        self.assertEqual([item.entity_count for item in december], [1, 2])
        self.assertFalse(
            any(item.admitted for item in december),
            msg="assembling across archives admitted a cross-section that is "
            "still below the floor",
        )
        self.assertEqual(
            [row.ref_date for row in parsed.rows if row.ref_date == date(2022, 12, 31)],
            [],
            msg="an excluded cross-section reached the panel",
        )

    def test_global_resolution_supersedes_more_than_per_archive_resolution(self):
        """The one conditional test: hold the fixtures to the real archives.

        Skips where `data/raw/sec_nmfp/` is not populated -- it is gitignored, so
        this runs only where the adapters have been run. Not `expectedFailure`:
        that marker claims the assertion is right and the code is wrong, and it
        hid a TypeError in this repo for the whole life of the class it was on.
        """

        raw = Path(__file__).parents[1] / "data" / "raw" / "sec_nmfp"
        manifests = sorted(raw.glob("*.manifest.json"))
        if not manifests:
            self.skipTest(
                f"no sec_nmfp snapshots under {raw}; data/raw/ is gitignored, so "
                "this check runs only where the adapters have been run. It is "
                "not waiting on an unwritten implementation."
            )

        from repo_model.ingest import _nmfp_archive_scan, _resolve_nmfp_submissions

        per_archive = 0
        everything = {}
        for manifest_path in manifests:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            artifact = SnapshotArtifact(
                source_id=manifest["source_id"],
                path=manifest_path.parent / Path(manifest["path"]).name,
                retrieved_at=manifest["retrieved_at"],
                sha256=manifest["sha256"],
                url=manifest["url"],
                byte_count=int(manifest["byte_count"]),
            )
            submissions, _types, _cells, _absent = _nmfp_archive_scan(
                artifact.path.read_bytes()
            )
            _kept, superseded = _resolve_nmfp_submissions(submissions)
            per_archive += len(superseded)
            everything.update(submissions)

        _kept, globally = _resolve_nmfp_submissions(everything)
        self.assertGreater(
            len(globally),
            per_archive,
            msg="global resolution found no amendment that per-archive "
            "resolution missed; either the archives no longer overlap or the "
            "resolution is not global",
        )

class PerTableRefusalTests(unittest.TestCase):
    """Refusal is per table, and the INVESTMENTCATEGORY vocabulary is declared.

    These two rules land together because the first one opens the door the
    second one has to close. Making an absent table cost its own fields is what
    admits the 71 archives filed before 2024-06-10, which carry no daily
    shareholder-flow table because the data did not exist. Every column this
    adapter reads is present under the same name in all of them, so a header
    check waves them all through -- and `INVESTMENTCATEGORY`, which the adapter
    matches on by *value*, was relabelled from `Treasury Debt` to
    `U.S. Treasury Debt` at the 2016-04 report month. Admitting the earlier
    archives without declaring that boundary would have produced
    `mmf_treasury_holdings` silently empty from 2010-11 to 2016-03 while
    `mmf_repo_holdings` populated, with the balance-sheet identity satisfied and
    nothing flagged.

    The fixtures use the report dates and the INVESTMENTCATEGORY strings the SEC
    extracts actually carry, so a fixture cannot pass by agreeing with the parser
    about a vocabulary the source does not use.
    """

    FLOOR = 2

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.output_root = Path(self.directory.name)
        self.registry_path = registry_with_nmfp_coverage_floor(
            self.output_root, self.FLOOR
        )
        self.registry = json.loads(self.registry_path.read_text(encoding="utf-8"))

    def _parse(self, payload: bytes, name: str = "fixture"):
        artifact = fetch_sec_nmfp(
            self.output_root,
            f"https://www.sec.gov/files/dera/data/form-n-mfp-data-sets/{name}.zip",
            lambda url: payload,
        )[0]
        return parse_snapshots([artifact], registry=self.registry)

    @staticmethod
    def _submissions(report: str):
        return (
            {
                "accession": "A1",
                "series": "S1",
                "report": report,
                "net_assets": 3_000_000_000,
            },
            {
                "accession": "A2",
                "series": "S2",
                "report": report,
                "net_assets": 5_000_000_000,
            },
        )

    def test_an_archive_without_the_flow_table_still_supplies_the_balance_sheet(self):
        """A missing table costs its own fields, and costs nothing else.

        This is the shape of every Form N-MFP archive filed before 2024-06-10:
        `NMFP_SERIESLEVELINFO` and `NMFP_SCHPORTFOLIOSECURITIES` are there,
        `NMFP_DLYSHAREHOLDERFLOWREPORT` is not, because daily shareholder flows
        were not collected. Fourteen years of balance sheets and holdings were
        being discarded over the absence of a flow table.

        The second half of the assertion matters as much as the first. The three
        flow series must be **absent**, not zero. A month with no flow table has
        no `mmf_net_flow` row; it does not have a zero one, and a zero would be
        this adapter stating that subscriptions equalled redemptions on a day
        nobody reported.
        """

        report_date = date(2023, 1, 31)
        parsed = self._parse(
            nmfp_archive(
                self._submissions("31-JAN-2023"),
                omit=("NMFP_DLYSHAREHOLDERFLOWREPORT.tsv",),
            )
        )

        values = {}
        for row in parsed.rows:
            values.setdefault(row.series_id, {})[row.ref_date] = row.value

        self.assertTrue(
            {item.ref_date for item in parsed.coverage if item.admitted}
            == {report_date},
            msg="the cross-section was not admitted at all",
        )
        for series_id, expected in (
            ("mmf_net_assets", 8.0),
            ("mmf_portfolio_securities", 8.0),
            ("mmf_treasury_holdings", 4.0),
            ("mmf_repo_holdings", 2.0),
            ("mmf_on_rrp", 2.0),
        ):
            self.assertEqual(
                sorted(values.get(series_id, {})),
                [report_date],
                msg=f"{series_id} was lost with the absent flow table",
            )
            self.assertAlmostEqual(values[series_id][report_date], expected)

        for series_id in (
            "mmf_gross_subscriptions",
            "mmf_gross_redemptions",
            "mmf_net_flow",
        ):
            self.assertNotIn(
                series_id,
                values,
                msg=f"{series_id} was emitted for an archive that carries no "
                "flow table; an unobserved value has no row, not a zero one",
            )

        # The cost is recorded next to the coverage decision rather than left to
        # be inferred from a row that is not there.
        coverage = {item.ref_date: item for item in parsed.coverage}
        self.assertEqual(
            coverage[report_date].absent_fields,
            ("mmf_gross_redemptions", "mmf_gross_subscriptions", "mmf_net_flow"),
        )

    def test_treasury_holdings_populate_under_the_pre_2016_category_vocabulary(self):
        """The boundary, from the side that would otherwise be silently empty.

        `Treasury Debt` is what the source filed through the 2016-03 report
        month. Matching only `U.S. Treasury Debt` there yields no rows at all for
        `mmf_treasury_holdings` while `mmf_repo_holdings` populates normally,
        because the substring the repo rule matched survived the relabelling and
        the exact string the treasury rule matched did not.
        """

        report_date = date(2013, 1, 31)
        parsed = self._parse(
            nmfp_archive(
                self._submissions("31-JAN-2013"),
                omit=("NMFP_DLYSHAREHOLDERFLOWREPORT.tsv",),
                treasury_category="Treasury Debt",
                repo_category="Treasury Repurchase Agreement",
            ),
            name="era1",
        )

        treasury = {
            row.ref_date: row.value
            for row in parsed.rows
            if row.series_id == "mmf_treasury_holdings"
        }
        repo = {
            row.ref_date: row.value
            for row in parsed.rows
            if row.series_id == "mmf_repo_holdings"
        }
        self.assertEqual(
            sorted(treasury),
            [report_date],
            msg="mmf_treasury_holdings is silently empty in the pre-2016 "
            "vocabulary era while mmf_repo_holdings populates -- the exact "
            "partial balance sheet the era declaration exists to prevent",
        )
        self.assertAlmostEqual(treasury[report_date], 4.0)
        self.assertAlmostEqual(repo[report_date], 2.0)

    def test_a_category_the_era_does_not_declare_raises(self):
        """An unmatched value is a moved vocabulary, not an uninteresting holding.

        Falling through to no row would leave the holdings series short with the
        identity still satisfied and nothing flagged, one layer below the failure
        the era declaration was written for.
        """

        with self.assertRaises(ValueError) as raised:
            self._parse(
                nmfp_archive(
                    self._submissions("31-JAN-2023"),
                    omit=("NMFP_DLYSHAREHOLDERFLOWREPORT.tsv",),
                    treasury_category="Sovereign Wealth Debt",
                ),
                name="undeclared_value",
            )
        self.assertIn("Sovereign Wealth Debt", str(raised.exception))
        self.assertIn("2023-01-31", str(raised.exception))

    def test_a_report_month_in_no_declared_era_costs_only_the_holdings_fields(self):
        """An undeclared era refuses the field, not the archive.

        The last era is bounded by the newest report month the declared archive
        set carries, because the vocabulary is still moving. A report month past
        it has no vocabulary anyone has read, so the categorical fields have no
        observation -- and the balance sheet, which does not depend on the
        categorical at all, is unaffected.
        """

        report_date = date(2005, 6, 30)
        parsed = self._parse(
            nmfp_archive(
                self._submissions("30-JUN-2005"),
                omit=("NMFP_DLYSHAREHOLDERFLOWREPORT.tsv",),
                treasury_category="Whatever Was Filed In 2005",
            ),
            name="undeclared_era",
        )

        series = {row.series_id for row in parsed.rows}
        self.assertIn("mmf_net_assets", series)
        for series_id in (
            "mmf_treasury_holdings",
            "mmf_repo_holdings",
            "mmf_on_rrp",
        ):
            self.assertNotIn(series_id, series)
        coverage = {item.ref_date: item for item in parsed.coverage}
        self.assertEqual(
            coverage[report_date].absent_fields,
            (
                "mmf_gross_redemptions",
                "mmf_gross_subscriptions",
                "mmf_net_flow",
                "mmf_on_rrp",
                "mmf_repo_holdings",
                "mmf_treasury_holdings",
            ),
        )

    def test_the_declared_eras_do_not_overlap_and_classify_each_value_once(self):
        """The declaration is a declaration, not three overlapping guesses."""

        eras = NMFP_INVESTMENT_CATEGORY_ERAS
        self.assertTrue(eras)
        for era in eras:
            self.assertLessEqual(era.start, era.end)
            self.assertEqual(
                len(era.treasury) + len(era.repo) + len(era.excluded),
                len(era.declared),
                msg=f"a category is classified twice in the {era.start} era",
            )
        for earlier, later in zip(eras, eras[1:]):
            self.assertLess(
                earlier.end,
                later.start,
                msg="declared vocabulary eras overlap, so one report month "
                "would be read against two vocabularies",
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


class LegacySourceIdBuildTests(unittest.TestCase):
    """A snapshot that parses must also build.

    `IngestTests.test_legacy_snapshot_source_ids_remain_parseable` proves that
    `observations_from_snapshots` reads a snapshot captured before the registry
    adopted Python-style source IDs. It proves nothing about the builder, and
    the builder was where the archive went to die: `parse_snapshots` normalized
    the IDs through `LEGACY_SOURCE_IDS`, and `build_point_in_time_snapshot`
    then compared the *un-normalized* artifacts against the registry three
    lines later and raised. Every snapshot the repository had archived to that
    point was refused by a check that had never learned the mapping the parser
    beside it applies -- which is the reason Milestone A could not be run at
    all, against snapshots that were sitting on disk and were perfectly good.

    A function with a unit test and no exercised caller is not a working path.

    Mutation record
    ---------------
    Run in a disposable copy under `$HOME` with the full suite, `-B` and
    `PYTHONDONTWRITEBYTECODE=1`. Control was OK (617 tests) before and after.

    | Mutation                                                  | Result     |
    |-----------------------------------------------------------|------------|
    | Exempt legacy IDs from the raise only, leaving `resolved`  | `KeyError` |
    | out of `selected_registry` (the guard-the-raise fix).      |            |
    | Revert the resolution entirely (restore the un-normalized  | ValueError |
    | registry check).                                           |            |

    Each killed both tests in this class and nothing else in the suite; the
    two are one defect seen twice, which is why the exception type is recorded
    rather than the count. The first mutation is the one the block exists for:
    silencing the raise is what a reasonable person writes first, it looks
    like a fix, and it moves the failure one hop down into `selected_registry`
    as a `KeyError` on the legacy ID.
    """

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.output_root = Path(self.directory.name)

    def legacy_artifacts(self):
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
        return [
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

    def test_a_snapshot_with_a_legacy_source_id_builds_rather_than_being_refused(self):
        panel_path = self.output_root / "processed" / "panel.csv"

        panel = build_point_in_time_snapshot(
            self.legacy_artifacts(),
            panel_path,
            created_at=datetime(2026, 1, 6, tzinfo=timezone.utc),
        )

        rows = load_point_in_time_panel(panel_path)
        self.assertEqual(
            {row.series_id for row in rows},
            {"SOFR", "SOFR_volume", "IORB"},
        )
        self.assertEqual(panel.row_count, 3)

    def test_the_manifest_records_the_source_ids_as_they_were_filed(self):
        panel_path = self.output_root / "processed" / "panel.csv"

        build_point_in_time_snapshot(
            self.legacy_artifacts(),
            panel_path,
            created_at=datetime(2026, 1, 6, tzinfo=timezone.utc),
        )

        manifest = json.loads(
            panel_path.with_suffix(".csv.manifest.json").read_text()
        )
        self.assertEqual(
            {item["source_id"] for item in manifest["raw_snapshots"]},
            {"nyfed-sofr-rate", "nyfed-sofr-volume", "fred-macro-latest-vintage"},
        )


class MonthCrossSectionTests(unittest.TestCase):
    """A split month-end is one cross-section, assembled by month.

    A month-end that is not a business day splits the reporting universe across
    two adjacent `REPORTDATE`s: the funds that report as of the last business
    day and the funds that report as of the last calendar day. Measured on the
    archives on disk, 2013-06 files 159 series on the 28th and 473 on the 30th
    -- 632 together, against 629 and 634 in the adjacent complete months.

    Judged a report date at a time, neither half is the universe. Usually only
    the larger clears the coverage floor, so the month is admitted about a
    quarter short; where both cleared it -- 2011-07 and 2011-12 -- the same
    month put *two* partial cross-sections in the panel, and the identity was
    reconciled on each as though it were whole. The alternating identity scale,
    roughly 5,500 against 3,900 USD billions, tracks the split exactly.

    So the assembly unit moves from the report date to the calendar month. The
    cross-section's reference date is the **greatest `REPORTDATE` observed in
    that month**, which is a date the data contains, rather than the calendar
    month-end, which may be a date no filer used. See
    `docs/DATA_QUALITY_DECISIONS.md`, "The split month-end".

    Three things move with the unit, and each has a test here because each is a
    way this change could be made wrong:

    - **Supersession.** `_resolve_nmfp_submissions` keys on (series,
      cross-section). While the cross-section was the report date, a series
      that filed in both halves of a split month was two submissions and both
      were kept; once the halves are one cross-section, keeping both books that
      series' balance sheet twice. The unit the block moves is the unit
      supersession resolves on.
    - **Cell dating.** A balance-sheet cell is dated by the cross-section it was
      filed under and moves with it. A daily shareholder-flow cell is dated by
      the day it describes and does not. Re-dating flows would relabel the flows
      of 28 June as the flows of 30 June, and June 2024 -- the first month with
      a flow table -- is itself a split month, so this is not hypothetical.
    - **The ordinary month.** A month filed under one report date must come out
      exactly as it did. That is `test_a_month_with_one_report_date_is_unchanged`,
      and it is the test that says this block fixed the split case rather than
      changing every case.

    The floor's *value* is untouched -- 200 distinct `SERIESID` in
    `metadata/sources.json`, which this block does not edit. Only the population
    it counts over moved, from a report date's filers to a month's.

    These fixtures are built from in-memory archives rather than from
    `data/raw/`, so they state the structural case rather than depending on a
    particular backfill still containing it. They date themselves into 2016-04
    -- a real split month-end, the 30th being a Saturday -- and into the
    `INVESTMENTCATEGORY` era beginning 2016-04-01, so the holdings tables parse
    rather than being refused for an undeclared vocabulary.

    Mutation record
    ---------------
    Run in a copy under `$HOME` -- never in the mount -- with `data/`,
    `.github/`, `metadata/`, `.gitignore`, the root Markdown and
    `docs/PROJECT_STATUS.md` alongside, `__pycache__` cleared before each run,
    `-B` and PYTHONDONTWRITEBYTECODE=1. Unmutated control run before and after,
    green both times: 628 tests, OK, zero expected failures. A red run is not
    evidence the aimed-at test fired, so every kill is recorded with the
    exception it raised.

    | Mutation                                                   | Result      |
    |------------------------------------------------------------|-------------|
    | 1. `_nmfp_cross_section` returns the report date itself, so | 5 failures  |
    |    assembly is keyed on `REPORTDATE` again.                 |             |
    | 2. The reference date taken as the *earliest* `REPORTDATE`  | 5 failures  |
    |    observed in the month rather than the greatest.          |             |
    | 3. `_nmfp_cross_section` returns a 35-day bucket counted    | 1 failure   |
    |    from a fixed epoch rather than the calendar month.       |             |
    | 4. `_nmfp_cross_section` rewritten to an equivalent key --  | no change   |
    |    `f"{year:04d}-{month:02d}"` for the `(year, month)`      |             |
    |    tuple -- and nothing else touched.                       |             |

    Which tests fired, and with what. Every kill is an `AssertionError`, and
    every one is in this class:

    1. All five of the tests that assert something about a split month:
       `test_a_month_split_across_two_report_dates_is_one_cross_section`
       (`[] is not true : no mmf_net_assets row was emitted at all on
       2016-04-30` -- neither half clears the floor alone, so the month reaches
       the panel as nothing at all),
       `test_the_reference_date_is_the_greatest_report_date_in_the_month`
       (`[] != [datetime.date(2016, 4, 30)]`),
       `test_the_assembled_count_is_distinct_series_and_not_submissions`
       (`2 != 3 : the assembled month counted submissions rather than series`),
       `test_a_daily_flow_keeps_its_own_date_when_its_month_is_assembled`
       (the same empty-panel assertion) and
       `test_two_cross_sections_in_different_months_are_not_merged`
       (`[datetime.date(2016, 5, 31)] != [datetime.date(2016, 4, 30),
       datetime.date(2016, 5, 31)]` -- April is assembled from neither half and
       so is not admitted). This is the defect the block exists for and the
       acceptance test sees it.
    2. The same five. The date-rule kills are the legible ones:
       `test_the_reference_date_is_the_greatest_report_date_in_the_month` gives
       `[datetime.date(2016, 4, 29)] != [datetime.date(2016, 4, 30)]` and
       `test_two_cross_sections_in_different_months_are_not_merged` gives
       `[datetime.date(2016, 4, 29), datetime.date(2016, 5, 31)] !=
       [datetime.date(2016, 4, 30), datetime.date(2016, 5, 31)]`. The date rule
       is defended, which is what this mutation was run to establish.
    3. Only `test_two_cross_sections_in_different_months_are_not_merged`, with
       the same list mismatch as in mutation 1: 30 April and 31 May 2016 fall in
       one 35-day bucket, so the second month is swallowed by the first. It does
       **not** kill the acceptance test, and that is correct rather than a gap:
       within a single month a bucket and a calendar month agree, so no
       one-month fixture can distinguish them. That is precisely why the
       not-merged companion exists.
    4. Nothing changed. The month key is a value, not a shape, and rewriting it
       to an equivalent must not move a single test.

    One test in this class was killed by none of the four:
    `test_a_month_with_one_report_date_is_unchanged`. That is not a hole, it is
    what the test is for. All four mutations change how the *split* case
    assembles, and on a month filed under one report date every one of them --
    the report date, the earliest, the greatest, a 35-day bucket -- names the
    same cross-section and the same reference date, because assembly has nothing
    to do there. The test would fire on a mutation that moved the ordinary
    month, and its value is that it is standing by when someone writes one.
    """

    #: 2016-04-30 was a Saturday, so April 2016 is a real split month-end: the
    #: funds that report as of the last business day file the 29th and the rest
    #: file the 30th. The month is also inside the `INVESTMENTCATEGORY` era
    #: beginning 2016-04-01, so the fixtures' category strings are declared.
    BUSINESS_DAY = "29-APR-2016"
    CALENDAR_DAY = "30-APR-2016"
    REF_DATE = date(2016, 4, 30)
    EARLIER_HALF = date(2016, 4, 29)

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.output_root = Path(self.directory.name)

    @staticmethod
    def _submission(accession, series, report, billions, filing="10-MAY-2016", **extra):
        entry = {
            "accession": accession,
            "series": series,
            "report": report,
            "filing": filing,
            "submission_type": "N-MFP3",
            "net_assets": billions * 1_000_000_000,
        }
        entry.update(extra)
        return entry

    def _archive(self, name, submissions, retrieved_at, **kwargs):
        artifact = fetch_sec_nmfp(
            self.output_root / name,
            f"https://www.sec.gov/files/dera/data/form-n-mfp-data-sets/{name}.zip",
            lambda url: nmfp_archive(submissions, **kwargs),
        )[0]
        return replace(artifact, retrieved_at=retrieved_at)

    def _value(self, parsed, series_id, ref_date):
        """The latest vintage of one series on one reference date."""

        rows = [
            row
            for row in parsed.rows
            if row.series_id == series_id and row.ref_date == ref_date
        ]
        self.assertTrue(
            rows, f"no {series_id} row was emitted at all on {ref_date.isoformat()}"
        )
        return max(rows, key=lambda row: row.available_at).value

    def _admitted(self, parsed):
        """The reference dates the coverage floor admitted, in date order."""

        return sorted(
            {item.ref_date for item in parsed.coverage if item.admitted}
        )

    def _section(self, parsed, ref_date):
        """The last coverage record for one reference date.

        Asserted rather than indexed, so a mutation that stops a cross-section
        being assembled at all reports which date went missing instead of an
        `IndexError` on an empty list.
        """

        found = [item for item in parsed.coverage if item.ref_date == ref_date]
        self.assertTrue(
            found, f"no cross-section was recorded at {ref_date.isoformat()}"
        )
        return found[-1]

    def test_a_month_split_across_two_report_dates_is_one_cross_section(self):
        """The acceptance criterion. Fails against per-report-date assembly.

        Two disjoint halves of one April: two series file as of Friday the 29th
        and two as of Saturday the 30th. Against a floor of three, neither half
        is a cross-section and the month reaches the panel as nothing at all --
        not as a small cross-section, as no rows. Assembled by month it is four
        series, dated the 30th, and admitted.
        """

        archive = self._archive(
            "split",
            [
                self._submission("0000000000-16-000001", "S000000001", self.BUSINESS_DAY, 1),
                self._submission("0000000000-16-000002", "S000000002", self.BUSINESS_DAY, 2),
                self._submission("0000000000-16-000003", "S000000003", self.CALENDAR_DAY, 3),
                self._submission("0000000000-16-000004", "S000000004", self.CALENDAR_DAY, 4),
            ],
            "2026-03-01T00:00:00+00:00",
        )

        parsed = parse_snapshots(
            [archive],
            registry_path=registry_with_nmfp_coverage_floor(self.output_root, 3),
        )

        self.assertEqual(
            self._value(parsed, "mmf_net_assets", self.REF_DATE),
            10.0,
            msg="the halves of a split month-end were not assembled into one "
            "cross-section",
        )
        self.assertEqual(self._admitted(parsed), [self.REF_DATE])
        section = self._section(parsed, self.REF_DATE)
        self.assertEqual(section.entity_count, 4)
        self.assertTrue(section.admitted)

    def test_the_reference_date_is_the_greatest_report_date_in_the_month(self):
        """Dated by a date the data contains, chosen by a rule.

        Not the calendar month-end, which in a month whose last day is a Sunday
        is a date no filer used, and not the earliest, which would date the
        whole universe to the half that filed first. The earlier half must not
        survive as a reference date of its own: that is the two-partial-
        cross-sections shape the decision exists to remove.
        """

        archive = self._archive(
            "dated",
            [
                self._submission("0000000000-16-000001", "S000000001", self.BUSINESS_DAY, 1),
                self._submission("0000000000-16-000002", "S000000002", self.BUSINESS_DAY, 2),
                self._submission("0000000000-16-000003", "S000000003", self.CALENDAR_DAY, 3),
            ],
            "2026-03-01T00:00:00+00:00",
        )

        parsed = parse_snapshots(
            [archive],
            registry_path=registry_with_nmfp_coverage_floor(self.output_root, 3),
        )

        self.assertEqual(self._admitted(parsed), [self.REF_DATE])
        self.assertEqual(
            [item.ref_date for item in parsed.coverage],
            [self.REF_DATE],
            msg="the earlier half of the split survived as its own cross-section",
        )
        self.assertEqual(
            [row.ref_date for row in parsed.rows if row.series_id == "mmf_net_assets"],
            [self.REF_DATE],
        )

    def test_two_cross_sections_in_different_months_are_not_merged(self):
        """Assemble by month, not by proximity -- the obvious way to overshoot.

        April 2016 is split across the 29th and the 30th; May 2016 is not split.
        The last report date of April and the only one of May are 31 days apart,
        so any rule that gathers report dates within a window wide enough to
        catch a split month-end also merges two adjacent months. The calendar
        month does not, and that is the difference this test holds.
        """

        archive = self._archive(
            "adjacent",
            [
                self._submission("0000000000-16-000001", "S000000001", self.BUSINESS_DAY, 1),
                self._submission("0000000000-16-000002", "S000000002", self.CALENDAR_DAY, 2),
                self._submission("0000000000-16-000003", "S000000003", self.CALENDAR_DAY, 3),
                self._submission(
                    "0000000000-16-000011", "S000000001", "31-MAY-2016", 10,
                    filing="10-JUN-2016",
                ),
                self._submission(
                    "0000000000-16-000012", "S000000002", "31-MAY-2016", 5,
                    filing="10-JUN-2016",
                ),
                self._submission(
                    "0000000000-16-000013", "S000000003", "31-MAY-2016", 16,
                    filing="10-JUN-2016",
                ),
            ],
            "2026-03-01T00:00:00+00:00",
        )

        parsed = parse_snapshots(
            [archive],
            registry_path=registry_with_nmfp_coverage_floor(self.output_root, 3),
        )

        self.assertEqual(
            self._admitted(parsed), [self.REF_DATE, date(2016, 5, 31)]
        )
        self.assertEqual(self._value(parsed, "mmf_net_assets", self.REF_DATE), 6.0)
        self.assertEqual(
            self._value(parsed, "mmf_net_assets", date(2016, 5, 31)), 31.0
        )

    def test_the_assembled_count_is_distinct_series_and_not_submissions(self):
        """A filer in both halves is one filer, counted once and valued once.

        `S000000001` files as of the 29th and again as of the 30th. Counted by
        submission the month is four filings; counted by reporting entity it is
        three series, which is what the floor is declared in. The value follows
        the same unit: the two filings are one series' account of one
        cross-section, so the later-filed one supersedes the earlier rather than
        being added to it. Adding them is the double-booking
        `_resolve_nmfp_submissions` exists to prevent, one assembly unit up --
        and it is a defect this block would introduce, because while the
        cross-section was the report date the two filings were not the same
        cross-section at all.
        """

        archive = self._archive(
            "repeat-filer",
            [
                self._submission(
                    "0000000000-16-000001", "S000000001", self.BUSINESS_DAY, 1,
                    filing="10-MAY-2016",
                ),
                self._submission(
                    "0000000000-16-000009", "S000000001", self.CALENDAR_DAY, 100,
                    filing="12-MAY-2016",
                ),
                self._submission("0000000000-16-000002", "S000000002", self.BUSINESS_DAY, 2),
                self._submission("0000000000-16-000003", "S000000003", self.CALENDAR_DAY, 3),
            ],
            "2026-03-01T00:00:00+00:00",
        )

        parsed = parse_snapshots(
            [archive],
            registry_path=registry_with_nmfp_coverage_floor(self.output_root, 3),
        )

        section = self._section(parsed, self.REF_DATE)
        self.assertEqual(
            section.entity_count,
            3,
            msg="the assembled month counted submissions rather than series",
        )
        # 100 + 2 + 3. 106.0 would mean both of S000000001's filings were
        # booked into the month it filed them for.
        self.assertEqual(
            self._value(parsed, "mmf_net_assets", self.REF_DATE),
            105.0,
            msg="a series that filed in both halves was booked twice",
        )

    def test_a_daily_flow_keeps_its_own_date_when_its_month_is_assembled(self):
        """Balance cells move with the cross-section; flow cells do not.

        A balance-sheet cell is dated by the cross-section it was filed under,
        so assembling the month re-dates it. A daily shareholder-flow cell is
        dated by the day whose flows it reports, and that day does not move
        because the month it was filed in was assembled. June 2024 -- the first
        report month with a flow table at all -- ends on a Sunday and is
        therefore itself a split month, so re-dating the earlier half's flows
        onto the later half's date is a defect that would land on the very first
        month the table exists for.
        """

        archive = self._archive(
            "flows",
            [
                self._submission(
                    "0000000000-16-000001", "S000000001", self.BUSINESS_DAY, 1,
                    flows=(("28-APR-2016", 7_000_000_000, 3_000_000_000),),
                ),
                self._submission("0000000000-16-000002", "S000000002", self.BUSINESS_DAY, 2),
                self._submission("0000000000-16-000003", "S000000003", self.CALENDAR_DAY, 3),
            ],
            "2026-03-01T00:00:00+00:00",
        )

        parsed = parse_snapshots(
            [archive],
            registry_path=registry_with_nmfp_coverage_floor(self.output_root, 3),
        )

        # The balance sheet is dated by the assembled month.
        self.assertEqual(self._value(parsed, "mmf_net_assets", self.REF_DATE), 6.0)
        # The flows are dated by the day they describe.
        self.assertEqual(
            self._value(parsed, "mmf_net_flow", date(2016, 4, 28)), 4.0
        )
        self.assertEqual(
            [row.ref_date for row in parsed.rows if row.series_id == "mmf_net_flow"],
            [date(2016, 4, 28)],
            msg="a daily flow was re-dated onto the assembled month's reference date",
        )

    def test_a_month_with_one_report_date_is_unchanged(self):
        """The ordinary case, which this block must leave exactly alone.

        Almost every month-end is a business day and files under one report
        date. Assembling by month has nothing to do there, and the cross-section
        must come out with the same reference date, the same entity count and
        the same values it had before. A block that fixes the split month by
        changing every month has not fixed the split month.
        """

        archive = self._archive(
            "ordinary",
            [
                self._submission(
                    "0000000000-16-000011", "S000000001", "31-MAY-2016", 10,
                    filing="10-JUN-2016",
                ),
                self._submission(
                    "0000000000-16-000012", "S000000002", "31-MAY-2016", 5,
                    filing="10-JUN-2016",
                ),
                self._submission(
                    "0000000000-16-000013", "S000000003", "31-MAY-2016", 16,
                    filing="10-JUN-2016",
                ),
            ],
            "2026-03-01T00:00:00+00:00",
        )

        parsed = parse_snapshots(
            [archive],
            registry_path=registry_with_nmfp_coverage_floor(self.output_root, 3),
        )

        self.assertEqual(self._admitted(parsed), [date(2016, 5, 31)])
        self.assertEqual(
            self._value(parsed, "mmf_net_assets", date(2016, 5, 31)), 31.0
        )
        section = self._section(parsed, date(2016, 5, 31))
        self.assertEqual(section.entity_count, 3)
        self.assertEqual(section.declared_floor, 3)


if __name__ == "__main__":
    unittest.main()
