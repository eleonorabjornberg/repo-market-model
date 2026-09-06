"""Executable specification for `repo_model.registry.max_release_lag_days`.

Track A owns `src/repo_model/registry.py`. It is in Track B's forbidden paths
and CI enforces that, so what is here is a spec Track A codes against, in the
form `CLAUDE.md` names and `tests/test_events_metadata.py` already uses.

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

Nothing here computes a lag
---------------------------

That is the discipline this file is written under, and it shapes how the
expectations below are stated. Every expected value is a **literal integer with
its arithmetic worked out in the surrounding prose**, never a number produced by
a helper in this file. A local conversion function -- even one written "just for
the test" -- would be a second implementation of a Track A rule, and two
implementations of a point-in-time rule agree until they do not.

What *is* here is a shape validator, `validate_release_lag`, which checks that a
declaration is well formed and that its declared invariants hold. Checking that
``worst_case_calendar_days >= days + 5`` is not converting a lag; it is
verifying a bound the contract requires the source to declare. The distinction
is that the validator never answers "how many days is this worth".

Names: which are the contract's and which are proposed
-------------------------------------------------------

From the contract, non-negotiable: `max_release_lag_days`, its three parameters,
`decision_time`, `days`, `worst_case_calendar_days`, `available_time`, and the
three basis names `ref_date`, `record_date`, `snapshot_retrieved_at`.

Proposed by this file, and Track A's to rename: the container key `release_lag`
on a source, and the keys `basis` and `unit` inside it. The contract describes
the rules as "`ref_date` + `business_days`" and "`record_date` +
`calendar_days`" without saying how the pair is spelled in JSON. If Track A
spells it differently, change `FIXTURE_REGISTRY` here and the spec still holds --
what must not change is the arithmetic in `MaxReleaseLagDaysSpecTests`.

One thing the contract does not determine
------------------------------------------

The `snapshot_retrieved_at` rule says `max_release_lag_days` "raises if such a
source is passed without every row carrying `available_at`". The pinned
signature takes `(registry, sources, *, decision_time)` and no rows, so the
function cannot inspect rows and cannot evaluate that condition. Two readings:

  a. It always raises when a snapshot source is named, and the `available_at`
     check lives with the panel loader.
  b. The signature needs a fourth argument, which is a change to a pinned
     interface and therefore a human decision, not Track B's and not Track A's.

This file pins only the half both readings agree on -- that such a source is
never silently worth 0 -- and flags the rest. See
`test_a_snapshot_source_is_never_worth_zero`. **This needs the human's ruling
before Track A implements it.**

Does this spec actually discriminate?
-------------------------------------

An `expectedFailure` that would go green on a wrong implementation is worse than
no spec, so five stand-in implementations of `max_release_lag_days` were
injected at runtime -- into `sys.modules`, never into `src/repo_model/` -- and
the spec run against each:

  * **Conforming.** 9 unexpected successes: the whole spec flips, which is the
    intended red build and the signal to promote these assertions.
  * **Snapshot mapped to 0** instead of raising. Caught -- the one thing both
    readings of the snapshot rule agree on holds.
  * **Maximum taken over the whole registry** rather than the named sources.
    Caught by 5 tests, including the feature-set test, which is the one that
    reports the actual damage: 9 days where 3 was correct, six calendar days of
    training rows deleted from the front of every fold.
  * **`available_time` ignored**, so the record_date rule never adds its day.
    Caught by 3.
  * **`decision_time` given a default.** Caught by 8 -- it is the argument the
    as-of rule exists to make explicit, so nearly everything depends on it.

In every run one real failure also appears: `test_the_declared_registry_is_well_
formed`, reporting that no source in `metadata/sources.json` declares a
`release_lag` at all. That is correct and is the point -- the registry on `main`
has not been updated yet, and the spec says so by name rather than by silence.

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
    analyzed". Run against `metadata/sources.json` as it stands, every one of
    the four sources fails: all four lack `coverage`, `structural_zeros` and
    `structural_zeros_reviewed`, and three carry prose in `fields`
    ("revision indicator", "portfolio holdings", "liquid assets",
    "shareholder flows", "offering amount").

  * **The publication-gap check.** The contract says "a test asserts no observed
    publication gap exceeds the declared bound" in the passive voice, and the
    Ownership list does not mention it, so it was on course to be nobody's. See
    `PublicationGapTests` for why Track B cares: a bound that is too small makes
    every purge sized from it too small, and no test in `repo_model.splits` can
    see that -- the splitter stays correct with respect to a number that was
    already wrong.

How this file signals when the work lands
-----------------------------------------

Same two-part pattern as `tests/test_events_metadata.py`:

  * `RegistryModuleTests` skips while `repo_model.registry` is absent and runs
    the full spec the moment it exists, so a wrong implementation fails loudly.
  * `MaxReleaseLagDaysSpecTests` is `expectedFailure`; a conforming
    implementation turns it into an unexpected success, which `unittest` and CI
    both treat as a build failure. That is the signal to delete it and promote
    the assertions.
"""

