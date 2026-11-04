# The simple baselines with the candidate's SRF cap: B1'*-cap and B2*-cap (#1421)

**Development data, not a verdict.** Hypothesis H5 (primary goal), registration design (benchmarks), step 3. The candidate, (s3c-ann-net), is capped at the Standing Repo Facility line on target days at full allotment. A baseline left uncapped could make part of the candidate's gain a mechanical truncation at that line. This page gives the baselines the candidate's own cap (the same line, read from `metadata/policy_events.json` as public at the decision instant, margin 0 bp) and the candidate's probability rule (b) (`capped_law`, `open_tail`), and scores them beside the uncapped versions. Panel digest `4ddc3882cd6d406b11e1088f8ff6195e16dde175a0ad6818abe40dd5bdac8999`; walked at the 18:00 decision instant; seed 1421, 10000 draws.

**Which version is confirmatory is ruled, not open** (Eleonora, 3 November 2026, comment on #1421): the capped baselines are the confirmatory benchmarks and the uncapped versions are reported beside them. This page does not reopen it.

**B2 stands in for B2\*.** B2\* is #1420's and is not on main. Every B2 figure below is B2 as `protocol_benchmarks.b2_forecast` gives it, capped for "B2-cap"; the size-and-power study (#1399) used B2 as the same stand-in. When #1420 merges, B2\*-cap wraps B2\* and a later directive re-runs this page.

The grid CRPS, the upper-tail twCRPS and the Brier score are losses (lower is better). "Mean d" is the reference's loss less the arm's, so a positive value favours the arm; the interval is scoring protocol v1's studentized stationary bootstrap on decision-day means, read on the bound on mean d (her ruling on #1009) as `gain`, `loss` or `undecided` from whether it excludes zero. † marks a bound taken from the resamples that have a long-run variance (#1239). A group of fewer than 20 decision days is not tested. The mean grid CRPS of the candidate, B2 and B1'* reproduces #1314's record and #1388's result to 1e-9 in both windows (the study refuses to write otherwise).

## 2026 days (targets 2026-01-02 to 2026-09-03; full allotment on every target), shown apart

165 decision days, 825 cells, 825 of them at full allotment. Cells at full allotment where the model's uncapped q99 is above the line, so that the cap changes at least one quantile: B1'* 558, B2 804; the candidate's own uncapped vector, 404.

**Mean losses, pooled (all cells)**

| model | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|
| (s3c-ann-net) | 1.669 | 0.514 | 0.0352 |
| B1'* (uncapped) | 1.865 | 0.631 | 0.0445 |
| B1'*-cap | 1.856 | 0.623 | 0.0445 |
| B2 (uncapped; stands in for B2*) | 2.155 | 0.636 | 0.0356 |
| B2*-cap (B2 as the stand-in) | 2.104 | 0.585 | 0.0356 |

**The candidate against each baseline, pooled** (mean d: baseline less candidate; positive favours the candidate)

| comparison | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|
| (s3c-ann-net) against B1'*-cap | +0.188 [-0.169, +0.415]: undecided | +0.109 [+0.026, +0.210]: gain | +0.0093 [+0.0001, +0.0357]: gain |
| (s3c-ann-net) against B1'* | +0.196 [-0.163, +0.423]: undecided | +0.117 [+0.034, +0.222]: gain | +0.0093 [+0.0001, +0.0357]: gain |
| (s3c-ann-net) against B2-cap | +0.435 [+0.059, +0.870]: gain | +0.071 [-0.101, +0.188]: undecided | +0.0005 [-0.0186, +0.0088]: undecided |
| (s3c-ann-net) against B2 | +0.486 [+0.115, +0.942]: gain | +0.122 [-0.044, +0.241]: undecided | +0.0005 [-0.0186, +0.0088]: undecided |

**What the cap alone buys, pooled** (mean d: uncapped baseline less capped baseline; positive favours the cap)

| comparison | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|
| B1'*-cap against B1'* (what the cap alone buys) | +0.0084 [+0.0050, +0.0141]: gain | +0.0084 [+0.0050, +0.0141]: gain | +8.68e-08 [+5.67e-08, +1.25e-07]: gain |
| B2-cap against B2 (what the cap alone buys) | +0.0508 [+0.0342, +0.0713]: gain | +0.0508 [+0.0342, +0.0713]: gain | +3.75e-06 [-1.07e-05, +1.91e-05]: undecided |

Every target of this window is at full allotment, so the group "target days at full allotment" is the pooled group and its tables are not repeated.

**The share of the candidate's gain over the uncapped baseline that the cap alone buys** (uncapped less capped, over uncapped less candidate; defined only where the candidate's gain over the uncapped baseline excludes zero on the positive side; interval: percentile, stationary bootstrap of the decision days)

