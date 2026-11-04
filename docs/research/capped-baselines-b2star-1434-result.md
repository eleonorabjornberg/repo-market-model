# The simple baselines with the candidate's SRF cap, with B2*-cap proper: B1'*-cap and B2*-cap (#1440, the finding of #1434)

**Development data, not a verdict.** Hypothesis H5 (primary goal), registration design (benchmarks), step 3. The candidate, (s3c-ann-net), is capped at the Standing Repo Facility line on target days at full allotment. A baseline left uncapped could make part of the candidate's gain a mechanical truncation at that line. This page gives the baselines the candidate's own cap (the same line, read from `metadata/policy_events.json` as public at the decision instant, margin 0 bp) and the candidate's probability rule (b) (`capped_law`, `open_tail`), and scores them beside the uncapped versions. This is the study of #1421 re-run, the same scores, days, intervals and splits, with B2* in the place plain B2 held on #1422's page. Panel digest `4ddc3882cd6d406b11e1088f8ff6195e16dde175a0ad6818abe40dd5bdac8999`; walked at the 18:00 decision instant; seed 1421, 10000 draws.

**Which version is confirmatory is ruled, not open** (Eleonora, 3 November 2026, comment on #1421): the capped baselines are the confirmatory benchmarks and the uncapped versions are reported beside them. This page does not reopen it.

**This page supersedes the B2-cap rows of [#1422's page](capped-baselines-1421-result.md).** That page capped plain B2 in B2\*'s place, because B2\* (#1420) was thought not to be on main; it was (#1423). Here B2\* is `protocol_benchmarks.b2_star_forecast` and B2\*-cap is `b2_star_capped_forecast`. #1422's page is not edited; its B1'\*-cap rows are unchanged and reproduce here to 1e-9. Plain B2 and the stand-in B2-cap are copied from its result beside B2\*-cap in the pooled mean-loss table, labelled as such.

The grid CRPS, the upper-tail twCRPS and the Brier score are losses (lower is better). "Mean d" is the reference's loss less the arm's, so a positive value favours the arm; the interval is scoring protocol v1's studentized stationary bootstrap on decision-day means, read on the bound on mean d (her ruling on #1009) as `gain`, `loss` or `undecided` from whether it excludes zero. † marks a bound taken from the resamples that have a long-run variance (#1239). A group of fewer than 20 decision days is not tested. The pooled mean grid CRPS of the candidate reproduces #1314's record, that of B1'* #1388's result, that of B2* #1420's result, and the candidate, B1'* and B1'*-cap #1422's result, to 1e-9 in both windows (the study refuses to write otherwise).

## Development window (targets up to 2025-12-31; this window decides what the page reads)

1855 decision days, 9275 cells, 50 of them at full allotment. Cells at full allotment where the model's uncapped q99 is above the line, so that the cap changes at least one quantile: B1'* 49, B2* 39; the candidate's own uncapped vector, 50.

**Mean losses, pooled (all cells)**

| model | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|
| (s3c-ann-net) | 1.601 | 0.845 | 0.0461 |
| B1'* (uncapped) | 1.843 | 0.991 | 0.0543 |
| B1'*-cap | 1.843 | 0.991 | 0.0543 |
| B2* (uncapped) | 2.979 | 1.191 | 0.0679 |
| B2*-cap | 2.979 | 1.191 | 0.0679 |
| B2 (plain; the stand-in) (from #1422's result) | 2.514 | 1.133 | 0.0643 |
| B2-cap (plain B2 capped; the stand-in of #1422) (from #1422's result) | 2.515 | 1.133 | 0.0643 |

**The candidate against each baseline, pooled** (mean d: baseline less candidate; positive favours the candidate)

| comparison | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|
| (s3c-ann-net) against B1'*-cap | +0.242 [+0.157, +0.344]: gain | +0.146 [+0.075, +0.253]: gain | +0.0082 [+0.0010, +0.0161]: gain |
| (s3c-ann-net) against B1'* | +0.242 [+0.157, +0.343]: gain | +0.146 [+0.074, +0.253]: gain | +0.0082 [+0.0010, +0.0161]: gain |
| (s3c-ann-net) against B2*-cap | +1.378 [+1.080, +1.747]: gain | +0.346 [+0.223, +0.525]: gain | +0.0218 [+0.0113, +0.0351]: gain |
| (s3c-ann-net) against B2* | +1.378 [+1.080, +1.746]: gain | +0.346 [+0.223, +0.525]: gain | +0.0218 [+0.0113, +0.0351]: gain |

**What the cap alone buys, pooled** (mean d: uncapped baseline less capped baseline; positive favours the cap)

| comparison | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|
| B1'*-cap against B1'* (what the cap alone buys) | -0.0003 [-0.0075, +0.0001]: undecided † | -0.0003 [-0.0075, +0.0001]: undecided † | -8.43e-10 [-1.42e-08, +1.53e-10]: undecided † |
| B2*-cap against B2* (what the cap alone buys) | -0.0002 [-0.0162, +0.0000]: undecided † | -0.0002 [-0.0162, +0.0000]: undecided † | -4.05e-10 [-3.24e-08, +6.99e-11]: undecided † |

**Mean losses, target days at full allotment**

| model | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|
| (s3c-ann-net) | 2.154 | 1.769 | 0.1287 |
| B1'* (uncapped) | 2.358 | 2.254 | 0.2042 |
| B1'*-cap | 2.406 | 2.303 | 0.2042 |
| B2* (uncapped) | 7.274 | 3.467 | 0.2340 |
| B2*-cap | 7.305 | 3.498 | 0.2340 |

**The candidate against each baseline, target days at full allotment**

| comparison | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|
| (s3c-ann-net) against B1'*-cap | fewer than 20 decision days | fewer than 20 decision days | fewer than 20 decision days |
| (s3c-ann-net) against B1'* | fewer than 20 decision days | fewer than 20 decision days | fewer than 20 decision days |
| (s3c-ann-net) against B2*-cap | fewer than 20 decision days | fewer than 20 decision days | fewer than 20 decision days |
| (s3c-ann-net) against B2* | fewer than 20 decision days | fewer than 20 decision days | fewer than 20 decision days |

**What the cap alone buys, target days at full allotment**

| comparison | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|
| B1'*-cap against B1'* (what the cap alone buys) | fewer than 20 decision days | fewer than 20 decision days | fewer than 20 decision days |
| B2*-cap against B2* (what the cap alone buys) | fewer than 20 decision days | fewer than 20 decision days | fewer than 20 decision days |

**The share of the candidate's gain over the uncapped baseline that the cap alone buys** (uncapped less capped, over uncapped less candidate; defined only where the candidate's gain over the uncapped baseline excludes zero on the positive side; interval: percentile, stationary bootstrap of the decision days)

| group | baseline | metric | uncapped | capped | candidate | share of the gain the cap alone buys [90% interval] |
|---|---|---|---|---|---|---|
| target days at full allotment | B1'* | Brier P(> +5 bp) | 0.2042 | 0.2042 | 0.1287 | not defined: the candidate's gain over the uncapped baseline was not tested |
| target days at full allotment | B1'* | grid CRPS | 2.358 | 2.406 | 2.154 | not defined: the candidate's gain over the uncapped baseline was not tested |
| target days at full allotment | B1'* | upper-tail twCRPS | 2.254 | 2.303 | 1.769 | not defined: the candidate's gain over the uncapped baseline was not tested |
| target days at full allotment | B2* | Brier P(> +5 bp) | 0.2340 | 0.2340 | 0.1287 | not defined: the candidate's gain over the uncapped baseline was not tested |
| target days at full allotment | B2* | grid CRPS | 7.274 | 7.305 | 2.154 | not defined: the candidate's gain over the uncapped baseline was not tested |
| target days at full allotment | B2* | upper-tail twCRPS | 3.467 | 3.498 | 1.769 | not defined: the candidate's gain over the uncapped baseline was not tested |
| all cells | B1'* | Brier P(> +5 bp) | 0.0543 | 0.0543 | 0.0461 | -0.000 [-0.000, 0.000] (42 resample(s) without a gain dropped) |
| all cells | B1'* | grid CRPS | 1.843 | 1.843 | 1.601 | -0.001 [-0.003, 0.000] |
| all cells | B1'* | upper-tail twCRPS | 0.991 | 0.991 | 0.845 | -0.002 [-0.006, 0.000] |
| all cells | B2* | Brier P(> +5 bp) | 0.0679 | 0.0679 | 0.0461 | -0.000 [-0.000, 0.000] |
| all cells | B2* | grid CRPS | 2.979 | 2.979 | 1.601 | -0.000 [-0.000, 0.000] |
| all cells | B2* | upper-tail twCRPS | 1.191 | 1.191 | 0.845 | -0.000 [-0.001, 0.000] |

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

**grid CRPS: (s3c-ann-net) against B2*-cap, by regime of the target day**

| regime | decision days | B2*-cap |
|---|---|---|
| 2018-19 | 361 | +0.900 [+0.432, +1.457]: gain |
| 2020 | 255 | +1.189 [+0.736, +2.116]: gain |
| 2021-23 | 752 | +1.688 [+1.213, +2.256]: gain |
| 2024 | 254 | +0.794 [+0.551, +1.151]: gain |
| 2025-26 | 249 | +1.997 [+0.584, +4.417]: gain |

**grid CRPS: (s3c-ann-net) against B2*-cap, by pressure day type of the target day**

| pressure day type | decision days | B2*-cap |
|---|---|---|
| ordinary | 1855 | +1.195 [+0.904, +1.539]: gain |
| quarter_end_turn | 132 | +2.493 [+1.473, +3.967]: gain |
| tax_date | 214 | +2.796 [+1.869, +3.817]: gain |
| turn | 360 | +2.217 [+1.403, +4.116]: gain |
| year_end | 43 | +4.311 [+0.992, +10.558]: gain |

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

**upper-tail twCRPS: (s3c-ann-net) against B2*-cap, by regime of the target day**

| regime | decision days | B2*-cap |
|---|---|---|
| 2018-19 | 361 | +0.640 [+0.245, +1.133]: gain |
| 2020 | 255 | +0.684 [+0.495, +0.866]: gain |
| 2021-23 | 752 | +0.102 [+0.052, +0.177]: gain |
| 2024 | 254 | +0.045 [-0.009, +0.437]: undecided |
| 2025-26 | 249 | +0.695 [+0.109, +2.783]: gain |

**upper-tail twCRPS: (s3c-ann-net) against B2*-cap, by pressure day type of the target day**

| pressure day type | decision days | B2*-cap |
|---|---|---|
| ordinary | 1855 | +0.196 [+0.088, +0.330]: gain |
| quarter_end_turn | 132 | +1.147 [+0.306, +4.386]: gain |
| tax_date | 214 | +1.191 [+0.519, +2.287]: gain |
| turn | 360 | +1.108 [+0.445, +3.395]: gain |
| year_end | 43 | +3.188 [-0.165, +14.106]: undecided |

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

**Brier P(> +5 bp): (s3c-ann-net) against B2*-cap, by regime of the target day**

| regime | decision days | B2*-cap |
|---|---|---|
| 2018-19 | 361 | +0.0379 [-0.0071, +0.0909]: undecided |
| 2020 | 255 | +0.0571 [+0.0451, +0.0729]: gain |
| 2021-23 | 752 | +0.0056 [+0.0028, +0.0105]: gain |
| 2024 | 254 | +0.0058 [-0.0013, +0.1275]: undecided |
| 2025-26 | 249 | +0.0382 [+0.0059, +0.1511]: gain |

**Brier P(> +5 bp): (s3c-ann-net) against B2*-cap, by pressure day type of the target day**

| pressure day type | decision days | B2*-cap |
|---|---|---|
| ordinary | 1855 | +0.0105 [-0.0002, +0.0227]: undecided |
| quarter_end_turn | 132 | +0.0886 [+0.0260, +0.2124]: gain |
| tax_date | 214 | +0.0763 [+0.0307, +0.1358]: gain |
| turn | 360 | +0.0823 [+0.0372, +0.1699]: gain |
| year_end | 43 | +0.2306 [-0.0163, +0.6003]: undecided |

## 2026 days (targets 2026-01-02 to 2026-09-03; full allotment on every target), shown apart

165 decision days, 825 cells, 825 of them at full allotment. Cells at full allotment where the model's uncapped q99 is above the line, so that the cap changes at least one quantile: B1'* 558, B2* 825; the candidate's own uncapped vector, 404.

**Mean losses, pooled (all cells)**

| model | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|
| (s3c-ann-net) | 1.669 | 0.514 | 0.0352 |
| B1'* (uncapped) | 1.865 | 0.631 | 0.0445 |
| B1'*-cap | 1.856 | 0.623 | 0.0445 |
| B2* (uncapped) | 2.650 | 0.493 | 0.0269 |
| B2*-cap | 2.631 | 0.474 | 0.0269 |
| B2 (plain; the stand-in) (from #1422's result) | 2.155 | 0.636 | 0.0356 |
| B2-cap (plain B2 capped; the stand-in of #1422) (from #1422's result) | 2.104 | 0.585 | 0.0356 |

**The candidate against each baseline, pooled** (mean d: baseline less candidate; positive favours the candidate)

| comparison | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|
| (s3c-ann-net) against B1'*-cap | +0.188 [-0.169, +0.415]: undecided | +0.109 [+0.026, +0.210]: gain | +0.0093 [+0.0001, +0.0357]: gain |
| (s3c-ann-net) against B1'* | +0.196 [-0.163, +0.423]: undecided | +0.117 [+0.034, +0.222]: gain | +0.0093 [+0.0001, +0.0357]: gain |
| (s3c-ann-net) against B2*-cap | +0.963 [+0.079, +1.999]: gain | -0.040 [-0.197, +0.107]: undecided | -0.0083 [-0.0282, +0.0004]: undecided |
| (s3c-ann-net) against B2* | +0.981 [+0.097, +2.023]: gain | -0.022 [-0.177, +0.127]: undecided | -0.0082 [-0.0284, +0.0003]: undecided |

**What the cap alone buys, pooled** (mean d: uncapped baseline less capped baseline; positive favours the cap)

| comparison | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|
| B1'*-cap against B1'* (what the cap alone buys) | +0.0084 [+0.0050, +0.0141]: gain | +0.0084 [+0.0050, +0.0141]: gain | +8.68e-08 [+5.67e-08, +1.25e-07]: gain |
| B2*-cap against B2* (what the cap alone buys) | +0.0186 [+0.0136, +0.0249]: gain | +0.0186 [+0.0136, +0.0249]: gain | +2.09e-05 [-2.63e-04, +1.51e-04]: undecided |

Every target of this window is at full allotment, so the group "target days at full allotment" is the pooled group and its tables are not repeated.

**The share of the candidate's gain over the uncapped baseline that the cap alone buys** (uncapped less capped, over uncapped less candidate; defined only where the candidate's gain over the uncapped baseline excludes zero on the positive side; interval: percentile, stationary bootstrap of the decision days)

| group | baseline | metric | uncapped | capped | candidate | share of the gain the cap alone buys [90% interval] |
|---|---|---|---|---|---|---|
| all cells | B1'* | Brier P(> +5 bp) | 0.0445 | 0.0445 | 0.0352 | 0.000 [0.000, 0.000] (132 resample(s) without a gain dropped) |
| all cells | B1'* | grid CRPS | 1.865 | 1.856 | 1.669 | not defined: the candidate's gain over the uncapped baseline is not distinguished from zero |
| all cells | B1'* | upper-tail twCRPS | 0.631 | 0.623 | 0.514 | 0.072 [0.041, 0.181] (17 resample(s) without a gain dropped) |
| all cells | B2* | Brier P(> +5 bp) | 0.0269 | 0.0269 | 0.0352 | not defined: the candidate's gain over the uncapped baseline is not distinguished from zero |
| all cells | B2* | grid CRPS | 2.650 | 2.631 | 1.669 | 0.019 [0.011, 0.053] (13 resample(s) without a gain dropped) |
| all cells | B2* | upper-tail twCRPS | 0.493 | 0.474 | 0.514 | not defined: the candidate's gain over the uncapped baseline is not distinguished from zero |

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

**grid CRPS: (s3c-ann-net) against B2*-cap, by regime of the target day**

| regime | decision days | B2*-cap |
|---|---|---|
| 2025-26 | 165 | +0.963 [+0.079, +1.999]: gain |

**grid CRPS: (s3c-ann-net) against B2*-cap, by pressure day type of the target day**

| pressure day type | decision days | B2*-cap |
|---|---|---|
| ordinary | 165 | +0.959 [+0.050, +1.992]: gain |
| quarter_end_turn | 12 | not tested |
| tax_date | 15 | not tested |
| turn | 34 | +1.306 [-0.952, +3.957]: undecided |
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

**upper-tail twCRPS: (s3c-ann-net) against B2*-cap, by regime of the target day**

| regime | decision days | B2*-cap |
|---|---|---|
| 2025-26 | 165 | -0.040 [-0.197, +0.107]: undecided |

**upper-tail twCRPS: (s3c-ann-net) against B2*-cap, by pressure day type of the target day**

| pressure day type | decision days | B2*-cap |
|---|---|---|
| ordinary | 165 | -0.104 [-0.262, +0.024]: undecided |
| quarter_end_turn | 12 | not tested |
| tax_date | 15 | not tested |
| turn | 34 | +0.578 [-0.134, +1.856]: undecided |
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

**Brier P(> +5 bp): (s3c-ann-net) against B2*-cap, by regime of the target day**

| regime | decision days | B2*-cap |
|---|---|---|
| 2025-26 | 165 | -0.0083 [-0.0282, +0.0004]: undecided |

**Brier P(> +5 bp): (s3c-ann-net) against B2*-cap, by pressure day type of the target day**

| pressure day type | decision days | B2*-cap |
|---|---|---|
| ordinary | 165 | -0.0119 [-0.0338, -0.0038]: loss |
| quarter_end_turn | 12 | not tested |
| tax_date | 15 | not tested |
| turn | 34 | +0.0208 [-0.0068, +0.1355]: undecided |
| year_end | 1 | not tested |

## What it shows, and what it does not

- **development, pooled, the candidate against the capped baselines:** grid CRPS: gain against B1'*-cap, gain against B2*-cap; upper-tail twCRPS: gain against B1'*-cap, gain against B2*-cap; Brier P(> +5 bp): gain against B1'*-cap, gain against B2*-cap.
- **development, pooled, what the cap alone buys the baselines:** grid CRPS: undecided for B1'*, undecided for B2*; upper-tail twCRPS: undecided for B1'*, undecided for B2*; Brier P(> +5 bp): undecided for B1'*, undecided for B2*.
- **development, target days at full allotment:** 10 decision days, so the comparisons are not tested (fewer than 20 decision days); the means are in the table.
- **development, pooled, the share of the candidate's gain the cap alone buys:** B1'*, Brier P(> +5 bp): -0.000 [-0.000, 0.000]; B1'*, grid CRPS: -0.001 [-0.003, 0.000]; B1'*, upper-tail twCRPS: -0.002 [-0.006, 0.000]; B2*, Brier P(> +5 bp): -0.000 [-0.000, 0.000]; B2*, grid CRPS: -0.000 [-0.000, 0.000]; B2*, upper-tail twCRPS: -0.000 [-0.001, 0.000].
- **2026, pooled, the candidate against the capped baselines:** grid CRPS: undecided against B1'*-cap, gain against B2*-cap; upper-tail twCRPS: gain against B1'*-cap, undecided against B2*-cap; Brier P(> +5 bp): gain against B1'*-cap, undecided against B2*-cap.
- **2026, pooled, what the cap alone buys the baselines:** grid CRPS: gain for B1'*, gain for B2*; upper-tail twCRPS: gain for B1'*, gain for B2*; Brier P(> +5 bp): gain for B1'*, undecided for B2*.
- **2026, pooled, the share of the candidate's gain the cap alone buys:** B1'*, Brier P(> +5 bp): 0.000 [0.000, 0.000]; B1'*, upper-tail twCRPS: 0.072 [0.041, 0.181]; B2*, grid CRPS: 0.019 [0.011, 0.053].
- **Against B2\*-cap, pooled, upper-tail twCRPS and Brier P(> +5 bp)** (a loss is lower-is-better; a positive difference favours the candidate): development: upper-tail twCRPS: candidate 0.845, B2*-cap 1.191, paired difference (B2*-cap less candidate) +0.3465 [+0.2234, +0.5249]: gain; Brier P(> +5 bp): candidate 0.0461, B2*-cap 0.0679, paired difference (B2*-cap less candidate) +0.0218 [+0.0113, +0.0351]: gain. 2026: upper-tail twCRPS: candidate 0.514, B2*-cap 0.474, paired difference (B2*-cap less candidate) -0.0402 [-0.1974, +0.1065]: undecided; Brier P(> +5 bp): candidate 0.0352, B2*-cap 0.0269, paired difference (B2*-cap less candidate) -0.0083 [-0.0282, +0.0004]: undecided. Where the reading is `loss` or `undecided`, the candidate does not beat the confirmatory benchmark on that measure there.
- A development figure is paired, carries an interval and is split by regime and by pressure-day type; a pooled figure alone is not a result. The development window decides what this page reads; the 2026 days have been seen by earlier studies and are shown apart.
- Lens C's caveat: the lag-10 HAC standard error is understated about 2x after 2020, so an interval that excludes zero is narrower than it should be.
- Nothing is registered, published or adopted here. The cap is a transform of the baselines' quantiles; no model was fitted or tuned.

## Ruled, and what stays open

- **Ruled** (3 November 2026): the capped versions are the confirmatory benchmarks, the uncapped versions are reported beside them. `protocol_benchmarks` carries `capped_forecast`, `capped_exceedance`, `b1_calendar_anchor_capped_forecast` and, since #1440, `b2_star_capped_forecast`; the stand-in `b2_capped_forecast` is gone.
- **Not done:** any change to the scoring protocol's text, to #1394 or to the confirmation design; no benchmark is adopted, the candidate stays frozen, and no verdict is given. Walked at the 18:00 instant only.

