"""The hook that refuses an out-of-lane edit before it happens.

`.github/check_ownership.py` answers "may this branch have changed these files"
on a pushed branch, from a diff, in CI. `.claude/hooks/ownership_guard.py` asks
the same gate the same question one tool call earlier, so a contract breach
costs a sentence rather than a round.

It exists because of 9 September 2026, when a block was queued to Track B whose
three files were all `HUMAN_ONLY`. Its six stated preconditions -- branch, merge
base, three greps, a green suite -- all passed. Every one described the state of
the tree; none asked who was allowed to change it. The agent checked ownership
on its own initiative and stopped, and this module is that initiative made
mechanical.

**This file tests a guard, so it is worth saying what would make it worthless.**
A decision table checked in isolation proves the mapping and nothing about the
hook: the payload could be parsed wrong, the branch read from the wrong
directory, the exit code ignored. *A function with a unit test and no exercised
caller is not a working path* -- said in this repository about a metric, then
found again in `LEGACY_SOURCE_IDS`, where a parser was proved to read a legacy
snapshot and the builder was never asked. So `HookEndToEndTests` runs the hook
as the tool actually runs it: a real git repository in a temporary directory, a
real JSON payload on stdin, and the exit code as the verdict.

The hook and the gate are both `HUMAN_ONLY`, and so is this file. An agent that
can weaken the test guarding the hook that enforces the contract has edited
around the contract in three moves instead of one.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
HOOK = REPO_ROOT / ".claude" / "hooks" / "ownership_guard.py"
GATE = REPO_ROOT / ".github" / "check_ownership.py"

TRACK_A = "feature/data-layer"
TRACK_B = "feature/model-eval"


def _load(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class HookDecisionTests(unittest.TestCase):
    """Every category of the split, decided the way the gate decides it.

    The expectations are written as categories, not as a copy of the lists. A
    test that restated `HUMAN_ONLY` would pass forever against its own copy --
    the drift this repository refuses in a registry that copies the parser's
    column names, one layer over.
    """

    @classmethod
    def setUpClass(cls):
        cls.hook = _load("ownership_guard", HOOK)
        cls.gate = _load("check_ownership_for_hook", GATE)

    def refusal(self, path, branch):
        return self.hook.decide(path, branch, self.gate)

    def test_a_human_only_path_is_refused_to_either_track(self):
        human_only = self.gate.HUMAN_ONLY[0]
        self.assertTrue(human_only)
        for branch in (TRACK_A, TRACK_B):
            with self.subTest(branch=branch):
                message = self.refusal(human_only, branch)
                self.assertIsNotNone(message)
                self.assertIn("reserved for the human", message)
                self.assertIn(human_only, message)

    def test_the_hook_and_its_own_configuration_are_human_only(self):
        """The loophole this closes is the reason the hook is worth having.

        An agent that may edit `.claude/settings.json` may delete the hook; one
        that may edit `CLAUDE.md` may delete the rule telling it to check. Both
        are edits around the contract, which AGENT_CONTRACT.md forbids outright,
        and neither is visible as a breach in the block's own diff of source.
        """
        for path in (
            "CLAUDE.md",
            "AGENTS.md",
            ".claude/settings.json",
            ".claude/hooks/ownership_guard.py",
            "tests/test_ownership_hook.py",
            ".github/check_ownership.py",
        ):
            with self.subTest(path=path):
                message = self.refusal(path, TRACK_B)
                self.assertIsNotNone(
                    message, f"{path} is editable by a track branch"
                )
                self.assertIn("reserved for the human", message)

    def test_each_track_is_refused_the_other_track_s_files(self):
        for branch, forbidden in (
            (TRACK_A, self.gate.TRACKS[TRACK_A]["forbidden"][0]),
            (TRACK_B, self.gate.TRACKS[TRACK_B]["forbidden"][0]),
        ):
            with self.subTest(branch=branch, path=forbidden):
                message = self.refusal(forbidden, branch)
                self.assertIsNotNone(message)
                self.assertIn("belongs to", message)

    def test_a_track_may_edit_a_file_in_its_own_lane(self):
        """The other half. A guard that refuses everything refuses nothing."""
        self.assertIsNone(self.refusal("src/repo_model/ingest.py", TRACK_A))
        self.assertIsNone(self.refusal("src/repo_model/metrics.py", TRACK_B))
        self.assertIsNone(self.refusal("tests/test_ingest.py", TRACK_A))

    def test_a_shared_path_is_allowed_and_is_not_silently_reserved(self):
        """`tests/test_contract.py` is the seam both tracks are meant to meet at.

        A path-level gate cannot see a semantic collision, so blocking here
        would be wrong: CI surfaces it for review instead.
        """
        for shared in self.gate.SHARED:
            with self.subTest(path=shared):
                self.assertIsNone(self.refusal(shared, TRACK_A))
                self.assertIsNone(self.refusal(shared, TRACK_B))
                self.assertTrue(self.hook.is_shared(shared, self.gate))

    def test_the_human_branch_is_not_constrained(self):
        """The split constrains the tracks. `main` is the human's."""
        for path in ("README.md", "src/repo_model/ingest.py", "CLAUDE.md"):
            with self.subTest(path=path):
                self.assertIsNone(self.refusal(path, "main"))


