# The drivers audit read on ruling 1's bound (#1017, H5 and H2)

**Development data, not a verdict.** No re-scoring: every figure is read from `docs/research/drivers-audit-951/score.json`. The original page (`drivers-audit-951-result.md`) stands as published; whether any reading of 15 October is reopened is Eleonora's question, marked at the end.

Ruling 1 of `docs/decisions/scoring-protocol.md` reads the studentized one-sided 95% lower bound on mean d = S(first) - S(second) of the grid CRPS (positive favours the second arm). The original page read the percentile 5th-95th interval of the skill. `gain` below means the interval lies above zero (percentile) or the bound is above zero (studentized). The one-sided bound cannot confirm a harm, so a row the percentile reading shows as `harm` reads `not seen` here and is listed as a change.

## 1. Rows whose side changes

### 1a. A gain on one reading and not on the other

8 rows.

| cut | first -> second | mean d | skill [90% percentile] | lower bound (studentized, one-sided) | percentile reading | studentized reading |
|---|---|---|---|---|---|---|
| day type: calendar days | gbm_funding -> direct_cal_leaf5 | +0.248 | +0.068 [+0.002, +0.141] | -0.015 | gain | not seen |
| day type: month_end | B1 -> direct_cal_leaf20 | +0.303 | +0.136 [+0.020, +0.243] | -0.009 | gain | not seen |
| day type: month_end | gbm_funding -> direct_cal_leaf20 | +0.233 | +0.108 [+0.010, +0.192] | -0.006 | gain | not seen |
| day type: ordinary | B1 -> direct_base_leaf5 | +0.287 | +0.144 [-0.005, +0.278] | +0.019 | not seen | gain |
| day type: tax_date | direct_base_leaf20 -> direct_cal_leaf20 | +0.135 | +0.024 [-0.001, +0.090] | +0.004 | not seen | gain |
| pooled: all | B1 -> direct_base_leaf5 | +0.279 | +0.121 [-0.001, +0.222] | +0.030 | not seen | gain |
| regime: 2024 | B1 -> direct_base_leaf5 | +0.321 | +0.191 [-0.015, +0.302] | +0.006 | not seen | gain |
| regime: 2025-26 | B2 -> gbm_funding | +0.982 | +0.264 [+0.056, +0.392] | -0.046 | gain | not seen |

### 1b. A harm on the percentile reading, which the one-sided bound cannot confirm

40 rows.

| cut | first -> second | mean d | skill [90% percentile] | lower bound (studentized, one-sided) | percentile reading | studentized reading |
|---|---|---|---|---|---|---|
| day type: calendar days | B1 -> direct_base_leaf5 | -0.279 | -0.079 [-0.147, -0.017] | -0.581 | harm | not seen |
| day type: calendar days | direct_base_leaf20 -> direct_base_leaf5 | -0.098 | -0.026 [-0.050, -0.010] | -0.174 | harm | not seen |
| day type: month_end | direct_base_leaf20 -> direct_base_leaf5 | -0.110 | -0.053 [-0.089, -0.017] | -0.207 | harm | not seen |
| day type: ordinary | direct_base_leaf20 -> direct_base_leaf5 | -0.096 | -0.060 [-0.089, -0.034] | -0.150 | harm | not seen |
| day type: ordinary | direct_cal_leaf20 -> direct_cal_leaf5 | -0.061 | -0.040 [-0.068, -0.013] | -0.115 | harm | not seen |
| day type: ordinary | gbm_funding -> direct_base_leaf20 | -0.115 | -0.077 [-0.130, -0.029] | -0.199 | harm | not seen |
| day type: ordinary | gbm_funding -> direct_base_leaf5 | -0.212 | -0.142 [-0.204, -0.085] | -0.313 | harm | not seen |
| day type: ordinary | gbm_funding -> direct_cal_leaf5 | -0.089 | -0.060 [-0.124, -0.003] | -0.191 | harm | not seen |
| day type: quarter_end | B1 -> direct_base_leaf20 | -0.885 | -0.131 [-0.277, -0.049] | -2.178 | harm | not seen |
| day type: quarter_end | B1 -> direct_base_leaf5 | -1.095 | -0.162 [-0.337, -0.076] | -2.259 | harm | not seen |
| day type: quarter_end | B1 -> gbm_funding | -0.894 | -0.133 [-0.212, -0.083] | -2.218 | harm | not seen |
| day type: quarter_end | direct_base_leaf20 -> direct_base_leaf5 | -0.210 | -0.027 [-0.067, -0.009] | -0.356 | harm | not seen |
| day type: tax_date | B1 -> direct_base_leaf20 | -0.613 | -0.125 [-0.345, -0.049] | -1.480 | harm | not seen |
| day type: tax_date | B1 -> direct_base_leaf5 | -0.671 | -0.136 [-0.391, -0.058] | -1.615 | harm | not seen |
| day type: tax_date | gbm_funding -> direct_base_leaf20 | -0.336 | -0.065 [-0.195, -0.032] | -0.821 | harm | not seen |
| day type: tax_date | gbm_funding -> direct_base_leaf5 | -0.394 | -0.076 [-0.213, -0.043] | -0.859 | harm | not seen |
| day type: tax_date | gbm_funding -> direct_cal_leaf20 | -0.200 | -0.039 [-0.123, -0.009] | -0.439 | harm | not seen |
| day type: tax_date | gbm_funding -> direct_cal_leaf5 | -0.216 | -0.042 [-0.137, -0.012] | -0.466 | harm | not seen |
| day type: tax_date | gbm_funding -> onestep_cal_leaf20 | -0.043 | -0.008 [-0.026, -0.002] | -0.094 | harm | not seen |
| day type: tax_date | onestep_cal_leaf20 -> direct_cal_leaf20 | -0.158 | -0.030 [-0.106, -0.001] | -0.373 | harm | not seen |
| pooled: all | direct_base_leaf20 -> direct_base_leaf5 | -0.098 | -0.051 [-0.074, -0.029] | -0.149 | harm | not seen |
| pooled: all | direct_cal_leaf20 -> direct_cal_leaf5 | -0.047 | -0.026 [-0.050, -0.004] | -0.095 | harm | not seen |
| pooled: all | gbm_funding -> direct_base_leaf20 | -0.099 | -0.054 [-0.098, -0.015] | -0.184 | harm | not seen |
| pooled: all | gbm_funding -> direct_base_leaf5 | -0.197 | -0.108 [-0.159, -0.063] | -0.295 | harm | not seen |
| regime: 2018-19 | direct_base_leaf20 -> direct_base_leaf5 | -0.269 | -0.064 [-0.115, -0.029] | -0.444 | harm | not seen |
| regime: 2018-19 | gbm_funding -> direct_base_leaf20 | -0.198 | -0.049 [-0.102, -0.012] | -0.378 | harm | not seen |
| regime: 2018-19 | gbm_funding -> direct_base_leaf5 | -0.466 | -0.117 [-0.200, -0.064] | -0.698 | harm | not seen |
| regime: 2018-19 | onestep_cal_leaf20 -> direct_cal_leaf20 | -0.177 | -0.046 [-0.104, -0.010] | -0.352 | harm | not seen |
| regime: 2021-23 | B1 -> direct_base_leaf20 | -0.148 | -0.208 [-0.365, -0.062] | -0.304 | harm | not seen |
| regime: 2021-23 | B1 -> direct_base_leaf5 | -0.207 | -0.291 [-0.476, -0.132] | -0.386 | harm | not seen |
| regime: 2021-23 | B1 -> direct_cal_leaf20 | -0.141 | -0.199 [-0.360, -0.052] | -0.305 | harm | not seen |
| regime: 2021-23 | B1 -> direct_cal_leaf5 | -0.202 | -0.285 [-0.478, -0.115] | -0.391 | harm | not seen |
| regime: 2021-23 | direct_base_leaf20 -> direct_base_leaf5 | -0.059 | -0.069 [-0.128, -0.011] | -0.114 | harm | not seen |
| regime: 2021-23 | direct_cal_leaf20 -> direct_cal_leaf5 | -0.061 | -0.072 [-0.135, -0.015] | -0.125 | harm | not seen |
| regime: 2021-23 | gbm_funding -> direct_base_leaf20 | -0.141 | -0.197 [-0.278, -0.134] | -0.208 | harm | not seen |
| regime: 2021-23 | gbm_funding -> direct_base_leaf5 | -0.201 | -0.280 [-0.396, -0.192] | -0.292 | harm | not seen |
| regime: 2021-23 | gbm_funding -> direct_cal_leaf20 | -0.135 | -0.188 [-0.269, -0.122] | -0.203 | harm | not seen |
| regime: 2021-23 | gbm_funding -> direct_cal_leaf5 | -0.196 | -0.273 [-0.394, -0.180] | -0.294 | harm | not seen |
| regime: 2021-23 | onestep_cal_leaf20 -> direct_cal_leaf20 | -0.126 | -0.174 [-0.253, -0.111] | -0.189 | harm | not seen |
| regime: 2024 | direct_base_leaf20 -> direct_base_leaf5 | -0.085 | -0.066 [-0.157, -0.009] | -0.244 | harm | not seen |

