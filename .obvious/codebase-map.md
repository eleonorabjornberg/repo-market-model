# Codebase map — repo-market-model

Folder-level orientation, depth two. The importable package is a src-layout
Python package; `tests/` mirrors the module split; everything under
`scripts/`, the root Markdown, and the reserved `docs/` pages are human-owned
per `AGENT_CONTRACT.md` and `.github/check_ownership.py`.

| Path | What lives there |
|---|---|
| `src/repo_model/` | The package. `cli.py` is the human-owned dispatcher; `cli_data.py` and `cli_eval.py` register the subcommands. |
| `src/repo_model/data.py`, `ingest.py`, `registry.py` | Data layer (Track A): panel loading, point-in-time rows, source adapters, registry access. |
| `src/repo_model/baseline.py`, `splits.py`, `metrics.py`, `event_eval.py`, `tail_diagnostics.py`, `ml.py` | Model and evaluation (Track B): fitted models (persistence, ARX, threshold, rolling-residual, gradient-boosted), the purged rolling-origin splitter, scoring, event holdouts, tail diagnostics. `ml.py` is the only module that may import numpy/scikit-learn. |
| `src/repo_model/contract.py` | Human-owned shared seam: the quantile grid, the feature-to-source map, release-lag and tolerance validation. |
| `tests/` | unittest suite; modules mirror the src split, plus the guard tests (`test_contract.py`, `test_docs_freshness.py`, `test_dependency_boundary.py`, `test_ownership_hook.py`, `test_generated_results.py`). |
| `scripts/` | Human-owned emitters and entry points, including `emit_results.py`, `emit_status.py` and `reproduce_milestone_a.py`. |
| `metadata/` | Machine-readable declarations: the source registry (`sources.json`), stress thresholds, event windows, funding-panel manifest, archive manifests. |
| `data/sample/` | The synthetic twenty-five-row fixture panel the published sample workflow runs on. Not market data. |
| `docs/` | Published results and records: run records under `runs/`, decision records under `decisions/`, generated figures under `figures/`, plus the status and summary pages. `docs/status.json` is regenerated in CI from `PLAN.md`. |
| `notebooks/`, `examples/` | Human-owned. `examples/walkthrough.py` runs the four published commands end to end; the notebook is generated from its cells. |
| `.github/`, `.claude/` | CI workflows, the ownership gate `check_ownership.py`, and the Claude Code ownership hook. |
