# The live-monitoring read, replayed on the development record (#969, H5 groundwork G3)

**Development data, not a verdict. No lockbox day and no day after 2025-12-31 is read; no published record or declaration changes; the thresholds below are proposals, not decisions.** Every figure is read from `docs/research/live-monitoring-969/replay.json`, written by `scripts/live_monitor.py replay` under the declaration `metadata/live_monitoring_969.json`, which was committed before any number was computed.

## What was built

A reported-only reader of the live record and the public outcomes (`src/repo_model/live_monitor.py`, `scripts/live_monitor.py`). It computes, per lead: the rolling 60-day coverage of the 90% band (q05 to q95); the 125-day Kupiec and Christoffersen tests on the q95 miss indicator (a miss is an outcome strictly above q95); the 6-bin PIT on the five published quantiles and the share at or below q25; the CRPS ratio of the published distribution to B1 and to B2 (below 1 favours the model); per-source input staleness against the worst-case lags in `metadata/sources.json`; and the pin check against `metadata/live_pin.json`. It gives no verdict, opens no tier and runs no new forecast.

The read of live outcomes is gated. `require_decision_record` refuses (`LookAheadError`) unless `docs/decisions/live-monitoring.md` exists as a merged record; only the draft, `docs/decisions/drafts/live-monitoring.md`, is in this pull request, and `tests/test_live_monitor.py` pins that a file under `drafts/` does not open the gate. Nothing in the repository reads a locked outcome.

## What the replay reads

The published model's daily forecasts at lead 1 (`docs/runs/published_distribution_daily_h1.json`, which reproduces the published CRPS record exactly) against the realised spread, from 2018-06-29 to 2025-12-31. B1 and B2 are rebuilt from the published panel (digest `4ddc3882cd6d406b11e1088f8ff6195e16dde175a0ad6818abe40dd5bdac8999`, built from the tracked fixtures as `REPRODUCIBILITY.md` describes) by `protocol_benchmarks`, as of each decision day. The 60-day coverage needs 60 days and the 125-day statistics 125, so the first rows carry no figure (`too_few_days`). The record's own `2025-26` regime label is read for 2025 only here.

## 1. By regime

Shares and rates are over the regime's days. A Kupiec p-value is two-sided in effect: too few misses is also a failure, and 2021-23 fails it that way.

| regime | days | 90% band coverage | lowest 60-day coverage | q95 misses (rate) | Kupiec p | Christoffersen p | share at or below q25 | CRPS ratio to B1 | CRPS ratio to B2 |
|---|---|---|---|---|---|---|---|---|---|
| 2018-19 | 375 | 0.861 | 0.700 | 31 (0.083) | 0.0077 | <1e-6 | 0.283 | 0.700 | 0.874 |
| 2020 | 251 | 0.896 | 0.800 | 15 (0.060) | 0.4906 | 0.2782 | 0.263 | 0.931 | 0.460 |
| 2021-23 | 748 | 0.910 | 0.767 | 17 (0.023) | 1.4e-04 | <1e-6 | 0.604 | 1.266 | 0.472 |
| 2024 | 250 | 0.844 | 0.717 | 29 (0.116) | 3.8e-05 | 7.0e-06 | 0.300 | 0.749 | 0.856 |
| 2025-26 | 249 | 0.892 | 0.733 | 23 (0.092) | 0.0058 | 0.0021 | 0.337 | 0.789 | 0.609 |


The PIT by regime, as shares of the regime's days in each bin (bin 0 is an outcome at or below q05, bin 5 above q95; expected 0.05, 0.20, 0.25, 0.25, 0.20, 0.05):

| regime | bin 0 | bin 1 | bin 2 | bin 3 | bin 4 | bin 5 |
|---|---|---|---|---|---|---|
| 2018-19 | 0.056 | 0.227 | 0.147 | 0.200 | 0.288 | 0.083 |
| 2020 | 0.044 | 0.219 | 0.219 | 0.127 | 0.331 | 0.060 |
| 2021-23 | 0.067 | 0.537 | 0.175 | 0.103 | 0.095 | 0.023 |
| 2024 | 0.040 | 0.260 | 0.180 | 0.168 | 0.236 | 0.116 |
| 2025-26 | 0.016 | 0.321 | 0.153 | 0.149 | 0.269 | 0.092 |

## 2. Would the signatures have fired?

The flags use the proposed thresholds of the declaration (amber when the 60-day coverage is below 0.80 or above 0.98, when a Kupiec or Christoffersen p-value is below 0.01, when the share at or below q25 is outside [0.15, 0.35], when the CRPS ratio to B1 is above 1.0; stop when the coverage is below 0.70, when both p-values are below 0.01 together, or when the ratio is above 1.1). Days are those of the regime on which the flag was set.

