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

Reproduction of the tracked score file: 421 records compared, largest absolute difference 6.11e-16 (headline figures and interval bounds); 0 not in the tracked file.

Records compared: 421; records in which a bound of the interval changes sign: 16.

| record | metric | days (without) | with | without | interval with | interval without | bound changes sign |
|---|---|---|---|---|---|---|---|
| `/groups/anchor_day_type/month_end/grid_crps/vs/B1_recentred/B1` | skill | 149 (149) | +0.362 | +0.362 | [+0.234, +0.530] | [+0.234, +0.530] |  |
| `/groups/anchor_day_type/month_end/grid_crps/vs/B1_recentred/B2` | skill | 149 (149) | +0.279 | +0.279 | [+0.149, +0.397] | [+0.149, +0.397] |  |
| `/groups/anchor_day_type/month_end/grid_crps/vs/spread_mr_b2/B1` | skill | 149 (149) | +0.361 | +0.361 | [+0.246, +0.552] | [+0.246, +0.552] |  |
| `/groups/anchor_day_type/month_end/grid_crps/vs/spread_mr_b2/B2` | skill | 149 (149) | +0.278 | +0.278 | [+0.159, +0.409] | [+0.159, +0.409] |  |
| `/groups/anchor_day_type/month_end/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 149 (149) | +0.029 | +0.029 | [-0.018, +0.091] | [-0.018, +0.091] |  |
| `/groups/anchor_day_type/month_end/grid_crps/vs/spread_mr_ctx/B1` | skill | 149 (149) | +0.356 | +0.356 | [+0.244, +0.530] | [+0.244, +0.530] |  |
| `/groups/anchor_day_type/month_end/grid_crps/vs/spread_mr_ctx/B2` | skill | 149 (149) | +0.272 | +0.272 | [+0.157, +0.392] | [+0.157, +0.392] |  |
| `/groups/anchor_day_type/month_end/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 149 (149) | +0.021 | +0.021 | [+0.001, +0.035] | [+0.001, +0.035] |  |
| `/groups/anchor_day_type/month_end/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 149 (149) | +0.372 | +0.372 | [+0.256, +0.564] | [+0.256, +0.564] |  |
| `/groups/anchor_day_type/month_end/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 149 (149) | +0.291 | +0.291 | [+0.174, +0.420] | [+0.174, +0.420] |  |
| `/groups/anchor_day_type/month_end/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 149 (149) | +0.047 | +0.047 | [-0.008, +0.116] | [-0.008, +0.116] |  |
| `/groups/anchor_day_type/month_end/grid_crps/vs/spread_mr_level10/B1` | skill | 149 (149) | +0.342 | +0.342 | [+0.229, +0.529] | [+0.229, +0.529] |  |
| `/groups/anchor_day_type/month_end/grid_crps/vs/spread_mr_level10/B2` | skill | 149 (149) | +0.256 | +0.256 | [+0.133, +0.379] | [+0.133, +0.379] |  |
| `/groups/anchor_day_type/month_end/upper_tail_twcrps/vs/B1_recentred/B1` | skill | 149 (149) | +0.491 | +0.491 | [+0.322, +0.610] | [+0.322, +0.610] |  |
| `/groups/anchor_day_type/month_end/upper_tail_twcrps/vs/B1_recentred/B2` | skill | 149 (149) | +0.192 | +0.192 | [+0.003, +0.393] | [+0.003, +0.393] |  |
| `/groups/anchor_day_type/month_end/upper_tail_twcrps/vs/spread_mr_b2/B1` | skill | 149 (149) | +0.494 | +0.494 | [+0.328, +0.667] | [+0.328, +0.667] |  |
| `/groups/anchor_day_type/month_end/upper_tail_twcrps/vs/spread_mr_b2/B2` | skill | 149 (149) | +0.196 | +0.196 | [+0.081, +0.291] | [+0.081, +0.291] |  |
| `/groups/anchor_day_type/month_end/upper_tail_twcrps/vs/spread_mr_b2/spread_mr_level10` | skill | 149 (149) | +0.075 | +0.075 | [-0.071, +0.411] | [-0.071, +0.411] |  |
| `/groups/anchor_day_type/month_end/upper_tail_twcrps/vs/spread_mr_ctx/B1` | skill | 149 (149) | +0.468 | +0.468 | [+0.344, +0.597] | [+0.344, +0.597] |  |
| `/groups/anchor_day_type/month_end/upper_tail_twcrps/vs/spread_mr_ctx/B2` | skill | 149 (149) | +0.156 | +0.156 | [+0.053, +0.319] | [+0.053, +0.319] |  |
| `/groups/anchor_day_type/month_end/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10` | skill | 149 (149) | +0.028 | +0.028 | [-0.021, +0.059] | [-0.021, +0.059] |  |
| `/groups/anchor_day_type/month_end/upper_tail_twcrps/vs/spread_mr_ctx_b2/B1` | skill | 149 (149) | +0.509 | +0.509 | [+0.331, +0.681] | [+0.331, +0.681] |  |
| `/groups/anchor_day_type/month_end/upper_tail_twcrps/vs/spread_mr_ctx_b2/B2` | skill | 149 (149) | +0.220 | +0.220 | [+0.091, +0.326] | [+0.091, +0.326] |  |
| `/groups/anchor_day_type/month_end/upper_tail_twcrps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 149 (149) | +0.102 | +0.102 | [-0.065, +0.417] | [-0.065, +0.417] |  |
| `/groups/anchor_day_type/month_end/upper_tail_twcrps/vs/spread_mr_level10/B1` | skill | 149 (149) | +0.453 | +0.453 | [+0.340, +0.591] | [+0.340, +0.591] |  |
| `/groups/anchor_day_type/month_end/upper_tail_twcrps/vs/spread_mr_level10/B2` | skill | 149 (149) | +0.131 | +0.131 | [+0.012, +0.291] | [+0.012, +0.291] |  |
| `/groups/anchor_day_type/ordinary/grid_crps/vs/spread_mr_b2/B1` | skill | 1588 (1588) | +0.104 | +0.104 | [+0.048, +0.169] | [+0.048, +0.169] |  |
| `/groups/anchor_day_type/ordinary/grid_crps/vs/spread_mr_b2/B2` | skill | 1588 (1588) | +0.293 | +0.293 | [+0.193, +0.375] | [+0.193, +0.375] |  |
| `/groups/anchor_day_type/ordinary/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 1588 (1588) | -0.009 | -0.009 | [-0.061, +0.025] | [-0.061, +0.025] |  |
| `/groups/anchor_day_type/ordinary/grid_crps/vs/spread_mr_ctx/B1` | skill | 1588 (1588) | +0.128 | +0.128 | [+0.088, +0.184] | [+0.088, +0.184] |  |
| `/groups/anchor_day_type/ordinary/grid_crps/vs/spread_mr_ctx/B2` | skill | 1588 (1588) | +0.312 | +0.312 | [+0.212, +0.401] | [+0.212, +0.401] |  |
| `/groups/anchor_day_type/ordinary/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 1588 (1588) | +0.018 | +0.018 | [+0.002, +0.033] | [+0.002, +0.033] |  |
| `/groups/anchor_day_type/ordinary/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 1588 (1588) | +0.115 | +0.115 | [+0.061, +0.177] | [+0.061, +0.177] |  |
| `/groups/anchor_day_type/ordinary/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 1588 (1588) | +0.302 | +0.302 | [+0.210, +0.379] | [+0.210, +0.379] |  |
| `/groups/anchor_day_type/ordinary/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 1588 (1588) | +0.003 | +0.003 | [-0.051, +0.039] | [-0.051, +0.039] |  |
| `/groups/anchor_day_type/ordinary/grid_crps/vs/spread_mr_level10/B1` | skill | 1588 (1588) | +0.112 | +0.112 | [+0.072, +0.171] | [+0.072, +0.171] |  |
| `/groups/anchor_day_type/ordinary/grid_crps/vs/spread_mr_level10/B2` | skill | 1588 (1588) | +0.299 | +0.299 | [+0.190, +0.394] | [+0.190, +0.394] |  |
| `/groups/anchor_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_b2/B1` | skill | 1588 (1588) | +0.145 | +0.145 | [+0.052, +0.259] | [+0.052, +0.259] |  |
| `/groups/anchor_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_b2/B2` | skill | 1588 (1588) | +0.176 | +0.176 | [+0.051, +0.290] | [+0.051, +0.290] |  |
| `/groups/anchor_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_b2/spread_mr_level10` | skill | 1588 (1588) | -0.015 | -0.015 | [-0.081, +0.022] | [-0.081, +0.022] |  |
| `/groups/anchor_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_ctx/B1` | skill | 1588 (1588) | +0.178 | +0.178 | [+0.108, +0.282] | [+0.108, +0.282] |  |
| `/groups/anchor_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_ctx/B2` | skill | 1588 (1588) | +0.208 | +0.208 | [+0.082, +0.338] | [+0.082, +0.338] |  |
| `/groups/anchor_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10` | skill | 1588 (1588) | +0.024 | +0.024 | [+0.001, +0.046] | [+0.001, +0.046] |  |
| `/groups/anchor_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_ctx_b2/B1` | skill | 1588 (1588) | +0.160 | +0.160 | [+0.076, +0.266] | [+0.076, +0.266] |  |
| `/groups/anchor_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_ctx_b2/B2` | skill | 1588 (1588) | +0.191 | +0.191 | [+0.082, +0.301] | [+0.082, +0.301] |  |
| `/groups/anchor_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 1588 (1588) | +0.004 | +0.004 | [-0.068, +0.049] | [-0.068, +0.049] |  |
| `/groups/anchor_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_level10/B1` | skill | 1588 (1588) | +0.157 | +0.157 | [+0.074, +0.274] | [+0.074, +0.274] |  |
| `/groups/anchor_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_level10/B2` | skill | 1588 (1588) | +0.188 | +0.188 | [+0.045, +0.328] | [+0.045, +0.328] |  |
| `/groups/anchor_day_type/quarter_end/grid_crps/vs/B1_recentred/B1` | skill | 29 (29) | +0.650 | +0.650 | [+0.348, +1.474] | [+0.348, +1.474] |  |
| `/groups/anchor_day_type/quarter_end/grid_crps/vs/B1_recentred/B2` | skill | 29 (29) | +0.083 | +0.083 | [-0.954, +0.732] | [-0.954, +0.732] |  |
| `/groups/anchor_day_type/quarter_end/grid_crps/vs/spread_mr_b2/B1` | skill | 29 (29) | +0.674 | +0.674 | [+0.416, +0.946] | [+0.416, +0.946] |  |
| `/groups/anchor_day_type/quarter_end/grid_crps/vs/spread_mr_b2/B2` | skill | 29 (29) | +0.145 | +0.145 | [-0.386, +0.493] | [-0.386, +0.493] |  |
| `/groups/anchor_day_type/quarter_end/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 29 (29) | +0.045 | +0.045 | [-0.051, +0.158] | [-0.051, +0.158] |  |
| `/groups/anchor_day_type/quarter_end/grid_crps/vs/spread_mr_ctx/B1` | skill | 29 (29) | +0.652 | +0.652 | [+0.360, +1.040] | [+0.360, +1.040] |  |
| `/groups/anchor_day_type/quarter_end/grid_crps/vs/spread_mr_ctx/B2` | skill | 29 (29) | +0.087 | +0.087 | [-0.525, +0.536] | [-0.525, +0.536] |  |
| `/groups/anchor_day_type/quarter_end/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 29 (29) | -0.019 | -0.019 | [-0.044, +0.002] | [-0.044, +0.002] |  |
| `/groups/anchor_day_type/quarter_end/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 29 (29) | +0.668 | +0.668 | [+0.402, +0.924] | [+0.402, +0.924] |  |
| `/groups/anchor_day_type/quarter_end/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 29 (29) | +0.129 | +0.129 | [-0.409, +0.469] | [-0.409, +0.469] |  |
| `/groups/anchor_day_type/quarter_end/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 29 (29) | +0.027 | +0.027 | [-0.077, +0.181] | [-0.077, +0.181] |  |
| `/groups/anchor_day_type/quarter_end/grid_crps/vs/spread_mr_level10/B1` | skill | 29 (29) | +0.659 | +0.659 | [+0.363, +1.072] | [+0.363, +1.072] |  |
| `/groups/anchor_day_type/quarter_end/grid_crps/vs/spread_mr_level10/B2` | skill | 29 (29) | +0.105 | +0.105 | [-0.536, +0.570] | [-0.536, +0.570] |  |
| `/groups/anchor_day_type/quarter_end/upper_tail_twcrps/vs/B1_recentred/B1` | skill | 29 (29) | +0.826 | +0.826 | [+0.763, +0.958] | [+0.763, +0.958] |  |
| `/groups/anchor_day_type/quarter_end/upper_tail_twcrps/vs/B1_recentred/B2` | skill | 29 (29) | +0.223 | +0.223 | [-0.994, +0.629] | [-0.994, +0.629] |  |
| `/groups/anchor_day_type/quarter_end/upper_tail_twcrps/vs/spread_mr_b2/B1` | skill | 29 (29) | +0.843 | +0.843 | [+0.589, +0.893] | [+0.589, +0.893] |  |
| `/groups/anchor_day_type/quarter_end/upper_tail_twcrps/vs/spread_mr_b2/B2` | skill | 29 (29) | +0.302 | +0.302 | [+0.187, +0.414] | [+0.187, +0.414] |  |
| `/groups/anchor_day_type/quarter_end/upper_tail_twcrps/vs/spread_mr_b2/spread_mr_level10` | skill | 29 (29) | -0.024 | -0.024 | [-0.100, +0.087] | [-0.100, +0.087] |  |
| `/groups/anchor_day_type/quarter_end/upper_tail_twcrps/vs/spread_mr_ctx/B1` | skill | 29 (29) | +0.845 | +0.845 | [+0.435, +0.901] | [+0.435, +0.901] |  |
| `/groups/anchor_day_type/quarter_end/upper_tail_twcrps/vs/spread_mr_ctx/B2` | skill | 29 (29) | +0.308 | +0.308 | [+0.015, +0.395] | [+0.015, +0.395] |  |
| `/groups/anchor_day_type/quarter_end/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10` | skill | 29 (29) | -0.015 | -0.015 | [-0.210, +0.042] | [-0.210, +0.042] |  |
| `/groups/anchor_day_type/quarter_end/upper_tail_twcrps/vs/spread_mr_ctx_b2/B1` | skill | 29 (29) | +0.841 | +0.841 | [+0.537, +0.889] | [+0.537, +0.889] |  |
| `/groups/anchor_day_type/quarter_end/upper_tail_twcrps/vs/spread_mr_ctx_b2/B2` | skill | 29 (29) | +0.290 | +0.290 | [+0.139, +0.443] | [+0.139, +0.443] |  |
| `/groups/anchor_day_type/quarter_end/upper_tail_twcrps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 29 (29) | -0.041 | -0.041 | [-0.329, +0.110] | [-0.329, +0.110] |  |
| `/groups/anchor_day_type/quarter_end/upper_tail_twcrps/vs/spread_mr_level10/B1` | skill | 29 (29) | +0.847 | +0.847 | [+0.501, +0.904] | [+0.501, +0.904] |  |
| `/groups/anchor_day_type/quarter_end/upper_tail_twcrps/vs/spread_mr_level10/B2` | skill | 29 (29) | +0.318 | +0.318 | [+0.118, +0.411] | [+0.118, +0.411] |  |
| `/groups/anchor_day_type/tax_date/grid_crps/vs/B1_recentred/B1` | skill | 89 (88) | +0.744 | +0.386 | [+0.411, +2.090] | [+0.241, +0.625] |  |
| `/groups/anchor_day_type/tax_date/grid_crps/vs/B1_recentred/B2` | skill | 89 (88) | +0.457 | +0.456 | [+0.204, +0.642] | [+0.200, +0.640] |  |
| `/groups/anchor_day_type/tax_date/grid_crps/vs/spread_mr_b2/B1` | skill | 89 (88) | +0.703 | +0.387 | [+0.387, +1.737] | [+0.196, +0.683] |  |
| `/groups/anchor_day_type/tax_date/grid_crps/vs/spread_mr_b2/B2` | skill | 89 (88) | +0.369 | +0.457 | [-0.018, +0.553] | [+0.193, +0.614] | yes |
| `/groups/anchor_day_type/tax_date/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 89 (88) | +0.086 | +0.052 | [+0.029, +0.134] | [-0.079, +0.196] | yes |
| `/groups/anchor_day_type/tax_date/grid_crps/vs/spread_mr_ctx/B1` | skill | 89 (88) | +0.672 | +0.346 | [+0.294, +2.156] | [+0.055, +0.956] |  |
| `/groups/anchor_day_type/tax_date/grid_crps/vs/spread_mr_ctx/B2` | skill | 89 (88) | +0.303 | +0.421 | [-0.167, +0.537] | [-0.080, +0.638] |  |
| `/groups/anchor_day_type/tax_date/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 89 (88) | -0.009 | -0.010 | [-0.038, +0.036] | [-0.044, +0.046] |  |
| `/groups/anchor_day_type/tax_date/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 89 (88) | +0.705 | +0.391 | [+0.383, +1.727] | [+0.182, +0.718] |  |
| `/groups/anchor_day_type/tax_date/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 89 (88) | +0.372 | +0.461 | [-0.007, +0.555] | [+0.167, +0.618] | yes |
| `/groups/anchor_day_type/tax_date/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 89 (88) | +0.090 | +0.059 | [+0.040, +0.140] | [-0.037, +0.186] | yes |
| `/groups/anchor_day_type/tax_date/grid_crps/vs/spread_mr_level10/B1` | skill | 89 (88) | +0.675 | +0.353 | [+0.314, +2.116] | [+0.092, +0.885] |  |
| `/groups/anchor_day_type/tax_date/grid_crps/vs/spread_mr_level10/B2` | skill | 89 (88) | +0.309 | +0.427 | [-0.168, +0.538] | [-0.005, +0.634] |  |
| `/groups/context/ordinary after a risk day/grid_crps/vs/B1_recentred/B1` | skill | 200 (200) | +0.159 | +0.048 | [+0.025, +1.315] | [+0.028, +0.071] |  |
| `/groups/context/ordinary after a risk day/grid_crps/vs/B1_recentred/B2` | skill | 200 (200) | +0.326 | +0.326 | [+0.207, +0.439] | [+0.207, +0.439] |  |
| `/groups/context/ordinary after a risk day/grid_crps/vs/spread_mr_b2/B1` | skill | 200 (200) | +0.078 | -0.019 | [-0.065, +0.437] | [-0.117, +0.033] |  |
| `/groups/context/ordinary after a risk day/grid_crps/vs/spread_mr_b2/B2` | skill | 200 (200) | +0.261 | +0.278 | [+0.165, +0.366] | [+0.182, +0.382] |  |
| `/groups/context/ordinary after a risk day/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 200 (200) | -0.043 | -0.054 | [-0.148, -0.001] | [-0.166, -0.011] |  |
| `/groups/context/ordinary after a risk day/grid_crps/vs/spread_mr_ctx/B1` | skill | 200 (200) | +0.116 | +0.033 | [+0.007, +0.487] | [-0.008, +0.071] | yes |
| `/groups/context/ordinary after a risk day/grid_crps/vs/spread_mr_ctx/B2` | skill | 200 (200) | +0.291 | +0.315 | [+0.176, +0.404] | [+0.206, +0.421] |  |
| `/groups/context/ordinary after a risk day/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 200 (200) | -0.001 | +0.000 | [-0.025, +0.026] | [-0.025, +0.027] |  |
| `/groups/context/ordinary after a risk day/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 200 (200) | +0.084 | -0.012 | [-0.048, +0.431] | [-0.090, +0.037] |  |
| `/groups/context/ordinary after a risk day/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 200 (200) | +0.265 | +0.284 | [+0.169, +0.364] | [+0.189, +0.379] |  |
| `/groups/context/ordinary after a risk day/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 200 (200) | -0.037 | -0.047 | [-0.102, +0.004] | [-0.115, -0.000] | yes |
| `/groups/context/ordinary after a risk day/grid_crps/vs/spread_mr_level10/B1` | skill | 200 (200) | +0.116 | +0.033 | [+0.000, +0.576] | [-0.005, +0.075] | yes |
| `/groups/context/ordinary after a risk day/grid_crps/vs/spread_mr_level10/B2` | skill | 200 (200) | +0.291 | +0.315 | [+0.176, +0.403] | [+0.203, +0.422] |  |
| `/groups/context/ordinary after a risk day/upper_tail_twcrps/vs/B1_recentred/B1` | skill | 200 (200) | +0.227 | +0.054 | [-0.003, +2.066] | [+0.030, +0.088] | yes |
| `/groups/context/ordinary after a risk day/upper_tail_twcrps/vs/B1_recentred/B2` | skill | 200 (200) | +0.236 | +0.235 | [+0.108, +0.370] | [+0.108, +0.369] |  |
| `/groups/context/ordinary after a risk day/upper_tail_twcrps/vs/spread_mr_b2/B1` | skill | 200 (200) | +0.131 | -0.021 | [-0.084, +0.767] | [-0.110, +0.039] |  |
| `/groups/context/ordinary after a risk day/upper_tail_twcrps/vs/spread_mr_b2/B2` | skill | 200 (200) | +0.141 | +0.175 | [+0.083, +0.223] | [+0.097, +0.286] |  |
| `/groups/context/ordinary after a risk day/upper_tail_twcrps/vs/spread_mr_b2/spread_mr_level10` | skill | 200 (200) | -0.048 | -0.066 | [-0.168, -0.001] | [-0.228, -0.021] |  |
| `/groups/context/ordinary after a risk day/upper_tail_twcrps/vs/spread_mr_ctx/B1` | skill | 200 (200) | +0.150 | +0.019 | [-0.022, +0.821] | [-0.033, +0.076] |  |
| `/groups/context/ordinary after a risk day/upper_tail_twcrps/vs/spread_mr_ctx/B2` | skill | 200 (200) | +0.160 | +0.207 | [+0.064, +0.301] | [+0.106, +0.362] |  |
| `/groups/context/ordinary after a risk day/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10` | skill | 200 (200) | -0.025 | -0.025 | [-0.053, +0.004] | [-0.055, +0.007] |  |
| `/groups/context/ordinary after a risk day/upper_tail_twcrps/vs/spread_mr_ctx_b2/B1` | skill | 200 (200) | +0.121 | -0.032 | [-0.083, +0.752] | [-0.114, +0.035] |  |
| `/groups/context/ordinary after a risk day/upper_tail_twcrps/vs/spread_mr_ctx_b2/B2` | skill | 200 (200) | +0.131 | +0.166 | [+0.068, +0.225] | [+0.092, +0.280] |  |
| `/groups/context/ordinary after a risk day/upper_tail_twcrps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 200 (200) | -0.059 | -0.077 | [-0.124, -0.015] | [-0.145, -0.026] |  |
| `/groups/context/ordinary after a risk day/upper_tail_twcrps/vs/spread_mr_level10/B1` | skill | 200 (200) | +0.171 | +0.042 | [-0.008, +0.970] | [+0.007, +0.093] | yes |
| `/groups/context/ordinary after a risk day/upper_tail_twcrps/vs/spread_mr_level10/B2` | skill | 200 (200) | +0.180 | +0.226 | [+0.087, +0.298] | [+0.117, +0.360] |  |
| `/groups/context/ordinary after an ordinary day/grid_crps/vs/B1_recentred/B1` | skill | 1276 (1276) | +0.219 | +0.141 | [+0.087, +0.806] | [+0.090, +0.226] |  |
| `/groups/context/ordinary after an ordinary day/grid_crps/vs/B1_recentred/B2` | skill | 1276 (1276) | +0.180 | +0.180 | [+0.023, +0.301] | [+0.023, +0.301] |  |
| `/groups/context/ordinary after an ordinary day/grid_crps/vs/spread_mr_b2/B1` | skill | 1276 (1276) | +0.353 | +0.292 | [+0.221, +0.626] | [+0.206, +0.412] |  |
| `/groups/context/ordinary after an ordinary day/grid_crps/vs/spread_mr_b2/B2` | skill | 1276 (1276) | +0.320 | +0.324 | [+0.237, +0.405] | [+0.242, +0.408] |  |
| `/groups/context/ordinary after an ordinary day/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 1276 (1276) | +0.025 | +0.023 | [-0.033, +0.068] | [-0.034, +0.066] |  |
| `/groups/context/ordinary after an ordinary day/grid_crps/vs/spread_mr_ctx/B1` | skill | 1276 (1276) | +0.348 | +0.289 | [+0.227, +0.649] | [+0.213, +0.407] |  |
| `/groups/context/ordinary after an ordinary day/grid_crps/vs/spread_mr_ctx/B2` | skill | 1276 (1276) | +0.316 | +0.321 | [+0.212, +0.412] | [+0.220, +0.415] |  |
| `/groups/context/ordinary after an ordinary day/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 1276 (1276) | +0.018 | +0.018 | [+0.003, +0.033] | [+0.003, +0.033] |  |
| `/groups/context/ordinary after an ordinary day/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 1276 (1276) | +0.363 | +0.303 | [+0.233, +0.622] | [+0.219, +0.418] |  |
| `/groups/context/ordinary after an ordinary day/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 1276 (1276) | +0.331 | +0.335 | [+0.247, +0.416] | [+0.252, +0.418] |  |
| `/groups/context/ordinary after an ordinary day/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 1276 (1276) | +0.040 | +0.038 | [-0.017, +0.082] | [-0.019, +0.080] |  |
| `/groups/context/ordinary after an ordinary day/grid_crps/vs/spread_mr_level10/B1` | skill | 1276 (1276) | +0.336 | +0.276 | [+0.214, +0.662] | [+0.200, +0.400] |  |
| `/groups/context/ordinary after an ordinary day/grid_crps/vs/spread_mr_level10/B2` | skill | 1276 (1276) | +0.303 | +0.308 | [+0.200, +0.400] | [+0.207, +0.403] |  |
| `/groups/context/ordinary after an ordinary day/upper_tail_twcrps/vs/B1_recentred/B1` | skill | 1276 (1276) | +0.366 | +0.241 | [+0.159, +1.141] | [+0.163, +0.356] |  |
| `/groups/context/ordinary after an ordinary day/upper_tail_twcrps/vs/B1_recentred/B2` | skill | 1276 (1276) | -0.172 | -0.173 | [-0.555, +0.061] | [-0.556, +0.060] |  |
| `/groups/context/ordinary after an ordinary day/upper_tail_twcrps/vs/spread_mr_b2/B1` | skill | 1276 (1276) | +0.574 | +0.498 | [+0.420, +0.791] | [+0.385, +0.613] |  |
| `/groups/context/ordinary after an ordinary day/upper_tail_twcrps/vs/spread_mr_b2/B2` | skill | 1276 (1276) | +0.212 | +0.223 | [+0.111, +0.314] | [+0.131, +0.320] |  |
| `/groups/context/ordinary after an ordinary day/upper_tail_twcrps/vs/spread_mr_b2/spread_mr_level10` | skill | 1276 (1276) | +0.068 | +0.064 | [+0.002, +0.132] | [-0.002, +0.129] | yes |
| `/groups/context/ordinary after an ordinary day/upper_tail_twcrps/vs/spread_mr_ctx/B1` | skill | 1276 (1276) | +0.572 | +0.498 | [+0.424, +0.783] | [+0.390, +0.608] |  |
| `/groups/context/ordinary after an ordinary day/upper_tail_twcrps/vs/spread_mr_ctx/B2` | skill | 1276 (1276) | +0.208 | +0.223 | [+0.077, +0.340] | [+0.105, +0.348] |  |
| `/groups/context/ordinary after an ordinary day/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10` | skill | 1276 (1276) | +0.064 | +0.065 | [+0.021, +0.104] | [+0.020, +0.105] |  |
| `/groups/context/ordinary after an ordinary day/upper_tail_twcrps/vs/spread_mr_ctx_b2/B1` | skill | 1276 (1276) | +0.593 | +0.520 | [+0.438, +0.778] | [+0.404, +0.626] |  |
| `/groups/context/ordinary after an ordinary day/upper_tail_twcrps/vs/spread_mr_ctx_b2/B2` | skill | 1276 (1276) | +0.247 | +0.258 | [+0.146, +0.364] | [+0.165, +0.370] |  |
| `/groups/context/ordinary after an ordinary day/upper_tail_twcrps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 1276 (1276) | +0.110 | +0.106 | [+0.027, +0.177] | [+0.022, +0.174] |  |
| `/groups/context/ordinary after an ordinary day/upper_tail_twcrps/vs/spread_mr_level10/B1` | skill | 1276 (1276) | +0.542 | +0.463 | [+0.389, +0.803] | [+0.358, +0.591] |  |
| `/groups/context/ordinary after an ordinary day/upper_tail_twcrps/vs/spread_mr_level10/B2` | skill | 1276 (1276) | +0.154 | +0.170 | [+0.015, +0.282] | [+0.044, +0.289] |  |
| `/groups/context/risk day/grid_crps/vs/B1_recentred/B1` | skill | 383 (383) | -0.001 | -0.001 | [-0.010, +0.008] | [-0.010, +0.008] |  |
| `/groups/context/risk day/grid_crps/vs/B1_recentred/B2` | skill | 383 (383) | +0.256 | +0.256 | [-0.032, +0.463] | [-0.032, +0.463] |  |
| `/groups/context/risk day/grid_crps/vs/spread_mr_b2/B1` | skill | 383 (383) | +0.010 | +0.010 | [-0.052, +0.063] | [-0.052, +0.063] |  |
| `/groups/context/risk day/grid_crps/vs/spread_mr_b2/B2` | skill | 383 (383) | +0.264 | +0.264 | [-0.005, +0.427] | [-0.005, +0.427] |  |
| `/groups/context/risk day/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 383 (383) | -0.023 | -0.023 | [-0.090, +0.026] | [-0.090, +0.026] |  |
| `/groups/context/risk day/grid_crps/vs/spread_mr_ctx/B1` | skill | 383 (383) | +0.052 | +0.052 | [-0.024, +0.105] | [-0.024, +0.105] |  |
| `/groups/context/risk day/grid_crps/vs/spread_mr_ctx/B2` | skill | 383 (383) | +0.295 | +0.295 | [+0.042, +0.448] | [+0.042, +0.448] |  |
| `/groups/context/risk day/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 383 (383) | +0.021 | +0.021 | [-0.051, +0.069] | [-0.051, +0.069] |  |
| `/groups/context/risk day/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 383 (383) | +0.020 | +0.020 | [-0.083, +0.092] | [-0.083, +0.092] |  |
| `/groups/context/risk day/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 383 (383) | +0.272 | +0.272 | [+0.041, +0.401] | [+0.041, +0.401] |  |
| `/groups/context/risk day/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 383 (383) | -0.012 | -0.012 | [-0.112, +0.069] | [-0.112, +0.069] |  |
| `/groups/context/risk day/grid_crps/vs/spread_mr_level10/B1` | skill | 383 (383) | +0.032 | +0.032 | [-0.008, +0.060] | [-0.008, +0.060] |  |
| `/groups/context/risk day/grid_crps/vs/spread_mr_level10/B2` | skill | 383 (383) | +0.281 | +0.281 | [-0.024, +0.464] | [-0.024, +0.464] |  |
| `/groups/context/risk day/upper_tail_twcrps/vs/B1_recentred/B1` | skill | 383 (383) | -0.004 | -0.004 | [-0.012, +0.005] | [-0.012, +0.005] |  |
| `/groups/context/risk day/upper_tail_twcrps/vs/B1_recentred/B2` | skill | 383 (383) | +0.173 | +0.173 | [-0.130, +0.443] | [-0.130, +0.443] |  |
| `/groups/context/risk day/upper_tail_twcrps/vs/spread_mr_b2/B1` | skill | 383 (383) | -0.021 | -0.021 | [-0.104, +0.035] | [-0.104, +0.035] |  |
| `/groups/context/risk day/upper_tail_twcrps/vs/spread_mr_b2/B2` | skill | 383 (383) | +0.159 | +0.159 | [-0.064, +0.362] | [-0.064, +0.362] |  |
| `/groups/context/risk day/upper_tail_twcrps/vs/spread_mr_b2/spread_mr_level10` | skill | 383 (383) | -0.043 | -0.043 | [-0.163, +0.032] | [-0.163, +0.032] |  |
| `/groups/context/risk day/upper_tail_twcrps/vs/spread_mr_ctx/B1` | skill | 383 (383) | +0.031 | +0.031 | [-0.057, +0.085] | [-0.057, +0.085] |  |
| `/groups/context/risk day/upper_tail_twcrps/vs/spread_mr_ctx/B2` | skill | 383 (383) | +0.202 | +0.202 | [-0.041, +0.401] | [-0.041, +0.401] |  |
| `/groups/context/risk day/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10` | skill | 383 (383) | +0.011 | +0.011 | [-0.097, +0.071] | [-0.097, +0.071] |  |
| `/groups/context/risk day/upper_tail_twcrps/vs/spread_mr_ctx_b2/B1` | skill | 383 (383) | -0.009 | -0.009 | [-0.155, +0.083] | [-0.155, +0.083] |  |
| `/groups/context/risk day/upper_tail_twcrps/vs/spread_mr_ctx_b2/B2` | skill | 383 (383) | +0.169 | +0.169 | [-0.014, +0.322] | [-0.014, +0.322] |  |
| `/groups/context/risk day/upper_tail_twcrps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 383 (383) | -0.031 | -0.031 | [-0.191, +0.086] | [-0.191, +0.086] |  |
| `/groups/context/risk day/upper_tail_twcrps/vs/spread_mr_level10/B1` | skill | 383 (383) | +0.021 | +0.021 | [-0.007, +0.047] | [-0.007, +0.047] |  |
| `/groups/context/risk day/upper_tail_twcrps/vs/spread_mr_level10/B2` | skill | 383 (383) | +0.194 | +0.194 | [-0.127, +0.443] | [-0.127, +0.443] |  |
| `/groups/pooled/all decision days/grid_crps/vs/B1_recentred/B1` | skill | 1855 (1854) | +0.148 | +0.085 | [+0.069, +0.515] | [+0.061, +0.119] |  |
| `/groups/pooled/all decision days/grid_crps/vs/B1_recentred/B2` | skill | 1855 (1854) | +0.226 | +0.226 | [+0.113, +0.326] | [+0.111, +0.327] |  |
| `/groups/pooled/all decision days/grid_crps/vs/spread_mr_b2/B1` | skill | 1855 (1854) | +0.222 | +0.170 | [+0.147, +0.382] | [+0.116, +0.240] |  |
| `/groups/pooled/all decision days/grid_crps/vs/spread_mr_b2/B2` | skill | 1855 (1854) | +0.293 | +0.297 | [+0.195, +0.374] | [+0.206, +0.377] |  |
| `/groups/pooled/all decision days/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 1855 (1854) | -0.001 | -0.003 | [-0.045, +0.031] | [-0.047, +0.029] |  |
| `/groups/pooled/all decision days/grid_crps/vs/spread_mr_ctx/B1` | skill | 1855 (1854) | +0.235 | +0.186 | [+0.164, +0.407] | [+0.140, +0.250] |  |
| `/groups/pooled/all decision days/grid_crps/vs/spread_mr_ctx/B2` | skill | 1855 (1854) | +0.305 | +0.311 | [+0.204, +0.393] | [+0.218, +0.397] |  |
| `/groups/pooled/all decision days/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 1855 (1854) | +0.016 | +0.016 | [+0.002, +0.029] | [+0.002, +0.030] |  |
| `/groups/pooled/all decision days/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 1855 (1854) | +0.232 | +0.180 | [+0.153, +0.395] | [+0.125, +0.250] |  |
| `/groups/pooled/all decision days/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 1855 (1854) | +0.302 | +0.306 | [+0.211, +0.380] | [+0.221, +0.382] |  |
| `/groups/pooled/all decision days/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 1855 (1854) | +0.011 | +0.009 | [-0.034, +0.045] | [-0.035, +0.041] |  |
| `/groups/pooled/all decision days/grid_crps/vs/spread_mr_level10/B1` | skill | 1855 (1854) | +0.223 | +0.172 | [+0.157, +0.395] | [+0.128, +0.238] |  |
| `/groups/pooled/all decision days/grid_crps/vs/spread_mr_level10/B2` | skill | 1855 (1854) | +0.294 | +0.300 | [+0.184, +0.387] | [+0.199, +0.392] |  |
| `/groups/pooled/all decision days/upper_tail_twcrps/vs/B1_recentred/B1` | skill | 1855 (1854) | +0.226 | +0.126 | [+0.116, +0.668] | [+0.086, +0.175] |  |
| `/groups/pooled/all decision days/upper_tail_twcrps/vs/B1_recentred/B2` | skill | 1855 (1854) | +0.060 | +0.058 | [-0.090, +0.176] | [-0.093, +0.176] |  |
| `/groups/pooled/all decision days/upper_tail_twcrps/vs/spread_mr_b2/B1` | skill | 1855 (1854) | +0.322 | +0.243 | [+0.231, +0.487] | [+0.151, +0.347] |  |
| `/groups/pooled/all decision days/upper_tail_twcrps/vs/spread_mr_b2/B2` | skill | 1855 (1854) | +0.176 | +0.185 | [+0.047, +0.291] | [+0.073, +0.292] |  |
| `/groups/pooled/all decision days/upper_tail_twcrps/vs/spread_mr_b2/spread_mr_level10` | skill | 1855 (1854) | -0.003 | -0.007 | [-0.053, +0.030] | [-0.056, +0.025] |  |
| `/groups/pooled/all decision days/upper_tail_twcrps/vs/spread_mr_ctx/B1` | skill | 1855 (1854) | +0.340 | +0.267 | [+0.260, +0.503] | [+0.189, +0.359] |  |
| `/groups/pooled/all decision days/upper_tail_twcrps/vs/spread_mr_ctx/B2` | skill | 1855 (1854) | +0.198 | +0.210 | [+0.069, +0.323] | [+0.102, +0.330] |  |
| `/groups/pooled/all decision days/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10` | skill | 1855 (1854) | +0.024 | +0.024 | [+0.002, +0.043] | [+0.002, +0.045] |  |
| `/groups/pooled/all decision days/upper_tail_twcrps/vs/spread_mr_ctx_b2/B1` | skill | 1855 (1854) | +0.335 | +0.258 | [+0.242, +0.503] | [+0.170, +0.357] |  |
| `/groups/pooled/all decision days/upper_tail_twcrps/vs/spread_mr_ctx_b2/B2` | skill | 1855 (1854) | +0.191 | +0.200 | [+0.077, +0.304] | [+0.102, +0.306] |  |
| `/groups/pooled/all decision days/upper_tail_twcrps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 1855 (1854) | +0.016 | +0.012 | [-0.042, +0.056] | [-0.043, +0.050] |  |
| `/groups/pooled/all decision days/upper_tail_twcrps/vs/spread_mr_level10/B1` | skill | 1855 (1854) | +0.324 | +0.249 | [+0.245, +0.487] | [+0.163, +0.346] |  |
| `/groups/pooled/all decision days/upper_tail_twcrps/vs/spread_mr_level10/B2` | skill | 1855 (1854) | +0.178 | +0.191 | [+0.031, +0.311] | [+0.068, +0.318] |  |
| `/groups/pressure_day_type/month_end/grid_crps/vs/spread_mr_b2/B1` | skill | 150 (150) | +0.048 | +0.048 | [-0.074, +0.153] | [-0.074, +0.153] |  |
| `/groups/pressure_day_type/month_end/grid_crps/vs/spread_mr_b2/B2` | skill | 150 (150) | +0.269 | +0.269 | [+0.145, +0.445] | [+0.145, +0.445] |  |
| `/groups/pressure_day_type/month_end/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 150 (150) | -0.020 | -0.020 | [-0.129, +0.063] | [-0.129, +0.063] |  |
| `/groups/pressure_day_type/month_end/grid_crps/vs/spread_mr_ctx/B1` | skill | 150 (150) | +0.057 | +0.057 | [-0.248, +0.194] | [-0.248, +0.194] |  |
| `/groups/pressure_day_type/month_end/grid_crps/vs/spread_mr_ctx/B2` | skill | 150 (150) | +0.276 | +0.276 | [+0.156, +0.399] | [+0.156, +0.399] |  |
| `/groups/pressure_day_type/month_end/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 150 (150) | -0.010 | -0.010 | [-0.307, +0.127] | [-0.307, +0.127] |  |
| `/groups/pressure_day_type/month_end/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 150 (150) | +0.022 | +0.022 | [-0.196, +0.184] | [-0.196, +0.184] |  |
| `/groups/pressure_day_type/month_end/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 150 (150) | +0.249 | +0.249 | [+0.160, +0.328] | [+0.160, +0.328] |  |
| `/groups/pressure_day_type/month_end/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 150 (150) | -0.047 | -0.047 | [-0.235, +0.106] | [-0.235, +0.106] |  |
| `/groups/pressure_day_type/month_end/grid_crps/vs/spread_mr_level10/B1` | skill | 150 (150) | +0.066 | +0.066 | [+0.026, +0.108] | [+0.026, +0.108] |  |
| `/groups/pressure_day_type/month_end/grid_crps/vs/spread_mr_level10/B2` | skill | 150 (150) | +0.283 | +0.283 | [+0.109, +0.429] | [+0.109, +0.429] |  |
| `/groups/pressure_day_type/ordinary/grid_crps/vs/B1_recentred/B1` | skill | 1590 (1590) | +0.195 | +0.117 | [+0.075, +0.801] | [+0.077, +0.180] |  |
| `/groups/pressure_day_type/ordinary/grid_crps/vs/B1_recentred/B2` | skill | 1590 (1590) | +0.222 | +0.222 | [+0.100, +0.323] | [+0.100, +0.323] |  |
| `/groups/pressure_day_type/ordinary/grid_crps/vs/spread_mr_b2/B1` | skill | 1590 (1590) | +0.285 | +0.222 | [+0.170, +0.551] | [+0.152, +0.314] |  |
| `/groups/pressure_day_type/ordinary/grid_crps/vs/spread_mr_b2/B2` | skill | 1590 (1590) | +0.309 | +0.315 | [+0.236, +0.382] | [+0.244, +0.387] |  |
| `/groups/pressure_day_type/ordinary/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 1590 (1590) | -0.001 | -0.004 | [-0.056, +0.038] | [-0.060, +0.034] |  |
| `/groups/pressure_day_type/ordinary/grid_crps/vs/spread_mr_ctx/B1` | skill | 1590 (1590) | +0.296 | +0.237 | [+0.190, +0.570] | [+0.177, +0.322] |  |
| `/groups/pressure_day_type/ordinary/grid_crps/vs/spread_mr_ctx/B2` | skill | 1590 (1590) | +0.320 | +0.328 | [+0.233, +0.401] | [+0.245, +0.407] |  |
| `/groups/pressure_day_type/ordinary/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 1590 (1590) | +0.015 | +0.015 | [+0.004, +0.025] | [+0.004, +0.025] |  |
| `/groups/pressure_day_type/ordinary/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 1590 (1590) | +0.296 | +0.234 | [+0.183, +0.547] | [+0.165, +0.321] |  |
| `/groups/pressure_day_type/ordinary/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 1590 (1590) | +0.320 | +0.325 | [+0.246, +0.393] | [+0.254, +0.397] |  |
| `/groups/pressure_day_type/ordinary/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 1590 (1590) | +0.014 | +0.011 | [-0.038, +0.051] | [-0.041, +0.048] |  |
| `/groups/pressure_day_type/ordinary/grid_crps/vs/spread_mr_level10/B1` | skill | 1590 (1590) | +0.286 | +0.226 | [+0.179, +0.592] | [+0.167, +0.316] |  |
| `/groups/pressure_day_type/ordinary/grid_crps/vs/spread_mr_level10/B2` | skill | 1590 (1590) | +0.310 | +0.318 | [+0.223, +0.392] | [+0.235, +0.397] |  |
| `/groups/pressure_day_type/ordinary/upper_tail_twcrps/vs/B1_recentred/B1` | skill | 1590 (1590) | +0.319 | +0.192 | [+0.121, +1.177] | [+0.128, +0.286] |  |
| `/groups/pressure_day_type/ordinary/upper_tail_twcrps/vs/B1_recentred/B2` | skill | 1590 (1590) | -0.015 | -0.015 | [-0.244, +0.137] | [-0.244, +0.136] |  |
| `/groups/pressure_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_b2/B1` | skill | 1590 (1590) | +0.459 | +0.371 | [+0.310, +0.734] | [+0.283, +0.470] |  |
| `/groups/pressure_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_b2/B2` | skill | 1590 (1590) | +0.194 | +0.210 | [+0.108, +0.282] | [+0.134, +0.293] |  |
| `/groups/pressure_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_b2/spread_mr_level10` | skill | 1590 (1590) | +0.016 | +0.009 | [-0.040, +0.063] | [-0.047, +0.056] |  |
| `/groups/pressure_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_ctx/B1` | skill | 1590 (1590) | +0.468 | +0.387 | [+0.334, +0.726] | [+0.313, +0.474] |  |
| `/groups/pressure_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_ctx/B2` | skill | 1590 (1590) | +0.208 | +0.230 | [+0.100, +0.312] | [+0.138, +0.327] |  |
| `/groups/pressure_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10` | skill | 1590 (1590) | +0.033 | +0.034 | [+0.009, +0.056] | [+0.009, +0.057] |  |
| `/groups/pressure_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_ctx_b2/B1` | skill | 1590 (1590) | +0.473 | +0.388 | [+0.326, +0.717] | [+0.298, +0.481] |  |
| `/groups/pressure_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_ctx_b2/B2` | skill | 1590 (1590) | +0.215 | +0.231 | [+0.125, +0.309] | [+0.151, +0.321] |  |
| `/groups/pressure_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 1590 (1590) | +0.042 | +0.036 | [-0.021, +0.093] | [-0.027, +0.087] |  |
| `/groups/pressure_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_level10/B1` | skill | 1590 (1590) | +0.450 | +0.365 | [+0.313, +0.754] | [+0.292, +0.463] |  |
| `/groups/pressure_day_type/ordinary/upper_tail_twcrps/vs/spread_mr_level10/B2` | skill | 1590 (1590) | +0.180 | +0.202 | [+0.072, +0.284] | [+0.109, +0.298] |  |
| `/groups/pressure_day_type/quarter_end/grid_crps/vs/spread_mr_b2/B1` | skill | 30 (30) | +0.098 | +0.098 | [-0.052, +0.206] | [-0.052, +0.206] |  |
| `/groups/pressure_day_type/quarter_end/grid_crps/vs/spread_mr_b2/B2` | skill | 30 (30) | +0.170 | +0.170 | [-0.151, +0.445] | [-0.151, +0.445] |  |
| `/groups/pressure_day_type/quarter_end/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 30 (30) | +0.126 | +0.126 | [+0.016, +0.280] | [+0.016, +0.280] |  |
| `/groups/pressure_day_type/quarter_end/grid_crps/vs/spread_mr_ctx/B1` | skill | 30 (30) | +0.067 | +0.067 | [-0.013, +0.108] | [-0.013, +0.108] |  |
| `/groups/pressure_day_type/quarter_end/grid_crps/vs/spread_mr_ctx/B2` | skill | 30 (30) | +0.142 | +0.142 | [-0.345, +0.458] | [-0.345, +0.458] |  |
| `/groups/pressure_day_type/quarter_end/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 30 (30) | +0.097 | +0.097 | [+0.039, +0.141] | [+0.039, +0.141] |  |
| `/groups/pressure_day_type/quarter_end/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 30 (30) | +0.143 | +0.143 | [-0.040, +0.249] | [-0.040, +0.249] |  |
| `/groups/pressure_day_type/quarter_end/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 30 (30) | +0.211 | +0.211 | [-0.099, +0.433] | [-0.099, +0.433] |  |
| `/groups/pressure_day_type/quarter_end/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 30 (30) | +0.170 | +0.170 | [+0.034, +0.286] | [+0.034, +0.286] |  |
| `/groups/pressure_day_type/quarter_end/grid_crps/vs/spread_mr_level10/B1` | skill | 30 (30) | -0.032 | -0.032 | [-0.073, -0.004] | [-0.073, -0.004] |  |
| `/groups/pressure_day_type/quarter_end/grid_crps/vs/spread_mr_level10/B2` | skill | 30 (30) | +0.050 | +0.050 | [-0.513, +0.453] | [-0.513, +0.453] |  |
| `/groups/pressure_day_type/tax_date/grid_crps/vs/B1_recentred/B1` | skill | 89 (89) | +0.002 | +0.002 | [-0.045, +0.038] | [-0.045, +0.038] |  |
| `/groups/pressure_day_type/tax_date/grid_crps/vs/B1_recentred/B2` | skill | 89 (89) | +0.291 | +0.291 | [-0.637, +0.560] | [-0.637, +0.560] |  |
| `/groups/pressure_day_type/tax_date/grid_crps/vs/spread_mr_b2/B1` | skill | 89 (89) | -0.030 | -0.030 | [-0.061, +0.006] | [-0.061, +0.006] |  |
| `/groups/pressure_day_type/tax_date/grid_crps/vs/spread_mr_b2/B2` | skill | 89 (89) | +0.268 | +0.268 | [-0.505, +0.518] | [-0.505, +0.518] |  |
| `/groups/pressure_day_type/tax_date/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 89 (89) | -0.047 | -0.047 | [-0.114, +0.036] | [-0.114, +0.036] |  |
| `/groups/pressure_day_type/tax_date/grid_crps/vs/spread_mr_ctx/B1` | skill | 89 (89) | +0.023 | +0.023 | [-0.031, +0.072] | [-0.031, +0.072] |  |
| `/groups/pressure_day_type/tax_date/grid_crps/vs/spread_mr_ctx/B2` | skill | 89 (89) | +0.306 | +0.306 | [-0.600, +0.522] | [-0.600, +0.522] |  |
| `/groups/pressure_day_type/tax_date/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 89 (89) | +0.007 | +0.007 | [-0.071, +0.075] | [-0.071, +0.075] |  |
| `/groups/pressure_day_type/tax_date/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 89 (89) | -0.019 | -0.019 | [-0.121, +0.061] | [-0.121, +0.061] |  |
| `/groups/pressure_day_type/tax_date/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 89 (89) | +0.277 | +0.277 | [-0.516, +0.484] | [-0.516, +0.484] |  |
| `/groups/pressure_day_type/tax_date/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 89 (89) | -0.035 | -0.035 | [-0.140, +0.099] | [-0.140, +0.099] |  |
| `/groups/pressure_day_type/tax_date/grid_crps/vs/spread_mr_level10/B1` | skill | 89 (89) | +0.016 | +0.016 | [-0.047, +0.073] | [-0.047, +0.073] |  |
| `/groups/pressure_day_type/tax_date/grid_crps/vs/spread_mr_level10/B2` | skill | 89 (89) | +0.301 | +0.301 | [-0.693, +0.557] | [-0.693, +0.557] |  |
| `/groups/regime/2018-19/grid_crps/vs/B1_recentred/B1` | skill | 361 (361) | +0.248 | +0.129 | [+0.125, +0.749] | [+0.077, +0.191] |  |
| `/groups/regime/2018-19/grid_crps/vs/B1_recentred/B2` | skill | 361 (361) | +0.024 | +0.024 | [-0.125, +0.143] | [-0.126, +0.143] |  |
| `/groups/regime/2018-19/grid_crps/vs/spread_mr_b2/B1` | skill | 361 (361) | +0.350 | +0.258 | [+0.253, +0.541] | [+0.128, +0.377] |  |
| `/groups/regime/2018-19/grid_crps/vs/spread_mr_b2/B2` | skill | 361 (361) | +0.156 | +0.168 | [-0.010, +0.292] | [+0.031, +0.291] | yes |
| `/groups/regime/2018-19/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 361 (361) | +0.016 | +0.011 | [-0.013, +0.045] | [-0.017, +0.040] |  |
| `/groups/regime/2018-19/grid_crps/vs/spread_mr_ctx/B1` | skill | 361 (361) | +0.362 | +0.276 | [+0.271, +0.538] | [+0.161, +0.386] |  |
| `/groups/regime/2018-19/grid_crps/vs/spread_mr_ctx/B2` | skill | 361 (361) | +0.172 | +0.189 | [+0.028, +0.326] | [+0.073, +0.328] |  |
| `/groups/regime/2018-19/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 361 (361) | +0.035 | +0.035 | [+0.017, +0.052] | [+0.017, +0.054] |  |
| `/groups/regime/2018-19/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 361 (361) | +0.368 | +0.279 | [+0.271, +0.548] | [+0.156, +0.393] |  |
| `/groups/regime/2018-19/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 361 (361) | +0.180 | +0.192 | [+0.032, +0.316] | [+0.068, +0.316] |  |
| `/groups/regime/2018-19/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 361 (361) | +0.044 | +0.039 | [+0.012, +0.078] | [+0.009, +0.072] |  |
| `/groups/regime/2018-19/grid_crps/vs/spread_mr_level10/B1` | skill | 361 (361) | +0.339 | +0.249 | [+0.249, +0.529] | [+0.126, +0.366] |  |
| `/groups/regime/2018-19/grid_crps/vs/spread_mr_level10/B2` | skill | 361 (361) | +0.142 | +0.159 | [-0.018, +0.301] | [+0.030, +0.301] | yes |
| `/groups/regime/2018-19/upper_tail_twcrps/vs/B1_recentred/B1` | skill | 361 (361) | +0.273 | +0.145 | [+0.148, +0.755] | [+0.080, +0.212] |  |
| `/groups/regime/2018-19/upper_tail_twcrps/vs/B1_recentred/B2` | skill | 361 (361) | -0.007 | -0.007 | [-0.189, +0.116] | [-0.190, +0.116] |  |
| `/groups/regime/2018-19/upper_tail_twcrps/vs/spread_mr_b2/B1` | skill | 361 (361) | +0.362 | +0.261 | [+0.257, +0.558] | [+0.108, +0.396] |  |
| `/groups/regime/2018-19/upper_tail_twcrps/vs/spread_mr_b2/B2` | skill | 361 (361) | +0.116 | +0.130 | [-0.034, +0.260] | [+0.005, +0.260] | yes |
| `/groups/regime/2018-19/upper_tail_twcrps/vs/spread_mr_b2/spread_mr_level10` | skill | 361 (361) | +0.024 | +0.018 | [-0.003, +0.053] | [-0.010, +0.050] |  |
| `/groups/regime/2018-19/upper_tail_twcrps/vs/spread_mr_ctx/B1` | skill | 361 (361) | +0.373 | +0.279 | [+0.273, +0.550] | [+0.143, +0.404] |  |
| `/groups/regime/2018-19/upper_tail_twcrps/vs/spread_mr_ctx/B2` | skill | 361 (361) | +0.131 | +0.151 | [-0.004, +0.290] | [+0.041, +0.293] | yes |
| `/groups/regime/2018-19/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10` | skill | 361 (361) | +0.041 | +0.041 | [+0.022, +0.059] | [+0.022, +0.060] |  |
| `/groups/regime/2018-19/upper_tail_twcrps/vs/spread_mr_ctx_b2/B1` | skill | 361 (361) | +0.382 | +0.285 | [+0.277, +0.563] | [+0.138, +0.413] |  |
| `/groups/regime/2018-19/upper_tail_twcrps/vs/spread_mr_ctx_b2/B2` | skill | 361 (361) | +0.144 | +0.158 | [+0.005, +0.291] | [+0.042, +0.292] |  |
| `/groups/regime/2018-19/upper_tail_twcrps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 361 (361) | +0.054 | +0.050 | [+0.025, +0.090] | [+0.021, +0.086] |  |
| `/groups/regime/2018-19/upper_tail_twcrps/vs/spread_mr_level10/B1` | skill | 361 (361) | +0.346 | +0.247 | [+0.247, +0.541] | [+0.108, +0.381] |  |
| `/groups/regime/2018-19/upper_tail_twcrps/vs/spread_mr_level10/B2` | skill | 361 (361) | +0.095 | +0.114 | [-0.051, +0.255] | [-0.002, +0.256] |  |
| `/groups/regime/2020/grid_crps/vs/B1_recentred/B1` | skill | 251 (251) | -0.011 | -0.011 | [-0.026, +0.001] | [-0.026, +0.001] |  |
| `/groups/regime/2020/grid_crps/vs/B1_recentred/B2` | skill | 251 (251) | +0.404 | +0.404 | [+0.041, +0.671] | [+0.041, +0.671] |  |
| `/groups/regime/2020/grid_crps/vs/spread_mr_b2/B1` | skill | 251 (251) | +0.027 | +0.027 | [-0.109, +0.160] | [-0.109, +0.160] |  |
| `/groups/regime/2020/grid_crps/vs/spread_mr_b2/B2` | skill | 251 (251) | +0.426 | +0.426 | [+0.193, +0.669] | [+0.193, +0.669] |  |
| `/groups/regime/2020/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 251 (251) | -0.035 | -0.035 | [-0.116, +0.009] | [-0.116, +0.009] |  |
| `/groups/regime/2020/grid_crps/vs/spread_mr_ctx/B1` | skill | 251 (251) | -0.004 | -0.004 | [-0.109, +0.157] | [-0.109, +0.157] |  |
| `/groups/regime/2020/grid_crps/vs/spread_mr_ctx/B2` | skill | 251 (251) | +0.409 | +0.409 | [+0.161, +0.663] | [+0.161, +0.663] |  |
| `/groups/regime/2020/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 251 (251) | -0.067 | -0.067 | [-0.098, -0.037] | [-0.098, -0.037] |  |
| `/groups/regime/2020/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 251 (251) | -0.021 | -0.021 | [-0.172, +0.137] | [-0.172, +0.137] |  |
| `/groups/regime/2020/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 251 (251) | +0.398 | +0.398 | [+0.164, +0.638] | [+0.164, +0.638] |  |
| `/groups/regime/2020/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 251 (251) | -0.087 | -0.087 | [-0.178, -0.029] | [-0.178, -0.029] |  |
| `/groups/regime/2020/grid_crps/vs/spread_mr_level10/B1` | skill | 251 (251) | +0.060 | +0.060 | [-0.025, +0.187] | [-0.025, +0.187] |  |
| `/groups/regime/2020/grid_crps/vs/spread_mr_level10/B2` | skill | 251 (251) | +0.446 | +0.446 | [+0.199, +0.691] | [+0.199, +0.691] |  |
| `/groups/regime/2020/upper_tail_twcrps/vs/B1_recentred/B1` | skill | 251 (251) | +0.009 | +0.009 | [-0.008, +0.028] | [-0.008, +0.028] |  |
| `/groups/regime/2020/upper_tail_twcrps/vs/B1_recentred/B2` | skill | 251 (251) | +0.398 | +0.398 | [-0.996, +0.766] | [-0.996, +0.766] |  |
| `/groups/regime/2020/upper_tail_twcrps/vs/spread_mr_b2/B1` | skill | 251 (251) | +0.132 | +0.132 | [-0.156, +0.970] | [-0.156, +0.970] |  |
| `/groups/regime/2020/upper_tail_twcrps/vs/spread_mr_b2/B2` | skill | 251 (251) | +0.473 | +0.473 | [+0.003, +0.706] | [+0.003, +0.706] |  |
| `/groups/regime/2020/upper_tail_twcrps/vs/spread_mr_b2/spread_mr_level10` | skill | 251 (251) | -0.095 | -0.095 | [-0.238, +0.043] | [-0.238, +0.043] |  |
| `/groups/regime/2020/upper_tail_twcrps/vs/spread_mr_ctx/B1` | skill | 251 (251) | +0.104 | +0.104 | [-0.191, +0.750] | [-0.191, +0.750] |  |
| `/groups/regime/2020/upper_tail_twcrps/vs/spread_mr_ctx/B2` | skill | 251 (251) | +0.456 | +0.456 | [-0.030, +0.712] | [-0.030, +0.712] |  |
| `/groups/regime/2020/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10` | skill | 251 (251) | -0.130 | -0.130 | [-0.246, -0.020] | [-0.246, -0.020] |  |
| `/groups/regime/2020/upper_tail_twcrps/vs/spread_mr_ctx_b2/B1` | skill | 251 (251) | +0.059 | +0.059 | [-0.289, +0.790] | [-0.289, +0.790] |  |
| `/groups/regime/2020/upper_tail_twcrps/vs/spread_mr_ctx_b2/B2` | skill | 251 (251) | +0.429 | +0.429 | [-0.003, +0.666] | [-0.003, +0.666] |  |
| `/groups/regime/2020/upper_tail_twcrps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 251 (251) | -0.187 | -0.187 | [-0.382, +0.011] | [-0.382, +0.011] |  |
| `/groups/regime/2020/upper_tail_twcrps/vs/spread_mr_level10/B1` | skill | 251 (251) | +0.207 | +0.207 | [-0.001, +1.012] | [-0.001, +1.012] |  |
| `/groups/regime/2020/upper_tail_twcrps/vs/spread_mr_level10/B2` | skill | 251 (251) | +0.519 | +0.519 | [-0.047, +0.765] | [-0.047, +0.765] |  |
| `/groups/regime/2021-23/grid_crps/vs/B1_recentred/B1` | skill | 748 (748) | +0.027 | +0.027 | [+0.008, +0.049] | [+0.008, +0.049] |  |
| `/groups/regime/2021-23/grid_crps/vs/B1_recentred/B2` | skill | 748 (748) | +0.537 | +0.537 | [+0.411, +0.643] | [+0.411, +0.643] |  |
| `/groups/regime/2021-23/grid_crps/vs/spread_mr_b2/B1` | skill | 748 (748) | -0.030 | -0.030 | [-0.083, +0.019] | [-0.083, +0.019] |  |
| `/groups/regime/2021-23/grid_crps/vs/spread_mr_b2/B2` | skill | 748 (748) | +0.510 | +0.510 | [+0.386, +0.610] | [+0.386, +0.610] |  |
| `/groups/regime/2021-23/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 748 (748) | -0.004 | -0.004 | [-0.019, +0.009] | [-0.019, +0.009] |  |
| `/groups/regime/2021-23/grid_crps/vs/spread_mr_ctx/B1` | skill | 748 (748) | -0.029 | -0.029 | [-0.085, +0.021] | [-0.085, +0.021] |  |
| `/groups/regime/2021-23/grid_crps/vs/spread_mr_ctx/B2` | skill | 748 (748) | +0.510 | +0.510 | [+0.388, +0.609] | [+0.388, +0.609] |  |
| `/groups/regime/2021-23/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 748 (748) | -0.003 | -0.003 | [-0.018, +0.008] | [-0.018, +0.008] |  |
| `/groups/regime/2021-23/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 748 (748) | -0.038 | -0.038 | [-0.099, +0.019] | [-0.099, +0.019] |  |
| `/groups/regime/2021-23/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 748 (748) | +0.506 | +0.506 | [+0.387, +0.602] | [+0.387, +0.602] |  |
| `/groups/regime/2021-23/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 748 (748) | -0.012 | -0.012 | [-0.036, +0.008] | [-0.036, +0.008] |  |
| `/groups/regime/2021-23/grid_crps/vs/spread_mr_level10/B1` | skill | 748 (748) | -0.026 | -0.026 | [-0.073, +0.017] | [-0.073, +0.017] |  |
| `/groups/regime/2021-23/grid_crps/vs/spread_mr_level10/B2` | skill | 748 (748) | +0.512 | +0.512 | [+0.386, +0.614] | [+0.386, +0.614] |  |
| `/groups/regime/2021-23/upper_tail_twcrps/vs/spread_mr_ctx/B1` | skill | 748 (748) | -0.922 | -0.922 | [-1.933, +0.423] | [-1.933, +0.423] |  |
| `/groups/regime/2021-23/upper_tail_twcrps/vs/spread_mr_ctx/B2` | skill | 748 (748) | -4.614 | -4.614 | [-7.985, -0.164] | [-7.985, -0.164] |  |
| `/groups/regime/2021-23/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10` | skill | 748 (748) | -0.377 | -0.377 | [-0.863, +0.091] | [-0.863, +0.091] |  |
| `/groups/regime/2021-23/upper_tail_twcrps/vs/spread_mr_ctx_b2/B1` | skill | 748 (748) | -0.818 | -0.818 | [-1.806, +0.471] | [-1.806, +0.471] |  |
| `/groups/regime/2021-23/upper_tail_twcrps/vs/spread_mr_ctx_b2/B2` | skill | 748 (748) | -4.312 | -4.312 | [-7.576, -0.169] | [-7.576, -0.169] |  |
| `/groups/regime/2021-23/upper_tail_twcrps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 748 (748) | -0.303 | -0.303 | [-0.796, +0.172] | [-0.796, +0.172] |  |
| `/groups/regime/2021-23/upper_tail_twcrps/vs/spread_mr_level10/B1` | skill | 748 (748) | -0.396 | -0.396 | [-0.749, +0.333] | [-0.749, +0.333] |  |
| `/groups/regime/2021-23/upper_tail_twcrps/vs/spread_mr_level10/B2` | skill | 748 (748) | -3.077 | -3.077 | [-5.047, +0.022] | [-5.047, +0.022] |  |
| `/groups/regime/2024/grid_crps/vs/B1_recentred/B1` | skill | 250 (250) | +0.080 | +0.080 | [+0.047, +0.126] | [+0.047, +0.126] |  |
| `/groups/regime/2024/grid_crps/vs/B1_recentred/B2` | skill | 250 (250) | -0.065 | -0.065 | [-0.315, +0.102] | [-0.315, +0.102] |  |
| `/groups/regime/2024/grid_crps/vs/spread_mr_b2/B1` | skill | 250 (250) | +0.234 | +0.234 | [+0.148, +0.348] | [+0.148, +0.348] |  |
| `/groups/regime/2024/grid_crps/vs/spread_mr_b2/B2` | skill | 250 (250) | +0.114 | +0.114 | [-0.001, +0.220] | [-0.001, +0.220] |  |
| `/groups/regime/2024/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 250 (250) | +0.042 | +0.042 | [+0.006, +0.076] | [+0.006, +0.076] |  |
| `/groups/regime/2024/grid_crps/vs/spread_mr_ctx/B1` | skill | 250 (250) | +0.222 | +0.222 | [+0.130, +0.318] | [+0.130, +0.318] |  |
| `/groups/regime/2024/grid_crps/vs/spread_mr_ctx/B2` | skill | 250 (250) | +0.099 | +0.099 | [-0.049, +0.227] | [-0.049, +0.227] |  |
| `/groups/regime/2024/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 250 (250) | +0.026 | +0.026 | [+0.000, +0.048] | [+0.000, +0.048] |  |
| `/groups/regime/2024/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 250 (250) | +0.250 | +0.250 | [+0.158, +0.366] | [+0.158, +0.366] |  |
| `/groups/regime/2024/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 250 (250) | +0.133 | +0.133 | [+0.013, +0.236] | [+0.013, +0.236] |  |
| `/groups/regime/2024/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 250 (250) | +0.062 | +0.062 | [+0.019, +0.100] | [+0.019, +0.100] |  |
| `/groups/regime/2024/grid_crps/vs/spread_mr_level10/B1` | skill | 250 (250) | +0.201 | +0.201 | [+0.126, +0.295] | [+0.126, +0.295] |  |
| `/groups/regime/2024/grid_crps/vs/spread_mr_level10/B2` | skill | 250 (250) | +0.075 | +0.075 | [-0.065, +0.204] | [-0.065, +0.204] |  |
| `/groups/regime/2025-26/grid_crps/vs/B1_recentred/B1` | skill | 249 (249) | +0.083 | +0.083 | [+0.049, +0.127] | [+0.049, +0.127] |  |
| `/groups/regime/2025-26/grid_crps/vs/B1_recentred/B2` | skill | 249 (249) | +0.185 | +0.185 | [-0.069, +0.405] | [-0.069, +0.405] |  |
| `/groups/regime/2025-26/grid_crps/vs/spread_mr_b2/B1` | skill | 249 (249) | +0.145 | +0.145 | [-0.034, +0.273] | [-0.034, +0.273] |  |
| `/groups/regime/2025-26/grid_crps/vs/spread_mr_b2/B2` | skill | 249 (249) | +0.240 | +0.240 | [+0.106, +0.397] | [+0.106, +0.397] |  |
| `/groups/regime/2025-26/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 249 (249) | -0.035 | -0.035 | [-0.260, +0.108] | [-0.260, +0.108] |  |
| `/groups/regime/2025-26/grid_crps/vs/spread_mr_ctx/B1` | skill | 249 (249) | +0.206 | +0.206 | [+0.120, +0.292] | [+0.120, +0.292] |  |
| `/groups/regime/2025-26/grid_crps/vs/spread_mr_ctx/B2` | skill | 249 (249) | +0.294 | +0.294 | [+0.054, +0.485] | [+0.054, +0.485] |  |
| `/groups/regime/2025-26/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 249 (249) | +0.038 | +0.038 | [+0.014, +0.063] | [+0.014, +0.063] |  |
| `/groups/regime/2025-26/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 249 (249) | +0.170 | +0.170 | [-0.014, +0.299] | [-0.014, +0.299] |  |
| `/groups/regime/2025-26/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 249 (249) | +0.262 | +0.262 | [+0.122, +0.422] | [+0.122, +0.422] |  |
| `/groups/regime/2025-26/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 249 (249) | -0.005 | -0.005 | [-0.243, +0.130] | [-0.243, +0.130] |  |
| `/groups/regime/2025-26/grid_crps/vs/spread_mr_level10/B1` | skill | 249 (249) | +0.174 | +0.174 | [+0.097, +0.250] | [+0.097, +0.250] |  |
| `/groups/regime/2025-26/grid_crps/vs/spread_mr_level10/B2` | skill | 249 (249) | +0.266 | +0.266 | [+0.021, +0.459] | [+0.021, +0.459] |  |
| `/groups/regime/2025-26/upper_tail_twcrps/vs/B1_recentred/B1` | skill | 249 (249) | +0.128 | +0.128 | [+0.077, +0.183] | [+0.077, +0.183] |  |
| `/groups/regime/2025-26/upper_tail_twcrps/vs/B1_recentred/B2` | skill | 249 (249) | +0.092 | +0.092 | [-0.144, +0.371] | [-0.144, +0.371] |  |
| `/groups/regime/2025-26/upper_tail_twcrps/vs/spread_mr_b2/B1` | skill | 249 (249) | +0.222 | +0.222 | [-0.087, +0.402] | [-0.087, +0.402] |  |
| `/groups/regime/2025-26/upper_tail_twcrps/vs/spread_mr_b2/B2` | skill | 249 (249) | +0.190 | +0.190 | [+0.124, +0.268] | [+0.124, +0.268] |  |
| `/groups/regime/2025-26/upper_tail_twcrps/vs/spread_mr_b2/spread_mr_level10` | skill | 249 (249) | -0.078 | -0.078 | [-0.323, +0.071] | [-0.323, +0.071] |  |
| `/groups/regime/2025-26/upper_tail_twcrps/vs/spread_mr_ctx/B1` | skill | 249 (249) | +0.317 | +0.317 | [+0.185, +0.426] | [+0.185, +0.426] |  |
| `/groups/regime/2025-26/upper_tail_twcrps/vs/spread_mr_ctx/B2` | skill | 249 (249) | +0.289 | +0.289 | [+0.192, +0.424] | [+0.192, +0.424] |  |
| `/groups/regime/2025-26/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10` | skill | 249 (249) | +0.052 | +0.052 | [+0.007, +0.096] | [+0.007, +0.096] |  |
| `/groups/regime/2025-26/upper_tail_twcrps/vs/spread_mr_ctx_b2/B1` | skill | 249 (249) | +0.253 | +0.253 | [-0.104, +0.444] | [-0.104, +0.444] |  |
| `/groups/regime/2025-26/upper_tail_twcrps/vs/spread_mr_ctx_b2/B2` | skill | 249 (249) | +0.222 | +0.222 | [+0.134, +0.336] | [+0.134, +0.336] |  |
| `/groups/regime/2025-26/upper_tail_twcrps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 249 (249) | -0.037 | -0.037 | [-0.383, +0.139] | [-0.383, +0.139] |  |
| `/groups/regime/2025-26/upper_tail_twcrps/vs/spread_mr_level10/B1` | skill | 249 (249) | +0.279 | +0.279 | [+0.164, +0.375] | [+0.164, +0.375] |  |
| `/groups/regime/2025-26/upper_tail_twcrps/vs/spread_mr_level10/B2` | skill | 249 (249) | +0.249 | +0.249 | [+0.143, +0.391] | [+0.143, +0.391] |  |
| `/groups/scarcity_state/ample/grid_crps/vs/B1_recentred/B1` | skill | 1354 (1354) | +0.040 | +0.040 | [+0.024, +0.059] | [+0.024, +0.059] |  |
| `/groups/scarcity_state/ample/grid_crps/vs/B1_recentred/B2` | skill | 1354 (1354) | +0.304 | +0.304 | [+0.151, +0.433] | [+0.151, +0.433] |  |
| `/groups/scarcity_state/ample/grid_crps/vs/spread_mr_b2/B1` | skill | 1354 (1354) | +0.113 | +0.113 | [+0.056, +0.175] | [+0.056, +0.175] |  |
| `/groups/scarcity_state/ample/grid_crps/vs/spread_mr_b2/B2` | skill | 1354 (1354) | +0.356 | +0.356 | [+0.252, +0.464] | [+0.252, +0.464] |  |
| `/groups/scarcity_state/ample/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 1354 (1354) | +0.038 | +0.038 | [+0.004, +0.074] | [+0.004, +0.074] |  |
| `/groups/scarcity_state/ample/grid_crps/vs/spread_mr_ctx/B1` | skill | 1354 (1354) | +0.079 | +0.079 | [+0.027, +0.135] | [+0.027, +0.135] |  |
| `/groups/scarcity_state/ample/grid_crps/vs/spread_mr_ctx/B2` | skill | 1354 (1354) | +0.331 | +0.331 | [+0.212, +0.445] | [+0.212, +0.445] |  |
| `/groups/scarcity_state/ample/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 1354 (1354) | +0.001 | +0.001 | [-0.014, +0.014] | [-0.014, +0.014] |  |
| `/groups/scarcity_state/ample/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 1354 (1354) | +0.104 | +0.104 | [+0.041, +0.172] | [+0.041, +0.172] |  |
| `/groups/scarcity_state/ample/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 1354 (1354) | +0.349 | +0.349 | [+0.248, +0.453] | [+0.248, +0.453] |  |
| `/groups/scarcity_state/ample/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 1354 (1354) | +0.027 | +0.027 | [-0.012, +0.066] | [-0.012, +0.066] |  |
| `/groups/scarcity_state/ample/grid_crps/vs/spread_mr_level10/B1` | skill | 1354 (1354) | +0.078 | +0.078 | [+0.033, +0.128] | [+0.033, +0.128] |  |
| `/groups/scarcity_state/ample/grid_crps/vs/spread_mr_level10/B2` | skill | 1354 (1354) | +0.331 | +0.331 | [+0.207, +0.450] | [+0.207, +0.450] |  |
| `/groups/scarcity_state/ample/upper_tail_twcrps/vs/B1_recentred/B1` | skill | 1354 (1354) | +0.051 | +0.051 | [-0.011, +0.126] | [-0.011, +0.126] |  |
| `/groups/scarcity_state/ample/upper_tail_twcrps/vs/B1_recentred/B2` | skill | 1354 (1354) | +0.221 | +0.221 | [-0.391, +0.662] | [-0.391, +0.662] |  |
| `/groups/scarcity_state/ample/upper_tail_twcrps/vs/spread_mr_b2/B1` | skill | 1354 (1354) | +0.204 | +0.204 | [+0.017, +0.534] | [+0.017, +0.534] |  |
| `/groups/scarcity_state/ample/upper_tail_twcrps/vs/spread_mr_b2/B2` | skill | 1354 (1354) | +0.347 | +0.347 | [+0.029, +0.717] | [+0.029, +0.717] |  |
| `/groups/scarcity_state/ample/upper_tail_twcrps/vs/spread_mr_b2/spread_mr_level10` | skill | 1354 (1354) | -0.004 | -0.004 | [-0.052, +0.038] | [-0.052, +0.038] |  |
| `/groups/scarcity_state/ample/upper_tail_twcrps/vs/spread_mr_ctx/B1` | skill | 1354 (1354) | +0.102 | +0.102 | [-0.153, +0.456] | [-0.153, +0.456] |  |
| `/groups/scarcity_state/ample/upper_tail_twcrps/vs/spread_mr_ctx/B2` | skill | 1354 (1354) | +0.263 | +0.263 | [-0.077, +0.657] | [-0.077, +0.657] |  |
| `/groups/scarcity_state/ample/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10` | skill | 1354 (1354) | -0.132 | -0.132 | [-0.250, -0.047] | [-0.250, -0.047] |  |
| `/groups/scarcity_state/ample/upper_tail_twcrps/vs/spread_mr_ctx_b2/B1` | skill | 1354 (1354) | +0.104 | +0.104 | [-0.173, +0.481] | [-0.173, +0.481] |  |
| `/groups/scarcity_state/ample/upper_tail_twcrps/vs/spread_mr_ctx_b2/B2` | skill | 1354 (1354) | +0.265 | +0.265 | [-0.050, +0.628] | [-0.050, +0.628] |  |
| `/groups/scarcity_state/ample/upper_tail_twcrps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 1354 (1354) | -0.129 | -0.129 | [-0.286, -0.018] | [-0.286, -0.018] |  |
| `/groups/scarcity_state/ample/upper_tail_twcrps/vs/spread_mr_level10/B1` | skill | 1354 (1354) | +0.207 | +0.207 | [+0.042, +0.514] | [+0.042, +0.514] |  |
| `/groups/scarcity_state/ample/upper_tail_twcrps/vs/spread_mr_level10/B2` | skill | 1354 (1354) | +0.349 | +0.349 | [+0.004, +0.740] | [+0.004, +0.740] |  |
| `/groups/scarcity_state/scarce/grid_crps/vs/B1_recentred/B1` | skill | 501 (500) | +0.213 | +0.115 | [+0.102, +0.673] | [+0.077, +0.165] |  |
| `/groups/scarcity_state/scarce/grid_crps/vs/B1_recentred/B2` | skill | 501 (500) | +0.158 | +0.157 | [+0.001, +0.296] | [-0.003, +0.297] | yes |
| `/groups/scarcity_state/scarce/grid_crps/vs/spread_mr_b2/B1` | skill | 501 (500) | +0.288 | +0.208 | [+0.184, +0.486] | [+0.117, +0.313] |  |
| `/groups/scarcity_state/scarce/grid_crps/vs/spread_mr_b2/B2` | skill | 501 (500) | +0.238 | +0.246 | [+0.087, +0.351] | [+0.114, +0.351] |  |
| `/groups/scarcity_state/scarce/grid_crps/vs/spread_mr_b2/spread_mr_level10` | skill | 501 (500) | -0.031 | -0.036 | [-0.116, +0.018] | [-0.120, +0.012] |  |
| `/groups/scarcity_state/scarce/grid_crps/vs/spread_mr_ctx/B1` | skill | 501 (500) | +0.328 | +0.257 | [+0.246, +0.502] | [+0.183, +0.346] |  |
| `/groups/scarcity_state/scarce/grid_crps/vs/spread_mr_ctx/B2` | skill | 501 (500) | +0.282 | +0.292 | [+0.119, +0.417] | [+0.153, +0.420] |  |
| `/groups/scarcity_state/scarce/grid_crps/vs/spread_mr_ctx/spread_mr_level10` | skill | 501 (500) | +0.028 | +0.028 | [+0.008, +0.045] | [+0.008, +0.047] |  |
| `/groups/scarcity_state/scarce/grid_crps/vs/spread_mr_ctx_b2/B1` | skill | 501 (500) | +0.308 | +0.231 | [+0.203, +0.499] | [+0.142, +0.332] |  |
| `/groups/scarcity_state/scarce/grid_crps/vs/spread_mr_ctx_b2/B2` | skill | 501 (500) | +0.260 | +0.268 | [+0.121, +0.371] | [+0.146, +0.372] |  |
| `/groups/scarcity_state/scarce/grid_crps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 501 (500) | -0.002 | -0.006 | [-0.085, +0.050] | [-0.088, +0.044] |  |
| `/groups/scarcity_state/scarce/grid_crps/vs/spread_mr_level10/B1` | skill | 501 (500) | +0.309 | +0.236 | [+0.230, +0.491] | [+0.158, +0.327] |  |
| `/groups/scarcity_state/scarce/grid_crps/vs/spread_mr_level10/B2` | skill | 501 (500) | +0.261 | +0.272 | [+0.082, +0.405] | [+0.117, +0.406] |  |
| `/groups/scarcity_state/scarce/upper_tail_twcrps/vs/B1_recentred/B1` | skill | 501 (500) | +0.238 | +0.132 | [+0.124, +0.691] | [+0.087, +0.184] |  |
| `/groups/scarcity_state/scarce/upper_tail_twcrps/vs/B1_recentred/B2` | skill | 501 (500) | +0.043 | +0.041 | [-0.113, +0.159] | [-0.116, +0.159] |  |
| `/groups/scarcity_state/scarce/upper_tail_twcrps/vs/spread_mr_b2/B1` | skill | 501 (500) | +0.330 | +0.246 | [+0.232, +0.505] | [+0.144, +0.355] |  |
| `/groups/scarcity_state/scarce/upper_tail_twcrps/vs/spread_mr_b2/B2` | skill | 501 (500) | +0.158 | +0.168 | [+0.030, +0.269] | [+0.056, +0.273] |  |
| `/groups/scarcity_state/scarce/upper_tail_twcrps/vs/spread_mr_b2/spread_mr_level10` | skill | 501 (500) | -0.003 | -0.007 | [-0.057, +0.033] | [-0.059, +0.027] |  |
| `/groups/scarcity_state/scarce/upper_tail_twcrps/vs/spread_mr_ctx/B1` | skill | 501 (500) | +0.356 | +0.280 | [+0.273, +0.516] | [+0.191, +0.378] |  |
| `/groups/scarcity_state/scarce/upper_tail_twcrps/vs/spread_mr_ctx/B2` | skill | 501 (500) | +0.191 | +0.205 | [+0.058, +0.322] | [+0.093, +0.326] |  |
| `/groups/scarcity_state/scarce/upper_tail_twcrps/vs/spread_mr_ctx/spread_mr_level10` | skill | 501 (500) | +0.036 | +0.037 | [+0.018, +0.053] | [+0.017, +0.055] |  |
| `/groups/scarcity_state/scarce/upper_tail_twcrps/vs/spread_mr_ctx_b2/B1` | skill | 501 (500) | +0.350 | +0.270 | [+0.252, +0.520] | [+0.170, +0.374] |  |
| `/groups/scarcity_state/scarce/upper_tail_twcrps/vs/spread_mr_ctx_b2/B2` | skill | 501 (500) | +0.184 | +0.194 | [+0.066, +0.295] | [+0.094, +0.297] |  |
| `/groups/scarcity_state/scarce/upper_tail_twcrps/vs/spread_mr_ctx_b2/spread_mr_level10` | skill | 501 (500) | +0.028 | +0.024 | [-0.029, +0.068] | [-0.031, +0.063] |  |
| `/groups/scarcity_state/scarce/upper_tail_twcrps/vs/spread_mr_level10/B1` | skill | 501 (500) | +0.332 | +0.252 | [+0.248, +0.501] | [+0.157, +0.356] |  |
| `/groups/scarcity_state/scarce/upper_tail_twcrps/vs/spread_mr_level10/B2` | skill | 501 (500) | +0.160 | +0.174 | [+0.016, +0.297] | [+0.053, +0.304] |  |
| `/published/candidate_vs/B1_recentred` | skill | 1855 (1854) | -0.082 | -0.082 | [-0.155, -0.037] | [-0.156, -0.037] |  |
| `/published/candidate_vs/spread_mr_b2` | skill | 1855 (1854) | +0.014 | +0.020 | [-0.034, +0.057] | [-0.027, +0.061] |  |
| `/published/candidate_vs/spread_mr_ctx` | skill | 1855 (1854) | +0.031 | +0.040 | [-0.008, +0.068] | [+0.001, +0.076] | yes |
| `/published/candidate_vs/spread_mr_ctx_b2` | skill | 1855 (1854) | +0.027 | +0.033 | [-0.021, +0.070] | [-0.017, +0.075] |  |
| `/published/candidate_vs/spread_mr_level10` | skill | 1855 (1854) | +0.012 | +0.020 | [-0.029, +0.049] | [-0.014, +0.054] |  |

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
