"""Executable specification for `repo_model.registry.max_release_lag_days`.

Track A owns `src/repo_model/registry.py`. It is in Track B's forbidden paths
and CI enforces that, so what is here is a spec Track A codes against, in the
form `CLAUDE.md` names and `tests/test_events_metadata_spec.py` already uses.

Why the conversion is not in splits.py
--------------------------------------

`AGENT_CONTRACT.md`, "Decided: release lag and the purge gap":

    `rolling_origin(dates, min_train, step, purge)` and `evaluate_event_window`
    keep their pinned semantics: `purge` is an integer of calendar days, the
    boundary is `dates[i] + purge < start`, strict. Neither learns about
    calendars, timezones or vintages.

    ...

    `src/repo_model/registry.py`, owned by Track A:

        max_release_lag_days(registry, sources, *, decision_time) -> int

    Track B imports it and passes the result as `purge`. Track B does not
    reimplement it, and does not read `release_lag` directly.

`repo_model.splits` previously carried a TODO proposing the opposite -- a helper
that read ``registry[source]["release_lag"]`` and took a maximum. That was wrong
twice: the key is a structured object rather than a number, so "take the
maximum" was not defined on it, and the judgement involved is about provenance
rather than evaluation. The TODO is gone and this file replaces it.

The shape is imported, not restated
-----------------------------------

An earlier revision of this file carried its own `validate_release_lag`, written
from the contract's prose. Track A wrote one too, from the same prose. Both were
faithful readings; they disagreed on the key name (`unit` versus `calendar`), on
whether a snapshot source carries `days: 0`, and on whether `available_time` is
`HH:MM` or `HH:MM:SS`. The path-level ownership gate could not see any of it,
because neither track had touched a file the other owned.

`AGENT_CONTRACT.md`, "Decided: the `release_lag` schema", settles all three and
makes the shape executable in `src/repo_model/contract.py`, owned by neither
track. This file imports `validate_release_lag`, `validate_registry_release_lags`
and `UNIT_FOR_BASIS` from there rather than reading the prose a second time. A
second reading is what collided, so a second reading is what was deleted.

What survives here is what only Track B can test, and none of it is shape:

  * that `max_release_lag_days` takes the maximum over the *named* sources
    rather than over the whole registry,
  * that each basis converts to the number the contract says it does,
  * that the result is a type `require_purge_days` accepts,
  * that the three silent-zero cases raise instead of returning a number.

Nothing here computes a lag
---------------------------

That is the discipline this file is written under, and it shapes how the
expectations below are stated. Every expected value is a **literal integer with
its arithmetic worked out in the surrounding prose**, never a number produced by
a helper in this file. A local conversion function -- even one written "just for
the test" -- would be a second implementation of a Track A rule, and two
implementations of a point-in-time rule agree until they do not.

Importing the shared validator is not an exception to that rule. It answers "is
this declaration well formed", never "how many days is it worth".

Does this spec actually discriminate?
-------------------------------------

An `expectedFailure` that would go green on a wrong implementation is worse than
no spec, so five stand-in implementations of `max_release_lag_days` were
injected at runtime -- into `sys.modules`, never into `src/repo_model/` -- and
the spec run against each:

  * **Conforming.** The whole spec flips, which is the intended red build and
    the signal to promote these assertions.
  * **Snapshot mapped to 0** instead of raising. Caught.
  * **Maximum taken over the whole registry** rather than the named sources.
    Caught, including by the feature-set test, which is the one that reports the
    actual damage: 9 days where 3 was correct, six calendar days of training rows
    deleted from the front of every fold.
  * **`available_time` ignored**, so the record_date rule never adds its day.
  * **`decision_time` given a default.** Caught nearly everywhere -- it is the
    argument the as-of rule exists to make explicit.

Five of these went green in the 7 September trial merge and have been promoted
out of `expectedFailure` into `RegistryModuleTests`, which is the class that can
tell "not written yet" from "written wrong". Promoting them was not a rename:
three of the five asserted only `assertRaises(Exception)`, and against Track A's
tip at the time every one of them passed for the wrong reason -- the fixture
registry omitted the `timezone` that implementation then demanded, so the call
raised before it ever reached the rule under test. Each promoted test now pairs
its raise with a control call on the same registry that must succeed, so a
registry that is broken outright cannot masquerade as the rule holding.

Two further requirements from the same section
-----------------------------------------------

Beyond the conversion, that contract section carries two more things, and
neither was landing anywhere, so both are pinned here rather than in
`tests/test_contract.py` -- that file is the shared seam and every edit to it is
a review notice in CI, which is friction worth spending only when the assertion
has to live there. These do not.

  * **"Two registry corrections."** `validate_source_corrections` below, with
    fixture tests that run today. `fields` becomes machine field names only with
    prose moving to `coverage`, and `structural_zeros_reviewed` plus
    `reviewed_note` make "reviewed and empty" distinguishable from "not yet
    analyzed". The contract adopted both and assigned them to Track A.

  * **The publication-gap check.** The contract says "a test asserts no observed
    publication gap exceeds the declared bound" in the passive voice, and the
    Ownership list did not mention it, so it was on course to be nobody's. See
    `PublicationGapTests` for why Track B cares: a bound that is too small makes
    every purge sized from it too small, and no test in `repo_model.splits` can
    see that -- the splitter stays correct with respect to a number that was
    already wrong. The contract adopted it too, and it is Track A's.

How this file signals when the work lands
-----------------------------------------

Same two-part pattern as `tests/test_events_metadata_spec.py`:

  * `RegistryModuleTests` skips while `repo_model.registry` is absent and runs
    the full spec the moment it exists, so a wrong implementation fails loudly
    with a real diff rather than as an anonymous unexpected success.
  * `MaxReleaseLagDaysSpecTests` holds what is still unbuilt as
    `expectedFailure`; a conforming implementation turns each into an unexpected
    success, which `unittest` and CI both treat as a build failure. That is the
    signal to move it into `RegistryModuleTests` and give it a control.
"""

