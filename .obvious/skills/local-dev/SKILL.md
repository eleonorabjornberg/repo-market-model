---
name: local-dev
description: Bring a clean checkout of repo-market-model to a green suite and a working CLI in one pass
---

# local-dev — how this repository runs

Durable record of the onboarding run on 2026-09-17. Everything below was
executed and observed on sandbox snapshot `ilpqiz9twy0oq9kmlvofp`.

## Requirements

- An interpreter inside the declared range `>=3.9,<3.12`. `pyproject.toml` is
  the single declaration, and a suite guard fails the run on an interpreter
  outside it. The sandbox image ships `python3` at 3.13.14 — outside the
  range — so create a 3.11 virtual environment first.
- No services, no secrets, no required environment variables. `PYTHONPATH=src`
  is the only setting the core needs; `REPO_MODEL_REQUIRE_ML=1` makes the ml
  cases fail rather than skip when the extra is missing.
- The core is standard library only: nothing to install for the suite or the
  sample workflow. Only `src/repo_model/ml.py` needs the `ml` extra
  (numpy, scikit-learn, bounded in `pyproject.toml`).

## Procedure

1. `uv venv --python 3.11 .venv`
2. `uv pip install --python .venv ".[ml]"`
3. Stdlib-only suite: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -B -m unittest discover -s tests`
4. Suite with the ml extra: `REPO_MODEL_REQUIRE_ML=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -B -m unittest discover -s tests` — the gradient-boosted cases dominate the runtime, so give the run room or start it detached.
5. Sample workflow, each command exiting 0 and writing a JSON report: the
   four invocations listed in `../../obvious.md` (audit, persistence
   backtest, compare, climatology exceedance-backtest), then
   `.venv/bin/python examples/walkthrough.py` for the same four in-process.
6. Strongest check: `.venv/bin/python scripts/reproduce_milestone_a.py`
   re-derives the published persistence record exactly from tracked inputs.
   The suite runs the same function, so a green suite already covers it.

## Observed results (2026-09-17)

- Both suite runs green (`OK`). The stdlib-only run skips the ml and
  `data/raw` cases; the ml run leaves only the `data/raw` snapshot skips,
  expected in a clone without the gitignored inputs.
- All four CLI commands and the walkthrough exited 0 and produced their
  reports under `/tmp`.

## Gotchas recorded for the next worker

- **Interpreter guard.** The suite refuses an interpreter outside the
  declared range. Do not edit `pyproject.toml` (human-owned) to widen it;
  pick a 3.11 environment instead.
- **Bytecode caching.** Always run with `-B` and `PYTHONDONTWRITEBYTECODE=1`;
  a stale `__pycache__` once produced a false mutation result here, and CI
  does the same.
- **Tracked Markdown is policed.** `tests/test_docs_freshness.py` scans every
  Markdown file a clone receives — including anything you add. No
  transcribed suite counts (say the suite reports `OK`; never put a numeral
  near the word), no dates in the future, every published CLI invocation must
  parse against the real parser, and subcommands recorded as deliberately
  unpublished must not appear as invocations. Run that module after writing
  any Markdown, before pushing.
- **Ownership.** `.github/check_ownership.py` plus the tripwire in
  `tests/test_contract.py` govern who may edit what. Root Markdown,
  `pyproject.toml`, `scripts/`, `examples/`, `notebooks/`, `docs/figures/`,
  `docs/decisions/`, `.github/`, `.claude/` and `.gitignore` are human-only.
  The gate skips branches that are not track branches, but the rules still
  apply in review.
- **Two subcommands are deliberately unpublished** because they exit on
  things a clean clone does not have (a contact address, the frozen panel).
  They are named, with their reasons, in `tests/test_docs_freshness.py`; do
  not publish invocations of them in any Markdown.
- **Skip counts are not acceptance criteria.** They vary with whether
  `data/raw/` snapshots are present; `REPRODUCIBILITY.md` says so expressly.
