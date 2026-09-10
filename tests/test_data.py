import hashlib
import sys
import tempfile
import unittest
import json
from dataclasses import fields
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from repo_model.data import (
    build_daily_panel,
    write_daily_panel,
    DataContractError,
    PointInTimeObservation,
    audit_point_in_time_panel,
    audit_panel,
    declared_coverage_floor,
    declared_structural_zeros,
    expected_ref_dates_from_registry,
    fixed_bp_stress_label_columns,
    load_daily_panel,
    load_point_in_time_panel,
    stress_label_threshold,
    validate_publication_gaps,
    validate_accounting_identities,
    verify_daily_panel,
    write_point_in_time_audit_report,
)

# The N-MFP fixture helpers live beside the adapter tests that own them. Imported
# rather than copied: a second archive builder would be a second thing to keep
# in step with the SEC layout, and the copy that drifted would be the one still
# passing. `tests/` is on the path under `unittest discover -s tests`; the insert
# is what makes `python3 -m unittest tests.test_data` agree with it.
sys.path.insert(0, str(Path(__file__).parents[0]))

from repo_model.ingest import build_point_in_time_snapshot, fetch_sec_nmfp
from test_ingest import nmfp_archive, registry_with_nmfp_coverage_floor


def manifest_digest(manifest_path: Path) -> str:
    """The `sha256` a manifest records, read without `data.py` in between."""

    return json.loads(manifest_path.read_text(encoding="utf-8"))["sha256"]



class DataContractTests(unittest.TestCase):
    def write_csv(self, contents: str) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "panel.csv"
        path.write_text(contents, encoding="utf-8")
        return path

    def test_load_and_audit(self):
        path = self.write_csv(
            "date,sofr,iorb,sofr_p25,sofr_p75,reserve_balances\n"
            "2026-01-02,4.31,4.30,4.30,4.32,3200\n"
            "2026-01-05,4.33,4.30,4.31,4.34,3190\n"
        )
        rows = load_daily_panel(path)
        report = audit_panel(rows)
        self.assertEqual(report.row_count, 2)
        self.assertAlmostEqual(rows[0].spread_bps, 1.0)
        self.assertEqual(report.warnings, [])

    def test_rejects_unsorted_dates(self):
        path = self.write_csv(
            "date,sofr,iorb\n"
            "2026-01-05,4.33,4.30\n"
            "2026-01-02,4.31,4.30\n"
        )
        with self.assertRaisesRegex(DataContractError, "sorted"):
            audit_panel(load_daily_panel(path))

    def test_warns_on_impossible_percentiles(self):
        path = self.write_csv(
            "date,sofr,iorb,sofr_p25,sofr_p75\n"
            "2026-01-02,4.31,4.30,4.35,4.30\n"
        )
        report = audit_panel(load_daily_panel(path))
        self.assertEqual(len(report.warnings), 1)


class PointInTimeDataContractTests(unittest.TestCase):
    SHA = "a" * 64

    def write_csv(self, contents: str) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "panel.csv"
        path.write_text(contents, encoding="utf-8")
        return path

    def test_cutoff_uses_available_at_not_reference_date(self):
        path = self.write_csv(
            "series_id,ref_date,available_at,value,vintage_id,source_sha\n"
            f"IORB,2026-01-01,2026-01-02T12:00:00+00:00,4.30,v1,{self.SHA}\n"
            f"IORB,2026-01-02,2026-01-05T12:00:00+00:00,4.31,v2,{self.SHA}\n"
        )

        rows = load_point_in_time_panel(
            path,
            cutoff=datetime(2026, 1, 3, tzinfo=timezone.utc),
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].ref_date.isoformat(), "2026-01-01")

    def test_rejects_available_at_without_timezone(self):
        path = self.write_csv(
            "series_id,ref_date,available_at,value,vintage_id,source_sha\n"
            f"IORB,2026-01-01,2026-01-02T12:00:00,4.30,v1,{self.SHA}\n"
        )

        with self.assertRaisesRegex(DataContractError, "UTC offset"):
            load_point_in_time_panel(path)

    def test_rejects_invalid_source_checksum(self):
        path = self.write_csv(
            "series_id,ref_date,available_at,value,vintage_id,source_sha\n"
            "IORB,2026-01-01,2026-01-02T12:00:00Z,4.30,v1,not-a-sha\n"
        )

        with self.assertRaisesRegex(DataContractError, "SHA-256"):
            load_point_in_time_panel(path)

    def observation(self, series, ref_date, available_at, value, vintage):
        return PointInTimeObservation(
            series_id=series,
            ref_date=date.fromisoformat(ref_date),
            available_at=datetime.fromisoformat(available_at),
            value=value,
            vintage_id=vintage,
            source_sha=self.SHA,
        )

    def test_missingness_and_revision_report_keeps_the_two_distinct(self):
        rows = [
            self.observation("A", "2026-01-01", "2026-01-02T12:00:00+00:00", 1, "v1"),
            self.observation("B", "2026-01-02", "2026-01-02T12:01:00+00:00", 2, "v1"),
            self.observation("A", "2026-01-01", "2026-01-03T12:00:00+00:00", 1.5, "v2"),
        ]
        report = audit_point_in_time_panel(rows)
        self.assertEqual(report.series["A"].missing_reference_dates, 1)
        self.assertEqual(report.series["A"].revised_reference_dates, 1)
        self.assertEqual(report.series["A"].revision_rows, 1)
        self.assertEqual(report.series["A"].largest_absolute_revision, 0.5)

    def test_quality_report_is_machine_readable_json(self):
        rows = [
            self.observation("A", "2026-01-01", "2026-01-02T12:00:00+00:00", 1, "v1")
        ]
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        output = Path(directory.name) / "quality.json"
        write_point_in_time_audit_report(rows, output)
        self.assertEqual(json.loads(output.read_text())["series"]["A"]["observations"], 1)

    def test_publication_gap_is_checked_against_registry_bound(self):
        rows = [
            self.observation("A", "2026-01-01", "2026-01-08T12:00:00+00:00", 1, "v1")
        ]
        registry = {
            "source": {
                "fields": ["A"],
                "release_lag": {
                    "basis": "ref_date",
                    "worst_case_calendar_days": 6,
                },
            }
        }
        with self.assertRaisesRegex(DataContractError, "published 7 calendar days"):
            validate_publication_gaps(rows, registry)

    def test_missingness_grid_uses_same_source_and_frequency_peer(self):
        rows = [
            self.observation("daily_anchor", "2026-01-01", "2026-01-02T12:00:00+00:00", 1, "v1"),
            self.observation("daily_anchor", "2026-01-02", "2026-01-03T12:00:00+00:00", 1, "v2"),
            self.observation("daily_sparse", "2026-01-01", "2026-01-03T12:01:00+00:00", 1, "v1"),
            self.observation("weekly", "2026-01-01", "2026-01-03T12:02:00+00:00", 1, "v1"),
            self.observation("daily_anchor", "2026-01-03", "2026-01-04T12:00:00+00:00", 1, "v3"),
            self.observation("daily_sparse", "2026-01-03", "2026-01-04T12:01:00+00:00", 1, "v2"),
        ]
        registry = {
            "source": {
                "field_frequencies": {
                    "daily_anchor": "business_daily",
                    "daily_sparse": "business_daily",
                    "weekly": "weekly",
                    "weekly_absent": "weekly",
                },
                "fields": [
                    "daily_anchor", "daily_sparse", "weekly", "weekly_absent"
                ],
            }
        }
        expected = expected_ref_dates_from_registry(rows, registry)
        report = audit_point_in_time_panel(rows, expected_ref_dates=expected)
        self.assertEqual(report.series["daily_sparse"].missing_reference_dates, 1)
        self.assertEqual(report.series["weekly"].missing_reference_dates, 0)
        self.assertEqual(report.missing_series["weekly_absent"], 1)

    def test_accounting_identity_uses_latest_vintages_and_declared_tolerance(self):
        rows = [
            self.observation("assets", "2026-01-01", "2026-01-02T12:00:00+00:00", 10, "v1"),
            self.observation("liabilities", "2026-01-01", "2026-01-02T12:01:00+00:00", 4, "v1"),
            self.observation("equity", "2026-01-01", "2026-01-02T12:02:00+00:00", 5, "v1"),
            self.observation("equity", "2026-01-01", "2026-01-03T12:00:00+00:00", 6, "v2"),
        ]
        registry = {
            "source": {
                "identities": [{
                    "name": "balance_sheet",
                    "left": ["assets"],
                    "right": ["liabilities", "equity"],
                    "tolerance": {"absolute": 0.01, "unit": "USD"},
                }]
            }
        }
        evaluations = validate_accounting_identities(rows, registry)
        self.assertEqual(evaluations["source:balance_sheet"].maximum_residual, 0.0)
        bad = dict(registry)
        bad["source"] = dict(registry["source"])
        bad["source"]["identities"] = [dict(registry["source"]["identities"][0])]
        bad["source"]["identities"][0]["tolerance"] = {"absolute": 0.0, "unit": "USD"}
        # A residual outside the declared tolerance is rejected as a verdict
        # rather than an exception since the violation-verdict block; the
        # rejection is the same, the channel is not. See `IdentityVerdictTests`.
        rejected = validate_accounting_identities(rows[:-1], bad)["source:balance_sheet"]
        self.assertEqual(rejected.verdict, "violated")
        self.assertEqual(rejected.violated_ref_dates, (date(2026, 1, 1),))
        self.assertAlmostEqual(rejected.violations[0].residual, 1.0)
        self.assertEqual(rejected.violations[0].bound, 0.0)

    def test_a_relative_tolerance_is_the_same_rule_at_every_scale(self):
        """The property an absolute bound cannot have.

        One absolute number on a quantity that moves by orders of magnitude is
        not a tolerance: calibrated on the largest cross-section it is
        unfalsifiable on the smallest, and calibrated on the smallest it fails
        the largest. So this fixture holds the residual at a fixed *fraction*
        of the identity's own magnitude and moves the magnitude, which is
        exactly the move a per-month panel makes on its own. A relative bound
        must give the same verdict at both scales; an absolute one cannot.

        Both halves are asserted. Only checking that the big scale holds would
        pass for a bound of infinity, and only checking that the small scale
        fails would pass for a bound of zero.
        """

        def rows_at(scale, residual_fraction):
            left = scale
            right = scale * (1.0 - residual_fraction)
            return [
                self.observation("assets", "2026-01-01", "2026-01-02T12:00:00+00:00", left, "v1"),
                self.observation("liabilities", "2026-01-01", "2026-01-02T12:01:00+00:00", right, "v1"),
            ]

        def registry_with(tolerance):
            return {
                "source": {
                    "identities": [{
                        "name": "one_sided",
                        "left": ["assets"],
                        "right": ["liabilities"],
                        "tolerance": tolerance,
                    }]
                }
            }

        relative = registry_with({"relative_ppm": 500, "absolute": 1e-9, "unit": "USD billions"})
        # 100 ppm of the identity's own magnitude, five times inside the bound,
        # at two scales four orders of magnitude apart.
        for scale in (2.0, 9000.0):
            with self.subTest(scale=scale, tolerance="relative"):
                evaluations = validate_accounting_identities(
                    rows_at(scale, 100e-6), relative
                )
                self.assertEqual(evaluations["source:one_sided"].evaluated_ref_dates, 1)

        # And the absolute bound that would be calibrated from the large scale,
        # against a small cross-section that is 20% wrong. It passes, because
        # 0.5 is a quarter of the whole cross-section: at that scale there is
        # no residual the bound could reject, so its verdict carries no
        # information. The relative bound rejects the same rows.
        absolute = registry_with({"absolute": 0.5, "unit": "USD billions"})
        wildly_broken = rows_at(2.0, 0.2)
        with self.subTest(tolerance="absolute", scale=2.0):
            evaluations = validate_accounting_identities(wildly_broken, absolute)
            self.assertEqual(evaluations["source:one_sided"].evaluated_ref_dates, 1)
        with self.subTest(tolerance="relative", scale=2.0):
            rejected = validate_accounting_identities(wildly_broken, relative)[
                "source:one_sided"
            ]
            self.assertEqual(rejected.verdict, "violated")
            self.assertEqual(rejected.violated_ref_dates, (date(2026, 1, 1),))
            self.assertAlmostEqual(rejected.violations[0].residual, 0.4)

    def test_the_scale_is_the_larger_side_and_not_the_left_one(self):
        """Which side the scale comes from, pinned because nothing else pins it.

        Written after a mutation that was expected to be boring and was:
        taking the scale from `left` alone instead of from the larger side
        killed nothing in the suite. That is a finding about the tests, not a
        mutation to discard -- every other fixture here has two sides of nearly
        equal magnitude, so the choice was free.

        It stops being free when the sides differ, which is exactly when an
        identity is close to failing. So this fixture makes them differ by a
        factor of two and puts the bound between the two candidate scales: the
        larger side admits the residual, the left side alone rejects it. The
        percentages are artificial because the rule is, and a rule tested only
        at values where it does not matter is not tested.
        """

        rows = [
            self.observation("assets", "2026-01-01", "2026-01-02T12:00:00+00:00", 1.0, "v1"),
            self.observation("liabilities", "2026-01-01", "2026-01-02T12:01:00+00:00", 2.0, "v1"),
        ]
        registry = {
            "source": {
                "identities": [{
                    "name": "lopsided",
                    "left": ["assets"],
                    "right": ["liabilities"],
                    # 60% of the larger side is 1.2 and admits the residual of
                    # 1.0; 60% of the left side is 0.6 and does not.
                    "tolerance": {"relative_ppm": 600000, "unit": "USD billions"},
                }]
            }
        }
        evaluations = validate_accounting_identities(rows, registry)
        self.assertEqual(evaluations["source:lopsided"].evaluated_ref_dates, 1)
        self.assertAlmostEqual(evaluations["source:lopsided"].maximum_residual, 1.0)

    def test_an_identity_with_an_unobserved_term_is_recorded_unevaluated_not_satisfied(
        self,
    ):
        """An identity that could not be checked must not read as one that held.

        The defect this pins, in the panel it was found in: `sec_nmfp` declares
        a balance-sheet identity over five terms, and `CASH` and
        `TOTALVALUEPORTFOLIOSECURITIES` are empty in every archive before the
        2016-04 report month. Those months were not violating the identity and
        were not passing it -- they never reached it, because the check iterated
        the intersection of the terms' reference dates. The panel reported one
        maximum residual, the quality report reported no violation, and a reader
        concluded a balance sheet reconciled over history where two of its three
        left-hand terms had no observation at all.

        So this asserts the distinction itself rather than any count: the same
        fixture with a term withheld and with every term present must give
        answers a caller can tell apart, and the withheld one must name the term
        that was missing. Both halves are load-bearing. Without the second, an
        implementation that reported everything unevaluable would pass; without
        the first, one that reported everything held would.

        Fixture-based, so it holds in a fresh clone with an empty `data/raw/`.
        """

        def panel(with_equity_on_second_date: bool):
            rows = [
                self.observation(
                    "assets", "2026-01-01", "2026-01-02T12:00:00+00:00", 10.0, "v1"
                ),
                self.observation(
                    "liabilities", "2026-01-01", "2026-01-02T12:01:00+00:00", 4.0, "v1"
                ),
                self.observation(
                    "equity", "2026-01-01", "2026-01-02T12:02:00+00:00", 6.0, "v1"
                ),
                self.observation(
                    "assets", "2026-02-01", "2026-02-02T12:00:00+00:00", 12.0, "v1"
                ),
                self.observation(
                    "liabilities", "2026-02-01", "2026-02-02T12:01:00+00:00", 5.0, "v1"
                ),
            ]
            if with_equity_on_second_date:
                rows.append(
                    self.observation(
                        "equity", "2026-02-01", "2026-02-02T12:02:00+00:00", 7.0, "v1"
                    )
                )
            return rows

        registry = {
            "source": {
                "identities": [
                    {
                        "name": "balance_sheet",
                        "left": ["assets"],
                        "right": ["liabilities", "equity"],
                        "tolerance": {"absolute": 0.01, "unit": "USD"},
                    }
                ]
            }
        }

        withheld = validate_accounting_identities(panel(False), registry)[
            "source:balance_sheet"
        ]
        complete = validate_accounting_identities(panel(True), registry)[
            "source:balance_sheet"
        ]

        # Every term present on every date: checked throughout, and it held.
        self.assertEqual(complete.verdict, "held")
        self.assertTrue(complete.fully_evaluated)
        self.assertEqual(complete.unevaluated, ())
        self.assertEqual(complete.evaluated_ref_dates, 2)

        # One term withheld on one date: that date is not reported as satisfied,
        # and the verdict of the identity as a whole is no longer `held`.
        self.assertNotEqual(withheld.verdict, complete.verdict)
        self.assertNotEqual(withheld.verdict, "held")
        self.assertFalse(withheld.fully_evaluated)
        self.assertEqual(withheld.evaluated_ref_dates, 1)

        # And the absent term is named, per reference date. A verdict that says
        # "this did not evaluate" without saying what was missing is a claim a
        # reader cannot act on.
        self.assertEqual(len(withheld.unevaluated), 1)
        unevaluated = withheld.unevaluated[0]
        self.assertEqual(unevaluated.ref_date, date(2026, 2, 1))
        self.assertEqual(unevaluated.absent_fields, ("equity",))
        self.assertEqual(withheld.absent_fields, ("equity",))
        self.assertEqual(unevaluated.as_dict()["verdict"], "not_evaluable")
        self.assertEqual(unevaluated.as_dict()["absent_fields"], ["equity"])

        # The reference date that did evaluate is unchanged by the other one
        # having been withheld: it held, with the residual it always had.
        self.assertEqual(withheld.maximum_residual, 0.0)

        # And the record reaches the quality report a reader actually opens,
        # beside the coverage decision rather than folded into it.
        report = audit_point_in_time_panel(
            panel(False), unevaluated_identities=withheld.unevaluated
        ).as_dict()
        self.assertEqual(len(report["unevaluated_identities"]), 1)
        self.assertEqual(
            report["unevaluated_identities"][0]["absent_fields"], ["equity"]
        )
        self.assertEqual(
            report["unevaluated_identities"][0]["ref_date"], "2026-02-01"
        )


