"""Executable specification for `metadata/events.json`.

Track A owns the file. `CLAUDE.md` is explicit that model-eval must not create
or edit anything under `metadata/`, and must not write a second implementation
of a Track A rule to unblock itself -- so what is here is a spec Track A codes
against, in the form `CLAUDE.md` names: a fixture-level executable one.

Why this file needs a spec at all
---------------------------------

`AGENT_CONTRACT.md`, "Two holdout roles":

    Event window boundaries are frozen in versioned, checksummed
    metadata/events.json (data layer owns the file; model-eval consumes it).
    Boundaries are never constants in evaluator code -- moving a window edge is
    the realistic cherry-pick, not swapping window type.

That last clause is the whole design. Nobody switches a knowledge holdout to a
scoring holdout to flatter a result; it is too visible. What is not visible is
March 2020 starting a week later than it used to, which quietly moves the worst
days out of the scored window and into the training set. The file exists to make
that edit leave a trace, and everything specified below serves that end and no
other.

What the checksum is *of*
-------------------------

This is the one real decision in the spec, and it belongs to whoever consumes
the file, so it is made here and Track A should either adopt it or say why it
is wrong.

A per-window `checksum` that is an arbitrary opaque string pins nothing: an
edit that moves `start` and leaves `checksum` alone yields a document that
still validates, and the field is then decoration that looks like provenance.
For the checksum to detect the edit the contract is worried about, it has to be
a function of the boundaries themselves. So:

    checksum = sha256(json.dumps({name, start, end},
                                 sort_keys=True, separators=(",", ":")))

over exactly those three fields, dates as their ISO strings.
`repo_model.contract.event_window_digest` is the normative implementation --
this file wrote it while `metadata/events.json` was still hypothetical, and it
moved to `contract.py` unchanged under `AGENT_CONTRACT.md`, "It is a shared
shape, so it moves": Track A writes the file and Track B reads it, so the rule
belongs where neither track can edit it and both must import it. What this file
holds is the assertions *through* that function, not a second reading of it.
`ChecksumIntegrityTests` is what checks it does what this prose says.
Moving an edge without recomputing the digest now fails validation; moving an
edge *and* recomputing it changes a value that is in git and in every journal
line that ever scored the old window, which is a trace, which is all a checksum
can honestly buy.

What this spec deliberately does not say
----------------------------------------

**The dates.** No test here asserts when September 2019 or March 2020 begins or
ends. Those are the declaration; they belong to the human and to Track A, and a
model-eval test that pinned them would be exactly the boundaries-as-constants-
in-evaluator-code the contract prohibits, merely relocated into a test file.
The reference fixture uses obviously fictional windows for that reason: it is a
template for the *shape*, and copying its dates into the real file would be a
mistake this file should not make easy. `test_the_reference_dates_are_not_the_
declared_ones` is the tripwire on that.

**The tau family.** The contract puts the stress threshold in `metadata/`,
versioned, but does not say it lives in this file, and guessing its home would
be model-eval deciding Track A's file layout.

How this file signalled when the work landed
--------------------------------------------

Two tests pointed at the real path, doing different jobs:

  * `DeclaredFileTests` skips while the file is absent and runs the full
    validator the moment it exists. This is the test that holds Track A to the
    spec: a malformed file fails it, loudly, with every fault listed at once.
  * `TargetDeclarationTests` was an `expectedFailure` tripwire. A conforming
    file made it an unexpected success, which `unittest` reports as a build
    failure -- the signal to come back here, delete it, and promote
    `DeclaredFileTests` to the plain requirement it would by then be.

That is what happened. The 7 September 2026 trial merge turned the tripwire
green, so it is gone and `DeclaredFileTests` is the requirement. The two were
needed together while the file was hypothetical -- `expectedFailure` cannot tell
"not written yet" from "written wrong", and the skipping test is silent about a
file that never arrives -- but only one of those jobs is still open, and keeping
a fired tripwire would mean a permanently red build.

The residual gap is honest and worth naming: `DeclaredFileTests` skips on a
branch where `metadata/events.json` is absent, which on `feature/model-eval`
alone it is. It is present on `feature/data-layer`, so on `main` after the merge
these tests run unconditionally. The skip is what keeps this branch green in
isolation, not a way for the file to go missing unnoticed.
"""

