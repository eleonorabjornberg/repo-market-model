# The candidate's calibration by period and day type, and whether its misses cluster in time

Terms such as candidate, cell, band, regime and B1' are defined in the [glossary](glossary.md). Issue numbers and files are in the Record at the end.

## The question

**Do the candidate's bands hold the share of outcomes they name, in every period and on every type of day, and do its misses come in runs?** The answer is evidence for the known-limits section of the registration and for the validation report.

## The answer

Over all cells of the development window the candidate's 90% band covers less than its nominal share and its 50% band is consistent with its nominal coverage. The groups where a band is off are listed below, largest gap first; the last paragraph says whether a miss makes another miss more likely.

**Development window, all cells (1859 target days).** The candidate covers the 50% band 47.4% [43.9%, 51.0%] (consistent) and the 90% band 87.5% [85.3%, 89.5%] (under-covers); B1' covers the 90% band 83.3% [80.2%, 86.2%]. Its q05 sits above 6.7% of outcomes (nominal 5.0%; quantile too high) and its q95 above 94.2% (nominal 95.0%; consistent).
On the 2026 days (shown apart, 169 target days) the 50% band covers 46.2% [36.2%, 55.7%] (consistent) and the 90% band 89.2% [82.4%, 94.3%] (consistent).

**Where a band is off on the development window** (candidate; the size in brackets is coverage less nominal; groups of 20 or more target days):

- regimes: 2018-19 50% band 42.5% (-7.5 pp, 361 days); 2025-26 50% band 43.0% (-7.0 pp, 249 days)
- day types: quarter_end 90% band 49.3% (-40.7 pp, 30 days); quarter_end 50% band 15.1% (-34.9 pp, 30 days); tax_date 50% band 33.5% (-16.5 pp, 89 days); iorb_window 90% band 73.8% (-16.2 pp, 78 days); iorb_window 50% band 35.9% (-14.1 pp, 78 days); month_end 50% band 36.5% (-13.5 pp, 180 days); post_month_end_window 50% band 37.0% (-13.0 pp, 267 days); fomc_day 50% band 37.1% (-12.9 pp, 118 days); month_end 90% band 78.2% (-11.8 pp, 180 days); post_month_end_window 90% band 78.3% (-11.7 pp, 267 days); coupon_settlement 50% band 40.1% (-9.9 pp, 242 days); coupon_settlement 90% band 80.2% (-9.8 pp, 242 days); fomc_day 90% band 83.9% (-6.1 pp, 118 days); bill_settlement 90% band 87.2% (-2.8 pp, 777 days); ordinary 90% band 92.5% (+2.5 pp, 507 days)
- pressure-day types: quarter_end_turn 50% band 15.0% (-35.0 pp, 44 days); quarter_end_turn 90% band 58.6% (-31.4 pp, 44 days); tax_date 50% band 33.5% (-16.5 pp, 89 days); turn 50% band 38.8% (-11.2 pp, 120 days); turn 90% band 83.3% (-6.7 pp, 120 days)

**Do misses follow misses?** Of the 40 hit sequences of the candidate (four events, two tie rules, five leads), 40 are read as serially dependent (Holm-adjusted permutation p below 0.05); inside regimes 200 of 200. After a miss of the 90% band the next day's miss chance at lead 1 is 42.1% against 7.8% after a hit; the longest run of band misses at lead 1 is 8 days. Sequences read as dependent among the 40 of each reference: B1 40, B1' 40, B2 40.

## Data

The candidate, (s3c-ann-net), at the 18:00 decision instant, walked unchanged, with B1, B1' and B2 beside it. The development window (decision days whose five targets are on or before 2025-12-31) decides what is said here; the 2026 days (targets 2026-01-02 to 2026-09-03) had already been seen by earlier studies, are shown apart and decide nothing.

## Method

**Intervals.** Intervals are 90% stationary-bootstrap percentile intervals of a rate (mean block 10 target days, 2000 resamples, seed 1363) over the group's target days in date order. This is the current method; it has been questioned and a ruling on it is pending, so no reading of a day-type group is a finding.

**Readings.** Groups of fewer than 20 target days are listed with their rates and not read. A band is read 'under-covers' or 'over-covers' when its interval lies wholly below or above the nominal; a quantile is read 'too high' when the interval of the share of outcomes strictly below it lies wholly above its level and 'too low' when the interval of the share at or below it lies wholly below. Nothing is corrected for the number of readings.

## The development window

1855 decision days (2018-07-19 to 2025-12-23), 9275 cells, last target 2025-12-31.

### Pooled and by lead

Each band cell gives the coverage, its 90% interval and the reading. Each quantile cell gives the share of outcomes strictly below the quantile and the share at or below it, to be compared with the quantile's level, and then the reading. The first table sets the candidate beside the benchmarks; the second splits the candidate by lead.

| group | target days | cells | model | 50% band | 90% band | q05 strict / at-or-below | q95 strict / at-or-below |
|---|---|---|---|---|---|---|---|
| all cells | 1859 | 9275 | (s3c-ann-net) | 47.4% [43.9%, 51.0%] consistent | 87.5% [85.3%, 89.5%] under-covers | 6.7% / 6.7% quantile too high | 94.2% / 94.2% consistent |
| all cells | 1859 | 9275 | B1 | 53.1% [48.7%, 57.6%] consistent | 84.3% [81.5%, 86.9%] under-covers | 7.5% / 8.7% quantile too high | 90.7% / 91.7% quantile too low |
| all cells | 1859 | 9275 | B1' | 53.1% [48.6%, 57.7%] consistent | 83.3% [80.2%, 86.2%] under-covers | 7.1% / 9.1% quantile too high | 89.2% / 90.4% quantile too low |
| all cells | 1859 | 9275 | B2 | 46.3% [41.0%, 51.4%] consistent | 80.6% [77.3%, 83.8%] under-covers | 8.7% / 23.8% quantile too high | 85.2% / 89.4% quantile too low |

| group | target days | cells | model | 50% band | 90% band | q05 strict / at-or-below | q95 strict / at-or-below |
|---|---|---|---|---|---|---|---|
| h=1 | 1855 | 1855 | (s3c-ann-net) | 48.0% [44.6%, 51.3%] consistent | 88.1% [86.1%, 90.0%] under-covers | 6.5% / 6.5% quantile too high | 94.6% / 94.6% consistent |
| h=2 | 1855 | 1855 | (s3c-ann-net) | 47.0% [43.5%, 50.5%] consistent | 87.9% [85.8%, 90.0%] consistent | 6.6% / 6.6% quantile too high | 94.5% / 94.5% consistent |
| h=3 | 1855 | 1855 | (s3c-ann-net) | 47.5% [43.8%, 51.3%] consistent | 87.3% [85.1%, 89.5%] under-covers | 7.0% / 7.0% quantile too high | 94.3% / 94.3% consistent |
| h=4 | 1855 | 1855 | (s3c-ann-net) | 47.7% [43.9%, 51.5%] consistent | 86.9% [84.4%, 89.2%] under-covers | 6.9% / 6.9% quantile too high | 93.8% / 93.8% consistent |
| h=5 | 1855 | 1855 | (s3c-ann-net) | 47.0% [43.2%, 50.9%] consistent | 87.2% [84.7%, 89.6%] under-covers | 6.7% / 6.7% consistent | 93.9% / 93.9% consistent |

### By regime of the target day

The same columns for all four models, one block per regime.

| group | target days | cells | model | 50% band | 90% band | q05 strict / at-or-below | q95 strict / at-or-below |
|---|---|---|---|---|---|---|---|
| 2018-19 | 361 | 1795 | (s3c-ann-net) | 42.5% [38.2%, 46.9%] under-covers | 86.7% [82.9%, 90.2%] consistent | 7.1% / 7.1% consistent | 93.8% / 93.8% consistent |
| 2018-19 | 361 | 1795 | B1 | 49.2% [43.3%, 55.7%] consistent | 82.5% [77.6%, 87.2%] under-covers | 8.6% / 9.1% quantile too high | 90.8% / 91.1% quantile too low |
| 2018-19 | 361 | 1795 | B1' | 49.7% [43.4%, 56.7%] consistent | 83.8% [79.1%, 88.6%] under-covers | 5.1% / 5.7% consistent | 88.0% / 88.9% quantile too low |
| 2018-19 | 361 | 1795 | B2 | 47.6% [37.8%, 56.2%] consistent | 79.7% [73.8%, 85.3%] under-covers | 2.8% / 4.5% consistent | 80.3% / 82.5% quantile too low |
| 2020 | 251 | 1255 | (s3c-ann-net) | 47.0% [38.2%, 56.2%] consistent | 86.5% [80.0%, 92.3%] consistent | 9.4% / 9.4% consistent | 95.9% / 95.9% consistent |
| 2020 | 251 | 1255 | B1 | 79.8% [73.2%, 85.5%] over-covers | 97.5% [93.8%, 100.0%] over-covers | 1.2% / 1.2% quantile too low | 98.6% / 98.6% quantile too high |
| 2020 | 251 | 1255 | B1' | 75.5% [68.5%, 81.8%] over-covers | 96.5% [91.5%, 99.9%] over-covers | 1.8% / 3.1% consistent | 98.3% / 98.3% quantile too high |
| 2020 | 251 | 1255 | B2 | 59.4% [41.8%, 75.1%] consistent | 86.9% [75.4%, 96.0%] consistent | 12.3% / 18.6% consistent | 98.8% / 99.2% quantile too high |
| 2021-23 | 748 | 3740 | (s3c-ann-net) | 51.8% [45.3%, 58.6%] consistent | 87.5% [83.4%, 91.4%] consistent | 6.3% / 6.3% consistent | 93.8% / 93.8% consistent |
| 2021-23 | 748 | 3740 | B1 | 59.1% [51.9%, 66.8%] over-covers | 88.5% [84.2%, 92.4%] consistent | 5.1% / 6.0% consistent | 92.7% / 93.5% consistent |
| 2021-23 | 748 | 3740 | B1' | 60.9% [53.7%, 68.6%] over-covers | 89.0% [84.8%, 92.8%] consistent | 4.6% / 6.5% consistent | 92.6% / 93.5% consistent |
| 2021-23 | 748 | 3740 | B2 | 44.7% [36.4%, 53.2%] consistent | 81.3% [76.1%, 86.2%] under-covers | 12.7% / 43.7% quantile too high | 89.3% / 94.0% consistent |
| 2024 | 250 | 1250 | (s3c-ann-net) | 46.4% [39.9%, 53.1%] consistent | 88.1% [83.4%, 92.2%] consistent | 6.6% / 6.6% consistent | 94.6% / 94.6% consistent |
| 2024 | 250 | 1250 | B1 | 43.3% [35.5%, 51.5%] consistent | 77.0% [69.3%, 84.2%] under-covers | 12.0% / 14.1% quantile too high | 86.3% / 89.0% quantile too low |
| 2024 | 250 | 1250 | B1' | 41.9% [33.4%, 51.3%] consistent | 75.0% [66.3%, 83.5%] under-covers | 11.3% / 14.2% quantile too high | 83.6% / 86.3% quantile too low |
| 2024 | 250 | 1250 | B2 | 53.5% [41.8%, 65.0%] consistent | 81.9% [73.8%, 89.5%] under-covers | 0.8% / 4.8% consistent | 71.6% / 82.7% quantile too low |
| 2025-26 | 249 | 1235 | (s3c-ann-net) | 43.0% [36.5%, 49.2%] under-covers | 89.1% [84.3%, 92.7%] consistent | 4.9% / 4.9% consistent | 94.1% / 94.1% consistent |
| 2025-26 | 249 | 1235 | B1 | 23.4% [19.4%, 26.9%] under-covers | 67.9% [62.0%, 73.7%] under-covers | 14.9% / 18.4% quantile too high | 81.2% / 82.8% quantile too low |
| 2025-26 | 249 | 1235 | B1' | 22.8% [19.0%, 26.2%] under-covers | 60.2% [54.8%, 65.4%] under-covers | 19.2% / 22.8% quantile too high | 77.3% / 79.4% quantile too low |
| 2025-26 | 249 | 1235 | B2 | 28.7% [18.5%, 38.2%] under-covers | 72.2% [63.0%, 80.5%] under-covers | 10.0% / 16.2% consistent | 79.6% / 82.2% quantile too low |

