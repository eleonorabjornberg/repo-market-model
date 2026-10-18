# H5 step 3: the scored results that informed H5 steps 2 to 4, without decision day 2019-09-18 (#882)

Hypothesis and step: **H5** (primary goal), development step 3 of `docs/research/hypotheses/H5.md` ("diagnose the known weaknesses"), on finding #798. **Development data, not a verdict** (scoring protocol v1, #640; #46 top block). A sensitivity table: nothing is re-ruled, no declaration or published page is edited, no candidate is registered, no new variant is run, and no published figure moves. No day after 2025-12-31 is read and no locked day is scored (`docs/decisions/lockbox.md`).

On decision day 2019-09-18 B1's anchor is +315 bp (the day's anchor, 2019-09-17, is a tax date by the declared split), and B1's grid CRPS that day is 297.6 bp (#805). #805 removed the day for #634's and #707's walks. This page does it for the three other scored results that fed H5 steps 2 to 4, each with its **original script, panel digest and seed**:

| result | script | scored by |
|---|---|---|
| #775 / #758: `gbm_funding`, the H2 ceiling, the reachable line, the headroom | `scripts/h5_step4_758.py` (walks of `scripts/spread_distribution_634.py`, fits of `scripts/upper_bound_635.py`) | `docs/pivot/h5-step4-result.md` |
| #815 / #767 (scored in #761): mean reversion and the `spread_mr_ctx` variants, upper-tail twCRPS included | `scripts/spread_mr_variants_761.py` | `docs/pivot/spread-mr-variants-result.md` |
| #822 / #688: the window flag and bill settlement, each against the control | `scripts/near_threshold_688.py` | `docs/pivot/near-threshold-688-result.md` |

Each script gained one option, `score --without-day YYYY-MM-DD`, which leaves that one decision day out of every window and changes nothing else; without it a script's output is what it was (tested in `tests/test_without_day_882.py`). `scripts/without_day_882.py` lines the two score files up and compares the "with" run with the tracked file. Everything below is in `docs/pivot/evidence/without-day-882/` (`comparison-*.json`, every record; `report.md`, every record as a table).

## The "with" column reproduces the tracked figures, except the H2 ceiling

Published panel `4ddc3882…` (`build` and `verify-panel` clean, byte-identical after the merge of main). `/opt/rmm-venv`, one thread per process. The studentized stationary bootstrap and the seeds are the scripts' own.

* **#761 and #688 reproduce.** Every record of the "with" run equals the tracked score file: the largest difference is 5e-15 (#761, the sum order of the bootstrap) and 0 (#688).
* **#758: the candidates reproduce, the H2 lines do not.** The records of `gbm_funding` and `c_two_part_new` (the walks of #634, rerun) equal the tracked ones exactly. The records that involve "ceiling gbm" or "reachable gbm" differ by up to 0.056 in skill or bound. The scratch panel `DERIV.csv` of H2 (`docs/pivot/upper-bound-result.md`) could not be rebuilt byte for byte: the chain of `derived-features-result.md` (Reproduce) gives digest `400372d6…` here, `92bf10a4…` in the #758 rerun and `08df8d19…` in H2's record. The #758 reproduction check (tolerance 0.01 on the pooled skills of the two lines) passes (reachable +0.193, ceiling +0.160 against recorded +0.192 and +0.162). So the "with the day" and "without the day" columns of the ceiling and reachable rows are this session's fits, compared with each other; they are not the tracked page's. **The declared reading of #758 does not reproduce either:** the tracked page shows headroom in regime 2024 (+0.110 [+0.027, +0.160]); this rerun gives +0.087 [-0.021, +0.146] with or without the day, so it reads "stop at the best available candidate" (nowhere shown). This is a marked question below, and it does not depend on 2019-09-18.

## #775 / #758: the candidate, the H2 lines and the headroom

**Pooled, ordinary targets, grid CRPS: skill against B1 (points of skill, 90% interval)**