import io
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from repo_model.contract import (
    EVENT_WINDOW_KEYS,
    event_window_digest,
    validate_event_windows_document,
)
from repo_model.event_eval import (
    EventWindow,
    SplitError,
    load_event_windows,
    load_events_file,
)


REPO_ROOT = Path(__file__).parents[1]
EVENTS_PATH = REPO_ROOT / "metadata" / "events.json"

#: Window names the contract itself names, so requiring them here is not this
#: file inventing a declaration. The *dates* behind them are not specified.
REQUIRED_WINDOWS = ("sep-2019", "mar-2020")

# --------------------------------------------------------------------------
# The reference document
# --------------------------------------------------------------------------

# Deliberately fictional windows. This is a template for the shape of the file
# and nothing else -- see "What this spec deliberately does not say". Copying
# these dates into metadata/events.json would be a bug, and the names are what
# they are so that it would be an obvious one.
REFERENCE_WINDOWS = (
    ("example-alpha", "2001-03-05", "2001-03-09"),
    ("example-beta", "2002-11-18", "2002-11-22"),
)

WELL_FORMED = {
    "version": 1,
    "windows": [
        {
            "name": name,
            "start": start,
            "end": end,
            "checksum": event_window_digest(name, start, end),
        }
        for name, start, end in REFERENCE_WINDOWS
    ],
}


def variant(index=0, **changes):
    """`WELL_FORMED` with one window's keys changed, checksum left alone.

    Leaving it alone is the point for most callers: a spec whose checksum
    followed every edit could not detect one.
    """

    document = json.loads(json.dumps(WELL_FORMED))
    document["windows"][index].update(changes)
    return document


def resealed(index=0, **changes):
    """`variant`, with the edited window's checksum recomputed to match.

    A cherry-pick that did its homework. It validates -- correctly, because a
    checksum cannot detect an edit that updates it -- and the trace it leaves is
    in git and in the journal, not here.
    """

    document = variant(index, **changes)
    window = document["windows"][index]
    window["checksum"] = event_window_digest(window["name"], window["start"], window["end"])
    return document


class ReferenceDocumentTests(unittest.TestCase):
    """The spec accepts the document it holds out as conforming."""

    def test_the_reference_document_validates(self):
        self.assertEqual(validate_event_windows_document(WELL_FORMED), [])

    def test_the_reference_document_survives_a_json_round_trip(self):
        """It is a file on disk in the end, not a Python literal."""

        self.assertEqual(
            validate_event_windows_document(json.loads(json.dumps(WELL_FORMED))), []
        )

    def test_extra_keys_on_a_window_are_permitted(self):
        """Track A may want a rationale or a citation; model-eval ignores them."""

        self.assertEqual(
            validate_event_windows_document(variant(0, rationale="repo spike", source="FRBNY")),
            [],
        )

    def test_the_reference_dates_are_not_the_declared_ones(self):
        """A tripwire against this file quietly becoming the declaration.

        If somebody makes the fixture realistic, the temptation to copy it into
        `metadata/events.json` becomes real, and then model-eval has set the
        boundaries after all.
        """

        for name, _start, _end in REFERENCE_WINDOWS:
            self.assertNotIn(name, REQUIRED_WINDOWS)
            self.assertTrue(name.startswith("example-"))


