# Superseded: the funding declaration calibrated by CV+

These three records were the published funding declaration's gbm, calibrated by cross-conformal (CV+,
`--calibration cross_conformal --calibration-folds 5`), scored under the as-of rule through 2026-09-03:

- `backtest_gbm_cross_conformal_funding.json`
- `compare_persistence_vs_gbm_cross_conformal_funding_crps.json`
- `exceedance_gbm_cross_conformal_funding.json`

**Why they were archived.** Eleonora ruled on
[#123](https://github.com/eleonorabjornberg/repo-market-model/issues/123) that the published funding
declaration replaces CV+ with conformal PID and its calendar scorecaster, exactly as
[#122](https://github.com/eleonorabjornberg/repo-market-model/pull/122) scored it. Directive
[#124](https://github.com/eleonorabjornberg/repo-market-model/issues/124) republished the declaration under
that calibration. The pull request for #124 moved these records here unedited, as the rule "never edit a
published record in place" requires.

**What replaced them.** `backtest_gbm_conformal_pid_funding.json`,
`compare_persistence_vs_gbm_conformal_pid_funding_crps.json` and
`exceedance_gbm_conformal_pid_funding.json` at the top level of `docs/runs/`. Under
`docs/decisions/lockbox.md` those score only days before 2026-01-01, so their figures are not comparable with
the figures here.

No page is generated from this folder: `scripts/emit_results.py` renders from the records at the top level of
`docs/runs/` only.