| row | days (without) | with the day | without the day | a bound changes sign |
|---|---|---|---|---|
| gbm_funding | 1598 (1597) | +0.257 [+0.114, +0.400] | +0.169 [+0.106, +0.229] |  |
| c_two_part_new | 1598 (1597) | +0.224 [+0.052, +0.380] | +0.132 [+0.037, +0.213] |  |
| reachable gbm | 1598 (1597) | +0.193 [+0.015, +0.352] | +0.097 [-0.008, +0.186] | **yes** |
| ceiling gbm | 1598 (1597) | +0.160 [-0.006, +0.310] | +0.061 [-0.035, +0.147] |  |

**Headroom of the H2 line over the candidate (positive: the line is ahead)**

| row | days (without) | with the day | without the day | a bound changes sign |
|---|---|---|---|---|
| gbm_funding vs ceiling gbm | 1598 (1597) | -0.097 [-0.170, -0.026] | -0.107 [-0.189, -0.027] |  |
| gbm_funding vs reachable gbm | 1598 (1597) | -0.064 [-0.123, -0.015] | -0.071 [-0.133, -0.017] |  |
| c_two_part_new vs ceiling gbm | 1598 (1597) | -0.064 [-0.132, +0.012] | -0.071 [-0.150, +0.014] |  |
| c_two_part_new vs reachable gbm | 1598 (1597) | -0.031 [-0.079, +0.019] | -0.035 [-0.088, +0.020] |  |

**Pooled, ordinary targets, upper-tail twCRPS: skill against B1 and headroom**

| row | days (without) | with the day | without the day | a bound changes sign |
|---|---|---|---|---|
| gbm_funding | 1598 (1597) | +0.516 [+0.291, +0.665] | +0.368 [+0.282, +0.450] |  |
| c_two_part_new | 1598 (1597) | +0.559 [+0.347, +0.698] | +0.425 [+0.329, +0.515] |  |
| reachable gbm | 1598 (1597) | +0.486 [+0.236, +0.643] | +0.329 [+0.211, +0.422] |  |
| ceiling gbm | 1598 (1597) | +0.453 [+0.224, +0.608] | +0.289 [+0.172, +0.414] |  |
| headroom gbm_funding vs ceiling gbm | 1598 (1597) | -0.063 [-0.128, +0.024] | -0.078 [-0.175, +0.029] |  |
| headroom c_two_part_new vs ceiling gbm | 1598 (1597) | -0.105 [-0.161, -0.040] | -0.136 [-0.220, -0.040] |  |

**`gbm_funding` by regime (ordinary targets), skill against B1, and headroom of the ceiling over it**

| row | days (without) | with the day | without the day | a bound changes sign |
|---|---|---|---|---|
| 2018-19: skill | 101 (100) | +0.660 [+0.240, +0.799] | +0.401 [+0.224, +0.513] |  |
| 2020: skill | 251 (251) | +0.148 [+0.033, +0.258] | +0.148 [+0.033, +0.258] |  |
| 2021-23: skill | 751 (751) | -0.007 [-0.129, +0.109] | -0.007 [-0.129, +0.109] |  |
| 2024: skill | 250 (250) | +0.162 [+0.100, +0.225] | +0.162 [+0.100, +0.225] |  |
| 2025-26: skill | 249 (249) | +0.186 [+0.099, +0.265] | +0.186 [+0.099, +0.265] |  |
| 2018-19: headroom (ceiling) | 101 (100) | -0.127 [-0.281, +0.030] | -0.216 [-0.385, +0.042] |  |
| 2020: headroom (ceiling) | 251 (251) | +0.033 [-0.060, +0.104] | +0.033 [-0.060, +0.104] |  |
| 2021-23: headroom (ceiling) | 751 (751) | -0.253 [-0.466, -0.075] | -0.253 [-0.466, -0.075] |  |
| 2024: headroom (ceiling) | 250 (250) | +0.087 [-0.021, +0.146] | +0.087 [-0.021, +0.146] |  |
| 2025-26: headroom (ceiling) | 249 (249) | -0.121 [-0.270, +0.025] | -0.121 [-0.270, +0.025] |  |

