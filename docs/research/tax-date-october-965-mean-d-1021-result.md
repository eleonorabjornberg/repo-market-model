# 15 October as a tax date (#965), read on the mean-d bound (#1021; H5 step 2, reporting)

**Development data, not a verdict.** No re-scoring, no lockbox day, and no published declaration, record or decided value moves. Every figure is read from `docs/research/tax-date-october-965/result.json`, the record of the original page (`tax-date-october-965-result.md`, which stands), by `scripts/mean_d_reading_1021.py report`.

## What changes and why

The original page read each row from the studentized skill interval. The skill interval and the interval on the mean difference d are built from different studentized draws, so their ends can fall on different sides of zero (#1009). The protocol's verdict reads the one-sided studentized bound on mean d (ruling 1/5). By Eleonora's ruling on #1009 this page shows both intervals for every row and reads the mean-d bound: **better** when the lower bound of mean d is above zero, **worse** when its upper bound is below zero, **no difference** otherwise. The 90% two-sided interval on mean d is the pair of one-sided 95% bounds. d = S(benchmark) − S(candidate), positive favouring the candidate; skill is mean(d) / mean(S(benchmark)); seed 965, 10,000 draws, as on the original page.

**Caveat (Lens C of the five-lens review, #958).** The lag-10 HAC standard error that studentizes the mean-d bound is understated about 2× after 2020 (about 2.3× in 2021–23, 1.7× in 2024–26), and the bootstrap block of 10 days is an order of magnitude shorter than the autocorrelation of d. The bound is therefore optimistic: an interval that excludes zero here is narrower than it should be after 2020. A development reading on this page is evidence for a question, not a verdict.

## Rows whose reading changes

| section | group | comparison | skill [90%] | mean d [90%] | reading on the skill interval | reading on the mean-d bound |
|---|---|---|---|---|---|---|
| a / crps | regime 2020 | B1 -> B2 as is | -69.5% [-176.7, +5.7] | -1.1422 [-2.8499, -0.2730] | no difference | **candidate worse** |
| a / crps | regime 2020 | B1 -> B2 control | -65.3% [-165.6, +12.2] | -1.0728 [-2.6086, -0.2046] | no difference | **candidate worse** |
| a / crps | regime 2020 | B1 -> B2 october | -70.2% [-178.4, +4.9] | -1.1539 [-2.8878, -0.2787] | no difference | **candidate worse** |
| a / crps | target: october window | B2 as is -> B2 october | +16.7% [+2.8, +36.6] | +0.6697 [-0.1871, +2.6345] | candidate better | **no difference** |
| a / crps | target: tax_date as is | B1 -> B2 as is | -47.3% [-119.5, +54.0] | -2.2657 [-3.7119, -1.3712] | no difference | **candidate worse** |
| a / crps | target: tax_date as is | B1 -> B2 control | -34.5% [-87.5, +37.1] | -1.6508 [-2.5504, -0.9794] | no difference | **candidate worse** |
| a / crps | target: tax_date as is | B1 -> B2 october | -49.8% [-126.9, +45.9] | -2.3845 [-4.2078, -1.3382] | no difference | **candidate worse** |
| a / crps | target: tax_date as is | B2 as is -> B2 control | +8.7% [-3.3, +18.7] | +0.6149 [+0.2389, +1.1786] | no difference | **candidate better** |
| a / twcrps | pooled | B1 -> B2 as is | +18.6% [+1.4, +49.4] | +0.2543 [-0.0009, +1.1469] | candidate better | **no difference** |
| a / twcrps | pooled | B1 -> B2 october | +18.9% [+1.5, +48.9] | +0.2577 [-0.0009, +1.1339] | candidate better | **no difference** |
| a / twcrps | regime 2024 | B1 -> B2 control | +39.0% [-0.2, +157.5] | +0.1255 [+0.0216, +14.6491] | no difference | **candidate better** |
| a / twcrps | target: control window | B1 -> B2 as is | -17.8% [-46.7, +4.2] | -0.1457 [-0.4244, -0.0021] | no difference | **candidate worse** |
| a / twcrps | target: control window | B1 -> B2 control | -21.7% [-52.0, +1.9] | -0.1771 [-0.4110, -0.0265] | no difference | **candidate worse** |
| a / twcrps | target: control window | B1 -> B2 october | -17.7% [-45.8, +3.4] | -0.1449 [-0.4211, -0.0042] | no difference | **candidate worse** |
| a / twcrps | target: october window | B1 -> B2 as is | -11.0% [-18.0, +2.2] | -0.2721 [-0.6962, -0.0370] | no difference | **candidate worse** |
| a / twcrps | target: october window | B1 -> B2 control | -11.2% [-18.8, +1.9] | -0.2766 [-0.7308, -0.0343] | no difference | **candidate worse** |
| a / twcrps | target: tax_date as is | B1 -> B2 as is | -25.6% [-77.1, +16.7] | -1.0037 [-2.7755, -0.2458] | no difference | **candidate worse** |
| a / twcrps | target: tax_date as is | B1 -> B2 control | -15.2% [-38.1, +8.2] | -0.5938 [-1.5892, -0.1749] | no difference | **candidate worse** |
| a / twcrps | target: tax_date as is | B1 -> B2 october | -29.4% [-94.6, +14.6] | -1.1513 [-3.3050, -0.2327] | no difference | **candidate worse** |
| a / twcrps | target: tax_date as is | B2 as is -> B2 control | +8.3% [-11.7, +27.0] | +0.4099 [+0.0802, +1.4036] | no difference | **candidate better** |

Every other tested row reads the same on both intervals.

## All tested rows

Rows the scorer left undefined (scores identical, or a zero benchmark) are on the original page and carry no interval here.

### a / crps

| group | comparison | decision or target days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| pooled | B1 -> B2 as is | 1908 | -8.5% [-28.5, +21.6] | -0.1969 [-0.5338, +0.4597] | no difference |
| pooled | B1 -> B2 control | 1908 | -7.5% [-27.0, +21.9] | -0.1739 [-0.5064, +0.4782] | no difference |
| pooled | B1 -> B2 october | 1908 | -8.2% [-28.3, +21.6] | -0.1904 [-0.5277, +0.4675] | no difference |
| pooled | B2 as is -> B2 control | 1908 | +0.9% [+0.1, +2.0] | +0.0229 [+0.0024, +0.0491] | candidate better |
| pooled | B2 as is -> B2 october | 1908 | +0.3% [-0.2, +1.1] | +0.0064 [-0.0056, +0.0275] | no difference |
| regime 2018-19 | B1 -> B2 as is | 415 | +23.5% [+6.8, +56.9] | +1.2801 [+0.1470, +5.9074] | candidate better |
| regime 2018-19 | B1 -> B2 control | 415 | +24.3% [+8.5, +56.7] | +1.3260 [+0.2134, +6.0142] | candidate better |
| regime 2018-19 | B1 -> B2 october | 415 | +24.0% [+7.2, +56.6] | +1.3063 [+0.1617, +5.8393] | candidate better |
| regime 2018-19 | B2 as is -> B2 control | 415 | +1.1% [-0.4, +3.6] | +0.0459 [-0.0107, +0.1362] | no difference |
| regime 2018-19 | B2 as is -> B2 october | 415 | +0.6% [-0.3, +4.8] | +0.0261 [-0.0129, +0.1729] | no difference |
| regime 2020 | B1 -> B2 as is | 251 | -69.5% [-176.7, +5.7] | -1.1422 [-2.8499, -0.2730] | candidate worse (was no difference) |
| regime 2020 | B1 -> B2 control | 251 | -65.3% [-165.6, +12.2] | -1.0728 [-2.6086, -0.2046] | candidate worse (was no difference) |
| regime 2020 | B1 -> B2 october | 251 | -70.2% [-178.4, +4.9] | -1.1539 [-2.8878, -0.2787] | candidate worse (was no difference) |
| regime 2020 | B2 as is -> B2 control | 251 | +2.5% [-1.2, +6.5] | +0.0695 [-0.0361, +0.2134] | no difference |
| regime 2020 | B2 as is -> B2 october | 251 | -0.4% [-2.0, +0.6] | -0.0116 [-0.0595, +0.0176] | no difference |
| regime 2021-23 | B1 -> B2 as is | 748 | -108.4% [-168.7, -63.7] | -0.7703 [-1.1315, -0.4878] | candidate worse |
| regime 2021-23 | B1 -> B2 control | 748 | -107.4% [-167.3, -62.9] | -0.7634 [-1.1238, -0.4788] | candidate worse |
| regime 2021-23 | B1 -> B2 october | 748 | -108.2% [-168.4, -63.5] | -0.7690 [-1.1335, -0.4875] | candidate worse |
| regime 2021-23 | B2 as is -> B2 control | 748 | +0.5% [-0.6, +1.8] | +0.0069 [-0.0091, +0.0262] | no difference |
| regime 2021-23 | B2 as is -> B2 october | 748 | +0.1% [-0.6, +0.6] | +0.0013 [-0.0089, +0.0092] | no difference |
| regime 2024 | B1 -> B2 as is | 250 | +18.1% [+1.3, +37.7] | +0.3051 [+0.0172, +0.9449] | candidate better |
| regime 2024 | B1 -> B2 control | 250 | +18.4% [+1.1, +37.9] | +0.3091 [+0.0146, +0.9481] | candidate better |
| regime 2024 | B1 -> B2 october | 250 | +18.3% [+1.5, +37.9] | +0.3081 [+0.0193, +0.9550] | candidate better |
| regime 2024 | B2 as is -> B2 control | 250 | +0.3% [-0.9, +1.3] | +0.0040 [-0.0105, +0.0177] | no difference |
| regime 2024 | B2 as is -> B2 october | 250 | +0.2% [-0.1, +0.7] | +0.0030 [-0.0019, +0.0111] | no difference |
| regime 2025-26 | B1 -> B2 as is | 244 | -15.3% [-51.9, +9.4] | -0.4931 [-1.7796, +0.3249] | no difference |
| regime 2025-26 | B1 -> B2 control | 244 | -15.1% [-51.5, +9.4] | -0.4885 [-1.7526, +0.3259] | no difference |
| regime 2025-26 | B1 -> B2 october | 244 | -14.9% [-53.1, +10.0] | -0.4823 [-1.8187, +0.3332] | no difference |
| regime 2025-26 | B2 as is -> B2 control | 244 | +0.1% [-1.3, +1.3] | +0.0046 [-0.0443, +0.0474] | no difference |
| regime 2025-26 | B2 as is -> B2 october | 244 | +0.3% [-1.0, +3.5] | +0.0107 [-0.0336, +0.1082] | no difference |
| target: control window | B1 -> B2 as is | 371 | -34.1% [-64.4, -9.7] | -0.5065 [-0.8572, -0.2248] | candidate worse |
| target: control window | B1 -> B2 control | 371 | -39.2% [-77.2, -9.2] | -0.5821 [-1.0085, -0.2450] | candidate worse |
| target: control window | B1 -> B2 october | 371 | -34.0% [-63.9, -10.0] | -0.5049 [-0.8505, -0.2247] | candidate worse |
| target: control window | B2 as is -> B2 control | 371 | -3.8% [-17.5, +9.5] | -0.0756 [-0.3131, +0.1907] | no difference |
| target: control window | B2 as is -> B2 october | 371 | +0.1% [-0.7, +0.6] | +0.0017 [-0.0129, +0.0106] | no difference |
| target: october window | B1 -> B2 as is | 56 | -25.7% [-44.1, -3.0] | -0.8194 [-1.9260, -0.3307] | candidate worse |
| target: october window | B1 -> B2 control | 56 | -25.3% [-41.7, -4.6] | -0.8062 [-1.7980, -0.3393] | candidate worse |
| target: october window | B1 -> B2 october | 56 | -4.7% [-39.2, +39.9] | -0.1498 [-0.9309, +1.3612] | no difference |
| target: october window | B2 as is -> B2 control | 56 | +0.3% [-1.8, +2.6] | +0.0132 [-0.0273, +0.0845] | no difference |
| target: october window | B2 as is -> B2 october | 56 | +16.7% [+2.8, +36.6] | +0.6697 [-0.1871, +2.6345] | no difference (was candidate better) |
| target: other days | B1 -> B2 as is | 1908 | -5.8% [-26.6, +26.7] | -0.1192 [-0.4537, +0.5632] | no difference |
| target: other days | B1 -> B2 control | 1908 | -5.8% [-26.2, +26.4] | -0.1200 [-0.4493, +0.5589] | no difference |
| target: other days | B1 -> B2 october | 1908 | -5.6% [-26.3, +26.9] | -0.1144 [-0.4495, +0.5680] | no difference |
| target: other days | B2 as is -> B2 control | 1908 | -0.0% [-0.7, +0.6] | -0.0008 [-0.0142, +0.0120] | no difference |
| target: other days | B2 as is -> B2 october | 1908 | +0.2% [-0.3, +0.5] | +0.0048 [-0.0052, +0.0109] | no difference |
| target: tax_date as is | B1 -> B2 as is | 222 | -47.3% [-119.5, +54.0] | -2.2657 [-3.7119, -1.3712] | candidate worse (was no difference) |
| target: tax_date as is | B1 -> B2 control | 222 | -34.5% [-87.5, +37.1] | -1.6508 [-2.5504, -0.9794] | candidate worse (was no difference) |
| target: tax_date as is | B1 -> B2 october | 222 | -49.8% [-126.9, +45.9] | -2.3845 [-4.2078, -1.3382] | candidate worse (was no difference) |
| target: tax_date as is | B2 as is -> B2 control | 222 | +8.7% [-3.3, +18.7] | +0.6149 [+0.2389, +1.1786] | candidate better (was no difference) |
| target: tax_date as is | B2 as is -> B2 october | 222 | -1.7% [-4.7, +1.2] | -0.1188 [-0.3883, +0.1664] | no difference |

### a / twcrps

| group | comparison | decision or target days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| pooled | B1 -> B2 as is | 1908 | +18.6% [+1.4, +49.4] | +0.2543 [-0.0009, +1.1469] | no difference (was candidate better) |
| pooled | B1 -> B2 control | 1908 | +19.7% [+3.3, +49.0] | +0.2695 [+0.0169, +1.1602] | candidate better |
| pooled | B1 -> B2 october | 1908 | +18.9% [+1.5, +48.9] | +0.2577 [-0.0009, +1.1339] | no difference (was candidate better) |
| pooled | B2 as is -> B2 control | 1908 | +1.4% [-0.3, +3.7] | +0.0152 [-0.0023, +0.0394] | no difference |
| pooled | B2 as is -> B2 october | 1908 | +0.3% [-0.6, +2.3] | +0.0034 [-0.0070, +0.0235] | no difference |
| regime 2018-19 | B1 -> B2 as is | 415 | +28.4% [+11.2, +61.7] | +1.3454 [+0.2201, +6.6277] | candidate better |
| regime 2018-19 | B1 -> B2 control | 415 | +29.2% [+12.8, +61.5] | +1.3809 [+0.2722, +6.7412] | candidate better |
| regime 2018-19 | B1 -> B2 october | 415 | +29.0% [+11.7, +61.2] | +1.3711 [+0.2359, +6.5096] | candidate better |
| regime 2018-19 | B2 as is -> B2 control | 415 | +1.0% [-0.6, +4.2] | +0.0355 [-0.0171, +0.1291] | no difference |
| regime 2018-19 | B2 as is -> B2 october | 415 | +0.8% [-0.5, +6.4] | +0.0257 [-0.0129, +0.1802] | no difference |
| regime 2020 | B1 -> B2 as is | 251 | -62.2% [-209.4, +110.2] | -0.4605 [-0.8484, +0.1197] | no difference |
| regime 2020 | B1 -> B2 control | 251 | -54.4% [-196.5, +128.0] | -0.4027 [-0.7853, +0.2886] | no difference |
| regime 2020 | B1 -> B2 october | 251 | -64.4% [-215.7, +108.2] | -0.4770 [-0.8779, +0.0867] | no difference |
| regime 2020 | B2 as is -> B2 control | 251 | +4.8% [-3.6, +13.6] | +0.0578 [-0.0398, +0.1948] | no difference |
| regime 2020 | B2 as is -> B2 october | 251 | -1.4% [-5.5, +1.2] | -0.0164 [-0.0679, +0.0141] | no difference |
| regime 2021-23 | B1 -> B2 as is | 748 | +72.1% [+59.2, +89.2] | +0.0056 [+0.0022, +0.0242] | candidate better |
| regime 2021-23 | B1 -> B2 control | 748 | +61.0% [+33.8, +77.3] | +0.0047 [+0.0017, +0.0186] | candidate better |
| regime 2021-23 | B1 -> B2 october | 748 | +70.9% [+57.5, +89.9] | +0.0055 [+0.0021, +0.0243] | candidate better |
| regime 2021-23 | B2 as is -> B2 control | 748 | -39.9% [-88.2, -13.8] | -0.0009 [-0.0032, -0.0002] | candidate worse |
| regime 2021-23 | B2 as is -> B2 october | 748 | -4.4% [-6.7, -2.7] | -0.0001 [-0.0002, -0.0000] | candidate worse |
| regime 2024 | B1 -> B2 control | 250 | +39.0% [-0.2, +157.5] | +0.1255 [+0.0216, +14.6491] | candidate better (was no difference) |
| regime 2025-26 | B1 -> B2 as is | 244 | +1.8% [-39.0, +21.4] | +0.0282 [-0.4203, +0.3005] | no difference |
| regime 2025-26 | B1 -> B2 control | 244 | +2.0% [-38.4, +21.5] | +0.0301 [-0.4102, +0.3012] | no difference |
| regime 2025-26 | B1 -> B2 october | 244 | +1.9% [-44.8, +22.4] | +0.0284 [-0.4742, +0.3124] | no difference |
| regime 2025-26 | B2 as is -> B2 control | 244 | +0.1% [-3.6, +0.8] | +0.0019 [-0.0196, +0.0119] | no difference |
| regime 2025-26 | B2 as is -> B2 october | 244 | +0.0% [-2.2, +5.3] | +0.0002 [-0.0310, +0.0405] | no difference |
| target: control window | B1 -> B2 as is | 371 | -17.8% [-46.7, +4.2] | -0.1457 [-0.4244, -0.0021] | candidate worse (was no difference) |
| target: control window | B1 -> B2 control | 371 | -21.7% [-52.0, +1.9] | -0.1771 [-0.4110, -0.0265] | candidate worse (was no difference) |
| target: control window | B1 -> B2 october | 371 | -17.7% [-45.8, +3.4] | -0.1449 [-0.4211, -0.0042] | candidate worse (was no difference) |
| target: control window | B2 as is -> B2 control | 371 | -3.3% [-30.9, +14.6] | -0.0314 [-0.2192, +0.1635] | no difference |
| target: control window | B2 as is -> B2 october | 371 | +0.1% [-1.0, +0.9] | +0.0008 [-0.0091, +0.0072] | no difference |
| target: october window | B1 -> B2 as is | 56 | -11.0% [-18.0, +2.2] | -0.2721 [-0.6962, -0.0370] | candidate worse (was no difference) |
| target: october window | B1 -> B2 control | 56 | -11.2% [-18.8, +1.9] | -0.2766 [-0.7308, -0.0343] | candidate worse (was no difference) |
| target: october window | B2 as is -> B2 control | 56 | -0.2% [-2.5, +1.2] | -0.0046 [-0.0420, +0.0130] | no difference |
| target: other days | B1 -> B2 as is | 1908 | +28.6% [+6.4, +66.1] | +0.3191 [+0.0582, +1.2656] | candidate better |
| target: other days | B1 -> B2 control | 1908 | +28.4% [+6.2, +65.8] | +0.3164 [+0.0573, +1.2587] | candidate better |
| target: other days | B1 -> B2 october | 1908 | +29.0% [+6.7, +66.2] | +0.3231 [+0.0622, +1.2689] | candidate better |
| target: other days | B2 as is -> B2 control | 1908 | -0.3% [-1.1, +0.4] | -0.0027 [-0.0100, +0.0029] | no difference |
| target: other days | B2 as is -> B2 october | 1908 | +0.5% [-0.5, +1.2] | +0.0041 [-0.0031, +0.0086] | no difference |
| target: tax_date as is | B1 -> B2 as is | 222 | -25.6% [-77.1, +16.7] | -1.0037 [-2.7755, -0.2458] | candidate worse (was no difference) |
| target: tax_date as is | B1 -> B2 control | 222 | -15.2% [-38.1, +8.2] | -0.5938 [-1.5892, -0.1749] | candidate worse (was no difference) |
| target: tax_date as is | B1 -> B2 october | 222 | -29.4% [-94.6, +14.6] | -1.1513 [-3.3050, -0.2327] | candidate worse (was no difference) |
| target: tax_date as is | B2 as is -> B2 control | 222 | +8.3% [-11.7, +27.0] | +0.4099 [+0.0802, +1.4036] | candidate better (was no difference) |
| target: tax_date as is | B2 as is -> B2 october | 222 | -3.0% [-8.8, +1.7] | -0.1476 [-0.4411, +0.0457] | no difference |

### The ranker tables (b)

The precision and recall gains of the original page's part (b) are differences of means with their own studentized interval, and were already read on that interval. They are not re-read here.

Nothing here is a verdict for a hypothesis. The originals stand.
