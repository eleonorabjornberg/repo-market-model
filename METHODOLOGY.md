# Academic methodology

## Status of this work

This is an academic exercise. Its purpose is to demonstrate that a forecasting claim
about a funding market can be made *defensibly* — with point-in-time provenance,
declared availability, honest holdouts, and evaluation that cannot quietly reward a
leak. It is not a production system and produces no investment advice. Where the
repository has not yet earned a claim, the correct entry in these documents is that
it has not, and that convention is enforced rather than left to editorial care.

## Contributors and their roles

| Person | Role |
|---|---|
| Eleonora Björnberg | Author. Research design, implementation, evaluation protocol, and final academic responsibility for every claim made here. |
| Nicholas Beroud | Finance collaborator. Repo- and money-market domain expertise; the finance side of the research design, including which quantities are economically meaningful, how funding-market mechanics should be represented in the panel, and which open decisions are finance questions rather than engineering ones. |

Domain input is advisory. It shapes what this project chooses to measure and how the
measurements are interpreted; it does not certify any result, and responsibility for
what the repository asserts is not divisible.

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

## Standard of evidence

A claim in this repository is admissible only when the artifact that supports it is
identifiable: a commit, a snapshot digest, a declared feature set, and a run record.
Prose is not evidence, and a passing suite is evidence about software, not about
markets. Two conventions follow, and both are enforced by tests rather than by
diligence:

- No published document transcribes a measurement that rots — a test count, or a
  hand-typed date. The commit is the timestamp.
- A quantity that could not be computed is recorded as absent rather than defaulted,
  because a default is indistinguishable from a measurement once it is written down.

## Literature access

The project uses publisher-open articles, working papers, author manuscripts,
government publications, and institutional repositories. It does not circumvent
paywalls or access controls. Citations should identify the version actually analyzed.

