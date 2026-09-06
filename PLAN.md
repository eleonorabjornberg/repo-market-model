# Implementation plan

## Objective and scope

Build a reproducible model of U.S. Treasury repo-market pressure that starts with
public daily data and can graduate to bank-level and intraday modeling if restricted
data become available.

Initial forecast horizon: next business day, later extended to five business days
and intraday nowcasting.

Primary targets:

1. `SOFR - IORB`, in basis points;
2. SOFR percentile dispersion;
3. SOFR transaction volume; and
4. probability that the market enters a stressed regime.

The system is a hybrid, not a single black box:

```text
observations -> latent liquidity state -> supply/demand estimates -> market clearing
                    |                                      |
                    +---------- probabilistic ML ----------+
```

## Phase 0 — Reproducible foundation (started)

- Define a point-in-time daily data contract.
- Record source, native frequency, release lag, revision behavior, and transformations.
- Add validation, missingness reporting, and accounting checks.
- Establish persistence and rolling-distribution baselines.
- Use rolling-origin evaluation; never use random train/test splits.

Exit criterion: one command validates a panel and produces a leakage-safe baseline
backtest.

## Phase 1 — Public U.S. dataset

Ingest and align:

- SOFR, its percentiles and volume; TGCR; BGCR;
- IORB, effective federal funds rate, ON RRP rate and usage;
- reserve balances, Treasury General Account, currency, and Fed securities holdings;
- Treasury auction, issuance, maturity, coupon, and settlement calendars;
- primary-dealer Treasury positions, financing, and settlement fails;
- money-market-fund assets, flows, repo holdings, Treasury holdings, and ON RRP use;
- Treasury bill yields, cash/futures basis proxies, volatility, depth, and bid-ask proxies;
- tax dates, holidays, month-end, quarter-end, and year-end indicators.

Every observation must carry an `available_at` timestamp or conservative release-lag
rule. Low-frequency series are joined as-of; values are not backfilled into dates on
which they were not yet known.

Exit criterion: frozen, checksummed modeling snapshots with provenance and a data
quality report.

## Phase 2 — Forecasting benchmarks and probabilistic ML

Benchmarks:

- last observation;
- rolling mean/quantiles;
- AR and ARX;
- threshold regression.

Candidate ML models:

- gradient-boosted trees for conditional mean and quantiles;
- calibrated classification for stress probability;
- hidden Markov or mixture-of-experts regimes;
- state-space model for the latent effective liquidity surplus.

Neural sequence models are deferred until the data volume and benchmark results
justify them.

Evaluation:

- rolling-origin backtests;
- pinball loss and interval coverage for quantiles;
- Brier score and calibration for stress probabilities;
- MAE by regime and calendar event;
- event holdouts including September 2019, March 2020, tax dates, Treasury
  settlements, and reporting dates.

Exit criterion: a model that beats persistence out of sample and remains calibrated
in the tails.

## Phase 3 — Latent reserves and payment needs

Estimate deployable liquidity rather than a reported internal buffer:

```text
deployable reserves = observed/estimated reserves - latent desired buffer
```

The desired buffer combines:

- predictable operational needs;
- a conditional tail estimate of maximum cumulative net outflow;
- regulatory liquidity needs; and
- a time-varying management overlay inferred from revealed repo-supply behavior.

Use a constrained state-space or Bayesian model with observable heads for repo
lending, rate spreads, payment timing, and facility usage.

Exit criterion: stable posterior intervals for aggregate effective liquidity, with
clear sensitivity to unobserved bank-level reserve distribution.

## Phase 4 — Repo supply, demand, and market clearing

Estimate separate schedules for:

- cash supply from banks, money funds, and other lenders;
- financing demand from dealers and leveraged investors;
- dealer intermediation capacity; and
- Fed facility outside options.

Impose:

- borrowing equals lending;
- facility-rate and no-arbitrage bounds;
- nonnegative quantities;
- monotone responses where economically required; and
- balance-sheet and collateral feasibility.

Exit criterion: coherent rate and volume predictions plus transparent
counterfactual scenarios.

## Phase 5 — Missing-data and network ensemble

- Infer relationship existence with a hurdle model.
- Infer edge sizes using entropy-regularized matrix completion under row/column totals.
- Preserve daily relationship persistence.
- Reconstruct possible collateral paths using security, quantity, timestamp, and
  reuse constraints.
- Sample many feasible networks rather than selecting one completion.
- Report which stress conclusions are robust across the ensemble.

Exit criterion: mask-and-reconstruct tests recover held-out observed edges and
aggregate identities within declared tolerances.

## Phase 6 — Stress engine

Iterate:

1. asset or funding shock;
2. collateral repricing;
3. margin calls and rollover decisions;
4. balance-sheet constraint breaches;
5. forced sales and funding withdrawal;
6. price impact and downstream defaults.

Exit criterion: historical replay and sensitivity reports, with no claim that a
single reconstructed network is the true network.

## Phase 7 — European extension

Add adapters for:

- public SFTR weekly aggregates;
- ECB MMSR aggregates;
- ICMA surveys;
- sovereign issuance and collateral data; and
- restricted SFTR/MMSR transaction data if access is obtained.

The European model must explicitly represent currency, sovereign issuer, collateral
eligibility, CCP/CSD, and cross-border settlement.

## Immediate next tasks

1. Populate the source registry and implement download adapters.
2. Build the first point-in-time daily panel.
3. Produce a missingness/revision report.
4. Backtest persistence and ARX benchmarks.
5. Add a gradient-boosted quantile model only after the baseline is frozen.

