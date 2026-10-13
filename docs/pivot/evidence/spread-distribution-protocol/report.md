Decision days scored: 1868 (2018-06-29 to 2025-12-23); every target day on or before 2025-12-31. Bootstrap: stationary, mean block 10, 10,000 draws, seed 634, one-sided 95%.

Reading of each cell: **skill [one-sided 95% lower bound, upper bound] / lower bound of the mean daily difference** (bp). Skill is mean(d) / mean(benchmark score), d = benchmark − candidate, positive favours the candidate. The protocol would call a candidate better only if the lower bound of the mean difference is above 0 against B1 and B2 and the skill is at least 3%; on development days this is a reading, not a verdict.

### Table 1. Primary score: grid CRPS (bp), averaged over h = 1 to 5, pooled

| model | mean | vs B1 | vs B2 | vs B3 |
|---|---|---|---|---|
| B1 as-of persistence | 2.302 | - | n/a | n/a |
| B2 calendar climatology | 2.514 | n/a | - | n/a |
| B3 published declaration | 1.823 | +20.8% [+11.5%, +29.0%] / +0.206 | +27.5% [+20.1%, +35.2%] / +0.486 | - |
| gbm, published features (phase 2) | 1.826 | +20.7% [+11.3%, +28.9%] / +0.205 | +27.4% [+19.8%, +35.2%] / +0.482 | -0.2% [-1.7%, +1.5%] / -0.033 |
| (a) published + new inputs | 1.838 | +20.2% [+10.6%, +28.6%] / +0.188 | +26.9% [+19.5%, +34.4%] / +0.471 | -0.8% [-2.2%, +0.4%] / -0.038 |
| (b) gbm + new inputs | 1.841 | +20.1% [+10.4%, +28.5%] / +0.188 | +26.8% [+19.3%, +34.5%] / +0.471 | -1.0% [-3.1%, +1.0%] / -0.055 |
| (c) two-part + new inputs | 1.835 | +20.3% [+9.0%, +29.4%] / +0.162 | +27.0% [+19.9%, +34.3%] / +0.477 | -0.7% [-5.1%, +3.2%] / -0.087 |

### Table 2. Key secondary: upper-tail twCRPS (weight 1{y > 0 bp}), pooled

| model | mean | vs B1 | vs B2 | vs B3 |
|---|---|---|---|---|
| B1 as-of persistence | 1.379 | - | n/a | n/a |
| B2 calendar climatology | 1.126 | n/a | - | n/a |
| B3 published declaration | 0.939 | +31.9% [+19.2%, +41.9%] / +0.167 | +16.6% [+8.2%, +27.2%] / +0.089 | - |
| gbm, published features (phase 2) | 0.947 | +31.3% [+18.8%, +41.4%] / +0.164 | +15.9% [+7.1%, +27.3%] / +0.080 | -0.9% [-2.5%, +1.4%] / -0.027 |
| (a) published + new inputs | 0.933 | +32.3% [+19.8%, +42.2%] / +0.171 | +17.1% [+9.0%, +27.4%] / +0.096 | +0.6% [-1.2%, +2.3%] / -0.009 |
| (b) gbm + new inputs | 0.944 | +31.6% [+19.0%, +41.6%] / +0.166 | +16.2% [+7.9%, +27.1%] / +0.087 | -0.5% [-2.8%, +2.0%] / -0.026 |
| (c) two-part + new inputs | 0.886 | +35.7% [+23.4%, +45.6%] / +0.206 | +21.3% [+13.1%, +32.4%] / +0.143 | +5.6% [+1.5%, +10.9%] / +0.013 |

### Table 3. Ablation: each variant against the same model without the new inputs (primary score)

| pair (parent → variant) | skill [bounds] / lower bound of mean(d) |
|---|---|
| B3 published declaration → (a) published + new inputs | -0.8% [-2.2%, +0.4%] / -0.038 |
| gbm, published features (phase 2) → (b) gbm + new inputs | -0.8% [-2.2%, +0.4%] / -0.036 |
| (b) gbm + new inputs → (c) two-part + new inputs | +0.3% [-4.4%, +4.5%] / -0.075 |

