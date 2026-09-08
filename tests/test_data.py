import sys
import tempfile
import unittest
import json
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
    expected_ref_dates_from_registry,
    fixed_bp_stress_label_columns,
    load_daily_panel,
    load_point_in_time_panel,
    stress_label_threshold,
    validate_publication_gaps,
    validate_accounting_identities,
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

    def test_a_source_that_declares_no_floor_is_a_contract_error(self):
        with self.assertRaisesRegex(DataContractError, "declares no"):
            declared_coverage_floor("sec_nmfp", {"access": "public"})

    def test_a_floor_of_zero_is_rejected_as_the_prohibited_silent_zero(self):
        with self.assertRaisesRegex(DataContractError, "guards nothing"):
            declared_coverage_floor(
                "sec_nmfp",
                {
                    "cross_section": {
                        "entity_unit": "series_id",
                        "minimum_reporting_entities": 0,
                    }
                },
            )

    def test_a_boolean_does_not_pass_as_a_floor(self):
        with self.assertRaisesRegex(DataContractError, "must be an integer"):
            declared_coverage_floor(
                "sec_nmfp",
                {
                    "cross_section": {
                        "entity_unit": "series_id",
                        "minimum_reporting_entities": True,
                    }
                },
            )

    def test_an_unnamed_entity_unit_is_rejected(self):
        with self.assertRaisesRegex(DataContractError, "entity_unit"):
            declared_coverage_floor(
                "sec_nmfp",
                {"cross_section": {"minimum_reporting_entities": 200}},
            )

    def test_an_unpermitted_key_is_rejected_rather_than_ignored(self):
        with self.assertRaisesRegex(DataContractError, "unpermitted keys"):
            declared_coverage_floor(
                "sec_nmfp",
                {
                    "cross_section": {
                        "entity_unit": "series_id",
                        "minimum_reporting_entities": 200,
                        "minimum_net_assets": 1000,
                    }
                },
            )

    def test_the_live_registry_declaration_is_readable(self):
        registry = json.loads(
            (Path(__file__).parents[1] / "metadata" / "sources.json").read_text(
                encoding="utf-8"
            )
        )
        entity_unit, floor = declared_coverage_floor(
            "sec_nmfp", registry["sec_nmfp"]
        )
        self.assertEqual(entity_unit, "series_id")
        self.assertGreaterEqual(floor, 1)


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

    def test_a_hole_is_not_the_previous_value(self):
        """A `ref_date` with no observation for a column stays empty.

        The gap is a real one: 6 January carries an observation for `tgcr` and
        none for `sofr`, so the `sofr` cell is `None` -- not 4.30 carried
        forward, not 0.0, and not the row's absence from the panel.
        """

        rows = [
            self.observation(date(2026, 1, 5), 4.30),
            self.observation(date(2026, 1, 7), 4.32),
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
        build = self.build(registry, rows, columns=("sofr", "tgcr"))

        by_date = {row.date: row.values for row in build.observations}
        self.assertEqual(sorted(by_date), [date(2026, 1, 5), date(2026, 1, 6), date(2026, 1, 7)])
        self.assertIsNone(by_date[date(2026, 1, 6)]["sofr"])
        self.assertAlmostEqual(by_date[date(2026, 1, 5)]["sofr"], 4.30)
        self.assertAlmostEqual(by_date[date(2026, 1, 7)]["sofr"], 4.32)

    def test_holes_are_counted_not_filled(self):
        """`holes` counts the empty cells the panel kept, per built column."""

        rows = [
            self.observation(date(2026, 1, 5), 4.30),
            self.observation(date(2026, 1, 7), 4.32),
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
        build = self.build(registry, rows, columns=("sofr", "tgcr"))
        self.assertEqual(len(build.observations), 3)
        self.assertEqual(build.holes, {"sofr": 1, "tgcr": 2})

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
