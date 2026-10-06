"""The live record's code pin is a registered literal, not a rule on main (#255, review findings 2 and 6).

`PINNED_CODE_SHA` was `None` and `resolve_pin` ran from main's own code with a
write token, so a change on main could repoint the commit that records the
forecast with no dated record, and mutating the pin to forty zeros left every
test green. This file holds the replacement: `metadata/live_pin.json` names the
pin and every registered transition, and `scripts/live_pin.py` checks it.

* the manifest (`ManifestTests`): the current pin is the last transition, each
  transition's SHA is an ancestor of main and is named in the decision record
  it cites, and a malformed or unregistered manifest raises `ValueError`;
* the scorer (`ScorerPinTests`): `live_score.load_records` refuses a record
  whose `code.pinned_sha` is not a registered transition;
* the workflow (`WorkflowPinTests`): the pin is read from the manifest with
  `jq`, before any repository Python runs, and the digest and failed-runs
  issues are found by number, not by title.

Red first: this file was committed, and run, before `scripts/live_pin.py` and
`metadata/live_pin.json` existed; every class failed at import.

Recorded mutations, each run in a disposable copy under /tmp, the mutated line
confirmed applied by grep (one match) and killed by the test named:

* registry: in `live_pin.require_registered`, `if sha not in registered(manifest):`
  -> `if False:` makes `test_a_pin_that_is_not_registered_is_refused` fail with
  `AssertionError: ValueError not raised`, and
  `test_the_scorer_refuses_a_record_made_at_an_unregistered_sha` likewise.
* ancestry: in `live_pin.verify_manifest`, `if not _is_ancestor(repo, sha, ref):`
  -> `if False:` makes `test_a_sha_that_is_not_on_main_is_refused` fail with
  `AssertionError: ValueError not raised`.
* the literal: `"current": "c69a361965fd601a4e69fdbc92643d669dba8e9e"` in
  `metadata/live_pin.json` changed to forty zeros makes
  `test_the_real_manifest_is_valid_and_its_pin_is_on_main` fail with
  `ValueError: ... is not an ancestor of origin/main` (the old mutation that
  no test caught).
"""

from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
import tempfile
import unittest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
WORKFLOW = ROOT / ".github" / "workflows" / "live-log.yml"
PIN_SHA = "c69a361965fd601a4e69fdbc92643d669dba8e9e"


def _load(name):
    spec = spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


pins = _load("live_pin")
score = _load("live_score")


def _git(repo, *argv):
    return subprocess.run(
        ["git", "-C", str(repo), *argv], check=True, capture_output=True, text=True
    ).stdout.strip()


def build_repo(tmp):
    """A repository with `main`, one commit, and a decision record naming it."""

    repo = Path(tmp) / "repo"
    repo.mkdir()
    _git(repo, "init", "--quiet", "-b", "main")
    _git(repo, "config", "user.email", "t@example.org")
    _git(repo, "config", "user.name", "t")
    (repo / "code.py").write_text("v = 1\n", encoding="utf-8")
    _git(repo, "add", "code.py")
    _git(repo, "commit", "--quiet", "-m", "pin me")
    sha = _git(repo, "rev-parse", "HEAD")
    (repo / "docs" / "decisions").mkdir(parents=True)
    (repo / "docs" / "decisions" / "live-pin.md").write_text(
        f"# Pin\n\nTransition t0 pins `{sha}`.\n", encoding="utf-8"
    )
    _git(repo, "add", "docs")
    _git(repo, "commit", "--quiet", "-m", "record")
    return repo, sha


def manifest_for(sha):
    return {
        "version": 1,
        "current": sha,
        "transitions": [{"id": "t0", "sha": sha, "record": "docs/decisions/live-pin.md"}],
    }