### Table 4. Grid CRPS by lead (bp)

| model | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|
| B1 as-of persistence | 2.029 | 2.228 | 2.353 | 2.424 | 2.478 |
| B2 calendar climatology | 2.480 | 2.503 | 2.518 | 2.528 | 2.544 |
| B3 published declaration | 1.648 | 1.765 | 1.851 | 1.899 | 1.950 |
| gbm, published features (phase 2) | 1.636 | 1.768 | 1.859 | 1.905 | 1.962 |
| (a) published + new inputs | 1.642 | 1.783 | 1.866 | 1.917 | 1.982 |
| (b) gbm + new inputs | 1.632 | 1.777 | 1.874 | 1.927 | 1.993 |
| (c) two-part + new inputs | 1.633 | 1.775 | 1.846 | 1.910 | 2.013 |

### Table 5. By regime of the decision day (primary score)

The regimes were drawn after the fact; no split is a pass requirement (protocol section 7).

**2018-19** (375 decision days)

| model | mean | vs B1 | vs B2 | vs B3 |
|---|---|---|---|---|
| B1 as-of persistence | 5.727 | - | n/a | n/a |
| B2 calendar climatology | 4.364 | n/a | - | n/a |
| B3 published declaration | 4.031 | +29.6% [+12.5%, +41.2%] / +0.449 | +7.6% [-0.0%, +16.8%] / -0.001 | - |
| gbm, published features (phase 2) | 3.993 | +30.3% [+13.6%, +41.9%] / +0.492 | +8.5% [+1.1%, +18.2%] / +0.049 | +0.9% [-1.0%, +3.8%] / -0.046 |
| (a) published + new inputs | 3.977 | +30.6% [+13.8%, +41.9%] / +0.492 | +8.9% [+1.0%, +18.3%] / +0.039 | +1.3% [-0.6%, +3.3%] / -0.020 |
| (b) gbm + new inputs | 3.926 | +31.4% [+15.1%, +42.9%] / +0.537 | +10.0% [+2.6%, +19.6%] / +0.110 | +2.6% [+0.2%, +5.8%] / +0.010 |
| (c) two-part + new inputs | 3.897 | +32.0% [+14.2%, +44.1%] / +0.529 | +10.7% [+4.7%, +19.8%] / +0.205 | +3.3% [-2.3%, +9.7%] / -0.088 |

**2020** (251 decision days)

| model | mean | vs B1 | vs B2 | vs B3 |
|---|---|---|---|---|
| B1 as-of persistence | 1.644 | - | n/a | n/a |
| B2 calendar climatology | 2.786 | n/a | - | n/a |
| B3 published declaration | 1.438 | +12.6% [-1.7%, +22.8%] / -0.022 | +48.4% [+33.6%, +60.4%] / +0.672 | - |
| gbm, published features (phase 2) | 1.417 | +13.8% [+1.7%, +25.0%] / +0.023 | +49.1% [+32.5%, +63.4%] / +0.688 | +1.4% [-4.7%, +10.5%] / -0.092 |
| (a) published + new inputs | 1.443 | +12.2% [-0.6%, +22.1%] / -0.008 | +48.2% [+32.6%, +61.1%] / +0.665 | -0.4% [-4.1%, +4.4%] / -0.074 |
| (b) gbm + new inputs | 1.457 | +11.4% [-1.6%, +23.2%] / -0.023 | +47.7% [+30.8%, +62.6%] / +0.653 | -1.3% [-9.4%, +9.8%] / -0.175 |
| (c) two-part + new inputs | 1.670 | -1.6% [-25.5%, +15.1%] / -0.336 | +40.1% [+23.5%, +53.7%] / +0.471 | -16.2% [-30.3%, -5.4%] / -0.417 |

**2021-23** (748 decision days)

