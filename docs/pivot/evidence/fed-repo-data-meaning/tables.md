Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | false alarms per onset, pooled across horizons (limit 2), flat count / weighted count (tier 1 is decided on the one named) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes tested, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 12 of 26 | 0.462 [0.286, 0.667] | 0.368 | 6.85 flat / 3.90 weighted (tier 1 on the weighted count) | 2.7 / 4.7 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| hierarchical_logistic | 15 of 26 | 0.577 [0.400, 0.750] | 0.385 | 7.15 flat / 3.38 weighted (tier 1 on the weighted count) | 0.0 / 0.0 | 2 of 2 | no, yes | fail (tiers no / yes / no) | fail (no / no / no) |
| hierarchical_logistic_fed_repo | 15 of 26 | 0.577 [0.409, 0.750] | 0.380 | 7.04 flat / 3.17 weighted (tier 1 on the weighted count) | 0.0 / 0.0 | 2 of 2 | no, yes | fail (tiers no / yes / no) | fail (no / no / no) |
| hierarchical_logistic_fed_repo_sameday | 16 of 26 | 0.615 [0.440, 0.783] | 0.380 | 7.04 flat / 3.15 weighted (tier 1 on the weighted count) | 0.0 / 0.0 | 2 of 2 | no, yes | fail (tiers no / yes / no) | fail (no / no / no) |
| hierarchical_logistic_srf | 15 of 26 | 0.577 [0.389, 0.741] | 0.385 | 7.23 flat / 3.30 weighted (tier 1 on the weighted count) | 0.0 / 0.0 | 2 of 2 | no, yes | fail (tiers no / yes / no) | fail (no / no / no) |
| hierarchical_logistic_srf_sameday | 15 of 26 | 0.577 [0.400, 0.750] | 0.375 | 6.96 flat / 3.19 weighted (tier 1 on the weighted count) | 0.0 / 0.0 | 2 of 2 | no, yes | fail (tiers no / yes / no) | fail (no / no / no) |
| persistence_logistic | 12 of 26 | 0.462 [0.273, 0.650] | 0.423 | 8.46 flat / 4.09 weighted (tier 1 on the weighted count) | 1.5 / 0.0 | 1 of 2 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| published_v1 | 14 of 26 | 0.538 [0.350, 0.720] | 0.385 | 7.38 flat / 3.06 weighted (tier 1 on the weighted count) | 1.2 / 0.0 | 2 of 2 | no, yes | fail (tiers no / yes / no) | fail (no / yes / no) |

Table 1b. Tier 1 at each lead alone, inside and outside the early years, and the recall with equal weight per regime: reported for every model, not part of the pass rule.

calendar_climatology:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 12 | 0.462 [0.286, 0.667] | 6.692 [4.583, 10.002] | 3.750 [2.485, 5.938] |
| lead 2 alone (fail) | 26 | 10 | 0.385 [0.208, 0.588] | 5.538 [3.440, 8.668] | 3.173 [1.975, 5.211] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.208, 0.588] | 5.577 [3.464, 8.734] | 3.212 [1.990, 5.282] |
| lead 4 alone (fail) | 26 | 10 | 0.385 [0.208, 0.588] | 5.615 [3.500, 8.739] | 3.250 [2.012, 5.360] |
| lead 5 alone (fail) | 26 | 10 | 0.385 [0.208, 0.588] | 5.654 [3.516, 8.811] | 3.288 [2.033, 5.400] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.923] | 7.765 [5.086, 12.286] | 3.324 [2.034, 5.576] |
| outside 2018-2019 | 9 | 0 | 0.000 (no interval) | 5.111 (no interval) | 5.000 (no interval) |

Recall with equal weight per regime: 0.176 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 0/5).