| group | baseline | metric | uncapped | capped | candidate | share of the gain the cap alone buys [90% interval] |
|---|---|---|---|---|---|---|
| all cells | B1'* | Brier P(> +5 bp) | 0.0445 | 0.0445 | 0.0352 | 0.000 [0.000, 0.000] (132 resample(s) without a gain dropped) |
| all cells | B1'* | grid CRPS | 1.865 | 1.856 | 1.669 | not defined: the candidate's gain over the uncapped baseline is not distinguished from zero |
| all cells | B1'* | upper-tail twCRPS | 0.631 | 0.623 | 0.514 | 0.072 [0.041, 0.181] (17 resample(s) without a gain dropped) |
| all cells | B2 | Brier P(> +5 bp) | 0.0356 | 0.0356 | 0.0352 | not defined: the candidate's gain over the uncapped baseline is not distinguished from zero |
| all cells | B2 | grid CRPS | 2.155 | 2.104 | 1.669 | 0.105 [0.057, 0.285] (1 resample(s) without a gain dropped) |
| all cells | B2 | upper-tail twCRPS | 0.636 | 0.585 | 0.514 | not defined: the candidate's gain over the uncapped baseline is not distinguished from zero |

**grid CRPS: (s3c-ann-net) against B1'*-cap, by regime of the target day**

| regime | decision days | B1'*-cap |
|---|---|---|
| 2025-26 | 165 | +0.188 [-0.169, +0.415]: undecided |

**grid CRPS: (s3c-ann-net) against B1'*-cap, by pressure day type of the target day**

| pressure day type | decision days | B1'*-cap |
|---|---|---|
| ordinary | 165 | +0.105 [-0.275, +0.342]: undecided |
| quarter_end_turn | 12 | not tested |
| tax_date | 15 | not tested |
| turn | 34 | +0.362 [+0.180, +0.558]: gain |
| year_end | 1 | not tested |

**grid CRPS: (s3c-ann-net) against B2-cap, by regime of the target day**

| regime | decision days | B2-cap |
|---|---|---|
| 2025-26 | 165 | +0.435 [+0.059, +0.870]: gain |

**grid CRPS: (s3c-ann-net) against B2-cap, by pressure day type of the target day**

| pressure day type | decision days | B2-cap |
|---|---|---|
| ordinary | 165 | +0.372 [-0.058, +0.831]: undecided |
| quarter_end_turn | 12 | not tested |
| tax_date | 15 | not tested |
| turn | 34 | +0.758 [-0.313, +1.994]: undecided |
| year_end | 1 | not tested |

**upper-tail twCRPS: (s3c-ann-net) against B1'*-cap, by regime of the target day**

| regime | decision days | B1'*-cap |
|---|---|---|
| 2025-26 | 165 | +0.109 [+0.026, +0.210]: gain |

**upper-tail twCRPS: (s3c-ann-net) against B1'*-cap, by pressure day type of the target day**

| pressure day type | decision days | B1'*-cap |
|---|---|---|
| ordinary | 165 | +0.050 [-0.050, +0.159]: undecided |
| quarter_end_turn | 12 | not tested |
| tax_date | 15 | not tested |
| turn | 34 | +0.400 [+0.184, +0.674]: gain |
| year_end | 1 | not tested |

**upper-tail twCRPS: (s3c-ann-net) against B2-cap, by regime of the target day**

| regime | decision days | B2-cap |
|---|---|---|
| 2025-26 | 165 | +0.071 [-0.101, +0.188]: undecided |

**upper-tail twCRPS: (s3c-ann-net) against B2-cap, by pressure day type of the target day**

| pressure day type | decision days | B2-cap |
|---|---|---|
| ordinary | 165 | -0.006 [-0.183, +0.107]: undecided |
| quarter_end_turn | 12 | not tested |
| tax_date | 15 | not tested |
| turn | 34 | +0.775 [+0.643, +0.910]: gain |
| year_end | 1 | not tested |

**Brier P(> +5 bp): (s3c-ann-net) against B1'*-cap, by regime of the target day**

