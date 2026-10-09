# Can the direct-pairs twin's turning-point gain be had with an ex-ante switch? (#453)

A scratch measurement. It writes nothing into `docs/runs/` and moves no published figure, declaration or live pin. Scored days are 2018-06-29 to 2025-12-31 only (`docs/decisions/lockbox.md`): the panel is cut at 2025-12-31 before any fit and the 2026 tier is not opened. The candidates, the primary test, the Holm rule, the calendar, the turning-point model and its 0.5 threshold were declared in `metadata/turning_point_variant.json`, committed before the scoring script (`scripts/turning_point_variant.py`; evidence in `docs/pivot/evidence/turning_point_variant/`). The pressure candidates were declared in an amendment of the same file, committed after the CRPS scores and before any pressure score.

## Result in one paragraph

**One of the three is better under the declared test: `blend_equal`.** Its paired five-quantile CRPS gain over the published model is +0.023 bp, 90% interval [+0.006, +0.042], and its Holm-adjusted lower bound is +0.0012 bp, above 0. The gain is small (about 1.4% of the published mean CRPS of 1.659 bp) and the lower bound is close to 0. `calendar_switch` (+0.014 bp) and `predicted_turn_switch` (+0.009 bp) are not distinguishable from the published model after the Holm correction. None of the three passes tier 1 of the pressure judge at lead >= 1. Nothing is adopted: because a candidate is better, a `needs-eleonora` "Publish?" issue carries the evidence.

## 1. The primary test (h = 1, all 1873 scored days)

Gain = CRPS(published) − CRPS(candidate) per day, positive favours the candidate; 90% stationary-bootstrap interval (block length 2, 2000 replications, seed 453, all three read off the same resamples); Holm across the three at one-sided alpha 0.05.

| Candidate | Mean CRPS (bp) | Gain over published | Holm rank | One-sided p | Holm-adjusted lower bound | Verdict |
|---|---|---|---|---|---|---|
| `blend_equal` | 1.636 | +0.023 [+0.006, +0.042] | 1 | 0.012 | +0.0012 | **better** |
| `predicted_turn_switch` | 1.650 | +0.009 [-0.000, +0.020] | 2 | 0.064 | -0.0019 | **no difference** |
| `calendar_switch` | 1.645 | +0.014 [-0.005, +0.034] | 3 | 0.102 | -0.0047 | **no difference** |

References: persistence 2.086, published 1.659, twin 1.704 bp. The published walk reproduces `docs/runs/published_distribution_daily_h1.json` on every scored day.

## 2. Gain over the published model, split (bp; 90% interval)

| Cell | Days | blend_equal | calendar_switch | predicted_turn_switch |
|---|---|---|---|---|
| all | 1873 | +0.023 [+0.006, +0.042] | +0.014 [-0.005, +0.034] | +0.009 [-0.000, +0.020] |
| regime: 2018-19 | 375 | +0.042 [-0.020, +0.105] | +0.069 [-0.013, +0.148] | +0.057 [+0.014, +0.108] |
| regime: 2020 | 251 | +0.040 [-0.004, +0.089] | +0.006 [-0.022, +0.033] | -0.003 [-0.016, +0.007] |
| regime: 2021-23 | 748 | -0.024 [-0.038, -0.011] | -0.012 [-0.028, +0.002] | +0.000 [+0.000, +0.000] |
| regime: 2024 | 250 | +0.060 [+0.024, +0.097] | +0.007 [-0.025, +0.039] | -0.007 [-0.021, +0.000] |
| regime: 2025-26 | 249 | +0.084 [+0.021, +0.143] | +0.026 [-0.036, +0.084] | -0.008 [-0.030, +0.011] |
| day_type: month_end | 150 | +0.116 [+0.048, +0.188] | +0.150 [+0.032, +0.277] | +0.075 [+0.003, +0.175] |
| day_type: ordinary | 1603 | +0.008 [-0.010, +0.027] | +0.001 [-0.012, +0.012] | +0.005 [-0.002, +0.012] |
| day_type: quarter_end | 31 | +0.004 [-0.148, +0.156] | -0.132 [-0.436, +0.170] | -0.059 [-0.269, +0.152] |
| day_type: tax_date | 89 | +0.150 [+0.009, +0.271] | +0.079 [-0.182, +0.302] | +0.000 [+0.000, +0.000] |
| outcome: other days | 1733 | +0.016 [+0.001, +0.032] | +0.003 [-0.010, +0.015] | -0.001 [-0.004, +0.002] |
| outcome: pressure day (> +5 bp) | 140 | +0.117 [-0.044, +0.267] | +0.156 [-0.074, +0.390] | +0.135 [+0.001, +0.292] |
| turning-point days | 99 | +0.346 [+0.219, +0.476] | +0.363 [+0.131, +0.600] | +0.158 [+0.017, +0.327] |
| not turning-point days | 1774 | +0.005 [-0.011, +0.022] | -0.005 [-0.022, +0.010] | +0.001 [-0.005, +0.007] |
| month-end days | 188 | +0.067 [+0.004, +0.133] | +0.047 [-0.073, +0.173] | +0.044 [-0.032, +0.139] |
| not month-end days | 1685 | +0.019 [+0.001, +0.037] | +0.011 [-0.007, +0.027] | +0.005 [-0.001, +0.012] |