hierarchical_logistic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.321, 0.680] | 5.154 [3.100, 7.818] | 2.308 [1.265, 3.708] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.257, 0.607] | 4.385 [2.599, 6.572] | 1.750 [0.984, 2.775] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.257, 0.607] | 4.038 [2.269, 6.218] | 1.615 [0.852, 2.633] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.257, 0.607] | 4.577 [2.709, 6.913] | 2.058 [1.125, 3.222] |
| lead 5 alone (fail) | 26 | 13 | 0.500 [0.333, 0.682] | 6.231 [4.000, 9.080] | 2.913 [1.714, 4.500] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.909] | 8.765 [5.863, 13.167] | 3.882 [2.400, 6.151] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.111 (no interval) | 2.417 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

hierarchical_logistic_fed_repo:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.323, 0.682] | 4.692 [2.769, 7.305] | 2.010 [1.081, 3.333] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.500 [2.735, 6.867] | 1.760 [1.009, 2.840] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.250, 0.609] | 4.462 [2.735, 6.783] | 1.788 [1.025, 2.917] |
| lead 4 alone (fail) | 26 | 12 | 0.462 [0.294, 0.639] | 5.115 [3.237, 7.682] | 2.298 [1.370, 3.630] |
| lead 5 alone (fail) | 26 | 13 | 0.500 [0.333, 0.684] | 6.385 [4.235, 9.333] | 2.942 [1.765, 4.543] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 8.765 [5.826, 13.236] | 3.882 [2.396, 6.225] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 3.778 (no interval) | 1.833 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

hierarchical_logistic_fed_repo_sameday:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 14 | 0.538 [0.357, 0.708] | 4.808 [2.884, 7.316] | 2.010 [1.065, 3.217] |
| lead 2 alone (fail) | 26 | 11 | 0.423 [0.240, 0.613] | 4.308 [2.542, 6.600] | 1.779 [0.991, 2.857] |
| lead 3 alone (fail) | 26 | 11 | 0.423 [0.240, 0.613] | 4.192 [2.484, 6.456] | 1.644 [0.902, 2.691] |
| lead 4 alone (fail) | 26 | 11 | 0.423 [0.240, 0.613] | 5.577 [3.545, 8.357] | 2.615 [1.500, 4.208] |
| lead 5 alone (fail) | 26 | 15 | 0.577 [0.389, 0.758] | 6.500 [4.356, 9.476] | 2.990 [1.848, 4.625] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 8.765 [6.000, 13.183] | 3.882 [2.442, 6.160] |
| outside 2018-2019 | 9 | 4 | 0.444 (no interval) | 3.778 (no interval) | 1.778 (no interval) |

Recall with equal weight per regime: 0.451 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 3/5).

hierarchical_logistic_srf:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.312, 0.677] | 4.962 [3.038, 7.625] | 2.144 [1.177, 3.579] |
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.312, 0.677] | 4.654 [2.793, 7.000] | 1.817 [1.021, 2.876] |
| lead 3 alone (fail) | 26 | 12 | 0.462 [0.273, 0.650] | 4.885 [2.960, 7.438] | 2.058 [1.145, 3.333] |
| lead 4 alone (fail) | 26 | 13 | 0.500 [0.312, 0.677] | 5.038 [3.000, 7.522] | 2.279 [1.286, 3.549] |
| lead 5 alone (fail) | 26 | 15 | 0.577 [0.389, 0.741] | 6.385 [4.111, 9.228] | 2.942 [1.740, 4.596] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.471, 0.909] | 8.765 [5.782, 13.445] | 3.882 [2.343, 6.265] |
| outside 2018-2019 | 9 | 3 | 0.333 (no interval) | 4.333 (no interval) | 2.194 (no interval) |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