class RejectedDocumentTests(unittest.TestCase):
    """Each way a document can be wrong, one test each.

    Assertions match on the substance of a message rather than its exact
    wording: Track A reads these when something fails, so the message is part of
    the spec, but not to the comma.
    """

    def assertRejected(self, document, fragment):
        problems = validate_event_windows_document(document)
        self.assertTrue(
            problems, msg=f"expected a problem mentioning {fragment!r}, got none"
        )
        self.assertTrue(
            any(fragment in problem for problem in problems),
            msg=f"no problem mentioned {fragment!r}; got {problems}",
        )

    def test_a_bare_list_is_rejected_as_the_declared_file(self):
        self.assertRejected(WELL_FORMED["windows"], "must be a JSON object")

    def test_a_document_without_a_version_is_rejected(self):
        document = json.loads(json.dumps(WELL_FORMED))
        del document["version"]
        self.assertRejected(document, "no 'version'")

    def test_an_empty_version_is_rejected(self):
        document = json.loads(json.dumps(WELL_FORMED))
        document["version"] = "  "
        self.assertRejected(document, "non-empty int or string")

    def test_a_document_without_windows_is_rejected(self):
        self.assertRejected({"version": 1}, "no 'windows'")

    def test_an_empty_window_list_is_rejected(self):
        self.assertRejected({"version": 1, "windows": []}, "non-empty list")

    def test_a_window_missing_a_required_key_is_rejected(self):
        for key in EVENT_WINDOW_KEYS:
            with self.subTest(missing=key):
                document = json.loads(json.dumps(WELL_FORMED))
                del document["windows"][0][key]
                self.assertRejected(document, f"missing {key}")

    def test_a_non_iso_date_is_rejected(self):
        self.assertRejected(variant(0, start="05/03/2001"), "non-ISO start")

    def test_a_non_string_date_is_rejected(self):
        self.assertRejected(variant(0, start=20010305), "non-string start")

    def test_a_backwards_window_is_rejected(self):
        self.assertRejected(
            resealed(0, start="2001-03-09", end="2001-03-05"), "before it starts"
        )

    def test_an_empty_checksum_is_rejected(self):
        self.assertRejected(variant(0, checksum="   "), "empty checksum")

    def test_a_duplicate_name_is_rejected(self):
        document = json.loads(json.dumps(WELL_FORMED))
        document["windows"][1] = json.loads(json.dumps(document["windows"][0]))
        self.assertRejected(document, "declared twice")

    def test_out_of_order_windows_are_rejected(self):
        document = json.loads(json.dumps(WELL_FORMED))
        document["windows"].reverse()
        self.assertRejected(document, "ascending order")

    def test_overlapping_windows_are_rejected(self):
        """A day in two knowledge holdouts is scored twice."""

        document = json.loads(json.dumps(WELL_FORMED))
        window = {"name": "example-beta", "start": "2001-03-07", "end": "2001-03-20"}
        window["checksum"] = event_window_digest(
            window["name"], window["start"], window["end"]
        )
        document["windows"][1] = window
        self.assertRejected(document, "overlap")

    def test_a_touching_pair_is_rejected_as_overlapping(self):
        """Windows are inclusive at both ends, so a shared edge is a shared day."""

        document = json.loads(json.dumps(WELL_FORMED))
        window = {"name": "example-beta", "start": "2001-03-09", "end": "2001-03-20"}
        window["checksum"] = event_window_digest(
            window["name"], window["start"], window["end"]
        )
        document["windows"][1] = window
        self.assertRejected(document, "overlap")

    def test_all_faults_are_reported_in_one_pass(self):
        """Track A should not fix one key, re-run, and find the next."""

        document = json.loads(json.dumps(WELL_FORMED))
        del document["version"]
        document["windows"][0]["start"] = "not-a-date"
        document["windows"][1]["checksum"] = ""
        self.assertGreaterEqual(len(validate_event_windows_document(document)), 3)


