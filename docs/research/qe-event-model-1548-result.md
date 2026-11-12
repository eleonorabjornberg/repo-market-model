# An event-conditional quarter-end distribution beside the frozen candidate

Terms such as arm, cell, kill rule, grid CRPS and B1 are defined in the [glossary](glossary.md). Issue numbers and files are in the Record at the end.

## The question

**Does giving the quarter-end target days their own residual distribution, level by level and shrunk toward the pool, repair the candidate's quarter-end bands?** The candidate's 90% band covers too few outcomes around quarter-ends. An earlier arm rescaled the band's width on those days; this one lets the quarter-end days change the band's shape and location as well.

## The answer

Not on the development data: the arm's 90% band covers 0.663 [0.574, 0.747] of the group's cells against 0.601 for the candidate; the gap to 90% is 23.7 percentage points. The arm improved on the candidate's coverage beyond its interval but scored worse on grid CRPS, so under the rule declared before the run it is killed.

## Data

The published panel, with every forecast made at the 18:00 decision. The answer rests on the development window; the 2026 development days are shown at the end and decide nothing.

## Method

On quarter-end and year-end target days the arm replaces the candidate's band with a blend of that band and one built from past quarter-end errors alone, so the band can shift and change shape as well as widen. The fewer past quarter-ends there are, the less weight they get. Every other forecast is the candidate's, unchanged. The arm fails (is killed) if its 90% band does not cover more of the quarter-end outcomes than the candidate's by a margin that excludes chance, or if its forecasts on those days score worse than the candidate's.

## Result on the development window (targets up to 2025-12-31)

Scored decision days: 1,855 (2018-07-19 to 2025-12-23); 89 refits. Group cells: 291, of which the arm changes 251; cells outside the group: 8,984, every one identical to the candidate (the walk fails otherwise). The group holds 30 turn events and 291 cells. **That is few, so every interval is wide.**

### Coverage and tail misses on the group, candidate against arm

The table shows how often each model's 90% band held the outcome on the group and how often the outcome fell outside a tail quantile; the kill rule reads the first row's "arm minus candidate".

| set | cells | events | 90% coverage: candidate | arm | arm minus candidate | below q05 (5%): cand. / arm | above q95 (5%): cand. / arm | below q01 (1%): cand. / arm | above q99 (1%): cand. / arm |
|---|---|---|---|---|---|---|---|---|---|
| group, pooled over h = 1-5 | 291 | 30 | 0.601 [0.498, 0.703] | 0.663 [0.574, 0.747] | +0.062 [+0.010, +0.121] | 0.089 / 0.096 | 0.309 / 0.241 | 0.045 / 0.069 | 0.127 / 0.113 |
| group, h = 1 | 58 | 29 | 0.638 [0.534, 0.741] | 0.672 [0.569, 0.776] | +0.034 [-0.017, +0.086] | 0.086 / 0.086 | 0.276 / 0.241 | 0.017 / 0.052 | 0.155 / 0.121 |
| group, h = 2 | 58 | 29 | 0.638 [0.517, 0.741] | 0.672 [0.569, 0.776] | +0.034 [+0.000, +0.069] | 0.086 / 0.086 | 0.276 / 0.241 | 0.034 / 0.069 | 0.103 / 0.103 |
| group, h = 3 | 58 | 29 | 0.621 [0.517, 0.724] | 0.672 [0.586, 0.759] | +0.052 [-0.034, +0.138] | 0.086 / 0.103 | 0.293 / 0.224 | 0.052 / 0.069 | 0.103 / 0.103 |
| group, h = 4 | 58 | 29 | 0.534 [0.414, 0.655] | 0.638 [0.517, 0.741] | +0.103 [+0.034, +0.172] | 0.103 / 0.103 | 0.362 / 0.259 | 0.069 / 0.086 | 0.121 / 0.121 |
| group, h = 5 | 59 | 30 | 0.576 [0.446, 0.700] | 0.661 [0.542, 0.772] | +0.085 [+0.000, +0.179] | 0.085 / 0.102 | 0.339 / 0.237 | 0.051 / 0.068 | 0.153 / 0.119 |
| group, quarter_end_turn only | 220 | 22 | 0.586 [0.468, 0.705] | 0.668 [0.573, 0.764] | +0.082 [+0.014, +0.164] | 0.077 / 0.086 | 0.336 / 0.245 | 0.041 / 0.055 | 0.109 / 0.100 |
| group, year_end only | 71 | 8 | 0.648 [0.419, 0.845] | 0.648 [0.419, 0.845] | +0.000 [+0.000, +0.000] | 0.127 / 0.127 | 0.225 / 0.225 | 0.056 / 0.113 | 0.183 / 0.155 |
| `quarter_end` days of the calibration study (the group behind its 49.3% figure) | 146 | 30 | 0.493 [0.359, 0.627] | 0.568 [0.440, 0.692] | +0.075 [+0.007, +0.151] | 0.164 / 0.171 | 0.342 / 0.260 | 0.089 / 0.137 | 0.137 / 0.130 |

**The arm's 90% band covers 0.663 [0.574, 0.747] of the group's cells against 0.601 for the candidate; the gap to 90% is 23.7 percentage points.**

### The declared kill

Coverage on the group: +0.062 [+0.010, +0.121] (arm minus candidate, event-cluster 90% interval). The lower end of the interval is above zero, so the arm improves beyond its interval. Grid CRPS on the group: +0.001 [-0.287, +0.352] bp (arm minus candidate). The arm's is above the candidate's, so the arm loses. **Against the declared kill: killed.**

## What it means, and its limits

The page shows what an event-conditional residual distribution on the quarter-end group does to the candidate's coverage, tail misses and CRPS on development days, with the event's own shape and location. It does not show a verdict, an adoption, or that this arm beats the width-only arm (no test between them is run). Thin events are handled by shrinkage and the fallback only; the outer levels of an event pool of a few dozen residuals rest on a handful of events. The candidate stays frozen and nothing is adopted, registered or published. The 2026 days are shown apart and decide nothing.