**Reading.** Without the day the candidates stay ahead of B1 on ordinary targets with intervals above zero, by about 9 points less (`gbm_funding` +0.257 to +0.169; (c) +0.224 to +0.132); the upper-tail figure falls by about 15 points. The headroom of the H2 lines over the candidate does not change sign in any pooled cell, and in none of the five regimes: the day sits in regime 2018-19, the only regime where any figure moves (candidate skill +0.660 to +0.401; headroom -0.127 to -0.216). The pooled skill of the *reachable* line against B1 loses its resolved lower bound without the day (+0.193 [+0.015, +0.352] to +0.097 [-0.008, +0.186]); the ceiling line's pooled ordinary-day interval already covered zero, and its other intervals that exclude zero with the day (all targets, ordinary day type, regime 2018-19) cover it without. One bound moves the other way by 0.003 (the ceiling against B2 in the upper tail, lower bound -0.001 to +0.002). Records in which a bound changes sign:

| record | days (without) | with the day | without the day | a bound changes sign |
|---|---|---|---|---|
| crps/day type: ordinary/tests/B1 -> ceiling gbm | 1598 (1597) | +0.167 [+0.004, +0.308] | +0.070 [-0.024, +0.154] | **yes** |
| crps/day type: ordinary/tests/B1 -> reachable gbm | 1598 (1597) | +0.197 [+0.021, +0.348] | +0.103 [-0.001, +0.190] | **yes** |
| crps/pooled, all targets/tests/B1 -> ceiling gbm | 1598 (1597) | +0.149 [+0.011, +0.262] | +0.066 [-0.014, +0.142] | **yes** |
| crps/pooled, ordinary targets/tests/B1 -> reachable gbm | 1598 (1597) | +0.193 [+0.015, +0.352] | +0.097 [-0.008, +0.186] | **yes** |
| crps/regime: 2018-19/tests/B1 -> ceiling gbm | 101 (100) | +0.533 [+0.045, +0.709] | +0.185 [-0.039, +0.401] | **yes** |
| twcrps/pooled, ordinary targets/tests/B2 -> ceiling gbm | 1598 (1597) | +0.170 [-0.001, +0.342] | +0.172 [+0.002, +0.353] | **yes** |

## #815 / #767 (scored in #761): mean reversion and the context variants

Decision days 1,855 with the day, 1,854 without. Variants: the level-10 mean reversion of #686 (`spread_mr_level10`), the B2 average (`spread_mr_b2`), context-pooled residuals (`spread_mr_ctx`) and both (`spread_mr_ctx_b2`).

**Grid CRPS, all decision days: skill against B1**

| row | days (without) | with the day | without the day | a bound changes sign |
|---|---|---|---|---|
| spread_mr_level10 | 1855 (1854) | +0.223 [+0.275, +1.473] | +0.172 [+0.237, +0.617] |  |
| spread_mr_b2 | 1855 (1854) | +0.222 [+0.258, +1.387] | +0.170 [+0.220, +0.608] |  |
| spread_mr_ctx | 1855 (1854) | +0.235 [+0.287, +1.507] | +0.186 [+0.251, +0.653] |  |
| spread_mr_ctx_b2 | 1855 (1854) | +0.232 [+0.266, +1.425] | +0.180 [+0.232, +0.639] |  |

**Grid CRPS, all decision days: skill against B2**

| row | days (without) | with the day | without the day | a bound changes sign |
|---|---|---|---|---|
| spread_mr_level10 | 1855 (1854) | +0.294 [+0.502, +1.036] | +0.300 [+0.521, +1.051] |  |
| spread_mr_b2 | 1855 (1854) | +0.293 [+0.532, +0.998] | +0.297 [+0.545, +1.008] |  |
| spread_mr_ctx | 1855 (1854) | +0.305 [+0.531, +1.062] | +0.311 [+0.551, +1.078] |  |
| spread_mr_ctx_b2 | 1855 (1854) | +0.302 [+0.555, +1.019] | +0.306 [+0.566, +1.027] |  |

**Upper-tail twCRPS, all decision days: skill against B1**

