Decision days scored: 1868 (2018-06-29 to 2025-12-23); every target day on or before 2025-12-31. Bootstrap: stationary, mean block 10, 10,000 draws, seed 634, one-sided 95%.

Reading of each cell: **skill [one-sided 95% lower bound, upper bound] / lower bound of the mean daily difference** (bp). Skill is mean(d) / mean(benchmark score), d = benchmark − candidate, positive favours the candidate. The protocol would call a candidate better only if the lower bound of the mean difference is above 0 against B1 and B2 and the skill is at least 3%; on development days this is a reading, not a verdict. Tables 1 to 6 are on the protocol's 23-level grid against B1 and B2 (the primary comparisons). B3, the published declaration, is a secondary benchmark scored on its own five levels (0.05, 0.25, 0.5, 0.75, 0.95), never refitted or interpolated to the grid (Eleonora, #660 and #700); every row of a five-level table is read at the same five levels, so B3 and each candidate are paired like for like (Tables 1b, 2b, 3, 5b, 6b).

### Table 1. Primary score: grid CRPS (bp), averaged over h = 1 to 5, pooled

| model | mean | vs B1 | vs B2 |
|---|---|---|---|
| B1 as-of persistence | 2.302 | - | n/a |
| B2 calendar climatology | 2.514 | n/a | - |
| gbm, published features (phase 2) | 1.826 | +20.7% [+11.3%, +40.0%] / +0.236 | +27.4% [+19.8%, +36.6%] / +0.460 |
| (a) published + new inputs | 1.838 | +20.2% [+10.6%, +41.9%] / +0.216 | +26.9% [+19.5%, +36.0%] / +0.448 |
| (b) gbm + new inputs | 1.841 | +20.1% [+10.4%, +41.4%] / +0.216 | +26.8% [+19.3%, +36.0%] / +0.447 |
| (c) two-part + new inputs | 1.835 | +20.3% [+9.0%, +38.0%] / +0.192 | +27.0% [+19.9%, +36.0%] / +0.454 |

### Table 1b. Secondary benchmark B3: CRPS on the five published levels (bp), averaged over h = 1 to 5, pooled

| model (five levels) | mean | vs B3 |
|---|---|---|
| B1 as-of persistence | 2.319 | B3 vs B1: +21.8% [+12.5%, +41.0%] / +0.253 |
| B2 calendar climatology | 2.498 | B3 vs B2: +27.4% [+20.0%, +36.5%] / +0.461 |
| B3 published declaration | 1.814 | - |
| gbm, published features (phase 2) | 1.830 | -0.9% [-2.4%, +0.8%] / -0.052 |
| (a) published + new inputs | 1.829 | -0.9% [-2.3%, +0.6%] / -0.040 |
| (b) gbm + new inputs | 1.850 | -2.0% [-4.1%, +0.2%] / -0.080 |
| (c) two-part + new inputs | 1.829 | -0.8% [-5.2%, +3.6%] / -0.097 |

### Table 2. Key secondary: upper-tail twCRPS (weight 1{y > 0 bp}), pooled

| model | mean | vs B1 | vs B2 |
|---|---|---|---|
| B1 as-of persistence | 1.379 | - | n/a |
| B2 calendar climatology | 1.126 | n/a | - |
| gbm, published features (phase 2) | 0.947 | +31.3% [+18.8%, +50.4%] / +0.196 | +15.9% [+7.1%, +29.0%] / +0.072 |
| (a) published + new inputs | 0.933 | +32.3% [+19.8%, +54.4%] / +0.200 | +17.1% [+9.0%, +29.1%] / +0.087 |
| (b) gbm + new inputs | 0.944 | +31.6% [+19.0%, +52.4%] / +0.195 | +16.2% [+7.9%, +28.5%] / +0.079 |
| (c) two-part + new inputs | 0.886 | +35.7% [+23.4%, +51.6%] / +0.235 | +21.3% [+13.1%, +34.0%] / +0.136 |

### Table 2b. Key secondary against B3: upper-tail twCRPS on the five published levels, pooled

