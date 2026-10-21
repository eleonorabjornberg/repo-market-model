---
name: long-run
description: Run a step of repo-market-model expected to take more than about two hours (walk-forward refits, power studies, long simulations) without losing it to a session timeout. Use before starting any such step, in the cloud or locally.
---

# Long runs

A long step is never run in a cloud session, where it can run out of time and lose its work. It runs overnight on
Eleonora's Mac (`docs/decisions/workflow.md`, "Long runs go to her Mac").

1. **Commit the script and the exact commands first**, and push the branch, so the run is reproducible from the branch.
2. **Comment `needs-mac:` on the PR** with the paste, complete and ready to run, so it lives on GitHub and not in a
   session. The orchestrating session hands it to her in the 5 pm message; she runs it overnight. Its shape:
   ```
   bash -s <<'EOF'
   set -euo pipefail
   [ -d ~/rmm-<N> ] || git clone -b <branch> https://github.com/eleonorabjornberg/repo-market-model ~/rmm-<N>
   cd ~/rmm-<N> && git fetch origin && git checkout <branch> && git merge --ff-only origin/<branch>
   source ~/rmm-venv/bin/activate   # Python 3.11.17, numpy and scikit-learn at the versions CI's ml job pins
   python -c "import sys, numpy, sklearn; print(sys.version, numpy.__version__, sklearn.__version__)"
   <the exact commands> > ~/<N>.log 2>&1
   git add <the result paths> && git commit -m "#<N>: Mac run" && git push origin HEAD
   echo PUSHED
   EOF
   ```
   Say the expected hours, and whether it can run beside another paste.
3. **Do not push to the branch, or merge main into it, while her run is out**: her push would fail. The orchestrating
   session says on the PR when a run has started.
4. **Record the environment** in the PR: Python, numpy and scikit-learn versions of the run.
5. Split a long run into independent pieces (per horizon, per regime, per seed), each writing its own output file, and
   make the scoring step score only the pieces that exist, so a lost piece costs only itself and a re-run skips what
   finished.
6. Her pushed results are finished by a cloud session like any other branch.
