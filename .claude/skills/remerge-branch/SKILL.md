---
name: remerge-branch
description: Merge origin/main into a pull request's branch of repo-market-model when GitHub reports a conflict (or main changed what the branch depends on), resolving the mechanical parts by regeneration, never by hand. Use for a `dirty` PR, a held merge that now conflicts, or a resync.
---

# Remerge a branch

A mechanical conflict is one in generated or built files, or a research-log conflict where both sides only appended
entries (`docs/decisions/workflow.md`, "Mechanical escalations"; #46's research-log ruling of 15 October 2026).
Anything else (code, tests, metadata, a record in `docs/runs/`, hand-written docs, an edited log entry) is not
mechanical: stop and comment on the PR naming the paths.

1. **Check first.** Never push to a branch a Mac run is out on: read the PR's comments for a run that has started and
   not yet pushed ("Do not push to this branch … until that commit lands"). Then decide whether a merge is needed at
   all: only when GitHub reports a conflict, or when, since the merge base, main changed `src/`, `metadata/`,
   `tests/fixtures/snapshots/` or a file the branch also changes
   (`git diff --name-only $(git merge-base origin/main HEAD) origin/main`).
2. **Merge** in a full clone (`git fetch --unshallow` if shallow), with the neutral identity:
   ```
   git -c user.name="repo-market-model orchestrator" -c user.email="orchestrator@users.noreply.github.com" merge origin/main
   ```
   A merge commit; never rebase, never force-push.
3. **Resolve.**
   - Files built on main and never committed (#928, #946: `site/index.html`, `docs/visual/data/`,
     `docs/research/log.md`, `docs/pivot/progress.md`, `docs/research/progress.json`): remove them from the branch
     (`git rm --cached`); `scripts/check_built_outputs.py` lists what must not be tracked.
   - Committed generated files (`docs/status.json`, the blocks between `<!-- generated: … -->` markers): take either
     side, then regenerate in a separate commit after the merge, in this order: `python3 scripts/emit_results.py`,
     `python3 scripts/emit_visual.py`, `python3 scripts/emit_status.py`.
   - Research-log entries are one file per entry under `docs/research/log/` and do not conflict; a PR that still
     carries entries in `log.md` moves them into entry files, with no entry's text changed.
4. **Check** with `python3 scripts/pre_review.py --base origin/main`; every check must pass.
5. **Push** with `git push origin HEAD`, then comment once on the PR: "Merged origin/main at <sha> to clear a
   mechanical conflict in <paths>; regenerated with the repo's scripts; no hand edits." Its CI then runs on the new
   head; a reviewer reviews the author's changes, not this merge.
