# Repo Market Model

A probabilistic model of U.S. Treasury repo-market pressure built from public data,
with explicit extension points for confidential transaction, payment, balance-sheet,
and collateral-chain data.

The first target is deliberately narrow:

- Forecast the next-day distribution of `SOFR - IORB`.
- Forecast SOFR rate dispersion and transaction volume.
- Estimate the probability of entering a stressed funding regime.
- Explain predictions through reserves, Treasury settlement pressure, money-fund
  cash capacity, dealer intermediation, calendar effects, and recent market state.

The project treats internal liquidity buffers and missing network positions as
latent variables. It does not replace missing observations with a single invented
value. Later stages will generate an ensemble of market states constrained by
accounting identities and observable aggregates.

## Current status

The vertical slice contains:

- a versioned daily data contract, and a point-in-time panel loader;
- source and publication-lag metadata, with the release-lag → purge conversion
  owned by the data layer;
- validation and accounting checks;
- a no-dependency persistence baseline with calibrated empirical intervals;
- a purged rolling-origin splitter (the **scoring** holdout) whose leakage
  guards raise rather than assert;
- an event-holdout evaluator over frozen, checksummed stress windows (the
  **knowledge** holdout, kept deliberately separate from the scoring one);
- Brier skill against climatology with a Murphy decomposition, so reliability is
  reported apart from resolution;
- immutable, checksummed downloads from official public sources; and
- 335 tests runnable with the Python standard library.

It intentionally does not yet claim to be an ML model. The persistence baseline
is the benchmark that every later statistical or ML model must beat out of
sample.

## How the repository is built

The repository carries a second artifact alongside the model: a machine-checked
protocol for two AI coding agents working the same tree in parallel, in separate
git worktrees on separate branches. `AGENT_CONTRACT.md` is the single source of
truth for both; `.github/check_ownership.py` enforces the file-ownership split on
every pull request.

Two ideas from that protocol are worth naming here, because both are general:

1. **Shapes shared by both tracks are executable, and owned by neither.** A
   path-level ownership gate can enforce who writes a file, but not what a
   shared key means — a distinction the project paid for four times. Shapes both
   sides must agree on live in `src/repo_model/contract.py`, which both import
   and neither edits.
2. **The ownership list is asserted against the tree.** A list that is not
   tested silently stops describing the tree; five files had drifted out of it.
   `tests/test_contract.py` now fails if any module belongs to nobody.

`docs/state-of-main-*.md` is the long-form report on both the model and the
protocol, including what went wrong and what it cost.

## Quick start

```bash
cd repo-market-model
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m repo_model.cli audit data/sample/daily_market.csv
PYTHONPATH=src python3 -m repo_model.cli backtest data/sample/daily_market.csv
PYTHONPATH=src python3 -m repo_model.cli fetch nyfed-sofr
PYTHONPATH=src python3 -m repo_model.cli fetch fred-macro
```

No installation is required. Standard library only, by contract — a property that
is load-bearing for reproducibility rather than an aesthetic preference.

Run the full suite with bytecode caching disabled:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest discover -s tests
```

The `-B` is not decoration. Mutation testing on this repository once produced a
false green because CPython validates cached bytecode on modification time and
source size, and the mutations most worth testing are exactly the ones that
preserve source length. The report tells that story in full.

## Design principles

1. **No look-ahead:** features are timestamped by when they became observable.
2. **Forecast distributions:** tail probabilities matter more than tiny average
   rate improvements.
3. **Preserve identities:** reserves, payments, cash, collateral, and matched-book
   positions must reconcile.
4. **Separate structural zeros from missing trades:** a nonexistent relationship is
   not an unobserved transaction.
5. **Use ensembles for missing networks:** stress results must survive multiple
   plausible data completions.
6. **Keep forecasting separate from policy claims:** predictive ML does not, by
   itself, identify causal effects of a Fed intervention.

See [PLAN.md](PLAN.md) for the implementation roadmap, [DATA.md](DATA.md) for
the data map, and [METHODOLOGY.md](METHODOLOGY.md) for the academic protocol.