| model (five levels) | mean | vs B3 |
|---|---|---|
| B1 as-of persistence | 1.388 | B3 vs B1: +32.5% [+19.8%, +52.8%] / +0.202 |
| B2 calendar climatology | 1.130 | B3 vs B2: +17.1% [+8.7%, +29.7%] / +0.087 |
| B3 published declaration | 0.936 | - |
| gbm, published features (phase 2) | 0.949 | -1.3% [-3.0%, +0.5%] / -0.039 |
| (a) published + new inputs | 0.930 | +0.7% [-1.2%, +2.4%] / -0.009 |
| (b) gbm + new inputs | 0.948 | -1.2% [-3.6%, +1.1%] / -0.037 |
| (c) two-part + new inputs | 0.887 | +5.3% [+1.2%, +10.5%] / +0.008 |

### Table 3. Ablation: each variant against the same model without the new inputs (primary score)

| pair (parent → variant) | skill [bounds] / lower bound of mean(d) |
|---|---|
| B3 published declaration → (a) published + new inputs (five levels) | -0.9% [-2.3%, +0.6%] / -0.040 |
| gbm, published features (phase 2) → (b) gbm + new inputs | -0.8% [-2.2%, +0.6%] / -0.038 |
| (b) gbm + new inputs → (c) two-part + new inputs | +0.3% [-4.4%, +4.9%] / -0.083 |

### Table 4. Grid CRPS by lead (bp)

| model | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|
| B1 as-of persistence | 2.029 | 2.228 | 2.353 | 2.424 | 2.478 |
| B2 calendar climatology | 2.480 | 2.503 | 2.518 | 2.528 | 2.544 |
| gbm, published features (phase 2) | 1.636 | 1.768 | 1.859 | 1.905 | 1.962 |
| (a) published + new inputs | 1.642 | 1.783 | 1.866 | 1.917 | 1.982 |
| (b) gbm + new inputs | 1.632 | 1.777 | 1.874 | 1.927 | 1.993 |
| (c) two-part + new inputs | 1.633 | 1.775 | 1.846 | 1.910 | 2.013 |

Five published levels (B3 on its own levels), CRPS by lead (bp):

| model | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|
| B1 as-of persistence | 2.056 | 2.245 | 2.363 | 2.436 | 2.496 |
| B2 calendar climatology | 2.463 | 2.486 | 2.501 | 2.510 | 2.529 |
| B3 published declaration | 1.641 | 1.756 | 1.843 | 1.887 | 1.942 |
| gbm, published features (phase 2) | 1.641 | 1.770 | 1.864 | 1.909 | 1.967 |
| (a) published + new inputs | 1.632 | 1.774 | 1.855 | 1.910 | 1.974 |
| (b) gbm + new inputs | 1.640 | 1.783 | 1.888 | 1.936 | 2.002 |
| (c) two-part + new inputs | 1.622 | 1.766 | 1.842 | 1.904 | 2.009 |

### Table 5. By regime of the decision day (primary score)

The regimes were drawn after the fact; no split is a pass requirement (protocol section 7).

**2018-19** (375 decision days)

| model | mean | vs B1 | vs B2 |
|---|---|---|---|
| B1 as-of persistence | 5.727 | - | n/a |
| B2 calendar climatology | 4.364 | n/a | - |
| gbm, published features (phase 2) | 3.993 | +30.3% [+13.6%, +62.6%] / +0.621 | +8.5% [+1.1%, +20.0%] / +0.009 |
| (a) published + new inputs | 3.977 | +30.6% [+13.8%, +68.8%] / +0.596 | +8.9% [+1.0%, +20.0%] / -0.004 |
| (b) gbm + new inputs | 3.926 | +31.4% [+15.1%, +65.5%] / +0.661 | +10.0% [+2.6%, +21.7%] / +0.068 |
| (c) two-part + new inputs | 3.897 | +32.0% [+14.2%, +60.3%] / +0.647 | +10.7% [+4.7%, +22.6%] / +0.183 |

| model (five levels) | mean | vs B3 |
|---|---|---|
| B1 as-of persistence | 5.753 | B3 vs B1: +30.3% [+12.9%, +67.1%] / +0.579 |
| B2 calendar climatology | 4.337 | B3 vs B2: +7.5% [-0.0%, +18.1%] / -0.034 |
| B3 published declaration | 4.012 | - |
| gbm, published features (phase 2) | 3.994 | +0.5% [-1.4%, +3.1%] / -0.082 |
| (a) published + new inputs | 3.951 | +1.5% [-0.4%, +3.4%] / -0.019 |
| (b) gbm + new inputs | 3.929 | +2.1% [-0.1%, +4.9%] / -0.014 |
| (c) two-part + new inputs | 3.904 | +2.7% [-3.0%, +9.0%] / -0.168 |