class StressLabelTests(unittest.TestCase):
    def test_fixed_bp_labels_use_strict_exceedance(self):
        declaration = {"primary_rule": "fixed_bp", "taus_bp": [5, 10, 20, 50]}

        rows = fixed_bp_stress_label_columns([5.0, 10.01, 51.0], declaration)

        self.assertEqual(rows[0]["stress_gt_5bp"], 0)
        self.assertEqual(rows[1]["stress_gt_5bp"], 1)
        self.assertEqual(rows[1]["stress_gt_10bp"], 1)
        self.assertEqual(rows[1]["stress_gt_20bp"], 0)
        self.assertEqual(rows[2]["stress_gt_50bp"], 1)

    def test_trailing_threshold_excludes_the_current_row(self):
        values = [1.0, 2.0, 3.0, 4.0, 1000.0]

        self.assertEqual(stress_label_threshold(values, 4, 4, 1.0), 4.0)

    def test_trailing_threshold_requires_declared_history(self):
        with self.assertRaisesRegex(DataContractError, "insufficient"):
            stress_label_threshold([1.0, 2.0], 1, 2, 0.9)



class RealSnapshotPublicationGapTests(unittest.TestCase):
    """The publication-gap bound, actually executed -- and what it cannot tell us.

    Replaces `PublicationGapTests` in `tests/test_registry_interface.py`, deleted on
    8 September 2026 under the standing invitation in its own docstring ("If Track A
    would rather site the test in its own suite, delete this class; what must not
    happen is that it exists in neither"). Track A owns the panel and the registry,
    so the check lives here.

    Why it had to move rather than be fixed in place. That class called
    `load_point_in_time_panel()` with no arguments; the implementation has always
    required a `path`. It was marked `expectedFailure`, so the `TypeError` read as
    "waiting on real snapshots" for as long as it existed, and the guard the contract
    calls the more important of Track A's two escalations never ran once. An
    `expectedFailure` is a claim that the assertion is right and the code is not.
    A missing input is not that, and marking it that way hides a signature error
    behind a red square. This class skips instead, and says what is missing.

    And now the finding, which is worse than the signature error.

    For every `ref_date` source in the registry today, `available_at` is not observed.
    `_nyfed_rows` computes it as `ref_date` plus one business day at 15:00 ET, because
    the API exposes no publication timestamp. The gap this test measures is therefore
    a function of the declaration it is being compared against: with `days: 1` the
    derived gap is 1, or 3 across a weekend, and `worst_case_calendar_days` is
    required by contract to be at least `days + 5`. The check cannot fail. It is the
    self-sealing-fixture problem from the `sort_keys` mutation record, arrived at from
    the other direction -- there the fixture moved with the rule, here the observation
    moves with the declaration.

    So this class asserts the thing that is actually true and actually checkable: no
    row claims to have been available later than the registry says it would be. The
    day a source arrives carrying a real provider publication timestamp, that
    assertion starts doing the work the bound was written for, and the skip message
    below stops being the whole story. Until then the guard with teeth is
    `AvailableAtDerivationTests` in `tests/test_ingest.py`, which pins the adapter's
    derivation to the registry's declaration.

    Known gap, not fixed here: snapshot manifests record the absolute path of the
    machine that captured them, so a panel cannot be rebuilt from a manifest in a
    different checkout without rebasing paths as this test does. Provenance that is
    not portable is provenance that only reproduces on one laptop.
    """

    RAW_ROOT = Path(__file__).parents[1] / "data" / "raw"
    REGISTRY_PATH = Path(__file__).parents[1] / "metadata" / "sources.json"

    def observations(self):
        from repo_model.ingest import SnapshotArtifact, observations_from_snapshots

        manifests = sorted(self.RAW_ROOT.glob("*/*.manifest.json"))
        if not manifests:
            self.skipTest(
                f"no raw snapshots under {self.RAW_ROOT}; data/raw/ is gitignored, so "
                "this check runs only where the adapters have been run. It is not "
                "waiting on an unwritten implementation."
            )
        artifacts = []
        for manifest_path in manifests:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            artifacts.append(
                SnapshotArtifact(
                    source_id=manifest["source_id"],
                    # Rebased off the capture host; see the class docstring.
                    path=manifest_path.parent / Path(manifest["path"]).name,
                    retrieved_at=manifest["retrieved_at"],
                    sha256=manifest["sha256"],
                    url=manifest["url"],
                    byte_count=int(manifest["byte_count"]),
                )
            )
        # Payload checksums are verified on read, so a tampered snapshot fails here.
        return list(observations_from_snapshots(artifacts))

    def test_no_observed_publication_gap_exceeds_the_declared_bound(self):
        registry = json.loads(self.REGISTRY_PATH.read_text(encoding="utf-8"))
        validate_publication_gaps(self.observations(), registry)

    def test_no_row_is_available_later_than_the_registry_declares(self):
        """Row resolution, where the bound is only source resolution.

        A source may satisfy its worst case in aggregate and still emit a single row
        that postdates its own declaration. This is the assertion that will start
        failing when an observed publication timestamp replaces a derived one.
        """

        registry = json.loads(self.REGISTRY_PATH.read_text(encoding="utf-8"))
        declarations = {}
        for source in registry.values():
            lag = source.get("release_lag", {})
            if lag.get("basis") != "ref_date":
                continue
            for series_id in source["fields"]:
                declarations[series_id] = lag

        checked = 0
        for row in self.observations():
            lag = declarations.get(row.series_id)
            if lag is None:
                continue
            current = row.ref_date
            remaining = lag["days"]
            while remaining:
                current += timedelta(days=1)
                if current.weekday() < 5:
                    remaining -= 1
            declared = datetime.combine(
                current,
                time.fromisoformat(lag["available_time"]),
                tzinfo=ZoneInfo(lag["timezone"]),
            )
            self.assertLessEqual(
                row.available_at,
                declared,
                msg=f"{row.series_id} for {row.ref_date} became available at "
                f"{row.available_at}, later than the {declared} the registry declares.",
            )
            checked += 1
        self.assertGreater(checked, 0, "no ref_date rows were checked")

class CoverageFloorDeclarationTests(unittest.TestCase):
    """`declared_coverage_floor` fails closed, and says which way it failed.

    Every branch here is a way the registry can stop guarding without anything
    else noticing, so each one is exercised. An unreachable raise is a guard
    that has never been shown to fire.
    """

    @staticmethod
    def _era(**overrides):
        era = {
            "era_id": "only",
            "start": "2010-11",
            "end": "2026-07",
            "minimum_reporting_entities": 200,
            "observed_minimum_entities": 325,
            "observed_complete_months": 12,
        }
        era.update(overrides)
        return era

    def _floor(self, cross_section):
        return declared_coverage_floor("sec_nmfp", {"cross_section": cross_section})

    def test_a_source_that_declares_no_floor_is_a_contract_error(self):
        with self.assertRaisesRegex(DataContractError, "declares no"):
            declared_coverage_floor("sec_nmfp", {"access": "public"})

    def test_a_source_that_declares_no_eras_is_a_contract_error(self):
        with self.assertRaisesRegex(DataContractError, "declares no eras"):
            self._floor({"entity_unit": "series_id"})

    def test_an_empty_era_list_is_rejected(self):
        with self.assertRaisesRegex(DataContractError, "no floor anywhere"):
            self._floor({"entity_unit": "series_id", "eras": []})

    def test_a_floor_of_zero_is_rejected_as_the_prohibited_silent_zero(self):
        with self.assertRaisesRegex(DataContractError, "guards nothing"):
            self._floor(
                {
                    "entity_unit": "series_id",
                    "eras": [self._era(minimum_reporting_entities=0)],
                }
            )

    def test_a_boolean_does_not_pass_as_a_floor(self):
        with self.assertRaisesRegex(DataContractError, "must be an integer"):
            self._floor(
                {
                    "entity_unit": "series_id",
                    "eras": [self._era(minimum_reporting_entities=True)],
                }
            )

    def test_an_unnamed_entity_unit_is_rejected(self):
        with self.assertRaisesRegex(DataContractError, "entity_unit"):
            self._floor({"eras": [self._era()]})

    def test_an_unpermitted_key_is_rejected_rather_than_ignored(self):
        with self.assertRaisesRegex(DataContractError, "unpermitted keys"):
            self._floor(
                {
                    "entity_unit": "series_id",
                    "eras": [self._era()],
                    "minimum_net_assets": 1000,
                }
            )

    def test_an_unpermitted_key_inside_an_era_is_rejected(self):
        with self.assertRaisesRegex(DataContractError, "unpermitted keys"):
            self._floor(
                {
                    "entity_unit": "series_id",
                    "eras": [self._era(minimum_net_assets=1000)],
                }
            )

    def test_an_era_missing_its_calibration_numbers_is_rejected(self):
        """A floor whose calibration input is absent is a number nobody computed."""

        era = self._era()
        del era["observed_minimum_entities"]
        with self.assertRaisesRegex(
            DataContractError, r"lacks required keys \['observed_minimum_entities'\]"
        ):
            self._floor({"entity_unit": "series_id", "eras": [era]})

    def test_a_floor_above_its_own_calibration_minimum_is_rejected(self):
        """The floor refuses a month its own calibration observed.

        Whatever such a number is guarding against, it is not stragglers, and
        it is wrong on the evidence stated beside it.
        """

        with self.assertRaisesRegex(DataContractError, "refuses a cross-section"):
            self._floor(
                {
                    "entity_unit": "series_id",
                    "eras": [
                        self._era(
                            minimum_reporting_entities=400,
                            observed_minimum_entities=325,
                        )
                    ],
                }
            )

    def test_a_bound_that_is_not_a_month_is_rejected(self):
        with self.assertRaisesRegex(DataContractError, "inclusive YYYY-MM months"):
            self._floor(
                {
                    "entity_unit": "series_id",
                    "eras": [self._era(start="2010-11-30")],
                }
            )

    def test_an_era_that_ends_before_it_starts_is_rejected(self):
        with self.assertRaisesRegex(DataContractError, "no months at all"):
            self._floor(
                {
                    "entity_unit": "series_id",
                    "eras": [self._era(start="2016-04", end="2010-11")],
                }
            )

    def test_overlapping_eras_are_rejected(self):
        """One month cannot have two floors, and picking one would be arbitrary."""

        with self.assertRaisesRegex(DataContractError, "overlap"):
            self._floor(
                {
                    "entity_unit": "series_id",
                    "eras": [
                        self._era(era_id="a", start="2010-11", end="2016-03"),
                        self._era(era_id="b", start="2016-03", end="2026-07"),
                    ],
                }
            )

    def test_a_gap_between_eras_is_rejected(self):
        """A month inside the declared range that no era claims.

        Worse than the undeclared tail, which at least looks undeclared: these
        months lie between the first era and the last, so they read as covered,
        and are refused anyway.
        """

        with self.assertRaisesRegex(DataContractError, "2016-04 undeclared"):
            self._floor(
                {
                    "entity_unit": "series_id",
                    "eras": [
                        self._era(era_id="a", start="2010-11", end="2016-03"),
                        self._era(era_id="b", start="2016-05", end="2026-07"),
                    ],
                }
            )

    def test_a_duplicate_era_id_is_rejected(self):
        with self.assertRaisesRegex(DataContractError, "twice"):
            self._floor(
                {
                    "entity_unit": "series_id",
                    "eras": [
                        self._era(era_id="same", start="2010-11", end="2016-03"),
                        self._era(era_id="same", start="2016-04", end="2026-07"),
                    ],
                }
            )

    def test_the_live_registry_declaration_is_readable(self):
        registry = json.loads(
            (Path(__file__).parents[1] / "metadata" / "sources.json").read_text(
                encoding="utf-8"
            )
        )
        floors = declared_coverage_floor("sec_nmfp", registry["sec_nmfp"])
        self.assertEqual(floors.entity_unit, "series_id")
        self.assertTrue(floors.eras)
        for era in floors.eras:
            self.assertGreaterEqual(era.minimum_reporting_entities, 1)