## 2. Every row, both readings

### day type: calendar days

n = 750 decision days.

| first -> second | mean d | skill [90% percentile] | lower bound (studentized, one-sided) | percentile | studentized |
|---|---|---|---|---|---|
| B1 -> direct_base_leaf20 | -0.181 | -0.051 [-0.108, +0.008] | -0.443 | not seen | not seen |
| B1 -> direct_base_leaf5 | -0.279 | -0.079 [-0.147, -0.017] | -0.581 | harm | not seen |
| B1 -> direct_cal_leaf20 | +0.055 | +0.016 [-0.053, +0.100] | -0.222 | not seen | not seen |
| B1 -> direct_cal_leaf5 | +0.117 | +0.033 [-0.047, +0.124] | -0.185 | not seen | not seen |
| B1 -> gbm_funding | -0.131 | -0.037 [-0.071, +0.001] | -0.318 | not seen | not seen |
| B1 -> onestep_cal_leaf20 | +0.095 | +0.027 [-0.017, +0.090] | -0.097 | not seen | not seen |
| B2 -> direct_base_leaf20 | +0.938 | +0.202 [+0.077, +0.362] | +0.341 | gain | gain |
| B2 -> direct_base_leaf5 | +0.840 | +0.181 [+0.058, +0.340] | +0.235 | gain | gain |
| B2 -> direct_cal_leaf20 | +1.174 | +0.252 [+0.129, +0.410] | +0.635 | gain | gain |
| B2 -> direct_cal_leaf5 | +1.236 | +0.266 [+0.151, +0.416] | +0.746 | gain | gain |
| B2 -> gbm_funding | +0.988 | +0.213 [+0.080, +0.381] | +0.345 | gain | gain |
| B2 -> onestep_cal_leaf20 | +1.214 | +0.261 [+0.133, +0.425] | +0.632 | gain | gain |
| direct_base_leaf20 -> direct_base_leaf5 | -0.098 | -0.026 [-0.050, -0.010] | -0.174 | harm | not seen |
| direct_base_leaf20 -> direct_cal_leaf20 | +0.236 | +0.064 [+0.033, +0.110] | +0.102 | gain | gain |
| direct_base_leaf5 -> direct_cal_leaf5 | +0.396 | +0.104 [+0.061, +0.160] | +0.186 | gain | gain |
| direct_cal_leaf20 -> direct_cal_leaf5 | +0.062 | +0.018 [-0.016, +0.048] | -0.046 | not seen | not seen |
| gbm_funding -> direct_base_leaf20 | -0.050 | -0.014 [-0.056, +0.025] | -0.199 | not seen | not seen |
| gbm_funding -> direct_base_leaf5 | -0.149 | -0.041 [-0.093, +0.001] | -0.323 | not seen | not seen |
| gbm_funding -> direct_cal_leaf20 | +0.185 | +0.051 [-0.000, +0.114] | -0.014 | not seen | not seen |
| gbm_funding -> direct_cal_leaf5 | +0.248 | +0.068 [+0.002, +0.141] | -0.015 | gain | not seen |
| gbm_funding -> onestep_cal_leaf20 | +0.226 | +0.062 [+0.032, +0.107] | +0.106 | gain | gain |
| onestep_cal_leaf20 -> direct_cal_leaf20 | -0.041 | -0.012 [-0.054, +0.025] | -0.168 | not seen | not seen |