hierarchical_logistic_srf_sameday:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 13 | 0.500 [0.318, 0.690] | 4.731 [2.758, 7.552] | 2.048 [1.076, 3.517] |
| lead 2 alone (pass) | 26 | 13 | 0.500 [0.318, 0.690] | 4.615 [2.865, 7.000] | 1.856 [1.072, 2.990] |
| lead 3 alone (pass) | 26 | 13 | 0.500 [0.318, 0.690] | 4.231 [2.469, 6.520] | 1.635 [0.886, 2.680] |
| lead 4 alone (fail) | 26 | 13 | 0.500 [0.318, 0.690] | 4.962 [3.087, 7.333] | 2.202 [1.293, 3.463] |
| lead 5 alone (fail) | 26 | 15 | 0.577 [0.400, 0.750] | 6.269 [4.111, 9.238] | 2.894 [1.710, 4.605] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.917] | 8.765 [5.823, 13.092] | 3.882 [2.361, 6.292] |
| outside 2018-2019 | 9 | 3 | 0.333 [0.000, 0.625] | 3.556 [1.333, 8.168] | 1.889 [0.646, 4.752] |

Recall with equal weight per regime: 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5).

persistence_logistic:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 11 | 0.423 [0.233, 0.609] | 7.038 [4.823, 10.000] | 3.250 [2.032, 4.952] |
| lead 2 alone (fail) | 26 | 7 | 0.269 [0.111, 0.444] | 4.769 [2.961, 7.201] | 2.067 [1.193, 3.329] |
| lead 3 alone (fail) | 26 | 10 | 0.385 [0.206, 0.567] | 5.923 [3.750, 8.714] | 2.683 [1.527, 4.207] |
| lead 4 alone (fail) | 26 | 8 | 0.308 [0.136, 0.500] | 5.385 [3.275, 8.160] | 2.375 [1.310, 3.931] |
| lead 5 alone (fail) | 26 | 8 | 0.308 [0.148, 0.481] | 4.538 [2.761, 7.000] | 1.856 [1.083, 2.962] |
| inside 2018-2019 | 17 | 11 | 0.647 [0.400, 0.880] | 8.471 [5.500, 13.182] | 3.706 [2.208, 6.083] |
| outside 2018-2019 | 9 | 1 | 0.111 (no interval) | 8.444 (no interval) | 4.806 (no interval) |

Recall with equal weight per regime: 0.287 (2018-19 11/17, 2020 1/2, 2024 0/2, 2025-26 0/5).

published_v1:

| tier 1 on | onsets | flagged | recall [90%] | false alarms per onset, flat [90%] | weighted [90%] |
|---|---|---|---|---|---|
| lead 1 alone (fail) | 26 | 8 | 0.308 [0.143, 0.480] | 5.692 [3.906, 8.133] | 2.308 [1.432, 3.548] |
| lead 2 alone (fail) | 26 | 8 | 0.308 [0.150, 0.474] | 5.615 [3.774, 8.056] | 2.356 [1.470, 3.607] |
| lead 3 alone (fail) | 26 | 6 | 0.231 [0.091, 0.379] | 4.538 [2.869, 6.778] | 1.942 [1.086, 3.133] |
| lead 4 alone (fail) | 26 | 9 | 0.346 [0.190, 0.500] | 5.731 [3.844, 8.251] | 2.375 [1.462, 3.619] |
| lead 5 alone (fail) | 26 | 13 | 0.500 [0.320, 0.680] | 5.538 [3.684, 8.000] | 2.385 [1.468, 3.650] |
| inside 2018-2019 | 17 | 12 | 0.706 [0.500, 0.909] | 8.647 [5.952, 12.813] | 3.706 [2.333, 6.018] |
| outside 2018-2019 | 9 | 2 | 0.222 [0.000, 0.533] | 5.000 [2.667, 9.751] | 1.833 [0.925, 3.562] |

