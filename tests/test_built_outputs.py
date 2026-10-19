"""The page, its data and the assembled research log are built on main and never committed (#928).

`scripts/check_built_outputs.py` refuses a change that tracks, adds, edits or deletes one; `tests/built_outputs.py` builds
them for the tests that read them. The last class shows the point of the rule: two branches that each add a research-log
entry merge one after the other with no conflict, because neither touches `log.md` or the page.

This is not a leakage, availability or staleness guard, so it carries no recorded mutation.
"""
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import built_outputs

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cbo = load("check_built_outputs")
crl = load("check_research_log")


class BuiltPathTests(unittest.TestCase):
    def test_the_three_outputs_are_built_and_nothing_else(self):
        for path in ("site/index.html", "docs/visual/data/research.json", "docs/visual/data/newcomer_n4.json",
                     "docs/research/log.md"):
            with self.subTest(path=path):
                self.assertTrue(cbo.built(path))
        for path in ("site/template.html", "docs/visual/annotations.json", "docs/research/log/_header.md",
                     "docs/research/log/0001-2026-10-05-model-00073-H5-step3.md", "docs/research/plan.md",
                     "docs/visual/data-notes.md", "docs/pivot/progress.md"):
            with self.subTest(path=path):
                self.assertFalse(cbo.built(path))

    def test_the_message_says_to_change_the_inputs(self):
        message = cbo.errors(["site/index.html"])[0]
        self.assertIn("site/index.html", message)
        self.assertIn("change its inputs instead", message)

    def test_a_clean_list_has_no_error(self):
        self.assertEqual(cbo.errors(["scripts/emit_visual.py", "docs/research/log/x.md"]), [])


class RepositoryTests(unittest.TestCase):
    def test_nothing_built_is_tracked(self):
        tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
        self.assertEqual(cbo.errors(tracked.split("\n")), [])

    def test_the_builder_writes_all_three_and_they_are_ignored(self):
        built_outputs.ensure()
        for rel in ("site/index.html", "docs/visual/data/research.json", "docs/research/log.md"):
            with self.subTest(path=rel):
                self.assertTrue((ROOT / rel).is_file())
                ignored = subprocess.run(["git", "check-ignore", "-q", rel], cwd=ROOT)
                self.assertEqual(ignored.returncode, 0, rel + " is not gitignored")

    def test_the_built_log_is_the_assembly_of_the_entry_files(self):
        built_outputs.ensure()
        header, files = crl.read_entry_files()
        self.assertEqual(crl.assemble(header, files), crl.LOG.read_text(encoding="utf-8"))

    def test_a_tracked_log_is_an_error(self):
        self.assertTrue(crl.tracked_errors(["docs/research/log.md"]))
        self.assertEqual(crl.tracked_errors(["docs/research/log/_header.md"]), [])


class TwoBranchesTests(unittest.TestCase):
    """Two branches that each add one entry merge, one after the other, with no conflict (#928, criterion 5)."""

    def run_git(self, cwd, *args):
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                   GIT_COMMITTER_EMAIL="t@t")
        return subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True, check=True).stdout

    def entry(self, pr):
        return ("### 2026-10-19 [H5] step 3 · eleonorabjornberg/repo-market-model#%d\n"
                "- Directive: #%d\n- Step: 3\n- Tier: development\n- Pins: none\n- Tried: x\n- Result: y\n"
                "- Against kill: z\n- Next: n\n" % (pr, pr))

    def test_two_entry_branches_merge_in_turn(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.run_git(repo, "init", "-q", "-b", "main")
            log_dir = repo / "docs" / "research" / "log"
            log_dir.mkdir(parents=True)
            (log_dir / "_header.md").write_text("# Log\n", encoding="utf-8")
            self.run_git(repo, "add", "-A")
            self.run_git(repo, "commit", "-q", "-m", "base")
            names = {}
            for branch, pr in (("a", 901), ("b", 902)):
                self.run_git(repo, "checkout", "-q", "-b", branch, "main")
                names[branch] = crl.entry_name(crl.HEADING.match(self.entry(pr).splitlines()[0]))
                (log_dir / names[branch]).write_text(self.entry(pr), encoding="utf-8")
                self.run_git(repo, "add", "-A")
                self.run_git(repo, "commit", "-q", "-m", branch)
            self.run_git(repo, "checkout", "-q", "main")
            self.run_git(repo, "merge", "-q", "--no-ff", "-m", "merge a", "a")
            self.run_git(repo, "merge", "-q", "--no-ff", "-m", "merge b", "b")
            self.assertEqual(sorted(p.name for p in log_dir.glob("*.md")), sorted(["_header.md", *names.values()]))
            header, files = crl.read_entry_files(log_dir)
            self.assertEqual(crl.assemble(header, files).count("\n### "), 2)


if __name__ == "__main__":
    unittest.main()
