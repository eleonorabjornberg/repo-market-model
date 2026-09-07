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
    # Shared contract fixtures. Both tracks import them; neither edits them.
    # A path-level gate cannot see a semantic collision, so the shape both
    # tracks must agree on is made executable and put out of both their reach.
    "src/repo_model/contract.py",
)

# Owned by neither track. Allowed, but always surfaced for human review.
SHARED = ("tests/test_contract.py",)

# Each track's counterpart. Two branches that independently ADD the same new
# path are not caught by the ownership lists -- both can be perfectly in lane --
# but they are an add/add conflict waiting at the merge, and usually a sign the
# same artifact was specified twice. tests/ is the usual site: it belongs to
# neither track wholesale, so nothing else notices.
COUNTERPART = {
    "feature/model-eval": "feature/data-layer",
    "feature/data-layer": "feature/model-eval",
}

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


def added_files(base: str, head: str) -> set[str]:
    """Paths this branch adds that did not exist on the base."""
    out = subprocess.run(
        ["git", "diff", "--name-status", f"{base}...{head}"],
        capture_output=True,
        text=True,
        check=True,
    )
    added = set()
    for line in out.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) == 2 and parts[0].startswith("A"):
            added.add(parts[1])
    return added


def ref_exists(ref: str) -> bool:
    return (
        subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", ref],
            capture_output=True,
        ).returncode
        == 0
    )


def collisions(base: str, head: str, branch: str) -> tuple[set[str], str | None]:
    """New paths this branch and the other track's branch both create.

    Prefers a local ref, falling back to the remote, and names the ref it used.
    A stale ref is more dangerous than a missing one: it returns a confident
    empty answer. In CI only the remote exists, so the check is exactly as fresh
    as the counterpart's last push, and the summary has to say so rather than
    print an unqualified "no collision".

    Returns (paths, ref_used). An absent counterpart is reported, not treated as
    evidence of no collision.
    """
    other = COUNTERPART.get(branch)
    if other is None:
        return set(), None
    for ref in (other, f"origin/{other}"):
        if ref_exists(ref):
            return added_files(base, head) & added_files(base, ref), ref
    return set(), None


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

    both_added, counterpart_ref = collisions(base, head, branch)

    lines = [f"## Ownership check - {track['name']}", ""]
    if both_added:
        breaches.extend(
            (path, f"also added by {COUNTERPART[branch]}; one track must own it")
            for path in sorted(both_added)
        )
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

    if counterpart_ref is None:
        lines.append(
            f"Collision check SKIPPED: no ref found for {COUNTERPART.get(branch)}. "
            "This is not evidence that no path is claimed twice."
        )
    else:
        lines.append(f"Collision check ran against `{counterpart_ref}` (as fresh as its last push).")
    lines.append("")
    lines.append(f"No breach. {len(files)} file(s) changed, all within scope.")
    summarise("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
