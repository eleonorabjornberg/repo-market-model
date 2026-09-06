#!/usr/bin/env python3
"""Enforce the AGENT_CONTRACT.md ownership split on a branch.

Two tracks work in parallel worktrees on one repo. The contract assigns every
file to Track A (data layer), Track B (model and evaluation), or to the human.
A pull request that edits the other track's files is a contract breach whatever
the diff says, so it is cheaper to reject it mechanically than to notice it in
review.

Two tiers, deliberately:

  Hard failure  - the branch touched a file the other track owns, or a document
                  reserved for the human. Exit 1.
  Review notice - the branch touched a file owned by neither track. Exit 0, but
                  the file is named in the job summary. Blocking these would be
                  wrong: `tests/test_contract.py` is the seam both tracks are
                  supposed to meet at.

Usage:
    python3 .github/check_ownership.py <base-ref> <head-branch>

Runs anywhere git does; CI is not required.
"""

from __future__ import annotations

import os
import subprocess
import sys

# A pattern ending in "/" matches a directory prefix; anything else is an exact
# path. Deliberately not globs -- a glob invites a rule nobody can read.
HUMAN_ONLY = (
    "AGENT_CONTRACT.md",
    "PLAN.md",
    "METHODOLOGY.md",
    "DATA.md",
    "README.md",
    ".github/",
)

# Owned by neither track. Allowed, but always surfaced for human review.
SHARED = ("tests/test_contract.py",)

TRACKS = {
    "feature/model-eval": {
        "name": "Track B (model and evaluation)",
        "forbidden": (
            "metadata/",
            "src/repo_model/ingest.py",
            "src/repo_model/data.py",
            "src/repo_model/registry.py",
            "data/",
        ),
        "owner": "Track A (data layer)",
    },
    "feature/data-layer": {
        "name": "Track A (data layer)",
        "forbidden": (
            "src/repo_model/splits.py",
            "src/repo_model/event_eval.py",
            "src/repo_model/metrics.py",
        ),
        "owner": "Track B (model and evaluation)",
    },
}


def matches(path: str, pattern: str) -> bool:
    return path.startswith(pattern) if pattern.endswith("/") else path == pattern


def changed_files(base: str, head: str) -> list[str]:
    """Files the branch changed relative to its merge base.

    Three dots, not two: two would also report everything that landed on the
    base since the branch was cut, and blame this branch for it.
    """
    out = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...{head}"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in out.stdout.splitlines() if line]


def summarise(text: str) -> None:
    print(text)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write(text + "\n")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    base, head = argv[1], argv[2]

    branch = head.removeprefix("refs/heads/").removeprefix("origin/")
    track = TRACKS.get(branch)
    if track is None:
        summarise(
            f"Ownership check skipped: `{branch}` is not a track branch. "
            "Human branches are not constrained by the split."
        )
        return 0

    files = changed_files(base, head)
    if not files:
        summarise(f"Ownership check: `{branch}` changed no files against `{base}`.")
        return 0

    breaches: list[tuple[str, str]] = []
    notices: list[str] = []
    for path in files:
        if any(matches(path, p) for p in SHARED):
            notices.append(path)
            continue
        if any(matches(path, p) for p in HUMAN_ONLY):
            breaches.append((path, "reserved for the human"))
            continue
        if any(matches(path, p) for p in track["forbidden"]):
            breaches.append((path, f"owned by {track['owner']}"))

    lines = [f"## Ownership check - {track['name']}", ""]
    if notices:
        lines += [
            "**Review required.** These files are owned by neither track, so a",
            "change to one is a change to the seam between them:",
            "",
        ]
        lines += [f"- `{path}`" for path in notices]
        lines.append("")
    if breaches:
        lines += ["**Contract breach.** This branch may not edit:", ""]
        lines += [f"- `{path}` - {why}" for path, why in breaches]
        lines += [
            "",
            "Revert these paths and let the owning track make the change. If the",
            "split itself is wrong, that is a human edit to AGENT_CONTRACT.md,",
            "not a exception granted in a pull request.",
        ]
        summarise("\n".join(lines))
        return 1

    lines.append(f"No breach. {len(files)} file(s) changed, all within scope.")
    summarise("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