### By day type of the target day (the types overlap; ordinary is none of them)

These day types are calendar flags, and one day can carry several, so the rows do not add up to the whole. The candidate is shown beside B1'.

| group | target days | cells | model | 50% band | 90% band | q05 strict / at-or-below | q95 strict / at-or-below |
|---|---|---|---|---|---|---|---|
| quarter_end | 30 | 146 | (s3c-ann-net) | 15.1% [5.3%, 24.7%] under-covers | 49.3% [36.0%, 61.3%] under-covers | 16.4% / 16.4% consistent | 65.8% / 65.8% quantile too low |
| quarter_end | 30 | 146 | B1' | 35.6% [13.3%, 56.7%] consistent | 52.7% [28.7%, 74.7%] under-covers | 2.1% / 2.1% quantile too low | 54.1% / 54.8% quantile too low |
| month_end | 180 | 893 | (s3c-ann-net) | 36.5% [28.8%, 45.6%] under-covers | 78.2% [73.2%, 82.4%] under-covers | 10.2% / 10.2% quantile too high | 88.4% / 88.4% quantile too low |
| month_end | 180 | 893 | B1' | 43.6% [31.4%, 55.0%] consistent | 73.6% [64.3%, 82.4%] under-covers | 4.7% / 7.8% consistent | 76.1% / 78.3% quantile too low |
| tax_date | 89 | 445 | (s3c-ann-net) | 33.5% [26.7%, 40.2%] under-covers | 84.0% [76.9%, 91.0%] consistent | 8.3% / 8.3% consistent | 92.4% / 92.4% consistent |
| tax_date | 89 | 445 | B1' | 51.2% [36.9%, 67.6%] consistent | 81.6% [73.5%, 89.9%] under-covers | 5.8% / 6.1% consistent | 85.8% / 87.4% quantile too low |
| coupon_settlement | 242 | 1205 | (s3c-ann-net) | 40.1% [34.5%, 46.2%] under-covers | 80.2% [75.6%, 84.2%] under-covers | 6.4% / 6.4% consistent | 86.6% / 86.6% quantile too low |
| coupon_settlement | 242 | 1205 | B1' | 45.2% [33.2%, 57.8%] consistent | 74.0% [65.0%, 82.7%] under-covers | 3.2% / 6.2% consistent | 75.4% / 77.3% quantile too low |
| bill_settlement | 777 | 3881 | (s3c-ann-net) | 45.9% [41.8%, 50.5%] consistent | 87.2% [84.5%, 89.7%] under-covers | 6.4% / 6.4% consistent | 93.7% / 93.7% consistent |
| bill_settlement | 777 | 3881 | B1' | 51.9% [45.5%, 58.3%] consistent | 82.5% [78.4%, 86.5%] under-covers | 6.5% / 8.3% consistent | 87.9% / 89.1% quantile too low |
| fomc_day | 118 | 590 | (s3c-ann-net) | 37.1% [30.2%, 44.6%] under-covers | 83.9% [78.0%, 89.5%] under-covers | 8.8% / 8.8% quantile too high | 92.7% / 92.7% consistent |
| fomc_day | 118 | 590 | B1' | 54.1% [43.1%, 67.1%] consistent | 78.6% [71.5%, 86.9%] under-covers | 9.5% / 11.2% consistent | 87.5% / 88.1% quantile too low |
| iorb_window | 78 | 390 | (s3c-ann-net) | 35.9% [28.5%, 43.1%] under-covers | 73.8% [67.4%, 80.8%] under-covers | 17.7% / 17.7% quantile too high | 91.5% / 91.5% consistent |
| iorb_window | 78 | 390 | B1' | 39.5% [29.7%, 49.2%] under-covers | 75.9% [67.9%, 83.3%] under-covers | 12.1% / 13.3% quantile too high | 86.4% / 87.9% quantile too low |
| dom_19_23 | 305 | 1518 | (s3c-ann-net) | 45.9% [40.2%, 51.5%] consistent | 90.1% [86.2%, 93.9%] consistent | 9.2% / 9.2% quantile too high | 99.2% / 99.2% quantile too high |
| dom_19_23 | 305 | 1518 | B1' | 55.1% [47.4%, 63.5%] consistent | 87.5% [83.1%, 91.8%] consistent | 11.0% / 14.0% quantile too high | 98.2% / 98.5% quantile too high |
| post_month_end_window | 267 | 1335 | (s3c-ann-net) | 37.0% [29.4%, 45.4%] under-covers | 78.3% [73.2%, 83.4%] under-covers | 9.1% / 9.1% quantile too high | 87.4% / 87.4% quantile too low |
| post_month_end_window | 267 | 1335 | B1' | 47.4% [38.8%, 56.6%] consistent | 78.1% [71.5%, 84.9%] under-covers | 5.3% / 8.2% consistent | 82.2% / 83.4% quantile too low |
| ordinary | 507 | 2530 | (s3c-ann-net) | 55.0% [49.8%, 60.8%] consistent | 92.5% [90.3%, 94.4%] over-covers | 4.3% / 4.3% consistent | 96.8% / 96.8% quantile too high |
| ordinary | 507 | 2530 | B1' | 57.0% [50.0%, 64.2%] over-covers | 87.0% [82.9%, 90.9%] consistent | 7.2% / 8.6% quantile too high | 93.0% / 94.2% consistent |

### By pressure-day type of the target day

The same comparison on the pressure-day labels the quarter-end studies use.

| group | target days | cells | model | 50% band | 90% band | q05 strict / at-or-below | q95 strict / at-or-below |
|---|---|---|---|---|---|---|---|
| ordinary | 1591 | 7939 | (s3c-ann-net) | 49.8% [46.2%, 53.6%] consistent | 89.0% [86.6%, 91.1%] consistent | 6.6% / 6.6% quantile too high | 95.6% / 95.6% consistent |
| ordinary | 1591 | 7939 | B1' | 54.4% [49.7%, 59.3%] consistent | 84.7% [81.5%, 87.8%] under-covers | 7.6% / 9.1% quantile too high | 91.0% / 92.2% quantile too low |
| quarter_end_turn | 44 | 220 | (s3c-ann-net) | 15.0% [8.2%, 22.3%] under-covers | 58.6% [46.8%, 70.5%] under-covers | 7.7% / 7.7% consistent | 66.4% / 66.4% quantile too low |
| quarter_end_turn | 44 | 220 | B1' | 32.7% [12.3%, 53.7%] consistent | 59.1% [41.4%, 76.8%] under-covers | 1.8% / 1.8% quantile too low | 59.1% / 60.9% quantile too low |
| tax_date | 89 | 445 | (s3c-ann-net) | 33.5% [26.7%, 40.2%] under-covers | 84.0% [76.9%, 91.0%] consistent | 8.3% / 8.3% consistent | 92.4% / 92.4% consistent |
| tax_date | 89 | 445 | B1' | 51.2% [36.9%, 67.6%] consistent | 81.6% [73.5%, 89.9%] under-covers | 5.8% / 6.1% consistent | 85.8% / 87.4% quantile too low |
| turn | 120 | 600 | (s3c-ann-net) | 38.8% [31.7%, 47.2%] under-covers | 83.3% [79.2%, 87.5%] under-covers | 5.7% / 5.7% consistent | 89.0% / 89.0% quantile too low |
| turn | 120 | 600 | B1' | 45.5% [35.8%, 56.8%] consistent | 77.5% [68.8%, 86.5%] under-covers | 4.8% / 14.0% consistent | 81.8% / 82.3% quantile too low |
| year_end | 15 | 71 | (s3c-ann-net) | 42.3% not tested | 64.8% not tested | 12.7% / 12.7% not tested | 77.5% / 77.5% not tested |
| year_end | 15 | 71 | B1' | 47.9% not tested | 62.0% not tested | 4.2% / 4.2% not tested | 66.2% / 66.2% not tested |

### Every grid quantile, all cells (candidate)

For a calibrated model each share, read as a fraction, equals the level in the first column.

| level | share strictly below | share at or below |
|---|---|---|
| 0.01 | 1.94% | 1.94% |
| 0.025 | 3.90% | 3.90% |
| 0.05 | 6.73% | 6.73% |
| 0.1 | 12.42% | 12.47% |
| 0.15 | 17.66% | 17.67% |
| 0.2 | 22.66% | 22.70% |
| 0.25 | 27.09% | 27.31% |
| 0.3 | 31.45% | 31.60% |
| 0.35 | 36.95% | 37.06% |
| 0.4 | 41.81% | 41.90% |
| 0.45 | 46.04% | 47.83% |
| 0.5 | 49.10% | 54.19% |
| 0.55 | 55.00% | 57.40% |
| 0.6 | 59.77% | 61.23% |
| 0.65 | 65.11% | 65.15% |
| 0.7 | 69.13% | 69.21% |
| 0.75 | 73.99% | 74.53% |
| 0.8 | 79.39% | 79.67% |
| 0.85 | 83.65% | 83.68% |
| 0.9 | 89.10% | 89.12% |
| 0.95 | 94.21% | 94.21% |
| 0.975 | 96.86% | 96.86% |
| 0.99 | 98.38% | 98.38% |

### Randomized PIT (seed 1363; the range is over seeds 1364 to 1383)

The PIT is the probability the forecast gave to outcomes at or below the one that happened; it is randomized where the outcome ties a quantile. For a calibrated model the six bins hold ten, fifteen, twenty-five, twenty-five, fifteen and ten percent of the cells. The last two columns give the two outer bins with their range over 20 other seeds, which shows how far the randomization moves them.

pooled, candidate:

| group | cells | bins (≤0.10, ≤0.25, ≤0.50, ≤0.75, ≤0.90, >0.90) | ≤0.10 (20 other seeds) | ≥0.90 (20 other seeds) |
|---|---|---|---|---|
| all cells | 9275 | 12.5 14.7 24.4 22.8 14.8 10.9 | 12.5% (12.4% to 12.5%) | 10.9% (10.9% to 10.9%) |