| model | mean | vs B1 | vs B2 | vs B3 |
|---|---|---|---|---|
| B1 as-of persistence | 0.711 | - | n/a | n/a |
| B2 calendar climatology | 1.481 | n/a | - | n/a |
| B3 published declaration | 0.752 | -5.8% [-17.4%, +5.2%] / -0.124 | +49.2% [+37.7%, +59.7%] / +0.485 | - |
| gbm, published features (phase 2) | 0.717 | -0.9% [-12.6%, +10.4%] / -0.092 | +51.6% [+40.3%, +62.2%] / +0.521 | +4.6% [+1.5%, +8.5%] / +0.011 |
| (a) published + new inputs | 0.784 | -10.3% [-22.3%, +1.0%] / -0.163 | +47.1% [+34.8%, +58.2%] / +0.450 | -4.3% [-7.4%, -1.2%] / -0.056 |
| (b) gbm + new inputs | 0.744 | -4.7% [-17.1%, +7.2%] / -0.126 | +49.7% [+37.5%, +61.0%] / +0.489 | +1.0% [-2.8%, +5.4%] / -0.023 |
| (c) two-part + new inputs | 0.927 | -30.4% [-48.4%, -14.3%] / -0.352 | +37.4% [+23.7%, +50.1%] / +0.311 | -23.3% [-34.1%, -13.8%] / -0.258 |

**2024** (250 decision days)

| model | mean | vs B1 | vs B2 | vs B3 |
|---|---|---|---|---|
| B1 as-of persistence | 1.683 | - | n/a | n/a |
| B2 calendar climatology | 1.378 | n/a | - | n/a |
| B3 published declaration | 1.362 | +19.1% [+12.0%, +23.9%] / +0.136 | +1.2% [-11.2%, +14.7%] / -0.156 | - |
| gbm, published features (phase 2) | 1.411 | +16.2% [+9.3%, +21.6%] / +0.110 | -2.4% [-16.1%, +12.9%] / -0.232 | -3.6% [-6.1%, -0.8%] / -0.104 |
| (a) published + new inputs | 1.398 | +16.9% [+10.7%, +21.3%] / +0.121 | -1.5% [-15.8%, +13.6%] / -0.224 | -2.7% [-5.4%, -0.1%] / -0.083 |
| (b) gbm + new inputs | 1.435 | +14.7% [+8.0%, +19.9%] / +0.095 | -4.1% [-18.4%, +11.4%] / -0.266 | -5.4% [-8.4%, -2.0%] / -0.138 |
| (c) two-part + new inputs | 1.265 | +24.8% [+11.9%, +32.9%] / +0.132 | +8.2% [-2.2%, +16.9%] / -0.027 | +7.1% [-1.6%, +13.0%] / -0.016 |

**2025-26** (244 decision days)

| model | mean | vs B1 | vs B2 | vs B3 |
|---|---|---|---|---|
| B1 as-of persistence | 3.231 | - | n/a | n/a |
| B2 calendar climatology | 3.724 | n/a | - | n/a |
| B3 published declaration | 2.580 | +20.1% [+13.2%, +26.2%] / +0.360 | +30.7% [+12.0%, +41.9%] / +0.313 | - |
| gbm, published features (phase 2) | 2.742 | +15.1% [+7.5%, +22.0%] / +0.207 | +26.4% [+5.5%, +39.0%] / +0.143 | -6.3% [-9.1%, -3.6%] / -0.237 |
| (a) published + new inputs | 2.637 | +18.4% [+11.7%, +24.3%] / +0.320 | +29.2% [+10.6%, +40.4%] / +0.277 | -2.2% [-3.9%, -0.5%] / -0.106 |
| (b) gbm + new inputs | 2.807 | +13.1% [+5.8%, +19.8%] / +0.160 | +24.6% [+3.9%, +37.3%] / +0.102 | -8.8% [-11.7%, -5.6%] / -0.316 |
| (c) two-part + new inputs | 2.207 | +31.7% [+23.7%, +38.8%] / +0.646 | +40.7% [+24.5%, +50.2%] / +0.635 | +14.4% [+9.0%, +19.8%] / +0.219 |

### Table 6. By pressure-day type of the target day (primary score)

**month_end** (507 decision days with such a target, 747 target cells)

