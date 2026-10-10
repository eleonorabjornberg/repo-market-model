Best single passer (unweighted rule): `risk_gbm_base`. Onsets 26 (warned at some h >= 1).

| row | warned | 2018 (of 4) | 2019 (of 13) | 2020 (of 2) | 2024 (of 2) | 2025 (of 5) |
|---|---|---|---|---|---|---|
| risk_gbm | 13 | 0 | 10 | 0 | 0 | 3 |
| risk_gbm_base | 14 | 0 | 10 | 0 | 0 | 4 |
| risk_logistic | 14 | 0 | 10 | 0 | 0 | 4 |
| risk_logistic_base | 13 | 0 | 10 | 0 | 0 | 3 |
| risk_quantile_skewt_base | 14 | 0 | 10 | 0 | 0 | 4 |
| calibrated_stack_logistic | 14 | 0 | 13 | 0 | 0 | 1 |
| calibrated_stack_isotonic | 11 | 0 | 11 | 0 | 0 | 0 |

Brier gain over `risk_gbm_base` at +5 bp (mean per day, 90% stationary-bootstrap interval; positive: the stack is better).

| candidate | h=1 | h=2 | h=3 | h=4 | h=5 | onsets warned minus best |
|---|---|---|---|---|---|---|
| calibrated_stack_logistic | +0.0041 [+0.0001, +0.0087] | +0.0073 [+0.0017, +0.0140] | +0.0071 [+0.0016, +0.0136] | +0.0066 [+0.0009, +0.0130] | +0.0103 [+0.0045, +0.0168] | +0 |
| calibrated_stack_isotonic | -0.0002 [-0.0085, +0.0083] | +0.0055 [-0.0043, +0.0170] | +0.0070 [-0.0038, +0.0187] | +0.0038 [-0.0058, +0.0144] | +0.0067 [-0.0043, +0.0193] | -3 |
