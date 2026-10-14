# Upper-bound study: tables (#635)

Scored days 1873 (2018-06-29 to 2025-12-31), of which ordinary 1469; ordinary pressure days 82 of 140.
Decision days with all five leads: 1868 in the ceiling window (cross-fitted ceiling; `memorised` is the first declaration's in-sample fit), 1598 on the walk-forward days (first 2019-07-31).

## The spread: grid CRPS averaged over leads 1 to 5

### Walk-forward days, ordinary days (the primary cell)

1598 decision days, 10000 draws. Skill = (benchmark mean - candidate mean) / benchmark mean; positive favours the candidate. Interval: 5th to 95th percentile of the paired skill draws.

| candidate | benchmark | benchmark mean | candidate mean | skill [90%] | lower bound of mean difference (one-sided 95%) | bootstrap p | DM p |
|---|---|---|---|---|---|---|---|
| ceiling gbm | B1 | 1.718 | 1.440 | +0.162 [-0.009, +0.310] | -0.012 | 0.061 | 0.093 |
| ceiling ridge | B1 | 1.718 | 3.576 | -1.081 [-1.683, -0.634] | -2.307 | 1.000 | 1.000 |
| memorised gbm | B1 | 1.718 | 0.372 | +0.784 [+0.740, +0.823] | +0.973 | 0.000 | 0.000 |
| memorised ridge | B1 | 1.718 | 1.481 | +0.138 [-0.061, +0.295] | -0.080 | 0.149 | 0.149 |
| reachable gbm | B1 | 1.718 | 1.388 | +0.192 [+0.007, +0.352] | +0.010 | 0.041 | 0.073 |
| reachable ridge | B1 | 1.718 | 3.804 | -1.213 [-2.114, -0.620] | -3.232 | 1.000 | 1.000 |
| ceiling gbm | B2 | 1.954 | 1.440 | +0.263 [+0.176, +0.349] | +0.325 | 0.000 | 0.000 |
| ceiling ridge | B2 | 1.954 | 3.576 | -0.830 [-1.109, -0.604] | -1.977 | 1.000 | 1.000 |
| memorised gbm | B2 | 1.954 | 0.372 | +0.810 [+0.779, +0.838] | +1.320 | 0.000 | 0.000 |
| memorised ridge | B2 | 1.954 | 1.481 | +0.242 [+0.131, +0.334] | +0.225 | 0.000 | 0.000 |
| reachable gbm | B2 | 1.954 | 1.388 | +0.290 [+0.227, +0.351] | +0.401 | 0.000 | 0.000 |
| reachable ridge | B2 | 1.954 | 3.804 | -0.947 [-1.421, -0.557] | -2.860 | 1.000 | 1.000 |
| ceiling gbm | reachable gbm | 1.388 | 1.440 | -0.037 [-0.124, +0.049] | -0.175 | 0.750 | 0.791 |
| memorised gbm | reachable gbm | 1.388 | 0.372 | +0.732 [+0.706, +0.758] | +0.860 | 0.000 | 0.000 |
| ceiling ridge | reachable ridge | 3.804 | 3.576 | +0.060 [-0.185, +0.265] | -0.561 | 0.381 | 0.323 |
| memorised ridge | reachable ridge | 3.804 | 1.481 | +0.611 [+0.505, +0.699] | +1.497 | 0.000 | 0.000 |

### Walk-forward days, all days

1598 decision days, 10000 draws. Skill = (benchmark mean - candidate mean) / benchmark mean; positive favours the candidate. Interval: 5th to 95th percentile of the paired skill draws.

| candidate | benchmark | benchmark mean | candidate mean | skill [90%] | lower bound of mean difference (one-sided 95%) | bootstrap p | DM p |
|---|---|---|---|---|---|---|---|
| ceiling gbm | B1 | 2.026 | 1.720 | +0.151 [+0.010, +0.261] | +0.015 | 0.038 | 0.071 |
| ceiling ridge | B1 | 2.026 | 3.867 | -0.909 [-1.560, -0.473] | -2.315 | 1.000 | 1.000 |
| memorised gbm | B1 | 2.026 | 0.541 | +0.733 [+0.684, +0.781] | +1.044 | 0.000 | 0.000 |
| memorised ridge | B1 | 2.026 | 1.746 | +0.138 [-0.072, +0.284] | -0.103 | 0.163 | 0.155 |
| reachable gbm | B1 | 2.026 | 1.672 | +0.175 [+0.023, +0.288] | +0.037 | 0.026 | 0.055 |
| reachable ridge | B1 | 2.026 | 4.282 | -1.114 [-2.022, -0.562] | -3.382 | 1.000 | 1.000 |
| ceiling gbm | B2 | 2.348 | 1.720 | +0.267 [+0.175, +0.368] | +0.415 | 0.000 | 0.000 |
| ceiling ridge | B2 | 2.348 | 3.867 | -0.647 [-0.915, -0.446] | -1.878 | 1.000 | 1.000 |
| memorised gbm | B2 | 2.348 | 0.541 | +0.769 [+0.696, +0.836] | +1.485 | 0.000 | 0.000 |
| memorised ridge | B2 | 2.348 | 1.746 | +0.256 [+0.163, +0.339] | +0.327 | 0.000 | 0.000 |
| reachable gbm | B2 | 2.348 | 1.672 | +0.288 [+0.213, +0.366] | +0.487 | 0.000 | 0.000 |
| reachable ridge | B2 | 2.348 | 4.282 | -0.824 [-1.229, -0.509] | -2.886 | 1.000 | 1.000 |
| ceiling gbm | reachable gbm | 1.672 | 1.720 | -0.029 [-0.097, +0.044] | -0.170 | 0.742 | 0.783 |
| memorised gbm | reachable gbm | 1.672 | 0.541 | +0.676 [+0.605, +0.747] | +0.924 | 0.000 | 0.000 |
| ceiling ridge | reachable ridge | 4.282 | 3.867 | +0.097 [-0.102, +0.271] | -0.364 | 0.238 | 0.195 |
| memorised ridge | reachable ridge | 4.282 | 1.746 | +0.592 [+0.496, +0.681] | +1.718 | 0.000 | 0.000 |

### Walk-forward days, risk dates

975 decision days, 2000 draws. Skill = (benchmark mean - candidate mean) / benchmark mean; positive favours the candidate. Interval: 5th to 95th percentile of the paired skill draws.

| candidate | benchmark | benchmark mean | candidate mean | skill [90%] | lower bound of mean difference (one-sided 95%) | bootstrap p | DM p |
|---|---|---|---|---|---|---|---|
| ceiling gbm | B1 | 2.554 | 2.570 | -0.006 [-0.094, +0.091] | -0.227 | 0.530 | 0.552 |
| ceiling ridge | B1 | 2.554 | 4.586 | -0.796 [-1.608, -0.390] | -2.552 | 1.000 | 1.000 |
| memorised gbm | B1 | 2.554 | 1.015 | +0.603 [+0.507, +0.742] | +1.053 | 0.000 | 0.000 |
| memorised ridge | B1 | 2.554 | 2.457 | +0.038 [-0.232, +0.165] | -0.349 | 0.416 | 0.362 |
| reachable gbm | B1 | 2.554 | 2.535 | +0.007 [-0.095, +0.097] | -0.198 | 0.426 | 0.437 |
| reachable ridge | B1 | 2.554 | 5.828 | -1.282 [-2.561, -0.660] | -4.669 | 1.000 | 1.000 |
| ceiling gbm | B2 | 3.628 | 2.570 | +0.292 [+0.164, +0.454] | +0.656 | 0.000 | 0.000 |
| ceiling ridge | B2 | 3.628 | 4.586 | -0.264 [-0.576, -0.087] | -1.534 | 0.998 | 0.998 |
| memorised gbm | B2 | 3.628 | 1.015 | +0.720 [+0.603, +0.853] | +1.963 | 0.000 | 0.000 |
| memorised ridge | B2 | 3.628 | 2.457 | +0.323 [+0.221, +0.408] | +0.575 | 0.000 | 0.000 |
| reachable gbm | B2 | 3.628 | 2.535 | +0.301 [+0.185, +0.441] | +0.717 | 0.000 | 0.000 |
| reachable ridge | B2 | 3.628 | 5.828 | -0.606 [-1.093, -0.303] | -3.353 | 1.000 | 1.000 |
| ceiling gbm | reachable gbm | 2.535 | 2.570 | -0.014 [-0.076, +0.059] | -0.203 | 0.622 | 0.662 |
| memorised gbm | reachable gbm | 2.535 | 1.015 | +0.600 [+0.510, +0.742] | +1.068 | 0.000 | 0.000 |
| ceiling ridge | reachable ridge | 5.828 | 4.586 | +0.213 [+0.042, +0.359] | +0.176 | 0.021 | 0.034 |
| memorised ridge | reachable ridge | 5.828 | 2.457 | +0.578 [+0.475, +0.682] | +2.195 | 0.000 | 0.000 |

### Ceiling window (all scored days; ceiling cross-fitted, memorised in-sample), ordinary days

1868 decision days, 10000 draws. Skill = (benchmark mean - candidate mean) / benchmark mean; positive favours the candidate. Interval: 5th to 95th percentile of the paired skill draws.

| candidate | benchmark | benchmark mean | candidate mean | skill [90%] | lower bound of mean difference (one-sided 95%) | bootstrap p | DM p |
|---|---|---|---|---|---|---|---|
| ceiling gbm | B1 | 1.966 | 1.682 | +0.144 [+0.000, +0.271] | +0.000 | 0.050 | 0.075 |
| ceiling ridge | B1 | 1.966 | 4.243 | -1.158 [-1.682, -0.753] | -2.778 | 1.000 | 1.000 |
| memorised gbm | B1 | 1.966 | 0.430 | +0.781 [+0.747, +0.815] | +1.178 | 0.000 | 0.000 |
| memorised ridge | B1 | 1.966 | 1.642 | +0.165 [+0.007, +0.294] | +0.011 | 0.043 | 0.067 |
| ceiling gbm | B2 | 2.112 | 1.682 | +0.203 [+0.123, +0.280] | +0.247 | 0.000 | 0.000 |
| ceiling ridge | B2 | 2.112 | 4.243 | -1.009 [-1.314, -0.752] | -2.572 | 1.000 | 1.000 |
| memorised gbm | B2 | 2.112 | 0.430 | +0.796 [+0.767, +0.824] | +1.436 | 0.000 | 0.000 |
| memorised ridge | B2 | 2.112 | 1.642 | +0.223 [+0.129, +0.302] | +0.243 | 0.000 | 0.000 |

### Ceiling window (all scored days; ceiling cross-fitted, memorised in-sample), all days

1868 decision days, 10000 draws. Skill = (benchmark mean - candidate mean) / benchmark mean; positive favours the candidate. Interval: 5th to 95th percentile of the paired skill draws.

| candidate | benchmark | benchmark mean | candidate mean | skill [90%] | lower bound of mean difference (one-sided 95%) | bootstrap p | DM p |
|---|---|---|---|---|---|---|---|
| ceiling gbm | B1 | 2.302 | 1.954 | +0.152 [+0.035, +0.246] | +0.064 | 0.013 | 0.037 |
| ceiling ridge | B1 | 2.302 | 4.502 | -0.955 [-1.479, -0.564] | -2.712 | 1.000 | 1.000 |
| memorised gbm | B1 | 2.302 | 0.594 | +0.742 [+0.702, +0.780] | +1.292 | 0.000 | 0.000 |
| memorised ridge | B1 | 2.302 | 1.895 | +0.177 [+0.021, +0.294] | +0.036 | 0.031 | 0.056 |
| ceiling gbm | B2 | 2.514 | 1.954 | +0.223 [+0.144, +0.303] | +0.362 | 0.000 | 0.000 |
| ceiling ridge | B2 | 2.514 | 4.502 | -0.791 [-1.068, -0.566] | -2.426 | 1.000 | 1.000 |
| memorised gbm | B2 | 2.514 | 0.594 | +0.764 [+0.702, +0.818] | +1.629 | 0.000 | 0.000 |
| memorised ridge | B2 | 2.514 | 1.895 | +0.246 [+0.167, +0.316] | +0.366 | 0.000 | 0.000 |

## Splits (walk-forward days; grid CRPS, 2000 draws)

### day type: month_end

433 decision days, 2000 draws. Skill = (benchmark mean - candidate mean) / benchmark mean; positive favours the candidate. Interval: 5th to 95th percentile of the paired skill draws.

| candidate | benchmark | benchmark mean | candidate mean | skill [90%] | lower bound of mean difference (one-sided 95%) | bootstrap p | DM p |
|---|---|---|---|---|---|---|---|
| ceiling gbm | B1 | 1.830 | 1.635 | +0.107 [-0.069, +0.272] | -0.120 | 0.154 | 0.147 |
| ceiling ridge | B1 | 1.830 | 3.673 | -1.007 [-1.693, -0.555] | -2.525 | 1.000 | 1.000 |
| memorised gbm | B1 | 1.830 | 0.455 | +0.752 [+0.709, +0.788] | +0.974 | 0.000 | 0.000 |
| memorised ridge | B1 | 1.830 | 1.718 | +0.061 [-0.135, +0.206] | -0.193 | 0.289 | 0.292 |
| reachable gbm | B1 | 1.830 | 1.653 | +0.097 [-0.120, +0.250] | -0.177 | 0.216 | 0.186 |
| reachable ridge | B1 | 1.830 | 4.440 | -1.427 [-2.821, -0.575] | -4.502 | 1.000 | 0.997 |
| ceiling gbm | reachable gbm | 1.653 | 1.635 | +0.011 [-0.110, +0.153] | -0.205 | 0.429 | 0.444 |
| memorised gbm | reachable gbm | 1.653 | 0.455 | +0.725 [+0.683, +0.774] | +0.916 | 0.000 | 0.000 |
| ceiling ridge | reachable ridge | 4.440 | 3.673 | +0.173 [-0.121, +0.405] | -0.415 | 0.211 | 0.190 |
| memorised ridge | reachable ridge | 4.440 | 1.718 | +0.613 [+0.445, +0.733] | +1.415 | 0.000 | 0.002 |

### day type: ordinary

1598 decision days, 2000 draws. Skill = (benchmark mean - candidate mean) / benchmark mean; positive favours the candidate. Interval: 5th to 95th percentile of the paired skill draws.

| candidate | benchmark | benchmark mean | candidate mean | skill [90%] | lower bound of mean difference (one-sided 95%) | bootstrap p | DM p |
|---|---|---|---|---|---|---|---|
| ceiling gbm | B1 | 1.742 | 1.447 | +0.169 [+0.002, +0.316] | +0.002 | 0.049 | 0.081 |
| ceiling ridge | B1 | 1.742 | 3.568 | -1.048 [-1.646, -0.618] | -2.290 | 1.000 | 1.000 |
| memorised gbm | B1 | 1.742 | 0.372 | +0.787 [+0.744, +0.825] | +0.988 | 0.000 | 0.000 |
| memorised ridge | B1 | 1.742 | 1.489 | +0.145 [-0.053, +0.297] | -0.069 | 0.129 | 0.134 |
| reachable gbm | B1 | 1.742 | 1.400 | +0.197 [+0.011, +0.357] | +0.015 | 0.037 | 0.066 |
| reachable ridge | B1 | 1.742 | 3.815 | -1.190 [-2.127, -0.609] | -3.298 | 1.000 | 1.000 |
| ceiling gbm | reachable gbm | 1.400 | 1.447 | -0.034 [-0.121, +0.049] | -0.171 | 0.721 | 0.775 |
| memorised gbm | reachable gbm | 1.400 | 0.372 | +0.735 [+0.710, +0.759] | +0.871 | 0.000 | 0.000 |
| ceiling ridge | reachable ridge | 3.815 | 3.568 | +0.065 [-0.170, +0.273] | -0.531 | 0.363 | 0.310 |
| memorised ridge | reachable ridge | 3.815 | 1.489 | +0.610 [+0.503, +0.701] | +1.500 | 0.000 | 0.000 |

### day type: quarter_end

126 decision days, 2000 draws. Skill = (benchmark mean - candidate mean) / benchmark mean; positive favours the candidate. Interval: 5th to 95th percentile of the paired skill draws.

| candidate | benchmark | benchmark mean | candidate mean | skill [90%] | lower bound of mean difference (one-sided 95%) | bootstrap p | DM p |
|---|---|---|---|---|---|---|---|
| ceiling gbm | B1 | 4.401 | 4.340 | +0.014 [-0.350, +0.233] | -0.957 | 0.473 | 0.462 |
| ceiling ridge | B1 | 4.401 | 6.102 | -0.386 [-1.825, +0.063] | -3.765 | 0.904 | 0.915 |
| memorised gbm | B1 | 4.401 | 1.656 | +0.624 [+0.525, +0.741] | +1.213 | 0.000 | 0.001 |
| memorised ridge | B1 | 4.401 | 3.633 | +0.175 [-0.706, +0.449] | -1.407 | 0.324 | 0.272 |
| reachable gbm | B1 | 4.401 | 4.624 | -0.051 [-0.417, +0.147] | -1.231 | 0.658 | 0.639 |
| reachable ridge | B1 | 4.401 | 8.902 | -1.023 [-2.940, -0.251] | -8.355 | 0.992 | 0.982 |
| ceiling gbm | reachable gbm | 4.624 | 4.340 | +0.061 [-0.015, +0.156] | -0.064 | 0.090 | 0.128 |
| memorised gbm | reachable gbm | 4.624 | 1.656 | +0.642 [+0.583, +0.744] | +1.703 | 0.000 | 0.000 |
| ceiling ridge | reachable ridge | 8.902 | 6.102 | +0.315 [+0.001, +0.489] | +0.004 | 0.049 | 0.092 |
| memorised ridge | reachable ridge | 8.902 | 3.633 | +0.592 [+0.407, +0.689] | +2.142 | 0.000 | 0.008 |

### day type: tax_date

185 decision days, 2000 draws. Skill = (benchmark mean - candidate mean) / benchmark mean; positive favours the candidate. Interval: 5th to 95th percentile of the paired skill draws.

| candidate | benchmark | benchmark mean | candidate mean | skill [90%] | lower bound of mean difference (one-sided 95%) | bootstrap p | DM p |
|---|---|---|---|---|---|---|---|
| ceiling gbm | B1 | 5.224 | 5.793 | -0.109 [-0.445, -0.017] | -1.149 | 0.964 | 0.952 |
| ceiling ridge | B1 | 5.224 | 7.881 | -0.509 [-3.106, -0.132] | -3.549 | 1.000 | 1.000 |
| memorised gbm | B1 | 5.224 | 3.071 | +0.412 [+0.359, +0.717] | +0.695 | 0.000 | 0.027 |
| memorised ridge | B1 | 5.224 | 5.464 | -0.046 [-1.491, +0.162] | -1.633 | 0.625 | 0.584 |
| reachable gbm | B1 | 5.224 | 5.606 | -0.073 [-0.342, +0.019] | -0.864 | 0.924 | 0.906 |
| reachable ridge | B1 | 5.224 | 11.795 | -1.258 [-6.296, -0.519] | -9.744 | 1.000 | 1.000 |
| ceiling gbm | reachable gbm | 5.606 | 5.793 | -0.033 [-0.107, -0.001] | -0.410 | 0.954 | 0.935 |
| memorised gbm | reachable gbm | 5.606 | 3.071 | +0.452 [+0.393, +0.742] | +0.912 | 0.000 | 0.023 |
| ceiling ridge | reachable ridge | 11.795 | 7.881 | +0.332 [+0.170, +0.503] | +1.339 | 0.000 | 0.010 |
| memorised ridge | reachable ridge | 11.795 | 5.464 | +0.537 [+0.415, +0.683] | +3.217 | 0.000 | 0.001 |

### regime: 2018-19

104 decision days, 2000 draws. Skill = (benchmark mean - candidate mean) / benchmark mean; positive favours the candidate. Interval: 5th to 95th percentile of the paired skill draws.

| candidate | benchmark | benchmark mean | candidate mean | skill [90%] | lower bound of mean difference (one-sided 95%) | bootstrap p | DM p |
|---|---|---|---|---|---|---|---|
| ceiling gbm | B1 | 10.407 | 6.836 | +0.343 [+0.053, +0.543] | +0.319 | 0.013 | 0.097 |
| ceiling ridge | B1 | 10.407 | 10.589 | -0.018 [-1.506, +0.325] | -4.858 | 0.566 | 0.520 |
| memorised gbm | B1 | 10.407 | 3.199 | +0.693 [+0.547, +0.856] | +2.481 | 0.000 | 0.026 |
| memorised ridge | B1 | 10.407 | 6.123 | +0.412 [-0.089, +0.593] | -0.348 | 0.100 | 0.125 |
| reachable gbm | B1 | 10.407 | 6.439 | +0.381 [+0.061, +0.580] | +0.298 | 0.011 | 0.087 |
| reachable ridge | B1 | 10.407 | 12.746 | -0.225 [-2.011, +0.180] | -7.109 | 0.771 | 0.764 |
| ceiling gbm | reachable gbm | 6.439 | 6.836 | -0.062 [-0.216, +0.145] | -1.328 | 0.752 | 0.783 |
| memorised gbm | reachable gbm | 6.439 | 3.199 | +0.503 [+0.422, +0.781] | +1.887 | 0.000 | 0.001 |
| ceiling ridge | reachable ridge | 12.746 | 10.589 | +0.169 [-0.057, +0.345] | -0.540 | 0.098 | 0.129 |
| memorised ridge | reachable ridge | 12.746 | 6.123 | +0.520 [+0.363, +0.694] | +4.105 | 0.000 | 0.000 |

### regime: 2018-19, ordinary

101 decision days, 2000 draws. Skill = (benchmark mean - candidate mean) / benchmark mean; positive favours the candidate. Interval: 5th to 95th percentile of the paired skill draws.

| candidate | benchmark | benchmark mean | candidate mean | skill [90%] | lower bound of mean difference (one-sided 95%) | bootstrap p | DM p |
|---|---|---|---|---|---|---|---|
| ceiling gbm | B1 | 6.673 | 3.144 | +0.529 [+0.030, +0.701] | +0.093 | 0.036 | 0.111 |
| ceiling ridge | B1 | 6.673 | 7.438 | -0.115 [-1.896, +0.421] | -5.219 | 0.672 | 0.589 |
| memorised gbm | B1 | 6.673 | 0.688 | +0.897 [+0.797, +0.932] | +2.065 | 0.000 | 0.029 |
| memorised ridge | B1 | 6.673 | 3.580 | +0.464 [-0.279, +0.693] | -0.746 | 0.199 | 0.162 |
| reachable gbm | B1 | 6.673 | 2.683 | +0.598 [+0.053, +0.763] | +0.141 | 0.026 | 0.100 |
| reachable ridge | B1 | 6.673 | 8.218 | -0.232 [-2.033, +0.318] | -5.694 | 0.732 | 0.689 |
| ceiling gbm | reachable gbm | 2.683 | 3.144 | -0.172 [-0.505, +0.261] | -1.514 | 0.750 | 0.783 |
| memorised gbm | reachable gbm | 2.683 | 0.688 | +0.743 [+0.664, +0.843] | +1.749 | 0.000 | 0.000 |
| ceiling ridge | reachable ridge | 8.218 | 7.438 | +0.095 [-0.212, +0.295] | -1.379 | 0.277 | 0.299 |
| memorised ridge | reachable ridge | 8.218 | 3.580 | +0.564 [+0.354, +0.692] | +2.329 | 0.001 | 0.001 |

### regime: 2020

255 decision days, 2000 draws. Skill = (benchmark mean - candidate mean) / benchmark mean; positive favours the candidate. Interval: 5th to 95th percentile of the paired skill draws.

| candidate | benchmark | benchmark mean | candidate mean | skill [90%] | lower bound of mean difference (one-sided 95%) | bootstrap p | DM p |
|---|---|---|---|---|---|---|---|
| ceiling gbm | B1 | 1.645 | 1.415 | +0.140 [-0.022, +0.272] | -0.031 | 0.071 | 0.109 |
| ceiling ridge | B1 | 1.645 | 4.507 | -1.739 [-2.627, -1.118] | -3.470 | 1.000 | 1.000 |
| memorised gbm | B1 | 1.645 | 0.426 | +0.741 [+0.694, +0.793] | +0.844 | 0.000 | 0.000 |
| memorised ridge | B1 | 1.645 | 1.690 | -0.027 [-0.404, +0.225] | -0.462 | 0.590 | 0.555 |
| reachable gbm | B1 | 1.645 | 1.631 | +0.008 [-0.250, +0.203] | -0.367 | 0.427 | 0.477 |
| reachable ridge | B1 | 1.645 | 9.866 | -4.996 [-8.956, -2.362] | -13.521 | 1.000 | 0.999 |
| ceiling gbm | reachable gbm | 1.631 | 1.415 | +0.133 [+0.046, +0.198] | +0.055 | 0.009 | 0.020 |
| memorised gbm | reachable gbm | 1.631 | 0.426 | +0.739 [+0.656, +0.811] | +0.729 | 0.000 | 0.000 |
| ceiling ridge | reachable ridge | 9.866 | 4.507 | +0.543 [+0.251, +0.686] | +1.477 | 0.001 | 0.019 |
| memorised ridge | reachable ridge | 9.866 | 1.690 | +0.829 [+0.711, +0.886] | +4.011 | 0.000 | 0.001 |

### regime: 2020, ordinary

251 decision days, 2000 draws. Skill = (benchmark mean - candidate mean) / benchmark mean; positive favours the candidate. Interval: 5th to 95th percentile of the paired skill draws.

| candidate | benchmark | benchmark mean | candidate mean | skill [90%] | lower bound of mean difference (one-sided 95%) | bootstrap p | DM p |
|---|---|---|---|---|---|---|---|
| ceiling gbm | B1 | 1.683 | 1.366 | +0.188 [+0.038, +0.309] | +0.052 | 0.025 | 0.042 |
| ceiling ridge | B1 | 1.683 | 4.559 | -1.709 [-2.649, -1.076] | -3.573 | 1.000 | 1.000 |
| memorised gbm | B1 | 1.683 | 0.441 | +0.738 [+0.681, +0.800] | +0.857 | 0.000 | 0.000 |
| memorised ridge | B1 | 1.683 | 1.574 | +0.065 [-0.251, +0.281] | -0.290 | 0.387 | 0.369 |
| reachable gbm | B1 | 1.683 | 1.588 | +0.056 [-0.184, +0.237] | -0.266 | 0.288 | 0.343 |
| reachable ridge | B1 | 1.683 | 9.788 | -4.816 [-9.071, -2.173] | -13.514 | 1.000 | 0.998 |
| ceiling gbm | reachable gbm | 1.588 | 1.366 | +0.140 [+0.050, +0.213] | +0.063 | 0.009 | 0.018 |
| memorised gbm | reachable gbm | 1.588 | 0.441 | +0.722 [+0.630, +0.808] | +0.683 | 0.000 | 0.000 |
| ceiling ridge | reachable ridge | 9.788 | 4.559 | +0.534 [+0.190, +0.695] | +1.019 | 0.004 | 0.028 |
| memorised ridge | reachable ridge | 9.788 | 1.574 | +0.839 [+0.710, +0.895] | +3.683 | 0.000 | 0.002 |

### regime: 2021-23

752 decision days, 2000 draws. Skill = (benchmark mean - candidate mean) / benchmark mean; positive favours the candidate. Interval: 5th to 95th percentile of the paired skill draws.

| candidate | benchmark | benchmark mean | candidate mean | skill [90%] | lower bound of mean difference (one-sided 95%) | bootstrap p | DM p |
|---|---|---|---|---|---|---|---|
| ceiling gbm | B1 | 0.706 | 0.898 | -0.271 [-0.504, -0.046] | -0.372 | 0.982 | 0.977 |
| ceiling ridge | B1 | 0.706 | 3.120 | -3.416 [-4.856, -2.406] | -2.971 | 1.000 | 1.000 |
| memorised gbm | B1 | 0.706 | 0.213 | +0.698 [+0.650, +0.748] | +0.411 | 0.000 | 0.000 |
| memorised ridge | B1 | 0.706 | 1.166 | -0.651 [-0.971, -0.405] | -0.571 | 1.000 | 1.000 |
| reachable gbm | B1 | 0.706 | 0.939 | -0.329 [-0.538, -0.141] | -0.385 | 0.999 | 0.998 |
| reachable ridge | B1 | 0.706 | 2.533 | -2.586 [-3.388, -1.964] | -2.094 | 1.000 | 1.000 |
| ceiling gbm | reachable gbm | 0.939 | 0.898 | +0.044 [-0.096, +0.192] | -0.090 | 0.294 | 0.280 |
| memorised gbm | reachable gbm | 0.939 | 0.213 | +0.773 [+0.736, +0.814] | +0.568 | 0.000 | 0.000 |
| ceiling ridge | reachable ridge | 2.533 | 3.120 | -0.232 [-0.457, -0.045] | -1.125 | 0.984 | 0.991 |
| memorised ridge | reachable ridge | 2.533 | 1.166 | +0.540 [+0.494, +0.582] | +1.139 | 0.000 | 0.000 |

### regime: 2021-23, ordinary

751 decision days, 2000 draws. Skill = (benchmark mean - candidate mean) / benchmark mean; positive favours the candidate. Interval: 5th to 95th percentile of the paired skill draws.

| candidate | benchmark | benchmark mean | candidate mean | skill [90%] | lower bound of mean difference (one-sided 95%) | bootstrap p | DM p |
|---|---|---|---|---|---|---|---|
| ceiling gbm | B1 | 0.707 | 0.888 | -0.256 [-0.491, -0.043] | -0.361 | 0.983 | 0.971 |
| ceiling ridge | B1 | 0.707 | 3.014 | -3.263 [-4.718, -2.274] | -2.871 | 1.000 | 1.000 |
| memorised gbm | B1 | 0.707 | 0.213 | +0.699 [+0.650, +0.750] | +0.405 | 0.000 | 0.000 |
| memorised ridge | B1 | 0.707 | 1.059 | -0.498 [-0.827, -0.264] | -0.473 | 1.000 | 1.000 |
| reachable gbm | B1 | 0.707 | 0.932 | -0.318 [-0.529, -0.133] | -0.370 | 1.000 | 0.997 |
| reachable ridge | B1 | 0.707 | 2.234 | -2.160 [-2.965, -1.561] | -1.803 | 1.000 | 1.000 |
| ceiling gbm | reachable gbm | 0.932 | 0.888 | +0.047 [-0.092, +0.183] | -0.084 | 0.281 | 0.259 |
| memorised gbm | reachable gbm | 0.932 | 0.213 | +0.772 [+0.734, +0.813] | +0.558 | 0.000 | 0.000 |
| ceiling ridge | reachable ridge | 2.234 | 3.014 | -0.349 [-0.619, -0.121] | -1.321 | 0.997 | 0.999 |
| memorised ridge | reachable ridge | 2.234 | 1.059 | +0.526 [+0.468, +0.580] | +0.926 | 0.000 | 0.000 |

### regime: 2024

254 decision days, 2000 draws. Skill = (benchmark mean - candidate mean) / benchmark mean; positive favours the candidate. Interval: 5th to 95th percentile of the paired skill draws.

| candidate | benchmark | benchmark mean | candidate mean | skill [90%] | lower bound of mean difference (one-sided 95%) | bootstrap p | DM p |
|---|---|---|---|---|---|---|---|
| ceiling gbm | B1 | 1.679 | 1.183 | +0.296 [+0.191, +0.381] | +0.222 | 0.000 | 0.002 |
| ceiling ridge | B1 | 1.679 | 2.044 | -0.217 [-0.571, -0.027] | -0.638 | 0.972 | 0.979 |
| memorised gbm | B1 | 1.679 | 0.402 | +0.761 [+0.732, +0.791] | +0.815 | 0.000 | 0.000 |
| memorised ridge | B1 | 1.679 | 1.361 | +0.190 [-0.053, +0.319] | -0.056 | 0.086 | 0.080 |
| reachable gbm | B1 | 1.679 | 1.227 | +0.269 [+0.166, +0.357] | +0.197 | 0.000 | 0.002 |
| reachable ridge | B1 | 1.679 | 1.887 | -0.124 [-0.412, +0.025] | -0.468 | 0.905 | 0.922 |
| ceiling gbm | reachable gbm | 1.227 | 1.183 | +0.036 [-0.029, +0.088] | -0.029 | 0.174 | 0.165 |
| memorised gbm | reachable gbm | 1.227 | 0.402 | +0.673 [+0.646, +0.707] | +0.562 | 0.000 | 0.000 |
| ceiling ridge | reachable ridge | 1.887 | 2.044 | -0.083 [-0.211, +0.014] | -0.344 | 0.911 | 0.920 |
| memorised ridge | reachable ridge | 1.887 | 1.361 | +0.279 [+0.199, +0.342] | +0.296 | 0.000 | 0.000 |

### regime: 2024, ordinary

250 decision days, 2000 draws. Skill = (benchmark mean - candidate mean) / benchmark mean; positive favours the candidate. Interval: 5th to 95th percentile of the paired skill draws.

| candidate | benchmark | benchmark mean | candidate mean | skill [90%] | lower bound of mean difference (one-sided 95%) | bootstrap p | DM p |
|---|---|---|---|---|---|---|---|
| ceiling gbm | B1 | 1.544 | 1.130 | +0.268 [+0.142, +0.367] | +0.148 | 0.001 | 0.007 |
| ceiling ridge | B1 | 1.544 | 1.950 | -0.263 [-0.691, -0.044] | -0.690 | 0.981 | 0.989 |
| memorised gbm | B1 | 1.544 | 0.397 | +0.743 [+0.706, +0.787] | +0.706 | 0.000 | 0.000 |
| memorised ridge | B1 | 1.544 | 1.238 | +0.198 [-0.065, +0.335] | -0.060 | 0.104 | 0.088 |
| reachable gbm | B1 | 1.544 | 1.124 | +0.272 [+0.162, +0.365] | +0.172 | 0.001 | 0.003 |
| reachable ridge | B1 | 1.544 | 1.737 | -0.125 [-0.416, +0.032] | -0.439 | 0.897 | 0.917 |
| ceiling gbm | reachable gbm | 1.124 | 1.130 | -0.005 [-0.080, +0.049] | -0.072 | 0.560 | 0.556 |
| memorised gbm | reachable gbm | 1.124 | 0.397 | +0.647 [+0.614, +0.698] | +0.490 | 0.000 | 0.000 |
| ceiling ridge | reachable ridge | 1.737 | 1.950 | -0.123 [-0.279, -0.019] | -0.391 | 0.975 | 0.978 |
| memorised ridge | reachable ridge | 1.737 | 1.238 | +0.288 [+0.194, +0.351] | +0.248 | 0.000 | 0.001 |

### regime: 2025-26

249 decision days, 2000 draws. Skill = (benchmark mean - candidate mean) / benchmark mean; positive favours the candidate. Interval: 5th to 95th percentile of the paired skill draws.

| candidate | benchmark | benchmark mean | candidate mean | skill [90%] | lower bound of mean difference (one-sided 95%) | bootstrap p | DM p |
|---|---|---|---|---|---|---|---|
| ceiling gbm | B1 | 3.362 | 2.989 | +0.111 [-0.027, +0.244] | -0.097 | 0.091 | 0.102 |
| ceiling ridge | B1 | 3.362 | 4.526 | -0.346 [-0.574, -0.172] | -1.768 | 1.000 | 0.999 |
| memorised gbm | B1 | 3.362 | 0.711 | +0.788 [+0.758, +0.814] | +2.051 | 0.000 | 0.000 |
| memorised ridge | B1 | 3.362 | 2.204 | +0.344 [+0.257, +0.413] | +0.706 | 0.000 | 0.000 |
| reachable gbm | B1 | 3.362 | 2.489 | +0.260 [+0.136, +0.364] | +0.409 | 0.001 | 0.001 |
| reachable ridge | B1 | 3.362 | 3.022 | +0.101 [-0.020, +0.198] | -0.063 | 0.086 | 0.121 |
| ceiling gbm | reachable gbm | 2.489 | 2.989 | -0.201 [-0.335, -0.070] | -0.915 | 0.997 | 0.993 |
| memorised gbm | reachable gbm | 2.489 | 0.711 | +0.714 [+0.683, +0.741] | +1.363 | 0.000 | 0.000 |
| ceiling ridge | reachable ridge | 3.022 | 4.526 | -0.497 [-0.605, -0.390] | -1.945 | 1.000 | 1.000 |
| memorised ridge | reachable ridge | 3.022 | 2.204 | +0.271 [+0.228, +0.306] | +0.591 | 0.000 | 0.000 |

### regime: 2025-26, ordinary

249 decision days, 2000 draws. Skill = (benchmark mean - candidate mean) / benchmark mean; positive favours the candidate. Interval: 5th to 95th percentile of the paired skill draws.

| candidate | benchmark | benchmark mean | candidate mean | skill [90%] | lower bound of mean difference (one-sided 95%) | bootstrap p | DM p |
|---|---|---|---|---|---|---|---|
| ceiling gbm | B1 | 3.042 | 2.867 | +0.058 [-0.102, +0.206] | -0.312 | 0.253 | 0.280 |
| ceiling ridge | B1 | 3.042 | 4.375 | -0.438 [-0.674, -0.246] | -1.933 | 1.000 | 1.000 |
| memorised gbm | B1 | 3.042 | 0.661 | +0.783 [+0.745, +0.815] | +1.838 | 0.000 | 0.000 |
| memorised ridge | B1 | 3.042 | 2.090 | +0.313 [+0.223, +0.387] | +0.553 | 0.000 | 0.000 |
| reachable gbm | B1 | 3.042 | 2.374 | +0.220 [+0.081, +0.339] | +0.229 | 0.006 | 0.009 |
| reachable ridge | B1 | 3.042 | 2.888 | +0.051 [-0.076, +0.154] | -0.206 | 0.243 | 0.285 |
| ceiling gbm | reachable gbm | 2.374 | 2.867 | -0.208 [-0.350, -0.075] | -0.899 | 0.999 | 0.994 |
| memorised gbm | reachable gbm | 2.374 | 0.661 | +0.721 [+0.686, +0.753] | +1.336 | 0.000 | 0.000 |
| ceiling ridge | reachable ridge | 2.888 | 4.375 | -0.515 [-0.626, -0.400] | -1.946 | 1.000 | 1.000 |
| memorised ridge | reachable ridge | 2.888 | 2.090 | +0.276 [+0.228, +0.316] | +0.575 | 0.000 | 0.000 |

## MAE of the median (bp)

### Walk-forward days, ordinary days

1598 decision days, 2000 draws. Skill = (benchmark mean - candidate mean) / benchmark mean; positive favours the candidate. Interval: 5th to 95th percentile of the paired skill draws.

| candidate | benchmark | benchmark mean | candidate mean | skill [90%] | lower bound of mean difference (one-sided 95%) | bootstrap p | DM p |
|---|---|---|---|---|---|---|---|
| ceiling gbm | B1 | 2.147 | 2.028 | +0.055 [-0.114, +0.200] | -0.201 | 0.326 | 0.298 |
| ceiling ridge | B1 | 2.147 | 4.541 | -1.115 [-1.686, -0.702] | -2.926 | 1.000 | 1.000 |
| memorised gbm | B1 | 2.147 | 0.439 | +0.796 [+0.753, +0.833] | +1.265 | 0.000 | 0.000 |
| memorised ridge | B1 | 2.147 | 2.059 | +0.041 [-0.160, +0.192] | -0.266 | 0.407 | 0.359 |
| reachable gbm | B1 | 2.147 | 1.949 | +0.092 [-0.093, +0.256] | -0.167 | 0.247 | 0.208 |
| reachable ridge | B1 | 2.147 | 4.804 | -1.238 [-2.095, -0.696] | -3.975 | 1.000 | 1.000 |
| ceiling gbm | reachable gbm | 1.949 | 2.028 | -0.040 [-0.128, +0.043] | -0.260 | 0.755 | 0.812 |
| memorised gbm | reachable gbm | 1.949 | 0.439 | +0.775 [+0.737, +0.810] | +1.295 | 0.000 | 0.000 |
| ceiling ridge | reachable ridge | 4.804 | 4.541 | +0.055 [-0.149, +0.241] | -0.605 | 0.363 | 0.312 |
| memorised ridge | reachable ridge | 4.804 | 2.059 | +0.571 [+0.472, +0.660] | +1.839 | 0.000 | 0.000 |

### Walk-forward days, all days

1598 decision days, 2000 draws. Skill = (benchmark mean - candidate mean) / benchmark mean; positive favours the candidate. Interval: 5th to 95th percentile of the paired skill draws.

| candidate | benchmark | benchmark mean | candidate mean | skill [90%] | lower bound of mean difference (one-sided 95%) | bootstrap p | DM p |
|---|---|---|---|---|---|---|---|
| ceiling gbm | B1 | 2.486 | 2.353 | +0.054 [-0.097, +0.171] | -0.195 | 0.303 | 0.274 |
| ceiling ridge | B1 | 2.486 | 4.877 | -0.961 [-1.555, -0.557] | -2.941 | 1.000 | 1.000 |
| memorised gbm | B1 | 2.486 | 0.683 | +0.725 [+0.656, +0.796] | +1.343 | 0.000 | 0.000 |
| memorised ridge | B1 | 2.486 | 2.382 | +0.042 [-0.170, +0.185] | -0.306 | 0.403 | 0.354 |
| reachable gbm | B1 | 2.486 | 2.266 | +0.089 [-0.077, +0.214] | -0.151 | 0.208 | 0.178 |
| reachable ridge | B1 | 2.486 | 5.366 | -1.158 [-2.046, -0.646] | -4.175 | 1.000 | 1.000 |
| ceiling gbm | reachable gbm | 2.266 | 2.353 | -0.039 [-0.111, +0.032] | -0.268 | 0.782 | 0.840 |
| memorised gbm | reachable gbm | 2.266 | 0.683 | +0.699 [+0.592, +0.794] | +1.354 | 0.000 | 0.000 |
| ceiling ridge | reachable ridge | 5.366 | 4.877 | +0.091 [-0.077, +0.251] | -0.356 | 0.217 | 0.177 |
| memorised ridge | reachable ridge | 5.366 | 2.382 | +0.556 [+0.464, +0.646] | +2.090 | 0.000 | 0.000 |

## By lead (walk-forward days; grid CRPS per decision-day cell, against B1)

**Lead 1, all days (1598 cells).** ceiling gbm: +0.155 [-0.014, +0.271]; ceiling ridge: -1.259 [-2.251, -0.651]; memorised gbm: +0.704 [+0.656, +0.749]; memorised ridge: -0.005 [-0.347, +0.201]; reachable gbm: +0.172 [-0.013, +0.293]; reachable ridge: -1.568 [-2.911, -0.846]

**Lead 1, ordinary days (1256 cells).** ceiling gbm: +0.224 [+0.001, +0.404]; ceiling ridge: -1.401 [-2.378, -0.729]; memorised gbm: +0.776 [+0.709, +0.830]; memorised ridge: +0.025 [-0.321, +0.255]; reachable gbm: +0.256 [+0.008, +0.445]; reachable ridge: -1.589 [-2.819, -0.795]

**Lead 2, all days (1598 cells).** ceiling gbm: +0.140 [-0.017, +0.260]; ceiling ridge: -0.980 [-1.719, -0.512]; memorised gbm: +0.723 [+0.673, +0.774]; memorised ridge: +0.115 [-0.123, +0.274]; reachable gbm: +0.168 [+0.004, +0.287]; reachable ridge: -1.057 [-1.971, -0.540]

**Lead 2, ordinary days (1255 cells).** ceiling gbm: +0.223 [+0.021, +0.396]; ceiling ridge: -1.048 [-1.787, -0.536]; memorised gbm: +0.795 [+0.740, +0.844]; memorised ridge: +0.174 [-0.067, +0.356]; reachable gbm: +0.263 [+0.051, +0.440]; reachable ridge: -0.947 [-1.770, -0.398]

**Lead 3, all days (1598 cells).** ceiling gbm: +0.151 [+0.005, +0.267]; ceiling ridge: -0.743 [-1.338, -0.357]; memorised gbm: +0.741 [+0.688, +0.793]; memorised ridge: +0.192 [+0.005, +0.322]; reachable gbm: +0.183 [+0.034, +0.297]; reachable ridge: -0.871 [-1.652, -0.420]

**Lead 3, ordinary days (1254 cells).** ceiling gbm: +0.232 [+0.044, +0.389]; ceiling ridge: -0.777 [-1.385, -0.361]; memorised gbm: +0.812 [+0.767, +0.851]; memorised ridge: +0.257 [+0.055, +0.411]; reachable gbm: +0.278 [+0.087, +0.435]; reachable ridge: -0.772 [-1.547, -0.276]

**Lead 4, all days (1598 cells).** ceiling gbm: +0.149 [+0.014, +0.263]; ceiling ridge: -0.769 [-1.333, -0.398]; memorised gbm: +0.742 [+0.683, +0.797]; memorised ridge: +0.174 [-0.017, +0.304]; reachable gbm: +0.178 [+0.034, +0.292]; reachable ridge: -1.116 [-2.163, -0.509]

**Lead 4, ordinary days (1253 cells).** ceiling gbm: +0.226 [+0.051, +0.374]; ceiling ridge: -0.844 [-1.417, -0.429]; memorised gbm: +0.810 [+0.765, +0.849]; memorised ridge: +0.215 [+0.007, +0.373]; reachable gbm: +0.253 [+0.065, +0.411]; reachable ridge: -1.051 [-2.062, -0.392]

**Lead 5, all days (1598 cells).** ceiling gbm: +0.158 [+0.029, +0.269]; ceiling ridge: -0.857 [-1.474, -0.445]; memorised gbm: +0.748 [+0.688, +0.807]; memorised ridge: +0.189 [+0.014, +0.314]; reachable gbm: +0.173 [+0.025, +0.288]; reachable ridge: -1.024 [-1.947, -0.480]

**Lead 5, ordinary days (1252 cells).** ceiling gbm: +0.224 [+0.065, +0.363]; ceiling ridge: -0.940 [-1.558, -0.493]; memorised gbm: +0.812 [+0.769, +0.849]; memorised ridge: +0.223 [+0.032, +0.371]; reachable gbm: +0.237 [+0.051, +0.388]; reachable ridge: -0.975 [-1.846, -0.381]

## The +5 bp indicator on ordinary days

1469 ordinary scored days, 82 pressure days. AUROC and Brier skill averaged over leads 1 to 5; 90% stationary-bootstrap intervals.

| fit, window, split | row | AUROC [90%] | AUROC minus persistence-logistic [90%] | Brier | Brier skill vs climatology [90%] | Brier skill vs persistence-logistic [90%] | ordinary days / pressure days by lead |
|---|---|---|---|---|---|---|---|
| ceiling, full, ordinary, pooled | gbm | 0.864 [0.821, 0.899] | -0.016 [-0.044, +0.015] | 0.0576 | -0.039 [-0.138, +0.035] | -0.159 [-0.245, -0.059] | 1469/82 / 1469/82 / 1469/82 / 1469/82 / 1469/82 |
| ceiling, full, ordinary, pooled | ridge | 0.792 [0.737, 0.839] | -0.088 [-0.137, -0.036] | 0.1036 | -0.869 [-1.830, -0.355] | -1.072 [-1.965, -0.544] |  |
| ceiling, full, ordinary, pooled | persistence_logistic | 0.880 [0.841, 0.911] | n/a n/a | 0.0497 | +0.103 [-0.002, +0.167] | n/a n/a |  |
| ceiling, full, ordinary, pooled | climatology | n/a n/a | n/a n/a | 0.0554 | n/a n/a | n/a n/a |  |
| ceiling, walk, ordinary, pooled | gbm | 0.911 [0.856, 0.941] | +0.004 [-0.024, +0.033] | 0.0328 | +0.056 [+0.015, +0.150] | -0.122 [-0.227, +0.032] | 1271/51 / 1271/51 / 1254/37 / 1254/37 / 1254/37 |
| ceiling, walk, ordinary, pooled | ridge | 0.812 [0.763, 0.859] | -0.095 [-0.145, -0.029] | 0.0374 | -0.086 [-0.250, +0.005] | -0.288 [-0.524, -0.149] |  |
| ceiling, walk, ordinary, pooled | persistence_logistic | 0.907 [0.854, 0.937] | n/a n/a | 0.0292 | +0.157 [+0.069, +0.230] | n/a n/a |  |
| ceiling, walk, ordinary, pooled | climatology | n/a n/a | n/a n/a | 0.0347 | n/a n/a | n/a n/a |  |
| ceiling, walk, regime: 2018-19 | gbm | 0.536 [0.377, 0.675] | -0.213 [-0.429, +0.011] | 0.2522 | -0.022 [-0.043, -0.004] | -0.297 [-0.439, -0.099] | 96/31 / 96/31 / 79/17 / 79/17 / 79/17 |
| ceiling, walk, regime: 2018-19 | ridge | 0.512 [0.409, 0.656] | -0.236 [-0.402, -0.042] | 0.2505 | -0.035 [-0.339, +0.053] | -0.309 [-0.552, -0.147] |  |
| ceiling, walk, regime: 2018-19 | persistence_logistic | 0.749 [0.622, 0.850] | n/a n/a | 0.1944 | +0.210 [+0.050, +0.273] | n/a n/a |  |
| ceiling, walk, regime: 2018-19 | climatology | n/a n/a | n/a n/a | 0.2478 | n/a n/a | n/a n/a |  |
| ceiling, walk, regime: 2020 | gbm | n/a n/a | n/a n/a | 0.0154 | +0.105 [-0.019, +1.000] | +0.307 [+0.059, +1.000] | 195/3 / 195/3 / 195/3 / 195/3 / 195/3 |
| ceiling, walk, regime: 2020 | ridge | n/a n/a | n/a n/a | 0.0205 | -0.191 [-1.199, +0.168] | +0.083 [-0.917, +0.412] |  |
| ceiling, walk, regime: 2020 | persistence_logistic | n/a n/a | n/a n/a | 0.0223 | -0.295 [-1.159, +0.113] | n/a n/a |  |
| ceiling, walk, regime: 2020 | climatology | n/a n/a | n/a n/a | 0.0172 | n/a n/a | n/a n/a |  |
| ceiling, walk, regime: 2021-23 | gbm | n/a n/a | n/a n/a | 0.0000 | +1.000 [+1.000, +1.000] | +1.000 [+1.000, +1.000] | 586/0 / 586/0 / 586/0 / 586/0 / 586/0 |
| ceiling, walk, regime: 2021-23 | ridge | n/a n/a | n/a n/a | 0.0000 | +0.992 [+0.983, +0.998] | +0.908 [+0.810, +0.983] |  |
| ceiling, walk, regime: 2021-23 | persistence_logistic | n/a n/a | n/a n/a | 0.0005 | +0.880 [+0.841, +0.906] | n/a n/a |  |
| ceiling, walk, regime: 2021-23 | climatology | n/a n/a | n/a n/a | 0.0039 | n/a n/a | n/a n/a |  |
| ceiling, walk, regime: 2024 | gbm | n/a n/a | n/a n/a | 0.0102 | +0.201 [+0.038, +1.000] | +0.101 [+0.010, +1.000] | 197/2 / 197/2 / 197/2 / 197/2 / 197/2 |
| ceiling, walk, regime: 2024 | ridge | n/a n/a | n/a n/a | 0.0198 | -0.556 [-1.927, +0.224] | -0.745 [-10.537, -0.047] |  |
| ceiling, walk, regime: 2024 | persistence_logistic | n/a n/a | n/a n/a | 0.0113 | +0.111 [-0.023, +0.785] | n/a n/a |  |
| ceiling, walk, regime: 2024 | climatology | n/a n/a | n/a n/a | 0.0127 | n/a n/a | n/a n/a |  |
| ceiling, walk, regime: 2025-26 | gbm | 0.884 [0.790, 0.942] | -0.005 [-0.040, +0.036] | 0.0732 | -0.027 [-0.055, +0.282] | -0.115 [-0.237, +0.441] | 197/15 / 197/15 / 197/15 / 197/15 / 197/15 |
| ceiling, walk, regime: 2025-26 | ridge | 0.656 [0.564, 0.744] | -0.232 [-0.333, -0.108] | 0.0894 | -0.254 [-3.247, -0.047] | -0.360 [-3.149, -0.110] |  |
| ceiling, walk, regime: 2025-26 | persistence_logistic | 0.889 [0.798, 0.939] | n/a n/a | 0.0659 | +0.075 [-0.166, +0.186] | n/a n/a |  |
| ceiling, walk, regime: 2025-26 | climatology | n/a n/a | n/a n/a | 0.0713 | n/a n/a | n/a n/a |  |
| ceiling, walk, state: ample | gbm | n/a n/a | n/a n/a | 0.0019 | +0.640 [+0.413, +0.987] | +0.363 [+0.201, +0.936] | 1065/2 / 1066/2 / 1066/2 / 1066/2 / 1066/2 |
| ceiling, walk, state: ample | ridge | n/a n/a | n/a n/a | 0.0073 | -0.370 [-1.077, +0.172] | -1.422 [-4.434, -0.502] |  |
| ceiling, walk, state: ample | persistence_logistic | n/a n/a | n/a n/a | 0.0030 | +0.433 [+0.256, +0.732] | n/a n/a |  |
| ceiling, walk, state: ample | climatology | n/a n/a | n/a n/a | 0.0053 | n/a n/a | n/a n/a |  |
| ceiling, walk, state: scarce | gbm | 0.622 [0.524, 0.705] | -0.085 [-0.205, +0.021] | 0.2009 | -0.033 [-0.057, -0.012] | -0.170 [-0.280, -0.026] | 206/49 / 205/49 / 188/35 / 188/35 / 188/35 |
| ceiling, walk, state: scarce | ridge | 0.526 [0.440, 0.608] | -0.181 [-0.292, -0.054] | 0.2015 | -0.047 [-0.151, +0.017] | -0.181 [-0.336, -0.031] |  |
| ceiling, walk, state: scarce | persistence_logistic | 0.707 [0.613, 0.780] | n/a n/a | 0.1714 | +0.114 [-0.016, +0.192] | n/a n/a |  |
| ceiling, walk, state: scarce | climatology | n/a n/a | n/a n/a | 0.1945 | n/a n/a | n/a n/a |  |
| memorised, full, ordinary, pooled | gbm | 1.000 [1.000, 1.000] | +0.075 [+0.053, +0.108] | 0.0000 | +1.000 [+1.000, +1.000] | +1.000 [+1.000, +1.000] | 1469/82 / 1469/82 / 1469/82 / 1469/82 / 1469/82 |
| memorised, full, ordinary, pooled | ridge | 0.992 [0.988, 0.996] | +0.068 [+0.048, +0.097] | 0.0152 | +0.711 [+0.643, +0.759] | +0.669 [+0.608, +0.716] |  |
| memorised, full, ordinary, pooled | persistence_logistic | 0.925 [0.892, 0.947] | n/a n/a | 0.0458 | +0.131 [+0.017, +0.204] | n/a n/a |  |
| memorised, full, ordinary, pooled | climatology | n/a n/a | n/a n/a | 0.0527 | n/a n/a | n/a n/a |  |
| memorised, walk, ordinary, pooled | gbm | 1.000 [1.000, 1.000] | +0.063 [+0.039, +0.110] | 0.0000 | +1.000 [+1.000, +1.000] | +1.000 [+1.000, +1.000] | 1271/51 / 1271/51 / 1254/37 / 1254/37 / 1254/37 |
| memorised, walk, ordinary, pooled | ridge | 0.996 [0.992, 0.998] | +0.059 [+0.036, +0.104] | 0.0089 | +0.726 [+0.637, +0.781] | +0.682 [+0.603, +0.736] |  |
| memorised, walk, ordinary, pooled | persistence_logistic | 0.937 [0.890, 0.961] | n/a n/a | 0.0281 | +0.144 [+0.036, +0.225] | n/a n/a |  |
| memorised, walk, ordinary, pooled | climatology | n/a n/a | n/a n/a | 0.0331 | n/a n/a | n/a n/a |  |
| reachable, walk, ordinary, pooled | gbm | 0.905 [0.851, 0.938] | +0.015 [-0.017, +0.058] | 0.0355 | +0.037 [-0.139, +0.265] | -0.192 [-0.374, +0.034] | 1271/51 / 1271/51 / 1254/37 / 1254/37 / 1254/37 |
| reachable, walk, ordinary, pooled | ridge | 0.870 [0.805, 0.914] | -0.020 [-0.078, +0.044] | 0.0335 | +0.091 [-0.067, +0.277] | -0.122 [-0.309, +0.059] |  |
| reachable, walk, ordinary, pooled | persistence_logistic | 0.890 [0.821, 0.937] | n/a n/a | 0.0299 | +0.192 [+0.131, +0.276] | n/a n/a |  |
| reachable, walk, ordinary, pooled | climatology | n/a n/a | n/a n/a | 0.0370 | n/a n/a | n/a n/a |  |
| reachable, walk, regime: 2018-19 | gbm | 0.463 [0.349, 0.633] | -0.192 [-0.369, +0.036] | 0.2921 | -0.484 [-0.913, -0.194] | -0.635 [-0.973, -0.341] | 96/31 / 96/31 / 79/17 / 79/17 / 79/17 |
| reachable, walk, regime: 2018-19 | ridge | 0.402 [0.250, 0.610] | -0.253 [-0.502, +0.034] | 0.2671 | -0.343 [-0.723, -0.094] | -0.480 [-0.875, -0.225] |  |
| reachable, walk, regime: 2018-19 | persistence_logistic | 0.655 [0.503, 0.779] | n/a n/a | 0.1822 | +0.095 [+0.009, +0.165] | n/a n/a |  |
| reachable, walk, regime: 2018-19 | climatology | n/a n/a | n/a n/a | 0.2026 | n/a n/a | n/a n/a |  |
| reachable, walk, regime: 2020 | gbm | n/a n/a | n/a n/a | 0.0154 | +0.610 [+0.332, +0.999] | +0.479 [+0.207, +0.998] | 195/3 / 195/3 / 195/3 / 195/3 / 195/3 |
| reachable, walk, regime: 2020 | ridge | n/a n/a | n/a n/a | 0.0180 | +0.545 [+0.279, +0.954] | +0.392 [+0.154, +0.907] |  |
| reachable, walk, regime: 2020 | persistence_logistic | n/a n/a | n/a n/a | 0.0296 | +0.252 [+0.095, +0.467] | n/a n/a |  |
| reachable, walk, regime: 2020 | climatology | n/a n/a | n/a n/a | 0.0396 | n/a n/a | n/a n/a |  |
| reachable, walk, regime: 2021-23 | gbm | n/a n/a | n/a n/a | 0.0000 | +1.000 [+1.000, +1.000] | +1.000 [+1.000, +1.000] | 586/0 / 586/0 / 586/0 / 586/0 / 586/0 |
| reachable, walk, regime: 2021-23 | ridge | n/a n/a | n/a n/a | 0.0002 | +0.979 [+0.962, +0.991] | +0.861 [+0.740, +0.941] |  |
| reachable, walk, regime: 2021-23 | persistence_logistic | n/a n/a | n/a n/a | 0.0013 | +0.843 [+0.802, +0.875] | n/a n/a |  |
| reachable, walk, regime: 2021-23 | climatology | n/a n/a | n/a n/a | 0.0083 | n/a n/a | n/a n/a |  |
| reachable, walk, regime: 2024 | gbm | n/a n/a | n/a n/a | 0.0102 | +0.171 [+0.028, +1.000] | +0.095 [+0.009, +1.000] | 197/2 / 197/2 / 197/2 / 197/2 / 197/2 |
| reachable, walk, regime: 2024 | ridge | n/a n/a | n/a n/a | 0.0101 | +0.173 [+0.035, +0.983] | +0.098 [+0.016, +0.935] |  |
| reachable, walk, regime: 2024 | persistence_logistic | n/a n/a | n/a n/a | 0.0112 | +0.083 [-0.042, +0.773] | n/a n/a |  |
| reachable, walk, regime: 2024 | climatology | n/a n/a | n/a n/a | 0.0122 | n/a n/a | n/a n/a |  |
| reachable, walk, regime: 2025-26 | gbm | 0.871 [0.777, 0.939] | -0.014 [-0.060, +0.050] | 0.0747 | -0.048 [-0.244, +0.175] | -0.131 [-0.299, +0.154] | 197/15 / 197/15 / 197/15 / 197/15 / 197/15 |
| reachable, walk, regime: 2025-26 | ridge | 0.799 [0.689, 0.925] | -0.086 [-0.179, +0.044] | 0.0686 | +0.036 [-0.412, +0.179] | -0.032 [-0.354, +0.153] |  |
| reachable, walk, regime: 2025-26 | persistence_logistic | 0.885 [0.795, 0.937] | n/a n/a | 0.0664 | +0.068 [-0.216, +0.174] | n/a n/a |  |
| reachable, walk, regime: 2025-26 | climatology | n/a n/a | n/a n/a | 0.0712 | n/a n/a | n/a n/a |  |
| reachable, walk, state: ample | gbm | n/a n/a | n/a n/a | 0.0019 | +0.818 [+0.634, +0.999] | +0.596 [+0.370, +0.998] | 1065/2 / 1066/2 / 1066/2 / 1066/2 / 1066/2 |
| reachable, walk, state: ample | ridge | n/a n/a | n/a n/a | 0.0022 | +0.785 [+0.608, +0.958] | +0.522 [+0.313, +0.866] |  |
| reachable, walk, state: ample | persistence_logistic | n/a n/a | n/a n/a | 0.0048 | +0.544 [+0.418, +0.694] | n/a n/a |  |
| reachable, walk, state: ample | climatology | n/a n/a | n/a n/a | 0.0104 | n/a n/a | n/a n/a |  |
| reachable, walk, state: scarce | gbm | 0.587 [0.469, 0.691] | -0.017 [-0.149, +0.122] | 0.2192 | -0.213 [-0.432, -0.013] | -0.318 [-0.546, -0.108] | 206/49 / 205/49 / 188/35 / 188/35 / 188/35 |
| reachable, walk, state: scarce | ridge | 0.549 [0.439, 0.656] | -0.055 [-0.235, +0.111] | 0.2041 | -0.131 [-0.360, +0.041] | -0.227 [-0.480, -0.038] |  |
| reachable, walk, state: scarce | persistence_logistic | 0.604 [0.472, 0.736] | n/a n/a | 0.1668 | +0.081 [+0.008, +0.139] | n/a n/a |  |
| reachable, walk, state: scarce | climatology | n/a n/a | n/a n/a | 0.1818 | n/a n/a | n/a n/a |  |

## The reading

* spread, ceiling (all scored days, cross-fitted, gbm): skill against B1 +0.144 [+0.000, +0.271]; barely above: no.
* spread, reachable (walk-forward days, gbm): skill against B1 +0.192 [+0.007, +0.352]; barely above: no.
* spread, memorised (all scored days, in-sample (memorising; reported, no reading), gbm): skill against B1 +0.781 [+0.747, +0.815]; barely above: no. Reported only: it carries no reading.
* spread verdict: **partly reached**.
* indicator, ceiling (all scored days, cross-fitted, gbm): AUROC minus persistence-logistic -0.016 [-0.044, +0.015], Brier skill against persistence-logistic -0.159 [-0.245, -0.059]; barely above: yes. Secondary: AUROC 0.864 [0.821, 0.899] (persistence-logistic 0.880), under the 0.6 line: no.
* indicator, reachable (walk-forward days, gbm): AUROC minus persistence-logistic +0.015 [-0.017, +0.058], Brier skill against persistence-logistic -0.192 [-0.374, +0.034]; barely above: yes. Secondary: AUROC 0.905 [0.851, 0.938] (persistence-logistic 0.890), under the 0.6 line: no.
* indicator, memorised (all scored days, in-sample (memorising; reported, no reading), gbm): AUROC minus persistence-logistic +0.075 [+0.053, +0.108], Brier skill against persistence-logistic +1.000 [+1.000, +1.000]; barely above: no. Secondary: AUROC 1.000 [1.000, 1.000] (persistence-logistic 0.925), under the 0.6 line: no. Reported only: it carries no reading.
* indicator verdict: **data problem**.

**spread: partly reached; ordinary-day indicator: data problem; the primary target (the spread) decides: partly reached**

