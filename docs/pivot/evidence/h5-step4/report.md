# H5 step 4: the best candidate against H2's ceiling (#758), tables

Decision days: 1598 (2019-07-31 to 2025-12-23).
Skill = (mean S(B1) - mean S(forecast)) / mean S(B1), with the 90% interval of the stationary bootstrap (5th to 95th percentile). Headroom = skill(ceiling) - skill(candidate) in points of skill, paired, same resample.

## Grid CRPS (bp): day type: month_end

n = 433 decision days, 2000 draws.

| forecast | mean | skill vs B1 [90%] | skill vs B2 [90%] |
|---|---|---|---|
| B1 | 1.830 | | |
| B2 | 2.523 | | |
| c_two_part_new | 1.573 | +0.140 [-0.040, +0.263] | +0.376 [+0.262, +0.455] |
| ceiling gbm | 1.634 | +0.107 [-0.082, +0.272] | +0.352 [+0.241, +0.458] |
| gbm_funding | 1.693 | +0.075 [-0.007, +0.153] | +0.329 [+0.153, +0.465] |
| reachable gbm | 1.656 | +0.095 [-0.134, +0.251] | +0.343 [+0.249, +0.408] |

| headroom | points of skill [90%] | ceiling or reachable line relative to the candidate [90%] |
|---|---|---|
| c_two_part_new -> ceiling gbm | -0.033 [-0.138, +0.080] | -0.039 [-0.160, +0.091] |
| c_two_part_new -> reachable gbm | -0.045 [-0.120, +0.010] | -0.053 [-0.125, +0.012] |
| gbm_funding -> ceiling gbm | +0.032 [-0.127, +0.180] | +0.035 [-0.135, +0.193] |
| gbm_funding -> reachable gbm | +0.020 [-0.173, +0.148] | +0.022 [-0.183, +0.160] |

## Grid CRPS (bp): day type: ordinary

n = 1598 decision days, 2000 draws.

| forecast | mean | skill vs B1 [90%] | skill vs B2 [90%] |
|---|---|---|---|
| B1 | 1.742 | | |
| B2 | 1.989 | | |
| c_two_part_new | 1.344 | +0.228 [+0.065, +0.376] | +0.324 [+0.244, +0.396] |
| ceiling gbm | 1.440 | +0.173 [+0.012, +0.314] | +0.276 [+0.193, +0.355] |
| gbm_funding | 1.303 | +0.252 [+0.114, +0.390] | +0.345 [+0.267, +0.416] |
| reachable gbm | 1.394 | +0.200 [+0.026, +0.351] | +0.299 [+0.236, +0.361] |

| headroom | points of skill [90%] | ceiling or reachable line relative to the candidate [90%] |
|---|---|---|
| c_two_part_new -> ceiling gbm | -0.055 [-0.119, +0.013] | -0.071 [-0.169, +0.015] |
| c_two_part_new -> reachable gbm | -0.029 [-0.072, +0.014] | -0.037 [-0.096, +0.017] |
| gbm_funding -> ceiling gbm | -0.079 [-0.145, -0.012] | -0.105 [-0.199, -0.015] |
| gbm_funding -> reachable gbm | -0.052 [-0.111, -0.003] | -0.070 [-0.143, -0.004] |

## Grid CRPS (bp): day type: quarter_end

n = 126 decision days, 2000 draws.

| forecast | mean | skill vs B1 [90%] | skill vs B2 [90%] |
|---|---|---|---|
| B1 | 4.401 | | |
| B2 | 5.877 | | |
| c_two_part_new | 3.942 | +0.104 [-0.295, +0.301] | +0.329 [+0.113, +0.510] |
| ceiling gbm | 4.302 | +0.022 [-0.364, +0.246] | +0.268 [-0.008, +0.501] |
| gbm_funding | 5.166 | -0.174 [-0.248, -0.105] | +0.121 [-0.347, +0.505] |
| reachable gbm | 4.616 | -0.049 [-0.407, +0.154] | +0.215 [-0.054, +0.440] |

| headroom | points of skill [90%] | ceiling or reachable line relative to the candidate [90%] |
|---|---|---|
| c_two_part_new -> ceiling gbm | -0.082 [-0.139, +0.015] | -0.092 [-0.163, +0.014] |
| c_two_part_new -> reachable gbm | -0.153 [-0.207, -0.067] | -0.171 [-0.241, -0.060] |
| gbm_funding -> ceiling gbm | +0.196 [-0.131, +0.371] | +0.167 [-0.105, +0.330] |
| gbm_funding -> reachable gbm | +0.125 [-0.198, +0.288] | +0.106 [-0.161, +0.253] |

## Grid CRPS (bp): day type: tax_date

n = 185 decision days, 2000 draws.

