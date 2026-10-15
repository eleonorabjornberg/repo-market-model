Table M1 is not made: the judge is not run on days past 2025-12-31 (#684, ruling of 13 October 2026).

Table M2. On ordinary days at +5 bp: the forecast's AUROC for pressure days [90%], and the reliability intercept and slope (logistic of the outcome on logit(forecast); `-` where the forecast is constant or the fit is not formed). The control forecasts exactly 0 there.

| row | h | days | pressure days | mean forecast | realised | AUROC [90%] | intercept | slope |
|---|---|---|---|---|---|---|---|---|
| `risk_gbm+settle+h41+dist_roll` | 1 | 1602 | 84 | 0.0000 | 0.0524 | 0.500 (constant) | - | - |
| `risk_gbm+settle+h41+dist_roll` | 2 | 1602 | 84 | 0.0000 | 0.0524 | 0.500 (constant) | - | - |
| `risk_gbm+settle+h41+dist_roll` | 3 | 1602 | 84 | 0.0000 | 0.0524 | 0.500 (constant) | - | - |
| `risk_gbm+settle+h41+dist_roll` | 4 | 1601 | 84 | 0.0000 | 0.0525 | 0.500 (constant) | - | - |
| `risk_gbm+settle+h41+dist_roll` | 5 | 1600 | 84 | 0.0000 | 0.0525 | 0.500 (constant) | - | - |
| `risk_gbm+settle+h41+dist_roll+every_day` | 1 | 1602 | 84 | 0.0819 | 0.0524 | 0.900 [0.86, 0.93] | -0.61 | 1.00 |
| `risk_gbm+settle+h41+dist_roll+every_day` | 2 | 1602 | 84 | 0.0846 | 0.0524 | 0.842 [0.77, 0.90] | -0.72 | 0.94 |
| `risk_gbm+settle+h41+dist_roll+every_day` | 3 | 1602 | 84 | 0.0989 | 0.0524 | 0.802 [0.72, 0.87] | -0.77 | 0.99 |
| `risk_gbm+settle+h41+dist_roll+every_day` | 4 | 1601 | 84 | 0.0887 | 0.0525 | 0.821 [0.73, 0.89] | -0.71 | 0.97 |
| `risk_gbm+settle+h41+dist_roll+every_day` | 5 | 1600 | 84 | 0.0885 | 0.0525 | 0.807 [0.71, 0.88] | -0.96 | 0.83 |
| `risk_gbm+settle+h41+dist_roll+every_day+lagpress` | 1 | 1602 | 84 | 0.0829 | 0.0524 | 0.860 [0.79, 0.92] | -0.72 | 0.96 |
| `risk_gbm+settle+h41+dist_roll+every_day+lagpress` | 2 | 1602 | 84 | 0.0834 | 0.0524 | 0.800 [0.70, 0.88] | -0.99 | 0.80 |
| `risk_gbm+settle+h41+dist_roll+every_day+lagpress` | 3 | 1602 | 84 | 0.0885 | 0.0524 | 0.780 [0.68, 0.86] | -1.13 | 0.76 |
| `risk_gbm+settle+h41+dist_roll+every_day+lagpress` | 4 | 1601 | 84 | 0.0831 | 0.0525 | 0.783 [0.68, 0.87] | -1.11 | 0.73 |
| `risk_gbm+settle+h41+dist_roll+every_day+lagpress` | 5 | 1600 | 84 | 0.0850 | 0.0525 | 0.812 [0.70, 0.88] | -1.04 | 0.78 |

Table M3. Paired on ordinary days: the AUROC of the test less the parent's, 90% stationary-bootstrap interval.

| h | difference [90%] |
|---|---|
| 1 | -0.040 [-0.078, -0.013] |
| 2 | -0.043 [-0.093, +0.004] |
| 3 | -0.023 [-0.081, +0.030] |
| 4 | -0.038 [-0.094, +0.012] |
| 5 | +0.005 [-0.043, +0.052] |