regime, candidate:

| group | cells | bins (≤0.10, ≤0.25, ≤0.50, ≤0.75, ≤0.90, >0.90) | ≤0.10 (20 other seeds) | ≥0.90 (20 other seeds) |
|---|---|---|---|---|
| 2018-19 | 1795 | 13.9 16.8 19.9 22.6 16.5 10.3 | 13.9% (13.9% to 13.9%) | 10.3% (10.3% to 10.3%) |
| 2020 | 1255 | 17.5 11.3 21.6 25.4 15.2 9.0 | 17.5% (17.5% to 17.5%) | 9.0% (9.0% to 9.0%) |
| 2021-23 | 3740 | 11.2 14.4 28.0 23.1 12.1 11.1 | 11.2% (11.2% to 11.3%) | 11.1% (11.0% to 11.1%) |
| 2024 | 1250 | 12.4 13.2 21.9 24.1 17.0 11.4 | 12.4% (12.3% to 12.5%) | 11.4% (11.4% to 11.4%) |
| 2025-26 | 1235 | 9.0 17.7 23.7 19.3 17.8 12.6 | 9.0% (9.0% to 9.0%) | 12.6% (12.6% to 12.6%) |

target_day_type, candidate:

| group | cells | bins (≤0.10, ≤0.25, ≤0.50, ≤0.75, ≤0.90, >0.90) | ≤0.10 (20 other seeds) | ≥0.90 (20 other seeds) |
|---|---|---|---|---|
| quarter_end | 146 | 19.2 12.3 10.3 4.8 12.3 41.1 | 19.2% (19.2% to 19.2%) | 41.1% (41.1% to 41.1%) |
| month_end | 893 | 16.0 13.3 18.0 18.5 14.0 20.2 | 16.0% (16.0% to 16.0%) | 20.2% (20.2% to 20.2%) |
| tax_date | 445 | 14.4 16.4 16.6 16.9 17.8 18.0 | 14.4% (14.4% to 14.4%) | 18.0% (18.0% to 18.0%) |
| coupon_settlement | 1205 | 9.2 11.7 24.2 15.9 17.9 21.1 | 9.2% (9.2% to 9.2%) | 21.1% (21.1% to 21.1%) |
| bill_settlement | 3881 | 11.8 14.4 23.5 22.3 16.1 11.9 | 11.8% (11.8% to 11.8%) | 11.9% (11.9% to 11.9%) |
| fomc_day | 590 | 17.5 17.5 21.9 14.6 15.4 13.2 | 17.5% (17.5% to 17.5%) | 13.2% (13.2% to 13.2%) |
| iorb_window | 390 | 22.1 15.6 18.5 16.9 13.8 13.1 | 22.1% (22.1% to 22.1%) | 13.1% (13.1% to 13.1%) |
| dom_19_23 | 1518 | 13.3 16.9 15.3 29.1 21.0 4.4 | 13.3% (13.3% to 13.3%) | 4.4% (4.4% to 4.4%) |
| post_month_end_window | 1335 | 16.1 15.1 24.0 12.2 14.0 18.5 | 16.1% (16.1% to 16.1%) | 18.5% (18.5% to 18.5%) |
| ordinary | 2530 | 11.0 14.5 28.7 26.1 11.9 7.7 | 11.0% (10.9% to 11.1%) | 7.7% (7.7% to 7.7%) |

pressure_day_type, candidate:

| group | cells | bins (≤0.10, ≤0.25, ≤0.50, ≤0.75, ≤0.90, >0.90) | ≤0.10 (20 other seeds) | ≥0.90 (20 other seeds) |
|---|---|---|---|---|
| ordinary | 7939 | 12.6 14.8 25.1 24.3 14.3 8.9 | 12.6% (12.6% to 12.6%) | 8.9% (8.8% to 8.9%) |
| quarter_end_turn | 220 | 11.4 13.6 9.1 5.9 15.9 44.1 | 11.4% (11.4% to 11.4%) | 44.1% (44.1% to 44.1%) |
| tax_date | 445 | 14.4 16.4 16.6 16.9 17.8 18.0 | 14.4% (14.4% to 14.4%) | 18.0% (18.0% to 18.0%) |
| turn | 600 | 9.2 14.5 23.7 15.0 19.2 18.5 | 9.2% (9.2% to 9.2%) | 18.5% (18.5% to 18.5%) |
| year_end | 71 | 14.1 5.6 28.2 14.1 9.9 28.2 | 14.1% (14.1% to 14.1%) | 28.2% (28.2% to 28.2%) |

pooled, the references:

B1:

| group | cells | bins (≤0.10, ≤0.25, ≤0.50, ≤0.75, ≤0.90, >0.90) | ≤0.10 (20 other seeds) | ≥0.90 (20 other seeds) |
|---|---|---|---|---|
| all cells | 9275 | 12.8 13.5 23.5 23.6 12.9 13.7 | 12.8% (12.7% to 13.0%) | 13.7% (13.6% to 13.9%) |

B1':

| group | cells | bins (≤0.10, ≤0.25, ≤0.50, ≤0.75, ≤0.90, >0.90) | ≤0.10 (20 other seeds) | ≥0.90 (20 other seeds) |
|---|---|---|---|---|
| all cells | 9275 | 12.1 13.2 22.6 23.3 13.3 15.5 | 12.1% (12.0% to 12.3%) | 15.5% (15.5% to 15.8%) |

B2:

| group | cells | bins (≤0.10, ≤0.25, ≤0.50, ≤0.75, ≤0.90, >0.90) | ≤0.10 (20 other seeds) | ≥0.90 (20 other seeds) |
|---|---|---|---|---|
| all cells | 9275 | 19.4 12.1 16.7 20.8 12.6 18.5 | 19.4% (18.9% to 19.6%) | 18.5% (18.4% to 18.9%) |

### Readings that are not 'consistent' (candidate)

The full list behind the summary in the answer, largest first.

80 of 225 readings in tested groups. Sizes are observed less nominal for a band, distance of the level from [strict, at-or-below] for a quantile.

| split | group | target days | what | reading | size |
|---|---|---|---|---|---|
| target_day_type | quarter_end | 30 | 90% band | under-covers | -40.7 pp |
| pressure_day_type | quarter_end_turn | 44 | 50% band | under-covers | -35.0 pp |
| pressure_day_type | quarter_end_turn | 44 | q0.75 | quantile too low | -35.0 pp |
| target_day_type | quarter_end | 30 | 50% band | under-covers | -34.9 pp |
| pressure_day_type | quarter_end_turn | 44 | 90% band | under-covers | -31.4 pp |
| target_day_type | quarter_end | 30 | q0.95 | quantile too low | -29.2 pp |
| pressure_day_type | quarter_end_turn | 44 | q0.95 | quantile too low | -28.6 pp |
| target_day_type | quarter_end | 30 | q0.75 | quantile too low | -28.4 pp |
| target_day_type | tax_date | 89 | 50% band | under-covers | -16.5 pp |
| pressure_day_type | tax_date | 89 | 50% band | under-covers | -16.5 pp |
| target_day_type | iorb_window | 78 | 90% band | under-covers | -16.2 pp |
| target_day_type | iorb_window | 78 | 50% band | under-covers | -14.1 pp |
| target_day_type | coupon_settlement | 242 | q0.75 | quantile too low | -14.0 pp |
| target_day_type | month_end | 180 | 50% band | under-covers | -13.5 pp |
| target_day_type | post_month_end_window | 267 | 50% band | under-covers | -13.0 pp |
| target_day_type | fomc_day | 118 | 50% band | under-covers | -12.9 pp |
| target_day_type | quarter_end | 30 | q0.99 | quantile too low | -12.7 pp |
| target_day_type | iorb_window | 78 | q0.05 | quantile too high | +12.7 pp |
| target_day_type | iorb_window | 78 | q0.25 | quantile too high | +12.2 pp |
| target_day_type | month_end | 180 | 90% band | under-covers | -11.8 pp |
| target_day_type | post_month_end_window | 267 | 90% band | under-covers | -11.7 pp |
| pressure_day_type | turn | 120 | 50% band | under-covers | -11.2 pp |
| target_day_type | coupon_settlement | 242 | 50% band | under-covers | -9.9 pp |
| target_day_type | fomc_day | 118 | q0.25 | quantile too high | +9.9 pp |
| pressure_day_type | quarter_end_turn | 44 | q0.99 | quantile too low | -9.9 pp |
| target_day_type | coupon_settlement | 242 | 90% band | under-covers | -9.8 pp |
| target_day_type | coupon_settlement | 242 | q0.95 | quantile too low | -8.4 pp |
| target_day_type | post_month_end_window | 267 | q0.95 | quantile too low | -7.6 pp |
| regime | 2018-19 | 361 | 50% band | under-covers | -7.5 pp |
| target_day_type | post_month_end_window | 267 | q0.75 | quantile too low | -7.5 pp |
| regime | 2025-26 | 249 | 50% band | under-covers | -7.0 pp |
| pressure_day_type | turn | 120 | 90% band | under-covers | -6.7 pp |
| target_day_type | month_end | 180 | q0.95 | quantile too low | -6.6 pp |
| target_day_type | fomc_day | 118 | 90% band | under-covers | -6.1 pp |
| pressure_day_type | turn | 120 | q0.95 | quantile too low | -6.0 pp |
| target_day_type | iorb_window | 78 | q0.01 | quantile too high | +5.7 pp |
| target_day_type | ordinary | 507 | q0.75 | quantile too high | +5.3 pp |
| target_day_type | month_end | 180 | q0.05 | quantile too high | +5.2 pp |
| target_day_type | dom_19_23 | 305 | q0.95 | quantile too high | +4.2 pp |
| target_day_type | dom_19_23 | 305 | q0.05 | quantile too high | +4.2 pp |
| target_day_type | post_month_end_window | 267 | q0.05 | quantile too high | +4.1 pp |
| target_day_type | month_end | 180 | q0.99 | quantile too low | -3.8 pp |
| target_day_type | fomc_day | 118 | q0.05 | quantile too high | +3.8 pp |
| target_day_type | coupon_settlement | 242 | q0.99 | quantile too low | -3.5 pp |
| lead | h=4 | 1855 | 90% band | under-covers | -3.1 pp |
| target_day_type | bill_settlement | 777 | 90% band | under-covers | -2.8 pp |
| lead | h=5 | 1855 | 90% band | under-covers | -2.8 pp |
| lead | h=3 | 1855 | 90% band | under-covers | -2.7 pp |
| target_day_type | month_end | 180 | q0.01 | quantile too high | +2.6 pp |
| lead | h=2 | 1855 | q0.25 | quantile too high | +2.5 pp |
| pooled | all cells | 1859 | 90% band | under-covers | -2.5 pp |
| target_day_type | ordinary | 507 | 90% band | over-covers | +2.5 pp |
| target_day_type | post_month_end_window | 267 | q0.99 | quantile too low | -2.1 pp |
| target_day_type | dom_19_23 | 305 | q0.01 | quantile too high | +2.0 pp |
| lead | h=3 | 1855 | q0.05 | quantile too high | +2.0 pp |
| lead | h=1 | 1855 | 90% band | under-covers | -1.9 pp |
| lead | h=4 | 1855 | q0.05 | quantile too high | +1.9 pp |
| target_day_type | ordinary | 507 | q0.95 | quantile too high | +1.8 pp |
| pooled | all cells | 1859 | q0.05 | quantile too high | +1.7 pp |
| pressure_day_type | ordinary | 1591 | q0.05 | quantile too high | +1.6 pp |
| lead | h=2 | 1855 | q0.05 | quantile too high | +1.6 pp |
| regime | 2020 | 251 | q0.01 | quantile too high | +1.6 pp |
| lead | h=1 | 1855 | q0.05 | quantile too high | +1.5 pp |
| regime | 2021-23 | 748 | q0.01 | quantile too high | +1.3 pp |
| target_day_type | post_month_end_window | 267 | q0.01 | quantile too high | +1.2 pp |
| regime | 2021-23 | 748 | q0.99 | quantile too low | -1.2 pp |
| target_day_type | bill_settlement | 777 | q0.99 | quantile too low | -1.1 pp |
| target_day_type | bill_settlement | 777 | q0.01 | quantile too high | +1.1 pp |
| lead | h=3 | 1855 | q0.01 | quantile too high | +1.0 pp |
| lead | h=4 | 1855 | q0.01 | quantile too high | +1.0 pp |
| lead | h=5 | 1855 | q0.01 | quantile too high | +1.0 pp |
| target_day_type | dom_19_23 | 305 | q0.99 | quantile too high | +1.0 pp |
| pooled | all cells | 1859 | q0.01 | quantile too high | +0.9 pp |
| pressure_day_type | ordinary | 1591 | q0.01 | quantile too high | +0.9 pp |
| lead | h=1 | 1855 | q0.01 | quantile too high | +0.8 pp |
| lead | h=2 | 1855 | q0.01 | quantile too high | +0.8 pp |
| lead | h=5 | 1855 | q0.99 | quantile too low | -0.7 pp |
| lead | h=1 | 1855 | q0.99 | quantile too low | -0.7 pp |
| pooled | all cells | 1859 | q0.99 | quantile too low | -0.6 pp |
| lead | h=2 | 1855 | q0.99 | quantile too low | -0.6 pp |

