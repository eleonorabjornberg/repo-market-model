# Scaled mean reversion (#941), read on the mean-d bound (#1167; H5 reporting, for #1009)

**Development data, not a verdict.** No re-scoring, no lockbox day, and no published declaration, record or decided value moves. Every figure is read from `docs/research/fhs-scale-941/result.json`, the record of the original page (`fhs-scale-941-result.md`, which stands), by `scripts/mean_d_reading_1167.py report`. Seed 941, 10,000 draws, as on the original page.

## What changes and why

The original page read each row from the studentized skill interval. The skill interval and the interval on the mean difference d are built from different studentized draws, so their ends can fall on different sides of zero (#1009). The protocol's verdict reads the one-sided studentized bound on mean d (ruling 1/5). By Eleonora's ruling on #1009 this page shows both intervals for every paired row and reads the mean-d bound: **gain** when the lower bound of mean d is above zero, **loss** when its upper bound is below zero, **undecided** otherwise. The 90% two-sided interval on mean d is the pair of one-sided 95% bounds. d = S(benchmark) − S(candidate), positive favouring the candidate; skill is mean(d) / mean(S(benchmark)). A row the scorer left undefined carries no interval and is not read here.

**Caveat (Lens C of the five-lens review, #958).** The lag-10 HAC standard error that studentizes the mean-d bound is understated about 2× after 2020 (about 2.3× in 2021–23, 1.7× in 2024–26), and the bootstrap block of 10 days is an order of magnitude shorter than the autocorrelation of d. The bound is therefore optimistic: an interval that excludes zero here is narrower than it should be after 2020. A development reading on this page is evidence for a question, not a verdict.

Paired rows read: 1180. Rows whose reading changes: 115.

| reading on the skill interval -> reading on the mean-d bound | rows |
|---|---|
| gain -> undecided | 10 |
| loss -> undecided | 10 |
| undecided -> gain | 90 |
| undecided -> loss | 5 |

## Readings that change

| section | group | comparison | skill [90%] | mean d [90%] | on the skill interval | on the mean-d bound |
|---|---|---|---|---|---|---|
| brier_10, by lead | h=1 | spread_mr_level10 against B2 | +10.8% [-0.5, +21.0] | +0.003179 [+8.643e-05, +0.007147] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | spread_mr_fhs_mad10_f0.5 against B2 | +20.4% [-2.7, +36.8] | +0.2273 [+0.08476, +0.3908] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | spread_mr_fhs_mad20_f0.25 against B2 | +20.2% [-2.8, +36.0] | +0.2247 [+0.08086, +0.3888] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | spread_mr_fhs_mad20_f0.5 against B2 | +21.0% [-2.7, +37.0] | +0.2341 [+0.09036, +0.3964] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | spread_mr_fhs_mad20_f1.0 against B2 | +20.9% [-2.7, +36.8] | +0.2325 [+0.08975, +0.3939] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | spread_mr_fhs_mad40_f0.5 against B2 | +19.9% [-3.0, +36.0] | +0.2211 [+0.0778, +0.3818] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | spread_mr_level10 against B2 | +17.6% [-6.7, +33.6] | +0.1962 [+0.04712, +0.3462] | undecided | **gain** |
| brier_10, by lead | h=2 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | +4.0% [-0.1, +7.8] | +0.001162 [+8.893e-07, +0.002715] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=2 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | -10.3% [-43.8, -0.1] | -0.09576 [-0.4473, +0.008253] | loss | **undecided** |
| upper_tail_twcrps, by lead | h=3 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | -12.3% [-51.7, -0.9] | -0.1147 [-0.5315, +0.003964] | loss | **undecided** |
| upper_tail_twcrps, by lead | h=4 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | -14.0% [-56.9, -1.2] | -0.1302 [-0.5879, +0.00113] | loss | **undecided** |
| brier_5, by lead | h=5 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | +5.7% [-0.2, +11.8] | +0.003336 [+0.0001644, +0.007875] | undecided | **gain** |
| grid_crps, by lead | h=5 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | +2.9% [-0.1, +5.2] | +0.05505 [+0.002868, +0.1027] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=5 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | -15.2% [-64.5, -1.2] | -0.1432 [-0.666, +0.001506] | loss | **undecided** |
| upper_tail_twcrps, by all decision days | all decision days | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | -11.8% [-51.6, -0.5] | -0.11 [-0.539, +0.006388] | loss | **undecided** |
| grid_crps, by pressure-day type | month_end | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | +7.4% [-0.2, +17.0] | +0.156 [+0.02926, +0.4316] | undecided | **gain** |
| grid_crps, by pressure-day type | month_end | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | +7.6% [-0.3, +16.1] | +0.1605 [+0.04211, +0.4189] | undecided | **gain** |
| upper_tail_twcrps, by pressure-day type | month_end | spread_mr_fhs_mad10_f0.5 against B1 | +9.7% [-3.1, +24.6] | +0.1125 [+0.01396, +0.5355] | undecided | **gain** |
| upper_tail_twcrps, by pressure-day type | month_end | spread_mr_fhs_mad10_f0.5 against B2 | +30.9% [-20.3, +73.2] | +0.4705 [+0.09726, +2.147] | undecided | **gain** |
| upper_tail_twcrps, by pressure-day type | month_end | spread_mr_fhs_mad20_f0.25 against B2 | +32.9% [-5.4, +71.0] | +0.5006 [+0.1048, +2.053] | undecided | **gain** |
| upper_tail_twcrps, by pressure-day type | month_end | spread_mr_fhs_mad20_f0.5 against B2 | +33.2% [-8.9, +71.0] | +0.5055 [+0.1148, +2.045] | undecided | **gain** |
| upper_tail_twcrps, by pressure-day type | month_end | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | +7.8% [-12.4, +29.8] | +0.08654 [+0.0009638, +0.4906] | undecided | **gain** |
| upper_tail_twcrps, by pressure-day type | month_end | spread_mr_fhs_mad20_f1.0 against B2 | +32.8% [-8.3, +69.0] | +0.499 [+0.117, +1.985] | undecided | **gain** |
| upper_tail_twcrps, by pressure-day type | month_end | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | +7.3% [-14.4, +24.4] | +0.08005 [+0.003573, +0.4079] | undecided | **gain** |
| upper_tail_twcrps, by pressure-day type | month_end | spread_mr_fhs_mad40_f0.5 against B2 | +33.7% [-3.2, +69.7] | +0.5134 [+0.1183, +1.953] | undecided | **gain** |
| upper_tail_twcrps, by pressure-day type | month_end | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | +8.6% [-6.6, +28.8] | +0.09445 [+0.01414, +0.523] | undecided | **gain** |
| upper_tail_twcrps, by pressure-day type | month_end | spread_mr_fhs_sd20_f0.5 against B1 | +12.1% [-6.7, +20.6] | +0.1411 [+0.001689, +0.5146] | undecided | **gain** |
| upper_tail_twcrps, by pressure-day type | month_end | spread_mr_fhs_sd20_f0.5 against B2 | +32.8% [-16.0, +55.5] | +0.4991 [+0.09178, +1.576] | undecided | **gain** |
| brier_5, by pressure-day type | ordinary | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | +5.7% [-0.3, +12.8] | +0.002928 [+2.204e-06, +0.007827] | undecided | **gain** |
| brier_5, by pressure-day type | ordinary | spread_mr_fhs_sd20_f0.5 against B2 | +15.2% [-0.3, +28.8] | +0.008666 [+5.432e-05, +0.02001] | undecided | **gain** |
| grid_crps, by pressure-day type | ordinary | spread_mr_fhs_sd20_f0.5 against B2 | +23.4% [-1.2, +36.9] | +0.4918 [+0.05135, +0.8265] | undecided | **gain** |
| grid_crps, by pressure-day type | quarter_end | spread_mr_level10 against B1 | -3.2% [-7.3, -0.4] | -0.2251 [-0.5343, +0.02676] | loss | **undecided** |
| grid_crps, by pressure-day type | tax_date | spread_mr_fhs_mad10_f0.5 against B1 | +6.7% [-3.7, +13.6] | +0.3706 [+0.07494, +1.175] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | spread_mr_fhs_mad10_f0.5 against B2 | +33.8% [-64.5, +57.8] | +2.612 [+1.408, +4.765] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | spread_mr_fhs_mad20_f0.25 against B1 | +6.7% [-3.1, +12.9] | +0.3661 [+0.07103, +1.146] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | spread_mr_fhs_mad20_f0.25 against B2 | +33.7% [-61.9, +57.5] | +2.608 [+1.414, +4.788] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | spread_mr_fhs_mad20_f0.5 against B1 | +6.8% [-6.2, +13.7] | +0.3754 [+0.05328, +1.128] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | spread_mr_fhs_mad20_f0.5 against B2 | +33.8% [-62.9, +57.7] | +2.617 [+1.417, +4.825] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | spread_mr_fhs_mad20_f1.0 against B1 | +6.3% [-4.7, +13.0] | +0.3473 [+0.01495, +1.117] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | spread_mr_fhs_mad20_f1.0 against B2 | +33.5% [-62.1, +57.0] | +2.589 [+1.384, +4.787] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | spread_mr_fhs_mad40_f0.5 against B2 | +32.0% [-62.8, +56.6] | +2.479 [+1.41, +4.439] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | spread_mr_fhs_sd20_f0.5 against B2 | +30.3% [-76.8, +56.0] | +2.347 [+1.366, +3.862] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | spread_mr_level10 against B2 | +30.1% [-71.1, +54.4] | +2.331 [+1.358, +4.061] | undecided | **gain** |
| grid_crps, by regime | 2018-19 | spread_mr_fhs_mad10_f0.5 against B2 | +12.3% [-1.2, +26.0] | +0.549 [+0.05028, +1.083] | undecided | **gain** |
| grid_crps, by regime | 2018-19 | spread_mr_fhs_mad40_f0.5 against B2 | +13.1% [-0.5, +27.6] | +0.5834 [+0.1305, +1.135] | undecided | **gain** |
| grid_crps, by regime | 2018-19 | spread_mr_fhs_sd20_f0.5 against B1 | +17.6% [-0.4, +36.0] | +1.018 [+0.02047, +3.57] | undecided | **gain** |
| grid_crps, by regime | 2018-19 | spread_mr_level10 against B2 | +14.2% [-1.9, +30.2] | +0.6349 [+0.1706, +1.188] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2018-19 | spread_mr_fhs_mad20_f0.25 against B2 | +11.1% [-1.1, +24.2] | +0.4227 [+0.041, +0.8803] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2018-19 | spread_mr_fhs_mad20_f0.5 against B2 | +11.0% [-1.1, +24.2] | +0.419 [+0.03926, +0.8762] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2018-19 | spread_mr_fhs_mad20_f1.0 against B2 | +10.8% [-1.3, +24.2] | +0.4123 [+0.03342, +0.8683] | undecided | **gain** |
| brier_0, by regime | 2020 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | +12.9% [-0.4, +34.6] | +0.01647 [+0.001356, +0.04071] | undecided | **gain** |
| brier_0, by regime | 2020 | spread_mr_level10 against B1 | -11.9% [-28.2, +0.4] | -0.01359 [-0.02914, -0.0003726] | undecided | **loss** |
| brier_10, by regime | 2020 | spread_mr_fhs_mad10_f0.5 against B1 | +38.9% [-12.7, +54.9] | +0.008314 [+0.0006161, +0.2536] | undecided | **gain** |
| brier_10, by regime | 2020 | spread_mr_fhs_mad10_f0.5 against B2 | +42.5% [-475.4, +85.3] | +0.009669 [+0.005442, +0.01528] | undecided | **gain** |
| brier_10, by regime | 2020 | spread_mr_fhs_mad20_f0.25 against B2 | +42.9% [-249.9, +83.9] | +0.009752 [+0.005317, +0.01674] | undecided | **gain** |
| brier_10, by regime | 2020 | spread_mr_fhs_mad20_f0.5 against B1 | +41.2% [-11.0, +70.1] | +0.008822 [+0.000579, +0.3039] | undecided | **gain** |
| brier_10, by regime | 2020 | spread_mr_fhs_mad20_f0.5 against B2 | +44.7% [-429.7, +87.0] | +0.01018 [+0.005839, +0.01708] | undecided | **gain** |
| brier_10, by regime | 2020 | spread_mr_fhs_mad20_f1.0 against B1 | +41.3% [-27.0, +70.1] | +0.008844 [+0.000613, +0.3211] | undecided | **gain** |
| brier_10, by regime | 2020 | spread_mr_fhs_mad20_f1.0 against B2 | +44.8% [-480.4, +87.2] | +0.0102 [+0.005837, +0.01715] | undecided | **gain** |
| brier_10, by regime | 2020 | spread_mr_fhs_mad40_f0.5 against B1 | +44.0% [-13.6, +82.5] | +0.009409 [+0.0004895, +0.5199] | undecided | **gain** |
| brier_10, by regime | 2020 | spread_mr_fhs_mad40_f0.5 against B2 | +47.3% [-559.3, +90.0] | +0.01076 [+0.006031, +0.01951] | undecided | **gain** |
| brier_10, by regime | 2020 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | +8.7% [-92.6, +31.6] | +0.001147 [+0.0003103, +0.001622] | undecided | **gain** |
| brier_10, by regime | 2020 | spread_mr_fhs_sd20_f0.5 against B2 | +40.2% [-177.1, +81.7] | +0.00914 [+0.005408, +0.01394] | undecided | **gain** |
| brier_10, by regime | 2020 | spread_mr_level10 against B1 | +38.6% [+17.2, +266.9] | +0.008263 [-0.00102, +0.6221] | gain | **undecided** |
| brier_10, by regime | 2020 | spread_mr_level10 against B2 | +42.3% [-149.1, +80.6] | +0.009617 [+0.004924, +0.01874] | undecided | **gain** |
| brier_5, by regime | 2020 | spread_mr_fhs_mad10_f0.5 against B2 | +69.1% [-100.3, +94.1] | +0.04412 [+0.0235, +0.07083] | undecided | **gain** |
| brier_5, by regime | 2020 | spread_mr_fhs_mad20_f0.25 against B2 | +67.7% [-64.7, +91.4] | +0.04322 [+0.02186, +0.07024] | undecided | **gain** |
| brier_5, by regime | 2020 | spread_mr_fhs_mad20_f0.5 against B2 | +68.8% [-90.4, +92.6] | +0.04389 [+0.02278, +0.07065] | undecided | **gain** |
| brier_5, by regime | 2020 | spread_mr_fhs_mad20_f1.0 against B1 | +34.9% [-12.6, +47.4] | +0.01047 [+0.003942, +0.05634] | undecided | **gain** |
| brier_5, by regime | 2020 | spread_mr_fhs_mad20_f1.0 against B2 | +69.4% [-129.5, +93.4] | +0.04427 [+0.02343, +0.07092] | undecided | **gain** |
| brier_5, by regime | 2020 | spread_mr_fhs_mad40_f0.5 against B2 | +70.9% [-108.8, +93.3] | +0.04523 [+0.0238, +0.07331] | undecided | **gain** |
| brier_5, by regime | 2020 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | +18.6% [-67.9, +49.5] | +0.00426 [+0.001917, +0.006222] | undecided | **gain** |
| brier_5, by regime | 2020 | spread_mr_fhs_sd20_f0.5 against B1 | +35.2% [-7.1, +50.3] | +0.01056 [+0.003875, +0.03168] | undecided | **gain** |
| brier_5, by regime | 2020 | spread_mr_fhs_sd20_f0.5 against B2 | +69.5% [-134.6, +94.4] | +0.04436 [+0.02475, +0.06807] | undecided | **gain** |
| brier_5, by regime | 2020 | spread_mr_level10 against B1 | +23.9% [+5.6, +116.7] | +0.007174 [-0.001695, +0.1548] | gain | **undecided** |
| brier_5, by regime | 2020 | spread_mr_level10 against B2 | +64.2% [-13.9, +85.7] | +0.04097 [+0.0196, +0.07] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | spread_mr_fhs_mad10_f0.5 against B2 | +59.0% [-13.8, +86.0] | +0.7193 [+0.3823, +1.141] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | spread_mr_fhs_mad20_f0.25 against B2 | +57.2% [-17.0, +84.0] | +0.6971 [+0.3438, +1.124] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | spread_mr_fhs_mad20_f0.5 against B2 | +58.1% [-22.6, +84.9] | +0.7083 [+0.3622, +1.132] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | spread_mr_fhs_mad20_f1.0 against B2 | +57.7% [-24.6, +84.4] | +0.7037 [+0.3611, +1.132] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | spread_mr_fhs_mad40_f0.5 against B2 | +58.7% [-26.5, +85.1] | +0.7158 [+0.3657, +1.155] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | +14.2% [-22.6, +38.0] | +0.08361 [+0.02833, +0.1379] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | spread_mr_fhs_sd20_f0.5 against B2 | +58.8% [-38.4, +86.9] | +0.7165 [+0.4057, +1.075] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | spread_mr_level10 against B1 | +20.7% [+0.0, +102.9] | +0.1533 [-0.0564, +2.36] | gain | **undecided** |
| upper_tail_twcrps, by regime | 2020 | spread_mr_level10 against B2 | +51.9% [-1.8, +76.7] | +0.6322 [+0.2791, +1.094] | undecided | **gain** |
| brier_0, by regime | 2021-23 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | +8.1% [-29.5, +28.9] | +0.0002699 [+3.436e-05, +0.0004918] | undecided | **gain** |
| brier_0, by regime | 2021-23 | spread_mr_fhs_sd20_f0.5 against B1 | +27.1% [-121.4, +46.0] | +0.000788 [+0.0001027, +0.005831] | undecided | **gain** |
| brier_0, by regime | 2021-23 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | +36.4% [-226.4, +61.2] | +0.001215 [+0.0002802, +0.005089] | undecided | **gain** |
| grid_crps, by regime | 2021-23 | spread_mr_fhs_mad10_f0.5 against B1 | +5.9% [-0.3, +10.8] | +0.04095 [+0.001272, +0.07246] | undecided | **gain** |
| grid_crps, by regime | 2021-23 | spread_mr_fhs_sd20_f0.5 against B1 | +7.6% [-0.0, +13.7] | +0.05301 [+0.006312, +0.09139] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | spread_mr_fhs_mad10_f0.5 against B1 | +27.3% [-39.9, +57.0] | +0.002438 [+0.0002305, +0.004609] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | spread_mr_fhs_mad10_f0.5 against B2 | -112.5% [-622.4, -19.6] | -0.003442 [-0.04122, +0.0005993] | loss | **undecided** |
| upper_tail_twcrps, by regime | 2021-23 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | +47.9% [-17.0, +79.0] | +0.005974 [+0.002956, +0.01053] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | spread_mr_fhs_mad20_f0.5 against B2 | -156.2% [-788.6, -35.4] | -0.004779 [-0.0499, +0.0003363] | loss | **undecided** |
| upper_tail_twcrps, by regime | 2021-23 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | +37.2% [-25.3, +74.9] | +0.004637 [+0.002259, +0.008115] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | spread_mr_fhs_mad20_f1.0 against B1 | +26.7% [-41.3, +50.7] | +0.00239 [+0.00018, +0.004743] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | spread_mr_fhs_mad20_f1.0 against B2 | -114.0% [-736.6, -21.5] | -0.003489 [-0.04863, +0.0003514] | loss | **undecided** |
| upper_tail_twcrps, by regime | 2021-23 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | +47.5% [-10.6, +75.9] | +0.005927 [+0.002964, +0.01034] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | spread_mr_fhs_mad40_f0.5 against B2 | -155.9% [-757.3, -40.0] | -0.00477 [-0.0471, +0.0001527] | loss | **undecided** |
| upper_tail_twcrps, by regime | 2021-23 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | +37.2% [-20.5, +72.6] | +0.004647 [+0.002251, +0.008047] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | spread_mr_fhs_sd20_f0.5 against B1 | +67.6% [-19.1, +83.3] | +0.006046 [+0.002612, +0.01672] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | +76.8% [-16.6, +90.5] | +0.009582 [+0.004021, +0.02337] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | spread_mr_level10 against B1 | -39.6% [-75.5, +33.8] | -0.003537 [-0.01041, -0.001234] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2021-23 | spread_mr_level10 against B2 | -307.7% [-508.1, +1.4] | -0.009416 [-0.03075, -0.003587] | undecided | **loss** |
| brier_0, by regime | 2024 | spread_mr_fhs_mad20_f0.25 against B1 | +25.6% [+3.6, +52.2] | +0.008652 [-0.002784, +0.1011] | gain | **undecided** |
| brier_0, by regime | 2024 | spread_mr_fhs_mad20_f1.0 against B1 | +31.7% [-69.8, +114.2] | +0.01074 [+0.001404, +0.1392] | undecided | **gain** |
| brier_0, by regime | 2024 | spread_mr_fhs_sd20_f0.5 against B1 | +24.5% [+8.2, +58.1] | +0.008278 [-0.00107, +0.07288] | gain | **undecided** |
| brier_0, by regime | 2024 | spread_mr_level10 against B1 | +29.0% [-197.9, +117.1] | +0.009821 [+0.0006607, +0.142] | undecided | **gain** |
| brier_0, by regime | 2024 | spread_mr_level10 against B2 | -7.6% [-27.6, +0.6] | -0.001705 [-0.04875, -9.817e-05] | undecided | **loss** |
| grid_crps, by regime | 2024 | spread_mr_fhs_mad20_f0.25 against B2 | +11.2% [+0.1, +20.2] | +0.1568 [-0.001694, +0.3593] | gain | **undecided** |
| brier_0, by regime | 2025-26 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | -21.5% [-64.0, +0.5] | -0.01522 [-0.02729, -0.002089] | undecided | **loss** |
| grid_crps, by regime | 2025-26 | spread_mr_level10 against B2 | +26.6% [+1.0, +46.1] | +1.004 [-0.04731, +2.576] | gain | **undecided** |
| upper_tail_twcrps, by regime | 2025-26 | spread_mr_fhs_mad10_f0.5 against B2 | +24.1% [+2.5, +47.9] | +0.3713 [-0.07231, +1.911] | gain | **undecided** |
| upper_tail_twcrps, by regime | 2025-26 | spread_mr_fhs_mad20_f0.25 against B2 | +24.4% [+3.2, +48.4] | +0.3757 [-0.07332, +2.052] | gain | **undecided** |
| upper_tail_twcrps, by regime | 2025-26 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | +7.9% [+2.2, +13.4] | +0.09143 [-0.001402, +0.3072] | gain | **undecided** |

Every other paired row reads the same on both intervals.

## All paired rows

### brier_0, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=1 | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +10.4% [+1.7, +17.3] | +0.006287 [+0.001122, +0.01177] | gain |
| h=1 | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +51.9% [+37.6, +64.6] | +0.0581 [+0.03248, +0.09147] | gain |
| h=1 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | +1.1% [-4.2, +6.3] | +0.0005725 [-0.002188, +0.00359] | undecided |
| h=1 | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +7.2% [-2.0, +14.2] | +0.004303 [-0.0009023, +0.009619] | undecided |
| h=1 | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +50.1% [+35.4, +63.1] | +0.05612 [+0.03068, +0.08917] | gain |
| h=1 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | -2.6% [-8.5, +3.5] | -0.001412 [-0.004469, +0.001969] | undecided |
| h=1 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +9.3% [+1.2, +15.9] | +0.005603 [+0.000746, +0.01069] | gain |
| h=1 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +51.3% [+37.0, +64.0] | +0.05742 [+0.03206, +0.09041] | gain |
| h=1 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | -0.2% [-5.0, +5.0] | -0.0001113 [-0.002647, +0.002764] | undecided |
| h=1 | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +9.4% [+1.5, +15.9] | +0.005662 [+0.0009916, +0.01063] | gain |
| h=1 | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +51.3% [+36.9, +64.1] | +0.05748 [+0.0321, +0.09066] | gain |
| h=1 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | -0.1% [-4.0, +3.6] | -5.253e-05 [-0.002133, +0.001985] | undecided |
| h=1 | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +9.9% [+1.9, +16.3] | +0.005929 [+0.001219, +0.01089] | gain |
| h=1 | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +51.6% [+37.1, +64.3] | +0.05774 [+0.03238, +0.09087] | gain |
| h=1 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +0.4% [-4.2, +5.3] | +0.0002143 [-0.00221, +0.002945] | undecided |
| h=1 | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +9.7% [-1.6, +17.5] | +0.005854 [-0.0004718, +0.01153] | undecided |
| h=1 | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | +51.5% [+36.9, +64.5] | +0.05767 [+0.0322, +0.0907] | gain |
| h=1 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | +0.3% [-9.6, +8.4] | +0.0001402 [-0.005078, +0.004761] | undecided |
| h=1 | spread_mr_level10 against B1 | 1855 | +9.5% [+1.5, +16.3] | +0.005714 [+0.0008728, +0.01097] | gain |
| h=1 | spread_mr_level10 against B2 | 1855 | +51.4% [+36.8, +64.4] | +0.05753 [+0.03189, +0.09119] | gain |

### brier_10, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=1 | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +30.1% [+20.4, +37.9] | +0.01091 [+0.006082, +0.01768] | gain |
| h=1 | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +14.3% [+1.2, +25.6] | +0.004232 [+0.0004867, +0.00921] | gain |
| h=1 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | +4.0% [-1.4, +8.8] | +0.001053 [-0.0002905, +0.0028] | undecided |
| h=1 | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +29.6% [+18.4, +37.6] | +0.01073 [+0.00567, +0.01738] | gain |
| h=1 | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +13.7% [+1.5, +24.4] | +0.004052 [+0.0005091, +0.008814] | gain |
| h=1 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | +3.3% [-1.3, +7.3] | +0.000873 [-0.0002844, +0.00232] | undecided |
| h=1 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +30.3% [+18.9, +38.3] | +0.01097 [+0.005944, +0.0176] | gain |
| h=1 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +14.6% [+2.5, +25.0] | +0.004298 [+0.0008054, +0.008958] | gain |
| h=1 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | +4.2% [+0.2, +7.9] | +0.001119 [+4.532e-05, +0.002486] | gain |
| h=1 | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +30.4% [+19.0, +38.4] | +0.011 [+0.006006, +0.01761] | gain |
| h=1 | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +14.7% [+2.7, +24.9] | +0.004326 [+0.0008676, +0.0089] | gain |
| h=1 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | +4.4% [+0.8, +7.7] | +0.001147 [+0.0001718, +0.002432] | gain |
| h=1 | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +27.9% [+16.1, +36.1] | +0.0101 [+0.005212, +0.01644] | gain |
| h=1 | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +11.6% [-1.1, +22.8] | +0.003422 [-8.278e-05, +0.008019] | undecided |
| h=1 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +0.9% [-3.5, +5.2] | +0.0002438 [-0.0007946, +0.001571] | undecided |
| h=1 | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +24.5% [+13.0, +33.4] | +0.00886 [+0.004118, +0.01524] | gain |
| h=1 | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | +7.4% [-7.6, +20.0] | +0.002187 [-0.001693, +0.007042] | undecided |
| h=1 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | -3.8% [-12.3, +3.6] | -0.0009921 [-0.0029, +0.0009961] | undecided |
| h=1 | spread_mr_level10 against B1 | 1855 | +27.2% [+15.8, +35.4] | +0.009853 [+0.005171, +0.0157] | gain |
| h=1 | spread_mr_level10 against B2 | 1855 | +10.8% [-0.5, +21.0] | +0.003179 [+8.643e-05, +0.007147] | gain (was undecided) |

### brier_5, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=1 | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +18.8% [+10.7, +25.3] | +0.01064 [+0.005363, +0.01693] | gain |
| h=1 | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +27.6% [+15.3, +39.2] | +0.01752 [+0.007988, +0.03098] | gain |
| h=1 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | +7.1% [+3.0, +12.3] | +0.003534 [+0.001318, +0.007158] | gain |
| h=1 | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +16.8% [+7.5, +23.6] | +0.009537 [+0.00396, +0.01572] | gain |
| h=1 | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +25.8% [+13.7, +37.8] | +0.01641 [+0.007039, +0.02979] | gain |
| h=1 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | +4.9% [+0.7, +9.7] | +0.002428 [+0.0003239, +0.005579] | gain |
| h=1 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +17.3% [+8.0, +24.1] | +0.009821 [+0.004314, +0.01588] | gain |
| h=1 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +26.3% [+14.2, +38.1] | +0.0167 [+0.00739, +0.02985] | gain |
| h=1 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | +5.5% [+1.4, +9.9] | +0.002712 [+0.0007498, +0.00563] | gain |
| h=1 | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +17.0% [+7.8, +23.8] | +0.009619 [+0.004147, +0.01553] | gain |
| h=1 | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +26.0% [+13.9, +37.9] | +0.01649 [+0.00727, +0.02953] | gain |
| h=1 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | +5.1% [+1.4, +9.1] | +0.00251 [+0.0007241, +0.005143] | gain |
| h=1 | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +14.7% [+6.1, +21.3] | +0.008317 [+0.003285, +0.01371] | gain |
| h=1 | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +23.9% [+11.0, +36.6] | +0.01519 [+0.005968, +0.02835] | gain |
| h=1 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +2.4% [-1.5, +6.9] | +0.001208 [-0.0005768, +0.003688] | undecided |
| h=1 | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +18.2% [+10.3, +24.6] | +0.01032 [+0.005173, +0.01642] | gain |
| h=1 | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | +27.1% [+14.8, +39.3] | +0.01719 [+0.007715, +0.03093] | gain |
| h=1 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | +6.5% [+1.8, +12.1] | +0.00321 [+0.0008369, +0.007011] | gain |
| h=1 | spread_mr_level10 against B1 | 1855 | +12.5% [+4.6, +19.0] | +0.007109 [+0.002527, +0.01194] | gain |
| h=1 | spread_mr_level10 against B2 | 1855 | +22.0% [+9.2, +34.5] | +0.01398 [+0.004988, +0.02625] | gain |

### grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=1 | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +22.5% [+17.2, +33.2] | +0.4546 [+0.2488, +1.158] | gain |
| h=1 | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +37.0% [+20.5, +47.4] | +0.9174 [+0.6486, +1.245] | gain |
| h=1 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | +4.3% [+2.4, +6.4] | +0.07069 [+0.03927, +0.1092] | gain |
| h=1 | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +21.8% [+15.7, +33.7] | +0.4402 [+0.2262, +1.154] | gain |
| h=1 | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +36.4% [+20.4, +46.5] | +0.9031 [+0.6382, +1.225] | gain |
| h=1 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | +3.5% [+1.5, +5.5] | +0.05637 [+0.02139, +0.0987] | gain |
| h=1 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +22.8% [+17.1, +34.0] | +0.4601 [+0.2468, +1.181] | gain |
| h=1 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +37.2% [+21.0, +47.4] | +0.923 [+0.659, +1.243] | gain |
| h=1 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | +4.7% [+3.0, +6.4] | +0.0762 [+0.04612, +0.1146] | gain |
| h=1 | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +22.2% [+16.5, +33.8] | +0.4489 [+0.2372, +1.182] | gain |
| h=1 | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +36.8% [+20.7, +46.9] | +0.9118 [+0.6494, +1.231] | gain |
| h=1 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | +4.0% [+2.6, +5.3] | +0.06502 [+0.03986, +0.09801] | gain |
| h=1 | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +21.6% [+15.7, +33.3] | +0.4366 [+0.2266, +1.156] | gain |
| h=1 | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +36.3% [+20.2, +46.5] | +0.8995 [+0.6365, +1.216] | gain |
| h=1 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +3.2% [+1.6, +4.9] | +0.05273 [+0.02408, +0.08646] | gain |
| h=1 | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +15.5% [+7.3, +24.8] | +0.3124 [+0.1292, +0.7325] | gain |
| h=1 | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | +31.3% [+7.5, +45.0] | +0.7753 [+0.3854, +1.119] | gain |
| h=1 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | -4.4% [-29.8, +3.0] | -0.07149 [-0.5003, +0.05431] | undecided |
| h=1 | spread_mr_level10 against B1 | 1855 | +19.0% [+13.0, +31.2] | +0.3839 [+0.1865, +1.075] | gain |
| h=1 | spread_mr_level10 against B2 | 1855 | +34.1% [+17.8, +44.3] | +0.8468 [+0.5846, +1.149] | gain |

### upper_tail_twcrps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=1 | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +31.0% [+25.6, +40.1] | +0.3984 [+0.1909, +1.178] | gain |
| h=1 | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +20.4% [-2.7, +36.8] | +0.2273 [+0.08476, +0.3908] | gain (was undecided) |
| h=1 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | +3.4% [+1.3, +5.5] | +0.03106 [+0.008053, +0.06447] | gain |
| h=1 | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +30.8% [+24.9, +40.5] | +0.3958 [+0.1816, +1.193] | gain |
| h=1 | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +20.2% [-2.8, +36.0] | +0.2247 [+0.08086, +0.3888] | gain (was undecided) |
| h=1 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | +3.1% [+0.7, +5.6] | +0.02853 [+0.002016, +0.06978] | gain |
| h=1 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +31.6% [+25.9, +40.5] | +0.4052 [+0.1916, +1.207] | gain |
| h=1 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +21.0% [-2.7, +37.0] | +0.2341 [+0.09036, +0.3964] | gain (was undecided) |
| h=1 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | +4.1% [+2.0, +6.5] | +0.03794 [+0.0134, +0.07803] | gain |
| h=1 | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +31.4% [+25.8, +40.3] | +0.4036 [+0.192, +1.21] | gain |
| h=1 | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +20.9% [-2.7, +36.8] | +0.2325 [+0.08975, +0.3939] | gain (was undecided) |
| h=1 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | +4.0% [+2.0, +6.0] | +0.03631 [+0.01449, +0.07285] | gain |
| h=1 | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +30.6% [+24.8, +39.7] | +0.3922 [+0.1824, +1.175] | gain |
| h=1 | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +19.9% [-3.0, +36.0] | +0.2211 [+0.0778, +0.3818] | gain (was undecided) |
| h=1 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +2.7% [+0.8, +4.7] | +0.0249 [+0.003536, +0.05751] | gain |
| h=1 | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +23.5% [+13.8, +34.0] | +0.3012 [+0.1209, +0.8656] | gain |
| h=1 | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | +11.7% [-20.9, +31.7] | +0.1301 [-0.1199, +0.3241] | undecided |
| h=1 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | -7.2% [-36.1, +1.6] | -0.06608 [-0.3434, +0.02011] | undecided |
| h=1 | spread_mr_level10 against B1 | 1855 | +28.6% [+23.1, +37.7] | +0.3673 [+0.1705, +1.113] | gain |
| h=1 | spread_mr_level10 against B2 | 1855 | +17.6% [-6.7, +33.6] | +0.1962 [+0.04712, +0.3462] | gain (was undecided) |

### brier_0, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=2 | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +16.3% [+8.8, +22.7] | +0.01082 [+0.005398, +0.01671] | gain |
| h=2 | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +51.0% [+36.5, +63.8] | +0.05792 [+0.03213, +0.0917] | gain |
| h=2 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | +0.8% [-5.1, +6.7] | +0.0004439 [-0.002752, +0.003892] | undecided |
| h=2 | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +13.7% [+5.6, +20.7] | +0.009115 [+0.003556, +0.01526] | gain |
| h=2 | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +49.5% [+34.7, +62.5] | +0.05622 [+0.03052, +0.08948] | gain |
| h=2 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | -2.2% [-8.7, +4.6] | -0.001261 [-0.004701, +0.002606] | undecided |
| h=2 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +15.6% [+8.3, +22.1] | +0.01037 [+0.005179, +0.0162] | gain |
| h=2 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +50.6% [+36.1, +63.5] | +0.05748 [+0.03199, +0.09074] | gain |
| h=2 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | -0.0% [-5.2, +5.7] | -2.851e-06 [-0.002836, +0.003259] | undecided |
| h=2 | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +16.0% [+9.1, +22.1] | +0.01063 [+0.005651, +0.01624] | gain |
| h=2 | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +50.8% [+36.4, +63.7] | +0.05773 [+0.03219, +0.09103] | gain |
| h=2 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | +0.4% [-3.7, +4.6] | +0.0002506 [-0.002028, +0.002576] | undecided |
| h=2 | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +16.5% [+9.1, +22.9] | +0.01094 [+0.00575, +0.01672] | gain |
| h=2 | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +51.1% [+36.9, +63.9] | +0.05804 [+0.03243, +0.0914] | gain |
| h=2 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +1.0% [-3.8, +6.6] | +0.0005624 [-0.002055, +0.00372] | undecided |
| h=2 | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +16.5% [+7.5, +23.6] | +0.01097 [+0.004967, +0.01709] | gain |
| h=2 | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | +51.1% [+36.6, +64.0] | +0.05807 [+0.03259, +0.0913] | gain |
| h=2 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | +1.1% [-8.0, +9.4] | +0.00059 [-0.004401, +0.005452] | undecided |
| h=2 | spread_mr_level10 against B1 | 1855 | +15.6% [+8.8, +21.8] | +0.01038 [+0.00541, +0.01602] | gain |
| h=2 | spread_mr_level10 against B2 | 1855 | +50.6% [+36.2, +63.8] | +0.05748 [+0.03207, +0.09078] | gain |

### brier_10, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=2 | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +29.6% [+22.5, +36.1] | +0.01193 [+0.007309, +0.0183] | gain |
| h=2 | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +6.2% [-8.5, +18.5] | +0.001866 [-0.001979, +0.006346] | undecided |
| h=2 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | +2.5% [-3.4, +7.6] | +0.0007156 [-0.0008075, +0.002594] | undecided |
| h=2 | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +30.0% [+21.3, +37.2] | +0.01211 [+0.007042, +0.01898] | gain |
| h=2 | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +6.8% [-5.7, +18.0] | +0.002051 [-0.001346, +0.006252] | undecided |
| h=2 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | +3.1% [-1.9, +8.2] | +0.0009005 [-0.0005069, +0.00287] | undecided |
| h=2 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +30.8% [+22.0, +38.0] | +0.01241 [+0.007403, +0.01917] | gain |
| h=2 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +7.8% [-4.4, +18.6] | +0.002353 [-0.0009733, +0.006448] | undecided |
| h=2 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | +4.1% [-0.3, +8.5] | +0.001203 [-8.676e-05, +0.002978] | undecided |
| h=2 | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +30.7% [+21.8, +38.0] | +0.01237 [+0.007419, +0.01906] | gain |
| h=2 | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +7.6% [-4.4, +18.2] | +0.002313 [-0.0009692, +0.006255] | undecided |
| h=2 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | +4.0% [-0.1, +7.8] | +0.001162 [+8.893e-07, +0.002715] | gain (was undecided) |
| h=2 | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +29.5% [+20.8, +36.8] | +0.01189 [+0.00698, +0.01851] | gain |
| h=2 | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +6.0% [-6.6, +17.3] | +0.001831 [-0.001578, +0.005978] | undecided |
| h=2 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +2.3% [-2.1, +7.1] | +0.0006811 [-0.0005169, +0.002445] | undecided |
| h=2 | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +24.8% [+16.4, +31.8] | +0.009988 [+0.005574, +0.01594] | gain |
| h=2 | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | -0.2% [-16.0, +12.9] | -7.193e-05 [-0.004127, +0.004414] | undecided |
| h=2 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | -4.2% [-12.7, +2.6] | -0.001222 [-0.003272, +0.0007928] | undecided |
| h=2 | spread_mr_level10 against B1 | 1855 | +27.8% [+18.5, +36.0] | +0.01121 [+0.006578, +0.01742] | gain |
| h=2 | spread_mr_level10 against B2 | 1855 | +3.8% [-7.9, +14.1] | +0.00115 [-0.002024, +0.004575] | undecided |

### brier_5, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=2 | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +17.7% [+9.7, +24.4] | +0.01081 [+0.005269, +0.01735] | gain |
| h=2 | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +22.1% [+8.6, +34.8] | +0.01425 [+0.004879, +0.02674] | gain |
| h=2 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | +6.0% [+1.4, +11.0] | +0.003187 [+0.0006864, +0.006828] | gain |
| h=2 | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +16.2% [+5.9, +24.0] | +0.009868 [+0.00352, +0.01697] | gain |
| h=2 | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +20.7% [+8.0, +33.2] | +0.01331 [+0.004426, +0.02542] | gain |
| h=2 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | +4.2% [-0.9, +9.7] | +0.002247 [-0.0004165, +0.005925] | undecided |
| h=2 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +17.3% [+7.1, +25.0] | +0.01053 [+0.0042, +0.01756] | gain |
| h=2 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +21.7% [+9.3, +33.9] | +0.01397 [+0.005225, +0.02593] | gain |
| h=2 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | +5.5% [+0.6, +10.5] | +0.002906 [+0.0004181, +0.006422] | gain |
| h=2 | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +17.3% [+7.2, +24.9] | +0.01051 [+0.004323, +0.01745] | gain |
| h=2 | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +21.7% [+9.3, +33.9] | +0.01395 [+0.005279, +0.02577] | gain |
| h=2 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | +5.4% [+1.0, +10.1] | +0.002893 [+0.0006227, +0.006138] | gain |
| h=2 | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +15.3% [+5.9, +22.7] | +0.009312 [+0.003426, +0.01577] | gain |
| h=2 | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +19.8% [+6.3, +32.9] | +0.01275 [+0.003727, +0.02484] | gain |
| h=2 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +3.2% [-1.3, +7.8] | +0.00169 [-0.0004792, +0.004585] | undecided |
| h=2 | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +18.2% [+9.6, +24.7] | +0.01107 [+0.005279, +0.01773] | gain |
| h=2 | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | +22.5% [+9.7, +35.1] | +0.01451 [+0.005523, +0.02713] | gain |
| h=2 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | +6.5% [+1.3, +11.8] | +0.003452 [+0.0006357, +0.007393] | gain |
| h=2 | spread_mr_level10 against B1 | 1855 | +12.5% [+3.3, +20.3] | +0.007621 [+0.002061, +0.01364] | gain |
| h=2 | spread_mr_level10 against B2 | 1855 | +17.2% [+3.3, +30.1] | +0.01106 [+0.00216, +0.02224] | gain |

### grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=2 | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +24.5% [+18.7, +38.6] | +0.5418 [+0.3082, +1.483] | gain |
| h=2 | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +33.2% [+20.9, +43.5] | +0.833 [+0.5719, +1.163] | gain |
| h=2 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | +3.6% [+1.3, +5.7] | +0.06335 [+0.02562, +0.1019] | gain |
| h=2 | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +24.0% [+17.4, +40.3] | +0.5324 [+0.2846, +1.515] | gain |
| h=2 | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +32.9% [+21.2, +42.8] | +0.8236 [+0.5698, +1.151] | gain |
| h=2 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | +3.1% [+1.0, +5.2] | +0.05396 [+0.01617, +0.1001] | gain |
| h=2 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +25.2% [+18.9, +40.5] | +0.5588 [+0.3121, +1.545] | gain |
| h=2 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +33.9% [+22.0, +43.7] | +0.85 [+0.5965, +1.176] | gain |
| h=2 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | +4.6% [+2.9, +6.4] | +0.08036 [+0.04829, +0.1218] | gain |
| h=2 | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +24.6% [+18.2, +40.4] | +0.546 [+0.301, +1.541] | gain |
| h=2 | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +33.4% [+21.6, +43.1] | +0.8373 [+0.5851, +1.158] | gain |
| h=2 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | +3.9% [+2.5, +5.3] | +0.06764 [+0.04145, +0.1031] | gain |
| h=2 | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +24.1% [+17.7, +39.1] | +0.5337 [+0.293, +1.486] | gain |
| h=2 | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +32.9% [+21.0, +42.8] | +0.825 [+0.5736, +1.146] | gain |
| h=2 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +3.2% [+1.5, +4.9] | +0.0553 [+0.02473, +0.09046] | gain |
| h=2 | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +17.3% [+9.0, +27.8] | +0.3833 [+0.1743, +0.9041] | gain |
| h=2 | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | +26.9% [+6.4, +40.3] | +0.6745 [+0.2824, +1.018] | gain |
| h=2 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | -5.5% [-32.3, +2.4] | -0.09512 [-0.5931, +0.05018] | undecided |
| h=2 | spread_mr_level10 against B1 | 1855 | +21.6% [+15.1, +37.6] | +0.4784 [+0.2465, +1.413] | gain |
| h=2 | spread_mr_level10 against B2 | 1855 | +30.7% [+18.6, +40.4] | +0.7697 [+0.5243, +1.072] | gain |

### upper_tail_twcrps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=2 | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +32.7% [+26.0, +47.1] | +0.4426 [+0.2066, +1.534] | gain |
| h=2 | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +19.1% [+3.2, +34.2] | +0.215 [+0.08875, +0.3797] | gain |
| h=2 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | +1.8% [-1.4, +4.4] | +0.01655 [-0.01035, +0.04798] | undecided |
| h=2 | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +33.1% [+25.7, +49.2] | +0.4482 [+0.2, +1.561] | gain |
| h=2 | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +19.6% [+4.8, +33.9] | +0.2206 [+0.09854, +0.3861] | gain |
| h=2 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | +2.4% [-0.8, +5.5] | +0.02216 [-0.007617, +0.07041] | undecided |
| h=2 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +34.1% [+27.0, +48.6] | +0.4614 [+0.2141, +1.578] | gain |
| h=2 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +20.8% [+5.1, +35.2] | +0.2338 [+0.1128, +0.3967] | gain |
| h=2 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | +3.8% [+1.3, +6.6] | +0.03541 [+0.008702, +0.08128] | gain |
| h=2 | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +34.0% [+27.0, +48.3] | +0.4606 [+0.2147, +1.575] | gain |
| h=2 | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +20.7% [+5.0, +35.1] | +0.233 [+0.1126, +0.3938] | gain |
| h=2 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | +3.7% [+1.5, +6.1] | +0.03456 [+0.01039, +0.0757] | gain |
| h=2 | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +33.3% [+26.3, +47.1] | +0.4503 [+0.209, +1.506] | gain |
| h=2 | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +19.8% [+3.7, +34.5] | +0.2227 [+0.1003, +0.3863] | gain |
| h=2 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +2.6% [+0.6, +4.8] | +0.02425 [+0.002355, +0.05596] | gain |
| h=2 | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +24.4% [+13.8, +38.4] | +0.3302 [+0.1265, +1.041] | gain |
| h=2 | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | +9.1% [-19.2, +27.4] | +0.1027 [-0.1521, +0.2943] | undecided |
| h=2 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | -10.3% [-43.8, -0.1] | -0.09576 [-0.4473, +0.008253] | undecided (was loss) |
| h=2 | spread_mr_level10 against B1 | 1855 | +31.5% [+24.6, +45.5] | +0.426 [+0.1956, +1.448] | gain |
| h=2 | spread_mr_level10 against B2 | 1855 | +17.6% [+1.0, +32.0] | +0.1984 [+0.08012, +0.347] | gain |

### brier_0, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=3 | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +16.5% [+9.2, +23.4] | +0.01136 [+0.00599, +0.01771] | gain |
| h=3 | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +49.9% [+35.3, +62.9] | +0.05723 [+0.03135, +0.09078] | gain |
| h=3 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | +0.3% [-5.7, +6.5] | +0.0002003 [-0.003136, +0.003876] | undecided |
| h=3 | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +14.4% [+6.4, +22.0] | +0.009865 [+0.004188, +0.01655] | gain |
| h=3 | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +48.6% [+34.0, +61.7] | +0.05574 [+0.03014, +0.08902] | gain |
| h=3 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | -2.2% [-8.8, +4.7] | -0.001293 [-0.004881, +0.002816] | undecided |
| h=3 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +16.3% [+8.8, +23.5] | +0.01119 [+0.005821, +0.01759] | gain |
| h=3 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +49.8% [+35.5, +62.7] | +0.05706 [+0.03156, +0.09038] | gain |
| h=3 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | +0.1% [-5.1, +5.8] | +3.092e-05 [-0.002877, +0.003454] | undecided |
| h=3 | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +16.8% [+9.6, +23.5] | +0.01152 [+0.006397, +0.01765] | gain |
| h=3 | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +50.1% [+35.9, +63.0] | +0.05739 [+0.03178, +0.09077] | gain |
| h=3 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | +0.6% [-3.5, +4.9] | +0.0003618 [-0.002003, +0.002848] | undecided |
| h=3 | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +17.6% [+9.6, +25.0] | +0.01212 [+0.006449, +0.01879] | gain |
| h=3 | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +50.6% [+36.6, +63.3] | +0.05799 [+0.03255, +0.09105] | gain |
| h=3 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +1.7% [-3.1, +7.4] | +0.0009615 [-0.001743, +0.004263] | undecided |
| h=3 | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +17.2% [+8.2, +25.2] | +0.01183 [+0.005619, +0.01874] | gain |
| h=3 | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | +50.4% [+36.0, +63.3] | +0.05771 [+0.03208, +0.09104] | gain |
| h=3 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | +1.2% [-7.8, +9.6] | +0.0006753 [-0.004361, +0.005748] | undecided |
| h=3 | spread_mr_level10 against B1 | 1855 | +16.2% [+9.5, +22.9] | +0.01116 [+0.006131, +0.0172] | gain |
| h=3 | spread_mr_level10 against B2 | 1855 | +49.8% [+35.4, +63.0] | +0.05703 [+0.03149, +0.09027] | gain |

### brier_10, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=3 | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +33.0% [+26.2, +39.4] | +0.01451 [+0.009029, +0.02218] | gain |
| h=3 | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +4.4% [-8.9, +15.6] | +0.001351 [-0.002189, +0.005462] | undecided |
| h=3 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | +1.9% [-4.7, +7.6] | +0.0005678 [-0.001178, +0.002666] | undecided |
| h=3 | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +33.9% [+25.3, +41.2] | +0.01492 [+0.008912, +0.02324] | gain |
| h=3 | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +5.7% [-6.8, +16.3] | +0.001762 [-0.001656, +0.005697] | undecided |
| h=3 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | +3.3% [-2.3, +8.4] | +0.0009789 [-0.0005807, +0.003061] | undecided |
| h=3 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +34.6% [+26.0, +42.0] | +0.01523 [+0.009256, +0.02341] | gain |
| h=3 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +6.7% [-5.5, +16.9] | +0.002069 [-0.001259, +0.005855] | undecided |
| h=3 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | +4.3% [-0.6, +8.7] | +0.001286 [-0.0001292, +0.003155] | undecided |
| h=3 | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +34.5% [+25.8, +42.0] | +0.01519 [+0.009254, +0.02329] | gain |
| h=3 | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +6.6% [-5.5, +16.4] | +0.002024 [-0.001247, +0.00567] | undecided |
| h=3 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | +4.1% [-0.3, +8.1] | +0.00124 [-4.015e-05, +0.002886] | undecided |
| h=3 | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +33.5% [+24.8, +41.0] | +0.01472 [+0.008874, +0.02281] | gain |
| h=3 | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +5.0% [-7.1, +15.6] | +0.001555 [-0.00179, +0.005383] | undecided |
| h=3 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +2.6% [-2.1, +7.5] | +0.0007713 [-0.0005492, +0.002666] | undecided |
| h=3 | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +28.0% [+19.7, +35.2] | +0.01231 [+0.007093, +0.01956] | gain |
| h=3 | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | -2.8% [-18.4, +10.0] | -0.0008479 [-0.005011, +0.003461] | undecided |
| h=3 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | -5.4% [-15.2, +2.2] | -0.001631 [-0.004025, +0.000653] | undecided |
| h=3 | spread_mr_level10 against B1 | 1855 | +31.7% [+22.6, +40.2] | +0.01395 [+0.008434, +0.02164] | gain |
| h=3 | spread_mr_level10 against B2 | 1855 | +2.5% [-8.2, +11.8] | +0.0007832 [-0.002246, +0.003869] | undecided |

### brier_5, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=3 | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +19.6% [+10.6, +27.0] | +0.01283 [+0.006287, +0.02065] | gain |
| h=3 | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +19.3% [+5.5, +32.2] | +0.01254 [+0.003328, +0.02469] | gain |
| h=3 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | +6.4% [+0.7, +12.7] | +0.003593 [+0.0003204, +0.008386] | gain |
| h=3 | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +18.9% [+8.0, +27.5] | +0.01235 [+0.004997, +0.02113] | gain |
| h=3 | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +18.5% [+5.6, +31.2] | +0.01206 [+0.003258, +0.02402] | gain |
| h=3 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | +5.5% [-0.3, +11.9] | +0.003112 [-0.000158, +0.007881] | undecided |
| h=3 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +19.8% [+8.9, +28.4] | +0.01296 [+0.005685, +0.02164] | gain |
| h=3 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +19.5% [+6.8, +31.8] | +0.01267 [+0.004053, +0.02434] | gain |
| h=3 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | +6.6% [+1.3, +12.4] | +0.003726 [+0.000724, +0.008231] | gain |
| h=3 | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +19.7% [+8.8, +28.3] | +0.01289 [+0.005724, +0.02134] | gain |
| h=3 | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +19.4% [+6.7, +31.6] | +0.0126 [+0.004079, +0.02401] | gain |
| h=3 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | +6.5% [+1.6, +11.8] | +0.003656 [+0.0008613, +0.007759] | gain |
| h=3 | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +17.8% [+6.7, +26.7] | +0.01165 [+0.004444, +0.01976] | gain |
| h=3 | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +17.5% [+3.8, +30.6] | +0.01136 [+0.002426, +0.02308] | gain |
| h=3 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +4.3% [-1.0, +10.1] | +0.00241 [-0.0003375, +0.006373] | undecided |
| h=3 | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +20.1% [+10.6, +27.7] | +0.01317 [+0.006302, +0.02133] | gain |
| h=3 | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | +19.8% [+6.7, +32.6] | +0.01288 [+0.004009, +0.02514] | gain |
| h=3 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | +7.0% [+0.6, +13.8] | +0.003935 [+0.0002915, +0.009199] | gain |
| h=3 | spread_mr_level10 against B1 | 1855 | +14.1% [+2.6, +23.2] | +0.009236 [+0.002127, +0.01671] | gain |
| h=3 | spread_mr_level10 against B2 | 1855 | +13.7% [-0.9, +27.0] | +0.008947 [-0.0001244, +0.01989] | undecided |

### grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=3 | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +25.5% [+19.7, +40.0] | +0.597 [+0.3514, +1.527] | gain |
| h=3 | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +31.0% [+20.2, +41.1] | +0.782 [+0.5197, +1.111] | gain |
| h=3 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | +3.2% [+0.5, +5.4] | +0.0568 [+0.01283, +0.1015] | gain |
| h=3 | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +25.6% [+19.0, +41.9] | +0.5981 [+0.3372, +1.569] | gain |
| h=3 | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +31.0% [+20.9, +40.7] | +0.7831 [+0.5268, +1.109] | gain |
| h=3 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | +3.2% [+1.0, +5.4] | +0.05791 [+0.01715, +0.1091] | gain |
| h=3 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +26.6% [+20.4, +42.0] | +0.6229 [+0.3633, +1.603] | gain |
| h=3 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +32.0% [+21.7, +41.6] | +0.8079 [+0.5546, +1.128] | gain |
| h=3 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | +4.6% [+2.9, +6.4] | +0.08268 [+0.04821, +0.1274] | gain |
| h=3 | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +26.1% [+19.7, +41.7] | +0.6091 [+0.3515, +1.594] | gain |
| h=3 | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +31.5% [+21.1, +41.0] | +0.7942 [+0.5422, +1.111] | gain |
| h=3 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | +3.8% [+2.4, +5.2] | +0.06895 [+0.04154, +0.105] | gain |
| h=3 | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +25.4% [+19.1, +40.3] | +0.5941 [+0.3422, +1.536] | gain |
| h=3 | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +30.9% [+20.3, +40.7] | +0.7791 [+0.5272, +1.099] | gain |
| h=3 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +3.0% [+1.2, +4.9] | +0.05386 [+0.02059, +0.09158] | gain |
| h=3 | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +18.4% [+10.2, +28.5] | +0.4308 [+0.2103, +0.9371] | gain |
| h=3 | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | +24.4% [+4.7, +37.6] | +0.6158 [+0.2105, +0.9633] | gain |
| h=3 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | -6.1% [-35.1, +2.3] | -0.1094 [-0.6644, +0.05031] | undecided |
| h=3 | spread_mr_level10 against B1 | 1855 | +23.1% [+16.6, +39.0] | +0.5402 [+0.2964, +1.464] | gain |
| h=3 | spread_mr_level10 against B2 | 1855 | +28.7% [+18.2, +38.2] | +0.7252 [+0.4805, +1.026] | gain |

### upper_tail_twcrps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=3 | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +33.8% [+26.3, +50.4] | +0.473 [+0.2278, +1.578] | gain |
| h=3 | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +18.4% [+5.9, +32.0] | +0.2086 [+0.08671, +0.3706] | gain |
| h=3 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | +0.6% [-3.7, +4.1] | +0.005752 [-0.02772, +0.04252] | undecided |
| h=3 | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +34.8% [+26.8, +52.3] | +0.4864 [+0.2271, +1.611] | gain |
| h=3 | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +19.6% [+7.6, +32.8] | +0.222 [+0.1027, +0.3865] | gain |
| h=3 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | +2.1% [-1.6, +5.4] | +0.01918 [-0.01245, +0.06792] | undecided |
| h=3 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +35.8% [+28.0, +51.8] | +0.5003 [+0.2418, +1.616] | gain |
| h=3 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +20.8% [+8.2, +34.1] | +0.2359 [+0.1179, +0.3978] | gain |
| h=3 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | +3.6% [+0.8, +6.2] | +0.03307 [+0.004848, +0.07903] | gain |
| h=3 | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +35.8% [+28.0, +51.4] | +0.5002 [+0.243, +1.6] | gain |
| h=3 | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +20.8% [+8.0, +34.1] | +0.2359 [+0.1195, +0.3949] | gain |
| h=3 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | +3.5% [+1.2, +5.8] | +0.03301 [+0.007936, +0.07392] | gain |
| h=3 | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +35.1% [+27.3, +49.9] | +0.4906 [+0.2403, +1.526] | gain |
| h=3 | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +20.0% [+6.3, +34.0] | +0.2263 [+0.1083, +0.3929] | gain |
| h=3 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +2.5% [+0.3, +5.0] | +0.02343 [+0.0007926, +0.05468] | gain |
| h=3 | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +25.2% [+13.9, +39.5] | +0.3525 [+0.1414, +1.022] | gain |
| h=3 | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | +7.8% [-21.0, +25.4] | +0.08812 [-0.1852, +0.2861] | undecided |
| h=3 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | -12.3% [-51.7, -0.9] | -0.1147 [-0.5315, +0.003964] | undecided (was loss) |
| h=3 | spread_mr_level10 against B1 | 1855 | +33.4% [+25.6, +48.4] | +0.4672 [+0.2252, +1.492] | gain |
| h=3 | spread_mr_level10 against B2 | 1855 | +17.9% [+4.2, +31.2] | +0.2029 [+0.09308, +0.3502] | gain |

### brier_0, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=4 | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +16.7% [+8.9, +24.0] | +0.01192 [+0.00606, +0.01883] | gain |
| h=4 | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +48.4% [+33.6, +61.7] | +0.05594 [+0.02986, +0.0893] | gain |
| h=4 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | -0.9% [-7.0, +5.6] | -0.0005029 [-0.004025, +0.00339] | undecided |
| h=4 | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +14.5% [+6.3, +22.4] | +0.01033 [+0.004116, +0.01765] | gain |
| h=4 | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +47.1% [+32.1, +60.4] | +0.05436 [+0.0286, +0.08759] | gain |
| h=4 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | -3.5% [-10.2, +3.8] | -0.00209 [-0.005784, +0.002427] | undecided |
| h=4 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +16.7% [+8.9, +24.3] | +0.01196 [+0.005962, +0.01909] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +48.5% [+34.0, +61.6] | +0.05598 [+0.03036, +0.08911] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | -0.8% [-6.1, +5.6] | -0.0004638 [-0.003554, +0.003436] | undecided |
| h=4 | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +17.2% [+9.3, +24.7] | +0.01229 [+0.006379, +0.01932] | gain |
| h=4 | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +48.7% [+34.3, +62.0] | +0.05632 [+0.03067, +0.08952] | gain |
| h=4 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | -0.2% [-4.4, +4.4] | -0.0001296 [-0.002604, +0.002597] | undecided |
| h=4 | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +18.9% [+10.5, +26.9] | +0.01351 [+0.007216, +0.02108] | gain |
| h=4 | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +49.8% [+35.7, +62.6] | +0.05753 [+0.03199, +0.09042] | gain |
| h=4 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +1.8% [-3.4, +8.4] | +0.001088 [-0.001948, +0.005046] | undecided |
| h=4 | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +18.1% [+8.7, +26.4] | +0.01294 [+0.006092, +0.02053] | gain |
| h=4 | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | +49.3% [+35.0, +62.4] | +0.05696 [+0.03134, +0.09012] | gain |
| h=4 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | +0.9% [-8.2, +9.7] | +0.0005179 [-0.004747, +0.005976] | undecided |
| h=4 | spread_mr_level10 against B1 | 1855 | +17.4% [+9.6, +25.2] | +0.01242 [+0.006567, +0.0197] | gain |
| h=4 | spread_mr_level10 against B2 | 1855 | +48.9% [+34.2, +62.3] | +0.05645 [+0.03076, +0.09016] | gain |

### brier_10, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=4 | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +35.9% [+29.0, +42.1] | +0.01648 [+0.009899, +0.02572] | gain |
| h=4 | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +4.6% [-9.0, +15.5] | +0.001413 [-0.00225, +0.005491] | undecided |
| h=4 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | +2.0% [-5.5, +8.3] | +0.0006162 [-0.001334, +0.00293] | undecided |
| h=4 | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +35.9% [+26.5, +43.4] | +0.01648 [+0.009315, +0.02628] | gain |
| h=4 | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +4.6% [-8.5, +14.8] | +0.001405 [-0.002146, +0.005264] | undecided |
| h=4 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | +2.0% [-4.3, +8.0] | +0.0006088 [-0.001106, +0.002819] | undecided |
| h=4 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +36.7% [+27.4, +44.2] | +0.01684 [+0.00975, +0.02657] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +5.7% [-6.9, +15.6] | +0.001765 [-0.001706, +0.005457] | undecided |
| h=4 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | +3.2% [-2.3, +8.4] | +0.0009687 [-0.0005645, +0.002948] | undecided |
| h=4 | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +36.9% [+27.6, +44.4] | +0.01695 [+0.009893, +0.02665] | gain |
| h=4 | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +6.1% [-6.2, +15.7] | +0.001878 [-0.001502, +0.005448] | undecided |
| h=4 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | +3.6% [-1.4, +8.1] | +0.001081 [-0.0003208, +0.002854] | undecided |
| h=4 | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +35.9% [+26.6, +43.7] | +0.01651 [+0.009465, +0.02621] | gain |
| h=4 | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +4.7% [-7.8, +14.8] | +0.001443 [-0.002013, +0.00515] | undecided |
| h=4 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +2.1% [-3.2, +7.7] | +0.0006463 [-0.0008352, +0.002697] | undecided |
| h=4 | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +29.3% [+20.0, +37.2] | +0.01346 [+0.007244, +0.02202] | gain |
| h=4 | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | -5.2% [-22.1, +7.6] | -0.001615 [-0.006071, +0.002704] | undecided |
| h=4 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | -8.0% [-19.6, +0.6] | -0.002412 [-0.005307, +9.394e-05] | undecided |
| h=4 | spread_mr_level10 against B1 | 1855 | +34.5% [+25.0, +43.2] | +0.01587 [+0.009223, +0.0251] | gain |
| h=4 | spread_mr_level10 against B2 | 1855 | +2.6% [-8.4, +11.4] | +0.0007964 [-0.002318, +0.003779] | undecided |

### brier_5, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=4 | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +22.3% [+13.1, +30.1] | +0.01507 [+0.007858, +0.02409] | gain |
| h=4 | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +19.8% [+6.3, +32.9] | +0.01302 [+0.003716, +0.02553] | gain |
| h=4 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | +8.4% [+2.2, +15.1] | +0.004838 [+0.00104, +0.01042] | gain |
| h=4 | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +20.9% [+10.3, +29.8] | +0.01412 [+0.006345, +0.02384] | gain |
| h=4 | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +18.4% [+5.2, +31.2] | +0.01207 [+0.003113, +0.02431] | gain |
| h=4 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | +6.8% [+0.7, +13.0] | +0.003886 [+0.0003305, +0.009161] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +22.0% [+11.5, +31.0] | +0.01491 [+0.007188, +0.02452] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +19.6% [+6.7, +32.2] | +0.01286 [+0.004077, +0.02486] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | +8.1% [+2.7, +13.8] | +0.004675 [+0.001384, +0.00967] | gain |
| h=4 | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +21.7% [+10.9, +30.9] | +0.01471 [+0.007, +0.02414] | gain |
| h=4 | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +19.3% [+6.6, +31.6] | +0.01265 [+0.003983, +0.02424] | gain |
| h=4 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | +7.8% [+2.8, +13.0] | +0.004471 [+0.001436, +0.009014] | gain |
| h=4 | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +19.3% [+8.2, +28.9] | +0.01307 [+0.005468, +0.02225] | gain |
| h=4 | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +16.8% [+3.0, +30.2] | +0.01101 [+0.001946, +0.02279] | gain |
| h=4 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +4.9% [-0.5, +10.6] | +0.00283 [-9.335e-05, +0.006912] | undecided |
| h=4 | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +20.7% [+10.8, +28.9] | +0.01401 [+0.006613, +0.0229] | gain |
| h=4 | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | +18.2% [+4.9, +31.0] | +0.01196 [+0.003066, +0.02396] | gain |
| h=4 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | +6.6% [-0.6, +14.2] | +0.003775 [-0.0002263, +0.009625] | undecided |
| h=4 | spread_mr_level10 against B1 | 1855 | +15.1% [+3.1, +25.7] | +0.01024 [+0.002661, +0.01916] | gain |
| h=4 | spread_mr_level10 against B2 | 1855 | +12.5% [-2.6, +25.7] | +0.008182 [-0.0009986, +0.01886] | undecided |

### grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=4 | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +25.9% [+19.6, +41.8] | +0.6248 [+0.3652, +1.57] | gain |
| h=4 | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +29.6% [+19.6, +39.3] | +0.7499 [+0.4877, +1.072] | gain |
| h=4 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | +3.0% [+0.1, +5.3] | +0.05522 [+0.006582, +0.1023] | gain |
| h=4 | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +26.0% [+19.0, +44.0] | +0.6259 [+0.3482, +1.623] | gain |
| h=4 | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +29.6% [+20.4, +39.0] | +0.7511 [+0.4977, +1.07] | gain |
| h=4 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | +3.1% [+0.7, +5.4] | +0.05635 [+0.01242, +0.1107] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +27.1% [+20.3, +44.3] | +0.6518 [+0.3759, +1.657] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +30.7% [+21.3, +39.9] | +0.7769 [+0.5263, +1.093] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | +4.5% [+2.6, +6.3] | +0.08222 [+0.04504, +0.1292] | gain |
| h=4 | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +26.6% [+19.7, +44.1] | +0.6395 [+0.3645, +1.658] | gain |
| h=4 | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +30.2% [+20.8, +39.3] | +0.7647 [+0.5131, +1.077] | gain |
| h=4 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | +3.8% [+2.3, +5.2] | +0.06998 [+0.04067, +0.1099] | gain |
| h=4 | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +25.8% [+19.0, +42.4] | +0.6209 [+0.3545, +1.596] | gain |
| h=4 | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +29.4% [+19.5, +38.9] | +0.7461 [+0.4916, +1.064] | gain |
| h=4 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +2.8% [+0.8, +5.0] | +0.05136 [+0.01418, +0.09256] | gain |
| h=4 | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +18.5% [+10.1, +29.1] | +0.4464 [+0.2196, +0.9647] | gain |
| h=4 | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | +22.6% [+3.3, +35.5] | +0.5716 [+0.1552, +0.9184] | gain |
| h=4 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | -6.7% [-37.4, +2.2] | -0.1231 [-0.717, +0.04947] | undecided |
| h=4 | spread_mr_level10 against B1 | 1855 | +23.6% [+16.7, +41.3] | +0.5695 [+0.3094, +1.536] | gain |
| h=4 | spread_mr_level10 against B2 | 1855 | +27.4% [+17.7, +36.5] | +0.6947 [+0.4509, +0.9922] | gain |

### upper_tail_twcrps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=4 | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +34.5% [+25.7, +54.8] | +0.489 [+0.2301, +1.652] | gain |
| h=4 | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +18.3% [+7.2, +30.4] | +0.2083 [+0.08617, +0.3686] | gain |
| h=4 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | +0.0% [-4.9, +4.0] | +0.0003991 [-0.03732, +0.03991] | undecided |
| h=4 | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +35.4% [+26.0, +56.9] | +0.5024 [+0.2269, +1.688] | gain |
| h=4 | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +19.5% [+9.3, +31.2] | +0.2218 [+0.1018, +0.3835] | gain |
| h=4 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | +1.5% [-2.7, +5.5] | +0.01384 [-0.0197, +0.06542] | undecided |
| h=4 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +36.6% [+27.4, +56.5] | +0.519 [+0.2443, +1.703] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +20.9% [+10.4, +32.7] | +0.2384 [+0.1205, +0.398] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | +3.3% [+0.1, +6.3] | +0.03043 [+0.0008766, +0.07946] | gain |
| h=4 | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +36.7% [+27.5, +56.1] | +0.5205 [+0.2471, +1.694] | gain |
| h=4 | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +21.1% [+10.4, +32.9] | +0.2399 [+0.1234, +0.3978] | gain |
| h=4 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | +3.4% [+0.7, +6.0] | +0.03194 [+0.005214, +0.07703] | gain |
| h=4 | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +36.0% [+26.7, +54.2] | +0.5106 [+0.2467, +1.606] | gain |
| h=4 | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +20.2% [+8.1, +33.2] | +0.2299 [+0.1134, +0.3941] | gain |
| h=4 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +2.4% [-0.0, +5.2] | +0.02196 [-0.0009769, +0.05378] | undecided |
| h=4 | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +25.3% [+13.4, +41.2] | +0.3584 [+0.1412, +1.041] | gain |
| h=4 | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | +6.8% [-21.9, +24.0] | +0.07777 [-0.2078, +0.2765] | undecided |
| h=4 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | -14.0% [-56.9, -1.2] | -0.1302 [-0.5879, +0.00113] | undecided (was loss) |
| h=4 | spread_mr_level10 against B1 | 1855 | +34.4% [+25.0, +53.0] | +0.4886 [+0.2318, +1.578] | gain |
| h=4 | spread_mr_level10 against B2 | 1855 | +18.3% [+6.6, +30.4] | +0.2079 [+0.1025, +0.3524] | gain |

### brier_0, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=5 | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +17.2% [+9.1, +24.7] | +0.01262 [+0.006202, +0.02003] | gain |
| h=5 | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +47.7% [+32.8, +61.0] | +0.05545 [+0.02952, +0.08898] | gain |
| h=5 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | -0.8% [-7.0, +5.4] | -0.000489 [-0.004071, +0.003386] | undecided |
| h=5 | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +14.5% [+5.8, +22.8] | +0.01061 [+0.003868, +0.01832] | gain |
| h=5 | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +46.0% [+30.8, +59.6] | +0.05345 [+0.02768, +0.0867] | gain |
| h=5 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | -4.1% [-10.7, +3.4] | -0.002496 [-0.006238, +0.002173] | undecided |
| h=5 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +16.6% [+8.3, +24.6] | +0.0122 [+0.005698, +0.01976] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +47.4% [+32.6, +60.7] | +0.05504 [+0.02934, +0.08836] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | -1.5% [-7.0, +5.0] | -0.0009001 [-0.004117, +0.003143] | undecided |
| h=5 | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +16.9% [+8.6, +24.7] | +0.0124 [+0.006116, +0.0199] | gain |
| h=5 | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +47.5% [+32.8, +61.0] | +0.05524 [+0.02947, +0.08877] | gain |
| h=5 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | -1.2% [-5.5, +3.4] | -0.0007074 [-0.003268, +0.002029] | undecided |
| h=5 | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +18.7% [+10.0, +27.0] | +0.01373 [+0.006933, +0.02174] | gain |
| h=5 | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +48.7% [+34.2, +61.7] | +0.05657 [+0.03099, +0.08973] | gain |
| h=5 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +1.0% [-4.3, +7.8] | +0.0006279 [-0.002514, +0.004705] | undecided |
| h=5 | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +18.2% [+8.8, +26.6] | +0.01339 [+0.00624, +0.02128] | gain |
| h=5 | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | +48.4% [+33.8, +61.6] | +0.05622 [+0.03068, +0.08926] | gain |
| h=5 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | +0.5% [-8.6, +9.4] | +0.0002819 [-0.005076, +0.005892] | undecided |
| h=5 | spread_mr_level10 against B1 | 1855 | +17.9% [+9.5, +26.0] | +0.0131 [+0.006567, +0.02099] | gain |
| h=5 | spread_mr_level10 against B2 | 1855 | +48.1% [+33.3, +61.7] | +0.05594 [+0.03004, +0.08993] | gain |

### brier_10, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=5 | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +35.6% [+29.3, +42.0] | +0.01671 [+0.01011, +0.0262] | gain |
| h=5 | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +3.8% [-9.7, +14.5] | +0.001204 [-0.002511, +0.005201] | undecided |
| h=5 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | +1.0% [-7.1, +7.6] | +0.000294 [-0.001805, +0.002658] | undecided |
| h=5 | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +35.3% [+27.3, +42.6] | +0.01657 [+0.009535, +0.02673] | gain |
| h=5 | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +3.4% [-10.1, +13.9] | +0.001063 [-0.002638, +0.005015] | undecided |
| h=5 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | +0.5% [-6.5, +7.4] | +0.0001537 [-0.001711, +0.002599] | undecided |
| h=5 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +36.3% [+28.3, +43.5] | +0.01701 [+0.01007, +0.02702] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +4.8% [-8.3, +14.8] | +0.001507 [-0.002098, +0.005276] | undecided |
| h=5 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | +2.0% [-4.3, +7.9] | +0.0005974 [-0.001101, +0.002769] | undecided |
| h=5 | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +36.3% [+28.3, +43.7] | +0.01702 [+0.01011, +0.02687] | gain |
| h=5 | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +4.8% [-7.9, +14.4] | +0.001512 [-0.002005, +0.005077] | undecided |
| h=5 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | +2.0% [-3.5, +7.0] | +0.0006024 [-0.0008971, +0.00245] | undecided |
| h=5 | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +36.2% [+28.2, +43.8] | +0.01699 [+0.01004, +0.02706] | gain |
| h=5 | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +4.7% [-7.7, +14.5] | +0.001482 [-0.001999, +0.005136] | undecided |
| h=5 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +1.9% [-3.8, +7.5] | +0.0005719 [-0.0009818, +0.002665] | undecided |
| h=5 | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +28.4% [+20.1, +36.2] | +0.01334 [+0.007244, +0.02208] | gain |
| h=5 | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | -6.9% [-24.4, +6.2] | -0.002166 [-0.006925, +0.002284] | undecided |
| h=5 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | -10.1% [-23.1, -0.3] | -0.003075 [-0.006486, -0.000196] | loss |
| h=5 | spread_mr_level10 against B1 | 1855 | +35.0% [+26.3, +43.8] | +0.01642 [+0.009684, +0.02601] | gain |
| h=5 | spread_mr_level10 against B2 | 1855 | +2.9% [-7.6, +11.4] | +0.0009097 [-0.002116, +0.003811] | undecided |

### brier_5, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=5 | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +20.7% [+11.3, +28.8] | +0.01383 [+0.006757, +0.02233] | gain |
| h=5 | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +19.3% [+5.7, +31.9] | +0.01268 [+0.003476, +0.02486] | gain |
| h=5 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | +8.9% [+3.0, +14.8] | +0.005214 [+0.001404, +0.01052] | gain |
| h=5 | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +18.9% [+8.5, +27.8] | +0.01265 [+0.00509, +0.02165] | gain |
| h=5 | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +17.5% [+4.0, +30.2] | +0.0115 [+0.002233, +0.02345] | gain |
| h=5 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | +6.9% [+0.9, +13.1] | +0.004037 [+0.0003813, +0.009351] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +20.0% [+9.3, +29.1] | +0.0134 [+0.005839, +0.02236] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +18.6% [+5.4, +31.1] | +0.01225 [+0.003155, +0.02391] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | +8.2% [+2.7, +13.8] | +0.004783 [+0.001378, +0.00976] | gain |
| h=5 | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +19.7% [+8.6, +29.0] | +0.01315 [+0.005568, +0.02206] | gain |
| h=5 | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +18.3% [+5.3, +30.4] | +0.01201 [+0.003194, +0.02315] | gain |
| h=5 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | +7.8% [+2.8, +12.8] | +0.00454 [+0.001474, +0.008876] | gain |
| h=5 | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +17.9% [+6.8, +27.3] | +0.01195 [+0.00451, +0.02045] | gain |
| h=5 | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +16.4% [+2.5, +29.5] | +0.0108 [+0.001644, +0.02217] | gain |
| h=5 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +5.7% [-0.2, +11.8] | +0.003336 [+0.0001644, +0.007875] | gain (was undecided) |
| h=5 | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +18.0% [+7.3, +26.8] | +0.01204 [+0.004736, +0.02057] | gain |
| h=5 | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | +16.6% [+2.5, +29.5] | +0.01089 [+0.001825, +0.02262] | gain |
| h=5 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | +5.9% [-1.5, +13.2] | +0.003422 [-0.0007018, +0.008991] | undecided |
| h=5 | spread_mr_level10 against B1 | 1855 | +12.9% [+1.4, +23.1] | +0.008614 [+0.001401, +0.01657] | gain |
| h=5 | spread_mr_level10 against B2 | 1855 | +11.4% [-3.5, +24.6] | +0.007466 [-0.001758, +0.01785] | undecided |

### grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=5 | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +25.8% [+19.2, +42.5] | +0.6355 [+0.3739, +1.594] | gain |
| h=5 | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +28.2% [+18.3, +37.8] | +0.7187 [+0.4557, +1.037] | gain |
| h=5 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | +2.9% [-0.1, +5.2] | +0.05505 [+0.002868, +0.1027] | gain (was undecided) |
| h=5 | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +25.8% [+18.5, +44.4] | +0.6351 [+0.3554, +1.632] | gain |
| h=5 | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +28.2% [+19.0, +37.4] | +0.7183 [+0.4611, +1.037] | gain |
| h=5 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | +2.9% [+0.4, +5.4] | +0.05469 [+0.0088, +0.1124] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +26.9% [+19.8, +44.6] | +0.6623 [+0.3847, +1.675] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +29.3% [+19.9, +38.4] | +0.7456 [+0.4907, +1.06] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | +4.3% [+2.3, +6.3] | +0.08191 [+0.04277, +0.1324] | gain |
| h=5 | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +26.4% [+19.2, +44.3] | +0.6502 [+0.3731, +1.673] | gain |
| h=5 | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +28.8% [+19.4, +37.9] | +0.7335 [+0.4782, +1.045] | gain |
| h=5 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | +3.7% [+2.1, +5.3] | +0.06983 [+0.03849, +0.1136] | gain |
| h=5 | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +25.7% [+18.4, +43.0] | +0.6329 [+0.3613, +1.615] | gain |
| h=5 | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +28.1% [+18.3, +37.6] | +0.7161 [+0.4586, +1.031] | gain |
| h=5 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +2.8% [+0.7, +5.0] | +0.05244 [+0.01309, +0.09627] | gain |
| h=5 | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +17.9% [+9.4, +28.7] | +0.4415 [+0.2101, +0.9351] | gain |
| h=5 | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | +20.6% [+0.8, +33.5] | +0.5247 [+0.08041, +0.8783] | gain |
| h=5 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | -7.4% [-41.4, +2.1] | -0.1389 [-0.8098, +0.04889] | undecided |
| h=5 | spread_mr_level10 against B1 | 1855 | +23.5% [+16.1, +41.8] | +0.5804 [+0.3141, +1.554] | gain |
| h=5 | spread_mr_level10 against B2 | 1855 | +26.0% [+16.4, +35.0] | +0.6636 [+0.4179, +0.9568] | gain |

### upper_tail_twcrps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=5 | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +33.6% [+23.6, +57.9] | +0.4782 [+0.2163, +1.698] | gain |
| h=5 | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +17.8% [+6.9, +29.4] | +0.204 [+0.08335, +0.36] | gain |
| h=5 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | +0.1% [-5.3, +4.1] | +0.0009262 [-0.04137, +0.04208] | undecided |
| h=5 | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +34.6% [+24.0, +59.6] | +0.4917 [+0.2136, +1.717] | gain |
| h=5 | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +18.9% [+9.0, +30.2] | +0.2175 [+0.0979, +0.3796] | gain |
| h=5 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | +1.5% [-2.8, +5.8] | +0.01446 [-0.02152, +0.07145] | undecided |
| h=5 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +35.8% [+25.5, +59.2] | +0.5088 [+0.232, +1.733] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +20.4% [+10.2, +31.9] | +0.2346 [+0.1172, +0.394] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | +3.3% [-0.0, +6.7] | +0.03151 [-0.0003263, +0.08459] | undecided |
| h=5 | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +35.9% [+25.6, +58.8] | +0.5109 [+0.2354, +1.731] | gain |
| h=5 | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +20.6% [+10.3, +32.0] | +0.2367 [+0.1213, +0.3937] | gain |
| h=5 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | +3.6% [+0.7, +6.4] | +0.03363 [+0.005168, +0.08352] | gain |
| h=5 | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +35.4% [+24.7, +56.8] | +0.5029 [+0.2363, +1.645] | gain |
| h=5 | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +19.9% [+7.9, +32.6] | +0.2287 [+0.112, +0.3894] | gain |
| h=5 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +2.7% [+0.3, +5.9] | +0.02562 [+0.001517, +0.06081] | gain |
| h=5 | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +23.5% [+10.9, +41.6] | +0.3341 [+0.1164, +1.01] | gain |
| h=5 | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | +5.2% [-25.3, +22.4] | +0.05988 [-0.2496, +0.2628] | undecided |
| h=5 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | -15.2% [-64.5, -1.2] | -0.1432 [-0.666, +0.001506] | undecided (was loss) |
| h=5 | spread_mr_level10 against B1 | 1855 | +33.6% [+22.5, +55.8] | +0.4772 [+0.2161, +1.615] | gain |
| h=5 | spread_mr_level10 against B2 | 1855 | +17.7% [+6.6, +29.4] | +0.2031 [+0.09894, +0.3463] | gain |

### brier_0, by all decision days

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| all decision days | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +15.6% [+8.7, +21.9] | +0.0106 [+0.005514, +0.0165] | gain |
| all decision days | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +49.8% [+35.0, +62.9] | +0.05693 [+0.03112, +0.0906] | gain |
| all decision days | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | +0.1% [-5.5, +6.1] | +4.497e-05 [-0.003093, +0.003584] | undecided |
| all decision days | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +13.0% [+5.6, +20.0] | +0.008845 [+0.003551, +0.015] | gain |
| all decision days | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +48.2% [+33.4, +61.6] | +0.05518 [+0.02965, +0.08863] | gain |
| all decision days | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | -3.0% [-9.1, +3.9] | -0.00171 [-0.005061, +0.002385] | undecided |
| all decision days | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +15.1% [+8.2, +21.6] | +0.01027 [+0.005226, +0.0162] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +49.5% [+35.0, +62.5] | +0.0566 [+0.03113, +0.08983] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | -0.5% [-5.5, +5.5] | -0.0002894 [-0.003095, +0.003232] | undecided |
| all decision days | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +15.4% [+8.7, +21.7] | +0.0105 [+0.005693, +0.01623] | gain |
| all decision days | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +49.7% [+35.3, +62.9] | +0.05683 [+0.03136, +0.09021] | gain |
| all decision days | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | -0.1% [-4.1, +4.0] | -5.543e-05 [-0.002327, +0.00233] | undecided |
| all decision days | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +16.5% [+9.3, +23.3] | +0.01125 [+0.006048, +0.01729] | gain |
| all decision days | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +50.3% [+36.2, +63.2] | +0.05758 [+0.03217, +0.09083] | gain |
| all decision days | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +1.2% [-3.5, +7.2] | +0.0006907 [-0.001995, +0.004145] | undecided |
| all decision days | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +16.2% [+7.4, +23.5] | +0.011 [+0.005042, +0.0174] | gain |
| all decision days | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | +50.1% [+35.7, +63.2] | +0.05733 [+0.03179, +0.09064] | gain |
| all decision days | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | +0.8% [-8.3, +9.3] | +0.000441 [-0.004655, +0.005541] | undecided |
| all decision days | spread_mr_level10 against B1 | 1855 | +15.5% [+9.0, +21.9] | +0.01056 [+0.005649, +0.01633] | gain |
| all decision days | spread_mr_level10 against B2 | 1855 | +49.7% [+35.3, +63.2] | +0.05689 [+0.03128, +0.09067] | gain |

### brier_10, by all decision days

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| all decision days | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +33.1% [+27.2, +38.4] | +0.01411 [+0.008786, +0.02138] | gain |
| all decision days | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +6.6% [-6.0, +17.4] | +0.002013 [-0.001406, +0.006073] | undecided |
| all decision days | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | +2.2% [-3.9, +7.5] | +0.0006493 [-0.0009352, +0.002549] | undecided |
| all decision days | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +33.2% [+25.1, +39.6] | +0.01416 [+0.008394, +0.02194] | gain |
| all decision days | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +6.8% [-5.0, +16.9] | +0.002067 [-0.001183, +0.005892] | undecided |
| all decision days | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | +2.4% [-2.8, +7.5] | +0.000703 [-0.0007113, +0.002599] | undecided |
| all decision days | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +34.0% [+26.0, +40.4] | +0.01449 [+0.008757, +0.02218] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +7.8% [-3.6, +17.6] | +0.002399 [-0.0007883, +0.006079] | undecided |
| all decision days | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | +3.5% [-1.0, +7.9] | +0.001035 [-0.0002412, +0.002721] | undecided |
| all decision days | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +34.0% [+25.9, +40.6] | +0.0145 [+0.008821, +0.02212] | gain |
| all decision days | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +7.9% [-3.4, +17.3] | +0.00241 [-0.000701, +0.005965] | undecided |
| all decision days | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | +3.6% [-0.5, +7.3] | +0.001047 [-0.0001005, +0.002517] | undecided |
| all decision days | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +32.9% [+24.8, +39.7] | +0.01404 [+0.008396, +0.02166] | gain |
| all decision days | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +6.4% [-5.3, +16.4] | +0.001947 [-0.001264, +0.005672] | undecided |
| all decision days | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +2.0% [-2.5, +6.7] | +0.0005829 [-0.0006277, +0.002251] | undecided |
| all decision days | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +27.2% [+19.2, +33.7] | +0.01159 [+0.006628, +0.01835] | gain |
| all decision days | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | -1.6% [-17.0, +10.9] | -0.0005028 [-0.004542, +0.003652] | undecided |
| all decision days | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | -6.4% [-16.1, +1.1] | -0.001866 [-0.00433, +0.0002588] | undecided |
| all decision days | spread_mr_level10 against B1 | 1855 | +31.5% [+23.3, +39.0] | +0.01346 [+0.008184, +0.02058] | gain |
| all decision days | spread_mr_level10 against B2 | 1855 | +4.5% [-5.5, +13.1] | +0.001364 [-0.001386, +0.004313] | undecided |

### brier_5, by all decision days

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| all decision days | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +19.9% [+12.1, +26.2] | +0.01264 [+0.00685, +0.01955] | gain |
| all decision days | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +21.6% [+8.5, +34.1] | +0.014 [+0.004838, +0.0266] | gain |
| all decision days | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | +7.4% [+2.3, +13.2] | +0.004073 [+0.001046, +0.008759] | gain |
| all decision days | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +18.4% [+8.8, +26.0] | +0.01171 [+0.005185, +0.01919] | gain |
| all decision days | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +20.1% [+7.3, +32.5] | +0.01307 [+0.004258, +0.02546] | gain |
| all decision days | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | +5.7% [+0.5, +11.6] | +0.003142 [+0.0001912, +0.007617] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +19.4% [+9.8, +27.0] | +0.01232 [+0.00589, +0.01972] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +21.1% [+8.5, +33.2] | +0.01369 [+0.005027, +0.02576] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | +6.8% [+1.9, +12.2] | +0.00376 [+0.001023, +0.007992] | gain |
| all decision days | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +19.2% [+9.4, +26.8] | +0.01218 [+0.005828, +0.01941] | gain |
| all decision days | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +20.9% [+8.6, +32.8] | +0.01354 [+0.00497, +0.02526] | gain |
| all decision days | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | +6.6% [+2.1, +11.4] | +0.003614 [+0.0011, +0.007429] | gain |
| all decision days | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +17.1% [+7.6, +24.9] | +0.01086 [+0.004739, +0.01773] | gain |
| all decision days | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +18.8% [+5.5, +31.8] | +0.01222 [+0.003427, +0.02422] | gain |
| all decision days | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +4.2% [-0.8, +9.6] | +0.002295 [-0.0002107, +0.005944] | undecided |
| all decision days | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +19.1% [+10.5, +25.6] | +0.01212 [+0.006097, +0.01903] | gain |
| all decision days | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | +20.8% [+7.9, +33.5] | +0.01349 [+0.004736, +0.02606] | gain |
| all decision days | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | +6.5% [+0.5, +13.1] | +0.003559 [+0.0002662, +0.008519] | gain |
| all decision days | spread_mr_level10 against B1 | 1855 | +13.5% [+3.7, +21.6] | +0.008563 [+0.002751, +0.01498] | gain |
| all decision days | spread_mr_level10 against B2 | 1855 | +15.3% [+1.4, +28.0] | +0.009928 [+0.001236, +0.02091] | gain |

### grid_crps, by all decision days

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| all decision days | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +24.9% [+19.1, +40.0] | +0.5707 [+0.3309, +1.506] | gain |
| all decision days | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +31.8% [+20.7, +41.9] | +0.8002 [+0.5396, +1.128] | gain |
| all decision days | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | +3.4% [+0.8, +5.5] | +0.06022 [+0.01882, +0.1023] | gain |
| all decision days | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +24.7% [+18.1, +41.8] | +0.5663 [+0.3111, +1.538] | gain |
| all decision days | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +31.6% [+21.1, +41.4] | +0.7959 [+0.541, +1.123] | gain |
| all decision days | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | +3.1% [+0.9, +5.3] | +0.05586 [+0.01576, +0.1056] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +25.8% [+19.5, +42.0] | +0.5912 [+0.3377, +1.572] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +32.6% [+21.9, +42.3] | +0.8207 [+0.5669, +1.145] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | +4.5% [+2.8, +6.3] | +0.08068 [+0.04675, +0.1241] | gain |
| all decision days | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +25.3% [+18.9, +41.8] | +0.5788 [+0.3269, +1.566] | gain |
| all decision days | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +32.1% [+21.4, +41.7] | +0.8083 [+0.5551, +1.128] | gain |
| all decision days | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | +3.8% [+2.4, +5.2] | +0.06828 [+0.04069, +0.1045] | gain |
| all decision days | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +24.6% [+18.2, +40.6] | +0.5636 [+0.3175, +1.514] | gain |
| all decision days | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +31.5% [+20.6, +41.3] | +0.7931 [+0.5405, +1.116] | gain |
| all decision days | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +3.0% [+1.1, +4.9] | +0.05314 [+0.01968, +0.09105] | gain |
| all decision days | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +17.6% [+9.3, +27.9] | +0.4029 [+0.1919, +0.9018] | gain |
| all decision days | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | +25.1% [+4.5, +38.3] | +0.6324 [+0.2197, +0.9779] | gain |
| all decision days | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | -6.1% [-36.0, +2.4] | -0.1076 [-0.6812, +0.04965] | undecided |
| all decision days | spread_mr_level10 against B1 | 1855 | +22.3% [+15.7, +39.4] | +0.5105 [+0.2727, +1.445] | gain |
| all decision days | spread_mr_level10 against B2 | 1855 | +29.4% [+18.5, +38.9] | +0.74 [+0.4952, +1.044] | gain |

### upper_tail_twcrps, by all decision days

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| all decision days | spread_mr_fhs_mad10_f0.5 against B1 | 1855 | +33.2% [+25.7, +50.6] | +0.4562 [+0.2164, +1.555] | gain |
| all decision days | spread_mr_fhs_mad10_f0.5 against B2 | 1855 | +18.8% [+5.2, +32.7] | +0.2126 [+0.08872, +0.3748] | gain |
| all decision days | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1855 | +1.2% [-2.6, +4.2] | +0.01094 [-0.01975, +0.04521] | undecided |
| all decision days | spread_mr_fhs_mad20_f0.25 against B1 | 1855 | +33.8% [+25.7, +52.2] | +0.4649 [+0.2112, +1.576] | gain |
| all decision days | spread_mr_fhs_mad20_f0.25 against B2 | 1855 | +19.6% [+6.8, +32.9] | +0.2213 [+0.09971, +0.3867] | gain |
| all decision days | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1855 | +2.1% [-1.4, +5.5] | +0.01963 [-0.01149, +0.06824] | undecided |
| all decision days | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +34.8% [+27.0, +51.8] | +0.4789 [+0.2256, +1.592] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +20.8% [+7.4, +34.2] | +0.2354 [+0.1155, +0.3996] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1855 | +3.6% [+1.0, +6.3] | +0.03367 [+0.006041, +0.07955] | gain |
| all decision days | spread_mr_fhs_mad20_f1.0 against B1 | 1855 | +34.8% [+27.1, +51.5] | +0.4792 [+0.2268, +1.587] | gain |
| all decision days | spread_mr_fhs_mad20_f1.0 against B2 | 1855 | +20.8% [+7.3, +34.2] | +0.2356 [+0.1168, +0.3966] | gain |
| all decision days | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1855 | +3.6% [+1.3, +6.0] | +0.03389 [+0.00894, +0.07579] | gain |
| all decision days | spread_mr_fhs_mad40_f0.5 against B1 | 1855 | +34.1% [+26.3, +49.9] | +0.4693 [+0.2236, +1.512] | gain |
| all decision days | spread_mr_fhs_mad40_f0.5 against B2 | 1855 | +20.0% [+5.7, +34.2] | +0.2257 [+0.1052, +0.3934] | gain |
| all decision days | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1855 | +2.6% [+0.4, +5.1] | +0.02403 [+0.001694, +0.05625] | gain |
| all decision days | spread_mr_fhs_sd20_f0.5 against B1 | 1855 | +24.4% [+13.2, +39.2] | +0.3353 [+0.1315, +1.017] | gain |
| all decision days | spread_mr_fhs_sd20_f0.5 against B2 | 1855 | +8.1% [-22.3, +25.9] | +0.09171 [-0.1883, +0.2866] | undecided |
| all decision days | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1855 | -11.8% [-51.6, -0.5] | -0.11 [-0.539, +0.006388] | undecided (was loss) |
| all decision days | spread_mr_level10 against B1 | 1855 | +32.4% [+24.5, +48.7] | +0.4453 [+0.2085, +1.481] | gain |
| all decision days | spread_mr_level10 against B2 | 1855 | +17.8% [+3.2, +31.4] | +0.2017 [+0.08814, +0.3521] | gain |

### brier_0, by pressure-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| month_end | spread_mr_fhs_mad10_f0.5 against B1 | 150 | -3.2% [-43.2, +17.9] | -0.001684 [-0.01832, +0.009602] | undecided |
| month_end | spread_mr_fhs_mad10_f0.5 against B2 | 150 | +54.6% [+30.5, +79.1] | +0.06498 [+0.01191, +0.211] | gain |
| month_end | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 150 | -2.2% [-10.8, +4.4] | -0.001164 [-0.005704, +0.002501] | undecided |
| month_end | spread_mr_fhs_mad20_f0.25 against B1 | 150 | -5.4% [-47.4, +18.8] | -0.002826 [-0.01983, +0.009775] | undecided |
| month_end | spread_mr_fhs_mad20_f0.25 against B2 | 150 | +53.6% [+29.9, +76.8] | +0.06383 [+0.0107, +0.2065] | gain |
| month_end | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 150 | -4.4% [-12.5, +2.8] | -0.002306 [-0.006484, +0.00173] | undecided |
| month_end | spread_mr_fhs_mad20_f0.5 against B1 | 150 | -2.2% [-38.5, +19.6] | -0.001145 [-0.01649, +0.01088] | undecided |
| month_end | spread_mr_fhs_mad20_f0.5 against B2 | 150 | +55.0% [+31.0, +78.7] | +0.06551 [+0.01214, +0.2107] | gain |
| month_end | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 150 | -1.2% [-9.6, +5.4] | -0.0006248 [-0.00466, +0.003033] | undecided |
| month_end | spread_mr_fhs_mad20_f1.0 against B1 | 150 | -0.8% [-33.3, +20.1] | -0.0004203 [-0.01469, +0.0114] | undecided |
| month_end | spread_mr_fhs_mad20_f1.0 against B2 | 150 | +55.6% [+31.3, +79.7] | +0.06624 [+0.01246, +0.2138] | gain |
| month_end | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 150 | +0.2% [-10.2, +7.1] | +9.948e-05 [-0.004312, +0.003788] | undecided |
| month_end | spread_mr_fhs_mad40_f0.5 against B1 | 150 | -0.5% [-34.8, +22.3] | -0.0002558 [-0.01483, +0.01305] | undecided |
| month_end | spread_mr_fhs_mad40_f0.5 against B2 | 150 | +55.8% [+31.8, +78.4] | +0.0664 [+0.01192, +0.2106] | gain |
| month_end | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 150 | +0.5% [-7.9, +6.8] | +0.000264 [-0.003474, +0.003973] | undecided |
| month_end | spread_mr_fhs_sd20_f0.5 against B1 | 150 | +2.4% [-29.1, +18.7] | +0.001253 [-0.01184, +0.01101] | undecided |
| month_end | spread_mr_fhs_sd20_f0.5 against B2 | 150 | +57.1% [+34.1, +82.0] | +0.06791 [+0.01424, +0.2217] | gain |
| month_end | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 150 | +3.4% [-7.7, +16.3] | +0.001772 [-0.003722, +0.01006] | undecided |
| month_end | spread_mr_level10 against B1 | 150 | -1.0% [-42.1, +24.4] | -0.0005197 [-0.01923, +0.01404] | undecided |
| month_end | spread_mr_level10 against B2 | 150 | +55.6% [+30.5, +79.7] | +0.06614 [+0.0107, +0.2126] | gain |

### grid_crps, by pressure-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| month_end | spread_mr_fhs_mad10_f0.5 against B1 | 150 | +11.8% [+5.2, +19.7] | +0.2654 [+0.1001, +0.6091] | gain |
| month_end | spread_mr_fhs_mad10_f0.5 against B2 | 150 | +32.3% [+12.4, +50.8] | +0.9451 [+0.4061, +1.988] | gain |
| month_end | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 150 | +5.5% [-4.3, +16.2] | +0.1161 [-0.01979, +0.3572] | undecided |
| month_end | spread_mr_fhs_mad20_f0.25 against B1 | 150 | +13.6% [+7.4, +20.5] | +0.3054 [+0.104, +0.6644] | gain |
| month_end | spread_mr_fhs_mad20_f0.25 against B2 | 150 | +33.6% [+15.3, +51.2] | +0.9851 [+0.4363, +2.043] | gain |
| month_end | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 150 | +7.4% [-0.2, +17.0] | +0.156 [+0.02926, +0.4316] | gain (was undecided) |
| month_end | spread_mr_fhs_mad20_f0.5 against B1 | 150 | +13.8% [+8.0, +20.1] | +0.3099 [+0.1169, +0.6493] | gain |
| month_end | spread_mr_fhs_mad20_f0.5 against B2 | 150 | +33.8% [+15.4, +51.0] | +0.9896 [+0.4463, +2.035] | gain |
| month_end | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 150 | +7.6% [-0.3, +16.1] | +0.1605 [+0.04211, +0.4189] | gain (was undecided) |
| month_end | spread_mr_fhs_mad20_f1.0 against B1 | 150 | +12.4% [+7.7, +17.5] | +0.2786 [+0.1036, +0.5748] | gain |
| month_end | spread_mr_fhs_mad20_f1.0 against B2 | 150 | +32.7% [+14.0, +49.7] | +0.9583 [+0.4117, +1.968] | gain |
| month_end | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 150 | +6.2% [+0.0, +13.1] | +0.1292 [+0.03671, +0.3532] | gain |
| month_end | spread_mr_fhs_mad40_f0.5 against B1 | 150 | +13.0% [+7.6, +18.8] | +0.2924 [+0.09402, +0.6136] | gain |
| month_end | spread_mr_fhs_mad40_f0.5 against B2 | 150 | +33.2% [+16.1, +49.7] | +0.9721 [+0.4382, +1.971] | gain |
| month_end | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 150 | +6.8% [+1.0, +14.7] | +0.1431 [+0.0328, +0.3882] | gain |
| month_end | spread_mr_fhs_sd20_f0.5 against B1 | 150 | +12.9% [+1.4, +19.2] | +0.291 [+0.0706, +0.5886] | gain |
| month_end | spread_mr_fhs_sd20_f0.5 against B2 | 150 | +33.1% [+13.2, +49.0] | +0.9707 [+0.4227, +1.898] | gain |
| month_end | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 150 | +6.7% [-14.7, +13.9] | +0.1417 [-0.1343, +0.3166] | undecided |
| month_end | spread_mr_level10 against B1 | 150 | +6.6% [+2.5, +10.8] | +0.1494 [+0.01876, +0.3356] | gain |
| month_end | spread_mr_level10 against B2 | 150 | +28.3% [+11.3, +42.8] | +0.8291 [+0.3212, +1.615] | gain |

### upper_tail_twcrps, by pressure-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| month_end | spread_mr_fhs_mad10_f0.5 against B1 | 150 | +9.7% [-3.1, +24.6] | +0.1125 [+0.01396, +0.5355] | gain (was undecided) |
| month_end | spread_mr_fhs_mad10_f0.5 against B2 | 150 | +30.9% [-20.3, +73.2] | +0.4705 [+0.09726, +2.147] | gain (was undecided) |
| month_end | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 150 | +4.7% [-20.9, +47.0] | +0.05153 [-0.04969, +0.3659] | undecided |
| month_end | spread_mr_fhs_mad20_f0.25 against B1 | 150 | +12.2% [+2.6, +22.7] | +0.1426 [+0.01489, +0.6364] | gain |
| month_end | spread_mr_fhs_mad20_f0.25 against B2 | 150 | +32.9% [-5.4, +71.0] | +0.5006 [+0.1048, +2.053] | gain (was undecided) |
| month_end | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 150 | +7.4% [-7.8, +32.0] | +0.08168 [-0.008602, +0.5358] | undecided |
| month_end | spread_mr_fhs_mad20_f0.5 against B1 | 150 | +12.7% [+1.8, +22.0] | +0.1475 [+0.02543, +0.5777] | gain |
| month_end | spread_mr_fhs_mad20_f0.5 against B2 | 150 | +33.2% [-8.9, +71.0] | +0.5055 [+0.1148, +2.045] | gain (was undecided) |
| month_end | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 150 | +7.8% [-12.4, +29.8] | +0.08654 [+0.0009638, +0.4906] | gain (was undecided) |
| month_end | spread_mr_fhs_mad20_f1.0 against B1 | 150 | +12.1% [+2.5, +20.1] | +0.141 [+0.02598, +0.5226] | gain |
| month_end | spread_mr_fhs_mad20_f1.0 against B2 | 150 | +32.8% [-8.3, +69.0] | +0.499 [+0.117, +1.985] | gain (was undecided) |
| month_end | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 150 | +7.3% [-14.4, +24.4] | +0.08005 [+0.003573, +0.4079] | gain (was undecided) |
| month_end | spread_mr_fhs_mad40_f0.5 against B1 | 150 | +13.3% [+5.6, +21.5] | +0.1554 [+0.02628, +0.5659] | gain |
| month_end | spread_mr_fhs_mad40_f0.5 against B2 | 150 | +33.7% [-3.2, +69.7] | +0.5134 [+0.1183, +1.953] | gain (was undecided) |
| month_end | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 150 | +8.6% [-6.6, +28.8] | +0.09445 [+0.01414, +0.523] | gain (was undecided) |
| month_end | spread_mr_fhs_sd20_f0.5 against B1 | 150 | +12.1% [-6.7, +20.6] | +0.1411 [+0.001689, +0.5146] | gain (was undecided) |
| month_end | spread_mr_fhs_sd20_f0.5 against B2 | 150 | +32.8% [-16.0, +55.5] | +0.4991 [+0.09178, +1.576] | gain (was undecided) |
| month_end | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 150 | +7.3% [-31.2, +19.3] | +0.0801 [-0.08576, +0.2814] | undecided |
| month_end | spread_mr_level10 against B1 | 150 | +5.2% [-1.1, +12.2] | +0.06095 [-0.02193, +0.2515] | undecided |
| month_end | spread_mr_level10 against B2 | 150 | +27.5% [+5.9, +52.8] | +0.419 [+0.09644, +1.434] | gain |

### brier_0, by pressure-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| ordinary | spread_mr_fhs_mad10_f0.5 against B1 | 1590 | +17.0% [+9.5, +24.3] | +0.01154 [+0.006057, +0.01816] | gain |
| ordinary | spread_mr_fhs_mad10_f0.5 against B2 | 1590 | +49.4% [+34.9, +62.8] | +0.05517 [+0.03, +0.08985] | gain |
| ordinary | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1590 | +0.4% [-6.0, +6.8] | +0.0001999 [-0.003282, +0.00403] | undecided |
| ordinary | spread_mr_fhs_mad20_f0.25 against B1 | 1590 | +13.9% [+6.1, +21.8] | +0.009486 [+0.003971, +0.01628] | gain |
| ordinary | spread_mr_fhs_mad20_f0.25 against B2 | 1590 | +47.6% [+32.9, +61.2] | +0.05311 [+0.02816, +0.08743] | gain |
| ordinary | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1590 | -3.3% [-10.2, +4.2] | -0.001853 [-0.005514, +0.002525] | undecided |
| ordinary | spread_mr_fhs_mad20_f0.5 against B1 | 1590 | +16.2% [+8.8, +23.7] | +0.01101 [+0.005644, +0.01761] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5 against B2 | 1590 | +48.9% [+34.6, +62.3] | +0.05464 [+0.0299, +0.08914] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1590 | -0.6% [-6.0, +5.5] | -0.0003257 [-0.003328, +0.003251] | undecided |
| ordinary | spread_mr_fhs_mad20_f1.0 against B1 | 1590 | +16.5% [+9.3, +23.8] | +0.01125 [+0.006076, +0.01763] | gain |
| ordinary | spread_mr_fhs_mad20_f1.0 against B2 | 1590 | +49.1% [+34.9, +62.7] | +0.05488 [+0.03025, +0.0895] | gain |
| ordinary | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1590 | -0.2% [-4.4, +4.1] | -8.613e-05 [-0.002469, +0.002339] | undecided |
| ordinary | spread_mr_fhs_mad40_f0.5 against B1 | 1590 | +17.3% [+9.6, +25.1] | +0.01179 [+0.006374, +0.01862] | gain |
| ordinary | spread_mr_fhs_mad40_f0.5 against B2 | 1590 | +49.6% [+35.4, +63.0] | +0.05542 [+0.03064, +0.08988] | gain |
| ordinary | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1590 | +0.8% [-4.3, +6.9] | +0.0004531 [-0.002389, +0.003967] | undecided |
| ordinary | spread_mr_fhs_sd20_f0.5 against B1 | 1590 | +16.6% [+7.8, +24.8] | +0.01132 [+0.005256, +0.01821] | gain |
| ordinary | spread_mr_fhs_sd20_f0.5 against B2 | 1590 | +49.2% [+34.6, +62.8] | +0.05495 [+0.02993, +0.08955] | gain |
| ordinary | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1590 | -0.0% [-9.6, +8.8] | -2.12e-05 [-0.005295, +0.005183] | undecided |
| ordinary | spread_mr_level10 against B1 | 1590 | +16.7% [+9.6, +24.1] | +0.01134 [+0.006185, +0.01781] | gain |
| ordinary | spread_mr_level10 against B2 | 1590 | +49.2% [+34.7, +63.1] | +0.05497 [+0.02989, +0.08989] | gain |

### brier_10, by pressure-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| ordinary | spread_mr_fhs_mad10_f0.5 against B1 | 1590 | +37.9% [+30.4, +44.6] | +0.01512 [+0.009182, +0.0236] | gain |
| ordinary | spread_mr_fhs_mad10_f0.5 against B2 | 1590 | -3.9% [-20.5, +9.3] | -0.00092 [-0.004011, +0.002452] | undecided |
| ordinary | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1590 | -1.8% [-11.0, +5.1] | -0.0004367 [-0.002229, +0.001312] | undecided |
| ordinary | spread_mr_fhs_mad20_f0.25 against B1 | 1590 | +37.7% [+27.6, +45.5] | +0.01502 [+0.008661, +0.02393] | gain |
| ordinary | spread_mr_fhs_mad20_f0.25 against B2 | 1590 | -4.3% [-19.2, +6.9] | -0.001013 [-0.003802, +0.00182] | undecided |
| ordinary | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1590 | -2.2% [-8.6, +3.3] | -0.0005297 [-0.00183, +0.0008797] | undecided |
| ordinary | spread_mr_fhs_mad20_f0.5 against B1 | 1590 | +38.7% [+28.7, +46.5] | +0.01544 [+0.009167, +0.02418] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5 against B2 | 1590 | -2.5% [-16.9, +7.9] | -0.0006015 [-0.003355, +0.002158] | undecided |
| ordinary | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1590 | -0.5% [-6.0, +4.1] | -0.0001182 [-0.001271, +0.001101] | undecided |
| ordinary | spread_mr_fhs_mad20_f1.0 against B1 | 1590 | +39.0% [+28.9, +47.0] | +0.01553 [+0.009276, +0.02424] | gain |
| ordinary | spread_mr_fhs_mad20_f1.0 against B2 | 1590 | -2.1% [-16.0, +8.0] | -0.0005033 [-0.003182, +0.00217] | undecided |
| ordinary | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1590 | -0.1% [-4.9, +3.9] | -2.001e-05 [-0.001046, +0.001027] | undecided |
| ordinary | spread_mr_fhs_mad40_f0.5 against B1 | 1590 | +38.5% [+28.3, +46.4] | +0.01533 [+0.008944, +0.02414] | gain |
| ordinary | spread_mr_fhs_mad40_f0.5 against B2 | 1590 | -3.0% [-17.3, +7.5] | -0.0007038 [-0.003459, +0.002049] | undecided |
| ordinary | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1590 | -0.9% [-7.0, +4.2] | -0.0002205 [-0.001485, +0.001145] | undecided |
| ordinary | spread_mr_fhs_sd20_f0.5 against B1 | 1590 | +30.3% [+20.9, +37.7] | +0.01208 [+0.006546, +0.01966] | gain |
| ordinary | spread_mr_fhs_sd20_f0.5 against B2 | 1590 | -16.6% [-39.4, -0.4] | -0.003959 [-0.008098, -0.0002449] | loss |
| ordinary | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1590 | -14.3% [-30.5, -3.4] | -0.003476 [-0.006844, -0.0009396] | loss |
| ordinary | spread_mr_level10 against B1 | 1590 | +39.0% [+28.7, +48.2] | +0.01555 [+0.009203, +0.02443] | gain |
| ordinary | spread_mr_level10 against B2 | 1590 | -2.0% [-13.8, +6.7] | -0.0004833 [-0.002837, +0.001696] | undecided |

### brier_5, by pressure-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| ordinary | spread_mr_fhs_mad10_f0.5 against B1 | 1590 | +21.5% [+12.2, +29.0] | +0.01307 [+0.006819, +0.02049] | gain |
| ordinary | spread_mr_fhs_mad10_f0.5 against B2 | 1590 | +16.2% [+0.4, +29.4] | +0.009221 [+0.0004517, +0.02072] | gain |
| ordinary | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1590 | +6.8% [+0.1, +13.8] | +0.003453 [+3.08e-05, +0.00851] | gain |
| ordinary | spread_mr_fhs_mad20_f0.25 against B1 | 1590 | +19.4% [+8.3, +28.1] | +0.01176 [+0.004894, +0.01989] | gain |
| ordinary | spread_mr_fhs_mad20_f0.25 against B2 | 1590 | +13.9% [-0.9, +26.8] | +0.00791 [-0.0003129, +0.01886] | undecided |
| ordinary | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1590 | +4.2% [-2.5, +12.0] | +0.002141 [-0.001035, +0.007362] | undecided |
| ordinary | spread_mr_fhs_mad20_f0.5 against B1 | 1590 | +20.7% [+9.4, +29.6] | +0.01255 [+0.005706, +0.02061] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5 against B2 | 1590 | +15.3% [+0.8, +27.8] | +0.008696 [+0.0005936, +0.01929] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1590 | +5.7% [-0.3, +12.8] | +0.002928 [+2.204e-06, +0.007827] | gain (was undecided) |
| ordinary | spread_mr_fhs_mad20_f1.0 against B1 | 1590 | +20.7% [+9.4, +29.8] | +0.01254 [+0.005725, +0.0204] | gain |
| ordinary | spread_mr_fhs_mad20_f1.0 against B2 | 1590 | +15.3% [+1.1, +27.5] | +0.008689 [+0.000646, +0.01897] | gain |
| ordinary | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1590 | +5.7% [+0.3, +11.9] | +0.002921 [+0.0002665, +0.007279] | gain |
| ordinary | spread_mr_fhs_mad40_f0.5 against B1 | 1590 | +18.9% [+7.7, +28.5] | +0.01148 [+0.004706, +0.01926] | gain |
| ordinary | spread_mr_fhs_mad40_f0.5 against B2 | 1590 | +13.4% [-1.9, +26.8] | +0.007629 [-0.0006766, +0.01818] | undecided |
| ordinary | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1590 | +3.6% [-2.4, +10.4] | +0.001861 [-0.0009202, +0.00594] | undecided |
| ordinary | spread_mr_fhs_sd20_f0.5 against B1 | 1590 | +20.6% [+10.9, +28.6] | +0.01252 [+0.006113, +0.02014] | gain |
| ordinary | spread_mr_fhs_sd20_f0.5 against B2 | 1590 | +15.2% [-0.3, +28.8] | +0.008666 [+5.432e-05, +0.02001] | gain (was undecided) |
| ordinary | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1590 | +5.7% [-2.2, +13.8] | +0.002898 [-0.0008397, +0.008427] | undecided |
| ordinary | spread_mr_level10 against B1 | 1590 | +15.8% [+3.8, +26.8] | +0.00962 [+0.00285, +0.01744] | gain |
| ordinary | spread_mr_level10 against B2 | 1590 | +10.1% [-6.7, +23.8] | +0.005769 [-0.002805, +0.01547] | undecided |

### grid_crps, by pressure-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| ordinary | spread_mr_fhs_mad10_f0.5 against B1 | 1590 | +29.9% [+20.7, +55.2] | +0.6079 [+0.3372, +1.618] | gain |
| ordinary | spread_mr_fhs_mad10_f0.5 against B2 | 1590 | +32.3% [+22.4, +41.8] | +0.6788 [+0.4384, +0.9885] | gain |
| ordinary | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1590 | +1.9% [-2.5, +5.0] | +0.02721 [-0.03217, +0.07112] | undecided |
| ordinary | spread_mr_fhs_mad20_f0.25 against B1 | 1590 | +29.4% [+18.8, +57.7] | +0.5973 [+0.307, +1.681] | gain |
| ordinary | spread_mr_fhs_mad20_f0.25 against B2 | 1590 | +31.8% [+22.7, +41.0] | +0.6683 [+0.4369, +0.9713] | gain |
| ordinary | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1590 | +1.2% [-1.5, +3.9] | +0.01669 [-0.01948, +0.05813] | undecided |
| ordinary | spread_mr_fhs_mad20_f0.5 against B1 | 1590 | +30.9% [+20.8, +58.7] | +0.6284 [+0.3391, +1.717] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5 against B2 | 1590 | +33.3% [+24.4, +42.2] | +0.6993 [+0.471, +0.9997] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1590 | +3.3% [+1.0, +5.6] | +0.04773 [+0.01644, +0.08184] | gain |
| ordinary | spread_mr_fhs_mad20_f1.0 against B1 | 1590 | +30.6% [+20.4, +59.0] | +0.6222 [+0.3326, +1.727] | gain |
| ordinary | spread_mr_fhs_mad20_f1.0 against B2 | 1590 | +33.0% [+24.0, +41.8] | +0.6931 [+0.4643, +0.9903] | gain |
| ordinary | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1590 | +2.9% [+0.9, +4.6] | +0.04154 [+0.01615, +0.06713] | gain |
| ordinary | spread_mr_fhs_mad40_f0.5 against B1 | 1590 | +30.0% [+19.6, +58.6] | +0.6104 [+0.3201, +1.717] | gain |
| ordinary | spread_mr_fhs_mad40_f0.5 against B2 | 1590 | +32.4% [+23.3, +41.5] | +0.6813 [+0.4499, +0.9838] | gain |
| ordinary | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1590 | +2.0% [-0.3, +4.5] | +0.02972 [-0.00302, +0.06473] | undecided |
| ordinary | spread_mr_fhs_sd20_f0.5 against B1 | 1590 | +20.7% [+9.7, +34.6] | +0.4209 [+0.1846, +0.9488] | gain |
| ordinary | spread_mr_fhs_sd20_f0.5 against B2 | 1590 | +23.4% [-1.2, +36.9] | +0.4918 [+0.05135, +0.8265] | gain (was undecided) |
| ordinary | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1590 | -11.0% [-60.8, +1.6] | -0.1598 [-0.9115, +0.02502] | undecided |
| ordinary | spread_mr_level10 against B1 | 1590 | +28.6% [+17.7, +58.7] | +0.5807 [+0.2876, +1.701] | gain |
| ordinary | spread_mr_level10 against B2 | 1590 | +31.0% [+22.4, +39.5] | +0.6516 [+0.4302, +0.9371] | gain |

### upper_tail_twcrps, by pressure-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| ordinary | spread_mr_fhs_mad10_f0.5 against B1 | 1590 | +43.3% [+30.3, +74.8] | +0.4951 [+0.2206, +1.684] | gain |
| ordinary | spread_mr_fhs_mad10_f0.5 against B2 | 1590 | +15.6% [+0.8, +28.4] | +0.1193 [+0.01548, +0.2502] | gain |
| ordinary | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 1590 | -3.0% [-10.4, +1.5] | -0.01906 [-0.06613, +0.01042] | undecided |
| ordinary | spread_mr_fhs_mad20_f0.25 against B1 | 1590 | +44.0% [+29.5, +76.7] | +0.5028 [+0.2115, +1.723] | gain |
| ordinary | spread_mr_fhs_mad20_f0.25 against B2 | 1590 | +16.6% [+4.2, +28.2] | +0.127 [+0.03088, +0.258] | gain |
| ordinary | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 1590 | -1.8% [-6.2, +2.8] | -0.01139 [-0.03511, +0.01738] | undecided |
| ordinary | spread_mr_fhs_mad20_f0.5 against B1 | 1590 | +45.5% [+31.6, +75.9] | +0.5202 [+0.2296, +1.746] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5 against B2 | 1590 | +18.8% [+6.6, +30.2] | +0.1443 [+0.04962, +0.2742] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 1590 | +0.9% [-2.7, +4.7] | +0.005958 [-0.01427, +0.03127] | undecided |
| ordinary | spread_mr_fhs_mad20_f1.0 against B1 | 1590 | +45.8% [+32.0, +75.4] | +0.5238 [+0.2339, +1.749] | gain |
| ordinary | spread_mr_fhs_mad20_f1.0 against B2 | 1590 | +19.3% [+7.2, +30.5] | +0.1479 [+0.05463, +0.2761] | gain |
| ordinary | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 1590 | +1.5% [-1.8, +4.8] | +0.009598 [-0.008741, +0.03129] | undecided |
| ordinary | spread_mr_fhs_mad40_f0.5 against B1 | 1590 | +45.5% [+31.4, +74.4] | +0.5194 [+0.23, +1.701] | gain |
| ordinary | spread_mr_fhs_mad40_f0.5 against B2 | 1590 | +18.7% [+6.6, +30.4] | +0.1436 [+0.04834, +0.2756] | gain |
| ordinary | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 1590 | +0.8% [-2.5, +4.5] | +0.005254 [-0.01401, +0.02962] | undecided |
| ordinary | spread_mr_fhs_sd20_f0.5 against B1 | 1590 | +31.5% [+14.2, +52.1] | +0.3598 [+0.128, +1.073] | gain |
| ordinary | spread_mr_fhs_sd20_f0.5 against B2 | 1590 | -2.1% [-55.4, +22.3] | -0.01601 [-0.3508, +0.1709] | undecided |
| ordinary | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 1590 | -24.6% [-102.2, -2.8] | -0.1544 [-0.7413, -0.01451] | loss |
| ordinary | spread_mr_level10 against B1 | 1590 | +45.0% [+30.7, +74.6] | +0.5142 [+0.2253, +1.713] | gain |
| ordinary | spread_mr_level10 against B2 | 1590 | +18.0% [+7.2, +28.6] | +0.1384 [+0.05185, +0.2567] | gain |

### grid_crps, by pressure-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| quarter_end | spread_mr_fhs_mad10_f0.5 against B1 | 30 | +10.5% [+7.0, +16.7] | +0.7291 [+0.1375, +2.75] | gain |
| quarter_end | spread_mr_fhs_mad10_f0.5 against B2 | 30 | +17.6% [-40.6, +59.8] | +1.333 [-1.155, +4.535] | undecided |
| quarter_end | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 30 | +13.3% [+8.5, +22.3] | +0.9542 [+0.1317, +3.24] | gain |
| quarter_end | spread_mr_fhs_mad20_f0.25 against B1 | 30 | +12.3% [+8.4, +15.8] | +0.8527 [+0.1679, +2.451] | gain |
| quarter_end | spread_mr_fhs_mad20_f0.25 against B2 | 30 | +19.3% [-29.1, +54.0] | +1.457 [-0.5352, +4.101] | undecided |
| quarter_end | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 30 | +15.0% [+9.9, +20.5] | +1.078 [+0.0756, +2.668] | gain |
| quarter_end | spread_mr_fhs_mad20_f0.5 against B1 | 30 | +9.8% [+8.0, +11.5] | +0.6847 [+0.1558, +2.247] | gain |
| quarter_end | spread_mr_fhs_mad20_f0.5 against B2 | 30 | +17.0% [-33.5, +54.4] | +1.289 [-0.9958, +4.073] | undecided |
| quarter_end | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 30 | +12.7% [+9.8, +15.5] | +0.9098 [+0.08062, +2.658] | gain |
| quarter_end | spread_mr_fhs_mad20_f1.0 against B1 | 30 | +6.9% [+3.6, +10.2] | +0.4779 [+0.05656, +2.107] | gain |
| quarter_end | spread_mr_fhs_mad20_f1.0 against B2 | 30 | +14.3% [-38.3, +54.1] | +1.082 [-1.58, +4.003] | undecided |
| quarter_end | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 30 | +9.8% [+7.2, +14.3] | +0.7031 [+0.05802, +3.845] | gain |
| quarter_end | spread_mr_fhs_mad40_f0.5 against B1 | 30 | +6.5% [+2.7, +9.5] | +0.4503 [+0.09596, +1.191] | gain |
| quarter_end | spread_mr_fhs_mad40_f0.5 against B2 | 30 | +13.9% [-38.4, +51.3] | +1.055 [-1.331, +3.587] | undecided |
| quarter_end | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 30 | +9.4% [+4.4, +14.6] | +0.6754 [+0.02047, +1.731] | gain |
| quarter_end | spread_mr_fhs_sd20_f0.5 against B1 | 30 | +13.1% [+9.8, +19.1] | +0.9131 [+0.1603, +4.094] | gain |
| quarter_end | spread_mr_fhs_sd20_f0.5 against B2 | 30 | +20.1% [-35.6, +60.2] | +1.517 [-0.8803, +4.785] | undecided |
| quarter_end | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 30 | +15.8% [+12.2, +25.5] | +1.138 [+0.1515, +4.601] | gain |
| quarter_end | spread_mr_level10 against B1 | 30 | -3.2% [-7.3, -0.4] | -0.2251 [-0.5343, +0.02676] | undecided (was loss) |
| quarter_end | spread_mr_level10 against B2 | 30 | +5.0% [-53.0, +46.7] | +0.3792 [-3.075, +3.135] | undecided |
| tax_date | spread_mr_fhs_mad10_f0.5 against B1 | 89 | +6.7% [-3.7, +13.6] | +0.3706 [+0.07494, +1.175] | gain (was undecided) |
| tax_date | spread_mr_fhs_mad10_f0.5 against B2 | 89 | +33.8% [-64.5, +57.8] | +2.612 [+1.408, +4.765] | gain (was undecided) |
| tax_date | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 89 | +5.2% [+2.6, +7.3] | +0.281 [+0.07646, +1.133] | gain |
| tax_date | spread_mr_fhs_mad20_f0.25 against B1 | 89 | +6.7% [-3.1, +12.9] | +0.3661 [+0.07103, +1.146] | gain (was undecided) |
| tax_date | spread_mr_fhs_mad20_f0.25 against B2 | 89 | +33.7% [-61.9, +57.5] | +2.608 [+1.414, +4.788] | gain (was undecided) |
| tax_date | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 89 | +5.1% [+2.9, +6.9] | +0.2764 [+0.06778, +1.114] | gain |
| tax_date | spread_mr_fhs_mad20_f0.5 against B1 | 89 | +6.8% [-6.2, +13.7] | +0.3754 [+0.05328, +1.128] | gain (was undecided) |
| tax_date | spread_mr_fhs_mad20_f0.5 against B2 | 89 | +33.8% [-62.9, +57.7] | +2.617 [+1.417, +4.825] | gain (was undecided) |
| tax_date | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 89 | +5.3% [+2.7, +7.5] | +0.2857 [+0.07815, +1.264] | gain |
| tax_date | spread_mr_fhs_mad20_f1.0 against B1 | 89 | +6.3% [-4.7, +13.0] | +0.3473 [+0.01495, +1.117] | gain (was undecided) |
| tax_date | spread_mr_fhs_mad20_f1.0 against B2 | 89 | +33.5% [-62.1, +57.0] | +2.589 [+1.384, +4.787] | gain (was undecided) |
| tax_date | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 89 | +4.8% [+3.0, +6.6] | +0.2577 [+0.04998, +1.566] | gain |
| tax_date | spread_mr_fhs_mad40_f0.5 against B1 | 89 | +4.3% [-9.3, +10.8] | +0.2372 [-0.05822, +0.5311] | undecided |
| tax_date | spread_mr_fhs_mad40_f0.5 against B2 | 89 | +32.0% [-62.8, +56.6] | +2.479 [+1.41, +4.439] | gain (was undecided) |
| tax_date | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 89 | +2.7% [+0.6, +4.9] | +0.1476 [+0.03373, +0.3654] | gain |
| tax_date | spread_mr_fhs_sd20_f0.5 against B1 | 89 | +1.9% [-10.0, +10.4] | +0.1058 [-0.1677, +0.381] | undecided |
| tax_date | spread_mr_fhs_sd20_f0.5 against B2 | 89 | +30.3% [-76.8, +56.0] | +2.347 [+1.366, +3.862] | gain (was undecided) |
| tax_date | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 89 | +0.3% [-3.2, +3.4] | +0.01616 [-0.1467, +0.132] | undecided |
| tax_date | spread_mr_level10 against B1 | 89 | +1.6% [-5.1, +7.6] | +0.08967 [-0.09145, +0.3621] | undecided |
| tax_date | spread_mr_level10 against B2 | 89 | +30.1% [-71.1, +54.4] | +2.331 [+1.358, +4.061] | gain (was undecided) |

### brier_0, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2018-19 | spread_mr_fhs_mad10_f0.5 against B1 | 361 | +13.6% [+3.8, +22.4] | +0.0226 [+0.00709, +0.03792] | gain |
| 2018-19 | spread_mr_fhs_mad10_f0.5 against B2 | 361 | +44.3% [+24.4, +61.6] | +0.1145 [+0.0508, +0.1873] | gain |
| 2018-19 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 361 | -6.8% [-13.7, -1.6] | -0.009151 [-0.01771, -0.002313] | loss |
| 2018-19 | spread_mr_fhs_mad20_f0.25 against B1 | 361 | +13.5% [+4.4, +21.7] | +0.02253 [+0.00821, +0.03667] | gain |
| 2018-19 | spread_mr_fhs_mad20_f0.25 against B2 | 361 | +44.3% [+24.3, +62.0] | +0.1145 [+0.05062, +0.1885] | gain |
| 2018-19 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 361 | -6.9% [-12.1, -2.2] | -0.009222 [-0.01592, -0.00309] | loss |
| 2018-19 | spread_mr_fhs_mad20_f0.5 against B1 | 361 | +13.7% [+4.3, +22.1] | +0.02283 [+0.008186, +0.03725] | gain |
| 2018-19 | spread_mr_fhs_mad20_f0.5 against B2 | 361 | +44.4% [+24.5, +62.0] | +0.1148 [+0.05112, +0.1886] | gain |
| 2018-19 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 361 | -6.6% [-11.9, -1.9] | -0.008926 [-0.01579, -0.002653] | loss |
| 2018-19 | spread_mr_fhs_mad20_f1.0 against B1 | 361 | +13.6% [+4.2, +22.1] | +0.02269 [+0.007878, +0.03714] | gain |
| 2018-19 | spread_mr_fhs_mad20_f1.0 against B2 | 361 | +44.4% [+24.5, +62.1] | +0.1146 [+0.05113, +0.1888] | gain |
| 2018-19 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 361 | -6.7% [-12.1, -1.9] | -0.009059 [-0.01612, -0.002688] | loss |
| 2018-19 | spread_mr_fhs_mad40_f0.5 against B1 | 361 | +16.1% [+6.1, +24.4] | +0.02673 [+0.01213, +0.04002] | gain |
| 2018-19 | spread_mr_fhs_mad40_f0.5 against B2 | 361 | +45.9% [+26.2, +63.5] | +0.1187 [+0.05598, +0.192] | gain |
| 2018-19 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 361 | -3.7% [-8.5, +0.9] | -0.005021 [-0.01198, +0.0008724] | undecided |
| 2018-19 | spread_mr_fhs_sd20_f0.5 against B1 | 361 | +10.5% [-0.9, +19.4] | +0.01754 [-0.002265, +0.03468] | undecided |
| 2018-19 | spread_mr_fhs_sd20_f0.5 against B2 | 361 | +42.4% [+23.0, +59.9] | +0.1095 [+0.04473, +0.1841] | gain |
| 2018-19 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 361 | -10.6% [-29.0, -1.6] | -0.01421 [-0.03453, -0.002389] | loss |
| 2018-19 | spread_mr_level10 against B1 | 361 | +19.1% [+11.4, +26.1] | +0.03175 [+0.02076, +0.04314] | gain |
| 2018-19 | spread_mr_level10 against B2 | 361 | +47.9% [+28.9, +64.4] | +0.1237 [+0.06057, +0.1954] | gain |

### brier_10, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2018-19 | spread_mr_fhs_mad10_f0.5 against B1 | 361 | +33.6% [+24.7, +41.4] | +0.04685 [+0.02912, +0.07044] | gain |
| 2018-19 | spread_mr_fhs_mad10_f0.5 against B2 | 361 | +2.1% [-16.2, +17.4] | +0.00199 [-0.01294, +0.01952] | undecided |
| 2018-19 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 361 | +2.2% [-5.6, +8.5] | +0.002112 [-0.004059, +0.009408] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f0.25 against B1 | 361 | +33.4% [+19.9, +42.9] | +0.0466 [+0.02587, +0.07339] | gain |
| 2018-19 | spread_mr_fhs_mad20_f0.25 against B2 | 361 | +1.8% [-14.2, +15.0] | +0.001739 [-0.0116, +0.01686] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 361 | +2.0% [-3.4, +7.2] | +0.00186 [-0.002725, +0.008021] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f0.5 against B1 | 361 | +33.4% [+19.9, +42.9] | +0.04658 [+0.02587, +0.07334] | gain |
| 2018-19 | spread_mr_fhs_mad20_f0.5 against B2 | 361 | +1.8% [-14.2, +15.0] | +0.00172 [-0.0116, +0.01682] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 361 | +1.9% [-3.3, +7.1] | +0.001841 [-0.002695, +0.007892] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f1.0 against B1 | 361 | +33.5% [+19.8, +43.1] | +0.04668 [+0.02588, +0.07329] | gain |
| 2018-19 | spread_mr_fhs_mad20_f1.0 against B2 | 361 | +1.9% [-14.0, +15.0] | +0.001813 [-0.01148, +0.01687] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 361 | +2.0% [-3.0, +7.0] | +0.001934 [-0.002497, +0.007756] | undecided |
| 2018-19 | spread_mr_fhs_mad40_f0.5 against B1 | 361 | +30.9% [+17.4, +40.6] | +0.04301 [+0.02264, +0.06876] | gain |
| 2018-19 | spread_mr_fhs_mad40_f0.5 against B2 | 361 | -2.0% [-18.2, +11.6] | -0.001852 [-0.01505, +0.01317] | undecided |
| 2018-19 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 361 | -1.8% [-7.4, +2.3] | -0.00173 [-0.006005, +0.002334] | undecided |
| 2018-19 | spread_mr_fhs_sd20_f0.5 against B1 | 361 | +23.0% [+11.2, +32.0] | +0.0321 [+0.01426, +0.05418] | gain |
| 2018-19 | spread_mr_fhs_sd20_f0.5 against B2 | 361 | -13.5% [-37.3, +4.2] | -0.01277 [-0.03028, +0.005463] | undecided |
| 2018-19 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 361 | -13.4% [-28.4, -4.2] | -0.01264 [-0.02373, -0.00478] | loss |
| 2018-19 | spread_mr_level10 against B1 | 361 | +32.1% [+18.7, +42.8] | +0.04474 [+0.02529, +0.07055] | gain |
| 2018-19 | spread_mr_level10 against B2 | 361 | -0.1% [-14.8, +12.9] | -0.0001216 [-0.01267, +0.01415] | undecided |

### brier_5, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2018-19 | spread_mr_fhs_mad10_f0.5 against B1 | 361 | +16.0% [+4.8, +25.0] | +0.03416 [+0.01121, +0.05788] | gain |
| 2018-19 | spread_mr_fhs_mad10_f0.5 against B2 | 361 | +13.8% [-4.4, +30.0] | +0.02868 [-0.008035, +0.07389] | undecided |
| 2018-19 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 361 | +5.4% [+0.2, +12.5] | +0.01017 [+0.0005112, +0.02668] | gain |
| 2018-19 | spread_mr_fhs_mad20_f0.25 against B1 | 361 | +14.5% [+0.6, +25.5] | +0.03098 [+0.003118, +0.05878] | gain |
| 2018-19 | spread_mr_fhs_mad20_f0.25 against B2 | 361 | +12.2% [-3.9, +28.0] | +0.02549 [-0.008109, +0.06821] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 361 | +3.7% [-1.1, +10.1] | +0.006988 [-0.001908, +0.02128] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f0.5 against B1 | 361 | +14.3% [+0.3, +25.4] | +0.03067 [+0.002579, +0.05847] | gain |
| 2018-19 | spread_mr_fhs_mad20_f0.5 against B2 | 361 | +12.1% [-4.1, +27.9] | +0.02518 [-0.008281, +0.06783] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 361 | +3.5% [-1.4, +10.0] | +0.006674 [-0.00229, +0.02086] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f1.0 against B1 | 361 | +14.3% [+0.2, +25.3] | +0.03049 [+0.002282, +0.05835] | gain |
| 2018-19 | spread_mr_fhs_mad20_f1.0 against B2 | 361 | +12.0% [-4.2, +27.8] | +0.025 [-0.008414, +0.06773] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 361 | +3.4% [-1.5, +9.9] | +0.006499 [-0.002538, +0.02061] | undecided |
| 2018-19 | spread_mr_fhs_mad40_f0.5 against B1 | 361 | +10.6% [-2.5, +21.3] | +0.02268 [-0.003265, +0.04822] | undecided |
| 2018-19 | spread_mr_fhs_mad40_f0.5 against B2 | 361 | +8.3% [-9.5, +25.2] | +0.01719 [-0.01753, +0.06029] | undecided |
| 2018-19 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 361 | -0.7% [-5.4, +4.2] | -0.00131 [-0.009447, +0.007548] | undecided |
| 2018-19 | spread_mr_fhs_sd20_f0.5 against B1 | 361 | +13.8% [+1.9, +23.1] | +0.02959 [+0.004632, +0.05406] | gain |
| 2018-19 | spread_mr_fhs_sd20_f0.5 against B2 | 361 | +11.6% [-6.2, +28.0] | +0.0241 [-0.01145, +0.06988] | undecided |
| 2018-19 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 361 | +3.0% [-3.7, +11.1] | +0.0056 [-0.006522, +0.02394] | undecided |
| 2018-19 | spread_mr_level10 against B1 | 361 | +11.2% [-1.6, +21.9] | +0.02399 [-0.001764, +0.04875] | undecided |
| 2018-19 | spread_mr_level10 against B2 | 361 | +8.9% [-10.4, +26.4] | +0.0185 [-0.0188, +0.06288] | undecided |

### grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2018-19 | spread_mr_fhs_mad10_f0.5 against B1 | 361 | +32.4% [+23.6, +55.8] | +1.878 [+0.7438, +9.372] | gain |
| 2018-19 | spread_mr_fhs_mad10_f0.5 against B2 | 361 | +12.3% [-1.2, +26.0] | +0.549 [+0.05028, +1.083] | gain (was undecided) |
| 2018-19 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 361 | -2.2% [-7.5, +2.3] | -0.08595 [-0.228, +0.04028] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f0.25 against B1 | 361 | +33.9% [+24.1, +58.4] | +1.966 [+0.7577, +8.919] | gain |
| 2018-19 | spread_mr_fhs_mad20_f0.25 against B2 | 361 | +14.3% [+1.1, +27.9] | +0.6364 [+0.1859, +1.174] | gain |
| 2018-19 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 361 | +0.0% [-4.0, +6.4] | +0.001492 [-0.1093, +0.2652] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f0.5 against B1 | 361 | +34.1% [+24.3, +57.8] | +1.974 [+0.7707, +8.894] | gain |
| 2018-19 | spread_mr_fhs_mad20_f0.5 against B2 | 361 | +14.5% [+1.2, +28.2] | +0.645 [+0.1946, +1.18] | gain |
| 2018-19 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 361 | +0.3% [-3.5, +5.8] | +0.01011 [-0.09614, +0.252] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f1.0 against B1 | 361 | +34.2% [+24.5, +57.0] | +1.98 [+0.7828, +8.815] | gain |
| 2018-19 | spread_mr_fhs_mad20_f1.0 against B2 | 361 | +14.6% [+1.3, +28.6] | +0.6507 [+0.2024, +1.183] | gain |
| 2018-19 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 361 | +0.4% [-3.1, +5.1] | +0.01576 [-0.08418, +0.2256] | undecided |
| 2018-19 | spread_mr_fhs_mad40_f0.5 against B1 | 361 | +33.0% [+23.2, +54.8] | +1.913 [+0.7368, +8.254] | gain |
| 2018-19 | spread_mr_fhs_mad40_f0.5 against B2 | 361 | +13.1% [-0.5, +27.6] | +0.5834 [+0.1305, +1.135] | gain (was undecided) |
| 2018-19 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 361 | -1.3% [-4.9, +2.5] | -0.05153 [-0.1296, +0.06007] | undecided |
| 2018-19 | spread_mr_fhs_sd20_f0.5 against B1 | 361 | +17.6% [-0.4, +36.0] | +1.018 [+0.02047, +3.57] | gain (was undecided) |
| 2018-19 | spread_mr_fhs_sd20_f0.5 against B2 | 361 | -7.0% [-55.5, +14.1] | -0.3113 [-2.51, +0.7494] | undecided |
| 2018-19 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 361 | -24.7% [-93.5, -4.7] | -0.9463 [-4.26, -0.1858] | loss |
| 2018-19 | spread_mr_level10 against B1 | 361 | +33.9% [+24.6, +51.8] | +1.964 [+0.8407, +8.161] | gain |
| 2018-19 | spread_mr_level10 against B2 | 361 | +14.2% [-1.9, +30.2] | +0.6349 [+0.1706, +1.188] | gain (was undecided) |

### upper_tail_twcrps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2018-19 | spread_mr_fhs_mad10_f0.5 against B1 | 361 | +34.3% [+24.6, +57.2] | +1.811 [+0.6451, +9.148] | gain |
| 2018-19 | spread_mr_fhs_mad10_f0.5 against B2 | 361 | +9.0% [-3.0, +22.2] | +0.3445 [-0.06908, +0.8101] | undecided |
| 2018-19 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 361 | -0.5% [-5.1, +3.7] | -0.01657 [-0.1236, +0.1205] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f0.25 against B1 | 361 | +35.8% [+25.2, +59.1] | +1.889 [+0.6612, +8.759] | gain |
| 2018-19 | spread_mr_fhs_mad20_f0.25 against B2 | 361 | +11.1% [-1.1, +24.2] | +0.4227 [+0.041, +0.8803] | gain (was undecided) |
| 2018-19 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 361 | +1.8% [-1.8, +7.7] | +0.06162 [-0.05385, +0.41] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f0.5 against B1 | 361 | +35.7% [+25.1, +58.8] | +1.885 [+0.6622, +8.743] | gain |
| 2018-19 | spread_mr_fhs_mad20_f0.5 against B2 | 361 | +11.0% [-1.1, +24.2] | +0.419 [+0.03926, +0.8762] | gain (was undecided) |
| 2018-19 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 361 | +1.7% [-1.8, +7.0] | +0.0579 [-0.0524, +0.3681] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f1.0 against B1 | 361 | +35.6% [+25.1, +58.3] | +1.878 [+0.6613, +8.67] | gain |
| 2018-19 | spread_mr_fhs_mad20_f1.0 against B2 | 361 | +10.8% [-1.3, +24.2] | +0.4123 [+0.03342, +0.8683] | gain (was undecided) |
| 2018-19 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 361 | +1.5% [-1.8, +6.1] | +0.05123 [-0.0513, +0.3134] | undecided |
| 2018-19 | spread_mr_fhs_mad40_f0.5 against B1 | 361 | +34.5% [+24.0, +56.4] | +1.822 [+0.6365, +8.227] | gain |
| 2018-19 | spread_mr_fhs_mad40_f0.5 against B2 | 361 | +9.3% [-3.0, +23.7] | +0.3556 [-0.02607, +0.8287] | undecided |
| 2018-19 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 361 | -0.2% [-2.9, +3.1] | -0.005511 [-0.07133, +0.1166] | undecided |
| 2018-19 | spread_mr_fhs_sd20_f0.5 against B1 | 361 | +21.4% [+6.1, +42.6] | +1.128 [+0.154, +4.606] | gain |
| 2018-19 | spread_mr_fhs_sd20_f0.5 against B2 | 361 | -8.9% [-49.0, +9.9] | -0.338 [-1.892, +0.4991] | undecided |
| 2018-19 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 361 | -20.2% [-74.3, -2.7] | -0.6991 [-3.073, -0.135] | loss |
| 2018-19 | spread_mr_level10 against B1 | 361 | +34.6% [+24.4, +53.3] | +1.827 [+0.6969, +8.035] | gain |
| 2018-19 | spread_mr_level10 against B2 | 361 | +9.5% [-4.9, +25.5] | +0.3611 [-0.04185, +0.8421] | undecided |

### brier_0, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2020 | spread_mr_fhs_mad10_f0.5 against B1 | 251 | +6.8% [-9.8, +19.4] | +0.007699 [-0.01044, +0.0219] | undecided |
| 2020 | spread_mr_fhs_mad10_f0.5 against B2 | 251 | +57.0% [+28.2, +78.0] | +0.1407 [+0.0455, +0.2497] | gain |
| 2020 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 251 | +16.7% [+2.2, +32.5] | +0.02129 [+0.005275, +0.03959] | gain |
| 2020 | spread_mr_fhs_mad20_f0.25 against B1 | 251 | +2.8% [-15.3, +17.6] | +0.003242 [-0.0179, +0.01974] | undecided |
| 2020 | spread_mr_fhs_mad20_f0.25 against B2 | 251 | +55.2% [+24.8, +76.6] | +0.1362 [+0.04107, +0.2414] | gain |
| 2020 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 251 | +13.2% [-3.8, +34.9] | +0.01683 [-0.003163, +0.04183] | undecided |
| 2020 | spread_mr_fhs_mad20_f0.5 against B1 | 251 | +3.5% [-12.2, +15.9] | +0.003957 [-0.01445, +0.01811] | undecided |
| 2020 | spread_mr_fhs_mad20_f0.5 against B2 | 251 | +55.5% [+26.6, +76.5] | +0.1369 [+0.04399, +0.2429] | gain |
| 2020 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 251 | +13.8% [+0.6, +32.7] | +0.01755 [+0.002204, +0.039] | gain |
| 2020 | spread_mr_fhs_mad20_f1.0 against B1 | 251 | +1.1% [-13.2, +11.2] | +0.0013 [-0.01477, +0.01315] | undecided |
| 2020 | spread_mr_fhs_mad20_f1.0 against B2 | 251 | +54.4% [+26.7, +75.5] | +0.1343 [+0.04219, +0.2422] | gain |
| 2020 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 251 | +11.7% [+2.8, +23.1] | +0.01489 [+0.005581, +0.02673] | gain |
| 2020 | spread_mr_fhs_mad40_f0.5 against B1 | 251 | +2.5% [-13.5, +15.8] | +0.002877 [-0.01561, +0.01778] | undecided |
| 2020 | spread_mr_fhs_mad40_f0.5 against B2 | 251 | +55.0% [+26.5, +75.8] | +0.1358 [+0.04417, +0.2412] | gain |
| 2020 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 251 | +12.9% [-0.4, +34.6] | +0.01647 [+0.001356, +0.04071] | gain (was undecided) |
| 2020 | spread_mr_fhs_sd20_f0.5 against B1 | 251 | +11.6% [-17.3, +33.4] | +0.01325 [-0.02031, +0.03404] | undecided |
| 2020 | spread_mr_fhs_sd20_f0.5 against B2 | 251 | +59.2% [+25.4, +80.4] | +0.1462 [+0.05333, +0.2488] | gain |
| 2020 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 251 | +21.0% [-7.4, +46.5] | +0.02684 [-0.005182, +0.05279] | undecided |
| 2020 | spread_mr_level10 against B1 | 251 | -11.9% [-28.2, +0.4] | -0.01359 [-0.02914, -0.0003726] | loss (was undecided) |
| 2020 | spread_mr_level10 against B2 | 251 | +48.4% [+20.2, +70.9] | +0.1194 [+0.02651, +0.23] | gain |

### brier_10, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2020 | spread_mr_fhs_mad10_f0.5 against B1 | 251 | +38.9% [-12.7, +54.9] | +0.008314 [+0.0006161, +0.2536] | gain (was undecided) |
| 2020 | spread_mr_fhs_mad10_f0.5 against B2 | 251 | +42.5% [-475.4, +85.3] | +0.009669 [+0.005442, +0.01528] | gain (was undecided) |
| 2020 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 251 | +0.4% [-200.5, +14.2] | +5.128e-05 [-0.01449, +0.0021] | undecided |
| 2020 | spread_mr_fhs_mad20_f0.25 against B1 | 251 | +39.3% [+15.3, +75.1] | +0.008397 [+8.32e-05, +0.2399] | gain |
| 2020 | spread_mr_fhs_mad20_f0.25 against B2 | 251 | +42.9% [-249.9, +83.9] | +0.009752 [+0.005317, +0.01674] | gain (was undecided) |
| 2020 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 251 | +1.0% [-28.2, +10.5] | +0.0001344 [-0.003706, +0.001311] | undecided |
| 2020 | spread_mr_fhs_mad20_f0.5 against B1 | 251 | +41.2% [-11.0, +70.1] | +0.008822 [+0.000579, +0.3039] | gain (was undecided) |
| 2020 | spread_mr_fhs_mad20_f0.5 against B2 | 251 | +44.7% [-429.7, +87.0] | +0.01018 [+0.005839, +0.01708] | gain (was undecided) |
| 2020 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 251 | +4.3% [-87.0, +20.2] | +0.0005595 [-0.004427, +0.001735] | undecided |
| 2020 | spread_mr_fhs_mad20_f1.0 against B1 | 251 | +41.3% [-27.0, +70.1] | +0.008844 [+0.000613, +0.3211] | gain (was undecided) |
| 2020 | spread_mr_fhs_mad20_f1.0 against B2 | 251 | +44.8% [-480.4, +87.2] | +0.0102 [+0.005837, +0.01715] | gain (was undecided) |
| 2020 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 251 | +4.4% [-114.5, +21.3] | +0.000581 [-0.004611, +0.00175] | undecided |
| 2020 | spread_mr_fhs_mad40_f0.5 against B1 | 251 | +44.0% [-13.6, +82.5] | +0.009409 [+0.0004895, +0.5199] | gain (was undecided) |
| 2020 | spread_mr_fhs_mad40_f0.5 against B2 | 251 | +47.3% [-559.3, +90.0] | +0.01076 [+0.006031, +0.01951] | gain (was undecided) |
| 2020 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 251 | +8.7% [-92.6, +31.6] | +0.001147 [+0.0003103, +0.001622] | gain (was undecided) |
| 2020 | spread_mr_fhs_sd20_f0.5 against B1 | 251 | +36.4% [+3.5, +60.6] | +0.007786 [+9.112e-05, +0.07914] | gain |
| 2020 | spread_mr_fhs_sd20_f0.5 against B2 | 251 | +40.2% [-177.1, +81.7] | +0.00914 [+0.005408, +0.01394] | gain (was undecided) |
| 2020 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 251 | -3.6% [-36.2, +10.2] | -0.0004768 [-0.01004, +0.002109] | undecided |
| 2020 | spread_mr_level10 against B1 | 251 | +38.6% [+17.2, +266.9] | +0.008263 [-0.00102, +0.6221] | undecided (was gain) |
| 2020 | spread_mr_level10 against B2 | 251 | +42.3% [-149.1, +80.6] | +0.009617 [+0.004924, +0.01874] | gain (was undecided) |

### brier_5, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2020 | spread_mr_fhs_mad10_f0.5 against B1 | 251 | +34.4% [+7.0, +44.3] | +0.01032 [+0.003911, +0.04173] | gain |
| 2020 | spread_mr_fhs_mad10_f0.5 against B2 | 251 | +69.1% [-100.3, +94.1] | +0.04412 [+0.0235, +0.07083] | gain (was undecided) |
| 2020 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 251 | +13.8% [-113.1, +41.6] | +0.003145 [-0.009932, +0.007161] | undecided |
| 2020 | spread_mr_fhs_mad20_f0.25 against B1 | 251 | +31.4% [+12.6, +45.1] | +0.009426 [+0.002619, +0.0484] | gain |
| 2020 | spread_mr_fhs_mad20_f0.25 against B2 | 251 | +67.7% [-64.7, +91.4] | +0.04322 [+0.02186, +0.07024] | gain (was undecided) |
| 2020 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 251 | +9.9% [-44.7, +37.9] | +0.002252 [-0.004582, +0.005652] | undecided |
| 2020 | spread_mr_fhs_mad20_f0.5 against B1 | 251 | +33.6% [+6.4, +46.3] | +0.01009 [+0.003438, +0.05136] | gain |
| 2020 | spread_mr_fhs_mad20_f0.5 against B2 | 251 | +68.8% [-90.4, +92.6] | +0.04389 [+0.02278, +0.07065] | gain (was undecided) |
| 2020 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 251 | +12.8% [-75.6, +45.8] | +0.002914 [-0.004939, +0.006279] | undecided |
| 2020 | spread_mr_fhs_mad20_f1.0 against B1 | 251 | +34.9% [-12.6, +47.4] | +0.01047 [+0.003942, +0.05634] | gain (was undecided) |
| 2020 | spread_mr_fhs_mad20_f1.0 against B2 | 251 | +69.4% [-129.5, +93.4] | +0.04427 [+0.02343, +0.07092] | gain (was undecided) |
| 2020 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 251 | +14.4% [-157.2, +50.3] | +0.003297 [-0.006058, +0.006528] | undecided |
| 2020 | spread_mr_fhs_mad40_f0.5 against B1 | 251 | +38.1% [+6.2, +58.1] | +0.01143 [+0.003294, +0.08645] | gain |
| 2020 | spread_mr_fhs_mad40_f0.5 against B2 | 251 | +70.9% [-108.8, +93.3] | +0.04523 [+0.0238, +0.07331] | gain (was undecided) |
| 2020 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 251 | +18.6% [-67.9, +49.5] | +0.00426 [+0.001917, +0.006222] | gain (was undecided) |
| 2020 | spread_mr_fhs_sd20_f0.5 against B1 | 251 | +35.2% [-7.1, +50.3] | +0.01056 [+0.003875, +0.03168] | gain (was undecided) |
| 2020 | spread_mr_fhs_sd20_f0.5 against B2 | 251 | +69.5% [-134.6, +94.4] | +0.04436 [+0.02475, +0.06807] | gain (was undecided) |
| 2020 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 251 | +14.8% [-75.5, +52.6] | +0.003384 [-0.01256, +0.008954] | undecided |
| 2020 | spread_mr_level10 against B1 | 251 | +23.9% [+5.6, +116.7] | +0.007174 [-0.001695, +0.1548] | undecided (was gain) |
| 2020 | spread_mr_level10 against B2 | 251 | +64.2% [-13.9, +85.7] | +0.04097 [+0.0196, +0.07] | gain (was undecided) |

### grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2020 | spread_mr_fhs_mad10_f0.5 against B1 | 251 | +18.1% [+10.2, +27.9] | +0.2986 [+0.1283, +0.8057] | gain |
| 2020 | spread_mr_fhs_mad10_f0.5 against B2 | 251 | +51.7% [+29.6, +72.0] | +1.447 [+0.6011, +3.236] | gain |
| 2020 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 251 | +12.9% [+9.1, +16.6] | +0.1999 [+0.1305, +0.3382] | gain |
| 2020 | spread_mr_fhs_mad20_f0.25 against B1 | 251 | +12.2% [+3.3, +22.2] | +0.2011 [+0.04561, +0.553] | gain |
| 2020 | spread_mr_fhs_mad20_f0.25 against B2 | 251 | +48.3% [+24.2, +69.1] | +1.35 [+0.5236, +3.052] | gain |
| 2020 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 251 | +6.6% [+2.6, +10.5] | +0.1025 [+0.04741, +0.1632] | gain |
| 2020 | spread_mr_fhs_mad20_f0.5 against B1 | 251 | +14.6% [+6.2, +22.9] | +0.2409 [+0.09231, +0.5808] | gain |
| 2020 | spread_mr_fhs_mad20_f0.5 against B2 | 251 | +49.7% [+24.8, +70.1] | +1.39 [+0.5628, +3.107] | gain |
| 2020 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 251 | +9.2% [+3.6, +13.7] | +0.1422 [+0.09475, +0.1968] | gain |
| 2020 | spread_mr_fhs_mad20_f1.0 against B1 | 251 | +15.4% [+7.3, +22.7] | +0.2546 [+0.1122, +0.5831] | gain |
| 2020 | spread_mr_fhs_mad20_f1.0 against B2 | 251 | +50.2% [+24.6, +70.6] | +1.403 [+0.5732, +3.127] | gain |
| 2020 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 251 | +10.1% [+2.8, +14.7] | +0.1559 [+0.1181, +0.1969] | gain |
| 2020 | spread_mr_fhs_mad40_f0.5 against B1 | 251 | +10.9% [+0.6, +17.5] | +0.18 [+0.0481, +0.3771] | gain |
| 2020 | spread_mr_fhs_mad40_f0.5 against B2 | 251 | +47.5% [+20.3, +69.6] | +1.329 [+0.5175, +3.043] | gain |
| 2020 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 251 | +5.3% [-5.3, +12.5] | +0.08137 [-0.01389, +0.1409] | undecided |
| 2020 | spread_mr_fhs_sd20_f0.5 against B1 | 251 | +11.6% [-3.6, +22.6] | +0.192 [-0.01184, +0.477] | undecided |
| 2020 | spread_mr_fhs_sd20_f0.5 against B2 | 251 | +47.9% [+22.9, +64.5] | +1.341 [+0.5762, +2.776] | gain |
| 2020 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 251 | +6.0% [-5.6, +13.2] | +0.09332 [-0.09728, +0.1894] | undecided |
| 2020 | spread_mr_level10 against B1 | 251 | +6.0% [-2.5, +18.8] | +0.09867 [-0.03433, +0.4453] | undecided |
| 2020 | spread_mr_level10 against B2 | 251 | +44.6% [+20.5, +68.8] | +1.247 [+0.4299, +3.043] | gain |

### upper_tail_twcrps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2020 | spread_mr_fhs_mad10_f0.5 against B1 | 251 | +32.5% [+21.8, +48.3] | +0.2404 [+0.06356, +1.586] | gain |
| 2020 | spread_mr_fhs_mad10_f0.5 against B2 | 251 | +59.0% [-13.8, +86.0] | +0.7193 [+0.3823, +1.141] | gain (was undecided) |
| 2020 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 251 | +14.8% [-27.3, +35.1] | +0.08711 [-0.03227, +0.1459] | undecided |
| 2020 | spread_mr_fhs_mad20_f0.25 against B1 | 251 | +29.5% [+15.9, +57.0] | +0.2181 [+0.03892, +1.453] | gain |
| 2020 | spread_mr_fhs_mad20_f0.25 against B2 | 251 | +57.2% [-17.0, +84.0] | +0.6971 [+0.3438, +1.124] | gain (was undecided) |
| 2020 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 251 | +11.0% [-14.2, +36.1] | +0.06485 [-0.01429, +0.1345] | undecided |
| 2020 | spread_mr_fhs_mad20_f0.5 against B1 | 251 | +31.0% [+17.2, +55.5] | +0.2293 [+0.05255, +1.633] | gain |
| 2020 | spread_mr_fhs_mad20_f0.5 against B2 | 251 | +58.1% [-22.6, +84.9] | +0.7083 [+0.3622, +1.132] | gain (was undecided) |
| 2020 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 251 | +13.0% [-21.6, +38.7] | +0.07604 [-0.006488, +0.1363] | undecided |
| 2020 | spread_mr_fhs_mad20_f1.0 against B1 | 251 | +30.4% [+17.2, +55.9] | +0.2247 [+0.04885, +1.833] | gain |
| 2020 | spread_mr_fhs_mad20_f1.0 against B2 | 251 | +57.7% [-24.6, +84.4] | +0.7037 [+0.3611, +1.132] | gain (was undecided) |
| 2020 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 251 | +12.2% [-34.5, +35.7] | +0.07144 [-0.02716, +0.1195] | undecided |
| 2020 | spread_mr_fhs_mad40_f0.5 against B1 | 251 | +32.0% [+16.3, +64.3] | +0.2369 [+0.04811, +1.928] | gain |
| 2020 | spread_mr_fhs_mad40_f0.5 against B2 | 251 | +58.7% [-26.5, +85.1] | +0.7158 [+0.3657, +1.155] | gain (was undecided) |
| 2020 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 251 | +14.2% [-22.6, +38.0] | +0.08361 [+0.02833, +0.1379] | gain (was undecided) |
| 2020 | spread_mr_fhs_sd20_f0.5 against B1 | 251 | +32.1% [+8.0, +47.8] | +0.2376 [+0.07696, +0.966] | gain |
| 2020 | spread_mr_fhs_sd20_f0.5 against B2 | 251 | +58.8% [-38.4, +86.9] | +0.7165 [+0.4057, +1.075] | gain (was undecided) |
| 2020 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 251 | +14.4% [-40.6, +47.1] | +0.08431 [-0.1585, +0.1926] | undecided |
| 2020 | spread_mr_level10 against B1 | 251 | +20.7% [+0.0, +102.9] | +0.1533 [-0.0564, +2.36] | undecided (was gain) |
| 2020 | spread_mr_level10 against B2 | 251 | +51.9% [-1.8, +76.7] | +0.6322 [+0.2791, +1.094] | gain (was undecided) |

### brier_0, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2021-23 | spread_mr_fhs_mad10_f0.5 against B1 | 748 | -9.5% [-86.8, +37.6] | -0.0002775 [-0.002625, +0.0004554] | undecided |
| 2021-23 | spread_mr_fhs_mad10_f0.5 against B2 | 748 | -82.0% [-713.2, +24.2] | -0.001436 [-0.0206, +0.000329] | undecided |
| 2021-23 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 748 | +4.5% [-15.0, +21.5] | +0.0001493 [-0.0002098, +0.0004023] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f0.25 against B1 | 748 | -24.6% [-165.0, +79.8] | -0.0007165 [-0.00451, +0.0003516] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f0.25 against B2 | 748 | -107.0% [-712.8, +56.3] | -0.001875 [-0.0205, +0.0001631] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 748 | -8.7% [-25.4, +4.8] | -0.0002897 [-0.001581, +0.0001911] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f0.5 against B1 | 748 | -16.0% [-155.9, +46.6] | -0.0004644 [-0.005197, +0.0004906] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f0.5 against B2 | 748 | -92.6% [-878.1, +42.6] | -0.001623 [-0.02476, +0.0003432] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 748 | -1.1% [-17.1, +12.8] | -3.757e-05 [-0.001015, +0.0003259] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f1.0 against B1 | 748 | -5.4% [-109.6, +33.1] | -0.0001569 [-0.00495, +0.0006203] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f1.0 against B2 | 748 | -75.1% [-945.6, +26.4] | -0.001316 [-0.02749, +0.0004112] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 748 | +8.1% [-29.5, +28.9] | +0.0002699 [+3.436e-05, +0.0004918] | gain (was undecided) |
| 2021-23 | spread_mr_fhs_mad40_f0.5 against B1 | 748 | -11.3% [-147.6, +40.8] | -0.0003294 [-0.005845, +0.0005747] | undecided |
| 2021-23 | spread_mr_fhs_mad40_f0.5 against B2 | 748 | -84.9% [-950.0, +38.6] | -0.001488 [-0.02957, +0.0003875] | undecided |
| 2021-23 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 748 | +2.9% [-20.6, +17.9] | +9.744e-05 [-0.0005315, +0.0003718] | undecided |
| 2021-23 | spread_mr_fhs_sd20_f0.5 against B1 | 748 | +27.1% [-121.4, +46.0] | +0.000788 [+0.0001027, +0.005831] | gain (was undecided) |
| 2021-23 | spread_mr_fhs_sd20_f0.5 against B2 | 748 | -21.2% [-729.6, +14.1] | -0.000371 [-0.004941, +0.000478] | undecided |
| 2021-23 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 748 | +36.4% [-226.4, +61.2] | +0.001215 [+0.0002802, +0.005089] | gain (was undecided) |
| 2021-23 | spread_mr_level10 against B1 | 748 | -14.7% [-84.2, +104.8] | -0.0004268 [-0.002658, +0.0003572] | undecided |
| 2021-23 | spread_mr_level10 against B2 | 748 | -90.5% [-730.5, +38.2] | -0.001586 [-0.03562, +6.48e-05] | undecided |

### grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2021-23 | spread_mr_fhs_mad10_f0.5 against B1 | 748 | +5.9% [-0.3, +10.8] | +0.04095 [+0.001272, +0.07246] | gain (was undecided) |
| 2021-23 | spread_mr_fhs_mad10_f0.5 against B2 | 748 | +55.2% [+41.3, +67.6] | +0.8088 [+0.5078, +1.188] | gain |
| 2021-23 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 748 | +8.3% [+2.9, +15.7] | +0.05907 [+0.02262, +0.1045] | gain |
| 2021-23 | spread_mr_fhs_mad20_f0.25 against B1 | 748 | +5.3% [-1.5, +11.5] | +0.03666 [-0.007595, +0.07738] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f0.25 against B2 | 748 | +54.9% [+40.6, +67.9] | +0.8045 [+0.499, +1.191] | gain |
| 2021-23 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 748 | +7.7% [+1.0, +16.8] | +0.05477 [+0.007304, +0.1121] | gain |
| 2021-23 | spread_mr_fhs_mad20_f0.5 against B1 | 748 | +5.5% [-0.6, +10.5] | +0.03824 [-0.0002277, +0.06997] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f0.5 against B2 | 748 | +55.0% [+41.1, +67.4] | +0.8061 [+0.5081, +1.182] | gain |
| 2021-23 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 748 | +7.9% [+2.6, +15.5] | +0.05635 [+0.02051, +0.1024] | gain |
| 2021-23 | spread_mr_fhs_mad20_f1.0 against B1 | 748 | +3.0% [-2.4, +6.9] | +0.02063 [-0.01374, +0.04661] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f1.0 against B2 | 748 | +53.8% [+40.5, +65.4] | +0.7885 [+0.5003, +1.148] | gain |
| 2021-23 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 748 | +5.4% [+2.1, +10.3] | +0.03874 [+0.01722, +0.06686] | gain |
| 2021-23 | spread_mr_fhs_mad40_f0.5 against B1 | 748 | +4.2% [-2.4, +9.7] | +0.02953 [-0.01397, +0.0632] | undecided |
| 2021-23 | spread_mr_fhs_mad40_f0.5 against B2 | 748 | +54.4% [+40.2, +67.0] | +0.7974 [+0.499, +1.167] | gain |
| 2021-23 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 748 | +6.7% [+1.2, +14.7] | +0.04764 [+0.0112, +0.09425] | gain |
| 2021-23 | spread_mr_fhs_sd20_f0.5 against B1 | 748 | +7.6% [-0.0, +13.7] | +0.05301 [+0.006312, +0.09139] | gain (was undecided) |
| 2021-23 | spread_mr_fhs_sd20_f0.5 against B2 | 748 | +56.0% [+41.9, +68.8] | +0.8208 [+0.5183, +1.2] | gain |
| 2021-23 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 748 | +9.9% [+3.8, +18.4] | +0.07113 [+0.03072, +0.1211] | gain |
| 2021-23 | spread_mr_level10 against B1 | 748 | -2.6% [-7.5, +1.7] | -0.01811 [-0.05081, +0.0115] | undecided |
| 2021-23 | spread_mr_level10 against B2 | 748 | +51.2% [+39.0, +61.4] | +0.7497 [+0.4787, +1.085] | gain |

### upper_tail_twcrps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2021-23 | spread_mr_fhs_mad10_f0.5 against B1 | 748 | +27.3% [-39.9, +57.0] | +0.002438 [+0.0002305, +0.004609] | gain (was undecided) |
| 2021-23 | spread_mr_fhs_mad10_f0.5 against B2 | 748 | -112.5% [-622.4, -19.6] | -0.003442 [-0.04122, +0.0005993] | undecided (was loss) |
| 2021-23 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 748 | +47.9% [-17.0, +79.0] | +0.005974 [+0.002956, +0.01053] | gain (was undecided) |
| 2021-23 | spread_mr_fhs_mad20_f0.25 against B1 | 748 | -18.2% [-94.8, +20.9] | -0.001628 [-0.01153, +0.001786] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f0.25 against B2 | 748 | -245.3% [-672.3, -77.9] | -0.007507 [-0.0405, -0.0008442] | loss |
| 2021-23 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 748 | +15.3% [-21.4, +59.1] | +0.001909 [-0.0008649, +0.005159] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f0.5 against B1 | 748 | +12.3% [-65.2, +44.6] | +0.0011 [-0.003811, +0.003375] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f0.5 against B2 | 748 | -156.2% [-788.6, -35.4] | -0.004779 [-0.0499, +0.0003363] | undecided (was loss) |
| 2021-23 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 748 | +37.2% [-25.3, +74.9] | +0.004637 [+0.002259, +0.008115] | gain (was undecided) |
| 2021-23 | spread_mr_fhs_mad20_f1.0 against B1 | 748 | +26.7% [-41.3, +50.7] | +0.00239 [+0.00018, +0.004743] | gain (was undecided) |
| 2021-23 | spread_mr_fhs_mad20_f1.0 against B2 | 748 | -114.0% [-736.6, -21.5] | -0.003489 [-0.04863, +0.0003514] | undecided (was loss) |
| 2021-23 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 748 | +47.5% [-10.6, +75.9] | +0.005927 [+0.002964, +0.01034] | gain (was undecided) |
| 2021-23 | spread_mr_fhs_mad40_f0.5 against B1 | 748 | +12.4% [-59.6, +42.0] | +0.00111 [-0.003203, +0.003247] | undecided |
| 2021-23 | spread_mr_fhs_mad40_f0.5 against B2 | 748 | -155.9% [-757.3, -40.0] | -0.00477 [-0.0471, +0.0001527] | undecided (was loss) |
| 2021-23 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 748 | +37.2% [-20.5, +72.6] | +0.004647 [+0.002251, +0.008047] | gain (was undecided) |
| 2021-23 | spread_mr_fhs_sd20_f0.5 against B1 | 748 | +67.6% [-19.1, +83.3] | +0.006046 [+0.002612, +0.01672] | gain (was undecided) |
| 2021-23 | spread_mr_fhs_sd20_f0.5 against B2 | 748 | +5.4% [-331.2, +54.3] | +0.0001664 [-0.002593, +0.001455] | undecided |
| 2021-23 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 748 | +76.8% [-16.6, +90.5] | +0.009582 [+0.004021, +0.02337] | gain (was undecided) |
| 2021-23 | spread_mr_level10 against B1 | 748 | -39.6% [-75.5, +33.8] | -0.003537 [-0.01041, -0.001234] | loss (was undecided) |
| 2021-23 | spread_mr_level10 against B2 | 748 | -307.7% [-508.1, +1.4] | -0.009416 [-0.03075, -0.003587] | loss (was undecided) |

### brier_0, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2024 | spread_mr_fhs_mad10_f0.5 against B1 | 250 | +33.5% [+18.2, +68.1] | +0.01133 [+0.0009794, +0.1173] | gain |
| 2024 | spread_mr_fhs_mad10_f0.5 against B2 | 250 | -0.9% [-27.3, +25.5] | -0.0001929 [-0.003204, +0.006374] | undecided |
| 2024 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 250 | +6.3% [-8.2, +18.3] | +0.001512 [-0.00147, +0.01719] | undecided |
| 2024 | spread_mr_fhs_mad20_f0.25 against B1 | 250 | +25.6% [+3.6, +52.2] | +0.008652 [-0.002784, +0.1011] | undecided (was gain) |
| 2024 | spread_mr_fhs_mad20_f0.25 against B2 | 250 | -12.9% [-57.4, +53.6] | -0.002873 [-0.006705, +0.005023] | undecided |
| 2024 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 250 | -4.9% [-43.0, +17.5] | -0.001169 [-0.005422, +0.01211] | undecided |
| 2024 | spread_mr_fhs_mad20_f0.5 against B1 | 250 | +32.8% [+15.1, +112.5] | +0.01109 [+0.0008234, +0.1349] | gain |
| 2024 | spread_mr_fhs_mad20_f0.5 against B2 | 250 | -1.9% [-24.3, +22.5] | -0.0004316 [-0.002827, +0.004304] | undecided |
| 2024 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 250 | +5.3% [-5.3, +12.9] | +0.001273 [-0.001165, +0.01853] | undecided |
| 2024 | spread_mr_fhs_mad20_f1.0 against B1 | 250 | +31.7% [-69.8, +114.2] | +0.01074 [+0.001404, +0.1392] | gain (was undecided) |
| 2024 | spread_mr_fhs_mad20_f1.0 against B2 | 250 | -3.5% [-29.6, +6.9] | -0.0007886 [-0.00629, +0.0007688] | undecided |
| 2024 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 250 | +3.8% [-3.9, +17.0] | +0.0009159 [-6.678e-05, +0.0182] | undecided |
| 2024 | spread_mr_fhs_mad40_f0.5 against B1 | 250 | +30.7% [+10.2, +117.7] | +0.01039 [+0.0001219, +0.1186] | gain |
| 2024 | spread_mr_fhs_mad40_f0.5 against B2 | 250 | -5.1% [-24.1, +17.3] | -0.001135 [-0.003147, +0.001404] | undecided |
| 2024 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 250 | +2.4% [-10.5, +9.3] | +0.0005696 [-0.001438, +0.009405] | undecided |
| 2024 | spread_mr_fhs_sd20_f0.5 against B1 | 250 | +24.5% [+8.2, +58.1] | +0.008278 [-0.00107, +0.07288] | undecided (was gain) |
| 2024 | spread_mr_fhs_sd20_f0.5 against B2 | 250 | -14.5% [-66.6, +28.3] | -0.003247 [-0.009099, +0.001536] | undecided |
| 2024 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 250 | -6.4% [-48.4, +12.0] | -0.001542 [-0.005688, +0.003724] | undecided |
| 2024 | spread_mr_level10 against B1 | 250 | +29.0% [-197.9, +117.1] | +0.009821 [+0.0006607, +0.142] | gain (was undecided) |
| 2024 | spread_mr_level10 against B2 | 250 | -7.6% [-27.6, +0.6] | -0.001705 [-0.04875, -9.817e-05] | loss (was undecided) |

### grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2024 | spread_mr_fhs_mad10_f0.5 against B1 | 250 | +25.8% [+19.4, +36.4] | +0.4155 [+0.208, +1.019] | gain |
| 2024 | spread_mr_fhs_mad10_f0.5 against B2 | 250 | +14.1% [+2.7, +24.0] | +0.1967 [+0.03203, +0.4067] | gain |
| 2024 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 250 | +7.1% [+1.3, +16.4] | +0.09201 [+0.009462, +0.3383] | gain |
| 2024 | spread_mr_fhs_mad20_f0.25 against B1 | 250 | +23.3% [+14.4, +37.6] | +0.3755 [+0.1473, +1.03] | gain |
| 2024 | spread_mr_fhs_mad20_f0.25 against B2 | 250 | +11.2% [+0.1, +20.2] | +0.1568 [-0.001694, +0.3593] | undecided (was gain) |
| 2024 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 250 | +4.0% [-6.0, +16.0] | +0.05209 [-0.05826, +0.2903] | undecided |
| 2024 | spread_mr_fhs_mad20_f0.5 against B1 | 250 | +25.3% [+18.7, +35.6] | +0.4088 [+0.2053, +0.9608] | gain |
| 2024 | spread_mr_fhs_mad20_f0.5 against B2 | 250 | +13.6% [+2.5, +23.0] | +0.19 [+0.03133, +0.3803] | gain |
| 2024 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 250 | +6.6% [+1.9, +12.5] | +0.08535 [+0.01429, +0.2602] | gain |
| 2024 | spread_mr_fhs_mad20_f1.0 against B1 | 250 | +22.9% [+16.3, +31.8] | +0.37 [+0.196, +0.808] | gain |
| 2024 | spread_mr_fhs_mad20_f1.0 against B2 | 250 | +10.8% [-1.8, +22.2] | +0.1513 [-0.01166, +0.3374] | undecided |
| 2024 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 250 | +3.6% [+1.9, +6.7] | +0.04656 [+0.01633, +0.1371] | gain |
| 2024 | spread_mr_fhs_mad40_f0.5 against B1 | 250 | +23.8% [+16.9, +35.0] | +0.3833 [+0.1848, +0.9413] | gain |
| 2024 | spread_mr_fhs_mad40_f0.5 against B2 | 250 | +11.8% [-0.3, +21.9] | +0.1646 [-0.002131, +0.3586] | undecided |
| 2024 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 250 | +4.6% [-0.4, +11.0] | +0.05989 [-0.005785, +0.2207] | undecided |
| 2024 | spread_mr_fhs_sd20_f0.5 against B1 | 250 | +22.7% [+16.3, +32.9] | +0.366 [+0.1751, +0.9018] | gain |
| 2024 | spread_mr_fhs_sd20_f0.5 against B2 | 250 | +10.6% [-2.2, +21.0] | +0.1472 [-0.02382, +0.3515] | undecided |
| 2024 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 250 | +3.3% [-4.1, +10.6] | +0.04255 [-0.03847, +0.1884] | undecided |
| 2024 | spread_mr_level10 against B1 | 250 | +20.1% [+12.8, +29.4] | +0.3234 [+0.1654, +0.6962] | gain |
| 2024 | spread_mr_level10 against B2 | 250 | +7.5% [-6.6, +20.3] | +0.1047 [-0.06932, +0.2969] | undecided |

### brier_0, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2025-26 | spread_mr_fhs_mad10_f0.5 against B1 | 249 | +25.5% [+17.4, +34.8] | +0.02772 [+0.01127, +0.05393] | gain |
| 2025-26 | spread_mr_fhs_mad10_f0.5 against B2 | 249 | +60.3% [+23.1, +88.4] | +0.123 [+0.006207, +0.3564] | gain |
| 2025-26 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 249 | -14.5% [-47.4, +2.3] | -0.0103 [-0.02162, +3.359e-05] | undecided |
| 2025-26 | spread_mr_fhs_mad20_f0.25 against B1 | 249 | +21.0% [+9.8, +32.9] | +0.0228 [+0.003942, +0.05313] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.25 against B2 | 249 | +57.8% [+21.1, +86.4] | +0.1181 [+0.002479, +0.3518] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 249 | -21.5% [-64.0, +0.5] | -0.01522 [-0.02729, -0.002089] | loss (was undecided) |
| 2025-26 | spread_mr_fhs_mad20_f0.5 against B1 | 249 | +26.7% [+17.5, +38.7] | +0.02907 [+0.01242, +0.05804] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.5 against B2 | 249 | +60.9% [+25.0, +88.7] | +0.1243 [+0.009587, +0.3589] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 249 | -12.6% [-41.6, +2.2] | -0.008945 [-0.01869, +0.0002832] | undecided |
| 2025-26 | spread_mr_fhs_mad20_f1.0 against B1 | 249 | +30.5% [+19.6, +43.8] | +0.03316 [+0.01724, +0.06128] | gain |
| 2025-26 | spread_mr_fhs_mad20_f1.0 against B2 | 249 | +62.9% [+26.6, +90.7] | +0.1284 [+0.01398, +0.3651] | gain |
| 2025-26 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 249 | -6.9% [-25.8, +2.2] | -0.004864 [-0.01234, +0.0009788] | undecided |
| 2025-26 | spread_mr_fhs_mad40_f0.5 against B1 | 249 | +29.6% [+19.3, +43.4] | +0.03217 [+0.01435, +0.06213] | gain |
| 2025-26 | spread_mr_fhs_mad40_f0.5 against B2 | 249 | +62.4% [+27.6, +89.5] | +0.1274 [+0.01287, +0.3609] | gain |
| 2025-26 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 249 | -8.3% [-30.9, +4.8] | -0.005848 [-0.01418, +0.003574] | undecided |
| 2025-26 | spread_mr_fhs_sd20_f0.5 against B1 | 249 | +29.6% [+18.6, +41.4] | +0.03217 [+0.01475, +0.06176] | gain |
| 2025-26 | spread_mr_fhs_sd20_f0.5 against B2 | 249 | +62.4% [+26.4, +89.6] | +0.1274 [+0.01198, +0.3619] | gain |
| 2025-26 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 249 | -8.3% [-29.8, +3.9] | -0.005852 [-0.01353, +0.003279] | undecided |
| 2025-26 | spread_mr_level10 against B1 | 249 | +34.9% [+19.1, +52.8] | +0.03802 [+0.02146, +0.06638] | gain |
| 2025-26 | spread_mr_level10 against B2 | 249 | +65.3% [+26.3, +94.0] | +0.1333 [+0.01584, +0.3722] | gain |

### brier_5, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2025-26 | spread_mr_fhs_mad10_f0.5 against B1 | 249 | +25.2% [+13.6, +34.2] | +0.02826 [+0.008422, +0.06374] | gain |
| 2025-26 | spread_mr_fhs_mad10_f0.5 against B2 | 249 | +17.2% [-17.6, +49.1] | +0.01734 [-0.01384, +0.1031] | undecided |
| 2025-26 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 249 | +11.8% [-4.6, +21.3] | +0.0112 [-0.00519, +0.04319] | undecided |
| 2025-26 | spread_mr_fhs_mad20_f0.25 against B1 | 249 | +25.3% [+13.7, +35.7] | +0.02828 [+0.00669, +0.06795] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.25 against B2 | 249 | +17.2% [-17.6, +48.9] | +0.01737 [-0.01464, +0.1069] | undecided |
| 2025-26 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 249 | +11.8% [-5.1, +21.8] | +0.01123 [-0.006385, +0.04519] | undecided |
| 2025-26 | spread_mr_fhs_mad20_f0.5 against B1 | 249 | +28.9% [+15.0, +41.1] | +0.03237 [+0.01146, +0.07178] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.5 against B2 | 249 | +21.2% [-9.9, +48.7] | +0.02145 [-0.008903, +0.1031] | undecided |
| 2025-26 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 249 | +16.1% [+6.8, +22.4] | +0.01531 [+6.823e-05, +0.04588] | gain |
| 2025-26 | spread_mr_fhs_mad20_f1.0 against B1 | 249 | +28.4% [+11.0, +42.6] | +0.03175 [+0.0114, +0.07026] | gain |
| 2025-26 | spread_mr_fhs_mad20_f1.0 against B2 | 249 | +20.6% [-9.3, +46.4] | +0.02084 [-0.007541, +0.09394] | undecided |
| 2025-26 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 249 | +15.5% [+9.3, +20.4] | +0.01469 [+0.001919, +0.04016] | gain |
| 2025-26 | spread_mr_fhs_mad40_f0.5 against B1 | 249 | +29.0% [+14.7, +43.0] | +0.03248 [+0.01185, +0.07254] | gain |
| 2025-26 | spread_mr_fhs_mad40_f0.5 against B2 | 249 | +21.3% [-10.9, +49.0] | +0.02156 [-0.008744, +0.1005] | undecided |
| 2025-26 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 249 | +16.3% [+8.7, +21.9] | +0.01542 [+0.001043, +0.04337] | gain |
| 2025-26 | spread_mr_fhs_sd20_f0.5 against B1 | 249 | +28.7% [+15.5, +39.9] | +0.03206 [+0.01163, +0.06987] | gain |
| 2025-26 | spread_mr_fhs_sd20_f0.5 against B2 | 249 | +20.9% [-10.7, +50.3] | +0.02115 [-0.009227, +0.1059] | undecided |
| 2025-26 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 249 | +15.8% [+6.1, +22.5] | +0.01501 [+9.803e-05, +0.04805] | gain |
| 2025-26 | spread_mr_level10 against B1 | 249 | +15.2% [-11.5, +33.3] | +0.01705 [-0.002552, +0.04185] | undecided |
| 2025-26 | spread_mr_level10 against B2 | 249 | +6.1% [-28.7, +36.3] | +0.00614 [-0.01884, +0.05] | undecided |

### grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2025-26 | spread_mr_fhs_mad10_f0.5 against B1 | 249 | +20.8% [+13.0, +28.0] | +0.6977 [+0.3564, +1.156] | gain |
| 2025-26 | spread_mr_fhs_mad10_f0.5 against B2 | 249 | +29.6% [+3.6, +51.4] | +1.116 [+0.02916, +2.961] | gain |
| 2025-26 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 249 | +4.1% [-0.9, +8.4] | +0.1124 [-0.01557, +0.267] | undecided |
| 2025-26 | spread_mr_fhs_mad20_f0.25 against B1 | 249 | +20.6% [+13.2, +28.0] | +0.6923 [+0.3479, +1.17] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.25 against B2 | 249 | +29.4% [+4.4, +51.6] | +1.111 [+0.05258, +3.027] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 249 | +3.9% [-1.2, +8.5] | +0.107 [-0.02774, +0.276] | undecided |
| 2025-26 | spread_mr_fhs_mad20_f0.5 against B1 | 249 | +23.4% [+16.6, +30.3] | +0.7857 [+0.4465, +1.261] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.5 against B2 | 249 | +31.9% [+8.0, +52.1] | +1.204 [+0.1472, +3.065] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 249 | +7.2% [+4.0, +10.4] | +0.2003 [+0.09597, +0.3431] | gain |
| 2025-26 | spread_mr_fhs_mad20_f1.0 against B1 | 249 | +22.7% [+15.1, +30.0] | +0.7622 [+0.4141, +1.243] | gain |
| 2025-26 | spread_mr_fhs_mad20_f1.0 against B2 | 249 | +31.3% [+6.5, +51.3] | +1.181 [+0.1089, +2.988] | gain |
| 2025-26 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 249 | +6.4% [+3.9, +9.5] | +0.1768 [+0.09297, +0.32] | gain |
| 2025-26 | spread_mr_fhs_mad40_f0.5 against B1 | 249 | +23.4% [+17.0, +30.3] | +0.7849 [+0.4537, +1.27] | gain |
| 2025-26 | spread_mr_fhs_mad40_f0.5 against B2 | 249 | +31.9% [+8.0, +52.3] | +1.204 [+0.1428, +3.091] | gain |
| 2025-26 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 249 | +7.2% [+3.2, +10.6] | +0.1995 [+0.08028, +0.3475] | gain |
| 2025-26 | spread_mr_fhs_sd20_f0.5 against B1 | 249 | +24.3% [+17.4, +31.2] | +0.8147 [+0.4719, +1.303] | gain |
| 2025-26 | spread_mr_fhs_sd20_f0.5 against B2 | 249 | +32.7% [+9.2, +52.5] | +1.233 [+0.1725, +3.094] | gain |
| 2025-26 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 249 | +8.3% [+5.6, +11.3] | +0.2293 [+0.13, +0.3762] | gain |
| 2025-26 | spread_mr_level10 against B1 | 249 | +17.4% [+9.8, +25.0] | +0.5854 [+0.2747, +0.9843] | gain |
| 2025-26 | spread_mr_level10 against B2 | 249 | +26.6% [+1.0, +46.1] | +1.004 [-0.04731, +2.576] | undecided (was gain) |

### upper_tail_twcrps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2025-26 | spread_mr_fhs_mad10_f0.5 against B1 | 249 | +27.1% [+19.8, +35.1] | +0.4346 [+0.1026, +1.133] | gain |
| 2025-26 | spread_mr_fhs_mad10_f0.5 against B2 | 249 | +24.1% [+2.5, +47.9] | +0.3713 [-0.07231, +1.911] | undecided (was gain) |
| 2025-26 | spread_mr_fhs_mad10_f0.5 against spread_mr_level10 | 249 | -1.1% [-20.8, +12.4] | -0.0125 [-0.1633, +0.1987] | undecided |
| 2025-26 | spread_mr_fhs_mad20_f0.25 against B1 | 249 | +27.4% [+19.5, +35.7] | +0.439 [+0.08828, +1.149] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.25 against B2 | 249 | +24.4% [+3.2, +48.4] | +0.3757 [-0.07332, +2.052] | undecided (was gain) |
| 2025-26 | spread_mr_fhs_mad20_f0.25 against spread_mr_level10 | 249 | -0.7% [-18.1, +12.7] | -0.008129 [-0.1467, +0.2414] | undecided |
| 2025-26 | spread_mr_fhs_mad20_f0.5 against B1 | 249 | +32.3% [+26.1, +39.3] | +0.5183 [+0.178, +1.22] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.5 against B2 | 249 | +29.6% [+14.2, +49.4] | +0.455 [+0.0229, +2.123] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.5 against spread_mr_level10 | 249 | +6.2% [-3.0, +14.4] | +0.07122 [-0.03985, +0.3159] | undecided |
| 2025-26 | spread_mr_fhs_mad20_f1.0 against B1 | 249 | +33.6% [+26.5, +41.1] | +0.5385 [+0.2062, +1.23] | gain |
| 2025-26 | spread_mr_fhs_mad20_f1.0 against B2 | 249 | +30.9% [+17.8, +47.9] | +0.4752 [+0.05639, +2.062] | gain |
| 2025-26 | spread_mr_fhs_mad20_f1.0 against spread_mr_level10 | 249 | +7.9% [+2.2, +13.4] | +0.09143 [-0.001402, +0.3072] | undecided (was gain) |
| 2025-26 | spread_mr_fhs_mad40_f0.5 against B1 | 249 | +33.6% [+26.7, +41.2] | +0.5383 [+0.186, +1.249] | gain |
| 2025-26 | spread_mr_fhs_mad40_f0.5 against B2 | 249 | +30.9% [+16.2, +49.4] | +0.475 [+0.03725, +2.118] | gain |
| 2025-26 | spread_mr_fhs_mad40_f0.5 against spread_mr_level10 | 249 | +7.9% [-0.9, +15.1] | +0.09119 [-0.02533, +0.3411] | undecided |
| 2025-26 | spread_mr_fhs_sd20_f0.5 against B1 | 249 | +33.5% [+27.3, +40.6] | +0.5363 [+0.1907, +1.269] | gain |
| 2025-26 | spread_mr_fhs_sd20_f0.5 against B2 | 249 | +30.7% [+16.2, +50.3] | +0.473 [+0.03729, +2.197] | gain |
| 2025-26 | spread_mr_fhs_sd20_f0.5 against spread_mr_level10 | 249 | +7.7% [-0.1, +15.7] | +0.08924 [-0.02059, +0.3752] | undecided |
| 2025-26 | spread_mr_level10 against B1 | 249 | +27.9% [+16.3, +37.6] | +0.4471 [+0.1854, +0.9972] | gain |
| 2025-26 | spread_mr_level10 against B2 | 249 | +24.9% [+14.3, +39.0] | +0.3838 [+0.05028, +1.593] | gain |

Nothing here is a verdict for a hypothesis. The originals stand.