| model | mean | vs B1 | vs B2 | vs B3 |
|---|---|---|---|---|
| B1 as-of persistence | 2.220 | - | n/a | n/a |
| B2 calendar climatology | 2.875 | n/a | - | n/a |
| B3 published declaration | 2.052 | +7.6% [+1.1%, +13.7%] / +0.022 | +28.6% [+15.9%, +39.8%] / +0.385 | - |
| gbm, published features (phase 2) | 2.150 | +3.2% [-3.6%, +10.2%] / -0.079 | +25.2% [+11.1%, +37.6%] / +0.274 | -4.8% [-7.2%, -1.8%] / -0.171 |
| (a) published + new inputs | 2.064 | +7.0% [+0.6%, +12.5%] / +0.012 | +28.2% [+15.8%, +39.0%] / +0.379 | -0.6% [-4.2%, +2.9%] / -0.082 |
| (b) gbm + new inputs | 2.170 | +2.3% [-4.3%, +8.5%] / -0.089 | +24.5% [+11.0%, +36.5%] / +0.269 | -5.7% [-9.5%, -1.8%] / -0.212 |
| (c) two-part + new inputs | 1.910 | +14.0% [+2.3%, +23.3%] / +0.040 | +33.6% [+24.7%, +41.0%] / +0.571 | +7.0% [-2.5%, +14.2%] / -0.042 |

**ordinary** (1868 decision days with such a target, 8002 target cells)

| model | mean | vs B1 | vs B2 | vs B3 |
|---|---|---|---|---|
| B1 as-of persistence | 1.995 | - | n/a | n/a |
| B2 calendar climatology | 2.151 | n/a | - | n/a |
| B3 published declaration | 1.510 | +24.3% [+12.7%, +35.7%] / +0.205 | +29.8% [+22.9%, +36.3%] / +0.453 | - |
| gbm, published features (phase 2) | 1.496 | +25.0% [+13.3%, +36.5%] / +0.216 | +30.5% [+23.5%, +37.1%] / +0.470 | +1.0% [-0.9%, +3.0%] / -0.015 |
| (a) published + new inputs | 1.520 | +23.8% [+12.0%, +35.4%] / +0.195 | +29.4% [+22.2%, +36.0%] / +0.440 | -0.7% [-2.1%, +0.8%] / -0.032 |
| (b) gbm + new inputs | 1.502 | +24.7% [+12.6%, +36.4%] / +0.207 | +30.2% [+23.2%, +36.8%] / +0.461 | +0.5% [-2.0%, +3.0%] / -0.031 |
| (c) two-part + new inputs | 1.567 | +21.4% [+7.4%, +34.2%] / +0.122 | +27.2% [+20.1%, +33.8%] / +0.397 | -3.8% [-8.8%, +0.9%] / -0.130 |

**quarter_end** (146 decision days with such a target, 146 target cells)

| model | mean | vs B1 | vs B2 | vs B3 |
|---|---|---|---|---|
| B1 as-of persistence | 6.745 | - | n/a | n/a |
| B2 calendar climatology | 7.382 | n/a | - | n/a |
| B3 published declaration | 6.966 | -3.3% [-12.6%, +0.2%] / -0.472 | +5.6% [-25.3%, +39.2%] / -1.835 | - |
| gbm, published features (phase 2) | 7.639 | -13.3% [-21.1%, -8.3%] / -1.496 | -3.5% [-38.7%, +35.7%] / -2.953 | -9.7% [-14.4%, -3.2%] / -1.336 |
| (a) published + new inputs | 7.002 | -3.8% [-16.2%, +0.7%] / -0.564 | +5.1% [-26.6%, +38.1%] / -1.893 | -0.5% [-5.1%, +2.7%] / -0.256 |
| (b) gbm + new inputs | 7.645 | -13.3% [-23.2%, -9.1%] / -1.356 | -3.6% [-38.3%, +34.1%] / -2.871 | -9.7% [-13.5%, -5.8%] / -1.192 |
| (c) two-part + new inputs | 6.124 | +9.2% [-11.3%, +24.9%] / -0.456 | +17.0% [-5.5%, +44.1%] / -0.434 | +12.1% [-1.7%, +27.3%] / -0.073 |

