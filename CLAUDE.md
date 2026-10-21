# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# repo-market-model — standing rules

Read this first. **This file summarises; the tracked decision documents decide.** Where it
disagrees with `docs/decisions/`, `docs/process/AGENT_CONTRACT.md`, `PLAN.md`,
`docs/DATA_QUALITY_DECISIONS.md` or `REPRODUCIBILITY.md`, they win and this file is the bug.

## The current direction

The direction is not in this file. It is the top block of the "Directive queue" issue (#46): the primary and
secondary goals, the research plan H1–H10 (`docs/research/plan.md`), what is paused, what gates the queue, and her
standing orders (among them: long runs go to her Mac with a `needs-mac:` comment). Read it first, and the ruling
comments on your directive:

```
gh api repos/eleonorabjornberg/repo-market-model/issues/46 -q .body
```

Every directive names its hypothesis and step. A result from a model that does not read calendar days at the target
day is provisional (`docs/research/provisional-calendar-register.md`). A session starts from
`docs/pivot/next-session.md`; `docs/archive/` is not binding.

## How work happens

`docs/decisions/workflow.md` decides this.

- **One session, one branch, one pull request.** Branch from `origin/main` (directive branches are named
  `directive/<issue>-<what-it-does>`). Push only your own branch, as `git push origin HEAD`, and open a PR.
  **Never push to `main`.**
- **`main` is the only integration point.** A PR merges when CI (`tests.yml`) is green and it has been reviewed.
- **The PR description is the record of the work.** It carries what changed, the base SHA, the hypothesis and step,
  the panel digest if a panel was built, the result tables, what was checked, and what was *not* checked.
- **Judgement calls are hers.** Anything that changes what the project claims or how it decides — a new rule, a
  threshold, a data meaning, a published figure — goes to an issue labelled `needs-eleonora`, or to a clearly marked
  question in the PR. Do not settle it in code.
- **`docs/decisions/` records her decisions.** A PR may *draft* a decision record for her to review, and must say so in
  its description. A decision is in force only once she has merged it.
- **Research log, one file per entry.** Each entry is a file under `docs/research/log/`, named like
  `2026-10-20-model-01037-H5-step3.md`. `docs/research/log.md` is assembled from them and never hand-edited;
  `python3 scripts/check_research_log.py check` validates the entries.
- **Publishing a record** follows `docs/decisions/publish-rule.md`: a PR that adds the records and regenerates the
  blocks rendered from them (`python3 scripts/emit_results.py`) in the same commit. Generated blocks are never
  hand-edited.
- **Built on main, never committed** (#928): the results page (`site/index.html`), its data (`docs/visual/data/`) and
  the assembled `docs/research/log.md` are gitignored. A PR changes only their inputs (log entry files, records, the
  template, the scripts). `scripts/check_built_outputs.py` fails a PR that adds or edits one. To read them locally:
  `python3 scripts/emit_visual.py` and `python3 scripts/check_research_log.py assemble`. The newcomer layer ("Start
  here") is part of that page.
- **Committed generated files** are regenerated in the PR that changes their inputs, never hand-edited:
  `docs/status.json` (`scripts/emit_status.py`, from `PLAN.md`, top-level `docs/runs/`, `metadata/events.json`,
  `pyproject.toml`; commit it after the input change, since it is stamped with that commit, and `git fetch
  --unshallow` first in a shallow clone) and `docs/pivot/progress.md` with `docs/research/progress.json`
  (`scripts/emit_progress.py`). After merging main, a conflict in these is mechanical: regenerate in a separate commit.

## The science rules

- **Information set:** `docs/decisions/information-set.md`. A forecast uses exactly what was public at its decision
  instant (16:00 the business day before), read per field. Leakage guards and staleness guards both have to hold.
- **Calendar first** (Eleonora, 20 October 2026). A repo-market model that does not read calendar days at the target
  day (quarter-end, month-end, tax dates, Treasury settlements, scheduled IORB) is wrong. A new spread model reads
  them, on direct pairs. A result from a model that did not, or that learned them one row off (the #914 class), is
  provisional until re-run, and is listed in `docs/research/provisional-calendar-register.md`.
- **Calendar and scheduled columns at the target day.** `asof` rule 2 serves a calendar column
  (`contract.CALENDAR_FEATURES`) or a `scheduled_availability` field from the target row. A one-step fitter (row `p`
  against the spread of `p + 1`) would learn it a day off, so `repo_model.one_step_guard` makes such a fit raise
  `ValueError`. Train on direct pairs (`training_pairs="direct"`) or drop the column.
  `one_step_guard.ONE_STEP_ALLOW_LIST` holds the only exemptions (frozen declarations, some with an end date); adding
  to it is her decision.
  See `docs/pivot/one-step-guard-947.md`.
- **Scoring protocol v1** (`docs/decisions/scoring-protocol.md`, `repo_model.scoring_protocol`,
  `repo_model.protocol_benchmarks`) gates all new scoring. Only prospective confirmation days give a verdict;
  development data never does. H5's primary score is grid CRPS averaged over h = 1–5, with upper-tail twCRPS as key
  secondary, against benchmarks B1, B2 and B3, on a studentized stationary bootstrap. The +5 bp judge is retired as a
  decision rule. A development figure is paired, carries an interval, and is split by regime and by pressure-day type;
  a pooled figure alone is not a result.
- **The lockbox:** `docs/decisions/lockbox.md` and `metadata/lockbox.json`. No comparison scores a locked day; every
  scoring entry point refuses one.
- **Never edit a published record in place.** `docs/runs/` holds runs that happened. Re-score and publish anew, or
  archive with a note saying why. A provisional result is marked by the register, not edited.
- **Point-in-time data rules**: `docs/process/AGENT_CONTRACT.md` (panel schema, the as-of rule, the forecast and
  splitter interfaces) and `docs/DATA_QUALITY_DECISIONS.md`.
- Leakage guards raise `LookAheadError` (`repo_model.splits`), never `assert`. Data guards raise `ValueError`.
- **Dependencies:** `src/` is stdlib-only, except `src/repo_model/ml.py` and `tests/test_ml.py`, which may use the `ml`
  extra (numpy, scikit-learn). `tests/test_dependency_boundary.py` enforces this. Notebooks may use pandas and
  matplotlib. A new package in `src/` is her decision.
- **Python:** whatever `pyproject.toml` declares (3.11 only). Newer interpreters run, but move published figures in their
  last digits. Changing that ceiling is a decision about exact versus tolerant reproduction, not a side effect of a PR.

## How the code fits together

```
data/ snapshots (checksummed) + metadata/ (sources, release lags, event windows, lockbox)
  -> panel build        ingest.py, data.py, cli_data.py          (cli build / verify-panel)
  -> as-of read          asof.py, contract.py, splits.py          (LookAheadError, staleness)
  -> models              baseline.py (persistence, climatology, ARX, ...), ml.py (gradient-boosted quantiles)
  -> scoring             scoring_protocol.py, protocol_benchmarks.py, metrics.py, cli_eval.py
  -> records             docs/runs/ (published), docs/research/*-result.md (development evidence)
  -> generated pages     scripts/emit_results.py, emit_visual.py, emit_progress.py, emit_status.py
```

- The command-line entry point is the `cli` module, which `pyproject.toml` also installs as a console script; its
  subcommands live in `cli_data.py` and `cli_eval.py`.
- `scripts/` holds the generators and checkers above, plus one script per study, named for its issue
  (`b3_orientation_1014.py`) and paired with `docs/research/<name>-result.md`, often a `result.json`, and a test.
  A new study follows the same pattern; shared logic belongs in `src/`.
- `tests/fixtures/snapshots/` holds the tracked inputs the published panel builds from; `tests/built_outputs.py`
  builds the gitignored pages for the tests.

## Tests

- **Write the test first and watch it fail.** A new leakage, availability or staleness guard also gets one recorded
  mutation that kills it: the mutated line, and the exception type the failing test raised. The record goes in the
  test's docstring. Other code needs no mutation ritual; CI and review cover it.
- **Before you ask for review, run `python3 scripts/pre_review.py --base origin/main` and the test modules your change
  touches.** The full suite runs in the pull request's CI, in its shards (`docs/decisions/workflow.md`, "Fewer round
  trips"); read it with `gh pr checks`.
- **CI runs with networking disabled** (`unshare --net`), in shards from `scripts/ci_shards.py`. A test that quietly needs
  the network fails there.
- **Zero `expectedFailure` is load-bearing.** Skip counts vary by environment and mean nothing.
- **Never put a count in an acceptance criterion or a published page.** `tests/test_docs_freshness.py` also refuses a
  hand-written future date, a `repo_model.cli` command that no longer parses, and a Python version other than the
  declared one. Run it after any edit to Markdown.

## Commands

Use a 3.11 interpreter. Outside the `rmm` environment, `python3` may be newer: use `python3.11` or a 3.11 venv, with
`pip install '.[ml]'` for the `ml.py` tests.

```
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests
PYTHONPATH=src:tests python3 -m unittest test_module.ClassName
PYTHONPATH=src:tests python3 -B -m unittest $(python3 scripts/ci_shards.py modules --shard 1)
PYTHONPATH=src python3 -m repo_model.cli <subcommand>
python3 examples/walkthrough.py
```

- A class-targeted run needs `tests/` on the path and the bare module name. The dotted form
  (`tests.test_module.ClassName`) fails on the modules that import from `test_contract`.
- Before asking for review, also run the checks CI runs on the generated files:

  ```
  python3 -B scripts/emit_visual.py --check
  python3 -B scripts/emit_progress.py --check
  python3 -B scripts/emit_status.py --check
  python3 -B scripts/check_research_log.py check
  python3 -B scripts/check_built_outputs.py
  ```

- The published panel builds from the tracked fixtures in seconds, with no network. The exact build and verify commands
  are in `REPRODUCIBILITY.md` and `docs/pivot/next-session.md`.
- `build --source` takes the snapshot **directory** name, not the registry id.
- Fetching needs network access to the NY Fed, FRED, ALFRED or Treasury. FRED serves the latest revised vintage, so a
  re-fetch does not reproduce an old snapshot's bytes.

## This file, and `.claude/`

Both are Eleonora's. A PR may propose changes to them, and must say so in its description. Nothing here is changed
without her review. `AGENTS.md` only points here. CI's `owner-attested` job (`scripts/owner_attested.py`) treats a
change to either as binding, like the lockbox, the live pin and registrations: the PR appends an entry to
`metadata/owner_attestations.json` citing a `GO #<issue>` comment she posted herself. A session never posts that
comment for her.

`.claude/` holds the hooks that enforce some of these rules before an action (`hooks/`: no push to `main`, no
`GO #<n>` comment, no commit of a built file, the documentation guards after a Markdown edit, the pre-review checks
before stopping), the subagents (`agents/`: implementer, reviewer, auditor, `pr-remerger`, `finding-triager`), the
skills (`skills/`: `new-study`, `publish-record`, `register-producer`, `long-run`, `directive-orchestrator`,
`remerge-branch`, `daily-decision-message`) and every routine's instructions (`routines/`, with its README). Eleonora
works in cloud sessions only: nothing a session follows lives outside this repository.

## Delegated review

Until Eleonora revokes it in writing, queued pull requests are reviewed and merged by the "Directive loop" routine
(a Claude Code cloud session in the `rmm` environment), under "Delegated review" in `docs/decisions/workflow.md`. Once
she has ruled on the judgement call a `needs-eleonora` pull request waits on (her own GitHub comment, or a ruling the
orchestrating session relays from chat), the reviewer may merge a pull request that implements exactly that ruling.
Decision records, registrations, the lockbox, the live record and its pin, and changes to this file or `.claude/` still
need her own GitHub action (#256). Everything else in this file still applies.