| forecast | mean | skill vs B1 [90%] | skill vs B2 [90%] |
|---|---|---|---|
| B1 | 5.224 | | |
| B2 | 7.511 | | |
| c_two_part_new | 5.445 | -0.042 [-0.357, +0.075] | +0.275 [+0.152, +0.628] |
| ceiling gbm | 5.782 | -0.107 [-0.509, -0.013] | +0.230 [+0.105, +0.592] |
| gbm_funding | 5.375 | -0.029 [-0.147, +0.110] | +0.284 [+0.143, +0.686] |
| reachable gbm | 5.594 | -0.071 [-0.392, +0.025] | +0.255 [+0.134, +0.606] |

| headroom | points of skill [90%] | ceiling or reachable line relative to the candidate [90%] |
|---|---|---|
| c_two_part_new -> ceiling gbm | -0.064 [-0.202, -0.019] | -0.062 [-0.182, -0.018] |
| c_two_part_new -> reachable gbm | -0.029 [-0.109, +0.022] | -0.027 [-0.101, +0.018] |
| gbm_funding -> ceiling gbm | -0.078 [-0.397, -0.032] | -0.076 [-0.377, -0.031] |
| gbm_funding -> reachable gbm | -0.042 [-0.304, -0.002] | -0.041 [-0.292, -0.002] |

## Grid CRPS (bp): pooled, all targets

n = 1598 decision days, 10000 draws.

| forecast | mean | skill vs B1 [90%] | skill vs B2 [90%] |
|---|---|---|---|
| B1 | 2.026 | | |
| B2 | 2.348 | | |
| c_two_part_new | 1.608 | +0.206 [+0.066, +0.316] | +0.315 [+0.231, +0.400] |
| ceiling gbm | 1.712 | +0.155 [+0.018, +0.266] | +0.271 [+0.178, +0.367] |
| gbm_funding | 1.605 | +0.208 [+0.097, +0.307] | +0.316 [+0.224, +0.410] |
| reachable gbm | 1.667 | +0.177 [+0.031, +0.292] | +0.290 [+0.214, +0.368] |

| headroom | points of skill [90%] | ceiling or reachable line relative to the candidate [90%] |
|---|---|---|
| c_two_part_new -> ceiling gbm | -0.052 [-0.106, +0.011] | -0.065 [-0.137, +0.013] |
| c_two_part_new -> reachable gbm | -0.030 [-0.067, +0.008] | -0.037 [-0.082, +0.010] |
| gbm_funding -> ceiling gbm | -0.053 [-0.115, +0.006] | -0.067 [-0.141, +0.007] |
| gbm_funding -> reachable gbm | -0.031 [-0.087, +0.014] | -0.039 [-0.104, +0.017] |

## Grid CRPS (bp): pooled, ordinary targets

n = 1598 decision days, 10000 draws.

| forecast | mean | skill vs B1 [90%] | skill vs B2 [90%] |
|---|---|---|---|
| B1 | 1.718 | | |
| B2 | 1.954 | | |
| c_two_part_new | 1.333 | +0.224 [+0.052, +0.380] | +0.318 [+0.234, +0.393] |
| ceiling gbm | 1.430 | +0.168 [+0.003, +0.316] | +0.268 [+0.182, +0.351] |
| gbm_funding | 1.276 | +0.257 [+0.114, +0.400] | +0.347 [+0.267, +0.421] |
| reachable gbm | 1.381 | +0.196 [+0.019, +0.354] | +0.293 [+0.229, +0.353] |

| headroom | points of skill [90%] | ceiling or reachable line relative to the candidate [90%] |
|---|---|---|
| c_two_part_new -> ceiling gbm | -0.057 [-0.123, +0.019] | -0.073 [-0.171, +0.023] |
| c_two_part_new -> reachable gbm | -0.028 [-0.076, +0.021] | -0.036 [-0.097, +0.026] |
| gbm_funding -> ceiling gbm | -0.090 [-0.161, -0.019] | -0.121 [-0.221, -0.024] |
| gbm_funding -> reachable gbm | -0.061 [-0.119, -0.013] | -0.083 [-0.153, -0.017] |

## Grid CRPS (bp): regime: 2018-19

n = 101 decision days, 2000 draws.

| forecast | mean | skill vs B1 [90%] | skill vs B2 [90%] |
|---|---|---|---|
| B1 | 6.673 | | |
| B2 | 2.613 | | |
| c_two_part_new | 2.023 | +0.697 [+0.339, +0.821] | +0.226 [+0.084, +0.375] |
| ceiling gbm | 3.086 | +0.538 [+0.053, +0.711] | -0.181 [-0.511, +0.242] |
| gbm_funding | 2.266 | +0.660 [+0.240, +0.799] | +0.133 [+0.020, +0.233] |
| reachable gbm | 2.638 | +0.605 [+0.070, +0.770] | -0.010 [-0.124, +0.066] |