| row | days (without) | with the day | without the day | a bound changes sign |
|---|---|---|---|---|
| spread_mr_level10 | 1855 (1854) | +0.324 [+0.214, +1.520] | +0.249 [+0.179, +0.578] |  |
| spread_mr_b2 | 1855 (1854) | +0.322 [+0.201, +1.478] | +0.243 [+0.166, +0.567] |  |
| spread_mr_ctx | 1855 (1854) | +0.340 [+0.222, +1.545] | +0.267 [+0.187, +0.610] |  |
| spread_mr_ctx_b2 | 1855 (1854) | +0.335 [+0.206, +1.509] | +0.258 [+0.172, +0.593] |  |

**Upper-tail twCRPS, all decision days: skill against B2**

| row | days (without) | with the day | without the day | a bound changes sign |
|---|---|---|---|---|
| spread_mr_level10 | 1855 (1854) | +0.178 [+0.091, +0.350] | +0.191 [+0.110, +0.367] |  |
| spread_mr_b2 | 1855 (1854) | +0.176 [+0.107, +0.321] | +0.185 [+0.120, +0.332] |  |
| spread_mr_ctx | 1855 (1854) | +0.198 [+0.116, +0.376] | +0.210 [+0.132, +0.394] |  |
| spread_mr_ctx_b2 | 1855 (1854) | +0.191 [+0.123, +0.345] | +0.200 [+0.134, +0.357] |  |

**Grid CRPS by regime, skill of `spread_mr_ctx_b2` against B1**

| row | days (without) | with the day | without the day | a bound changes sign |
|---|---|---|---|---|
| 2018-19 | 361 (361) | +0.368 [+0.925, +8.417] | +0.279 [+0.826, +2.798] |  |
| 2020 | 251 (251) | -0.021 [-0.226, +0.203] | -0.021 [-0.226, +0.203] |  |
| 2021-23 | 748 (748) | -0.038 [-0.067, +0.012] | -0.038 [-0.067, +0.012] |  |
| 2024 | 250 (250) | +0.250 [+0.202, +0.852] | +0.250 [+0.202, +0.852] |  |
| 2025-26 | 249 (249) | +0.170 [+0.065, +1.094] | +0.170 [+0.065, +1.094] |  |

**Reading.** Against B1 every pooled skill falls without the day (for example `spread_mr_ctx_b2`, grid CRPS +0.232 to +0.180, upper-tail twCRPS +0.335 to +0.258) and the upper bounds, inflated by the day, fall by half or more; every pooled interval stays above zero. Against B2 the figures do not move (+0.302 to +0.306). The records in which a bound changes sign (twelve of 421) are all in groups that hold the day's cells: the tax-date-anchor group (where the day's weight made the intervals against B1 run to +100 and more; without it they close to a few units and exclude zero), the context "ordinary after a risk day" and regime 2018-19. They move in both directions:

| record | days (without) | with the day | without the day | a bound changes sign |
|---|---|---|---|---|
| anchor_day_type/tax_date/grid_crps/vs/B1_recentred/B1 | 89 (88) | +0.744 [-0.261, +101.363] | +0.386 [+0.254, +2.859] | **yes** |
| anchor_day_type/tax_date/grid_crps/vs/spread_mr_b2/B1 | 89 (88) | +0.703 [-0.217, +92.685] | +0.387 [+0.182, +3.086] | **yes** |
| anchor_day_type/tax_date/grid_crps/vs/spread_mr_b2/spread_mr_level10 | 89 (88) | +0.086 [+0.037, +0.418] | +0.052 [-0.063, +0.344] | **yes** |
| anchor_day_type/tax_date/grid_crps/vs/spread_mr_ctx/B1 | 89 (88) | +0.672 [-0.380, +124.640] | +0.346 [+0.073, +4.365] | **yes** |
| anchor_day_type/tax_date/grid_crps/vs/spread_mr_ctx_b2/B1 | 89 (88) | +0.705 [-0.230, +91.759] | +0.391 [+0.167, +3.255] | **yes** |
| anchor_day_type/tax_date/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10 | 89 (88) | +0.090 [+0.037, +0.474] | +0.059 [-0.036, +0.359] | **yes** |
| anchor_day_type/tax_date/grid_crps/vs/spread_mr_level10/B1 | 89 (88) | +0.675 [-0.346, +121.789] | +0.353 [+0.111, +4.048] | **yes** |
| context/ordinary after a risk day/grid_crps/vs/spread_mr_b2/spread_mr_level10 | 200 (200) | -0.043 [-0.380, +0.002] | -0.054 [-0.435, -0.015] | **yes** |
| context/ordinary after a risk day/grid_crps/vs/spread_mr_ctx/B1 | 200 (200) | +0.116 [+0.009, +1.814] | +0.033 [-0.020, +0.181] | **yes** |
| context/ordinary after a risk day/upper_tail_twcrps/vs/B1_recentred/B1 | 200 (200) | +0.227 [-0.009, +6.980] | +0.054 [+0.012, +0.189] | **yes** |
| context/ordinary after a risk day/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10 | 200 (200) | -0.025 [-0.075, -0.000] | -0.025 [-0.070, +0.000] | **yes** |
| regime/2018-19/upper_tail_twcrps/vs/spread_mr_level10/B2 | 361 (361) | +0.095 [-0.036, +0.840] | +0.114 [+0.081, +0.903] | **yes** |

