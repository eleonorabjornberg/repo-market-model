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

The initial vertical slice contains:

- a versioned daily data contract;
- source and publication-lag metadata;
- validation and accounting checks;
- a no-dependency persistence baseline with calibrated empirical intervals;
- time-ordered backtesting; and
- unit tests runnable with the Python standard library.

It intentionally does not yet claim to be an ML model. The persistence baseline is
the benchmark that every later statistical or ML model must beat out of sample.

## Quick start

```bash
cd repo-market-model
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m repo_model.cli audit data/sample/daily_market.csv
PYTHONPATH=src python3 -m repo_model.cli backtest data/sample/daily_market.csv
```

No installation is required for these initial commands.

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

See [PLAN.md](PLAN.md) for the implementation roadmap and [DATA.md](DATA.md) for
the data map.
