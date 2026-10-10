Best single passer (weighted rule): `risk_logistic`. Onsets 26 (warned at some h >= 1).

| row | warned | 2018 (of 4) | 2019 (of 13) | 2020 (of 2) | 2024 (of 2) | 2025 (of 5) |
|---|---|---|---|---|---|---|
| risk_gbm | 13 | 0 | 10 | 0 | 0 | 3 |
| risk_gbm_base | 14 | 0 | 10 | 0 | 0 | 4 |
| risk_logistic | 16 | 0 | 10 | 0 | 1 | 5 |
| risk_logistic_base | 15 | 0 | 10 | 0 | 0 | 5 |
| risk_quantile_skewt_base | 15 | 0 | 10 | 0 | 0 | 5 |
| calibrated_stack_logistic | 15 | 0 | 13 | 0 | 0 | 2 |
| calibrated_stack_isotonic | 12 | 0 | 12 | 0 | 0 | 0 |

Brier gain over `risk_logistic` at +5 bp (mean per day, 90% stationary-bootstrap interval; positive: the stack is better).

| candidate | h=1 | h=2 | h=3 | h=4 | h=5 | onsets warned minus best |
|---|---|---|---|---|---|---|
| calibrated_stack_logistic | +0.0055 [+0.0006, +0.0111] | +0.0059 [+0.0001, +0.0126] | +0.0082 [+0.0015, +0.0159] | +0.0086 [+0.0028, +0.0154] | +0.0096 [+0.0037, +0.0164] | -1 |
| calibrated_stack_isotonic | +0.0013 [-0.0074, +0.0104] | +0.0040 [-0.0056, +0.0150] | +0.0082 [-0.0023, +0.0199] | +0.0058 [-0.0034, +0.0161] | +0.0061 [-0.0047, +0.0186] | -4 |
