# H4 step 3 re-read: the back-fill against H5's candidate on the ruled interval (#935), development days, not a verdict

Decision days 2018-06-28 to 2025-12-23 (1869). d = CRPS(without) - CRPS(with), positive when the back-fill helps. Interval: the studentized stationary bootstrap (ruling 1), two-sided 90%. Reference value c = 2.426 (the 250-day value of the grid comparison): `mean - c se` and `mean + c se` carry both orientations of #830 (d = without - with, or the reverse).

| group | days | CRPS without | CRPS with | mean d | se | studentized 90% interval | percentile 90% (superseded) | mean - c se | mean + c se | back-filled share | imputed cells | reading |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pooled | 1869 | 1.830 | 1.805 | +0.025 | 0.0259 | [-0.012, +0.098] | [-0.014, +0.069] | -0.038 | +0.088 | 52% | 52% | neither shown (the interval covers zero) |
| regime 2018-19 | 376 | 4.005 | 4.053 | -0.048 | 0.0372 | [-0.122, +0.016] | [-0.108, +0.011] | -0.138 | +0.042 | 80% | 80% | neither shown (the interval covers zero) |
| period 2018 H1 | 2 | | | | | | | | | | | not tested (too few decision days) |
| period 2018 | 126 | 3.367 | 3.520 | -0.152 | 0.0779 | [-0.291, -0.032] | [-0.251, -0.055] | -0.341 | +0.036 | 89% | 89% | cost shown |
| period 2018 H2 | 124 | 3.318 | 3.461 | -0.143 | 0.0759 | [-0.277, -0.022] | [-0.244, -0.049] | -0.327 | +0.041 | 89% | 89% | cost shown |
| period 2019 H1 | 124 | 2.931 | 2.888 | +0.043 | 0.0382 | [-0.016, +0.118] | [-0.009, +0.099] | -0.049 | +0.136 | 79% | 79% | neither shown (the interval covers zero) |
| period 2019 | 250 | 4.327 | 4.322 | +0.004 | 0.0350 | [-0.059, +0.070] | [-0.052, +0.060] | -0.080 | +0.089 | 75% | 75% | neither shown (the interval covers zero) |
| period 2019 H2 | 126 | 5.700 | 5.734 | -0.034 | 0.0548 | [-0.141, +0.072] | [-0.119, +0.051] | -0.167 | +0.099 | 71% | 71% | neither shown (the interval covers zero) |
| regime 2020 | 251 | 1.417 | 1.294 | +0.124 | 0.1078 | [-0.026, +0.744] | [-0.017, +0.320] | -0.138 | +0.385 | 62% | 62% | neither shown (the interval covers zero) |
| regime 2021-23 | 748 | 0.717 | 0.654 | +0.063 | 0.0479 | [-0.002, +0.245] | [-0.006, +0.146] | -0.053 | +0.179 | 47% | 47% | neither shown (the interval covers zero) |
| regime 2024 | 250 | 1.411 | 1.392 | +0.019 | 0.0136 | [-0.000, +0.047] | [-0.000, +0.041] | -0.014 | +0.052 | 37% | 37% | neither shown (the interval covers zero) |
| regime 2025-26 | 244 | 2.742 | 2.814 | -0.072 | 0.0232 | [-0.127, -0.029] | [-0.116, -0.032] | -0.128 | -0.016 | 33% | 33% | cost shown |
| type quarter_end | 30 | 3.855 | 3.706 | +0.150 | 0.1150 | [-0.033, +0.707] | [-0.021, +0.330] | -0.129 | +0.429 | 53% | 53% | neither shown (the interval covers zero) |
| type ordinary | 1601 | 1.699 | 1.681 | +0.018 | 0.0224 | [-0.017, +0.071] | [-0.017, +0.056] | -0.037 | +0.072 | 52% | 52% | neither shown (the interval covers zero) |
| type month_end | 149 | 2.098 | 2.103 | -0.005 | 0.0411 | [-0.073, +0.072] | [-0.070, +0.062] | -0.105 | +0.095 | 52% | 52% | neither shown (the interval covers zero) |
| type tax_date | 89 | 3.053 | 2.881 | +0.173 | 0.1737 | [-0.046, +1.563] | [-0.044, +0.481] | -0.249 | +0.594 | 52% | 52% | neither shown (the interval covers zero) |
| share <= 75%: pooled | 1617 | 1.618 | 1.580 | +0.037 | 0.0288 | [-0.004, +0.125] | [-0.005, +0.087] | -0.032 | +0.107 | 47% | 47% | neither shown (the interval covers zero) |
| share > 75%: pooled | 252 | 3.190 | 3.243 | -0.053 | 0.0480 | [-0.151, +0.024] | [-0.126, +0.017] | -0.170 | +0.063 | 84% | 84% | neither shown (the interval covers zero) |
| share <= 75%: regime 2018-19 | 124 | 5.662 | 5.699 | -0.038 | 0.0549 | [-0.145, +0.071] | [-0.123, +0.047] | -0.171 | +0.095 | 71% | 71% | neither shown (the interval covers zero) |
| share <= 75%: regime 2020 | 251 | 1.417 | 1.294 | +0.124 | 0.1078 | [-0.026, +0.744] | [-0.017, +0.320] | -0.138 | +0.385 | 62% | 62% | neither shown (the interval covers zero) |
| share <= 75%: regime 2021-23 | 748 | 0.717 | 0.654 | +0.063 | 0.0479 | [-0.002, +0.245] | [-0.006, +0.146] | -0.053 | +0.179 | 47% | 47% | neither shown (the interval covers zero) |
| share <= 75%: regime 2024 | 250 | 1.411 | 1.392 | +0.019 | 0.0136 | [-0.000, +0.047] | [-0.000, +0.041] | -0.014 | +0.052 | 37% | 37% | neither shown (the interval covers zero) |
| share <= 75%: regime 2025-26 | 244 | 2.742 | 2.814 | -0.072 | 0.0232 | [-0.127, -0.029] | [-0.116, -0.032] | -0.128 | -0.016 | 33% | 33% | cost shown |
| share <= 50%: pooled | 1029 | 1.396 | 1.386 | +0.010 | 0.0336 | [-0.034, +0.138] | [-0.036, +0.070] | -0.072 | +0.091 | 40% | 40% | neither shown (the interval covers zero) |
| share > 50%: pooled | 840 | 2.361 | 2.317 | +0.044 | 0.0402 | [-0.019, +0.159] | [-0.017, +0.117] | -0.053 | +0.142 | 68% | 68% | neither shown (the interval covers zero) |
| share <= 50%: regime 2021-23 | 535 | 0.775 | 0.733 | +0.043 | 0.0627 | [-0.039, +0.362] | [-0.041, +0.154] | -0.109 | +0.195 | 44% | 44% | neither shown (the interval covers zero) |
| share <= 50%: regime 2024 | 250 | 1.411 | 1.392 | +0.019 | 0.0136 | [-0.000, +0.047] | [-0.000, +0.041] | -0.014 | +0.052 | 37% | 37% | neither shown (the interval covers zero) |
| share <= 50%: regime 2025-26 | 244 | 2.742 | 2.814 | -0.072 | 0.0232 | [-0.127, -0.029] | [-0.116, -0.032] | -0.128 | -0.016 | 33% | 33% | cost shown |
| share <= 90%: pooled | 1827 | 1.820 | 1.789 | +0.031 | 0.0260 | [-0.007, +0.106] | [-0.007, +0.077] | -0.032 | +0.095 | 51% | 51% | neither shown (the interval covers zero) |
| share > 90%: pooled | 42 | 2.252 | 2.493 | -0.240 | 0.1652 | [-0.801, +0.176] | [-0.509, +0.020] | -0.641 | +0.160 | 93% | 93% | neither shown (the interval covers zero) |
| share <= 90%: regime 2018-19 | 334 | 4.226 | 4.250 | -0.024 | 0.0342 | [-0.090, +0.039] | [-0.080, +0.033] | -0.107 | +0.059 | 78% | 78% | neither shown (the interval covers zero) |
| share <= 90%: regime 2020 | 251 | 1.417 | 1.294 | +0.124 | 0.1078 | [-0.026, +0.744] | [-0.017, +0.320] | -0.138 | +0.385 | 62% | 62% | neither shown (the interval covers zero) |
| share <= 90%: regime 2021-23 | 748 | 0.717 | 0.654 | +0.063 | 0.0479 | [-0.002, +0.245] | [-0.006, +0.146] | -0.053 | +0.179 | 47% | 47% | neither shown (the interval covers zero) |
| share <= 90%: regime 2024 | 250 | 1.411 | 1.392 | +0.019 | 0.0136 | [-0.000, +0.047] | [-0.000, +0.041] | -0.014 | +0.052 | 37% | 37% | neither shown (the interval covers zero) |
| share <= 90%: regime 2025-26 | 244 | 2.742 | 2.814 | -0.072 | 0.0232 | [-0.127, -0.029] | [-0.116, -0.032] | -0.128 | -0.016 | 33% | 33% | cost shown |

