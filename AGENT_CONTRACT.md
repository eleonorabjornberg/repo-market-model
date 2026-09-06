# Agent contract

Single source of truth for both coding agents. `CLAUDE.md` and `AGENTS.md`
each point here. Do not duplicate rules into those files — they drift.

## Tracks and ownership

Two tracks run in parallel in separate git worktrees on separate branches.

**Track A — data (`feature/data-layer`)**
Owns: source registry, download adapters, provenance and checksums,
point-in-time panel construction, missingness and revision reporting.
Maps to PLAN.md immediate tasks 1–3.

**Track B — model (`feature/model-eval`)**
Owns: benchmarks (persistence, rolling quantiles, AR/ARX, threshold
regression), rolling-origin backtest harness, scoring, calibration
diagnostics, event holdouts.
Maps to PLAN.md immediate tasks 4–5.

**Neither track owns** the panel schema, the forecast interface, the
splitter interface, or `tests/test_contract.py`. Changes to these are
proposed to the human and applied once, by one agent, before either track
resumes. An agent that believes the contract is wrong stops and says so.
It does not edit around it.

## Why this matters more than usual here

Both tracks can silently introduce look-ahead. Track A leaks by backfilling
a value into a date on which it was not yet known. Track B leaks by fitting
a scaler, imputer, or hyperparameter on rows outside the training window.
Neither failure raises an error. Both invalidate every downstream result.
The contract tests are the only thing standing between the project and a
backtest that looks excellent and means nothing.

## The panel schema

Long format. One row per observation, never wide-by-default.

| field         | meaning                                              |
|---------------|------------------------------------------------------|
| `series_id`   | stable identifier from the source registry            |
| `ref_date`    | date the value describes                              |
| `available_at`| timestamp the value first became observable           |
| `value`       | the observation                                       |
| `vintage_id`  | revision identifier; a revised value is a new row     |
| `source_sha`  | SHA-256 of the raw response the value was parsed from |

Revisions are appended, never overwritten. A value observed on day T and
revised on day T+3 is two rows with the same `series_id` and `ref_date`,
different `available_at` and `vintage_id`.

## The as-of rule

For a forecast created at cutoff `C`, a row is eligible only if
`available_at <= C`. Where a true `available_at` is unavailable, the source
registry declares a conservative release-lag rule and it is applied
uniformly. Lags are never estimated per-observation from the data.

Feature construction takes eligible rows and returns a feature frame. It
must be a pure function of the eligible set. If it reads anything else, it
is wrong.

## The forecast interface

```
fit(train_frame)            -> fitted model
predict(feature_row)        -> quantile vector at declared levels
predict_stress(feature_row) -> probability in [0, 1]
```

Quantile levels are declared once in the contract and fixed across all
models, so pinball loss and interval coverage are comparable. A model that
wants different levels is a new model, not a config change.

Every fitted object carries the cutoff it was fitted at. Any transform with
learned parameters — scaling, imputation, encoding, hyperparameter choice —
is fitted inside `fit` and nowhere else.

## The splitter interface

```
rolling_origin(dates, min_train, step, purge) -> yields (train_idx, test_idx)
```

`purge` inserts a gap between train end and test start, sized to the longest
release lag in the feature set. Without it, a feature revised after the
training window ends can carry information from the test period. Random
splits are prohibited. There is no configuration flag that enables them.

## Contract tests

`tests/test_contract.py`. Both tracks run it before every commit. It fails
the build, not a warning.

1. **Eligibility.** No row in any training window has
   `available_at` later than that window's cutoff.
2. **Future perturbation.** Take a fitted model and a forecast for T+1.
   Modify observations dated after T. Refit and re-predict. The forecast
   must be bit-identical. Any change is look-ahead, and this test finds
   leaks that eligibility checks miss because it tests behaviour rather
   than structure.
3. **Transform isolation.** Fitted transform parameters are recomputed on
   a training window alone and must equal the parameters produced by the
   full pipeline on that window.
4. **Identity preservation.** Accounting identities declared in the source
   registry reconcile within stated tolerance on every panel snapshot.
5. **Structural zero handling.** A declared structural zero is
   distinguishable from a missing observation at every stage. Neither is
   silently coerced to 0.0.

Test 2 is the cheapest high-value leakage detector available and should be
written before either track starts producing models.

## Working rules

- Each agent works only in its own worktree. Do not `cd` into the other.
- Do not edit files owned by the other track, even to fix an obvious bug.
  Report it instead.
- Do not add third-party dependencies. The baseline runs on the standard
  library and that property is load-bearing for reproducibility.
- Raw and processed data stay out of git. Code and metadata are committed.
- A model that does not beat persistence out of sample is reported as such
  and kept in the results. Failed specifications are published, per
  METHODOLOGY.md.

## Open decision for the human

Event holdouts and stress calibration are in tension. September 2019 and
March 2020 are both designated holdouts and are also most of the available
positive labels for the stress target. Held out, the classifier trains
almost entirely on quarter-end and year-end spikes, and Brier score on the
holdouts then measures extrapolation to unprecedented conditions rather
than calibration — which METHODOLOGY.md already declines to claim.

Resolve before Track B builds the stress head, since it determines whether
target 4 is a calibrated probability or a declared stress score.
