# H4 step 3 re-read: the back-fill against H5's candidate on the ruled interval (#870), development days, not a verdict

Decision days 2018-06-28 to 2025-12-23 (1869). d = CRPS(without) - CRPS(with), positive when the back-fill helps. Interval: the studentized stationary bootstrap (ruling 1), two-sided 90%. Reference value c = 2.426 (the 250-day value of the grid comparison): `mean - c se` and `mean + c se` carry both orientations of #830 (d = without - with, or the reverse).

| group | days | CRPS without | CRPS with | mean d | se | studentized 90% interval | percentile 90% (superseded) | mean - c se | mean + c se | back-filled share | imputed cells | reading |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pooled | 1869 | 1.830 | 1.831 | -0.001 | 0.0254 | [-0.037, +0.064] | [-0.038, +0.040] | -0.063 | +0.060 | 52% | 45% | neither shown (the interval covers zero) |
| regime 2018-19 | 376 | 4.005 | 4.119 | -0.114 | 0.0355 | [-0.180, -0.058] | [-0.168, -0.061] | -0.200 | -0.027 | 80% | 69% | cost shown |
| period 2018 H1 | 2 | | | | | | | | | | | not tested (too few decision days) |
| period 2018 | 126 | 3.367 | 3.605 | -0.238 | 0.0781 | [-0.373, -0.115] | [-0.349, -0.135] | -0.428 | -0.049 | 89% | 77% | cost shown |
| period 2018 H2 | 124 | 3.318 | 3.547 | -0.229 | 0.0756 | [-0.359, -0.114] | [-0.333, -0.129] | -0.412 | -0.045 | 89% | 77% | cost shown |
| period 2019 H1 | 124 | 2.931 | 2.973 | -0.041 | 0.0264 | [-0.085, +0.011] | [-0.079, +0.002] | -0.105 | +0.023 | 79% | 68% | neither shown (the interval covers zero) |
| period 2019 | 250 | 4.327 | 4.378 | -0.051 | 0.0287 | [-0.098, +0.006] | [-0.094, -0.005] | -0.120 | +0.019 | 75% | 65% | neither shown (the interval covers zero) |
| period 2019 H2 | 126 | 5.700 | 5.761 | -0.060 | 0.0502 | [-0.145, +0.051] | [-0.132, +0.021] | -0.182 | +0.062 | 71% | 61% | neither shown (the interval covers zero) |
| regime 2020 | 251 | 1.417 | 1.317 | +0.100 | 0.0934 | [-0.024, +0.470] | [-0.020, +0.257] | -0.127 | +0.326 | 62% | 54% | neither shown (the interval covers zero) |
| regime 2021-23 | 748 | 0.717 | 0.670 | +0.047 | 0.0493 | [-0.018, +0.231] | [-0.022, +0.131] | -0.073 | +0.167 | 47% | 40% | neither shown (the interval covers zero) |
| regime 2024 | 250 | 1.411 | 1.442 | -0.030 | 0.0176 | [-0.077, -0.005] | [-0.064, -0.001] | -0.073 | +0.012 | 37% | 32% | cost shown |
| regime 2025-26 | 244 | 2.742 | 2.791 | -0.048 | 0.0214 | [-0.088, -0.015] | [-0.083, -0.015] | -0.100 | +0.004 | 33% | 29% | cost shown |
| type quarter_end | 30 | 3.855 | 3.806 | +0.049 | 0.1120 | [-0.128, +0.505] | [-0.121, +0.230] | -0.222 | +0.321 | 53% | 46% | neither shown (the interval covers zero) |
| type ordinary | 1601 | 1.699 | 1.708 | -0.009 | 0.0211 | [-0.041, +0.036] | [-0.041, +0.027] | -0.060 | +0.043 | 52% | 45% | neither shown (the interval covers zero) |
| type month_end | 149 | 2.098 | 2.108 | -0.010 | 0.0369 | [-0.069, +0.061] | [-0.066, +0.050] | -0.099 | +0.080 | 52% | 45% | neither shown (the interval covers zero) |
| type tax_date | 89 | 3.053 | 2.921 | +0.133 | 0.1864 | [-0.111, +1.397] | [-0.114, +0.464] | -0.319 | +0.585 | 52% | 44% | neither shown (the interval covers zero) |
| share <= 50%: pooled | 1029 | 1.396 | 1.398 | -0.002 | 0.0350 | [-0.047, +0.121] | [-0.048, +0.060] | -0.087 | +0.083 | 40% | 34% | neither shown (the interval covers zero) |
| share > 50%: pooled | 840 | 2.361 | 2.361 | +0.000 | 0.0367 | [-0.058, +0.089] | [-0.054, +0.064] | -0.089 | +0.089 | 68% | 58% | neither shown (the interval covers zero) |
| share <= 50%: regime 2021-23 | 535 | 0.775 | 0.743 | +0.032 | 0.0654 | [-0.051, +0.324] | [-0.054, +0.148] | -0.126 | +0.191 | 44% | 38% | neither shown (the interval covers zero) |
| share <= 50%: regime 2024 | 250 | 1.411 | 1.442 | -0.030 | 0.0176 | [-0.077, -0.005] | [-0.064, -0.001] | -0.073 | +0.012 | 37% | 32% | cost shown |
| share <= 50%: regime 2025-26 | 244 | 2.742 | 2.791 | -0.048 | 0.0214 | [-0.088, -0.015] | [-0.083, -0.015] | -0.100 | +0.004 | 33% | 29% | cost shown |
| share <= 75%: pooled | 1617 | 1.618 | 1.597 | +0.021 | 0.0281 | [-0.018, +0.100] | [-0.020, +0.067] | -0.047 | +0.089 | 47% | 41% | neither shown (the interval covers zero) |
| share > 75%: pooled | 252 | 3.190 | 3.330 | -0.140 | 0.0457 | [-0.233, -0.075] | [-0.207, -0.076] | -0.251 | -0.029 | 84% | 72% | cost shown |
| share <= 75%: regime 2018-19 | 124 | 5.662 | 5.721 | -0.060 | 0.0511 | [-0.144, +0.058] | [-0.133, +0.022] | -0.184 | +0.064 | 71% | 61% | neither shown (the interval covers zero) |
| share <= 75%: regime 2020 | 251 | 1.417 | 1.317 | +0.100 | 0.0934 | [-0.024, +0.470] | [-0.020, +0.257] | -0.127 | +0.326 | 62% | 54% | neither shown (the interval covers zero) |
| share <= 75%: regime 2021-23 | 748 | 0.717 | 0.670 | +0.047 | 0.0493 | [-0.018, +0.231] | [-0.022, +0.131] | -0.073 | +0.167 | 47% | 40% | neither shown (the interval covers zero) |
| share <= 75%: regime 2024 | 250 | 1.411 | 1.442 | -0.030 | 0.0176 | [-0.077, -0.005] | [-0.064, -0.001] | -0.073 | +0.012 | 37% | 32% | cost shown |
| share <= 75%: regime 2025-26 | 244 | 2.742 | 2.791 | -0.048 | 0.0214 | [-0.088, -0.015] | [-0.083, -0.015] | -0.100 | +0.004 | 33% | 29% | cost shown |
| share <= 90%: pooled | 1827 | 1.820 | 1.814 | +0.007 | 0.0254 | [-0.030, +0.074] | [-0.031, +0.049] | -0.055 | +0.068 | 51% | 44% | neither shown (the interval covers zero) |
| share > 90%: pooled | 42 | 2.252 | 2.583 | -0.330 | 0.1762 | [-0.726, +0.147] | [-0.582, -0.069] | -0.757 | +0.097 | 93% | 80% | neither shown (the interval covers zero) |
| share <= 90%: regime 2018-19 | 334 | 4.226 | 4.312 | -0.086 | 0.0308 | [-0.144, -0.035] | [-0.134, -0.038] | -0.161 | -0.012 | 78% | 67% | cost shown |
| share <= 90%: regime 2020 | 251 | 1.417 | 1.317 | +0.100 | 0.0934 | [-0.024, +0.470] | [-0.020, +0.257] | -0.127 | +0.326 | 62% | 54% | neither shown (the interval covers zero) |
| share <= 90%: regime 2021-23 | 748 | 0.717 | 0.670 | +0.047 | 0.0493 | [-0.018, +0.231] | [-0.022, +0.131] | -0.073 | +0.167 | 47% | 40% | neither shown (the interval covers zero) |
| share <= 90%: regime 2024 | 250 | 1.411 | 1.442 | -0.030 | 0.0176 | [-0.077, -0.005] | [-0.064, -0.001] | -0.073 | +0.012 | 37% | 32% | cost shown |
| share <= 90%: regime 2025-26 | 244 | 2.742 | 2.791 | -0.048 | 0.0214 | [-0.088, -0.015] | [-0.083, -0.015] | -0.100 | +0.004 | 33% | 29% | cost shown |

