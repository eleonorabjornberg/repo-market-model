# Reliability slope by regime, from the tracked evidence of #624 (#683)

Pooled slopes mislead here (#670): a regime with no pressure day (2021-23) forecasts near 0 and adds a long, well-ordered stretch at the bottom of the curve, which raises the pooled slope. Read calibration within a regime. A cell with no pressure day has no slope. Figures here are development, not a verdict.

Source: `docs/pivot/evidence/off-risk-day/step2-off-risk-days.json`. Points only: that file carries no interval for a regime's slope. The slope is that of the logistic fit of the outcome on logit(forecast) on the days that are not risk dates where the forecast is above 1e-4 (1 is reliable); `undefined` is a regime with no pressure day; `–` a regime whose forecast is constant or whose fit is not formed; `uncalibrated: zero on all N` a regime whose forecast is zero (1e-4 or below) on all N pressure days, so no fit is formed and the row misses every event; `unstable` a near-separated fit (a slope beyond 25 in size); `†` a cell with fewer than 5 pressure days in the fit (the pressure days on forecasts above 1e-4, not all the cell's), whose slope is a handful of events' worth.

## `risk_gbm+every_day+gate+settle+h41+iorb+tailcap75`

| lead | all days (pooled) | regime 2018-19 | regime 2020 | regime 2021-23 | regime 2024 | regime 2025-26 |
|---|---|---|---|---|---|---|
| 1 | 2.03† | 1.39† | – | undefined | uncalibrated: zero on all 2 | uncalibrated: zero on all 15 |
| 2 | 2.66 | 2.31 | uncalibrated: zero on all 3 | undefined | uncalibrated: zero on all 2 | uncalibrated: zero on all 15 |
| 3 | 3.19 | 2.31 | uncalibrated: zero on all 3 | undefined | uncalibrated: zero on all 2 | uncalibrated: zero on all 15 |
| 4 | 1.82 | 0.19 | uncalibrated: zero on all 3 | undefined | uncalibrated: zero on all 2 | uncalibrated: zero on all 15 |
| 5 | 2.40 | 1.58 | uncalibrated: zero on all 3 | undefined | uncalibrated: zero on all 2 | uncalibrated: zero on all 15 |

## `risk_gbm+settle+h41+dist_roll`

| lead | all days (pooled) | regime 2018-19 | regime 2020 | regime 2021-23 | regime 2024 | regime 2025-26 |
|---|---|---|---|---|---|---|
| 1 | uncalibrated: zero on all 82 | uncalibrated: zero on all 62 | uncalibrated: zero on all 3 | undefined | uncalibrated: zero on all 2 | uncalibrated: zero on all 15 |
| 2 | uncalibrated: zero on all 82 | uncalibrated: zero on all 62 | uncalibrated: zero on all 3 | undefined | uncalibrated: zero on all 2 | uncalibrated: zero on all 15 |
| 3 | uncalibrated: zero on all 82 | uncalibrated: zero on all 62 | uncalibrated: zero on all 3 | undefined | uncalibrated: zero on all 2 | uncalibrated: zero on all 15 |
| 4 | uncalibrated: zero on all 82 | uncalibrated: zero on all 62 | uncalibrated: zero on all 3 | undefined | uncalibrated: zero on all 2 | uncalibrated: zero on all 15 |
| 5 | uncalibrated: zero on all 82 | uncalibrated: zero on all 62 | uncalibrated: zero on all 3 | undefined | uncalibrated: zero on all 2 | uncalibrated: zero on all 15 |

## `risk_gbm+settle+h41+dist_roll+offday`

| lead | all days (pooled) | regime 2018-19 | regime 2020 | regime 2021-23 | regime 2024 | regime 2025-26 |
|---|---|---|---|---|---|---|
| 1 | 0.83 | 0.48 | 0.61† | undefined | 0.77† | 0.79 |
| 2 | 0.85 | 0.45 | 0.91† | undefined | 2.82† | 0.70 |
| 3 | 0.80 | 0.22 | 1.10† | undefined | -0.35† | 0.73 |
| 4 | 0.78 | 0.14 | 0.98† | undefined | 1.76† | 0.76 |
| 5 | 0.79 | 0.17 | 1.16† | undefined | 1.62† | 0.73 |

## `risk_gbm+settle+h41+dist_roll+offday_mono`

| lead | all days (pooled) | regime 2018-19 | regime 2020 | regime 2021-23 | regime 2024 | regime 2025-26 |
|---|---|---|---|---|---|---|
| 1 | 0.46 | 0.31 | 0.01† | undefined | -0.69† | 0.32 |
| 2 | 0.39 | 0.14 | 0.37† | undefined | 0.17† | 0.22 |
| 3 | 0.36 | 0.10 | 0.21† | undefined | 0.26† | 0.27 |
| 4 | 0.37 | 0.07 | 0.43† | undefined | uncalibrated: zero on all 2 | 0.39 |
| 5 | 0.32 | 0.09 | 0.21† | undefined | 0.39† | 0.21 |

## `risk_gbm+settle+h41+dist_roll+offday_rate`

| lead | all days (pooled) | regime 2018-19 | regime 2020 | regime 2021-23 | regime 2024 | regime 2025-26 |
|---|---|---|---|---|---|---|
| 1 | 0.73 | 0.20 | 0.66† | undefined | 0.90† | 0.79 |
| 2 | 0.70 | 0.06 | 0.67† | undefined | 2.76† | 0.71 |
| 3 | 0.67 | -0.06 | 0.74† | undefined | 0.39† | 0.73 |
| 4 | 0.65 | -0.13 | 0.70† | undefined | 1.71† | 0.76 |
| 5 | 0.64 | -0.12 | 0.79† | undefined | 1.64† | 0.72 |