class StructuralZeroPeriodGrammarTests(unittest.TestCase):
    """Every refusal of the period grammar names its own reason.

    `declared_structural_zeros` reads one source's `structural_zeros` and
    returns, per field, the period a reviewer declared. Block 7 gave that
    declaration a grammar -- `through` required and inclusive, `from`
    optional -- and recorded, as item 8 of its mutation record in
    `DerivedFieldAbsenceTests` (`tests/test_ingest.py`), that the three
    refusals the grammar added were **unguarded**: the `through` requirement
    made a no-op killed nothing at all. That record names this module as
    where the guard belongs, and names the state it found: `tests/test_data.py`
    tested nothing about structural zeros. This class is the repair, and it is
    the first thing here to test them.

    **A refusal shadowed by a later refusal is killable only by its message.**
    That is the shape of the whole class. With the `through is None` check made
    a no-op, the declaration does not sail through: `_structural_zero_bound`
    refuses `None` one line down as a bound that is not a string. A
    `DataContractError` is still raised, the entry is still refused, and a test
    asserting only `assertRaises(DataContractError)` is green over a deleted
    refusal. So each case below asserts `assertRaisesRegex` on the phrase only
    its own refusal writes, and each also asserts that the *shadowing*
    refusal's phrase is absent -- the two halves of "this refusal, not the one
    behind it". The kill for a shadowed refusal is an `AssertionError` of the
    regex-mismatch kind, not "not raised", and the record below says which kind
    each was.

    The distinction is not decorative. The three refusals are not
    interchangeable: no `through` is the declaration that annexes every month
    the source has not reached, an unparseable bound is a typo that would
    otherwise silently stop declaring, and a `from` after its `through` is a
    declaration that covers nothing while reading as though it covers a span.
    A caller told only "DataContractError" cannot act on any of them, and a
    reviewer reading the message is the person who has to fix the registry.

    Mutation record
    ---------------

    Run in a disposable copy under `$HOME`, never in the mount, made from
    git's own file list (`git ls-files -z --cached --others
    --exclude-standard` piped through `tar`) as `CLAUDE.md` directs.
    `PYTHONDONTWRITEBYTECODE=1` and `python3 -B`, CPython 3.9.6 on darwin.
    Unmutated control green in the copy before the first mutation and again
    after the last was reverted; each mutation was applied to a freshly
    restored copy rather than on top of the last, and the branch carries none
    of them. Each is the named check in `src/repo_model/data.py` made a no-op.

    1. **The `through` requirement made a no-op** -- the acceptance mutation.
       `if through is None: raise` deleted from `declared_structural_zeros`,
       leaving `through = declaration.get("through")`. Kills
       `test_each_structural_zero_period_refusal_names_its_own_reason`
       **alone**, and the kind is the one this class is about: an
       `AssertionError` of the **regex mismatch**, not "not raised" --
       `"states no 'through'" does not match "sec_nmfp: structural_zeros entry
       for 'mmf_on_rrp' has a through of None; bounds are inclusive ISO
       YYYY-MM-DD dates"`. The entry is still refused, one line further down,
       by `_structural_zero_bound` reading `None` as a bound that is not a
       string. This is item 8 of the block-7 record repaired: the same
       mutation killed nothing there.

    2. **The unparseable-bound refusal made a no-op**: `except ValueError:
       return date.min` in `_structural_zero_bound` in place of the
       `DataContractError`, so a bound that does not parse is accepted as a
       date rather than refused. Kills the same test **alone**, both subTests,
       `AssertionError: DataContractError not raised` -- **not** shadowed,
       because with the bound accepted there is nothing left to object to:
       `2013-08-32` becomes a `through` and `31-08-2010` a `from` that is not
       after it. The two subTests are the point of the mutation: one refusal
       serves both keys, and the message names the key it read, so a single
       kill would not have shown the `from` path runs at all.

    3. **The empty-period refusal made a no-op**: `if first > last: raise`
       deleted, so a declaration running from `2013-08-31` through
       `2010-11-30` is accepted and declares nothing -- `covers` is false for
       every date. Kills the same test **alone**, `AssertionError:
       DataContractError not raised`. This is the one case of the three that
       is not shadowed, and the kill kind says so: nothing behind it objects,
       so the entry becomes a declaration a reviewer wrote and no
       cross-section can ever match.

    Each kill is a single test and it is the acceptance criterion, so the
    criterion and the mutation target did not come apart. Nothing else in the
    suite noticed any of the three, which is the same finding block 7 recorded
    and the reason this class exists rather than a fourth assertion added to
    something already green.
    """

    #: The reviewer's prose is required and orthogonal to the period, so every
    #: fixture here carries the same one. What varies below is only the dates.
    WHEN = "the facility did not exist; see the review of 2026-09-10"

    def source(self, **declaration):
        """One source declaring one structural zero for `mmf_on_rrp`.

        A mapping rather than the real registry: `metadata/sources.json` is a
        human's file and the grammar under test is not about any source in it.
        `declared_structural_zeros` reads `structural_zeros` and nothing else.
        """

        entry = {"field": "mmf_on_rrp", "when": self.WHEN}
        entry.update(declaration)
        return {"structural_zeros": [entry]}

    def test_a_well_formed_declaration_is_read_as_the_period_it_states(self):
        """The control. Without it every refusal below could be the fixture's."""

        declared = declared_structural_zeros(
            "sec_nmfp", self.source(through="2013-08-31", **{"from": "2010-11-30"})
        )
        period = declared["mmf_on_rrp"]
        self.assertEqual(period.when, self.WHEN)
        self.assertEqual(period.through, date(2013, 8, 31))
        self.assertEqual(period.start, date(2010, 11, 30))
        self.assertTrue(period.covers(date(2013, 8, 31)))
        self.assertFalse(period.covers(date(2026, 7, 31)))

    def test_each_structural_zero_period_refusal_names_its_own_reason(self):
        """The acceptance criterion and the mutation target. See the class docstring.

        Three refusals, each asserted against the phrase only that refusal's
        message carries, and each asserted not to be answered by the refusal
        standing behind it. `assertRaises(DataContractError)` alone would pass
        for (a) with the check deleted, which is the trap block 7 proved on the
        same function and this test exists not to re-prove.
        """

        # (a) No `through`. Shadowed by `_structural_zero_bound`, which refuses
        # `None` as a bound that is not a string -- a different reason for the
        # same entry, and the one a reader would have to act on if this refusal
        # were gone.
        with self.assertRaisesRegex(DataContractError, "states no 'through'") as caught:
            declared_structural_zeros("sec_nmfp", self.source())
        self.assertNotIn("bounds are inclusive", str(caught.exception))

        # (b) An unparseable bound, `through` and `from` separately. Both are
        # the same refusal in `_structural_zero_bound`, and it names which key
        # it read, so each case asserts its own key as well as the phrase.
        for key, entry in (
            ("through", {"through": "2013-08-32"}),
            ("from", {"through": "2013-08-31", "from": "31-08-2010"}),
        ):
            with self.subTest(key=key):
                with self.assertRaisesRegex(
                    DataContractError, "not an ISO YYYY-MM-DD date"
                ) as caught:
                    declared_structural_zeros("sec_nmfp", self.source(**entry))
                self.assertIn(f"has a {key} of", str(caught.exception))

        # (c) `from` after `through`. Not shadowed: both bounds parse and the
        # field is named once, so with this check gone the entry is accepted
        # and declares an empty period -- no refusal at all, which is why its
        # kill is "not raised" and the other two are regex mismatches.
        with self.assertRaisesRegex(
            DataContractError, "declares no cross-sections at all"
        ) as caught:
            declared_structural_zeros(
                "sec_nmfp",
                self.source(through="2010-11-30", **{"from": "2013-08-31"}),
            )
        message = str(caught.exception)
        self.assertIn("2013-08-31", message)
        self.assertIn("2010-11-30", message)

class RealSnapshotCoverageTests(unittest.TestCase):
    """The coverage floor, against the extract in `data/raw/` rather than a fixture.

    `CrossSectionCoverageTests` in `tests/test_ingest.py` proves the wiring on a
    fixture this track wrote, and a fixture that seals itself proves only that
    the code calls the code. These two run the same guard against the real SEC
    bulk extract, where the numbers were not chosen by anyone here.

    Test 2 below is the independent anchor -- the role `metadata/events.json`
    plays for the event-window digest, and the role nothing was playing for the
    publication-gap bound, which is why that guard ran its whole life without
    ever being able to fail. Lower the declared floor in the registry far enough
    to admit an amendment month and this test fails; no fixture can see that,
    because every fixture declares its own floor.

    Follows `RealSnapshotPublicationGapTests`: runs when `data/raw/` is
    populated, skips with a stated reason when it is not. Not `expectedFailure`
    -- that marker claims the assertion is right and the code is wrong, and it
    hid a TypeError in this repo for the whole life of the class it was on.
    """

    RAW_ROOT = Path(__file__).parents[1] / "data" / "raw"
    REGISTRY_PATH = Path(__file__).parents[1] / "metadata" / "sources.json"
    SOURCE_ID = "sec_nmfp"

    def parsed(self):
        from repo_model.ingest import SnapshotArtifact, parse_snapshots

        manifests = sorted(self.RAW_ROOT.glob(f"{self.SOURCE_ID}/*.manifest.json"))
        if not manifests:
            self.skipTest(
                f"no {self.SOURCE_ID} snapshots under {self.RAW_ROOT}; data/raw/ is "
                "gitignored, so this check runs only where the adapters have been "
                "run. It is not waiting on an unwritten implementation."
            )
        artifacts = []
        for manifest_path in manifests:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            artifacts.append(
                SnapshotArtifact(
                    source_id=manifest["source_id"],
                    # Rebased off the capture host, as in the class above.
                    path=manifest_path.parent / Path(manifest["path"]).name,
                    retrieved_at=manifest["retrieved_at"],
                    sha256=manifest["sha256"],
                    url=manifest["url"],
                    byte_count=int(manifest["byte_count"]),
                )
            )
        # Payload checksums are verified on read, so a tampered snapshot fails here.
        return parse_snapshots(
            artifacts,
            registry=json.loads(self.REGISTRY_PATH.read_text(encoding="utf-8")),
        )

    def test_every_admitted_nmfp_cross_section_clears_the_declared_floor(self):
        parsed = self.parsed()
        admitted = [item for item in parsed.coverage if item.admitted]
        self.assertGreater(
            len(admitted),
            0,
            "the floor admitted no cross-section at all; a guard that empties the "
            "panel is not a guard that passed",
        )
        for item in admitted:
            self.assertGreaterEqual(
                item.entity_count,
                item.declared_floor,
                msg=f"{item.source_id} {item.ref_date} was admitted with "
                f"{item.entity_count} reporting {item.entity_unit} values against a "
                f"declared floor of {item.declared_floor}",
            )

        admitted_dates = {item.ref_date for item in admitted}
        # Coverage is a judgement about a cross-section *within one archive*, and
        # the backfill made that distinction load-bearing. One report month is a
        # straggler cohort in the archive filed after it and the complete month in
        # the archive filed for it, so it is legitimately excluded in one and
        # admitted in another. The panel-level claim is the intersection of those:
        # a ref_date no archive admitted must contribute nothing. With a single
        # archive on disk the two readings coincide, which is why this held for as
        # long as there was one.
        never_admitted = {
            item.ref_date for item in parsed.coverage if not item.admitted
        } - admitted_dates
        monthly = {
            row.ref_date for row in parsed.rows if row.series_id == "mmf_net_assets"
        }
        self.assertTrue(
            monthly.issubset(admitted_dates),
            msg=f"monthly rows survive for un-admitted cross-sections "
            f"{sorted(monthly - admitted_dates)}",
        )
        self.assertEqual(
            monthly & never_admitted,
            set(),
            msg="a cross-section no archive admitted still contributes monthly rows",
        )

    def test_the_current_snapshot_contains_cross_sections_that_must_be_excluded(self):
        parsed = self.parsed()
        excluded = [item for item in parsed.coverage if not item.admitted]
        self.assertGreater(
            len(excluded),
            0,
            "the current extract carries amendment and straggler filings for "
            "adjacent months, so at least one cross-section must be excluded. "
            "Nothing was: either the guard is not running, or the floor declared "
            "in metadata/sources.json is low enough to admit a partial month. "
            "Reporting-entity counts seen: "
            + ", ".join(
                f"{item.ref_date}={item.entity_count}" for item in parsed.coverage
            ),
        )
        for item in excluded:
            self.assertLess(
                item.entity_count,
                item.declared_floor,
                msg=f"{item.source_id} {item.ref_date} was excluded despite "
                f"{item.entity_count} reporting {item.entity_unit} values clearing "
                f"its declared floor of {item.declared_floor}",
            )
            self.assertGreater(
                item.row_count,
                0,
                msg=f"{item.ref_date} excluded no rows, so nothing was guarded",
            )

        # An excluded cross-section leaves no monthly rows behind. Two
        # qualifications, both of which only became visible once more than one
        # archive was on disk:
        #
        # "Excluded" has to mean excluded by every archive that saw the date.
        # A report month is a straggler cohort in the archive filed after it and
        # the complete month in the archive filed for it.
        #
        # "Monthly" has to be said, because `ref_date` carries two different
        # meanings in this panel. A monthly series is dated by its submission's
        # report date, so it stands or falls with that cross-section. A
        # business-daily flow series is dated by the flow day, which lies inside
        # the reporting month -- and the last business day of a month is also the
        # report date of the minority of funds that report on it rather than on
        # the calendar month end. Those funds are a cohort of about 70, well under
        # the declared floor, so their cross-section is correctly excluded; the
        # flow rows dated that same day belong to the admitted month-end
        # cross-section and are correctly kept. Asserting over every series
        # conflates the two and fails on a panel that is right.
        #
        # The frequencies come from the registry rather than from a list written
        # out here, so a series that changes frequency cannot quietly fall out of
        # the guard.
        registry = json.loads(self.REGISTRY_PATH.read_text(encoding="utf-8"))
        frequencies = registry[self.SOURCE_ID]["field_frequencies"]
        monthly_series = {
            field for field, frequency in frequencies.items() if frequency == "monthly"
        }
        self.assertGreater(len(monthly_series), 0, "the registry declares no monthly series")

        admitted_dates = {item.ref_date for item in parsed.coverage if item.admitted}
        never_admitted = {item.ref_date for item in excluded} - admitted_dates
        self.assertGreater(
            len(never_admitted),
            0,
            "no report date was excluded by every archive that saw it, so this "
            "assertion is guarding nothing on the snapshots present",
        )
        surviving = sorted(
            {
                (row.series_id, row.ref_date)
                for row in parsed.rows
                if row.series_id in monthly_series and row.ref_date in never_admitted
            }
        )
        self.assertEqual(
            surviving,
            [],
            msg=f"monthly rows survive on reference dates no archive admitted "
            f"{surviving}",
        )


if __name__ == "__main__":
    unittest.main()


