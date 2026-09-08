import sys
import tempfile
import unittest
import json
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from repo_model.data import (
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
        with self.assertRaisesRegex(DataContractError, "residual"):
            validate_accounting_identities(rows[:-1], bad)

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
            with self.assertRaisesRegex(DataContractError, "residual"):
                validate_accounting_identities(wildly_broken, relative)

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
