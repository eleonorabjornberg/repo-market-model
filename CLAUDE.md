# repo-market-model — standing rules

Read this first, then `AGENT_CONTRACT.md`. **This file summarises; the tracked decision
documents decide.** Where this disagrees with `AGENT_CONTRACT.md`, `PLAN.md`,
`docs/DATA_QUALITY_DECISIONS.md` or `REPRODUCIBILITY.md`, they win and this file is the
bug.

## Which checkout am I in?

Your branch says. Run it before anything else:

```
git rev-parse --abbrev-ref HEAD
```

| Branch | Where | Who you are |
|---|---|---|
| `main` | `repo-market-model` | the **integration checkout** — no track work happens here |
| `feature/data-layer` | `../rmm-data` | **Track A**, the data layer |
| `feature/model-eval` | `../rmm-model` | **Track B**, model and evaluation |

**If you are on `main` and you were asked to do track work, you are in the wrong folder.
Say so and stop.** Do not switch branches and do not create a worktree to get around it.
What legitimately happens on `main`: reading history, inspecting both branches, running the
suite, and human-authored edits to the documents and files reserved for the human.

## Step 0 — ownership, before you read the rest of a brief

List every file the block will create or modify and check each one against
`.github/check_ownership.py`, **using the gate's own `matches()`, not by eye.** If any is
`HUMAN_ONLY`, or is in your track's forbidden list, **stop and report before writing
anything.**

Do not relocate the acceptance criterion into a module you do own. That is a different
criterion, and it hides the defect instead of surfacing it. `AGENT_CONTRACT.md`: an agent
that believes the contract is wrong stops and says so; it does not edit around it.

This step exists because a block was once queued to a track whose three files were all
human-owned, and **every stated precondition passed** — branch, merge base, greps, a green
suite. All of them described the state of the tree and none asked who was allowed to change
it. A `PreToolUse` hook now refuses such an edit before it happens
(`.claude/hooks/ownership_guard.py`), but the hook cannot see a write performed through
`Bash`, so this step is still yours.

## The block protocol

One block, then stop and report. Never two.

1. Run the block's **preconditions** first, exactly as written. If any disagrees with its
   stated expectation, **stop and report which one.** Do not adapt the block to the
   repository you found.
2. `grep -c` **exits 1 when it counts none.** An `expect 0` line printing `0` is the
   precondition *passing*, not a failing command. Only the printed number decides.
3. Each brief greps for a class the previous block was required to create. That is "the
   block before this one landed", made mechanical. A `0` there is worth more than starting.
4. **One acceptance criterion per block, named by module path and test name, and it is also
   the mutation target.** If implementing block *n* appears to require a change block *n+1*
   owns, that is a stop-and-report, not a judgement call.
5. Read only the block you were given. Reading ahead is how two criteria end up in one
   block.
6. **A brief that asks you to fix a defect carries a command that shows the defect on the
   current tree.** Run it with the preconditions. If it shows nothing, the defect is not
   there: stop and report, and do not go looking for a version of it that is.
7. **A negative result is a finding.** "The defect is not there", "the data is complete",
   "the premise is false" -- whatever closes a question goes into a tracked document or a
   tracked test docstring in the commit that closes it. A gitignored memo is where a
   finding goes to be re-derived by the next block.

## Mutations are the evidence, and they are not optional

Every new guard gets a recorded mutation.

- Run it in a **disposable copy under `$HOME`**, never in the mount.
- Make the copy from **git's own file list**, not from a list of directories:

  ```
  BR="$(git rev-parse --abbrev-ref HEAD | tr / -)"; rm -rf "$HOME/mutation-copy-$BR"-*
  COPY="$HOME/mutation-copy-$BR-$(git rev-parse --short HEAD)"; mkdir -p "$COPY"
  git ls-files -z --cached --others --exclude-standard | tar --null -T - -cf - | tar -xf - -C "$COPY"
  ```

  The path is per branch and per commit because both tracks run mutations at once: a
  shared `$HOME/mutation-copy` was rebuilt by one track in the middle of the other's run,
  and scored a mutation against the wrong branch. The branch is the part that isolates —
  after a round's fast-forward both tracks sit on the same commit — and the first line
  clears only your own track's stale copies.

  That is every tracked file as your working tree has it, plus your new untracked files,
  and nothing gitignored -- no `.venv/`, no frozen panel. A hand-kept list of directories
  here was short twice: first `.claude/` (seven errors in an otherwise green control),
  then `notebooks/`, `examples/` and `pyproject.toml`. Every omission was a red control
  that looked like a finding and was a missing path, and both tracks reported and worked
  around each one. The copy is not a git work tree; guards that ask git skip or fall back
  there, which is why the copy has to be right by construction.