| headroom | points of skill [90%] | ceiling or reachable line relative to the candidate [90%] |
|---|---|---|
| c_two_part_new -> ceiling gbm | -0.159 [-0.320, -0.054] | -0.526 [-0.792, -0.138] |
| c_two_part_new -> reachable gbm | -0.092 [-0.307, -0.038] | -0.304 [-0.571, -0.138] |
| gbm_funding -> ceiling gbm | -0.123 [-0.272, +0.036] | -0.362 [-0.668, +0.065] |
| gbm_funding -> reachable gbm | -0.056 [-0.182, -0.023] | -0.164 [-0.278, -0.084] |

## Grid CRPS (bp): regime: 2020

n = 251 decision days, 2000 draws.

| forecast | mean | skill vs B1 [90%] | skill vs B2 [90%] |
|---|---|---|---|
| B1 | 1.683 | | |
| B2 | 2.551 | | |
| c_two_part_new | 1.636 | +0.028 [-0.214, +0.196] | +0.359 [+0.151, +0.536] |
| ceiling gbm | 1.376 | +0.182 [+0.031, +0.309] | +0.460 [+0.323, +0.578] |
| gbm_funding | 1.435 | +0.148 [+0.033, +0.258] | +0.438 [+0.262, +0.582] |
| reachable gbm | 1.594 | +0.053 [-0.206, +0.245] | +0.375 [+0.255, +0.496] |

| headroom | points of skill [90%] | ceiling or reachable line relative to the candidate [90%] |
|---|---|---|
| c_two_part_new -> ceiling gbm | +0.154 [+0.028, +0.361] | +0.159 [+0.032, +0.310] |
| c_two_part_new -> reachable gbm | +0.025 [-0.158, +0.234] | +0.025 [-0.174, +0.218] |
| gbm_funding -> ceiling gbm | +0.035 [-0.059, +0.107] | +0.041 [-0.070, +0.125] |
| gbm_funding -> reachable gbm | -0.095 [-0.277, +0.040] | -0.111 [-0.315, +0.047] |

## Grid CRPS (bp): regime: 2021-23

n = 751 decision days, 2000 draws.

| forecast | mean | skill vs B1 [90%] | skill vs B2 [90%] |
|---|---|---|---|
| B1 | 0.707 | | |
| B2 | 1.414 | | |
| c_two_part_new | 0.887 | -0.255 [-0.435, -0.097] | +0.373 [+0.228, +0.500] |
| ceiling gbm | 0.890 | -0.259 [-0.499, -0.058] | +0.371 [+0.201, +0.517] |
| gbm_funding | 0.712 | -0.007 [-0.129, +0.109] | +0.496 [+0.374, +0.605] |
| reachable gbm | 0.928 | -0.312 [-0.517, -0.131] | +0.344 [+0.228, +0.455] |

| headroom | points of skill [90%] | ceiling or reachable line relative to the candidate [90%] |
|---|---|---|
| c_two_part_new -> ceiling gbm | -0.004 [-0.165, +0.165] | -0.003 [-0.131, +0.127] |
| c_two_part_new -> reachable gbm | -0.058 [-0.179, +0.067] | -0.046 [-0.151, +0.051] |
| gbm_funding -> ceiling gbm | -0.252 [-0.465, -0.075] | -0.250 [-0.466, -0.073] |
| gbm_funding -> reachable gbm | -0.305 [-0.451, -0.184] | -0.303 [-0.456, -0.182] |

## Grid CRPS (bp): regime: 2024

n = 250 decision days, 2000 draws.

| forecast | mean | skill vs B1 [90%] | skill vs B2 [90%] |
|---|---|---|---|
| B1 | 1.544 | | |
| B2 | 1.314 | | |
| c_two_part_new | 1.306 | +0.154 [+0.023, +0.254] | +0.006 [-0.108, +0.105] |
| ceiling gbm | 1.125 | +0.271 [+0.147, +0.365] | +0.143 [+0.049, +0.239] |
| gbm_funding | 1.295 | +0.162 [+0.100, +0.225] | +0.015 [-0.117, +0.168] |
| reachable gbm | 1.123 | +0.273 [+0.163, +0.363] | +0.145 [+0.029, +0.263] |

| headroom | points of skill [90%] | ceiling or reachable line relative to the candidate [90%] |
|---|---|---|
| c_two_part_new -> ceiling gbm | +0.117 [+0.072, +0.171] | +0.139 [+0.085, +0.193] |
| c_two_part_new -> reachable gbm | +0.119 [+0.077, +0.180] | +0.140 [+0.093, +0.197] |
| gbm_funding -> ceiling gbm | +0.110 [+0.027, +0.160] | +0.131 [+0.031, +0.200] |
| gbm_funding -> reachable gbm | +0.111 [+0.044, +0.156] | +0.132 [+0.050, +0.194] |