**tax_date** (214 decision days with such a target, 445 target cells)

| model | mean | vs B1 | vs B2 | vs B3 |
|---|---|---|---|---|
| B1 as-of persistence | 4.919 | - | n/a | n/a |
| B2 calendar climatology | 7.162 | n/a | - | n/a |
| B3 published declaration | 5.192 | -5.6% [-19.7%, +2.6%] / -0.641 | +27.5% [+14.4%, +58.9%] / +1.248 | - |
| gbm, published features (phase 2) | 5.196 | -5.6% [-18.1%, +4.1%] / -0.681 | +27.5% [+13.6%, +61.1%] / +1.180 | -0.1% [-3.2%, +6.4%] / -0.147 |
| (a) published + new inputs | 5.245 | -6.6% [-25.1%, +0.1%] / -0.673 | +26.8% [+14.2%, +57.0%] / +1.199 | -1.0% [-7.2%, +0.6%] / -0.159 |
| (b) gbm + new inputs | 5.285 | -7.4% [-25.9%, -0.3%] / -0.768 | +26.2% [+13.1%, +58.0%] / +1.093 | -1.8% [-10.8%, +1.9%] / -0.296 |
| (c) two-part + new inputs | 5.215 | -6.0% [-30.2%, +3.9%] / -0.741 | +27.2% [+14.8%, +57.1%] / +1.192 | -0.4% [-9.6%, +2.7%] / -0.203 |

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
| mae_median | gbm, published features (phase 2) | +16.7% [+7.9%, +24.4%] / +0.183 | +0.9% [+0.1%, +2.0%] / +0.003 |
| mae_median | (a) published + new inputs | +14.9% [+5.3%, +23.2%] / +0.124 | -1.2% [-2.8%, +0.2%] / -0.064 |
| mae_median | (b) gbm + new inputs | +16.3% [+7.2%, +24.3%] / +0.166 | +0.5% [-1.0%, +1.9%] / -0.023 |
| mae_median | (c) two-part + new inputs | +12.0% [+0.1%, +21.8%] / +0.003 | -4.6% [-10.0%, +0.1%] / -0.227 |
| pinball_0.05 | gbm, published features (phase 2) | +55.8% [+35.0%, +69.0%] / +0.196 | -5.6% [-20.3%, +7.2%] / -0.068 |
| pinball_0.05 | (a) published + new inputs | +57.2% [+40.1%, +68.5%] / +0.220 | -2.3% [-6.1%, +1.4%] / -0.021 |
| pinball_0.05 | (b) gbm + new inputs | +54.7% [+33.5%, +68.2%] / +0.188 | -8.3% [-23.9%, +5.1%] / -0.080 |
| pinball_0.05 | (c) two-part + new inputs | +57.2% [+36.4%, +70.1%] / +0.202 | -2.4% [-17.7%, +10.5%] / -0.060 |
| pinball_0.25 | gbm, published features (phase 2) | +36.3% [+24.9%, +45.8%] / +0.264 | +2.7% [+1.7%, +3.9%] / +0.016 |
| pinball_0.25 | (a) published + new inputs | +33.7% [+21.4%, +43.9%] / +0.227 | -1.2% [-3.2%, +0.8%] / -0.028 |
| pinball_0.25 | (b) gbm + new inputs | +35.2% [+23.5%, +44.9%] / +0.249 | +1.1% [-0.8%, +2.9%] / -0.007 |
| pinball_0.25 | (c) two-part + new inputs | +33.0% [+19.9%, +43.6%] / +0.210 | -2.2% [-7.2%, +2.6%] / -0.062 |
| pinball_0.5 | gbm, published features (phase 2) | +16.7% [+7.9%, +24.4%] / +0.091 | +0.9% [+0.1%, +2.0%] / +0.001 |
| pinball_0.5 | (a) published + new inputs | +14.9% [+5.3%, +23.2%] / +0.062 | -1.2% [-2.8%, +0.2%] / -0.032 |
| pinball_0.5 | (b) gbm + new inputs | +16.3% [+7.2%, +24.3%] / +0.083 | +0.5% [-1.0%, +1.9%] / -0.012 |
| pinball_0.5 | (c) two-part + new inputs | +12.0% [+0.1%, +21.8%] / +0.002 | -4.6% [-10.0%, +0.1%] / -0.113 |
| pinball_0.75 | gbm, published features (phase 2) | +6.4% [+1.1%, +11.3%] / +0.013 | +1.1% [+0.5%, +1.8%] / +0.007 |
| pinball_0.75 | (a) published + new inputs | +4.8% [-1.1%, +10.2%] / -0.012 | -0.5% [-2.5%, +1.0%] / -0.028 |
| pinball_0.75 | (b) gbm + new inputs | +6.3% [+0.8%, +11.4%] / +0.009 | +1.0% [-0.7%, +2.5%] / -0.008 |
| pinball_0.75 | (c) two-part + new inputs | +7.0% [-0.7%, +13.4%] / -0.008 | +1.8% [-3.2%, +6.1%] / -0.038 |
| pinball_0.95 | gbm, published features (phase 2) | -6.6% [-14.9%, +0.3%] / -0.116 | -8.9% [-15.5%, -2.9%] / -0.126 |
| pinball_0.95 | (a) published + new inputs | +2.2% [-3.8%, +7.4%] / -0.027 | +0.1% [-2.7%, +2.7%] / -0.019 |
| pinball_0.95 | (b) gbm + new inputs | -9.0% [-17.4%, -2.3%] / -0.131 | -11.3% [-19.4%, -4.8%] / -0.148 |
| pinball_0.95 | (c) two-part + new inputs | +4.9% [-1.5%, +11.5%] / -0.011 | +2.9% [-1.7%, +8.5%] / -0.014 |

