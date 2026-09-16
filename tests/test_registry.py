import csv
import json
import re
import unittest
from datetime import date, time, timedelta, timezone
from pathlib import Path

from repo_model.contract import END_OF_DAY
from repo_model.registry import (
    AVAILABILITY_PROVENANCE_KEY,
    AVAILABILITY_PROVENANCE_PUBLICATION,
    RegistryContractError,
    check_availability_provenance,
    max_release_lag_days,
)


def source(
    basis,
    unit=None,
    days=None,
    available_time=None,
    timezone_name="America/New_York",
    provenance=None,
    **extra,
):
    release_lag = {"basis": basis, **extra}
    if unit is not None:
        release_lag["unit"] = unit
    if days is not None:
        release_lag["days"] = days
    if available_time is not None:
        release_lag["available_time"] = available_time
        release_lag["timezone"] = timezone_name
    declared = {"release_lag": release_lag}
    if provenance is not None:
        declared[AVAILABILITY_PROVENANCE_KEY] = provenance
    return declared


#: A revision-only field block: the licence that lets a `snapshot_retrieved_at`
#: source be priced from rows carrying `available_at`. No basis of its own, and
#: field-level because the claim is true of some series of a latest-vintage
#: source and false of others -- see `contract._FIELD_ALLOWED_KEYS`.
_REVISION_ONLY = {
    "revision_policy": "never_revised",
    "revision_evidence": "fixture: stands for an ALFRED vintage comparison",
    "note": "fixture: revision-only, licences pricing from rows",
}


class MaxReleaseLagDaysTests(unittest.TestCase):
    def test_ref_date_business_days_uses_declared_calendar_bound(self):
        registry = {
            "daily": source(
                "ref_date",
                "business_days",
                1,
                worst_case_calendar_days=6,
            )
        }

        self.assertEqual(
            max_release_lag_days(registry, ["daily"], decision_time=time(8)),
            6,
        )

    def test_record_date_calendar_days_adds_day_after_decision_time(self):
        registry = {
            "auction": source(
                "record_date",
                "calendar_days",
                2,
                available_time="16:00",
            )
        }

        self.assertEqual(
            max_release_lag_days(registry, ["auction"], decision_time=time(15)),
            3,
        )
        self.assertEqual(
            max_release_lag_days(registry, ["auction"], decision_time=time(16)),
            2,
        )

    def test_snapshot_retrieved_at_contributes_no_purge_with_available_at(self):
        registry = {
            "snapshot": source(
                "snapshot_retrieved_at",
            ),
            "auction": source(
                "record_date",
                "calendar_days",
                2,
                available_time="10:00",
            ),
        }
        # The snapshot leg is selected in the three-tuple form and its field
        # declares a revision-only block. Rows alone stopped being enough when
        # the licence landed: they say when a row arrived, not whether the
        # latest vintage is the value that stood on the day.
        registry["snapshot"]["field_release_lags"] = {"px": _REVISION_ONLY}
        selected = [
            ("snapshot", "px", [{"available_at": "2026-01-02T12:00:00Z"}]),
            "auction",
        ]

        self.assertEqual(
            max_release_lag_days(registry, selected, decision_time=time(15)),
            2,
        )

    def test_snapshot_retrieved_at_raises_when_available_at_is_absent(self):
        registry = {
            "snapshot": source(
                "snapshot_retrieved_at",
            )
        }

        with self.assertRaisesRegex(RegistryContractError, "available_at"):
            max_release_lag_days(
                registry,
                {"snapshot": [{"ref_date": "2026-01-02"}]},
                decision_time=time(15),
            )

        with self.assertRaisesRegex(RegistryContractError, "available_at"):
            max_release_lag_days(registry, ["snapshot"], decision_time=time(15))

    def test_snapshot_retrieved_at_raises_when_rows_are_empty(self):
        registry = {
            "snapshot": source(
                "snapshot_retrieved_at",
            )
        }

        with self.assertRaisesRegex(RegistryContractError, "available_at"):
            max_release_lag_days(
                registry,
                {"snapshot": []},
                decision_time=time(15),
            )

    def test_empty_source_selection_raises_instead_of_returning_zero(self):
        for selected in ({}, []):
            with self.subTest(sources=selected):
                with self.assertRaisesRegex(RegistryContractError, "at least one"):
                    max_release_lag_days({}, selected, decision_time=time(15))

    def test_zero_purge_is_rejected_instead_of_returned(self):
        registry = {
            "already_available": source(
                "record_date",
                "calendar_days",
                0,
                available_time="09:00",
            )
        }

        with self.assertRaisesRegex(RegistryContractError, "nonzero purge"):
            max_release_lag_days(
                registry,
                ["already_available"],
                decision_time=time(15),
            )

    def test_release_lag_shape_errors_come_from_the_shared_validator(self):
        registry = {
            "legacy": {
                "release_lag": {
                    "basis": "record_date",
                    "calendar": "calendar_days",
                    "days": 1,
                    "available_time": "12:00:00",
                    "timezone": "America/New_York",
                }
            }
        }

        with self.assertRaisesRegex(
            RegistryContractError,
            "unknown release_lag keys.*unit.*HH:MM",
        ):
            max_release_lag_days(registry, ["legacy"], decision_time=time(15))

    def test_aware_decision_time_must_match_the_declared_timezone(self):
        registry = {
            "auction": source(
                "record_date",
                "calendar_days",
                0,
                available_time="16:00",
            )
        }

        with self.assertRaisesRegex(RegistryContractError, "does not match"):
            max_release_lag_days(
                registry,
                ["auction"],
                decision_time=time(15, tzinfo=timezone.utc),
            )

    def test_naive_decision_time_rejects_multiple_release_timezones(self):
        registry = {
            "new_york": source(
                "record_date",
                "calendar_days",
                0,
                available_time="09:00",
            ),
            "utc": source(
                "record_date",
                "calendar_days",
                0,
                available_time="09:00",
                timezone_name="UTC",
            ),
        }

        with self.assertRaisesRegex(RegistryContractError, "across release timezones"):
            max_release_lag_days(
                registry,
                ["new_york", "utc"],
                decision_time=time(15),
            )

    def test_matching_aware_timezone_is_compared_as_declared_wall_clock(self):
        registry = {
            "filing": source(
                "record_date",
                "calendar_days",
                2,
                available_time="16:00",
                timezone_name="UTC",
            )
        }

        self.assertEqual(
            max_release_lag_days(
                registry,
                ["filing"],
                decision_time=time(15, tzinfo=timezone.utc),
            ),
            3,
        )

    def test_only_selected_feature_sources_contribute_to_maximum(self):
        registry = {
            "used": source(
                "record_date",
                "calendar_days",
                2,
                available_time="10:00",
            ),
            "unused": source(
                "ref_date",
                "business_days",
                30,
                worst_case_calendar_days=35,
            ),
        }

        self.assertEqual(
            max_release_lag_days(registry, ["used"], decision_time=time(15)),
            2,
        )


class SnapshotOnlySelectionTests(unittest.TestCase):
    """A selection priced entirely by per-row availability may purge zero.

    The nonzero-purge guard exists because a feature set that prices to no gap
    is the shape of an error: a missing declaration, a `days` of zero, or a
    calendar-only selection resolving to nothing. It was global, and that made
    it refuse the one selection for which zero is the correct answer. A
    `snapshot_retrieved_at` source carries `available_at` on every row, so each
    row states when it could first be read and there is nothing for a
    calendar-day bound to conservatively cover. The guard now asks whether the
    zero was *accounted for* rather than whether it is zero.

    Why this mattered beyond the abstraction: `data._priceable_columns` prices
    every declared column **alone**, through
    `contract.field_sources_for_features([column])`. A column whose only source
    is snapshot-basis therefore reached this guard by itself and could never
    clear it, so `on_rrp`, `reserve_balances` and `mmf_assets` were refused from
    the panel on every build, whatever the snapshot held. That is half the
    defect; the other half is the call site passing no rows, which is Track A's
    and is not this commit.

    The preserved half is asserted here too, and is the reason this is a scoping
    and not a removal: a selection that prices to zero with no per-row
    availability behind it is still refused.

    Mutation record, 12 September 2026. A copy outside the mount,
    `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`, `OMP_NUM_THREADS=1`, the whole
    suite each time, reverted after. Unmutated control green before (823 tests,
    before these tests existed) and after (825 tests, `OK`).

    1. **The zero never accounted for** -- the `snapshot_retrieved_at` branch
       setting `contribution = 0` without setting `per_row_availability`. One
       error, this test,
       `repo_model.registry.RegistryContractError: selected sources must produce
       a nonzero purge`. That is the defect this commit repairs, reproduced: the
       exception is raised on the one selection for which zero is the right
       answer.
    2. **The guard dropped entirely** rather than scoped -- the refusal made
       unreachable. Three failures, and only one of them is this test. The other
       two are pre-existing and were written by other blocks:
       `MaxReleaseLagDaysTests.test_zero_purge_is_rejected_instead_of_returned`,
       and, in `tests/test_event_eval.py`, `PurgeBoundaryTests`'
       `test_the_gap_is_derived_and_cannot_be_supplied`. Both
       `AssertionError: RegistryContractError not raised`.
       That result is the evidence the change is a scoping: the guard it narrows
       is still independently held up by two tests this commit did not write, so
       narrowing it did not blunt it. A mutation that killed only the new test
       would have meant the opposite.
    """

    ROWS = ({"available_at": "2026-01-02T10:00:00-05:00"},)

    def test_a_snapshot_only_selection_prices_to_zero_and_is_not_refused(self):
        registry = {"snap": source("snapshot_retrieved_at")}
        registry["snap"]["field_release_lags"] = {"X": _REVISION_ONLY}

        self.assertEqual(
            max_release_lag_days(
                registry, [("snap", "X", self.ROWS)], decision_time=time(16)
            ),
            0,
        )

        # A row missing the instant is still refused: scoping the zero did not
        # weaken what the zero is conditional on.
        with self.assertRaises(RegistryContractError) as caught:
            max_release_lag_days(
                registry, [("snap", "X", ({"available_at": ""},))], decision_time=time(16)
            )
        self.assertIn("available_at", str(caught.exception))

        # And a zero with nothing per-row behind it is the error the guard was
        # written for, so it still raises: a `record_date` source declaring no
        # lag and an instant the decision time clears.
        with self.assertRaises(RegistryContractError) as caught:
            max_release_lag_days(
                {"filing": source("record_date", "calendar_days", 0,
                                  available_time="09:00")},
                ["filing"],
                decision_time=time(17),
            )
        self.assertIn("nonzero purge", str(caught.exception))