class HookEndToEndTests(unittest.TestCase):
    """The hook as the tool runs it: JSON on stdin, verdict as the exit code.

    Everything above tests a mapping. This tests the path: payload parsed, the
    branch read from the payload's `cwd` rather than from wherever the test
    happens to run, the target resolved relative to the checkout it is in, and
    exit 2 as the refusal with the reason on stderr where the model reads it.

    Mutation record, run in a disposable clone under `$HOME`;
    `PYTHONDONTWRITEBYTECODE=1`, `python3 -B`; control green before and after
    each, module alone and whole suite. Each kill is an `AssertionError` on the
    exit code, which is the hook's entire verdict.

    1. **`DENY` changed from `2` to `1`.** Killed all three refusal tests,
       `AssertionError: 1 != 2`. Exit 1 does not block a `PreToolUse` call, so
       the hook would print its refusal and let the edit through -- a guard that
       states its objection and then stands aside. **This was not a hypothetical
       when it was written:** the first version of the hook exited 1 whenever
       the gate could not be imported, because `exec_module` raised out of
       `load_gate`, and its own docstring claimed it failed closed. The
       gate-cannot-be-imported test found it on the first run.
    2. **The `relative_to(root)` guard removed**, so the path is tested as an
       absolute one. Killed the two in-checkout refusal tests with
       `AssertionError: 0 != 2` -- and the direction is the point. It does not
       over-block; `matches()` compares `/tmp/.../checkout/README.md` against
       `README.md`, nothing matches, and **the hook allows everything, in
       silence.** Note also what it did *not* kill:
       `test_a_path_outside_the_checkout_is_none_of_its_business` passed
       throughout, because allowing is what it asserts. A test that asserts a
       permission cannot detect a guard that has stopped refusing; the refusal
       tests are what hold path resolution honest.
    3. **`git rev-parse --abbrev-ref HEAD` run without `-C cwd`**, so the branch
       comes from the process's own directory instead of the payload's. Killed
       all three refusal tests with `AssertionError: 0 != 2` when the suite was
       run from `main` -- the hook read `main`, concluded the human was editing,
       and allowed. Run from a checkout already on a track branch it would kill
       less, or nothing. **A test whose result depends on the branch it is run
       from is not a test**, which is why the payload carries `cwd` and why
       these cases build their own repository rather than using this one.
    """

    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="ownership-hook-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        checkout = self.tmp / "checkout"
        (checkout / ".github").mkdir(parents=True)
        (checkout / ".claude" / "hooks").mkdir(parents=True)
        shutil.copy(GATE, checkout / ".github" / "check_ownership.py")
        shutil.copy(HOOK, checkout / ".claude" / "hooks" / "ownership_guard.py")
        (checkout / "README.md").write_text("placeholder\n")
        self._git(checkout, "init", "--quiet")
        self._git(checkout, "config", "user.email", "hook@example.invalid")
        self._git(checkout, "config", "user.name", "hook test")
        self._git(checkout, "add", "-A")
        self._git(checkout, "commit", "--quiet", "-m", "base")
        self._git(checkout, "checkout", "--quiet", "-b", TRACK_B)
        self.checkout = checkout

    @staticmethod
    def _git(cwd, *arguments):
        subprocess.run(["git", "-C", str(cwd), *arguments], check=True,
                       capture_output=True)

    def run_hook(self, tool, file_path, cwd=None):
        payload = json.dumps({
            "tool_name": tool,
            "tool_input": {"file_path": str(file_path)},
            "cwd": str(cwd or self.checkout),
        })
        done = subprocess.run(
            ["python3", str(self.checkout / ".claude/hooks/ownership_guard.py")],
            input=payload, capture_output=True, text=True,
        )
        return done.returncode, done.stderr

    def test_an_out_of_lane_edit_is_refused_with_the_reason_on_stderr(self):
        code, stderr = self.run_hook("Edit", self.checkout / "README.md")
        self.assertEqual(code, 2, "exit 2 is what blocks a PreToolUse call")
        self.assertIn("CONTRACT", stderr)
        self.assertIn("README.md", stderr)

    def test_an_in_lane_edit_is_allowed(self):
        code, _ = self.run_hook("Edit", self.checkout / "src/repo_model/metrics.py")
        self.assertEqual(code, 0)

    def test_the_branch_is_read_from_the_payload_not_from_the_process(self):
        """Two branches, one process, opposite verdicts on the same path."""
        self._git(self.checkout, "checkout", "--quiet", "-b", TRACK_A)
        code, stderr = self.run_hook(
            "Edit", self.checkout / "src/repo_model/baseline.py"
        )
        self.assertEqual(code, 2)
        self.assertIn("belongs to", stderr)
        self._git(self.checkout, "checkout", "--quiet", TRACK_B)
        code, _ = self.run_hook(
            "Edit", self.checkout / "src/repo_model/baseline.py"
        )
        self.assertEqual(code, 0)

    def test_a_path_outside_the_checkout_is_none_of_its_business(self):
        """Mutation copies live under `$HOME`, by instruction."""
        code, _ = self.run_hook("Edit", self.tmp / "elsewhere" / "README.md")
        self.assertEqual(code, 0)

    def test_a_tool_that_does_not_write_a_file_is_not_watched(self):
        """Stated as a test because it is this guard's largest blind spot.

        A write performed through `Bash` -- `sed -i`, a heredoc, `cp` -- is not
        an `Edit`, and this hook does not see it. Matching command text for
        path-like substrings would refuse `grep README.md` and would still miss
        a path built from a variable. CI remains the backstop, and nothing
        anywhere should describe this hook as making a breach impossible.
        """
        code, _ = self.run_hook("Bash", self.checkout / "README.md")
        self.assertEqual(code, 0)

    def test_a_gate_it_cannot_import_is_refused_rather_than_waved_through(self):
        """A guard that passes when it cannot run is the shape this repo refuses."""
        (self.checkout / ".github" / "check_ownership.py").unlink()
        code, stderr = self.run_hook("Edit", self.checkout / "README.md")
        self.assertEqual(code, 2)
        self.assertIn("could not import", stderr)


if __name__ == "__main__":
    unittest.main()
