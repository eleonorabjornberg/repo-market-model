# Decision: one session, one pull request, `main` the only integration point

**Status: decided.** This replaces the two-track workflow. `CLAUDE.md` summarises it.

## The rule

- Work is done one session per branch, and each branch ends in a pull request against `main`.
  Nothing is pushed to `main` directly.
- A pull request merges when CI (`tests.yml`) is green and Eleonora has reviewed it.
- The pull request's description is the record of the work: what changed, the base SHA, the
  panel digest if a panel was built, the result tables, and what was and was not checked.
- Judgement calls go to her. They go to an issue labelled `needs-eleonora`, or to a clearly marked
  question in the pull request. Decision records are hers. A pull request may draft one for her
  review, and it is in force only once merged.
- Publishing follows `docs/decisions/publish-rule.md`.

## What is retired

- **Tracks A and B**, their worktrees and branches (`feature/data-layer`, `feature/model-eval`),
  and the round close that merged them in lockstep.
- **The Mac job lanes**: queues, heartbeats, `STOP`, and the overnight task that topped them up.
  The scripts stay on disk as a fallback. They are not part of the workflow.
- **The block protocol and the per-block verification ritual**: the ownership gate run by hand,
  test-name set arithmetic, the suite in a copy under `$HOME`, and mutation reproduction for every
  block. CI on the pull request replaces them. A recorded mutation is still required for a
  leakage, availability or staleness guard.
- In `AGENT_CONTRACT.md`, **"Tracks and ownership" and every "Ownership" subsection** are
  historical. The panel schema, the as-of rule, the interfaces and the data decisions still apply.

`.github/check_ownership.py`, its CI job and `.claude/hooks/ownership_guard.py` stay in place for
now. All three act only on the two track branch names, so they do not constrain this workflow.
Removing them is a later, separate pull request.

## Why

Three weeks of the old workflow produced a large verification apparatus and very little measured
science. Most of the entries in the project's error log were operational. They were reach problems
between the Mac and the VM, serialisation through a single scoring lane and a publish window, and
handoff documents drifting from the tree. One scoring run took well over an hour on the Mac, and
the same panel builds in seconds in a fresh cloud checkout. A workflow where every change is an
independent, CI-checked pull request removes the serialisation, and it removes the need for state
documents that restate what git already records.
