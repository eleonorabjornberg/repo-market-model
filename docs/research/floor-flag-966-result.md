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
- (iii) against `gbm_funding`: **not run**: it needs `gbm_funding`'s walks, which go to Eleonora's Mac (#46). The commands are in the pull request.

A kill is a statement about development days; it neither supports nor kills H5 (the declaration's `kill.reading`).

## Arms (i) and (ii)

1,855 decision days, 2018-07-19 to 2025-12-23 (the last target is 2025-12-31). Mean reversion has no forecast on 75 early days (history), a benchmark is missing on 0. The fit is renewed 89 times (every 21 decision days). Refits whose own flag pool was used (not the whole-lead fallback), by lead 1 to 5: flag on [53, 53, 53, 53, 53], flag off [69, 69, 69, 69, 69].

### Arms (i) and (ii): grid CRPS, pooled (1,855 decision days), skill [90%]

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 1.778 | +22.3% [+15.7%, +39.8%] | +29.4% [+18.7%, +38.7%] |  |
| (i) flag-restricted B1 | 2.260 | +1.2% [+0.5%, +2.2%] | +10.2% [-22.4%, +24.9%] |  |
| (ii) flag-restricted mean reversion | 1.751 | +23.5% [+17.2%, +39.8%] | +30.5% [+19.6%, +39.8%] | +1.5% [+0.5%, +2.7%] |

#### grid CRPS by lead

**h = 1** (1855 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 1.634 | +19.0% [+13.1%, +31.5%] | +34.1% [+17.9%, +44.0%] |  |
| (i) flag-restricted B1 | 1.990 | +1.4% [+0.5%, +2.3%] | +19.8% [-16.7%, +35.4%] |  |
| (ii) flag-restricted mean reversion | 1.608 | +20.3% [+14.7%, +31.6%] | +35.2% [+18.5%, +45.0%] | +1.6% [+0.6%, +2.7%] |

**h = 2** (1855 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 1.737 | +21.6% [+15.2%, +38.2%] | +30.7% [+18.7%, +40.1%] |  |
| (i) flag-restricted B1 | 2.188 | +1.2% [+0.5%, +2.2%] | +12.7% [-22.3%, +28.0%] |  |
| (ii) flag-restricted mean reversion | 1.710 | +22.8% [+16.7%, +38.2%] | +31.8% [+19.5%, +41.2%] | +1.5% [+0.6%, +2.7%] |

**h = 3** (1855 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 1.798 | +23.1% [+16.7%, +39.6%] | +28.7% [+18.1%, +38.0%] |  |
| (i) flag-restricted B1 | 2.305 | +1.4% [+0.6%, +2.4%] | +8.6% [-22.9%, +23.3%] |  |
| (ii) flag-restricted mean reversion | 1.771 | +24.3% [+18.1%, +39.5%] | +29.8% [+18.9%, +39.1%] | +1.5% [+0.4%, +2.7%] |

**h = 4** (1855 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 1.839 | +23.6% [+16.6%, +41.9%] | +27.4% [+17.8%, +36.4%] |  |
| (i) flag-restricted B1 | 2.378 | +1.2% [+0.4%, +2.2%] | +6.1% [-24.3%, +20.6%] |  |
| (ii) flag-restricted mean reversion | 1.810 | +24.8% [+18.0%, +42.0%] | +28.5% [+18.7%, +37.5%] | +1.5% [+0.5%, +2.8%] |

**h = 5** (1855 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 1.885 | +23.5% [+16.2%, +42.5%] | +26.0% [+16.6%, +34.8%] |  |
| (i) flag-restricted B1 | 2.440 | +1.0% [+0.2%, +2.0%] | +4.3% [-25.8%, +18.6%] |  |
| (ii) flag-restricted mean reversion | 1.855 | +24.7% [+17.6%, +42.8%] | +27.2% [+17.6%, +36.1%] | +1.6% [+0.5%, +2.9%] |

#### grid CRPS by regime (target day)

**2018-19** (361 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 3.827 | +33.9% [+24.7%, +52.0%] | +14.2% [-1.7%, +30.1%] |  |
| (i) flag-restricted B1 | 5.784 | +0.1% [-0.0%, +0.2%] | -29.6% [-98.1%, -5.5%] |  |
| (ii) flag-restricted mean reversion | 3.829 | +33.9% [+24.6%, +52.4%] | +14.2% [-1.5%, +30.0%] | -0.1% [-0.3%, +0.2%] |

**2020** (251 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 1.550 | +6.0% [-2.5%, +18.8%] | +44.6% [+20.0%, +69.6%] |  |
| (i) flag-restricted B1 | 1.650 | -0.1% [-0.5%, +0.6%] | +41.0% [+5.8%, +68.7%] |  |
| (ii) flag-restricted mean reversion | 1.554 | +5.7% [-3.0%, +19.0%] | +44.4% [+20.1%, +69.4%] | -0.3% [-0.6%, +0.4%] |

**2021-23** (748 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.716 | -2.6% [-7.4%, +1.7%] | +51.2% [+38.7%, +61.4%] |  |
| (i) flag-restricted B1 | 0.697 | +0.1% [-3.5%, +4.8%] | +52.5% [+38.5%, +64.3%] |  |
| (ii) flag-restricted mean reversion | 0.700 | -0.4% [-7.7%, +5.7%] | +52.2% [+38.7%, +63.5%] | +2.2% [-2.8%, +8.7%] |

**2024** (250 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 1.290 | +20.1% [+12.5%, +29.2%] | +7.5% [-6.4%, +20.5%] |  |
| (i) flag-restricted B1 | 1.556 | +3.6% [+2.0%, +5.7%] | -11.6% [-37.1%, +5.4%] |  |
| (ii) flag-restricted mean reversion | 1.251 | +22.5% [+15.4%, +31.7%] | +10.3% [-2.4%, +22.1%] | +3.0% [+1.5%, +4.8%] |

**2025-26** (249 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 2.772 | +17.4% [+9.5%, +25.1%] | +26.6% [+0.4%, +46.0%] |  |
| (i) flag-restricted B1 | 3.211 | +4.3% [+3.3%, +5.4%] | +15.0% [-7.6%, +36.1%] |  |
| (ii) flag-restricted mean reversion | 2.644 | +21.2% [+14.4%, +28.1%] | +30.0% [+5.8%, +48.1%] | +4.6% [+3.5%, +5.8%] |

#### grid CRPS by window (target day)

**2021-23** (748 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.716 | -2.6% [-7.4%, +1.7%] | +51.2% [+38.7%, +61.4%] |  |
| (i) flag-restricted B1 | 0.697 | +0.1% [-3.5%, +4.8%] | +52.5% [+38.5%, +64.3%] |  |
| (ii) flag-restricted mean reversion | 0.700 | -0.4% [-7.7%, +5.7%] | +52.2% [+38.7%, +63.5%] | +2.2% [-2.8%, +8.7%] |

**2024-26** (499 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 2.029 | +18.3% [+12.7%, +23.7%] | +21.4% [+2.2%, +39.5%] |  |
| (i) flag-restricted B1 | 2.382 | +4.1% [+3.2%, +5.2%] | +7.8% [-11.3%, +27.7%] |  |
| (ii) flag-restricted mean reversion | 1.946 | +21.6% [+16.7%, +26.6%] | +24.6% [+6.8%, +41.8%] | +4.1% [+3.2%, +5.1%] |

**before 2021** (612 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 2.893 | +29.3% [+20.9%, +50.3%] | +23.4% [+5.8%, +39.7%] |  |
| (i) flag-restricted B1 | 4.088 | +0.1% [-0.1%, +0.2%] | -8.2% [-63.5%, +16.7%] |  |
| (ii) flag-restricted mean reversion | 2.896 | +29.2% [+20.8%, +50.5%] | +23.4% [+5.8%, +39.6%] | -0.1% [-0.4%, +0.1%] |

#### grid CRPS by pressure-day type (target day)

**month_end** (150 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 2.100 | +6.6% [+2.5%, +10.8%] | +28.3% [+11.1%, +43.0%] |  |
| (i) flag-restricted B1 | 2.207 | +1.9% [+0.3%, +4.6%] | +24.7% [+4.3%, +43.0%] |  |
| (ii) flag-restricted mean reversion | 2.044 | +9.1% [+4.9%, +13.7%] | +30.2% [+14.2%, +44.9%] | +2.7% [+0.7%, +6.0%] |

**ordinary** (1590 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 1.451 | +28.6% [+17.7%, +59.3%] | +31.0% [+22.5%, +39.2%] |  |
| (i) flag-restricted B1 | 2.006 | +1.3% [+0.4%, +2.3%] | +4.6% [-36.8%, +22.0%] |  |
| (ii) flag-restricted mean reversion | 1.428 | +29.7% [+19.0%, +59.4%] | +32.1% [+23.7%, +40.3%] | +1.6% [+0.3%, +3.0%] |

**quarter_end** (30 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 7.181 | -3.2% [-7.3%, -0.4%] | +5.0% [-53.3%, +45.8%] |  |
| (i) flag-restricted B1 | 6.827 | +1.9% [+0.1%, +6.5%] | +9.7% [-44.9%, +50.6%] |  |
| (ii) flag-restricted mean reversion | 7.022 | -1.0% [-6.0%, +1.1%] | +7.1% [-48.0%, +46.2%] | +2.2% [-0.2%, +8.2%] |

**tax_date** (89 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 5.407 | +1.6% [-5.0%, +7.5%] | +30.1% [-67.3%, +54.3%] |  |
| (i) flag-restricted B1 | 5.471 | +0.5% [-0.5%, +1.3%] | +29.3% [-50.7%, +53.5%] |  |
| (ii) flag-restricted mean reversion | 5.381 | +2.1% [-6.5%, +8.2%] | +30.5% [-64.3%, +54.8%] | +0.5% [-0.4%, +1.3%] |

#### grid CRPS by flag state at the anchor

**off** (1096 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 2.560 | +25.2% [+18.3%, +42.1%] | +25.1% [+12.7%, +36.3%] |  |
| (i) flag-restricted B1 | 3.374 | +1.4% [+0.6%, +2.3%] | +1.2% [-37.8%, +18.3%] |  |
| (ii) flag-restricted mean reversion | 2.525 | +26.2% [+19.7%, +42.4%] | +26.1% [+13.7%, +37.2%] | +1.4% [+0.7%, +2.3%] |

**on** (759 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.649 | +0.7% [-4.2%, +4.9%] | +46.9% [+34.2%, +57.8%] |  |
| (i) flag-restricted B1 | 0.653 | +0.1% [-3.7%, +5.1%] | +46.6% [+31.7%, +60.1%] |  |
| (ii) flag-restricted mean reversion | 0.634 | +3.1% [-5.1%, +9.5%] | +48.2% [+34.1%, +60.4%] | +2.4% [-3.0%, +9.4%] |

### Arms (i) and (ii): upper-tail twCRPS, pooled (1,855 decision days), skill [90%]

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.930 | +32.4% [+24.6%, +48.4%] | +17.8% [+3.2%, +30.9%] |  |
| (i) flag-restricted B1 | 1.364 | +0.8% [+0.3%, +1.5%] | -20.6% [-83.4%, +1.4%] |  |
| (ii) flag-restricted mean reversion | 0.925 | +32.7% [+25.1%, +48.5%] | +18.2% [+3.4%, +31.5%] | +0.5% [+0.0%, +1.3%] |

#### upper-tail twCRPS by lead

**h = 1** (1855 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.916 | +28.6% [+23.1%, +37.6%] | +17.6% [-7.3%, +33.5%] |  |
| (i) flag-restricted B1 | 1.274 | +0.7% [+0.2%, +1.3%] | -14.6% [-72.4%, +9.5%] |  |
| (ii) flag-restricted mean reversion | 0.912 | +29.0% [+23.6%, +37.7%] | +18.0% [-7.2%, +34.0%] | +0.5% [+0.1%, +1.1%] |

**h = 2** (1855 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.927 | +31.5% [+24.6%, +45.4%] | +17.6% [+0.5%, +31.5%] |  |
| (i) flag-restricted B1 | 1.344 | +0.7% [+0.2%, +1.3%] | -19.4% [-82.5%, +3.1%] |  |
| (ii) flag-restricted mean reversion | 0.923 | +31.8% [+25.0%, +45.5%] | +18.0% [+0.7%, +32.0%] | +0.5% [+0.0%, +1.1%] |

**h = 3** (1855 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.930 | +33.4% [+25.7%, +48.3%] | +17.9% [+3.9%, +30.8%] |  |
| (i) flag-restricted B1 | 1.385 | +0.9% [+0.3%, +1.7%] | -22.2% [-80.7%, -1.2%] |  |
| (ii) flag-restricted mean reversion | 0.926 | +33.7% [+26.1%, +48.3%] | +18.3% [+4.1%, +31.3%] | +0.4% [-0.0%, +1.2%] |

**h = 4** (1855 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.930 | +34.4% [+25.1%, +52.9%] | +18.3% [+6.3%, +29.8%] |  |
| (i) flag-restricted B1 | 1.407 | +0.8% [+0.3%, +1.6%] | -23.6% [-83.7%, -2.6%] |  |
| (ii) flag-restricted mean reversion | 0.925 | +34.8% [+25.6%, +53.0%] | +18.7% [+6.5%, +30.5%] | +0.6% [+0.0%, +1.5%] |

**h = 5** (1855 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.945 | +33.6% [+22.7%, +55.8%] | +17.7% [+6.7%, +29.0%] |  |
| (i) flag-restricted B1 | 1.411 | +0.8% [+0.3%, +1.6%] | -22.9% [-88.7%, -1.5%] |  |
| (ii) flag-restricted mean reversion | 0.939 | +34.0% [+23.2%, +55.8%] | +18.2% [+6.7%, +29.5%] | +0.6% [+0.0%, +1.6%] |

#### upper-tail twCRPS by regime (target day)

**2018-19** (361 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 3.452 | +34.6% [+24.3%, +53.4%] | +9.5% [-4.9%, +25.2%] |  |
| (i) flag-restricted B1 | 5.267 | +0.2% [+0.1%, +0.3%] | -38.1% [-112.4%, -12.4%] |  |
| (ii) flag-restricted mean reversion | 3.456 | +34.5% [+24.3%, +53.6%] | +9.4% [-4.6%, +25.0%] | -0.1% [-0.5%, +0.2%] |

**2020** (251 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.587 | +20.7% [+0.2%, +103.0%] | +51.9% [-3.0%, +76.4%] |  |
| (i) flag-restricted B1 | 0.740 | +0.0% [-0.8%, +1.2%] | +39.3% [-91.8%, +75.5%] |  |
| (ii) flag-restricted mean reversion | 0.589 | +20.5% [-0.6%, +104.0%] | +51.7% [-1.6%, +75.9%] | -0.3% [-1.5%, +1.7%] |

**2021-23** (748 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.012 | -39.6% [-75.3%, +32.7%] | -307.7% [-507.7%, -9.1%] |  |
| (i) flag-restricted B1 | 0.008 | undefined | undefined |  |
| (ii) flag-restricted mean reversion | 0.012 | undefined | undefined | undefined |

**2024** (250 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.204 | undefined | undefined |  |
| (i) flag-restricted B1 | 0.274 | undefined | undefined |  |
| (ii) flag-restricted mean reversion | 0.198 | undefined | undefined | undefined |

**2025-26** (249 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 1.155 | +27.9% [+16.5%, +37.9%] | +24.9% [+14.2%, +38.9%] |  |
| (i) flag-restricted B1 | 1.548 | +3.4% [+2.8%, +4.3%] | -0.5% [-27.0%, +30.1%] |  |
| (ii) flag-restricted mean reversion | 1.119 | +30.2% [+19.7%, +39.5%] | +27.3% [+16.6%, +41.2%] | +3.2% [+2.4%, +4.0%] |

#### upper-tail twCRPS by window (target day)

**2021-23** (748 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.012 | -39.6% [-75.3%, +32.7%] | -307.7% [-507.7%, -9.1%] |  |
| (i) flag-restricted B1 | 0.008 | undefined | undefined |  |
| (ii) flag-restricted mean reversion | 0.012 | undefined | undefined | undefined |

**2024-26** (499 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.679 | +27.8% [+18.4%, +35.9%] | +21.6% [+10.1%, +38.8%] |  |
| (i) flag-restricted B1 | 0.910 | +3.3% [+2.7%, +3.9%] | -5.0% [-30.1%, +25.0%] |  |
| (ii) flag-restricted mean reversion | 0.657 | +30.1% [+21.3%, +37.9%] | +24.1% [+12.7%, +41.4%] | +3.2% [+2.4%, +4.0%] |

**before 2021** (612 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 2.277 | +33.4% [+24.2%, +51.4%] | +17.2% [-0.9%, +34.1%] |  |
| (i) flag-restricted B1 | 3.410 | +0.2% [+0.1%, +0.3%] | -24.0% [-93.3%, +1.3%] |  |
| (ii) flag-restricted mean reversion | 2.280 | +33.3% [+24.1%, +51.6%] | +17.1% [-0.8%, +33.8%] | -0.1% [-0.5%, +0.1%] |

#### upper-tail twCRPS by pressure-day type (target day)

**month_end** (150 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 1.104 | undefined | undefined |  |
| (i) flag-restricted B1 | 1.149 | undefined | undefined |  |
| (ii) flag-restricted mean reversion | 1.087 | undefined | undefined | undefined |

**ordinary** (1590 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.628 | +45.0% [+30.5%, +76.0%] | +18.0% [+7.4%, +28.2%] |  |
| (i) flag-restricted B1 | 1.134 | +0.8% [+0.3%, +1.6%] | -47.9% [-171.0%, -9.3%] |  |
| (ii) flag-restricted mean reversion | 0.627 | +45.2% [+30.9%, +76.0%] | +18.3% [+7.4%, +28.5%] | +0.3% [-0.5%, +1.3%] |

**quarter_end** (30 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 5.560 | undefined | undefined |  |
| (i) flag-restricted B1 | 5.294 | undefined | undefined |  |
| (ii) flag-restricted mean reversion | 5.459 | undefined | undefined | undefined |

**tax_date** (89 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 4.612 | undefined | undefined |  |
| (i) flag-restricted B1 | 4.645 | undefined | undefined |  |
| (ii) flag-restricted mean reversion | 4.598 | undefined | undefined | undefined |

#### upper-tail twCRPS by flag state at the anchor

**off** (1096 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 1.572 | +32.4% [+24.5%, +48.6%] | +17.9% [+3.2%, +31.0%] |  |
| (i) flag-restricted B1 | 2.308 | +0.8% [+0.3%, +1.5%] | -20.6% [-83.6%, +1.4%] |  |
| (ii) flag-restricted mean reversion | 1.564 | +32.8% [+25.0%, +48.6%] | +18.3% [+3.4%, +31.5%] | +0.5% [-0.0%, +1.3%] |

**on** (759 days)

| | mean bp | vs B1 | vs B2 | vs mean reversion (#686; arm (ii)'s own pool) |
|---|---|---|---|---|
| mean reversion (#686; arm (ii)'s own pool) | 0.003 | -60.0% [-84.9%, -22.0%] | -545.6% [-757.2%, -428.6%] |  |
| (i) flag-restricted B1 | 0.001 | +30.6% [+1.0%, +81.4%] | -179.9% [-275.6%, -132.8%] |  |
| (ii) flag-restricted mean reversion | 0.002 | -22.7% [-79.6%, +47.1%] | -394.9% [-489.4%, -315.4%] | +23.3% [+0.8%, +67.0%] |

## Arm (iii)

Not run in this record (`gbm_funding`'s walks are a long run; they go to Eleonora's Mac and the result returns as a commit on the pull request's branch).

## Variant count

Three arms on one flag; no new fit beyond #686's own refits.

## Not checked, or for Eleonora

- The flag and its three arms were chosen after the author saw 2018-2025 (Lens B's replication is on the same days), so every figure is exploration. Whether any arm joins #634's candidates, and the flag's threshold (1 bp) and windows (60 and 40 rows), are hers.
- The outcome is the panel's `spread_bps`, not the first-published vintage of protocol section 11.
- Lens B's crude replication used its own exact CRPS on B1's change pool; the figures here use the protocol's grid scorer and are not expected to match it.
