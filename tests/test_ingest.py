import csv
import hashlib
from dataclasses import replace
from datetime import date, datetime, time, timedelta, timezone
import gzip
import io
import json
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from repo_model.data import (
    DERIVED_ABSENCE_DECLARED_ZERO,
    DERIVED_ABSENCE_UNDECLARED,
    EXCLUSION_BELOW_FLOOR,
    EXCLUSION_NO_REPO_ROWS,
    EXCLUSION_REASONS,
    CrossSectionCoverage,
    IDENTITY_HELD,
    IDENTITY_HELD_WHERE_EVALUABLE,
    absent_cells_from_quality_report,
    declared_coverage_floor,
    load_point_in_time_panel,
    validate_accounting_identities,
)
from repo_model.ingest import (
    ArchiveRecord,
    ArchiveRefusal,
    FR2004_SOURCE_ID,
    NMFP_CATEGORY_FIELDS,
    NMFP_DERIVED_FROM_MATCH,
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
    """The real registry with only `sec_nmfp`'s declared coverage floors changed.

    A fixture cross-section is a handful of rows, so exercising the production
    floors -- hundreds of reporting series -- would mean fabricating a universe
    before any assertion could be made. Overriding the number keeps every other
    declaration -- `entity_unit` and the era bounds above all -- exactly the
    shape the adapter reads in production, so a registry that drifts still
    breaks these tests.

    Every declared era gets the same floor, deliberately. A fixture that lowered
    one era's floor would be admitted or refused according to which era its
    invented `REPORTDATE` happened to land in, and a test that changes verdict
    because someone moved a fixture date by a month is testing the calendar.
    Tests about the eras themselves declare their own registry rather than
    calling this.
    """

    registry = json.loads(SOURCE_REGISTRY.read_text(encoding="utf-8"))
    for era in registry["sec_nmfp"]["cross_section"]["eras"]:
        era["minimum_reporting_entities"] = floor
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

#: The three counterparty columns a repo holding files, and what every fixture
#: has always put in them: a Federal Reserve counterparty, which the `mmf_on_rrp`
#: derivation matches. Named here so a fixture can file a repo row the derivation
#: does *not* match without restating the columns, and so the default stays one
#: literal rather than one per call site.
FIXTURE_FED_COUNTERPARTY = ("Federal Reserve Bank of New York", "Reverse repo", "")

#: A repo counterparty with no `FEDERAL RESERVE` anywhere in any of the three
#: joined columns. A dealer name, because that is what the other 9,000-odd repo
#: rows in the real extract carry; the point of the fixture is that the row is
#: entirely ordinary and simply is not the facility.
FIXTURE_DEALER_COUNTERPARTY = (
    "Barclays Capital Inc.",
    "Tri-party repurchase agreement",
    "Collateralized by U.S. Treasuries",
)
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

    A submission may also override `repo_counterparty`, the
    `(NAMEOFISSUER, TITLEOFISSUER, BRIEFDESCRIPTION)` triple its repo holding
    files, which is what the `mmf_on_rrp` derivation matches `FEDERAL RESERVE`
    against. It defaults to `FIXTURE_FED_COUNTERPARTY`, the literal every fixture
    has always filed, so absent the key the row is byte-for-byte what it always
    was and no existing fixture moves -- the same posture `other_assets` takes one
    field up. It exists because every fixture in this module matched the facility,
    so the case where a repo row is present and readable and simply is not the Fed
    was unreachable.
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
        issuer, title, brief = entry.get(
            "repo_counterparty", FIXTURE_FED_COUNTERPARTY
        )
        holding_rows.append(
            f"{entry['accession']}\t{repo_category}\t{net // 4}\t"
            f"{issuer}\t{title}\t{brief}"
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
        """The aggregate, its two public legs and SOMA, through the whole hop.

        The records carry `auction_date` and `security_type` because the
        adapter now requires them: an unclassifiable record would otherwise
        reach the aggregate and no component, and the identity would fail
        somewhere far from the record that broke it. `record_date` before
        `issue_date` is the announcement-dated shape, which the real snapshot
        does not have, so it is kept here.
        """

        payload = json.dumps(
            {
                "data": [
                    {
                        "issue_date": "2026-01-15",
                        "record_date": "2026-01-10",
                        "auction_date": "2026-01-08",
                        "security_type": "Bill",
                        "offering_amt": "50000000000",
                        "soma_accepted": "1000000000",
                    },
                    {
                        "issue_date": "2026-01-15",
                        "record_date": "2026-01-10",
                        "auction_date": "2026-01-08",
                        "security_type": "Note",
                        "offering_amt": "25000000000",
                        "soma_accepted": "0",
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
        values = {row.series_id: row.value for row in rows}
        self.assertEqual(
            values,
            {
                "treasury_settlement": 75.0,
                "treasury_settlement_bill": 50.0,
                "treasury_settlement_coupon": 25.0,
                "treasury_settlement_soma": 1.0,
            },
        )
        self.assertEqual(rows[0].series_id, "treasury_settlement")
        for row in rows:
            self.assertLess(row.available_at.date(), row.ref_date)

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

    The single `minimum_reporting_entities` named in item 4 was replaced by a
    per-era declaration in a later block -- see `CoverageEraTests`. The record
    above is left as it was run rather than restated, because it is the account
    of an experiment on the tree as it then stood; only this note is new.
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

        The registry's *coverage* eras are widened here so that this test asks
        only its own question. Those are a second era vocabulary, bounded for
        their own reasons, and a `ref_date` outside them is refused outright --
        see `CoverageEraTests`. The two vocabularies currently share their
        bounds, so without this widening the archive would be refused for
        having no declared floor and the rule under test here would never be
        reached. That is a real interaction and it is asserted, in
        `test_an_undeclared_coverage_era_refuses_before_the_category_era_can_cost_fields`;
        what it must not do is quietly stand in for this rule.
        """

        report_date = date(2005, 6, 30)
        registry = json.loads(json.dumps(self.registry))
        registry["sec_nmfp"]["cross_section"]["eras"][0]["start"] = "2005-01"
        artifact = fetch_sec_nmfp(
            self.output_root,
            "https://www.sec.gov/files/dera/data/form-n-mfp-data-sets/undeclared_era.zip",
            lambda url: nmfp_archive(
                self._submissions("30-JUN-2005"),
                omit=("NMFP_DLYSHAREHOLDERFLOWREPORT.tsv",),
                treasury_category="Whatever Was Filed In 2005",
            ),
        )[0]
        parsed = parse_snapshots([artifact], registry=registry)

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
    | (That single key is now a per-era declaration; the row   |              |
    | records the run as it was made.)                         |              |
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



class DerivedFieldAbsenceTests(unittest.TestCase):
    """A derived field that matched nothing in a table it read is absent, not missing.

    Two kinds of absence were already recorded and neither is this one.
    `REFUSAL_ABSENT_FIELDS` says the table is not in the archive, so every panel
    field that table supplies has no observation.
    `CrossSectionCoverage.absent_fields` says the archive could supply no
    observation of a field for a cross-section -- the table is absent, or the
    report month has no declared `INVESTMENTCATEGORY` vocabulary to read it with.

    `mmf_on_rrp` has a third way to be absent that neither covers.
    `NMFP_SCHPORTFOLIOSECURITIES.tsv` is present, readable and parsed; its
    repo-category rows produce `mmf_repo_holdings` for the cross-section; and the
    counterparty match finds no `FEDERAL RESERVE` in any of them. No row is
    emitted, and until this class nothing recorded that the derivation had run, so
    a month in which money funds lent nothing to the facility read exactly like a
    month the adapter never looked at. In the declared archive set that is 33 repo
    months, 32 of which precede the facility and one -- 2026-07-31, sitting on the
    `n_mfp3` era bound, the month after one reporting 6.8 bn -- does not.

    **The zero is the trap, not the gap.** Coercing the absent field to `0.0`
    would close the recording gap in the one direction that makes the panel worse:
    an emitted zero is an observation, every downstream check accepts it, and the
    distinction the structural-zero declaration exists to preserve is destroyed
    at the point of ingest. So `unmatched_derived_fields` records that the
    derivation ran and matched nothing, and the rows stay as they were: absent.

    **This class does not decide which kind of absence any month is.** That is a
    review, recorded by a human in `metadata/sources.json` under
    `structural_zeros` with `structural_zeros_reviewed`. What the code decides is
    the disposition: whether a declaration covers the month in hand, which is the
    difference between "these funds held none" and "we never found it". `test_a_declared_structural_zero_changes_the_disposition` is what
    makes that read load-bearing rather than decorative -- it is the first thing
    in this package to read `structural_zeros`, which was declared, shape-checked
    and never consulted.

    **A declaration covers a period, and "declared at all" was the wrong
    question.** `when` stays the reviewer's prose and is still required, but a
    declaration now also carries `through` (required, inclusive) and may carry
    `from`, and the disposition is decided against the cross-section's own
    ref_date. The 33 months above are why: the review this class waits on will
    declare the 32 pre-facility months structurally zero, and a disposition
    that answered "declared at all" would extend that reviewer's statement
    over 2026-07-31 as well -- the one month of the 33 where the facility
    existed, and so the only one where "these funds held none" is a claim
    nobody has made. `test_a_declaration_does_not_reach_past_its_period` is
    that case. Outside a declared period the record reads `no_declaration`,
    which is literally true of that month.

    Mutation record
    ---------------

    Run in a disposable copy under `$HOME` -- never in the mount -- built by
    copying the whole tree minus `.git`, which is a strict superset of the list
    `CLAUDE.md` names (`data/`, `.github/`, `.claude/`, `metadata/`,
    `.gitignore`, the root Markdown, `docs/PROJECT_STATUS.md`) and so cannot be
    short again the way that list was for three rounds. `python3 -B` with
    `PYTHONDONTWRITEBYTECODE=1`, on **3.9.6**. Unmutated control green before and
    after all five -- 702 tests OK zero expectedFailure before this class, 708
    after it -- and each mutation applied to a freshly restored copy rather than
    on top of the last. Every kill below is an `AssertionError`; no mutation
    produced an incidental exception, and none produced an error rather than a
    failure.

    Recorded as run, not as predicted: the draft of this record guessed the kills
    and was wrong about three of the five. 1 and 2 each kill more than the one
    test claimed for them, and 5 kills a test in a different class from the one
    named. The measured results are below.

    1. **The zero written instead of the record.** An
       `add(accession, "mmf_on_rrp", section, 0.0, ...)` in the `else` of the
       `FEDERAL RESERVE` match -- the trap this block exists to refuse,
       implemented. Kills **four**, all `AssertionError` (**three** when first
       run; re-run below on the period commit, where it also kills the new
       acceptance test):
       `test_a_derived_field_with_no_match_in_a_read_table_is_recorded_absent_not_omitted`
       (the acceptance test and the mutation target) on
       `'mmf_on_rrp' unexpectedly found in {...}`, and
       `test_a_declared_structural_zero_changes_the_disposition`,
       `test_an_excluded_cross_section_still_carries_the_record` and
       `test_a_declaration_does_not_reach_past_its_period` on
       `() != (('mmf_on_rrp', ...),)`. The last three are the informative part: an
       emitted zero does not merely add a row, it *erases the record*, because a
       field that is observed is by definition not one the derivation missed. The
       zero and the record cannot coexist, which is the strongest available
       statement that this block closed the gap in the right direction.
    2. **The input condition dropped**: `base not in observed` removed from
       `_nmfp_unmatched_derived_fields`. Kills **two**, both `AssertionError`:
       `test_an_absent_table_is_not_an_unmatched_derivation` on
       `(('mmf_on_rrp', 'no_declaration'),) != ()` and
       `test_an_undeclared_era_is_not_an_unmatched_derivation` on
       `'mmf_on_rrp' unexpectedly found in ['mmf_on_rrp']`. Both of the first two
       kinds of absence start reporting themselves as the third one, which is
       what makes this the mutation that proves the three are disjoint by
       construction rather than by a rule someone has to remember.
    3. **The output condition dropped**: `derived in observed` removed, so a
       cross-section that *did* match the facility is recorded as having matched
       nothing beside the row proving it did. Kills
       `test_a_matched_derivation_records_no_absence`, `AssertionError`,
       `(('mmf_on_rrp', 'no_declaration'),) != ()`.
    4. **The registry read discarded**: `declared_structural_zeros` still called
       and its result replaced with `{}` at the call site, so every disposition is
       `no_declaration`. Kills **two**, both `AssertionError` (**one** when first
       run; re-run below on the period commit):
       `test_a_declared_structural_zero_changes_the_disposition` and
       `test_a_declaration_does_not_reach_past_its_period`, each on
       `(('mmf_on_rrp', 'no_declaration'),) != (('mmf_on_rrp', 'declared_structural_zero'),)`
       -- the second on the half of that test where the declaration *does* cover
       the cross-section. This is the mutation that proves the declaration is
       *read* rather than mentioned, which is the second clause of the published
       limitation's predicate and the only clause an agent can satisfy -- see the
       sixth run below.
    5. **The era case collapsed**: the `undeclared` branch in
       `_nmfp_archive_scan` made to fall through instead of costing
       `NMFP_CATEGORY_FIELDS`. Kills **two**, both `AssertionError`:
       `test_an_undeclared_era_is_not_an_unmatched_derivation` on
       `'mmf_on_rrp' not found in ()`, and
       `PerTableRefusalTests::test_a_report_month_in_no_declared_era_costs_only_the_holdings_fields`
       on the three holdings fields vanishing from `absent_fields`. That second
       one is not the test the draft predicted and it is the better witness: the
       fourth trap in the brief is that a vocabulary which does not declare the
       category is not a vocabulary that declares it and matched nothing, and the
       pre-existing guard on the era case fires alongside the new one rather than
       being replaced by it.

    A sixth run, which is a finding rather than a mutation of this block's code.
    A structural zero for `mmf_on_rrp` added to `metadata/sources.json` with
    `structural_zeros_reviewed` left `false`, to establish what it takes to
    satisfy the *first* clause of `nmfp_absence_indistinguishable`. Three
    failures: `test_source_registry_declares_identities_and_structural_zeros`
    twice (the subTest and the outer test), because
    `tests/test_contract.py` requires an unreviewed source's `structural_zeros` to
    be `[]`, and `test_no_published_limitation_outlives_its_repair`. So the first
    clause cannot be landed without `structural_zeros_reviewed: true`, which is a
    human's field and a stop-and-report for this block -- and the limitation guard
    fires the moment a reviewer lands it, on the strength of the read this block
    added. See the report for the consequence: this block does **not** turn the
    suite red, contrary to the brief that asked for it.

    Mutation record: the declared period
    ------------------------------------

    The block that gave a declaration a `through` and a `from`, and decided the
    disposition against the cross-section's own ref_date. Same protocol: a
    disposable copy under `$HOME` built by copying the whole tree minus `.git`,
    `python3 -B` with `PYTHONDONTWRITEBYTECODE=1`, on **3.9.6**, each mutation
    applied to a freshly restored copy. Unmutated control green before and
    after -- 743 tests OK, zero `expectedFailure`, both runs.

    7. **The period comparison dropped** (the required mutation): `covers`
       removed from the disposition in `_nmfp_unmatched_derived_fields`, so a
       declared field reads `declared_structural_zero` whatever month it is.
       Kills `test_a_declaration_does_not_reach_past_its_period` **alone**,
       `AssertionError`,
       `(('mmf_on_rrp', 'declared_structural_zero'),) != (('mmf_on_rrp', 'no_declaration'),)`
       on the first half. That it kills exactly one test is the point: this is
       the whole of the difference between "declared at all" and "declared for
       this month", and nothing else in the suite could tell the two apart.
       Mutations 1 and 4 above were re-run on this tree because the fixture
       they name changed: the declaration in
       `test_a_declared_structural_zero_changes_the_disposition` was prose with
       no `through`, which is now refused, so it was given a period covering
       `REF_DATE`. Both kill strictly more than they did, and their entries
       above are updated in place rather than restated here.

    8. **The `through` requirement removed**, which is a **finding and not a
       kill**. A declaration with no `through` made to mean unbounded above
       (`last = date.max`) instead of raising `DataContractError`. Kills
       **nothing**: 743 tests OK. So the three refusals the grammar added to
       `declared_structural_zeros` -- no `through`, an unparseable bound,
       `from` later than `through` -- were unguarded when this was run. They
       are real refusals and they run, but no test asserted any of them, and
       the first is exactly the declaration that would silently annex every
       month the source has not reached. Recorded here rather than repaired: a
       test for them is a second acceptance criterion, which is a block and
       not a patch.

       **Repaired at the block after next**, where it belonged: with
       `declared_structural_zeros` in `tests/test_data.py`, which at the time
       of this run tested nothing about structural zeros at all.
       `StructuralZeroPeriodGrammarTests` there now asserts each of the three
       against the phrase only that refusal writes, and its own record carries
       the three mutations. This one is the reason the guard had to be written
       that way: with the `through` requirement made a no-op, the entry is
       still refused by `_structural_zero_bound` behind it, so the refusal is
       killable only by its message and never by "DataContractError not
       raised".
    """

    #: Three filers over the floor, none of whose repo rows is the facility. The
    #: month is otherwise entirely ordinary: the holdings table is present, both
    #: categories parse, and `mmf_repo_holdings` is observed from the very rows
    #: the derivation matches over and misses.
    #:
    #: The flow rows are there so the fixture is a month and not the minimum the
    #: parser accepts: `build_point_in_time_snapshot` refuses a panel on which a
    #: declared identity has no complete reference date, so without them the
    #: record could not be followed as far as the published quality report, which
    #: is where a reader actually meets it.
    DEALER_ONLY = tuple(
        {
            "accession": f"D{index}",
            "series": f"S{index}",
            "report": "31-JUL-2026",
            "net_assets": 4_000_000_000,
            "repo_counterparty": FIXTURE_DEALER_COUNTERPARTY,
            "flows": ((f"0{index}-JUL-2026", 100_000_000 * index, 40_000_000 * index),),
        }
        for index in (1, 2, 3)
    )

    FLOOR = 3
    REF_DATE = date(2026, 7, 31)

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.output_root = Path(self.directory.name)

    def archive(self, submissions, **kwargs):
        """One fetched fixture artifact, named so each test reads as its own case."""

        return fetch_sec_nmfp(
            self.output_root,
            "https://www.sec.gov/files/dera/data/form-n-mfp-data-sets/fixture.zip",
            lambda url: nmfp_archive(submissions, **kwargs),
        )[0]

    def registry(self, *, structural_zeros=()):
        """The real registry with the floors lowered and `structural_zeros` stated.

        The declarations go in a temporary copy and never in
        `metadata/sources.json`. Which months are structurally zero is a review a
        human records there, with `structural_zeros_reviewed`; what a fixture needs
        is a source that declares one so the disposition can be *observed*, which
        is a different thing from asserting that any real month is one.

        **`sec_nmfp`'s declarations are overwritten either way, including with the
        empty list.** `registry_with_nmfp_coverage_floor` copies the real registry,
        so a declaration landed in `metadata/sources.json` -- which is exactly what
        the pending review of the 33 absent repo months would land -- would
        otherwise reach these fixtures and flip the disposition under every test
        here that asserts the undeclared one. A test that changes verdict because
        someone recorded a review is testing the review, which is the defect that
        helper's own docstring refuses one field over. So the premise is written
        down rather than inherited.

        `structural_zeros_reviewed` is set to match, because
        `tests/test_contract.py` requires an unreviewed source's declarations to be
        empty -- and that coupling is the reason no agent can satisfy the published
        limitation's first clause on its own.
        """

        path = registry_with_nmfp_coverage_floor(self.output_root, self.FLOOR)
        registry = json.loads(path.read_text(encoding="utf-8"))
        registry["sec_nmfp"]["structural_zeros"] = list(structural_zeros)
        registry["sec_nmfp"]["structural_zeros_reviewed"] = bool(structural_zeros)
        if structural_zeros:
            registry["sec_nmfp"]["reviewed_note"] = "fixture declaration"
        path.write_text(
            json.dumps(registry, indent=2, sort_keys=True), encoding="utf-8"
        )
        return registry

    def coverage_for(self, parsed, ref_date):
        records = [item for item in parsed.coverage if item.ref_date == ref_date]
        self.assertEqual(
            len(records), 1, msg=f"expected exactly one coverage record for {ref_date}"
        )
        return records[0]

    def test_a_derived_field_with_no_match_in_a_read_table_is_recorded_absent_not_omitted(self):
        artifact = self.archive(self.DEALER_ONLY)
        parsed = parse_snapshots([artifact], registry=self.registry())
        record = self.coverage_for(parsed, self.REF_DATE)

        # The premise: the table was read and its repo rows were counted. Without
        # this the rest of the test would pass on a cross-section nobody parsed.
        self.assertTrue(record.admitted)
        observed = {row.series_id for row in parsed.rows if row.ref_date == self.REF_DATE}
        self.assertIn("mmf_repo_holdings", observed)

        # The finding: no row for the derived field. Not a zero one -- a zero is
        # an observation, and coercing the absent field to one is the trap.
        self.assertNotIn("mmf_on_rrp", observed)
        self.assertEqual(
            [row.value for row in parsed.rows if row.series_id == "mmf_on_rrp"],
            [],
            msg="a 0.0 row was emitted for a derived field that matched nothing",
        )

        # The record, and the disposition: declared nowhere, so "we never found
        # it" and not "they held none".
        self.assertEqual(
            record.unmatched_derived_fields,
            (("mmf_on_rrp", DERIVED_ABSENCE_UNDECLARED),),
        )

        # Distinguishable from the second kind: `absent_fields` is what the
        # archive could supply no observation of, and this archive could have --
        # it read the table and the rows.
        self.assertNotIn("mmf_on_rrp", record.absent_fields)

        # Distinguishable from the first kind: the schema refusal path reports no
        # absent table, because the table is present. Read from the payload rather
        # than restated, so a fixture that stopped writing the table would fail
        # here instead of quietly agreeing.
        refusals = nmfp_schema_refusals(artifact.path.read_bytes())
        self.assertEqual(
            [item for item in refusals if item.kind == REFUSAL_ABSENT_FIELDS], []
        )

        # And it survives the round trip into the published quality report, which
        # is where a reader meets it.
        panel_path = self.output_root / "panel.csv"
        build_point_in_time_snapshot(
            [artifact],
            panel_path,
            registry_path=self.output_root / "sources.json",
        )
        self.assertEqual(
            [row for row in panel_path.read_text(encoding="utf-8").splitlines()
             if "mmf_on_rrp" in row],
            [],
            msg="the panel carries an mmf_on_rrp row for a month that matched nothing",
        )

    def test_a_matched_derivation_records_no_absence(self):
        """A cross-section that found the facility has an observation, not a record."""

        matched = tuple(dict(entry) for entry in self.DEALER_ONLY)
        for entry in matched:
            del entry["repo_counterparty"]
        parsed = parse_snapshots([self.archive(matched)], registry=self.registry())
        record = self.coverage_for(parsed, self.REF_DATE)

        self.assertEqual(record.unmatched_derived_fields, ())
        self.assertIn(
            "mmf_on_rrp",
            {row.series_id for row in parsed.rows if row.ref_date == self.REF_DATE},
        )

    def test_an_absent_table_is_not_an_unmatched_derivation(self):
        """The first kind stays the first kind: no rows to match means no record.

        The holdings table is gone, so `mmf_on_rrp` has no observation *and* no
        derivation ran. Recording it as an unmatched derivation would claim the
        adapter looked at rows that are not in the archive.
        """

        artifact = self.archive(
            self.DEALER_ONLY, omit=("NMFP_SCHPORTFOLIOSECURITIES.tsv",)
        )
        parsed = parse_snapshots([artifact], registry=self.registry())
        record = self.coverage_for(parsed, self.REF_DATE)

        self.assertIn("mmf_on_rrp", record.absent_fields)
        self.assertIn("mmf_repo_holdings", record.absent_fields)
        self.assertEqual(record.unmatched_derived_fields, ())

    def test_an_undeclared_era_is_not_an_unmatched_derivation(self):
        """The fourth trap: no declared vocabulary is not a vocabulary that missed.

        A report month in no declared `INVESTMENTCATEGORY` era costs
        `NMFP_CATEGORY_FIELDS` and reads no holdings row at all. The category the
        derivation needs is not declared for that month, so "it matched nothing"
        would be a claim about a match that never ran.
        """

        before_any_declared_era = tuple(
            dict(entry, report="31-JUL-2010", accession=f"E{index}")
            for index, entry in enumerate(self.DEALER_ONLY, start=1)
        )
        parsed = parse_snapshots(
            [self.archive(before_any_declared_era)], registry=self.registry()
        )
        record = self.coverage_for(parsed, date(2010, 7, 31))

        for field in NMFP_DERIVED_FROM_MATCH:
            self.assertIn(field, record.absent_fields)
            self.assertNotIn(
                field,
                [name for name, _disposition in record.unmatched_derived_fields],
            )

    def test_a_declared_structural_zero_changes_the_disposition(self):
        """The registry declaration is read, and it is the only thing that decides.

        Same archive, same rows, same absent row in the panel. The one thing that
        differs is that the source declares `mmf_on_rrp` a structural zero, and
        the record says so -- which is the second clause of the published
        limitation's predicate and the reason a declaration nothing reads was not
        a repair.
        """

        artifact = self.archive(self.DEALER_ONLY)
        # `through` is required, so the declaration that used to be prose alone
        # would now be refused. It is given a period that covers `REF_DATE`
        # because this test is about the disposition a covering declaration
        # produces; that a non-covering one produces the other disposition is
        # `test_a_declaration_does_not_reach_past_its_period`, and keeping the
        # two apart is what stops either from passing for the wrong reason.
        declared = self.registry(
            structural_zeros=(
                {
                    "field": "mmf_on_rrp",
                    "when": "months in which no reporting series lent to the facility",
                    "from": "2010-11-30",
                    "through": "2026-12-31",
                },
            )
        )
        record = self.coverage_for(
            parse_snapshots([artifact], registry=declared), self.REF_DATE
        )

        self.assertEqual(
            record.unmatched_derived_fields,
            (("mmf_on_rrp", DERIVED_ABSENCE_DECLARED_ZERO),),
        )

        # Declared does not mean observed. A reviewer saying the true value is
        # zero still does not put a row in the panel, because there was no
        # observation to put there.
        self.assertEqual(
            [row for row in parse_snapshots([artifact], registry=declared).rows
             if row.series_id == "mmf_on_rrp"],
            [],
            msg="a declared structural zero was materialised as a 0.0 observation",
        )

    def test_a_declaration_does_not_reach_past_its_period(self):
        """A declared period that ended before this month does not declare it.

        The fixture month is 2026-07-31 -- the one of the 33 unmatched repo
        months in which the facility existed. The review this class waits on
        declares the 32 months from 2010-11 to 2013-08, and the question here is
        whether that declaration reaches a month thirteen years past its own
        last covered date. It must not: the disposition would then say a
        reviewer had judged 2026-07-31 a structural zero, which no reviewer has.

        Both halves are here on purpose, and neither alone is the criterion. The
        first passes an implementation that ignores declarations entirely; the
        second passes one that ignores the period. Only the pair says the
        declaration is read *and* bounded.

        The date it is bounded against is the cross-section's own `ref_date`.
        Comparing against today, the build cutoff, or the latest month in the
        batch would each get this fixture right by coincidence -- all three sit
        past 2013-08 -- and would each read a re-run or a backfill differently
        from the run that wrote the record.
        """

        artifact = self.archive(self.DEALER_ONLY)

        expired = self.registry(
            structural_zeros=(
                {
                    "field": "mmf_on_rrp",
                    "when": "months before the facility accepted money-fund cash",
                    "from": "2010-11-30",
                    "through": "2013-08-31",
                },
            )
        )
        self.assertEqual(
            self.coverage_for(
                parse_snapshots([artifact], registry=expired), self.REF_DATE
            ).unmatched_derived_fields,
            (("mmf_on_rrp", DERIVED_ABSENCE_UNDECLARED),),
            msg="a declaration that ends in 2013 was read as covering 2026-07-31",
        )

        current = self.registry(
            structural_zeros=(
                {
                    "field": "mmf_on_rrp",
                    "when": "months before the facility accepted money-fund cash",
                    "from": "2010-11-30",
                    "through": self.REF_DATE.isoformat(),
                },
            )
        )
        self.assertEqual(
            self.coverage_for(
                parse_snapshots([artifact], registry=current), self.REF_DATE
            ).unmatched_derived_fields,
            (("mmf_on_rrp", DERIVED_ABSENCE_DECLARED_ZERO),),
            msg=(
                "a declaration whose `through` is the cross-section's own date "
                "was not read as covering it; the bound is inclusive"
            ),
        )

    def test_an_excluded_cross_section_still_carries_the_record(self):
        """The record is about the archive, not about the panel.

        A cross-section the coverage floor drops is not in the panel, and the
        question the brief asks is whether it should carry an absence record
        anyway. It should: the record states what the adapter observed in the
        archive -- the table was read, the rows were there, the match found
        nothing -- and none of that stops being true because the month was too
        thin to admit. `CrossSectionCoverage` already exists for excluded
        cross-sections and already carries `absent_fields` on them; making this
        one field behave differently would mean an absence record changed meaning
        depending on a coverage decision it has nothing to do with. A dropped
        month is also the one a reader is most likely to re-examine.
        """

        one_filer = ({**self.DEALER_ONLY[0], "accession": "X1", "series": "X1"},)
        parsed = parse_snapshots([self.archive(one_filer)], registry=self.registry())
        record = self.coverage_for(parsed, self.REF_DATE)

        self.assertFalse(record.admitted)
        self.assertEqual(
            record.unmatched_derived_fields,
            (("mmf_on_rrp", DERIVED_ABSENCE_UNDECLARED),),
        )
        self.assertEqual(parsed.rows, ())


class EmptyRepoCrossSectionTests(unittest.TestCase):
    """A cross-section that read its holdings and found no repo is excluded, with its reason.

    Decided 11 Sep, `docs/DATA_QUALITY_DECISIONS.md`, "An empty repo
    cross-section is excluded, with its reason". Before it, a cross-section that
    cleared the floor and whose holdings table was read in a declared
    `INVESTMENTCATEGORY` era, but matched no repo category, was admitted with no
    `mmf_repo_holdings` row and no record of why -- the one case
    `NMFP_DERIVED_FROM_MATCH` said it deliberately did not record. The fund
    industry always holds repo, so that month is a vocabulary failure until
    shown otherwise, and it now leaves the panel whole with
    `exclusion_reason` `no_repo_rows` on its coverage record.

    The traps, each a subtest: triggering on a missing table or on an undeclared
    era, which are `absent_fields` and stay admitted; triggering on
    `mmf_on_rrp`'s absence, which is `unmatched_derived_fields` and stays
    admitted; dropping only the repo field rather than the cross-section;
    writing a `0.0`; and losing the excluded month's coverage record.

    **Two readings this block chose, for review.** `below_floor` names both floor
    refusals, including a `ref_date` in no declared coverage era, because the
    brief's vocabulary is closed at two reasons; `reason` and `era_id` still tell
    them apart, as they did. And the rule fires on "no `mmf_repo_holdings`
    observation", so a month whose only repo rows carry absent value cells is
    excluded under `no_repo_rows` too; its cells are in `absent_cells`.

    **On the archives, 11 Sep.** Over all 97 declared archives in
    `data/raw/sec_nmfp/` -- the tracked 2026-07 extract and the backfill -- no
    cross-section hits `no_repo_rows`: zero `ref_date`s. The `sec_nmfp` rows
    parsed from them, and the rebuilt `data/processed/point_in_time.csv` and
    `daily_panel_point_in_time.csv`, are byte-identical before and after this
    block. The rule is a guard on the next vocabulary change, not a correction
    of a month already in the panel.

    Mutation record
    ---------------

    Disposable copy under `$HOME` built from `git ls-files --cached --others
    --exclude-standard`, `python3 -B` with `PYTHONDONTWRITEBYTECODE=1`,
    `OMP_NUM_THREADS=1`, each mutation applied to a fresh copy and confirmed
    applied by grep before the run. Unmutated control green before and after,
    zero `expectedFailure`. Each run is the whole suite; every kill below is in
    the acceptance test alone unless named otherwise.

    1. **The `no_repo_rows` check removed**, so a month that clears its floor is
       admitted whatever its holdings supplied. Kills the acceptance test on its
       first subtest, `AssertionError: True is not false` at
       `assertFalse(record.admitted)`.
    2. **The check triggering on a missing table too**: the `absent_so_far`
       clause removed. Kills two tests, all `AssertionError`: the acceptance
       test on two subtests -- the missing table and the undeclared era, each
       `False is not true` at `assertTrue(record.admitted)` -- and
       `PerTableRefusalTests::test_a_report_month_in_no_declared_era_costs_only_the_holdings_fields`
       on `'mmf_net_assets' not found in set()`. The second is the older
       per-table guard firing beside the new one: a month short of its
       vocabulary losing its whole balance sheet is what that class refuses.
    3. **Only the repo field dropped, the month kept**: the `continue` removed
       from the `no_repo_rows` branch and the record read from `refused` alone,
       so the record says `no_repo_rows` while the balance sheet and flows are
       emitted. Kills the acceptance test on its first subtest,
       `AssertionError: True is not false` at `assertFalse(record.admitted)` --
       the assertion mutation 1 hits, reached before the row assertions.
    4. **`below_floor` recorded as `None`.** Kills the acceptance test on its
       second subtest, `AssertionError: None != 'below_floor'`.
    5. **The vocabulary check removed** from `CrossSectionCoverage.__post_init__`.
       Kills the acceptance test on its last subtest,
       `AssertionError: ValueError not raised`.

    Two findings, recorded rather than repaired; each would be a second
    criterion.

    6. **Survives: the progressive reading is unguarded.** `absent_so_far`
       replaced by the every-archive `absent`, whole suite OK. No test files two
       archives into one month, the earlier without
       `NMFP_SCHPORTFOLIOSECURITIES.tsv` and the later with it and no repo
       category, which is the one shape that separates the two readings. The
       rule is judged as of each retrieval by construction and by nothing else.
       The same shape shows that `absent_fields` on a coverage record is taken
       from every archive, not from those retrieved so far -- older than this
       block, and a statement in the record rather than in the rows. **Closed by
       A21**: both now read the archives retrieved so far, and this mutation
       kills `AmendedRepoVintageTests`.
    7. **An amended-away repo month writes zeros, before this block and after
       it.** Reproduced by scratch on this tree: three filers admitted with repo
       rows, then a later archive whose `N-MFP3/A` amendments for all three file
       no repo category. The later vintage emits `mmf_repo_holdings` and
       `mmf_on_rrp` as `0.0` at 2026-07-31, and the month's record reads
       admitted with no `exclusion_reason`. Admission is never retracted, and
       `_assemble_sec_nmfp` re-totals a dirty cell over active submissions that
       no longer supply it. It is the never-a-zero trap reached through
       supersession, and this rule, judged at admission, does not reach it.
       **Closed by A21**: the rule is judged per vintage, see
       `AmendedRepoVintageTests`.
    """

    FLOOR = 3
    ADMITTED = date(2026, 7, 31)
    NO_REPO = date(2026, 6, 30)
    UNDECLARED_ERA = date(2026, 8, 31)

    #: A declared category this adapter reads no field from, in every era the
    #: fixture months fall in. Filed in the repo row's place, so the holdings
    #: table is present, parsed and classified, and simply carries no repo.
    NON_REPO_CATEGORY = "Certificate of Deposit"

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.output_root = Path(self.directory.name)
        self.fetched = 0

    def filers(self, report, prefix, count=3, **extra):
        day = report.split("-", 1)[1]
        return tuple(
            {
                "accession": f"{prefix}{index}",
                "series": f"S{index}",
                "report": report,
                "net_assets": 4_000_000_000,
                "flows": ((f"0{index}-{day}", 100_000_000 * index, 40_000_000 * index),),
                **extra,
            }
            for index in range(1, count + 1)
        )

    def archive(self, submissions, **kwargs):
        self.fetched += 1
        return fetch_sec_nmfp(
            self.output_root,
            "https://www.sec.gov/files/dera/data/form-n-mfp-data-sets/"
            f"fixture-{self.fetched}.zip",
            lambda url: nmfp_archive(submissions, **kwargs),
        )[0]

    def registry(self, *, extend_last_era_to=None):
        """The real registry, floors lowered, structural zeros stated as none.

        `extend_last_era_to` widens the last *coverage* era past the last
        declared `INVESTMENTCATEGORY` era. The two are bounded at the same month
        in the real registry, so a month with a floor and no category vocabulary
        can only be built this way.
        """

        path = registry_with_nmfp_coverage_floor(self.output_root, self.FLOOR)
        registry = json.loads(path.read_text(encoding="utf-8"))
        registry["sec_nmfp"]["structural_zeros"] = []
        registry["sec_nmfp"]["structural_zeros_reviewed"] = False
        if extend_last_era_to is not None:
            registry["sec_nmfp"]["cross_section"]["eras"][-1]["end"] = extend_last_era_to
        return registry

    @staticmethod
    def record(parsed, ref_date):
        records = [item for item in parsed.coverage if item.ref_date == ref_date]
        if len(records) != 1:
            raise AssertionError(f"expected one coverage record for {ref_date}: {records}")
        return records[0]

    def test_a_cross_section_with_no_repo_rows_is_excluded_with_its_reason(self):
        registry = self.registry()

        with self.subTest("holdings read, no repo category: excluded whole, with its reason"):
            no_repo = self.archive(
                self.filers("30-JUN-2026", "N"), repo_category=self.NON_REPO_CATEGORY
            )
            admitted = self.archive(self.filers("31-JUL-2026", "A"))
            parsed = parse_snapshots([no_repo, admitted], registry=registry)
            record = self.record(parsed, self.NO_REPO)

            # The premise: the month cleared its floor and its table was read.
            self.assertEqual(record.entity_count, self.FLOOR)
            self.assertNotIn("mmf_repo_holdings", record.absent_fields)
            self.assertIn(
                "mmf_treasury_holdings",
                {row.series_id for row in parse_snapshots(
                    [self.archive(self.filers("30-JUN-2026", "T"))], registry=registry
                ).rows},
                msg="the fixture month does not read holdings at all",
            )

            self.assertFalse(record.admitted)
            self.assertEqual(record.exclusion_reason, EXCLUSION_NO_REPO_ROWS)
            self.assertEqual(record.as_dict()["exclusion_reason"], EXCLUSION_NO_REPO_ROWS)
            self.assertIn("no repo holding", record.reason)
            # The coverage record is kept, and still counts what it declined.
            self.assertGreater(record.row_count, 0)

            # Excluded whole: no row from its archive and none dated in its
            # month -- not the balance sheet, not the flows -- and never a zero.
            self.assertEqual(
                [row for row in parsed.rows if row.source_sha == no_repo.sha256], []
            )
            self.assertEqual(
                [row for row in parsed.rows
                 if (row.ref_date.year, row.ref_date.month) == (2026, 6)],
                [],
            )
            self.assertNotIn(
                0.0,
                [row.value for row in parsed.rows if row.series_id == "mmf_repo_holdings"],
            )

        with self.subTest("an admitted cross-section reads None; a thin one reads below_floor"):
            self.assertTrue(self.record(parsed, self.ADMITTED).admitted)
            self.assertIsNone(self.record(parsed, self.ADMITTED).exclusion_reason)

            thin = parse_snapshots(
                [self.archive(self.filers("31-JUL-2026", "B", count=1))],
                registry=registry,
            )
            thin_record = self.record(thin, self.ADMITTED)
            self.assertFalse(thin_record.admitted)
            self.assertEqual(thin_record.exclusion_reason, EXCLUSION_BELOW_FLOOR)
            self.assertEqual(thin.rows, ())

        with self.subTest("a missing holdings table is absent_fields, and admitted"):
            parsed = parse_snapshots(
                [self.archive(
                    self.filers("31-JUL-2026", "M"),
                    omit=("NMFP_SCHPORTFOLIOSECURITIES.tsv",),
                )],
                registry=registry,
            )
            record = self.record(parsed, self.ADMITTED)
            self.assertIn("mmf_repo_holdings", record.absent_fields)
            self.assertTrue(record.admitted)
            self.assertIsNone(record.exclusion_reason)
            self.assertIn("mmf_net_assets", {row.series_id for row in parsed.rows})

        with self.subTest("an undeclared category era is absent_fields, and admitted"):
            parsed = parse_snapshots(
                [self.archive(self.filers("31-AUG-2026", "U"))],
                registry=self.registry(extend_last_era_to="2026-08"),
            )
            record = self.record(parsed, self.UNDECLARED_ERA)
            self.assertEqual(record.era_id, "n_mfp3")
            self.assertIn("mmf_repo_holdings", record.absent_fields)
            self.assertTrue(record.admitted)
            self.assertIsNone(record.exclusion_reason)
            self.assertIn("mmf_net_assets", {row.series_id for row in parsed.rows})

        with self.subTest("repo rows with no Fed counterparty: admitted, on_rrp record unchanged"):
            parsed = parse_snapshots(
                [self.archive(self.filers(
                    "31-JUL-2026", "D", repo_counterparty=FIXTURE_DEALER_COUNTERPARTY
                ))],
                registry=registry,
            )
            record = self.record(parsed, self.ADMITTED)
            observed = {row.series_id for row in parsed.rows}
            self.assertTrue(record.admitted)
            self.assertIsNone(record.exclusion_reason)
            self.assertIn("mmf_repo_holdings", observed)
            self.assertNotIn("mmf_on_rrp", observed)
            self.assertEqual(
                record.unmatched_derived_fields,
                (("mmf_on_rrp", DERIVED_ABSENCE_UNDECLARED),),
            )

        with self.subTest("the reason vocabulary is closed"):
            self.assertEqual(
                EXCLUSION_REASONS, (EXCLUSION_BELOW_FLOOR, EXCLUSION_NO_REPO_ROWS)
            )
            fields = dict(
                source_id="sec_nmfp",
                ref_date=self.NO_REPO,
                entity_unit="series_id",
                entity_count=self.FLOOR,
                declared_floor=self.FLOOR,
                admitted=False,
                row_count=0,
                era_id="n_mfp3",
            )
            for reason in EXCLUSION_REASONS:
                self.assertEqual(
                    CrossSectionCoverage(**fields, exclusion_reason=reason).exclusion_reason,
                    reason,
                )
            with self.assertRaises(ValueError) as refused:
                CrossSectionCoverage(**fields, exclusion_reason="quiet_month")
            self.assertIs(type(refused.exception), ValueError)
            self.assertIn("'quiet_month'", str(refused.exception))


class AmendedRepoVintageTests(unittest.TestCase):
    """An amendment that removes every repo row of an admitted month writes no zero.

    A21, closing the two findings `EmptyRepoCrossSectionTests` recorded. Before
    it, `no_repo_rows` was judged once, at admission, and admission was never
    retracted. A later archive whose `N-MFP3/A` amendments filed no repo category
    for an admitted month re-totalled that month's repo cells over submissions
    that no longer supplied them, and emitted `mmf_repo_holdings` and
    `mmf_on_rrp` as `0.0` -- the never-a-zero trap reached through supersession
    -- while the vintage's coverage record read admitted with no reason.

    **The rule now.** `no_repo_rows` is judged at every archive that files into
    the month. An amended vintage with no repo holding contributes no rows, for
    any field, and its coverage record reads `no_repo_rows`. The vintage before it
    keeps its rows and its record: what was known before the amendment stays
    known, and an as-of query between the two retrievals reads exactly what it
    read before this block. A later archive that restores repo rows re-admits the
    month with the new value.

    **"Archives retrieved so far", stated.** A field is in a coverage record's
    `absent_fields` when no archive retrieved up to and including that record's
    own supplies it for the month -- the intersection of their absences, never a
    later archive's. `no_repo_rows` reads that same set: it fires when the
    surviving submissions as of that archive supply no `mmf_repo_holdings` and
    the field is not in that set. So a month whose first archive lacks
    `NMFP_SCHPORTFOLIOSECURITIES.tsv` is admitted with the holdings fields absent,
    and an amendment carrying the table and no repo category excludes the
    amendment's vintage and not the first. Before this block the record's
    `absent_fields` was taken from every archive, so the first vintage's record
    denied an absence its own rows showed.

    The traps: dropping the amended vintage's coverage record, which fails the
    unpacking of the month's two records before any subtest; excluding the
    earlier vintage too, which rewrites history and fails the second subtest;
    and a `NaN` row, which is still a row and fails the first.

    **On the archives, 11 Sep.** Over all 97 declared archives in
    `data/raw/sec_nmfp/`, the `sec_nmfp` rows parsed (digest `5eeff385...`), the
    coverage records (`37770994...`), and the rebuilt
    `data/processed/point_in_time.csv` (`77983873...`) and
    `daily_panel_point_in_time.csv` (`18d06799...`) are byte-identical before and
    after this block; no record reads `no_repo_rows` and no repo row is `0.0`.
    No declared archive is the first, for its month, to lack a table a later
    archive carries -- or `absent_fields` would have moved. Both rules are guards
    on a future amendment, not corrections of a month in the panel.

    **Finding, recorded rather than repaired (a second criterion).** An amendment
    that *keeps* every repo row but files a dealer counterparty where the original
    filed the Federal Reserve still writes `mmf_on_rrp` `0.0` in its vintage, on
    this tree and before it, beside a record whose `unmatched_derived_fields`
    says the derivation matched nothing. Same mechanism -- a dirty cell
    re-totalled over submissions that no longer supply it -- reached through the
    derived field rather than the required one; the month is rightly admitted,
    so the per-vintage exclusion does not reach it.

    Mutation record
    ---------------

    Disposable copies under `$HOME` built from `git ls-files --cached --others
    --exclude-standard`, `python3 -B` with `PYTHONDONTWRITEBYTECODE=1`,
    `OMP_NUM_THREADS=1`, each mutation applied to a fresh copy and confirmed
    applied by grep before the run. Unmutated control green before and after,
    zero `expectedFailure`. Each run is the whole suite, and every kill is in
    this test alone, every one an `AssertionError`.

    1. **The per-vintage check removed** -- `admitted.discard(section)` deleted,
       which is the behaviour before this block. Four subtests: the amended
       vintage, `Lists differ: [0.0] != []` on its `mmf_on_rrp` row; its record,
       `True is not false` at `assertFalse(later.admitted)`; the restoring
       amendment, the excluded vintage's zero rows at
       `rows_from(again, amended)`; and the two-archive fixture, `True is not
       false` at `assertFalse(second.admitted)`.
    2. **The earlier vintage excluded as well**: on a `no_repo_rows` refusal the
       month's earlier candidates are dropped and its earlier records rewritten
       to excluded. Three subtests: `Tuples differ` at
       `assertEqual(alone.coverage, (earlier,))`, where the earlier record reads
       `admitted=False`; and `False is not true` at `assertTrue(first.admitted)`
       in both two-archive subtests. The first subtest survives it, rightly --
       the amended vintage still writes nothing.
    3. **A `0.0` written for `mmf_on_rrp` only**: the withdrawn submissions'
       `mmf_on_rrp` cells dirtied and re-totalled. Three subtests: `Lists
       differ: [0.0] != []` on the amended vintage's `mmf_on_rrp`; `Tuples
       differ` at `assertEqual(parsed.rows, alone.rows)`, one row longer; and
       the extra row at `rows_from(again, amended)`.
    4. **A20 probe 6**: the repo rule reads absence from every archive, the
       intersection over all of `scanned_absent`, instead of `absent_so_far`.
       Two subtests, both `False is not true` at `assertTrue(first.admitted)`:
       the earlier, tableless vintage is refused over a table no archive had
       yet carried. It survived the whole suite at A20.

    A first run had a fifth kill under mutation 2, `0.0 unexpectedly found`,
    in the restoring amendment: with its prior rows dropped, the fixture's
    genuine `CASH` of 0 was re-emitted. That was an incidental zero, not the
    defect, so the subtest now pins the repo fields' exact values, and all
    four mutations were re-run against the test as it stands.
    """

    FLOOR = 3
    MONTH = date(2026, 7, 31)
    REPORT = "31-JUL-2026"
    NON_REPO_CATEGORY = "Certificate of Deposit"
    REPO_FIELDS = ("mmf_on_rrp", "mmf_repo_holdings")

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.output_root = Path(self.directory.name)
        self.fetched = 0

    def filers(self, prefix, series=(1, 2, 3), *, amended=False, net_assets=4_000_000_000):
        """One submission per series for July 2026; an amendment files later."""

        return tuple(
            {
                "accession": f"{prefix}{index}",
                "series": f"S{index}",
                "report": self.REPORT,
                "filing": "20-AUG-2026" if amended else "05-AUG-2026",
                "submission_type": "N-MFP3/A" if amended else "N-MFP3",
                "net_assets": net_assets,
                "flows": ((f"0{index}-JUL-2026", 100_000_000 * index, 40_000_000 * index),),
            }
            for index in series
        )

    def archive(self, submissions, **kwargs):
        self.fetched += 1
        return fetch_sec_nmfp(
            self.output_root,
            "https://www.sec.gov/files/dera/data/form-n-mfp-data-sets/"
            f"amended-{self.fetched}.zip",
            lambda url: nmfp_archive(submissions, **kwargs),
        )[0]

    def registry(self):
        path = registry_with_nmfp_coverage_floor(self.output_root, self.FLOOR)
        registry = json.loads(path.read_text(encoding="utf-8"))
        registry["sec_nmfp"]["structural_zeros"] = []
        registry["sec_nmfp"]["structural_zeros_reviewed"] = False
        return registry

    def records(self, parsed):
        """The month's coverage records, one per archive, in retrieval order."""

        return [item for item in parsed.coverage if item.ref_date == self.MONTH]

    @staticmethod
    def rows_from(parsed, artifact):
        return [row for row in parsed.rows if row.source_sha == artifact.sha256]

    @staticmethod
    def values(rows, series_id):
        return [row.value for row in rows if row.series_id == series_id]

    def test_an_amendment_that_removes_every_repo_row_writes_no_zero(self):
        registry = self.registry()
        original = self.archive(self.filers("O"))
        amended = self.archive(
            self.filers("R", amended=True), repo_category=self.NON_REPO_CATEGORY
        )
        alone = parse_snapshots([original], registry=registry)
        parsed = parse_snapshots([original, amended], registry=registry)
        earlier, later = self.records(parsed)

        with self.subTest("the amended vintage emits no repo row and no 0.0 at all"):
            # The premise: the amendments superseded all three originals, and the
            # holdings table they carry was read.
            self.assertEqual(later.submission_types, (("N-MFP3", 3), ("N-MFP3/A", 3)))
            self.assertNotIn("mmf_repo_holdings", later.absent_fields)
            self.assertEqual(self.values(alone.rows, "mmf_repo_holdings"), [3.0])

            amended_rows = self.rows_from(parsed, amended)
            for field in self.REPO_FIELDS:
                self.assertEqual(self.values(amended_rows, field), [], msg=field)
            self.assertNotIn(0.0, [row.value for row in amended_rows])
            self.assertEqual(amended_rows, [])
            self.assertEqual(
                [row for row in parsed.rows if row.vintage_id == amended.retrieved_at], []
            )

        with self.subTest("its record reads no_repo_rows; the earlier vintage is unchanged"):
            self.assertFalse(later.admitted)
            self.assertEqual(later.exclusion_reason, EXCLUSION_NO_REPO_ROWS)
            self.assertIn("no repo holding", later.reason)
            self.assertGreater(later.row_count, 0)

            self.assertEqual(alone.coverage, (earlier,))
            self.assertTrue(earlier.admitted)
            self.assertIsNone(earlier.exclusion_reason)
            self.assertEqual(self.rows_from(parsed, original), list(alone.rows))
            self.assertEqual(parsed.rows, alone.rows)

        with self.subTest("an amendment that keeps some repo rows is admitted with its new value"):
            # S2 and S3 amend to no repo; S1's original repo row survives.
            partial = self.archive(
                self.filers("P", (2, 3), amended=True),
                repo_category=self.NON_REPO_CATEGORY,
            )
            kept = parse_snapshots([original, partial], registry=registry)
            record = self.records(kept)[-1]
            partial_rows = self.rows_from(kept, partial)
            self.assertTrue(record.admitted)
            self.assertIsNone(record.exclusion_reason)
            # Exact values, not "no 0.0 anywhere": the fixture files CASH and
            # liabilities as a real 0, which is an observation.
            self.assertEqual(self.values(partial_rows, "mmf_repo_holdings"), [1.0])
            self.assertEqual(self.values(partial_rows, "mmf_on_rrp"), [1.0])

            # And after an excluded vintage, a restoring amendment re-admits the
            # month with its new value rather than leaving it excluded.
            restored = self.archive(
                self.filers("T", (1,), amended=True, net_assets=8_000_000_000)
            )
            again = parse_snapshots([original, amended, restored], registry=registry)
            record = self.records(again)[-1]
            restored_rows = self.rows_from(again, restored)
            self.assertTrue(record.admitted)
            self.assertIsNone(record.exclusion_reason)
            self.assertEqual(self.values(restored_rows, "mmf_repo_holdings"), [2.0])
            self.assertEqual(self.values(restored_rows, "mmf_on_rrp"), [2.0])
            self.assertEqual(self.rows_from(again, amended), [])

        # The two-archive fixture: the earlier archive has no holdings table,
        # the later carries it and files no repo category.
        tableless = self.archive(
            self.filers("E"), omit=("NMFP_SCHPORTFOLIOSECURITIES.tsv",)
        )
        tabled = self.archive(
            self.filers("F", amended=True), repo_category=self.NON_REPO_CATEGORY
        )
        first_alone = parse_snapshots([tableless], registry=registry)
        both = parse_snapshots([tableless, tabled], registry=registry)
        first, second = self.records(both)

        with self.subTest(
            "absent_fields and no_repo_rows are judged on the archives retrieved so far"
        ):
            holdings = set(NMFP_CATEGORY_FIELDS)
            self.assertTrue(holdings <= set(first.absent_fields), first.absent_fields)
            self.assertTrue(first.admitted)
            self.assertIsNone(first.exclusion_reason)
            self.assertEqual(first_alone.coverage, (first,))

            self.assertEqual(holdings & set(second.absent_fields), set())
            self.assertFalse(second.admitted)
            self.assertEqual(second.exclusion_reason, EXCLUSION_NO_REPO_ROWS)
            self.assertEqual(self.rows_from(both, tabled), [])
            self.assertEqual(both.rows, first_alone.rows)

        with self.subTest("the every-archive reading would refuse the earlier vintage"):
            # This fixture is the shape that separates the two readings. Across
            # every archive the holdings fields are not absent, and the earlier
            # vintage supplies no repo row -- so reading absence from every
            # archive would exclude a vintage over a table not yet retrieved.
            every_archive = set(first.absent_fields) & set(second.absent_fields)
            self.assertNotIn("mmf_repo_holdings", every_archive)
            self.assertEqual(
                self.values(self.rows_from(both, tableless), "mmf_repo_holdings"), []
            )
            self.assertTrue(first.admitted)
            self.assertEqual(
                self.values(self.rows_from(both, tableless), "mmf_net_assets"), [12.0]
            )


class CoverageEraTests(unittest.TestCase):
    """The coverage floor is per era, and an undeclared date has none.

    One absolute floor cannot guard a universe that changes size. `sec_nmfp`
    falls from 730 reporting series in 2010 to 307 in 2024, so the single floor
    of 200 these replaced was 27 percent of the early universe and 65 percent of
    the late one: not one rule applied twice, but two different rules wearing
    one number. The first test here is the whole content of that claim -- one
    entity count, two eras, opposite verdicts -- and no single-absolute
    implementation can pass it.

    The eras declared in these fixtures are invented, and deliberately so. The
    production numbers are calibrated from the archives on disk and would make
    every assertion here depend on a backfill; what is under test is that a
    declared era is *read and applied*, not that any particular number is right.

    Mutation record
    ---------------
    Run in a disposable copy under `$HOME` carrying `data/`, `.github/`,
    `metadata/`, `.gitignore`, the root Markdown and `docs/PROJECT_STATUS.md`,
    with `PYTHONDONTWRITEBYTECODE=1` and `python3 -B`. The unmutated control was
    OK with zero expected failures. Every kill below is an assertion failure,
    not a raise: no mutation was caught by one incidental `ValueError` counted
    several times.

    1. **The era floors collapsed to one number.** `CoverageFloor.era_for`
       returns `self.eras[0]` whatever the `ref_date`. 5 failures, all in this
       class, including the acceptance test
       `test_one_entity_count_is_admitted_in_one_era_and_refused_in_another`.
       This is the acceptance criterion and its own mutation target, and they
       did not come apart.
    2. **The era inferred from the counts rather than read from the declared
       bounds** -- the admitting loop picks the era whose
       `observed_minimum_entities` is nearest the count it is judging, which is
       the floor choosing its own eras from the data it guards. 4 failures,
       including the acceptance test. Something notices, which was the open
       question this mutation was written to settle.
    3. **An undeclared `ref_date` admitted on the nearest era's floor** instead
       of refused. 4 failures, including both undeclared-`ref_date` tests and
       the live-registry test.
    4. **The boring one, and it stayed boring.** Rebuilt the panel and the
       cross-section coverage from the 97 archives on disk before and after the
       change: `daily_panel.csv` and `daily_panel_point_in_time.csv` are
       byte-identical, all 6474 observations are identical, and all 929
       coverage verdicts agree on `(ref_date, entity_count, admitted, rows)`.
       189 cross-sections admitted before, 189 after, the same ones. The only
       field that moved is `declared_floor`, from the single 200 to the floor of
       the era each cross-section falls in. Per-era floors change which floor
       applies where; they do not change what this extract admits.

    Under mutations 1 to 3 the panel still builds and the quality report still
    reports. That is the point: none of them is visible in an output anyone
    reads, which is why each needs a test that names it.
    """

    #: Two eras whose floors differ, and one entity count that falls between
    #: them. `EARLY_FLOOR` is above the count and `LATE_FLOOR` below it, so the
    #: same three-series cross-section is refused in one and admitted in the
    #: other on `ref_date` alone.
    EARLY_FLOOR = 4
    LATE_FLOOR = 3
    EARLY_REPORT = "29-JUN-2018"
    LATE_REPORT = "30-JUN-2025"
    EARLY_REF = date(2018, 6, 29)
    LATE_REF = date(2025, 6, 30)

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.output_root = Path(self.directory.name)

    def _registry(self, eras):
        registry = json.loads(SOURCE_REGISTRY.read_text(encoding="utf-8"))
        registry["sec_nmfp"]["cross_section"]["eras"] = eras
        return registry

    @staticmethod
    def _era(era_id, start, end, floor):
        return {
            "era_id": era_id,
            "start": start,
            "end": end,
            "minimum_reporting_entities": floor,
            "observed_minimum_entities": floor,
            "observed_complete_months": 1,
            "note": "declared by a fixture",
        }

    def _two_eras(self):
        return [
            self._era("early", "2010-11", "2024-05", self.EARLY_FLOOR),
            self._era("late", "2024-06", "2026-07", self.LATE_FLOOR),
        ]

    def _submissions(self, report):
        return tuple(
            {
                "accession": f"A{index}{report[:2]}",
                "series": f"S{index}",
                "report": report,
                "net_assets": 1_000_000_000,
            }
            for index in (1, 2, 3)
        )

    def _parse(self, registry, submissions, name):
        artifact = fetch_sec_nmfp(
            self.output_root,
            f"https://www.sec.gov/files/dera/data/form-n-mfp-data-sets/{name}.zip",
            lambda url: nmfp_archive(submissions),
        )[0]
        return parse_snapshots([artifact], registry=registry)

    def test_one_entity_count_is_admitted_in_one_era_and_refused_in_another(self):
        """Same count, opposite verdicts, on `ref_date` alone.

        This is the acceptance criterion for the per-era floor and it is also
        the mutation target: collapse the era floors to any single number and
        the two verdicts become the same verdict, whichever number is chosen.
        """

        registry = self._registry(self._two_eras())
        early = self._parse(registry, self._submissions(self.EARLY_REPORT), "early")
        late = self._parse(registry, self._submissions(self.LATE_REPORT), "late")

        early_section = {item.ref_date: item for item in early.coverage}[self.EARLY_REF]
        late_section = {item.ref_date: item for item in late.coverage}[self.LATE_REF]

        # The premise: one count, so the verdicts cannot differ on the count.
        self.assertEqual(early_section.entity_count, late_section.entity_count)
        self.assertEqual(early_section.entity_count, 3)

        self.assertFalse(
            early_section.admitted,
            msg="three series cleared a floor of four in the early era",
        )
        self.assertTrue(
            late_section.admitted,
            msg="three series failed a floor of three in the late era",
        )
        self.assertEqual(early_section.declared_floor, self.EARLY_FLOOR)
        self.assertEqual(late_section.declared_floor, self.LATE_FLOOR)
        self.assertEqual(early_section.era_id, "early")
        self.assertEqual(late_section.era_id, "late")

    def test_a_ref_date_before_the_first_era_is_refused_and_named(self):
        """No declared floor is not a floor of zero, and not the nearest one."""

        registry = self._registry(
            [self._era("late", "2024-06", "2026-07", self.LATE_FLOOR)]
        )
        parsed = self._parse(registry, self._submissions(self.EARLY_REPORT), "before")

        section = {item.ref_date: item for item in parsed.coverage}[self.EARLY_REF]
        self.assertFalse(section.admitted)
        self.assertIsNone(section.era_id)
        self.assertIsNone(
            section.declared_floor,
            msg="an undeclared era reported a floor it does not have",
        )
        self.assertIn("no declared coverage era", section.reason)
        self.assertNotIn(
            "mmf_net_assets", {row.series_id for row in parsed.rows},
            msg="a cross-section with no declared floor reached the panel",
        )

    def test_a_ref_date_after_the_last_era_is_refused_and_named(self):
        """The last era is bounded, so a later month is undeclared, not open."""

        registry = self._registry(
            [self._era("early", "2010-11", "2024-05", self.LATE_FLOOR)]
        )
        parsed = self._parse(registry, self._submissions(self.LATE_REPORT), "after")

        section = {item.ref_date: item for item in parsed.coverage}[self.LATE_REF]
        self.assertFalse(
            section.admitted,
            msg="a month past the last declared era was admitted on the "
            "nearest era's floor",
        )
        self.assertIsNone(section.era_id)
        self.assertIsNone(section.declared_floor)

    def test_an_undeclared_coverage_era_refuses_before_the_category_era_can_cost_fields(
        self,
    ):
        """The two era vocabularies are separate, and this one refuses first.

        `NMFP_INVESTMENT_CATEGORY_ERAS` costs a month outside it the categorical
        fields and admits the rest of the archive. The coverage eras refuse the
        cross-section outright. Both rules are right and they are about
        different things, so the order matters and is asserted rather than left
        to whichever check happens to run first.

        The two vocabularies currently share their bounds, because both follow
        the Form N-MFP version. Nothing requires them to stay equal -- a form
        revision that rewrites the categories without moving the universe is
        exactly when they should diverge -- so this asserts the precedence, not
        the coincidence.
        """

        registry = self._registry(self._two_eras())
        parsed = self._parse(registry, self._submissions("30-JUN-2005"), "undeclared")

        section = {item.ref_date: item for item in parsed.coverage}[date(2005, 6, 30)]
        self.assertFalse(section.admitted)
        self.assertIsNone(section.era_id)
        self.assertEqual(parsed.rows, ())

    def test_the_live_registry_declares_a_floor_for_every_month_it_carries(self):
        """The production eras cover the archive set, with no month left out.

        The independent anchor: the eras are declared by hand in
        `metadata/sources.json` and the months come from the archives on disk,
        so a boundary typed a month out lands here rather than in a silently
        smaller panel.
        """

        registry = json.loads(SOURCE_REGISTRY.read_text(encoding="utf-8"))
        floors = declared_coverage_floor("sec_nmfp", registry["sec_nmfp"])
        self.assertGreater(len(floors.eras), 1, "a single era is not a per-era floor")
        for era in floors.eras:
            self.assertLessEqual(
                era.minimum_reporting_entities,
                era.observed_minimum_entities,
                msg=f"era {era.era_id} refuses the smallest month it was "
                "calibrated from",
            )
        first, last = floors.eras[0], floors.eras[-1]
        self.assertIsNotNone(floors.era_for(date(2010, 11, 30)))
        self.assertIsNotNone(floors.era_for(date(2026, 7, 31)))
        self.assertIsNone(
            floors.era_for(date(2010, 10, 31)),
            msg=f"a month before {first.start} found a floor",
        )
        self.assertIsNone(
            floors.era_for(date(2026, 8, 31)),
            msg=f"a month after {last.end} found a floor",
        )


class FR2004DealerPositionTests(unittest.TestCase):
    """The FR 2004 adapter for `PDPOSGST-TOT` and the thirteen terms that sum to it.

    Anchored on the tracked export
    ------------------------------

    `tests/fixtures/snapshots/nyfed-primary-dealer/latest.csv` is a real
    download, not a hand-built row. `PDPOSGST-TOT` appears in it exactly once,
    at 2026-08-26, value 477607 millions, and that figure equals the sum of
    thirteen named series to the last million. The export also mixes five as-of
    dates -- 2026-07-31, -08-13, -08-18, -08-20 and -08-26 -- so a parser that
    read one date for the file would misdate 441 of its 1540 rows, and nothing
    in the file itself would say so.

    Named terms, never a glob
    -------------------------

    The thirteen are `PDPOSGS-B`, `PDPOSGS-BFRN`, the seven `PDPOSGSC-` maturity
    buckets and the four `PDPOSTIPS-` buckets. A glob over the two prefixes also
    matches the C-suffixed series in the same buckets (`PDPOSGSC-L2C` and its
    siblings) and sums to 492637 rather than 477607 millions at that date. The
    registry therefore names all thirteen and the mutation record below applies
    the glob's error directly.

    What a suppression can and cannot be recorded as
    ------------------------------------------------

    `*` marks a value the New York Fed withheld. It yields no observation.
    Asked whether the tree already distinguishes a suppression from a series the
    export does not carry: **it does not.** The two absence records that exist --
    `CrossSectionCoverage.absent_fields` and its `unmatched_derived_fields` --
    both hang off a cross-sectional assembly with a declared `entity_unit` and a
    coverage floor, and FR 2004 is a weekly time series with neither. Recording
    a suppression distinctly would mean inventing both, which is its own block.
    So this adapter stops at "no observation", and the distinction it can make
    is the identity's: a week with a suppressed term is `not_evaluable`, naming
    the term, rather than `violated` against a fabricated zero.

    **Superseded at A18.** A suppression is now recorded, and neither an entity
    unit nor a floor had to be invented for it: the record hangs off the cell,
    not a cross-section. `_fr2004_rows` records each `*` it reads as an
    `AbsentCell` with reason `suppressed`, carried in the quality report's
    `absent_cells`; see `AbsentValueReasonTests`. The identity's handling below
    is unchanged.

    Why the suppressed week is a second week
    ----------------------------------------

    `validate_accounting_identities` raises `DataContractError` -- "has no
    complete reference date" -- when *no* reference date has every declared
    term. The tracked export carries one week, so suppressing a term in place
    would take the identity down that raising path instead of the
    `not_evaluable` one, and the verdict this block is about would never be
    reached. The copy below therefore carries the real week and a synthetic
    earlier one, and only the synthetic week is suppressed. That the single-week
    case raises rather than recording `not_evaluable` is a finding about
    `validate_accounting_identities`, not about this adapter; it is reported and
    left alone, because changing it would move a shared guard that `sec_nmfp`
    also depends on.

    Mutation record
    ---------------

    Disposable copy under `$HOME` built from `git ls-files -z --cached --others
    --exclude-standard`, `python3 -B` with `PYTHONDONTWRITEBYTECODE=1`, Python
    3.9.6. Each mutation was applied to a freshly restored copy and each
    replacement was confirmed present in the file before the run.

    **The control was not green when this record was written, and that was this
    block's finding.** Exactly one failure, before the mutations and after them:
    `test_contract.FeatureSourceMapCoverageTests.test_every_registry_source_reaches_at_least_one_panel_column`,
    because `nyfed_fr2004` was ingested here and no panel column drew on it. What
    was outstanding was a human edit to `src/repo_model/contract.py`, which no
    track may make: moving `dealer_treasury_position` out of
    `UNSOURCED_FEATURES` and declaring it in `FEATURE_FIELDS` as
    `nyfed_fr2004.PDPOSGST-TOT`. **That move landed on 10 September 2026 and the
    control is green**, so the exclusion below applies to nothing. The guard was
    not the thing that was wrong; it was reporting a tree one human edit short
    of complete, and the edit arrived.

    **Re-run 10 September 2026 at block A14, python3 3.9.6**, because that block
    changed `metadata/sources.json` -- which mutations 1 and 4 both name -- by
    declaring the identity's three eras and the retired `PDPOSGSC-G11` bucket
    with them. Every mutation below still kills what it killed. One count moved:
    mutation 4 now kills three tests rather than two.

    1. `release_lag.days` 6 -> 0 in `metadata/sources.json`. Kills
       `test_the_fr2004_dealer_total_is_its_components_on_its_release_date`,
       `AssertionError`, on the availability instant -- 2026-08-26 16:30 where
       2026-09-03 16:30 is asserted. Also kills
       `test_each_row_is_dated_by_its_own_as_of_date`. Total 2.

       `AvailableAtDerivationTests` does **not** kill it, and the reason is
       worth keeping: that test recomputes its expectation from the same
       declaration the adapter reads, so a mutated `days` moves both sides
       together and the equality still holds. It catches an adapter that has
       drifted from the registry; it cannot catch a registry that is wrong.
       Only a literal instant can, which is why this test asserts one.
    2. The unit conversion dropped -- `value=value` in place of
       `value=value / FR2004_MILLIONS_PER_BILLION`. Kills the acceptance test,
       `AssertionError: 477607.0 != 477.607 within 9 places`. Total 1.
    3. `*` parsed as 0.0 -- the `FR2004_SUPPRESSED` branch rewrites the value to
       `"0"` instead of yielding no observation. Kills the acceptance test,
       `AssertionError`, at the `assertNotIn`: the suppressed week now carries a
       `PDPOSTIPS-G11` observation of 0.0. Had that assertion not been there the
       identity would have gone on to report `violated` by exactly the
       suppressed term, which is the second half of the same kill. Total 1.
    4. `PDPOSGSC-L2C` added to the identity's `right` terms, and to `fields` and
       `field_frequencies` with it -- `tests/test_contract.py` requires the
       terms to be a subset of `fields`, so the glob's error cannot be applied
       to the identity alone. Kills the acceptance test, `AssertionError`, on
       the parsed series set, and kills
       `test_a_series_the_registry_does_not_declare_is_ignored` with it. Since
       A14 it also kills
       `test_data.FR2004EraIdentityTests.test_every_fr2004_week_is_checked_against_its_own_eras_components`
       -- and by an *exception*, `repo_model.data.DataContractError`, not an
       assertion: the top-level terms no longer restate the most recent era, so
       the declaration is refused before any week is evaluated. Total 3.
    5. The non-numeric refusal made a no-op -- `except ValueError: continue`.
       Kills the acceptance test, `AssertionError: ValueError not raised`.
       Total 1.
    6. The missing-as-of-date refusal made a no-op, the same way. Kills the
       acceptance test, `AssertionError: ValueError not raised`. Total 1.

    Each refusal is asserted by the phrase only its own message carries, and
    each mutated copy carries exactly one defect, so neither refusal can stand
    in for the other: 5 and 6 both report `ValueError not raised` because each
    removed the only refusal its own case reaches.
    """

    FIXTURE = (
        Path(__file__).parents[1]
        / "tests"
        / "fixtures"
        / "snapshots"
        / "nyfed-primary-dealer"
        / "latest.csv"
    )

    #: The as-of date `PDPOSGST-TOT` appears at, and the only one in the export
    #: that carries the identity's terms.
    REF_DATE = date(2026, 8, 26)

    #: A second week, present in no download. It exists so the identity has a
    #: complete reference date to be evaluable on while another week is not.
    SUPPRESSED_REF_DATE = date(2026, 8, 19)

    TOTAL_SERIES = "PDPOSGST-TOT"

    COMPONENTS = (
        "PDPOSGS-B",
        "PDPOSGS-BFRN",
        "PDPOSGSC-L2",
        "PDPOSGSC-G2L3",
        "PDPOSGSC-G3L6",
        "PDPOSGSC-G6L7",
        "PDPOSGSC-G7L11",
        "PDPOSGSC-G11L21",
        "PDPOSGSC-G21",
        "PDPOSTIPS-L2",
        "PDPOSTIPS-G2",
        "PDPOSTIPS-G6L11",
        "PDPOSTIPS-G11",
    )

    def registry(self):
        return json.loads(SOURCE_REGISTRY.read_text(encoding="utf-8"))

    def fr2004_registry(self, registry=None):
        """Only the source under test, the way `build_daily_panel` restricts it.

        `validate_accounting_identities` evaluates every identity in whatever
        registry it is handed, and raises on one with no complete reference
        date. Handing it the whole registry would make this test fail on
        `sec_nmfp`'s balance sheet, which these observations say nothing about.
        """

        registry = registry or self.registry()
        return {"nyfed_fr2004": registry["nyfed_fr2004"]}

    def snapshot(self, text, registry=None):
        """One `SnapshotArtifact` over `text`, written to a temporary file."""

        payload = text.encode("utf-8")
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "latest.csv"
        path.write_bytes(payload)
        return SnapshotArtifact(
            source_id="nyfed_fr2004",
            path=path,
            retrieved_at="2026-09-10T00:00:00+00:00",
            sha256=hashlib.sha256(payload).hexdigest(),
            url=(
                "https://www.newyorkfed.org/markets/counterparties/"
                "primary-dealers-statistics"
            ),
            byte_count=len(payload),
        )

    def fixture_text(self):
        return self.FIXTURE.read_text(encoding="utf-8")

    def parse(self, text, registry=None):
        registry = registry or self.registry()
        return list(
            parse_snapshots([self.snapshot(text)], registry=registry).rows
        )

    def by_series(self, rows, ref_date):
        return {
            row.series_id: row for row in rows if row.ref_date == ref_date
        }

    def with_suppressed_week(self, suppressed):
        """The tracked export plus a synthetic earlier week with one term withheld.

        The added rows repeat the real week's values so the only thing that
        distinguishes the two weeks is the `*`. The total is carried across
        unchanged, which is what makes the case sharp: a parser that read `*` as
        0.0 would evaluate the identity and find it violated by exactly the
        suppressed term.
        """

        lines = [self.fixture_text().rstrip("\n")]
        values = self.by_series(self.parse(self.fixture_text()), self.REF_DATE)
        for series_id in (self.TOTAL_SERIES, *self.COMPONENTS):
            if series_id == suppressed:
                raw = "*"
            else:
                raw = str(round(values[series_id].value * 1000))
            lines.append(
                f'"{self.SUPPRESSED_REF_DATE.isoformat()}","{series_id}","{raw}"'
            )
        return "\n".join(lines) + "\n"

    def test_the_fr2004_dealer_total_is_its_components_on_its_release_date(self):
        registry = self.registry()
        rows = self.parse(self.fixture_text(), registry)

        # -- the value, and the unit it is in -----------------------------
        observed = self.by_series(rows, self.REF_DATE)
        self.assertEqual(
            sorted(observed), sorted([self.TOTAL_SERIES, *self.COMPONENTS])
        )
        self.assertAlmostEqual(observed[self.TOTAL_SERIES].value, 477.607, places=9)

        # -- availability, from the registry and not from the file --------
        self.assertEqual(
            observed[self.TOTAL_SERIES].available_at,
            datetime(2026, 9, 3, 16, 30, tzinfo=ZoneInfo("America/New_York")),
        )
        # Read from the declaration on every parse rather than compiled in: a
        # registry that declares one more business day moves the adapter with
        # it. An equality against the literal above alone would pass just as
        # well over a hard-coded constant.
        drifted = self.registry()
        drifted["nyfed_fr2004"]["release_lag"]["days"] += 1
        # `contract.validate_release_lag` holds `worst_case_calendar_days` at
        # or above `days + 5`, and the adapter fails closed on a non-empty
        # result from it, so the drifted declaration has to stay well formed or
        # this leg would pass on a refusal rather than on a moved availability.
        drifted["nyfed_fr2004"]["release_lag"]["worst_case_calendar_days"] += 1
        moved = self.by_series(self.parse(self.fixture_text(), drifted), self.REF_DATE)
        self.assertEqual(
            moved[self.TOTAL_SERIES].available_at,
            datetime(2026, 9, 4, 16, 30, tzinfo=ZoneInfo("America/New_York")),
        )

        # -- the declared identity, on the week it can be evaluated on ----
        held = validate_accounting_identities(rows, self.fr2004_registry(registry))[
            "nyfed_fr2004:dealer_treasury_total_is_its_declared_components"
        ]
        self.assertEqual(held.verdict, IDENTITY_HELD)
        self.assertEqual(held.evaluated_ref_dates, 1)
        self.assertEqual(held.violations, ())

        # -- a suppressed term: no observation, and not_evaluable ---------
        suppressed_series = "PDPOSTIPS-G11"
        suppressed_rows = self.parse(
            self.with_suppressed_week(suppressed_series), registry
        )
        withheld_week = self.by_series(suppressed_rows, self.SUPPRESSED_REF_DATE)
        self.assertNotIn(suppressed_series, withheld_week)
        self.assertEqual(
            sorted(withheld_week),
            sorted(
                series
                for series in (self.TOTAL_SERIES, *self.COMPONENTS)
                if series != suppressed_series
            ),
        )
        evaluation = validate_accounting_identities(
            suppressed_rows, self.fr2004_registry(registry)
        )["nyfed_fr2004:dealer_treasury_total_is_its_declared_components"]
        self.assertEqual(evaluation.violations, ())
        self.assertEqual(len(evaluation.unevaluated), 1)
        unevaluated = evaluation.unevaluated[0]
        self.assertEqual(unevaluated.ref_date, self.SUPPRESSED_REF_DATE)
        self.assertEqual(unevaluated.absent_fields, (suppressed_series,))
        self.assertEqual(evaluation.verdict, IDENTITY_HELD_WHERE_EVALUABLE)

        # -- the two refusals, each by the phrase only its message carries -
        non_numeric = self.fixture_text().replace(
            '"2026-08-26","PDPOSGST-TOT","477607"',
            '"2026-08-26","PDPOSGST-TOT","n/a"',
        )
        self.assertNotEqual(non_numeric, self.fixture_text())
        with self.assertRaisesRegex(
            ValueError, r"only '\*' marks a suppressed value"
        ):
            self.parse(non_numeric, registry)

        undated = self.fixture_text().replace(
            '"2026-08-26","PDPOSGST-TOT","477607"',
            '"","PDPOSGST-TOT","477607"',
        )
        self.assertNotEqual(undated, self.fixture_text())
        with self.assertRaisesRegex(ValueError, r"has no valid As Of Date"):
            self.parse(undated, registry)

    def test_a_series_the_registry_does_not_declare_is_ignored(self):
        """The export carries over two hundred series; this adapter claims fifteen.

        Including the C-suffixed siblings of the identity's own terms, which is
        why "ignored" has to be checked rather than assumed: `PDPOSGSC-L2C` is
        in the file, at the same as-of date, and it is not in the registry.

        The equality is against the declared fields *this export carries*, not
        against the declared fields outright, and the difference is one series.
        `PDPOSGSC-G11` is the over-eleven-year nominal coupon bucket the New York
        Fed retired at the 2022-01-05 report; it is declared because the
        identity's two earlier eras are checked against it, and this fixture is
        a current-era download, so no row of it can be parsed. Weakening the
        equality to a subset would have covered the same case and would also
        have stopped noticing a declared series the adapter never parses, which
        is what this test is for -- so what the file carries is computed from
        the file, and equality is kept.
        """

        rows = self.parse(self.fixture_text())
        declared = set(self.registry()["nyfed_fr2004"]["fields"])
        carried = {
            record["Time Series"].strip()
            for record in csv.DictReader(io.StringIO(self.fixture_text()))
        }
        self.assertEqual({row.series_id for row in rows}, declared & carried)
        self.assertEqual(declared - carried, {"PDPOSGSC-G11"})
        self.assertIn(
            '"2026-08-26","PDPOSGSC-L2C"', self.fixture_text(),
        )
        self.assertNotIn("PDPOSGSC-L2C", {row.series_id for row in rows})

    def test_each_row_is_dated_by_its_own_as_of_date(self):
        """Five as-of dates in one file, and none of the fourteen may borrow another's."""

        text = self.fixture_text()
        moved = text.replace(
            '"2026-08-26","PDPOSGS-B","69687"',
            '"2026-08-20","PDPOSGS-B","69687"',
        )
        self.assertNotEqual(moved, text)
        rows = self.parse(moved)
        dates = {row.series_id: row.ref_date for row in rows}
        self.assertEqual(dates["PDPOSGS-B"], date(2026, 8, 20))
        self.assertEqual(dates[self.TOTAL_SERIES], self.REF_DATE)
        self.assertEqual(
            {row.available_at for row in rows if row.series_id == "PDPOSGS-B"},
            {datetime(2026, 8, 28, 16, 30, tzinfo=ZoneInfo("America/New_York"))},
        )

    def test_an_undeclared_source_is_refused_rather_than_parsed_with_a_default(self):
        """No fallback lag. A registry without the entry cannot yield an availability."""

        registry = self.registry()
        del registry["nyfed_fr2004"]
        with self.assertRaisesRegex(
            ValueError, r"is not declared in the source registry"
        ):
            self.parse(self.fixture_text(), registry)


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
    The duplication is not removed for `_nyfed_rows`; it is made detectable.

    `nyfed_fr2004` is the first source where it is removed. `_fr2004_rows` takes the
    registry as an argument and reads `days`, `available_time` and `timezone` off it
    on every call, so for that source the two statements are one and this test cannot
    fail by disagreement. What it still does there is name the source as covered, so
    a fourth `ref_date` source cannot be added without a case. Note the limit, which
    `FR2004DealerPositionTests` records in full: an expectation recomputed from the
    declaration moves with the declaration, so this test cannot see a registry whose
    `days` is simply wrong. Only an assertion against a literal instant can, and that
    one lives with the adapter's own acceptance test.

    See `RealSnapshotPublicationGapTests` in `tests/test_data.py` for why this test,
    and not the publication-gap bound, is the one with teeth for these sources.
    """

    REGISTRY = json.loads(
        (Path(__file__).parents[1] / "metadata" / "sources.json").read_text(
            encoding="utf-8"
        )
    )

    def fr2004_snapshot(self, ref_date, retrieved):
        """One FR 2004 row, in the export's own CSV shape.

        A separate builder because the source shares the `nyfed_` prefix and
        nothing else: the reference-rate sources are JSON from the markets API
        and this one is a three-column CSV of Primary Dealer Statistics.
        """

        payload = (
            '"As Of Date","Time Series","Value (millions)"\n'
            f'"{ref_date}","PDPOSGST-TOT","477607"\n'
        ).encode("utf-8")
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "latest.csv"
        path.write_bytes(payload)
        return SnapshotArtifact(
            source_id=FR2004_SOURCE_ID,
            path=path,
            retrieved_at=retrieved,
            sha256=hashlib.sha256(payload).hexdigest(),
            url=(
                "https://www.newyorkfed.org/markets/counterparties/"
                "primary-dealers-statistics"
            ),
            byte_count=len(payload),
        )

    def source_snapshot(self, source_id, ref_date, retrieved):
        if source_id == FR2004_SOURCE_ID:
            return self.fr2004_snapshot(ref_date, retrieved)
        return self.nyfed_snapshot(source_id, ref_date, retrieved)

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
            self.ref_date_sources(),
            ["nyfed_bgcr", "nyfed_fr2004", "nyfed_sofr", "nyfed_tgcr"],
        )

    def test_adapter_available_at_matches_the_registry_declaration(self):
        for source_id in self.ref_date_sources():
            lag = self.REGISTRY[source_id]["release_lag"]
            # A midweek date and a Friday: the Friday is the only one whose
            # calendar gap differs from its business-day lag.
            for ref_date in (date(2026, 1, 6), date(2026, 1, 9)):
                with self.subTest(source=source_id, ref_date=ref_date):
                    snapshot = self.source_snapshot(
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
        snapshot = self.source_snapshot(
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


class TreasurySettlementSplitTests(unittest.TestCase):
    """A10: the adapter emits the split `contract.py` defines, on the tracked snapshot.

    Anchored on a real download
    ---------------------------

    `tests/fixtures/snapshots/treasury_auctions/auctions_2018_present.json` is
    Fiscal Data's `auctions_query`, fetched 10 September 2026: one page, meta
    `total-count` 3562 equal to its row count, issue dates 2018-01-02 through
    2026-09-30. Its manifest is beside it (A16, `TreasurySnapshotManifestTests`)
    and the test takes `retrieved_at` from there, building the rest of the
    `SnapshotArtifact` itself.

    What the snapshot exercises, and what it does not
    -------------------------------------------------

    `security_type` takes three values in it: `Bill` (2641), `Note` (719) and
    `Bond` (202). `CMB`, `TIPS` and `FRN` are declared in `contract.py` and are
    not exercised here -- cash-management bills arrive as `Bill` with a
    day-count term, e.g. the 2018-01-19 "6-Day". Nothing in the file is
    unlisted, so there is nothing to report as a missing declaration; the
    `Perpetual` record below is planted precisely because the snapshot has no
    natural undeclared type.

    `record_date` equals `issue_date` on every one of the 3562 rows, and is
    greater than or equal to `auction_date` on every one (equal on exactly one,
    the 2018-01-19 cash-management bill). So `record_date` is the settlement
    date, not a publication date -- see the corrected `treasury_auctions`
    limitation in `metadata/sources.json`. The consequence for this test is
    that the fourth assertion has nothing natural to fire on and its record is
    planted too.

    The trap, and which assertion kills it
    --------------------------------------

    Fiscal Data reports an auction result it does not have yet as the JSON
    **string** `"null"`. Five rows carry it: the auctions of 14-17 September
    2026, unheld at retrieval, settling 17-30 September. Read as `0.0`, the
    SOMA leg of an unheld auction publishes as a real award of nothing; skipped
    instead, the key's remaining records publish a partial award wearing the
    face of a complete one. Both readings are the union-identity trap A14 found
    in the FR 2004 identity, one source over. The third assertion refuses both:
    the three affected settlement dates -- 17, 18 and 30 September 2026 -- get
    no `treasury_settlement_soma` observation at all. A genuine zero award is a
    different thing and survives: 1093 records carry `soma_accepted` `"0"`.

    Why an absent leg is absent and not zero
    ----------------------------------------

    801 of the 1088 settlement dates have no coupon auction and 204 have no
    bill. Those keys get no observation for the missing leg. A `0.0` there
    would be arithmetically true and operationally unreadable: it is exactly
    what a classification failure also produces, and the panel would have no
    way to tell the two apart. The identity is therefore checked over the legs
    that are present, with the tolerance read from
    `TREASURY_SETTLEMENT_IDENTITY` rather than restated.

    Mutation record
    ---------------

    Disposable copy under `$HOME` built from `git ls-files -z --cached --others
    --exclude-standard`, `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`, Python
    3.9.6. Each mutation was applied to a freshly restored copy, and each
    replacement was confirmed present in the file before the run.

    **The control is not green, and that is this block's second finding.**
    Exactly one failure, identical before the mutations and after them:
    `test_docs_freshness.PublishedLimitationTests.test_no_published_limitation_outlives_its_repair`,
    naming `treasury_settlement_aggregate` at `docs/PROJECT_STATUS.md:262`.
    That guard's predicate reads `treasury_auctions`' declared `fields` and
    fails the moment any `treasury_settlement_` component appears beside the
    aggregate -- it was wired for this block before this block existed. The page
    still says the adapter does not emit the components. It does now, and
    `docs/PROJECT_STATUS.md` is `HUMAN_ONLY`, so the repair is a human edit,
    reported rather than made. That failure is excluded from "control" for that
    reason and no other; the mutations below are each scored as tests failing
    beyond it.

    1. **`"null"` read as zero.** `_treasury_amount`'s withheld branch returns
       `0.0` instead of `None`. Killed this test, `AssertionError` -- "a
       withheld SOMA award was published as a number", naming all three unheld
       settlement dates. One test beyond the control.
    2. **The unknown type defaulted to coupon.** The call to
       `treasury_settlement_component` replaced by an inline
       `"treasury_settlement_bill" if security_type in ("Bill", "CMB") else
       "treasury_settlement_coupon"`. Killed this test, `AssertionError`
       ("ValueError not raised"). This is the mutation that shows the
       classification really goes through the contract's function rather than a
       copy of its sets: the inline version classifies every fixture record
       identically and differs only on the planted `Perpetual`. One test beyond
       the control.
    3. **The date guard removed.** The `record_date < auction_date` `raise`
       deleted. Killed this test, `AssertionError` ("ValueError not raised").
       One test beyond the control.
    4. **The tolerance hard-coded tighter, and it did not kill.** The identity
       tolerance read replaced by a literal `0.0` in this test. The test still
       passes, and that is the honest result rather than a fourth kill. On this
       snapshot the aggregate equals bill plus coupon **exactly**, to the bit,
       on all 1088 settlement dates, and reversing the order the components are
       summed in does not change that. Every `offering_amt` is a whole number of
       millions taking one of two residues modulo a billion, 0 or 25000000, and
       the largest key aggregate is 531.0 USD billions, whose ulp is 1.1e-13.
       So the widest summation-order disagreement this fixture can produce is
       four orders of magnitude inside the declared 1e-9, and every tolerance
       from 0.0 up to 1e-9 returns the same verdict on every key. The declared
       tolerance is **not exercisable here**, and no mutation of it can be
       recorded as killing this test. It is read from
       `TREASURY_SETTLEMENT_IDENTITY` anyway: a literal would be a second
       definition of a number `contract.py` already owns, and a later snapshot
       -- odd-million cash-management bills, or aggregates large enough to move
       the exponent -- would exercise it. What guards the declared number today
       is `test_contract.TreasurySettlementSplitTests.test_soma_is_outside_the_identity`,
       which checks the declaration rather than a sum.

    Re-run of an existing record
    ----------------------------

    This block edits `treasury_auctions` in `metadata/sources.json`, which
    mutation 10 of `test_docs_freshness.PublishedLimitationTests` names. Re-run
    on this tree: `access` set to `"licensed"` still kills
    `test_no_published_limitation_claims_a_blocker_that_has_cleared`,
    `AssertionError`. It had not gone quiet under the rewritten limitation.
    """

    FIXTURE = (
        REPO_ROOT
        / "tests"
        / "fixtures"
        / "snapshots"
        / "treasury_auctions"
        / "auctions_2018_present.json"
    )
    MANIFEST = FIXTURE.with_name(FIXTURE.name + ".manifest.json")

    def _artifact(self):
        payload = self.FIXTURE.read_bytes()
        manifest = json.loads(self.MANIFEST.read_text(encoding="utf-8"))
        return (
            SnapshotArtifact(
                source_id="treasury_auctions",
                path=self.FIXTURE,
                retrieved_at=manifest["retrieved_at"],
                sha256=hashlib.sha256(payload).hexdigest(),
                url="https://api.fiscaldata.treasury.gov/services/api/fiscal_service/"
                "v1/accounting/od/auctions_query",
                byte_count=len(payload),
            ),
            payload,
        )

    def _planted(self, payload, **overrides):
        """The snapshot with one extra record, copied from a real one."""

        parsed = json.loads(payload)
        record = dict(parsed["data"][0])
        record.update(overrides)
        parsed["data"] = list(parsed["data"]) + [record]
        return json.dumps(parsed).encode()

    def test_every_auction_settles_into_one_declared_component_and_the_parts_sum_to_the_aggregate(
        self,
    ):
        from repo_model.contract import (
            TREASURY_SETTLEMENT_COMPONENTS,
            TREASURY_SETTLEMENT_IDENTITY,
        )
        from repo_model.ingest import _treasury_rows

        artifact, payload = self._artifact()
        rows = _treasury_rows(artifact, payload)

        by_key = {}
        for row in rows:
            by_key.setdefault((row.ref_date, row.available_at), {})[
                row.series_id
            ] = row.value

        # The components exist at all, which is what A10 was about.
        emitted = {row.series_id for row in rows}
        self.assertEqual(
            emitted,
            {"treasury_settlement"} | set(TREASURY_SETTLEMENT_COMPONENTS),
            msg="the adapter emits the aggregate alone, unsplit",
        )

        # The identity, over the legs that are present, at the declared
        # tolerance. An absent leg is absent: no key carries a component whose
        # value is exactly the zero an absent one would have been given.
        tolerance = float(TREASURY_SETTLEMENT_IDENTITY["tolerance"]["absolute"])
        right = tuple(TREASURY_SETTLEMENT_IDENTITY["right"])
        keys_missing_a_leg = 0
        for key, values in by_key.items():
            left = values["treasury_settlement"]
            present = [values[name] for name in right if name in values]
            self.assertTrue(present, msg=f"{key} settles into no declared component")
            if len(present) < len(right):
                keys_missing_a_leg += 1
            self.assertLessEqual(
                abs(left - sum(present)),
                tolerance,
                msg=(
                    f"{key}: aggregate {left!r} is not the sum of its present "
                    f"components {present!r} within {tolerance}"
                ),
            )
        self.assertGreater(
            keys_missing_a_leg,
            0,
            msg="no key is missing a leg, so absence is not being exercised",
        )

        # Classification goes through the contract's function, so an undeclared
        # security type is a refusal and not a third bucket.
        with self.assertRaisesRegex(ValueError, "neither a declared bill"):
            _treasury_rows(
                artifact, self._planted(payload, security_type="Perpetual")
            )

        # A withheld result takes its whole key's component with it. The three
        # settlement dates whose auctions were unheld at retrieval carry no
        # SOMA value -- not a zero, and not the sum of their held siblings.
        soma_keys = {
            key for key, values in by_key.items() if "treasury_settlement_soma" in values
        }
        unheld = {date(2026, 9, 17), date(2026, 9, 18), date(2026, 9, 30)}
        self.assertEqual(
            {key[0] for key in by_key} & unheld,
            unheld,
            msg="the fixture no longer carries the unheld auctions",
        )
        self.assertEqual(
            {key[0] for key in soma_keys} & unheld,
            set(),
            msg="a withheld SOMA award was published as a number",
        )
        seventeenth = next(key for key in by_key if key[0] == date(2026, 9, 17))
        self.assertNotIn("treasury_settlement_soma", by_key[seventeenth])

        # A result dated before the auction that produced it is refused. The
        # snapshot has none, so this one is planted.
        with self.assertRaisesRegex(ValueError, "a result dated before its auction"):
            _treasury_rows(
                artifact,
                self._planted(
                    payload,
                    auction_date="2026-09-15",
                    record_date="2026-09-14",
                    issue_date="2026-09-14",
                    soma_accepted="1000000000",
                ),
            )


class TreasuryBillRateTests(unittest.TestCase):
    """A15: every tracked year of Treasury daily bill rates is read by its own header.

    The inputs
    ----------

    `tests/fixtures/snapshots/treasury_bills/` holds Treasury's "Daily Treasury
    Bill Rates" export, one CSV per year, 2018 through 2026: dates MM/DD/YYYY,
    newest row first, a BANK DISCOUNT and a COUPON EQUIVALENT column per tenor.
    Only 2026 has no manifest: Treasury's export for the year in progress no
    longer returns the committed bytes (A16, `TreasurySnapshotManifestTests`).
    The test builds each `SnapshotArtifact` itself, taking `retrieved_at` from
    the year's manifest, and 2026's from `RETRIEVED_AT_2026`. Each is the
    committer time of the commit that first tracked that file, an upper bound on
    its retrieval rather than a measurement of it.

    Moving both classes onto the manifests' times changed no expected value, and
    that was checked rather than assumed. `retrieved_at` reaches two places in
    `parse_snapshots`: `vintage_id`, and the revision ordering at
    `ingest.py:2585-2601`, which re-dates a row whose key a later vintage
    repeats. Neither can move here. The nine files partition the calendar, so no
    `(series_id, ref_date)` key appears twice across them -- 24050 rows, 0
    repeated keys -- and the ordering branch never fires: parsing all nine under
    the single old time and under the eight manifests' times returns the same
    24050 rows, identical in `available_at`, `value` and `source_sha`, differing
    only in `vintage_id`. `TreasurySettlementSplitTests` parses one artifact, so
    it has no ordering to change. Neither class asserts an expected
    `vintage_id`, which is why the rider that queued this change asked for
    updated ones and there were none to update.

    The header changes twice. 2018-2021 carry 4, 8, 13, 26 and 52 weeks; 17
    weeks appears in 2022 and 6 weeks in 2025. A tenor is blank before its first
    auction: 8 weeks on 198 rows of 2018, 17 weeks on 199 rows of 2022, 6 weeks
    on 31 rows of 2025, each a contiguous run of the year's oldest dates. No
    other cell is blank, none is non-numeric, and eight cells of 25-26 March
    2020 are negative, which are rates and not faults.

    The trap, and which assertion kills it
    --------------------------------------

    Reading columns by position, or by the newest file's header applied to every
    year. On 2018 the eighth rate column is the 26-week coupon equivalent, and
    under the 2026 header it is the 13-week one. That reading parses and emits
    exactly the declared series, so the first assertion passes over it. The
    second compares the 13-week coupon equivalent on a 2018 date and a 2025 date
    with the cell under that file's own header, read here by `csv.DictReader`
    and pinned to a literal, and the column-to-field table below is written out
    rather than spelled by the adapter's rule. Each literal is unequal to every
    other cell of its row, so a misread neighbouring column cannot pass by
    coincidence -- the first 2025 date tried, 13 June, ties the 13-week coupon
    equivalent with the 8-week bank discount and was replaced.

    As A15 left it, and none of it occurring in the nine files: a row with
    fewer cells than the header raised `IndexError` rather than a phrased
    `ValueError`, a row with more had its extra cells ignored, and two header
    columns naming the same field were both read, two observations for one
    `(series, date)`. A17 refuses all three; see
    `test_a_row_or_header_that_does_not_line_up_is_refused` below.

    Mutation record
    ---------------

    Disposable copy under `$HOME` built from `git ls-files -z --cached --others
    --exclude-standard`, `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`, Python
    3.9.6, whole suite per mutation. Each mutation was applied to its own copy
    of the control, and each replacement was confirmed present in the file
    before the run.

    **The control is not green, and the failure is the human's to clear.**
    Exactly one failure, identical before the mutations and after:
    `test_contract.FeatureSourceMapCoverageTests.test_every_registry_source_reaches_at_least_one_panel_column`,
    naming `treasury_bill_rates`. Declaring a source no panel column draws on
    is what that test exists to surface, `AGENT_CONTRACT.md` says the human
    resolves it, and `contract.FEATURE_FIELDS` is `HUMAN_ONLY`. Each mutation
    below is scored as tests failing beyond it.

    1. **Columns mapped by the 2026 header positionally**, each row truncated to
       its own width so the file still parses. Killed this test,
       `AssertionError`, one test beyond the control: the second assertion's
       2018 case, "2.07 != 1.94", which is the 26-week coupon equivalent
       published as the 13-week one. The 2025 case passes under it, as it
       must, since 2025's header is 2026's. The third assertion fails too, on
       the per-series counts; the first does not, which is the trap.
    2. **A blank read as `0.0`.** Killed this test, `AssertionError`, one test
       beyond the control: the third assertion, the per-series counts.
    3. **An unknown header column skipped** instead of refused. Killed this
       test, `AssertionError` ("ValueError not raised"), one test beyond the
       control.
    4. **The date parsed permissively**: `%m/%d/%Y`, then `%Y-%m-%d`, `%m/%d/%y`
       and `%d/%m/%Y` in turn. Killed this test, `AssertionError` ("ValueError
       not raised"), one test beyond the control.
    5. **A non-numeric cell read as blank**, beyond the four the brief named,
       because it is a guard too. Killed this test, `AssertionError`
       ("ValueError not raised"), one test beyond the control.

    A17: a row or header that does not line up is refused
    -----------------------------------------------------

    `test_a_row_or_header_that_does_not_line_up_is_refused` plants five faults
    on the 2026 file, each in its own subtest asserting `ValueError` and the
    line number or the column names in the message: a short row, a blank line
    mid-file (the csv reader yields it as a row of no cells), a long row, a
    header column repeated by name, and `04 WEEKS BANK DISCOUNT` added beside
    `4 WEEKS BANK DISCOUNT`, two names the adapter's rule maps to one field.
    Each header case gives every row the matching cell, so the rows line up
    and only the header is at fault. A positive subtest pins 2018 and 2025 to
    a digest of what they parsed to before the guard, so a refusal that also
    caught the real files, or reordered their rows, cannot pass.

    Two traps. Checking only `len(record) < len(header)` ends the `IndexError`
    and still accepts the long row. De-duplicating the header silently rather
    than refusing it hides the fault the refusal exists to surface, and comparing
    raw names rather than mapped fields refuses the repeat and accepts two
    spellings of one tenor.

    Mutation record: disposable copies under `$HOME` from `git ls-files -z
    --cached --others --exclude-standard`, one per mutation,
    `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`, Python 3.9.6, whole suite per
    mutation. Each replacement was asserted present, exactly once, before the
    run. The control is green before and after, no expected failures, and
    every failure below is in this test and no other.

    1. **The length check removed.** Killed this test: the short-row and
       blank-line subtests with `IndexError` ("list index out of range"), the
       long-row subtest with `AssertionError` ("ValueError not raised").
    2. **The length check weakened to `<`.** Killed this test, the long-row
       subtest alone, `AssertionError` ("ValueError not raised").
    3. **The repeated-field check removed.** Killed this test, both header
       subtests, `AssertionError` ("ValueError not raised").
    4. **The repeated-field check comparing raw names instead of mapped
       fields.** Killed this test, the two-names subtest alone,
       `AssertionError` ("ValueError not raised"); the repeated name is still
       refused under it.
    """

    DIRECTORY = REPO_ROOT / "tests" / "fixtures" / "snapshots" / "treasury_bills"
    YEARS = tuple(range(2018, 2027))
    #: 2026 has no manifest, so its `retrieved_at` is declared here: the
    #: committer time of 1d715b6, the commit that first tracked the file.
    RETRIEVED_AT_2026 = "2026-09-10T16:00:11Z"

    #: Written out, not derived: a table spelled by the adapter's own rule would
    #: agree with the adapter whatever the rule said.
    FIELD_FOR_COLUMN = {
        "4 WEEKS BANK DISCOUNT": "tbill_4w_bank_discount",
        "4 WEEKS COUPON EQUIVALENT": "tbill_4w_coupon_equivalent",
        "6 WEEKS BANK DISCOUNT": "tbill_6w_bank_discount",
        "6 WEEKS COUPON EQUIVALENT": "tbill_6w_coupon_equivalent",
        "8 WEEKS BANK DISCOUNT": "tbill_8w_bank_discount",
        "8 WEEKS COUPON EQUIVALENT": "tbill_8w_coupon_equivalent",
        "13 WEEKS BANK DISCOUNT": "tbill_13w_bank_discount",
        "13 WEEKS COUPON EQUIVALENT": "tbill_13w_coupon_equivalent",
        "17 WEEKS BANK DISCOUNT": "tbill_17w_bank_discount",
        "17 WEEKS COUPON EQUIVALENT": "tbill_17w_coupon_equivalent",
        "26 WEEKS BANK DISCOUNT": "tbill_26w_bank_discount",
        "26 WEEKS COUPON EQUIVALENT": "tbill_26w_coupon_equivalent",
        "52 WEEKS BANK DISCOUNT": "tbill_52w_bank_discount",
        "52 WEEKS COUPON EQUIVALENT": "tbill_52w_coupon_equivalent",
    }

    def _path(self, year):
        return self.DIRECTORY / f"daily_treasury_bill_rates_{year}.csv"

    def _retrieved_at(self, year):
        if year == 2026:
            return self.RETRIEVED_AT_2026
        manifest = self._path(year).with_name(self._path(year).name + ".manifest.json")
        return json.loads(manifest.read_text(encoding="utf-8"))["retrieved_at"]

    def _artifact(self, year):
        payload = self._path(year).read_bytes()
        return SnapshotArtifact(
            source_id="treasury_bill_rates",
            path=self._path(year),
            retrieved_at=self._retrieved_at(year),
            sha256=hashlib.sha256(payload).hexdigest(),
            url=(
                "https://home.treasury.gov/resource-center/data-chart-center/"
                f"interest-rates/TextView?type=daily_treasury_bill_rates"
                f"&field_tdr_date_value={year}"
            ),
            byte_count=len(payload),
        )

    def _records(self, year):
        """One file read by its own header, touching no adapter code."""

        with self._path(year).open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    def _planted(self, year, edit):
        """One file's text with `edit` applied to its list of lines."""

        lines = self._path(year).read_text(encoding="utf-8").split("\n")
        edit(lines)
        return "\n".join(lines).encode("utf-8")

    def test_every_tracked_year_parses_by_its_own_header_and_an_unissued_tenor_is_absent(
        self,
    ):
        from repo_model.ingest import _treasury_bill_rate_rows, load_source_registry

        registry = load_source_registry()
        declared = set(registry["treasury_bill_rates"]["fields"])
        self.assertEqual(
            sorted(self.DIRECTORY.glob("*.csv")),
            [self._path(year) for year in self.YEARS],
            msg="the tracked files are not the nine years this test names",
        )

        # All nine parse, and the series they emit are the declared fields,
        # in both directions.
        rows = observations_from_snapshots(
            [self._artifact(year) for year in self.YEARS]
        )
        observed = {row.series_id for row in rows}
        self.assertEqual(
            observed - declared, set(), msg="an observation's series is undeclared"
        )
        self.assertEqual(
            declared - observed, set(), msg="a declared field is never observed"
        )
        by_key = {(row.series_id, row.ref_date): row.value for row in rows}

        # The 13-week coupon equivalent is the cell under this file's own
        # header, in a year before the header changed and a year after.
        for year, quote_date, literal in (
            (2018, date(2018, 6, 15), "1.94"),
            (2025, date(2025, 6, 12), "4.38"),
        ):
            with self.subTest(year=year):
                cell = next(
                    record["13 WEEKS COUPON EQUIVALENT"]
                    for record in self._records(year)
                    if record["Date"] == quote_date.strftime("%m/%d/%Y")
                )
                self.assertEqual(cell, literal, msg="the fixture cell moved")
                self.assertEqual(
                    by_key.get(("tbill_13w_coupon_equivalent", quote_date)),
                    float(cell),
                    msg=(
                        f"{quote_date}: the 13-week coupon equivalent is not the "
                        f"cell under {year}'s own header"
                    ),
                )

        # A tenor not yet auctioned is absent, never zero: each series has
        # exactly as many observations as it has non-blank cells, and none on a
        # date its cell is blank.
        expected_counts = {}
        blank = set()
        for year in self.YEARS:
            for record in self._records(year):
                quote_date = datetime.strptime(record["Date"], "%m/%d/%Y").date()
                for column, cell in record.items():
                    if column == "Date":
                        continue
                    field = self.FIELD_FOR_COLUMN[column]
                    if cell.strip():
                        expected_counts[field] = expected_counts.get(field, 0) + 1
                    else:
                        blank.add((field, quote_date))
        counts = {}
        for row in rows:
            counts[row.series_id] = counts.get(row.series_id, 0) + 1
        self.assertEqual(
            {field for field, _ in blank},
            {
                "tbill_6w_bank_discount",
                "tbill_6w_coupon_equivalent",
                "tbill_8w_bank_discount",
                "tbill_8w_coupon_equivalent",
                "tbill_17w_bank_discount",
                "tbill_17w_coupon_equivalent",
            },
            msg="the fixture no longer carries the three unissued tenors",
        )
        self.assertEqual(
            counts,
            expected_counts,
            msg="a series' observation count is not its count of non-blank cells",
        )
        self.assertEqual(
            {key for key in blank if key in by_key},
            set(),
            msg="a tenor not yet auctioned was published as a value",
        )

        # Refusals, each planted on the 2026 file.
        artifact = self._artifact(2026)
        with self.assertRaisesRegex(ValueError, "maps to no declared field"):
            _treasury_bill_rate_rows(
                artifact,
                self._planted(
                    2026,
                    lambda lines: lines.__setitem__(
                        0, lines[0].replace('"6 WEEKS BANK', '"10 WEEKS BANK')
                    ),
                ),
                registry,
            )
        with self.assertRaisesRegex(ValueError, "a date not in MM/DD/YYYY"):
            _treasury_bill_rate_rows(
                artifact,
                self._planted(
                    2026,
                    lambda lines: lines.__setitem__(
                        1, lines[1].replace("09/09/2026", "2026-09-09")
                    ),
                ),
                registry,
            )

        def non_numeric(lines):
            cells = lines[1].split(",")
            cells[3] = "N/A"
            lines[1] = ",".join(cells)

        with self.assertRaisesRegex(ValueError, "non-numeric"):
            _treasury_bill_rate_rows(
                artifact, self._planted(2026, non_numeric), registry
            )

    #: sha256 of what `_treasury_bill_rate_rows` returned for these two files
    #: before A17's refusals existed, at b0f48cc: one line per observation in
    #: the order returned, `series_id|ref_date|available_at|value|vintage_id|
    #: source_sha`, joined by newlines.
    PARSED_BEFORE_A17 = {
        2018: "b0f592ecf8bd945129987d5029fcc8173a91e92a76de407086f4397fbb866d32",
        2025: "e3ef7c14e8be56ac34b210682a9d5bef01cd23801f133bdb1e8fcdc6c60213d9",
    }

    def test_a_row_or_header_that_does_not_line_up_is_refused(self):
        from repo_model.ingest import _treasury_bill_rate_rows, load_source_registry

        registry = load_source_registry()

        def short_row(lines):
            lines[5] = lines[5].rsplit(",", 1)[0]

        def blank_line(lines):
            lines.insert(5, "")

        def long_row(lines):
            lines[5] = lines[5] + ",9.99"

        def added_column(name, copied_position):
            # Every row gets the matching cell, so the rows line up and only
            # the header is at fault.
            def edit(lines):
                lines[0] = f'{lines[0]},"{name}"'
                for index in range(1, len(lines)):
                    cells = lines[index].split(",")
                    lines[index] = f"{lines[index]},{cells[copied_position]}"

            return edit

        # Planted on the 2026 file. Lines count from 1 with the header, so
        # `lines[5]` is line 6; the trailing space keeps "line 6" off line 60.
        for case, edit, message in (
            ("short row", short_row, "line 6 "),
            ("blank line mid-file", blank_line, "line 6 "),
            ("long row", long_row, "line 6 "),
            (
                "the same header name twice",
                added_column("13 WEEKS COUPON EQUIVALENT", 8),
                "'13 WEEKS COUPON EQUIVALENT' and '13 WEEKS COUPON EQUIVALENT'",
            ),
            (
                "two names mapping to one declared field",
                added_column("04 WEEKS BANK DISCOUNT", 1),
                "'4 WEEKS BANK DISCOUNT' and '04 WEEKS BANK DISCOUNT'",
            ),
        ):
            with self.subTest(case=case):
                with self.assertRaisesRegex(ValueError, message):
                    _treasury_bill_rate_rows(
                        self._artifact(2026), self._planted(2026, edit), registry
                    )

        # The real files, which line up, parse to what they parsed to before.
        for year, digest in self.PARSED_BEFORE_A17.items():
            with self.subTest(year=year):
                rows = _treasury_bill_rate_rows(
                    self._artifact(year), self._path(year).read_bytes(), registry
                )
                text = "\n".join(
                    f"{row.series_id}|{row.ref_date.isoformat()}|"
                    f"{row.available_at.isoformat()}|{row.value!r}|"
                    f"{row.vintage_id}|{row.source_sha}"
                    for row in rows
                )
                self.assertEqual(
                    hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    digest,
                    msg=f"{year} no longer parses to the rows it parsed to before A17",
                )


class TreasurySnapshotManifestTests(unittest.TestCase):
    """A16: each Treasury snapshot that can carry a manifest carries one, bound to its bytes.

    The two tracked Treasury folders held ten snapshots and no manifest, so
    nothing recorded where a file came from, when, or that the bytes in the tree
    are the bytes that arrived. Nine now carry the per-file manifest
    `tests/fixtures/snapshots/funding_inputs/` uses, plus a `note`.

    Two decisions, both the user's, 11 September 2026
    -------------------------------------------------

    1. **The bill manifests carry `source_id` `"treasury_bill_rates"`, the
       registry id. The folder stays `treasury_bills/`; it is a location and
       nothing else.** `parse_snapshots` dispatches on `source_id`, and the only
       alias it applies is `LEGACY_SOURCE_IDS`, which exists for ids an adapter
       once wrote into a checksummed manifest. No adapter ever wrote
       `treasury_bills`. A manifest carrying the folder name loads --
       `load_snapshot_manifest` reads `source_id` as a string and checks
       nothing else about it -- and then has no parser. Making it parse would
       mean an `ingest.py` change or a legacy alias for a name that was never
       legacy; recording the registry id needs neither.

    2. **`daily_treasury_bill_rates_2026.csv` gets no manifest. Only a year
       whose download byte-matches the tracked file gets one.** 2018 through
       2025 do, at the url each manifest records. For 2026, Treasury's export
       for the year in progress no longer returns the committed bytes. A
       manifest is a claim that its `url` produced its `sha256`, and for 2026
       that claim would be false; leaving `url` out is not an alternative,
       because `load_snapshot_manifest` requires the key. So 2026 has no
       manifest, and this test requires that it has none.

    What the fields record
    ----------------------

    `retrieved_at` is the committer time of the commit that first tracked the
    file -- 62899d7 for the auctions, 304b6f5 for 2018-2023, 1d715b6 for
    2024-2025. It is a ceiling on when the file was retrieved, not a
    measurement, and each note says so. The eight bill files do not share one:
    2024-2026 were tracked 39 minutes before 2018-2023, so the earlier time is
    not a ceiling for 2018-2023 and the later one is not 2024-2025's first
    commit.

    The auctions `url` records the request that was made and cannot reproduce
    the bytes: its `issue_date` filter has no upper bound, so the same request
    returns every auction added since. Its note says so. Each bill `url` is one
    whose download byte-matched the tracked file.

    The traps
    ---------

    * One `retrieved_at` for all eight bill files: killed by the per-file
      `retrieved_at` assertion (mutation 4).
    * A digest of decoded text: `sha256` and `byte_count` are taken from
      `read_bytes()`. **On these ten files the trap is not exercisable.** None
      carries a carriage return or a byte-order mark, so UTF-8 text read and
      re-encoded is byte-identical to the file, and a text digest would pass
      here. The bytes are read anyway, because the next export might carry
      either.
    * Asserting the `source_id` string without parsing: this test asserts no
      `source_id` literal. Each manifest goes through `load_snapshot_manifest`
      and then `parse_snapshots` against the real registry, which is the check
      that caught the first A16 brief's `treasury_bills` (mutation 5).

    Mutation record
    ---------------

    Disposable copy under `$HOME` built from `git ls-files -z --cached --others
    --exclude-standard`, `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`, Python
    3.9.6, whole suite per mutation. Each mutation was applied to its own copy
    of the control, and each copy was diffed against the control before the run
    to confirm it differed in exactly one file.

    **The control is green, before the mutations and after,** in the copy and
    in the worktree. Both earlier records in this module had to score against a
    standing failure and neither failure remains: the one
    `TreasuryBillRateTests` names cleared when `treasury_bill_rates` was
    declared in `contract.UNMODELLED_SOURCES` (35eb88b), and the one
    `TreasurySettlementSplitTests` names cleared when the human edited
    `docs/PROJECT_STATUS.md` (9b0ccee). Those two records stand as written; they
    record the runs that happened.

    1. **A byte appended to one fixture** (`#` on the last line of
       `daily_treasury_bill_rates_2019.csv`). Killed this test,
       `AssertionError`, "sha256 is not the digest of the file's bytes". One
       test beyond it, incidentally:
       `TreasuryBillRateTests.test_every_tracked_year_parses_by_its_own_header_and_an_unissued_tenor_is_absent`,
       `ValueError` on the now non-numeric cell `'2.60#'` -- the adapter's own
       guard, not a second reading of the digest.
    2. **One manifest's `path` pointed at its sibling** (2020's manifest naming
       2021's CSV). Killed this test on three subtests, all `AssertionError`:
       2020 named by no manifest, 2021 named by two, and 2020's manifest not
       naming its own file. The middle one is the reason the count is asserted
       rather than the membership.
    3. **One manifest removed** (2022's). Killed this test, `AssertionError`,
       2022 named by no manifest. One test beyond it, incidentally:
       `TreasuryBillRateTests`, `FileNotFoundError` -- that class now reads the
       year's manifest for its `retrieved_at`, so a missing manifest stops it
       before any assertion. A `FileNotFoundError` there is not this guard
       firing twice.
    4. **2024's `retrieved_at` set to 304b6f5's time** (`16:39:19Z` for
       `16:00:11Z`), which is the "one `retrieved_at` for all eight bill files"
       trap made concrete. Killed this test, `AssertionError`, one test only.
       Nothing else notices: the value reaches `vintage_id`, which no assertion
       reads.
    5. **One bill manifest's `source_id` set to `"treasury_bills"`** (2023's),
       the folder name. Killed this test, **`ValueError`: "no point-in-time
       parser for treasury_bills"**, raised by `parse_snapshots`, not by an
       assertion. `load_snapshot_manifest` accepts it -- it reads `source_id`
       as a string and checks nothing else -- so a test that asserted the
       string would have to know the right answer in advance, and a test that
       only loaded would pass. This is the mutation the parse step exists for,
       and it is the defect the first A16 brief carried.
    6. **A manifest added for 2026**, well-formed otherwise: real `sha256` and
       `byte_count`, 1d715b6's time, and the export url for 2026. Killed this
       test on two subtests, both `AssertionError`: 2026 has a manifest and
       must not, and the manifest is undeclared. Well-formed is the point --
       the manifest loads and parses, so only the ruling that 2026 has none
       can catch it.

    Re-run of the existing records
    ------------------------------

    This block changes no fixture, so no existing mutation record names
    anything it edits. It does change what `retrieved_at` both Treasury classes
    pass, which is an input those records' mutations run over. That cannot
    blunt them: the checks above show the value reaches no assertion and no
    admitted row.
    """

    SNAPSHOTS = REPO_ROOT / "tests" / "fixtures" / "snapshots"
    DIRECTORIES = (SNAPSHOTS / "treasury_auctions", SNAPSHOTS / "treasury_bills")
    SIDECAR = ".manifest.json"

    AUCTIONS_URL = (
        "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/"
        "accounting/od/auctions_query?page[size]=10000&filter=issue_date:gte:2018-01-01"
    )
    BILL_URL = (
        "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
        "daily-treasury-rates.csv/{year}/all?type=daily_treasury_bill_rates"
        "&field_tdr_date_value={year}&page&_format=csv"
    )

    #: Committer time of the commit that first tracked each file.
    FIRST_TRACKED_62899D7 = "2026-09-10T19:22:46Z"
    FIRST_TRACKED_304B6F5 = "2026-09-10T16:39:19Z"
    FIRST_TRACKED_1D715B6 = "2026-09-10T16:00:11Z"

    #: Repo-relative path to (`retrieved_at`, `url`), written out per file.
    MANIFESTED = {
        "tests/fixtures/snapshots/treasury_auctions/auctions_2018_present.json": (
            FIRST_TRACKED_62899D7,
            AUCTIONS_URL,
        ),
        "tests/fixtures/snapshots/treasury_bills/daily_treasury_bill_rates_2018.csv": (
            FIRST_TRACKED_304B6F5,
            BILL_URL.format(year=2018),
        ),
        "tests/fixtures/snapshots/treasury_bills/daily_treasury_bill_rates_2019.csv": (
            FIRST_TRACKED_304B6F5,
            BILL_URL.format(year=2019),
        ),
        "tests/fixtures/snapshots/treasury_bills/daily_treasury_bill_rates_2020.csv": (
            FIRST_TRACKED_304B6F5,
            BILL_URL.format(year=2020),
        ),
        "tests/fixtures/snapshots/treasury_bills/daily_treasury_bill_rates_2021.csv": (
            FIRST_TRACKED_304B6F5,
            BILL_URL.format(year=2021),
        ),
        "tests/fixtures/snapshots/treasury_bills/daily_treasury_bill_rates_2022.csv": (
            FIRST_TRACKED_304B6F5,
            BILL_URL.format(year=2022),
        ),
        "tests/fixtures/snapshots/treasury_bills/daily_treasury_bill_rates_2023.csv": (
            FIRST_TRACKED_304B6F5,
            BILL_URL.format(year=2023),
        ),
        "tests/fixtures/snapshots/treasury_bills/daily_treasury_bill_rates_2024.csv": (
            FIRST_TRACKED_1D715B6,
            BILL_URL.format(year=2024),
        ),
        "tests/fixtures/snapshots/treasury_bills/daily_treasury_bill_rates_2025.csv": (
            FIRST_TRACKED_1D715B6,
            BILL_URL.format(year=2025),
        ),
    }

    #: Tracked files that must have no manifest, and why.
    UNMANIFESTED = {
        "tests/fixtures/snapshots/treasury_bills/daily_treasury_bill_rates_2026.csv": (
            "Treasury's export for the year in progress no longer returns the "
            "committed bytes, so no url can be recorded that produced them"
        ),
    }

    def test_each_treasury_snapshot_carries_a_manifest_bound_to_its_bytes(self):
        from repo_model.ingest import load_source_registry

        files = {}
        manifests = {}
        for directory in self.DIRECTORIES:
            for path in sorted(directory.iterdir()):
                if path.name.startswith("."):
                    continue
                relative = path.relative_to(REPO_ROOT).as_posix()
                if relative.endswith(self.SIDECAR):
                    manifests[relative] = json.loads(path.read_text(encoding="utf-8"))
                else:
                    files[relative] = path
        self.assertEqual(
            set(files),
            set(self.MANIFESTED) | set(self.UNMANIFESTED),
            msg="the tracked Treasury snapshots are not the files this test names",
        )

        # Every manifest has its file.
        for sidecar in manifests:
            with self.subTest(manifest=sidecar):
                self.assertIn(
                    sidecar[: -len(self.SIDECAR)],
                    files,
                    msg="a manifest has no snapshot beside it",
                )

        # Every file is named by exactly one manifest, its own -- except those
        # that must have none.
        for relative in files:
            with self.subTest(file=relative):
                naming = sorted(
                    sidecar
                    for sidecar, manifest in manifests.items()
                    if manifest.get("path") == relative
                )
                if relative in self.UNMANIFESTED:
                    self.assertEqual(
                        (naming, relative + self.SIDECAR in manifests),
                        ([], False),
                        msg=(
                            f"{relative} has a manifest and must not: "
                            f"{self.UNMANIFESTED[relative]}"
                        ),
                    )
                else:
                    self.assertEqual(
                        naming,
                        [relative + self.SIDECAR],
                        msg=f"{relative} is not named by exactly its own manifest",
                    )

        # Each manifest is bound to its file's bytes, records the declared
        # retrieval ceiling and url, and loads and parses as written. The
        # manifest's path is repo-relative, so it is resolved from the root.
        registry = load_source_registry()
        previous = os.getcwd()
        os.chdir(REPO_ROOT)
        try:
            for sidecar, manifest in sorted(manifests.items()):
                relative = sidecar[: -len(self.SIDECAR)]
                with self.subTest(manifest=sidecar):
                    self.assertIn(relative, self.MANIFESTED, msg="an undeclared manifest")
                    payload = files[relative].read_bytes()
                    self.assertEqual(
                        manifest["sha256"],
                        hashlib.sha256(payload).hexdigest(),
                        msg="sha256 is not the digest of the file's bytes",
                    )
                    self.assertEqual(
                        manifest["byte_count"],
                        len(payload),
                        msg="byte_count is not the file's length in bytes",
                    )
                    self.assertEqual(manifest["path"], relative)
                    retrieved_at, url = self.MANIFESTED[relative]
                    self.assertEqual(manifest["retrieved_at"], retrieved_at)
                    self.assertEqual(manifest["url"], url)
                    artifact = load_snapshot_manifest(REPO_ROOT / sidecar)
                    parsed = parse_snapshots([artifact], registry=registry)
                    self.assertTrue(parsed.rows, msg="the manifest parses to nothing")
        finally:
            os.chdir(previous)


class AbsentValueReasonTests(unittest.TestCase):
    """A18: every absent cell is recorded with the token it was read from.

    The decision is `docs/DATA_QUALITY_DECISIONS.md`, "An absent value keeps its
    reason". Six adapters used to drop an absent token without a trace, so the
    panel showed a hole that could not say whether its cell was blank, `.`, not
    yet published or suppressed. Each now calls `ingest._read_cell`, the one
    place a token becomes an absence, and the absence is appended to
    `ParsedSnapshots.absent_cells` and written to the quality report's
    `absent_cells`, with a count for every reason in the vocabulary.

    The sites, every one in `src/repo_model/ingest.py`: `_nyfed_rows`,
    `_fr2004_rows`, `_fred_rows`, `_treasury_amount` (for `_treasury_rows`),
    `_treasury_bill_rate_rows` and `_nmfp_number` (for `_nmfp_archive_scan`).
    A seventh copy of the N-MFP token set exists outside the package, in
    `scripts/nmfp_identity_residuals.py`, which restates `_nmfp_number` so the
    script depends on nothing. `scripts/` is `HUMAN_ONLY`; it is reported, not
    edited, and it writes no panel.

    What it records, and what it does not
    -------------------------------------

    Each adapter keeps its own token table, because each publisher writes its
    own tokens: `NA` is absent to the New York Fed and a refusal to FRED, and
    blank is absent to FRED and a refusal to FR 2004. No token was added to or
    removed from any adapter, so every refusal that existed still refuses. A
    `None` -- a JSON null, or a delimited row short of its header -- was read as
    the empty cell by every adapter, and is recorded as `blank`.

    A New York Fed key the record does not carry is not a cell and is not
    recorded. The API has used two spellings of each percentile and a response
    carries one, so the other spelling is missing from every record; recording
    it would log four absences per day that no file contains. An FR 2004 series
    the registry does not declare is skipped before its value is read, so its
    `*` is not recorded either: the tracked export carries 182 `*` cells, every
    one in an undeclared series, and none of the fifteen declared ones.

    What it found on the tracked inputs
    -----------------------------------

    No observation moved. `repo_model.cli build` over
    `tests/fixtures/snapshots/funding_inputs/`, python3 3.9.6, before and after:
    the panel pinned to `metadata/funding_panel_manifest.json`'s columns is
    `b6af33bb...4bec` both times, the default build `d6e9a2b2...af16` both
    times, and the long point-in-time panel `ef76551d...981e` both times. The
    quality report beside it moved, as it must, from `1c31ce8a...` to
    `fda80909...`, and from about 4 KB to about 12 MB: it records 49036 absent
    cells, 49028 `blank` and 8 `na`. The 8 are the SOFR rate snapshot's four
    percentiles on two days, written `NA`. The blanks are all FRED's -- 24500
    `IORB` and 21692 `IOER`, each series blank across the other's years, 2831
    `RRPONTSYD` and 5 `DFF` -- because the graph CSV joins series of different
    spans on one date column. It writes no `.` at all in that snapshot: its
    missing observations arrive blank, so the `dot` count there is zero and is
    stated as zero.

    The Treasury offering-amount refusal is shadowed, and still raises
    ------------------------------------------------------------------

    `_treasury_rows` refuses a withheld `offering_amt` with "withholds
    offering_amt: an announced offering amount is known when the auction is
    announced". That message is unreachable: the same record's `offering_amt`
    is parsed with `float()` a few lines earlier, for the aggregate, and a
    `"null"` or a blank refuses the file there first, as "lacks ... or
    offering_amt". The file is refused either way, which is what the subtest
    below asserts; which of the two messages refuses it is not changed here.

    Mutation record
    ---------------

    11 September 2026, python3 3.9.6. Disposable copies under `$HOME`, one per
    mutation, each built from `git ls-files -z --cached --others
    --exclude-standard`; `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`, whole suite
    per mutation. Each replacement was asserted to occur exactly once and then
    confirmed present in the file before the run. The unmutated control is
    green before and after, with no expected failures. Every failure below is
    in this test and no other.

    1. **`.` recorded as `blank`**, in `NMFP_ABSENT_TOKENS`. Killed the
       `sec_nmfp` subtest, `AssertionError` ("Lists differ"): the two `.`
       cells come back `blank`.
    2. **The FR 2004 `*` branch recording nothing**: `_fr2004_rows` back on
       its old `if raw_value == FR2004_SUPPRESSED: continue`. Killed the
       `nyfed_fr2004` subtest, `AssertionError` ("Lists differ: [] != ..."):
       no observation either way, and no record.
    3. **FRED calling the old skip**: `_fred_rows` back on
       `if raw_value in {"", "."}: continue`. Killed the `fred` subtest,
       `AssertionError` ("Lists differ: [] != ..."). It also killed the
       vocabulary refusal subtest, `AssertionError` ("ValueError not raised"),
       and rightly: that refusal is shown through FRED's table, and an adapter
       that no longer reads its table cannot refuse what the table says.
    4. **The unknown-token refusal removed**: `_nmfp_number`'s `raise` replaced
       by `return None`. Killed the `sec_nmfp unknown token` refusal subtest,
       `AssertionError` ("ValueError not raised"). The other five adapters'
       refusals are untouched by it and still pass.
    5. **The vocabulary check removed** from `_read_cell`. Killed the
       vocabulary refusal subtest, `AssertionError` ("ValueError not raised").

    Re-run under A19, 11 September 2026, by the same procedure. A19 changed
    this test's `sec_nmfp` report assertion to read the report back through
    `data.absent_cells_from_quality_report`, since the report now writes runs.
    Mutations 1, 4 and 5 kill exactly what is recorded above and nothing else.
    Mutations 2 and 3 kill what is recorded above and now also
    `AbsentCellRunTests`, whose expansion subtest reads the same adapters, so
    "no other" is no longer true of them: 2 kills its expansion subtest,
    `AssertionError` ("() is not true : nyfed_fr2004"); 3 kills its four
    run-shape and expansion subtests, `AssertionError` (no runs at all), and
    its refusal subtest, `IndexError`, because the FRED report it tampers with
    has no run left to tamper with.
    """

    RETRIEVED_AT = "2026-09-11T12:00:00+00:00"

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def artifact(self, source_id, name, payload, url):
        path = self.root / name
        path.write_bytes(payload)
        return SnapshotArtifact(
            source_id=source_id,
            path=path,
            retrieved_at=self.RETRIEVED_AT,
            sha256=hashlib.sha256(payload).hexdigest(),
            url=url,
            byte_count=len(payload),
        )

    @staticmethod
    def recorded(parsed):
        return sorted(
            (cell.source_id, cell.field, cell.ref_date, cell.reason, cell.source_sha)
            for cell in parsed.absent_cells
        )

    @staticmethod
    def planted_tsv(payload, table, edits):
        """An N-MFP archive with cells replaced: `edits` maps (row, column) to text.

        `row` counts data rows from 0, in file order.
        """

        source = zipfile.ZipFile(io.BytesIO(payload))
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as target:
            for name in source.namelist():
                text = source.read(name).decode("utf-8")
                if name == table:
                    lines = [line.split("\t") for line in text.rstrip("\n").split("\n")]
                    header = lines[0]
                    for (row, column), token in edits.items():
                        lines[row + 1][header.index(column)] = token
                    text = "\n".join("\t".join(line) for line in lines) + "\n"
                target.writestr(name, text)
        return buffer.getvalue()

    def nmfp_payload(self):
        """Five filers for July 2026; the first four carry the planted tokens.

        The fifth is untouched, so every series still has an observation and
        the build's identities have a complete reference date to run on.
        """

        net = 1_000_000_000
        payload = nmfp_archive(
            [
                {
                    "accession": f"A{index}",
                    "series": f"S{index}",
                    "report": "31-JUL-2026",
                    "net_assets": net,
                    "flows": [("30-JUL-2026", 300_000_000, 100_000_000)]
                    if index in (1, 5)
                    else [],
                }
                for index in range(1, 6)
            ]
        )
        payload = self.planted_tsv(
            payload,
            "NMFP_SERIESLEVELINFO.tsv",
            {(0, "CASH"): "", (1, "CASH"): "NA", (2, "CASH"): "N/A", (3, "CASH"): "."},
        )
        payload = self.planted_tsv(
            payload,
            "NMFP_DLYSHAREHOLDERFLOWREPORT.tsv",
            {(0, "DAILYGROSSREDEMPTIONS"): "."},
        )
        # Holdings rows are two per filer, Treasury then repo: row 2 is A2's
        # Treasury holding.
        return self.planted_tsv(
            payload,
            "NMFP_SCHPORTFOLIOSECURITIES.tsv",
            {(2, "INCLUDINGVALUEOFANYSPONSORSUPP"): "N/A"},
        )

    def test_every_absent_cell_is_recorded_with_the_token_it_was_read_from(self):
        from unittest import mock

        from repo_model import ingest
        from repo_model.data import ABSENCE_REASONS
        from repo_model.ingest import (
            _fr2004_rows,
            _fred_rows,
            _nyfed_rows,
            _treasury_bill_rate_rows,
            _treasury_rows,
            load_source_registry,
        )

        registry = load_source_registry()
        nmfp_url = "https://www.sec.gov/files/dera/data/form-n-mfp-data-sets/a18.zip"

        # The vocabulary is closed, and these are its members.
        self.assertEqual(
            ABSENCE_REASONS, ("blank", "na", "dot", "null", "suppressed")
        )

        with self.subTest(adapter="sec_nmfp"):
            payload = self.nmfp_payload()
            artifact = self.artifact("sec_nmfp", "a18.zip", payload, nmfp_url)
            sha = artifact.sha256
            expected = sorted(
                [
                    ("sec_nmfp", "mmf_cash", date(2026, 7, 31), "blank", sha),
                    ("sec_nmfp", "mmf_cash", date(2026, 7, 31), "na", sha),
                    ("sec_nmfp", "mmf_cash", date(2026, 7, 31), "na", sha),
                    ("sec_nmfp", "mmf_cash", date(2026, 7, 31), "dot", sha),
                    # A flow cell is dated by its flow date, not its report date.
                    ("sec_nmfp", "mmf_gross_redemptions", date(2026, 7, 30), "dot", sha),
                    ("sec_nmfp", "mmf_treasury_holdings", date(2026, 7, 31), "na", sha),
                ]
            )
            panel_path = self.root / "nmfp.csv"
            registry_path = registry_with_nmfp_coverage_floor(self.root, 1)
            build_point_in_time_snapshot(
                [artifact], panel_path, registry_path=registry_path
            )
            parsed = parse_snapshots(
                [artifact],
                registry=json.loads(registry_path.read_text()),
                keep_row_dates=True,
            )
            self.assertEqual(self.recorded(parsed), expected)

            # ...and the quality report carries exactly those, with a count for
            # every reason, a zero stated rather than omitted. Since A19 it
            # writes them as runs, read back here into one record per cell.
            quality = json.loads(
                panel_path.with_suffix(".csv.quality.json").read_text()
            )
            report = quality["absent_cells"]
            self.assertEqual(
                report["counts"],
                {"blank": 1, "na": 3, "dot": 2, "null": 0, "suppressed": 0},
            )
            self.assertEqual(
                sorted(
                    (
                        cell.source_id,
                        cell.field,
                        cell.ref_date,
                        cell.reason,
                        cell.source_sha,
                    )
                    for cell in absent_cells_from_quality_report(
                        quality, parsed.absent_cell_row_dates
                    )
                ),
                expected,
            )

            # No value was invented for an absent cell: A1 was the only filer
            # to lose its redemptions, and A5 files the same day, so the day
            # keeps A5's redemptions and the net flow is A5's alone.
            values = {
                (row.series_id, row.ref_date): row.value
                for row in load_point_in_time_panel(panel_path)
            }
            self.assertEqual(values[("mmf_gross_subscriptions", date(2026, 7, 30))], 0.6)
            self.assertEqual(values[("mmf_gross_redemptions", date(2026, 7, 30))], 0.1)
            self.assertEqual(values[("mmf_net_flow", date(2026, 7, 30))], 0.2)
            self.assertEqual(values[("mmf_cash", date(2026, 7, 31))], 0.0)

        with self.subTest(adapter="nyfed_fr2004"):
            fixture = FR2004DealerPositionTests
            text = fixture.FIXTURE.read_text(encoding="utf-8")
            declared = set(registry[FR2004_SOURCE_ID]["fields"])
            real_week = {
                row.series_id: row.value
                for row in _fr2004_rows(
                    self.artifact(FR2004_SOURCE_ID, "real.csv", text.encode(), "fr2004"),
                    text.encode(),
                    registry,
                )
                if row.ref_date == fixture.REF_DATE
            }
            suppressed_series = "PDPOSTIPS-G11"
            lines = [text.rstrip("\n")]
            for series_id in (fixture.TOTAL_SERIES, *fixture.COMPONENTS):
                raw = (
                    "*"
                    if series_id == suppressed_series
                    else str(round(real_week[series_id] * 1000))
                )
                lines.append(
                    f'"{fixture.SUPPRESSED_REF_DATE.isoformat()}","{series_id}","{raw}"'
                )
            planted = ("\n".join(lines) + "\n").encode("utf-8")
            artifact = self.artifact(FR2004_SOURCE_ID, "latest.csv", planted, "fr2004")
            parsed = parse_snapshots([artifact], registry=registry)

            # Read off the text by `csv`, touching no adapter code.
            from_text = sorted(
                (
                    FR2004_SOURCE_ID,
                    record["Time Series"].strip(),
                    date.fromisoformat(record["As Of Date"].strip()),
                    "suppressed",
                    artifact.sha256,
                )
                for record in csv.DictReader(io.StringIO(planted.decode("utf-8-sig")))
                if record["Time Series"].strip() in declared
                and record["Value (millions)"].strip() == "*"
            )
            self.assertEqual(
                from_text,
                [
                    (
                        FR2004_SOURCE_ID,
                        suppressed_series,
                        fixture.SUPPRESSED_REF_DATE,
                        "suppressed",
                        artifact.sha256,
                    )
                ],
            )
            self.assertEqual(self.recorded(parsed), from_text)

            # The identity that names the series is not_evaluable, not violated.
            evaluation = validate_accounting_identities(
                list(parsed.rows), {FR2004_SOURCE_ID: registry[FR2004_SOURCE_ID]}
            )["nyfed_fr2004:dealer_treasury_total_is_its_declared_components"]
            self.assertEqual(evaluation.violations, ())
            self.assertEqual(
                [
                    (item.ref_date, item.absent_fields)
                    for item in evaluation.unevaluated
                ],
                [(fixture.SUPPRESSED_REF_DATE, (suppressed_series,))],
            )

        def nyfed_artifacts(rate_payload, volume_payload):
            artifacts = fetch_nyfed_reference_rate(
                self.root / "nyfed",
                "sofr",
                "2026-01-01",
                "2026-01-06",
                lambda url: volume_payload if "type=volume" in url else rate_payload,
            )
            return {
                ("volume" if "type=volume" in item.url else "rate"): item
                for item in artifacts
            }

        with self.subTest(adapter="nyfed"):
            rate = json.dumps(
                {
                    "refRates": [
                        {
                            "effectiveDate": "2026-01-02",
                            "percentRate": 4.31,
                            "percentPercentile1": "",
                            "percentPercentile25": "NA",
                            "percentPercentile75": "N/A",
                            "percentPercentile99": ".",
                        },
                        {
                            # Lower case folds, a JSON null is the empty cell,
                            # and a key the record does not carry is no cell.
                            "effectiveDate": "2026-01-05",
                            "percentRate": 4.30,
                            "percentPercentile1": "na",
                            "percentPercentile25": None,
                            "percentPercentile75": 4.29,
                        },
                    ]
                }
            ).encode()
            volume = json.dumps(
                {
                    "refRates": [
                        {"effectiveDate": "2026-01-02", "volumeInBillions": "."},
                        {"effectiveDate": "2026-01-05", "volumeInBillions": 2000},
                    ]
                }
            ).encode()
            artifacts = nyfed_artifacts(rate, volume)
            parsed = parse_snapshots(list(artifacts.values()), registry=registry)
            rate_sha, volume_sha = artifacts["rate"].sha256, artifacts["volume"].sha256
            self.assertEqual(
                self.recorded(parsed),
                sorted(
                    [
                        ("nyfed_sofr", "SOFR_p1", date(2026, 1, 2), "blank", rate_sha),
                        ("nyfed_sofr", "SOFR_p25", date(2026, 1, 2), "na", rate_sha),
                        ("nyfed_sofr", "SOFR_p75", date(2026, 1, 2), "na", rate_sha),
                        ("nyfed_sofr", "SOFR_p99", date(2026, 1, 2), "dot", rate_sha),
                        ("nyfed_sofr", "SOFR_p1", date(2026, 1, 5), "na", rate_sha),
                        ("nyfed_sofr", "SOFR_p25", date(2026, 1, 5), "blank", rate_sha),
                        ("nyfed_sofr", "SOFR_volume", date(2026, 1, 2), "dot", volume_sha),
                    ]
                ),
            )
            self.assertEqual(
                sorted((row.series_id, row.ref_date, row.value) for row in parsed.rows),
                [
                    ("SOFR", date(2026, 1, 2), 4.31),
                    ("SOFR", date(2026, 1, 5), 4.30),
                    ("SOFR_p75", date(2026, 1, 5), 4.29),
                    ("SOFR_volume", date(2026, 1, 5), 2000.0),
                ],
            )

        fred_payload = b"observation_date,IORB,DFF\n2026-01-02,,.\n2026-01-05,4.30,4.33\n"

        with self.subTest(adapter="fred"):
            artifact = fetch_fred_macro(self.root / "fred", lambda url: fred_payload)[0]
            parsed = parse_snapshots([artifact], registry=registry)
            self.assertEqual(
                self.recorded(parsed),
                [
                    ("fred_macro_latest_vintage", "DFF", date(2026, 1, 2), "dot", artifact.sha256),
                    ("fred_macro_latest_vintage", "IORB", date(2026, 1, 2), "blank", artifact.sha256),
                ],
            )
            self.assertEqual(
                sorted((row.series_id, row.ref_date, row.value) for row in parsed.rows),
                [("DFF", date(2026, 1, 5), 4.33), ("IORB", date(2026, 1, 5), 4.30)],
            )

        def auction(issue, security_type, offering, soma):
            return {
                "issue_date": issue,
                "record_date": issue,
                "auction_date": "2026-01-08",
                "security_type": security_type,
                "offering_amt": offering,
                "soma_accepted": soma,
            }

        treasury_records = [
            auction("2026-01-15", "Bill", "50000000000", "null"),
            auction("2026-01-22", "Note", "25000000000", ""),
            auction("2026-01-29", "Bill", "30000000000", "1000000000"),
        ]

        def treasury_payload(records):
            return json.dumps({"data": records}).encode()

        with self.subTest(adapter="treasury_auctions"):
            artifact = fetch_treasury_auctions(
                self.root / "treasury",
                "2026-01-01",
                "2026-01-31",
                lambda url: treasury_payload(treasury_records),
            )[0]
            parsed = parse_snapshots([artifact], registry=registry)
            self.assertEqual(
                self.recorded(parsed),
                [
                    ("treasury_auctions", "treasury_settlement_soma", date(2026, 1, 15), "null", artifact.sha256),
                    ("treasury_auctions", "treasury_settlement_soma", date(2026, 1, 22), "blank", artifact.sha256),
                ],
            )
            self.assertEqual(
                sorted(
                    row.ref_date
                    for row in parsed.rows
                    if row.series_id == "treasury_settlement_soma"
                ),
                [date(2026, 1, 29)],
            )
            # A withheld announced offering amount still refuses the file.
            withheld = treasury_records + [
                auction("2026-01-29", "Bill", "null", "1000000000")
            ]
            with self.assertRaisesRegex(ValueError, "offering_amt"):
                _treasury_rows(artifact, treasury_payload(withheld))

        bill_url = (
            "https://home.treasury.gov/resource-center/data-chart-center/"
            "interest-rates/TextView?type=daily_treasury_bill_rates"
        )

        def bill_payload(cell):
            return (
                'Date,"4 WEEKS BANK DISCOUNT","4 WEEKS COUPON EQUIVALENT"\n'
                f"09/09/2026,{cell},4.10\n"
                "09/08/2026,4.01,4.11\n"
            ).encode()

        with self.subTest(adapter="treasury_bill_rates"):
            artifact = self.artifact(
                "treasury_bill_rates", "bills.csv", bill_payload(""), bill_url
            )
            parsed = parse_snapshots([artifact], registry=registry)
            self.assertEqual(
                self.recorded(parsed),
                [
                    (
                        "treasury_bill_rates",
                        "tbill_4w_bank_discount",
                        date(2026, 9, 9),
                        "blank",
                        artifact.sha256,
                    )
                ],
            )
            self.assertNotIn(
                ("tbill_4w_bank_discount", date(2026, 9, 9)),
                {(row.series_id, row.ref_date) for row in parsed.rows},
            )

        # -- refusals: a token outside an adapter's own table still refuses
        # the file, each by the message only its adapter writes ------------
        with self.subTest(refusal="sec_nmfp unknown token"):
            payload = self.planted_tsv(
                nmfp_archive(
                    [{"accession": "A1", "series": "S1", "report": "31-JUL-2026"}]
                ),
                "NMFP_SERIESLEVELINFO.tsv",
                {(0, "CASH"): "null"},
            )
            artifact = self.artifact("sec_nmfp", "unknown.zip", payload, nmfp_url)
            with self.assertRaisesRegex(
                ValueError, r"SEC Form N-MFP CASH value is not numeric: 'null'"
            ):
                parse_snapshots([artifact], registry=registry)

        with self.subTest(refusal="nyfed unknown token"):
            artifacts = nyfed_artifacts(
                b'{"refRates":[{"effectiveDate":"2026-01-02","percentRate":"*"}]}',
                b'{"refRates":[]}',
            )
            with self.assertRaisesRegex(
                ValueError, "New York Fed percentRate is not numeric"
            ):
                _nyfed_rows(artifacts["rate"], artifacts["rate"].path.read_bytes())

        with self.subTest(refusal="nyfed_fr2004 unknown token"):
            blank = text.replace(
                '"2026-08-26","PDPOSGST-TOT","477607"',
                '"2026-08-26","PDPOSGST-TOT",""',
            ).encode()
            self.assertNotEqual(blank, text.encode())
            with self.assertRaisesRegex(
                ValueError, r"only '\*' marks a suppressed value"
            ):
                _fr2004_rows(
                    self.artifact(FR2004_SOURCE_ID, "blank.csv", blank, "fr2004"),
                    blank,
                    registry,
                )

        with self.subTest(refusal="fred unknown token"):
            payload = b"observation_date,IORB\n2026-01-02,NA\n"
            artifact = self.artifact(
                "fred_macro_latest_vintage", "fred.csv", payload, "fred"
            )
            with self.assertRaisesRegex(ValueError, "FRED IORB is not numeric"):
                _fred_rows(artifact, payload)

        with self.subTest(refusal="treasury_auctions unknown token"):
            payload = treasury_payload(
                [auction("2026-01-15", "Bill", "50000000000", "NULL")]
            )
            artifact = self.artifact("treasury_auctions", "t.json", payload, "fiscal")
            with self.assertRaisesRegex(
                ValueError, "has a non-numeric soma_accepted: 'NULL'"
            ):
                _treasury_rows(artifact, payload)

        with self.subTest(refusal="treasury_bill_rates unknown token"):
            payload = bill_payload(".")
            artifact = self.artifact("treasury_bill_rates", "b.csv", payload, bill_url)
            with self.assertRaisesRegex(
                ValueError, r"has a non-numeric '4 WEEKS BANK DISCOUNT' cell: '\.'"
            ):
                _treasury_bill_rate_rows(artifact, payload, registry)

        # -- refusal: an adapter emitting a reason outside the vocabulary -----
        with self.subTest(refusal="reason outside the vocabulary"):
            artifact = self.artifact(
                "fred_macro_latest_vintage", "fred-vocab.csv", fred_payload, "fred"
            )
            with mock.patch.dict(ingest.FRED_ABSENT_TOKENS, {".": "missing"}):
                with self.assertRaisesRegex(
                    ValueError, r"absence reason 'missing' is outside the vocabulary"
                ):
                    _fred_rows(artifact, fred_payload, absent_cells=[])


class AbsentCellRunTests(unittest.TestCase):
    """A19: absent cells are recorded as runs, and the runs expand back exactly.

    A18's quality report listed every absent cell as its own object. It now
    writes `absent_cells.runs`: one `data.AbsentCellRun` per source, snapshot
    (`source_sha`), field and reason, over a maximal stretch of consecutive rows
    in the adapter's own row sequence -- the rows it read that field at, in the
    order it read them -- with the first and last date, the number of rows, and
    the row the stretch starts at. `absent_cells.counts`, one per reason, stays,
    summed from the runs.

    The runs are built by `data.AbsentCellRecorder`, which `ingest._read_cell`
    now tells about every value it reads as well as every absence: a value row
    is what ends a run, and nothing but that read knows the row was there. A
    date the source never wrote a row for is not a row, so a weekend or a
    holiday neither ends a run nor counts in one. They are read back by
    `data.absent_cells_from_quality_report`, which expands each run over the
    snapshots' row sequences (`parse_snapshots(..., keep_row_dates=True)`) and
    refuses a run whose `count` rows, taken from `row`, do not run from `first`
    to `last`.

    Why a run also carries `row`
    ----------------------------

    The brief named a first date, a last date and a count. Those three do not
    place a run when a field's row sequence repeats a date or is not in date
    order, and two adapters' sequences are both. Form N-MFP reads one row per
    filer, many filers share a `REPORTDATE`, and filer order is not date order;
    Treasury auctions read one row per auction, and auctions share an
    `issue_date`. Rows dated d1, d1, d2, d2 that are absent at positions 0-2 or
    at 1-3 are both "d1 to d2, three rows", and they expand to different cells.
    `row` places the run, and `first` and `last` are what the read-back checks
    it against. A run records where its rows are, not each row's date, so the
    snapshot it was read from is what expands it: the report alone does not.

    What it found on the tracked inputs
    -----------------------------------

    `repo_model.cli build` over `tests/fixtures/snapshots/funding_inputs/`,
    python3 3.9.6, before and after, both with the columns
    `metadata/funding_panel_manifest.json` records and with none. The quality
    report went from 11,885,055 bytes (`fda80909...`) to 65,576 bytes
    (`6a4466a5...`): 49036 absent cells in 195 runs, the counts unchanged at
    49028 `blank` and 8 `na`. No panel byte moved: the pinned panel is
    `b6af33bb...4bec`, the default build `d6e9a2b2...af16` and the long
    point-in-time panel `ef76551d...981e`, each the same before and after.
    Expanding the 195 runs over that parse's row sequences gives back the 49036
    cells exactly. By field: `RRPONTSYD` 183 runs, `IOER` 2 (19824 rows from
    1954-07-01 and 1868 from 2021-07-29), `IORB` 1, `DFF` 1, and each of the
    four SOFR percentiles 2.

    Mutation record
    ---------------

    11 September 2026, python3 3.9.6. Disposable copies under `$HOME`, one per
    mutation, each built from `git ls-files -z --cached --others
    --exclude-standard`; `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`, whole suite
    per mutation. Each replacement was asserted to occur exactly once and then
    confirmed present in the file before the run. The unmutated control is
    green before and after, with no expected failures.

    1. **Runs split only on reason, never on an intervening value**:
       `AbsentCellRecorder._read` returns on a value before it looks at the
       open run. Killed this test only: the "blanks, a value, blanks" subtest,
       `AssertionError` ("Lists differ": one run of four rows from 2026-01-05 to
       -01-09), and the refusal subtest, `AssertionError` ("ValueError not
       raised"). The second is incidental: the merged run spans all five rows,
       so one row more than it records still ends on its last date.
    2. **Runs keyed without the snapshot sha**: the open-run key
       `(source_id, field)`, row sequences still per snapshot. Killed this test
       only: the expansion subtest, `AssertionError` ("Lists differ"), where the
       FRED retrieval that ends on an `IORB` blank and the one that begins with
       one become a single two-row run carrying the first retrieval's sha. A
       first attempt dropped the sha from the row-sequence key too, and was
       killed by the read-back's `ValueError` ("0 rows") on the first fixture
       instead, a lookup miss rather than the merge; the key was split so this
       mutation reaches the run alone.
    3. **Count as calendar days between first and last**:
       `(last - first).days + 1`. Killed the "dates the source skips" subtest,
       `AssertionError` (6 for three rows), and the expansion subtest,
       `AssertionError` ("Lists differ": N-MFP's same-day runs of two expand to
       one). It also kills `AbsentValueReasonTests`' `sec_nmfp` subtest,
       `AssertionError` on the report's counts (`na` 2 for 3), rightly: those
       counts are now summed from the runs.
    4. **The read-back count check removed**: its `if` made `if False:`.
       Killed this test only: the refusal subtest, `AssertionError`
       ("ValueError not raised").
    """

    RETRIEVED_AT = AbsentValueReasonTests.RETRIEVED_AT
    FRED = "fred_macro_latest_vintage"

    setUp = AbsentValueReasonTests.setUp
    artifact = AbsentValueReasonTests.artifact
    planted_tsv = staticmethod(AbsentValueReasonTests.planted_tsv)
    nmfp_payload = AbsentValueReasonTests.nmfp_payload

    @staticmethod
    def runs(parsed):
        return [
            (run.field, run.reason, run.first, run.last, run.count, run.row)
            for run in parsed.absent_cell_runs
        ]

    @staticmethod
    def cells(cells):
        return sorted(
            (cell.source_id, cell.field, cell.ref_date, cell.reason, cell.source_sha)
            for cell in cells
        )

    def quality_report(self, parsed, name):
        """The quality report for `parsed`, as written to disk and read back."""

        from repo_model.data import write_point_in_time_audit_report

        path = self.root / f"{name}.quality.json"
        write_point_in_time_audit_report(
            parsed.rows, path, absent_cell_runs=parsed.absent_cell_runs
        )
        return json.loads(path.read_text(encoding="utf-8"))

    def test_absent_cells_collapse_into_runs_that_expand_back_exactly(self):
        from repo_model.ingest import load_source_registry

        registry = load_source_registry()

        def fred(name, text):
            payload = text.encode("utf-8")
            return self.artifact(self.FRED, name, payload, "fred")

        with self.subTest("blanks, a value, blanks: two runs"):
            parsed = parse_snapshots(
                [
                    fred(
                        "split.csv",
                        "observation_date,IORB\n"
                        "2026-01-05,\n2026-01-06,\n2026-01-07,4.30\n"
                        "2026-01-08,\n2026-01-09,\n",
                    )
                ],
                registry=registry,
            )
            self.assertEqual(
                self.runs(parsed),
                [
                    ("IORB", "blank", date(2026, 1, 5), date(2026, 1, 6), 2, 0),
                    ("IORB", "blank", date(2026, 1, 8), date(2026, 1, 9), 2, 3),
                ],
            )

        with self.subTest("a change of reason splits the run"):
            parsed = parse_snapshots(
                [
                    fred(
                        "reasons.csv",
                        "observation_date,IORB\n"
                        "2026-01-05,\n2026-01-06,.\n2026-01-07,.\n2026-01-08,\n",
                    )
                ],
                registry=registry,
            )
            self.assertEqual(
                self.runs(parsed),
                [
                    ("IORB", "blank", date(2026, 1, 5), date(2026, 1, 5), 1, 0),
                    ("IORB", "dot", date(2026, 1, 6), date(2026, 1, 7), 2, 1),
                    ("IORB", "blank", date(2026, 1, 8), date(2026, 1, 8), 1, 3),
                ],
            )

        bill_url = (
            "https://home.treasury.gov/resource-center/data-chart-center/"
            "interest-rates/TextView?type=daily_treasury_bill_rates"
        )

        with self.subTest("dates the source skips neither split nor count"):
            # A business-daily FRED column: Friday 16 January, then Tuesday 20
            # January -- a weekend and Martin Luther King Day are not rows.
            parsed = parse_snapshots(
                [
                    fred(
                        "business.csv",
                        "observation_date,RRPONTSYD\n"
                        "2026-01-15,1.5\n2026-01-16,\n2026-01-20,\n"
                        "2026-01-21,\n2026-01-22,2.0\n",
                    )
                ],
                registry=registry,
            )
            self.assertEqual(
                self.runs(parsed),
                [("RRPONTSYD", "blank", date(2026, 1, 16), date(2026, 1, 21), 3, 1)],
            )
            # Treasury's bill rates are written newest first, and a run's first
            # and last follow the file: Monday 12 January, then Friday 9.
            bills = (
                'Date,"4 WEEKS BANK DISCOUNT","4 WEEKS COUPON EQUIVALENT"\n'
                "01/12/2026,,4.10\n01/09/2026,,4.11\n01/08/2026,4.01,4.12\n"
            ).encode()
            parsed = parse_snapshots(
                [self.artifact("treasury_bill_rates", "bills.csv", bills, bill_url)],
                registry=registry,
            )
            self.assertEqual(
                self.runs(parsed),
                [
                    (
                        "tbill_4w_bank_discount",
                        "blank",
                        date(2026, 1, 12),
                        date(2026, 1, 9),
                        2,
                        0,
                    )
                ],
            )

        with self.subTest("every run over each A18 fixture expands back exactly"):
            fixtures = {}

            # sec_nmfp: AbsentValueReasonTests.nmfp_payload, which it builds.
            fixtures["sec_nmfp"] = (
                [
                    self.artifact(
                        "sec_nmfp",
                        "a18.zip",
                        self.nmfp_payload(),
                        "https://www.sec.gov/files/dera/data/form-n-mfp-data-sets/a18.zip",
                    )
                ],
                json.loads(
                    registry_with_nmfp_coverage_floor(self.root, 1).read_text()
                ),
            )

            # nyfed_fr2004: the tracked export plus A18's planted week, one
            # declared series suppressed.
            dealer = FR2004DealerPositionTests
            text = dealer.FIXTURE.read_text(encoding="utf-8")
            real_week = {
                row.series_id: row.value
                for row in parse_snapshots(
                    [
                        self.artifact(
                            FR2004_SOURCE_ID, "real.csv", text.encode(), "fr2004"
                        )
                    ],
                    registry=registry,
                ).rows
                if row.ref_date == dealer.REF_DATE
            }
            lines = [text.rstrip("\n")]
            for series_id in (dealer.TOTAL_SERIES, *dealer.COMPONENTS):
                raw = (
                    "*"
                    if series_id == "PDPOSTIPS-G11"
                    else str(round(real_week[series_id] * 1000))
                )
                lines.append(
                    f'"{dealer.SUPPRESSED_REF_DATE.isoformat()}","{series_id}","{raw}"'
                )
            fixtures["nyfed_fr2004"] = (
                [
                    self.artifact(
                        FR2004_SOURCE_ID,
                        "latest.csv",
                        ("\n".join(lines) + "\n").encode("utf-8"),
                        "fr2004",
                    )
                ],
                registry,
            )

            # nyfed: A18's rate and volume responses.
            rate = json.dumps(
                {
                    "refRates": [
                        {
                            "effectiveDate": "2026-01-02",
                            "percentRate": 4.31,
                            "percentPercentile1": "",
                            "percentPercentile25": "NA",
                            "percentPercentile75": "N/A",
                            "percentPercentile99": ".",
                        },
                        {
                            "effectiveDate": "2026-01-05",
                            "percentRate": 4.30,
                            "percentPercentile1": "na",
                            "percentPercentile25": None,
                            "percentPercentile75": 4.29,
                        },
                    ]
                }
            ).encode()
            volume = json.dumps(
                {
                    "refRates": [
                        {"effectiveDate": "2026-01-02", "volumeInBillions": "."},
                        {"effectiveDate": "2026-01-05", "volumeInBillions": 2000},
                    ]
                }
            ).encode()
            fixtures["nyfed"] = (
                fetch_nyfed_reference_rate(
                    self.root / "nyfed",
                    "sofr",
                    "2026-01-01",
                    "2026-01-06",
                    lambda url: volume if "type=volume" in url else rate,
                ),
                registry,
            )

            # fred: A18's payload, read beside a second retrieval that ends on
            # the blank A18's begins with. Two snapshots are two runs.
            earlier = fred(
                "earlier.csv",
                "observation_date,IORB,DFF\n2026-01-05,4.30,4.33\n2026-01-06,,4.33\n",
            )
            later = fred(
                "later.csv",
                "observation_date,IORB,DFF\n2026-01-02,,.\n2026-01-05,4.30,4.33\n",
            )
            fixtures["fred"] = ([earlier, later], registry)

            # treasury_auctions: A18's three auction records.
            def auction(issue, security_type, offering, soma):
                return {
                    "issue_date": issue,
                    "record_date": issue,
                    "auction_date": "2026-01-08",
                    "security_type": security_type,
                    "offering_amt": offering,
                    "soma_accepted": soma,
                }

            records = [
                auction("2026-01-15", "Bill", "50000000000", "null"),
                auction("2026-01-22", "Note", "25000000000", ""),
                auction("2026-01-29", "Bill", "30000000000", "1000000000"),
            ]
            fixtures["treasury_auctions"] = (
                fetch_treasury_auctions(
                    self.root / "treasury",
                    "2026-01-01",
                    "2026-01-31",
                    lambda url: json.dumps({"data": records}).encode(),
                ),
                registry,
            )

            # treasury_bill_rates: A18's two quote dates.
            fixtures["treasury_bill_rates"] = (
                [
                    self.artifact(
                        "treasury_bill_rates",
                        "a18-bills.csv",
                        (
                            'Date,"4 WEEKS BANK DISCOUNT","4 WEEKS COUPON EQUIVALENT"\n'
                            "09/09/2026,,4.10\n09/08/2026,4.01,4.11\n"
                        ).encode(),
                        bill_url,
                    )
                ],
                registry,
            )

            for adapter, (artifacts, adapter_registry) in fixtures.items():
                parsed = parse_snapshots(
                    artifacts, registry=adapter_registry, keep_row_dates=True
                )
                self.assertTrue(parsed.absent_cells, adapter)
                if adapter == "fred":
                    # No run crosses from one retrieval into the next.
                    self.assertEqual(
                        sorted(
                            (
                                run.source_sha,
                                run.field,
                                run.reason,
                                run.first,
                                run.count,
                                run.row,
                            )
                            for run in parsed.absent_cell_runs
                        ),
                        sorted(
                            [
                                (earlier.sha256, "IORB", "blank", date(2026, 1, 6), 1, 1),
                                (later.sha256, "DFF", "dot", date(2026, 1, 2), 1, 0),
                                (later.sha256, "IORB", "blank", date(2026, 1, 2), 1, 0),
                            ]
                        ),
                    )
                report = self.quality_report(parsed, adapter)
                self.assertEqual(
                    self.cells(
                        absent_cells_from_quality_report(
                            report, parsed.absent_cell_row_dates
                        )
                    ),
                    self.cells(parsed.absent_cells),
                    adapter,
                )
                # The per-reason counts are still the cells', one each.
                counts = {reason: 0 for reason in report["absent_cells"]["counts"]}
                for cell in parsed.absent_cells:
                    counts[cell.reason] += 1
                self.assertEqual(report["absent_cells"]["counts"], counts, adapter)

        with self.subTest(refusal="a run's count disagrees with its rows"):
            parsed = parse_snapshots(
                [
                    fred(
                        "tampered.csv",
                        "observation_date,IORB\n"
                        "2026-01-05,\n2026-01-06,\n2026-01-07,4.30\n"
                        "2026-01-08,\n2026-01-09,\n",
                    )
                ],
                registry=registry,
                keep_row_dates=True,
            )
            report = self.quality_report(parsed, "tampered")
            # One more row than the stretch has, with the per-reason count
            # moved to agree, so only the run itself can say it is wrong.
            report["absent_cells"]["runs"][0]["count"] += 1
            report["absent_cells"]["counts"]["blank"] += 1
            with self.assertRaisesRegex(
                ValueError,
                r"IORB blank at row 0 records 3 rows from 2026-01-05 to "
                r"2026-01-06, and its snapshot's rows from row 0 do not",
            ):
                absent_cells_from_quality_report(report, parsed.absent_cell_row_dates)


if __name__ == "__main__":
    unittest.main()
