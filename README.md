# Repo Market Model

[![tests](https://github.com/eleonorabjornberg/repo-market-model/actions/workflows/tests.yml/badge.svg)](https://github.com/eleonorabjornberg/repo-market-model/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A work-in-progress research system for forecasting pressure in the U.S. Treasury
repurchase-agreement market from public data.

The first target is deliberately narrow: the next-business-day distribution of
`SOFR - IORB`, accompanied by SOFR dispersion and volume forecasts and the
probability that the spread exceeds predeclared stress thresholds.

This is an **academic exercise** and a portfolio project. It is not a production
trading system, not a risk-management tool, and not a source of investment advice,
and no part of it should be used to size, price, or time a position. It currently
demonstrates the data, validation, and evaluation architecture needed for credible
forecasting; it does **not** yet claim successful predictive performance on
historical market data.

## Why this project

Repo-market stress is a useful test of financial modeling discipline. The most
dangerous failure is often not a visibly broken model but a convincing backtest
that used information before it was actually available. This repository therefore
treats point-in-time availability, data provenance, release lags, revisions, and
holdout design as first-class parts of the model.

The intended research question is:

> Can publicly observable funding, reserve, Treasury-settlement, dealer,
> money-fund, and calendar variables forecast the next-day distribution of
> Treasury repo-market pressure, including transitions into the upper tail?

## Current status

Implemented:

- a versioned point-in-time data contract and panel builder;
- immutable, checksummed snapshots from official public sources;
- source, publication-lag, revision, and availability metadata;
- validation, missingness, provenance, and accounting checks;
- a persistence benchmark with empirical prediction intervals;
- purged rolling-origin evaluation for the main scoring holdout;
- frozen, checksummed event windows for separate knowledge holdouts;
- probabilistic metrics, including pinball loss, threshold-weighted CRPS,
  Brier skill, calibration diagnostics, and stationary-bootstrap intervals; and
- a standard-library test suite of leakage and mutation-oriented guards. Its
  size is deliberately not quoted here: a count transcribed into prose is stale
  at the next commit, and a repository about point-in-time honesty should not
  publish one. The badge above and the CI log are the count.

Still in progress:

- validating complete SEC Form N-MFP monthly cross-sections;
- freezing a sufficiently long historical modeling panel;
- implementing the common fitted-model forecast interface;
- adding AR/ARX, threshold, and quantile-model challengers; and
- producing genuine out-of-sample and event-window results.

The only current end-to-end backtest uses a small synthetic fixture. Its output
tests the harness and must not be interpreted as empirical evidence. See
[`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md) for the current boundary between
implemented infrastructure and open research work.

## Quick start

Requirements: Python 3.10. That is the interpreter the suite is run on, and it is
declared once in `pyproject.toml`; 3.11 rejects the package at import. The project
intentionally uses only the Python
standard library, so no package installation is required.

```bash
git clone https://github.com/eleonorabjornberg/repo-market-model.git
cd repo-market-model

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  python3 -B -m unittest discover -s tests

PYTHONPATH=src python3 -m repo_model.cli audit data/sample/daily_market.csv
PYTHONPATH=src python3 -m repo_model.cli backtest data/sample/daily_market.csv \
  --registry metadata/sources.json \
  --feature spread_bps \
  --decision-time 16:00 \
  --model persistence \
  --report /tmp/persistence_sample.json
```

The sample file is synthetic and exists only to make the workflow executable.
For data acquisition and exact reproducibility boundaries, see
[`REPRODUCIBILITY.md`](REPRODUCIBILITY.md).

## Research design

The project follows six rules:

1. Features must be timestamped by when they became observable, not merely by the
   date they describe.
2. Random train/test splits are prohibited; evaluation follows time.
3. Scoring holdouts and historically important event windows have different roles
   and are reported separately.
4. Missing observations, structural zeros, and unavailable cross-sections remain
   distinguishable.
5. Stress probabilities come from the same predictive distribution as the
   quantile forecasts, rather than from unrelated classifiers.
6. Predictive results are not presented as causal policy estimates.

The planned architecture is:

```text
public observations -> point-in-time panel -> probabilistic forecast
                              |                       |
                              +-> quality controls    +-> stress exceedance curve
                                                        and holdout evaluation
```

Longer-term latent-liquidity, market-clearing, and network-stress components are
research directions, not completed features.

## People

- **Eleonora Björnberg** — author. Research design, implementation, and all final
  academic responsibility for what this repository claims.
- **Nicholas Beroud** — finance collaborator. Repo-market and money-market domain
  expertise, and the finance side of the research design: which quantities are
  economically meaningful, how the funding market's institutional mechanics should be
  represented, and which of the open modelling decisions are questions of finance
  rather than questions of code.

The distinction matters to how this repository is read. Most of what is built here is
data engineering and evaluation discipline, and those are the parts a test suite can
defend. The judgments a suite cannot defend — whether a series measures the thing its
name suggests, whether an aggregate hides the mechanism that matters, which decisions
must be made before fitting rather than after — are finance judgments, and they are
where the collaboration sits.

## Repository guide

- [`METHODOLOGY.md`](METHODOLOGY.md) defines the academic claims and evaluation
  protocol.
- [`DATA.md`](DATA.md) maps public and restricted data sources.
- [`PLAN.md`](PLAN.md) records the staged implementation roadmap.
- [`AGENT_CONTRACT.md`](AGENT_CONTRACT.md) specifies the machine-checked division
  of work used during development.
- [`docs/DATA_QUALITY_DECISIONS.md`](docs/DATA_QUALITY_DECISIONS.md) records open
  modeling decisions that must be resolved before empirical fitting.
- [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) separates what a clean clone can
  reproduce today from what a published empirical result would additionally require.

## Development process and AI disclosure

Parts of the implementation were developed with AI coding agents operating in
separate Git worktrees. Their allowed files and shared interfaces are defined in a
human-owned contract and checked in CI. Tests, source provenance, model claims, and
final academic responsibility remain with the project author. Domain input from the
finance collaborator named above is advisory: it informs the research design, and it
does not transfer responsibility for any claim this repository makes. Any academic
submission based on this repository should also follow the relevant instructor's
AI-use and citation requirements, and should disclose both the AI-agent workflow and
the collaboration.

## License

The code and repository documentation are available under the [MIT License](LICENSE).
Third-party data remain subject to the terms of their original providers and are
not redistributed in this repository.