### Do the misses cluster in time?

A hit sequence records, day by day, whether the outcome fell outside a quantile or a band. If misses were independent, a miss would be no more likely after a miss than after a hit. The first table counts, for each model, how many of its sequences are read as serially dependent; the table after it gives the detail.

Christoffersen's independence test on each lead's sequence over the scored decision days (no transition across a gap or, for the regime rows, a regime change); the permutation p is the reading, Holm-adjusted at 0.05 over the 40 sequences of a model and window (per regime for the regime rows).

| model | sequences (all days) | clustered by Holm | sequences inside regimes | clustered by Holm |
|---|---|---|---|---|
| (s3c-ann-net) | 40 | 40 | 200 | 200 |
| B1 | 40 | 40 | 200 | 160 |
| B1' | 40 | 40 | 200 | 184 |
| B2 | 40 | 40 | 200 | 190 |

| model | lead | sequence | misses (rate) | P(miss after miss) | P(miss after hit) | longest run | LR p (asymptotic) | p (permutation) | clusters (Holm) |
|---|---|---|---|---|---|---|---|---|---|
| (s3c-ann-net) | 1 | upper/strict | 101 (5.4%) | 38.6% | 3.5% | 5 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 1 | lower/strict | 120 (6.5%) | 38.3% | 4.3% | 7 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 1 | band90/strict | 221 (11.9%) | 42.1% | 7.8% | 8 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 1 | band50/strict | 965 (52.0%) | 68.8% | 33.9% | 24 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 2 | upper/strict | 102 (5.5%) | 46.5% | 3.1% | 6 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 2 | lower/strict | 123 (6.6%) | 48.8% | 3.6% | 9 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 2 | band90/strict | 225 (12.1%) | 49.6% | 7.0% | 9 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 2 | band50/strict | 983 (53.0%) | 71.3% | 32.5% | 36 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 3 | upper/strict | 106 (5.7%) | 48.6% | 3.1% | 6 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 3 | lower/strict | 129 (7.0%) | 57.4% | 3.2% | 9 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 3 | band90/strict | 235 (12.7%) | 53.8% | 6.7% | 9 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 3 | band50/strict | 973 (52.5%) | 70.9% | 32.2% | 25 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 4 | upper/strict | 115 (6.2%) | 54.8% | 3.0% | 10 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 4 | lower/strict | 128 (6.9%) | 59.4% | 3.0% | 9 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 4 | band90/strict | 243 (13.1%) | 57.6% | 6.4% | 10 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 4 | band50/strict | 971 (52.3%) | 72.3% | 30.4% | 25 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 5 | upper/strict | 113 (6.1%) | 58.9% | 2.7% | 9 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 5 | lower/strict | 124 (6.7%) | 61.3% | 2.8% | 11 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 5 | band90/strict | 237 (12.8%) | 61.0% | 5.7% | 11 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 5 | band50/strict | 983 (53.0%) | 73.3% | 30.2% | 33 | 0.0000 | 0.0001 | yes |
| B1' | 1 | upper/strict | 214 (11.5%) | 47.7% | 6.8% | 5 | 0.0000 | 0.0001 | yes |
| B1' | 1 | lower/strict | 179 (9.6%) | 44.1% | 6.0% | 4 | 0.0000 | 0.0001 | yes |
| B1' | 1 | band90/strict | 393 (21.2%) | 54.7% | 12.2% | 11 | 0.0000 | 0.0001 | yes |
| B1' | 1 | band50/strict | 928 (50.0%) | 72.0% | 28.2% | 38 | 0.0000 | 0.0001 | yes |
| B1' | 2 | upper/strict | 167 (9.0%) | 47.0% | 5.3% | 4 | 0.0000 | 0.0001 | yes |
| B1' | 2 | lower/strict | 138 (7.4%) | 44.9% | 4.4% | 8 | 0.0000 | 0.0001 | yes |
| B1' | 2 | band90/strict | 305 (16.4%) | 49.3% | 10.0% | 13 | 0.0000 | 0.0001 | yes |
| B1' | 2 | band50/strict | 873 (47.1%) | 72.1% | 24.8% | 21 | 0.0000 | 0.0001 | yes |
| B1' | 3 | upper/strict | 161 (8.7%) | 51.9% | 4.6% | 9 | 0.0000 | 0.0001 | yes |
| B1' | 3 | lower/strict | 115 (6.2%) | 47.0% | 3.5% | 8 | 0.0000 | 0.0001 | yes |
| B1' | 3 | band90/strict | 276 (14.9%) | 52.0% | 8.4% | 14 | 0.0000 | 0.0001 | yes |
| B1' | 3 | band50/strict | 865 (46.6%) | 70.0% | 26.3% | 33 | 0.0000 | 0.0001 | yes |
| B1' | 4 | upper/strict | 166 (8.9%) | 53.0% | 4.6% | 9 | 0.0000 | 0.0001 | yes |
| B1' | 4 | lower/strict | 121 (6.5%) | 53.7% | 3.2% | 9 | 0.0000 | 0.0001 | yes |
| B1' | 4 | band90/strict | 287 (15.5%) | 56.8% | 7.9% | 11 | 0.0000 | 0.0001 | yes |
| B1' | 4 | band50/strict | 847 (45.7%) | 73.8% | 22.1% | 23 | 0.0000 | 0.0001 | yes |
| B1' | 5 | upper/strict | 180 (9.7%) | 54.2% | 5.0% | 9 | 0.0000 | 0.0001 | yes |
| B1' | 5 | lower/strict | 110 (5.9%) | 52.7% | 3.0% | 10 | 0.0000 | 0.0001 | yes |
| B1' | 5 | band90/strict | 290 (15.6%) | 56.1% | 8.2% | 16 | 0.0000 | 0.0001 | yes |
| B1' | 5 | band50/strict | 838 (45.2%) | 74.8% | 20.8% | 34 | 0.0000 | 0.0001 | yes |
| B2 | 1 | upper/strict | 190 (10.2%) | 56.3% | 5.0% | 11 | 0.0000 | 0.0001 | yes |
| B2 | 1 | lower/strict | 156 (8.4%) | 72.4% | 2.5% | 17 | 0.0000 | 0.0001 | yes |
| B2 | 1 | band90/strict | 346 (18.7%) | 63.6% | 8.4% | 17 | 0.0000 | 0.0001 | yes |
| B2 | 1 | band50/strict | 984 (53.0%) | 82.2% | 20.1% | 78 | 0.0000 | 0.0001 | yes |
| B2 | 2 | upper/strict | 194 (10.5%) | 58.0% | 4.9% | 11 | 0.0000 | 0.0001 | yes |
| B2 | 2 | lower/strict | 159 (8.6%) | 74.2% | 2.4% | 17 | 0.0000 | 0.0001 | yes |
| B2 | 2 | band90/strict | 353 (19.0%) | 65.3% | 8.2% | 17 | 0.0000 | 0.0001 | yes |
| B2 | 2 | band50/strict | 992 (53.5%) | 82.3% | 20.3% | 79 | 0.0000 | 0.0001 | yes |
| B2 | 3 | upper/strict | 197 (10.6%) | 58.2% | 5.0% | 11 | 0.0000 | 0.0001 | yes |
| B2 | 3 | lower/strict | 161 (8.7%) | 74.5% | 2.4% | 18 | 0.0000 | 0.0001 | yes |
| B2 | 3 | band90/strict | 358 (19.3%) | 65.5% | 8.3% | 18 | 0.0000 | 0.0001 | yes |
| B2 | 3 | band50/strict | 995 (53.6%) | 82.5% | 20.3% | 80 | 0.0000 | 0.0001 | yes |
| B2 | 4 | upper/strict | 201 (10.8%) | 58.7% | 5.0% | 16 | 0.0000 | 0.0001 | yes |
| B2 | 4 | lower/strict | 166 (8.9%) | 76.5% | 2.3% | 25 | 0.0000 | 0.0001 | yes |
| B2 | 4 | band90/strict | 367 (19.8%) | 66.8% | 8.2% | 25 | 0.0000 | 0.0001 | yes |
| B2 | 4 | band50/strict | 1002 (54.0%) | 82.5% | 20.5% | 148 | 0.0000 | 0.0001 | yes |
| B2 | 5 | upper/strict | 205 (11.1%) | 59.3% | 5.1% | 16 | 0.0000 | 0.0001 | yes |
| B2 | 5 | lower/strict | 169 (9.1%) | 76.3% | 2.4% | 25 | 0.0000 | 0.0001 | yes |
| B2 | 5 | band90/strict | 374 (20.2%) | 67.0% | 8.4% | 25 | 0.0000 | 0.0001 | yes |
| B2 | 5 | band50/strict | 1007 (54.3%) | 82.9% | 20.4% | 149 | 0.0000 | 0.0001 | yes |

