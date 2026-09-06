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

over exactly those three fields, dates as their ISO strings. `window_digest`
below is the normative implementation -- Track A should call an equivalent when
writing the file, and `ChecksumIntegrityTests` is what checks the two agree.
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

How this file signals when the work lands
-----------------------------------------

Two tests point at the real path, doing different jobs:

  * `DeclaredFileTests` skips while the file is absent and runs the full
    validator the moment it exists. This is the test that holds Track A to the
    spec: a malformed file fails it, loudly, with every fault listed at once.
  * `TargetDeclarationTests` is `expectedFailure`, the pattern
    `tests/test_contract.py` already uses. A conforming file makes it an
    unexpected success, which `unittest` reports as a build failure -- the
    signal to come back here, delete it, and promote `DeclaredFileTests` to the
    plain requirement it will by then be.

Neither alone is enough: `expectedFailure` cannot tell "not written yet" from
"written wrong", and the skipping test is silent about a file that never
arrives. Together they cover both.
"""

import hashlib
import json
import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from repo_model.event_eval import EventWindow, SplitError, load_event_windows


REPO_ROOT = Path(__file__).parents[1]
EVENTS_PATH = REPO_ROOT / "metadata" / "events.json"

#: Window names the contract itself names, so requiring them here is not this
#: file inventing a declaration. The *dates* behind them are not specified.
REQUIRED_WINDOWS = ("sep-2019", "mar-2020")

#: Keys every window must carry. Extra keys are permitted -- Track A may want a
#: rationale, a source citation, a revision note -- and model-eval ignores them.
REQUIRED_WINDOW_KEYS = ("name", "start", "end", "checksum")


def window_digest(name, start, end):
    """The normative per-window checksum. See "What the checksum is *of*".

    Args:
        name: the window's stable slug.
        start, end: ISO date strings, `YYYY-MM-DD`. Strings rather than `date`
            objects on purpose: the digest must be computable from the file's
            own bytes without a parse step that could normalise something, so
            what is hashed is what is written.

    Returns:
        Lowercase hex SHA-256, 64 characters.
    """

    canonical = json.dumps(
        {"name": name, "start": start, "end": end},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate_events_document(payload):
    """Every way `payload` fails the spec, as a list of readable problems.

    Returns a list rather than raising so a malformed file reports all of its
    faults in one run. Track A should not have to fix one key, re-run, and
    discover the next. An empty list means conforming.
    """

    problems = []

    if not isinstance(payload, dict):
        return [
            "document must be a JSON object with 'version' and 'windows', got "
            f"{type(payload).__name__}; the bare-list form load_event_windows "
            "also accepts is for fixtures, not for the declared file, because a "
            "list has nowhere to carry a version"
        ]

    if "version" not in payload:
        problems.append(
            "document has no 'version'; the contract requires the file be versioned"
        )
    elif not isinstance(payload["version"], (int, str)) or not str(
        payload["version"]
    ).strip():
        problems.append(
            f"'version' must be a non-empty int or string, got {payload['version']!r}"
        )

    entries = payload.get("windows")
    if entries is None:
        problems.append("document has no 'windows'")
        return problems
    if not isinstance(entries, list) or not entries:
        problems.append("'windows' must be a non-empty list")
        return problems

    seen_names = set()
    parsed = []
    for position, entry in enumerate(entries):
        label = f"window {position}"
        if not isinstance(entry, dict):
            problems.append(f"{label} is not an object")
            continue

        missing = [key for key in REQUIRED_WINDOW_KEYS if key not in entry]
        if missing:
            problems.append(f"{label} is missing {', '.join(missing)}")
            continue

        name = entry["name"]
        label = f"window {name!r}"
        if not isinstance(name, str) or not name.strip():
            problems.append(f"{label} has a non-string or empty name")
            continue
        if name in seen_names:
            problems.append(
                f"{label} is declared twice; names identify windows in the journal"
            )
        seen_names.add(name)

        boundaries = {}
        for key in ("start", "end"):
            raw = entry[key]
            if not isinstance(raw, str):
                problems.append(f"{label} has a non-string {key}: {raw!r}")
                continue
            try:
                boundaries[key] = date.fromisoformat(raw)
            except ValueError:
                problems.append(
                    f"{label} has a non-ISO {key}: {raw!r}, expected YYYY-MM-DD"
                )
        if len(boundaries) != 2:
            continue
        if boundaries["end"] < boundaries["start"]:
            problems.append(
                f"{label} ends {boundaries['end']} before it starts {boundaries['start']}"
            )
            continue

        checksum = entry["checksum"]
        if not isinstance(checksum, str) or not checksum.strip():
            problems.append(f"{label} has a non-string or empty checksum")
        else:
            expected = window_digest(name, entry["start"], entry["end"])
            if checksum != expected:
                problems.append(
                    f"{label} checksum {checksum!r} does not match its boundaries; "
                    f"expected {expected!r}. Either an edge moved without the digest "
                    "being recomputed, or the digest is not "
                    "window_digest(name, start, end)"
                )

        parsed.append((name, boundaries["start"], boundaries["end"]))

    ordered = sorted(parsed, key=lambda item: item[1])
    if parsed != ordered:
        problems.append(
            "windows are not in ascending order of start date; the file is read "
            "by humans checking that a boundary has not moved, and an unsorted "
            "list makes that diff harder than it needs to be"
        )
    for earlier, later in zip(ordered, ordered[1:]):
        if later[1] <= earlier[2]:
            problems.append(
                f"windows {earlier[0]!r} ({earlier[1]}..{earlier[2]}) and "
                f"{later[0]!r} ({later[1]}..{later[2]}) overlap; a day in two "
                "knowledge holdouts is scored twice and spends two budgets"
            )

    return problems


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
            "checksum": window_digest(name, start, end),
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
    window["checksum"] = window_digest(window["name"], window["start"], window["end"])
    return document


class ReferenceDocumentTests(unittest.TestCase):
    """The spec accepts the document it holds out as conforming."""

    def test_the_reference_document_validates(self):
        self.assertEqual(validate_events_document(WELL_FORMED), [])

    def test_the_reference_document_survives_a_json_round_trip(self):
        """It is a file on disk in the end, not a Python literal."""

        self.assertEqual(
            validate_events_document(json.loads(json.dumps(WELL_FORMED))), []
        )

    def test_extra_keys_on_a_window_are_permitted(self):
        """Track A may want a rationale or a citation; model-eval ignores them."""

        self.assertEqual(
            validate_events_document(variant(0, rationale="repo spike", source="FRBNY")),
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
        problems = validate_events_document(document)
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
        for key in REQUIRED_WINDOW_KEYS:
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
        window["checksum"] = window_digest(
            window["name"], window["start"], window["end"]
        )
        document["windows"][1] = window
        self.assertRejected(document, "overlap")

    def test_a_touching_pair_is_rejected_as_overlapping(self):
        """Windows are inclusive at both ends, so a shared edge is a shared day."""

        document = json.loads(json.dumps(WELL_FORMED))
        window = {"name": "example-beta", "start": "2001-03-09", "end": "2001-03-20"}
        window["checksum"] = window_digest(
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
        self.assertGreaterEqual(len(validate_events_document(document)), 3)


class ChecksumIntegrityTests(unittest.TestCase):
    """The checksum is load-bearing: it is a function of the boundaries."""

    def test_the_digest_is_lowercase_hex_sha256(self):
        digest = window_digest("example-alpha", "2001-03-05", "2001-03-09")
        self.assertEqual(len(digest), 64)
        self.assertEqual(digest, digest.lower())
        int(digest, 16)  # raises if it is not hex

    def test_moving_an_edge_without_resealing_fails_validation(self):
        """The cherry-pick the contract names, caught.

        `start` moved by one day and nothing else touched. This is the whole
        reason the checksum is specified as a digest of the boundaries rather
        than as an opaque string.
        """

        problems = validate_events_document(variant(0, start="2001-03-06"))
        self.assertTrue(
            any("does not match its boundaries" in problem for problem in problems),
            msg=f"an edge moved and nothing objected; got {problems}",
        )

    def test_every_edge_move_is_caught(self):
        for key, moved in (("start", "2001-03-04"), ("end", "2001-03-10")):
            with self.subTest(field=key):
                problems = validate_events_document(variant(0, **{key: moved}))
                self.assertTrue(
                    any(
                        "does not match its boundaries" in problem
                        for problem in problems
                    )
                )

    def test_renaming_a_window_without_resealing_fails_validation(self):
        problems = validate_events_document(variant(0, name="example-gamma"))
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

        self.assertEqual(validate_events_document(resealed(0, start="2001-03-06")), [])
        self.assertNotEqual(
            window_digest("example-alpha", "2001-03-05", "2001-03-09"),
            window_digest("example-alpha", "2001-03-06", "2001-03-09"),
        )

    def test_the_digest_ignores_extra_keys(self):
        """A rationale can be reworded without invalidating the boundaries."""

        self.assertEqual(
            validate_events_document(variant(0, rationale="revised wording")), []
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
            self.assertEqual(window.checksum, window_digest(name, start, end))

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
                self.assertTrue(validate_events_document(document))
                with self.assertRaises(SplitError):
                    load_event_windows(document)

    def test_the_loader_accepts_an_unchecksummed_edge_move_the_validator_catches(self):
        """Where the two legitimately differ, stated rather than left implicit.

        `load_event_windows` does not verify digests -- it cannot, since it
        takes a decoded object and has no opinion about how the checksum was
        computed. That is why this validator exists, and why it is the thing
        `metadata/events.json` is checked against, not the loader.
        """

        moved = variant(0, start="2001-03-06")
        self.assertTrue(validate_events_document(moved))
        self.assertEqual(load_event_windows(moved)[0].start, date(2001, 3, 6))


class DeclaredFileTests(unittest.TestCase):
    """The real `metadata/events.json`, once it exists.

    Skips while absent, so this file is green on a branch where Track A has not
    landed yet. The moment the file appears it is held to the full spec, and a
    malformed one fails here with every fault listed.
    """

    def setUp(self):
        if not EVENTS_PATH.exists():
            self.skipTest(
                "metadata/events.json does not exist yet; it is Track A's to "
                "write, and TargetDeclarationTests is the tripwire for its arrival"
            )
        try:
            self.payload = json.loads(EVENTS_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            self.fail(f"metadata/events.json is not valid JSON: {exc}")

    def test_the_declared_file_conforms_to_this_spec(self):
        problems = validate_events_document(self.payload)
        self.assertEqual(
            problems,
            [],
            msg="metadata/events.json does not conform:\n  - "
            + "\n  - ".join(problems),
        )

    def test_the_declared_file_loads_into_event_windows(self):
        windows = load_event_windows(self.payload)
        self.assertTrue(windows)
        for window in windows:
            self.assertIsInstance(window, EventWindow)

    def test_the_declared_file_names_the_windows_the_contract_names(self):
        declared = {window.name for window in load_event_windows(self.payload)}
        for required in REQUIRED_WINDOWS:
            self.assertIn(
                required,
                declared,
                msg=f"the contract names {required} as a single-evaluation window",
            )


class TargetDeclarationTests(unittest.TestCase):
    """`expectedFailure` tripwire: goes red when Track A lands the file.

    Same mechanism as `TargetSchemaTests` in `tests/test_contract.py`. An
    unexpected success is a build failure, which is the signal to come back
    here, delete this class, and promote `DeclaredFileTests` to the plain
    requirement it will by then be.
    """

    @unittest.expectedFailure
    def test_events_metadata_exists_and_declares_the_contract_windows(self):
        payload = json.loads(EVENTS_PATH.read_text(encoding="utf-8"))
        self.assertEqual(validate_events_document(payload), [])
        declared = {window.name for window in load_event_windows(payload)}
        for required in REQUIRED_WINDOWS:
            self.assertIn(required, declared)


if __name__ == "__main__":
    unittest.main()
