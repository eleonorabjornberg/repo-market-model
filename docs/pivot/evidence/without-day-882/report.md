# With and without decision day 2019-09-18 (#882)

Development data, not a verdict.

## 758

Reproduction of the tracked score file: 208 records compared, largest absolute difference 0.00e+00 (headline figures and interval bounds); 0 not in the tracked file. Records whose path names ceiling or reachable: largest difference 5.59e-02.

Records compared: 208; records in which a bound of the interval changes sign: 6.

| record | metric | days (without) | with | without | interval with | interval without | bound changes sign |
|---|---|---|---|---|---|---|---|
| `/cells/crps/day type: month_end/headroom/c_two_part_new -> ceiling gbm` | headroom | 433 (433) | -0.033 | -0.033 | [-0.141, +0.082] | [-0.141, +0.082] |  |
| `/cells/crps/day type: month_end/headroom/c_two_part_new -> reachable gbm` | headroom | 433 (433) | -0.047 | -0.047 | [-0.122, +0.009] | [-0.122, +0.009] |  |
| `/cells/crps/day type: month_end/headroom/gbm_funding -> ceiling gbm` | headroom | 433 (433) | +0.032 | +0.032 | [-0.128, +0.183] | [-0.128, +0.183] |  |
| `/cells/crps/day type: month_end/headroom/gbm_funding -> reachable gbm` | headroom | 433 (433) | +0.019 | +0.019 | [-0.176, +0.146] | [-0.176, +0.146] |  |
| `/cells/crps/day type: month_end/tests/B1 -> c_two_part_new` | skill | 433 (433) | +0.140 | +0.140 | [-0.040, +0.263] | [-0.040, +0.263] |  |
| `/cells/crps/day type: month_end/tests/B1 -> ceiling gbm` | skill | 433 (433) | +0.107 | +0.107 | [-0.084, +0.275] | [-0.084, +0.275] |  |
| `/cells/crps/day type: month_end/tests/B1 -> gbm_funding` | skill | 433 (433) | +0.075 | +0.075 | [-0.007, +0.153] | [-0.007, +0.153] |  |
| `/cells/crps/day type: month_end/tests/B1 -> reachable gbm` | skill | 433 (433) | +0.094 | +0.094 | [-0.137, +0.251] | [-0.137, +0.251] |  |
| `/cells/crps/day type: month_end/tests/B2 -> c_two_part_new` | skill | 433 (433) | +0.376 | +0.376 | [+0.262, +0.455] | [+0.262, +0.455] |  |
| `/cells/crps/day type: month_end/tests/B2 -> ceiling gbm` | skill | 433 (433) | +0.352 | +0.352 | [+0.241, +0.458] | [+0.241, +0.458] |  |
| `/cells/crps/day type: month_end/tests/B2 -> gbm_funding` | skill | 433 (433) | +0.329 | +0.329 | [+0.153, +0.465] | [+0.153, +0.465] |  |
| `/cells/crps/day type: month_end/tests/B2 -> reachable gbm` | skill | 433 (433) | +0.343 | +0.343 | [+0.251, +0.407] | [+0.251, +0.407] |  |
| `/cells/crps/day type: month_end/tests/c_two_part_new -> ceiling gbm` | skill | 433 (433) | -0.039 | -0.039 | [-0.161, +0.091] | [-0.161, +0.091] |  |
| `/cells/crps/day type: month_end/tests/c_two_part_new -> reachable gbm` | skill | 433 (433) | -0.054 | -0.054 | [-0.128, +0.011] | [-0.128, +0.011] |  |
| `/cells/crps/day type: month_end/tests/gbm_funding -> ceiling gbm` | skill | 433 (433) | +0.035 | +0.035 | [-0.134, +0.200] | [-0.134, +0.200] |  |
| `/cells/crps/day type: month_end/tests/gbm_funding -> reachable gbm` | skill | 433 (433) | +0.021 | +0.021 | [-0.184, +0.160] | [-0.184, +0.160] |  |
| `/cells/crps/day type: ordinary/headroom/c_two_part_new -> ceiling gbm` | headroom | 1598 (1597) | -0.061 | -0.068 | [-0.127, +0.006] | [-0.145, +0.010] |  |
| `/cells/crps/day type: ordinary/headroom/c_two_part_new -> reachable gbm` | headroom | 1598 (1597) | -0.031 | -0.035 | [-0.076, +0.011] | [-0.086, +0.014] |  |
| `/cells/crps/day type: ordinary/headroom/gbm_funding -> ceiling gbm` | headroom | 1598 (1597) | -0.085 | -0.094 | [-0.153, -0.018] | [-0.171, -0.017] |  |
| `/cells/crps/day type: ordinary/headroom/gbm_funding -> reachable gbm` | headroom | 1598 (1597) | -0.055 | -0.061 | [-0.115, -0.006] | [-0.126, -0.006] |  |
| `/cells/crps/day type: ordinary/tests/B1 -> c_two_part_new` | skill | 1598 (1597) | +0.228 | +0.138 | [+0.065, +0.376] | [+0.043, +0.220] |  |
| `/cells/crps/day type: ordinary/tests/B1 -> ceiling gbm` | skill | 1598 (1597) | +0.167 | +0.070 | [+0.004, +0.308] | [-0.024, +0.154] | yes |
| `/cells/crps/day type: ordinary/tests/B1 -> gbm_funding` | skill | 1598 (1597) | +0.252 | +0.164 | [+0.114, +0.390] | [+0.104, +0.224] |  |
| `/cells/crps/day type: ordinary/tests/B1 -> reachable gbm` | skill | 1598 (1597) | +0.197 | +0.103 | [+0.021, +0.348] | [-0.001, +0.190] | yes |
| `/cells/crps/day type: ordinary/tests/B2 -> c_two_part_new` | skill | 1598 (1597) | +0.324 | +0.324 | [+0.244, +0.396] | [+0.245, +0.398] |  |
| `/cells/crps/day type: ordinary/tests/B2 -> ceiling gbm` | skill | 1598 (1597) | +0.270 | +0.271 | [+0.186, +0.351] | [+0.186, +0.352] |  |
| `/cells/crps/day type: ordinary/tests/B2 -> gbm_funding` | skill | 1598 (1597) | +0.345 | +0.345 | [+0.267, +0.416] | [+0.265, +0.420] |  |
| `/cells/crps/day type: ordinary/tests/B2 -> reachable gbm` | skill | 1598 (1597) | +0.297 | +0.297 | [+0.233, +0.358] | [+0.234, +0.359] |  |
| `/cells/crps/day type: ordinary/tests/c_two_part_new -> ceiling gbm` | skill | 1598 (1597) | -0.080 | -0.078 | [-0.180, +0.007] | [-0.179, +0.011] |  |
| `/cells/crps/day type: ordinary/tests/c_two_part_new -> reachable gbm` | skill | 1598 (1597) | -0.041 | -0.041 | [-0.100, +0.014] | [-0.101, +0.016] |  |
| `/cells/crps/day type: ordinary/tests/gbm_funding -> ceiling gbm` | skill | 1598 (1597) | -0.114 | -0.112 | [-0.209, -0.023] | [-0.208, -0.020] |  |
| `/cells/crps/day type: ordinary/tests/gbm_funding -> reachable gbm` | skill | 1598 (1597) | -0.074 | -0.073 | [-0.147, -0.007] | [-0.148, -0.008] |  |
| `/cells/crps/day type: quarter_end/headroom/c_two_part_new -> ceiling gbm` | headroom | 126 (126) | -0.075 | -0.075 | [-0.134, +0.021] | [-0.134, +0.021] |  |
| `/cells/crps/day type: quarter_end/headroom/c_two_part_new -> reachable gbm` | headroom | 126 (126) | -0.153 | -0.153 | [-0.207, -0.070] | [-0.207, -0.070] |  |
| `/cells/crps/day type: quarter_end/headroom/gbm_funding -> ceiling gbm` | headroom | 126 (126) | +0.203 | +0.203 | [-0.124, +0.378] | [-0.124, +0.378] |  |
| `/cells/crps/day type: quarter_end/headroom/gbm_funding -> reachable gbm` | headroom | 126 (126) | +0.125 | +0.125 | [-0.195, +0.289] | [-0.195, +0.289] |  |
| `/cells/crps/day type: quarter_end/tests/B1 -> c_two_part_new` | skill | 126 (126) | +0.104 | +0.104 | [-0.295, +0.301] | [-0.295, +0.301] |  |
| `/cells/crps/day type: quarter_end/tests/B1 -> ceiling gbm` | skill | 126 (126) | +0.029 | +0.029 | [-0.361, +0.253] | [-0.361, +0.253] |  |
| `/cells/crps/day type: quarter_end/tests/B1 -> gbm_funding` | skill | 126 (126) | -0.174 | -0.174 | [-0.248, -0.105] | [-0.248, -0.105] |  |
| `/cells/crps/day type: quarter_end/tests/B1 -> reachable gbm` | skill | 126 (126) | -0.049 | -0.049 | [-0.410, +0.155] | [-0.410, +0.155] |  |
| `/cells/crps/day type: quarter_end/tests/B2 -> c_two_part_new` | skill | 126 (126) | +0.329 | +0.329 | [+0.113, +0.510] | [+0.113, +0.510] |  |
| `/cells/crps/day type: quarter_end/tests/B2 -> ceiling gbm` | skill | 126 (126) | +0.273 | +0.273 | [-0.002, +0.504] | [-0.002, +0.504] |  |
| `/cells/crps/day type: quarter_end/tests/B2 -> gbm_funding` | skill | 126 (126) | +0.121 | +0.121 | [-0.347, +0.505] | [-0.347, +0.505] |  |
| `/cells/crps/day type: quarter_end/tests/B2 -> reachable gbm` | skill | 126 (126) | +0.214 | +0.214 | [-0.053, +0.439] | [-0.053, +0.439] |  |
| `/cells/crps/day type: quarter_end/tests/c_two_part_new -> ceiling gbm` | skill | 126 (126) | -0.084 | -0.084 | [-0.154, +0.023] | [-0.154, +0.023] |  |
| `/cells/crps/day type: quarter_end/tests/c_two_part_new -> reachable gbm` | skill | 126 (126) | -0.171 | -0.171 | [-0.240, -0.062] | [-0.240, -0.062] |  |
| `/cells/crps/day type: quarter_end/tests/gbm_funding -> ceiling gbm` | skill | 126 (126) | +0.173 | +0.173 | [-0.100, +0.336] | [-0.100, +0.336] |  |
| `/cells/crps/day type: quarter_end/tests/gbm_funding -> reachable gbm` | skill | 126 (126) | +0.106 | +0.106 | [-0.162, +0.253] | [-0.162, +0.253] |  |
| `/cells/crps/day type: tax_date/headroom/c_two_part_new -> ceiling gbm` | headroom | 185 (185) | -0.066 | -0.066 | [-0.203, -0.020] | [-0.203, -0.020] |  |
| `/cells/crps/day type: tax_date/headroom/c_two_part_new -> reachable gbm` | headroom | 185 (185) | -0.030 | -0.030 | [-0.116, +0.015] | [-0.116, +0.015] |  |
| `/cells/crps/day type: tax_date/headroom/gbm_funding -> ceiling gbm` | headroom | 185 (185) | -0.079 | -0.079 | [-0.399, -0.034] | [-0.399, -0.034] |  |
| `/cells/crps/day type: tax_date/headroom/gbm_funding -> reachable gbm` | headroom | 185 (185) | -0.044 | -0.044 | [-0.313, -0.003] | [-0.313, -0.003] |  |
| `/cells/crps/day type: tax_date/tests/B1 -> c_two_part_new` | skill | 185 (185) | -0.042 | -0.042 | [-0.357, +0.075] | [-0.357, +0.075] |  |
| `/cells/crps/day type: tax_date/tests/B1 -> ceiling gbm` | skill | 185 (185) | -0.108 | -0.108 | [-0.505, -0.015] | [-0.505, -0.015] |  |
| `/cells/crps/day type: tax_date/tests/B1 -> gbm_funding` | skill | 185 (185) | -0.029 | -0.029 | [-0.147, +0.110] | [-0.147, +0.110] |  |
| `/cells/crps/day type: tax_date/tests/B1 -> reachable gbm` | skill | 185 (185) | -0.073 | -0.073 | [-0.403, +0.020] | [-0.403, +0.020] |  |
| `/cells/crps/day type: tax_date/tests/B2 -> c_two_part_new` | skill | 185 (185) | +0.275 | +0.275 | [+0.152, +0.628] | [+0.152, +0.628] |  |
| `/cells/crps/day type: tax_date/tests/B2 -> ceiling gbm` | skill | 185 (185) | +0.229 | +0.229 | [+0.103, +0.593] | [+0.103, +0.593] |  |
| `/cells/crps/day type: tax_date/tests/B2 -> gbm_funding` | skill | 185 (185) | +0.284 | +0.284 | [+0.143, +0.686] | [+0.143, +0.686] |  |
| `/cells/crps/day type: tax_date/tests/B2 -> reachable gbm` | skill | 185 (185) | +0.254 | +0.254 | [+0.133, +0.603] | [+0.133, +0.603] |  |
| `/cells/crps/day type: tax_date/tests/c_two_part_new -> ceiling gbm` | skill | 185 (185) | -0.063 | -0.063 | [-0.179, -0.019] | [-0.179, -0.019] |  |
| `/cells/crps/day type: tax_date/tests/c_two_part_new -> reachable gbm` | skill | 185 (185) | -0.029 | -0.029 | [-0.107, +0.012] | [-0.107, +0.012] |  |
| `/cells/crps/day type: tax_date/tests/gbm_funding -> ceiling gbm` | skill | 185 (185) | -0.077 | -0.077 | [-0.374, -0.033] | [-0.374, -0.033] |  |
| `/cells/crps/day type: tax_date/tests/gbm_funding -> reachable gbm` | skill | 185 (185) | -0.043 | -0.043 | [-0.298, -0.003] | [-0.298, -0.003] |  |
| `/cells/crps/pooled, all targets/headroom/c_two_part_new -> ceiling gbm` | headroom | 1598 (1597) | -0.057 | -0.062 | [-0.113, +0.006] | [-0.121, +0.005] |  |
| `/cells/crps/pooled, all targets/headroom/c_two_part_new -> reachable gbm` | headroom | 1598 (1597) | -0.032 | -0.035 | [-0.070, +0.006] | [-0.074, +0.005] |  |
| `/cells/crps/pooled, all targets/headroom/gbm_funding -> ceiling gbm` | headroom | 1598 (1597) | -0.058 | -0.063 | [-0.121, +0.001] | [-0.127, +0.002] |  |
| `/cells/crps/pooled, all targets/headroom/gbm_funding -> reachable gbm` | headroom | 1598 (1597) | -0.033 | -0.036 | [-0.090, +0.011] | [-0.095, +0.012] |  |
| `/cells/crps/pooled, all targets/tests/B1 -> c_two_part_new` | skill | 1598 (1597) | +0.206 | +0.128 | [+0.066, +0.316] | [+0.049, +0.196] |  |
| `/cells/crps/pooled, all targets/tests/B1 -> ceiling gbm` | skill | 1598 (1597) | +0.149 | +0.066 | [+0.011, +0.262] | [-0.014, +0.142] | yes |
| `/cells/crps/pooled, all targets/tests/B1 -> gbm_funding` | skill | 1598 (1597) | +0.208 | +0.129 | [+0.097, +0.307] | [+0.082, +0.175] |  |
| `/cells/crps/pooled, all targets/tests/B1 -> reachable gbm` | skill | 1598 (1597) | +0.174 | +0.093 | [+0.028, +0.291] | [+0.005, +0.168] |  |
| `/cells/crps/pooled, all targets/tests/B2 -> c_two_part_new` | skill | 1598 (1597) | +0.315 | +0.315 | [+0.231, +0.400] | [+0.229, +0.400] |  |
| `/cells/crps/pooled, all targets/tests/B2 -> ceiling gbm` | skill | 1598 (1597) | +0.266 | +0.267 | [+0.173, +0.363] | [+0.173, +0.363] |  |
| `/cells/crps/pooled, all targets/tests/B2 -> gbm_funding` | skill | 1598 (1597) | +0.316 | +0.316 | [+0.224, +0.410] | [+0.223, +0.411] |  |
| `/cells/crps/pooled, all targets/tests/B2 -> reachable gbm` | skill | 1598 (1597) | +0.288 | +0.288 | [+0.212, +0.365] | [+0.211, +0.365] |  |
| `/cells/crps/pooled, all targets/tests/c_two_part_new -> ceiling gbm` | skill | 1598 (1597) | -0.072 | -0.071 | [-0.145, +0.007] | [-0.143, +0.006] |  |
| `/cells/crps/pooled, all targets/tests/c_two_part_new -> reachable gbm` | skill | 1598 (1597) | -0.040 | -0.040 | [-0.086, +0.007] | [-0.086, +0.006] |  |
| `/cells/crps/pooled, all targets/tests/gbm_funding -> ceiling gbm` | skill | 1598 (1597) | -0.073 | -0.072 | [-0.149, +0.001] | [-0.147, +0.002] |  |
| `/cells/crps/pooled, all targets/tests/gbm_funding -> reachable gbm` | skill | 1598 (1597) | -0.042 | -0.041 | [-0.108, +0.015] | [-0.107, +0.014] |  |
| `/cells/crps/pooled, ordinary targets/headroom/c_two_part_new -> ceiling gbm` | headroom | 1598 (1597) | -0.064 | -0.071 | [-0.132, +0.012] | [-0.150, +0.014] |  |
| `/cells/crps/pooled, ordinary targets/headroom/c_two_part_new -> reachable gbm` | headroom | 1598 (1597) | -0.031 | -0.035 | [-0.079, +0.019] | [-0.088, +0.020] |  |
| `/cells/crps/pooled, ordinary targets/headroom/gbm_funding -> ceiling gbm` | headroom | 1598 (1597) | -0.097 | -0.107 | [-0.170, -0.026] | [-0.189, -0.027] |  |
| `/cells/crps/pooled, ordinary targets/headroom/gbm_funding -> reachable gbm` | headroom | 1598 (1597) | -0.064 | -0.071 | [-0.123, -0.015] | [-0.133, -0.017] |  |
| `/cells/crps/pooled, ordinary targets/tests/B1 -> c_two_part_new` | skill | 1598 (1597) | +0.224 | +0.132 | [+0.052, +0.380] | [+0.037, +0.213] |  |
| `/cells/crps/pooled, ordinary targets/tests/B1 -> ceiling gbm` | skill | 1598 (1597) | +0.160 | +0.061 | [-0.006, +0.310] | [-0.035, +0.147] |  |
| `/cells/crps/pooled, ordinary targets/tests/B1 -> gbm_funding` | skill | 1598 (1597) | +0.257 | +0.169 | [+0.114, +0.400] | [+0.106, +0.229] |  |
| `/cells/crps/pooled, ordinary targets/tests/B1 -> reachable gbm` | skill | 1598 (1597) | +0.193 | +0.097 | [+0.015, +0.352] | [-0.008, +0.186] | yes |
| `/cells/crps/pooled, ordinary targets/tests/B2 -> c_two_part_new` | skill | 1598 (1597) | +0.318 | +0.318 | [+0.234, +0.393] | [+0.234, +0.393] |  |
| `/cells/crps/pooled, ordinary targets/tests/B2 -> ceiling gbm` | skill | 1598 (1597) | +0.261 | +0.262 | [+0.174, +0.345] | [+0.173, +0.346] |  |
| `/cells/crps/pooled, ordinary targets/tests/B2 -> gbm_funding` | skill | 1598 (1597) | +0.347 | +0.347 | [+0.267, +0.421] | [+0.266, +0.421] |  |
| `/cells/crps/pooled, ordinary targets/tests/B2 -> reachable gbm` | skill | 1598 (1597) | +0.290 | +0.290 | [+0.227, +0.350] | [+0.227, +0.352] |  |
| `/cells/crps/pooled, ordinary targets/tests/c_two_part_new -> ceiling gbm` | skill | 1598 (1597) | -0.083 | -0.082 | [-0.183, +0.014] | [-0.181, +0.016] |  |
| `/cells/crps/pooled, ordinary targets/tests/c_two_part_new -> reachable gbm` | skill | 1598 (1597) | -0.040 | -0.040 | [-0.102, +0.022] | [-0.102, +0.022] |  |
| `/cells/crps/pooled, ordinary targets/tests/gbm_funding -> ceiling gbm` | skill | 1598 (1597) | -0.131 | -0.129 | [-0.233, -0.033] | [-0.231, -0.032] |  |
| `/cells/crps/pooled, ordinary targets/tests/gbm_funding -> reachable gbm` | skill | 1598 (1597) | -0.086 | -0.086 | [-0.158, -0.021] | [-0.157, -0.021] |  |
| `/cells/crps/regime: 2018-19/headroom/c_two_part_new -> ceiling gbm` | headroom | 101 (100) | -0.164 | -0.286 | [-0.329, -0.056] | [-0.428, -0.079] |  |
| `/cells/crps/regime: 2018-19/headroom/c_two_part_new -> reachable gbm` | headroom | 101 (100) | -0.093 | -0.167 | [-0.311, -0.038] | [-0.331, -0.078] |  |
| `/cells/crps/regime: 2018-19/headroom/gbm_funding -> ceiling gbm` | headroom | 101 (100) | -0.127 | -0.216 | [-0.281, +0.030] | [-0.385, +0.042] |  |
| `/cells/crps/regime: 2018-19/headroom/gbm_funding -> reachable gbm` | headroom | 101 (100) | -0.056 | -0.098 | [-0.184, -0.023] | [-0.200, -0.040] |  |
| `/cells/crps/regime: 2018-19/tests/B1 -> c_two_part_new` | skill | 101 (100) | +0.697 | +0.471 | [+0.339, +0.821] | [+0.328, +0.571] |  |
| `/cells/crps/regime: 2018-19/tests/B1 -> ceiling gbm` | skill | 101 (100) | +0.533 | +0.185 | [+0.045, +0.709] | [-0.039, +0.401] | yes |
| `/cells/crps/regime: 2018-19/tests/B1 -> gbm_funding` | skill | 101 (100) | +0.660 | +0.401 | [+0.240, +0.799] | [+0.224, +0.513] |  |
| `/cells/crps/regime: 2018-19/tests/B1 -> reachable gbm` | skill | 101 (100) | +0.604 | +0.304 | [+0.067, +0.770] | [+0.052, +0.456] |  |
| `/cells/crps/regime: 2018-19/tests/B2 -> c_two_part_new` | skill | 101 (100) | +0.226 | +0.225 | [+0.084, +0.375] | [+0.084, +0.377] |  |
| `/cells/crps/regime: 2018-19/tests/B2 -> ceiling gbm` | skill | 101 (100) | -0.192 | -0.193 | [-0.527, +0.236] | [-0.544, +0.242] |  |
| `/cells/crps/regime: 2018-19/tests/B2 -> gbm_funding` | skill | 101 (100) | +0.133 | +0.123 | [+0.020, +0.233] | [+0.008, +0.231] |  |
| `/cells/crps/regime: 2018-19/tests/B2 -> reachable gbm` | skill | 101 (100) | -0.011 | -0.019 | [-0.126, +0.065] | [-0.130, +0.057] |  |
| `/cells/crps/regime: 2018-19/tests/c_two_part_new -> ceiling gbm` | skill | 101 (100) | -0.539 | -0.541 | [-0.808, -0.150] | [-0.818, -0.142] |  |
| `/cells/crps/regime: 2018-19/tests/c_two_part_new -> reachable gbm` | skill | 101 (100) | -0.306 | -0.316 | [-0.574, -0.139] | [-0.590, -0.149] |  |
| `/cells/crps/regime: 2018-19/tests/gbm_funding -> ceiling gbm` | skill | 101 (100) | -0.374 | -0.361 | [-0.685, +0.062] | [-0.672, +0.064] |  |
| `/cells/crps/regime: 2018-19/tests/gbm_funding -> reachable gbm` | skill | 101 (100) | -0.166 | -0.163 | [-0.281, -0.085] | [-0.284, -0.074] |  |
| `/cells/crps/regime: 2020/headroom/c_two_part_new -> ceiling gbm` | headroom | 251 (251) | +0.153 | +0.153 | [+0.027, +0.361] | [+0.027, +0.361] |  |
| `/cells/crps/regime: 2020/headroom/c_two_part_new -> reachable gbm` | headroom | 251 (251) | +0.019 | +0.019 | [-0.166, +0.229] | [-0.166, +0.229] |  |
| `/cells/crps/regime: 2020/headroom/gbm_funding -> ceiling gbm` | headroom | 251 (251) | +0.033 | +0.033 | [-0.060, +0.104] | [-0.060, +0.104] |  |
| `/cells/crps/regime: 2020/headroom/gbm_funding -> reachable gbm` | headroom | 251 (251) | -0.101 | -0.101 | [-0.286, +0.034] | [-0.286, +0.034] |  |
| `/cells/crps/regime: 2020/tests/B1 -> c_two_part_new` | skill | 251 (251) | +0.028 | +0.028 | [-0.214, +0.196] | [-0.214, +0.196] |  |
| `/cells/crps/regime: 2020/tests/B1 -> ceiling gbm` | skill | 251 (251) | +0.181 | +0.181 | [+0.030, +0.307] | [+0.030, +0.307] |  |
| `/cells/crps/regime: 2020/tests/B1 -> gbm_funding` | skill | 251 (251) | +0.148 | +0.148 | [+0.033, +0.258] | [+0.033, +0.258] |  |
| `/cells/crps/regime: 2020/tests/B1 -> reachable gbm` | skill | 251 (251) | +0.047 | +0.047 | [-0.213, +0.240] | [-0.213, +0.240] |  |
| `/cells/crps/regime: 2020/tests/B2 -> c_two_part_new` | skill | 251 (251) | +0.359 | +0.359 | [+0.151, +0.536] | [+0.151, +0.536] |  |
| `/cells/crps/regime: 2020/tests/B2 -> ceiling gbm` | skill | 251 (251) | +0.460 | +0.460 | [+0.323, +0.579] | [+0.323, +0.579] |  |
| `/cells/crps/regime: 2020/tests/B2 -> gbm_funding` | skill | 251 (251) | +0.438 | +0.438 | [+0.262, +0.582] | [+0.262, +0.582] |  |
| `/cells/crps/regime: 2020/tests/B2 -> reachable gbm` | skill | 251 (251) | +0.371 | +0.371 | [+0.251, +0.493] | [+0.251, +0.493] |  |
| `/cells/crps/regime: 2020/tests/c_two_part_new -> ceiling gbm` | skill | 251 (251) | +0.157 | +0.157 | [+0.032, +0.310] | [+0.032, +0.310] |  |
| `/cells/crps/regime: 2020/tests/c_two_part_new -> reachable gbm` | skill | 251 (251) | +0.019 | +0.019 | [-0.181, +0.215] | [-0.181, +0.215] |  |
| `/cells/crps/regime: 2020/tests/gbm_funding -> ceiling gbm` | skill | 251 (251) | +0.039 | +0.039 | [-0.069, +0.122] | [-0.069, +0.122] |  |
| `/cells/crps/regime: 2020/tests/gbm_funding -> reachable gbm` | skill | 251 (251) | -0.118 | -0.118 | [-0.324, +0.041] | [-0.324, +0.041] |  |
| `/cells/crps/regime: 2021-23/headroom/c_two_part_new -> ceiling gbm` | headroom | 751 (751) | -0.006 | -0.006 | [-0.166, +0.163] | [-0.166, +0.163] |  |
| `/cells/crps/regime: 2021-23/headroom/c_two_part_new -> reachable gbm` | headroom | 751 (751) | -0.059 | -0.059 | [-0.181, +0.065] | [-0.181, +0.065] |  |
| `/cells/crps/regime: 2021-23/headroom/gbm_funding -> ceiling gbm` | headroom | 751 (751) | -0.253 | -0.253 | [-0.466, -0.075] | [-0.466, -0.075] |  |
| `/cells/crps/regime: 2021-23/headroom/gbm_funding -> reachable gbm` | headroom | 751 (751) | -0.307 | -0.307 | [-0.456, -0.183] | [-0.456, -0.183] |  |
| `/cells/crps/regime: 2021-23/tests/B1 -> c_two_part_new` | skill | 751 (751) | -0.255 | -0.255 | [-0.435, -0.097] | [-0.435, -0.097] |  |
| `/cells/crps/regime: 2021-23/tests/B1 -> ceiling gbm` | skill | 751 (751) | -0.260 | -0.260 | [-0.503, -0.060] | [-0.503, -0.060] |  |
| `/cells/crps/regime: 2021-23/tests/B1 -> gbm_funding` | skill | 751 (751) | -0.007 | -0.007 | [-0.129, +0.109] | [-0.129, +0.109] |  |
| `/cells/crps/regime: 2021-23/tests/B1 -> reachable gbm` | skill | 751 (751) | -0.314 | -0.314 | [-0.521, -0.130] | [-0.521, -0.130] |  |
| `/cells/crps/regime: 2021-23/tests/B2 -> c_two_part_new` | skill | 751 (751) | +0.373 | +0.373 | [+0.228, +0.500] | [+0.228, +0.500] |  |
| `/cells/crps/regime: 2021-23/tests/B2 -> ceiling gbm` | skill | 751 (751) | +0.370 | +0.370 | [+0.199, +0.517] | [+0.199, +0.517] |  |
| `/cells/crps/regime: 2021-23/tests/B2 -> gbm_funding` | skill | 751 (751) | +0.496 | +0.496 | [+0.374, +0.605] | [+0.374, +0.605] |  |
| `/cells/crps/regime: 2021-23/tests/B2 -> reachable gbm` | skill | 751 (751) | +0.343 | +0.343 | [+0.227, +0.453] | [+0.227, +0.453] |  |
| `/cells/crps/regime: 2021-23/tests/c_two_part_new -> ceiling gbm` | skill | 751 (751) | -0.005 | -0.005 | [-0.133, +0.126] | [-0.133, +0.126] |  |
| `/cells/crps/regime: 2021-23/tests/c_two_part_new -> reachable gbm` | skill | 751 (751) | -0.047 | -0.047 | [-0.151, +0.050] | [-0.151, +0.050] |  |
| `/cells/crps/regime: 2021-23/tests/gbm_funding -> ceiling gbm` | skill | 751 (751) | -0.251 | -0.251 | [-0.470, -0.074] | [-0.470, -0.074] |  |
| `/cells/crps/regime: 2021-23/tests/gbm_funding -> reachable gbm` | skill | 751 (751) | -0.304 | -0.304 | [-0.459, -0.181] | [-0.459, -0.181] |  |
| `/cells/crps/regime: 2024/headroom/c_two_part_new -> ceiling gbm` | headroom | 250 (250) | +0.095 | +0.095 | [+0.036, +0.151] | [+0.036, +0.151] |  |
| `/cells/crps/regime: 2024/headroom/c_two_part_new -> reachable gbm` | headroom | 250 (250) | +0.112 | +0.112 | [+0.069, +0.171] | [+0.069, +0.171] |  |
| `/cells/crps/regime: 2024/headroom/gbm_funding -> ceiling gbm` | headroom | 250 (250) | +0.087 | +0.087 | [-0.021, +0.146] | [-0.021, +0.146] |  |
| `/cells/crps/regime: 2024/headroom/gbm_funding -> reachable gbm` | headroom | 250 (250) | +0.104 | +0.104 | [+0.032, +0.151] | [+0.032, +0.151] |  |
| `/cells/crps/regime: 2024/tests/B1 -> c_two_part_new` | skill | 250 (250) | +0.154 | +0.154 | [+0.023, +0.254] | [+0.023, +0.254] |  |
| `/cells/crps/regime: 2024/tests/B1 -> ceiling gbm` | skill | 250 (250) | +0.249 | +0.249 | [+0.109, +0.348] | [+0.109, +0.348] |  |
| `/cells/crps/regime: 2024/tests/B1 -> gbm_funding` | skill | 250 (250) | +0.162 | +0.162 | [+0.100, +0.225] | [+0.100, +0.225] |  |
| `/cells/crps/regime: 2024/tests/B1 -> reachable gbm` | skill | 250 (250) | +0.266 | +0.266 | [+0.153, +0.358] | [+0.153, +0.358] |  |
| `/cells/crps/regime: 2024/tests/B2 -> c_two_part_new` | skill | 250 (250) | +0.006 | +0.006 | [-0.108, +0.105] | [-0.108, +0.105] |  |
| `/cells/crps/regime: 2024/tests/B2 -> ceiling gbm` | skill | 250 (250) | +0.117 | +0.117 | [-0.001, +0.220] | [-0.001, +0.220] |  |
| `/cells/crps/regime: 2024/tests/B2 -> gbm_funding` | skill | 250 (250) | +0.015 | +0.015 | [-0.117, +0.168] | [-0.117, +0.168] |  |
| `/cells/crps/regime: 2024/tests/B2 -> reachable gbm` | skill | 250 (250) | +0.137 | +0.137 | [+0.017, +0.254] | [+0.017, +0.254] |  |
| `/cells/crps/regime: 2024/tests/c_two_part_new -> ceiling gbm` | skill | 250 (250) | +0.112 | +0.112 | [+0.041, +0.172] | [+0.041, +0.172] |  |
| `/cells/crps/regime: 2024/tests/c_two_part_new -> reachable gbm` | skill | 250 (250) | +0.132 | +0.132 | [+0.083, +0.187] | [+0.083, +0.187] |  |
| `/cells/crps/regime: 2024/tests/gbm_funding -> ceiling gbm` | skill | 250 (250) | +0.104 | +0.104 | [-0.024, +0.180] | [-0.024, +0.180] |  |
| `/cells/crps/regime: 2024/tests/gbm_funding -> reachable gbm` | skill | 250 (250) | +0.124 | +0.124 | [+0.037, +0.188] | [+0.037, +0.188] |  |
| `/cells/crps/regime: 2025-26/headroom/c_two_part_new -> ceiling gbm` | headroom | 249 (249) | -0.214 | -0.214 | [-0.350, -0.077] | [-0.350, -0.077] |  |
| `/cells/crps/regime: 2025-26/headroom/c_two_part_new -> reachable gbm` | headroom | 249 (249) | -0.054 | -0.054 | [-0.131, +0.016] | [-0.131, +0.016] |  |
| `/cells/crps/regime: 2025-26/headroom/gbm_funding -> ceiling gbm` | headroom | 249 (249) | -0.121 | -0.121 | [-0.270, +0.025] | [-0.270, +0.025] |  |
| `/cells/crps/regime: 2025-26/headroom/gbm_funding -> reachable gbm` | headroom | 249 (249) | +0.038 | +0.038 | [-0.052, +0.123] | [-0.052, +0.123] |  |
| `/cells/crps/regime: 2025-26/tests/B1 -> c_two_part_new` | skill | 249 (249) | +0.278 | +0.278 | [+0.179, +0.372] | [+0.179, +0.372] |  |
| `/cells/crps/regime: 2025-26/tests/B1 -> ceiling gbm` | skill | 249 (249) | +0.065 | +0.065 | [-0.094, +0.212] | [-0.094, +0.212] |  |
| `/cells/crps/regime: 2025-26/tests/B1 -> gbm_funding` | skill | 249 (249) | +0.186 | +0.186 | [+0.099, +0.265] | [+0.099, +0.265] |  |
| `/cells/crps/regime: 2025-26/tests/B1 -> reachable gbm` | skill | 249 (249) | +0.224 | +0.224 | [+0.083, +0.350] | [+0.083, +0.350] |  |
| `/cells/crps/regime: 2025-26/tests/B2 -> c_two_part_new` | skill | 249 (249) | +0.362 | +0.362 | [+0.196, +0.472] | [+0.196, +0.472] |  |
| `/cells/crps/regime: 2025-26/tests/B2 -> ceiling gbm` | skill | 249 (249) | +0.174 | +0.174 | [+0.091, +0.229] | [+0.091, +0.229] |  |
| `/cells/crps/regime: 2025-26/tests/B2 -> gbm_funding` | skill | 249 (249) | +0.281 | +0.281 | [+0.078, +0.414] | [+0.078, +0.414] |  |
| `/cells/crps/regime: 2025-26/tests/B2 -> reachable gbm` | skill | 249 (249) | +0.314 | +0.314 | [+0.181, +0.406] | [+0.181, +0.406] |  |
| `/cells/crps/regime: 2025-26/tests/c_two_part_new -> ceiling gbm` | skill | 249 (249) | -0.296 | -0.296 | [-0.492, -0.104] | [-0.492, -0.104] |  |
| `/cells/crps/regime: 2025-26/tests/c_two_part_new -> reachable gbm` | skill | 249 (249) | -0.075 | -0.075 | [-0.178, +0.022] | [-0.178, +0.022] |  |
| `/cells/crps/regime: 2025-26/tests/gbm_funding -> ceiling gbm` | skill | 249 (249) | -0.149 | -0.149 | [-0.333, +0.031] | [-0.333, +0.031] |  |
| `/cells/crps/regime: 2025-26/tests/gbm_funding -> reachable gbm` | skill | 249 (249) | +0.046 | +0.046 | [-0.064, +0.153] | [-0.064, +0.153] |  |
| `/cells/twcrps/pooled, all targets/headroom/c_two_part_new -> ceiling gbm` | headroom | 1598 (1597) | -0.085 | -0.101 | [-0.138, -0.042] | [-0.149, -0.047] |  |
| `/cells/twcrps/pooled, all targets/headroom/c_two_part_new -> reachable gbm` | headroom | 1598 (1597) | -0.060 | -0.073 | [-0.120, -0.034] | [-0.126, -0.045] |  |
| `/cells/twcrps/pooled, all targets/headroom/gbm_funding -> ceiling gbm` | headroom | 1598 (1597) | -0.028 | -0.031 | [-0.071, +0.028] | [-0.083, +0.030] |  |
| `/cells/twcrps/pooled, all targets/headroom/gbm_funding -> reachable gbm` | headroom | 1598 (1597) | -0.003 | -0.003 | [-0.053, +0.035] | [-0.064, +0.039] |  |
| `/cells/twcrps/pooled, all targets/tests/B1 -> c_two_part_new` | skill | 1598 (1597) | +0.418 | +0.298 | [+0.272, +0.537] | [+0.207, +0.429] |  |
| `/cells/twcrps/pooled, all targets/tests/B1 -> ceiling gbm` | skill | 1598 (1597) | +0.334 | +0.197 | [+0.172, +0.460] | [+0.101, +0.349] |  |
| `/cells/twcrps/pooled, all targets/tests/B1 -> gbm_funding` | skill | 1598 (1597) | +0.362 | +0.228 | [+0.201, +0.486] | [+0.150, +0.346] |  |
| `/cells/twcrps/pooled, all targets/tests/B1 -> reachable gbm` | skill | 1598 (1597) | +0.358 | +0.225 | [+0.182, +0.486] | [+0.130, +0.347] |  |
| `/cells/twcrps/pooled, all targets/tests/B2 -> c_two_part_new` | skill | 1598 (1597) | +0.287 | +0.288 | [+0.162, +0.460] | [+0.158, +0.465] |  |
| `/cells/twcrps/pooled, all targets/tests/B2 -> ceiling gbm` | skill | 1598 (1597) | +0.184 | +0.185 | [+0.044, +0.384] | [+0.042, +0.394] |  |
| `/cells/twcrps/pooled, all targets/tests/B2 -> gbm_funding` | skill | 1598 (1597) | +0.218 | +0.217 | [+0.093, +0.392] | [+0.087, +0.406] |  |
| `/cells/twcrps/pooled, all targets/tests/B2 -> reachable gbm` | skill | 1598 (1597) | +0.214 | +0.214 | [+0.100, +0.366] | [+0.096, +0.373] |  |
| `/cells/twcrps/pooled, all targets/tests/c_two_part_new -> ceiling gbm` | skill | 1598 (1597) | -0.146 | -0.144 | [-0.233, -0.072] | [-0.232, -0.068] |  |
| `/cells/twcrps/pooled, all targets/tests/c_two_part_new -> reachable gbm` | skill | 1598 (1597) | -0.103 | -0.104 | [-0.194, -0.061] | [-0.197, -0.063] |  |
| `/cells/twcrps/pooled, all targets/tests/gbm_funding -> ceiling gbm` | skill | 1598 (1597) | -0.044 | -0.041 | [-0.111, +0.041] | [-0.111, +0.042] |  |
| `/cells/twcrps/pooled, all targets/tests/gbm_funding -> reachable gbm` | skill | 1598 (1597) | -0.005 | -0.004 | [-0.080, +0.053] | [-0.089, +0.051] |  |
| `/cells/twcrps/pooled, ordinary targets/headroom/c_two_part_new -> ceiling gbm` | headroom | 1598 (1597) | -0.105 | -0.136 | [-0.161, -0.040] | [-0.220, -0.040] |  |
| `/cells/twcrps/pooled, ordinary targets/headroom/c_two_part_new -> reachable gbm` | headroom | 1598 (1597) | -0.073 | -0.097 | [-0.144, -0.034] | [-0.170, -0.045] |  |
| `/cells/twcrps/pooled, ordinary targets/headroom/gbm_funding -> ceiling gbm` | headroom | 1598 (1597) | -0.063 | -0.078 | [-0.128, +0.024] | [-0.175, +0.029] |  |
| `/cells/twcrps/pooled, ordinary targets/headroom/gbm_funding -> reachable gbm` | headroom | 1598 (1597) | -0.030 | -0.039 | [-0.088, +0.013] | [-0.108, +0.015] |  |
| `/cells/twcrps/pooled, ordinary targets/tests/B1 -> c_two_part_new` | skill | 1598 (1597) | +0.559 | +0.425 | [+0.347, +0.698] | [+0.329, +0.515] |  |
| `/cells/twcrps/pooled, ordinary targets/tests/B1 -> ceiling gbm` | skill | 1598 (1597) | +0.453 | +0.289 | [+0.224, +0.608] | [+0.172, +0.414] |  |
| `/cells/twcrps/pooled, ordinary targets/tests/B1 -> gbm_funding` | skill | 1598 (1597) | +0.516 | +0.368 | [+0.291, +0.665] | [+0.282, +0.450] |  |
| `/cells/twcrps/pooled, ordinary targets/tests/B1 -> reachable gbm` | skill | 1598 (1597) | +0.486 | +0.329 | [+0.236, +0.643] | [+0.211, +0.422] |  |
| `/cells/twcrps/pooled, ordinary targets/tests/B2 -> c_two_part_new` | skill | 1598 (1597) | +0.330 | +0.330 | [+0.222, +0.437] | [+0.224, +0.441] |  |
| `/cells/twcrps/pooled, ordinary targets/tests/B2 -> ceiling gbm` | skill | 1598 (1597) | +0.170 | +0.172 | [-0.001, +0.342] | [+0.002, +0.353] | yes |
| `/cells/twcrps/pooled, ordinary targets/tests/B2 -> gbm_funding` | skill | 1598 (1597) | +0.265 | +0.263 | [+0.139, +0.383] | [+0.141, +0.380] |  |
| `/cells/twcrps/pooled, ordinary targets/tests/B2 -> reachable gbm` | skill | 1598 (1597) | +0.218 | +0.218 | [+0.124, +0.303] | [+0.122, +0.303] |  |
| `/cells/twcrps/pooled, ordinary targets/tests/c_two_part_new -> ceiling gbm` | skill | 1598 (1597) | -0.239 | -0.237 | [-0.397, -0.078] | [-0.408, -0.068] |  |
| `/cells/twcrps/pooled, ordinary targets/tests/c_two_part_new -> reachable gbm` | skill | 1598 (1597) | -0.166 | -0.168 | [-0.301, -0.073] | [-0.306, -0.074] |  |
| `/cells/twcrps/pooled, ordinary targets/tests/gbm_funding -> ceiling gbm` | skill | 1598 (1597) | -0.129 | -0.124 | [-0.291, +0.040] | [-0.288, +0.046] |  |
| `/cells/twcrps/pooled, ordinary targets/tests/gbm_funding -> reachable gbm` | skill | 1598 (1597) | -0.063 | -0.061 | [-0.168, +0.022] | [-0.171, +0.024] |  |

