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

## Mutations are the evidence, and they are not optional

Every new guard gets a recorded mutation.

- Run it in a **disposable copy under `$HOME`**, never in the mount.
- Copy `data/`, `.github/`, `metadata/`, `.gitignore`, the root Markdown and
  `docs/PROJECT_STATUS.md` into that copy. The docs-freshness guard reads the last three
  and their absence is a kill that looks real and is not.
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

- **Stdlib only. No install step. Python 3.10**, declared in `pyproject.toml`; the package
  does not import on 3.11 and that is a known, unfixed finding, not something to fix inside
  another block.
- Leakage guards raise `LookAheadError`, never `assert`. Data guards raise `ValueError`.
- **The frozen funding panel is gitignored and is not in your worktree.** No block may
  depend on reading it. Fixtures only.
- **Do not move a published figure.** `docs/runs/` holds records of runs that happened. If
  a change would alter what a re-run produces, that is a report, not a rewrite of the
  record.
- **Push your own branch only.** Never `main`, never a merge, never a rebase. Hand the human
  the command.
- You have no GitHub credentials and no network route to the NY Fed, FRED or ALFRED.
  Fetches are the human's.

## This file, and `.claude/`

Both are `HUMAN_ONLY`. An agent that can edit its own standing rules, or the hook that
enforces the contract, can edit around the contract — which is the one thing
`AGENT_CONTRACT.md` forbids outright. If a rule here is wrong, **say so in your report.**
That is a human edit, not an exception you grant yourself.
