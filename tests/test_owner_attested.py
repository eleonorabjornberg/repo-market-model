"""Owner attestation (#256): a binding approval counts only when Eleonora made it herself.

Agent posts reach GitHub under Eleonora's account, with `author_association:
OWNER`, so a "Ruling (Eleonora; relayed...)" comment proves nothing about her
instruction. What an app cannot fake is the REST field
`performed_via_github_app`: it names the app that posted the comment, and is
`null` only on a comment posted without one. `scripts/owner_attested.py`
accepts a comment as hers only when it is by `eleonorabjornberg`, a `User`,
with that field present and `null`, never edited since it was posted, on the
issue it is cited for, and containing the required phrase as a whole phrase.

The recorded payloads in `tests/fixtures/owner_attested/` are REST responses
fetched on 6 October 2026, unedited:

* `issue_63_comments.json`: `GET /repos/.../issues/63/comments`, Eleonora's own
  ruling of 1 October 2026 ("repo pressure has no hard ceiling"), posted with
  no app;
* `comment_6003148702.json`: the relayed "GO #151" that `metadata/lockbox.json`
  cites, posted through the `claude` app;
* `comment_5974697778.json`: the relayed "go for #151" of 3 October 2026, later
  withdrawn, posted through the same app.

Where a test needs a payload these do not hold (another login, an edit, a
body carrying a go phrase), it copies a recorded one and changes that one
field, and says so.

Tests written first and watched failing: every class below raised
`FileNotFoundError` on the missing script before `scripts/owner_attested.py`
existed.

Recorded mutation (6 October 2026), on the attestation check: in
`verify_comment`, the app test
`if app is not None:` -> `if False:`. Run alone with
`PYTHONPATH=src:tests python3 -B -m unittest test_owner_attested`,
`test_the_relayed_go_is_not_owner_attested`,
`test_the_withdrawn_relay_is_not_owner_attested`,
`test_a_relay_carrying_the_phrase_is_passed_over`,
`test_a_lockbox_change_citing_a_relay_fails` and
`test_an_added_entry_is_verified_even_without_a_change` failed with
`AssertionError` (`NotOwnerAttested not raised`), and
`test_the_cli_refuses_a_relay` with `AssertionError` (`0 == 0`, exit status 0).
Restored, all pass.
"""

from __future__ import annotations

import copy
import importlib.util
import io
import json
import re
import subprocess
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "owner_attested.py"
FIXTURES = ROOT / "tests" / "fixtures" / "owner_attested"
TESTS_WORKFLOW = ROOT / ".github" / "workflows" / "tests.yml"