class DailyPanelJoinTests(unittest.TestCase):
    """The join from long point-in-time observations to the wide daily panel.

    This class covers `data.build_daily_panel`, the hop that did not exist
    until 8 September 2026. `DailyObservation` was constructed in exactly one
    place -- inside `load_daily_panel`, parsing `data/sample/daily_market.csv`,
    a file written by hand -- so every number this project had reported came
    from twenty-five hand-written rows. The guards were real and protected
    nothing observable.

    The acceptance criterion is
    `test_the_join_does_not_apply_the_purge_gap_a_second_time`, and it is also
    the mutation target. Subtracting the release lag in the join *feels*
    conservative. It is not: `splits.rolling_origin` and
    `event_eval.evaluate_event_window` already hold the last training row a
    full release lag clear of the scored day, so a join that shifted values as
    well would apply the gap twice -- destroying training rows and moving every
    reported figure -- while looking careful. The test states the rule twice
    over: the cell for `ref_date` d carries the value whose `ref_date` is d,
    and the *same* fixture at a different declared lag produces the *same*
    panel, because the lag is not the join's business.

    Mutation record, 8 September 2026. Unmutated control first, green on the
    branch and green again in the copy the mutations were applied to. Each
    mutation was applied to a copy under `$HOME` -- never the mount -- carrying
    `data/`, `.github/`, `metadata/`, `.gitignore`, the root Markdown and
    `docs/PROJECT_STATUS.md`, because `tests/test_docs_freshness.py` reads
    those and their absence is two kills that look real and are not. Run with
    `PYTHONDONTWRITEBYTECODE=1` and `-B`. Every mutation was reverted before
    the next was applied, and the branch carries none of them.

    1. **The acceptance mutation.** In `build_daily_panel`, shift the join by
       the source's release lag: price the column with
       `registry.max_release_lag_days`, then file each observation under
       `ref_date - timedelta(days=purge)` instead of `ref_date`. The panel
       still builds, still validates, and still looks careful. Killed by four
       tests, all in this class:

       * `test_the_join_does_not_apply_the_purge_gap_a_second_time` -- the
         acceptance criterion, on both of its halves independently. The value
         assertion fails because the cell for d carries the number from
         d-plus-the-lag, and the invariance assertion fails because the two
         declared lags now produce two different panels.
       * `test_a_cell_carries_the_latest_vintage_available_at_the_cutoff`
       * `test_a_hole_is_not_the_previous_value`
       * `test_the_written_panel_records_its_cutoff_and_its_refusals`

       Nothing outside this class noticed. The criterion and the mutation
       target did not come apart.

    2. **The refusal reimplemented instead of delegated.** Replace the
       `_priceable_columns` call to `registry.max_release_lag_days` with a
       hard-coded refused set -- `iorb`, `reserve_balances`, `tga`, `on_rrp`,
       `mmf_assets`, `treasury_settlement`, `dealer_treasury_position`,
       `quarter_end`, `tax_date`, which is exactly what the pricing function
       refuses against `metadata/sources.json` today, so the panel is
       unchanged and every other test stays green. Then change a field's
       declaration in a fixture registry so the registry and the list
       disagree. Killed by exactly one test:
       `test_a_column_is_refused_by_the_registry_not_by_a_list`, which moves
       `sofr` onto a `snapshot_retrieved_at` source in a fixture registry and
       asserts the column stops being built. The hard-coded copy keeps
       building it, because a list cannot read a registry.

       The finding the brief asked for: **something noticed, and it was only
       the test written for it.** No pre-existing test in the suite can see a
       panel that has stopped tracking the registry, because until this block
       no code path built a panel from one. That is why the test varies the
       registry rather than the panel -- a fixture that varies only the data
       would have gone green under the hard-coded set.

    3. **A hole forward-filled from the previous `ref_date`.** Killed by two
       tests, both in this class: `test_a_hole_is_not_the_previous_value`
       (the 6 January `sofr` cell comes back 4.30 instead of `None`) and
       `test_holes_are_counted_not_filled` (the hole counts fall to
       `{"sofr": 0, "tgcr": 1}` while the row count is unchanged, which is the
       shape a filled panel has: the rows are all still there and the
       emptiness has gone).

    4. **The boring one, and it was boring.** `data/sample/daily_market.csv`,
       row one, `sofr` 4.31 -> 4.41. Killed only in `tests/test_baseline.py`:
       `FittedThresholdTests.test_the_arx_reports_the_numbers_it_reported_before_a_third_model_existed`,
       `PurgedBacktestTests.test_the_backtest_derives_its_purge_from_the_declared_feature_set`,
       `PurgedBacktestTests.test_the_purge_moves_the_reported_numbers_and_the_move_is_kept`
       and `RollingBacktestTests.test_persistence_remains_the_default_with_unchanged_numbers`.
       **Zero kills in this class and zero elsewhere in `tests/test_data.py`.**
       That is the intended result twice over: nothing in this block reaches an
       existing figure, and the join's tests are fixture-based precisely so
       they cannot start depending on the hand-written file this block exists
       to make unnecessary.

    Deliberately absent from all of the above: an absolute test count. The
    kill lists name tests; a total would be a transcribed number with nothing
    asserting it, which is the drift `tests/test_docs_freshness.py` exists to
    refuse in Markdown and no more defensible in a docstring.

    Addendum, 8 September 2026 -- rules 6 and 7, and what they did to the
    record above
    ----------------------------------------------------------------------
    Rule 6 (a date missing a required column is not a row) and rule 7 (a
    spliced column's fields must partition the dates) were added the same day
    Milestone A was run, because `build` was writing a panel `backtest` could
    not open: the grid was the union of every source's reference dates, so a
    calendar-daily administered rate and a business-daily market rate produced
    rows on which `sofr - iorb` does not exist, and `REQUIRED_FIELDS` then
    refused the file at row 2.

    New mutations, same conditions -- disposable copy under `$HOME`, `-B`,
    `PYTHONDONTWRITEBYTECODE=1`, control green before and after, each reverted
    before the next.

    A. **Rule 6 removed**: retain every reported date. Killed four tests, all
       in this class -- `test_a_date_missing_a_required_column_is_not_a_row`
       (the acceptance criterion), `test_a_panel_no_date_completes_is_refused_rather_than_written_empty`,
       `test_a_hole_is_not_the_previous_value` and
       `test_holes_are_counted_not_filled`. `AssertionError` throughout.
    B. **Rule 7 resolved instead of refused**: skip the overlap check and let
       rule 1's tie-break pick a winner. Killed exactly one,
       `test_two_fields_of_one_spliced_column_may_not_report_the_same_date`,
       which is this rule's acceptance criterion.

    Two of the kill lists above were re-run today, because rule 6 changed the
    fixture they were measured on, and one of them had gone quiet:

    * **Mutation 3 (a hole forward-filled) fired nothing on the first re-run.**
      The old fixture observed `tgcr` only on the date rule 6 drops, so no
      retained row had a value for the fill to carry: rule 6 had blunted rule
      4's guard, and the suite stayed green over it. The fixture now observes
      `tgcr` on a retained row as well, and the mutation kills
      `test_a_hole_is_not_the_previous_value`. It no longer reaches
      `test_holes_are_counted_not_filled`, which the old record named -- the
      count is taken before the fill, so filling does not move it. A mutation
      that fires nothing is a finding about the tests, and this one was.
    * **Mutation 1 (the join shifted by the declared lag)**, re-run in its
      shift-by-one-day form, kills seven: the acceptance criterion
      `test_the_join_does_not_apply_the_purge_gap_a_second_time`,
      `test_a_cell_carries_the_latest_vintage_available_at_the_cutoff`,
      `test_a_hole_is_not_the_previous_value`,
      `test_the_written_panel_records_its_cutoff_and_its_refusals`, the two new
      rule 6 tests, and `IdentityVerdictTests.test_a_violation_stops_a_panel_that_uses_the_source_and_not_one_that_does_not`.
      All `AssertionError`. The original record named four; the three additions
      are tests that did not exist when it was written, and no test it named
      has stopped being killed.
    """

    #: A `ref_date` source with a nonzero declared lag, copied from
    #: `metadata/sources.json` so the fixture and the tree agree on shape.
    #: `worst_case_calendar_days` is what the tests vary.
    def registry_at_lag(self, worst_case_calendar_days: int):
        return {
            "nyfed_sofr": {
                "release_lag": {
                    "basis": "ref_date",
                    "unit": "business_days",
                    "days": 1,
                    "worst_case_calendar_days": worst_case_calendar_days,
                    "available_time": "15:00",
                    "timezone": "America/New_York",
                    "note": "fixture",
                }
            }
        }

    def observation(self, ref_date: date, value: float, *, available_offset: int = 1):
        """One SOFR observation, available `available_offset` days after its ref_date."""

        return PointInTimeObservation(
            series_id="SOFR",
            ref_date=ref_date,
            available_at=datetime.combine(
                ref_date + timedelta(days=available_offset),
                time(19, 0),
                tzinfo=timezone.utc,
            ),
            value=value,
            vintage_id=f"v{ref_date.isoformat()}",
            source_sha="a" * 64,
        )

    def build(self, registry, rows, *, cutoff=None, columns=("sofr",)):
        return build_daily_panel(
            rows,
            registry,
            build_cutoff=cutoff or datetime(2026, 3, 1, tzinfo=timezone.utc),
            decision_time=time.fromisoformat("15:00"),
            columns=columns,
        )

    def test_the_join_does_not_apply_the_purge_gap_a_second_time(self):
        """The acceptance criterion, and the mutation target. See the class docstring.

        Two assertions, and both must hold. The cell for `ref_date` d carries
        the value whose `ref_date` is d -- not the value from d minus the
        declared lag, and not a hole where d has an observation. And the same
        observations, joined against a registry declaring a different lag,
        produce the same panel, because the lag is the evaluator's business and
        never the join's.
        """

        days = [date(2026, 1, 5), date(2026, 1, 6), date(2026, 1, 7), date(2026, 1, 8)]
        values = {day: 4.30 + index / 100 for index, day in enumerate(days)}
        rows = [self.observation(day, values[day]) for day in days]

        at_six = self.build(self.registry_at_lag(6), rows)

        self.assertEqual(at_six.built_columns, ("sofr",))
        self.assertEqual([row.date for row in at_six.observations], days)
        for row in at_six.observations:
            self.assertIsNotNone(
                row.values["sofr"],
                f"{row.date} has an observation and must not be a hole",
            )
            self.assertAlmostEqual(row.values["sofr"], values[row.date])

        # 20, not 1: `validate_release_lag` floors `worst_case_calendar_days`
        # at `days + 5`, so the other declared lag has to move upward to be a
        # legal declaration at all. Either direction proves the same thing.
        at_twenty = self.build(self.registry_at_lag(20), rows)
        self.assertEqual(
            [(row.date, row.values["sofr"]) for row in at_twenty.observations],
            [(row.date, row.values["sofr"]) for row in at_six.observations],
            "the declared release lag must not change the panel the join builds",
        )

    def test_a_column_is_refused_by_the_registry_not_by_a_list(self):
        """The refusal tracks the registry because it is delegated, not copied.

        Same column, same observations, two registries. On a `ref_date` basis
        `sofr` is built; moved to a `snapshot_retrieved_at` source with no
        `revision_policy` -- exactly the shape whose latest value may differ
        from the value that stood on the day -- `registry.max_release_lag_days`
        refuses it, and so does the join. A hard-coded refused set in `data.py`
        cannot follow that, which is what makes this the test for mutation 2.
        """

        rows = [self.observation(date(2026, 1, 5), 4.30)]
        built = self.build(self.registry_at_lag(6), rows)
        self.assertEqual(built.built_columns, ("sofr",))
        self.assertEqual(built.refusals, {})

        snapshot_registry = {
            "nyfed_sofr": {
                "release_lag": {
                    "basis": "snapshot_retrieved_at",
                    "note": "fixture: latest vintage only",
                }
            }
        }
        with self.assertRaises(DataContractError):
            # Every declared column refused leaves nothing to index, and the
            # refusal reasons travel with the error rather than an empty panel.
            self.build(snapshot_registry, rows)

        mixed = build_daily_panel(
            rows + [
                PointInTimeObservation(
                    series_id="TGCR",
                    ref_date=date(2026, 1, 5),
                    available_at=datetime(2026, 1, 6, 19, tzinfo=timezone.utc),
                    value=4.29,
                    vintage_id="t1",
                    source_sha="b" * 64,
                )
            ],
            {
                **snapshot_registry,
                "nyfed_tgcr": self.registry_at_lag(6)["nyfed_sofr"],
            },
            build_cutoff=datetime(2026, 3, 1, tzinfo=timezone.utc),
            decision_time=time.fromisoformat("15:00"),
            columns=("sofr", "tgcr"),
        )
        self.assertEqual(mixed.built_columns, ("tgcr",))
        self.assertIn("sofr", mixed.refusals)
        self.assertNotIn("sofr", mixed.observations[0].values)

    #: The fixture the hole and grid tests share. `sofr` is observed on 5 and
    #: 7 January; `tgcr` on 5 and 6 January. Under rule 6 the 6 January date is
    #: not a row, because `sofr` -- a `REQUIRED_FIELDS` column -- is missing
    #: there. Two rows survive: 5 January complete, 7 January with `tgcr`
    #: empty.
    #:
    #: The `tgcr` value on 5 January is the part that has to be there. An
    #: earlier version of this fixture observed `tgcr` only on the date rule 6
    #: drops, and a forward-fill mutation then killed nothing at all: with no
    #: value on any retained row there was nothing for the fill to carry. Rule
    #: 6 had quietly blunted rule 4's guard, and the fixture is what noticed.
    #: A hole is only observable when the cell above it is not one.
    def hole_fixture(self):
        rows = [
            self.observation(date(2026, 1, 5), 4.30),
            self.observation(date(2026, 1, 7), 4.32),
        ] + [
            PointInTimeObservation(
                series_id="TGCR",
                ref_date=ref_date,
                available_at=datetime(2026, 1, 7, 19, tzinfo=timezone.utc),
                value=value,
                vintage_id=f"t{ref_date.isoformat()}",
                source_sha="b" * 64,
            )
            for ref_date, value in (
                (date(2026, 1, 5), 4.29),
                (date(2026, 1, 6), 4.28),
            )
        ]
        registry = {
            "nyfed_sofr": self.registry_at_lag(6)["nyfed_sofr"],
            "nyfed_tgcr": self.registry_at_lag(6)["nyfed_sofr"],
        }
        return registry, rows

    def test_a_hole_is_not_the_previous_value(self):
        """A `ref_date` with no observation for a column stays empty.

        The gap is a real one. `tgcr` is 4.29 on 5 January and 4.28 on 6
        January, and 6 January is not a row because `sofr` is missing there.
        So 7 January's `tgcr` cell is `None`: not 4.29 carried down from the
        row above it, and not 4.28 carried out of a date the panel does not
        contain. Absent is not zero and is not yesterday -- and it is not
        yesterday whether or not yesterday survived rule 6.
        """

        registry, rows = self.hole_fixture()

        build = self.build(registry, rows, columns=("sofr", "tgcr"))

        by_date = {row.date: row.values for row in build.observations}
        self.assertEqual(sorted(by_date), [date(2026, 1, 5), date(2026, 1, 7)])
        self.assertAlmostEqual(by_date[date(2026, 1, 5)]["tgcr"], 4.29)
        self.assertIsNone(by_date[date(2026, 1, 7)]["tgcr"])
        self.assertAlmostEqual(by_date[date(2026, 1, 5)]["sofr"], 4.30)
        self.assertAlmostEqual(by_date[date(2026, 1, 7)]["sofr"], 4.32)

    def test_holes_are_counted_not_filled(self):
        """`holes` counts the empty cells the panel kept, per built column.

        Kept is the operative word, and it is why the count is taken after
        rule 6 rather than before: a hole count over dates the panel does not
        carry describes a file nobody has.
        """

        registry, rows = self.hole_fixture()

        build = self.build(registry, rows, columns=("sofr", "tgcr"))

        self.assertEqual(len(build.observations), 2)
        self.assertEqual(build.holes, {"sofr": 0, "tgcr": 1})

    def test_a_date_missing_a_required_column_is_not_a_row(self):
        """Rule 6, and the acceptance criterion for the panel grid.

        6 January has `tgcr` and no `sofr`. `sofr` is a `REQUIRED_FIELDS`
        column, so `sofr - iorb` does not exist on that date and neither does
        the row. The count of dropped dates is recorded rather than inferred:
        a build that silently narrowed its own grid would be indistinguishable
        from a build whose sources happened to agree.
        """

        registry, rows = self.hole_fixture()

        build = self.build(registry, rows, columns=("sofr", "tgcr"))

        self.assertEqual(
            [row.date for row in build.observations],
            [date(2026, 1, 5), date(2026, 1, 7)],
        )
        self.assertEqual(build.incomplete_dates, 1)

    def test_a_panel_no_date_completes_is_refused_rather_than_written_empty(self):
        """The degenerate end of rule 6. An empty panel is not a panel."""

        rows = [
            PointInTimeObservation(
                series_id="TGCR",
                ref_date=date(2026, 1, 6),
                available_at=datetime(2026, 1, 7, 19, tzinfo=timezone.utc),
                value=4.29,
                vintage_id="t1",
                source_sha="b" * 64,
            ),
        ]
        registry = {
            "nyfed_sofr": self.registry_at_lag(6)["nyfed_sofr"],
            "nyfed_tgcr": self.registry_at_lag(6)["nyfed_sofr"],
        }

        with self.assertRaisesRegex(DataContractError, "no reference date carries"):
            self.build(registry, rows, columns=("sofr", "tgcr"))

    def test_two_fields_of_one_spliced_column_may_not_report_the_same_date(self):
        """Rule 7, and the acceptance criterion for the splice.

        `iorb` is declared from IORB and IOER. In the real data they abut --
        IOER ends 2021-07-28, IORB begins 2021-07-29 -- and this asserts what
        happens if that ever stops being true. The tie-break in rule 1 orders
        by `(available_at, vintage_id)`, and two fields read out of one
        latest-vintage FRED snapshot share both exactly, so the winner on an
        overlapping date would be whichever the iteration reached last. That
        is a decision about what the administered leg *is*, taken by dict
        ordering, and it raises instead.
        """

        available_at = datetime(2021, 7, 29, 19, tzinfo=timezone.utc)
        rows = [
            PointInTimeObservation(
                series_id=series_id,
                ref_date=date(2021, 7, 28),
                available_at=available_at,
                value=value,
                vintage_id="one-snapshot",
                source_sha="c" * 64,
            )
            for series_id, value in (("IORB", 0.15), ("IOER", 0.10))
        ]
        registry = {
            "fred_macro_latest_vintage": {
                "release_lag": {
                    "basis": "record_date",
                    "unit": "calendar_days",
                    "days": 1,
                    "available_time": "16:15",
                    "timezone": "America/New_York",
                    "note": "fixture",
                }
            }
        }

        with self.assertRaisesRegex(DataContractError, "IOER and IORB both report 2021-07-28"):
            self.build(registry, rows, columns=("iorb",))

    def test_a_cell_carries_the_latest_vintage_available_at_the_cutoff(self):
        """The cutoff selects the vintage; it never selects the `ref_date`.

        Two vintages of one cell. A build cutoff before the revision lands
        carries the first value; a later cutoff carries the revision. Both
        carry it at the same `ref_date`, which is the half rule 1 shares with
        rule 2.
        """

        ref_date = date(2026, 1, 5)
        first = PointInTimeObservation(
            series_id="SOFR",
            ref_date=ref_date,
            available_at=datetime(2026, 1, 6, 19, tzinfo=timezone.utc),
            value=4.30,
            vintage_id="v1",
            source_sha="a" * 64,
        )
        revised = PointInTimeObservation(
            series_id="SOFR",
            ref_date=ref_date,
            available_at=datetime(2026, 1, 20, 19, tzinfo=timezone.utc),
            value=4.35,
            vintage_id="v2",
            source_sha="a" * 64,
        )
        registry = self.registry_at_lag(6)

        early = self.build(
            registry, [first, revised], cutoff=datetime(2026, 1, 10, tzinfo=timezone.utc)
        )
        self.assertEqual([row.date for row in early.observations], [ref_date])
        self.assertAlmostEqual(early.observations[0].values["sofr"], 4.30)

        late = self.build(
            registry, [first, revised], cutoff=datetime(2026, 2, 1, tzinfo=timezone.utc)
        )
        self.assertEqual([row.date for row in late.observations], [ref_date])
        self.assertAlmostEqual(late.observations[0].values["sofr"], 4.35)

    def test_a_naive_build_cutoff_is_refused(self):
        rows = [self.observation(date(2026, 1, 5), 4.30)]
        with self.assertRaisesRegex(DataContractError, "UTC offset"):
            build_daily_panel(
                rows,
                self.registry_at_lag(6),
                build_cutoff=datetime(2026, 3, 1),
                decision_time=time.fromisoformat("15:00"),
                columns=("sofr",),
            )

    def test_the_written_panel_records_its_cutoff_and_its_refusals(self):
        """The manifest is the committable half; the panel bytes are derived."""

        rows = [
            self.observation(date(2026, 1, 5), 4.30),
            self.observation(date(2026, 1, 7), 4.32),
        ]
        build = self.build(self.registry_at_lag(6), rows, columns=("sofr", "iorb"))
        self.assertEqual(build.built_columns, ("sofr",))
        self.assertIn("iorb", build.refusals)

        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "panel.csv"
        manifest_path = write_daily_panel(build, path, source_shas=("c" * 64,))

        self.assertEqual(
            path.read_text(encoding="utf-8"),
            "date,sofr\n2026-01-05,4.3\n2026-01-07,4.32\n",
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["build_cutoff"], "2026-03-01T00:00:00+00:00")
        self.assertEqual(manifest["built_columns"], ["sofr"])
        self.assertIn("iorb", manifest["refused_columns"])
        self.assertEqual(manifest["row_count"], 2)
        self.assertEqual(manifest["source_shas"], ["c" * 64])