#### The protocol's own reading (thinned: every h-th decision day at lead h; regime of the decision day), q05 and q95, strict rule

These are the two tests the scoring protocol applies: a Kupiec test of the hit rate and an independence test, each with its p-value.

| model | lead | level | regime | n | hits | Kupiec p | independence p |
|---|---|---|---|---|---|---|---|
| (s3c-ann-net) | 1 | q0.05 | 2018-19 | 362 | 31 | 0.005 | 0.000 |
| (s3c-ann-net) | 1 | q0.95 | 2018-19 | 362 | 19 | 0.829 | 0.000 |
| (s3c-ann-net) | 1 | q0.05 | 2020 | 251 | 19 | 0.081 | 0.001 |
| (s3c-ann-net) | 1 | q0.95 | 2020 | 251 | 10 | 0.445 | 0.004 |
| (s3c-ann-net) | 1 | q0.05 | 2021-23 | 748 | 43 | 0.358 | 0.000 |
| (s3c-ann-net) | 1 | q0.95 | 2021-23 | 748 | 43 | 0.358 | 0.000 |
| (s3c-ann-net) | 1 | q0.05 | 2024 | 250 | 18 | 0.133 | 0.000 |
| (s3c-ann-net) | 1 | q0.95 | 2024 | 250 | 15 | 0.481 | 0.007 |
| (s3c-ann-net) | 1 | q0.05 | 2025-26 | 244 | 9 | 0.325 | 0.025 |
| (s3c-ann-net) | 1 | q0.95 | 2025-26 | 244 | 14 | 0.605 | 0.000 |
| (s3c-ann-net) | 2 | q0.05 | 2018-19 | 181 | 11 | 0.519 | 0.689 |
| (s3c-ann-net) | 2 | q0.95 | 2018-19 | 181 | 9 | 0.986 | 0.330 |
| (s3c-ann-net) | 2 | q0.05 | 2020 | 126 | 13 | 0.016 | 0.029 |
| (s3c-ann-net) | 2 | q0.95 | 2020 | 126 | 7 | 0.778 | 0.002 |
| (s3c-ann-net) | 2 | q0.05 | 2021-23 | 374 | 23 | 0.324 | 0.000 |
| (s3c-ann-net) | 2 | q0.95 | 2021-23 | 374 | 20 | 0.760 | 0.392 |
| (s3c-ann-net) | 2 | q0.05 | 2024 | 125 | 8 | 0.490 | 0.382 |
| (s3c-ann-net) | 2 | q0.95 | 2024 | 125 | 8 | 0.490 | 0.078 |
| (s3c-ann-net) | 2 | q0.05 | 2025-26 | 122 | 6 | 0.967 | 0.471 |
| (s3c-ann-net) | 2 | q0.95 | 2025-26 | 122 | 7 | 0.715 | 0.030 |
| (s3c-ann-net) | 3 | q0.05 | 2018-19 | 121 | 9 | 0.250 | 0.142 |
| (s3c-ann-net) | 3 | q0.95 | 2018-19 | 121 | 8 | 0.437 | 0.084 |
| (s3c-ann-net) | 3 | q0.05 | 2020 | 84 | 8 | 0.089 | 0.781 |
| (s3c-ann-net) | 3 | q0.95 | 2020 | 84 | 2 | 0.222 | 0.753 |
| (s3c-ann-net) | 3 | q0.05 | 2021-23 | 249 | 17 | 0.209 | 0.000 |
| (s3c-ann-net) | 3 | q0.95 | 2021-23 | 249 | 14 | 0.658 | 0.809 |
| (s3c-ann-net) | 3 | q0.05 | 2024 | 83 | 7 | 0.189 | 0.068 |
| (s3c-ann-net) | 3 | q0.95 | 2024 | 83 | 5 | 0.678 | 0.420 |
| (s3c-ann-net) | 3 | q0.05 | 2025-26 | 82 | 4 | 0.959 | 0.578 |
| (s3c-ann-net) | 3 | q0.95 | 2025-26 | 82 | 5 | 0.659 | 0.208 |
| (s3c-ann-net) | 4 | q0.05 | 2018-19 | 91 | 8 | 0.132 | 0.017 |
| (s3c-ann-net) | 4 | q0.95 | 2018-19 | 91 | 4 | 0.787 | 0.542 |
| (s3c-ann-net) | 4 | q0.05 | 2020 | 63 | 5 | 0.323 | 0.349 |
| (s3c-ann-net) | 4 | q0.95 | 2020 | 63 | 4 | 0.637 | 0.213 |
| (s3c-ann-net) | 4 | q0.05 | 2021-23 | 187 | 12 | 0.393 | 0.023 |
| (s3c-ann-net) | 4 | q0.95 | 2021-23 | 187 | 11 | 0.590 | 0.001 |
| (s3c-ann-net) | 4 | q0.05 | 2024 | 62 | 3 | 0.953 | 0.651 |
| (s3c-ann-net) | 4 | q0.95 | 2024 | 62 | 3 | 0.953 | 0.577 |
| (s3c-ann-net) | 4 | q0.05 | 2025-26 | 61 | 4 | 0.594 | 0.449 |
| (s3c-ann-net) | 4 | q0.95 | 2025-26 | 61 | 6 | 0.124 | 0.294 |
| (s3c-ann-net) | 5 | q0.05 | 2018-19 | 73 | 4 | 0.853 | 0.179 |
| (s3c-ann-net) | 5 | q0.95 | 2018-19 | 73 | 5 | 0.491 | 0.387 |
| (s3c-ann-net) | 5 | q0.05 | 2020 | 50 | 7 | 0.016 | 0.040 |
| (s3c-ann-net) | 5 | q0.95 | 2020 | 50 | 2 | 0.737 | 0.680 |
| (s3c-ann-net) | 5 | q0.05 | 2021-23 | 150 | 9 | 0.585 | 0.092 |
| (s3c-ann-net) | 5 | q0.95 | 2021-23 | 150 | 12 | 0.120 | 0.305 |
| (s3c-ann-net) | 5 | q0.05 | 2024 | 50 | 4 | 0.369 | 0.467 |
| (s3c-ann-net) | 5 | q0.95 | 2024 | 50 | 2 | 0.737 | 0.680 |
| (s3c-ann-net) | 5 | q0.05 | 2025-26 | 48 | 1 | 0.296 | 0.835 |
| (s3c-ann-net) | 5 | q0.95 | 2025-26 | 48 | 3 | 0.702 | 0.136 |
| B1' | 1 | q0.05 | 2018-19 | 362 | 28 | 0.027 | 0.000 |
| B1' | 1 | q0.95 | 2018-19 | 362 | 45 | 0.000 | 0.000 |
| B1' | 1 | q0.05 | 2020 | 251 | 4 | 0.004 | 0.000 |
| B1' | 1 | q0.95 | 2020 | 251 | 6 | 0.035 | 0.000 |
| B1' | 1 | q0.05 | 2021-23 | 748 | 50 | 0.044 | 0.000 |
| B1' | 1 | q0.95 | 2021-23 | 748 | 64 | 0.000 | 0.000 |
| B1' | 1 | q0.05 | 2024 | 250 | 39 | 0.000 | 0.000 |
| B1' | 1 | q0.95 | 2024 | 250 | 42 | 0.000 | 0.000 |
| B1' | 1 | q0.05 | 2025-26 | 244 | 58 | 0.000 | 0.000 |
| B1' | 1 | q0.95 | 2025-26 | 244 | 57 | 0.000 | 0.000 |
| B1' | 2 | q0.05 | 2018-19 | 181 | 13 | 0.205 | 0.294 |
| B1' | 2 | q0.95 | 2018-19 | 181 | 17 | 0.015 | 0.575 |
| B1' | 2 | q0.05 | 2020 | 126 | 1 | 0.007 | 0.899 |
| B1' | 2 | q0.95 | 2020 | 126 | 3 | 0.135 | 0.043 |
| B1' | 2 | q0.05 | 2021-23 | 374 | 14 | 0.244 | 0.001 |
| B1' | 2 | q0.95 | 2021-23 | 374 | 20 | 0.760 | 0.000 |
| B1' | 2 | q0.05 | 2024 | 125 | 14 | 0.006 | 0.160 |
| B1' | 2 | q0.95 | 2024 | 125 | 17 | 0.000 | 0.235 |
| B1' | 2 | q0.05 | 2025-26 | 122 | 28 | 0.000 | 0.700 |
| B1' | 2 | q0.95 | 2025-26 | 122 | 25 | 0.000 | 0.981 |
| B1' | 3 | q0.05 | 2018-19 | 121 | 5 | 0.652 | 0.510 |
| B1' | 3 | q0.95 | 2018-19 | 121 | 12 | 0.028 | 0.835 |
| B1' | 3 | q0.05 | 2020 | 84 | 3 | 0.528 | 0.070 |
| B1' | 3 | q0.95 | 2020 | 84 | 0 | 0.003 | 1.000 |
| B1' | 3 | q0.05 | 2021-23 | 249 | 8 | 0.167 | 0.018 |
| B1' | 3 | q0.95 | 2021-23 | 249 | 13 | 0.874 | 0.022 |
| B1' | 3 | q0.05 | 2024 | 83 | 12 | 0.001 | 0.184 |
| B1' | 3 | q0.95 | 2024 | 83 | 11 | 0.004 | 0.636 |
| B1' | 3 | q0.05 | 2025-26 | 82 | 14 | 0.000 | 0.020 |
| B1' | 3 | q0.95 | 2025-26 | 82 | 16 | 0.000 | 0.979 |
| B1' | 4 | q0.05 | 2018-19 | 91 | 5 | 0.831 | 0.443 |
| B1' | 4 | q0.95 | 2018-19 | 91 | 7 | 0.273 | 0.277 |
| B1' | 4 | q0.05 | 2020 | 63 | 0 | 0.011 | 1.000 |
| B1' | 4 | q0.95 | 2020 | 63 | 2 | 0.477 | 0.715 |
| B1' | 4 | q0.05 | 2021-23 | 187 | 8 | 0.643 | 0.024 |
| B1' | 4 | q0.95 | 2021-23 | 187 | 10 | 0.829 | 0.009 |
| B1' | 4 | q0.05 | 2024 | 62 | 6 | 0.132 | 0.298 |
| B1' | 4 | q0.95 | 2024 | 62 | 3 | 0.953 | 0.577 |
| B1' | 4 | q0.05 | 2025-26 | 61 | 18 | 0.000 | 0.040 |
| B1' | 4 | q0.95 | 2025-26 | 61 | 13 | 0.000 | 0.630 |
| B1' | 5 | q0.05 | 2018-19 | 73 | 3 | 0.719 | 0.609 |
| B1' | 5 | q0.95 | 2018-19 | 73 | 10 | 0.005 | 0.072 |
| B1' | 5 | q0.05 | 2020 | 50 | 2 | 0.737 | 0.039 |
| B1' | 5 | q0.95 | 2020 | 50 | 0 | 0.024 | 1.000 |
| B1' | 5 | q0.05 | 2021-23 | 150 | 6 | 0.561 | 0.172 |
| B1' | 5 | q0.95 | 2021-23 | 150 | 12 | 0.120 | 0.059 |
| B1' | 5 | q0.05 | 2024 | 50 | 3 | 0.753 | 0.611 |
| B1' | 5 | q0.95 | 2024 | 50 | 9 | 0.001 | 0.746 |
| B1' | 5 | q0.05 | 2025-26 | 48 | 8 | 0.003 | 0.700 |
| B1' | 5 | q0.95 | 2025-26 | 48 | 11 | 0.000 | 0.732 |