class ManifestTests(unittest.TestCase):
    def test_the_real_manifest_is_valid_and_its_pin_is_on_main(self):
        manifest = pins.load_manifest()
        self.assertEqual(manifest["current"], PIN_SHA)
        pins.verify_manifest(manifest, ROOT, "HEAD")

    def test_a_well_formed_manifest_verifies(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, sha = build_repo(tmp)
            pins.verify_manifest(manifest_for(sha), repo, "main")

    def test_a_sha_that_is_not_on_main_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, sha = build_repo(tmp)
            _git(repo, "checkout", "--quiet", "-b", "side")
            (repo / "code.py").write_text("v = 2\n", encoding="utf-8")
            _git(repo, "commit", "--quiet", "-am", "off main")
            off_main = _git(repo, "rev-parse", "HEAD")
            _git(repo, "checkout", "--quiet", "main")
            manifest = manifest_for(off_main)
            (repo / "docs" / "decisions" / "live-pin.md").write_text(off_main, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "ancestor"):
                pins.verify_manifest(manifest, repo, "main")

    def test_forty_zeros_are_not_a_pin(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, _ = build_repo(tmp)
            with self.assertRaises(ValueError):
                pins.verify_manifest(manifest_for("0" * 40), repo, "main")

    def test_a_transition_the_record_does_not_name_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, sha = build_repo(tmp)
            (repo / "docs" / "decisions" / "live-pin.md").write_text("nothing here\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "names"):
                pins.verify_manifest(manifest_for(sha), repo, "main")

    def test_a_record_that_does_not_exist_or_is_outside_decisions_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, sha = build_repo(tmp)
            for record in ("docs/decisions/missing.md", "README.md", "../x.md"):
                with self.subTest(record=record):
                    manifest = manifest_for(sha)
                    manifest["transitions"][0]["record"] = record
                    with self.assertRaises(ValueError):
                        pins.verify_manifest(manifest, repo, "main")

    def test_a_malformed_manifest_is_refused(self):
        _, sha = "", PIN_SHA
        bad = []
        manifest = manifest_for(sha)
        manifest["current"] = "f" * 40
        bad.append(("current is not the last transition", manifest))
        manifest = manifest_for(sha)
        manifest["transitions"].append(dict(manifest["transitions"][0]))
        bad.append(("duplicate id", manifest))
        manifest = manifest_for(sha)
        manifest["transitions"][0]["sha"] = sha[:7]
        manifest["current"] = sha[:7]
        bad.append(("short sha", manifest))
        manifest = manifest_for(sha)
        manifest["extra"] = 1
        bad.append(("unknown key", manifest))
        manifest = manifest_for(sha)
        manifest["transitions"] = []
        bad.append(("no transitions", manifest))
        for label, manifest in bad:
            with self.subTest(label):
                with self.assertRaises(ValueError):
                    pins.check_shape(manifest)

    def test_a_pin_that_is_not_registered_is_refused(self):
        manifest = manifest_for(PIN_SHA)
        pins.require_registered(PIN_SHA, manifest)
        for sha in ("0" * 40, "f" * 40, PIN_SHA[:7], None):
            with self.subTest(sha=sha):
                with self.assertRaises(ValueError):
                    pins.require_registered(sha, manifest)

    def test_the_command_line_prints_the_pin_and_refuses_a_bad_manifest(self):
        out = subprocess.run(
            [sys.executable, "-B", str(SCRIPTS / "live_pin.py"), "current"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        self.assertEqual(out, PIN_SHA)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "m.json"
            bad = manifest_for(PIN_SHA)
            bad["current"] = "f" * 40
            path.write_text(json.dumps(bad), encoding="utf-8")
            done = subprocess.run(
                [sys.executable, "-B", str(SCRIPTS / "live_pin.py"), "current", "--manifest", str(path)],
                capture_output=True, text=True,
            )
            self.assertNotEqual(done.returncode, 0)
            self.assertIn("ValueError", done.stderr)


class ScorerPinTests(unittest.TestCase):
    def _log(self, tmp, sha):
        sys.path.insert(0, str(ROOT / "tests"))
        try:
            import test_live_integrity as fixtures
        finally:
            sys.path.pop(0)
        repo, comments = fixtures.build_log(tmp, pinned_sha=sha)
        return repo, fixtures.save(comments, tmp)

    def test_the_scorer_loads_records_made_at_a_registered_sha(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, digests = self._log(tmp, PIN_SHA)
            records = score.load_records(repo, digests, manifest_for(PIN_SHA))
            self.assertEqual(len(records), 3)

    def test_the_scorer_refuses_a_record_made_at_an_unregistered_sha(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, digests = self._log(tmp, "e" * 40)
            with self.assertRaisesRegex(ValueError, "registered"):
                score.load_records(repo, digests, manifest_for(PIN_SHA))


class WorkflowPinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def _step(self, name):
        match = re.search(rf"\n      - name: {re.escape(name)}\n(.*?)(?=\n      - name: |\Z)", self.text, re.S)
        self.assertIsNotNone(match, name)
        return match.group(1)

    def test_the_pin_is_read_from_the_manifest_with_jq_before_any_repository_python_runs(self):
        step = self._step("Check out main and the pinned code")
        self.assertIn("jq -r .current main/metadata/live_pin.json", step)
        self.assertNotIn("live_record.py pin", self.text)
        self.assertNotIn("PYTHONPATH=src", step)
        self.assertNotIn('"$PY"', step)
        self.assertLess(step.index("jq -r .current"), step.index("worktree add"))

    def test_the_pin_is_checked_to_be_a_full_sha_on_main(self):
        step = self._step("Check out main and the pinned code")
        self.assertIn("grep -Eq '^[0-9a-f]{40}$'", step)
        self.assertIn("merge-base --is-ancestor", step)

    def test_the_manifest_is_verified_after_the_checkout_and_a_failure_is_reported(self):
        step = self._step("Verify the pin is a registered transition")
        self.assertIn("id: pin", step)
        self.assertIn("live_pin.py verify", step)
        self.assertLess(self.text.index("- name: Check out main and the pinned code"),
                        self.text.index("- name: Verify the pin is a registered transition"))
        self.assertLess(self.text.index("- name: Verify the pin is a registered transition"),
                        self.text.index("- name: Install the ml extra"))
        self.assertIn("pin=${{ steps.pin.outcome }}", self._step("Open or update the failed-runs issue"))

    def test_the_digest_and_failed_runs_issues_are_found_by_number(self):
        self.assertNotIn("select(.title==", self.text)
        self.assertNotIn('"Live record: daily digests"', self.text)
        self.assertNotIn('"Live record: failed runs"', self.text)
        self.assertIn("DIGEST_ISSUE: 225", self.text)
        self.assertIn("FAILED_RUNS_ISSUE: 237", self.text)

    def test_the_two_issues_are_the_ones_the_records_name(self):
        # #225 holds the digests and #237 the failed runs, as the live record's
        # own decision (#215) and the finding that opened #237 say.
        self.assertRegex(self.text, r"DIGEST_ISSUE: 225\b")
        self.assertRegex(self.text, r"FAILED_RUNS_ISSUE: 237\b")


if __name__ == "__main__":
    unittest.main()