## Grid CRPS (bp): regime: 2025-26

n = 249 decision days, 2000 draws.

| forecast | mean | skill vs B1 [90%] | skill vs B2 [90%] |
|---|---|---|---|
| B1 | 3.042 | | |
| B2 | 3.444 | | |
| c_two_part_new | 2.196 | +0.278 [+0.179, +0.372] | +0.362 [+0.196, +0.472] |
| ceiling gbm | 2.817 | +0.074 [-0.082, +0.218] | +0.182 [+0.097, +0.238] |
| gbm_funding | 2.477 | +0.186 [+0.099, +0.265] | +0.281 [+0.078, +0.414] |
| reachable gbm | 2.356 | +0.226 [+0.087, +0.350] | +0.316 [+0.180, +0.409] |

| headroom | points of skill [90%] | ceiling or reachable line relative to the candidate [90%] |
|---|---|---|
| c_two_part_new -> ceiling gbm | -0.204 [-0.337, -0.075] | -0.283 [-0.474, -0.098] |
| c_two_part_new -> reachable gbm | -0.052 [-0.127, +0.016] | -0.073 [-0.173, +0.022] |
| gbm_funding -> ceiling gbm | -0.112 [-0.256, +0.031] | -0.137 [-0.316, +0.037] |
| gbm_funding -> reachable gbm | +0.040 [-0.049, +0.123] | +0.049 [-0.058, +0.154] |

## Grid CRPS (bp): regime: 2027

n = 0: fewer than 30 decision days

## Upper-tail twCRPS, weight 1{y > 0 bp}: pooled, all targets

n = 1598 decision days, 2000 draws.

| forecast | mean | skill vs B1 [90%] | skill vs B2 [90%] |
|---|---|---|---|
| B1 | 1.060 | | |
| B2 | 0.866 | | |
| c_two_part_new | 0.617 | +0.418 [+0.272, +0.537] | +0.287 [+0.162, +0.460] |
| ceiling gbm | 0.704 | +0.336 [+0.176, +0.462] | +0.187 [+0.047, +0.387] |
| gbm_funding | 0.677 | +0.362 [+0.201, +0.486] | +0.218 [+0.093, +0.392] |
| reachable gbm | 0.678 | +0.360 [+0.185, +0.488] | +0.217 [+0.101, +0.371] |

| headroom | points of skill [90%] | ceiling or reachable line relative to the candidate [90%] |
|---|---|---|
| c_two_part_new -> ceiling gbm | -0.082 [-0.133, -0.040] | -0.141 [-0.227, -0.069] |
| c_two_part_new -> reachable gbm | -0.058 [-0.116, -0.033] | -0.099 [-0.187, -0.059] |
| gbm_funding -> ceiling gbm | -0.026 [-0.067, +0.030] | -0.040 [-0.105, +0.044] |
| gbm_funding -> reachable gbm | -0.001 [-0.051, +0.039] | -0.002 [-0.076, +0.058] |

## Upper-tail twCRPS, weight 1{y > 0 bp}: pooled, ordinary targets

n = 1598 decision days, 2000 draws.

| forecast | mean | skill vs B1 [90%] | skill vs B2 [90%] |
|---|---|---|---|
| B1 | 0.778 | | |
| B2 | 0.512 | | |
| c_two_part_new | 0.343 | +0.559 [+0.347, +0.698] | +0.330 [+0.222, +0.437] |
| ceiling gbm | 0.421 | +0.459 [+0.232, +0.611] | +0.177 [+0.006, +0.348] |
| gbm_funding | 0.376 | +0.516 [+0.291, +0.665] | +0.265 [+0.139, +0.383] |
| reachable gbm | 0.398 | +0.489 [+0.242, +0.644] | +0.223 [+0.129, +0.308] |

| headroom | points of skill [90%] | ceiling or reachable line relative to the candidate [90%] |
|---|---|---|
| c_two_part_new -> ceiling gbm | -0.100 [-0.154, -0.037] | -0.227 [-0.385, -0.070] |
| c_two_part_new -> reachable gbm | -0.070 [-0.140, -0.031] | -0.158 [-0.293, -0.067] |
| gbm_funding -> ceiling gbm | -0.058 [-0.120, +0.027] | -0.119 [-0.278, +0.044] |
| gbm_funding -> reachable gbm | -0.027 [-0.083, +0.016] | -0.056 [-0.160, +0.028] |

Reading on gbm_funding: **continue model work**; headroom shown in: regime: 2024.

