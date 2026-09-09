#!/usr/bin/env python3
"""Refuse an edit the branch does not own, before the edit happens.

`.github/check_ownership.py` decides the same question on a pushed branch, in
CI, from a diff. By then the work exists, the commit exists, and the agent that
wrote it has stopped. This hook asks that gate the question one tool call
earlier, so a block is a sentence in the transcript rather than a round.

It happened on 9 September 2026. A block was queued to Track B whose three
files are all `HUMAN_ONLY`; the block's six stated preconditions -- branch,
merge base, three greps, a green suite -- all passed, because every one of them
described the state of the tree and none of them asked who was allowed to
change it. Track B checked ownership on its own initiative and stopped. This
hook is that initiative made mechanical, so the next agent does not have to
have it.

**It imports the gate rather than copying it.** Two lists of who owns what is
one list plus a way for them to disagree, which is the exact defect this
repository keeps finding one layer down: a registry that carries its own copy
of the parser's column names, a document that restates a version pyproject
declares. `HUMAN_ONLY`, `SHARED`, `TRACKS` and `matches()` are read out of
`.github/check_ownership.py` at call time.

What it cannot see, stated plainly because a guard's blind spot belongs beside
the guard:

  * **A write performed by the `Bash` tool.** `sed -i`, a heredoc, `cp`, a
    python one-liner -- none of them is an `Edit`, and matching command text
    for path-like substrings would refuse `grep README.md` and would still miss
    a path built from a variable. CI remains the backstop for that, and it is
    the reason this hook is not described anywhere as making a breach
    impossible. It makes an accidental one cost a tool call instead of a round.
  * **A semantic collision inside a file both tracks may touch.** A path-level
    gate never could; `tests/test_contract.py` is `SHARED` for that reason and
    is allowed through here.

The failure posture is deliberate and reversible. If this hook is running
inside a track worktree and cannot determine the answer -- a payload it cannot
parse, a gate it cannot import -- it **denies and says why**. A guard that
passes when it cannot run is the shape this repository has refused everywhere
else. The cost of getting that wrong is an agent that cannot edit and says so
in one turn; the cost of the other choice is a contract that is silently not
enforced. Outside a repository, or for a file outside it, it allows: mutation
copies live under `$HOME` by instruction and are none of its business.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

WATCHED_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}

ALLOW = 0
DENY = 2  # PreToolUse: exit 2 blocks the call and shows stderr to the model.


def deny(message: str) -> int:
    sys.stderr.write(message.rstrip() + "\n")
    return DENY


def git(cwd: str, *arguments: str) -> str | None:
    try:
        done = subprocess.run(
            ["git", "-C", cwd, *arguments],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if done.returncode != 0:
        return None
    return done.stdout.strip()


def load_gate(root: pathlib.Path):
    """The ownership gate itself, imported from the path CI runs."""
    location = root / ".github" / "check_ownership.py"
    try:
        spec = importlib.util.spec_from_file_location("check_ownership", location)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception:
        # Absent, unreadable, or broken. Every one of those means this hook
        # cannot answer, and the caller denies rather than guessing. Raising
        # here would exit 1, and **exit 1 does not block a PreToolUse call** --
        # the hook would print its refusal and let the edit through. Found by
        # tests/test_ownership_hook.py on its first run, in a hook whose own
        # docstring claimed it failed closed.
        return None
    return module


def decide(relative: str, branch: str, gate) -> str | None:
    """The denial message for this path on this branch, or `None` to allow.

    Split out from `main` so the decision table can be exercised without a git
    checkout and without a subprocess. `tests/test_ownership_hook.py` covers
    both: this function against every category, and the whole hook end to end
    against a real repository built in a temporary directory -- because a
    function with a unit test and no exercised caller is not a working path, a
    lesson this repository has now paid for twice.
    """
    track = gate.TRACKS.get(branch)
    if track is None:
        return None  # main, or a human branch: the split constrains the tracks

    if any(gate.matches(relative, pattern) for pattern in gate.SHARED):
        return None

    if any(gate.matches(relative, pattern) for pattern in gate.HUMAN_ONLY):
        return (
            f"CONTRACT: {relative} is reserved for the human ({branch} is "
            f"{track['name']}). .github/check_ownership.py lists it under "
            "HUMAN_ONLY and this edit would be a hard CI failure, not a review "
            "notice.\n\n"
            "Do not relocate your acceptance criterion into a file you do own -- "
            "that is a different criterion. Do not edit around it. Stop and "
            "report that the block requires a file you may not edit, naming it. "
            "AGENT_CONTRACT.md: an agent that believes the contract is wrong "
            "stops and says so."
        )

    if any(gate.matches(relative, pattern) for pattern in track["forbidden"]):
        return (
            f"CONTRACT: {relative} belongs to {track['owner']}, and you are "
            f"{track['name']} on {branch}. That track may be editing it right "
            "now in the other worktree.\n\n"
            "If your block genuinely needs a change there, stop and report it as "
            "a change to propose, not one to make."
        )

    return None


def is_shared(relative: str, gate) -> bool:
    return any(gate.matches(relative, pattern) for pattern in gate.SHARED)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        # Nothing identifies a repository yet, so there is nothing to enforce.
        return ALLOW

    if payload.get("tool_name") not in WATCHED_TOOLS:
        return ALLOW

    target = (payload.get("tool_input") or {}).get("file_path")
    cwd = payload.get("cwd") or "."
    if not target:
        return ALLOW

    top = git(cwd, "rev-parse", "--show-toplevel")
    if not top:
        return ALLOW  # not a git checkout; this hook has no opinion
    root = pathlib.Path(top).resolve()

    try:
        relative = pathlib.Path(target).resolve().relative_to(root).as_posix()
    except ValueError:
        return ALLOW  # outside the checkout: a mutation copy, a scratch file

    branch = git(cwd, "rev-parse", "--abbrev-ref", "HEAD")

    gate = load_gate(root)
    if gate is None:
        if branch in ("feature/data-layer", "feature/model-eval"):
            return deny(
                f"Ownership hook could not import {root}/.github/check_ownership.py, "
                f"so it cannot say whether {relative} is yours to edit. It denies "
                "rather than guessing. Report this; do not work around it."
            )
        return ALLOW

    if is_shared(relative, gate) and branch in gate.TRACKS:
        sys.stderr.write(
            f"note: {relative} is SHARED -- owned by neither track. Allowed, and "
            "surfaced by CI for review. It is the seam, so say in your report why "
            "you moved it.\n"
        )

    refusal = decide(relative, branch or "", gate)
    if refusal is not None:
        return deny(refusal)

    return ALLOW


def _on_a_track_branch() -> bool:
    """Best effort, for the crash path only. Unsure is not a track branch."""
    try:
        branch = git(".", "rev-parse", "--abbrev-ref", "HEAD")
    except Exception:
        return False
    return branch in ("feature/data-layer", "feature/model-eval")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as error:  # noqa: BLE001 -- the posture is the point
        if _on_a_track_branch():
            raise SystemExit(
                deny(
                    f"Ownership hook crashed: {error!r}. It cannot say whether "
                    "this edit is in your lane, so it refuses. Report it; do not "
                    "work around it by using a shell command to write the file."
                )
            )
        raise SystemExit(ALLOW)