class ChecksumIntegrityTests(unittest.TestCase):
    """The checksum is load-bearing: it is a function of the boundaries."""

    def test_the_digest_is_lowercase_hex_sha256(self):
        digest = event_window_digest("example-alpha", "2001-03-05", "2001-03-09")
        self.assertEqual(len(digest), 64)
        self.assertEqual(digest, digest.lower())
        int(digest, 16)  # raises if it is not hex

    def test_moving_an_edge_without_resealing_fails_validation(self):
        """The cherry-pick the contract names, caught.

        `start` moved by one day and nothing else touched. This is the whole
        reason the checksum is specified as a digest of the boundaries rather
        than as an opaque string.
        """

        problems = validate_event_windows_document(variant(0, start="2001-03-06"))
        self.assertTrue(
            any("does not match its boundaries" in problem for problem in problems),
            msg=f"an edge moved and nothing objected; got {problems}",
        )

    def test_every_edge_move_is_caught(self):
        for key, moved in (("start", "2001-03-04"), ("end", "2001-03-10")):
            with self.subTest(field=key):
                problems = validate_event_windows_document(variant(0, **{key: moved}))
                self.assertTrue(
                    any(
                        "does not match its boundaries" in problem
                        for problem in problems
                    )
                )

    def test_renaming_a_window_without_resealing_fails_validation(self):
        problems = validate_event_windows_document(variant(0, name="example-gamma"))
        self.assertTrue(
            any("does not match its boundaries" in problem for problem in problems)
        )

    def test_a_resealed_edit_validates_and_that_is_the_honest_limit(self):
        """Stated as a test so nobody mistakes the checksum for more than it is.

        Recomputing the digest after moving an edge produces a conforming
        document. It has to: a checksum cannot detect an edit that updates it.
        What it buys is that the value changes, so the edit shows up in a diff
        and disagrees with every journal line that scored the old window. The
        trace is in those two places, not in this validator, and a reviewer who
        expects the file alone to catch a resealed edit expects the wrong thing.
        """

        self.assertEqual(validate_event_windows_document(resealed(0, start="2001-03-06")), [])
        self.assertNotEqual(
            event_window_digest("example-alpha", "2001-03-05", "2001-03-09"),
            event_window_digest("example-alpha", "2001-03-06", "2001-03-09"),
        )

    def test_the_digest_ignores_extra_keys(self):
        """A rationale can be reworded without invalidating the boundaries."""

        self.assertEqual(
            validate_event_windows_document(variant(0, rationale="revised wording")), []
        )


class ConsumerCompatibilityTests(unittest.TestCase):
    """A conforming document must actually drive the evaluator.

    The most valuable assertions in this file. A spec Track A satisfies and
    model-eval still cannot read would be a spec that pinned the wrong thing, so
    the round trip through the real consumer is checked rather than assumed.
    """

    def test_a_conforming_document_loads(self):
        windows = load_event_windows(WELL_FORMED)
        self.assertEqual(
            [(w.name, w.start.isoformat(), w.end.isoformat()) for w in windows],
            list(REFERENCE_WINDOWS),
        )

    def test_loaded_windows_carry_the_declared_checksums(self):
        for window, (name, start, end) in zip(
            load_event_windows(WELL_FORMED), REFERENCE_WINDOWS
        ):
            self.assertEqual(window.checksum, event_window_digest(name, start, end))

    def test_loaded_windows_are_the_type_the_evaluator_requires(self):
        """`evaluate_event_window` takes an `EventWindow` and nothing else."""

        for window in load_event_windows(WELL_FORMED):
            self.assertIsInstance(window, EventWindow)

    def test_the_loader_and_the_validator_agree_on_what_is_broken(self):
        """Both reject the same documents, by different routes.

        They are separate implementations on purpose -- the validator reports
        every fault at once and knows about checksum integrity, the loader
        raises on the first and does not. What must not happen is one accepting
        what the other rejects: then a file passes review here and blows up at
        evaluation time, or worse, the reverse.
        """

        no_checksum = json.loads(json.dumps(WELL_FORMED))
        del no_checksum["windows"][0]["checksum"]
        broken = {
            "missing checksum": no_checksum,
            "backwards": resealed(0, start="2001-03-09", end="2001-03-05"),
            "non-ISO": variant(0, start="05/03/2001"),
        }
        for description, document in broken.items():
            with self.subTest(document=description):
                self.assertTrue(validate_event_windows_document(document))
                with self.assertRaises(SplitError):
                    load_event_windows(document)

    def test_the_loader_catches_the_unchecksummed_edge_move_the_validator_catches(self):
        """The one place the two used to differ, closed.

        This test used to assert the opposite, and the reasoning behind it was
        wrong rather than merely outdated: "`load_event_windows` does not verify
        digests -- it cannot, since it takes a decoded object and has no opinion
        about how the checksum was computed." Taking a decoded object was never
        the obstacle. Having no opinion was, and the opinion existed the whole
        time -- in this file, as the digest Track A's real checksums already
        satisfied. `AGENT_CONTRACT.md`, "Decided: the event-window checksum",
        moved it to `repo_model.contract` so the loader could hold it too.

        What remains between them is reporting, not reach: the validator lists
        every fault, the loader raises on the first. Neither now accepts a
        window the other rejects.
        """

        moved = variant(0, start="2001-03-06")
        self.assertTrue(validate_event_windows_document(moved))
        with self.assertRaisesRegex(SplitError, "does not match its boundaries"):
            load_event_windows(moved)

    def test_the_two_differ_only_in_how_much_they_report(self):
        """The honest remaining difference, stated so it is not mistaken for reach."""

        broken = json.loads(json.dumps(WELL_FORMED))
        del broken["version"]
        broken["windows"][0]["start"] = "2001-03-06"

        self.assertGreaterEqual(len(validate_event_windows_document(broken)), 2)
        with self.assertRaises(SplitError):
            load_event_windows(broken)


