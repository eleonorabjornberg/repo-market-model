# Implementation plan

## Objective and scope

Build a reproducible model of U.S. Treasury repo-market pressure that starts with
public daily data and can graduate to bank-level and intraday modeling if restricted
data become available.

This is an academic exercise, and the phase structure below should be read as one: the
committed scope is what the exercise undertakes to evidence, and the aspirational
phases are research directions recorded so that the committed scope is not quietly
widened to include them. The choice of data and its meaning across these phases rests
with Nicholas Beroud, co-owner and Financial Advisor; the model, methodology and
workflow, engineering and evaluation decisions rest with the author.

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

## What is committed, and what is not

**Phases 0 through 4 are the committed scope.** They are what this repository sets out
to deliver and what a reader should expect to find evidence for.

**Phases 5 through 7 are retained but aspirational.** They are kept in this document
because they explain why the data contract is shaped the way it is — point-in-time
provenance, declared identities, and per-source release lags are only worth their cost
if the eventual consumer is a network reconstruction and a stress engine. They are not
a commitment, and the decision on whether to attempt them is taken after Phase 4's exit
criterion is met, not before.

A plan whose later phases nobody expects to reach stops describing the work. Saying so
here is cheaper than discovering it later.

## Phase 0 — Reproducible foundation (complete)

- Define a point-in-time daily data contract.
- Record source, native frequency, release lag, revision behavior, and transformations.
- Add validation, missingness reporting, and accounting checks.
- Establish persistence and rolling-distribution baselines.
- Use rolling-origin evaluation; never use random train/test splits.

Exit criterion: one command validates a panel and produces a leakage-safe baseline
backtest. **Met.**

## Phase 1 — Public U.S. dataset (in progress)

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

Ingested so far: the SOFR, TGCR and BGCR families; the FRED macro block; Treasury
settlement, with bill, coupon and SOMA components at the adapter; Treasury daily bill
rates at the adapter (`treasury_bill_rates`); SEC Form N-MFP, whose declared archive set, per-table refusal rule and
per-era category vocabulary are recorded in `metadata/sec_nmfp_archives.json` and
`metadata/sources.json`; and the FR 2004 primary-dealer Treasury total (`nyfed_fr2004`,
`PDPOSGST-TOT`, from 2013-04-03). Not yet ingested: basis proxies, and the volatility,
depth and bid-ask proxies. The 4- and 13-week bill yields and the bill, coupon and SOMA settlement components
are panel columns.

Exit criterion: frozen, checksummed modeling snapshots with provenance and a data
quality report.

## Milestone A — the first observable result (published and reproducible)

**Was the single highest-value thing outstanding, ahead of the remainder of Phase 1.**
Until it landed, every backtest, every purge gap, every leakage guard and every
mutation record was anchored to a twenty-five-row synthetic fixture -- the
repository's own recurring finding turned on itself: *a check anchored to nothing
cannot fail.* The guards were real, the discipline was real, and until this milestone
they protected no observable quantity.

Steps taken, in order:

1. **Release lags declared at field granularity.** `fred_macro_latest_vintage` had
   carried one `release_lag` for a set of series whose revision behaviour is not one
   thing: administered rates that are never revised sit beside H.4.1 weeklies that
   are. A latest-vintage source may back a point-in-time feature only for a field
   declared never-revised, with its evidence recorded.
2. **The field-level declaration is consumed in the evaluation path**, so the purge
   is sized over the fields a feature set actually reads. Fields with no declared
   revision policy stay refused.
3. **A funding-only daily panel was fetched and frozen** -- the two legs of the
   spread and nothing else -- with its snapshot manifest and data-quality report.
4. **The persistence benchmark was published on it:** pinball loss, interval
   coverage and MAE under the registry-derived purge, beside the fold count and the
   training window.

Exit criterion, as written before the work and unchanged: *a reader who clones the
repository and runs one command reproduces a published quantile loss and interval
coverage for the persistence benchmark on a fetched panel rather than a fixture — and
the published figures are generated output, not prose. A number typed into a document
is the same drift as a hand-written date, and the rule against one is the rule against
the other.*

**It has two clauses and they do not have the same answer.**

**Publication: met.** `docs/runs/persistence_funding.json` is tracked and generated. A
cloner receives pinball loss at five quantiles, interval coverage, MAE with a
stationary-bootstrap interval and a recorded seed, over 2080 folds on a fetched panel
spanning 2018-04-03 to 2026-09-03, with the build manifest and source digests beside
them. No figure from it is transcribed into any Markdown page in this repository, which
was the harder half to hold and it held.

**Reproduction: met.** `scripts/reproduce_milestone_a.py` rebuilds the panel from the
tracked inputs, passes `verify-panel` against the published digest byte for byte, and
re-derives every figure in the record exactly; `tests/test_generated_results.py` runs it
on every suite run, so the clause stays met only while it stays true. It closed on a
defect the check itself surfaced: the tracked inputs' sidecars still named `data/raw/`,
so a rebuild from them had only ever worked in the checkout that also held the
originals. How it got here: the panel is `data/processed/funding_panel.csv` and is
gitignored, and re-running a download is not guaranteed to return an earlier byte
stream -- the FRED adapter acquires the latest revised vintage rather than the
historical one -- so the fetch a reader performs is not the fetch that produced the
record. The raw inputs the record was built from are therefore tracked under
`tests/fixtures/snapshots/funding_inputs/`, and `metadata/funding_panel_manifest.json`
binds each of them, and the panel, by digest; `repo_model.data.verify_daily_panel`
checks a panel's bytes against that digest and refuses a manifest whose digest is
missing or is not 64 lowercase hex characters.
The last piece was the rebuild: one command that builds the panel from those inputs,
verifies it and re-scores it against the record.

