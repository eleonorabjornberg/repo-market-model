# repo-market-model — standing rules

Read this first. **This file summarises; the tracked decision documents decide.** Where it
disagrees with `docs/decisions/`, `docs/process/AGENT_CONTRACT.md`, `PLAN.md`,
`docs/DATA_QUALITY_DECISIONS.md` or `REPRODUCIBILITY.md`, they win and this file is the bug.

## How work happens

`docs/decisions/workflow.md` decides this.

- **One session, one branch, one pull request.** Branch from `origin/main` and give it a
  name that says what it does. Push only
  your own branch, as `git push origin HEAD`, and open a PR. **Never push to `main`.**
- **`main` is the only integration point.** A PR merges when CI (`tests.yml`) is green and
  Eleonora has reviewed it.
- **The PR description is the record of the work.** It carries what changed, the base SHA,
  the panel digest if a panel was built, the result tables, what was checked, and what was
  *not* checked.
- **Judgement calls are hers.** Anything that changes what the project claims or how it
  decides — a new rule, a threshold, a data meaning, a published figure — goes to an issue
  labelled `needs-eleonora`, or to a clearly marked question in the PR. Do not settle it in
  code.
- **`docs/decisions/` records her decisions.** A PR may *draft* a decision record for her to
  review, and must say so in its description. A decision is in force only once she has merged
  it.
- **Publishing a record** follows `docs/decisions/publish-rule.md`. A publish is a PR that adds
  the records and regenerates the pages rendered from them (`python scripts/emit_results.py`)
  in the same commit. Those generated blocks are never hand-edited.

## The science rules

- **Information set:** `docs/decisions/information-set.md`. A forecast uses exactly what was
  public at its decision instant, read per field. Leakage guards and staleness guards both
  have to hold.
- **Benchmarks.** A headline claim is stated against as-of persistence (for a distribution)
  or climatology and a persistence-logistic model (for a pressure probability). It is paired,
  carries a bootstrap interval, and is split by regime and by pressure-day type. A pooled
  figure alone is not a result.
- **Never edit a published record in place.** `docs/runs/` holds runs that happened. Re-score
  and publish anew, or archive with a note saying why.
- **Point-in-time data rules are unchanged**: `docs/process/AGENT_CONTRACT.md` (panel schema, the as-of rule,
  the forecast and splitter interfaces) and `docs/DATA_QUALITY_DECISIONS.md`.
- Leakage guards raise `LookAheadError`, never `assert`. Data guards raise `ValueError`.
- **Dependencies:** `src/` is stdlib-only, except `src/repo_model/ml.py` and `tests/test_ml.py`,
  which may use the `ml` extra (numpy, scikit-learn). `tests/test_dependency_boundary.py`
  enforces this. Notebooks may use pandas and matplotlib. A new package in `src/` is her
  decision.
- **Python:** whatever `pyproject.toml` declares. Changing that ceiling is a decision about
  exact versus tolerant reproduction, not a side effect of a PR.

## Tests

- **Write the test first and watch it fail.** A new leakage, availability or staleness guard
  also gets one recorded mutation that kills it: the mutated line, and the exception type the
  failing test raised. The record goes in the test's docstring. Other code needs no mutation
  ritual; CI and review cover it.
- **Run the full suite in one process before you ask for review.** If it outlasts your shell's
  time limit, run it in the background and wait for it. Do not split it: some classes pass only
  when another class is loaded in the same run.
- **Zero `expectedFailure` is load-bearing.** Skip counts vary by environment and mean nothing.
- **Never put a count in an acceptance criterion or a published page.**
  `tests/test_docs_freshness.py` also refuses a hand-written future date, a `repo_model.cli`
  command that no longer parses, and a Python version other than the declared one. Run it
  after any edit to Markdown.

## Commands

```
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests
PYTHONPATH=src:tests python3 -m unittest test_module.ClassName
PYTHONPATH=src python3 -m repo_model.cli <subcommand>
```

- A class-targeted run needs `tests/` on the path and the bare module name. The dotted form
  (`tests.test_module.ClassName`) fails on the modules that import from `test_contract`.
- The published panel builds from the tracked fixtures in seconds, with no network. The exact
  build and verify commands are in `REPRODUCIBILITY.md`.
- `build --source` takes the snapshot **directory** name, not the registry id.
- Fetching needs network access to the NY Fed, FRED, ALFRED or Treasury. FRED serves the
  latest revised vintage, so a re-fetch does not reproduce an old snapshot's bytes.

## This file, and `.claude/`

Both are Eleonora's. A PR may propose changes to them, and must say so in its description.
Nothing here is changed without her review.

## Delegated review

Until directive 06 merges, queued pull requests are reviewed and merged by the review session in
`.github/workflows/directive-loop.yml`, under "Delegated review" in `docs/decisions/workflow.md`. Everything else in
this file still applies.