The intervals of the cells are not Holm-adjusted; only the all-days row is the declared test. `day_type: month_end` and `month-end days` differ: the first is the reporting day-type of `metadata/evaluation_splits.json`, the second the scorecaster's `month_end` indicator.

## 3. Against as-of persistence (CRPS(persistence) − CRPS(model), bp)

A candidate's gain over persistence minus the published model's is exactly its gain over the published model (section 2), so only the levels are given.

| Cell | Days | published | twin | blend_equal | calendar_switch | predicted_turn_switch |
|---|---|---|---|---|---|---|
| all | 1873 | +0.427 [+0.189, +0.749] | +0.382 [+0.137, +0.710] | +0.450 [+0.209, +0.773] | +0.441 [+0.202, +0.758] | +0.436 [+0.197, +0.763] |
| turning-point days | 99 | +0.884 [+0.365, +1.450] | +1.441 [+0.755, +2.201] | +1.230 [+0.652, +1.870] | +1.247 [+0.595, +1.960] | +1.042 [+0.453, +1.728] |
| not turning-point days | 1774 | +0.401 [+0.154, +0.761] | +0.323 [+0.073, +0.681] | +0.407 [+0.156, +0.769] | +0.396 [+0.149, +0.756] | +0.402 [+0.154, +0.763] |
| month-end days | 188 | +0.201 [-0.009, +0.426] | +0.248 [-0.040, +0.558] | +0.268 [+0.029, +0.528] | +0.248 [-0.040, +0.558] | +0.246 [+0.007, +0.503] |
| not month-end days | 1685 | +0.452 [+0.185, +0.832] | +0.397 [+0.126, +0.770] | +0.471 [+0.201, +0.849] | +0.463 [+0.199, +0.836] | +0.457 [+0.189, +0.837] |
| regime: 2018-19 | 375 | +1.649 [+0.507, +3.253] | +1.564 [+0.419, +3.166] | +1.691 [+0.550, +3.303] | +1.718 [+0.587, +3.307] | +1.706 [+0.570, +3.312] |
| regime: 2020 | 251 | +0.072 [-0.181, +0.400] | +0.076 [-0.224, +0.468] | +0.112 [-0.163, +0.471] | +0.078 [-0.179, +0.412] | +0.069 [-0.188, +0.395] |
| regime: 2021-23 | 748 | -0.083 [-0.162, -0.013] | -0.167 [-0.255, -0.090] | -0.107 [-0.189, -0.034] | -0.096 [-0.175, -0.023] | -0.083 [-0.162, -0.013] |
| regime: 2024 | 250 | +0.265 [+0.150, +0.407] | +0.318 [+0.165, +0.503] | +0.324 [+0.191, +0.491] | +0.271 [+0.147, +0.424] | +0.258 [+0.145, +0.400] |
| regime: 2025-26 | 249 | +0.639 [+0.372, +0.916] | +0.626 [+0.280, +0.968] | +0.723 [+0.416, +1.034] | +0.665 [+0.375, +0.959] | +0.631 [+0.364, +0.906] |

## 4. Best lag of the median

The integer k in −3..5 at which the median of day T correlates most with the actual spread of day T−k. The panel is cut at 2025-12-31, so the last three scored days (which would read January 2026 at k = −3) are left out of this statistic.

| Cell | Days | persistence | published | twin | blend_equal | calendar_switch | predicted_turn_switch |
|---|---|---|---|---|---|---|---|
| all | 1870 | 2 | 2 | 2 | 2 | 2 | 2 |
| regime: 2018-19 | 375 | 2 | 2 | 2 | 2 | 2 | 2 |
| regime: 2020 | 251 | 2 | 2 | 2 | 2 | 2 | 2 |
| regime: 2021-23 | 748 | 2 | 2 | 2 | 2 | 2 | 2 |
| regime: 2024 | 250 | 2 | 2 | 2 | 2 | 2 | 2 |
| regime: 2025-26 | 246 | 2 | 2 | 2 | 2 | 2 | 2 |