## The 2026 development days (shown apart; decide nothing)

165 decision days (2025-12-31 to 2026-08-27), 825 cells, last target 2026-09-03.

### Pooled and by lead

Each band cell gives the coverage, its 90% interval and the reading. Each quantile cell gives the share of outcomes strictly below the quantile and the share at or below it, to be compared with the quantile's level, and then the reading. The first table sets the candidate beside the benchmarks; the second splits the candidate by lead.

| group | target days | cells | model | 50% band | 90% band | q05 strict / at-or-below | q95 strict / at-or-below |
|---|---|---|---|---|---|---|---|
| all cells | 169 | 825 | (s3c-ann-net) | 46.2% [36.2%, 55.7%] consistent | 89.2% [82.4%, 94.3%] consistent | 7.8% / 7.8% consistent | 97.0% / 97.0% consistent |
| all cells | 169 | 825 | B1 | 46.4% [41.3%, 52.3%] consistent | 89.6% [85.0%, 93.4%] consistent | 5.5% / 5.8% consistent | 94.3% / 95.0% consistent |
| all cells | 169 | 825 | B1' | 43.9% [37.3%, 51.5%] consistent | 88.7% [84.3%, 93.0%] consistent | 5.6% / 7.8% consistent | 93.8% / 94.3% consistent |
| all cells | 169 | 825 | B2 | 77.2% [69.5%, 83.7%] over-covers | 96.8% [93.5%, 99.4%] over-covers | 3.0% / 3.6% consistent | 99.9% / 99.9% quantile too high |

| group | target days | cells | model | 50% band | 90% band | q05 strict / at-or-below | q95 strict / at-or-below |
|---|---|---|---|---|---|---|---|
| h=1 | 165 | 165 | (s3c-ann-net) | 44.8% [35.2%, 53.3%] consistent | 90.3% [83.6%, 95.8%] consistent | 7.3% / 7.3% consistent | 97.6% / 97.6% quantile too high |
| h=2 | 165 | 165 | (s3c-ann-net) | 43.0% [32.1%, 51.5%] consistent | 89.7% [81.8%, 95.8%] consistent | 7.3% / 7.3% consistent | 97.0% / 97.0% consistent |
| h=3 | 165 | 165 | (s3c-ann-net) | 47.9% [36.4%, 57.6%] consistent | 89.1% [81.8%, 95.2%] consistent | 7.3% / 7.3% consistent | 96.4% / 96.4% consistent |
| h=4 | 165 | 165 | (s3c-ann-net) | 48.5% [35.8%, 59.4%] consistent | 89.1% [82.4%, 94.5%] consistent | 7.9% / 7.9% consistent | 97.0% / 97.0% consistent |
| h=5 | 165 | 165 | (s3c-ann-net) | 46.7% [35.2%, 57.6%] consistent | 87.9% [81.2%, 93.9%] consistent | 9.1% / 9.1% consistent | 97.0% / 97.0% consistent |

### By regime of the target day

The same columns for all four models, one block per regime.

| group | target days | cells | model | 50% band | 90% band | q05 strict / at-or-below | q95 strict / at-or-below |
|---|---|---|---|---|---|---|---|
| 2025-26 | 169 | 825 | (s3c-ann-net) | 46.2% [36.2%, 55.7%] consistent | 89.2% [82.4%, 94.3%] consistent | 7.8% / 7.8% consistent | 97.0% / 97.0% consistent |
| 2025-26 | 169 | 825 | B1 | 46.4% [41.3%, 52.3%] consistent | 89.6% [85.0%, 93.4%] consistent | 5.5% / 5.8% consistent | 94.3% / 95.0% consistent |
| 2025-26 | 169 | 825 | B1' | 43.9% [37.3%, 51.5%] consistent | 88.7% [84.3%, 93.0%] consistent | 5.6% / 7.8% consistent | 93.8% / 94.3% consistent |
| 2025-26 | 169 | 825 | B2 | 77.2% [69.5%, 83.7%] over-covers | 96.8% [93.5%, 99.4%] over-covers | 3.0% / 3.6% consistent | 99.9% / 99.9% quantile too high |

### By day type of the target day (the types overlap; ordinary is none of them)

These day types are calendar flags, and one day can carry several, so the rows do not add up to the whole. The candidate is shown beside B1'.

| group | target days | cells | model | 50% band | 90% band | q05 strict / at-or-below | q95 strict / at-or-below |
|---|---|---|---|---|---|---|---|
| quarter_end | 2 | 10 | (s3c-ann-net) | 60.0% not tested | 100.0% not tested | 0.0% / 0.0% not tested | 100.0% / 100.0% not tested |
| quarter_end | 2 | 10 | B1' | 0.0% not tested | 100.0% not tested | 0.0% / 0.0% not tested | 100.0% / 100.0% not tested |
| month_end | 16 | 79 | (s3c-ann-net) | 58.2% not tested | 98.7% not tested | 0.0% / 0.0% not tested | 98.7% / 98.7% not tested |
| month_end | 16 | 79 | B1' | 57.0% not tested | 94.9% not tested | 0.0% / 0.0% not tested | 94.9% / 94.9% not tested |
| tax_date | 6 | 30 | (s3c-ann-net) | 53.3% not tested | 90.0% not tested | 0.0% / 0.0% not tested | 90.0% / 90.0% not tested |
| tax_date | 6 | 30 | B1' | 16.7% not tested | 73.3% not tested | 0.0% / 3.3% not tested | 73.3% / 73.3% not tested |
| coupon_settlement | 24 | 119 | (s3c-ann-net) | 53.8% [36.7%, 70.0%] consistent | 93.3% [86.7%, 100.0%] consistent | 4.2% / 4.2% consistent | 97.5% / 97.5% consistent |
| coupon_settlement | 24 | 119 | B1' | 39.5% [25.8%, 53.3%] consistent | 87.4% [81.7%, 93.3%] consistent | 0.8% / 2.5% quantile too low | 88.2% / 88.2% quantile too low |
| bill_settlement | 72 | 348 | (s3c-ann-net) | 50.3% [37.8%, 62.2%] consistent | 89.7% [81.9%, 94.6%] consistent | 8.3% / 8.3% consistent | 98.0% / 98.0% consistent |
| bill_settlement | 72 | 348 | B1' | 43.4% [36.7%, 50.8%] consistent | 88.5% [83.4%, 93.6%] consistent | 5.2% / 7.8% consistent | 92.5% / 93.7% consistent |
| fomc_day | 10 | 50 | (s3c-ann-net) | 62.0% not tested | 92.0% not tested | 8.0% / 8.0% not tested | 100.0% / 100.0% not tested |
| fomc_day | 10 | 50 | B1' | 42.0% not tested | 98.0% not tested | 2.0% / 2.0% not tested | 98.0% / 100.0% not tested |
| dom_19_23 | 27 | 135 | (s3c-ann-net) | 50.4% [39.3%, 62.2%] consistent | 88.9% [77.8%, 100.0%] consistent | 11.1% / 11.1% consistent | 100.0% / 100.0% quantile too high |
| dom_19_23 | 27 | 135 | B1' | 39.3% [28.9%, 50.4%] consistent | 87.4% [81.5%, 93.3%] consistent | 10.4% / 16.3% consistent | 97.8% / 97.8% quantile too high |
| post_month_end_window | 27 | 117 | (s3c-ann-net) | 41.9% [31.1%, 58.1%] consistent | 97.4% [89.4%, 99.3%] consistent | 1.7% / 1.7% quantile too low | 99.1% / 99.1% consistent |
| post_month_end_window | 27 | 117 | B1' | 60.7% [52.6%, 70.4%] over-covers | 97.4% [95.8%, 98.8%] over-covers | 1.7% / 2.6% consistent | 98.3% / 99.1% quantile too high |
| ordinary | 44 | 219 | (s3c-ann-net) | 37.9% [27.7%, 48.3%] under-covers | 83.6% [73.6%, 92.7%] consistent | 9.6% / 9.6% consistent | 93.2% / 93.2% consistent |
| ordinary | 44 | 219 | B1' | 36.5% [29.5%, 43.6%] under-covers | 86.3% [81.6%, 90.5%] consistent | 7.8% / 9.1% quantile too high | 94.1% / 94.1% consistent |

### By pressure-day type of the target day

The same comparison on the pressure-day labels the quarter-end studies use.

| group | target days | cells | model | 50% band | 90% band | q05 strict / at-or-below | q95 strict / at-or-below |
|---|---|---|---|---|---|---|---|
| ordinary | 146 | 717 | (s3c-ann-net) | 44.9% [34.8%, 55.0%] consistent | 88.1% [80.6%, 94.7%] consistent | 8.9% / 8.9% consistent | 97.1% / 97.1% consistent |
| ordinary | 146 | 717 | B1' | 44.1% [38.2%, 51.0%] consistent | 88.3% [83.3%, 92.7%] consistent | 6.3% / 8.6% consistent | 94.0% / 94.6% consistent |
| quarter_end_turn | 4 | 20 | (s3c-ann-net) | 50.0% not tested | 100.0% not tested | 0.0% / 0.0% not tested | 100.0% / 100.0% not tested |
| quarter_end_turn | 4 | 20 | B1' | 25.0% not tested | 100.0% not tested | 0.0% / 0.0% not tested | 100.0% / 100.0% not tested |
| tax_date | 6 | 30 | (s3c-ann-net) | 53.3% not tested | 90.0% not tested | 0.0% / 0.0% not tested | 90.0% / 90.0% not tested |
| tax_date | 6 | 30 | B1' | 16.7% not tested | 73.3% not tested | 0.0% / 3.3% not tested | 73.3% / 73.3% not tested |
| turn | 12 | 57 | (s3c-ann-net) | 57.9% not tested | 100.0% not tested | 0.0% / 0.0% not tested | 100.0% / 100.0% not tested |
| turn | 12 | 57 | B1' | 63.2% not tested | 98.2% not tested | 1.8% / 1.8% not tested | 100.0% / 100.0% not tested |
| year_end | 1 | 1 | (s3c-ann-net) | 0.0% not tested | 0.0% not tested | 0.0% / 0.0% not tested | 0.0% / 0.0% not tested |
| year_end | 1 | 1 | B1' | 0.0% not tested | 100.0% not tested | 0.0% / 0.0% not tested | 100.0% / 100.0% not tested |

### Every grid quantile, all cells (candidate)

For a calibrated model each share, read as a fraction, equals the level in the first column.

