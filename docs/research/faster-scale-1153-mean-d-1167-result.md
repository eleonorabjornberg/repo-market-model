# Faster-reacting scale arms (#1153), read on the mean-d bound (#1167; H5 reporting, for #1009)

**Development data, not a verdict.** No re-scoring, no lockbox day, and no published declaration, record or decided value moves. Every figure is read from `docs/research/faster-scale-1153/result.json`, the record of the original page (`faster-scale-1153-result.md`, which stands), by `scripts/mean_d_reading_1167.py report`. Seed 1153, 10,000 draws, as on the original page.

## What changes and why

The original page read each row from the studentized skill interval. The skill interval and the interval on the mean difference d are built from different studentized draws, so their ends can fall on different sides of zero (#1009). The protocol's verdict reads the one-sided studentized bound on mean d (ruling 1/5). By Eleonora's ruling on #1009 this page shows both intervals for every paired row and reads the mean-d bound: **gain** when the lower bound of mean d is above zero, **loss** when its upper bound is below zero, **undecided** otherwise. The 90% two-sided interval on mean d is the pair of one-sided 95% bounds. d = S(benchmark) − S(candidate), positive favouring the candidate; skill is mean(d) / mean(S(benchmark)). A row the scorer left undefined carries no interval and is not read here.

**Caveat (Lens C of the five-lens review, #958).** The lag-10 HAC standard error that studentizes the mean-d bound is understated about 2× after 2020 (about 2.3× in 2021–23, 1.7× in 2024–26), and the bootstrap block of 10 days is an order of magnitude shorter than the autocorrelation of d. The bound is therefore optimistic: an interval that excludes zero here is narrower than it should be after 2020. A development reading on this page is evidence for a question, not a verdict.

Paired rows read: 1422. Rows whose reading changes: 156.

| reading on the skill interval -> reading on the mean-d bound | rows |
|---|---|
| gain -> undecided | 21 |
| loss -> undecided | 23 |
| undecided -> gain | 105 |
| undecided -> loss | 7 |

## Readings that change

| section | group | comparison | skill [90%] | mean d [90%] | on the skill interval | on the mean-d bound |
|---|---|---|---|---|---|---|
| upper_tail_twcrps, by lead | h=1 | spread_mr_fhs_mad20_f0.5 against B1p | +14.4% [-3.5, +26.6] | +0.1481 [+0.04685, +0.3104] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | spread_mr_fhs_mad20_f0.5 against B2 | +21.0% [-3.5, +36.5] | +0.2341 [+0.08723, +0.3954] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | v1_blend5_20 against B1p | +11.5% [-5.2, +22.8] | +0.1179 [+0.02111, +0.2525] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | v1_blend5_20 against B2 | +18.3% [-5.2, +34.2] | +0.2039 [+0.05284, +0.3641] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | v1_mad10 against B1p | +13.8% [-2.6, +24.9] | +0.1412 [+0.04649, +0.2858] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | v1_mad10 against B2 | +20.4% [-3.1, +36.2] | +0.2273 [+0.08238, +0.3919] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | v2_ewma_hl10 against B2 | +16.0% [-9.2, +33.4] | +0.1782 [+0.004668, +0.3495] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | v2_ewma_hl5_asym against B2 | +16.3% [-9.7, +33.6] | +0.1813 [+0.001914, +0.3514] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | v3_miss against B1p | +14.5% [-3.0, +26.7] | +0.1485 [+0.04866, +0.3123] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | v3_miss against B2 | +21.1% [-2.9, +36.4] | +0.2346 [+0.08945, +0.3967] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | v4_v3_miss_cal against B1p | +16.3% [-1.6, +27.2] | +0.1672 [+0.06967, +0.3217] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | v4_v3_miss_cal against B2 | +22.8% [-1.4, +37.7] | +0.2532 [+0.1143, +0.4172] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=2 | v1_blend5_20 against B1p | +10.2% [-1.8, +20.6] | +0.1055 [+0.02145, +0.2255] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=2 | v2_ewma_hl10 against B2 | +14.5% [-4.6, +30.3] | +0.1629 [+0.008378, +0.331] | undecided | **gain** |
| grid_crps, by lead | h=3 | v2_ewma_hl10 against B1p | +7.7% [-0.1, +14.5] | +0.1493 [+0.01915, +0.2889] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=3 | v1_mad5 against B2 | +12.3% [-2.0, +25.4] | +0.139 [+0.00317, +0.2937] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=3 | v2_ewma_hl10 against B2 | +14.2% [-2.7, +29.0] | +0.1614 [+0.01033, +0.3273] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=3 | v3_miss against spread_mr_fhs_mad20_f0.5 | -0.3% [-0.6, +0.0] | -0.002532 [-0.00503, -0.00026] | undecided | **loss** |
| upper_tail_twcrps, by lead | h=4 | v2_ewma_hl10 against B2 | +14.2% [-1.5, +27.8] | +0.1618 [+0.01412, +0.3232] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=4 | v3_miss against spread_mr_fhs_mad20_f0.5 | -0.3% [-0.7, +0.1] | -0.002626 [-0.005121, -0.0002037] | undecided | **loss** |
| upper_tail_twcrps, by lead | h=5 | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | -2.4% [-5.2, -0.1] | -0.02175 [-0.05008, +0.0002538] | loss | **undecided** |
| upper_tail_twcrps, by lead | h=5 | v2_ewma_hl10 against B2 | +13.5% [-2.0, +26.8] | +0.1546 [+0.0007959, +0.3154] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=5 | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | +1.4% [-0.0, +3.0] | +0.01281 [+0.003177, +0.02733] | undecided | **gain** |
| grid_crps, by all decision days | all decision days | v1_mad5 against B1p | +5.6% [-0.2, +10.8] | +0.107 [+0.0114, +0.2142] | undecided | **gain** |
| upper_tail_twcrps, by all decision days | all decision days | v1_mad5 against B1p | +7.2% [-1.6, +16.2] | +0.07664 [+0.001252, +0.1901] | undecided | **gain** |
| upper_tail_twcrps, by all decision days | all decision days | v1_mad5 against B2 | +12.7% [-2.2, +25.8] | +0.1433 [+0.006228, +0.295] | undecided | **gain** |
| upper_tail_twcrps, by all decision days | all decision days | v2_ewma_hl10 against B1p | +9.1% [-2.8, +21.3] | +0.09711 [+0.001985, +0.2373] | undecided | **gain** |
| upper_tail_twcrps, by all decision days | all decision days | v2_ewma_hl10 against B2 | +14.5% [-3.3, +29.4] | +0.1638 [+0.008562, +0.3303] | undecided | **gain** |
| grid_crps, by pressure-day type | month_end | v1_blend5_20 against B1p | +5.9% [+1.4, +10.1] | +0.1232 [-0.001456, +0.2569] | gain | **undecided** |
| grid_crps, by pressure-day type | month_end | v1_mad10 against B1p | +5.5% [+0.2, +10.5] | +0.1152 [-0.002713, +0.2528] | gain | **undecided** |
| scaled_grid_crps, by pressure-day type | month_end | v1_blend5_20 against B2 | +26.9% [-1.3, +52.1] | +0.5462 [+0.155, +1.333] | undecided | **gain** |
| scaled_grid_crps, by pressure-day type | month_end | v1_mad10 against B2 | +27.2% [-1.7, +52.6] | +0.5524 [+0.1551, +1.345] | undecided | **gain** |
| scaled_grid_crps, by pressure-day type | month_end | v1_mad10 against spread_mr_fhs_mad20_f0.5 | -1.8% [-3.2, -0.3] | -0.0261 [-0.05795, +0.0008259] | loss | **undecided** |
| scaled_grid_crps, by pressure-day type | month_end | v1_mad5 against B2 | +24.3% [-3.7, +49.9] | +0.4937 [+0.09059, +1.237] | undecided | **gain** |
| scaled_grid_crps, by pressure-day type | month_end | v2_ewma_hl3 against B1 | +10.3% [+1.9, +20.2] | +0.1746 [-0.001412, +0.5173] | gain | **undecided** |
| scaled_grid_crps, by pressure-day type | month_end | v2_ewma_hl3 against B2 | +25.3% [-0.3, +50.1] | +0.5131 [+0.1239, +1.248] | undecided | **gain** |
| scaled_grid_crps, by pressure-day type | month_end | v3_miss against spread_mr_fhs_mad20_f0.5 | +0.6% [-0.0, +1.8] | +0.009218 [+0.0005858, +0.02866] | undecided | **gain** |
| scaled_grid_crps, by pressure-day type | ordinary | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | -5.1% [-29.2, -0.0] | -0.06797 [-0.4024, +0.0005397] | loss | **undecided** |
| upper_tail_twcrps, by pressure-day type | ordinary | v1_blend5_20 against B2 | +14.2% [-0.0, +27.0] | +0.1092 [+0.00726, +0.2357] | undecided | **gain** |
| grid_crps, by pressure-day type | quarter_end | v4_v3_miss_cal against B2 | +25.0% [-21.7, +56.3] | +1.889 [+0.114, +4.909] | undecided | **gain** |
| scaled_grid_crps, by pressure-day type | quarter_end | v4_v3_miss_cal against B1 | +25.8% [+16.8, +32.7] | +0.3974 [-0.0005063, +2.149] | gain | **undecided** |
| scaled_grid_crps, by pressure-day type | quarter_end | v4_v3_miss_cal against B1p | +25.4% [+16.1, +32.6] | +0.3884 [-0.007405, +2.202] | gain | **undecided** |
| scaled_grid_crps, by pressure-day type | quarter_end | v4_v3_miss_cal against B2 | +35.6% [-7.9, +70.7] | +0.6307 [+0.3941, +0.838] | undecided | **gain** |
| scaled_grid_crps, by pressure-day type | quarter_end | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | +13.0% [+6.3, +19.4] | +0.1712 [-0.03369, +0.8656] | gain | **undecided** |
| grid_crps, by pressure-day type | tax_date | spread_mr_fhs_mad20_f0.5 against B1 | +6.8% [-5.8, +13.7] | +0.3754 [+0.05028, +1.086] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | spread_mr_fhs_mad20_f0.5 against B2 | +33.8% [-60.8, +58.2] | +2.617 [+1.41, +4.882] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | v1_blend5_20 against B1 | +6.9% [-6.6, +14.3] | +0.377 [+0.07484, +1.076] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | v1_blend5_20 against B2 | +33.8% [-64.8, +58.5] | +2.619 [+1.417, +4.787] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | v1_mad10 against B1 | +6.7% [-3.6, +13.6] | +0.3706 [+0.07019, +1.132] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | v1_mad10 against B2 | +33.8% [-61.7, +58.2] | +2.612 [+1.399, +4.827] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | v1_mad5 against B1 | +7.0% [-3.1, +13.4] | +0.3831 [+0.08847, +1.249] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | v1_mad5 against B2 | +33.9% [-61.3, +58.3] | +2.625 [+1.399, +4.861] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | v2_ewma_hl10 against B2 | +31.8% [-70.3, +57.6] | +2.458 [+1.396, +4.253] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | -3.1% [-5.1, -2.0] | -0.159 [-1.841, +0.01819] | loss | **undecided** |
| grid_crps, by pressure-day type | tax_date | v2_ewma_hl3 against B1 | +5.0% [-9.2, +13.4] | +0.2737 [+0.01964, +0.6215] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | v2_ewma_hl3 against B2 | +32.5% [-68.3, +57.9] | +2.515 [+1.395, +4.437] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | -2.0% [-3.6, -0.8] | -0.1017 [-0.9656, +0.01707] | loss | **undecided** |
| grid_crps, by pressure-day type | tax_date | v2_ewma_hl5 against B1 | +4.4% [-10.9, +13.4] | +0.2438 [+0.005053, +0.5662] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | v2_ewma_hl5 against B2 | +32.1% [-70.2, +57.8] | +2.485 [+1.392, +4.337] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | -2.6% [-4.7, -1.3] | -0.1316 [-1.534, +0.01979] | loss | **undecided** |
| grid_crps, by pressure-day type | tax_date | v2_ewma_hl5_asym against B2 | +32.2% [-67.1, +57.7] | +2.491 [+1.391, +4.381] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | -2.5% [-4.0, -1.1] | -0.1258 [-1.061, +0.01516] | loss | **undecided** |
| grid_crps, by pressure-day type | tax_date | v3_miss against B1 | +7.2% [-6.3, +14.4] | +0.3954 [+0.0762, +1.167] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | v3_miss against B2 | +34.1% [-63.0, +58.6] | +2.637 [+1.425, +4.9] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | v3_miss against spread_mr_fhs_mad20_f0.5 | +0.4% [-0.2, +1.3] | +0.01999 [+0.0097, +0.04788] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | v4_v3_miss_cal against B1p | +3.7% [+1.2, +6.9] | +0.2021 [-0.07475, +0.9976] | gain | **undecided** |
| grid_crps, by pressure-day type | tax_date | v4_v3_miss_cal against B2 | +32.6% [-71.7, +55.6] | +2.52 [+1.416, +4.556] | undecided | **gain** |
| scaled_grid_crps, by pressure-day type | tax_date | spread_mr_fhs_mad20_f0.5 against B1 | +8.4% [-5.5, +23.0] | +0.1582 [+0.0005159, +0.5241] | undecided | **gain** |
| scaled_grid_crps, by pressure-day type | tax_date | spread_mr_fhs_mad20_f0.5 against B1p | +5.4% [+1.8, +10.4] | +0.09823 [-0.008694, +0.359] | gain | **undecided** |
| scaled_grid_crps, by pressure-day type | tax_date | spread_mr_fhs_mad20_f0.5 against B2 | +34.2% [-47.1, +57.5] | +0.9007 [+0.6677, +1.219] | undecided | **gain** |
| scaled_grid_crps, by pressure-day type | tax_date | v1_blend5_20 against B1 | +8.4% [-5.3, +23.7] | +0.1584 [+0.01333, +0.5271] | undecided | **gain** |
| scaled_grid_crps, by pressure-day type | tax_date | v1_blend5_20 against B2 | +34.2% [-49.0, +57.8] | +0.9009 [+0.6719, +1.209] | undecided | **gain** |
| scaled_grid_crps, by pressure-day type | tax_date | v1_mad10 against B1 | +8.1% [-3.2, +23.1] | +0.1533 [+0.01136, +0.544] | undecided | **gain** |
| scaled_grid_crps, by pressure-day type | tax_date | v1_mad10 against B1p | +5.1% [+2.5, +9.3] | +0.09333 [-0.001649, +0.3632] | gain | **undecided** |
| scaled_grid_crps, by pressure-day type | tax_date | v1_mad10 against B2 | +34.0% [-43.2, +57.2] | +0.8958 [+0.6597, +1.205] | undecided | **gain** |
| scaled_grid_crps, by pressure-day type | tax_date | v1_mad5 against B1 | +8.4% [-1.7, +21.7] | +0.158 [+0.02043, +0.5566] | undecided | **gain** |
| scaled_grid_crps, by pressure-day type | tax_date | v1_mad5 against B2 | +34.2% [-45.5, +57.2] | +0.9005 [+0.6673, +1.213] | undecided | **gain** |
| scaled_grid_crps, by pressure-day type | tax_date | v2_ewma_hl10 against B2 | +32.4% [-51.4, +57.1] | +0.8535 [+0.6477, +1.121] | undecided | **gain** |
| scaled_grid_crps, by pressure-day type | tax_date | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | -2.7% [-5.0, -0.9] | -0.04723 [-0.3625, +0.002773] | loss | **undecided** |
| scaled_grid_crps, by pressure-day type | tax_date | v2_ewma_hl3 against B2 | +32.8% [-48.8, +56.9] | +0.865 [+0.6525, +1.137] | undecided | **gain** |
| scaled_grid_crps, by pressure-day type | tax_date | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | -2.1% [-3.0, -1.2] | -0.03571 [-0.1926, +0.002724] | loss | **undecided** |
| scaled_grid_crps, by pressure-day type | tax_date | v2_ewma_hl5 against B2 | +32.5% [-50.0, +57.0] | +0.8571 [+0.6485, +1.124] | undecided | **gain** |
| scaled_grid_crps, by pressure-day type | tax_date | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | -2.5% [-4.1, -1.4] | -0.04363 [-0.3067, +0.00128] | loss | **undecided** |
| scaled_grid_crps, by pressure-day type | tax_date | v2_ewma_hl5_asym against B2 | +32.6% [-47.7, +56.8] | +0.8588 [+0.6465, +1.137] | undecided | **gain** |
| scaled_grid_crps, by pressure-day type | tax_date | v3_miss against B1 | +8.7% [-5.4, +24.2] | +0.1654 [+0.01153, +0.5487] | undecided | **gain** |
| scaled_grid_crps, by pressure-day type | tax_date | v3_miss against B2 | +34.5% [-48.8, +57.9] | +0.9078 [+0.6745, +1.226] | undecided | **gain** |
| scaled_grid_crps, by pressure-day type | tax_date | v3_miss against spread_mr_fhs_mad20_f0.5 | +0.4% [-0.1, +1.1] | +0.007163 [+0.00302, +0.01343] | undecided | **gain** |
| scaled_grid_crps, by pressure-day type | tax_date | v4_v3_miss_cal against B1p | +4.4% [+1.0, +9.6] | +0.07974 [-0.02623, +0.3442] | gain | **undecided** |
| scaled_grid_crps, by pressure-day type | tax_date | v4_v3_miss_cal against B2 | +33.5% [-57.2, +56.5] | +0.8822 [+0.6477, +1.195] | undecided | **gain** |
| scaled_grid_crps, by pressure-day type | tax_date | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | -1.1% [-3.7, -0.1] | -0.01849 [-0.06169, +0.008647] | loss | **undecided** |
| grid_crps, by regime | 2018-19 | v1_blend5_20 against B1p | +8.4% [-1.5, +21.3] | +0.364 [+0.04777, +0.9664] | undecided | **gain** |
| grid_crps, by regime | 2018-19 | v1_blend5_20 against B2 | +11.4% [-2.4, +25.6] | +0.5104 [+0.008381, +1.069] | undecided | **gain** |
| grid_crps, by regime | 2018-19 | v1_mad10 against B2 | +12.3% [-1.2, +26.1] | +0.549 [+0.04126, +1.09] | undecided | **gain** |
| scaled_grid_crps, by regime | 2018-19 | v1_mad5 against B1p | -19.2% [-56.5, -2.6] | -0.4593 [-1.813, +0.03935] | loss | **undecided** |
| scaled_grid_crps, by regime | 2018-19 | v2_ewma_hl10 against B1 | +36.2% [+11.6, +139.6] | +1.747 [-0.1984, +25.58] | gain | **undecided** |
| scaled_grid_crps, by regime | 2018-19 | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | -28.4% [-80.0, +7.7] | -0.683 [-2.244, -0.1474] | undecided | **loss** |
| scaled_grid_crps, by regime | 2018-19 | v2_ewma_hl3 against B1p | -39.7% [-169.6, -5.5] | -0.9484 [-5.944, +0.08594] | loss | **undecided** |
| scaled_grid_crps, by regime | 2018-19 | v2_ewma_hl3 against B2 | -42.6% [-174.5, -4.0] | -0.9968 [-5.155, +0.1475] | loss | **undecided** |
| scaled_grid_crps, by regime | 2018-19 | v2_ewma_hl5 against B1 | +33.7% [+12.5, +101.0] | +1.629 [-0.07671, +21.96] | gain | **undecided** |
| scaled_grid_crps, by regime | 2018-19 | v2_ewma_hl5 against B1p | -34.1% [-124.8, -6.1] | -0.8144 [-4.275, +0.02542] | loss | **undecided** |
| scaled_grid_crps, by regime | 2018-19 | v2_ewma_hl5 against B2 | -36.8% [-133.3, -0.4] | -0.8629 [-3.539, +0.1333] | loss | **undecided** |
| scaled_grid_crps, by regime | 2018-19 | v2_ewma_hl5_asym against B1 | +34.3% [+14.0, +100.8] | +1.659 [-0.04832, +22.95] | gain | **undecided** |
| scaled_grid_crps, by regime | 2018-19 | v2_ewma_hl5_asym against B1p | -32.8% [-122.3, -5.6] | -0.7847 [-4.208, +0.03685] | loss | **undecided** |
| scaled_grid_crps, by regime | 2018-19 | v2_ewma_hl5_asym against B2 | -35.6% [-128.9, -0.2] | -0.8331 [-3.455, +0.1421] | loss | **undecided** |
| scaled_grid_crps, by regime | 2018-19 | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | +2.1% [-1.5, +6.4] | +0.05105 [+0.00482, +0.1363] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2018-19 | spread_mr_fhs_mad20_f0.5 against B1p | +11.5% [-0.4, +30.9] | +0.4411 [+0.08168, +1.361] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2018-19 | spread_mr_fhs_mad20_f0.5 against B2 | +11.0% [-1.3, +24.3] | +0.419 [+0.03207, +0.8766] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2018-19 | v1_blend5_20 against B1p | +8.6% [-2.1, +24.2] | +0.3296 [+0.01251, +1.017] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2018-19 | v1_mad10 against B1p | +9.6% [-0.3, +24.9] | +0.3666 [+0.05869, +1.033] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2018-19 | v3_miss against B1p | +11.5% [-0.3, +30.8] | +0.4413 [+0.08174, +1.361] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2018-19 | v3_miss against B2 | +11.0% [-1.1, +24.2] | +0.4192 [+0.03092, +0.8783] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | spread_mr_fhs_mad20_f0.5 against B2 | +58.1% [-23.6, +84.3] | +0.7083 [+0.358, +1.139] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | v1_blend5_20 against B2 | +58.6% [-14.8, +85.3] | +0.7146 [+0.3732, +1.14] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | v1_mad10 against B2 | +59.0% [-14.2, +85.4] | +0.7193 [+0.3767, +1.145] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | v1_mad5 against B2 | +53.9% [-16.8, +82.1] | +0.6576 [+0.315, +1.064] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | v2_ewma_hl10 against B2 | +61.3% [-54.0, +89.0] | +0.7472 [+0.4138, +1.15] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | v2_ewma_hl3 against B2 | +60.9% [-29.0, +89.4] | +0.7429 [+0.4136, +1.147] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | v2_ewma_hl5 against B2 | +61.6% [-33.5, +89.5] | +0.7515 [+0.4245, +1.156] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | v2_ewma_hl5_asym against B2 | +62.1% [-35.2, +89.9] | +0.7573 [+0.4309, +1.162] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | v3_miss against B2 | +57.9% [-22.7, +84.2] | +0.706 [+0.3555, +1.137] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | v3_miss against spread_mr_fhs_mad20_f0.5 | -0.4% [-1.2, +0.3] | -0.002282 [-0.005422, -0.0005673] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2020 | v4_v3_miss_cal against B2 | +56.6% [-30.1, +83.9] | +0.69 [+0.3353, +1.118] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | -3.6% [-6.8, -1.2] | -0.01825 [-0.05412, +0.00225] | loss | **undecided** |
| grid_crps, by regime | 2021-23 | v1_mad10 against B1 | +5.9% [-0.4, +10.9] | +0.04095 [+0.0005034, +0.0729] | undecided | **gain** |
| grid_crps, by regime | 2021-23 | v2_ewma_hl10 against B1 | +7.3% [-0.3, +13.3] | +0.05103 [+0.003498, +0.08757] | undecided | **gain** |
| grid_crps, by regime | 2021-23 | v2_ewma_hl3 against B1 | +6.8% [-0.5, +12.2] | +0.04715 [+0.001457, +0.08132] | undecided | **gain** |
| grid_crps, by regime | 2021-23 | v2_ewma_hl5 against B1 | +7.2% [-0.2, +12.8] | +0.05009 [+0.004435, +0.08524] | undecided | **gain** |
| scaled_grid_crps, by regime | 2021-23 | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | +1.6% [-0.1, +3.3] | +0.0131 [+0.000546, +0.02628] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | spread_mr_fhs_mad20_f0.5 against B2 | -156.2% [-792.6, -37.3] | -0.004779 [-0.04745, +0.0002712] | loss | **undecided** |
| upper_tail_twcrps, by regime | 2021-23 | v1_blend5_20 against B1 | +27.5% [-11.4, +57.1] | +0.002463 [+0.0007232, +0.004895] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | v1_blend5_20 against B2 | -111.7% [-433.5, -29.0] | -0.003417 [-0.0274, +0.0003189] | loss | **undecided** |
| upper_tail_twcrps, by regime | 2021-23 | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | +17.4% [+4.0, +51.2] | +0.001362 [-4.525e-05, +0.01286] | gain | **undecided** |
| upper_tail_twcrps, by regime | 2021-23 | v1_mad10 against B1 | +27.3% [-37.6, +57.7] | +0.002438 [+0.0002383, +0.00462] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | v1_mad10 against B2 | -112.5% [-621.9, -17.6] | -0.003442 [-0.03919, +0.0005596] | loss | **undecided** |
| upper_tail_twcrps, by regime | 2021-23 | v2_ewma_hl10 against B1 | +67.8% [-12.7, +84.4] | +0.006065 [+0.002707, +0.0162] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | v2_ewma_hl10 against B1p | +57.3% [-10.6, +71.8] | +0.003854 [+0.001546, +0.01244] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | +63.3% [-45.8, +78.1] | +0.004965 [+0.0005857, +0.0277] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | +42.4% [-6.5, +67.7] | +0.003322 [+8.999e-05, +0.01849] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | v2_ewma_hl5 against B1 | +58.7% [-1.3, +80.6] | +0.00525 [+0.002403, +0.01239] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | v2_ewma_hl5 against B1p | +45.2% [-3.1, +62.1] | +0.003039 [+0.001288, +0.008238] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | +52.9% [-12.9, +73.2] | +0.00415 [+0.0003931, +0.02243] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | v2_ewma_hl5_asym against B1 | +59.4% [-2.0, +81.4] | +0.005306 [+0.00226, +0.01247] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | v2_ewma_hl5_asym against B1p | +46.0% [-3.4, +64.6] | +0.003096 [+0.001157, +0.008526] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | +53.7% [-5.4, +78.4] | +0.004206 [+0.000262, +0.02263] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | v3_miss against spread_mr_fhs_mad20_f0.5 | -4.9% [-12.2, +0.5] | -0.0003863 [-0.0008024, -0.0001635] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2021-23 | v4_v3_miss_cal against B2 | -128.6% [-665.4, -25.0] | -0.003935 [-0.03783, +0.0001805] | loss | **undecided** |
| grid_crps, by regime | 2025-26 | v1_mad5 against B2 | +27.3% [+1.6, +48.9] | +1.03 [-0.03824, +2.807] | gain | **undecided** |
| scaled_grid_crps, by regime | 2025-26 | v1_mad10 against B1p | +11.3% [-0.5, +23.3] | +0.2855 [+0.02305, +0.7063] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2025-26 | v1_blend5_20 against B2 | +26.0% [+7.5, +48.6] | +0.4002 [-0.03516, +2.026] | gain | **undecided** |
| upper_tail_twcrps, by regime | 2025-26 | v1_mad10 against B2 | +24.1% [+1.5, +47.5] | +0.3713 [-0.08082, +1.858] | gain | **undecided** |
| upper_tail_twcrps, by regime | 2025-26 | v1_mad5 against B1p | +12.8% [+4.4, +21.7] | +0.1782 [-0.007126, +0.5372] | gain | **undecided** |
| upper_tail_twcrps, by regime | 2025-26 | v2_ewma_hl3 against B2 | +25.5% [+6.1, +49.6] | +0.3932 [-0.04217, +2.073] | gain | **undecided** |
| upper_tail_twcrps, by regime | 2025-26 | v2_ewma_hl5 against B2 | +27.5% [+9.3, +50.3] | +0.4226 [-0.01887, +2.133] | gain | **undecided** |
| upper_tail_twcrps, by regime | 2025-26 | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | -3.0% [-7.1, +0.2] | -0.03242 [-0.07559, -0.005828] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2025-26 | v2_ewma_hl5_asym against B2 | +27.4% [+9.2, +50.5] | +0.4224 [-0.01971, +2.15] | gain | **undecided** |
| upper_tail_twcrps, by regime | 2025-26 | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | -3.0% [-7.1, +0.4] | -0.03263 [-0.07326, -0.005309] | undecided | **loss** |

Every other paired row reads the same on both intervals.

## All paired rows

### grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=1 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +22.8% [+17.2, +34.1] | +0.4601 [+0.2503, +1.194] | gain |
| h=1 | spread_mr_fhs_mad20_f0.5 against B1p | 1855 | +9.8% [+1.9, +16.8] | +0.1687 [+0.0619, +0.3192] | gain |
| h=1 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +37.2% [+20.9, +46.8] | +0.923 [+0.6621, +1.228] | gain |
| h=1 | v1_blend5_20 against B1 | 1855 | +21.3% [+16.2, +31.9] | +0.4306 [+0.2358, +1.106] | gain |
| h=1 | v1_blend5_20 against B1p | 1855 | +8.1% [+0.0, +14.5] | +0.1392 [+0.03538, +0.2656] | gain |
| h=1 | v1_blend5_20 against B2 | 1855 | +36.0% [+19.1, +46.1] | +0.8935 [+0.6245, +1.2] | gain |
| h=1 | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 1855 | -1.9% [-3.7, -0.8] | -0.02949 [-0.06983, -0.009868] | loss |
| h=1 | v1_mad10 against B1 | 1855 | +22.5% [+17.3, +33.2] | +0.4546 [+0.2534, +1.163] | gain |
| h=1 | v1_mad10 against B1p | 1855 | +9.5% [+1.8, +16.0] | +0.1632 [+0.06207, +0.2996] | gain |
| h=1 | v1_mad10 against B2 | 1855 | +37.0% [+20.6, +47.0] | +0.9174 [+0.6508, +1.23] | gain |
| h=1 | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 1855 | -0.4% [-2.0, +0.9] | -0.005513 [-0.03137, +0.01331] | undecided |
| h=1 | v1_mad5 against B1 | 1855 | +16.6% [+11.3, +27.6] | +0.3359 [+0.1667, +0.9247] | gain |
| h=1 | v1_mad5 against B1p | 1855 | +2.6% [-5.5, +8.9] | +0.04449 [-0.06749, +0.1483] | undecided |
| h=1 | v1_mad5 against B2 | 1855 | +32.2% [+14.8, +43.2] | +0.7988 [+0.5138, +1.103] | gain |
| h=1 | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 1855 | -8.0% [-11.7, -5.6] | -0.1242 [-0.2342, -0.07506] | loss |
| h=1 | v2_ewma_hl10 against B1 | 1855 | +19.8% [+14.7, +29.7] | +0.3997 [+0.2187, +1.013] | gain |
| h=1 | v2_ewma_hl10 against B1p | 1855 | +6.3% [-3.0, +14.0] | +0.1083 [-0.01277, +0.2453] | undecided |
| h=1 | v2_ewma_hl10 against B2 | 1855 | +34.8% [+16.4, +45.8] | +0.8626 [+0.5733, +1.178] | gain |
| h=1 | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 1855 | -3.9% [-9.9, -1.1] | -0.06039 [-0.1771, -0.01126] | loss |
| h=1 | v2_ewma_hl3 against B1 | 1855 | +18.3% [+14.2, +25.5] | +0.3689 [+0.217, +0.8602] | gain |
| h=1 | v2_ewma_hl3 against B1p | 1855 | +4.5% [-8.6, +13.0] | +0.07751 [-0.08857, +0.2148] | undecided |
| h=1 | v2_ewma_hl3 against B2 | 1855 | +33.5% [+11.7, +45.3] | +0.8318 [+0.501, +1.144] | gain |
| h=1 | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 1855 | -5.9% [-19.5, -2.0] | -0.09117 [-0.3879, -0.0211] | loss |
| h=1 | v2_ewma_hl5 against B1 | 1855 | +19.3% [+14.8, +27.7] | +0.3901 [+0.2247, +0.9457] | gain |
| h=1 | v2_ewma_hl5 against B1p | 1855 | +5.7% [-5.3, +14.0] | +0.09872 [-0.04059, +0.2366] | undecided |
| h=1 | v2_ewma_hl5 against B2 | 1855 | +34.4% [+14.2, +45.8] | +0.853 [+0.5438, +1.168] | gain |
| h=1 | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 1855 | -4.5% [-15.2, -1.2] | -0.06997 [-0.2899, -0.01043] | loss |
| h=1 | v2_ewma_hl5_asym against B1 | 1855 | +20.2% [+15.6, +29.1] | +0.4066 [+0.2347, +1.006] | gain |
| h=1 | v2_ewma_hl5_asym against B1p | 1855 | +6.7% [-3.6, +14.7] | +0.1152 [-0.01372, +0.2546] | undecided |
| h=1 | v2_ewma_hl5_asym against B2 | 1855 | +35.1% [+15.7, +46.2] | +0.8695 [+0.5692, +1.185] | gain |
| h=1 | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 1855 | -3.4% [-12.5, -0.4] | -0.05347 [-0.2268, -0.001144] | loss |
| h=1 | v3_miss against B1 | 1855 | +23.0% [+17.4, +34.5] | +0.4641 [+0.2531, +1.213] | gain |
| h=1 | v3_miss against B1p | 1855 | +10.0% [+2.3, +17.0] | +0.1727 [+0.06732, +0.3247] | gain |
| h=1 | v3_miss against B2 | 1855 | +37.4% [+21.3, +46.9] | +0.927 [+0.6669, +1.233] | gain |
| h=1 | v3_miss against spread_mr_fhs_mad20_f0.5 | 1855 | +0.3% [-0.0, +0.5] | +0.004038 [-1.567e-05, +0.009027] | undecided |
| h=1 | v4_v3_miss_cal against B1 | 1855 | +23.5% [+17.8, +34.9] | +0.4745 [+0.2597, +1.222] | gain |
| h=1 | v4_v3_miss_cal against B1p | 1855 | +10.6% [+3.1, +17.0] | +0.1831 [+0.08077, +0.3268] | gain |
| h=1 | v4_v3_miss_cal against B2 | 1855 | +37.8% [+21.9, +47.2] | +0.9374 [+0.6831, +1.244] | gain |
| h=1 | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 1855 | +0.9% [+0.0, +2.0] | +0.0144 [+0.0001539, +0.03281] | gain |

### upper_tail_twcrps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=1 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +31.6% [+25.9, +40.5] | +0.4052 [+0.1959, +1.211] | gain |
| h=1 | spread_mr_fhs_mad20_f0.5 against B1p | 1855 | +14.4% [-3.5, +26.6] | +0.1481 [+0.04685, +0.3104] | gain (was undecided) |
| h=1 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +21.0% [-3.5, +36.5] | +0.2341 [+0.08723, +0.3954] | gain (was undecided) |
| h=1 | v1_blend5_20 against B1 | 1855 | +29.2% [+23.8, +38.6] | +0.375 [+0.1786, +1.147] | gain |
| h=1 | v1_blend5_20 against B1p | 1855 | +11.5% [-5.2, +22.8] | +0.1179 [+0.02111, +0.2525] | gain (was undecided) |
| h=1 | v1_blend5_20 against B2 | 1855 | +18.3% [-5.2, +34.2] | +0.2039 [+0.05284, +0.3641] | gain (was undecided) |
| h=1 | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 1855 | -3.4% [-5.6, -1.5] | -0.03023 [-0.05991, -0.0141] | loss |
| h=1 | v1_mad10 against B1 | 1855 | +31.0% [+25.6, +40.0] | +0.3984 [+0.1947, +1.182] | gain |
| h=1 | v1_mad10 against B1p | 1855 | +13.8% [-2.6, +24.9] | +0.1412 [+0.04649, +0.2858] | gain (was undecided) |
| h=1 | v1_mad10 against B2 | 1855 | +20.4% [-3.1, +36.2] | +0.2273 [+0.08238, +0.3919] | gain (was undecided) |
| h=1 | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 1855 | -0.8% [-3.6, +1.1] | -0.006885 [-0.0309, +0.00837] | undecided |
| h=1 | v1_mad5 against B1 | 1855 | +24.2% [+18.1, +35.8] | +0.3106 [+0.1327, +1.032] | gain |
| h=1 | v1_mad5 against B1p | 1855 | +5.2% [-9.0, +16.0] | +0.05345 [-0.04273, +0.1634] | undecided |
| h=1 | v1_mad5 against B2 | 1855 | +12.5% [-9.5, +28.7] | +0.1395 [-0.02677, +0.2979] | undecided |
| h=1 | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 1855 | -10.8% [-15.6, -5.2] | -0.09465 [-0.1704, -0.05617] | loss |
| h=1 | v2_ewma_hl10 against B1 | 1855 | +27.2% [+21.4, +36.8] | +0.3493 [+0.1646, +1.069] | gain |
| h=1 | v2_ewma_hl10 against B1p | 1855 | +9.0% [-8.5, +22.2] | +0.09216 [-0.01434, +0.2292] | undecided |
| h=1 | v2_ewma_hl10 against B2 | 1855 | +16.0% [-9.2, +33.4] | +0.1782 [+0.004668, +0.3495] | gain (was undecided) |
| h=1 | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 1855 | -6.4% [-13.5, -2.3] | -0.05594 [-0.1432, -0.01677] | loss |
| h=1 | v2_ewma_hl3 against B1 | 1855 | +25.1% [+19.9, +33.6] | +0.3217 [+0.1574, +0.9843] | gain |
| h=1 | v2_ewma_hl3 against B1p | 1855 | +6.3% [-13.7, +20.0] | +0.06452 [-0.0609, +0.1952] | undecided |
| h=1 | v2_ewma_hl3 against B2 | 1855 | +13.5% [-15.9, +31.1] | +0.1506 [-0.05836, +0.3191] | undecided |
| h=1 | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 1855 | -9.5% [-19.4, -4.7] | -0.08358 [-0.2589, -0.03157] | loss |
| h=1 | v2_ewma_hl5 against B1 | 1855 | +26.4% [+21.0, +35.3] | +0.3394 [+0.1654, +1.038] | gain |
| h=1 | v2_ewma_hl5 against B1p | 1855 | +8.0% [-10.8, +21.5] | +0.08223 [-0.03127, +0.2169] | undecided |
| h=1 | v2_ewma_hl5 against B2 | 1855 | +15.1% [-12.6, +32.8] | +0.1683 [-0.0227, +0.3379] | undecided |
| h=1 | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 1855 | -7.5% [-16.7, -3.1] | -0.06588 [-0.2075, -0.02045] | loss |
| h=1 | v2_ewma_hl5_asym against B1 | 1855 | +27.5% [+22.1, +36.9] | +0.3524 [+0.1721, +1.103] | gain |
| h=1 | v2_ewma_hl5_asym against B1p | 1855 | +9.3% [-8.3, +22.5] | +0.09529 [-0.00956, +0.2353] | undecided |
| h=1 | v2_ewma_hl5_asym against B2 | 1855 | +16.3% [-9.7, +33.6] | +0.1813 [+0.001914, +0.3514] | gain (was undecided) |
| h=1 | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 1855 | -6.0% [-14.0, -1.7] | -0.05281 [-0.1594, -0.01376] | loss |
| h=1 | v3_miss against B1 | 1855 | +31.6% [+25.9, +40.8] | +0.4057 [+0.1951, +1.221] | gain |
| h=1 | v3_miss against B1p | 1855 | +14.5% [-3.0, +26.7] | +0.1485 [+0.04866, +0.3123] | gain (was undecided) |
| h=1 | v3_miss against B2 | 1855 | +21.1% [-2.9, +36.4] | +0.2346 [+0.08945, +0.3967] | gain (was undecided) |
| h=1 | v3_miss against spread_mr_fhs_mad20_f0.5 | 1855 | +0.0% [-0.3, +0.4] | +0.0004208 [-0.001751, +0.004012] | undecided |
| h=1 | v4_v3_miss_cal against B1 | 1855 | +33.1% [+27.3, +41.6] | +0.4243 [+0.2081, +1.241] | gain |
| h=1 | v4_v3_miss_cal against B1p | 1855 | +16.3% [-1.6, +27.2] | +0.1672 [+0.06967, +0.3217] | gain (was undecided) |
| h=1 | v4_v3_miss_cal against B2 | 1855 | +22.8% [-1.4, +37.7] | +0.2532 [+0.1143, +0.4172] | gain (was undecided) |
| h=1 | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 1855 | +2.2% [+0.7, +4.1] | +0.01907 [+0.005641, +0.03971] | gain |

### grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=2 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +25.2% [+19.0, +40.5] | +0.5588 [+0.3166, +1.546] | gain |
| h=2 | spread_mr_fhs_mad20_f0.5 against B1p | 1855 | +10.1% [+4.1, +16.3] | +0.186 [+0.08911, +0.3286] | gain |
| h=2 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +33.9% [+22.0, +43.2] | +0.85 [+0.6009, +1.158] | gain |
| h=2 | v1_blend5_20 against B1 | 1855 | +23.9% [+18.2, +37.5] | +0.5285 [+0.3045, +1.432] | gain |
| h=2 | v1_blend5_20 against B1p | 1855 | +8.5% [+1.9, +14.2] | +0.1558 [+0.05794, +0.2734] | gain |
| h=2 | v1_blend5_20 against B2 | 1855 | +32.7% [+20.0, +42.6] | +0.8198 [+0.5662, +1.129] | gain |
| h=2 | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 1855 | -1.8% [-4.2, -0.6] | -0.03023 [-0.08066, -0.007314] | loss |
| h=2 | v1_mad10 against B1 | 1855 | +24.5% [+18.8, +38.7] | +0.5418 [+0.3139, +1.481] | gain |
| h=2 | v1_mad10 against B1p | 1855 | +9.2% [+3.1, +14.9] | +0.169 [+0.07541, +0.291] | gain |
| h=2 | v1_mad10 against B2 | 1855 | +33.2% [+20.9, +43.1] | +0.833 [+0.5778, +1.145] | gain |
| h=2 | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 1855 | -1.0% [-3.4, +0.4] | -0.01701 [-0.06022, +0.006819] | undecided |
| h=2 | v1_mad5 against B1 | 1855 | +19.3% [+13.7, +33.0] | +0.427 [+0.2265, +1.215] | gain |
| h=2 | v1_mad5 against B1p | 1855 | +2.9% [-4.6, +8.4] | +0.05426 [-0.06284, +0.1556] | undecided |
| h=2 | v1_mad5 against B2 | 1855 | +28.7% [+15.1, +39.4] | +0.7183 [+0.4467, +1.024] | gain |
| h=2 | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 1855 | -8.0% [-12.5, -5.4] | -0.1317 [-0.2588, -0.07758] | loss |
| h=2 | v2_ewma_hl10 against B1 | 1855 | +21.8% [+16.3, +34.4] | +0.483 [+0.2756, +1.295] | gain |
| h=2 | v2_ewma_hl10 against B1p | 1855 | +6.0% [-2.8, +13.1] | +0.1102 [-0.02089, +0.2391] | undecided |
| h=2 | v2_ewma_hl10 against B2 | 1855 | +30.9% [+16.5, +41.8] | +0.7743 [+0.4933, +1.092] | gain |
| h=2 | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 1855 | -4.6% [-11.4, -1.5] | -0.07577 [-0.2173, -0.01698] | loss |
| h=2 | v2_ewma_hl3 against B1 | 1855 | +19.9% [+15.3, +28.1] | +0.4398 [+0.2661, +1.023] | gain |
| h=2 | v2_ewma_hl3 against B1p | 1855 | +3.6% [-11.7, +11.7] | +0.06707 [-0.1532, +0.2061] | undecided |
| h=2 | v2_ewma_hl3 against B2 | 1855 | +29.2% [+10.5, +40.8] | +0.7311 [+0.4072, +1.044] | gain |
| h=2 | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 1855 | -7.2% [-26.2, -2.6] | -0.1189 [-0.5393, -0.02882] | loss |
| h=2 | v2_ewma_hl5 against B1 | 1855 | +21.1% [+16.2, +31.2] | +0.4676 [+0.278, +1.162] | gain |
| h=2 | v2_ewma_hl5 against B1p | 1855 | +5.1% [-6.8, +12.7] | +0.09485 [-0.07452, +0.2288] | undecided |
| h=2 | v2_ewma_hl5 against B2 | 1855 | +30.3% [+13.8, +41.5] | +0.7589 [+0.4571, +1.073] | gain |
| h=2 | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 1855 | -5.5% [-18.9, -1.6] | -0.09114 [-0.3775, -0.01607] | loss |
| h=2 | v2_ewma_hl5_asym against B1 | 1855 | +21.5% [+16.6, +31.5] | +0.4754 [+0.2846, +1.18] | gain |
| h=2 | v2_ewma_hl5_asym against B1p | 1855 | +5.6% [-6.2, +13.1] | +0.1026 [-0.06301, +0.2346] | undecided |
| h=2 | v2_ewma_hl5_asym against B2 | 1855 | +30.6% [+14.2, +41.8] | +0.7666 [+0.4672, +1.08] | gain |
| h=2 | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 1855 | -5.0% [-17.4, -1.2] | -0.08339 [-0.3464, -0.01123] | loss |
| h=2 | v3_miss against B1 | 1855 | +25.4% [+19.2, +40.6] | +0.5617 [+0.3198, +1.552] | gain |
| h=2 | v3_miss against B1p | 1855 | +10.3% [+4.2, +16.4] | +0.1889 [+0.09211, +0.331] | gain |
| h=2 | v3_miss against B2 | 1855 | +34.0% [+22.1, +43.4] | +0.853 [+0.6041, +1.162] | gain |
| h=2 | v3_miss against spread_mr_fhs_mad20_f0.5 | 1855 | +0.2% [-0.0, +0.4] | +0.002929 [-0.0004538, +0.006454] | undecided |
| h=2 | v4_v3_miss_cal against B1 | 1855 | +25.9% [+19.7, +40.8] | +0.5734 [+0.3266, +1.559] | gain |
| h=2 | v4_v3_miss_cal against B1p | 1855 | +10.9% [+5.0, +16.8] | +0.2006 [+0.1056, +0.3405] | gain |
| h=2 | v4_v3_miss_cal against B2 | 1855 | +34.5% [+22.7, +43.6] | +0.8647 [+0.6177, +1.173] | gain |
| h=2 | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 1855 | +0.9% [+0.3, +1.7] | +0.01463 [+0.003903, +0.02939] | gain |

### upper_tail_twcrps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=2 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +34.1% [+27.0, +48.7] | +0.4614 [+0.2199, +1.586] | gain |
| h=2 | spread_mr_fhs_mad20_f0.5 against B1p | 1855 | +13.4% [+1.1, +24.9] | +0.138 [+0.05029, +0.2906] | gain |
| h=2 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +20.8% [+4.7, +34.3] | +0.2338 [+0.1107, +0.3943] | gain |
| h=2 | v1_blend5_20 against B1 | 1855 | +31.7% [+25.0, +46.5] | +0.429 [+0.2009, +1.51] | gain |
| h=2 | v1_blend5_20 against B1p | 1855 | +10.2% [-1.8, +20.6] | +0.1055 [+0.02145, +0.2255] | gain (was undecided) |
| h=2 | v1_blend5_20 against B2 | 1855 | +17.9% [+1.4, +32.2] | +0.2014 [+0.07327, +0.3591] | gain |
| h=2 | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 1855 | -3.6% [-6.2, -1.7] | -0.03242 [-0.07018, -0.01307] | loss |
| h=2 | v1_mad10 against B1 | 1855 | +32.7% [+26.0, +47.2] | +0.4426 [+0.2119, +1.548] | gain |
| h=2 | v1_mad10 against B1p | 1855 | +11.6% [+0.3, +21.8] | +0.1191 [+0.03847, +0.244] | gain |
| h=2 | v1_mad10 against B2 | 1855 | +19.1% [+2.8, +33.4] | +0.215 [+0.08811, +0.3775] | gain |
| h=2 | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 1855 | -2.1% [-6.2, +0.3] | -0.01886 [-0.05914, +0.001147] | undecided |
| h=2 | v1_mad5 against B1 | 1855 | +26.6% [+19.4, +44.3] | +0.3601 [+0.1519, +1.392] | gain |
| h=2 | v1_mad5 against B1p | 1855 | +3.6% [-8.0, +12.7] | +0.03659 [-0.05481, +0.131] | undecided |
| h=2 | v1_mad5 against B2 | 1855 | +11.8% [-4.5, +25.9] | +0.1325 [-0.009126, +0.2872] | undecided |
| h=2 | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 1855 | -11.4% [-16.7, -5.9] | -0.1014 [-0.1891, -0.05814] | loss |
| h=2 | v2_ewma_hl10 against B1 | 1855 | +28.9% [+21.6, +43.3] | +0.3905 [+0.1801, +1.381] | gain |
| h=2 | v2_ewma_hl10 against B1p | 1855 | +6.5% [-8.4, +18.3] | +0.06704 [-0.04099, +0.1882] | undecided |
| h=2 | v2_ewma_hl10 against B2 | 1855 | +14.5% [-4.6, +30.3] | +0.1629 [+0.008378, +0.331] | gain (was undecided) |
| h=2 | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 1855 | -8.0% [-16.8, -3.6] | -0.07091 [-0.1848, -0.02103] | loss |
| h=2 | v2_ewma_hl3 against B1 | 1855 | +25.8% [+19.5, +37.3] | +0.3493 [+0.1664, +1.159] | gain |
| h=2 | v2_ewma_hl3 against B1p | 1855 | +2.5% [-19.9, +14.9] | +0.02582 [-0.1437, +0.1442] | undecided |
| h=2 | v2_ewma_hl3 against B2 | 1855 | +10.8% [-13.9, +27.0] | +0.1217 [-0.0804, +0.2864] | undecided |
| h=2 | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 1855 | -12.6% [-28.6, -6.8] | -0.1121 [-0.3858, -0.03961] | loss |
| h=2 | v2_ewma_hl5 against B1 | 1855 | +27.7% [+21.0, +40.4] | +0.3744 [+0.1785, +1.289] | gain |
| h=2 | v2_ewma_hl5 against B1p | 1855 | +4.9% [-13.7, +17.1] | +0.05096 [-0.08327, +0.1692] | undecided |
| h=2 | v2_ewma_hl5 against B2 | 1855 | +13.0% [-8.8, +29.2] | +0.1468 [-0.0282, +0.3134] | undecided |
| h=2 | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 1855 | -9.8% [-23.1, -4.7] | -0.08699 [-0.2868, -0.0258] | loss |
| h=2 | v2_ewma_hl5_asym against B1 | 1855 | +28.1% [+21.5, +40.9] | +0.3804 [+0.1829, +1.31] | gain |
| h=2 | v2_ewma_hl5_asym against B1p | 1855 | +5.5% [-12.8, +17.6] | +0.05695 [-0.07262, +0.174] | undecided |
| h=2 | v2_ewma_hl5_asym against B2 | 1855 | +13.6% [-8.0, +29.7] | +0.1528 [-0.01874, +0.3196] | undecided |
| h=2 | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 1855 | -9.1% [-21.4, -4.2] | -0.08101 [-0.2662, -0.02254] | loss |
| h=2 | v3_miss against B1 | 1855 | +34.1% [+27.0, +48.9] | +0.4617 [+0.2191, +1.589] | gain |
| h=2 | v3_miss against B1p | 1855 | +13.4% [+1.2, +24.9] | +0.1382 [+0.05087, +0.2916] | gain |
| h=2 | v3_miss against B2 | 1855 | +20.8% [+4.7, +34.3] | +0.2341 [+0.1109, +0.3946] | gain |
| h=2 | v3_miss against spread_mr_fhs_mad20_f0.5 | 1855 | +0.0% [-0.2, +0.3] | +0.0002577 [-0.001613, +0.002527] | undecided |
| h=2 | v4_v3_miss_cal against B1 | 1855 | +35.3% [+28.2, +49.0] | +0.4772 [+0.2296, +1.585] | gain |
| h=2 | v4_v3_miss_cal against B1p | 1855 | +14.9% [+2.7, +25.8] | +0.1538 [+0.06779, +0.3041] | gain |
| h=2 | v4_v3_miss_cal against B2 | 1855 | +22.2% [+5.9, +35.5] | +0.2496 [+0.13, +0.412] | gain |
| h=2 | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 1855 | +1.8% [+0.7, +3.4] | +0.01581 [+0.006517, +0.03363] | gain |

### grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=3 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +26.6% [+20.4, +42.0] | +0.6229 [+0.3661, +1.596] | gain |
| h=3 | spread_mr_fhs_mad20_f0.5 against B1p | 1855 | +11.8% [+6.7, +17.8] | +0.2299 [+0.1297, +0.3849] | gain |
| h=3 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +32.0% [+21.7, +41.2] | +0.8079 [+0.5598, +1.113] | gain |
| h=3 | v1_blend5_20 against B1 | 1855 | +25.4% [+19.8, +38.8] | +0.5932 [+0.3553, +1.479] | gain |
| h=3 | v1_blend5_20 against B1p | 1855 | +10.3% [+4.8, +15.8] | +0.2002 [+0.101, +0.329] | gain |
| h=3 | v1_blend5_20 against B2 | 1855 | +30.8% [+19.7, +40.6] | +0.7782 [+0.5259, +1.086] | gain |
| h=3 | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 1855 | -1.7% [-4.1, -0.4] | -0.02968 [-0.07957, -0.004728] | loss |
| h=3 | v1_mad10 against B1 | 1855 | +25.5% [+19.8, +40.0] | +0.597 [+0.355, +1.525] | gain |
| h=3 | v1_mad10 against B1p | 1855 | +10.5% [+5.4, +16.0] | +0.204 [+0.1087, +0.3351] | gain |
| h=3 | v1_mad10 against B2 | 1855 | +31.0% [+20.2, +40.7] | +0.782 [+0.5264, +1.093] | gain |
| h=3 | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 1855 | -1.5% [-4.1, +0.1] | -0.02588 [-0.07426, +0.001489] | undecided |
| h=3 | v1_mad5 against B1 | 1855 | +21.3% [+15.9, +34.3] | +0.4989 [+0.2866, +1.28] | gain |
| h=3 | v1_mad5 against B1p | 1855 | +5.4% [-1.1, +10.8] | +0.1059 [-0.003855, +0.216] | undecided |
| h=3 | v1_mad5 against B2 | 1855 | +27.1% [+14.9, +37.6] | +0.6839 [+0.4177, +0.9868] | gain |
| h=3 | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 1855 | -7.2% [-12.1, -4.6] | -0.124 [-0.2482, -0.06888] | loss |
| h=3 | v2_ewma_hl10 against B1 | 1855 | +23.2% [+17.6, +35.3] | +0.5423 [+0.3239, +1.33] | gain |
| h=3 | v2_ewma_hl10 against B1p | 1855 | +7.7% [-0.1, +14.5] | +0.1493 [+0.01915, +0.2889] | gain (was undecided) |
| h=3 | v2_ewma_hl10 against B2 | 1855 | +28.8% [+15.8, +39.6] | +0.7273 [+0.4484, +1.043] | gain |
| h=3 | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 1855 | -4.7% [-11.8, -1.4] | -0.08055 [-0.2314, -0.01804] | loss |
| h=3 | v2_ewma_hl3 against B1 | 1855 | +21.2% [+16.7, +28.8] | +0.4949 [+0.3141, +1.04] | gain |
| h=3 | v2_ewma_hl3 against B1p | 1855 | +5.2% [-8.6, +12.9] | +0.1019 [-0.1138, +0.2486] | undecided |
| h=3 | v2_ewma_hl3 against B2 | 1855 | +27.0% [+10.1, +38.4] | +0.6799 [+0.3593, +0.9895] | gain |
| h=3 | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 1855 | -7.5% [-28.6, -2.5] | -0.128 [-0.5907, -0.02914] | loss |
| h=3 | v2_ewma_hl5 against B1 | 1855 | +22.4% [+17.5, +31.9] | +0.5246 [+0.327, +1.177] | gain |
| h=3 | v2_ewma_hl5 against B1p | 1855 | +6.8% [-4.0, +14.1] | +0.1316 [-0.03619, +0.2729] | undecided |
| h=3 | v2_ewma_hl5 against B2 | 1855 | +28.1% [+13.1, +39.3] | +0.7096 [+0.4096, +1.023] | gain |
| h=3 | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 1855 | -5.7% [-20.3, -1.5] | -0.09826 [-0.4085, -0.01618] | loss |
| h=3 | v2_ewma_hl5_asym against B1 | 1855 | +22.6% [+17.7, +32.0] | +0.5274 [+0.3301, +1.186] | gain |
| h=3 | v2_ewma_hl5_asym against B1p | 1855 | +6.9% [-3.7, +14.1] | +0.1344 [-0.02966, +0.2741] | undecided |
| h=3 | v2_ewma_hl5_asym against B2 | 1855 | +28.2% [+13.2, +39.4] | +0.7125 [+0.4169, +1.024] | gain |
| h=3 | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 1855 | -5.6% [-19.2, -1.4] | -0.09544 [-0.3899, -0.01519] | loss |
| h=3 | v3_miss against B1 | 1855 | +26.7% [+20.5, +42.0] | +0.6243 [+0.3678, +1.599] | gain |
| h=3 | v3_miss against B1p | 1855 | +11.9% [+6.8, +17.9] | +0.2313 [+0.1319, +0.3863] | gain |
| h=3 | v3_miss against B2 | 1855 | +32.1% [+21.8, +41.2] | +0.8093 [+0.5616, +1.114] | gain |
| h=3 | v3_miss against spread_mr_fhs_mad20_f0.5 | 1855 | +0.1% [-0.1, +0.4] | +0.00142 [-0.002512, +0.006048] | undecided |
| h=3 | v4_v3_miss_cal against B1 | 1855 | +27.4% [+21.1, +42.2] | +0.6399 [+0.3786, +1.603] | gain |
| h=3 | v4_v3_miss_cal against B1p | 1855 | +12.7% [+7.6, +18.5] | +0.2468 [+0.147, +0.402] | gain |
| h=3 | v4_v3_miss_cal against B2 | 1855 | +32.7% [+22.3, +41.7] | +0.8249 [+0.5767, +1.131] | gain |
| h=3 | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 1855 | +1.0% [+0.3, +1.9] | +0.01698 [+0.006016, +0.03318] | gain |

### upper_tail_twcrps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=3 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +35.8% [+27.9, +51.7] | +0.5003 [+0.2471, +1.616] | gain |
| h=3 | spread_mr_fhs_mad20_f0.5 against B1p | 1855 | +16.0% [+5.9, +27.2] | +0.1705 [+0.08108, +0.3418] | gain |
| h=3 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +20.8% [+7.7, +33.4] | +0.2359 [+0.1162, +0.397] | gain |
| h=3 | v1_blend5_20 against B1 | 1855 | +33.5% [+26.1, +49.3] | +0.4675 [+0.2286, +1.54] | gain |
| h=3 | v1_blend5_20 against B1p | 1855 | +12.9% [+2.8, +22.8] | +0.1378 [+0.0554, +0.2705] | gain |
| h=3 | v1_blend5_20 against B2 | 1855 | +17.9% [+4.4, +31.1] | +0.2032 [+0.08021, +0.3613] | gain |
| h=3 | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 1855 | -3.6% [-6.4, -1.6] | -0.03274 [-0.07007, -0.01199] | loss |
| h=3 | v1_mad10 against B1 | 1855 | +33.8% [+26.3, +50.2] | +0.473 [+0.2304, +1.58] | gain |
| h=3 | v1_mad10 against B1p | 1855 | +13.4% [+4.5, +23.1] | +0.1432 [+0.0633, +0.2777] | gain |
| h=3 | v1_mad10 against B2 | 1855 | +18.4% [+5.4, +31.3] | +0.2086 [+0.08684, +0.3666] | gain |
| h=3 | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 1855 | -3.0% [-7.5, -0.2] | -0.02732 [-0.07239, -0.004046] | loss |
| h=3 | v1_mad5 against B1 | 1855 | +28.9% [+21.4, +46.2] | +0.4033 [+0.1837, +1.41] | gain |
| h=3 | v1_mad5 against B1p | 1855 | +6.9% [-3.3, +15.7] | +0.07356 [-0.01302, +0.1783] | undecided |
| h=3 | v1_mad5 against B2 | 1855 | +12.3% [-2.0, +25.4] | +0.139 [+0.00317, +0.2937] | gain (was undecided) |
| h=3 | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 1855 | -10.8% [-16.5, -6.0] | -0.09696 [-0.1834, -0.05238] | loss |
| h=3 | v2_ewma_hl10 against B1 | 1855 | +30.5% [+22.5, +45.6] | +0.4257 [+0.2065, +1.386] | gain |
| h=3 | v2_ewma_hl10 against B1p | 1855 | +9.0% [-4.4, +20.8] | +0.09596 [-0.009603, +0.2276] | undecided |
| h=3 | v2_ewma_hl10 against B2 | 1855 | +14.2% [-2.7, +29.0] | +0.1614 [+0.01033, +0.3273] | gain (was undecided) |
| h=3 | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 1855 | -8.3% [-17.7, -3.7] | -0.07456 [-0.1973, -0.02083] | loss |
| h=3 | v2_ewma_hl3 against B1 | 1855 | +27.3% [+20.6, +38.3] | +0.3816 [+0.1929, +1.133] | gain |
| h=3 | v2_ewma_hl3 against B1p | 1855 | +4.9% [-16.4, +16.9] | +0.05181 [-0.1116, +0.1758] | undecided |
| h=3 | v2_ewma_hl3 against B2 | 1855 | +10.3% [-12.9, +25.5] | +0.1172 [-0.0823, +0.2815] | undecided |
| h=3 | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 1855 | -13.2% [-33.3, -6.7] | -0.1187 [-0.4295, -0.03807] | loss |
| h=3 | v2_ewma_hl5 against B1 | 1855 | +29.1% [+22.0, +41.7] | +0.4073 [+0.2048, +1.265] | gain |
| h=3 | v2_ewma_hl5 against B1p | 1855 | +7.3% [-10.1, +19.2] | +0.07757 [-0.05363, +0.2037] | undecided |
| h=3 | v2_ewma_hl5 against B2 | 1855 | +12.6% [-7.6, +27.8] | +0.143 [-0.03077, +0.3068] | undecided |
| h=3 | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 1855 | -10.4% [-26.4, -4.7] | -0.09295 [-0.3159, -0.02494] | loss |
| h=3 | v2_ewma_hl5_asym against B1 | 1855 | +29.3% [+22.3, +41.8] | +0.4098 [+0.2069, +1.277] | gain |
| h=3 | v2_ewma_hl5_asym against B1p | 1855 | +7.5% [-9.8, +19.2] | +0.08009 [-0.04833, +0.2038] | undecided |
| h=3 | v2_ewma_hl5_asym against B2 | 1855 | +12.8% [-7.2, +28.0] | +0.1455 [-0.02486, +0.3091] | undecided |
| h=3 | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 1855 | -10.1% [-24.9, -4.6] | -0.09042 [-0.3039, -0.02351] | loss |
| h=3 | v3_miss against B1 | 1855 | +35.6% [+27.7, +51.9] | +0.4977 [+0.2447, +1.616] | gain |
| h=3 | v3_miss against B1p | 1855 | +15.7% [+5.8, +27.0] | +0.168 [+0.07911, +0.3394] | gain |
| h=3 | v3_miss against B2 | 1855 | +20.6% [+7.6, +33.1] | +0.2334 [+0.1136, +0.3938] | gain |
| h=3 | v3_miss against spread_mr_fhs_mad20_f0.5 | 1855 | -0.3% [-0.6, +0.0] | -0.002532 [-0.00503, -0.00026] | loss (was undecided) |
| h=3 | v4_v3_miss_cal against B1 | 1855 | +37.0% [+28.8, +52.1] | +0.5165 [+0.2578, +1.61] | gain |
| h=3 | v4_v3_miss_cal against B1p | 1855 | +17.5% [+7.2, +28.1] | +0.1867 [+0.09782, +0.3561] | gain |
| h=3 | v4_v3_miss_cal against B2 | 1855 | +22.2% [+8.9, +34.7] | +0.2521 [+0.1353, +0.4141] | gain |
| h=3 | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 1855 | +1.8% [+0.4, +3.6] | +0.0162 [+0.006173, +0.03476] | gain |

### grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=4 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +27.1% [+20.3, +44.2] | +0.6518 [+0.3801, +1.65] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5 against B1p | 1855 | +13.3% [+8.8, +19.1] | +0.2697 [+0.163, +0.4398] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +30.7% [+21.2, +39.7] | +0.7769 [+0.527, +1.076] | gain |
| h=4 | v1_blend5_20 against B1 | 1855 | +26.0% [+19.7, +41.6] | +0.6262 [+0.3696, +1.557] | gain |
| h=4 | v1_blend5_20 against B1p | 1855 | +12.0% [+7.8, +17.2] | +0.2441 [+0.1464, +0.3895] | gain |
| h=4 | v1_blend5_20 against B2 | 1855 | +29.7% [+19.7, +39.1] | +0.7513 [+0.4989, +1.054] | gain |
| h=4 | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 1855 | -1.5% [-3.2, -0.2] | -0.02561 [-0.06168, -0.002853] | loss |
| h=4 | v1_mad10 against B1 | 1855 | +25.9% [+19.6, +41.9] | +0.6248 [+0.3684, +1.571] | gain |
| h=4 | v1_mad10 against B1p | 1855 | +12.0% [+7.7, +17.2] | +0.2427 [+0.1436, +0.3896] | gain |
| h=4 | v1_mad10 against B2 | 1855 | +29.6% [+19.5, +39.2] | +0.7499 [+0.491, +1.055] | gain |
| h=4 | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 1855 | -1.5% [-4.2, +0.1] | -0.027 [-0.07673, +0.002103] | undecided |
| h=4 | v1_mad5 against B1 | 1855 | +22.1% [+16.1, +37.1] | +0.5326 [+0.3026, +1.368] | gain |
| h=4 | v1_mad5 against B1p | 1855 | +7.4% [+2.8, +12.4] | +0.1505 [+0.05805, +0.2715] | gain |
| h=4 | v1_mad5 against B2 | 1855 | +26.0% [+15.2, +35.9] | +0.6578 [+0.3969, +0.9562] | gain |
| h=4 | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 1855 | -6.8% [-10.9, -4.3] | -0.1192 [-0.2183, -0.0677] | loss |
| h=4 | v2_ewma_hl10 against B1 | 1855 | +23.6% [+17.7, +36.8] | +0.5689 [+0.3392, +1.367] | gain |
| h=4 | v2_ewma_hl10 against B1p | 1855 | +9.2% [+3.0, +15.6] | +0.1868 [+0.07173, +0.3341] | gain |
| h=4 | v2_ewma_hl10 against B2 | 1855 | +27.4% [+15.1, +37.9] | +0.6941 [+0.4156, +1.005] | gain |
| h=4 | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 1855 | -4.7% [-12.0, -1.3] | -0.08282 [-0.2398, -0.01635] | loss |
| h=4 | v2_ewma_hl3 against B1 | 1855 | +21.6% [+17.0, +29.6] | +0.5203 [+0.3305, +1.076] | gain |
| h=4 | v2_ewma_hl3 against B1p | 1855 | +6.8% [-3.7, +14.0] | +0.1382 [-0.03163, +0.2814] | undecided |
| h=4 | v2_ewma_hl3 against B2 | 1855 | +25.5% [+9.6, +36.7] | +0.6455 [+0.3233, +0.9515] | gain |
| h=4 | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 1855 | -7.5% [-30.6, -2.2] | -0.1314 [-0.618, -0.02768] | loss |
| h=4 | v2_ewma_hl5 against B1 | 1855 | +22.8% [+17.6, +33.0] | +0.5487 [+0.3419, +1.217] | gain |
| h=4 | v2_ewma_hl5 against B1p | 1855 | +8.2% [+0.1, +15.0] | +0.1666 [+0.02796, +0.3096] | gain |
| h=4 | v2_ewma_hl5 against B2 | 1855 | +26.6% [+12.5, +37.5] | +0.6739 [+0.3753, +0.9823] | gain |
| h=4 | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 1855 | -5.9% [-21.2, -1.4] | -0.1031 [-0.428, -0.01519] | loss |
| h=4 | v2_ewma_hl5_asym against B1 | 1855 | +22.7% [+17.7, +32.6] | +0.547 [+0.3422, +1.212] | gain |
| h=4 | v2_ewma_hl5_asym against B1p | 1855 | +8.1% [+0.0, +14.9] | +0.1649 [+0.02746, +0.3063] | gain |
| h=4 | v2_ewma_hl5_asym against B2 | 1855 | +26.5% [+12.4, +37.5] | +0.6722 [+0.3757, +0.9801] | gain |
| h=4 | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 1855 | -6.0% [-21.1, -1.5] | -0.1047 [-0.4259, -0.01696] | loss |
| h=4 | v3_miss against B1 | 1855 | +27.1% [+20.4, +44.4] | +0.6528 [+0.3805, +1.658] | gain |
| h=4 | v3_miss against B1p | 1855 | +13.4% [+9.0, +19.1] | +0.2707 [+0.1642, +0.4399] | gain |
| h=4 | v3_miss against B2 | 1855 | +30.7% [+21.2, +39.7] | +0.778 [+0.5275, +1.076] | gain |
| h=4 | v3_miss against spread_mr_fhs_mad20_f0.5 | 1855 | +0.1% [-0.2, +0.4] | +0.001071 [-0.003404, +0.006882] | undecided |
| h=4 | v4_v3_miss_cal against B1 | 1855 | +27.7% [+20.9, +44.5] | +0.6681 [+0.392, +1.664] | gain |
| h=4 | v4_v3_miss_cal against B1p | 1855 | +14.1% [+9.6, +19.7] | +0.286 [+0.1773, +0.456] | gain |
| h=4 | v4_v3_miss_cal against B2 | 1855 | +31.3% [+21.9, +40.1] | +0.7932 [+0.5438, +1.091] | gain |
| h=4 | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 1855 | +0.9% [+0.3, +1.8] | +0.0163 [+0.005604, +0.03176] | gain |

### upper_tail_twcrps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=4 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +36.6% [+27.4, +56.3] | +0.519 [+0.2512, +1.696] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5 against B1p | 1855 | +17.9% [+10.1, +28.6] | +0.1962 [+0.1001, +0.3832] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +20.9% [+9.8, +32.3] | +0.2384 [+0.1184, +0.3944] | gain |
| h=4 | v1_blend5_20 against B1 | 1855 | +34.8% [+25.9, +54.8] | +0.4931 [+0.236, +1.649] | gain |
| h=4 | v1_blend5_20 against B1p | 1855 | +15.5% [+8.4, +24.7] | +0.1703 [+0.08613, +0.3223] | gain |
| h=4 | v1_blend5_20 against B2 | 1855 | +18.7% [+7.4, +30.5] | +0.2125 [+0.09232, +0.3668] | gain |
| h=4 | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 1855 | -2.9% [-5.3, -1.0] | -0.02588 [-0.05253, -0.007625] | loss |
| h=4 | v1_mad10 against B1 | 1855 | +34.5% [+25.8, +54.5] | +0.489 [+0.2337, +1.646] | gain |
| h=4 | v1_mad10 against B1p | 1855 | +15.2% [+8.3, +24.5] | +0.1662 [+0.08224, +0.3159] | gain |
| h=4 | v1_mad10 against B2 | 1855 | +18.3% [+6.7, +29.9] | +0.2083 [+0.08373, +0.3613] | gain |
| h=4 | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 1855 | -3.3% [-7.6, -0.5] | -0.03003 [-0.0748, -0.005436] | loss |
| h=4 | v1_mad5 against B1 | 1855 | +30.4% [+21.8, +51.9] | +0.4314 [+0.1931, +1.53] | gain |
| h=4 | v1_mad5 against B1p | 1855 | +9.9% [+3.2, +18.2] | +0.1086 [+0.03428, +0.2298] | gain |
| h=4 | v1_mad5 against B2 | 1855 | +13.2% [+1.3, +24.9] | +0.1507 [+0.02388, +0.2996] | gain |
| h=4 | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 1855 | -9.7% [-15.1, -5.2] | -0.08764 [-0.1555, -0.04667] | loss |
| h=4 | v2_ewma_hl10 against B1 | 1855 | +31.2% [+22.3, +48.9] | +0.4425 [+0.213, +1.44] | gain |
| h=4 | v2_ewma_hl10 against B1p | 1855 | +10.9% [+0.8, +22.1] | +0.1197 [+0.02536, +0.2639] | gain |
| h=4 | v2_ewma_hl10 against B2 | 1855 | +14.2% [-1.5, +27.8] | +0.1618 [+0.01412, +0.3232] | gain (was undecided) |
| h=4 | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 1855 | -8.5% [-18.3, -3.7] | -0.07652 [-0.2077, -0.01909] | loss |
| h=4 | v2_ewma_hl3 against B1 | 1855 | +28.3% [+21.0, +40.7] | +0.4009 [+0.2044, +1.176] | gain |
| h=4 | v2_ewma_hl3 against B1p | 1855 | +7.1% [-8.4, +18.4] | +0.07807 [-0.04714, +0.2019] | undecided |
| h=4 | v2_ewma_hl3 against B2 | 1855 | +10.6% [-10.9, +24.8] | +0.1202 [-0.07438, +0.2797] | undecided |
| h=4 | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 1855 | -13.1% [-37.1, -6.1] | -0.1181 [-0.4546, -0.03261] | loss |
| h=4 | v2_ewma_hl5 against B1 | 1855 | +29.8% [+21.9, +44.5] | +0.4234 [+0.2133, +1.304] | gain |
| h=4 | v2_ewma_hl5 against B1p | 1855 | +9.2% [-3.6, +20.4] | +0.1006 [-0.005725, +0.2308] | undecided |
| h=4 | v2_ewma_hl5 against B2 | 1855 | +12.5% [-6.4, +26.7] | +0.1427 [-0.02959, +0.3013] | undecided |
| h=4 | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 1855 | -10.6% [-28.8, -4.6] | -0.09565 [-0.337, -0.02201] | loss |
| h=4 | v2_ewma_hl5_asym against B1 | 1855 | +29.8% [+22.0, +44.3] | +0.4226 [+0.2137, +1.3] | gain |
| h=4 | v2_ewma_hl5_asym against B1p | 1855 | +9.1% [-3.5, +20.2] | +0.09981 [-0.004132, +0.2272] | undecided |
| h=4 | v2_ewma_hl5_asym against B2 | 1855 | +12.5% [-6.3, +26.7] | +0.142 [-0.0268, +0.2996] | undecided |
| h=4 | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 1855 | -10.7% [-28.0, -4.8] | -0.09641 [-0.3343, -0.02304] | loss |
| h=4 | v3_miss against B1 | 1855 | +36.4% [+27.2, +56.5] | +0.5164 [+0.2475, +1.697] | gain |
| h=4 | v3_miss against B1p | 1855 | +17.7% [+10.0, +28.4] | +0.1936 [+0.09788, +0.3818] | gain |
| h=4 | v3_miss against B2 | 1855 | +20.7% [+9.7, +32.0] | +0.2357 [+0.1157, +0.3923] | gain |
| h=4 | v3_miss against spread_mr_fhs_mad20_f0.5 | 1855 | -0.3% [-0.7, +0.1] | -0.002626 [-0.005121, -0.0002037] | loss (was undecided) |
| h=4 | v4_v3_miss_cal against B1 | 1855 | +37.6% [+28.1, +56.5] | +0.5335 [+0.2615, +1.698] | gain |
| h=4 | v4_v3_miss_cal against B1p | 1855 | +19.2% [+11.0, +29.3] | +0.2107 [+0.1126, +0.3972] | gain |
| h=4 | v4_v3_miss_cal against B2 | 1855 | +22.2% [+10.7, +33.6] | +0.2528 [+0.1338, +0.4107] | gain |
| h=4 | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 1855 | +1.6% [+0.2, +3.4] | +0.01446 [+0.004811, +0.03165] | gain |

### grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=5 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +26.9% [+19.9, +45.0] | +0.6623 [+0.3878, +1.659] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5 against B1p | 1855 | +14.2% [+9.8, +19.9] | +0.2977 [+0.1875, +0.4735] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +29.3% [+20.1, +38.2] | +0.7456 [+0.4943, +1.044] | gain |
| h=5 | v1_blend5_20 against B1 | 1855 | +25.8% [+19.4, +42.0] | +0.6368 [+0.3786, +1.567] | gain |
| h=5 | v1_blend5_20 against B1p | 1855 | +13.0% [+8.9, +18.0] | +0.2722 [+0.1719, +0.4246] | gain |
| h=5 | v1_blend5_20 against B2 | 1855 | +28.3% [+18.6, +37.5] | +0.72 [+0.4641, +1.024] | gain |
| h=5 | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 1855 | -1.4% [-3.4, +0.1] | -0.02554 [-0.0657, +0.002164] | undecided |
| h=5 | v1_mad10 against B1 | 1855 | +25.8% [+19.2, +42.6] | +0.6355 [+0.3773, +1.591] | gain |
| h=5 | v1_mad10 against B1p | 1855 | +12.9% [+8.6, +18.3] | +0.2709 [+0.1678, +0.4296] | gain |
| h=5 | v1_mad10 against B2 | 1855 | +28.2% [+18.3, +37.5] | +0.7187 [+0.456, +1.022] | gain |
| h=5 | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 1855 | -1.5% [-4.0, +0.0] | -0.02686 [-0.0762, +0.001835] | undecided |
| h=5 | v1_mad5 against B1 | 1855 | +22.1% [+16.0, +37.1] | +0.5447 [+0.3135, +1.367] | gain |
| h=5 | v1_mad5 against B1p | 1855 | +8.6% [+4.1, +13.5] | +0.1801 [+0.08487, +0.3066] | gain |
| h=5 | v1_mad5 against B2 | 1855 | +24.6% [+13.9, +34.5] | +0.6279 [+0.3598, +0.9275] | gain |
| h=5 | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 1855 | -6.5% [-11.3, -3.6] | -0.1177 [-0.2234, -0.05972] | loss |
| h=5 | v2_ewma_hl10 against B1 | 1855 | +23.2% [+17.1, +37.2] | +0.5728 [+0.343, +1.378] | gain |
| h=5 | v2_ewma_hl10 against B1p | 1855 | +9.9% [+3.9, +16.3] | +0.2082 [+0.09096, +0.3614] | gain |
| h=5 | v2_ewma_hl10 against B2 | 1855 | +25.7% [+13.7, +36.2] | +0.656 [+0.3744, +0.9674] | gain |
| h=5 | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 1855 | -5.0% [-12.8, -1.5] | -0.08957 [-0.2593, -0.01882] | loss |
| h=5 | v2_ewma_hl3 against B1 | 1855 | +21.5% [+16.7, +29.8] | +0.53 [+0.3407, +1.089] | gain |
| h=5 | v2_ewma_hl3 against B1p | 1855 | +7.9% [-1.9, +14.8] | +0.1654 [-0.0005447, +0.313] | undecided |
| h=5 | v2_ewma_hl3 against B2 | 1855 | +24.1% [+8.5, +35.2] | +0.6132 [+0.2805, +0.9219] | gain |
| h=5 | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 1855 | -7.3% [-31.7, -2.0] | -0.1324 [-0.6352, -0.02465] | loss |
| h=5 | v2_ewma_hl5 against B1 | 1855 | +22.5% [+17.1, +33.3] | +0.5552 [+0.3479, +1.227] | gain |
| h=5 | v2_ewma_hl5 against B1p | 1855 | +9.1% [+1.3, +15.7] | +0.1906 [+0.05326, +0.3381] | gain |
| h=5 | v2_ewma_hl5 against B2 | 1855 | +25.0% [+11.2, +35.9] | +0.6384 [+0.3323, +0.9491] | gain |
| h=5 | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 1855 | -5.9% [-22.3, -1.4] | -0.1071 [-0.4454, -0.01565] | loss |
| h=5 | v2_ewma_hl5_asym against B1 | 1855 | +22.3% [+17.1, +32.8] | +0.5509 [+0.347, +1.213] | gain |
| h=5 | v2_ewma_hl5_asym against B1p | 1855 | +8.9% [+1.1, +15.5] | +0.1863 [+0.05019, +0.332] | gain |
| h=5 | v2_ewma_hl5_asym against B2 | 1855 | +24.9% [+11.0, +35.9] | +0.6342 [+0.3287, +0.9448] | gain |
| h=5 | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 1855 | -6.2% [-22.2, -1.6] | -0.1114 [-0.4534, -0.01877] | loss |
| h=5 | v3_miss against B1 | 1855 | +26.9% [+19.9, +45.1] | +0.6624 [+0.3884, +1.662] | gain |
| h=5 | v3_miss against B1p | 1855 | +14.2% [+9.9, +19.8] | +0.2978 [+0.188, +0.4731] | gain |
| h=5 | v3_miss against B2 | 1855 | +29.3% [+20.1, +38.2] | +0.7456 [+0.4948, +1.044] | gain |
| h=5 | v3_miss against spread_mr_fhs_mad20_f0.5 | 1855 | +0.0% [-0.2, +0.3] | +6.776e-05 [-0.00423, +0.005564] | undecided |
| h=5 | v4_v3_miss_cal against B1 | 1855 | +27.4% [+20.3, +45.3] | +0.6759 [+0.3979, +1.678] | gain |
| h=5 | v4_v3_miss_cal against B1p | 1855 | +14.8% [+10.4, +20.4] | +0.3113 [+0.1994, +0.4881] | gain |
| h=5 | v4_v3_miss_cal against B2 | 1855 | +29.8% [+20.6, +38.6] | +0.7591 [+0.5091, +1.059] | gain |
| h=5 | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 1855 | +0.8% [+0.1, +1.5] | +0.01358 [+0.00306, +0.0275] | gain |

### upper_tail_twcrps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=5 | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +35.8% [+25.3, +59.3] | +0.5088 [+0.2379, +1.724] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5 against B1p | 1855 | +17.3% [+9.7, +28.5] | +0.1906 [+0.09483, +0.3831] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +20.4% [+9.7, +31.1] | +0.2346 [+0.1151, +0.389] | gain |
| h=5 | v1_blend5_20 against B1 | 1855 | +34.2% [+24.4, +57.4] | +0.487 [+0.2271, +1.676] | gain |
| h=5 | v1_blend5_20 against B1p | 1855 | +15.3% [+8.6, +24.8] | +0.1689 [+0.08385, +0.3275] | gain |
| h=5 | v1_blend5_20 against B2 | 1855 | +18.5% [+7.4, +29.8] | +0.2128 [+0.09086, +0.3664] | gain |
| h=5 | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 1855 | -2.4% [-5.2, -0.1] | -0.02175 [-0.05008, +0.0002538] | undecided (was loss) |
| h=5 | v1_mad10 against B1 | 1855 | +33.6% [+23.6, +58.0] | +0.4782 [+0.2208, +1.708] | gain |
| h=5 | v1_mad10 against B1p | 1855 | +14.5% [+7.7, +24.4] | +0.16 [+0.07591, +0.32] | gain |
| h=5 | v1_mad10 against B2 | 1855 | +17.8% [+6.7, +28.7] | +0.204 [+0.07965, +0.3532] | gain |
| h=5 | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 1855 | -3.3% [-7.4, -0.7] | -0.03058 [-0.07308, -0.006592] | loss |
| h=5 | v1_mad5 against B1 | 1855 | +30.2% [+20.7, +54.3] | +0.4291 [+0.1889, +1.549] | gain |
| h=5 | v1_mad5 against B1p | 1855 | +10.1% [+3.6, +18.4] | +0.111 [+0.03607, +0.2388] | gain |
| h=5 | v1_mad5 against B2 | 1855 | +13.5% [+1.4, +24.8] | +0.155 [+0.02312, +0.3058] | gain |
| h=5 | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 1855 | -8.7% [-14.8, -3.7] | -0.07962 [-0.1483, -0.03505] | loss |
| h=5 | v2_ewma_hl10 against B1 | 1855 | +30.2% [+20.3, +51.0] | +0.4288 [+0.1977, +1.468] | gain |
| h=5 | v2_ewma_hl10 against B1p | 1855 | +10.0% [+0.6, +21.4] | +0.1107 [+0.01915, +0.2569] | gain |
| h=5 | v2_ewma_hl10 against B2 | 1855 | +13.5% [-2.0, +26.8] | +0.1546 [+0.0007959, +0.3154] | gain (was undecided) |
| h=5 | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 1855 | -8.8% [-19.6, -3.6] | -0.07993 [-0.2178, -0.01913] | loss |
| h=5 | v2_ewma_hl3 against B1 | 1855 | +27.7% [+19.7, +42.5] | +0.3943 [+0.1971, +1.211] | gain |
| h=5 | v2_ewma_hl3 against B1p | 1855 | +6.9% [-6.6, +17.9] | +0.07617 [-0.03965, +0.1989] | undecided |
| h=5 | v2_ewma_hl3 against B2 | 1855 | +10.5% [-11.1, +24.3] | +0.1201 [-0.08098, +0.28] | undecided |
| h=5 | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 1855 | -12.5% [-39.5, -5.1] | -0.1145 [-0.4497, -0.0272] | loss |
| h=5 | v2_ewma_hl5 against B1 | 1855 | +29.0% [+20.2, +46.4] | +0.4124 [+0.2018, +1.335] | gain |
| h=5 | v2_ewma_hl5 against B1p | 1855 | +8.5% [-2.7, +19.7] | +0.09428 [-0.006115, +0.2267] | undecided |
| h=5 | v2_ewma_hl5 against B2 | 1855 | +12.0% [-6.8, +25.6] | +0.1382 [-0.03957, +0.2973] | undecided |
| h=5 | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 1855 | -10.5% [-30.6, -4.2] | -0.09635 [-0.3448, -0.02055] | loss |
| h=5 | v2_ewma_hl5_asym against B1 | 1855 | +28.8% [+20.1, +46.0] | +0.4094 [+0.2009, +1.328] | gain |
| h=5 | v2_ewma_hl5_asym against B1p | 1855 | +8.3% [-2.9, +19.3] | +0.09131 [-0.007069, +0.2211] | undecided |
| h=5 | v2_ewma_hl5_asym against B2 | 1855 | +11.8% [-7.0, +25.4] | +0.1353 [-0.04146, +0.2941] | undecided |
| h=5 | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 1855 | -10.9% [-30.5, -4.5] | -0.09931 [-0.3475, -0.02225] | loss |
| h=5 | v3_miss against B1 | 1855 | +35.6% [+25.1, +59.5] | +0.5061 [+0.2353, +1.726] | gain |
| h=5 | v3_miss against B1p | 1855 | +17.0% [+9.5, +28.3] | +0.188 [+0.09171, +0.3793] | gain |
| h=5 | v3_miss against B2 | 1855 | +20.2% [+9.6, +30.9] | +0.2319 [+0.1124, +0.3868] | gain |
| h=5 | v3_miss against spread_mr_fhs_mad20_f0.5 | 1855 | -0.3% [-0.6, -0.0] | -0.002665 [-0.004995, -0.0006946] | loss |
| h=5 | v4_v3_miss_cal against B1 | 1855 | +36.7% [+25.9, +59.4] | +0.5216 [+0.2472, +1.741] | gain |
| h=5 | v4_v3_miss_cal against B1p | 1855 | +18.4% [+10.5, +29.1] | +0.2034 [+0.1057, +0.3964] | gain |
| h=5 | v4_v3_miss_cal against B2 | 1855 | +21.5% [+10.5, +32.4] | +0.2474 [+0.1302, +0.4017] | gain |
| h=5 | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 1855 | +1.4% [-0.0, +3.0] | +0.01281 [+0.003177, +0.02733] | gain (was undecided) |

### grid_crps, by all decision days

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| all decision days | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +25.8% [+19.6, +42.0] | +0.5912 [+0.3413, +1.558] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5 against B1p | 1855 | +11.9% [+7.0, +18.1] | +0.2304 [+0.1342, +0.393] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +32.6% [+21.9, +41.9] | +0.8207 [+0.5722, +1.126] | gain |
| all decision days | v1_blend5_20 against B1 | 1855 | +24.6% [+18.9, +39.2] | +0.5631 [+0.3303, +1.461] | gain |
| all decision days | v1_blend5_20 against B1p | 1855 | +10.5% [+5.5, +15.9] | +0.2023 [+0.1124, +0.3366] | gain |
| all decision days | v1_blend5_20 against B2 | 1855 | +31.5% [+20.2, +41.2] | +0.7926 [+0.5403, +1.101] | gain |
| all decision days | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 1855 | -1.7% [-3.7, -0.4] | -0.02811 [-0.07202, -0.00548] | loss |
| all decision days | v1_mad10 against B1 | 1855 | +24.9% [+19.1, +40.2] | +0.5707 [+0.3345, +1.494] | gain |
| all decision days | v1_mad10 against B1p | 1855 | +10.9% [+6.1, +16.5] | +0.2099 [+0.1194, +0.3496] | gain |
| all decision days | v1_mad10 against B2 | 1855 | +31.8% [+20.6, +41.6] | +0.8002 [+0.5451, +1.11] | gain |
| all decision days | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 1855 | -1.2% [-3.5, +0.3] | -0.02045 [-0.06285, +0.004374] | undecided |
| all decision days | v1_mad5 against B1 | 1855 | +20.4% [+14.8, +34.5] | +0.4678 [+0.261, +1.265] | gain |
| all decision days | v1_mad5 against B1p | 1855 | +5.6% [-0.2, +10.8] | +0.107 [+0.0114, +0.2142] | gain (was undecided) |
| all decision days | v1_mad5 against B2 | 1855 | +27.7% [+15.3, +38.1] | +0.6973 [+0.4301, +0.9997] | gain |
| all decision days | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 1855 | -7.3% [-11.8, -4.8] | -0.1233 [-0.2412, -0.07081] | loss |
| all decision days | v2_ewma_hl10 against B1 | 1855 | +22.4% [+16.9, +35.4] | +0.5133 [+0.3016, +1.314] | gain |
| all decision days | v2_ewma_hl10 against B1p | 1855 | +7.9% [+0.6, +14.6] | +0.1526 [+0.03523, +0.2929] | gain |
| all decision days | v2_ewma_hl10 against B2 | 1855 | +29.5% [+16.1, +40.3] | +0.7429 [+0.4628, +1.059] | gain |
| all decision days | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 1855 | -4.6% [-11.8, -1.4] | -0.07782 [-0.2302, -0.01637] | loss |
| all decision days | v2_ewma_hl3 against B1 | 1855 | +20.6% [+16.3, +28.6] | +0.4708 [+0.2951, +1.036] | gain |
| all decision days | v2_ewma_hl3 against B1p | 1855 | +5.7% [-6.7, +13.1] | +0.11 [-0.07465, +0.2494] | undecided |
| all decision days | v2_ewma_hl3 against B2 | 1855 | +27.8% [+10.4, +39.1] | +0.7003 [+0.3748, +1.009] | gain |
| all decision days | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 1855 | -7.1% [-28.8, -2.3] | -0.1204 [-0.5881, -0.02665] | loss |
| all decision days | v2_ewma_hl5 against B1 | 1855 | +21.7% [+16.9, +31.7] | +0.4972 [+0.3062, +1.174] | gain |
| all decision days | v2_ewma_hl5 against B1p | 1855 | +7.1% [-2.6, +14.2] | +0.1365 [-0.008747, +0.2741] | undecided |
| all decision days | v2_ewma_hl5 against B2 | 1855 | +28.9% [+13.4, +40.0] | +0.7268 [+0.4241, +1.038] | gain |
| all decision days | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 1855 | -5.5% [-20.4, -1.4] | -0.09392 [-0.4084, -0.01515] | loss |
| all decision days | v2_ewma_hl5_asym against B1 | 1855 | +21.9% [+17.2, +31.9] | +0.5015 [+0.3102, +1.184] | gain |
| all decision days | v2_ewma_hl5_asym against B1p | 1855 | +7.3% [-2.3, +14.3] | +0.1407 [-0.00135, +0.2763] | undecided |
| all decision days | v2_ewma_hl5_asym against B2 | 1855 | +29.0% [+13.7, +40.1] | +0.731 [+0.4327, +1.044] | gain |
| all decision days | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 1855 | -5.3% [-19.1, -1.3] | -0.08969 [-0.3861, -0.01359] | loss |
| all decision days | v3_miss against B1 | 1855 | +25.9% [+19.7, +42.2] | +0.5931 [+0.3426, +1.566] | gain |
| all decision days | v3_miss against B1p | 1855 | +12.0% [+7.2, +18.2] | +0.2323 [+0.1369, +0.3945] | gain |
| all decision days | v3_miss against B2 | 1855 | +32.7% [+22.0, +42.0] | +0.8226 [+0.5735, +1.128] | gain |
| all decision days | v3_miss against spread_mr_fhs_mad20_f0.5 | 1855 | +0.1% [-0.1, +0.3] | +0.001905 [-0.001468, +0.005781] | undecided |
| all decision days | v4_v3_miss_cal against B1 | 1855 | +26.5% [+20.2, +42.3] | +0.6063 [+0.3515, +1.572] | gain |
| all decision days | v4_v3_miss_cal against B1p | 1855 | +12.7% [+7.9, +18.6] | +0.2456 [+0.1494, +0.4065] | gain |
| all decision days | v4_v3_miss_cal against B2 | 1855 | +33.2% [+22.7, +42.3] | +0.8358 [+0.5892, +1.143] | gain |
| all decision days | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 1855 | +0.9% [+0.3, +1.7] | +0.01518 [+0.004576, +0.03122] | gain |

### scaled_grid_crps, by all decision days

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| all decision days | spread_mr_fhs_mad20_f0.5 against B1 | 1598 | +23.2% [+15.9, +41.0] | +0.4109 [+0.2339, +1.006] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5 against B1p | 1598 | +10.3% [+5.1, +16.8] | +0.1557 [+0.06865, +0.3052] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5 against B2 | 1598 | +28.4% [+19.4, +37.1] | +0.5408 [+0.3604, +0.7483] | gain |
| all decision days | v1_blend5_20 against B1 | 1598 | +22.3% [+15.6, +38.8] | +0.3954 [+0.2273, +0.9516] | gain |
| all decision days | v1_blend5_20 against B1p | 1598 | +9.2% [+3.8, +15.9] | +0.1401 [+0.05245, +0.2813] | gain |
| all decision days | v1_blend5_20 against B2 | 1598 | +27.6% [+17.9, +36.6] | +0.5252 [+0.3394, +0.7366] | gain |
| all decision days | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 1598 | -1.1% [-3.1, +0.2] | -0.01557 [-0.0438, +0.00217] | undecided |
| all decision days | v1_mad10 against B1 | 1598 | +22.3% [+15.1, +39.2] | +0.3941 [+0.2237, +0.9561] | gain |
| all decision days | v1_mad10 against B1p | 1598 | +9.2% [+3.7, +15.6] | +0.1388 [+0.05221, +0.2745] | gain |
| all decision days | v1_mad10 against B2 | 1598 | +27.6% [+17.6, +36.7] | +0.5239 [+0.3317, +0.7384] | gain |
| all decision days | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 1598 | -1.2% [-3.8, +0.2] | -0.01684 [-0.054, +0.003627] | undecided |
| all decision days | v1_mad5 against B1 | 1598 | +18.8% [+12.3, +34.1] | +0.3324 [+0.1806, +0.8324] | gain |
| all decision days | v1_mad5 against B1p | 1598 | +5.1% [-1.4, +11.9] | +0.0771 [-0.01453, +0.2018] | undecided |
| all decision days | v1_mad5 against B2 | 1598 | +24.3% [+13.5, +33.9] | +0.4622 [+0.2616, +0.6765] | gain |
| all decision days | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 1598 | -5.8% [-10.1, -3.3] | -0.07856 [-0.1527, -0.04209] | loss |
| all decision days | v2_ewma_hl10 against B1 | 1598 | +21.0% [+14.8, +36.1] | +0.372 [+0.2145, +0.885] | gain |
| all decision days | v2_ewma_hl10 against B1p | 1598 | +7.7% [+0.7, +15.1] | +0.1167 [+0.01501, +0.2609] | gain |
| all decision days | v2_ewma_hl10 against B2 | 1598 | +26.4% [+15.6, +36.0] | +0.5018 [+0.3006, +0.7213] | gain |
| all decision days | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 1598 | -2.9% [-10.9, +0.1] | -0.03896 [-0.1542, +0.001152] | undecided |
| all decision days | v2_ewma_hl3 against B1 | 1598 | +19.6% [+14.6, +29.7] | +0.3463 [+0.2135, +0.7255] | gain |
| all decision days | v2_ewma_hl3 against B1p | 1598 | +6.0% [-4.6, +13.8] | +0.09099 [-0.04663, +0.2259] | undecided |
| all decision days | v2_ewma_hl3 against B2 | 1598 | +25.0% [+11.6, +35.1] | +0.4761 [+0.2431, +0.6959] | gain |
| all decision days | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 1598 | -4.8% [-25.6, -0.2] | -0.06468 [-0.3754, -0.001446] | loss |
| all decision days | v2_ewma_hl5 against B1 | 1598 | +20.5% [+14.9, +32.9] | +0.3626 [+0.2184, +0.8042] | gain |
| all decision days | v2_ewma_hl5 against B1p | 1598 | +7.1% [-1.6, +14.6] | +0.1074 [-0.00984, +0.2457] | undecided |
| all decision days | v2_ewma_hl5 against B2 | 1598 | +25.9% [+13.8, +35.8] | +0.4925 [+0.2755, +0.7113] | gain |
| all decision days | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 1598 | -3.5% [-18.9, +0.2] | -0.04828 [-0.2695, +0.003922] | undecided |
| all decision days | v2_ewma_hl5_asym against B1 | 1598 | +20.7% [+15.1, +33.1] | +0.3661 [+0.2213, +0.8086] | gain |
| all decision days | v2_ewma_hl5_asym against B1p | 1598 | +7.3% [-1.2, +14.8] | +0.1109 [-0.005345, +0.2499] | undecided |
| all decision days | v2_ewma_hl5_asym against B2 | 1598 | +26.1% [+14.1, +35.8] | +0.496 [+0.2813, +0.7138] | gain |
| all decision days | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 1598 | -3.3% [-18.1, +0.4] | -0.0448 [-0.2602, +0.00587] | undecided |
| all decision days | v3_miss against B1 | 1598 | +23.2% [+15.9, +41.3] | +0.411 [+0.234, +1.007] | gain |
| all decision days | v3_miss against B1p | 1598 | +10.3% [+5.2, +16.7] | +0.1557 [+0.07012, +0.3023] | gain |
| all decision days | v3_miss against B2 | 1598 | +28.5% [+19.3, +37.1] | +0.5408 [+0.36, +0.7485] | gain |
| all decision days | v3_miss against spread_mr_fhs_mad20_f0.5 | 1598 | +0.0% [-0.4, +0.4] | +5.883e-05 [-0.005685, +0.00544] | undecided |
| all decision days | v4_v3_miss_cal against B1 | 1598 | +23.8% [+16.5, +41.6] | +0.421 [+0.2431, +1.022] | gain |
| all decision days | v4_v3_miss_cal against B1p | 1598 | +10.9% [+5.9, +17.4] | +0.1658 [+0.07987, +0.3144] | gain |
| all decision days | v4_v3_miss_cal against B2 | 1598 | +29.0% [+20.0, +37.6] | +0.5509 [+0.3702, +0.7595] | gain |
| all decision days | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 1598 | +0.7% [+0.2, +1.3] | +0.01011 [+0.002746, +0.01741] | gain |

### upper_tail_twcrps, by all decision days

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| all decision days | spread_mr_fhs_mad20_f0.5 against B1 | 1855 | +34.8% [+27.0, +51.7] | +0.4789 [+0.2306, +1.59] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5 against B1p | 1855 | +15.8% [+6.4, +27.5] | +0.1687 [+0.08159, +0.3546] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5 against B2 | 1855 | +20.8% [+6.9, +33.5] | +0.2354 [+0.1142, +0.396] | gain |
| all decision days | v1_blend5_20 against B1 | 1855 | +32.8% [+25.3, +49.7] | +0.4503 [+0.2148, +1.531] | gain |
| all decision days | v1_blend5_20 against B1p | 1855 | +13.2% [+4.2, +23.2] | +0.1401 [+0.06254, +0.2892] | gain |
| all decision days | v1_blend5_20 against B2 | 1855 | +18.3% [+4.2, +31.5] | +0.2068 [+0.08267, +0.3649] | gain |
| all decision days | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 1855 | -3.2% [-5.7, -1.3] | -0.0286 [-0.05998, -0.01021] | loss |
| all decision days | v1_mad10 against B1 | 1855 | +33.2% [+25.7, +50.4] | +0.4562 [+0.2178, +1.553] | gain |
| all decision days | v1_mad10 against B1p | 1855 | +13.7% [+5.3, +23.8] | +0.1459 [+0.0676, +0.2987] | gain |
| all decision days | v1_mad10 against B2 | 1855 | +18.8% [+4.8, +31.7] | +0.2126 [+0.08819, +0.371] | gain |
| all decision days | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 1855 | -2.5% [-6.3, -0.1] | -0.02273 [-0.06156, -0.002318] | loss |
| all decision days | v1_mad5 against B1 | 1855 | +28.1% [+20.6, +47.2] | +0.3869 [+0.1698, +1.417] | gain |
| all decision days | v1_mad5 against B1p | 1855 | +7.2% [-1.6, +16.2] | +0.07664 [+0.001252, +0.1901] | gain (was undecided) |
| all decision days | v1_mad5 against B2 | 1855 | +12.7% [-2.2, +25.8] | +0.1433 [+0.006228, +0.295] | gain (was undecided) |
| all decision days | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 1855 | -10.3% [-15.5, -5.7] | -0.09205 [-0.1701, -0.05087] | loss |
| all decision days | v2_ewma_hl10 against B1 | 1855 | +29.6% [+22.0, +45.5] | +0.4074 [+0.1935, +1.381] | gain |
| all decision days | v2_ewma_hl10 against B1p | 1855 | +9.1% [-2.8, +21.3] | +0.09711 [+0.001985, +0.2373] | gain (was undecided) |
| all decision days | v2_ewma_hl10 against B2 | 1855 | +14.5% [-3.3, +29.4] | +0.1638 [+0.008562, +0.3303] | gain (was undecided) |
| all decision days | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 1855 | -8.0% [-17.3, -3.5] | -0.07157 [-0.1932, -0.01944] | loss |
| all decision days | v2_ewma_hl3 against B1 | 1855 | +26.9% [+20.5, +38.8] | +0.3695 [+0.1836, +1.165] | gain |
| all decision days | v2_ewma_hl3 against B1p | 1855 | +5.6% [-12.5, +17.5] | +0.05928 [-0.07616, +0.1811] | undecided |
| all decision days | v2_ewma_hl3 against B2 | 1855 | +11.1% [-13.3, +26.4] | +0.126 [-0.07937, +0.2873] | undecided |
| all decision days | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 1855 | -12.2% [-31.4, -6.2] | -0.1094 [-0.4093, -0.03441] | loss |
| all decision days | v2_ewma_hl5 against B1 | 1855 | +28.5% [+21.5, +42.0] | +0.3914 [+0.1932, +1.277] | gain |
| all decision days | v2_ewma_hl5 against B1p | 1855 | +7.6% [-7.5, +19.6] | +0.08112 [-0.03123, +0.2101] | undecided |
| all decision days | v2_ewma_hl5 against B2 | 1855 | +13.1% [-8.2, +28.3] | +0.1478 [-0.03153, +0.3115] | undecided |
| all decision days | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 1855 | -9.8% [-25.2, -4.5] | -0.08756 [-0.3068, -0.02302] | loss |
| all decision days | v2_ewma_hl5_asym against B1 | 1855 | +28.7% [+21.9, +42.5] | +0.3949 [+0.1957, +1.296] | gain |
| all decision days | v2_ewma_hl5_asym against B1p | 1855 | +8.0% [-6.9, +19.7] | +0.08469 [-0.02419, +0.2121] | undecided |
| all decision days | v2_ewma_hl5_asym against B2 | 1855 | +13.4% [-7.5, +28.6] | +0.1514 [-0.02313, +0.3138] | undecided |
| all decision days | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 1855 | -9.4% [-23.7, -4.3] | -0.08399 [-0.29, -0.02212] | loss |
| all decision days | v3_miss against B1 | 1855 | +34.7% [+26.9, +51.9] | +0.4775 [+0.2287, +1.596] | gain |
| all decision days | v3_miss against B1p | 1855 | +15.7% [+6.4, +27.4] | +0.1673 [+0.08019, +0.3532] | gain |
| all decision days | v3_miss against B2 | 1855 | +20.7% [+6.9, +33.3] | +0.2339 [+0.1128, +0.3946] | gain |
| all decision days | v3_miss against spread_mr_fhs_mad20_f0.5 | 1855 | -0.2% [-0.4, +0.1] | -0.001429 [-0.00327, +0.0003658] | undecided |
| all decision days | v4_v3_miss_cal against B1 | 1855 | +36.0% [+28.1, +52.0] | +0.4946 [+0.2408, +1.603] | gain |
| all decision days | v4_v3_miss_cal against B1p | 1855 | +17.3% [+7.8, +27.9] | +0.1844 [+0.09677, +0.3656] | gain |
| all decision days | v4_v3_miss_cal against B2 | 1855 | +22.2% [+8.2, +34.9] | +0.251 [+0.133, +0.4131] | gain |
| all decision days | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 1855 | +1.7% [+0.5, +3.4] | +0.01567 [+0.005852, +0.03422] | gain |

### grid_crps, by pressure-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| month_end | spread_mr_fhs_mad20_f0.5 against B1 | 150 | +13.8% [+8.0, +20.1] | +0.3099 [+0.1168, +0.6568] | gain |
| month_end | spread_mr_fhs_mad20_f0.5 against B1p | 150 | +7.6% [+2.4, +13.0] | +0.1597 [+0.02063, +0.3404] | gain |
| month_end | spread_mr_fhs_mad20_f0.5 against B2 | 150 | +33.8% [+15.4, +51.2] | +0.9896 [+0.448, +2.021] | gain |
| month_end | v1_blend5_20 against B1 | 150 | +12.2% [+6.5, +20.0] | +0.2734 [+0.09713, +0.6396] | gain |
| month_end | v1_blend5_20 against B1p | 150 | +5.9% [+1.4, +10.1] | +0.1232 [-0.001456, +0.2569] | undecided (was gain) |
| month_end | v1_blend5_20 against B2 | 150 | +32.5% [+13.5, +50.2] | +0.9531 [+0.4109, +1.974] | gain |
| month_end | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 150 | -1.9% [-7.3, +0.1] | -0.03649 [-0.1576, +0.0002532] | undecided |
| month_end | v1_mad10 against B1 | 150 | +11.8% [+5.2, +19.8] | +0.2654 [+0.09945, +0.6195] | gain |
| month_end | v1_mad10 against B1p | 150 | +5.5% [+0.2, +10.5] | +0.1152 [-0.002713, +0.2528] | undecided (was gain) |
| month_end | v1_mad10 against B2 | 150 | +32.3% [+12.4, +50.8] | +0.9451 [+0.4072, +1.99] | gain |
| month_end | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 150 | -2.3% [-5.5, -0.3] | -0.04446 [-0.1483, -0.001511] | loss |
| month_end | v1_mad5 against B1 | 150 | +8.2% [+0.1, +16.6] | +0.1839 [+0.01257, +0.4847] | gain |
| month_end | v1_mad5 against B1p | 150 | +1.6% [-3.6, +6.3] | +0.03371 [-0.07128, +0.144] | undecided |
| month_end | v1_mad5 against B2 | 150 | +29.5% [+8.5, +47.7] | +0.8636 [+0.3246, +1.816] | gain |
| month_end | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 150 | -6.5% [-21.2, -2.0] | -0.1259 [-0.5287, -0.03555] | loss |
| month_end | v2_ewma_hl10 against B1 | 150 | +14.6% [+8.6, +20.8] | +0.3289 [+0.1323, +0.6845] | gain |
| month_end | v2_ewma_hl10 against B1p | 150 | +8.5% [+4.1, +12.6] | +0.1787 [+0.04287, +0.3352] | gain |
| month_end | v2_ewma_hl10 against B2 | 150 | +34.4% [+15.9, +50.7] | +1.009 [+0.4665, +2.001] | gain |
| month_end | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 150 | +1.0% [-8.6, +4.5] | +0.01907 [-0.1115, +0.08608] | undecided |
| month_end | v2_ewma_hl3 against B1 | 150 | +8.8% [-7.7, +17.7] | +0.1988 [-0.05599, +0.4633] | undecided |
| month_end | v2_ewma_hl3 against B1p | 150 | +2.3% [-10.7, +8.8] | +0.04859 [-0.1851, +0.1837] | undecided |
| month_end | v2_ewma_hl3 against B2 | 150 | +30.0% [+5.7, +48.2] | +0.8785 [+0.3104, +1.802] | gain |
| month_end | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 150 | -5.7% [-76.8, +1.3] | -0.1111 [-1.676, +0.03694] | undecided |
| month_end | v2_ewma_hl5 against B1 | 150 | +11.8% [+1.0, +19.6] | +0.2664 [+0.06213, +0.5794] | gain |
| month_end | v2_ewma_hl5 against B1p | 150 | +5.5% [-2.0, +10.7] | +0.1162 [-0.02682, +0.2498] | undecided |
| month_end | v2_ewma_hl5 against B2 | 150 | +32.3% [+10.8, +49.7] | +0.9461 [+0.3966, +1.911] | gain |
| month_end | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 150 | -2.2% [-39.6, +2.8] | -0.04346 [-0.6937, +0.05377] | undecided |
| month_end | v2_ewma_hl5_asym against B1 | 150 | +11.6% [+1.3, +19.5] | +0.2611 [+0.06296, +0.5761] | gain |
| month_end | v2_ewma_hl5_asym against B1p | 150 | +5.3% [-1.7, +10.3] | +0.1109 [-0.02523, +0.2418] | undecided |
| month_end | v2_ewma_hl5_asym against B2 | 150 | +32.1% [+10.8, +49.8] | +0.9408 [+0.3933, +1.912] | gain |
| month_end | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 150 | -2.5% [-36.8, +2.3] | -0.04877 [-0.6434, +0.04561] | undecided |
| month_end | v3_miss against B1 | 150 | +14.2% [+8.6, +20.2] | +0.3189 [+0.1244, +0.6622] | gain |
| month_end | v3_miss against B1p | 150 | +8.0% [+3.1, +13.2] | +0.1687 [+0.03099, +0.3502] | gain |
| month_end | v3_miss against B2 | 150 | +34.1% [+15.9, +51.1] | +0.9986 [+0.4571, +2.026] | gain |
| month_end | v3_miss against spread_mr_fhs_mad20_f0.5 | 150 | +0.5% [+0.1, +1.0] | +0.008994 [+0.001286, +0.02048] | gain |
| month_end | v4_v3_miss_cal against B1 | 150 | +13.2% [+6.8, +20.7] | +0.2972 [+0.09754, +0.6745] | gain |
| month_end | v4_v3_miss_cal against B1p | 150 | +7.0% [+2.4, +11.7] | +0.147 [+0.02005, +0.3139] | gain |
| month_end | v4_v3_miss_cal against B2 | 150 | +33.3% [+15.0, +50.7] | +0.9769 [+0.4462, +2.025] | gain |
| month_end | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 150 | -0.7% [-2.9, +0.8] | -0.01269 [-0.05281, +0.01646] | undecided |

### scaled_grid_crps, by pressure-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| month_end | spread_mr_fhs_mad20_f0.5 against B1 | 128 | +14.2% [+6.6, +24.2] | +0.24 [+0.05645, +0.6706] | gain |
| month_end | spread_mr_fhs_mad20_f0.5 against B1p | 128 | +2.3% [-10.2, +12.1] | +0.03341 [-0.1224, +0.1843] | undecided |
| month_end | spread_mr_fhs_mad20_f0.5 against B2 | 128 | +28.5% [+0.9, +53.3] | +0.5785 [+0.1956, +1.39] | gain |
| month_end | v1_blend5_20 against B1 | 128 | +12.3% [+5.3, +22.3] | +0.2078 [+0.04176, +0.6289] | gain |
| month_end | v1_blend5_20 against B1p | 128 | +0.1% [-11.9, +9.2] | +0.001161 [-0.1561, +0.1339] | undecided |
| month_end | v1_blend5_20 against B2 | 128 | +26.9% [-1.3, +52.1] | +0.5462 [+0.155, +1.333] | gain (was undecided) |
| month_end | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 128 | -2.2% [-5.5, -0.8] | -0.03225 [-0.09591, -0.007054] | loss |
| month_end | v1_mad10 against B1 | 128 | +12.7% [+5.2, +22.5] | +0.2139 [+0.04772, +0.6327] | gain |
| month_end | v1_mad10 against B1p | 128 | +0.5% [-12.5, +10.3] | +0.007306 [-0.1606, +0.148] | undecided |
| month_end | v1_mad10 against B2 | 128 | +27.2% [-1.7, +52.6] | +0.5524 [+0.1551, +1.345] | gain (was undecided) |
| month_end | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 128 | -1.8% [-3.2, -0.3] | -0.0261 [-0.05795, +0.0008259] | undecided (was loss) |
| month_end | v1_mad5 against B1 | 128 | +9.2% [+2.5, +18.6] | +0.1553 [+0.009549, +0.4901] | gain |
| month_end | v1_mad5 against B1p | 128 | -3.5% [-13.6, +4.9] | -0.05133 [-0.2025, +0.06475] | undecided |
| month_end | v1_mad5 against B2 | 128 | +24.3% [-3.7, +49.9] | +0.4937 [+0.09059, +1.237] | gain (was undecided) |
| month_end | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 128 | -5.8% [-15.4, -2.4] | -0.08474 [-0.2749, -0.02486] | loss |
| month_end | v2_ewma_hl10 against B1 | 128 | +14.3% [+7.2, +24.0] | +0.242 [+0.052, +0.7003] | gain |
| month_end | v2_ewma_hl10 against B1p | 128 | +2.4% [-8.9, +10.8] | +0.03538 [-0.111, +0.1694] | undecided |
| month_end | v2_ewma_hl10 against B2 | 128 | +28.6% [+3.6, +52.2] | +0.5804 [+0.2134, +1.354] | gain |
| month_end | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 128 | +0.1% [-6.2, +2.7] | +0.001977 [-0.07279, +0.03839] | undecided |
| month_end | v2_ewma_hl3 against B1 | 128 | +10.3% [+1.9, +20.2] | +0.1746 [-0.001412, +0.5173] | undecided (was gain) |
| month_end | v2_ewma_hl3 against B1p | 128 | -2.2% [-12.5, +6.7] | -0.03196 [-0.1822, +0.09387] | undecided |
| month_end | v2_ewma_hl3 against B2 | 128 | +25.3% [-0.3, +50.1] | +0.5131 [+0.1239, +1.248] | gain (was undecided) |
| month_end | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 128 | -4.5% [-41.7, +0.4] | -0.06537 [-0.6765, +0.008802] | undecided |
| month_end | v2_ewma_hl5 against B1 | 128 | +12.7% [+5.2, +22.5] | +0.2143 [+0.03159, +0.6229] | gain |
| month_end | v2_ewma_hl5 against B1p | 128 | +0.5% [-9.6, +9.0] | +0.007707 [-0.133, +0.1335] | undecided |
| month_end | v2_ewma_hl5 against B2 | 128 | +27.2% [+2.2, +51.1] | +0.5528 [+0.1782, +1.307] | gain |
| month_end | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 128 | -1.8% [-22.7, +1.8] | -0.0257 [-0.3019, +0.02636] | undecided |
| month_end | v2_ewma_hl5_asym against B1 | 128 | +12.6% [+5.2, +22.3] | +0.2128 [+0.02938, +0.6233] | gain |
| month_end | v2_ewma_hl5_asym against B1p | 128 | +0.4% [-9.7, +8.8] | +0.006168 [-0.1327, +0.1314] | undecided |
| month_end | v2_ewma_hl5_asym against B2 | 128 | +27.2% [+2.0, +51.1] | +0.5512 [+0.177, +1.312] | gain |
| month_end | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 128 | -1.9% [-19.4, +1.6] | -0.02724 [-0.2592, +0.02194] | undecided |
| month_end | v3_miss against B1 | 128 | +14.7% [+7.8, +23.9] | +0.2492 [+0.066, +0.6663] | gain |
| month_end | v3_miss against B1p | 128 | +2.9% [-8.8, +12.1] | +0.04263 [-0.1028, +0.1873] | undecided |
| month_end | v3_miss against B2 | 128 | +29.0% [+1.5, +53.1] | +0.5877 [+0.2083, +1.381] | gain |
| month_end | v3_miss against spread_mr_fhs_mad20_f0.5 | 128 | +0.6% [-0.0, +1.8] | +0.009218 [+0.0005858, +0.02866] | gain (was undecided) |
| month_end | v4_v3_miss_cal against B1 | 128 | +14.4% [+6.9, +25.3] | +0.2431 [+0.05274, +0.7113] | gain |
| month_end | v4_v3_miss_cal against B1p | 128 | +2.5% [-9.1, +12.0] | +0.03651 [-0.1062, +0.1882] | undecided |
| month_end | v4_v3_miss_cal against B2 | 128 | +28.7% [+2.1, +53.7] | +0.5816 [+0.2067, +1.415] | gain |
| month_end | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 128 | +0.2% [-1.4, +1.5] | +0.003103 [-0.01766, +0.02619] | undecided |

### grid_crps, by pressure-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| ordinary | spread_mr_fhs_mad20_f0.5 against B1 | 1590 | +30.9% [+20.8, +58.4] | +0.6284 [+0.3437, +1.702] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5 against B1p | 1590 | +14.0% [+8.3, +20.9] | +0.2277 [+0.1211, +0.4072] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5 against B2 | 1590 | +33.3% [+24.2, +42.1] | +0.6993 [+0.4636, +1.003] | gain |
| ordinary | v1_blend5_20 against B1 | 1590 | +29.3% [+20.1, +54.3] | +0.5951 [+0.3317, +1.582] | gain |
| ordinary | v1_blend5_20 against B1p | 1590 | +11.9% [+5.8, +18.2] | +0.1944 [+0.088, +0.3494] | gain |
| ordinary | v1_blend5_20 against B2 | 1590 | +31.7% [+21.7, +41.1] | +0.666 [+0.4214, +0.9696] | gain |
| ordinary | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 1590 | -2.4% [-5.6, -0.6] | -0.03333 [-0.08452, -0.007797] | loss |
| ordinary | v1_mad10 against B1 | 1590 | +29.9% [+20.7, +55.1] | +0.6079 [+0.3419, +1.607] | gain |
| ordinary | v1_mad10 against B1p | 1590 | +12.7% [+6.7, +19.2] | +0.2072 [+0.09928, +0.3676] | gain |
| ordinary | v1_mad10 against B2 | 1590 | +32.3% [+22.2, +41.7] | +0.6788 [+0.431, +0.9876] | gain |
| ordinary | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 1590 | -1.5% [-4.8, +0.5] | -0.02052 [-0.06983, +0.00702] | undecided |
| ordinary | v1_mad5 against B1 | 1590 | +24.3% [+15.7, +47.3] | +0.4929 [+0.2608, +1.375] | gain |
| ordinary | v1_mad5 against B1p | 1590 | +5.7% [-2.6, +12.2] | +0.09225 [-0.02743, +0.2187] | undecided |
| ordinary | v1_mad5 against B2 | 1590 | +26.8% [+14.9, +37.3] | +0.5639 [+0.3042, +0.8626] | gain |
| ordinary | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 1590 | -9.7% [-17.1, -6.0] | -0.1355 [-0.2687, -0.07759] | loss |
| ordinary | v2_ewma_hl10 against B1 | 1590 | +26.5% [+17.9, +47.8] | +0.5392 [+0.299, +1.408] | gain |
| ordinary | v2_ewma_hl10 against B1p | 1590 | +8.5% [-1.5, +16.6] | +0.1386 [-0.007977, +0.2993] | undecided |
| ordinary | v2_ewma_hl10 against B2 | 1590 | +29.0% [+16.1, +39.7] | +0.6102 [+0.3301, +0.9213] | gain |
| ordinary | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 1590 | -6.4% [-19.1, -1.5] | -0.08917 [-0.2864, -0.01924] | loss |
| ordinary | v2_ewma_hl3 against B1 | 1590 | +24.6% [+18.3, +38.2] | +0.4995 [+0.3012, +1.128] | gain |
| ordinary | v2_ewma_hl3 against B1p | 1590 | +6.1% [-11.6, +15.0] | +0.09884 [-0.1304, +0.2591] | undecided |
| ordinary | v2_ewma_hl3 against B2 | 1590 | +27.1% [+10.0, +38.3] | +0.5704 [+0.2402, +0.8763] | gain |
| ordinary | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 1590 | -9.2% [-40.3, -2.2] | -0.1289 [-0.6202, -0.02856] | loss |
| ordinary | v2_ewma_hl5 against B1 | 1590 | +25.9% [+18.6, +42.6] | +0.5254 [+0.3081, +1.263] | gain |
| ordinary | v2_ewma_hl5 against B1p | 1590 | +7.6% [-5.9, +16.1] | +0.1247 [-0.05978, +0.2831] | undecided |
| ordinary | v2_ewma_hl5 against B2 | 1590 | +28.4% [+13.4, +39.3] | +0.5963 [+0.2915, +0.9034] | gain |
| ordinary | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 1590 | -7.3% [-30.4, -1.4] | -0.103 [-0.4557, -0.01788] | loss |
| ordinary | v2_ewma_hl5_asym against B1 | 1590 | +26.1% [+19.0, +42.9] | +0.5306 [+0.3134, +1.274] | gain |
| ordinary | v2_ewma_hl5_asym against B1p | 1590 | +8.0% [-5.4, +16.3] | +0.13 [-0.05171, +0.2872] | undecided |
| ordinary | v2_ewma_hl5_asym against B2 | 1590 | +28.6% [+13.8, +39.4] | +0.6016 [+0.299, +0.9081] | gain |
| ordinary | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 1590 | -7.0% [-29.2, -1.2] | -0.09779 [-0.4422, -0.01447] | loss |
| ordinary | v3_miss against B1 | 1590 | +30.9% [+20.8, +58.6] | +0.6284 [+0.3437, +1.71] | gain |
| ordinary | v3_miss against B1p | 1590 | +14.0% [+8.4, +20.9] | +0.2277 [+0.1221, +0.4065] | gain |
| ordinary | v3_miss against B2 | 1590 | +33.3% [+24.2, +42.1] | +0.6993 [+0.4627, +1.002] | gain |
| ordinary | v3_miss against spread_mr_fhs_mad20_f0.5 | 1590 | +0.0% [-0.2, +0.2] | +3.77e-06 [-0.003364, +0.003473] | undecided |
| ordinary | v4_v3_miss_cal against B1 | 1590 | +31.6% [+21.5, +58.5] | +0.6423 [+0.3552, +1.721] | gain |
| ordinary | v4_v3_miss_cal against B1p | 1590 | +14.8% [+9.5, +21.5] | +0.2417 [+0.1367, +0.4194] | gain |
| ordinary | v4_v3_miss_cal against B2 | 1590 | +33.9% [+25.0, +42.7] | +0.7133 [+0.4777, +1.015] | gain |
| ordinary | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 1590 | +1.0% [+0.3, +1.6] | +0.01396 [+0.00517, +0.02283] | gain |

### scaled_grid_crps, by pressure-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| ordinary | spread_mr_fhs_mad20_f0.5 against B1 | 1371 | +25.1% [+16.5, +46.3] | +0.4471 [+0.2441, +1.074] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5 against B1p | 1371 | +11.3% [+5.9, +18.3] | +0.1702 [+0.07584, +0.3377] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5 against B2 | 1371 | +28.1% [+18.4, +37.4] | +0.5207 [+0.3302, +0.7361] | gain |
| ordinary | v1_blend5_20 against B1 | 1371 | +24.2% [+16.2, +43.8] | +0.4316 [+0.2395, +1.022] | gain |
| ordinary | v1_blend5_20 against B1p | 1371 | +10.3% [+4.4, +17.4] | +0.1547 [+0.0578, +0.3194] | gain |
| ordinary | v1_blend5_20 against B2 | 1371 | +27.2% [+17.2, +36.8] | +0.5052 [+0.3093, +0.7246] | gain |
| ordinary | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 1371 | -1.2% [-3.4, +0.3] | -0.01556 [-0.04598, +0.003331] | undecided |
| ordinary | v1_mad10 against B1 | 1371 | +24.1% [+15.9, +43.3] | +0.4299 [+0.2378, +1.014] | gain |
| ordinary | v1_mad10 against B1p | 1371 | +10.2% [+4.3, +17.0] | +0.153 [+0.05718, +0.3075] | gain |
| ordinary | v1_mad10 against B2 | 1371 | +27.1% [+16.6, +37.0] | +0.5035 [+0.3014, +0.7262] | gain |
| ordinary | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 1371 | -1.3% [-4.3, +0.4] | -0.01725 [-0.05909, +0.005256] | undecided |
| ordinary | v1_mad5 against B1 | 1371 | +20.4% [+12.9, +38.5] | +0.3632 [+0.1904, +0.9042] | gain |
| ordinary | v1_mad5 against B1p | 1371 | +5.7% [-1.3, +13.3] | +0.08631 [-0.01475, +0.2312] | undecided |
| ordinary | v1_mad5 against B2 | 1371 | +23.6% [+12.3, +33.7] | +0.4368 [+0.2304, +0.6592] | gain |
| ordinary | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 1371 | -6.3% [-11.5, -3.4] | -0.08391 [-0.1627, -0.04402] | loss |
| ordinary | v2_ewma_hl10 against B1 | 1371 | +22.6% [+15.2, +39.6] | +0.4032 [+0.2239, +0.9303] | gain |
| ordinary | v2_ewma_hl10 against B1p | 1371 | +8.4% [+0.5, +16.5] | +0.1263 [+0.01001, +0.2919] | gain |
| ordinary | v2_ewma_hl10 against B2 | 1371 | +25.7% [+14.4, +35.9] | +0.4768 [+0.2645, +0.7049] | gain |
| ordinary | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 1371 | -3.3% [-13.5, +0.1] | -0.04392 [-0.1836, +0.001908] | undecided |
| ordinary | v2_ewma_hl3 against B1 | 1371 | +21.3% [+15.5, +32.8] | +0.3792 [+0.2284, +0.7748] | gain |
| ordinary | v2_ewma_hl3 against B1p | 1371 | +6.8% [-5.3, +15.1] | +0.1023 [-0.05256, +0.2542] | undecided |
| ordinary | v2_ewma_hl3 against B2 | 1371 | +24.4% [+10.8, +35.0] | +0.4527 [+0.2096, +0.6803] | gain |
| ordinary | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 1371 | -5.1% [-29.2, -0.0] | -0.06797 [-0.4024, +0.0005397] | undecided (was loss) |
| ordinary | v2_ewma_hl5 against B1 | 1371 | +22.2% [+15.6, +36.2] | +0.3948 [+0.2322, +0.8509] | gain |
| ordinary | v2_ewma_hl5 against B1p | 1371 | +7.8% [-2.0, +15.9] | +0.1179 [-0.01572, +0.2741] | undecided |
| ordinary | v2_ewma_hl5 against B2 | 1371 | +25.3% [+12.8, +35.6] | +0.4684 [+0.2423, +0.6947] | gain |
| ordinary | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 1371 | -3.9% [-22.0, +0.3] | -0.05232 [-0.2996, +0.004818] | undecided |
| ordinary | v2_ewma_hl5_asym against B1 | 1371 | +22.4% [+15.9, +36.3] | +0.3989 [+0.2347, +0.8551] | gain |
| ordinary | v2_ewma_hl5_asym against B1p | 1371 | +8.1% [-1.7, +16.2] | +0.122 [-0.0123, +0.2796] | undecided |
| ordinary | v2_ewma_hl5_asym against B2 | 1371 | +25.5% [+13.2, +35.8] | +0.4725 [+0.2475, +0.6982] | gain |
| ordinary | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 1371 | -3.6% [-21.4, +0.5] | -0.04823 [-0.2894, +0.007005] | undecided |
| ordinary | v3_miss against B1 | 1371 | +25.0% [+16.4, +46.6] | +0.4459 [+0.2439, +1.078] | gain |
| ordinary | v3_miss against B1p | 1371 | +11.2% [+5.9, +18.1] | +0.169 [+0.07575, +0.3347] | gain |
| ordinary | v3_miss against B2 | 1371 | +28.0% [+18.3, +37.4] | +0.5194 [+0.328, +0.7349] | gain |
| ordinary | v3_miss against spread_mr_fhs_mad20_f0.5 | 1371 | -0.1% [-0.6, +0.3] | -0.00127 [-0.007465, +0.004328] | undecided |
| ordinary | v4_v3_miss_cal against B1 | 1371 | +25.6% [+17.0, +47.2] | +0.4568 [+0.2533, +1.096] | gain |
| ordinary | v4_v3_miss_cal against B1p | 1371 | +12.0% [+6.8, +18.7] | +0.1799 [+0.08742, +0.3452] | gain |
| ordinary | v4_v3_miss_cal against B2 | 1371 | +28.6% [+18.9, +38.0] | +0.5304 [+0.3398, +0.7468] | gain |
| ordinary | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 1371 | +0.7% [+0.1, +1.4] | +0.009684 [+0.001326, +0.01743] | gain |

### upper_tail_twcrps, by pressure-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| ordinary | spread_mr_fhs_mad20_f0.5 against B1 | 1590 | +45.5% [+31.8, +77.2] | +0.5202 [+0.2372, +1.741] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5 against B1p | 1590 | +20.3% [+9.9, +32.5] | +0.159 [+0.06052, +0.3562] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5 against B2 | 1590 | +18.8% [+6.9, +30.0] | +0.1443 [+0.04871, +0.2721] | gain |
| ordinary | v1_blend5_20 against B1 | 1590 | +42.5% [+29.5, +75.1] | +0.485 [+0.2205, +1.669] | gain |
| ordinary | v1_blend5_20 against B1p | 1590 | +15.9% [+4.0, +27.2] | +0.1239 [+0.02963, +0.2842] | gain |
| ordinary | v1_blend5_20 against B2 | 1590 | +14.2% [-0.0, +27.0] | +0.1092 [+0.00726, +0.2357] | gain (was undecided) |
| ordinary | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 1590 | -5.6% [-9.7, -2.7] | -0.03512 [-0.07364, -0.01481] | loss |
| ordinary | v1_mad10 against B1 | 1590 | +43.3% [+30.5, +75.0] | +0.4951 [+0.2273, +1.685] | gain |
| ordinary | v1_mad10 against B1p | 1590 | +17.1% [+5.9, +28.5] | +0.134 [+0.03856, +0.2985] | gain |
| ordinary | v1_mad10 against B2 | 1590 | +15.6% [+1.4, +28.3] | +0.1193 [+0.01599, +0.2464] | gain |
| ordinary | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 1590 | -4.0% [-9.5, -0.4] | -0.02502 [-0.06696, -0.002529] | loss |
| ordinary | v1_mad5 against B1 | 1590 | +36.3% [+23.3, +71.1] | +0.415 [+0.1735, +1.543] | gain |
| ordinary | v1_mad5 against B1p | 1590 | +6.9% [-8.8, +19.2] | +0.05384 [-0.04571, +0.1789] | undecided |
| ordinary | v1_mad5 against B2 | 1590 | +5.1% [-13.3, +19.9] | +0.03917 [-0.08225, +0.1642] | undecided |
| ordinary | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 1590 | -16.9% [-25.4, -11.0] | -0.1051 [-0.1989, -0.05886] | loss |
| ordinary | v2_ewma_hl10 against B1 | 1590 | +38.4% [+25.4, +65.2] | +0.4392 [+0.1947, +1.482] | gain |
| ordinary | v2_ewma_hl10 against B1p | 1590 | +10.0% [-9.9, +25.2] | +0.07807 [-0.04591, +0.2336] | undecided |
| ordinary | v2_ewma_hl10 against B2 | 1590 | +8.3% [-14.9, +24.7] | +0.0634 [-0.08624, +0.2028] | undecided |
| ordinary | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 1590 | -13.0% [-33.2, -4.4] | -0.08091 [-0.2446, -0.02169] | loss |
| ordinary | v2_ewma_hl3 against B1 | 1590 | +35.2% [+25.3, +55.8] | +0.402 [+0.1904, +1.253] | gain |
| ordinary | v2_ewma_hl3 against B1p | 1590 | +5.2% [-27.9, +21.5] | +0.0408 [-0.1385, +0.1826] | undecided |
| ordinary | v2_ewma_hl3 against B2 | 1590 | +3.4% [-30.9, +21.9] | +0.02612 [-0.1876, +0.1715] | undecided |
| ordinary | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 1590 | -19.0% [-58.9, -7.2] | -0.1182 [-0.4548, -0.03681] | loss |
| ordinary | v2_ewma_hl5 against B1 | 1590 | +37.1% [+26.1, +60.4] | +0.4243 [+0.1983, +1.367] | gain |
| ordinary | v2_ewma_hl5 against B1p | 1590 | +8.1% [-18.2, +23.6] | +0.06316 [-0.08624, +0.2083] | undecided |
| ordinary | v2_ewma_hl5 against B2 | 1590 | +6.3% [-22.8, +23.7] | +0.04849 [-0.1321, +0.1903] | undecided |
| ordinary | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 1590 | -15.4% [-48.8, -5.2] | -0.09582 [-0.3689, -0.02575] | loss |
| ordinary | v2_ewma_hl5_asym against B1 | 1590 | +37.5% [+26.5, +60.9] | +0.428 [+0.2012, +1.385] | gain |
| ordinary | v2_ewma_hl5_asym against B1p | 1590 | +8.6% [-17.2, +23.7] | +0.06683 [-0.07893, +0.2109] | undecided |
| ordinary | v2_ewma_hl5_asym against B2 | 1590 | +6.8% [-21.5, +23.9] | +0.05215 [-0.1241, +0.1923] | undecided |
| ordinary | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 1590 | -14.8% [-46.2, -5.0] | -0.09216 [-0.3502, -0.02407] | loss |
| ordinary | v3_miss against B1 | 1590 | +45.3% [+31.5, +77.5] | +0.5177 [+0.2342, +1.745] | gain |
| ordinary | v3_miss against B1p | 1590 | +20.0% [+9.5, +32.3] | +0.1565 [+0.05829, +0.3535] | gain |
| ordinary | v3_miss against B2 | 1590 | +18.5% [+6.6, +29.7] | +0.1418 [+0.04663, +0.2692] | gain |
| ordinary | v3_miss against spread_mr_fhs_mad20_f0.5 | 1590 | -0.4% [-0.7, -0.1] | -0.002487 [-0.00449, -0.0009001] | loss |
| ordinary | v4_v3_miss_cal against B1 | 1590 | +46.6% [+32.8, +76.2] | +0.5324 [+0.2467, +1.753] | gain |
| ordinary | v4_v3_miss_cal against B1p | 1590 | +21.9% [+12.1, +33.3] | +0.1712 [+0.07393, +0.3658] | gain |
| ordinary | v4_v3_miss_cal against B2 | 1590 | +20.4% [+9.0, +31.5] | +0.1565 [+0.06248, +0.2842] | gain |
| ordinary | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 1590 | +2.0% [+0.4, +3.3] | +0.01224 [+0.004494, +0.02016] | gain |

### grid_crps, by pressure-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| quarter_end | spread_mr_fhs_mad20_f0.5 against B1 | 30 | +9.8% [+8.0, +11.5] | +0.6847 [+0.1427, +2.136] | gain |
| quarter_end | spread_mr_fhs_mad20_f0.5 against B1p | 30 | +8.4% [+6.0, +10.4] | +0.5759 [+0.1426, +1.673] | gain |
| quarter_end | spread_mr_fhs_mad20_f0.5 against B2 | 30 | +17.0% [-34.1, +53.9] | +1.289 [-1.056, +4.061] | undecided |
| quarter_end | v1_blend5_20 against B1 | 30 | +12.6% [+9.3, +19.0] | +0.8787 [+0.1021, +3.745] | gain |
| quarter_end | v1_blend5_20 against B1p | 30 | +11.2% [+8.5, +16.2] | +0.77 [+0.1138, +2.898] | gain |
| quarter_end | v1_blend5_20 against B2 | 30 | +19.6% [-35.2, +60.3] | +1.483 [-0.9451, +4.786] | undecided |
| quarter_end | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 30 | +3.1% [-0.9, +22.1] | +0.1941 [-0.05854, +3.829] | undecided |
| quarter_end | v1_mad10 against B1 | 30 | +10.5% [+7.1, +16.7] | +0.7291 [+0.137, +2.607] | gain |
| quarter_end | v1_mad10 against B1p | 30 | +9.1% [+6.0, +13.9] | +0.6203 [+0.1483, +1.963] | gain |
| quarter_end | v1_mad10 against B2 | 30 | +17.6% [-41.6, +59.4] | +1.333 [-1.169, +4.517] | undecided |
| quarter_end | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 30 | +0.7% [-4.2, +9.5] | +0.04438 [-0.1588, +0.6899] | undecided |
| quarter_end | v1_mad5 against B1 | 30 | +11.7% [+8.3, +19.0] | +0.8164 [+0.09438, +3.456] | gain |
| quarter_end | v1_mad5 against B1p | 30 | +10.3% [+7.4, +16.0] | +0.7077 [+0.103, +2.616] | gain |
| quarter_end | v1_mad5 against B2 | 30 | +18.8% [-38.0, +59.8] | +1.421 [-1.036, +4.71] | undecided |
| quarter_end | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 30 | +2.1% [-2.2, +15.4] | +0.1317 [-0.1114, +2.361] | undecided |
| quarter_end | v2_ewma_hl10 against B1 | 30 | +13.6% [+9.9, +22.5] | +0.9482 [+0.1956, +3.818] | gain |
| quarter_end | v2_ewma_hl10 against B1p | 30 | +12.3% [+8.8, +19.2] | +0.8394 [+0.2017, +2.998] | gain |
| quarter_end | v2_ewma_hl10 against B2 | 30 | +20.5% [-37.8, +61.7] | +1.553 [-0.8272, +4.9] | undecided |
| quarter_end | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 30 | +4.2% [-0.7, +22.4] | +0.2635 [-0.007716, +3.327] | undecided |
| quarter_end | v2_ewma_hl3 against B1 | 30 | +12.5% [+9.9, +17.2] | +0.8681 [+0.1381, +3.256] | gain |
| quarter_end | v2_ewma_hl3 against B1p | 30 | +11.1% [+8.9, +14.6] | +0.7593 [+0.1442, +2.483] | gain |
| quarter_end | v2_ewma_hl3 against B2 | 30 | +19.5% [-35.4, +59.6] | +1.472 [-0.8913, +4.7] | undecided |
| quarter_end | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 30 | +2.9% [-0.5, +11.3] | +0.1834 [-0.02378, +1.367] | undecided |
| quarter_end | v2_ewma_hl5 against B1 | 30 | +12.9% [+9.9, +19.6] | +0.8998 [+0.1803, +3.409] | gain |
| quarter_end | v2_ewma_hl5 against B1p | 30 | +11.6% [+8.7, +16.6] | +0.791 [+0.189, +2.612] | gain |
| quarter_end | v2_ewma_hl5 against B2 | 30 | +19.9% [-37.3, +60.4] | +1.504 [-0.8674, +4.757] | undecided |
| quarter_end | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 30 | +3.4% [-0.8, +15.3] | +0.2151 [-0.01292, +2.226] | undecided |
| quarter_end | v2_ewma_hl5_asym against B1 | 30 | +12.8% [+9.7, +19.9] | +0.8917 [+0.185, +3.354] | gain |
| quarter_end | v2_ewma_hl5_asym against B1p | 30 | +11.4% [+8.5, +16.9] | +0.783 [+0.1905, +2.587] | gain |
| quarter_end | v2_ewma_hl5_asym against B2 | 30 | +19.8% [-38.1, +60.5] | +1.496 [-0.8695, +4.759] | undecided |
| quarter_end | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 30 | +3.3% [-1.2, +13.9] | +0.207 [-0.02121, +1.765] | undecided |
| quarter_end | v3_miss against B1 | 30 | +10.0% [+8.2, +11.6] | +0.6966 [+0.1479, +2.169] | gain |
| quarter_end | v3_miss against B1p | 30 | +8.6% [+6.2, +10.5] | +0.5878 [+0.1464, +1.713] | gain |
| quarter_end | v3_miss against B2 | 30 | +17.2% [-33.8, +53.8] | +1.301 [-1.036, +4.073] | undecided |
| quarter_end | v3_miss against spread_mr_fhs_mad20_f0.5 | 30 | +0.2% [+0.1, +0.3] | +0.01186 [+0.001773, +0.02608] | gain |
| quarter_end | v4_v3_miss_cal against B1 | 30 | +18.5% [+13.6, +22.2] | +1.285 [+0.1372, +3.751] | gain |
| quarter_end | v4_v3_miss_cal against B1p | 30 | +17.2% [+11.4, +21.4] | +1.176 [+0.1237, +3.223] | gain |
| quarter_end | v4_v3_miss_cal against B2 | 30 | +25.0% [-21.7, +56.3] | +1.889 [+0.114, +4.909] | gain (was undecided) |
| quarter_end | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 30 | +9.6% [+5.1, +13.7] | +0.6 [+0.01796, +1.691] | gain |

### scaled_grid_crps, by pressure-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| quarter_end | spread_mr_fhs_mad20_f0.5 against B1 | 26 | +14.7% [+11.2, +17.3] | +0.2262 [+0.03029, +0.8834] | gain |
| quarter_end | spread_mr_fhs_mad20_f0.5 against B1p | 26 | +14.2% [+10.7, +16.8] | +0.2172 [+0.02178, +0.8833] | gain |
| quarter_end | spread_mr_fhs_mad20_f0.5 against B2 | 26 | +25.9% [-35.1, +71.3] | +0.4595 [-0.09244, +0.8956] | undecided |
| quarter_end | v1_blend5_20 against B1 | 26 | +15.3% [+10.2, +20.0] | +0.2352 [+0.05199, +0.7233] | gain |
| quarter_end | v1_blend5_20 against B1p | 26 | +14.8% [+10.1, +18.9] | +0.2261 [+0.04482, +0.7206] | gain |
| quarter_end | v1_blend5_20 against B2 | 26 | +26.4% [-39.1, +72.8] | +0.4685 [-0.1191, +0.9088] | undecided |
| quarter_end | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 26 | +0.7% [-2.6, +10.1] | +0.008959 [-0.03274, +0.1436] | undecided |
| quarter_end | v1_mad10 against B1 | 26 | +14.8% [+10.2, +18.3] | +0.2275 [+0.05637, +0.6858] | gain |
| quarter_end | v1_mad10 against B1p | 26 | +14.3% [+10.0, +17.3] | +0.2184 [+0.04986, +0.6806] | gain |
| quarter_end | v1_mad10 against B2 | 26 | +26.0% [-38.3, +73.0] | +0.4608 [-0.1391, +0.9141] | undecided |
| quarter_end | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 26 | +0.1% [-3.0, +5.1] | +0.001244 [-0.03765, +0.06242] | undecided |
| quarter_end | v1_mad5 against B1 | 26 | +14.0% [+9.5, +17.8] | +0.2154 [+0.05036, +0.6537] | gain |
| quarter_end | v1_mad5 against B1p | 26 | +13.5% [+9.3, +16.8] | +0.2063 [+0.04498, +0.6458] | gain |
| quarter_end | v1_mad5 against B2 | 26 | +25.3% [-42.5, +72.5] | +0.4487 [-0.1705, +0.9194] | undecided |
| quarter_end | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 26 | -0.8% [-3.8, +4.1] | -0.01084 [-0.05595, +0.04314] | undecided |
| quarter_end | v2_ewma_hl10 against B1 | 26 | +17.5% [+11.7, +24.7] | +0.2687 [+0.06859, +0.7608] | gain |
| quarter_end | v2_ewma_hl10 against B1p | 26 | +17.0% [+11.7, +23.3] | +0.2596 [+0.06218, +0.7558] | gain |
| quarter_end | v2_ewma_hl10 against B2 | 26 | +28.3% [-40.8, +74.9] | +0.502 [-0.06536, +0.9228] | undecided |
| quarter_end | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 26 | +3.2% [-2.2, +37.3] | +0.04248 [-0.0122, +0.5772] | undecided |
| quarter_end | v2_ewma_hl3 against B1 | 26 | +15.1% [+10.9, +18.6] | +0.2324 [+0.06395, +0.6648] | gain |
| quarter_end | v2_ewma_hl3 against B1p | 26 | +14.6% [+10.8, +17.5] | +0.2233 [+0.05688, +0.6606] | gain |
| quarter_end | v2_ewma_hl3 against B2 | 26 | +26.3% [-41.2, +75.0] | +0.4657 [-0.1197, +0.9397] | undecided |
| quarter_end | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 26 | +0.5% [-3.0, +4.8] | +0.006153 [-0.03401, +0.06428] | undecided |
| quarter_end | v2_ewma_hl5 against B1 | 26 | +16.6% [+11.8, +21.6] | +0.2555 [+0.06766, +0.7239] | gain |
| quarter_end | v2_ewma_hl5 against B1p | 26 | +16.1% [+11.6, +20.4] | +0.2464 [+0.06155, +0.7223] | gain |
| quarter_end | v2_ewma_hl5 against B2 | 26 | +27.6% [-40.5, +75.0] | +0.4888 [-0.08268, +0.9315] | undecided |
| quarter_end | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 26 | +2.2% [-1.5, +16.2] | +0.02925 [-0.01485, +0.3041] | undecided |
| quarter_end | v2_ewma_hl5_asym against B1 | 26 | +16.3% [+11.5, +21.5] | +0.2512 [+0.06309, +0.727] | gain |
| quarter_end | v2_ewma_hl5_asym against B1p | 26 | +15.8% [+11.2, +20.3] | +0.2421 [+0.05637, +0.7217] | gain |
| quarter_end | v2_ewma_hl5_asym against B2 | 26 | +27.3% [-41.5, +74.4] | +0.4845 [-0.09356, +0.9246] | undecided |
| quarter_end | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 26 | +1.9% [-1.7, +12.6] | +0.02495 [-0.02305, +0.2137] | undecided |
| quarter_end | v3_miss against B1 | 26 | +14.8% [+11.6, +17.2] | +0.2277 [+0.03094, +0.9198] | gain |
| quarter_end | v3_miss against B1p | 26 | +14.3% [+11.0, +16.7] | +0.2186 [+0.02415, +0.9205] | gain |
| quarter_end | v3_miss against B2 | 26 | +26.0% [-34.9, +71.5] | +0.461 [-0.08884, +0.8977] | undecided |
| quarter_end | v3_miss against spread_mr_fhs_mad20_f0.5 | 26 | +0.1% [-0.1, +0.4] | +0.001478 [-0.001674, +0.005994] | undecided |
| quarter_end | v4_v3_miss_cal against B1 | 26 | +25.8% [+16.8, +32.7] | +0.3974 [-0.0005063, +2.149] | undecided (was gain) |
| quarter_end | v4_v3_miss_cal against B1p | 26 | +25.4% [+16.1, +32.6] | +0.3884 [-0.007405, +2.202] | undecided (was gain) |
| quarter_end | v4_v3_miss_cal against B2 | 26 | +35.6% [-7.9, +70.7] | +0.6307 [+0.3941, +0.838] | gain (was undecided) |
| quarter_end | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 26 | +13.0% [+6.3, +19.4] | +0.1712 [-0.03369, +0.8656] | undecided (was gain) |

### grid_crps, by pressure-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| tax_date | spread_mr_fhs_mad20_f0.5 against B1 | 89 | +6.8% [-5.8, +13.7] | +0.3754 [+0.05028, +1.086] | gain (was undecided) |
| tax_date | spread_mr_fhs_mad20_f0.5 against B1p | 89 | +5.5% [+1.8, +8.9] | +0.299 [+0.01095, +1.208] | gain |
| tax_date | spread_mr_fhs_mad20_f0.5 against B2 | 89 | +33.8% [-60.8, +58.2] | +2.617 [+1.41, +4.882] | gain (was undecided) |
| tax_date | v1_blend5_20 against B1 | 89 | +6.9% [-6.6, +14.3] | +0.377 [+0.07484, +1.076] | gain (was undecided) |
| tax_date | v1_blend5_20 against B1p | 89 | +5.5% [+1.5, +9.5] | +0.3006 [+0.03172, +1.228] | gain |
| tax_date | v1_blend5_20 against B2 | 89 | +33.8% [-64.8, +58.5] | +2.619 [+1.417, +4.787] | gain (was undecided) |
| tax_date | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 89 | +0.0% [-0.7, +1.0] | +0.00155 [-0.03184, +0.03125] | undecided |
| tax_date | v1_mad10 against B1 | 89 | +6.7% [-3.6, +13.6] | +0.3706 [+0.07019, +1.132] | gain (was undecided) |
| tax_date | v1_mad10 against B1p | 89 | +5.4% [+2.6, +8.6] | +0.2943 [+0.02176, +1.311] | gain |
| tax_date | v1_mad10 against B2 | 89 | +33.8% [-61.7, +58.2] | +2.612 [+1.399, +4.827] | gain (was undecided) |
| tax_date | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 89 | -0.1% [-0.6, +0.6] | -0.004766 [-0.0339, +0.03974] | undecided |
| tax_date | v1_mad5 against B1 | 89 | +7.0% [-3.1, +13.4] | +0.3831 [+0.08847, +1.249] | gain (was undecided) |
| tax_date | v1_mad5 against B1p | 89 | +5.7% [+2.9, +8.7] | +0.3067 [+0.031, +1.496] | gain |
| tax_date | v1_mad5 against B2 | 89 | +33.9% [-61.3, +58.3] | +2.625 [+1.399, +4.861] | gain (was undecided) |
| tax_date | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 89 | +0.1% [-0.6, +0.9] | +0.007672 [-0.0342, +0.0642] | undecided |
| tax_date | v2_ewma_hl10 against B1 | 89 | +3.9% [-11.5, +12.8] | +0.2164 [-0.01968, +0.5091] | undecided |
| tax_date | v2_ewma_hl10 against B1p | 89 | +2.6% [-3.0, +7.4] | +0.14 [-0.04316, +0.3652] | undecided |
| tax_date | v2_ewma_hl10 against B2 | 89 | +31.8% [-70.3, +57.6] | +2.458 [+1.396, +4.253] | gain (was undecided) |
| tax_date | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 89 | -3.1% [-5.1, -2.0] | -0.159 [-1.841, +0.01819] | undecided (was loss) |
| tax_date | v2_ewma_hl3 against B1 | 89 | +5.0% [-9.2, +13.4] | +0.2737 [+0.01964, +0.6215] | gain (was undecided) |
| tax_date | v2_ewma_hl3 against B1p | 89 | +3.6% [-1.2, +8.4] | +0.1973 [-0.01557, +0.5431] | undecided |
| tax_date | v2_ewma_hl3 against B2 | 89 | +32.5% [-68.3, +57.9] | +2.515 [+1.395, +4.437] | gain (was undecided) |
| tax_date | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 89 | -2.0% [-3.6, -0.8] | -0.1017 [-0.9656, +0.01707] | undecided (was loss) |
| tax_date | v2_ewma_hl5 against B1 | 89 | +4.4% [-10.9, +13.4] | +0.2438 [+0.005053, +0.5662] | gain (was undecided) |
| tax_date | v2_ewma_hl5 against B1p | 89 | +3.1% [-2.4, +8.1] | +0.1674 [-0.03049, +0.434] | undecided |
| tax_date | v2_ewma_hl5 against B2 | 89 | +32.1% [-70.2, +57.8] | +2.485 [+1.392, +4.337] | gain (was undecided) |
| tax_date | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 89 | -2.6% [-4.7, -1.3] | -0.1316 [-1.534, +0.01979] | undecided (was loss) |
| tax_date | v2_ewma_hl5_asym against B1 | 89 | +4.5% [-10.6, +13.2] | +0.2496 [-0.02206, +0.5745] | undecided |
| tax_date | v2_ewma_hl5_asym against B1p | 89 | +3.2% [-2.6, +7.9] | +0.1732 [-0.05475, +0.4462] | undecided |
| tax_date | v2_ewma_hl5_asym against B2 | 89 | +32.2% [-67.1, +57.7] | +2.491 [+1.391, +4.381] | gain (was undecided) |
| tax_date | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 89 | -2.5% [-4.0, -1.1] | -0.1258 [-1.061, +0.01516] | undecided (was loss) |
| tax_date | v3_miss against B1 | 89 | +7.2% [-6.3, +14.4] | +0.3954 [+0.0762, +1.167] | gain (was undecided) |
| tax_date | v3_miss against B1p | 89 | +5.9% [+1.8, +9.6] | +0.319 [+0.03151, +1.332] | gain |
| tax_date | v3_miss against B2 | 89 | +34.1% [-63.0, +58.6] | +2.637 [+1.425, +4.9] | gain (was undecided) |
| tax_date | v3_miss against spread_mr_fhs_mad20_f0.5 | 89 | +0.4% [-0.2, +1.3] | +0.01999 [+0.0097, +0.04788] | gain (was undecided) |
| tax_date | v4_v3_miss_cal against B1 | 89 | +5.1% [-2.0, +11.4] | +0.2785 [-0.04437, +0.9441] | undecided |
| tax_date | v4_v3_miss_cal against B1p | 89 | +3.7% [+1.2, +6.9] | +0.2021 [-0.07475, +0.9976] | undecided (was gain) |
| tax_date | v4_v3_miss_cal against B2 | 89 | +32.6% [-71.7, +55.6] | +2.52 [+1.416, +4.556] | gain (was undecided) |
| tax_date | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 89 | -1.9% [-9.1, +0.2] | -0.09695 [-0.4029, +0.01872] | undecided |

### scaled_grid_crps, by pressure-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| tax_date | spread_mr_fhs_mad20_f0.5 against B1 | 77 | +8.4% [-5.5, +23.0] | +0.1582 [+0.0005159, +0.5241] | gain (was undecided) |
| tax_date | spread_mr_fhs_mad20_f0.5 against B1p | 77 | +5.4% [+1.8, +10.4] | +0.09823 [-0.008694, +0.359] | undecided (was gain) |
| tax_date | spread_mr_fhs_mad20_f0.5 against B2 | 77 | +34.2% [-47.1, +57.5] | +0.9007 [+0.6677, +1.219] | gain (was undecided) |
| tax_date | v1_blend5_20 against B1 | 77 | +8.4% [-5.3, +23.7] | +0.1584 [+0.01333, +0.5271] | gain (was undecided) |
| tax_date | v1_blend5_20 against B1p | 77 | +5.4% [+2.1, +10.5] | +0.09847 [+0.003791, +0.356] | gain |
| tax_date | v1_blend5_20 against B2 | 77 | +34.2% [-49.0, +57.8] | +0.9009 [+0.6719, +1.209] | gain (was undecided) |
| tax_date | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 77 | +0.0% [-0.6, +0.8] | +0.000241 [-0.01164, +0.01473] | undecided |
| tax_date | v1_mad10 against B1 | 77 | +8.1% [-3.2, +23.1] | +0.1533 [+0.01136, +0.544] | gain (was undecided) |
| tax_date | v1_mad10 against B1p | 77 | +5.1% [+2.5, +9.3] | +0.09333 [-0.001649, +0.3632] | undecided (was gain) |
| tax_date | v1_mad10 against B2 | 77 | +34.0% [-43.2, +57.2] | +0.8958 [+0.6597, +1.205] | gain (was undecided) |
| tax_date | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 77 | -0.3% [-1.8, +0.6] | -0.004899 [-0.03258, +0.01335] | undecided |
| tax_date | v1_mad5 against B1 | 77 | +8.4% [-1.7, +21.7] | +0.158 [+0.02043, +0.5566] | gain (was undecided) |
| tax_date | v1_mad5 against B1p | 77 | +5.4% [+3.1, +8.9] | +0.09806 [+0.005547, +0.3955] | gain |
| tax_date | v1_mad5 against B2 | 77 | +34.2% [-45.5, +57.2] | +0.9005 [+0.6673, +1.213] | gain (was undecided) |
| tax_date | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 77 | -0.0% [-1.7, +1.8] | -0.0001686 [-0.02575, +0.02934] | undecided |
| tax_date | v2_ewma_hl10 against B1 | 77 | +5.9% [-12.3, +23.9] | +0.111 [-0.02087, +0.4784] | undecided |
| tax_date | v2_ewma_hl10 against B1p | 77 | +2.8% [-2.8, +10.5] | +0.051 [-0.02504, +0.1953] | undecided |
| tax_date | v2_ewma_hl10 against B2 | 77 | +32.4% [-51.4, +57.1] | +0.8535 [+0.6477, +1.121] | gain (was undecided) |
| tax_date | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 77 | -2.7% [-5.0, -0.9] | -0.04723 [-0.3625, +0.002773] | undecided (was loss) |
| tax_date | v2_ewma_hl3 against B1 | 77 | +6.5% [-9.2, +22.0] | +0.1225 [-0.004155, +0.4655] | undecided |
| tax_date | v2_ewma_hl3 against B1p | 77 | +3.4% [-0.5, +8.8] | +0.06252 [-0.01379, +0.1989] | undecided |
| tax_date | v2_ewma_hl3 against B2 | 77 | +32.8% [-48.8, +56.9] | +0.865 [+0.6525, +1.137] | gain (was undecided) |
| tax_date | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 77 | -2.1% [-3.0, -1.2] | -0.03571 [-0.1926, +0.002724] | undecided (was loss) |
| tax_date | v2_ewma_hl5 against B1 | 77 | +6.1% [-10.9, +23.0] | +0.1146 [-0.01301, +0.4759] | undecided |
| tax_date | v2_ewma_hl5 against B1p | 77 | +3.0% [-1.7, +9.5] | +0.0546 [-0.02037, +0.1906] | undecided |
| tax_date | v2_ewma_hl5 against B2 | 77 | +32.5% [-50.0, +57.0] | +0.8571 [+0.6485, +1.124] | gain (was undecided) |
| tax_date | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 77 | -2.5% [-4.1, -1.4] | -0.04363 [-0.3067, +0.00128] | undecided (was loss) |
| tax_date | v2_ewma_hl5_asym against B1 | 77 | +6.1% [-10.7, +21.7] | +0.1163 [-0.02082, +0.4537] | undecided |
| tax_date | v2_ewma_hl5_asym against B1p | 77 | +3.1% [-1.7, +9.1] | +0.05635 [-0.03037, +0.1905] | undecided |
| tax_date | v2_ewma_hl5_asym against B2 | 77 | +32.6% [-47.7, +56.8] | +0.8588 [+0.6465, +1.137] | gain (was undecided) |
| tax_date | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 77 | -2.4% [-3.5, -1.1] | -0.04188 [-0.209, -0.0006354] | loss |
| tax_date | v3_miss against B1 | 77 | +8.7% [-5.4, +24.2] | +0.1654 [+0.01153, +0.5487] | gain (was undecided) |
| tax_date | v3_miss against B1p | 77 | +5.8% [+2.1, +11.1] | +0.1054 [+0.001665, +0.3815] | gain |
| tax_date | v3_miss against B2 | 77 | +34.5% [-48.8, +57.9] | +0.9078 [+0.6745, +1.226] | gain (was undecided) |
| tax_date | v3_miss against spread_mr_fhs_mad20_f0.5 | 77 | +0.4% [-0.1, +1.1] | +0.007163 [+0.00302, +0.01343] | gain (was undecided) |
| tax_date | v4_v3_miss_cal against B1 | 77 | +7.4% [-5.2, +24.4] | +0.1397 [-0.0218, +0.5541] | undecided |
| tax_date | v4_v3_miss_cal against B1p | 77 | +4.4% [+1.0, +9.6] | +0.07974 [-0.02623, +0.3442] | undecided (was gain) |
| tax_date | v4_v3_miss_cal against B2 | 77 | +33.5% [-57.2, +56.5] | +0.8822 [+0.6477, +1.195] | gain (was undecided) |
| tax_date | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 77 | -1.1% [-3.7, -0.1] | -0.01849 [-0.06169, +0.008647] | undecided (was loss) |

### grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2018-19 | spread_mr_fhs_mad20_f0.5 against B1 | 361 | +34.1% [+24.7, +58.8] | +1.974 [+0.7821, +8.904] | gain |
| 2018-19 | spread_mr_fhs_mad20_f0.5 against B1p | 361 | +11.6% [+1.3, +27.9] | +0.4986 [+0.1447, +1.361] | gain |
| 2018-19 | spread_mr_fhs_mad20_f0.5 against B2 | 361 | +14.5% [+1.2, +28.4] | +0.645 [+0.1897, +1.181] | gain |
| 2018-19 | v1_blend5_20 against B1 | 361 | +31.8% [+23.2, +54.3] | +1.84 [+0.7355, +8.617] | gain |
| 2018-19 | v1_blend5_20 against B1p | 361 | +8.4% [-1.5, +21.3] | +0.364 [+0.04777, +0.9664] | gain (was undecided) |
| 2018-19 | v1_blend5_20 against B2 | 361 | +11.4% [-2.4, +25.6] | +0.5104 [+0.008381, +1.069] | gain (was undecided) |
| 2018-19 | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 361 | -3.5% [-7.9, -1.3] | -0.1346 [-0.3781, -0.03314] | loss |
| 2018-19 | v1_mad10 against B1 | 361 | +32.4% [+23.7, +56.3] | +1.878 [+0.7561, +9.331] | gain |
| 2018-19 | v1_mad10 against B1p | 361 | +9.3% [+0.3, +22.3] | +0.4025 [+0.09044, +1.02] | gain |
| 2018-19 | v1_mad10 against B2 | 361 | +12.3% [-1.2, +26.1] | +0.549 [+0.04126, +1.09] | gain (was undecided) |
| 2018-19 | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 361 | -2.5% [-8.5, +0.3] | -0.09606 [-0.3695, +0.01039] | undecided |
| 2018-19 | v1_mad5 against B1 | 361 | +26.5% [+18.2, +50.3] | +1.534 [+0.5404, +7.968] | gain |
| 2018-19 | v1_mad5 against B1p | 361 | +1.3% [-9.5, +11.0] | +0.0581 [-0.3249, +0.4711] | undecided |
| 2018-19 | v1_mad5 against B2 | 361 | +4.6% [-11.7, +17.9] | +0.2045 [-0.4592, +0.815] | undecided |
| 2018-19 | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 361 | -11.5% [-21.2, -5.7] | -0.4405 [-1.056, -0.2059] | loss |
| 2018-19 | v2_ewma_hl10 against B1 | 361 | +26.6% [+17.3, +49.4] | +1.54 [+0.5348, +7.361] | gain |
| 2018-19 | v2_ewma_hl10 against B1p | 361 | +1.5% [-12.6, +15.6] | +0.0645 [-0.4526, +0.6685] | undecided |
| 2018-19 | v2_ewma_hl10 against B2 | 361 | +4.7% [-14.8, +19.6] | +0.2109 [-0.6006, +0.8946] | undecided |
| 2018-19 | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 361 | -11.4% [-26.5, -4.8] | -0.4341 [-1.115, -0.1342] | loss |
| 2018-19 | v2_ewma_hl3 against B1 | 361 | +23.2% [+16.3, +36.6] | +1.341 [+0.5543, +5.585] | gain |
| 2018-19 | v2_ewma_hl3 against B1p | 361 | -3.1% [-31.6, +11.2] | -0.1347 [-1.225, +0.4681] | undecided |
| 2018-19 | v2_ewma_hl3 against B2 | 361 | +0.3% [-33.0, +16.8] | +0.01172 [-1.373, +0.7676] | undecided |
| 2018-19 | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 361 | -16.6% [-55.6, -7.3] | -0.6333 [-2.941, -0.165] | loss |
| 2018-19 | v2_ewma_hl5 against B1 | 361 | +25.0% [+17.1, +42.2] | +1.449 [+0.5645, +6.508] | gain |
| 2018-19 | v2_ewma_hl5 against B1p | 361 | -0.6% [-21.3, +13.2] | -0.0267 [-0.7848, +0.552] | undecided |
| 2018-19 | v2_ewma_hl5 against B2 | 361 | +2.7% [-23.6, +18.4] | +0.1197 [-0.9694, +0.8391] | undecided |
| 2018-19 | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 361 | -13.8% [-42.1, -5.8] | -0.5253 [-2.012, -0.1307] | loss |
| 2018-19 | v2_ewma_hl5_asym against B1 | 361 | +25.3% [+17.7, +42.5] | +1.467 [+0.5806, +6.743] | gain |
| 2018-19 | v2_ewma_hl5_asym against B1p | 361 | -0.2% [-20.6, +13.3] | -0.008477 [-0.7467, +0.556] | undecided |
| 2018-19 | v2_ewma_hl5_asym against B2 | 361 | +3.1% [-22.5, +18.6] | +0.1379 [-0.9198, +0.8453] | undecided |
| 2018-19 | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 361 | -13.3% [-40.2, -5.7] | -0.5071 [-1.94, -0.1271] | loss |
| 2018-19 | v3_miss against B1 | 361 | +34.1% [+24.7, +58.9] | +1.977 [+0.7807, +8.915] | gain |
| 2018-19 | v3_miss against B1p | 361 | +11.6% [+1.5, +27.9] | +0.501 [+0.1477, +1.364] | gain |
| 2018-19 | v3_miss against B2 | 361 | +14.5% [+1.3, +28.4] | +0.6474 [+0.1931, +1.182] | gain |
| 2018-19 | v3_miss against spread_mr_fhs_mad20_f0.5 | 361 | +0.1% [-0.2, +0.3] | +0.002424 [-0.006057, +0.01202] | undecided |
| 2018-19 | v4_v3_miss_cal against B1 | 361 | +35.0% [+25.2, +58.3] | +2.025 [+0.8164, +8.681] | gain |
| 2018-19 | v4_v3_miss_cal against B1p | 361 | +12.7% [+2.2, +27.4] | +0.5498 [+0.1988, +1.361] | gain |
| 2018-19 | v4_v3_miss_cal against B2 | 361 | +15.6% [+2.5, +29.6] | +0.6962 [+0.2753, +1.22] | gain |
| 2018-19 | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 361 | +1.3% [+0.1, +3.7] | +0.05124 [+0.008864, +0.1393] | gain |

### scaled_grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2018-19 | spread_mr_fhs_mad20_f0.5 against B1 | 104 | +50.3% [+31.7, +134.6] | +2.43 [+0.2381, +39.32] | gain |
| 2018-19 | spread_mr_fhs_mad20_f0.5 against B1p | 104 | -0.5% [-14.5, +10.2] | -0.01296 [-0.311, +0.2346] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f0.5 against B2 | 104 | -2.6% [-17.4, +9.6] | -0.06141 [-0.4126, +0.3137] | undecided |
| 2018-19 | v1_blend5_20 against B1 | 104 | +47.2% [+30.0, +120.2] | +2.279 [+0.2141, +34.89] | gain |
| 2018-19 | v1_blend5_20 against B1p | 104 | -6.9% [-26.0, +6.4] | -0.1642 [-0.6835, +0.1739] | undecided |
| 2018-19 | v1_blend5_20 against B2 | 104 | -9.1% [-31.8, +6.1] | -0.2127 [-0.7743, +0.2591] | undecided |
| 2018-19 | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 104 | -6.3% [-25.4, -1.6] | -0.1512 [-1.03, -0.01016] | loss |
| 2018-19 | v1_mad10 against B1 | 104 | +47.8% [+30.3, +128.5] | +2.312 [+0.2141, +36.68] | gain |
| 2018-19 | v1_mad10 against B1p | 104 | -5.5% [-24.7, +7.6] | -0.1308 [-0.619, +0.2187] | undecided |
| 2018-19 | v1_mad10 against B2 | 104 | -7.7% [-33.7, +7.3] | -0.1793 [-0.798, +0.2605] | undecided |
| 2018-19 | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 104 | -4.9% [-33.2, +1.7] | -0.1179 [-0.9147, +0.04437] | undecided |
| 2018-19 | v1_mad5 against B1 | 104 | +41.0% [+23.9, +120.0] | +1.984 [+0.1037, +31.72] | gain |
| 2018-19 | v1_mad5 against B1p | 104 | -19.2% [-56.5, -2.6] | -0.4593 [-1.813, +0.03935] | undecided (was loss) |
| 2018-19 | v1_mad5 against B2 | 104 | -21.7% [-64.5, +0.7] | -0.5078 [-1.64, +0.1457] | undecided |
| 2018-19 | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 104 | -18.6% [-61.7, -4.8] | -0.4464 [-2.794, -0.09038] | loss |
| 2018-19 | v2_ewma_hl10 against B1 | 104 | +36.2% [+11.6, +139.6] | +1.747 [-0.1984, +25.58] | undecided (was gain) |
| 2018-19 | v2_ewma_hl10 against B1p | 104 | -29.1% [-73.5, -6.8] | -0.696 [-1.991, -0.1058] | loss |
| 2018-19 | v2_ewma_hl10 against B2 | 104 | -31.8% [-95.3, +3.5] | -0.7445 [-2.081, +0.09923] | undecided |
| 2018-19 | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 104 | -28.4% [-80.0, +7.7] | -0.683 [-2.244, -0.1474] | loss (was undecided) |
| 2018-19 | v2_ewma_hl3 against B1 | 104 | +30.9% [+13.7, +74.9] | +1.495 [+0.009948, +16.85] | gain |
| 2018-19 | v2_ewma_hl3 against B1p | 104 | -39.7% [-169.6, -5.5] | -0.9484 [-5.944, +0.08594] | undecided (was loss) |
| 2018-19 | v2_ewma_hl3 against B2 | 104 | -42.6% [-174.5, -4.0] | -0.9968 [-5.155, +0.1475] | undecided (was loss) |
| 2018-19 | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 104 | -38.9% [-456.9, -7.7] | -0.9354 [-22.13, -0.02893] | loss |
| 2018-19 | v2_ewma_hl5 against B1 | 104 | +33.7% [+12.5, +101.0] | +1.629 [-0.07671, +21.96] | undecided (was gain) |
| 2018-19 | v2_ewma_hl5 against B1p | 104 | -34.1% [-124.8, -6.1] | -0.8144 [-4.275, +0.02542] | undecided (was loss) |
| 2018-19 | v2_ewma_hl5 against B2 | 104 | -36.8% [-133.3, -0.4] | -0.8629 [-3.539, +0.1333] | undecided (was loss) |
| 2018-19 | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 104 | -33.4% [-187.9, -3.3] | -0.8015 [-7.382, -0.05924] | loss |
| 2018-19 | v2_ewma_hl5_asym against B1 | 104 | +34.3% [+14.0, +100.8] | +1.659 [-0.04832, +22.95] | undecided (was gain) |
| 2018-19 | v2_ewma_hl5_asym against B1p | 104 | -32.8% [-122.3, -5.6] | -0.7847 [-4.208, +0.03685] | undecided (was loss) |
| 2018-19 | v2_ewma_hl5_asym against B2 | 104 | -35.6% [-128.9, -0.2] | -0.8331 [-3.455, +0.1421] | undecided (was loss) |
| 2018-19 | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 104 | -32.1% [-186.2, -3.4] | -0.7717 [-7.348, -0.05134] | loss |
| 2018-19 | v3_miss against B1 | 104 | +50.3% [+31.7, +135.9] | +2.432 [+0.2302, +39.68] | gain |
| 2018-19 | v3_miss against B1p | 104 | -0.5% [-14.1, +10.3] | -0.01099 [-0.2999, +0.2355] | undecided |
| 2018-19 | v3_miss against B2 | 104 | -2.5% [-17.1, +9.6] | -0.05944 [-0.4055, +0.3119] | undecided |
| 2018-19 | v3_miss against spread_mr_fhs_mad20_f0.5 | 104 | +0.1% [-0.5, +0.5] | +0.001965 [-0.007915, +0.01527] | undecided |
| 2018-19 | v4_v3_miss_cal against B1 | 104 | +51.3% [+33.1, +131.4] | +2.481 [+0.2736, +38.15] | gain |
| 2018-19 | v4_v3_miss_cal against B1p | 104 | +1.6% [-13.7, +13.9] | +0.03809 [-0.2567, +0.3023] | undecided |
| 2018-19 | v4_v3_miss_cal against B2 | 104 | -0.4% [-14.0, +11.6] | -0.01036 [-0.3278, +0.3347] | undecided |
| 2018-19 | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 104 | +2.1% [-1.5, +6.4] | +0.05105 [+0.00482, +0.1363] | gain (was undecided) |

### upper_tail_twcrps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2018-19 | spread_mr_fhs_mad20_f0.5 against B1 | 361 | +35.7% [+25.5, +59.7] | +1.885 [+0.6762, +8.774] | gain |
| 2018-19 | spread_mr_fhs_mad20_f0.5 against B1p | 361 | +11.5% [-0.4, +30.9] | +0.4411 [+0.08168, +1.361] | gain (was undecided) |
| 2018-19 | spread_mr_fhs_mad20_f0.5 against B2 | 361 | +11.0% [-1.3, +24.3] | +0.419 [+0.03207, +0.8766] | gain (was undecided) |
| 2018-19 | v1_blend5_20 against B1 | 361 | +33.6% [+24.1, +57.1] | +1.773 [+0.6314, +8.57] | gain |
| 2018-19 | v1_blend5_20 against B1p | 361 | +8.6% [-2.1, +24.2] | +0.3296 [+0.01251, +1.017] | gain (was undecided) |
| 2018-19 | v1_blend5_20 against B2 | 361 | +8.1% [-4.3, +21.2] | +0.3075 [-0.1124, +0.7879] | undecided |
| 2018-19 | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 361 | -3.3% [-6.8, -1.0] | -0.1115 [-0.2788, -0.02803] | loss |
| 2018-19 | v1_mad10 against B1 | 361 | +34.3% [+24.8, +57.7] | +1.811 [+0.6657, +9.093] | gain |
| 2018-19 | v1_mad10 against B1p | 361 | +9.6% [-0.3, +24.9] | +0.3666 [+0.05869, +1.033] | gain (was undecided) |
| 2018-19 | v1_mad10 against B2 | 361 | +9.0% [-3.2, +22.2] | +0.3445 [-0.07325, +0.8095] | undecided |
| 2018-19 | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 361 | -2.2% [-8.1, +0.8] | -0.07448 [-0.308, +0.01939] | undecided |
| 2018-19 | v1_mad5 against B1 | 361 | +29.5% [+20.3, +55.0] | +1.557 [+0.4983, +8.454] | gain |
| 2018-19 | v1_mad5 against B1p | 361 | +2.9% [-7.4, +14.9] | +0.113 [-0.2128, +0.6033] | undecided |
| 2018-19 | v1_mad5 against B2 | 361 | +2.4% [-12.2, +14.6] | +0.09089 [-0.4358, +0.6044] | undecided |
| 2018-19 | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 361 | -9.7% [-17.1, -3.6] | -0.3281 [-0.7221, -0.1457] | loss |
| 2018-19 | v2_ewma_hl10 against B1 | 361 | +28.3% [+18.1, +54.0] | +1.492 [+0.4446, +7.789] | gain |
| 2018-19 | v2_ewma_hl10 against B1p | 361 | +1.2% [-11.9, +16.7] | +0.04772 [-0.3811, +0.6554] | undecided |
| 2018-19 | v2_ewma_hl10 against B2 | 361 | +0.7% [-16.9, +14.0] | +0.02562 [-0.6268, +0.6056] | undecided |
| 2018-19 | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 361 | -11.6% [-24.4, -4.9] | -0.3934 [-0.914, -0.1445] | loss |
| 2018-19 | v2_ewma_hl3 against B1 | 361 | +25.4% [+17.6, +43.7] | +1.343 [+0.4617, +6.592] | gain |
| 2018-19 | v2_ewma_hl3 against B1p | 361 | -2.6% [-24.4, +11.9] | -0.1005 [-0.8159, +0.4428] | undecided |
| 2018-19 | v2_ewma_hl3 against B2 | 361 | -3.2% [-30.5, +11.4] | -0.1226 [-1.155, +0.4946] | undecided |
| 2018-19 | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 361 | -16.0% [-42.1, -7.7] | -0.5416 [-2.069, -0.1729] | loss |
| 2018-19 | v2_ewma_hl5 against B1 | 361 | +27.0% [+18.1, +48.4] | +1.425 [+0.4717, +7.264] | gain |
| 2018-19 | v2_ewma_hl5 against B1p | 361 | -0.5% [-17.7, +14.1] | -0.01898 [-0.5657, +0.531] | undecided |
| 2018-19 | v2_ewma_hl5 against B2 | 361 | -1.1% [-23.6, +12.9] | -0.04107 [-0.8862, +0.5543] | undecided |
| 2018-19 | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 361 | -13.6% [-34.0, -6.3] | -0.4601 [-1.489, -0.146] | loss |
| 2018-19 | v2_ewma_hl5_asym against B1 | 361 | +27.3% [+18.5, +48.8] | +1.442 [+0.4846, +7.494] | gain |
| 2018-19 | v2_ewma_hl5_asym against B1p | 361 | -0.1% [-16.8, +14.3] | -0.002199 [-0.5293, +0.536] | undecided |
| 2018-19 | v2_ewma_hl5_asym against B2 | 361 | -0.6% [-22.5, +13.2] | -0.0243 [-0.838, +0.5604] | undecided |
| 2018-19 | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 361 | -13.1% [-32.0, -6.1] | -0.4433 [-1.407, -0.1409] | loss |
| 2018-19 | v3_miss against B1 | 361 | +35.7% [+25.5, +59.9] | +1.885 [+0.6737, +8.795] | gain |
| 2018-19 | v3_miss against B1p | 361 | +11.5% [-0.3, +30.8] | +0.4413 [+0.08174, +1.361] | gain (was undecided) |
| 2018-19 | v3_miss against B2 | 361 | +11.0% [-1.1, +24.2] | +0.4192 [+0.03092, +0.8783] | gain (was undecided) |
| 2018-19 | v3_miss against spread_mr_fhs_mad20_f0.5 | 361 | +0.0% [-0.3, +0.2] | +0.000162 [-0.007851, +0.008852] | undecided |
| 2018-19 | v4_v3_miss_cal against B1 | 361 | +36.9% [+26.3, +59.4] | +1.946 [+0.7203, +8.583] | gain |
| 2018-19 | v4_v3_miss_cal against B1p | 361 | +13.1% [+0.8, +30.4] | +0.5025 [+0.1424, +1.356] | gain |
| 2018-19 | v4_v3_miss_cal against B2 | 361 | +12.6% [+0.5, +26.6] | +0.4804 [+0.1248, +0.9273] | gain |
| 2018-19 | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 361 | +1.8% [+0.2, +4.6] | +0.0614 [+0.0192, +0.1612] | gain |

### grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2020 | spread_mr_fhs_mad20_f0.5 against B1 | 251 | +14.6% [+6.4, +22.9] | +0.2409 [+0.09646, +0.5858] | gain |
| 2020 | spread_mr_fhs_mad20_f0.5 against B1p | 251 | +12.6% [+2.7, +27.0] | +0.2022 [+0.02117, +0.7189] | gain |
| 2020 | spread_mr_fhs_mad20_f0.5 against B2 | 251 | +49.7% [+24.7, +70.6] | +1.39 [+0.5512, +3.136] | gain |
| 2020 | v1_blend5_20 against B1 | 251 | +17.0% [+8.8, +25.8] | +0.2798 [+0.1192, +0.7033] | gain |
| 2020 | v1_blend5_20 against B1p | 251 | +15.0% [+4.7, +30.0] | +0.2412 [+0.0415, +0.8486] | gain |
| 2020 | v1_blend5_20 against B2 | 251 | +51.1% [+28.0, +72.0] | +1.429 [+0.5779, +3.222] | gain |
| 2020 | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 251 | +2.8% [+1.0, +5.5] | +0.03897 [+0.009539, +0.114] | gain |
| 2020 | v1_mad10 against B1 | 251 | +18.1% [+10.5, +28.1] | +0.2986 [+0.1305, +0.8135] | gain |
| 2020 | v1_mad10 against B1p | 251 | +16.1% [+5.9, +32.9] | +0.2599 [+0.05066, +0.9758] | gain |
| 2020 | v1_mad10 against B2 | 251 | +51.7% [+29.2, +72.4] | +1.447 [+0.5871, +3.285] | gain |
| 2020 | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 251 | +4.1% [+1.4, +8.7] | +0.05771 [+0.01144, +0.2155] | gain |
| 2020 | v1_mad5 against B1 | 251 | +12.3% [+1.4, +20.8] | +0.2023 [+0.04879, +0.4867] | gain |
| 2020 | v1_mad5 against B1p | 251 | +10.2% [-1.6, +24.4] | +0.1636 [-0.01985, +0.594] | undecided |
| 2020 | v1_mad5 against B2 | 251 | +48.3% [+24.3, +70.5] | +1.351 [+0.5341, +3.103] | gain |
| 2020 | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 251 | -2.7% [-7.9, +1.3] | -0.0386 [-0.1204, +0.008302] | undecided |
| 2020 | v2_ewma_hl10 against B1 | 251 | +15.5% [+6.1, +22.8] | +0.255 [+0.1127, +0.5241] | gain |
| 2020 | v2_ewma_hl10 against B1p | 251 | +13.4% [+3.8, +24.6] | +0.2164 [+0.04541, +0.6141] | gain |
| 2020 | v2_ewma_hl10 against B2 | 251 | +50.2% [+23.7, +69.8] | +1.404 [+0.5848, +3.071] | gain |
| 2020 | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 251 | +1.0% [-2.5, +5.1] | +0.01417 [-0.03536, +0.06213] | undecided |
| 2020 | v2_ewma_hl3 against B1 | 251 | +18.0% [+8.8, +25.9] | +0.2964 [+0.1345, +0.6618] | gain |
| 2020 | v2_ewma_hl3 against B1p | 251 | +16.0% [+5.6, +28.7] | +0.2578 [+0.05942, +0.7875] | gain |
| 2020 | v2_ewma_hl3 against B2 | 251 | +51.7% [+28.5, +71.7] | +1.445 [+0.608, +3.198] | gain |
| 2020 | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 251 | +3.9% [+1.0, +6.8] | +0.05556 [+0.01895, +0.112] | gain |
| 2020 | v2_ewma_hl5 against B1 | 251 | +17.5% [+8.3, +25.7] | +0.289 [+0.1279, +0.6475] | gain |
| 2020 | v2_ewma_hl5 against B1p | 251 | +15.6% [+5.2, +28.5] | +0.2504 [+0.05518, +0.7639] | gain |
| 2020 | v2_ewma_hl5 against B2 | 251 | +51.4% [+27.7, +71.0] | +1.438 [+0.6044, +3.179] | gain |
| 2020 | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 251 | +3.4% [+0.7, +6.1] | +0.04815 [+0.01067, +0.09571] | gain |
| 2020 | v2_ewma_hl5_asym against B1 | 251 | +18.0% [+9.2, +26.2] | +0.2975 [+0.1362, +0.6732] | gain |
| 2020 | v2_ewma_hl5_asym against B1p | 251 | +16.1% [+6.0, +29.1] | +0.2588 [+0.06234, +0.8003] | gain |
| 2020 | v2_ewma_hl5_asym against B2 | 251 | +51.7% [+28.1, +71.3] | +1.446 [+0.6082, +3.2] | gain |
| 2020 | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 251 | +4.0% [+1.4, +6.6] | +0.05659 [+0.01746, +0.1085] | gain |
| 2020 | v3_miss against B1 | 251 | +14.6% [+6.3, +22.9] | +0.2414 [+0.09638, +0.5821] | gain |
| 2020 | v3_miss against B1p | 251 | +12.6% [+2.7, +26.8] | +0.2028 [+0.02067, +0.712] | gain |
| 2020 | v3_miss against B2 | 251 | +49.7% [+24.8, +70.6] | +1.39 [+0.5524, +3.131] | gain |
| 2020 | v3_miss against spread_mr_fhs_mad20_f0.5 | 251 | +0.0% [-0.4, +0.4] | +0.0005591 [-0.0053, +0.005001] | undecided |
| 2020 | v4_v3_miss_cal against B1 | 251 | +12.7% [+4.3, +21.1] | +0.2099 [+0.0721, +0.5034] | gain |
| 2020 | v4_v3_miss_cal against B1p | 251 | +10.6% [+0.7, +25.0] | +0.1713 [+0.0003153, +0.6185] | gain |
| 2020 | v4_v3_miss_cal against B2 | 251 | +48.6% [+22.7, +70.0] | +1.359 [+0.5231, +3.104] | gain |
| 2020 | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 251 | -2.2% [-3.7, -1.0] | -0.03094 [-0.06546, -0.00852] | loss |

### scaled_grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2020 | spread_mr_fhs_mad20_f0.5 against B1 | 251 | +15.3% [+8.0, +24.2] | +0.1186 [+0.04986, +0.3034] | gain |
| 2020 | spread_mr_fhs_mad20_f0.5 against B1p | 251 | +12.6% [+2.7, +29.2] | +0.09407 [+0.007873, +0.3691] | gain |
| 2020 | spread_mr_fhs_mad20_f0.5 against B2 | 251 | +43.8% [+17.7, +65.8] | +0.5108 [+0.1881, +1.097] | gain |
| 2020 | v1_blend5_20 against B1 | 251 | +17.7% [+10.1, +27.3] | +0.1372 [+0.05901, +0.3569] | gain |
| 2020 | v1_blend5_20 against B1p | 251 | +15.0% [+4.4, +32.0] | +0.1127 [+0.01594, +0.4269] | gain |
| 2020 | v1_blend5_20 against B2 | 251 | +45.4% [+21.0, +67.4] | +0.5295 [+0.2007, +1.13] | gain |
| 2020 | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 251 | +2.8% [+0.9, +5.5] | +0.01866 [+0.004484, +0.05151] | gain |
| 2020 | v1_mad10 against B1 | 251 | +18.8% [+11.5, +29.7] | +0.1458 [+0.06333, +0.4124] | gain |
| 2020 | v1_mad10 against B1p | 251 | +16.2% [+5.4, +35.5] | +0.1213 [+0.02022, +0.4945] | gain |
| 2020 | v1_mad10 against B2 | 251 | +46.1% [+22.3, +67.8] | +0.5381 [+0.2055, +1.148] | gain |
| 2020 | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 251 | +4.2% [+1.4, +8.7] | +0.02725 [+0.005873, +0.09814] | gain |
| 2020 | v1_mad5 against B1 | 251 | +13.3% [+4.2, +22.0] | +0.1026 [+0.03214, +0.2528] | gain |
| 2020 | v1_mad5 against B1p | 251 | +10.4% [-0.8, +26.0] | +0.07814 [-0.007714, +0.3034] | undecided |
| 2020 | v1_mad5 against B2 | 251 | +42.4% [+17.7, +65.8] | +0.4949 [+0.1802, +1.082] | gain |
| 2020 | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 251 | -2.4% [-7.4, +1.6] | -0.01594 [-0.05074, +0.005535] | undecided |
| 2020 | v2_ewma_hl10 against B1 | 251 | +16.5% [+8.2, +23.9] | +0.1274 [+0.05993, +0.2669] | gain |
| 2020 | v2_ewma_hl10 against B1p | 251 | +13.7% [+4.4, +25.9] | +0.1029 [+0.02036, +0.307] | gain |
| 2020 | v2_ewma_hl10 against B2 | 251 | +44.6% [+16.7, +65.5] | +0.5197 [+0.2013, +1.07] | gain |
| 2020 | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 251 | +1.4% [-2.4, +5.9] | +0.008869 [-0.0153, +0.03286] | undecided |
| 2020 | v2_ewma_hl3 against B1 | 251 | +18.9% [+10.7, +27.0] | +0.1462 [+0.06799, +0.3343] | gain |
| 2020 | v2_ewma_hl3 against B1p | 251 | +16.2% [+5.9, +30.0] | +0.1217 [+0.02678, +0.3888] | gain |
| 2020 | v2_ewma_hl3 against B2 | 251 | +46.2% [+21.9, +67.2] | +0.5385 [+0.216, +1.118] | gain |
| 2020 | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 251 | +4.2% [+1.1, +7.2] | +0.02761 [+0.008685, +0.05487] | gain |
| 2020 | v2_ewma_hl5 against B1 | 251 | +18.4% [+10.1, +26.8] | +0.1427 [+0.0652, +0.3264] | gain |
| 2020 | v2_ewma_hl5 against B1p | 251 | +15.8% [+5.5, +29.8] | +0.1182 [+0.02369, +0.3787] | gain |
| 2020 | v2_ewma_hl5 against B2 | 251 | +45.9% [+21.0, +66.6] | +0.535 [+0.2119, +1.103] | gain |
| 2020 | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 251 | +3.7% [+0.7, +6.6] | +0.02416 [+0.004767, +0.04739] | gain |
| 2020 | v2_ewma_hl5_asym against B1 | 251 | +18.9% [+10.7, +27.3] | +0.1462 [+0.06798, +0.3385] | gain |
| 2020 | v2_ewma_hl5_asym against B1p | 251 | +16.2% [+6.1, +30.5] | +0.1217 [+0.02644, +0.394] | gain |
| 2020 | v2_ewma_hl5_asym against B2 | 251 | +46.2% [+21.4, +66.8] | +0.5385 [+0.2139, +1.112] | gain |
| 2020 | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 251 | +4.2% [+1.2, +7.0] | +0.02763 [+0.007455, +0.05271] | gain |
| 2020 | v3_miss against B1 | 251 | +15.3% [+8.0, +24.2] | +0.1187 [+0.04949, +0.3] | gain |
| 2020 | v3_miss against B1p | 251 | +12.6% [+2.6, +28.9] | +0.09422 [+0.007607, +0.3632] | gain |
| 2020 | v3_miss against B2 | 251 | +43.8% [+17.8, +65.8] | +0.511 [+0.1887, +1.095] | gain |
| 2020 | v3_miss against spread_mr_fhs_mad20_f0.5 | 251 | +0.0% [-0.4, +0.3] | +0.0001408 [-0.002886, +0.002271] | undecided |
| 2020 | v4_v3_miss_cal against B1 | 251 | +15.1% [+8.0, +23.3] | +0.1171 [+0.0527, +0.2783] | gain |
| 2020 | v4_v3_miss_cal against B1p | 251 | +12.4% [+3.3, +27.4] | +0.09257 [+0.01124, +0.3371] | gain |
| 2020 | v4_v3_miss_cal against B2 | 251 | +43.7% [+16.2, +65.8] | +0.5093 [+0.1889, +1.086] | gain |
| 2020 | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 251 | -0.2% [-2.4, +1.4] | -0.001508 [-0.01761, +0.007039] | undecided |

### upper_tail_twcrps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2020 | spread_mr_fhs_mad20_f0.5 against B1 | 251 | +31.0% [+17.0, +56.4] | +0.2293 [+0.05468, +1.643] | gain |
| 2020 | spread_mr_fhs_mad20_f0.5 against B1p | 251 | +32.1% [+19.2, +64.1] | +0.2412 [+0.03441, +2.184] | gain |
| 2020 | spread_mr_fhs_mad20_f0.5 against B2 | 251 | +58.1% [-23.6, +84.3] | +0.7083 [+0.358, +1.139] | gain (was undecided) |
| 2020 | v1_blend5_20 against B1 | 251 | +31.8% [+21.7, +46.1] | +0.2356 [+0.07025, +1.649] | gain |
| 2020 | v1_blend5_20 against B1p | 251 | +32.9% [+23.8, +52.5] | +0.2475 [+0.04805, +2.166] | gain |
| 2020 | v1_blend5_20 against B2 | 251 | +58.6% [-14.8, +85.3] | +0.7146 [+0.3732, +1.14] | gain (was undecided) |
| 2020 | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 251 | +1.2% [-19.4, +7.0] | +0.006334 [-0.05017, +0.03828] | undecided |
| 2020 | v1_mad10 against B1 | 251 | +32.5% [+21.6, +48.7] | +0.2404 [+0.06777, +1.605] | gain |
| 2020 | v1_mad10 against B1p | 251 | +33.5% [+23.7, +55.0] | +0.2522 [+0.04507, +2.087] | gain |
| 2020 | v1_mad10 against B2 | 251 | +59.0% [-14.2, +85.4] | +0.7193 [+0.3767, +1.145] | gain (was undecided) |
| 2020 | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 251 | +2.2% [-10.3, +7.2] | +0.01107 [-0.02163, +0.04423] | undecided |
| 2020 | v1_mad5 against B1 | 251 | +24.1% [+16.3, +36.7] | +0.1786 [+0.03789, +1.185] | gain |
| 2020 | v1_mad5 against B1p | 251 | +25.3% [+15.8, +44.3] | +0.1904 [+0.01466, +1.625] | gain |
| 2020 | v1_mad5 against B2 | 251 | +53.9% [-16.8, +82.1] | +0.6576 [+0.315, +1.064] | gain (was undecided) |
| 2020 | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 251 | -9.9% [-48.0, +6.7] | -0.05072 [-0.2754, +0.01215] | undecided |
| 2020 | v2_ewma_hl10 against B1 | 251 | +36.2% [+5.4, +51.7] | +0.2683 [+0.1101, +1.37] | gain |
| 2020 | v2_ewma_hl10 against B1p | 251 | +37.3% [+15.1, +53.5] | +0.2801 [+0.0911, +1.907] | gain |
| 2020 | v2_ewma_hl10 against B2 | 251 | +61.3% [-54.0, +89.0] | +0.7472 [+0.4138, +1.15] | gain (was undecided) |
| 2020 | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 251 | +7.6% [-16.1, +29.9] | +0.03896 [-0.01596, +0.08357] | undecided |
| 2020 | v2_ewma_hl3 against B1 | 251 | +35.7% [+16.7, +45.6] | +0.2639 [+0.1124, +1.312] | gain |
| 2020 | v2_ewma_hl3 against B1p | 251 | +36.7% [+23.0, +46.3] | +0.2758 [+0.09223, +1.816] | gain |
| 2020 | v2_ewma_hl3 against B2 | 251 | +60.9% [-29.0, +89.4] | +0.7429 [+0.4136, +1.147] | gain (was undecided) |
| 2020 | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 251 | +6.8% [-24.6, +18.7] | +0.03463 [-0.0799, +0.08703] | undecided |
| 2020 | v2_ewma_hl5 against B1 | 251 | +36.8% [+13.5, +48.9] | +0.2725 [+0.1153, +1.388] | gain |
| 2020 | v2_ewma_hl5 against B1p | 251 | +37.8% [+20.9, +50.1] | +0.2844 [+0.09487, +1.891] | gain |
| 2020 | v2_ewma_hl5 against B2 | 251 | +61.6% [-33.5, +89.5] | +0.7515 [+0.4245, +1.156] | gain (was undecided) |
| 2020 | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 251 | +8.5% [-15.6, +21.9] | +0.04319 [-0.0324, +0.08659] | undecided |
| 2020 | v2_ewma_hl5_asym against B1 | 251 | +37.6% [+13.1, +49.9] | +0.2784 [+0.119, +1.464] | gain |
| 2020 | v2_ewma_hl5_asym against B1p | 251 | +38.6% [+21.0, +50.9] | +0.2902 [+0.09775, +1.985] | gain |
| 2020 | v2_ewma_hl5_asym against B2 | 251 | +62.1% [-35.2, +89.9] | +0.7573 [+0.4309, +1.162] | gain (was undecided) |
| 2020 | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 251 | +9.6% [-14.9, +23.9] | +0.04905 [-0.01652, +0.09054] | undecided |
| 2020 | v3_miss against B1 | 251 | +30.7% [+16.9, +56.0] | +0.227 [+0.05267, +1.605] | gain |
| 2020 | v3_miss against B1p | 251 | +31.8% [+18.9, +63.7] | +0.2389 [+0.03244, +2.15] | gain |
| 2020 | v3_miss against B2 | 251 | +57.9% [-22.7, +84.2] | +0.706 [+0.3555, +1.137] | gain (was undecided) |
| 2020 | v3_miss against spread_mr_fhs_mad20_f0.5 | 251 | -0.4% [-1.2, +0.3] | -0.002282 [-0.005422, -0.0005673] | loss (was undecided) |
| 2020 | v4_v3_miss_cal against B1 | 251 | +28.5% [+13.9, +52.1] | +0.2111 [+0.04964, +1.268] | gain |
| 2020 | v4_v3_miss_cal against B1p | 251 | +29.6% [+16.4, +59.5] | +0.2229 [+0.0304, +1.817] | gain |
| 2020 | v4_v3_miss_cal against B2 | 251 | +56.6% [-30.1, +83.9] | +0.69 [+0.3353, +1.118] | gain (was undecided) |
| 2020 | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 251 | -3.6% [-6.8, -1.2] | -0.01825 [-0.05412, +0.00225] | undecided (was loss) |

### grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2021-23 | spread_mr_fhs_mad20_f0.5 against B1 | 748 | +5.5% [-0.6, +10.5] | +0.03824 [-0.0002371, +0.07008] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f0.5 against B1p | 748 | +1.0% [-5.3, +6.5] | +0.006723 [-0.03535, +0.04172] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f0.5 against B2 | 748 | +55.0% [+41.1, +67.8] | +0.8061 [+0.5082, +1.202] | gain |
| 2021-23 | v1_blend5_20 against B1 | 748 | +6.0% [-0.7, +11.1] | +0.04153 [-0.0009311, +0.07395] | undecided |
| 2021-23 | v1_blend5_20 against B1p | 748 | +1.5% [-5.3, +7.0] | +0.01002 [-0.03633, +0.04496] | undecided |
| 2021-23 | v1_blend5_20 against B2 | 748 | +55.2% [+41.2, +68.0] | +0.8094 [+0.5104, +1.211] | gain |
| 2021-23 | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 748 | +0.5% [-1.3, +2.1] | +0.003293 [-0.007293, +0.01343] | undecided |
| 2021-23 | v1_mad10 against B1 | 748 | +5.9% [-0.4, +10.9] | +0.04095 [+0.0005034, +0.0729] | gain (was undecided) |
| 2021-23 | v1_mad10 against B1p | 748 | +1.4% [-5.2, +6.8] | +0.009439 [-0.03453, +0.04383] | undecided |
| 2021-23 | v1_mad10 against B2 | 748 | +55.2% [+41.3, +67.9] | +0.8088 [+0.5106, +1.21] | gain |
| 2021-23 | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 748 | +0.4% [-1.5, +2.5] | +0.002717 [-0.008731, +0.01654] | undecided |
| 2021-23 | v1_mad5 against B1 | 748 | +4.7% [-2.1, +9.7] | +0.0328 [-0.0118, +0.06571] | undecided |
| 2021-23 | v1_mad5 against B1p | 748 | +0.2% [-6.9, +5.6] | +0.001288 [-0.04667, +0.03671] | undecided |
| 2021-23 | v1_mad5 against B2 | 748 | +54.6% [+40.4, +67.4] | +0.8006 [+0.5001, +1.2] | gain |
| 2021-23 | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 748 | -0.8% [-3.3, +2.2] | -0.005435 [-0.02067, +0.01298] | undecided |
| 2021-23 | v2_ewma_hl10 against B1 | 748 | +7.3% [-0.3, +13.3] | +0.05103 [+0.003498, +0.08757] | gain (was undecided) |
| 2021-23 | v2_ewma_hl10 against B1p | 748 | +2.9% [-4.7, +9.2] | +0.01951 [-0.03095, +0.05839] | undecided |
| 2021-23 | v2_ewma_hl10 against B2 | 748 | +55.9% [+41.7, +68.8] | +0.8189 [+0.5188, +1.216] | gain |
| 2021-23 | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 748 | +1.9% [-0.4, +3.6] | +0.01279 [-0.0003114, +0.02189] | undecided |
| 2021-23 | v2_ewma_hl3 against B1 | 748 | +6.8% [-0.5, +12.2] | +0.04715 [+0.001457, +0.08132] | gain (was undecided) |
| 2021-23 | v2_ewma_hl3 against B1p | 748 | +2.3% [-5.0, +8.0] | +0.01564 [-0.03303, +0.0518] | undecided |
| 2021-23 | v2_ewma_hl3 against B2 | 748 | +55.6% [+41.6, +68.5] | +0.815 [+0.5154, +1.215] | gain |
| 2021-23 | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 748 | +1.4% [-1.3, +3.2] | +0.008914 [-0.006656, +0.02079] | undecided |
| 2021-23 | v2_ewma_hl5 against B1 | 748 | +7.2% [-0.2, +12.8] | +0.05009 [+0.004435, +0.08524] | gain (was undecided) |
| 2021-23 | v2_ewma_hl5 against B1p | 748 | +2.8% [-4.6, +8.7] | +0.01858 [-0.03058, +0.05568] | undecided |
| 2021-23 | v2_ewma_hl5 against B2 | 748 | +55.8% [+41.8, +68.7] | +0.8179 [+0.5179, +1.218] | gain |
| 2021-23 | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 748 | +1.8% [-0.4, +3.3] | +0.01186 [-0.0009336, +0.02123] | undecided |
| 2021-23 | v2_ewma_hl5_asym against B1 | 748 | +6.7% [-1.1, +12.7] | +0.04684 [-0.002456, +0.08407] | undecided |
| 2021-23 | v2_ewma_hl5_asym against B1p | 748 | +2.3% [-5.5, +8.5] | +0.01533 [-0.03629, +0.05393] | undecided |
| 2021-23 | v2_ewma_hl5_asym against B2 | 748 | +55.6% [+41.3, +68.6] | +0.8147 [+0.5156, +1.212] | gain |
| 2021-23 | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 748 | +1.3% [-1.3, +3.1] | +0.008605 [-0.006583, +0.01899] | undecided |
| 2021-23 | v3_miss against B1 | 748 | +6.4% [+0.3, +11.4] | +0.04462 [+0.006598, +0.07644] | gain |
| 2021-23 | v3_miss against B1p | 748 | +2.0% [-4.3, +7.3] | +0.0131 [-0.02858, +0.04757] | undecided |
| 2021-23 | v3_miss against B2 | 748 | +55.4% [+41.7, +68.1] | +0.8124 [+0.5151, +1.209] | gain |
| 2021-23 | v3_miss against spread_mr_fhs_mad20_f0.5 | 748 | +1.0% [+0.1, +2.1] | +0.006382 [+0.001007, +0.01535] | gain |
| 2021-23 | v4_v3_miss_cal against B1 | 748 | +6.5% [+0.6, +11.4] | +0.04522 [+0.008679, +0.07615] | gain |
| 2021-23 | v4_v3_miss_cal against B1p | 748 | +2.1% [-4.1, +7.3] | +0.0137 [-0.02696, +0.04754] | undecided |
| 2021-23 | v4_v3_miss_cal against B2 | 748 | +55.5% [+41.8, +68.0] | +0.813 [+0.5152, +1.21] | gain |
| 2021-23 | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 748 | +1.1% [+0.1, +2.1] | +0.006979 [+0.0007026, +0.01553] | gain |

### scaled_grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2021-23 | spread_mr_fhs_mad20_f0.5 against B1 | 748 | +4.9% [+0.5, +8.7] | +0.04088 [+0.006065, +0.07505] | gain |
| 2021-23 | spread_mr_fhs_mad20_f0.5 against B1p | 748 | -1.0% [-6.0, +3.7] | -0.007506 [-0.04596, +0.02822] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f0.5 against B2 | 748 | +43.9% [+30.3, +56.3] | +0.6224 [+0.4005, +0.8796] | gain |
| 2021-23 | v1_blend5_20 against B1 | 748 | +5.4% [+0.9, +9.3] | +0.04475 [+0.009991, +0.08041] | gain |
| 2021-23 | v1_blend5_20 against B1p | 748 | -0.5% [-5.4, +4.0] | -0.003635 [-0.04219, +0.03169] | undecided |
| 2021-23 | v1_blend5_20 against B2 | 748 | +44.2% [+30.5, +56.7] | +0.6262 [+0.4037, +0.8873] | gain |
| 2021-23 | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 748 | +0.5% [-1.1, +1.9] | +0.003871 [-0.007375, +0.01446] | undecided |
| 2021-23 | v1_mad10 against B1 | 748 | +5.2% [+0.8, +9.0] | +0.04312 [+0.009181, +0.07805] | gain |
| 2021-23 | v1_mad10 against B1p | 748 | -0.7% [-5.5, +3.7] | -0.005261 [-0.04292, +0.02901] | undecided |
| 2021-23 | v1_mad10 against B2 | 748 | +44.1% [+30.5, +56.7] | +0.6246 [+0.4037, +0.8864] | gain |
| 2021-23 | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 748 | +0.3% [-1.7, +2.3] | +0.002246 [-0.01221, +0.01793] | undecided |
| 2021-23 | v1_mad5 against B1 | 748 | +3.9% [-0.6, +7.9] | +0.03269 [-0.002357, +0.06829] | undecided |
| 2021-23 | v1_mad5 against B1p | 748 | -2.0% [-7.2, +2.6] | -0.01569 [-0.05641, +0.02091] | undecided |
| 2021-23 | v1_mad5 against B2 | 748 | +43.3% [+29.5, +56.1] | +0.6142 [+0.3899, +0.8782] | gain |
| 2021-23 | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 748 | -1.0% [-3.3, +1.5] | -0.008184 [-0.02516, +0.01086] | undecided |
| 2021-23 | v2_ewma_hl10 against B1 | 748 | +6.9% [+1.8, +11.2] | +0.05733 [+0.01873, +0.09694] | gain |
| 2021-23 | v2_ewma_hl10 against B1p | 748 | +1.1% [-4.3, +6.1] | +0.008953 [-0.03258, +0.04828] | undecided |
| 2021-23 | v2_ewma_hl10 against B2 | 748 | +45.1% [+31.6, +57.5] | +0.6388 [+0.4154, +0.8995] | gain |
| 2021-23 | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 748 | +2.1% [+0.6, +3.4] | +0.01646 [+0.005649, +0.02751] | gain |
| 2021-23 | v2_ewma_hl3 against B1 | 748 | +6.4% [+1.7, +10.5] | +0.05341 [+0.0173, +0.09127] | gain |
| 2021-23 | v2_ewma_hl3 against B1p | 748 | +0.6% [-4.7, +5.2] | +0.00503 [-0.03517, +0.04166] | undecided |
| 2021-23 | v2_ewma_hl3 against B2 | 748 | +44.8% [+31.3, +57.2] | +0.6349 [+0.4123, +0.8971] | gain |
| 2021-23 | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 748 | +1.6% [-0.5, +3.4] | +0.01254 [-0.002507, +0.02762] | undecided |
| 2021-23 | v2_ewma_hl5 against B1 | 748 | +6.7% [+1.9, +10.9] | +0.05624 [+0.0196, +0.09464] | gain |
| 2021-23 | v2_ewma_hl5 against B1p | 748 | +1.0% [-4.4, +5.7] | +0.007858 [-0.03258, +0.04584] | undecided |
| 2021-23 | v2_ewma_hl5 against B2 | 748 | +45.0% [+31.5, +57.4] | +0.6377 [+0.4159, +0.8984] | gain |
| 2021-23 | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 748 | +1.9% [+0.3, +3.4] | +0.01536 [+0.003512, +0.0278] | gain |
| 2021-23 | v2_ewma_hl5_asym against B1 | 748 | +6.5% [+1.2, +11.0] | +0.05397 [+0.01456, +0.09525] | gain |
| 2021-23 | v2_ewma_hl5_asym against B1p | 748 | +0.7% [-5.0, +5.9] | +0.005592 [-0.03729, +0.04627] | undecided |
| 2021-23 | v2_ewma_hl5_asym against B2 | 748 | +44.8% [+31.3, +57.3] | +0.6355 [+0.4119, +0.8964] | gain |
| 2021-23 | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 748 | +1.6% [-0.1, +3.3] | +0.0131 [+0.000546, +0.02628] | gain (was undecided) |
| 2021-23 | v3_miss against B1 | 748 | +5.7% [+1.4, +9.5] | +0.04736 [+0.01358, +0.08388] | gain |
| 2021-23 | v3_miss against B1p | 748 | -0.1% [-5.0, +4.5] | -0.001018 [-0.03797, +0.03541] | undecided |
| 2021-23 | v3_miss against B2 | 748 | +44.4% [+30.9, +56.7] | +0.6288 [+0.4071, +0.8874] | gain |
| 2021-23 | v3_miss against spread_mr_fhs_mad20_f0.5 | 748 | +0.8% [-0.1, +2.0] | +0.006488 [-0.0003378, +0.01718] | undecided |
| 2021-23 | v4_v3_miss_cal against B1 | 748 | +5.8% [+1.5, +9.6] | +0.0481 [+0.01486, +0.08404] | gain |
| 2021-23 | v4_v3_miss_cal against B1p | 748 | -0.0% [-5.0, +4.6] | -0.0002776 [-0.03777, +0.03613] | undecided |
| 2021-23 | v4_v3_miss_cal against B2 | 748 | +44.4% [+30.9, +56.8] | +0.6296 [+0.4072, +0.8891] | gain |
| 2021-23 | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 748 | +0.9% [+0.0, +2.0] | +0.007229 [+0.000307, +0.01654] | gain |

### upper_tail_twcrps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2021-23 | spread_mr_fhs_mad20_f0.5 against B1 | 748 | +12.3% [-63.3, +44.0] | +0.0011 [-0.003811, +0.003373] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f0.5 against B1p | 748 | -16.5% [-104.6, +16.1] | -0.001111 [-0.009788, +0.001218] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f0.5 against B2 | 748 | -156.2% [-792.6, -37.3] | -0.004779 [-0.04745, +0.0002712] | undecided (was loss) |
| 2021-23 | v1_blend5_20 against B1 | 748 | +27.5% [-11.4, +57.1] | +0.002463 [+0.0007232, +0.004895] | gain (was undecided) |
| 2021-23 | v1_blend5_20 against B1p | 748 | +3.7% [-33.3, +25.3] | +0.0002518 [-0.001847, +0.001542] | undecided |
| 2021-23 | v1_blend5_20 against B2 | 748 | -111.7% [-433.5, -29.0] | -0.003417 [-0.0274, +0.0003189] | undecided (was loss) |
| 2021-23 | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 748 | +17.4% [+4.0, +51.2] | +0.001362 [-4.525e-05, +0.01286] | undecided (was gain) |
| 2021-23 | v1_mad10 against B1 | 748 | +27.3% [-37.6, +57.7] | +0.002438 [+0.0002383, +0.00462] | gain (was undecided) |
| 2021-23 | v1_mad10 against B1p | 748 | +3.4% [-56.8, +27.6] | +0.0002267 [-0.002998, +0.001626] | undecided |
| 2021-23 | v1_mad10 against B2 | 748 | -112.5% [-621.9, -17.6] | -0.003442 [-0.03919, +0.0005596] | undecided (was loss) |
| 2021-23 | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 748 | +17.1% [+2.8, +35.2] | +0.001337 [+0.0002084, +0.006984] | gain |
| 2021-23 | v1_mad5 against B1 | 748 | +10.6% [-20.2, +35.6] | +0.0009518 [-0.001529, +0.003233] | undecided |
| 2021-23 | v1_mad5 against B1p | 748 | -18.7% [-63.1, +9.8] | -0.001259 [-0.005014, +0.0006721] | undecided |
| 2021-23 | v1_mad5 against B2 | 748 | -161.0% [-353.1, -60.0] | -0.004927 [-0.02238, -0.0005906] | loss |
| 2021-23 | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 748 | -1.9% [-34.2, +40.8] | -0.0001484 [-0.001809, +0.003112] | undecided |
| 2021-23 | v2_ewma_hl10 against B1 | 748 | +67.8% [-12.7, +84.4] | +0.006065 [+0.002707, +0.0162] | gain (was undecided) |
| 2021-23 | v2_ewma_hl10 against B1p | 748 | +57.3% [-10.6, +71.8] | +0.003854 [+0.001546, +0.01244] | gain (was undecided) |
| 2021-23 | v2_ewma_hl10 against B2 | 748 | +6.1% [-351.1, +53.8] | +0.0001859 [-0.002772, +0.001405] | undecided |
| 2021-23 | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 748 | +63.3% [-45.8, +78.1] | +0.004965 [+0.0005857, +0.0277] | gain (was undecided) |
| 2021-23 | v2_ewma_hl3 against B1 | 748 | +49.5% [+6.9, +75.3] | +0.004422 [+0.001928, +0.009348] | gain |
| 2021-23 | v2_ewma_hl3 against B1p | 748 | +32.9% [+0.6, +50.5] | +0.002211 [+0.0008474, +0.004997] | gain |
| 2021-23 | v2_ewma_hl3 against B2 | 748 | -47.6% [-303.7, +9.1] | -0.001458 [-0.01364, +0.0007256] | undecided |
| 2021-23 | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 748 | +42.4% [-6.5, +67.7] | +0.003322 [+8.999e-05, +0.01849] | gain (was undecided) |
| 2021-23 | v2_ewma_hl5 against B1 | 748 | +58.7% [-1.3, +80.6] | +0.00525 [+0.002403, +0.01239] | gain (was undecided) |
| 2021-23 | v2_ewma_hl5 against B1p | 748 | +45.2% [-3.1, +62.1] | +0.003039 [+0.001288, +0.008238] | gain (was undecided) |
| 2021-23 | v2_ewma_hl5 against B2 | 748 | -20.6% [-318.6, +31.5] | -0.0006295 [-0.008042, +0.001075] | undecided |
| 2021-23 | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 748 | +52.9% [-12.9, +73.2] | +0.00415 [+0.0003931, +0.02243] | gain (was undecided) |
| 2021-23 | v2_ewma_hl5_asym against B1 | 748 | +59.4% [-2.0, +81.4] | +0.005306 [+0.00226, +0.01247] | gain (was undecided) |
| 2021-23 | v2_ewma_hl5_asym against B1p | 748 | +46.0% [-3.4, +64.6] | +0.003096 [+0.001157, +0.008526] | gain (was undecided) |
| 2021-23 | v2_ewma_hl5_asym against B2 | 748 | -18.7% [-288.7, +33.4] | -0.0005728 [-0.006919, +0.001096] | undecided |
| 2021-23 | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 748 | +53.7% [-5.4, +78.4] | +0.004206 [+0.000262, +0.02263] | gain (was undecided) |
| 2021-23 | v3_miss against B1 | 748 | +8.0% [-64.6, +38.8] | +0.000714 [-0.004455, +0.003077] | undecided |
| 2021-23 | v3_miss against B1p | 748 | -22.2% [-110.5, +12.2] | -0.001497 [-0.01031, +0.0009377] | undecided |
| 2021-23 | v3_miss against B2 | 748 | -168.8% [-756.7, -47.1] | -0.005165 [-0.04462, -8.599e-06] | loss |
| 2021-23 | v3_miss against spread_mr_fhs_mad20_f0.5 | 748 | -4.9% [-12.2, +0.5] | -0.0003863 [-0.0008024, -0.0001635] | loss (was undecided) |
| 2021-23 | v4_v3_miss_cal against B1 | 748 | +21.8% [-49.4, +47.9] | +0.001945 [-0.001161, +0.004513] | undecided |
| 2021-23 | v4_v3_miss_cal against B1p | 748 | -4.0% [-76.4, +25.9] | -0.0002662 [-0.004385, +0.001537] | undecided |
| 2021-23 | v4_v3_miss_cal against B2 | 748 | -128.6% [-665.4, -25.0] | -0.003935 [-0.03783, +0.0001805] | undecided (was loss) |
| 2021-23 | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 748 | +10.8% [-0.3, +18.8] | +0.0008445 [-0.0002512, +0.004173] | undecided |

### grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2024 | spread_mr_fhs_mad20_f0.5 against B1 | 250 | +25.3% [+18.7, +35.7] | +0.4088 [+0.199, +0.9872] | gain |
| 2024 | spread_mr_fhs_mad20_f0.5 against B1p | 250 | +19.0% [+11.2, +29.8] | +0.2819 [+0.1065, +0.7204] | gain |
| 2024 | spread_mr_fhs_mad20_f0.5 against B2 | 250 | +13.6% [+3.1, +23.2] | +0.19 [+0.03713, +0.3893] | gain |
| 2024 | v1_blend5_20 against B1 | 250 | +24.8% [+18.9, +33.9] | +0.3995 [+0.2016, +0.9793] | gain |
| 2024 | v1_blend5_20 against B1p | 250 | +18.3% [+11.0, +28.6] | +0.2726 [+0.1047, +0.7036] | gain |
| 2024 | v1_blend5_20 against B2 | 250 | +13.0% [+1.2, +23.6] | +0.1807 [+0.01745, +0.3994] | gain |
| 2024 | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 250 | -0.8% [-6.4, +2.8] | -0.009311 [-0.06724, +0.03129] | undecided |
| 2024 | v1_mad10 against B1 | 250 | +25.8% [+19.2, +36.6] | +0.4155 [+0.2027, +1.037] | gain |
| 2024 | v1_mad10 against B1p | 250 | +19.4% [+11.7, +31.0] | +0.2886 [+0.1092, +0.767] | gain |
| 2024 | v1_mad10 against B2 | 250 | +14.1% [+3.0, +24.2] | +0.1967 [+0.03552, +0.4174] | gain |
| 2024 | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 250 | +0.6% [-1.6, +3.8] | +0.00666 [-0.01731, +0.0493] | undecided |
| 2024 | v1_mad5 against B1 | 250 | +22.0% [+16.0, +31.6] | +0.3545 [+0.1694, +0.9074] | gain |
| 2024 | v1_mad5 against B1p | 250 | +15.3% [+7.5, +26.4] | +0.2276 [+0.06833, +0.6436] | gain |
| 2024 | v1_mad5 against B2 | 250 | +9.7% [-4.5, +21.6] | +0.1358 [-0.04583, +0.3627] | undecided |
| 2024 | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 250 | -4.5% [-15.3, +1.5] | -0.05428 [-0.1769, +0.011] | undecided |
| 2024 | v2_ewma_hl10 against B1 | 250 | +24.2% [+18.1, +35.0] | +0.3904 [+0.1901, +1.001] | gain |
| 2024 | v2_ewma_hl10 against B1p | 250 | +17.7% [+10.3, +29.4] | +0.2635 [+0.09458, +0.7311] | gain |
| 2024 | v2_ewma_hl10 against B2 | 250 | +12.3% [+0.4, +23.1] | +0.1717 [+0.005025, +0.3901] | gain |
| 2024 | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 250 | -1.5% [-6.1, +1.1] | -0.01836 [-0.06709, +0.01186] | undecided |
| 2024 | v2_ewma_hl3 against B1 | 250 | +23.6% [+17.8, +34.0] | +0.3814 [+0.1904, +0.9987] | gain |
| 2024 | v2_ewma_hl3 against B1p | 250 | +17.1% [+9.8, +28.7] | +0.2545 [+0.09312, +0.7182] | gain |
| 2024 | v2_ewma_hl3 against B2 | 250 | +11.7% [-0.6, +22.6] | +0.1627 [-0.003731, +0.3799] | undecided |
| 2024 | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 250 | -2.3% [-8.1, +1.7] | -0.02735 [-0.093, +0.01778] | undecided |
| 2024 | v2_ewma_hl5 against B1 | 250 | +24.0% [+18.2, +34.5] | +0.3878 [+0.1926, +0.9997] | gain |
| 2024 | v2_ewma_hl5 against B1p | 250 | +17.6% [+10.3, +29.1] | +0.261 [+0.0962, +0.7256] | gain |
| 2024 | v2_ewma_hl5 against B2 | 250 | +12.1% [+0.1, +22.8] | +0.1691 [+0.002309, +0.3865] | gain |
| 2024 | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 250 | -1.7% [-7.2, +1.4] | -0.02095 [-0.08027, +0.01591] | undecided |
| 2024 | v2_ewma_hl5_asym against B1 | 250 | +24.3% [+18.5, +34.6] | +0.3925 [+0.1959, +1.008] | gain |
| 2024 | v2_ewma_hl5_asym against B1p | 250 | +17.9% [+10.5, +29.3] | +0.2656 [+0.09923, +0.7284] | gain |
| 2024 | v2_ewma_hl5_asym against B2 | 250 | +12.5% [+0.9, +22.8] | +0.1737 [+0.01163, +0.3867] | gain |
| 2024 | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 250 | -1.4% [-6.7, +1.5] | -0.0163 [-0.07189, +0.0176] | undecided |
| 2024 | v3_miss against B1 | 250 | +25.1% [+18.5, +35.5] | +0.4043 [+0.1985, +0.9919] | gain |
| 2024 | v3_miss against B1p | 250 | +18.7% [+11.0, +29.4] | +0.2774 [+0.1054, +0.719] | gain |
| 2024 | v3_miss against B2 | 250 | +13.3% [+2.3, +23.0] | +0.1855 [+0.02936, +0.3862] | gain |
| 2024 | v3_miss against spread_mr_fhs_mad20_f0.5 | 250 | -0.4% [-1.4, +0.3] | -0.004518 [-0.01718, +0.004308] | undecided |
| 2024 | v4_v3_miss_cal against B1 | 250 | +25.6% [+18.7, +36.2] | +0.4124 [+0.2027, +1.012] | gain |
| 2024 | v4_v3_miss_cal against B1p | 250 | +19.2% [+11.5, +30.2] | +0.2855 [+0.1104, +0.7421] | gain |
| 2024 | v4_v3_miss_cal against B2 | 250 | +13.9% [+3.1, +23.5] | +0.1937 [+0.03957, +0.3968] | gain |
| 2024 | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 250 | +0.3% [-0.8, +1.3] | +0.003626 [-0.009523, +0.0154] | undecided |

### scaled_grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2024 | spread_mr_fhs_mad20_f0.5 against B1 | 250 | +24.3% [+17.4, +35.1] | +0.8229 [+0.438, +1.763] | gain |
| 2024 | spread_mr_fhs_mad20_f0.5 against B1p | 250 | +17.7% [+9.7, +28.2] | +0.5496 [+0.2103, +1.255] | gain |
| 2024 | spread_mr_fhs_mad20_f0.5 against B2 | 250 | +16.8% [+3.8, +30.4] | +0.5158 [+0.08249, +1.163] | gain |
| 2024 | v1_blend5_20 against B1 | 250 | +23.7% [+17.6, +32.7] | +0.8004 [+0.4443, +1.693] | gain |
| 2024 | v1_blend5_20 against B1p | 250 | +17.0% [+9.3, +26.3] | +0.5272 [+0.2039, +1.182] | gain |
| 2024 | v1_blend5_20 against B2 | 250 | +16.0% [+2.1, +30.6] | +0.4934 [+0.04173, +1.168] | gain |
| 2024 | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 250 | -0.9% [-6.0, +2.4] | -0.02241 [-0.1446, +0.05826] | undecided |
| 2024 | v1_mad10 against B1 | 250 | +24.6% [+17.9, +35.3] | +0.8314 [+0.4514, +1.824] | gain |
| 2024 | v1_mad10 against B1p | 250 | +17.9% [+10.0, +28.6] | +0.5581 [+0.2201, +1.292] | gain |
| 2024 | v1_mad10 against B2 | 250 | +17.0% [+3.6, +31.3] | +0.5243 [+0.07639, +1.209] | gain |
| 2024 | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 250 | +0.3% [-1.7, +2.9] | +0.008546 [-0.04244, +0.07502] | undecided |
| 2024 | v1_mad5 against B1 | 250 | +20.5% [+14.0, +29.4] | +0.6928 [+0.3575, +1.516] | gain |
| 2024 | v1_mad5 against B1p | 250 | +13.5% [+5.1, +23.4] | +0.4196 [+0.1122, +1.029] | gain |
| 2024 | v1_mad5 against B2 | 250 | +12.5% [-3.4, +27.8] | +0.3858 [-0.08814, +1.049] | undecided |
| 2024 | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 250 | -5.1% [-14.9, +0.4] | -0.13 [-0.3851, +0.004079] | undecided |
| 2024 | v2_ewma_hl10 against B1 | 250 | +23.3% [+17.1, +33.9] | +0.7897 [+0.4279, +1.751] | gain |
| 2024 | v2_ewma_hl10 against B1p | 250 | +16.6% [+9.1, +27.1] | +0.5164 [+0.1932, +1.226] | gain |
| 2024 | v2_ewma_hl10 against B2 | 250 | +15.7% [+1.7, +30.3] | +0.4827 [+0.02998, +1.169] | gain |
| 2024 | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 250 | -1.3% [-4.8, +0.9] | -0.03313 [-0.116, +0.02323] | undecided |
| 2024 | v2_ewma_hl3 against B1 | 250 | +22.5% [+16.6, +32.5] | +0.7626 [+0.4199, +1.696] | gain |
| 2024 | v2_ewma_hl3 against B1p | 250 | +15.7% [+8.4, +25.7] | +0.4893 [+0.1838, +1.163] | gain |
| 2024 | v2_ewma_hl3 against B2 | 250 | +14.8% [+0.6, +29.3] | +0.4555 [+0.007199, +1.118] | gain |
| 2024 | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 250 | -2.4% [-7.3, +1.0] | -0.06025 [-0.1857, +0.02498] | undecided |
| 2024 | v2_ewma_hl5 against B1 | 250 | +23.0% [+16.9, +33.2] | +0.7783 [+0.4272, +1.719] | gain |
| 2024 | v2_ewma_hl5 against B1p | 250 | +16.2% [+8.9, +26.3] | +0.505 [+0.1921, +1.192] | gain |
| 2024 | v2_ewma_hl5 against B2 | 250 | +15.3% [+1.3, +29.6] | +0.4713 [+0.02075, +1.14] | gain |
| 2024 | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 250 | -1.7% [-6.2, +0.9] | -0.04453 [-0.1552, +0.02438] | undecided |
| 2024 | v2_ewma_hl5_asym against B1 | 250 | +23.3% [+17.1, +33.7] | +0.788 [+0.4327, +1.739] | gain |
| 2024 | v2_ewma_hl5_asym against B1p | 250 | +16.6% [+9.0, +26.9] | +0.5148 [+0.198, +1.216] | gain |
| 2024 | v2_ewma_hl5_asym against B2 | 250 | +15.6% [+1.9, +29.7] | +0.481 [+0.03988, +1.141] | gain |
| 2024 | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 250 | -1.4% [-5.7, +1.1] | -0.03481 [-0.1394, +0.03005] | undecided |
| 2024 | v3_miss against B1 | 250 | +24.0% [+17.2, +34.9] | +0.8104 [+0.4333, +1.776] | gain |
| 2024 | v3_miss against B1p | 250 | +17.3% [+9.4, +27.6] | +0.5371 [+0.2055, +1.232] | gain |
| 2024 | v3_miss against B2 | 250 | +16.4% [+3.1, +30.1] | +0.5033 [+0.06466, +1.15] | gain |
| 2024 | v3_miss against spread_mr_fhs_mad20_f0.5 | 250 | -0.5% [-1.5, +0.3] | -0.01247 [-0.04092, +0.009128] | undecided |
| 2024 | v4_v3_miss_cal against B1 | 250 | +24.2% [+17.4, +35.1] | +0.8192 [+0.4421, +1.778] | gain |
| 2024 | v4_v3_miss_cal against B1p | 250 | +17.6% [+9.8, +27.8] | +0.5459 [+0.2178, +1.247] | gain |
| 2024 | v4_v3_miss_cal against B2 | 250 | +16.7% [+3.3, +30.7] | +0.5121 [+0.07296, +1.167] | gain |
| 2024 | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 250 | -0.1% [-1.2, +0.8] | -0.003673 [-0.03482, +0.02035] | undecided |

### grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2025-26 | spread_mr_fhs_mad20_f0.5 against B1 | 249 | +23.4% [+16.3, +30.4] | +0.7857 [+0.437, +1.267] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.5 against B1p | 249 | +16.2% [+9.0, +23.6] | +0.4967 [+0.2221, +0.8749] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.5 against B2 | 249 | +31.9% [+7.7, +52.0] | +1.204 [+0.1189, +3.063] | gain |
| 2025-26 | v1_blend5_20 against B1 | 249 | +21.7% [+14.6, +28.7] | +0.7301 [+0.3912, +1.195] | gain |
| 2025-26 | v1_blend5_20 against B1p | 249 | +14.4% [+7.1, +22.0] | +0.4412 [+0.1746, +0.8115] | gain |
| 2025-26 | v1_blend5_20 against B2 | 249 | +30.4% [+5.7, +51.0] | +1.149 [+0.06674, +2.965] | gain |
| 2025-26 | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 249 | -2.2% [-3.7, -1.1] | -0.05557 [-0.09755, -0.02836] | loss |
| 2025-26 | v1_mad10 against B1 | 249 | +20.8% [+12.8, +28.2] | +0.6977 [+0.3443, +1.164] | gain |
| 2025-26 | v1_mad10 against B1p | 249 | +13.3% [+5.6, +20.6] | +0.4088 [+0.1385, +0.7527] | gain |
| 2025-26 | v1_mad10 against B2 | 249 | +29.6% [+2.8, +51.2] | +1.116 [+0.002806, +2.955] | gain |
| 2025-26 | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 249 | -3.4% [-7.8, -1.1] | -0.08791 [-0.2086, -0.02934] | loss |
| 2025-26 | v1_mad5 against B1 | 249 | +18.2% [+11.0, +25.3] | +0.6116 [+0.2935, +1.049] | gain |
| 2025-26 | v1_mad5 against B1p | 249 | +10.5% [+3.1, +18.2] | +0.3227 [+0.07217, +0.6636] | gain |
| 2025-26 | v1_mad5 against B2 | 249 | +27.3% [+1.6, +48.9] | +1.03 [-0.03824, +2.807] | undecided (was gain) |
| 2025-26 | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 249 | -6.8% [-9.7, -4.8] | -0.174 [-0.2642, -0.1199] | loss |
| 2025-26 | v2_ewma_hl10 against B1 | 249 | +23.8% [+16.9, +30.6] | +0.7977 [+0.4516, +1.289] | gain |
| 2025-26 | v2_ewma_hl10 against B1p | 249 | +16.6% [+9.6, +23.9] | +0.5088 [+0.2335, +0.8927] | gain |
| 2025-26 | v2_ewma_hl10 against B2 | 249 | +32.2% [+8.2, +52.3] | +1.216 [+0.1341, +3.087] | gain |
| 2025-26 | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 249 | +0.5% [-0.4, +1.4] | +0.01206 [-0.01103, +0.03681] | undecided |
| 2025-26 | v2_ewma_hl3 against B1 | 249 | +22.2% [+15.3, +28.9] | +0.7442 [+0.408, +1.212] | gain |
| 2025-26 | v2_ewma_hl3 against B1p | 249 | +14.8% [+7.8, +22.1] | +0.4553 [+0.1886, +0.8208] | gain |
| 2025-26 | v2_ewma_hl3 against B2 | 249 | +30.8% [+7.1, +51.3] | +1.163 [+0.09494, +3.013] | gain |
| 2025-26 | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 249 | -1.6% [-3.1, -0.3] | -0.04144 [-0.08075, -0.00708] | loss |
| 2025-26 | v2_ewma_hl5 against B1 | 249 | +23.2% [+16.4, +30.0] | +0.779 [+0.4378, +1.259] | gain |
| 2025-26 | v2_ewma_hl5 against B1p | 249 | +16.0% [+9.0, +23.3] | +0.4901 [+0.2218, +0.8668] | gain |
| 2025-26 | v2_ewma_hl5 against B2 | 249 | +31.7% [+7.9, +52.0] | +1.198 [+0.1221, +3.055] | gain |
| 2025-26 | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 249 | -0.3% [-1.4, +0.8] | -0.006663 [-0.03614, +0.02132] | undecided |
| 2025-26 | v2_ewma_hl5_asym against B1 | 249 | +23.2% [+16.5, +30.1] | +0.7805 [+0.4392, +1.267] | gain |
| 2025-26 | v2_ewma_hl5_asym against B1p | 249 | +16.0% [+9.1, +23.3] | +0.4915 [+0.2222, +0.8709] | gain |
| 2025-26 | v2_ewma_hl5_asym against B2 | 249 | +31.8% [+8.1, +52.1] | +1.199 [+0.1211, +3.064] | gain |
| 2025-26 | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 249 | -0.2% [-1.4, +1.1] | -0.005191 [-0.0354, +0.02812] | undecided |
| 2025-26 | v3_miss against B1 | 249 | +23.3% [+16.2, +30.2] | +0.781 [+0.4333, +1.261] | gain |
| 2025-26 | v3_miss against B1p | 249 | +16.0% [+8.9, +23.4] | +0.492 [+0.2174, +0.8661] | gain |
| 2025-26 | v3_miss against B2 | 249 | +31.8% [+7.5, +51.9] | +1.2 [+0.1133, +3.057] | gain |
| 2025-26 | v3_miss against spread_mr_fhs_mad20_f0.5 | 249 | -0.2% [-0.5, +0.1] | -0.004694 [-0.01392, +0.001941] | undecided |
| 2025-26 | v4_v3_miss_cal against B1 | 249 | +24.9% [+17.9, +31.8] | +0.8371 [+0.4826, +1.338] | gain |
| 2025-26 | v4_v3_miss_cal against B1p | 249 | +17.9% [+10.9, +25.2] | +0.5482 [+0.2695, +0.9388] | gain |
| 2025-26 | v4_v3_miss_cal against B2 | 249 | +33.3% [+9.6, +52.9] | +1.256 [+0.1645, +3.121] | gain |
| 2025-26 | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 249 | +2.0% [+1.2, +2.8] | +0.05143 [+0.03041, +0.07551] | gain |

### scaled_grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2025-26 | spread_mr_fhs_mad20_f0.5 against B1 | 249 | +21.2% [+11.1, +29.8] | +0.5743 [+0.3038, +0.9935] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.5 against B1p | 249 | +15.4% [+4.6, +28.5] | +0.3888 [+0.1235, +0.9244] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.5 against B2 | 249 | +22.3% [-6.9, +47.9] | +0.6142 [-0.1003, +1.687] | undecided |
| 2025-26 | v1_blend5_20 against B1 | 249 | +19.5% [+9.4, +28.5] | +0.5283 [+0.2593, +0.943] | gain |
| 2025-26 | v1_blend5_20 against B1p | 249 | +13.6% [+2.4, +27.4] | +0.3428 [+0.07754, +0.8758] | gain |
| 2025-26 | v1_blend5_20 against B2 | 249 | +20.6% [-8.7, +46.8] | +0.5682 [-0.1494, +1.628] | undecided |
| 2025-26 | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 249 | -2.1% [-3.3, -1.1] | -0.04601 [-0.07054, -0.02554] | loss |
| 2025-26 | v1_mad10 against B1 | 249 | +17.3% [+5.2, +26.4] | +0.471 [+0.1843, +0.8238] | gain |
| 2025-26 | v1_mad10 against B1p | 249 | +11.3% [-0.5, +23.3] | +0.2855 [+0.02305, +0.7063] | gain (was undecided) |
| 2025-26 | v1_mad10 against B2 | 249 | +18.5% [-15.3, +46.9] | +0.5109 [-0.2754, +1.588] | undecided |
| 2025-26 | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 249 | -4.8% [-15.2, -1.6] | -0.1033 [-0.3892, -0.0273] | loss |
| 2025-26 | v1_mad5 against B1 | 249 | +15.7% [+5.4, +24.5] | +0.4252 [+0.1639, +0.7973] | gain |
| 2025-26 | v1_mad5 against B1p | 249 | +9.5% [-1.8, +23.0] | +0.2397 [-0.01606, +0.7108] | undecided |
| 2025-26 | v1_mad5 against B2 | 249 | +16.9% [-14.2, +44.2] | +0.4651 [-0.2686, +1.495] | undecided |
| 2025-26 | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 249 | -7.0% [-9.2, -5.1] | -0.1491 [-0.2178, -0.1054] | loss |
| 2025-26 | v2_ewma_hl10 against B1 | 249 | +21.5% [+12.2, +30.1] | +0.5835 [+0.3195, +1.023] | gain |
| 2025-26 | v2_ewma_hl10 against B1p | 249 | +15.7% [+5.4, +29.5] | +0.398 [+0.1351, +0.9636] | gain |
| 2025-26 | v2_ewma_hl10 against B2 | 249 | +22.6% [-5.7, +48.3] | +0.6234 [-0.07745, +1.704] | undecided |
| 2025-26 | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 249 | +0.4% [-0.9, +1.9] | +0.009206 [-0.01846, +0.04477] | undecided |
| 2025-26 | v2_ewma_hl3 against B1 | 249 | +20.0% [+10.3, +28.6] | +0.5417 [+0.2796, +0.9597] | gain |
| 2025-26 | v2_ewma_hl3 against B1p | 249 | +14.1% [+3.6, +27.7] | +0.3563 [+0.09615, +0.8945] | gain |
| 2025-26 | v2_ewma_hl3 against B2 | 249 | +21.1% [-7.6, +47.0] | +0.5816 [-0.1223, +1.646] | undecided |
| 2025-26 | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 249 | -1.5% [-2.8, -0.2] | -0.03258 [-0.05776, -0.00694] | loss |
| 2025-26 | v2_ewma_hl5 against B1 | 249 | +21.0% [+11.8, +29.6] | +0.5715 [+0.3105, +0.998] | gain |
| 2025-26 | v2_ewma_hl5 against B1p | 249 | +15.3% [+5.0, +28.7] | +0.386 [+0.1275, +0.9378] | gain |
| 2025-26 | v2_ewma_hl5 against B2 | 249 | +22.2% [-6.2, +47.9] | +0.6114 [-0.09055, +1.69] | undecided |
| 2025-26 | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 249 | -0.1% [-1.3, +1.1] | -0.002797 [-0.02593, +0.02546] | undecided |
| 2025-26 | v2_ewma_hl5_asym against B1 | 249 | +21.2% [+11.9, +29.8] | +0.5744 [+0.3129, +1.017] | gain |
| 2025-26 | v2_ewma_hl5_asym against B1p | 249 | +15.4% [+5.1, +29.1] | +0.389 [+0.1294, +0.9566] | gain |
| 2025-26 | v2_ewma_hl5_asym against B2 | 249 | +22.3% [-5.9, +47.9] | +0.6143 [-0.08641, +1.695] | undecided |
| 2025-26 | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 249 | +0.0% [-1.4, +1.7] | +0.0001522 [-0.02806, +0.03858] | undecided |
| 2025-26 | v3_miss against B1 | 249 | +20.9% [+10.8, +29.3] | +0.5665 [+0.2972, +0.9715] | gain |
| 2025-26 | v3_miss against B1p | 249 | +15.1% [+4.3, +27.8] | +0.381 [+0.1196, +0.8955] | gain |
| 2025-26 | v3_miss against B2 | 249 | +22.0% [-7.5, +47.8] | +0.6064 [-0.1123, +1.677] | undecided |
| 2025-26 | v3_miss against spread_mr_fhs_mad20_f0.5 | 249 | -0.4% [-1.1, -0.0] | -0.007817 [-0.02761, -0.0004169] | loss |
| 2025-26 | v4_v3_miss_cal against B1 | 249 | +22.2% [+12.4, +30.8] | +0.6035 [+0.3343, +1.033] | gain |
| 2025-26 | v4_v3_miss_cal against B1p | 249 | +16.5% [+6.0, +29.3] | +0.4181 [+0.1529, +0.9615] | gain |
| 2025-26 | v4_v3_miss_cal against B2 | 249 | +23.4% [-5.4, +48.6] | +0.6434 [-0.06849, +1.726] | undecided |
| 2025-26 | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 249 | +1.4% [+0.6, +2.1] | +0.02925 [+0.01172, +0.04607] | gain |

### upper_tail_twcrps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2025-26 | spread_mr_fhs_mad20_f0.5 against B1 | 249 | +32.3% [+26.3, +39.4] | +0.5183 [+0.1817, +1.229] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.5 against B1p | 249 | +22.3% [+14.8, +31.1] | +0.3108 [+0.09228, +0.7239] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.5 against B2 | 249 | +29.6% [+13.6, +48.9] | +0.455 [+0.01624, +2.073] | gain |
| 2025-26 | v1_blend5_20 against B1 | 249 | +28.9% [+23.1, +36.0] | +0.4635 [+0.1417, +1.165] | gain |
| 2025-26 | v1_blend5_20 against B1p | 249 | +18.4% [+11.2, +26.6] | +0.256 [+0.05264, +0.6436] | gain |
| 2025-26 | v1_blend5_20 against B2 | 249 | +26.0% [+7.5, +48.6] | +0.4002 [-0.03516, +2.026] | undecided (was gain) |
| 2025-26 | v1_blend5_20 against spread_mr_fhs_mad20_f0.5 | 249 | -5.1% [-10.4, -1.7] | -0.05479 [-0.1265, -0.02645] | loss |
| 2025-26 | v1_mad10 against B1 | 249 | +27.1% [+19.7, +35.1] | +0.4346 [+0.105, +1.148] | gain |
| 2025-26 | v1_mad10 against B1p | 249 | +16.3% [+8.0, +24.2] | +0.2271 [+0.01651, +0.6055] | gain |
| 2025-26 | v1_mad10 against B2 | 249 | +24.1% [+1.5, +47.5] | +0.3713 [-0.08082, +1.858] | undecided (was gain) |
| 2025-26 | v1_mad10 against spread_mr_fhs_mad20_f0.5 | 249 | -7.7% [-26.8, -1.6] | -0.08372 [-0.2659, -0.0281] | loss |
| 2025-26 | v1_mad5 against B1 | 249 | +24.1% [+17.0, +32.5] | +0.3857 [+0.08317, +1.066] | gain |
| 2025-26 | v1_mad5 against B1p | 249 | +12.8% [+4.4, +21.7] | +0.1782 [-0.007126, +0.5372] | undecided (was gain) |
| 2025-26 | v1_mad5 against B2 | 249 | +20.9% [-1.1, +46.7] | +0.3224 [-0.09954, +1.854] | undecided |
| 2025-26 | v1_mad5 against spread_mr_fhs_mad20_f0.5 | 249 | -12.2% [-22.5, -5.5] | -0.1326 [-0.271, -0.07637] | loss |
| 2025-26 | v2_ewma_hl10 against B1 | 249 | +31.7% [+25.9, +38.9] | +0.5088 [+0.1702, +1.244] | gain |
| 2025-26 | v2_ewma_hl10 against B1p | 249 | +21.6% [+14.5, +30.0] | +0.3013 [+0.08024, +0.7149] | gain |
| 2025-26 | v2_ewma_hl10 against B2 | 249 | +28.9% [+12.2, +49.9] | +0.4455 [+0.003958, +2.137] | gain |
| 2025-26 | v2_ewma_hl10 against spread_mr_fhs_mad20_f0.5 | 249 | -0.9% [-2.9, +0.8] | -0.00953 [-0.02813, +0.007494] | undecided |
| 2025-26 | v2_ewma_hl3 against B1 | 249 | +28.5% [+22.6, +36.4] | +0.4565 [+0.1389, +1.196] | gain |
| 2025-26 | v2_ewma_hl3 against B1p | 249 | +17.8% [+10.8, +25.7] | +0.249 [+0.04705, +0.6361] | gain |
| 2025-26 | v2_ewma_hl3 against B2 | 249 | +25.5% [+6.1, +49.6] | +0.3932 [-0.04217, +2.073] | undecided (was gain) |
| 2025-26 | v2_ewma_hl3 against spread_mr_fhs_mad20_f0.5 | 249 | -5.7% [-11.5, -1.4] | -0.06182 [-0.1303, -0.02564] | loss |
| 2025-26 | v2_ewma_hl5 against B1 | 249 | +30.3% [+24.6, +37.6] | +0.4859 [+0.1566, +1.226] | gain |
| 2025-26 | v2_ewma_hl5 against B1p | 249 | +20.0% [+13.1, +27.9] | +0.2784 [+0.06428, +0.6785] | gain |
| 2025-26 | v2_ewma_hl5 against B2 | 249 | +27.5% [+9.3, +50.3] | +0.4226 [-0.01887, +2.133] | undecided (was gain) |
| 2025-26 | v2_ewma_hl5 against spread_mr_fhs_mad20_f0.5 | 249 | -3.0% [-7.1, +0.2] | -0.03242 [-0.07559, -0.005828] | loss (was undecided) |
| 2025-26 | v2_ewma_hl5_asym against B1 | 249 | +30.3% [+24.7, +38.1] | +0.4857 [+0.1565, +1.24] | gain |
| 2025-26 | v2_ewma_hl5_asym against B1p | 249 | +19.9% [+13.3, +27.5] | +0.2782 [+0.06312, +0.6822] | gain |
| 2025-26 | v2_ewma_hl5_asym against B2 | 249 | +27.4% [+9.2, +50.5] | +0.4224 [-0.01971, +2.15] | undecided (was gain) |
| 2025-26 | v2_ewma_hl5_asym against spread_mr_fhs_mad20_f0.5 | 249 | -3.0% [-7.1, +0.4] | -0.03263 [-0.07326, -0.005309] | loss (was undecided) |
| 2025-26 | v3_miss against B1 | 249 | +32.1% [+26.2, +39.0] | +0.5151 [+0.1816, +1.227] | gain |
| 2025-26 | v3_miss against B1p | 249 | +22.1% [+14.7, +30.7] | +0.3076 [+0.09262, +0.7173] | gain |
| 2025-26 | v3_miss against B2 | 249 | +29.4% [+13.2, +49.0] | +0.4519 [+0.01404, +2.082] | gain |
| 2025-26 | v3_miss against spread_mr_fhs_mad20_f0.5 | 249 | -0.3% [-0.8, +0.1] | -0.003165 [-0.01045, +0.0009815] | undecided |
| 2025-26 | v4_v3_miss_cal against B1 | 249 | +35.4% [+29.2, +42.1] | +0.5668 [+0.2159, +1.304] | gain |
| 2025-26 | v4_v3_miss_cal against B1p | 249 | +25.8% [+18.4, +34.6] | +0.3593 [+0.1283, +0.7997] | gain |
| 2025-26 | v4_v3_miss_cal against B2 | 249 | +32.7% [+18.9, +49.7] | +0.5035 [+0.05686, +2.093] | gain |
| 2025-26 | v4_v3_miss_cal against spread_mr_fhs_mad20_f0.5 | 249 | +4.5% [+2.0, +7.4] | +0.04849 [+0.02756, +0.08925] | gain |

### Politis-White block beside 10: grid_crps, by all decision days

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| all decision days | v1_blend5_20 against the base (a) | 1855 | -1.7% [-3.9, -0.4] | -0.02811 [-0.07815, -0.004876] | loss |
| all decision days | v1_mad10 against the base (a) | 1855 | -1.2% [-3.5, +0.2] | -0.02045 [-0.06405, +0.004037] | undecided |
| all decision days | v1_mad5 against the base (a) | 1855 | -7.3% [-12.1, -4.9] | -0.1233 [-0.2676, -0.06658] | loss |
| all decision days | v2_ewma_hl10 against the base (a) | 1855 | -4.6% [-19.9, -0.9] | -0.07782 [-0.4653, -0.001337] | loss |
| all decision days | v2_ewma_hl3 against the base (a) | 1855 | -7.1% [-35.9, -2.1] | -0.1204 [-0.8133, -0.01895] | loss |
| all decision days | v2_ewma_hl5 against the base (a) | 1855 | -5.5% [-30.6, -1.2] | -0.09392 [-0.6988, -0.006659] | loss |
| all decision days | v2_ewma_hl5_asym against the base (a) | 1855 | -5.3% [-28.4, -1.1] | -0.08969 [-0.6415, -0.006027] | loss |
| all decision days | v3_miss against the base (a) | 1855 | +0.1% [-0.1, +0.3] | +0.001905 [-0.001468, +0.005781] | undecided |
| all decision days | v4_v3_miss_cal against the base (a) | 1855 | +0.9% [+0.3, +1.8] | +0.01518 [+0.003972, +0.03421] | gain |

### Politis-White block beside 10: upper_tail_twcrps, by all decision days

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| all decision days | v1_blend5_20 against the base (a) | 1855 | -3.2% [-5.6, -1.5] | -0.0286 [-0.06357, -0.009796] | loss |
| all decision days | v1_mad10 against the base (a) | 1855 | -2.5% [-5.9, -0.2] | -0.02273 [-0.06216, -0.002403] | loss |
| all decision days | v1_mad5 against the base (a) | 1855 | -10.3% [-14.7, -6.3] | -0.09205 [-0.1853, -0.04804] | loss |
| all decision days | v2_ewma_hl10 against the base (a) | 1855 | -8.0% [-22.1, -3.8] | -0.07157 [-0.4275, -0.004699] | loss |
| all decision days | v2_ewma_hl3 against the base (a) | 1855 | -12.2% [-32.8, -6.9] | -0.1094 [-0.5624, -0.02664] | loss |
| all decision days | v2_ewma_hl5 against the base (a) | 1855 | -9.8% [-29.8, -5.1] | -0.08756 [-0.5412, -0.01439] | loss |
| all decision days | v2_ewma_hl5_asym against the base (a) | 1855 | -9.4% [-27.4, -4.8] | -0.08399 [-0.5016, -0.01233] | loss |
| all decision days | v3_miss against the base (a) | 1855 | -0.2% [-0.4, +0.1] | -0.001429 [-0.003179, +0.0002962] | undecided |
| all decision days | v4_v3_miss_cal against the base (a) | 1855 | +1.7% [+0.7, +3.3] | +0.01567 [+0.004828, +0.0408] | gain |

Nothing here is a verdict for a hypothesis. The originals stand.
