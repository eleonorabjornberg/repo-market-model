# Reliability slope by regime, from the tracked evidence of #624 (#683)

Pooled slopes mislead here (#670): a regime with no pressure day (2021-23) forecasts near 0 and adds a long, well-ordered stretch at the bottom of the curve, which raises the pooled slope. Read calibration within a regime. A cell with no pressure day has no slope. Figures here are development, not a verdict.

Source: `docs/pivot/evidence/off-risk-day/step1.json`. Points only: that file carries no interval for a regime's slope. The slope is that of the logistic fit of the outcome on logit(forecast) on the days that are not risk dates where the forecast is above 1e-4 (1 is reliable); `undefined` is a regime with no pressure day; `–` a regime whose forecast is constant or whose fit is not formed; `unstable` a near-separated fit (a slope beyond 25 in size); `†` a cell with fewer than 5 pressure days, whose slope is a handful of events' worth.

## `risk_gbm+every_day+gate+settle+h41+iorb`

| lead | all days (pooled) | regime 2018-19 | regime 2020 | regime 2021-23 | regime 2024 | regime 2025-26 |
|---|---|---|---|---|---|---|
| 1 | 0.49 | 0.24 | – | undefined | – | 0.40 |
| 2 | 0.57 | 0.28 | – | undefined | – | 0.29 |
| 3 | 0.45 | 0.10 | – | undefined | – | 0.30 |
| 4 | 0.65 | 0.38 | – | undefined | – | 0.26 |
| 5 | 0.56 | 0.08 | – | undefined | – | 0.42 |

## `risk_gbm+every_day+gate+settle+h41+iorb+tailcap75`

| lead | all days (pooled) | regime 2018-19 | regime 2020 | regime 2021-23 | regime 2024 | regime 2025-26 |
|---|---|---|---|---|---|---|
| 1 | 2.03 | 1.39 | – | undefined | – | – |
| 2 | 2.66 | 2.31 | – | undefined | – | – |
| 3 | 3.19 | 2.31 | – | undefined | – | – |
| 4 | 1.82 | 0.19 | – | undefined | – | – |
| 5 | 2.40 | 1.58 | – | undefined | – | – |

## `risk_gbm+every_day+gate+settle+h41+iorb+tailcap75+floor`

| lead | all days (pooled) | regime 2018-19 | regime 2020 | regime 2021-23 | regime 2024 | regime 2025-26 |
|---|---|---|---|---|---|---|
| 1 | 0.46 | 0.12 | 6.20† | undefined | unstable | -11.27 |
| 2 | 0.38 | -0.01 | 6.92† | undefined | unstable | -19.70 |
| 3 | 0.27 | -0.05 | 6.66† | undefined | unstable | unstable |
| 4 | 0.40 | 0.05 | 6.39† | undefined | unstable | unstable |
| 5 | 0.46 | 0.12 | 7.09† | undefined | unstable | unstable |

## `risk_gbm+every_day+gate+settle+h41+iorb+tailcap75+recent_floor`

| lead | all days (pooled) | regime 2018-19 | regime 2020 | regime 2021-23 | regime 2024 | regime 2025-26 |
|---|---|---|---|---|---|---|
| 1 | 0.57 | 0.13 | 0.41† | undefined | – | 0.89 |
| 2 | 0.55 | 0.08 | -0.69† | undefined | – | 0.81 |
| 3 | 0.53 | 0.07 | -0.70† | undefined | – | 0.72 |
| 4 | 0.58 | 0.13 | -0.70† | undefined | – | 0.73 |
| 5 | 0.59 | 0.15 | 0.06† | undefined | – | 0.70 |

## `risk_gbm+every_day+gate+settle+h41+iorb+tailcap75+state_floor`

| lead | all days (pooled) | regime 2018-19 | regime 2020 | regime 2021-23 | regime 2024 | regime 2025-26 |
|---|---|---|---|---|---|---|
| 1 | 0.73 | 0.12 | 6.20† | undefined | unstable | 1.36 |
| 2 | 0.73 | -0.01 | 6.92† | undefined | unstable | 1.35 |
| 3 | 0.63 | -0.05 | 6.66† | undefined | unstable | 1.35 |
| 4 | 0.75 | 0.05 | 6.39† | undefined | unstable | 1.34 |
| 5 | 0.76 | 0.12 | 7.09† | undefined | unstable | 1.17 |
