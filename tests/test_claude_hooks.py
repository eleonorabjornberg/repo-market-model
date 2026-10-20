"""The repository's Claude Code hooks (`.claude/hooks/`, registered in `.claude/settings.json`).

`guard_bash.py` refuses a push to main, a comment carrying Eleonora's `GO #<n>` (#1053), and a commit of a file built on
main (#928). `after_edit.py` checks Markdown edits only. `on_stop.py` never asks twice in a row. Each hook reads its
event as JSON on stdin and blocks with exit status 2.

Recorded mutation: in `guard_bash.refusal`, `if COMMENTING.search(command) and APPROVAL.search(command):` ->
`if False:`. `test_a_comment_carrying_her_approval_phrase_is_refused` failed with `AssertionError: None is not true`;
restored, it passes.
"""

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOKS = ROOT / ".claude" / "hooks"


def load(name):
    spec = importlib.util.spec_from_file_location(name, HOOKS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


guard = load("guard_bash")
after_edit = load("after_edit")


class GuardBashTests(unittest.TestCase):

    def refused(self, command, staged=(), built=("site/index.html", "docs/visual/data/")):
        return guard.refusal(command, staged_paths=list(staged), built=built)

    def test_a_push_to_main_is_refused(self):
        for command in ("git push origin main", "git push origin HEAD:main", "git push -f origin main",
                        "cd repo && git push origin +main"):
            self.assertTrue(self.refused(command), command)

    def test_a_push_of_ones_own_branch_passes(self):
        for command in ("git push origin HEAD", "git push -u origin directive/1027-main-calendar",
                        "git push origin feature-main", "git fetch origin main"):
            self.assertIsNone(self.refused(command), command)

    def test_a_comment_carrying_her_approval_phrase_is_refused(self):
        for command in ('gh pr comment 1039 --body "GO #1039"',
                        "gh issue comment 46 -b 'ok, GO #46'",
                        "gh api repos/o/r/issues/12/comments -f body='GO #12'"):
            self.assertTrue(self.refused(command), command)

    def test_a_body_or_a_comment_without_the_phrase_passes(self):
        for command in ('gh pr create --title t --body "cites GO #656 in the registry"',
                        'gh pr comment 1039 --body "needs her own GO"',
                        "gh api repos/o/r/issues/12 -q .body"):
            self.assertIsNone(self.refused(command), command)

    def test_a_commit_staging_a_built_file_is_refused(self):
        self.assertTrue(self.refused("git commit -m x", staged=["site/index.html", "README.md"]))
        self.assertTrue(self.refused("git commit -m x", staged=["docs/visual/data/a.json"]))

    def test_a_commit_of_inputs_passes(self):
        self.assertIsNone(self.refused("git commit -m x", staged=["site/template.html", "docs/research/log/a.md"]))

    def test_built_is_read_from_the_checker(self):
        self.assertIn("site/index.html", guard.built_paths())

    def test_the_hook_blocks_with_exit_status_2(self):
        event = json.dumps({"tool_name": "Bash", "tool_input": {"command": "git push origin main"}})
        result = subprocess.run([sys.executable, str(HOOKS / "guard_bash.py")], input=event, text=True,
                                capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Never push to main", result.stderr)


class AfterEditTests(unittest.TestCase):

    def test_only_markdown_inside_the_repository_is_checked(self):
        self.assertTrue(after_edit.wants_check(str(ROOT / "CLAUDE.md")))
        self.assertFalse(after_edit.wants_check(str(ROOT / "src" / "repo_model" / "asof.py")))
        self.assertFalse(after_edit.wants_check("/tmp/elsewhere.md"))
        self.assertFalse(after_edit.wants_check(str(ROOT / ".claude" / "worktrees" / "x" / "README.md")))


class OnStopTests(unittest.TestCase):

    def test_it_never_asks_twice_in_a_row(self):
        result = subprocess.run([sys.executable, str(HOOKS / "on_stop.py")],
                                input=json.dumps({"stop_hook_active": True}), text=True, capture_output=True)
        self.assertEqual(result.returncode, 0)


class SettingsTests(unittest.TestCase):

    def test_every_registered_hook_exists(self):
        settings = json.loads((ROOT / ".claude" / "settings.json").read_text())
        commands = [hook["command"] for groups in settings["hooks"].values() for group in groups
                    for hook in group["hooks"]]
        self.assertTrue(commands)
        for command in commands:
            script = command.split("/.claude/hooks/")[1].rstrip('"')
            self.assertTrue((HOOKS / script).exists(), script)


if __name__ == "__main__":
    unittest.main()