**2020** (251 decision days)

| model | mean | vs B1 | vs B2 |
|---|---|---|---|
| B1 as-of persistence | 1.644 | - | n/a |
| B2 calendar climatology | 2.786 | n/a | - |
| gbm, published features (phase 2) | 1.417 | +13.8% [+1.7%, +23.3%] / +0.037 | +49.1% [+32.5%, +67.6%] / +0.591 |
| (a) published + new inputs | 1.443 | +12.2% [-0.6%, +23.6%] / +0.021 | +48.2% [+32.6%, +65.8%] / +0.574 |
| (b) gbm + new inputs | 1.457 | +11.4% [-1.6%, +20.7%] / -0.034 | +47.7% [+30.8%, +67.4%] / +0.557 |
| (c) two-part + new inputs | 1.670 | -1.6% [-25.5%, +21.5%] / -0.369 | +40.1% [+23.5%, +59.2%] / +0.363 |

| model (five levels) | mean | vs B3 |
|---|---|---|
| B1 as-of persistence | 1.664 | B3 vs B1: +13.6% [-1.6%, +30.6%] / +0.020 |
| B2 calendar climatology | 2.821 | B3 vs B2: +49.1% [+34.4%, +65.3%] / +0.625 |
| B3 published declaration | 1.437 | - |
| gbm, published features (phase 2) | 1.440 | -0.2% [-6.7%, +10.5%] / -0.255 |
| (a) published + new inputs | 1.447 | -0.7% [-4.4%, +3.8%] / -0.106 |
| (b) gbm + new inputs | 1.471 | -2.4% [-10.3%, +9.7%] / -0.347 |
| (c) two-part + new inputs | 1.666 | -15.9% [-29.7%, -4.0%] / -0.518 |

**2021-23** (748 decision days)

| model | mean | vs B1 | vs B2 |
|---|---|---|---|
| B1 as-of persistence | 0.711 | - | n/a |
| B2 calendar climatology | 1.481 | n/a | - |
| gbm, published features (phase 2) | 0.717 | -0.9% [-12.6%, +9.9%] / -0.121 | +51.6% [+40.3%, +65.8%] / +0.492 |
| (a) published + new inputs | 0.784 | -10.3% [-22.3%, +0.8%] / -0.198 | +47.1% [+34.8%, +62.5%] / +0.422 |
| (b) gbm + new inputs | 0.744 | -4.7% [-17.1%, +6.7%] / -0.161 | +49.7% [+37.5%, +64.8%] / +0.459 |
| (c) two-part + new inputs | 0.927 | -30.4% [-48.4%, -13.6%] / -0.412 | +37.4% [+23.7%, +55.0%] / +0.280 |

| model (five levels) | mean | vs B3 |
|---|---|---|
| B1 as-of persistence | 0.730 | B3 vs B1: -1.4% [-12.6%, +8.8%] / -0.116 |
| B2 calendar climatology | 1.465 | B3 vs B2: +49.4% [+38.2%, +63.8%] / +0.461 |
| B3 published declaration | 0.741 | - |
| gbm, published features (phase 2) | 0.719 | +3.0% [-0.0%, +7.3%] / -0.003 |
| (a) published + new inputs | 0.777 | -4.8% [-8.1%, -1.4%] / -0.066 |
| (b) gbm + new inputs | 0.751 | -1.3% [-5.2%, +3.3%] / -0.051 |
| (c) two-part + new inputs | 0.914 | -23.3% [-33.7%, -13.2%] / -0.275 |

**2024** (250 decision days)

| model | mean | vs B1 | vs B2 |
|---|---|---|---|
| B1 as-of persistence | 1.683 | - | n/a |
| B2 calendar climatology | 1.378 | n/a | - |
| gbm, published features (phase 2) | 1.411 | +16.2% [+9.3%, +23.3%] / +0.129 | -2.4% [-16.1%, +12.9%] / -0.288 |
| (a) published + new inputs | 1.398 | +16.9% [+10.7%, +23.1%] / +0.129 | -1.5% [-15.8%, +12.1%] / -0.294 |
| (b) gbm + new inputs | 1.435 | +14.7% [+8.0%, +21.6%] / +0.107 | -4.1% [-18.4%, +9.9%] / -0.339 |
| (c) two-part + new inputs | 1.265 | +24.8% [+11.9%, +39.2%] / +0.147 | +8.2% [-2.2%, +17.6%] / -0.062 |

