#!/usr/bin/env python3
"""The checks CI and `scripts/pre_review.py` run, one declaration file each under `metadata/ci_checks/` (#1059).

A declaration is JSON:

    {"command": ["scripts/emit_visual.py", "--check"],   # run as `python3 -B <command>` from the repository root
     "env": {"PYTHONPATH": "src"},                        # optional, added to the environment
     "where": "ci:pages",                                 # see WHERE
     "pre_review": true}                                  # `scripts/pre_review.py` runs it too

`where` says what runs the check: `ci:pages` is the `pages` job of `tests.yml`, which runs every such declaration with
`python3 -B scripts/ci_checks.py run ci:pages`; `workflow:<file>` is a step of that workflow file written by hand (it
needs an event condition or a base commit); `suite` is a test module that exercises the script. A new generator check is
one new file here, not an edit to a shared list. `tests/test_ci_checks.py` fails for a script that can check its own
output (a `--check` flag or a `check` subcommand) and has no declaration.

    python3 scripts/ci_checks.py run ci:pages    # run every declared check of that kind; exit 1 if any fails
    python3 scripts/ci_checks.py list            # the declarations

Standard library only.
"""
import argparse
import ast
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKS_DIR = ROOT / "metadata" / "ci_checks"
SCRIPTS = ROOT / "scripts"

WHERE = ("ci:pages", "suite")
WORKFLOW_PREFIX = "workflow:"


def load(directory=CHECKS_DIR):
    """The declarations, by file name, each with its `id` (the file stem). `ValueError` for one that is malformed."""
    found = []
    for path in sorted(Path(directory).glob("*.json")):
        body = json.loads(path.read_text(encoding="utf-8"))
        command = body.get("command")
        if not (isinstance(command, list) and command and all(isinstance(c, str) for c in command)):
            raise ValueError(f"{path.name}: `command` must be a non-empty list of strings")
        where = body.get("where")
        if where not in WHERE and not (isinstance(where, str) and where.startswith(WORKFLOW_PREFIX) and where[len(WORKFLOW_PREFIX):]):
            raise ValueError(f"{path.name}: `where` must be one of {WHERE} or `workflow:<file>`, not {where!r}")
        env = body.get("env", {})
        if not (isinstance(env, dict) and all(isinstance(v, str) for v in env.values())):
            raise ValueError(f"{path.name}: `env` must map names to strings")
        found.append({"id": path.stem, "command": command, "env": env, "where": where,
                      "pre_review": bool(body.get("pre_review", False))})
    return found


def can_check(tree):
    """True if the parsed script has a `--check` flag or a `check` subcommand."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and node.value == "--check":
            return True
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "add_parser"
                and node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value == "check"):
            return True
    return False


def undeclared_scripts(directory=CHECKS_DIR):
    """The scripts that can check their own output and appear in no declaration."""
    declared = {c["command"][0] for c in load(directory)}
    found = []
    for path in sorted(SCRIPTS.glob("*.py")):
        if path.resolve() == Path(__file__).resolve():
            continue  # this script names the flag it looks for
        rel = f"scripts/{path.name}"
        if rel not in declared and can_check(ast.parse(path.read_text(encoding="utf-8"), filename=rel)):
            found.append(rel)
    return found


def run(where, directory=CHECKS_DIR, report=None):
    """Run every declared check with this `where`, all of them even after a failure; the number that failed."""
    failed = 0
    for check in (c for c in load(directory) if c["where"] == where):
        result = subprocess.run([sys.executable, "-B", *check["command"]], cwd=ROOT, capture_output=True, text=True,
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", **check["env"]})
        ok = result.returncode == 0
        print(f"{'ok  ' if ok else 'FAIL'}  {check['id']}: {' '.join(check['command'])}")
        if not ok:
            failed += 1
            print((result.stdout + result.stderr).rstrip())
        if report:
            report(check | {"ok": ok})
    return failed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="action", required=True)
    runner = sub.add_parser("run", help="run every declared check of one kind")
    runner.add_argument("where", help="ci:pages")
    sub.add_parser("list", help="print the declarations")
    args = parser.parse_args(argv)
    if args.action == "list":
        for check in load():
            print(f"{check['id']}\t{check['where']}\t{' '.join(check['command'])}")
        return 0
    if args.where not in WHERE:
        raise ValueError(f"run takes one of {WHERE}")
    return 1 if run(args.where) else 0


if __name__ == "__main__":
    sys.exit(main())
