#!/usr/bin/env python3
"""Stop hook: before a session ends with new commits on its branch, run the checks CI runs on generated files.

Runs `scripts/pre_review.py --base origin/main` once per branch head: a head that passed is remembered in
`.git/claude-pre-review-ok`, so ending a turn again costs nothing. On `main`, with no new commits, or without
`scripts/pre_review.py`, it does nothing. On a failure it exits 2 and the output goes back to the session, which fixes
it before stopping; `stop_hook_active` stops it from asking twice in a row. It never runs the test suite: that runs in
CI. Standard library only.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def git(*args):
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else ""


def marker():
    common = git("rev-parse", "--git-common-dir")
    return (ROOT / common / "claude-pre-review-ok") if common else None


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        event = {}
    if event.get("stop_hook_active"):
        return 0
    script = ROOT / "scripts" / "pre_review.py"
    branch = git("branch", "--show-current")
    head = git("rev-parse", "HEAD")
    if not script.exists() or not head or branch in ("", "main", "master"):
        return 0
    if git("rev-list", "--count", "origin/main..HEAD") in ("", "0"):
        return 0
    seen = marker()
    if seen and seen.exists() and head in seen.read_text().split():
        return 0
    python = shutil.which("python3.11") or sys.executable
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    try:
        result = subprocess.run([python, "-B", str(script), "--base", "origin/main"], cwd=ROOT, env=env,
                                capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        return 0
    if result.returncode != 0:
        print("Before stopping: the pre-review checks fail on %s.\n%s" % (head[:8], result.stdout[-3000:]),
              file=sys.stderr)
        return 2
    if seen:
        with open(seen, "a") as handle:
            handle.write(head + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