| model (five levels) | mean | vs B3 |
|---|---|---|
| B1 as-of persistence | 1.699 | B3 vs B1: +20.2% [+12.6%, +28.2%] / +0.162 |
| B2 calendar climatology | 1.357 | B3 vs B2: +0.0% [-12.1%, +12.6%] / -0.207 |
| B3 published declaration | 1.356 | - |
| gbm, published features (phase 2) | 1.419 | -4.6% [-7.4%, -0.9%] / -0.198 |
| (a) published + new inputs | 1.392 | -2.6% [-5.4%, -0.5%] / -0.114 |
| (b) gbm + new inputs | 1.449 | -6.8% [-10.3%, -3.3%] / -0.243 |
| (c) two-part + new inputs | 1.265 | +6.7% [-1.9%, +15.4%] / -0.022 |

**2025-26** (244 decision days)

| model | mean | vs B1 | vs B2 |
|---|---|---|---|
| B1 as-of persistence | 3.231 | - | n/a |
| B2 calendar climatology | 3.724 | n/a | - |
| gbm, published features (phase 2) | 2.742 | +15.1% [+7.5%, +25.0%] / +0.232 | +26.4% [+5.5%, +46.3%] / +0.000 |
| (a) published + new inputs | 2.637 | +18.4% [+11.7%, +26.8%] / +0.353 | +29.2% [+10.6%, +47.2%] / +0.142 |
| (b) gbm + new inputs | 2.807 | +13.1% [+5.8%, +22.9%] / +0.191 | +24.6% [+3.9%, +44.7%] / -0.036 |
| (c) two-part + new inputs | 2.207 | +31.7% [+23.7%, +40.5%] / +0.671 | +40.7% [+24.5%, +55.2%] / +0.486 |

| model (five levels) | mean | vs B3 |
|---|---|---|
| B1 as-of persistence | 3.223 | B3 vs B1: +19.9% [+12.5%, +28.8%] / +0.367 |
| B2 calendar climatology | 3.672 | B3 vs B2: +29.7% [+10.3%, +48.2%] / +0.126 |
| B3 published declaration | 2.581 | - |
| gbm, published features (phase 2) | 2.734 | -5.9% [-9.0%, -3.0%] / -0.244 |
| (a) published + new inputs | 2.636 | -2.1% [-3.8%, -0.6%] / -0.116 |
| (b) gbm + new inputs | 2.826 | -9.5% [-12.8%, -6.1%] / -0.357 |
| (c) two-part + new inputs | 2.190 | +15.1% [+9.6%, +21.8%] / +0.231 |

### Table 6. By pressure-day type of the target day (primary score)

**month_end** (507 decision days with such a target, 747 target cells)

| model | mean | vs B1 | vs B2 |
|---|---|---|---|
| B1 as-of persistence | 2.220 | - | n/a |
| B2 calendar climatology | 2.875 | n/a | - |
| gbm, published features (phase 2) | 2.150 | +3.2% [-3.6%, +11.1%] / -0.091 | +25.2% [+11.1%, +40.3%] / +0.246 |
| (a) published + new inputs | 2.064 | +7.0% [+0.6%, +12.9%] / +0.007 | +28.2% [+15.8%, +41.5%] / +0.346 |
| (b) gbm + new inputs | 2.170 | +2.3% [-4.3%, +9.0%] / -0.100 | +24.5% [+11.0%, +38.7%] / +0.229 |
| (c) two-part + new inputs | 1.910 | +14.0% [+2.3%, +24.6%] / +0.009 | +33.6% [+24.7%, +44.3%] / +0.561 |

| model (five levels) | mean | vs B3 |
|---|---|---|
| B1 as-of persistence | 2.254 | B3 vs B1: +8.4% [+2.0%, +14.7%] / +0.032 |
| B2 calendar climatology | 2.836 | B3 vs B2: +27.2% [+14.3%, +41.6%] / +0.321 |
| B3 published declaration | 2.066 | - |
| gbm, published features (phase 2) | 2.162 | -4.7% [-7.5%, -1.2%] / -0.206 |
| (a) published + new inputs | 2.090 | -1.2% [-4.6%, +4.4%] / -0.089 |
| (b) gbm + new inputs | 2.173 | -5.2% [-9.6%, +0.6%] / -0.229 |
| (c) two-part + new inputs | 1.884 | +8.8% [-0.6%, +17.4%] / -0.024 |