## Beside #870 (which read the workbook SOFR volume; extended panel `1e09ae43`)

| group | mean d now | 90% interval now | mean d before | 90% interval before | moved by |
|---|---|---|---|---|---|
| period 2018 H2 | -0.143 | [-0.277, -0.022] | -0.229 | [-0.359, -0.114] | +0.085 |
| period 2019 H1 | +0.043 | [-0.016, +0.118] | -0.041 | [-0.085, +0.011] | +0.085 |
| period 2019 H2 | -0.034 | [-0.141, +0.072] | -0.060 | [-0.145, +0.051] | +0.027 |
| regime 2018-19 | -0.048 | [-0.122, +0.016] | -0.114 | [-0.180, -0.058] | +0.066 |
| regime 2024 | +0.019 | [-0.000, +0.047] | -0.030 | [-0.077, -0.005] | +0.049 |
| regime 2025-26 | -0.072 | [-0.127, -0.029] | -0.048 | [-0.088, -0.015] | -0.024 |
| pooled | +0.025 | [-0.012, +0.098] | -0.001 | [-0.037, +0.064] | +0.026 |
| share <= 75%: regime 2018-19 | -0.038 | [-0.145, +0.071] | -0.060 | [-0.144, +0.058] | +0.022 |
| share <= 75%: pooled | +0.037 | [-0.004, +0.125] | +0.021 | [-0.018, +0.100] | +0.017 |

