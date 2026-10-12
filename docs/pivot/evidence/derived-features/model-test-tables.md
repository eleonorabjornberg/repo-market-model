Table M1. The judge in force (tiers 1, 3 and 5; the weighted rule is the one in force, the flat rule is reported beside it). Tier 1: onsets flagged at some lead 1 to 5, recall [90%], the pooled false alarms per onset (a false alarm counted once however many leads flag it; limit 2, #550); tier 1 also needs the recall conditions at each lead.

| row | rule | onsets flagged | recall [90%] | pooled false alarms per onset | tier 1 | tier 3 | tier 5 | passes |
|---|---|---|---|---|---|---|---|---|
| `risk_gbm+settle+h41` | weighted | 14 of 26 | 0.538 [0.353, 0.710] | 1.44 | yes | no | no | no |
| `risk_gbm+settle+h41` | flat | 14 of 26 | 0.538 [0.353, 0.710] | 2.00 | yes | no | no | no |
| `risk_gbm+settle+h41+dist_roll` | weighted | 15 of 26 | 0.577 [0.400, 0.762] | 1.27 | yes | no | no | no |
| `risk_gbm+settle+h41+dist_roll` | flat | 15 of 26 | 0.577 [0.400, 0.762] | 1.85 | yes | no | no | no |
| `risk_gbm+settle+h41+dist_roll+every_day` | weighted | 19 of 26 | 0.731 [0.556, 0.889] | 3.49 | no | yes | yes | no |
| `risk_gbm+settle+h41+dist_roll+every_day` | flat | 17 of 26 | 0.654 [0.476, 0.826] | 5.62 | no | yes | yes | no |
| `risk_gbm+settle+h41+dist_roll+every_day+lagpress` | weighted | 17 of 26 | 0.654 [0.461, 0.826] | 3.51 | no | yes | yes | no |
| `risk_gbm+settle+h41+dist_roll+every_day+lagpress` | flat | 16 of 26 | 0.615 [0.429, 0.790] | 4.92 | no | yes | yes | no |

Table M2. On ordinary days at +5 bp: the forecast's AUROC for pressure days [90%], and the reliability intercept and slope (logistic of the outcome on logit(forecast); `-` where the forecast is constant or the fit is not formed). The control forecasts exactly 0 there.

| row | h | days | pressure days | mean forecast | realised | AUROC [90%] | intercept | slope |
|---|---|---|---|---|---|---|---|---|
| `risk_gbm+settle+h41+dist_roll` | 1 | 1469 | 82 | 0.0000 | 0.0558 | 0.500 (constant) | - | - |
| `risk_gbm+settle+h41+dist_roll` | 2 | 1469 | 82 | 0.0000 | 0.0558 | 0.500 (constant) | - | - |
| `risk_gbm+settle+h41+dist_roll` | 3 | 1469 | 82 | 0.0000 | 0.0558 | 0.500 (constant) | - | - |
| `risk_gbm+settle+h41+dist_roll` | 4 | 1468 | 82 | 0.0000 | 0.0559 | 0.500 (constant) | - | - |
| `risk_gbm+settle+h41+dist_roll` | 5 | 1467 | 82 | 0.0000 | 0.0559 | 0.500 (constant) | - | - |
| `risk_gbm+settle+h41+dist_roll+every_day` | 1 | 1469 | 82 | 0.0811 | 0.0558 | 0.903 [0.86, 0.94] | -0.51 | 1.00 |
| `risk_gbm+settle+h41+dist_roll+every_day` | 2 | 1469 | 82 | 0.0828 | 0.0558 | 0.844 [0.78, 0.90] | -0.61 | 0.94 |
| `risk_gbm+settle+h41+dist_roll+every_day` | 3 | 1469 | 82 | 0.0981 | 0.0558 | 0.802 [0.72, 0.87] | -0.72 | 0.98 |
| `risk_gbm+settle+h41+dist_roll+every_day` | 4 | 1468 | 82 | 0.0866 | 0.0559 | 0.827 [0.73, 0.89] | -0.57 | 0.99 |
| `risk_gbm+settle+h41+dist_roll+every_day` | 5 | 1467 | 82 | 0.0866 | 0.0559 | 0.814 [0.73, 0.88] | -0.83 | 0.85 |
| `risk_gbm+settle+h41+dist_roll+every_day+lagpress` | 1 | 1469 | 82 | 0.0840 | 0.0558 | 0.864 [0.79, 0.92] | -0.68 | 0.96 |
| `risk_gbm+settle+h41+dist_roll+every_day+lagpress` | 2 | 1469 | 82 | 0.0839 | 0.0558 | 0.799 [0.70, 0.88] | -0.95 | 0.79 |
| `risk_gbm+settle+h41+dist_roll+every_day+lagpress` | 3 | 1469 | 82 | 0.0900 | 0.0558 | 0.779 [0.68, 0.87] | -1.09 | 0.75 |
| `risk_gbm+settle+h41+dist_roll+every_day+lagpress` | 4 | 1468 | 82 | 0.0830 | 0.0559 | 0.786 [0.69, 0.87] | -1.03 | 0.73 |
| `risk_gbm+settle+h41+dist_roll+every_day+lagpress` | 5 | 1467 | 82 | 0.0854 | 0.0559 | 0.818 [0.71, 0.89] | -0.97 | 0.79 |

Table M3. Paired on ordinary days: the AUROC of the test less the parent's, 90% stationary-bootstrap interval.

| h | difference [90%] |
|---|---|
| 1 | -0.039 [-0.077, -0.014] |
| 2 | -0.045 [-0.100, +0.006] |
| 3 | -0.022 [-0.083, +0.033] |
| 4 | -0.040 [-0.098, +0.010] |
| 5 | +0.004 [-0.044, +0.052] |