### Table 8. Central coverage (share of target cells inside the interval), pooled

| level | nominal | B1 as-of persistence | B2 calendar climatology | B3 published declaration | gbm, published features (phase 2) | (a) published + new inputs | (b) gbm + new inputs | (c) two-part + new inputs |
|---|---|---|---|---|---|---|---|---|
| 50% | 0.50 | 0.530 | 0.466 | 0.303 | 0.307 | 0.298 | 0.336 | 0.380 |
| 90% | 0.90 | 0.842 | 0.823 | 0.886 | 0.695 | 0.888 | 0.665 | 0.749 |

### Table 9. Upper tail: Brier score of P(spread > threshold), read off each distribution, against the models fitted at the threshold and lead

**> +0 bp** (1868 decision days, 1586 event cells)

| model | mean Brier | vs persistence-logistic | vs calendar climatology |
|---|---|---|---|
| B1 as-of persistence | 0.06930 | n/a | n/a |
| B2 calendar climatology | 0.11425 | n/a | n/a |
| B3 published declaration | 0.06373 | +18.5% [+10.4%, +26.5%] / +0.008 | +56.7% [+48.0%, +65.1%] / +0.065 |
| (a) published + new inputs | 0.06121 | +21.7% [+14.0%, +29.5%] / +0.010 | +58.4% [+50.1%, +66.5%] / +0.068 |
| (b) gbm + new inputs | 0.06141 | +21.4% [+12.3%, +31.1%] / +0.009 | +58.3% [+48.7%, +67.6%] / +0.067 |
| (c) two-part + new inputs | 0.06240 | +20.2% [+13.8%, +26.6%] / +0.010 | +57.6% [+49.9%, +65.3%] / +0.069 |
| calendar climatology | 0.14726 | n/a | - |
| gbm, published features (phase 2) | 0.06245 | +20.1% [+10.3%, +30.3%] / +0.008 | +57.6% [+47.7%, +67.2%] / +0.065 |
| persistence-logistic | 0.07817 | - | n/a |

**> +10 bp** (1868 decision days, 293 event cells)

