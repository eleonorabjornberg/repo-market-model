import contextlib
import hashlib
import io
import sys
import tempfile
import unittest
import unittest.mock
import json
from dataclasses import fields, replace
from datetime import date, datetime, time, timedelta, timezone
from types import MappingProxyType
from zoneinfo import ZoneInfo
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from repo_model.data import (
    IDENTITY_HELD,
    IDENTITY_HELD_WHERE_EVALUABLE,
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

    def test_the_interquartile_range_is_a_width_in_basis_points(self):
        """`p75 - p25`, scaled like `spread_bps`, and never the reverse.

        The reader test in `tests/test_contract.py` checks that
        `contract.DERIVED_FEATURES` names the columns this property reads. It
        cannot check the arithmetic: swapping the operands or dropping the
        scale leaves the same two columns being read, so both pass it
        untouched. This is the guard for the arithmetic, and the swap is the
        case that matters -- an inverted range is a sign error that reads as an
        unusually narrow day rather than as an error.

        Mutation record, 12 September 2026, the mount's `.venv/bin/python`
        against copies staged under `$HOME`, `PYTHONDONTWRITEBYTECODE=1`,
        `python3 -B`, `OMP_NUM_THREADS=1`, the whole suite each time, reverted
        and confirmed byte-identical after. Unmutated control green before and
        after; the control carrying this test against a tree without the
        property errors here and nowhere else.

        1. **Operands swapped** -- `p25 - p75`. One failure, this test,
           `AssertionError: -2.000000000000046 != 2.0 within 7 places`. Nothing
           else in the suite moved.
        2. **The basis-point scale dropped** -- `100.0` to `1.0` in this
           property only. One failure, this test,
           `AssertionError: 0.020000000000000462 != 2.0 within 7 places`.
           Nothing else moved.
        3. **The declaration narrowed** -- `DERIVED_FEATURES["sofr_iqr_bps"]`
           cut to `("sofr_p75",)`. Killed
           `test_contract.FeatureSourceMapCoverageTests`'
           `test_a_derived_feature_declares_the_columns_its_implementation_reads`
           and **not** this test. That is the division of labour the two guards
           are supposed to have: the reader test holds the declaration against
           the implementation, this one holds the arithmetic, and neither
           covers for the other.

        Recording how mutation 2 nearly went unrun: its first attempt guarded
        application with `grep -cF` on a multi-line anchor, which counts
        matching *lines* rather than occurrences, saw three and refused. The
        refusal was correct and the anchor was not; counting an exact substring
        in python is what settled it.
        """

        path = self.write_csv(
            "date,sofr,iorb,sofr_p25,sofr_p75\n"
            "2026-01-02,4.31,4.30,4.30,4.32\n"
        )
        rows = load_daily_panel(path)
        self.assertAlmostEqual(rows[0].sofr_iqr_bps, 2.0)
        self.assertGreater(rows[0].sofr_iqr_bps, 0.0)

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

    Addendum, 12 September 2026 -- A30, and mutation 2 re-run
    ---------------------------------------------------------
    `_priceable_columns` now prices a `snapshot_retrieved_at` column from the
    rows the build can see. Mutation 2's test had used a bare snapshot source as
    its registry refusal, and that refusal was the defect: every row carries
    `available_at`, so `sofr` there is now built. The fixture's `SOFR` field now
    declares a `record_date` lag with no `revision_policy`, which the registry
    refuses on the declaration's own terms whatever the rows.

    Mutation 2 re-run on the changed fixture, same conditions, python3 3.9.6.
    The list has to change with the tree: the pricing function no longer refuses
    the set recorded above, so the hard-coded set is `{"mmf_assets"}`, with the
    retry through rows disabled. Still killed by
    `test_a_column_is_refused_by_the_registry_not_by_a_list`,
    `AssertionError: DataContractError not raised`. It is no longer the only
    kill -- a one-name list is not the panel the tracked registry builds -- and
    the rest are recorded so they are not misread: `SnapshotBasisPricingTests`'
    acceptance test, all four parts; `IdentityVerdictTests.test_a_violation_
    stops_a_panel_that_uses_the_source_and_not_one_that_does_not` and
    `SourceSuppliedNothingTests.test_a_built_column_whose_source_supplied_
    nothing_builds_empty` (`AssertionError`); and two errors,
    `test_the_written_panel_records_its_cutoff_and_its_refusals`
    (`DataContractError`: with `iorb` built on no rows, no date carries both
    required columns) and `RequestedColumnsBuildTests`' acceptance test
    (`KeyError: 'quarter_end'`: the calendar column, refused today by the
    pricing function's empty-selection error, is built unpriced and is not in
    `FEATURE_FIELDS`).
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
        `sofr` is built; moved to a `snapshot_retrieved_at` source whose `SOFR`
        field declares a `record_date` lag with no `revision_policy` -- a field
        declaration talking the snapshot refusal out of a correct answer --
        `registry.max_release_lag_days` refuses it, and so does the join. A
        hard-coded refused set in `data.py` cannot follow that, which is what
        makes this the test for mutation 2.

        Until A30 the snapshot registry here declared no field lag at all, and
        was refused only because `_priceable_columns` handed the pricing
        function no rows. That was the defect A30 repairs: every row here
        carries `available_at`, so a bare snapshot source now prices `sofr`
        from them. The refusal this test needs is now one the registry makes
        on the declaration's own terms. See the addendum in the class docstring.
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
                },
                "field_release_lags": {
                    "SOFR": {
                        "basis": "record_date",
                        "unit": "calendar_days",
                        "days": 1,
                        "available_time": "16:15",
                        "timezone": "America/New_York",
                        "note": "fixture: no revision_policy, so not priceable",
                    }
                },
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
    `python3 -B`. Each mutation was reverted before the next. When this record
    was written the unmutated control was red on exactly one test, before the
    first mutation and again after the last --
    `test_contract.FeatureSourceMapCoverageTests.test_every_registry_source_
    reaches_at_least_one_panel_column` -- and it was excluded from every kill
    list below. **Re-run 10 September 2026 at block A14, python3 3.9.6, after
    the human's move of `dealer_treasury_position` into `contract.FEATURE_FIELDS`
    landed: the control is green, that exclusion no longer applies to anything,
    and mutation 1 now kills two tests rather than one.** Mutations 2 and 3 kill
    exactly what they killed.

    1. **The acceptance mutation.** The supply half of rule 5's restriction
       removed -- `_source_supplied_anything` no longer consulted, so the
       registry is restricted on the built columns alone, which is the behaviour
       before this block. Killed by two tests:

       * `test_a_built_column_whose_source_supplied_nothing_builds_empty` --
         `repo_model.data.DataContractError: sec_nmfp: identity
         series_assets_reconcile_to_liabilities_and_net_assets has no complete
         reference date`, raised out of the build that must succeed. The
         exception reaching the test rather than an `AssertionError` is the
         point: the empty case does not fail an assertion, it aborts.
       * `RequestedColumnsBuildTests.test_a_build_given_the_manifests_columns_
         reproduces_its_digest_after_a_source_joins` -- `AssertionError: 2 != 0`,
         the CLI's exit code, carrying `nyfed_fr2004: identity
         dealer_treasury_total_is_its_declared_components has no complete
         reference date`. This is the second kill the move brought with it, and
         it is the case this class's docstring describes in prose: a column
         priceable from a source whose export the build holds none of. It could
         not fire while the move was pending, because no build then depended on
         `nyfed_fr2004`.

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


class RequestedColumnsBuildTests(unittest.TestCase):
    """`build --column`: the published panel is pinned to its manifest's columns.

    The default build is every column in `data.PANEL_COLUMNS` that latest
    vintage can carry. That set is not fixed: it widens the moment a column
    gains an ingesting source. `metadata/funding_panel_manifest.json` records
    `built_columns` and a `sha256` over the panel those columns produce, so the
    day `dealer_treasury_position` moves out of `contract.UNSOURCED_FEATURES`
    and into `contract.FEATURE_FIELDS` against `nyfed_fr2004`, the default build
    of the tracked `funding_inputs/` grows a ninth, entirely empty column and
    stops reproducing the published digest -- without one number in the panel
    changing. User decision, 10 September 2026: the published panel is pinned to
    its manifest's `built_columns`, so a source joining the registry never moves
    it, and `scripts/reproduce_milestone_a.py` passes `--column` per
    `built_columns` (the human's change, not this block's).

    **What this test patches, and why it becomes a no-op.** `contract.py` is
    human-owned and the FR 2004 move has not landed, so the test simulates
    exactly that move's `contract.py` hunk for its own duration: it adds
    `dealer_treasury_position -> (("nyfed_fr2004", "PDPOSGST-TOT"),)` to
    `FEATURE_FIELDS`, reprojects `FEATURE_SOURCES` from it the way `contract.py`
    does, and drops `dealer_treasury_position` from `UNSOURCED_FEATURES`.
    Nothing else. `build_daily_panel` and `_priceable_columns` both read these
    three names off the module at call time, so the patch reaches them without
    touching either. Once the human's move lands the patch sets each name to
    what it already holds and the test asserts the same six things about the
    same tree.

    **Through the CLI, in process.** `repo_model.cli.main` is what
    `scripts/reproduce_milestone_a.py` invokes, so it is what the criterion is
    stated over; in process rather than as a subprocess because the simulated
    contract move has to be visible to the code under test. `main` returns 2 on
    any `ValueError`, which is the exit code every refusal below is asserted
    through.

    Measured on this tree, python3 3.9.6, with the patch applied: the default
    build hashes to `d6e9a2b2...af16` and the manifest's columns to
    `b6af33bb...4bec`, which is the digest `metadata/funding_panel_manifest.json`
    records. Those two figures are the premise and the fix, and the test
    computes both rather than restating them.

    Mutation record, 10 September 2026, python3 3.9.6. Every mutation applied
    in a disposable copy under `$HOME`, built from `git ls-files -z --cached
    --others --exclude-standard` so the copy is every tracked file plus the
    untracked ones and nothing gitignored. `PYTHONDONTWRITEBYTECODE=1` and
    `python3 -B`. Each mutation was reverted before the next, and the unmutated
    control was green before the first and after the last -- see the report for
    the one pre-existing red this tree carries.

    When this record was written every mutation below also left one
    pre-existing red, `test_contract.FeatureSourceMapCoverageTests.test_every_
    registry_source_reaches_at_least_one_panel_column`, excluded from every kill
    list -- the same constant red `SourceSuppliedNothingTests` records. **The
    human's move of `dealer_treasury_position` into `contract.FEATURE_FIELDS`
    has landed and the control is green; the exclusion applies to nothing.** The
    kill lists below are unchanged by it.

    1. **`--column` ignored.** Both the sites that read `args.column` in
       `cli_data._build` disabled: `columns = _requested_columns(...) if ...`
       replaced by `columns = PANEL_COLUMNS`, and the `build.refusals` guard's
       condition replaced by `False`, so the flag has no effect anywhere. This
       is the mutation the premise assertion exists for -- with the flag
       ignored, the requested-columns build *is* the default build, and only a
       test that has already pinned the default build's digest as not the
       manifest's can tell the difference. Killed by:

       * `test_a_build_given_the_manifests_columns_reproduces_its_digest_after_
         a_source_joins` -- `AssertionError: 'd6e9a2b2af6f...ccb32af16' !=
         'b6af33bb7c64...4dd332c4bec'`, from the reproduce assertion, the
         premise assertion having passed one line above it.

       Disabling only the `columns = ...` line, leaving the refusals guard
       reading `args.column`, is a weaker mutation and was run separately: it is
       killed earlier and for a different reason -- `AssertionError: 2 != 0 :
       error: --column asked for a column this build cannot price: mmf_assets:
       ...; on_rrp: ...`, the pinned build now carrying the default build's six
       refusals. Recorded because it is not the premise-then-reproduce kill and
       would be misread as one.

    2. **The trap: order passed through.** `_requested_columns`' return replaced
       by `tuple(requested)`, so the columns reach `build_daily_panel` in flag
       order. Both the premise and the manifest-order reproduce assertion still
       pass -- the manifest lists `built_columns` in `PANEL_COLUMNS` order, so
       that case is order-independent by accident. Killed by:

       * the same test -- `AssertionError: '952e973951ea...41cfaf3f8e' !=
         'b6af33bb7c64...4dd332c4bec'`, from the reversed-order assertion.
         `write_daily_panel` writes its header from `built_columns`, so the
         reversed request writes `date,treasury_settlement,bgcr,...` and hashes
         to a third digest.

    3. **Each refusal made a no-op**, one at a time, each killed by its own
       phrase in this test, and every one of them through the same shape:
       `AssertionError: 0 != 2`, the build exiting **0** having written a
       one-column panel. That shape is the finding. `_requested_columns` keys on
       a set and walks `PANEL_COLUMNS`, so with a check gone the bad request is
       not passed through to fail somewhere downstream -- it is silently
       repaired into a different build:

       * the duplicate `raise` deleted -- exit 0, `"built_columns": ["sofr"]`,
         the repeat absorbed by the set. The `date,sofr,sofr` header the check
         is named after is what the *unnormalised* request produces, not this
         one;
       * the unknown-column `raise` deleted -- exit 0, `"built_columns":
         ["sofr"]`. `sofr_rate` is not in `PANEL_COLUMNS`, so it is simply never
         emitted; it never reaches `build_daily_panel` and no
         `UndeclaredFeatureError` is raised. Deleting both checks together gives
         the same exit 0 and the same one-column panel, not a compound failure;
       * the `build.refusals` `raise` deleted -- exit 0, `"built_columns":
         ["sofr"]` and `"refused_columns": {"on_rrp": "fred_macro_latest_
         vintage: every snapshot row must carry available_at"}`. The column was
         asked for by name and the panel came back without it, with the reason
         in the manifest and exit 0 on the terminal, which is the case this
         assertion exists for.

    Addendum, 12 September 2026 -- A30. The unpriced column asked for by name
    is `quarter_end`, not `on_rrp`: A30 prices a snapshot column from the rows
    the build can see, and `funding_inputs/` carries `on_rrp`'s. The manifest's
    `refused_columns` still names both, because it records the published build.
    The two mutations that read this phrase were re-run, python3 3.9.6, same
    conditions as above:

    * the `build.refusals` `raise` deleted -- killed by the same test,
      `AssertionError: 0 != 2`, exit 0 with `quarter_end` absent from the panel;
    * only the `columns = ...` line disabled -- killed by the same test,
      `AssertionError: 2 != 0`, the refusals now naming `mmf_assets` (no
      `sec_nmfp` rows in `funding_inputs/`), `quarter_end` and the rest; and
      also `test_generated_results.MilestoneAReproductionTests.test_the_
      published_persistence_run_reproduces_from_tracked_inputs`, whose build
      exits 2 for the same reason.

    The pinned build still reproduces the manifest's digest after A30: the
    manifest's `built_columns` hold no snapshot-basis column.
    """

    #: The FR 2004 move's `contract.py` hunk, and nothing else. The human's
    #: move has landed, so this is now a no-op: each name is set to what
    #: `contract.py` already holds. Kept rather than deleted, because what it
    #: guards is not the move -- it is that this test states its own premise
    #: instead of inheriting it. A later change to `FEATURE_FIELDS` that took
    #: `dealer_treasury_position` back out would make the criterion vacuous, and
    #: with the patch in place it stays exactly as sharp as it is today.
    MOVED_FEATURE = "dealer_treasury_position"
    MOVED_PAIRS = (("nyfed_fr2004", "PDPOSGST-TOT"),)

    @contextlib.contextmanager
    def source_joins_the_contract(self):
        """`dealer_treasury_position` gains its source, for this block only."""

        from repo_model import contract

        fields_map = dict(contract.FEATURE_FIELDS)
        fields_map[self.MOVED_FEATURE] = self.MOVED_PAIRS
        # Reprojected from `FEATURE_FIELDS` exactly as `contract.py` derives it,
        # rather than written out a second time here.
        sources_map = {
            feature: tuple(sorted({source for source, _field in pairs}))
            for feature, pairs in fields_map.items()
        }
        unsourced = {
            name: reason
            for name, reason in contract.UNSOURCED_FEATURES.items()
            if name != self.MOVED_FEATURE
        }
        with unittest.mock.patch.multiple(
            contract,
            FEATURE_FIELDS=MappingProxyType(fields_map),
            FEATURE_SOURCES=MappingProxyType(sources_map),
            UNSOURCED_FEATURES=MappingProxyType(unsourced),
        ):
            yield

    def run_build(self, output, *columns):
        """`repo_model.cli build` over the tracked inputs. Returns (code, text)."""

        from repo_model import cli

        root = Path(__file__).parents[1]
        manifest = json.loads(
            (root / "metadata" / "funding_panel_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        argv = [
            "build",
            "--raw-root", str(root / "tests" / "fixtures" / "snapshots" / "funding_inputs"),
            "--registry", str(root / "metadata" / "sources.json"),
            "--output", str(output),
            "--build-cutoff", manifest["build_cutoff"],
            "--decision-time", manifest["decision_time"],
        ]
        for column in columns:
            argv += ["--column", column]
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(argv)
        return code, out.getvalue() + err.getvalue()

    def digest_of(self, directory, name, *columns):
        """Build into a fresh name and return the panel's SHA-256."""

        panel = Path(directory) / f"{name}.csv"
        code, text = self.run_build(panel, *columns)
        self.assertEqual(code, 0, text)
        return hashlib.sha256(panel.read_bytes()).hexdigest()

    def test_a_build_given_the_manifests_columns_reproduces_its_digest_after_a_source_joins(
        self,
    ):
        """The acceptance criterion. Six assertions, and the first is the premise."""

        root = Path(__file__).parents[1]
        manifest = json.loads(
            (root / "metadata" / "funding_panel_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        published = manifest["sha256"]
        built_columns = list(manifest["built_columns"])

        with self.source_joins_the_contract(), tempfile.TemporaryDirectory() as tmp:
            # The premise. With the source joined, the default build carries a
            # ninth column -- empty in every row, because `funding_inputs/`
            # holds no FR 2004 export -- and no longer hashes to the published
            # digest. Asserted, not assumed: if the default build still
            # reproduced, `--column` would be pinning nothing.
            default = self.digest_of(tmp, "default")
            self.assertNotEqual(default, published)

            # The fix. The manifest's own `built_columns`, and the bytes are the
            # bytes the manifest records.
            self.assertEqual(self.digest_of(tmp, "pinned", *built_columns), published)

            # ...and the digest is a function of the set, not of the order the
            # flags were typed in. The panel carries its columns in
            # `PANEL_COLUMNS` order however they were asked for.
            self.assertEqual(
                self.digest_of(tmp, "reversed", *reversed(built_columns)), published
            )

            # A column asked for twice is refused, rather than absorbed by the
            # set `_requested_columns` keys on and built as a narrower panel.
            code, text = self.run_build(Path(tmp) / "dup.csv", "sofr", "sofr")
            self.assertEqual(code, 2, text)
            self.assertIn("more than once", text)

            # A name that is not a panel column is refused here, by name.
            # Nothing downstream would catch it: it is not in `PANEL_COLUMNS`,
            # so it is never emitted and never reaches the pricing function.
            code, text = self.run_build(Path(tmp) / "unknown.csv", "sofr", "sofr_rate")
            self.assertEqual(code, 2, text)
            self.assertIn("is not a panel column", text)

            # A panel column this build cannot price is refused rather than
            # silently absent. `quarter_end` is a declared column and is in the
            # manifest's `refused_columns`; asked for by name it must not come
            # back as a panel without it. It was `on_rrp` until A30, which
            # prices a snapshot column from the rows the build can see, and
            # this build can see `on_rrp`'s; `quarter_end` is calendar-only and
            # refused whatever the rows.
            self.assertIn("quarter_end", manifest["refused_columns"])
            code, text = self.run_build(Path(tmp) / "unpriced.csv", "sofr", "quarter_end")
            self.assertEqual(code, 2, text)
            self.assertIn("cannot price", text)
            self.assertIn("quarter_end", text)


class FR2004EraIdentityTests(unittest.TestCase):
    """`PDPOSGST-TOT`'s identity is checked on every week, against its own era's terms.

    The defect this closes
    ----------------------

    `metadata/sources.json` declared one identity over the thirteen components
    the New York Fed publishes today. The tracked extract
    `tests/fixtures/snapshots/fr2004/pdposgst_tot_and_components.csv` carries 700
    weekly as-of dates from 2013-04-03, and only 243 of them -- 2022-01-05
    onwards -- carry all thirteen. On the other 457 the identity came back
    `not_evaluable`, which is honest and is also five sixths of the history
    behind a guard that could not fail. The source's vocabulary has a history:
    there is no floating-rate-note bucket (`PDPOSGS-BFRN`) before 2015-01-07, and
    the over-eleven-year nominal coupon bucket is one series (`PDPOSGSC-G11`)
    until 2021-12-29 and two (`PDPOSGSC-G11L21`, `PDPOSGSC-G21`) from 2022-01-05.
    `docs/DATA_QUALITY_DECISIONS.md`, "Dealer Treasury positions", records the
    three eras; the extract's sidecar records them as `identity_eras`.

    Why not one identity over the union
    -----------------------------------

    The repair that suggests itself is to declare all fifteen terms once and let
    the absent ones fall out. It does not work, and the way it fails is the
    reason `not_evaluable` exists. Over the union, an early week is missing the
    later era's terms, so the union identity is `not_evaluable` on *every* date
    rather than on 457 of them -- strictly worse. Make it evaluate by reading an
    absent term as `0.0` and it `holds` on every date instead, because the
    missing buckets are on the right-hand side and contribute nothing to a sum
    that already balances. That is a guard that passes 700 times while checking
    nothing, and it turns an absence into a measured value, which
    `docs/DATA_QUALITY_DECISIONS.md` forbids outright (a `*` suppression is not
    a zero either). So the test below does not stop at "every week holds": it
    plants a week missing one of *its own era's* terms and requires
    `not_evaluable` naming that term. A union-with-zeros implementation passes
    the first assertion and dies on that one.

    The three refusals
    ------------------

    An era declaration is a piece of this repository's own writing, so a
    malformed one raises `DataContractError` rather than being recorded as a
    finding about the data -- the same split `validate_accounting_identities`
    already makes. Two overlapping windows would make a date's term set depend
    on which era is consulted first, and a term set chosen by list order is not
    a declaration. An era whose `from` is after its `through` covers no date at
    all, so every date it was written for would quietly become undeclared. And a
    date covered by no era is recorded `not_evaluable` with
    `undeclared_ref_date` set rather than skipped, because a date the
    declaration is silent about is not a date the identity held on -- the same
    finding `CrossSectionCoverage` records as "ref_date falls in no declared
    coverage era", one hop down.

    Contiguity, and what an era window claims
    -----------------------------------------

    The declared windows abut -- `2015-01-06`/`2015-01-07` and
    `2022-01-04`/`2022-01-05` -- rather than ending on each era's last observed
    as-of date (2014-12-31 and 2021-12-29). An era window is a claim about which
    vocabulary was in force, not a claim that an as-of date exists inside it, and
    ending on the last observed date would leave the turn-of-year weeks declared
    by nobody: a date arriving there later would be recorded `not_evaluable`
    instead of checked. Before 2013-04-03 there is deliberately no era, because
    the earlier report used other vocabularies, ends 2013-03-27, and is not
    mapped.

    Mutation record
    ---------------

    Every mutation applied in a disposable copy under `$HOME`, built from
    `git ls-files -z --cached --others --exclude-standard` so the copy is every
    tracked file plus the untracked ones and nothing gitignored, at the per
    branch and per commit path `CLAUDE.md` now specifies.
    `PYTHONDONTWRITEBYTECODE=1` and `python3 -B`, Python 3.9.6. Each mutation was
    reverted before the next, and the unmutated control was green before the
    first and after the last -- the pre-existing red that
    `SourceSuppliedNothingTests` and `FR2004DealerPositionTests` both record as
    constant is gone, because the human's move of `dealer_treasury_position`
    into `contract.FEATURE_FIELDS` has landed. Every kill below is an
    `AssertionError` unless the entry says otherwise.

    1. **Era windows ignored -- the defect itself.** `declared_identity_eras`
       reads `declared = None` in place of `identity.get("eras")`, so every
       identity gets the single unbounded era of its top-level terms and the
       declaration's `eras` are inert. Killed by exactly one test:

       * this one -- `AssertionError: 'held_where_evaluable' != 'held'`. The 457
         pre-2022 weeks go back to `not_evaluable`, which is the tree as it
         stood before this block.

    2. **The overlap refusal a no-op.** The `if` guarding the overlap raise in
       `declared_identity_eras` replaced by `if False:`. Killed by exactly one
       test:

       * this one -- `AssertionError: DataContractError not raised`, at the
         phrase that widens the first era's `through` onto the second era's
         `from`.

    3. **The order refusal a no-op.** The `if` guarding the `from`-after-
       `through` raise replaced by `if False:`, the same way. Killed by exactly
       one test:

       * this one -- `AssertionError: DataContractError not raised`, at the
         phrase that swaps the middle era's two bounds. 2 and 3 both report
         `DataContractError not raised` because each removed the only refusal
         its own phrase reaches, and each mutated copy carried one defect.

    4. **The restatement refusal a no-op.** The `if` comparing the most recent
       era's terms with the identity's top-level ones replaced by `if False:`.
       Killed by exactly one test:

       * this one -- `AssertionError: DataContractError not raised`, at the
         phrase that drops `PDPOSTIPS-G11` from the top level only.

    5. **An absent term read as zero.** `_identity_verdict`'s `absent` tuple
       replaced by `()` and both sums by `float(values[field] or 0.0)`, so no
       date is ever `not_evaluable` and a missing term contributes nothing.
       Killed by four tests:

       * this one -- `AssertionError: 'violated' != 'held_where_evaluable'`, at
         the planted week: the withheld term is on the right-hand side, so the
         sum comes up short by exactly it and the week reads as a violation
         rather than as unevaluable;
       * `PointInTimeDataContractTests.test_an_identity_with_an_unobserved_term_
         is_recorded_unevaluated_not_satisfied` -- `AssertionError: True is not
         false`;
       * `SourceSuppliedNothingTests.test_a_built_column_whose_source_supplied_
         nothing_builds_empty` -- `AssertionError`, on the phrase that expects
         "no complete reference date" and gets `sec_nmfp`'s identity violated
         instead;
       * `FR2004DealerPositionTests.test_the_fr2004_dealer_total_is_its_
         components_on_its_release_date` -- `AssertionError`, on a
         `ViolatedIdentity` where `()` is asserted.

    6. **The trap, applied whole: one identity over the union, with zeros.**
       Mutation 5's two hunks, plus mutation 1's, plus `PDPOSGSC-G11` inserted
       into the identity's top-level `right` in `metadata/sources.json` -- so
       the declaration really is a single identity over all fifteen terms and an
       absent term really is a zero. This is the shape worth running because it
       is the one that looks correct: **it passes the 700-week block.** Every
       week reports `held`, because the terms missing from a week are on the
       right-hand side and contribute nothing to a sum that already balances, so
       an implementation that checks nothing agrees with one that checks
       everything on the assertion a reader would think of first. Killed by the
       same four tests as mutation 5 and by the same messages; on this test it
       is again the planted week and not the 700-week block that fails --
       `AssertionError: 'violated' != 'held_where_evaluable'`. The planted-
       absence phrase is therefore the only thing standing between this suite
       and a guard that passes 700 times while checking nothing, which is why
       it is in the acceptance test and not in a separate one.
    """

    EXTRACT = (
        Path(__file__).parents[1]
        / "tests"
        / "fixtures"
        / "snapshots"
        / "fr2004"
        / "pdposgst_tot_and_components.csv"
    )
    REGISTRY_PATH = Path(__file__).parents[1] / "metadata" / "sources.json"

    KEY = "nyfed_fr2004:dealer_treasury_total_is_its_declared_components"

    #: The bucket the New York Fed retired at the 2022-01-05 report. Declared in
    #: `fields` for the two earlier eras and carried by no current export.
    RETIRED = "PDPOSGSC-G11"

    #: One week inside each era, and the term this test withholds from it. Each
    #: term belongs to that era and to at most one other, so a verdict that
    #: turned on the union rather than on the era could not produce these.
    ERA_WEEKS = (
        ("no_frn_combined_over_11", date(2013, 4, 3), RETIRED),
        ("frn_combined_over_11", date(2016, 6, 1), "PDPOSGS-BFRN"),
        ("frn_split_over_11", date(2024, 10, 2), "PDPOSGSC-G21"),
    )

    #: A week before `PDPOSGST-TOT`'s first as-of date, and therefore inside no
    #: declared era. 2013-03-27 is the last as-of date of the earlier, unmapped
    #: vocabulary, so it is the date a splice would have reached for.
    UNDECLARED_WEEK = date(2013, 3, 27)

    def registry(self):
        """Only the source under test, the way `build_daily_panel` restricts it.

        `validate_accounting_identities` evaluates every identity in whatever
        registry it is handed and raises on one with no complete reference date.
        The whole registry would fail here on `sec_nmfp`'s balance sheet, which
        these observations say nothing about.
        """

        registry = json.loads(self.REGISTRY_PATH.read_text(encoding="utf-8"))
        return {"nyfed_fr2004": registry["nyfed_fr2004"]}

    def identity(self, registry):
        return registry["nyfed_fr2004"]["identities"][0]

    def extract_rows(self):
        """The tracked extract, parsed by the adapter and not by this test.

        Through `parse_snapshots` rather than by reading the CSV here, so the
        unit conversion, the per-row as-of date and the `*` handling are the
        ones the adapter actually performs. A second reader in this file would
        be a second thing to keep in step with the export's layout.
        """

        from repo_model.ingest import SnapshotArtifact, parse_snapshots

        payload = self.EXTRACT.read_bytes()
        artifact = SnapshotArtifact(
            source_id="nyfed_fr2004",
            path=self.EXTRACT,
            retrieved_at="2026-09-10T00:00:00+00:00",
            sha256=hashlib.sha256(payload).hexdigest(),
            url=None,
            byte_count=len(payload),
        )
        return list(parse_snapshots([artifact], registry=self.registry()).rows)

    def evaluate(self, rows, registry=None):
        return validate_accounting_identities(rows, registry or self.registry())[
            self.KEY
        ]

    def test_every_fr2004_week_is_checked_against_its_own_eras_components(self):
        registry = self.registry()
        rows = self.extract_rows()
        weeks = {row.ref_date for row in rows}

        # -- the premise: the extract really does span the three eras --------
        # Without this the acceptance assertion below could pass over a fixture
        # that happened to carry only the current era, which is the shape of the
        # defect and not of its repair.
        self.assertEqual(len(weeks), 700)
        self.assertEqual(min(weeks), date(2013, 4, 3))
        self.assertEqual(
            len({row.ref_date for row in rows if row.series_id == self.RETIRED}),
            457,
        )

        # -- every week holds, and none is unchecked -------------------------
        evaluation = self.evaluate(rows, registry)
        self.assertEqual(evaluation.verdict, IDENTITY_HELD)
        self.assertEqual(evaluation.unevaluated, ())
        self.assertEqual(evaluation.violations, ())
        self.assertEqual(evaluation.evaluated_ref_dates, len(weeks))
        self.assertLess(evaluation.maximum_residual, 1e-6)

        # -- each era against exactly its own component set -------------------
        # The trap this kills is one identity over the union of all fifteen
        # terms with an absent term read as 0.0: it passes the block above on
        # every one of the 700 weeks and fails here, because a term withheld
        # from its own era's set must leave the identity with no residual to
        # compare rather than with a fabricated zero.
        for era_id, week, term in self.ERA_WEEKS:
            self.assertIn(week, weeks)
            withheld = [
                row for row in rows
                if not (row.ref_date == week and row.series_id == term)
            ]
            self.assertEqual(len(withheld), len(rows) - 1)
            planted = self.evaluate(withheld, registry)
            self.assertEqual(planted.verdict, IDENTITY_HELD_WHERE_EVALUABLE)
            self.assertEqual(len(planted.unevaluated), 1)
            record = planted.unevaluated[0]
            self.assertEqual(record.ref_date, week)
            self.assertEqual(record.absent_fields, (term,))
            self.assertEqual(record.era_id, era_id)
            self.assertFalse(record.undeclared_ref_date)
            self.assertEqual(planted.evaluated_ref_dates, len(weeks) - 1)

        # A term that belongs to another era is not this era's business. The
        # retired bucket is absent from every week from 2022-01-05 on and the
        # split pair is absent from every week before it; if either were being
        # looked for outside its own era, the 700-week verdict above could not
        # have been `held`.
        split = {"PDPOSGSC-G11L21", "PDPOSGSC-G21"}
        current = {
            row.ref_date for row in rows if row.series_id in split
        }
        retired = {row.ref_date for row in rows if row.series_id == self.RETIRED}
        self.assertEqual(current & retired, set())
        self.assertEqual(current | retired, weeks)

        # -- a date in no declared era is recorded, not skipped ---------------
        era_one = [
            era
            for era in self.identity(registry)["eras"]
            if era["id"] == "no_frn_combined_over_11"
        ][0]
        first_week = {
            row.series_id: row for row in rows if row.ref_date == date(2013, 4, 3)
        }
        before = list(rows) + [
            replace_observation(first_week[term], self.UNDECLARED_WEEK)
            for term in (*era_one["left"], *era_one["right"])
        ]
        undeclared = self.evaluate(before, registry)
        # Every term of the neighbouring era is present on that week, so a
        # verdict driven by the terms alone would have said `held`. It is the
        # window that refuses it.
        self.assertEqual(undeclared.verdict, IDENTITY_HELD_WHERE_EVALUABLE)
        self.assertEqual(undeclared.undeclared_ref_dates, (self.UNDECLARED_WEEK,))
        self.assertEqual(undeclared.evaluated_ref_dates, len(weeks))
        gap = undeclared.unevaluated[0]
        self.assertEqual(gap.ref_date, self.UNDECLARED_WEEK)
        self.assertTrue(gap.undeclared_ref_date)
        self.assertIsNone(gap.era_id)
        self.assertEqual(gap.absent_fields, ())
        self.assertIn("falls in no declared era", gap.as_dict()["reason"])

        # -- two overlapping windows are refused ------------------------------
        overlapped = self.registry()
        eras = self.identity(overlapped)["eras"]
        self.assertEqual(eras[1]["from"], "2015-01-07")
        eras[0]["through"] = "2015-01-07"
        with self.assertRaisesRegex(DataContractError, r"overlap"):
            self.evaluate(rows, overlapped)

        # -- an era whose `from` is after its `through` is refused ------------
        reversed_window = self.registry()
        era = self.identity(reversed_window)["eras"][1]
        era["from"], era["through"] = era["through"], era["from"]
        with self.assertRaisesRegex(
            DataContractError, r"covers no reference date"
        ):
            self.evaluate(rows, reversed_window)

        # -- the top-level terms must restate the most recent era -------------
        # `tests/test_contract.py` reads an identity's top-level `left` and
        # `right` as the shape both tracks build against, and it is human-owned,
        # so the declaration cannot simply move into the eras. Left unchecked
        # beside them it would be a second statement of the current component
        # set with nothing holding the two together -- the duplicated-fact
        # failure this repository keeps meeting, and the one an era'd identity
        # invites, because the copy that drifts is the one nothing evaluates.
        drifted = self.registry()
        identity = self.identity(drifted)
        self.assertEqual(identity["right"][-1], "PDPOSTIPS-G11")
        identity["right"] = identity["right"][:-1]
        with self.assertRaisesRegex(
            DataContractError, r"must restate its most recent era"
        ):
            self.evaluate(rows, drifted)


class TreasurySettlementZeroTests(unittest.TestCase):
    """A business day with no Treasury settlement reads 0.0, inside coverage only.

    Human decision, 11 September 2026 (`docs/DATA_QUALITY_DECISIONS.md`, "Panel
    columns (human, 11 Sep)"): the auction record lists every settlement, so a
    business day with none settled nothing, and `treasury_settlement_bills`,
    `_coupons`, `_soma` and the aggregate read `0.0` -- but only up to the
    snapshot's retrieval date, and a day the snapshot cannot speak to stays a
    hole. `data.build_daily_panel` rule 8; the declaration is
    `data.SETTLEMENT_ZERO_COLUMNS`. Before this block every such day was a
    hole: the adapter emits nothing for an absent leg, and still does.

    Three blocks, one criterion each, each its own mutation target:

    * A24's is `test_a_business_day_with_no_settlement_reads_zero_inside_the_snapshot_coverage_only`
      -- the rule and its retrieval bound;
    * A25's is `test_no_zero_is_written_where_the_settlement_would_not_be_observable_at_the_cutoff`
      -- the same rule bounded by `build_cutoff`. Its fixture and its record are
      the second half of this docstring.
    * A27's is `test_the_manifest_counts_the_zeros_rule_8_wrote_as_well_as_the_holes`
      -- the build records how many zeros the rule wrote. Third section below.

    The fixture is a fortnight of January 2026. SOFR prints on nine weekdays,
    so those are the grid; 10 and 11 January are inside coverage and off it.
    The snapshot's first settlement is 6 January. It was retrieved at
    03:00 UTC on 14 January, which is 13 January on the Eastern calendar
    Treasury's issue dates are written in, so 13 January is the last covered
    day and 14 January the first uncovered one. 7 and 13 January settle
    nothing; 8 January settles a coupon and no bill; 6 and 9 January a bill
    and no coupon, and 9 January's SOMA award is withheld (the adapter emits
    that day's public legs and no SOMA leg); 12 January settles both and a
    genuine SOMA zero.

    Mutation record, 11 September 2026, python3 3.9.6. Every mutation applied to
    `src/repo_model/data.py` in a disposable copy under `$HOME` built from
    `git ls-files -z --cached --others --exclude-standard`, confirmed applied
    (the replaced text occurs exactly once before and the file differs after),
    reverted and confirmed byte-identical before the next.
    `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`, `OMP_NUM_THREADS=1`, the whole
    suite each time. Unmutated control green before the first and after the
    last, no expected failure. Every mutation was killed by this test and by
    nothing else in the suite, each subtest failing with `AssertionError`:

    1. **The retrieval bound removed**: each snapshot's coverage runs to
       `date.max` (the retrieval timestamp still read, so the refusal stands).
       Killed "a grid date after the retrieval date is a hole" --
       `0.0 is not None : 2026-01-14 treasury_settlement`.
    2. **Every optional column zero-filled**: the fill writes `0.0` into any
       `OPTIONAL_NUMERIC_FIELDS` column on any date some declared column took a
       zero. Killed "a withheld SOMA leg is a hole" and "an undeclared optional
       column is still a hole on the same dates" (`0.0 is not None : 2026-01-06`).
    3. **The aggregate left a hole on zero days**: `treasury_settlement` taken
       out of `SETTLEMENT_ZERO_COLUMNS`. Killed "a covered grid date with
       neither" (`None != 0.0 : 2026-01-07 treasury_settlement`) and "the
       identity holds on every zero day" (`unexpectedly None : 2026-01-07`).
    4. **The withheld SOMA leg zero-filled**: the SOMA leg declared `leg`
       rather than `day`. Killed "a withheld SOMA leg is a hole" alone.
    5. **Each refusal removed.** (a) The missing-timestamp `raise` replaced by
       `return date.max`, an unbounded fill: killed the refusal subtest "a
       snapshot with no retrieval timestamp", `DataContractError not raised`.
       (b) The source check's condition replaced by `False`: killed "a declared
       column not drawn from the auction snapshot", `DataContractError not
       raised`.
    6. **The retrieval instant read on the UTC calendar** (`parsed.date()`),
       which puts 14 January inside coverage. Killed "a grid date after the
       retrieval date is a hole", `0.0 is not None : 2026-01-14
       treasury_settlement`.
    7. **A zero counted as a hole.** Killed "holes count the empty cells, not
       the zeros": `treasury_settlement_bills` 6 against 3.

    What rebuilding the real snapshots showed, for the record (no page carries
    it): only the four settlement columns moved, every other column's bytes
    unchanged, and the holes left in them are the two grid dates before the
    snapshot's first settlement. The retrieval bound does not bind on that
    snapshot -- its last settlement and the panel's last grid date coincide,
    days before its retrieval date -- and no SOMA result was withheld on a grid
    date, so on today's data mutations 1, 4 and 6 would move nothing. This
    test is what holds them.

    ---- A25: the zero is bounded by the build cutoff ----

    A24 left this open in its own words, and rule 8's docstring said the same:
    the rule "never writes a zero past the build cutoff only because `sofr` is
    published the next day. A build with no required column has no such
    guarantee." That guarantee is real and it is a coincidence. A settlement
    dated d publishes at 23:59 Eastern on d; SOFR for d does not publish until
    15:00 Eastern on the next business day, so any cutoff that admits d as a row
    under rule 6 has already admitted d's settlement record. Take `sofr` out of
    the declared columns and the grid end is held by whatever the caller did
    declare, which can publish hours earlier the same day -- and rule 8 then
    wrote 0.0 on a date whose settlement record nobody could read yet. Rule 1
    had removed that date's settlement row; the rule read its own filtering as
    evidence that nothing settled.

    **The fix** is the second condition of rule 8: a grid date takes a zero only
    if `datetime.combine(d + days, available_time, timezone) <= build_cutoff`,
    with `days`, `available_time` and `timezone` read from the auction source's
    declared `release_lag` -- rule 1's arithmetic applied to the date, because an
    absence carries no `available_at` of its own. `data._settlement_publication`.
    A basis other than `record_date` is refused, not reinterpreted.

    **No published figure moves, and it cannot.** Measured against
    `docs/runs/funding_panel.manifest.json` (build cutoff 2026-09-08T21:31:42Z,
    grid 2018-04-03 to 2026-09-03) on the tracked registry: the published end
    date's settlement publishes 2026-09-04T03:59Z, five days inside the cutoff,
    and on no grid date in that range does a settlement publish later than that
    day's SOFR. So on every build that declares `sofr` -- which is every
    published one -- the new bound is slack on every date. That is A24's
    coincidence, measured rather than assumed, and it is why this block needed a
    fixture that declares no `REQUIRED_FIELDS` column at all.

    **A25's fixture.** The same fortnight, with `tgcr` in place of `sofr` as the
    only non-settlement column, so rule 6 retains every date any visible row
    reports and nothing anchors the grid end. TGCR publishes at 10:00 Eastern on
    its own date. The cutoff is 14 January 12:00 Eastern: past TGCR for the 14th,
    short of 23:59 Eastern when the 14th's settlement record publishes. 14
    January settles 60 billion of bills, which rule 1 hides, so the unbounded
    rule wrote `0.0` there over a true 60.0 -- a false zero, not merely an early
    one, and the test asserts the 60.0 by rebuilding at a later cutoff. The
    snapshot is retrieved 19 January on the Eastern calendar, five days past the
    cutoff, so A24's retrieval bound cannot be what holds the 14th out. 7, 9 and
    13 January settle nothing and are inside both bounds, and keep reading 0.0.
    15 and 16 January never reach the grid: rule 1 drops their TGCR rows.

    Mutation record, 11 September 2026, python3 3.9.6. Every mutation applied to
    `src/repo_model/data.py` in a disposable copy under `$HOME` built from
    `git ls-files -z --cached --others --exclude-standard`, confirmed applied
    (the replaced text occurs exactly once before and the digest differs after),
    reverted and confirmed byte-identical before the next.
    `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`, `OMP_NUM_THREADS=1`, the whole
    suite each time. Unmutated control green before the first and after the
    last, no expected failure. Each mutation was killed by one test and one
    subtest and by nothing else in the suite, every failure an `AssertionError`:

    1. **The cutoff bound dropped**, restoring A24's behaviour: the `covered`
       comprehension keeps only the retrieval test. Killed A25's criterion, "a
       grid date whose settlement is not yet published is a hole" --
       `0.0 is not None : treasury_settlement`.
    2. **The basis refusal removed**: `_settlement_publication`'s guard condition
       replaced by `False`, so a `ref_date`/`business_days` lag is read as if the
       arithmetic spoke for it. Killed the refusal subtest "a lag the
       availability arithmetic cannot read", `DataContractError not raised`.
    3. **Bounded on the cutoff's calendar date** rather than on the declared
       publication instant (`ref_date <= build_cutoff.date()`) -- the plausible
       wrong implementation, and one that passes every other assertion here.
       Killed A25's criterion, `0.0 is not None : treasury_settlement`.

    Mutations 1 and 6 of A24's record above were **re-run** against the changed
    `covered` comprehension, per `CLAUDE.md`: a guard that goes quiet under a new
    rule is how a suite stays green over a blunted one. Both still bite, and both
    still kill A24's criterion alone and not A25's -- the retrieval bound
    removed (coverage to `date.max`) and the retrieval instant read on the UTC
    calendar (`parsed.date()`), each `0.0 is not None : 2026-01-14
    treasury_settlement`. The two bounds are independent, and the suite now
    shows it rather than asserting it.

    ---- A27: the build counts the zeros rule 8 wrote ----------------------

    A22 left it in its own words: the manifest counts holes but not zeros.
    `DailyPanelBuild.holes` counts, per built column, the `ref_date`s carrying
    no value, and a settlement zero is a value and is not among them. Those are
    two different facts about the same column's absences -- how much of it is
    missing, and how much of it is a zero written where an observation was
    absent -- and only one was recorded. A25 made it sharper rather than
    softer: since the zero is bounded by the build cutoff, the set of dates
    that get one is derived, and nothing recorded how large that set was on the
    build that ran. The count is the audit of that bound.

    `DailyPanelBuild.settlement_zeros` is that count, keyed over every built
    column exactly as `holes` is.

    **It counts at the write, not over the eligible dates**, which is the whole
    distinction and the reason it is not derived from
    `_settlement_zero_dates`'s return. Six grid dates of A24's fixture are
    eligible for a zero -- inside the snapshot's coverage, published by the
    cutoff -- and no column takes six: `treasury_settlement` settled on four of
    them. A count over the eligible set over-reports on exactly the columns
    that have the most data. Nor is it a scan of the panel for `0.0`: 12
    January's SOMA award is an observed zero and is not rule 8's.

    **A column that took none records zero rather than omitting the key**, to
    the standard `DailyPanelBuild.incomplete_dates` already states -- a reader
    tells "none were written" from "this build was never asked". That clause is
    a refusal and has its own mutation below.

    **The file manifest does not carry it yet, and that is a finding, not an
    omission.** `write_daily_panel`'s JSON is where a *reader of a published
    manifest* would meet the count, and A22's complaint is about that reader.
    Writing the key there turns `test_generated_results.MilestoneAReproduction
    Tests` red: `scripts/reproduce_milestone_a.py` compares the rebuilt
    `panel.build_manifest` with the one `docs/runs/persistence_funding.json`
    records key by key, and `_differences` reports a key on one side only.
    Measured as mutation 4 below, in the copy and in the mount. That test's own
    docstring says the answer to a published figure moving is "a report and a
    re-scored record, not a tolerance", and `CLAUDE.md` refuses a rewrite of a
    published record inside a block. So this block publishes the count to every
    reader of a build and leaves the file half to the human, and the last
    subtest asserts the state it left so the undone half stays visible.

    **No published number moves, and it is the key alone that goes red.**
    Rebuilt from the tracked inputs at the published cutoff and columns
    (2026-09-08T21:31:42Z, the eight of `metadata/funding_panel_manifest.json`),
    `settlement_zeros` is 0 on every one of them. The tracked funding inputs
    carry no auction snapshot -- `treasury_settlement` has 2104 holes over 2104
    rows -- so rule 8 fills nothing on that build and the new key would carry
    no figure the record disagrees with. The reproduction fails on the key's
    presence, not on a value.

    Mutation record, 12 September 2026, python3 3.9.6. Every mutation applied
    to `src/repo_model/data.py` in a disposable copy under `$HOME` built from
    `git ls-files -z --cached --others --exclude-standard`, confirmed applied
    (the replaced text occurs exactly once before), reverted from a kept
    original and confirmed byte-identical before the next.
    `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`, `OMP_NUM_THREADS=1`, the whole
    suite each time. Unmutated control green before the first and after the
    last, no expected failure.

    1. **The cheap count**: `settlement_zeros` taken from the eligible dates
       -- `_settlement_zero_dates` also returns `frozenset(covered)` and the
       count reads its length for every declared column -- rather than from the
       write. Killed by this test and nothing else, three subtests, every
       failure an `AssertionError`: "a filled column reports the count of its
       zeros" (`treasury_settlement` 6 against 2, and every declared column 6),
       "the count is of zeros written, not of dates eligible"
       (`6 not less than 6 : treasury_settlement`) and "holes and zeros are the
       two halves of the same grid" (`13 != 9`).
    2. **The count never made**: the increment at the write removed. Killed by
       this test and nothing else, the same three subtests, `AssertionError` --
       every count 0, `3 != 1` on the SOMA cross-check, `7 != 9` on the grid
       identity. The refusal subtest passes under it, which is why clause 3
       needs mutation 3 and not this one.
    3. **The key omitted where none was written**: the dict starts empty and
       the increment becomes `setdefault`-style, so a column that took no zero
       has no key. Killed by this test and nothing else: `AssertionError` on "a
       filled column reports the count of its zeros" (`sofr` and `tgcr` absent)
       and on "a build that wrote none records zero, not an absent key"
       (`{} != {'sofr': 0, 'tgcr': 0}`), and a **`KeyError: 'sofr'`** on the
       grid identity. The exception type is the point: an absent key is not a
       wrong number, it is a reader crashing.
    4. **The key written into the file manifest**: `"settlement_zeros"` added
       to `write_daily_panel`'s JSON. Killed by two tests, both
       `AssertionError`: this test's last subtest ("'settlement_zeros'
       unexpectedly found in ...") and
       `test_generated_results.MilestoneAReproductionTests` (`['panel.
       build_manifest.settlement_zeros: present on one side only']`). This is
       the measurement behind the finding above, not a defect being guarded
       against.

    A24's mutation 7 -- **a zero counted as a hole** -- was **re-run** against
    the changed row-assembly loop, per `CLAUDE.md`: the loop that counts the
    holes is the loop this block edited. It still bites, and it now kills three
    tests rather than one, all `AssertionError`: A24's "holes count the empty
    cells, not the zeros" (`treasury_settlement` 5 against 3), A25's same
    subtest (5 against 2) and this test's grid identity (`11 != 9`). The guard
    was strengthened by the new count, not blunted by it.
    """

    SOFR_SHA = "a" * 64
    AUCTION_SHA = "b" * 64
    RETRIEVED_AT = "2026-01-14T03:00:00+00:00"

    GRID = (
        date(2026, 1, 5),
        date(2026, 1, 6),
        date(2026, 1, 7),
        date(2026, 1, 8),
        date(2026, 1, 9),
        date(2026, 1, 12),
        date(2026, 1, 13),
        date(2026, 1, 14),
        date(2026, 1, 15),
    )

    #: The adapter's series, as `ingest._treasury_rows` names them, per
    #: settlement date. A leg not named has no observation that day.
    SETTLEMENTS = {
        date(2026, 1, 6): {
            "treasury_settlement": 50.0,
            "treasury_settlement_bill": 50.0,
            "treasury_settlement_soma": 2.0,
        },
        date(2026, 1, 8): {
            "treasury_settlement": 30.0,
            "treasury_settlement_coupon": 30.0,
            "treasury_settlement_soma": 1.0,
        },
        # Withheld: an auction not yet held, so no SOMA leg for the day.
        date(2026, 1, 9): {
            "treasury_settlement": 40.0,
            "treasury_settlement_bill": 40.0,
        },
        date(2026, 1, 12): {
            "treasury_settlement": 30.0,
            "treasury_settlement_bill": 20.0,
            "treasury_settlement_coupon": 10.0,
            "treasury_settlement_soma": 0.0,
        },
    }
    TGCR = {date(2026, 1, 5): 4.29, date(2026, 1, 8): 4.30, date(2026, 1, 12): 4.31}

    SETTLEMENT_COLUMNS = (
        "treasury_settlement",
        "treasury_settlement_bills",
        "treasury_settlement_coupons",
        "treasury_settlement_soma",
    )
    COLUMNS = ("sofr", "tgcr") + SETTLEMENT_COLUMNS

    LAG = {
        "basis": "ref_date",
        "unit": "business_days",
        "days": 1,
        "worst_case_calendar_days": 6,
        "available_time": "15:00",
        "timezone": "America/New_York",
        "note": "fixture",
    }

    def registry(self):
        """The auction source's lag as `metadata/sources.json` declares it."""

        real = json.loads(
            (Path(__file__).parents[1] / "metadata" / "sources.json").read_text(
                encoding="utf-8"
            )
        )
        return {
            "nyfed_sofr": {"release_lag": dict(self.LAG)},
            "nyfed_tgcr": {"release_lag": dict(self.LAG)},
            "treasury_auctions": {
                "release_lag": dict(real["treasury_auctions"]["release_lag"])
            },
        }

    def rows(self):
        new_york = ZoneInfo("America/New_York")
        rows = []
        for index, ref_date in enumerate(self.GRID):
            rows.append(
                PointInTimeObservation(
                    series_id="SOFR",
                    ref_date=ref_date,
                    available_at=datetime.combine(
                        ref_date + timedelta(days=1), time(19, 0), tzinfo=timezone.utc
                    ),
                    value=4.30 + index / 100,
                    vintage_id=f"SOFR-{ref_date.isoformat()}",
                    source_sha=self.SOFR_SHA,
                )
            )
        for ref_date, value in self.TGCR.items():
            rows.append(
                PointInTimeObservation(
                    series_id="TGCR",
                    ref_date=ref_date,
                    available_at=datetime.combine(
                        ref_date + timedelta(days=1), time(19, 0), tzinfo=timezone.utc
                    ),
                    value=value,
                    vintage_id=f"TGCR-{ref_date.isoformat()}",
                    source_sha=self.SOFR_SHA,
                )
            )
        for ref_date, legs in self.SETTLEMENTS.items():
            for series_id, value in legs.items():
                rows.append(
                    PointInTimeObservation(
                        series_id=series_id,
                        ref_date=ref_date,
                        available_at=datetime.combine(
                            ref_date, time(23, 59), tzinfo=new_york
                        ),
                        value=value,
                        vintage_id=f"{ref_date.isoformat()}:{self.RETRIEVED_AT}",
                        source_sha=self.AUCTION_SHA,
                    )
                )
        return rows

    def build(self, *, retrieved_at=None):
        return build_daily_panel(
            self.rows(),
            self.registry(),
            build_cutoff=datetime(2026, 2, 1, tzinfo=timezone.utc),
            decision_time=time.fromisoformat("16:00"),
            columns=self.COLUMNS,
            snapshot_retrieved_at=(
                {self.AUCTION_SHA: self.RETRIEVED_AT}
                if retrieved_at is None
                else retrieved_at
            ),
        )

    def test_a_business_day_with_no_settlement_reads_zero_inside_the_snapshot_coverage_only(
        self,
    ):
        """The acceptance criterion and the mutation target. See the class docstring."""

        build = self.build()
        self.assertEqual(build.built_columns, self.COLUMNS)
        panel = {row.date: row.values for row in build.observations}

        with self.subTest("a covered grid date with no bill auction"):
            coupon_only = panel[date(2026, 1, 8)]
            self.assertEqual(coupon_only["treasury_settlement_bills"], 0.0)
            self.assertEqual(coupon_only["treasury_settlement_coupons"], 30.0)
            self.assertEqual(
                coupon_only["treasury_settlement"],
                coupon_only["treasury_settlement_coupons"],
            )

        with self.subTest("a covered grid date with neither: every leg and the aggregate"):
            for day in (date(2026, 1, 7), date(2026, 1, 13)):
                for column in self.SETTLEMENT_COLUMNS:
                    self.assertEqual(panel[day][column], 0.0, f"{day} {column}")

        # Every date on which rule 8 wrote a zero into some column, stated
        # rather than derived, so a mutation that stops writing one cannot
        # empty the set the identity is checked over.
        zero_days = (
            date(2026, 1, 6),
            date(2026, 1, 7),
            date(2026, 1, 8),
            date(2026, 1, 9),
            date(2026, 1, 13),
        )
        with self.subTest("the identity holds on every zero day"):
            for day in zero_days:
                values = panel[day]
                parts = (
                    values["treasury_settlement_bills"],
                    values["treasury_settlement_coupons"],
                )
                self.assertIsNotNone(values["treasury_settlement"], day)
                self.assertNotIn(None, parts, day)
                self.assertAlmostEqual(
                    values["treasury_settlement"], sum(parts), delta=1e-9, msg=day
                )

        with self.subTest("a grid date after the retrieval date is a hole"):
            # 14 January is the retrieval instant's UTC date and not its
            # Eastern one; 15 January is past both.
            for day in (date(2026, 1, 14), date(2026, 1, 15)):
                for column in self.SETTLEMENT_COLUMNS:
                    self.assertIsNone(panel[day][column], f"{day} {column}")

        with self.subTest("a grid date before the snapshot's first settlement is a hole"):
            for column in self.SETTLEMENT_COLUMNS:
                self.assertIsNone(panel[date(2026, 1, 5)][column], column)

        with self.subTest("a withheld SOMA leg is a hole"):
            withheld = panel[date(2026, 1, 9)]
            self.assertEqual(withheld["treasury_settlement"], 40.0)
            self.assertIsNone(withheld["treasury_settlement_soma"])
            # ...and a genuine zero award is the observation, not the fill.
            self.assertEqual(panel[date(2026, 1, 12)]["treasury_settlement_soma"], 0.0)

        with self.subTest("an undeclared optional column is still a hole on the same dates"):
            for day in zero_days:
                if day not in self.TGCR:
                    self.assertIsNone(panel[day]["tgcr"], day)

        with self.subTest("no row for a date off the grid"):
            self.assertEqual(tuple(panel), self.GRID)
            self.assertNotIn(date(2026, 1, 10), panel)
            self.assertNotIn(date(2026, 1, 11), panel)

        with self.subTest("holes count the empty cells, not the zeros"):
            self.assertEqual(
                dict(build.holes),
                {
                    column: sum(1 for values in panel.values() if values[column] is None)
                    for column in self.COLUMNS
                },
            )

        with self.subTest(refusal="a snapshot with no retrieval timestamp"):
            for retrieved_at in (
                {},
                {self.AUCTION_SHA: ""},
                {self.AUCTION_SHA: "2026-01-14T03:00:00"},
            ):
                with self.assertRaisesRegex(
                    DataContractError, r"no usable retrieval timestamp"
                ):
                    self.build(retrieved_at=retrieved_at)

        with self.subTest(refusal="a declared column not drawn from the auction snapshot"):
            from repo_model import data

            declared = dict(data.SETTLEMENT_ZERO_COLUMNS)
            declared["tgcr"] = data.SETTLEMENT_ZERO_LEG
            with unittest.mock.patch.object(
                data, "SETTLEMENT_ZERO_COLUMNS", MappingProxyType(declared)
            ):
                with self.assertRaisesRegex(
                    DataContractError, r"not the auction snapshot"
                ):
                    self.build()

    # ---- A25: the zero is bounded by the build cutoff ----------------------
    #
    # The fixture above cannot show the defect, and that is the point: it
    # declares `sofr`, so rule 6 holds the grid end to a SOFR date, and a SOFR
    # date readable at the cutoff carries a settlement that was readable
    # earlier. The bound only has anything to do where no required column
    # anchors the grid, so this fixture declares none.
    #
    #: The grid end is held by `tgcr` alone, readable at 10:00 Eastern on its
    #: own date. A settlement dated the same day is not readable until 23:59
    #: Eastern, as the registry declares and the adapter writes. A cutoff
    #: between the two is a cutoff at which that day's settlement record has
    #: not been published.
    UNANCHORED_COLUMNS = ("tgcr",) + SETTLEMENT_COLUMNS
    UNANCHORED_CUTOFF = datetime(
        2026, 1, 14, 12, 0, tzinfo=ZoneInfo("America/New_York")
    )
    #: Retrieved 19 January on the Eastern calendar -- five days past the
    #: cutoff, so the retrieval bound of the criterion above cannot be what
    #: holds 14 January out. Only the cutoff can.
    UNANCHORED_RETRIEVED_AT = "2026-01-20T03:00:00+00:00"
    #: Every weekday of the fortnight. 15 and 16 January fall out on their own
    #: availability under rule 1 and are never grid dates.
    UNANCHORED_TGCR_DATES = (
        date(2026, 1, 5),
        date(2026, 1, 6),
        date(2026, 1, 7),
        date(2026, 1, 8),
        date(2026, 1, 9),
        date(2026, 1, 12),
        date(2026, 1, 13),
        date(2026, 1, 14),
        date(2026, 1, 15),
        date(2026, 1, 16),
    )
    UNANCHORED_GRID = UNANCHORED_TGCR_DATES[:-2]
    #: 14 January settles 60 billion of bills. Rule 1 hides it -- it is not
    #: published until 23:59 Eastern that day -- which is exactly why the
    #: unbounded rule reads 0.0 there: a value from the future wearing a zero,
    #: and in this fixture a demonstrably false one.
    UNANCHORED_SETTLEMENTS = {
        date(2026, 1, 6): {
            "treasury_settlement": 50.0,
            "treasury_settlement_bill": 50.0,
            "treasury_settlement_soma": 2.0,
        },
        date(2026, 1, 8): {
            "treasury_settlement": 30.0,
            "treasury_settlement_coupon": 30.0,
            "treasury_settlement_soma": 0.0,
        },
        date(2026, 1, 12): {
            "treasury_settlement": 30.0,
            "treasury_settlement_bill": 20.0,
            "treasury_settlement_coupon": 10.0,
            "treasury_settlement_soma": 1.0,
        },
        date(2026, 1, 14): {
            "treasury_settlement": 60.0,
            "treasury_settlement_bill": 60.0,
            "treasury_settlement_soma": 3.0,
        },
    }
    #: The covered grid dates on which nothing settled at all. Stated rather
    #: than derived, for the reason the criterion above states it: a mutation
    #: that stops writing a zero must not be able to empty the set.
    UNANCHORED_ZERO_DAYS = (date(2026, 1, 7), date(2026, 1, 9), date(2026, 1, 13))

    def unanchored_rows(self):
        new_york = ZoneInfo("America/New_York")
        rows = []
        for index, ref_date in enumerate(self.UNANCHORED_TGCR_DATES):
            rows.append(
                PointInTimeObservation(
                    series_id="TGCR",
                    ref_date=ref_date,
                    available_at=datetime.combine(
                        ref_date, time(10, 0), tzinfo=new_york
                    ),
                    value=4.29 + index / 100,
                    vintage_id=f"TGCR-{ref_date.isoformat()}",
                    source_sha=self.SOFR_SHA,
                )
            )
        for ref_date, legs in self.UNANCHORED_SETTLEMENTS.items():
            for series_id, value in legs.items():
                rows.append(
                    PointInTimeObservation(
                        series_id=series_id,
                        ref_date=ref_date,
                        available_at=datetime.combine(
                            ref_date, time(23, 59), tzinfo=new_york
                        ),
                        value=value,
                        vintage_id=f"{ref_date.isoformat()}:{self.UNANCHORED_RETRIEVED_AT}",
                        source_sha=self.AUCTION_SHA,
                    )
                )
        return rows

    def build_unanchored(self, *, build_cutoff=None, registry=None):
        return build_daily_panel(
            self.unanchored_rows(),
            self.registry() if registry is None else registry,
            build_cutoff=self.UNANCHORED_CUTOFF if build_cutoff is None else build_cutoff,
            decision_time=time.fromisoformat("16:00"),
            columns=self.UNANCHORED_COLUMNS,
            snapshot_retrieved_at={self.AUCTION_SHA: self.UNANCHORED_RETRIEVED_AT},
        )

    def test_no_zero_is_written_where_the_settlement_would_not_be_observable_at_the_cutoff(
        self,
    ):
        """A25's acceptance criterion and mutation target. See the class docstring."""

        from repo_model import data

        build = self.build_unanchored()
        self.assertEqual(build.built_columns, self.UNANCHORED_COLUMNS)
        panel = {row.date: row.values for row in build.observations}

        with self.subTest("the premise: no required column anchors the grid end"):
            # Without this the bound is unreachable and the test proves nothing.
            self.assertEqual(
                [
                    column
                    for column in build.built_columns
                    if column in data.REQUIRED_FIELDS
                ],
                [],
            )
            self.assertEqual(tuple(panel), self.UNANCHORED_GRID)

        with self.subTest("a grid date whose settlement is not yet published is a hole"):
            unpublished = panel[date(2026, 1, 14)]
            # On the grid, and readable: `tgcr` is what put the date there.
            self.assertIsNotNone(unpublished["tgcr"])
            for column in self.SETTLEMENT_COLUMNS:
                self.assertIsNone(unpublished[column], column)

        with self.subTest("the zero it would have written is false, not merely early"):
            # The same fixture at a cutoff past 14 January's 23:59 Eastern
            # publication. The day settled 60 billion of bills.
            later = {
                row.date: row.values
                for row in self.build_unanchored(
                    build_cutoff=datetime(
                        2026, 1, 15, 12, 0, tzinfo=ZoneInfo("America/New_York")
                    )
                ).observations
            }
            self.assertEqual(later[date(2026, 1, 14)]["treasury_settlement_bills"], 60.0)
            self.assertEqual(later[date(2026, 1, 14)]["treasury_settlement"], 60.0)
            self.assertEqual(later[date(2026, 1, 14)]["treasury_settlement_soma"], 3.0)
            self.assertEqual(later[date(2026, 1, 14)]["treasury_settlement_coupons"], 0.0)

        with self.subTest("a date observable at the cutoff still reads 0.0"):
            for day in self.UNANCHORED_ZERO_DAYS:
                for column in self.SETTLEMENT_COLUMNS:
                    self.assertEqual(panel[day][column], 0.0, f"{day} {column}")
            # ...including a leg zero beside a settled leg, on both sides.
            self.assertEqual(panel[date(2026, 1, 6)]["treasury_settlement_coupons"], 0.0)
            self.assertEqual(panel[date(2026, 1, 6)]["treasury_settlement_bills"], 50.0)
            self.assertEqual(panel[date(2026, 1, 8)]["treasury_settlement_bills"], 0.0)
            self.assertEqual(panel[date(2026, 1, 8)]["treasury_settlement_coupons"], 30.0)
            # ...and an observed zero award is still the observation.
            self.assertEqual(panel[date(2026, 1, 8)]["treasury_settlement_soma"], 0.0)

        with self.subTest("the identity holds on every zero day"):
            for day in self.UNANCHORED_ZERO_DAYS + (date(2026, 1, 6), date(2026, 1, 8)):
                values = panel[day]
                parts = (
                    values["treasury_settlement_bills"],
                    values["treasury_settlement_coupons"],
                )
                self.assertIsNotNone(values["treasury_settlement"], day)
                self.assertNotIn(None, parts, day)
                self.assertAlmostEqual(
                    values["treasury_settlement"], sum(parts), delta=1e-9, msg=day
                )

        with self.subTest("the other bound is untouched: before the first settlement"):
            for column in self.SETTLEMENT_COLUMNS:
                self.assertIsNone(panel[date(2026, 1, 5)][column], column)

        with self.subTest("holes count the empty cells, not the zeros"):
            self.assertEqual(
                dict(build.holes),
                {
                    column: sum(1 for values in panel.values() if values[column] is None)
                    for column in self.UNANCHORED_COLUMNS
                },
            )

        with self.subTest(refusal="a naive build cutoff"):
            # The bound compares a declared availability instant with the
            # cutoff, so an offsetless cutoff is not a comparison this rule can
            # make. It is refused before rule 8 is reached, and this asserts it
            # stays refused there.
            with self.assertRaisesRegex(
                DataContractError, r"build_cutoff must include a UTC offset"
            ):
                self.build_unanchored(build_cutoff=datetime(2026, 1, 14, 12, 0))

        with self.subTest(refusal="a declared column not drawn from the auction snapshot"):
            declared = dict(data.SETTLEMENT_ZERO_COLUMNS)
            declared["tgcr"] = data.SETTLEMENT_ZERO_LEG
            with unittest.mock.patch.object(
                data, "SETTLEMENT_ZERO_COLUMNS", MappingProxyType(declared)
            ):
                with self.assertRaisesRegex(
                    DataContractError, r"not the auction snapshot"
                ):
                    self.build_unanchored()

        with self.subTest(refusal="a lag the availability arithmetic cannot read"):
            # A zero needs a declared instant to be bounded against. A basis
            # this arithmetic does not speak for is refused rather than assumed
            # away -- the same reason a snapshot with no retrieval timestamp is
            # refused rather than filled to `date.max`. A `ref_date` basis is
            # the case that gets here: `business_days` needs the holiday
            # calendar this repository does not have. A `snapshot_retrieved_at`
            # basis never reaches rule 8 at all, because rule 3 refuses the
            # column first, so it is not asserted here.
            registry = self.registry()
            registry["treasury_auctions"] = {"release_lag": dict(self.LAG)}
            with self.assertRaisesRegex(
                DataContractError, r"when a settlement dated that day is published"
            ):
                self.build_unanchored(registry=registry)

    # ---- A27: the manifest counts the written zeros ------------------------
    #
    #: The zeros rule 8 writes into A24's fixture, per column, stated rather
    #: than derived -- the reason the two criteria above state their zero days:
    #: a count derived from the panel a mutation just changed agrees with the
    #: mutation. Read off the fixture: the covered grid dates are 6, 7, 8, 9,
    #: 12 and 13 January (inside the snapshot's coverage, all published by the
    #: 1 February cutoff), less the dates each column's own series settled on --
    #: and, for the SOMA leg, less every date any leg settled on.
    #:
    #: Six dates are eligible and no column takes six, which is the whole
    #: distinction: `treasury_settlement` settled on four of them. A count over
    #: the eligible dates would report 6 for all four columns.
    ZEROS_WRITTEN = {
        "sofr": 0,
        "tgcr": 0,
        "treasury_settlement": 2,  # 7, 13
        "treasury_settlement_bills": 3,  # 7, 8, 13
        "treasury_settlement_coupons": 4,  # 6, 7, 9, 13
        "treasury_settlement_soma": 2,  # 7, 13 -- 12 January's 0.0 is observed
    }
    #: The grid dates rule 8's two bounds make eligible for a zero, which is
    #: what the cheap implementation counts.
    ZERO_ELIGIBLE_DATES = 6

    def test_the_manifest_counts_the_zeros_rule_8_wrote_as_well_as_the_holes(self):
        """A27's acceptance criterion and mutation target. See the class docstring."""

        build = self.build()
        panel = {row.date: row.values for row in build.observations}

        with self.subTest("a filled column reports the count of its zeros"):
            self.assertEqual(dict(build.settlement_zeros), self.ZEROS_WRITTEN)

        with self.subTest("the count is of zeros written, not of dates eligible"):
            # The eligible set is the same for all four settlement columns and
            # no column's count is it. A count over `covered` over-reports on
            # exactly the columns that have the most data, because a date
            # carrying a real settlement is eligible and is not a zero.
            for column in self.SETTLEMENT_COLUMNS:
                self.assertLess(
                    build.settlement_zeros[column], self.ZERO_ELIGIBLE_DATES, column
                )
            # ...and it is not a scan of the panel for 0.0 either: 12 January's
            # SOMA award is an observed zero and is not rule 8's.
            self.assertEqual(panel[date(2026, 1, 12)]["treasury_settlement_soma"], 0.0)
            self.assertEqual(
                sum(
                    1
                    for values in panel.values()
                    if values["treasury_settlement_soma"] == 0.0
                ),
                build.settlement_zeros["treasury_settlement_soma"] + 1,
            )

        with self.subTest("holes and zeros are the two halves of the same grid"):
            # Every cell of a built column is an observation, a rule 8 zero or
            # a hole, and the manifest now publishes the last two rather than
            # one of them. The observation counts are read off the fixture for
            # the reason the zeros are.
            observed = {
                "sofr": 9,
                "tgcr": 3,
                "treasury_settlement": 4,
                "treasury_settlement_bills": 3,
                "treasury_settlement_coupons": 2,
                "treasury_settlement_soma": 3,
            }
            self.assertEqual(len(panel), len(self.GRID))
            for column in self.COLUMNS:
                self.assertEqual(
                    build.holes[column]
                    + build.settlement_zeros[column]
                    + observed[column],
                    len(panel),
                    column,
                )

        with self.subTest("a build that wrote none records zero, not an absent key"):
            # No settlement column is declared, so rule 8 fills nothing. The
            # key is present for every built column and reads 0 -- the standard
            # `incomplete_dates` is held to, and the difference between "none
            # were written" and "this build was never asked".
            none_written = build_daily_panel(
                self.rows(),
                self.registry(),
                build_cutoff=datetime(2026, 2, 1, tzinfo=timezone.utc),
                decision_time=time.fromisoformat("16:00"),
                columns=("sofr", "tgcr"),
                snapshot_retrieved_at={self.AUCTION_SHA: self.RETRIEVED_AT},
            )
            self.assertEqual(none_written.built_columns, ("sofr", "tgcr"))
            self.assertEqual(dict(none_written.settlement_zeros), {"sofr": 0, "tgcr": 0})
            # ...and the keys are the built columns on both builds, as `holes`'
            # are, so neither count is silently narrower than the other.
            for candidate in (build, none_written):
                self.assertEqual(
                    sorted(candidate.settlement_zeros), sorted(candidate.built_columns)
                )
                self.assertEqual(
                    sorted(candidate.settlement_zeros), sorted(candidate.holes)
                )

        with self.subTest("the file manifest does not carry it, and that is measured"):
            # Not an endorsement: the record of a measurement. Writing the key
            # into `write_daily_panel`'s JSON turns the Milestone A
            # reproduction red, because the published record's
            # `panel.build_manifest` has no such key. See the class docstring.
            # This asserts the state the block leaves, so the day the human
            # re-publishes the record, this line is what says the other half is
            # still undone.
            with tempfile.TemporaryDirectory() as directory:
                manifest_path = write_daily_panel(build, Path(directory) / "panel.csv")
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["holes"], dict(build.holes))
            self.assertNotIn("settlement_zeros", manifest)


class BillRatePanelTests(unittest.TestCase):
    """The bill-rate panel columns: the coupon-equivalent quote, read a day late.

    Human decision, 11 September 2026 (`docs/DATA_QUALITY_DECISIONS.md`,
    "Bill-rate panel columns"): `tbill_4w` and `tbill_13w` are the
    coupon-equivalent yields in percent as Treasury publishes them. Treasury
    takes the quotations at about 3:30 PM; availability is declared at end of
    day on the quote date, so a 16:00 decision reads the previous business
    day's rate. The columns were declared (`contract.FEATURE_FIELDS`) and priced
    (`metadata/sources.json`) before this class, and no panel-build test said
    any of it. This is a test block: the behaviour held on the tree it was
    written against, and nothing under `src/` or `metadata/` changed with it.

    The acceptance criterion and the mutation target are the one test,
    `test_a_16_00_decision_reads_the_previous_business_days_coupon_equivalent_quote`.

    The fixture is a fortnight of January 2026 in Treasury's own CSV layout,
    read by `ingest._treasury_bill_rate_rows` against the tracked registry, so
    `available_at` comes from the registry's `release_lag` and not from this
    file. The two bases differ on every row. SOFR prints on every weekday, so
    those are the grid; Wednesday 14 January has no bill-rate line at all.

    **Left out, and why.** The brief asked for one more subtest: a Monday
    decision reads Friday's quote, "shown through the function that turns a
    decision date and a purge into the latest readable row", and to leave it
    out if the repository has none. It has none. The two candidates both take
    the date the scored window *opens*, not the decision date:
    `splits.clears_purge(row_date, opens, purge)` is a predicate, and
    `baseline._feature_index(dates, train_indices, scored_index, purge)` returns
    the last row with `row_date + purge < dates[scored_index]`. Writing the
    mapping from a decision date to a scored day here would be writing the
    function, which the brief forbids.

    A finding for Track B and the human, not closed here. The README's target
    (`README.md`, "Key findings") is the next business day's `spread_bps`,
    forecast from what is available at 16:00 on the previous business day. At
    the one-day purge these columns price, `_feature_index` for a Monday scored
    day (decided Friday at 16:00) returns Friday's row, whose quote this
    registry declares available at 23:59 that Friday; for a Wednesday scored day
    (decided Tuesday) it returns Monday's, as the decision says. The gap is
    counted to the scored day, so a weekend between decision and scored day
    counts toward it. The published runs report a six-day purge, and this
    block did not check whether any run binds on it.

    Treasury's actual publication time for these rates has not been read from
    Treasury by anyone on this project; the registry note says so, and this
    test pins the declaration as it stands, not the world.

    Mutation record, 11 September 2026, python3 3.9.6. Every mutation applied in
    a disposable copy under `$HOME` built from
    `git ls-files -z --cached --others --exclude-standard`, confirmed applied
    (the replaced text occurs exactly once before and the file differs after),
    reverted and confirmed byte-identical before the next.
    `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`, `OMP_NUM_THREADS=1`, the whole
    suite each time. Unmutated control green before the first and after the
    last, no expected failure. Every mutation was killed by this test:

    1. **`contract.py` maps `tbill_4w` to `tbill_4w_bank_discount`.** Killed
       "each carries its ref date's coupon-equivalent quote", `AssertionError:
       3.61 != 3.68 : 2026-01-05 tbill_4w`, and nothing else in the suite: no
       other test pins which basis the column reads.
    2. **The tracked registry's `treasury_bill_rates` `available_time` moved to
       15:30.** The purge prices to zero and `max_release_lag_days` refuses it,
       so both columns are refused. Killed "both columns are built"
       (`AssertionError`, `('sofr',)` against all three), "the purge priced at
       16:00 is one day" (`RegistryContractError: selected sources must produce
       a nonzero purge`), and the basis and hole subtests as `KeyError:
       'tbill_4w'` -- incidental, the column is absent. Also killed
       `test_ingest.TreasuryBillRateTests`'s row digests (`AssertionError`),
       because the adapter's `available_at` moved with the registry.
    3. **`tbill_4w` added to `data.SETTLEMENT_ZERO_COLUMNS`.** It never reaches
       a 0.0: `_settlement_zero_dates` refuses a declared column not drawn from
       the auction snapshot, on every build. Killed "neither column is declared
       to read 0.0" (`AssertionError`) and this test's build
       (`DataContractError`), and every other panel build in the suite the same
       way, `DataContractError` or a CLI build exiting 2.
       **3b, so the "never 0.0" assertion is exercised too:** the build's hole
       branch writes `0.0` into `tbill_4w`, uncounted. Killed "a business day
       with no quote is a hole", `AssertionError: 0.0 is not None : tbill_4w`,
       and nothing else in the suite.
    4. **A forward fill**: the build's hole branch writes the previous row's
       value when it has one. Killed "a business day with no quote is a hole",
       `AssertionError: 3.74 is not None : tbill_4w`; also the rule-4 tests in
       `DailyPanelJoinTests`, `TreasurySettlementZeroTests`, the requested
       columns digest and the Milestone A reproduction, all `AssertionError`.
    """

    REGISTRY_PATH = Path(__file__).parents[1] / "metadata" / "sources.json"
    SOFR_SHA = "a" * 64
    RETRIEVED_AT = "2026-01-20T14:00:00+00:00"
    DECISION_TIME = time(16, 0)
    NEW_YORK = ZoneInfo("America/New_York")

    GRID = (
        date(2026, 1, 5),
        date(2026, 1, 6),
        date(2026, 1, 7),
        date(2026, 1, 8),
        date(2026, 1, 9),
        date(2026, 1, 12),
        date(2026, 1, 13),
        date(2026, 1, 14),
        date(2026, 1, 15),
        date(2026, 1, 16),
    )
    HOLE = date(2026, 1, 14)

    HEADER = (
        "Date",
        "4 WEEKS BANK DISCOUNT",
        "4 WEEKS COUPON EQUIVALENT",
        "13 WEEKS BANK DISCOUNT",
        "13 WEEKS COUPON EQUIVALENT",
    )
    #: One line per quote date, cells in `HEADER` order. No line for `HOLE`.
    QUOTES = {
        date(2026, 1, 5): ("3.61", "3.68", "3.55", "3.63"),
        date(2026, 1, 6): ("3.62", "3.69", "3.56", "3.64"),
        date(2026, 1, 7): ("3.63", "3.70", "3.57", "3.65"),
        date(2026, 1, 8): ("3.64", "3.71", "3.58", "3.66"),
        date(2026, 1, 9): ("3.65", "3.72", "3.59", "3.67"),
        date(2026, 1, 12): ("3.66", "3.73", "3.60", "3.68"),
        date(2026, 1, 13): ("3.67", "3.74", "3.61", "3.69"),
        date(2026, 1, 15): ("3.69", "3.76", "3.63", "3.71"),
        date(2026, 1, 16): ("3.70", "3.77", "3.64", "3.72"),
    }

    BILL_COLUMNS = ("tbill_4w", "tbill_13w")
    COLUMNS = ("sofr",) + BILL_COLUMNS

    #: Panel column -> (the header it must carry, the header it must not),
    #: written out rather than read from `contract.FEATURE_FIELDS`, which is
    #: the mapping under test.
    BASIS = {
        "tbill_4w": ("4 WEEKS COUPON EQUIVALENT", "4 WEEKS BANK DISCOUNT"),
        "tbill_13w": ("13 WEEKS COUPON EQUIVALENT", "13 WEEKS BANK DISCOUNT"),
    }

    def registry(self):
        from repo_model.ingest import load_source_registry

        return load_source_registry(self.REGISTRY_PATH)

    def payload(self):
        """The export as Treasury lays it out: quoted header, newest date first."""

        lines = [
            ",".join(
                name if name == "Date" else f'"{name}"' for name in self.HEADER
            )
        ]
        for day in sorted(self.QUOTES, reverse=True):
            lines.append(",".join((day.strftime("%m/%d/%Y"),) + self.QUOTES[day]))
        return ("\n".join(lines) + "\n").encode("utf-8")

    def rows(self, registry):
        from repo_model.ingest import SnapshotArtifact, _treasury_bill_rate_rows

        payload = self.payload()
        artifact = SnapshotArtifact(
            source_id="treasury_bill_rates",
            path=Path("daily_treasury_bill_rates_2026.csv"),
            retrieved_at=self.RETRIEVED_AT,
            sha256=hashlib.sha256(payload).hexdigest(),
            url=str(registry["treasury_bill_rates"]["url"]),
            byte_count=len(payload),
        )
        rows = list(_treasury_bill_rate_rows(artifact, payload, registry))
        for index, ref_date in enumerate(self.GRID):
            published = ref_date + timedelta(days=3 if ref_date.weekday() == 4 else 1)
            rows.append(
                PointInTimeObservation(
                    series_id="SOFR",
                    ref_date=ref_date,
                    available_at=datetime.combine(
                        published, time(15, 0), tzinfo=self.NEW_YORK
                    ),
                    value=3.64 + index / 100,
                    vintage_id=f"SOFR-{ref_date.isoformat()}",
                    source_sha=self.SOFR_SHA,
                )
            )
        return rows

    def build(self, registry, *, build_cutoff, columns):
        return build_daily_panel(
            self.rows(registry),
            registry,
            build_cutoff=build_cutoff,
            decision_time=self.DECISION_TIME,
            columns=columns,
        )

    def test_a_16_00_decision_reads_the_previous_business_days_coupon_equivalent_quote(
        self,
    ):
        """The acceptance criterion and the mutation target. See the class docstring."""

        from repo_model import data
        from repo_model.contract import field_sources_for_features
        from repo_model.registry import max_release_lag_days

        registry = self.registry()

        # The fixture's own premise, so the basis subtest cannot pass on a row
        # where the two quotes happen to agree.
        for day, quote in self.QUOTES.items():
            cells = dict(zip(self.HEADER[1:], quote))
            for coupon_equivalent, bank_discount in self.BASIS.values():
                self.assertNotEqual(cells[coupon_equivalent], cells[bank_discount], day)

        with self.subTest("neither column is declared to read 0.0 on a day with no quote"):
            for column in self.BILL_COLUMNS:
                self.assertNotIn(column, data.SETTLEMENT_ZERO_COLUMNS)

        build = self.build(
            registry,
            build_cutoff=datetime(2026, 2, 1, tzinfo=timezone.utc),
            columns=self.COLUMNS,
        )
        panel = {row.date: row.values for row in build.observations}

        with self.subTest("both columns are built, not refused, at 16:00"):
            self.assertEqual(build.built_columns, self.COLUMNS)
            for column in self.BILL_COLUMNS:
                self.assertNotIn(column, build.refusals)
            self.assertEqual(tuple(panel), self.GRID)

        with self.subTest(
            "each carries its ref date's coupon-equivalent quote, never the bank-discount one"
        ):
            for day, quote in self.QUOTES.items():
                cells = dict(zip(self.HEADER[1:], quote))
                for column, (coupon_equivalent, bank_discount) in self.BASIS.items():
                    self.assertEqual(
                        panel[day][column], float(cells[coupon_equivalent]), f"{day} {column}"
                    )
                    self.assertNotEqual(
                        panel[day][column], float(cells[bank_discount]), f"{day} {column}"
                    )

        with self.subTest(
            "the purge priced at 16:00 is one day, so a decision on D reads D-1's quote"
        ):
            decision_day = date(2026, 1, 8)
            # The day's own quote exists; what is under test is that it is not
            # yet available at the decision.
            self.assertIn(decision_day, self.QUOTES)
            for column in self.BILL_COLUMNS:
                # The call `data._priceable_columns` makes for the column.
                purge = max_release_lag_days(
                    registry,
                    field_sources_for_features([column]),
                    decision_time=self.DECISION_TIME,
                )
                self.assertEqual(purge, 1, column)
                at_decision = self.build(
                    registry,
                    build_cutoff=datetime.combine(
                        decision_day, self.DECISION_TIME, tzinfo=self.NEW_YORK
                    ),
                    columns=(column,),
                )
                latest = at_decision.observations[-1]
                self.assertEqual(latest.date, decision_day - timedelta(days=purge), column)
                self.assertEqual(latest.date, date(2026, 1, 7), column)
                self.assertEqual(
                    latest.values[column], panel[date(2026, 1, 7)][column], column
                )

        with self.subTest("a business day with no quote is a hole, never filled and never 0.0"):
            for column in self.BILL_COLUMNS:
                self.assertIsNone(panel[self.HOLE][column], column)
                self.assertEqual(build.holes[column], 1, column)
            self.assertIsNotNone(panel[self.HOLE]["sofr"])
            self.assertEqual(build.holes["sofr"], 0)


class EmptyColumnTests(unittest.TestCase):
    """A built column that is a hole on every row is built *and empty*, and says so.

    A28. Measured on the merged tree of 12 September 2026, from
    `docs/runs/funding_panel.manifest.json`: over 2104 rows, `bgcr`, `tgcr` and
    `treasury_settlement` each have 2104 holes. Three of the eight built columns
    contain no data at all. The manifest already said so, in `holes` -- but only
    to a reader who compares each count against `row_count`, and
    `built_columns` lists those three beside `sofr` with nothing to separate
    them.

    That distinction is about to matter. The exceedance work needs a settlement
    or calendar proxy in the tail and `treasury_settlement` is the column
    anyone reaches for first; a feature declared on an all-hole column is a
    column of fitted imputations, not data. `DailyPanelBuild.empty_columns` is
    the build stating the difference.

    The acceptance criterion and the mutation target is
    `test_a_column_that_is_a_hole_on_every_row_is_named_empty_and_refused_as_a_feature`.

    **The refusal half is not in this block, and the test name still carries
    it.** The brief's last subtest was "declaring an empty column as a feature
    to the build is refused", conditional on the feature declaration being
    reachable from `data.py` on this tree. It is not. `data.py`'s only contact
    with the word is rule 3, which resolves a *declared panel column* through
    `contract.field_sources_for_features` -- and refusing there would refuse
    the published funding build, whose declared columns include all three empty
    ones, and would contradict this block's own rule that an empty column stays
    in `built_columns`. A feature *set* is declared to the model layer, not to
    the build: `grep -rn "features=" src/repo_model/*.py` is
    `baseline.py:6151`, `event_eval.py:623` and `cli_eval.py` three times, all
    of them Track B's and all on Track A's forbidden list, and the
    classification behind them is `contract.FEATURE_FIELDS`, which is
    human-only. So the refusal would have to be written where this track may
    not write, the subtest is left out, and the criterion keeps the name the
    brief gave it rather than being renamed to fit what landed. Mutation M3 of
    the brief -- the refusal message drops the column name -- has no target on
    this tree and was not run, for the same reason.

    **Read off `holes`, not off a second pass over the rows.** The membership
    test is `holes[column] == row_count` on the build's own count. A second
    scan would key on a grid of its own and could disagree with the published
    `holes` on an incomplete date, and then two numbers in the same manifest
    would describe two different panels.

    **An empty column stays in `built_columns`.** Nothing that reads that list
    today changes meaning; `empty_columns` is a second, narrower fact beside it.

    **A build over zero rows has no empty columns, not every column.**
    `holes[c] == row_count` is true of every `c` when `row_count` is 0, so the
    cheap implementation reports a panel with no rows as empty in every column
    -- when it says nothing about any of them. Rule 6 raises before
    `build_daily_panel` can return a build with no rows, so the case is not
    reachable through the join; it is reachable on the frozen dataclass, which
    is public, and the subtest reaches it the only honest way -- by taking a
    real fixture build's rows away with `dataclasses.replace`, holes with them.
    That unreachability is why `empty_columns` is a property and not a field
    the join computes: a field would leave the trap untestable and the guard
    unmutatable, which is the same thing as not having one.

    **Not in the written file manifest.** A27's wall, unchanged and for the
    same reason: `write_daily_panel`'s manifest is carried whole into the
    published run records under `panel.build_manifest`, and
    `scripts/reproduce_milestone_a.py` compares it key by key, so a new key is
    "present on one side only" and the Milestone A reproduction goes red. The
    last subtest asserts the key's absence so the undone half stays visible,
    and the comment in `write_daily_panel` now points at both keys rather than
    carrying a second copy of the argument. Landing either file half is one
    human commit with every affected record re-scored.

    **No published figure moves.** `empty_columns` is derived from `holes`,
    which this block does not touch, and it is published nowhere the
    reproduction reads.

    **The fixture.** A working week, 5 to 9 January 2026. `sofr` prints on all
    five and is the only `REQUIRED_FIELDS` column declared, so rule 6 retains
    all five. `tgcr` prints on 7 January alone -- a hole on every row but one,
    which is the near miss the `==` has to reject. `bgcr` and `on_rrp` have no
    observation at all, and they are declared in the other order so a tuple
    that is not sorted cannot pass. `treasury_settlement_coupons` has no
    observation either and is *not* empty: the auction snapshot supplies a bill
    settlement on 5 January and is retrieved on 19 January Eastern, so all five
    grid dates are inside coverage and rule 8 writes 0.0 on every one of them.
    A settlement zero is a value, not a hole (`TreasurySettlementZeroTests` is
    the precedent), and reading emptiness off `holes` is what gets that right.

    Mutation record, 12 September 2026, python3 3.9.6. Both mutations applied
    to `src/repo_model/data.py` in a disposable copy under `$HOME` built from
    `git ls-files -z --cached --others --exclude-standard`, confirmed applied
    (the replaced text occurs exactly once before), reverted from a kept
    original and confirmed byte-identical before the next.
    `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`, `OMP_NUM_THREADS=1`, the whole
    suite each time. Unmutated control green before the first and after the
    last, no expected failure.

    1. **The emptiness test becomes `>`** (`self.holes[column] > row_count`) --
       a count of holes can never exceed the row count, so the guard never
       fires. Killed by this test and nothing else, one subtest, "a column that
       is a hole on every row is named empty": `AssertionError`,
       `() != ('bgcr', 'on_rrp')`. The sortedness subtest passes under it,
       because the empty tuple is sorted; sortedness is asserted against the
       declaration order and cannot be what holds the `==`, which is why the
       naming subtest states the tuple in full rather than testing membership.
    2. **The zero-row guard deleted** (`if row_count == 0: return ()` removed).
       Killed by this test and nothing else, `AssertionError` on the trap
       subtest alone: `('bgcr', 'on_rrp', 'sofr', 'tgcr', 'treasury_settlement_coupons') != ()`.
       Every other subtest passes under it, which is why the trap needs its own
       assertion and is not a consequence of the others.
    """

    SOFR_SHA = "c" * 64
    AUCTION_SHA = "d" * 64
    RETRIEVED_AT = "2026-01-20T03:00:00+00:00"

    GRID = (
        date(2026, 1, 5),
        date(2026, 1, 6),
        date(2026, 1, 7),
        date(2026, 1, 8),
        date(2026, 1, 9),
    )

    #: Declared out of sorted order on purpose: the two empty ones are `on_rrp`
    #: then `bgcr` here, and `empty_columns` must report `bgcr` first.
    COLUMNS = ("sofr", "on_rrp", "tgcr", "bgcr", "treasury_settlement_coupons")

    #: `tgcr` is the near miss: a hole on every row but this one.
    TGCR_DATE = date(2026, 1, 7)

    #: The one settlement the snapshot supplies. It fixes the lower edge of
    #: coverage at the first grid date; its column is not declared, and the
    #: coverage bound does not care, because "nothing settled that day" is a
    #: fact about the whole auction record.
    BILL_DATE = date(2026, 1, 5)

    LAG = {
        "basis": "ref_date",
        "unit": "business_days",
        "days": 1,
        "worst_case_calendar_days": 6,
        "available_time": "15:00",
        "timezone": "America/New_York",
        "note": "fixture",
    }

    def registry(self):
        """Every source the declared columns draw on; the auction lag is the real one."""

        real = json.loads(
            (Path(__file__).parents[1] / "metadata" / "sources.json").read_text(
                encoding="utf-8"
            )
        )
        return {
            "nyfed_sofr": {"release_lag": dict(self.LAG)},
            "nyfed_tgcr": {"release_lag": dict(self.LAG)},
            "nyfed_bgcr": {"release_lag": dict(self.LAG)},
            "fred_macro_latest_vintage": {"release_lag": dict(self.LAG)},
            "treasury_auctions": {
                "release_lag": dict(real["treasury_auctions"]["release_lag"])
            },
        }

    def rows(self):
        new_york = ZoneInfo("America/New_York")
        rows = [
            PointInTimeObservation(
                series_id="SOFR",
                ref_date=ref_date,
                available_at=datetime.combine(
                    ref_date + timedelta(days=1), time(19, 0), tzinfo=timezone.utc
                ),
                value=4.30 + index / 100,
                vintage_id=f"SOFR-{ref_date.isoformat()}",
                source_sha=self.SOFR_SHA,
            )
            for index, ref_date in enumerate(self.GRID)
        ]
        rows.append(
            PointInTimeObservation(
                series_id="TGCR",
                ref_date=self.TGCR_DATE,
                available_at=datetime.combine(
                    self.TGCR_DATE + timedelta(days=1), time(19, 0), tzinfo=timezone.utc
                ),
                value=4.29,
                vintage_id=f"TGCR-{self.TGCR_DATE.isoformat()}",
                source_sha=self.SOFR_SHA,
            )
        )
        rows.append(
            PointInTimeObservation(
                series_id="treasury_settlement_bill",
                ref_date=self.BILL_DATE,
                available_at=datetime.combine(
                    self.BILL_DATE, time(23, 59), tzinfo=new_york
                ),
                value=50.0,
                vintage_id=f"{self.BILL_DATE.isoformat()}:{self.RETRIEVED_AT}",
                source_sha=self.AUCTION_SHA,
            )
        )
        return rows

    def build(self):
        return build_daily_panel(
            self.rows(),
            self.registry(),
            build_cutoff=datetime(2026, 2, 1, tzinfo=timezone.utc),
            decision_time=time.fromisoformat("16:00"),
            columns=self.COLUMNS,
            snapshot_retrieved_at={self.AUCTION_SHA: self.RETRIEVED_AT},
        )

    def test_a_column_that_is_a_hole_on_every_row_is_named_empty_and_refused_as_a_feature(
        self,
    ):
        """A28's acceptance criterion and mutation target. See the class docstring.

        The refusal half of the name is not implemented and is not reachable
        from `data.py` on this tree; the class docstring says what was grepped.
        """

        build = self.build()
        panel = {row.date: row.values for row in build.observations}
        self.assertEqual(len(panel), len(self.GRID))

        with self.subTest("a column that is a hole on every row is named empty"):
            self.assertEqual(build.holes["bgcr"], len(self.GRID))
            self.assertEqual(build.holes["on_rrp"], len(self.GRID))
            self.assertEqual(build.empty_columns, ("bgcr", "on_rrp"))
            for day in self.GRID:
                self.assertIsNone(panel[day]["bgcr"], day)

        with self.subTest("an empty column is still a built column"):
            # The whole point of the tuple being a second fact rather than a
            # narrowing: nothing that reads `built_columns` changes meaning.
            self.assertEqual(build.built_columns, self.COLUMNS)
            for column in build.empty_columns:
                self.assertIn(column, build.built_columns)

        with self.subTest("the names are sorted, not the declaration order"):
            self.assertEqual(build.empty_columns, tuple(sorted(build.empty_columns)))
            # Declared `on_rrp` before `bgcr`, so declaration order would fail.
            self.assertLess(
                self.COLUMNS.index("on_rrp"), self.COLUMNS.index("bgcr")
            )

        with self.subTest("a column with one value is not empty"):
            # The near miss the `==` exists to reject: four holes over five rows.
            self.assertEqual(build.holes["tgcr"], len(self.GRID) - 1)
            self.assertEqual(panel[self.TGCR_DATE]["tgcr"], 4.29)
            self.assertNotIn("tgcr", build.empty_columns)
            self.assertEqual(build.holes["sofr"], 0)
            self.assertNotIn("sofr", build.empty_columns)

        with self.subTest("a rule 8 settlement zero is a value, so its column is not empty"):
            # No coupon settlement is observed anywhere in the fixture, and the
            # column still is not empty: rule 8 wrote 0.0 on all five grid
            # dates, and a written zero is a value. Read off `holes` -- which
            # does not count a zero -- this is right by construction; a second
            # pass that counted "no observation" would call it empty.
            for day in self.GRID:
                self.assertEqual(panel[day]["treasury_settlement_coupons"], 0.0, day)
            self.assertEqual(
                build.settlement_zeros["treasury_settlement_coupons"], len(self.GRID)
            )
            self.assertEqual(build.holes["treasury_settlement_coupons"], 0)
            self.assertNotIn("treasury_settlement_coupons", build.empty_columns)

        with self.subTest("a build over no rows has no empty columns, not every column"):
            # THE TRAP. `holes[c] == row_count` is true of every column when
            # `row_count` is 0. Rule 6 raises before the join can return such a
            # build -- asserted here rather than assumed -- so the case is
            # reached on the dataclass, which is public: the fixture build with
            # its rows taken away, and its holes with them, which is what a
            # build over no rows would carry.
            with self.assertRaises(DataContractError):
                build_daily_panel(
                    [],
                    self.registry(),
                    build_cutoff=datetime(2026, 2, 1, tzinfo=timezone.utc),
                    decision_time=time.fromisoformat("16:00"),
                    columns=self.COLUMNS,
                    snapshot_retrieved_at={self.AUCTION_SHA: self.RETRIEVED_AT},
                )
            no_rows = replace(
                build,
                observations=(),
                holes={column: 0 for column in build.built_columns},
            )
            self.assertEqual(len(no_rows.observations), 0)
            self.assertEqual(no_rows.built_columns, self.COLUMNS)
            self.assertEqual(no_rows.empty_columns, ())

        with self.subTest("the file manifest does not carry it, and that is measured"):
            # A27's wall, and the same one. Not an endorsement: the record of a
            # measurement, asserting the state this block leaves so the day the
            # human re-publishes the records, this line says the other half is
            # still undone. See the class docstring.
            with tempfile.TemporaryDirectory() as directory:
                manifest_path = write_daily_panel(build, Path(directory) / "panel.csv")
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["holes"], dict(build.holes))
            self.assertEqual(manifest["built_columns"], list(build.built_columns))
            self.assertNotIn("empty_columns", manifest)
            self.assertNotIn("settlement_zeros", manifest)


class SnapshotBasisPricingTests(unittest.TestCase):
    """A30: a `snapshot_retrieved_at` column is priced from rows, and only visible ones.

    `_priceable_columns` asked `registry.max_release_lag_days` about every
    column in the `(source, field)` pair form, which carries no rows, so every
    column on a `snapshot_retrieved_at` source was refused with `every snapshot
    row must carry available_at` without ever having been handed a row. On the
    tracked registry that was `on_rrp`, `reserve_balances` and `tga`
    (`fred_macro_latest_vintage`) and `mmf_assets` (`sec_nmfp`). The registry
    half landed in the human's `4f317b24`: a per-row priced selection may now
    return a purge of zero. This is the `data.py` half.

    Fixture registries throughout, never `metadata/sources.json`: a test that
    asserted which tracked columns are built would be asserting the registry,
    and a registry edit would break a test that is about pricing.

    Two existing tests asserted the defect and were changed with it, each
    keeping what it is for: `DailyPanelJoinTests.test_a_column_is_refused_by_
    the_registry_not_by_a_list` (see the addendum there) and the `on_rrp`
    phrase of `RequestedColumnsBuildTests`, now `quarter_end` (see that class).

    Mutation record, 12 September 2026, python3 3.9.6. Each mutation applied
    in its own disposable copy under `$HOME`, built from `git ls-files -z
    --cached --others --exclude-standard`; `PYTHONDONTWRITEBYTECODE=1`,
    `python3 -B`, the whole suite run in each. Every target was confirmed
    present exactly once before and absent after. The unmutated control was
    green before and after. Every kill below is `AssertionError`, and the
    subtests named are the parts of the one acceptance test.

    1. **The rows dropped again**: the retry with rows replaced by `pass`, so
       every column is priced in the pair form. Killed only this test: part 1
       (`[] != ['reserve_balances']`) and part 3's premise, the later-cutoff
       build (`'reserve_balances' not found in ('sofr',)`).
    2. **All `observations` passed** to `_priceable_columns` in place of the
       cutoff-visible rows. Killed only part 3: `('sofr', 'reserve_balances')
       != ('sofr',)`, the column built at the cutoff from a row published
       after it.
    3. **Every column priced by the mapping form**, each source handed the
       visible rows of the column's fields, no pair-form call. Killed part 4
       (`[] != ['iorb']`, a declared field refused for want of rows its
       declaration never needed), and outside this class
       `DailyPanelJoinTests.test_a_column_is_refused_by_the_registry_not_by_a_
       list` (`DataContractError not raised`, a field declaration with no
       revision policy rescued by its source's basis).
    4. **The refusal composed in `data.py`**: `refusals[column]` set to
       `f"{column}: a snapshot row carries no available_at"`. Killed only this
       test: part 2, and parts 3 and 4, which also compare the recorded reason
       against the pricing function's own message.
    """

    SOURCE = "fred_macro_latest_vintage"
    DECISION_TIME = time(16, 0)
    CUTOFF = datetime(2026, 3, 1, tzinfo=timezone.utc)

    def snapshot_registry(self, **field_release_lags):
        registry = {
            self.SOURCE: {
                "release_lag": {
                    "basis": "snapshot_retrieved_at",
                    "note": "fixture: latest vintage only",
                }
            },
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
            },
        }
        if field_release_lags:
            registry[self.SOURCE]["field_release_lags"] = field_release_lags
        return registry

    #: Stands for the tracked `IORB` and `IOER` entries of
    #: `fred_macro_latest_vintage.field_release_lags`: a `record_date` lag
    #: licensed on a snapshot source by `revision_policy: "never_revised"`.
    #: The notes and evidence are shortened; the shape is theirs.
    def field_lag(self, *, with_policy=True):
        block = {
            "basis": "record_date",
            "unit": "calendar_days",
            "days": 1,
            "available_time": "16:15",
            "timezone": "America/New_York",
            "note": "fixture",
        }
        if with_policy:
            block["revision_policy"] = "never_revised"
            block["revision_evidence"] = "fixture: stands for the ALFRED vintage comparison"
        return block

    def row(self, series_id, ref_date, available_at, value=1.0):
        return PointInTimeObservation(
            series_id=series_id,
            ref_date=ref_date,
            available_at=available_at,
            value=value,
            vintage_id=f"{series_id}-{ref_date.isoformat()}",
            source_sha="d" * 64,
        )

    def registry_refusal(self, registry, selection):
        """The pricing function's own message for a selection, asked directly."""

        from repo_model.registry import RegistryContractError, max_release_lag_days

        with self.assertRaises(RegistryContractError) as caught:
            max_release_lag_days(registry, selection, decision_time=self.DECISION_TIME)
        return str(caught.exception)

    def test_a_snapshot_basis_column_is_priced_from_the_rows_this_build_can_see(self):
        """The acceptance criterion and the mutation target. See the class docstring."""

        from repo_model.contract import field_sources_for_features
        from repo_model.data import _priceable_columns

        registry = self.snapshot_registry()
        seen = datetime(2026, 1, 9, 21, tzinfo=timezone.utc)
        rows = [
            self.row("WRESBAL", date(2026, 1, 5), seen),
            self.row("WRESBAL", date(2026, 1, 6), seen),
        ]

        with self.subTest("built: every visible row carries available_at"):
            # The premise: with no rows the same column is refused, which is
            # what every call made before A30 amounted to.
            built, refusals = _priceable_columns(
                ["reserve_balances"], registry, self.DECISION_TIME
            )
            self.assertEqual(built, [])
            self.assertIn("reserve_balances", refusals)

            built, refusals = _priceable_columns(
                ["reserve_balances"], registry, self.DECISION_TIME, rows
            )
            self.assertEqual(built, ["reserve_balances"])
            self.assertNotIn("reserve_balances", refusals)

        with self.subTest("refused, by the registry: one visible row has no available_at"):
            missing = rows + [self.row("WRESBAL", date(2026, 1, 7), None)]
            built, refusals = _priceable_columns(
                ["reserve_balances"], registry, self.DECISION_TIME, missing
            )
            self.assertEqual(built, [])
            self.assertEqual(
                refusals["reserve_balances"],
                self.registry_refusal(registry, {self.SOURCE: missing}),
            )

        with self.subTest("the cutoff binds: a row published after it prices nothing"):
            sofr = self.row("SOFR", date(2026, 1, 5), seen, value=4.30)
            future = self.row(
                "WRESBAL", date(2026, 1, 5), self.CUTOFF + timedelta(days=1)
            )

            def build(observations, cutoff):
                return build_daily_panel(
                    observations,
                    registry,
                    build_cutoff=cutoff,
                    decision_time=self.DECISION_TIME,
                    columns=("sofr", "reserve_balances"),
                )

            # The two answers differ, or the assertion below could not fail:
            # at a cutoff that can see the row, the column is built.
            later = build([sofr, future], self.CUTOFF + timedelta(days=2))
            self.assertIn("reserve_balances", later.built_columns)

            at_cutoff = build([sofr, future], self.CUTOFF)
            self.assertEqual(at_cutoff.built_columns, ("sofr",))
            without_it = build([sofr], self.CUTOFF)
            self.assertEqual(
                at_cutoff.refusals["reserve_balances"],
                without_it.refusals["reserve_balances"],
            )
            self.assertEqual(
                at_cutoff.refusals["reserve_balances"],
                self.registry_refusal(registry, {self.SOURCE: []}),
            )

        with self.subTest("field declarations still win on a snapshot-basis source"):
            declared = self.snapshot_registry(
                IORB=self.field_lag(), IOER=self.field_lag()
            )
            # Priced by its declaration, with no rows to price it otherwise.
            built, refusals = _priceable_columns(["iorb"], declared, self.DECISION_TIME, ())
            self.assertEqual(built, ["iorb"])
            self.assertEqual(refusals, {})

            # And refused by its declaration, however good the rows: a field
            # lag with no revision policy is not rescued by the source's basis.
            unlicensed = self.snapshot_registry(
                IORB=self.field_lag(with_policy=False),
                IOER=self.field_lag(with_policy=False),
            )
            iorb_rows = [self.row("IORB", date(2026, 1, 5), seen, value=4.40)]
            built, refusals = _priceable_columns(
                ["iorb"], unlicensed, self.DECISION_TIME, iorb_rows
            )
            self.assertEqual(built, [])
            self.assertEqual(
                refusals["iorb"],
                self.registry_refusal(unlicensed, field_sources_for_features(["iorb"])),
            )
            self.assertIn("revision_policy", refusals["iorb"])


def replace_observation(observation, ref_date):
    """One observation moved to another reference date, availability with it.

    `available_at` is moved by the same number of days rather than recomputed,
    so the moved row keeps the lag the adapter derived from the registry and
    `validate_publication_gaps` would still accept it. Only the identity's
    date arithmetic is under test here, not the lag's.
    """

    shift = ref_date - observation.ref_date
    return replace(
        observation,
        ref_date=ref_date,
        available_at=observation.available_at + shift,
    )