| regime | decision days | B1'*-cap |
|---|---|---|
| 2025-26 | 165 | +0.0093 [+0.0001, +0.0357]: gain |

**Brier P(> +5 bp): (s3c-ann-net) against B1'*-cap, by pressure day type of the target day**

| pressure day type | decision days | B1'*-cap |
|---|---|---|
| ordinary | 165 | +0.0057 [-0.0035, +0.0278]: undecided |
| quarter_end_turn | 12 | not tested |
| tax_date | 15 | not tested |
| turn | 34 | +0.0529 [-0.0001, +0.0928]: undecided |
| year_end | 1 | not tested |

**Brier P(> +5 bp): (s3c-ann-net) against B2-cap, by regime of the target day**

| regime | decision days | B2-cap |
|---|---|---|
| 2025-26 | 165 | +0.0005 [-0.0186, +0.0088]: undecided |

**Brier P(> +5 bp): (s3c-ann-net) against B2-cap, by pressure day type of the target day**

| pressure day type | decision days | B2-cap |
|---|---|---|
| ordinary | 165 | -0.0043 [-0.0264, +0.0042]: undecided |
| quarter_end_turn | 12 | not tested |
| tax_date | 15 | not tested |
| turn | 34 | +0.0580 [+0.0478, +0.0645]: gain |
| year_end | 1 | not tested |

## Development window (targets up to 2025-12-31; this window decides what the page reads)

1855 decision days, 9275 cells, 50 of them at full allotment. Cells at full allotment where the model's uncapped q99 is above the line, so that the cap changes at least one quantile: B1'* 49, B2 38; the candidate's own uncapped vector, 50.

**Mean losses, pooled (all cells)**

| model | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|
| (s3c-ann-net) | 1.601 | 0.845 | 0.0461 |
| B1'* (uncapped) | 1.843 | 0.991 | 0.0543 |
| B1'*-cap | 1.843 | 0.991 | 0.0543 |
| B2 (uncapped; stands in for B2*) | 2.514 | 1.133 | 0.0643 |
| B2*-cap (B2 as the stand-in) | 2.515 | 1.133 | 0.0643 |

**The candidate against each baseline, pooled** (mean d: baseline less candidate; positive favours the candidate)

| comparison | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|
| (s3c-ann-net) against B1'*-cap | +0.242 [+0.157, +0.344]: gain | +0.146 [+0.075, +0.253]: gain | +0.0082 [+0.0010, +0.0161]: gain |
| (s3c-ann-net) against B1'* | +0.242 [+0.157, +0.343]: gain | +0.146 [+0.074, +0.253]: gain | +0.0082 [+0.0010, +0.0161]: gain |
| (s3c-ann-net) against B2-cap | +0.913 [+0.665, +1.230]: gain | +0.288 [+0.164, +0.462]: gain | +0.0182 [+0.0078, +0.0315]: gain |
| (s3c-ann-net) against B2 | +0.913 [+0.665, +1.230]: gain | +0.288 [+0.163, +0.461]: gain | +0.0182 [+0.0078, +0.0315]: gain |

**What the cap alone buys, pooled** (mean d: uncapped baseline less capped baseline; positive favours the cap)

| comparison | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|
| B1'*-cap against B1'* (what the cap alone buys) | -0.0003 [-0.0075, +0.0001]: undecided † | -0.0003 [-0.0075, +0.0001]: undecided † | -8.43e-10 [-1.42e-08, +1.53e-10]: undecided † |
| B2-cap against B2 (what the cap alone buys) | -0.0001 [-0.0044, +0.0000]: undecided † | -0.0001 [-0.0044, +0.0000]: undecided † | -2.21e-10 [-3.29e-09, +5.74e-11]: undecided † |

**Mean losses, target days at full allotment**

| model | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|
| (s3c-ann-net) | 2.154 | 1.769 | 0.1287 |
| B1'* (uncapped) | 2.358 | 2.254 | 0.2042 |
| B1'*-cap | 2.406 | 2.303 | 0.2042 |
| B2 (uncapped; stands in for B2*) | 5.599 | 3.115 | 0.2210 |
| B2*-cap (B2 as the stand-in) | 5.626 | 3.142 | 0.2210 |

**The candidate against each baseline, target days at full allotment**