**ordinary** (1868 decision days with such a target, 8002 target cells)

| model | mean | vs B1 | vs B2 |
|---|---|---|---|
| B1 as-of persistence | 1.995 | - | n/a |
| B2 calendar climatology | 2.151 | n/a | - |
| gbm, published features (phase 2) | 1.496 | +25.0% [+13.3%, +55.4%] / +0.245 | +30.5% [+23.5%, +38.5%] / +0.447 |
| (a) published + new inputs | 1.520 | +23.8% [+12.0%, +56.0%] / +0.221 | +29.4% [+22.2%, +37.6%] / +0.418 |
| (b) gbm + new inputs | 1.502 | +24.7% [+12.6%, +57.3%] / +0.234 | +30.2% [+23.2%, +38.2%] / +0.438 |
| (c) two-part + new inputs | 1.567 | +21.4% [+7.4%, +47.8%] / +0.151 | +27.2% [+20.1%, +35.8%] / +0.374 |

| model (five levels) | mean | vs B3 |
|---|---|---|
| B1 as-of persistence | 2.005 | B3 vs B1: +25.2% [+13.6%, +54.7%] / +0.250 |
| B2 calendar climatology | 2.132 | B3 vs B2: +29.6% [+22.8%, +37.5%] / +0.426 |
| B3 published declaration | 1.500 | - |
| gbm, published features (phase 2) | 1.499 | +0.1% [-1.8%, +2.3%] / -0.033 |
| (a) published + new inputs | 1.508 | -0.5% [-2.0%, +1.1%] / -0.032 |
| (b) gbm + new inputs | 1.509 | -0.6% [-3.1%, +2.3%] / -0.054 |
| (c) two-part + new inputs | 1.562 | -4.1% [-9.1%, +1.3%] / -0.142 |

**quarter_end** (146 decision days with such a target, 146 target cells)

| model | mean | vs B1 | vs B2 |
|---|---|---|---|
| B1 as-of persistence | 6.745 | - | n/a |
| B2 calendar climatology | 7.382 | n/a | - |
| gbm, published features (phase 2) | 7.639 | -13.3% [-21.1%, -6.1%] / -2.272 | -3.5% [-38.7%, +43.9%] / -3.945 |
| (a) published + new inputs | 7.002 | -3.8% [-16.2%, +2.5%] / -0.578 | +5.1% [-26.6%, +50.9%] / -2.366 |
| (b) gbm + new inputs | 7.645 | -13.3% [-23.2%, -7.5%] / -1.626 | -3.6% [-38.3%, +42.9%] / -3.779 |
| (c) two-part + new inputs | 6.124 | +9.2% [-11.3%, +23.4%] / -0.825 | +17.0% [-5.5%, +48.6%] / -0.611 |

| model (five levels) | mean | vs B3 |
|---|---|---|
| B1 as-of persistence | 6.919 | B3 vs B1: -0.7% [-9.4%, +3.5%] / -0.392 |
| B2 calendar climatology | 7.306 | B3 vs B2: +4.6% [-26.4%, +49.6%] / -2.396 |
| B3 published declaration | 6.968 | - |
| gbm, published features (phase 2) | 7.664 | -10.0% [-15.1%, -4.4%] / -2.832 |
| (a) published + new inputs | 7.001 | -0.5% [-5.2%, +4.6%] / -0.216 |
| (b) gbm + new inputs | 7.781 | -11.7% [-15.9%, -7.1%] / -2.295 |
| (c) two-part + new inputs | 6.172 | +11.4% [-2.6%, +28.0%] / -0.387 |

**tax_date** (214 decision days with such a target, 445 target cells)