| model | mean Brier | vs persistence-logistic | vs calendar climatology |
|---|---|---|---|
| B1 as-of persistence | 0.04291 | n/a | n/a |
| B2 calendar climatology | 0.03037 | n/a | n/a |
| B3 published declaration | 0.02849 | +4.3% [-2.7%, +9.3%] / -0.001 | +10.1% [+2.0%, +18.1%] / +0.001 |
| (a) published + new inputs | 0.02896 | +2.7% [-5.2%, +8.6%] / -0.001 | +8.6% [+0.2%, +17.0%] / +0.000 |
| (b) gbm + new inputs | 0.02917 | +2.0% [-3.4%, +6.6%] / -0.001 | +7.9% [+0.4%, +16.6%] / +0.000 |
| (c) two-part + new inputs | 0.02593 | +12.9% [+7.9%, +17.3%] / +0.002 | +18.2% [+11.6%, +25.8%] / +0.003 |
| calendar climatology | 0.03169 | n/a | - |
| gbm, published features (phase 2) | 0.02907 | +2.3% [-2.2%, +6.3%] / -0.001 | +8.3% [+1.0%, +16.9%] / +0.000 |
| persistence-logistic | 0.02976 | - | n/a |

**> +2 bp** (1868 decision days, 1143 event cells)

| model | mean Brier | vs persistence-logistic | vs calendar climatology |
|---|---|---|---|
| B1 as-of persistence | 0.06856 | n/a | n/a |
| B2 calendar climatology | 0.09538 | n/a | n/a |
| B3 published declaration | 0.06292 | +17.2% [+9.3%, +24.9%] / +0.006 | +43.8% [+35.3%, +52.2%] / +0.036 |
| (a) published + new inputs | 0.06041 | +20.5% [+12.6%, +28.1%] / +0.008 | +46.0% [+37.8%, +54.1%] / +0.038 |
| (b) gbm + new inputs | 0.06220 | +18.1% [+9.7%, +26.7%] / +0.007 | +44.4% [+35.6%, +53.3%] / +0.037 |
| (c) two-part + new inputs | 0.06040 | +20.5% [+15.5%, +26.2%] / +0.011 | +46.0% [+39.0%, +53.7%] / +0.041 |
| calendar climatology | 0.11186 | n/a | - |
| gbm, published features (phase 2) | 0.06379 | +16.0% [+7.7%, +24.7%] / +0.005 | +43.0% [+33.7%, +52.3%] / +0.035 |
| persistence-logistic | 0.07596 | - | n/a |

**> +5 bp** (1868 decision days, 681 event cells)

| model | mean Brier | vs persistence-logistic | vs calendar climatology |
|---|---|---|---|
| B1 as-of persistence | 0.06420 | n/a | n/a |
| B2 calendar climatology | 0.06453 | n/a | n/a |
| B3 published declaration | 0.05214 | +13.0% [+6.7%, +18.9%] / +0.003 | +25.7% [+17.9%, +34.0%] / +0.011 |
| (a) published + new inputs | 0.05194 | +13.3% [+6.3%, +19.9%] / +0.003 | +25.9% [+17.6%, +34.7%] / +0.011 |
| (b) gbm + new inputs | 0.05470 | +8.7% [+1.3%, +16.2%] / +0.001 | +22.0% [+12.9%, +32.0%] / +0.008 |
| (c) two-part + new inputs | 0.04856 | +19.0% [+14.4%, +24.2%] / +0.008 | +30.8% [+25.0%, +38.3%] / +0.017 |
| calendar climatology | 0.07013 | n/a | - |
| gbm, published features (phase 2) | 0.05378 | +10.3% [+3.9%, +16.8%] / +0.002 | +23.3% [+15.0%, +32.6%] / +0.010 |
| persistence-logistic | 0.05993 | - | n/a |

### Missing forecasts (protocol section 11)

- B3 published declaration: 0 decision days with at least one lead scored as B1's (0.00%).
- (a) published + new inputs: 0 decision days with at least one lead scored as B1's (0.00%).
- (b) gbm + new inputs: 0 decision days with at least one lead scored as B1's (0.00%).
- (c) two-part + new inputs: 2 decision days with at least one lead scored as B1's (0.11%).
- gbm, published features (phase 2): 0 decision days with at least one lead scored as B1's (0.00%).