Every candidate keeps the two-day lag of the published model and of the twin, as #450 found for the twin: no ex-ante switch or blend removes it.

## 5. Band coverage by regime (share of days inside the band)

| Regime | Days | band | published | twin | blend_equal | calendar_switch | predicted_turn_switch |
|---|---|---|---|---|---|---|---|
| all | 1873 | 0.50 | 0.318 | 0.385 | 0.384 | 0.347 | 0.321 |
| all | 1873 | 0.90 | 0.887 | 0.876 | 0.889 | 0.889 | 0.887 |
| regime: 2018-19 | 375 | 0.50 | 0.347 | 0.352 | 0.381 | 0.381 | 0.352 |
| regime: 2018-19 | 375 | 0.90 | 0.861 | 0.843 | 0.859 | 0.859 | 0.859 |
| regime: 2020 | 251 | 0.50 | 0.347 | 0.422 | 0.414 | 0.382 | 0.359 |
| regime: 2020 | 251 | 0.90 | 0.896 | 0.896 | 0.920 | 0.904 | 0.896 |
| regime: 2021-23 | 748 | 0.50 | 0.290 | 0.360 | 0.352 | 0.299 | 0.290 |
| regime: 2021-23 | 748 | 0.90 | 0.910 | 0.894 | 0.904 | 0.905 | 0.910 |
| regime: 2024 | 250 | 0.50 | 0.348 | 0.444 | 0.460 | 0.392 | 0.348 |
| regime: 2024 | 250 | 0.90 | 0.844 | 0.868 | 0.868 | 0.856 | 0.844 |
| regime: 2025-26 | 249 | 0.50 | 0.301 | 0.418 | 0.378 | 0.353 | 0.301 |
| regime: 2025-26 | 249 | 0.90 | 0.892 | 0.859 | 0.880 | 0.904 | 0.896 |

## 6. The switches

| Switch | Days it uses the twin | Hit rate on the actual turning-point days | Precision |
|---|---|---|---|
| `calendar_switch` | 404 of 1873 | 0.586 (58 of 99) | 0.144 |
| `predicted_turn_switch` | 34 of 1873 | 0.141 (14 of 99) | 0.412 |

The turning-point probability model fires on few days at the fixed 0.5 threshold and finds a small share of the turning-point days; the calendar finds more of them but also flags 404 days, most of them not turning points. Neither threshold nor model was changed after a score.

## 7. Pressure days: the judge's tier 1 (lead >= 1, +5 bp)

The three variants are added to the pressure judge as candidates, one file each (`metadata/pressure_judge/candidates/published_v1_<variant>.json`). Each is an h = 1 object: at h = 1 its probability is built from `published_v1` and `published_v1_direct` (the same classifier trained on direct pairs) as declared in the amendment, and at h = 2 to 5 it is `published_v1`'s probability exactly. `blend_equal` here is the average of the two calibrated probabilities, not of the quantile vectors, because the law and the Platt step come after the quantiles. The judge is run as declared, over the days to 2025-12-31, with no confirmation look (`docs/pivot/evidence/turning_point_variant/judge.md`).

| Candidate | Episodes (onsets) | Warned at lead >= 1 | Recall [90%] | Worst false alarms per episode | Tier 1 |
|---|---|---|---|---|---|
| `published_v1` | 26 | 2 | 0.077 [0.000, 0.185] | 2.35 | no |
| `published_v1_blend_equal` | 26 | 3 | 0.115 [0.000, 0.250] | 2.27 | no |
| `published_v1_calendar_switch` | 26 | 8 | 0.308 [0.152, 0.464] | 2.92 | no |
| `published_v1_predicted_turn_switch` | 26 | 5 | 0.192 [0.071, 0.333] | 2.88 | no |

No variant passes tier 1 (recall at least 0.5 with at most 2 false alarms per episode). `published_v1_calendar_switch` warns the most episodes (8 of 26) but at 2.9 false alarms per episode, above the limit.

## What this does not show

* The CRPS gain of `blend_equal` is small and its Holm-adjusted lower bound is close to 0; the 2026 tier is not opened, so there is no held-out confirmation. It is a development-window result chosen from three declared candidates.
* `blend_equal` is worse than the published model in regime 2021–23 and does not help on ordinary days; its gain comes from month-ends, turning-point days and 2024–25.
* The turning-point probability model has no tuning at all (fixed features, C = 1, threshold 0.5); a different declared threshold or feature set is a different candidate and would need its own declaration.
* The pressure variants differ from `published_v1` at h = 1 only, and `blend_equal` there is a probability average, so the pressure table is not a test of the CRPS blend itself.