| level | share strictly below | share at or below |
|---|---|---|
| 0.01 | 4.85% | 4.85% |
| 0.025 | 6.06% | 6.06% |
| 0.05 | 7.76% | 7.76% |
| 0.1 | 13.09% | 13.09% |
| 0.15 | 21.33% | 21.33% |
| 0.2 | 27.15% | 27.15% |
| 0.25 | 32.48% | 32.48% |
| 0.3 | 37.82% | 37.82% |
| 0.35 | 41.58% | 41.58% |
| 0.4 | 46.30% | 46.30% |
| 0.45 | 50.30% | 50.30% |
| 0.5 | 54.42% | 54.55% |
| 0.55 | 59.15% | 59.15% |
| 0.6 | 65.70% | 65.70% |
| 0.65 | 68.48% | 68.48% |
| 0.7 | 72.36% | 72.36% |
| 0.75 | 78.67% | 78.67% |
| 0.8 | 84.12% | 84.12% |
| 0.85 | 89.09% | 89.09% |
| 0.9 | 92.85% | 92.85% |
| 0.95 | 96.97% | 96.97% |
| 0.975 | 98.55% | 98.55% |
| 0.99 | 99.64% | 99.64% |

### Randomized PIT (seed 1363; the range is over seeds 1364 to 1383)

The PIT is the probability the forecast gave to outcomes at or below the one that happened; it is randomized where the outcome ties a quantile. For a calibrated model the six bins hold ten, fifteen, twenty-five, twenty-five, fifteen and ten percent of the cells. The last two columns give the two outer bins with their range over 20 other seeds, which shows how far the randomization moves them.

pooled, candidate:

| group | cells | bins (≤0.10, ≤0.25, ≤0.50, ≤0.75, ≤0.90, >0.90) | ≤0.10 (20 other seeds) | ≥0.90 (20 other seeds) |
|---|---|---|---|---|
| all cells | 825 | 13.1 19.4 21.9 24.2 14.2 7.2 | 13.1% (13.1% to 13.1%) | 7.2% (7.2% to 7.2%) |

regime, candidate:

| group | cells | bins (≤0.10, ≤0.25, ≤0.50, ≤0.75, ≤0.90, >0.90) | ≤0.10 (20 other seeds) | ≥0.90 (20 other seeds) |
|---|---|---|---|---|
| 2025-26 | 825 | 13.1 19.4 21.9 24.2 14.2 7.2 | 13.1% (13.1% to 13.1%) | 7.2% (7.2% to 7.2%) |

target_day_type, candidate:

| group | cells | bins (≤0.10, ≤0.25, ≤0.50, ≤0.75, ≤0.90, >0.90) | ≤0.10 (20 other seeds) | ≥0.90 (20 other seeds) |
|---|---|---|---|---|
| quarter_end | 10 | 0.0 40.0 10.0 50.0 0.0 0.0 | 0.0% (0.0% to 0.0%) | 0.0% (0.0% to 0.0%) |
| month_end | 79 | 2.5 25.3 38.0 20.3 8.9 5.1 | 2.5% (2.5% to 2.5%) | 5.1% (5.1% to 5.1%) |
| tax_date | 30 | 0.0 3.3 13.3 40.0 23.3 20.0 | 0.0% (0.0% to 0.0%) | 20.0% (20.0% to 20.0%) |
| coupon_settlement | 119 | 5.0 10.9 24.4 29.4 15.1 15.1 | 5.0% (5.0% to 5.0%) | 15.1% (15.1% to 15.1%) |
| bill_settlement | 348 | 12.9 14.4 23.3 27.0 14.9 7.5 | 12.9% (12.9% to 12.9%) | 7.5% (7.5% to 7.5%) |
| fomc_day | 50 | 10.0 16.0 16.0 46.0 12.0 0.0 | 10.0% (10.0% to 10.0%) | 0.0% (0.0% to 0.0%) |
| dom_19_23 | 135 | 15.6 10.4 13.3 37.0 23.0 0.7 | 15.6% (15.6% to 15.6%) | 0.7% (0.7% to 0.7%) |
| post_month_end_window | 117 | 7.7 20.5 26.5 15.4 20.5 9.4 | 7.7% (7.7% to 7.7%) | 9.4% (9.4% to 9.4%) |
| ordinary | 219 | 18.3 27.9 17.8 20.1 7.3 8.7 | 18.3% (18.3% to 18.3%) | 8.7% (8.7% to 8.7%) |

pressure_day_type, candidate:

| group | cells | bins (≤0.10, ≤0.25, ≤0.50, ≤0.75, ≤0.90, >0.90) | ≤0.10 (20 other seeds) | ≥0.90 (20 other seeds) |
|---|---|---|---|---|
| ordinary | 717 | 15.1 20.6 21.6 23.3 13.1 6.3 | 15.1% (15.1% to 15.1%) | 6.3% (6.3% to 6.3%) |
| quarter_end_turn | 20 | 0.0 20.0 20.0 30.0 30.0 0.0 | 0.0% (0.0% to 0.0%) | 0.0% (0.0% to 0.0%) |
| tax_date | 30 | 0.0 3.3 13.3 40.0 23.3 20.0 | 0.0% (0.0% to 0.0%) | 20.0% (20.0% to 20.0%) |
| turn | 57 | 0.0 12.3 33.3 24.6 17.5 12.3 | 0.0% (0.0% to 0.0%) | 12.3% (12.3% to 12.3%) |
| year_end | 1 | 0.0 0.0 0.0 0.0 0.0 100.0 | 0.0% (0.0% to 0.0%) | 100.0% (100.0% to 100.0%) |

pooled, the references:

B1:

| group | cells | bins (≤0.10, ≤0.25, ≤0.50, ≤0.75, ≤0.90, >0.90) | ≤0.10 (20 other seeds) | ≥0.90 (20 other seeds) |
|---|---|---|---|---|
| all cells | 825 | 13.5 16.7 19.9 24.4 16.8 8.7 | 13.5% (13.3% to 14.2%) | 8.7% (8.4% to 9.0%) |

B1':

| group | cells | bins (≤0.10, ≤0.25, ≤0.50, ≤0.75, ≤0.90, >0.90) | ≤0.10 (20 other seeds) | ≥0.90 (20 other seeds) |
|---|---|---|---|---|
| all cells | 825 | 13.1 19.3 19.5 21.0 17.9 9.2 | 13.1% (12.6% to 13.6%) | 9.2% (9.0% to 9.6%) |

B2:

| group | cells | bins (≤0.10, ≤0.25, ≤0.50, ≤0.75, ≤0.90, >0.90) | ≤0.10 (20 other seeds) | ≥0.90 (20 other seeds) |
|---|---|---|---|---|
| all cells | 825 | 5.7 9.2 36.4 37.2 10.1 1.5 | 5.7% (5.7% to 5.7%) | 1.5% (1.3% to 1.6%) |

### Readings that are not 'consistent' (candidate)

The full list behind the summary in the answer, largest first.

21 of 117 readings in tested groups. Sizes are observed less nominal for a band, distance of the level from [strict, at-or-below] for a quantile.

| split | group | target days | what | reading | size |
|---|---|---|---|---|---|
| target_day_type | ordinary | 44 | q0.25 | quantile too high | +21.1 pp |
| target_day_type | ordinary | 44 | q0.5 | quantile too high | +13.9 pp |
| target_day_type | ordinary | 44 | 50% band | under-covers | -12.1 pp |
| pressure_day_type | ordinary | 146 | q0.25 | quantile too high | +10.7 pp |
| lead | h=2 | 165 | q0.25 | quantile too high | +10.2 pp |
| target_day_type | coupon_settlement | 24 | q0.5 | quantile too low | -9.7 pp |
| target_day_type | bill_settlement | 72 | q0.01 | quantile too high | +5.0 pp |
| target_day_type | dom_19_23 | 27 | q0.95 | quantile too high | +5.0 pp |
| pressure_day_type | ordinary | 146 | q0.01 | quantile too high | +4.6 pp |
| lead | h=3 | 165 | q0.01 | quantile too high | +4.5 pp |
| lead | h=5 | 165 | q0.01 | quantile too high | +3.8 pp |
| target_day_type | post_month_end_window | 27 | q0.05 | quantile too low | -3.3 pp |
| lead | h=1 | 165 | q0.01 | quantile too high | +3.2 pp |
| lead | h=1 | 165 | q0.95 | quantile too high | +2.6 pp |
| lead | h=3 | 165 | q0.99 | quantile too high | +1.0 pp |
| lead | h=4 | 165 | q0.99 | quantile too high | +1.0 pp |
| lead | h=5 | 165 | q0.99 | quantile too high | +1.0 pp |
| target_day_type | coupon_settlement | 24 | q0.99 | quantile too high | +1.0 pp |
| target_day_type | dom_19_23 | 27 | q0.99 | quantile too high | +1.0 pp |
| target_day_type | post_month_end_window | 27 | q0.01 | quantile too low | -1.0 pp |
| pressure_day_type | ordinary | 146 | q0.99 | quantile too high | +0.7 pp |

### Do the misses cluster in time?

A hit sequence records, day by day, whether the outcome fell outside a quantile or a band. If misses were independent, a miss would be no more likely after a miss than after a hit. The first table counts, for each model, how many of its sequences are read as serially dependent; the table after it gives the detail.

Christoffersen's independence test on each lead's sequence over the scored decision days (no transition across a gap or, for the regime rows, a regime change); the permutation p is the reading, Holm-adjusted at 0.05 over the 40 sequences of a model and window (per regime for the regime rows).

| model | sequences (all days) | clustered by Holm | sequences inside regimes | clustered by Holm |
|---|---|---|---|---|
| (s3c-ann-net) | 40 | 40 | 0 | 0 |
| B1 | 40 | 25 | 0 | 0 |
| B1' | 40 | 28 | 0 | 0 |
| B2 | 40 | 30 | 0 | 0 |

