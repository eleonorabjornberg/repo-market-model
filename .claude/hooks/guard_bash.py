#!/usr/bin/env python3
"""PreToolUse hook on Bash: refuse three actions the standing rules forbid, before they happen rather than in CI.

1. A push to `main` (CLAUDE.md: never push to `main`; push only your own branch as `git push origin HEAD`).
2. A GitHub comment that carries Eleonora's approval phrase `GO #<n>`. An agent posting with her token is
   indistinguishable from her to `scripts/owner_attested.py` (#1053), so no agent may post one. Pull request and issue
   bodies are not checked: the attestation reads comments only.
3. A commit that stages a file built on main (#928): `scripts/check_built_outputs.py`'s `BUILT`.

Reads the hook's JSON on stdin; exits 2 with the reason on stderr to block, 0 otherwise. Standard library only.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PUSH_TO_MAIN = re.compile(r"\bgit\b[^|;&\n]*\bpush\b[^|;&\n]*[\s:+](main|master)\b")
COMMENTING = re.compile(r"\bgh\s+(?:issue\s+comment|pr\s+comment|pr\s+review)\b|\bgh\s+api\b[^|;&\n]*/comments\b")
APPROVAL = re.compile(r"\bGO\s*#\d+")
COMMIT = re.compile(r"\bgit\b[^|;&\n]*\bcommit\b")


def built_paths():
    """`BUILT` from scripts/check_built_outputs.py, or an empty tuple if it cannot be read."""
    source = ROOT / "scripts" / "check_built_outputs.py"
    try:
        match = re.search(r"^BUILT\s*=\s*(\([^)]*\))", source.read_text(), re.M)
        return tuple(eval(match.group(1), {"__builtins__": {}})) if match else ()
    except (OSError, SyntaxError, ValueError):
        return ()


def staged():
    result = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=ROOT, capture_output=True, text=True)
    return result.stdout.split() if result.returncode == 0 else []


def refusal(command, staged_paths=None, built=None):
    """The reason to block `command`, or None."""
    if PUSH_TO_MAIN.search(command):
        return "Never push to main (CLAUDE.md). Push your own branch with `git push origin HEAD` and open a PR."
    if COMMENTING.search(command) and APPROVAL.search(command):
        return ("A comment containing `GO #<n>` would read as Eleonora's own approval to scripts/owner_attested.py "
                "(#1053). Only she posts it. Reword the comment without the phrase.")
    if COMMIT.search(command) and " -a" not in command and "--all" not in command:
        built = built_paths() if built is None else built
        paths = staged() if staged_paths is None else staged_paths
        hits = [p for p in paths if any(p == b or (b.endswith("/") and p.startswith(b)) for b in built)]
        if hits:
            return ("These files are built on main and never committed (#928): %s. Unstage them "
                    "(`git restore --staged <path>`) and change their inputs instead." % ", ".join(hits))
    return None


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    command = (event.get("tool_input") or {}).get("command") or ""
    reason = refusal(command)
    if reason:
        print(reason, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
