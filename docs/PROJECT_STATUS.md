# Project Status

**Measured on 10 September 2026 at commit `f52c7c8`.** This page is a snapshot,
not a claim that the repository is complete.

## Summary

Repo Market Model is currently a tested research and evaluation foundation for a
probabilistic repo-market forecast. It is not yet a validated forecasting model.

The strongest completed work is the part that prevents misleading empirical
results: point-in-time provenance, release-lag handling, immutable acquisition,
purged time-series evaluation, event-window separation, and probabilistic scoring.
A shared fitted-model interface now exists and is checked behaviourally rather than
by presence. The principal missing work is a complete historical panel and a fitted
challenger that can be evaluated against persistence.

## Evidence available now

- The standard-library suite completes successfully: 380 tests pass, with no
  expected failures remaining. Both intentional tripwires have been discharged
  into real assertions.
- The `fit` / `predict` / `predict_stress` interface is implemented, and the
  persistence backtest consumes the fitted model rather than deriving a second set
  of quantiles beside it. Quantile levels and the reported interval have one
  declared origin.
- Stress probabilities are derived from the predictive distribution, and a
  conformance test asserts the derivation: at a declared level `q`, the exceedance
  reported at that quantile is `1 - q`. A separately fitted classifier fails that
  test even when it is well calibrated on its own terms.
- A synthetic 25-row panel runs through the audit, persistence backtest and
  event-holdout commands.
- Public-source downloads are stored immutably with retrieval timestamps, request
  URLs, byte counts and SHA-256 digests.
- Panel rows can carry `ref_date`, `available_at`, vintage, and source provenance.
- Under-covered SEC Form N-MFP cross-sections are excluded from the modeling panel
  by an entity-count floor declared in the source registry, and the exclusion is
  recorded separately from ordinary missingness. The rule is anchored to a trailing
  median rather than to the extract that produced it.
- Source metadata drive the purge interval: the splitter takes it as a required
  argument with no default, and the event-holdout command derives it from the
  registry over the sources its feature set names.
- September 2019 and March 2020 event windows are frozen and checksummed, and the
  scoring and knowledge holdouts are kept distinct in code and in reporting.
- Forecast-distribution, exceedance, calibration, and dependence-aware uncertainty
  metrics are implemented and tested.

These facts show that the research harness operates. They do not establish
forecast skill, because the checked-in sample is synthetic and only one model has
been fitted.

## Known gaps in the evidence

Stated explicitly, because each is easy to mistake for something stronger.

- **The forecast interface has one implementer.** Its conformance suite is
  therefore evidence about `FittedPersistence`, not yet about the interface. A
  second model is what converts that into a tested constraint.
- **The training-frame and feature-row shapes are undeclared.** Only `date`,
  `sofr` and `iorb` are guaranteed columns; every other field is optional and may
  be absent. No model has yet needed more, so nothing has had to specify it.
- **The persistence backtest does not route through the splitter.** It is a
  one-step-ahead walk-forward, refitting at every origin. The purged rolling-origin
  splitter is implemented and tested, and the event-holdout path uses a
  registry-derived purge, but the benchmark backtest does not yet call either.
- **Transform isolation is untested in practice.** The contract requires fitted
  transform parameters to come from the training window alone; the only fitted
  model learns no transforms, so the check has nothing to act on until a model
  with imputation or scaling exists.
- **The monthly N-MFP panel is a single observation.** One quarterly archive yields
  one complete monthly cross-section, and one archive has been acquired. After the
  coverage floor is applied, the monthly `mmf_*` series have one reference date. No
  monthly N-MFP field can serve as a regressor until the archive history is
  backfilled. The daily shareholder-flow series are not affected.
- **A declared field has never produced data.** `mmf_on_rrp` is declared in the
  source registry and has emitted no row against any real archive. Its derivation
  searches security-description text for a counterparty name. For the period held
  the true value is probably near zero, which is precisely why that period cannot
  distinguish a working derivation from a broken one. `mmf_repo_holdings` is
  affected wherever this is, since private-sector repo is the difference between
  the two series.
- **The adapter has parsed exactly one archive.** Form N-MFP has been through
  several schema versions. A renamed column in a table that still exists yields no
  error, no missingness signal, and an accounting identity that still reconciles
  because both sides lost the same rows. Nothing has yet tested the adapter against
  schema variation.

## Work required before empirical claims

1. Backfill and freeze the SEC Form N-MFP archive history, applying the coverage
   floor to every reference date found rather than trusting an archive's contents,
   and refusing any archive whose schema the adapter cannot read faithfully. This
   gates most of what follows.
2. Establish whether `mmf_on_rrp` is derived correctly, against a period in which
   money funds held Fed reverse repo at scale, and make an absent declared field
   distinguishable from a parsing failure.
3. Resolve the N-MFP identity-tolerance and Treasury-settlement aggregation
   decisions recorded in `DATA_QUALITY_DECISIONS.md`. The tolerance decision waits
   on item 1: it cannot honestly be calibrated against one cross-section.
4. Extend the same freeze to the remaining sources, with a machine-readable quality
   report.
5. Fit transparent ARX and threshold benchmarks against the shared interface,
   before adding a more flexible quantile model.
6. Route the benchmark backtests through the purged rolling-origin splitter, so
   every model is compared on the same gap.
7. Compare every challenger with persistence under purged rolling-origin
   evaluation, then report the frozen event windows separately.
8. Add a quantile machine-learning model only after the baselines are frozen.

## Portfolio interpretation

The repository may accurately be described as a leakage-safe, point-in-time
financial research pipeline with a tested probabilistic evaluation harness. It
should not yet be described as a successful machine-learning forecast of repo
stress: no challenger has been fitted, no result rests on real data, and the
monthly money-fund panel is one cross-section rather than a series.

The next portfolio milestone is a compact results package containing a frozen data
snapshot, a persistence-versus-challenger comparison under purged evaluation,
tail-calibration evidence, event-window plots, limitations, and exact reproduction
instructions.
