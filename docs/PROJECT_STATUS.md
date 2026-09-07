# Project Status

**Measured on 7 September 2026 at commit `5dea543`.** This page is a snapshot,
not a claim that the repository is complete.

## Summary

Repo Market Model is currently a tested research and evaluation foundation for a
probabilistic repo-market forecast. It is not yet a validated forecasting model.

The strongest completed work is the part that prevents misleading empirical
results: point-in-time provenance, release-lag handling, immutable acquisition,
purged time-series evaluation, event-window separation, and probabilistic scoring.
The principal missing work is a complete historical panel and a fitted challenger
that can be evaluated against persistence.

## Evidence available now

- The standard-library suite completes successfully: 360 tests pass and one
  expected failure marks the intentionally absent fitted-model interface.
- A synthetic 25-row panel runs through audit and persistence backtest commands.
- Public-source downloads are stored immutably with timestamps and checksums.
- Panel rows can carry `ref_date`, `available_at`, vintage, and source provenance.
- Source metadata drive the purge interval used by time-series evaluation.
- September 2019 and March 2020 event windows are frozen and checksummed.
- Forecast-distribution, exceedance, calibration, and dependence-aware uncertainty
  metrics are implemented and tested.

These facts show that the research harness operates. They do not establish
forecast skill because the checked-in sample is synthetic.

## Work required before empirical claims

1. Exclude incomplete SEC Form N-MFP cross-sections using an independently
   testable coverage rule.
2. Resolve the N-MFP identity-tolerance and Treasury-settlement aggregation
   decisions recorded in `DATA_QUALITY_DECISIONS.md`.
3. Acquire and freeze a sufficiently long public-data history with a machine-readable
   quality report.
4. Implement the shared `fit`, `predict`, and `predict_stress` interface and replace
   its expected-failure presence test with behavioral tests.
5. Fit transparent AR/ARX and threshold benchmarks before adding a more flexible
   quantile model.
6. Compare every challenger with persistence under purged rolling-origin evaluation,
   then report the frozen event windows separately.

## Portfolio interpretation

The repository may accurately be described as a leakage-safe, point-in-time
financial research pipeline. It should not yet be described as a successful ML
forecast of repo stress. The next portfolio milestone is a compact results package
containing a frozen data snapshot, baseline comparison, tail-calibration evidence,
event-window plots, limitations, and exact reproduction instructions.
