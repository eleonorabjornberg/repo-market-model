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

## Open decision for the human — RESOLVED, see "Decided: stress target and
event holdouts" below

Left in place as the record of what was asked. It is answered; do not treat
it as open.

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

## Decided: the `sources` argument, and two escalations answered

Track B read the previous section carefully enough to find a hole in it, and
was right to stop rather than pick a reading. The hole: the section requires
`max_release_lag_days` to raise when a `snapshot_retrieved_at` source is passed
without every row carrying `available_at`, but the signature it pins takes no
rows, so the function cannot evaluate that condition.

### The resolution

`sources` is a mapping from source id to the rows being used from it:

    max_release_lag_days(registry, {"nyfed_sofr": None, "sec_nmfp": rows},
                         decision_time=time(16, 0))

A value of `None` means the caller is not supplying rows for that source. For a
lag-based source that is fine — its purge comes from the registry, not from
rows. For a `snapshot_retrieved_at` source it raises, because the only reason
such a source contributes no purge is that its rows carry `available_at`, and
a caller that supplies no rows has not shown that.

An iterable of bare source ids is accepted as sugar for
`{source_id: None for source_id in ids}`. The signature is unchanged; what was
underspecified was the type of its second argument, not its arity.

This is the shape Track A had already built. It is now written down, which is
the difference that matters: an interface discovered by reading the other
track's implementation is not pinned, it is merely observed.

### An empty source set raises

`max_release_lag_days(registry, {}, ...)` raises. It does not return 0. A purge
of zero derived from an empty feature set is the same silent-zero failure this
contract keeps legislating against, and it is the likeliest form of it, because
an empty feature set is what a partially-wired pipeline produces.

Likewise a `snapshot_retrieved_at` source whose row collection is empty: an
empty collection satisfies "every row carries `available_at`" vacuously, and
vacuous satisfaction is not evidence. It raises.

### The two escalations

Track B pinned two requirements beyond what it was asked for, and asked whether
to drop them. It should not. Both are adopted:

1. **The two registry corrections** (`fields` versus `coverage`,
   `structural_zeros_reviewed`) were stated in this contract without an owner.
   They are Track A's.
2. **The publication-gap check** — that no observed publication gap exceeds a
   source's declared `worst_case_calendar_days` — is Track A's, and it is the
   more important of the two. Its reasoning is correct and worth recording: a
   declared bound that is too small makes every purge sized from it too small,
   and no test in `splits.py` can detect that. The splitter remains correct with
   respect to a number that was already wrong. A guard that can only be written
   on one side of an interface belongs to that side, whatever the passive voice
   in the prose suggested.

### On where specs live

Track B put its interface specs in its own files rather than in
`tests/test_contract.py`, reasoning that every edit there costs a CI review
notice. That is the right instinct and it stands. The correction is only to the
naming: a spec file that describes an artifact the other track will build must
be named for the track that wrote it — `test_events_metadata_spec.py`, not
`test_events_metadata.py` — because both tracks reaching for the obvious
filename is an add/add conflict that no ownership list can see. The gate now
checks for it directly.


## Decided: the `release_lag` schema

Resolved by the human, 7 September 2026, after a trial merge of
`feature/data-layer` and `feature/model-eval` showed the two halves do not
compose. This section supersedes any earlier reading of "One rule per basis".

### What went wrong

"One rule per basis" above writes the pairings as `ref_date` + `business_days`
and `record_date` + `calendar_days`. It never says what the key holding
`business_days` is *called*. Track A implemented it as `calendar`, with a third
value `none` for snapshot sources; Track B's blind spec pinned it as `unit`.
Both were faithful readings. Both were in lane. Neither could have caught it,
because the ownership gate checks who writes a file, not what a shared key
means.

This is the third collision of that class on this project. The first two were
`release_lag` dict-versus-scalar and the duplicate spec filename. The pattern is
now named: **a field named in prose without a key name gets two key names**, the
same way a requirement stated without an owner gets done twice or not at all.

### The schema

`release_lag` is an object. `basis` is required and is one of `ref_date`,
`record_date`, `snapshot_retrieved_at`. No other keys are permitted than those
below.

- **`unit`** — the key name is `unit`, not `calendar`. Values `business_days`
  for a `ref_date` source and `calendar_days` for a `record_date` source.
  `snapshot_retrieved_at` declares no unit.

  The pairing is fixed, so `unit` is strictly redundant with `basis`. It is
  declared anyway, and validated against `basis`, so that a source whose author
  meant the other calendar is a validation error rather than a silent
  reinterpretation. `calendar` was rejected for two reasons: one of its values
  was `calendar_days`, which makes the key unreadable, and a holiday calendar is
  already promised elsewhere in this contract, so the name is spoken for.

- **`days`** — a non-negative integer, in the declared `unit`. Booleans do not
  pass as integers. Required for `ref_date` and `record_date`.

- **`worst_case_calendar_days`** — required for `ref_date`, and at least
  `days + 5`, as already specified above.

