# Project Status

**Measured on 11 September 2026 at commit `ada77ac`.** This page is a snapshot,
not a claim that the repository is complete. It describes `main` only: work sitting
unmerged on a branch is named as such.

## Summary

Repo Market Model is currently a tested research and evaluation foundation for a
probabilistic repo-market forecast. It is not yet a validated forecasting model.

The strongest completed work is the part that prevents misleading empirical
results: point-in-time provenance, release-lag handling, immutable acquisition,
purged time-series evaluation, event-window separation, and probabilistic scoring.
The shared fitted-model interface now has two implementers, and the benchmark
backtest runs on a registry-derived purge rather than beside one. The principal
missing work is a complete historical panel: every number this repository reports
was produced on a 25-row synthetic sample.

## Evidence available now

- The standard-library suite completes successfully: 409 tests pass, with no
  expected failures remaining. Both intentional tripwires have been discharged
  into real assertions.
- The `fit` / `predict` / `predict_stress` interface has **two** implementers — a
  persistence benchmark and an autoregressive model with exogenous regressors. Its
  conformance tests are parametrized over implementations, so each runs once per
  implementer rather than once in total; that doubling, not the file diff, is what
  makes it an interface rather than a description of one model.
- Stress probabilities are derived from the predictive distribution, and a
  conformance test asserts the derivation: at a declared level `q`, the exceedance
  reported at that quantile is `1 - q`. A separately fitted classifier fails that
  test even when it is well calibrated on its own terms.
- Fitted transform parameters are checked to come from the training window alone.
  The check is no longer vacuous: the ARX imputes absent regressors from a training
  window mean, and a mutation that widens that window to the whole frame is caught
  by a named test.
- Regressor names are fitted state on the fitted object, not a global. An absent
  regressor raises; an unobserved value takes the training-window mean. Neither
  becomes `0.0`, which is the one value the contract forbids appearing by accident.
- Prediction intervals use a leave-one-out residual law. The in-sample alternative
  was measured rather than assumed, and is about 11% too narrow at the 90% level on
  the checked-in sample.
- The rolling benchmark backtest takes its folds from the purged rolling-origin
  splitter. `purge` is a required argument with no default, the feature row is the
  last training row that cleared the gap rather than the previous calendar row, and
  a zero gap reproduces every previously reported number exactly.
- Source metadata drive the purge interval: the splitter takes it as a required
  argument with no default, and both evaluation commands derive it from the
  registry over the sources their feature set names.
- Under-covered SEC Form N-MFP cross-sections are excluded from the modeling panel
  by an entity-count floor declared in the source registry, and the exclusion is
  recorded separately from ordinary missingness. The floor is a **declared absolute
  count**, calibrated from an observed complete month. A fraction of a trailing
  median was considered and rejected: the trailing window is itself computed from
  straggler months, which would set the floor low enough to admit the
  cross-sections it exists to reject.
- September 2019 and March 2020 event windows are frozen and checksummed, and the
  scoring and knowledge holdouts are kept distinct in code and in reporting.
- Public-source downloads are stored immutably with retrieval timestamps, request
  URLs, byte counts and SHA-256 digests.
- Panel rows can carry `ref_date`, `available_at`, vintage, and source provenance.
- Forecast-distribution, exceedance, calibration, and dependence-aware uncertainty
  metrics are implemented and tested.

These facts show that the research harness operates. They do not establish
forecast skill, because the checked-in sample is synthetic.

## Known gaps in the evidence

Stated explicitly, because each is easy to mistake for something stronger.

- **No result rests on real data.** The persistence benchmark beats the ARX on mean
  absolute error at every regressor set tried, and that comparison is reported
  rather than tuned away. On 25 synthetic rows with one constant regressor and five
  distinct rate values it is evidence about the harness, not about either model.