### day type: coupon settlement

n = 1012 decision days.

| first -> second | mean d | skill [90% percentile] | lower bound (studentized, one-sided) | percentile | studentized |
|---|---|---|---|---|---|
| B1 -> direct_base_leaf20 | -0.139 | -0.049 [-0.126, +0.024] | -0.382 | not seen | not seen |
| B1 -> direct_base_leaf5 | -0.200 | -0.070 [-0.157, +0.011] | -0.464 | not seen | not seen |
| B1 -> direct_cal_leaf20 | +0.170 | +0.060 [-0.021, +0.135] | -0.080 | not seen | not seen |
| B1 -> direct_cal_leaf5 | +0.233 | +0.082 [-0.016, +0.167] | -0.076 | not seen | not seen |
| B1 -> gbm_funding | -0.123 | -0.043 [-0.089, +0.001] | -0.279 | not seen | not seen |
| B1 -> onestep_cal_leaf20 | +0.139 | +0.049 [-0.002, +0.096] | -0.021 | not seen | not seen |
| B2 -> direct_base_leaf20 | +0.852 | +0.222 [+0.127, +0.316] | +0.461 | gain | gain |
| B2 -> direct_base_leaf5 | +0.791 | +0.206 [+0.114, +0.300] | +0.395 | gain | gain |
| B2 -> direct_cal_leaf20 | +1.161 | +0.303 [+0.219, +0.385] | +0.783 | gain | gain |
| B2 -> direct_cal_leaf5 | +1.223 | +0.319 [+0.247, +0.388] | +0.858 | gain | gain |
| B2 -> gbm_funding | +0.868 | +0.226 [+0.125, +0.328] | +0.429 | gain | gain |
| B2 -> onestep_cal_leaf20 | +1.129 | +0.295 [+0.203, +0.381] | +0.720 | gain | gain |
| direct_base_leaf20 -> direct_base_leaf5 | -0.061 | -0.021 [-0.046, +0.003] | -0.141 | not seen | not seen |
| direct_base_leaf20 -> direct_cal_leaf20 | +0.309 | +0.104 [+0.072, +0.135] | +0.182 | gain | gain |
| direct_base_leaf5 -> direct_cal_leaf5 | +0.433 | +0.142 [+0.096, +0.183] | +0.240 | gain | gain |
| direct_cal_leaf20 -> direct_cal_leaf5 | +0.062 | +0.023 [-0.017, +0.060] | -0.047 | not seen | not seen |
| gbm_funding -> direct_base_leaf20 | -0.016 | -0.005 [-0.048, +0.035] | -0.148 | not seen | not seen |
| gbm_funding -> direct_base_leaf5 | -0.077 | -0.026 [-0.079, +0.023] | -0.231 | not seen | not seen |
| gbm_funding -> direct_cal_leaf20 | +0.293 | +0.099 [+0.048, +0.148] | +0.112 | gain | gain |
| gbm_funding -> direct_cal_leaf5 | +0.355 | +0.120 [+0.053, +0.181] | +0.111 | gain | gain |
| gbm_funding -> onestep_cal_leaf20 | +0.261 | +0.088 [+0.065, +0.113] | +0.162 | gain | gain |
| onestep_cal_leaf20 -> direct_cal_leaf20 | +0.032 | +0.012 [-0.032, +0.053] | -0.092 | not seen | not seen |

### day type: month_end

n = 507 decision days.

| first -> second | mean d | skill [90% percentile] | lower bound (studentized, one-sided) | percentile | studentized |
|---|---|---|---|---|---|
| B1 -> direct_base_leaf20 | +0.157 | +0.071 [-0.040, +0.175] | -0.112 | not seen | not seen |
| B1 -> direct_base_leaf5 | +0.047 | +0.021 [-0.109, +0.143] | -0.265 | not seen | not seen |
| B1 -> direct_cal_leaf20 | +0.303 | +0.136 [+0.020, +0.243] | -0.009 | gain | not seen |
| B1 -> direct_cal_leaf5 | +0.410 | +0.185 [+0.055, +0.297] | +0.064 | gain | gain |
| B1 -> gbm_funding | +0.070 | +0.032 [-0.034, +0.104] | -0.091 | not seen | not seen |
| B1 -> onestep_cal_leaf20 | +0.308 | +0.139 [+0.064, +0.204] | +0.095 | gain | gain |
| B2 -> direct_base_leaf20 | +0.812 | +0.283 [+0.192, +0.376] | +0.445 | gain | gain |
| B2 -> direct_base_leaf5 | +0.702 | +0.244 [+0.148, +0.346] | +0.339 | gain | gain |
| B2 -> direct_cal_leaf20 | +0.958 | +0.333 [+0.258, +0.405] | +0.606 | gain | gain |
| B2 -> direct_cal_leaf5 | +1.065 | +0.370 [+0.299, +0.438] | +0.674 | gain | gain |
| B2 -> gbm_funding | +0.725 | +0.252 [+0.115, +0.379] | +0.248 | gain | gain |
| B2 -> onestep_cal_leaf20 | +0.963 | +0.335 [+0.239, +0.423] | +0.561 | gain | gain |
| direct_base_leaf20 -> direct_base_leaf5 | -0.110 | -0.053 [-0.089, -0.017] | -0.207 | harm | not seen |
| direct_base_leaf20 -> direct_cal_leaf20 | +0.145 | +0.070 [+0.020, +0.114] | +0.030 | gain | gain |
| direct_base_leaf5 -> direct_cal_leaf5 | +0.362 | +0.167 [+0.112, +0.212] | +0.194 | gain | gain |
| direct_cal_leaf20 -> direct_cal_leaf5 | +0.107 | +0.056 [+0.004, +0.108] | +0.002 | gain | gain |
| gbm_funding -> direct_base_leaf20 | +0.087 | +0.041 [-0.037, +0.109] | -0.087 | not seen | not seen |
| gbm_funding -> direct_base_leaf5 | -0.023 | -0.011 [-0.108, +0.078] | -0.240 | not seen | not seen |
| gbm_funding -> direct_cal_leaf20 | +0.233 | +0.108 [+0.010, +0.192] | -0.006 | gain | not seen |
| gbm_funding -> direct_cal_leaf5 | +0.340 | +0.158 [+0.047, +0.257] | +0.058 | gain | gain |
| gbm_funding -> onestep_cal_leaf20 | +0.237 | +0.110 [+0.051, +0.158] | +0.073 | gain | gain |
| onestep_cal_leaf20 -> direct_cal_leaf20 | -0.005 | -0.003 [-0.066, +0.064] | -0.142 | not seen | not seen |