def _script():
    spec = importlib.util.spec_from_file_location("owner_attested_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


oa = _script()


def _fixture(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


#: Eleonora's own comment on #63, posted with no app.
OWNER = _fixture("issue_63_comments.json")[0]
OWNER_PHRASE = "repo pressure has no hard ceiling"
#: The relayed "GO #151", posted through the claude app.
GO_RELAY = _fixture("comment_6003148702.json")
#: The relayed "go for #151", later withdrawn.
GO_FOR_RELAY = _fixture("comment_5974697778.json")


def _owner_go(issue=63):
    """The recorded owner comment, its body changed to carry the go phrase."""

    comment = copy.deepcopy(OWNER)
    comment["body"] = f"GO #{issue}. {comment['body']}"
    comment["issue_url"] = comment["issue_url"].rsplit("/", 1)[0] + f"/{issue}"
    return comment


class RecordedPayloadTests(unittest.TestCase):
    def test_the_payloads_are_what_the_docstring_says(self):
        self.assertEqual(OWNER["id"], 5932848456)
        self.assertIsNone(OWNER["performed_via_github_app"])
        self.assertEqual(GO_RELAY["performed_via_github_app"]["slug"], "claude")
        self.assertEqual(GO_FOR_RELAY["performed_via_github_app"]["slug"], "claude")
        for comment in (OWNER, GO_RELAY, GO_FOR_RELAY):
            self.assertEqual(comment["user"]["login"], "eleonorabjornberg")
            self.assertEqual(comment["author_association"], "OWNER")

    def test_her_own_comment_is_owner_attested(self):
        found = oa.verify_comment(OWNER, OWNER_PHRASE, issue=63)
        self.assertEqual(found["id"], 5932848456)

    def test_the_relayed_go_is_not_owner_attested(self):
        with self.assertRaisesRegex(oa.NotOwnerAttested, "claude"):
            oa.verify_comment(GO_RELAY, "GO #151", issue=151)

    def test_the_withdrawn_relay_is_not_owner_attested(self):
        with self.assertRaises(oa.NotOwnerAttested):
            oa.verify_comment(GO_FOR_RELAY, "go for #151", issue=151)

    def test_another_login_is_refused(self):
        comment = copy.deepcopy(OWNER)
        comment["user"]["login"] = "someone-else"
        with self.assertRaisesRegex(oa.NotOwnerAttested, "someone-else"):
            oa.verify_comment(comment, OWNER_PHRASE, issue=63)

    def test_a_bot_account_is_refused(self):
        comment = copy.deepcopy(OWNER)
        comment["user"]["type"] = "Bot"
        with self.assertRaises(oa.NotOwnerAttested):
            oa.verify_comment(comment, OWNER_PHRASE, issue=63)

    def test_a_payload_without_the_app_field_is_refused(self):
        comment = copy.deepcopy(OWNER)
        del comment["performed_via_github_app"]
        with self.assertRaisesRegex(oa.NotOwnerAttested, "performed_via_github_app"):
            oa.verify_comment(comment, OWNER_PHRASE, issue=63)

    def test_an_edited_comment_is_refused(self):
        # An app can edit the body of a comment she posted herself; the edit
        # leaves `performed_via_github_app` null, so only the timestamps show it.
        comment = copy.deepcopy(OWNER)
        comment["updated_at"] = "2026-10-06T00:00:00Z"
        with self.assertRaisesRegex(oa.NotOwnerAttested, "edited"):
            oa.verify_comment(comment, OWNER_PHRASE, issue=63)

    def test_a_comment_on_another_issue_is_refused(self):
        with self.assertRaisesRegex(oa.NotOwnerAttested, "#151"):
            oa.verify_comment(OWNER, OWNER_PHRASE, issue=151)

    def test_the_phrase_must_be_in_the_body(self):
        with self.assertRaisesRegex(oa.NotOwnerAttested, "GO #63"):
            oa.verify_comment(OWNER, "GO #63", issue=63)

    def test_the_phrase_is_matched_whole_and_case_sensitively(self):
        self.assertTrue(oa.phrase_in("**GO #151.** Opened.", "GO #151"))
        self.assertFalse(oa.phrase_in("GO #1510", "GO #151"))
        self.assertFalse(oa.phrase_in("GO #151", "GO #15"))
        self.assertFalse(oa.phrase_in("go #151", "GO #151"))
        self.assertFalse(oa.phrase_in("NOGO #151", "GO #151"))

    def test_an_empty_phrase_is_refused(self):
        with self.assertRaises(ValueError):
            oa.verify_comment(OWNER, " ", issue=63)


class FindTests(unittest.TestCase):
    def test_her_comment_is_found_among_relays(self):
        found = oa.find_attested([GO_FOR_RELAY, GO_RELAY, OWNER], OWNER_PHRASE)
        self.assertEqual(found["id"], OWNER["id"])

    def test_a_relay_carrying_the_phrase_is_passed_over(self):
        with self.assertRaisesRegex(oa.NotOwnerAttested, str(GO_RELAY["id"])):
            oa.find_attested([GO_FOR_RELAY, GO_RELAY, OWNER], "GO #151", issue=151)

    def test_no_comment_with_the_phrase(self):
        with self.assertRaisesRegex(oa.NotOwnerAttested, "no comment"):
            oa.find_attested([OWNER], "GO #999")

    def test_the_cli_finds_her_comment_in_a_recorded_file(self):
        out = io.StringIO()
        with redirect_stdout(out):
            status = oa.main([
                "find", "--issue", "63", "--phrase", OWNER_PHRASE,
                "--comments-file", str(FIXTURES / "issue_63_comments.json"),
            ])
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(out.getvalue())["id"], OWNER["id"])

    def test_the_cli_refuses_a_relay(self):
        err = io.StringIO()
        with redirect_stderr(err), redirect_stdout(io.StringIO()):
            status = oa.main([
                "find", "--issue", "151", "--phrase", "GO #151",
                "--comments-file", str(FIXTURES / "comment_6003148702.json"),
            ])
        self.assertNotEqual(status, 0)
        self.assertIn("not owner-attested", err.getvalue())


def _tree(**files):
    """A reader over a made-up tree: path -> text, missing -> None."""

    return lambda path: files.get(path)


def _real(path):
    target = ROOT / path
    return target.read_text(encoding="utf-8") if target.exists() else None


LOCKBOX = "metadata/lockbox.json"
LIVE = "scripts/live_record.py"
PIN_MANIFEST = "metadata/live_pin.json"
REGISTRY = "metadata/owner_attestations.json"


class BindingKindTests(unittest.TestCase):
    live = _real(LIVE)
    lockbox = _real(LOCKBOX)

    def _kinds(self, base, head):
        return oa.binding_kinds(_tree(**base), _tree(**head))

    def test_the_tree_against_itself_changes_nothing(self):
        self.assertEqual(oa.binding_kinds(_real, _real), set())

    def test_the_real_files_parse(self):
        self.assertIsNone(oa.live_pin_state(self.live)["PINNED_CODE_SHA"])
        self.assertIn("pressure_model_v1", oa.live_model_state(self.live)["models"])
        self.assertIn(
            "docs/runs/compare_persistence_vs_gbm_conformal_pid_nested_funding_crps.json",
            oa.live_model_state(self.live)["records"],
        )

    def test_opening_a_tier_is_binding(self):
        opened = json.loads(self.lockbox)
        opened["tiers"][1]["opened"] = {"date": "2027-04-01", "ruling": "x"}
        head = json.dumps(opened)
        self.assertEqual(self._kinds({LOCKBOX: self.lockbox}, {LOCKBOX: head}), {"lockbox"})

    def test_reformatting_the_lockbox_is_not(self):
        head = json.dumps(json.loads(self.lockbox))
        self.assertEqual(self._kinds({LOCKBOX: self.lockbox}, {LOCKBOX: head}), set())

    def test_setting_the_pin_is_binding(self):
        head = self.live.replace("PINNED_CODE_SHA = None", 'PINNED_CODE_SHA = "' + "a" * 40 + '"')
        self.assertNotEqual(head, self.live)
        self.assertEqual(self._kinds({LIVE: self.live}, {LIVE: head}), {"live-pin"})

    def test_changing_how_the_pin_resolves_is_binding(self):
        head = self.live.replace('"--first-parent", "--reverse"', '"--reverse"')
        self.assertNotEqual(head, self.live)
        self.assertEqual(self._kinds({LIVE: self.live}, {LIVE: head}), {"live-pin"})

    def test_a_pin_manifest_is_binding(self):
        head = {LIVE: self.live, PIN_MANIFEST: '{"sha": "' + "b" * 40 + '"}'}
        self.assertEqual(self._kinds({LIVE: self.live}, head), {"live-pin"})

    def test_a_model_joining_the_live_record_is_binding(self):
        head = self.live.replace(
            'CRPS_RECORD = "',
            'V2_RECORD = "docs/runs/pressure_model_v2_h1.json"\nCRPS_RECORD = "',
        )
        self.assertNotEqual(head, self.live)
        self.assertEqual(self._kinds({LIVE: self.live}, {LIVE: head}), {"live-model"})

    def test_renaming_a_logged_model_is_binding(self):
        head = self.live.replace('"name": "pressure_model_v1"', '"name": "pressure_model_v2"')
        self.assertNotEqual(head, self.live)
        self.assertEqual(self._kinds({LIVE: self.live}, {LIVE: head}), {"live-model"})

    def test_an_ordinary_edit_of_the_live_script_is_not(self):
        head = self.live.replace("STEPS = (", "# a comment\nSTEPS = (")
        self.assertNotEqual(head, self.live)
        self.assertEqual(self._kinds({LIVE: self.live}, {LIVE: head}), set())


def _registry(*entries):
    return json.dumps({"version": 1, "rule": "docs/decisions/drafts/owner-attestation.md",
                       "attestations": list(entries)})


def _entry(kind="lockbox", issue=63, comment_id=OWNER["id"], phrase=None):
    return {"kind": kind, "issue": issue, "comment_id": comment_id,
            "phrase": phrase or f"GO #{issue}", "what": "a test entry"}


class RegistryTests(unittest.TestCase):
    def test_the_tracked_registry_loads(self):
        entries = oa.load_registry(_real(REGISTRY))
        self.assertIsInstance(entries, list)

    def test_the_phrase_follows_the_go_convention(self):
        with self.assertRaisesRegex(ValueError, "GO #63"):
            oa.load_registry(_registry(_entry(phrase="approved")))

    def test_an_unknown_kind_is_refused(self):
        with self.assertRaisesRegex(ValueError, "kind"):
            oa.load_registry(_registry(_entry(kind="anything")))

    def test_an_added_entry_is_found(self):
        added = oa.added_entries(_registry(), _registry(_entry()))
        self.assertEqual([e["comment_id"] for e in added], [OWNER["id"]])

    def test_the_registry_is_append_only(self):
        with self.assertRaisesRegex(ValueError, "append-only"):
            oa.added_entries(_registry(_entry()), _registry())
        changed = _entry()
        changed["what"] = "edited"
        with self.assertRaisesRegex(ValueError, "append-only"):
            oa.added_entries(_registry(_entry()), _registry(changed))

    def test_a_missing_base_registry_is_empty(self):
        self.assertEqual(len(oa.added_entries(None, _registry(_entry()))), 1)


class CheckTests(unittest.TestCase):
    lockbox = _real(LOCKBOX)

    def _opened(self):
        opened = json.loads(self.lockbox)
        opened["tiers"][1]["opened"] = {"date": "2027-04-01", "ruling": "x"}
        return json.dumps(opened)

    @staticmethod
    def _fetch(payloads):
        def fetch(comment_id):
            return payloads[comment_id]
        return fetch

    @staticmethod
    def _no_fetch(comment_id):
        raise AssertionError(f"fetched {comment_id} with nothing to verify")

    def test_no_binding_change_fetches_nothing(self):
        tree = _tree(**{LOCKBOX: self.lockbox, REGISTRY: _registry()})
        self.assertEqual(oa.check(tree, tree, self._no_fetch), [])

    def test_a_lockbox_change_without_a_citation_fails(self):
        base = _tree(**{LOCKBOX: self.lockbox, REGISTRY: _registry()})
        head = _tree(**{LOCKBOX: self._opened(), REGISTRY: _registry()})
        with self.assertRaisesRegex(oa.NotOwnerAttested, "lockbox"):
            oa.check(base, head, self._no_fetch, cited={63})

    def test_a_lockbox_change_citing_a_relay_fails(self):
        base = _tree(**{LOCKBOX: self.lockbox, REGISTRY: _registry()})
        head = _tree(**{LOCKBOX: self._opened(),
                        REGISTRY: _registry(_entry(issue=151, comment_id=GO_RELAY["id"]))})
        with self.assertRaises(oa.NotOwnerAttested):
            oa.check(base, head, self._fetch({GO_RELAY["id"]: GO_RELAY}), cited={151})

    def test_a_lockbox_change_citing_her_go_passes(self):
        base = _tree(**{LOCKBOX: self.lockbox, REGISTRY: _registry()})
        head = _tree(**{LOCKBOX: self._opened(), REGISTRY: _registry(_entry())})
        verified = oa.check(base, head, self._fetch({OWNER["id"]: _owner_go()}), cited={63})
        self.assertEqual([c["id"] for c in verified], [OWNER["id"]])

    def test_a_citation_of_another_kind_does_not_cover_the_change(self):
        base = _tree(**{LOCKBOX: self.lockbox, REGISTRY: _registry()})
        head = _tree(**{LOCKBOX: self._opened(), REGISTRY: _registry(_entry(kind="live-pin"))})
        with self.assertRaisesRegex(oa.NotOwnerAttested, "lockbox"):
            oa.check(base, head, self._fetch({OWNER["id"]: _owner_go()}), cited={63})

    def test_the_fetched_comment_must_be_the_cited_one(self):
        base = _tree(**{LOCKBOX: self.lockbox, REGISTRY: _registry()})
        head = _tree(**{LOCKBOX: self._opened(),
                        REGISTRY: _registry(_entry(comment_id=1))})
        with self.assertRaisesRegex(oa.NotOwnerAttested, "id"):
            oa.check(base, head, self._fetch({1: _owner_go()}), cited={63})

    def test_an_added_entry_is_verified_even_without_a_change(self):
        base = _tree(**{REGISTRY: _registry()})
        head = _tree(**{REGISTRY: _registry(_entry(issue=151, comment_id=GO_RELAY["id"]))})
        with self.assertRaises(oa.NotOwnerAttested):
            oa.check(base, head, self._fetch({GO_RELAY["id"]: GO_RELAY}), cited={151})


class CommentReuseTests(unittest.TestCase):
    """Each binding change needs a fresh `GO #<n>` comment (#1225, finding #1212).

    An added entry may not cite a `comment_id` the base registry already holds, nor one another added entry
    holds. Entries already on the base are grandfathered: only added entries are looked at.

    Recorded mutation (26 October 2026), on the re-use guard: in `check`, the line
    `reused = sorted(...)` replaced by `reused = [] and sorted(...)`: `test_an_added_entry_reusing_a_base_comment_is_refused`
    failed with `AssertionError: NotOwnerAttested not raised`.
    """

    @staticmethod
    def _fetch(comment_id):
        return _owner_go()

    def test_an_added_entry_reusing_a_base_comment_is_refused(self):
        base = _tree(**{REGISTRY: _registry(_entry())})
        head = _tree(**{REGISTRY: _registry(_entry(), _entry(kind="live-pin"))})
        with self.assertRaisesRegex(oa.NotOwnerAttested, "already in the registry"):
            oa.check(base, head, self._fetch, cited={63})

    def test_two_added_entries_sharing_a_comment_are_refused(self):
        base = _tree(**{REGISTRY: _registry()})
        head = _tree(**{REGISTRY: _registry(_entry(), _entry(kind="live-pin"))})
        with self.assertRaisesRegex(oa.NotOwnerAttested, "already in the registry"):
            oa.check(base, head, self._fetch, cited={63})

    def test_a_fresh_comment_passes(self):
        base = _tree(**{REGISTRY: _registry(_entry(comment_id=1))})
        head = _tree(**{REGISTRY: _registry(_entry(comment_id=1), _entry())})
        verified = oa.check(base, head, self._fetch, cited={63})
        self.assertEqual([c["id"] for c in verified], [OWNER["id"]])

    def test_the_tracked_registry_as_its_own_base_passes(self):
        tree = _tree(**{REGISTRY: _real(REGISTRY)})
        self.assertEqual(oa.check(tree, tree, lambda i: self.fail("fetched")), [])

    def test_existing_reuses_are_grandfathered(self):
        ids = [e["comment_id"] for e in oa.load_registry(_real(REGISTRY))]
        self.assertGreater(len(ids) - len(set(ids)), 0, "the registry holds a grandfathered re-use")
        tree = _tree(**{REGISTRY: _real(REGISTRY)})
        self.assertEqual(oa.check(tree, tree, lambda i: self.fail("fetched")), [])


class PathKindTests(unittest.TestCase):
    """#944 (ruling on PR #943): CLAUDE.md, `.claude/` and a registration are binding by their path.

    Tests written first and watched failing: every one raised `AttributeError` (no `path_kinds`) or `TypeError`
    (no `changed_paths` argument) before the change.

    Recorded mutation (19 October 2026), on the path guard: in `path_kinds`,
    `if path in CLAUDE_FILES or path.startswith(CLAUDE_DIRS):` -> `if False:`. Run alone with
    `PYTHONPATH=src:tests python3 -B -m unittest test_owner_attested`, `test_claude_md_is_binding`,
    `test_a_file_under_dot_claude_is_binding`, `test_binding_kinds_reads_the_changed_paths` failed with
    `AssertionError` (`Items in the second set but not the first`) and
    `test_a_claude_md_change_without_a_citation_fails` with `AssertionError` (`NotOwnerAttested not raised`).
    Restored, all pass.
    """

    def test_claude_md_is_binding(self):
        self.assertEqual(oa.path_kinds(["CLAUDE.md"]), {"claude-files"})

    def test_a_file_under_dot_claude_is_binding(self):
        self.assertEqual(oa.path_kinds([".claude/settings.json"]), {"claude-files"})

    def test_a_registration_record_is_binding(self):
        self.assertEqual(oa.path_kinds(["metadata/registrations/h5.json"]), {"registration"})

    def test_look_alike_paths_are_not(self):
        paths = ["docs/CLAUDE.md", "tests/CLAUDE.md", ".claudeignore", "metadata/registrations.json",
                 "docs/decisions.md", "docs/decision/x.md", "docs/research/decisions/x.md", "README.md"]
        self.assertEqual(oa.path_kinds(paths), set())

    def test_binding_kinds_reads_the_changed_paths(self):
        kinds = oa.binding_kinds(_real, _real, lambda: ["CLAUDE.md", "metadata/registrations/h5.json"])
        self.assertEqual(kinds, {"claude-files", "registration"})

    def test_no_changed_paths_given_changes_nothing(self):
        self.assertEqual(oa.binding_kinds(_real, _real), set())

    def test_the_kinds_may_be_cited_in_the_registry(self):
        for kind in ("claude-files", "registration"):
            self.assertEqual(oa.load_registry(_registry(_entry(kind=kind)))[0]["kind"], kind)

    def test_a_claude_md_change_without_a_citation_fails(self):
        tree = _tree(**{REGISTRY: _registry()})
        with self.assertRaisesRegex(oa.NotOwnerAttested, "claude-files"):
            oa.check(tree, tree, CheckTests._no_fetch, lambda: ["CLAUDE.md"], cited={63})

    def test_a_dot_claude_change_citing_a_relay_fails(self):
        base = _tree(**{REGISTRY: _registry()})
        head = _tree(**{REGISTRY: _registry(_entry(kind="claude-files", issue=151, comment_id=GO_RELAY["id"]))})
        with self.assertRaises(oa.NotOwnerAttested):
            oa.check(base, head, CheckTests._fetch({GO_RELAY["id"]: GO_RELAY}), lambda: [".claude/settings.json"], cited={151})

    def test_a_registration_without_a_citation_fails(self):
        tree = _tree(**{REGISTRY: _registry()})
        with self.assertRaisesRegex(oa.NotOwnerAttested, "registration"):
            oa.check(tree, tree, CheckTests._no_fetch, lambda: ["metadata/registrations/h5.json"], cited={63})

    def test_a_registration_citing_her_go_passes(self):
        base = _tree(**{REGISTRY: _registry()})
        head = _tree(**{REGISTRY: _registry(_entry(kind="registration"))})
        verified = oa.check(base, head, CheckTests._fetch({OWNER["id"]: _owner_go()}),
                            lambda: ["metadata/registrations/h5.json"], cited={63})
        self.assertEqual([c["id"] for c in verified], [OWNER["id"]])

    def test_a_citation_of_another_kind_does_not_cover_a_registration(self):
        base = _tree(**{REGISTRY: _registry()})
        head = _tree(**{REGISTRY: _registry(_entry(kind="claude-files"))})
        with self.assertRaisesRegex(oa.NotOwnerAttested, "registration"):
            oa.check(base, head, CheckTests._fetch({OWNER["id"]: _owner_go()}),
                     lambda: ["metadata/registrations/h5.json"], cited={63})


class DecisionsPathTests(unittest.TestCase):
    """#1074 (ruling on #1068, 21 October 2026): every file under `docs/decisions/`, drafts included, is binding.

    Tests written first and watched failing: each raised `AssertionError` (`set()` is not `{'decisions'}`) or
    `ValueError` (kind 'decisions' is not one of KINDS) before the change.

    Recorded mutation (21 October 2026), on the path guard: in `path_kinds`,
    `if path.startswith(DECISIONS_DIRS):` -> `if False:`. Run alone with
    `PYTHONPATH=src:tests python3 -B -m unittest test_owner_attested.DecisionsPathTests`,
    `test_a_decision_record_is_binding`, `test_a_draft_is_binding`, `test_moving_a_draft_out_is_binding` and
    `test_a_new_decision_without_a_citation_fails` and
    `test_a_citation_of_another_kind_does_not_cover_a_decision` failed with `AssertionError`
    (`NotOwnerAttested not raised` for the last two). Restored, all pass.
    """

    PATH = "docs/decisions/x.md"

    def test_a_decision_record_is_binding(self):
        self.assertEqual(oa.path_kinds([self.PATH]), {"decisions"})

    def test_a_draft_is_binding(self):
        self.assertEqual(oa.path_kinds(["docs/decisions/drafts/y.md"]), {"decisions"})

    def test_moving_a_draft_out_is_binding(self):
        # `git diff --no-renames` lists the old and the new path, so a move shows as a delete and an add.
        self.assertEqual(oa.path_kinds(["docs/decisions/drafts/y.md", "docs/decisions/y.md"]), {"decisions"})

    def test_the_kind_may_be_cited_in_the_registry(self):
        self.assertEqual(oa.load_registry(_registry(_entry(kind="decisions")))[0]["kind"], "decisions")

    def test_a_new_decision_without_a_citation_fails(self):
        tree = _tree(**{REGISTRY: _registry()})
        with self.assertRaisesRegex(oa.NotOwnerAttested, "decisions"):
            oa.check(tree, tree, CheckTests._no_fetch, lambda: [self.PATH], cited={63})

    def test_a_new_decision_citing_her_go_passes(self):
        base = _tree(**{REGISTRY: _registry()})
        head = _tree(**{REGISTRY: _registry(_entry(kind="decisions"))})
        verified = oa.check(base, head, CheckTests._fetch({OWNER["id"]: _owner_go()}), lambda: [self.PATH], cited={63})
        self.assertEqual([c["id"] for c in verified], [OWNER["id"]])

    def test_a_new_decision_citing_a_relay_fails(self):
        base = _tree(**{REGISTRY: _registry()})
        head = _tree(**{REGISTRY: _registry(_entry(kind="decisions", issue=151, comment_id=GO_RELAY["id"]))})
        with self.assertRaises(oa.NotOwnerAttested):
            oa.check(base, head, CheckTests._fetch({GO_RELAY["id"]: GO_RELAY}), lambda: [self.PATH], cited={151})

    def test_a_citation_of_another_kind_does_not_cover_a_decision(self):
        base = _tree(**{REGISTRY: _registry()})
        head = _tree(**{REGISTRY: _registry(_entry(kind="claude-files"))})
        with self.assertRaisesRegex(oa.NotOwnerAttested, "decisions"):
            oa.check(base, head, CheckTests._fetch({OWNER["id"]: _owner_go()}), lambda: [self.PATH], cited={63})


class SettlementDatingFilesTests(unittest.TestCase):
    """#1327 (her ruling of 30 October 2026, ledger item 86; finding #1317): the two settlement-dating declarations are
    binding by their path, under the kind `decisions`.

    `metadata/settlement_announcement_dating.json` holds the H5 candidate's announcement instant (read by
    `repo_model.settlement_dating`, `repo_model.s3c_announced`) and `metadata/net_settlement.json` holds the instant that sizes
    its net terms. Neither the final-test freeze nor this check covered them, so a pull request could move the candidate's
    information set without her `GO`. They share the kind `decisions` and not a new one: a change that edits the decision record
    and the declaration together then needs one entry, because the registry refuses one comment cited twice by a change (#1225).

    Tests written first and watched failing: three raised `AssertionError` (`set()` is not `{'decisions'}`, or
    `NotOwnerAttested not raised`) before the change.

    Recorded mutation (30 October 2026), on the path guard: in `path_kinds`,
    `if path.startswith(DECISIONS_DIRS) or path in DATING_FILES:` -> `if path.startswith(DECISIONS_DIRS) or False:`. Run alone
    with `PYTHONPATH=src:tests python3 -B -m unittest test_owner_attested.SettlementDatingFilesTests`,
    `test_the_announcement_dating_is_binding` and `test_the_net_settlement_declaration_is_binding` failed with `AssertionError`
    (`Items in the second set but not the first`) and `test_a_dating_change_without_a_citation_fails` with `AssertionError`
    (`NotOwnerAttested not raised`). Restored, all pass.
    """

    FILES = ("metadata/settlement_announcement_dating.json", "metadata/net_settlement.json")

    def test_the_announcement_dating_is_binding(self):
        self.assertEqual(oa.path_kinds([self.FILES[0]]), {"decisions"})

    def test_the_net_settlement_declaration_is_binding(self):
        self.assertEqual(oa.path_kinds([self.FILES[1]]), {"decisions"})

    def test_both_files_exist_in_the_tree(self):
        for path in self.FILES:
            self.assertTrue((ROOT / path).is_file(), path)

    def test_look_alike_paths_are_not(self):
        paths = ["metadata/settlement_result_dating.json", "metadata/net_settlement_inputs.json",
                 "metadata/sources_measurement.json", "tests/fixtures/net_settlement.json",
                 "metadata/net_settlement.json.bak", "docs/metadata/settlement_announcement_dating.json"]
        self.assertEqual(oa.path_kinds(paths), set())

    def test_a_dating_change_without_a_citation_fails(self):
        tree = _tree(**{REGISTRY: _registry()})
        for path in self.FILES:
            with self.assertRaisesRegex(oa.NotOwnerAttested, "decisions"):
                oa.check(tree, tree, CheckTests._no_fetch, lambda: [path], cited={1327})

    def test_a_dating_change_citing_a_relay_fails(self):
        base = _tree(**{REGISTRY: _registry()})
        head = _tree(**{REGISTRY: _registry(_entry(kind="decisions", issue=151, comment_id=GO_RELAY["id"]))})
        with self.assertRaises(oa.NotOwnerAttested):
            oa.check(base, head, CheckTests._fetch({GO_RELAY["id"]: GO_RELAY}), lambda: [self.FILES[0]], cited={151})

    def test_one_go_covers_the_record_and_both_declarations(self):
        base = _tree(**{REGISTRY: _registry()})
        head = _tree(**{REGISTRY: _registry(_entry(kind="decisions"))})
        changed = ["docs/decisions/information-set.md", *self.FILES]
        verified = oa.check(base, head, CheckTests._fetch({OWNER["id"]: _owner_go()}), lambda: changed, cited={63})
        self.assertEqual([c["id"] for c in verified], [OWNER["id"]])


class GitPathTests(unittest.TestCase):
    def test_a_commit_against_itself_changes_no_path(self):
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
        if head.returncode != 0:
            self.skipTest("not a git checkout")
        sha = head.stdout.strip()
        self.assertEqual(list(oa.git_changed(sha, sha)()), [])


class PushRangeTests(unittest.TestCase):
    """#1122 (ruling on finding #1110, 22 October 2026): the check runs on a push to `main`, over `before..after`.

    #1078 changed `docs/decisions/scoring-protocol.md` and merged on CI that ran before #1080 bound `docs/decisions/`.
    A fixture history reproduces it: a commit changes a binding file with no registry entry.

    Tests written first and watched failing: `test_a_push_that_changes_a_binding_file_fails`,
    `test_the_failure_names_the_commit_and_the_file` and `test_a_new_branch_push_is_read_against_the_parent`
    raised `AttributeError` (no `push_range_report` / `resolve_push_base`) and the wiring tests `AssertionError`
    (`'push' not found`) before the change.

    Recorded mutation (22 October 2026), on the range check: in `main`, `return 1` after `NotOwnerAttested` ->
    `return 0`. Run alone with
    `PYTHONPATH=src:tests python3 -B -m unittest test_owner_attested.PushRangeTests`,
    `test_a_push_that_changes_a_binding_file_fails` failed with `AssertionError` (`0 != 1`).
    Restored, all pass.
    """

    def setUp(self):
        import tempfile

        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = Path(self._tmp.name)
        self._git("init", "-q")
        self._git("config", "user.email", "t@example.invalid")
        self._git("config", "user.name", "t")
        self.first = self._commit({REGISTRY: _registry(), "README.md": "a\n"}, "start")
        self.old, oa.REPO = oa.REPO, self.repo
        self.addCleanup(setattr, oa, "REPO", self.old)

    def _git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, capture_output=True, text=True, check=True).stdout.strip()

    def _commit(self, files, message):
        for path, text in files.items():
            target = self.repo / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
        self._git("add", "-A")
        self._git("commit", "-q", "-m", message)
        return self._git("rev-parse", "HEAD")

    def _run(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = oa.main(["check", *args])
        return code, out.getvalue(), err.getvalue()

    def test_a_push_that_changes_nothing_binding_passes(self):
        after = self._commit({"README.md": "b\n"}, "docs")
        self.assertEqual(self._run("--base", self.first, "--head", after)[0], 0)

    def test_a_push_that_changes_a_binding_file_fails(self):
        after = self._commit({"docs/decisions/scoring-protocol.md": "changed\n"}, "binding change")
        code, _, err = self._run("--base", self.first, "--head", after)
        self.assertEqual(code, 1)
        self.assertIn("decisions", err)

    def test_the_failure_names_the_commit_and_the_file(self):
        self._commit({"README.md": "b\n"}, "ordinary")
        after = self._commit({"docs/decisions/scoring-protocol.md": "changed\n"}, "binding change")
        _, _, err = self._run("--base", self.first, "--head", after)
        self.assertIn(after[:8], err)
        self.assertIn("docs/decisions/scoring-protocol.md", err)
        self.assertIn("binding change", err)

    def test_a_multi_commit_push_is_read_as_one_range(self):
        # The change and its entry may land in one push; the aggregate range is what the pull request check reads.
        self._commit({"docs/decisions/x.md": "changed\n"}, "binding change")
        after = self._commit({REGISTRY: _registry(_entry(kind="decisions"))}, "entry")
        out = oa.push_range_report(self.first, after)
        self.assertIn("docs/decisions/x.md", out)

    def test_a_new_branch_push_is_read_against_the_parent(self):
        after = self._commit({"README.md": "b\n"}, "docs")
        self.assertEqual(oa.resolve_push_base("0" * 40, after), after + "^")
        self.assertEqual(oa.resolve_push_base("f" * 40, after), after + "^")
        self.assertEqual(oa.resolve_push_base(self.first, after), self.first)


class WiringTests(unittest.TestCase):
    workflow = TESTS_WORKFLOW.read_text(encoding="utf-8")

    def _job(self):
        match = re.search(r"\n  owner-attested:\n(.*?)(?=\n  \S|\Z)", self.workflow, re.S)
        self.assertIsNotNone(match, "tests.yml has no owner-attested job")
        return match.group(1)

    def test_ci_runs_the_check_on_every_pull_request(self):
        job = self._job()
        self.assertIn("github.event_name == 'pull_request'", job)
        self.assertIn("scripts/owner_attested.py check", job)
        self.assertIn("github.event.pull_request.base.sha", job)
        self.assertIn("fetch-depth: 0", job)

    def test_ci_also_runs_the_check_on_every_push_to_main(self):
        job = self._job()
        self.assertIn("github.event_name == 'push'", job)
        self.assertIn("github.event.before", job)
        self.assertIn("--head \"$GITHUB_SHA\"", job)
        self.assertNotIn("schedule", job)
        self.assertRegex(self.workflow, r"(?s)\n  push:\n    branches: \[main\]")

    def test_the_job_can_read_issue_comments_and_nothing_more(self):
        job = self._job()
        self.assertIn("issues: read", job)
        self.assertNotIn("write", job)

    def test_the_lockbox_says_where_an_opening_is_attested(self):
        text = (ROOT / "src" / "repo_model" / "lockbox.py").read_text(encoding="utf-8")
        self.assertIn("metadata/owner_attestations.json", text)

    def test_the_live_pin_says_where_a_transition_is_attested(self):
        self.assertIn("metadata/owner_attestations.json", _real(LIVE))

    def test_the_script_runs_from_a_clean_interpreter(self):
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--help"], capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


class MatchingTests(unittest.TestCase):
    """#1195 (finding #1188): a binding kind is covered only by an entry the change itself added, for an issue it cites.

    Tests written first and watched failing: each raised `AssertionError` (`NotOwnerAttested not raised`) or
    `TypeError` (`check()` took no `cited`) before the change.

    Recorded mutations (24 October 2026), each run with
    `PYTHONPATH=src:tests python3 -B -m unittest test_owner_attested`:
    (1) in `check`, `covered = {entry["kind"] for entry in added if entry["issue"] in cited}` ->
    `covered = {entry["kind"] for entry in added}`: `test_an_entry_for_another_issue_covers_nothing` failed with
    `AssertionError` (`NotOwnerAttested not raised`);
    (2) in `_check`, the push loop `for sha in push_commits(base, args.head):` -> one range, base to head:
    `test_each_merge_of_a_push_range_is_checked_on_its_own_range` failed with `AssertionError`;
    (3) in `_check`, `head = f"{args.head}^2"` -> `head = args.head`:
    `test_a_merge_ref_picking_up_main_is_checked_on_the_pr_range` failed with `AssertionError`.
    Restored, all pass.
    """

    PATH = "docs/decisions/drafts/b2-thin-pool.md"

    def test_an_entry_for_another_issue_covers_nothing(self):
        # #1157: the change cites #1155; the only entry added is #1130's (decisions kind).
        base = _tree(**{REGISTRY: _registry()})
        head = _tree(**{REGISTRY: _registry(_entry(kind="decisions", issue=1130))})
        with self.assertRaisesRegex(oa.NotOwnerAttested, "decisions"):
            oa.check(base, head, CheckTests._fetch({OWNER["id"]: _owner_go(1130)}), lambda: [self.PATH],
                     cited={1155})

    def test_an_entry_for_the_cited_issue_covers_it(self):
        base = _tree(**{REGISTRY: _registry()})
        head = _tree(**{REGISTRY: _registry(_entry(kind="decisions", issue=1155))})
        verified = oa.check(base, head, CheckTests._fetch({OWNER["id"]: _owner_go(1155)}), lambda: [self.PATH],
                            cited={1155})
        self.assertEqual([c["id"] for c in verified], [OWNER["id"]])

    def test_an_entry_already_on_the_base_covers_nothing(self):
        old = _registry(_entry(kind="decisions", issue=1155))
        tree = _tree(**{REGISTRY: old})
        with self.assertRaisesRegex(oa.NotOwnerAttested, "decisions"):
            oa.check(tree, tree, CheckTests._no_fetch, lambda: [self.PATH], cited={1155})

    def test_no_cited_issue_is_refused_not_assumed(self):
        tree = _tree(**{REGISTRY: _registry()})
        with self.assertRaises(ValueError):
            oa.check(tree, tree, CheckTests._no_fetch, lambda: [self.PATH])

    def test_what_a_change_cites(self):
        self.assertEqual(oa.cited_issues("directive/1155-b2-thin-pool", "x", "Closes #1155.\nGO #1135 later"),
                         {1155, 1135})
        self.assertEqual(oa.cited_issues("see #1130 and PR #1137; fixes: #7"), {7})
        self.assertEqual(oa.cited_issues(None, ""), set())

    def test_a_merge_ref_picking_up_main_is_checked_on_the_pr_range(self):
        # The pull_request event checks out a merge ref: main's newer entry (#1130) is in the base..merge range.
        # The pull request cites #1130 too and adds no entry of its own, so only its own range shows that.
        with _TempRepo() as repo:
            repo.commit({"README": "a"}, "root")
            first = repo.head()
            repo.commit({"docs/decisions/x.md": "x", REGISTRY: _registry(_entry(kind="decisions", issue=1130))},
                        "main moves: Closes #1130")
            repo.git("checkout", "-q", "-b", "pr", first)
            repo.commit({self.PATH: "draft"}, "the draft")
            repo.git("checkout", "-q", "-")
            repo.git("merge", "--no-ff", "-q", "pr", "-m", "merge ref")
            args = ["check", "--base", first, "--merge-ref", "--cite", "1130"]
            with _stub_fetch():
                code, err = repo.run(args)
        self.assertEqual(code, 1, err)
        self.assertIn("decisions", err)

    def test_each_merge_of_a_push_range_is_checked_on_its_own_range(self):
        with _TempRepo() as repo:
            repo.commit({"README": "a"}, "root")
            before = repo.head()
            repo.commit({"docs/decisions/x.md": "x", REGISTRY: _registry(_entry(kind="decisions", issue=1130))},
                        "one (#1) Closes #1130")
            repo.commit({self.PATH: "draft"}, "two Closes #1130")
            with _stub_fetch():
                code, err = repo.run(["check", "--push-before", before, "--no-fetch-pull"])
        self.assertEqual(code, 1, err)
        self.assertIn("two Closes #1130", err)

    def test_a_push_range_of_covered_merges_passes(self):
        with _TempRepo() as repo:
            repo.commit({"README": "a"}, "root")
            before = repo.head()
            repo.commit({"docs/decisions/x.md": "x", REGISTRY: _registry(_entry(kind="decisions", issue=1130))},
                        "one Closes #1130")
            with _stub_fetch():
                code, err = repo.run(["check", "--push-before", before, "--no-fetch-pull"])
        self.assertEqual(code, 0, err)


def _stub_fetch():
    class Stub:
        def __enter__(self):
            self.saved = oa.fetch_comment
            comment = _owner_go(1130)
            oa.fetch_comment = lambda repository, comment_id, token: comment
        def __exit__(self, *exc):
            oa.fetch_comment = self.saved
    return Stub()


class _TempRepo:
    """A throwaway git repository the script is pointed at (`oa.REPO`)."""

    def __enter__(self):
        import tempfile
        self._dir = tempfile.TemporaryDirectory()
        self.path = Path(self._dir.name)
        self.saved = oa.REPO
        oa.REPO = self.path
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@example.org")
        self.git("config", "user.name", "t")
        return self

    def __exit__(self, *exc):
        oa.REPO = self.saved
        self._dir.cleanup()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.path, check=True, capture_output=True, text=True).stdout.strip()

    def head(self):
        return self.git("rev-parse", "HEAD")

    def commit(self, files, message):
        for name, text in files.items():
            target = self.path / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)

    def run(self, args):
        err = io.StringIO()
        with redirect_stderr(err), redirect_stdout(io.StringIO()):
            code = oa.main(args)
        return code, err.getvalue()


class ReplayTests(unittest.TestCase):
    """The recorded failures of 23 October 2026 on this repository's own history (skipped in a clone without it)."""

    def _have(self, *shas):
        for sha in shas:
            if subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"], cwd=ROOT).returncode:
                self.skipTest(f"{sha} is not in this clone")

    def test_the_1157_push_range_fails(self):
        self._have("0ee0a145", "22e2c572")
        err = io.StringIO()
        with redirect_stderr(err), redirect_stdout(io.StringIO()):
            code = oa.main(["check", "--push-before", "0ee0a145", "--head", "22e2c572", "--no-fetch-pull"])
        self.assertEqual(code, 1)
        self.assertIn("b2-thin-pool", err.getvalue())

    def test_the_1157_merge_ref_case_fails(self):
        # Base b2f4619c; the merge ref held #1137's #1130 entry, the pull request added none.
        self._have("b2f4619c", "22e2c572")
        err = io.StringIO()
        with redirect_stderr(err), redirect_stdout(io.StringIO()):
            code = oa.main(["check", "--base", "b2f4619c", "--head", "22e2c572", "--merge-ref", "--cite", "1155"])
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