**Dated note, 11 November 2026 (finding #1559; her ruling of 11 November, decision docket, card f1559-k-1111, option (a) "note").** Beside the sentence above, which stays as written: "an event pool of a few dozen residuals" overstates what the fits held. The table of the development window below ("The event pools, over the window's refits") gives the event pairs per lead as 14.1 on average and 2 to 16 at most, because the candidate trains on a trailing two-year window that holds at most eight quarter-end turns.

## Questions for Eleonora (marked; the defaults change no claim)

**Question 1. Is k = 20 the right shrinkage constant for the event model?** The rule is `w = n / (n + k)`, `n` the event set's training pairs at a refit and lead (a turn gives two pairs per lead). It is the constant of the width-only arm (your 10 November answer), written in the declaration before any score and not tuned on scores. It is a judgment call, so it is yours.

**Options** (the default applies if you have not answered by the next 5 pm batch):

1. **k = 20** (default). Half weight at ten turns. This page.
2. **k = 10.** Less shrinkage. A fresh run with a fresh declaration.
3. **k = 40.** More shrinkage. A fresh run with a fresh declaration.

**Dated note, 11 November 2026 (finding #1559; her ruling of 11 November, decision docket, card f1559-k-1111, option (a) "note").** Beside the options above, which stay as written. With at most 16 event pairs per lead (eight turns in the two-year window; the table of the development window below, "The event pools, over the window's refits"), the weight w = n / (n + k) with k = 20 never passed 16 / 36 = 0.444, and its mean was 0.376. "Half weight at ten turns" describes a weight no refit could reach. Her ruling: k = 20 stands; no figure on this page is re-run or changed; how much history the fit may use is taken up through #1561.

**Question 2. What goes on from here?** This page is one arm of the family on the quarter-end event set. Whether the event model is read against the width-only arm with a paired test (a further run), whether it is extended to the other calendar-event types (turn, tax date, month-end), or whether the family stops, is yours; adopting the arm is not in scope and the 2 November freeze holds.

**Options:** 1. **Read this page and rule on the family** (default; no claim changes). 2. **Run a paired test of this arm against the width-only arm.** 3. **Extend the event model to another event type** (a new declaration). 4. **Stop the family here.**

## Details

**The change.** The event set is every target day whose type is `quarter_end_turn` or `year_end`: the last business day of each calendar quarter and the first after it. On those days the candidate's 23 pool quantiles are replaced by `(1 - w) pool_j + w event_j`, where `event_j` is the empirical quantile of the refit's training residuals whose own target day is in that event set (at that lead), `w = n / (n + k)` and `k = 20`. Each level has its own correction, so the arm carries the event's shape and location shift, where the width-only arm applied one multiplier. With fewer than 10 such residuals the pool is the candidate's, exactly. On every other target day every quantile equals the candidate's, bit for bit, and the walk fails if it does not. The center, the calendar terms, the scale and the fit are the candidate's, on direct pairs; the SRF cap is applied after.

**The kill rule, as declared.** The arm is killed if its 90% coverage on the group does not improve on the candidate's beyond its interval (the lower end of the 90% event-cluster interval of the paired difference, arm minus candidate, is not above zero), or if the arm's mean grid CRPS on the group is above the candidate's. Pooled figures cannot pass or fail it alone, since everything outside the event set is identical.

**The intervals.** The h = 1-5 forecasts aimed at one turn, and the turn's two days, are one cluster. Intervals on the group are 90% percentile intervals of a cluster bootstrap over turn events (2,000 resamples, seed 1548). Against the benchmarks the interval is the studentized stationary bootstrap (mean block 10 business days, 10,000 draws, seed 1548, two-sided 90% interval), and the reading is taken from the bound on mean d. Two caveats carry over: which interval method applies to day types has not been ruled on, and the HAC standard error is understated about 2x after 2020.

## Other tables

### Development window

#### Accuracy of the distribution on the group (paired, same cells)

Grid CRPS and upper-tail twCRPS on the group, in bp; lower is better, so a negative difference favors the arm.

| set | grid CRPS (bp): candidate | arm | arm minus candidate (negative favors the arm) | upper-tail twCRPS (bp): candidate | arm | arm minus candidate |
|---|---|---|---|---|---|---|
| group, pooled over h = 1-5 | 4.722 | 4.723 | +0.001 [-0.287, +0.352] | 3.511 | 3.662 | +0.151 [-0.076, +0.438] |
| group, h = 1 | 4.509 | 4.533 | +0.024 [-0.253, +0.354] | 3.449 | 3.593 | +0.144 [-0.059, +0.385] |
| group, h = 2 | 4.490 | 4.604 | +0.114 [-0.159, +0.449] | 3.527 | 3.727 | +0.200 [-0.010, +0.470] |
| group, h = 3 | 4.724 | 4.777 | +0.053 [-0.268, +0.437] | 3.526 | 3.716 | +0.191 [-0.054, +0.507] |
| group, h = 4 | 4.932 | 4.867 | -0.064 [-0.391, +0.343] | 3.522 | 3.650 | +0.128 [-0.121, +0.465] |
| group, h = 5 | 4.949 | 4.832 | -0.117 [-0.420, +0.247] | 3.530 | 3.623 | +0.093 [-0.134, +0.399] |
| group, quarter_end_turn only | 3.512 | 3.397 | -0.115 [-0.477, +0.301] | 2.136 | 2.201 | +0.065 [-0.199, +0.397] |
| group, year_end only | 8.469 | 8.833 | +0.363 [-0.000, +0.761] | 7.771 | 8.187 | +0.416 [+0.060, +0.788] |
| `quarter_end` days of the calibration study (the group behind its 49.3% figure) | 5.153 | 4.933 | -0.220 [-0.804, +0.297] | 3.964 | 3.840 | -0.124 [-0.690, +0.376] |

#### The event pools, over the window's refits

How much the events had to say at each lead: `w` is the weight the event pool receives, a positive median shift means the events' residuals sit above the pool's, and a span ratio above 1 means they are more spread out.

| lead | event pairs n: mean (least to greatest) | w: mean (least to greatest) | share of refits at the fallback | event pool's median minus the pool's (standardised units): mean | event pool's 90% span over the pool's: mean |
|---|---|---|---|---|---|
| h=1 | 14.1 (2 to 16) | 0.376 (0.000 to 0.444) | 0.13 | +1.116 | 1.655 |
| h=2 | 14.1 (2 to 16) | 0.376 (0.000 to 0.444) | 0.13 | +1.137 | 1.354 |
| h=3 | 14.1 (2 to 16) | 0.376 (0.000 to 0.444) | 0.13 | +1.678 | 1.476 |
| h=4 | 14.1 (2 to 16) | 0.376 (0.000 to 0.444) | 0.13 | +1.882 | 1.592 |
| h=5 | 14.1 (2 to 16) | 0.376 (0.000 to 0.444) | 0.13 | +1.777 | 1.592 |

#### Beside the width-only arm (context only, same cells, no test between the arms)

The width-only arm's figures (k = 20) are copied from its published result and the candidate's column is checked to equal it; no interval or test compares the two arms.

| measure (event set, pooled over h = 1-5) | candidate | width-only arm (k = 20) | this arm (event-conditional) |
|---|---|---|---|
| 90% coverage | 0.601 | 0.646 | 0.663 |
| below q05 (5%) | 0.089 | 0.082 | 0.096 |
| above q95 (5%) | 0.309 | 0.271 | 0.241 |
| below q01 (1%) | 0.045 | 0.024 | 0.069 |
| above q99 (1%) | 0.127 | 0.107 | 0.113 |
| grid CRPS (bp) | 4.722 | 4.616 | 4.723 |
| upper-tail twCRPS (bp) | 3.511 | 3.451 | 3.662 |

#### Pooled, against B1, B1' and B2 (studentized stationary bootstrap)

Both models against each benchmark on all decision days: each cell gives the skill (the share of the benchmark's score the model removes) and then mean d in bp, both with a 90% interval, and ends with the reading taken from the interval of d: **gain** when it lies above zero, **undecided** when it includes zero.

| model against | grid CRPS | upper-tail twCRPS |
|---|---|---|
| (s3c-ann-net) against B1 | +30.0% [+24.0%, +42.5%]; d +0.688 [+0.424, +1.597]: **gain** | +38.6% [+31.0%, +51.9%]; d +0.530 [+0.268, +1.611]: **gain** |
| (s3c-ann-net) against B1' | +13.5% [+8.4%, +17.9%]; d +0.249 [+0.161, +0.353]: **gain** | +15.5% [+6.3%, +23.6%]; d +0.154 [+0.079, +0.264]: **gain** |
| (s3c-ann-net) against B2 | +36.3% [+25.7%, +45.4%]; d +0.913 [+0.668, +1.229]: **gain** | +25.4% [+10.8%, +38.1%]; d +0.288 [+0.166, +0.458]: **gain** |
| (s3c-ann-net-ev) against B1 | +30.0% [+23.8%, +42.2%]; d +0.688 [+0.422, +1.582]: **gain** | +38.2% [+30.5%, +52.0%]; d +0.526 [+0.262, +1.605]: **gain** |
| (s3c-ann-net-ev) against B1' | +13.5% [+8.1%, +18.0%]; d +0.249 [+0.157, +0.354]: **gain** | +15.0% [+6.2%, +22.9%]; d +0.150 [+0.074, +0.257]: **gain** |
| (s3c-ann-net-ev) against B2 | +36.3% [+25.8%, +45.3%]; d +0.913 [+0.669, +1.224]: **gain** | +25.0% [+10.9%, +37.3%]; d +0.283 [+0.162, +0.452]: **gain** |

#### The same comparison, split

The pooled comparison repeated by regime and by pressure-day type, the candidate's table first and the arm's second for each benchmark; the two differ only through the group's cells.

##### By regime: (s3c-ann-net) against B1

| regime | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| 2018-19 | 361 | +37.1% [+28.0%, +57.4%]; d +2.149 [+0.977, +9.098]: **gain** | +39.3% [+29.2%, +58.7%]; d +2.074 [+0.891, +8.932]: **gain** | n/a |
| 2020 | 251 | +9.6% [-18.0%, +21.2%]; d +0.158 [-0.144, +0.398]: **undecided** | +21.9% [+6.0%, +44.9%]; d +0.162 [-0.004, +0.918]: **undecided (skill interval: gain)** | n/a |
| 2021-23 | 748 | +9.2% [+3.7%, +13.8%]; d +0.064 [+0.031, +0.096]: **gain** | +23.0% [-32.3%, +47.9%]; d +0.002 [-0.001, +0.004]: **undecided** | n/a |
| 2024 | 250 | +33.4% [+26.7%, +42.1%]; d +0.539 [+0.284, +1.189]: **gain** | +39.6% [+22.0%, +79.0%]; d +0.111 [+0.011, +1.224]: **gain** | n/a |
| 2025-26 | 249 | +33.6% [+25.9%, +41.7%]; d +1.128 [+0.727, +1.685]: **gain** | +42.2% [+31.0%, +53.3%]; d +0.676 [+0.236, +1.665]: **gain** | n/a |

##### By regime: (s3c-ann-net-ev) against B1

| regime | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| 2018-19 | 361 | +37.1% [+27.9%, +57.7%]; d +2.147 [+0.973, +9.083]: **gain** | +39.3% [+29.1%, +58.9%]; d +2.072 [+0.886, +8.923]: **gain** | n/a |
| 2020 | 251 | +6.8% [-30.2%, +20.0%]; d +0.112 [-0.309, +0.359]: **undecided** | +16.2% [-6.4%, +40.1%]; d +0.120 [-0.050, +0.667]: **undecided** | n/a |
| 2021-23 | 748 | +9.3% [+3.8%, +13.9%]; d +0.065 [+0.031, +0.098]: **gain** | +17.7% [-42.0%, +44.0%]; d +0.002 [-0.001, +0.003]: **undecided** | n/a |
| 2024 | 250 | +34.7% [+27.2%, +43.8%]; d +0.560 [+0.292, +1.242]: **gain** | +42.0% [+23.4%, +84.2%]; d +0.118 [+0.011, +1.015]: **gain** | n/a |
| 2025-26 | 249 | +34.4% [+26.6%, +42.4%]; d +1.153 [+0.749, +1.703]: **gain** | +42.5% [+31.2%, +53.6%]; d +0.681 [+0.239, +1.670]: **gain** | n/a |

##### By regime: (s3c-ann-net) against B1'

| regime | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| 2018-19 | 361 | +10.0% [+0.5%, +17.9%]; d +0.406 [+0.145, +0.728]: **gain** | +10.7% [-0.9%, +19.9%]; d +0.384 [+0.118, +0.729]: **gain (skill interval: undecided)** | n/a |
| 2020 | 251 | +7.7% [-17.6%, +22.8%]; d +0.125 [-0.167, +0.475]: **undecided** | +24.3% [+7.6%, +52.2%]; d +0.186 [-0.025, +1.347]: **undecided (skill interval: gain)** | n/a |
| 2021-23 | 748 | +4.6% [-1.3%, +9.8%]; d +0.030 [-0.006, +0.067]: **undecided** | +2.2% [-38.1%, +24.9%]; d +0.000 [-0.003, +0.002]: **undecided** | n/a |
| 2024 | 250 | +22.0% [+13.8%, +33.2%]; d +0.302 [+0.126, +0.733]: **gain** | +18.4% [-0.0%, +56.6%]; d +0.038 [-0.002, +0.543]: **undecided** | n/a |
| 2025-26 | 249 | +25.5% [+17.9%, +33.3%]; d +0.764 [+0.497, +1.097]: **gain** | +29.3% [+17.4%, +44.1%]; d +0.383 [+0.109, +1.029]: **gain** | n/a |

##### By regime: (s3c-ann-net-ev) against B1'

| regime | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| 2018-19 | 361 | +10.0% [+0.8%, +17.6%]; d +0.404 [+0.141, +0.728]: **gain** | +10.6% [-0.6%, +19.6%]; d +0.382 [+0.113, +0.727]: **gain (skill interval: undecided)** | n/a |
| 2020 | 251 | +4.9% [-28.9%, +21.1%]; d +0.078 [-0.295, +0.397]: **undecided** | +18.8% [-5.1%, +47.4%]; d +0.144 [-0.067, +1.010]: **undecided** | n/a |
| 2021-23 | 748 | +4.7% [-1.1%, +10.0%]; d +0.031 [-0.005, +0.068]: **undecided** | -4.5% [-45.5%, +19.1%]; d -0.000 [-0.004, +0.001]: **undecided** | n/a |
| 2024 | 250 | +23.4% [+15.7%, +33.1%]; d +0.323 [+0.140, +0.756]: **gain** | +21.6% [+10.7%, +39.4%]; d +0.045 [+0.001, +0.667]: **gain** | n/a |
| 2025-26 | 249 | +26.4% [+18.2%, +34.3%]; d +0.789 [+0.513, +1.126]: **gain** | +29.6% [+17.7%, +45.3%]; d +0.387 [+0.114, +1.046]: **gain** | n/a |

##### By regime: (s3c-ann-net) against B2

| regime | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| 2018-19 | 361 | +17.6% [+3.0%, +30.8%]; d +0.779 [+0.318, +1.305]: **gain** | +14.9% [+1.0%, +27.3%]; d +0.561 [+0.185, +0.995]: **gain** | n/a |
| 2020 | 251 | +48.8% [+25.5%, +69.3%]; d +1.421 [+0.619, +2.910]: **gain** | +56.2% [-4.5%, +82.6%]; d +0.743 [+0.375, +1.187]: **gain (skill interval: undecided)** | n/a |
| 2021-23 | 748 | +56.9% [+44.4%, +68.4%]; d +0.837 [+0.546, +1.208]: **gain** | -133.3% [-551.0%, -38.1%]; d -0.004 [-0.035, +0.000]: **undecided (skill interval: loss)** | n/a |
| 2024 | 250 | +20.6% [+8.6%, +30.7%]; d +0.279 [+0.086, +0.516]: **gain** | skill undefined; d +0.016 [-0.006, +0.307]: **undecided (skill interval: skill undefined)** | n/a |
| 2025-26 | 249 | +40.2% [+18.4%, +57.6%]; d +1.496 [+0.396, +3.437]: **gain** | +39.6% [+29.0%, +55.1%]; d +0.607 [+0.112, +2.410]: **gain** | n/a |

##### By regime: (s3c-ann-net-ev) against B2

| regime | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| 2018-19 | 361 | +17.6% [+3.2%, +30.4%]; d +0.778 [+0.317, +1.294]: **gain** | +14.9% [+1.3%, +26.9%]; d +0.559 [+0.186, +0.990]: **gain** | n/a |
| 2020 | 251 | +47.2% [+23.5%, +68.8%]; d +1.375 [+0.601, +2.838]: **gain** | +53.1% [-6.5%, +81.2%]; d +0.701 [+0.345, +1.146]: **gain (skill interval: undecided)** | n/a |
| 2021-23 | 748 | +57.0% [+44.5%, +68.5%]; d +0.838 [+0.547, +1.210]: **gain** | -149.4% [-523.1%, -60.8%]; d -0.004 [-0.036, -0.000]: **loss** | n/a |
| 2024 | 250 | +22.1% [+10.1%, +31.7%]; d +0.299 [+0.104, +0.542]: **gain** | skill undefined; d +0.023 [-0.003, +0.420]: **undecided (skill interval: skill undefined)** | n/a |
| 2025-26 | 249 | +40.8% [+19.6%, +57.9%]; d +1.521 [+0.431, +3.473]: **gain** | +39.9% [+29.2%, +55.4%]; d +0.611 [+0.117, +2.447]: **gain** | n/a |

##### By pressure-day type of the target day: (s3c-ann-net) against B1

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 1591 | +34.1% [+24.2%, +59.6%]; d +0.666 [+0.389, +1.678]: **gain** | +49.9% [+36.4%, +76.7%]; d +0.537 [+0.259, +1.682]: **gain** | n/a |
| quarter_end_turn | 44 | +19.5% [-18.1%, +30.7%]; d +0.849 [-0.268, +2.007]: **undecided** | skill undefined; d +0.537 [-0.004, +2.530]: **undecided (skill interval: skill undefined)** | n/a |
| tax_date | 89 | +7.5% [-5.3%, +18.3%]; d +0.414 [-0.016, +1.129]: **undecided** | +6.4% [-8.8%, +17.1%]; d +0.298 [+0.006, +1.408]: **gain (skill interval: undecided)** | n/a |
| turn | 120 | +35.2% [+21.1%, +50.8%]; d +0.916 [+0.220, +2.129]: **gain** | +31.5% [+12.5%, +52.6%]; d +0.458 [-0.005, +2.058]: **undecided (skill interval: gain)** | n/a |
| year_end | 15 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

##### By pressure-day type of the target day: (s3c-ann-net-ev) against B1

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 1591 | +34.1% [+24.2%, +59.6%]; d +0.666 [+0.389, +1.678]: **gain** | +49.9% [+36.4%, +76.7%]; d +0.537 [+0.259, +1.682]: **gain** | n/a |
| quarter_end_turn | 44 | +22.1% [-63.9%, +43.3%]; d +0.964 [-0.896, +2.648]: **undecided** | skill undefined; d +0.472 [-0.264, +1.723]: **undecided (skill interval: skill undefined)** | n/a |
| tax_date | 89 | +7.5% [-5.3%, +18.3%]; d +0.414 [-0.016, +1.129]: **undecided** | +6.4% [-8.8%, +17.1%]; d +0.298 [+0.006, +1.408]: **gain (skill interval: undecided)** | n/a |
| turn | 120 | +35.2% [+21.1%, +50.8%]; d +0.916 [+0.220, +2.129]: **gain** | +31.5% [+12.5%, +52.6%]; d +0.458 [-0.005, +2.058]: **undecided (skill interval: gain)** | n/a |
| year_end | 15 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

##### By pressure-day type of the target day: (s3c-ann-net) against B1'

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 1591 | +12.3% [+6.8%, +17.1%]; d +0.180 [+0.094, +0.278]: **gain** | +15.8% [+3.2%, +25.8%]; d +0.101 [+0.022, +0.203]: **gain** | n/a |
| quarter_end_turn | 44 | +17.0% [-22.6%, +28.8%]; d +0.721 [-0.383, +1.789]: **undecided** | skill undefined; d +0.493 [-0.007, +2.321]: **undecided (skill interval: skill undefined)** | n/a |
| tax_date | 89 | +5.9% [-0.2%, +11.6%]; d +0.320 [-0.032, +1.043]: **undecided** | +6.1% [-4.4%, +12.8%]; d +0.281 [+0.008, +1.407]: **gain (skill interval: undecided)** | n/a |
| turn | 120 | +29.5% [+18.6%, +40.1%]; d +0.705 [+0.190, +1.485]: **gain** | +31.8% [+9.4%, +44.0%]; d +0.466 [+0.082, +1.393]: **gain** | n/a |
| year_end | 15 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

##### By pressure-day type of the target day: (s3c-ann-net-ev) against B1'

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 1591 | +12.3% [+6.8%, +17.1%]; d +0.180 [+0.094, +0.278]: **gain** | +15.8% [+3.2%, +25.8%]; d +0.101 [+0.022, +0.203]: **gain** | n/a |
| quarter_end_turn | 44 | +19.8% [-70.2%, +41.8%]; d +0.836 [-1.025, +2.448]: **undecided** | skill undefined; d +0.428 [-0.281, +1.563]: **undecided (skill interval: skill undefined)** | n/a |
| tax_date | 89 | +5.9% [-0.2%, +11.6%]; d +0.320 [-0.032, +1.043]: **undecided** | +6.1% [-4.4%, +12.8%]; d +0.281 [+0.008, +1.407]: **gain (skill interval: undecided)** | n/a |
| turn | 120 | +29.5% [+18.6%, +40.1%]; d +0.705 [+0.190, +1.485]: **gain** | +31.8% [+9.4%, +44.0%]; d +0.466 [+0.082, +1.393]: **gain** | n/a |
| year_end | 15 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

##### By pressure-day type of the target day: (s3c-ann-net) against B2

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 1591 | +36.2% [+26.5%, +44.9%]; d +0.731 [+0.485, +1.028]: **gain** | +21.9% [+5.6%, +34.5%]; d +0.151 [+0.041, +0.284]: **gain** | n/a |
| quarter_end_turn | 44 | +30.0% [-10.8%, +48.5%]; d +1.502 [-0.014, +2.871]: **undecided** | skill undefined; d +0.670 [-0.089, +4.716]: **undecided (skill interval: skill undefined)** | n/a |
| tax_date | 89 | +34.3% [-69.4%, +59.4%]; d +2.655 [+1.475, +4.923]: **gain (skill interval: undecided)** | skill undefined; d +1.295 [+0.091, +4.495]: **gain (skill interval: skill undefined)** | n/a |
| turn | 120 | +49.2% [+29.5%, +68.8%]; d +1.634 [+0.809, +3.999]: **gain** | +50.4% [-4.9%, +86.5%]; d +1.013 [+0.234, +4.061]: **gain (skill interval: undecided)** | n/a |
| year_end | 15 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

##### By pressure-day type of the target day: (s3c-ann-net-ev) against B2

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 1591 | +36.2% [+26.5%, +44.9%]; d +0.731 [+0.485, +1.028]: **gain** | +21.9% [+5.6%, +34.5%]; d +0.151 [+0.041, +0.284]: **gain** | n/a |
| quarter_end_turn | 44 | +32.3% [+11.6%, +46.2%]; d +1.618 [+0.832, +2.376]: **gain** | skill undefined; d +0.605 [+0.066, +2.889]: **gain (skill interval: skill undefined)** | n/a |
| tax_date | 89 | +34.3% [-69.4%, +59.4%]; d +2.655 [+1.475, +4.923]: **gain (skill interval: undecided)** | skill undefined; d +1.295 [+0.091, +4.495]: **gain (skill interval: skill undefined)** | n/a |
| turn | 120 | +49.2% [+29.5%, +68.8%]; d +1.634 [+0.809, +3.999]: **gain** | +50.4% [-4.9%, +86.5%]; d +1.013 [+0.234, +4.061]: **gain (skill interval: undecided)** | n/a |
| year_end | 15 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

#### By pressure-day type: the arm against the candidate (identical outside the group)

The arm scored against the candidate, so a positive d favors the arm.

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 1591 | identical | identical | n/a |
| quarter_end_turn | 44 | +3.3% [-40.7%, +24.0%]; d +0.115 [-0.721, +0.753]: **undecided** | skill undefined; d -0.065 [-0.831, +0.218] (5 of 10000 resamples dropped): **undecided (skill interval: skill undefined)** | n/a |
| tax_date | 89 | identical | identical | n/a |
| turn | 120 | identical | identical | n/a |
| year_end | 15 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

#### Against B3 (the published record's five levels, grid CRPS on those five)

Grid CRPS (bp) on the five quantile levels the published model forecasts; reported, with no decision rule.

| decision days | days | B3 | (s3c-ann-net) | (s3c-ann-net-ev) | (s3c-ann-net) against B3 | (s3c-ann-net-ev) against B3 |
|---|---|---|---|---|---|---|
| 2018-19 | 362 | 4.078 | 3.635 | 3.642 | +10.9% [+0.5%, +18.4%]; d +0.443 [+0.215, +0.681]: **gain** | +10.7% [+0.8%, +18.1%]; d +0.436 [+0.206, +0.677]: **gain** |
| 2020 | 251 | 1.437 | 1.490 | 1.530 | -3.7% [-25.7%, +7.3%]; d -0.053 [-0.372, +0.101]: **undecided** | -6.5% [-37.6%, +6.0%]; d -0.093 [-0.559, +0.086]: **undecided** |
| 2021-23 | 748 | 0.741 | 0.646 | 0.644 | +12.8% [+3.3%, +22.3%]; d +0.095 [+0.025, +0.191]: **gain** | +13.1% [+3.6%, +22.5%]; d +0.097 [+0.027, +0.194]: **gain** |
| 2024 | 250 | 1.356 | 1.117 | 1.101 | +17.6% [+11.4%, +22.8%]; d +0.239 [+0.118, +0.479]: **gain** | +18.8% [+10.9%, +26.2%]; d +0.255 [+0.124, +0.533]: **gain** |
| 2025-26 | 244 | 2.581 | 2.112 | 2.077 | +18.2% [+10.3%, +25.2%]; d +0.469 [+0.247, +0.714]: **gain** | +19.5% [+11.3%, +26.5%]; d +0.504 [+0.272, +0.752]: **gain** |
| all decision days | 1855 | 1.811 | 1.600 | 1.599 | +11.7% [+6.5%, +16.0%]; d +0.212 [+0.136, +0.291]: **gain** | +11.7% [+6.3%, +16.1%]; d +0.212 [+0.132, +0.295]: **gain** |

Groups of fewer than 20 days, listed and not tested: pressure_day_type/year_end (15).

### The 2026 development days (targets 2026-01-02 to 2026-09-03)

These days are kept apart from the development window. The kill rule is not read on them and they decide nothing.

Scored decision days: 165 (2025-12-31 to 2026-08-27); 97 refits. Group cells: 21, of which the arm changes 21; cells outside the group: 804, every one identical to the candidate (the walk fails otherwise). The group holds 3 turn events and 21 cells. **That is few, so every interval is wide.**

#### Coverage and tail misses on the group, candidate against arm

The table shows how often each model's 90% band held the outcome on the group and how often the outcome fell outside a tail quantile; the kill rule reads the first row's "arm minus candidate".

| set | cells | events | 90% coverage: candidate | arm | arm minus candidate | below q05 (5%): cand. / arm | above q95 (5%): cand. / arm | below q01 (1%): cand. / arm | above q99 (1%): cand. / arm |
|---|---|---|---|---|---|---|---|---|---|
| group, pooled over h = 1-5 | 21 | 3 | 0.952 [0.833, 1.000] | 0.952 [0.833, 1.000] | +0.000 [+0.000, +0.000] | 0.000 / 0.000 | 0.048 / 0.048 | 0.000 / 0.000 | 0.048 / 0.048 |
| group, h = 1 | 5 | 3 | 0.800 [0.500, 1.000] | 0.800 [0.500, 1.000] | +0.000 [+0.000, +0.000] | 0.000 / 0.000 | 0.200 / 0.200 | 0.000 / 0.000 | 0.200 / 0.200 |
| group, h = 2 | 4 | 2 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | +0.000 [+0.000, +0.000] | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 |
| group, h = 3 | 4 | 2 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | +0.000 [+0.000, +0.000] | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 |
| group, h = 4 | 4 | 2 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | +0.000 [+0.000, +0.000] | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 |
| group, h = 5 | 4 | 2 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | +0.000 [+0.000, +0.000] | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 |
| group, quarter_end_turn only | 20 | 2 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | +0.000 [+0.000, +0.000] | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 |
| group, year_end only | 1 | 1 | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | +0.000 [+0.000, +0.000] | 0.000 / 0.000 | 1.000 / 1.000 | 0.000 / 0.000 | 1.000 / 1.000 |
| `quarter_end` days of the calibration study (the group behind its 49.3% figure) | 10 | 2 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | +0.000 [+0.000, +0.000] | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 | 0.000 / 0.000 |

**The arm's 90% band covers 0.952 [0.833, 1.000] of the group's cells against 0.952 for the candidate; the gap to 90% is -5.2 percentage points (negative: the band covers more than 90%).**

#### The declared kill (shown apart; the kill is read on the development window only, and these days decide nothing)

Coverage on the group: +0.000 [+0.000, +0.000] (arm minus candidate, event-cluster 90% interval). The lower end of the interval is not above zero, so the arm does not improve beyond its interval. Grid CRPS on the group: +0.187 [-0.418, +0.595] bp over 3 events (arm minus candidate): an interval that spans zero. **The declared kill is read on the development window only; it is not called on these days.**

#### Accuracy of the distribution on the group (paired, same cells)

Grid CRPS and upper-tail twCRPS on the group, in bp; lower is better, so a negative difference favors the arm.

| set | grid CRPS (bp): candidate | arm | arm minus candidate (negative favors the arm) | upper-tail twCRPS (bp): candidate | arm | arm minus candidate |
|---|---|---|---|---|---|---|
| group, pooled over h = 1-5 | 1.011 | 1.198 | +0.187 [-0.418, +0.595] | 0.759 | 1.094 | +0.335 [-0.240, +0.691] |
| group, h = 1 | 1.435 | 0.953 | -0.481 [-1.154, -0.033] | 1.002 | 0.776 | -0.227 [-0.965, +0.266] |
| group, h = 2 | 0.889 | 1.060 | +0.172 [-0.202, +0.545] | 0.569 | 0.922 | +0.353 [+0.030, +0.677] |
| group, h = 3 | 0.856 | 1.332 | +0.476 [+0.052, +0.900] | 0.698 | 1.260 | +0.563 [+0.191, +0.934] |
| group, h = 4 | 0.875 | 1.375 | +0.500 [+0.036, +0.964] | 0.715 | 1.316 | +0.601 [+0.204, +0.999] |
| group, h = 5 | 0.894 | 1.330 | +0.436 [-0.082, +0.955] | 0.752 | 1.276 | +0.524 [+0.064, +0.984] |
| group, quarter_end_turn only | 0.909 | 1.195 | +0.286 [-0.143, +0.715] | 0.646 | 1.086 | +0.440 [+0.067, +0.814] |
| group, year_end only | 3.057 | 1.265 | -1.791 [-1.791, -1.791] | 3.024 | 1.249 | -1.775 [-1.775, -1.775] |
| `quarter_end` days of the calibration study (the group behind its 49.3% figure) | 0.845 | 1.391 | +0.546 [+0.135, +0.956] | 0.835 | 1.387 | +0.552 [+0.146, +0.957] |

#### The event pools, over the window's refits

How much the events had to say at each lead: `w` is the weight the event pool receives, a positive median shift means the events' residuals sit above the pool's, and a span ratio above 1 means they are more spread out.

| lead | event pairs n: mean (least to greatest) | w: mean (least to greatest) | share of refits at the fallback | event pool's median minus the pool's (standardised units): mean | event pool's 90% span over the pool's: mean |
|---|---|---|---|---|---|
| h=1 | 14.2 (2 to 16) | 0.382 (0.000 to 0.444) | 0.12 | +1.230 | 1.671 |
| h=2 | 14.2 (2 to 16) | 0.382 (0.000 to 0.444) | 0.12 | +1.233 | 1.393 |
| h=3 | 14.2 (2 to 16) | 0.382 (0.000 to 0.444) | 0.12 | +1.733 | 1.500 |
| h=4 | 14.2 (2 to 16) | 0.382 (0.000 to 0.444) | 0.12 | +1.906 | 1.603 |
| h=5 | 14.2 (2 to 16) | 0.382 (0.000 to 0.444) | 0.12 | +1.809 | 1.606 |

#### Beside the width-only arm (context only, same cells, no test between the arms)

The width-only arm's figures (k = 20) are copied from its published result and the candidate's column is checked to equal it; no interval or test compares the two arms.

| measure (event set, pooled over h = 1-5) | candidate | width-only arm (k = 20) | this arm (event-conditional) |
|---|---|---|---|
| 90% coverage | 0.952 | 0.952 | 0.952 |
| below q05 (5%) | 0.000 | 0.000 | 0.000 |
| above q95 (5%) | 0.048 | 0.048 | 0.048 |
| below q01 (1%) | 0.000 | 0.000 | 0.000 |
| above q99 (1%) | 0.048 | 0.048 | 0.048 |
| grid CRPS (bp) | 1.011 | 1.162 | 1.198 |
| upper-tail twCRPS (bp) | 0.759 | 0.849 | 1.094 |

#### Pooled, against B1, B1' and B2 (studentized stationary bootstrap)

Both models against each benchmark on all decision days: each cell gives the skill (the share of the benchmark's score the model removes) and then mean d in bp, both with a 90% interval, and ends with the reading taken from the interval of d: **gain** when it lies above zero, **undecided** when it includes zero.

| model against | grid CRPS | upper-tail twCRPS |
|---|---|---|
| (s3c-ann-net) against B1 | +22.7% [-0.2%, +35.8%]; d +0.491 [+0.133, +0.814]: **gain (skill interval: undecided)** | +37.7% [+23.8%, +51.8%]; d +0.311 [+0.134, +0.681]: **gain** |
| (s3c-ann-net) against B1' | +10.7% [-12.9%, +22.7%]; d +0.200 [-0.143, +0.428]: **undecided** | +17.2% [+4.4%, +27.9%]; d +0.107 [+0.016, +0.224]: **gain** |
| (s3c-ann-net) against B2 | +22.6% [+3.9%, +41.4%]; d +0.486 [+0.120, +0.940]: **gain** | +19.1% [-6.4%, +36.9%]; d +0.122 [-0.041, +0.240]: **undecided** |
| (s3c-ann-net-ev) against B1 | +22.5% [+0.1%, +35.7%]; d +0.486 [+0.132, +0.811]: **gain** | +36.7% [+22.2%, +52.0%]; d +0.303 [+0.124, +0.687]: **gain** |
| (s3c-ann-net-ev) against B1' | +10.5% [-13.0%, +22.2%]; d +0.196 [-0.145, +0.422]: **undecided** | +15.9% [+3.1%, +26.7%]; d +0.099 [+0.008, +0.213]: **gain** |
| (s3c-ann-net-ev) against B2 | +22.3% [+3.6%, +41.5%]; d +0.481 [+0.114, +0.939]: **gain** | +17.8% [-6.8%, +35.5%]; d +0.113 [-0.044, +0.233]: **undecided** |

#### The same comparison, split

The pooled comparison repeated by regime and by pressure-day type, the candidate's table first and the arm's second for each benchmark; the two differ only through the group's cells.

##### By pressure-day type of the target day: (s3c-ann-net) against B1

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 146 | +20.1% [-7.3%, +38.3%]; d +0.432 [+0.023, +0.871]: **gain (skill interval: undecided)** | +41.5% [+23.9%, +61.9%]; d +0.342 [+0.120, +1.048]: **gain** | n/a |
| quarter_end_turn | 4 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| tax_date | 6 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| turn | 12 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| year_end | 1 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

##### By pressure-day type of the target day: (s3c-ann-net-ev) against B1

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 146 | +20.1% [-7.3%, +38.3%]; d +0.432 [+0.023, +0.871]: **gain (skill interval: undecided)** | +41.5% [+23.9%, +61.9%]; d +0.342 [+0.120, +1.048]: **gain** | n/a |
| quarter_end_turn | 4 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| tax_date | 6 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| turn | 12 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| year_end | 1 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

##### By pressure-day type of the target day: (s3c-ann-net) against B1'

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 146 | +5.8% [-23.1%, +19.3%]; d +0.105 [-0.326, +0.352]: **undecided** | +11.0% [-7.6%, +25.2%]; d +0.059 [-0.042, +0.191]: **undecided** | n/a |
| quarter_end_turn | 4 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| tax_date | 6 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| turn | 12 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| year_end | 1 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

##### By pressure-day type of the target day: (s3c-ann-net-ev) against B1'

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 146 | +5.8% [-23.1%, +19.3%]; d +0.105 [-0.326, +0.352]: **undecided** | +11.0% [-7.6%, +25.2%]; d +0.059 [-0.042, +0.191]: **undecided** | n/a |
| quarter_end_turn | 4 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| tax_date | 6 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| turn | 12 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| year_end | 1 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

##### By pressure-day type of the target day: (s3c-ann-net) against B2

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 146 | +19.6% [-0.6%, +38.8%]; d +0.419 [+0.015, +0.866]: **gain (skill interval: undecided)** | -1.7% [-44.2%, +22.4%]; d -0.008 [-0.213, +0.111]: **undecided** | n/a |
| quarter_end_turn | 4 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| tax_date | 6 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| turn | 12 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| year_end | 1 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

##### By pressure-day type of the target day: (s3c-ann-net-ev) against B2

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 146 | +19.6% [-0.6%, +38.8%]; d +0.419 [+0.015, +0.866]: **gain (skill interval: undecided)** | -1.7% [-44.2%, +22.4%]; d -0.008 [-0.213, +0.111]: **undecided** | n/a |
| quarter_end_turn | 4 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| tax_date | 6 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| turn | 12 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| year_end | 1 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

#### By pressure-day type: the arm against the candidate (identical outside the group)

The arm scored against the candidate, so a positive d favors the arm.

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 146 | identical | identical | n/a |
| quarter_end_turn | 4 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| tax_date | 6 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| turn | 12 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| year_end | 1 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

#### Against B3 (the published record's five levels, grid CRPS on those five)

Grid CRPS (bp) on the five quantile levels the published model forecasts; reported, with no decision rule.

The published record holds no decision day of this window with all five leads, so B3 is not scored here.


Groups of fewer than 20 days, listed and not tested: pressure_day_type/quarter_end_turn (4), pressure_day_type/tax_date (6), pressure_day_type/turn (12), pressure_day_type/year_end (1).

## Addendum of 11 November 2026 (#1572): the arm's gain by regime of the event

#1548's declaration promised, as its third reading rule, the arm's gain by regime of the event. This section is that table. It re-reads the walk above: the same panel, refits and forecasts, nothing fitted again, no new forecast and no figure above changed. **The kill stays as declared** (above): this section does not re-read it, move it or apply it to a cell. Nothing here is a verdict, a choice or an adoption, and (s3c-ann-net) stays frozen. Generated by `scripts/qe_event_regime_1572.py page` from `docs/research/qe-event-regime-1572/result.json`, not edited by hand; settled-questions register: #1548 is recorded as run and no entry splits it by event regime.

**How to read it.** A cell is the group's cells (the target days of type `quarter_end_turn` or `year_end`, h = 1 to 5) of one set in one regime. The regime of an event is the declared regime (`metadata/evaluation_splits.json`) of the calendar date of the quarter-end the event is named for; a year-end's two days belong to the regime of the December that names it. Each cell gives the candidate's figure, the arm's, and d, the arm minus the candidate on the same cells, with its 90% event-cluster interval (whole events resampled, 2,000 resamples, seed 1548, the method of #1548). The h = 1 to 5 forecasts aimed at one turn are one event, so the events column is the number of independent turns behind a cell. A cell of fewer than 5 events is flagged: its interval is narrower than its evidence, and a bootstrap over so few events can return a degenerate interval (a difference that is exactly zero in every event has an interval of [+0.000, +0.000], which is not a finding). The flag is a reading aid, not a rule. The all-regimes rows equal the figures of #1548 above (group CRPS, the 22 turns' coverage, the 8 year-ends' twCRPS), and the script refuses to write if they do not.

### The development window

Group cells 291; the cells below are exactly these, cut by set and regime (the regime cells of each set add up to its all-regimes row).

**Coverage and tail misses**

| set | regime of the event | events | cells | flag | 90% coverage: cand. / arm; d [interval] | above q95 (5%): cand. / arm; d [interval] | below q01 (1%): cand. / arm; d [interval] |
|---|---|---|---|---|---|---|---|
| group (turns and year-ends) | all regimes | 30 | 291 |  | 0.601 / 0.663; d +0.062 [+0.010, +0.121] | 0.309 / 0.241; d -0.069 [-0.124, -0.018] | 0.045 / 0.069; d +0.024 [+0.007, +0.045] |
| group (turns and year-ends) | 2018-19 | 6 | 60 |  | 0.500 / 0.483; d -0.017 [-0.050, +0.000] | 0.417 / 0.417; d +0.000 [+0.000, +0.000] | 0.033 / 0.067; d +0.033 [+0.000, +0.100] |
| group (turns and year-ends) | 2020 | 4 | 40 | **few events (4)** | 0.550 / 0.550; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 0.275 / 0.350; d +0.075 [+0.000, +0.150] |
| group (turns and year-ends) | 2021-23 | 12 | 120 |  | 0.742 / 0.750; d +0.008 [-0.042, +0.067] | 0.233 / 0.217; d -0.017 [-0.067, +0.033] | 0.000 / 0.017; d +0.017 [+0.000, +0.050] |
| group (turns and year-ends) | 2024 | 4 | 40 | **few events (4)** | 0.425 / 0.700; d +0.275 [+0.000, +0.600] | 0.575 / 0.300; d -0.275 [-0.600, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] |
| group (turns and year-ends) | 2025-26 | 4 | 31 | **few events (4)** | 0.548 / 0.774; d +0.226 [+0.000, +0.364] | 0.452 / 0.226; d -0.226 [-0.364, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] |
| quarter-end turns | all regimes | 22 | 220 |  | 0.586 / 0.668; d +0.082 [+0.014, +0.164] | 0.336 / 0.245; d -0.091 [-0.168, -0.023] | 0.041 / 0.055; d +0.014 [+0.000, +0.032] |
| quarter-end turns | 2018-19 | 4 | 40 | **few events (4)** | 0.625 / 0.600; d -0.025 [-0.050, +0.000] | 0.375 / 0.375; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] |
| quarter-end turns | 2020 | 3 | 30 | **few events (3)** | 0.533 / 0.533; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 0.300 / 0.333; d +0.033 [+0.000, +0.067] |
| quarter-end turns | 2021-23 | 9 | 90 |  | 0.711 / 0.722; d +0.011 [-0.056, +0.078] | 0.256 / 0.233; d -0.022 [-0.089, +0.044] | 0.000 / 0.022; d +0.022 [+0.000, +0.067] |
| quarter-end turns | 2024 | 3 | 30 | **few events (3)** | 0.233 / 0.600; d +0.367 [+0.100, +0.633] | 0.767 / 0.400; d -0.367 [-0.633, -0.100] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] |
| quarter-end turns | 2025-26 | 3 | 30 | **few events (3)** | 0.567 / 0.800; d +0.233 [+0.100, +0.367] | 0.433 / 0.200; d -0.233 [-0.367, -0.100] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] |
| year-ends | all regimes | 8 | 71 |  | 0.648 / 0.648; d +0.000 [+0.000, +0.000] | 0.225 / 0.225; d +0.000 [+0.000, +0.000] | 0.056 / 0.113; d +0.056 [+0.000, +0.113] |
| year-ends | 2018-19 | 2 | 20 | **few events (2)** | 0.250 / 0.250; d +0.000 [+0.000, +0.000] | 0.500 / 0.500; d +0.000 [+0.000, +0.000] | 0.100 / 0.200; d +0.100 [+0.000, +0.200] |
| year-ends | 2020 | 1 | 10 | **few events (1)** | 0.600 / 0.600; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 0.200 / 0.400; d +0.200 [+0.200, +0.200] |
| year-ends | 2021-23 | 3 | 30 | **few events (3)** | 0.833 / 0.833; d +0.000 [+0.000, +0.000] | 0.167 / 0.167; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] |
| year-ends | 2024 | 1 | 10 | **few events (1)** | 1.000 / 1.000; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] |
| year-ends | 2025-26 | 1 | 1 | **few events (1)** | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 1.000 / 1.000; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] |