- **`available_time`** — an `HH:MM` wall-clock string, not `HH:MM:SS`. Nothing
  in the as-of rule resolves below a minute, and a trailing `:59` invites the
  reader to believe it does. Required for `record_date`. A source whose intraday
  publication time is unknown declares `"23:59"`, the conservative end-of-day
  convention.

- **`timezone`** — a valid IANA zone. Required wherever `available_time` is
  declared, and **forbidden where it is not**. A declared-and-never-read
  timezone is exactly how naive times came to be compared across zones in the
  first place; a key that nothing reads is not documentation, it is a latent
  bug with a comment on it.

- **`note`** — an optional string. Allowed everywhere.

### A snapshot source declares no day count at all

`snapshot_retrieved_at` sources declare `basis` and `note`, and nothing else.
No `unit`, no `days`, no `available_time`, no `timezone`.

This is not a new rule. "One rule per basis" above already says such a source
contributes no purge and MUST NOT be mapped to zero. A `days: 0` on a snapshot
source is that prohibited zero, written down as data, where the next reader will
take it for a measurement. Track B's blind spec was right about this against the
contract's own text, and Track A's `days: 0` was a violation of it.

### The shape is executable, and owned by neither track

`src/repo_model/contract.py` holds `validate_release_lag(source_id, obj)` and
`validate_registry_release_lags(registry)`. Stdlib only. Both tracks import it:
Track A's `registry.py` fails closed on a non-empty result, and Track B's specs
assert against the same function rather than against a second reading of this
prose.

Neither track edits it. It is in `HUMAN_ONLY` in the ownership gate, alongside
this file.

Prose in this contract is how a shared shape gets described twice. Where a shape
is shared by both tracks and can be expressed as code, it goes in that module
and this file explains *why* rather than restating *what*. That is the general
rule, not a one-off for `release_lag`.

### Ownership of the follow-up

- Track A: bring `metadata/sources.json` to this schema, and make `registry.py`
  validate through `repo_model.contract` instead of its own inline checks.
- Track B: rename `unit` expectations to read from `repo_model.contract`, drop
  the duplicated shape rules from its specs, and declare `timezone` in the
  fixture registries that now need one.
- Neither track edits this file or `src/repo_model/contract.py`.

## Decided: the event-window checksum

`metadata/events.json` landed with a per-window `checksum`, and nothing in `src/`
checks it. `load_event_windows` requires the key to be present and non-empty, which
detects an author who forgot it and nothing else: a window whose `start` moved and
whose digest did not still loads and still scores. A checksum that is only required,
never verified, is a field that looks like a guard.

### What the checksum is of

    checksum = sha256(json.dumps({name, start, end},
                                 sort_keys=True, separators=(",", ":")))

Hex, lowercase, 64 characters. `start` and `end` are hashed as the ISO **strings the
file carries**, not as parsed dates: the digest must be computable from the file's own
bytes, without a parse step that could normalise something between what was written and
what was hashed.

This is not a new rule. It is the rule Track B wrote into
`tests/test_events_metadata_spec.py` while `metadata/events.json` was still
hypothetical, and Track A's file already satisfies it — both declared checksums verify
unchanged. The decision here is only about where it lives.

### It is a shared shape, so it moves

Track A writes the file, Track B reads it. Under "The shape is executable, and owned by
neither track" that makes it a shared shape, and the general rule applies without
needing a ruling: it goes in `src/repo_model/contract.py`, which is stdlib-only,
`HUMAN_ONLY` in the ownership gate, imported by both tracks and edited by neither.

`src/repo_model/contract.py` now also holds:

- `EVENT_WINDOW_KEYS` — `name`, `start`, `end`, `checksum`. Extra keys are permitted;
  Track A may carry a rationale or a citation, and model-eval ignores them.
- `event_window_digest(name, start, end)` — the digest above.
- `validate_event_windows_document(payload)` — every way a document fails, as a list of
  readable problems rather than a raise on the first, so a malformed file reports all of
  its faults in one run.

Left in `tests/test_events_metadata_spec.py`, it would have been the fourth semantic
collision this project has paid for, and the first one visible far enough in advance to
avoid.

### Ownership of the follow-up

- Track B: verify the checksum in `load_event_windows` through
  `repo_model.contract.event_window_digest`; add a path-taking loader for the declared
  file; delete the duplicated digest and validator from its spec file and assert through
  the shared ones; recompute the placeholder checksums in its fixtures rather than
  loosening the check.
- Track A: nothing. `metadata/events.json` already conforms. A future edit to a window
  boundary must recompute that window's digest, and
  `validate_event_windows_document` will say so if it does not.
- Neither track edits this file or `src/repo_model/contract.py`.

### Still open, and not either track's to settle

`src/repo_model/cli.py` is owned by neither track and is not in `SHARED`. The gate does
not fail a branch that edits it and does not surface it for review either, so both tracks
can edit it and nothing says so until the merge — the same hole as a field named in prose
with no key name. Nothing needs the CLI yet; the event-holdout subcommand is held out of
Track B's next block until this is assigned.