### day type: ordinary

n = 1868 decision days.

| first -> second | mean d | skill [90% percentile] | lower bound (studentized, one-sided) | percentile | studentized |
|---|---|---|---|---|---|
| B1 -> direct_base_leaf20 | +0.384 | +0.192 [+0.051, +0.318] | +0.115 | gain | gain |
| B1 -> direct_base_leaf5 | +0.287 | +0.144 [-0.005, +0.278] | +0.019 | not seen | gain |
| B1 -> direct_cal_leaf20 | +0.470 | +0.236 [+0.101, +0.355] | +0.194 | gain | gain |
| B1 -> direct_cal_leaf5 | +0.410 | +0.205 [+0.062, +0.334] | +0.130 | gain | gain |
| B1 -> gbm_funding | +0.499 | +0.250 [+0.133, +0.365] | +0.246 | gain | gain |
| B1 -> onestep_cal_leaf20 | +0.532 | +0.267 [+0.151, +0.378] | +0.278 | gain | gain |
| B2 -> direct_base_leaf20 | +0.541 | +0.251 [+0.184, +0.317] | +0.338 | gain | gain |
| B2 -> direct_base_leaf5 | +0.444 | +0.206 [+0.129, +0.282] | +0.225 | gain | gain |
| B2 -> direct_cal_leaf20 | +0.627 | +0.291 [+0.227, +0.354] | +0.423 | gain | gain |
| B2 -> direct_cal_leaf5 | +0.566 | +0.263 [+0.188, +0.335] | +0.347 | gain | gain |
| B2 -> gbm_funding | +0.656 | +0.305 [+0.235, +0.372] | +0.444 | gain | gain |
| B2 -> onestep_cal_leaf20 | +0.689 | +0.320 [+0.251, +0.386] | +0.476 | gain | gain |
| direct_base_leaf20 -> direct_base_leaf5 | -0.096 | -0.060 [-0.089, -0.034] | -0.150 | harm | not seen |
| direct_base_leaf20 -> direct_cal_leaf20 | +0.086 | +0.054 [+0.035, +0.072] | +0.053 | gain | gain |
| direct_base_leaf5 -> direct_cal_leaf5 | +0.122 | +0.072 [+0.049, +0.095] | +0.078 | gain | gain |
| direct_cal_leaf20 -> direct_cal_leaf5 | -0.061 | -0.040 [-0.068, -0.013] | -0.115 | harm | not seen |
| gbm_funding -> direct_base_leaf20 | -0.115 | -0.077 [-0.130, -0.029] | -0.199 | harm | not seen |
| gbm_funding -> direct_base_leaf5 | -0.212 | -0.142 [-0.204, -0.085] | -0.313 | harm | not seen |
| gbm_funding -> direct_cal_leaf20 | -0.029 | -0.019 [-0.072, +0.029] | -0.113 | not seen | not seen |
| gbm_funding -> direct_cal_leaf5 | -0.089 | -0.060 [-0.124, -0.003] | -0.191 | harm | not seen |
| gbm_funding -> onestep_cal_leaf20 | +0.033 | +0.022 [+0.011, +0.033] | +0.017 | gain | gain |
| onestep_cal_leaf20 -> direct_cal_leaf20 | -0.062 | -0.042 [-0.093, +0.004] | -0.140 | not seen | not seen |

### day type: quarter_end

n = 146 decision days.

| first -> second | mean d | skill [90% percentile] | lower bound (studentized, one-sided) | percentile | studentized |
|---|---|---|---|---|---|
| B1 -> direct_base_leaf20 | -0.885 | -0.131 [-0.277, -0.049] | -2.178 | harm | not seen |
| B1 -> direct_base_leaf5 | -1.095 | -0.162 [-0.337, -0.076] | -2.259 | harm | not seen |
| B1 -> direct_cal_leaf20 | -0.010 | -0.001 [-0.192, +0.153] | -1.248 | not seen | not seen |
| B1 -> direct_cal_leaf5 | -0.073 | -0.011 [-0.254, +0.152] | -1.719 | not seen | not seen |
| B1 -> gbm_funding | -0.894 | -0.133 [-0.212, -0.083] | -2.218 | harm | not seen |
| B1 -> onestep_cal_leaf20 | -0.165 | -0.025 [-0.132, +0.043] | -0.858 | not seen | not seen |
| B2 -> direct_base_leaf20 | -0.247 | -0.034 [-0.340, +0.317] | -3.448 | not seen | not seen |
| B2 -> direct_base_leaf5 | -0.457 | -0.062 [-0.369, +0.281] | -3.698 | not seen | not seen |
| B2 -> direct_cal_leaf20 | +0.628 | +0.085 [-0.163, +0.386] | -1.842 | not seen | not seen |
| B2 -> direct_cal_leaf5 | +0.564 | +0.076 [-0.137, +0.343] | -1.661 | not seen | not seen |
| B2 -> gbm_funding | -0.257 | -0.035 [-0.379, +0.345] | -3.921 | not seen | not seen |
| B2 -> onestep_cal_leaf20 | +0.472 | +0.064 [-0.218, +0.385] | -2.189 | not seen | not seen |
| direct_base_leaf20 -> direct_base_leaf5 | -0.210 | -0.027 [-0.067, -0.009] | -0.356 | harm | not seen |
| direct_base_leaf20 -> direct_cal_leaf20 | +0.875 | +0.115 [+0.027, +0.226] | +0.001 | gain | gain |
| direct_base_leaf5 -> direct_cal_leaf5 | +1.021 | +0.130 [-0.002, +0.261] | -0.094 | not seen | not seen |
| direct_cal_leaf20 -> direct_cal_leaf5 | -0.063 | -0.009 [-0.109, +0.052] | -0.528 | not seen | not seen |
| gbm_funding -> direct_base_leaf20 | +0.009 | +0.001 [-0.069, +0.042] | -0.382 | not seen | not seen |
| gbm_funding -> direct_base_leaf5 | -0.200 | -0.026 [-0.123, +0.019] | -0.617 | not seen | not seen |
| gbm_funding -> direct_cal_leaf20 | +0.884 | +0.116 [-0.018, +0.240] | -0.316 | not seen | not seen |
| gbm_funding -> direct_cal_leaf5 | +0.821 | +0.107 [-0.081, +0.245] | -0.773 | not seen | not seen |
| gbm_funding -> onestep_cal_leaf20 | +0.729 | +0.095 [+0.043, +0.140] | +0.058 | gain | gain |
| onestep_cal_leaf20 -> direct_cal_leaf20 | +0.155 | +0.022 [-0.074, +0.123] | -0.524 | not seen | not seen |