| comparison | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|
| (s3c-ann-net) against B1'*-cap | fewer than 20 decision days | fewer than 20 decision days | fewer than 20 decision days |
| (s3c-ann-net) against B1'* | fewer than 20 decision days | fewer than 20 decision days | fewer than 20 decision days |
| (s3c-ann-net) against B2-cap | fewer than 20 decision days | fewer than 20 decision days | fewer than 20 decision days |
| (s3c-ann-net) against B2 | fewer than 20 decision days | fewer than 20 decision days | fewer than 20 decision days |

**What the cap alone buys, target days at full allotment**

| comparison | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|
| B1'*-cap against B1'* (what the cap alone buys) | fewer than 20 decision days | fewer than 20 decision days | fewer than 20 decision days |
| B2-cap against B2 (what the cap alone buys) | fewer than 20 decision days | fewer than 20 decision days | fewer than 20 decision days |

**The share of the candidate's gain over the uncapped baseline that the cap alone buys** (uncapped less capped, over uncapped less candidate; defined only where the candidate's gain over the uncapped baseline excludes zero on the positive side; interval: percentile, stationary bootstrap of the decision days)

| group | baseline | metric | uncapped | capped | candidate | share of the gain the cap alone buys [90% interval] |
|---|---|---|---|---|---|---|
| target days at full allotment | B1'* | Brier P(> +5 bp) | 0.2042 | 0.2042 | 0.1287 | not defined: the candidate's gain over the uncapped baseline was not tested |
| target days at full allotment | B1'* | grid CRPS | 2.358 | 2.406 | 2.154 | not defined: the candidate's gain over the uncapped baseline was not tested |
| target days at full allotment | B1'* | upper-tail twCRPS | 2.254 | 2.303 | 1.769 | not defined: the candidate's gain over the uncapped baseline was not tested |
| target days at full allotment | B2 | Brier P(> +5 bp) | 0.2210 | 0.2210 | 0.1287 | not defined: the candidate's gain over the uncapped baseline was not tested |
| target days at full allotment | B2 | grid CRPS | 5.599 | 5.626 | 2.154 | not defined: the candidate's gain over the uncapped baseline was not tested |
| target days at full allotment | B2 | upper-tail twCRPS | 3.115 | 3.142 | 1.769 | not defined: the candidate's gain over the uncapped baseline was not tested |
| all cells | B1'* | Brier P(> +5 bp) | 0.0543 | 0.0543 | 0.0461 | -0.000 [-0.000, 0.000] (42 resample(s) without a gain dropped) |
| all cells | B1'* | grid CRPS | 1.843 | 1.843 | 1.601 | -0.001 [-0.003, 0.000] |
| all cells | B1'* | upper-tail twCRPS | 0.991 | 0.991 | 0.845 | -0.002 [-0.006, 0.000] |
| all cells | B2 | Brier P(> +5 bp) | 0.0643 | 0.0643 | 0.0461 | -0.000 [-0.000, 0.000] |
| all cells | B2 | grid CRPS | 2.514 | 2.515 | 1.601 | -0.000 [-0.000, 0.000] |
| all cells | B2 | upper-tail twCRPS | 1.133 | 1.133 | 0.845 | -0.001 [-0.002, 0.000] |

**grid CRPS: (s3c-ann-net) against B1'*-cap, by regime of the target day**

| regime | decision days | B1'*-cap |
|---|---|---|
| 2018-19 | 361 | +0.384 [+0.132, +0.695]: gain |
| 2020 | 255 | +0.144 [-0.134, +0.508]: undecided |
| 2021-23 | 752 | +0.040 [-0.001, +0.078]: undecided |
| 2024 | 254 | +0.315 [+0.118, +0.832]: gain |
| 2025-26 | 249 | +0.728 [+0.462, +1.054]: gain |

**grid CRPS: (s3c-ann-net) against B1'*-cap, by pressure day type of the target day**

| pressure day type | decision days | B1'*-cap |
|---|---|---|
| ordinary | 1855 | +0.159 [+0.077, +0.251]: gain |
| quarter_end_turn | 132 | +0.686 [-0.531, +1.784]: undecided |
| tax_date | 214 | +0.236 [+0.018, +0.772]: gain |
| turn | 360 | +0.676 [+0.361, +1.141]: gain |
| year_end | 43 | +2.290 [-0.094, +11.460]: undecided |

**grid CRPS: (s3c-ann-net) against B2-cap, by regime of the target day**

