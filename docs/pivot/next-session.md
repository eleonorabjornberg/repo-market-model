# Next session — start here

For sessions in the `rmm` cloud environment. Everything a session needs is in this repository. Every statement about
state below comes with the command that checks it, and the command's output wins over this page.

## Read, in this order

1. [`CLAUDE.md`](../../CLAUDE.md): the standing rules. One directive, one branch, one pull request, and never push to `main`.
2. [`docs/process/AGENT_CONTRACT.md`](../../AGENT_CONTRACT.md): the data and model interfaces.
3. `docs/decisions/information-set.md`, `workflow.md` and `publish-rule.md`.
4. [`lag-assessment.md`](lag-assessment.md): why every published record is being re-scored.
5. [`plan.md`](plan.md), and the directive you were given, from [`directives/`](directives) or its GitHub issue.
6. As needed: [`literature.md`](literature.md). `docs/archive/` holds superseded documents and is **not binding**.

## State, and how to check it

- **`main` carries the current rules.** It has this folder, `CLAUDE.md`, `docs/process/AGENT_CONTRACT.md` and the three decision
  records:

  ```
  git fetch origin && git log --oneline -5 origin/main
  ls docs/pivot docs/pivot/directives docs/decisions
  ```

- **The published panel rebuilds from tracked fixtures and verifies,** with no network:

  ```
  PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output /tmp/funding_panel.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
  PYTHONPATH=src python3 -m repo_model.cli verify-panel /tmp/funding_panel.csv --manifest metadata/funding_panel_manifest.json
  ```

  The expected digest is `4ddc3882…`, the panel with `reserve_balances` and `tga` in USD billions (#41). The
  records in `docs/runs/` were scored on the panel before that and before `quarter_end` became the last business day
  of the quarter (#44), digest `d8b716cf…`.
- **Nothing is re-scored yet.** Every record in `docs/runs/` was scored under the earlier rule.
- **The environment:** `/opt/rmm-venv` should exist, on Python 3.11, with numpy 2.4.6 and scikit-learn 1.9.1, the
  versions CI's ml job pins (#55). If it is missing or carries other versions, the environment's setup script did
  not apply. Say so rather than installing other versions, because scikit-learn's version can move gbm figures. The
  records in `docs/runs/` were fitted with numpy 2.0.2 and scikit-learn 1.6.1.

  ```
  ls /opt/rmm-venv/bin/python && /opt/rmm-venv/bin/python -c "import numpy, sklearn; print(numpy.__version__, sklearn.__version__)"
  ```

- **Open work:**

  ```
  gh issue list --repo eleonorabjornberg/repo-market-model --label directive
  gh pr list --repo eleonorabjornberg/repo-market-model
  ```

## The directives, in order

1. [`01`](directives/01-as-of-information-set.md): implement the as-of information set.
2. `02`, streamline the front door: done in PR #24.
3. [`03`](directives/03-rescore-publish.md): re-score and publish, after 01 merges.
4. [`04`](directives/04-retire-legacy-gates.md): retire the legacy ownership gates: done in PR #30.
5. [`05`](directives/05-review-ci-and-tests.md): review CI and the test suite, after 04.
6. The rest of [`plan.md`](plan.md) §7, each drafted as a directive when its turn comes.

## Open for Eleonora

Raise these as `needs-eleonora` issues if they block you. Do not settle them in code.

- **Public pages outside this repository** (the Notion advisor pages and the website) still carry the old figures.
  They are corrected from records after directive 03.