**Accuracy of the distribution**

| set | regime of the event | events | cells | flag | grid CRPS: cand. / arm; d [interval] (negative favours the arm) | upper-tail twCRPS: cand. / arm; d [interval] (negative favours the arm) |
|---|---|---|---|---|---|---|
| group (turns and year-ends) | all regimes | 30 | 291 |  | 4.722 / 4.723; d +0.001 [-0.287, +0.352] | 3.511 / 3.662; d +0.151 [-0.076, +0.438] |
| group (turns and year-ends) | 2018-19 | 6 | 60 |  | 12.697 / 12.860; d +0.163 [-0.226, +0.714] | 12.612 / 12.762; d +0.150 [-0.223, +0.673] |
| group (turns and year-ends) | 2020 | 4 | 40 | **few events (4)** | 4.485 / 5.799; d +1.313 [+0.276, +3.354] | 2.076 / 3.290; d +1.214 [+0.275, +2.970] |
| group (turns and year-ends) | 2021-23 | 12 | 120 |  | 1.097 / 1.048; d -0.049 [-0.095, -0.008] | 0.003 / 0.009; d +0.006 [+0.000, +0.017] |
| group (turns and year-ends) | 2024 | 4 | 40 | **few events (4)** | 4.245 / 3.857; d -0.388 [-1.157, +0.319] | 2.724 / 2.747; d +0.023 [-0.454, +0.501] |
| group (turns and year-ends) | 2025-26 | 4 | 31 | **few events (4)** | 4.233 / 2.929; d -1.304 [-1.759, -0.873] | 2.340 / 1.847; d -0.494 [-0.800, -0.043] |
| quarter-end turns | all regimes | 22 | 220 |  | 3.512 / 3.397; d -0.115 [-0.477, +0.301] | 2.136 / 2.201; d +0.065 [-0.199, +0.397] |
| quarter-end turns | 2018-19 | 4 | 40 | **few events (4)** | 6.018 / 5.848; d -0.170 [-0.339, +0.000] | 5.950 / 5.782; d -0.168 [-0.335, +0.000] |
| quarter-end turns | 2020 | 3 | 30 | **few events (3)** | 5.398 / 7.061; d +1.663 [+0.298, +3.028] | 2.621 / 4.133; d +1.512 [+0.292, +2.733] |
| quarter-end turns | 2021-23 | 9 | 90 |  | 1.095 / 1.058; d -0.038 [-0.080, +0.003] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] |
| quarter-end turns | 2024 | 3 | 30 | **few events (3)** | 5.073 / 4.250; d -0.822 [-1.346, -0.298] | 3.092 / 2.791; d -0.301 [-0.606, +0.003] |
| quarter-end turns | 2025-26 | 3 | 30 | **few events (3)** | 3.974 / 2.627; d -1.348 [-1.692, -1.003] | 2.018 / 1.508; d -0.510 [-0.788, -0.232] |
| year-ends | all regimes | 8 | 71 |  | 8.469 / 8.833; d +0.363 [-0.000, +0.761] | 7.771 / 8.187; d +0.416 [+0.060, +0.788] |
| year-ends | 2018-19 | 2 | 20 | **few events (2)** | 26.056 / 26.883; d +0.827 [+0.000, +1.655] | 25.937 / 26.722; d +0.785 [+0.000, +1.570] |
| year-ends | 2020 | 1 | 10 | **few events (1)** | 1.748 / 2.011; d +0.263 [+0.263, +0.263] | 0.441 / 0.762; d +0.320 [+0.320, +0.320] |
| year-ends | 2021-23 | 3 | 30 | **few events (3)** | 1.103 / 1.019; d -0.084 [-0.165, -0.003] | 0.013 / 0.037; d +0.023 [+0.000, +0.046] |
| year-ends | 2024 | 1 | 10 | **few events (1)** | 1.764 / 2.678; d +0.914 [+0.914, +0.914] | 1.619 / 2.616; d +0.997 [+0.997, +0.997] |
| year-ends | 2025-26 | 1 | 1 | **few events (1)** | 12.001 / 12.000; d -0.001 [-0.001, -0.001] | 12.001 / 12.000; d -0.001 [-0.001, -0.001] |

