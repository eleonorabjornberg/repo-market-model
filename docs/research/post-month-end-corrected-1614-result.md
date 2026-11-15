# The misses after a month-end, by business day 1, 2 and 3: re-issued with every resample kept (#1614)

**Development, not a verdict.** H5, known limits of the frozen candidate (s3c-ann-net). This is a new dated version of the page of #1611 (merged as #1612); the old page and its `result.json` stand as published, with a dated note pointing here. No refit, no new arm, no change to the candidate, no lockbox day, no record in `docs/runs/` edited, nothing registered. Implements her docket rulings of 15 November 2026: finding #1613, option (a), with the second interval added in chat, and #1612, option (a). Every figure is read from `docs/research/post-month-end-corrected-1614/result.json`; the script is `scripts/post_month_end_corrected_1614.py`, the test `tests/test_post_month_end_corrected_1614.py`. The forecasts are the walks of #1547 and #1555 (the 1363 walk, regenerated and checked against its sha256).

**Prior work** (`docs/research/settled-questions.md`, 15 November). S18 (#1275, failed) and #1547 cover location in aggregate; #1611 is the business-day split this page corrects. No entry covers miss-share intervals for rows that can draw no miss, so this is a new question.

## What changed from #1611

**The rule, stated.** The studentized bootstrap is scoring protocol v1's (10,000 draws, mean block 10, Newey-West lag 10, 90%, seed 1611, the same resample stream as #1611), applied to the group's target days in date order. **Every resample is kept**, including those that draw no miss. A resample with no variance has no standard error: its studentized value is -infinity if its mean is below the observed share, +infinity if above, 0 on a tie. So the upper end of a share's interval can reach 1 (the page prints 1.000), and an unclipped end that is unbounded prints as 'unbounded'. #1611 dropped those resamples and reported an interval while at least 90% remained; the protocol's scorer refuses such a resample instead of skipping it. A group with no miss in the data has no studentized interval, as in the protocol. A group under 20 target days has none either. The median error's interval is the percentile interval of the resampled medians, as before.

**The share column.** A share printed beside a cell count is misses over cells. #1611's 2026 table printed the mean of each day's own share, which differs when days have unequal numbers of cells. The development windows have five cells on every day, where the two agree (checked at scoring).

**A second interval, exploratory.** Beside each studentized interval is a Wilson score interval of the share on an effective number of cells, N / DEFF (N the cells; DEFF the Newey-West variance of the mean of the daily shares at lag 10 over the variance of a proportion of N independent cells, never below 1). It is built for rare events (it keeps a lower end at 0 and an upper end above 0 with no miss) and corrects for the five leads of a day and for the dependence between days. It is exploratory: it is not the protocol's interval and not a calibrated one, with no miss DEFF is not estimable and is held at 1 (too narrow if misses would cluster), and lag 10 on non-consecutive monthly days is a choice of this page. Which interval the project uses for such shares is her decision, put as a question in the pull request; nothing here settles it.

**Rows that moved** (development window, against #1611's figures). Listed: every share interval whose printed figures differ or whose reading against 0.05 changes. Every share interval not listed is as #1611 published it, or differs only beyond the third decimal (all of them are in `result.json`, `changed_from_1611`). A reading of 'holds 0.05' that rests on an upper end of 1.000 carries no information: it says the share cannot be bounded from above on so few misses.

| scope | target | group | tail | misses | #1611 interval | interval here | resamples with no miss | reading then | reading now |
|---|---|---|---|---|---|---|---|---|---|
| all | business day 1 | lead 1 | below q05 | 2 of 89 | none | [0.004, 1.000] | 1041 | no interval | holds 0.05 (changed) |
| all | business day 1 | lead 2 | below q05 | 1 of 89 | none | [0.000, 1.000] | 3283 | no interval | holds 0.05 (changed) |
| all | business day 1 | lead 3 | above q95 | 13 of 89 | [0.063, 0.251] | [0.063, 0.252] | 2 | above 0.05 | above 0.05 |
| all | business day 1 | lead 4 | below q05 | 6 of 89 | [0.024, 0.135] | [0.024, 0.137] | 23 | holds 0.05 | holds 0.05 |
| all | business day 1 | lead 4 | above q95 | 16 of 89 | [0.060, 0.319] | [0.060, 0.320] | 2 | above 0.05 | above 0.05 |
| all | business day 1 | lead 5 | below q05 | 7 of 89 | [0.028, 0.162] | [0.028, 0.165] | 20 | holds 0.05 | holds 0.05 |
| all | business day 1 | pooled | below q05 | 19 of 445 | [0.016, 0.087] | [0.016, 0.088] | 20 | holds 0.05 | holds 0.05 |
| all | business day 2 | lead 3 | below q05 | 4 of 89 | [0.014, 0.116] | [0.015, 0.117] | 195 | holds 0.05 | holds 0.05 |
| all | business day 2 | lead 4 | below q05 | 5 of 89 | [0.017, 0.125] | [0.017, 0.172] | 180 | holds 0.05 | holds 0.05 |
| all | business day 2 | lead 5 | below q05 | 7 of 89 | [0.022, 0.186] | [0.022, 0.192] | 114 | holds 0.05 | holds 0.05 |
| all | business day 3 | lead 2 | above q95 | 7 of 89 | [0.024, 0.189] | [0.024, 0.212] | 85 | holds 0.05 | holds 0.05 |
| all | business day 3 | lead 3 | below q05 | 10 of 89 | [0.043, 0.217] | [0.043, 0.218] | 6 | holds 0.05 | holds 0.05 |
| all | business day 3 | lead 4 | above q95 | 7 of 89 | [0.024, 0.189] | [0.024, 0.212] | 85 | holds 0.05 | holds 0.05 |
| all | business day 3 | lead 5 | above q95 | 6 of 89 | [0.021, 0.159] | [0.022, 0.169] | 102 | holds 0.05 | holds 0.05 |
| all | business day 3 | pooled | above q95 | 30 of 445 | [0.021, 0.153] | [0.021, 0.166] | 85 | holds 0.05 | holds 0.05 |
| quarter_end | business day 1 | lead 1 | above q95 | 8 of 29 | [0.041, 0.492] | [0.041, 0.493] | 4 | holds 0.05 | holds 0.05 |
| quarter_end | business day 1 | lead 3 | above q95 | 6 of 29 | [0.000, 0.840] | [0.000, 0.968] | 285 | holds 0.05 | holds 0.05 |
| quarter_end | business day 1 | lead 4 | below q05 | 1 of 29 | none | [0.000, 1.000] | 2444 | no interval | holds 0.05 (changed) |
| quarter_end | business day 1 | lead 4 | above q95 | 10 of 29 | [0.003, 0.795] | [0.003, 0.797] | 5 | holds 0.05 | holds 0.05 |
| quarter_end | business day 1 | lead 5 | below q05 | 1 of 29 | none | [0.000, 1.000] | 2444 | no interval | holds 0.05 (changed) |
| quarter_end | business day 1 | lead 5 | above q95 | 9 of 29 | [0.015, 0.650] | [0.015, 0.652] | 5 | holds 0.05 | holds 0.05 |
| quarter_end | business day 1 | pooled | below q05 | 2 of 145 | none | [0.000, 1.000] | 2444 | no interval | holds 0.05 (changed) |
| quarter_end | business day 1 | pooled | above q95 | 40 of 145 | [0.011, 0.585] | [0.011, 0.587] | 3 | holds 0.05 | holds 0.05 |
| quarter_end | business day 2 | lead 1 | below q05 | 4 of 29 | [0.066, 0.248] | [0.066, 0.252] | 18 | above 0.05 | above 0.05 |
| quarter_end | business day 2 | lead 1 | above q95 | 5 of 29 | [0.070, 0.441] | [0.070, 0.445] | 11 | above 0.05 | above 0.05 |
| quarter_end | business day 2 | lead 2 | below q05 | 1 of 29 | none | [0.000, 1.000] | 2380 | no interval | holds 0.05 (changed) |
| quarter_end | business day 2 | lead 3 | below q05 | 1 of 29 | none | [0.000, 1.000] | 2380 | no interval | holds 0.05 (changed) |
| quarter_end | business day 2 | lead 4 | below q05 | 1 of 29 | none | [0.000, 1.000] | 2380 | no interval | holds 0.05 (changed) |
| quarter_end | business day 2 | lead 5 | below q05 | 2 of 29 | [0.021, 0.109] | [0.022, 0.109] | 295 | holds 0.05 | holds 0.05 |
| quarter_end | business day 3 | lead 1 | below q05 | 7 of 29 | [0.000, 0.918] | [0.001, 0.967] | 62 | holds 0.05 | holds 0.05 |
| quarter_end | business day 3 | lead 2 | below q05 | 5 of 29 | [0.000, 0.397] | [0.000, 0.721] | 396 | holds 0.05 | holds 0.05 |
| quarter_end | business day 3 | lead 2 | above q95 | 4 of 29 | [0.051, 0.373] | [0.051, 0.379] | 102 | above 0.05 | above 0.05 |
| quarter_end | business day 3 | lead 3 | below q05 | 2 of 29 | none | [0.000, 1.000] | 1053 | no interval | holds 0.05 (changed) |
| quarter_end | business day 3 | lead 3 | above q95 | 4 of 29 | [0.051, 0.373] | [0.051, 0.379] | 102 | above 0.05 | above 0.05 |
| quarter_end | business day 3 | lead 4 | below q05 | 2 of 29 | none | [0.000, 1.000] | 1053 | no interval | holds 0.05 (changed) |
| quarter_end | business day 3 | lead 4 | above q95 | 4 of 29 | [0.051, 0.373] | [0.051, 0.379] | 102 | above 0.05 | above 0.05 |
| quarter_end | business day 3 | lead 5 | below q05 | 2 of 29 | [0.000, 0.122] | [0.001, 1.000] | 549 | holds 0.05 | holds 0.05 |
| quarter_end | business day 3 | lead 5 | above q95 | 3 of 29 | [0.045, 0.215] | [0.046, 0.215] | 151 | holds 0.05 | holds 0.05 |
| quarter_end | business day 3 | pooled | below q05 | 18 of 145 | [0.000, 0.475] | [0.000, 0.496] | 58 | holds 0.05 | holds 0.05 |
| quarter_end | business day 3 | pooled | above q95 | 17 of 145 | [0.048, 0.268] | [0.048, 0.270] | 102 | holds 0.05 | holds 0.05 |
| other | business day 1 | lead 1 | below q05 | 2 of 60 | [0.003, 0.054] | [0.003, 1.000] | 1000 | holds 0.05 | holds 0.05 |
| other | business day 1 | lead 2 | below q05 | 1 of 60 | none | [0.002, 1.000] | 3029 | no interval | holds 0.05 (changed) |
| other | business day 1 | lead 2 | above q95 | 7 of 60 | [0.033, 0.260] | [0.033, 0.261] | 12 | holds 0.05 | holds 0.05 |
| other | business day 1 | lead 3 | above q95 | 7 of 60 | [0.033, 0.260] | [0.033, 0.261] | 12 | holds 0.05 | holds 0.05 |
| other | business day 1 | lead 4 | above q95 | 6 of 60 | [0.001, 0.267] | [0.002, 0.375] | 252 | holds 0.05 | holds 0.05 |
| other | business day 1 | pooled | below q05 | 17 of 300 | [0.023, 0.105] | [0.023, 0.107] | 16 | holds 0.05 | holds 0.05 |
| other | business day 1 | pooled | above q95 | 34 of 300 | [0.033, 0.262] | [0.033, 0.263] | 4 | holds 0.05 | holds 0.05 |
| other | business day 2 | lead 1 | below q05 | 12 of 60 | [0.054, 0.359] | [0.054, 0.360] | 1 | above 0.05 | above 0.05 |
| other | business day 2 | lead 5 | below q05 | 5 of 60 | [0.025, 0.180] | [0.025, 0.188] | 101 | holds 0.05 | holds 0.05 |
| other | business day 3 | lead 1 | above q95 | 2 of 60 | none | [0.000, 1.000] | 2645 | no interval | holds 0.05 (changed) |
| other | business day 3 | lead 2 | above q95 | 3 of 60 | [0.009, 0.115] | [0.010, 1.000] | 610 | holds 0.05 | holds 0.05 |
| other | business day 3 | lead 3 | below q05 | 8 of 60 | [0.029, 0.287] | [0.029, 0.290] | 26 | holds 0.05 | holds 0.05 |
| other | business day 3 | lead 3 | above q95 | 2 of 60 | [0.006, 0.054] | [0.007, 1.000] | 694 | holds 0.05 | holds 0.05 |
| other | business day 3 | lead 4 | below q05 | 8 of 60 | [0.033, 0.268] | [0.033, 0.274] | 25 | holds 0.05 | holds 0.05 |
| other | business day 3 | lead 4 | above q95 | 3 of 60 | [0.009, 0.115] | [0.010, 1.000] | 610 | holds 0.05 | holds 0.05 |
| other | business day 3 | lead 5 | below q05 | 8 of 60 | [0.033, 0.268] | [0.033, 0.274] | 25 | holds 0.05 | holds 0.05 |
| other | business day 3 | lead 5 | above q95 | 3 of 60 | [0.009, 0.115] | [0.010, 1.000] | 610 | holds 0.05 | holds 0.05 |
| other | business day 3 | pooled | above q95 | 13 of 300 | [0.008, 0.108] | [0.008, 1.000] | 610 | holds 0.05 | holds 0.05 |
| by regime | business day 1 | 2021-23 | below q05 | 6 of 180 | none | [0.000, 1.000] | 2165 | no interval | holds 0.05 (changed) |
| by regime | business day 2 | 2021-23 | below q05 | 3 of 180 | [0.000, 0.045] | [0.000, 1.000] | 708 | below 0.05 | holds 0.05 (changed) |
| by regime | business day 3 | 2021-23 | below q05 | 9 of 180 | [0.003, 0.232] | [0.003, 0.233] | 23 | holds 0.05 | holds 0.05 |
| by regime | business day 3 | 2021-23 | above q95 | 16 of 180 | [0.000, 0.246] | [0.000, 1.000] | 804 | holds 0.05 | holds 0.05 |

## Note of 15 November 2026 under the post-month-end known limit

For the known limit "Post-month-end band coverage" of `docs/model/candidate.json` (the validation report states no figure, so the figures are quoted here and the limit's source list points to this page). Development data, no change to the candidate.

- Business day 1, above q95, all month-ends, leads pooled: 74 misses in 445 cells (0.166); studentized 90% interval [0.065, 0.277]; exploratory score interval [0.106, 0.252] (DEFF 6.4).
- Business day 2, above q95, all month-ends, leads pooled: 64 misses in 445 cells (0.144); studentized 90% interval [0.090, 0.216]; exploratory score interval [0.096, 0.210] (DEFF 4.4).
- Business day 3, below q05, all month-ends, leads pooled: 67 misses in 445 cells (0.151); studentized 90% interval [0.071, 0.249]; exploratory score interval [0.096, 0.228] (DEFF 5.6).
- Business day 2, 2021-23, below q05, leads pooled (3 misses in 180 cells): #1611 showed [0.000, 0.045] (below 0.05); with every resample kept the studentized interval is [0.000, 1.000] and the exploratory score interval is [0.006, 0.049] (DEFF 1.5).
- Pooled row that changes its reading: quarter_end, business day 1, below q05: no interval to holds 0.05 (interval [0.000, 1.000]).

## What is measured

A target day is business day b when `derived_features.bday_of_month` is b, the count the candidate's `post_month_end_window` term reads. For each business day and lead: the cells whose outcome fell below the forecast q05 and above its q95 (the strict miss; nominal share 0.05), and the signed error y - q50 in bp, as a median and as a mean. A pooled figure alone is not a result: the pooled row sits beside the five leads, and every regime is split below.

## Reading, by business day

Mechanical, from the pooled rows of the development window: whether each interval of the miss share excludes the nominal 0.05, and whether the interval of the median error excludes 0.

| scope | target | days | below q05, studentized | below q05, score | above q95, studentized | above q95, score | median error interval |
|---|---|---|---|---|---|---|---|
| All month-ends | business day 1 | 89 | holds 0.05 | holds 0.05 | above 0.05 | above 0.05 | holds 0 |
| All month-ends | business day 2 | 89 | holds 0.05 | holds 0.05 | above 0.05 | above 0.05 | holds 0 |
| All month-ends | business day 3 | 89 | above 0.05 | above 0.05 | holds 0.05 | holds 0.05 | excludes 0 |
| After a quarter-end month-end | business day 1 | 29 | holds 0.05 | below 0.05 | holds 0.05 | above 0.05 | excludes 0 |
| After a quarter-end month-end | business day 2 | 29 | holds 0.05 | holds 0.05 | above 0.05 | above 0.05 | excludes 0 |
| After a quarter-end month-end | business day 3 | 29 | holds 0.05 | holds 0.05 | holds 0.05 | above 0.05 | holds 0 |
| After the other month-ends | business day 1 | 60 | holds 0.05 | holds 0.05 | holds 0.05 | above 0.05 | holds 0 |
| After the other month-ends | business day 2 | 60 | holds 0.05 | holds 0.05 | above 0.05 | above 0.05 | holds 0 |
| After the other month-ends | business day 3 | 60 | above 0.05 | above 0.05 | holds 0.05 | holds 0.05 | excludes 0 |

## All month-ends

| target | lead | days | cells | below q05: misses (share) [studentized 90%] | below q05: score 90% (exploratory) | above q95: misses (share) [studentized 90%] | above q95: score 90% (exploratory) | median error, bp [90%] | mean error, bp [90%] |
|---|---|---|---|---|---|---|---|---|---|
| business day 1 | 1 | 89 | 89 | 2 (0.022) [0.004, 1.000] | [0.007, 0.066] (DEFF 1.0) | 16 (0.180) [0.074, 0.289] | [0.115, 0.270] (DEFF 1.4) | 0.10 [-0.25, 1.00] | 1.68 [0.29, 5.43] |
| business day 1 | 2 | 89 | 89 | 1 (0.011) [0.000, 1.000] | [0.003, 0.049] (DEFF 1.0) | 14 (0.157) [0.067, 0.275] | [0.096, 0.247] (DEFF 1.4) | -0.14 [-0.37, 0.64] | 1.17 [-0.06, 4.36] |
| business day 1 | 3 | 89 | 89 | 3 (0.034) [0.014, 0.066] | [0.014, 0.081] (DEFF 1.0) | 13 (0.146) [0.063, 0.252] | [0.090, 0.228] (DEFF 1.2) | 0.17 [-0.41, 0.67] | 1.01 [-0.27, 3.66] |
| business day 1 | 4 | 89 | 89 | 6 (0.067) [0.024, 0.137] | [0.035, 0.126] (DEFF 1.0) | 16 (0.180) [0.060, 0.320] | [0.109, 0.282] (DEFF 1.7) | -0.12 [-0.50, 0.77] | 1.14 [-0.36, 3.78] |
| business day 1 | 5 | 89 | 89 | 7 (0.079) [0.028, 0.165] | [0.040, 0.147] (DEFF 1.2) | 15 (0.169) [0.066, 0.297] | [0.102, 0.265] (DEFF 1.6) | -0.02 [-0.38, 1.07] | 1.13 [-0.57, 3.55] |
| business day 1 | pooled | 89 | 445 | 19 (0.043) [0.016, 0.088] | [0.022, 0.080] (DEFF 3.2) | 74 (0.166) [0.065, 0.277] | [0.106, 0.252] (DEFF 6.4) | 0.11 [-0.39, 0.88] | 1.23 [-0.16, 4.07] |
| business day 2 | 1 | 89 | 89 | 16 (0.180) [0.086, 0.292] | [0.113, 0.273] (DEFF 1.5) | 10 (0.112) [0.055, 0.241] | [0.061, 0.198] (DEFF 1.5) | -0.21 [-0.35, 0.07] | -0.57 [-1.45, 0.08] |
| business day 2 | 2 | 89 | 89 | 4 (0.045) [0.014, 0.118] | [0.020, 0.099] (DEFF 1.1) | 14 (0.157) [0.098, 0.234] | [0.104, 0.231] (DEFF 1.0) | 0.20 [-0.17, 0.58] | 0.61 [0.01, 1.44] |
| business day 2 | 3 | 89 | 89 | 4 (0.045) [0.015, 0.117] | [0.020, 0.097] (DEFF 1.0) | 12 (0.135) [0.089, 0.199] | [0.086, 0.205] (DEFF 1.0) | -0.07 [-0.25, 0.36] | 0.26 [-0.35, 0.96] |
| business day 2 | 4 | 89 | 89 | 5 (0.056) [0.017, 0.172] | [0.025, 0.121] (DEFF 1.3) | 13 (0.146) [0.091, 0.220] | [0.095, 0.218] (DEFF 1.0) | 0.04 [-0.23, 0.48] | 0.27 [-0.39, 0.91] |
| business day 2 | 5 | 89 | 89 | 7 (0.079) [0.022, 0.192] | [0.035, 0.166] (DEFF 1.8) | 15 (0.169) [0.096, 0.279] | [0.108, 0.254] (DEFF 1.3) | 0.02 [-0.25, 0.65] | 0.33 [-0.49, 1.00] |
| business day 2 | pooled | 89 | 445 | 36 (0.081) [0.037, 0.170] | [0.045, 0.141] (DEFF 4.9) | 64 (0.144) [0.090, 0.216] | [0.096, 0.210] (DEFF 4.4) | 0.11 [-0.20, 0.25] | 0.18 [-0.43, 0.75] |
| business day 3 | 1 | 89 | 89 | 18 (0.202) [0.104, 0.348] | [0.132, 0.298] (DEFF 1.4) | 4 (0.045) [0.012, 0.120] | [0.019, 0.101] (DEFF 1.1) | -0.30 [-1.07, -0.22] | -1.34 [-2.96, -0.24] |
| business day 3 | 2 | 89 | 89 | 19 (0.213) [0.090, 0.353] | [0.135, 0.321] (DEFF 1.7) | 7 (0.079) [0.024, 0.212] | [0.036, 0.165] (DEFF 1.8) | -0.45 [-1.71, -0.25] | -1.45 [-3.16, -0.24] |
| business day 3 | 3 | 89 | 89 | 10 (0.112) [0.043, 0.218] | [0.062, 0.194] (DEFF 1.4) | 6 (0.067) [0.018, 0.186] | [0.028, 0.152] (DEFF 1.8) | -0.21 [-0.59, -0.13] | -0.63 [-1.78, 0.19] |
| business day 3 | 4 | 89 | 89 | 10 (0.112) [0.043, 0.214] | [0.063, 0.193] (DEFF 1.4) | 7 (0.079) [0.024, 0.212] | [0.036, 0.165] (DEFF 1.8) | -0.17 [-0.53, -0.11] | -0.76 [-1.90, 0.05] |
| business day 3 | 5 | 89 | 89 | 10 (0.112) [0.051, 0.205] | [0.064, 0.189] (DEFF 1.3) | 6 (0.067) [0.022, 0.169] | [0.031, 0.139] (DEFF 1.4) | -0.18 [-0.50, -0.06] | -0.84 [-1.84, -0.10] |
| business day 3 | pooled | 89 | 445 | 67 (0.151) [0.071, 0.249] | [0.096, 0.228] (DEFF 5.6) | 30 (0.067) [0.021, 0.166] | [0.031, 0.139] (DEFF 7.0) | -0.29 [-0.87, -0.18] | -1.00 [-2.29, -0.09] |

## After a quarter-end month-end (target in January, April, July or October)

| target | lead | days | cells | below q05: misses (share) [studentized 90%] | below q05: score 90% (exploratory) | above q95: misses (share) [studentized 90%] | above q95: score 90% (exploratory) | median error, bp [90%] | mean error, bp [90%] |
|---|---|---|---|---|---|---|---|---|---|
| business day 1 | 1 | 29 | 29 | 0 (0.000) | [0.000, 0.085] (DEFF 1.0) | 8 (0.276) [0.041, 0.493] | [0.150, 0.451] (DEFF 1.3) | 0.98 [0.04, 2.19] | 4.12 [0.78, 17.89] |
| business day 1 | 2 | 29 | 29 | 0 (0.000) | [0.000, 0.085] (DEFF 1.0) | 7 (0.241) [0.030, 0.395] | [0.137, 0.390] (DEFF 1.0) | 0.95 [-0.14, 1.95] | 3.56 [0.36, 17.10] |
| business day 1 | 3 | 29 | 29 | 0 (0.000) | [0.000, 0.085] (DEFF 1.0) | 6 (0.207) [0.000, 0.968] | [0.076, 0.452] (DEFF 2.6) | 0.94 [0.53, 2.40] | 3.71 [0.45, 15.96] |
| business day 1 | 4 | 29 | 29 | 1 (0.034) [0.000, 1.000] | [0.008, 0.141] (DEFF 1.0) | 10 (0.345) [0.003, 0.797] | [0.169, 0.577] (DEFF 2.4) | 0.97 [-0.15, 2.33] | 4.09 [0.51, 14.65] |
| business day 1 | 5 | 29 | 29 | 1 (0.034) [0.000, 1.000] | [0.008, 0.141] (DEFF 1.0) | 9 (0.310) [0.015, 0.652] | [0.159, 0.517] (DEFF 1.8) | 1.38 [-0.07, 2.39] | 4.00 [0.25, 13.56] |
| business day 1 | pooled | 29 | 145 | 2 (0.014) [0.000, 1.000] | [0.004, 0.046] (DEFF 1.3) | 40 (0.276) [0.011, 0.587] | [0.143, 0.465] (DEFF 7.7) | 0.98 [0.28, 2.45] | 3.90 [0.50, 15.79] |
| business day 2 | 1 | 29 | 29 | 4 (0.138) [0.066, 0.252] | [0.063, 0.274] (DEFF 1.0) | 5 (0.172) [0.070, 0.445] | [0.087, 0.314] (DEFF 1.0) | 0.45 [-0.22, 0.54] | -0.23 [-1.20, 0.58] |
| business day 2 | 2 | 29 | 29 | 1 (0.034) [0.000, 1.000] | [0.008, 0.141] (DEFF 1.0) | 9 (0.310) [0.164, 0.449] | [0.190, 0.463] (DEFF 1.0) | 1.11 [0.39, 1.75] | 1.57 [0.46, 3.31] |
| business day 2 | 3 | 29 | 29 | 1 (0.034) [0.000, 1.000] | [0.008, 0.141] (DEFF 1.0) | 7 (0.241) [0.173, 0.309] | [0.137, 0.390] (DEFF 1.0) | 0.96 [0.05, 1.83] | 1.29 [0.30, 2.98] |
| business day 2 | 4 | 29 | 29 | 1 (0.034) [0.000, 1.000] | [0.008, 0.141] (DEFF 1.0) | 8 (0.276) [0.069, 0.416] | [0.163, 0.427] (DEFF 1.0) | 1.41 [0.36, 2.78] | 1.55 [0.44, 3.13] |
| business day 2 | 5 | 29 | 29 | 2 (0.069) [0.022, 0.109] | [0.023, 0.188] (DEFF 1.0) | 10 (0.345) [0.063, 0.618] | [0.195, 0.534] (DEFF 1.5) | 1.98 [0.49, 2.62] | 1.81 [0.31, 3.34] |
| business day 2 | pooled | 29 | 145 | 9 (0.062) [0.022, 0.178] | [0.030, 0.123] (DEFF 1.9) | 39 (0.269) [0.129, 0.380] | [0.181, 0.380] (DEFF 2.8) | 1.32 [0.23, 1.79] | 1.20 [0.24, 2.38] |
| business day 3 | 1 | 29 | 29 | 7 (0.241) [0.001, 0.967] | [0.098, 0.484] (DEFF 2.5) | 2 (0.069) [0.033, 0.106] | [0.023, 0.188] (DEFF 1.0) | -0.25 [-0.63, -0.02] | -2.08 [-4.90, -0.16] |
| business day 3 | 2 | 29 | 29 | 5 (0.172) [0.000, 0.721] | [0.062, 0.395] (DEFF 2.2) | 4 (0.138) [0.051, 0.379] | [0.063, 0.274] (DEFF 1.0) | -0.23 [-1.09, 0.30] | -1.54 [-3.47, 0.22] |
| business day 3 | 3 | 29 | 29 | 2 (0.069) [0.000, 1.000] | [0.022, 0.194] (DEFF 1.1) | 4 (0.138) [0.051, 0.379] | [0.063, 0.274] (DEFF 1.0) | 0.29 [-0.29, 0.60] | -0.29 [-1.39, 0.71] |
| business day 3 | 4 | 29 | 29 | 2 (0.069) [0.000, 1.000] | [0.022, 0.194] (DEFF 1.1) | 4 (0.138) [0.051, 0.379] | [0.063, 0.274] (DEFF 1.0) | 0.01 [-0.28, 0.28] | -0.34 [-1.34, 0.52] |
| business day 3 | 5 | 29 | 29 | 2 (0.069) [0.001, 1.000] | [0.023, 0.188] (DEFF 1.0) | 3 (0.103) [0.046, 0.215] | [0.042, 0.232] (DEFF 1.0) | 0.18 [0.03, 0.48] | -0.25 [-1.09, 0.60] |
| business day 3 | pooled | 29 | 145 | 18 (0.124) [0.000, 0.496] | [0.048, 0.284] (DEFF 6.8) | 17 (0.117) [0.048, 0.270] | [0.059, 0.220] (DEFF 3.3) | -0.07 [-0.57, 0.34] | -0.90 [-2.29, 0.33] |

## After the other month-ends

| target | lead | days | cells | below q05: misses (share) [studentized 90%] | below q05: score 90% (exploratory) | above q95: misses (share) [studentized 90%] | above q95: score 90% (exploratory) | median error, bp [90%] | mean error, bp [90%] |
|---|---|---|---|---|---|---|---|---|---|
| business day 1 | 1 | 60 | 60 | 2 (0.033) [0.003, 1.000] | [0.011, 0.096] (DEFF 1.0) | 8 (0.133) [0.054, 0.243] | [0.077, 0.222] (DEFF 1.0) | -0.07 [-0.38, 0.64] | 0.51 [-0.44, 1.26] |
| business day 1 | 2 | 60 | 60 | 1 (0.017) [0.002, 1.000] | [0.004, 0.071] (DEFF 1.0) | 7 (0.117) [0.033, 0.261] | [0.060, 0.214] (DEFF 1.2) | -0.26 [-0.47, 0.40] | 0.01 [-0.69, 0.64] |
| business day 1 | 3 | 60 | 60 | 3 (0.050) [0.023, 0.092] | [0.020, 0.119] (DEFF 1.0) | 7 (0.117) [0.033, 0.261] | [0.060, 0.214] (DEFF 1.2) | -0.24 [-0.99, 0.47] | -0.30 [-1.48, 0.55] |
| business day 1 | 4 | 60 | 60 | 5 (0.083) [0.034, 0.145] | [0.041, 0.161] (DEFF 1.0) | 6 (0.100) [0.002, 0.375] | [0.044, 0.212] (DEFF 1.7) | -0.22 [-1.40, 0.36] | -0.29 [-1.82, 0.64] |
| business day 1 | 5 | 60 | 60 | 6 (0.100) [0.038, 0.191] | [0.052, 0.185] (DEFF 1.1) | 6 (0.100) [0.030, 0.205] | [0.052, 0.183] (DEFF 1.0) | -0.20 [-1.48, 0.39] | -0.26 [-1.97, 0.82] |
| business day 1 | pooled | 60 | 300 | 17 (0.057) [0.023, 0.107] | [0.030, 0.103] (DEFF 2.6) | 34 (0.113) [0.033, 0.263] | [0.059, 0.205] (DEFF 5.8) | -0.25 [-0.80, 0.48] | -0.07 [-1.26, 0.74] |
| business day 2 | 1 | 60 | 60 | 12 (0.200) [0.054, 0.360] | [0.114, 0.328] (DEFF 1.6) | 5 (0.083) [0.045, 0.141] | [0.041, 0.161] (DEFF 1.0) | -0.26 [-0.98, -0.12] | -0.73 [-2.05, 0.01] |
| business day 2 | 2 | 60 | 60 | 3 (0.050) [0.015, 0.105] | [0.020, 0.119] (DEFF 1.0) | 5 (0.083) [0.048, 0.131] | [0.041, 0.161] (DEFF 1.0) | -0.02 [-0.22, 0.28] | 0.14 [-0.20, 0.45] |
| business day 2 | 3 | 60 | 60 | 3 (0.050) [0.016, 0.105] | [0.020, 0.119] (DEFF 1.0) | 5 (0.083) [0.048, 0.131] | [0.041, 0.161] (DEFF 1.0) | -0.18 [-0.75, 0.17] | -0.24 [-0.92, 0.20] |
| business day 2 | 4 | 60 | 60 | 4 (0.067) [0.016, 0.188] | [0.028, 0.152] (DEFF 1.3) | 5 (0.083) [0.048, 0.131] | [0.041, 0.161] (DEFF 1.0) | -0.24 [-0.58, 0.37] | -0.34 [-1.00, 0.14] |
| business day 2 | 5 | 60 | 60 | 5 (0.083) [0.025, 0.188] | [0.038, 0.172] (DEFF 1.2) | 5 (0.083) [0.048, 0.131] | [0.041, 0.161] (DEFF 1.0) | -0.18 [-0.62, 0.02] | -0.38 [-1.06, 0.17] |
| business day 2 | pooled | 60 | 300 | 27 (0.090) [0.032, 0.175] | [0.048, 0.163] (DEFF 4.3) | 25 (0.083) [0.051, 0.128] | [0.052, 0.131] (DEFF 2.2) | -0.17 [-0.54, 0.22] | -0.31 [-0.95, 0.14] |
| business day 3 | 1 | 60 | 60 | 11 (0.183) [0.101, 0.254] | [0.115, 0.279] (DEFF 1.0) | 2 (0.033) [0.000, 1.000] | [0.009, 0.120] (DEFF 1.6) | -0.60 [-1.19, -0.24] | -0.99 [-2.76, 0.14] |
| business day 3 | 2 | 60 | 60 | 14 (0.233) [0.057, 0.385] | [0.141, 0.361] (DEFF 1.6) | 3 (0.050) [0.010, 1.000] | [0.020, 0.122] (DEFF 1.1) | -0.65 [-2.55, -0.26] | -1.41 [-3.87, -0.02] |
| business day 3 | 3 | 60 | 60 | 8 (0.133) [0.029, 0.290] | [0.067, 0.248] (DEFF 1.6) | 2 (0.033) [0.007, 1.000] | [0.011, 0.096] (DEFF 1.0) | -0.24 [-1.21, -0.20] | -0.79 [-2.76, 0.17] |
| business day 3 | 4 | 60 | 60 | 8 (0.133) [0.033, 0.274] | [0.068, 0.245] (DEFF 1.5) | 3 (0.050) [0.010, 1.000] | [0.020, 0.122] (DEFF 1.1) | -0.37 [-1.31, -0.14] | -0.96 [-3.08, 0.04] |
| business day 3 | 5 | 60 | 60 | 8 (0.133) [0.033, 0.274] | [0.068, 0.245] (DEFF 1.5) | 3 (0.050) [0.010, 1.000] | [0.020, 0.122] (DEFF 1.1) | -0.40 [-1.51, -0.07] | -1.13 [-2.88, -0.18] |
| business day 3 | pooled | 60 | 300 | 49 (0.163) [0.055, 0.289] | [0.097, 0.262] (DEFF 5.6) | 13 (0.043) [0.008, 1.000] | [0.017, 0.108] (DEFF 4.9) | -0.65 [-1.33, -0.19] | -1.06 [-3.05, -0.00] |

## By regime (leads pooled)

All month-ends, one row per business day and regime; the lead rows beside are points (misses of cells at that lead). A regime with under 20 target days has no interval.

| target | regime | days | cells | below q05: misses (share) [studentized 90%] | below q05: score 90% (exploratory) | above q95: misses (share) [studentized 90%] | above q95: score 90% (exploratory) | median error, bp [90%] | low/up misses by lead |
|---|---|---|---|---|---|---|---|---|---|
| business day 1 | 2018-19 | 17 | 85 | 4 (0.047) | none | 11 (0.129) | none | 0.67 (no interval) | h1: 1/2 of 17; h2: 0/2 of 17; h3: 1/2 of 17; h4: 1/2 of 17; h5: 1/3 of 17 |
| business day 1 | 2020 | 12 | 60 | 4 (0.067) | none | 0 (0.000) | none | -1.16 (no interval) | h1: 0/0 of 12; h2: 0/0 of 12; h3: 0/0 of 12; h4: 2/0 of 12; h5: 2/0 of 12 |
| business day 1 | 2021-23 | 36 | 180 | 6 (0.033) [0.000, 1.000] | [0.008, 0.125] (DEFF 5.1) | 34 (0.189) [0.034, 0.334] | [0.102, 0.323] (DEFF 5.4) | 0.36 [-0.21, 0.69] | h1: 1/8 of 36; h2: 1/8 of 36; h3: 1/5 of 36; h4: 1/7 of 36; h5: 2/6 of 36 |
| business day 1 | 2024 | 12 | 60 | 3 (0.050) | none | 20 (0.333) | none | 1.71 (no interval) | h1: 0/3 of 12; h2: 0/3 of 12; h3: 1/4 of 12; h4: 1/5 of 12; h5: 1/5 of 12 |
| business day 1 | 2025-26 | 12 | 60 | 2 (0.033) | none | 9 (0.150) | none | 1.47 (no interval) | h1: 0/3 of 12; h2: 0/1 of 12; h3: 0/2 of 12; h4: 1/2 of 12; h5: 1/1 of 12 |
| business day 2 | 2018-19 | 17 | 85 | 12 (0.141) | none | 13 (0.153) | none | 0.11 (no interval) | h1: 6/1 of 17; h2: 1/3 of 17; h3: 1/3 of 17; h4: 2/3 of 17; h5: 2/3 of 17 |
| business day 2 | 2020 | 12 | 60 | 6 (0.100) | none | 5 (0.083) | none | 0.32 (no interval) | h1: 1/1 of 12; h2: 1/1 of 12; h3: 1/1 of 12; h4: 1/1 of 12; h5: 2/1 of 12 |
| business day 2 | 2021-23 | 36 | 180 | 3 (0.017) [0.000, 1.000] | [0.006, 0.049] (DEFF 1.5) | 34 (0.189) [0.071, 0.323] | [0.095, 0.340] (DEFF 6.8) | -0.03 [-0.21, 0.36] | h1: 3/7 of 36; h2: 0/8 of 36; h3: 0/6 of 36; h4: 0/6 of 36; h5: 0/7 of 36 |
| business day 2 | 2024 | 12 | 60 | 6 (0.100) | none | 8 (0.133) | none | 0.28 (no interval) | h1: 3/1 of 12; h2: 0/1 of 12; h3: 1/1 of 12; h4: 1/2 of 12; h5: 1/3 of 12 |
| business day 2 | 2025-26 | 12 | 60 | 9 (0.150) | none | 4 (0.067) | none | -1.37 (no interval) | h1: 3/0 of 12; h2: 2/1 of 12; h3: 1/1 of 12; h4: 1/1 of 12; h5: 2/1 of 12 |
| business day 3 | 2018-19 | 17 | 85 | 18 (0.212) | none | 5 (0.059) | none | -2.15 (no interval) | h1: 4/1 of 17; h2: 5/1 of 17; h3: 3/1 of 17; h4: 3/1 of 17; h5: 3/1 of 17 |
| business day 3 | 2020 | 12 | 60 | 5 (0.083) | none | 9 (0.150) | none | 0.11 (no interval) | h1: 1/2 of 12; h2: 1/2 of 12; h3: 1/1 of 12; h4: 1/2 of 12; h5: 1/2 of 12 |
| business day 3 | 2021-23 | 36 | 180 | 9 (0.050) [0.003, 0.233] | [0.020, 0.120] (DEFF 3.1) | 16 (0.089) [0.000, 1.000] | [0.031, 0.231] (DEFF 7.5) | -0.18 [-0.29, -0.14] | h1: 4/1 of 36; h2: 4/4 of 36; h3: 0/4 of 36; h4: 0/4 of 36; h5: 1/3 of 36 |
| business day 3 | 2024 | 12 | 60 | 18 (0.300) | none | 0 (0.000) | none | -1.30 (no interval) | h1: 6/0 of 12; h2: 5/0 of 12; h3: 2/0 of 12; h4: 3/0 of 12; h5: 2/0 of 12 |
| business day 3 | 2025-26 | 12 | 60 | 17 (0.283) | none | 0 (0.000) | none | -2.78 (no interval) | h1: 3/0 of 12; h2: 4/0 of 12; h3: 4/0 of 12; h4: 3/0 of 12; h5: 3/0 of 12 |

## The 2026 days (shown apart, decide nothing)

Points only: no interval, and no bootstrap is run on these days. The share is misses over cells.

| target | lead | days | cells | below q05: misses (share) | above q95: misses (share) | median error, bp |
|---|---|---|---|---|---|---|
| business day 1 | 1 | 8 | 8 | 0 (0.000) | 1 (0.125) | 2.54 |
| business day 1 | 2 | 7 | 7 | 0 (0.000) | 0 (0.000) | 1.13 |
| business day 1 | 3 | 8 | 8 | 0 (0.000) | 0 (0.000) | 0.42 |
| business day 1 | 4 | 8 | 8 | 0 (0.000) | 0 (0.000) | 0.34 |
| business day 1 | 5 | 8 | 8 | 0 (0.000) | 0 (0.000) | 0.76 |
| business day 1 | pooled | 9 | 39 | 0 (0.000) | 1 (0.026) | 1.13 |
| business day 2 | 1 | 8 | 8 | 0 (0.000) | 0 (0.000) | 0.02 |
| business day 2 | 2 | 8 | 8 | 0 (0.000) | 0 (0.000) | 1.20 |
| business day 2 | 3 | 7 | 7 | 0 (0.000) | 0 (0.000) | 1.26 |
| business day 2 | 4 | 8 | 8 | 0 (0.000) | 0 (0.000) | 0.06 |
| business day 2 | 5 | 8 | 8 | 0 (0.000) | 0 (0.000) | 0.05 |
| business day 2 | pooled | 9 | 39 | 0 (0.000) | 0 (0.000) | -0.05 |
| business day 3 | 1 | 8 | 8 | 0 (0.000) | 0 (0.000) | -1.62 |
| business day 3 | 2 | 8 | 8 | 1 (0.125) | 0 (0.000) | -1.93 |
| business day 3 | 3 | 8 | 8 | 0 (0.000) | 0 (0.000) | -1.76 |
| business day 3 | 4 | 7 | 7 | 0 (0.000) | 0 (0.000) | -1.38 |
| business day 3 | 5 | 8 | 8 | 1 (0.125) | 0 (0.000) | -1.28 |
| business day 3 | pooled | 9 | 39 | 2 (0.051) | 0 (0.000) | -1.64 |

## Limits and what was not checked

- Development data on days already seen, never a verdict; the 2026 days decide nothing.
- The five leads of one target day are not independent, so the pooled and regime rows count a target day once in the resample and the cell counts are not the effective sample.
- Per business day and lead a group holds under one hundred target days, so under five expected misses at the 0.05 level in most cells: an interval that holds 0.05 is not evidence that the share is 0.05, and an upper end of 1.000 says only that so few misses cannot bound the share.
- The studentized bootstrap is the protocol's interval for a mean of paired daily differences; applied to a rare-event share and to a series of non-consecutive days it is this study's reading, not a calibrated one (the calibration of #656 did not cover it). The score interval is exploratory and has not been calibrated either.
- The error is the outcome less the published (capped) forecast median; the shape ratios of #1547 are not recomputed here.
- No arm is fitted or scored. If a figure here pointed at a change to the candidate or its registration (#1511), that goes to Eleonora, not into code.