| regime | days | band coverage flag days | Kupiec flag days | Christoffersen flag days | PIT flag days | CRPS ratio amber days | CRPS ratio stop days | calibration stop days | band coverage stop days |
|---|---|---|---|---|---|---|---|---|---|
| 2018-19 | 375 | 32 | 31 | 125 | 6 | 0 | 0 | 5 | 0 |
| 2020 | 251 | 20 | 0 | 35 | 127 | 42 | 12 | 0 | 0 |
| 2021-23 | 748 | 163 | 443 | 87 | 634 | 497 | 428 | 0 | 0 |
| 2024 | 250 | 28 | 78 | 182 | 52 | 0 | 0 | 13 | 0 |
| 2025-26 | 249 | 21 | 122 | 121 | 123 | 0 | 0 | 98 | 0 |

| regime | first dates a flag fired |
|---|---|
| 2018-19 | band coverage amber 2018-11-19; calibration stop 2018-12-31; christoffersen amber 2018-12-31; kupiec amber 2018-12-31; pit amber 2019-12-23 |
| 2020 | band coverage amber 2020-06-17; christoffersen amber 2020-01-30; crps ratio amber 2020-09-02; crps ratio stop 2020-09-16; pit amber 2020-01-02 |
| 2021-23 | band coverage amber 2021-01-27; christoffersen amber 2021-07-01; crps ratio amber 2021-06-29; crps ratio stop 2021-07-09; kupiec amber 2021-07-02; pit amber 2021-03-08 |
| 2024 | band coverage amber 2024-11-04; calibration stop 2024-09-04; christoffersen amber 2024-01-02; kupiec amber 2024-09-04; pit amber 2024-01-02 |
| 2025-26 | band coverage amber 2025-01-02; calibration stop 2025-01-02; christoffersen amber 2025-01-02; kupiec amber 2025-01-02; pit amber 2025-03-13 |


- **2021-23 would have fired, on the score, from mid-2021.** The CRPS ratio to B1 goes above 1.0 on 2021-06-29 and above 1.1 on 2021-07-09, and the share at or below q25 leaves its band on 2021-03-08; across the regime the published distribution scores 1.266 times B1 and 0.604 of outcomes fall at or below q25 (expected 0.25; bin 1 holds 0.537 against 0.20). The CRPS-ratio stop is set on no day outside 2020 (12 days, from 2020-09-16) and 2021-23, so among the figures read here it is the one that separates this regime from the others.
- **2024 would have fired, on tail calibration, from September.** The q95 misses are 29 of 250 days (0.116 against 0.05), the Kupiec and Christoffersen p-values are both far below 0.01 (3.8e-05 and 7.0e-06), and the combined calibration stop is set from 2024-09-04. The same stop is set in 2018-19 (5 days, from 2018-12-31) and in 2025 (98 days), so it does not separate 2024 from the other years. The CRPS ratio to B1 stays below 1 in 2024 (0.749): the score does not flag it.
- **The proposed thresholds do not discriminate.** Under them at least one flag is set on 1,500 of the 1,873 days. The Christoffersen test is set in every regime, because the published distribution's misses cluster in all of them (the directive's own check finds the published model at h = 1 failing independence on every tracked record), and the Kupiec and PIT flags are set in most. A reader acting on every amber would be told most days that something is wrong. What the replay supports is the narrower statement above: a CRPS ratio to B1 above 1.1 is set only in late 2020 and 2021-23, and the combined Kupiec and Christoffersen stop only where the q95 miss rate is far above 5% (2018-19, 2024 and 2025). The share at or below q25 is outside its band in 2020, 2021-23, 2024 and 2025, so it does not single out 2021-23 either, although it is the furthest out there (0.604).
- **What this does not show.** It is one model at one lead on development days, replayed with thresholds written by the directive's author with the 2021-23 and 2024 episodes already known, so the table is a description, not a test of the thresholds. Lens D's own thresholds (#958, #950 row 8) are not in the directive and were not used.

## 3. The other checks, on synthetic records

Per-field staleness and the pin check have no development record to replay: the daily file holds forecasts and outcomes only. Both are exercised on synthetic records in `tests/test_live_monitor.py`. The live record carries each source's retrieval time and the panel's last date, not each field's last print, so the staleness read is per source and per panel, against `release_lag.worst_case_calendar_days`; per-field staleness needs the record to carry field dates, which is a change to the live record (#970 part 4 proposes it; the record and its pin are owner-attested).

## 4. For Eleonora

The decision record is `docs/decisions/drafts/live-monitoring.md`. Its three questions are marked there: whether a monitoring read of blind-tier outcomes before a scoring date is a comparison under `lockbox.md`, how often the job runs and where it publishes, and which thresholds, if any. Nothing reads a locked outcome until she has merged the record herself.

## Reproduce

```
PYTHONPATH=src python3 scripts/live_monitor.py replay --panel /tmp/funding_panel.csv --output /tmp/replay.json
```

with `/tmp/funding_panel.csv` built and verified by the first two commands of `REPRODUCIBILITY.md`, and the output equal to `docs/research/live-monitoring-969/replay.json`.