| model | lead | sequence | misses (rate) | P(miss after miss) | P(miss after hit) | longest run | LR p (asymptotic) | p (permutation) | clusters (Holm) |
|---|---|---|---|---|---|---|---|---|---|
| (s3c-ann-net) | 1 | upper/strict | 4 (2.4%) | 25.0% | 1.2% | 2 | 0.0469 | 0.0047 | yes |
| (s3c-ann-net) | 1 | lower/strict | 12 (7.3%) | 58.3% | 3.3% | 6 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 1 | band90/strict | 16 (9.7%) | 50.0% | 4.7% | 6 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 1 | band50/strict | 91 (55.2%) | 68.1% | 38.4% | 14 | 0.0001 | 0.0002 | yes |
| (s3c-ann-net) | 2 | upper/strict | 5 (3.0%) | 40.0% | 1.9% | 3 | 0.0041 | 0.0050 | yes |
| (s3c-ann-net) | 2 | lower/strict | 12 (7.3%) | 66.7% | 2.6% | 6 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 2 | band90/strict | 17 (10.3%) | 58.8% | 4.8% | 6 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 2 | band50/strict | 94 (57.0%) | 72.3% | 37.1% | 33 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 3 | upper/strict | 6 (3.6%) | 33.3% | 2.5% | 3 | 0.0106 | 0.0106 | yes |
| (s3c-ann-net) | 3 | lower/strict | 12 (7.3%) | 66.7% | 2.6% | 6 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 3 | band90/strict | 18 (10.9%) | 55.6% | 5.5% | 6 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 3 | band50/strict | 86 (52.1%) | 70.9% | 30.8% | 26 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 4 | upper/strict | 5 (3.0%) | 40.0% | 1.9% | 3 | 0.0041 | 0.0050 | yes |
| (s3c-ann-net) | 4 | lower/strict | 13 (7.9%) | 61.5% | 3.3% | 6 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 4 | band90/strict | 18 (10.9%) | 55.6% | 5.5% | 6 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 4 | band50/strict | 85 (51.5%) | 71.8% | 30.4% | 27 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 5 | upper/strict | 5 (3.0%) | 40.0% | 1.9% | 3 | 0.0041 | 0.0050 | yes |
| (s3c-ann-net) | 5 | lower/strict | 15 (9.1%) | 60.0% | 4.0% | 6 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 5 | band90/strict | 20 (12.1%) | 55.0% | 6.2% | 6 | 0.0000 | 0.0001 | yes |
| (s3c-ann-net) | 5 | band50/strict | 88 (53.3%) | 72.7% | 30.3% | 18 | 0.0000 | 0.0001 | yes |
| B1' | 1 | upper/strict | 14 (8.5%) | 50.0% | 4.7% | 3 | 0.0000 | 0.0001 | yes |
| B1' | 1 | lower/strict | 10 (6.1%) | 40.0% | 3.9% | 2 | 0.0008 | 0.0012 | yes |
| B1' | 1 | band90/strict | 24 (14.5%) | 45.8% | 9.3% | 3 | 0.0000 | 0.0001 | yes |
| B1' | 1 | band50/strict | 108 (65.5%) | 68.5% | 58.9% | 15 | 0.2238 | 0.2216 | no |
| B1' | 2 | upper/strict | 10 (6.1%) | 40.0% | 3.9% | 3 | 0.0008 | 0.0012 | yes |
| B1' | 2 | lower/strict | 14 (8.5%) | 42.9% | 5.3% | 3 | 0.0002 | 0.0003 | yes |
| B1' | 2 | band90/strict | 24 (14.5%) | 41.7% | 10.0% | 3 | 0.0003 | 0.0007 | yes |
| B1' | 2 | band50/strict | 93 (56.4%) | 65.6% | 45.1% | 11 | 0.0085 | 0.0089 | no |
| B1' | 3 | upper/strict | 7 (4.2%) | 28.6% | 3.2% | 3 | 0.0230 | 0.0207 | no |
| B1' | 3 | lower/strict | 10 (6.1%) | 30.0% | 4.5% | 2 | 0.0131 | 0.0118 | no |
| B1' | 3 | band90/strict | 17 (10.3%) | 29.4% | 8.2% | 3 | 0.0188 | 0.0149 | no |
| B1' | 3 | band50/strict | 91 (55.2%) | 63.7% | 43.8% | 11 | 0.0107 | 0.0099 | no |
| B1' | 4 | upper/strict | 8 (4.8%) | 50.0% | 2.6% | 3 | 0.0001 | 0.0001 | yes |
| B1' | 4 | lower/strict | 8 (4.8%) | 37.5% | 3.2% | 3 | 0.0026 | 0.0024 | yes |
| B1' | 4 | band90/strict | 16 (9.7%) | 43.8% | 6.1% | 3 | 0.0001 | 0.0003 | yes |
| B1' | 4 | band50/strict | 82 (49.7%) | 62.2% | 36.6% | 8 | 0.0010 | 0.0014 | yes |
| B1' | 5 | upper/strict | 8 (4.8%) | 50.0% | 2.6% | 3 | 0.0001 | 0.0001 | yes |
| B1' | 5 | lower/strict | 4 (2.4%) | 50.0% | 1.2% | 3 | 0.0012 | 0.0020 | yes |
| B1' | 5 | band90/strict | 12 (7.3%) | 50.0% | 3.9% | 3 | 0.0000 | 0.0002 | yes |
| B1' | 5 | band50/strict | 89 (53.9%) | 61.8% | 44.0% | 15 | 0.0225 | 0.0255 | no |
| B2 | 1 | upper/strict | 1 (0.6%) | 0.0% | 0.0% | 1 | 1.0000 | 1.0000 | no |
| B2 | 1 | lower/strict | 5 (3.0%) | 60.0% | 1.3% | 3 | 0.0000 | 0.0002 | yes |
| B2 | 1 | band90/strict | 6 (3.6%) | 50.0% | 1.3% | 3 | 0.0001 | 0.0001 | yes |
| B2 | 1 | band50/strict | 40 (24.2%) | 60.0% | 12.1% | 8 | 0.0000 | 0.0001 | yes |
| B2 | 2 | upper/strict | 0 (0.0%) | n/a | 0.0% | 0 | 1.0000 | 1.0000 | no |
| B2 | 2 | lower/strict | 5 (3.0%) | 60.0% | 1.3% | 3 | 0.0000 | 0.0002 | yes |
| B2 | 2 | band90/strict | 5 (3.0%) | 60.0% | 1.3% | 3 | 0.0000 | 0.0002 | yes |
| B2 | 2 | band50/strict | 39 (23.6%) | 59.0% | 12.0% | 8 | 0.0000 | 0.0001 | yes |
| B2 | 3 | upper/strict | 0 (0.0%) | n/a | 0.0% | 0 | 1.0000 | 1.0000 | no |
| B2 | 3 | lower/strict | 5 (3.0%) | 60.0% | 1.3% | 3 | 0.0000 | 0.0002 | yes |
| B2 | 3 | band90/strict | 5 (3.0%) | 60.0% | 1.3% | 3 | 0.0000 | 0.0002 | yes |
| B2 | 3 | band50/strict | 38 (23.0%) | 57.9% | 11.9% | 8 | 0.0000 | 0.0001 | yes |
| B2 | 4 | upper/strict | 0 (0.0%) | n/a | 0.0% | 0 | 1.0000 | 1.0000 | no |
| B2 | 4 | lower/strict | 5 (3.0%) | 60.0% | 1.3% | 3 | 0.0000 | 0.0002 | yes |
| B2 | 4 | band90/strict | 5 (3.0%) | 60.0% | 1.3% | 3 | 0.0000 | 0.0002 | yes |
| B2 | 4 | band50/strict | 36 (21.8%) | 58.3% | 11.7% | 7 | 0.0000 | 0.0001 | yes |
| B2 | 5 | upper/strict | 0 (0.0%) | n/a | 0.0% | 0 | 1.0000 | 1.0000 | no |
| B2 | 5 | lower/strict | 5 (3.0%) | 60.0% | 1.3% | 3 | 0.0000 | 0.0002 | yes |
| B2 | 5 | band90/strict | 5 (3.0%) | 60.0% | 1.3% | 3 | 0.0000 | 0.0002 | yes |
| B2 | 5 | band50/strict | 35 (21.2%) | 57.1% | 11.6% | 7 | 0.0000 | 0.0001 | yes |

#### The protocol's own reading (thinned: every h-th decision day at lead h; regime of the decision day), q05 and q95, strict rule

These are the two tests the scoring protocol applies: a Kupiec test of the hit rate and an independence test, each with its p-value.

| model | lead | level | regime | n | hits | Kupiec p | independence p |
|---|---|---|---|---|---|---|---|
| (s3c-ann-net) | 1 | q0.05 | 2025-26 | 165 | 12 | 0.208 | 0.000 |
| (s3c-ann-net) | 1 | q0.95 | 2025-26 | 165 | 4 | 0.093 | 0.047 |
| (s3c-ann-net) | 2 | q0.05 | 2025-26 | 83 | 6 | 0.381 | 0.002 |
| (s3c-ann-net) | 2 | q0.95 | 2025-26 | 83 | 2 | 0.230 | 0.752 |
| (s3c-ann-net) | 3 | q0.05 | 2025-26 | 55 | 4 | 0.468 | 0.250 |
| (s3c-ann-net) | 3 | q0.95 | 2025-26 | 55 | 1 | 0.215 | 0.846 |
| (s3c-ann-net) | 4 | q0.05 | 2025-26 | 42 | 4 | 0.229 | 0.345 |
| (s3c-ann-net) | 4 | q0.95 | 2025-26 | 42 | 2 | 0.943 | 0.651 |
| (s3c-ann-net) | 5 | q0.05 | 2025-26 | 33 | 3 | 0.331 | 0.430 |
| (s3c-ann-net) | 5 | q0.95 | 2025-26 | 33 | 0 | 0.066 | 1.000 |
| B1' | 1 | q0.05 | 2025-26 | 165 | 10 | 0.545 | 0.001 |
| B1' | 1 | q0.95 | 2025-26 | 165 | 14 | 0.061 | 0.000 |
| B1' | 2 | q0.05 | 2025-26 | 83 | 7 | 0.189 | 0.597 |
| B1' | 2 | q0.95 | 2025-26 | 83 | 4 | 0.939 | 0.522 |
| B1' | 3 | q0.05 | 2025-26 | 55 | 4 | 0.468 | 0.423 |
| B1' | 3 | q0.95 | 2025-26 | 55 | 1 | 0.215 | 0.846 |
| B1' | 4 | q0.05 | 2025-26 | 42 | 1 | 0.388 | 0.823 |
| B1' | 4 | q0.95 | 2025-26 | 42 | 3 | 0.548 | 0.491 |
| B1' | 5 | q0.05 | 2025-26 | 33 | 1 | 0.577 | 0.799 |
| B1' | 5 | q0.95 | 2025-26 | 33 | 1 | 0.577 | 0.799 |

## What it means, and its limits

It shows how the candidate's bands and quantiles hold on seen days, by regime and by day type, and whether its tail and band misses are serially dependent. It does not show that any group is miscalibrated for the next days, nothing here is a verdict, and a miss rate that moves with the regime would also reject independence: the regime rows and the day-type tables are there to tell the two apart. B4 is not compared.

## Record

- Study: #1363. Hypothesis and step: H5 (primary goal), registration design: step 3 evidence for the known-limits section of the registration and the validation report.
- Status: **development data, not a verdict** (scoring protocol v1, #640). Nothing is registered or published, no record is edited, and nothing is adopted.
- Generated by `scripts/candidate_calibration_1363.py page` from `docs/research/candidate-calibration-1363/result.json`; declared in `metadata/candidate_calibration_1363.json` before any figure.
- Panel digest `4ddc3882cd6d406b11e1088f8ff6195e16dde175a0ad6818abe40dd5bdac8999`.
- Reproduction: each walk's mean grid CRPS (candidate, B1, B1' and B2, all cells) equals the 18:00 record of #1314 (`docs/research/s3c-ann-net-1800-1314/announced-settlement-1800.json`) to 1e-9, or the script refused to write this record.
- B4 (#1360, a plain quantile regression on reserves and calendar days) is not on main at the base of this pull request and is not compared; the page says so. Once #1360 merges the walk command can add it; nothing here waits on it.
- The 2026 days were already seen by #845, #1229, #1255, #1273, #1288 and #1321.
- The interval method: #1221 questions it and #1228 will decide.
