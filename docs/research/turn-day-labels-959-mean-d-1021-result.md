# Turn-day labels against the month-end label (#959), read on the mean-d bound (#1021; H5 step 2, reporting)

**Development data, not a verdict.** No re-scoring, no lockbox day, and no published declaration, record or decided value moves. Every figure is read from `docs/research/turn-day-labels-959/result.json`, the record of the original page (`turn-day-labels-959-result.md`, which stands), by `scripts/mean_d_reading_1021.py report`.

## What changes and why

The original page read each row from the studentized skill interval. The skill interval and the interval on the mean difference d are built from different studentized draws, so their ends can fall on different sides of zero (#1009). The protocol's verdict reads the one-sided studentized bound on mean d (ruling 1/5). By Eleonora's ruling on #1009 this page shows both intervals for every row and reads the mean-d bound: **better** when the lower bound of mean d is above zero, **worse** when its upper bound is below zero, **no difference** otherwise. The 90% two-sided interval on mean d is the pair of one-sided 95% bounds. d = S(benchmark) − S(candidate), positive favouring the candidate; skill is mean(d) / mean(S(benchmark)); seed 959, 10,000 draws, as on the original page.

**Caveat (Lens C of the five-lens review, #958).** The lag-10 HAC standard error that studentizes the mean-d bound is understated about 2× after 2020 (about 2.3× in 2021–23, 1.7× in 2024–26), and the bootstrap block of 10 days is an order of magnitude shorter than the autocorrelation of d. The bound is therefore optimistic: an interval that excludes zero here is narrower than it should be after 2020. A development reading on this page is evidence for a question, not a verdict.

## Rows whose reading changes

| section | group | comparison | skill [90%] | mean d [90%] | reading on the skill interval | reading on the mean-d bound |
|---|---|---|---|---|---|---|
| a | regime 2020 | B1 -> B2 as is | -69.5% [-178.8, +5.4] | -1.1422 [-2.8148, -0.2830] | no difference | **candidate worse** |
| a | regime 2020 | B1 -> B2 relabelled | -74.7% [-186.8, +3.8] | -1.2274 [-2.9427, -0.3446] | no difference | **candidate worse** |
| a | regime 2025-26 | B2 as is -> B2 relabelled | +1.3% [-0.3, +3.0] | +0.0484 [+0.0041, +0.0964] | no difference | **candidate better** |
| a | target: december_26 | B1 -> B2 as is | -20.4% [-54.7, +14.4] | -1.4107 [-2.1542, -0.2396] | no difference | **candidate worse** |
| a | target: december_26 | B1 -> B2 relabelled | -22.2% [-54.9, +13.4] | -1.5345 [-2.1779, -0.5057] | no difference | **candidate worse** |
| a | target: december_26 | B2 as is -> B2 relabelled | -1.5% [-2.2, -0.6] | -0.1238 [-0.2856, +0.0937] | candidate worse | **no difference** |
| a | target: tax_date | B1 -> B2 as is | -47.3% [-117.0, +54.4] | -2.2657 [-3.7019, -1.4009] | no difference | **candidate worse** |
| a | target: tax_date | B1 -> B2 relabelled | -47.3% [-117.0, +54.4] | -2.2657 [-3.7019, -1.4009] | no difference | **candidate worse** |
| a | target: year_end | B1 -> B2 as is | -103.2% [-686.5, +59.7] | -2.7754 [-20.9024, -0.1570] | no difference | **candidate worse** |
| a | target: year_end | B1 -> B2 relabelled | -458.6% [-3451.1, +360.3] | -12.3329 [-117.3930, -0.3803] | no difference | **candidate worse** |
| b | target: tax_date | as is -> turn days and tax dates excluded | -0.6% [-1.1, -0.1] | -0.0310 [-0.1184, +0.0090] | candidate worse | **no difference** |
| b | target: tax_date | as is -> turn days only excluded | -0.8% [-1.2, -0.5] | -0.0408 [-0.1562, +0.0006] | candidate worse | **no difference** |
| b | target: year_end | as is -> turn days and tax dates excluded | +0.3% [-0.1, +0.7] | +0.0295 [+0.0144, +0.0439] | no difference | **candidate better** |
| c / sets / as is | pooled | B1 -> calendar | -36.6% [-87.2, +4.4] | -1.1107 [-2.0138, -0.5064] | no difference | **candidate worse** |
| c / sets / as is | type: settlement | B1 -> calendar | -55.2% [-138.1, +1.9] | -0.8860 [-1.7121, -0.2386] | no difference | **candidate worse** |
| c / sets / as is | type: tax_date | B1 -> calendar | -42.5% [-102.8, +47.1] | -2.2603 [-3.9297, -1.3112] | no difference | **candidate worse** |
| c / sets / turn set | type: settlement | B1 -> calendar | -48.1% [-136.8, +23.3] | -0.7736 [-1.5442, -0.0585] | no difference | **candidate worse** |
| c / sets / turn set | type: tax_date | B1 -> calendar | -42.5% [-102.8, +47.1] | -2.2603 [-3.9297, -1.3112] | no difference | **candidate worse** |

Every other tested row reads the same on both intervals.

## All tested rows

Rows the scorer left undefined (scores identical, or a zero benchmark) are on the original page and carry no interval here.

### a

| group | comparison | decision or target days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| pooled | B1 -> B2 as is | 1900 | -8.7% [-28.8, +23.1] | -0.1951 [-0.5257, +0.4751] | no difference |
| pooled | B1 -> B2 relabelled | 1900 | -11.9% [-33.6, +19.1] | -0.2671 [-0.6191, +0.3448] | no difference |
| pooled | B2 as is -> B2 relabelled | 1900 | -3.0% [-13.0, -0.5] | -0.0720 [-0.3257, -0.0110] | candidate worse |
| regime 2018-19 | B1 -> B2 as is | 407 | +25.4% [+7.4, +61.9] | +1.3177 [+0.1590, +6.1402] | candidate better |
| regime 2018-19 | B1 -> B2 relabelled | 407 | +19.9% [-5.3, +51.6] | +1.0317 [-0.2279, +4.2399] | no difference |
| regime 2018-19 | B2 as is -> B2 relabelled | 407 | -7.4% [-49.4, -0.2] | -0.2860 [-2.0334, -0.0111] | candidate worse |
| regime 2020 | B1 -> B2 as is | 251 | -69.5% [-178.8, +5.4] | -1.1422 [-2.8148, -0.2830] | candidate worse (was no difference) |
| regime 2020 | B1 -> B2 relabelled | 251 | -74.7% [-186.8, +3.8] | -1.2274 [-2.9427, -0.3446] | candidate worse (was no difference) |
| regime 2020 | B2 as is -> B2 relabelled | 251 | -3.1% [-5.1, -1.6] | -0.0852 [-0.1590, -0.0403] | candidate worse |
| regime 2021-23 | B1 -> B2 as is | 748 | -108.4% [-169.6, -63.6] | -0.7703 [-1.1335, -0.4884] | candidate worse |
| regime 2021-23 | B1 -> B2 relabelled | 748 | -112.2% [-172.9, -67.0] | -0.7972 [-1.1568, -0.5200] | candidate worse |
| regime 2021-23 | B2 as is -> B2 relabelled | 748 | -1.8% [-7.5, +0.1] | -0.0269 [-0.1095, +0.0017] | no difference |
| regime 2024 | B1 -> B2 as is | 250 | +18.1% [+1.5, +36.9] | +0.3051 [+0.0106, +0.9363] | candidate better |
| regime 2024 | B1 -> B2 relabelled | 250 | +20.3% [+3.1, +39.4] | +0.3425 [+0.0330, +1.0073] | candidate better |
| regime 2024 | B2 as is -> B2 relabelled | 250 | +2.7% [+0.9, +5.0] | +0.0373 [+0.0139, +0.0751] | candidate better |
| regime 2025-26 | B1 -> B2 as is | 244 | -15.3% [-50.8, +9.4] | -0.4931 [-1.7382, +0.3265] | no difference |
| regime 2025-26 | B1 -> B2 relabelled | 244 | -13.8% [-51.0, +12.2] | -0.4447 [-1.7331, +0.4090] | no difference |
| regime 2025-26 | B2 as is -> B2 relabelled | 244 | +1.3% [-0.3, +3.0] | +0.0484 [+0.0041, +0.0964] | candidate better (was no difference) |
| target: december_26 | B1 -> B2 as is | 22 | -20.4% [-54.7, +14.4] | -1.4107 [-2.1542, -0.2396] | candidate worse (was no difference) |
| target: december_26 | B1 -> B2 relabelled | 22 | -22.2% [-54.9, +13.4] | -1.5345 [-2.1779, -0.5057] | candidate worse (was no difference) |
| target: december_26 | B2 as is -> B2 relabelled | 22 | -1.5% [-2.2, -0.6] | -0.1238 [-0.2856, +0.0937] | no difference (was candidate worse) |
| target: ordinary | B1 -> B2 as is | 1900 | -5.7% [-26.9, +29.3] | -0.1091 [-0.4269, +0.5771] | no difference |
| target: ordinary | B1 -> B2 relabelled | 1900 | -6.2% [-27.1, +29.1] | -0.1169 [-0.4316, +0.5663] | no difference |
| target: ordinary | B2 as is -> B2 relabelled | 1900 | -0.4% [-1.4, +0.7] | -0.0079 [-0.0290, +0.0127] | no difference |
| target: penultimate days | B1 -> B2 as is | 449 | -51.2% [-109.5, -8.5] | -0.7421 [-1.5183, -0.1875] | candidate worse |
| target: penultimate days | B1 -> B2 relabelled | 449 | -46.4% [-94.4, -6.5] | -0.6727 [-1.3345, -0.1824] | candidate worse |
| target: penultimate days | B2 as is -> B2 relabelled | 449 | +3.2% [-6.8, +14.6] | +0.0694 [-0.1358, +0.3443] | no difference |
| target: quarter_end_turn | B1 -> B2 as is | 132 | -13.4% [-62.5, +17.8] | -0.5889 [-2.0681, +0.8900] | no difference |
| target: quarter_end_turn | B1 -> B2 relabelled | 132 | -20.9% [-98.4, +19.7] | -0.9157 [-3.4193, +0.9436] | no difference |
| target: quarter_end_turn | B2 as is -> B2 relabelled | 132 | -6.6% [-36.0, +17.3] | -0.3268 [-1.8732, +0.6597] | no difference |
| target: tax_date | B1 -> B2 as is | 222 | -47.3% [-117.0, +54.4] | -2.2657 [-3.7019, -1.4009] | candidate worse (was no difference) |
| target: tax_date | B1 -> B2 relabelled | 222 | -47.3% [-117.0, +54.4] | -2.2657 [-3.7019, -1.4009] | candidate worse (was no difference) |
| target: turn | B1 -> B2 as is | 366 | -25.7% [-56.5, -4.3] | -0.6942 [-1.6977, -0.1673] | candidate worse |
| target: turn | B1 -> B2 relabelled | 366 | -23.3% [-64.1, +3.1] | -0.6299 [-1.7229, +0.0477] | no difference |
| target: turn | B2 as is -> B2 relabelled | 366 | +1.9% [-14.5, +11.8] | +0.0644 [-0.4299, +0.4445] | no difference |
| target: turn days (all three labels) | B1 -> B2 as is | 535 | -26.0% [-56.4, -1.7] | -0.8122 [-1.6378, -0.1625] | candidate worse |
| target: turn days (all three labels) | B1 -> B2 relabelled | 535 | -48.4% [-155.4, -8.9] | -1.5098 [-4.5698, -0.3535] | candidate worse |
| target: turn days (all three labels) | B2 as is -> B2 relabelled | 535 | -17.7% [-88.4, +3.9] | -0.6976 [-3.5522, +0.1209] | no difference |
| target: year_end | B1 -> B2 as is | 37 | -103.2% [-686.5, +59.7] | -2.7754 [-20.9024, -0.1570] | candidate worse (was no difference) |
| target: year_end | B1 -> B2 relabelled | 37 | -458.6% [-3451.1, +360.3] | -12.3329 [-117.3930, -0.3803] | candidate worse (was no difference) |
| target: year_end | B2 as is -> B2 relabelled | 37 | -174.9% [-603.5, +49.3] | -9.5574 [-75.0038, +0.0104] | no difference |

### b

| group | comparison | decision or target days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| pooled | as is -> turn days and tax dates excluded | 1855 | -0.1% [-0.5, +0.2] | -0.0022 [-0.0087, +0.0038] | no difference |
| pooled | as is -> turn days only excluded | 1855 | -1.0% [-3.7, +0.1] | -0.0177 [-0.0673, +0.0026] | no difference |
| regime 2018-19 | as is -> turn days and tax dates excluded | 362 | +0.1% [-0.5, +0.7] | +0.0041 [-0.0184, +0.0210] | no difference |
| regime 2018-19 | as is -> turn days only excluded | 362 | -1.6% [-8.9, +0.6] | -0.0611 [-0.3863, +0.0286] | no difference |
| regime 2020 | as is -> turn days and tax dates excluded | 251 | -0.4% [-1.4, +0.4] | -0.0070 [-0.0227, +0.0068] | no difference |
| regime 2020 | as is -> turn days only excluded | 251 | +0.5% [-0.9, +1.6] | +0.0071 [-0.0143, +0.0281] | no difference |
| regime 2021-23 | as is -> turn days and tax dates excluded | 748 | +0.1% [-0.5, +0.7] | +0.0007 [-0.0033, +0.0052] | no difference |
| regime 2021-23 | as is -> turn days only excluded | 748 | -2.0% [-7.0, +0.1] | -0.0146 [-0.0557, +0.0001] | no difference |
| regime 2024 | as is -> turn days and tax dates excluded | 250 | -0.1% [-1.0, +0.8] | -0.0020 [-0.0126, +0.0095] | no difference |
| regime 2024 | as is -> turn days only excluded | 250 | -0.5% [-2.7, +2.6] | -0.0063 [-0.0326, +0.0285] | no difference |
| regime 2025-26 | as is -> turn days and tax dates excluded | 244 | -0.6% [-1.8, +0.6] | -0.0160 [-0.0468, +0.0174] | no difference |
| regime 2025-26 | as is -> turn days only excluded | 244 | -0.0% [-1.5, +1.5] | -0.0002 [-0.0390, +0.0429] | no difference |
| target: december_26 | as is -> turn days and tax dates excluded | 24 | -1.2% [-5.1, +0.3] | -0.0640 [-0.4397, +0.0287] | no difference |
| target: december_26 | as is -> turn days only excluded | 24 | +4.2% [+1.8, +5.9] | +0.2260 [+0.0341, +0.7705] | candidate better |
| target: ordinary | as is -> turn days and tax dates excluded | 1855 | -0.1% [-0.6, +0.3] | -0.0020 [-0.0082, +0.0045] | no difference |
| target: ordinary | as is -> turn days only excluded | 1855 | -1.7% [-7.3, +0.2] | -0.0234 [-0.1008, +0.0028] | no difference |
| target: penultimate days | as is -> turn days and tax dates excluded | 447 | -0.2% [-0.9, +0.3] | -0.0032 [-0.0117, +0.0037] | no difference |
| target: penultimate days | as is -> turn days only excluded | 447 | -4.4% [-23.4, +0.2] | -0.0589 [-0.3303, +0.0003] | no difference |
| target: quarter_end_turn | as is -> turn days and tax dates excluded | 132 | +0.4% [+0.2, +0.6] | +0.0188 [+0.0065, +0.0372] | candidate better |
| target: quarter_end_turn | as is -> turn days only excluded | 132 | +0.2% [-2.5, +2.3] | +0.0087 [-0.1004, +0.1189] | no difference |
| target: tax_date | as is -> turn days and tax dates excluded | 214 | -0.6% [-1.1, -0.1] | -0.0310 [-0.1184, +0.0090] | no difference (was candidate worse) |
| target: tax_date | as is -> turn days only excluded | 214 | -0.8% [-1.2, -0.5] | -0.0408 [-0.1562, +0.0006] | no difference (was candidate worse) |
| target: turn | as is -> turn days and tax dates excluded | 360 | +0.8% [+0.6, +1.2] | +0.0207 [+0.0107, +0.0333] | candidate better |
| target: turn | as is -> turn days only excluded | 360 | +0.8% [-0.0, +1.9] | +0.0204 [-0.0015, +0.0535] | no difference |
| target: turn days (all three labels) | as is -> turn days and tax dates excluded | 535 | +0.6% [+0.4, +0.8] | +0.0209 [+0.0128, +0.0310] | candidate better |
| target: turn days (all three labels) | as is -> turn days only excluded | 535 | +0.8% [-0.2, +1.6] | +0.0280 [-0.0083, +0.0665] | no difference |
| target: year_end | as is -> turn days and tax dates excluded | 43 | +0.3% [-0.1, +0.7] | +0.0295 [+0.0144, +0.0439] | candidate better (was no difference) |
| target: year_end | as is -> turn days only excluded | 43 | +1.4% [+0.2, +2.9] | +0.1512 [+0.0315, +0.4453] | candidate better |

### c / cross

| group | comparison | decision or target days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| pooled | as is -> turn set | 307 | -5.8% [-14.7, -2.4] | -0.2675 [-0.9039, -0.0803] | candidate worse |
| regime 2018-19 | as is -> turn set | 64 | -8.2% [-27.5, -0.4] | -0.9060 [-3.9759, -0.0722] | candidate worse |
| regime 2020 | as is -> turn set | 42 | -5.2% [-9.6, -1.8] | -0.2117 [-0.4306, -0.0874] | candidate worse |
| regime 2021-23 | as is -> turn set | 124 | -6.5% [-18.5, -1.9] | -0.1297 [-0.3403, -0.0303] | candidate worse |
| regime 2024 | as is -> turn set | 40 | -2.5% [-8.3, +4.8] | -0.0649 [-0.2957, +0.1318] | no difference |
| regime 2025-26 | as is -> turn set | 37 | +1.7% [-0.5, +4.0] | +0.0926 [-0.0525, +0.2668] | no difference |

### c / sets / as is

| group | comparison | decision or target days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| pooled | B1 -> calendar | 391 | -36.6% [-87.2, +4.4] | -1.1107 [-2.0138, -0.5064] | candidate worse (was no difference) |
| regime 2018-19 | B1 -> calendar | 83 | -5.1% [-28.6, +7.1] | -0.4403 [-1.8932, +0.4547] | no difference |
| regime 2020 | B1 -> calendar | 52 | -254.2% [-848.6, -48.8] | -2.8645 [-11.1648, -0.3763] | candidate worse |
| regime 2021-23 | B1 -> calendar | 158 | -168.4% [-365.4, -85.2] | -1.2206 [-2.1503, -0.6548] | candidate worse |
| regime 2024 | B1 -> calendar | 51 | -11.2% [-30.5, +6.1] | -0.2188 [-0.5533, +0.0329] | no difference |
| regime 2025-26 | B1 -> calendar | 47 | -22.3% [-184.2, +54.3] | -0.9524 [-8.7551, +1.7987] | no difference |
| type: month_end | B1 -> calendar | 153 | -27.0% [-63.6, -0.2] | -0.6221 [-1.3985, -0.0656] | candidate worse |
| type: quarter_end | B1 -> calendar | 29 | -16.9% [-100.0, +33.9] | -0.9002 [-3.7571, +2.0024] | no difference |
| type: settlement | B1 -> calendar | 116 | -55.2% [-138.1, +1.9] | -0.8860 [-1.7121, -0.2386] | candidate worse (was no difference) |
| type: tax_date | B1 -> calendar | 93 | -42.5% [-102.8, +47.1] | -2.2603 [-3.9297, -1.3112] | candidate worse (was no difference) |

### c / sets / turn set

| group | comparison | decision or target days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| pooled | B1 -> calendar | 370 | -45.9% [-121.5, -2.0] | -1.5069 [-3.5003, -0.6802] | candidate worse |
| regime 2018-19 | B1 -> calendar | 76 | -11.2% [-96.4, +6.3] | -1.0655 [-6.4784, +0.2480] | no difference |
| regime 2020 | B1 -> calendar | 51 | -399.4% [-1051.8, -98.3] | -4.6028 [-13.7731, -0.3479] | candidate worse |
| regime 2021-23 | B1 -> calendar | 150 | -178.4% [-380.1, -87.5] | -1.3474 [-2.2365, -0.7464] | candidate worse |
| regime 2024 | B1 -> calendar | 47 | -12.1% [-31.6, +5.7] | -0.2981 [-0.7734, +0.0476] | no difference |
| regime 2025-26 | B1 -> calendar | 46 | -12.4% [-157.7, +50.7] | -0.5589 [-7.4103, +1.7921] | no difference |
| type: quarter_end_turn | B1 -> calendar | 44 | -21.8% [-112.3, +35.8] | -0.9497 [-3.5591, +1.6957] | no difference |
| type: settlement | B1 -> calendar | 98 | -48.1% [-136.8, +23.3] | -0.7736 [-1.5442, -0.0585] | candidate worse (was no difference) |
| type: tax_date | B1 -> calendar | 93 | -42.5% [-102.8, +47.1] | -2.2603 [-3.9297, -1.3112] | candidate worse (was no difference) |
| type: turn | B1 -> calendar | 122 | -23.9% [-66.2, +3.1] | -0.6430 [-1.6865, +0.0282] | no difference |

Nothing here is a verdict for a hypothesis. The originals stand.