import ast
import importlib
import inspect
import io
import json
import sys
import types
import unittest
from datetime import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from repo_model.contract import (
    UNIT_FOR_BASIS,
    validate_registry_release_lags,
    validate_release_lag,
)


REPO_ROOT = Path(__file__).parents[1]
SPLITS_PATH = REPO_ROOT / "src" / "repo_model" / "splits.py"
EVENT_EVAL_PATH = REPO_ROOT / "src" / "repo_model" / "event_eval.py"
SOURCES_PATH = REPO_ROOT / "metadata" / "sources.json"


def registry_module():
    """`repo_model.registry` if Track A has landed it, else None."""

    try:
        return importlib.import_module("repo_model.registry")
    except ImportError:
        return None


# --------------------------------------------------------------------------
# The fixture registry
# --------------------------------------------------------------------------

# Fictional sources. Like tests/test_events_metadata_spec.py, this is a template
# for the shape and not a declaration -- the real registry is
# metadata/sources.json and Track A's to fill in.
#
# Both business-day sources sit exactly on the `days + 5` bound, which is the
# interesting case: one day looser and the invariant is untested, one day
# tighter and it is violated.
#
# Both filings declare the same timezone. That is not incidental: `DECISION_TIME`
# below is a naive wall clock, and a naive time compared against two different
# declared zones is meaningless. One zone keeps the fixture about the day-count
# rule, which is what it is here to exercise.
FIXTURE_TIMEZONE = "America/New_York"

FIXTURE_REGISTRY = {
    "daily_rate": {
        "release_lag": {
            "basis": "ref_date",
            "unit": UNIT_FOR_BASIS["ref_date"],
            "days": 1,
            "worst_case_calendar_days": 6,
        }
    },
    "weekly_balance": {
        "release_lag": {
            "basis": "ref_date",
            "unit": UNIT_FOR_BASIS["ref_date"],
            "days": 4,
            "worst_case_calendar_days": 9,
        }
    },
    "morning_filing": {
        "release_lag": {
            "basis": "record_date",
            "unit": UNIT_FOR_BASIS["record_date"],
            "days": 1,
            "available_time": "09:00",
            "timezone": FIXTURE_TIMEZONE,
        }
    },
    "evening_filing": {
        "release_lag": {
            "basis": "record_date",
            "unit": UNIT_FOR_BASIS["record_date"],
            "days": 2,
            "available_time": "18:00",
            "timezone": FIXTURE_TIMEZONE,
        }
    },
    # `basis` and `note`, and nothing else. No unit, no days, no available_time,
    # and therefore no timezone: a declared-and-never-read zone is how naive
    # times came to be compared across zones in the first place.
    "vendor_snapshot": {
        "release_lag": {
            "basis": "snapshot_retrieved_at",
            "note": "Rows are valid from their snapshot timestamp, which is an "
            "available_at fact about a row rather than a lag on a source.",
        }
    },
}

#: Rows for the snapshot source, each carrying the `available_at` that is the
#: only reason such a source can contribute no purge. Only that field matters
#: here; the rest of the panel schema is Track A's.
SNAPSHOT_ROWS = (
    {"series_id": "vendor_px", "ref_date": "2020-03-16", "available_at": "2020-03-17T09:00:00-04:00"},
    {"series_id": "vendor_px", "ref_date": "2020-03-17", "available_at": "2020-03-18T09:00:00-04:00"},
)

#: The decision time every expectation below is worked against.
DECISION_TIME = time(16, 0)

# Per-source lags at DECISION_TIME, derived by hand from "One rule per basis".
# These are the arithmetic, written out so that nothing in this file computes
# them:
#
#   daily_rate      ref_date + business_days. The declared conservative bound is
#                   used directly, so 6. (days=1, and 1 + 5 = 6, on the bound.)
#   weekly_balance  same rule, so the declared 9. (days=4, 4 + 5 = 9.)
#   morning_filing  record_date + calendar_days, days=1. available_time 09:00 is
#                   not after the 16:00 decision time, so no extra day: 1.
#   evening_filing  record_date + calendar_days, days=2. available_time 18:00 is
#                   after 16:00, so one further day: 2 + 1 = 3.
#   vendor_snapshot snapshot_retrieved_at. Contributes no purge and must not be
#                   mapped to 0; passing it without rows raises.
EXPECTED_LAG = {
    "daily_rate": 6,
    "weekly_balance": 9,
    "morning_filing": 1,
    "evening_filing": 3,
}