### day type: tax_date

n = 214 decision days.

| first -> second | mean d | skill [90% percentile] | lower bound (studentized, one-sided) | percentile | studentized |
|---|---|---|---|---|---|
| B1 -> direct_base_leaf20 | -0.613 | -0.125 [-0.345, -0.049] | -1.480 | harm | not seen |
| B1 -> direct_base_leaf5 | -0.671 | -0.136 [-0.391, -0.058] | -1.615 | harm | not seen |
| B1 -> direct_cal_leaf20 | -0.477 | -0.097 [-0.309, +0.003] | -1.336 | not seen | not seen |
| B1 -> direct_cal_leaf5 | -0.493 | -0.100 [-0.329, +0.004] | -1.393 | not seen | not seen |
| B1 -> gbm_funding | -0.277 | -0.056 [-0.192, +0.039] | -0.900 | not seen | not seen |
| B1 -> onestep_cal_leaf20 | -0.320 | -0.065 [-0.210, +0.029] | -0.979 | not seen | not seen |
| B2 -> direct_base_leaf20 | +1.631 | +0.228 [+0.096, +0.549] | +0.791 | gain | gain |
| B2 -> direct_base_leaf5 | +1.573 | +0.220 [+0.085, +0.544] | +0.698 | gain | gain |
| B2 -> direct_cal_leaf20 | +1.766 | +0.247 [+0.116, +0.574] | +0.947 | gain | gain |
| B2 -> direct_cal_leaf5 | +1.751 | +0.244 [+0.109, +0.576] | +0.906 | gain | gain |
| B2 -> gbm_funding | +1.966 | +0.275 [+0.134, +0.614] | +1.064 | gain | gain |
| B2 -> onestep_cal_leaf20 | +1.924 | +0.269 [+0.128, +0.607] | +1.024 | gain | gain |
| direct_base_leaf20 -> direct_base_leaf5 | -0.058 | -0.010 [-0.047, +0.008] | -0.147 | not seen | not seen |
| direct_base_leaf20 -> direct_cal_leaf20 | +0.135 | +0.024 [-0.001, +0.090] | +0.004 | not seen | gain |
| direct_base_leaf5 -> direct_cal_leaf5 | +0.178 | +0.032 [+0.008, +0.102] | +0.031 | gain | gain |
| direct_cal_leaf20 -> direct_cal_leaf5 | -0.016 | -0.003 [-0.032, +0.019] | -0.095 | not seen | not seen |
| gbm_funding -> direct_base_leaf20 | -0.336 | -0.065 [-0.195, -0.032] | -0.821 | harm | not seen |
| gbm_funding -> direct_base_leaf5 | -0.394 | -0.076 [-0.213, -0.043] | -0.859 | harm | not seen |
| gbm_funding -> direct_cal_leaf20 | -0.200 | -0.039 [-0.123, -0.009] | -0.439 | harm | not seen |
| gbm_funding -> direct_cal_leaf5 | -0.216 | -0.042 [-0.137, -0.012] | -0.466 | harm | not seen |
| gbm_funding -> onestep_cal_leaf20 | -0.043 | -0.008 [-0.026, -0.002] | -0.094 | harm | not seen |
| onestep_cal_leaf20 -> direct_cal_leaf20 | -0.158 | -0.030 [-0.106, -0.001] | -0.373 | harm | not seen |

### pooled: all

n = 1868 decision days.

