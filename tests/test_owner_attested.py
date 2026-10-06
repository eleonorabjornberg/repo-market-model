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
            oa.check(base, head, self._no_fetch)

    def test_a_lockbox_change_citing_a_relay_fails(self):
        base = _tree(**{LOCKBOX: self.lockbox, REGISTRY: _registry()})
        head = _tree(**{LOCKBOX: self._opened(),
                        REGISTRY: _registry(_entry(issue=151, comment_id=GO_RELAY["id"]))})
        with self.assertRaises(oa.NotOwnerAttested):
            oa.check(base, head, self._fetch({GO_RELAY["id"]: GO_RELAY}))

    def test_a_lockbox_change_citing_her_go_passes(self):
        base = _tree(**{LOCKBOX: self.lockbox, REGISTRY: _registry()})
        head = _tree(**{LOCKBOX: self._opened(), REGISTRY: _registry(_entry())})
        verified = oa.check(base, head, self._fetch({OWNER["id"]: _owner_go()}))
        self.assertEqual([c["id"] for c in verified], [OWNER["id"]])

    def test_a_citation_of_another_kind_does_not_cover_the_change(self):
        base = _tree(**{LOCKBOX: self.lockbox, REGISTRY: _registry()})
        head = _tree(**{LOCKBOX: self._opened(), REGISTRY: _registry(_entry(kind="live-pin"))})
        with self.assertRaisesRegex(oa.NotOwnerAttested, "lockbox"):
            oa.check(base, head, self._fetch({OWNER["id"]: _owner_go()}))

    def test_the_fetched_comment_must_be_the_cited_one(self):
        base = _tree(**{LOCKBOX: self.lockbox, REGISTRY: _registry()})
        head = _tree(**{LOCKBOX: self._opened(),
                        REGISTRY: _registry(_entry(comment_id=1))})
        with self.assertRaisesRegex(oa.NotOwnerAttested, "id"):
            oa.check(base, head, self._fetch({1: _owner_go()}))

    def test_an_added_entry_is_verified_even_without_a_change(self):
        base = _tree(**{REGISTRY: _registry()})
        head = _tree(**{REGISTRY: _registry(_entry(issue=151, comment_id=GO_RELAY["id"]))})
        with self.assertRaises(oa.NotOwnerAttested):
            oa.check(base, head, self._fetch({GO_RELAY["id"]: GO_RELAY}))


class WiringTests(unittest.TestCase):
    workflow = TESTS_WORKFLOW.read_text(encoding="utf-8")

    def _job(self):
        match = re.search(r"\n  owner-attested:\n(.*?)(?=\n  \S|\Z)", self.workflow, re.S)
        self.assertIsNotNone(match, "tests.yml has no owner-attested job")
        return match.group(1)

    def test_ci_runs_the_check_on_every_pull_request(self):
        job = self._job()
        self.assertIn("if: github.event_name == 'pull_request'", job)
        self.assertIn("scripts/owner_attested.py check", job)
        self.assertIn("github.event.pull_request.base.sha", job)
        self.assertIn("fetch-depth: 0", job)

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


if __name__ == "__main__":
    unittest.main()
