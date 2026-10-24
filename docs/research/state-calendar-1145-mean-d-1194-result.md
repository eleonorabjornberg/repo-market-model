# State-scaled calendar effects, read on the mean-d bound (#1194; H5 reporting, for #1009)

**Development data, not a verdict.** No re-scoring, no lockbox day, and no published declaration, record or decided value moves; **no claim changes**. Every figure is read from `docs/research/state-calendar-1145/result.json`, the record of the first page (`state-calendar-1145-result.md`, which stands), by `scripts/mean_d_reading_1194.py report`. Seed 1145, 10,000 draws, as on the first page.

## What changes and why

The first page read each row from the studentized skill interval. Her ruling on #1009 (20 October 2026) is that a development page shows both intervals and reads the studentized bound on mean d, as the protocol's verdict does (ruling 1/5). #1145 was declared two days after that ruling and read the skill interval (finding #1187). This page shows both for every paired row and reads the mean-d bound: **gain** when the lower bound of mean d is above zero, **loss** when its upper bound is below zero, **undecided** otherwise. The 90% two-sided interval on mean d is the pair of one-sided 95% bounds. d = S(reference) - S(arm), positive favouring the arm; skill is mean(d) / mean(S(reference)). A row the scorer left undefined carries no interval and is not read here.

**Caveat (Lens C of the five-lens review, #958).** The lag-10 HAC standard error that studentizes the mean-d bound is understated about 2× after 2020 (about 2.3× in 2021–23, 1.7× in 2024–26), and the bootstrap block of 10 days is an order of magnitude shorter than the autocorrelation of d. The bound is therefore optimistic: an interval that excludes zero here is narrower than it should be after 2020. A reading on this page is evidence for a question, not a verdict.

Paired rows read: 1260. Rows whose reading changes: 170.

| reading on the skill interval -> reading on the mean-d bound | rows |
|---|---|
| gain -> undecided | 19 |
| loss -> undecided | 5 |
| undecided -> gain | 99 |
| undecided -> loss | 47 |

## The candidate (s3) against (a)

(s3), the scaled mean reversion with the calendar terms in standardised units, a Huber fit and a heavier ridge, is the H5 candidate by her ruling on #1151 (23 October 2026). It is read here against (a), the model it replaced, pooled, by regime and by target-day type, on both scores. Grid CRPS is the primary score; upper-tail twCRPS is the key secondary.

| split | group | days | measure | skill [90%] | mean d [90%] | on the skill interval | on the mean-d bound |
|---|---|---|---|---|---|---|---|
| pooled | all decision days | 1855 | grid CRPS | +4.3% [+1.8, +6.4] | +0.07369 [+0.03455, +0.1078] | gain | gain |
| pooled | all decision days | 1855 | upper-tail twCRPS | +4.4% [+1.0, +7.6] | +0.03913 [+0.01369, +0.06945] | gain | gain |
| regime | 2018-19 | 361 | grid CRPS | +3.0% [-0.0, +5.9] | +0.1142 [+0.0138, +0.2216] | undecided | **gain** |
| regime | 2018-19 | 361 | upper-tail twCRPS | +4.3% [-0.0, +7.8] | +0.1454 [+0.05925, +0.2448] | undecided | **gain** |
| regime | 2020 | 251 | grid CRPS | -2.6% [-29.7, +4.4] | -0.03695 [-0.4042, +0.06133] | undecided | undecided |
| regime | 2020 | 251 | upper-tail twCRPS | -9.1% [-51.7, +1.1] | -0.04644 [-0.2381, -0.001595] | undecided | **loss** |
| regime | 2021-23 | 748 | grid CRPS | +3.9% [+1.7, +6.1] | +0.02539 [+0.009048, +0.04575] | gain | gain |
| regime | 2021-23 | 748 | upper-tail twCRPS | +16.0% [+6.8, +33.5] | +0.001255 [+8.16e-05, +0.01142] | gain | gain |
| regime | 2024 | 250 | grid CRPS | +7.6% [+5.1, +10.0] | +0.09173 [+0.04682, +0.1567] | gain | gain |
| regime | 2024 | 250 | upper-tail twCRPS | +5.2% [-17.1, +15.7] | +0.00946 [+0.002453, +0.06367] | undecided | **gain** |
| regime | 2025-26 | 249 | grid CRPS | +11.0% [+4.7, +16.9] | +0.2827 [+0.1411, +0.4426] | gain | gain |
| regime | 2025-26 | 249 | upper-tail twCRPS | +13.2% [+1.6, +24.2] | +0.1427 [+0.03759, +0.3526] | gain | gain |
| target_day_type | calendar_days | 1352 | grid CRPS | +4.9% [+1.6, +7.6] | +0.09305 [+0.03685, +0.1446] | gain | gain |
| target_day_type | calendar_days | 1352 | upper-tail twCRPS | +4.3% [+0.5, +8.1] | +0.04638 [+0.008818, +0.09127] | gain | gain |
| target_day_type | dom_19_23 | 305 | grid CRPS | +14.0% [+6.2, +21.8] | +0.1878 [+0.0782, +0.3292] | gain | gain |
| target_day_type | dom_19_23 | 305 | upper-tail twCRPS | +21.4% [+10.2, +30.5] | +0.112 [+0.04678, +0.2611] | gain | gain |
| target_day_type | fomc_day | 118 | grid CRPS | -1.5% [-5.9, +0.7] | -0.06631 [-0.3161, +0.04199] | undecided | undecided |
| target_day_type | fomc_day | 118 | upper-tail twCRPS | -1.7% [-5.1, +1.7] | -0.0599 [-0.2308, -0.008443] | undecided | **loss** |
| target_day_type | iorb_window | 78 | grid CRPS | +7.6% [-9.3, +26.4] | +0.1822 [-0.06444, +0.7208] | undecided | undecided |
| target_day_type | month_end | 180 | grid CRPS | +12.0% [-1.7, +22.0] | +0.319 [-0.09236, +0.7656] | undecided | undecided |
| target_day_type | month_end | 180 | upper-tail twCRPS | +12.5% [-0.7, +23.4] | +0.2052 [-0.07038, +0.6673] | undecided | undecided |
| target_day_type | ordinary | 507 | grid CRPS | +3.2% [+2.4, +4.0] | +0.03643 [+0.02321, +0.05369] | gain | gain |
| target_day_type | ordinary | 507 | upper-tail twCRPS | +7.5% [+5.6, +9.4] | +0.03347 [+0.0198, +0.05499] | gain | gain |
| target_day_type | post_month_end_window | 267 | grid CRPS | +0.3% [-9.9, +6.9] | +0.006241 [-0.1707, +0.1423] | undecided | undecided |
| target_day_type | post_month_end_window | 267 | upper-tail twCRPS | -6.1% [-28.8, +8.5] | -0.06525 [-0.2343, +0.04435] | undecided | undecided |
| target_day_type | quarter_end | 30 | grid CRPS | +18.4% [-8.5, +34.7] | +1.154 [-0.3386, +3.605] | undecided | undecided |
| target_day_type | quarter_end | 30 | upper-tail twCRPS | +19.4% [+1.2, +31.2] | +0.9301 [-0.02054, +3.766] | gain | **undecided** |
| target_day_type | settlement | 946 | grid CRPS | +5.8% [+1.2, +9.2] | +0.1213 [+0.04889, +0.1893] | gain | gain |
| target_day_type | settlement | 946 | upper-tail twCRPS | +5.1% [-0.1, +9.9] | +0.06485 [+0.01872, +0.1277] | undecided | **gain** |
| target_day_type | tax_date | 89 | grid CRPS | -0.8% [-3.5, +1.3] | -0.03843 [-0.1611, +0.0365] | undecided | undecided |
| target_day_type | tax_date | 89 | upper-tail twCRPS | -0.4% [-2.4, +0.9] | -0.01822 [-0.1014, +0.02052] | undecided | undecided |

**Regime line on the mean-d bound** (decision-day regimes of the target day, (s3) against (a)):

- grid CRPS: 2018-19: gain; 2020: undecided; 2021-23: gain; 2024: gain; 2025-26: gain.
- upper-tail twCRPS: 2018-19: gain; 2020: loss; 2021-23: gain; 2024: gain; 2025-26: gain.

**Open question, recorded by her ruling on #1187 (24 October 2026).** (s3) stays the candidate. Read on the mean-d bound, it is worse than (a) on upper-tail twCRPS in 2020 (mean d -0.046 bp, interval [-0.238, -0.002]), on fomc_day (mean d -0.060 bp, interval [-0.231, -0.008]). Whether those two upper-tail losses matter for the H5 registration is to be settled before any registration; it is her decision, and the 2020 loss comes with Lens C's caveat above (the 2020 interval is about 2× too narrow), so it is evidence for a question, not a verdict. This page settles nothing.

## Readings that change

| section | group | comparison | skill [90%] | mean d [90%] | on the skill interval | on the mean-d bound |
|---|---|---|---|---|---|---|
| grid_crps, by lead | h=1 | (s2) against B1' | +8.4% [-1.2, +16.9] | +0.1446 [+0.006841, +0.3103] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | (a) against B1' | +14.4% [-3.5, +26.9] | +0.1481 [+0.04729, +0.3099] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | (a) against B2 | +21.0% [-2.5, +36.7] | +0.2341 [+0.095, +0.3959] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | (s1) against B1' | +13.2% [-4.4, +26.9] | +0.1355 [+0.01507, +0.304] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | (s1) against B2 | +19.9% [-2.8, +34.8] | +0.2216 [+0.07629, +0.3851] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | (s2) against B1' | +13.4% [-4.2, +27.1] | +0.1375 [+0.01967, +0.302] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | (s2) against B2 | +20.1% [-3.5, +34.5] | +0.2236 [+0.07893, +0.381] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | (s3) against B1' | +20.6% [-2.5, +33.1] | +0.2112 [+0.1008, +0.3883] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | (s3) against B2 | +26.7% [-1.4, +42.4] | +0.2973 [+0.155, +0.468] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | (s4) against B2 | +17.8% [-1.7, +32.1] | +0.1981 [+0.05597, +0.3601] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=1 | (s4) against (s1) | -2.6% [-6.8, +0.3] | -0.02351 [-0.05182, -0.00591] | undecided | **loss** |
| upper_tail_twcrps, by lead | h=2 | (s1) against B1' | +12.3% [-1.4, +25.3] | +0.1266 [+0.01413, +0.295] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=2 | (s2) against B1' | +12.6% [-1.8, +25.6] | +0.1303 [+0.01309, +0.2972] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=2 | (s3) against spread_mr_ctx | +4.6% [-0.4, +9.5] | +0.04164 [+0.004348, +0.09092] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=2 | (s4) against B1' | +10.9% [-1.6, +23.5] | +0.1127 [+0.001658, +0.2793] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=3 | (s4) against (s1) | -2.1% [-5.8, +0.1] | -0.01918 [-0.046, -0.003959] | undecided | **loss** |
| upper_tail_twcrps, by lead | h=4 | (s3) against spread_mr_ctx | +5.0% [-0.5, +10.5] | +0.04548 [+0.003392, +0.1013] | undecided | **gain** |
| upper_tail_twcrps, by lead | h=5 | (s3) against spread_mr_ctx | +5.6% [-0.2, +11.3] | +0.05206 [+0.00525, +0.1124] | undecided | **gain** |
| upper_tail_twcrps, by all decision days | all decision days | (s4) against (s1) | -2.6% [-6.5, +0.0] | -0.02338 [-0.05405, -0.005957] | undecided | **loss** |
| grid_crps, by regime | 2018-19 | (s3) against (a) | +3.0% [-0.0, +5.9] | +0.1142 [+0.0138, +0.2216] | undecided | **gain** |
| grid_crps, by regime | 2018-19 | (s4) against (s1) | -2.9% [-9.2, +0.4] | -0.1137 [-0.3301, -0.0179] | undecided | **loss** |
| grid_crps, by regime | 2018-19 | (s4) against spread_mr_ctx | -10.5% [-27.7, +1.9] | -0.3889 [-0.8386, -0.02118] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2018-19 | (a) against B1' | +11.5% [-0.5, +30.8] | +0.4411 [+0.08072, +1.374] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2018-19 | (a) against B2 | +11.0% [-1.2, +23.7] | +0.419 [+0.05043, +0.875] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2018-19 | (s3) against B1' | +15.3% [-0.4, +34.4] | +0.5865 [+0.1718, +1.547] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2018-19 | (s3) against B2 | +14.8% [-1.5, +29.0] | +0.5644 [+0.1498, +1.052] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2018-19 | (s3) against (a) | +4.3% [-0.0, +7.8] | +0.1454 [+0.05925, +0.2448] | undecided | **gain** |
| grid_crps, by regime | 2020 | (s4) against (s1) | -4.1% [-10.8, +0.7] | -0.0687 [-0.1443, -0.01415] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2020 | (a) against B2 | +58.1% [-22.6, +84.8] | +0.7083 [+0.361, +1.127] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | (a) against spread_mr_ctx | +22.9% [-17.4, +50.8] | +0.1521 [+0.08842, +0.2214] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | (s1) against B2 | +37.6% [-17.4, +68.2] | +0.4586 [+0.08857, +0.836] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | (s1) against (a) | -48.9% [-180.0, +5.1] | -0.2497 [-0.8954, -0.09727] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2020 | (s2) against B2 | +45.7% [-35.3, +77.3] | +0.5571 [+0.2101, +0.9225] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | (s2) against (a) | -29.6% [-231.6, +0.2] | -0.1512 [-1.084, -0.006518] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2020 | (s2) against (s1) | +13.0% [-4.8, +37.0] | +0.0985 [+0.04949, +0.2211] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | (s3) against B1' | +25.9% [+11.0, +53.8] | +0.1947 [-0.001213, +1.695] | gain | **undecided** |
| upper_tail_twcrps, by regime | 2020 | (s3) against B2 | +54.3% [-10.6, +82.0] | +0.6618 [+0.3365, +1.058] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | (s3) against (a) | -9.1% [-51.7, +1.1] | -0.04644 [-0.2381, -0.001595] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2020 | (s3) against (s1) | +26.7% [-7.5, +56.0] | +0.2033 [+0.0904, +0.6362] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | (s4) against B2 | +33.0% [-9.2, +62.3] | +0.4021 [+0.01088, +0.7869] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2020 | (s4) against (a) | -59.9% [-173.2, +15.4] | -0.3062 [-0.8324, -0.1513] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2020 | (s4) against (s1) | -7.4% [-24.1, +3.5] | -0.05646 [-0.1306, -0.009179] | undecided | **loss** |
| grid_crps, by regime | 2021-23 | (s2) against B1' | +5.4% [-0.2, +10.6] | +0.03603 [+0.000587, +0.07351] | undecided | **gain** |
| grid_crps, by regime | 2021-23 | (s2) against (a) | +4.4% [+0.3, +8.9] | +0.02931 [-0.0007745, +0.06836] | gain | **undecided** |
| upper_tail_twcrps, by regime | 2021-23 | (a) against B2 | -156.2% [-814.7, -37.2] | -0.004779 [-0.05043, +0.000294] | loss | **undecided** |
| upper_tail_twcrps, by regime | 2021-23 | (a) against spread_mr_ctx | +54.4% [-44.3, +86.0] | +0.009339 [+0.004353, +0.01617] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | (s1) against B2 | -112.5% [-498.6, -28.6] | -0.003441 [-0.03227, +0.0003153] | loss | **undecided** |
| upper_tail_twcrps, by regime | 2021-23 | (s1) against spread_mr_ctx | +62.2% [-10.4, +88.5] | +0.01068 [+0.005612, +0.01803] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | (s2) against B1 | +42.0% [-0.5, +64.9] | +0.003758 [+0.001763, +0.008238] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | (s2) against B1' | +23.0% [-5.1, +39.8] | +0.001547 [+0.0005092, +0.003578] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | (s2) against B2 | -69.3% [-364.3, -7.7] | -0.002121 [-0.02415, +0.0005179] | loss | **undecided** |
| upper_tail_twcrps, by regime | 2021-23 | (s3) against B1 | +26.3% [-27.7, +52.5] | +0.002355 [+0.0001014, +0.004681] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | (s3) against B2 | -115.2% [-539.5, -26.8] | -0.003524 [-0.03477, +0.0003426] | loss | **undecided** |
| upper_tail_twcrps, by regime | 2021-23 | (s3) against spread_mr_ctx | +61.7% [-13.7, +88.0] | +0.01059 [+0.005564, +0.0181] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2021-23 | (s4) against B2 | -248.6% [-2911.8, -31.7] | -0.007608 [-0.1762, +0.0002376] | loss | **undecided** |
| upper_tail_twcrps, by regime | 2024 | (s1) against (a) | +7.2% [-14.7, +18.0] | +0.01328 [+0.003012, +0.09028] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2024 | (s1) against spread_mr_ctx | +16.4% [+5.6, +44.3] | +0.0334 [-0.001691, +0.911] | gain | **undecided** |
| upper_tail_twcrps, by regime | 2024 | (s2) against (a) | +7.2% [-14.7, +18.0] | +0.01329 [+0.00301, +0.0903] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2024 | (s2) against spread_mr_ctx | +16.4% [+5.6, +44.3] | +0.0334 [-0.001692, +0.9114] | gain | **undecided** |
| upper_tail_twcrps, by regime | 2024 | (s3) against (a) | +5.2% [-17.1, +15.7] | +0.00946 [+0.002453, +0.06367] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2024 | (s3) against (s1) | -2.2% [-4.8, +1.4] | -0.003824 [-0.02822, -3.552e-05] | undecided | **loss** |
| upper_tail_twcrps, by regime | 2024 | (s3) against spread_mr_ctx | +14.5% [+1.9, +38.6] | +0.02957 [-0.002607, +0.8908] | gain | **undecided** |
| upper_tail_twcrps, by regime | 2024 | (s4) against (a) | +7.1% [-15.1, +17.7] | +0.0131 [+0.002863, +0.08668] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2024 | (s4) against spread_mr_ctx | +16.3% [+5.5, +43.8] | +0.03321 [-0.0018, +0.8732] | gain | **undecided** |
| upper_tail_twcrps, by regime | 2025-26 | (s1) against (a) | +10.6% [-1.0, +22.0] | +0.1153 [+0.00922, +0.2981] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2025-26 | (s1) against spread_mr_ctx | +11.5% [+2.1, +21.0] | +0.1259 [-0.01331, +0.3778] | gain | **undecided** |
| upper_tail_twcrps, by regime | 2025-26 | (s4) against (a) | +10.5% [-2.5, +22.7] | +0.1142 [+0.002976, +0.3027] | undecided | **gain** |
| upper_tail_twcrps, by regime | 2025-26 | (s4) against spread_mr_ctx | +11.4% [+2.0, +21.1] | +0.1248 [-0.01191, +0.3734] | gain | **undecided** |
| scaled_grid_crps, by scaled | 2018-19 | (a) against spread_mr_ctx | -5.9% [-14.7, +4.2] | -0.1295 [-0.2301, -0.04611] | undecided | **loss** |
| scaled_grid_crps, by scaled | 2018-19 | (s1) against B1 | +43.6% [+20.2, +147.0] | +1.926 [-0.07263, +30.56] | gain | **undecided** |
| scaled_grid_crps, by scaled | 2018-19 | (s1) against spread_mr_ctx | -14.2% [-39.5, +3.5] | -0.3101 [-0.7632, -0.0669] | undecided | **loss** |
| scaled_grid_crps, by scaled | 2018-19 | (s2) against B1 | +43.4% [+20.1, +147.7] | +1.92 [-0.07873, +30.32] | gain | **undecided** |
| scaled_grid_crps, by scaled | 2018-19 | (s2) against spread_mr_ctx | -14.5% [-40.1, +3.9] | -0.316 [-0.7815, -0.07402] | undecided | **loss** |
| scaled_grid_crps, by scaled | 2018-19 | (s3) against (s1) | +6.8% [-0.2, +12.3] | +0.1704 [+0.09107, +0.3117] | undecided | **gain** |
| scaled_grid_crps, by scaled | 2018-19 | (s4) against B1 | +41.4% [+13.6, +139.2] | +1.829 [-0.2081, +24.12] | gain | **undecided** |
| scaled_grid_crps, by scaled | 2018-19 | (s4) against (a) | -12.0% [-36.7, +4.4] | -0.2774 [-0.7308, -0.01682] | undecided | **loss** |
| scaled_grid_crps, by scaled | 2018-19 | (s4) against spread_mr_ctx | -18.6% [-54.5, +8.5] | -0.4069 [-0.9639, -0.08582] | undecided | **loss** |
| scaled_grid_crps, by scaled | 2020 | (a) against B1' | +12.0% [+1.1, +33.1] | +0.08959 [-0.0008499, +0.4139] | gain | **undecided** |
| scaled_grid_crps, by scaled | 2020 | (s2) against B1 | +13.3% [-1.3, +25.9] | +0.1027 [+0.006887, +0.2833] | undecided | **gain** |
| scaled_grid_crps, by scaled | 2020 | (s2) against (s1) | +2.0% [-0.1, +6.1] | +0.01335 [+0.001289, +0.03746] | undecided | **gain** |
| scaled_grid_crps, by scaled | 2020 | (s4) against (a) | -9.1% [-22.4, +1.3] | -0.06019 [-0.135, -0.005491] | undecided | **loss** |
| scaled_grid_crps, by scaled | 2021-23 | (s3) against B1' | +5.4% [-0.2, +10.6] | +0.04417 [+0.0009768, +0.09719] | undecided | **gain** |
| scaled_grid_crps, by scaled | 2024 | (a) against B2 | +14.7% [+0.0, +30.4] | +0.445 [-0.007935, +1.118] | gain | **undecided** |
| scaled_grid_crps, by scaled | 2024 | (s3) against (a) | +4.9% [-0.2, +8.5] | +0.127 [+0.01826, +0.232] | undecided | **gain** |
| scaled_grid_crps, by scaled | 2025-26 | (a) against B1' | +10.1% [-0.4, +17.8] | +0.2316 [+0.008497, +0.4319] | undecided | **gain** |
| scaled_grid_crps, by scaled | all decision days | (a) against spread_mr_ctx | +2.5% [-0.0, +5.3] | +0.035 [+0.000913, +0.08038] | undecided | **gain** |
| grid_crps, by target-day type | calendar_days | (s1) against B1' | +7.9% [-0.5, +14.8] | +0.1668 [+0.001242, +0.3373] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | calendar_days | (s1) against B1' | +10.6% [-1.1, +21.0] | +0.1311 [+0.002824, +0.304] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | calendar_days | (s4) against (s1) | -2.8% [-7.5, +0.3] | -0.03062 [-0.07335, -0.007107] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | dom_19_23 | (s1) against B1' | +31.0% [-14.6, +63.0] | +0.1781 [+0.02081, +0.508] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | dom_19_23 | (s2) against B1' | +27.5% [-15.7, +61.9] | +0.158 [+0.005245, +0.4923] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | dom_19_23 | (s2) against spread_mr_ctx | +14.4% [-1.2, +30.8] | +0.06996 [+0.007482, +0.2137] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | dom_19_23 | (s3) against B1' | +28.5% [-14.9, +60.1] | +0.164 [+0.01109, +0.4822] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | dom_19_23 | (s4) against B1' | +30.7% [-9.5, +64.8] | +0.1762 [+0.02654, +0.5316] | undecided | **gain** |
| grid_crps, by target-day type | fomc_day | (a) against B1 | +4.0% [-1.3, +9.8] | +0.1822 [+0.03153, +0.3955] | undecided | **gain** |
| grid_crps, by target-day type | fomc_day | (a) against B1' | +2.9% [+0.9, +4.9] | +0.1323 [-0.00972, +0.4011] | gain | **undecided** |
| grid_crps, by target-day type | fomc_day | (a) against B2 | +20.0% [-14.9, +40.9] | +1.098 [+0.4607, +1.865] | undecided | **gain** |
| grid_crps, by target-day type | fomc_day | (s1) against B2 | +13.4% [-7.6, +29.3] | +0.734 [+0.1877, +1.346] | undecided | **gain** |
| grid_crps, by target-day type | fomc_day | (s1) against (a) | -8.3% [-32.2, +3.4] | -0.3638 [-1.159, -0.03975] | undecided | **loss** |
| grid_crps, by target-day type | fomc_day | (s2) against B2 | +13.9% [-12.7, +31.8] | +0.7648 [+0.02703, +1.459] | undecided | **gain** |
| grid_crps, by target-day type | fomc_day | (s3) against B2 | +18.8% [-13.4, +39.5] | +1.031 [+0.4786, +1.737] | undecided | **gain** |
| grid_crps, by target-day type | fomc_day | (s3) against (s1) | +6.2% [-3.1, +26.7] | +0.2975 [+0.08091, +0.9771] | undecided | **gain** |
| grid_crps, by target-day type | fomc_day | (s4) against B1 | -20.8% [-54.5, +7.3] | -0.9514 [-2.318, -0.05602] | undecided | **loss** |
| grid_crps, by target-day type | fomc_day | (s4) against B1' | -22.1% [-58.6, +11.3] | -1.001 [-2.3, -0.1778] | undecided | **loss** |
| grid_crps, by target-day type | fomc_day | (s4) against (a) | -25.8% [-63.8, +11.2] | -1.134 [-2.532, -0.2169] | undecided | **loss** |
| grid_crps, by target-day type | fomc_day | (s4) against (s1) | -16.2% [-38.0, +2.8] | -0.7698 [-2.019, -0.169] | undecided | **loss** |
| grid_crps, by target-day type | fomc_day | (s4) against spread_mr_ctx | -23.7% [-56.5, +8.7] | -1.059 [-2.47, -0.1282] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | fomc_day | (a) against B1 | +2.3% [-0.3, +4.4] | +0.0818 [+0.01057, +0.3473] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | fomc_day | (a) against B2 | +11.5% [-14.1, +24.7] | +0.4614 [+0.07462, +1.291] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | fomc_day | (s1) against B1 | -5.9% [-23.7, +6.4] | -0.2129 [-0.5819, -0.03087] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | fomc_day | (s1) against B1' | -5.3% [-25.4, +8.1] | -0.1926 [-0.5789, -0.003396] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | fomc_day | (s1) against (a) | -8.3% [-36.5, +7.5] | -0.2947 [-0.846, -0.06908] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | fomc_day | (s1) against spread_mr_ctx | -7.2% [-28.6, +4.8] | -0.2573 [-0.902, -0.02427] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | fomc_day | (s2) against (a) | -8.2% [-60.1, +7.4] | -0.2914 [-2.032, -0.03042] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | fomc_day | (s3) against B2 | +10.0% [-6.3, +20.6] | +0.4015 [+0.07109, +1.142] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | fomc_day | (s3) against (a) | -1.7% [-5.1, +1.7] | -0.0599 [-0.2308, -0.008443] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | fomc_day | (s3) against (s1) | +6.1% [-10.5, +34.7] | +0.2348 [+0.06115, +0.7831] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | fomc_day | (s4) against B1 | -19.5% [-54.6, +8.6] | -0.7085 [-2.001, -0.1445] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | fomc_day | (s4) against B1' | -18.9% [-54.4, +10.9] | -0.6882 [-1.795, -0.1527] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | fomc_day | (s4) against (a) | -22.3% [-60.9, +13.1] | -0.7903 [-2.13, -0.1589] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | fomc_day | (s4) against (s1) | -12.9% [-36.8, +4.5] | -0.4956 [-2.345, -0.05419] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | fomc_day | (s4) against spread_mr_ctx | -21.0% [-52.9, +11.7] | -0.7529 [-2.062, -0.1232] | undecided | **loss** |
| grid_crps, by target-day type | iorb_window | (a) against B1 | +52.7% [+16.6, +219.7] | +2.688 [-0.08449, +67.75] | gain | **undecided** |
| grid_crps, by target-day type | iorb_window | (a) against B2 | +33.8% [-19.7, +55.6] | +1.23 [+0.1603, +2.871] | undecided | **gain** |
| grid_crps, by target-day type | iorb_window | (s1) against B2 | +36.2% [-31.3, +68.6] | +1.317 [+0.02845, +3.647] | undecided | **gain** |
| grid_crps, by target-day type | iorb_window | (s2) against B2 | +35.8% [-32.9, +65.2] | +1.304 [+0.03107, +3.416] | undecided | **gain** |
| grid_crps, by target-day type | iorb_window | (s3) against B2 | +38.8% [-23.0, +66.3] | +1.413 [+0.1981, +3.626] | undecided | **gain** |
| grid_crps, by target-day type | iorb_window | (s4) against B2 | +36.8% [-19.7, +68.1] | +1.339 [+0.1357, +3.714] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | month_end | (a) against B2 | +24.9% [-10.9, +57.6] | +0.5462 [+0.05145, +1.878] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | month_end | (s3) against B2 | +34.3% [-1.8, +66.0] | +0.7514 [+0.1961, +2.628] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | month_end | (s3) against spread_mr_ctx | +20.5% [-0.4, +35.8] | +0.3721 [+0.1283, +0.8113] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | post_month_end_window | (s1) against (a) | -24.4% [-62.2, +5.8] | -0.26 [-0.696, -0.05783] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | post_month_end_window | (s2) against (a) | -26.8% [-70.5, +5.7] | -0.2859 [-0.8201, -0.06278] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | post_month_end_window | (s4) against (a) | -25.0% [-60.0, +5.3] | -0.2663 [-0.6436, -0.07258] | undecided | **loss** |
| grid_crps, by target-day type | quarter_end | (s3) against B1 | +26.4% [+0.2, +41.2] | +1.839 [-0.05085, +5.46] | gain | **undecided** |
| grid_crps, by target-day type | quarter_end | (s4) against (s1) | +0.5% [+0.1, +0.9] | +0.02753 [-0.001569, +0.1047] | gain | **undecided** |
| upper_tail_twcrps, by target-day type | quarter_end | (a) against spread_mr_ctx | +4.3% [-6.6, +9.5] | +0.2161 [+0.05458, +0.3827] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | quarter_end | (s3) against (a) | +19.4% [+1.2, +31.2] | +0.9301 [-0.02054, +3.766] | gain | **undecided** |
| upper_tail_twcrps, by target-day type | quarter_end | (s3) against spread_mr_ctx | +22.9% [-4.7, +37.4] | +1.146 [+0.1349, +4.306] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | settlement | (s1) against B1' | +12.7% [-1.4, +26.0] | +0.1843 [+0.02916, +0.4499] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | settlement | (s2) against B1' | +12.4% [-1.8, +25.6] | +0.1786 [+0.02895, +0.4296] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | settlement | (s2) against B2 | +21.7% [-0.1, +36.8] | +0.351 [+0.1596, +0.6299] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | settlement | (s3) against (a) | +5.1% [-0.1, +9.9] | +0.06485 [+0.01872, +0.1277] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | settlement | (s3) against (s1) | +5.3% [-0.1, +13.1] | +0.06678 [+0.01319, +0.1539] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | settlement | (s3) against spread_mr_ctx | +8.4% [-1.4, +16.7] | +0.1095 [+0.04211, +0.2265] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | settlement | (s4) against B1' | +11.0% [-1.5, +23.8] | +0.1595 [+0.003697, +0.4184] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | settlement | (s4) against (s1) | -2.0% [-5.8, +0.3] | -0.02482 [-0.06608, -0.00457] | undecided | **loss** |
| grid_crps, by target-day type | tax_date | (a) against B1 | +6.8% [-5.8, +13.6] | +0.3754 [+0.04441, +1.088] | undecided | **gain** |
| grid_crps, by target-day type | tax_date | (a) against B2 | +33.8% [-60.1, +59.1] | +2.617 [+1.368, +4.855] | undecided | **gain** |
| grid_crps, by target-day type | tax_date | (a) against spread_mr_ctx | +4.6% [-5.2, +15.1] | +0.2475 [+0.06285, +0.5576] | undecided | **gain** |
| grid_crps, by target-day type | tax_date | (s1) against B2 | +26.6% [-43.3, +44.5] | +2.061 [+1.104, +3.718] | undecided | **gain** |
| grid_crps, by target-day type | tax_date | (s1) against (a) | -10.9% [-43.1, +5.1] | -0.5558 [-1.637, -0.095] | undecided | **loss** |
| grid_crps, by target-day type | tax_date | (s1) against spread_mr_ctx | -5.7% [-19.1, +2.3] | -0.3083 [-0.802, -0.01938] | undecided | **loss** |
| grid_crps, by target-day type | tax_date | (s2) against B2 | +30.6% [-56.7, +54.8] | +2.371 [+1.247, +4.062] | undecided | **gain** |
| grid_crps, by target-day type | tax_date | (s3) against B1' | +4.8% [+2.2, +7.1] | +0.2606 [-0.04544, +0.9945] | gain | **undecided** |
| grid_crps, by target-day type | tax_date | (s3) against B2 | +33.3% [-52.0, +58.3] | +2.579 [+1.351, +4.949] | undecided | **gain** |
| grid_crps, by target-day type | tax_date | (s3) against (s1) | +9.1% [-7.9, +35.7] | +0.5174 [+0.04628, +1.945] | undecided | **gain** |
| grid_crps, by target-day type | tax_date | (s3) against spread_mr_ctx | +3.9% [-3.7, +13.8] | +0.2091 [+0.003758, +0.5733] | undecided | **gain** |
| grid_crps, by target-day type | tax_date | (s4) against B2 | +25.2% [-17.6, +42.1] | +1.953 [+1.056, +3.76] | undecided | **gain** |
| grid_crps, by target-day type | tax_date | (s4) against (a) | -13.0% [-45.8, +9.1] | -0.664 [-1.676, -0.1864] | undecided | **loss** |
| grid_crps, by target-day type | tax_date | (s4) against spread_mr_ctx | -7.8% [-27.7, +5.6] | -0.4165 [-1.229, -0.09337] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | tax_date | (a) against B1 | +6.1% [-12.2, +15.3] | +0.286 [+0.01513, +1.965] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | tax_date | (a) against B1' | +5.9% [-2.7, +12.3] | +0.2765 [+0.0107, +2.534] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | tax_date | (a) against spread_mr_ctx | +4.1% [-6.3, +16.3] | +0.1885 [+0.005494, +0.6318] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | tax_date | (s2) against (a) | -4.5% [-17.4, +0.3] | -0.1965 [-1.324, -0.007305] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | tax_date | (s3) against B1 | +5.7% [-6.8, +12.4] | +0.2678 [+0.008825, +1.745] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | tax_date | (s3) against B1' | +5.6% [-1.6, +9.4] | +0.2583 [+0.007184, +2.022] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | tax_date | (s3) against spread_mr_ctx | +3.7% [-5.0, +14.5] | +0.1702 [+0.009531, +0.6147] | undecided | **gain** |
| upper_tail_twcrps, by target-day type | tax_date | (s4) against (a) | -8.9% [-55.5, +5.3] | -0.3915 [-1.579, -0.01775] | undecided | **loss** |
| upper_tail_twcrps, by target-day type | tax_date | (s4) against spread_mr_ctx | -4.4% [-28.9, +4.8] | -0.2031 [-0.9658, -0.001946] | undecided | **loss** |

Every other paired row reads the same on both intervals.

## All paired rows

### grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=1 | (a) against B1 | 1855 | +22.8% [+17.2, +34.0] | +0.4601 [+0.25, +1.185] | gain |
| h=1 | (a) against B1' | 1855 | +9.8% [+2.0, +16.9] | +0.1687 [+0.06321, +0.3184] | gain |
| h=1 | (a) against B2 | 1855 | +37.2% [+21.0, +47.0] | +0.923 [+0.6681, +1.232] | gain |
| h=1 | (a) against spread_mr_ctx | 1855 | +1.7% [-0.9, +4.3] | +0.02722 [-0.01405, +0.06805] | undecided |
| h=1 | (s1) against B1 | 1855 | +20.8% [+12.8, +31.3] | +0.4205 [+0.192, +1.004] | gain |
| h=1 | (s1) against B1' | 1855 | +7.5% [-2.1, +16.2] | +0.1291 [-0.01115, +0.2979] | undecided |
| h=1 | (s1) against B2 | 1855 | +35.6% [+20.2, +45.3] | +0.8834 [+0.6284, +1.177] | gain |
| h=1 | (s1) against (a) | 1855 | -2.5% [-8.8, +1.3] | -0.03956 [-0.1313, +0.02174] | undecided |
| h=1 | (s1) against spread_mr_ctx | 1855 | -0.8% [-6.9, +3.3] | -0.01234 [-0.1041, +0.05458] | undecided |
| h=1 | (s2) against B1 | 1855 | +21.6% [+14.1, +31.4] | +0.436 [+0.2124, +1.021] | gain |
| h=1 | (s2) against B1' | 1855 | +8.4% [-1.2, +16.9] | +0.1446 [+0.006841, +0.3103] | gain (was undecided) |
| h=1 | (s2) against B2 | 1855 | +36.2% [+20.3, +45.9] | +0.8988 [+0.6429, +1.192] | gain |
| h=1 | (s2) against (a) | 1855 | -1.5% [-8.0, +2.3] | -0.02411 [-0.1203, +0.03681] | undecided |
| h=1 | (s2) against (s1) | 1855 | +1.0% [-0.8, +2.9] | +0.01545 [-0.01242, +0.04558] | undecided |
| h=1 | (s2) against spread_mr_ctx | 1855 | +0.2% [-6.6, +4.5] | +0.003106 [-0.1011, +0.07407] | undecided |
| h=1 | (s3) against B1 | 1855 | +27.0% [+21.7, +35.4] | +0.5455 [+0.3197, +1.231] | gain |
| h=1 | (s3) against B1' | 1855 | +14.7% [+5.4, +22.0] | +0.2542 [+0.1372, +0.4197] | gain |
| h=1 | (s3) against B2 | 1855 | +40.7% [+23.8, +50.0] | +1.008 [+0.756, +1.315] | gain |
| h=1 | (s3) against (a) | 1855 | +5.5% [+2.9, +7.5] | +0.08546 [+0.04789, +0.1183] | gain |
| h=1 | (s3) against (s1) | 1855 | +7.8% [+4.5, +12.2] | +0.125 [+0.07887, +0.2007] | gain |
| h=1 | (s3) against spread_mr_ctx | 1855 | +7.1% [+3.8, +9.9] | +0.1127 [+0.07112, +0.1569] | gain |
| h=1 | (s4) against B1 | 1855 | +18.5% [+9.8, +30.5] | +0.3736 [+0.1459, +0.9506] | gain |
| h=1 | (s4) against B1' | 1855 | +4.8% [-3.9, +13.2] | +0.08223 [-0.05218, +0.2415] | undecided |
| h=1 | (s4) against B2 | 1855 | +33.7% [+19.4, +43.4] | +0.8365 [+0.5803, +1.13] | gain |
| h=1 | (s4) against (a) | 1855 | -5.6% [-12.6, -0.7] | -0.08646 [-0.1856, -0.01599] | loss |
| h=1 | (s4) against (s1) | 1855 | -2.9% [-6.0, -1.0] | -0.0469 [-0.09687, -0.02057] | loss |
| h=1 | (s4) against spread_mr_ctx | 1855 | -3.7% [-10.8, +1.1] | -0.05924 [-0.1632, +0.01674] | undecided |

### upper_tail_twcrps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=1 | (a) against B1 | 1855 | +31.6% [+25.8, +40.5] | +0.4052 [+0.1921, +1.187] | gain |
| h=1 | (a) against B1' | 1855 | +14.4% [-3.5, +26.9] | +0.1481 [+0.04729, +0.3099] | gain (was undecided) |
| h=1 | (a) against B2 | 1855 | +21.0% [-2.5, +36.7] | +0.2341 [+0.095, +0.3959] | gain (was undecided) |
| h=1 | (a) against spread_mr_ctx | 1855 | -0.6% [-4.3, +2.7] | -0.005333 [-0.03573, +0.02607] | undecided |
| h=1 | (s1) against B1 | 1855 | +30.6% [+23.1, +39.5] | +0.3927 [+0.1682, +1.08] | gain |
| h=1 | (s1) against B1' | 1855 | +13.2% [-4.4, +26.9] | +0.1355 [+0.01507, +0.304] | gain (was undecided) |
| h=1 | (s1) against B2 | 1855 | +19.9% [-2.8, +34.8] | +0.2216 [+0.07629, +0.3851] | gain (was undecided) |
| h=1 | (s1) against (a) | 1855 | -1.4% [-9.3, +3.5] | -0.01258 [-0.07396, +0.03403] | undecided |
| h=1 | (s1) against spread_mr_ctx | 1855 | -2.1% [-10.3, +3.4] | -0.01792 [-0.07986, +0.03194] | undecided |
| h=1 | (s2) against B1 | 1855 | +30.8% [+23.4, +39.3] | +0.3947 [+0.1737, +1.084] | gain |
| h=1 | (s2) against B1' | 1855 | +13.4% [-4.2, +27.1] | +0.1375 [+0.01967, +0.302] | gain (was undecided) |
| h=1 | (s2) against B2 | 1855 | +20.1% [-3.5, +34.5] | +0.2236 [+0.07893, +0.381] | gain (was undecided) |
| h=1 | (s2) against (a) | 1855 | -1.2% [-9.1, +3.5] | -0.01057 [-0.07427, +0.03404] | undecided |
| h=1 | (s2) against (s1) | 1855 | +0.2% [-2.3, +3.0] | +0.00202 [-0.0224, +0.02791] | undecided |
| h=1 | (s2) against spread_mr_ctx | 1855 | -1.8% [-10.4, +3.6] | -0.0159 [-0.08263, +0.03426] | undecided |
| h=1 | (s3) against B1 | 1855 | +36.5% [+31.0, +42.7] | +0.4684 [+0.242, +1.233] | gain |
| h=1 | (s3) against B1' | 1855 | +20.6% [-2.5, +33.1] | +0.2112 [+0.1008, +0.3883] | gain (was undecided) |
| h=1 | (s3) against B2 | 1855 | +26.7% [-1.4, +42.4] | +0.2973 [+0.155, +0.468] | gain (was undecided) |
| h=1 | (s3) against (a) | 1855 | +7.2% [+2.7, +10.9] | +0.06312 [+0.03548, +0.09565] | gain |
| h=1 | (s3) against (s1) | 1855 | +8.5% [+2.6, +15.8] | +0.07571 [+0.04217, +0.1309] | gain |
| h=1 | (s3) against spread_mr_ctx | 1855 | +6.6% [+1.6, +10.8] | +0.05779 [+0.0261, +0.09849] | gain |
| h=1 | (s4) against B1 | 1855 | +28.8% [+20.2, +39.7] | +0.3691 [+0.143, +1.075] | gain |
| h=1 | (s4) against B1' | 1855 | +10.9% [-4.3, +24.1] | +0.112 [-0.005726, +0.2795] | undecided |
| h=1 | (s4) against B2 | 1855 | +17.8% [-1.7, +32.1] | +0.1981 [+0.05597, +0.3601] | gain (was undecided) |
| h=1 | (s4) against (a) | 1855 | -4.1% [-14.2, +2.3] | -0.03609 [-0.1034, +0.01646] | undecided |
| h=1 | (s4) against (s1) | 1855 | -2.6% [-6.8, +0.3] | -0.02351 [-0.05182, -0.00591] | loss (was undecided) |
| h=1 | (s4) against spread_mr_ctx | 1855 | -4.7% [-15.3, +2.4] | -0.04142 [-0.111, +0.0159] | undecided |

### grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=2 | (a) against B1 | 1855 | +25.2% [+19.1, +40.4] | +0.5588 [+0.3156, +1.534] | gain |
| h=2 | (a) against B1' | 1855 | +10.1% [+4.1, +16.4] | +0.186 [+0.09038, +0.3286] | gain |
| h=2 | (a) against B2 | 1855 | +33.9% [+21.9, +43.2] | +0.85 [+0.6058, +1.16] | gain |
| h=2 | (a) against spread_mr_ctx | 1855 | +3.0% [+0.3, +5.6] | +0.05042 [+0.01083, +0.0945] | gain |
| h=2 | (s1) against B1 | 1855 | +24.0% [+16.0, +37.7] | +0.5326 [+0.2687, +1.35] | gain |
| h=2 | (s1) against B1' | 1855 | +8.7% [+0.6, +16.2] | +0.1598 [+0.02421, +0.3202] | gain |
| h=2 | (s1) against B2 | 1855 | +32.9% [+21.3, +42.0] | +0.8239 [+0.5716, +1.124] | gain |
| h=2 | (s1) against (a) | 1855 | -1.6% [-7.8, +2.4] | -0.02615 [-0.1219, +0.04061] | undecided |
| h=2 | (s1) against spread_mr_ctx | 1855 | +1.4% [-4.9, +5.9] | +0.02427 [-0.07855, +0.1048] | undecided |
| h=2 | (s2) against B1 | 1855 | +24.6% [+16.6, +37.7] | +0.5451 [+0.2789, +1.35] | gain |
| h=2 | (s2) against B1' | 1855 | +9.4% [+0.6, +17.1] | +0.1723 [+0.02936, +0.3344] | gain |
| h=2 | (s2) against B2 | 1855 | +33.4% [+21.3, +42.6] | +0.8364 [+0.5765, +1.134] | gain |
| h=2 | (s2) against (a) | 1855 | -0.8% [-8.1, +3.4] | -0.01365 [-0.1298, +0.05841] | undecided |
| h=2 | (s2) against (s1) | 1855 | +0.7% [-0.9, +2.1] | +0.0125 [-0.01467, +0.03459] | undecided |
| h=2 | (s2) against spread_mr_ctx | 1855 | +2.2% [-5.5, +7.0] | +0.03677 [-0.08709, +0.122] | undecided |
| h=2 | (s3) against B1 | 1855 | +27.9% [+22.1, +40.8] | +0.6185 [+0.3677, +1.572] | gain |
| h=2 | (s3) against B1' | 1855 | +13.3% [+6.5, +19.7] | +0.2457 [+0.1415, +0.3973] | gain |
| h=2 | (s3) against B2 | 1855 | +36.3% [+24.1, +45.4] | +0.9098 [+0.662, +1.218] | gain |
| h=2 | (s3) against (a) | 1855 | +3.6% [+1.5, +5.5] | +0.05975 [+0.02477, +0.09136] | gain |
| h=2 | (s3) against (s1) | 1855 | +5.1% [+2.1, +9.8] | +0.0859 [+0.04001, +0.1641] | gain |
| h=2 | (s3) against spread_mr_ctx | 1855 | +6.5% [+2.8, +9.6] | +0.1102 [+0.05967, +0.163] | gain |
| h=2 | (s4) against B1 | 1855 | +22.8% [+14.4, +37.6] | +0.5051 [+0.2387, +1.327] | gain |
| h=2 | (s4) against B1' | 1855 | +7.2% [-0.6, +14.7] | +0.1323 [-0.00123, +0.2925] | undecided |
| h=2 | (s4) against B2 | 1855 | +31.8% [+20.8, +40.9] | +0.7963 [+0.5421, +1.094] | gain |
| h=2 | (s4) against (a) | 1855 | -3.2% [-9.8, +1.2] | -0.05369 [-0.1507, +0.01746] | undecided |
| h=2 | (s4) against (s1) | 1855 | -1.6% [-3.3, -0.3] | -0.02754 [-0.05249, -0.009468] | loss |
| h=2 | (s4) against spread_mr_ctx | 1855 | -0.2% [-6.7, +4.4] | -0.003268 [-0.1066, +0.07823] | undecided |

### upper_tail_twcrps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=2 | (a) against B1 | 1855 | +34.1% [+27.0, +48.7] | +0.4614 [+0.2164, +1.554] | gain |
| h=2 | (a) against B1' | 1855 | +13.4% [+1.1, +25.0] | +0.138 [+0.05045, +0.2915] | gain |
| h=2 | (a) against B2 | 1855 | +20.8% [+5.3, +34.7] | +0.2338 [+0.1151, +0.3983] | gain |
| h=2 | (a) against spread_mr_ctx | 1855 | +1.0% [-2.7, +5.0] | +0.008986 [-0.02109, +0.04646] | undecided |
| h=2 | (s1) against B1 | 1855 | +33.3% [+24.4, +47.8] | +0.4501 [+0.188, +1.444] | gain |
| h=2 | (s1) against B1' | 1855 | +12.3% [-1.4, +25.3] | +0.1266 [+0.01413, +0.295] | gain (was undecided) |
| h=2 | (s1) against B2 | 1855 | +19.8% [+4.7, +32.4] | +0.2225 [+0.09153, +0.3879] | gain |
| h=2 | (s1) against (a) | 1855 | -1.3% [-9.6, +4.2] | -0.01132 [-0.0771, +0.04117] | undecided |
| h=2 | (s1) against spread_mr_ctx | 1855 | -0.3% [-9.3, +6.5] | -0.00233 [-0.07398, +0.0651] | undecided |
| h=2 | (s2) against B1 | 1855 | +33.5% [+24.4, +47.4] | +0.4537 [+0.1913, +1.434] | gain |
| h=2 | (s2) against B1' | 1855 | +12.6% [-1.8, +25.6] | +0.1303 [+0.01309, +0.2972] | gain (was undecided) |
| h=2 | (s2) against B2 | 1855 | +20.1% [+4.1, +32.7] | +0.2261 [+0.09005, +0.3876] | gain |
| h=2 | (s2) against (a) | 1855 | -0.9% [-10.5, +4.8] | -0.007698 [-0.08546, +0.04698] | undecided |
| h=2 | (s2) against (s1) | 1855 | +0.4% [-1.9, +2.5] | +0.003618 [-0.01914, +0.02204] | undecided |
| h=2 | (s2) against spread_mr_ctx | 1855 | +0.1% [-10.2, +7.1] | +0.001288 [-0.08277, +0.0711] | undecided |
| h=2 | (s3) against B1 | 1855 | +36.5% [+29.9, +49.2] | +0.4941 [+0.2432, +1.596] | gain |
| h=2 | (s3) against B1' | 1855 | +16.6% [+2.8, +28.5] | +0.1706 [+0.07487, +0.3359] | gain |
| h=2 | (s3) against B2 | 1855 | +23.7% [+6.7, +37.6] | +0.2665 [+0.1398, +0.4375] | gain |
| h=2 | (s3) against (a) | 1855 | +3.7% [+1.1, +6.2] | +0.03265 [+0.01054, +0.05841] | gain |
| h=2 | (s3) against (s1) | 1855 | +4.9% [+0.0, +12.7] | +0.04397 [+0.006896, +0.1032] | gain |
| h=2 | (s3) against spread_mr_ctx | 1855 | +4.6% [-0.4, +9.5] | +0.04164 [+0.004348, +0.09092] | gain (was undecided) |
| h=2 | (s4) against B1 | 1855 | +32.2% [+22.8, +48.4] | +0.4362 [+0.172, +1.445] | gain |
| h=2 | (s4) against B1' | 1855 | +10.9% [-1.6, +23.5] | +0.1127 [+0.001658, +0.2793] | gain (was undecided) |
| h=2 | (s4) against B2 | 1855 | +18.5% [+4.8, +30.6] | +0.2086 [+0.07644, +0.37] | gain |
| h=2 | (s4) against (a) | 1855 | -2.8% [-12.5, +3.4] | -0.02523 [-0.09328, +0.02975] | undecided |
| h=2 | (s4) against (s1) | 1855 | -1.5% [-4.5, +0.7] | -0.01391 [-0.03413, +0.001744] | undecided |
| h=2 | (s4) against spread_mr_ctx | 1855 | -1.8% [-11.7, +5.2] | -0.01624 [-0.08985, +0.05088] | undecided |

### grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=3 | (a) against B1 | 1855 | +26.6% [+20.5, +41.8] | +0.6229 [+0.3682, +1.58] | gain |
| h=3 | (a) against B1' | 1855 | +11.8% [+6.8, +17.9] | +0.2299 [+0.1322, +0.3882] | gain |
| h=3 | (a) against B2 | 1855 | +32.0% [+21.6, +41.1] | +0.8079 [+0.5634, +1.118] | gain |
| h=3 | (a) against spread_mr_ctx | 1855 | +3.5% [+1.1, +5.9] | +0.06143 [+0.02226, +0.105] | gain |
| h=3 | (s1) against B1 | 1855 | +26.2% [+18.5, +39.0] | +0.6125 [+0.3347, +1.396] | gain |
| h=3 | (s1) against B1' | 1855 | +11.3% [+3.4, +18.6] | +0.2194 [+0.07341, +0.392] | gain |
| h=3 | (s1) against B2 | 1855 | +31.6% [+21.1, +40.6] | +0.7975 [+0.5418, +1.095] | gain |
| h=3 | (s1) against (a) | 1855 | -0.6% [-6.9, +3.5] | -0.01042 [-0.1156, +0.06222] | undecided |
| h=3 | (s1) against spread_mr_ctx | 1855 | +2.9% [-3.5, +7.4] | +0.05101 [-0.05767, +0.135] | undecided |
| h=3 | (s2) against B1 | 1855 | +26.1% [+17.9, +38.4] | +0.6104 [+0.3291, +1.357] | gain |
| h=3 | (s2) against B1' | 1855 | +11.2% [+2.3, +18.8] | +0.2174 [+0.05659, +0.3905] | gain |
| h=3 | (s2) against B2 | 1855 | +31.5% [+20.5, +40.7] | +0.7954 [+0.5317, +1.09] | gain |
| h=3 | (s2) against (a) | 1855 | -0.7% [-9.3, +4.0] | -0.01246 [-0.1577, +0.06957] | undecided |
| h=3 | (s2) against (s1) | 1855 | -0.1% [-2.4, +1.2] | -0.002037 [-0.04239, +0.01991] | undecided |
| h=3 | (s2) against spread_mr_ctx | 1855 | +2.8% [-5.7, +7.9] | +0.04898 [-0.09573, +0.1426] | undecided |
| h=3 | (s3) against B1 | 1855 | +30.0% [+24.1, +42.3] | +0.7006 [+0.4365, +1.608] | gain |
| h=3 | (s3) against B1' | 1855 | +15.8% [+9.7, +22.2] | +0.3075 [+0.194, +0.4767] | gain |
| h=3 | (s3) against B2 | 1855 | +35.1% [+24.4, +43.9] | +0.8856 [+0.6398, +1.194] | gain |
| h=3 | (s3) against (a) | 1855 | +4.5% [+1.9, +6.8] | +0.07768 [+0.03697, +0.1149] | gain |
| h=3 | (s3) against (s1) | 1855 | +5.1% [+2.3, +9.8] | +0.0881 [+0.04098, +0.1741] | gain |
| h=3 | (s3) against spread_mr_ctx | 1855 | +7.8% [+4.2, +10.9] | +0.1391 [+0.08662, +0.1961] | gain |
| h=3 | (s4) against B1 | 1855 | +24.7% [+16.5, +38.6] | +0.5777 [+0.2974, +1.372] | gain |
| h=3 | (s4) against B1' | 1855 | +9.5% [+1.8, +16.9] | +0.1846 [+0.03921, +0.3562] | gain |
| h=3 | (s4) against B2 | 1855 | +30.2% [+20.1, +39.1] | +0.7627 [+0.5051, +1.057] | gain |
| h=3 | (s4) against (a) | 1855 | -2.6% [-9.3, +1.9] | -0.04522 [-0.1532, +0.03236] | undecided |
| h=3 | (s4) against (s1) | 1855 | -2.0% [-4.0, -0.7] | -0.0348 [-0.06637, -0.01534] | loss |
| h=3 | (s4) against spread_mr_ctx | 1855 | +0.9% [-5.8, +5.7] | +0.01621 [-0.09678, +0.1046] | undecided |

### upper_tail_twcrps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=3 | (a) against B1 | 1855 | +35.8% [+28.1, +51.6] | +0.5003 [+0.2434, +1.593] | gain |
| h=3 | (a) against B1' | 1855 | +16.0% [+6.1, +27.2] | +0.1705 [+0.0819, +0.3393] | gain |
| h=3 | (a) against B2 | 1855 | +20.8% [+8.5, +33.8] | +0.2359 [+0.1197, +0.3972] | gain |
| h=3 | (a) against spread_mr_ctx | 1855 | +2.0% [-1.4, +5.6] | +0.01793 [-0.0098, +0.05394] | undecided |
| h=3 | (s1) against B1 | 1855 | +35.0% [+25.7, +50.0] | +0.4898 [+0.2164, +1.45] | gain |
| h=3 | (s1) against B1' | 1855 | +15.0% [+2.4, +27.5] | +0.16 [+0.04114, +0.338] | gain |
| h=3 | (s1) against B2 | 1855 | +19.9% [+6.2, +32.0] | +0.2254 [+0.09228, +0.3909] | gain |
| h=3 | (s1) against (a) | 1855 | -1.2% [-9.9, +4.6] | -0.01052 [-0.08302, +0.04496] | undecided |
| h=3 | (s1) against spread_mr_ctx | 1855 | +0.8% [-8.4, +7.6] | +0.007406 [-0.0698, +0.07675] | undecided |
| h=3 | (s2) against B1 | 1855 | +34.3% [+24.0, +49.0] | +0.479 [+0.2055, +1.382] | gain |
| h=3 | (s2) against B1' | 1855 | +14.0% [+0.1, +26.6] | +0.1493 [+0.01943, +0.3228] | gain |
| h=3 | (s2) against B2 | 1855 | +18.9% [+4.3, +30.9] | +0.2147 [+0.06964, +0.3752] | gain |
| h=3 | (s2) against (a) | 1855 | -2.4% [-14.9, +4.3] | -0.02125 [-0.126, +0.04091] | undecided |
| h=3 | (s2) against (s1) | 1855 | -1.2% [-5.5, +0.9] | -0.01073 [-0.05233, +0.008323] | undecided |
| h=3 | (s2) against spread_mr_ctx | 1855 | -0.4% [-12.9, +7.2] | -0.003327 [-0.1078, +0.07225] | undecided |
| h=3 | (s3) against B1 | 1855 | +38.6% [+31.0, +51.9] | +0.5392 [+0.2743, +1.614] | gain |
| h=3 | (s3) against B1' | 1855 | +19.6% [+7.6, +31.3] | +0.2094 [+0.1068, +0.3967] | gain |
| h=3 | (s3) against B2 | 1855 | +24.3% [+9.7, +37.2] | +0.2748 [+0.1495, +0.4459] | gain |
| h=3 | (s3) against (a) | 1855 | +4.3% [+0.9, +7.6] | +0.0389 [+0.01247, +0.06988] | gain |
| h=3 | (s3) against (s1) | 1855 | +5.4% [+0.6, +13.7] | +0.04942 [+0.01194, +0.1174] | gain |
| h=3 | (s3) against spread_mr_ctx | 1855 | +6.2% [+0.8, +11.4] | +0.05683 [+0.01793, +0.1093] | gain |
| h=3 | (s4) against B1 | 1855 | +33.7% [+23.6, +50.5] | +0.4706 [+0.1937, +1.444] | gain |
| h=3 | (s4) against B1' | 1855 | +13.2% [+1.3, +25.4] | +0.1408 [+0.02112, +0.318] | gain |
| h=3 | (s4) against B2 | 1855 | +18.2% [+5.3, +29.7] | +0.2062 [+0.06837, +0.3695] | gain |
| h=3 | (s4) against (a) | 1855 | -3.3% [-13.4, +3.2] | -0.0297 [-0.1058, +0.02991] | undecided |
| h=3 | (s4) against (s1) | 1855 | -2.1% [-5.8, +0.1] | -0.01918 [-0.046, -0.003959] | loss (was undecided) |
| h=3 | (s4) against spread_mr_ctx | 1855 | -1.3% [-11.6, +6.0] | -0.01178 [-0.09348, +0.06069] | undecided |

### grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=4 | (a) against B1 | 1855 | +27.1% [+20.4, +43.9] | +0.6518 [+0.3815, +1.64] | gain |
| h=4 | (a) against B1' | 1855 | +13.3% [+9.0, +19.1] | +0.2697 [+0.1655, +0.4385] | gain |
| h=4 | (a) against B2 | 1855 | +30.7% [+21.3, +39.5] | +0.7769 [+0.529, +1.083] | gain |
| h=4 | (a) against spread_mr_ctx | 1855 | +3.3% [+0.9, +5.8] | +0.06034 [+0.01883, +0.1066] | gain |
| h=4 | (s1) against B1 | 1855 | +26.3% [+18.2, +39.9] | +0.6337 [+0.3454, +1.419] | gain |
| h=4 | (s1) against B1' | 1855 | +12.4% [+5.1, +19.4] | +0.2516 [+0.1012, +0.4331] | gain |
| h=4 | (s1) against B2 | 1855 | +30.0% [+19.9, +38.6] | +0.7588 [+0.5087, +1.047] | gain |
| h=4 | (s1) against (a) | 1855 | -1.0% [-7.0, +3.1] | -0.01808 [-0.1222, +0.05578] | undecided |
| h=4 | (s1) against spread_mr_ctx | 1855 | +2.3% [-3.9, +7.0] | +0.04225 [-0.06565, +0.1292] | undecided |
| h=4 | (s2) against B1 | 1855 | +26.2% [+17.8, +39.5] | +0.6316 [+0.3421, +1.392] | gain |
| h=4 | (s2) against B1' | 1855 | +12.3% [+4.3, +19.5] | +0.2495 [+0.0897, +0.4297] | gain |
| h=4 | (s2) against B2 | 1855 | +29.9% [+19.5, +38.6] | +0.7568 [+0.4992, +1.04] | gain |
| h=4 | (s2) against (a) | 1855 | -1.1% [-8.6, +3.4] | -0.02013 [-0.1513, +0.06051] | undecided |
| h=4 | (s2) against (s1) | 1855 | -0.1% [-1.7, +0.9] | -0.002046 [-0.03184, +0.01641] | undecided |
| h=4 | (s2) against spread_mr_ctx | 1855 | +2.2% [-5.5, +7.4] | +0.04021 [-0.09375, +0.1347] | undecided |
| h=4 | (s3) against B1 | 1855 | +30.1% [+23.6, +43.7] | +0.7243 [+0.4478, +1.636] | gain |
| h=4 | (s3) against B1' | 1855 | +16.9% [+11.5, +23.0] | +0.3422 [+0.2199, +0.5213] | gain |
| h=4 | (s3) against B2 | 1855 | +33.5% [+23.6, +42.0] | +0.8494 [+0.6029, +1.149] | gain |
| h=4 | (s3) against (a) | 1855 | +4.1% [+1.3, +6.5] | +0.0725 [+0.02848, +0.1127] | gain |
| h=4 | (s3) against (s1) | 1855 | +5.1% [+2.5, +9.1] | +0.09058 [+0.04588, +0.168] | gain |
| h=4 | (s3) against spread_mr_ctx | 1855 | +7.3% [+3.6, +10.6] | +0.1328 [+0.07556, +0.1935] | gain |
| h=4 | (s4) against B1 | 1855 | +24.5% [+15.8, +39.2] | +0.589 [+0.2977, +1.372] | gain |
| h=4 | (s4) against B1' | 1855 | +10.2% [+2.7, +17.4] | +0.2069 [+0.04976, +0.3895] | gain |
| h=4 | (s4) against B2 | 1855 | +28.2% [+18.3, +36.9] | +0.7142 [+0.4569, +1.003] | gain |
| h=4 | (s4) against (a) | 1855 | -3.6% [-10.1, +1.0] | -0.06274 [-0.1735, +0.0193] | undecided |
| h=4 | (s4) against (s1) | 1855 | -2.5% [-5.1, -0.9] | -0.04465 [-0.08755, -0.01912] | loss |
| h=4 | (s4) against spread_mr_ctx | 1855 | -0.1% [-6.9, +5.0] | -0.0024 [-0.121, +0.09297] | undecided |

### upper_tail_twcrps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=4 | (a) against B1 | 1855 | +36.6% [+27.5, +56.2] | +0.519 [+0.2491, +1.683] | gain |
| h=4 | (a) against B1' | 1855 | +17.9% [+10.2, +28.7] | +0.1962 [+0.1032, +0.3805] | gain |
| h=4 | (a) against B2 | 1855 | +20.9% [+10.3, +32.7] | +0.2384 [+0.1213, +0.3962] | gain |
| h=4 | (a) against spread_mr_ctx | 1855 | +1.8% [-1.7, +5.5] | +0.01626 [-0.01354, +0.05468] | undecided |
| h=4 | (s1) against B1 | 1855 | +34.9% [+23.9, +53.2] | +0.4948 [+0.2127, +1.486] | gain |
| h=4 | (s1) against B1' | 1855 | +15.7% [+4.8, +27.2] | +0.172 [+0.04932, +0.3565] | gain |
| h=4 | (s1) against B2 | 1855 | +18.8% [+6.3, +29.9] | +0.2142 [+0.08386, +0.3745] | gain |
| h=4 | (s1) against (a) | 1855 | -2.7% [-11.2, +3.4] | -0.02418 [-0.09746, +0.03117] | undecided |
| h=4 | (s1) against spread_mr_ctx | 1855 | -0.9% [-10.3, +6.4] | -0.007913 [-0.08715, +0.0623] | undecided |
| h=4 | (s2) against B1 | 1855 | +34.2% [+22.7, +52.3] | +0.4853 [+0.203, +1.438] | gain |
| h=4 | (s2) against B1' | 1855 | +14.8% [+3.2, +26.4] | +0.1625 [+0.03433, +0.3409] | gain |
| h=4 | (s2) against B2 | 1855 | +18.0% [+5.1, +28.8] | +0.2047 [+0.06755, +0.3594] | gain |
| h=4 | (s2) against (a) | 1855 | -3.7% [-14.7, +2.8] | -0.03372 [-0.1275, +0.02649] | undecided |
| h=4 | (s2) against (s1) | 1855 | -1.0% [-4.0, +0.5] | -0.009541 [-0.03865, +0.005053] | undecided |
| h=4 | (s2) against spread_mr_ctx | 1855 | -1.9% [-13.3, +5.8] | -0.01745 [-0.1142, +0.05658] | undecided |
| h=4 | (s3) against B1 | 1855 | +38.6% [+29.6, +55.7] | +0.5482 [+0.2737, +1.668] | gain |
| h=4 | (s3) against B1' | 1855 | +20.6% [+11.0, +31.7] | +0.2254 [+0.1184, +0.4228] | gain |
| h=4 | (s3) against B2 | 1855 | +23.5% [+10.9, +35.1] | +0.2676 [+0.1425, +0.4337] | gain |
| h=4 | (s3) against (a) | 1855 | +3.2% [-0.4, +6.8] | +0.02921 [-1.305e-05, +0.06131] | undecided |
| h=4 | (s3) against (s1) | 1855 | +5.8% [+1.4, +13.0] | +0.05339 [+0.01705, +0.1191] | gain |
| h=4 | (s3) against spread_mr_ctx | 1855 | +5.0% [-0.5, +10.5] | +0.04548 [+0.003392, +0.1013] | gain (was undecided) |
| h=4 | (s4) against B1 | 1855 | +32.9% [+21.0, +53.3] | +0.467 [+0.1822, +1.445] | gain |
| h=4 | (s4) against B1' | 1855 | +13.2% [+2.0, +24.8] | +0.1442 [+0.01628, +0.3256] | gain |
| h=4 | (s4) against B2 | 1855 | +16.4% [+4.0, +27.0] | +0.1864 [+0.04558, +0.3481] | gain |
| h=4 | (s4) against (a) | 1855 | -5.8% [-16.3, +1.4] | -0.05198 [-0.1341, +0.01005] | undecided |
| h=4 | (s4) against (s1) | 1855 | -3.0% [-8.1, -0.2] | -0.02781 [-0.0681, -0.007563] | loss |
| h=4 | (s4) against spread_mr_ctx | 1855 | -3.9% [-15.4, +4.3] | -0.03572 [-0.1254, +0.04011] | undecided |

### grid_crps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=5 | (a) against B1 | 1855 | +26.9% [+19.8, +44.4] | +0.6623 [+0.3907, +1.65] | gain |
| h=5 | (a) against B1' | 1855 | +14.2% [+10.0, +19.9] | +0.2977 [+0.1894, +0.4739] | gain |
| h=5 | (a) against B2 | 1855 | +29.3% [+20.1, +37.9] | +0.7456 [+0.4946, +1.044] | gain |
| h=5 | (a) against spread_mr_ctx | 1855 | +3.4% [+1.0, +5.9] | +0.06397 [+0.02085, +0.112] | gain |
| h=5 | (s1) against B1 | 1855 | +26.2% [+18.0, +40.8] | +0.647 [+0.3584, +1.45] | gain |
| h=5 | (s1) against B1' | 1855 | +13.4% [+6.6, +20.3] | +0.2824 [+0.1316, +0.4684] | gain |
| h=5 | (s1) against B2 | 1855 | +28.7% [+18.8, +37.1] | +0.7302 [+0.4783, +1.017] | gain |
| h=5 | (s1) against (a) | 1855 | -0.9% [-6.4, +3.2] | -0.01533 [-0.1143, +0.05881] | undecided |
| h=5 | (s1) against spread_mr_ctx | 1855 | +2.6% [-3.2, +7.3] | +0.04864 [-0.05408, +0.1375] | undecided |
| h=5 | (s2) against B1 | 1855 | +26.3% [+17.9, +40.4] | +0.6477 [+0.3598, +1.428] | gain |
| h=5 | (s2) against B1' | 1855 | +13.5% [+6.2, +20.4] | +0.2831 [+0.1266, +0.4693] | gain |
| h=5 | (s2) against B2 | 1855 | +28.7% [+18.7, +37.2] | +0.7309 [+0.4739, +1.015] | gain |
| h=5 | (s2) against (a) | 1855 | -0.8% [-7.4, +3.5] | -0.01461 [-0.1331, +0.06415] | undecided |
| h=5 | (s2) against (s1) | 1855 | +0.0% [-1.3, +1.0] | +0.0007219 [-0.02406, +0.01799] | undecided |
| h=5 | (s2) against spread_mr_ctx | 1855 | +2.6% [-4.3, +7.6] | +0.04936 [-0.07411, +0.1431] | undecided |
| h=5 | (s3) against B1 | 1855 | +29.8% [+23.0, +44.4] | +0.7354 [+0.4575, +1.645] | gain |
| h=5 | (s3) against B1' | 1855 | +17.6% [+12.3, +23.5] | +0.3708 [+0.2445, +0.553] | gain |
| h=5 | (s3) against B2 | 1855 | +32.1% [+22.7, +40.4] | +0.8186 [+0.5707, +1.111] | gain |
| h=5 | (s3) against (a) | 1855 | +4.1% [+1.1, +6.5] | +0.07304 [+0.02477, +0.1156] | gain |
| h=5 | (s3) against (s1) | 1855 | +4.9% [+2.5, +8.5] | +0.08837 [+0.04657, +0.1596] | gain |
| h=5 | (s3) against spread_mr_ctx | 1855 | +7.3% [+3.6, +10.7] | +0.137 [+0.07857, +0.2004] | gain |
| h=5 | (s4) against B1 | 1855 | +24.3% [+15.6, +39.8] | +0.5989 [+0.3075, +1.387] | gain |
| h=5 | (s4) against B1' | 1855 | +11.2% [+4.0, +18.3] | +0.2343 [+0.0773, +0.4223] | gain |
| h=5 | (s4) against B2 | 1855 | +26.8% [+17.0, +35.4] | +0.6821 [+0.4234, +0.966] | gain |
| h=5 | (s4) against (a) | 1855 | -3.5% [-9.7, +1.0] | -0.06341 [-0.1706, +0.01918] | undecided |
| h=5 | (s4) against (s1) | 1855 | -2.6% [-5.2, -0.9] | -0.04808 [-0.09437, -0.0204] | loss |
| h=5 | (s4) against spread_mr_ctx | 1855 | +0.0% [-6.5, +5.1] | +0.0005577 [-0.1167, +0.09738] | undecided |

### upper_tail_twcrps, by lead

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| h=5 | (a) against B1 | 1855 | +35.8% [+25.4, +59.2] | +0.5088 [+0.2396, +1.717] | gain |
| h=5 | (a) against B1' | 1855 | +17.3% [+10.0, +28.4] | +0.1906 [+0.09536, +0.3801] | gain |
| h=5 | (a) against B2 | 1855 | +20.4% [+10.2, +31.5] | +0.2346 [+0.1187, +0.3898] | gain |
| h=5 | (a) against spread_mr_ctx | 1855 | +2.2% [-1.4, +6.0] | +0.0203 [-0.01104, +0.06213] | undecided |
| h=5 | (s1) against B1 | 1855 | +34.4% [+22.4, +55.9] | +0.4897 [+0.2068, +1.515] | gain |
| h=5 | (s1) against B1' | 1855 | +15.5% [+5.1, +27.2] | +0.1716 [+0.05242, +0.3595] | gain |
| h=5 | (s1) against B2 | 1855 | +18.8% [+6.7, +29.5] | +0.2156 [+0.08443, +0.3749] | gain |
| h=5 | (s1) against (a) | 1855 | -2.1% [-10.1, +3.8] | -0.01901 [-0.08937, +0.03647] | undecided |
| h=5 | (s1) against spread_mr_ctx | 1855 | +0.1% [-8.8, +7.4] | +0.001287 [-0.07561, +0.0736] | undecided |
| h=5 | (s2) against B1 | 1855 | +33.8% [+21.5, +55.1] | +0.4812 [+0.2, +1.484] | gain |
| h=5 | (s2) against B1' | 1855 | +14.8% [+4.0, +26.3] | +0.1631 [+0.04165, +0.348] | gain |
| h=5 | (s2) against B2 | 1855 | +18.0% [+5.6, +28.7] | +0.207 [+0.07301, +0.3633] | gain |
| h=5 | (s2) against (a) | 1855 | -3.0% [-12.6, +3.1] | -0.02754 [-0.112, +0.02996] | undecided |
| h=5 | (s2) against (s1) | 1855 | -0.9% [-3.4, +0.5] | -0.008532 [-0.03204, +0.004912] | undecided |
| h=5 | (s2) against spread_mr_ctx | 1855 | -0.8% [-11.0, +6.7] | -0.007245 [-0.09477, +0.0675] | undecided |
| h=5 | (s3) against B1 | 1855 | +38.0% [+27.5, +58.1] | +0.5405 [+0.2641, +1.676] | gain |
| h=5 | (s3) against B1' | 1855 | +20.1% [+11.1, +31.1] | +0.2224 [+0.1147, +0.4226] | gain |
| h=5 | (s3) against B2 | 1855 | +23.2% [+10.9, +34.3] | +0.2663 [+0.1417, +0.4303] | gain |
| h=5 | (s3) against (a) | 1855 | +3.5% [-0.5, +7.3] | +0.03176 [-0.001026, +0.06665] | undecided |
| h=5 | (s3) against (s1) | 1855 | +5.4% [+1.5, +11.9] | +0.05077 [+0.01725, +0.1094] | gain |
| h=5 | (s3) against spread_mr_ctx | 1855 | +5.6% [-0.2, +11.3] | +0.05206 [+0.00525, +0.1124] | gain (was undecided) |
| h=5 | (s4) against B1 | 1855 | +32.2% [+19.4, +55.5] | +0.4573 [+0.1728, +1.466] | gain |
| h=5 | (s4) against B1' | 1855 | +12.6% [+1.6, +24.4] | +0.1391 [+0.0124, +0.3284] | gain |
| h=5 | (s4) against B2 | 1855 | +15.9% [+3.6, +26.5] | +0.1831 [+0.04046, +0.3434] | gain |
| h=5 | (s4) against (a) | 1855 | -5.6% [-15.9, +1.5] | -0.0515 [-0.1317, +0.01144] | undecided |
| h=5 | (s4) against (s1) | 1855 | -3.5% [-8.7, -0.3] | -0.03249 [-0.07658, -0.0106] | loss |
| h=5 | (s4) against spread_mr_ctx | 1855 | -3.3% [-14.5, +4.9] | -0.0312 [-0.1213, +0.04724] | undecided |

### grid_crps, by all decision days

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| all decision days | (a) against B1 | 1855 | +25.8% [+19.6, +41.9] | +0.5912 [+0.3428, +1.551] | gain |
| all decision days | (a) against B1' | 1855 | +11.9% [+7.2, +18.1] | +0.2304 [+0.1364, +0.3953] | gain |
| all decision days | (a) against B2 | 1855 | +32.6% [+22.1, +41.7] | +0.8207 [+0.5766, +1.132] | gain |
| all decision days | (a) against spread_mr_ctx | 1855 | +3.0% [+0.6, +5.5] | +0.05267 [+0.01281, +0.09531] | gain |
| all decision days | (s1) against B1 | 1855 | +24.9% [+17.1, +38.5] | +0.5693 [+0.3024, +1.362] | gain |
| all decision days | (s1) against B1' | 1855 | +10.8% [+3.3, +18.1] | +0.2085 [+0.07138, +0.3824] | gain |
| all decision days | (s1) against B2 | 1855 | +31.7% [+20.9, +40.8] | +0.7988 [+0.5483, +1.091] | gain |
| all decision days | (s1) against (a) | 1855 | -1.3% [-7.4, +2.5] | -0.02191 [-0.1218, +0.04423] | undecided |
| all decision days | (s1) against spread_mr_ctx | 1855 | +1.8% [-4.4, +6.1] | +0.03077 [-0.07216, +0.1093] | undecided |
| all decision days | (s2) against B1 | 1855 | +25.1% [+17.2, +38.2] | +0.5742 [+0.3062, +1.348] | gain |
| all decision days | (s2) against B1' | 1855 | +11.1% [+3.1, +18.4] | +0.2134 [+0.06993, +0.3857] | gain |
| all decision days | (s2) against B2 | 1855 | +31.9% [+20.8, +41.0] | +0.8037 [+0.5463, +1.097] | gain |
| all decision days | (s2) against (a) | 1855 | -1.0% [-8.5, +3.1] | -0.01699 [-0.1419, +0.05397] | undecided |
| all decision days | (s2) against (s1) | 1855 | +0.3% [-1.4, +1.5] | +0.004918 [-0.02446, +0.0248] | undecided |
| all decision days | (s2) against spread_mr_ctx | 1855 | +2.0% [-5.6, +6.8] | +0.03568 [-0.09283, +0.1201] | undecided |
| all decision days | (s3) against B1 | 1855 | +29.0% [+23.1, +42.1] | +0.6648 [+0.4079, +1.575] | gain |
| all decision days | (s3) against B1' | 1855 | +15.8% [+9.9, +22.0] | +0.3041 [+0.1944, +0.4775] | gain |
| all decision days | (s3) against B2 | 1855 | +35.5% [+24.6, +44.4] | +0.8944 [+0.6494, +1.199] | gain |
| all decision days | (s3) against (a) | 1855 | +4.3% [+1.8, +6.4] | +0.07369 [+0.03455, +0.1078] | gain |
| all decision days | (s3) against (s1) | 1855 | +5.6% [+3.0, +9.9] | +0.09559 [+0.05253, +0.1747] | gain |
| all decision days | (s3) against spread_mr_ctx | 1855 | +7.2% [+3.6, +10.3] | +0.1264 [+0.07552, +0.1802] | gain |
| all decision days | (s4) against B1 | 1855 | +23.1% [+14.7, +38.0] | +0.5289 [+0.2594, +1.318] | gain |
| all decision days | (s4) against B1' | 1855 | +8.7% [+1.4, +16.1] | +0.1681 [+0.03076, +0.3393] | gain |
| all decision days | (s4) against B2 | 1855 | +30.1% [+19.7, +39.2] | +0.7584 [+0.5041, +1.051] | gain |
| all decision days | (s4) against (a) | 1855 | -3.7% [-10.1, +0.7] | -0.0623 [-0.1643, +0.01] | undecided |
| all decision days | (s4) against (s1) | 1855 | -2.3% [-4.6, -0.8] | -0.04039 [-0.07735, -0.01799] | loss |
| all decision days | (s4) against spread_mr_ctx | 1855 | -0.6% [-7.1, +4.1] | -0.009628 [-0.1192, +0.07413] | undecided |

### upper_tail_twcrps, by all decision days

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| all decision days | (a) against B1 | 1855 | +34.8% [+27.0, +51.7] | +0.4789 [+0.2292, +1.568] | gain |
| all decision days | (a) against B1' | 1855 | +15.8% [+6.5, +27.4] | +0.1687 [+0.0828, +0.3553] | gain |
| all decision days | (a) against B2 | 1855 | +20.8% [+7.4, +33.9] | +0.2354 [+0.118, +0.3982] | gain |
| all decision days | (a) against spread_mr_ctx | 1855 | +1.3% [-2.1, +5.0] | +0.01163 [-0.01672, +0.04745] | undecided |
| all decision days | (s1) against B1 | 1855 | +33.7% [+24.2, +49.9] | +0.4634 [+0.2003, +1.448] | gain |
| all decision days | (s1) against B1' | 1855 | +14.4% [+2.7, +27.0] | +0.1532 [+0.04071, +0.3413] | gain |
| all decision days | (s1) against B2 | 1855 | +19.4% [+5.3, +31.8] | +0.2198 [+0.09045, +0.3835] | gain |
| all decision days | (s1) against (a) | 1855 | -1.7% [-10.1, +3.6] | -0.01552 [-0.08345, +0.03507] | undecided |
| all decision days | (s1) against spread_mr_ctx | 1855 | -0.4% [-9.3, +6.1] | -0.003894 [-0.07706, +0.06014] | undecided |
| all decision days | (s2) against B1 | 1855 | +33.4% [+23.6, +49.1] | +0.4588 [+0.1951, +1.414] | gain |
| all decision days | (s2) against B1' | 1855 | +13.9% [+1.7, +26.5] | +0.1485 [+0.03409, +0.328] | gain |
| all decision days | (s2) against B2 | 1855 | +19.0% [+4.4, +31.0] | +0.2152 [+0.07999, +0.3745] | gain |
| all decision days | (s2) against (a) | 1855 | -2.2% [-12.7, +3.4] | -0.02016 [-0.1061, +0.03184] | undecided |
| all decision days | (s2) against (s1) | 1855 | -0.5% [-3.2, +1.3] | -0.004633 [-0.0316, +0.01187] | undecided |
| all decision days | (s2) against spread_mr_ctx | 1855 | -0.9% [-11.6, +5.9] | -0.008527 [-0.09803, +0.05829] | undecided |
| all decision days | (s3) against B1 | 1855 | +37.7% [+30.2, +51.7] | +0.5181 [+0.2599, +1.597] | gain |
| all decision days | (s3) against B1' | 1855 | +19.5% [+8.4, +31.2] | +0.2078 [+0.1086, +0.4091] | gain |
| all decision days | (s3) against B2 | 1855 | +24.3% [+8.9, +37.2] | +0.2745 [+0.1484, +0.4451] | gain |
| all decision days | (s3) against (a) | 1855 | +4.4% [+1.0, +7.6] | +0.03913 [+0.01369, +0.06945] | gain |
| all decision days | (s3) against (s1) | 1855 | +6.0% [+1.6, +13.6] | +0.05465 [+0.02122, +0.1164] | gain |
| all decision days | (s3) against spread_mr_ctx | 1855 | +5.6% [+0.5, +10.8] | +0.05076 [+0.01267, +0.1024] | gain |
| all decision days | (s4) against B1 | 1855 | +32.0% [+21.6, +50.4] | +0.44 [+0.1736, +1.431] | gain |
| all decision days | (s4) against B1' | 1855 | +12.2% [+1.0, +24.7] | +0.1298 [+0.01441, +0.3133] | gain |
| all decision days | (s4) against B2 | 1855 | +17.4% [+4.2, +29.0] | +0.1965 [+0.06201, +0.357] | gain |
| all decision days | (s4) against (a) | 1855 | -4.3% [-14.3, +2.2] | -0.0389 [-0.1113, +0.016] | undecided |
| all decision days | (s4) against (s1) | 1855 | -2.6% [-6.5, +0.0] | -0.02338 [-0.05405, -0.005957] | loss (was undecided) |
| all decision days | (s4) against spread_mr_ctx | 1855 | -3.0% [-13.7, +4.3] | -0.02727 [-0.1059, +0.03963] | undecided |

### grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2018-19 | (a) against B1 | 361 | +34.1% [+24.4, +59.4] | +1.974 [+0.8044, +8.888] | gain |
| 2018-19 | (a) against B1' | 361 | +11.6% [+1.1, +27.7] | +0.4986 [+0.1452, +1.378] | gain |
| 2018-19 | (a) against B2 | 361 | +14.5% [+1.1, +27.9] | +0.645 [+0.2071, +1.18] | gain |
| 2018-19 | (a) against spread_mr_ctx | 361 | -3.3% [-7.5, +1.2] | -0.1227 [-0.2216, +0.01039] | undecided |
| 2018-19 | (s1) against B1 | 361 | +31.5% [+18.7, +53.3] | +1.822 [+0.5675, +6.791] | gain |
| 2018-19 | (s1) against B1' | 361 | +8.0% [-7.5, +24.5] | +0.3461 [-0.2254, +1.183] | undecided |
| 2018-19 | (s1) against B2 | 361 | +11.0% [-4.9, +24.4] | +0.4925 [-0.1275, +1.121] | undecided |
| 2018-19 | (s1) against (a) | 361 | -4.0% [-15.9, +2.9] | -0.1525 [-0.5521, +0.1246] | undecided |
| 2018-19 | (s1) against spread_mr_ctx | 361 | -7.4% [-22.5, +2.3] | -0.2751 [-0.6913, +0.06635] | undecided |
| 2018-19 | (s2) against B1 | 361 | +30.1% [+15.7, +51.5] | +1.741 [+0.4486, +6.214] | gain |
| 2018-19 | (s2) against B1' | 361 | +6.2% [-11.4, +22.3] | +0.2658 [-0.3947, +1.086] | undecided |
| 2018-19 | (s2) against B2 | 361 | +9.2% [-8.2, +22.4] | +0.4122 [-0.2907, +1.064] | undecided |
| 2018-19 | (s2) against (a) | 361 | -6.1% [-24.6, +2.3] | -0.2328 [-0.8245, +0.09274] | undecided |
| 2018-19 | (s2) against (s1) | 361 | -2.0% [-9.0, -0.0] | -0.08029 [-0.3576, -0.01311] | loss |
| 2018-19 | (s2) against spread_mr_ctx | 361 | -9.6% [-30.5, +1.9] | -0.3554 [-0.9271, +0.02661] | undecided |
| 2018-19 | (s3) against B1 | 361 | +36.1% [+26.5, +58.5] | +2.088 [+0.9021, +9.016] | gain |
| 2018-19 | (s3) against B1' | 361 | +14.2% [+1.3, +30.6] | +0.6128 [+0.2072, +1.518] | gain |
| 2018-19 | (s3) against B2 | 361 | +17.0% [+0.7, +31.2] | +0.7592 [+0.2628, +1.339] | gain |
| 2018-19 | (s3) against (a) | 361 | +3.0% [-0.0, +5.9] | +0.1142 [+0.0138, +0.2216] | gain (was undecided) |
| 2018-19 | (s3) against (s1) | 361 | +6.7% [+0.7, +18.0] | +0.2667 [+0.07676, +0.6604] | gain |
| 2018-19 | (s3) against spread_mr_ctx | 361 | -0.2% [-5.1, +4.8] | -0.008439 [-0.1705, +0.2067] | undecided |
| 2018-19 | (s4) against B1 | 361 | +29.5% [+15.6, +53.9] | +1.708 [+0.4313, +6.69] | gain |
| 2018-19 | (s4) against B1' | 361 | +5.4% [-9.1, +20.6] | +0.2324 [-0.333, +1.037] | undecided |
| 2018-19 | (s4) against B2 | 361 | +8.5% [-6.3, +20.7] | +0.3788 [-0.264, +1.014] | undecided |
| 2018-19 | (s4) against (a) | 361 | -7.0% [-21.2, +1.9] | -0.2662 [-0.687, +0.04246] | undecided |
| 2018-19 | (s4) against (s1) | 361 | -2.9% [-9.2, +0.4] | -0.1137 [-0.3301, -0.0179] | loss (was undecided) |
| 2018-19 | (s4) against spread_mr_ctx | 361 | -10.5% [-27.7, +1.9] | -0.3889 [-0.8386, -0.02118] | loss (was undecided) |

### upper_tail_twcrps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2018-19 | (a) against B1 | 361 | +35.7% [+25.2, +60.3] | +1.885 [+0.6971, +8.759] | gain |
| 2018-19 | (a) against B1' | 361 | +11.5% [-0.5, +30.8] | +0.4411 [+0.08072, +1.374] | gain (was undecided) |
| 2018-19 | (a) against B2 | 361 | +11.0% [-1.2, +23.7] | +0.419 [+0.05043, +0.875] | gain (was undecided) |
| 2018-19 | (a) against spread_mr_ctx | 361 | -2.5% [-6.9, +2.6] | -0.08234 [-0.1823, +0.07006] | undecided |
| 2018-19 | (s1) against B1 | 361 | +36.0% [+24.1, +56.0] | +1.902 [+0.6538, +7.376] | gain |
| 2018-19 | (s1) against B1' | 361 | +11.9% [-5.6, +30.9] | +0.4581 [-0.06768, +1.357] | undecided |
| 2018-19 | (s1) against B2 | 361 | +11.4% [-4.7, +24.2] | +0.436 [-0.05186, +0.9508] | undecided |
| 2018-19 | (s1) against (a) | 361 | +0.5% [-7.9, +6.2] | +0.01705 [-0.2669, +0.2421] | undecided |
| 2018-19 | (s1) against spread_mr_ctx | 361 | -2.0% [-12.7, +6.1] | -0.0653 [-0.3633, +0.2513] | undecided |
| 2018-19 | (s2) against B1 | 361 | +34.7% [+21.9, +54.3] | +1.834 [+0.5585, +6.809] | gain |
| 2018-19 | (s2) against B1' | 361 | +10.2% [-8.5, +28.3] | +0.3904 [-0.1871, +1.258] | undecided |
| 2018-19 | (s2) against B2 | 361 | +9.7% [-7.3, +21.9] | +0.3683 [-0.1806, +0.8936] | undecided |
| 2018-19 | (s2) against (a) | 361 | -1.5% [-14.2, +5.2] | -0.05072 [-0.4645, +0.2102] | undecided |
| 2018-19 | (s2) against (s1) | 361 | -2.0% [-9.3, -0.0] | -0.06777 [-0.2977, -0.01321] | loss |
| 2018-19 | (s2) against spread_mr_ctx | 361 | -4.0% [-19.2, +5.2] | -0.1331 [-0.5256, +0.2023] | undecided |
| 2018-19 | (s3) against B1 | 361 | +38.5% [+28.2, +59.8] | +2.03 [+0.8325, +8.919] | gain |
| 2018-19 | (s3) against B1' | 361 | +15.3% [-0.4, +34.4] | +0.5865 [+0.1718, +1.547] | gain (was undecided) |
| 2018-19 | (s3) against B2 | 361 | +14.8% [-1.5, +29.0] | +0.5644 [+0.1498, +1.052] | gain (was undecided) |
| 2018-19 | (s3) against (a) | 361 | +4.3% [-0.0, +7.8] | +0.1454 [+0.05925, +0.2448] | gain (was undecided) |
| 2018-19 | (s3) against (s1) | 361 | +3.8% [-1.0, +13.4] | +0.1283 [-0.0205, +0.4043] | undecided |
| 2018-19 | (s3) against spread_mr_ctx | 361 | +1.9% [-3.0, +7.7] | +0.06303 [-0.08529, +0.306] | undecided |
| 2018-19 | (s4) against B1 | 361 | +34.7% [+21.9, +56.7] | +1.831 [+0.5593, +7.314] | gain |
| 2018-19 | (s4) against B1' | 361 | +10.1% [-6.0, +27.6] | +0.3867 [-0.1543, +1.257] | undecided |
| 2018-19 | (s4) against B2 | 361 | +9.6% [-5.4, +21.2] | +0.3646 [-0.156, +0.8869] | undecided |
| 2018-19 | (s4) against (a) | 361 | -1.6% [-12.4, +5.0] | -0.05442 [-0.3775, +0.2009] | undecided |
| 2018-19 | (s4) against (s1) | 361 | -2.1% [-8.9, +1.0] | -0.07147 [-0.2338, +0.006684] | undecided |
| 2018-19 | (s4) against spread_mr_ctx | 361 | -4.1% [-17.9, +5.6] | -0.1368 [-0.4759, +0.1975] | undecided |

### grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2020 | (a) against B1 | 251 | +14.6% [+6.3, +22.8] | +0.2409 [+0.09387, +0.5855] | gain |
| 2020 | (a) against B1' | 251 | +12.6% [+2.5, +27.0] | +0.2022 [+0.01813, +0.7297] | gain |
| 2020 | (a) against B2 | 251 | +49.7% [+24.4, +70.1] | +1.39 [+0.5801, +3.093] | gain |
| 2020 | (a) against spread_mr_ctx | 251 | +14.9% [+8.2, +20.4] | +0.2467 [+0.1893, +0.3185] | gain |
| 2020 | (s1) against B1 | 251 | -2.2% [-46.4, +15.8] | -0.0359 [-0.6068, +0.2625] | undecided |
| 2020 | (s1) against B1' | 251 | -4.6% [-47.1, +17.8] | -0.07457 [-0.5957, +0.2635] | undecided |
| 2020 | (s1) against B2 | 251 | +39.8% [+16.8, +64.1] | +1.113 [+0.3996, +2.51] | gain |
| 2020 | (s1) against (a) | 251 | -19.7% [-68.0, -4.1] | -0.2768 [-1.056, -0.06665] | loss |
| 2020 | (s1) against spread_mr_ctx | 251 | -1.8% [-44.8, +10.4] | -0.03012 [-0.7171, +0.1667] | undecided |
| 2020 | (s2) against B1 | 251 | +4.2% [-44.4, +19.7] | +0.06913 [-0.5112, +0.3454] | undecided |
| 2020 | (s2) against B1' | 251 | +1.9% [-41.2, +19.6] | +0.03046 [-0.4579, +0.3367] | undecided |
| 2020 | (s2) against B2 | 251 | +43.5% [+19.4, +65.7] | +1.218 [+0.528, +2.614] | gain |
| 2020 | (s2) against (a) | 251 | -12.2% [-67.3, +1.4] | -0.1717 [-0.9974, +0.02626] | undecided |
| 2020 | (s2) against (s1) | 251 | +6.2% [+1.3, +15.0] | +0.105 [+0.04935, +0.2168] | gain |
| 2020 | (s2) against spread_mr_ctx | 251 | +4.5% [-43.2, +16.6] | +0.07491 [-0.6001, +0.2544] | undecided |
| 2020 | (s3) against B1 | 251 | +12.4% [-11.9, +22.8] | +0.2039 [-0.05296, +0.4523] | undecided |
| 2020 | (s3) against B1' | 251 | +10.3% [-11.5, +23.7] | +0.1653 [-0.08949, +0.5175] | undecided |
| 2020 | (s3) against B2 | 251 | +48.4% [+25.2, +69.2] | +1.353 [+0.6054, +2.886] | gain |
| 2020 | (s3) against (a) | 251 | -2.6% [-29.7, +4.4] | -0.03695 [-0.4042, +0.06133] | undecided |
| 2020 | (s3) against (s1) | 251 | +14.2% [+6.0, +26.5] | +0.2398 [+0.1142, +0.6454] | gain |
| 2020 | (s3) against spread_mr_ctx | 251 | +12.7% [-11.7, +21.0] | +0.2097 [-1.172e-05, +0.2995] | undecided |
| 2020 | (s4) against B1 | 251 | -6.3% [-45.9, +13.9] | -0.1046 [-0.6283, +0.2036] | undecided |
| 2020 | (s4) against B1' | 251 | -8.9% [-47.9, +17.4] | -0.1433 [-0.6328, +0.2104] | undecided |
| 2020 | (s4) against B2 | 251 | +37.3% [+15.1, +62.0] | +1.044 [+0.303, +2.435] | gain |
| 2020 | (s4) against (a) | 251 | -24.5% [-62.9, -7.1] | -0.3455 [-1.002, -0.1354] | loss |
| 2020 | (s4) against (s1) | 251 | -4.1% [-10.8, +0.7] | -0.0687 [-0.1443, -0.01415] | loss (was undecided) |
| 2020 | (s4) against spread_mr_ctx | 251 | -6.0% [-43.0, +6.2] | -0.09882 [-0.6925, +0.0996] | undecided |

### upper_tail_twcrps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2020 | (a) against B1 | 251 | +31.0% [+17.6, +56.1] | +0.2293 [+0.05281, +1.653] | gain |
| 2020 | (a) against B1' | 251 | +32.1% [+19.4, +63.8] | +0.2412 [+0.032, +2.216] | gain |
| 2020 | (a) against B2 | 251 | +58.1% [-22.6, +84.8] | +0.7083 [+0.361, +1.127] | gain (was undecided) |
| 2020 | (a) against spread_mr_ctx | 251 | +22.9% [-17.4, +50.8] | +0.1521 [+0.08842, +0.2214] | gain (was undecided) |
| 2020 | (s1) against B1 | 251 | -2.8% [-51.7, +34.7] | -0.02039 [-0.2641, +0.2586] | undecided |
| 2020 | (s1) against B1' | 251 | -1.1% [-54.2, +43.3] | -0.008532 [-0.2626, +0.3533] | undecided |
| 2020 | (s1) against B2 | 251 | +37.6% [-17.4, +68.2] | +0.4586 [+0.08857, +0.836] | gain (was undecided) |
| 2020 | (s1) against (a) | 251 | -48.9% [-180.0, +5.1] | -0.2497 [-0.8954, -0.09727] | loss (was undecided) |
| 2020 | (s1) against spread_mr_ctx | 251 | -14.7% [-118.2, +9.2] | -0.09761 [-0.9433, +0.08016] | undecided |
| 2020 | (s2) against B1 | 251 | +10.6% [-29.8, +32.5] | +0.07811 [-0.1306, +0.3633] | undecided |
| 2020 | (s2) against B1' | 251 | +12.0% [-28.2, +38.0] | +0.08997 [-0.1351, +0.6374] | undecided |
| 2020 | (s2) against B2 | 251 | +45.7% [-35.3, +77.3] | +0.5571 [+0.2101, +0.9225] | gain (was undecided) |
| 2020 | (s2) against (a) | 251 | -29.6% [-231.6, +0.2] | -0.1512 [-1.084, -0.006518] | loss (was undecided) |
| 2020 | (s2) against (s1) | 251 | +13.0% [-4.8, +37.0] | +0.0985 [+0.04949, +0.2211] | gain (was undecided) |
| 2020 | (s2) against spread_mr_ctx | 251 | +0.1% [-126.4, +24.8] | +0.000892 [-0.8889, +0.1752] | undecided |
| 2020 | (s3) against B1 | 251 | +24.7% [+9.9, +45.1] | +0.1829 [+0.01771, +1.06] | gain |
| 2020 | (s3) against B1' | 251 | +25.9% [+11.0, +53.8] | +0.1947 [-0.001213, +1.695] | undecided (was gain) |
| 2020 | (s3) against B2 | 251 | +54.3% [-10.6, +82.0] | +0.6618 [+0.3365, +1.058] | gain (was undecided) |
| 2020 | (s3) against (a) | 251 | -9.1% [-51.7, +1.1] | -0.04644 [-0.2381, -0.001595] | loss (was undecided) |
| 2020 | (s3) against (s1) | 251 | +26.7% [-7.5, +56.0] | +0.2033 [+0.0904, +0.6362] | gain (was undecided) |
| 2020 | (s3) against spread_mr_ctx | 251 | +15.9% [-32.9, +38.2] | +0.1056 [-0.07651, +0.191] | undecided |
| 2020 | (s4) against B1 | 251 | -10.4% [-69.0, +40.5] | -0.07685 [-0.3337, +0.2194] | undecided |
| 2020 | (s4) against B1' | 251 | -8.6% [-72.1, +52.3] | -0.06499 [-0.3358, +0.3116] | undecided |
| 2020 | (s4) against B2 | 251 | +33.0% [-9.2, +62.3] | +0.4021 [+0.01088, +0.7869] | gain (was undecided) |
| 2020 | (s4) against (a) | 251 | -59.9% [-173.2, +15.4] | -0.3062 [-0.8324, -0.1513] | loss (was undecided) |
| 2020 | (s4) against (s1) | 251 | -7.4% [-24.1, +3.5] | -0.05646 [-0.1306, -0.009179] | loss (was undecided) |
| 2020 | (s4) against spread_mr_ctx | 251 | -23.2% [-131.3, +3.4] | -0.1541 [-0.8623, +0.02022] | undecided |

### grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2021-23 | (a) against B1 | 748 | +5.5% [-0.6, +10.6] | +0.03824 [-0.0004272, +0.07045] | undecided |
| 2021-23 | (a) against B1' | 748 | +1.0% [-5.3, +6.6] | +0.006723 [-0.03586, +0.04236] | undecided |
| 2021-23 | (a) against B2 | 748 | +55.0% [+40.7, +67.4] | +0.8061 [+0.4997, +1.18] | gain |
| 2021-23 | (a) against spread_mr_ctx | 748 | +8.2% [+2.1, +16.3] | +0.05876 [+0.01641, +0.1098] | gain |
| 2021-23 | (s1) against B1 | 748 | +6.2% [+0.9, +10.8] | +0.04303 [+0.007065, +0.07902] | gain |
| 2021-23 | (s1) against B1' | 748 | +1.7% [-3.9, +6.9] | +0.01151 [-0.0248, +0.04774] | undecided |
| 2021-23 | (s1) against B2 | 748 | +55.3% [+43.2, +65.7] | +0.8109 [+0.5248, +1.166] | gain |
| 2021-23 | (s1) against (a) | 748 | +0.7% [-5.2, +5.4] | +0.004788 [-0.03166, +0.04003] | undecided |
| 2021-23 | (s1) against spread_mr_ctx | 748 | +8.9% [+4.4, +13.4] | +0.06355 [+0.02996, +0.1012] | gain |
| 2021-23 | (s2) against B1 | 748 | +9.7% [+4.6, +14.2] | +0.06754 [+0.03325, +0.104] | gain |
| 2021-23 | (s2) against B1' | 748 | +5.4% [-0.2, +10.6] | +0.03603 [+0.000587, +0.07351] | gain (was undecided) |
| 2021-23 | (s2) against B2 | 748 | +57.0% [+44.2, +67.8] | +0.8354 [+0.5407, +1.202] | gain |
| 2021-23 | (s2) against (a) | 748 | +4.4% [+0.3, +8.9] | +0.02931 [-0.0007745, +0.06836] | undecided (was gain) |
| 2021-23 | (s2) against (s1) | 748 | +3.7% [+1.2, +8.2] | +0.02452 [+0.008381, +0.05424] | gain |
| 2021-23 | (s2) against spread_mr_ctx | 748 | +12.3% [+6.7, +18.0] | +0.08807 [+0.0472, +0.136] | gain |
| 2021-23 | (s3) against B1 | 748 | +9.1% [+3.5, +13.7] | +0.06362 [+0.03016, +0.09493] | gain |
| 2021-23 | (s3) against B1' | 748 | +4.8% [-0.9, +9.8] | +0.03211 [-0.003093, +0.06449] | undecided |
| 2021-23 | (s3) against B2 | 748 | +56.7% [+43.6, +68.2] | +0.8315 [+0.5346, +1.202] | gain |
| 2021-23 | (s3) against (a) | 748 | +3.9% [+1.7, +6.1] | +0.02539 [+0.009048, +0.04575] | gain |
| 2021-23 | (s3) against (s1) | 748 | +3.1% [+0.0, +7.7] | +0.0206 [+0.002158, +0.04641] | gain |
| 2021-23 | (s3) against spread_mr_ctx | 748 | +11.7% [+6.5, +18.1] | +0.08415 [+0.04778, +0.1269] | gain |
| 2021-23 | (s4) against B1 | 748 | +3.1% [-4.5, +8.6] | +0.02159 [-0.02793, +0.06165] | undecided |
| 2021-23 | (s4) against B1' | 748 | -1.5% [-9.3, +4.5] | -0.009924 [-0.06018, +0.03017] | undecided |
| 2021-23 | (s4) against B2 | 748 | +53.9% [+41.4, +64.3] | +0.7894 [+0.5046, +1.139] | gain |
| 2021-23 | (s4) against (a) | 748 | -2.5% [-9.8, +2.9] | -0.01665 [-0.05891, +0.01904] | undecided |
| 2021-23 | (s4) against (s1) | 748 | -3.3% [-14.0, -0.8] | -0.02143 [-0.09626, -0.005096] | loss |
| 2021-23 | (s4) against spread_mr_ctx | 748 | +5.9% [+0.1, +10.6] | +0.04211 [+0.001811, +0.07792] | gain |

### upper_tail_twcrps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2021-23 | (a) against B1 | 748 | +12.3% [-68.3, +44.6] | +0.0011 [-0.003843, +0.00335] | undecided |
| 2021-23 | (a) against B1' | 748 | -16.5% [-107.0, +16.7] | -0.001111 [-0.01001, +0.001231] | undecided |
| 2021-23 | (a) against B2 | 748 | -156.2% [-814.7, -37.2] | -0.004779 [-0.05043, +0.000294] | undecided (was loss) |
| 2021-23 | (a) against spread_mr_ctx | 748 | +54.4% [-44.3, +86.0] | +0.009339 [+0.004353, +0.01617] | gain (was undecided) |
| 2021-23 | (s1) against B1 | 748 | +27.3% [-31.8, +51.4] | +0.002438 [-0.0001449, +0.004906] | undecided |
| 2021-23 | (s1) against B1' | 748 | +3.4% [-43.7, +29.5] | +0.000227 [-0.002533, +0.001786] | undecided |
| 2021-23 | (s1) against B2 | 748 | -112.5% [-498.6, -28.6] | -0.003441 [-0.03227, +0.0003153] | undecided (was loss) |
| 2021-23 | (s1) against (a) | 748 | +17.1% [-3.6, +37.5] | +0.001338 [-7.527e-05, +0.009241] | undecided |
| 2021-23 | (s1) against spread_mr_ctx | 748 | +62.2% [-10.4, +88.5] | +0.01068 [+0.005612, +0.01803] | gain (was undecided) |
| 2021-23 | (s2) against B1 | 748 | +42.0% [-0.5, +64.9] | +0.003758 [+0.001763, +0.008238] | gain (was undecided) |
| 2021-23 | (s2) against B1' | 748 | +23.0% [-5.1, +39.8] | +0.001547 [+0.0005092, +0.003578] | gain (was undecided) |
| 2021-23 | (s2) against B2 | 748 | -69.3% [-364.3, -7.7] | -0.002121 [-0.02415, +0.0005179] | undecided (was loss) |
| 2021-23 | (s2) against (a) | 748 | +33.9% [+14.9, +55.0] | +0.002658 [+0.000241, +0.02188] | gain |
| 2021-23 | (s2) against (s1) | 748 | +20.3% [+7.5, +57.3] | +0.00132 [+0.0001822, +0.00837] | gain |
| 2021-23 | (s2) against spread_mr_ctx | 748 | +69.8% [+0.7, +89.8] | +0.012 [+0.006413, +0.02096] | gain |
| 2021-23 | (s3) against B1 | 748 | +26.3% [-27.7, +52.5] | +0.002355 [+0.0001014, +0.004681] | gain (was undecided) |
| 2021-23 | (s3) against B1' | 748 | +2.1% [-44.7, +27.0] | +0.0001444 [-0.00256, +0.001644] | undecided |
| 2021-23 | (s3) against B2 | 748 | -115.2% [-539.5, -26.8] | -0.003524 [-0.03477, +0.0003426] | undecided (was loss) |
| 2021-23 | (s3) against (a) | 748 | +16.0% [+6.8, +33.5] | +0.001255 [+8.16e-05, +0.01142] | gain |
| 2021-23 | (s3) against (s1) | 748 | -1.3% [-12.3, +15.0] | -8.262e-05 [-0.0006803, +0.00042] | undecided |
| 2021-23 | (s3) against spread_mr_ctx | 748 | +61.7% [-13.7, +88.0] | +0.01059 [+0.005564, +0.0181] | gain (was undecided) |
| 2021-23 | (s4) against B1 | 748 | -19.3% [-559.4, +42.7] | -0.001729 [-0.04238, +0.003847] | undecided |
| 2021-23 | (s4) against B1' | 748 | -58.6% [-740.7, +28.2] | -0.00394 [-0.06535, +0.001918] | undecided |
| 2021-23 | (s4) against B2 | 748 | -248.6% [-2911.8, -31.7] | -0.007608 [-0.1762, +0.0002376] | undecided (was loss) |
| 2021-23 | (s4) against (a) | 748 | -36.1% [-430.7, +17.5] | -0.002829 [-0.05514, +0.001088] | undecided |
| 2021-23 | (s4) against (s1) | 748 | -64.1% [-2592.6, +1.8] | -0.004167 [-0.2333, +0.000671] | undecided |
| 2021-23 | (s4) against spread_mr_ctx | 748 | +37.9% [-257.5, +80.5] | +0.00651 [-0.00317, +0.01247] | undecided |

### grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2024 | (a) against B1 | 250 | +25.3% [+18.5, +35.3] | +0.4088 [+0.2018, +0.974] | gain |
| 2024 | (a) against B1' | 250 | +19.0% [+11.1, +29.5] | +0.2819 [+0.1057, +0.7081] | gain |
| 2024 | (a) against B2 | 250 | +13.6% [+2.8, +23.2] | +0.19 [+0.03647, +0.3826] | gain |
| 2024 | (a) against spread_mr_ctx | 250 | +4.1% [-2.1, +12.3] | +0.0513 [-0.02334, +0.2276] | undecided |
| 2024 | (s1) against B1 | 250 | +30.6% [+22.2, +41.7] | +0.4942 [+0.2379, +1.155] | gain |
| 2024 | (s1) against B1' | 250 | +24.7% [+15.1, +36.1] | +0.3673 [+0.1412, +0.8817] | gain |
| 2024 | (s1) against B2 | 250 | +19.8% [+9.0, +28.2] | +0.2754 [+0.09913, +0.5102] | gain |
| 2024 | (s1) against (a) | 250 | +7.1% [+2.1, +11.9] | +0.08539 [+0.01642, +0.186] | gain |
| 2024 | (s1) against spread_mr_ctx | 250 | +10.9% [+1.3, +21.0] | +0.1367 [+0.005778, +0.413] | gain |
| 2024 | (s2) against B1 | 250 | +30.6% [+22.2, +41.7] | +0.4939 [+0.2378, +1.154] | gain |
| 2024 | (s2) against B1' | 250 | +24.7% [+15.0, +36.1] | +0.367 [+0.1411, +0.8819] | gain |
| 2024 | (s2) against B2 | 250 | +19.7% [+8.9, +28.2] | +0.2752 [+0.09893, +0.5096] | gain |
| 2024 | (s2) against (a) | 250 | +7.1% [+2.1, +11.9] | +0.08513 [+0.01625, +0.1856] | gain |
| 2024 | (s2) against (s1) | 250 | -0.0% [-0.1, -0.0] | -0.0002565 [-0.001355, -5.078e-05] | loss |
| 2024 | (s2) against spread_mr_ctx | 250 | +10.9% [+1.2, +21.0] | +0.1364 [+0.005683, +0.4119] | gain |
| 2024 | (s3) against B1 | 250 | +31.0% [+24.3, +40.6] | +0.5005 [+0.2604, +1.133] | gain |
| 2024 | (s3) against B1' | 250 | +25.1% [+17.2, +35.1] | +0.3736 [+0.1654, +0.8617] | gain |
| 2024 | (s3) against B2 | 250 | +20.2% [+9.5, +29.0] | +0.2818 [+0.1102, +0.5054] | gain |
| 2024 | (s3) against (a) | 250 | +7.6% [+5.1, +10.0] | +0.09173 [+0.04682, +0.1567] | gain |
| 2024 | (s3) against (s1) | 250 | +0.6% [-3.0, +3.4] | +0.006339 [-0.03241, +0.03346] | undecided |
| 2024 | (s3) against spread_mr_ctx | 250 | +11.4% [+4.2, +19.5] | +0.143 [+0.03235, +0.3942] | gain |
| 2024 | (s4) against B1 | 250 | +30.6% [+22.3, +41.6] | +0.4944 [+0.239, +1.153] | gain |
| 2024 | (s4) against B1' | 250 | +24.7% [+15.1, +35.9] | +0.3675 [+0.1427, +0.8785] | gain |
| 2024 | (s4) against B2 | 250 | +19.8% [+9.0, +28.3] | +0.2757 [+0.09982, +0.5091] | gain |
| 2024 | (s4) against (a) | 250 | +7.1% [+2.2, +11.8] | +0.08561 [+0.01827, +0.1828] | gain |
| 2024 | (s4) against (s1) | 250 | +0.0% [-0.5, +0.6] | +0.0002221 [-0.00604, +0.00663] | undecided |
| 2024 | (s4) against spread_mr_ctx | 250 | +10.9% [+1.6, +20.7] | +0.1369 [+0.008192, +0.4077] | gain |

### upper_tail_twcrps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2024 | (a) against B1 | 250 | +34.6% [+15.9, +103.7] | +0.09708 [+0.004158, +1.015] | gain |
| 2024 | (a) against B1' | 250 | +30.5% [+16.0, +73.0] | +0.08036 [+0.003648, +0.6966] | gain |
| 2024 | (a) against spread_mr_ctx | 250 | +9.9% [-2.4, +20.4] | +0.02011 [-0.005197, +0.3942] | undecided |
| 2024 | (s1) against B1 | 250 | +39.4% [+19.6, +83.8] | +0.1104 [+0.01074, +0.8764] | gain |
| 2024 | (s1) against B1' | 250 | +35.5% [+19.3, +67.3] | +0.09365 [+0.009201, +0.6343] | gain |
| 2024 | (s1) against (a) | 250 | +7.2% [-14.7, +18.0] | +0.01328 [+0.003012, +0.09028] | gain (was undecided) |
| 2024 | (s1) against spread_mr_ctx | 250 | +16.4% [+5.6, +44.3] | +0.0334 [-0.001691, +0.911] | undecided (was gain) |
| 2024 | (s2) against B1 | 250 | +39.4% [+19.6, +83.7] | +0.1104 [+0.01075, +0.8766] | gain |
| 2024 | (s2) against B1' | 250 | +35.5% [+19.3, +67.3] | +0.09365 [+0.009208, +0.6344] | gain |
| 2024 | (s2) against (a) | 250 | +7.2% [-14.7, +18.0] | +0.01329 [+0.00301, +0.0903] | gain (was undecided) |
| 2024 | (s2) against (s1) | 250 | +0.0% [-0.0, +0.0] | +1.899e-06 [-1.511e-05, +1.824e-05] | undecided |
| 2024 | (s2) against spread_mr_ctx | 250 | +16.4% [+5.6, +44.3] | +0.0334 [-0.001692, +0.9114] | undecided (was gain) |
| 2024 | (s3) against B1 | 250 | +38.0% [+19.3, +87.9] | +0.1065 [+0.009814, +1] | gain |
| 2024 | (s3) against B1' | 250 | +34.1% [+19.2, +66.5] | +0.08982 [+0.008441, +0.7078] | gain |
| 2024 | (s3) against (a) | 250 | +5.2% [-17.1, +15.7] | +0.00946 [+0.002453, +0.06367] | gain (was undecided) |
| 2024 | (s3) against (s1) | 250 | -2.2% [-4.8, +1.4] | -0.003824 [-0.02822, -3.552e-05] | loss (was undecided) |
| 2024 | (s3) against spread_mr_ctx | 250 | +14.5% [+1.9, +38.6] | +0.02957 [-0.002607, +0.8908] | undecided (was gain) |
| 2024 | (s4) against B1 | 250 | +39.3% [+19.6, +83.9] | +0.1102 [+0.01064, +0.8734] | gain |
| 2024 | (s4) against B1' | 250 | +35.4% [+19.3, +67.4] | +0.09346 [+0.00913, +0.6316] | gain |
| 2024 | (s4) against (a) | 250 | +7.1% [-15.1, +17.7] | +0.0131 [+0.002863, +0.08668] | gain (was undecided) |
| 2024 | (s4) against (s1) | 250 | -0.1% [-0.3, -0.0] | -0.0001867 [-0.000838, -1.264e-05] | loss |
| 2024 | (s4) against spread_mr_ctx | 250 | +16.3% [+5.5, +43.8] | +0.03321 [-0.0018, +0.8732] | undecided (was gain) |

### grid_crps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2025-26 | (a) against B1 | 249 | +23.4% [+16.4, +30.2] | +0.7857 [+0.4429, +1.257] | gain |
| 2025-26 | (a) against B1' | 249 | +16.2% [+8.8, +23.4] | +0.4967 [+0.2184, +0.8637] | gain |
| 2025-26 | (a) against B2 | 249 | +31.9% [+8.2, +51.8] | +1.204 [+0.154, +3.038] | gain |
| 2025-26 | (a) against spread_mr_ctx | 249 | +3.5% [-0.8, +7.8] | +0.09389 [-0.0184, +0.2373] | undecided |
| 2025-26 | (s1) against B1 | 249 | +31.0% [+23.1, +38.5] | +1.04 [+0.655, +1.538] | gain |
| 2025-26 | (s1) against B1' | 249 | +24.5% [+16.7, +31.5] | +0.7506 [+0.439, +1.122] | gain |
| 2025-26 | (s1) against B2 | 249 | +38.6% [+18.6, +55.4] | +1.458 [+0.4232, +3.277] | gain |
| 2025-26 | (s1) against (a) | 249 | +9.9% [+1.7, +17.3] | +0.2539 [+0.06633, +0.4487] | gain |
| 2025-26 | (s1) against spread_mr_ctx | 249 | +13.0% [+5.8, +19.9] | +0.3478 [+0.1546, +0.5619] | gain |
| 2025-26 | (s2) against B1 | 249 | +30.0% [+22.5, +37.5] | +1.008 [+0.6431, +1.485] | gain |
| 2025-26 | (s2) against B1' | 249 | +23.4% [+15.4, +30.6] | +0.7191 [+0.4173, +1.08] | gain |
| 2025-26 | (s2) against B2 | 249 | +37.8% [+17.9, +54.0] | +1.427 [+0.4071, +3.186] | gain |
| 2025-26 | (s2) against (a) | 249 | +8.6% [+0.3, +16.2] | +0.2224 [+0.03723, +0.4129] | gain |
| 2025-26 | (s2) against (s1) | 249 | -1.4% [-4.2, +0.2] | -0.03153 [-0.1015, +0.004575] | undecided |
| 2025-26 | (s2) against spread_mr_ctx | 249 | +11.9% [+4.5, +18.7] | +0.3163 [+0.1281, +0.5233] | gain |
| 2025-26 | (s3) against B1 | 249 | +31.8% [+24.4, +38.9] | +1.068 [+0.6818, +1.591] | gain |
| 2025-26 | (s3) against B1' | 249 | +25.4% [+18.1, +32.4] | +0.7794 [+0.4737, +1.175] | gain |
| 2025-26 | (s3) against B2 | 249 | +39.4% [+19.0, +56.2] | +1.487 [+0.4341, +3.353] | gain |
| 2025-26 | (s3) against (a) | 249 | +11.0% [+4.7, +16.9] | +0.2827 [+0.1411, +0.4426] | gain |
| 2025-26 | (s3) against (s1) | 249 | +1.2% [-1.8, +4.1] | +0.02879 [-0.03677, +0.1003] | undecided |
| 2025-26 | (s3) against spread_mr_ctx | 249 | +14.1% [+8.8, +19.1] | +0.3766 [+0.2212, +0.5534] | gain |
| 2025-26 | (s4) against B1 | 249 | +30.9% [+22.8, +38.6] | +1.036 [+0.6516, +1.535] | gain |
| 2025-26 | (s4) against B1' | 249 | +24.4% [+16.3, +31.6] | +0.7476 [+0.4322, +1.122] | gain |
| 2025-26 | (s4) against B2 | 249 | +38.5% [+18.6, +55.1] | +1.455 [+0.4194, +3.251] | gain |
| 2025-26 | (s4) against (a) | 249 | +9.8% [+1.2, +17.5] | +0.2508 [+0.0576, +0.4514] | gain |
| 2025-26 | (s4) against (s1) | 249 | -0.1% [-0.9, +0.4] | -0.003061 [-0.02093, +0.008935] | undecided |
| 2025-26 | (s4) against spread_mr_ctx | 249 | +12.9% [+5.6, +19.9] | +0.3447 [+0.1511, +0.5581] | gain |

### upper_tail_twcrps, by regime

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2025-26 | (a) against B1 | 249 | +32.3% [+26.0, +39.3] | +0.5183 [+0.1787, +1.184] | gain |
| 2025-26 | (a) against B1' | 249 | +22.3% [+14.5, +30.8] | +0.3108 [+0.08795, +0.7112] | gain |
| 2025-26 | (a) against B2 | 249 | +29.6% [+14.0, +48.4] | +0.455 [+0.02137, +2.018] | gain |
| 2025-26 | (a) against spread_mr_ctx | 249 | +1.0% [-9.8, +12.3] | +0.01062 [-0.08116, +0.2036] | undecided |
| 2025-26 | (s1) against B1 | 249 | +39.5% [+29.0, +48.3] | +0.6336 [+0.222, +1.434] | gain |
| 2025-26 | (s1) against B1' | 249 | +30.5% [+19.2, +41.4] | +0.4261 [+0.1449, +0.9522] | gain |
| 2025-26 | (s1) against B2 | 249 | +37.0% [+25.3, +52.6] | +0.5703 [+0.09113, +2.196] | gain |
| 2025-26 | (s1) against (a) | 249 | +10.6% [-1.0, +22.0] | +0.1153 [+0.00922, +0.2981] | gain (was undecided) |
| 2025-26 | (s1) against spread_mr_ctx | 249 | +11.5% [+2.1, +21.0] | +0.1259 [-0.01331, +0.3778] | undecided (was gain) |
| 2025-26 | (s2) against B1 | 249 | +36.9% [+26.6, +46.0] | +0.5917 [+0.2163, +1.34] | gain |
| 2025-26 | (s2) against B1' | 249 | +27.5% [+15.7, +38.6] | +0.3842 [+0.1322, +0.8782] | gain |
| 2025-26 | (s2) against B2 | 249 | +34.3% [+22.5, +49.7] | +0.5284 [+0.07749, +2.071] | gain |
| 2025-26 | (s2) against (a) | 249 | +6.8% [-5.4, +17.4] | +0.0734 [-0.01893, +0.2181] | undecided |
| 2025-26 | (s2) against (s1) | 249 | -4.3% [-10.4, -0.7] | -0.04187 [-0.1413, -0.001721] | loss |
| 2025-26 | (s2) against spread_mr_ctx | 249 | +7.7% [-2.3, +16.6] | +0.08402 [-0.03485, +0.2825] | undecided |
| 2025-26 | (s3) against B1 | 249 | +41.2% [+30.8, +50.3] | +0.661 [+0.237, +1.468] | gain |
| 2025-26 | (s3) against B1' | 249 | +32.5% [+21.7, +45.0] | +0.4535 [+0.1595, +1.023] | gain |
| 2025-26 | (s3) against B2 | 249 | +38.8% [+27.9, +52.8] | +0.5978 [+0.11, +2.199] | gain |
| 2025-26 | (s3) against (a) | 249 | +13.2% [+1.6, +24.2] | +0.1427 [+0.03759, +0.3526] | gain |
| 2025-26 | (s3) against (s1) | 249 | +2.8% [-0.3, +7.6] | +0.02746 [-0.002609, +0.09272] | undecided |
| 2025-26 | (s3) against spread_mr_ctx | 249 | +14.0% [+6.5, +22.5] | +0.1534 [+0.01343, +0.4319] | gain |
| 2025-26 | (s4) against B1 | 249 | +39.5% [+27.6, +48.9] | +0.6325 [+0.2232, +1.433] | gain |
| 2025-26 | (s4) against B1' | 249 | +30.5% [+17.6, +41.8] | +0.425 [+0.1442, +0.9603] | gain |
| 2025-26 | (s4) against B2 | 249 | +37.0% [+25.6, +51.9] | +0.5692 [+0.09351, +2.156] | gain |
| 2025-26 | (s4) against (a) | 249 | +10.5% [-2.5, +22.7] | +0.1142 [+0.002976, +0.3027] | gain (was undecided) |
| 2025-26 | (s4) against (s1) | 249 | -0.1% [-1.8, +1.5] | -0.001111 [-0.017, +0.01102] | undecided |
| 2025-26 | (s4) against spread_mr_ctx | 249 | +11.4% [+2.0, +21.1] | +0.1248 [-0.01191, +0.3734] | undecided (was gain) |

### scaled_grid_crps, by scaled

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| 2018-19 | (a) against B1 | 118 | +47.7% [+25.8, +149.4] | +2.106 [+0.08956, +35.39] | gain |
| 2018-19 | (a) against B1' | 118 | -1.2% [-14.0, +8.7] | -0.02639 [-0.2915, +0.1958] | undecided |
| 2018-19 | (a) against B2 | 118 | -0.7% [-17.7, +12.9] | -0.01605 [-0.4023, +0.3572] | undecided |
| 2018-19 | (a) against spread_mr_ctx | 118 | -5.9% [-14.7, +4.2] | -0.1295 [-0.2301, -0.04611] | loss (was undecided) |
| 2018-19 | (s1) against B1 | 118 | +43.6% [+20.2, +147.0] | +1.926 [-0.07263, +30.56] | undecided (was gain) |
| 2018-19 | (s1) against B1' | 118 | -9.1% [-27.2, +2.9] | -0.2071 [-0.6652, +0.08781] | undecided |
| 2018-19 | (s1) against B2 | 118 | -8.6% [-38.3, +10.1] | -0.1967 [-0.8777, +0.3205] | undecided |
| 2018-19 | (s1) against (a) | 118 | -7.8% [-22.6, +1.4] | -0.1807 [-0.5267, +0.01649] | undecided |
| 2018-19 | (s1) against spread_mr_ctx | 118 | -14.2% [-39.5, +3.5] | -0.3101 [-0.7632, -0.0669] | loss (was undecided) |
| 2018-19 | (s2) against B1 | 118 | +43.4% [+20.1, +147.7] | +1.92 [-0.07873, +30.32] | undecided (was gain) |
| 2018-19 | (s2) against B1' | 118 | -9.3% [-27.5, +2.9] | -0.2129 [-0.6735, +0.08382] | undecided |
| 2018-19 | (s2) against B2 | 118 | -8.8% [-39.2, +9.9] | -0.2026 [-0.8911, +0.3075] | undecided |
| 2018-19 | (s2) against (a) | 118 | -8.1% [-23.5, +1.5] | -0.1865 [-0.5413, +0.008409] | undecided |
| 2018-19 | (s2) against (s1) | 118 | -0.2% [-0.8, +0.3] | -0.005853 [-0.01794, +0.004903] | undecided |
| 2018-19 | (s2) against spread_mr_ctx | 118 | -14.5% [-40.1, +3.9] | -0.316 [-0.7815, -0.07402] | loss (was undecided) |
| 2018-19 | (s3) against B1 | 118 | +47.4% [+26.9, +132.3] | +2.096 [+0.1003, +34.27] | gain |
| 2018-19 | (s3) against B1' | 118 | -1.6% [-19.0, +9.9] | -0.03663 [-0.4202, +0.2326] | undecided |
| 2018-19 | (s3) against B2 | 118 | -1.1% [-24.6, +15.6] | -0.02628 [-0.5815, +0.4358] | undecided |
| 2018-19 | (s3) against (a) | 118 | -0.4% [-7.2, +4.8] | -0.01023 [-0.2101, +0.1226] | undecided |
| 2018-19 | (s3) against (s1) | 118 | +6.8% [-0.2, +12.3] | +0.1704 [+0.09107, +0.3117] | gain (was undecided) |
| 2018-19 | (s3) against spread_mr_ctx | 118 | -6.4% [-21.7, +3.7] | -0.1397 [-0.4221, +0.04129] | undecided |
| 2018-19 | (s4) against B1 | 118 | +41.4% [+13.6, +139.2] | +1.829 [-0.2081, +24.12] | undecided (was gain) |
| 2018-19 | (s4) against B1' | 118 | -13.3% [-34.5, +1.2] | -0.3038 [-0.7422, +0.01868] | undecided |
| 2018-19 | (s4) against B2 | 118 | -12.8% [-50.0, +9.2] | -0.2934 [-1.057, +0.2569] | undecided |
| 2018-19 | (s4) against (a) | 118 | -12.0% [-36.7, +4.4] | -0.2774 [-0.7308, -0.01682] | loss (was undecided) |
| 2018-19 | (s4) against (s1) | 118 | -3.9% [-19.8, +2.8] | -0.09672 [-0.3491, +0.01525] | undecided |
| 2018-19 | (s4) against spread_mr_ctx | 118 | -18.6% [-54.5, +8.5] | -0.4069 [-0.9639, -0.08582] | loss (was undecided) |
| 2020 | (a) against B1 | 251 | +14.9% [+6.9, +26.7] | +0.1151 [+0.04119, +0.3387] | gain |
| 2020 | (a) against B1' | 251 | +12.0% [+1.1, +33.1] | +0.08959 [-0.0008499, +0.4139] | undecided (was gain) |
| 2020 | (a) against B2 | 251 | +43.4% [+17.9, +65.5] | +0.504 [+0.1878, +1.08] | gain |
| 2020 | (a) against spread_mr_ctx | 251 | +10.6% [+6.0, +14.9] | +0.07782 [+0.05415, +0.1039] | gain |
| 2020 | (s1) against B1 | 251 | +11.6% [-3.2, +25.8] | +0.08937 [-0.01028, +0.2747] | undecided |
| 2020 | (s1) against B1' | 251 | +8.5% [-8.4, +30.7] | +0.06388 [-0.04686, +0.3202] | undecided |
| 2020 | (s1) against B2 | 251 | +41.2% [+18.8, +62.5] | +0.4783 [+0.1822, +0.9916] | gain |
| 2020 | (s1) against (a) | 251 | -3.9% [-16.8, +3.2] | -0.02571 [-0.1045, +0.0192] | undecided |
| 2020 | (s1) against spread_mr_ctx | 251 | +7.1% [-5.7, +13.2] | +0.05211 [-0.02817, +0.09897] | undecided |
| 2020 | (s2) against B1 | 251 | +13.3% [-1.3, +25.9] | +0.1027 [+0.006887, +0.2833] | gain (was undecided) |
| 2020 | (s2) against B1' | 251 | +10.3% [-5.3, +30.0] | +0.07722 [-0.03054, +0.3349] | undecided |
| 2020 | (s2) against B2 | 251 | +42.3% [+20.1, +63.0] | +0.4916 [+0.2011, +1.003] | gain |
| 2020 | (s2) against (a) | 251 | -1.9% [-14.0, +5.0] | -0.01236 [-0.08586, +0.03307] | undecided |
| 2020 | (s2) against (s1) | 251 | +2.0% [-0.1, +6.1] | +0.01335 [+0.001289, +0.03746] | gain (was undecided) |
| 2020 | (s2) against spread_mr_ctx | 251 | +8.9% [-3.5, +15.0] | +0.06546 [-0.006241, +0.1091] | undecided |
| 2020 | (s3) against B1 | 251 | +16.4% [+4.7, +26.9] | +0.127 [+0.04246, +0.3226] | gain |
| 2020 | (s3) against B1' | 251 | +13.6% [+0.9, +30.8] | +0.1016 [+0.002489, +0.4] | gain |
| 2020 | (s3) against B2 | 251 | +44.4% [+20.5, +65.3] | +0.5159 [+0.2164, +1.051] | gain |
| 2020 | (s3) against (a) | 251 | +1.8% [-7.7, +5.8] | +0.01196 [-0.03965, +0.0378] | undecided |
| 2020 | (s3) against (s1) | 251 | +5.5% [+0.8, +10.7] | +0.03767 [+0.01404, +0.07424] | gain |
| 2020 | (s3) against spread_mr_ctx | 251 | +12.2% [+0.4, +17.5] | +0.08978 [+0.04396, +0.1187] | gain |
| 2020 | (s4) against B1 | 251 | +7.1% [-8.8, +26.4] | +0.05489 [-0.05036, +0.2548] | undecided |
| 2020 | (s4) against B1' | 251 | +3.9% [-15.3, +32.9] | +0.0294 [-0.08841, +0.299] | undecided |
| 2020 | (s4) against B2 | 251 | +38.2% [+16.5, +60.4] | +0.4438 [+0.1399, +0.9628] | gain |
| 2020 | (s4) against (a) | 251 | -9.1% [-22.4, +1.3] | -0.06019 [-0.135, -0.005491] | loss (was undecided) |
| 2020 | (s4) against (s1) | 251 | -5.0% [-12.3, -0.1] | -0.03448 [-0.06884, -0.01231] | loss |
| 2020 | (s4) against spread_mr_ctx | 251 | +2.4% [-9.3, +9.8] | +0.01763 [-0.05985, +0.07692] | undecided |
| 2021-23 | (a) against B1 | 748 | +5.8% [+1.2, +9.8] | +0.05021 [+0.01348, +0.0933] | gain |
| 2021-23 | (a) against B1' | 748 | +0.2% [-5.2, +5.4] | +0.001758 [-0.03933, +0.04466] | undecided |
| 2021-23 | (a) against B2 | 748 | +43.7% [+30.4, +56.0] | +0.637 [+0.4124, +0.886] | gain |
| 2021-23 | (a) against spread_mr_ctx | 748 | +2.2% [-1.7, +7.2] | +0.01862 [-0.01489, +0.05614] | undecided |
| 2021-23 | (s1) against B1 | 748 | +10.0% [+4.6, +14.5] | +0.08664 [+0.03631, +0.147] | gain |
| 2021-23 | (s1) against B1' | 748 | +4.7% [-1.5, +10.4] | +0.03819 [-0.009877, +0.09686] | undecided |
| 2021-23 | (s1) against B2 | 748 | +46.2% [+34.3, +57.1] | +0.6735 [+0.456, +0.9169] | gain |
| 2021-23 | (s1) against (a) | 748 | +4.4% [+0.7, +7.8] | +0.03643 [+0.002356, +0.07306] | gain |
| 2021-23 | (s1) against spread_mr_ctx | 748 | +6.6% [+2.0, +10.6] | +0.05505 [+0.0155, +0.09281] | gain |
| 2021-23 | (s2) against B1 | 748 | +11.0% [+5.6, +15.5] | +0.09533 [+0.04518, +0.1564] | gain |
| 2021-23 | (s2) against B1' | 748 | +5.7% [-0.5, +11.5] | +0.04688 [-0.002056, +0.1068] | undecided |
| 2021-23 | (s2) against B2 | 748 | +46.8% [+34.7, +57.8] | +0.6822 [+0.4614, +0.9289] | gain |
| 2021-23 | (s2) against (a) | 748 | +5.5% [+1.8, +9.0] | +0.04513 [+0.01018, +0.08329] | gain |
| 2021-23 | (s2) against (s1) | 748 | +1.1% [+0.0, +3.3] | +0.008694 [+0.0006172, +0.02505] | gain |
| 2021-23 | (s2) against spread_mr_ctx | 748 | +7.6% [+2.6, +12.2] | +0.06375 [+0.02138, +0.1048] | gain |
| 2021-23 | (s3) against B1 | 748 | +10.7% [+5.9, +14.8] | +0.09263 [+0.04892, +0.1476] | gain |
| 2021-23 | (s3) against B1' | 748 | +5.4% [-0.2, +10.6] | +0.04417 [+0.0009768, +0.09719] | gain (was undecided) |
| 2021-23 | (s3) against B2 | 748 | +46.7% [+34.3, +57.8] | +0.6794 [+0.4595, +0.9231] | gain |
| 2021-23 | (s3) against (a) | 748 | +5.2% [+3.2, +7.2] | +0.04242 [+0.02133, +0.06744] | gain |
| 2021-23 | (s3) against (s1) | 748 | +0.8% [-1.0, +2.9] | +0.005984 [-0.008198, +0.02044] | undecided |
| 2021-23 | (s3) against spread_mr_ctx | 748 | +7.3% [+3.3, +11.5] | +0.06104 [+0.02869, +0.09473] | gain |
| 2021-23 | (s4) against B1 | 748 | +7.7% [+1.3, +12.9] | +0.0673 [+0.01242, +0.1284] | gain |
| 2021-23 | (s4) against B1' | 748 | +2.3% [-4.9, +8.7] | +0.01885 [-0.03417, +0.07854] | undecided |
| 2021-23 | (s4) against B2 | 748 | +44.9% [+33.1, +55.6] | +0.6541 [+0.4384, +0.8911] | gain |
| 2021-23 | (s4) against (a) | 748 | +2.1% [-3.0, +6.1] | +0.01709 [-0.02274, +0.05556] | undecided |
| 2021-23 | (s4) against (s1) | 748 | -2.5% [-7.9, -0.7] | -0.01934 [-0.06265, -0.006134] | loss |
| 2021-23 | (s4) against spread_mr_ctx | 748 | +4.3% [-1.0, +8.5] | +0.03571 [-0.007786, +0.074] | undecided |
| 2024 | (a) against B1 | 250 | +25.8% [+18.3, +38.5] | +0.8972 [+0.4745, +2.138] | gain |
| 2024 | (a) against B1' | 250 | +20.9% [+11.5, +37.9] | +0.6789 [+0.2638, +1.928] | gain |
| 2024 | (a) against B2 | 250 | +14.7% [+0.0, +30.4] | +0.445 [-0.007935, +1.118] | undecided (was gain) |
| 2024 | (a) against spread_mr_ctx | 250 | +2.8% [-3.2, +10.3] | +0.07342 [-0.06899, +0.3443] | undecided |
| 2024 | (s1) against B1 | 250 | +27.7% [+19.3, +38.6] | +0.9635 [+0.4948, +2.047] | gain |
| 2024 | (s1) against B1' | 250 | +22.9% [+12.8, +34.2] | +0.7452 [+0.2932, +1.71] | gain |
| 2024 | (s1) against B2 | 250 | +16.9% [-0.9, +29.8] | +0.5112 [-0.004728, +1.103] | undecided |
| 2024 | (s1) against (a) | 250 | +2.6% [-5.5, +8.8] | +0.06624 [-0.1104, +0.2313] | undecided |
| 2024 | (s1) against spread_mr_ctx | 250 | +5.3% [-3.2, +13.7] | +0.1397 [-0.07334, +0.4416] | undecided |
| 2024 | (s2) against B1 | 250 | +27.7% [+19.3, +38.6] | +0.963 [+0.4946, +2.045] | gain |
| 2024 | (s2) against B1' | 250 | +22.9% [+12.8, +34.2] | +0.7447 [+0.2931, +1.708] | gain |
| 2024 | (s2) against B2 | 250 | +16.9% [-0.9, +29.8] | +0.5107 [-0.005447, +1.103] | undecided |
| 2024 | (s2) against (a) | 250 | +2.6% [-5.5, +8.8] | +0.06574 [-0.1119, +0.2311] | undecided |
| 2024 | (s2) against (s1) | 250 | -0.0% [-0.1, -0.0] | -0.000505 [-0.002165, -0.0001008] | loss |
| 2024 | (s2) against spread_mr_ctx | 250 | +5.3% [-3.3, +13.6] | +0.1392 [-0.07403, +0.4404] | undecided |
| 2024 | (s3) against B1 | 250 | +29.5% [+22.7, +39.2] | +1.024 [+0.5756, +2.15] | gain |
| 2024 | (s3) against B1' | 250 | +24.8% [+16.4, +36.2] | +0.806 [+0.3739, +1.852] | gain |
| 2024 | (s3) against B2 | 250 | +18.9% [+2.3, +32.7] | +0.572 [+0.06684, +1.21] | gain |
| 2024 | (s3) against (a) | 250 | +4.9% [-0.2, +8.5] | +0.127 [+0.01826, +0.232] | gain (was undecided) |
| 2024 | (s3) against (s1) | 250 | +2.4% [-0.7, +5.6] | +0.06077 [-0.008637, +0.1404] | undecided |
| 2024 | (s3) against spread_mr_ctx | 250 | +7.6% [+1.7, +13.7] | +0.2004 [+0.02644, +0.4788] | gain |
| 2024 | (s4) against B1 | 250 | +27.8% [+19.5, +38.4] | +0.9667 [+0.4999, +2.035] | gain |
| 2024 | (s4) against B1' | 250 | +23.0% [+13.0, +34.0] | +0.7484 [+0.2993, +1.693] | gain |
| 2024 | (s4) against B2 | 250 | +17.0% [-0.8, +30.1] | +0.5145 [-0.005008, +1.114] | undecided |
| 2024 | (s4) against (a) | 250 | +2.7% [-5.6, +8.9] | +0.06949 [-0.1113, +0.235] | undecided |
| 2024 | (s4) against (s1) | 250 | +0.1% [-0.4, +0.8] | +0.003253 [-0.01129, +0.01966] | undecided |
| 2024 | (s4) against spread_mr_ctx | 250 | +5.4% [-3.1, +13.6] | +0.1429 [-0.06736, +0.4366] | undecided |
| 2025-26 | (a) against B1 | 244 | +18.7% [+8.6, +26.6] | +0.4745 [+0.2276, +0.7341] | gain |
| 2025-26 | (a) against B1' | 244 | +10.1% [-0.4, +17.8] | +0.2316 [+0.008497, +0.4319] | gain (was undecided) |
| 2025-26 | (a) against B2 | 244 | +23.7% [-3.4, +49.9] | +0.6404 [-0.04721, +1.78] | undecided |
| 2025-26 | (a) against spread_mr_ctx | 244 | +3.8% [-0.4, +7.7] | +0.08133 [-0.007161, +0.1893] | undecided |
| 2025-26 | (s1) against B1 | 244 | +25.9% [+12.8, +35.3] | +0.6549 [+0.3608, +0.9584] | gain |
| 2025-26 | (s1) against B1' | 244 | +18.0% [+4.1, +28.0] | +0.412 [+0.1287, +0.6682] | gain |
| 2025-26 | (s1) against B2 | 244 | +30.4% [+4.3, +52.8] | +0.8208 [+0.1346, +1.912] | gain |
| 2025-26 | (s1) against (a) | 244 | +8.8% [+1.2, +15.3] | +0.1804 [+0.04402, +0.3144] | gain |
| 2025-26 | (s1) against spread_mr_ctx | 244 | +12.2% [+3.6, +19.1] | +0.2618 [+0.09202, +0.4338] | gain |
| 2025-26 | (s2) against B1 | 244 | +25.0% [+12.4, +34.2] | +0.6339 [+0.3542, +0.9268] | gain |
| 2025-26 | (s2) against B1' | 244 | +17.1% [+3.7, +26.9] | +0.3909 [+0.1193, +0.6427] | gain |
| 2025-26 | (s2) against B2 | 244 | +29.6% [+3.9, +51.3] | +0.7997 [+0.1282, +1.854] | gain |
| 2025-26 | (s2) against (a) | 244 | +7.7% [+0.3, +14.4] | +0.1594 [+0.02469, +0.2923] | gain |
| 2025-26 | (s2) against (s1) | 244 | -1.1% [-4.0, +0.0] | -0.02106 [-0.07563, +7.519e-05] | undecided |
| 2025-26 | (s2) against spread_mr_ctx | 244 | +11.2% [+2.7, +18.1] | +0.2407 [+0.07342, +0.4121] | gain |
| 2025-26 | (s3) against B1 | 244 | +26.6% [+14.5, +35.7] | +0.6744 [+0.3956, +0.9746] | gain |
| 2025-26 | (s3) against B1' | 244 | +18.8% [+6.2, +28.4] | +0.4315 [+0.1721, +0.6792] | gain |
| 2025-26 | (s3) against B2 | 244 | +31.1% [+5.5, +53.7] | +0.8403 [+0.1589, +1.964] | gain |
| 2025-26 | (s3) against (a) | 244 | +9.7% [+3.6, +15.2] | +0.1999 [+0.09771, +0.3087] | gain |
| 2025-26 | (s3) against (s1) | 244 | +1.0% [-1.1, +3.1] | +0.01952 [-0.02029, +0.06142] | undecided |
| 2025-26 | (s3) against spread_mr_ctx | 244 | +13.1% [+6.1, +18.6] | +0.2813 [+0.1421, +0.4256] | gain |
| 2025-26 | (s4) against B1 | 244 | +25.7% [+12.5, +35.3] | +0.6512 [+0.3564, +0.9569] | gain |
| 2025-26 | (s4) against B1' | 244 | +17.8% [+3.7, +28.0] | +0.4083 [+0.1212, +0.6686] | gain |
| 2025-26 | (s4) against B2 | 244 | +30.3% [+4.0, +52.4] | +0.8171 [+0.1297, +1.896] | gain |
| 2025-26 | (s4) against (a) | 244 | +8.6% [+0.8, +15.4] | +0.1767 [+0.03625, +0.3149] | gain |
| 2025-26 | (s4) against (s1) | 244 | -0.2% [-0.8, +0.2] | -0.003679 [-0.01746, +0.003815] | undecided |
| 2025-26 | (s4) against spread_mr_ctx | 244 | +12.1% [+3.3, +19.1] | +0.2581 [+0.08699, +0.4308] | gain |
| all decision days | (a) against B1 | 1611 | +23.0% [+15.8, +41.2] | +0.4066 [+0.2338, +1.004] | gain |
| all decision days | (a) against B1' | 1611 | +10.1% [+5.0, +16.6] | +0.1533 [+0.06646, +0.2983] | gain |
| all decision days | (a) against B2 | 1611 | +28.3% [+19.4, +37.1] | +0.5392 [+0.3621, +0.7491] | gain |
| all decision days | (a) against spread_mr_ctx | 1611 | +2.5% [-0.0, +5.3] | +0.035 [+0.000913, +0.08038] | gain (was undecided) |
| all decision days | (s1) against B1 | 1611 | +25.1% [+18.4, +41.1] | +0.4439 [+0.2702, +0.9985] | gain |
| all decision days | (s1) against B1' | 1611 | +12.6% [+6.6, +18.9] | +0.1906 [+0.08975, +0.3356] | gain |
| all decision days | (s1) against B2 | 1611 | +30.3% [+20.9, +38.8] | +0.5764 [+0.3936, +0.7839] | gain |
| all decision days | (s1) against (a) | 1611 | +2.7% [-0.7, +5.8] | +0.03728 [-0.006736, +0.07997] | undecided |
| all decision days | (s1) against spread_mr_ctx | 1611 | +5.2% [+1.1, +9.1] | +0.07228 [+0.0165, +0.1336] | gain |
| all decision days | (s2) against B1 | 1611 | +25.2% [+18.6, +41.3] | +0.4463 [+0.2742, +1.005] | gain |
| all decision days | (s2) against B1' | 1611 | +12.7% [+6.8, +19.0] | +0.193 [+0.09353, +0.3363] | gain |
| all decision days | (s2) against B2 | 1611 | +30.4% [+21.0, +38.9] | +0.5789 [+0.3966, +0.7849] | gain |
| all decision days | (s2) against (a) | 1611 | +2.9% [-0.5, +6.0] | +0.0397 [-0.004041, +0.08196] | undecided |
| all decision days | (s2) against (s1) | 1611 | +0.2% [-0.3, +0.7] | +0.002419 [-0.004651, +0.009105] | undecided |
| all decision days | (s2) against spread_mr_ctx | 1611 | +5.3% [+1.2, +9.2] | +0.0747 [+0.01889, +0.1356] | gain |
| all decision days | (s3) against B1 | 1611 | +27.0% [+20.6, +42.9] | +0.4774 [+0.3023, +1.049] | gain |
| all decision days | (s3) against B1' | 1611 | +14.8% [+9.4, +20.5] | +0.2241 [+0.1279, +0.3686] | gain |
| all decision days | (s3) against B2 | 1611 | +32.1% [+23.0, +40.5] | +0.61 [+0.4321, +0.8197] | gain |
| all decision days | (s3) against (a) | 1611 | +5.2% [+2.8, +7.4] | +0.0708 [+0.04105, +0.1019] | gain |
| all decision days | (s3) against (s1) | 1611 | +2.5% [+1.2, +3.9] | +0.03352 [+0.01653, +0.05276] | gain |
| all decision days | (s3) against spread_mr_ctx | 1611 | +7.6% [+4.5, +10.6] | +0.1058 [+0.06112, +0.159] | gain |
| all decision days | (s4) against B1 | 1611 | +23.9% [+16.8, +40.4] | +0.4224 [+0.2463, +0.9788] | gain |
| all decision days | (s4) against B1' | 1611 | +11.1% [+4.9, +17.9] | +0.1691 [+0.06472, +0.3151] | gain |
| all decision days | (s4) against B2 | 1611 | +29.2% [+19.7, +37.7] | +0.555 [+0.3713, +0.7642] | gain |
| all decision days | (s4) against (a) | 1611 | +1.2% [-2.7, +4.5] | +0.01579 [-0.03485, +0.06272] | undecided |
| all decision days | (s4) against (s1) | 1611 | -1.6% [-3.2, -0.7] | -0.02149 [-0.0413, -0.009733] | loss |
| all decision days | (s4) against spread_mr_ctx | 1611 | +3.6% [-0.9, +7.7] | +0.05079 [-0.01111, +0.1139] | undecided |

### grid_crps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| calendar_days | (a) against B1 | 1352 | +23.3% [+17.2, +37.7] | +0.5815 [+0.3078, +1.625] | gain |
| calendar_days | (a) against B1' | 1352 | +9.8% [+4.9, +15.1] | +0.208 [+0.1106, +0.3575] | gain |
| calendar_days | (a) against B2 | 1352 | +32.5% [+19.2, +42.9] | +0.921 [+0.63, +1.309] | gain |
| calendar_days | (a) against spread_mr_ctx | 1352 | +3.6% [+0.8, +6.4] | +0.0709 [+0.02386, +0.1253] | gain |
| calendar_days | (s1) against B1 | 1352 | +21.7% [+13.2, +33.7] | +0.5404 [+0.2376, +1.316] | gain |
| calendar_days | (s1) against B1' | 1352 | +7.9% [-0.5, +14.8] | +0.1668 [+0.001242, +0.3373] | gain (was undecided) |
| calendar_days | (s1) against B2 | 1352 | +31.1% [+18.1, +41.4] | +0.8799 [+0.5797, +1.243] | gain |
| calendar_days | (s1) against (a) | 1352 | -2.2% [-9.9, +2.9] | -0.04115 [-0.1831, +0.05678] | undecided |
| calendar_days | (s1) against spread_mr_ctx | 1352 | +1.5% [-5.9, +6.8] | +0.02976 [-0.1108, +0.1372] | undecided |
| calendar_days | (s2) against B1 | 1352 | +21.9% [+12.9, +33.4] | +0.5456 [+0.2435, +1.286] | gain |
| calendar_days | (s2) against B1' | 1352 | +8.1% [-1.1, +15.2] | +0.1721 [-0.009449, +0.3432] | undecided |
| calendar_days | (s2) against B2 | 1352 | +31.3% [+17.5, +41.7] | +0.8852 [+0.5728, +1.243] | gain |
| calendar_days | (s2) against (a) | 1352 | -1.9% [-11.6, +3.6] | -0.03587 [-0.2181, +0.07074] | undecided |
| calendar_days | (s2) against (s1) | 1352 | +0.3% [-1.9, +1.9] | +0.005272 [-0.03877, +0.03554] | undecided |
| calendar_days | (s2) against spread_mr_ctx | 1352 | +1.8% [-7.6, +7.6] | +0.03503 [-0.1427, +0.1538] | undecided |
| calendar_days | (s3) against B1 | 1352 | +27.1% [+21.2, +37.6] | +0.6745 [+0.3874, +1.634] | gain |
| calendar_days | (s3) against B1' | 1352 | +14.2% [+7.6, +19.8] | +0.301 [+0.1822, +0.4636] | gain |
| calendar_days | (s3) against B2 | 1352 | +35.8% [+21.7, +45.8] | +1.014 [+0.7256, +1.389] | gain |
| calendar_days | (s3) against (a) | 1352 | +4.9% [+1.6, +7.6] | +0.09305 [+0.03685, +0.1446] | gain |
| calendar_days | (s3) against (s1) | 1352 | +6.9% [+3.3, +12.5] | +0.1342 [+0.0709, +0.2525] | gain |
| calendar_days | (s3) against spread_mr_ctx | 1352 | +8.3% [+3.8, +12.0] | +0.1639 [+0.1005, +0.2359] | gain |
| calendar_days | (s4) against B1 | 1352 | +19.5% [+10.3, +33.0] | +0.4869 [+0.1823, +1.259] | gain |
| calendar_days | (s4) against B1' | 1352 | +5.4% [-3.0, +12.4] | +0.1133 [-0.05654, +0.2842] | undecided |
| calendar_days | (s4) against B2 | 1352 | +29.2% [+16.8, +39.5] | +0.8264 [+0.5201, +1.186] | gain |
| calendar_days | (s4) against (a) | 1352 | -5.0% [-13.4, +0.7] | -0.09461 [-0.2413, +0.01094] | undecided |
| calendar_days | (s4) against (s1) | 1352 | -2.7% [-5.6, -0.8] | -0.05347 [-0.1067, -0.0231] | loss |
| calendar_days | (s4) against spread_mr_ctx | 1352 | -1.2% [-9.3, +4.4] | -0.02371 [-0.1744, +0.09041] | undecided |

### upper_tail_twcrps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| calendar_days | (a) against B1 | 1352 | +31.2% [+24.0, +45.4] | +0.4861 [+0.2145, +1.671] | gain |
| calendar_days | (a) against B1' | 1352 | +13.6% [+2.9, +22.5] | +0.1691 [+0.08447, +0.3296] | gain |
| calendar_days | (a) against B2 | 1352 | +21.8% [+5.0, +36.6] | +0.2986 [+0.1547, +0.5125] | gain |
| calendar_days | (a) against spread_mr_ctx | 1352 | +3.1% [-0.8, +7.5] | +0.03476 [-0.000647, +0.08215] | undecided |
| calendar_days | (s1) against B1 | 1352 | +28.7% [+19.1, +43.2] | +0.448 [+0.1566, +1.442] | gain |
| calendar_days | (s1) against B1' | 1352 | +10.6% [-1.1, +21.0] | +0.1311 [+0.002824, +0.304] | gain (was undecided) |
| calendar_days | (s1) against B2 | 1352 | +19.0% [+2.4, +33.1] | +0.2606 [+0.09443, +0.4844] | gain |
| calendar_days | (s1) against (a) | 1352 | -3.6% [-13.9, +2.9] | -0.03807 [-0.132, +0.03374] | undecided |
| calendar_days | (s1) against spread_mr_ctx | 1352 | -0.3% [-10.2, +6.8] | -0.003316 [-0.1019, +0.08436] | undecided |
| calendar_days | (s2) against B1 | 1352 | +28.3% [+18.1, +42.4] | +0.4405 [+0.1506, +1.389] | gain |
| calendar_days | (s2) against B1' | 1352 | +9.9% [-2.5, +20.5] | +0.1235 [-0.01024, +0.2886] | undecided |
| calendar_days | (s2) against B2 | 1352 | +18.5% [+1.5, +32.2] | +0.253 [+0.08241, +0.4653] | gain |
| calendar_days | (s2) against (a) | 1352 | -4.3% [-16.8, +2.8] | -0.04563 [-0.163, +0.03055] | undecided |
| calendar_days | (s2) against (s1) | 1352 | -0.7% [-3.7, +1.4] | -0.007555 [-0.04481, +0.01681] | undecided |
| calendar_days | (s2) against spread_mr_ctx | 1352 | -1.0% [-12.9, +6.6] | -0.01087 [-0.1303, +0.08073] | undecided |
| calendar_days | (s3) against B1 | 1352 | +34.2% [+27.2, +45.5] | +0.5325 [+0.2469, +1.676] | gain |
| calendar_days | (s3) against B1' | 1352 | +17.4% [+3.9, +27.2] | +0.2155 [+0.1107, +0.4001] | gain |
| calendar_days | (s3) against B2 | 1352 | +25.2% [+5.4, +40.3] | +0.345 [+0.1866, +0.5789] | gain |
| calendar_days | (s3) against (a) | 1352 | +4.3% [+0.5, +8.1] | +0.04638 [+0.008818, +0.09127] | gain |
| calendar_days | (s3) against (s1) | 1352 | +7.6% [+1.7, +16.5] | +0.08445 [+0.03599, +0.1706] | gain |
| calendar_days | (s3) against spread_mr_ctx | 1352 | +7.3% [+0.4, +13.5] | +0.08113 [+0.02822, +0.1531] | gain |
| calendar_days | (s4) against B1 | 1352 | +26.8% [+15.9, +43.3] | +0.4174 [+0.1189, +1.42] | gain |
| calendar_days | (s4) against B1' | 1352 | +8.1% [-3.2, +18.4] | +0.1005 [-0.033, +0.276] | undecided |
| calendar_days | (s4) against B2 | 1352 | +16.8% [+1.6, +30.0] | +0.23 [+0.05758, +0.4468] | gain |
| calendar_days | (s4) against (a) | 1352 | -6.4% [-19.4, +1.9] | -0.06869 [-0.1732, +0.009984] | undecided |
| calendar_days | (s4) against (s1) | 1352 | -2.8% [-7.5, +0.3] | -0.03062 [-0.07335, -0.007107] | loss (was undecided) |
| calendar_days | (s4) against spread_mr_ctx | 1352 | -3.1% [-14.9, +4.9] | -0.03393 [-0.1431, +0.0584] | undecided |

### grid_crps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| dom_19_23 | (a) against B1 | 305 | +36.4% [+6.0, +139.6] | +0.7708 [+0.0483, +7.573] | gain |
| dom_19_23 | (a) against B1' | 305 | -1.4% [-19.4, +24.3] | -0.01811 [-0.2156, +0.3031] | undecided |
| dom_19_23 | (a) against B2 | 305 | +30.5% [+4.4, +49.8] | +0.591 [+0.1053, +1.179] | gain |
| dom_19_23 | (a) against spread_mr_ctx | 305 | -1.8% [-6.5, +2.4] | -0.0236 [-0.08931, +0.03332] | undecided |
| dom_19_23 | (s1) against B1 | 305 | +40.9% [+12.6, +120.8] | +0.8657 [+0.1425, +7.042] | gain |
| dom_19_23 | (s1) against B1' | 305 | +5.8% [-15.0, +34.3] | +0.07669 [-0.1534, +0.4843] | undecided |
| dom_19_23 | (s1) against B2 | 305 | +35.4% [+6.0, +55.2] | +0.6858 [+0.1699, +1.314] | gain |
| dom_19_23 | (s1) against (a) | 305 | +7.0% [-8.6, +20.3] | +0.09481 [-0.09589, +0.2879] | undecided |
| dom_19_23 | (s1) against spread_mr_ctx | 305 | +5.4% [-14.7, +20.4] | +0.0712 [-0.1652, +0.2833] | undecided |
| dom_19_23 | (s2) against B1 | 305 | +40.0% [+10.7, +120.7] | +0.8465 [+0.1193, +6.92] | gain |
| dom_19_23 | (s2) against B1' | 305 | +4.3% [-16.2, +33.0] | +0.05751 [-0.173, +0.4574] | undecided |
| dom_19_23 | (s2) against B2 | 305 | +34.4% [+5.3, +54.5] | +0.6667 [+0.1535, +1.291] | gain |
| dom_19_23 | (s2) against (a) | 305 | +5.6% [-10.6, +19.4] | +0.07562 [-0.1223, +0.2733] | undecided |
| dom_19_23 | (s2) against (s1) | 305 | -1.5% [-4.1, +0.2] | -0.01919 [-0.05255, +0.00139] | undecided |
| dom_19_23 | (s2) against spread_mr_ctx | 305 | +3.9% [-16.8, +19.3] | +0.05202 [-0.1952, +0.2654] | undecided |
| dom_19_23 | (s3) against B1 | 305 | +45.3% [+19.8, +139.7] | +0.9586 [+0.2251, +8.553] | gain |
| dom_19_23 | (s3) against B1' | 305 | +12.8% [-3.5, +35.7] | +0.1697 [-0.0221, +0.5753] | undecided |
| dom_19_23 | (s3) against B2 | 305 | +40.2% [+15.2, +57.2] | +0.7788 [+0.3004, +1.385] | gain |
| dom_19_23 | (s3) against (a) | 305 | +14.0% [+6.2, +21.8] | +0.1878 [+0.0782, +0.3292] | gain |
| dom_19_23 | (s3) against (s1) | 305 | +7.4% [+1.1, +14.6] | +0.09296 [+0.01151, +0.2195] | gain |
| dom_19_23 | (s3) against spread_mr_ctx | 305 | +12.4% [+1.4, +22.3] | +0.1642 [+0.02991, +0.3226] | gain |
| dom_19_23 | (s4) against B1 | 305 | +39.2% [+7.9, +116.3] | +0.8291 [+0.09437, +6.339] | gain |
| dom_19_23 | (s4) against B1' | 305 | +3.0% [-19.9, +32.8] | +0.04011 [-0.2123, +0.4344] | undecided |
| dom_19_23 | (s4) against B2 | 305 | +33.5% [+2.2, +55.0] | +0.6493 [+0.112, +1.299] | gain |
| dom_19_23 | (s4) against (a) | 305 | +4.3% [-16.8, +19.0] | +0.05823 [-0.1954, +0.264] | undecided |
| dom_19_23 | (s4) against (s1) | 305 | -2.9% [-16.6, +0.5] | -0.03658 [-0.2226, +0.005226] | undecided |
| dom_19_23 | (s4) against spread_mr_ctx | 305 | +2.6% [-23.5, +19.3] | +0.03463 [-0.2719, +0.2644] | undecided |

### upper_tail_twcrps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| dom_19_23 | (a) against B1 | 305 | +60.0% [+29.9, +126.0] | +0.784 [+0.07995, +10.3] | gain |
| dom_19_23 | (a) against B1' | 305 | +9.0% [-34.5, +52.1] | +0.05201 [-0.1108, +0.3082] | undecided |
| dom_19_23 | (a) against B2 | 305 | -12.7% [-84.1, +31.2] | -0.05903 [-0.3437, +0.1154] | undecided |
| dom_19_23 | (a) against spread_mr_ctx | 305 | -7.4% [-13.1, -3.0] | -0.03607 [-0.07211, -0.01326] | loss |
| dom_19_23 | (s1) against B1 | 305 | +69.6% [+51.0, +99.9] | +0.91 [+0.1741, +8.463] | gain |
| dom_19_23 | (s1) against B1' | 305 | +31.0% [-14.6, +63.0] | +0.1781 [+0.02081, +0.508] | gain (was undecided) |
| dom_19_23 | (s1) against B2 | 305 | +14.4% [-59.0, +49.4] | +0.06705 [-0.1456, +0.2391] | undecided |
| dom_19_23 | (s1) against (a) | 305 | +24.1% [+8.8, +36.3] | +0.1261 [+0.04947, +0.2885] | gain |
| dom_19_23 | (s1) against spread_mr_ctx | 305 | +18.5% [+0.2, +33.1] | +0.09 [+0.0189, +0.2353] | gain |
| dom_19_23 | (s2) against B1 | 305 | +68.1% [+45.0, +103.2] | +0.89 [+0.151, +9.491] | gain |
| dom_19_23 | (s2) against B1' | 305 | +27.5% [-15.7, +61.9] | +0.158 [+0.005245, +0.4923] | gain (was undecided) |
| dom_19_23 | (s2) against B2 | 305 | +10.1% [-58.6, +47.0] | +0.04701 [-0.1635, +0.2178] | undecided |
| dom_19_23 | (s2) against (a) | 305 | +20.3% [+7.0, +32.8] | +0.106 [+0.03798, +0.2554] | gain |
| dom_19_23 | (s2) against (s1) | 305 | -5.0% [-39.7, +1.0] | -0.02004 [-0.2301, +0.0008759] | undecided |
| dom_19_23 | (s2) against spread_mr_ctx | 305 | +14.4% [-1.2, +30.8] | +0.06996 [+0.007482, +0.2137] | gain (was undecided) |
| dom_19_23 | (s3) against B1 | 305 | +68.5% [+48.3, +108.4] | +0.8959 [+0.1619, +8.854] | gain |
| dom_19_23 | (s3) against B1' | 305 | +28.5% [-14.9, +60.1] | +0.164 [+0.01109, +0.4822] | gain (was undecided) |
| dom_19_23 | (s3) against B2 | 305 | +11.4% [-60.5, +46.5] | +0.05295 [-0.1567, +0.2194] | undecided |
| dom_19_23 | (s3) against (a) | 305 | +21.4% [+10.2, +30.5] | +0.112 [+0.04678, +0.2611] | gain |
| dom_19_23 | (s3) against (s1) | 305 | -3.6% [-9.0, +1.6] | -0.0141 [-0.03468, +0.002078] | undecided |
| dom_19_23 | (s3) against spread_mr_ctx | 305 | +15.6% [+1.4, +27.2] | +0.0759 [+0.01768, +0.2101] | gain |
| dom_19_23 | (s4) against B1 | 305 | +69.5% [+48.4, +103.6] | +0.9082 [+0.1627, +8.921] | gain |
| dom_19_23 | (s4) against B1' | 305 | +30.7% [-9.5, +64.8] | +0.1762 [+0.02654, +0.5316] | gain (was undecided) |
| dom_19_23 | (s4) against B2 | 305 | +14.1% [-48.8, +49.7] | +0.06521 [-0.1234, +0.2416] | undecided |
| dom_19_23 | (s4) against (a) | 305 | +23.8% [+12.2, +33.8] | +0.1242 [+0.04755, +0.278] | gain |
| dom_19_23 | (s4) against (s1) | 305 | -0.5% [-9.0, +8.1] | -0.001834 [-0.02202, +0.0208] | undecided |
| dom_19_23 | (s4) against spread_mr_ctx | 305 | +18.1% [+2.6, +30.1] | +0.08817 [+0.01802, +0.2232] | gain |

### grid_crps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| fomc_day | (a) against B1 | 118 | +4.0% [-1.3, +9.8] | +0.1822 [+0.03153, +0.3955] | gain (was undecided) |
| fomc_day | (a) against B1' | 118 | +2.9% [+0.9, +4.9] | +0.1323 [-0.00972, +0.4011] | undecided (was gain) |
| fomc_day | (a) against B2 | 118 | +20.0% [-14.9, +40.9] | +1.098 [+0.4607, +1.865] | gain (was undecided) |
| fomc_day | (a) against spread_mr_ctx | 118 | +1.7% [-4.4, +5.7] | +0.07454 [-0.07701, +0.1875] | undecided |
| fomc_day | (s1) against B1 | 118 | -4.0% [-16.3, +4.0] | -0.1815 [-0.713, +0.1369] | undecided |
| fomc_day | (s1) against B1' | 118 | -5.1% [-22.0, +5.7] | -0.2315 [-0.7722, +0.04894] | undecided |
| fomc_day | (s1) against B2 | 118 | +13.4% [-7.6, +29.3] | +0.734 [+0.1877, +1.346] | gain (was undecided) |
| fomc_day | (s1) against (a) | 118 | -8.3% [-32.2, +3.4] | -0.3638 [-1.159, -0.03975] | loss (was undecided) |
| fomc_day | (s1) against spread_mr_ctx | 118 | -6.5% [-25.7, +1.7] | -0.2893 [-1.248, +0.06122] | undecided |
| fomc_day | (s2) against B1 | 118 | -3.3% [-20.2, +3.9] | -0.1508 [-1.009, +0.1721] | undecided |
| fomc_day | (s2) against B1' | 118 | -4.4% [-29.2, +5.0] | -0.2007 [-1.113, +0.104] | undecided |
| fomc_day | (s2) against B2 | 118 | +13.9% [-12.7, +31.8] | +0.7648 [+0.02703, +1.459] | gain (was undecided) |
| fomc_day | (s2) against (a) | 118 | -7.6% [-48.3, +2.4] | -0.333 [-2.339, +0.02309] | undecided |
| fomc_day | (s2) against (s1) | 118 | +0.6% [-2.7, +3.7] | +0.03079 [-0.1575, +0.1827] | undecided |
| fomc_day | (s2) against spread_mr_ctx | 118 | -5.8% [-35.9, +2.3] | -0.2585 [-2.353, +0.1401] | undecided |
| fomc_day | (s3) against B1 | 118 | +2.5% [-2.1, +6.3] | +0.1159 [-0.03858, +0.2929] | undecided |
| fomc_day | (s3) against B1' | 118 | +1.5% [-1.6, +3.6] | +0.06594 [-0.05987, +0.238] | undecided |
| fomc_day | (s3) against B2 | 118 | +18.8% [-13.4, +39.5] | +1.031 [+0.4786, +1.737] | gain (was undecided) |
| fomc_day | (s3) against (a) | 118 | -1.5% [-5.9, +0.7] | -0.06631 [-0.3161, +0.04199] | undecided |
| fomc_day | (s3) against (s1) | 118 | +6.2% [-3.1, +26.7] | +0.2975 [+0.08091, +0.9771] | gain (was undecided) |
| fomc_day | (s3) against spread_mr_ctx | 118 | +0.2% [-7.7, +3.7] | +0.008224 [-0.3537, +0.1762] | undecided |
| fomc_day | (s4) against B1 | 118 | -20.8% [-54.5, +7.3] | -0.9514 [-2.318, -0.05602] | loss (was undecided) |
| fomc_day | (s4) against B1' | 118 | -22.1% [-58.6, +11.3] | -1.001 [-2.3, -0.1778] | loss (was undecided) |
| fomc_day | (s4) against B2 | 118 | -0.7% [-12.8, +7.7] | -0.03582 [-0.7293, +0.5156] | undecided |
| fomc_day | (s4) against (a) | 118 | -25.8% [-63.8, +11.2] | -1.134 [-2.532, -0.2169] | loss (was undecided) |
| fomc_day | (s4) against (s1) | 118 | -16.2% [-38.0, +2.8] | -0.7698 [-2.019, -0.169] | loss (was undecided) |
| fomc_day | (s4) against spread_mr_ctx | 118 | -23.7% [-56.5, +8.7] | -1.059 [-2.47, -0.1282] | loss (was undecided) |

### upper_tail_twcrps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| fomc_day | (a) against B1 | 118 | +2.3% [-0.3, +4.4] | +0.0818 [+0.01057, +0.3473] | gain (was undecided) |
| fomc_day | (a) against B1' | 118 | +2.8% [+1.3, +4.7] | +0.1021 [+0.0008302, +0.7815] | gain |
| fomc_day | (a) against B2 | 118 | +11.5% [-14.1, +24.7] | +0.4614 [+0.07462, +1.291] | gain (was undecided) |
| fomc_day | (a) against spread_mr_ctx | 118 | +1.0% [-6.8, +4.3] | +0.03742 [-0.07456, +0.1199] | undecided |
| fomc_day | (s1) against B1 | 118 | -5.9% [-23.7, +6.4] | -0.2129 [-0.5819, -0.03087] | loss (was undecided) |
| fomc_day | (s1) against B1' | 118 | -5.3% [-25.4, +8.1] | -0.1926 [-0.5789, -0.003396] | loss (was undecided) |
| fomc_day | (s1) against B2 | 118 | +4.2% [-1.4, +8.4] | +0.1667 [-0.1553, +0.6148] | undecided |
| fomc_day | (s1) against (a) | 118 | -8.3% [-36.5, +7.5] | -0.2947 [-0.846, -0.06908] | loss (was undecided) |
| fomc_day | (s1) against spread_mr_ctx | 118 | -7.2% [-28.6, +4.8] | -0.2573 [-0.902, -0.02427] | loss (was undecided) |
| fomc_day | (s2) against B1 | 118 | -5.8% [-33.2, +7.1] | -0.2096 [-1.056, +0.01132] | undecided |
| fomc_day | (s2) against B1' | 118 | -5.2% [-37.7, +9.1] | -0.1893 [-1.006, +0.04059] | undecided |
| fomc_day | (s2) against B2 | 118 | +4.2% [-7.2, +9.6] | +0.17 [-0.2745, +0.6182] | undecided |
| fomc_day | (s2) against (a) | 118 | -8.2% [-60.1, +7.4] | -0.2914 [-2.032, -0.03042] | loss (was undecided) |
| fomc_day | (s2) against (s1) | 118 | +0.1% [-3.6, +3.1] | +0.003289 [-0.1571, +0.1212] | undecided |
| fomc_day | (s2) against spread_mr_ctx | 118 | -7.1% [-48.5, +4.3] | -0.254 [-2.06, +0.02633] | undecided |
| fomc_day | (s3) against B1 | 118 | +0.6% [-1.6, +2.6] | +0.0219 [-0.03553, +0.1304] | undecided |
| fomc_day | (s3) against B1' | 118 | +1.2% [-1.0, +3.9] | +0.04217 [-0.0354, +0.3158] | undecided |
| fomc_day | (s3) against B2 | 118 | +10.0% [-6.3, +20.6] | +0.4015 [+0.07109, +1.142] | gain (was undecided) |
| fomc_day | (s3) against (a) | 118 | -1.7% [-5.1, +1.7] | -0.0599 [-0.2308, -0.008443] | loss (was undecided) |
| fomc_day | (s3) against (s1) | 118 | +6.1% [-10.5, +34.7] | +0.2348 [+0.06115, +0.7831] | gain (was undecided) |
| fomc_day | (s3) against spread_mr_ctx | 118 | -0.6% [-5.5, +1.7] | -0.02248 [-0.2106, +0.07297] | undecided |
| fomc_day | (s4) against B1 | 118 | -19.5% [-54.6, +8.6] | -0.7085 [-2.001, -0.1445] | loss (was undecided) |
| fomc_day | (s4) against B1' | 118 | -18.9% [-54.4, +10.9] | -0.6882 [-1.795, -0.1527] | loss (was undecided) |
| fomc_day | (s4) against B2 | 118 | -8.2% [-29.0, +5.3] | -0.329 [-1.01, +0.04946] | undecided |
| fomc_day | (s4) against (a) | 118 | -22.3% [-60.9, +13.1] | -0.7903 [-2.13, -0.1589] | loss (was undecided) |
| fomc_day | (s4) against (s1) | 118 | -12.9% [-36.8, +4.5] | -0.4956 [-2.345, -0.05419] | loss (was undecided) |
| fomc_day | (s4) against spread_mr_ctx | 118 | -21.0% [-52.9, +11.7] | -0.7529 [-2.062, -0.1232] | loss (was undecided) |

### grid_crps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| iorb_window | (a) against B1 | 78 | +52.7% [+16.6, +219.7] | +2.688 [-0.08449, +67.75] | undecided (was gain) |
| iorb_window | (a) against B1' | 78 | -22.4% [-96.3, -4.0] | -0.4415 [-2.222, -0.05564] | loss |
| iorb_window | (a) against B2 | 78 | +33.8% [-19.7, +55.6] | +1.23 [+0.1603, +2.871] | gain (was undecided) |
| iorb_window | (a) against spread_mr_ctx | 78 | +1.2% [-7.7, +7.4] | +0.0286 [-0.1687, +0.188] | undecided |
| iorb_window | (s1) against B1 | 78 | +54.4% [+30.2, +122.9] | +2.774 [+0.1598, +31.74] | gain |
| iorb_window | (s1) against B1' | 78 | -18.0% [-122.5, +18.0] | -0.355 [-2.082, +0.2636] | undecided |
| iorb_window | (s1) against B2 | 78 | +36.2% [-31.3, +68.6] | +1.317 [+0.02845, +3.647] | gain (was undecided) |
| iorb_window | (s1) against (a) | 78 | +3.6% [-18.9, +27.2] | +0.08656 [-0.2789, +0.6516] | undecided |
| iorb_window | (s1) against spread_mr_ctx | 78 | +4.7% [-19.1, +28.9] | +0.1152 [-0.2814, +0.7086] | undecided |
| iorb_window | (s2) against B1 | 78 | +54.2% [+29.1, +134.5] | +2.761 [+0.1343, +34.88] | gain |
| iorb_window | (s2) against B1' | 78 | -18.7% [-136.3, +13.3] | -0.3683 [-2.355, +0.2005] | undecided |
| iorb_window | (s2) against B2 | 78 | +35.8% [-32.9, +65.2] | +1.304 [+0.03107, +3.416] | gain (was undecided) |
| iorb_window | (s2) against (a) | 78 | +3.0% [-18.8, +19.4] | +0.0732 [-0.2623, +0.4395] | undecided |
| iorb_window | (s2) against (s1) | 78 | -0.6% [-5.0, +3.2] | -0.01336 [-0.1313, +0.06815] | undecided |
| iorb_window | (s2) against spread_mr_ctx | 78 | +4.2% [-19.3, +22.1] | +0.1018 [-0.2957, +0.5324] | undecided |
| iorb_window | (s3) against B1 | 78 | +56.3% [+31.1, +137.6] | +2.87 [+0.1664, +35.73] | gain |
| iorb_window | (s3) against B1' | 78 | -13.2% [-115.6, +15.5] | -0.2593 [-1.774, +0.2443] | undecided |
| iorb_window | (s3) against B2 | 78 | +38.8% [-23.0, +66.3] | +1.413 [+0.1981, +3.626] | gain (was undecided) |
| iorb_window | (s3) against (a) | 78 | +7.6% [-9.3, +26.4] | +0.1822 [-0.06444, +0.7208] | undecided |
| iorb_window | (s3) against (s1) | 78 | +4.1% [-1.1, +10.0] | +0.09569 [-0.03723, +0.3013] | undecided |
| iorb_window | (s3) against spread_mr_ctx | 78 | +8.6% [-8.3, +27.4] | +0.2109 [-0.05329, +0.7358] | undecided |
| iorb_window | (s4) against B1 | 78 | +54.9% [+29.1, +136.7] | +2.796 [+0.131, +35.33] | gain |
| iorb_window | (s4) against B1' | 78 | -16.9% [-99.4, +15.7] | -0.3329 [-1.807, +0.2309] | undecided |
| iorb_window | (s4) against B2 | 78 | +36.8% [-19.7, +68.1] | +1.339 [+0.1357, +3.714] | gain (was undecided) |
| iorb_window | (s4) against (a) | 78 | +4.5% [-12.2, +23.2] | +0.1086 [-0.1896, +0.6277] | undecided |
| iorb_window | (s4) against (s1) | 78 | +0.9% [-3.9, +7.6] | +0.02205 [-0.06626, +0.18] | undecided |
| iorb_window | (s4) against spread_mr_ctx | 78 | +5.6% [-15.8, +24.0] | +0.1372 [-0.2324, +0.6416] | undecided |
| month_end | (a) against B1 | 180 | +12.3% [+7.7, +16.2] | +0.3723 [+0.1484, +0.7033] | gain |
| month_end | (a) against B1' | 180 | +7.9% [+4.0, +11.7] | +0.229 [+0.06815, +0.4641] | gain |
| month_end | (a) against B2 | 180 | +28.1% [+4.5, +50.1] | +1.039 [+0.3332, +2.175] | gain |
| month_end | (a) against spread_mr_ctx | 180 | +6.6% [-5.4, +20.6] | +0.1874 [-0.1336, +0.5568] | undecided |
| month_end | (s1) against B1 | 180 | +15.3% [-27.1, +32.6] | +0.4647 [-0.5521, +1.302] | undecided |
| month_end | (s1) against B1' | 180 | +11.1% [-31.1, +28.2] | +0.3214 [-0.5878, +1.048] | undecided |
| month_end | (s1) against B2 | 180 | +30.6% [+17.8, +46.1] | +1.132 [+0.6182, +2.109] | gain |
| month_end | (s1) against (a) | 180 | +3.5% [-42.6, +22.0] | +0.09233 [-0.823, +0.6876] | undecided |
| month_end | (s1) against spread_mr_ctx | 180 | +9.8% [-15.3, +22.4] | +0.2797 [-0.2859, +0.7206] | undecided |
| month_end | (s2) against B1 | 180 | +14.9% [-26.1, +30.9] | +0.4511 [-0.484, +1.203] | undecided |
| month_end | (s2) against B1' | 180 | +10.6% [-31.0, +26.6] | +0.3078 [-0.5354, +0.9476] | undecided |
| month_end | (s2) against B2 | 180 | +30.2% [+15.6, +44.8] | +1.118 [+0.6204, +1.952] | gain |
| month_end | (s2) against (a) | 180 | +3.0% [-42.8, +20.4] | +0.07873 [-0.7768, +0.6111] | undecided |
| month_end | (s2) against (s1) | 180 | -0.5% [-7.8, +6.2] | -0.01361 [-0.218, +0.15] | undecided |
| month_end | (s2) against spread_mr_ctx | 180 | +9.3% [-18.8, +22.5] | +0.2661 [-0.3391, +0.6928] | undecided |
| month_end | (s3) against B1 | 180 | +22.8% [+7.5, +34.2] | +0.6913 [+0.08669, +1.456] | gain |
| month_end | (s3) against B1' | 180 | +19.0% [+5.3, +29.0] | +0.548 [+0.04239, +1.189] | gain |
| month_end | (s3) against B2 | 180 | +36.7% [+18.3, +53.7] | +1.358 [+0.7542, +2.626] | gain |
| month_end | (s3) against (a) | 180 | +12.0% [-1.7, +22.0] | +0.319 [-0.09236, +0.7656] | undecided |
| month_end | (s3) against (s1) | 180 | +8.8% [-6.1, +31.7] | +0.2267 [-0.08487, +0.9195] | undecided |
| month_end | (s3) against spread_mr_ctx | 180 | +17.8% [+6.0, +27.5] | +0.5064 [+0.2203, +0.9129] | gain |
| month_end | (s4) against B1 | 180 | +14.1% [-26.4, +31.3] | +0.4277 [-0.5587, +1.229] | undecided |
| month_end | (s4) against B1' | 180 | +9.8% [-30.1, +26.6] | +0.2844 [-0.587, +0.9666] | undecided |
| month_end | (s4) against B2 | 180 | +29.6% [+15.1, +45.9] | +1.095 [+0.5833, +2.045] | gain |
| month_end | (s4) against (a) | 180 | +2.1% [-40.9, +20.8] | +0.05535 [-0.8169, +0.6312] | undecided |
| month_end | (s4) against (s1) | 180 | -1.4% [-12.5, +1.8] | -0.03698 [-0.3356, +0.04478] | undecided |
| month_end | (s4) against spread_mr_ctx | 180 | +8.5% [-16.8, +22.0] | +0.2427 [-0.3136, +0.6778] | undecided |

### upper_tail_twcrps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| month_end | (a) against B1 | 180 | +11.8% [+5.0, +17.5] | +0.2205 [+0.04646, +0.6758] | gain |
| month_end | (a) against B1' | 180 | +11.6% [+3.5, +17.0] | +0.2168 [+0.083, +0.5136] | gain |
| month_end | (a) against B2 | 180 | +24.9% [-10.9, +57.6] | +0.5462 [+0.05145, +1.878] | gain (was undecided) |
| month_end | (a) against spread_mr_ctx | 180 | +9.2% [-7.6, +25.5] | +0.1669 [-0.08039, +0.4048] | undecided |
| month_end | (s1) against B1 | 180 | +11.9% [-46.4, +31.4] | +0.223 [-0.4936, +0.9779] | undecided |
| month_end | (s1) against B1' | 180 | +11.8% [-39.3, +29.8] | +0.2193 [-0.412, +0.8817] | undecided |
| month_end | (s1) against B2 | 180 | +25.0% [+5.6, +49.2] | +0.5487 [+0.05006, +1.851] | gain |
| month_end | (s1) against (a) | 180 | +0.2% [-69.0, +21.8] | +0.002523 [-0.6617, +0.4837] | undecided |
| month_end | (s1) against spread_mr_ctx | 180 | +9.3% [-28.0, +24.5] | +0.1694 [-0.2939, +0.5671] | undecided |
| month_end | (s2) against B1 | 180 | +9.3% [-49.5, +28.4] | +0.1743 [-0.4812, +0.823] | undecided |
| month_end | (s2) against B1' | 180 | +9.2% [-45.7, +26.9] | +0.1705 [-0.4236, +0.7324] | undecided |
| month_end | (s2) against B2 | 180 | +22.8% [+4.4, +42.6] | +0.4999 [+0.04291, +1.545] | gain |
| month_end | (s2) against (a) | 180 | -2.8% [-73.0, +19.3] | -0.04624 [-0.7294, +0.383] | undecided |
| month_end | (s2) against (s1) | 180 | -3.0% [-12.8, +3.7] | -0.04876 [-0.277, +0.0576] | undecided |
| month_end | (s2) against spread_mr_ctx | 180 | +6.7% [-30.0, +22.3] | +0.1207 [-0.354, +0.4783] | undecided |
| month_end | (s3) against B1 | 180 | +22.8% [+7.3, +37.0] | +0.4257 [+0.0002633, +1.331] | gain |
| month_end | (s3) against B1' | 180 | +22.6% [+8.5, +35.3] | +0.422 [+0.0595, +1.222] | gain |
| month_end | (s3) against B2 | 180 | +34.3% [-1.8, +66.0] | +0.7514 [+0.1961, +2.628] | gain (was undecided) |
| month_end | (s3) against (a) | 180 | +12.5% [-0.7, +23.4] | +0.2052 [-0.07038, +0.6673] | undecided |
| month_end | (s3) against (s1) | 180 | +12.3% [-15.1, +47.1] | +0.2027 [-0.06633, +0.828] | undecided |
| month_end | (s3) against spread_mr_ctx | 180 | +20.5% [-0.4, +35.8] | +0.3721 [+0.1283, +0.8113] | gain (was undecided) |
| month_end | (s4) against B1 | 180 | +9.4% [-45.7, +29.2] | +0.1754 [-0.4998, +0.8653] | undecided |
| month_end | (s4) against B1' | 180 | +9.2% [-39.6, +27.4] | +0.1716 [-0.4255, +0.7564] | undecided |
| month_end | (s4) against B2 | 180 | +22.9% [+0.6, +47.8] | +0.501 [+0.01248, +1.701] | gain |
| month_end | (s4) against (a) | 180 | -2.7% [-66.6, +20.1] | -0.04514 [-0.6858, +0.4108] | undecided |
| month_end | (s4) against (s1) | 180 | -2.9% [-23.2, +1.9] | -0.04766 [-0.4305, +0.02988] | undecided |
| month_end | (s4) against spread_mr_ctx | 180 | +6.7% [-30.3, +23.4] | +0.1218 [-0.3239, +0.5015] | undecided |

### grid_crps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| ordinary | (a) against B1 | 507 | +35.0% [+26.1, +56.5] | +0.6181 [+0.3597, +1.481] | gain |
| ordinary | (a) against B1' | 507 | +20.3% [+12.7, +33.0] | +0.2935 [+0.1654, +0.5839] | gain |
| ordinary | (a) against B2 | 507 | +33.0% [+17.9, +47.7] | +0.5655 [+0.2729, +0.9799] | gain |
| ordinary | (a) against spread_mr_ctx | 507 | +0.3% [-4.5, +4.5] | +0.003806 [-0.05171, +0.05096] | undecided |
| ordinary | (s1) against B1 | 507 | +37.1% [+28.6, +56.8] | +0.6561 [+0.3905, +1.484] | gain |
| ordinary | (s1) against B1' | 507 | +23.0% [+15.4, +35.5] | +0.3314 [+0.1963, +0.6319] | gain |
| ordinary | (s1) against B2 | 507 | +35.2% [+20.9, +49.4] | +0.6035 [+0.312, +1.018] | gain |
| ordinary | (s1) against (a) | 507 | +3.3% [+1.8, +4.9] | +0.03799 [+0.01911, +0.06228] | gain |
| ordinary | (s1) against spread_mr_ctx | 507 | +3.6% [-0.5, +7.5] | +0.04179 [-0.002331, +0.08449] | undecided |
| ordinary | (s2) against B1 | 507 | +37.2% [+28.7, +56.8] | +0.6574 [+0.3917, +1.486] | gain |
| ordinary | (s2) against B1' | 507 | +23.0% [+15.5, +35.6] | +0.3328 [+0.1977, +0.6338] | gain |
| ordinary | (s2) against B2 | 507 | +35.3% [+20.9, +49.5] | +0.6049 [+0.3133, +1.02] | gain |
| ordinary | (s2) against (a) | 507 | +3.4% [+1.9, +5.0] | +0.03932 [+0.0201, +0.0639] | gain |
| ordinary | (s2) against (s1) | 507 | +0.1% [+0.0, +0.2] | +0.001333 [+0.0003492, +0.002377] | gain |
| ordinary | (s2) against spread_mr_ctx | 507 | +3.7% [-0.5, +7.6] | +0.04312 [-0.0008566, +0.08581] | undecided |
| ordinary | (s3) against B1 | 507 | +37.0% [+28.3, +57.9] | +0.6545 [+0.3875, +1.515] | gain |
| ordinary | (s3) against B1' | 507 | +22.8% [+15.5, +35.5] | +0.3299 [+0.197, +0.6309] | gain |
| ordinary | (s3) against B2 | 507 | +35.1% [+20.7, +49.2] | +0.602 [+0.3112, +1.016] | gain |
| ordinary | (s3) against (a) | 507 | +3.2% [+2.4, +4.0] | +0.03643 [+0.02321, +0.05369] | gain |
| ordinary | (s3) against (s1) | 507 | -0.1% [-1.1, +0.9] | -0.001554 [-0.01209, +0.009724] | undecided |
| ordinary | (s3) against spread_mr_ctx | 507 | +3.5% [-0.5, +7.3] | +0.04024 [-0.00306, +0.08241] | undecided |
| ordinary | (s4) against B1 | 507 | +36.8% [+28.3, +56.7] | +0.6507 [+0.3862, +1.475] | gain |
| ordinary | (s4) against B1' | 507 | +22.6% [+15.0, +35.2] | +0.326 [+0.1907, +0.6268] | gain |
| ordinary | (s4) against B2 | 507 | +34.9% [+20.5, +49.0] | +0.5981 [+0.3073, +1.008] | gain |
| ordinary | (s4) against (a) | 507 | +2.8% [+1.1, +4.6] | +0.03257 [+0.01141, +0.05718] | gain |
| ordinary | (s4) against (s1) | 507 | -0.5% [-1.4, +0.0] | -0.005416 [-0.01586, +0.000354] | undecided |
| ordinary | (s4) against spread_mr_ctx | 507 | +3.2% [-1.2, +7.0] | +0.03637 [-0.009909, +0.07862] | undecided |

### upper_tail_twcrps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| ordinary | (a) against B1 | 507 | +51.0% [+38.5, +71.0] | +0.4635 [+0.202, +1.516] | gain |
| ordinary | (a) against B1' | 507 | +28.0% [+8.5, +57.4] | +0.173 [+0.05533, +0.5188] | gain |
| ordinary | (a) against B2 | 507 | +14.5% [-5.4, +32.4] | +0.07544 [-0.01954, +0.2077] | undecided |
| ordinary | (a) against spread_mr_ctx | 507 | -11.9% [-18.6, -5.0] | -0.04711 [-0.08187, -0.02204] | loss |
| ordinary | (s1) against B1 | 507 | +57.1% [+46.2, +72.2] | +0.5187 [+0.2405, +1.572] | gain |
| ordinary | (s1) against B1' | 507 | +36.9% [+18.3, +65.5] | +0.2282 [+0.1025, +0.6135] | gain |
| ordinary | (s1) against B2 | 507 | +25.1% [+7.4, +43.1] | +0.1306 [+0.03244, +0.2873] | gain |
| ordinary | (s1) against (a) | 507 | +12.4% [+8.8, +15.8] | +0.05518 [+0.03214, +0.09299] | gain |
| ordinary | (s1) against spread_mr_ctx | 507 | +2.0% [-1.5, +5.7] | +0.008072 [-0.005148, +0.02696] | undecided |
| ordinary | (s2) against B1 | 507 | +57.3% [+46.4, +72.2] | +0.5207 [+0.2418, +1.576] | gain |
| ordinary | (s2) against B1' | 507 | +37.3% [+18.6, +65.8] | +0.2303 [+0.1042, +0.6179] | gain |
| ordinary | (s2) against B2 | 507 | +25.5% [+7.8, +43.5] | +0.1327 [+0.03413, +0.2899] | gain |
| ordinary | (s2) against (a) | 507 | +12.9% [+9.1, +16.4] | +0.05723 [+0.03333, +0.09628] | gain |
| ordinary | (s2) against (s1) | 507 | +0.5% [+0.3, +0.8] | +0.002047 [+0.001094, +0.003497] | gain |
| ordinary | (s2) against spread_mr_ctx | 507 | +2.5% [-0.9, +6.1] | +0.01012 [-0.003003, +0.02942] | undecided |
| ordinary | (s3) against B1 | 507 | +54.7% [+43.0, +71.8] | +0.497 [+0.2265, +1.554] | gain |
| ordinary | (s3) against B1' | 507 | +33.4% [+14.7, +62.4] | +0.2065 [+0.08488, +0.5731] | gain |
| ordinary | (s3) against B2 | 507 | +20.9% [+2.4, +38.7] | +0.1089 [+0.01302, +0.2531] | gain |
| ordinary | (s3) against (a) | 507 | +7.5% [+5.6, +9.4] | +0.03347 [+0.0198, +0.05499] | gain |
| ordinary | (s3) against (s1) | 507 | -5.6% [-7.8, -3.4] | -0.02171 [-0.03911, -0.01193] | loss |
| ordinary | (s3) against spread_mr_ctx | 507 | -3.4% [-8.4, +1.7] | -0.01364 [-0.03204, +0.00446] | undecided |
| ordinary | (s4) against B1 | 507 | +56.7% [+45.9, +72.4] | +0.5147 [+0.2387, +1.589] | gain |
| ordinary | (s4) against B1' | 507 | +36.3% [+18.4, +64.1] | +0.2242 [+0.1014, +0.6069] | gain |
| ordinary | (s4) against B2 | 507 | +24.4% [+6.8, +41.7] | +0.1266 [+0.02965, +0.2791] | gain |
| ordinary | (s4) against (a) | 507 | +11.5% [+8.2, +14.7] | +0.0512 [+0.02863, +0.08941] | gain |
| ordinary | (s4) against (s1) | 507 | -1.0% [-7.5, -0.0] | -0.00398 [-0.03201, -0.0001779] | loss |
| ordinary | (s4) against spread_mr_ctx | 507 | +1.0% [-3.2, +5.0] | +0.004092 [-0.01126, +0.02257] | undecided |

### grid_crps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| post_month_end_window | (a) against B1 | 267 | +21.3% [+14.7, +28.8] | +0.5563 [+0.2527, +1.141] | gain |
| post_month_end_window | (a) against B1' | 267 | +10.7% [+2.7, +20.2] | +0.2456 [+0.05109, +0.6884] | gain |
| post_month_end_window | (a) against B2 | 267 | +30.4% [+18.3, +42.9] | +0.895 [+0.3992, +1.571] | gain |
| post_month_end_window | (a) against spread_mr_ctx | 267 | +3.9% [-1.1, +10.7] | +0.08239 [-0.008558, +0.2925] | undecided |
| post_month_end_window | (s1) against B1 | 267 | +12.7% [-4.5, +25.4] | +0.3309 [-0.02467, +0.8641] | undecided |
| post_month_end_window | (s1) against B1' | 267 | +0.9% [-24.8, +17.5] | +0.02016 [-0.4191, +0.4158] | undecided |
| post_month_end_window | (s1) against B2 | 267 | +22.7% [+2.5, +36.6] | +0.6696 [+0.1058, +1.325] | gain |
| post_month_end_window | (s1) against (a) | 267 | -11.0% [-33.6, +1.9] | -0.2255 [-0.6846, +0.01926] | undecided |
| post_month_end_window | (s1) against spread_mr_ctx | 267 | -6.7% [-31.6, +9.3] | -0.1431 [-0.599, +0.1725] | undecided |
| post_month_end_window | (s2) against B1 | 267 | +11.5% [-9.5, +25.2] | +0.2995 [-0.09574, +0.8228] | undecided |
| post_month_end_window | (s2) against B1' | 267 | -0.5% [-29.9, +17.1] | -0.01119 [-0.5185, +0.3977] | undecided |
| post_month_end_window | (s2) against B2 | 267 | +21.7% [+0.0, +36.3] | +0.6382 [+0.05032, +1.295] | gain |
| post_month_end_window | (s2) against (a) | 267 | -12.5% [-40.1, +1.4] | -0.2568 [-0.8288, +0.01566] | undecided |
| post_month_end_window | (s2) against (s1) | 267 | -1.4% [-7.5, +0.6] | -0.03135 [-0.1951, +0.01565] | undecided |
| post_month_end_window | (s2) against spread_mr_ctx | 267 | -8.2% [-37.6, +8.8] | -0.1744 [-0.7241, +0.162] | undecided |
| post_month_end_window | (s3) against B1 | 267 | +21.6% [+12.7, +30.2] | +0.5626 [+0.2448, +1.267] | gain |
| post_month_end_window | (s3) against B1' | 267 | +11.0% [-4.6, +22.1] | +0.2519 [-0.02567, +0.6676] | undecided |
| post_month_end_window | (s3) against B2 | 267 | +30.6% [+15.2, +42.4] | +0.9013 [+0.3593, +1.6] | gain |
| post_month_end_window | (s3) against (a) | 267 | +0.3% [-9.9, +6.9] | +0.006241 [-0.1707, +0.1423] | undecided |
| post_month_end_window | (s3) against (s1) | 267 | +10.2% [+4.4, +21.6] | +0.2317 [+0.08716, +0.6445] | gain |
| post_month_end_window | (s3) against spread_mr_ctx | 267 | +4.2% [-8.6, +14.1] | +0.08863 [-0.1165, +0.3336] | undecided |
| post_month_end_window | (s4) against B1 | 267 | +12.3% [-4.3, +24.9] | +0.32 [-0.03166, +0.8518] | undecided |
| post_month_end_window | (s4) against B1' | 267 | +0.4% [-23.6, +17.1] | +0.009273 [-0.4063, +0.4016] | undecided |
| post_month_end_window | (s4) against B2 | 267 | +22.4% [+3.2, +36.1] | +0.6587 [+0.1114, +1.311] | gain |
| post_month_end_window | (s4) against (a) | 267 | -11.5% [-32.4, +1.2] | -0.2363 [-0.6594, +0.003246] | undecided |
| post_month_end_window | (s4) against (s1) | 267 | -0.5% [-2.1, +0.9] | -0.01089 [-0.04295, +0.0197] | undecided |
| post_month_end_window | (s4) against spread_mr_ctx | 267 | -7.2% [-30.4, +8.7] | -0.154 [-0.5791, +0.1564] | undecided |

### upper_tail_twcrps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| post_month_end_window | (a) against B1 | 267 | +28.4% [+19.9, +35.9] | +0.423 [+0.1447, +1.079] | gain |
| post_month_end_window | (a) against B1' | 267 | +13.4% [+0.8, +26.6] | +0.1654 [+0.00268, +0.6062] | gain |
| post_month_end_window | (a) against B2 | 267 | +25.2% [+15.1, +35.1] | +0.3585 [+0.08898, +0.9435] | gain |
| post_month_end_window | (a) against spread_mr_ctx | 267 | +5.3% [-3.6, +18.3] | +0.06004 [-0.01742, +0.3634] | undecided |
| post_month_end_window | (s1) against B1 | 267 | +11.0% [-15.9, +36.9] | +0.163 [-0.1233, +0.8495] | undecided |
| post_month_end_window | (s1) against B1' | 267 | -7.7% [-56.6, +29.8] | -0.09467 [-0.4737, +0.2673] | undecided |
| post_month_end_window | (s1) against B2 | 267 | +6.9% [-32.8, +29.4] | +0.09849 [-0.2751, +0.5696] | undecided |
| post_month_end_window | (s1) against (a) | 267 | -24.4% [-62.2, +5.8] | -0.26 [-0.696, -0.05783] | loss (was undecided) |
| post_month_end_window | (s1) against spread_mr_ctx | 267 | -17.8% [-64.3, +21.6] | -0.2 [-0.5862, +0.08577] | undecided |
| post_month_end_window | (s2) against B1 | 267 | +9.2% [-22.2, +36.8] | +0.1372 [-0.1702, +0.7776] | undecided |
| post_month_end_window | (s2) against B1' | 267 | -9.8% [-63.5, +29.9] | -0.1205 [-0.5515, +0.2496] | undecided |
| post_month_end_window | (s2) against B2 | 267 | +5.1% [-37.6, +29.0] | +0.07264 [-0.3183, +0.5368] | undecided |
| post_month_end_window | (s2) against (a) | 267 | -26.8% [-70.5, +5.7] | -0.2859 [-0.8201, -0.06278] | loss (was undecided) |
| post_month_end_window | (s2) against (s1) | 267 | -2.0% [-13.4, +0.8] | -0.02585 [-0.2049, +0.01229] | undecided |
| post_month_end_window | (s2) against spread_mr_ctx | 267 | -20.1% [-70.8, +21.5] | -0.2258 [-0.6797, +0.07384] | undecided |
| post_month_end_window | (s3) against B1 | 267 | +24.0% [+10.2, +37.9] | +0.3578 [+0.0665, +1.295] | gain |
| post_month_end_window | (s3) against B1' | 267 | +8.1% [-29.0, +30.5] | +0.1001 [-0.1474, +0.5072] | undecided |
| post_month_end_window | (s3) against B2 | 267 | +20.6% [-5.9, +34.4] | +0.2933 [-0.04738, +0.868] | undecided |
| post_month_end_window | (s3) against (a) | 267 | -6.1% [-28.8, +8.5] | -0.06525 [-0.2343, +0.04435] | undecided |
| post_month_end_window | (s3) against (s1) | 267 | +14.7% [+3.9, +28.1] | +0.1948 [+0.07417, +0.5554] | gain |
| post_month_end_window | (s3) against spread_mr_ctx | 267 | -0.5% [-30.5, +22.4] | -0.005211 [-0.1908, +0.2403] | undecided |
| post_month_end_window | (s4) against B1 | 267 | +10.5% [-14.9, +35.9] | +0.1567 [-0.1248, +0.8467] | undecided |
| post_month_end_window | (s4) against B1' | 267 | -8.2% [-53.0, +29.7] | -0.101 [-0.4453, +0.2631] | undecided |
| post_month_end_window | (s4) against B2 | 267 | +6.5% [-30.0, +28.9] | +0.09218 [-0.2644, +0.5693] | undecided |
| post_month_end_window | (s4) against (a) | 267 | -25.0% [-60.0, +5.3] | -0.2663 [-0.6436, -0.07258] | loss (was undecided) |
| post_month_end_window | (s4) against (s1) | 267 | -0.5% [-3.4, +1.7] | -0.006311 [-0.03905, +0.0243] | undecided |
| post_month_end_window | (s4) against spread_mr_ctx | 267 | -18.3% [-61.4, +21.1] | -0.2063 [-0.5547, +0.07359] | undecided |

### grid_crps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| quarter_end | (a) against B1 | 30 | +9.8% [+7.9, +11.5] | +0.6847 [+0.1578, +2.157] | gain |
| quarter_end | (a) against B1' | 30 | +8.4% [+5.9, +10.4] | +0.5759 [+0.1434, +1.687] | gain |
| quarter_end | (a) against B2 | 30 | +17.0% [-31.7, +53.6] | +1.289 [-1.006, +4.071] | undecided |
| quarter_end | (a) against spread_mr_ctx | 30 | +3.3% [-1.3, +9.6] | +0.2164 [-0.04341, +0.5723] | undecided |
| quarter_end | (s1) against B1 | 30 | +25.9% [-94.0, +51.6] | +1.8 [-1.529, +5.998] | undecided |
| quarter_end | (s1) against B1' | 30 | +24.7% [-100.0, +51.1] | +1.691 [-1.683, +5.713] | undecided |
| quarter_end | (s1) against B2 | 30 | +31.8% [+2.6, +42.9] | +2.404 [+1.459, +4.056] | gain |
| quarter_end | (s1) against (a) | 30 | +17.8% [-109.6, +46.0] | +1.115 [-2.13, +4.318] | undecided |
| quarter_end | (s1) against spread_mr_ctx | 30 | +20.5% [-90.1, +49.2] | +1.332 [-1.484, +4.631] | undecided |
| quarter_end | (s2) against B1 | 30 | +28.1% [-75.9, +50.9] | +1.955 [-1.008, +6.014] | undecided |
| quarter_end | (s2) against B1' | 30 | +27.0% [-81.5, +50.4] | +1.846 [-1.128, +5.706] | undecided |
| quarter_end | (s2) against B2 | 30 | +33.8% [+7.3, +45.0] | +2.559 [+1.73, +4.155] | gain |
| quarter_end | (s2) against (a) | 30 | +20.3% [-88.9, +45.6] | +1.27 [-1.487, +4.309] | undecided |
| quarter_end | (s2) against (s1) | 30 | +3.0% [-2.1, +18.2] | +0.1546 [-0.09544, +0.9379] | undecided |
| quarter_end | (s2) against spread_mr_ctx | 30 | +22.9% [-75.6, +47.1] | +1.486 [-0.9009, +4.527] | undecided |
| quarter_end | (s3) against B1 | 30 | +26.4% [+0.2, +41.2] | +1.839 [-0.05085, +5.46] | undecided (was gain) |
| quarter_end | (s3) against B1' | 30 | +25.3% [-2.7, +40.9] | +1.73 [-0.1275, +5.173] | undecided |
| quarter_end | (s3) against B2 | 30 | +32.3% [+0.7, +48.5] | +2.443 [+1.388, +4.633] | gain |
| quarter_end | (s3) against (a) | 30 | +18.4% [-8.5, +34.7] | +1.154 [-0.3386, +3.605] | undecided |
| quarter_end | (s3) against (s1) | 30 | +0.7% [-35.8, +86.1] | +0.03859 [-1.196, +2.467] | undecided |
| quarter_end | (s3) against spread_mr_ctx | 30 | +21.1% [+0.5, +38.8] | +1.37 [+0.05958, +4.138] | gain |
| quarter_end | (s4) against B1 | 30 | +26.3% [-93.4, +51.9] | +1.828 [-1.487, +6.081] | undecided |
| quarter_end | (s4) against B1' | 30 | +25.1% [-99.4, +51.4] | +1.719 [-1.628, +5.8] | undecided |
| quarter_end | (s4) against B2 | 30 | +32.2% [+3.5, +43.1] | +2.432 [+1.48, +4.142] | gain |
| quarter_end | (s4) against (a) | 30 | +18.2% [-109.0, +46.3] | +1.143 [-2.057, +4.376] | undecided |
| quarter_end | (s4) against (s1) | 30 | +0.5% [+0.1, +0.9] | +0.02753 [-0.001569, +0.1047] | undecided (was gain) |
| quarter_end | (s4) against spread_mr_ctx | 30 | +21.0% [-89.8, +49.5] | +1.359 [-1.438, +4.707] | undecided |

### upper_tail_twcrps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| quarter_end | (a) against B1 | 30 | +10.9% [+7.7, +13.2] | +0.5856 [+0.03993, +4.756] | gain |
| quarter_end | (a) against B1' | 30 | +9.8% [+4.7, +12.5] | +0.5194 [+0.04902, +3.556] | gain |
| quarter_end | (a) against spread_mr_ctx | 30 | +4.3% [-6.6, +9.5] | +0.2161 [+0.05458, +0.3827] | gain (was undecided) |
| quarter_end | (s1) against B1 | 30 | +25.0% [-91.5, +45.2] | +1.346 [-0.847, +5.469] | undecided |
| quarter_end | (s1) against B1' | 30 | +24.1% [-95.4, +44.6] | +1.28 [-0.8801, +5.212] | undecided |
| quarter_end | (s1) against (a) | 30 | +15.9% [-114.1, +38.7] | +0.7602 [-1.181, +3.47] | undecided |
| quarter_end | (s1) against spread_mr_ctx | 30 | +19.5% [-120.1, +42.2] | +0.9763 [-0.9062, +3.724] | undecided |
| quarter_end | (s2) against B1 | 30 | +26.3% [-85.4, +44.4] | +1.413 [-0.6097, +5.437] | undecided |
| quarter_end | (s2) against B1' | 30 | +25.4% [-90.0, +43.8] | +1.347 [-0.6402, +5.183] | undecided |
| quarter_end | (s2) against (a) | 30 | +17.3% [-103.8, +37.8] | +0.8272 [-0.8849, +3.444] | undecided |
| quarter_end | (s2) against (s1) | 30 | +1.7% [-3.5, +11.5] | +0.06705 [-0.1004, +0.4862] | undecided |
| quarter_end | (s2) against spread_mr_ctx | 30 | +20.8% [-121.2, +40.4] | +1.043 [-0.6321, +3.683] | undecided |
| quarter_end | (s3) against B1 | 30 | +28.2% [+10.6, +40.7] | +1.516 [+0.05395, +7.139] | gain |
| quarter_end | (s3) against B1' | 30 | +27.3% [+8.6, +40.4] | +1.45 [+0.05666, +6.653] | gain |
| quarter_end | (s3) against (a) | 30 | +19.4% [+1.2, +31.2] | +0.9301 [-0.02054, +3.766] | undecided (was gain) |
| quarter_end | (s3) against (s1) | 30 | +4.2% [-55.9, +101.8] | +0.1699 [-0.7664, +2.216] | undecided |
| quarter_end | (s3) against spread_mr_ctx | 30 | +22.9% [-4.7, +37.4] | +1.146 [+0.1349, +4.306] | gain (was undecided) |
| quarter_end | (s4) against B1 | 30 | +25.4% [-92.7, +45.5] | +1.366 [-0.8284, +5.564] | undecided |
| quarter_end | (s4) against B1' | 30 | +24.5% [-96.8, +44.9] | +1.3 [-0.8567, +5.297] | undecided |
| quarter_end | (s4) against (a) | 30 | +16.3% [-114.8, +38.9] | +0.7808 [-1.143, +3.53] | undecided |
| quarter_end | (s4) against (s1) | 30 | +0.5% [-0.1, +1.5] | +0.0206 [-0.002023, +0.1998] | undecided |
| quarter_end | (s4) against spread_mr_ctx | 30 | +19.9% [-123.2, +42.6] | +0.9969 [-0.8769, +3.803] | undecided |

### grid_crps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| settlement | (a) against B1 | 946 | +20.4% [+16.3, +26.9] | +0.5371 [+0.3015, +1.285] | gain |
| settlement | (a) against B1' | 946 | +10.3% [+5.1, +15.8] | +0.2401 [+0.1337, +0.4279] | gain |
| settlement | (a) against B2 | 946 | +32.3% [+16.3, +44.2] | +0.9976 [+0.6482, +1.462] | gain |
| settlement | (a) against spread_mr_ctx | 946 | +3.8% [+0.4, +7.3] | +0.08274 [+0.02267, +0.1519] | gain |
| settlement | (s1) against B1 | 946 | +21.4% [+13.1, +28.5] | +0.5631 [+0.2659, +1.149] | gain |
| settlement | (s1) against B1' | 946 | +11.4% [+1.6, +19.9] | +0.266 [+0.06745, +0.505] | gain |
| settlement | (s1) against B2 | 946 | +33.1% [+16.8, +44.2] | +1.024 [+0.6841, +1.47] | gain |
| settlement | (s1) against (a) | 946 | +1.2% [-6.3, +6.2] | +0.02598 [-0.1257, +0.1346] | undecided |
| settlement | (s1) against spread_mr_ctx | 946 | +5.0% [-2.4, +10.8] | +0.1087 [-0.02821, +0.237] | undecided |
| settlement | (s2) against B1 | 946 | +21.9% [+13.7, +28.6] | +0.575 [+0.2859, +1.148] | gain |
| settlement | (s2) against B1' | 946 | +11.9% [+2.0, +20.3] | +0.278 [+0.08528, +0.5076] | gain |
| settlement | (s2) against B2 | 946 | +33.5% [+16.6, +44.6] | +1.036 [+0.699, +1.471] | gain |
| settlement | (s2) against (a) | 946 | +1.8% [-6.0, +6.8] | +0.03795 [-0.1208, +0.1448] | undecided |
| settlement | (s2) against (s1) | 946 | +0.6% [-1.2, +2.4] | +0.01196 [-0.02684, +0.04739] | undecided |
| settlement | (s2) against spread_mr_ctx | 946 | +5.5% [-2.3, +11.7] | +0.1207 [-0.02399, +0.2495] | undecided |
| settlement | (s3) against B1 | 946 | +25.0% [+19.9, +30.4] | +0.6584 [+0.3881, +1.331] | gain |
| settlement | (s3) against B1' | 946 | +15.5% [+6.7, +22.5] | +0.3614 [+0.207, +0.5907] | gain |
| settlement | (s3) against B2 | 946 | +36.2% [+18.7, +47.4] | +1.119 [+0.7725, +1.583] | gain |
| settlement | (s3) against (a) | 946 | +5.8% [+1.2, +9.2] | +0.1213 [+0.04889, +0.1893] | gain |
| settlement | (s3) against (s1) | 946 | +4.6% [+1.3, +9.3] | +0.09531 [+0.03443, +0.1945] | gain |
| settlement | (s3) against spread_mr_ctx | 946 | +9.4% [+2.8, +14.3] | +0.204 [+0.1244, +0.3047] | gain |
| settlement | (s4) against B1 | 946 | +19.9% [+11.6, +27.5] | +0.5238 [+0.2325, +1.116] | gain |
| settlement | (s4) against B1' | 946 | +9.7% [+0.6, +18.0] | +0.2268 [+0.03173, +0.4579] | gain |
| settlement | (s4) against B2 | 946 | +31.9% [+16.4, +43.0] | +0.9843 [+0.6437, +1.424] | gain |
| settlement | (s4) against (a) | 946 | -0.6% [-8.3, +4.3] | -0.01329 [-0.1629, +0.09608] | undecided |
| settlement | (s4) against (s1) | 946 | -1.9% [-4.1, -0.4] | -0.03928 [-0.08281, -0.0153] | loss |
| settlement | (s4) against spread_mr_ctx | 946 | +3.2% [-3.9, +8.8] | +0.06945 [-0.07074, +0.1963] | undecided |

### upper_tail_twcrps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| settlement | (a) against B1 | 946 | +25.4% [+21.1, +31.4] | +0.4277 [+0.1951, +1.35] | gain |
| settlement | (a) against B1' | 946 | +12.9% [+1.8, +22.2] | +0.1862 [+0.08993, +0.4055] | gain |
| settlement | (a) against B2 | 946 | +22.2% [+3.5, +37.6] | +0.3586 [+0.1816, +0.6293] | gain |
| settlement | (a) against spread_mr_ctx | 946 | +3.4% [-1.5, +8.7] | +0.0446 [-0.002769, +0.1103] | undecided |
| settlement | (s1) against B1 | 946 | +25.2% [+16.4, +33.8] | +0.4258 [+0.1505, +1.174] | gain |
| settlement | (s1) against B1' | 946 | +12.7% [-1.4, +26.0] | +0.1843 [+0.02916, +0.4499] | gain (was undecided) |
| settlement | (s1) against B2 | 946 | +22.0% [+0.3, +37.6] | +0.3567 [+0.1579, +0.6571] | gain |
| settlement | (s1) against (a) | 946 | -0.2% [-9.3, +6.1] | -0.001933 [-0.1097, +0.08753] | undecided |
| settlement | (s1) against spread_mr_ctx | 946 | +3.3% [-7.2, +11.6] | +0.04267 [-0.06879, +0.1669] | undecided |
| settlement | (s2) against B1 | 946 | +24.9% [+16.2, +33.2] | +0.4201 [+0.1499, +1.167] | gain |
| settlement | (s2) against B1' | 946 | +12.4% [-1.8, +25.6] | +0.1786 [+0.02895, +0.4296] | gain (was undecided) |
| settlement | (s2) against B2 | 946 | +21.7% [-0.1, +36.8] | +0.351 [+0.1596, +0.6299] | gain (was undecided) |
| settlement | (s2) against (a) | 946 | -0.6% [-10.2, +5.7] | -0.007636 [-0.1211, +0.07971] | undecided |
| settlement | (s2) against (s1) | 946 | -0.5% [-2.8, +1.5] | -0.005703 [-0.04039, +0.02179] | undecided |
| settlement | (s2) against spread_mr_ctx | 946 | +2.8% [-7.7, +11.2] | +0.03697 [-0.07877, +0.1574] | undecided |
| settlement | (s3) against B1 | 946 | +29.2% [+23.1, +35.3] | +0.4926 [+0.2346, +1.356] | gain |
| settlement | (s3) against B1' | 946 | +17.4% [+1.4, +29.1] | +0.2511 [+0.1226, +0.5325] | gain |
| settlement | (s3) against B2 | 946 | +26.2% [+3.0, +42.2] | +0.4234 [+0.2243, +0.7235] | gain |
| settlement | (s3) against (a) | 946 | +5.1% [-0.1, +9.9] | +0.06485 [+0.01872, +0.1277] | gain (was undecided) |
| settlement | (s3) against (s1) | 946 | +5.3% [-0.1, +13.1] | +0.06678 [+0.01319, +0.1539] | gain (was undecided) |
| settlement | (s3) against spread_mr_ctx | 946 | +8.4% [-1.4, +16.7] | +0.1095 [+0.04211, +0.2265] | gain (was undecided) |
| settlement | (s4) against B1 | 946 | +23.8% [+14.8, +33.1] | +0.401 [+0.1275, +1.173] | gain |
| settlement | (s4) against B1' | 946 | +11.0% [-1.5, +23.8] | +0.1595 [+0.003697, +0.4184] | gain (was undecided) |
| settlement | (s4) against B2 | 946 | +20.5% [+1.4, +35.9] | +0.3318 [+0.1327, +0.625] | gain |
| settlement | (s4) against (a) | 946 | -2.1% [-12.2, +4.4] | -0.02676 [-0.1339, +0.06285] | undecided |
| settlement | (s4) against (s1) | 946 | -2.0% [-5.8, +0.3] | -0.02482 [-0.06608, -0.00457] | loss (was undecided) |
| settlement | (s4) against spread_mr_ctx | 946 | +1.4% [-8.9, +9.3] | +0.01784 [-0.09638, +0.1395] | undecided |

### grid_crps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| tax_date | (a) against B1 | 89 | +6.8% [-5.8, +13.6] | +0.3754 [+0.04441, +1.088] | gain (was undecided) |
| tax_date | (a) against B1' | 89 | +5.5% [+1.8, +8.9] | +0.299 [+0.006346, +1.217] | gain |
| tax_date | (a) against B2 | 89 | +33.8% [-60.1, +59.1] | +2.617 [+1.368, +4.855] | gain (was undecided) |
| tax_date | (a) against spread_mr_ctx | 89 | +4.6% [-5.2, +15.1] | +0.2475 [+0.06285, +0.5576] | gain (was undecided) |
| tax_date | (s1) against B1 | 89 | -3.3% [-23.8, +8.6] | -0.1804 [-0.978, +0.4674] | undecided |
| tax_date | (s1) against B1' | 89 | -4.7% [-32.5, +9.7] | -0.2568 [-0.9992, +0.3247] | undecided |
| tax_date | (s1) against B2 | 89 | +26.6% [-43.3, +44.5] | +2.061 [+1.104, +3.718] | gain (was undecided) |
| tax_date | (s1) against (a) | 89 | -10.9% [-43.1, +5.1] | -0.5558 [-1.637, -0.095] | loss (was undecided) |
| tax_date | (s1) against spread_mr_ctx | 89 | -5.7% [-19.1, +2.3] | -0.3083 [-0.802, -0.01938] | loss (was undecided) |
| tax_date | (s2) against B1 | 89 | +2.4% [-3.0, +6.5] | +0.1298 [-0.1787, +0.5215] | undecided |
| tax_date | (s2) against B1' | 89 | +1.0% [-4.6, +5.0] | +0.05338 [-0.2019, +0.4098] | undecided |
| tax_date | (s2) against B2 | 89 | +30.6% [-56.7, +54.8] | +2.371 [+1.247, +4.062] | gain (was undecided) |
| tax_date | (s2) against (a) | 89 | -4.8% [-10.8, -0.3] | -0.2456 [-0.6663, -0.08888] | loss |
| tax_date | (s2) against (s1) | 89 | +5.5% [-7.0, +44.8] | +0.3102 [-0.02027, +2.089] | undecided |
| tax_date | (s2) against spread_mr_ctx | 89 | +0.0% [-4.3, +3.3] | +0.001857 [-0.2519, +0.1636] | undecided |
| tax_date | (s3) against B1 | 89 | +6.1% [-1.0, +11.0] | +0.337 [-0.01868, +0.9696] | undecided |
| tax_date | (s3) against B1' | 89 | +4.8% [+2.2, +7.1] | +0.2606 [-0.04544, +0.9945] | undecided (was gain) |
| tax_date | (s3) against B2 | 89 | +33.3% [-52.0, +58.3] | +2.579 [+1.351, +4.949] | gain (was undecided) |
| tax_date | (s3) against (a) | 89 | -0.8% [-3.5, +1.3] | -0.03843 [-0.1611, +0.0365] | undecided |
| tax_date | (s3) against (s1) | 89 | +9.1% [-7.9, +35.7] | +0.5174 [+0.04628, +1.945] | gain (was undecided) |
| tax_date | (s3) against spread_mr_ctx | 89 | +3.9% [-3.7, +13.8] | +0.2091 [+0.003758, +0.5733] | gain (was undecided) |
| tax_date | (s4) against B1 | 89 | -5.3% [-32.9, +10.9] | -0.2886 [-1.041, +0.2944] | undecided |
| tax_date | (s4) against B1' | 89 | -6.7% [-38.1, +13.1] | -0.365 [-1.061, +0.1836] | undecided |
| tax_date | (s4) against B2 | 89 | +25.2% [-17.6, +42.1] | +1.953 [+1.056, +3.76] | gain (was undecided) |
| tax_date | (s4) against (a) | 89 | -13.0% [-45.8, +9.1] | -0.664 [-1.676, -0.1864] | loss (was undecided) |
| tax_date | (s4) against (s1) | 89 | -1.9% [-14.9, +4.0] | -0.1082 [-0.6463, +0.1055] | undecided |
| tax_date | (s4) against spread_mr_ctx | 89 | -7.8% [-27.7, +5.6] | -0.4165 [-1.229, -0.09337] | loss (was undecided) |

### upper_tail_twcrps, by target-day type

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| tax_date | (a) against B1 | 89 | +6.1% [-12.2, +15.3] | +0.286 [+0.01513, +1.965] | gain (was undecided) |
| tax_date | (a) against B1' | 89 | +5.9% [-2.7, +12.3] | +0.2765 [+0.0107, +2.534] | gain (was undecided) |
| tax_date | (a) against spread_mr_ctx | 89 | +4.1% [-6.3, +16.3] | +0.1885 [+0.005494, +0.6318] | gain (was undecided) |
| tax_date | (s1) against B1 | 89 | -1.2% [-24.2, +5.8] | -0.05749 [-0.7284, +0.3654] | undecided |
| tax_date | (s1) against B1' | 89 | -1.4% [-26.5, +5.9] | -0.06702 [-0.7494, +0.3348] | undecided |
| tax_date | (s1) against (a) | 89 | -7.8% [-51.7, +1.9] | -0.3435 [-2.508, +0.02635] | undecided |
| tax_date | (s1) against spread_mr_ctx | 89 | -3.4% [-12.7, +2.4] | -0.1551 [-0.8139, +0.05169] | undecided |
| tax_date | (s2) against B1 | 89 | +1.9% [-10.7, +6.5] | +0.08957 [-0.1755, +0.4918] | undecided |
| tax_date | (s2) against B1' | 89 | +1.7% [-7.1, +5.5] | +0.08003 [-0.1597, +0.4865] | undecided |
| tax_date | (s2) against (a) | 89 | -4.5% [-17.4, +0.3] | -0.1965 [-1.324, -0.007305] | loss (was undecided) |
| tax_date | (s2) against spread_mr_ctx | 89 | -0.2% [-5.4, +2.6] | -0.008008 [-0.2522, +0.1039] | undecided |
| tax_date | (s3) against B1 | 89 | +5.7% [-6.8, +12.4] | +0.2678 [+0.008825, +1.745] | gain (was undecided) |
| tax_date | (s3) against B1' | 89 | +5.6% [-1.6, +9.4] | +0.2583 [+0.007184, +2.022] | gain (was undecided) |
| tax_date | (s3) against (a) | 89 | -0.4% [-2.4, +0.9] | -0.01822 [-0.1014, +0.02052] | undecided |
| tax_date | (s3) against (s1) | 89 | +6.9% [-11.1, +51.9] | +0.3253 [-0.03392, +4.639] | undecided |
| tax_date | (s3) against spread_mr_ctx | 89 | +3.7% [-5.0, +14.5] | +0.1702 [+0.009531, +0.6147] | gain (was undecided) |
| tax_date | (s4) against B1 | 89 | -2.3% [-38.7, +6.6] | -0.1055 [-0.9511, +0.3219] | undecided |
| tax_date | (s4) against B1' | 89 | -2.5% [-47.0, +7.2] | -0.115 [-0.9952, +0.314] | undecided |
| tax_date | (s4) against (a) | 89 | -8.9% [-55.5, +5.3] | -0.3915 [-1.579, -0.01775] | loss (was undecided) |
| tax_date | (s4) against spread_mr_ctx | 89 | -4.4% [-28.9, +4.8] | -0.2031 [-0.9658, -0.001946] | loss (was undecided) |

### Politis-White block beside 10: grid_crps, by all decision days

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| all decision days | (s1) against the base (a) | 1855 | -1.3% [-7.4, +2.7] | -0.02191 [-0.1223, +0.04626] | undecided |
| all decision days | (s2) against the base (a) | 1855 | -1.0% [-8.7, +3.4] | -0.01699 [-0.146, +0.05799] | undecided |
| all decision days | (s3) against the base (a) | 1855 | +4.3% [+1.5, +6.8] | +0.07369 [+0.02798, +0.1171] | gain |
| all decision days | (s4) against the base (a) | 1855 | -3.7% [-10.3, +0.8] | -0.0623 [-0.1695, +0.01366] | undecided |

### Politis-White block beside 10: upper_tail_twcrps, by all decision days

| group | comparison | days | skill [90%] | mean d [90%] | reading (mean-d bound) |
|---|---|---|---|---|---|
| all decision days | (s1) against the base (a) | 1855 | -1.7% [-10.1, +3.8] | -0.01552 [-0.08369, +0.03602] | undecided |
| all decision days | (s2) against the base (a) | 1855 | -2.2% [-12.7, +3.5] | -0.02016 [-0.1072, +0.03274] | undecided |
| all decision days | (s3) against the base (a) | 1855 | +4.4% [+0.9, +7.9] | +0.03913 [+0.01235, +0.07395] | gain |
| all decision days | (s4) against the base (a) | 1855 | -4.3% [-14.7, +2.3] | -0.0389 [-0.1131, +0.01765] | undecided |

Nothing here is a verdict for a hypothesis. The first page stands.