| first -> second | mean d | skill [90% percentile] | lower bound (studentized, one-sided) | percentile | studentized |
|---|---|---|---|---|---|
| B1 -> direct_base_leaf20 | +0.377 | +0.164 [+0.051, +0.258] | +0.125 | gain | gain |
| B1 -> direct_base_leaf5 | +0.279 | +0.121 [-0.001, +0.222] | +0.030 | not seen | gain |
| B1 -> direct_cal_leaf20 | +0.479 | +0.208 [+0.103, +0.296] | +0.216 | gain | gain |
| B1 -> direct_cal_leaf5 | +0.432 | +0.187 [+0.073, +0.283] | +0.163 | gain | gain |
| B1 -> gbm_funding | +0.476 | +0.207 [+0.114, +0.289] | +0.235 | gain | gain |
| B1 -> onestep_cal_leaf20 | +0.534 | +0.232 [+0.143, +0.311] | +0.290 | gain | gain |
| B2 -> direct_base_leaf20 | +0.589 | +0.234 [+0.163, +0.310] | +0.373 | gain | gain |
| B2 -> direct_base_leaf5 | +0.491 | +0.195 [+0.119, +0.276] | +0.260 | gain | gain |
| B2 -> direct_cal_leaf20 | +0.691 | +0.275 [+0.205, +0.348] | +0.476 | gain | gain |
| B2 -> direct_cal_leaf5 | +0.643 | +0.256 [+0.184, +0.332] | +0.422 | gain | gain |
| B2 -> gbm_funding | +0.688 | +0.274 [+0.198, +0.353] | +0.456 | gain | gain |
| B2 -> onestep_cal_leaf20 | +0.745 | +0.296 [+0.222, +0.374] | +0.516 | gain | gain |
| direct_base_leaf20 -> direct_base_leaf5 | -0.098 | -0.051 [-0.074, -0.029] | -0.149 | harm | not seen |
| direct_base_leaf20 -> direct_cal_leaf20 | +0.102 | +0.053 [+0.037, +0.071] | +0.066 | gain | gain |
| direct_base_leaf5 -> direct_cal_leaf5 | +0.152 | +0.075 [+0.054, +0.098] | +0.102 | gain | gain |
| direct_cal_leaf20 -> direct_cal_leaf5 | -0.047 | -0.026 [-0.050, -0.004] | -0.095 | harm | not seen |
| gbm_funding -> direct_base_leaf20 | -0.099 | -0.054 [-0.098, -0.015] | -0.184 | harm | not seen |
| gbm_funding -> direct_base_leaf5 | -0.197 | -0.108 [-0.159, -0.063] | -0.295 | harm | not seen |
| gbm_funding -> direct_cal_leaf20 | +0.002 | +0.001 [-0.042, +0.043] | -0.081 | not seen | not seen |
| gbm_funding -> direct_cal_leaf5 | -0.045 | -0.024 [-0.076, +0.023] | -0.142 | not seen | not seen |
| gbm_funding -> onestep_cal_leaf20 | +0.057 | +0.031 [+0.019, +0.045] | +0.034 | gain | gain |
| onestep_cal_leaf20 -> direct_cal_leaf20 | -0.055 | -0.031 [-0.072, +0.008] | -0.133 | not seen | not seen |

### regime: 2018-19

n = 375 decision days.

| first -> second | mean d | skill [90% percentile] | lower bound (studentized, one-sided) | percentile | studentized |
|---|---|---|---|---|---|
| B1 -> direct_base_leaf20 | +1.537 | +0.268 [+0.084, +0.395] | +0.448 | gain | gain |
| B1 -> direct_base_leaf5 | +1.268 | +0.221 [+0.012, +0.356] | +0.177 | gain | gain |
| B1 -> direct_cal_leaf20 | +1.695 | +0.296 [+0.122, +0.419] | +0.571 | gain | gain |
| B1 -> direct_cal_leaf5 | +1.596 | +0.279 [+0.082, +0.408] | +0.409 | gain | gain |
| B1 -> gbm_funding | +1.734 | +0.303 [+0.140, +0.420] | +0.635 | gain | gain |
| B1 -> onestep_cal_leaf20 | +1.872 | +0.327 [+0.176, +0.439] | +0.770 | gain | gain |
| B2 -> direct_base_leaf20 | +0.174 | +0.040 [-0.037, +0.127] | -0.200 | not seen | not seen |
| B2 -> direct_base_leaf5 | -0.095 | -0.022 [-0.121, +0.072] | -0.549 | not seen | not seen |
| B2 -> direct_cal_leaf20 | +0.332 | +0.076 [-0.004, +0.166] | -0.046 | not seen | not seen |
| B2 -> direct_cal_leaf5 | +0.233 | +0.053 [-0.044, +0.149] | -0.241 | not seen | not seen |
| B2 -> gbm_funding | +0.371 | +0.085 [+0.009, +0.181] | +0.014 | gain | gain |
| B2 -> onestep_cal_leaf20 | +0.509 | +0.117 [+0.041, +0.218] | +0.147 | gain | gain |
| direct_base_leaf20 -> direct_base_leaf5 | -0.269 | -0.064 [-0.115, -0.029] | -0.444 | harm | not seen |
| direct_base_leaf20 -> direct_cal_leaf20 | +0.158 | +0.038 [+0.021, +0.059] | +0.070 | gain | gain |
| direct_base_leaf5 -> direct_cal_leaf5 | +0.328 | +0.074 [+0.040, +0.118] | +0.127 | gain | gain |
| direct_cal_leaf20 -> direct_cal_leaf5 | -0.099 | -0.025 [-0.072, +0.014] | -0.301 | not seen | not seen |
| gbm_funding -> direct_base_leaf20 | -0.198 | -0.049 [-0.102, -0.012] | -0.378 | harm | not seen |
| gbm_funding -> direct_base_leaf5 | -0.466 | -0.117 [-0.200, -0.064] | -0.698 | harm | not seen |
| gbm_funding -> direct_cal_leaf20 | -0.040 | -0.010 [-0.055, +0.029] | -0.222 | not seen | not seen |
| gbm_funding -> direct_cal_leaf5 | -0.139 | -0.035 [-0.105, +0.020] | -0.414 | not seen | not seen |
| gbm_funding -> onestep_cal_leaf20 | +0.137 | +0.034 [+0.020, +0.059] | +0.083 | gain | gain |
| onestep_cal_leaf20 -> direct_cal_leaf20 | -0.177 | -0.046 [-0.104, -0.010] | -0.352 | harm | not seen |

### regime: 2020

n = 251 decision days.

