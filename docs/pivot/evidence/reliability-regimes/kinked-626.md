# Reliability slope within regimes, #626's rows on the days that are not risk dates (#683)

Pooled slopes mislead here (#670): a regime with no pressure day (2021-23) forecasts near 0 and adds a long, well-ordered stretch at the bottom of the curve, which raises the pooled slope. Read calibration within a regime. A cell with no pressure day has no slope. Figures here are development, not a verdict.

Intercept and slope of `logit P(y = 1) = intercept + slope * logit(p)` (1 and 0 for a reliable forecast), 90% stationary-bootstrap intervals (block length 10, 2000 replications); `undefined` where the cell has no pressure day or the forecast is constant there; no interval where the cell has too few events to give one. Regimes: 2018-19, 2020-24 (which holds 2021-23, with no pressure day) and 2025-26.

## h = 1: 1568 days, 87 above +5 bp

### `structural_liquidity`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.64 [0.45, 0.92] | -1.26 [-1.97, -0.48] |
| 2018-19 | 314 | 63 | 0.29 [0.18, 0.48] | -1.00 [-1.61, -0.39] |
| 2020-24 | 1043 | 5 | 0.67 [-1.53, 1.09] | -3.12 [-12.03, -1.91] |
| 2025-26 | 211 | 19 | 1.18 [0.85, 1.98] | +0.76 [-0.40, 2.43] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.64 [0.45, 0.92] | -1.26 [-1.97, -0.48] |
| scarcity state 0 | 873 | 2 | -0.28† | -7.23† |
| scarcity state 1 | 260 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 7 | 1.14† | +1.23† |
| scarcity state 3 | 401 | 78 | 0.30 [0.19, 0.49] | -1.02 [-1.49, -0.49] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `structural_liquidity+h41`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.59 [0.40, 0.89] | -1.37 [-2.10, -0.55] |
| 2018-19 | 314 | 63 | 0.26 [0.16, 0.47] | -1.06 [-1.66, -0.42] |
| 2020-24 | 1043 | 5 | 0.69 [-1.62, 1.12] | -3.06 [-12.39, -1.82] |
| 2025-26 | 211 | 19 | 1.21 [0.87, 2.03] | +0.89 [-0.30, 2.62] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.59 [0.40, 0.89] | -1.37 [-2.10, -0.55] |
| scarcity state 0 | 873 | 2 | -0.35† | -7.51† |
| scarcity state 1 | 260 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 7 | 1.17† | +1.36† |
| scarcity state 3 | 401 | 78 | 0.27 [0.17, 0.49] | -1.07 [-1.54, -0.53] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `structural_kinked_fitted`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.57 [0.39, 0.83] | -1.42 [-2.15, -0.68] |
| 2018-19 | 314 | 63 | 0.27 [0.17, 0.50] | -1.03 [-1.64, -0.38] |
| 2020-24 | 1043 | 5 | 0.44 [-1.62, 0.75] | -3.86 [-12.43, -2.70] |
| 2025-26 | 211 | 19 | 1.21 [0.87, 2.03] | +0.88 [-0.31, 2.62] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.57 [0.39, 0.83] | -1.42 [-2.15, -0.68] |
| scarcity state 0 | 873 | 2 | -0.34† | -7.47† |
| scarcity state 1 | 260 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 7 | 1.18† | +1.39† |
| scarcity state 3 | 401 | 78 | 0.28 [0.18, 0.52] | -1.04 [-1.52, -0.49] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `structural_kinked_rolling`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.74 [0.52, 1.04] | -0.86 [-1.71, 0.00] |
| 2018-19 | 314 | 63 | 0.47 [0.26, 0.93] | -0.42 [-1.19, 0.67] |
| 2020-24 | 1043 | 5 | 0.34 [-1.19, 0.66] | -4.15 [-10.90, -2.92] |
| 2025-26 | 211 | 19 | 1.16 [0.89, 1.75] | +0.38 [-0.53, 1.44] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.74 [0.52, 1.04] | -0.86 [-1.71, 0.00] |
| scarcity state 0 | 873 | 2 | -0.21† | -6.98† |
| scarcity state 1 | 260 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 7 | 0.98† | +0.54† |
| scarcity state 3 | 401 | 78 | 0.48 [0.29, 0.82] | -0.52 [-1.13, 0.27] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm+settle+h41`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.03 [-0.11, 0.12] | -2.43 [-4.43, -1.25] |
| 2018-19 | 314 | 63 | -0.13† | -3.06† |
| 2020-24 | 1043 | 5 | undefined | undefined |
| 2025-26 | 211 | 19 | 0.26† | +1.11† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.03 [-0.11, 0.12] | -2.43 [-4.43, -1.25] |
| scarcity state 0 | 873 | 2 | undefined | undefined |
| scarcity state 1 | 260 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 7 | undefined | undefined |
| scarcity state 3 | 401 | 78 | -0.02 [-0.13, 0.07] | -1.65 [-3.09, -0.55] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm+settle+h41+dist_roll`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.03 [-0.11, 0.13] | -2.41 [-4.38, -1.22] |
| 2018-19 | 314 | 63 | -0.13† | -3.06† |
| 2020-24 | 1043 | 5 | undefined | undefined |
| 2025-26 | 211 | 19 | 0.25† | +0.88† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.03 [-0.11, 0.13] | -2.41 [-4.38, -1.22] |
| scarcity state 0 | 873 | 2 | undefined | undefined |
| scarcity state 1 | 260 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 7 | undefined | undefined |
| scarcity state 3 | 401 | 78 | -0.02 [-0.13, 0.07] | -1.65 [-3.16, -0.51] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `persistence_logistic`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 1.05 [0.73, 1.43] | -0.37 [-1.25, 0.49] |
| 2018-19 | 314 | 63 | 0.60 [0.31, 1.22] | -0.35 [-1.16, 0.79] |
| 2020-24 | 1043 | 5 | 0.63 [-1.21, 1.10] | -3.39 [-10.38, -2.14] |
| 2025-26 | 211 | 19 | 1.03 [0.75, 1.70] | -0.00 [-1.03, 1.16] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 1.05 [0.73, 1.43] | -0.37 [-1.25, 0.49] |
| scarcity state 0 | 873 | 2 | -0.06† | -6.32† |
| scarcity state 1 | 260 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 7 | 0.95† | +0.40† |
| scarcity state 3 | 401 | 78 | 0.54 [0.32, 0.98] | -0.57 [-1.16, 0.26] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `calendar_climatology`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.53 [-0.33, 1.33] | -1.65 [-3.77, -0.03] |
| 2018-19 | 314 | 63 | 0.65 [0.20, 1.16] | +0.04 [-1.16, 1.24] |
| 2020-24 | 1043 | 5 | 1.14† | -2.96† |
| 2025-26 | 211 | 19 | 4.23† | +9.43† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.53 [-0.33, 1.33] | -1.65 [-3.77, -0.03] |
| scarcity state 0 | 873 | 2 | -12.04† | -38.32† |
| scarcity state 1 | 260 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 7 | -3.18† | -10.19† |
| scarcity state 3 | 401 | 78 | 0.32 [-0.14, 0.78] | -0.74 [-1.89, 0.43] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

## h = 2: 1568 days, 87 above +5 bp

### `structural_liquidity`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.54 [0.37, 0.82] | -1.53 [-2.21, -0.75] |
| 2018-19 | 314 | 63 | 0.24 [0.13, 0.43] | -1.05 [-1.65, -0.45] |
| 2020-24 | 1043 | 5 | 0.87 [-3.62, 1.62] | -2.71 [-19.93, -1.11] |
| 2025-26 | 211 | 19 | 0.99 [0.62, 2.00] | +0.43 [-0.92, 2.93] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.54 [0.37, 0.82] | -1.53 [-2.21, -0.75] |
| scarcity state 0 | 873 | 1 | -0.70† | -9.39† |
| scarcity state 1 | 260 | 1 | -8.56† | -37.51† |
| scarcity state 2 | 34 | 8 | 1.52 [0.58, 3.75] | +2.31 [-0.18, 6.13] |
| scarcity state 3 | 401 | 77 | 0.22 [0.12, 0.39] | -1.12 [-1.64, -0.62] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `structural_liquidity+h41`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.50 [0.34, 0.79] | -1.63 [-2.32, -0.85] |
| 2018-19 | 314 | 63 | 0.22 [0.12, 0.41] | -1.10 [-1.72, -0.48] |
| 2020-24 | 1043 | 5 | 0.89 [-3.92, 1.66] | -2.66 [-21.07, -0.97] |
| 2025-26 | 211 | 19 | 1.02 [0.64, 2.08] | +0.57 [-0.82, 3.22] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.50 [0.34, 0.79] | -1.63 [-2.32, -0.85] |
| scarcity state 0 | 873 | 1 | -0.82† | -9.86† |
| scarcity state 1 | 260 | 1 | -8.92† | -38.97† |
| scarcity state 2 | 34 | 8 | 1.56 [0.59, 4.03] | +2.49 [-0.08, 6.88] |
| scarcity state 3 | 401 | 77 | 0.20 [0.11, 0.37] | -1.16 [-1.70, -0.63] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `structural_kinked_fitted`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.47 [0.33, 0.72] | -1.70 [-2.38, -1.00] |
| 2018-19 | 314 | 63 | 0.23 [0.13, 0.44] | -1.07 [-1.68, -0.43] |
| 2020-24 | 1043 | 5 | 0.43 [-3.97, 0.92] | -4.03 [-21.26, -2.44] |
| 2025-26 | 211 | 19 | 1.02 [0.64, 2.07] | +0.57 [-0.83, 3.21] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.47 [0.33, 0.72] | -1.70 [-2.38, -1.00] |
| scarcity state 0 | 873 | 1 | -0.82† | -9.84† |
| scarcity state 1 | 260 | 1 | -8.84† | -38.68† |
| scarcity state 2 | 34 | 8 | 1.60 [0.62, 3.99] | +2.60 [-0.03, 7.00] |
| scarcity state 3 | 401 | 77 | 0.21 [0.12, 0.40] | -1.13 [-1.66, -0.58] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `structural_kinked_rolling`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.67 [0.45, 0.97] | -1.06 [-1.93, -0.20] |
| 2018-19 | 314 | 63 | 0.40 [0.19, 0.81] | -0.49 [-1.29, 0.57] |
| 2020-24 | 1043 | 5 | 0.36 [-2.65, 0.84] | -4.18 [-16.62, -2.58] |
| 2025-26 | 211 | 19 | 0.98 [0.66, 2.03] | +0.12 [-0.96, 2.18] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.67 [0.45, 0.97] | -1.06 [-1.93, -0.20] |
| scarcity state 0 | 873 | 1 | -0.33† | -8.08† |
| scarcity state 1 | 260 | 1 | -6.70† | -31.50† |
| scarcity state 2 | 34 | 8 | 1.64† | +1.84† |
| scarcity state 3 | 401 | 77 | 0.35 [0.18, 0.63] | -0.71 [-1.35, 0.01] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm+settle+h41`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.02 [-0.13, 0.11] | -2.60 [-4.72, -1.46] |
| 2018-19 | 314 | 63 | -0.13† | -3.18† |
| 2020-24 | 1043 | 5 | undefined | undefined |
| 2025-26 | 211 | 19 | 0.34† | +2.17† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.02 [-0.13, 0.11] | -2.60 [-4.72, -1.46] |
| scarcity state 0 | 873 | 1 | undefined | undefined |
| scarcity state 1 | 260 | 1 | undefined | undefined |
| scarcity state 2 | 34 | 8 | 0.20† | +1.53† |
| scarcity state 3 | 401 | 77 | -0.05 [-0.17, 0.03] | -2.14 [-3.71, -1.09] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm+settle+h41+dist_roll`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.03 [-0.13, 0.13] | -2.46 [-4.80, -1.28] |
| 2018-19 | 314 | 63 | -0.14† | -3.24† |
| 2020-24 | 1043 | 5 | undefined | undefined |
| 2025-26 | 211 | 19 | 0.33† | +1.94† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.03 [-0.13, 0.13] | -2.46 [-4.80, -1.28] |
| scarcity state 0 | 873 | 1 | undefined | undefined |
| scarcity state 1 | 260 | 1 | undefined | undefined |
| scarcity state 2 | 34 | 8 | 0.20† | +1.46† |
| scarcity state 3 | 401 | 77 | -0.04 [-0.17, 0.04] | -1.99 [-3.74, -0.92] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `persistence_logistic`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.99 [0.70, 1.39] | -0.50 [-1.35, 0.38] |
| 2018-19 | 314 | 63 | 0.50 [0.21, 1.08] | -0.43 [-1.28, 0.70] |
| 2020-24 | 1043 | 5 | 0.87 [-2.50, 1.75] | -2.95 [-15.17, -1.15] |
| 2025-26 | 211 | 19 | 0.82 [0.51, 1.60] | -0.38 [-1.55, 1.19] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.99 [0.70, 1.39] | -0.50 [-1.35, 0.38] |
| scarcity state 0 | 873 | 1 | -0.15† | -7.31† |
| scarcity state 1 | 260 | 1 | -6.86† | -29.48† |
| scarcity state 2 | 34 | 8 | 1.23 [0.46, 2.77] | +1.02 [-0.94, 3.27] |
| scarcity state 3 | 401 | 77 | 0.36 [0.14, 0.71] | -0.80 [-1.44, -0.08] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `calendar_climatology`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.48 [-0.34, 1.30] | -1.76 [-3.87, -0.13] |
| 2018-19 | 314 | 63 | 0.62 [0.16, 1.17] | -0.02 [-1.18, 1.27] |
| 2020-24 | 1043 | 5 | 1.13† | -2.98† |
| 2025-26 | 211 | 19 | 3.80† | +8.26† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.48 [-0.34, 1.30] | -1.76 [-3.87, -0.13] |
| scarcity state 0 | 873 | 1 | -9.88† | -33.04† |
| scarcity state 1 | 260 | 1 | -4.66† | -16.90† |
| scarcity state 2 | 34 | 8 | -1.94† | -6.48† |
| scarcity state 3 | 401 | 77 | 0.29 [-0.17, 0.77] | -0.80 [-1.94, 0.33] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

## h = 3: 1568 days, 87 above +5 bp

### `structural_liquidity`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.38 [0.26, 0.66] | -1.98 [-2.58, -1.24] |
| 2018-19 | 314 | 63 | 0.17 [0.07, 0.33] | -1.16 [-1.76, -0.63] |
| 2020-24 | 1043 | 5 | 0.94† | -2.82† |
| 2025-26 | 211 | 19 | 1.44 [0.80, 3.48] | +1.76 [-0.13, 6.91] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.38 [0.26, 0.66] | -1.98 [-2.58, -1.24] |
| scarcity state 0 | 875 | 2 | -4.50† | -21.48† |
| scarcity state 1 | 258 | 0 | undefined | undefined |
| scarcity state 2 | 35 | 9 | 1.03 [-0.70, 2.86] | +1.46 [-2.75, 6.50] |
| scarcity state 3 | 400 | 76 | 0.16 [0.05, 0.30] | -1.23 [-1.78, -0.77] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `structural_liquidity+h41`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.39 [0.27, 0.68] | -1.97 [-2.58, -1.21] |
| 2018-19 | 314 | 63 | 0.18 [0.09, 0.35] | -1.16 [-1.78, -0.63] |
| 2020-24 | 1043 | 5 | 0.91† | -2.86† |
| 2025-26 | 211 | 19 | 1.51 [0.84, 3.65] | +2.04 [0.05, 7.64] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.39 [0.27, 0.68] | -1.97 [-2.58, -1.21] |
| scarcity state 0 | 875 | 2 | -4.83† | -22.68† |
| scarcity state 1 | 258 | 0 | undefined | undefined |
| scarcity state 2 | 35 | 9 | 0.94 [-0.85, 2.95] | +1.29 [-3.03, 6.84] |
| scarcity state 3 | 400 | 76 | 0.17 [0.07, 0.31] | -1.23 [-1.76, -0.76] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `structural_kinked_fitted`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.39 [0.27, 0.69] | -1.96 [-2.58, -1.20] |
| 2018-19 | 314 | 63 | 0.18 [0.09, 0.35] | -1.15 [-1.76, -0.61] |
| 2020-24 | 1043 | 5 | 0.87† | -2.97† |
| 2025-26 | 211 | 19 | 1.51 [0.84, 3.63] | +2.03 [0.04, 7.60] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.39 [0.27, 0.69] | -1.96 [-2.58, -1.20] |
| scarcity state 0 | 875 | 2 | -4.83† | -22.69† |
| scarcity state 1 | 258 | 0 | undefined | undefined |
| scarcity state 2 | 35 | 9 | 0.93 [-0.85, 2.93] | +1.26 [-3.03, 6.80] |
| scarcity state 3 | 400 | 76 | 0.17 [0.07, 0.32] | -1.22 [-1.76, -0.74] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `structural_kinked_rolling`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.56 [0.34, 0.88] | -1.45 [-2.31, -0.59] |
| 2018-19 | 314 | 63 | 0.30 [0.12, 0.70] | -0.69 [-1.46, 0.36] |
| 2020-24 | 1043 | 5 | 0.28 [-6.59, 0.80] | -4.57 [-29.71, -3.14] |
| 2025-26 | 211 | 19 | 1.39 [0.89, 2.90] | +1.04 [-0.29, 3.97] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.56 [0.34, 0.88] | -1.45 [-2.31, -0.59] |
| scarcity state 0 | 875 | 2 | -3.12† | -16.95† |
| scarcity state 1 | 258 | 0 | undefined | undefined |
| scarcity state 2 | 35 | 9 | 2.16† | +2.70† |
| scarcity state 3 | 400 | 76 | 0.25 [0.09, 0.53] | -0.91 [-1.56, -0.20] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm+settle+h41`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.04 [-0.11, 0.13] | -2.35 [-4.48, -1.27] |
| 2018-19 | 314 | 63 | -0.13† | -3.08† |
| 2020-24 | 1043 | 5 | undefined | undefined |
| 2025-26 | 211 | 19 | 0.29† | +1.46† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.04 [-0.11, 0.13] | -2.35 [-4.48, -1.27] |
| scarcity state 0 | 875 | 2 | undefined | undefined |
| scarcity state 1 | 258 | 0 | undefined | undefined |
| scarcity state 2 | 35 | 9 | 0.25† | +2.17† |
| scarcity state 3 | 400 | 76 | -0.05† | -2.13† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm+settle+h41+dist_roll`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.04 [-0.11, 0.13] | -2.33 [-4.50, -1.24] |
| 2018-19 | 314 | 63 | -0.13† | -3.09† |
| 2020-24 | 1043 | 5 | undefined | undefined |
| 2025-26 | 211 | 19 | 0.27† | +1.09† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.04 [-0.11, 0.13] | -2.33 [-4.50, -1.24] |
| scarcity state 0 | 875 | 2 | undefined | undefined |
| scarcity state 1 | 258 | 0 | undefined | undefined |
| scarcity state 2 | 35 | 9 | 0.25† | +2.18† |
| scarcity state 3 | 400 | 76 | -0.05† | -2.08† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `persistence_logistic`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.91 [0.50, 1.45] | -0.81 [-1.88, 0.31] |
| 2018-19 | 314 | 63 | 0.33 [0.09, 0.97] | -0.74 [-1.47, 0.56] |
| 2020-24 | 1043 | 5 | 1.04 [-7.07, 4.29] | -2.88 [-28.41, 1.96] |
| 2025-26 | 211 | 19 | 1.09 [0.61, 2.40] | +0.26 [-1.20, 2.92] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.91 [0.50, 1.45] | -0.81 [-1.88, 0.31] |
| scarcity state 0 | 875 | 2 | -2.88† | -15.08† |
| scarcity state 1 | 258 | 0 | undefined | undefined |
| scarcity state 2 | 35 | 9 | 1.42 [0.11, 2.90] | +1.56 [-1.34, 4.12] |
| scarcity state 3 | 400 | 76 | 0.21 [0.02, 0.61] | -1.08 [-1.67, -0.28] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `calendar_climatology`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.45 [-0.43, 1.33] | -1.83 [-4.09, -0.02] |
| 2018-19 | 314 | 63 | 0.61 [0.14, 1.11] | -0.04 [-1.22, 1.13] |
| 2020-24 | 1043 | 5 | 1.13† | -3.00† |
| 2025-26 | 211 | 19 | 3.27† | +6.78† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1568 | 87 | 0.45 [-0.43, 1.33] | -1.83 [-4.09, -0.02] |
| scarcity state 0 | 875 | 2 | -12.11† | -38.52† |
| scarcity state 1 | 258 | 0 | undefined | undefined |
| scarcity state 2 | 35 | 9 | -1.74† | -5.72† |
| scarcity state 3 | 400 | 76 | 0.29 [-0.16, 0.75] | -0.82 [-1.99, 0.29] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

## h = 4: 1567 days, 87 above +5 bp

### `structural_liquidity`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1567 | 87 | 0.44 [0.30, 0.70] | -1.71 [-2.33, -1.02] |
| 2018-19 | 313 | 63 | 0.16 [0.03, 0.31] | -1.09 [-1.73, -0.57] |
| 2020-24 | 1043 | 5 | 0.85 [-2.43, 1.43] | -2.86 [-14.95, -1.42] |
| 2025-26 | 211 | 19 | 1.01 [0.60, 2.09] | +0.41 [-1.08, 3.17] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1567 | 87 | 0.44 [0.30, 0.70] | -1.71 [-2.33, -1.02] |
| scarcity state 0 | 873 | 2 | -0.98† | -9.67† |
| scarcity state 1 | 260 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 9 | 1.83† | +3.20† |
| scarcity state 3 | 400 | 76 | 0.15 [0.00, 0.28] | -1.20 [-1.81, -0.76] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `structural_liquidity+h41`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1567 | 87 | 0.44 [0.29, 0.80] | -1.79 [-2.44, -0.85] |
| 2018-19 | 313 | 63 | 0.20 [0.11, 0.42] | -1.11 [-1.69, -0.47] |
| 2020-24 | 1043 | 5 | 0.86 [-2.73, 1.47] | -2.80 [-16.07, -1.33] |
| 2025-26 | 211 | 19 | 1.05 [0.63, 2.19] | +0.59 [-0.95, 3.55] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1567 | 87 | 0.44 [0.29, 0.80] | -1.79 [-2.44, -0.85] |
| scarcity state 0 | 873 | 2 | -1.19† | -10.44† |
| scarcity state 1 | 260 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 9 | 1.83† | +3.30† |
| scarcity state 3 | 400 | 76 | 0.19 [0.10, 0.38] | -1.19 [-1.72, -0.66] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `structural_kinked_fitted`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1567 | 87 | 0.44 [0.29, 0.80] | -1.78 [-2.43, -0.83] |
| 2018-19 | 313 | 63 | 0.20 [0.11, 0.43] | -1.10 [-1.68, -0.44] |
| 2020-24 | 1043 | 5 | 0.85 [-2.76, 1.45] | -2.86 [-16.19, -1.40] |
| 2025-26 | 211 | 19 | 1.05 [0.63, 2.18] | +0.59 [-0.95, 3.54] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1567 | 87 | 0.44 [0.29, 0.80] | -1.78 [-2.43, -0.83] |
| scarcity state 0 | 873 | 2 | -1.20† | -10.48† |
| scarcity state 1 | 260 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 9 | 1.83† | +3.30† |
| scarcity state 3 | 400 | 76 | 0.19 [0.10, 0.39] | -1.18 [-1.71, -0.65] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `structural_kinked_rolling`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1567 | 87 | 0.71 [0.50, 1.00] | -0.98 [-1.81, -0.16] |
| 2018-19 | 313 | 63 | 0.46 [0.26, 0.80] | -0.31 [-1.05, 0.65] |
| 2020-24 | 1043 | 5 | 0.38 [-1.85, 0.77] | -4.18 [-13.03, -2.89] |
| 2025-26 | 211 | 19 | 1.06 [0.69, 2.06] | +0.21 [-1.09, 2.14] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1567 | 87 | 0.71 [0.50, 1.00] | -0.98 [-1.81, -0.16] |
| scarcity state 0 | 873 | 2 | -0.71† | -8.78† |
| scarcity state 1 | 260 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 9 | 1.76† | +2.12† |
| scarcity state 3 | 400 | 76 | 0.37 [0.19, 0.61] | -0.65 [-1.30, -0.01] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm+settle+h41`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1567 | 87 | 0.05 [-0.09, 0.14] | -2.11 [-4.14, -1.08] |
| 2018-19 | 313 | 63 | -0.12† | -3.03† |
| 2020-24 | 1043 | 5 | undefined | undefined |
| 2025-26 | 211 | 19 | 0.31† | +1.70† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1567 | 87 | 0.05 [-0.09, 0.14] | -2.11 [-4.14, -1.08] |
| scarcity state 0 | 873 | 2 | undefined | undefined |
| scarcity state 1 | 260 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 9 | 0.39† | +4.11† |
| scarcity state 3 | 400 | 76 | -0.04† | -2.01† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm+settle+h41+dist_roll`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1567 | 87 | 0.07 [-0.09, 0.15] | -1.96 [-4.07, -0.94] |
| 2018-19 | 313 | 63 | -0.12† | -2.96† |
| 2020-24 | 1043 | 5 | undefined | undefined |
| 2025-26 | 211 | 19 | 0.31† | +1.74† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1567 | 87 | 0.07 [-0.09, 0.15] | -1.96 [-4.07, -0.94] |
| scarcity state 0 | 873 | 2 | undefined | undefined |
| scarcity state 1 | 260 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 9 | 0.29† | +2.75† |
| scarcity state 3 | 400 | 76 | -0.03† | -1.85† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `persistence_logistic`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1567 | 87 | 1.10 [0.80, 1.50] | -0.32 [-1.15, 0.53] |
| 2018-19 | 313 | 63 | 0.58 [0.26, 1.07] | -0.24 [-1.11, 0.69] |
| 2020-24 | 1043 | 5 | 0.92 [-1.80, 1.73] | -2.91 [-12.10, -1.21] |
| 2025-26 | 211 | 19 | 0.86 [0.51, 1.73] | -0.32 [-1.65, 1.53] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1567 | 87 | 1.10 [0.80, 1.50] | -0.32 [-1.15, 0.53] |
| scarcity state 0 | 873 | 2 | -0.53† | -7.88† |
| scarcity state 1 | 260 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 9 | 1.54† | +1.83† |
| scarcity state 3 | 400 | 76 | 0.38 [0.13, 0.72] | -0.77 [-1.47, -0.08] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `calendar_climatology`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1567 | 87 | 0.40 [-0.48, 1.27] | -1.93 [-4.18, -0.08] |
| 2018-19 | 313 | 63 | 0.58 [0.14, 1.10] | -0.08 [-1.30, 1.11] |
| 2020-24 | 1043 | 5 | 1.12† | -3.02† |
| 2025-26 | 211 | 19 | 2.97† | +5.97† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1567 | 87 | 0.40 [-0.48, 1.27] | -1.93 [-4.18, -0.08] |
| scarcity state 0 | 873 | 2 | -12.05† | -38.35† |
| scarcity state 1 | 260 | 0 | undefined | undefined |
| scarcity state 2 | 34 | 9 | -1.83† | -5.93† |
| scarcity state 3 | 400 | 76 | 0.26 [-0.18, 0.73] | -0.87 [-2.07, 0.25] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

## h = 5: 1566 days, 87 above +5 bp

### `structural_liquidity`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1566 | 87 | 0.32 [0.04, 0.61] | -1.96 [-2.98, -1.23] |
| 2018-19 | 312 | 63 | 0.10 [-0.04, 0.25] | -1.13 [-1.84, -0.63] |
| 2020-24 | 1043 | 5 | 1.16 [-0.90, 2.05] | -2.18 [-8.79, -0.34] |
| 2025-26 | 211 | 19 | 1.05 [0.66, 2.11] | +0.43 [-1.08, 2.98] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1566 | 87 | 0.32 [0.04, 0.61] | -1.96 [-2.98, -1.23] |
| scarcity state 0 | 871 | 2 | 0.84† | -3.18† |
| scarcity state 1 | 261 | 0 | undefined | undefined |
| scarcity state 2 | 35 | 10 | 1.59 [-0.18, 3.38] | +2.66 [-2.52, 5.68] |
| scarcity state 3 | 399 | 75 | 0.08 [-0.06, 0.22] | -1.27 [-1.91, -0.84] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `structural_liquidity+h41`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1566 | 87 | 0.42 [0.29, 0.77] | -1.82 [-2.47, -0.93] |
| 2018-19 | 312 | 63 | 0.19 [0.09, 0.37] | -1.05 [-1.70, -0.46] |
| 2020-24 | 1043 | 5 | 1.18 [-1.05, 2.12] | -2.10 [-9.30, -0.21] |
| 2025-26 | 211 | 19 | 1.09 [0.68, 2.24] | +0.60 [-0.97, 3.39] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1566 | 87 | 0.42 [0.29, 0.77] | -1.82 [-2.47, -0.93] |
| scarcity state 0 | 871 | 2 | 0.79† | -3.35† |
| scarcity state 1 | 261 | 0 | undefined | undefined |
| scarcity state 2 | 35 | 10 | 1.54 [-0.28, 3.32] | +2.63 [-2.79, 5.91] |
| scarcity state 3 | 399 | 75 | 0.18 [0.08, 0.33] | -1.16 [-1.71, -0.68] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `structural_kinked_fitted`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1566 | 87 | 0.42 [0.28, 0.77] | -1.82 [-2.48, -0.93] |
| 2018-19 | 312 | 63 | 0.19 [0.09, 0.37] | -1.04 [-1.70, -0.44] |
| 2020-24 | 1043 | 5 | 1.17 [-1.05, 2.10] | -2.15 [-9.29, -0.29] |
| 2025-26 | 211 | 19 | 1.09 [0.68, 2.23] | +0.60 [-0.97, 3.37] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1566 | 87 | 0.42 [0.28, 0.77] | -1.82 [-2.48, -0.93] |
| scarcity state 0 | 871 | 2 | 0.80† | -3.33† |
| scarcity state 1 | 261 | 0 | undefined | undefined |
| scarcity state 2 | 35 | 10 | 1.54 [-0.28, 3.32] | +2.63 [-2.78, 5.88] |
| scarcity state 3 | 399 | 75 | 0.18 [0.08, 0.33] | -1.16 [-1.70, -0.67] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `structural_kinked_rolling`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1566 | 87 | 0.74 [0.49, 1.04] | -0.90 [-1.81, -0.09] |
| 2018-19 | 312 | 63 | 0.38 [0.19, 0.69] | -0.42 [-1.21, 0.41] |
| 2020-24 | 1043 | 5 | 0.57 [-0.71, 1.04] | -3.70 [-8.21, -2.32] |
| 2025-26 | 211 | 19 | 1.12 [0.76, 2.08] | +0.41 [-0.93, 2.44] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1566 | 87 | 0.74 [0.49, 1.04] | -0.90 [-1.81, -0.09] |
| scarcity state 0 | 871 | 2 | 0.74† | -3.43† |
| scarcity state 1 | 261 | 0 | undefined | undefined |
| scarcity state 2 | 35 | 10 | 1.53 [0.56, 2.32] | +2.07 [-0.91, 4.27] |
| scarcity state 3 | 399 | 75 | 0.31 [0.14, 0.54] | -0.74 [-1.44, -0.09] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm+settle+h41`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1566 | 87 | 0.04 [-0.10, 0.13] | -2.34 [-4.37, -1.15] |
| 2018-19 | 312 | 63 | -0.13† | -3.08† |
| 2020-24 | 1043 | 5 | undefined | undefined |
| 2025-26 | 211 | 19 | 0.32† | +1.78† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1566 | 87 | 0.04 [-0.10, 0.13] | -2.34 [-4.37, -1.15] |
| scarcity state 0 | 871 | 2 | undefined | undefined |
| scarcity state 1 | 261 | 0 | undefined | undefined |
| scarcity state 2 | 35 | 10 | 0.33† | +3.36† |
| scarcity state 3 | 399 | 75 | -0.06† | -2.31† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm+settle+h41+dist_roll`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1566 | 87 | 0.05 [-0.09, 0.15] | -2.13 [-4.23, -0.93] |
| 2018-19 | 312 | 63 | -0.12† | -3.01† |
| 2020-24 | 1043 | 5 | undefined | undefined |
| 2025-26 | 211 | 19 | 0.29† | +1.41† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1566 | 87 | 0.05 [-0.09, 0.15] | -2.13 [-4.23, -0.93] |
| scarcity state 0 | 871 | 2 | undefined | undefined |
| scarcity state 1 | 261 | 0 | undefined | undefined |
| scarcity state 2 | 35 | 10 | 0.28† | +2.69† |
| scarcity state 3 | 399 | 75 | -0.04† | -2.05† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `persistence_logistic`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1566 | 87 | 0.94 [0.59, 1.38] | -0.63 [-1.63, 0.20] |
| 2018-19 | 312 | 63 | 0.35 [0.18, 0.66] | -0.56 [-1.29, 0.12] |
| 2020-24 | 1043 | 5 | 1.21 [-0.65, 2.67] | -2.33 [-7.85, 0.31] |
| 2025-26 | 211 | 19 | 0.92 [0.58, 1.80] | -0.20 [-1.64, 1.59] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1566 | 87 | 0.94 [0.59, 1.38] | -0.63 [-1.63, 0.20] |
| scarcity state 0 | 871 | 2 | 0.84† | -3.37† |
| scarcity state 1 | 261 | 0 | undefined | undefined |
| scarcity state 2 | 35 | 10 | 1.40 [-0.22, 2.84] | +1.72 [-2.54, 4.03] |
| scarcity state 3 | 399 | 75 | 0.27 [0.13, 0.49] | -0.89 [-1.50, -0.34] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `calendar_climatology`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1566 | 87 | 0.37 [-0.57, 1.26] | -2.00 [-4.37, -0.24] |
| 2018-19 | 312 | 63 | 0.56 [0.09, 1.08] | -0.12 [-1.33, 1.06] |
| 2020-24 | 1043 | 5 | 1.16† | -2.94† |
| 2025-26 | 211 | 19 | 2.93† | +5.86† |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1566 | 87 | 0.37 [-0.57, 1.26] | -2.00 [-4.37, -0.24] |
| scarcity state 0 | 871 | 2 | -10.84† | -35.00† |
| scarcity state 1 | 261 | 0 | undefined | undefined |
| scarcity state 2 | 35 | 10 | -1.88† | -5.97† |
| scarcity state 3 | 399 | 75 | 0.26 [-0.23, 0.71] | -0.90 [-2.17, 0.19] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.
