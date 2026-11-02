# (s3c-ann-net) without the SRF cap: the candidate beside its uncapped version (#1361)

**What does the Standing Repo Facility cap do to the candidate, and how often does it bind?** On the 2026 development days the uncapped version against the candidate, grid CRPS: -0.5% [-1.9%, -0.2%]; d -0.009 [-0.032, -0.003]: **loss**; on the development window the uncapped version against the candidate, grid CRPS: skill undefined; d +0.000 [-0.001, +0.003] (1496 of 10000 resamples dropped): **undecided (skill interval: skill undefined)**.

**Hypothesis and step:** H5 (primary goal), registration design. **Development data, not a verdict** (scoring protocol v1, #640). Her ruling of 2 November 2026 (chat, relayed on #1361): report an uncapped version of the candidate as a secondary result. **(s3c-ann-net) stays the candidate; it does not change.** Nothing is registered or published and no claim changes. The uncapped version is the candidate's walk with the cap off and nothing else changed (`metadata/s3c_uncapped_1361.json`, committed before any score); both are read at the 16:00 decision instant of the records of this family, so the candidate reproduces #1288's record (pooled means equal to 1e-9).

**How to read the tables.** A difference is the candidate's loss less the uncapped version's: positive favours the uncapped version. A reading is taken from the 90% interval of mean d (her #1009 ruling), never from a point estimate. The two windows are kept apart. The cap applies only to target days at full allotment (from 11 December 2025), so every difference below comes from those days; on all others the two versions are the same forecast, and a group of such days shows `identical`. The rates are means over cells, not tested: coverage of the central 90% band (nominal 0.90), of the central 50% band (nominal 0.50) and the exceedance rate of q95 (nominal 0.05).

## The development window (targets up to 2025-12-31; #1145, #1241)

1855 decision days; refits of the candidate's walk: 89. Cells without a cap that were checked identical between the versions: 9225; cells with a cap: 50.

### Pooled

| model | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | 90% band coverage | 50% band coverage | q95 exceedance |
|---|---|---|---|---|---|---|
| B1 | 2.289 | 1.375 | 0.0635 | 0.8426 | 0.5310 | 0.0827 |
| B1' (#960) | 1.851 | 0.999 | 0.0548 | 0.8328 | 0.5309 | 0.0957 |
| B2 | 2.514 | 1.133 | 0.0643 | 0.8061 | 0.4631 | 0.1064 |
| (s3c-ann-net), the candidate | 1.601 | 0.845 | 0.0461 | 0.8748 | 0.4744 | 0.0579 |
| (s3c-ann-net-uncapped) | 1.601 | 0.844 | 0.0461 | 0.8760 | 0.4749 | 0.0567 |

| (s3c-ann-net-uncapped) against | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|
| (s3c-ann-net), the candidate | skill undefined; d +0.000 [-0.001, +0.003] (1496 of 10000 resamples dropped): **undecided (skill interval: skill undefined)** | skill undefined; d +0.000 [-0.001, +0.003] (1496 of 10000 resamples dropped): **undecided (skill interval: skill undefined)** | identical |
| B1 | +30.1% [+24.0%, +42.5%]; d +0.688 [+0.421, +1.604]: **gain** | +38.6% [+31.0%, +51.9%]; d +0.531 [+0.268, +1.616]: **gain** | +27.4% [+15.8%, +36.7%]; d +0.017 [+0.009, +0.028]: **gain** |
| B1' (#960) | +13.5% [+8.3%, +17.8%]; d +0.250 [+0.160, +0.351]: **gain** | +15.5% [+6.2%, +23.4%]; d +0.155 [+0.079, +0.262]: **gain** | +15.9% [+1.9%, +26.3%]; d +0.009 [+0.001, +0.017]: **gain** |
| B2 | +36.3% [+25.4%, +45.0%]; d +0.914 [+0.664, +1.228]: **gain** | +25.5% [+10.4%, +38.1%]; d +0.288 [+0.167, +0.464]: **gain** | +28.3% [+13.9%, +40.0%]; d +0.018 [+0.008, +0.031]: **gain** |

### Full-allotment target days against the others

| full allotment | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| target days at full allotment | 14 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| other target days | 1845 | identical | identical | identical |

| full allotment | days | 90% band coverage (candidate) | 90% band coverage (uncapped) | 50% band coverage (candidate) | 50% band coverage (uncapped) | q95 exceedance (candidate) | q95 exceedance (uncapped) |
|---|---|---|---|---|---|---|---|
| other target days | 1845 | 0.875 | 0.875 | 0.473 | 0.473 | 0.057 | 0.057 |
| target days at full allotment | 14 | 0.743 | 1.000 | 0.686 | 0.818 | 0.257 | 0.000 |

### How often and by how much the cap binds

A cell binds when the uncapped version has a quantile above the line (IORB + 10 bp). The moves are the uncapped value less the capped one, over the cells in which the quantile moves. `outcome above the line` counts the cells at full allotment whose outcome is above the line.

| lead | cells | at full allotment | cap binds | share | outcome above the line | q95 moved: mean / largest (bp) | q99 moved: mean / largest (bp) | largest quantile moved: mean / largest (bp) |
|---|---|---|---|---|---|---|---|---|
| all | 9275 | 50 | 50 | 1.000 | 11 | 50: 10.27 / 32.91 | 50: 28.30 / 51.74 | 50: 28.30 / 51.74 |
| h=1 | 1855 | 10 | 10 | 1.000 | 1 | 10: 7.53 / 16.12 | 10: 23.41 / 33.05 | 10: 23.41 / 33.05 |
| h=2 | 1855 | 10 | 10 | 1.000 | 2 | 10: 9.31 / 18.09 | 10: 27.08 / 42.17 | 10: 27.08 / 42.17 |
| h=3 | 1855 | 10 | 10 | 1.000 | 3 | 10: 10.22 / 19.96 | 10: 28.23 / 39.61 | 10: 28.23 / 39.61 |
| h=4 | 1855 | 10 | 10 | 1.000 | 2 | 10: 10.38 / 14.62 | 10: 29.94 / 34.19 | 10: 29.94 / 34.19 |
| h=5 | 1855 | 10 | 10 | 1.000 | 3 | 10: 13.90 / 32.91 | 10: 32.84 / 51.74 | 10: 32.84 / 51.74 |

### By lead

| lead | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| h=1 | 1855 | skill undefined; d -0.001 [-0.011, +0.000] (1496 of 10000 resamples dropped): **undecided (skill interval: skill undefined)** | skill undefined; d -0.001 [-0.011, +0.000] (1496 of 10000 resamples dropped): **undecided (skill interval: skill undefined)** | identical |
| h=2 | 1855 | skill undefined; d -0.001 [-0.015, +0.000] (1496 of 10000 resamples dropped): **undecided (skill interval: skill undefined)** | skill undefined; d -0.001 [-0.015, +0.000] (1496 of 10000 resamples dropped): **undecided (skill interval: skill undefined)** | identical |
| h=3 | 1855 | skill undefined; d -0.001 [-0.004, +0.000] (1496 of 10000 resamples dropped): **undecided (skill interval: skill undefined)** | skill undefined; d -0.001 [-0.004, +0.000] (1496 of 10000 resamples dropped): **undecided (skill interval: skill undefined)** | identical |
| h=4 | 1855 | skill undefined; d -0.000 [-0.001, +0.000] (1496 of 10000 resamples dropped): **undecided (skill interval: skill undefined)** | skill undefined; d -0.000 [-0.001, +0.000] (1496 of 10000 resamples dropped): **undecided (skill interval: skill undefined)** | identical |
| h=5 | 1855 | skill undefined; d +0.005 [-0.001, +0.138] (1496 of 10000 resamples dropped): **undecided (skill interval: skill undefined)** | skill undefined; d +0.005 [-0.001, +0.138] (1496 of 10000 resamples dropped): **undecided (skill interval: skill undefined)** | identical |

### By regime

| regime | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| 2018-19 | 361 | identical | identical | identical |
| 2020 | 251 | identical | identical | identical |
| 2021-23 | 748 | identical | identical | identical |
| 2024 | 250 | identical | identical | identical |
| 2025-26 | 249 | skill undefined; d +0.036 [-0.013, +1.087] (838 of 10000 resamples dropped): **undecided (skill interval: skill undefined)** | skill undefined; d +0.036 [-0.013, +1.087] (838 of 10000 resamples dropped): **undecided (skill interval: skill undefined)** | identical |

### By pressure-day type of the target day

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 1591 | skill undefined; d -0.000 [-0.001, +0.000] (1489 of 10000 resamples dropped): **undecided (skill interval: skill undefined)** | skill undefined; d -0.000 [-0.001, +0.000] (1489 of 10000 resamples dropped): **undecided (skill interval: skill undefined)** | identical |
| quarter_end_turn | 44 | identical | identical | identical |
| tax_date | 89 | skill undefined; d -0.012 [-0.041, +0.004] (2569 of 10000 resamples dropped): **undecided (skill interval: skill undefined)** | skill undefined; d -0.012 [-0.041, +0.004] (2569 of 10000 resamples dropped): **undecided (skill interval: skill undefined)** | identical |
| turn | 120 | identical | identical | identical |
| year_end | 15 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

### Rates by regime

| regime | days | 90% band coverage (candidate) | 90% band coverage (uncapped) | 50% band coverage (candidate) | 50% band coverage (uncapped) | q95 exceedance (candidate) | q95 exceedance (uncapped) |
|---|---|---|---|---|---|---|---|
| 2018-19 | 361 | 0.868 | 0.868 | 0.427 | 0.427 | 0.062 | 0.062 |
| 2020 | 251 | 0.865 | 0.865 | 0.470 | 0.470 | 0.041 | 0.041 |
| 2021-23 | 748 | 0.875 | 0.875 | 0.518 | 0.518 | 0.062 | 0.062 |
| 2024 | 250 | 0.881 | 0.881 | 0.464 | 0.464 | 0.054 | 0.054 |
| 2025-26 | 249 | 0.887 | 0.901 | 0.429 | 0.436 | 0.064 | 0.050 |

### Rates by pressure day type

| pressure day type | days | 90% band coverage (candidate) | 90% band coverage (uncapped) | 50% band coverage (candidate) | 50% band coverage (uncapped) | q95 exceedance (candidate) | q95 exceedance (uncapped) |
|---|---|---|---|---|---|---|---|
| ordinary | 1591 | 0.890 | 0.891 | 0.499 | 0.499 | 0.044 | 0.043 |
| quarter_end_turn | 44 | 0.586 | 0.586 | 0.150 | 0.150 | 0.336 | 0.336 |
| tax_date | 89 | 0.840 | 0.847 | 0.335 | 0.342 | 0.076 | 0.070 |
| turn | 120 | 0.833 | 0.833 | 0.388 | 0.388 | 0.110 | 0.110 |
| year_end | 15 | 0.613 | 0.680 | 0.400 | 0.467 | 0.267 | 0.200 |

Groups of fewer than 20 days, not tested: full_allotment/target days at full allotment (14); pressure_day_type/year_end (15).

## The 2026 development days (targets 2026-01-02 to 2026-09-03; #1229, #1252)

165 decision days; refits of the candidate's walk: 97. Cells without a cap that were checked identical between the versions: 0; cells with a cap: 825.

### Pooled

| model | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) | 90% band coverage | 50% band coverage | q95 exceedance |
|---|---|---|---|---|---|---|
| B1 | 2.160 | 0.825 | 0.0562 | 0.8958 | 0.4642 | 0.0497 |
| B1' (#960) | 1.869 | 0.621 | 0.0430 | 0.8873 | 0.4388 | 0.0570 |
| B2 | 2.155 | 0.636 | 0.0356 | 0.9685 | 0.7721 | 0.0012 |
| (s3c-ann-net), the candidate | 1.669 | 0.514 | 0.0352 | 0.8921 | 0.4618 | 0.0303 |
| (s3c-ann-net-uncapped) | 1.678 | 0.523 | 0.0352 | 0.8933 | 0.4618 | 0.0291 |

| (s3c-ann-net-uncapped) against | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|
| (s3c-ann-net), the candidate | -0.5% [-1.9%, -0.2%]; d -0.009 [-0.032, -0.003]: **loss** | -1.8% [-5.1%, -0.4%]; d -0.009 [-0.032, -0.003]: **loss** | skill undefined; d -0.000 [-0.000, -0.000] (1042 of 10000 resamples dropped): **loss (skill interval: skill undefined)** |
| B1 | +22.3% [-0.3%, +35.0%]; d +0.482 [+0.136, +0.792]: **gain (skill interval: undecided)** | +36.6% [+22.4%, +50.0%]; d +0.302 [+0.126, +0.653]: **gain** | +37.5% [+21.6%, +50.6%]; d +0.021 [+0.005, +0.055]: **gain** |
| B1' (#960) | +10.2% [-13.1%, +22.3%]; d +0.191 [-0.148, +0.426]: **undecided** | +15.8% [+1.8%, +27.4%]; d +0.098 [+0.006, +0.213]: **gain** | +18.3% [-1.4%, +45.0%]; d +0.008 [-0.002, +0.038]: **undecided** |
| B2 | +22.1% [+3.5%, +41.4%]; d +0.477 [+0.097, +0.942]: **gain** | +17.7% [-11.0%, +36.1%]; d +0.112 [-0.071, +0.235]: **undecided** | +1.4% [-36.9%, +23.4%]; d +0.000 [-0.019, +0.009]: **undecided** |

### Full-allotment target days against the others

| full allotment | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| target days at full allotment | 169 | -0.7% [-3.0%, -0.1%]; d -0.012 [-0.050, -0.003]: **loss** | -2.1% [-6.7%, -0.4%]; d -0.012 [-0.050, -0.003]: **loss** | skill undefined; d -0.000 [-0.000, -0.000] (1064 of 10000 resamples dropped): **loss (skill interval: skill undefined)** |

| full allotment | days | 90% band coverage (candidate) | 90% band coverage (uncapped) | 50% band coverage (candidate) | 50% band coverage (uncapped) | q95 exceedance (candidate) | q95 exceedance (uncapped) |
|---|---|---|---|---|---|---|---|
| target days at full allotment | 169 | 0.889 | 0.895 | 0.465 | 0.465 | 0.034 | 0.028 |

### How often and by how much the cap binds

A cell binds when the uncapped version has a quantile above the line (IORB + 10 bp). The moves are the uncapped value less the capped one, over the cells in which the quantile moves. `outcome above the line` counts the cells at full allotment whose outcome is above the line.

| lead | cells | at full allotment | cap binds | share | outcome above the line | q95 moved: mean / largest (bp) | q99 moved: mean / largest (bp) | largest quantile moved: mean / largest (bp) |
|---|---|---|---|---|---|---|---|---|
| all | 825 | 825 | 404 | 0.490 | 1 | 119: 3.18 / 11.02 | 404: 5.48 / 26.00 | 404: 5.48 / 26.00 |
| h=1 | 165 | 165 | 75 | 0.455 | 1 | 16: 2.70 / 11.02 | 75: 5.22 / 21.30 | 75: 5.22 / 21.30 |
| h=2 | 165 | 165 | 59 | 0.358 | 0 | 19: 3.49 / 10.18 | 59: 5.57 / 20.23 | 59: 5.57 / 20.23 |
| h=3 | 165 | 165 | 85 | 0.515 | 0 | 24: 3.54 / 7.13 | 85: 5.30 / 20.82 | 85: 5.30 / 20.82 |
| h=4 | 165 | 165 | 86 | 0.521 | 0 | 27: 3.31 / 8.98 | 86: 5.77 / 25.30 | 86: 5.77 / 25.30 |
| h=5 | 165 | 165 | 99 | 0.600 | 0 | 33: 2.86 / 10.31 | 99: 5.52 / 26.00 | 99: 5.52 / 26.00 |

### By lead

| lead | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| h=1 | 165 | -0.6% [-7.1%, -0.1%]; d -0.009 [-0.111, -0.001]: **loss** | -2.0% [-16.9%, -0.2%]; d -0.009 [-0.111, -0.001]: **loss** | skill undefined; d -0.000 [-0.000, -0.000] (1042 of 10000 resamples dropped): **loss (skill interval: skill undefined)** |
| h=2 | 165 | -0.5% [-2.3%, -0.1%]; d -0.008 [-0.037, -0.002]: **loss** | -1.6% [-5.9%, -0.3%]; d -0.008 [-0.037, -0.002]: **loss** | identical |
| h=3 | 165 | -0.5% [-1.3%, -0.2%]; d -0.009 [-0.022, -0.003]: **loss** | -1.6% [-3.6%, -0.4%]; d -0.009 [-0.022, -0.003]: **loss** | identical |
| h=4 | 165 | -0.5% [-1.3%, -0.2%]; d -0.009 [-0.023, -0.004]: **loss** | -1.7% [-3.8%, -0.5%]; d -0.009 [-0.023, -0.004]: **loss** | identical |
| h=5 | 165 | -0.6% [-1.6%, -0.2%]; d -0.011 [-0.029, -0.004]: **loss** | -1.9% [-4.6%, -0.6%]; d -0.011 [-0.029, -0.004]: **loss** | identical |

### By pressure-day type of the target day

| pressure day type | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| ordinary | 146 | -0.7% [-3.7%, -0.1%]; d -0.012 [-0.061, -0.002]: **loss** | -2.4% [-9.0%, -0.2%]; d -0.012 [-0.061, -0.002]: **loss** | skill undefined; d -0.000 [-0.000, -0.000] (919 of 10000 resamples dropped): **loss (skill interval: skill undefined)** |
| quarter_end_turn | 4 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| tax_date | 6 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| turn | 12 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| year_end | 1 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

### By target month

| month | days | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|
| 2026-01 | 20 | -4.5% [-9.5%, -2.1%]; d -0.066 [-0.228, +0.005]: **undecided (skill interval: loss)** | -6.0% [-9.0%, -4.4%]; d -0.066 [-0.228, +0.005]: **undecided (skill interval: loss)** | identical |
| 2026-02 | 19 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |
| 2026-03 | 22 | -0.2% [-0.4%, -0.1%]; d -0.002 [-0.004, -0.001]: **loss** | -0.3% [-0.7%, -0.1%]; d -0.002 [-0.004, -0.001]: **loss** | identical |
| 2026-04 | 21 | -0.4% [-2.1%, +0.1%]; d -0.007 [-0.032, +0.001]: **undecided** | -1.2% [-5.5%, +2.6%]; d -0.007 [-0.032, +0.001]: **undecided** | skill undefined; d -0.000 [-0.000, +0.000] (2079 of 10000 resamples dropped): **undecided (skill interval: skill undefined)** |
| 2026-05 | 20 | skill undefined; d -0.011 [-0.045, +0.005] (3 of 10000 resamples dropped): **undecided (skill interval: skill undefined)** | skill undefined; d -0.011 [-0.045, +0.005] (3 of 10000 resamples dropped): **undecided (skill interval: skill undefined)** | identical |
| 2026-06 | 21 | skill undefined; d -0.000 [-0.000, +0.000] (8 of 10000 resamples dropped): **undecided (skill interval: skill undefined)** | skill undefined; d -0.000 [-0.000, +0.000] (8 of 10000 resamples dropped): **undecided (skill interval: skill undefined)** | identical |
| 2026-07 | 22 | -0.2% [-0.8%, +0.0%]; d -0.004 [-0.017, -0.000]: **loss (skill interval: undecided)** | -2.0% [-3.5%, -0.3%]; d -0.004 [-0.017, -0.000]: **loss** | skill undefined; d -0.000 [-0.000, +0.000] (2081 of 10000 resamples dropped): **undecided (skill interval: skill undefined)** |
| 2026-08 | 21 | skill undefined; d -0.006 [-0.110, +0.003] (25 of 10000 resamples dropped): **undecided (skill interval: skill undefined)** | skill undefined; d -0.006 [-0.110, +0.003] (25 of 10000 resamples dropped): **undecided (skill interval: skill undefined)** | identical |
| 2026-09 | 3 | not tested (fewer than 20 days) | not tested (fewer than 20 days) | not tested (fewer than 20 days) |

### Rates by pressure day type

| pressure day type | days | 90% band coverage (candidate) | 90% band coverage (uncapped) | 50% band coverage (candidate) | 50% band coverage (uncapped) | q95 exceedance (candidate) | q95 exceedance (uncapped) |
|---|---|---|---|---|---|---|---|
| ordinary | 146 | 0.883 | 0.883 | 0.453 | 0.453 | 0.029 | 0.029 |
| quarter_end_turn | 4 | 1.000 | 1.000 | 0.500 | 0.500 | 0.000 | 0.000 |
| tax_date | 6 | 0.900 | 0.900 | 0.533 | 0.533 | 0.100 | 0.100 |
| turn | 12 | 1.000 | 1.000 | 0.600 | 0.600 | 0.000 | 0.000 |
| year_end | 1 | 0.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 |

Groups of fewer than 20 days, not tested: month/2026-02 (19); month/2026-09 (3); pressure_day_type/quarter_end_turn (4); pressure_day_type/tax_date (6); pressure_day_type/turn (12); pressure_day_type/year_end (1); target_day_type/fomc_day (10); target_day_type/month_end (16); target_day_type/quarter_end (2); target_day_type/tax_date (6).

## What this does and does not show

- It shows what the cap does to the candidate's scores on days already seen, and how often and by how much it moves a quantile.
- It does not show how the uncapped version does when the facility is at full allotment for long: the development window holds only the days of December 2025 after it, and 2026 holds the rest. A tail rate on so few days is not read.
- It is a development figure on days already seen, not a verdict. The confirmation days give the verdict.
- Both versions are read at the 16:00 instant; the move to 18:00 (#1312) is a separate re-run.

## Questions for Eleonora (marked; defaults change no claim)

**Question 1. How the uncapped version is reported in the registration.** The directive says the uncapped version is logged and scored prospectively beside the candidate, reported and not deciding. The draft of the section is `docs/decisions/drafts/h5-uncapped-secondary.md`. The full-allotment period holds few days, so a tail rate on it carries a wide interval whichever version is read.

**Options** (the default applies if you have not answered by the next 5 pm batch):

1. **Report it as drafted: scored beside the candidate on every confirmation day, split by full-allotment and other days, reported only** (default). Nothing the project claims changes.
2. **Also report the cap's binding frequency and size on the confirmation days** as a standing table next to the score, so that a reader sees when the cap decided the forecast.
3. **Do not log it**, and report this page's development figures only.

**Question 2. What follows from this result.** (s3c-ann-net) stays the H5 candidate. Whether the cap stays in the candidate is a choice for her, and the figures above rest on days already seen, most of them before the facility was at full allotment.

**Options** (the default applies if you have not answered by the next 5 pm batch):

1. **The candidate keeps the cap and nothing changes** (default).
2. **Draft a directive that tests the candidate without the cap prospectively**, on the confirmation days only, under the scoring protocol.