class SnapshotLicenceTests(unittest.TestCase):
    """Rows do not buy you a latest-vintage snapshot; a field-level licence does.

    `available_at` on a row says when that row arrived. It does not say whether
    the value attached to an old date is the value that stood on that date, and
    on a latest-vintage source it usually is not: `fred_macro_latest_vintage`
    carries H.4.1 weeklies that are revised. `contract.validate_field_release_lag`
    has always held a *field-level* declaration on a snapshot source to
    `revision_policy: "never_revised"` with evidence, for exactly this reason,
    and the per-row path added around it reached the same source without ever
    asking that question.

    So a snapshot source is priced from rows only for a field that declares a
    **revision-only block** -- `revision_policy` and `revision_evidence`, no
    basis of its own -- which is the licence and not a lag. A source-level
    policy is not an option and never was: see `contract._FIELD_ALLOWED_KEYS`,
    where a policy declared for a whole source is named as the claim the split
    exists to stop anyone making.

    When this was written nothing on the tracked registry declared one, so
    `on_rrp`, `reserve_balances`, `tga` and `mmf_assets` then stayed unbuilt,
    which is what `PLAN.md` and `docs/PROJECT_STATUS.md` said and what they
    were briefly ahead of. `metadata/sources.json` has declared the licence for
    `WRESBAL` and `WTREGEN` since 14 September 2026, so `reserve_balances` and
    `tga` are built columns of the published panel; `on_rrp` and `mmf_assets`
    are not.

    Mutation record, 13 September 2026, `.venv/bin/python` with
    `REPO_MODEL_REQUIRE_ML=1`, whole suite per mutation, the patch committed in
    a disposable checkout under `$HOME` first --- reverting a mutation with
    `git checkout --` in a tree whose patch is uncommitted throws the patch away
    too, which is how the first attempt found zero anchors on its second
    mutation. Control green before and after.

    1. **The licence check removed** from the snapshot branch (`if not
       licensed:` -> `if False:`). Kills exactly two tests, one in each class
       that states the rule: this class's unlicensed-refusal test and
       `test_data.SnapshotLicenceAtTheCallSiteTests`' own. `AssertionError`,
       `RegistryContractError not raised`. Nothing else in the suite moves,
       which is the evidence that the licence is a new rule rather than a
       restatement of the rows rule.
    2. **A revision-only block read as a lag** (the licence arm also setting
       `release_lag = declared`). Kills nine tests across four modules --- and
       all nine are the same `KeyError: 'basis'`, because a licence has no
       basis to read. That is a crash, not nine independent guards, and it is
       recorded as one: the count here is not evidence of coverage.
    3. **The retry drops the field** (`data.py` passing `None` where it passes
       the field). Kills five subtests, all in the data layer:
       `SnapshotBasisPricingTests`' four and the call-site class's built test.
       `AssertionError`. A selection that carries no field can never be
       licensed, which is precisely why the pair and mapping forms were not
       enough and the three-tuple form exists.
    """

    ROWS = ({"available_at": "2026-01-02T10:00:00-05:00"},)

    def licensed(self):
        registry = {"snap": source("snapshot_retrieved_at")}
        registry["snap"]["field_release_lags"] = {
            "X": {
                "revision_policy": "never_revised",
                "revision_evidence": "fixture: stands for an ALFRED vintage comparison",
                "note": "fixture: revision-only, no lag of its own",
            }
        }
        return registry

    def test_an_unlicensed_snapshot_field_is_refused_however_good_its_rows_are(self):
        registry = {"snap": source("snapshot_retrieved_at")}
        with self.assertRaises(RegistryContractError) as caught:
            max_release_lag_days(
                registry, [("snap", "X", self.ROWS)], decision_time=time(16)
            )
        message = str(caught.exception)
        self.assertIn("revision_policy", message)
        self.assertNotIn("must carry available_at", message)

    def test_a_licensed_snapshot_field_prices_to_zero_from_rows(self):
        self.assertEqual(
            max_release_lag_days(
                self.licensed(), [("snap", "X", self.ROWS)], decision_time=time(16)
            ),
            0,
        )

    def test_a_licence_does_not_excuse_a_row_with_no_instant(self):
        with self.assertRaises(RegistryContractError) as caught:
            max_release_lag_days(
                self.licensed(),
                [("snap", "X", ({"available_at": ""},))],
                decision_time=time(16),
            )
        self.assertIn("available_at", str(caught.exception))


class AvailabilityProvenanceTests(unittest.TestCase):
    """A declared availability instant earlier than end of day cites its evidence.

    The acceptance criterion of A26. `contract.END_OF_DAY` asserts nothing about
    when anyone outside the publisher could read a value, so it needs no
    evidence. Anything earlier is a claim, and it is a claim in the single
    direction this declaration can cause harm: it makes the data appear
    available sooner. So the rule asserted here is the **link** between an early
    instant and its provenance, on constructed registries, and never that
    today's `metadata/sources.json` carries a particular number -- an equality
    against `treasury_bill_rates.available_time == "16:30"` would pass just as
    happily on a declaration someone tightened by guesswork next month, and
    would say nothing about the next source to declare one.

    A free-text `note` does not satisfy it. The registry has carried notes
    asserting an availability time since the first source landed, including the
    end-of-day note this block replaced, which said in prose that no publication
    time had been read and that checking it was a human-side step. Prose cannot
    be required of the next author by anything but a reader.

    **Two cases are out of reach rather than out of scope, and both are
    findings, not omissions.**

    1. **A `ref_date` source's `available_time`.** `check_availability_provenance`
       reads a source's own `record_date` block, which is the declaration
       `contract.validate_release_lag` *requires* an `available_time` of and the
       only one `max_release_lag_days` reads the instant from. On the tracked
       registry that leaves four early instants unguarded -- `nyfed_sofr`,
       `nyfed_tgcr` and `nyfed_bgcr` at 15:00 and `nyfed_fr2004` at 16:30 -- and
       B30's `baseline._check_decision_relative_availability` now reads them per
       fold, so they are read and not only declared. `nyfed_sofr`'s and
       `nyfed_fr2004`'s notes cite a publication schedule; `nyfed_tgcr`'s and
       `nyfed_bgcr`'s cite nothing but the convention, so extending the guard
       there refuses the tracked registry on evidence nobody on this project
       has. That is a fetch, and fetches are the human's.
    2. **A `field_release_lags` entry.** `fred_macro_latest_vintage` prices
       `IOER` and `IORB` at 16:15, an early instant, and no provenance can be
       declared for it at all: `contract._FIELD_ALLOWED_KEYS` is closed and
       `contract.py` is human-owned, so the key cannot be added there, and this
       module will not read a source-level claim as evidence for a field-level
       instant it does not describe.

    **Why the guard is not inside `max_release_lag_days`,** where the instant is
    actually priced and where the harm lands: the fixtures that price a
    `record_date` source through it declare `available_time` `"00:00"` with no
    provenance -- `tests/test_baseline.py`, `tests/test_cli_eval.py` and
    `tests/test_event_eval.py`, all forbidden to Track A -- and the SHARED
    `tests/test_registry_interface.py` declares 09:00 and 18:00. A guard there
    is a change to three files this track may not edit, so it is a proposal to
    the human and not a move Track A can make. The guard is on the registry
    *document*, at `ingest.load_source_registry`, which is the one door a
    document comes through and which no Track B fixture uses.

    Mutation record, 11 September 2026, python3 3.9.6. Both mutations applied in
    a disposable copy under `$HOME` built from
    `git ls-files -z --cached --others --exclude-standard`, reverted and
    confirmed byte-identical to the pristine file before the next.
    `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`, `OMP_NUM_THREADS=1`, the whole
    suite each time. Unmutated control green before the first and after the last,
    no expected failure. The copy is not a git work tree, so the guards that ask
    git skip there; the mount runs them and none of them reads an availability
    instant.

    1. **The no-provenance refusal returns no problem** --
       `registry._availability_provenance_problems` returns `[]` where it
       refuses a missing `availability_provenance`. Four failures, every one of
       them this test, every one `AssertionError: RegistryContractError not
       raised`: the three `evidence='none'` subtests, one per instant in
       `EARLY`, and the unsubtested case at the end that declares the claim in a
       `release_lag` `note` instead. That last one is the mutation's most useful
       result -- it is the shape the tracked registry carried until this block,
       and without the guard it is indistinguishable from evidence.
    2. **The names-no-source refusal returns no problem** -- the same function
       returns `[]` where it refuses a provenance whose `publication` is absent
       or blank. Three failures, every one this test, every one `AssertionError:
       RegistryContractError not raised`: the empty object, the object carrying
       only a `note`, and the one whose `publication` is whitespace.

    Neither mutation was caught anywhere else in the suite, which is the point
    of recording them: before this block nothing in the repository could tell an
    evidenced instant from an asserted one.

    Mutation record, 12 September 2026, for the widening past `record_date`.
    Same method: a copy outside the mount, `PYTHONDONTWRITEBYTECODE=1`,
    `python3 -B`, `OMP_NUM_THREADS=1`, the whole suite, reverted after.
    Unmutated control green before (823 tests, no new tests) and after (825).

    3. **The scope put back** -- `check_availability_provenance` skipping every
       source whose `release_lag` basis is not `record_date`, which is what this
       commit removed. Three failures, all of them
       `test_an_early_instant_carries_its_evidence_whatever_the_basis`, one per
       instant in `EARLY`, every one `AssertionError: RegistryContractError not
       raised`. Nothing else in the suite moved, so before this commit nothing
       could tell an evidenced `ref_date` instant from an asserted one either --
       and `baseline._check_decision_relative_availability` had been reading
       those instants per fold since B30.
    """

    #: Instants strictly earlier than end of day, including one a minute before
    #: it. Derived from `END_OF_DAY` rather than typed, so the boundary this
    #: guard turns on is the convention's own and not a number copied beside it.
    EARLY = ("00:00", "15:30", "16:30")

    #: A provenance naming what was read. The value is not asserted against the
    #: tracked registry's: what is asserted is that *something* non-empty names
    #: a publication.
    EVIDENCED = {
        AVAILABILITY_PROVENANCE_PUBLICATION: "A named release, with its instant",
        "note": "Who read it, and when.",
    }

    #: Every way a provenance can be present and still name no source.
    NAMES_NO_SOURCE = (
        {},
        {"note": "The instant was checked. By someone. Somewhere."},
        {AVAILABILITY_PROVENANCE_PUBLICATION: "   "},
    )

    def registry(self, available_time, provenance=None):
        return {
            "filing": source(
                "record_date",
                "calendar_days",
                1,
                available_time=available_time,
                provenance=provenance,
            )
        }

    def ref_date_registry(self, available_time, provenance=None):
        """A `ref_date` source declaring an instant, which is optional there.

        `worst_case_calendar_days` because a `ref_date` declaration is priced
        from its calendar bound and not from `days`; the instant is the only
        part of it this guard reads.
        """

        return {
            "daily": source(
                "ref_date",
                "business_days",
                1,
                available_time=available_time,
                provenance=provenance,
                worst_case_calendar_days=6,
            )
        }

    def test_an_early_instant_carries_its_evidence_whatever_the_basis(self):
        """Earliness is what makes the claim leak, not the basis it sits under.

        The guard was scoped to `record_date` because that is the only basis
        `max_release_lag_days` reads an instant from, and because the four NY
        Fed `ref_date` instants cited nothing machine-readable -- so widening it
        then would have refused the tracked registry on evidence nobody on this
        project had, which is a fetch, and fetches are the human's. The fetch
        happened. What is asserted here is the same link the `record_date` case
        asserts, on a constructed `ref_date` registry, and never that today's
        document carries a particular instant.

        B30's `baseline._check_decision_relative_availability` reads these
        instants per fold, so under this basis they are priced and not merely
        declared. That is what made the unguarded case a hole rather than a
        technicality.
        """

        for available_time in self.EARLY:
            with self.subTest(available_time=available_time, evidence="declared"):
                check_availability_provenance(
                    self.ref_date_registry(available_time, self.EVIDENCED)
                )

            with self.subTest(available_time=available_time, evidence="none"):
                with self.assertRaises(RegistryContractError) as caught:
                    check_availability_provenance(
                        self.ref_date_registry(available_time)
                    )
                message = str(caught.exception)
                self.assertIn(AVAILABILITY_PROVENANCE_KEY, message)
                self.assertIn(available_time, message)

        # End of day asserts nothing under this basis either.
        check_availability_provenance(self.ref_date_registry(END_OF_DAY))

        # And a `ref_date` source may decline to declare an instant at all: a
        # source with nothing to evidence is not a source with missing evidence.
        check_availability_provenance(self.ref_date_registry(None))

    def test_a_declared_availability_time_carries_the_evidence_for_it(self):
        for available_time in self.EARLY:
            with self.subTest(available_time=available_time, evidence="declared"):
                check_availability_provenance(
                    self.registry(available_time, self.EVIDENCED)
                )

            with self.subTest(available_time=available_time, evidence="none"):
                with self.assertRaises(RegistryContractError) as caught:
                    check_availability_provenance(self.registry(available_time))
                message = str(caught.exception)
                self.assertIn(AVAILABILITY_PROVENANCE_KEY, message)
                self.assertIn(available_time, message)

        for provenance in self.NAMES_NO_SOURCE:
            with self.subTest(provenance=provenance):
                with self.assertRaises(RegistryContractError) as caught:
                    check_availability_provenance(
                        self.registry(self.EARLY[-1], provenance)
                    )
                self.assertIn(
                    AVAILABILITY_PROVENANCE_PUBLICATION, str(caught.exception)
                )

        # End of day asserts nothing, so it is the one instant that needs no
        # evidence. Without this the guard could be satisfied by requiring
        # provenance of every source, which would make the conservative
        # declaration the expensive one.
        check_availability_provenance(self.registry(END_OF_DAY))

        # And the evidence has to be machine-readable: the note that carried
        # this claim in prose until this block does not satisfy the rule.
        with self.assertRaises(RegistryContractError):
            check_availability_provenance(
                {
                    "filing": source(
                        "record_date",
                        "calendar_days",
                        1,
                        available_time=self.EARLY[-1],
                        note="Published at 16:30 ET, per the bulk file.",
                    )
                }
            )


