#!/usr/bin/env python3
"""Do the human-side git steps a closed round always asks for, in one command.

Every round-closing directives file ends with the same three steps: push `main`,
fast-forward each worktree onto the new `origin/main`, push each. They are
copy-pasted from the handoff by hand every time, and the handoff itself warns
that `git status` in this repo has reported stale ahead-counts more than once —
so this script never trusts a status line, only `rev-list --count`.

It refuses to touch anything unless the tree is clean, and it never merges,
rebases or force-pushes anything other than a `--ff-only` fast-forward. If a
fast-forward is not possible, it stops and reports why instead of guessing.

Standard library only.

    python3 scripts/sync_round.py            # push main, fast-forward + push worktrees
    python3 scripts/sync_round.py --check    # report what would happen; touches nothing

Edit WORKTREES below if a worktree moves or a new one is added.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Sibling worktrees, as named in every round's handoff. Update if either moves.
WORKTREES = [
    ("feature/model-eval", ROOT.parent / "rmm-model"),
    ("feature/data-layer", ROOT.parent / "rmm-data"),
]

CHECK_ONLY = "--check" in sys.argv


def git(cwd, *args, check=True):
    result = subprocess.run(("git",) + args, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} in {cwd} failed:\n{result.stderr.strip()}")
    return result.stdout.strip()


def is_clean(cwd):
    return git(cwd, "status", "--porcelain") == ""


def ahead_count(cwd, local, upstream):
    """rev-list --count, never the `git status` ahead/behind line — see module docstring."""
    return int(git(cwd, "rev-list", "--count", f"{upstream}..{local}"))


def behind_count(cwd, local, upstream):
    return int(git(cwd, "rev-list", "--count", f"{local}..{upstream}"))


def sync_main():
    print(f"== {ROOT.name} (main) ==")
    if not is_clean(ROOT):
        print("  dirty working tree — not touching it. Commit or stash first.")
        return False

    git(ROOT, "fetch", "origin")
    ahead = ahead_count(ROOT, "main", "origin/main")
    behind = behind_count(ROOT, "main", "origin/main")

    if behind:
        print(f"  origin/main is {behind} commit(s) ahead of local main — fetch merged nothing "
              "to push; re-run after you've pulled.")
        return False
    if not ahead:
        print("  origin/main already matches main. Nothing to push.")
        return True

    print(f"  main is {ahead} commit(s) ahead of origin/main.")
    if CHECK_ONLY:
        print("  --check: would run `git push origin main`.")
        return True

    git(ROOT, "push", "origin", "main")
    print("  pushed.")
    return True


def sync_worktree(branch, path):
    print(f"== {path.name} ({branch}) ==")
    if not path.exists():
        print(f"  not found at {path} — skipping. Edit WORKTREES in this script if it moved.")
        return
    if not is_clean(path):
        print("  dirty working tree — not touching it. Commit or stash first.")
        return

    git(path, "fetch", "origin")
    local_ahead = ahead_count(path, branch, f"origin/{branch}")
    behind = behind_count(path, branch, f"origin/main")

    if local_ahead:
        print(f"  local {branch} has {local_ahead} commit(s) not on origin — "
              "not fast-forwarding over local work. Push or resolve by hand.")
        return
    if not behind:
        print(f"  {branch} already matches origin/main. Nothing to do.")
        return

    print(f"  {behind} commit(s) behind origin/main.")
    if CHECK_ONLY:
        print(f"  --check: would run `git merge --ff-only origin/main` then `git push`.")
        return

    git(path, "merge", "--ff-only", "origin/main")
    git(path, "push")
    print("  fast-forwarded and pushed.")


def main():
    ok = sync_main()
    if not ok and not CHECK_ONLY:
        print("\nmain did not push cleanly — stopping before touching the worktrees.")
        sys.exit(1)
    for branch, path in WORKTREES:
        sync_worktree(branch, path)


if __name__ == "__main__":
    main()