## #822 / #688: the window flag and bill settlement against the control

Decision days 1,868 with the day, 1,867 without.

**Grid CRPS, pooled: skill (against B1, B2) or difference from the control**

| row | days (without) | with the day | without the day | a bound changes sign |
|---|---|---|---|---|
| B1 vs control | 1868 (1867) | +0.193 [+0.105, +0.391] | +0.134 [+0.076, +0.205] |  |
| B1 vs bill_x_band | 1868 (1867) | +0.192 [+0.105, +0.388] | +0.133 [+0.075, +0.205] |  |
| B1 vs post_month_end_window | 1868 (1867) | +0.201 [+0.116, +0.393] | +0.143 [+0.085, +0.214] |  |
| control vs bill_x_band | 1868 (1867) | -0.001 [-0.005, +0.003] | -0.001 [-0.005, +0.003] |  |
| control vs post_month_end_window | 1868 (1867) | +0.010 [+0.004, +0.016] | +0.010 [+0.004, +0.016] |  |

**Upper-tail twCRPS, pooled: skill (against B1, B2) or difference from the control**

| row | days (without) | with the day | without the day | a bound changes sign |
|---|---|---|---|---|
| B1 vs control | 1868 (1867) | +0.338 [+0.246, +0.519] | +0.254 [+0.163, +0.354] |  |
| B1 vs bill_x_band | 1868 (1867) | +0.339 [+0.249, +0.516] | +0.256 [+0.163, +0.356] |  |
| B1 vs post_month_end_window | 1868 (1867) | +0.341 [+0.251, +0.521] | +0.257 [+0.165, +0.357] |  |
| control vs bill_x_band | 1868 (1867) | +0.003 [-0.004, +0.009] | +0.003 [-0.004, +0.010] |  |
| control vs post_month_end_window | 1868 (1867) | +0.004 [-0.004, +0.012] | +0.004 [-0.003, +0.012] |  |

**Grid CRPS by regime: `bill_x_band` against the control**

| row | days (without) | with the day | without the day | a bound changes sign |
|---|---|---|---|---|
| 2018-19 | 375 (374) | -0.001 [-0.005, +0.005] | -0.000 [-0.005, +0.005] |  |
| 2020 | 251 (251) | -0.003 [-0.014, +0.018] | -0.003 [-0.014, +0.018] |  |
| 2021-23 | 748 (748) | -0.002 [-0.008, +0.004] | -0.002 [-0.008, +0.004] |  |
| 2024 | 250 (250) | +0.012 [+0.006, +0.019] | +0.012 [+0.006, +0.019] |  |
| 2025-26 | 244 (244) | -0.008 [-0.029, +0.006] | -0.008 [-0.029, +0.006] |  |

**Grid CRPS by regime: `post_month_end_window` against the control**

| row | days (without) | with the day | without the day | a bound changes sign |
|---|---|---|---|---|
| 2018-19 | 375 (374) | +0.006 [-0.003, +0.016] | +0.006 [-0.003, +0.016] |  |
| 2020 | 251 (251) | +0.004 [-0.020, +0.028] | +0.004 [-0.020, +0.028] |  |
| 2021-23 | 748 (748) | +0.025 [+0.014, +0.037] | +0.025 [+0.014, +0.037] |  |
| 2024 | 250 (250) | +0.013 [-0.017, +0.033] | +0.013 [-0.017, +0.033] |  |
| 2025-26 | 244 (244) | +0.007 [-0.001, +0.018] | +0.007 [-0.001, +0.018] |  |