class FixtureRegistryTests(unittest.TestCase):
    """The fixture, checked against the shared validator rather than a local one.

    This is what makes the fixture trustworthy as a template. It runs today and
    does not depend on Track A. It deliberately asserts nothing about *shape* in
    its own words: every rule it enforces is `repo_model.contract`'s, so a
    fixture that drifts from the schema fails here instead of quietly teaching
    Track A the wrong thing.
    """

    def test_every_fixture_source_is_well_formed(self):
        for name, source in FIXTURE_REGISTRY.items():
            with self.subTest(source=name):
                self.assertEqual(validate_release_lag(name, source["release_lag"]), [])

    def test_the_fixture_registry_as_a_whole_is_well_formed(self):
        self.assertEqual(validate_registry_release_lags(FIXTURE_REGISTRY), {})

    def test_the_fixture_survives_a_json_round_trip(self):
        """It is a stand-in for a file on disk, not for a Python literal."""

        self.assertEqual(
            validate_registry_release_lags(
                json.loads(json.dumps(FIXTURE_REGISTRY))
            ),
            {},
        )

    def test_the_fixture_exercises_every_basis(self):
        """A template that omitted a basis would under-specify the interface."""

        declared = {
            source["release_lag"]["basis"] for source in FIXTURE_REGISTRY.values()
        }
        self.assertEqual(declared, set(UNIT_FOR_BASIS))

    def test_every_expected_lag_names_a_fixture_source(self):
        """The arithmetic above and the fixture cannot drift apart silently."""

        self.assertLess(set(EXPECTED_LAG), set(FIXTURE_REGISTRY))


# --------------------------------------------------------------------------
# Track B stays out of the conversion
# --------------------------------------------------------------------------


def _non_docstring_strings(path):
    """Every string literal in `path` that is not a docstring.

    Docstrings are excluded because this module's own prose has to be free to
    say `metadata/sources.json` and `release_lag` while explaining why it does
    not read them -- the same reason the fixed-bin ECE scanner tokenizes rather
    than greps. An identifier or a path in live code is the thing that matters.
    """

    tree = ast.parse(path.read_text(encoding="utf-8"))
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(
            node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        ):
            body = getattr(node, "body", None)
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                docstrings.add(id(body[0].value))
    return [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in docstrings
    ]