| model | mean | vs B1 | vs B2 |
|---|---|---|---|
| B1 as-of persistence | 4.919 | - | n/a |
| B2 calendar climatology | 7.162 | n/a | - |
| gbm, published features (phase 2) | 5.196 | -5.6% [-18.1%, -0.7%] / -0.927 | +27.5% [+13.6%, +58.3%] / +1.111 |
| (a) published + new inputs | 5.245 | -6.6% [-25.1%, +1.0%] / -0.880 | +26.8% [+14.2%, +54.5%] / +1.138 |
| (b) gbm + new inputs | 5.285 | -7.4% [-25.9%, +0.4%] / -0.999 | +26.2% [+13.1%, +56.0%] / +1.018 |
| (c) two-part + new inputs | 5.215 | -6.0% [-30.2%, +2.8%] / -0.993 | +27.2% [+14.8%, +53.9%] / +1.116 |

| model (five levels) | mean | vs B3 |
|---|---|---|
| B1 as-of persistence | 4.975 | B3 vs B1: -4.0% [-16.2%, +0.8%] / -0.741 |
| B2 calendar climatology | 7.261 | B3 vs B2: +28.8% [+14.8%, +59.0%] / +1.167 |
| B3 published declaration | 5.172 | - |
| gbm, published features (phase 2) | 5.193 | -0.4% [-3.2%, +2.2%] / -0.201 |
| (a) published + new inputs | 5.246 | -1.4% [-8.9%, +4.4%] / -0.222 |
| (b) gbm + new inputs | 5.296 | -2.4% [-12.4%, +3.1%] / -0.501 |
| (c) two-part + new inputs | 5.198 | -0.5% [-9.9%, +3.8%] / -0.218 |

### Table 7. Pinball loss at the fixed levels and MAE of the median (pooled, bp), paired against B1 and B3

| measure | B1 as-of persistence | B2 calendar climatology | B3 published declaration | gbm, published features (phase 2) | (a) published + new inputs | (b) gbm + new inputs | (c) two-part + new inputs |
|---|---|---|---|---|---|---|---|
| mae_median | 2.888 | 3.659 | 2.430 | 2.407 | 2.459 | 2.419 | 2.541 |
| pinball_0.05 | 0.821 | 0.464 | 0.343 | 0.363 | 0.351 | 0.372 | 0.352 |
| pinball_0.25 | 1.354 | 1.306 | 0.887 | 0.863 | 0.897 | 0.877 | 0.907 |
| pinball_0.5 | 1.444 | 1.829 | 1.215 | 1.204 | 1.229 | 1.209 | 1.270 |
| pinball_0.75 | 1.361 | 1.701 | 1.288 | 1.274 | 1.295 | 1.275 | 1.265 |
| pinball_0.95 | 0.818 | 0.944 | 0.801 | 0.873 | 0.801 | 0.892 | 0.778 |

Paired skill against B1 / B3 (one-sided 95% lower bound of the mean difference):

