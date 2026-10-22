# The floor flag as a pool selector (#966, H5 step 3)

**Hypothesis and step:** H5 (primary goal), step 3 (2021-23 and the residual pools). **Development data only: this is not a verdict** (scoring protocol v1, #640) and nothing here is registered or published. Every figure is read from `docs/research/floor-flag-966/result.json` by `scripts/floor_flag_966.py report`; the declaration is `metadata/floor_flag_966.json`, committed before any score. Studentized stationary bootstrap (ruling 1), mean block 10 business days, 10,000 draws, seed 966; the interval is a two-sided 90% interval. Skill is `mean(d) / mean(S(benchmark))` with `d = S(benchmark) - S(candidate)`: positive favours the candidate. Panel digest `4ddc3882…`.

## The flag

On from rows: 759; off 1,306; undefined 39. The runs of consecutive rows with the flag on: 2021-04-21 to 2023-12-08; 2024-02-14 to 2024-07-08. (Lens B read it on from 2021-04-21 to 2023-12-11 and from 2024-02-14 to 2024-07-09.)

| regime (decision day) | days | flag on | off | undefined |
|---|---|---|---|---|
| 2018-19 | 362 | 0 | 362 | 0 |
| 2020 | 251 | 0 | 251 | 0 |
| 2021-23 | 748 | 660 | 88 | 0 |
| 2024 | 250 | 99 | 151 | 0 |
| 2025-26 | 244 | 0 | 244 | 0 |

## Kill rules, as declared

- (ii) against its own pool (mean reversion) on the 2024-26 days: grid CRPS skill +4.1% [+3.2%, +5.1%]. Kill rule not met: the interval lies above 0.
- (iii) against `gbm_funding`: **not run**, by Eleonora's ruling of 22 October 2026 on #966 (comment 6350221714): the Mac run of `gbm_funding`'s walks is skipped. Kill rule (iii) is not evaluated.
- (iv) against its own pool (the scaled mean reversion, #941) on the 2024-26 days: grid CRPS skill -0.4% [-1.2%, +0.4%]. **Kill rule (iv) met**: the interval covers 0 or lies below it.
- (v) the two-part rule on the scaled mean reversion, against the scaled mean reversion pooled: grid CRPS skill -1.2% [-2.1%, -0.4%]. **Kill rule (v) met**: the upper bound is below 0.

A kill is a statement about development days; it neither supports nor kills H5 (the declaration's `kill.reading`).

## Arms (iv) and (v): the flag on the best model (#941's scaled mean reversion)

Added on Eleonora's ruling of 22 October 2026 (declaration amended before any score of these arms). (iv) restricts the scaled model's standardised residual pool to the training pairs whose origin has the anchor's flag; (v) is B1 while the flag is on and the scaled model otherwise. Their own pool and the model they are compared with is the scaled model, `spread_mr_fhs_mad20_f0.5`.

1,855 decision days, 2018-07-19 to 2025-12-23 (the last target is 2025-12-31). Refits whose own flag pool was used for the scaled arm (not the whole-lead fallback), by lead 1 to 5: flag on [53, 53, 53, 53, 53], flag off [69, 69, 69, 69, 69].

### Arms (iv) and (v): grid CRPS, pooled (1,855 decision days), skill [90%]

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 1.698 | +25.8% [+19.6%, +42.2%] | +32.6% [+22.0%, +42.0%] |  |
| (iv) flag-restricted scaled mean reversion | 1.700 | +25.7% [+19.4%, +42.1%] | +32.5% [+21.9%, +42.0%] | -0.1% [-0.6%, +0.3%] |
| (v) scaled mean reversion, two-part | 1.718 | +24.9% [+18.5%, +42.2%] | +31.8% [+21.4%, +41.0%] | -1.2% [-2.1%, -0.4%] |
| B1 | 2.289 |  |  |  |
| B2 | 2.518 |  |  |  |

#### grid CRPS by lead

**h = 1** (1855 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 1.557 | +22.8% [+17.2%, +34.1%] | +37.2% [+21.1%, +47.1%] |  |
| (iv) flag-restricted scaled mean reversion | 1.559 | +22.7% [+17.1%, +34.2%] | +37.2% [+21.1%, +47.1%] | -0.1% [-0.5%, +0.3%] |
| (v) scaled mean reversion, two-part | 1.562 | +22.6% [+16.9%, +34.1%] | +37.0% [+21.0%, +46.9%] | -0.3% [-0.9%, +0.2%] |
| B1 | 2.017 |  |  |  |
| B2 | 2.480 |  |  |  |

**h = 2** (1855 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 1.657 | +25.2% [+19.1%, +40.8%] | +33.9% [+21.9%, +43.5%] |  |
| (iv) flag-restricted scaled mean reversion | 1.659 | +25.1% [+19.0%, +40.8%] | +33.8% [+22.0%, +43.4%] | -0.1% [-0.6%, +0.3%] |
| (v) scaled mean reversion, two-part | 1.669 | +24.6% [+18.4%, +40.8%] | +33.4% [+21.6%, +42.9%] | -0.8% [-1.6%, -0.0%] |
| B1 | 2.215 |  |  |  |
| B2 | 2.507 |  |  |  |

**h = 3** (1855 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 1.715 | +26.6% [+20.4%, +42.2%] | +32.0% [+21.6%, +41.4%] |  |
| (iv) flag-restricted scaled mean reversion | 1.718 | +26.5% [+20.3%, +42.0%] | +31.9% [+21.5%, +41.3%] | -0.2% [-0.6%, +0.3%] |
| (v) scaled mean reversion, two-part | 1.732 | +25.9% [+19.6%, +42.2%] | +31.3% [+21.2%, +40.5%] | -1.0% [-2.0%, -0.1%] |
| B1 | 2.338 |  |  |  |
| B2 | 2.523 |  |  |  |

**h = 4** (1855 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 1.757 | +27.1% [+20.3%, +44.4%] | +30.7% [+21.3%, +39.7%] |  |
| (iv) flag-restricted scaled mean reversion | 1.759 | +27.0% [+20.1%, +44.3%] | +30.6% [+21.2%, +39.7%] | -0.1% [-0.7%, +0.4%] |
| (v) scaled mean reversion, two-part | 1.784 | +25.9% [+18.9%, +44.4%] | +29.6% [+20.5%, +38.4%] | -1.6% [-2.7%, -0.6%] |
| B1 | 2.408 |  |  |  |
| B2 | 2.534 |  |  |  |

**h = 5** (1855 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 1.803 | +26.9% [+19.8%, +45.1%] | +29.3% [+20.0%, +38.3%] |  |
| (iv) flag-restricted scaled mean reversion | 1.805 | +26.8% [+19.7%, +45.0%] | +29.2% [+19.8%, +38.2%] | -0.1% [-0.7%, +0.4%] |
| (v) scaled mean reversion, two-part | 1.842 | +25.3% [+17.9%, +45.0%] | +27.7% [+18.8%, +36.6%] | -2.2% [-3.5%, -1.1%] |
| B1 | 2.465 |  |  |  |
| B2 | 2.549 |  |  |  |

#### grid CRPS by regime (target day)

**2018-19** (361 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 3.817 | +34.1% [+24.5%, +58.7%] | +14.5% [+1.1%, +28.0%] |  |
| (iv) flag-restricted scaled mean reversion | 3.815 | +34.1% [+24.5%, +58.9%] | +14.5% [+1.1%, +28.0%] | +0.0% [-0.1%, +0.2%] |
| (v) scaled mean reversion, two-part | 3.817 | undefined | undefined | undefined |
| B1 | 5.791 |  |  |  |
| B2 | 4.462 |  |  |  |

**2020** (251 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 1.407 | +14.6% [+6.4%, +22.7%] | +49.7% [+24.5%, +70.6%] |  |
| (iv) flag-restricted scaled mean reversion | 1.407 | +14.6% [+6.4%, +22.7%] | +49.7% [+24.5%, +70.6%] | -0.0% [-0.1%, +0.1%] |
| (v) scaled mean reversion, two-part | 1.407 | undefined | undefined | undefined |
| B1 | 1.648 |  |  |  |
| B2 | 2.797 |  |  |  |

**2021-23** (748 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 0.659 | +5.5% [-0.7%, +10.6%] | +55.0% [+40.7%, +67.4%] |  |
| (iv) flag-restricted scaled mean reversion | 0.660 | +5.4% [-2.2%, +11.8%] | +55.0% [+40.1%, +67.8%] | -0.1% [-2.5%, +2.4%] |
| (v) scaled mean reversion, two-part | 0.694 | +0.5% [-2.9%, +3.1%] | +52.7% [+39.1%, +64.1%] | -5.2% [-10.1%, -0.1%] |
| B1 | 0.697 |  |  |  |
| B2 | 1.465 |  |  |  |

**2024** (250 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 1.204 | +25.3% [+18.5%, +35.2%] | +13.6% [+2.6%, +23.4%] |  |
| (iv) flag-restricted scaled mean reversion | 1.221 | +24.3% [+16.8%, +34.0%] | +12.4% [+1.3%, +22.5%] | -1.4% [-3.3%, -0.1%] |
| (v) scaled mean reversion, two-part | 1.252 | +22.4% [+13.6%, +35.3%] | +10.2% [-0.2%, +19.7%] | -3.9% [-12.4%, -0.7%] |
| B1 | 1.613 |  |  |  |
| B2 | 1.394 |  |  |  |

**2025-26** (249 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 2.571 | +23.4% [+16.4%, +30.3%] | +31.9% [+7.6%, +51.8%] |  |
| (iv) flag-restricted scaled mean reversion | 2.570 | +23.4% [+16.2%, +30.5%] | +31.9% [+7.6%, +51.6%] | +0.1% [-0.8%, +1.1%] |
| (v) scaled mean reversion, two-part | 2.571 | undefined | undefined | undefined |
| B1 | 3.357 |  |  |  |
| B2 | 3.776 |  |  |  |

#### grid CRPS by window (target day)

**2021-23** (748 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 0.659 | +5.5% [-0.7%, +10.6%] | +55.0% [+40.7%, +67.4%] |  |
| (iv) flag-restricted scaled mean reversion | 0.660 | +5.4% [-2.2%, +11.8%] | +55.0% [+40.1%, +67.8%] | -0.1% [-2.5%, +2.4%] |
| (v) scaled mean reversion, two-part | 0.694 | +0.5% [-2.9%, +3.1%] | +52.7% [+39.1%, +64.1%] | -5.2% [-10.1%, -0.1%] |
| B1 | 0.697 |  |  |  |
| B2 | 1.465 |  |  |  |

**2024-26** (499 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 1.887 | +24.0% [+18.8%, +29.2%] | +27.0% [+9.6%, +45.2%] |  |
| (iv) flag-restricted scaled mean reversion | 1.894 | +23.7% [+18.3%, +29.1%] | +26.7% [+9.1%, +45.0%] | -0.4% [-1.2%, +0.4%] |
| (v) scaled mean reversion, two-part | 1.910 | +23.1% [+17.6%, +28.7%] | +26.0% [+8.6%, +44.7%] | -1.3% [-4.1%, -0.3%] |
| B1 | 2.483 |  |  |  |
| B2 | 2.583 |  |  |  |

**before 2021** (612 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 2.829 | +30.9% [+22.3%, +54.5%] | +25.1% [+9.0%, +41.2%] |  |
| (iv) flag-restricted scaled mean reversion | 2.828 | +30.9% [+22.3%, +54.6%] | +25.2% [+9.1%, +41.2%] | +0.0% [-0.1%, +0.1%] |
| (v) scaled mean reversion, two-part | 2.829 | undefined | undefined | undefined |
| B1 | 4.092 |  |  |  |
| B2 | 3.779 |  |  |  |

#### grid CRPS by pressure-day type (target day)

**month_end** (150 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 1.940 | +13.8% [+7.9%, +19.9%] | +33.8% [+15.6%, +51.3%] |  |
| (iv) flag-restricted scaled mean reversion | 1.948 | +13.4% [+7.9%, +19.0%] | +33.5% [+15.1%, +51.0%] | -0.4% [-1.4%, +0.5%] |
| (v) scaled mean reversion, two-part | 1.969 | +12.5% [+6.6%, +19.7%] | +32.8% [+15.5%, +50.1%] | -1.5% [-6.6%, -0.0%] |
| B1 | 2.250 |  |  |  |
| B2 | 2.929 |  |  |  |

**ordinary** (1590 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 1.403 | +30.9% [+20.7%, +59.1%] | +33.3% [+24.4%, +42.0%] |  |
| (iv) flag-restricted scaled mean reversion | 1.403 | +30.9% [+20.7%, +58.8%] | +33.2% [+24.4%, +42.0%] | -0.0% [-0.6%, +0.5%] |
| (v) scaled mean reversion, two-part | 1.424 | +29.9% [+19.6%, +59.2%] | +32.3% [+23.6%, +40.9%] | -1.5% [-2.7%, -0.5%] |
| B1 | 2.031 |  |  |  |
| B2 | 2.102 |  |  |  |

**quarter_end** (30 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 6.271 | +9.8% [+7.9%, +11.5%] | +17.0% [-33.6%, +53.3%] |  |
| (iv) flag-restricted scaled mean reversion | 6.314 | +9.2% [+7.2%, +11.4%] | +16.5% [-34.3%, +53.6%] | -0.7% [-5.4%, +1.7%] |
| (v) scaled mean reversion, two-part | 6.299 | undefined | undefined | undefined |
| B1 | 6.956 |  |  |  |
| B2 | 7.560 |  |  |  |

**tax_date** (89 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 5.121 | +6.8% [-6.1%, +13.7%] | +33.8% [-60.3%, +57.6%] |  |
| (iv) flag-restricted scaled mean reversion | 5.131 | +6.6% [-4.5%, +12.7%] | +33.7% [-55.8%, +57.4%] | -0.2% [-1.0%, +0.5%] |
| (v) scaled mean reversion, two-part | 5.106 | undefined | undefined | undefined |
| B1 | 5.496 |  |  |  |
| B2 | 7.738 |  |  |  |

#### grid CRPS by flag state at the anchor

**off** (1096 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 2.455 | +28.2% [+21.7%, +44.8%] | +28.1% [+16.3%, +39.4%] |  |
| (iv) flag-restricted scaled mean reversion | 2.458 | +28.2% [+21.6%, +44.8%] | +28.0% [+16.1%, +39.3%] | -0.1% [-0.4%, +0.1%] |
| (v) scaled mean reversion, two-part | 2.455 | undefined | undefined | undefined |
| B1 | 3.421 |  |  |  |
| B2 | 3.416 |  |  |  |

**on** (759 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 0.604 | +7.6% [+1.6%, +12.5%] | +50.6% [+36.2%, +63.8%] |  |
| (iv) flag-restricted scaled mean reversion | 0.605 | +7.4% [-0.2%, +14.0%] | +50.5% [+35.5%, +64.4%] | -0.1% [-2.8%, +2.5%] |
| (v) scaled mean reversion, two-part | 0.654 | undefined | undefined | undefined |
| B1 | 0.654 |  |  |  |
| B2 | 1.222 |  |  |  |

### Arms (iv) and (v): upper-tail twCRPS, pooled (1,855 decision days), skill [90%]

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 0.896 | +34.8% [+27.1%, +51.7%] | +20.8% [+7.2%, +33.8%] |  |
| (iv) flag-restricted scaled mean reversion | 0.896 | +34.8% [+27.1%, +51.7%] | +20.8% [+7.1%, +33.7%] | -0.0% [-0.1%, +0.1%] |
| (v) scaled mean reversion, two-part | 0.897 | +34.8% [+27.0%, +51.7%] | +20.8% [+7.2%, +33.7%] | -0.1% [-0.2%, -0.0%] |
| B1 | 1.375 |  |  |  |
| B2 | 1.131 |  |  |  |

#### upper-tail twCRPS by lead

**h = 1** (1855 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 0.878 | +31.6% [+25.9%, +40.5%] | +21.0% [-3.1%, +36.6%] |  |
| (iv) flag-restricted scaled mean reversion | 0.880 | +31.5% [+25.7%, +40.5%] | +20.9% [-3.0%, +36.4%] | -0.2% [-0.4%, +0.1%] |
| (v) scaled mean reversion, two-part | 0.879 | +31.6% [+25.8%, +40.5%] | +21.0% [-3.1%, +36.6%] | -0.0% [-0.1%, -0.0%] |
| B1 | 1.283 |  |  |  |
| B2 | 1.112 |  |  |  |

**h = 2** (1855 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 0.892 | +34.1% [+27.1%, +48.8%] | +20.8% [+4.8%, +34.8%] |  |
| (iv) flag-restricted scaled mean reversion | 0.892 | +34.1% [+27.1%, +48.9%] | +20.7% [+4.7%, +34.6%] | -0.1% [-0.2%, +0.1%] |
| (v) scaled mean reversion, two-part | 0.893 | +34.0% [+27.1%, +48.8%] | +20.7% [+4.7%, +34.7%] | -0.1% [-0.2%, -0.0%] |
| B1 | 1.353 |  |  |  |
| B2 | 1.126 |  |  |  |

**h = 3** (1855 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 0.897 | +35.8% [+28.0%, +51.7%] | +20.8% [+8.0%, +33.6%] |  |
| (iv) flag-restricted scaled mean reversion | 0.898 | +35.8% [+28.0%, +51.6%] | +20.8% [+7.9%, +33.6%] | -0.0% [-0.2%, +0.1%] |
| (v) scaled mean reversion, two-part | 0.898 | +35.7% [+28.0%, +51.7%] | +20.8% [+8.0%, +33.5%] | -0.1% [-0.2%, -0.0%] |
| B1 | 1.398 |  |  |  |
| B2 | 1.133 |  |  |  |

**h = 4** (1855 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 0.899 | +36.6% [+27.5%, +56.4%] | +20.9% [+10.0%, +32.2%] |  |
| (iv) flag-restricted scaled mean reversion | 0.899 | +36.6% [+27.5%, +56.4%] | +21.0% [+10.1%, +32.3%] | +0.1% [-0.1%, +0.3%] |
| (v) scaled mean reversion, two-part | 0.900 | +36.5% [+27.4%, +56.4%] | +20.9% [+10.0%, +32.2%] | -0.1% [-0.2%, -0.0%] |
| B1 | 1.418 |  |  |  |
| B2 | 1.138 |  |  |  |

**h = 5** (1855 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 0.913 | +35.8% [+25.5%, +59.5%] | +20.4% [+9.9%, +31.2%] |  |
| (iv) flag-restricted scaled mean reversion | 0.913 | +35.8% [+25.5%, +59.5%] | +20.5% [+9.9%, +31.3%] | +0.1% [-0.2%, +0.4%] |
| (v) scaled mean reversion, two-part | 0.914 | +35.7% [+25.4%, +59.5%] | +20.4% [+9.9%, +31.1%] | -0.1% [-0.2%, -0.0%] |
| B1 | 1.422 |  |  |  |
| B2 | 1.148 |  |  |  |

#### upper-tail twCRPS by regime (target day)

**2018-19** (361 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 3.394 | +35.7% [+25.3%, +59.4%] | +11.0% [-1.0%, +24.1%] |  |
| (iv) flag-restricted scaled mean reversion | 3.395 | +35.7% [+25.3%, +59.5%] | +11.0% [-1.0%, +24.0%] | -0.0% [-0.1%, +0.1%] |
| (v) scaled mean reversion, two-part | 3.394 | undefined | undefined | undefined |
| B1 | 5.279 |  |  |  |
| B2 | 3.813 |  |  |  |

**2020** (251 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 0.511 | +31.0% [+17.0%, +55.4%] | +58.1% [-24.3%, +83.9%] |  |
| (iv) flag-restricted scaled mean reversion | 0.510 | +31.1% [+17.3%, +55.8%] | +58.2% [-23.8%, +83.9%] | +0.1% [-0.1%, +0.5%] |
| (v) scaled mean reversion, two-part | 0.511 | undefined | undefined | undefined |
| B1 | 0.740 |  |  |  |
| B2 | 1.219 |  |  |  |

**2021-23** (748 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 0.008 | +12.3% [-63.3%, +44.4%] | -156.2% [-770.4%, -36.0%] |  |
| (iv) flag-restricted scaled mean reversion | 0.008 | undefined | undefined | undefined |
| (v) scaled mean reversion, two-part | 0.009 | -5.1% [-76.8%, +18.7%] | -207.1% [-575.9%, -63.6%] | -19.9% [-75.4%, -1.3%] |
| B1 | 0.009 |  |  |  |
| B2 | 0.003 |  |  |  |

**2024** (250 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 0.183 | undefined | undefined |  |
| (iv) flag-restricted scaled mean reversion | 0.187 | undefined | undefined | undefined |
| (v) scaled mean reversion, two-part | 0.183 | undefined | undefined | undefined |
| B1 | 0.280 |  |  |  |
| B2 | 0.196 |  |  |  |

**2025-26** (249 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 1.084 | +32.3% [+26.1%, +39.4%] | +29.6% [+13.8%, +48.6%] |  |
| (iv) flag-restricted scaled mean reversion | 1.082 | +32.5% [+26.0%, +39.7%] | +29.7% [+14.4%, +48.3%] | +0.2% [-0.5%, +1.0%] |
| (v) scaled mean reversion, two-part | 1.084 | undefined | undefined | undefined |
| B1 | 1.603 |  |  |  |
| B2 | 1.539 |  |  |  |

#### upper-tail twCRPS by window (target day)

**2021-23** (748 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 0.008 | +12.3% [-63.3%, +44.4%] | -156.2% [-770.4%, -36.0%] |  |
| (iv) flag-restricted scaled mean reversion | 0.008 | undefined | undefined | undefined |
| (v) scaled mean reversion, two-part | 0.009 | -5.1% [-76.8%, +18.7%] | -207.1% [-575.9%, -63.6%] | -19.9% [-75.4%, -1.3%] |
| B1 | 0.009 |  |  |  |
| B2 | 0.003 |  |  |  |

**2024-26** (499 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 0.633 | +32.7% [+26.9%, +38.9%] | +27.0% [+11.9%, +48.6%] |  |
| (iv) flag-restricted scaled mean reversion | 0.634 | +32.6% [+26.6%, +39.0%] | +26.8% [+11.9%, +48.5%] | -0.2% [-0.7%, +0.5%] |
| (v) scaled mean reversion, two-part | 0.633 | undefined | undefined | undefined |
| B1 | 0.940 |  |  |  |
| B2 | 0.867 |  |  |  |

**before 2021** (612 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 2.212 | +35.3% [+25.9%, +55.8%] | +19.6% [+3.6%, +35.5%] |  |
| (iv) flag-restricted scaled mean reversion | 2.212 | +35.3% [+25.9%, +55.8%] | +19.6% [+3.6%, +35.5%] | +0.0% [-0.1%, +0.1%] |
| (v) scaled mean reversion, two-part | 2.212 | undefined | undefined | undefined |
| B1 | 3.418 |  |  |  |
| B2 | 2.749 |  |  |  |

#### upper-tail twCRPS by pressure-day type (target day)

**month_end** (150 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 1.017 | undefined | undefined |  |
| (iv) flag-restricted scaled mean reversion | 1.019 | undefined | undefined | undefined |
| (v) scaled mean reversion, two-part | 1.018 | undefined | undefined | undefined |
| B1 | 1.165 |  |  |  |
| B2 | 1.523 |  |  |  |

**ordinary** (1590 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 0.622 | +45.5% [+31.6%, +77.4%] | +18.8% [+7.1%, +29.9%] |  |
| (iv) flag-restricted scaled mean reversion | 0.622 | +45.5% [+31.6%, +77.4%] | +18.8% [+7.1%, +29.9%] | +0.0% [-0.2%, +0.2%] |
| (v) scaled mean reversion, two-part | 0.623 | +45.5% [+31.5%, +77.5%] | +18.7% [+7.0%, +29.8%] | -0.1% [-0.3%, -0.0%] |
| B1 | 1.142 |  |  |  |
| B2 | 0.767 |  |  |  |

**quarter_end** (30 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 4.792 | undefined | undefined |  |
| (iv) flag-restricted scaled mean reversion | 4.796 | undefined | undefined | undefined |
| (v) scaled mean reversion, two-part | 4.792 | undefined | undefined | undefined |
| B1 | 5.377 |  |  |  |
| B2 | 5.541 |  |  |  |

**tax_date** (89 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 4.376 | undefined | undefined |  |
| (iv) flag-restricted scaled mean reversion | 4.379 | undefined | undefined | undefined |
| (v) scaled mean reversion, two-part | 4.377 | undefined | undefined | undefined |
| B1 | 4.662 |  |  |  |
| B2 | 5.660 |  |  |  |

#### upper-tail twCRPS by flag state at the anchor

**off** (1096 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 1.516 | +34.8% [+27.1%, +52.0%] | +20.8% [+7.0%, +33.8%] |  |
| (iv) flag-restricted scaled mean reversion | 1.517 | +34.8% [+27.0%, +52.0%] | +20.8% [+7.0%, +33.8%] | -0.0% [-0.1%, +0.1%] |
| (v) scaled mean reversion, two-part | 1.516 | undefined | undefined | undefined |
| B1 | 2.326 |  |  |  |
| B2 | 1.915 |  |  |  |

**on** (759 days)

| | mean bp | vs B1 | vs B2 | vs scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) |
|---|---|---|---|---|
| scaled mean reversion (#941, mad window 20 floor 0.5; arms (iv) and (v)'s own pool) | 0.000 | +86.7% [+11.4%, +99.4%] | +46.2% [-305.1%, +95.5%] |  |
| (iv) flag-restricted scaled mean reversion | 0.000 | undefined | undefined | undefined |
| (v) scaled mean reversion, two-part | 0.002 | undefined | undefined | undefined |
| B1 | 0.002 |  |  |  |
| B2 | 0.000 |  |  |  |

## Arms (i) and (ii)

1,855 decision days, 2018-07-19 to 2025-12-23 (the last target is 2025-12-31). Mean reversion has no forecast on 75 early days (history), a benchmark is missing on 0. The fit is renewed 89 times (every 21 decision days). Refits whose own flag pool was used (not the whole-lead fallback), by lead 1 to 5: flag on [53, 53, 53, 53, 53], flag off [69, 69, 69, 69, 69].

### Arms (i) and (ii): grid CRPS, pooled (1,855 decision days), skill [90%]

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 1.778 | +22.3% [+15.7%, +39.8%] | +29.4% [+18.7%, +38.7%] |  |
| (i) flag-restricted B1 | 2.260 | +1.2% [+0.5%, +2.2%] | +10.2% [-22.4%, +24.9%] |  |
| (ii) flag-restricted mean reversion | 1.751 | +23.5% [+17.2%, +39.8%] | +30.5% [+19.6%, +39.8%] | +1.5% [+0.5%, +2.7%] |
| B1 | 2.289 |  |  |  |
| B2 | 2.518 |  |  |  |

#### grid CRPS by lead

**h = 1** (1855 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 1.634 | +19.0% [+13.1%, +31.5%] | +34.1% [+17.9%, +44.0%] |  |
| (i) flag-restricted B1 | 1.990 | +1.4% [+0.5%, +2.3%] | +19.8% [-16.7%, +35.4%] |  |
| (ii) flag-restricted mean reversion | 1.608 | +20.3% [+14.7%, +31.6%] | +35.2% [+18.5%, +45.0%] | +1.6% [+0.6%, +2.7%] |
| B1 | 2.017 |  |  |  |
| B2 | 2.480 |  |  |  |

**h = 2** (1855 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 1.737 | +21.6% [+15.2%, +38.2%] | +30.7% [+18.7%, +40.1%] |  |
| (i) flag-restricted B1 | 2.188 | +1.2% [+0.5%, +2.2%] | +12.7% [-22.3%, +28.0%] |  |
| (ii) flag-restricted mean reversion | 1.710 | +22.8% [+16.7%, +38.2%] | +31.8% [+19.5%, +41.2%] | +1.5% [+0.6%, +2.7%] |
| B1 | 2.215 |  |  |  |
| B2 | 2.507 |  |  |  |

**h = 3** (1855 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 1.798 | +23.1% [+16.7%, +39.6%] | +28.7% [+18.1%, +38.0%] |  |
| (i) flag-restricted B1 | 2.305 | +1.4% [+0.6%, +2.4%] | +8.6% [-22.9%, +23.3%] |  |
| (ii) flag-restricted mean reversion | 1.771 | +24.3% [+18.1%, +39.5%] | +29.8% [+18.9%, +39.1%] | +1.5% [+0.4%, +2.7%] |
| B1 | 2.338 |  |  |  |
| B2 | 2.523 |  |  |  |

**h = 4** (1855 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 1.839 | +23.6% [+16.6%, +41.9%] | +27.4% [+17.8%, +36.4%] |  |
| (i) flag-restricted B1 | 2.378 | +1.2% [+0.4%, +2.2%] | +6.1% [-24.3%, +20.6%] |  |
| (ii) flag-restricted mean reversion | 1.810 | +24.8% [+18.0%, +42.0%] | +28.5% [+18.7%, +37.5%] | +1.5% [+0.5%, +2.8%] |
| B1 | 2.408 |  |  |  |
| B2 | 2.534 |  |  |  |

**h = 5** (1855 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 1.885 | +23.5% [+16.2%, +42.5%] | +26.0% [+16.6%, +34.8%] |  |
| (i) flag-restricted B1 | 2.440 | +1.0% [+0.2%, +2.0%] | +4.3% [-25.8%, +18.6%] |  |
| (ii) flag-restricted mean reversion | 1.855 | +24.7% [+17.6%, +42.8%] | +27.2% [+17.6%, +36.1%] | +1.6% [+0.5%, +2.9%] |
| B1 | 2.465 |  |  |  |
| B2 | 2.549 |  |  |  |

#### grid CRPS by regime (target day)

**2018-19** (361 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 3.827 | +33.9% [+24.7%, +52.0%] | +14.2% [-1.7%, +30.1%] |  |
| (i) flag-restricted B1 | 5.784 | +0.1% [-0.0%, +0.2%] | -29.6% [-98.1%, -5.5%] |  |
| (ii) flag-restricted mean reversion | 3.829 | +33.9% [+24.6%, +52.4%] | +14.2% [-1.5%, +30.0%] | -0.1% [-0.3%, +0.2%] |
| B1 | 5.791 |  |  |  |
| B2 | 4.462 |  |  |  |

**2020** (251 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 1.550 | +6.0% [-2.5%, +18.8%] | +44.6% [+20.0%, +69.6%] |  |
| (i) flag-restricted B1 | 1.650 | -0.1% [-0.5%, +0.6%] | +41.0% [+5.8%, +68.7%] |  |
| (ii) flag-restricted mean reversion | 1.554 | +5.7% [-3.0%, +19.0%] | +44.4% [+20.1%, +69.4%] | -0.3% [-0.6%, +0.4%] |
| B1 | 1.648 |  |  |  |
| B2 | 2.797 |  |  |  |

**2021-23** (748 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.716 | -2.6% [-7.4%, +1.7%] | +51.2% [+38.7%, +61.4%] |  |
| (i) flag-restricted B1 | 0.697 | +0.1% [-3.5%, +4.8%] | +52.5% [+38.5%, +64.3%] |  |
| (ii) flag-restricted mean reversion | 0.700 | -0.4% [-7.7%, +5.7%] | +52.2% [+38.7%, +63.5%] | +2.2% [-2.8%, +8.7%] |
| B1 | 0.697 |  |  |  |
| B2 | 1.465 |  |  |  |

**2024** (250 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 1.290 | +20.1% [+12.5%, +29.2%] | +7.5% [-6.4%, +20.5%] |  |
| (i) flag-restricted B1 | 1.556 | +3.6% [+2.0%, +5.7%] | -11.6% [-37.1%, +5.4%] |  |
| (ii) flag-restricted mean reversion | 1.251 | +22.5% [+15.4%, +31.7%] | +10.3% [-2.4%, +22.1%] | +3.0% [+1.5%, +4.8%] |
| B1 | 1.613 |  |  |  |
| B2 | 1.394 |  |  |  |

**2025-26** (249 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 2.772 | +17.4% [+9.5%, +25.1%] | +26.6% [+0.4%, +46.0%] |  |
| (i) flag-restricted B1 | 3.211 | +4.3% [+3.3%, +5.4%] | +15.0% [-7.6%, +36.1%] |  |
| (ii) flag-restricted mean reversion | 2.644 | +21.2% [+14.4%, +28.1%] | +30.0% [+5.8%, +48.1%] | +4.6% [+3.5%, +5.8%] |
| B1 | 3.357 |  |  |  |
| B2 | 3.776 |  |  |  |

#### grid CRPS by window (target day)

**2021-23** (748 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.716 | -2.6% [-7.4%, +1.7%] | +51.2% [+38.7%, +61.4%] |  |
| (i) flag-restricted B1 | 0.697 | +0.1% [-3.5%, +4.8%] | +52.5% [+38.5%, +64.3%] |  |
| (ii) flag-restricted mean reversion | 0.700 | -0.4% [-7.7%, +5.7%] | +52.2% [+38.7%, +63.5%] | +2.2% [-2.8%, +8.7%] |
| B1 | 0.697 |  |  |  |
| B2 | 1.465 |  |  |  |

**2024-26** (499 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 2.029 | +18.3% [+12.7%, +23.7%] | +21.4% [+2.2%, +39.5%] |  |
| (i) flag-restricted B1 | 2.382 | +4.1% [+3.2%, +5.2%] | +7.8% [-11.3%, +27.7%] |  |
| (ii) flag-restricted mean reversion | 1.946 | +21.6% [+16.7%, +26.6%] | +24.6% [+6.8%, +41.8%] | +4.1% [+3.2%, +5.1%] |
| B1 | 2.483 |  |  |  |
| B2 | 2.583 |  |  |  |

**before 2021** (612 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 2.893 | +29.3% [+20.9%, +50.3%] | +23.4% [+5.8%, +39.7%] |  |
| (i) flag-restricted B1 | 4.088 | +0.1% [-0.1%, +0.2%] | -8.2% [-63.5%, +16.7%] |  |
| (ii) flag-restricted mean reversion | 2.896 | +29.2% [+20.8%, +50.5%] | +23.4% [+5.8%, +39.6%] | -0.1% [-0.4%, +0.1%] |
| B1 | 4.092 |  |  |  |
| B2 | 3.779 |  |  |  |

#### grid CRPS by pressure-day type (target day)

**month_end** (150 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 2.100 | +6.6% [+2.5%, +10.8%] | +28.3% [+11.1%, +43.0%] |  |
| (i) flag-restricted B1 | 2.207 | +1.9% [+0.3%, +4.6%] | +24.7% [+4.3%, +43.0%] |  |
| (ii) flag-restricted mean reversion | 2.044 | +9.1% [+4.9%, +13.7%] | +30.2% [+14.2%, +44.9%] | +2.7% [+0.7%, +6.0%] |
| B1 | 2.250 |  |  |  |
| B2 | 2.929 |  |  |  |

**ordinary** (1590 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 1.451 | +28.6% [+17.7%, +59.3%] | +31.0% [+22.5%, +39.2%] |  |
| (i) flag-restricted B1 | 2.006 | +1.3% [+0.4%, +2.3%] | +4.6% [-36.8%, +22.0%] |  |
| (ii) flag-restricted mean reversion | 1.428 | +29.7% [+19.0%, +59.4%] | +32.1% [+23.7%, +40.3%] | +1.6% [+0.3%, +3.0%] |
| B1 | 2.031 |  |  |  |
| B2 | 2.102 |  |  |  |

**quarter_end** (30 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 7.181 | -3.2% [-7.3%, -0.4%] | +5.0% [-53.3%, +45.8%] |  |
| (i) flag-restricted B1 | 6.827 | +1.9% [+0.1%, +6.5%] | +9.7% [-44.9%, +50.6%] |  |
| (ii) flag-restricted mean reversion | 7.022 | -1.0% [-6.0%, +1.1%] | +7.1% [-48.0%, +46.2%] | +2.2% [-0.2%, +8.2%] |
| B1 | 6.956 |  |  |  |
| B2 | 7.560 |  |  |  |

**tax_date** (89 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 5.407 | +1.6% [-5.0%, +7.5%] | +30.1% [-67.3%, +54.3%] |  |
| (i) flag-restricted B1 | 5.471 | +0.5% [-0.5%, +1.3%] | +29.3% [-50.7%, +53.5%] |  |
| (ii) flag-restricted mean reversion | 5.381 | +2.1% [-6.5%, +8.2%] | +30.5% [-64.3%, +54.8%] | +0.5% [-0.4%, +1.3%] |
| B1 | 5.496 |  |  |  |
| B2 | 7.738 |  |  |  |

#### grid CRPS by flag state at the anchor

**off** (1096 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 2.560 | +25.2% [+18.3%, +42.1%] | +25.1% [+12.7%, +36.3%] |  |
| (i) flag-restricted B1 | 3.374 | +1.4% [+0.6%, +2.3%] | +1.2% [-37.8%, +18.3%] |  |
| (ii) flag-restricted mean reversion | 2.525 | +26.2% [+19.7%, +42.4%] | +26.1% [+13.7%, +37.2%] | +1.4% [+0.7%, +2.3%] |
| B1 | 3.421 |  |  |  |
| B2 | 3.416 |  |  |  |

**on** (759 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.649 | +0.7% [-4.2%, +4.9%] | +46.9% [+34.2%, +57.8%] |  |
| (i) flag-restricted B1 | 0.653 | +0.1% [-3.7%, +5.1%] | +46.6% [+31.7%, +60.1%] |  |
| (ii) flag-restricted mean reversion | 0.634 | +3.1% [-5.1%, +9.5%] | +48.2% [+34.1%, +60.4%] | +2.4% [-3.0%, +9.4%] |
| B1 | 0.654 |  |  |  |
| B2 | 1.222 |  |  |  |

### Arms (i) and (ii): upper-tail twCRPS, pooled (1,855 decision days), skill [90%]

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.930 | +32.4% [+24.6%, +48.4%] | +17.8% [+3.2%, +30.9%] |  |
| (i) flag-restricted B1 | 1.364 | +0.8% [+0.3%, +1.5%] | -20.6% [-83.4%, +1.4%] |  |
| (ii) flag-restricted mean reversion | 0.925 | +32.7% [+25.1%, +48.5%] | +18.2% [+3.4%, +31.5%] | +0.5% [+0.0%, +1.3%] |
| B1 | 1.375 |  |  |  |
| B2 | 1.131 |  |  |  |

#### upper-tail twCRPS by lead

**h = 1** (1855 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.916 | +28.6% [+23.1%, +37.6%] | +17.6% [-7.3%, +33.5%] |  |
| (i) flag-restricted B1 | 1.274 | +0.7% [+0.2%, +1.3%] | -14.6% [-72.4%, +9.5%] |  |
| (ii) flag-restricted mean reversion | 0.912 | +29.0% [+23.6%, +37.7%] | +18.0% [-7.2%, +34.0%] | +0.5% [+0.1%, +1.1%] |
| B1 | 1.283 |  |  |  |
| B2 | 1.112 |  |  |  |

**h = 2** (1855 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.927 | +31.5% [+24.6%, +45.4%] | +17.6% [+0.5%, +31.5%] |  |
| (i) flag-restricted B1 | 1.344 | +0.7% [+0.2%, +1.3%] | -19.4% [-82.5%, +3.1%] |  |
| (ii) flag-restricted mean reversion | 0.923 | +31.8% [+25.0%, +45.5%] | +18.0% [+0.7%, +32.0%] | +0.5% [+0.0%, +1.1%] |
| B1 | 1.353 |  |  |  |
| B2 | 1.126 |  |  |  |

**h = 3** (1855 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.930 | +33.4% [+25.7%, +48.3%] | +17.9% [+3.9%, +30.8%] |  |
| (i) flag-restricted B1 | 1.385 | +0.9% [+0.3%, +1.7%] | -22.2% [-80.7%, -1.2%] |  |
| (ii) flag-restricted mean reversion | 0.926 | +33.7% [+26.1%, +48.3%] | +18.3% [+4.1%, +31.3%] | +0.4% [-0.0%, +1.2%] |
| B1 | 1.398 |  |  |  |
| B2 | 1.133 |  |  |  |

**h = 4** (1855 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.930 | +34.4% [+25.1%, +52.9%] | +18.3% [+6.3%, +29.8%] |  |
| (i) flag-restricted B1 | 1.407 | +0.8% [+0.3%, +1.6%] | -23.6% [-83.7%, -2.6%] |  |
| (ii) flag-restricted mean reversion | 0.925 | +34.8% [+25.6%, +53.0%] | +18.7% [+6.5%, +30.5%] | +0.6% [+0.0%, +1.5%] |
| B1 | 1.418 |  |  |  |
| B2 | 1.138 |  |  |  |

**h = 5** (1855 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.945 | +33.6% [+22.7%, +55.8%] | +17.7% [+6.7%, +29.0%] |  |
| (i) flag-restricted B1 | 1.411 | +0.8% [+0.3%, +1.6%] | -22.9% [-88.7%, -1.5%] |  |
| (ii) flag-restricted mean reversion | 0.939 | +34.0% [+23.2%, +55.8%] | +18.2% [+6.7%, +29.5%] | +0.6% [+0.0%, +1.6%] |
| B1 | 1.422 |  |  |  |
| B2 | 1.148 |  |  |  |

#### upper-tail twCRPS by regime (target day)

**2018-19** (361 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 3.452 | +34.6% [+24.3%, +53.4%] | +9.5% [-4.9%, +25.2%] |  |
| (i) flag-restricted B1 | 5.267 | +0.2% [+0.1%, +0.3%] | -38.1% [-112.4%, -12.4%] |  |
| (ii) flag-restricted mean reversion | 3.456 | +34.5% [+24.3%, +53.6%] | +9.4% [-4.6%, +25.0%] | -0.1% [-0.5%, +0.2%] |
| B1 | 5.279 |  |  |  |
| B2 | 3.813 |  |  |  |

**2020** (251 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.587 | +20.7% [+0.2%, +103.0%] | +51.9% [-3.0%, +76.4%] |  |
| (i) flag-restricted B1 | 0.740 | +0.0% [-0.8%, +1.2%] | +39.3% [-91.8%, +75.5%] |  |
| (ii) flag-restricted mean reversion | 0.589 | +20.5% [-0.6%, +104.0%] | +51.7% [-1.6%, +75.9%] | -0.3% [-1.5%, +1.7%] |
| B1 | 0.740 |  |  |  |
| B2 | 1.219 |  |  |  |

**2021-23** (748 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.012 | -39.6% [-75.3%, +32.7%] | -307.7% [-507.7%, -9.1%] |  |
| (i) flag-restricted B1 | 0.008 | undefined | undefined |  |
| (ii) flag-restricted mean reversion | 0.012 | undefined | undefined | undefined |
| B1 | 0.009 |  |  |  |
| B2 | 0.003 |  |  |  |

**2024** (250 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.204 | undefined | undefined |  |
| (i) flag-restricted B1 | 0.274 | undefined | undefined |  |
| (ii) flag-restricted mean reversion | 0.198 | undefined | undefined | undefined |
| B1 | 0.280 |  |  |  |
| B2 | 0.196 |  |  |  |

**2025-26** (249 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 1.155 | +27.9% [+16.5%, +37.9%] | +24.9% [+14.2%, +38.9%] |  |
| (i) flag-restricted B1 | 1.548 | +3.4% [+2.8%, +4.3%] | -0.5% [-27.0%, +30.1%] |  |
| (ii) flag-restricted mean reversion | 1.119 | +30.2% [+19.7%, +39.5%] | +27.3% [+16.6%, +41.2%] | +3.2% [+2.4%, +4.0%] |
| B1 | 1.603 |  |  |  |
| B2 | 1.539 |  |  |  |

#### upper-tail twCRPS by window (target day)

**2021-23** (748 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.012 | -39.6% [-75.3%, +32.7%] | -307.7% [-507.7%, -9.1%] |  |
| (i) flag-restricted B1 | 0.008 | undefined | undefined |  |
| (ii) flag-restricted mean reversion | 0.012 | undefined | undefined | undefined |
| B1 | 0.009 |  |  |  |
| B2 | 0.003 |  |  |  |

**2024-26** (499 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.679 | +27.8% [+18.4%, +35.9%] | +21.6% [+10.1%, +38.8%] |  |
| (i) flag-restricted B1 | 0.910 | +3.3% [+2.7%, +3.9%] | -5.0% [-30.1%, +25.0%] |  |
| (ii) flag-restricted mean reversion | 0.657 | +30.1% [+21.3%, +37.9%] | +24.1% [+12.7%, +41.4%] | +3.2% [+2.4%, +4.0%] |
| B1 | 0.940 |  |  |  |
| B2 | 0.867 |  |  |  |

**before 2021** (612 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 2.277 | +33.4% [+24.2%, +51.4%] | +17.2% [-0.9%, +34.1%] |  |
| (i) flag-restricted B1 | 3.410 | +0.2% [+0.1%, +0.3%] | -24.0% [-93.3%, +1.3%] |  |
| (ii) flag-restricted mean reversion | 2.280 | +33.3% [+24.1%, +51.6%] | +17.1% [-0.8%, +33.8%] | -0.1% [-0.5%, +0.1%] |
| B1 | 3.418 |  |  |  |
| B2 | 2.749 |  |  |  |

#### upper-tail twCRPS by pressure-day type (target day)

**month_end** (150 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 1.104 | undefined | undefined |  |
| (i) flag-restricted B1 | 1.149 | undefined | undefined |  |
| (ii) flag-restricted mean reversion | 1.087 | undefined | undefined | undefined |
| B1 | 1.165 |  |  |  |
| B2 | 1.523 |  |  |  |

**ordinary** (1590 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.628 | +45.0% [+30.5%, +76.0%] | +18.0% [+7.4%, +28.2%] |  |
| (i) flag-restricted B1 | 1.134 | +0.8% [+0.3%, +1.6%] | -47.9% [-171.0%, -9.3%] |  |
| (ii) flag-restricted mean reversion | 0.627 | +45.2% [+30.9%, +76.0%] | +18.3% [+7.4%, +28.5%] | +0.3% [-0.5%, +1.3%] |
| B1 | 1.142 |  |  |  |
| B2 | 0.767 |  |  |  |

**quarter_end** (30 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 5.560 | undefined | undefined |  |
| (i) flag-restricted B1 | 5.294 | undefined | undefined |  |
| (ii) flag-restricted mean reversion | 5.459 | undefined | undefined | undefined |
| B1 | 5.377 |  |  |  |
| B2 | 5.541 |  |  |  |

**tax_date** (89 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 4.612 | undefined | undefined |  |
| (i) flag-restricted B1 | 4.645 | undefined | undefined |  |
| (ii) flag-restricted mean reversion | 4.598 | undefined | undefined | undefined |
| B1 | 4.662 |  |  |  |
| B2 | 5.660 |  |  |  |

#### upper-tail twCRPS by flag state at the anchor

**off** (1096 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 1.572 | +32.4% [+24.5%, +48.6%] | +17.9% [+3.2%, +31.0%] |  |
| (i) flag-restricted B1 | 2.308 | +0.8% [+0.3%, +1.5%] | -20.6% [-83.6%, +1.4%] |  |
| (ii) flag-restricted mean reversion | 1.564 | +32.8% [+25.0%, +48.6%] | +18.3% [+3.4%, +31.5%] | +0.5% [-0.0%, +1.3%] |
| B1 | 2.326 |  |  |  |
| B2 | 1.915 |  |  |  |

**on** (759 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.003 | -60.0% [-84.9%, -22.0%] | -545.6% [-757.2%, -428.6%] |  |
| (i) flag-restricted B1 | 0.001 | +30.6% [+1.0%, +81.4%] | -179.9% [-275.6%, -132.8%] |  |
| (ii) flag-restricted mean reversion | 0.002 | -22.7% [-79.6%, +47.1%] | -394.9% [-489.4%, -315.4%] | +23.3% [+0.8%, +67.0%] |
| B1 | 0.002 |  |  |  |
| B2 | 0.000 |  |  |  |

## Arm (iii)

Not run in this record, by Eleonora's ruling of 22 October 2026 on #966 (comment 6350221714, relayed by the orchestrating session): the Mac run of `gbm_funding`'s walks, which would have scored arm (iii) and the `gbm_funding` reference rows, is skipped. Nothing is claimed about arm (iii) or those rows.

## Variant count

Five arms on one flag (three declared first, (iv) and (v) added on 22 October 2026); no new fit beyond #686's and #941's own refits.

## Not checked, or for Eleonora

- The flag and its three arms were chosen after the author saw 2018-2025 (Lens B's replication is on the same days), so every figure is exploration. Whether any arm joins #634's candidates, and the flag's threshold (1 bp) and windows (60 and 40 rows), are hers.
- The outcome is the panel's `spread_bps`, not the first-published vintage of protocol section 11.
- Lens B's crude replication used its own exact CRPS on B1's change pool; the figures here use the protocol's grid scorer and are not expected to match it.
