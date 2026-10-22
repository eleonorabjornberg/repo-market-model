"""The checks CI and `scripts/pre_review.py` run are declared one file each under `metadata/ci_checks/` (#1059).

Before this, adding a generator check meant a hand edit to a step list in `.github/workflows/tests.yml` and another to
`CHECKS` in `scripts/pre_review.py`, two lists that open pull requests conflicted in. Now a check is one file, the
`pages` job runs every `ci:pages` declaration through `scripts/ci_checks.py`, and `pre_review.py` reads the same files.
A script that can check its own output (a `--check` flag or a `check` subcommand) with no declaration fails here, so a new
check cannot be left out of CI by forgetting to list it.

**Recorded mutations** (21 October 2026):

* `test_a_script_with_a_check_flag_and_no_declaration_is_found`: in `scripts/ci_checks.py`, the last line of
  `undeclared_scripts`, `return found`, made `return []`; the test failed with
  `AssertionError: 'scripts/emit_progress.py' not found in []`. (The sibling test
  `test_a_script_with_a_check_flag_is_declared` fails the same way when a declaration file is removed.)
* `test_a_failing_check_fails_the_run_and_the_rest_still_run`: in `ci_checks.run`, `failed.append(...)` made `pass`;
  the test failed with `AssertionError: 0 != 1`.
"""
import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ci_checks = _module("ci_checks")
pre_review = _module("pre_review")


def declaration(directory, name, **fields):
    body = {"command": ["scripts/x.py", "--check"], "where": "ci:pages", "pre_review": False} | fields
    (Path(directory) / f"{name}.json").write_text(json.dumps(body), encoding="utf-8")


class Declarations(unittest.TestCase):
    def test_every_declaration_is_well_formed(self):
        found = ci_checks.load()
        self.assertTrue(found)
        for check in found:
            self.assertTrue((ROOT / check["command"][0]).is_file(), check["id"])

    def test_a_malformed_declaration_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            declaration(tmp, "bad", where="nowhere")
            with self.assertRaises(ValueError):
                ci_checks.load(tmp)
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "empty.json").write_text(json.dumps({"where": "ci:pages"}), encoding="utf-8")
            with self.assertRaises(ValueError):
                ci_checks.load(tmp)

    def test_a_script_with_a_check_flag_is_declared(self):
        self.assertEqual(ci_checks.undeclared_scripts(), [])

    def test_a_script_with_a_check_flag_and_no_declaration_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIn("scripts/emit_progress.py", ci_checks.undeclared_scripts(tmp))

    def test_where_a_check_runs_is_true(self):
        """`workflow:<file>` names a workflow that runs the script; `suite` a test module that exercises it."""
        tests = "".join(p.read_text(encoding="utf-8") for p in (ROOT / "tests").glob("test_*.py")
                        if p.name != "test_ci_checks.py")
        for check in ci_checks.load():
            script = check["command"][0]
            where = check["where"]
            if where.startswith("workflow:"):
                workflow = (ROOT / ".github" / "workflows" / where.split(":", 1)[1]).read_text(encoding="utf-8")
                self.assertIn(script, workflow, f"{check['id']}: {where} does not run {script}")
            elif where == "suite":
                self.assertIn(Path(script).stem, tests, f"{check['id']}: no test module mentions {script}")

    def test_the_pages_job_runs_the_declared_checks_and_nothing_by_hand(self):
        workflow = (ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
        job = re.search(r"(?ms)^  pages:\n(.*?)^  suite:", workflow).group(1)
        self.assertIn("scripts/ci_checks.py run ci:pages", job)
        for check in ci_checks.load():
            self.assertNotIn(check["command"][0], job, f"{check['id']} is run by hand in the pages job")
        self.assertTrue([c for c in ci_checks.load() if c["where"] == "ci:pages"])


class Running(unittest.TestCase):
    def test_a_failing_check_fails_the_run_and_the_rest_still_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            declaration(tmp, "a-fails", command=["scripts/ci_checks.py", "nonexistent-subcommand"])
            declaration(tmp, "b-passes", command=["scripts/ci_checks.py", "list", "--help"])
            ran = []
            failed = ci_checks.run("ci:pages", tmp, report=ran.append)
        self.assertEqual(failed, 1)
        self.assertEqual([r["id"] for r in ran], ["a-fails", "b-passes"])


class PreReview(unittest.TestCase):
    def test_pre_review_runs_the_checks_that_declare_it(self):
        declared = [tuple(c["command"]) for c in ci_checks.load() if c["pre_review"]]
        self.assertEqual(list(pre_review.CHECKS), declared)


if __name__ == "__main__":
    unittest.main()