| regime | decision days | B2-cap |
|---|---|---|
| 2018-19 | 361 | +0.802 [+0.325, +1.335]: gain |
| 2020 | 255 | +1.438 [+0.653, +2.886]: gain |
| 2021-23 | 752 | +0.842 [+0.552, +1.219]: gain |
| 2024 | 254 | +0.310 [+0.108, +0.576]: gain |
| 2025-26 | 249 | +1.437 [+0.302, +3.342]: gain |

**grid CRPS: (s3c-ann-net) against B2-cap, by pressure day type of the target day**

| pressure day type | decision days | B2-cap |
|---|---|---|
| ordinary | 1855 | +0.745 [+0.507, +1.025]: gain |
| quarter_end_turn | 132 | +1.482 [+0.151, +2.980]: gain |
| tax_date | 214 | +2.606 [+1.619, +4.208]: gain |
| turn | 360 | +1.640 [+0.841, +3.584]: gain |
| year_end | 43 | +2.965 [+0.667, +7.034]: gain |

**upper-tail twCRPS: (s3c-ann-net) against B1'*-cap, by regime of the target day**

| regime | decision days | B1'*-cap |
|---|---|---|
| 2018-19 | 361 | +0.345 [+0.086, +0.680]: gain |
| 2020 | 255 | +0.184 [-0.016, +1.278]: undecided |
| 2021-23 | 752 | +0.001 [-0.001, +0.002]: undecided |
| 2024 | 254 | +0.057 [-0.004, +0.767]: undecided |
| 2025-26 | 249 | +0.356 [+0.098, +0.923]: gain |

**upper-tail twCRPS: (s3c-ann-net) against B1'*-cap, by pressure day type of the target day**

| pressure day type | decision days | B1'*-cap |
|---|---|---|
| ordinary | 1855 | +0.078 [+0.006, +0.170]: gain |
| quarter_end_turn | 132 | +0.480 [-0.136, +2.009]: undecided |
| tax_date | 214 | +0.213 [+0.024, +0.977]: gain |
| turn | 360 | +0.441 [+0.183, +0.939]: gain |
| year_end | 43 | +1.731 [-0.151, +12.285]: undecided |

**upper-tail twCRPS: (s3c-ann-net) against B2-cap, by regime of the target day**

| regime | decision days | B2-cap |
|---|---|---|
| 2018-19 | 361 | +0.590 [+0.201, +1.038]: gain |
| 2020 | 255 | +0.776 [+0.384, +1.235]: gain |
| 2021-23 | 752 | -0.004 [-0.036, +0.000]: undecided |
| 2024 | 254 | +0.030 [-0.008, +0.224]: undecided |
| 2025-26 | 249 | +0.575 [+0.070, +2.492]: gain |

**upper-tail twCRPS: (s3c-ann-net) against B2-cap, by pressure day type of the target day**

| pressure day type | decision days | B2-cap |
|---|---|---|
| ordinary | 1855 | +0.154 [+0.043, +0.284]: gain |
| quarter_end_turn | 132 | +0.665 [-0.147, +3.927]: undecided |
| tax_date | 214 | +1.268 [+0.366, +2.987]: gain |
| turn | 360 | +1.014 [+0.320, +3.157]: gain |
| year_end | 43 | +2.199 [-0.350, +9.513]: undecided |

**Brier P(> +5 bp): (s3c-ann-net) against B1'*-cap, by regime of the target day**

| regime | decision days | B1'*-cap |
|---|---|---|
| 2018-19 | 361 | +0.0156 [-0.0191, +0.0459]: undecided |
| 2020 | 255 | +0.0089 [-0.0007, +0.0338]: undecided |
| 2021-23 | 752 | +0.0000 [-0.0000, +0.0002]: undecided |
| 2024 | 254 | +0.0037 [-0.0010, +0.0625]: undecided |
| 2025-26 | 249 | +0.0279 [+0.0043, +0.0850]: gain |

**Brier P(> +5 bp): (s3c-ann-net) against B1'*-cap, by pressure day type of the target day**

| pressure day type | decision days | B1'*-cap |
|---|---|---|
| ordinary | 1855 | +0.0031 [-0.0046, +0.0106]: undecided |
| quarter_end_turn | 132 | +0.0248 [-0.0258, +0.0932]: undecided |
| tax_date | 214 | +0.0159 [+0.0038, +0.0419]: gain |
| turn | 360 | +0.0373 [+0.0156, +0.0813]: gain |
| year_end | 43 | +0.0917 [-0.0001, +0.5450]: undecided |

