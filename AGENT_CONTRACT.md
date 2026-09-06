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

The stress target is a calibrated probability of a threshold event on a forecast quantity, read off the predictive distribution rather than from a separate classifier. Threshold value is declared in metadata/, versioned, not tunable after the fact.
The holdout rule: Sep 2019 and Mar 2020 are single-evaluation windows. State how many times each may be scored against and who authorises it.

## Decided: stress target and event holdouts

Resolved by the human. Supersedes the open decision on whether the stress
target is a calibrated probability or a declared score.

### Target

Stress is not a separately fitted rare-event classifier. It is an exceedance
derived from the predictive distribution of SOFR - IORB:

    P(spread_{t+1} > tau)  for tau in {5, 10, 20, 50} bp

Low tau carries the calibration evidence (hundreds of positives at quarter-ends,
tax dates, month-ends). High tau inherits calibration from the shared
distributional fit. Above the top of the observed range, use a peaks-over-
threshold GPD with covariates in the scale parameter rather than direct
frequency estimation.

Scored quantity is state ("t+1 is stressed"), not onset. Onset has too few
events to score and is reported qualitatively only.

### Label rule

The label MUST NOT use a full-sample percentile — same leak class the contract
suite already catches. Fixed bp thresholds are primary; trailing-window
percentile is secondary; full-sample is prohibited. At an event boundary the
trailing window is computed from pre-event rows only.

### Two holdout roles

These are distinct and must not be conflated in code or in reporting.

1. Scoring holdout — crisis dates excluded from the headline metric but
   available for training once they are in the past. This is the deployable
   model. Produced by rolling_origin.
2. Knowledge holdout — crises stripped from training entirely, scored once per
   window. An extrapolation check, reported separately and never averaged into
   the main table. Produced by event_eval, not by a splitter flag.

Event window boundaries are frozen in versioned, checksummed metadata/events.json
(data layer owns the file; model-eval consumes it). Boundaries are never
constants in evaluator code — moving a window edge is the realistic cherry-pick,
not swapping window type.

Purge at the event boundary uses splitter semantics: dates[i] + purge 
event_start, calendar days, strict.

### Splitter default

Expanding train window, no window-type flag. Deferred on scope. If added later
it is a pre-declared ablation reporting both arms, never a tuned parameter.

### Metrics

- Brier skill score against climatology, plus Murphy decomposition, so
  reliability is reported separately from resolution. Raw Brier is retained
  only to satisfy the stated commitment; it is not the headline.
- Log score and threshold-weighted CRPS on the continuous target.
- Precision-recall, not ROC.
- CORP/isotonic reliability with consistency bands. Fixed-bin ECE is prohibited
  at these base rates.
- All intervals from a stationary block bootstrap.
- Event windows get the exceedance curve and realized path. No aggregate Brier
  or reliability number on a single event window.

### Ownership

- Data layer: metadata/events.json, the label column and its point-in-time rule.
- Model-eval: event_eval.py, the metric implementations.
- Neither track edits this file.

## Decided: release lag and the purge gap

Resolved by the human after the source registry landed with a structured
`release_lag`. Track B's splitter still assumes that key is a number; it is not,
and nobody owned the conversion. This section assigns it.

### The purge stays a scalar

`rolling_origin(dates, min_train, step, purge)` and `evaluate_event_window`
keep their pinned semantics: `purge` is an integer of calendar days, the
boundary is `dates[i] + purge < start`, strict. Neither learns about
calendars, timezones or vintages.

This is deliberate. The purge is the leakage guard, and a guard whose
correctness depends on a holiday calendar cannot be audited by reading it. All
the judgement moves into a function that produces the number, where it can be
tested on its own.

### The conversion belongs to the data layer

`src/repo_model/registry.py`, owned by Track A:

    max_release_lag_days(registry, sources, *, decision_time) -> int

Track B imports it and passes the result as `purge`. Track B does not
reimplement it, and does not read `release_lag` directly. A wrong conversion is
a provenance error, not an evaluation error, and it belongs with the people who
know what the registry's fields mean.

`decision_time` is required and has no default. A default would be a silent
assumption about when the forecast is made, which is the assumption the whole
as-of rule exists to make explicit.

### One rule per basis

- `ref_date` + `business_days` — converted to a conservative calendar-day
  bound. Until a holiday calendar exists, each such source declares
  `worst_case_calendar_days` explicitly, and it must be at least `days + 5`: a
  weekend plus up to three consecutive holidays. When the point-in-time panel
  lands, a test asserts no observed publication gap exceeds the declared bound.
- `record_date` + `calendar_days` — the lag is `days`, plus one further day if
  `available_time` falls after `decision_time`.
- `snapshot_retrieved_at` — contributes no purge, and MUST NOT be mapped to
  zero. Those rows are valid only from their snapshot timestamp, which is an
  `available_at` fact about a row, not a lag on a source.
  `max_release_lag_days` raises if such a source is passed without every row
  carrying `available_at`.

### Purge over the feature set, not the registry

The purge for a backtest is the maximum over the sources whose fields the
feature set actually uses. Taking the maximum over the whole registry purges
more than the evidence requires and silently destroys training rows, which
reads as a weak model rather than as a configuration mistake.

### Two registry corrections

- `fields` is machine field names only. Human-readable coverage moves to a
  separate `coverage` key. Identity terms must be a subset of `fields`, and
  that check is only meaningful if `fields` is not also prose.
- An empty `structural_zeros` is not a finding. Each source declares
  `structural_zeros_reviewed` with a `reviewed_note`. Empty plus unreviewed
  means not yet analyzed, and contract test 5 stays a stand-in for that source.
  Absence of evidence is not to be recorded as evidence of absence anywhere in
  this repo.

### Ownership

- Data layer: `registry.py`, `metadata/sources.json`, `metadata/events.json`,
  the label column and its point-in-time rule.
- Model-eval: `splits.py`, `event_eval.py`, `metrics.py`.
- Neither track edits this file.