Recall with equal weight per regime: 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5).

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.81 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.59 (17) | 0.61 (101) | 0.44 (9) | 0.62 (13) |
| hierarchical_logistic | 0.73 (102) | 0.25 (4) | – | 0.00 (5) | 0.55 (29) | 0.71 (17) | 0.64 (101) | 0.56 (9) | 0.69 (13) |
| hierarchical_logistic_fed_repo | 0.73 (102) | 0.50 (4) | – | 0.00 (5) | 0.41 (29) | 0.65 (17) | 0.62 (101) | 0.56 (9) | 0.69 (13) |
| hierarchical_logistic_fed_repo_sameday | 0.73 (102) | 0.75 (4) | – | 0.00 (5) | 0.48 (29) | 0.65 (17) | 0.65 (101) | 0.56 (9) | 0.69 (13) |
| hierarchical_logistic_srf | 0.73 (102) | 0.25 (4) | – | 0.00 (5) | 0.52 (29) | 0.71 (17) | 0.63 (101) | 0.56 (9) | 0.69 (13) |
| hierarchical_logistic_srf_sameday | 0.73 (102) | 0.00 (4) | – | 0.00 (5) | 0.59 (29) | 0.76 (17) | 0.63 (101) | 0.56 (9) | 0.69 (13) |
| persistence_logistic | 0.82 (102) | 0.25 (4) | – | 0.20 (5) | 0.59 (29) | 0.82 (17) | 0.75 (101) | 0.56 (9) | 0.62 (13) |
| published_v1 | 0.74 (102) | 0.25 (4) | – | 0.20 (5) | 0.59 (29) | 0.82 (17) | 0.68 (101) | 0.44 (9) | 0.54 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| hierarchical_logistic | +0.0265 [+0.0024, +0.0512] | +0.0181 [+0.0037, +0.0311] | +0.0137 [+0.0120, +0.0155] | +0.0013 [-0.0036, +0.0053] | +0.0382 [+0.0069, +0.0750] | +0.0440 [+0.0227, +0.0682] | +0.0128 [+0.0065, +0.0202] | +0.0754 [+0.0169, +0.1274] | +0.0569 [+0.0308, +0.0829] |
| hierarchical_logistic_fed_repo | +0.0171 [-0.0113, +0.0465] | +0.0278 [+0.0171, +0.0377] | +0.0136 [+0.0120, +0.0154] | +0.0013 [-0.0037, +0.0054] | +0.0324 [+0.0069, +0.0645] | +0.0412 [+0.0223, +0.0626] | +0.0113 [+0.0044, +0.0186] | +0.0796 [+0.0219, +0.1321] | +0.0589 [+0.0344, +0.0846] |
| hierarchical_logistic_fed_repo_sameday | +0.0182 [-0.0092, +0.0454] | +0.0299 [+0.0195, +0.0401] | +0.0136 [+0.0120, +0.0155] | +0.0012 [-0.0037, +0.0052] | +0.0343 [+0.0103, +0.0676] | +0.0400 [+0.0222, +0.0606] | +0.0122 [+0.0054, +0.0194] | +0.0833 [+0.0198, +0.1388] | +0.0593 [+0.0348, +0.0866] |
| hierarchical_logistic_srf | +0.0220 [-0.0026, +0.0471] | +0.0267 [+0.0146, +0.0367] | +0.0137 [+0.0119, +0.0155] | +0.0013 [-0.0036, +0.0053] | +0.0358 [+0.0064, +0.0713] | +0.0446 [+0.0236, +0.0698] | +0.0126 [+0.0060, +0.0193] | +0.0810 [+0.0251, +0.1343] | +0.0570 [+0.0296, +0.0843] |
| hierarchical_logistic_srf_sameday | +0.0240 [-0.0001, +0.0514] | +0.0272 [+0.0157, +0.0375] | +0.0137 [+0.0120, +0.0156] | +0.0012 [-0.0041, +0.0053] | +0.0409 [+0.0100, +0.0799] | +0.0456 [+0.0241, +0.0714] | +0.0139 [+0.0074, +0.0211] | +0.0740 [+0.0189, +0.1252] | +0.0576 [+0.0312, +0.0851] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| published_v1 | +0.0460 [+0.0127, +0.0833] | +0.0328 [+0.0266, +0.0391] | +0.0127 [+0.0111, +0.0144] | +0.0010 [-0.0043, +0.0050] | +0.0229 [-0.0053, +0.0574] | +0.0421 [+0.0202, +0.0713] | +0.0169 [+0.0088, +0.0259] | +0.0922 [+0.0137, +0.1746] | +0.0534 [+0.0285, +0.0795] |
