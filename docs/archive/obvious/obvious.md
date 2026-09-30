# repo-market-model — agent guide

An auditable research pipeline for estimating funding pressure in the U.S.
Treasury repurchase-agreement market: a point-in-time data panel, purged
rolling-origin evaluation, and probabilistic scoring of next-day repo spread
forecasts against a persistence benchmark. It is a CLI research tool plus a
unittest suite — no web app, no servers, no databases, no containers.

## Stack

- **Language:** Python, supported range declared once in `pyproject.toml` as
  `requires-python = ">=3.9,<3.12"`. A suite guard fails the run on an
  interpreter outside that range, so use a 3.11 virtual environment (below);
  the sandbox image's default `python3` is 3.13.14 and is outside it.
- **Runtime dependencies:** none for the core. Everything a published result
  depends on is standard library; the optional `ml` extra (numpy,
  scikit-learn) is used only by `src/repo_model/ml.py`.
- **Package:** src layout — the importable package is `src/repo_model/`, found
  via `PYTHONPATH=src` with no install, or via `pip install ".[ml]"`, which
  also provides the console script declared under `[project.scripts]`.
- **Tests:** `unittest` (not pytest), discovered from `tests/`; CI runs the
  stdlib-only suite across the declared minor versions plus an ml-extra job.
- **Services:** none. The sample workflow needs no network. Commands that
  fetch real data write under the gitignored `data/raw/` and were not
  exercised during onboarding.

## Commands

From the repository root. One-time setup on a sandbox that has `uv`:

```bash
uv venv --python 3.11 .venv
uv pip install --python .venv ".[ml]"
```

Test suite — the stdlib-only path needs no installation at all:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -B -m unittest discover -s tests
REPO_MODEL_REQUIRE_ML=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -B -m unittest discover -s tests
```

The second form makes the ml cases fail rather than skip when the extra did
not install. Both report `OK` on this tree; the stdlib-only run skips the ml
and `data/raw` cases.

Primary user flow — the four published sample-workflow commands on the
synthetic fixture panel (the same ones `REPRODUCIBILITY.md` publishes; each
exits 0 and writes a JSON report):

```bash
PYTHONPATH=src .venv/bin/python -m repo_model.cli audit data/sample/daily_market.csv
PYTHONPATH=src .venv/bin/python -m repo_model.cli backtest data/sample/daily_market.csv --registry metadata/sources.json --feature spread_bps --decision-time 16:00 --model persistence --report /tmp/persistence_sample.json
PYTHONPATH=src .venv/bin/python -m repo_model.cli compare data/sample/daily_market.csv --registry metadata/sources.json --model-a persistence --feature-a spread_bps --model-b arx --feature-b spread_bps --feature-b sofr_volume --decision-time 16:00 --report /tmp/compare_sample.json
PYTHONPATH=src .venv/bin/python -m repo_model.cli exceedance-backtest --panel data/sample/daily_market.csv --thresholds metadata/stress_thresholds.json --registry metadata/sources.json --feature spread_bps --decision-time 16:00 --model climatology --report /tmp/climatology_sample.json
```

End to end in one command, no installation and no arguments:

```bash
.venv/bin/python examples/walkthrough.py
```

Exact reproduction of the published persistence record from tracked inputs
(no network, no gitignored files; the suite runs the same function):

```bash
.venv/bin/python scripts/reproduce_milestone_a.py
```

## Codebase map

The folder-level table is in `codebase-map.md`. Orientation in one line:
`src/repo_model/` holds the package — `data.py`, `ingest.py` and
`registry.py` are the data layer; `baseline.py`, `splits.py`, `metrics.py`,
`event_eval.py`, `tail_diagnostics.py` and `ml.py` are the model-and-
evaluation side; `contract.py` and `cli.py` are the human-owned seam both
sides build against. `tests/` mirrors that split, `scripts/` holds the
human-owned emitters and the reproduction entry point, `metadata/` the
machine-readable declarations, and `docs/` the published results, figures and
decision records.

## Standing rules — read before changing anything

`CLAUDE.md` carries the standing rules (`AGENTS.md` points there), and
`AGENT_CONTRACT.md` defines the enforced ownership split between the data
track, the model-eval track, and human-only files.
`.github/check_ownership.py` enforces it in CI, and `tests/test_contract.py`
carries a tripwire that fails when a governed path belongs to nobody.
Consequences for any agent here:

- Root Markdown, `pyproject.toml`, `scripts/`, `examples/`, `notebooks/`,
  `docs/figures/`, `docs/decisions/`, `.github/`, `.claude/`, `.gitignore`
  and the guard tests named in the contract are human-only. Do not edit them.
- Tracked Markdown is machine-checked by `tests/test_docs_freshness.py`, and
  Markdown you add is in scope the moment it is not gitignored: no
  transcribed suite counts, no dates in the future, every published CLI
  invocation must still parse against the real parser, and subcommands
  recorded as deliberately unpublished must not be published as invocations.
  Run that module after adding or editing any Markdown.

## Local verification summary

From the onboarding run on 2026-09-17; the durable procedure is
`skills/local-dev/SKILL.md`.

- Interpreter: CPython 3.11.16 in `.venv/` (uv-managed), inside the declared
  range, with the `ml` extra installed (numpy 2.0.2 and scikit-learn 1.6.1,
  inside the declared bounds).
- Stdlib-only suite: `OK`; the skips are the ml and `data/raw` cases.
- Suite with the ml extra and `REPO_MODEL_REQUIRE_ML=1`: `OK`; the remaining
  skips are `data/raw` snapshot cases, which need gitignored inputs a clean
  clone does not receive.
- All four sample-workflow CLI commands ran end to end, each exiting 0 and
  writing its report; the walkthrough ran the same four in-process.
- The exact-reproduction script re-derives the published persistence figures
  from tracked inputs; the suite exercises the same function, so a green
  suite covers it.

## Sandbox snapshot

- Snapshot id `ilpqiz9twy0oq9kmlvofp`, built 2026-09-17T14:36:30.757Z.
- Captured with the repository at `main` (commit `7422683`) and `.venv/`
  holding CPython 3.11.16 with the `ml` extra, so the commands above run
  there with no further setup.
