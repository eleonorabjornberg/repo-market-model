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
    SnapshotArtifact,
    _decode_transport,
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
    and optional `net_assets` (USD, not billions) and `flows`, a sequence of
    `(flow_date, subscriptions, redemptions)`. The tables carry the same column
    names and the same DD-MON-YYYY dates as the SEC extract, so a fixture cannot
    pass by agreeing with the parser about a format the source does not use.
    """

    submission_rows = ["ACCESSION_NUMBER\tSERIESID\tREPORTDATE"]
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
            f"{entry['accession']}\t{entry['series']}\t{entry['report']}"
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
                "ACCESSION_NUMBER\tSERIESID\tREPORTDATE\nA1\tS1\t31-JUL-2026\n",
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