class PanelDigestTests(unittest.TestCase):
    """The manifest carries the digest of the panel bytes it describes.

    Until this class, `write_daily_panel` recorded the panel's `"path"` and its
    extent and no digest, so a manifest found beside a panel was a claim about
    a *name*. `baseline._bind_build_manifest` could therefore bind a run record
    to a manifest only on `row_count`, `start_date` and `end_date`, and said so
    in the artifact as `build_manifest_binding.kind = "extent"` -- evidence that
    two files describe the same span, not that either describes the other. Its
    docstring names the gap as this writer's. This closes it: the manifest
    carries `sha256`, lowercase hex, over the panel bytes as written, which is
    the convention the run records already use. Comparing it in the binding is
    Track B's and is not here.

    This class now holds two blocks' criteria: the writer's, below, and the
    reader's, `test_a_panel_one_byte_off_its_manifest_digest_is_refused`, whose
    record is the second one at the end. Each is the mutation target of its own
    block; neither is the other's. It also holds one test that is no block's
    criterion --
    `test_a_manifest_digest_that_is_not_lowercase_hex_is_refused_as_such`,
    carried by the block after the reader's because the reader's brief asked
    for a mutation its refusal could not produce. Item 4 of the second record
    is that mutation, run at last.

    The writing side's acceptance criterion is
    `test_the_manifest_digest_is_the_digest_of_the_bytes_on_disk`, and it is
    also that block's mutation target. Its oracle shares no code path with
    `data.py`:
    the test opens the written panel with `path.read_bytes()` and hashes those
    bytes itself. That is the whole point of the test rather than an incidental
    style. The available shortcut is to hash a second rendering of the panel --
    the joined lines, the observations, the CSV re-emitted -- and on this
    filesystem such a digest agrees with the bytes on disk by coincidence. A
    second rendering can drift from the first without either being wrong, and a
    digest over the string that was never the file is green through exactly the
    drift a digest exists to catch.

    Mutation record, 10 September 2026, CPython 3.9.6 on darwin. Applied in a
    disposable copy under `$HOME`, never in the mount, carrying `data/`,
    `.github/`, `.claude/`, `metadata/`, `.gitignore`, the root Markdown and
    `docs/PROJECT_STATUS.md` -- `tests/test_docs_freshness.py` reads the last
    three and `tests/test_ownership_hook.py` reads `.claude/`, and their absence
    is a red control that looks like a finding. `PYTHONDONTWRITEBYTECODE=1` and
    `python3 -B`. Unmutated control green in the copy before the first mutation
    and again after the last was reverted; each was reverted before the next was
    applied, and the branch carries none of them.

    1. **The acceptance mutation, the one the brief required.** In
       `write_daily_panel`, take the digest over the rendered text without its
       trailing newline --
       `hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()` instead of
       `hashlib.sha256(path.read_bytes()).hexdigest()`. The panel is written
       unchanged, the manifest is well formed, the digest is 64 lowercase hex
       characters, and it is the digest of a string that is not the file.
       Killed by exactly one test, `AssertionError`:
       `test_the_manifest_digest_is_the_digest_of_the_bytes_on_disk`, on the
       first assertion, comparing the two hex digests. The criterion and the
       mutation target did not come apart.

    2. **The key never reaches the manifest.** Drop `"sha256": digest` from the
       manifest dict and leave the digest computed. Killed by the same one
       test, `KeyError: 'sha256'` -- an error rather than a failure, which is
       the honest report: a manifest without the key is not a manifest making a
       wrong claim, it is the state this block exists to leave behind.

    **The finding, and it is the same one both mutations report: nothing else in
    the suite noticed either.** Not `test_the_written_panel_records_its_cutoff_and_its_refusals`,
    which reads this manifest and asserts five of its keys; not
    `tests/test_baseline.py`, whose `_bind_build_manifest` is the function the
    digest exists for. That is expected and is the reason this block is queued
    before Track B's: the binding compares extent today and cannot compare a
    digest it was never given. Until that lands, the only thing asserting the
    manifest describes *these* bytes is the test above. A single-test kill list
    is a thin guard, and saying so is worth more than a longer list would be.

    Deliberately absent: a count of tests run. The kill lists name tests; a
    total would be a transcribed number with nothing asserting it, which is the
    drift `tests/test_docs_freshness.py` refuses in Markdown and no more
    defensible here.

    ----

    `verify_daily_panel` -- the reading side, and the second criterion
    ..................................................................

    A manifest that carries a digest nobody checks is a manifest. The writer
    above put `sha256` in it; this reads it back and compares it with the panel
    on disk, and refuses a manifest that has no digest to compare rather than
    reporting the absence of evidence as evidence. The acceptance criterion is
    `test_a_panel_one_byte_off_its_manifest_digest_is_refused`, and it is also
    the mutation target.

    The fixture is a panel `load_daily_panel` opens -- `loadable_written_panel`,
    which prices `iorb` as well so the file has every `REQUIRED_FIELDS` column.
    That is load-bearing twice over. It keeps the refusal under test the
    digest's rather than a parser's, and it is what makes the required mutation
    legible: an extent check that could not open the file at all would raise
    from the loader on the untampered panel and the kill would be an accident
    of the fixture rather than a statement about extent.

    Mutation record, 10 September 2026, CPython 3.9.6 on darwin. Applied in a
    disposable copy under `$HOME`, never in the mount, made from git's own file
    list (`git ls-files -z --cached --others --exclude-standard` piped through
    `tar`) as CLAUDE.md now directs -- every tracked file as the working tree
    has it plus the new untracked ones, nothing gitignored, so no guard is red
    for want of a path a hand-kept list forgot. `PYTHONDONTWRITEBYTECODE=1` and
    `python3 -B`. Unmutated control green in the copy before the first mutation
    and again after the last was reverted; each was reverted before the next was
    applied, and the branch carries none of them. No fixture named by the
    writer's record above was touched, so none of its mutations needed re-running.

    1. **The acceptance mutation, the one the brief required.** The digest
       comparison in `verify_daily_panel` replaced by a comparison of extent:
       the panel loaded, and `(len(observations), first date, last date)`
       checked against the manifest's `row_count`, `start_date` and `end_date`.
       Killed by exactly one test, `AssertionError: DataContractError not
       raised`: `test_a_panel_one_byte_off_its_manifest_digest_is_refused`. The
       criterion and the mutation target did not come apart. This is the
       `build_manifest_binding.kind = "extent"` binding the writer's record
       names, transplanted into the verifier, and the one-byte panel is the
       file it cannot tell from the original.

    2. **A missing digest treated as a pass.** `if recorded is None: return ""`
       in place of the refusal. Killed by exactly one test, `AssertionError:
       DataContractError not raised`:
       `test_a_manifest_with_no_digest_is_refused_rather_than_passed`. Every
       manifest written before the writer's block is such a manifest, so this
       is the mutation that decides whether "verified" means anything on the
       panels that exist today.

    3. **A negative result, and it is the reading side of the writer's own
       trap.** The digest taken over
       `panel_path.read_text(encoding="utf-8").encode("utf-8")` instead of
       `panel_path.read_bytes()`. **Nothing in the suite noticed.** The writer's
       record above kills the same substitution on the writing side, because
       there the second rendering is a *different* string -- the joined lines
       without the trailing newline. Here it is a re-decode and re-encode of
       the same file, and on a POSIX filesystem with an ASCII panel and LF
       terminators the two byte strings are equal, so no fixture in this
       repository can separate them. The guard against it is the docstring on
       `verify_daily_panel` and the fact that the writer hashes the same way;
       naming that here is worth more than a test that would pass either way.

    4. **The malformed-digest refusal made a no-op** -- the record of a
       mutation this block's brief asked for and could not get, run at the
       block after it, when the refusal acquired a test.
       `if not isinstance(recorded, str) or not SHA256_PATTERN.match(recorded)`
       and its raise deleted from `verify_daily_panel`. Kills
       `test_a_manifest_digest_that_is_not_lowercase_hex_is_refused_as_such`
       **alone**, both subTests, `AssertionError` of the **regex mismatch**
       kind: `"not 64 lowercase hex" does not match "... hashes to
       3a790697..., but ... records 3A790697.... The panel is not the file the
       manifest describes"`, and the same for the non-string, whose `repr`
       lands in the mismatch message instead.

       That is the whole of the correction. The brief for the block above
       required this refusal to be killed by `DataContractError not raised`,
       which it can never produce: a recorded digest that is not 64 lowercase
       hex characters can never equal a computed one, so the comparison below
       refuses the identical inputs -- for the wrong reason, reporting a
       mismatch where the truth is that there is nothing well formed to
       compare. **A refusal shadowed by a later refusal is killable only by
       its message.** The uppercase copy of the true digest is the case that
       earns the guard: it is the one malformed value that hashing agrees
       with, so any verifier that normalised case would pass it.
    """

    #: The same `ref_date` fixture source the join tests use, at one declared
    #: lag. This class varies nothing about the registry; it needs a panel that
    #: builds, not a panel that argues.
    REGISTRY = {
        "nyfed_sofr": {
            "release_lag": {
                "basis": "ref_date",
                "unit": "business_days",
                "days": 1,
                "worst_case_calendar_days": 6,
                "available_time": "15:00",
                "timezone": "America/New_York",
                "note": "fixture",
            }
        }
    }

    def observation(self, ref_date: date, value: float):
        return PointInTimeObservation(
            series_id="SOFR",
            ref_date=ref_date,
            available_at=datetime.combine(
                ref_date + timedelta(days=1), time(19, 0), tzinfo=timezone.utc
            ),
            value=value,
            vintage_id=f"v{ref_date.isoformat()}",
            source_sha="a" * 64,
        )

    def written_panel(self):
        """Build a small panel, write it, and return `(panel_path, manifest)`."""

        days = [date(2026, 1, 5), date(2026, 1, 6), date(2026, 1, 7)]
        build = build_daily_panel(
            [self.observation(day, 4.30 + index / 100) for index, day in enumerate(days)],
            self.REGISTRY,
            build_cutoff=datetime(2026, 3, 1, tzinfo=timezone.utc),
            decision_time=time.fromisoformat("15:00"),
            columns=("sofr",),
        )
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "panel.csv"
        manifest_path = write_daily_panel(build, path, source_shas=("c" * 64,))
        return path, json.loads(manifest_path.read_text(encoding="utf-8"))

    def test_the_manifest_digest_is_the_digest_of_the_bytes_on_disk(self):
        """The writing side's acceptance criterion and mutation target. See the class docstring.

        The oracle is the file: `path.read_bytes()` and `hashlib` in this test,
        with nothing from `data.py` between them. A manifest whose `sha256` is
        the digest of anything else -- the rendered text, that text without its
        trailing newline, a re-emission of the same observations -- describes a
        panel that was never written, however close the two happen to be.
        """

        path, manifest = self.written_panel()

        on_disk = path.read_bytes()
        self.assertEqual(
            manifest["sha256"],
            hashlib.sha256(on_disk).hexdigest(),
            "the manifest must carry the digest of the bytes that reached disk",
        )
        self.assertEqual(
            manifest["sha256"],
            manifest["sha256"].lower(),
            "the run records write lowercase hex and the manifest joins them",
        )
        self.assertEqual(len(manifest["sha256"]), 64)

    #: A registry that prices `iorb` as well, so the panel this class writes
    #: for `verify_daily_panel` carries every `REQUIRED_FIELDS` column and
    #: `load_daily_panel` can open it. The `fred_macro_latest_vintage` entry is
    #: the one the splice test uses: a `record_date` lag, which is what makes
    #: the column priceable at all -- the real source is
    #: `snapshot_retrieved_at` with no revision policy and is refused.
    LOADABLE_REGISTRY = {
        "nyfed_sofr": REGISTRY["nyfed_sofr"],
        "fred_macro_latest_vintage": {
            "release_lag": {
                "basis": "record_date",
                "unit": "calendar_days",
                "days": 1,
                "available_time": "16:15",
                "timezone": "America/New_York",
                "note": "fixture",
            }
        },
    }

    def loadable_written_panel(self):
        """Write a panel `load_daily_panel` can open; return `(panel, manifest)` paths.

        `written_panel` above builds `sofr` alone, which is enough to hold a
        digest but not enough to load: `REQUIRED_FIELDS` wants `iorb` too, and
        `write_daily_panel`'s docstring says why it writes the file anyway.
        The refusal under test here must be the digest's and not a loader's, so
        the panel this fixture writes is one the loader accepts -- before the
        byte changes and after.
        """

        days = [date(2026, 1, 5), date(2026, 1, 6), date(2026, 1, 7)]
        rows = [self.observation(day, 4.30 + index / 100) for index, day in enumerate(days)]
        rows += [
            PointInTimeObservation(
                series_id="IORB",
                ref_date=day,
                available_at=datetime.combine(
                    day + timedelta(days=1), time(19, 0), tzinfo=timezone.utc
                ),
                value=4.40,
                vintage_id=f"i{day.isoformat()}",
                source_sha="b" * 64,
            )
            for day in days
        ]
        build = build_daily_panel(
            rows,
            self.LOADABLE_REGISTRY,
            build_cutoff=datetime(2026, 3, 1, tzinfo=timezone.utc),
            decision_time=time.fromisoformat("15:00"),
            columns=("sofr", "iorb"),
        )
        self.assertEqual(build.built_columns, ("sofr", "iorb"))
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "panel.csv"
        manifest_path = write_daily_panel(build, path, source_shas=("c" * 64,))
        return path, manifest_path

    def test_a_panel_one_byte_off_its_manifest_digest_is_refused(self):
        """The reading side's acceptance criterion and mutation target. See the class docstring.

        One byte, chosen so that everything a weaker check could look at
        survives it: the file is the same length, it has the same three rows
        between the same two dates, and `load_daily_panel` opens it before and
        after. What changes is a value -- `sofr` on 6 January -- which is the
        whole content of the panel and the only thing the digest is for. A
        verifier that compares row count and end dates passes this file; that
        is `build_manifest_binding.kind = "extent"` and it is what this
        function exists not to be.
        """

        path, manifest_path = self.loadable_written_panel()
        before = load_daily_panel(path)

        self.assertEqual(verify_daily_panel(path, manifest_path), manifest_digest(manifest_path))

        original = path.read_bytes()
        self.assertIn(b"2026-01-06,4.31,4.4", original)
        tampered = original.replace(b"2026-01-06,4.31,4.4", b"2026-01-06,4.41,4.4", 1)
        self.assertEqual(len(tampered), len(original))
        self.assertEqual(
            sum(1 for old, new in zip(original, tampered) if old != new),
            1,
            "the fixture must change exactly one byte or it proves something weaker",
        )
        path.write_bytes(tampered)

        after = load_daily_panel(path)
        self.assertEqual(
            [row.date for row in after],
            [row.date for row in before],
            "the extent must survive the change, or extent would have caught it",
        )
        self.assertEqual(len(after), len(before))

        with self.assertRaises(DataContractError) as caught:
            verify_daily_panel(path, manifest_path)

        message = str(caught.exception)
        self.assertIn(hashlib.sha256(tampered).hexdigest(), message)
        self.assertIn(manifest_digest(manifest_path), message)
        self.assertIn(str(path), message)
        self.assertIn(str(manifest_path), message)

    def test_a_manifest_with_no_digest_is_refused_rather_than_passed(self):
        """Every manifest written before the digest landed is one of these.

        The failure mode is not that such a manifest is wrong; it is that a
        verifier can only report it as a pass, and a pass here reads as "these
        bytes are the ones that were built". Absence of evidence is refused
        with its own message so that a caller can tell "nothing to compare"
        from "compared and disagreed".
        """

        path, manifest_path = self.loadable_written_panel()
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        del manifest["sha256"]
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

        with self.assertRaisesRegex(DataContractError, "no digest to compare"):
            verify_daily_panel(path, manifest_path)



    def test_a_manifest_digest_that_is_not_lowercase_hex_is_refused_as_such(self):
        """Carried from the block above: the malformed-digest refusal, guarded.

        That block's brief asked for this refusal to be killed by
        `DataContractError not raised`, and it never can be. A malformed
        recorded digest can never equal a computed one, so with the format
        check made a no-op the comparison one line down refuses the very same
        inputs -- with a different message, about a mismatch, which is not what
        happened. The refusal is shadowed, so it is killable only by its own
        phrase, and the kill is a regex mismatch rather than a missing
        exception. Item 4 of the record above is that mutation.

        The uppercase copy of the *true* digest is the case that makes this
        more than a spelling rule. It is the one malformed digest that would
        otherwise be right: hashing agrees with it up to case, so a verifier
        that lowercased what it read, or compared case-insensitively, would
        pass it. It is refused because the manifest is a record other tools
        parse -- the run records write lowercase hex -- and a field that is
        sometimes one spelling and sometimes another is a field every reader
        has to normalise and one of them will forget.
        """

        path, manifest_path = self.loadable_written_panel()
        true_digest = manifest_digest(manifest_path)
        self.assertEqual(verify_daily_panel(path, manifest_path), true_digest)

        for label, recorded in (
            ("uppercase", true_digest.upper()),
            ("not a string", ["a" * 64]),
        ):
            with self.subTest(recorded=label):
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                manifest["sha256"] = recorded
                manifest_path.write_text(
                    json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(
                    DataContractError, "not 64 lowercase hex"
                ) as caught:
                    verify_daily_panel(path, manifest_path)
                message = str(caught.exception)
                self.assertNotIn("is not the file the manifest describes", message)
                self.assertIn(str(manifest_path), message)
                self.assertIn(str(path), message)



class IdentityVerdictTests(unittest.TestCase):
    """A violated identity is a verdict, and the abort belongs where the dependency is.

    `validate_accounting_identities` used to raise `DataContractError` on the
    first violating reference date, from inside `build_point_in_time_snapshot`
    -- the first hop, where no wide panel exists and "which columns this panel
    built" is therefore unknowable. So a violated `sec_nmfp` identity halted
    every build, including builds of the eight columns that have nothing to do
    with it, and `sec_nmfp` supplies a column to none of them: the pricing
    function refuses `mmf_assets` in every build, because the source is
    `snapshot_retrieved_at` with no declared revision policy.

    The decision is recorded in `docs/DATA_QUALITY_DECISIONS.md`, "Whether a
    source may abort a build it contributes nothing to": the verdict is always
    recorded in the quality report, and the abort is scoped to a source that
    actually supplied a column that was built. A scoping, not a loosening --
    which is why the acceptance criterion has two halves and why neither is
    optional. The first half alone is the behaviour before this block. The
    second half alone is the loosening the decision explicitly is not.

    `maximum_residual` now includes violating residuals. It could not have
    before -- the function raised on the first violation, so the field had never
    seen one -- and recording violations while leaving that line where it was
    would have produced a maximum computed over exactly the dates that passed:
    a statistic that falls as the data gets worse. The choice is pinned by
    `test_the_maximum_residual_does_not_exclude_the_violating_dates` rather than
    left to whoever reads the field next.

    Mutation record, 8 September 2026. Every mutation applied to a copy under
    `$HOME` -- never the mount -- carrying `data/`, `.github/`, `metadata/`,
    `.gitignore`, the root Markdown and `docs/PROJECT_STATUS.md`, because
    `tests/test_docs_freshness.py` reads the last three and their absence is two
    kills that look real and are not. Run with `PYTHONDONTWRITEBYTECODE=1` and
    `-B`. Each mutation was reverted before the next was applied. The unmutated
    control was green in that copy **before** the first mutation and again
    **after** the last, so no kill below is an artefact of the copy.

    Exception types are recorded because a red run is not evidence the aimed-at
    test fired: a mutation that breaks an import kills everything and proves
    nothing. Every kill below is an `AssertionError` from the test's own
    assertion, except mutation 2, which is a `DataContractError` reaching the
    test -- and that one is the point of the mutation.

    1. **The acceptance mutation, first half.** Rule 5 removed from
       `build_daily_panel` entirely -- the violation check deleted, the panel
       built regardless. Killed by exactly one test:

       * `test_a_violation_stops_a_panel_that_uses_the_source_and_not_one_that_does_not`
         -- `AssertionError: DataContractError not raised`. By assertion, from
         the second half of the criterion, and not by a `DataContractError`
         arriving from somewhere else.

    2. **The acceptance mutation, second half.** The check widened to raise for
       any source with a violated identity, whether or not it supplied a column
       the panel built -- which is the behaviour before this block. Killed by
       exactly one test, the same one:

       * `test_a_violation_stops_a_panel_that_uses_the_source_and_not_one_that_does_not`
         -- `repo_model.data.DataContractError: sec_nmfp: identity
         series_assets_reconcile_to_liabilities_and_net_assets is violated on 1
         reference date(s)`, raised out of the build that must succeed.

       This is the mutation the brief warned might kill nothing, because it
       restores current behaviour. It killed the criterion's *first* half and
       nothing else in the suite, which is the finding: before this block no
       test anywhere could see a build stopped by a source it did not contain.

    3. **The quality report's violation list emptied**, in
       `PointInTimeAuditReport.as_dict`. Killed by four tests, all in this class:

       * `test_the_quality_report_names_every_violating_reference_date` --
         `AssertionError: Lists differ: [] != ['2026-02-02', '2026-03-02']`
       * `test_the_ingest_hop_writes_the_verdict_into_the_quality_report` --
         `AssertionError: Lists differ: [] != ['2026-02-28']`
       * `test_audit_panel_surfaces_a_recorded_violation` --
         `AssertionError: 0 != 1`
       * `test_a_violation_stops_a_panel_that_uses_the_source_and_not_one_that_does_not`
         -- `AssertionError: Lists differ: [] != ['2026-02-02']`, from the half
         that asserts the surviving build still records what it did not stop for.

    3b. **The same list cut one hop earlier**, in `build_point_in_time_snapshot`:
       the verdicts are still computed and still fit the report, but the ingest
       hop stops handing them over. Killed by exactly one test:

       * `test_the_ingest_hop_writes_the_verdict_into_the_quality_report` --
         `AssertionError: Lists differ: [] != ['2026-02-28']`.

       Run because mutation 3 could not distinguish "the report cannot carry a
       violation" from "nothing ever puts one there", and those fail
       differently: the second leaves every in-memory assertion green while no
       reader ever sees a verdict. One test separates them, and it is the only
       one that runs a real archive through the hop rather than composing the
       two functions by hand.

    4. **The malformed-tolerance path demoted to a verdict too** -- a tolerance
       the schema rejects recorded as `violated` instead of raised. Killed by
       exactly one test, and nothing else fired:

       * `test_a_malformed_tolerance_still_raises_from_the_first_hop` --
         `AssertionError: DataContractError not raised`.

    5. **The boring one, and it was boring.** An unevaluable reference date
       stops being recorded: the `IDENTITY_NOT_EVALUABLE` branch keeps its
       `continue` and drops the `UnevaluatedIdentity`. Killed by exactly one
       test, and it is not in this class:

       * `PointInTimeDataContractTests.test_an_identity_with_an_unobserved_term_is_recorded_unevaluated_not_satisfied`
         -- `AssertionError: 'held' == 'held'`, the assertion `1b6d391` added
         that the withheld and complete panels must not give the same verdict.

       **Zero kills in `IdentityVerdictTests`.** That is the result this
       mutation was run for: the fourth outcome was added without the tests for
       it coming to depend on the third, so a future change to either can still
       be attributed to one of them.

    Deliberately absent: an absolute test count. The kill lists name tests; a
    total would be a transcribed number with nothing asserting it, which is the
    drift `tests/test_docs_freshness.py` refuses in Markdown and is no more
    defensible in a docstring.
    """

    #: A `ref_date`-basis lag, the shape `metadata/sources.json` declares and
    #: the shape `registry.validate_release_lag` accepts. Both fixture sources
    #: use it so that both their columns are priceable and the acceptance test
    #: turns on the identity rather than on a refusal.
    LAG = {
        "basis": "ref_date",
        "unit": "business_days",
        "days": 1,
        "worst_case_calendar_days": 6,
        "available_time": "15:00",
        "timezone": "America/New_York",
        "note": "fixture",
    }

    #: The declared terms of `sec_nmfp`'s balance-sheet identity, named here
    #: exactly as `metadata/sources.json` names them. The fixture registry is
    #: not the real one, but the field names are, so a rename in the source
    #: registry does not leave this test agreeing with itself.
    IDENTITY = {
        "name": "series_assets_reconcile_to_liabilities_and_net_assets",
        "left": ["mmf_cash", "mmf_portfolio_securities", "mmf_other_assets"],
        "right": ["mmf_liabilities", "mmf_net_assets"],
        "tolerance": {"absolute": 0.5, "unit": "USD billions"},
    }

    CLEAN = date(2026, 1, 5)
    VIOLATING = date(2026, 2, 2)
    OTHER_VIOLATING = date(2026, 3, 2)

    def observation(self, series_id, ref_date, value, *, available_offset=1):
        return PointInTimeObservation(
            series_id=series_id,
            ref_date=ref_date,
            available_at=datetime.combine(
                ref_date + timedelta(days=available_offset),
                time(19, 0),
                tzinfo=timezone.utc,
            ),
            value=value,
            vintage_id=f"{series_id}-{ref_date.isoformat()}",
            source_sha="a" * 64,
        )

    def registry(self):
        """Two sources. One clean, one carrying an identity that violates."""

        return {
            "nyfed_sofr": {"release_lag": dict(self.LAG)},
            "sec_nmfp": {
                "release_lag": dict(self.LAG),
                "identities": [dict(self.IDENTITY)],
            },
        }

    def rows(self, *, residuals=None):
        """SOFR from the clean source, a balance sheet from the other.

        `residuals` maps a reference date to the amount by which
        `mmf_other_assets` overstates the left side, in USD billions. A date not
        named reconciles exactly. Every declared term is observed on every date,
        so nothing here is unevaluable and the third outcome stays out of the
        way of the fourth.
        """

        residuals = residuals or {}
        rows = []
        for index, ref_date in enumerate(
            (self.CLEAN, self.VIOLATING, self.OTHER_VIOLATING)
        ):
            rows.append(self.observation("SOFR", ref_date, 4.30 + index / 100))
            net_assets = 9000.0
            rows.append(self.observation("mmf_cash", ref_date, 100.0))
            rows.append(
                self.observation("mmf_portfolio_securities", ref_date, 8850.0)
            )
            rows.append(
                self.observation(
                    "mmf_other_assets", ref_date, 100.0 + residuals.get(ref_date, 0.0)
                )
            )
            rows.append(self.observation("mmf_liabilities", ref_date, 50.0))
            rows.append(self.observation("mmf_net_assets", ref_date, net_assets))
        return rows

    def build(self, rows, columns):
        return build_daily_panel(
            rows,
            self.registry(),
            build_cutoff=datetime(2026, 6, 1, tzinfo=timezone.utc),
            decision_time=time.fromisoformat("15:00"),
            columns=columns,
        )

    def evaluation(self, rows):
        return validate_accounting_identities(rows, self.registry())[
            f"sec_nmfp:{self.IDENTITY['name']}"
        ]

    def test_a_violation_stops_a_panel_that_uses_the_source_and_not_one_that_does_not(
        self,
    ):
        """The acceptance criterion. One fixture, two builds, and both halves matter.

        A registry with two sources, one of which files a balance sheet that
        does not reconcile. A panel whose declared columns draw only on the
        clean source builds -- and the violation is still recorded, because
        scoping the abort is not the same as not looking. A panel whose columns
        draw on the violating source raises, naming the source, the reference
        date, the residual and the bound.

        Without the first half this is the behaviour before the block: any
        violation anywhere stops any build. Without the second it is a
        loosening, which the decision explicitly is not. A test asserting only
        one of them would pass for the wrong implementation in each direction.
        """

        rows = self.rows(residuals={self.VIOLATING: 2.0})

        # Half one. `sofr` comes from `nyfed_sofr`; `sec_nmfp` supplies no
        # column to this build, so its violated identity is a finding about the
        # source and not a reason to stop eight columns that never touched it.
        clean = self.build(rows, ("sofr",))
        self.assertEqual(clean.built_columns, ("sofr",))
        self.assertEqual(
            [row.date for row in clean.observations],
            [self.CLEAN, self.VIOLATING, self.OTHER_VIOLATING],
        )

        # And the violation is recorded rather than dropped: the build that
        # succeeded did not succeed by not looking.
        recorded = self.evaluation(rows)
        self.assertEqual(recorded.verdict, "violated")
        self.assertEqual(recorded.violated_ref_dates, (self.VIOLATING,))
        report = audit_point_in_time_panel(
            rows, violated_identities=recorded.violations
        ).as_dict()
        self.assertEqual(
            [item["ref_date"] for item in report["violated_identities"]],
            [self.VIOLATING.isoformat()],
        )

        # Half two. `mmf_assets` resolves to `sec_nmfp.mmf_net_assets`, so this
        # panel does contain a column the violating source built, and the build
        # stops -- naming what a reader has to know to act on it.
        with self.assertRaises(DataContractError) as caught:
            self.build(rows, ("sofr", "mmf_assets"))
        message = str(caught.exception)
        self.assertIn("sec_nmfp", message)
        self.assertIn(self.IDENTITY["name"], message)
        self.assertIn(self.VIOLATING.isoformat(), message)
        self.assertIn("2", message)  # the residual, 2 USD billions
        self.assertIn("0.5", message)  # against the declared bound
        self.assertIn("mmf_assets", message)

    def test_the_quality_report_names_every_violating_reference_date(self):
        """The dates, not a count -- and every one of them, not the first.

        A count is what let 5.5 years of an unchecked balance sheet read as a
        single number, and the same shape would hide the second violating month
        behind the first. The old code could not have reported more than one
        anyway: it raised on the first, so a second was unreachable by
        construction. This asserts both dates, with the residual and the bound
        each was measured against, through the file a reader actually opens.
        """

        rows = self.rows(residuals={self.VIOLATING: 2.0, self.OTHER_VIOLATING: 3.0})
        evaluation = self.evaluation(rows)

        self.assertEqual(
            evaluation.violated_ref_dates, (self.VIOLATING, self.OTHER_VIOLATING)
        )

        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "panel.csv.quality.json"
        write_point_in_time_audit_report(
            rows, path, violated_identities=evaluation.violations
        )
        written = json.loads(path.read_text(encoding="utf-8"))["violated_identities"]

        self.assertEqual(
            [item["ref_date"] for item in written],
            [self.VIOLATING.isoformat(), self.OTHER_VIOLATING.isoformat()],
        )
        for item, expected in zip(written, (2.0, 3.0)):
            self.assertEqual(item["verdict"], "violated")
            self.assertEqual(item["source_id"], "sec_nmfp")
            self.assertEqual(item["identity"], self.IDENTITY["name"])
            self.assertAlmostEqual(item["residual"], expected)
            self.assertAlmostEqual(item["bound"], 0.5)

        # The bound travels with the residual because neither is readable
        # alone: 2.0 against 0.5 and 2.0 against 10.0 are different findings.
        self.assertTrue(all("bound" in item for item in written))

    def test_a_malformed_tolerance_still_raises_from_the_first_hop(self):
        """A broken declaration is not data, and must not be demoted to a verdict.

        The block converts one raise into a record. It converts exactly one. A
        tolerance the schema does not accept is a fault in what this repository
        wrote, not a finding about what a source published, and a registry that
        cannot be read has no verdict to give -- reporting `violated` for it
        would claim a residual was computed and compared when nothing was.
        """

        registry = self.registry()
        registry["sec_nmfp"]["identities"][0] = dict(self.IDENTITY)
        registry["sec_nmfp"]["identities"][0]["tolerance"] = {
            "absolute": -1.0,
            "unit": "USD billions",
        }
        rows = self.rows(residuals={self.VIOLATING: 2.0})

        with self.assertRaises(DataContractError):
            validate_accounting_identities(rows, registry)

        # Same for a declaration that is not an identity at all. Both are
        # `DataContractError` from the first hop, where they always were.
        registry["sec_nmfp"]["identities"][0] = {"name": "nameless"}
        with self.assertRaises(DataContractError):
            validate_accounting_identities(rows, registry)

    def test_audit_panel_surfaces_a_recorded_violation(self):
        """If nothing surfaces the record, "recorded" means "discarded slowly".

        The verdict now leaves `validate_accounting_identities` as data instead
        of an exception, and data that no reader reaches is worse than the
        traceback it replaced: the traceback at least stopped somebody. So the
        audit report carries it, under its own key, beside the coverage decision
        and the unevaluable dates rather than folded into either -- for the same
        reason those two are separate from each other. "Held", "not checked" and
        "checked and failed" are three facts, and a reader who cannot tell them
        apart will read the third as the first.
        """

        rows = self.rows(residuals={self.VIOLATING: 2.0})
        evaluation = self.evaluation(rows)
        report = audit_point_in_time_panel(
            rows, violated_identities=evaluation.violations
        )

        self.assertEqual(len(report.violated_identities), 1)
        payload = report.as_dict()
        self.assertIn("violated_identities", payload)
        self.assertEqual(len(payload["violated_identities"]), 1)
        record = payload["violated_identities"][0]
        self.assertEqual(record["ref_date"], self.VIOLATING.isoformat())
        self.assertAlmostEqual(record["residual"], 2.0)
        self.assertAlmostEqual(record["bound"], 0.5)
        self.assertIn("exceeds the declared tolerance", record["reason"])

        # Its own key, and not confused with the other two verdicts.
        self.assertEqual(payload["unevaluated_identities"], [])
        self.assertEqual(payload["excluded_cross_sections"], [])

    def test_the_maximum_residual_does_not_exclude_the_violating_dates(self):
        """The summary statistic reports the worst thing it summarises.

        `maximum = max(maximum, residual)` sat after the branch that raised, so
        it had never seen a violating residual and could not have. Recording
        violations without moving that line would have left a maximum computed
        over exactly the dates that passed -- a number that goes *down* as the
        data gets worse, which is the anchoring failure this repository keeps
        naming, in a float.

        So this pins the direction that was chosen, and it is asserted as a
        comparison between two panels rather than against a constant: the same
        fixture with a violation must report a larger maximum than without it.
        """

        clean = self.evaluation(self.rows())
        violating = self.evaluation(self.rows(residuals={self.VIOLATING: 2.0}))

        self.assertEqual(clean.verdict, "held")
        self.assertAlmostEqual(clean.maximum_residual, 0.0)

        self.assertEqual(violating.verdict, "violated")
        self.assertAlmostEqual(violating.maximum_residual, 2.0)
        self.assertGreater(violating.maximum_residual, clean.maximum_residual)

        # Both dates still counted as evaluated: they were checked. Only an
        # absent term makes a date unevaluated, and nothing here is absent.
        self.assertEqual(violating.evaluated_ref_dates, 3)
        self.assertEqual(violating.unevaluated, ())

    def test_the_ingest_hop_writes_the_verdict_into_the_quality_report(self):
        """End to end, through the hop that used to raise instead of report.

        The four tests above compose `validate_accounting_identities` with the
        report writer by hand. This one does not: it runs a real N-MFP archive
        through `build_point_in_time_snapshot` and opens the quality report on
        disk. That matters because the composition is the thing this block
        moved. Before it, this call raised and no quality report was written at
        all -- so a violation reached a reader only as a traceback, and only if
        somebody was watching the build. A test that asserts the record exists
        in memory cannot tell that apart from a record nothing ever writes down.

        The fixture files one cross-section whose `TOTALVALUEOTHERASSETS`
        overstates the left side by 2 USD billions against a declared bound of
        0.5, and a second that reconciles, so the report has to distinguish them
        rather than flag the source wholesale.
        """

        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)

        submissions = [
            {
                "accession": f"{report}-{index}",
                "series": f"S{index:06d}",
                "report": report,
                "net_assets": 9_000_000_000,
                # `sec_nmfp` declares a second identity over daily shareholder
                # flows. It has to be evaluable or it raises "no complete
                # reference date" before the balance sheet is ever reached, and
                # a fixture that only files half a source is not exercising the
                # source. These reconcile, so the report has one violated
                # identity and one held -- which is also the pair a reader needs
                # to see kept apart.
                "flows": ((flow_date, 500_000_000, 400_000_000),),
                **({"other_assets": 2_000_000_000} if breaks else {}),
            }
            for report, flow_date, breaks in (
                ("28-FEB-2026", "27-FEB-2026", True),
                ("31-MAR-2026", "31-MAR-2026", False),
            )
            for index in range(3)
        ]
        artifact = fetch_sec_nmfp(
            root,
            "https://www.sec.gov/files/dera/data/form-n-mfp-data-sets/fixture.zip",
            lambda url: nmfp_archive(submissions),
        )[0]
        registry_path = registry_with_nmfp_coverage_floor(root, 3)

        panel_path = root / "panel.csv"
        build_point_in_time_snapshot(
            [artifact], panel_path, registry_path=registry_path
        )
        report = json.loads(
            panel_path.with_suffix(panel_path.suffix + ".quality.json").read_text(
                encoding="utf-8"
            )
        )

        violated = report["violated_identities"]
        self.assertEqual([item["ref_date"] for item in violated], ["2026-02-28"])
        self.assertEqual(violated[0]["source_id"], "sec_nmfp")
        self.assertEqual(violated[0]["verdict"], "violated")
        self.assertAlmostEqual(violated[0]["residual"], 6.0)
        self.assertAlmostEqual(violated[0]["bound"], 0.5)

        # The build completed. Before this block it raised on the first
        # violating reference date and wrote nothing, which is why the second
        # cross-section could not have been reported either way.
        self.assertTrue(panel_path.exists())