Cells resting on few events (under 5): group (turns and year-ends), 2020 (4); group (turns and year-ends), 2024 (4); group (turns and year-ends), 2025-26 (4); quarter-end turns, 2018-19 (4); quarter-end turns, 2020 (3); quarter-end turns, 2024 (3); quarter-end turns, 2025-26 (3); year-ends, 2018-19 (2); year-ends, 2020 (1); year-ends, 2021-23 (3); year-ends, 2024 (1); year-ends, 2025-26 (1).

Regime cells whose grid CRPS interval of d excludes zero: group (turns and year-ends), 2020 (+1.313 [+0.276, +3.354], 4 events); group (turns and year-ends), 2021-23 (-0.049 [-0.095, -0.008], 12 events); group (turns and year-ends), 2025-26 (-1.304 [-1.759, -0.873], 4 events); quarter-end turns, 2020 (+1.663 [+0.298, +3.028], 3 events); quarter-end turns, 2024 (-0.822 [-1.346, -0.298], 3 events); quarter-end turns, 2025-26 (-1.348 [-1.692, -1.003], 3 events); year-ends, 2021-23 (-0.084 [-0.165, -0.003], 3 events). Whose coverage interval of d excludes zero: quarter-end turns, 2024 (+0.367 [+0.100, +0.633], 3 events); quarter-end turns, 2025-26 (+0.233 [+0.100, +0.367], 3 events). Whose upper-tail twCRPS interval of d excludes zero: group (turns and year-ends), 2020 (+1.214 [+0.275, +2.970], 4 events); group (turns and year-ends), 2025-26 (-0.494 [-0.800, -0.043], 4 events); quarter-end turns, 2020 (+1.512 [+0.292, +2.733], 3 events); quarter-end turns, 2025-26 (-0.510 [-0.788, -0.232], 3 events). A cell of a single event resamples to itself, so its interval is a point and it is left out of these lists. With this many cells, several intervals are expected to exclude zero by chance, and none was chosen in advance.