| measure | candidate | vs B1 | vs B3 |
|---|---|---|---|
| mae_median | gbm, published features (phase 2) | +16.7% [+7.9%, +33.6%] / +0.214 | +0.9% [+0.1%, +2.4%] / +0.004 |
| mae_median | (a) published + new inputs | +14.9% [+5.3%, +33.1%] / +0.152 | -1.2% [-2.8%, +0.3%] / -0.066 |
| mae_median | (b) gbm + new inputs | +16.3% [+7.2%, +34.1%] / +0.195 | +0.5% [-1.0%, +2.0%] / -0.024 |
| mae_median | (c) two-part + new inputs | +12.0% [+0.1%, +29.2%] / +0.031 | -4.6% [-10.0%, +0.9%] / -0.242 |
| pinball_0.05 | gbm, published features (phase 2) | +55.8% [+35.0%, +90.0%] / +0.225 | -5.6% [-20.3%, +8.6%] / -0.082 |
| pinball_0.05 | (a) published + new inputs | +57.2% [+40.1%, +87.9%] / +0.249 | -2.3% [-6.1%, +1.7%] / -0.023 |
| pinball_0.05 | (b) gbm + new inputs | +54.7% [+33.5%, +90.8%] / +0.217 | -8.3% [-23.9%, +6.5%] / -0.094 |
| pinball_0.05 | (c) two-part + new inputs | +57.2% [+36.4%, +85.9%] / +0.232 | -2.4% [-17.7%, +12.1%] / -0.078 |
| pinball_0.25 | gbm, published features (phase 2) | +36.3% [+24.9%, +59.3%] / +0.287 | +2.7% [+1.7%, +4.1%] / +0.016 |
| pinball_0.25 | (a) published + new inputs | +33.7% [+21.4%, +57.8%] / +0.250 | -1.2% [-3.2%, +0.9%] / -0.031 |
| pinball_0.25 | (b) gbm + new inputs | +35.2% [+23.5%, +58.5%] / +0.272 | +1.1% [-0.8%, +3.0%] / -0.009 |
| pinball_0.25 | (c) two-part + new inputs | +33.0% [+19.9%, +53.5%] / +0.232 | -2.2% [-7.2%, +3.0%] / -0.067 |
| pinball_0.5 | gbm, published features (phase 2) | +16.7% [+7.9%, +33.6%] / +0.107 | +0.9% [+0.1%, +2.4%] / +0.002 |
| pinball_0.5 | (a) published + new inputs | +14.9% [+5.3%, +33.1%] / +0.076 | -1.2% [-2.8%, +0.3%] / -0.033 |
| pinball_0.5 | (b) gbm + new inputs | +16.3% [+7.2%, +34.1%] / +0.097 | +0.5% [-1.0%, +2.0%] / -0.012 |
| pinball_0.5 | (c) two-part + new inputs | +12.0% [+0.1%, +29.2%] / +0.015 | -4.6% [-10.0%, +0.9%] / -0.121 |
| pinball_0.75 | gbm, published features (phase 2) | +6.4% [+1.1%, +14.0%] / +0.020 | +1.1% [+0.5%, +1.8%] / +0.007 |
| pinball_0.75 | (a) published + new inputs | +4.8% [-1.1%, +14.2%] / -0.005 | -0.5% [-2.5%, +1.3%] / -0.029 |
| pinball_0.75 | (b) gbm + new inputs | +6.3% [+0.8%, +15.2%] / +0.017 | +1.0% [-0.7%, +2.6%] / -0.008 |
| pinball_0.75 | (c) two-part + new inputs | +7.0% [-0.7%, +15.5%] / -0.003 | +1.8% [-3.2%, +6.4%] / -0.045 |
| pinball_0.95 | gbm, published features (phase 2) | -6.6% [-14.9%, +0.2%] / -0.130 | -8.9% [-15.5%, -3.0%] / -0.140 |
| pinball_0.95 | (a) published + new inputs | +2.2% [-3.8%, +7.8%] / -0.027 | +0.1% [-2.7%, +2.8%] / -0.020 |
| pinball_0.95 | (b) gbm + new inputs | -9.0% [-17.4%, -1.1%] / -0.144 | -11.3% [-19.4%, -4.2%] / -0.159 |
| pinball_0.95 | (c) two-part + new inputs | +4.9% [-1.5%, +11.3%] / -0.015 | +2.9% [-1.7%, +8.2%] / -0.017 |

### Table 8. Central coverage (share of target cells inside the interval), pooled

| level | nominal | B1 as-of persistence | B2 calendar climatology | B3 published declaration | gbm, published features (phase 2) | (a) published + new inputs | (b) gbm + new inputs | (c) two-part + new inputs |
|---|---|---|---|---|---|---|---|---|
| 50% | 0.50 | 0.530 | 0.466 | 0.305 | 0.307 | 0.298 | 0.336 | 0.380 |
| 90% | 0.90 | 0.842 | 0.823 | 0.886 | 0.695 | 0.888 | 0.665 | 0.749 |

### Table 9. Upper tail: Brier score of P(spread > threshold), read off each distribution, against the models fitted at the threshold and lead

B3 is not in this table: a probability of exceeding a threshold is not a statistic of its five levels, and reading one would place the five levels on a continuous law, which the ruling excludes.

**> +0 bp** (1868 decision days, 1586 event cells)

| model | mean Brier | vs persistence-logistic | vs calendar climatology |
|---|---|---|---|
| B1 as-of persistence | 0.06930 | n/a | n/a |
| B2 calendar climatology | 0.11425 | n/a | n/a |
| (a) published + new inputs | 0.06121 | +21.7% [+14.0%, +30.9%] / +0.009 | +58.4% [+50.1%, +67.5%] / +0.065 |
| (b) gbm + new inputs | 0.06141 | +21.4% [+12.3%, +32.2%] / +0.008 | +58.3% [+48.7%, +68.6%] / +0.064 |
| (c) two-part + new inputs | 0.06240 | +20.2% [+13.8%, +26.9%] / +0.010 | +57.6% [+49.9%, +66.5%] / +0.067 |
| calendar climatology | 0.14726 | n/a | - |
| gbm, published features (phase 2) | 0.06245 | +20.1% [+10.3%, +31.0%] / +0.007 | +57.6% [+47.7%, +68.1%] / +0.063 |
| persistence-logistic | 0.07817 | - | n/a |

