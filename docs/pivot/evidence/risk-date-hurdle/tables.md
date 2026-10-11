**Tier 1 per lead** (flat rule, +5 bp): onsets flagged at that lead alone of 26 / false alarms per onset.

| model | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|
| risk_gbm | 13 / 1.30 | 8 / 1.08 | 7 / 1.04 | 7 / 0.88 | 7 / 1.04 |
| risk_gbm+hurdle_platt | 12 / 1.44 | 7 / 3.04 | 10 / 2.58 | 9 / 2.38 | 8 / 3.08 |
| risk_gbm+hurdle_isotonic | 13 / 1.48 | 6 / 2.62 | 9 / 2.50 | 8 / 1.96 | 7 / 2.19 |
| risk_gbm+hurdle_state_platt | 13 / 2.04 | 8 / 3.04 | 10 / 3.54 | 9 / 2.73 | 9 / 3.12 |
| risk_gbm+hurdle_state_isotonic | 14 / 2.15 | 6 / 1.92 | 9 / 2.46 | 9 / 2.00 | 7 / 2.27 |
| risk_logistic_base | 13 / 1.70 | 6 / 1.00 | 6 / 1.00 | 7 / 1.12 | 8 / 1.15 |
| risk_logistic_base+hurdle_platt | 5 / 1.44 | 6 / 1.73 | 7 / 1.73 | 7 / 1.85 | 7 / 2.85 |
| risk_logistic_base+hurdle_isotonic | 5 / 0.96 | 4 / 1.35 | 5 / 1.88 | 4 / 1.65 | 5 / 2.00 |
| risk_logistic_base+hurdle_state_platt | 7 / 2.56 | 4 / 1.65 | 7 / 2.85 | 6 / 1.77 | 8 / 2.96 |
| risk_logistic_base+hurdle_state_isotonic | 8 / 2.37 | 4 / 1.19 | 5 / 1.92 | 4 / 1.69 | 7 / 2.38 |

**Recall by year** (onsets flagged at some lead 1 to 5 / onsets in the year, flat rule).

| model | all | 2018 (4) | 2019 (13) | 2020 (2) | 2024 (2) | 2025 (5) |
|---|---|---|---|---|---|---|
| risk_gbm | 13 | 0 | 10 | 0 | 0 | 3 |
| risk_gbm+hurdle_platt | 15 | 0 | 13 | 0 | 0 | 2 |
| risk_gbm+hurdle_isotonic | 15 | 0 | 13 | 0 | 0 | 2 |
| risk_gbm+hurdle_state_platt | 15 | 0 | 13 | 0 | 0 | 2 |
| risk_gbm+hurdle_state_isotonic | 15 | 0 | 13 | 0 | 0 | 2 |
| risk_gbm_base | 14 | 0 | 10 | 0 | 0 | 4 |
| risk_gbm_base+hurdle_platt | 15 | 0 | 13 | 0 | 0 | 2 |
| risk_gbm_base+hurdle_isotonic | 15 | 0 | 13 | 0 | 0 | 2 |
| risk_gbm_base+hurdle_state_platt | 15 | 0 | 13 | 0 | 0 | 2 |
| risk_gbm_base+hurdle_state_isotonic | 13 | 0 | 11 | 0 | 0 | 2 |
| risk_logistic | 14 | 0 | 10 | 0 | 0 | 4 |
| risk_logistic+hurdle_platt | 13 | 0 | 11 | 0 | 0 | 2 |
| risk_logistic+hurdle_isotonic | 13 | 0 | 11 | 0 | 0 | 2 |
| risk_logistic+hurdle_state_platt | 14 | 0 | 12 | 0 | 0 | 2 |
| risk_logistic+hurdle_state_isotonic | 12 | 0 | 11 | 0 | 0 | 1 |
| risk_logistic_base | 13 | 0 | 10 | 0 | 0 | 3 |
| risk_logistic_base+hurdle_platt | 11 | 0 | 9 | 0 | 0 | 2 |
| risk_logistic_base+hurdle_isotonic | 8 | 0 | 8 | 0 | 0 | 0 |
| risk_logistic_base+hurdle_state_platt | 13 | 0 | 12 | 0 | 0 | 1 |
| risk_logistic_base+hurdle_state_isotonic | 11 | 0 | 11 | 0 | 0 | 0 |
| risk_quantile_skewt_base | 14 | 0 | 10 | 0 | 0 | 4 |
| risk_quantile_skewt_base+hurdle_platt | 13 | 0 | 12 | 0 | 0 | 1 |
| risk_quantile_skewt_base+hurdle_isotonic | 12 | 0 | 12 | 0 | 0 | 0 |
| risk_quantile_skewt_base+hurdle_state_platt | 13 | 0 | 12 | 0 | 0 | 1 |
| risk_quantile_skewt_base+hurdle_state_isotonic | 12 | 0 | 12 | 0 | 0 | 0 |

