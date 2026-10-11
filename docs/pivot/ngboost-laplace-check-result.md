# `ngboost_laplace`: the tier 1 pass #527 found, checked (#533)

A scratch measurement. [`judge-readings-result.md`](judge-readings-result.md) (#523) reports that `ngboost_laplace` passes tier 1
as declared under the weighted rule in force, 17 of 26 onsets warned at 1.73 weighted false alarms per onset, a row that neither
[`weighted-miss-result.md`](weighted-miss-result.md) (#463) nor [`weighted-miss-in-force-result.md`](weighted-miss-in-force-result.md)
(#472) lists. This page re-runs the row with the judge as declared and reports what the pass rests on. It changes nothing the
judge decides: `metadata/pressure_judge.json`, `metadata/weighted_miss.json` and every decision record are unchanged, nothing is
published, no rule changes, and no 2026 day is read ([`lockbox.md`](../decisions/lockbox.md)). Scored days 2018-06-29 to
2025-12-31, h = 1 to 5, +5 bp primary, 90% stationary-bootstrap intervals, the judge's seed. What is reported was declared before
any score in [`metadata/ngboost_laplace_check.json`](../../metadata/ngboost_laplace_check.json). Full tables and the machine-readable
result are in [`evidence/ngboost-laplace-check/`](evidence/ngboost-laplace-check/).

## 1. The 17 of 26 at 1.73 is confirmed

The judge, run with `--rule declared` (the weighted rule, in force) over the published benchmarks, the five risk-date passers and
`ngboost_laplace`, gives tier 1 for `ngboost_laplace`: **17 of 26 onsets warned, recall 0.654 [0.467, 0.826], climatology at the
same false alarms 0.231, 1.73 weighted false alarms per onset: pass.** Reading (a) of the script is checked against the judge's
own row for all eight rows under both rules (onsets warned, recall, false alarms per onset), and the script stops if they differ;
they agree. Nothing is corrected.

The same row's flat count is 4.08 false alarms per onset, which is what the "worst false alarms per onset" column of the
judge's Table 1 shows (the weighted count is the one the rule limits). The pass is on the weighted count only: under the unweighted rule it
warns 15 of 26 at 2.54 and fails.

**Why #463 and #472 did not list it.** #463 scored the candidates declared on `main` then and says so: "Candidates of open track
pull requests that are not declared on `main` (the quantile regression forest and the natural-gradient boosting rows of #413) are
not scored" (`weighted-miss-result.md`). #472 re-ran the judge on the benchmark forecasts and the risk-date severity forecasts only
(its reproduce commands read `bench_h?.json` and `risk_h?.json`); `ngboost_laplace` is produced by `scripts/pressure_track_q.py`
and was not an input. The row first appears with a weighted score in `regime-thresholds-result.md` (#461) (Table C, 17 of 26, 1.73,
tier 1 yes, tiers 3 and 5 no), and #523 carried it into its readings.

Tiers 3 and 5 are scored as well: `ngboost_laplace` fails both (tier 3: calibrated in 2 of the 4 regimes with a pressure day
at h = 1, so not at every regime; tier 5: not calibrated, though it beats climatology). **It does not pass the pass rule**, so no "Publish?" issue is
opened.

## 2. Tier 1 under readings (a) to (e)

Onsets warned (of 26) / false alarms per onset as the rule counts them. Weighted rule in force, with the five risk-date passers beside it.

| row | (a) as declared | (b1) one horizon alone | (b2) pooled | (d) before-episode discount | (e) outside 2018-19 |
|---|---|---|---|---|---|
| ngboost_laplace | 17 / 1.73 pass | pass (h = 1) | 17 / 2.34 fail | 16 / 2.23 fail | 5 of 9 / 0.50 fail |
| risk_gbm | 13 / 0.80 pass | pass | 13 / 1.48 pass | 13 / 0.95 pass | 3 / 1.61 fail |
| risk_gbm_base | 14 / 0.97 pass | pass | 14 / 1.59 pass | 14 / 1.08 pass | 4 / 2.06 fail |
| risk_logistic | 16 / 1.74 pass | pass | 16 / 2.55 fail | 16 / 1.90 pass | 6 / 4.39 fail |
| risk_logistic_base | 15 / 1.65 pass | pass | 15 / 2.18 fail | 14 / 1.78 pass | 5 / 3.67 fail |
| risk_quantile_skewt_base | 15 / 1.62 pass | pass | 15 / 2.14 fail | 15 / 1.81 pass | 5 / 3.81 fail |

Unweighted rule: `ngboost_laplace` is 15 / 2.54 fail as declared, 10 / 1.69 at its best single horizon (fail), 15 / 4.38 pooled, 4 / 0.33 outside
2018-19 (fail). The figures of the other five rows match `judge-readings-result.md` exactly. The pass is the same kind as the passers': it holds as
declared, and at h = 1 alone, and it does not hold pooled across horizons, under the before-episode discount, or outside 2018-19.
It is the one row that fails (d) while the five passers pass it.

* (e) Outside 2018-19, `ngboost_laplace` warns 5 of 9 onsets (recall 0.556, climatology 0.000) at 0.50 weighted false alarms per onset, the lowest
  of the rows shown there. Its recall criterion and its false alarm criterion are met, but the bootstrap interval on 9 onsets is undefined (it is not
  defined on every resample), so "the interval above climatology" cannot be shown and the subset fails, as it does for every row. In 2018-19 it warns 12 of 17 at 2.65.
* (c) The training-window check (cut-off in force applied to the earlier forecasts) is at most 2.0 at every refit and 0.74 to 1.64
  at the last refit, against 1.73 realised at the worst horizon: for this row the check is not inflating the count. (Beside
  `risk_gbm`: check at most 1.90, last 1.36 at h = 1.)

## 3. Recall by year

Onsets warned at lead of at least 1 (any horizon 1 to 5), weighted rule in force.

| row | 2018 | 2019 | 2020 | 2024 | 2025 |
|---|---|---|---|---|---|
| ngboost_laplace | 0 of 4 | 12 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| risk_gbm | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 3 of 5 |
| risk_gbm_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 4 of 5 |
| risk_logistic | 0 of 4 | 10 of 13 | 0 of 2 | 1 of 2 | 5 of 5 |
| risk_logistic_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| risk_quantile_skewt_base | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| calendar_climatology | 0 of 4 | 12 of 13 | 0 of 2 | 0 of 2 | 0 of 5 |
| persistence_logistic | 0 of 4 | 11 of 13 | 1 of 2 | 0 of 2 | 0 of 5 |

Those are all the years with an onset. **2018, 2020 and 2024: `ngboost_laplace` warns none of eight onsets** (0 of 4, 0 of 2, 0 of 2).
Its tier 1 pass is 2019 (12 of 13) and 2025 (5 of 5).

## 4. Episodes it warns that the five passers miss

`ngboost_laplace` warns 17 onsets; at least one of the five passers warns 16 (each passer: 13, 14, 16, 15, 15). Two onsets are warned by
`ngboost_laplace` and by none of the five:

* 2019-05-28, flagged at h = 3 and 5
* 2019-06-25, flagged at h = 2, 3, 4 and 5

Both are in 2019, and neither is flagged at h = 1. One onset,
2024-09-30, is warned by a passer (`risk_logistic`) and not by `ngboost_laplace`. So the 17 against the passers' 16 at most is a gain of two
2019 onsets and a loss of one in 2024.

## 5. Constant or degenerate across refits

Refit blocks of 21 scored days, at each horizon (90 blocks at h = 1 to 4, 89 at h = 5). "Constant": the +5 bp probability has a range
of at most 1e-9 over the block. "Flags nothing": the cut-off in force is infinite. "Flags every day": the cut-off is at or below the block's
smallest probability. No block is all zero and no day has probability 0.

| h | constant blocks | cut-off flags nothing | cut-off flags every day | distinct probabilities |
|---|---|---|---|---|
| 1 | 2 | 6 | 3 | 899 |
| 2 | 10 | 7 | 3 | 781 |
| 3 | 11 | 7 | 4 | 758 |
| 4 | 9 | 6 | 5 | 784 |
| 5 | 10 | 6 | 5 | 761 |

The constant blocks fall mostly between April 2021 and March 2022 (at h = 1 the two are 2018-11-30 and 2022-03-14; there is also 2023-02-16 at
h = 2 and 2025-12-31 at h = 4), a stretch with no onset. The cut-off flags nothing in the first six or seven blocks of every horizon (scoring
starts in June 2018 and the last of them is in January 2019 at the latest), and flags every day in three to five blocks, all in 2019. No block is constant
in 2019, or in 2025 except the one-day last block at h = 4, where the row's warnings are. The block dates are in the evidence (`blocks`).

## 6. Paired against `risk_gbm`, climatology and persistence-logistic

Brier difference at +5 bp, reference minus `ngboost_laplace` (positive: `ngboost_laplace` is better), 90% interval; the by-regime and
by-pressure-day-type cells at h = 1 are below, all horizons and the scarcity-state split are in the evidence.

| reference | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|
| risk_gbm | 0.011 [0.003, 0.021] | 0.012 [0.004, 0.022] | 0.007 [-0.001, 0.017] | 0.005 [-0.003, 0.016] | 0.006 [-0.003, 0.016] |
| calendar_climatology | 0.025 [0.019, 0.032] | 0.014 [0.009, 0.020] | 0.011 [0.005, 0.017] | 0.009 [0.003, 0.016] | 0.007 [-0.001, 0.014] |
| persistence_logistic | 0.010 [0.005, 0.015] | 0.004 [-0.001, 0.009] | 0.005 [-0.001, 0.010] | 0.001 [-0.005, 0.006] | -0.000 [-0.007, 0.006] |

At h = 1, by regime:

| regime | vs risk_gbm | vs calendar_climatology | vs persistence_logistic |
|---|---|---|---|
| 2018-19 | 0.053 [0.014, 0.098] | 0.054 [0.026, 0.084] | 0.038 [0.022, 0.055] |
| 2020 | -0.007 [-0.010, -0.003] | 0.033 [0.023, 0.042] | 0.009 [0.004, 0.016] |
| 2021-23 | 0.000 [-0.000, 0.000] | 0.014 [0.012, 0.016] | 0.001 [0.001, 0.001] |
| 2024 | 0.000 [0.000, 0.001] | 0.004 [0.001, 0.007] | 0.004 [0.001, 0.009] |
| 2025-26 | 0.013 [0.002, 0.026] | 0.029 [0.011, 0.050] | 0.003 [-0.021, 0.024] |

At h = 1, by pressure-day type:

| type | vs risk_gbm | vs calendar_climatology | vs persistence_logistic |
|---|---|---|---|
| month_end | -0.006 [-0.020, 0.008] | 0.048 [0.029, 0.068] | 0.027 [0.010, 0.045] |
| ordinary | 0.014 [0.005, 0.025] | 0.019 [0.012, 0.026] | 0.006 [0.002, 0.010] |
| quarter_end | 0.015 [-0.025, 0.064] | 0.131 [0.051, 0.213] | 0.070 [0.019, 0.133] |
| tax_date | -0.002 [-0.030, 0.031] | 0.067 [0.048, 0.086] | 0.031 [0.012, 0.053] |

Onset recall, `ngboost_laplace` minus the reference, each at its own chosen cut-offs, any horizon 1 to 5, 26 onsets:

| reference | recall difference [90%] | 2018-19 (17 onsets) | 2020 / 2024 (2 each) | 2025-26 (5) | ordinary day (12) |
|---|---|---|---|---|---|
| risk_gbm | 0.154 [0.038, 0.286] | 0.118 [0.000, 0.273] | 0.000 / 0.000 | 0.400 | 0.250 [0.000, 0.500] |
| calendar_climatology | 0.192 [0.000, 0.382] | 0.000 [-0.143, 0.143] | 0.000 / 0.000 | 1.000 | 0.167 [-0.100, 0.445] |
| persistence_logistic | 0.192 [0.000, 0.409] | 0.059 [-0.120, 0.250] | -0.500 / 0.000 | 1.000 | 0.083 [-0.222, 0.400] |

(An interval is shown only where the bootstrap defines it on every resample; cells with 2 to 5 onsets usually do not.)

* **Against `risk_gbm`** the row is better at h = 1 and h = 2 (the interval excludes 0), and it warns more onsets (2025: 5 against 3), but the gain
  is the 2018-19 regime and ordinary days; it is worse in 2020 (-0.007, the interval excludes 0) and not better on month-end or tax days. Its
  recall difference excludes 0 pooled (0.154 [0.038, 0.286]) but not within 2018-19 (the lower end is 0.000) and not on ordinary days.
* **Against climatology** its Brier is better at h = 1 to 4 pooled, but the recall difference's lower end is 0.000, and in 2018-19, where 17 of the 26 onsets are, the recall
  difference is 0.000: climatology's calendar warns as many onsets of 2019 (12 of 13) as `ngboost_laplace`. The recall advantage is the five onsets of 2025,
  which climatology never warns.
* **Against persistence-logistic** the Brier gain is at h = 1 only (0.010); the recall difference's lower end is 0.000.

## What this does and does not show

* The row's tier 1 pass is real as declared under the weighted rule in force, and is of the same kind as the five passers' pass: it depends on how the
  judge counts (pooling across horizons and the before-episode discount both take it away), and it does not hold outside 2018-19.
* It is not better than the passers on the hard years: none of 2018, 2020 or 2024. Its extra warnings are two 2019 onsets and 2025, where
  it warns all five onsets and `risk_gbm` three.
* It fails tiers 3 and 5, so it does not pass the pass rule and nothing about the published declaration moves. No "Publish?" issue is opened.

## Not checked

* Tier 1 is the only tier re-read under readings (a) to (e); tiers 3 and 5 are the judge's own verdicts as declared.
* Reading (d) is the one interpretation of "discount only alarms before an episode" of `judge-readings-result.md`.
* The paired onset recall uses each reference at its own chosen cut-offs and flags (any horizon); a reference matched to the row's false alarms is the
  judge's own "climatology recall at the same false alarms" column (0.231 for this row).
* Whether the row should join any declaration, and which reading is the right one, are Eleonora's decisions; this page makes neither.

## Reproduce

Published panel `4ddc3882…` (`REPRODUCIBILITY.md`), scratch panels as in [`judge-readings-result.md`](judge-readings-result.md). Run with
`/opt/rmm-venv/bin/python` and `OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`. The forecasts took about nine minutes per horizon for
`ngboost_laplace`, six for the benchmarks and thirteen for the risk-date rows at one thread; the scoring took about nine minutes.

```
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
for h in 1 2 3 4 5:
  PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUB.csv --horizon $h --published --output OUT/bench_h$h.json
  PYTHONPATH=src python3 scripts/risk_date_severity.py run --panel AUG2.csv --published PUB.csv --horizon $h --output OUT/risk_h$h.json
  PYTHONPATH=src python3 scripts/pressure_track_q.py forecasts --panel PUB.csv --horizon $h --output OUT/q_h$h.json --distribution OUT/qdist_h$h.json
PYTHONPATH=src python3 scripts/ngboost_laplace_check.py score --panel PUB.csv --bench 'OUT/bench_h{h}.json' --risk 'OUT/risk_h{h}.json' \
    --row 'OUT/q_h{h}.json' --output OUT/check.json --markdown OUT/check.md
```