**> +10 bp** (1868 decision days, 293 event cells)

| model | mean Brier | vs persistence-logistic | vs calendar climatology |
|---|---|---|---|
| B1 as-of persistence | 0.04291 | n/a | n/a |
| B2 calendar climatology | 0.03037 | n/a | n/a |
| (a) published + new inputs | 0.02896 | +2.7% [-5.2%, +10.0%] / -0.001 | +8.6% [+0.2%, +16.9%] / +0.000 |
| (b) gbm + new inputs | 0.02917 | +2.0% [-3.4%, +7.3%] / -0.001 | +7.9% [+0.4%, +15.7%] / +0.000 |
| (c) two-part + new inputs | 0.02593 | +12.9% [+7.9%, +17.6%] / +0.002 | +18.2% [+11.6%, +25.2%] / +0.003 |
| calendar climatology | 0.03169 | n/a | - |
| gbm, published features (phase 2) | 0.02907 | +2.3% [-2.2%, +6.5%] / -0.000 | +8.3% [+1.0%, +15.8%] / +0.000 |
| persistence-logistic | 0.02976 | - | n/a |

**> +2 bp** (1868 decision days, 1143 event cells)

| model | mean Brier | vs persistence-logistic | vs calendar climatology |
|---|---|---|---|
| B1 as-of persistence | 0.06856 | n/a | n/a |
| B2 calendar climatology | 0.09538 | n/a | n/a |
| (a) published + new inputs | 0.06041 | +20.5% [+12.6%, +30.1%] / +0.008 | +46.0% [+37.8%, +54.8%] / +0.037 |
| (b) gbm + new inputs | 0.06220 | +18.1% [+9.7%, +28.1%] / +0.007 | +44.4% [+35.6%, +53.9%] / +0.036 |
| (c) two-part + new inputs | 0.06040 | +20.5% [+15.5%, +26.2%] / +0.011 | +46.0% [+39.0%, +54.3%] / +0.040 |
| calendar climatology | 0.11186 | n/a | - |
| gbm, published features (phase 2) | 0.06379 | +16.0% [+7.7%, +26.3%] / +0.005 | +43.0% [+33.7%, +53.1%] / +0.034 |
| persistence-logistic | 0.07596 | - | n/a |

**> +5 bp** (1868 decision days, 681 event cells)

| model | mean Brier | vs persistence-logistic | vs calendar climatology |
|---|---|---|---|
| B1 as-of persistence | 0.06420 | n/a | n/a |
| B2 calendar climatology | 0.06453 | n/a | n/a |
| (a) published + new inputs | 0.05194 | +13.3% [+6.3%, +21.5%] / +0.003 | +25.9% [+17.6%, +35.0%] / +0.011 |
| (b) gbm + new inputs | 0.05470 | +8.7% [+1.3%, +18.2%] / +0.001 | +22.0% [+12.9%, +32.2%] / +0.008 |
| (c) two-part + new inputs | 0.04856 | +19.0% [+14.4%, +23.7%] / +0.008 | +30.8% [+25.0%, +37.8%] / +0.016 |
| calendar climatology | 0.07013 | n/a | - |
| gbm, published features (phase 2) | 0.05378 | +10.3% [+3.9%, +17.7%] / +0.002 | +23.3% [+15.0%, +32.3%] / +0.010 |
| persistence-logistic | 0.05993 | - | n/a |

### Missing forecasts (protocol section 11)

- B3 published declaration: 0 decision days with at least one lead scored as B1's (0.00%).
- (a) published + new inputs: 0 decision days with at least one lead scored as B1's (0.00%).
- (b) gbm + new inputs: 0 decision days with at least one lead scored as B1's (0.00%).
- (c) two-part + new inputs: 2 decision days with at least one lead scored as B1's (0.11%).
- gbm, published features (phase 2): 0 decision days with at least one lead scored as B1's (0.00%).