| first -> second | mean d | skill [90% percentile] | lower bound (studentized, one-sided) | percentile | studentized |
|---|---|---|---|---|---|
| B1 -> direct_base_leaf20 | +0.110 | +0.067 [-0.139, +0.222] | -0.261 | not seen | not seen |
| B1 -> direct_base_leaf5 | +0.120 | +0.073 [-0.136, +0.236] | -0.327 | not seen | not seen |
| B1 -> direct_cal_leaf20 | +0.073 | +0.045 [-0.200, +0.221] | -0.386 | not seen | not seen |
| B1 -> direct_cal_leaf5 | +0.118 | +0.072 [-0.161, +0.246] | -0.385 | not seen | not seen |
| B1 -> gbm_funding | +0.227 | +0.138 [+0.011, +0.250] | +0.048 | gain | gain |
| B1 -> onestep_cal_leaf20 | +0.209 | +0.127 [+0.001, +0.235] | +0.034 | gain | gain |
| B2 -> direct_base_leaf20 | +1.252 | +0.449 [+0.290, +0.577] | +0.577 | gain | gain |
| B2 -> direct_base_leaf5 | +1.262 | +0.453 [+0.290, +0.592] | +0.597 | gain | gain |
| B2 -> direct_cal_leaf20 | +1.215 | +0.436 [+0.282, +0.561] | +0.566 | gain | gain |
| B2 -> direct_cal_leaf5 | +1.261 | +0.452 [+0.291, +0.590] | +0.597 | gain | gain |
| B2 -> gbm_funding | +1.369 | +0.491 [+0.316, +0.626] | +0.649 | gain | gain |
| B2 -> onestep_cal_leaf20 | +1.351 | +0.485 [+0.313, +0.621] | +0.633 | gain | gain |
| direct_base_leaf20 -> direct_base_leaf5 | +0.010 | +0.007 [-0.039, +0.058] | -0.081 | not seen | not seen |
| direct_base_leaf20 -> direct_cal_leaf20 | -0.037 | -0.024 [-0.073, +0.019] | -0.122 | not seen | not seen |
| direct_base_leaf5 -> direct_cal_leaf5 | -0.002 | -0.001 [-0.037, +0.036] | -0.057 | not seen | not seen |
| direct_cal_leaf20 -> direct_cal_leaf5 | +0.045 | +0.029 [-0.012, +0.081] | -0.036 | not seen | not seen |
| gbm_funding -> direct_base_leaf20 | -0.117 | -0.082 [-0.222, +0.020] | -0.365 | not seen | not seen |
| gbm_funding -> direct_base_leaf5 | -0.107 | -0.075 [-0.214, +0.042] | -0.425 | not seen | not seen |
| gbm_funding -> direct_cal_leaf20 | -0.154 | -0.108 [-0.286, +0.026] | -0.481 | not seen | not seen |
| gbm_funding -> direct_cal_leaf5 | -0.108 | -0.077 [-0.235, +0.059] | -0.466 | not seen | not seen |
| gbm_funding -> onestep_cal_leaf20 | -0.018 | -0.013 [-0.048, +0.017] | -0.066 | not seen | not seen |
| onestep_cal_leaf20 -> direct_cal_leaf20 | -0.136 | -0.095 [-0.268, +0.034] | -0.462 | not seen | not seen |

### regime: 2021-23

n = 748 decision days.

| first -> second | mean d | skill [90% percentile] | lower bound (studentized, one-sided) | percentile | studentized |
|---|---|---|---|---|---|
| B1 -> direct_base_leaf20 | -0.148 | -0.208 [-0.365, -0.062] | -0.304 | harm | not seen |
| B1 -> direct_base_leaf5 | -0.207 | -0.291 [-0.476, -0.132] | -0.386 | harm | not seen |
| B1 -> direct_cal_leaf20 | -0.141 | -0.199 [-0.360, -0.052] | -0.305 | harm | not seen |
| B1 -> direct_cal_leaf5 | -0.202 | -0.285 [-0.478, -0.115] | -0.391 | harm | not seen |
| B1 -> gbm_funding | -0.006 | -0.009 [-0.134, +0.103] | -0.119 | not seen | not seen |
| B1 -> onestep_cal_leaf20 | -0.015 | -0.021 [-0.146, +0.092] | -0.136 | not seen | not seen |
| B2 -> direct_base_leaf20 | +0.622 | +0.420 [+0.293, +0.535] | +0.361 | gain | gain |
| B2 -> direct_base_leaf5 | +0.563 | +0.380 [+0.240, +0.504] | +0.287 | gain | gain |
| B2 -> direct_cal_leaf20 | +0.629 | +0.425 [+0.305, +0.535] | +0.373 | gain | gain |
| B2 -> direct_cal_leaf5 | +0.568 | +0.383 [+0.245, +0.506] | +0.289 | gain | gain |
| B2 -> gbm_funding | +0.764 | +0.516 [+0.405, +0.616] | +0.495 | gain | gain |
| B2 -> onestep_cal_leaf20 | +0.756 | +0.510 [+0.398, +0.612] | +0.488 | gain | gain |
| direct_base_leaf20 -> direct_base_leaf5 | -0.059 | -0.069 [-0.128, -0.011] | -0.114 | harm | not seen |
| direct_base_leaf20 -> direct_cal_leaf20 | +0.007 | +0.008 [-0.014, +0.031] | -0.013 | not seen | not seen |
| direct_base_leaf5 -> direct_cal_leaf5 | +0.005 | +0.005 [-0.013, +0.024] | -0.012 | not seen | not seen |
| direct_cal_leaf20 -> direct_cal_leaf5 | -0.061 | -0.072 [-0.135, -0.015] | -0.125 | harm | not seen |
| gbm_funding -> direct_base_leaf20 | -0.141 | -0.197 [-0.278, -0.134] | -0.208 | harm | not seen |
| gbm_funding -> direct_base_leaf5 | -0.201 | -0.280 [-0.396, -0.192] | -0.292 | harm | not seen |
| gbm_funding -> direct_cal_leaf20 | -0.135 | -0.188 [-0.269, -0.122] | -0.203 | harm | not seen |
| gbm_funding -> direct_cal_leaf5 | -0.196 | -0.273 [-0.394, -0.180] | -0.294 | harm | not seen |
| gbm_funding -> onestep_cal_leaf20 | -0.008 | -0.011 [-0.030, +0.007] | -0.022 | not seen | not seen |
| onestep_cal_leaf20 -> direct_cal_leaf20 | -0.126 | -0.174 [-0.253, -0.111] | -0.189 | harm | not seen |

### regime: 2024

n = 250 decision days.

