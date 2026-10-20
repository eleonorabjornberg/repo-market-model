# Next session — start here

For every session working a directive, in the `rmm` cloud environment or elsewhere. Everything a session needs is in this
repository, except the current direction, which is the top block of the "Directive queue" issue. Every statement about
state below comes with the command that checks it, and the command's output wins over this page. Where this page
disagrees with the top block of the queue issue (#46) or a later ruling comment on your directive, they win, and the
disagreement is a `finding`.

## Read, in this order

1. **The current direction:** the top block of the "Directive queue" issue (#46), then the ruling comments on your
   directive. It sets:
   - the primary goal H5, the SOFR − IORB spread distribution in bp, and the secondary goal H9, richer targets;
   - the research plan H1–H10, each with its test and its kill rule;
   - that new +5 bp classification variants are paused.

   ```
   gh api repos/eleonorabjornberg/repo-market-model/issues?state=open -q '.[] | select(.title=="Directive queue") | .body'
   ```

   Progress beyond pass or fail, for every candidate with evidence, is on
   [the progress page](https://eleonorabjornberg.github.io/repo-market-model/progress.md) (data:
   [`progress.json`](https://eleonorabjornberg.github.io/repo-market-model/progress.json)): the spread
   forecast (H5), the ordinary-day ranking, the Brier difference against climatology, calibration per regime, the
   judge's tiers and the running variant count. It is built on main from the committed evidence by
   `python3 scripts/emit_progress.py` and published on the site; it is never committed (#928), and the same command
   writes an untracked local copy to `docs/pivot/progress.md`. Every figure on it is development evidence, not a verdict.
2. **The research plan:** `docs/research/plan.md` and the hypothesis manuals, once #638 has merged. Until then the plan
   block in the top of #46 is the plan. Your pull request names the hypothesis and the step it serves, and, once
   `docs/research/log.md` exists, adds an entry to it.
3. **The scoring protocol:** #640. No new scoring starts until Eleonora has decided it; once decided it is
   `docs/decisions/scoring-protocol.md`. Directives already running finish as exploration only: their results are logged
   and none is a verdict.
4. [`CLAUDE.md`](../../CLAUDE.md): the standing rules. One directive, one branch, one pull request, and never push to `main`.
5. `docs/decisions/information-set.md` (the as-of rule, with its leakage and staleness guards) and
   [`docs/decisions/lockbox.md`](../decisions/lockbox.md) (no comparison scores a locked day).
6. [`docs/process/AGENT_CONTRACT.md`](../process/AGENT_CONTRACT.md): the data and model interfaces. Then
   `docs/decisions/workflow.md` and `publish-rule.md`.
7. As needed: [`lag-assessment.md`](lag-assessment.md), the finding behind the as-of rule, and [`literature.md`](literature.md).
   `docs/archive/` holds superseded documents, among them the September plan and directive briefs, and is **not binding**.

## State, and how to check it

- **`main` carries the current rules.** It has this folder, `CLAUDE.md`, `docs/process/AGENT_CONTRACT.md` and the
  decision records:

  ```
  git fetch origin && git log --oneline -5 origin/main
  ls docs/pivot docs/decisions
  ```

- **The published panel rebuilds from tracked fixtures and verifies,** with no network:

  ```
  PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output /tmp/funding_panel.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
  PYTHONPATH=src python3 -m repo_model.cli verify-panel /tmp/funding_panel.csv --manifest metadata/funding_panel_manifest.json
  ```

  The expected digest is `4ddc3882…`, the panel with `reserve_balances` and `tga` in USD billions (#41). The
  records in `docs/runs/` are scored on it.
- **Days after 2026-09-03 are locked** ([`lockbox.md`](../decisions/lockbox.md)). The near-blind tier
  (2026-01-01 to 2026-09-03) was opened once for the final test (#151) and is ordinary history; the
  blind tier is not. Every scoring entry point refuses a scored day in a tier `metadata/lockbox.json`
  has not opened. The published records are scored before 2026-01-01, with `--end`:

  ```
  PYTHONPATH=src python3 -m repo_model.cli backtest /tmp/funding_panel.csv --registry metadata/sources.json --feature spread_bps --decision-time 16:00 --model persistence --minimum-history 61 --refit-every 21 --end 2025-12-31 --report /tmp/persistence.json
  ```

- **The records are re-scored** under the as-of rule (directive 03, #27), refitted every 21 scored days. The records
  scored under the earlier rule, on the panel before #41 and #44 (digest `d8b716cf…`), are in
  `docs/runs/archive/pre-asof/`.
- **The environment:** `/opt/rmm-venv` should exist, on Python 3.11, with numpy 2.4.6 and scikit-learn 1.9.1, the
  versions CI's ml job pins (#55). If it is missing or carries other versions, the environment's setup script did
  not apply. Say so rather than installing other versions, because scikit-learn's version can move gbm figures. The
  records in `docs/runs/` were fitted with those pinned versions; the archived ones with numpy 2.0.2 and
  scikit-learn 1.6.1.

  ```
  ls /opt/rmm-venv/bin/python && /opt/rmm-venv/bin/python -c "import numpy, sklearn; print(numpy.__version__, sklearn.__version__)"
  ```

- **Open work:**

  ```
  gh issue list --repo eleonorabjornberg/repo-market-model --label directive
  gh pr list --repo eleonorabjornberg/repo-market-model
  ```

## Where a new pressure-day candidate goes

New +5 bp classification variants are paused (the top block of #46), and the judge is held under #640's decision 6. This
section says where a candidate is declared if a directive asks for one; it does not invite new ones.

A candidate for the pressure-day judge (#374) is declared in a file of its own,
`metadata/pressure_judge/candidates/<name>.json` (its `role`, `features` and `calibration`), and nowhere else:
`metadata/pressure_judge.json` holds the bar, tiers, thresholds, horizons and status, and the judge loads the union
(#446). Two pull requests that each add a candidate then touch different files and do not conflict. Add the name to
`confirmation.candidates` in `metadata/pressure_judge.json` only if the candidate is to be looked at in the single
confirmation look. Commit the file before the candidate is scored: `scripts/pressure_judge.py` refuses an uncommitted or
edited declaration or candidate file. A pull request that still lists candidates in `pressure_judge.json` moves them into
files when it next merges main; that is a mechanical change.

## The directives

The queue is the open issue titled "Directive queue" (#46). Its lines, in priority order, are the directives; its
notation (`after`, `merge after`, `stack on`) is explained in its body. The September briefs `01`–`06` are done and are in
`docs/archive/directives-2026-09/`.

## Open for Eleonora

Raise these as `needs-eleonora` issues if they block you. Do not settle them in code. Her decisions are batched into one
message at 5 pm ET.

- **Public pages outside this repository** (the Notion advisor pages and the website) may still carry figures older than
  `docs/runs/`. They are corrected from records, on her instruction.
