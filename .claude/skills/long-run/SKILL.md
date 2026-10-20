---
name: long-run
description: Run a step of repo-market-model expected to take more than about two hours (walk-forward refits, power studies, long simulations) without losing it to a session timeout. Use before starting any such step, in the cloud or locally.
---

# Long runs

A long step is never run in a cloud session, where it can run out of time and lose its work, and never as a heavy run
on Eleonora's Mac unless the rule below sends it there.

1. **Commit the script and the exact commands first**, and push the branch, so the run is reproducible from the branch.
2. **Up to six hours: the long-run workflow.** Once `.github/workflows/long-run.yml` is on `main` (PR #1043), start it
   on the branch (`gh workflow run long-run.yml --ref <branch> -f ...`, inputs as the workflow declares). It installs
   the pinned ml versions, runs the command, uploads the log, and commits the results under `docs/` and `metadata/`
   to the same branch with a neutral author. Its push does not start the PR's tests: push again afterwards, or ask
   the orchestrating session to re-run them.
3. **Longer than six hours, or it needs her machine:** comment `needs-mac:` on the PR with the commands
   (`docs/decisions/workflow.md`, "Long runs go to her Mac"). The orchestrating session hands her one paste; her pushed
   results are then finished by a cloud session.
4. **Record the environment** in the PR: Python, numpy and scikit-learn versions of the run.
5. Split a long run into independent pieces (per horizon, per regime, per seed) that each finish well inside the
   limit, and write each piece's output to its own file, so a lost piece costs only itself.