**Predicted against realised pressure rate (+5 bp), h = 1, by regime** (mean forecast / realised frequency over the regime's scored days).

| model | all | 2018-19 | 2020 | 2021-23 | 2024 | 2025-26 |
|---|---|---|---|---|---|---|
| risk_gbm | 0.027 / 0.075 | 0.096 / 0.272 | 0.015 / 0.016 | 0.001 / 0.000 | 0.003 / 0.020 | 0.039 / 0.116 |
| risk_gbm+hurdle_platt | 0.108 / 0.075 | 0.283 / 0.272 | 0.200 / 0.016 | 0.036 / 0.000 | 0.012 / 0.020 | 0.067 / 0.116 |
| risk_gbm+hurdle_isotonic | 0.105 / 0.075 | 0.312 / 0.272 | 0.192 / 0.016 | 0.016 / 0.000 | 0.007 / 0.020 | 0.068 / 0.116 |
| risk_gbm+hurdle_state_platt | 0.093 / 0.075 | 0.280 / 0.272 | 0.165 / 0.016 | 0.014 / 0.000 | 0.004 / 0.020 | 0.068 / 0.116 |
| risk_gbm+hurdle_state_isotonic | 0.095 / 0.075 | 0.314 / 0.272 | 0.142 / 0.016 | 0.009 / 0.000 | 0.003 / 0.020 | 0.070 / 0.116 |
| risk_gbm_base | 0.028 / 0.075 | 0.097 / 0.272 | 0.025 / 0.016 | 0.000 / 0.000 | 0.002 / 0.020 | 0.035 / 0.116 |
| risk_gbm_base+hurdle_platt | 0.109 / 0.075 | 0.284 / 0.272 | 0.211 / 0.016 | 0.036 / 0.000 | 0.011 / 0.020 | 0.064 / 0.116 |
| risk_gbm_base+hurdle_isotonic | 0.106 / 0.075 | 0.313 / 0.272 | 0.203 / 0.016 | 0.016 / 0.000 | 0.006 / 0.020 | 0.065 / 0.116 |
| risk_gbm_base+hurdle_state_platt | 0.094 / 0.075 | 0.281 / 0.272 | 0.175 / 0.016 | 0.014 / 0.000 | 0.003 / 0.020 | 0.065 / 0.116 |
| risk_gbm_base+hurdle_state_isotonic | 0.096 / 0.075 | 0.316 / 0.272 | 0.152 / 0.016 | 0.009 / 0.000 | 0.003 / 0.020 | 0.067 / 0.116 |
| risk_logistic | 0.031 / 0.075 | 0.107 / 0.272 | 0.031 / 0.016 | 0.000 / 0.000 | 0.006 / 0.020 | 0.033 / 0.116 |
| risk_logistic+hurdle_platt | 0.112 / 0.075 | 0.294 / 0.272 | 0.216 / 0.016 | 0.036 / 0.000 | 0.015 / 0.020 | 0.062 / 0.116 |
| risk_logistic+hurdle_isotonic | 0.109 / 0.075 | 0.323 / 0.272 | 0.208 / 0.016 | 0.016 / 0.000 | 0.010 / 0.020 | 0.063 / 0.116 |
| risk_logistic+hurdle_state_platt | 0.097 / 0.075 | 0.291 / 0.272 | 0.181 / 0.016 | 0.014 / 0.000 | 0.007 / 0.020 | 0.063 / 0.116 |
| risk_logistic+hurdle_state_isotonic | 0.100 / 0.075 | 0.326 / 0.272 | 0.158 / 0.016 | 0.009 / 0.000 | 0.007 / 0.020 | 0.065 / 0.116 |
| risk_logistic_base | 0.030 / 0.075 | 0.108 / 0.272 | 0.029 / 0.016 | 0.000 / 0.000 | 0.003 / 0.020 | 0.031 / 0.116 |
| risk_logistic_base+hurdle_platt | 0.112 / 0.075 | 0.295 / 0.272 | 0.215 / 0.016 | 0.036 / 0.000 | 0.012 / 0.020 | 0.060 / 0.116 |
| risk_logistic_base+hurdle_isotonic | 0.108 / 0.075 | 0.324 / 0.272 | 0.207 / 0.016 | 0.016 / 0.000 | 0.007 / 0.020 | 0.061 / 0.116 |
| risk_logistic_base+hurdle_state_platt | 0.097 / 0.075 | 0.292 / 0.272 | 0.179 / 0.016 | 0.014 / 0.000 | 0.004 / 0.020 | 0.060 / 0.116 |
| risk_logistic_base+hurdle_state_isotonic | 0.099 / 0.075 | 0.326 / 0.272 | 0.156 / 0.016 | 0.009 / 0.000 | 0.003 / 0.020 | 0.063 / 0.116 |
| risk_quantile_skewt_base | 0.040 / 0.075 | 0.120 / 0.272 | 0.047 / 0.016 | 0.003 / 0.000 | 0.012 / 0.020 | 0.051 / 0.116 |
| risk_quantile_skewt_base+hurdle_platt | 0.121 / 0.075 | 0.307 / 0.272 | 0.232 / 0.016 | 0.039 / 0.000 | 0.021 / 0.020 | 0.079 / 0.116 |
| risk_quantile_skewt_base+hurdle_isotonic | 0.118 / 0.075 | 0.336 / 0.272 | 0.224 / 0.016 | 0.018 / 0.000 | 0.016 / 0.020 | 0.081 / 0.116 |
| risk_quantile_skewt_base+hurdle_state_platt | 0.106 / 0.075 | 0.304 / 0.272 | 0.197 / 0.016 | 0.016 / 0.000 | 0.013 / 0.020 | 0.080 / 0.116 |
| risk_quantile_skewt_base+hurdle_state_isotonic | 0.108 / 0.075 | 0.338 / 0.272 | 0.174 / 0.016 | 0.012 / 0.000 | 0.013 / 0.020 | 0.083 / 0.116 |

**Brier score and log loss the parent loses to the variant** (positive favours the variant; +5 bp, all scored days, 90% interval).

| model | h | Brier vs parent | log loss vs parent |
|---|---|---|---|
| risk_gbm+hurdle_platt | 1 | +0.0016 [-0.0072, +0.0110] | +0.447 [+0.236, +0.685] |
| risk_gbm+hurdle_platt | 5 | -0.0032 [-0.0121, +0.0061] | +0.525 [+0.285, +0.803] |
| risk_gbm+hurdle_isotonic | 1 | -0.0029 [-0.0138, +0.0079] | +0.389 [+0.186, +0.624] |
| risk_gbm+hurdle_isotonic | 5 | -0.0032 [-0.0120, +0.0057] | +0.509 [+0.280, +0.764] |
| risk_gbm+hurdle_state_platt | 1 | +0.0042 [-0.0044, +0.0147] | +0.465 [+0.260, +0.717] |
| risk_gbm+hurdle_state_platt | 5 | +0.0003 [-0.0080, +0.0101] | +0.547 [+0.306, +0.825] |
| risk_gbm+hurdle_state_isotonic | 1 | -0.0023 [-0.0137, +0.0087] | +0.364 [+0.171, +0.594] |
| risk_gbm+hurdle_state_isotonic | 5 | -0.0039 [-0.0142, +0.0058] | +0.443 [+0.209, +0.696] |
| risk_gbm_base+hurdle_platt | 1 | +0.0016 [-0.0069, +0.0114] | +0.447 [+0.236, +0.691] |
| risk_gbm_base+hurdle_platt | 5 | -0.0032 [-0.0118, +0.0065] | +0.525 [+0.279, +0.805] |
| risk_gbm_base+hurdle_isotonic | 1 | -0.0029 [-0.0133, +0.0080] | +0.389 [+0.189, +0.627] |
| risk_gbm_base+hurdle_isotonic | 5 | -0.0032 [-0.0120, +0.0063] | +0.509 [+0.275, +0.785] |
| risk_gbm_base+hurdle_state_platt | 1 | +0.0042 [-0.0043, +0.0139] | +0.465 [+0.253, +0.692] |
| risk_gbm_base+hurdle_state_platt | 5 | +0.0003 [-0.0087, +0.0101] | +0.547 [+0.314, +0.815] |
| risk_gbm_base+hurdle_state_isotonic | 1 | -0.0023 [-0.0135, +0.0094] | +0.364 [+0.164, +0.590] |
| risk_gbm_base+hurdle_state_isotonic | 5 | -0.0039 [-0.0145, +0.0063] | +0.443 [+0.208, +0.707] |
| risk_logistic+hurdle_platt | 1 | +0.0016 [-0.0073, +0.0114] | +0.447 [+0.235, +0.692] |
| risk_logistic+hurdle_platt | 5 | -0.0032 [-0.0117, +0.0066] | +0.525 [+0.298, +0.820] |
| risk_logistic+hurdle_isotonic | 1 | -0.0029 [-0.0128, +0.0080] | +0.389 [+0.186, +0.635] |
| risk_logistic+hurdle_isotonic | 5 | -0.0032 [-0.0119, +0.0063] | +0.509 [+0.281, +0.791] |
| risk_logistic+hurdle_state_platt | 1 | +0.0042 [-0.0045, +0.0143] | +0.465 [+0.251, +0.699] |
| risk_logistic+hurdle_state_platt | 5 | +0.0003 [-0.0085, +0.0101] | +0.547 [+0.303, +0.823] |
| risk_logistic+hurdle_state_isotonic | 1 | -0.0023 [-0.0141, +0.0090] | +0.364 [+0.159, +0.591] |
| risk_logistic+hurdle_state_isotonic | 5 | -0.0039 [-0.0140, +0.0064] | +0.443 [+0.215, +0.699] |
| risk_logistic_base+hurdle_platt | 1 | +0.0016 [-0.0069, +0.0111] | +0.447 [+0.234, +0.702] |
| risk_logistic_base+hurdle_platt | 5 | -0.0032 [-0.0119, +0.0061] | +0.525 [+0.293, +0.815] |
| risk_logistic_base+hurdle_isotonic | 1 | -0.0029 [-0.0136, +0.0080] | +0.389 [+0.191, +0.612] |
| risk_logistic_base+hurdle_isotonic | 5 | -0.0032 [-0.0118, +0.0063] | +0.509 [+0.280, +0.775] |
| risk_logistic_base+hurdle_state_platt | 1 | +0.0042 [-0.0047, +0.0142] | +0.465 [+0.249, +0.707] |
| risk_logistic_base+hurdle_state_platt | 5 | +0.0003 [-0.0083, +0.0101] | +0.547 [+0.307, +0.816] |
| risk_logistic_base+hurdle_state_isotonic | 1 | -0.0023 [-0.0139, +0.0091] | +0.364 [+0.165, +0.588] |
| risk_logistic_base+hurdle_state_isotonic | 5 | -0.0039 [-0.0139, +0.0061] | +0.443 [+0.214, +0.700] |
| risk_quantile_skewt_base+hurdle_platt | 1 | +0.0016 [-0.0071, +0.0109] | +0.447 [+0.233, +0.681] |
| risk_quantile_skewt_base+hurdle_platt | 5 | -0.0032 [-0.0124, +0.0062] | +0.525 [+0.275, +0.807] |
| risk_quantile_skewt_base+hurdle_isotonic | 1 | -0.0029 [-0.0133, +0.0076] | +0.389 [+0.189, +0.623] |
| risk_quantile_skewt_base+hurdle_isotonic | 5 | -0.0032 [-0.0120, +0.0062] | +0.509 [+0.274, +0.759] |
| risk_quantile_skewt_base+hurdle_state_platt | 1 | +0.0042 [-0.0049, +0.0145] | +0.465 [+0.250, +0.700] |
| risk_quantile_skewt_base+hurdle_state_platt | 5 | +0.0003 [-0.0088, +0.0099] | +0.547 [+0.300, +0.802] |
| risk_quantile_skewt_base+hurdle_state_isotonic | 1 | -0.0023 [-0.0142, +0.0093] | +0.364 [+0.150, +0.610] |
| risk_quantile_skewt_base+hurdle_state_isotonic | 5 | -0.0039 [-0.0138, +0.0060] | +0.443 [+0.201, +0.698] |
