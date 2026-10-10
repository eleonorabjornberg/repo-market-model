# Tier 3 for the tier-1 passers: why regime calibration fails, and a per-regime recalibration (#471)

A scratch measurement under the pressure-day judge (#375, as amended by #407 and the draft weighted rule of #454). It writes
nothing into `docs/runs/`, moves no published figure and logs nothing to the live record. Scored days 2018-06-29 to
2025-12-31 only; no 2026 day is read and the confirmation window is not looked at (`docs/decisions/lockbox.md`).

**The five.** The risk-date models of #428 that meet tier 1 (`docs/pivot/risk-date-severity-result.md`): `risk_gbm`,
`risk_gbm_base`, `risk_logistic`, `risk_logistic_base`, `risk_quantile_skewt_base`. Each is fitted exactly as
`metadata/risk_date_severity.json` declares, unchanged.

## What was declared

Before any recalibrated score, in `metadata/regime_recalibration.json` and one candidate file per form
(`metadata/pressure_judge/candidates/<base>+regime_recal.json`), committed first:

* **Remedy.** A Platt curve per declared regime (`metadata/evaluation_splits.json`: 2018-19, 2020, 2021-23, 2024, 2025-26), per
  threshold and horizon, applied to the base's raw exceedance probability on every scored day, then made non-increasing in tau.
* **No look-ahead.** The regime is read off the calendar date (known at the decision instant). A refit block's curve for a regime is
  fitted on that regime's own pairs whose scored day is at or before the block's last training label, and on none other
  (`group_calibration.regime_walk_forward`, which is `walk_forward('group')` with the regime as the group; the guard
  `group_calibration.require_regimes_asof` refuses a label that is not the calendar's, and `fit` refuses a late pair).
* **Fallback and gate.** The pooled Platt curve while the regime holds fewer than 60 earlier pairs or 3 events; identity before
  the pooled gate of 250 pairs and 5 events. Both are the constants #380 declared; none was searched.
* **Flag cut-offs** are the judge's, chosen at each refit from its training window alone.

## Reproduce

Published panel `4ddc3882…`; scratch panel from `pressure_v1_1.py panel` then `measurement_fields.py panel`.

```
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
for h in 1 2 3 4 5: OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/regime_recalibration.py run --panel AUG2.csv --published PUBLISHED.csv --horizon $h --output OUT/regime_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src /opt/rmm-venv/bin/python scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --published --output OUT/bench_h$h.json
for r in unweighted weighted: PYTHONPATH=src /opt/rmm-venv/bin/python scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule $r --output OUT/judge_$r.json OUT/bench_h?.json OUT/regime_h?.json
PYTHONPATH=src python3 scripts/regime_recalibration.py tables OUT/judge_unweighted.json OUT/judge_weighted.json --output OUT/tables.md
```

Evidence: `docs/pivot/evidence/regime-recalibration/tables.md` (the diagnosis for every horizon, and the full judge row).

## Result: no form passes; per-regime recalibration is not the remedy

### Diagnosis (the base forms)

Cells are mean predicted / realised pressure-day rate at +5 bp, then realised minus predicted with the judge's 90% stationary-bootstrap
interval (positive = the model under-forecasts). Tier 3 tests only regimes that had a pressure day; 2021-23 had none and is reported.

Table 1. Horizon 1.

| model | 2018-19 | 2020 | 2021-23 | 2024 | 2025-26 |
|---|---|---|---|---|---|
| risk_gbm | 0.096 / 0.272: +0.176 [+0.099, +0.253] | 0.015 / 0.016: +0.001 [-0.012, +0.017] | 0.001 / 0.000: -0.001 [-0.001, -0.000] | 0.003 / 0.020: +0.017 [-0.001, +0.039] | 0.039 / 0.116: +0.078 [+0.011, +0.162] |
| risk_gbm_base | 0.097 / 0.272: +0.175 [+0.105, +0.252] | 0.025 / 0.016: -0.009 [-0.027, +0.010] | 0.000 / 0.000: -0.000 [-0.000, -0.000] | 0.002 / 0.020: +0.018 [-0.000, +0.040] | 0.035 / 0.116: +0.081 [+0.018, +0.163] |
| risk_logistic | 0.107 / 0.272: +0.165 [+0.092, +0.234] | 0.031 / 0.016: -0.015 [-0.037, +0.007] | 0.000 / 0.000: -0.000 [-0.001, -0.000] | 0.006 / 0.020: +0.014 [-0.002, +0.034] | 0.033 / 0.116: +0.083 [+0.014, +0.170] |
| risk_logistic_base | 0.108 / 0.272: +0.164 [+0.091, +0.235] | 0.029 / 0.016: -0.013 [-0.031, +0.005] | 0.000 / 0.000: -0.000 [-0.000, -0.000] | 0.003 / 0.020: +0.017 [-0.000, +0.040] | 0.031 / 0.116: +0.085 [+0.018, +0.168] |
| risk_quantile_skewt_base | 0.120 / 0.272: +0.152 [+0.077, +0.228] | 0.047 / 0.016: -0.031 [-0.052, -0.008] | 0.003 / 0.000: -0.003 [-0.004, -0.002] | 0.012 / 0.020: +0.008 [-0.004, +0.024] | 0.051 / 0.116: +0.066 [+0.009, +0.134] |

Table 2. Horizon 5 (h = 2 to 4 read alike; see the evidence file).

| model | 2018-19 | 2020 | 2021-23 | 2024 | 2025-26 |
|---|---|---|---|---|---|
| risk_gbm | 0.054 / 0.270: +0.215 [+0.133, +0.301] | 0.014 / 0.016: +0.002 [-0.016, +0.027] | 0.001 / 0.000: -0.001 [-0.002, -0.000] | 0.001 / 0.020: +0.019 [-0.000, +0.046] | 0.012 / 0.116: +0.105 [+0.027, +0.198] |
| risk_gbm_base | 0.059 / 0.270: +0.210 [+0.129, +0.300] | 0.019 / 0.016: -0.004 [-0.023, +0.020] | 0.001 / 0.000: -0.001 [-0.001, -0.001] | 0.000 / 0.020: +0.020 [-0.000, +0.045] | 0.007 / 0.116: +0.109 [+0.032, +0.208] |
| risk_logistic | 0.061 / 0.270: +0.208 [+0.121, +0.292] | 0.020 / 0.016: -0.005 [-0.035, +0.025] | 0.000 / 0.000: -0.000 [-0.001, -0.000] | 0.002 / 0.020: +0.018 [-0.001, +0.042] | 0.016 / 0.116: +0.101 [+0.024, +0.200] |
| risk_logistic_base | 0.070 / 0.270: +0.200 [+0.117, +0.286] | 0.023 / 0.016: -0.007 [-0.036, +0.022] | 0.000 / 0.000: -0.000 [-0.000, -0.000] | 0.001 / 0.020: +0.019 [-0.000, +0.044] | 0.013 / 0.116: +0.103 [+0.026, +0.197] |
| risk_quantile_skewt_base | 0.092 / 0.270: +0.177 [+0.099, +0.263] | 0.032 / 0.016: -0.016 [-0.042, +0.011] | 0.003 / 0.000: -0.003 [-0.004, -0.002] | 0.004 / 0.020: +0.016 [-0.002, +0.039] | 0.025 / 0.116: +0.092 [+0.023, +0.175] |

All five fail tier 3 at every horizon in the same two regimes, in the same direction: **2018-19 and 2025-26 are under-forecast**
(realised 0.27 and 0.12 against predicted 0.05 to 0.12 and 0.01 to 0.05). 2020 and 2024 cover zero at every horizon (except \`risk_quantile_skewt_base\` in 2020 at h = 1, over-forecast); 2021-23 is
over-forecast by about a thousandth. The abundant-regime flag-rate limit holds. What fails is level, not ranking: the models separate pressure days but
sit far below the realised rate in the two regimes with the most pressure days, because they forecast exactly 0 on every day that is
not a risk date, and in those regimes a large share of pressure days fall on non-risk days (see the risk-date result: only 21 of 27
onsets at h = 1 and 13 of 26 at h >= 2 fall on risk dates).

### The remedy

Table 3. Horizon 1, per-regime Platt forms.

| model | 2018-19 | 2020 | 2021-23 | 2024 | 2025-26 |
|---|---|---|---|---|---|
| risk_gbm+regime_recal | 0.144 / 0.272: +0.128 [+0.050, +0.206] | 0.086 / 0.016: -0.070 [-0.108, -0.039] | 0.090 / 0.000: -0.090 [-0.098, -0.084] | 0.055 / 0.020: -0.035 [-0.053, -0.013] | 0.072 / 0.116: +0.044 [-0.028, +0.130] |
| risk_gbm_base+regime_recal | 0.143 / 0.272: +0.129 [+0.054, +0.208] | 0.087 / 0.016: -0.071 [-0.108, -0.040] | 0.090 / 0.000: -0.090 [-0.096, -0.083] | 0.055 / 0.020: -0.035 [-0.053, -0.012] | 0.076 / 0.116: +0.041 [-0.026, +0.130] |
| risk_logistic+regime_recal | 0.152 / 0.272: +0.120 [+0.047, +0.197] | 0.088 / 0.016: -0.073 [-0.111, -0.041] | 0.092 / 0.000: -0.092 [-0.098, -0.087] | 0.064 / 0.020: -0.044 [-0.062, -0.022] | 0.069 / 0.116: +0.047 [-0.031, +0.145] |
| risk_logistic_base+regime_recal | 0.152 / 0.272: +0.120 [+0.046, +0.200] | 0.087 / 0.016: -0.071 [-0.109, -0.040] | 0.091 / 0.000: -0.091 [-0.096, -0.085] | 0.061 / 0.020: -0.041 [-0.059, -0.017] | 0.070 / 0.116: +0.046 [-0.029, +0.139] |
| risk_quantile_skewt_base+regime_recal | 0.163 / 0.272: +0.109 [+0.032, +0.192] | 0.086 / 0.016: -0.070 [-0.105, -0.039] | 0.092 / 0.000: -0.092 [-0.097, -0.087] | 0.063 / 0.020: -0.043 [-0.061, -0.023] | 0.076 / 0.116: +0.041 [-0.029, +0.131] |

Table 4. Horizon 5.

| model | 2018-19 | 2020 | 2021-23 | 2024 | 2025-26 |
|---|---|---|---|---|---|
| risk_gbm+regime_recal | 0.103 / 0.270: +0.166 [+0.077, +0.259] | 0.091 / 0.016: -0.075 [-0.113, -0.043] | 0.105 / 0.000: -0.105 [-0.112, -0.098] | 0.064 / 0.020: -0.044 [-0.063, -0.020] | 0.066 / 0.116: +0.051 [-0.025, +0.145] |
| risk_gbm_base+regime_recal | 0.105 / 0.270: +0.165 [+0.073, +0.259] | 0.091 / 0.016: -0.075 [-0.113, -0.043] | 0.105 / 0.000: -0.105 [-0.111, -0.098] | 0.063 / 0.020: -0.043 [-0.063, -0.019] | 0.064 / 0.116: +0.052 [-0.028, +0.151] |
| risk_logistic+regime_recal | 0.111 / 0.270: +0.159 [+0.074, +0.253] | 0.091 / 0.016: -0.075 [-0.114, -0.042] | 0.105 / 0.000: -0.105 [-0.112, -0.100] | 0.069 / 0.020: -0.049 [-0.068, -0.025] | 0.066 / 0.116: +0.051 [-0.029, +0.151] |
| risk_logistic_base+regime_recal | 0.117 / 0.270: +0.153 [+0.067, +0.242] | 0.091 / 0.016: -0.075 [-0.115, -0.042] | 0.104 / 0.000: -0.104 [-0.111, -0.098] | 0.067 / 0.020: -0.047 [-0.066, -0.022] | 0.066 / 0.116: +0.050 [-0.027, +0.144] |
| risk_quantile_skewt_base+regime_recal | 0.136 / 0.270: +0.134 [+0.048, +0.221] | 0.090 / 0.016: -0.074 [-0.113, -0.040] | 0.101 / 0.000: -0.101 [-0.106, -0.096] | 0.066 / 0.020: -0.046 [-0.065, -0.022] | 0.066 / 0.116: +0.051 [-0.028, +0.147] |

The recalibration fixes what it was built for in 2025-26 (the interval now covers zero at every horizon) and narrows the miss in 2018-19 (about +0.18 to +0.11 at h = 1),
but it breaks three regimes that were calibrated or nearly so (2020 and 2024 fail at every horizon for all five forms):

* **2021-23, 2020 and 2024 are now over-forecast** (about 0.09, 0.09 and 0.06 predicted against 0.00, 0.02 and 0.02 realised). The raw
  forecast is exactly 0 on every non-risk day, so a Platt curve fitted on all days gives those days the regime's non-risk base rate;
  2021-23 holds no event, so it takes the pooled curve, which carries the pressure rate of 2018-19 into the calm years.
* **2018-19 is still under-forecast** (+0.11 to +0.13 at h = 1). The regime is the first one scored: the pooled gate (250 pairs, 5
  events) holds the curve at the identity for the regime's first 250 days of its 375, so most of 2018-19 is never recalibrated.

So the per-regime curve cannot be learned where it is needed most: a regime's own pairs are not there when its first days are forecast,
and the pooled stand-in imports the wrong regime's rate. This is a property of walk-forward calibration by calendar regime, not a tuning
detail.

### Full judge row (tiers 1, 3, 5)

Table 5. Base and recalibrated forms under the rule in force (flat: every false alarm counts 1) and the draft weighted rule
(`docs/decisions/weighted-miss.md`, a draft, not in force). Recall is onsets flagged of 26 over leads 1 to 5; false alarms per onset is
the worst horizon's under the run's own count (limit 2).

| model | onsets flagged (flat rule) | worst FA per onset (flat count) | tier 1 / 3 / 5, flat rule | pass, flat rule | onsets flagged (weighted rule) | worst FA per onset (weighted count) | tier 1 / 3 / 5, weighted rule | pass, weighted rule |
|---|---|---|---|---|---|---|---|---|
| risk_gbm | 13 of 26 (recall 0.50 [0.31, 0.67]) | 1.35 | pass / fail / fail | fail | 13 of 26 (recall 0.50 [0.31, 0.67]) | 1.38 | pass / fail / fail | fail |
| risk_gbm+regime_recal | 13 of 26 (recall 0.50 [0.31, 0.68]) | 2.62 | fail / fail / pass | fail | 13 of 26 (recall 0.50 [0.31, 0.68]) | 4.38 | fail / fail / pass | fail |
| risk_gbm_base | 14 of 26 (recall 0.54 [0.36, 0.72]) | 1.50 | pass / fail / fail | fail | 14 of 26 (recall 0.54 [0.36, 0.72]) | 1.50 | pass / fail / fail | fail |
| risk_gbm_base+regime_recal | 13 of 26 (recall 0.50 [0.31, 0.69]) | 2.58 | fail / fail / pass | fail | 13 of 26 (recall 0.50 [0.31, 0.69]) | 3.81 | pass / fail / pass | fail |
| risk_logistic | 14 of 26 (recall 0.54 [0.35, 0.72]) | 1.85 | pass / fail / fail | fail | 16 of 26 (recall 0.62 [0.43, 0.80]) | 2.42 | pass / fail / fail | fail |
| risk_logistic+regime_recal | 14 of 26 (recall 0.54 [0.36, 0.71]) | 2.92 | fail / fail / pass | fail | 14 of 26 (recall 0.54 [0.36, 0.71]) | 4.42 | fail / fail / pass | fail |
| risk_logistic_base | 13 of 26 (recall 0.50 [0.33, 0.68]) | 1.77 | pass / fail / fail | fail | 15 of 26 (recall 0.58 [0.39, 0.76]) | 2.31 | pass / fail / fail | fail |
| risk_logistic_base+regime_recal | 13 of 26 (recall 0.50 [0.31, 0.68]) | 2.35 | fail / fail / pass | fail | 13 of 26 (recall 0.50 [0.31, 0.68]) | 3.85 | pass / fail / pass | fail |
| risk_quantile_skewt_base | 14 of 26 (recall 0.54 [0.36, 0.71]) | 1.88 | pass / fail / fail | fail | 15 of 26 (recall 0.58 [0.39, 0.75]) | 2.31 | pass / fail / fail | fail |
| risk_quantile_skewt_base+regime_recal | 13 of 26 (recall 0.50 [0.32, 0.69]) | 2.65 | fail / fail / pass | fail | 13 of 26 (recall 0.50 [0.32, 0.69]) | 3.69 | pass / fail / pass | fail |

Every form fails tier 3 under both rules. The recalibrated forms lose tier 1 under the flat rule: the worst horizon's false alarms rise to 2.35 to 2.92 per
onset (limit 2). Under the weighted rule three of the five recalibrated forms keep tier 1 and meet tier 5 (week-ahead), but tier 3 still fails.
No form meets the full pass rule under either rule, so no "Publish?" issue is opened and the published declaration is unchanged.

## What it does not show

* The groups are the five declared calendar regimes; another grouping (the reserve-scarcity state, or a regime that begins at a policy
  date) is a new declaration. #380's group (scarcity band by day type) was not re-run here.
* The remedy was not applied to a risk-date-only target (fit on risk dates, leave ordinary days at 0). That would restore 2021-23 but cannot
  fix the under-forecast in regimes where pressure falls on non-risk days.
* Confirmation (the single look at 2026) is not run and no form is put forward for it.