## Training frames of the with arm (lead 1), by half-year of the refit

| half-year | refits | back-filled share of rows (min to max) | imputed share of input cells (min to max) |
|---|---|---|---|
| 2018 H1 | 1 | 94% to 94% | 94% to 94% |
| 2018 H2 | 6 | 83% to 92% | 83% to 92% |
| 2019 H1 | 5 | 75% to 81% | 76% to 81% |
| 2019 H2 | 6 | 68% to 74% | 68% to 74% |
| 2020 H1 | 6 | 62% to 67% | 62% to 67% |
| 2020 H2 | 6 | 57% to 61% | 57% to 61% |
| 2021 H1 | 6 | 53% to 57% | 53% to 57% |
| 2021 H2 | 6 | 49% to 52% | 49% to 52% |
| 2022 H1 | 6 | 46% to 49% | 46% to 49% |
| 2022 H2 | 6 | 43% to 46% | 43% to 46% |
| 2023 H1 | 6 | 41% to 43% | 41% to 43% |
| 2023 H2 | 6 | 39% to 40% | 39% to 41% |
| 2024 H1 | 6 | 37% to 38% | 37% to 38% |
| 2024 H2 | 6 | 35% to 36% | 35% to 36% |
| 2025 H1 | 6 | 33% to 35% | 33% to 35% |
| 2025 H2 | 6 | 32% to 33% | 32% to 33% |

## Readings against H4's kill clause (development, not a verdict; whether the kill is read is Eleonora's)

- **2018-19, all days.** regime 2018-19: neither shown (the interval covers zero)
- **2018-19 by half-year.** period 2018 H1: not tested (too few decision days); period 2018 H2: cost shown; period 2019 H1: neither shown (the interval covers zero); period 2019 H2: neither shown (the interval covers zero)
- **2019 alone.** period 2019: neither shown (the interval covers zero)
- **2018-19 on days at or under each declared share.** share <= 75%: regime 2018-19: neither shown (the interval covers zero); share <= 50%: regime 2018-19: not tested (too few decision days); share <= 90%: regime 2018-19: neither shown (the interval covers zero)
- **every other regime and the pooled sample, for a cost.** regime 2020: neither shown (the interval covers zero); regime 2021-23: neither shown (the interval covers zero); regime 2024: neither shown (the interval covers zero); regime 2025-26: cost shown; pooled: neither shown (the interval covers zero)
