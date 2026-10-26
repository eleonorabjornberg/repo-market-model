# Walk-forward calibration of the bands (#1133), read on the mean-d bound (#1167; H5 reporting, for #1009)

**Development data, not a verdict.** No re-scoring, no lockbox day, and no published declaration, record or decided value moves. Every figure is read from `docs/research/walk-calibration-1133/result.json`, the record of the original page (`walk-calibration-1133-result.md`, which stands), by `scripts/mean_d_reading_1167.py report`. Seed 1133, 10,000 draws, as on the original page.

## What changes and why

The original page read each row from the studentized skill interval. The skill interval and the interval on the mean difference d are built from different studentized draws, so their ends can fall on different sides of zero (#1009). The protocol's verdict reads the one-sided studentized bound on mean d (ruling 1/5). By Eleonora's ruling on #1009 this page shows both intervals for every paired row and reads the mean-d bound: **gain** when the lower bound of mean d is above zero, **loss** when its upper bound is below zero, **undecided** otherwise. The 90% two-sided interval on mean d is the pair of one-sided 95% bounds. d = S(benchmark) − S(candidate), positive favouring the candidate; skill is mean(d) / mean(S(benchmark)). A row the scorer left undefined carries no interval and is not read here.

**Caveat (Lens C of the five-lens review, #958).** The lag-10 HAC standard error that studentizes the mean-d bound is understated about 2× after 2020 (about 2.3× in 2021–23, 1.7× in 2024–26), and the bootstrap block of 10 days is an order of magnitude shorter than the autocorrelation of d. The bound is therefore optimistic: an interval that excludes zero here is narrower than it should be after 2020. A development reading on this page is evidence for a question, not a verdict.

Paired rows read: 287. Rows whose reading changes: 49.

| reading on the skill interval -> reading on the mean-d bound | rows |
|---|---|
| gain -> undecided | 9 |
| loss -> undecided | 2 |
| undecided -> gain | 23 |
| undecided -> loss | 15 |

## Readings that change

| section | group | comparison | skill [90%] | mean d [90%] | on the skill interval | on the mean-d bound |
|---|---|---|---|---|---|---|
| grid_crps, by lead | h=1 | spread_mr_fhs_mad20_f0.5 against B1p | +6.3% [-2.5, +12.6] | +0.0931 [+0.003789, +0.1811] | undecided | **gain** |
| grid_crps, by lead | h=1 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | -1.1% [-2.1, +0.1] | -0.01494 [-0.02644, -0.003852] | undecided | **loss** |
| upper_tail_twcrps, by lead | h=1 | spread_mr_fhs_mad20_f0.5 against B2 | +21.1% [-22.1, +46.9] | +0.1811 [+0.03218, +0.3554] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | spread_mr_fhs_mad20_f0.5+pooled against B2 | +20.0% [-19.5, +45.2] | +0.1715 [+0.02471, +0.347] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | -1.4% [-3.7, +1.8] | -0.009622 [-0.01735, -0.0009301] | undecided | **loss** |
| grid_crps, by lead | h=2 | spread_mr_fhs_mad20_f0.5+pooled against B1p | +6.0% [-0.0, +11.5] | +0.09633 [+0.01543, +0.1862] | undecided | **gain** |
| grid_crps, by lead | h=2 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | -1.2% [-2.3, +0.0] | -0.01808 [-0.03086, -0.005226] | undecided | **loss** |
| upper_tail_twcrps, by lead | h=2 | spread_mr_fhs_mad20_f0.5 against B1p | +9.7% [-8.7, +22.3] | +0.07233 [+0.004233, +0.1514] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=2 | spread_mr_fhs_mad20_f0.5 against B2 | +22.6% [-7.1, +45.7] | +0.196 [+0.07337, +0.3774] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=2 | spread_mr_fhs_mad20_f0.5+pooled against B2 | +21.3% [-5.2, +43.9] | +0.1846 [+0.06065, +0.3654] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=2 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | -1.7% [-4.2, +1.9] | -0.01137 [-0.01999, -0.0007794] | undecided | **loss** |
| upper_tail_twcrps, by lead | h=3 | spread_mr_fhs_mad20_f0.5 against B1p | +13.3% [-1.2, +26.2] | +0.1031 [+0.03704, +0.2081] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=3 | spread_mr_fhs_mad20_f0.5 against B2 | +22.8% [-0.9, +44.5] | +0.1982 [+0.08159, +0.383] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=3 | spread_mr_fhs_mad20_f0.5+pooled against B1p | +11.5% [-0.5, +23.2] | +0.08898 [+0.02132, +0.1922] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=3 | spread_mr_fhs_mad20_f0.5+pooled against B2 | +21.1% [-0.0, +41.9] | +0.184 [+0.06449, +0.3667] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=3 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | -2.1% [-4.9, +2.0] | -0.01412 [-0.02428, -0.003379] | undecided | **loss** |
| upper_tail_twcrps, by lead | h=4 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | -2.7% [-6.1, +2.4] | -0.01799 [-0.03293, -0.0046] | undecided | **loss** |
| upper_tail_twcrps, by lead | h=5 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | -3.0% [-7.0, +2.6] | -0.02063 [-0.03887, -0.004769] | undecided | **loss** |
| upper_tail_twcrps, by all decision days | all decision days | spread_mr_fhs_mad20_f0.5 against B2 | +22.4% [-1.7, +44.2] | +0.1946 [+0.07416, +0.3797] | undecided | **gain** |
| upper_tail_twcrps, by all decision days | all decision days | spread_mr_fhs_mad20_f0.5+pooled against B2 | +20.7% [-0.9, +41.5] | +0.1799 [+0.0575, +0.3638] | undecided | **gain** |
| upper_tail_twcrps, by all decision days | all decision days | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | -2.2% [-5.0, +2.0] | -0.01475 [-0.02665, -0.003677] | undecided | **loss** |
| upper_tail_twcrps, by pressure-day type | ordinary | spread_mr_fhs_mad20_f0.5 against B2 | +18.4% [-0.3, +35.3] | +0.09739 [+0.008796, +0.2232] | undecided | **gain** |
| grid_crps, by pressure-day type | quarter_end | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | +3.7% [+2.5, +4.5] | +0.154 [-0.02144, +0.4624] | gain | **undecided** |
| scaled_grid_crps, by pressure-day type | quarter_end | spread_mr_fhs_mad20_f0.5+pooled against B2 | +28.9% [-25.7, +69.7] | +0.5115 [+0.0704, +0.8493] | undecided | **gain** |
| scaled_grid_crps, by pressure-day type | quarter_end | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | +4.0% [+0.6, +5.7] | +0.05202 [-0.02673, +0.2245] | gain | **undecided** |
| grid_crps, by pressure-day type | tax_date | spread_mr_fhs_mad20_f0.5 against B1 | +5.4% [-1.4, +9.8] | +0.3156 [+0.02492, +1.139] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | spread_mr_fhs_mad20_f0.5 against B1p | +4.3% [+2.4, +6.0] | +0.2482 [-0.02448, +1.196] | gain | **undecided** |
| grid_crps, by pressure-day type | tax_date | spread_mr_fhs_mad20_f0.5 against B2 | +32.2% [-78.4, +60.9] | +2.628 [+1.232, +5.742] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | spread_mr_fhs_mad20_f0.5+pooled against B1p | +5.6% [+4.3, +7.1] | +0.3218 [-0.02379, +2.109] | gain | **undecided** |
| grid_crps, by pressure-day type | tax_date | spread_mr_fhs_mad20_f0.5+pooled against B2 | +33.1% [-74.4, +61.1] | +2.702 [+1.241, +6.144] | undecided | **gain** |
| grid_crps, by pressure-day type | tax_date | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | +1.3% [+0.4, +2.4] | +0.07359 [-0.0166, +0.7621] | gain | **undecided** |
| scaled_grid_crps, by pressure-day type | tax_date | spread_mr_fhs_mad20_f0.5 against B1p | +5.4% [+1.6, +10.3] | +0.09823 [-0.01205, +0.3339] | gain | **undecided** |
| scaled_grid_crps, by pressure-day type | tax_date | spread_mr_fhs_mad20_f0.5 against B2 | +34.2% [-46.9, +56.8] | +0.9007 [+0.6623, +1.205] | undecided | **gain** |
| scaled_grid_crps, by pressure-day type | tax_date | spread_mr_fhs_mad20_f0.5+pooled against B1 | +9.2% [-0.9, +22.0] | +0.1734 [+0.002955, +0.597] | undecided | **gain** |
| scaled_grid_crps, by pressure-day type | tax_date | spread_mr_fhs_mad20_f0.5+pooled against B1p | +6.2% [+3.4, +10.2] | +0.1134 [-0.006937, +0.4805] | gain | **undecided** |
| scaled_grid_crps, by pressure-day type | tax_date | spread_mr_fhs_mad20_f0.5+pooled against B2 | +34.8% [-43.1, +56.8] | +0.9159 [+0.6641, +1.251] | undecided | **gain** |
| scaled_grid_crps, by regime | 2018-19 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | -3.5% [-9.1, +5.5] | -0.084 [-0.177, -0.01622] | undecided | **loss** |
| grid_crps, by regime | 2020 | spread_mr_fhs_mad20_f0.5+pooled against B1p | +11.2% [+0.3, +28.3] | +0.1796 [-0.007619, +0.7376] | gain | **undecided** |
| grid_crps, by regime | 2020 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | -1.6% [-3.6, +1.2] | -0.02263 [-0.03622, -0.002368] | undecided | **loss** |
| scaled_grid_crps, by regime | 2020 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | -1.8% [-3.8, +0.9] | -0.0115 [-0.01858, -0.002309] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2020 | spread_mr_fhs_mad20_f0.5 against B2 | +58.1% [-25.1, +84.6] | +0.7083 [+0.3551, +1.135] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | spread_mr_fhs_mad20_f0.5+pooled against B2 | +56.6% [-17.8, +82.6] | +0.6896 [+0.3336, +1.117] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | -3.7% [-11.0, +10.1] | -0.01867 [-0.02731, -0.001669] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2021-23 | spread_mr_fhs_mad20_f0.5 against B2 | -156.2% [-802.3, -33.9] | -0.004779 [-0.04836, +0.0003283] | loss | **undecided** |
| upper_tail_twcrps, by regime | 2021-23 | spread_mr_fhs_mad20_f0.5+pooled against B2 | -154.0% [-836.3, -34.1] | -0.004711 [-0.05119, +0.0003274] | loss | **undecided** |
| grid_crps, by regime | 2024 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | -2.9% [-6.2, +0.2] | -0.03497 [-0.05966, -0.006025] | undecided | **loss** |
| grid_crps, by regime | 2025-26 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | -1.5% [-3.3, +0.0] | -0.03733 [-0.08691, -0.001692] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2025-26 | spread_mr_fhs_mad20_f0.5+pooled against B2 | +27.6% [+9.4, +50.2] | +0.4256 [-0.02539, +2.195] | gain | **undecided** |
| upper_tail_twcrps, by regime | 2025-26 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | -2.7% [-6.0, +0.4] | -0.02942 [-0.05487, -0.004121] | undecided | **loss** |

Every other paired row reads the same on both intervals.

## All paired rows

### grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=1 | spread_mr_fhs_mad20_f0.5 against B1 | 1600 | +21.8% [+14.5, +38.7] | +0.3878 [+0.1629, +1.377] | gain |
| h=1 | spread_mr_fhs_mad20_f0.5 against B1p | 1600 | +6.3% [-2.5, +12.6] | +0.0931 [+0.003789, +0.1811] | gain (was undecided) |
| h=1 | spread_mr_fhs_mad20_f0.5 against B2 | 1600 | +40.0% [+16.4, +52.4] | +0.9247 [+0.6395, +1.292] | gain |
| h=1 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 1600 | +21.0% [+13.1, +39.0] | +0.3728 [+0.1464, +1.366] | gain |
| h=1 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 1600 | +5.3% [-2.7, +11.6] | +0.07816 [-0.008753, +0.1681] | undecided |
| h=1 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 1600 | +39.3% [+16.6, +51.8] | +0.9097 [+0.6246, +1.278] | gain |
| h=1 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 1600 | -1.1% [-2.1, +0.1] | -0.01494 [-0.02644, -0.003852] | loss (was undecided) |

### scaled_grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=1 | spread_mr_fhs_mad20_f0.5 against B1 | 1598 | +20.9% [+13.9, +36.3] | +0.3191 [+0.17, +0.8022] | gain |
| h=1 | spread_mr_fhs_mad20_f0.5 against B1p | 1598 | +7.8% [+0.6, +14.4] | +0.103 [+0.01491, +0.2155] | gain |
| h=1 | spread_mr_fhs_mad20_f0.5 against B2 | 1598 | +35.3% [+25.0, +43.8] | +0.6611 [+0.4839, +0.8652] | gain |
| h=1 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 1598 | +19.6% [+12.2, +35.2] | +0.2997 [+0.1499, +0.7723] | gain |
| h=1 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 1598 | +6.4% [-1.1, +13.6] | +0.08366 [-0.007282, +0.2028] | undecided |
| h=1 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 1598 | +34.3% [+24.1, +42.7] | +0.6417 [+0.4621, +0.8471] | gain |
| h=1 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 1598 | -1.6% [-2.7, -0.6] | -0.01936 [-0.03153, -0.00791] | loss |

### upper_tail_twcrps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=1 | spread_mr_fhs_mad20_f0.5 against B1 | 1600 | +32.9% [+25.8, +45.8] | +0.3313 [+0.1061, +1.537] | gain |
| h=1 | spread_mr_fhs_mad20_f0.5 against B1p | 1600 | +10.3% [-18.4, +24.5] | +0.07777 [-0.005971, +0.164] | undecided |
| h=1 | spread_mr_fhs_mad20_f0.5 against B2 | 1600 | +21.1% [-22.1, +46.9] | +0.1811 [+0.03218, +0.3554] | gain (was undecided) |
| h=1 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 1600 | +31.9% [+24.7, +46.4] | +0.3216 [+0.09591, +1.537] | gain |
| h=1 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 1600 | +9.0% [-14.6, +22.5] | +0.06815 [-0.01174, +0.1547] | undecided |
| h=1 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 1600 | +20.0% [-19.5, +45.2] | +0.1715 [+0.02471, +0.347] | gain (was undecided) |
| h=1 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 1600 | -1.4% [-3.7, +1.8] | -0.009622 [-0.01735, -0.0009301] | loss (was undecided) |

### grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=2 | spread_mr_fhs_mad20_f0.5 against B1 | 1600 | +23.9% [+16.0, +45.0] | +0.4643 [+0.2105, +1.68] | gain |
| h=2 | spread_mr_fhs_mad20_f0.5 against B1p | 1600 | +7.2% [+0.6, +12.7] | +0.1144 [+0.03421, +0.2025] | gain |
| h=2 | spread_mr_fhs_mad20_f0.5 against B2 | 1600 | +36.8% [+19.9, +48.2] | +0.8606 [+0.5898, +1.236] | gain |
| h=2 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 1600 | +22.9% [+14.6, +45.9] | +0.4462 [+0.1915, +1.665] | gain |
| h=2 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 1600 | +6.0% [-0.0, +11.5] | +0.09633 [+0.01543, +0.1862] | gain (was undecided) |
| h=2 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 1600 | +36.0% [+19.9, +47.7] | +0.8425 [+0.5698, +1.217] | gain |
| h=2 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 1600 | -1.2% [-2.3, +0.0] | -0.01808 [-0.03086, -0.005226] | loss (was undecided) |

### scaled_grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=2 | spread_mr_fhs_mad20_f0.5 against B1 | 1598 | +22.6% [+15.3, +40.6] | +0.3856 [+0.2147, +0.9805] | gain |
| h=2 | spread_mr_fhs_mad20_f0.5 against B1p | 1598 | +8.0% [+2.2, +14.2] | +0.1154 [+0.03033, +0.2363] | gain |
| h=2 | spread_mr_fhs_mad20_f0.5 against B2 | 1598 | +29.9% [+20.9, +38.5] | +0.5648 [+0.3944, +0.7745] | gain |
| h=2 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 1598 | +21.1% [+13.5, +39.5] | +0.3604 [+0.1887, +0.9515] | gain |
| h=2 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 1598 | +6.3% [+0.1, +12.9] | +0.09015 [+0.002685, +0.2129] | gain |
| h=2 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 1598 | +28.6% [+19.4, +37.4] | +0.5395 [+0.364, +0.7503] | gain |
| h=2 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 1598 | -1.9% [-3.0, -0.8] | -0.02523 [-0.03903, -0.01229] | loss |

### upper_tail_twcrps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=2 | spread_mr_fhs_mad20_f0.5 against B1 | 1600 | +35.4% [+26.7, +55.5] | +0.369 [+0.115, +1.898] | gain |
| h=2 | spread_mr_fhs_mad20_f0.5 against B1p | 1600 | +9.7% [-8.7, +22.3] | +0.07233 [+0.004233, +0.1514] | gain (was undecided) |
| h=2 | spread_mr_fhs_mad20_f0.5 against B2 | 1600 | +22.6% [-7.1, +45.7] | +0.196 [+0.07337, +0.3774] | gain (was undecided) |
| h=2 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 1600 | +34.3% [+25.1, +57.5] | +0.3577 [+0.1026, +1.908] | gain |
| h=2 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 1600 | +8.2% [-6.9, +19.7] | +0.06095 [-0.005367, +0.1406] | undecided |
| h=2 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 1600 | +21.3% [-5.2, +43.9] | +0.1846 [+0.06065, +0.3654] | gain (was undecided) |
| h=2 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 1600 | -1.7% [-4.2, +1.9] | -0.01137 [-0.01999, -0.0007794] | loss (was undecided) |

### grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=3 | spread_mr_fhs_mad20_f0.5 against B1 | 1600 | +25.5% [+17.7, +46.5] | +0.5263 [+0.2569, +1.725] | gain |
| h=3 | spread_mr_fhs_mad20_f0.5 against B1p | 1600 | +9.1% [+3.9, +14.7] | +0.1549 [+0.07277, +0.2646] | gain |
| h=3 | spread_mr_fhs_mad20_f0.5 against B2 | 1600 | +34.6% [+20.7, +45.9] | +0.8136 [+0.5437, +1.184] | gain |
| h=3 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 1600 | +24.3% [+16.1, +47.2] | +0.5016 [+0.2329, +1.716] | gain |
| h=3 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 1600 | +7.7% [+2.7, +13.1] | +0.1302 [+0.04568, +0.2401] | gain |
| h=3 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 1600 | +33.5% [+20.1, +45.1] | +0.789 [+0.5142, +1.163] | gain |
| h=3 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 1600 | -1.6% [-2.8, -0.3] | -0.02469 [-0.03959, -0.01083] | loss |

### scaled_grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=3 | spread_mr_fhs_mad20_f0.5 against B1 | 1598 | +23.8% [+16.4, +41.1] | +0.4311 [+0.2442, +1.035] | gain |
| h=3 | spread_mr_fhs_mad20_f0.5 against B1p | 1598 | +9.8% [+4.2, +16.9] | +0.1496 [+0.05649, +0.3071] | gain |
| h=3 | spread_mr_fhs_mad20_f0.5 against B2 | 1598 | +27.5% [+18.4, +36.4] | +0.5235 [+0.3426, +0.7392] | gain |
| h=3 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 1598 | +21.9% [+14.1, +39.9] | +0.3954 [+0.2085, +0.9872] | gain |
| h=3 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 1598 | +7.5% [+1.6, +14.7] | +0.1139 [+0.02031, +0.2636] | gain |
| h=3 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 1598 | +25.6% [+16.3, +34.7] | +0.4878 [+0.3033, +0.7046] | gain |
| h=3 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 1598 | -2.6% [-3.9, -1.4] | -0.03568 [-0.0535, -0.02052] | loss |

### upper_tail_twcrps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=3 | spread_mr_fhs_mad20_f0.5 against B1 | 1600 | +37.7% [+27.8, +59.4] | +0.4067 [+0.1409, +1.925] | gain |
| h=3 | spread_mr_fhs_mad20_f0.5 against B1p | 1600 | +13.3% [-1.2, +26.2] | +0.1031 [+0.03704, +0.2081] | gain (was undecided) |
| h=3 | spread_mr_fhs_mad20_f0.5 against B2 | 1600 | +22.8% [-0.9, +44.5] | +0.1982 [+0.08159, +0.383] | gain (was undecided) |
| h=3 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 1600 | +36.4% [+26.2, +61.7] | +0.3926 [+0.126, +1.938] | gain |
| h=3 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 1600 | +11.5% [-0.5, +23.2] | +0.08898 [+0.02132, +0.1922] | gain (was undecided) |
| h=3 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 1600 | +21.1% [-0.0, +41.9] | +0.184 [+0.06449, +0.3667] | gain (was undecided) |
| h=3 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 1600 | -2.1% [-4.9, +2.0] | -0.01412 [-0.02428, -0.003379] | loss (was undecided) |

### grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=4 | spread_mr_fhs_mad20_f0.5 against B1 | 1600 | +26.1% [+17.7, +49.2] | +0.558 [+0.2739, +1.788] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5 against B1p | 1600 | +11.3% [+7.1, +16.2] | +0.2023 [+0.1109, +0.3278] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5 against B2 | 1600 | +33.0% [+20.8, +44.0] | +0.7808 [+0.5088, +1.146] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 1600 | +24.6% [+15.8, +49.9] | +0.5257 [+0.2407, +1.758] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 1600 | +9.5% [+5.1, +14.4] | +0.1699 [+0.07693, +0.2952] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 1600 | +31.7% [+19.7, +42.9] | +0.7484 [+0.4711, +1.116] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 1600 | -2.0% [-3.5, -0.4] | -0.03237 [-0.05146, -0.01499] | loss |

### scaled_grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=4 | spread_mr_fhs_mad20_f0.5 against B1 | 1598 | +23.8% [+16.2, +41.2] | +0.4446 [+0.2533, +1.038] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5 against B1p | 1598 | +11.2% [+5.9, +18.0] | +0.1802 [+0.08202, +0.3426] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5 against B2 | 1598 | +25.8% [+16.3, +34.8] | +0.4937 [+0.303, +0.7124] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 1598 | +21.4% [+13.4, +39.6] | +0.3997 [+0.209, +0.9839] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 1598 | +8.4% [+2.6, +15.3] | +0.1352 [+0.03644, +0.2885] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 1598 | +23.4% [+13.4, +32.8] | +0.4487 [+0.2503, +0.6698] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 1598 | -3.2% [-4.6, -1.8] | -0.04496 [-0.0671, -0.02697] | loss |

### upper_tail_twcrps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=4 | spread_mr_fhs_mad20_f0.5 against B1 | 1600 | +38.5% [+26.4, +66.6] | +0.4205 [+0.1394, +2.024] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5 against B1p | 1600 | +16.1% [+6.6, +26.8] | +0.1285 [+0.05922, +0.2486] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5 against B2 | 1600 | +23.1% [+3.4, +42.3] | +0.2011 [+0.08456, +0.3815] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 1600 | +36.9% [+24.6, +69.7] | +0.4025 [+0.1209, +2.025] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 1600 | +13.8% [+6.1, +23.6] | +0.1105 [+0.03939, +0.2303] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 1600 | +21.0% [+3.4, +38.9] | +0.1832 [+0.06217, +0.3645] | gain |
| h=4 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 1600 | -2.7% [-6.1, +2.4] | -0.01799 [-0.03293, -0.0046] | loss (was undecided) |

### grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=5 | spread_mr_fhs_mad20_f0.5 against B1 | 1600 | +26.2% [+17.6, +49.8] | +0.5797 [+0.2892, +1.796] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5 against B1p | 1600 | +12.9% [+8.7, +17.8] | +0.2419 [+0.1453, +0.3747] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5 against B2 | 1600 | +31.5% [+19.7, +42.5] | +0.7489 [+0.4753, +1.115] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 1600 | +24.5% [+15.5, +50.2] | +0.5403 [+0.2505, +1.762] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 1600 | +10.8% [+6.5, +15.5] | +0.2026 [+0.1047, +0.3328] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 1600 | +29.8% [+18.2, +41.1] | +0.7095 [+0.4276, +1.079] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 1600 | -2.4% [-4.1, -0.6] | -0.03937 [-0.06272, -0.01924] | loss |

### scaled_grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=5 | spread_mr_fhs_mad20_f0.5 against B1 | 1598 | +24.4% [+17.0, +41.0] | +0.4742 [+0.2785, +1.061] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5 against B1p | 1598 | +13.6% [+8.4, +20.4] | +0.2302 [+0.1218, +0.4196] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5 against B2 | 1598 | +23.9% [+13.9, +33.0] | +0.4609 [+0.2617, +0.6839] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 1598 | +21.6% [+13.9, +39.1] | +0.42 [+0.2269, +0.9959] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 1598 | +10.4% [+4.7, +17.4] | +0.176 [+0.06795, +0.3515] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 1598 | +21.1% [+10.5, +30.6] | +0.4067 [+0.1977, +0.6331] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 1598 | -3.7% [-5.3, -2.2] | -0.05417 [-0.08067, -0.03299] | loss |

### upper_tail_twcrps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=5 | spread_mr_fhs_mad20_f0.5 against B1 | 1600 | +37.8% [+23.1, +70.9] | +0.4152 [+0.1288, +2.058] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5 against B1p | 1600 | +15.8% [+7.3, +25.5] | +0.1279 [+0.05831, +0.2467] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5 against B2 | 1600 | +22.3% [+3.7, +40.6] | +0.1966 [+0.0805, +0.3756] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 1600 | +35.9% [+21.6, +74.7] | +0.3946 [+0.1091, +2.051] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 1600 | +13.2% [+6.2, +21.9] | +0.1073 [+0.03601, +0.2254] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 1600 | +20.0% [+3.6, +36.6] | +0.1759 [+0.05359, +0.3563] | gain |
| h=5 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 1600 | -3.0% [-7.0, +2.6] | -0.02063 [-0.03887, -0.004769] | loss (was undecided) |

### grid_crps, by all decision days

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| all decision days | spread_mr_fhs_mad20_f0.5 against B1 | 1600 | +24.8% [+16.9, +46.7] | +0.5032 [+0.2407, +1.719] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5 against B1p | 1600 | +9.6% [+4.8, +14.7] | +0.1613 [+0.08657, +0.2653] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5 against B2 | 1600 | +35.1% [+20.9, +46.6] | +0.8257 [+0.5571, +1.201] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5+pooled against B1 | 1600 | +23.5% [+15.2, +47.4] | +0.4773 [+0.2144, +1.709] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5+pooled against B1p | 1600 | +8.0% [+3.4, +13.1] | +0.1354 [+0.05906, +0.2396] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5+pooled against B2 | 1600 | +34.0% [+20.3, +45.7] | +0.7998 [+0.5263, +1.177] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 1600 | -1.7% [-2.9, -0.3] | -0.02589 [-0.04197, -0.01168] | loss |

### scaled_grid_crps, by all decision days

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| all decision days | spread_mr_fhs_mad20_f0.5 against B1 | 1598 | +23.2% [+16.0, +41.0] | +0.4109 [+0.2325, +1.005] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5 against B1p | 1598 | +10.3% [+5.1, +16.9] | +0.1557 [+0.0678, +0.3058] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5 against B2 | 1598 | +28.4% [+19.5, +37.3] | +0.5408 [+0.3628, +0.7572] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5+pooled against B1 | 1598 | +21.2% [+13.6, +39.6] | +0.3751 [+0.1978, +0.9625] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5+pooled against B1p | 1598 | +7.9% [+2.3, +14.8] | +0.1198 [+0.03126, +0.264] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5+pooled against B2 | 1598 | +26.6% [+17.2, +35.6] | +0.5049 [+0.3229, +0.7222] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 1598 | -2.6% [-3.9, -1.5] | -0.03588 [-0.05362, -0.02064] | loss |

### upper_tail_twcrps, by all decision days

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| all decision days | spread_mr_fhs_mad20_f0.5 against B1 | 1600 | +36.5% [+26.6, +59.9] | +0.3886 [+0.1266, +1.91] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5 against B1p | 1600 | +13.1% [+0.8, +24.8] | +0.1019 [+0.04245, +0.2031] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5 against B2 | 1600 | +22.4% [-1.7, +44.2] | +0.1946 [+0.07416, +0.3797] | gain (was undecided) |
| all decision days | spread_mr_fhs_mad20_f0.5+pooled against B1 | 1600 | +35.1% [+24.7, +62.4] | +0.3738 [+0.1109, +1.925] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5+pooled against B1p | 1600 | +11.2% [+1.0, +22.1] | +0.08717 [+0.02682, +0.1878] | gain |
| all decision days | spread_mr_fhs_mad20_f0.5+pooled against B2 | 1600 | +20.7% [-0.9, +41.5] | +0.1799 [+0.0575, +0.3638] | gain (was undecided) |
| all decision days | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 1600 | -2.2% [-5.0, +2.0] | -0.01475 [-0.02665, -0.003677] | loss (was undecided) |

### grid_crps, by pressure-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| month_end | spread_mr_fhs_mad20_f0.5 against B1 | 130 | +17.3% [+10.9, +23.9] | +0.3255 [+0.09874, +0.8767] | gain |
| month_end | spread_mr_fhs_mad20_f0.5 against B1p | 130 | +10.0% [+2.0, +16.9] | +0.1737 [+0.009492, +0.4136] | gain |
| month_end | spread_mr_fhs_mad20_f0.5 against B2 | 130 | +39.5% [+17.9, +56.4] | +1.018 [+0.3571, +2.338] | gain |
| month_end | spread_mr_fhs_mad20_f0.5+pooled against B1 | 130 | +17.3% [+9.9, +25.2] | +0.3264 [+0.08785, +0.9193] | gain |
| month_end | spread_mr_fhs_mad20_f0.5+pooled against B1p | 130 | +10.1% [+1.7, +17.0] | +0.1747 [+0.004383, +0.4291] | gain |
| month_end | spread_mr_fhs_mad20_f0.5+pooled against B2 | 130 | +39.5% [+18.6, +56.8] | +1.019 [+0.357, +2.369] | gain |
| month_end | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 130 | +0.1% [-2.2, +1.7] | +0.0009825 [-0.03082, +0.02843] | undecided |

### scaled_grid_crps, by pressure-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| month_end | spread_mr_fhs_mad20_f0.5 against B1 | 128 | +14.2% [+6.4, +23.7] | +0.24 [+0.05334, +0.668] | gain |
| month_end | spread_mr_fhs_mad20_f0.5 against B1p | 128 | +2.3% [-10.8, +11.7] | +0.03341 [-0.1278, +0.1791] | undecided |
| month_end | spread_mr_fhs_mad20_f0.5 against B2 | 128 | +28.5% [+0.4, +53.0] | +0.5785 [+0.1847, +1.362] | gain |
| month_end | spread_mr_fhs_mad20_f0.5+pooled against B1 | 128 | +14.7% [+6.5, +24.9] | +0.2478 [+0.04463, +0.6871] | gain |
| month_end | spread_mr_fhs_mad20_f0.5+pooled against B1p | 128 | +2.8% [-9.6, +12.6] | +0.04116 [-0.1121, +0.1996] | undecided |
| month_end | spread_mr_fhs_mad20_f0.5+pooled against B2 | 128 | +28.9% [+2.3, +53.9] | +0.5862 [+0.194, +1.407] | gain |
| month_end | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 128 | +0.5% [-2.1, +2.2] | +0.007758 [-0.0252, +0.03749] | undecided |

### grid_crps, by pressure-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| ordinary | spread_mr_fhs_mad20_f0.5 against B1 | 1371 | +29.8% [+17.1, +71.0] | +0.5331 [+0.2395, +1.938] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5 against B1p | 1371 | +10.8% [+5.1, +16.6] | +0.1527 [+0.06661, +0.2686] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5 against B2 | 1371 | +35.5% [+24.5, +45.7] | +0.6902 [+0.4285, +1.029] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5+pooled against B1 | 1371 | +27.7% [+14.9, +69.2] | +0.496 [+0.2088, +1.873] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5+pooled against B1p | 1371 | +8.2% [+1.8, +14.5] | +0.1155 [+0.02438, +0.232] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5+pooled against B2 | 1371 | +33.6% [+21.9, +44.3] | +0.6531 [+0.3866, +0.9929] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 1371 | -3.0% [-4.4, -1.8] | -0.03716 [-0.05826, -0.02185] | loss |

### scaled_grid_crps, by pressure-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| ordinary | spread_mr_fhs_mad20_f0.5 against B1 | 1371 | +25.1% [+16.4, +46.8] | +0.4471 [+0.2432, +1.089] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5 against B1p | 1371 | +11.3% [+5.9, +18.5] | +0.1702 [+0.07565, +0.344] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5 against B2 | 1371 | +28.1% [+18.3, +37.3] | +0.5207 [+0.3291, +0.7385] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5+pooled against B1 | 1371 | +22.6% [+13.5, +44.5] | +0.4028 [+0.2017, +1.025] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5+pooled against B1p | 1371 | +8.4% [+2.3, +16.0] | +0.1259 [+0.03083, +0.2917] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5+pooled against B2 | 1371 | +25.7% [+15.4, +35.1] | +0.4764 [+0.2797, +0.6956] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 1371 | -3.3% [-4.7, -2.0] | -0.04429 [-0.06497, -0.0275] | loss |

### upper_tail_twcrps, by pressure-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| ordinary | spread_mr_fhs_mad20_f0.5 against B1 | 1371 | +49.4% [+30.3, +105.3] | +0.4226 [+0.1285, +2.154] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5 against B1p | 1371 | +16.5% [+2.2, +28.2] | +0.08564 [+0.0135, +0.1925] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5 against B2 | 1371 | +18.4% [-0.3, +35.3] | +0.09739 [+0.008796, +0.2232] | gain (was undecided) |
| ordinary | spread_mr_fhs_mad20_f0.5+pooled against B1 | 1371 | +46.8% [+27.0, +105.3] | +0.4001 [+0.1115, +2.132] | gain |
| ordinary | spread_mr_fhs_mad20_f0.5+pooled against B1p | 1371 | +12.2% [-4.3, +25.9] | +0.06309 [-0.01081, +0.17] | undecided |
| ordinary | spread_mr_fhs_mad20_f0.5+pooled against B2 | 1371 | +14.1% [-6.4, +32.7] | +0.07485 [-0.01765, +0.2002] | undecided |
| ordinary | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 1371 | -5.2% [-8.0, -2.6] | -0.02254 [-0.04369, -0.01162] | loss |

### grid_crps, by pressure-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| quarter_end | spread_mr_fhs_mad20_f0.5 against B1 | 26 | +10.9% [+7.9, +13.8] | +0.5122 [+0.1527, +1.571] | gain |
| quarter_end | spread_mr_fhs_mad20_f0.5 against B1p | 26 | +9.7% [+6.7, +12.5] | +0.4519 [+0.1298, +1.305] | gain |
| quarter_end | spread_mr_fhs_mad20_f0.5 against B2 | 26 | +31.4% [-36.6, +70.3] | +1.924 [-0.782, +5.965] | undecided |
| quarter_end | spread_mr_fhs_mad20_f0.5+pooled against B1 | 26 | +14.1% [+11.0, +17.2] | +0.6661 [+0.1734, +2.348] | gain |
| quarter_end | spread_mr_fhs_mad20_f0.5+pooled against B1p | 26 | +13.0% [+9.7, +16.0] | +0.6059 [+0.1507, +2.032] | gain |
| quarter_end | spread_mr_fhs_mad20_f0.5+pooled against B2 | 26 | +33.9% [-30.9, +70.7] | +2.078 [-0.4416, +6.317] | undecided |
| quarter_end | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 26 | +3.7% [+2.5, +4.5] | +0.154 [-0.02144, +0.4624] | undecided (was gain) |

### scaled_grid_crps, by pressure-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| quarter_end | spread_mr_fhs_mad20_f0.5 against B1 | 26 | +14.7% [+11.4, +17.2] | +0.2262 [+0.03504, +0.888] | gain |
| quarter_end | spread_mr_fhs_mad20_f0.5 against B1p | 26 | +14.2% [+10.9, +16.7] | +0.2172 [+0.02682, +0.8928] | gain |
| quarter_end | spread_mr_fhs_mad20_f0.5 against B2 | 26 | +25.9% [-34.1, +71.9] | +0.4595 [-0.07589, +0.8955] | undecided |
| quarter_end | spread_mr_fhs_mad20_f0.5+pooled against B1 | 26 | +18.1% [+13.5, +21.2] | +0.2782 [+0.01784, +1.499] | gain |
| quarter_end | spread_mr_fhs_mad20_f0.5+pooled against B1p | 26 | +17.6% [+12.8, +21.0] | +0.2692 [+0.01021, +1.567] | gain |
| quarter_end | spread_mr_fhs_mad20_f0.5+pooled against B2 | 26 | +28.9% [-25.7, +69.7] | +0.5115 [+0.0704, +0.8493] | gain (was undecided) |
| quarter_end | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 26 | +4.0% [+0.6, +5.7] | +0.05202 [-0.02673, +0.2245] | undecided (was gain) |

### grid_crps, by pressure-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| tax_date | spread_mr_fhs_mad20_f0.5 against B1 | 77 | +5.4% [-1.4, +9.8] | +0.3156 [+0.02492, +1.139] | gain (was undecided) |
| tax_date | spread_mr_fhs_mad20_f0.5 against B1p | 77 | +4.3% [+2.4, +6.0] | +0.2482 [-0.02448, +1.196] | undecided (was gain) |
| tax_date | spread_mr_fhs_mad20_f0.5 against B2 | 77 | +32.2% [-78.4, +60.9] | +2.628 [+1.232, +5.742] | gain (was undecided) |
| tax_date | spread_mr_fhs_mad20_f0.5+pooled against B1 | 77 | +6.7% [+2.1, +10.0] | +0.3892 [+0.03441, +1.905] | gain |
| tax_date | spread_mr_fhs_mad20_f0.5+pooled against B1p | 77 | +5.6% [+4.3, +7.1] | +0.3218 [-0.02379, +2.109] | undecided (was gain) |
| tax_date | spread_mr_fhs_mad20_f0.5+pooled against B2 | 77 | +33.1% [-74.4, +61.1] | +2.702 [+1.241, +6.144] | gain (was undecided) |
| tax_date | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 77 | +1.3% [+0.4, +2.4] | +0.07359 [-0.0166, +0.7621] | undecided (was gain) |

### scaled_grid_crps, by pressure-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| tax_date | spread_mr_fhs_mad20_f0.5 against B1 | 77 | +8.4% [-6.1, +22.6] | +0.1582 [-0.005427, +0.4873] | undecided |
| tax_date | spread_mr_fhs_mad20_f0.5 against B1p | 77 | +5.4% [+1.6, +10.3] | +0.09823 [-0.01205, +0.3339] | undecided (was gain) |
| tax_date | spread_mr_fhs_mad20_f0.5 against B2 | 77 | +34.2% [-46.9, +56.8] | +0.9007 [+0.6623, +1.205] | gain (was undecided) |
| tax_date | spread_mr_fhs_mad20_f0.5+pooled against B1 | 77 | +9.2% [-0.9, +22.0] | +0.1734 [+0.002955, +0.597] | gain (was undecided) |
| tax_date | spread_mr_fhs_mad20_f0.5+pooled against B1p | 77 | +6.2% [+3.4, +10.2] | +0.1134 [-0.006937, +0.4805] | undecided (was gain) |
| tax_date | spread_mr_fhs_mad20_f0.5+pooled against B2 | 77 | +34.8% [-43.1, +56.8] | +0.9159 [+0.6641, +1.251] | gain (was undecided) |
| tax_date | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 77 | +0.9% [-0.9, +2.2] | +0.01522 [-0.009233, +0.08525] | undecided |

### grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2018-19 | spread_mr_fhs_mad20_f0.5 against B1 | 106 | +38.7% [+22.1, +104.1] | +3.999 [+0.4993, +66.12] | gain |
| 2018-19 | spread_mr_fhs_mad20_f0.5 against B1p | 106 | +1.9% [-4.8, +7.7] | +0.121 [-0.2454, +0.5208] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f0.5 against B2 | 106 | +4.5% [-11.2, +21.2] | +0.3005 [-0.6762, +1.851] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 106 | +37.7% [+21.9, +117.3] | +3.893 [+0.3355, +68.68] | gain |
| 2018-19 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 106 | +0.2% [-5.7, +4.9] | +0.01458 [-0.3433, +0.3854] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 106 | +2.9% [-12.7, +17.4] | +0.1941 [-0.861, +1.733] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 106 | -1.7% [-6.9, +7.6] | -0.1064 [-0.2385, +0.1116] | undecided |

### scaled_grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2018-19 | spread_mr_fhs_mad20_f0.5 against B1 | 104 | +50.3% [+32.3, +134.7] | +2.43 [+0.3002, +39.77] | gain |
| 2018-19 | spread_mr_fhs_mad20_f0.5 against B1p | 104 | -0.5% [-14.2, +10.0] | -0.01296 [-0.3046, +0.2279] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f0.5 against B2 | 104 | -2.6% [-17.4, +9.8] | -0.06141 [-0.4133, +0.3136] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 104 | +48.5% [+29.4, +145.9] | +2.346 [+0.2109, +41.32] | gain |
| 2018-19 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 104 | -4.1% [-15.3, +4.6] | -0.09696 [-0.373, +0.1221] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 104 | -6.2% [-23.7, +7.2] | -0.1454 [-0.5424, +0.2626] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 104 | -3.5% [-9.1, +5.5] | -0.084 [-0.177, -0.01622] | loss (was undecided) |

### upper_tail_twcrps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2018-19 | spread_mr_fhs_mad20_f0.5 against B1 | 106 | +39.0% [+21.2, +105.4] | +3.923 [+0.3844, +62.31] | gain |
| 2018-19 | spread_mr_fhs_mad20_f0.5 against B1p | 106 | +1.6% [-5.2, +7.9] | +0.1028 [-0.2702, +0.5579] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f0.5 against B2 | 106 | +4.2% [-10.5, +19.5] | +0.267 [-0.6385, +1.608] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 106 | +38.1% [+21.4, +116.4] | +3.827 [+0.2403, +64.03] | gain |
| 2018-19 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 106 | +0.1% [-6.2, +5.5] | +0.006287 [-0.3625, +0.4289] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 106 | +2.7% [-12.0, +16.3] | +0.1705 [-0.8047, +1.524] | undecided |
| 2018-19 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 106 | -1.6% [-7.0, +8.6] | -0.09653 [-0.2211, +0.1344] | undecided |

### grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2020 | spread_mr_fhs_mad20_f0.5 against B1 | 251 | +14.6% [+6.5, +22.8] | +0.2409 [+0.09461, +0.5759] | gain |
| 2020 | spread_mr_fhs_mad20_f0.5 against B1p | 251 | +12.6% [+2.7, +26.7] | +0.2022 [+0.02212, +0.7148] | gain |
| 2020 | spread_mr_fhs_mad20_f0.5 against B2 | 251 | +49.7% [+24.0, +70.0] | +1.39 [+0.5597, +3.093] | gain |
| 2020 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 251 | +13.2% [+5.0, +23.0] | +0.2182 [+0.06587, +0.5933] | gain |
| 2020 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 251 | +11.2% [+0.3, +28.3] | +0.1796 [-0.007619, +0.7376] | undecided (was gain) |
| 2020 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 251 | +48.9% [+23.8, +69.6] | +1.367 [+0.5284, +3.079] | gain |
| 2020 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 251 | -1.6% [-3.6, +1.2] | -0.02263 [-0.03622, -0.002368] | loss (was undecided) |

### scaled_grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2020 | spread_mr_fhs_mad20_f0.5 against B1 | 251 | +15.3% [+8.1, +24.1] | +0.1186 [+0.04911, +0.2992] | gain |
| 2020 | spread_mr_fhs_mad20_f0.5 against B1p | 251 | +12.6% [+2.8, +28.8] | +0.09407 [+0.00773, +0.3667] | gain |
| 2020 | spread_mr_fhs_mad20_f0.5 against B2 | 251 | +43.8% [+17.3, +65.3] | +0.5108 [+0.1904, +1.082] | gain |
| 2020 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 251 | +13.8% [+6.2, +24.7] | +0.1071 [+0.03458, +0.3082] | gain |
| 2020 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 251 | +11.0% [-0.0, +30.9] | +0.08257 [-0.007335, +0.3786] | undecided |
| 2020 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 251 | +42.8% [+17.1, +64.8] | +0.4993 [+0.1766, +1.074] | gain |
| 2020 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 251 | -1.8% [-3.8, +0.9] | -0.0115 [-0.01858, -0.002309] | loss (was undecided) |

### upper_tail_twcrps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2020 | spread_mr_fhs_mad20_f0.5 against B1 | 251 | +31.0% [+16.8, +55.5] | +0.2293 [+0.05455, +1.621] | gain |
| 2020 | spread_mr_fhs_mad20_f0.5 against B1p | 251 | +32.1% [+19.4, +63.9] | +0.2412 [+0.03314, +2.161] | gain |
| 2020 | spread_mr_fhs_mad20_f0.5 against B2 | 251 | +58.1% [-25.1, +84.6] | +0.7083 [+0.3551, +1.135] | gain (was undecided) |
| 2020 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 251 | +28.5% [+15.1, +60.2] | +0.2106 [+0.02957, +1.606] | gain |
| 2020 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 251 | +29.6% [+15.6, +69.6] | +0.2225 [+0.00822, +2.137] | gain |
| 2020 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 251 | +56.6% [-17.8, +82.6] | +0.6896 [+0.3336, +1.117] | gain (was undecided) |
| 2020 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 251 | -3.7% [-11.0, +10.1] | -0.01867 [-0.02731, -0.001669] | loss (was undecided) |

### grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2021-23 | spread_mr_fhs_mad20_f0.5 against B1 | 748 | +5.5% [-0.5, +10.7] | +0.03824 [-0.00013, +0.0708] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f0.5 against B1p | 748 | +1.0% [-5.2, +6.6] | +0.006723 [-0.03471, +0.04264] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f0.5 against B2 | 748 | +55.0% [+41.3, +67.8] | +0.8061 [+0.5108, +1.189] | gain |
| 2021-23 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 748 | +4.3% [-2.7, +10.6] | +0.03002 [-0.01724, +0.07019] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 748 | -0.2% [-7.9, +6.4] | -0.001497 [-0.05405, +0.04172] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 748 | +54.5% [+40.0, +67.4] | +0.7978 [+0.4975, +1.18] | gain |
| 2021-23 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 748 | -1.2% [-4.8, +1.1] | -0.008219 [-0.03198, +0.006737] | undecided |

### scaled_grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2021-23 | spread_mr_fhs_mad20_f0.5 against B1 | 748 | +4.9% [+0.5, +8.8] | +0.04088 [+0.006202, +0.07568] | gain |
| 2021-23 | spread_mr_fhs_mad20_f0.5 against B1p | 748 | -1.0% [-5.8, +3.7] | -0.007506 [-0.04528, +0.02876] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f0.5 against B2 | 748 | +43.9% [+30.4, +56.6] | +0.6224 [+0.4045, +0.8795] | gain |
| 2021-23 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 748 | +3.2% [-2.5, +8.4] | +0.02666 [-0.01749, +0.07267] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 748 | -2.8% [-9.2, +3.3] | -0.02172 [-0.07002, +0.02476] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 748 | +42.9% [+29.0, +55.8] | +0.6081 [+0.3842, +0.8673] | gain |
| 2021-23 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 748 | -1.8% [-4.5, +0.5] | -0.01421 [-0.03477, +0.002676] | undecided |

### upper_tail_twcrps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2021-23 | spread_mr_fhs_mad20_f0.5 against B1 | 748 | +12.3% [-64.6, +44.5] | +0.0011 [-0.003806, +0.003362] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f0.5 against B1p | 748 | -16.5% [-105.6, +17.7] | -0.001111 [-0.009813, +0.001242] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f0.5 against B2 | 748 | -156.2% [-802.3, -33.9] | -0.004779 [-0.04836, +0.0003283] | undecided (was loss) |
| 2021-23 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 748 | +13.1% [-71.3, +44.8] | +0.001168 [-0.00353, +0.00339] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 748 | -15.5% [-101.1, +16.9] | -0.001043 [-0.009197, +0.001212] | undecided |
| 2021-23 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 748 | -154.0% [-836.3, -34.1] | -0.004711 [-0.05119, +0.0003274] | undecided (was loss) |
| 2021-23 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 748 | +0.9% [-2.9, +4.0] | +6.759e-05 [-0.0002248, +0.0004502] | undecided |

### grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2024 | spread_mr_fhs_mad20_f0.5 against B1 | 250 | +25.3% [+18.7, +35.5] | +0.4088 [+0.2025, +0.9724] | gain |
| 2024 | spread_mr_fhs_mad20_f0.5 against B1p | 250 | +19.0% [+11.3, +29.7] | +0.2819 [+0.1073, +0.7125] | gain |
| 2024 | spread_mr_fhs_mad20_f0.5 against B2 | 250 | +13.6% [+2.8, +23.2] | +0.19 [+0.0353, +0.3846] | gain |
| 2024 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 250 | +23.2% [+15.1, +35.2] | +0.3738 [+0.1566, +0.9563] | gain |
| 2024 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 250 | +16.6% [+7.4, +29.1] | +0.2469 [+0.06151, +0.6977] | gain |
| 2024 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 250 | +11.1% [-0.6, +20.6] | +0.1551 [-0.009636, +0.3572] | undecided |
| 2024 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 250 | -2.9% [-6.2, +0.2] | -0.03497 [-0.05966, -0.006025] | loss (was undecided) |

### scaled_grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2024 | spread_mr_fhs_mad20_f0.5 against B1 | 250 | +24.3% [+17.5, +34.8] | +0.8229 [+0.4394, +1.741] | gain |
| 2024 | spread_mr_fhs_mad20_f0.5 against B1p | 250 | +17.7% [+9.7, +28.0] | +0.5496 [+0.2112, +1.231] | gain |
| 2024 | spread_mr_fhs_mad20_f0.5 against B2 | 250 | +16.8% [+3.6, +30.7] | +0.5158 [+0.08178, +1.16] | gain |
| 2024 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 250 | +21.5% [+13.0, +33.9] | +0.7278 [+0.3129, +1.668] | gain |
| 2024 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 250 | +14.6% [+4.8, +26.7] | +0.4546 [+0.0871, +1.174] | gain |
| 2024 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 250 | +13.7% [-0.0, +26.4] | +0.4208 [-0.02005, +1.027] | undecided |
| 2024 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 250 | -3.7% [-7.2, -0.7] | -0.09501 [-0.1547, -0.03081] | loss |

### grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2025-26 | spread_mr_fhs_mad20_f0.5 against B1 | 249 | +23.4% [+16.3, +30.2] | +0.7857 [+0.436, +1.261] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.5 against B1p | 249 | +16.2% [+8.8, +23.5] | +0.4967 [+0.2164, +0.875] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.5 against B2 | 249 | +31.9% [+7.0, +52.5] | +1.204 [+0.1148, +3.122] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 249 | +22.3% [+15.2, +29.1] | +0.7483 [+0.4038, +1.209] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 249 | +15.0% [+7.7, +21.9] | +0.4594 [+0.185, +0.8148] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 249 | +30.9% [+5.8, +52.6] | +1.167 [+0.07485, +3.111] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 249 | -1.5% [-3.3, +0.0] | -0.03733 [-0.08691, -0.001692] | loss (was undecided) |

### scaled_grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2025-26 | spread_mr_fhs_mad20_f0.5 against B1 | 249 | +21.2% [+11.1, +29.8] | +0.5743 [+0.2994, +1.005] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.5 against B1p | 249 | +15.4% [+4.0, +28.8] | +0.3888 [+0.1156, +0.9423] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.5 against B2 | 249 | +22.3% [-6.6, +48.7] | +0.6142 [-0.104, +1.715] | undecided |
| 2025-26 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 249 | +19.5% [+9.2, +27.7] | +0.5293 [+0.2612, +0.903] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 249 | +13.6% [+2.6, +25.5] | +0.3439 [+0.08361, +0.8142] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 249 | +20.7% [-10.2, +48.5] | +0.5692 [-0.1746, +1.672] | undecided |
| 2025-26 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 249 | -2.1% [-5.5, -0.3] | -0.04495 [-0.1407, -0.007567] | loss |

### upper_tail_twcrps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2025-26 | spread_mr_fhs_mad20_f0.5 against B1 | 249 | +32.3% [+25.9, +39.4] | +0.5183 [+0.1777, +1.215] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.5 against B1p | 249 | +22.3% [+14.7, +31.2] | +0.3108 [+0.08897, +0.7246] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.5 against B2 | 249 | +29.6% [+13.7, +49.6] | +0.455 [+0.008164, +2.201] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.5+pooled against B1 | 249 | +30.5% [+24.2, +37.4] | +0.4889 [+0.1441, +1.163] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.5+pooled against B1p | 249 | +20.2% [+12.2, +29.0] | +0.2814 [+0.05913, +0.6899] | gain |
| 2025-26 | spread_mr_fhs_mad20_f0.5+pooled against B2 | 249 | +27.6% [+9.4, +50.2] | +0.4256 [-0.02539, +2.195] | undecided (was gain) |
| 2025-26 | spread_mr_fhs_mad20_f0.5+pooled against spread_mr_fhs_mad20_f0.5 | 249 | -2.7% [-6.0, +0.4] | -0.02942 [-0.05487, -0.004121] | loss (was undecided) |

Nothing here is a verdict for a hypothesis. The originals stand.
