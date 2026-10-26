# The ordinary-day result of #934 on the five declared regimes (#1023)

**Hypothesis and step:** H1 (regime splits), applied to the ordinary-day result of H5 step 3 (#844, corrected by #934). **Development data only: this is not a verdict** (scoring protocol v1, #640). On Eleonora's ruling on #1011 (20 October 2026): #934 restated on the five regimes of `metadata/evaluation_splits.json`, with the three-regime table kept beside it. **No pooled gain is claimed.**

**provisional: calendar not read at the target day.** The rows that carry the figures here are the models of #934, whose result is row 10 of the provisional register (`docs/research/provisional-calendar-register.md`, class b): the figures below restate #934's cells on the five regimes and stay provisional until #934 is re-run on direct pairs. The register marks this; no figure here is edited (#1169).

Nothing new is modelled: the rows, the reference, the outcome and the ordinary-day definition (`risk_dates.NON_ORDINARY`, read at the target day) are #844's. Each cell is the paired AUROC difference from persistence-logistic on ordinary target days with its 90% stationary-bootstrap percentile interval (block 10, 2000 replications; the interval #934 used, so the two tables compare). Above zero is better than persistence-logistic. `n/a`: fewer than 3 pressure days. `†`: no interval. No day after 2025-12-31 is read: the regime labelled 2025-26 holds the days of 2025, and the declared 2027 regime holds none.

**Ruling recorded (Eleonora, 22 October 2026, comment 6340379028 on PR #1103):** read these AUROC differences on the protocol's studentized one-sided bound as well, beside #934's percentile interval. Each five-regime cell below carries both: the percentile interval, which compares with #934's table, and the studentized one-sided 95% lower bound of the scoring protocol (section 5). The studentization is over target days, the unit the bootstrap resamples (one decision per day), in date order within the cell: the standard error is the Newey-West (Bartlett) one at the protocol's lag 10, of the day-level influence series of the AUROC difference (DeLong placement values, so that the AUROC difference is, to first order, the mean of that series, as `mean(d)` is for a CRPS difference); each resample's difference is divided by its own such standard error, and the bound is the point value less the 95th percentile of those t-draws times the observed standard error. Decision days would be the same days here: a lead's forecasts are scored on their target days. The resamples are the percentile interval's own (same seed, block 10). The bound is one-sided at 5%, the level of each tail of the 90% percentile interval, and a cell with no percentile interval shows no bound.

## Five declared regimes

Regimes: 2018-19 (2018-01-01 to 2019-12-31), 2020 (2020-01-01 to 2020-12-31), 2021-23 (2021-01-01 to 2023-12-31), 2024 (2024-01-01 to 2024-12-31), 2025-26 (2025-01-01 onward, read to 2025-12-31).

### mean reversion (#686)

| lead | 2018-19 | 2020 | 2021-23 | 2024 | 2025-26 |
|---|---|---|---|---|---|
| 1 | +0.077 [+0.020, +0.142] (61 pressure days); studentized lower bound +0.025 | -0.041† (3 pressure days) | n/a (0 pressure days) | n/a (2 pressure days) | +0.015 [+0.000, +0.041] (15 pressure days); studentized lower bound -0.001 |
| 2 | +0.095 [+0.017, +0.174] (61 pressure days); studentized lower bound +0.025 | -0.125† (3 pressure days) | n/a (0 pressure days) | n/a (2 pressure days) | +0.037 [+0.011, +0.088] (15 pressure days); studentized lower bound +0.002 |
| 3 | +0.076 [-0.003, +0.162] (61 pressure days); studentized lower bound +0.002 | -0.099† (3 pressure days) | n/a (0 pressure days) | n/a (2 pressure days) | +0.038 [+0.008, +0.090] (16 pressure days); studentized lower bound +0.002 |
| 4 | +0.075 [-0.017, +0.159] (61 pressure days); studentized lower bound -0.007 | -0.149† (3 pressure days) | n/a (0 pressure days) | n/a (2 pressure days) | +0.033 [+0.001, +0.094] (16 pressure days); studentized lower bound -0.008 |
| 5 | +0.075 [-0.019, +0.169] (61 pressure days); studentized lower bound -0.014 | -0.176† (3 pressure days) | n/a (0 pressure days) | n/a (2 pressure days) | +0.026 [-0.006, +0.083] (16 pressure days); studentized lower bound -0.016 |

### (i) context-pooled residuals (#761)

| lead | 2018-19 | 2020 | 2021-23 | 2024 | 2025-26 |
|---|---|---|---|---|---|
| 1 | +0.083 [+0.027, +0.150] (61 pressure days); studentized lower bound +0.031 | -0.152† (3 pressure days) | n/a (0 pressure days) | n/a (2 pressure days) | +0.017 [+0.003, +0.047] (15 pressure days); studentized lower bound -0.002 |
| 2 | +0.109 [+0.034, +0.193] (61 pressure days); studentized lower bound +0.037 | -0.232† (3 pressure days) | n/a (0 pressure days) | n/a (2 pressure days) | +0.035 [+0.009, +0.092] (15 pressure days); studentized lower bound -0.001 |
| 3 | +0.078 [-0.001, +0.166] (61 pressure days); studentized lower bound +0.000 | -0.161† (3 pressure days) | n/a (0 pressure days) | n/a (2 pressure days) | +0.031 [+0.003, +0.079] (16 pressure days); studentized lower bound -0.005 |
| 4 | +0.076 [-0.017, +0.165] (61 pressure days); studentized lower bound -0.009 | -0.293† (3 pressure days) | n/a (0 pressure days) | n/a (2 pressure days) | +0.023 [-0.006, +0.082] (16 pressure days); studentized lower bound -0.018 |
| 5 | +0.082 [-0.013, +0.177] (61 pressure days); studentized lower bound -0.009 | -0.288† (3 pressure days) | n/a (0 pressure days) | n/a (2 pressure days) | +0.020 [-0.009, +0.073] (16 pressure days); studentized lower bound -0.020 |

### (c) two-part (#634)

| lead | 2018-19 | 2020 | 2021-23 | 2024 | 2025-26 |
|---|---|---|---|---|---|
| 1 | -0.009 [-0.075, +0.056] (61 pressure days); studentized lower bound -0.077 | -0.285† (3 pressure days) | n/a (0 pressure days) | n/a (2 pressure days) | +0.003 [-0.019, +0.045] (15 pressure days); studentized lower bound -0.032 |
| 2 | +0.011 [-0.095, +0.119] (61 pressure days); studentized lower bound -0.147 | -0.201† (3 pressure days) | n/a (0 pressure days) | n/a (2 pressure days) | +0.011 [-0.012, +0.063] (15 pressure days); studentized lower bound -0.030 |
| 3 | -0.024 [-0.119, +0.074] (61 pressure days); studentized lower bound -0.155 | -0.202† (3 pressure days) | n/a (0 pressure days) | n/a (2 pressure days) | +0.008 [-0.020, +0.071] (16 pressure days); studentized lower bound -0.041 |
| 4 | -0.067 [-0.136, +0.009] (61 pressure days); studentized lower bound -0.150 | -0.117† (3 pressure days) | n/a (0 pressure days) | n/a (2 pressure days) | +0.020 [-0.007, +0.075] (16 pressure days); studentized lower bound -0.026 |
| 5 | -0.061 [-0.145, +0.015] (61 pressure days); studentized lower bound -0.168 | -0.196† (3 pressure days) | n/a (0 pressure days) | n/a (2 pressure days) | -0.065 [-0.171, +0.019] (16 pressure days); studentized lower bound -0.419 |

### gbm_funding (#634)

| lead | 2018-19 | 2020 | 2021-23 | 2024 | 2025-26 |
|---|---|---|---|---|---|
| 1 | +0.031 [-0.027, +0.090] (61 pressure days); studentized lower bound -0.021 | +0.072† (3 pressure days) | n/a (0 pressure days) | n/a (2 pressure days) | -0.011 [-0.032, +0.020] (15 pressure days); studentized lower bound -0.058 |
| 2 | +0.078 [+0.003, +0.155] (61 pressure days); studentized lower bound +0.007 | +0.040† (3 pressure days) | n/a (0 pressure days) | n/a (2 pressure days) | -0.010 [-0.043, +0.037] (15 pressure days); studentized lower bound -0.082 |
| 3 | +0.075 [-0.006, +0.164] (61 pressure days); studentized lower bound -0.001 | -0.038† (3 pressure days) | n/a (0 pressure days) | n/a (2 pressure days) | -0.004 [-0.031, +0.040] (16 pressure days); studentized lower bound -0.070 |
| 4 | +0.063 [-0.012, +0.141] (61 pressure days); studentized lower bound -0.002 | -0.091† (3 pressure days) | n/a (0 pressure days) | n/a (2 pressure days) | -0.010 [-0.034, +0.025] (16 pressure days); studentized lower bound -0.072 |
| 5 | +0.068 [-0.031, +0.161] (61 pressure days); studentized lower bound -0.014 | +0.042† (3 pressure days) | n/a (0 pressure days) | n/a (2 pressure days) | -0.026 [-0.051, +0.007] (16 pressure days); studentized lower bound -0.090 |

### Tally of regime-by-lead cells (five regimes, development)

- **mean reversion (#686)**: of 10 regime-by-lead cells with at least 3 pressure days and an interval, above zero in 5, covers zero in 5, below zero in 0.
- **(i) context-pooled residuals (#761)**: of 10 regime-by-lead cells with at least 3 pressure days and an interval, above zero in 5, covers zero in 5, below zero in 0.
- **(c) two-part (#634)**: of 10 regime-by-lead cells with at least 3 pressure days and an interval, above zero in 0, covers zero in 10, below zero in 0.
- **gbm_funding (#634)**: of 10 regime-by-lead cells with at least 3 pressure days and an interval, above zero in 1, covers zero in 9, below zero in 0.

- **mean reversion (#686)**: the studentized one-sided lower bound is above zero in 5 of 10 cells that have one.
- **(i) context-pooled residuals (#761)**: the studentized one-sided lower bound is above zero in 3 of 10 cells that have one.
- **(c) two-part (#634)**: the studentized one-sided lower bound is above zero in 0 of 10 cells that have one.
- **gbm_funding (#634)**: the studentized one-sided lower bound is above zero in 1 of 10 cells that have one.

These lines count cells; they set no threshold.

## The three-regime table of #683/#934, kept

Read from the committed score of #844 (`docs/pivot/ordinary-day-p5-844/score.json`); nothing is rescored and neither published page is edited. Its 2020-24 cell pools 2020, 2021-23 and 2024: its pairs cross regimes, so it is **cross-regime, not a regime result**.

### mean reversion (#686)

| lead | 2018-19 | 2020-24 (cross-regime, not a regime result) | 2025-26 |
|---|---|---|---|
| 1 | +0.077 [+0.020, +0.143] (61 pressure days) | -0.068 [-0.310, +0.036] (5 pressure days) | +0.015 [+0.000, +0.042] (15 pressure days) |
| 2 | +0.095 [+0.021, +0.177] (61 pressure days) | -0.022 [-0.201, +0.148] (5 pressure days) | +0.037 [+0.010, +0.086] (15 pressure days) |
| 3 | +0.076 [-0.003, +0.161] (61 pressure days) | -0.038 [-0.304, +0.164] (5 pressure days) | +0.038 [+0.008, +0.088] (16 pressure days) |
| 4 | +0.075 [-0.017, +0.161] (61 pressure days) | -0.123 [-0.339, -0.027] (5 pressure days) | +0.033 [+0.001, +0.094] (16 pressure days) |
| 5 | +0.075 [-0.020, +0.164] (61 pressure days) | -0.097 [-0.235, -0.030] (5 pressure days) | +0.026 [-0.007, +0.088] (16 pressure days) |

### (i) context-pooled residuals (#761)

| lead | 2018-19 | 2020-24 (cross-regime, not a regime result) | 2025-26 |
|---|---|---|---|
| 1 | +0.083 [+0.026, +0.151] (61 pressure days) | -0.080 [-0.305, +0.038] (5 pressure days) | +0.017 [+0.003, +0.047] (15 pressure days) |
| 2 | +0.109 [+0.039, +0.192] (61 pressure days) | -0.037 [-0.215, +0.142] (5 pressure days) | +0.035 [+0.008, +0.093] (15 pressure days) |
| 3 | +0.078 [-0.002, +0.166] (61 pressure days) | -0.044 [-0.301, +0.162] (5 pressure days) | +0.031 [+0.002, +0.077] (16 pressure days) |
| 4 | +0.076 [-0.015, +0.168] (61 pressure days) | -0.140 [-0.332, -0.055] (5 pressure days) | +0.023 [-0.006, +0.080] (16 pressure days) |
| 5 | +0.082 [-0.013, +0.172] (61 pressure days) | -0.173 [-0.384, -0.057] (5 pressure days) | +0.020 [-0.011, +0.077] (16 pressure days) |

### (c) two-part (#634)

| lead | 2018-19 | 2020-24 (cross-regime, not a regime result) | 2025-26 |
|---|---|---|---|
| 1 | -0.009 [-0.074, +0.059] (61 pressure days) | -0.149 [-0.326, +0.102] (5 pressure days) | +0.003 [-0.020, +0.049] (15 pressure days) |
| 2 | +0.011 [-0.096, +0.120] (61 pressure days) | -0.091 [-0.312, +0.197] (5 pressure days) | +0.011 [-0.012, +0.060] (15 pressure days) |
| 3 | -0.024 [-0.118, +0.073] (61 pressure days) | -0.030 [-0.302, +0.522] (5 pressure days) | +0.008 [-0.021, +0.063] (16 pressure days) |
| 4 | -0.067 [-0.138, +0.009] (61 pressure days) | -0.085 [-0.225, -0.022] (5 pressure days) | +0.020 [-0.008, +0.073] (16 pressure days) |
| 5 | -0.061 [-0.149, +0.015] (61 pressure days) | -0.161 [-0.345, -0.060] (5 pressure days) | -0.065 [-0.161, +0.023] (16 pressure days) |

### gbm_funding (#634)

| lead | 2018-19 | 2020-24 (cross-regime, not a regime result) | 2025-26 |
|---|---|---|---|
| 1 | +0.031 [-0.028, +0.093] (61 pressure days) | -0.027 [-0.230, +0.099] (5 pressure days) | -0.011 [-0.032, +0.023] (15 pressure days) |
| 2 | +0.078 [+0.003, +0.156] (61 pressure days) | +0.021 [-0.143, +0.221] (5 pressure days) | -0.010 [-0.045, +0.035] (15 pressure days) |
| 3 | +0.075 [-0.008, +0.162] (61 pressure days) | -0.017 [-0.237, +0.210] (5 pressure days) | -0.004 [-0.033, +0.039] (16 pressure days) |
| 4 | +0.063 [-0.011, +0.141] (61 pressure days) | -0.102 [-0.263, -0.027] (5 pressure days) | -0.010 [-0.034, +0.026] (16 pressure days) |
| 5 | +0.068 [-0.029, +0.163] (61 pressure days) | -0.111 [-0.317, +0.001] (5 pressure days) | -0.026 [-0.050, +0.009] (16 pressure days) |

### Tally of regime-by-lead cells (three regimes, development)

- **mean reversion (#686)**: of 15 regime-by-lead cells with at least 3 pressure days and an interval, above zero in 5, covers zero in 8, below zero in 2.
- **(i) context-pooled residuals (#761)**: of 15 regime-by-lead cells with at least 3 pressure days and an interval, above zero in 5, covers zero in 8, below zero in 2.
- **(c) two-part (#634)**: of 15 regime-by-lead cells with at least 3 pressure days and an interval, above zero in 0, covers zero in 13, below zero in 2.
- **gbm_funding (#634)**: of 15 regime-by-lead cells with at least 3 pressure days and an interval, above zero in 1, covers zero in 13, below zero in 1.

The 2020-24 cells are counted here as #934 counted them; they are not a regime result.
