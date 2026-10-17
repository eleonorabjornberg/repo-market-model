# Reliability slope within regimes, #632's rows on the ordinary days (#786)

Pooled slopes mislead here (#670): a regime with no pressure day (2021-23) forecasts near 0 and adds a long, well-ordered stretch at the bottom of the curve, which raises the pooled slope. Read calibration within a regime. A cell with no pressure day has no slope. Figures here are development, not a verdict.

Intercept and slope of `logit P(y = 1) = intercept + slope * logit(p)` (1 and 0 for a reliable forecast), 90% stationary-bootstrap intervals (block length 10, 2000 replications); `undefined` where the cell has no pressure day, the forecast is constant there or the fit has no maximum; no interval where the cell has too few events to give one. Regimes: 2018-19, 2020-24 (which holds 2021-23, with no pressure day) and 2025-26.

## h = 1: 1603 days, 101 above +5 bp

### `risk_gbm+settle+h41`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.16 [0.13, 0.21] | -0.70 [-1.24, -0.28] |
| 2018-19 | 320 | 74 | 0.09 [0.05, 0.13] | -0.12 [-0.74, 0.49] |
| 2020-24 | 1069 | 7 | 0.24† | -2.09† |
| 2025-26 | 214 | 20 | 0.23 [0.16, 0.39] | +0.60 [-0.60, 1.83] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.16 [0.13, 0.21] | -0.70 [-1.24, -0.28] |
| scarcity state 0 | 891 | 3 | 0.29† | -2.04† |
| scarcity state 1 | 268 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 8 | 0.09† | +0.01† |
| scarcity state 3 | 410 | 90 | 0.10 [0.06, 0.14] | -0.05 [-0.62, 0.50] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm+settle+h41+dist_roll`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.16 [0.13, 0.21] | -0.67 [-1.19, -0.26] |
| 2018-19 | 320 | 74 | 0.09 [0.05, 0.13] | -0.07 [-0.69, 0.54] |
| 2020-24 | 1069 | 7 | 0.24† | -2.07† |
| 2025-26 | 214 | 20 | 0.22 [0.15, 0.36] | +0.36 [-0.80, 1.50] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.16 [0.13, 0.21] | -0.67 [-1.19, -0.26] |
| scarcity state 0 | 891 | 3 | 0.30† | -1.98† |
| scarcity state 1 | 268 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 8 | 0.10† | +0.15† |
| scarcity state 3 | 410 | 90 | 0.11 [0.07, 0.15] | +0.03 [-0.54, 0.56] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm+every_day+gate+settle+h41+iorb+tailcap75`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.12 [0.09, 0.17] | -1.25 [-1.78, -0.83] |
| 2018-19 | 320 | 74 | 0.06 [0.02, 0.11] | -0.51 [-1.09, 0.04] |
| 2020-24 | 1069 | 7 | 0.24† | -2.48† |
| 2025-26 | 214 | 20 | 0.23 [0.16, 0.39] | +0.60 [-0.60, 1.83] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.12 [0.09, 0.17] | -1.25 [-1.78, -0.83] |
| scarcity state 0 | 891 | 3 | 0.10† | -4.48† |
| scarcity state 1 | 268 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 8 | 0.09† | +0.01† |
| scarcity state 3 | 410 | 90 | 0.08 [0.04, 0.13] | -0.32 [-0.83, 0.16] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `spread_q_gbm+settle+h41+dist_roll`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.12 [0.08, 0.16] | -1.30 [-1.91, -0.86] |
| 2018-19 | 320 | 74 | 0.09 [0.05, 0.14] | -0.08 [-0.74, 0.56] |
| 2020-24 | 1069 | 7 | 0.15† | -3.32† |
| 2025-26 | 214 | 20 | 0.20 [0.13, 0.34] | +0.07 [-1.09, 1.04] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.12 [0.08, 0.16] | -1.30 [-1.91, -0.86] |
| scarcity state 0 | 891 | 3 | 0.16† | -3.85† |
| scarcity state 1 | 268 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 8 | 0.11† | +0.28† |
| scarcity state 3 | 410 | 90 | 0.11 [0.07, 0.15] | +0.05 [-0.58, 0.64] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `spread_q_gbm+two_part+settle+h41+dist_roll`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.50 [0.31, 0.84] | -0.71 [-1.36, -0.16] |
| 2018-19 | 320 | 74 | 0.33 [0.06, 0.93] | -0.60 [-1.33, 0.13] |
| 2020-24 | 1069 | 7 | 0.25† | -2.99† |
| 2025-26 | 214 | 20 | 0.82 [0.63, 1.09] | +0.11 [-0.91, 0.73] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.50 [0.31, 0.84] | -0.71 [-1.36, -0.16] |
| scarcity state 0 | 891 | 3 | 0.08† | -4.82† |
| scarcity state 1 | 268 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 8 | 0.64 [0.34, 1.39] | +0.56 [-0.64, 2.05] |
| scarcity state 3 | 410 | 90 | 0.38 [0.10, 0.86] | -0.61 [-1.27, 0.02] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.17 [0.13, 0.21] | -0.66 [-1.19, -0.23] |
| 2018-19 | 320 | 74 | 0.09 [0.05, 0.13] | -0.12 [-0.73, 0.51] |
| 2020-24 | 1069 | 7 | 0.26† | -1.89† |
| 2025-26 | 214 | 20 | 0.28 [0.19, 0.46] | +1.16 [-0.07, 2.57] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.17 [0.13, 0.21] | -0.66 [-1.19, -0.23] |
| scarcity state 0 | 891 | 3 | 0.36† | -1.31† |
| scarcity state 1 | 268 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 8 | 0.15† | +0.78† |
| scarcity state 3 | 410 | 90 | 0.10 [0.07, 0.14] | -0.02 [-0.61, 0.53] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `ngboost_laplace`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.61 [0.48, 0.77] | -0.25 [-0.71, 0.14] |
| 2018-19 | 320 | 74 | 0.63 [0.44, 0.87] | -0.18 [-0.66, 0.26] |
| 2020-24 | 1069 | 7 | 0.27 [-0.02, 0.61] | -2.84 [-5.83, -1.30] |
| 2025-26 | 214 | 20 | 0.80 [0.62, 1.89] | +1.39 [0.46, 5.25] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.61 [0.48, 0.77] | -0.25 [-0.71, 0.14] |
| scarcity state 0 | 891 | 3 | 0.29† | -2.54† |
| scarcity state 1 | 268 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 8 | 1.91† | +6.64† |
| scarcity state 3 | 410 | 90 | 0.59 [0.42, 0.78] | -0.17 [-0.61, 0.21] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `calendar_climatology`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.53 [-0.38, 1.34] | -1.51 [-3.80, 0.17] |
| 2018-19 | 320 | 74 | 0.68 [0.22, 1.19] | +0.31 [-0.83, 1.56] |
| 2020-24 | 1069 | 7 | 1.04† | -2.84† |
| 2025-26 | 214 | 20 | 3.50† | +7.54† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.53 [-0.38, 1.34] | -1.51 [-3.80, 0.17] |
| scarcity state 0 | 891 | 3 | -13.01† | -40.65† |
| scarcity state 1 | 268 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 8 | -2.67† | -8.62† |
| scarcity state 3 | 410 | 90 | 0.34 [-0.10, 0.77] | -0.53 [-1.68, 0.57] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `persistence_logistic`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 1.05 [0.74, 1.41] | -0.19 [-1.05, 0.61] |
| 2018-19 | 320 | 74 | 0.56 [0.28, 1.11] | -0.21 [-0.98, 0.85] |
| 2020-24 | 1069 | 7 | 0.78 [-0.03, 1.48] | -2.70 [-6.04, -1.13] |
| 2025-26 | 214 | 20 | 0.98 [0.73, 1.54] | +0.00 [-1.00, 1.10] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 1.05 [0.74, 1.41] | -0.19 [-1.05, 0.61] |
| scarcity state 0 | 891 | 3 | 0.89† | -2.39† |
| scarcity state 1 | 268 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 8 | 0.82† | +0.40† |
| scarcity state 3 | 410 | 90 | 0.50 [0.29, 0.89] | -0.46 [-1.08, 0.32] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

## h = 2: 1603 days, 101 above +5 bp

### `risk_gbm+settle+h41`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.16 [0.12, 0.21] | -0.68 [-1.26, -0.24] |
| 2018-19 | 320 | 74 | 0.09 [0.05, 0.14] | -0.09 [-0.78, 0.55] |
| 2020-24 | 1069 | 7 | 0.23† | -2.20† |
| 2025-26 | 214 | 20 | 0.25 [0.17, 0.43] | +0.84 [-0.36, 2.20] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.16 [0.12, 0.21] | -0.68 [-1.26, -0.24] |
| scarcity state 0 | 891 | 2 | 0.32† | -2.11† |
| scarcity state 1 | 268 | 1 | undefined | undefined |
| scarcity state 2 | 35 | 9 | 0.19† | +1.36† |
| scarcity state 3 | 409 | 89 | 0.10 [0.07, 0.15] | -0.03 [-0.67, 0.55] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm+settle+h41+dist_roll`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.17 [0.13, 0.21] | -0.65 [-1.23, -0.22] |
| 2018-19 | 320 | 74 | 0.09 [0.05, 0.14] | -0.05 [-0.75, 0.57] |
| 2020-24 | 1069 | 7 | 0.21† | -2.37† |
| 2025-26 | 214 | 20 | 0.22 [0.15, 0.37] | +0.45 [-0.73, 1.55] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.17 [0.13, 0.21] | -0.65 [-1.23, -0.22] |
| scarcity state 0 | 891 | 2 | 0.27† | -2.69† |
| scarcity state 1 | 268 | 1 | undefined | undefined |
| scarcity state 2 | 35 | 9 | 0.14† | +0.73† |
| scarcity state 3 | 409 | 89 | 0.11 [0.07, 0.15] | +0.06 [-0.57, 0.64] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm+every_day+gate+settle+h41+iorb+tailcap75`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.13 [0.09, 0.17] | -1.26 [-1.87, -0.78] |
| 2018-19 | 320 | 74 | 0.05 [0.00, 0.10] | -0.70 [-1.35, -0.06] |
| 2020-24 | 1069 | 7 | 0.13† | -3.47† |
| 2025-26 | 214 | 20 | 0.25 [0.17, 0.43] | +0.84 [-0.36, 2.20] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.13 [0.09, 0.17] | -1.26 [-1.87, -0.78] |
| scarcity state 0 | 891 | 2 | 0.14† | -4.43† |
| scarcity state 1 | 268 | 1 | undefined | undefined |
| scarcity state 2 | 35 | 9 | 0.19† | +1.36† |
| scarcity state 3 | 409 | 89 | 0.07 [0.02, 0.11] | -0.56 [-1.17, 0.06] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `spread_q_gbm+settle+h41+dist_roll`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.12 [0.08, 0.16] | -1.29 [-1.93, -0.84] |
| 2018-19 | 320 | 74 | 0.10 [0.05, 0.14] | -0.02 [-0.74, 0.63] |
| 2020-24 | 1069 | 7 | 0.14† | -3.35† |
| 2025-26 | 214 | 20 | 0.19 [0.13, 0.33] | +0.04 [-1.16, 1.03] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.12 [0.08, 0.16] | -1.29 [-1.93, -0.84] |
| scarcity state 0 | 891 | 2 | 0.22† | -3.64† |
| scarcity state 1 | 268 | 1 | undefined | undefined |
| scarcity state 2 | 35 | 9 | 0.16† | +0.88† |
| scarcity state 3 | 409 | 89 | 0.11 [0.07, 0.16] | +0.04 [-0.64, 0.66] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `spread_q_gbm+two_part+settle+h41+dist_roll`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.60 [0.42, 0.86] | -0.50 [-1.05, 0.01] |
| 2018-19 | 320 | 74 | 0.60 [0.38, 0.88] | -0.17 [-0.75, 0.36] |
| 2020-24 | 1069 | 7 | 0.24† | -3.00† |
| 2025-26 | 214 | 20 | 0.66 [0.47, 1.07] | -0.29 [-1.20, 0.44] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.60 [0.42, 0.86] | -0.50 [-1.05, 0.01] |
| scarcity state 0 | 891 | 2 | 0.13† | -4.73† |
| scarcity state 1 | 268 | 1 | undefined | undefined |
| scarcity state 2 | 35 | 9 | 0.84 [0.52, 1.55] | +0.88 [-0.63, 2.44] |
| scarcity state 3 | 409 | 89 | 0.57 [0.38, 0.81] | -0.31 [-0.77, 0.13] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.03† | -2.31† |
| 2018-19 | 320 | 74 | undefined | undefined |
| 2020-24 | 1069 | 7 | undefined | undefined |
| 2025-26 | 214 | 20 | 0.27† | +1.29† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.03† | -2.31† |
| scarcity state 0 | 891 | 2 | undefined | undefined |
| scarcity state 1 | 268 | 1 | undefined | undefined |
| scarcity state 2 | 35 | 9 | undefined | undefined |
| scarcity state 3 | 409 | 89 | -0.08† | -2.31† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `ngboost_laplace`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.45 [0.35, 0.62] | -0.53 [-1.05, -0.04] |
| 2018-19 | 320 | 74 | 0.40 [0.18, 0.74] | -0.55 [-1.17, -0.01] |
| 2020-24 | 1069 | 7 | 0.26† | -2.76† |
| 2025-26 | 214 | 20 | 0.52 [0.36, 1.13] | +0.68 [-0.41, 3.47] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.45 [0.35, 0.62] | -0.53 [-1.05, -0.04] |
| scarcity state 0 | 891 | 2 | -0.17† | -8.19† |
| scarcity state 1 | 268 | 1 | undefined | undefined |
| scarcity state 2 | 35 | 9 | 1.03† | +4.16† |
| scarcity state 3 | 409 | 89 | 0.35 [0.14, 0.61] | -0.63 [-1.19, -0.11] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `calendar_climatology`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.49 [-0.40, 1.36] | -1.61 [-3.84, 0.19] |
| 2018-19 | 320 | 74 | 0.65 [0.20, 1.18] | +0.26 [-0.90, 1.53] |
| 2020-24 | 1069 | 7 | 1.03† | -2.86† |
| 2025-26 | 214 | 20 | 2.44† | +4.56† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.49 [-0.40, 1.36] | -1.61 [-3.84, 0.19] |
| scarcity state 0 | 891 | 2 | -12.07† | -38.47† |
| scarcity state 1 | 268 | 1 | -4.63† | -16.85† |
| scarcity state 2 | 35 | 9 | -1.87† | -6.16† |
| scarcity state 3 | 409 | 89 | 0.32 [-0.13, 0.77] | -0.57 [-1.76, 0.51] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `persistence_logistic`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.99 [0.71, 1.38] | -0.35 [-1.15, 0.49] |
| 2018-19 | 320 | 74 | 0.48 [0.18, 1.00] | -0.28 [-1.09, 0.75] |
| 2020-24 | 1069 | 7 | 0.82 [-2.43, 1.84] | -2.74 [-14.36, -0.79] |
| 2025-26 | 214 | 20 | 0.82 [0.55, 1.52] | -0.32 [-1.35, 1.02] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1603 | 101 | 0.99 [0.71, 1.38] | -0.35 [-1.15, 0.49] |
| scarcity state 0 | 891 | 2 | -1.15† | -10.27† |
| scarcity state 1 | 268 | 1 | -7.00† | -30.08† |
| scarcity state 2 | 35 | 9 | 0.96 [-0.04, 2.62] | +0.72 [-1.90, 3.09] |
| scarcity state 3 | 409 | 89 | 0.35 [0.13, 0.68] | -0.67 [-1.30, 0.01] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

## h = 3: 1602 days, 100 above +5 bp

### `risk_gbm+settle+h41`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1602 | 100 | 0.15 [0.12, 0.20] | -0.80 [-1.35, -0.34] |
| 2018-19 | 319 | 73 | 0.08 [0.04, 0.13] | -0.19 [-0.89, 0.48] |
| 2020-24 | 1069 | 7 | 0.20† | -2.50† |
| 2025-26 | 214 | 20 | 0.23 [0.14, 0.37] | +0.52 [-0.98, 1.73] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1602 | 100 | 0.15 [0.12, 0.20] | -0.80 [-1.35, -0.34] |
| scarcity state 0 | 892 | 2 | undefined | undefined |
| scarcity state 1 | 267 | 1 | 0.22† | -3.00† |
| scarcity state 2 | 35 | 9 | 0.15† | +0.82† |
| scarcity state 3 | 408 | 88 | 0.10 [0.06, 0.14] | -0.12 [-0.73, 0.45] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm+settle+h41+dist_roll`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1602 | 100 | 0.16 [0.12, 0.20] | -0.73 [-1.26, -0.29] |
| 2018-19 | 319 | 73 | 0.09 [0.05, 0.13] | -0.13 [-0.84, 0.50] |
| 2020-24 | 1069 | 7 | 0.20† | -2.55† |
| 2025-26 | 214 | 20 | 0.21 [0.13, 0.35] | +0.27 [-1.06, 1.34] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1602 | 100 | 0.16 [0.12, 0.20] | -0.73 [-1.26, -0.29] |
| scarcity state 0 | 892 | 2 | undefined | undefined |
| scarcity state 1 | 267 | 1 | 0.16† | -3.68† |
| scarcity state 2 | 35 | 9 | 0.12† | +0.48† |
| scarcity state 3 | 408 | 88 | 0.10 [0.07, 0.14] | -0.05 [-0.65, 0.50] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm+every_day+gate+settle+h41+iorb+tailcap75`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1602 | 100 | 0.11 [0.06, 0.15] | -1.48 [-2.06, -1.00] |
| 2018-19 | 319 | 73 | 0.03 [-0.01, 0.08] | -0.87 [-1.55, -0.30] |
| 2020-24 | 1069 | 7 | 0.11† | -3.76† |
| 2025-26 | 214 | 20 | 0.23 [0.14, 0.37] | +0.52 [-0.98, 1.73] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1602 | 100 | 0.11 [0.06, 0.15] | -1.48 [-2.06, -1.00] |
| scarcity state 0 | 892 | 2 | undefined | undefined |
| scarcity state 1 | 267 | 1 | 0.21† | -3.19† |
| scarcity state 2 | 35 | 9 | 0.15† | +0.82† |
| scarcity state 3 | 408 | 88 | 0.05 [0.01, 0.10] | -0.72 [-1.29, -0.17] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `spread_q_gbm+settle+h41+dist_roll`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1602 | 100 | 0.11 [0.07, 0.15] | -1.36 [-1.93, -0.89] |
| 2018-19 | 319 | 73 | 0.09 [0.05, 0.13] | -0.12 [-0.84, 0.56] |
| 2020-24 | 1069 | 7 | 0.14† | -3.38† |
| 2025-26 | 214 | 20 | 0.19 [0.11, 0.30] | -0.01 [-1.40, 0.96] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1602 | 100 | 0.11 [0.07, 0.15] | -1.36 [-1.93, -0.89] |
| scarcity state 0 | 892 | 2 | undefined | undefined |
| scarcity state 1 | 267 | 1 | 0.43† | -2.13† |
| scarcity state 2 | 35 | 9 | 0.19† | +1.28† |
| scarcity state 3 | 408 | 88 | 0.10 [0.06, 0.15] | -0.03 [-0.65, 0.56] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `spread_q_gbm+two_part+settle+h41+dist_roll`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1602 | 100 | 0.60 [0.40, 0.88] | -0.53 [-1.11, -0.02] |
| 2018-19 | 319 | 73 | 0.59 [0.35, 0.92] | -0.17 [-0.74, 0.38] |
| 2020-24 | 1069 | 7 | 0.19† | -3.42† |
| 2025-26 | 214 | 20 | 0.65 [0.40, 1.38] | -0.28 [-1.22, 0.58] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1602 | 100 | 0.60 [0.40, 0.88] | -0.53 [-1.11, -0.02] |
| scarcity state 0 | 892 | 2 | undefined | undefined |
| scarcity state 1 | 267 | 1 | 0.35† | -3.66† |
| scarcity state 2 | 35 | 9 | 0.67 [0.02, 1.73] | +0.58 [-2.09, 2.60] |
| scarcity state 3 | 408 | 88 | 0.54 [0.33, 0.82] | -0.33 [-0.85, 0.11] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1602 | 100 | 0.04† | -2.19† |
| 2018-19 | 319 | 73 | undefined | undefined |
| 2020-24 | 1069 | 7 | undefined | undefined |
| 2025-26 | 214 | 20 | 0.28† | +1.43† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1602 | 100 | 0.04† | -2.19† |
| scarcity state 0 | 892 | 2 | undefined | undefined |
| scarcity state 1 | 267 | 1 | undefined | undefined |
| scarcity state 2 | 35 | 9 | undefined | undefined |
| scarcity state 3 | 408 | 88 | -0.05† | -1.98† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `ngboost_laplace`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1602 | 100 | 0.41 [0.32, 0.55] | -0.61 [-1.10, -0.15] |
| 2018-19 | 319 | 73 | 0.32 [0.08, 0.67] | -0.64 [-1.23, -0.10] |
| 2020-24 | 1069 | 7 | 0.26† | -2.72† |
| 2025-26 | 214 | 20 | 0.50 [0.34, 1.14] | +0.85 [-0.27, 4.42] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1602 | 100 | 0.41 [0.32, 0.55] | -0.61 [-1.10, -0.15] |
| scarcity state 0 | 892 | 2 | -0.04† | -6.56† |
| scarcity state 1 | 267 | 1 | undefined | undefined |
| scarcity state 2 | 35 | 9 | 0.04 [-0.65, 0.49] | -0.86 [-4.13, 1.06] |
| scarcity state 3 | 408 | 88 | 0.26 [0.05, 0.54] | -0.78 [-1.38, -0.26] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `calendar_climatology`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1602 | 100 | 0.49 [-0.41, 1.33] | -1.60 [-3.85, 0.13] |
| 2018-19 | 319 | 73 | 0.67 [0.21, 1.18] | +0.29 [-0.85, 1.50] |
| 2020-24 | 1069 | 7 | 1.02† | -2.88† |
| 2025-26 | 214 | 20 | 1.77† | +2.69† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1602 | 100 | 0.49 [-0.41, 1.33] | -1.60 [-3.85, 0.13] |
| scarcity state 0 | 892 | 2 | -12.10† | -38.53† |
| scarcity state 1 | 267 | 1 | -4.62† | -16.82† |
| scarcity state 2 | 35 | 9 | -2.09† | -6.75† |
| scarcity state 3 | 408 | 88 | 0.34 [-0.11, 0.79] | -0.55 [-1.72, 0.50] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `persistence_logistic`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1602 | 100 | 0.92 [0.54, 1.43] | -0.66 [-1.66, 0.36] |
| 2018-19 | 319 | 73 | 0.35 [0.10, 0.91] | -0.54 [-1.26, 0.63] |
| 2020-24 | 1069 | 7 | 0.86 [-7.28, 4.32] | -2.95 [-28.62, 2.28] |
| 2025-26 | 214 | 20 | 1.07 [0.62, 2.30] | +0.26 [-1.05, 2.72] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1602 | 100 | 0.92 [0.54, 1.43] | -0.66 [-1.66, 0.36] |
| scarcity state 0 | 892 | 2 | -3.04† | -15.61† |
| scarcity state 1 | 267 | 1 | -10.46† | -38.35† |
| scarcity state 2 | 35 | 9 | 0.79† | +0.46† |
| scarcity state 3 | 408 | 88 | 0.21 [0.02, 0.61] | -0.91 [-1.50, -0.10] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

## h = 4: 1601 days, 100 above +5 bp

### `risk_gbm+settle+h41`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1601 | 100 | 0.16 [0.12, 0.20] | -0.77 [-1.34, -0.34] |
| 2018-19 | 318 | 73 | 0.08 [0.04, 0.12] | -0.22 [-0.92, 0.39] |
| 2020-24 | 1069 | 7 | 0.24† | -2.04† |
| 2025-26 | 214 | 20 | 0.26 [0.17, 0.43] | +0.96 [-0.51, 2.25] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1601 | 100 | 0.16 [0.12, 0.20] | -0.77 [-1.34, -0.34] |
| scarcity state 0 | 891 | 3 | 0.34† | -1.45† |
| scarcity state 1 | 268 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 9 | 0.24† | +2.07† |
| scarcity state 3 | 408 | 88 | 0.10 [0.06, 0.14] | -0.12 [-0.72, 0.43] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm+settle+h41+dist_roll`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1601 | 100 | 0.16 [0.12, 0.21] | -0.70 [-1.28, -0.28] |
| 2018-19 | 318 | 73 | 0.09 [0.05, 0.13] | -0.15 [-0.85, 0.45] |
| 2020-24 | 1069 | 7 | 0.23† | -2.22† |
| 2025-26 | 214 | 20 | 0.25 [0.17, 0.39] | +0.75 [-0.48, 1.77] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1601 | 100 | 0.16 [0.12, 0.21] | -0.70 [-1.28, -0.28] |
| scarcity state 0 | 891 | 3 | 0.28† | -2.20† |
| scarcity state 1 | 268 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 9 | 0.20† | +1.58† |
| scarcity state 3 | 408 | 88 | 0.10 [0.07, 0.14] | -0.02 [-0.62, 0.52] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm+every_day+gate+settle+h41+iorb+tailcap75`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1601 | 100 | 0.12 [0.08, 0.17] | -1.28 [-1.90, -0.82] |
| 2018-19 | 318 | 73 | 0.05 [0.01, 0.10] | -0.63 [-1.26, -0.05] |
| 2020-24 | 1069 | 7 | 0.14† | -3.42† |
| 2025-26 | 214 | 20 | 0.26 [0.17, 0.43] | +0.96 [-0.51, 2.25] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1601 | 100 | 0.12 [0.08, 0.17] | -1.28 [-1.90, -0.82] |
| scarcity state 0 | 891 | 3 | 0.13† | -4.14† |
| scarcity state 1 | 268 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 9 | 0.24† | +2.07† |
| scarcity state 3 | 408 | 88 | 0.07 [0.03, 0.12] | -0.50 [-1.03, 0.03] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `spread_q_gbm+settle+h41+dist_roll`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1601 | 100 | 0.11 [0.07, 0.15] | -1.41 [-2.06, -0.96] |
| 2018-19 | 318 | 73 | 0.08 [0.04, 0.12] | -0.22 [-0.95, 0.42] |
| 2020-24 | 1069 | 7 | 0.13† | -3.44† |
| 2025-26 | 214 | 20 | 0.19 [0.11, 0.30] | -0.08 [-1.37, 0.77] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1601 | 100 | 0.11 [0.07, 0.15] | -1.41 [-2.06, -0.96] |
| scarcity state 0 | 891 | 3 | 0.15† | -3.86† |
| scarcity state 1 | 268 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 9 | 0.16† | +1.02† |
| scarcity state 3 | 408 | 88 | 0.10 [0.06, 0.14] | -0.10 [-0.74, 0.48] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `spread_q_gbm+two_part+settle+h41+dist_roll`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1601 | 100 | 0.29 [0.18, 0.61] | -1.19 [-1.78, -0.54] |
| 2018-19 | 318 | 73 | 0.07 [-0.01, 0.32] | -0.98 [-1.58, -0.42] |
| 2020-24 | 1069 | 7 | 0.18† | -3.49† |
| 2025-26 | 214 | 20 | 0.90 [0.68, 1.42] | -0.05 [-0.97, 0.89] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1601 | 100 | 0.29 [0.18, 0.61] | -1.19 [-1.78, -0.54] |
| scarcity state 0 | 891 | 3 | 0.05† | -5.09† |
| scarcity state 1 | 268 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 9 | 1.07 [0.48, 1.79] | +1.47 [-0.91, 3.65] |
| scarcity state 3 | 408 | 88 | 0.07 [-0.00, 0.37] | -1.07 [-1.56, -0.51] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1601 | 100 | 0.04† | -2.21† |
| 2018-19 | 318 | 73 | undefined | undefined |
| 2020-24 | 1069 | 7 | undefined | undefined |
| 2025-26 | 214 | 20 | 0.28† | +1.51† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1601 | 100 | 0.04† | -2.21† |
| scarcity state 0 | 891 | 3 | undefined | undefined |
| scarcity state 1 | 268 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 9 | undefined | undefined |
| scarcity state 3 | 408 | 88 | -0.06† | -2.13† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `ngboost_laplace`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1601 | 100 | 0.36 [0.28, 0.49] | -0.76 [-1.28, -0.31] |
| 2018-19 | 318 | 73 | 0.17 [-0.03, 0.44] | -0.83 [-1.48, -0.30] |
| 2020-24 | 1069 | 7 | 0.27 [-0.13, 1.28] | -2.78 [-7.00, -0.01] |
| 2025-26 | 214 | 20 | 0.45 [0.30, 1.32] | +0.59 [-0.48, 5.61] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1601 | 100 | 0.36 [0.28, 0.49] | -0.76 [-1.28, -0.31] |
| scarcity state 0 | 891 | 3 | 0.03† | -5.35† |
| scarcity state 1 | 268 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 9 | -0.27 [-0.91, 0.36] | -2.53 [-5.42, 0.37] |
| scarcity state 3 | 408 | 88 | 0.12 [-0.07, 0.35] | -1.02 [-1.68, -0.48] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `calendar_climatology`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1601 | 100 | 0.45 [-0.48, 1.32] | -1.69 [-3.99, 0.03] |
| 2018-19 | 318 | 73 | 0.65 [0.22, 1.17] | +0.25 [-0.86, 1.46] |
| 2020-24 | 1069 | 7 | 1.01† | -2.90† |
| 2025-26 | 214 | 20 | 1.38† | +1.61† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1601 | 100 | 0.45 [-0.48, 1.32] | -1.69 [-3.99, 0.03] |
| scarcity state 0 | 891 | 3 | -13.00† | -40.63† |
| scarcity state 1 | 268 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 9 | -2.22† | -7.06† |
| scarcity state 3 | 408 | 88 | 0.31 [-0.14, 0.78] | -0.60 [-1.78, 0.57] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `persistence_logistic`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1601 | 100 | 1.08 [0.79, 1.46] | -0.22 [-1.01, 0.56] |
| 2018-19 | 318 | 73 | 0.58 [0.29, 1.05] | -0.07 [-0.83, 0.79] |
| 2020-24 | 1069 | 7 | 0.78 [-2.69, 1.85] | -2.92 [-14.76, -0.71] |
| 2025-26 | 214 | 20 | 0.82 [0.50, 1.66] | -0.34 [-1.57, 1.41] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1601 | 100 | 1.08 [0.79, 1.46] | -0.22 [-1.01, 0.56] |
| scarcity state 0 | 891 | 3 | -1.67† | -11.49† |
| scarcity state 1 | 268 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 9 | 1.10 [-3.02, 2.36] | +1.09 [-10.32, 3.51] |
| scarcity state 3 | 408 | 88 | 0.36 [0.13, 0.70] | -0.63 [-1.27, 0.06] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

## h = 5: 1600 days, 100 above +5 bp

### `risk_gbm+settle+h41`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1600 | 100 | 0.15 [0.11, 0.19] | -0.84 [-1.40, -0.39] |
| 2018-19 | 317 | 73 | 0.08 [0.04, 0.12] | -0.21 [-0.88, 0.37] |
| 2020-24 | 1069 | 7 | 0.16† | -3.01† |
| 2025-26 | 214 | 20 | 0.23 [0.15, 0.38] | +0.58 [-0.71, 1.68] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1600 | 100 | 0.15 [0.11, 0.19] | -0.84 [-1.40, -0.39] |
| scarcity state 0 | 890 | 3 | 0.13† | -4.03† |
| scarcity state 1 | 268 | 0 | undefined | undefined |
| scarcity state 2 | 35 | 10 | 0.16† | +1.17† |
| scarcity state 3 | 407 | 87 | 0.09 [0.06, 0.14] | -0.16 [-0.74, 0.38] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm+settle+h41+dist_roll`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1600 | 100 | 0.15 [0.12, 0.20] | -0.80 [-1.34, -0.37] |
| 2018-19 | 317 | 73 | 0.08 [0.04, 0.13] | -0.17 [-0.84, 0.43] |
| 2020-24 | 1069 | 7 | 0.19† | -2.65† |
| 2025-26 | 214 | 20 | 0.21 [0.14, 0.36] | +0.31 [-1.00, 1.41] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1600 | 100 | 0.15 [0.12, 0.20] | -0.80 [-1.34, -0.37] |
| scarcity state 0 | 890 | 3 | 0.17† | -3.46† |
| scarcity state 1 | 268 | 0 | undefined | undefined |
| scarcity state 2 | 35 | 10 | 0.15† | +0.97† |
| scarcity state 3 | 407 | 87 | 0.10 [0.06, 0.14] | -0.08 [-0.65, 0.45] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm+every_day+gate+settle+h41+iorb+tailcap75`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1600 | 100 | 0.12 [0.09, 0.17] | -1.27 [-1.82, -0.83] |
| 2018-19 | 317 | 73 | 0.06 [0.02, 0.10] | -0.60 [-1.18, -0.09] |
| 2020-24 | 1069 | 7 | 0.07† | -4.19† |
| 2025-26 | 214 | 20 | 0.20 [0.12, 0.34] | +0.20 [-1.23, 1.26] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1600 | 100 | 0.12 [0.09, 0.17] | -1.27 [-1.82, -0.83] |
| scarcity state 0 | 890 | 3 | -0.01† | -5.80† |
| scarcity state 1 | 268 | 0 | undefined | undefined |
| scarcity state 2 | 35 | 10 | 0.16† | +1.17† |
| scarcity state 3 | 407 | 87 | 0.07 [0.03, 0.12] | -0.51 [-1.02, -0.02] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `spread_q_gbm+settle+h41+dist_roll`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1600 | 100 | 0.10 [0.07, 0.14] | -1.44 [-2.02, -0.99] |
| 2018-19 | 317 | 73 | 0.08 [0.04, 0.13] | -0.20 [-0.90, 0.43] |
| 2020-24 | 1069 | 7 | 0.12† | -3.55† |
| 2025-26 | 214 | 20 | 0.19 [0.12, 0.33] | +0.06 [-1.26, 1.09] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1600 | 100 | 0.10 [0.07, 0.14] | -1.44 [-2.02, -0.99] |
| scarcity state 0 | 890 | 3 | 0.15† | -3.87† |
| scarcity state 1 | 268 | 0 | undefined | undefined |
| scarcity state 2 | 35 | 10 | 0.13† | +0.76† |
| scarcity state 3 | 407 | 87 | 0.10 [0.06, 0.14] | -0.11 [-0.72, 0.48] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `spread_q_gbm+two_part+settle+h41+dist_roll`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1600 | 100 | 0.42 [0.28, 0.71] | -0.93 [-1.49, -0.39] |
| 2018-19 | 317 | 73 | 0.21 [0.06, 0.59] | -0.72 [-1.37, -0.12] |
| 2020-24 | 1069 | 7 | 0.29† | -3.04† |
| 2025-26 | 214 | 20 | 0.30 [0.12, 1.20] | -1.07 [-2.22, -0.27] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1600 | 100 | 0.42 [0.28, 0.71] | -0.93 [-1.49, -0.39] |
| scarcity state 0 | 890 | 3 | 0.18† | -4.02† |
| scarcity state 1 | 268 | 0 | undefined | undefined |
| scarcity state 2 | 35 | 10 | -0.03 [-0.20, 0.92] | -1.02 [-3.14, 0.49] |
| scarcity state 3 | 407 | 87 | 0.24 [0.08, 0.59] | -0.79 [-1.35, -0.26] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1600 | 100 | -0.02† | -2.97† |
| 2018-19 | 317 | 73 | undefined | undefined |
| 2020-24 | 1069 | 7 | undefined | undefined |
| 2025-26 | 214 | 20 | 0.26† | +1.24† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1600 | 100 | -0.02† | -2.97† |
| scarcity state 0 | 890 | 3 | undefined | undefined |
| scarcity state 1 | 268 | 0 | undefined | undefined |
| scarcity state 2 | 35 | 10 | undefined | undefined |
| scarcity state 3 | 407 | 87 | -0.11† | -2.79† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `ngboost_laplace`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1600 | 100 | 0.34 [0.26, 0.48] | -0.87 [-1.39, -0.40] |
| 2018-19 | 317 | 73 | 0.14 [-0.03, 0.42] | -0.88 [-1.54, -0.35] |
| 2020-24 | 1069 | 7 | 0.34 [0.06, 1.63] | -2.53 [-5.15, 0.15] |
| 2025-26 | 214 | 20 | 0.35 [0.21, 0.90] | +0.13 [-0.79, 2.82] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1600 | 100 | 0.34 [0.26, 0.48] | -0.87 [-1.39, -0.40] |
| scarcity state 0 | 890 | 3 | 0.36† | -1.92† |
| scarcity state 1 | 268 | 0 | undefined | undefined |
| scarcity state 2 | 35 | 10 | -0.52 [-1.03, -0.00] | -4.22 [-7.21, -1.86] |
| scarcity state 3 | 407 | 87 | 0.10 [-0.07, 0.31] | -1.08 [-1.71, -0.55] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `calendar_climatology`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1600 | 100 | 0.42 [-0.55, 1.28] | -1.75 [-4.20, 0.03] |
| 2018-19 | 317 | 73 | 0.63 [0.17, 1.19] | +0.22 [-1.00, 1.46] |
| 2020-24 | 1069 | 7 | 1.04† | -2.84† |
| 2025-26 | 214 | 20 | 0.61† | -0.56† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1600 | 100 | 0.42 [-0.55, 1.28] | -1.75 [-4.20, 0.03] |
| scarcity state 0 | 890 | 3 | -11.99† | -37.85† |
| scarcity state 1 | 268 | 0 | undefined | undefined |
| scarcity state 2 | 35 | 10 | -2.22† | -6.95† |
| scarcity state 3 | 407 | 87 | 0.30 [-0.15, 0.74] | -0.63 [-1.80, 0.46] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `persistence_logistic`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1600 | 100 | 0.89 [0.53, 1.33] | -0.59 [-1.58, 0.28] |
| 2018-19 | 317 | 73 | 0.32 [0.16, 0.63] | -0.43 [-1.09, 0.22] |
| 2020-24 | 1069 | 7 | 1.05 [-1.00, 2.31] | -2.34 [-8.76, 0.13] |
| 2025-26 | 214 | 20 | 0.89 [0.54, 1.73] | -0.20 [-1.46, 1.54] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1600 | 100 | 0.89 [0.53, 1.33] | -0.59 [-1.58, 0.28] |
| scarcity state 0 | 890 | 3 | 0.33† | -4.60† |
| scarcity state 1 | 268 | 0 | undefined | undefined |
| scarcity state 2 | 35 | 10 | 1.13 [-1.05, 2.34] | +1.26 [-4.73, 3.31] |
| scarcity state 3 | 407 | 87 | 0.25 [0.12, 0.46] | -0.76 [-1.33, -0.21] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.