### The 2026 development days (decide nothing)

Group cells 21; the cells below are exactly these, cut by set and regime (the regime cells of each set add up to its all-regimes row).

**Coverage and tail misses**

| set | regime of the event | events | cells | flag | 90% coverage: cand. / arm; d [interval] | above q95 (5%): cand. / arm; d [interval] | below q01 (1%): cand. / arm; d [interval] |
|---|---|---|---|---|---|---|---|
| group (turns and year-ends) | all regimes | 3 | 21 | **few events (3)** | 0.952 / 0.952; d +0.000 [+0.000, +0.000] | 0.048 / 0.048; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] |
| group (turns and year-ends) | 2018-19 | 0 | 0 | none | n/a | n/a | n/a |
| group (turns and year-ends) | 2020 | 0 | 0 | none | n/a | n/a | n/a |
| group (turns and year-ends) | 2021-23 | 0 | 0 | none | n/a | n/a | n/a |
| group (turns and year-ends) | 2024 | 0 | 0 | none | n/a | n/a | n/a |
| group (turns and year-ends) | 2025-26 | 3 | 21 | **few events (3)** | 0.952 / 0.952; d +0.000 [+0.000, +0.000] | 0.048 / 0.048; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] |
| quarter-end turns | all regimes | 2 | 20 | **few events (2)** | 1.000 / 1.000; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] |
| quarter-end turns | 2018-19 | 0 | 0 | none | n/a | n/a | n/a |
| quarter-end turns | 2020 | 0 | 0 | none | n/a | n/a | n/a |
| quarter-end turns | 2021-23 | 0 | 0 | none | n/a | n/a | n/a |
| quarter-end turns | 2024 | 0 | 0 | none | n/a | n/a | n/a |
| quarter-end turns | 2025-26 | 2 | 20 | **few events (2)** | 1.000 / 1.000; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] |
| year-ends | all regimes | 1 | 1 | **few events (1)** | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 1.000 / 1.000; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] |
| year-ends | 2018-19 | 0 | 0 | none | n/a | n/a | n/a |
| year-ends | 2020 | 0 | 0 | none | n/a | n/a | n/a |
| year-ends | 2021-23 | 0 | 0 | none | n/a | n/a | n/a |
| year-ends | 2024 | 0 | 0 | none | n/a | n/a | n/a |
| year-ends | 2025-26 | 1 | 1 | **few events (1)** | 0.000 / 0.000; d +0.000 [+0.000, +0.000] | 1.000 / 1.000; d +0.000 [+0.000, +0.000] | 0.000 / 0.000; d +0.000 [+0.000, +0.000] |