- `PYTHONDONTWRITEBYTECODE=1` and `python3 -B`. **Unmutated control green before and
  after.**
- Record the **exception type**, not just that something went red. A mutation that kills
  seven tests may be one incidental `ValueError` seven times.
- **The acceptance test and the mutation target must be the same test.** If they come
  apart, that is a finding to report, not a second test to add.
- If you change a fixture that an existing mutation record names, **re-run that mutation.**
  One had gone quiet under a new rule and the suite stayed green over a blunted guard.

The record goes in the **tracked test-module or class docstring** — not in a `RECORD.md`,
and not in a `docs/block-*/` folder, which is gitignored and would leave the record in one
checkout that no later session can read.

## Commands

```
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests
PYTHONPATH=src python3 -m repo_model.cli <subcommand>
```

- **Zero `expectedFailure` is load-bearing.** Skip counts vary by checkout and mean
  nothing. **Never put a count of any kind in an acceptance criterion**, or in a published
  document — `tests/test_docs_freshness.py` refuses it.
- Any edit to published Markdown must run `tests/test_docs_freshness.py`. It also refuses a
  hand-written future date, a `repo_model.cli` command that no longer parses, and a stated
  Python version other than the one `pyproject.toml` declares.
- `build --source` takes the snapshot **directory** name, not the registry id.

## Working rules

- **Stdlib only, except `src/repo_model/ml.py` and `tests/test_ml.py`**, which may use the
  optional `ml` extra (numpy, scikit-learn) -- `AGENT_CONTRACT.md`, working rules, and
  `tests/test_dependency_boundary.py`. A new package is the human's decision. Where a
  worktree has a `.venv/`, run the suite with `.venv/bin/python` in place of `python3`.
- **Python 3.9, 3.10 or 3.11**, which is what
  `pyproject.toml` declares -- `requires-python = ">=3.9,<3.12"`. Measured 10 Sep: 3.9.23,
  3.10 and 3.11.15 run the whole suite green; 3.12 and 3.13 fail the exact Milestone A
  reproduction, because 3.12's `sum()` rounds floats differently. That ceiling is a
  decision about exact versus tolerant reproduction, and not something to change inside
  a block.
- Leakage guards raise `LookAheadError`, never `assert`. Data guards raise `ValueError`.
- **The frozen funding panel is gitignored and is not in your worktree.** No block may
  depend on reading it. Fixtures only.
- **Do not move a published figure.** `docs/runs/` holds records of runs that happened. If
  a change would alter what a re-run produces, that is a report, not a rewrite of the
  record.
- **Your base, at session start and only then:** `git fetch origin`, then
  `git merge --ff-only origin/main`, before you edit anything. It either fast-forwards or
  refuses. A refusal means your branch holds commits `main` does not -- **stop and report
  it; do not merge, rebase or repair.** No other merge, ever, and never a rebase. The
  fast-forward carries CI's `docs/status.json` commits with it, which is why the base is
  yours to take rather than the human's to prepare: a human fast-forward was stale the
  moment CI committed behind it.
- **Push your own branch only**, as `git push origin HEAD`. Never `main`. If the push is
  refused, the commit stands; say so and hand the human the command.
- You have no network route to the NY Fed, FRED or ALFRED. Fetches are the human's.

## This file, and `.claude/`

Both are `HUMAN_ONLY`. An agent that can edit its own standing rules, or the hook that
enforces the contract, can edit around the contract — which is the one thing
`AGENT_CONTRACT.md` forbids outright. If a rule here is wrong, **say so in your report.**
That is a human edit, not an exception you grant yourself.