import ast
import importlib
import inspect
import sys
import unittest
from datetime import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))


REPO_ROOT = Path(__file__).parents[1]
SPLITS_PATH = REPO_ROOT / "src" / "repo_model" / "splits.py"
EVENT_EVAL_PATH = REPO_ROOT / "src" / "repo_model" / "event_eval.py"

#: The contract's three bases.
BASES = ("ref_date", "record_date", "snapshot_retrieved_at")

#: "at least `days` + 5: a weekend plus up to three consecutive holidays."
WORST_CASE_MARGIN = 5


def registry_module():
    """`repo_model.registry` if Track A has landed it, else None."""

    try:
        return importlib.import_module("repo_model.registry")
    except ImportError:
        return None


# --------------------------------------------------------------------------
# The fixture registry
# --------------------------------------------------------------------------

# Fictional sources. Like tests/test_events_metadata.py, this is a template for
# the shape and not a declaration -- the real registry is metadata/sources.json
# and Track A's to fill in.
#
# Both business-day sources sit exactly on the `days + 5` bound, which is the
# interesting case: one day looser and the invariant is untested, one day
# tighter and it is violated.
FIXTURE_REGISTRY = {
    "daily_rate": {
        "release_lag": {
            "basis": "ref_date",
            "unit": "business_days",
            "days": 1,
            "worst_case_calendar_days": 6,
        }
    },
    "weekly_balance": {
        "release_lag": {
            "basis": "ref_date",
            "unit": "business_days",
            "days": 4,
            "worst_case_calendar_days": 9,
        }
    },
    "morning_filing": {
        "release_lag": {
            "basis": "record_date",
            "unit": "calendar_days",
            "days": 1,
            "available_time": "09:00",
        }
    },
    "evening_filing": {
        "release_lag": {
            "basis": "record_date",
            "unit": "calendar_days",
            "days": 2,
            "available_time": "18:00",
        }
    },
    "vendor_snapshot": {"release_lag": {"basis": "snapshot_retrieved_at"}},
}

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
#                   mapped to 0; passing it raises.
EXPECTED_LAG = {
    "daily_rate": 6,
    "weekly_balance": 9,
    "morning_filing": 1,
    "evening_filing": 3,
}


# --------------------------------------------------------------------------
# Shape validation -- not conversion
# --------------------------------------------------------------------------


def validate_release_lag(entry):
    """Problems with one source's `release_lag` declaration, as a list.

    Checks that the declaration is well formed and that the invariants the
    contract requires a source to declare actually hold. Deliberately does not
    compute, return or imply a number of days -- that is
    `max_release_lag_days`, and it is Track A's.
    """

    problems = []
    if not isinstance(entry, dict):
        return [f"release_lag must be an object, got {type(entry).__name__}"]

    basis = entry.get("basis")
    if basis is None:
        return ["release_lag has no 'basis'"]
    if basis not in BASES:
        return [f"unknown basis {basis!r}; the contract declares one rule per {BASES}"]

    if basis == "snapshot_retrieved_at":
        for forbidden in ("days", "worst_case_calendar_days"):
            if forbidden in entry:
                problems.append(
                    f"a snapshot_retrieved_at source declares {forbidden!r}; it "
                    "contributes no purge, and a day count here invites exactly "
                    "the mapping-to-zero the contract prohibits"
                )
        return problems

    unit = entry.get("unit")
    days = entry.get("days")
    if not isinstance(days, int) or isinstance(days, bool) or days < 0:
        problems.append(f"'days' must be a non-negative int, got {days!r}")
        days = None

    if basis == "ref_date":
        if unit != "business_days":
            problems.append(
                f"a ref_date source must declare unit 'business_days', got {unit!r}"
            )
        bound = entry.get("worst_case_calendar_days")
        if not isinstance(bound, int) or isinstance(bound, bool):
            problems.append(
                "a ref_date + business_days source must declare "
                f"'worst_case_calendar_days', got {bound!r}; until a holiday "
                "calendar exists the conservative bound is declared, not derived"
            )
        elif days is not None and bound < days + WORST_CASE_MARGIN:
            problems.append(
                f"worst_case_calendar_days {bound} is below days + "
                f"{WORST_CASE_MARGIN} ({days + WORST_CASE_MARGIN}); the bound must "
                "cover a weekend plus up to three consecutive holidays"
            )
    elif basis == "record_date":
        if unit != "calendar_days":
            problems.append(
                f"a record_date source must declare unit 'calendar_days', got {unit!r}"
            )
        available = entry.get("available_time")
        if not isinstance(available, str) or not _is_hh_mm(available):
            problems.append(
                f"'available_time' must be an HH:MM string, got {available!r}; the "
                "rule adds a day when it falls after decision_time, which cannot "
                "be evaluated without it"
            )

    return problems