**Accuracy of the distribution**

| set | regime of the event | events | cells | flag | grid CRPS: cand. / arm; d [interval] (negative favours the arm) | upper-tail twCRPS: cand. / arm; d [interval] (negative favours the arm) |
|---|---|---|---|---|---|---|
| group (turns and year-ends) | all regimes | 3 | 21 | **few events (3)** | 1.011 / 1.198; d +0.187 [-0.418, +0.595] | 0.759 / 1.094; d +0.335 [-0.240, +0.691] |
| group (turns and year-ends) | 2018-19 | 0 | 0 | none | n/a | n/a |
| group (turns and year-ends) | 2020 | 0 | 0 | none | n/a | n/a |
| group (turns and year-ends) | 2021-23 | 0 | 0 | none | n/a | n/a |
| group (turns and year-ends) | 2024 | 0 | 0 | none | n/a | n/a |
| group (turns and year-ends) | 2025-26 | 3 | 21 | **few events (3)** | 1.011 / 1.198; d +0.187 [-0.418, +0.595] | 0.759 / 1.094; d +0.335 [-0.240, +0.691] |
| quarter-end turns | all regimes | 2 | 20 | **few events (2)** | 0.909 / 1.195; d +0.286 [-0.143, +0.715] | 0.646 / 1.086; d +0.440 [+0.067, +0.814] |
| quarter-end turns | 2018-19 | 0 | 0 | none | n/a | n/a |
| quarter-end turns | 2020 | 0 | 0 | none | n/a | n/a |
| quarter-end turns | 2021-23 | 0 | 0 | none | n/a | n/a |
| quarter-end turns | 2024 | 0 | 0 | none | n/a | n/a |
| quarter-end turns | 2025-26 | 2 | 20 | **few events (2)** | 0.909 / 1.195; d +0.286 [-0.143, +0.715] | 0.646 / 1.086; d +0.440 [+0.067, +0.814] |
| year-ends | all regimes | 1 | 1 | **few events (1)** | 3.057 / 1.265; d -1.791 [-1.791, -1.791] | 3.024 / 1.249; d -1.775 [-1.775, -1.775] |
| year-ends | 2018-19 | 0 | 0 | none | n/a | n/a |
| year-ends | 2020 | 0 | 0 | none | n/a | n/a |
| year-ends | 2021-23 | 0 | 0 | none | n/a | n/a |
| year-ends | 2024 | 0 | 0 | none | n/a | n/a |
| year-ends | 2025-26 | 1 | 1 | **few events (1)** | 3.057 / 1.265; d -1.791 [-1.791, -1.791] | 3.024 / 1.249; d -1.775 [-1.775, -1.775] |