## Training frames of the with arm (lead 1), by half-year of the refit

| half-year | refits | back-filled share of rows (min to max) | imputed share of input cells (min to max) |
|---|---|---|---|
| 2018 H1 | 1 | 94% to 94% | 82% to 82% |
| 2018 H2 | 6 | 83% to 92% | 72% to 80% |
| 2019 H1 | 5 | 75% to 81% | 66% to 71% |
| 2019 H2 | 6 | 68% to 74% | 60% to 65% |
| 2020 H1 | 6 | 62% to 67% | 55% to 59% |
| 2020 H2 | 6 | 57% to 61% | 50% to 54% |
| 2021 H1 | 6 | 53% to 57% | 46% to 50% |
| 2021 H2 | 6 | 49% to 52% | 43% to 46% |
| 2022 H1 | 6 | 46% to 49% | 40% to 43% |
| 2022 H2 | 6 | 43% to 46% | 38% to 40% |
| 2023 H1 | 6 | 41% to 43% | 36% to 38% |
| 2023 H2 | 6 | 39% to 40% | 34% to 35% |
| 2024 H1 | 6 | 37% to 38% | 32% to 34% |
| 2024 H2 | 6 | 35% to 36% | 31% to 32% |
| 2025 H1 | 6 | 33% to 35% | 29% to 30% |
| 2025 H2 | 6 | 32% to 33% | 28% to 29% |

## Readings against H4's kill clause (development, not a verdict; whether the kill is read is Eleonora's)

- **2018-19, all days.** regime 2018-19: cost shown
- **2018-19 by half-year.** period 2018 H1: not tested (too few decision days); period 2018 H2: cost shown; period 2019 H1: neither shown (the interval covers zero); period 2019 H2: neither shown (the interval covers zero)
- **2019 alone.** period 2019: neither shown (the interval covers zero)
- **2018-19 on days at or under each declared share.** share <= 50%: regime 2018-19: not tested (too few decision days); share <= 75%: regime 2018-19: neither shown (the interval covers zero); share <= 90%: regime 2018-19: cost shown
- **every other regime and the pooled sample, for a cost.** regime 2020: neither shown (the interval covers zero); regime 2021-23: neither shown (the interval covers zero); regime 2024: cost shown; regime 2025-26: cost shown; pooled: neither shown (the interval covers zero)