class IdentityToleranceScaleTests(unittest.TestCase):
    """One residual, two cross-sections, opposite verdicts on scale alone.

    `resolve_identity_tolerance` makes the effective bound
    `max(absolute, relative_ppm * 1e-6 * abs(scale))`, so a tolerance that
    declares both parts is not one number applied twice: the same residual is
    inside the bound on a large cross-section and outside it on a small one.
    That difference is the whole content of a relative bound, and no
    absolute-only tolerance can produce it -- an absolute-only tolerance gives
    both cross-sections the same bound, and therefore the same verdict, however
    far apart their scales are.

    The tolerance in these fixtures is invented, and deliberately so. The
    production declaration for `sec_nmfp` is an absolute bound and this block
    left it that way: the residual derived over the admitted cross-sections
    does not license a relative one, and the registry's `tolerance_note`
    records why. What is under test here is that a declared `relative_ppm` is
    *read and applied to scale*, not that any particular number belongs in the
    registry. Calibrating a fixture from the archives would make every
    assertion below depend on a backfill, which is the mistake
    `CoverageEraTests` records one layer up.

    A note on what could not be mutated, because it is a property of the
    bound's shape rather than of this test. The absolute part is a *floor*
    under the relative part, so it can only ever raise the effective bound --
    it admits, and it can never refuse. It follows that no two-cross-section
    fixture can make dropping `relative_ppm` flip a verdict while dropping
    `absolute` also flips one: `max` is monotone in scale, so the larger
    cross-section's bound is never below the smaller's, and the only reachable
    pair of opposite verdicts is (larger held, smaller violated). Removing the
    floor lowers both bounds and leaves that pair unchanged. Mutation 3 below
    is that argument executed rather than asserted.

    Mutation record
    ---------------
    Run in a disposable copy under `$HOME` carrying `data/`, `.github/`,
    `.claude/`, `metadata/`, `.gitignore`, the root Markdown and
    `docs/PROJECT_STATUS.md`, with `PYTHONDONTWRITEBYTECODE=1` and
    `python3 -B`. `.claude/` is absent from `CLAUDE.md`'s copy list and its
    absence costs seven errors in the control; it is copied here anyway and
    that gap is reported. The unmutated control was OK with zero expected
    failures.

    1. **The effective bound ignores `relative_ppm`** -- `resolve_identity_tolerance`
       returns `absolute` alone. 3 failures, all assertion failures: the
       acceptance test here, and `IdentityToleranceTests`'
       `test_the_resolved_bound_moves_with_the_scale` and
       `test_the_absolute_part_is_a_floor_and_not_a_ceiling` in
       `tests/test_contract.py`. This is the acceptance criterion and its own
       mutation target, and they did not come apart.
    2. **The bound stops being a function of scale** -- `_identity_verdict`
       takes `scale = 1.0` instead of the larger side. 1 failure, this test
       alone. The narrowest kill available and the one that names the claim
       exactly: with scale held constant the two cross-sections get one bound,
       and one residual against one bound cannot earn two verdicts. Production
       is untouched by this mutation, every declared tolerance being absolute
       only, which is why nothing else notices.
    3. **The effective bound ignores the absolute floor** -- it returns the
       relative part alone. 5 failures, and **the acceptance test is not among
       them.** This is the argument in the paragraph above, executed rather
       than asserted: the floor can only raise a bound, so removing it cannot
       turn the larger cross-section's `held` into a `violated`, and the pair
       of verdicts this test asserts is unchanged. What the mutation does kill
       is `test_the_absolute_part_is_a_floor_and_not_a_ceiling` in
       `tests/test_contract.py` and four `IdentityVerdictTests` here, whose
       absolute-only production tolerances collapse to a bound of zero. The
       floor is guarded; it is guarded there and not here, and a mutation
       record that did not run this one would have implied otherwise.
    4. **The fixture drops `absolute`**, leaving `relative_ppm` alone -- the
       same claim from the declaration side. The acceptance assertion passes
       unchanged; the run then errors in the collapse assertion below it,
       where removing `relative_ppm` from an already-relative-only tolerance
       leaves a tolerance declaring neither part, and
       `validate_identity_tolerance` refuses it as one that "bounds nothing
       admits everything". A `DataContractError`, not a kill of the criterion,
       and recorded as such: the second assertion is a statement about the
       absolute part being load-bearing *for the pair*, and mutation 3 is why
       only one direction of it can be.
    """

    #: Same residual on both cross-sections, and the scales are far enough
    #: apart that the relative part binds on one and the absolute floor on the
    #: other. 100 ppm of 9000 is 0.9, above the 0.5 floor; 100 ppm of 3000 is
    #: 0.3, below it.
    TOLERANCE = {"absolute": 0.5, "relative_ppm": 100, "unit": "USD billions"}

    LARGE = date(2026, 6, 30)
    SMALL = date(2016, 6, 30)

    @staticmethod
    def _registry(tolerance):
        return {
            "sec_nmfp": {
                "identities": [
                    {
                        "name": "series_assets_reconcile_to_liabilities_and_net_assets",
                        "left": [
                            "mmf_cash",
                            "mmf_portfolio_securities",
                            "mmf_other_assets",
                        ],
                        "right": ["mmf_liabilities", "mmf_net_assets"],
                        "tolerance": dict(tolerance),
                    }
                ]
            }
        }

    def _observations(self):
        """Two cross-sections carrying a residual of 0.7 on scales 9000 and 3000."""

        rows = []
        for ref_date, cash, securities, other, liabilities, net_assets in (
            (self.LARGE, 100.0, 8850.0, 50.0, 200.0, 8799.3),
            (self.SMALL, 50.0, 2930.0, 20.0, 100.0, 2899.3),
        ):
            for series_id, value in (
                ("mmf_cash", cash),
                ("mmf_portfolio_securities", securities),
                ("mmf_other_assets", other),
                ("mmf_liabilities", liabilities),
                ("mmf_net_assets", net_assets),
            ):
                rows.append(
                    PointInTimeObservation(
                        series_id=series_id,
                        ref_date=ref_date,
                        available_at=datetime(
                            ref_date.year, ref_date.month, ref_date.day, 16, 0,
                            tzinfo=timezone.utc,
                        ),
                        value=value,
                        vintage_id=f"{ref_date.isoformat()}-v1",
                        source_sha="0" * 64,
                    )
                )
        return rows

    def _violated_dates(self, tolerance):
        evaluations = validate_accounting_identities(
            self._observations(), self._registry(tolerance)
        )
        evaluation = evaluations[
            "sec_nmfp:series_assets_reconcile_to_liabilities_and_net_assets"
        ]
        self.assertEqual(evaluation.evaluated_ref_dates, 2)
        return [item.ref_date for item in evaluation.violations]

    def test_one_residual_is_admitted_at_one_scale_and_refused_at_another(self):
        # The acceptance criterion. The two cross-sections carry the same
        # residual, so anything that separates them separated them on scale.
        self.assertEqual(self._violated_dates(self.TOLERANCE), [self.SMALL])

        # And the difference is created by the declaration, not present without
        # it: keep the absolute part alone and both cross-sections get the same
        # bound, so the same residual earns the same verdict on both.
        absolute_only = {
            key: value
            for key, value in self.TOLERANCE.items()
            if key != "relative_ppm"
        }
        self.assertEqual(
            self._violated_dates(absolute_only), [self.SMALL, self.LARGE]
        )