**Brier P(> +5 bp): (s3c-ann-net) against B2-cap, by regime of the target day**

| regime | decision days | B2-cap |
|---|---|---|
| 2018-19 | 361 | +0.0346 [-0.0072, +0.0860]: undecided |
| 2020 | 255 | +0.0586 [+0.0331, +0.0946]: gain |
| 2021-23 | 752 | -0.0001 [-0.0011, -0.0000]: loss † |
| 2024 | 254 | +0.0040 [-0.0011, +0.0652]: undecided |
| 2025-26 | 249 | +0.0343 [+0.0054, +0.1349]: gain |

**Brier P(> +5 bp): (s3c-ann-net) against B2-cap, by pressure day type of the target day**

| pressure day type | decision days | B2-cap |
|---|---|---|
| ordinary | 1855 | +0.0088 [-0.0013, +0.0206]: undecided |
| quarter_end_turn | 132 | +0.0478 [-0.0042, +0.1722]: undecided |
| tax_date | 214 | +0.0702 [+0.0223, +0.1570]: gain |
| turn | 360 | +0.0763 [+0.0273, +0.1771]: gain |
| year_end | 43 | +0.1628 [+0.0158, +0.5717]: gain |

## What it shows, and what it does not

- **2026, pooled, the candidate against the capped baselines:** grid CRPS: undecided against B1'*-cap, gain against B2-cap; upper-tail twCRPS: gain against B1'*-cap, undecided against B2-cap; Brier P(> +5 bp): gain against B1'*-cap, undecided against B2-cap.
- **2026, pooled, what the cap alone buys the baselines:** grid CRPS: gain for B1'*, gain for B2; upper-tail twCRPS: gain for B1'*, gain for B2; Brier P(> +5 bp): gain for B1'*, undecided for B2.
- **2026, pooled, the share of the candidate's gain the cap alone buys:** B1'*, Brier P(> +5 bp): 0.000 [0.000, 0.000]; B1'*, upper-tail twCRPS: 0.072 [0.041, 0.181]; B2, grid CRPS: 0.105 [0.057, 0.285].
- **development, pooled, the candidate against the capped baselines:** grid CRPS: gain against B1'*-cap, gain against B2-cap; upper-tail twCRPS: gain against B1'*-cap, gain against B2-cap; Brier P(> +5 bp): gain against B1'*-cap, gain against B2-cap.
- **development, pooled, what the cap alone buys the baselines:** grid CRPS: undecided for B1'*, undecided for B2; upper-tail twCRPS: undecided for B1'*, undecided for B2; Brier P(> +5 bp): undecided for B1'*, undecided for B2.
- **development, target days at full allotment:** 10 decision days, so the comparisons are not tested (fewer than 20 decision days); the means are in the table.
- **development, pooled, the share of the candidate's gain the cap alone buys:** B1'*, Brier P(> +5 bp): -0.000 [-0.000, 0.000]; B1'*, grid CRPS: -0.001 [-0.003, 0.000]; B1'*, upper-tail twCRPS: -0.002 [-0.006, 0.000]; B2, Brier P(> +5 bp): -0.000 [-0.000, 0.000]; B2, grid CRPS: -0.000 [-0.000, 0.000]; B2, upper-tail twCRPS: -0.001 [-0.002, 0.000].
- A development figure is paired, carries an interval and is split by regime and by pressure-day type; a pooled figure alone is not a result. The development window decides what this page reads; the 2026 days have been seen by earlier studies and are shown apart.
- Lens C's caveat: the lag-10 HAC standard error is understated about 2x after 2020, so an interval that excludes zero is narrower than it should be.
- Nothing is registered, published or adopted here. The cap is a transform of the baselines' quantiles; no model was fitted or tuned.

## Ruled, and what stays open

- **Ruled** (3 November 2026): the capped versions are the confirmatory benchmarks, the uncapped versions are reported beside them. `protocol_benchmarks` now carries `capped_forecast`, `capped_exceedance`, `b1_calendar_anchor_capped_forecast` and `b2_capped_forecast`.
- **Not done:** B2\*-cap proper (B2\* is #1420's); any change to the scoring protocol's text, to #1394 or to the registration manifest; any verdict. Walked at the 18:00 instant only.