| first -> second | mean d | skill [90% percentile] | lower bound (studentized, one-sided) | percentile | studentized |
|---|---|---|---|---|---|
| B1 -> direct_base_leaf20 | +0.406 | +0.241 [+0.090, +0.334] | +0.121 | gain | gain |
| B1 -> direct_base_leaf5 | +0.321 | +0.191 [-0.015, +0.302] | +0.006 | not seen | gain |
| B1 -> direct_cal_leaf20 | +0.545 | +0.324 [+0.211, +0.404] | +0.257 | gain | gain |
| B1 -> direct_cal_leaf5 | +0.525 | +0.312 [+0.188, +0.395] | +0.233 | gain | gain |
| B1 -> gbm_funding | +0.272 | +0.162 [+0.092, +0.216] | +0.131 | gain | gain |
| B1 -> onestep_cal_leaf20 | +0.311 | +0.185 [+0.127, +0.230] | +0.168 | gain | gain |
| B2 -> direct_base_leaf20 | +0.101 | +0.073 [-0.037, +0.159] | -0.063 | not seen | not seen |
| B2 -> direct_base_leaf5 | +0.016 | +0.012 [-0.183, +0.142] | -0.271 | not seen | not seen |
| B2 -> direct_cal_leaf20 | +0.240 | +0.174 [+0.070, +0.273] | +0.060 | gain | gain |
| B2 -> direct_cal_leaf5 | +0.220 | +0.160 [+0.041, +0.267] | +0.013 | gain | gain |
| B2 -> gbm_funding | -0.033 | -0.024 [-0.167, +0.128] | -0.278 | not seen | not seen |
| B2 -> onestep_cal_leaf20 | +0.006 | +0.004 [-0.140, +0.156] | -0.242 | not seen | not seen |
| direct_base_leaf20 -> direct_base_leaf5 | -0.085 | -0.066 [-0.157, -0.009] | -0.244 | harm | not seen |
| direct_base_leaf20 -> direct_cal_leaf20 | +0.139 | +0.109 [+0.061, +0.166] | +0.090 | gain | gain |
| direct_base_leaf5 -> direct_cal_leaf5 | +0.204 | +0.150 [+0.095, +0.222] | +0.138 | gain | gain |
| direct_cal_leaf20 -> direct_cal_leaf5 | -0.020 | -0.017 [-0.058, +0.010] | -0.062 | not seen | not seen |
| gbm_funding -> direct_base_leaf20 | +0.134 | +0.095 [-0.018, +0.161] | -0.017 | not seen | not seen |
| gbm_funding -> direct_base_leaf5 | +0.049 | +0.035 [-0.140, +0.130] | -0.150 | not seen | not seen |
| gbm_funding -> direct_cal_leaf20 | +0.273 | +0.193 [+0.117, +0.253] | +0.121 | gain | gain |
| gbm_funding -> direct_cal_leaf5 | +0.253 | +0.179 [+0.092, +0.239] | +0.093 | gain | gain |
| gbm_funding -> onestep_cal_leaf20 | +0.039 | +0.028 [+0.007, +0.057] | +0.009 | gain | gain |
| onestep_cal_leaf20 -> direct_cal_leaf20 | +0.234 | +0.170 [+0.084, +0.235] | +0.084 | gain | gain |

### regime: 2025-26

n = 244 decision days.

| first -> second | mean d | skill [90% percentile] | lower bound (studentized, one-sided) | percentile | studentized |
|---|---|---|---|---|---|
| B1 -> direct_base_leaf20 | +0.448 | +0.139 [-0.047, +0.278] | -0.128 | not seen | not seen |
| B1 -> direct_base_leaf5 | +0.370 | +0.114 [-0.057, +0.247] | -0.175 | not seen | not seen |
| B1 -> direct_cal_leaf20 | +0.859 | +0.266 [+0.114, +0.390] | +0.357 | gain | gain |
| B1 -> direct_cal_leaf5 | +0.812 | +0.251 [+0.094, +0.376] | +0.307 | gain | gain |
| B1 -> gbm_funding | +0.489 | +0.151 [+0.078, +0.216] | +0.243 | gain | gain |
| B1 -> onestep_cal_leaf20 | +0.719 | +0.223 [+0.144, +0.287] | +0.433 | gain | gain |
| B2 -> direct_base_leaf20 | +0.941 | +0.253 [+0.083, +0.361] | +0.112 | gain | gain |
| B2 -> direct_base_leaf5 | +0.863 | +0.232 [+0.062, +0.336] | +0.062 | gain | gain |
| B2 -> direct_cal_leaf20 | +1.352 | +0.363 [+0.237, +0.445] | +0.523 | gain | gain |
| B2 -> direct_cal_leaf5 | +1.305 | +0.350 [+0.231, +0.429] | +0.509 | gain | gain |
| B2 -> gbm_funding | +0.982 | +0.264 [+0.056, +0.392] | -0.046 | gain | not seen |
| B2 -> onestep_cal_leaf20 | +1.212 | +0.326 [+0.146, +0.438] | +0.201 | gain | gain |
| direct_base_leaf20 -> direct_base_leaf5 | -0.079 | -0.028 [-0.059, +0.007] | -0.202 | not seen | not seen |
| direct_base_leaf20 -> direct_cal_leaf20 | +0.411 | +0.148 [+0.115, +0.185] | +0.297 | gain | gain |
| direct_base_leaf5 -> direct_cal_leaf5 | +0.442 | +0.155 [+0.119, +0.197] | +0.331 | gain | gain |
| direct_cal_leaf20 -> direct_cal_leaf5 | -0.047 | -0.020 [-0.040, +0.004] | -0.130 | not seen | not seen |
| gbm_funding -> direct_base_leaf20 | -0.040 | -0.015 [-0.173, +0.121] | -0.611 | not seen | not seen |
| gbm_funding -> direct_base_leaf5 | -0.119 | -0.043 [-0.184, +0.085] | -0.695 | not seen | not seen |
| gbm_funding -> direct_cal_leaf20 | +0.371 | +0.135 [-0.001, +0.264] | -0.057 | not seen | not seen |
| gbm_funding -> direct_cal_leaf5 | +0.324 | +0.118 [-0.020, +0.249] | -0.123 | not seen | not seen |
| gbm_funding -> onestep_cal_leaf20 | +0.231 | +0.084 [+0.054, +0.115] | +0.144 | gain | gain |
| onestep_cal_leaf20 -> direct_cal_leaf20 | +0.140 | +0.056 [-0.069, +0.177] | -0.267 | not seen | not seen |

## Question for Eleonora (marked, not settled here)

Whether any reading of the original page that changes side above is reopened is hers. This page decides nothing and changes no published figure.
