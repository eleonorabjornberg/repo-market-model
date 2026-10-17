# Reliability slope within regimes, #631's rows on the ordinary days (#785)

Pooled slopes mislead here (#670): a regime with no pressure day (2021-23) forecasts near 0 and adds a long, well-ordered stretch at the bottom of the curve, which raises the pooled slope. Read calibration within a regime. A cell with no pressure day has no slope. Figures here are development, not a verdict.

Intercept and slope of `logit P(y = 1) = intercept + slope * logit(p)` (1 and 0 for a reliable forecast), 90% stationary-bootstrap intervals (block length 10, 2000 replications); `undefined` where the cell has no pressure day, the forecast is constant there or the fit has no maximum; no interval where the cell has too few events to give one. Regimes: 2018-19, 2020-24 (which holds 2021-23, with no pressure day) and 2025-26.

## h = 1: 1469 days, 82 above +5 bp

### `risk_gbm+settle+h41+dist_roll+every_day`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1469 | 82 | 1.00 [0.68, 1.40] | -0.51 [-1.49, 0.37] |
| 2018-19 | 294 | 62 | 0.61 [0.29, 1.24] | -0.33 [-1.17, 0.77] |
| 2020-24 | 978 | 5 | 0.62 [-0.24, 1.07] | -3.41 [-6.99, -2.28] |
| 2025-26 | 197 | 15 | 0.94 [0.71, 1.48] | -0.46 [-1.76, 0.63] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1469 | 82 | 1.00 [0.68, 1.40] | -0.51 [-1.49, 0.37] |
| scarcity state 0 | 819 | 2 | 0.41† | -4.49† |
| scarcity state 1 | 244 | 0 | undefined | undefined |
| scarcity state 2 | 32 | 7 | 0.94† | +0.41† |
| scarcity state 3 | 374 | 73 | 0.49 [0.27, 0.94] | -0.69 [-1.28, 0.14] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm+settle+h41+dist_roll+every_day+lagpress`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1469 | 82 | 0.96 [0.71, 1.21] | -0.68 [-1.38, -0.18] |
| 2018-19 | 294 | 62 | 0.51 [0.28, 0.86] | -0.53 [-1.19, -0.00] |
| 2020-24 | 978 | 5 | 0.76 [-0.82, 1.26] | -2.95 [-9.02, -1.62] |
| 2025-26 | 197 | 15 | 0.91 [0.67, 1.58] | -0.53 [-1.77, 0.58] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1469 | 82 | 0.96 [0.71, 1.21] | -0.68 [-1.38, -0.18] |
| scarcity state 0 | 819 | 2 | -0.14† | -6.50† |
| scarcity state 1 | 244 | 0 | undefined | undefined |
| scarcity state 2 | 32 | 7 | 1.05† | +0.76† |
| scarcity state 3 | 374 | 73 | 0.49 [0.28, 0.79] | -0.71 [-1.25, -0.22] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

## h = 2: 1469 days, 82 above +5 bp

### `risk_gbm+settle+h41+dist_roll+every_day`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1469 | 82 | 0.94 [0.69, 1.28] | -0.61 [-1.43, 0.13] |
| 2018-19 | 294 | 62 | 0.50 [0.23, 0.95] | -0.40 [-1.19, 0.42] |
| 2020-24 | 978 | 5 | 0.84 [-0.49, 1.55] | -2.90 [-8.12, -1.23] |
| 2025-26 | 197 | 15 | 0.68 [0.44, 1.30] | -1.03 [-2.29, 0.02] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1469 | 82 | 0.94 [0.69, 1.28] | -0.61 [-1.43, 0.13] |
| scarcity state 0 | 819 | 1 | 0.33† | -5.54† |
| scarcity state 1 | 244 | 1 | -6.51† | -27.62† |
| scarcity state 2 | 32 | 7 | 0.96 [0.17, 1.93] | +0.29 [-1.61, 2.01] |
| scarcity state 3 | 374 | 73 | 0.34 [0.15, 0.63] | -0.84 [-1.44, -0.23] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm+settle+h41+dist_roll+every_day+lagpress`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1469 | 82 | 0.79 [0.54, 1.05] | -0.95 [-1.68, -0.45] |
| 2018-19 | 294 | 62 | 0.30 [0.12, 0.57] | -0.74 [-1.46, -0.24] |
| 2020-24 | 978 | 5 | 1.24 [-2.07, 2.23] | -1.65 [-13.40, 0.58] |
| 2025-26 | 197 | 15 | 0.78 [0.53, 1.53] | -0.85 [-2.13, 0.52] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1469 | 82 | 0.79 [0.54, 1.05] | -0.95 [-1.68, -0.45] |
| scarcity state 0 | 819 | 1 | -0.18† | -7.34† |
| scarcity state 1 | 244 | 1 | -9.10† | -37.29† |
| scarcity state 2 | 32 | 7 | 1.17† | +0.92† |
| scarcity state 3 | 374 | 73 | 0.29 [0.12, 0.53] | -0.91 [-1.48, -0.45] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

## h = 3: 1469 days, 82 above +5 bp

### `risk_gbm+settle+h41+dist_roll+every_day`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1469 | 82 | 0.91 [0.50, 1.40] | -0.85 [-1.84, 0.12] |
| 2018-19 | 294 | 62 | 0.32 [0.10, 0.87] | -0.71 [-1.43, 0.40] |
| 2020-24 | 978 | 5 | 1.05 [-0.77, 3.17] | -2.76 [-8.17, 0.55] |
| 2025-26 | 197 | 15 | 0.87 [0.48, 1.60] | -0.66 [-2.24, 0.88] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1469 | 82 | 0.91 [0.50, 1.40] | -0.85 [-1.84, 0.12] |
| scarcity state 0 | 820 | 2 | -0.29† | -6.91† |
| scarcity state 1 | 243 | 0 | undefined | undefined |
| scarcity state 2 | 32 | 7 | 1.21 [-1.09, 2.05] | +0.79 [-4.63, 2.32] |
| scarcity state 3 | 374 | 73 | 0.21 [0.05, 0.57] | -1.05 [-1.61, -0.29] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm+settle+h41+dist_roll+every_day+lagpress`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1469 | 82 | 0.75 [0.45, 1.04] | -1.09 [-1.84, -0.58] |
| 2018-19 | 294 | 62 | 0.23 [0.05, 0.51] | -0.86 [-1.53, -0.32] |
| 2020-24 | 978 | 5 | 1.67 [-1.48, 3.24] | -0.89 [-10.71, 2.31] |
| 2025-26 | 197 | 15 | 0.76 [0.49, 1.38] | -0.85 [-2.21, 0.27] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1469 | 82 | 0.75 [0.45, 1.04] | -1.09 [-1.84, -0.58] |
| scarcity state 0 | 820 | 2 | -0.28† | -6.93† |
| scarcity state 1 | 243 | 0 | undefined | undefined |
| scarcity state 2 | 32 | 7 | 1.21† | +1.52† |
| scarcity state 3 | 374 | 73 | 0.23 [0.05, 0.51] | -0.99 [-1.55, -0.52] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

## h = 4: 1468 days, 82 above +5 bp

### `risk_gbm+settle+h41+dist_roll+every_day`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1468 | 82 | 0.99 [0.72, 1.35] | -0.57 [-1.34, 0.20] |
| 2018-19 | 293 | 62 | 0.52 [0.23, 0.96] | -0.32 [-1.15, 0.48] |
| 2020-24 | 978 | 5 | 0.92 [-0.25, 1.72] | -2.81 [-6.93, -1.03] |
| 2025-26 | 197 | 15 | 0.73 [0.45, 1.42] | -1.02 [-2.49, 0.27] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1468 | 82 | 0.99 [0.72, 1.35] | -0.57 [-1.34, 0.20] |
| scarcity state 0 | 819 | 2 | 0.36† | -4.82† |
| scarcity state 1 | 244 | 0 | undefined | undefined |
| scarcity state 2 | 31 | 7 | 1.15 [-1.44, 2.19] | +0.77 [-5.28, 3.41] |
| scarcity state 3 | 374 | 73 | 0.35 [0.13, 0.65] | -0.81 [-1.45, -0.20] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm+settle+h41+dist_roll+every_day+lagpress`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1468 | 82 | 0.71 [0.35, 1.03] | -1.08 [-2.09, -0.44] |
| 2018-19 | 293 | 62 | 0.21 [0.05, 0.54] | -0.90 [-1.63, -0.23] |
| 2020-24 | 978 | 5 | 1.19 [-0.43, 2.11] | -1.81 [-8.03, 0.49] |
| 2025-26 | 197 | 15 | 0.68 [0.44, 1.50] | -1.03 [-2.22, 0.60] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1468 | 82 | 0.71 [0.35, 1.03] | -1.08 [-2.09, -0.44] |
| scarcity state 0 | 819 | 2 | -0.02† | -6.10† |
| scarcity state 1 | 244 | 0 | undefined | undefined |
| scarcity state 2 | 31 | 7 | 1.76 [-4.62, 4.42] | +2.82 [-14.89, 8.56] |
| scarcity state 3 | 374 | 73 | 0.20 [0.05, 0.48] | -1.06 [-1.65, -0.51] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

## h = 5: 1467 days, 82 above +5 bp

### `risk_gbm+settle+h41+dist_roll+every_day`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1467 | 82 | 0.85 [0.51, 1.26] | -0.83 [-1.82, 0.04] |
| 2018-19 | 292 | 62 | 0.32 [0.15, 0.65] | -0.60 [-1.32, 0.11] |
| 2020-24 | 978 | 5 | 1.18 [-0.10, 2.39] | -2.28 [-6.20, 0.08] |
| 2025-26 | 197 | 15 | 0.81 [0.52, 1.52] | -0.87 [-2.41, 0.39] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1467 | 82 | 0.85 [0.51, 1.26] | -0.83 [-1.82, 0.04] |
| scarcity state 0 | 819 | 2 | 0.86† | -3.24† |
| scarcity state 1 | 243 | 0 | undefined | undefined |
| scarcity state 2 | 32 | 8 | 1.15 [-1.25, 2.22] | +0.91 [-5.30, 3.48] |
| scarcity state 3 | 373 | 72 | 0.26 [0.12, 0.48] | -0.92 [-1.51, -0.34] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

### `risk_gbm+settle+h41+dist_roll+every_day+lagpress`

By regime.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1467 | 82 | 0.79 [0.55, 1.04] | -0.97 [-1.66, -0.48] |
| 2018-19 | 292 | 62 | 0.34 [0.16, 0.55] | -0.61 [-1.27, -0.14] |
| 2020-24 | 978 | 5 | 1.35 [-0.37, 2.41] | -1.38 [-7.92, 1.08] |
| 2025-26 | 197 | 15 | 0.62 [0.39, 1.42] | -1.09 [-2.29, 0.52] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.

By as-of scarcity state.

| cell | days | pressure days | slope [90%] | intercept [90%] |
|---|---|---|---|---|
| pooled | 1467 | 82 | 0.79 [0.55, 1.04] | -0.97 [-1.66, -0.48] |
| scarcity state 0 | 819 | 2 | 0.37† | -4.76† |
| scarcity state 1 | 243 | 0 | undefined | undefined |
| scarcity state 2 | 32 | 8 | 2.38† | +4.09† |
| scarcity state 3 | 373 | 72 | 0.31 [0.15, 0.50] | -0.86 [-1.44, -0.41] |

† a figure without an interval: the cell has too few pressure days (or days without one), or too many of its resamples were undefined; its slope is a handful of events' worth.