def _is_hh_mm(text):
    try:
        hours, minutes = text.split(":")
        return 0 <= int(hours) <= 23 and 0 <= int(minutes) <= 59
    except (ValueError, AttributeError):
        return False


class ReleaseLagShapeTests(unittest.TestCase):
    """The validator, exercised against the fixture and against each fault.

    These run today and do not depend on Track A. They are what makes the
    fixture trustworthy as a template.
    """

    def assertRejected(self, entry, fragment):
        problems = validate_release_lag(entry)
        self.assertTrue(problems, msg=f"expected a problem mentioning {fragment!r}")
        self.assertTrue(
            any(fragment in problem for problem in problems),
            msg=f"no problem mentioned {fragment!r}; got {problems}",
        )

    def test_every_fixture_source_is_well_formed(self):
        for name, source in FIXTURE_REGISTRY.items():
            with self.subTest(source=name):
                self.assertEqual(validate_release_lag(source["release_lag"]), [])

    def test_an_unknown_basis_is_rejected(self):
        self.assertRejected({"basis": "publication_date"}, "unknown basis")

    def test_a_missing_basis_is_rejected(self):
        self.assertRejected({"days": 2}, "no 'basis'")

    def test_a_business_day_source_must_declare_its_worst_case_bound(self):
        self.assertRejected(
            {"basis": "ref_date", "unit": "business_days", "days": 2},
            "worst_case_calendar_days",
        )

    def test_a_worst_case_bound_below_days_plus_five_is_rejected(self):
        """The margin the contract sets: a weekend plus three holidays."""

        self.assertRejected(
            {
                "basis": "ref_date",
                "unit": "business_days",
                "days": 4,
                "worst_case_calendar_days": 8,
            },
            "below days + 5",
        )

    def test_a_bound_exactly_on_the_margin_is_accepted(self):
        self.assertEqual(
            validate_release_lag(
                {
                    "basis": "ref_date",
                    "unit": "business_days",
                    "days": 4,
                    "worst_case_calendar_days": 9,
                }
            ),
            [],
        )

    def test_a_ref_date_source_measured_in_calendar_days_is_rejected(self):
        self.assertRejected(
            {
                "basis": "ref_date",
                "unit": "calendar_days",
                "days": 2,
                "worst_case_calendar_days": 7,
            },
            "must declare unit 'business_days'",
        )

    def test_a_record_date_source_must_declare_an_available_time(self):
        self.assertRejected(
            {"basis": "record_date", "unit": "calendar_days", "days": 1},
            "available_time",
        )

    def test_a_malformed_available_time_is_rejected(self):
        for bad in ("6pm", "25:00", "16:99", 1600):
            with self.subTest(available_time=bad):
                self.assertRejected(
                    {
                        "basis": "record_date",
                        "unit": "calendar_days",
                        "days": 1,
                        "available_time": bad,
                    },
                    "HH:MM",
                )

    def test_a_snapshot_source_declaring_a_day_count_is_rejected(self):
        """A day count on a snapshot source is the mapping-to-zero in disguise."""

        self.assertRejected(
            {"basis": "snapshot_retrieved_at", "days": 0}, "contributes no purge"
        )

    def test_a_bare_snapshot_source_is_well_formed(self):
        self.assertEqual(validate_release_lag({"basis": "snapshot_retrieved_at"}), [])

    def test_a_negative_day_count_is_rejected(self):
        self.assertRejected(
            {
                "basis": "ref_date",
                "unit": "business_days",
                "days": -1,
                "worst_case_calendar_days": 6,
            },
            "non-negative int",
        )


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
    """`expectedFailure` specs. Each goes red as an unexpected success on landing.

    Every expected number here is worked out by hand in `EXPECTED_LAG` and its
    comment. Nothing in this file computes one.
    """

    @unittest.expectedFailure
    def test_the_signature_is_the_one_the_contract_pins(self):
        from repo_model.registry import max_release_lag_days

        parameters = inspect.signature(max_release_lag_days).parameters
        self.assertEqual(
            list(parameters), ["registry", "sources", "decision_time"]
        )
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

    @unittest.expectedFailure
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

    @unittest.expectedFailure
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

    @unittest.expectedFailure
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

    @unittest.expectedFailure
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

    @unittest.expectedFailure
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

    @unittest.expectedFailure
    def test_a_snapshot_source_is_never_worth_zero(self):
        """The half of the snapshot rule both readings agree on.

        "contributes no purge, and MUST NOT be mapped to zero." A function that
        returned 0 for a snapshot source would hand the splitter a legal-looking
        gap of zero -- exactly the silent failure `purge` has no default in
        order to prevent.

        This asserts only that passing one raises. Whether it *always* raises,
        or only when rows lack `available_at`, is the open question in the module
        docstring: the pinned signature takes no rows, so the function cannot
        evaluate the condition the contract states. That needs the human.
        """

        from repo_model.registry import max_release_lag_days

        with self.assertRaises(Exception):
            max_release_lag_days(
                FIXTURE_REGISTRY, ["vendor_snapshot"], decision_time=DECISION_TIME
            )

    @unittest.expectedFailure
    def test_an_unknown_source_raises_rather_than_being_skipped(self):
        """Skipping it would under-purge, which is the dangerous direction.

        A typo in a source id must not quietly shrink the gap.
        """

        from repo_model.registry import max_release_lag_days

        with self.assertRaises(Exception):
            max_release_lag_days(
                FIXTURE_REGISTRY, ["daily_rate", "typo_source"],
                decision_time=DECISION_TIME,
            )

    @unittest.expectedFailure
    def test_an_empty_source_set_raises_rather_than_returning_zero(self):
        """An empty feature set is a caller bug, and 0 would look like an answer."""

        from repo_model.registry import max_release_lag_days

        with self.assertRaises(Exception):
            max_release_lag_days(FIXTURE_REGISTRY, [], decision_time=DECISION_TIME)


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

    `MaxReleaseLagDaysSpecTests` cannot tell "not written yet" from "written
    wrong"; this can. A malformed implementation fails here with a real diff.
    """

    def setUp(self):
        self.registry = registry_module()
        if self.registry is None:
            self.skipTest(
                "repo_model.registry does not exist yet; it is Track A's to write, "
                "and MaxReleaseLagDaysSpecTests is the tripwire for its arrival"
            )

    def test_the_module_exposes_max_release_lag_days(self):
        self.assertTrue(hasattr(self.registry, "max_release_lag_days"))

    def test_the_fixture_registry_converts_as_specified(self):
        for source, expected in EXPECTED_LAG.items():
            with self.subTest(source=source):
                self.assertEqual(
                    self.registry.max_release_lag_days(
                        FIXTURE_REGISTRY, [source], decision_time=DECISION_TIME
                    ),
                    expected,
                )

    def test_the_declared_registry_is_well_formed(self):
        """Every source in metadata/sources.json, against the shape validator."""

        import json

        path = REPO_ROOT / "metadata" / "sources.json"
        registry = json.loads(path.read_text(encoding="utf-8"))
        offenders = {}
        for name, source in registry.items():
            declaration = source.get("release_lag")
            if declaration is None:
                offenders[name] = ["no release_lag declared"]
                continue
            problems = validate_release_lag(declaration)
            if problems:
                offenders[name] = problems
        self.assertEqual(offenders, {}, msg=f"malformed release_lag: {offenders}")


if __name__ == "__main__":
    unittest.main()