class DeclaredFileTests(unittest.TestCase):
    """The real `metadata/events.json`. The requirement, not a placeholder.

    Promoted from tripwire to plain requirement on 7 September 2026, when the
    trial merge showed Track A's file conforming and turned
    `TargetDeclarationTests` into an unexpected success. That class is deleted;
    everything it asserted is asserted here, against the same document, by tests
    that report which fault they found instead of only that something changed.

    Still skips while the file is absent, so this branch is green in isolation.
    The moment the file appears it is held to the full spec, and a malformed one
    fails here with every fault listed at once.

    The assertions are what they were. What changed is the route: each now goes
    through `repo_model.event_eval.load_events_file`, the consumer's own
    path-taking loader, rather than a `json.loads` in `setUp`. A spec that read
    the file its own way was checking a document nothing in `src/` had agreed to
    read, which is the narrower version of the mistake this whole block is
    about. `EVENTS_PATH` is still resolved per call, so `MutationRecordTests`
    can point it elsewhere.
    """

    def setUp(self):
        if not EVENTS_PATH.exists():
            self.skipTest(
                "metadata/events.json does not exist yet; it is Track A's to "
                "write, and it is present on feature/data-layer, so this skip "
                "should not survive the merge"
            )

    def test_the_declared_file_conforms_to_this_spec(self):
        try:
            load_events_file(EVENTS_PATH)
        except json.JSONDecodeError as exc:
            self.fail(f"metadata/events.json is not valid JSON: {exc}")
        except SplitError as exc:
            self.fail(str(exc))

    def test_the_declared_file_loads_into_event_windows(self):
        windows = load_events_file(EVENTS_PATH)
        self.assertTrue(windows)
        for window in windows:
            self.assertIsInstance(window, EventWindow)

    def test_the_declared_file_names_the_windows_the_contract_names(self):
        declared = {window.name for window in load_events_file(EVENTS_PATH)}
        for required in REQUIRED_WINDOWS:
            self.assertIn(
                required,
                declared,
                msg=f"the contract names {required} as a single-evaluation window",
            )

# --------------------------------------------------------------------------
# The mutation record
# --------------------------------------------------------------------------


#: A conforming document that names the windows the contract names, for the
#: mutation record alone. The dates are 1900, which is not a plausible repo
#: market observation and could not be pasted into `metadata/events.json`
#: without somebody noticing -- the same reason `REFERENCE_WINDOWS` is
#: fictional, applied to the one fixture that has to carry the real names.
#: `test_the_record_document_cannot_be_mistaken_for_a_declaration` is the
#: tripwire on that.
RECORD_WINDOWS = (
    ("sep-2019", "1900-01-01", "1900-01-05"),
    ("mar-2020", "1900-02-01", "1900-02-05"),
)


