# Calendar and FOMC terms on the scaled mean reversion (#1115), read on the mean-d bound (#1167; H5 reporting, for #1009)

**Development data, not a verdict.** No re-scoring, no lockbox day, and no published declaration, record or decided value moves. Every figure is read from `docs/research/calendar-mr-1115/result.json`, the record of the original page (`calendar-mr-1115-result.md`, which stands), by `scripts/mean_d_reading_1167.py report`. Seed 1115, 10,000 draws, as on the original page.

## What changes and why

The original page read each row from the studentized skill interval. The skill interval and the interval on the mean difference d are built from different studentized draws, so their ends can fall on different sides of zero (#1009). The protocol's verdict reads the one-sided studentized bound on mean d (ruling 1/5). By Eleonora's ruling on #1009 this page shows both intervals for every paired row and reads the mean-d bound: **gain** when the lower bound of mean d is above zero, **loss** when its upper bound is below zero, **undecided** otherwise. The 90% two-sided interval on mean d is the pair of one-sided 95% bounds. d = S(benchmark) − S(candidate), positive favouring the candidate; skill is mean(d) / mean(S(benchmark)). A row the scorer left undefined carries no interval and is not read here.

**Caveat (Lens C of the five-lens review, #958).** The lag-10 HAC standard error that studentizes the mean-d bound is understated about 2× after 2020 (about 2.3× in 2021–23, 1.7× in 2024–26), and the bootstrap block of 10 days is an order of magnitude shorter than the autocorrelation of d. The bound is therefore optimistic: an interval that excludes zero here is narrower than it should be after 2020. A development reading on this page is evidence for a question, not a verdict.

Paired rows read: 1190. Rows whose reading changes: 131.

| reading on the skill interval -> reading on the mean-d bound | rows |
|---|---|
| gain -> undecided | 21 |
| loss -> undecided | 1 |
| undecided -> gain | 38 |
| undecided -> loss | 71 |

## Readings that change

| section | group | comparison | skill [90%] | mean d [90%] | on the skill interval | on the mean-d bound |
|---|---|---|---|---|---|---|
| upper_tail_twcrps, by lead | h=1 | mr_cal_a_base against B1_prime | +14.4% [-3.2, +26.9] | +0.1481 [+0.04625, +0.3098] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | mr_cal_a_base against B2 | +21.0% [-2.9, +36.7] | +0.2341 [+0.09195, +0.395] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | mr_cal_b_location against B1 | +18.6% [+0.6, +37.8] | +0.2393 [-0.01747, +0.8622] | gain | **undecided** |
| upper_tail_twcrps, by lead | h=1 | mr_cal_c_location_scale against B2 | +13.5% [-4.4, +27.4] | +0.1498 [+0.005711, +0.3136] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | mr_cal_c_location_scale against mr_cal_a_base | -9.6% [-26.5, +1.1] | -0.08439 [-0.1828, -0.007579] | undecided | **loss** |
| upper_tail_twcrps, by lead | h=1 | mr_cal_c_location_scale against spread_mr_ctx | -10.3% [-25.7, +0.7] | -0.08972 [-0.1708, -0.01966] | undecided | **loss** |
| upper_tail_twcrps, by lead | h=1 | mr_cal_d_no_fomc_iorb against B2 | +16.7% [-4.1, +31.2] | +0.1861 [+0.04383, +0.3514] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=2 | mr_cal_a_base against gbm_funding | +4.7% [-0.5, +8.8] | +0.04404 [+0.002715, +0.09105] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=2 | mr_cal_c_location_scale against mr_cal_a_base | -10.6% [-29.3, +1.4] | -0.09424 [-0.1994, -0.008592] | undecided | **loss** |
| grid_crps, by lead | h=3 | mr_cal_c_location_scale against spread_mr_ctx | -5.7% [-13.6, +0.3] | -0.1021 [-0.2184, -0.0003856] | undecided | **loss** |
| grid_crps, by lead | h=4 | mr_cal_d_no_fomc_iorb against mr_cal_a_base | -5.4% [-12.7, +0.0] | -0.09411 [-0.2083, -3.668e-05] | undecided | **loss** |
| upper_tail_twcrps, by lead | h=4 | mr_cal_c_location_scale against mr_cal_a_base | -10.2% [-26.2, +0.2] | -0.09181 [-0.1906, -0.01065] | undecided | **loss** |
| upper_tail_twcrps, by lead | h=4 | mr_cal_d_no_fomc_iorb against B1_prime | +12.1% [+0.8, +24.3] | +0.1322 [-0.002876, +0.3308] | gain | **undecided** |
| upper_tail_twcrps, by lead | h=5 | mr_cal_d_no_fomc_iorb against B1_prime | +11.2% [+0.0, +24.0] | +0.124 [-0.009331, +0.3265] | gain | **undecided** |
| upper_tail_twcrps, by all decision days | all decision days | mr_cal_c_location_scale against mr_cal_a_base | -10.3% [-27.2, +0.4] | -0.09261 [-0.1953, -0.0124] | undecided | **loss** |
| upper_tail_twcrps, by all decision days | all decision days | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | -3.3% [-7.8, +0.5] | -0.03154 [-0.06304, -0.005401] | undecided | **loss** |
| upper_tail_twcrps, by all decision days | all decision days | mr_cal_c_location_scale against spread_mr_ctx | -8.9% [-23.8, +1.5] | -0.08099 [-0.1706, -0.001595] | undecided | **loss** |
| grid_crps, by regime | 2018-19 | mr_cal_d_no_fomc_iorb against B1_prime | +12.4% [-2.5, +29.2] | +0.5338 [+0.027, +1.385] | undecided | **gain** |
| grid_crps, by regime | 2018-19 | mr_cal_d_no_fomc_iorb against B2 | +15.2% [-0.1, +29.5] | +0.6802 [+0.1842, +1.276] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2018-19 | mr_cal_a_base against B1_prime | +11.5% [-0.5, +30.8] | +0.4411 [+0.07829, +1.368] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2018-19 | mr_cal_a_base against B2 | +11.0% [-1.3, +24.5] | +0.419 [+0.03364, +0.89] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2018-19 | mr_cal_c_location_scale against B2 | +12.9% [-0.5, +25.2] | +0.4905 [+0.06005, +0.9824] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2018-19 | mr_cal_d_no_fomc_iorb against B1_prime | +14.5% [-3.8, +33.2] | +0.5569 [+0.04943, +1.426] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2018-19 | mr_cal_d_no_fomc_iorb against B2 | +14.0% [-1.8, +28.3] | +0.5348 [+0.1396, +1.031] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2018-19 | mr_cal_d_no_fomc_iorb against gbm_funding | +10.0% [-2.6, +19.9] | +0.3645 [+0.009498, +0.7606] | undecided | **gain** |
| grid_crps, by regime | 2020 | mr_cal_b_location against B1 | -62.4% [-130.0, +11.6] | -1.028 [-1.627, -0.4779] | undecided | **loss** |
| grid_crps, by regime | 2020 | mr_cal_b_location against B1_prime | -66.3% [-145.5, +25.8] | -1.067 [-1.684, -0.4617] | undecided | **loss** |
| grid_crps, by regime | 2020 | mr_cal_c_location_scale against B1 | -42.2% [-94.6, +21.7] | -0.6955 [-1.156, -0.1701] | undecided | **loss** |
| grid_crps, by regime | 2020 | mr_cal_c_location_scale against B1_prime | -45.6% [-107.2, +35.9] | -0.7342 [-1.214, -0.1341] | undecided | **loss** |
| grid_crps, by regime | 2020 | mr_cal_c_location_scale against gbm_funding | -66.6% [-140.7, +0.4] | -0.9368 [-1.394, -0.5305] | undecided | **loss** |
| grid_crps, by regime | 2020 | mr_cal_c_location_scale against gbm_funding_cal_aligned | -61.4% [-136.2, +5.2] | -0.8914 [-1.366, -0.4814] | undecided | **loss** |
| grid_crps, by regime | 2020 | mr_cal_d_no_fomc_iorb against B1 | -30.4% [-70.9, +14.8] | -0.5003 [-0.9006, -0.07623] | undecided | **loss** |
| grid_crps, by regime | 2020 | mr_cal_d_no_fomc_iorb against B1_prime | -33.5% [-81.9, +24.6] | -0.539 [-0.962, -0.04678] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2020 | mr_cal_a_base against B2 | +58.1% [-24.5, +84.2] | +0.7083 [+0.3634, +1.13] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | mr_cal_a_base against spread_mr_ctx | +22.9% [-19.4, +50.4] | +0.1521 [+0.08778, +0.2191] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | mr_cal_b_location against B1 | -102.9% [-359.8, +118.8] | -0.7617 [-1.378, -0.22] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2020 | mr_cal_b_location against B1_prime | -99.7% [-373.3, +139.1] | -0.7498 [-1.383, -0.1575] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2020 | mr_cal_b_location against gbm_funding | -245.2% [-872.6, +159.1] | -1.067 [-1.697, -0.6729] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2020 | mr_cal_b_location against gbm_funding_cal_aligned | -213.7% [-711.7, +142.7] | -1.023 [-1.669, -0.6354] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2020 | mr_cal_b_location against mr_cal_a_base | -194.0% [-564.1, +82.3] | -0.991 [-1.635, -0.6232] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2020 | mr_cal_b_location against spread_mr_ctx | -126.5% [-303.0, +30.5] | -0.8389 [-1.442, -0.4984] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2020 | mr_cal_c_location_scale against gbm_funding | -188.4% [-678.8, +152.9] | -0.8195 [-1.259, -0.478] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2020 | mr_cal_c_location_scale against gbm_funding_cal_aligned | -162.0% [-543.7, +146.4] | -0.7757 [-1.22, -0.4458] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2020 | mr_cal_c_location_scale against mr_cal_a_base | -145.6% [-426.2, +90.9] | -0.7437 [-1.181, -0.4421] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2020 | mr_cal_c_location_scale against spread_mr_ctx | -89.2% [-217.2, +45.4] | -0.5916 [-0.9848, -0.3197] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2020 | mr_cal_d_no_fomc_iorb against gbm_funding | -160.0% [-555.4, +98.6] | -0.6958 [-1.058, -0.4376] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2020 | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | -136.2% [-445.2, +91.5] | -0.6521 [-1.014, -0.4073] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2020 | mr_cal_d_no_fomc_iorb against mr_cal_a_base | -121.4% [-345.3, +38.8] | -0.62 [-0.986, -0.3846] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2020 | mr_cal_d_no_fomc_iorb against spread_mr_ctx | -70.6% [-169.7, +10.3] | -0.468 [-0.7956, -0.2536] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2021-23 | mr_cal_a_base against B2 | -156.2% [-785.5, -33.6] | -0.004779 [-0.04788, +0.0004231] | loss | **undecided** |
| upper_tail_twcrps, by regime | 2021-23 | mr_cal_a_base against spread_mr_ctx | +54.4% [-42.2, +86.2] | +0.009339 [+0.004547, +0.01604] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | mr_cal_b_location against gbm_funding_cal_aligned | -3208.8% [-13202.3, +667.4] | -0.0705 [-0.2282, -0.02548] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2021-23 | mr_cal_c_location_scale against gbm_funding_cal_aligned | -2730.3% [-9405.5, +568.8] | -0.05998 [-0.1484, -0.02626] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2021-23 | mr_cal_d_no_fomc_iorb against B1 | -441.0% [-1668.3, +2.1] | -0.03942 [-0.1155, -0.01168] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2021-23 | mr_cal_d_no_fomc_iorb against B1_prime | -618.7% [-2492.6, +37.2] | -0.04163 [-0.1185, -0.01369] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2021-23 | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | -2101.2% [-8450.2, +386.5] | -0.04616 [-0.1214, -0.01756] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2024 | mr_cal_a_base against gbm_funding | +12.9% [+7.0, +19.3] | +0.02713 [-0.0007173, +0.2087] | gain | **undecided** |
| upper_tail_twcrps, by regime | 2024 | mr_cal_a_base against gbm_funding_cal_aligned | +10.4% [+5.7, +16.1] | +0.02129 [-0.002273, +0.2851] | gain | **undecided** |
| upper_tail_twcrps, by regime | 2024 | mr_cal_b_location against spread_mr_ctx | +11.5% [+1.6, +31.2] | +0.02347 [-0.001206, +0.7724] | gain | **undecided** |
| grid_crps, by target-day type | calendar_days | mr_cal_b_location against gbm_funding | -11.0% [-27.5, +0.4] | -0.228 [-0.4936, -0.002911] | undecided | **loss** |
| grid_crps, by target-day type | calendar_days | mr_cal_c_location_scale against B1 | +13.6% [+0.6, +31.2] | +0.3378 [-0.003526, +1.113] | gain | **undecided** |
| upper_tail_twcrps, by target-day type | calendar_days | mr_cal_c_location_scale against mr_cal_a_base | -13.6% [-36.3, +0.3] | -0.1463 [-0.293, -0.03019] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | calendar_days | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | -3.4% [-8.4, +0.9] | -0.04042 [-0.08156, -0.002144] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | calendar_days | mr_cal_d_no_fomc_iorb against mr_cal_a_base | -9.9% [-27.7, +0.5] | -0.1058 [-0.2287, -0.007683] | undecided | **loss** |
| grid_crps, by target-day type | dom_19_23 | mr_cal_c_location_scale against B1 | +35.2% [+2.6, +108.0] | +0.7442 [-0.004407, +5.402] | gain | **undecided** |
| grid_crps, by target-day type | dom_19_23 | mr_cal_d_no_fomc_iorb against B1 | +34.7% [+2.1, +102.0] | +0.7333 [-0.005644, +5.029] | gain | **undecided** |
| upper_tail_twcrps, by target-day type | dom_19_23 | mr_cal_b_location against B1_prime | +25.5% [-7.5, +58.3] | +0.1464 [+0.008901, +0.4764] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | dom_19_23 | mr_cal_b_location against spread_mr_ctx | +12.0% [+1.6, +21.6] | +0.05836 [-0.0008313, +0.1762] | gain | **undecided** |
| upper_tail_twcrps, by target-day type | dom_19_23 | mr_cal_c_location_scale against B1_prime | +25.7% [-10.0, +59.4] | +0.1478 [+0.00415, +0.4782] | undecided | **gain** |
| grid_crps, by target-day type | fomc_day | mr_cal_a_base against B1 | +4.0% [-1.2, +10.0] | +0.1822 [+0.03228, +0.4005] | undecided | **gain** |
| grid_crps, by target-day type | fomc_day | mr_cal_a_base against B1_prime | +2.9% [+1.0, +4.9] | +0.1323 [-0.006994, +0.407] | gain | **undecided** |
| grid_crps, by target-day type | fomc_day | mr_cal_a_base against B2 | +20.0% [-15.1, +40.7] | +1.098 [+0.4646, +1.866] | undecided | **gain** |
| grid_crps, by target-day type | fomc_day | mr_cal_b_location against B1_prime | -52.0% [-287.5, +28.4] | -2.357 [-9.315, -0.03955] | undecided | **loss** |
| grid_crps, by target-day type | fomc_day | mr_cal_b_location against gbm_funding_cal_aligned | -53.7% [-283.4, +26.9] | -2.407 [-9.262, -0.07806] | undecided | **loss** |
| grid_crps, by target-day type | fomc_day | mr_cal_b_location against mr_cal_a_base | -56.6% [-290.6, +29.5] | -2.489 [-9.038, -0.1679] | undecided | **loss** |
| grid_crps, by target-day type | fomc_day | mr_cal_b_location against spread_mr_ctx | -54.0% [-268.4, +29.0] | -2.414 [-8.651, -0.1251] | undecided | **loss** |
| grid_crps, by target-day type | fomc_day | mr_cal_c_location_scale against B1_prime | -37.9% [-193.5, +23.1] | -1.716 [-6.503, -0.0702] | undecided | **loss** |
| grid_crps, by target-day type | fomc_day | mr_cal_c_location_scale against gbm_funding_cal_aligned | -39.4% [-188.1, +21.4] | -1.767 [-6.41, -0.09493] | undecided | **loss** |
| grid_crps, by target-day type | fomc_day | mr_cal_c_location_scale against mr_cal_a_base | -42.0% [-191.0, +23.6] | -1.848 [-6.439, -0.1799] | undecided | **loss** |
| grid_crps, by target-day type | fomc_day | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | -26.6% [-88.2, +24.8] | -1.314 [-4.437, -0.1836] | undecided | **loss** |
| grid_crps, by target-day type | fomc_day | mr_cal_c_location_scale against spread_mr_ctx | -39.6% [-173.7, +22.8] | -1.774 [-6.059, -0.139] | undecided | **loss** |
| grid_crps, by target-day type | fomc_day | mr_cal_d_no_fomc_iorb against mr_cal_a_base | -12.1% [-87.1, +6.8] | -0.5339 [-2.48, -0.01257] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | fomc_day | mr_cal_a_base against B1 | +2.3% [-0.3, +4.5] | +0.0818 [+0.01097, +0.3687] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | fomc_day | mr_cal_a_base against B2 | +11.5% [-13.6, +24.9] | +0.4614 [+0.07378, +1.293] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | fomc_day | mr_cal_b_location against B1 | -43.8% [-309.4, +20.4] | -1.59 [-8.491, -0.00864] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | fomc_day | mr_cal_b_location against B1_prime | -43.0% [-310.2, +21.1] | -1.57 [-8.508, -0.01744] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | fomc_day | mr_cal_b_location against mr_cal_a_base | -47.1% [-322.0, +23.0] | -1.672 [-8.697, -0.07707] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | fomc_day | mr_cal_b_location against spread_mr_ctx | -45.6% [-301.5, +29.8] | -1.634 [-8.342, -0.07027] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | fomc_day | mr_cal_c_location_scale against mr_cal_a_base | -34.3% [-213.8, +20.5] | -1.216 [-6.063, -0.05556] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | fomc_day | mr_cal_c_location_scale against mr_cal_b_location | +8.7% [-14.9, +31.6] | +0.4557 [+0.01189, +2.048] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | fomc_day | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | -21.2% [-95.2, +39.4] | -0.8345 [-4.153, -0.03258] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | fomc_day | mr_cal_c_location_scale against spread_mr_ctx | -32.9% [-203.9, +24.4] | -1.179 [-5.967, -0.05176] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | fomc_day | mr_cal_d_no_fomc_iorb against mr_cal_a_base | -10.8% [-97.1, +6.7] | -0.3814 [-2.015, -0.002082] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | fomc_day | mr_cal_d_no_fomc_iorb against spread_mr_ctx | -9.6% [-89.5, +6.7] | -0.344 [-1.899, -0.002983] | undecided | **loss** |
| grid_crps, by target-day type | iorb_window | mr_cal_a_base against B1 | +52.7% [+18.3, +220.0] | +2.688 [-0.06602, +67.87] | gain | **undecided** |
| grid_crps, by target-day type | iorb_window | mr_cal_a_base against B2 | +33.8% [-18.5, +55.1] | +1.23 [+0.1547, +2.928] | undecided | **gain** |
| grid_crps, by target-day type | iorb_window | mr_cal_b_location against B1 | +52.3% [+17.8, +143.9] | +2.668 [-0.07469, +34.71] | gain | **undecided** |
| grid_crps, by target-day type | iorb_window | mr_cal_b_location against B2 | +33.3% [-23.8, +62.2] | +1.211 [+0.0116, +3.335] | undecided | **gain** |
| grid_crps, by target-day type | iorb_window | mr_cal_c_location_scale against B1 | +53.4% [+21.4, +149.6] | +2.721 [-0.0193, +38.86] | gain | **undecided** |
| grid_crps, by target-day type | iorb_window | mr_cal_c_location_scale against B2 | +34.7% [-18.3, +63.5] | +1.264 [+0.0657, +3.463] | undecided | **gain** |
| grid_crps, by target-day type | iorb_window | mr_cal_d_no_fomc_iorb against B1 | +52.8% [+22.4, +143.0] | +2.693 [-0.001419, +36.92] | gain | **undecided** |
| upper_tail_twcrps, by target-day type | iorb_window | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | +5.9% [+0.3, +20.0] | +0.09045 [-0.006357, +0.5773] | gain | **undecided** |
| upper_tail_twcrps, by target-day type | iorb_window | mr_cal_c_location_scale against spread_mr_ctx | +9.3% [-5.2, +17.6] | +0.1473 [+0.01168, +0.4191] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | month_end | mr_cal_a_base against B2 | +24.9% [-10.9, +58.2] | +0.5462 [+0.06021, +1.908] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | month_end | mr_cal_c_location_scale against B2 | +24.4% [+2.5, +41.6] | +0.5355 [-0.03505, +1.681] | gain | **undecided** |
| upper_tail_twcrps, by target-day type | month_end | mr_cal_d_no_fomc_iorb against B2 | +24.6% [+1.8, +40.9] | +0.5396 [-0.0813, +1.664] | gain | **undecided** |
| upper_tail_twcrps, by target-day type | post_month_end_window | mr_cal_b_location against B1 | +18.5% [+2.4, +29.2] | +0.2757 [-0.03426, +0.8032] | gain | **undecided** |
| upper_tail_twcrps, by target-day type | post_month_end_window | mr_cal_c_location_scale against B1 | +19.2% [+0.0, +31.2] | +0.2854 [-0.0468, +0.9209] | gain | **undecided** |
| upper_tail_twcrps, by target-day type | quarter_end | mr_cal_a_base against spread_mr_ctx | +4.3% [-6.5, +9.4] | +0.2161 [+0.05864, +0.387] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | quarter_end | mr_cal_c_location_scale against mr_cal_b_location | +15.4% [+13.4, +16.7] | +0.8497 [-0.04904, +3.485] | gain | **undecided** |
| grid_crps, by target-day type | settlement | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | -2.1% [-4.4, +0.1] | -0.04594 [-0.08944, -0.00521] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | settlement | mr_cal_a_base against gbm_funding_cal_aligned | +6.6% [-1.5, +14.7] | +0.08862 [+0.009439, +0.226] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | settlement | mr_cal_b_location against spread_mr_ctx | -11.5% [-33.9, +1.3] | -0.1496 [-0.3339, -0.01167] | undecided | **loss** |
| grid_crps, by target-day type | tax_date | mr_cal_a_base against B1 | +6.8% [-6.0, +13.7] | +0.3754 [+0.04967, +1.108] | undecided | **gain** |
| grid_crps, by target-day type | tax_date | mr_cal_a_base against B2 | +33.8% [-61.4, +58.0] | +2.617 [+1.42, +4.86] | undecided | **gain** |
| grid_crps, by target-day type | tax_date | mr_cal_a_base against gbm_funding_cal_aligned | +11.6% [-0.4, +23.5] | +0.6712 [+0.1149, +2.019] | undecided | **gain** |
| grid_crps, by target-day type | tax_date | mr_cal_a_base against spread_mr_ctx | +4.6% [-5.2, +14.2] | +0.2475 [+0.06492, +0.5525] | undecided | **gain** |
| grid_crps, by target-day type | tax_date | mr_cal_b_location against mr_cal_a_base | -69.0% [-413.8, +37.2] | -3.534 [-14.18, -0.1294] | undecided | **loss** |
| grid_crps, by target-day type | tax_date | mr_cal_b_location against spread_mr_ctx | -61.2% [-356.7, +44.3] | -3.287 [-13.41, -0.05867] | undecided | **loss** |
| grid_crps, by target-day type | tax_date | mr_cal_c_location_scale against mr_cal_a_base | -47.7% [-270.4, +28.7] | -2.441 [-10.43, -0.123] | undecided | **loss** |
| grid_crps, by target-day type | tax_date | mr_cal_c_location_scale against spread_mr_ctx | -40.9% [-226.9, +32.3] | -2.194 [-9.565, -0.04346] | undecided | **loss** |
| grid_crps, by target-day type | tax_date | mr_cal_d_no_fomc_iorb against mr_cal_a_base | -49.7% [-253.3, +25.4] | -2.545 [-9.544, -0.1312] | undecided | **loss** |
| grid_crps, by target-day type | tax_date | mr_cal_d_no_fomc_iorb against spread_mr_ctx | -42.8% [-208.9, +28.9] | -2.297 [-8.695, -0.0573] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | tax_date | mr_cal_a_base against B1 | +6.1% [-12.4, +15.7] | +0.286 [+0.0233, +2.129] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | tax_date | mr_cal_a_base against B1_prime | +5.9% [-2.7, +12.3] | +0.2765 [+0.01466, +2.68] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | tax_date | mr_cal_a_base against spread_mr_ctx | +4.1% [-6.4, +15.3] | +0.1885 [+0.01273, +0.6059] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | tax_date | mr_cal_b_location against mr_cal_a_base | -54.5% [-399.4, +19.6] | -2.384 [-13.36, -0.0463] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | tax_date | mr_cal_b_location against spread_mr_ctx | -48.1% [-352.2, +62.0] | -2.196 [-12.11, -0.005788] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | tax_date | mr_cal_c_location_scale against mr_cal_a_base | -36.5% [-267.3, +15.7] | -1.597 [-9.703, -0.02028] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | tax_date | mr_cal_c_location_scale against mr_cal_b_location | +11.6% [-52.0, +41.5] | +0.7872 [+0.001461, +3.602] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | tax_date | mr_cal_d_no_fomc_iorb against mr_cal_a_base | -37.9% [-228.7, +12.1] | -1.658 [-8.037, -0.02744] | undecided | **loss** |

Every other paired row reads the same on both intervals.

## All paired rows

### grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=1 | mr_cal_a_base against B1 | 1855 | +22.8% [+17.2, +34.3] | +0.4601 [+0.2517, +1.203] | gain |
| h=1 | mr_cal_a_base against B1_prime | 1855 | +9.8% [+2.1, +17.0] | +0.1687 [+0.06296, +0.3215] | gain |
| h=1 | mr_cal_a_base against B2 | 1855 | +37.2% [+20.9, +47.3] | +0.923 [+0.6621, +1.237] | gain |
| h=1 | mr_cal_a_base against gbm_funding | 1855 | +4.4% [-3.1, +9.1] | +0.0723 [-0.02027, +0.1405] | undecided |
| h=1 | mr_cal_a_base against gbm_funding_cal_aligned | 1855 | +0.8% [-6.4, +6.8] | +0.01309 [-0.09145, +0.1015] | undecided |
| h=1 | mr_cal_a_base against spread_mr_ctx | 1855 | +1.7% [-1.0, +4.3] | +0.02722 [-0.01413, +0.06804] | undecided |
| h=1 | mr_cal_b_location against B1 | 1855 | +6.3% [-9.8, +26.2] | +0.1266 [-0.1517, +0.6845] | undecided |
| h=1 | mr_cal_b_location against B1_prime | 1855 | -9.5% [-24.0, +3.4] | -0.1648 [-0.3721, +0.05417] | undecided |
| h=1 | mr_cal_b_location against B2 | 1855 | +23.8% [+12.2, +33.1] | +0.5895 [+0.3393, +0.869] | gain |
| h=1 | mr_cal_b_location against gbm_funding | 1855 | -16.0% [-30.1, -5.5] | -0.2612 [-0.4575, -0.09549] | loss |
| h=1 | mr_cal_b_location against gbm_funding_cal_aligned | 1855 | -20.4% [-35.6, -8.4] | -0.3204 [-0.5185, -0.1487] | loss |
| h=1 | mr_cal_b_location against mr_cal_a_base | 1855 | -21.4% [-38.0, -8.9] | -0.3335 [-0.5216, -0.1887] | loss |
| h=1 | mr_cal_b_location against spread_mr_ctx | 1855 | -19.3% [-33.4, -8.2] | -0.3063 [-0.4716, -0.1758] | loss |
| h=1 | mr_cal_c_location_scale against B1 | 1855 | +13.8% [+2.2, +30.0] | +0.2786 [+0.02817, +0.8942] | gain |
| h=1 | mr_cal_c_location_scale against B1_prime | 1855 | -0.7% [-11.5, +10.2] | -0.01282 [-0.178, +0.1894] | undecided |
| h=1 | mr_cal_c_location_scale against B2 | 1855 | +29.9% [+16.9, +38.9] | +0.7415 [+0.4973, +1.028] | gain |
| h=1 | mr_cal_c_location_scale against gbm_funding | 1855 | -6.7% [-16.4, +1.3] | -0.1092 [-0.2567, +0.02321] | undecided |
| h=1 | mr_cal_c_location_scale against gbm_funding_cal_aligned | 1855 | -10.7% [-21.3, -1.7] | -0.1684 [-0.3205, -0.02802] | loss |
| h=1 | mr_cal_c_location_scale against mr_cal_a_base | 1855 | -11.7% [-22.6, -3.5] | -0.1815 [-0.3077, -0.07654] | loss |
| h=1 | mr_cal_c_location_scale against mr_cal_b_location | 1855 | +8.0% [+4.7, +11.5] | +0.152 [+0.1034, +0.2176] | gain |
| h=1 | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 1855 | -3.2% [-5.5, -1.2] | -0.05345 [-0.08575, -0.02883] | loss |
| h=1 | mr_cal_c_location_scale against spread_mr_ctx | 1855 | -9.7% [-18.5, -2.8] | -0.1543 [-0.26, -0.06295] | loss |
| h=1 | mr_cal_d_no_fomc_iorb against B1 | 1855 | +16.5% [+6.4, +30.5] | +0.332 [+0.08964, +0.9425] | gain |
| h=1 | mr_cal_d_no_fomc_iorb against B1_prime | 1855 | +2.4% [-7.8, +12.9] | +0.04063 [-0.1167, +0.236] | undecided |
| h=1 | mr_cal_d_no_fomc_iorb against B2 | 1855 | +32.0% [+17.7, +41.1] | +0.7949 [+0.5476, +1.082] | gain |
| h=1 | mr_cal_d_no_fomc_iorb against gbm_funding | 1855 | -3.4% [-12.5, +4.1] | -0.05576 [-0.1977, +0.06761] | undecided |
| h=1 | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 1855 | -7.3% [-16.9, +1.0] | -0.115 [-0.2581, +0.01521] | undecided |
| h=1 | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 1855 | -8.2% [-17.5, -1.8] | -0.1281 [-0.2416, -0.03543] | loss |
| h=1 | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 1855 | -6.4% [-13.5, -1.0] | -0.1008 [-0.1935, -0.02141] | loss |

### upper_tail_twcrps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=1 | mr_cal_a_base against B1 | 1855 | +31.6% [+25.9, +40.6] | +0.4052 [+0.1951, +1.224] | gain |
| h=1 | mr_cal_a_base against B1_prime | 1855 | +14.4% [-3.2, +26.9] | +0.1481 [+0.04625, +0.3098] | gain (was undecided) |
| h=1 | mr_cal_a_base against B2 | 1855 | +21.0% [-2.9, +36.7] | +0.2341 [+0.09195, +0.395] | gain (was undecided) |
| h=1 | mr_cal_a_base against gbm_funding | 1855 | +1.3% [-12.8, +7.7] | +0.01169 [-0.07698, +0.05981] | undecided |
| h=1 | mr_cal_a_base against gbm_funding_cal_aligned | 1855 | -4.4% [-14.7, +2.5] | -0.03676 [-0.1284, +0.01815] | undecided |
| h=1 | mr_cal_a_base against spread_mr_ctx | 1855 | -0.6% [-4.2, +2.6] | -0.005333 [-0.03544, +0.02525] | undecided |
| h=1 | mr_cal_b_location against B1 | 1855 | +18.6% [+0.6, +37.8] | +0.2393 [-0.01747, +0.8622] | undecided (was gain) |
| h=1 | mr_cal_b_location against B1_prime | 1855 | -1.7% [-20.7, +14.6] | -0.0178 [-0.1824, +0.1717] | undecided |
| h=1 | mr_cal_b_location against B2 | 1855 | +6.1% [-9.5, +19.5] | +0.06824 [-0.08644, +0.2298] | undecided |
| h=1 | mr_cal_b_location against gbm_funding | 1855 | -17.3% [-39.0, -3.1] | -0.1542 [-0.3079, -0.03625] | loss |
| h=1 | mr_cal_b_location against gbm_funding_cal_aligned | 1855 | -24.1% [-50.2, -7.0] | -0.2027 [-0.3574, -0.0858] | loss |
| h=1 | mr_cal_b_location against mr_cal_a_base | 1855 | -18.9% [-46.0, -1.6] | -0.1659 [-0.3159, -0.06194] | loss |
| h=1 | mr_cal_b_location against spread_mr_ctx | 1855 | -19.6% [-44.9, -1.8] | -0.1712 [-0.3036, -0.07532] | loss |
| h=1 | mr_cal_c_location_scale against B1 | 1855 | +25.0% [+13.1, +39.5] | +0.3209 [+0.08152, +1.014] | gain |
| h=1 | mr_cal_c_location_scale against B1_prime | 1855 | +6.2% [-9.9, +21.4] | +0.06372 [-0.07291, +0.2533] | undecided |
| h=1 | mr_cal_c_location_scale against B2 | 1855 | +13.5% [-4.4, +27.4] | +0.1498 [+0.005711, +0.3136] | gain (was undecided) |
| h=1 | mr_cal_c_location_scale against gbm_funding | 1855 | -8.2% [-22.5, +2.3] | -0.0727 [-0.1895, +0.02365] | undecided |
| h=1 | mr_cal_c_location_scale against gbm_funding_cal_aligned | 1855 | -14.4% [-31.4, -2.1] | -0.1211 [-0.2394, -0.02446] | loss |
| h=1 | mr_cal_c_location_scale against mr_cal_a_base | 1855 | -9.6% [-26.5, +1.1] | -0.08439 [-0.1828, -0.007579] | loss (was undecided) |
| h=1 | mr_cal_c_location_scale against mr_cal_b_location | 1855 | +7.8% [+2.1, +14.2] | +0.08152 [+0.04414, +0.1369] | gain |
| h=1 | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 1855 | -3.9% [-8.2, -0.3] | -0.03636 [-0.06151, -0.01754] | loss |
| h=1 | mr_cal_c_location_scale against spread_mr_ctx | 1855 | -10.3% [-25.7, +0.7] | -0.08972 [-0.1708, -0.01966] | loss (was undecided) |
| h=1 | mr_cal_d_no_fomc_iorb against B1 | 1855 | +27.8% [+18.2, +39.7] | +0.3572 [+0.1245, +1.049] | gain |
| h=1 | mr_cal_d_no_fomc_iorb against B1_prime | 1855 | +9.8% [-7.2, +24.6] | +0.1001 [-0.03114, +0.2867] | undecided |
| h=1 | mr_cal_d_no_fomc_iorb against B2 | 1855 | +16.7% [-4.1, +31.2] | +0.1861 [+0.04383, +0.3514] | gain (was undecided) |
| h=1 | mr_cal_d_no_fomc_iorb against gbm_funding | 1855 | -4.1% [-17.6, +5.7] | -0.03634 [-0.1475, +0.05252] | undecided |
| h=1 | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 1855 | -10.1% [-24.1, +0.4] | -0.08479 [-0.1949, +0.003423] | undecided |
| h=1 | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 1855 | -5.5% [-17.8, +2.1] | -0.04803 [-0.1292, +0.01778] | undecided |
| h=1 | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 1855 | -6.1% [-16.8, +1.4] | -0.05336 [-0.1187, +0.006212] | undecided |

### grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=2 | mr_cal_a_base against B1 | 1855 | +25.2% [+19.1, +40.8] | +0.5588 [+0.3156, +1.571] | gain |
| h=2 | mr_cal_a_base against B1_prime | 1855 | +10.1% [+4.2, +16.4] | +0.186 [+0.09031, +0.3309] | gain |
| h=2 | mr_cal_a_base against B2 | 1855 | +33.9% [+22.2, +43.6] | +0.85 [+0.5997, +1.166] | gain |
| h=2 | mr_cal_a_base against gbm_funding | 1855 | +6.1% [+2.5, +9.5] | +0.1079 [+0.04805, +0.1729] | gain |
| h=2 | mr_cal_a_base against gbm_funding_cal_aligned | 1855 | +5.9% [+1.0, +10.6] | +0.1044 [+0.02414, +0.1932] | gain |
| h=2 | mr_cal_a_base against spread_mr_ctx | 1855 | +3.0% [+0.3, +5.6] | +0.05042 [+0.009658, +0.09437] | gain |
| h=2 | mr_cal_b_location against B1 | 1855 | +12.1% [-1.2, +32.4] | +0.2672 [-0.02926, +0.9963] | undecided |
| h=2 | mr_cal_b_location against B1_prime | 1855 | -5.7% [-17.4, +5.0] | -0.1056 [-0.2913, +0.09402] | undecided |
| h=2 | mr_cal_b_location against B2 | 1855 | +22.3% [+13.1, +30.9] | +0.5585 [+0.3217, +0.8382] | gain |
| h=2 | mr_cal_b_location against gbm_funding | 1855 | -10.4% [-23.2, -1.0] | -0.1836 [-0.3651, -0.02852] | loss |
| h=2 | mr_cal_b_location against gbm_funding_cal_aligned | 1855 | -10.6% [-23.3, -0.9] | -0.1872 [-0.367, -0.02575] | loss |
| h=2 | mr_cal_b_location against mr_cal_a_base | 1855 | -17.6% [-31.4, -7.5] | -0.2916 [-0.462, -0.1593] | loss |
| h=2 | mr_cal_b_location against spread_mr_ctx | 1855 | -14.1% [-25.6, -5.5] | -0.2411 [-0.3942, -0.1194] | loss |
| h=2 | mr_cal_c_location_scale against B1 | 1855 | +17.2% [+5.8, +36.7] | +0.3818 [+0.09039, +1.212] | gain |
| h=2 | mr_cal_c_location_scale against B1_prime | 1855 | +0.5% [-9.1, +10.1] | +0.009002 [-0.1515, +0.2057] | undecided |
| h=2 | mr_cal_c_location_scale against B2 | 1855 | +26.8% [+18.0, +35.0] | +0.673 [+0.4402, +0.9571] | gain |
| h=2 | mr_cal_c_location_scale against gbm_funding | 1855 | -3.9% [-13.8, +3.8] | -0.06907 [-0.217, +0.0707] | undecided |
| h=2 | mr_cal_c_location_scale against gbm_funding_cal_aligned | 1855 | -4.1% [-14.0, +3.9] | -0.07261 [-0.2197, +0.07353] | undecided |
| h=2 | mr_cal_c_location_scale against mr_cal_a_base | 1855 | -10.7% [-21.4, -2.7] | -0.177 [-0.3102, -0.06604] | loss |
| h=2 | mr_cal_c_location_scale against mr_cal_b_location | 1855 | +5.9% [+4.0, +7.9] | +0.1146 [+0.07917, +0.1596] | gain |
| h=2 | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 1855 | -3.4% [-6.3, -1.0] | -0.06069 [-0.1011, -0.02578] | loss |
| h=2 | mr_cal_c_location_scale against spread_mr_ctx | 1855 | -7.4% [-15.9, -0.6] | -0.1266 [-0.2423, -0.02302] | loss |
| h=2 | mr_cal_d_no_fomc_iorb against B1 | 1855 | +20.0% [+10.4, +37.0] | +0.4425 [+0.1664, +1.269] | gain |
| h=2 | mr_cal_d_no_fomc_iorb against B1_prime | 1855 | +3.8% [-4.8, +12.5] | +0.0697 [-0.0795, +0.2519] | undecided |
| h=2 | mr_cal_d_no_fomc_iorb against B2 | 1855 | +29.3% [+19.5, +37.6] | +0.7337 [+0.5005, +1.021] | gain |
| h=2 | mr_cal_d_no_fomc_iorb against gbm_funding | 1855 | -0.5% [-8.4, +5.9] | -0.008381 [-0.1368, +0.1136] | undecided |
| h=2 | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 1855 | -0.7% [-8.6, +6.1] | -0.01192 [-0.14, +0.1152] | undecided |
| h=2 | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 1855 | -7.0% [-15.5, -1.0] | -0.1163 [-0.2314, -0.02502] | loss |
| h=2 | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 1855 | -3.9% [-10.5, +1.3] | -0.06588 [-0.1638, +0.0202] | undecided |

### upper_tail_twcrps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=2 | mr_cal_a_base against B1 | 1855 | +34.1% [+27.1, +48.7] | +0.4614 [+0.2172, +1.601] | gain |
| h=2 | mr_cal_a_base against B1_prime | 1855 | +13.4% [+1.4, +25.1] | +0.138 [+0.04933, +0.2924] | gain |
| h=2 | mr_cal_a_base against B2 | 1855 | +20.8% [+5.0, +35.0] | +0.2338 [+0.1132, +0.3963] | gain |
| h=2 | mr_cal_a_base against gbm_funding | 1855 | +4.7% [-0.5, +8.8] | +0.04404 [+0.002715, +0.09105] | gain (was undecided) |
| h=2 | mr_cal_a_base against gbm_funding_cal_aligned | 1855 | +4.6% [-2.2, +10.4] | +0.04293 [-0.01266, +0.1061] | undecided |
| h=2 | mr_cal_a_base against spread_mr_ctx | 1855 | +1.0% [-2.6, +5.1] | +0.008986 [-0.02086, +0.04652] | undecided |
| h=2 | mr_cal_b_location against B1 | 1855 | +22.8% [+6.7, +45.6] | +0.3091 [+0.03006, +1.16] | gain |
| h=2 | mr_cal_b_location against B1_prime | 1855 | -1.4% [-18.1, +13.0] | -0.01435 [-0.1598, +0.1557] | undecided |
| h=2 | mr_cal_b_location against B2 | 1855 | +7.2% [-5.7, +18.7] | +0.08152 [-0.06055, +0.2377] | undecided |
| h=2 | mr_cal_b_location against gbm_funding | 1855 | -11.6% [-33.0, +2.0] | -0.1083 [-0.2445, +0.00708] | undecided |
| h=2 | mr_cal_b_location against gbm_funding_cal_aligned | 1855 | -11.7% [-33.2, +2.0] | -0.1094 [-0.2467, +0.008963] | undecided |
| h=2 | mr_cal_b_location against mr_cal_a_base | 1855 | -17.1% [-40.6, -2.3] | -0.1523 [-0.2867, -0.05708] | loss |
| h=2 | mr_cal_b_location against spread_mr_ctx | 1855 | -15.9% [-36.7, -2.1] | -0.1433 [-0.2594, -0.05407] | loss |
| h=2 | mr_cal_c_location_scale against B1 | 1855 | +27.1% [+13.3, +48.3] | +0.3672 [+0.08455, +1.322] | gain |
| h=2 | mr_cal_c_location_scale against B1_prime | 1855 | +4.2% [-10.3, +18.4] | +0.04371 [-0.09187, +0.2303] | undecided |
| h=2 | mr_cal_c_location_scale against B2 | 1855 | +12.4% [+0.6, +23.6] | +0.1396 [+0.003474, +0.3025] | gain |
| h=2 | mr_cal_c_location_scale against gbm_funding | 1855 | -5.4% [-22.1, +6.1] | -0.05021 [-0.164, +0.06366] | undecided |
| h=2 | mr_cal_c_location_scale against gbm_funding_cal_aligned | 1855 | -5.5% [-22.7, +6.2] | -0.05131 [-0.1681, +0.06573] | undecided |
| h=2 | mr_cal_c_location_scale against mr_cal_a_base | 1855 | -10.6% [-29.3, +1.4] | -0.09424 [-0.1994, -0.008592] | loss (was undecided) |
| h=2 | mr_cal_c_location_scale against mr_cal_b_location | 1855 | +5.6% [+2.7, +8.6] | +0.05806 [+0.03298, +0.09431] | gain |
| h=2 | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 1855 | -3.1% [-8.1, +1.3] | -0.02921 [-0.06392, +0.004598] | undecided |
| h=2 | mr_cal_c_location_scale against spread_mr_ctx | 1855 | -9.5% [-25.6, +2.2] | -0.08526 [-0.1772, +0.0004368] | undecided |
| h=2 | mr_cal_d_no_fomc_iorb against B1 | 1855 | +29.3% [+18.1, +47.9] | +0.3964 [+0.1255, +1.37] | gain |
| h=2 | mr_cal_d_no_fomc_iorb against B1_prime | 1855 | +7.1% [-6.2, +20.5] | +0.07292 [-0.04855, +0.2463] | undecided |
| h=2 | mr_cal_d_no_fomc_iorb against B2 | 1855 | +15.0% [+2.4, +27.2] | +0.1688 [+0.04343, +0.3333] | gain |
| h=2 | mr_cal_d_no_fomc_iorb against gbm_funding | 1855 | -2.2% [-14.5, +6.9] | -0.02099 [-0.1154, +0.07735] | undecided |
| h=2 | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 1855 | -2.4% [-15.2, +7.1] | -0.0221 [-0.1205, +0.0813] | undecided |
| h=2 | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 1855 | -7.3% [-20.8, +1.1] | -0.06503 [-0.1491, +0.003383] | undecided |
| h=2 | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 1855 | -6.2% [-17.6, +2.3] | -0.05605 [-0.1293, +0.01567] | undecided |

### grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=3 | mr_cal_a_base against B1 | 1855 | +26.6% [+20.5, +42.2] | +0.6229 [+0.3664, +1.598] | gain |
| h=3 | mr_cal_a_base against B1_prime | 1855 | +11.8% [+6.9, +17.9] | +0.2299 [+0.1315, +0.3897] | gain |
| h=3 | mr_cal_a_base against B2 | 1855 | +32.0% [+21.7, +41.5] | +0.8079 [+0.5562, +1.123] | gain |
| h=3 | mr_cal_a_base against gbm_funding | 1855 | +7.6% [+4.1, +10.9] | +0.1406 [+0.07165, +0.2182] | gain |
| h=3 | mr_cal_a_base against gbm_funding_cal_aligned | 1855 | +6.7% [+2.2, +10.9] | +0.1224 [+0.03858, +0.217] | gain |
| h=3 | mr_cal_a_base against spread_mr_ctx | 1855 | +3.5% [+1.0, +5.9] | +0.06143 [+0.02096, +0.1054] | gain |
| h=3 | mr_cal_b_location against B1 | 1855 | +15.0% [+3.1, +33.9] | +0.3515 [+0.0471, +1.091] | gain |
| h=3 | mr_cal_b_location against B1_prime | 1855 | -2.1% [-13.2, +8.0] | -0.04152 [-0.2328, +0.1682] | undecided |
| h=3 | mr_cal_b_location against B2 | 1855 | +21.3% [+12.4, +29.8] | +0.5365 [+0.2943, +0.8155] | gain |
| h=3 | mr_cal_b_location against gbm_funding | 1855 | -7.0% [-19.1, +1.9] | -0.1308 [-0.3172, +0.03493] | undecided |
| h=3 | mr_cal_b_location against gbm_funding_cal_aligned | 1855 | -8.1% [-20.3, +1.3] | -0.149 [-0.3328, +0.02038] | undecided |
| h=3 | mr_cal_b_location against mr_cal_a_base | 1855 | -15.8% [-28.4, -6.9] | -0.2714 [-0.4411, -0.1392] | loss |
| h=3 | mr_cal_b_location against spread_mr_ctx | 1855 | -11.8% [-22.5, -4.0] | -0.2099 [-0.3629, -0.08517] | loss |
| h=3 | mr_cal_c_location_scale against B1 | 1855 | +19.7% [+9.5, +37.6] | +0.4594 [+0.1612, +1.277] | gain |
| h=3 | mr_cal_c_location_scale against B1_prime | 1855 | +3.4% [-5.5, +12.5] | +0.06638 [-0.1013, +0.2723] | undecided |
| h=3 | mr_cal_c_location_scale against B2 | 1855 | +25.5% [+16.9, +33.7] | +0.6444 [+0.4057, +0.9298] | gain |
| h=3 | mr_cal_c_location_scale against gbm_funding | 1855 | -1.2% [-10.5, +6.1] | -0.02287 [-0.1756, +0.1249] | undecided |
| h=3 | mr_cal_c_location_scale against gbm_funding_cal_aligned | 1855 | -2.2% [-11.8, +5.5] | -0.04107 [-0.193, +0.1119] | undecided |
| h=3 | mr_cal_c_location_scale against mr_cal_a_base | 1855 | -9.5% [-18.9, -2.6] | -0.1635 [-0.2928, -0.05528] | loss |
| h=3 | mr_cal_c_location_scale against mr_cal_b_location | 1855 | +5.4% [+3.5, +7.5] | +0.1079 [+0.07172, +0.1525] | gain |
| h=3 | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 1855 | -3.4% [-5.8, -1.4] | -0.0618 [-0.09905, -0.0321] | loss |
| h=3 | mr_cal_c_location_scale against spread_mr_ctx | 1855 | -5.7% [-13.6, +0.3] | -0.1021 [-0.2184, -0.0003856] | loss (was undecided) |
| h=3 | mr_cal_d_no_fomc_iorb against B1 | 1855 | +22.3% [+13.4, +38.5] | +0.5212 [+0.2319, +1.343] | gain |
| h=3 | mr_cal_d_no_fomc_iorb against B1_prime | 1855 | +6.6% [-1.5, +15.0] | +0.1282 [-0.02857, +0.3257] | undecided |
| h=3 | mr_cal_d_no_fomc_iorb against B2 | 1855 | +28.0% [+18.8, +36.3] | +0.7062 [+0.4715, +0.9967] | gain |
| h=3 | mr_cal_d_no_fomc_iorb against gbm_funding | 1855 | +2.1% [-5.7, +8.5] | +0.03893 [-0.09816, +0.1747] | undecided |
| h=3 | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 1855 | +1.1% [-6.8, +7.8] | +0.02073 [-0.1141, +0.1586] | undecided |
| h=3 | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 1855 | -5.9% [-13.8, -0.3] | -0.1017 [-0.2174, -0.007108] | loss |
| h=3 | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 1855 | -2.3% [-8.4, +2.6] | -0.04025 [-0.1405, +0.04905] | undecided |

### upper_tail_twcrps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=3 | mr_cal_a_base against B1 | 1855 | +35.8% [+27.9, +51.8] | +0.5003 [+0.2452, +1.641] | gain |
| h=3 | mr_cal_a_base against B1_prime | 1855 | +16.0% [+6.2, +27.2] | +0.1705 [+0.08058, +0.3402] | gain |
| h=3 | mr_cal_a_base against B2 | 1855 | +20.8% [+8.0, +33.9] | +0.2359 [+0.1178, +0.3944] | gain |
| h=3 | mr_cal_a_base against gbm_funding | 1855 | +7.2% [+2.6, +11.6] | +0.06944 [+0.02068, +0.1378] | gain |
| h=3 | mr_cal_a_base against gbm_funding_cal_aligned | 1855 | +5.9% [-0.6, +11.7] | +0.05648 [-0.005331, +0.1336] | undecided |
| h=3 | mr_cal_a_base against spread_mr_ctx | 1855 | +2.0% [-1.3, +5.6] | +0.01793 [-0.01004, +0.05363] | undecided |
| h=3 | mr_cal_b_location against B1 | 1855 | +25.0% [+10.2, +47.7] | +0.3494 [+0.06295, +1.208] | gain |
| h=3 | mr_cal_b_location against B1_prime | 1855 | +1.8% [-13.7, +15.5] | +0.01967 [-0.1298, +0.1998] | undecided |
| h=3 | mr_cal_b_location against B2 | 1855 | +7.5% [-5.2, +18.5] | +0.0851 [-0.05857, +0.2415] | undecided |
| h=3 | mr_cal_b_location against gbm_funding | 1855 | -8.4% [-29.1, +4.7] | -0.0814 [-0.2238, +0.04567] | undecided |
| h=3 | mr_cal_b_location against gbm_funding_cal_aligned | 1855 | -9.9% [-31.6, +4.1] | -0.09437 [-0.2377, +0.03459] | undecided |
| h=3 | mr_cal_b_location against mr_cal_a_base | 1855 | -16.8% [-38.9, -3.3] | -0.1508 [-0.2838, -0.05675] | loss |
| h=3 | mr_cal_b_location against spread_mr_ctx | 1855 | -14.5% [-33.7, -2.0] | -0.1329 [-0.2508, -0.04307] | loss |
| h=3 | mr_cal_c_location_scale against B1 | 1855 | +28.9% [+16.1, +50.1] | +0.4038 [+0.1167, +1.351] | gain |
| h=3 | mr_cal_c_location_scale against B1_prime | 1855 | +6.9% [-6.9, +20.2] | +0.07408 [-0.06513, +0.267] | undecided |
| h=3 | mr_cal_c_location_scale against B2 | 1855 | +12.3% [+0.7, +23.1] | +0.1395 [+0.003509, +0.3021] | gain |
| h=3 | mr_cal_c_location_scale against gbm_funding | 1855 | -2.8% [-19.0, +8.2] | -0.027 [-0.1461, +0.09751] | undecided |
| h=3 | mr_cal_c_location_scale against gbm_funding_cal_aligned | 1855 | -4.2% [-21.5, +7.6] | -0.03996 [-0.1634, +0.08803] | undecided |
| h=3 | mr_cal_c_location_scale against mr_cal_a_base | 1855 | -10.7% [-27.8, -0.1] | -0.09644 [-0.1988, -0.01463] | loss |
| h=3 | mr_cal_c_location_scale against mr_cal_b_location | 1855 | +5.2% [+2.2, +8.3] | +0.0544 [+0.03024, +0.08903] | gain |
| h=3 | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 1855 | -3.6% [-8.1, -0.0] | -0.03481 [-0.06747, -0.008033] | loss |
| h=3 | mr_cal_c_location_scale against spread_mr_ctx | 1855 | -8.6% [-23.0, +1.6] | -0.07851 [-0.1691, +0.003393] | undecided |
| h=3 | mr_cal_d_no_fomc_iorb against B1 | 1855 | +31.4% [+20.3, +50.4] | +0.4386 [+0.1594, +1.417] | gain |
| h=3 | mr_cal_d_no_fomc_iorb against B1_prime | 1855 | +10.2% [-2.1, +23.0] | +0.1089 [-0.01868, +0.2959] | undecided |
| h=3 | mr_cal_d_no_fomc_iorb against B2 | 1855 | +15.4% [+4.0, +26.9] | +0.1743 [+0.04931, +0.3398] | gain |
| h=3 | mr_cal_d_no_fomc_iorb against gbm_funding | 1855 | +0.8% [-11.7, +10.1] | +0.007812 [-0.09733, +0.1221] | undecided |
| h=3 | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 1855 | -0.5% [-14.0, +9.4] | -0.00515 [-0.1108, +0.114] | undecided |
| h=3 | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 1855 | -6.9% [-19.4, +1.3] | -0.06163 [-0.1463, +0.00913] | undecided |
| h=3 | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 1855 | -4.8% [-15.1, +3.1] | -0.0437 [-0.1178, +0.02913] | undecided |

### grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=4 | mr_cal_a_base against B1 | 1855 | +27.1% [+20.3, +44.4] | +0.6518 [+0.3799, +1.657] | gain |
| h=4 | mr_cal_a_base against B1_prime | 1855 | +13.3% [+9.0, +19.0] | +0.2697 [+0.1649, +0.4396] | gain |
| h=4 | mr_cal_a_base against B2 | 1855 | +30.7% [+21.2, +39.8] | +0.7769 [+0.5235, +1.089] | gain |
| h=4 | mr_cal_a_base against gbm_funding | 1855 | +7.6% [+4.0, +10.9] | +0.1452 [+0.06738, +0.2311] | gain |
| h=4 | mr_cal_a_base against gbm_funding_cal_aligned | 1855 | +6.8% [+2.1, +11.0] | +0.1277 [+0.03659, +0.2273] | gain |
| h=4 | mr_cal_a_base against spread_mr_ctx | 1855 | +3.3% [+0.8, +5.8] | +0.06034 [+0.01737, +0.1064] | gain |
| h=4 | mr_cal_b_location against B1 | 1855 | +16.3% [+4.7, +35.4] | +0.3921 [+0.07614, +1.155] | gain |
| h=4 | mr_cal_b_location against B1_prime | 1855 | +0.5% [-10.3, +10.1] | +0.009955 [-0.1892, +0.2264] | undecided |
| h=4 | mr_cal_b_location against B2 | 1855 | +20.4% [+11.8, +28.7] | +0.5172 [+0.2702, +0.7936] | gain |
| h=4 | mr_cal_b_location against gbm_funding | 1855 | -6.0% [-17.7, +2.8] | -0.1145 [-0.3014, +0.05421] | undecided |
| h=4 | mr_cal_b_location against gbm_funding_cal_aligned | 1855 | -7.0% [-18.9, +2.1] | -0.132 [-0.3191, +0.03893] | undecided |
| h=4 | mr_cal_b_location against mr_cal_a_base | 1855 | -14.8% [-26.6, -6.6] | -0.2597 [-0.4239, -0.1286] | loss |
| h=4 | mr_cal_b_location against spread_mr_ctx | 1855 | -11.0% [-21.0, -3.7] | -0.1994 [-0.3511, -0.07632] | loss |
| h=4 | mr_cal_c_location_scale against B1 | 1855 | +21.0% [+10.7, +39.9] | +0.5055 [+0.1908, +1.357] | gain |
| h=4 | mr_cal_c_location_scale against B1_prime | 1855 | +6.1% [-2.7, +14.8] | +0.1234 [-0.05364, +0.3436] | undecided |
| h=4 | mr_cal_c_location_scale against B2 | 1855 | +24.9% [+16.8, +32.9] | +0.6307 [+0.3882, +0.9148] | gain |
| h=4 | mr_cal_c_location_scale against gbm_funding | 1855 | -0.1% [-9.4, +7.3] | -0.0009734 [-0.159, +0.1541] | undecided |
| h=4 | mr_cal_c_location_scale against gbm_funding_cal_aligned | 1855 | -1.0% [-10.6, +6.7] | -0.01849 [-0.1772, +0.1384] | undecided |
| h=4 | mr_cal_c_location_scale against mr_cal_a_base | 1855 | -8.3% [-17.2, -1.8] | -0.1462 [-0.2732, -0.03938] | loss |
| h=4 | mr_cal_c_location_scale against mr_cal_b_location | 1855 | +5.6% [+3.9, +7.5] | +0.1135 [+0.07613, +0.1602] | gain |
| h=4 | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 1855 | -2.8% [-5.2, -0.7] | -0.05211 [-0.08945, -0.0197] | loss |
| h=4 | mr_cal_c_location_scale against spread_mr_ctx | 1855 | -4.7% [-12.2, +1.1] | -0.08589 [-0.2026, +0.01614] | undecided |
| h=4 | mr_cal_d_no_fomc_iorb against B1 | 1855 | +23.2% [+14.0, +40.6] | +0.5576 [+0.2543, +1.41] | gain |
| h=4 | mr_cal_d_no_fomc_iorb against B1_prime | 1855 | +8.7% [+1.0, +16.8] | +0.1755 [+0.01021, +0.3856] | gain |
| h=4 | mr_cal_d_no_fomc_iorb against B2 | 1855 | +27.0% [+18.5, +34.9] | +0.6828 [+0.4462, +0.9686] | gain |
| h=4 | mr_cal_d_no_fomc_iorb against gbm_funding | 1855 | +2.7% [-5.1, +9.1] | +0.05114 [-0.09033, +0.1907] | undecided |
| h=4 | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 1855 | +1.8% [-6.1, +8.5] | +0.03362 [-0.1057, +0.176] | undecided |
| h=4 | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 1855 | -5.4% [-12.7, +0.0] | -0.09411 [-0.2083, -3.668e-05] | loss (was undecided) |
| h=4 | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 1855 | -1.9% [-7.9, +3.0] | -0.03378 [-0.1339, +0.05576] | undecided |

### upper_tail_twcrps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=4 | mr_cal_a_base against B1 | 1855 | +36.6% [+27.4, +56.4] | +0.519 [+0.2504, +1.73] | gain |
| h=4 | mr_cal_a_base against B1_prime | 1855 | +17.9% [+10.3, +28.7] | +0.1962 [+0.102, +0.3813] | gain |
| h=4 | mr_cal_a_base against B2 | 1855 | +20.9% [+9.9, +32.4] | +0.2384 [+0.1206, +0.396] | gain |
| h=4 | mr_cal_a_base against gbm_funding | 1855 | +7.5% [+2.9, +11.8] | +0.07337 [+0.01841, +0.1531] | gain |
| h=4 | mr_cal_a_base against gbm_funding_cal_aligned | 1855 | +6.5% [-0.6, +12.3] | +0.06266 [-0.005554, +0.1476] | undecided |
| h=4 | mr_cal_a_base against spread_mr_ctx | 1855 | +1.8% [-1.7, +5.4] | +0.01626 [-0.014, +0.05338] | undecided |
| h=4 | mr_cal_b_location against B1 | 1855 | +25.9% [+10.8, +50.9] | +0.367 [+0.06868, +1.283] | gain |
| h=4 | mr_cal_b_location against B1_prime | 1855 | +4.0% [-11.1, +17.2] | +0.0442 [-0.1115, +0.2344] | undecided |
| h=4 | mr_cal_b_location against B2 | 1855 | +7.6% [-5.1, +17.9] | +0.08635 [-0.05801, +0.2404] | undecided |
| h=4 | mr_cal_b_location against gbm_funding | 1855 | -8.1% [-28.9, +5.3] | -0.07865 [-0.2219, +0.05212] | undecided |
| h=4 | mr_cal_b_location against gbm_funding_cal_aligned | 1855 | -9.3% [-30.8, +4.7] | -0.08936 [-0.2348, +0.04468] | undecided |
| h=4 | mr_cal_b_location against mr_cal_a_base | 1855 | -16.9% [-37.7, -4.2] | -0.152 [-0.2821, -0.05878] | loss |
| h=4 | mr_cal_b_location against spread_mr_ctx | 1855 | -14.8% [-33.6, -2.9] | -0.1358 [-0.2531, -0.04659] | loss |
| h=4 | mr_cal_c_location_scale against B1 | 1855 | +30.1% [+16.5, +54.5] | +0.4272 [+0.1236, +1.447] | gain |
| h=4 | mr_cal_c_location_scale against B1_prime | 1855 | +9.5% [-3.4, +22.2] | +0.1044 [-0.04334, +0.3116] | undecided |
| h=4 | mr_cal_c_location_scale against B2 | 1855 | +12.9% [+2.0, +22.4] | +0.1466 [+0.009944, +0.3089] | gain |
| h=4 | mr_cal_c_location_scale against gbm_funding | 1855 | -1.9% [-18.5, +9.5] | -0.01844 [-0.1413, +0.1145] | undecided |
| h=4 | mr_cal_c_location_scale against gbm_funding_cal_aligned | 1855 | -3.0% [-20.8, +8.9] | -0.02915 [-0.156, +0.1051] | undecided |
| h=4 | mr_cal_c_location_scale against mr_cal_a_base | 1855 | -10.2% [-26.2, +0.2] | -0.09181 [-0.1906, -0.01065] | loss (was undecided) |
| h=4 | mr_cal_c_location_scale against mr_cal_b_location | 1855 | +5.7% [+3.3, +8.5] | +0.06021 [+0.03324, +0.09812] | gain |
| h=4 | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 1855 | -2.9% [-7.4, +1.0] | -0.02775 [-0.06163, +0.001712] | undecided |
| h=4 | mr_cal_c_location_scale against spread_mr_ctx | 1855 | -8.3% [-22.3, +1.7] | -0.07555 [-0.165, +0.007087] | undecided |
| h=4 | mr_cal_d_no_fomc_iorb against B1 | 1855 | +32.1% [+20.0, +54.2] | +0.455 [+0.1613, +1.486] | gain |
| h=4 | mr_cal_d_no_fomc_iorb against B1_prime | 1855 | +12.1% [+0.8, +24.3] | +0.1322 [-0.002876, +0.3308] | undecided (was gain) |
| h=4 | mr_cal_d_no_fomc_iorb against B2 | 1855 | +15.3% [+5.0, +25.5] | +0.1743 [+0.05012, +0.3336] | gain |
| h=4 | mr_cal_d_no_fomc_iorb against gbm_funding | 1855 | +1.0% [-12.1, +10.5] | +0.009306 [-0.0991, +0.1306] | undecided |
| h=4 | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 1855 | -0.1% [-14.0, +10.0] | -0.001403 [-0.1112, +0.1229] | undecided |
| h=4 | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 1855 | -7.1% [-19.1, +0.9] | -0.06406 [-0.1475, +0.006356] | undecided |
| h=4 | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 1855 | -5.2% [-15.5, +2.7] | -0.0478 [-0.1208, +0.02364] | undecided |

### grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=5 | mr_cal_a_base against B1 | 1855 | +26.9% [+19.9, +45.0] | +0.6623 [+0.3869, +1.669] | gain |
| h=5 | mr_cal_a_base against B1_prime | 1855 | +14.2% [+10.0, +19.9] | +0.2977 [+0.1898, +0.4741] | gain |
| h=5 | mr_cal_a_base against B2 | 1855 | +29.3% [+20.0, +38.3] | +0.7456 [+0.489, +1.051] | gain |
| h=5 | mr_cal_a_base against gbm_funding | 1855 | +8.0% [+4.3, +11.3] | +0.1568 [+0.07363, +0.2477] | gain |
| h=5 | mr_cal_a_base against gbm_funding_cal_aligned | 1855 | +7.8% [+3.2, +12.0] | +0.1531 [+0.05695, +0.2553] | gain |
| h=5 | mr_cal_a_base against spread_mr_ctx | 1855 | +3.4% [+1.0, +5.8] | +0.06397 [+0.02007, +0.1112] | gain |
| h=5 | mr_cal_b_location against B1 | 1855 | +16.9% [+5.8, +35.9] | +0.4165 [+0.09931, +1.184] | gain |
| h=5 | mr_cal_b_location against B1_prime | 1855 | +2.5% [-7.5, +11.7] | +0.05195 [-0.1457, +0.2725] | undecided |
| h=5 | mr_cal_b_location against B2 | 1855 | +19.6% [+10.9, +27.9] | +0.4998 [+0.2541, +0.7764] | gain |
| h=5 | mr_cal_b_location against gbm_funding | 1855 | -4.5% [-15.7, +3.8] | -0.08901 [-0.2773, +0.07948] | undecided |
| h=5 | mr_cal_b_location against gbm_funding_cal_aligned | 1855 | -4.7% [-16.0, +3.6] | -0.09274 [-0.2812, +0.07869] | undecided |
| h=5 | mr_cal_b_location against mr_cal_a_base | 1855 | -13.6% [-24.9, -5.8] | -0.2458 [-0.4112, -0.1169] | loss |
| h=5 | mr_cal_b_location against spread_mr_ctx | 1855 | -9.7% [-19.4, -2.8] | -0.1818 [-0.3343, -0.05983] | loss |
| h=5 | mr_cal_c_location_scale against B1 | 1855 | +21.0% [+11.0, +40.0] | +0.5178 [+0.2022, +1.366] | gain |
| h=5 | mr_cal_c_location_scale against B1_prime | 1855 | +7.3% [-1.0, +15.7] | +0.1532 [-0.02648, +0.3776] | undecided |
| h=5 | mr_cal_c_location_scale against B2 | 1855 | +23.6% [+15.3, +31.6] | +0.601 [+0.3566, +0.8828] | gain |
| h=5 | mr_cal_c_location_scale against gbm_funding | 1855 | +0.6% [-8.6, +7.8] | +0.01224 [-0.151, +0.1693] | undecided |
| h=5 | mr_cal_c_location_scale against gbm_funding_cal_aligned | 1855 | +0.4% [-8.9, +7.7] | +0.008512 [-0.156, +0.1669] | undecided |
| h=5 | mr_cal_c_location_scale against mr_cal_a_base | 1855 | -8.0% [-16.6, -1.7] | -0.1445 [-0.2733, -0.03841] | loss |
| h=5 | mr_cal_c_location_scale against mr_cal_b_location | 1855 | +4.9% [+3.3, +6.8] | +0.1013 [+0.0659, +0.1451] | gain |
| h=5 | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 1855 | -2.9% [-5.3, -0.7] | -0.05415 [-0.09341, -0.0204] | loss |
| h=5 | mr_cal_c_location_scale against spread_mr_ctx | 1855 | -4.3% [-11.6, +1.4] | -0.08057 [-0.1992, +0.02406] | undecided |
| h=5 | mr_cal_d_no_fomc_iorb against B1 | 1855 | +23.2% [+14.1, +40.8] | +0.5719 [+0.2673, +1.424] | gain |
| h=5 | mr_cal_d_no_fomc_iorb against B1_prime | 1855 | +9.9% [+2.4, +17.8] | +0.2074 [+0.04074, +0.4208] | gain |
| h=5 | mr_cal_d_no_fomc_iorb against B2 | 1855 | +25.7% [+17.2, +33.7] | +0.6552 [+0.4166, +0.938] | gain |
| h=5 | mr_cal_d_no_fomc_iorb against gbm_funding | 1855 | +3.4% [-4.2, +9.7] | +0.06639 [-0.07949, +0.2086] | undecided |
| h=5 | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 1855 | +3.2% [-4.4, +9.6] | +0.06266 [-0.08232, +0.2068] | undecided |
| h=5 | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 1855 | -5.0% [-12.0, +0.2] | -0.09039 [-0.2058, +0.004125] | undecided |
| h=5 | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 1855 | -1.4% [-7.2, +3.4] | -0.02641 [-0.1273, +0.06543] | undecided |

### upper_tail_twcrps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=5 | mr_cal_a_base against B1 | 1855 | +35.8% [+25.4, +59.2] | +0.5088 [+0.2368, +1.751] | gain |
| h=5 | mr_cal_a_base against B1_prime | 1855 | +17.3% [+9.9, +28.7] | +0.1906 [+0.09507, +0.3842] | gain |
| h=5 | mr_cal_a_base against B2 | 1855 | +20.4% [+9.9, +31.6] | +0.2346 [+0.1171, +0.391] | gain |
| h=5 | mr_cal_a_base against gbm_funding | 1855 | +7.9% [+3.2, +12.4] | +0.07866 [+0.02075, +0.1632] | gain |
| h=5 | mr_cal_a_base against gbm_funding_cal_aligned | 1855 | +7.5% [+0.8, +13.3] | +0.07404 [+0.003182, +0.1624] | gain |
| h=5 | mr_cal_a_base against spread_mr_ctx | 1855 | +2.2% [-1.4, +6.0] | +0.0203 [-0.01162, +0.06076] | undecided |
| h=5 | mr_cal_b_location against B1 | 1855 | +25.5% [+9.8, +52.8] | +0.362 [+0.06133, +1.297] | gain |
| h=5 | mr_cal_b_location against B1_prime | 1855 | +4.0% [-10.7, +17.2] | +0.04382 [-0.1084, +0.2328] | undecided |
| h=5 | mr_cal_b_location against B2 | 1855 | +7.6% [-5.1, +17.8] | +0.08777 [-0.05704, +0.2419] | undecided |
| h=5 | mr_cal_b_location against gbm_funding | 1855 | -6.9% [-26.9, +6.0] | -0.06814 [-0.2113, +0.06378] | undecided |
| h=5 | mr_cal_b_location against gbm_funding_cal_aligned | 1855 | -7.4% [-27.6, +5.7] | -0.07276 [-0.219, +0.0603] | undecided |
| h=5 | mr_cal_b_location against mr_cal_a_base | 1855 | -16.1% [-36.1, -4.3] | -0.1468 [-0.2756, -0.05407] | loss |
| h=5 | mr_cal_b_location against spread_mr_ctx | 1855 | -13.5% [-31.0, -2.2] | -0.1265 [-0.2421, -0.0385] | loss |
| h=5 | mr_cal_c_location_scale against B1 | 1855 | +29.0% [+14.6, +56.3] | +0.4126 [+0.1098, +1.442] | gain |
| h=5 | mr_cal_c_location_scale against B1_prime | 1855 | +8.6% [-4.3, +21.6] | +0.09444 [-0.05095, +0.3027] | undecided |
| h=5 | mr_cal_c_location_scale against B2 | 1855 | +12.1% [+1.0, +21.6] | +0.1384 [+0.0009419, +0.2994] | gain |
| h=5 | mr_cal_c_location_scale against gbm_funding | 1855 | -1.8% [-18.4, +9.6] | -0.01753 [-0.1428, +0.1187] | undecided |
| h=5 | mr_cal_c_location_scale against gbm_funding_cal_aligned | 1855 | -2.2% [-19.4, +9.4] | -0.02214 [-0.1519, +0.1131] | undecided |
| h=5 | mr_cal_c_location_scale against mr_cal_a_base | 1855 | -10.5% [-26.0, -0.4] | -0.09619 [-0.1959, -0.0158] | loss |
| h=5 | mr_cal_c_location_scale against mr_cal_b_location | 1855 | +4.8% [+2.4, +7.5] | +0.05062 [+0.02481, +0.0874] | gain |
| h=5 | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 1855 | -3.0% [-7.7, +1.0] | -0.02955 [-0.0645, +0.001497] | undecided |
| h=5 | mr_cal_c_location_scale against spread_mr_ctx | 1855 | -8.1% [-21.9, +1.7] | -0.07589 [-0.166, +0.007151] | undecided |
| h=5 | mr_cal_d_no_fomc_iorb against B1 | 1855 | +31.1% [+17.8, +56.5] | +0.4421 [+0.1468, +1.489] | gain |
| h=5 | mr_cal_d_no_fomc_iorb against B1_prime | 1855 | +11.2% [+0.0, +24.0] | +0.124 [-0.009331, +0.3265] | undecided (was gain) |
| h=5 | mr_cal_d_no_fomc_iorb against B2 | 1855 | +14.6% [+4.3, +24.8] | +0.1679 [+0.04376, +0.3288] | gain |
| h=5 | mr_cal_d_no_fomc_iorb against gbm_funding | 1855 | +1.2% [-11.6, +10.8] | +0.01202 [-0.0984, +0.1352] | undecided |
| h=5 | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 1855 | +0.7% [-12.4, +10.7] | +0.007402 [-0.104, +0.1339] | undecided |
| h=5 | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 1855 | -7.3% [-18.9, +0.6] | -0.06664 [-0.152, +0.005199] | undecided |
| h=5 | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 1855 | -5.0% [-14.9, +2.9] | -0.04634 [-0.121, +0.02788] | undecided |

### grid_crps, by all decision days

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| all decision days | mr_cal_a_base against B1 | 1855 | +25.8% [+19.5, +42.3] | +0.5912 [+0.3413, +1.574] | gain |
| all decision days | mr_cal_a_base against B1_prime | 1855 | +11.9% [+7.3, +18.1] | +0.2304 [+0.1362, +0.3952] | gain |
| all decision days | mr_cal_a_base against B2 | 1855 | +32.6% [+22.1, +42.0] | +0.8207 [+0.5695, +1.136] | gain |
| all decision days | mr_cal_a_base against gbm_funding | 1855 | +6.8% [+3.3, +10.1] | +0.1246 [+0.06132, +0.1941] | gain |
| all decision days | mr_cal_a_base against gbm_funding_cal_aligned | 1855 | +5.8% [+1.1, +10.2] | +0.1041 [+0.0233, +0.1932] | gain |
| all decision days | mr_cal_a_base against spread_mr_ctx | 1855 | +3.0% [+0.5, +5.5] | +0.05267 [+0.0117, +0.0959] | gain |
| all decision days | mr_cal_b_location against B1 | 1855 | +13.6% [+1.1, +33.5] | +0.3108 [+0.01117, +1.047] | gain |
| all decision days | mr_cal_b_location against B1_prime | 1855 | -2.6% [-13.9, +7.9] | -0.04999 [-0.2405, +0.1635] | undecided |
| all decision days | mr_cal_b_location against B2 | 1855 | +21.5% [+12.5, +30.1] | +0.5403 [+0.2992, +0.8223] | gain |
| all decision days | mr_cal_b_location against gbm_funding | 1855 | -8.6% [-20.8, +0.5] | -0.1558 [-0.3392, +0.005546] | undecided |
| all decision days | mr_cal_b_location against gbm_funding_cal_aligned | 1855 | -9.8% [-22.1, -0.3] | -0.1762 [-0.3601, -0.01048] | loss |
| all decision days | mr_cal_b_location against mr_cal_a_base | 1855 | -16.5% [-29.7, -7.2] | -0.2804 [-0.4536, -0.1463] | loss |
| all decision days | mr_cal_b_location against spread_mr_ctx | 1855 | -13.0% [-24.1, -5.0] | -0.2277 [-0.3841, -0.1039] | loss |
| all decision days | mr_cal_c_location_scale against B1 | 1855 | +18.7% [+8.2, +37.6] | +0.4286 [+0.1382, +1.256] | gain |
| all decision days | mr_cal_c_location_scale against B1_prime | 1855 | +3.5% [-5.4, +12.8] | +0.06784 [-0.09604, +0.2784] | undecided |
| all decision days | mr_cal_c_location_scale against B2 | 1855 | +26.1% [+17.3, +34.4] | +0.6581 [+0.4215, +0.9449] | gain |
| all decision days | mr_cal_c_location_scale against gbm_funding | 1855 | -2.1% [-11.3, +5.2] | -0.03798 [-0.1851, +0.1031] | undecided |
| all decision days | mr_cal_c_location_scale against gbm_funding_cal_aligned | 1855 | -3.2% [-12.8, +4.5] | -0.05842 [-0.2073, +0.08776] | undecided |
| all decision days | mr_cal_c_location_scale against mr_cal_a_base | 1855 | -9.6% [-19.2, -2.5] | -0.1625 [-0.2923, -0.05644] | loss |
| all decision days | mr_cal_c_location_scale against mr_cal_b_location | 1855 | +6.0% [+4.1, +8.1] | +0.1178 [+0.08051, +0.1652] | gain |
| all decision days | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 1855 | -3.1% [-5.5, -1.1] | -0.05644 [-0.09185, -0.02785] | loss |
| all decision days | mr_cal_c_location_scale against spread_mr_ctx | 1855 | -6.3% [-14.2, -0.1] | -0.1099 [-0.2238, -0.00899] | loss |
| all decision days | mr_cal_d_no_fomc_iorb against B1 | 1855 | +21.2% [+12.0, +38.3] | +0.4851 [+0.2038, +1.308] | gain |
| all decision days | mr_cal_d_no_fomc_iorb against B1_prime | 1855 | +6.4% [-1.5, +15.1] | +0.1243 [-0.02691, +0.3262] | undecided |
| all decision days | mr_cal_d_no_fomc_iorb against B2 | 1855 | +28.4% [+19.0, +36.7] | +0.7146 [+0.4799, +1.005] | gain |
| all decision days | mr_cal_d_no_fomc_iorb against gbm_funding | 1855 | +1.0% [-6.7, +7.4] | +0.01847 [-0.1145, +0.1462] | undecided |
| all decision days | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 1855 | -0.1% [-8.0, +6.6] | -0.001974 [-0.1334, +0.1299] | undecided |
| all decision days | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 1855 | -6.2% [-14.2, -0.6] | -0.1061 [-0.2213, -0.01299] | loss |
| all decision days | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 1855 | -3.1% [-9.3, +1.8] | -0.05343 [-0.1513, +0.03265] | undecided |

### upper_tail_twcrps, by all decision days

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| all decision days | mr_cal_a_base against B1 | 1855 | +34.8% [+27.1, +51.7] | +0.4789 [+0.2291, +1.619] | gain |
| all decision days | mr_cal_a_base against B1_prime | 1855 | +15.8% [+6.7, +27.5] | +0.1687 [+0.08129, +0.3539] | gain |
| all decision days | mr_cal_a_base against B2 | 1855 | +20.8% [+7.1, +34.0] | +0.2354 [+0.1153, +0.3957] | gain |
| all decision days | mr_cal_a_base against gbm_funding | 1855 | +5.8% [+0.8, +10.3] | +0.05544 [+0.01074, +0.1129] | gain |
| all decision days | mr_cal_a_base against gbm_funding_cal_aligned | 1855 | +4.3% [-2.8, +10.2] | +0.03987 [-0.01874, +0.1088] | undecided |
| all decision days | mr_cal_a_base against spread_mr_ctx | 1855 | +1.3% [-2.0, +5.0] | +0.01163 [-0.0168, +0.04689] | undecided |
| all decision days | mr_cal_b_location against B1 | 1855 | +23.7% [+7.9, +47.6] | +0.3254 [+0.044, +1.195] | gain |
| all decision days | mr_cal_b_location against B1_prime | 1855 | +1.4% [-14.5, +15.6] | +0.01511 [-0.133, +0.2017] | undecided |
| all decision days | mr_cal_b_location against B2 | 1855 | +7.2% [-5.8, +18.5] | +0.0818 [-0.0629, +0.2399] | undecided |
| all decision days | mr_cal_b_location against gbm_funding | 1855 | -10.3% [-31.2, +3.1] | -0.09814 [-0.2402, +0.02455] | undecided |
| all decision days | mr_cal_b_location against gbm_funding_cal_aligned | 1855 | -12.1% [-34.0, +2.1] | -0.1137 [-0.2564, +0.011] | undecided |
| all decision days | mr_cal_b_location against mr_cal_a_base | 1855 | -17.1% [-39.8, -3.2] | -0.1536 [-0.2893, -0.05868] | loss |
| all decision days | mr_cal_b_location against spread_mr_ctx | 1855 | -15.6% [-35.7, -2.5] | -0.1419 [-0.2628, -0.05251] | loss |
| all decision days | mr_cal_c_location_scale against B1 | 1855 | +28.1% [+14.8, +50.4] | +0.3863 [+0.105, +1.355] | gain |
| all decision days | mr_cal_c_location_scale against B1_prime | 1855 | +7.1% [-6.1, +20.8] | +0.07607 [-0.05958, +0.2764] | undecided |
| all decision days | mr_cal_c_location_scale against B2 | 1855 | +12.6% [+0.8, +23.5] | +0.1428 [+0.007976, +0.3069] | gain |
| all decision days | mr_cal_c_location_scale against gbm_funding | 1855 | -3.9% [-19.8, +7.1] | -0.03717 [-0.1523, +0.08018] | undecided |
| all decision days | mr_cal_c_location_scale against gbm_funding_cal_aligned | 1855 | -5.6% [-22.8, +6.3] | -0.05274 [-0.1716, +0.06738] | undecided |
| all decision days | mr_cal_c_location_scale against mr_cal_a_base | 1855 | -10.3% [-27.2, +0.4] | -0.09261 [-0.1953, -0.0124] | loss (was undecided) |
| all decision days | mr_cal_c_location_scale against mr_cal_b_location | 1855 | +5.8% [+2.9, +9.2] | +0.06096 [+0.03486, +0.09857] | gain |
| all decision days | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 1855 | -3.3% [-7.8, +0.5] | -0.03154 [-0.06304, -0.005401] | loss (was undecided) |
| all decision days | mr_cal_c_location_scale against spread_mr_ctx | 1855 | -8.9% [-23.8, +1.5] | -0.08099 [-0.1706, -0.001595] | loss (was undecided) |
| all decision days | mr_cal_d_no_fomc_iorb against B1 | 1855 | +30.4% [+19.2, +50.4] | +0.4179 [+0.1444, +1.407] | gain |
| all decision days | mr_cal_d_no_fomc_iorb against B1_prime | 1855 | +10.1% [-1.8, +23.3] | +0.1076 [-0.01554, +0.3023] | undecided |
| all decision days | mr_cal_d_no_fomc_iorb against B2 | 1855 | +15.4% [+3.4, +27.3] | +0.1743 [+0.04974, +0.3409] | gain |
| all decision days | mr_cal_d_no_fomc_iorb against gbm_funding | 1855 | -0.6% [-13.0, +8.6] | -0.005639 [-0.105, +0.1015] | undecided |
| all decision days | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 1855 | -2.3% [-15.5, +7.7] | -0.02121 [-0.1215, +0.08952] | undecided |
| all decision days | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 1855 | -6.8% [-19.6, +1.2] | -0.06108 [-0.1466, +0.007377] | undecided |
| all decision days | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 1855 | -5.4% [-16.0, +2.5] | -0.04945 [-0.1219, +0.01984] | undecided |

### grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2018-19 | mr_cal_a_base against B1 | 361 | +34.1% [+24.5, +59.1] | +1.974 [+0.7838, +9.176] | gain |
| 2018-19 | mr_cal_a_base against B1_prime | 361 | +11.6% [+1.2, +27.9] | +0.4986 [+0.1416, +1.369] | gain |
| 2018-19 | mr_cal_a_base against B2 | 361 | +14.5% [+1.1, +28.5] | +0.645 [+0.1938, +1.188] | gain |
| 2018-19 | mr_cal_a_base against gbm_funding | 361 | +6.1% [+0.3, +11.5] | +0.2483 [+0.05741, +0.4727] | gain |
| 2018-19 | mr_cal_a_base against gbm_funding_cal_aligned | 361 | +4.2% [-3.7, +11.3] | +0.1683 [-0.1218, +0.4914] | undecided |
| 2018-19 | mr_cal_a_base against spread_mr_ctx | 361 | -3.3% [-7.4, +1.4] | -0.1227 [-0.2204, +0.01283] | undecided |
| 2018-19 | mr_cal_b_location against B1 | 361 | +30.9% [+17.8, +53.8] | +1.791 [+0.5117, +6.858] | gain |
| 2018-19 | mr_cal_b_location against B1_prime | 361 | +7.3% [-7.1, +22.4] | +0.3151 [-0.2536, +1.088] | undecided |
| 2018-19 | mr_cal_b_location against B2 | 361 | +10.3% [-2.7, +23.1] | +0.4615 [-0.09712, +1.06] | undecided |
| 2018-19 | mr_cal_b_location against gbm_funding | 361 | +1.6% [-10.6, +10.2] | +0.06478 [-0.4267, +0.4853] | undecided |
| 2018-19 | mr_cal_b_location against gbm_funding_cal_aligned | 361 | -0.4% [-14.7, +9.4] | -0.01516 [-0.5508, +0.4567] | undecided |
| 2018-19 | mr_cal_b_location against mr_cal_a_base | 361 | -4.8% [-18.7, +2.7] | -0.1835 [-0.6488, +0.1165] | undecided |
| 2018-19 | mr_cal_b_location against spread_mr_ctx | 361 | -8.3% [-24.9, +1.3] | -0.3061 [-0.7431, +0.01911] | undecided |
| 2018-19 | mr_cal_c_location_scale against B1 | 361 | +33.7% [+21.6, +56.4] | +1.95 [+0.6445, +7.64] | gain |
| 2018-19 | mr_cal_c_location_scale against B1_prime | 361 | +11.0% [-2.6, +27.1] | +0.4741 [-0.05084, +1.338] | undecided |
| 2018-19 | mr_cal_c_location_scale against B2 | 361 | +13.9% [+0.7, +26.9] | +0.6205 [+0.08935, +1.218] | gain |
| 2018-19 | mr_cal_c_location_scale against gbm_funding | 361 | +5.5% [-4.4, +13.8] | +0.2238 [-0.1784, +0.6412] | undecided |
| 2018-19 | mr_cal_c_location_scale against gbm_funding_cal_aligned | 361 | +3.6% [-8.1, +12.9] | +0.1439 [-0.3078, +0.6124] | undecided |
| 2018-19 | mr_cal_c_location_scale against mr_cal_a_base | 361 | -0.6% [-9.8, +5.3] | -0.02446 [-0.357, +0.2364] | undecided |
| 2018-19 | mr_cal_c_location_scale against mr_cal_b_location | 361 | +4.0% [+1.4, +7.2] | +0.159 [+0.06147, +0.3001] | gain |
| 2018-19 | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 361 | -1.6% [-6.2, +1.1] | -0.05969 [-0.1845, +0.01614] | undecided |
| 2018-19 | mr_cal_c_location_scale against spread_mr_ctx | 361 | -4.0% [-15.7, +4.3] | -0.1471 [-0.468, +0.1684] | undecided |
| 2018-19 | mr_cal_d_no_fomc_iorb against B1 | 361 | +34.7% [+23.4, +55.2] | +2.009 [+0.7432, +7.603] | gain |
| 2018-19 | mr_cal_d_no_fomc_iorb against B1_prime | 361 | +12.4% [-2.5, +29.2] | +0.5338 [+0.027, +1.385] | gain (was undecided) |
| 2018-19 | mr_cal_d_no_fomc_iorb against B2 | 361 | +15.2% [-0.1, +29.5] | +0.6802 [+0.1842, +1.276] | gain (was undecided) |
| 2018-19 | mr_cal_d_no_fomc_iorb against gbm_funding | 361 | +7.0% [-2.9, +15.6] | +0.2835 [-0.07272, +0.6716] | undecided |
| 2018-19 | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 361 | +5.1% [-5.3, +14.8] | +0.2036 [-0.1925, +0.6618] | undecided |
| 2018-19 | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 361 | +0.9% [-6.1, +6.3] | +0.03523 [-0.2525, +0.2604] | undecided |
| 2018-19 | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 361 | -2.4% [-10.8, +4.3] | -0.08743 [-0.3536, +0.1892] | undecided |

### upper_tail_twcrps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2018-19 | mr_cal_a_base against B1 | 361 | +35.7% [+25.3, +59.8] | +1.885 [+0.6816, +8.962] | gain |
| 2018-19 | mr_cal_a_base against B1_prime | 361 | +11.5% [-0.5, +30.8] | +0.4411 [+0.07829, +1.368] | gain (was undecided) |
| 2018-19 | mr_cal_a_base against B2 | 361 | +11.0% [-1.3, +24.5] | +0.419 [+0.03364, +0.89] | gain (was undecided) |
| 2018-19 | mr_cal_a_base against gbm_funding | 361 | +6.8% [+0.1, +12.8] | +0.2487 [+0.06483, +0.485] | gain |
| 2018-19 | mr_cal_a_base against gbm_funding_cal_aligned | 361 | +5.1% [-3.7, +12.7] | +0.183 [-0.09586, +0.5024] | undecided |
| 2018-19 | mr_cal_a_base against spread_mr_ctx | 361 | -2.5% [-6.8, +2.8] | -0.08234 [-0.1805, +0.07441] | undecided |
| 2018-19 | mr_cal_b_location against B1 | 361 | +34.9% [+21.6, +55.4] | +1.844 [+0.5405, +7.037] | gain |
| 2018-19 | mr_cal_b_location against B1_prime | 361 | +10.4% [-6.0, +26.5] | +0.4001 [-0.1549, +1.164] | undecided |
| 2018-19 | mr_cal_b_location against B2 | 361 | +9.9% [-2.4, +21.8] | +0.378 [-0.06227, +0.8448] | undecided |
| 2018-19 | mr_cal_b_location against gbm_funding | 361 | +5.7% [-6.7, +14.6] | +0.2077 [-0.2653, +0.6068] | undecided |
| 2018-19 | mr_cal_b_location against gbm_funding_cal_aligned | 361 | +4.0% [-10.0, +13.9] | +0.142 [-0.3796, +0.587] | undecided |
| 2018-19 | mr_cal_b_location against mr_cal_a_base | 361 | -1.2% [-13.5, +5.9] | -0.04099 [-0.4949, +0.233] | undecided |
| 2018-19 | mr_cal_b_location against spread_mr_ctx | 361 | -3.7% [-18.6, +4.4] | -0.1233 [-0.5267, +0.1677] | undecided |
| 2018-19 | mr_cal_c_location_scale against B1 | 361 | +37.1% [+24.7, +57.7] | +1.957 [+0.6397, +7.76] | gain |
| 2018-19 | mr_cal_c_location_scale against B1_prime | 361 | +13.4% [-2.9, +31.0] | +0.5126 [-0.0124, +1.388] | undecided |
| 2018-19 | mr_cal_c_location_scale against B2 | 361 | +12.9% [-0.5, +25.2] | +0.4905 [+0.06005, +0.9824] | gain (was undecided) |
| 2018-19 | mr_cal_c_location_scale against gbm_funding | 361 | +8.8% [-2.5, +17.9] | +0.3203 [-0.07447, +0.7448] | undecided |
| 2018-19 | mr_cal_c_location_scale against gbm_funding_cal_aligned | 361 | +7.1% [-5.6, +17.2] | +0.2545 [-0.1984, +0.729] | undecided |
| 2018-19 | mr_cal_c_location_scale against mr_cal_a_base | 361 | +2.1% [-6.7, +8.1] | +0.07152 [-0.258, +0.3217] | undecided |
| 2018-19 | mr_cal_c_location_scale against mr_cal_b_location | 361 | +3.3% [+0.8, +6.9] | +0.1125 [+0.03461, +0.2494] | gain |
| 2018-19 | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 361 | -1.3% [-6.9, +1.6] | -0.04424 [-0.1686, +0.03045] | undecided |
| 2018-19 | mr_cal_c_location_scale against spread_mr_ctx | 361 | -0.3% [-11.0, +7.2] | -0.01082 [-0.315, +0.3037] | undecided |
| 2018-19 | mr_cal_d_no_fomc_iorb against B1 | 361 | +37.9% [+25.8, +56.8] | +2.001 [+0.719, +7.707] | gain |
| 2018-19 | mr_cal_d_no_fomc_iorb against B1_prime | 361 | +14.5% [-3.8, +33.2] | +0.5569 [+0.04943, +1.426] | gain (was undecided) |
| 2018-19 | mr_cal_d_no_fomc_iorb against B2 | 361 | +14.0% [-1.8, +28.3] | +0.5348 [+0.1396, +1.031] | gain (was undecided) |
| 2018-19 | mr_cal_d_no_fomc_iorb against gbm_funding | 361 | +10.0% [-2.6, +19.9] | +0.3645 [+0.009498, +0.7606] | gain (was undecided) |
| 2018-19 | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 361 | +8.4% [-4.4, +19.6] | +0.2987 [-0.09462, +0.76] | undecided |
| 2018-19 | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 361 | +3.4% [-5.0, +9.3] | +0.1158 [-0.1629, +0.3294] | undecided |
| 2018-19 | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 361 | +1.0% [-7.0, +7.9] | +0.03342 [-0.2148, +0.308] | undecided |

### grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2020 | mr_cal_a_base against B1 | 251 | +14.6% [+6.5, +22.7] | +0.2409 [+0.09329, +0.5803] | gain |
| 2020 | mr_cal_a_base against B1_prime | 251 | +12.6% [+2.5, +26.9] | +0.2022 [+0.01987, +0.7199] | gain |
| 2020 | mr_cal_a_base against B2 | 251 | +49.7% [+24.0, +70.4] | +1.39 [+0.5604, +3.102] | gain |
| 2020 | mr_cal_a_base against gbm_funding | 251 | -0.0% [-10.0, +9.5] | -0.0004046 [-0.1124, +0.1613] | undecided |
| 2020 | mr_cal_a_base against gbm_funding_cal_aligned | 251 | +3.1% [-8.2, +16.4] | +0.04498 [-0.1087, +0.3139] | undecided |
| 2020 | mr_cal_a_base against spread_mr_ctx | 251 | +14.9% [+8.0, +20.3] | +0.2467 [+0.1891, +0.3205] | gain |
| 2020 | mr_cal_b_location against B1 | 251 | -62.4% [-130.0, +11.6] | -1.028 [-1.627, -0.4779] | loss (was undecided) |
| 2020 | mr_cal_b_location against B1_prime | 251 | -66.3% [-145.5, +25.8] | -1.067 [-1.684, -0.4617] | loss (was undecided) |
| 2020 | mr_cal_b_location against B2 | 251 | +4.3% [-39.0, +34.4] | +0.1209 [-0.866, +1.211] | undecided |
| 2020 | mr_cal_b_location against gbm_funding | 251 | -90.2% [-187.4, -10.5] | -1.269 [-1.883, -0.8091] | loss |
| 2020 | mr_cal_b_location against gbm_funding_cal_aligned | 251 | -84.3% [-181.6, -6.0] | -1.224 [-1.846, -0.7614] | loss |
| 2020 | mr_cal_b_location against mr_cal_a_base | 251 | -90.2% [-172.4, -22.9] | -1.269 [-1.868, -0.8474] | loss |
| 2020 | mr_cal_b_location against spread_mr_ctx | 251 | -61.8% [-119.7, -14.1] | -1.022 [-1.611, -0.6073] | loss |
| 2020 | mr_cal_c_location_scale against B1 | 251 | -42.2% [-94.6, +21.7] | -0.6955 [-1.156, -0.1701] | loss (was undecided) |
| 2020 | mr_cal_c_location_scale against B1_prime | 251 | -45.6% [-107.2, +35.9] | -0.7342 [-1.214, -0.1341] | loss (was undecided) |
| 2020 | mr_cal_c_location_scale against B2 | 251 | +16.2% [-17.7, +42.3] | +0.4532 [-0.4547, +1.67] | undecided |
| 2020 | mr_cal_c_location_scale against gbm_funding | 251 | -66.6% [-140.7, +0.4] | -0.9368 [-1.394, -0.5305] | loss (was undecided) |
| 2020 | mr_cal_c_location_scale against gbm_funding_cal_aligned | 251 | -61.4% [-136.2, +5.2] | -0.8914 [-1.366, -0.4814] | loss (was undecided) |
| 2020 | mr_cal_c_location_scale against mr_cal_a_base | 251 | -66.5% [-128.5, -10.2] | -0.9364 [-1.374, -0.5884] | loss |
| 2020 | mr_cal_c_location_scale against mr_cal_b_location | 251 | +12.4% [+8.5, +17.1] | +0.3324 [+0.2209, +0.5173] | gain |
| 2020 | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 251 | -9.1% [-18.9, -0.3] | -0.1952 [-0.3574, -0.05611] | loss |
| 2020 | mr_cal_c_location_scale against spread_mr_ctx | 251 | -41.7% [-84.2, -3.1] | -0.6897 [-1.112, -0.3486] | loss |
| 2020 | mr_cal_d_no_fomc_iorb against B1 | 251 | -30.4% [-70.9, +14.8] | -0.5003 [-0.9006, -0.07623] | loss (was undecided) |
| 2020 | mr_cal_d_no_fomc_iorb against B1_prime | 251 | -33.5% [-81.9, +24.6] | -0.539 [-0.962, -0.04678] | loss (was undecided) |
| 2020 | mr_cal_d_no_fomc_iorb against B2 | 251 | +23.2% [-4.8, +47.4] | +0.6484 [-0.2166, +1.908] | undecided |
| 2020 | mr_cal_d_no_fomc_iorb against gbm_funding | 251 | -52.7% [-113.6, -4.2] | -0.7416 [-1.141, -0.415] | loss |
| 2020 | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 251 | -47.9% [-106.8, -0.2] | -0.6962 [-1.097, -0.3748] | loss |
| 2020 | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 251 | -52.7% [-102.4, -14.1] | -0.7412 [-1.134, -0.448] | loss |
| 2020 | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 251 | -29.9% [-63.3, -4.6] | -0.4945 [-0.8733, -0.2215] | loss |

### upper_tail_twcrps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2020 | mr_cal_a_base against B1 | 251 | +31.0% [+17.0, +55.6] | +0.2293 [+0.05256, +1.646] | gain |
| 2020 | mr_cal_a_base against B1_prime | 251 | +32.1% [+19.0, +63.9] | +0.2412 [+0.0313, +2.217] | gain |
| 2020 | mr_cal_a_base against B2 | 251 | +58.1% [-24.5, +84.2] | +0.7083 [+0.3634, +1.13] | gain (was undecided) |
| 2020 | mr_cal_a_base against gbm_funding | 251 | -17.4% [-71.5, +28.2] | -0.07579 [-0.1383, +0.01499] | undecided |
| 2020 | mr_cal_a_base against gbm_funding_cal_aligned | 251 | -6.7% [-36.0, +13.4] | -0.03204 [-0.0904, +0.04521] | undecided |
| 2020 | mr_cal_a_base against spread_mr_ctx | 251 | +22.9% [-19.4, +50.4] | +0.1521 [+0.08778, +0.2191] | gain (was undecided) |
| 2020 | mr_cal_b_location against B1 | 251 | -102.9% [-359.8, +118.8] | -0.7617 [-1.378, -0.22] | loss (was undecided) |
| 2020 | mr_cal_b_location against B1_prime | 251 | -99.7% [-373.3, +139.1] | -0.7498 [-1.383, -0.1575] | loss (was undecided) |
| 2020 | mr_cal_b_location against B2 | 251 | -23.2% [-103.6, +18.5] | -0.2827 [-1.073, +0.2136] | undecided |
| 2020 | mr_cal_b_location against gbm_funding | 251 | -245.2% [-872.6, +159.1] | -1.067 [-1.697, -0.6729] | loss (was undecided) |
| 2020 | mr_cal_b_location against gbm_funding_cal_aligned | 251 | -213.7% [-711.7, +142.7] | -1.023 [-1.669, -0.6354] | loss (was undecided) |
| 2020 | mr_cal_b_location against mr_cal_a_base | 251 | -194.0% [-564.1, +82.3] | -0.991 [-1.635, -0.6232] | loss (was undecided) |
| 2020 | mr_cal_b_location against spread_mr_ctx | 251 | -126.5% [-303.0, +30.5] | -0.8389 [-1.442, -0.4984] | loss (was undecided) |
| 2020 | mr_cal_c_location_scale against B1 | 251 | -69.5% [-262.1, +124.4] | -0.5144 [-0.9775, +0.0505] | undecided |
| 2020 | mr_cal_c_location_scale against B1_prime | 251 | -66.8% [-274.6, +144.8] | -0.5025 [-0.9902, +0.1381] | undecided |
| 2020 | mr_cal_c_location_scale against B2 | 251 | -2.9% [-59.2, +30.3] | -0.03542 [-0.6302, +0.4328] | undecided |
| 2020 | mr_cal_c_location_scale against gbm_funding | 251 | -188.4% [-678.8, +152.9] | -0.8195 [-1.259, -0.478] | loss (was undecided) |
| 2020 | mr_cal_c_location_scale against gbm_funding_cal_aligned | 251 | -162.0% [-543.7, +146.4] | -0.7757 [-1.22, -0.4458] | loss (was undecided) |
| 2020 | mr_cal_c_location_scale against mr_cal_a_base | 251 | -145.6% [-426.2, +90.9] | -0.7437 [-1.181, -0.4421] | loss (was undecided) |
| 2020 | mr_cal_c_location_scale against mr_cal_b_location | 251 | +16.5% [+11.0, +23.8] | +0.2473 [+0.1456, +0.4502] | gain |
| 2020 | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 251 | -10.9% [-29.8, +7.3] | -0.1236 [-0.2741, +0.02256] | undecided |
| 2020 | mr_cal_c_location_scale against spread_mr_ctx | 251 | -89.2% [-217.2, +45.4] | -0.5916 [-0.9848, -0.3197] | loss (was undecided) |
| 2020 | mr_cal_d_no_fomc_iorb against B1 | 251 | -52.8% [-195.5, +79.4] | -0.3907 [-0.7575, +0.05342] | undecided |
| 2020 | mr_cal_d_no_fomc_iorb against B1_prime | 251 | -50.4% [-205.5, +92.5] | -0.3789 [-0.77, +0.1359] | undecided |
| 2020 | mr_cal_d_no_fomc_iorb against B2 | 251 | +7.2% [-30.9, +36.0] | +0.08823 [-0.3963, +0.5085] | undecided |
| 2020 | mr_cal_d_no_fomc_iorb against gbm_funding | 251 | -160.0% [-555.4, +98.6] | -0.6958 [-1.058, -0.4376] | loss (was undecided) |
| 2020 | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 251 | -136.2% [-445.2, +91.5] | -0.6521 [-1.014, -0.4073] | loss (was undecided) |
| 2020 | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 251 | -121.4% [-345.3, +38.8] | -0.62 [-0.986, -0.3846] | loss (was undecided) |
| 2020 | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 251 | -70.6% [-169.7, +10.3] | -0.468 [-0.7956, -0.2536] | loss (was undecided) |

### grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2021-23 | mr_cal_a_base against B1 | 748 | +5.5% [-0.6, +10.7] | +0.03824 [-0.0006573, +0.07125] | undecided |
| 2021-23 | mr_cal_a_base against B1_prime | 748 | +1.0% [-5.3, +6.6] | +0.006723 [-0.03569, +0.04244] | undecided |
| 2021-23 | mr_cal_a_base against B2 | 748 | +55.0% [+41.2, +67.7] | +0.8061 [+0.5099, +1.193] | gain |
| 2021-23 | mr_cal_a_base against gbm_funding | 748 | +6.8% [-4.8, +19.4] | +0.0478 [-0.02646, +0.1549] | undecided |
| 2021-23 | mr_cal_a_base against gbm_funding_cal_aligned | 748 | +13.6% [+1.7, +26.8] | +0.1037 [+0.01571, +0.2453] | gain |
| 2021-23 | mr_cal_a_base against spread_mr_ctx | 748 | +8.2% [+2.2, +16.5] | +0.05876 [+0.01731, +0.1108] | gain |
| 2021-23 | mr_cal_b_location against B1 | 748 | -35.3% [-83.3, -11.7] | -0.2464 [-0.5427, -0.09415] | loss |
| 2021-23 | mr_cal_b_location against B1_prime | 748 | -41.7% [-91.9, -16.8] | -0.278 [-0.5727, -0.126] | loss |
| 2021-23 | mr_cal_b_location against B2 | 748 | +35.6% [+24.0, +44.6] | +0.5214 [+0.3204, +0.7528] | gain |
| 2021-23 | mr_cal_b_location against gbm_funding | 748 | -33.5% [-81.4, -3.6] | -0.2369 [-0.5108, -0.05183] | loss |
| 2021-23 | mr_cal_b_location against gbm_funding_cal_aligned | 748 | -23.7% [-68.2, +4.9] | -0.1809 [-0.4548, +0.01906] | undecided |
| 2021-23 | mr_cal_b_location against mr_cal_a_base | 748 | -43.2% [-104.4, -15.2] | -0.2847 [-0.6133, -0.1209] | loss |
| 2021-23 | mr_cal_b_location against spread_mr_ctx | 748 | -31.5% [-74.5, -11.0] | -0.2259 [-0.506, -0.08947] | loss |
| 2021-23 | mr_cal_c_location_scale against B1 | 748 | -21.9% [-52.7, -5.4] | -0.153 [-0.3433, -0.04491] | loss |
| 2021-23 | mr_cal_c_location_scale against B1_prime | 748 | -27.7% [-60.0, -10.2] | -0.1845 [-0.3743, -0.07783] | loss |
| 2021-23 | mr_cal_c_location_scale against B2 | 748 | +42.0% [+33.0, +50.0] | +0.6148 [+0.4069, +0.8752] | gain |
| 2021-23 | mr_cal_c_location_scale against gbm_funding | 748 | -20.3% [-52.5, +3.0] | -0.1434 [-0.3261, +0.006735] | undecided |
| 2021-23 | mr_cal_c_location_scale against gbm_funding_cal_aligned | 748 | -11.5% [-42.0, +10.9] | -0.08747 [-0.2739, +0.08008] | undecided |
| 2021-23 | mr_cal_c_location_scale against mr_cal_a_base | 748 | -29.0% [-70.4, -8.8] | -0.1912 [-0.4136, -0.07242] | loss |
| 2021-23 | mr_cal_c_location_scale against mr_cal_b_location | 748 | +9.9% [+5.2, +17.3] | +0.09347 [+0.04652, +0.1971] | gain |
| 2021-23 | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 748 | -5.4% [-11.5, -1.5] | -0.0432 [-0.09171, -0.01254] | loss |
| 2021-23 | mr_cal_c_location_scale against spread_mr_ctx | 748 | -18.4% [-45.4, -4.7] | -0.1325 [-0.3089, -0.04149] | loss |
| 2021-23 | mr_cal_d_no_fomc_iorb against B1 | 748 | -15.7% [-47.3, -0.9] | -0.1098 [-0.3072, -0.01153] | loss |
| 2021-23 | mr_cal_d_no_fomc_iorb against B1_prime | 748 | -21.2% [-54.3, -5.5] | -0.1413 [-0.3364, -0.04387] | loss |
| 2021-23 | mr_cal_d_no_fomc_iorb against B2 | 748 | +44.9% [+35.6, +53.4] | +0.658 [+0.4387, +0.9361] | gain |
| 2021-23 | mr_cal_d_no_fomc_iorb against gbm_funding | 748 | -14.2% [-46.4, +6.7] | -0.1002 [-0.2822, +0.0403] | undecided |
| 2021-23 | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 748 | -5.8% [-35.3, +14.2] | -0.04428 [-0.2296, +0.1134] | undecided |
| 2021-23 | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 748 | -22.5% [-64.0, -4.2] | -0.148 [-0.3794, -0.03772] | loss |
| 2021-23 | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 748 | -12.4% [-41.0, -0.1] | -0.08926 [-0.2762, -0.005611] | loss |

### upper_tail_twcrps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2021-23 | mr_cal_a_base against B1 | 748 | +12.3% [-64.7, +44.7] | +0.0011 [-0.003833, +0.003384] | undecided |
| 2021-23 | mr_cal_a_base against B1_prime | 748 | -16.5% [-104.4, +16.6] | -0.001111 [-0.009837, +0.001258] | undecided |
| 2021-23 | mr_cal_a_base against B2 | 748 | -156.2% [-785.5, -33.6] | -0.004779 [-0.04788, +0.0004231] | undecided (was loss) |
| 2021-23 | mr_cal_a_base against gbm_funding | 748 | -62.5% [-728.6, +71.3] | -0.003015 [-0.01749, +0.004337] | undecided |
| 2021-23 | mr_cal_a_base against gbm_funding_cal_aligned | 748 | -256.8% [-1262.4, +61.4] | -0.005642 [-0.0371, +0.0001448] | undecided |
| 2021-23 | mr_cal_a_base against spread_mr_ctx | 748 | +54.4% [-42.2, +86.2] | +0.009339 [+0.004547, +0.01604] | gain (was undecided) |
| 2021-23 | mr_cal_b_location against B1 | 748 | -713.2% [-2474.9, -79.9] | -0.06375 [-0.2173, -0.02055] | loss |
| 2021-23 | mr_cal_b_location against B1_prime | 748 | -980.4% [-3524.8, -44.4] | -0.06596 [-0.2207, -0.02251] | loss |
| 2021-23 | mr_cal_b_location against B2 | 748 | -2275.7% [-7583.5, -252.8] | -0.06963 [-0.2259, -0.02512] | loss |
| 2021-23 | mr_cal_b_location against gbm_funding | 748 | -1406.9% [-6280.5, -226.1] | -0.06787 [-0.2258, -0.02245] | loss |
| 2021-23 | mr_cal_b_location against gbm_funding_cal_aligned | 748 | -3208.8% [-13202.3, +667.4] | -0.0705 [-0.2282, -0.02548] | loss (was undecided) |
| 2021-23 | mr_cal_b_location against mr_cal_a_base | 748 | -827.3% [-3634.4, -122.1] | -0.06485 [-0.2215, -0.02205] | loss |
| 2021-23 | mr_cal_b_location against spread_mr_ctx | 748 | -323.2% [-987.8, -99.0] | -0.05551 [-0.2071, -0.01511] | loss |
| 2021-23 | mr_cal_c_location_scale against B1 | 748 | -595.6% [-1611.8, -65.9] | -0.05324 [-0.1372, -0.02189] | loss |
| 2021-23 | mr_cal_c_location_scale against B1_prime | 748 | -824.2% [-2359.4, -22.7] | -0.05545 [-0.1402, -0.02354] | loss |
| 2021-23 | mr_cal_c_location_scale against B2 | 748 | -1932.1% [-5002.5, -236.1] | -0.05912 [-0.1462, -0.02608] | loss |
| 2021-23 | mr_cal_c_location_scale against gbm_funding | 748 | -1189.0% [-4308.9, -222.4] | -0.05736 [-0.1465, -0.02301] | loss |
| 2021-23 | mr_cal_c_location_scale against gbm_funding_cal_aligned | 748 | -2730.3% [-9405.5, +568.8] | -0.05998 [-0.1484, -0.02626] | loss (was undecided) |
| 2021-23 | mr_cal_c_location_scale against mr_cal_a_base | 748 | -693.2% [-2398.9, -101.6] | -0.05434 [-0.1382, -0.02306] | loss |
| 2021-23 | mr_cal_c_location_scale against mr_cal_b_location | 748 | +14.5% [-13.9, +34.7] | +0.01051 [-0.004487, +0.05655] | undecided |
| 2021-23 | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 748 | -28.6% [-113.0, +15.4] | -0.01382 [-0.04682, +0.004598] | undecided |
| 2021-23 | mr_cal_c_location_scale against spread_mr_ctx | 748 | -262.0% [-603.4, -106.0] | -0.045 [-0.123, -0.01631] | loss |
| 2021-23 | mr_cal_d_no_fomc_iorb against B1 | 748 | -441.0% [-1668.3, +2.1] | -0.03942 [-0.1155, -0.01168] | loss (was undecided) |
| 2021-23 | mr_cal_d_no_fomc_iorb against B1_prime | 748 | -618.7% [-2492.6, +37.2] | -0.04163 [-0.1185, -0.01369] | loss (was undecided) |
| 2021-23 | mr_cal_d_no_fomc_iorb against B2 | 748 | -1480.4% [-5171.5, -149.6] | -0.0453 [-0.1205, -0.01695] | loss |
| 2021-23 | mr_cal_d_no_fomc_iorb against gbm_funding | 748 | -902.5% [-3676.1, -138.8] | -0.04353 [-0.1189, -0.01433] | loss |
| 2021-23 | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 748 | -2101.2% [-8450.2, +386.5] | -0.04616 [-0.1214, -0.01756] | loss (was undecided) |
| 2021-23 | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 748 | -516.9% [-2468.2, -12.4] | -0.04052 [-0.1191, -0.01222] | loss |
| 2021-23 | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 748 | -181.5% [-583.8, -14.1] | -0.03118 [-0.1023, -0.005746] | loss |

### grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2024 | mr_cal_a_base against B1 | 250 | +25.3% [+18.5, +35.4] | +0.4088 [+0.1987, +0.9714] | gain |
| 2024 | mr_cal_a_base against B1_prime | 250 | +19.0% [+11.1, +29.6] | +0.2819 [+0.1045, +0.7136] | gain |
| 2024 | mr_cal_a_base against B2 | 250 | +13.6% [+2.9, +23.4] | +0.19 [+0.03487, +0.386] | gain |
| 2024 | mr_cal_a_base against gbm_funding | 250 | +12.7% [+7.8, +18.9] | +0.1748 [+0.07586, +0.423] | gain |
| 2024 | mr_cal_a_base against gbm_funding_cal_aligned | 250 | +7.4% [+2.0, +14.7] | +0.09683 [+0.01375, +0.2752] | gain |
| 2024 | mr_cal_a_base against spread_mr_ctx | 250 | +4.1% [-2.3, +12.4] | +0.0513 [-0.02445, +0.2296] | undecided |
| 2024 | mr_cal_b_location against B1 | 250 | +30.1% [+23.4, +39.0] | +0.4849 [+0.2484, +1.063] | gain |
| 2024 | mr_cal_b_location against B1_prime | 250 | +24.1% [+16.3, +33.5] | +0.358 [+0.1555, +0.811] | gain |
| 2024 | mr_cal_b_location against B2 | 250 | +19.1% [+8.3, +28.3] | +0.2662 [+0.09354, +0.481] | gain |
| 2024 | mr_cal_b_location against gbm_funding | 250 | +18.2% [+12.6, +23.6] | +0.2509 [+0.1231, +0.5151] | gain |
| 2024 | mr_cal_b_location against gbm_funding_cal_aligned | 250 | +13.3% [+7.4, +19.5] | +0.173 [+0.0631, +0.3777] | gain |
| 2024 | mr_cal_b_location against mr_cal_a_base | 250 | +6.3% [+4.0, +8.7] | +0.07613 [+0.03722, +0.1196] | gain |
| 2024 | mr_cal_b_location against spread_mr_ctx | 250 | +10.1% [+3.9, +16.7] | +0.1274 [+0.02723, +0.3357] | gain |
| 2024 | mr_cal_c_location_scale against B1 | 250 | +30.8% [+22.9, +40.2] | +0.4974 [+0.2565, +1.073] | gain |
| 2024 | mr_cal_c_location_scale against B1_prime | 250 | +24.9% [+16.4, +34.2] | +0.3705 [+0.1637, +0.8158] | gain |
| 2024 | mr_cal_c_location_scale against B2 | 250 | +20.0% [+8.5, +29.5] | +0.2787 [+0.1043, +0.4929] | gain |
| 2024 | mr_cal_c_location_scale against gbm_funding | 250 | +19.1% [+12.5, +24.5] | +0.2634 [+0.1338, +0.5258] | gain |
| 2024 | mr_cal_c_location_scale against gbm_funding_cal_aligned | 250 | +14.3% [+7.6, +20.1] | +0.1855 [+0.07308, +0.3791] | gain |
| 2024 | mr_cal_c_location_scale against mr_cal_a_base | 250 | +7.4% [+3.0, +11.1] | +0.08863 [+0.04287, +0.1467] | gain |
| 2024 | mr_cal_c_location_scale against mr_cal_b_location | 250 | +1.1% [-3.2, +4.5] | +0.0125 [-0.02077, +0.04526] | undecided |
| 2024 | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 250 | -0.1% [-0.7, +0.4] | -0.00125 [-0.007703, +0.005053] | undecided |
| 2024 | mr_cal_c_location_scale against spread_mr_ctx | 250 | +11.1% [+6.2, +15.9] | +0.1399 [+0.0454, +0.3286] | gain |
| 2024 | mr_cal_d_no_fomc_iorb against B1 | 250 | +30.9% [+23.0, +40.3] | +0.4987 [+0.2584, +1.075] | gain |
| 2024 | mr_cal_d_no_fomc_iorb against B1_prime | 250 | +25.0% [+16.6, +34.4] | +0.3718 [+0.1649, +0.8164] | gain |
| 2024 | mr_cal_d_no_fomc_iorb against B2 | 250 | +20.1% [+8.9, +29.4] | +0.2799 [+0.1092, +0.4909] | gain |
| 2024 | mr_cal_d_no_fomc_iorb against gbm_funding | 250 | +19.2% [+12.7, +24.5] | +0.2647 [+0.1366, +0.531] | gain |
| 2024 | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 250 | +14.3% [+7.8, +20.2] | +0.1867 [+0.07523, +0.3832] | gain |
| 2024 | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 250 | +7.5% [+3.2, +11.0] | +0.08988 [+0.04681, +0.1461] | gain |
| 2024 | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 250 | +11.2% [+6.4, +15.9] | +0.1412 [+0.04795, +0.3351] | gain |

### upper_tail_twcrps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2024 | mr_cal_a_base against B1 | 250 | +34.6% [+15.9, +102.8] | +0.09708 [+0.003668, +1.045] | gain |
| 2024 | mr_cal_a_base against B1_prime | 250 | +30.5% [+16.1, +72.7] | +0.08036 [+0.003378, +0.7233] | gain |
| 2024 | mr_cal_a_base against gbm_funding | 250 | +12.9% [+7.0, +19.3] | +0.02713 [-0.0007173, +0.2087] | undecided (was gain) |
| 2024 | mr_cal_a_base against gbm_funding_cal_aligned | 250 | +10.4% [+5.7, +16.1] | +0.02129 [-0.002273, +0.2851] | undecided (was gain) |
| 2024 | mr_cal_a_base against spread_mr_ctx | 250 | +9.9% [-2.4, +20.6] | +0.02011 [-0.005431, +0.3951] | undecided |
| 2024 | mr_cal_b_location against B1 | 250 | +35.8% [+14.8, +112.4] | +0.1004 [+0.00789, +1.308] | gain |
| 2024 | mr_cal_b_location against B1_prime | 250 | +31.7% [+15.3, +81.9] | +0.08372 [+0.007495, +0.8854] | gain |
| 2024 | mr_cal_b_location against gbm_funding | 250 | +14.5% [+9.3, +22.4] | +0.03048 [+0.003154, +0.2172] | gain |
| 2024 | mr_cal_b_location against gbm_funding_cal_aligned | 250 | +12.0% [+8.8, +18.6] | +0.02464 [+0.0024, +0.1616] | gain |
| 2024 | mr_cal_b_location against mr_cal_a_base | 250 | +1.8% [-30.2, +6.1] | +0.003354 [-0.003295, +0.007349] | undecided |
| 2024 | mr_cal_b_location against spread_mr_ctx | 250 | +11.5% [+1.6, +31.2] | +0.02347 [-0.001206, +0.7724] | undecided (was gain) |
| 2024 | mr_cal_c_location_scale against B1 | 250 | +38.5% [+13.7, +111.3] | +0.108 [+0.006104, +1.049] | gain |
| 2024 | mr_cal_c_location_scale against B1_prime | 250 | +34.6% [+14.6, +85.9] | +0.09124 [+0.006306, +0.7474] | gain |
| 2024 | mr_cal_c_location_scale against gbm_funding | 250 | +18.1% [+13.0, +24.9] | +0.03801 [+0.003914, +0.3212] | gain |
| 2024 | mr_cal_c_location_scale against gbm_funding_cal_aligned | 250 | +15.7% [+9.4, +26.0] | +0.03217 [+0.002205, +0.236] | gain |
| 2024 | mr_cal_c_location_scale against mr_cal_a_base | 250 | +5.9% [-17.4, +13.8] | +0.01088 [-0.001735, +0.04218] | undecided |
| 2024 | mr_cal_c_location_scale against mr_cal_b_location | 250 | +4.2% [-13.0, +17.9] | +0.007525 [-0.003345, +0.08118] | undecided |
| 2024 | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 250 | -0.1% [-0.4, +0.2] | -0.0001652 [-0.0003827, +0.0001122] | undecided |
| 2024 | mr_cal_c_location_scale against spread_mr_ctx | 250 | +15.2% [+11.4, +23.9] | +0.03099 [+0.001808, +0.7216] | gain |
| 2024 | mr_cal_d_no_fomc_iorb against B1 | 250 | +38.6% [+13.8, +111.5] | +0.1081 [+0.006329, +1.054] | gain |
| 2024 | mr_cal_d_no_fomc_iorb against B1_prime | 250 | +34.7% [+14.3, +86.2] | +0.09141 [+0.006569, +0.7504] | gain |
| 2024 | mr_cal_d_no_fomc_iorb against gbm_funding | 250 | +18.1% [+13.1, +25.0] | +0.03817 [+0.004177, +0.3225] | gain |
| 2024 | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 250 | +15.8% [+9.5, +26.0] | +0.03233 [+0.002425, +0.2354] | gain |
| 2024 | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 250 | +6.0% [-18.4, +13.7] | +0.01104 [-0.001456, +0.04203] | undecided |
| 2024 | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 250 | +15.3% [+11.5, +24.2] | +0.03116 [+0.002031, +0.7482] | gain |

### grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2025-26 | mr_cal_a_base against B1 | 249 | +23.4% [+16.4, +30.4] | +0.7857 [+0.441, +1.27] | gain |
| 2025-26 | mr_cal_a_base against B1_prime | 249 | +16.2% [+9.2, +23.5] | +0.4967 [+0.2255, +0.8785] | gain |
| 2025-26 | mr_cal_a_base against B2 | 249 | +31.9% [+8.4, +52.0] | +1.204 [+0.1648, +3.047] | gain |
| 2025-26 | mr_cal_a_base against gbm_funding | 249 | +9.3% [+1.1, +15.7] | +0.2623 [+0.03383, +0.4969] | gain |
| 2025-26 | mr_cal_a_base against gbm_funding_cal_aligned | 249 | +2.3% [-8.7, +12.6] | +0.06116 [-0.2051, +0.3741] | undecided |
| 2025-26 | mr_cal_a_base against spread_mr_ctx | 249 | +3.5% [-0.8, +7.8] | +0.09389 [-0.01746, +0.2379] | undecided |
| 2025-26 | mr_cal_b_location against B1 | 249 | +31.0% [+24.7, +37.1] | +1.041 [+0.6798, +1.546] | gain |
| 2025-26 | mr_cal_b_location against B1_prime | 249 | +24.5% [+17.9, +31.4] | +0.7522 [+0.4651, +1.168] | gain |
| 2025-26 | mr_cal_b_location against B2 | 249 | +38.7% [+18.6, +54.8] | +1.46 [+0.4337, +3.267] | gain |
| 2025-26 | mr_cal_b_location against gbm_funding | 249 | +18.3% [+10.7, +24.2] | +0.5178 [+0.2844, +0.7512] | gain |
| 2025-26 | mr_cal_b_location against gbm_funding_cal_aligned | 249 | +12.0% [+2.5, +19.5] | +0.3167 [+0.05515, +0.5961] | gain |
| 2025-26 | mr_cal_b_location against mr_cal_a_base | 249 | +9.9% [+6.0, +13.3] | +0.2555 [+0.1718, +0.3459] | gain |
| 2025-26 | mr_cal_b_location against spread_mr_ctx | 249 | +13.1% [+9.4, +16.5] | +0.3494 [+0.2282, +0.4861] | gain |
| 2025-26 | mr_cal_c_location_scale against B1 | 249 | +31.4% [+24.8, +37.8] | +1.054 [+0.6802, +1.586] | gain |
| 2025-26 | mr_cal_c_location_scale against B1_prime | 249 | +24.9% [+18.0, +31.9] | +0.7653 [+0.466, +1.195] | gain |
| 2025-26 | mr_cal_c_location_scale against B2 | 249 | +39.0% [+19.5, +55.3] | +1.473 [+0.4421, +3.309] | gain |
| 2025-26 | mr_cal_c_location_scale against gbm_funding | 249 | +18.7% [+11.4, +24.4] | +0.5309 [+0.2979, +0.7645] | gain |
| 2025-26 | mr_cal_c_location_scale against gbm_funding_cal_aligned | 249 | +12.5% [+3.3, +19.9] | +0.3297 [+0.0706, +0.6092] | gain |
| 2025-26 | mr_cal_c_location_scale against mr_cal_a_base | 249 | +10.4% [+6.4, +14.1] | +0.2686 [+0.1734, +0.3779] | gain |
| 2025-26 | mr_cal_c_location_scale against mr_cal_b_location | 249 | +0.6% [-1.0, +2.4] | +0.01308 [-0.02314, +0.05825] | undecided |
| 2025-26 | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 249 | -0.3% [-0.6, -0.0] | -0.005836 [-0.01499, -0.0008788] | loss |
| 2025-26 | mr_cal_c_location_scale against spread_mr_ctx | 249 | +13.6% [+10.1, +16.8] | +0.3625 [+0.2402, +0.5056] | gain |
| 2025-26 | mr_cal_d_no_fomc_iorb against B1 | 249 | +31.6% [+25.0, +38.0] | +1.06 [+0.684, +1.596] | gain |
| 2025-26 | mr_cal_d_no_fomc_iorb against B1_prime | 249 | +25.1% [+18.2, +32.1] | +0.7712 [+0.4704, +1.203] | gain |
| 2025-26 | mr_cal_d_no_fomc_iorb against B2 | 249 | +39.2% [+19.5, +55.5] | +1.479 [+0.445, +3.333] | gain |
| 2025-26 | mr_cal_d_no_fomc_iorb against gbm_funding | 249 | +18.9% [+11.7, +24.6] | +0.5367 [+0.3019, +0.7717] | gain |
| 2025-26 | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 249 | +12.7% [+3.5, +20.1] | +0.3356 [+0.07428, +0.6197] | gain |
| 2025-26 | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 249 | +10.7% [+6.8, +14.2] | +0.2744 [+0.1807, +0.3825] | gain |
| 2025-26 | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 249 | +13.8% [+10.3, +17.0] | +0.3683 [+0.2436, +0.514] | gain |

### upper_tail_twcrps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2025-26 | mr_cal_a_base against B1 | 249 | +32.3% [+26.2, +39.3] | +0.5183 [+0.1827, +1.229] | gain |
| 2025-26 | mr_cal_a_base against B1_prime | 249 | +22.3% [+14.6, +31.0] | +0.3108 [+0.0912, +0.7208] | gain |
| 2025-26 | mr_cal_a_base against B2 | 249 | +29.6% [+14.2, +48.8] | +0.455 [+0.02351, +2.023] | gain |
| 2025-26 | mr_cal_a_base against gbm_funding | 249 | +10.4% [-1.2, +18.8] | +0.1252 [-0.01166, +0.3832] | undecided |
| 2025-26 | mr_cal_a_base against gbm_funding_cal_aligned | 249 | +4.1% [-12.1, +21.4] | +0.04626 [-0.1008, +0.3555] | undecided |
| 2025-26 | mr_cal_a_base against spread_mr_ctx | 249 | +1.0% [-9.4, +12.4] | +0.01062 [-0.07931, +0.2063] | undecided |
| 2025-26 | mr_cal_b_location against B1 | 249 | +40.1% [+30.9, +47.5] | +0.6422 [+0.2511, +1.42] | gain |
| 2025-26 | mr_cal_b_location against B1_prime | 249 | +31.2% [+21.3, +41.1] | +0.4347 [+0.1688, +0.9381] | gain |
| 2025-26 | mr_cal_b_location against B2 | 249 | +37.6% [+27.9, +48.9] | +0.5789 [+0.1214, +2.055] | gain |
| 2025-26 | mr_cal_b_location against gbm_funding | 249 | +20.6% [+8.4, +28.6] | +0.2491 [+0.07633, +0.5583] | gain |
| 2025-26 | mr_cal_b_location against gbm_funding_cal_aligned | 249 | +15.1% [+3.4, +24.3] | +0.1702 [+0.01726, +0.5262] | gain |
| 2025-26 | mr_cal_b_location against mr_cal_a_base | 249 | +11.4% [+1.9, +19.1] | +0.1239 [+0.05225, +0.2484] | gain |
| 2025-26 | mr_cal_b_location against spread_mr_ctx | 249 | +12.3% [+6.4, +17.5] | +0.1345 [+0.02352, +0.3337] | gain |
| 2025-26 | mr_cal_c_location_scale against B1 | 249 | +40.1% [+30.3, +47.6] | +0.6421 [+0.2469, +1.45] | gain |
| 2025-26 | mr_cal_c_location_scale against B1_prime | 249 | +31.2% [+21.1, +40.3] | +0.4346 [+0.1634, +0.9425] | gain |
| 2025-26 | mr_cal_c_location_scale against B2 | 249 | +37.6% [+28.0, +51.2] | +0.5788 [+0.1178, +2.195] | gain |
| 2025-26 | mr_cal_c_location_scale against gbm_funding | 249 | +20.6% [+10.6, +27.6] | +0.249 [+0.07777, +0.5632] | gain |
| 2025-26 | mr_cal_c_location_scale against gbm_funding_cal_aligned | 249 | +15.0% [+4.8, +24.5] | +0.17 [+0.01946, +0.5565] | gain |
| 2025-26 | mr_cal_c_location_scale against mr_cal_a_base | 249 | +11.4% [+1.0, +18.1] | +0.1238 [+0.04238, +0.2423] | gain |
| 2025-26 | mr_cal_c_location_scale against mr_cal_b_location | 249 | -0.0% [-3.1, +3.2] | -0.0001389 [-0.02691, +0.02976] | undecided |
| 2025-26 | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 249 | -0.5% [-1.3, -0.1] | -0.00439 [-0.02256, -0.000156] | loss |
| 2025-26 | mr_cal_c_location_scale against spread_mr_ctx | 249 | +12.3% [+6.9, +16.6] | +0.1344 [+0.02141, +0.3377] | gain |
| 2025-26 | mr_cal_d_no_fomc_iorb against B1 | 249 | +40.3% [+31.0, +47.8] | +0.6465 [+0.2467, +1.464] | gain |
| 2025-26 | mr_cal_d_no_fomc_iorb against B1_prime | 249 | +31.5% [+21.9, +40.5] | +0.439 [+0.1648, +0.9525] | gain |
| 2025-26 | mr_cal_d_no_fomc_iorb against B2 | 249 | +37.9% [+28.2, +51.9] | +0.5832 [+0.1182, +2.23] | gain |
| 2025-26 | mr_cal_d_no_fomc_iorb against gbm_funding | 249 | +20.9% [+11.3, +27.7] | +0.2534 [+0.07988, +0.5745] | gain |
| 2025-26 | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 249 | +15.4% [+5.3, +25.1] | +0.1744 [+0.02092, +0.5726] | gain |
| 2025-26 | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 249 | +11.8% [+2.0, +18.2] | +0.1282 [+0.0461, +0.2501] | gain |
| 2025-26 | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 249 | +12.7% [+7.1, +17.1] | +0.1388 [+0.02204, +0.354] | gain |

### grid_crps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| calendar_days | mr_cal_a_base against B1 | 1352 | +23.3% [+17.2, +37.7] | +0.5815 [+0.3053, +1.626] | gain |
| calendar_days | mr_cal_a_base against B1_prime | 1352 | +9.8% [+5.1, +15.2] | +0.208 [+0.1108, +0.3586] | gain |
| calendar_days | mr_cal_a_base against B2 | 1352 | +32.5% [+19.7, +43.0] | +0.921 [+0.63, +1.311] | gain |
| calendar_days | mr_cal_a_base against gbm_funding | 1352 | +7.5% [+3.8, +11.3] | +0.1554 [+0.08206, +0.2462] | gain |
| calendar_days | mr_cal_a_base against gbm_funding_cal_aligned | 1352 | +5.4% [+0.6, +10.3] | +0.1094 [+0.0181, +0.2187] | gain |
| calendar_days | mr_cal_a_base against spread_mr_ctx | 1352 | +3.6% [+0.9, +6.5] | +0.0709 [+0.0242, +0.1262] | gain |
| calendar_days | mr_cal_b_location against B1 | 1352 | +8.0% [-8.1, +27.5] | +0.1981 [-0.1683, +0.8922] | undecided |
| calendar_days | mr_cal_b_location against B1_prime | 1352 | -8.3% [-23.7, +3.2] | -0.1755 [-0.4338, +0.07087] | undecided |
| calendar_days | mr_cal_b_location against B2 | 1352 | +19.0% [+8.7, +28.9] | +0.5376 [+0.2398, +0.885] | gain |
| calendar_days | mr_cal_b_location against gbm_funding | 1352 | -11.0% [-27.5, +0.4] | -0.228 [-0.4936, -0.002911] | loss (was undecided) |
| calendar_days | mr_cal_b_location against gbm_funding_cal_aligned | 1352 | -13.6% [-30.5, -1.6] | -0.274 [-0.5315, -0.05007] | loss |
| calendar_days | mr_cal_b_location against mr_cal_a_base | 1352 | -20.1% [-37.9, -7.6] | -0.3834 [-0.6309, -0.1946] | loss |
| calendar_days | mr_cal_b_location against spread_mr_ctx | 1352 | -15.8% [-30.7, -5.3] | -0.3125 [-0.5346, -0.1376] | loss |
| calendar_days | mr_cal_c_location_scale against B1 | 1352 | +13.6% [+0.6, +31.2] | +0.3378 [-0.003526, +1.113] | undecided (was gain) |
| calendar_days | mr_cal_c_location_scale against B1_prime | 1352 | -1.7% [-13.3, +8.1] | -0.03571 [-0.2493, +0.1956] | undecided |
| calendar_days | mr_cal_c_location_scale against B2 | 1352 | +23.9% [+13.8, +33.4] | +0.6774 [+0.3897, +1.034] | gain |
| calendar_days | mr_cal_c_location_scale against gbm_funding | 1352 | -4.3% [-16.6, +4.9] | -0.08826 [-0.3017, +0.1111] | undecided |
| calendar_days | mr_cal_c_location_scale against gbm_funding_cal_aligned | 1352 | -6.7% [-19.6, +3.0] | -0.1343 [-0.3413, +0.06477] | undecided |
| calendar_days | mr_cal_c_location_scale against mr_cal_a_base | 1352 | -12.8% [-26.2, -3.3] | -0.2437 [-0.4332, -0.0903] | loss |
| calendar_days | mr_cal_c_location_scale against mr_cal_b_location | 1352 | +6.1% [+3.8, +8.7] | +0.1398 [+0.09104, +0.2037] | gain |
| calendar_days | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 1352 | -3.6% [-6.4, -1.1] | -0.07487 [-0.1216, -0.03498] | loss |
| calendar_days | mr_cal_c_location_scale against spread_mr_ctx | 1352 | -8.7% [-19.5, -0.7] | -0.1728 [-0.3383, -0.02813] | loss |
| calendar_days | mr_cal_d_no_fomc_iorb against B1 | 1352 | +16.6% [+5.6, +32.2] | +0.4127 [+0.08753, +1.191] | gain |
| calendar_days | mr_cal_d_no_fomc_iorb against B1_prime | 1352 | +1.8% [-7.7, +10.6] | +0.03917 [-0.1525, +0.2499] | undecided |
| calendar_days | mr_cal_d_no_fomc_iorb against B2 | 1352 | +26.6% [+15.8, +36.0] | +0.7522 [+0.4741, +1.115] | gain |
| calendar_days | mr_cal_d_no_fomc_iorb against gbm_funding | 1352 | -0.6% [-10.8, +7.2] | -0.01339 [-0.2028, +0.1671] | undecided |
| calendar_days | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 1352 | -2.9% [-13.3, +5.3] | -0.05941 [-0.2416, +0.1206] | undecided |
| calendar_days | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 1352 | -8.8% [-19.6, -1.4] | -0.1688 [-0.3323, -0.03742] | loss |
| calendar_days | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 1352 | -4.9% [-13.2, +1.3] | -0.09789 [-0.237, +0.02543] | undecided |

### upper_tail_twcrps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| calendar_days | mr_cal_a_base against B1 | 1352 | +31.2% [+24.0, +45.8] | +0.4861 [+0.2119, +1.683] | gain |
| calendar_days | mr_cal_a_base against B1_prime | 1352 | +13.6% [+3.2, +23.0] | +0.1691 [+0.08293, +0.3304] | gain |
| calendar_days | mr_cal_a_base against B2 | 1352 | +21.8% [+5.2, +36.8] | +0.2986 [+0.1519, +0.5107] | gain |
| calendar_days | mr_cal_a_base against gbm_funding | 1352 | +7.7% [+1.7, +13.3] | +0.09001 [+0.0327, +0.1781] | gain |
| calendar_days | mr_cal_a_base against gbm_funding_cal_aligned | 1352 | +5.1% [-2.1, +11.6] | +0.05751 [-0.01079, +0.15] | undecided |
| calendar_days | mr_cal_a_base against spread_mr_ctx | 1352 | +3.1% [-1.0, +7.7] | +0.03476 [-0.0006466, +0.08277] | undecided |
| calendar_days | mr_cal_b_location against B1 | 1352 | +16.7% [-2.7, +39.1] | +0.2597 [-0.07509, +1.053] | undecided |
| calendar_days | mr_cal_b_location against B1_prime | 1352 | -4.6% [-25.7, +9.5] | -0.05726 [-0.2621, +0.1434] | undecided |
| calendar_days | mr_cal_b_location against B2 | 1352 | +5.3% [-10.0, +17.7] | +0.07225 [-0.1275, +0.2874] | undecided |
| calendar_days | mr_cal_b_location against gbm_funding | 1352 | -11.7% [-39.0, +3.7] | -0.1364 [-0.3452, +0.04147] | undecided |
| calendar_days | mr_cal_b_location against gbm_funding_cal_aligned | 1352 | -14.9% [-43.4, +2.0] | -0.1689 [-0.3749, +0.005655] | undecided |
| calendar_days | mr_cal_b_location against mr_cal_a_base | 1352 | -21.1% [-51.9, -2.9] | -0.2264 [-0.4194, -0.08898] | loss |
| calendar_days | mr_cal_b_location against spread_mr_ctx | 1352 | -17.3% [-42.6, -1.7] | -0.1916 [-0.3644, -0.06202] | loss |
| calendar_days | mr_cal_c_location_scale against B1 | 1352 | +21.8% [+6.3, +42.2] | +0.3398 [+0.01169, +1.239] | gain |
| calendar_days | mr_cal_c_location_scale against B1_prime | 1352 | +1.8% [-14.1, +14.5] | +0.02287 [-0.153, +0.2312] | undecided |
| calendar_days | mr_cal_c_location_scale against B2 | 1352 | +11.1% [-2.0, +23.4] | +0.1524 [-0.03112, +0.3768] | undecided |
| calendar_days | mr_cal_c_location_scale against gbm_funding | 1352 | -4.8% [-24.7, +7.8] | -0.05626 [-0.2234, +0.1136] | undecided |
| calendar_days | mr_cal_c_location_scale against gbm_funding_cal_aligned | 1352 | -7.9% [-29.6, +5.8] | -0.08876 [-0.2541, +0.07924] | undecided |
| calendar_days | mr_cal_c_location_scale against mr_cal_a_base | 1352 | -13.6% [-36.3, +0.3] | -0.1463 [-0.293, -0.03019] | loss (was undecided) |
| calendar_days | mr_cal_c_location_scale against mr_cal_b_location | 1352 | +6.2% [+2.5, +10.2] | +0.08013 [+0.04445, +0.1331] | gain |
| calendar_days | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 1352 | -3.4% [-8.4, +0.9] | -0.04042 [-0.08156, -0.002144] | loss (was undecided) |
| calendar_days | mr_cal_c_location_scale against spread_mr_ctx | 1352 | -10.1% [-28.4, +2.0] | -0.1115 [-0.238, +0.002164] | undecided |
| calendar_days | mr_cal_d_no_fomc_iorb against B1 | 1352 | +24.4% [+11.8, +42.7] | +0.3802 [+0.06572, +1.307] | gain |
| calendar_days | mr_cal_d_no_fomc_iorb against B1_prime | 1352 | +5.1% [-7.7, +16.6] | +0.0633 [-0.08979, +0.2549] | undecided |
| calendar_days | mr_cal_d_no_fomc_iorb against B2 | 1352 | +14.1% [+0.9, +27.4] | +0.1928 [+0.02746, +0.4185] | gain |
| calendar_days | mr_cal_d_no_fomc_iorb against gbm_funding | 1352 | -1.4% [-16.5, +9.1] | -0.01584 [-0.1604, +0.1392] | undecided |
| calendar_days | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 1352 | -4.3% [-20.7, +7.2] | -0.04834 [-0.1891, +0.1075] | undecided |
| calendar_days | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 1352 | -9.9% [-27.7, +0.5] | -0.1058 [-0.2287, -0.007683] | loss (was undecided) |
| calendar_days | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 1352 | -6.4% [-19.6, +2.6] | -0.07109 [-0.1742, +0.02606] | undecided |

### grid_crps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| dom_19_23 | mr_cal_a_base against B1 | 305 | +36.4% [+6.2, +142.4] | +0.7708 [+0.05157, +7.829] | gain |
| dom_19_23 | mr_cal_a_base against B1_prime | 305 | -1.4% [-19.2, +24.7] | -0.01811 [-0.2127, +0.3056] | undecided |
| dom_19_23 | mr_cal_a_base against B2 | 305 | +30.5% [+4.3, +49.8] | +0.591 [+0.1196, +1.169] | gain |
| dom_19_23 | mr_cal_a_base against gbm_funding | 305 | -12.4% [-38.7, +4.9] | -0.1479 [-0.4693, +0.04889] | undecided |
| dom_19_23 | mr_cal_a_base against gbm_funding_cal_aligned | 305 | -8.4% [-34.1, +12.1] | -0.1046 [-0.3985, +0.1352] | undecided |
| dom_19_23 | mr_cal_a_base against spread_mr_ctx | 305 | -1.8% [-6.5, +2.3] | -0.0236 [-0.08888, +0.03194] | undecided |
| dom_19_23 | mr_cal_b_location against B1 | 305 | +32.5% [-1.4, +102.8] | +0.6886 [-0.05475, +4.862] | undecided |
| dom_19_23 | mr_cal_b_location against B1_prime | 305 | -7.6% [-28.8, +12.8] | -0.1004 [-0.3278, +0.1591] | undecided |
| dom_19_23 | mr_cal_b_location against B2 | 305 | +26.3% [+6.1, +40.8] | +0.5087 [+0.1323, +0.9678] | gain |
| dom_19_23 | mr_cal_b_location against gbm_funding | 305 | -19.2% [-49.1, +4.0] | -0.2302 [-0.5589, +0.04132] | undecided |
| dom_19_23 | mr_cal_b_location against gbm_funding_cal_aligned | 305 | -15.1% [-45.1, +10.2] | -0.1869 [-0.5124, +0.1216] | undecided |
| dom_19_23 | mr_cal_b_location against mr_cal_a_base | 305 | -6.1% [-30.0, +8.6] | -0.0823 [-0.3634, +0.1256] | undecided |
| dom_19_23 | mr_cal_b_location against spread_mr_ctx | 305 | -8.0% [-29.1, +6.7] | -0.1059 [-0.3503, +0.09223] | undecided |
| dom_19_23 | mr_cal_c_location_scale against B1 | 305 | +35.2% [+2.6, +108.0] | +0.7442 [-0.004407, +5.402] | undecided (was gain) |
| dom_19_23 | mr_cal_c_location_scale against B1_prime | 305 | -3.4% [-21.1, +15.8] | -0.04475 [-0.2398, +0.2122] | undecided |
| dom_19_23 | mr_cal_c_location_scale against B2 | 305 | +29.1% [+7.9, +43.4] | +0.5644 [+0.1736, +1.03] | gain |
| dom_19_23 | mr_cal_c_location_scale against gbm_funding | 305 | -14.6% [-40.9, +7.2] | -0.1745 [-0.4626, +0.08022] | undecided |
| dom_19_23 | mr_cal_c_location_scale against gbm_funding_cal_aligned | 305 | -10.6% [-36.9, +13.4] | -0.1313 [-0.417, +0.1627] | undecided |
| dom_19_23 | mr_cal_c_location_scale against mr_cal_a_base | 305 | -2.0% [-20.9, +11.2] | -0.02663 [-0.2533, +0.1658] | undecided |
| dom_19_23 | mr_cal_c_location_scale against mr_cal_b_location | 305 | +3.9% [+1.0, +8.4] | +0.05566 [+0.01575, +0.1283] | gain |
| dom_19_23 | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 305 | +0.8% [-2.5, +4.5] | +0.01092 [-0.03071, +0.06343] | undecided |
| dom_19_23 | mr_cal_c_location_scale against spread_mr_ctx | 305 | -3.8% [-20.7, +9.6] | -0.05024 [-0.2493, +0.1344] | undecided |
| dom_19_23 | mr_cal_d_no_fomc_iorb against B1 | 305 | +34.7% [+2.1, +102.0] | +0.7333 [-0.005644, +5.029] | undecided (was gain) |
| dom_19_23 | mr_cal_d_no_fomc_iorb against B1_prime | 305 | -4.2% [-24.5, +15.3] | -0.05567 [-0.2766, +0.2007] | undecided |
| dom_19_23 | mr_cal_d_no_fomc_iorb against B2 | 305 | +28.6% [+7.4, +42.3] | +0.5535 [+0.1687, +1.002] | gain |
| dom_19_23 | mr_cal_d_no_fomc_iorb against gbm_funding | 305 | -15.5% [-45.2, +6.8] | -0.1855 [-0.5117, +0.07855] | undecided |
| dom_19_23 | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 305 | -11.5% [-41.1, +12.7] | -0.1422 [-0.4648, +0.1542] | undecided |
| dom_19_23 | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 305 | -2.8% [-24.3, +11.0] | -0.03755 [-0.2981, +0.1627] | undecided |
| dom_19_23 | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 305 | -4.6% [-23.6, +9.3] | -0.06116 [-0.2866, +0.1315] | undecided |

### upper_tail_twcrps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| dom_19_23 | mr_cal_a_base against B1 | 305 | +60.0% [+29.5, +128.6] | +0.784 [+0.07714, +10.82] | gain |
| dom_19_23 | mr_cal_a_base against B1_prime | 305 | +9.0% [-33.6, +52.4] | +0.05201 [-0.1086, +0.3087] | undecided |
| dom_19_23 | mr_cal_a_base against B2 | 305 | -12.7% [-83.0, +30.6] | -0.05903 [-0.3427, +0.1143] | undecided |
| dom_19_23 | mr_cal_a_base against gbm_funding | 305 | -50.0% [-132.5, -8.1] | -0.1743 [-0.7725, -0.03453] | loss |
| dom_19_23 | mr_cal_a_base against gbm_funding_cal_aligned | 305 | -47.2% [-112.0, -4.9] | -0.1678 [-0.6223, -0.03092] | loss |
| dom_19_23 | mr_cal_a_base against spread_mr_ctx | 305 | -7.4% [-12.9, -3.0] | -0.03607 [-0.07227, -0.01364] | loss |
| dom_19_23 | mr_cal_b_location against B1 | 305 | +67.2% [+43.1, +114.1] | +0.8784 [+0.1289, +9.586] | gain |
| dom_19_23 | mr_cal_b_location against B1_prime | 305 | +25.5% [-7.5, +58.3] | +0.1464 [+0.008901, +0.4764] | gain (was undecided) |
| dom_19_23 | mr_cal_b_location against B2 | 305 | +7.6% [-47.2, +40.5] | +0.0354 [-0.1402, +0.1914] | undecided |
| dom_19_23 | mr_cal_b_location against gbm_funding | 305 | -22.9% [-94.5, +6.6] | -0.07985 [-0.3899, +0.01029] | undecided |
| dom_19_23 | mr_cal_b_location against gbm_funding_cal_aligned | 305 | -20.6% [-75.6, +9.7] | -0.07334 [-0.2964, +0.01649] | undecided |
| dom_19_23 | mr_cal_b_location against mr_cal_a_base | 305 | +18.1% [+10.4, +25.4] | +0.09443 [+0.02404, +0.2287] | gain |
| dom_19_23 | mr_cal_b_location against spread_mr_ctx | 305 | +12.0% [+1.6, +21.6] | +0.05836 [-0.0008313, +0.1762] | undecided (was gain) |
| dom_19_23 | mr_cal_c_location_scale against B1 | 305 | +67.3% [+43.5, +110.1] | +0.8798 [+0.1339, +9.365] | gain |
| dom_19_23 | mr_cal_c_location_scale against B1_prime | 305 | +25.7% [-10.0, +59.4] | +0.1478 [+0.00415, +0.4782] | gain (was undecided) |
| dom_19_23 | mr_cal_c_location_scale against B2 | 305 | +7.9% [-50.7, +41.9] | +0.03678 [-0.1497, +0.1963] | undecided |
| dom_19_23 | mr_cal_c_location_scale against gbm_funding | 305 | -22.5% [-102.4, +8.1] | -0.07847 [-0.4162, +0.01654] | undecided |
| dom_19_23 | mr_cal_c_location_scale against gbm_funding_cal_aligned | 305 | -20.3% [-81.9, +11.7] | -0.07196 [-0.3172, +0.02314] | undecided |
| dom_19_23 | mr_cal_c_location_scale against mr_cal_a_base | 305 | +18.3% [+9.5, +26.9] | +0.09581 [+0.02683, +0.2237] | gain |
| dom_19_23 | mr_cal_c_location_scale against mr_cal_b_location | 305 | +0.3% [-2.8, +3.7] | +0.001378 [-0.0122, +0.01232] | undecided |
| dom_19_23 | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 305 | +2.2% [-1.8, +7.9] | +0.009482 [-0.006217, +0.03965] | undecided |
| dom_19_23 | mr_cal_c_location_scale against spread_mr_ctx | 305 | +12.3% [+1.1, +23.3] | +0.05974 [+0.000746, +0.1741] | gain |
| dom_19_23 | mr_cal_d_no_fomc_iorb against B1 | 305 | +66.6% [+44.0, +105.9] | +0.8703 [+0.1335, +8.815] | gain |
| dom_19_23 | mr_cal_d_no_fomc_iorb against B1_prime | 305 | +24.1% [-14.2, +55.5] | +0.1383 [-0.01027, +0.4359] | undecided |
| dom_19_23 | mr_cal_d_no_fomc_iorb against B2 | 305 | +5.9% [-60.8, +39.2] | +0.0273 [-0.1819, +0.1788] | undecided |
| dom_19_23 | mr_cal_d_no_fomc_iorb against gbm_funding | 305 | -25.2% [-119.8, +9.6] | -0.08795 [-0.4666, +0.01641] | undecided |
| dom_19_23 | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 305 | -22.9% [-95.4, +12.2] | -0.08144 [-0.3613, +0.02217] | undecided |
| dom_19_23 | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 305 | +16.5% [+5.9, +26.6] | +0.08633 [+0.01451, +0.2067] | gain |
| dom_19_23 | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 305 | +10.3% [-3.0, +23.0] | +0.05026 [-0.01275, +0.1601] | undecided |

### grid_crps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| fomc_day | mr_cal_a_base against B1 | 118 | +4.0% [-1.2, +10.0] | +0.1822 [+0.03228, +0.4005] | gain (was undecided) |
| fomc_day | mr_cal_a_base against B1_prime | 118 | +2.9% [+1.0, +4.9] | +0.1323 [-0.006994, +0.407] | undecided (was gain) |
| fomc_day | mr_cal_a_base against B2 | 118 | +20.0% [-15.1, +40.7] | +1.098 [+0.4646, +1.866] | gain (was undecided) |
| fomc_day | mr_cal_a_base against gbm_funding | 118 | +4.4% [+2.3, +6.3] | +0.2005 [+0.01436, +0.716] | gain |
| fomc_day | mr_cal_a_base against gbm_funding_cal_aligned | 118 | +1.8% [-1.3, +4.6] | +0.08147 [-0.06166, +0.3288] | undecided |
| fomc_day | mr_cal_a_base against spread_mr_ctx | 118 | +1.7% [-4.3, +5.7] | +0.07454 [-0.07607, +0.1853] | undecided |
| fomc_day | mr_cal_b_location against B1 | 118 | -50.3% [-281.5, +24.1] | -2.307 [-9.07, +0.07826] | undecided |
| fomc_day | mr_cal_b_location against B1_prime | 118 | -52.0% [-287.5, +28.4] | -2.357 [-9.315, -0.03955] | loss (was undecided) |
| fomc_day | mr_cal_b_location against B2 | 118 | -25.3% [-137.6, +19.1] | -1.391 [-6.225, +0.5655] | undecided |
| fomc_day | mr_cal_b_location against gbm_funding | 118 | -49.7% [-280.9, +27.6] | -2.288 [-9.308, +0.01809] | undecided |
| fomc_day | mr_cal_b_location against gbm_funding_cal_aligned | 118 | -53.7% [-283.4, +26.9] | -2.407 [-9.262, -0.07806] | loss (was undecided) |
| fomc_day | mr_cal_b_location against mr_cal_a_base | 118 | -56.6% [-290.6, +29.5] | -2.489 [-9.038, -0.1679] | loss (was undecided) |
| fomc_day | mr_cal_b_location against spread_mr_ctx | 118 | -54.0% [-268.4, +29.0] | -2.414 [-8.651, -0.1251] | loss (was undecided) |
| fomc_day | mr_cal_c_location_scale against B1 | 118 | -36.4% [-189.1, +19.5] | -1.666 [-6.355, +0.05532] | undecided |
| fomc_day | mr_cal_c_location_scale against B1_prime | 118 | -37.9% [-193.5, +23.1] | -1.716 [-6.503, -0.0702] | loss (was undecided) |
| fomc_day | mr_cal_c_location_scale against B2 | 118 | -13.6% [-77.0, +14.6] | -0.7503 [-3.499, +0.591] | undecided |
| fomc_day | mr_cal_c_location_scale against gbm_funding | 118 | -35.8% [-187.2, +22.8] | -1.648 [-6.345, +0.0164] | undecided |
| fomc_day | mr_cal_c_location_scale against gbm_funding_cal_aligned | 118 | -39.4% [-188.1, +21.4] | -1.767 [-6.41, -0.09493] | loss (was undecided) |
| fomc_day | mr_cal_c_location_scale against mr_cal_a_base | 118 | -42.0% [-191.0, +23.6] | -1.848 [-6.439, -0.1799] | loss (was undecided) |
| fomc_day | mr_cal_c_location_scale against mr_cal_b_location | 118 | +9.3% [-8.1, +33.6] | +0.6407 [-0.02034, +2.4] | undecided |
| fomc_day | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 118 | -26.6% [-88.2, +24.8] | -1.314 [-4.437, -0.1836] | loss (was undecided) |
| fomc_day | mr_cal_c_location_scale against spread_mr_ctx | 118 | -39.6% [-173.7, +22.8] | -1.774 [-6.059, -0.139] | loss (was undecided) |
| fomc_day | mr_cal_d_no_fomc_iorb against B1 | 118 | -7.7% [-55.5, +7.2] | -0.3516 [-2.375, +0.2507] | undecided |
| fomc_day | mr_cal_d_no_fomc_iorb against B1_prime | 118 | -8.9% [-78.4, +8.7] | -0.4016 [-2.53, +0.1643] | undecided |
| fomc_day | mr_cal_d_no_fomc_iorb against B2 | 118 | +10.3% [-4.4, +19.8] | +0.5639 [-0.07889, +1.214] | undecided |
| fomc_day | mr_cal_d_no_fomc_iorb against gbm_funding | 118 | -7.2% [-70.9, +10.1] | -0.3333 [-1.86, +0.2926] | undecided |
| fomc_day | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 118 | -10.1% [-68.5, +8.8] | -0.4524 [-1.985, +0.1257] | undecided |
| fomc_day | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 118 | -12.1% [-87.1, +6.8] | -0.5339 [-2.48, -0.01257] | loss (was undecided) |
| fomc_day | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 118 | -10.3% [-59.1, +5.2] | -0.4594 [-1.905, +0.01737] | undecided |

### upper_tail_twcrps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| fomc_day | mr_cal_a_base against B1 | 118 | +2.3% [-0.3, +4.5] | +0.0818 [+0.01097, +0.3687] | gain (was undecided) |
| fomc_day | mr_cal_a_base against B1_prime | 118 | +2.8% [+1.3, +4.8] | +0.1021 [+0.002014, +0.7973] | gain |
| fomc_day | mr_cal_a_base against B2 | 118 | +11.5% [-13.6, +24.9] | +0.4614 [+0.07378, +1.293] | gain (was undecided) |
| fomc_day | mr_cal_a_base against gbm_funding | 118 | +5.4% [+2.5, +8.7] | +0.2027 [+0.007342, +1.461] | gain |
| fomc_day | mr_cal_a_base against gbm_funding_cal_aligned | 118 | +3.2% [-0.3, +6.2] | +0.1171 [-0.005491, +0.5128] | undecided |
| fomc_day | mr_cal_a_base against spread_mr_ctx | 118 | +1.0% [-6.7, +4.3] | +0.03742 [-0.07342, +0.1197] | undecided |
| fomc_day | mr_cal_b_location against B1 | 118 | -43.8% [-309.4, +20.4] | -1.59 [-8.491, -0.00864] | loss (was undecided) |
| fomc_day | mr_cal_b_location against B1_prime | 118 | -43.0% [-310.2, +21.1] | -1.57 [-8.508, -0.01744] | loss (was undecided) |
| fomc_day | mr_cal_b_location against B2 | 118 | -30.2% [-224.8, +25.0] | -1.21 [-6.136, +0.2655] | undecided |
| fomc_day | mr_cal_b_location against gbm_funding | 118 | -39.2% [-312.8, +15.9] | -1.469 [-8.056, +0.08572] | undecided |
| fomc_day | mr_cal_b_location against gbm_funding_cal_aligned | 118 | -42.4% [-309.2, +14.4] | -1.555 [-8.314, +0.02174] | undecided |
| fomc_day | mr_cal_b_location against mr_cal_a_base | 118 | -47.1% [-322.0, +23.0] | -1.672 [-8.697, -0.07707] | loss (was undecided) |
| fomc_day | mr_cal_b_location against spread_mr_ctx | 118 | -45.6% [-301.5, +29.8] | -1.634 [-8.342, -0.07027] | loss (was undecided) |
| fomc_day | mr_cal_c_location_scale against B1 | 118 | -31.2% [-214.8, +18.0] | -1.134 [-5.877, +0.02017] | undecided |
| fomc_day | mr_cal_c_location_scale against B1_prime | 118 | -30.5% [-212.5, +19.2] | -1.114 [-5.783, +0.02289] | undecided |
| fomc_day | mr_cal_c_location_scale against B2 | 118 | -18.8% [-145.9, +21.1] | -0.7546 [-3.651, +0.3549] | undecided |
| fomc_day | mr_cal_c_location_scale against gbm_funding | 118 | -27.0% [-215.3, +15.1] | -1.013 [-5.164, +0.1458] | undecided |
| fomc_day | mr_cal_c_location_scale against gbm_funding_cal_aligned | 118 | -30.0% [-213.9, +13.2] | -1.099 [-5.603, +0.06527] | undecided |
| fomc_day | mr_cal_c_location_scale against mr_cal_a_base | 118 | -34.3% [-213.8, +20.5] | -1.216 [-6.063, -0.05556] | loss (was undecided) |
| fomc_day | mr_cal_c_location_scale against mr_cal_b_location | 118 | +8.7% [-14.9, +31.6] | +0.4557 [+0.01189, +2.048] | gain (was undecided) |
| fomc_day | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 118 | -21.2% [-95.2, +39.4] | -0.8345 [-4.153, -0.03258] | loss (was undecided) |
| fomc_day | mr_cal_c_location_scale against spread_mr_ctx | 118 | -32.9% [-203.9, +24.4] | -1.179 [-5.967, -0.05176] | loss (was undecided) |
| fomc_day | mr_cal_d_no_fomc_iorb against B1 | 118 | -8.3% [-86.3, +7.2] | -0.2996 [-1.946, +0.09946] | undecided |
| fomc_day | mr_cal_d_no_fomc_iorb against B1_prime | 118 | -7.7% [-99.7, +8.1] | -0.2794 [-1.748, +0.1322] | undecided |
| fomc_day | mr_cal_d_no_fomc_iorb against B2 | 118 | +2.0% [-15.2, +10.6] | +0.07992 [-0.6131, +0.7235] | undecided |
| fomc_day | mr_cal_d_no_fomc_iorb against gbm_funding | 118 | -4.8% [-71.2, +8.7] | -0.1788 [-1.239, +0.333] | undecided |
| fomc_day | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 118 | -7.2% [-78.4, +7.0] | -0.2644 [-1.51, +0.1818] | undecided |
| fomc_day | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 118 | -10.8% [-97.1, +6.7] | -0.3814 [-2.015, -0.002082] | loss (was undecided) |
| fomc_day | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 118 | -9.6% [-89.5, +6.7] | -0.344 [-1.899, -0.002983] | loss (was undecided) |

### grid_crps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| iorb_window | mr_cal_a_base against B1 | 78 | +52.7% [+18.3, +220.0] | +2.688 [-0.06602, +67.87] | undecided (was gain) |
| iorb_window | mr_cal_a_base against B1_prime | 78 | -22.4% [-95.6, -3.9] | -0.4415 [-2.229, -0.06283] | loss |
| iorb_window | mr_cal_a_base against B2 | 78 | +33.8% [-18.5, +55.1] | +1.23 [+0.1547, +2.928] | gain (was undecided) |
| iorb_window | mr_cal_a_base against gbm_funding | 78 | -3.4% [-63.4, +21.4] | -0.08001 [-1.172, +0.4822] | undecided |
| iorb_window | mr_cal_a_base against gbm_funding_cal_aligned | 78 | -0.2% [-64.5, +27.6] | -0.00507 [-1.156, +0.6745] | undecided |
| iorb_window | mr_cal_a_base against spread_mr_ctx | 78 | +1.2% [-7.9, +7.4] | +0.0286 [-0.17, +0.1843] | undecided |
| iorb_window | mr_cal_b_location against B1 | 78 | +52.3% [+17.8, +143.9] | +2.668 [-0.07469, +34.71] | undecided (was gain) |
| iorb_window | mr_cal_b_location against B1_prime | 78 | -23.4% [-118.4, +5.6] | -0.4609 [-2.587, +0.03061] | undecided |
| iorb_window | mr_cal_b_location against B2 | 78 | +33.3% [-23.8, +62.2] | +1.211 [+0.0116, +3.335] | gain (was undecided) |
| iorb_window | mr_cal_b_location against gbm_funding | 78 | -4.3% [-76.4, +25.8] | -0.09944 [-1.225, +0.5759] | undecided |
| iorb_window | mr_cal_b_location against gbm_funding_cal_aligned | 78 | -1.0% [-72.8, +31.1] | -0.0245 [-1.185, +0.7591] | undecided |
| iorb_window | mr_cal_b_location against mr_cal_a_base | 78 | -0.8% [-46.0, +11.4] | -0.01943 [-0.8844, +0.3083] | undecided |
| iorb_window | mr_cal_b_location against spread_mr_ctx | 78 | +0.4% [-25.2, +10.6] | +0.009171 [-0.5056, +0.2863] | undecided |
| iorb_window | mr_cal_c_location_scale against B1 | 78 | +53.4% [+21.4, +149.6] | +2.721 [-0.0193, +38.86] | undecided (was gain) |
| iorb_window | mr_cal_c_location_scale against B1_prime | 78 | -20.7% [-96.1, +8.0] | -0.4078 [-1.99, +0.06357] | undecided |
| iorb_window | mr_cal_c_location_scale against B2 | 78 | +34.7% [-18.3, +63.5] | +1.264 [+0.0657, +3.463] | gain (was undecided) |
| iorb_window | mr_cal_c_location_scale against gbm_funding | 78 | -2.0% [-66.1, +27.6] | -0.0463 [-1.053, +0.6291] | undecided |
| iorb_window | mr_cal_c_location_scale against gbm_funding_cal_aligned | 78 | +1.2% [-66.2, +32.9] | +0.02864 [-1.061, +0.8145] | undecided |
| iorb_window | mr_cal_c_location_scale against mr_cal_a_base | 78 | +1.4% [-25.7, +12.3] | +0.03371 [-0.503, +0.3389] | undecided |
| iorb_window | mr_cal_c_location_scale against mr_cal_b_location | 78 | +2.2% [-1.9, +7.7] | +0.05314 [-0.03482, +0.2006] | undecided |
| iorb_window | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 78 | +1.2% [-2.0, +6.1] | +0.02809 [-0.04303, +0.174] | undecided |
| iorb_window | mr_cal_c_location_scale against spread_mr_ctx | 78 | +2.6% [-17.2, +11.4] | +0.06231 [-0.3027, +0.31] | undecided |
| iorb_window | mr_cal_d_no_fomc_iorb against B1 | 78 | +52.8% [+22.4, +143.0] | +2.693 [-0.001419, +36.92] | undecided (was gain) |
| iorb_window | mr_cal_d_no_fomc_iorb against B1_prime | 78 | -22.1% [-115.5, +8.6] | -0.4359 [-2.368, +0.08457] | undecided |
| iorb_window | mr_cal_d_no_fomc_iorb against B2 | 78 | +34.0% [-26.4, +63.7] | +1.236 [-0.01754, +3.393] | undecided |
| iorb_window | mr_cal_d_no_fomc_iorb against gbm_funding | 78 | -3.2% [-80.7, +27.7] | -0.07439 [-1.248, +0.6248] | undecided |
| iorb_window | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 78 | +0.0% [-79.6, +32.8] | +0.000553 [-1.251, +0.8047] | undecided |
| iorb_window | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 78 | +0.2% [-30.3, +12.8] | +0.005623 [-0.5418, +0.3354] | undecided |
| iorb_window | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 78 | +1.4% [-20.6, +12.7] | +0.03422 [-0.3482, +0.3219] | undecided |

### upper_tail_twcrps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| iorb_window | mr_cal_c_location_scale against B1 | 78 | +66.4% [+44.9, +125.2] | +2.834 [+0.05355, +55.64] | gain |
| iorb_window | mr_cal_c_location_scale against B1_prime | 78 | -16.4% [-302.6, +23.7] | -0.2024 [-1.825, +0.2055] | undecided |
| iorb_window | mr_cal_c_location_scale against gbm_funding | 78 | -5.5% [-294.9, +44.3] | -0.07522 [-0.9806, +0.4239] | undecided |
| iorb_window | mr_cal_c_location_scale against gbm_funding_cal_aligned | 78 | -5.3% [-284.0, +46.1] | -0.07194 [-1.053, +0.4646] | undecided |
| iorb_window | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 78 | +5.9% [+0.3, +20.0] | +0.09045 [-0.006357, +0.5773] | undecided (was gain) |
| iorb_window | mr_cal_c_location_scale against spread_mr_ctx | 78 | +9.3% [-5.2, +17.6] | +0.1473 [+0.01168, +0.4191] | gain (was undecided) |
| iorb_window | mr_cal_d_no_fomc_iorb against B1 | 78 | +64.3% [+42.9, +112.1] | +2.744 [+0.02769, +49.37] | gain |
| iorb_window | mr_cal_d_no_fomc_iorb against B1_prime | 78 | -23.8% [-352.7, +25.5] | -0.2929 [-2.422, +0.1971] | undecided |
| iorb_window | mr_cal_d_no_fomc_iorb against gbm_funding | 78 | -12.2% [-364.4, +49.3] | -0.1657 [-1.357, +0.4129] | undecided |
| iorb_window | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 78 | -11.9% [-342.0, +51.0] | -0.1624 [-1.44, +0.4513] | undecided |
| iorb_window | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 78 | +3.6% [-25.2, +17.9] | +0.0568 [-0.1179, +0.3166] | undecided |

### grid_crps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| month_end | mr_cal_a_base against B1 | 180 | +12.3% [+7.7, +16.1] | +0.3723 [+0.1504, +0.6945] | gain |
| month_end | mr_cal_a_base against B1_prime | 180 | +7.9% [+3.9, +11.7] | +0.229 [+0.07491, +0.4613] | gain |
| month_end | mr_cal_a_base against B2 | 180 | +28.1% [+3.6, +49.4] | +1.039 [+0.3282, +2.188] | gain |
| month_end | mr_cal_a_base against gbm_funding | 180 | +14.8% [+11.1, +18.5] | +0.4626 [+0.1846, +0.9592] | gain |
| month_end | mr_cal_a_base against gbm_funding_cal_aligned | 180 | +0.3% [-10.0, +9.8] | +0.008952 [-0.2426, +0.2622] | undecided |
| month_end | mr_cal_a_base against spread_mr_ctx | 180 | +6.6% [-5.7, +21.0] | +0.1874 [-0.1331, +0.5677] | undecided |
| month_end | mr_cal_b_location against B1 | 180 | +5.6% [-51.5, +26.9] | +0.1714 [-1.006, +1.091] | undecided |
| month_end | mr_cal_b_location against B1_prime | 180 | +1.0% [-54.5, +22.7] | +0.02808 [-1.023, +0.8333] | undecided |
| month_end | mr_cal_b_location against B2 | 180 | +22.7% [+7.9, +35.5] | +0.8385 [+0.2766, +1.658] | gain |
| month_end | mr_cal_b_location against gbm_funding | 180 | +8.4% [-45.0, +29.6] | +0.2616 [-0.882, +1.294] | undecided |
| month_end | mr_cal_b_location against gbm_funding_cal_aligned | 180 | -7.2% [-49.7, +18.6] | -0.192 [-0.9972, +0.4929] | undecided |
| month_end | mr_cal_b_location against mr_cal_a_base | 180 | -7.6% [-68.0, +17.2] | -0.201 [-1.335, +0.5208] | undecided |
| month_end | mr_cal_b_location against spread_mr_ctx | 180 | -0.5% [-30.8, +14.6] | -0.01356 [-0.6394, +0.45] | undecided |
| month_end | mr_cal_c_location_scale against B1 | 180 | +10.9% [-37.8, +29.7] | +0.3306 [-0.6779, +1.271] | undecided |
| month_end | mr_cal_c_location_scale against B1_prime | 180 | +6.5% [-39.5, +25.6] | +0.1873 [-0.6849, +1.009] | undecided |
| month_end | mr_cal_c_location_scale against B2 | 180 | +27.0% [+13.5, +38.3] | +0.9978 [+0.4265, +1.885] | gain |
| month_end | mr_cal_c_location_scale against gbm_funding | 180 | +13.5% [-32.4, +32.3] | +0.4209 [-0.5911, +1.487] | undecided |
| month_end | mr_cal_c_location_scale against gbm_funding_cal_aligned | 180 | -1.2% [-35.2, +22.2] | -0.03277 [-0.6688, +0.6584] | undecided |
| month_end | mr_cal_c_location_scale against mr_cal_a_base | 180 | -1.6% [-52.2, +20.4] | -0.04172 [-0.9684, +0.6686] | undecided |
| month_end | mr_cal_c_location_scale against mr_cal_b_location | 180 | +5.6% [+2.7, +8.2] | +0.1592 [+0.06799, +0.3068] | gain |
| month_end | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 180 | -0.5% [-6.8, +2.7] | -0.01465 [-0.1782, +0.06818] | undecided |
| month_end | mr_cal_c_location_scale against spread_mr_ctx | 180 | +5.1% [-16.9, +18.3] | +0.1457 [-0.3079, +0.63] | undecided |
| month_end | mr_cal_d_no_fomc_iorb against B1 | 180 | +11.4% [-37.6, +30.3] | +0.3453 [-0.6821, +1.309] | undecided |
| month_end | mr_cal_d_no_fomc_iorb against B1_prime | 180 | +7.0% [-39.5, +26.5] | +0.202 [-0.6929, +1.061] | undecided |
| month_end | mr_cal_d_no_fomc_iorb against B2 | 180 | +27.4% [+13.0, +38.7] | +1.012 [+0.3835, +1.913] | gain |
| month_end | mr_cal_d_no_fomc_iorb against gbm_funding | 180 | +13.9% [-32.7, +32.9] | +0.4355 [-0.6058, +1.525] | undecided |
| month_end | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 180 | -0.7% [-37.4, +21.0] | -0.01812 [-0.6923, +0.6558] | undecided |
| month_end | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 180 | -1.0% [-54.8, +20.7] | -0.02707 [-0.9848, +0.6973] | undecided |
| month_end | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 180 | +5.6% [-17.7, +18.4] | +0.1603 [-0.3216, +0.6537] | undecided |

### upper_tail_twcrps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| month_end | mr_cal_a_base against B1 | 180 | +11.8% [+4.9, +17.4] | +0.2205 [+0.05505, +0.6384] | gain |
| month_end | mr_cal_a_base against B1_prime | 180 | +11.6% [+3.7, +17.0] | +0.2168 [+0.08812, +0.5127] | gain |
| month_end | mr_cal_a_base against B2 | 180 | +24.9% [-10.9, +58.2] | +0.5462 [+0.06021, +1.908] | gain (was undecided) |
| month_end | mr_cal_a_base against gbm_funding | 180 | +16.5% [+9.2, +21.6] | +0.3256 [+0.05109, +0.938] | gain |
| month_end | mr_cal_a_base against gbm_funding_cal_aligned | 180 | +2.9% [-13.7, +14.8] | +0.04943 [-0.1261, +0.2529] | undecided |
| month_end | mr_cal_a_base against spread_mr_ctx | 180 | +9.2% [-7.6, +25.3] | +0.1669 [-0.08527, +0.4098] | undecided |
| month_end | mr_cal_b_location against B1 | 180 | +4.3% [-70.9, +26.3] | +0.08113 [-0.6671, +0.8223] | undecided |
| month_end | mr_cal_b_location against B1_prime | 180 | +4.2% [-59.7, +24.9] | +0.07742 [-0.5685, +0.7202] | undecided |
| month_end | mr_cal_b_location against B2 | 180 | +18.6% [-5.1, +38.0] | +0.4068 [-0.1319, +1.436] | undecided |
| month_end | mr_cal_b_location against gbm_funding | 180 | +9.4% [-67.4, +30.3] | +0.1862 [-0.6352, +1.133] | undecided |
| month_end | mr_cal_b_location against gbm_funding_cal_aligned | 180 | -5.3% [-69.7, +25.8] | -0.08994 [-0.6871, +0.5109] | undecided |
| month_end | mr_cal_b_location against mr_cal_a_base | 180 | -8.5% [-90.8, +18.3] | -0.1394 [-0.9096, +0.4112] | undecided |
| month_end | mr_cal_b_location against spread_mr_ctx | 180 | +1.5% [-38.4, +18.4] | +0.02753 [-0.4105, +0.4019] | undecided |
| month_end | mr_cal_c_location_scale against B1 | 180 | +11.2% [-58.7, +30.4] | +0.2098 [-0.4836, +1.059] | undecided |
| month_end | mr_cal_c_location_scale against B1_prime | 180 | +11.1% [-47.0, +29.4] | +0.206 [-0.3928, +0.9644] | undecided |
| month_end | mr_cal_c_location_scale against B2 | 180 | +24.4% [+2.5, +41.6] | +0.5355 [-0.03505, +1.681] | undecided (was gain) |
| month_end | mr_cal_c_location_scale against gbm_funding | 180 | +16.0% [-57.1, +34.4] | +0.3149 [-0.4735, +1.391] | undecided |
| month_end | mr_cal_c_location_scale against gbm_funding_cal_aligned | 180 | +2.3% [-51.6, +30.4] | +0.03869 [-0.4704, +0.7391] | undecided |
| month_end | mr_cal_c_location_scale against mr_cal_a_base | 180 | -0.7% [-74.8, +23.1] | -0.01073 [-0.6414, +0.5819] | undecided |
| month_end | mr_cal_c_location_scale against mr_cal_b_location | 180 | +7.2% [+3.7, +9.6] | +0.1286 [+0.04561, +0.2864] | gain |
| month_end | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 180 | -0.2% [-7.9, +3.7] | -0.004109 [-0.1214, +0.05569] | undecided |
| month_end | mr_cal_c_location_scale against spread_mr_ctx | 180 | +8.6% [-24.2, +23.4] | +0.1562 [-0.2101, +0.622] | undecided |
| month_end | mr_cal_d_no_fomc_iorb against B1 | 180 | +11.5% [-67.2, +31.3] | +0.2139 [-0.5358, +1.098] | undecided |
| month_end | mr_cal_d_no_fomc_iorb against B1_prime | 180 | +11.3% [-54.0, +30.6] | +0.2102 [-0.4369, +1.01] | undecided |
| month_end | mr_cal_d_no_fomc_iorb against B2 | 180 | +24.6% [+1.8, +40.9] | +0.5396 [-0.0813, +1.664] | undecided (was gain) |
| month_end | mr_cal_d_no_fomc_iorb against gbm_funding | 180 | +16.2% [-63.7, +35.3] | +0.319 [-0.5207, +1.427] | undecided |
| month_end | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 180 | +2.5% [-59.6, +28.0] | +0.0428 [-0.5149, +0.7123] | undecided |
| month_end | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 180 | -0.4% [-86.0, +23.6] | -0.006625 [-0.6948, +0.6061] | undecided |
| month_end | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 180 | +8.8% [-30.5, +24.1] | +0.1603 [-0.2492, +0.6489] | undecided |

### grid_crps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| ordinary | mr_cal_a_base against B1 | 507 | +35.0% [+26.4, +56.5] | +0.6181 [+0.3665, +1.497] | gain |
| ordinary | mr_cal_a_base against B1_prime | 507 | +20.3% [+12.8, +33.2] | +0.2935 [+0.1638, +0.5876] | gain |
| ordinary | mr_cal_a_base against B2 | 507 | +33.0% [+18.1, +47.4] | +0.5655 [+0.2718, +0.9739] | gain |
| ordinary | mr_cal_a_base against gbm_funding | 507 | +4.0% [-2.9, +10.4] | +0.04769 [-0.03124, +0.127] | undecided |
| ordinary | mr_cal_a_base against gbm_funding_cal_aligned | 507 | +6.6% [-1.2, +14.4] | +0.0813 [-0.007967, +0.1856] | undecided |
| ordinary | mr_cal_a_base against spread_mr_ctx | 507 | +0.3% [-4.5, +4.7] | +0.003806 [-0.05222, +0.05217] | undecided |
| ordinary | mr_cal_b_location against B1 | 507 | +35.3% [+26.6, +55.9] | +0.6248 [+0.3672, +1.462] | gain |
| ordinary | mr_cal_b_location against B1_prime | 507 | +20.8% [+12.2, +35.0] | +0.3001 [+0.1555, +0.6181] | gain |
| ordinary | mr_cal_b_location against B2 | 507 | +33.3% [+19.1, +46.8] | +0.5722 [+0.2906, +0.9673] | gain |
| ordinary | mr_cal_b_location against gbm_funding | 507 | +4.5% [-3.0, +11.7] | +0.05437 [-0.03093, +0.1428] | undecided |
| ordinary | mr_cal_b_location against gbm_funding_cal_aligned | 507 | +7.1% [-1.4, +16.0] | +0.08798 [-0.01092, +0.208] | undecided |
| ordinary | mr_cal_b_location against mr_cal_a_base | 507 | +0.6% [-2.9, +3.6] | +0.00668 [-0.03077, +0.04207] | undecided |
| ordinary | mr_cal_b_location against spread_mr_ctx | 507 | +0.9% [-4.2, +4.9] | +0.01049 [-0.04545, +0.05498] | undecided |
| ordinary | mr_cal_c_location_scale against B1 | 507 | +38.5% [+29.7, +60.2] | +0.6804 [+0.4119, +1.588] | gain |
| ordinary | mr_cal_c_location_scale against B1_prime | 507 | +24.6% [+17.4, +38.4] | +0.3557 [+0.2154, +0.684] | gain |
| ordinary | mr_cal_c_location_scale against B2 | 507 | +36.6% [+22.9, +49.9] | +0.6278 [+0.3407, +1.035] | gain |
| ordinary | mr_cal_c_location_scale against gbm_funding | 507 | +9.2% [+3.4, +15.2] | +0.1099 [+0.03923, +0.1915] | gain |
| ordinary | mr_cal_c_location_scale against gbm_funding_cal_aligned | 507 | +11.7% [+5.0, +19.6] | +0.1436 [+0.0611, +0.2571] | gain |
| ordinary | mr_cal_c_location_scale against mr_cal_a_base | 507 | +5.4% [+3.2, +7.7] | +0.06226 [+0.03218, +0.1002] | gain |
| ordinary | mr_cal_c_location_scale against mr_cal_b_location | 507 | +4.9% [+2.5, +8.2] | +0.05558 [+0.0291, +0.1076] | gain |
| ordinary | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 507 | -0.6% [-3.1, -0.0] | -0.006705 [-0.03555, -6.615e-05] | loss |
| ordinary | mr_cal_c_location_scale against spread_mr_ctx | 507 | +5.7% [+2.4, +9.4] | +0.06606 [+0.03018, +0.1072] | gain |
| ordinary | mr_cal_d_no_fomc_iorb against B1 | 507 | +38.9% [+30.0, +60.2] | +0.6871 [+0.416, +1.586] | gain |
| ordinary | mr_cal_d_no_fomc_iorb against B1_prime | 507 | +25.1% [+17.9, +38.7] | +0.3624 [+0.2213, +0.6884] | gain |
| ordinary | mr_cal_d_no_fomc_iorb against B2 | 507 | +37.0% [+23.4, +50.4] | +0.6345 [+0.3456, +1.042] | gain |
| ordinary | mr_cal_d_no_fomc_iorb against gbm_funding | 507 | +9.7% [+4.1, +15.6] | +0.1167 [+0.04685, +0.1976] | gain |
| ordinary | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 507 | +12.2% [+5.6, +20.1] | +0.1503 [+0.0692, +0.2628] | gain |
| ordinary | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 507 | +6.0% [+4.0, +8.2] | +0.06896 [+0.03992, +0.1089] | gain |
| ordinary | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 507 | +6.3% [+3.2, +9.9] | +0.07277 [+0.03821, +0.1131] | gain |

### upper_tail_twcrps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| ordinary | mr_cal_a_base against B1 | 507 | +51.0% [+38.5, +70.9] | +0.4635 [+0.2065, +1.534] | gain |
| ordinary | mr_cal_a_base against B1_prime | 507 | +28.0% [+8.2, +57.9] | +0.173 [+0.05713, +0.5333] | gain |
| ordinary | mr_cal_a_base against B2 | 507 | +14.5% [-5.9, +32.1] | +0.07544 [-0.01957, +0.2052] | undecided |
| ordinary | mr_cal_a_base against gbm_funding | 507 | -7.2% [-18.7, +3.4] | -0.03 [-0.07866, +0.01298] | undecided |
| ordinary | mr_cal_a_base against gbm_funding_cal_aligned | 507 | -3.3% [-17.8, +14.3] | -0.01405 [-0.06955, +0.06547] | undecided |
| ordinary | mr_cal_a_base against spread_mr_ctx | 507 | -11.9% [-18.6, -4.9] | -0.04711 [-0.08114, -0.02153] | loss |
| ordinary | mr_cal_b_location against B1 | 507 | +56.6% [+45.8, +73.8] | +0.5143 [+0.2407, +1.612] | gain |
| ordinary | mr_cal_b_location against B1_prime | 507 | +36.2% [+18.1, +65.1] | +0.2238 [+0.1003, +0.6306] | gain |
| ordinary | mr_cal_b_location against B2 | 507 | +24.3% [+7.7, +40.8] | +0.1262 [+0.03421, +0.273] | gain |
| ordinary | mr_cal_b_location against gbm_funding | 507 | +5.0% [-4.8, +16.8] | +0.02078 [-0.01738, +0.07886] | undecided |
| ordinary | mr_cal_b_location against gbm_funding_cal_aligned | 507 | +8.5% [-4.5, +30.5] | +0.03673 [-0.01629, +0.1649] | undecided |
| ordinary | mr_cal_b_location against mr_cal_a_base | 507 | +11.4% [+6.8, +15.3] | +0.05078 [+0.02382, +0.0881] | gain |
| ordinary | mr_cal_b_location against spread_mr_ctx | 507 | +0.9% [-4.3, +4.8] | +0.003672 [-0.01492, +0.02099] | undecided |
| ordinary | mr_cal_c_location_scale against B1 | 507 | +57.5% [+46.0, +73.1] | +0.5223 [+0.2468, +1.638] | gain |
| ordinary | mr_cal_c_location_scale against B1_prime | 507 | +37.5% [+18.7, +66.2] | +0.2318 [+0.1073, +0.6399] | gain |
| ordinary | mr_cal_c_location_scale against B2 | 507 | +25.8% [+8.6, +42.6] | +0.1342 [+0.04152, +0.2808] | gain |
| ordinary | mr_cal_c_location_scale against gbm_funding | 507 | +6.9% [-3.2, +19.1] | +0.02878 [-0.01021, +0.08831] | undecided |
| ordinary | mr_cal_c_location_scale against gbm_funding_cal_aligned | 507 | +10.4% [-2.8, +33.4] | +0.04473 [-0.008364, +0.1755] | undecided |
| ordinary | mr_cal_c_location_scale against mr_cal_a_base | 507 | +13.2% [+8.6, +17.8] | +0.05878 [+0.03256, +0.09573] | gain |
| ordinary | mr_cal_c_location_scale against mr_cal_b_location | 507 | +2.0% [-0.5, +4.1] | +0.008 [-0.0001633, +0.01478] | undecided |
| ordinary | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 507 | -2.0% [-14.9, -0.2] | -0.007544 [-0.05996, -0.001163] | loss |
| ordinary | mr_cal_c_location_scale against spread_mr_ctx | 507 | +2.9% [-1.3, +6.7] | +0.01167 [-0.004238, +0.02941] | undecided |
| ordinary | mr_cal_d_no_fomc_iorb against B1 | 507 | +58.3% [+46.6, +72.5] | +0.5298 [+0.2535, +1.614] | gain |
| ordinary | mr_cal_d_no_fomc_iorb against B1_prime | 507 | +38.8% [+19.4, +67.2] | +0.2394 [+0.1122, +0.6477] | gain |
| ordinary | mr_cal_d_no_fomc_iorb against B2 | 507 | +27.3% [+9.2, +45.1] | +0.1418 [+0.04468, +0.2969] | gain |
| ordinary | mr_cal_d_no_fomc_iorb against gbm_funding | 507 | +8.8% [-1.4, +21.1] | +0.03632 [-0.001923, +0.09832] | undecided |
| ordinary | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 507 | +12.1% [-1.2, +34.8] | +0.05227 [-0.0009725, +0.1842] | undecided |
| ordinary | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 507 | +14.9% [+9.8, +19.9] | +0.06632 [+0.03991, +0.1063] | gain |
| ordinary | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 507 | +4.8% [+1.5, +8.7] | +0.01922 [+0.006974, +0.03951] | gain |

### grid_crps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| post_month_end_window | mr_cal_a_base against B1 | 267 | +21.3% [+14.8, +28.8] | +0.5563 [+0.2475, +1.15] | gain |
| post_month_end_window | mr_cal_a_base against B1_prime | 267 | +10.7% [+2.7, +20.3] | +0.2456 [+0.04766, +0.69] | gain |
| post_month_end_window | mr_cal_a_base against B2 | 267 | +30.4% [+18.3, +42.7] | +0.895 [+0.3951, +1.577] | gain |
| post_month_end_window | mr_cal_a_base against gbm_funding | 267 | +6.7% [-4.4, +15.4] | +0.1474 [-0.06476, +0.4694] | undecided |
| post_month_end_window | mr_cal_a_base against gbm_funding_cal_aligned | 267 | +7.3% [-5.7, +17.7] | +0.1622 [-0.09287, +0.535] | undecided |
| post_month_end_window | mr_cal_a_base against spread_mr_ctx | 267 | +3.9% [-1.0, +10.9] | +0.08239 [-0.008527, +0.2936] | undecided |
| post_month_end_window | mr_cal_b_location against B1 | 267 | +17.5% [+7.0, +26.1] | +0.4573 [+0.1013, +0.9894] | gain |
| post_month_end_window | mr_cal_b_location against B1_prime | 267 | +6.4% [-7.7, +17.9] | +0.1466 [-0.1337, +0.5327] | undecided |
| post_month_end_window | mr_cal_b_location against B2 | 267 | +27.0% [+14.0, +38.6] | +0.796 [+0.3055, +1.449] | gain |
| post_month_end_window | mr_cal_b_location against gbm_funding | 267 | +2.2% [-12.6, +13.7] | +0.04831 [-0.2201, +0.3728] | undecided |
| post_month_end_window | mr_cal_b_location against gbm_funding_cal_aligned | 267 | +2.9% [-12.6, +14.8] | +0.06314 [-0.2227, +0.4131] | undecided |
| post_month_end_window | mr_cal_b_location against mr_cal_a_base | 267 | -4.8% [-18.1, +3.8] | -0.09906 [-0.3456, +0.09162] | undecided |
| post_month_end_window | mr_cal_b_location against spread_mr_ctx | 267 | -0.8% [-13.0, +8.5] | -0.01667 [-0.2291, +0.1975] | undecided |
| post_month_end_window | mr_cal_c_location_scale against B1 | 267 | +19.1% [+7.7, +28.2] | +0.4972 [+0.1229, +1.107] | gain |
| post_month_end_window | mr_cal_c_location_scale against B1_prime | 267 | +8.1% [-6.7, +20.9] | +0.1865 [-0.1094, +0.6403] | undecided |
| post_month_end_window | mr_cal_c_location_scale against B2 | 267 | +28.4% [+15.3, +39.5] | +0.8359 [+0.3273, +1.517] | gain |
| post_month_end_window | mr_cal_c_location_scale against gbm_funding | 267 | +4.0% [-12.2, +16.5] | +0.08821 [-0.2047, +0.4697] | undecided |
| post_month_end_window | mr_cal_c_location_scale against gbm_funding_cal_aligned | 267 | +4.7% [-12.3, +17.8] | +0.103 [-0.2077, +0.5111] | undecided |
| post_month_end_window | mr_cal_c_location_scale against mr_cal_a_base | 267 | -2.9% [-16.3, +5.7] | -0.05916 [-0.298, +0.1349] | undecided |
| post_month_end_window | mr_cal_c_location_scale against mr_cal_b_location | 267 | +1.9% [-0.4, +3.9] | +0.0399 [-0.003321, +0.1055] | undecided |
| post_month_end_window | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 267 | -2.4% [-7.8, +0.4] | -0.04858 [-0.1392, +0.003538] | undecided |
| post_month_end_window | mr_cal_c_location_scale against spread_mr_ctx | 267 | +1.1% [-11.7, +11.4] | +0.02323 [-0.1922, +0.2776] | undecided |
| post_month_end_window | mr_cal_d_no_fomc_iorb against B1 | 267 | +20.9% [+12.3, +28.8] | +0.5457 [+0.208, +1.149] | gain |
| post_month_end_window | mr_cal_d_no_fomc_iorb against B1_prime | 267 | +10.2% [-3.1, +21.5] | +0.235 [-0.04139, +0.6621] | undecided |
| post_month_end_window | mr_cal_d_no_fomc_iorb against B2 | 267 | +30.0% [+16.8, +41.3] | +0.8845 [+0.3782, +1.552] | gain |
| post_month_end_window | mr_cal_d_no_fomc_iorb against gbm_funding | 267 | +6.2% [-8.4, +17.1] | +0.1368 [-0.1374, +0.4932] | undecided |
| post_month_end_window | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 267 | +6.8% [-8.7, +18.4] | +0.1516 [-0.1481, +0.5424] | undecided |
| post_month_end_window | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 267 | -0.5% [-11.5, +6.7] | -0.01058 [-0.2145, +0.1522] | undecided |
| post_month_end_window | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 267 | +3.4% [-8.3, +12.0] | +0.07181 [-0.1247, +0.2984] | undecided |

### upper_tail_twcrps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| post_month_end_window | mr_cal_a_base against B1 | 267 | +28.4% [+20.2, +35.6] | +0.423 [+0.1394, +1.094] | gain |
| post_month_end_window | mr_cal_a_base against B1_prime | 267 | +13.4% [+0.6, +26.9] | +0.1654 [+0.000477, +0.6085] | gain |
| post_month_end_window | mr_cal_a_base against B2 | 267 | +25.2% [+15.0, +35.1] | +0.3585 [+0.08459, +0.9572] | gain |
| post_month_end_window | mr_cal_a_base against gbm_funding | 267 | +11.2% [-2.3, +23.5] | +0.1341 [-0.01284, +0.6675] | undecided |
| post_month_end_window | mr_cal_a_base against gbm_funding_cal_aligned | 267 | +12.7% [-2.0, +27.2] | +0.1556 [-0.02732, +0.7209] | undecided |
| post_month_end_window | mr_cal_a_base against spread_mr_ctx | 267 | +5.3% [-3.7, +18.4] | +0.06004 [-0.01928, +0.3668] | undecided |
| post_month_end_window | mr_cal_b_location against B1 | 267 | +18.5% [+2.4, +29.2] | +0.2757 [-0.03426, +0.8032] | undecided (was gain) |
| post_month_end_window | mr_cal_b_location against B1_prime | 267 | +1.5% [-27.1, +19.1] | +0.01804 [-0.2192, +0.3173] | undecided |
| post_month_end_window | mr_cal_b_location against B2 | 267 | +14.8% [-5.5, +29.7] | +0.2112 [-0.09203, +0.7393] | undecided |
| post_month_end_window | mr_cal_b_location against gbm_funding | 267 | -1.1% [-30.3, +17.7] | -0.01323 [-0.2282, +0.2648] | undecided |
| post_month_end_window | mr_cal_b_location against gbm_funding_cal_aligned | 267 | +0.7% [-31.4, +20.1] | +0.008247 [-0.2343, +0.3284] | undecided |
| post_month_end_window | mr_cal_b_location against mr_cal_a_base | 267 | -13.8% [-37.2, -0.1] | -0.1473 [-0.3553, -0.01559] | loss |
| post_month_end_window | mr_cal_b_location against spread_mr_ctx | 267 | -7.8% [-32.4, +10.9] | -0.08728 [-0.2592, +0.09134] | undecided |
| post_month_end_window | mr_cal_c_location_scale against B1 | 267 | +19.2% [+0.0, +31.2] | +0.2854 [-0.0468, +0.9209] | undecided (was gain) |
| post_month_end_window | mr_cal_c_location_scale against B1_prime | 267 | +2.3% [-30.9, +23.1] | +0.02773 [-0.2275, +0.3946] | undecided |
| post_month_end_window | mr_cal_c_location_scale against B2 | 267 | +15.5% [-7.8, +32.0] | +0.2209 [-0.1089, +0.8247] | undecided |
| post_month_end_window | mr_cal_c_location_scale against gbm_funding | 267 | -0.3% [-34.1, +22.8] | -0.003543 [-0.244, +0.3572] | undecided |
| post_month_end_window | mr_cal_c_location_scale against gbm_funding_cal_aligned | 267 | +1.5% [-36.1, +25.1] | +0.01794 [-0.2538, +0.4265] | undecided |
| post_month_end_window | mr_cal_c_location_scale against mr_cal_a_base | 267 | -12.9% [-39.0, +3.6] | -0.1376 [-0.3299, +0.007337] | undecided |
| post_month_end_window | mr_cal_c_location_scale against mr_cal_b_location | 267 | +0.8% [-4.8, +6.1] | +0.009691 [-0.03573, +0.09306] | undecided |
| post_month_end_window | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 267 | -2.0% [-10.6, +1.7] | -0.02374 [-0.1074, +0.01718] | undecided |
| post_month_end_window | mr_cal_c_location_scale against spread_mr_ctx | 267 | -6.9% [-35.6, +16.3] | -0.07759 [-0.2605, +0.1612] | undecided |
| post_month_end_window | mr_cal_d_no_fomc_iorb against B1 | 267 | +20.8% [+5.8, +32.0] | +0.3091 [+0.003764, +0.9727] | gain |
| post_month_end_window | mr_cal_d_no_fomc_iorb against B1_prime | 267 | +4.2% [-26.3, +24.0] | +0.05147 [-0.1878, +0.4133] | undecided |
| post_month_end_window | mr_cal_d_no_fomc_iorb against B2 | 267 | +17.2% [-4.3, +32.8] | +0.2446 [-0.07844, +0.8472] | undecided |
| post_month_end_window | mr_cal_d_no_fomc_iorb against gbm_funding | 267 | +1.7% [-28.6, +23.5] | +0.0202 [-0.2014, +0.3792] | undecided |
| post_month_end_window | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 267 | +3.4% [-31.3, +25.8] | +0.04168 [-0.2174, +0.449] | undecided |
| post_month_end_window | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 267 | -10.7% [-30.9, +3.8] | -0.1139 [-0.2722, +0.008715] | undecided |
| post_month_end_window | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 267 | -4.8% [-30.1, +16.9] | -0.05385 [-0.2177, +0.1697] | undecided |

### grid_crps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| quarter_end | mr_cal_a_base against B1 | 30 | +9.8% [+8.0, +11.5] | +0.6847 [+0.1587, +2.157] | gain |
| quarter_end | mr_cal_a_base against B1_prime | 30 | +8.4% [+6.0, +10.4] | +0.5759 [+0.1434, +1.712] | gain |
| quarter_end | mr_cal_a_base against B2 | 30 | +17.0% [-31.3, +53.6] | +1.289 [-0.9806, +4.05] | undecided |
| quarter_end | mr_cal_a_base against gbm_funding | 30 | +19.9% [+17.3, +23.8] | +1.562 [+0.4638, +6.285] | gain |
| quarter_end | mr_cal_a_base against gbm_funding_cal_aligned | 30 | +9.1% [-21.1, +33.0] | +0.6253 [-1.656, +2.93] | undecided |
| quarter_end | mr_cal_a_base against spread_mr_ctx | 30 | +3.3% [-1.2, +9.8] | +0.2164 [-0.03731, +0.5915] | undecided |
| quarter_end | mr_cal_b_location against B1 | 30 | -3.2% [-254.0, +39.1] | -0.2227 [-6.772, +3.711] | undecided |
| quarter_end | mr_cal_b_location against B1_prime | 30 | -4.8% [-264.6, +38.4] | -0.3315 [-7.155, +3.547] | undecided |
| quarter_end | mr_cal_b_location against B2 | 30 | +5.0% [-48.0, +22.3] | +0.3816 [-3.096, +1.775] | undecided |
| quarter_end | mr_cal_b_location against gbm_funding | 30 | +8.4% [-198.9, +42.7] | +0.6547 [-5.189, +4.868] | undecided |
| quarter_end | mr_cal_b_location against gbm_funding_cal_aligned | 30 | -4.1% [-146.0, +33.4] | -0.2822 [-4.635, +2.251] | undecided |
| quarter_end | mr_cal_b_location against mr_cal_a_base | 30 | -14.5% [-281.7, +31.7] | -0.9074 [-8.803, +2.538] | undecided |
| quarter_end | mr_cal_b_location against spread_mr_ctx | 30 | -10.7% [-243.6, +36.6] | -0.691 [-7.437, +2.667] | undecided |
| quarter_end | mr_cal_c_location_scale against B1 | 30 | +11.1% [-186.7, +46.0] | +0.7717 [-4.079, +4.997] | undecided |
| quarter_end | mr_cal_c_location_scale against B1_prime | 30 | +9.7% [-195.1, +45.2] | +0.6629 [-4.257, +4.792] | undecided |
| quarter_end | mr_cal_c_location_scale against B2 | 30 | +18.2% [-24.2, +31.0] | +1.376 [-0.5738, +2.842] | undecided |
| quarter_end | mr_cal_c_location_scale against gbm_funding | 30 | +21.1% [-143.7, +49.2] | +1.649 [-3.107, +6.584] | undecided |
| quarter_end | mr_cal_c_location_scale against gbm_funding_cal_aligned | 30 | +10.3% [-95.6, +41.4] | +0.7123 [-2.235, +3.998] | undecided |
| quarter_end | mr_cal_c_location_scale against mr_cal_a_base | 30 | +1.4% [-214.9, +39.5] | +0.08702 [-5.15, +3.503] | undecided |
| quarter_end | mr_cal_c_location_scale against mr_cal_b_location | 30 | +13.9% [+10.5, +17.9] | +0.9944 [+0.04225, +3.276] | gain |
| quarter_end | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 30 | +0.2% [-1.1, +1.3] | +0.0119 [-0.03073, +0.07122] | undecided |
| quarter_end | mr_cal_c_location_scale against spread_mr_ctx | 30 | +4.7% [-176.2, +43.2] | +0.3034 [-4.1, +3.764] | undecided |
| quarter_end | mr_cal_d_no_fomc_iorb against B1 | 30 | +10.9% [-186.5, +45.4] | +0.7598 [-4.068, +4.929] | undecided |
| quarter_end | mr_cal_d_no_fomc_iorb against B1_prime | 30 | +9.5% [-194.6, +44.7] | +0.651 [-4.244, +4.721] | undecided |
| quarter_end | mr_cal_d_no_fomc_iorb against B2 | 30 | +18.0% [-21.7, +30.4] | +1.364 [-0.5317, +2.782] | undecided |
| quarter_end | mr_cal_d_no_fomc_iorb against gbm_funding | 30 | +20.9% [-141.0, +48.6] | +1.637 [-3.089, +6.495] | undecided |
| quarter_end | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 30 | +10.2% [-93.7, +40.4] | +0.7004 [-2.206, +3.915] | undecided |
| quarter_end | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 30 | +1.2% [-211.8, +38.8] | +0.07512 [-5.138, +3.441] | undecided |
| quarter_end | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 30 | +4.5% [-173.8, +42.5] | +0.2915 [-4.088, +3.698] | undecided |

### upper_tail_twcrps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| quarter_end | mr_cal_a_base against B1 | 30 | +10.9% [+7.6, +13.3] | +0.5856 [+0.04033, +4.798] | gain |
| quarter_end | mr_cal_a_base against B1_prime | 30 | +9.8% [+4.6, +12.5] | +0.5194 [+0.05248, +3.615] | gain |
| quarter_end | mr_cal_a_base against gbm_funding | 30 | +19.7% [+16.5, +28.3] | +1.177 [+0.002908, +12.89] | gain |
| quarter_end | mr_cal_a_base against gbm_funding_cal_aligned | 30 | +11.2% [-8.4, +31.2] | +0.6016 [-0.5156, +3.505] | undecided |
| quarter_end | mr_cal_a_base against spread_mr_ctx | 30 | +4.3% [-6.5, +9.4] | +0.2161 [+0.05864, +0.387] | gain (was undecided) |
| quarter_end | mr_cal_b_location against B1 | 30 | -2.3% [-243.3, +32.3] | -0.1232 [-3.967, +2.44] | undecided |
| quarter_end | mr_cal_b_location against B1_prime | 30 | -3.6% [-253.3, +31.8] | -0.1894 [-4.143, +2.316] | undecided |
| quarter_end | mr_cal_b_location against gbm_funding | 30 | +7.8% [-172.9, +35.7] | +0.4682 [-2.719, +3.861] | undecided |
| quarter_end | mr_cal_b_location against gbm_funding_cal_aligned | 30 | -2.0% [-154.8, +38.1] | -0.1072 [-3.312, +2.063] | undecided |
| quarter_end | mr_cal_b_location against mr_cal_a_base | 30 | -14.8% [-268.9, +24.6] | -0.7088 [-5.861, +1.412] | undecided |
| quarter_end | mr_cal_b_location against spread_mr_ctx | 30 | -9.8% [-326.7, +32.7] | -0.4927 [-5.122, +1.676] | undecided |
| quarter_end | mr_cal_c_location_scale against B1 | 30 | +13.5% [-228.7, +41.5] | +0.7265 [-2.139, +4.316] | undecided |
| quarter_end | mr_cal_c_location_scale against B1_prime | 30 | +12.4% [-238.5, +41.0] | +0.6603 [-2.213, +4.064] | undecided |
| quarter_end | mr_cal_c_location_scale against gbm_funding | 30 | +22.1% [-154.1, +44.7] | +1.318 [-1.676, +6.321] | undecided |
| quarter_end | mr_cal_c_location_scale against gbm_funding_cal_aligned | 30 | +13.8% [-129.3, +46.1] | +0.7425 [-1.607, +4.981] | undecided |
| quarter_end | mr_cal_c_location_scale against mr_cal_a_base | 30 | +2.9% [-255.9, +34.9] | +0.141 [-2.742, +2.508] | undecided |
| quarter_end | mr_cal_c_location_scale against mr_cal_b_location | 30 | +15.4% [+13.4, +16.7] | +0.8497 [-0.04904, +3.485] | undecided (was gain) |
| quarter_end | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 30 | +0.0% [-2.2, +2.0] | +0.00119 [-0.03813, +0.04805] | undecided |
| quarter_end | mr_cal_c_location_scale against spread_mr_ctx | 30 | +7.1% [-354.1, +41.2] | +0.3571 [-2.349, +2.909] | undecided |
| quarter_end | mr_cal_d_no_fomc_iorb against B1 | 30 | +13.5% [-220.2, +41.0] | +0.7253 [-2.1, +4.262] | undecided |
| quarter_end | mr_cal_d_no_fomc_iorb against B1_prime | 30 | +12.4% [-229.7, +40.4] | +0.6591 [-2.176, +4.014] | undecided |
| quarter_end | mr_cal_d_no_fomc_iorb against gbm_funding | 30 | +22.1% [-150.5, +44.2] | +1.317 [-1.642, +6.271] | undecided |
| quarter_end | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 30 | +13.7% [-125.8, +45.3] | +0.7414 [-1.575, +4.931] | undecided |
| quarter_end | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 30 | +2.9% [-247.4, +34.3] | +0.1398 [-2.705, +2.464] | undecided |
| quarter_end | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 30 | +7.1% [-337.4, +40.4] | +0.3559 [-2.316, +2.861] | undecided |

### grid_crps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| settlement | mr_cal_a_base against B1 | 946 | +20.4% [+16.2, +27.0] | +0.5371 [+0.2986, +1.282] | gain |
| settlement | mr_cal_a_base against B1_prime | 946 | +10.3% [+5.1, +15.9] | +0.2401 [+0.1321, +0.4345] | gain |
| settlement | mr_cal_a_base against B2 | 946 | +32.3% [+16.9, +44.2] | +0.9976 [+0.6624, +1.468] | gain |
| settlement | mr_cal_a_base against gbm_funding | 946 | +10.0% [+5.5, +14.1] | +0.2319 [+0.1379, +0.3676] | gain |
| settlement | mr_cal_a_base against gbm_funding_cal_aligned | 946 | +6.5% [+1.3, +12.0] | +0.1458 [+0.04431, +0.2819] | gain |
| settlement | mr_cal_a_base against spread_mr_ctx | 946 | +3.8% [+0.5, +7.3] | +0.08274 [+0.02322, +0.1523] | gain |
| settlement | mr_cal_b_location against B1 | 946 | +7.9% [-7.8, +21.7] | +0.207 [-0.1564, +0.7713] | undecided |
| settlement | mr_cal_b_location against B1_prime | 946 | -3.9% [-19.2, +7.3] | -0.09002 [-0.3847, +0.1961] | undecided |
| settlement | mr_cal_b_location against B2 | 946 | +21.6% [+10.4, +32.2] | +0.6676 [+0.3379, +1.096] | gain |
| settlement | mr_cal_b_location against gbm_funding | 946 | -4.2% [-19.8, +6.3] | -0.09814 [-0.3972, +0.1689] | undecided |
| settlement | mr_cal_b_location against gbm_funding_cal_aligned | 946 | -8.2% [-23.8, +2.7] | -0.1843 [-0.4574, +0.06877] | undecided |
| settlement | mr_cal_b_location against mr_cal_a_base | 946 | -15.8% [-33.9, -4.2] | -0.3301 [-0.601, -0.1268] | loss |
| settlement | mr_cal_b_location against spread_mr_ctx | 946 | -11.4% [-25.6, -1.9] | -0.2473 [-0.4864, -0.06252] | loss |
| settlement | mr_cal_c_location_scale against B1 | 946 | +13.0% [+0.9, +24.7] | +0.3427 [+0.01054, +0.9537] | gain |
| settlement | mr_cal_c_location_scale against B1_prime | 946 | +2.0% [-9.4, +11.7] | +0.04562 [-0.1999, +0.3241] | undecided |
| settlement | mr_cal_c_location_scale against B2 | 946 | +26.0% [+13.9, +36.3] | +0.8032 [+0.4805, +1.241] | gain |
| settlement | mr_cal_c_location_scale against gbm_funding | 946 | +1.6% [-9.9, +10.3] | +0.03749 [-0.2079, +0.2867] | undecided |
| settlement | mr_cal_c_location_scale against gbm_funding_cal_aligned | 946 | -2.2% [-14.1, +7.0] | -0.04866 [-0.2718, +0.1868] | undecided |
| settlement | mr_cal_c_location_scale against mr_cal_a_base | 946 | -9.3% [-22.7, -0.6] | -0.1944 [-0.4009, -0.02734] | loss |
| settlement | mr_cal_c_location_scale against mr_cal_b_location | 946 | +5.6% [+2.9, +8.4] | +0.1356 [+0.08365, +0.2021] | gain |
| settlement | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 946 | -2.1% [-4.4, +0.1] | -0.04594 [-0.08944, -0.00521] | loss (was undecided) |
| settlement | mr_cal_c_location_scale against spread_mr_ctx | 946 | -5.1% [-15.2, +2.1] | -0.1117 [-0.2871, +0.04768] | undecided |
| settlement | mr_cal_d_no_fomc_iorb against B1 | 946 | +14.8% [+4.1, +25.3] | +0.3886 [+0.06517, +0.9916] | gain |
| settlement | mr_cal_d_no_fomc_iorb against B1_prime | 946 | +3.9% [-6.2, +13.3] | +0.09156 [-0.1372, +0.3586] | undecided |
| settlement | mr_cal_d_no_fomc_iorb against B2 | 946 | +27.5% [+14.9, +37.8] | +0.8491 [+0.5319, +1.291] | gain |
| settlement | mr_cal_d_no_fomc_iorb against gbm_funding | 946 | +3.6% [-6.7, +11.9] | +0.08343 [-0.146, +0.3201] | undecided |
| settlement | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 946 | -0.1% [-10.4, +8.4] | -0.002719 [-0.207, +0.2188] | undecided |
| settlement | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 946 | -7.1% [-18.7, +0.4] | -0.1485 [-0.3397, +0.002187] | undecided |
| settlement | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 946 | -3.0% [-11.3, +3.1] | -0.06576 [-0.2221, +0.07513] | undecided |

### upper_tail_twcrps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| settlement | mr_cal_a_base against B1 | 946 | +25.4% [+21.2, +31.7] | +0.4277 [+0.1924, +1.333] | gain |
| settlement | mr_cal_a_base against B1_prime | 946 | +12.9% [+1.9, +22.1] | +0.1862 [+0.09008, +0.4097] | gain |
| settlement | mr_cal_a_base against B2 | 946 | +22.2% [+3.7, +37.6] | +0.3586 [+0.1857, +0.6281] | gain |
| settlement | mr_cal_a_base against gbm_funding | 946 | +10.3% [+1.7, +17.0] | +0.144 [+0.06271, +0.2993] | gain |
| settlement | mr_cal_a_base against gbm_funding_cal_aligned | 946 | +6.6% [-1.5, +14.7] | +0.08862 [+0.009439, +0.226] | gain (was undecided) |
| settlement | mr_cal_a_base against spread_mr_ctx | 946 | +3.4% [-1.3, +8.7] | +0.0446 [-0.002576, +0.1117] | undecided |
| settlement | mr_cal_b_location against B1 | 946 | +13.8% [-3.7, +28.4] | +0.2335 [-0.07597, +0.8461] | undecided |
| settlement | mr_cal_b_location against B1_prime | 946 | -0.6% [-19.2, +11.7] | -0.008018 [-0.2321, +0.2266] | undecided |
| settlement | mr_cal_b_location against B2 | 946 | +10.2% [-3.7, +23.1] | +0.1644 [-0.05331, +0.44] | undecided |
| settlement | mr_cal_b_location against gbm_funding | 946 | -3.6% [-26.2, +8.9] | -0.0503 [-0.2871, +0.1686] | undecided |
| settlement | mr_cal_b_location against gbm_funding_cal_aligned | 946 | -7.8% [-31.6, +5.6] | -0.1056 [-0.3268, +0.0953] | undecided |
| settlement | mr_cal_b_location against mr_cal_a_base | 946 | -15.4% [-43.0, -0.5] | -0.1942 [-0.4025, -0.05252] | loss |
| settlement | mr_cal_b_location against spread_mr_ctx | 946 | -11.5% [-33.9, +1.3] | -0.1496 [-0.3339, -0.01167] | loss (was undecided) |
| settlement | mr_cal_c_location_scale against B1 | 946 | +18.6% [+5.3, +30.9] | +0.3142 [+0.01541, +1.009] | gain |
| settlement | mr_cal_c_location_scale against B1_prime | 946 | +5.0% [-9.7, +16.9] | +0.07268 [-0.1222, +0.3307] | undecided |
| settlement | mr_cal_c_location_scale against B2 | 946 | +15.1% [+0.4, +28.7] | +0.2451 [+0.0364, +0.5404] | gain |
| settlement | mr_cal_c_location_scale against gbm_funding | 946 | +2.2% [-14.5, +12.9] | +0.03041 [-0.1701, +0.2568] | undecided |
| settlement | mr_cal_c_location_scale against gbm_funding_cal_aligned | 946 | -1.8% [-19.7, +9.7] | -0.02492 [-0.2072, +0.1888] | undecided |
| settlement | mr_cal_c_location_scale against mr_cal_a_base | 946 | -9.0% [-29.3, +2.1] | -0.1135 [-0.2734, +0.0118] | undecided |
| settlement | mr_cal_c_location_scale against mr_cal_b_location | 946 | +5.6% [+1.2, +9.7] | +0.0807 [+0.04297, +0.1364] | gain |
| settlement | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 946 | -1.5% [-4.5, +1.8] | -0.01995 [-0.05276, +0.02099] | undecided |
| settlement | mr_cal_c_location_scale against spread_mr_ctx | 946 | -5.3% [-20.8, +4.6] | -0.06894 [-0.2069, +0.06485] | undecided |
| settlement | mr_cal_d_no_fomc_iorb against B1 | 946 | +19.8% [+8.0, +31.2] | +0.3341 [+0.03874, +1.032] | gain |
| settlement | mr_cal_d_no_fomc_iorb against B1_prime | 946 | +6.4% [-7.1, +18.3] | +0.09264 [-0.08894, +0.343] | undecided |
| settlement | mr_cal_d_no_fomc_iorb against B2 | 946 | +16.4% [+1.2, +30.4] | +0.265 [+0.06536, +0.5622] | gain |
| settlement | mr_cal_d_no_fomc_iorb against gbm_funding | 946 | +3.6% [-10.9, +13.9] | +0.05036 [-0.1378, +0.2701] | undecided |
| settlement | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 946 | -0.4% [-15.7, +10.7] | -0.004973 [-0.175, +0.2045] | undecided |
| settlement | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 946 | -7.4% [-24.7, +2.2] | -0.09359 [-0.24, +0.02189] | undecided |
| settlement | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 946 | -3.8% [-16.4, +4.8] | -0.04899 [-0.1704, +0.07478] | undecided |

### grid_crps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| tax_date | mr_cal_a_base against B1 | 89 | +6.8% [-6.0, +13.7] | +0.3754 [+0.04967, +1.108] | gain (was undecided) |
| tax_date | mr_cal_a_base against B1_prime | 89 | +5.5% [+1.7, +9.0] | +0.299 [+0.01204, +1.243] | gain |
| tax_date | mr_cal_a_base against B2 | 89 | +33.8% [-61.4, +58.0] | +2.617 [+1.42, +4.86] | gain (was undecided) |
| tax_date | mr_cal_a_base against gbm_funding | 89 | +11.3% [+0.2, +21.8] | +0.6516 [+0.1416, +2.265] | gain |
| tax_date | mr_cal_a_base against gbm_funding_cal_aligned | 89 | +11.6% [-0.4, +23.5] | +0.6712 [+0.1149, +2.019] | gain (was undecided) |
| tax_date | mr_cal_a_base against spread_mr_ctx | 89 | +4.6% [-5.2, +14.2] | +0.2475 [+0.06492, +0.5525] | gain (was undecided) |
| tax_date | mr_cal_b_location against B1 | 89 | -57.5% [-368.9, +39.0] | -3.159 [-14.34, +0.2047] | undecided |
| tax_date | mr_cal_b_location against B1_prime | 89 | -59.7% [-373.7, +42.0] | -3.235 [-14.7, +0.0866] | undecided |
| tax_date | mr_cal_b_location against B2 | 89 | -11.9% [-96.7, +20.3] | -0.9171 [-9.927, +1.704] | undecided |
| tax_date | mr_cal_b_location against gbm_funding | 89 | -49.9% [-356.6, +27.6] | -2.883 [-14.18, +0.526] | undecided |
| tax_date | mr_cal_b_location against gbm_funding_cal_aligned | 89 | -49.4% [-342.9, +26.6] | -2.863 [-14.06, +0.5393] | undecided |
| tax_date | mr_cal_b_location against mr_cal_a_base | 89 | -69.0% [-413.8, +37.2] | -3.534 [-14.18, -0.1294] | loss (was undecided) |
| tax_date | mr_cal_b_location against spread_mr_ctx | 89 | -61.2% [-356.7, +44.3] | -3.287 [-13.41, -0.05867] | loss (was undecided) |
| tax_date | mr_cal_c_location_scale against B1 | 89 | -37.6% [-242.6, +30.7] | -2.066 [-9.785, +0.2567] | undecided |
| tax_date | mr_cal_c_location_scale against B1_prime | 89 | -39.5% [-245.7, +33.3] | -2.142 [-9.885, +0.1214] | undecided |
| tax_date | mr_cal_c_location_scale against B2 | 89 | +2.3% [-33.5, +19.2] | +0.1759 [-3.936, +1.921] | undecided |
| tax_date | mr_cal_c_location_scale against gbm_funding | 89 | -31.0% [-232.1, +23.0] | -1.79 [-9.022, +0.628] | undecided |
| tax_date | mr_cal_c_location_scale against gbm_funding_cal_aligned | 89 | -30.6% [-215.8, +22.5] | -1.77 [-8.713, +0.6408] | undecided |
| tax_date | mr_cal_c_location_scale against mr_cal_a_base | 89 | -47.7% [-270.4, +28.7] | -2.441 [-10.43, -0.123] | loss (was undecided) |
| tax_date | mr_cal_c_location_scale against mr_cal_b_location | 89 | +12.6% [-16.5, +38.2] | +1.093 [-0.01102, +3.988] | undecided |
| tax_date | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 89 | +1.3% [-2.8, +4.5] | +0.1034 [-0.1586, +0.4757] | undecided |
| tax_date | mr_cal_c_location_scale against spread_mr_ctx | 89 | -40.9% [-226.9, +32.3] | -2.194 [-9.565, -0.04346] | loss (was undecided) |
| tax_date | mr_cal_d_no_fomc_iorb against B1 | 89 | -39.5% [-221.6, +27.9] | -2.169 [-8.809, +0.2353] | undecided |
| tax_date | mr_cal_d_no_fomc_iorb against B1_prime | 89 | -41.4% [-224.0, +30.5] | -2.245 [-8.965, +0.1112] | undecided |
| tax_date | mr_cal_d_no_fomc_iorb against B2 | 89 | +0.9% [-29.7, +18.0] | +0.0725 [-3.702, +1.794] | undecided |
| tax_date | mr_cal_d_no_fomc_iorb against gbm_funding | 89 | -32.8% [-207.7, +20.7] | -1.893 [-8.457, +0.5688] | undecided |
| tax_date | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 89 | -32.3% [-194.2, +20.0] | -1.873 [-8.211, +0.5632] | undecided |
| tax_date | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 89 | -49.7% [-253.3, +25.4] | -2.545 [-9.544, -0.1312] | loss (was undecided) |
| tax_date | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 89 | -42.8% [-208.9, +28.9] | -2.297 [-8.695, -0.0573] | loss (was undecided) |

### upper_tail_twcrps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| tax_date | mr_cal_a_base against B1 | 89 | +6.1% [-12.4, +15.7] | +0.286 [+0.0233, +2.129] | gain (was undecided) |
| tax_date | mr_cal_a_base against B1_prime | 89 | +5.9% [-2.7, +12.3] | +0.2765 [+0.01466, +2.68] | gain (was undecided) |
| tax_date | mr_cal_a_base against gbm_funding_cal_aligned | 89 | +10.9% [-2.7, +31.9] | +0.5354 [-0.05183, +13.41] | undecided |
| tax_date | mr_cal_a_base against spread_mr_ctx | 89 | +4.1% [-6.4, +15.3] | +0.1885 [+0.01273, +0.6059] | gain (was undecided) |
| tax_date | mr_cal_b_location against B1 | 89 | -45.0% [-383.6, +21.8] | -2.098 [-13.16, +0.2137] | undecided |
| tax_date | mr_cal_b_location against B1_prime | 89 | -45.3% [-383.4, +22.9] | -2.108 [-13.21, +0.1753] | undecided |
| tax_date | mr_cal_b_location against gbm_funding_cal_aligned | 89 | -37.6% [-312.3, +19.3] | -1.849 [-10.78, +0.466] | undecided |
| tax_date | mr_cal_b_location against mr_cal_a_base | 89 | -54.5% [-399.4, +19.6] | -2.384 [-13.36, -0.0463] | loss (was undecided) |
| tax_date | mr_cal_b_location against spread_mr_ctx | 89 | -48.1% [-352.2, +62.0] | -2.196 [-12.11, -0.005788] | loss (was undecided) |
| tax_date | mr_cal_c_location_scale against B1 | 89 | -28.1% [-262.4, +17.7] | -1.311 [-8.275, +0.2643] | undecided |
| tax_date | mr_cal_c_location_scale against B1_prime | 89 | -28.4% [-261.3, +18.7] | -1.321 [-8.319, +0.2318] | undecided |
| tax_date | mr_cal_c_location_scale against gbm_funding_cal_aligned | 89 | -21.6% [-191.8, +17.8] | -1.062 [-5.741, +0.6362] | undecided |
| tax_date | mr_cal_c_location_scale against mr_cal_a_base | 89 | -36.5% [-267.3, +15.7] | -1.597 [-9.703, -0.02028] | loss (was undecided) |
| tax_date | mr_cal_c_location_scale against mr_cal_b_location | 89 | +11.6% [-52.0, +41.5] | +0.7872 [+0.001461, +3.602] | gain (was undecided) |
| tax_date | mr_cal_c_location_scale against mr_cal_d_no_fomc_iorb | 89 | +1.0% [-4.8, +5.9] | +0.06114 [-0.2046, +0.4118] | undecided |
| tax_date | mr_cal_c_location_scale against spread_mr_ctx | 89 | -30.9% [-228.7, +44.4] | -1.409 [-8.437, +0.02451] | undecided |
| tax_date | mr_cal_d_no_fomc_iorb against B1 | 89 | -29.4% [-206.7, +14.5] | -1.372 [-7.242, +0.2279] | undecided |
| tax_date | mr_cal_d_no_fomc_iorb against B1_prime | 89 | -29.7% [-208.6, +15.5] | -1.382 [-7.34, +0.1868] | undecided |
| tax_date | mr_cal_d_no_fomc_iorb against gbm_funding_cal_aligned | 89 | -22.9% [-157.7, +15.5] | -1.123 [-5.495, +0.5582] | undecided |
| tax_date | mr_cal_d_no_fomc_iorb against mr_cal_a_base | 89 | -37.9% [-228.7, +12.1] | -1.658 [-8.037, -0.02744] | loss (was undecided) |
| tax_date | mr_cal_d_no_fomc_iorb against spread_mr_ctx | 89 | -32.2% [-181.6, +40.1] | -1.47 [-6.744, +0.009984] | undecided |

### Politis-White block beside 10: grid_crps, by all decision days

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| all decision days | mr_cal_b_location against the base (a) | 1855 | -16.5% [-37.6, -4.6] | -0.2804 [-0.5614, -0.08892] | loss |
| all decision days | mr_cal_c_location_scale against the base (a) | 1855 | -9.6% [-25.2, -0.6] | -0.1625 [-0.3687, -0.01272] | loss |
| all decision days | mr_cal_d_no_fomc_iorb against the base (a) | 1855 | -6.2% [-18.2, +1.0] | -0.1061 [-0.2733, +0.01544] | undecided |

### Politis-White block beside 10: upper_tail_twcrps, by all decision days

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| all decision days | mr_cal_b_location against the base (a) | 1855 | -17.1% [-52.2, -1.0] | -0.1536 [-0.3629, -0.03111] | loss |
| all decision days | mr_cal_c_location_scale against the base (a) | 1855 | -10.3% [-38.9, +2.4] | -0.09261 [-0.2595, +0.01803] | undecided |
| all decision days | mr_cal_d_no_fomc_iorb against the base (a) | 1855 | -6.8% [-25.9, +2.8] | -0.06108 [-0.1856, +0.02921] | undecided |

Nothing here is a verdict for a hypothesis. The originals stand.
