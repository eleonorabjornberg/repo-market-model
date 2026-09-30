# Contract: data and model interfaces

> Code and tests that cite `AGENT_CONTRACT.md` mean this file. Where they cite a section by a name that no longer
> appears here (for example "The purge stays a scalar" or "The conversion belongs to the data layer"), the reasoning
> is kept in `docs/archive/AGENT_CONTRACT-two-track.md`. The rule is the one stated below.

These rules bind any code that builds the panel, fits a model or evaluates a forecast, whoever writes it. Records in
`docs/decisions/` refine them, and where a decision record is later than this file, the decision record wins. Where a
shape can be expressed as code it lives in `src/repo_model/contract.py`, and this file explains why rather than
restating what.

## Why this matters

Look-ahead enters silently. It comes from backfilling a value into a date on which it was not yet known, or from
fitting a scaler, imputer or hyperparameter on rows outside the training window. Neither raises an error, and both
invalidate every downstream result. The contract tests are what stand between the project and a backtest that looks
excellent and means nothing.

## The panel schema

Long format. One row per observation.

| field | meaning |
|---|---|
| `series_id` | stable identifier from the source registry |
| `ref_date` | date the value describes |
| `available_at` | timestamp the value first became observable |
| `value` | the observation |
| `vintage_id` | revision identifier; a revised value is a new row |
| `source_sha` | SHA-256 of the raw response the value was parsed from |

Revisions are appended, never overwritten.

## The as-of rule

For a forecast created at cutoff `C`, a row is eligible only if `available_at <= C`. Where a true `available_at` is
unavailable, the source registry declares a conservative release-lag rule. Lags are never estimated per observation
from the data. Feature construction is a pure function of the eligible set.

How a forecast reads its inputs under this rule, per field and at its decision instant, is decided in
`docs/decisions/information-set.md`.

## Building the daily panel

The model layer consumes a wide daily panel built from the long canonical one.

1. **The panel is indexed by `ref_date`, and a cell carries the latest vintage available at a declared build
   cutoff.** The cutoff is recorded in the panel manifest.
2. **The join does not subtract the release lag.** Availability is applied once, by the evaluator. A join that also
   shifted values would apply it twice.
3. **A column may be built only if its latest vintage is faithful**, which the join learns by calling the registry's
   pricing function. A refused column is absent, with its reason recorded.
4. **No forward fill.** A missing observation is a hole. The declared exceptions (settlement zeros, bounded weekly
   carries) are in `docs/DATA_QUALITY_DECISIONS.md` and `docs/decisions/weekly-carry.md`.

## Release-lag declarations

`release_lag` is an object, validated by `contract.validate_release_lag` and `validate_registry_release_lags`.

- `basis` is required. It is one of `ref_date`, `record_date` or `snapshot_retrieved_at`.
- `unit` is `business_days` for `ref_date` and `calendar_days` for `record_date`. It is validated against `basis`.
- `days` is a non-negative integer. It is required for `ref_date` and `record_date`.
- `worst_case_calendar_days` is required for `ref_date`, and must be at least `days + 5`.
- `available_time` is `HH:MM`, required for `record_date`. An unknown intraday time is declared as `"23:59"`.
- `timezone` is a valid IANA zone. It is required wherever `available_time` is declared, and forbidden where it is not.
- `note` is optional.

A `snapshot_retrieved_at` source declares only `basis` and `note`. Its rows carry `available_at`, and it is never mapped
to a zero lag.

Registry hygiene:
- `fields` holds machine field names only. Prose goes under `coverage`.
- Every source declares `structural_zeros_reviewed` with a `reviewed_note`. An empty list with no review is "not yet
  analysed", never "none".

## Features and sources

- `contract.FEATURE_SOURCES` maps each panel column to the sources it draws on, and
  `contract.sources_for_features(names)` is the only supported route from a feature set to its sources. The map is
  declared, not derived from the registry.
- **Sources are derived, never supplied.** A caller declares a feature set, and its sources and availability follow.
- **A fitter may not exceed its declaration.** A fitted model whose regressors go beyond the declared feature set
  raises `LookAheadError`.

## The forecast interface

```
fit(train_frame)            -> fitted model
predict(feature_row)        -> quantile vector at declared levels
predict_stress(feature_row) -> exceedance vector aligned to metadata taus_bp
```

- `contract.QUANTILE_LEVELS` is fixed across all models, so pinball loss and coverage are comparable.
- `predict_stress` returns one exceedance probability per `taus_bp` entry in `metadata/stress_thresholds.json`, derived
  from the same predictive distribution as `predict`.
- Every fitted object carries its cutoff. Any learned transform is fitted inside `fit` and nowhere else.

## Evaluation

- **Splits** are expanding-window and time-ordered. Random splits are prohibited, and no flag enables them. The splitter
  is `rolling_origin(dates, min_train, step, purge)`. Today its `purge` both trims training rows and chooses the feature
  row. `docs/decisions/information-set.md` replaces the second use; its implementation is the next task in
  `docs/pivot/next-session.md`.
- **The stress target** is an exceedance of SOFR − IORB derived from the predictive distribution, at the thresholds in
  `metadata/stress_thresholds.json`. It is scored as state, not onset. Labels use fixed bp thresholds and never a
  full-sample percentile.
- **Two holdout roles, never conflated.**
  - The scoring holdout: crisis dates excluded from the headline metric but available for training once past
    (`rolling_origin`).
  - The knowledge holdout: crises stripped from training and scored once per window (`event_eval`), reported separately.
  Window boundaries live in `metadata/events.json`, each with a checksum verified through
  `contract.event_window_digest`.
- **Metrics.**
  - Brier skill against climatology, with the Murphy decomposition.
  - Log score and threshold-weighted CRPS.
  - Precision-recall rather than ROC.
  - CORP/isotonic reliability with consistency bands; no fixed-bin ECE.
  - Every interval comes from a stationary block bootstrap.
  - An event window gets its exceedance curve and realised path, never an aggregate Brier.

## Contract tests

`tests/test_contract.py` runs in CI on every pull request. A failure fails the build.

1. **Eligibility.** No training row has `available_at` later than its window's cutoff.
2. **Future perturbation.** Modify observations dated after T, refit, and re-predict. The forecast must be bit-identical.
3. **Transform isolation.** Fitted transform parameters are recomputed on the training window alone and must match.
4. **Identity preservation.** Declared accounting identities reconcile within tolerance on every panel snapshot.
5. **Structural zeros.** A declared structural zero stays distinguishable from a missing observation, and neither is
   coerced to 0.0.

## Dependencies and data

- Third-party packages live in `src/repo_model/ml.py` (the optional `ml` extra: numpy and scikit-learn) and nowhere else
  in `src/`. `tests/test_dependency_boundary.py` enforces this.
- `tests/test_ml.py` skips without the extra, and fails instead when `REPO_MODEL_REQUIRE_ML=1`, which CI sets.
- Raw and processed data stay out of git. Code, metadata and the tracked fixtures are committed.
- A model that does not beat its benchmark out of sample is reported as such and kept in the results.
