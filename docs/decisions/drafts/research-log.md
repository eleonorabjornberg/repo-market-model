# Draft: every result adds a research-log entry, and every directive names its hypothesis (#638)

**Status: a draft for Eleonora, not in force.** Drafted by the pull request that closes #638, as that directive
asks. It takes effect only when she merges the amendment below into `docs/decisions/workflow.md`.

## Why

The research plan (`docs/research/plan.md`) and the log (`docs/research/log.md`) are only worth having if they stay
current. `scripts/check_research_log.py`, run in CI, refuses a pull request that changes a result page or a
declaration without a log entry for its directive. This amendment makes that a rule of the workflow, not only a
check.

## The amendment to `workflow.md`, as drafted

---

## The research log

Decided by Eleonora, (date). Every new directive names its hypothesis (H1 to H10 in `docs/research/plan.md`) and the
step it serves. Every pull request that produces a result (a new or changed `docs/pivot/*-result.md`, or a new or
changed declaration or candidate under `metadata/`) adds an entry to `docs/research/log.md` that names its
directive, in the format `scripts/check_research_log.py` states. CI refuses a pull request that does not. Changes to
`docs/research/plan.md` are hers or are relayed rulings that the change cites. Work that serves no step goes to the
auditor's `avenue` list, not to the queue.

---