**Grid CRPS by regime: the control against B1**

| row | days (without) | with the day | without the day | a bound changes sign |
|---|---|---|---|---|
| 2018-19 | 375 (374) | +0.323 [+0.206, +0.596] | +0.217 [+0.124, +0.350] |  |
| 2020 | 251 (251) | +0.066 [-0.171, +0.207] | +0.066 [-0.171, +0.207] |  |
| 2021-23 | 748 (748) | -0.268 [-0.490, -0.123] | -0.268 [-0.490, -0.123] |  |
| 2024 | 250 (250) | +0.157 [+0.088, +0.248] | +0.157 [+0.088, +0.248] |  |
| 2025-26 | 244 (244) | +0.234 [+0.173, +0.328] | +0.234 [+0.173, +0.328] |  |

**Reading.** The control's skill against B1 falls without the day (grid CRPS +0.193 to +0.134; upper-tail +0.338 to +0.254; regime 2018-19 +0.323 to +0.217), and the intervals stay above zero. The two variants' differences from the control do not move in any pooled or regime cell, and no bound changes sign in any record of this page. The window flag's gain over the control (+0.010 [+0.004, +0.016] pooled, +0.025 in 2021-23) is the same with and without the day.

## Marked questions for Eleonora (nothing decided here)

1. **The H2 ceiling cannot be rebuilt.** `DERIV.csv` has now given three digests (`08df8d19…` recorded, `92bf10a4…` in #758, `400372d6…` here), and the pooled skills of the two lines move by up to 0.008 and the 2024 headroom cell by 0.023, with a lower bound that crosses zero, which flips #758's declared reading from "continue model work in 2024" to "stop". Is that a finding to be worked as a directive (the chain that builds `DERIV.csv`), and does the #758 reading stand meanwhile? This PR neither answers nor changes it.
2. **What the day means for the reachable line.** Without the day, the reachable line's pooled ordinary-day skill against B1 no longer excludes zero (the ceiling's never did). H2's kill criterion reads "spread CRPS skill against persistence covers 0". The sign change is reported here and decided nowhere; whether it bears on H2's reading is hers.
3. **Nothing here reads on B1, the MME or the calibrated critical values.** They are untouched; the day's weight on B1's denominator (6.9%, #805) is why every skill against B1 falls and every skill against B2 does not.

## Reproduce

`/opt/rmm-venv` (numpy 2.4.6, scikit-learn 1.9.1), `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`. The walks (25, 15 to 40 minutes each) and the fits of H2 (about 5 hours on two cores) are the original scripts' commands (their docstrings); the scratch panels are built as in `scripts/spread_distribution_634.py` (`AUG2D`) and `docs/pivot/derived-features-result.md` (`DERIV`, as `scripts/h5_step4_758.py` says). Then, for each of the three scripts, once as published and once with `--without-day 2019-09-18`:

```
PYTHONPATH=src python3 scripts/h5_step4_758.py score --published PUBLISHED.csv --fits OUT/fits.json --walks OUT634 --tolerance 0.01 [--without-day 2019-09-18] --output o758/score.json
PYTHONPATH=src python3 scripts/spread_mr_variants_761.py score --panel PUBLISHED.csv [--without-day 2019-09-18] --output o761/score.json
PYTHONPATH=src python3 scripts/near_threshold_688.py score --published PUBLISHED.csv --walks OUT688 [--without-day 2019-09-18] --output o688/score.json
PYTHONPATH=src python3 scripts/without_day_882.py compare --name 758 --words ceiling reachable --tracked docs/pivot/evidence/h5-step4/score.json --with o758/score.json --without o758w/score.json --output comparison-758.json
PYTHONPATH=src python3 scripts/without_day_882.py report --comparison comparison-758.json comparison-761.json comparison-688.json --output report.md
```