## 761

Reproduction of the tracked score file: 421 records compared, largest absolute difference 5.33e-15 (headline figures and interval bounds); 0 not in the tracked file.

Records compared: 421; records in which a bound of the interval changes sign: 12.

| record | metric | days (without) | with | without | interval with | interval without | bound changes sign |
|---|---|---|---|---|---|---|---|
| `/groups/anchor_day_type/month_end/grid_crps/vs/B1_recentred/B1` | skill | 149 (149) | +0.362 | +0.362 | [+0.263, +2.483] | [+0.263, +2.483] |  |
| `/groups/anchor_day_type/month_end/grid_crps/vs/B1_recentred/B2` | skill | 149 (149) | +0.279 | +0.279 | [+0.265, +1.030] | [+0.265, +1.030] |  |
| `/groups/anchor_day_type/month_end/grid_crps/vs/spread_mr_b2/B1` | skill | 149 (149) | +0.361 | +0.361 | [+0.260, +2.596] | [+0.260, +2.596] |  |
| `/groups/anchor_day_type/month_end/grid_crps/vs/spread_mr_b2/B2` | skill | 149 (149) | +0.278 | +0.278 | [+0.275, +1.069] | [+0.275, +1.069] |  |
| `/groups/anchor_day_type/month_end/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 149 (149) | +0.029 | +0.029 | [-0.019, +0.163] | [-0.019, +0.163] |  |
| `/groups/anchor_day_type/month_end/grid_crps/vs/spread_mr_ctx/B1` | skill | 149 (149) | +0.356 | +0.356 | [+0.260, +2.543] | [+0.260, +2.543] |  |
| `/groups/anchor_day_type/month_end/grid_crps/vs/spread_mr_ctx/B2` | skill | 149 (149) | +0.272 | +0.272 | [+0.266, +1.020] | [+0.266, +1.020] |  |
| `/groups/anchor_day_type/month_end/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 149 (149) | +0.021 | +0.021 | [+0.010, +0.063] | [+0.010, +0.063] |  |
| `/groups/anchor_day_type/month_end/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 149 (149) | +0.372 | +0.372 | [+0.280, +2.646] | [+0.280, +2.646] |  |
| `/groups/anchor_day_type/month_end/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 149 (149) | +0.291 | +0.291 | [+0.305, +1.106] | [+0.305, +1.106] |  |
| `/groups/anchor_day_type/month_end/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 149 (149) | +0.047 | +0.047 | [-0.001, +0.221] | [-0.001, +0.221] |  |
| `/groups/anchor_day_type/month_end/grid_crps/vs/spread_mr_level10/B1` | skill | 149 (149) | +0.342 | +0.342 | [+0.233, +2.542] | [+0.233, +2.542] |  |
| `/groups/anchor_day_type/month_end/grid_crps/vs/spread_mr_level10/B2` | skill | 149 (149) | +0.256 | +0.256 | [+0.223, +0.990] | [+0.223, +0.990] |  |
| `/groups/anchor_day_type/month_end/upper_tail_twcrps/vs/B1_recentred/B1` | skill | 149 (149) | +0.491 | +0.491 | [+0.070, +2.422] | [+0.070, +2.422] |  |
| `/groups/anchor_day_type/month_end/upper_tail_twcrps/vs/B1_recentred/B2` | skill | 149 (149) | +0.192 | +0.192 | [-0.026, +0.689] | [-0.026, +0.689] |  |
| `/groups/anchor_day_type/month_end/upper_tail_twcrps/vs/spread_mr_b2/B1` | skill | 149 (149) | +0.494 | +0.494 | [+0.107, +2.860] | [+0.107, +2.860] |  |
| `/groups/anchor_day_type/month_end/upper_tail_twcrps/vs/spread_mr_b2/B2` | skill | 149 (149) | +0.196 | +0.196 | [+0.038, +0.483] | [+0.038, +0.483] |  |
| `/groups/anchor_day_type/month_end/upper_tail_twcrps/vs/spread_mr_b2/spread_mr_level10` | skill | 149 (149) | +0.075 | +0.075 | [-0.018, +0.395] | [-0.018, +0.395] |  |
| `/groups/anchor_day_type/month_end/upper_tail_twcrps/vs/spread_mr_ctx/B1` | skill | 149 (149) | +0.468 | +0.468 | [+0.103, +2.582] | [+0.103, +2.582] |  |
| `/groups/anchor_day_type/month_end/upper_tail_twcrps/vs/spread_mr_ctx/B2` | skill | 149 (149) | +0.156 | +0.156 | [+0.016, +0.524] | [+0.016, +0.524] |  |
| `/groups/anchor_day_type/month_end/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10` | skill | 149 (149) | +0.028 | +0.028 | [+0.001, +0.062] | [+0.001, +0.062] |  |
| `/groups/anchor_day_type/month_end/upper_tail_twcrps/vs/spread_mr_ctx_b2/B1` | skill | 149 (149) | +0.509 | +0.509 | [+0.119, +2.894] | [+0.119, +2.894] |  |
| `/groups/anchor_day_type/month_end/upper_tail_twcrps/vs/spread_mr_ctx_b2/B2` | skill | 149 (149) | +0.220 | +0.220 | [+0.049, +0.550] | [+0.049, +0.550] |  |
| `/groups/anchor_day_type/month_end/upper_tail_twcrps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 149 (149) | +0.102 | +0.102 | [-0.005, +0.486] | [-0.005, +0.486] |  |
| `/groups/anchor_day_type/month_end/upper_tail_twcrps/vs/spread_mr_level10/B1` | skill | 149 (149) | +0.453 | +0.453 | [+0.095, +2.584] | [+0.095, +2.584] |  |
| `/groups/anchor_day_type/month_end/upper_tail_twcrps/vs/spread_mr_level10/B2` | skill | 149 (149) | +0.131 | +0.131 | [-0.005, +0.446] | [-0.005, +0.446] |  |
| `/groups/anchor_day_type/ordinary/grid_crps/vs/spread_mr_b2/B1` | skill | 1588 (1588) | +0.104 | +0.104 | [+0.096, +0.381] | [+0.096, +0.381] |  |
| `/groups/anchor_day_type/ordinary/grid_crps/vs/spread_mr_b2/B2` | skill | 1588 (1588) | +0.293 | +0.293 | [+0.537, +1.013] | [+0.537, +1.013] |  |
| `/groups/anchor_day_type/ordinary/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 1588 (1588) | -0.009 | -0.009 | [-0.109, +0.044] | [-0.109, +0.044] |  |
| `/groups/anchor_day_type/ordinary/grid_crps/vs/spread_mr_ctx/B1` | skill | 1588 (1588) | +0.128 | +0.128 | [+0.153, +0.439] | [+0.153, +0.439] |  |
| `/groups/anchor_day_type/ordinary/grid_crps/vs/spread_mr_ctx/B2` | skill | 1588 (1588) | +0.312 | +0.312 | [+0.552, +1.109] | [+0.552, +1.109] |  |
| `/groups/anchor_day_type/ordinary/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 1588 (1588) | +0.018 | +0.018 | [+0.004, +0.071] | [+0.004, +0.071] |  |
| `/groups/anchor_day_type/ordinary/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 1588 (1588) | +0.115 | +0.115 | [+0.111, +0.410] | [+0.111, +0.410] |  |
| `/groups/anchor_day_type/ordinary/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 1588 (1588) | +0.302 | +0.302 | [+0.560, +1.033] | [+0.560, +1.033] |  |
| `/groups/anchor_day_type/ordinary/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 1588 (1588) | +0.003 | +0.003 | [-0.082, +0.072] | [-0.082, +0.072] |  |
| `/groups/anchor_day_type/ordinary/grid_crps/vs/spread_mr_level10/B1` | skill | 1588 (1588) | +0.112 | +0.112 | [+0.135, +0.401] | [+0.135, +0.401] |  |
| `/groups/anchor_day_type/ordinary/grid_crps/vs/spread_mr_level10/B2` | skill | 1588 (1588) | +0.299 | +0.299 | [+0.518, +1.075] | [+0.518, +1.075] |  |
| `/groups/anchor_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_b2/B1` | skill | 1588 (1588) | +0.145 | +0.145 | [+0.068, +0.360] | [+0.068, +0.360] |  |
| `/groups/anchor_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_b2/B2` | skill | 1588 (1588) | +0.176 | +0.176 | [+0.111, +0.339] | [+0.111, +0.339] |  |
| `/groups/anchor_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_b2/spread_mr_level10` | skill | 1588 (1588) | -0.015 | -0.015 | [-0.078, +0.020] | [-0.078, +0.020] |  |
| `/groups/anchor_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_ctx/B1` | skill | 1588 (1588) | +0.178 | +0.178 | [+0.105, +0.409] | [+0.105, +0.409] |  |
| `/groups/anchor_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_ctx/B2` | skill | 1588 (1588) | +0.208 | +0.208 | [+0.127, +0.419] | [+0.127, +0.419] |  |
| `/groups/anchor_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10` | skill | 1588 (1588) | +0.024 | +0.024 | [-0.001, +0.066] | [-0.001, +0.066] |  |
| `/groups/anchor_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_ctx_b2/B1` | skill | 1588 (1588) | +0.160 | +0.160 | [+0.078, +0.381] | [+0.078, +0.381] |  |
| `/groups/anchor_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_ctx_b2/B2` | skill | 1588 (1588) | +0.191 | +0.191 | [+0.125, +0.363] | [+0.125, +0.363] |  |
| `/groups/anchor_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 1588 (1588) | +0.004 | +0.004 | [-0.053, +0.049] | [-0.053, +0.049] |  |
| `/groups/anchor_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_level10/B1` | skill | 1588 (1588) | +0.157 | +0.157 | [+0.092, +0.396] | [+0.092, +0.396] |  |
| `/groups/anchor_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_level10/B2` | skill | 1588 (1588) | +0.188 | +0.188 | [+0.105, +0.391] | [+0.105, +0.391] |  |
| `/groups/anchor_day_type/quarter_end/grid_crps/vs/B1_recentred/B1` | skill | 29 (29) | +0.650 | +0.650 | [+0.215, +29.402] | [+0.215, +29.402] |  |
| `/groups/anchor_day_type/quarter_end/grid_crps/vs/B1_recentred/B2` | skill | 29 (29) | +0.083 | +0.083 | [-1.499, +2.141] | [-1.499, +2.141] |  |
| `/groups/anchor_day_type/quarter_end/grid_crps/vs/spread_mr_b2/B1` | skill | 29 (29) | +0.674 | +0.674 | [+0.099, +17.939] | [+0.099, +17.939] |  |
| `/groups/anchor_day_type/quarter_end/grid_crps/vs/spread_mr_b2/B2` | skill | 29 (29) | +0.145 | +0.145 | [-1.122, +1.869] | [-1.122, +1.869] |  |
| `/groups/anchor_day_type/quarter_end/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 29 (29) | +0.045 | +0.045 | [-0.076, +0.389] | [-0.076, +0.389] |  |
| `/groups/anchor_day_type/quarter_end/grid_crps/vs/spread_mr_ctx/B1` | skill | 29 (29) | +0.652 | +0.652 | [-0.045, +20.685] | [-0.045, +20.685] |  |
| `/groups/anchor_day_type/quarter_end/grid_crps/vs/spread_mr_ctx/B2` | skill | 29 (29) | +0.087 | +0.087 | [-1.270, +1.885] | [-1.270, +1.885] |  |
| `/groups/anchor_day_type/quarter_end/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 29 (29) | -0.019 | -0.019 | [-0.114, -0.004] | [-0.114, -0.004] |  |
| `/groups/anchor_day_type/quarter_end/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 29 (29) | +0.668 | +0.668 | [+0.044, +17.628] | [+0.044, +17.628] |  |
| `/groups/anchor_day_type/quarter_end/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 29 (29) | +0.129 | +0.129 | [-1.180, +1.743] | [-1.180, +1.743] |  |
| `/groups/anchor_day_type/quarter_end/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 29 (29) | +0.027 | +0.027 | [-0.134, +0.395] | [-0.134, +0.395] |  |
| `/groups/anchor_day_type/quarter_end/grid_crps/vs/spread_mr_level10/B1` | skill | 29 (29) | +0.659 | +0.659 | [-0.028, +21.322] | [-0.028, +21.322] |  |
| `/groups/anchor_day_type/quarter_end/grid_crps/vs/spread_mr_level10/B2` | skill | 29 (29) | +0.105 | +0.105 | [-1.282, +2.013] | [-1.282, +2.013] |  |
| `/groups/anchor_day_type/quarter_end/upper_tail_twcrps/vs/B1_recentred/B1` | skill | 29 (29) | +0.826 | +0.826 | [-0.518, +45.202] | [-0.518, +45.202] |  |
| `/groups/anchor_day_type/quarter_end/upper_tail_twcrps/vs/B1_recentred/B2` | skill | 29 (29) | +0.223 | +0.223 | [-0.406, +1.526] | [-0.406, +1.526] |  |
| `/groups/anchor_day_type/quarter_end/upper_tail_twcrps/vs/spread_mr_b2/B1` | skill | 29 (29) | +0.843 | +0.843 | [-0.390, +28.664] | [-0.390, +28.664] |  |
| `/groups/anchor_day_type/quarter_end/upper_tail_twcrps/vs/spread_mr_b2/B2` | skill | 29 (29) | +0.302 | +0.302 | [-0.076, +9.133] | [-0.076, +9.133] |  |
| `/groups/anchor_day_type/quarter_end/upper_tail_twcrps/vs/spread_mr_b2/spread_mr_level10` | skill | 29 (29) | -0.024 | -0.024 | [-0.074, +0.012] | [-0.074, +0.012] |  |
| `/groups/anchor_day_type/quarter_end/upper_tail_twcrps/vs/spread_mr_ctx/B1` | skill | 29 (29) | +0.845 | +0.845 | [-0.368, +28.511] | [-0.368, +28.511] |  |
| `/groups/anchor_day_type/quarter_end/upper_tail_twcrps/vs/spread_mr_ctx/B2` | skill | 29 (29) | +0.308 | +0.308 | [-0.047, +3.364] | [-0.047, +3.364] |  |
| `/groups/anchor_day_type/quarter_end/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10` | skill | 29 (29) | -0.015 | -0.015 | [-0.119, +0.019] | [-0.119, +0.019] |  |
| `/groups/anchor_day_type/quarter_end/upper_tail_twcrps/vs/spread_mr_ctx_b2/B1` | skill | 29 (29) | +0.841 | +0.841 | [-0.389, +28.309] | [-0.389, +28.309] |  |
| `/groups/anchor_day_type/quarter_end/upper_tail_twcrps/vs/spread_mr_ctx_b2/B2` | skill | 29 (29) | +0.290 | +0.290 | [-0.073, +6.188] | [-0.073, +6.188] |  |
| `/groups/anchor_day_type/quarter_end/upper_tail_twcrps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 29 (29) | -0.041 | -0.041 | [-0.227, +0.020] | [-0.227, +0.020] |  |
| `/groups/anchor_day_type/quarter_end/upper_tail_twcrps/vs/spread_mr_level10/B1` | skill | 29 (29) | +0.847 | +0.847 | [-0.377, +28.861] | [-0.377, +28.861] |  |
| `/groups/anchor_day_type/quarter_end/upper_tail_twcrps/vs/spread_mr_level10/B2` | skill | 29 (29) | +0.318 | +0.318 | [-0.057, +4.391] | [-0.057, +4.391] |  |
| `/groups/anchor_day_type/tax_date/grid_crps/vs/B1_recentred/B1` | skill | 89 (88) | +0.744 | +0.386 | [-0.261, +101.363] | [+0.254, +2.859] | yes |
| `/groups/anchor_day_type/tax_date/grid_crps/vs/B1_recentred/B2` | skill | 89 (88) | +0.457 | +0.456 | [+0.526, +2.080] | [+0.508, +2.041] |  |
| `/groups/anchor_day_type/tax_date/grid_crps/vs/spread_mr_b2/B1` | skill | 89 (88) | +0.703 | +0.387 | [-0.217, +92.685] | [+0.182, +3.086] | yes |
| `/groups/anchor_day_type/tax_date/grid_crps/vs/spread_mr_b2/B2` | skill | 89 (88) | +0.369 | +0.457 | [+0.414, +1.581] | [+0.454, +1.946] |  |
| `/groups/anchor_day_type/tax_date/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 89 (88) | +0.086 | +0.052 | [+0.037, +0.418] | [-0.063, +0.344] | yes |
| `/groups/anchor_day_type/tax_date/grid_crps/vs/spread_mr_ctx/B1` | skill | 89 (88) | +0.672 | +0.346 | [-0.380, +124.640] | [+0.073, +4.365] | yes |
| `/groups/anchor_day_type/tax_date/grid_crps/vs/spread_mr_ctx/B2` | skill | 89 (88) | +0.303 | +0.421 | [+0.062, +1.504] | [+0.114, +2.020] |  |
| `/groups/anchor_day_type/tax_date/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 89 (88) | -0.009 | -0.010 | [-0.063, +0.038] | [-0.065, +0.044] |  |
| `/groups/anchor_day_type/tax_date/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 89 (88) | +0.705 | +0.391 | [-0.230, +91.759] | [+0.167, +3.255] | yes |
| `/groups/anchor_day_type/tax_date/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 89 (88) | +0.372 | +0.461 | [+0.404, +1.598] | [+0.420, +1.975] |  |
| `/groups/anchor_day_type/tax_date/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 89 (88) | +0.090 | +0.059 | [+0.037, +0.474] | [-0.036, +0.359] | yes |
| `/groups/anchor_day_type/tax_date/grid_crps/vs/spread_mr_level10/B1` | skill | 89 (88) | +0.675 | +0.353 | [-0.346, +121.789] | [+0.111, +4.048] | yes |
| `/groups/anchor_day_type/tax_date/grid_crps/vs/spread_mr_level10/B2` | skill | 89 (88) | +0.309 | +0.427 | [+0.110, +1.496] | [+0.202, +2.008] |  |
| `/groups/context/ordinary after a risk day/grid_crps/vs/B1_recentred/B1` | skill | 200 (200) | +0.159 | +0.048 | [+0.033, +4.905] | [+0.038, +0.202] |  |
| `/groups/context/ordinary after a risk day/grid_crps/vs/B1_recentred/B2` | skill | 200 (200) | +0.326 | +0.326 | [+0.599, +1.669] | [+0.599, +1.668] |  |
| `/groups/context/ordinary after a risk day/grid_crps/vs/spread_mr_b2/B1` | skill | 200 (200) | +0.078 | -0.019 | [-0.118, +1.486] | [-0.240, +0.062] |  |
| `/groups/context/ordinary after a risk day/grid_crps/vs/spread_mr_b2/B2` | skill | 200 (200) | +0.261 | +0.278 | [+0.481, +1.276] | [+0.508, +1.350] |  |
| `/groups/context/ordinary after a risk day/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 200 (200) | -0.043 | -0.054 | [-0.380, +0.002] | [-0.435, -0.015] | yes |
| `/groups/context/ordinary after a risk day/grid_crps/vs/spread_mr_ctx/B1` | skill | 200 (200) | +0.116 | +0.033 | [+0.009, +1.814] | [-0.020, +0.181] | yes |
| `/groups/context/ordinary after a risk day/grid_crps/vs/spread_mr_ctx/B2` | skill | 200 (200) | +0.291 | +0.315 | [+0.520, +1.490] | [+0.574, +1.591] |  |
| `/groups/context/ordinary after a risk day/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 200 (200) | -0.001 | +0.000 | [-0.055, +0.054] | [-0.052, +0.055] |  |
| `/groups/context/ordinary after a risk day/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 200 (200) | +0.084 | -0.012 | [-0.087, +1.375] | [-0.187, +0.074] |  |
| `/groups/context/ordinary after a risk day/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 200 (200) | +0.265 | +0.284 | [+0.506, +1.271] | [+0.542, +1.346] |  |
| `/groups/context/ordinary after a risk day/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 200 (200) | -0.037 | -0.047 | [-0.262, +0.016] | [-0.293, +0.009] |  |
| `/groups/context/ordinary after a risk day/grid_crps/vs/spread_mr_level10/B1` | skill | 200 (200) | +0.116 | +0.033 | [-0.008, +2.224] | [-0.021, +0.198] |  |
| `/groups/context/ordinary after a risk day/grid_crps/vs/spread_mr_level10/B2` | skill | 200 (200) | +0.291 | +0.315 | [+0.510, +1.493] | [+0.552, +1.600] |  |
| `/groups/context/ordinary after a risk day/upper_tail_twcrps/vs/B1_recentred/B1` | skill | 200 (200) | +0.227 | +0.054 | [-0.009, +6.980] | [+0.012, +0.189] | yes |
| `/groups/context/ordinary after a risk day/upper_tail_twcrps/vs/B1_recentred/B2` | skill | 200 (200) | +0.236 | +0.235 | [+0.074, +1.042] | [+0.075, +1.040] |  |
| `/groups/context/ordinary after a risk day/upper_tail_twcrps/vs/spread_mr_b2/B1` | skill | 200 (200) | +0.131 | -0.021 | [-0.080, +2.104] | [-0.149, +0.038] |  |
| `/groups/context/ordinary after a risk day/upper_tail_twcrps/vs/spread_mr_b2/B2` | skill | 200 (200) | +0.141 | +0.175 | [+0.052, +0.589] | [+0.057, +0.770] |  |
| `/groups/context/ordinary after a risk day/upper_tail_twcrps/vs/spread_mr_b2/spread_mr_level10` | skill | 200 (200) | -0.048 | -0.066 | [-0.288, -0.003] | [-0.426, -0.017] |  |
| `/groups/context/ordinary after a risk day/upper_tail_twcrps/vs/spread_mr_ctx/B1` | skill | 200 (200) | +0.150 | +0.019 | [-0.027, +2.414] | [-0.047, +0.116] |  |
| `/groups/context/ordinary after a risk day/upper_tail_twcrps/vs/spread_mr_ctx/B2` | skill | 200 (200) | +0.160 | +0.207 | [+0.040, +0.802] | [+0.063, +1.030] |  |
| `/groups/context/ordinary after a risk day/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10` | skill | 200 (200) | -0.025 | -0.025 | [-0.075, -0.000] | [-0.070, +0.000] | yes |
| `/groups/context/ordinary after a risk day/upper_tail_twcrps/vs/spread_mr_ctx_b2/B1` | skill | 200 (200) | +0.121 | -0.032 | [-0.085, +1.869] | [-0.154, +0.028] |  |
| `/groups/context/ordinary after a risk day/upper_tail_twcrps/vs/spread_mr_ctx_b2/B2` | skill | 200 (200) | +0.131 | +0.166 | [+0.038, +0.599] | [+0.049, +0.758] |  |
| `/groups/context/ordinary after a risk day/upper_tail_twcrps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 200 (200) | -0.059 | -0.077 | [-0.228, -0.025] | [-0.284, -0.033] |  |
| `/groups/context/ordinary after a risk day/upper_tail_twcrps/vs/spread_mr_level10/B1` | skill | 200 (200) | +0.171 | +0.042 | [-0.009, +3.029] | [-0.006, +0.157] |  |
| `/groups/context/ordinary after a risk day/upper_tail_twcrps/vs/spread_mr_level10/B2` | skill | 200 (200) | +0.180 | +0.226 | [+0.066, +0.808] | [+0.079, +1.014] |  |
| `/groups/context/ordinary after an ordinary day/grid_crps/vs/B1_recentred/B1` | skill | 1276 (1276) | +0.219 | +0.141 | [+0.150, +2.318] | [+0.145, +0.500] |  |
| `/groups/context/ordinary after an ordinary day/grid_crps/vs/B1_recentred/B2` | skill | 1276 (1276) | +0.180 | +0.180 | [+0.057, +0.615] | [+0.056, +0.615] |  |
| `/groups/context/ordinary after an ordinary day/grid_crps/vs/spread_mr_b2/B1` | skill | 1276 (1276) | +0.353 | +0.292 | [+0.355, +1.834] | [+0.315, +0.921] |  |
| `/groups/context/ordinary after an ordinary day/grid_crps/vs/spread_mr_b2/B2` | skill | 1276 (1276) | +0.320 | +0.324 | [+0.398, +0.879] | [+0.406, +0.885] |  |
| `/groups/context/ordinary after an ordinary day/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 1276 (1276) | +0.025 | +0.023 | [-0.040, +0.091] | [-0.042, +0.087] |  |
| `/groups/context/ordinary after an ordinary day/grid_crps/vs/spread_mr_ctx/B1` | skill | 1276 (1276) | +0.348 | +0.289 | [+0.361, +1.896] | [+0.324, +0.916] |  |
| `/groups/context/ordinary after an ordinary day/grid_crps/vs/spread_mr_ctx/B2` | skill | 1276 (1276) | +0.316 | +0.321 | [+0.363, +0.887] | [+0.374, +0.896] |  |
| `/groups/context/ordinary after an ordinary day/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 1276 (1276) | +0.018 | +0.018 | [+0.005, +0.042] | [+0.004, +0.042] |  |
| `/groups/context/ordinary after an ordinary day/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 1276 (1276) | +0.363 | +0.303 | [+0.378, +1.838] | [+0.336, +0.935] |  |
| `/groups/context/ordinary after an ordinary day/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 1276 (1276) | +0.331 | +0.335 | [+0.417, +0.902] | [+0.424, +0.908] |  |
| `/groups/context/ordinary after an ordinary day/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 1276 (1276) | +0.040 | +0.038 | [-0.020, +0.109] | [-0.022, +0.106] |  |
| `/groups/context/ordinary after an ordinary day/grid_crps/vs/spread_mr_level10/B1` | skill | 1276 (1276) | +0.336 | +0.276 | [+0.339, +1.918] | [+0.302, +0.899] |  |
| `/groups/context/ordinary after an ordinary day/grid_crps/vs/spread_mr_level10/B2` | skill | 1276 (1276) | +0.303 | +0.308 | [+0.340, +0.866] | [+0.351, +0.873] |  |
| `/groups/context/ordinary after an ordinary day/upper_tail_twcrps/vs/B1_recentred/B1` | skill | 1276 (1276) | +0.366 | +0.241 | [+0.116, +2.378] | [+0.109, +0.481] |  |
| `/groups/context/ordinary after an ordinary day/upper_tail_twcrps/vs/B1_recentred/B2` | skill | 1276 (1276) | -0.172 | -0.173 | [-0.317, +0.026] | [-0.318, +0.025] |  |
| `/groups/context/ordinary after an ordinary day/upper_tail_twcrps/vs/spread_mr_b2/B1` | skill | 1276 (1276) | +0.574 | +0.498 | [+0.287, +1.889] | [+0.249, +0.888] |  |
| `/groups/context/ordinary after an ordinary day/upper_tail_twcrps/vs/spread_mr_b2/B2` | skill | 1276 (1276) | +0.212 | +0.223 | [+0.051, +0.232] | [+0.058, +0.238] |  |
| `/groups/context/ordinary after an ordinary day/upper_tail_twcrps/vs/spread_mr_b2/spread_mr_level10` | skill | 1276 (1276) | +0.068 | +0.064 | [+0.001, +0.075] | [+0.000, +0.071] |  |
| `/groups/context/ordinary after an ordinary day/upper_tail_twcrps/vs/spread_mr_ctx/B1` | skill | 1276 (1276) | +0.572 | +0.498 | [+0.298, +1.917] | [+0.260, +0.878] |  |
| `/groups/context/ordinary after an ordinary day/upper_tail_twcrps/vs/spread_mr_ctx/B2` | skill | 1276 (1276) | +0.208 | +0.223 | [+0.043, +0.233] | [+0.054, +0.242] |  |
| `/groups/context/ordinary after an ordinary day/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10` | skill | 1276 (1276) | +0.064 | +0.065 | [+0.016, +0.048] | [+0.015, +0.048] |  |
| `/groups/context/ordinary after an ordinary day/upper_tail_twcrps/vs/spread_mr_ctx_b2/B1` | skill | 1276 (1276) | +0.593 | +0.520 | [+0.310, +1.902] | [+0.271, +0.903] |  |
| `/groups/context/ordinary after an ordinary day/upper_tail_twcrps/vs/spread_mr_ctx_b2/B2` | skill | 1276 (1276) | +0.247 | +0.258 | [+0.072, +0.253] | [+0.079, +0.261] |  |
| `/groups/context/ordinary after an ordinary day/upper_tail_twcrps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 1276 (1276) | +0.110 | +0.106 | [+0.019, +0.094] | [+0.018, +0.090] |  |
| `/groups/context/ordinary after an ordinary day/upper_tail_twcrps/vs/spread_mr_level10/B1` | skill | 1276 (1276) | +0.542 | +0.463 | [+0.266, +1.913] | [+0.231, +0.850] |  |
| `/groups/context/ordinary after an ordinary day/upper_tail_twcrps/vs/spread_mr_level10/B2` | skill | 1276 (1276) | +0.154 | +0.170 | [+0.010, +0.198] | [+0.021, +0.207] |  |
| `/groups/context/risk day/grid_crps/vs/B1_recentred/B1` | skill | 383 (383) | -0.001 | -0.001 | [-0.037, +0.019] | [-0.037, +0.019] |  |
| `/groups/context/risk day/grid_crps/vs/B1_recentred/B2` | skill | 383 (383) | +0.256 | +0.256 | [+0.557, +1.955] | [+0.557, +1.955] |  |
| `/groups/context/risk day/grid_crps/vs/spread_mr_b2/B1` | skill | 383 (383) | +0.010 | +0.010 | [-0.185, +0.224] | [-0.185, +0.224] |  |
| `/groups/context/risk day/grid_crps/vs/spread_mr_b2/B2` | skill | 383 (383) | +0.264 | +0.264 | [+0.740, +1.806] | [+0.740, +1.806] |  |
| `/groups/context/risk day/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 383 (383) | -0.023 | -0.023 | [-0.271, +0.071] | [-0.271, +0.071] |  |
| `/groups/context/risk day/grid_crps/vs/spread_mr_ctx/B1` | skill | 383 (383) | +0.052 | +0.052 | [-0.119, +0.480] | [-0.119, +0.480] |  |
| `/groups/context/risk day/grid_crps/vs/spread_mr_ctx/B2` | skill | 383 (383) | +0.295 | +0.295 | [+0.827, +2.020] | [+0.827, +2.020] |  |
| `/groups/context/risk day/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 383 (383) | +0.021 | +0.021 | [-0.111, +0.311] | [-0.111, +0.311] |  |
| `/groups/context/risk day/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 383 (383) | +0.020 | +0.020 | [-0.252, +0.384] | [-0.252, +0.384] |  |
| `/groups/context/risk day/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 383 (383) | +0.272 | +0.272 | [+0.801, +1.767] | [+0.801, +1.767] |  |
| `/groups/context/risk day/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 383 (383) | -0.012 | -0.012 | [-0.261, +0.219] | [-0.261, +0.219] |  |
| `/groups/context/risk day/grid_crps/vs/spread_mr_level10/B1` | skill | 383 (383) | +0.032 | +0.032 | [-0.019, +0.206] | [-0.019, +0.206] |  |
| `/groups/context/risk day/grid_crps/vs/spread_mr_level10/B2` | skill | 383 (383) | +0.281 | +0.281 | [+0.705, +1.995] | [+0.705, +1.995] |  |
| `/groups/context/risk day/upper_tail_twcrps/vs/B1_recentred/B1` | skill | 383 (383) | -0.004 | -0.004 | [-0.046, +0.008] | [-0.046, +0.008] |  |
| `/groups/context/risk day/upper_tail_twcrps/vs/B1_recentred/B2` | skill | 383 (383) | +0.173 | +0.173 | [+0.120, +1.138] | [+0.120, +1.138] |  |
| `/groups/context/risk day/upper_tail_twcrps/vs/spread_mr_b2/B1` | skill | 383 (383) | -0.021 | -0.021 | [-0.210, +0.050] | [-0.210, +0.050] |  |
| `/groups/context/risk day/upper_tail_twcrps/vs/spread_mr_b2/B2` | skill | 383 (383) | +0.159 | +0.159 | [+0.155, +0.963] | [+0.155, +0.963] |  |
| `/groups/context/risk day/upper_tail_twcrps/vs/spread_mr_b2/spread_mr_level10` | skill | 383 (383) | -0.043 | -0.043 | [-0.308, -0.006] | [-0.308, -0.006] |  |
| `/groups/context/risk day/upper_tail_twcrps/vs/spread_mr_ctx/B1` | skill | 383 (383) | +0.031 | +0.031 | [-0.123, +0.368] | [-0.123, +0.368] |  |
| `/groups/context/risk day/upper_tail_twcrps/vs/spread_mr_ctx/B2` | skill | 383 (383) | +0.202 | +0.202 | [+0.201, +1.207] | [+0.201, +1.207] |  |
| `/groups/context/risk day/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10` | skill | 383 (383) | +0.011 | +0.011 | [-0.124, +0.273] | [-0.124, +0.273] |  |
| `/groups/context/risk day/upper_tail_twcrps/vs/spread_mr_ctx_b2/B1` | skill | 383 (383) | -0.009 | -0.009 | [-0.225, +0.232] | [-0.225, +0.232] |  |
| `/groups/context/risk day/upper_tail_twcrps/vs/spread_mr_ctx_b2/B2` | skill | 383 (383) | +0.169 | +0.169 | [+0.164, +0.966] | [+0.164, +0.966] |  |
| `/groups/context/risk day/upper_tail_twcrps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 383 (383) | -0.031 | -0.031 | [-0.238, +0.141] | [-0.238, +0.141] |  |
| `/groups/context/risk day/upper_tail_twcrps/vs/spread_mr_level10/B1` | skill | 383 (383) | +0.021 | +0.021 | [-0.000, +0.119] | [-0.000, +0.119] |  |
| `/groups/context/risk day/upper_tail_twcrps/vs/spread_mr_level10/B2` | skill | 383 (383) | +0.194 | +0.194 | [+0.184, +1.179] | [+0.184, +1.179] |  |
| `/groups/pooled/all decision days/grid_crps/vs/B1_recentred/B1` | skill | 1855 (1854) | +0.148 | +0.085 | [+0.121, +1.834] | [+0.112, +0.305] |  |
| `/groups/pooled/all decision days/grid_crps/vs/B1_recentred/B2` | skill | 1855 (1854) | +0.226 | +0.226 | [+0.309, +0.855] | [+0.306, +0.853] |  |
| `/groups/pooled/all decision days/grid_crps/vs/spread_mr_b2/B1` | skill | 1855 (1854) | +0.222 | +0.170 | [+0.258, +1.387] | [+0.220, +0.608] |  |
| `/groups/pooled/all decision days/grid_crps/vs/spread_mr_b2/B2` | skill | 1855 (1854) | +0.293 | +0.297 | [+0.532, +0.998] | [+0.545, +1.008] |  |
| `/groups/pooled/all decision days/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 1855 (1854) | -0.001 | -0.003 | [-0.078, +0.056] | [-0.082, +0.051] |  |
| `/groups/pooled/all decision days/grid_crps/vs/spread_mr_ctx/B1` | skill | 1855 (1854) | +0.235 | +0.186 | [+0.287, +1.507] | [+0.251, +0.653] |  |
| `/groups/pooled/all decision days/grid_crps/vs/spread_mr_ctx/B2` | skill | 1855 (1854) | +0.305 | +0.311 | [+0.531, +1.062] | [+0.551, +1.078] |  |
| `/groups/pooled/all decision days/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 1855 (1854) | +0.016 | +0.016 | [+0.004, +0.061] | [+0.004, +0.062] |  |
| `/groups/pooled/all decision days/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 1855 (1854) | +0.232 | +0.180 | [+0.266, +1.425] | [+0.232, +0.639] |  |
| `/groups/pooled/all decision days/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 1855 (1854) | +0.302 | +0.306 | [+0.555, +1.019] | [+0.566, +1.027] |  |
| `/groups/pooled/all decision days/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 1855 (1854) | +0.011 | +0.009 | [-0.055, +0.083] | [-0.057, +0.076] |  |
| `/groups/pooled/all decision days/grid_crps/vs/spread_mr_level10/B1` | skill | 1855 (1854) | +0.223 | +0.172 | [+0.275, +1.473] | [+0.237, +0.617] |  |
| `/groups/pooled/all decision days/grid_crps/vs/spread_mr_level10/B2` | skill | 1855 (1854) | +0.294 | +0.300 | [+0.502, +1.036] | [+0.521, +1.051] |  |
| `/groups/pooled/all decision days/upper_tail_twcrps/vs/B1_recentred/B1` | skill | 1855 (1854) | +0.226 | +0.126 | [+0.092, +1.877] | [+0.084, +0.282] |  |
| `/groups/pooled/all decision days/upper_tail_twcrps/vs/B1_recentred/B2` | skill | 1855 (1854) | +0.060 | +0.058 | [-0.089, +0.201] | [-0.090, +0.198] |  |
| `/groups/pooled/all decision days/upper_tail_twcrps/vs/spread_mr_b2/B1` | skill | 1855 (1854) | +0.322 | +0.243 | [+0.201, +1.478] | [+0.166, +0.567] |  |
| `/groups/pooled/all decision days/upper_tail_twcrps/vs/spread_mr_b2/B2` | skill | 1855 (1854) | +0.176 | +0.185 | [+0.107, +0.321] | [+0.120, +0.332] |  |
| `/groups/pooled/all decision days/upper_tail_twcrps/vs/spread_mr_b2/spread_mr_level10` | skill | 1855 (1854) | -0.003 | -0.007 | [-0.048, +0.028] | [-0.052, +0.023] |  |
| `/groups/pooled/all decision days/upper_tail_twcrps/vs/spread_mr_ctx/B1` | skill | 1855 (1854) | +0.340 | +0.267 | [+0.222, +1.545] | [+0.187, +0.610] |  |
| `/groups/pooled/all decision days/upper_tail_twcrps/vs/spread_mr_ctx/B2` | skill | 1855 (1854) | +0.198 | +0.210 | [+0.116, +0.376] | [+0.132, +0.394] |  |
| `/groups/pooled/all decision days/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10` | skill | 1855 (1854) | +0.024 | +0.024 | [+0.001, +0.056] | [+0.001, +0.058] |  |
| `/groups/pooled/all decision days/upper_tail_twcrps/vs/spread_mr_ctx_b2/B1` | skill | 1855 (1854) | +0.335 | +0.258 | [+0.206, +1.509] | [+0.172, +0.593] |  |
| `/groups/pooled/all decision days/upper_tail_twcrps/vs/spread_mr_ctx_b2/B2` | skill | 1855 (1854) | +0.191 | +0.200 | [+0.123, +0.345] | [+0.134, +0.357] |  |
| `/groups/pooled/all decision days/upper_tail_twcrps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 1855 (1854) | +0.016 | +0.012 | [-0.032, +0.059] | [-0.034, +0.051] |  |
| `/groups/pooled/all decision days/upper_tail_twcrps/vs/spread_mr_level10/B1` | skill | 1855 (1854) | +0.324 | +0.249 | [+0.214, +1.520] | [+0.179, +0.578] |  |
| `/groups/pooled/all decision days/upper_tail_twcrps/vs/spread_mr_level10/B2` | skill | 1855 (1854) | +0.178 | +0.191 | [+0.091, +0.350] | [+0.110, +0.367] |  |
| `/groups/pressure_day_type/month_end/grid_crps/vs/spread_mr_b2/B1` | skill | 150 (150) | +0.048 | +0.048 | [-0.125, +0.371] | [-0.125, +0.371] |  |
| `/groups/pressure_day_type/month_end/grid_crps/vs/spread_mr_b2/B2` | skill | 150 (150) | +0.269 | +0.269 | [+0.399, +1.391] | [+0.399, +1.391] |  |
| `/groups/pressure_day_type/month_end/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 150 (150) | -0.020 | -0.020 | [-0.291, +0.110] | [-0.291, +0.110] |  |
| `/groups/pressure_day_type/month_end/grid_crps/vs/spread_mr_ctx/B1` | skill | 150 (150) | +0.057 | +0.057 | [-0.382, +0.578] | [-0.382, +0.578] |  |
| `/groups/pressure_day_type/month_end/grid_crps/vs/spread_mr_ctx/B2` | skill | 150 (150) | +0.276 | +0.276 | [+0.359, +1.644] | [+0.359, +1.644] |  |
| `/groups/pressure_day_type/month_end/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 150 (150) | -0.010 | -0.010 | [-0.457, +0.306] | [-0.457, +0.306] |  |
| `/groups/pressure_day_type/month_end/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 150 (150) | +0.022 | +0.022 | [-0.385, +0.500] | [-0.385, +0.500] |  |
| `/groups/pressure_day_type/month_end/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 150 (150) | +0.249 | +0.249 | [+0.366, +1.270] | [+0.366, +1.270] |  |
| `/groups/pressure_day_type/month_end/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 150 (150) | -0.047 | -0.047 | [-0.456, +0.229] | [-0.456, +0.229] |  |
| `/groups/pressure_day_type/month_end/grid_crps/vs/spread_mr_level10/B1` | skill | 150 (150) | +0.066 | +0.066 | [+0.020, +0.333] | [+0.020, +0.333] |  |
| `/groups/pressure_day_type/month_end/grid_crps/vs/spread_mr_level10/B2` | skill | 150 (150) | +0.283 | +0.283 | [+0.320, +1.597] | [+0.320, +1.597] |  |
| `/groups/pressure_day_type/ordinary/grid_crps/vs/B1_recentred/B1` | skill | 1590 (1590) | +0.195 | +0.117 | [+0.134, +2.234] | [+0.128, +0.391] |  |
| `/groups/pressure_day_type/ordinary/grid_crps/vs/B1_recentred/B2` | skill | 1590 (1590) | +0.222 | +0.222 | [+0.220, +0.730] | [+0.220, +0.730] |  |
| `/groups/pressure_day_type/ordinary/grid_crps/vs/spread_mr_b2/B1` | skill | 1590 (1590) | +0.285 | +0.222 | [+0.289, +1.596] | [+0.246, +0.710] |  |
| `/groups/pressure_day_type/ordinary/grid_crps/vs/spread_mr_b2/B2` | skill | 1590 (1590) | +0.309 | +0.315 | [+0.455, +0.898] | [+0.469, +0.909] |  |
| `/groups/pressure_day_type/ordinary/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 1590 (1590) | -0.001 | -0.004 | [-0.079, +0.054] | [-0.084, +0.048] |  |
| `/groups/pressure_day_type/ordinary/grid_crps/vs/spread_mr_ctx/B1` | skill | 1590 (1590) | +0.296 | +0.237 | [+0.318, +1.659] | [+0.281, +0.740] |  |
| `/groups/pressure_day_type/ordinary/grid_crps/vs/spread_mr_ctx/B2` | skill | 1590 (1590) | +0.320 | +0.328 | [+0.448, +0.947] | [+0.469, +0.964] |  |
| `/groups/pressure_day_type/ordinary/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 1590 (1590) | +0.015 | +0.015 | [+0.007, +0.035] | [+0.007, +0.035] |  |
| `/groups/pressure_day_type/ordinary/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 1590 (1590) | +0.296 | +0.234 | [+0.310, +1.593] | [+0.268, +0.728] |  |
| `/groups/pressure_day_type/ordinary/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 1590 (1590) | +0.320 | +0.325 | [+0.475, +0.923] | [+0.490, +0.932] |  |
| `/groups/pressure_day_type/ordinary/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 1590 (1590) | +0.014 | +0.011 | [-0.053, +0.074] | [-0.058, +0.068] |  |
| `/groups/pressure_day_type/ordinary/grid_crps/vs/spread_mr_level10/B1` | skill | 1590 (1590) | +0.286 | +0.226 | [+0.298, +1.682] | [+0.260, +0.725] |  |
| `/groups/pressure_day_type/ordinary/grid_crps/vs/spread_mr_level10/B2` | skill | 1590 (1590) | +0.310 | +0.318 | [+0.428, +0.927] | [+0.449, +0.945] |  |
| `/groups/pressure_day_type/ordinary/upper_tail_twcrps/vs/B1_recentred/B1` | skill | 1590 (1590) | +0.319 | +0.192 | [+0.103, +2.288] | [+0.096, +0.372] |  |
| `/groups/pressure_day_type/ordinary/upper_tail_twcrps/vs/B1_recentred/B2` | skill | 1590 (1590) | -0.015 | -0.015 | [-0.169, +0.101] | [-0.170, +0.101] |  |
| `/groups/pressure_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_b2/B1` | skill | 1590 (1590) | +0.459 | +0.371 | [+0.233, +1.680] | [+0.199, +0.681] |  |
| `/groups/pressure_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_b2/B2` | skill | 1590 (1590) | +0.194 | +0.210 | [+0.072, +0.255] | [+0.085, +0.269] |  |
| `/groups/pressure_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_b2/spread_mr_level10` | skill | 1590 (1590) | +0.016 | +0.009 | [-0.024, +0.040] | [-0.028, +0.034] |  |
| `/groups/pressure_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_ctx/B1` | skill | 1590 (1590) | +0.468 | +0.387 | [+0.253, +1.684] | [+0.218, +0.685] |  |
| `/groups/pressure_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_ctx/B2` | skill | 1590 (1590) | +0.208 | +0.230 | [+0.071, +0.276] | [+0.092, +0.297] |  |
| `/groups/pressure_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10` | skill | 1590 (1590) | +0.033 | +0.034 | [+0.008, +0.033] | [+0.008, +0.033] |  |
| `/groups/pressure_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_ctx_b2/B1` | skill | 1590 (1590) | +0.473 | +0.388 | [+0.250, +1.667] | [+0.216, +0.691] |  |
| `/groups/pressure_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_ctx_b2/B2` | skill | 1590 (1590) | +0.215 | +0.231 | [+0.087, +0.275] | [+0.101, +0.288] |  |
| `/groups/pressure_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 1590 (1590) | +0.042 | +0.036 | [-0.010, +0.058] | [-0.014, +0.052] |  |
| `/groups/pressure_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_level10/B1` | skill | 1590 (1590) | +0.450 | +0.365 | [+0.231, +1.699] | [+0.198, +0.673] |  |
| `/groups/pressure_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_level10/B2` | skill | 1590 (1590) | +0.180 | +0.202 | [+0.051, +0.254] | [+0.071, +0.273] |  |
| `/groups/pressure_day_type/quarter_end/grid_crps/vs/spread_mr_b2/B1` | skill | 30 (30) | +0.098 | +0.098 | [-0.244, +2.649] | [-0.244, +2.649] |  |
| `/groups/pressure_day_type/quarter_end/grid_crps/vs/spread_mr_b2/B2` | skill | 30 (30) | +0.170 | +0.170 | [-0.241, +3.336] | [-0.241, +3.336] |  |
| `/groups/pressure_day_type/quarter_end/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 30 (30) | +0.126 | +0.126 | [-0.146, +4.224] | [-0.146, +4.224] |  |
| `/groups/pressure_day_type/quarter_end/grid_crps/vs/spread_mr_ctx/B1` | skill | 30 (30) | +0.067 | +0.067 | [-0.145, +1.632] | [-0.145, +1.632] |  |
| `/groups/pressure_day_type/quarter_end/grid_crps/vs/spread_mr_ctx/B2` | skill | 30 (30) | +0.142 | +0.142 | [-1.103, +3.420] | [-1.103, +3.420] |  |
| `/groups/pressure_day_type/quarter_end/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 30 (30) | +0.097 | +0.097 | [-0.110, +2.334] | [-0.110, +2.334] |  |
| `/groups/pressure_day_type/quarter_end/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 30 (30) | +0.143 | +0.143 | [-0.322, +3.748] | [-0.322, +3.748] |  |
| `/groups/pressure_day_type/quarter_end/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 30 (30) | +0.211 | +0.211 | [+0.298, +3.793] | [+0.298, +3.793] |  |
| `/groups/pressure_day_type/quarter_end/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 30 (30) | +0.170 | +0.170 | [-0.265, +4.657] | [-0.265, +4.657] |  |
| `/groups/pressure_day_type/quarter_end/grid_crps/vs/spread_mr_level10/B1` | skill | 30 (30) | -0.032 | -0.032 | [-0.533, +0.022] | [-0.533, +0.022] |  |
| `/groups/pressure_day_type/quarter_end/grid_crps/vs/spread_mr_level10/B2` | skill | 30 (30) | +0.050 | +0.050 | [-3.084, +3.072] | [-3.084, +3.072] |  |
| `/groups/pressure_day_type/tax_date/grid_crps/vs/B1_recentred/B1` | skill | 89 (89) | +0.002 | +0.002 | [-0.149, +0.118] | [-0.149, +0.118] |  |
| `/groups/pressure_day_type/tax_date/grid_crps/vs/B1_recentred/B2` | skill | 89 (89) | +0.291 | +0.291 | [+1.323, +3.936] | [+1.323, +3.936] |  |
| `/groups/pressure_day_type/tax_date/grid_crps/vs/spread_mr_b2/B1` | skill | 89 (89) | -0.030 | -0.030 | [-0.349, -0.021] | [-0.349, -0.021] |  |
| `/groups/pressure_day_type/tax_date/grid_crps/vs/spread_mr_b2/B2` | skill | 89 (89) | +0.268 | +0.268 | [+1.200, +3.777] | [+1.200, +3.777] |  |
| `/groups/pressure_day_type/tax_date/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 89 (89) | -0.047 | -0.047 | [-0.553, -0.073] | [-0.553, -0.073] |  |
| `/groups/pressure_day_type/tax_date/grid_crps/vs/spread_mr_ctx/B1` | skill | 89 (89) | +0.023 | +0.023 | [-0.261, +0.771] | [-0.261, +0.771] |  |
| `/groups/pressure_day_type/tax_date/grid_crps/vs/spread_mr_ctx/B2` | skill | 89 (89) | +0.306 | +0.306 | [+1.279, +4.434] | [+1.279, +4.434] |  |
| `/groups/pressure_day_type/tax_date/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 89 (89) | +0.007 | +0.007 | [-0.182, +0.643] | [-0.182, +0.643] |  |
| `/groups/pressure_day_type/tax_date/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 89 (89) | -0.019 | -0.019 | [-0.437, +0.244] | [-0.437, +0.244] |  |
| `/groups/pressure_day_type/tax_date/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 89 (89) | +0.277 | +0.277 | [+1.209, +3.847] | [+1.209, +3.847] |  |
| `/groups/pressure_day_type/tax_date/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 89 (89) | -0.035 | -0.035 | [-0.413, +0.053] | [-0.413, +0.053] |  |
| `/groups/pressure_day_type/tax_date/grid_crps/vs/spread_mr_level10/B1` | skill | 89 (89) | +0.016 | +0.016 | [-0.088, +0.357] | [-0.088, +0.357] |  |
| `/groups/pressure_day_type/tax_date/grid_crps/vs/spread_mr_level10/B2` | skill | 89 (89) | +0.301 | +0.301 | [+1.341, +4.083] | [+1.341, +4.083] |  |
| `/groups/regime/2018-19/grid_crps/vs/B1_recentred/B1` | skill | 361 (361) | +0.248 | +0.129 | [+0.334, +9.783] | [+0.331, +1.265] |  |
| `/groups/regime/2018-19/grid_crps/vs/B1_recentred/B2` | skill | 361 (361) | +0.024 | +0.024 | [-0.535, +0.666] | [-0.538, +0.665] |  |
| `/groups/regime/2018-19/grid_crps/vs/spread_mr_b2/B1` | skill | 361 (361) | +0.350 | +0.258 | [+0.870, +8.442] | [+0.755, +2.697] |  |
| `/groups/regime/2018-19/grid_crps/vs/spread_mr_b2/B2` | skill | 361 (361) | +0.156 | +0.168 | [+0.320, +1.156] | [+0.406, +1.190] |  |
| `/groups/regime/2018-19/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 361 (361) | +0.016 | +0.011 | [-0.071, +0.185] | [-0.085, +0.155] |  |
| `/groups/regime/2018-19/grid_crps/vs/spread_mr_ctx/B1` | skill | 361 (361) | +0.362 | +0.276 | [+0.921, +8.370] | [+0.826, +2.759] |  |
| `/groups/regime/2018-19/grid_crps/vs/spread_mr_ctx/B2` | skill | 361 (361) | +0.172 | +0.189 | [+0.358, +1.318] | [+0.442, +1.375] |  |
| `/groups/regime/2018-19/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 361 (361) | +0.035 | +0.035 | [+0.048, +0.288] | [+0.047, +0.288] |  |
| `/groups/regime/2018-19/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 361 (361) | +0.368 | +0.279 | [+0.925, +8.417] | [+0.826, +2.798] |  |
| `/groups/regime/2018-19/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 361 (361) | +0.180 | +0.192 | [+0.450, +1.281] | [+0.513, +1.318] |  |
| `/groups/regime/2018-19/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 361 (361) | +0.044 | +0.039 | [+0.016, +0.366] | [+0.008, +0.310] |  |
| `/groups/regime/2018-19/grid_crps/vs/spread_mr_level10/B1` | skill | 361 (361) | +0.339 | +0.249 | [+0.853, +8.419] | [+0.743, +2.649] |  |
| `/groups/regime/2018-19/grid_crps/vs/spread_mr_level10/B2` | skill | 361 (361) | +0.142 | +0.159 | [+0.181, +1.193] | [+0.294, +1.245] |  |
| `/groups/regime/2018-19/upper_tail_twcrps/vs/B1_recentred/B1` | skill | 361 (361) | +0.273 | +0.145 | [+0.337, +9.888] | [+0.335, +1.275] |  |
| `/groups/regime/2018-19/upper_tail_twcrps/vs/B1_recentred/B2` | skill | 361 (361) | -0.007 | -0.007 | [-0.709, +0.480] | [-0.712, +0.478] |  |
| `/groups/regime/2018-19/upper_tail_twcrps/vs/spread_mr_b2/B1` | skill | 361 (361) | +0.362 | +0.261 | [+0.748, +8.442] | [+0.639, +2.651] |  |
| `/groups/regime/2018-19/upper_tail_twcrps/vs/spread_mr_b2/B2` | skill | 361 (361) | +0.116 | +0.130 | [+0.121, +0.843] | [+0.205, +0.883] |  |
| `/groups/regime/2018-19/upper_tail_twcrps/vs/spread_mr_b2/spread_mr_level10` | skill | 361 (361) | +0.024 | +0.018 | [-0.033, +0.195] | [-0.044, +0.164] |  |
| `/groups/regime/2018-19/upper_tail_twcrps/vs/spread_mr_ctx/B1` | skill | 361 (361) | +0.373 | +0.279 | [+0.787, +8.259] | [+0.690, +2.646] |  |
| `/groups/regime/2018-19/upper_tail_twcrps/vs/spread_mr_ctx/B2` | skill | 361 (361) | +0.131 | +0.151 | [+0.155, +0.978] | [+0.237, +1.046] |  |
| `/groups/regime/2018-19/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10` | skill | 361 (361) | +0.041 | +0.041 | [+0.057, +0.295] | [+0.057, +0.295] |  |
| `/groups/regime/2018-19/upper_tail_twcrps/vs/spread_mr_ctx_b2/B1` | skill | 361 (361) | +0.382 | +0.285 | [+0.806, +8.462] | [+0.709, +2.738] |  |
| `/groups/regime/2018-19/upper_tail_twcrps/vs/spread_mr_ctx_b2/B2` | skill | 361 (361) | +0.144 | +0.158 | [+0.254, +0.971] | [+0.310, +1.012] |  |
| `/groups/regime/2018-19/upper_tail_twcrps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 361 (361) | +0.054 | +0.050 | [+0.047, +0.388] | [+0.042, +0.324] |  |
| `/groups/regime/2018-19/upper_tail_twcrps/vs/spread_mr_level10/B1` | skill | 361 (361) | +0.346 | +0.247 | [+0.710, +8.287] | [+0.601, +2.526] |  |
| `/groups/regime/2018-19/upper_tail_twcrps/vs/spread_mr_level10/B2` | skill | 361 (361) | +0.095 | +0.114 | [-0.036, +0.840] | [+0.081, +0.903] | yes |
| `/groups/regime/2020/grid_crps/vs/B1_recentred/B1` | skill | 251 (251) | -0.011 | -0.011 | [-0.040, +0.001] | [-0.040, +0.001] |  |
| `/groups/regime/2020/grid_crps/vs/B1_recentred/B2` | skill | 251 (251) | +0.404 | +0.404 | [+0.270, +2.780] | [+0.270, +2.780] |  |
| `/groups/regime/2020/grid_crps/vs/spread_mr_b2/B1` | skill | 251 (251) | +0.027 | +0.027 | [-0.132, +0.307] | [-0.132, +0.307] |  |
| `/groups/regime/2020/grid_crps/vs/spread_mr_b2/B2` | skill | 251 (251) | +0.426 | +0.426 | [+0.392, +2.876] | [+0.392, +2.876] |  |
| `/groups/regime/2020/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 251 (251) | -0.035 | -0.035 | [-0.192, +0.014] | [-0.192, +0.014] |  |
| `/groups/regime/2020/grid_crps/vs/spread_mr_ctx/B1` | skill | 251 (251) | -0.004 | -0.004 | [-0.144, +0.253] | [-0.144, +0.253] |  |
| `/groups/regime/2020/grid_crps/vs/spread_mr_ctx/B2` | skill | 251 (251) | +0.409 | +0.409 | [+0.313, +2.851] | [+0.313, +2.851] |  |
| `/groups/regime/2020/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 251 (251) | -0.067 | -0.067 | [-0.150, -0.063] | [-0.150, -0.063] |  |
| `/groups/regime/2020/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 251 (251) | -0.021 | -0.021 | [-0.226, +0.203] | [-0.226, +0.203] |  |
| `/groups/regime/2020/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 251 (251) | +0.398 | +0.398 | [+0.327, +2.704] | [+0.327, +2.704] |  |
| `/groups/regime/2020/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 251 (251) | -0.087 | -0.087 | [-0.304, -0.048] | [-0.304, -0.048] |  |
| `/groups/regime/2020/grid_crps/vs/spread_mr_level10/B1` | skill | 251 (251) | +0.060 | +0.060 | [-0.035, +0.447] | [-0.035, +0.447] |  |
| `/groups/regime/2020/grid_crps/vs/spread_mr_level10/B2` | skill | 251 (251) | +0.446 | +0.446 | [+0.398, +3.033] | [+0.398, +3.033] |  |
| `/groups/regime/2020/upper_tail_twcrps/vs/B1_recentred/B1` | skill | 251 (251) | +0.009 | +0.009 | [+0.002, +0.011] | [+0.002, +0.011] |  |
| `/groups/regime/2020/upper_tail_twcrps/vs/B1_recentred/B2` | skill | 251 (251) | +0.398 | +0.398 | [-0.069, +0.881] | [-0.069, +0.881] |  |
| `/groups/regime/2020/upper_tail_twcrps/vs/spread_mr_b2/B1` | skill | 251 (251) | +0.132 | +0.132 | [-0.112, +1.713] | [-0.112, +1.713] |  |
| `/groups/regime/2020/upper_tail_twcrps/vs/spread_mr_b2/B2` | skill | 251 (251) | +0.473 | +0.473 | [+0.248, +0.997] | [+0.248, +0.997] |  |
| `/groups/regime/2020/upper_tail_twcrps/vs/spread_mr_b2/spread_mr_level10` | skill | 251 (251) | -0.095 | -0.095 | [-0.108, -0.020] | [-0.108, -0.020] |  |
| `/groups/regime/2020/upper_tail_twcrps/vs/spread_mr_ctx/B1` | skill | 251 (251) | +0.104 | +0.104 | [-0.125, +1.059] | [-0.125, +1.059] |  |
| `/groups/regime/2020/upper_tail_twcrps/vs/spread_mr_ctx/B2` | skill | 251 (251) | +0.456 | +0.456 | [+0.196, +0.998] | [+0.196, +0.998] |  |
| `/groups/regime/2020/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10` | skill | 251 (251) | -0.130 | -0.130 | [-0.114, -0.040] | [-0.114, -0.040] |  |
| `/groups/regime/2020/upper_tail_twcrps/vs/spread_mr_ctx_b2/B1` | skill | 251 (251) | +0.059 | +0.059 | [-0.160, +0.995] | [-0.160, +0.995] |  |
| `/groups/regime/2020/upper_tail_twcrps/vs/spread_mr_ctx_b2/B2` | skill | 251 (251) | +0.429 | +0.429 | [+0.185, +0.936] | [+0.185, +0.936] |  |
| `/groups/regime/2020/upper_tail_twcrps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 251 (251) | -0.187 | -0.187 | [-0.156, -0.069] | [-0.156, -0.069] |  |
| `/groups/regime/2020/upper_tail_twcrps/vs/spread_mr_level10/B1` | skill | 251 (251) | +0.207 | +0.207 | [-0.056, +2.336] | [-0.056, +2.336] |  |
| `/groups/regime/2020/upper_tail_twcrps/vs/spread_mr_level10/B2` | skill | 251 (251) | +0.519 | +0.519 | [+0.277, +1.080] | [+0.277, +1.080] |  |
| `/groups/regime/2021-23/grid_crps/vs/B1_recentred/B1` | skill | 748 (748) | +0.027 | +0.027 | [+0.006, +0.036] | [+0.006, +0.036] |  |
| `/groups/regime/2021-23/grid_crps/vs/B1_recentred/B2` | skill | 748 (748) | +0.537 | +0.537 | [+0.509, +1.142] | [+0.509, +1.142] |  |
| `/groups/regime/2021-23/grid_crps/vs/spread_mr_b2/B1` | skill | 748 (748) | -0.030 | -0.030 | [-0.056, +0.012] | [-0.056, +0.012] |  |
| `/groups/regime/2021-23/grid_crps/vs/spread_mr_b2/B2` | skill | 748 (748) | +0.510 | +0.510 | [+0.480, +1.085] | [+0.480, +1.085] |  |
| `/groups/regime/2021-23/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 748 (748) | -0.004 | -0.004 | [-0.014, +0.007] | [-0.014, +0.007] |  |
| `/groups/regime/2021-23/grid_crps/vs/spread_mr_ctx/B1` | skill | 748 (748) | -0.029 | -0.029 | [-0.058, +0.014] | [-0.058, +0.014] |  |
| `/groups/regime/2021-23/grid_crps/vs/spread_mr_ctx/B2` | skill | 748 (748) | +0.510 | +0.510 | [+0.485, +1.078] | [+0.485, +1.078] |  |
| `/groups/regime/2021-23/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 748 (748) | -0.003 | -0.003 | [-0.013, +0.006] | [-0.013, +0.006] |  |
| `/groups/regime/2021-23/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 748 (748) | -0.038 | -0.038 | [-0.067, +0.012] | [-0.067, +0.012] |  |
| `/groups/regime/2021-23/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 748 (748) | +0.506 | +0.506 | [+0.484, +1.068] | [+0.484, +1.068] |  |
| `/groups/regime/2021-23/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 748 (748) | -0.012 | -0.012 | [-0.025, +0.006] | [-0.025, +0.006] |  |
| `/groups/regime/2021-23/grid_crps/vs/spread_mr_level10/B1` | skill | 748 (748) | -0.026 | -0.026 | [-0.050, +0.011] | [-0.050, +0.011] |  |
| `/groups/regime/2021-23/grid_crps/vs/spread_mr_level10/B2` | skill | 748 (748) | +0.512 | +0.512 | [+0.480, +1.090] | [+0.480, +1.090] |  |
| `/groups/regime/2021-23/upper_tail_twcrps/vs/spread_mr_ctx/B1` | skill | 748 (748) | -0.922 | -0.922 | [-0.016, -0.004] | [-0.016, -0.004] |  |
| `/groups/regime/2021-23/upper_tail_twcrps/vs/spread_mr_ctx/B2` | skill | 748 (748) | -4.614 | -4.614 | [-0.028, -0.007] | [-0.028, -0.007] |  |
| `/groups/regime/2021-23/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10` | skill | 748 (748) | -0.377 | -0.377 | [-0.009, -0.001] | [-0.009, -0.001] |  |
| `/groups/regime/2021-23/upper_tail_twcrps/vs/spread_mr_ctx_b2/B1` | skill | 748 (748) | -0.818 | -0.818 | [-0.014, -0.003] | [-0.014, -0.003] |  |
| `/groups/regime/2021-23/upper_tail_twcrps/vs/spread_mr_ctx_b2/B2` | skill | 748 (748) | -4.312 | -4.312 | [-0.025, -0.007] | [-0.025, -0.007] |  |
| `/groups/regime/2021-23/upper_tail_twcrps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 748 (748) | -0.303 | -0.303 | [-0.008, -0.000] | [-0.008, -0.000] |  |
| `/groups/regime/2021-23/upper_tail_twcrps/vs/spread_mr_level10/B1` | skill | 748 (748) | -0.396 | -0.396 | [-0.010, -0.001] | [-0.010, -0.001] |  |
| `/groups/regime/2021-23/upper_tail_twcrps/vs/spread_mr_level10/B2` | skill | 748 (748) | -3.077 | -3.077 | [-0.031, -0.004] | [-0.031, -0.004] |  |
| `/groups/regime/2024/grid_crps/vs/B1_recentred/B1` | skill | 250 (250) | +0.080 | +0.080 | [+0.061, +0.257] | [+0.061, +0.257] |  |
| `/groups/regime/2024/grid_crps/vs/B1_recentred/B2` | skill | 250 (250) | -0.065 | -0.065 | [-0.439, +0.146] | [-0.439, +0.146] |  |
| `/groups/regime/2024/grid_crps/vs/spread_mr_b2/B1` | skill | 250 (250) | +0.234 | +0.234 | [+0.184, +0.818] | [+0.184, +0.818] |  |
| `/groups/regime/2024/grid_crps/vs/spread_mr_b2/B2` | skill | 250 (250) | +0.114 | +0.114 | [+0.014, +0.319] | [+0.014, +0.319] |  |
| `/groups/regime/2024/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 250 (250) | +0.042 | +0.042 | [+0.005, +0.110] | [+0.005, +0.110] |  |
| `/groups/regime/2024/grid_crps/vs/spread_mr_ctx/B1` | skill | 250 (250) | +0.222 | +0.222 | [+0.181, +0.742] | [+0.181, +0.742] |  |
| `/groups/regime/2024/grid_crps/vs/spread_mr_ctx/B2` | skill | 250 (250) | +0.099 | +0.099 | [-0.041, +0.329] | [-0.041, +0.329] |  |
| `/groups/regime/2024/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 250 (250) | +0.026 | +0.026 | [+0.010, +0.059] | [+0.010, +0.059] |  |
| `/groups/regime/2024/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 250 (250) | +0.250 | +0.250 | [+0.202, +0.852] | [+0.202, +0.852] |  |
| `/groups/regime/2024/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 250 (250) | +0.133 | +0.133 | [+0.040, +0.341] | [+0.040, +0.341] |  |
| `/groups/regime/2024/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 250 (250) | +0.062 | +0.062 | [+0.023, +0.143] | [+0.023, +0.143] |  |
| `/groups/regime/2024/grid_crps/vs/spread_mr_level10/B1` | skill | 250 (250) | +0.201 | +0.201 | [+0.159, +0.712] | [+0.159, +0.712] |  |
| `/groups/regime/2024/grid_crps/vs/spread_mr_level10/B2` | skill | 250 (250) | +0.075 | +0.075 | [-0.073, +0.296] | [-0.073, +0.296] |  |
| `/groups/regime/2025-26/grid_crps/vs/B1_recentred/B1` | skill | 249 (249) | +0.083 | +0.083 | [+0.159, +0.523] | [+0.159, +0.523] |  |
| `/groups/regime/2025-26/grid_crps/vs/B1_recentred/B2` | skill | 249 (249) | +0.185 | +0.185 | [-0.241, +2.098] | [-0.241, +2.098] |  |
| `/groups/regime/2025-26/grid_crps/vs/spread_mr_b2/B1` | skill | 249 (249) | +0.145 | +0.145 | [-0.014, +0.977] | [-0.014, +0.977] |  |
| `/groups/regime/2025-26/grid_crps/vs/spread_mr_b2/B2` | skill | 249 (249) | +0.240 | +0.240 | [+0.182, +2.292] | [+0.182, +2.292] |  |
| `/groups/regime/2025-26/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 249 (249) | -0.035 | -0.035 | [-0.693, +0.284] | [-0.693, +0.284] |  |
| `/groups/regime/2025-26/grid_crps/vs/spread_mr_ctx/B1` | skill | 249 (249) | +0.206 | +0.206 | [+0.342, +1.169] | [+0.342, +1.169] |  |
| `/groups/regime/2025-26/grid_crps/vs/spread_mr_ctx/B2` | skill | 249 (249) | +0.294 | +0.294 | [+0.078, +2.761] | [+0.078, +2.761] |  |
| `/groups/regime/2025-26/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 249 (249) | +0.038 | +0.038 | [+0.040, +0.191] | [+0.040, +0.191] |  |
| `/groups/regime/2025-26/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 249 (249) | +0.170 | +0.170 | [+0.065, +1.094] | [+0.065, +1.094] |  |
| `/groups/regime/2025-26/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 249 (249) | +0.262 | +0.262 | [+0.228, +2.449] | [+0.228, +2.449] |  |
| `/groups/regime/2025-26/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 249 (249) | -0.005 | -0.005 | [-0.602, +0.347] | [-0.602, +0.347] |  |
| `/groups/regime/2025-26/grid_crps/vs/spread_mr_level10/B1` | skill | 249 (249) | +0.174 | +0.174 | [+0.276, +0.985] | [+0.276, +0.985] |  |
| `/groups/regime/2025-26/grid_crps/vs/spread_mr_level10/B2` | skill | 249 (249) | +0.266 | +0.266 | [-0.005, +2.585] | [-0.005, +2.585] |  |
| `/groups/regime/2025-26/upper_tail_twcrps/vs/B1_recentred/B1` | skill | 249 (249) | +0.128 | +0.128 | [+0.079, +0.561] | [+0.079, +0.561] |  |
| `/groups/regime/2025-26/upper_tail_twcrps/vs/B1_recentred/B2` | skill | 249 (249) | +0.092 | +0.092 | [-0.174, +0.913] | [-0.174, +0.913] |  |
| `/groups/regime/2025-26/upper_tail_twcrps/vs/spread_mr_b2/B1` | skill | 249 (249) | +0.222 | +0.222 | [+0.032, +0.852] | [+0.032, +0.852] |  |
| `/groups/regime/2025-26/upper_tail_twcrps/vs/spread_mr_b2/B2` | skill | 249 (249) | +0.190 | +0.190 | [+0.047, +1.039] | [+0.047, +1.039] |  |
| `/groups/regime/2025-26/upper_tail_twcrps/vs/spread_mr_b2/spread_mr_level10` | skill | 249 (249) | -0.078 | -0.078 | [-0.503, +0.065] | [-0.503, +0.065] |  |
| `/groups/regime/2025-26/upper_tail_twcrps/vs/spread_mr_ctx/B1` | skill | 249 (249) | +0.317 | +0.317 | [+0.209, +1.208] | [+0.209, +1.208] |  |
| `/groups/regime/2025-26/upper_tail_twcrps/vs/spread_mr_ctx/B2` | skill | 249 (249) | +0.289 | +0.289 | [+0.078, +1.869] | [+0.078, +1.869] |  |
| `/groups/regime/2025-26/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10` | skill | 249 (249) | +0.052 | +0.052 | [+0.011, +0.182] | [+0.011, +0.182] |  |
| `/groups/regime/2025-26/upper_tail_twcrps/vs/spread_mr_ctx_b2/B1` | skill | 249 (249) | +0.253 | +0.253 | [+0.055, +0.977] | [+0.055, +0.977] |  |
| `/groups/regime/2025-26/upper_tail_twcrps/vs/spread_mr_ctx_b2/B2` | skill | 249 (249) | +0.222 | +0.222 | [+0.065, +1.250] | [+0.065, +1.250] |  |
| `/groups/regime/2025-26/upper_tail_twcrps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 249 (249) | -0.037 | -0.037 | [-0.431, +0.122] | [-0.431, +0.122] |  |
| `/groups/regime/2025-26/upper_tail_twcrps/vs/spread_mr_level10/B1` | skill | 249 (249) | +0.279 | +0.279 | [+0.188, +1.027] | [+0.188, +1.027] |  |
| `/groups/regime/2025-26/upper_tail_twcrps/vs/spread_mr_level10/B2` | skill | 249 (249) | +0.249 | +0.249 | [+0.052, +1.599] | [+0.052, +1.599] |  |
| `/groups/scarcity_state/ample/grid_crps/vs/B1_recentred/B1` | skill | 1354 (1354) | +0.040 | +0.040 | [+0.028, +0.073] | [+0.028, +0.073] |  |
| `/groups/scarcity_state/ample/grid_crps/vs/B1_recentred/B2` | skill | 1354 (1354) | +0.304 | +0.304 | [+0.249, +0.771] | [+0.249, +0.771] |  |
| `/groups/scarcity_state/ample/grid_crps/vs/spread_mr_b2/B1` | skill | 1354 (1354) | +0.113 | +0.113 | [+0.057, +0.239] | [+0.057, +0.239] |  |
| `/groups/scarcity_state/ample/grid_crps/vs/spread_mr_b2/B2` | skill | 1354 (1354) | +0.356 | +0.356 | [+0.375, +0.853] | [+0.375, +0.853] |  |
| `/groups/scarcity_state/ample/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 1354 (1354) | +0.038 | +0.038 | [+0.004, +0.087] | [+0.004, +0.087] |  |
| `/groups/scarcity_state/ample/grid_crps/vs/spread_mr_ctx/B1` | skill | 1354 (1354) | +0.079 | +0.079 | [+0.028, +0.180] | [+0.028, +0.180] |  |
| `/groups/scarcity_state/ample/grid_crps/vs/spread_mr_ctx/B2` | skill | 1354 (1354) | +0.331 | +0.331 | [+0.324, +0.806] | [+0.324, +0.806] |  |
| `/groups/scarcity_state/ample/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 1354 (1354) | +0.001 | +0.001 | [-0.015, +0.016] | [-0.015, +0.016] |  |
| `/groups/scarcity_state/ample/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 1354 (1354) | +0.104 | +0.104 | [+0.041, +0.233] | [+0.041, +0.233] |  |
| `/groups/scarcity_state/ample/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 1354 (1354) | +0.349 | +0.349 | [+0.370, +0.829] | [+0.370, +0.829] |  |
| `/groups/scarcity_state/ample/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 1354 (1354) | +0.027 | +0.027 | [-0.012, +0.076] | [-0.012, +0.076] |  |
| `/groups/scarcity_state/ample/grid_crps/vs/spread_mr_level10/B1` | skill | 1354 (1354) | +0.078 | +0.078 | [+0.035, +0.171] | [+0.035, +0.171] |  |
| `/groups/scarcity_state/ample/grid_crps/vs/spread_mr_level10/B2` | skill | 1354 (1354) | +0.331 | +0.331 | [+0.317, +0.816] | [+0.317, +0.816] |  |
| `/groups/scarcity_state/ample/upper_tail_twcrps/vs/B1_recentred/B1` | skill | 1354 (1354) | +0.051 | +0.051 | [+0.001, +0.020] | [+0.001, +0.020] |  |
| `/groups/scarcity_state/ample/upper_tail_twcrps/vs/B1_recentred/B2` | skill | 1354 (1354) | +0.221 | +0.221 | [-0.031, +0.116] | [-0.031, +0.116] |  |
| `/groups/scarcity_state/ample/upper_tail_twcrps/vs/spread_mr_b2/B1` | skill | 1354 (1354) | +0.204 | +0.204 | [-0.001, +0.121] | [-0.001, +0.121] |  |
| `/groups/scarcity_state/ample/upper_tail_twcrps/vs/spread_mr_b2/B2` | skill | 1354 (1354) | +0.347 | +0.347 | [+0.004, +0.159] | [+0.004, +0.159] |  |
| `/groups/scarcity_state/ample/upper_tail_twcrps/vs/spread_mr_b2/spread_mr_level10` | skill | 1354 (1354) | -0.004 | -0.004 | [-0.004, +0.004] | [-0.004, +0.004] |  |
| `/groups/scarcity_state/ample/upper_tail_twcrps/vs/spread_mr_ctx/B1` | skill | 1354 (1354) | +0.102 | +0.102 | [-0.014, +0.087] | [-0.014, +0.087] |  |
| `/groups/scarcity_state/ample/upper_tail_twcrps/vs/spread_mr_ctx/B2` | skill | 1354 (1354) | +0.263 | +0.263 | [-0.009, +0.144] | [-0.009, +0.144] |  |
| `/groups/scarcity_state/ample/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10` | skill | 1354 (1354) | -0.132 | -0.132 | [-0.022, -0.007] | [-0.022, -0.007] |  |
| `/groups/scarcity_state/ample/upper_tail_twcrps/vs/spread_mr_ctx_b2/B1` | skill | 1354 (1354) | +0.104 | +0.104 | [-0.016, +0.091] | [-0.016, +0.091] |  |
| `/groups/scarcity_state/ample/upper_tail_twcrps/vs/spread_mr_ctx_b2/B2` | skill | 1354 (1354) | +0.265 | +0.265 | [-0.006, +0.139] | [-0.006, +0.139] |  |
| `/groups/scarcity_state/ample/upper_tail_twcrps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 1354 (1354) | -0.129 | -0.129 | [-0.024, -0.004] | [-0.024, -0.004] |  |
| `/groups/scarcity_state/ample/upper_tail_twcrps/vs/spread_mr_level10/B1` | skill | 1354 (1354) | +0.207 | +0.207 | [+0.001, +0.121] | [+0.001, +0.121] |  |
| `/groups/scarcity_state/ample/upper_tail_twcrps/vs/spread_mr_level10/B2` | skill | 1354 (1354) | +0.349 | +0.349 | [+0.002, +0.163] | [+0.002, +0.163] |  |
| `/groups/scarcity_state/scarce/grid_crps/vs/B1_recentred/B1` | skill | 501 (500) | +0.213 | +0.115 | [+0.338, +6.773] | [+0.322, +0.950] |  |
| `/groups/scarcity_state/scarce/grid_crps/vs/B1_recentred/B2` | skill | 501 (500) | +0.158 | +0.157 | [+0.093, +1.501] | [+0.089, +1.502] |  |
| `/groups/scarcity_state/scarce/grid_crps/vs/spread_mr_b2/B1` | skill | 501 (500) | +0.288 | +0.208 | [+0.672, +5.065] | [+0.535, +1.802] |  |
| `/groups/scarcity_state/scarce/grid_crps/vs/spread_mr_b2/B2` | skill | 501 (500) | +0.238 | +0.246 | [+0.722, +1.751] | [+0.784, +1.791] |  |
| `/groups/scarcity_state/scarce/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 501 (500) | -0.031 | -0.036 | [-0.393, +0.058] | [-0.413, +0.038] |  |
| `/groups/scarcity_state/scarce/grid_crps/vs/spread_mr_ctx/B1` | skill | 501 (500) | +0.328 | +0.257 | [+0.892, +5.627] | [+0.787, +2.070] |  |
| `/groups/scarcity_state/scarce/grid_crps/vs/spread_mr_ctx/B2` | skill | 501 (500) | +0.282 | +0.292 | [+0.832, +2.136] | [+0.894, +2.209] |  |
| `/groups/scarcity_state/scarce/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 501 (500) | +0.028 | +0.028 | [+0.027, +0.213] | [+0.026, +0.222] |  |
| `/groups/scarcity_state/scarce/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 501 (500) | +0.308 | +0.231 | [+0.743, +5.235] | [+0.615, +1.929] |  |
| `/groups/scarcity_state/scarce/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 501 (500) | +0.260 | +0.268 | [+0.831, +1.874] | [+0.880, +1.913] |  |
| `/groups/scarcity_state/scarce/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 501 (500) | -0.002 | -0.006 | [-0.271, +0.188] | [-0.286, +0.165] |  |
| `/groups/scarcity_state/scarce/grid_crps/vs/spread_mr_level10/B1` | skill | 501 (500) | +0.309 | +0.236 | [+0.841, +5.586] | [+0.735, +1.952] |  |
| `/groups/scarcity_state/scarce/grid_crps/vs/spread_mr_level10/B2` | skill | 501 (500) | +0.261 | +0.272 | [+0.705, +2.033] | [+0.790, +2.110] |  |
| `/groups/scarcity_state/scarce/upper_tail_twcrps/vs/B1_recentred/B1` | skill | 501 (500) | +0.238 | +0.132 | [+0.344, +6.843] | [+0.328, +0.956] |  |
| `/groups/scarcity_state/scarce/upper_tail_twcrps/vs/B1_recentred/B2` | skill | 501 (500) | +0.043 | +0.041 | [-0.412, +0.609] | [-0.409, +0.601] |  |
| `/groups/scarcity_state/scarce/upper_tail_twcrps/vs/spread_mr_b2/B1` | skill | 501 (500) | +0.330 | +0.246 | [+0.726, +5.245] | [+0.610, +1.888] |  |
| `/groups/scarcity_state/scarce/upper_tail_twcrps/vs/spread_mr_b2/B2` | skill | 501 (500) | +0.158 | +0.168 | [+0.318, +0.919] | [+0.380, +0.943] |  |
| `/groups/scarcity_state/scarce/upper_tail_twcrps/vs/spread_mr_b2/spread_mr_level10` | skill | 501 (500) | -0.003 | -0.007 | [-0.180, +0.109] | [-0.193, +0.087] |  |
| `/groups/scarcity_state/scarce/upper_tail_twcrps/vs/spread_mr_ctx/B1` | skill | 501 (500) | +0.356 | +0.280 | [+0.846, +5.610] | [+0.749, +2.048] |  |
| `/groups/scarcity_state/scarce/upper_tail_twcrps/vs/spread_mr_ctx/B2` | skill | 501 (500) | +0.191 | +0.205 | [+0.388, +1.154] | [+0.456, +1.204] |  |
| `/groups/scarcity_state/scarce/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10` | skill | 501 (500) | +0.036 | +0.037 | [+0.046, +0.228] | [+0.044, +0.236] |  |
| `/groups/scarcity_state/scarce/upper_tail_twcrps/vs/spread_mr_ctx_b2/B1` | skill | 501 (500) | +0.350 | +0.270 | [+0.785, +5.378] | [+0.678, +1.988] |  |
| `/groups/scarcity_state/scarce/upper_tail_twcrps/vs/spread_mr_ctx_b2/B2` | skill | 501 (500) | +0.184 | +0.194 | [+0.426, +1.026] | [+0.473, +1.062] |  |
| `/groups/scarcity_state/scarce/upper_tail_twcrps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 501 (500) | +0.028 | +0.024 | [-0.088, +0.242] | [-0.100, +0.216] |  |
| `/groups/scarcity_state/scarce/upper_tail_twcrps/vs/spread_mr_level10/B1` | skill | 501 (500) | +0.332 | +0.252 | [+0.779, +5.477] | [+0.669, +1.918] |  |
| `/groups/scarcity_state/scarce/upper_tail_twcrps/vs/spread_mr_level10/B2` | skill | 501 (500) | +0.160 | +0.174 | [+0.242, +1.038] | [+0.329, +1.082] |  |
| `/published/candidate_vs/B1_recentred` | skill | 1855 (1854) | -0.082 | -0.082 | [-0.295, -0.064] | [-0.297, -0.065] |  |
| `/published/candidate_vs/spread_mr_b2` | skill | 1855 (1854) | +0.014 | +0.020 | [-0.061, +0.102] | [-0.049, +0.113] |  |
| `/published/candidate_vs/spread_mr_ctx` | skill | 1855 (1854) | +0.031 | +0.040 | [-0.013, +0.127] | [-0.001, +0.149] |  |
| `/published/candidate_vs/spread_mr_ctx_b2` | skill | 1855 (1854) | +0.027 | +0.033 | [-0.037, +0.129] | [-0.031, +0.145] |  |
| `/published/candidate_vs/spread_mr_level10` | skill | 1855 (1854) | +0.012 | +0.020 | [-0.051, +0.087] | [-0.026, +0.101] |  |

## 688

Reproduction of the tracked score file: 110 records compared, largest absolute difference 0.00e+00 (headline figures and interval bounds); 0 not in the tracked file.

Records compared: 110; records in which a bound of the interval changes sign: 0.

| record | metric | days (without) | with | without | interval with | interval without | bound changes sign |
|---|---|---|---|---|---|---|---|
| `/also/mae_median/tests/control -> bill_x_band` | skill | 1868 (1867) | -0.002 | -0.002 | [-0.007, +0.003] | [-0.007, +0.003] |  |
| `/also/mae_median/tests/control -> post_month_end_window` | skill | 1868 (1867) | +0.010 | +0.010 | [+0.003, +0.016] | [+0.003, +0.016] |  |
| `/also/pinball_0.05/tests/control -> bill_x_band` | skill | 1868 (1867) | -0.001 | -0.001 | [-0.011, +0.009] | [-0.011, +0.009] |  |
| `/also/pinball_0.05/tests/control -> post_month_end_window` | skill | 1868 (1867) | +0.011 | +0.011 | [-0.000, +0.022] | [-0.000, +0.022] |  |
| `/also/pinball_0.25/tests/control -> bill_x_band` | skill | 1868 (1867) | -0.006 | -0.006 | [-0.016, +0.003] | [-0.016, +0.003] |  |
| `/also/pinball_0.25/tests/control -> post_month_end_window` | skill | 1868 (1867) | +0.010 | +0.010 | [+0.001, +0.019] | [+0.002, +0.019] |  |
| `/also/pinball_0.5/tests/control -> bill_x_band` | skill | 1868 (1867) | -0.002 | -0.002 | [-0.007, +0.003] | [-0.007, +0.003] |  |
| `/also/pinball_0.5/tests/control -> post_month_end_window` | skill | 1868 (1867) | +0.010 | +0.010 | [+0.003, +0.016] | [+0.003, +0.016] |  |
| `/also/pinball_0.75/tests/control -> bill_x_band` | skill | 1868 (1867) | -0.000 | -0.000 | [-0.006, +0.005] | [-0.006, +0.005] |  |
| `/also/pinball_0.75/tests/control -> post_month_end_window` | skill | 1868 (1867) | +0.013 | +0.013 | [+0.007, +0.021] | [+0.007, +0.021] |  |
| `/also/pinball_0.95/tests/control -> bill_x_band` | skill | 1868 (1867) | +0.004 | +0.004 | [-0.006, +0.016] | [-0.007, +0.015] |  |
| `/also/pinball_0.95/tests/control -> post_month_end_window` | skill | 1868 (1867) | +0.006 | +0.006 | [-0.005, +0.018] | [-0.006, +0.018] |  |
| `/by_lead_tests/1/control -> bill_x_band` | skill | 1868 (1867) | -0.000 | -0.000 | [-0.006, +0.005] | [-0.006, +0.005] |  |
| `/by_lead_tests/1/control -> post_month_end_window` | skill | 1868 (1867) | -0.001 | -0.001 | [-0.004, +0.002] | [-0.004, +0.002] |  |
| `/by_lead_tests/2/control -> bill_x_band` | skill | 1868 (1867) | +0.005 | +0.005 | [-0.001, +0.011] | [-0.001, +0.011] |  |
| `/by_lead_tests/2/control -> post_month_end_window` | skill | 1868 (1867) | +0.003 | +0.003 | [-0.002, +0.008] | [-0.002, +0.008] |  |
| `/by_lead_tests/3/control -> bill_x_band` | skill | 1868 (1867) | -0.001 | -0.001 | [-0.008, +0.005] | [-0.008, +0.005] |  |
| `/by_lead_tests/3/control -> post_month_end_window` | skill | 1868 (1867) | +0.013 | +0.013 | [+0.004, +0.022] | [+0.004, +0.022] |  |
| `/by_lead_tests/4/control -> bill_x_band` | skill | 1868 (1867) | -0.004 | -0.004 | [-0.012, +0.002] | [-0.012, +0.002] |  |
| `/by_lead_tests/4/control -> post_month_end_window` | skill | 1868 (1867) | +0.017 | +0.017 | [+0.008, +0.026] | [+0.008, +0.027] |  |
| `/by_lead_tests/5/control -> bill_x_band` | skill | 1868 (1867) | -0.004 | -0.004 | [-0.008, -0.000] | [-0.008, -0.000] |  |
| `/by_lead_tests/5/control -> post_month_end_window` | skill | 1868 (1867) | +0.017 | +0.017 | [+0.009, +0.025] | [+0.009, +0.025] |  |
| `/by_regime/2018-19/tests/B1 -> bill_x_band` | skill | 375 (374) | +0.322 | +0.216 | [+0.206, +0.594] | [+0.122, +0.349] |  |
| `/by_regime/2018-19/tests/B1 -> control` | skill | 375 (374) | +0.323 | +0.217 | [+0.206, +0.596] | [+0.124, +0.350] |  |
| `/by_regime/2018-19/tests/B1 -> post_month_end_window` | skill | 375 (374) | +0.327 | +0.222 | [+0.213, +0.599] | [+0.128, +0.356] |  |
| `/by_regime/2018-19/tests/B2 -> bill_x_band` | skill | 375 (374) | +0.111 | +0.110 | [+0.024, +0.225] | [+0.023, +0.225] |  |
| `/by_regime/2018-19/tests/B2 -> control` | skill | 375 (374) | +0.111 | +0.111 | [+0.027, +0.225] | [+0.024, +0.225] |  |
| `/by_regime/2018-19/tests/B2 -> post_month_end_window` | skill | 375 (374) | +0.117 | +0.116 | [+0.030, +0.233] | [+0.028, +0.233] |  |
| `/by_regime/2018-19/tests/control -> bill_x_band` | skill | 375 (374) | -0.001 | -0.000 | [-0.005, +0.005] | [-0.005, +0.005] |  |
| `/by_regime/2018-19/tests/control -> post_month_end_window` | skill | 375 (374) | +0.006 | +0.006 | [-0.003, +0.016] | [-0.003, +0.016] |  |
| `/by_regime/2020/tests/B1 -> bill_x_band` | skill | 251 (251) | +0.063 | +0.063 | [-0.186, +0.213] | [-0.186, +0.213] |  |
| `/by_regime/2020/tests/B1 -> control` | skill | 251 (251) | +0.066 | +0.066 | [-0.171, +0.207] | [-0.171, +0.207] |  |
| `/by_regime/2020/tests/B1 -> post_month_end_window` | skill | 251 (251) | +0.070 | +0.070 | [-0.209, +0.212] | [-0.209, +0.212] |  |
| `/by_regime/2020/tests/B2 -> bill_x_band` | skill | 251 (251) | +0.447 | +0.447 | [+0.222, +0.621] | [+0.222, +0.621] |  |
| `/by_regime/2020/tests/B2 -> control` | skill | 251 (251) | +0.449 | +0.449 | [+0.211, +0.624] | [+0.211, +0.624] |  |
| `/by_regime/2020/tests/B2 -> post_month_end_window` | skill | 251 (251) | +0.451 | +0.451 | [+0.211, +0.619] | [+0.211, +0.619] |  |
| `/by_regime/2020/tests/control -> bill_x_band` | skill | 251 (251) | -0.003 | -0.003 | [-0.014, +0.018] | [-0.014, +0.018] |  |
| `/by_regime/2020/tests/control -> post_month_end_window` | skill | 251 (251) | +0.004 | +0.004 | [-0.020, +0.028] | [-0.020, +0.028] |  |
| `/by_regime/2021-23/tests/B1 -> bill_x_band` | skill | 748 (748) | -0.270 | -0.270 | [-0.496, -0.123] | [-0.496, -0.123] |  |
| `/by_regime/2021-23/tests/B1 -> control` | skill | 748 (748) | -0.268 | -0.268 | [-0.490, -0.123] | [-0.490, -0.123] |  |
| `/by_regime/2021-23/tests/B1 -> post_month_end_window` | skill | 748 (748) | -0.237 | -0.237 | [-0.464, -0.092] | [-0.464, -0.092] |  |
| `/by_regime/2021-23/tests/B2 -> bill_x_band` | skill | 748 (748) | +0.391 | +0.391 | [+0.231, +0.561] | [+0.231, +0.561] |  |
| `/by_regime/2021-23/tests/B2 -> control` | skill | 748 (748) | +0.392 | +0.392 | [+0.233, +0.562] | [+0.233, +0.562] |  |
| `/by_regime/2021-23/tests/B2 -> post_month_end_window` | skill | 748 (748) | +0.407 | +0.407 | [+0.247, +0.574] | [+0.247, +0.574] |  |
| `/by_regime/2021-23/tests/control -> bill_x_band` | skill | 748 (748) | -0.002 | -0.002 | [-0.008, +0.004] | [-0.008, +0.004] |  |
| `/by_regime/2021-23/tests/control -> post_month_end_window` | skill | 748 (748) | +0.025 | +0.025 | [+0.014, +0.037] | [+0.014, +0.037] |  |
| `/by_regime/2024/tests/B1 -> bill_x_band` | skill | 250 (250) | +0.167 | +0.167 | [+0.097, +0.265] | [+0.097, +0.265] |  |
| `/by_regime/2024/tests/B1 -> control` | skill | 250 (250) | +0.157 | +0.157 | [+0.088, +0.248] | [+0.088, +0.248] |  |
| `/by_regime/2024/tests/B1 -> post_month_end_window` | skill | 250 (250) | +0.168 | +0.168 | [+0.101, +0.244] | [+0.101, +0.244] |  |
| `/by_regime/2024/tests/B2 -> bill_x_band` | skill | 250 (250) | -0.018 | -0.018 | [-0.262, +0.120] | [-0.262, +0.120] |  |
| `/by_regime/2024/tests/B2 -> control` | skill | 250 (250) | -0.030 | -0.030 | [-0.281, +0.111] | [-0.281, +0.111] |  |
| `/by_regime/2024/tests/B2 -> post_month_end_window` | skill | 250 (250) | -0.016 | -0.016 | [-0.273, +0.121] | [-0.273, +0.121] |  |
| `/by_regime/2024/tests/control -> bill_x_band` | skill | 250 (250) | +0.012 | +0.012 | [+0.006, +0.019] | [+0.006, +0.019] |  |
| `/by_regime/2024/tests/control -> post_month_end_window` | skill | 250 (250) | +0.013 | +0.013 | [-0.017, +0.033] | [-0.017, +0.033] |  |
| `/by_regime/2025-26/tests/B1 -> bill_x_band` | skill | 244 (244) | +0.228 | +0.228 | [+0.161, +0.324] | [+0.161, +0.324] |  |
| `/by_regime/2025-26/tests/B1 -> control` | skill | 244 (244) | +0.234 | +0.234 | [+0.173, +0.328] | [+0.173, +0.328] |  |
| `/by_regime/2025-26/tests/B1 -> post_month_end_window` | skill | 244 (244) | +0.239 | +0.239 | [+0.179, +0.332] | [+0.179, +0.332] |  |
| `/by_regime/2025-26/tests/B2 -> bill_x_band` | skill | 244 (244) | +0.330 | +0.330 | [+0.122, +0.503] | [+0.122, +0.503] |  |
| `/by_regime/2025-26/tests/B2 -> control` | skill | 244 (244) | +0.336 | +0.336 | [+0.121, +0.513] | [+0.121, +0.513] |  |
| `/by_regime/2025-26/tests/B2 -> post_month_end_window` | skill | 244 (244) | +0.340 | +0.340 | [+0.127, +0.516] | [+0.127, +0.516] |  |
| `/by_regime/2025-26/tests/control -> bill_x_band` | skill | 244 (244) | -0.008 | -0.008 | [-0.029, +0.006] | [-0.029, +0.006] |  |
| `/by_regime/2025-26/tests/control -> post_month_end_window` | skill | 244 (244) | +0.007 | +0.007 | [-0.001, +0.018] | [-0.001, +0.018] |  |
| `/by_type/month_end/tests/B1 -> bill_x_band` | skill | 507 (507) | +0.149 | +0.149 | [+0.021, +0.257] | [+0.021, +0.257] |  |
| `/by_type/month_end/tests/B1 -> control` | skill | 507 (507) | +0.146 | +0.146 | [+0.019, +0.253] | [+0.019, +0.253] |  |
| `/by_type/month_end/tests/B1 -> post_month_end_window` | skill | 507 (507) | +0.145 | +0.145 | [+0.018, +0.253] | [+0.018, +0.253] |  |
| `/by_type/month_end/tests/B2 -> bill_x_band` | skill | 507 (507) | +0.343 | +0.343 | [+0.252, +0.442] | [+0.252, +0.442] |  |
| `/by_type/month_end/tests/B2 -> control` | skill | 507 (507) | +0.341 | +0.341 | [+0.249, +0.441] | [+0.249, +0.441] |  |
| `/by_type/month_end/tests/B2 -> post_month_end_window` | skill | 507 (507) | +0.340 | +0.340 | [+0.249, +0.440] | [+0.249, +0.440] |  |
| `/by_type/month_end/tests/control -> bill_x_band` | skill | 507 (507) | +0.004 | +0.004 | [-0.000, +0.011] | [-0.000, +0.011] |  |
| `/by_type/month_end/tests/control -> post_month_end_window` | skill | 507 (507) | -0.001 | -0.001 | [-0.004, +0.004] | [-0.004, +0.004] |  |
| `/by_type/ordinary/tests/B1 -> bill_x_band` | skill | 1868 (1867) | +0.201 | +0.133 | [+0.082, +0.493] | [+0.062, +0.220] |  |
| `/by_type/ordinary/tests/B1 -> control` | skill | 1868 (1867) | +0.203 | +0.135 | [+0.084, +0.500] | [+0.065, +0.222] |  |
| `/by_type/ordinary/tests/B1 -> post_month_end_window` | skill | 1868 (1867) | +0.215 | +0.149 | [+0.098, +0.507] | [+0.080, +0.235] |  |
| `/by_type/ordinary/tests/B2 -> bill_x_band` | skill | 1868 (1867) | +0.259 | +0.259 | [+0.177, +0.343] | [+0.178, +0.343] |  |
| `/by_type/ordinary/tests/B2 -> control` | skill | 1868 (1867) | +0.261 | +0.261 | [+0.178, +0.346] | [+0.179, +0.346] |  |
| `/by_type/ordinary/tests/B2 -> post_month_end_window` | skill | 1868 (1867) | +0.272 | +0.273 | [+0.189, +0.355] | [+0.191, +0.355] |  |
| `/by_type/ordinary/tests/control -> bill_x_band` | skill | 1868 (1867) | -0.003 | -0.003 | [-0.009, +0.003] | [-0.009, +0.003] |  |
| `/by_type/ordinary/tests/control -> post_month_end_window` | skill | 1868 (1867) | +0.015 | +0.016 | [+0.007, +0.024] | [+0.006, +0.024] |  |
| `/by_type/quarter_end/tests/B1 -> bill_x_band` | skill | 146 (146) | +0.092 | +0.092 | [-0.079, +0.235] | [-0.079, +0.235] |  |
| `/by_type/quarter_end/tests/B1 -> control` | skill | 146 (146) | +0.092 | +0.092 | [-0.079, +0.235] | [-0.079, +0.235] |  |
| `/by_type/quarter_end/tests/B1 -> post_month_end_window` | skill | 146 (146) | +0.092 | +0.092 | [-0.079, +0.235] | [-0.079, +0.235] |  |
| `/by_type/quarter_end/tests/B2 -> bill_x_band` | skill | 146 (146) | +0.170 | +0.170 | [-0.309, +0.480] | [-0.309, +0.480] |  |
| `/by_type/quarter_end/tests/B2 -> control` | skill | 146 (146) | +0.170 | +0.170 | [-0.309, +0.480] | [-0.309, +0.480] |  |
| `/by_type/quarter_end/tests/B2 -> post_month_end_window` | skill | 146 (146) | +0.170 | +0.170 | [-0.309, +0.480] | [-0.309, +0.480] |  |
| `/by_type/quarter_end/tests/control -> bill_x_band` | skill | 146 (146) | +0.000 | +0.000 |  |  |  |
| `/by_type/quarter_end/tests/control -> post_month_end_window` | skill | 146 (146) | +0.000 | +0.000 |  |  |  |
| `/by_type/tax_date/tests/B1 -> bill_x_band` | skill | 214 (214) | -0.056 | -0.056 | [-0.194, +0.028] | [-0.194, +0.028] |  |
| `/by_type/tax_date/tests/B1 -> control` | skill | 214 (214) | -0.057 | -0.057 | [-0.196, +0.028] | [-0.196, +0.028] |  |
| `/by_type/tax_date/tests/B1 -> post_month_end_window` | skill | 214 (214) | -0.058 | -0.058 | [-0.198, +0.028] | [-0.198, +0.028] |  |
| `/by_type/tax_date/tests/B2 -> bill_x_band` | skill | 214 (214) | +0.275 | +0.275 | [-0.332, +0.545] | [-0.332, +0.545] |  |
| `/by_type/tax_date/tests/B2 -> control` | skill | 214 (214) | +0.274 | +0.274 | [-0.328, +0.546] | [-0.328, +0.546] |  |
| `/by_type/tax_date/tests/B2 -> post_month_end_window` | skill | 214 (214) | +0.274 | +0.274 | [-0.326, +0.545] | [-0.326, +0.545] |  |
| `/by_type/tax_date/tests/control -> bill_x_band` | skill | 214 (214) | +0.000 | +0.000 |  |  |  |
| `/by_type/tax_date/tests/control -> post_month_end_window` | skill | 214 (214) | -0.001 | -0.001 |  |  |  |
| `/pooled_key_secondary/B1 -> bill_x_band` | skill | 1868 (1867) | +0.339 | +0.256 | [+0.249, +0.516] | [+0.163, +0.356] |  |
| `/pooled_key_secondary/B1 -> control` | skill | 1868 (1867) | +0.338 | +0.254 | [+0.246, +0.519] | [+0.163, +0.354] |  |
| `/pooled_key_secondary/B1 -> post_month_end_window` | skill | 1868 (1867) | +0.341 | +0.257 | [+0.251, +0.521] | [+0.165, +0.357] |  |
| `/pooled_key_secondary/B2 -> bill_x_band` | skill | 1868 (1867) | +0.191 | +0.191 | [+0.069, +0.311] | [+0.069, +0.310] |  |
| `/pooled_key_secondary/B2 -> control` | skill | 1868 (1867) | +0.189 | +0.189 | [+0.071, +0.309] | [+0.069, +0.309] |  |
| `/pooled_key_secondary/B2 -> post_month_end_window` | skill | 1868 (1867) | +0.192 | +0.193 | [+0.073, +0.312] | [+0.073, +0.310] |  |
| `/pooled_key_secondary/control -> bill_x_band` | skill | 1868 (1867) | +0.003 | +0.003 | [-0.004, +0.009] | [-0.004, +0.010] |  |
| `/pooled_key_secondary/control -> post_month_end_window` | skill | 1868 (1867) | +0.004 | +0.004 | [-0.004, +0.012] | [-0.003, +0.012] |  |
| `/pooled_primary/B1 -> bill_x_band` | skill | 1868 (1867) | +0.192 | +0.133 | [+0.105, +0.388] | [+0.075, +0.205] |  |
| `/pooled_primary/B1 -> control` | skill | 1868 (1867) | +0.193 | +0.134 | [+0.105, +0.391] | [+0.076, +0.205] |  |
| `/pooled_primary/B1 -> post_month_end_window` | skill | 1868 (1867) | +0.201 | +0.143 | [+0.116, +0.393] | [+0.085, +0.214] |  |
| `/pooled_primary/B2 -> bill_x_band` | skill | 1868 (1867) | +0.260 | +0.260 | [+0.169, +0.347] | [+0.168, +0.348] |  |
| `/pooled_primary/B2 -> control` | skill | 1868 (1867) | +0.261 | +0.261 | [+0.170, +0.349] | [+0.169, +0.349] |  |
| `/pooled_primary/B2 -> post_month_end_window` | skill | 1868 (1867) | +0.268 | +0.268 | [+0.177, +0.356] | [+0.175, +0.356] |  |
| `/pooled_primary/control -> bill_x_band` | skill | 1868 (1867) | -0.001 | -0.001 | [-0.005, +0.003] | [-0.005, +0.003] |  |
| `/pooled_primary/control -> post_month_end_window` | skill | 1868 (1867) | +0.010 | +0.010 | [+0.004, +0.016] | [+0.004, +0.016] |  |
