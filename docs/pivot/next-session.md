# Next session — start here

Written at the pivot for sessions in the `rmm` cloud environment. Everything a session needs is in
this repository. Every statement about state below comes with the command that checks it, and the
command's output wins over this page.

## Read, in this order

1. [`CLAUDE.md`](../../CLAUDE.md): the standing rules. One session per branch per PR, and never push to `main`.
2. `docs/decisions/information-set.md`, `workflow.md` and `publish-rule.md`: the rulings of the pivot.
3. [`lag-assessment.md`](lag-assessment.md): the finding, its measured impact, its reach, and the fix.
4. [`plan.md`](plan.md): methodology, data, testing, workflow, the sequence, and the task briefs.
5. As needed: [`history.md`](history.md) (what the first three weeks built and what still stands) and
   [`literature.md`](literature.md) (borrowable methods and free data, with links).

## State, and how to check it

- **The pivot PR is merged into `main`.** It lands `CLAUDE.md`, the three decision records, this folder and
  `notebooks/scouting/`.

  ```
  git fetch origin && git log --oneline -5 origin/main
  ls docs/pivot docs/decisions
  ```

- **The published panel rebuilds from tracked fixtures and verifies.** No network is needed:

  ```
  PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output /tmp/funding_panel.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
  PYTHONPATH=src python3 -m repo_model.cli verify-panel /tmp/funding_panel.csv --manifest metadata/funding_panel_manifest.json
  ```

  The expected digest is `d8b716cf…`.
- **Nothing is re-scored yet.** Every record in `docs/runs/` was scored under the old rule. The lag assessment
  shows what that means.
- **The environment:** the `rmm` setup script should provide `/opt/rmm-venv`, with numpy 2.0.2 and
  scikit-learn 1.6.1. If `/opt/rmm-venv` is missing, the setup script did not apply. That matches a known
  bug where a selected custom environment is silently not used. Say so rather than installing other
  versions, because scikit-learn's version can move gbm figures.

  ```
  ls /opt/rmm-venv/bin/python && /opt/rmm-venv/bin/python -c "import numpy, sklearn; print(numpy.__version__, sklearn.__version__)"
  ```

- **An earlier cloud pilot** may have left a branch, `cloud-pilot/control-rescore`, that re-scores the old control.
  It is the reproducibility baseline for the *old* design, and is not for `main`.

  ```
  git ls-remote origin 'refs/heads/cloud-pilot/*'
  ```

## The tasks, in order

1. **The as-of PR.** This is the next session's task, and its brief is in [`plan.md`](plan.md) under "Brief — step 1".
   It implements `docs/decisions/information-set.md`: per-field as-of reads, scheduled inputs (including the
   approved auction-time settlement declaration), label observability, one fold grid, the staleness guard, and
   `--refit-every`. Acceptance is reproducing the scouting controls, not tuning to them.
2. **The streamlining PR** runs in a separate session, in parallel. Its brief is under "Brief — the streamlining PR":
   the README lead with a plain-English overview and figure, the Colab badge and `notebooks/00_overview.ipynb`, and the
   housekeeping.
3. **The re-score and publish PR**, after step 1 merges:
   - re-score persistence, gbm (none and cross_conformal) and the published funding declaration, plus the
     pressure-probability baselines (climatology and persistence-logistic);
   - archive the old records under `docs/runs/archive/pre-asof/`;
   - regenerate the pages.
4. **Then:** pressure model v1 and the scarcity indicator, the calibration re-diagnosis, the data additions, the model
   documentation and validation report, and the plain-language results page (plan §8).

## Decisions still pending Eleonora

Open each as an issue labelled `needs-eleonora` if it blocks you. Do not settle any of them in code.

- **The materiality rule** (plan §2). Until she adopts it, refused series stay refused.
- **Removing `.obvious/`.** It is left alone until she rules.
- **Retiring `.github/check_ownership.py`, its CI job and `.claude/hooks/ownership_guard.py`.** They act only on the
  two old track branch names, so they do not block this workflow. Removing them is a separate PR for her review.

## Outside the repository

- **The Mac lanes are retired.** Eleonora stops them on the Mac. No session touches the Mac checkout.
- **The Notion advisor pages and the website still carry the old claims:** next-day forecasting, Phase 2 "met" and the
  "no gaps" claim. They are corrected only after the re-score, from records.
