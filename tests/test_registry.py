import unittest
from datetime import time, timezone

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
        selected = {
            "snapshot": [{"available_at": "2026-01-02T12:00:00Z"}],
            "auction": [],
        }

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


if __name__ == "__main__":
    unittest.main()