class SourceSuppliedNothingTests(unittest.TestCase):
    """A source that supplied nothing cannot fail a build, by any channel.

    `build_daily_panel` rule 5 restricts the registry it checks to the sources
    behind the columns the build made, and its own comment says why: "a source
    that supplied nothing should not be able to fail this build through any
    channel, including a malformed declaration of its own." The restriction
    keyed on the built columns, which is what the panel *declares*, and not on
    what arrived. Those come apart the moment a column is priceable from a
    source whose file the build holds none of -- which is what happens to
    `dealer_treasury_position` and `nyfed_fr2004` the moment the column gains a
    source, because `funding_inputs/` carries no FR 2004 export. Rule 5 then
    evaluated an identity over zero observations, and
    `validate_accounting_identities` raised

        nyfed_fr2004: identity dealer_treasury_total_is_its_declared_components
        has no complete reference date

    out of a build of eight columns that have nothing to do with FR 2004. The
    channel is not the violation branch, which is why the existing scoping did
    not cover it: it is the *malformed-declaration* channel that the comment
    above already names, arriving at a declaration that is not malformed at all.

    **What the skip is keyed on: the source's declared `fields`.** A source is
    checked when the panel built a column from it and at least one of its
    declared series appears among the rows the build can see. Not keyed on the
    identity having a complete reference date, which is the near-miss this class
    exists to separate: that rule passes the empty case and also swallows the
    partial one, where terms were observed but never together on one date. That
    case is a finding about data a source published and must still raise --
    `sec_nmfp` reaches its unevaluable dates through it. A source that declares
    no `fields` is checked as before; "supplied nothing" is a claim about a
    declared vocabulary, and reading an absent list as an empty one would exempt
    every source that declares none. `IdentityVerdictTests`' fixture registry
    declares no fields and is unaffected, which is the property that keeps the
    two halves of the scoping independent.

    **The build records no identity verdict, and there is none to record.**
    `DailyPanelBuild` carries the observations, the built columns, the refusals,
    the holes and the two times; no field of it is a verdict, and the acceptance
    test pins that rather than assuming it. Nor could one be recorded elsewhere
    for the empty case: asked directly, `validate_accounting_identities` raises
    for a source with nothing to evaluate rather than returning a verdict. The
    verdict channel is the quality report at the ingest hop, over the archive
    that source actually supplied. So the empty column is recorded as what it
    is -- a hole count -- and the identity is not answered, because on zero
    observations there is no answer to give.

    Mutation record, 10 September 2026, python3 3.9.6. Every mutation applied in
    a disposable copy under `$HOME`, built from `git ls-files -z --cached
    --others --exclude-standard` so the copy is every tracked file plus the
    untracked ones and nothing gitignored. `PYTHONDONTWRITEBYTECODE=1` and
    `python3 -B`. Each mutation was reverted before the next. The unmutated
    control was red on exactly one test before the first mutation and again
    after the last -- `test_contract.FeatureSourceMapCoverageTests.test_every_
    registry_source_reaches_at_least_one_panel_column`, which is constant while
    the human's move of `dealer_treasury_position` into `FEATURE_FIELDS` is
    pending and is excluded from every kill list below.

    1. **The acceptance mutation.** The supply half of rule 5's restriction
       removed -- `_source_supplied_anything` no longer consulted, so the
       registry is restricted on the built columns alone, which is the behaviour
       before this block. Killed by exactly one test:

       * `test_a_built_column_whose_source_supplied_nothing_builds_empty` --
         `repo_model.data.DataContractError: sec_nmfp: identity
         series_assets_reconcile_to_liabilities_and_net_assets has no complete
         reference date`, raised out of the build that must succeed. The
         exception reaching the test rather than an `AssertionError` is the
         point: the empty case does not fail an assertion, it aborts.

    2. **The trap, keyed on complete dates instead of on supply.**
       `_source_supplied_anything` replaced by a test of whether the identity's
       declared terms share a reference date -- skip when they do not. It passes
       the empty case, which is why it is worth running. Killed by exactly one
       test, through the partial phrase:

       * `test_a_built_column_whose_source_supplied_nothing_builds_empty` --
         `AssertionError: DataContractError not raised`, from the phrase where
         `mmf_cash` and `mmf_net_assets` are each observed and never on the same
         date.

    3. **The skip applied to every source regardless of supply.**
       `_source_supplied_anything` replaced by `return False`, so every source
       is exempt and rule 5 checks nothing at all. Killed by two tests:

       * `test_a_built_column_whose_source_supplied_nothing_builds_empty` --
         `AssertionError: DataContractError not raised`, from the violated
         phrase.
       * `IdentityVerdictTests.test_a_violation_stops_a_panel_that_uses_the_
         source_and_not_one_that_does_not` -- `AssertionError:
         DataContractError not raised`. The second half of the previous block's
         criterion, which is the guard that says this scoping is not a
         loosening; it firing here is the evidence that this block did not blunt
         it.

    Rule 5's code changed under an existing mutation record, so
    `IdentityVerdictTests`' first two mutations were re-run on this tree rather
    than taken on trust -- CLAUDE.md, "if you change a fixture that an existing
    mutation record names". Both still kill the test they name, with the
    exception each records: rule 5 deleted outright gives `AssertionError:
    DataContractError not raised`, and the check widened to every source with an
    identity gives `repo_model.data.DataContractError: sec_nmfp: identity
    series_assets_reconcile_to_liabilities_and_net_assets is violated on 1
    reference date(s)` out of the build that must succeed. Each now also kills
    the acceptance test above, which is the two halves of the scoping being the
    same restriction seen from two sides.
    """

    #: A `ref_date`-basis lag in the shape `metadata/sources.json` declares, so
    #: both fixture columns are priceable and the test turns on rule 5 rather
    #: than on a refusal. The same shape `IdentityVerdictTests` uses.
    LAG = {
        "basis": "ref_date",
        "unit": "business_days",
        "days": 1,
        "worst_case_calendar_days": 6,
        "available_time": "15:00",
        "timezone": "America/New_York",
        "note": "fixture",
    }

    #: `sec_nmfp`'s declared series, named as `metadata/sources.json` names them.
    #: This is the list the skip is keyed on, and it is deliberately wider than
    #: the identity's terms are: the two are the same set here, and the docstring
    #: of `_source_supplied_anything` says which one is consulted.
    FIELDS = [
        "mmf_cash",
        "mmf_portfolio_securities",
        "mmf_other_assets",
        "mmf_liabilities",
        "mmf_net_assets",
    ]

    IDENTITY = {
        "name": "series_assets_reconcile_to_liabilities_and_net_assets",
        "left": ["mmf_cash", "mmf_portfolio_securities", "mmf_other_assets"],
        "right": ["mmf_liabilities", "mmf_net_assets"],
        "tolerance": {"absolute": 0.5, "unit": "USD billions"},
    }

    FIRST = date(2026, 1, 5)
    SECOND = date(2026, 1, 12)

    def registry(self):
        """Two sources, both declaring their fields, one carrying an identity."""

        return {
            "nyfed_sofr": {"release_lag": dict(self.LAG), "fields": ["SOFR"]},
            "sec_nmfp": {
                "release_lag": dict(self.LAG),
                "fields": list(self.FIELDS),
                "identities": [dict(self.IDENTITY)],
            },
        }

    def observation(self, series_id, ref_date, value):
        return PointInTimeObservation(
            series_id=series_id,
            ref_date=ref_date,
            available_at=datetime.combine(
                ref_date + timedelta(days=1), time(19, 0), tzinfo=timezone.utc
            ),
            value=value,
            vintage_id=f"{series_id}-{ref_date.isoformat()}",
            source_sha="a" * 64,
        )

    def sofr_rows(self):
        """The clean source alone. `sofr` is the only REQUIRED_FIELDS column."""

        return [
            self.observation("SOFR", self.FIRST, 4.30),
            self.observation("SOFR", self.SECOND, 4.31),
        ]

    def balance_sheet(self, ref_date, *, residual=0.0):
        """Every declared term on one date. `residual` overstates the left side."""

        return [
            self.observation("mmf_cash", ref_date, 100.0),
            self.observation("mmf_portfolio_securities", ref_date, 8850.0),
            self.observation("mmf_other_assets", ref_date, 100.0 + residual),
            self.observation("mmf_liabilities", ref_date, 50.0),
            self.observation("mmf_net_assets", ref_date, 9000.0),
        ]

    def build(self, rows):
        return build_daily_panel(
            rows,
            self.registry(),
            build_cutoff=datetime(2026, 6, 1, tzinfo=timezone.utc),
            decision_time=time.fromisoformat("15:00"),
            columns=("sofr", "mmf_assets"),
        )

    def test_a_built_column_whose_source_supplied_nothing_builds_empty(self):
        """The acceptance criterion. One fixture, three phrases, and all three matter.

        `mmf_assets` resolves to `sec_nmfp.mmf_net_assets` and is priceable
        under this registry, so the build prices it and rule 5 reaches the
        source behind it. What varies between the phrases is only what that
        source supplied.
        """

        # Phrase one. The source supplied none of its declared series. The build
        # succeeds; the column is present and empty, and empty is recorded as a
        # hole count rather than as a zero or a missing column.
        rows = self.sofr_rows()
        build = self.build(rows)
        self.assertEqual(build.built_columns, ("sofr", "mmf_assets"))
        self.assertEqual(build.refusals, {})
        self.assertEqual(
            [row.date for row in build.observations], [self.FIRST, self.SECOND]
        )
        self.assertEqual(
            [row.values["mmf_assets"] for row in build.observations], [None, None]
        )
        self.assertEqual(build.holes["mmf_assets"], 2)
        self.assertEqual(build.holes["sofr"], 0)

        # The build records no identity verdict for that source, and there is
        # none to record: `DailyPanelBuild` has no verdict field, and the
        # evaluator asked directly refuses rather than returning one, because on
        # zero observations there is no verdict to give. Pinned rather than
        # assumed -- a build that grows one has to say here what it says.
        self.assertEqual(
            [field.name for field in fields(build) if "identit" in field.name], []
        )
        with self.assertRaises(DataContractError) as caught:
            validate_accounting_identities(rows, self.registry())
        self.assertIn("no complete reference date", str(caught.exception))

        # Phrase two. The same source, supplying its balance sheet, with a
        # violation on a date this build can see: it still stops the build. Rule
        # 5 is scoped on supply, not loosened.
        violating = (
            self.sofr_rows()
            + self.balance_sheet(self.FIRST)
            + self.balance_sheet(self.SECOND, residual=2.0)
        )
        with self.assertRaises(DataContractError) as caught:
            self.build(violating)
        message = str(caught.exception)
        self.assertIn("sec_nmfp", message)
        self.assertIn(self.IDENTITY["name"], message)
        self.assertIn(self.SECOND.isoformat(), message)
        self.assertIn("mmf_assets", message)

        # Phrase three. Terms observed, but never together on one reference
        # date. The source supplied something, so it is not exempt, and the
        # unevaluable path still raises -- this is the path `sec_nmfp` relies on
        # and the trap that a skip keyed on complete dates would swallow.
        partial = self.sofr_rows() + [
            self.observation("mmf_cash", self.FIRST, 100.0),
            self.observation("mmf_net_assets", self.SECOND, 9000.0),
        ]
        with self.assertRaises(DataContractError) as caught:
            self.build(partial)
        self.assertIn("no complete reference date", str(caught.exception))
