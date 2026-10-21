---
name: long-run
description: Run a step of repo-market-model expected to take more than about two hours (walk-forward refits, power studies, long simulations) without losing it to a session timeout. Use before starting any such step, in the cloud or locally.
---

# Long runs

A long step is never run in a cloud session, where it can run out of time and lose its work. It runs overnight on
Eleonora's Mac (`docs/decisions/workflow.md`, "Long runs go to her Mac").

1. **Commit the script and the exact commands first**, and push the branch, so the run is reproducible from the branch.
2. **Comment `needs-mac:` on the PR** with the commands: a fresh clone of the branch, the project's virtual environment
   at the declared Python, output to a log file, and a push of the results to the same branch. The orchestrating
   session hands her the paste in the 5 pm catch-up; she runs it overnight.
3. **Do not push to the branch, or merge main into it, while her run is out**: her push would fail. The orchestrating
   session says on the PR when a run has started.
4. **Record the environment** in the PR: Python, numpy and scikit-learn versions of the run.
5. Split a long run into independent pieces (per horizon, per regime, per seed), each writing its own output file, and
   make the scoring step score only the pieces that exist, so a lost piece costs only itself and a re-run skips what
   finished.
6. Her pushed results are finished by a cloud session like any other branch.
