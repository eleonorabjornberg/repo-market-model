# Academic methodology

## Research question

Can publicly observable funding, reserve, Treasury-settlement, dealer, money-fund,
and calendar variables forecast the next-day distribution of Treasury repo-market
pressure, including transitions into the upper tail?

The primary outcome is the SOFR spread to the administered reserve rate. Secondary
outcomes are SOFR dispersion, volume, and a pre-declared stress indicator.

## Claims the first version may support

- Predictive associations under rolling out-of-sample evaluation.
- Calibration of next-day conditional distributions.
- Robustness of forecasts to alternative public-data transformations.
- Scenario sensitivity under explicitly declared assumptions.

## Claims it may not support

- Causal effects of reserves, regulation, or Federal Reserve facilities without a
  separate identification strategy.
- Exact institution-level liquidity buffers from aggregate data.
- The true bilateral funding or collateral network.
- Reliable probabilities for unprecedented stress outside the support of the data.

## Reproducibility protocol

1. Save each raw response immutably.
2. Record retrieval time, complete request URL, byte count, and SHA-256 digest.
3. Keep raw and processed datasets out of Git; commit code and metadata.
4. Record release lags and revision behavior for every feature.
5. Build point-in-time panels using only information available at forecast creation.
6. Fit imputation and normalization inside each training window.
7. Use rolling-origin evaluation and untouched event holdouts.
8. Compare all models with persistence and transparent econometric baselines.
9. Publish uncertainty, ablations, and failed specifications alongside final results.

## Missing information

Missing aggregates may be imputed with time-aware statistical models. Missing
counterparty networks and collateral paths will be represented by posterior ensembles
subject to accounting, relationship, timing, and collateral constraints. Systemic-risk
results will be labelled robust only when they persist across plausible completions.

## Literature access

The project uses publisher-open articles, working papers, author manuscripts,
government publications, and institutional repositories. It does not circumvent
paywalls or access controls. Citations should identify the version actually analyzed.