**This criterion was briefly rewritten to say it had been met**, on 9 September, by
pointing at `REPRODUCIBILITY.md`'s command list instead of naming the figures — and the
rewritten version was not true either. The original stands above because a criterion
edited after the result is not a criterion, which is the same finding this repository
records about a guard shaped to fit the thing it measures. What closes the gap is the
rebuild described above. See `docs/PROJECT_STATUS.md` for what the benchmark does and
does not establish.

## Phase 2 — Forecasting benchmarks and probabilistic ML (evaluation foundation complete)

Benchmarks:

- last observation;
- rolling mean/quantiles;
- AR and ARX;
- threshold regression.

Candidate ML models:

- gradient-boosted trees for conditional mean and quantiles;
- stress exceedance probabilities derived from the fitted predictive distribution;
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

The evaluation machinery exists: rolling-origin folds behind a purge derived from the
declared feature set, a common fitted-model forecast interface with more than one
implementer, an event-holdout path, and the metric implementations. On the frozen
panel, gradient-boosted quantiles and the trailing-window residual law beat persistence
under CRPS at paired origins (`docs/PROJECT_STATUS.md`). Gradient-boosted quantiles'
nominal interval covers well under its nominal probability
(`docs/runs/backtest_gbm_mh61.json`), so the model that wins on accuracy is not
calibrated in its interval; split-conformal calibration narrows the coverage gap without
closing it and gives up the accuracy win (`docs/runs/backtest_gbm_conformal_mh61.json`); a
cross-conformal interval keeping the full fit is built and not yet scored. Its exceedance probabilities have not been scored in the
tails, nor has a conditional predictor been scored against climatology on a
knowledge-holdout window, so the exit criterion is not met.

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

**Decision point.** Whether to attempt Phases 5 through 7 is decided here, against what
Phases 0 through 4 actually produced, and not before.

## Phase 5 — Missing-data and network ensemble (aspirational)

- Infer relationship existence with a hurdle model.
- Infer edge sizes using entropy-regularized matrix completion under row/column totals.
- Preserve daily relationship persistence.
- Reconstruct possible collateral paths using security, quantity, timestamp, and
  reuse constraints.
- Sample many feasible networks rather than selecting one completion.
- Report which stress conclusions are robust across the ensemble.

Exit criterion: mask-and-reconstruct tests recover held-out observed edges and
aggregate identities within declared tolerances.

## Phase 6 — Stress engine (aspirational)

Iterate:

1. asset or funding shock;
2. collateral repricing;
3. margin calls and rollover decisions;
4. balance-sheet constraint breaches;
5. forced sales and funding withdrawal;
6. price impact and downstream defaults.

Exit criterion: historical replay and sensitivity reports, with no claim that a
single reconstructed network is the true network.

## Phase 7 — European extension (aspirational)

Add adapters for:

- public SFTR weekly aggregates;
- ECB MMSR aggregates;
- ICMA surveys;
- sovereign issuance and collateral data; and
- restricted SFTR/MMSR transaction data if access is obtained.

The European model must explicitly represent currency, sovereign issuer, collateral
eligibility, CCP/CSD, and cross-border settlement.

## The critical path

This section names phases and milestones. It deliberately does **not** track individual
work blocks: a plan's "next steps" section is the part that goes stale first, and
listing blocks here guarantees it. Block-level sequencing lives in the session handoff
and in the block briefs; what belongs here is the order of the milestones and why.

1. **Milestone A — the first observable result.** **Met**, both clauses -- see above.
   Every guard now protects an observable quantity, and the reproduction is a test.
2. **Finish Phase 1's provenance work on what is already ingested**, before widening.
   The N-MFP identity tolerance is settled as a calibrated absolute bound: a relative
   bound was argued from three orders of magnitude of scale, and the coverage floor and
   monthly assembly left a 2.9x range, over which scale explains almost none of the
   residual. The `sec_nmfp` structural-zero review is recorded: `mmf_on_rrp` is a
   declared zero through 2013-08-31, before the facility. The Treasury-settlement split into bill, coupon and SOMA components is
   done at the adapter; its panel columns are not. Both are recorded in
   `docs/DATA_QUALITY_DECISIONS.md`.
3. **Then widen Phase 1**: primary-dealer positions, the 4- and 13-week bill yields and the
   settlement components are sourced; the liquidity proxies are next. The published Milestone A panel stays pinned to its
   manifest's columns, so a new source does not move it.
4. **Phase 2 to its exit criterion**: a conditional model scored against climatology on
   the declared knowledge holdouts, and a benchmark that beats persistence out of sample
   while staying calibrated in the tails.
5. **Phases 3 and 4.**
6. **Decision point**, then Phases 5 through 7 or a stop.

## How this document stays true

- **No test counts and no hand-written dates in prose.** The suite's size is whatever CI
  last printed; "when" is a commit sha, which is a timestamp nobody types. Dates that are
  *data* — September 2019, March 2020, a report month — are unaffected.
- **Published results are generated output, not prose.** A figure retyped into a document
  is right when it is typed and silently wrong afterwards, which is the same failure one
  level up from a stale date.
- **Status claims name the artifact that proves them.** "Met", "in progress" and
  "aspirational" are claims about the tree, and a claim about the tree that is not
  asserted against it stops describing it.