Cells resting on few events (under 5): group (turns and year-ends), 2025-26 (3); quarter-end turns, 2025-26 (2); year-ends, 2025-26 (1).

Regime cells whose grid CRPS interval of d excludes zero: none. Whose coverage interval of d excludes zero: none. Whose upper-tail twCRPS interval of d excludes zero: quarter-end turns, 2025-26 (+0.440 [+0.067, +0.814], 2 events). A cell of a single event resamples to itself, so its interval is a point and it is left out of these lists. With this many cells, several intervals are expected to exclude zero by chance, and none was chosen in advance.

### What this adds and does not add

It adds where the group figures of #1548 come from: which regimes and which kind of turn carry the coverage gain and the CRPS and twCRPS differences, and how many events each rests on. It does not change the declared kill, which compares the group's point difference in grid CRPS and the coverage interval and stays as declared; it does not test one regime against another, correct for the number of cells read, or say that a regime's gain would recur. It is development data (scoring protocol v1), not a verdict. The ruling on the quarter-end family (#1561 waits on it) is hers.

## Record

- Study: #1548. Hypothesis and step: H5 (primary goal), step 3, her ruling of 10 November 2026 (an event-conditional distribution model in place of B).
- Status: **development data, not a verdict** (scoring protocol v1, #640). (s3c-ann-net) stays frozen; nothing is adopted, registered or published and no claim changes.
- Generated by `scripts/qe_event_model_1548.py page` from `docs/research/qe-event-model-1548/result.json`, not edited by hand; declared in `metadata/qe_event_model_1548.json` before any score.
- Panel digest `4ddc3882cd6d406b11e1088f8ff6195e16dde175a0ad6818abe40dd5bdac8999`.
- Reproduction: the candidate's pooled mean grid CRPS equals #1314's 18:00 record to 1e-9 (development 1.601162, 2026 1.668524), or the script refused to write this record.
- Where the parts come from: the target-day labels, #959; the width-only arm (arm A), #1531; the quarter-end diagnosis and its location shift, #1533; the `quarter_end` group and its 49.3% figure, #1363; the development window, #1145 and #1241; the 2026 development days, #1229 and #1252.
- Open or inherited rulings: the day-type interval method, where #1228 has not ruled; the reading from the mean-d bound, her ruling on #1009; the understated HAC standard error, #958.