def _imported_names(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names.add(node.module)
            names.update(alias.name for alias in node.names)
    return names


class TrackBDoesNotReimplementTheConversionTests(unittest.TestCase):
    """The prohibition, enforced rather than promised.

    `CLAUDE.md`: "Never write a second implementation of a Track A rule to
    unblock yourself." The failure mode is not malice, it is convenience --
    a four-line helper that reads the registry and takes a maximum, added to
    keep a backtest running while Track A finishes. It would work, it would
    disagree with `registry.py` in some corner, and nothing would notice.
    """

    def owned_modules(self):
        return {"splits.py": SPLITS_PATH, "event_eval.py": EVENT_EVAL_PATH}

    def test_no_owned_module_reads_the_source_registry(self):
        for name, path in self.owned_modules().items():
            with self.subTest(module=name):
                for literal in _non_docstring_strings(path):
                    self.assertNotIn(
                        "sources.json",
                        literal,
                        msg=f"{name} names metadata/sources.json in live code; the "
                        "registry is Track A's to read",
                    )

    def test_no_owned_module_reaches_for_a_release_lag_field(self):
        for name, path in self.owned_modules().items():
            with self.subTest(module=name):
                for literal in _non_docstring_strings(path):
                    self.assertNotEqual(
                        literal,
                        "release_lag",
                        msg=f"{name} subscripts a release_lag field; the key is a "
                        "structured object and reading it is Track A's job",
                    )

    def test_no_owned_module_imports_registry_yet(self):
        """Not even conditionally.

        A try/except ImportError around it would create a second code path, and
        the branch that runs when the import fails is the one nobody tests.
        """

        for name, path in self.owned_modules().items():
            with self.subTest(module=name):
                for imported in _imported_names(path):
                    self.assertNotIn(
                        "registry",
                        imported,
                        msg=f"{name} imports {imported!r}; repo_model.registry does "
                        "not exist yet and must not be imported until it does",
                    )

    def test_no_owned_module_defines_a_lag_conversion(self):
        for name, path in self.owned_modules().items():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    lowered = node.name.lower()
                    for forbidden in ("release_lag", "lag_days", "max_lag"):
                        with self.subTest(module=name, function=node.name):
                            self.assertNotIn(
                                forbidden,
                                lowered,
                                msg=f"{name} defines {node.name!r}; the conversion "
                                "belongs to repo_model.registry",
                            )

    def test_the_splitter_still_takes_purge_as_a_plain_int(self):
        """The half of this that must *not* change.

        The contract keeps the pinned semantics. If sizing the gap ever moved
        into the splitter, this is what would have to be deleted first.
        """

        from repo_model.splits import require_purge_days, rolling_origin

        self.assertEqual(
            list(inspect.signature(rolling_origin).parameters),
            ["dates", "min_train", "step", "purge"],
        )
        require_purge_days(3)
        with self.assertRaises(Exception):
            require_purge_days(3.0)



# --------------------------------------------------------------------------
# The interface Track A must satisfy
# --------------------------------------------------------------------------


class MaxReleaseLagDaysSpecTests(unittest.TestCase):
    """Arithmetic specs for the completed Track A conversion.

    Every expected number is worked out by hand in `EXPECTED_LAG` and its
    comment. Nothing in this file computes one.
    """

    def test_each_basis_converts_as_the_contract_says(self):
        from repo_model.registry import max_release_lag_days

        for source, expected in EXPECTED_LAG.items():
            with self.subTest(source=source):
                self.assertEqual(
                    max_release_lag_days(
                        FIXTURE_REGISTRY, [source], decision_time=DECISION_TIME
                    ),
                    expected,
                )

    def test_an_available_time_after_the_decision_time_adds_a_day(self):
        """The record_date rule's second clause, isolated.

        `evening_filing` declares days=2 and available_time 18:00. Against a
        16:00 decision time the value is not in hand, so the lag is 3. Against a
        23:00 decision time it is, so the lag is 2. Same source, same registry,
        different decision time -- which is why decision_time is required.
        """

        from repo_model.registry import max_release_lag_days

        self.assertEqual(
            max_release_lag_days(
                FIXTURE_REGISTRY, ["evening_filing"], decision_time=time(16, 0)
            ),
            3,
        )
        self.assertEqual(
            max_release_lag_days(
                FIXTURE_REGISTRY, ["evening_filing"], decision_time=time(23, 0)
            ),
            2,
        )

    def test_the_result_is_the_maximum_over_the_named_sources(self):
        from repo_model.registry import max_release_lag_days

        self.assertEqual(
            max_release_lag_days(
                FIXTURE_REGISTRY,
                ["daily_rate", "morning_filing"],
                decision_time=DECISION_TIME,
            ),
            6,
        )
        self.assertEqual(
            max_release_lag_days(
                FIXTURE_REGISTRY,
                ["weekly_balance", "evening_filing"],
                decision_time=DECISION_TIME,
            ),
            9,
        )

    def test_the_maximum_is_over_the_feature_set_not_the_whole_registry(self):
        """"Purge over the feature set, not the registry", as a number.

        A feature set using only the two filings is worth 3 days. Taking the
        maximum over the whole registry would return 9 and silently delete six
        calendar days of training rows from the front of every fold -- which
        reads as a weak model rather than as a configuration mistake, and that
        is precisely why it is worth a test.
        """

        from repo_model.registry import max_release_lag_days

        feature_set = max_release_lag_days(
            FIXTURE_REGISTRY,
            ["morning_filing", "evening_filing"],
            decision_time=DECISION_TIME,
        )
        self.assertEqual(feature_set, 3)
        self.assertLess(feature_set, max(EXPECTED_LAG.values()))

    def test_the_result_is_an_int_the_splitter_will_accept(self):
        """`require_purge_days` rejects a float and rejects a bool.

        The two ends have to agree on the type or the handoff fails at the call
        site, so the check is written against the real validator rather than
        against `isinstance`.
        """

        from repo_model.registry import max_release_lag_days
        from repo_model.splits import require_purge_days

        purge = max_release_lag_days(
            FIXTURE_REGISTRY, ["daily_rate"], decision_time=DECISION_TIME
        )
        self.assertIsInstance(purge, int)
        self.assertNotIsInstance(purge, bool)
        require_purge_days(purge)


def validate_source_corrections(source):
    """The "Two registry corrections" from the same contract section.

    Separate from `validate_release_lag` because they are about the source entry
    as a whole rather than about its lag declaration, and because they land on a
    different schedule -- a registry can have correct lags and still record an
    unreviewed `structural_zeros` as though it were a finding.
    """

    problems = []
    if not isinstance(source, dict):
        return [f"source must be an object, got {type(source).__name__}"]

    fields = source.get("fields")
    if not isinstance(fields, list) or not fields:
        problems.append("'fields' must be a non-empty list of machine field names")
    else:
        for field in fields:
            if not isinstance(field, str) or " " in field.strip():
                problems.append(
                    f"field {field!r} reads as prose; 'fields' is machine field "
                    "names only, and the identity-subset check is meaningless "
                    "unless it is"
                )
    if "coverage" not in source:
        problems.append(
            "no 'coverage'; human-readable coverage moved out of 'fields' and "
            "has to land somewhere"
        )

    if "structural_zeros" not in source:
        problems.append("no 'structural_zeros'")
    if "structural_zeros_reviewed" not in source:
        problems.append(
            "no 'structural_zeros_reviewed'; an empty structural_zeros is not a "
            "finding, and absence of evidence is not to be recorded as evidence "
            "of absence"
        )
    elif not isinstance(source["structural_zeros_reviewed"], bool):
        problems.append("'structural_zeros_reviewed' must be a bool")
    elif source["structural_zeros_reviewed"] and not str(
        source.get("reviewed_note", "")
    ).strip():
        problems.append(
            "structural_zeros_reviewed is true with no 'reviewed_note'; the note "
            "is what makes the claim checkable"
        )

    return problems


class RegistryCorrectionsTests(unittest.TestCase):
    """The validator for "Two registry corrections", exercised on fixtures.

    Runs today. The corrections are Track A's to apply to
    `metadata/sources.json`; what this pins is what "applied" means, so that
    "reviewed" cannot be recorded by leaving a key empty.
    """

    WELL_FORMED = {
        "fields": ["IORB", "WRESBAL"],
        "coverage": "Reserve balances and the interest-on-reserves rate.",
        "structural_zeros": [],
        "structural_zeros_reviewed": True,
        "reviewed_note": "No structural zeros: both series are strictly positive.",
    }

    def assertRejected(self, source, fragment):
        problems = validate_source_corrections(source)
        self.assertTrue(problems, msg=f"expected a problem mentioning {fragment!r}")
        self.assertTrue(
            any(fragment in problem for problem in problems),
            msg=f"no problem mentioned {fragment!r}; got {problems}",
        )

    def test_a_corrected_source_validates(self):
        self.assertEqual(validate_source_corrections(self.WELL_FORMED), [])

    def test_prose_in_fields_is_rejected(self):
        """Today's registry has "revision indicator" and "portfolio holdings"."""

        self.assertRejected(
            dict(self.WELL_FORMED, fields=["rate", "revision indicator"]),
            "reads as prose",
        )

    def test_a_source_without_coverage_is_rejected(self):
        source = dict(self.WELL_FORMED)
        del source["coverage"]
        self.assertRejected(source, "no 'coverage'")

    def test_an_unreviewed_empty_structural_zeros_is_not_a_finding(self):
        """The correction's whole point.

        An empty list plus no review means "not yet analyzed", and contract test
        5 stays a stand-in for that source. Recording it as a finding would be
        absence of evidence written down as evidence of absence.
        """

        source = dict(self.WELL_FORMED)
        del source["structural_zeros_reviewed"]
        self.assertRejected(source, "not a finding")

    def test_a_review_claim_without_a_note_is_rejected(self):
        self.assertRejected(
            dict(self.WELL_FORMED, reviewed_note="   "), "no 'reviewed_note'"
        )

    def test_an_unreviewed_source_may_omit_the_note(self):
        """"Not yet analyzed" is a legitimate state to be in, honestly recorded."""

        self.assertEqual(
            validate_source_corrections(
                dict(self.WELL_FORMED, structural_zeros_reviewed=False, reviewed_note="")
            ),
            [],
        )


class PublicationGapTests(unittest.TestCase):
    """The one requirement in this contract section nobody was assigned.

    "When the point-in-time panel lands, a test asserts no observed publication
    gap exceeds the declared bound." The contract states it in the passive voice
    and the Ownership list does not mention it, so it was on course to be
    nobody's. It is pinned here because Track B is the consumer of the number
    the bound produces: if a real publication gap exceeds the declared
    `worst_case_calendar_days`, then a purge sized from that declaration is too
    small, and every backtest run behind it has a leak that no test in
    `repo_model.splits` can see -- the splitter is correct with respect to a
    number that was wrong before it arrived.

    Track A owns the panel and the registry, so Track A implements it. If Track A
    would rather site the test in its own suite, delete this class; what must not
    happen is that it exists in neither.
    """

    @unittest.expectedFailure
    def test_no_observed_publication_gap_exceeds_the_declared_bound(self):
        from repo_model.data import load_point_in_time_panel

        registry_path = REPO_ROOT / "metadata" / "sources.json"
        import json

        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        rows = load_point_in_time_panel()

        worst_observed = {}
        for row in rows:
            gap = (row.available_at.date() - row.ref_date).days
            worst_observed[row.series_id] = max(
                worst_observed.get(row.series_id, 0), gap
            )

        for source_id, source in registry.items():
            declaration = source.get("release_lag", {})
            if declaration.get("basis") != "ref_date":
                continue
            bound = declaration["worst_case_calendar_days"]
            for series_id in source["fields"]:
                observed = worst_observed.get(series_id)
                if observed is None:
                    continue
                self.assertLessEqual(
                    observed,
                    bound,
                    msg=f"{series_id} was published {observed} calendar days "
                    f"after its ref_date, but {source_id} declares a worst case "
                    f"of {bound}. Every purge sized from that declaration was "
                    "too small.",
                )


class RegistryModuleTests(unittest.TestCase):
    """The real module, once it exists. Skips until then.

    Two jobs. The first is the one it always had: `MaxReleaseLagDaysSpecTests`
    cannot tell "not written yet" from "written wrong", and this can, because a
    malformed implementation fails here with a real diff instead of as an
    anonymous unexpected success.

    The second is where the five promoted assertions live. The 7 September trial
    merge turned five `expectedFailure` placeholders green, and a placeholder
    that passes is evidence that an interface landed, not evidence that it is
    correct. Three of the five asserted only that a call raised, and against
    Track A's tip at the time every one of them raised for a reason unrelated to
    the rule under test: the fixture registry omitted a `timezone` that
    implementation demanded, so the call failed on the way in.

    So each promoted test now carries a control -- a call on the same registry
    that must *succeed* -- and the controls assert a type rather than a number.
    Sizing the arithmetic is `MaxReleaseLagDaysSpecTests`' job, still red; what
    is asserted here is that the raise came from the rule and not from a registry
    that was broken outright.
    """

    def setUp(self):
        self.registry = registry_module()
        if self.registry is None:
            self.skipTest(
                "repo_model.registry does not exist yet; it is Track A's to write, "
                "and MaxReleaseLagDaysSpecTests is the tripwire for its arrival"
            )

    # -- helpers ----------------------------------------------------------

    def convert(self, sources, *, decision_time=DECISION_TIME):
        return self.registry.max_release_lag_days(
            FIXTURE_REGISTRY, sources, decision_time=decision_time
        )

    def assertConverts(self, sources):
        """The control: this call must succeed and yield a usable purge.

        Deliberately asserts a type and not a number. If it asserted the
        arithmetic, a wrong conversion would fail every promoted test below and
        bury the thing each one is actually about.
        """

        purge = self.convert(sources)
        self.assertIsInstance(purge, int)
        self.assertNotIsInstance(purge, bool)
        return purge

    def assertRaisesDeliberately(self, sources, *, decision_time=DECISION_TIME):
        """Raises, and not by accident.

        The contract says these cases raise; it does not name an exception type,
        so pinning one would be this file inventing an interface. What is pinned
        instead is that the failure is a deliberate rejection rather than the
        implementation falling over: a `TypeError` from a signature mismatch, an
        `AttributeError` from a half-built module or a bare `KeyError` from an
        unguarded lookup would all satisfy `assertRaises(Exception)` while
        telling us nothing about the rule.
        """

        accidents = (TypeError, AttributeError, NameError, KeyError, IndexError)
        with self.assertRaises(Exception) as caught:
            self.convert(sources, decision_time=decision_time)
        self.assertNotIsInstance(
            caught.exception,
            accidents,
            msg=f"raised {type(caught.exception).__name__}: "
            f"{caught.exception}. That is the implementation falling over, not "
            "the rule rejecting the input.",
        )
        return caught.exception

    # -- the module itself ------------------------------------------------

    def test_the_module_exposes_max_release_lag_days(self):
        self.assertTrue(hasattr(self.registry, "max_release_lag_days"))

    def test_the_signature_is_the_one_the_contract_pins(self):
        """Promoted from `expectedFailure`, 7 September 2026.

        `decision_time` is keyword-only and has no default. A default would be a
        silent assumption about when the forecast is made, which is the
        assumption the whole as-of rule exists to make explicit.
        """

        parameters = inspect.signature(
            self.registry.max_release_lag_days
        ).parameters
        self.assertEqual(list(parameters), ["registry", "sources", "decision_time"])
        self.assertIs(
            parameters["decision_time"].kind, inspect.Parameter.KEYWORD_ONLY
        )
        self.assertIs(
            parameters["decision_time"].default,
            inspect.Parameter.empty,
            msg="decision_time acquired a default; that is a silent assumption "
            "about when the forecast is made, which the as-of rule exists to "
            "make explicit",
        )

    def test_the_fixture_registry_converts_as_specified(self):
        for source, expected in EXPECTED_LAG.items():
            with self.subTest(source=source):
                self.assertEqual(self.convert([source]), expected)

    # -- the three silent-zero cases --------------------------------------

    def test_a_snapshot_source_without_rows_is_never_worth_zero(self):
        """Promoted from `expectedFailure`, 7 September 2026.

        "contributes no purge, and MUST NOT be mapped to zero." A function that
        returned 0 here would hand the splitter a legal-looking gap of zero --
        the silent failure `purge` has no default in order to prevent.

        The control is `["daily_rate"]`, a lag-based source in the same registry:
        if that converts, the registry is fine and the raise below is about the
        snapshot rule. Without it this test passed against an implementation
        that rejected the whole fixture for an unrelated reason.
        """

        self.assertConverts(["daily_rate"])
        self.assertRaisesDeliberately(["vendor_snapshot"])
        self.assertRaisesDeliberately({"vendor_snapshot": None})

    def test_a_snapshot_source_with_no_rows_at_all_is_not_vacuously_satisfied(self):
        """"An empty collection satisfies the check vacuously, and vacuous
        satisfaction is not evidence."

        `AGENT_CONTRACT.md`, "An empty source set raises". The only reason a
        snapshot source can contribute no purge is that its rows carry
        `available_at`; a caller supplying no rows has not shown that.
        """

        self.assertConverts(["daily_rate"])
        self.assertRaisesDeliberately({"vendor_snapshot": []})

    def test_a_snapshot_source_with_rows_contributes_no_purge(self):
        """The other half of the rule, and what makes the raise above meaningful.

        Supplied with rows that carry `available_at`, the snapshot source is
        accepted and adds nothing. Asserted as "adds nothing to what the other
        source alone is worth" rather than against a literal, so it holds
        whatever the record_date arithmetic turns out to be.
        """

        alone = self.assertConverts(["morning_filing"])
        with_snapshot = self.convert(
            {"morning_filing": None, "vendor_snapshot": SNAPSHOT_ROWS}
        )
        self.assertEqual(
            with_snapshot,
            alone,
            msg="a snapshot source whose rows carry available_at changed the "
            "purge; it contributes none",
        )

    def test_an_unknown_source_raises_rather_than_being_skipped(self):
        """Promoted from `expectedFailure`, 7 September 2026.

        A typo in a source id must not quietly shrink the gap. Skipping it would
        under-purge, which is the dangerous direction.

        The control is the same call without the typo. The assertion that the
        typo does not merely return the control's value is the substance: an
        implementation that skipped unknown ids would return `daily_rate`'s lag
        and look entirely healthy.
        """

        self.assertConverts(["daily_rate"])
        self.assertRaisesDeliberately(["daily_rate", "typo_source"])
        self.assertRaisesDeliberately(["typo_source", "daily_rate"])
        self.assertRaisesDeliberately(["typo_source"])

    def test_an_empty_source_set_raises_rather_than_returning_zero(self):
        """Promoted from `expectedFailure`, 7 September 2026.

        "An empty feature set is a caller bug, and 0 would look like an answer."
        It is also the likeliest form of the silent zero, because an empty
        feature set is what a partially-wired pipeline produces.

        Both spellings of empty, because the contract accepts both an iterable of
        ids and a source-to-rows mapping, and a guard written against one of them
        leaves the other returning 0.
        """

        self.assertConverts(["daily_rate"])
        self.assertRaisesDeliberately([])
        self.assertRaisesDeliberately({})

    # -- the declared registry --------------------------------------------

    def test_the_declared_registry_is_well_formed(self):
        """Every source in metadata/sources.json, against the shared validator.

        `repo_model.contract`'s validator, not a local reading of the contract's
        prose. That is the whole point of the module: Track A's `registry.py`
        fails closed on a non-empty result from the same function, so the two
        tracks cannot disagree about what conforming means.
        """

        registry = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
        offenders = validate_registry_release_lags(registry)
        self.assertEqual(
            offenders,
            {},
            msg="metadata/sources.json does not conform to the release_lag "
            f"schema: {offenders}",
        )


# --------------------------------------------------------------------------
# The mutation record
# --------------------------------------------------------------------------


def _stand_in_registry(
    *,
    snapshot_worth_zero=False,
    skip_unknown_sources=False,
    empty_set_worth_zero=False,
    decision_time_defaulted=False,
):
    """A stand-in `repo_model.registry`, correct except for the named fault.

    This is the only thing in this file that computes a lag, and it is not a
    source of truth for one: no expectation anywhere is taken from it, and
    `test_the_conforming_stand_in_agrees_with_the_hand_derived_lags` below
    asserts it against `EXPECTED_LAG` rather than the other way round. If the
    two ever disagree, the hand-worked arithmetic wins and this function is the
    thing that is wrong.

    Its job is narrow: a guard is only worth having if some implementation fails
    it, and the way to know is to run one. Each keyword introduces exactly one
    fault, so a test that fires tells us which fault it saw.
    """

    def contribution(source_id, lag, rows, decision_time):
        basis = lag["basis"]
        if basis == "ref_date":
            return lag["worst_case_calendar_days"]
        if basis == "record_date":
            hours, minutes = lag["available_time"].split(":")
            published = time(int(hours), int(minutes))
            return lag["days"] + int(published > decision_time)
        if snapshot_worth_zero:
            return 0
        supplied = None if rows is None else list(rows)
        if not supplied or any(
            row.get("available_at") in (None, "") for row in supplied
        ):
            raise ValueError(
                f"{source_id}: every snapshot row must carry available_at"
            )
        return 0

    def body(registry, sources, decision_time):
        if hasattr(sources, "items"):
            selected = list(sources.items())
        else:
            selected = [(source_id, None) for source_id in sources]
        if not selected and not empty_set_worth_zero:
            raise ValueError("sources must select at least one feature source")

        purge = 0
        for source_id, rows in selected:
            if source_id not in registry:
                if skip_unknown_sources:
                    continue
                raise ValueError(f"unknown source: {source_id}")
            purge = max(
                purge,
                contribution(
                    source_id,
                    registry[source_id]["release_lag"],
                    rows,
                    decision_time,
                ),
            )
        return purge

    if decision_time_defaulted:

        def max_release_lag_days(registry, sources, *, decision_time=DECISION_TIME):
            return body(registry, sources, decision_time)

    else:

        def max_release_lag_days(registry, sources, *, decision_time):
            return body(registry, sources, decision_time)

    module = types.ModuleType("repo_model.registry")
    module.max_release_lag_days = max_release_lag_days
    return module


#: The promoted assertions, and nothing else. `test_the_module_exposes_...` is
#: excluded on purpose: every stand-in exposes the function, so it discriminates
#: nothing and would only pad the record.
PROMOTED_TESTS = (
    "test_the_signature_is_the_one_the_contract_pins",
    "test_the_fixture_registry_converts_as_specified",
    "test_a_snapshot_source_without_rows_is_never_worth_zero",
    "test_a_snapshot_source_with_no_rows_at_all_is_not_vacuously_satisfied",
    "test_a_snapshot_source_with_rows_contributes_no_purge",
    "test_an_unknown_source_raises_rather_than_being_skipped",
    "test_an_empty_source_set_raises_rather_than_returning_zero",
)


class MutationRecordTests(unittest.TestCase):
    """The mutation record for the promoted assertions, as assertions.

    `CLAUDE.md` requires a mutation for every new guard, and
    `tests/test_metrics.py` established the form: a record written as a
    paragraph goes stale silently -- the mutation stops being caught and the
    paragraph still says it is. These re-run the mutations on every suite run,
    so a guard that stops discriminating fails the build.

    The record matters more than usual here. Five of these tests spent the last
    block as `expectedFailure` placeholders, and three of them asserted nothing
    beyond `assertRaises(Exception)`. All five went green in the 7 September
    trial merge, and at least three did so for a reason unrelated to the rule
    they name: Track A's implementation at that tip required a `timezone` key
    the fixture registry did not carry, so the call raised before it reached
    anything. Promoting them without checking would have converted five
    accidents into five assertions that looked like evidence.

    Each test below names one fault, injects a stand-in carrying it, and asserts
    that the tests which should catch it do and the ones which should not do
    not. The negative half is the part that keeps this honest -- a guard that
    fires on every stand-in is not discriminating, it is just broken.
    """

    def setUp(self):
        self.saved = sys.modules.get("repo_model.registry")

    def tearDown(self):
        if self.saved is None:
            sys.modules.pop("repo_model.registry", None)
        else:
            sys.modules["repo_model.registry"] = self.saved

    def caught_by(self, module):
        """Names of the promoted tests that fail against `module`."""

        sys.modules["repo_model.registry"] = module
        failing = set()
        for name in PROMOTED_TESTS:
            result = unittest.TextTestRunner(
                stream=io.StringIO(), verbosity=0
            ).run(unittest.TestSuite([RegistryModuleTests(name)]))
            if not result.wasSuccessful():
                failing.add(name)
        return failing

    def assertMutationCaughtBy(self, module, expected):
        caught = self.caught_by(module)
        self.assertEqual(
            caught,
            set(expected),
            msg="the mutation record has drifted: caught by "
            f"{sorted(caught)}, recorded as {sorted(expected)}",
        )

    def test_the_conforming_stand_in_passes_every_promoted_assertion(self):
        """The control for the whole record.

        If a conforming implementation failed any of these, every "caught"
        below would be meaningless -- the test would be firing on the stand-in
        rather than on the fault.
        """

        self.assertEqual(self.caught_by(_stand_in_registry()), set())

    def test_the_conforming_stand_in_agrees_with_the_hand_derived_lags(self):
        """The stand-in is checked against the arithmetic, not consulted for it.

        `EXPECTED_LAG` is worked out by hand from the contract's prose. This
        asserts the stand-in reproduces it, so that the stand-in cannot become a
        second, quieter source of truth for what a lag is worth.
        """

        module = _stand_in_registry()
        for source, expected in EXPECTED_LAG.items():
            with self.subTest(source=source):
                self.assertEqual(
                    module.max_release_lag_days(
                        FIXTURE_REGISTRY, [source], decision_time=DECISION_TIME
                    ),
                    expected,
                )

    def test_a_snapshot_source_mapped_to_zero_is_caught(self):
        """"contributes no purge, and MUST NOT be mapped to zero."

        Caught by the two tests that pass no usable rows. Not caught by
        `..._with_rows_contributes_no_purge`, and correctly so: supplied with
        rows that carry `available_at`, zero is the right contribution, so that
        test cannot tell the two implementations apart and is not the guard for
        this fault.
        """

        self.assertMutationCaughtBy(
            _stand_in_registry(snapshot_worth_zero=True),
            {
                "test_a_snapshot_source_without_rows_is_never_worth_zero",
                "test_a_snapshot_source_with_no_rows_at_all_is_not_vacuously_satisfied",
            },
        )

    def test_skipping_an_unknown_source_is_caught(self):
        """The dangerous direction: a typo silently shrinks the gap.

        This is the fault the old `assertRaises(Exception)` placeholder was
        least able to see, because an implementation that skips unknown ids
        raises nothing at all and returns a healthy-looking number.
        """

        self.assertMutationCaughtBy(
            _stand_in_registry(skip_unknown_sources=True),
            {"test_an_unknown_source_raises_rather_than_being_skipped"},
        )

    def test_an_empty_source_set_returning_zero_is_caught(self):
        """An empty feature set is a caller bug, and 0 would look like an answer."""

        self.assertMutationCaughtBy(
            _stand_in_registry(empty_set_worth_zero=True),
            {"test_an_empty_source_set_raises_rather_than_returning_zero"},
        )

    def test_a_defaulted_decision_time_is_caught(self):
        """Caught by the signature test alone, which is the whole reason it exists.

        A default makes every call succeed and every number look right; nothing
        that inspects a return value can see it. That it is caught by exactly
        one test is not a weakness of the record, it is what a structural guard
        looks like.
        """

        self.assertMutationCaughtBy(
            _stand_in_registry(decision_time_defaulted=True),
            {"test_the_signature_is_the_one_the_contract_pins"},
        )

    def test_the_promoted_tests_are_not_vacuous_without_their_controls(self):
        """Why each promoted test carries a control call.

        The three raise-based assertions passed in the trial merge against an
        implementation that rejected the fixture registry outright. This
        reproduces that: a stand-in that raises on everything satisfies a bare
        `assertRaises` but must not satisfy these, because each one first
        requires a call on the same registry to succeed.
        """

        module = types.ModuleType("repo_model.registry")

        def raises_on_everything(registry, sources, *, decision_time):
            raise ValueError("release_lag.timezone is required")

        module.max_release_lag_days = raises_on_everything
        caught = self.caught_by(module)
        for name in (
            "test_a_snapshot_source_without_rows_is_never_worth_zero",
            "test_a_snapshot_source_with_no_rows_at_all_is_not_vacuously_satisfied",
            "test_an_unknown_source_raises_rather_than_being_skipped",
            "test_an_empty_source_set_raises_rather_than_returning_zero",
        ):
            with self.subTest(test=name):
                self.assertIn(
                    name,
                    caught,
                    msg="this test still passes against an implementation that "
                    "raises on every input; its control is not doing its job",
                )


if __name__ == "__main__":
    unittest.main()