- **The monthly N-MFP panel is a single observation.** One quarterly archive yields
  one complete monthly cross-section, and one archive has been acquired. After the
  coverage floor is applied, the monthly `mmf_*` series have one reference date. No
  monthly N-MFP field can serve as a regressor until the archive history is
  backfilled. The daily shareholder-flow series are not affected.
- **The coverage floor is declared for one era.** A single absolute count
  calibrated on a recent month is weak in eras when the filer universe was
  substantially larger. The registry schema is intended to accept a per-era
  declaration, each entry calibrated from an observed complete month; the evidence
  for those entries does not exist until the backfill runs.
- **A declared field has never produced data.** `mmf_on_rrp` is declared in the
  source registry and has emitted no row against any real archive. Its derivation
  searches security-description text for a counterparty name. For the period held
  the true value is probably near zero, which is precisely why that period cannot
  distinguish a working derivation from a broken one. `mmf_repo_holdings` is
  affected wherever this is, since private-sector repo is the difference between
  the two series.
- **The adapter has parsed exactly one archive.** Form N-MFP has been through
  several schema versions, and the version boundaries have not been established
  empirically. A column-level refusal guard — which raises rather than silently
  yielding nothing when an expected column is renamed — exists on the data branch
  and is **not yet merged into `main`**. Until the backfill supplies more archives,
  nothing has tested the adapter against real schema variation.
- **Which sources a model's feature set draws on is not yet enforced in code.** The
  correspondence between registry field names and panel column names has been
  decided and is to be declared in the contract module; until it is, the evaluation
  commands take a hand-supplied source list, and a caller can size the purge over a
  narrower set than the model actually reads. Nothing currently checks that.
- **The Treasury settlement series aggregates decisions it does not record.**
  Security type, tenor, and Fed SOMA add-ons are summed into one series. That is
  defensible for a first phase, but bill and coupon settlements have different
  collateral and reserve-drain profiles, and SOMA add-ons do not drain private cash.
  The source limitation does not yet say so.
- **The N-MFP identity tolerance is a single absolute bound** across cross-sections
  spanning three orders of magnitude, so it is loose on the smallest and tight on
  the largest. It cannot honestly be recalibrated against one admitted month.

## Work required before empirical claims

1. Backfill and freeze the SEC Form N-MFP archive history, applying the coverage
   floor to every reference date found rather than trusting an archive's contents,
   refusing any archive whose schema the adapter cannot read faithfully, and proving
   that overlapping archives, amendments and straggler filings do not double count.
   This gates most of what follows.
2. Establish whether `mmf_on_rrp` is derived correctly, against a period in which
   money funds held Fed reverse repo at scale, and make an absent declared field
   distinguishable from a parsing failure.
3. Declare the feature-to-source correspondence in the contract module and derive
   the purge from it on every evaluation path, removing the hand-supplied source
   list.
4. Resolve the N-MFP identity-tolerance and Treasury-settlement aggregation
   decisions recorded in `DATA_QUALITY_DECISIONS.md`. The tolerance decision waits
   on item 1: it cannot honestly be calibrated against one cross-section.
5. Extend the same freeze to the remaining sources, with a machine-readable quality
   report.
6. Add a threshold benchmark against the shared interface, and re-run the
   persistence-versus-ARX comparison on the backfilled panel, where the result
   carries evidence.
7. Report the frozen event windows separately from rolling-origin evaluation.
8. Add a quantile machine-learning model only after the baselines are frozen.

## Portfolio interpretation

The repository may accurately be described as a leakage-safe, point-in-time
financial research pipeline with a tested probabilistic evaluation harness, a
model interface with two implementers, and purged rolling-origin evaluation of
both. It should not yet be described as a successful machine-learning forecast of
repo stress: no result rests on real data, and the monthly money-fund panel is one
cross-section rather than a series.

The next portfolio milestone is a compact results package containing a frozen data
snapshot, a persistence-versus-challenger comparison under purged evaluation,
tail-calibration evidence, event-window plots, limitations, and exact reproduction
instructions.