def record_document():
    return {
        "version": 1,
        "windows": [
            {
                "name": name,
                "start": start,
                "end": end,
                "checksum": event_window_digest(name, start, end),
            }
            for name, start, end in RECORD_WINDOWS
        ],
    }


#: The assertions `TargetDeclarationTests` was promoted into.
PROMOTED_TESTS = (
    "test_the_declared_file_conforms_to_this_spec",
    "test_the_declared_file_loads_into_event_windows",
    "test_the_declared_file_names_the_windows_the_contract_names",
)


class MutationRecordTests(unittest.TestCase):
    """The mutation record for the promoted assertions, as assertions.

    `CLAUDE.md` requires a mutation for every new guard, and
    `tests/test_metrics.py` established the form: a record written as prose goes
    stale silently, because the mutation stops being caught and the paragraph
    still says it is.

    What was promoted here is not new code -- `DeclaredFileTests` predates this
    block -- but its status changed. It was one of two tests on the same file,
    backed by an `expectedFailure` tripwire that would fire if it ever went
    quiet. The tripwire is gone, so these three are now the only thing standing
    between a tampered `metadata/events.json` and a green build, and that is
    worth a record.

    Each test names one edit to a conforming document, points `EVENTS_PATH` at
    the result, and asserts exactly which of the three catch it. The negative
    half matters as much as the positive: a resealed edit is *not* caught, by
    design, and recording that keeps the checksum from being mistaken for more
    than it is.

    Re-recorded 7 September 2026, after `load_event_windows` began verifying the
    digest and the three assertions moved onto `load_events_file`. Two entries
    changed, both widening: an unresealed edge move and a missing `version` are
    now caught by all three rather than by the conformance test alone. That is
    the guard doing its job, and it is also a loss of resolution worth stating
    plainly -- once every assertion runs the whole document through one loader,
    a document-level fault fails all three, and *which* of them fired stops
    telling a reader anything about *what* is wrong. The entries that still
    discriminate are the ones where the document is conforming and the fault is
    in what it declares: a resealed edge move (caught by nothing) and a renamed
    or dropped window (caught by the name check alone). Those are the rows this
    record is now carrying.
    """

    def setUp(self):
        self.saved_path = EVENTS_PATH
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.addCleanup(self.restore)

    def restore(self):
        globals()["EVENTS_PATH"] = self.saved_path

    def caught_by(self, payload):
        """Names of the promoted tests that fail against `payload`."""

        path = Path(self.directory.name) / "events.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        globals()["EVENTS_PATH"] = path

        failing = set()
        for name in PROMOTED_TESTS:
            result = unittest.TextTestRunner(
                stream=io.StringIO(), verbosity=0
            ).run(unittest.TestSuite([DeclaredFileTests(name)]))
            if not result.wasSuccessful():
                failing.add(name)
            self.assertEqual(
                len(result.skipped),
                0,
                msg=f"{name} skipped; the record would then be recording nothing",
            )
        return failing

    def assertMutationCaughtBy(self, payload, expected):
        caught = self.caught_by(payload)
        self.assertEqual(
            caught,
            set(expected),
            msg="the mutation record has drifted: caught by "
            f"{sorted(caught)}, recorded as {sorted(expected)}",
        )

    def edited(self, **changes):
        """`record_document()` with window 0 changed, checksum left alone."""

        payload = record_document()
        payload["windows"][0].update(changes)
        return payload

    def test_the_record_document_cannot_be_mistaken_for_a_declaration(self):
        """The tripwire `REFERENCE_WINDOWS` has, for the one fixture that
        cannot use fictional names.

        This document has to carry `sep-2019` and `mar-2020` -- the name check
        is one of the things being recorded -- so the safeguard moves onto the
        dates. If somebody makes these realistic, the temptation to paste them
        into `metadata/events.json` becomes real, and then model-eval has set
        the boundaries after all.
        """

        for name, start, end in RECORD_WINDOWS:
            self.assertIn(name, REQUIRED_WINDOWS)
            self.assertTrue(start.startswith("1900-"))
            self.assertTrue(end.startswith("1900-"))

    def test_the_conforming_document_passes_every_promoted_assertion(self):
        """The control for the whole record."""

        self.assertEqual(self.caught_by(record_document()), set())

    def test_an_edge_moved_without_resealing_is_caught(self):
        """The cherry-pick the contract names.

        "What is not visible is March 2020 starting a week later than it used
        to, which quietly moves the worst days out of the scored window and into
        the training set."

        Was caught by the conformance test alone, because "the loader has no
        opinion about checksums, and the name is untouched". The loader has one
        now -- `repo_model.contract.event_window_digest`, the same rule the
        conformance test applies -- so all three fire. The extra two catch it as
        a refusal to load rather than as a report of what is wrong; the
        conformance test is still the one whose failure names the moved edge.
        """

        self.assertMutationCaughtBy(
            self.edited(start="1900-01-02"),
            {
                "test_the_declared_file_conforms_to_this_spec",
                "test_the_declared_file_loads_into_event_windows",
                "test_the_declared_file_names_the_windows_the_contract_names",
            },
        )

    def test_a_resealed_edge_move_is_not_caught_and_that_is_the_honest_limit(self):
        """Recorded because it is a limit, not an oversight.

        A checksum cannot detect an edit that updates it. What it buys is that
        the value changes, so the edit shows up in a diff and disagrees with
        every journal line that scored the old window. Anyone who expects this
        suite to catch a resealed edit expects the wrong thing, and the place to
        say so is a test rather than a comment.
        """

        payload = self.edited(start="1900-01-02")
        window = payload["windows"][0]
        window["checksum"] = event_window_digest(
            window["name"], window["start"], window["end"]
        )
        self.assertMutationCaughtBy(payload, set())

    def test_a_renamed_window_is_caught_even_when_resealed(self):
        """The name check is what survives a resealing.

        Renaming `sep-2019` to something else -- the shape a "revised
        definition" of an event window would take -- reseals cleanly and passes
        the conformance and loader tests. Only the check against the names the
        contract itself declares sees it.
        """

        payload = record_document()
        window = payload["windows"][0]
        window["name"] = "sep-2019-revised"
        window["checksum"] = event_window_digest(
            window["name"], window["start"], window["end"]
        )
        self.assertMutationCaughtBy(
            payload,
            {"test_the_declared_file_names_the_windows_the_contract_names"},
        )

    def test_a_dropped_window_is_caught(self):
        """A single-evaluation window quietly removed from the file."""

        payload = record_document()
        del payload["windows"][1]
        self.assertMutationCaughtBy(
            payload,
            {"test_the_declared_file_names_the_windows_the_contract_names"},
        )

    def test_a_missing_version_is_caught(self):
        """The contract requires the file be versioned.

        All three now, for the routing reason rather than a checksum one: the
        version is a property of the document, `load_events_file` validates the
        document before it parses anything, and every assertion goes through it.
        A bare list would fail the same way, which is the point -- a list has
        nowhere to carry a version.
        """

        payload = record_document()
        del payload["version"]
        self.assertMutationCaughtBy(
            payload,
            {
                "test_the_declared_file_conforms_to_this_spec",
                "test_the_declared_file_loads_into_event_windows",
                "test_the_declared_file_names_the_windows_the_contract_names",
            },
        )

    def test_a_malformed_date_is_caught_by_both_the_validator_and_the_loader(self):
        """Where the two agree, which is most places.

        `test_the_loader_and_the_validator_agree_on_what_is_broken` asserts the
        agreement on fixtures; this records that it holds through the real file
        path as well.
        """

        self.assertMutationCaughtBy(
            self.edited(start="01/01/1900"),
            {
                "test_the_declared_file_conforms_to_this_spec",
                "test_the_declared_file_loads_into_event_windows",
                "test_the_declared_file_names_the_windows_the_contract_names",
            },
        )


if __name__ == "__main__":
    unittest.main()