REPO_ROOT = Path(__file__).parents[1]
TRACKED_REGISTRY = REPO_ROOT / "metadata" / "sources.json"
TRACKED_SNAPSHOTS = REPO_ROOT / "tests" / "fixtures" / "snapshots" / "funding_inputs"


class RegistryProseAgainstTrackedSidecarsTests(unittest.TestCase):
    """No registry prose claims a fixture property its tracked sidecar contradicts.

    The acceptance criterion of A37. `metadata/sources.json` describes the
    tracked fixtures in free text, and free text is not re-read when a fixture
    is replaced. A34's fetched snapshots were promoted into
    `tests/fixtures/snapshots/funding_inputs/` and three sentences went on
    describing the files they replaced: `nyfed_fr2004`'s `release_lag.note` and
    its `availability_provenance.note` both said the fixture's manifest records
    a null `retrieved_at` and a null `url`, and `treasury_bill_rates.limitation`
    said 2026 alone lacks a manifest. The promoted sidecars carry a real `url`
    and `retrieved_at`, and every year's export has one.

    The brief named two notes. The third, `availability_provenance.note`, makes
    the first note's claim word for word and would have kept this test red, so
    it was corrected in the same commit rather than exempted -- an exemption
    would have been the defect moved out of sight.

    **Anchored on the sidecars, never on today's wording.** Each sidecar is read
    and keyed by its own `source_id`; a payload with no sidecar is keyed by the
    `source_id` of the sidecars beside it, or by its directory name where there
    are none. Every string anywhere under a source with tracked fixtures is
    prose this test reads. Two claims are checked:

    1. **`null <field>`** is contradicted when every tracked sidecar of that
       source carries `<field>` with a non-null value. A field no sidecar
       carries is not contradicted: the sidecar says nothing about it.
    2. **A manifest is missing** -- "lacks a manifest", "without a manifest",
       "except 2026 has a manifest" and their near spellings -- is contradicted
       when the source has tracked payloads and every one of them has a sidecar.
       It is not narrowed to a year: the payload does not name one, and a
       year-reading rule would be a Treasury rule, not a registry rule.

    What it does not reach, and these are findings rather than omissions:
    numerical claims about a fixture's contents. This block reported
    `nyfed_fr2004.identities[0].eras_note`'s "243 of the tracked extract's 700
    weekly as-of dates" as stale against the promoted export's 1960 as-of dates
    and 244 covered ones. That was a misreading, corrected by A38: the note
    describes `tests/fixtures/snapshots/fr2004/pdposgst_tot_and_components.csv`,
    a different tracked file, on which both figures hold.
    `tests/test_data.py`'s `FR2004ExtractCountProseTests` now recomputes them
    for all three sites that state them. The same field's `tolerance_note` still holds on
    the promoted file: the residual at 2026-08-26 is 5.7e-14 and the globbed
    sum is 492637 against 477607 millions.

    Mutation record, 14 September 2026. Each mutation applied to
    `metadata/sources.json` in a disposable copy under `$HOME` built from
    `git ls-files -z --cached --others --exclude-standard`,
    `PYTHONDONTWRITEBYTECODE=1`, python3 3.9.6 `-B`, this class run with
    `tests/` on the path, then reverted and confirmed byte-identical to the
    mount's file. Unmutated control green before the first and after the last.
    Only this class was run under mutation, so nothing here says whether any
    other test would also have caught them.

    1. **Clause 1, the `nyfed_fr2004` `release_lag.note` sentence put back** --
       "the tracked fixture's manifest records retrieved_on 2026-09-10 with a
       null retrieved_at and a null url". One failure, this test,
       `AssertionError: Lists differ`, naming two contradictions:
       `nyfed_fr2004/release_lag/note: says 'null retrieved_at', but every
       tracked nyfed_fr2004 sidecar carries a non-null retrieved_at`, and the
       same for `'null url'`. `retrieved_on` is not named: no sidecar carries
       that field, so no sidecar contradicts it.
    2. **Clause 2, the `treasury_bill_rates` `limitation` sentence put back** --
       "Only 2026 lacks a manifest, because Treasury's export for the year in
       progress no longer returns the committed bytes." One failure, this test,
       `AssertionError: Lists differ`, naming one contradiction:
       `treasury_bill_rates/limitation: says 'lacks a manifest', but all 9
       tracked treasury_bill_rates payloads have a sidecar`.
    """

    NULL_CLAIM = re.compile(r"\bnull ([a-z][a-z0-9_]*)\b")
    MISSING_MANIFEST_CLAIM = re.compile(
        r"\b(?:lacks?|without|has no|have no|carries no|carry no)"
        r" (?:a |any )?(?:snapshot )?manifest"
        r"|\bexcept \S+ ha(?:s|ve) a (?:snapshot )?manifest",
        re.IGNORECASE,
    )

    @staticmethod
    def tracked_fixtures():
        fixtures = {}
        for directory in sorted(p for p in TRACKED_SNAPSHOTS.iterdir() if p.is_dir()):
            sidecar_paths = sorted(directory.glob("*.manifest.json"))
            sidecars = [json.loads(p.read_text(encoding="utf-8")) for p in sidecar_paths]
            covered = {p.name[: -len(".manifest.json")] for p in sidecar_paths}
            for sidecar in sidecars:
                entry = fixtures.setdefault(
                    sidecar["source_id"], {"sidecars": [], "payloads": [], "bare": []}
                )
                entry["sidecars"].append(sidecar)
            owners = {sidecar["source_id"] for sidecar in sidecars}
            owner = owners.pop() if len(owners) == 1 else directory.name
            for payload in sorted(directory.iterdir()):
                if payload.name.endswith(".manifest.json") or not payload.is_file():
                    continue
                entry = fixtures.setdefault(
                    owner, {"sidecars": [], "payloads": [], "bare": []}
                )
                entry["payloads"].append(payload)
                if payload.name not in covered:
                    entry["bare"].append(payload)
        return fixtures

    @classmethod
    def prose(cls, value, path):
        if isinstance(value, dict):
            for key, item in value.items():
                yield from cls.prose(item, f"{path}/{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                yield from cls.prose(item, f"{path}/{index}")
        elif isinstance(value, str):
            yield path, value

    def test_no_registry_prose_contradicts_a_tracked_sidecar(self):
        registry = json.loads(TRACKED_REGISTRY.read_text(encoding="utf-8"))
        fixtures = self.tracked_fixtures()
        # Not vacuous: a moved fixture root would otherwise pass by reading nothing.
        self.assertTrue(
            any(entry["sidecars"] for entry in fixtures.values()),
            f"no tracked sidecar under {TRACKED_SNAPSHOTS}",
        )

        contradictions = []
        for source_id, entry in sorted(fixtures.items()):
            if source_id not in registry:
                continue
            for path, text in self.prose(registry[source_id], source_id):
                for match in self.NULL_CLAIM.finditer(text):
                    field = match.group(1)
                    if entry["sidecars"] and all(
                        sidecar.get(field) is not None for sidecar in entry["sidecars"]
                    ):
                        contradictions.append(
                            f"{path}: says '{match.group(0)}', but every tracked "
                            f"{source_id} sidecar carries a non-null {field}"
                        )
                for match in self.MISSING_MANIFEST_CLAIM.finditer(text):
                    if entry["payloads"] and not entry["bare"]:
                        contradictions.append(
                            f"{path}: says '{match.group(0)}', but all "
                            f"{len(entry['payloads'])} tracked {source_id} payloads "
                            "have a sidecar"
                        )

        self.assertEqual(contradictions, [], "\n".join(contradictions))


TRACKED_RUNS = REPO_ROOT / "docs" / "runs"


class CandidateColumnPairingRecordTests(unittest.TestCase):
    """A42: four candidate columns priced, and why the paired-evidence gate was not built.

    Written 14 September 2026 against the registry and the records of that day.
    Nothing here builds, declares or scores a column.

    **Half 1 -- the gate each candidate faces.**

    * ON RRP (`RRPONTSYD`) is a revision-policy question, and the answer is
      already on record as *no*. The brief framed it as whether `IOER`-style
      evidence can be assembled. It has been measured, and it refutes the claim:
      `metadata/sources.json`, `fred_macro_latest_vintage.field_release_lags.
      WRESBAL.revision_evidence`, says RRPONTSYD's differences "are not a
      constant ratio: it was restated on 2020-02-19 from 5.149 to 0.095, and on
      2020-11-18 from 0.103 to 0.000 and back to 0.103, so RRPONTSYD remains
      refused" (also `tests/test_baseline.py`, the `on_rrp` refusal docstring).
      A latest-vintage FRED series with measured restatements cannot declare
      `never_revised`. The only route is a point-in-time source of the facility's
      own results, which no source declares: a new-adapter question, unpriced.
    * IORB - EFFR: the IORB leg is priced (`IORB` and `IOER` declare
      `never_revised`, `record_date`, one day). The EFFR leg is `DFF` on the same
      latest-vintage source, with no `field_release_lags` entry, and
      `registry.max_release_lag_days` refuses it with the same message as
      `RRPONTSYD`. A revision-policy question on the `IOER` precedent, with no
      evidence either way in the tree: no `alfred-dff` fixture is tracked.
    * SRF usage / primary credit rate: a new-adapter question. No source in the
      registry covers either; a case-insensitive search for standing repo, SRF,
      primary credit and discount window over `src/`, `metadata/` and `tests/`
      finds nothing.
    * Bill supply net of maturities: already declared. `treasury_auctions` is a
      `record_date` source at zero days, and the tracked refetch
      (`funding_inputs/treasury_auctions`, `issue_date` from 2017-01-03) carries
      `maturity_date` and `total_accepted` on every bill.
      `est_pub_held_mat_by_type_amt` is null only on cash
      management bills, so it cannot stand in for the maturing leg. The adapter
      reads only `offering_amt` and `soma_accepted` today, so it needs adapter
      work and a `contract.FEATURE_FIELDS` column (human-owned), but no new
      source and no new lag. The brief's "net of settlement" is read here as net
      of maturing bills; a column dated at *announcement* to capture forward
      issuance pressure would be a different, earlier availability basis on this
      source and is the human's declaration, not this one.

    **Half 2 -- the price.** Every published record runs at a six-day purge
    (`derived.purge_days`, the `nyfed_sofr` worst case). `max_release_lag_days`
    on the real registry, over the four-feature declaration's fields plus the
    candidate's: `treasury_auctions.treasury_settlement_bill` leaves it at six;
    `DFF`, given an in-memory copy of `IOER`'s declaration (the file is not
    edited), leaves it at six; `RRPONTSYD` and bare `DFF` are refused;
    `nyfed_fr2004.PDPOSGST-TOT`, for comparison, moves it to eleven. So neither
    priceable candidate moves the fold grid. `scripts/purge_availability_audit.py`
    could not be run: its default panel, `data/processed/funding_panel.csv`, is
    gitignored and absent from this worktree. Span: `DFF` has a value on every
    weekday of the published panel span, 2018-04-03 to 2026-09-03; net bill
    supply needs issues up to a year before the panel starts, which the 2017
    refetch covers (cash management bills are shorter). Ranking, which reverses
    the order named: net bill supply (build only once a paired record can be
    published for it), IORB - EFFR (build only if ALFRED vintages of `DFF` show
    no restatement -- a human fetch), SRF / primary credit (do not build until a
    source is declared), ON RRP (do not build from FRED; the evidence refutes it).

    **Half 3 -- the gate was not built, because the records do not pair.** The
    brief asked for a test failing when a column in a record's
    `declaration.features` has no sibling record that is the same configuration
    with that column absent. Anchored on `docs/runs/` that gate cries wolf in
    three ways, each readable from the records:

    1. `spread_bps` is in every record's `declaration.features`, and it is the
       target's own column. It can never be absent, so the gate needs an
       exemption, and the records carry no `target` field to anchor one.
    2. `declaration.features` is the set the purge is sized over, not the set a
       model reads. `backtest_persistence_mh61.json` declares `sofr_volume`,
       `sofr_p25` and `sofr_p75`, and `baseline.fit` takes no regressor at all.
       A persistence record would be flagged for columns it cannot use.
    3. A group ablation is invisible to a per-column gate. The calendar columns
       were scored paired -- `exceedance_gbm_conformal_calendar_mh61.json`
       against `exceedance_gbm_conformal_mh61.json`, same declaration, panel and
       holdout, the three calendar columns absent together -- and a gate asking
       for a sibling missing exactly one column flags all three. This test holds
       that fact.

    The brief's "nine were scored paired" is also not what the records show:
    of the nine columns the rebuild added (DATA_QUALITY_DECISIONS, "The rebuild
    takes all nine"), only the calendar three appear in any record's
    `declaration.features`, and only as that one group. And `built_columns` sits
    at `panel.build_manifest.built_columns`, not `panel.built_columns`.

    For the gate to be mechanical a record would have to carry, in `declaration`:
    `ablation_of`, naming the sibling record and the columns withheld from it (so
    a group counts for each member and the sibling is named, not inferred by
    matching declarations whose keys differ by record kind); `target`, the column
    that is never ablated; and, in `derived`, the columns the fitted model
    actually consumed, distinct from those the gap was sized over.

    **Red here** means a group-ablated column acquired a sibling missing it
    alone, or the group sibling left the view: re-open the gate question, do not
    edit the assertion.

    Mutation record (disposable copy under `$HOME` from `git ls-files`,
    `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`; class control green before and
    after): `docs/runs/exceedance_gbm_conformal_mh61.json` deleted from the copy
    -- the calendar columns' paired sibling removed from the test's view, the
    deletion confirmed with `ls` before scoring. This test fails with
    `AssertionError` (`set() == set()`, "no record ablates a column only as part
    of a group").
    """

    @staticmethod
    def _configuration(record):
        declaration = {
            key: value
            for key, value in record["declaration"].items()
            if key != "features"
        }
        return json.dumps(
            {
                "kind": sorted(record),
                "holdout_role": record.get("holdout_role"),
                "declaration": declaration,
                "purge_days": record["derived"]["purge_days"],
                "panel": record["panel"]["sha256"],
            },
            sort_keys=True,
        )

    def test_a_column_scored_paired_as_a_group_has_no_per_column_sibling(self):
        by_configuration = {}
        for path in sorted(TRACKED_RUNS.glob("*.json")):
            record = json.loads(path.read_text(encoding="utf-8"))
            features = (record.get("declaration") or {}).get("features")
            if features is None:
                continue  # comparisons and the build manifest declare per model
            by_configuration.setdefault(self._configuration(record), []).append(
                frozenset(features)
            )

        group_only = set()
        for feature_sets in by_configuration.values():
            for features in feature_sets:
                smaller = [other for other in feature_sets if other < features]
                for column in features:
                    lacking = [other for other in smaller if column not in other]
                    alone = [other for other in lacking if features - other == {column}]
                    if lacking and not alone:
                        group_only.add(column)

        self.assertNotEqual(
            group_only,
            set(),
            "no record ablates a column only as part of a group; a per-column "
            "paired-evidence gate may now be mechanical -- see this docstring",
        )


TRACKED_ALFRED_DFF = (
    REPO_ROOT / "tests" / "fixtures" / "snapshots" / "alfred-dff",
    REPO_ROOT / "tests" / "fixtures" / "snapshots" / "alfred-dff-first-print",
)


class DffFirstPrintRecordTests(unittest.TestCase):
    """A43: `DFF` through the IOER gate. Never revised, and still refused.

    Written 15 September 2026 from ALFRED vintages fetched that day, as ALFRED
    serves them (`alfredgraph.csv?id=DFF&vintage_date=...`). Nothing here
    declares, builds or scores a column.

    **The revision half is clean.** Three vintages, chosen so a restatement had
    somewhere to hide, under `tests/fixtures/snapshots/alfred-dff/`:

    * 2020-01-15 -- before March 2020, so any later restatement of the history
      it carries would show against both later vintages;
    * 2023-06-30 -- spanning the 2020 dislocation and 2021-2023, when
      RRPONTSYD's restatements landed, so the latest vintage is compared with an
      earlier one over those years and not only over the calm ones;
    * 2026-09-01 -- recent.

    `python3 scripts/alfred_vintages.py tests/fixtures/snapshots/alfred-dff/*.csv`
    exits 0: 23939 identical of 23939 shared between 2020-01-15 and each later
    vintage (1954-07-01 to 2020-01-14), and 25201 identical of 25201 between
    2023-06-30 and 2026-09-01 (1954-07-01 to 2023-06-29). With
    `alfred-dff-first-print/` added it still exits 0, and 2020-03-20 -- the
    first print of 2020-03-16 to 2020-03-19, the cut to 0.25 and the 0.20 that
    followed -- agrees with every later vintage on all 24004 shared
    observations. No difference at all, so neither the WRESBAL case (a constant
    ratio, a units rescale) nor the RRPONTSYD case (a restatement) arises.

    **The lag half is not.** The brief held that EFFR for a day is published the
    following morning, so a one-day `record_date` lag is the honest floor. That
    is true only of a business day followed by a business day, and DFF is
    `calendar_daily`. Consecutive-day vintages under `alfred-dff-first-print/`
    date each observation's first appearance exactly:

    * 2026-08-31 (Mon) first carries 2026-08-28 (Fri): 3 days. 2026-08-30 did not.
    * 2026-09-01 (Tue) first carries 2026-08-29 (Sat), 2026-08-30 (Sun) and
      2026-08-31 (Mon): 3, 2 and 1 days.
    * 2026-09-08 (Tue, after Labor Day) first carries 2026-09-04 (Fri) to
      2026-09-07 (Mon): 4, 3, 2 and 1 days. The 2026-09-07 vintage ends at
      2026-09-03.

    So a one-day declaration would date a Friday's value to Saturday when the
    vintages first show it on Monday, or Tuesday across a holiday: a look-ahead,
    in the direction that leaks. A43 therefore declared nothing. The longest
    measured gap is four days; that is a floor from one holiday weekend, not a
    worst case (an unscheduled market closure could exceed it), and the vintage
    date carries no time of day, so `available_time` is unmeasured too. The
    number was left to the human, as `IORB`'s was.

    A43 also asked, for this case, for DFF's own refusal note in
    `field_release_lags`. The contract cannot hold one:
    `contract.validate_field_release_lag` accepts no block without a basis and
    a revision policy, and a revision-only block would *license* DFF on rows
    rather than refuse it. The refusal was recorded here instead.

    ---

    **A47, 15 September 2026: the declaration, and the number held at both
    ends.**

    Eleonora took the decision A43 handed her. `DFF` is declared `record_date`,
    `never_revised` on the eight vintages above, 16:15, at the floor those
    vintages measure plus `HEADROOM_DAYS` -- one deliberate day above what is
    measured.

    **A44 was sent to write that and refused, correctly.** The assertion then
    read `declared.days >= floor`, which the new number passes and the old
    floor passes too: the extra day would have sat in the registry defended by
    nothing, and a later edit back down to the floor would have passed every
    test in the suite. The assertion is now an *equality* against
    `floor + HEADROOM_DAYS`, so the declaration is red in both directions -- a
    retreat to the floor and a drift a day past it are each a failure -- and
    the decision is legible in the tree rather than only in a report.

    `HEADROOM_DAYS` is the stored decision, not a measurement. Moving it does
    not defeat this guard; it states a different decision, which is exactly what
    the constant exists to make explicit. It is not a mutation target.

    **The extra day is free, and the second test below runs that rather than
    asserting it in prose.** The (source, field) pairs come from
    `derived.fields` of the published funding record -- the eleven pairs behind its nine features, which is what
    the purge was actually sized over. Not from the panel manifest, whose
    `built_columns` is a list of column names with no map to sources, and is a
    different question. At the record's own 16:00 decision time a run reading
    those pairs *and* `DFF` purges exactly what the record already publishes,
    while one day further would not. Measured over the declaration and the
    record as committed: `DFF` alone prices 5, 6 and 7 days at four, five and
    six; beside the published pairs it prices 6, 6 and 7. That is where the
    headroom stopped.

    **Red here** means one of four things, and none of them is an assertion to
    edit: `DFF` declared at something other than the tracked vintages' floor
    plus the stored headroom; those vintages stopping showing a first print
    later than a day; no `DFF` declaration on the source at all, so the
    source-level snapshot refusal prices it instead of this number; or the
    published funding record's purge no longer being what this registry prices
    once `DFF` joins it, which costs history on every run that reads those
    columns.

    Mutation record (disposable copy under `$HOME` from `git ls-files`,
    `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`; class control green before and
    after):

    * A43: `metadata/sources.json` given a `DFF` entry copying `IOER`'s
      declaration -- `record_date`, one day, 16:15, `never_revised`, with
      evidence -- which is the declaration A43's brief asked for. It then failed
      with `AssertionError` (`1 not greater than or equal to 4`). **Re-run under
      A47's equality** (CLAUDE.md: a mutation whose guard changed is re-run): it
      still fails, and now both tests do -- `AssertionError: 5 != 1 : DFF is
      declared 1 days; the tracked vintages measure a 4-day first-print floor
      and Eleonora's decision of 15 September 2026 adds HEADROOM_DAYS=1. ...`,
      and `AssertionError: 6 == 6 : a day beyond DFF's declared lag no longer
      moves the published purge ...`, which is the headroom claim failing
      because at one day the day after it is still free.
    * A47, the retreat to the floor: `DFF`'s `days` set to 4 -- the edit A44
      said the tree could not refuse, and could not, under `>=`.
      `AssertionError: 5 != 4 : DFF is declared 4 days; the tracked vintages
      measure a 4-day first-print floor and Eleonora's decision of 15 September
      2026 adds HEADROOM_DAYS=1. Fewer leaks: an unscheduled closure longer than
      the one Labor Day weekend behind the floor would be dated before it was
      published. More costs a day of purge on every run that reads this column.
      Neither is an assertion to edit`. The second test fails too, with the
      `6 == 6` above.
    * A47, the drift past it: `DFF`'s `days` set to 6.
      `AssertionError: 5 != 6 : DFF is declared 6 days; ...` (same message), and
      the second test fails with `AssertionError: 6 != 7 : declaring DFF at its
      stored lag moves the purge of
      exceedance_gbm_cross_conformal_funding_mh61.json: the headroom is no
      longer free, and taking it costs a day of history on every run that reads
      these columns`. That is the "six is not free" measurement, run.
    * A47, the removal: the `DFF` entry deleted from `field_release_lags`
      entirely, which is the state A43 left, and the state a fallthrough to
      `declared.get(...)` on `None` would have reported as an `AttributeError`.
      Both tests fail with `AssertionError: 'DFF' not found in ['IOER', 'IORB',
      'WRESBAL', 'WTREGEN'] : fred_macro_latest_vintage declares no DFF release
      lag. Eleonora declared one on 15 September 2026; without it the field
      falls back to the source-level snapshot_retrieved_at refusal and this
      number is not in the tree at all`.

    Each mutation applied (the edit was checked to change the entry before the
    run) and each failed; the class control was green before and after all four.
    """

    #: The cushion above the measured first-print floor at which `DFF` is
    #: declared. **Eleonora's decision of 15 September 2026, and a decision
    #: rather than a measurement.** The floor is what the tracked vintages
    #: happen to show -- four days, from one Labor Day weekend -- and a floor is
    #: not a proven worst case: an unscheduled closure appended to a holiday
    #: weekend would print later than anything in these fixtures, and a
    #: declaration at the floor would date that value before it existed. This
    #: day is the cushion for exactly that. It stops here rather than a day
    #: higher because the second test below measures that one more day would
    #: move the published funding record's purge, and this one does not.
    #:
    #: Changing this constant is not a mutation of the guard: it states a
    #: different decision, which is what the constant is here to make explicit.
    HEADROOM_DAYS = 1

    SOURCE_ID = "fred_macro_latest_vintage"
    FIELD = "DFF"

    #: The published record whose purge the headroom had to leave alone. Its
    #: `derived.fields` are (source, field) pairs and are what the purge was
    #: sized over; the panel manifest's `built_columns` are column names with no
    #: map to a source, and are not the same question.
    FUNDING_RECORD = "exceedance_gbm_cross_conformal_funding_mh61.json"

    @staticmethod
    def _vintage(path):
        with open(path, newline="", encoding="utf-8") as handle:
            rows = list(csv.reader(handle))
        stamp = re.fullmatch(r"DFF_(\d{8})", rows[0][1].strip()).group(1)
        vintage = date(int(stamp[:4]), int(stamp[4:6]), int(stamp[6:]))
        carried = {
            date.fromisoformat(ref) for ref, value in rows[1:] if value.strip() not in ("", ".")
        }
        return vintage, carried

    def _measured_floor(self):
        vintages = sorted(
            self._vintage(path)
            for directory in TRACKED_ALFRED_DFF
            for path in directory.glob("DFF_*.csv")
        )
        self.assertGreaterEqual(len(vintages), 2, f"no DFF vintages under {TRACKED_ALFRED_DFF}")

        # An observation absent from one vintage and present in the next was
        # first published after the earlier vintage date: a lower bound on its
        # lag, exact when the two vintages are a day apart.
        floor = max(
            (earlier + timedelta(days=1) - ref).days
            for (earlier, before), (_later, after) in zip(vintages, vintages[1:])
            for ref in after - before
        )
        self.assertGreater(floor, 1, "no tracked DFF vintage shows a first print later than a day")
        return floor

    def _declaration(self, registry):
        field_lags = registry[self.SOURCE_ID].get("field_release_lags") or {}
        # Against the sorted keys, not the mapping: a missing declaration should
        # name itself, not print four notes at the reader.
        self.assertIn(
            self.FIELD,
            sorted(field_lags),
            f"{self.SOURCE_ID} declares no {self.FIELD} release lag. Eleonora "
            f"declared one on 15 September 2026; without it the field falls back "
            f"to the source-level snapshot_retrieved_at refusal and this number "
            f"is not in the tree at all",
        )
        return field_lags[self.FIELD]

    def test_dff_is_declared_at_its_measured_first_print_plus_stored_headroom(self):
        floor = self._measured_floor()
        registry = json.loads(TRACKED_REGISTRY.read_text(encoding="utf-8"))
        declared = self._declaration(registry)

        # Equality, not a lower bound: a lower bound leaves the headroom day
        # undefended upward and the floor still passing, which is what A44
        # refused to commit.
        self.assertEqual(
            floor + self.HEADROOM_DAYS,
            declared.get("days"),
            f"{self.FIELD} is declared {declared.get('days')!r} days; the tracked "
            f"vintages measure a {floor}-day first-print floor and Eleonora's "
            f"decision of 15 September 2026 adds HEADROOM_DAYS="
            f"{self.HEADROOM_DAYS}. Fewer leaks: an unscheduled closure longer "
            f"than the one Labor Day weekend behind the floor would be dated "
            f"before it was published. More costs a day of purge on every run "
            f"that reads this column. Neither is an assertion to edit",
        )

    def test_the_declared_dff_headroom_costs_the_published_funding_run_nothing(self):
        registry = json.loads(TRACKED_REGISTRY.read_text(encoding="utf-8"))
        declared = self._declaration(registry)

        record = json.loads((TRACKED_RUNS / self.FUNDING_RECORD).read_text(encoding="utf-8"))
        hour, minute = record["declaration"]["decision_time"].split(":")
        decision_time = time(int(hour), int(minute))
        published = [tuple(name.split(".", 1)) for name in record["derived"]["fields"]]
        with_dff = published + [(self.SOURCE_ID, self.FIELD)]

        # What the record was published at, still priced by this registry.
        without = max_release_lag_days(registry, published, decision_time=decision_time)
        self.assertEqual(record["derived"]["purge_days"], without, self.FUNDING_RECORD)

        self.assertEqual(
            without,
            max_release_lag_days(registry, with_dff, decision_time=decision_time),
            f"declaring {self.FIELD} at its stored lag moves the purge of "
            f"{self.FUNDING_RECORD}: the headroom is no longer free, and taking "
            f"it costs a day of history on every run that reads these columns",
        )

        # And one day further is not free. This is where the headroom stopped,
        # measured rather than asserted.
        dearer = json.loads(TRACKED_REGISTRY.read_text(encoding="utf-8"))
        dearer[self.SOURCE_ID]["field_release_lags"][self.FIELD] = dict(
            declared, days=declared["days"] + 1
        )
        self.assertNotEqual(
            without,
            max_release_lag_days(dearer, with_dff, decision_time=decision_time),
            f"a day beyond {self.FIELD}'s declared lag no longer moves the "
            f"published purge, so 'the headroom was taken where it was free and "
            f"stopped before it was not' has stopped being true of this registry. "
            f"The note on the declaration must be re-derived, not the assertion",
        )


TRACKED_ALFRED_H41_FIRST_PRINT = (
    REPO_ROOT / "tests" / "fixtures" / "snapshots" / "alfred-h41-first-print"
)


class OnRrpRoutesRecordTests(unittest.TestCase):
    """A45: two routes to ON RRP, priced from fetched evidence. Neither is built.

    Written 15 September 2026 from ALFRED vintages, the Board's H.4.1 archive
    and the New York Fed's markets API, all fetched that day. Nothing here
    declares, builds or scores a column; `on_rrp` stays refused.

    **Route A -- the H.4.1 line. It does not restate; its lag is not one day.**

    1. *The series is `WLRRAOL`*, "Liabilities and Capital: Liabilities: Reverse
       Repurchase Agreements: Others: Wednesday Level", release H.4.1 (FRED
       `rid=20`, Table 1). It is not `WLRRAL`, the H.4.1's *total* reverse-repo
       line: `WLRRAL = WLRRAFOIAL + WLRRAOL` on every observation of the
       2026-09-10 vintages, and `WLRRAFOIAL` is the foreign official and
       international pool (357217 USD millions on 2026-09-02, against 525 in
       `WLRRAOL`), which is not the facility. `WLRRAOL` is the facility, and
       not the Desk's operational series `RRPONTSYD` (FRED `rid=379`, Temporary
       Open Market Operations), because it is a Wednesday *outstanding* level:
       it equals the New York Fed's accepted ON RRP total for that Wednesday to
       the million on every panel-span Wednesday with an operation but two, and
       both are outstanding-versus-accepted: 2019-11-20 is 26097 = 26026 + the
       71 of the 2019-11-19 small value exercise, which matured 2019-11-21;
       2024-10-16 is one million short of the accepted sum, the unsettled
       trade the Desk's note on that exercise records. On holiday Wednesdays
       with no operation it carries the prior operation still outstanding
       (2018-12-05 is the two-day 2018-12-04 operation's 3135).
    2. *It has not restated.* Ten vintages under `alfred-wlrraol/` -- 2019-09-19,
       2020-01-02, 2020-03-26, 2020-11-27, 2021-07-29, 2024-09-26, 2026-09-03,
       2026-09-08, 2026-09-09, 2026-09-10 -- and
       `python3 scripts/alfred_vintages.py tests/fixtures/snapshots/alfred-wlrraol/*.csv`
       exits 0: every pair identical on every shared observation (875 of 875
       from 2002-12-18 between the first and the last; 1137 of 1137 between
       2024-09-26 and 2026-09-10). No units rescale either: unlike `WRESBAL` the
       line has been served in millions throughout. `alfred-wlrral/` and
       `alfred-wlrrafoial/`, the same ten dates, also exit 0.
    3. *The lag.* The Board: "released each Thursday, generally at 4:30 p.m.
       Publication may be shifted to the next business day when the regular
       publication date falls on a federal holiday." Wednesday data, so one
       calendar day in an ordinary week -- and the shift is real. ALFRED
       lists `WLRRAOL` vintages since 2018 on Thursdays, fifteen Fridays and one
       Monday; consecutive-day vintages under `alfred-h41-first-print/` date
       the first appearance exactly, for `WLRRAOL` and `WRESBAL` alike:

       * 2020-12-23 (Wed) is absent from the 2020-12-24 and 2020-12-27 vintages
         and first carried by 2020-12-28 (Mon): **5 days**. The Board's archive
         has `releases/h41/20201228/`, "Release Date: December 28, 2020", for
         the week ended December 23; `releases/h41/20201224/` is a 404.
       * 2025-11-26 (Wed, Thanksgiving week) first carried 2025-11-28 (Fri):
         2 days; `releases/h41/20251128/` exists and `20251127/` is a 404.
       * 2026-09-09 first carried 2026-09-10: 1 day. (The 2026-09-09 vintage
         itself adds no observation.)

       Two days recurs every Thanksgiving and on Thursday holidays (July 4,
       Juneteenth 2025, 2025-01-09, Veterans Day 2021). Five is also
       2014-12-29, before the panel. Five is a floor from history, not a worst
       case: the stated rule allows more if a Thursday closure meets a longer
       run of holidays.
    4. *The price.* An honest declaration is `record_date`, at least 5 days,
       16:30. At the published records' decision time, 16:00, that contributes
       6 -- exactly the six `nyfed_sofr` already imposes, so for a run that
       declared `on_rrp` beside the current nine the purge stays 6 (computed
       with an in-memory copy of the registry; the file is not edited). At
       one day it would contribute 2 and still leave 6. `nyfed_fr2004` moves
       it to 11.

    **Finding outside this block: `WRESBAL` and `WTREGEN` are declared one
    day.** They are H.4.1 lines on the same release. `alfred-h41-first-print/`
    shows `WRESBAL`'s 2020-12-23 first carried on 2020-12-28, as `WLRRAOL`'s
    was, so their `days: 1` and their note ("the lag is one calendar day") are
    shorter than a measured first print, in the direction that leaks. No
    published purge moves -- 6 either way, for the reason above -- but the
    declarations are wrong, and correcting them is the human's decision, not
    this block's. A45 did not pin them; **A46 does, below.**

    ---

    **A46, 15 September 2026: the correction, and the guard over the release.**

    Eleonora took the decision A45 handed her: `WRESBAL` and `WTREGEN` are
    corrected from one day to **five**, the measured floor exactly, and their
    notes now record the holiday shift instead of denying it. Five and not six
    because six is not free: over the nine features
    `docs/runs/exceedance_gbm_cross_conformal_funding_mh61.json` declares, at
    its 16:00 decision time, `max_release_lag_days` is 6 at every lag from 1 to
    5 and 7 at six. `test_the_h41_release_is_declared_at_its_measured_first_print`
    checks that, on the real registry and the published record, so the "the
    correction is free" claim is a run of the code and not a line of the report.

    `DFF` is untouched: its floor is A44's open question and this block does not
    reach into it.

    The guard is no longer about one field. `H41_FIELDS` names the release and
    `NOT_H41_FIELDS` names what is deliberately outside it; together they must
    cover every field `fred_macro_latest_vintage` declares, so a field added to
    this source cannot be swept into -- or quietly out of -- the H.4.1 without a
    line saying which release it comes from.

    **A finding against this block's brief.** The brief calls `IOER` and `IORB`
    "H.15, a different release at a different time". They are not H.15. FRED
    serves both from release `rid=185`, "Interest Rate on Reserve Balances";
    `rid=18` is H.15 Selected Interest Rates, which is where `DFF` comes from
    (fetched 15 September 2026 from `fred.stlouisfed.org/series/<ID>`). The
    exclusion the brief asked for is right and `NOT_H41_FIELDS` makes it; only
    its stated reason was wrong, and the constant carries the measured one.

    **`WTREGEN` has no first-print fixture, and does not need one.** Its
    membership is not measured here, it is the release it comes from, which two
    independent artefacts fix. FRED lists it under `rid=20`, H.4.1 Factors
    Affecting Reserve Balances. And the Board's own
    `releases/h41/20201228/` -- "Release Date: December 28, 2020", for the week
    ended December 23, the release whose lateness this whole correction is
    about -- carries "U.S. Treasury, General Account" at 1,602,407 beside
    "Reserve balances with Federal Reserve Banks" at 3,143,041, which are
    `WTREGEN`'s and `WRESBAL`'s 2020-12-23 values to the million as FRED serves
    them today. The line that was late on 28 December 2020 is the line
    `WTREGEN` copies, so its first print is that release's, whatever ALFRED
    vintage happens to be tracked for it.

    **Route B -- the Desk's operation results. Reachable, not amended in value,
    and its release time is not established.**

    1. *Endpoint.* `https://markets.newyorkfed.org/api/rp/results/search.json?
       startDate=YYYY-MM-DD&endDate=YYYY-MM-DD` returns
       `{"repo": {"operations": [...]}}`, repo and reverse repo together; each
       operation carries `operationId`, `operationDate`, `settlementDate`,
       `maturityDate`, `operationType`, `operationMethod`, `term`,
       `termCalenderDays` (sic), `closeTime`, `releaseTime` (absent before
       2021-09-20), `lastUpdated`, `note`, `totalAmtSubmitted`,
       `totalAmtAccepted` in US dollars, `details` by security type and
       `propositions` by counterparty type. It reaches back at least to the
       facility's September 2013 test operations, so it covers the panel's
       2018-04-02 start. The path
       `rp/reverserepo/all/results/search.json` answers 400 to a date search,
       though its `lastTwoWeeks` and `last/N` siblings answer. Samples as served
       are under `nyfed-rrp-results/`, one operation date each.
    2. *Release time.* The claimed "about 1:15 PM" is the operation's *close*,
       not a publication time: the Desk's FAQ gives the schedule "from 12:45
       p.m. to 1:15 p.m." and says only that "after the completion of a reverse
       repo operation, the Desk publishes a summary of results", with no clock
       time. The one timestamp in the data is `lastUpdated`, a last-write time
       and not a publication time. Across the regular operations since 2018
       with no note and a same-day `lastUpdated`, it runs from 13:15:15 to
       14:38:54 (2021-08-16), median 13:15:50; a delayed operation (2023-07-17,
       closing 14:00) reads 14:43:00; a small value exercise annotated later in
       the day (2024-10-16) reads 16:50:30. So `available_time` cannot be
       established from published artefacts. It is bounded below by 13:15, and
       any number above that is a human decision.
    3. *Amendments.* Tested two ways. (a) Nine reverse-repo records carry a
       `lastUpdated` after their operation date: 2018-12-04, 2019-04-18,
       2020-04-09, 2020-07-02 and 2021-04-01 (all rewritten 2023-09-27),
       2021-09-03 and 2021-09-10 (2021-09-16), 2023-01-05 (2023-01-13, a note
       that $3.6 billion did not settle) and 2022-11-17's exercise
       (2024-11-13). So records *are* touched later, and the FAQ says
       propositions by counterparty type "are added ... each month with data
       lagged by one month". (b) Whether a *value* moved: 35 ALFRED vintages of
       `RRPONTSYD` under `alfred-rrpontsyd/`, 2018-12-31 to 2026-09-15 and
       including one the day before each later rewrite (2021-09-15, 2023-01-12,
       2023-09-26, 2024-11-12), are dated copies of the Desk's numbers. On
       every single-operation day each vintage carries, the vintage equals
       today's `totalAmtAccepted` to the million, none differing -- and that
       covers seven of the nine rewritten records from before their rewrite;
       2018-12-04 and 2019-04-18 are not in `RRPONTSYD` at all, and 2018-12-04
       agrees with the H.4.1's 2018-12-05 level. No accepted amount has been
       amended. One same-day amendment is on record: the 2020-02-19 exercise,
       whose note says its results "were updated at 2:00 PM ET".
    4. *What A42's restatement actually is.* `alfred_vintages.py` over
       `alfred-rrpontsyd/` restates exactly two dates, 2020-02-19 and
       2020-11-18, and both are days with two operations: an early small value
       exercise and the regular operation (95 + 5054 = 5149; 103 + 0 = 103).
       FRED has alternated between the sum and one leg -- 0.095 or 5.149, and
       0.103 or 0.000. It is FRED's aggregation over a two-operation day, not
       the Desk revising a print. `RRPONTSYD` stays refused, since it did
       change, but the refusal's reason is this, and the Desk's own series
       does not have it.
    5. *The price.* A `record_date` source at zero days contributes 0 at 13:20
       or 15:00 against 16:00, and 1 at 17:00; beside the current nine the
       purge stays 6 in every case.
    6. *What the adapter would do.* Fetch
       `rp/results/search.json` in yearly windows (a year is at most 0.6 MB)
       into a `nyfed_on_rrp` snapshot; keep `operationType == "Reverse Repo"`;
       sum `totalAmtAccepted` over *every* reverse-repo operation of the
       `operationDate`, exercises included, because that is what
       `WLRRAOL` agrees with and what FRED got wrong; read neither
       `propositions` (added a month later) nor `note`. A `record_date` source
       like `treasury_auctions`, and the fetch is `fetch_nyfed_reference_rate`'s
       shape (`startDate`/`endDate` JSON from the same host) with a different
       path and a list under `repo.operations` rather than `refRates`. Business
       daily: the panel since 2018-04-02 has 95 weekdays with no operation --
       federal holidays and the 2018-12-05 closure -- and gaps between
       operation dates of up to 4 calendar days. Rule 10 does not apply as it
       stands: `CARRY_FORWARD_COLUMNS` is a weekly carry, and a no-operation
       holiday is not a missed print. Whether the facility balance on a
       holiday is carried (the H.4.1 shows it outstanding) or a hole is the
       human's rule. Its `available_time` is item 2's open question.

    **Recommendation.** Route A is buildable on an adapter that already
    passed the gate, once a human declares at least five days -- and it should
    not be declared before `WRESBAL` and `WTREGEN` are corrected to the same
    number, or three lines of one release will carry two lags. It is weekly.
    Route B is daily and its values are sound, but it is a new adapter with no
    publication time to declare. Route A first.

    **Red here** means one of four things, and none of them is an assertion to
    edit: an H.4.1 field was declared with fewer days than a first print the
    tracked vintages show; those vintages stopped showing a first print later
    than a day; a field appeared on this source that neither constant
    classifies, so nobody has said which release it is on; or the published
    funding record's six-day purge stopped being what the registry prices,
    which is a history-losing change to every run that reads it.

    Mutation record (disposable copy under `$HOME` from `git ls-files`,
    `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`; class control green before and
    after):

    * A45: `metadata/sources.json` given a `WLRRAOL` entry copying `WRESBAL`'s
      declaration -- `record_date`, one day, 16:30, `never_revised`, with
      evidence -- the declaration Route A would make if the H.4.1 schedule were
      taken at its word. The test then failed with `AssertionError`
      (`1 not greater than or equal to 5`). **Re-run under A46's extended
      guard** (CLAUDE.md: a mutation whose guard changed is re-run): it still
      fails, now naming the field -- `AssertionError: 1 not greater than or
      equal to 5 : WLRRAOL is declared 1 days, shorter than the 5-day first
      print the tracked H.4.1 vintages show: rid=20, Table 1, ...`.
    * A46, the correction itself: `WRESBAL`'s `days` set back to `1` fails with
      `AssertionError: 1 not greater than or equal to 5 : WRESBAL is declared
      1 days, shorter than the 5-day first print the tracked H.4.1 vintages
      show: ...`; `WTREGEN`'s set back to `1` fails the same way naming
      `WTREGEN`. Each is the declaration this block corrected, put back.
    * A46, the membership set: `"WSHOMCB"` appended to the source's `fields`,
      a real H.4.1 line nobody has classified. `AssertionError: Items in the
      second set but not the first: 'WSHOMCB' : ['WSHOMCB'] on
      fred_macro_latest_vintage belong to no named release: say which one in
      H41_FIELDS or NOT_H41_FIELDS before declaring a lag`.
    * A46, the purge: `WRESBAL` at **six** days rather than five -- the choice
      the brief rejected. `AssertionError: 6 != 7 :
      exceedance_gbm_cross_conformal_funding_mh61.json was published at a purge
      this registry no longer prices ...`. That is the measurement behind "five
      is free and six is not", run rather than asserted.
    """

    #: Two vintages further apart than this are not a first-print measurement:
    #: an observation between them could have appeared on any day in the gap.
    ADJACENT_DAYS = 7

    SOURCE_ID = "fred_macro_latest_vintage"

    #: The H.4.1 membership set: every field of `SOURCE_ID` that is a line of
    #: the Board's H.4.1, and therefore inherits that release's schedule --
    #: including the holiday shift -- whatever its own vintages happen to show.
    #: One line each for how membership is known. FRED release ids were read
    #: from `fred.stlouisfed.org/series/<ID>` on 15 September 2026; `rid=20` is
    #: "H.4.1 Factors Affecting Reserve Balances".
    H41_FIELDS = {
        "WRESBAL": "rid=20; its 2020-12-23 value 3143041 is the 'Reserve "
        "balances with Federal Reserve Banks' line of the Board's "
        "releases/h41/20201228/ to the million; first-print vintages tracked "
        "under alfred-h41-first-print/",
        "WTREGEN": "rid=20; its 2020-12-23 value 1602407 is the 'U.S. "
        "Treasury, General Account' line of that same 28 December 2020 "
        "release to the million. No first-print fixture of its own: its "
        "membership is the release, not a measurement in this tree",
        "WLRRAOL": "rid=20, Table 1, the 'Others' reverse-repo line; "
        "first-print vintages tracked under alfred-h41-first-print/ show the "
        "same 2020-12-28 first print as WRESBAL (A45)",
        "TREAST": "rid=20, Table 1, Treasury securities held outright, "
        "Wednesday level. Carried by this source and declared no lag, so the "
        "refusal below is what prices it",
    }

    #: Deliberately outside the H.4.1, with the release each is actually on.
    #: Written down rather than left silent so a later declaration cannot be
    #: swept into the wrong release by resembling one.
    NOT_H41_FIELDS = {
        "IOER": "rid=185, 'Interest Rate on Reserve Balances' -- an "
        "administered rate announced ahead of its effective date, not a "
        "weekly balance-sheet line, and NOT H.15",
        "IORB": "rid=185, 'Interest Rate on Reserve Balances' -- same "
        "release as IOER, which it abuts at 2021-07-29, and NOT H.15",
        "DFF": "rid=18, H.15 Selected Interest Rates. This is the release "
        "the H.15 name belongs to",
        "RRPONTSYD": "rid=379, Temporary Open Market Operations -- the Desk's "
        "operation results, not the H.4.1's Wednesday outstanding level",
        "RRPONTSYAWARD": "rid=379, Temporary Open Market Operations",
    }

    #: The published funding record the correction had to leave alone.
    FUNDING_RECORD = "exceedance_gbm_cross_conformal_funding_mh61.json"

    @staticmethod
    def _vintage(path):
        with open(path, newline="", encoding="utf-8") as handle:
            rows = list(csv.reader(handle))
        series, stamp = re.fullmatch(r"(\w+?)_(\d{8})", rows[0][1].strip()).groups()
        vintage = date(int(stamp[:4]), int(stamp[4:6]), int(stamp[6:]))
        carried = {
            date.fromisoformat(ref) for ref, value in rows[1:] if value.strip() not in ("", ".")
        }
        return series, vintage, carried

    def test_the_h41_release_is_declared_at_its_measured_first_print(self):
        by_series = {}
        for path in TRACKED_ALFRED_H41_FIRST_PRINT.glob("*.csv"):
            series, vintage, carried = self._vintage(path)
            by_series.setdefault(series, []).append((vintage, carried))
        self.assertEqual(set(by_series), {"WLRRAOL", "WRESBAL"})
        self.assertLessEqual(set(by_series), set(self.H41_FIELDS))

        floors = {}
        for series, vintages in by_series.items():
            vintages.sort()
            floors[series] = max(
                (earlier + timedelta(days=1) - ref).days
                for (earlier, before), (later, after) in zip(vintages, vintages[1:])
                if (later - earlier).days <= self.ADJACENT_DAYS
                for ref in after - before
            )
        # One release: both lines first appear on the same day.
        self.assertEqual(floors["WLRRAOL"], floors["WRESBAL"])
        # Not hardcoded: a longer first print in the fixtures tightens the
        # floor every H.4.1 field below is held to.
        floor = floors["WLRRAOL"]
        self.assertGreater(floor, 1, "no tracked H.4.1 vintage shows a first print later than a day")

        registry = json.loads(TRACKED_REGISTRY.read_text(encoding="utf-8"))
        source_id = self.SOURCE_ID
        source = registry[source_id]
        field_lags = source.get("field_release_lags") or {}

        # Nothing on this source is on neither list: a new field must be said
        # to be on the H.4.1 or said not to be, with the release it is on.
        classified = set(self.H41_FIELDS) | set(self.NOT_H41_FIELDS)
        unclassified = (set(source.get("fields") or ()) | set(field_lags)) - classified
        self.assertEqual(
            set(),
            unclassified,
            f"{sorted(unclassified)} on {source_id} belong to no named release: "
            "say which one in H41_FIELDS or NOT_H41_FIELDS before declaring a lag",
        )

        # The release, not one field: every H.4.1 line this source declares.
        for field in sorted(self.H41_FIELDS):
            declared = field_lags.get(field)
            if declared is None:
                with self.assertRaisesRegex(
                    RegistryContractError,
                    f"^{source_id}: a snapshot_retrieved_at source is priced from rows only",
                ):
                    max_release_lag_days(
                        registry, [(source_id, field)], decision_time=time(16)
                    )
            else:
                self.assertGreaterEqual(
                    declared.get("days", 0),
                    floor,
                    f"{field} is declared {declared.get('days', 0)} days, shorter than "
                    f"the {floor}-day first print the tracked H.4.1 vintages show: "
                    f"{self.H41_FIELDS[field]}",
                )

        # A46: the correction is free. The published funding record's purge is
        # what this registry prices over the fields that record declares.
        record = json.loads(
            (TRACKED_RUNS / self.FUNDING_RECORD).read_text(encoding="utf-8")
        )
        hour, minute = record["declaration"]["decision_time"].split(":")
        self.assertEqual(
            record["derived"]["purge_days"],
            max_release_lag_days(
                registry,
                [tuple(name.split(".", 1)) for name in record["derived"]["fields"]],
                decision_time=time(int(hour), int(minute)),
            ),
            f"{self.FUNDING_RECORD} was published at a purge this registry no "
            "longer prices: a declaration moved it, which costs history on "
            "every run that reads these columns",
        )


class WlrraolFirstPrintRecordTests(unittest.TestCase):
    """A48: `WLRRAOL` declared at the H.4.1's measured first print, and held there.

    Job 651 priced Route A of `OnRrpRoutesRecordTests` on the merged tree
    (`ed33b566`) in memory, declaring nothing. **Eleonora's ruling, 16 September
    2026: build it, at five days.** This block declares it on
    `fred_macro_latest_vintage` -- a `field_release_lags` entry, a `weekly`
    frequency and membership in `fields` -- and nothing else. No column is
    built: `on_rrp` still maps to `RRPONTSYD` in `contract.py`, which is
    human-owned, and `RRPONTSYD` stays refused.

    **Five is measured, not headroom.** Unlike `DFF`, whose fifth day is a
    stored cushion over a four-day floor, five here is the floor itself:
    `alfred-h41-first-print/` shows `WLRRAOL`'s 2020-12-23 absent from the
    2020-12-24 and 2020-12-27 vintages and first carried by 2020-12-28, exactly
    as `WRESBAL`'s. Re-derived 16 September 2026 from the tracked files, and
    again from the Board's archive, re-fetched that day:
    `releases/h41/20201228/` answers 200, "Release Date: December 28, 2020",
    and its Wednesday-level "Reverse repurchase agreements ... Others" line is
    857, `WLRRAOL`'s 2020-12-23 value; `releases/h41/20201224/` answers 404.
    So the test computes the floor from the fixtures and asserts the
    declaration **equal** to it. No literal 5 appears: a longer first print in
    the fixtures moves the number this declaration is held to.

    **Five is free, six is not.** The published funding record's
    `derived.fields` are eleven `(source, field)` pairs (read from the record,
    not the panel manifest's `built_columns`, which are names with no source).
    At its 16:00 decision time they purge 6. Measured over the committed
    registry, in memory: with `WLRRAOL` beside them the purge is 6 at every lag
    from 0 to 5, 7 at six and 8 at seven; `WLRRAOL` alone prices 1 at zero and
    one more per day. The test checks the record's own pairs, the declared lag
    and a day more. That the pairs are eleven was checked before this block
    wrote anything and is not asserted here: CLAUDE.md keeps counts out of an
    acceptance criterion, and the test prices whatever pairs the record
    declares.

    **A finding against nothing in this tree, and outside this block:**
    `ingest.FRED_MACRO_SERIES`, the list the FRED fetcher requests, did not
    name `WLRRAOL`, so a snapshot fetched then would not have carried the
    series. Closed by A49, which added it and guards the set relation in
    `test_ingest.FredFetchCoversDeclaredFieldsTests`. Building the column is
    not this block.

    **Red here** means one of four things, and none of them is an assertion
    to edit: `WLRRAOL` declared at anything other than the first-print floor
    the tracked H.4.1 vintages show; no `WLRRAOL` declaration, frequency or
    `fields` membership on the source, so the snapshot refusal or the
    frequency check prices it instead of this number; the published funding
    record's purge no longer being what this registry prices; or the declared
    lag moving that record's purge, or a day
    more no longer moving it, so "five is free and six is not" has stopped
    being true and the note must be re-derived.

    Mutation record (disposable copy under `$HOME` from `git ls-files`,
    `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`; control
    `test_registry test_generated_results test_docs_freshness` green before
    and after; each edit checked to change `metadata/sources.json` before the
    run):

    * `WLRRAOL`'s `days` set to 4 -- one short of the holiday shift.
      `AssertionError: 5 != 4 : WLRRAOL is declared 4 days; the tracked H.4.1
      vintages under alfred-h41-first-print/ measure a 5-day first print, and
      Eleonora's decision of 16 September 2026 is that floor exactly. Fewer
      dates a holiday-shifted release before it was published; more costs
      purge nobody decided to pay. Neither is an assertion to edit`.
      `OnRrpRoutesRecordTests` fails too, on its `>=`: `AssertionError: 4 not
      greater than or equal to 5 : WLRRAOL is declared 4 days, shorter than
      the 5-day first print ...`.
    * `WLRRAOL`'s `days` set to 6 -- a cushion the brief refused.
      `AssertionError: 5 != 6 : WLRRAOL is declared 6 days; ...`, the same
      message, and this test is the only failure: A46's `>=` passes six.
    * The `WLRRAOL` entry deleted from `field_release_lags`, the only failure:
      `AssertionError: 'WLRRAOL' not found in ['DFF', 'IOER', 'IORB',
      'WRESBAL', 'WTREGEN'] : fred_macro_latest_vintage declares no WLRRAOL
      release lag. Eleonora decided on 16 September 2026 to build it at the
      H.4.1's measured first print; without it the field falls back to the
      source-level snapshot_retrieved_at refusal and this number is not in the
      tree`. (A46's guard accepts an undeclared H.4.1 field by design.)
    * `WLRRAOL` removed from the source's `fields`:
      `AssertionError: 'WLRRAOL' not found in ['DFF', 'IOER', 'IORB',
      'RRPONTSYAWARD', 'RRPONTSYD', 'TREAST', 'WRESBAL', 'WTREGEN'] : WLRRAOL
      is not in fred_macro_latest_vintage's fields: the declaration Eleonora
      decided on 16 September 2026 is incomplete`. Also red, incidentally:
      `test_generated_results.MilestoneAReproductionTests` with
      `AssertionError: the reproduction did not run: repo_model.cli build
      exited 2`, because `field_frequencies` then names a field `fields` does
      not.

    Each mutation applied and each failed this test with `AssertionError`;
    none was a load or parse error.
    """

    SOURCE_ID = "fred_macro_latest_vintage"
    FIELD = "WLRRAOL"
    FUNDING_RECORD = OnRrpRoutesRecordTests.FUNDING_RECORD

    def _measured_floor(self):
        vintages = sorted(
            OnRrpRoutesRecordTests._vintage(path)[1:]
            for path in TRACKED_ALFRED_H41_FIRST_PRINT.glob(f"{self.FIELD}_*.csv")
        )
        self.assertGreaterEqual(
            len(vintages), 2, f"no {self.FIELD} vintages under {TRACKED_ALFRED_H41_FIRST_PRINT}"
        )
        floor = max(
            (earlier + timedelta(days=1) - ref).days
            for (earlier, before), (later, after) in zip(vintages, vintages[1:])
            if (later - earlier).days <= OnRrpRoutesRecordTests.ADJACENT_DAYS
            for ref in after - before
        )
        self.assertGreater(
            floor, 1, f"no tracked {self.FIELD} vintage shows a first print later than a day"
        )
        return floor

    def test_wlrraol_is_declared_at_its_measured_first_print_and_costs_the_funding_run_nothing(self):
        floor = self._measured_floor()
        registry = json.loads(TRACKED_REGISTRY.read_text(encoding="utf-8"))
        source = registry[self.SOURCE_ID]

        # All three parts of the declaration, each naming itself when absent.
        self.assertIn(
            self.FIELD,
            sorted(source.get("fields") or ()),
            f"{self.FIELD} is not in {self.SOURCE_ID}'s fields: the declaration "
            "Eleonora decided on 16 September 2026 is incomplete",
        )
        self.assertEqual(
            "weekly",
            (source.get("field_frequencies") or {}).get(self.FIELD),
            f"{self.FIELD} is a Wednesday level on the weekly H.4.1",
        )
        field_lags = source.get("field_release_lags") or {}
        self.assertIn(
            self.FIELD,
            sorted(field_lags),
            f"{self.SOURCE_ID} declares no {self.FIELD} release lag. Eleonora "
            "decided on 16 September 2026 to build it at the H.4.1's measured "
            "first print; without it the field falls back to the source-level "
            "snapshot_retrieved_at refusal and this number is not in the tree",
        )
        declared = field_lags[self.FIELD]

        # Equality: fewer leaks a holiday-shifted print, more is a cushion
        # nobody decided on.
        self.assertEqual(
            floor,
            declared.get("days"),
            f"{self.FIELD} is declared {declared.get('days')!r} days; the tracked "
            f"H.4.1 vintages under alfred-h41-first-print/ measure a {floor}-day "
            f"first print, and Eleonora's decision of 16 September 2026 is that "
            f"floor exactly. Fewer dates a holiday-shifted release before it was "
            f"published; more costs purge nobody decided to pay. Neither is an "
            f"assertion to edit",
        )

        record = json.loads((TRACKED_RUNS / self.FUNDING_RECORD).read_text(encoding="utf-8"))
        hour, minute = record["declaration"]["decision_time"].split(":")
        decision_time = time(int(hour), int(minute))
        published = [tuple(name.split(".", 1)) for name in record["derived"]["fields"]]
        with_field = published + [(self.SOURCE_ID, self.FIELD)]

        without = max_release_lag_days(registry, published, decision_time=decision_time)
        self.assertEqual(record["derived"]["purge_days"], without, self.FUNDING_RECORD)
        self.assertEqual(
            without,
            max_release_lag_days(registry, with_field, decision_time=decision_time),
            f"declaring {self.FIELD} at its stored lag moves the purge of "
            f"{self.FUNDING_RECORD}, which costs a day of history on every run "
            "that reads these columns",
        )

        dearer = json.loads(TRACKED_REGISTRY.read_text(encoding="utf-8"))
        dearer[self.SOURCE_ID]["field_release_lags"][self.FIELD] = dict(
            declared, days=declared["days"] + 1
        )
        self.assertNotEqual(
            without,
            max_release_lag_days(dearer, with_field, decision_time=decision_time),
            f"a day beyond {self.FIELD}'s declared lag no longer moves the "
            f"published purge, so 'five is free and six is not' has stopped "
            "being true of this registry. The note on the declaration must be "
            "re-derived, not the assertion",
        )


if __name__ == "__main__":
    unittest.main()
