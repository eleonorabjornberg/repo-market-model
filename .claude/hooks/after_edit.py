#!/usr/bin/env python3
"""PostToolUse hook on Edit and Write: after a Markdown edit, run the documentation guards at once.

`tests/test_docs_freshness.py` (counts, future dates, CLI commands that no longer parse, the declared Python) and
`tests/test_claim_sources.py` (pointers to working pages) take seconds. Run here, they catch a wording problem before it
costs a push and a CI run. On a failure the hook exits 2 and the tail of the output goes back to the session, which
fixes the wording. Other files are left to CI. Standard library only.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULES = ("test_docs_freshness", "test_claim_sources")


def interpreter():
    """The declared Python (3.11) when it is on PATH, else the one running this hook."""
    return shutil.which("python3.11") or sys.executable


def wants_check(file_path):
    try:
        path = Path(file_path).resolve()
        relative = path.relative_to(ROOT)
    except (ValueError, OSError):
        return False
    return path.suffix == ".md" and ".claude/worktrees" not in relative.as_posix()


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    file_path = (event.get("tool_input") or {}).get("file_path") or ""
    if not wants_check(file_path):
        return 0
    env = {"PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": "src:tests", "PATH": os.environ.get("PATH", "")}
    try:
        result = subprocess.run([interpreter(), "-B", "-m", "unittest", *MODULES], cwd=ROOT, env=env,
                                capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        return 0
    if result.returncode != 0:
        print("The documentation guards fail after this edit:\n" + result.stderr[-3000:], file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
