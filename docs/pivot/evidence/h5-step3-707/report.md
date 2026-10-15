# H5 step 3 (#707): the 2021-23 loss and the upper tail

Development days only; 1868 decision days 2018-06-29 to 2025-12-23, 748 of them in 2021-23. Declaration: `metadata/h5_step3_707.json`. Studentized stationary bootstrap, block 10, 10000 draws, seed 707, one-sided 95%. Skill cells: skill [lower, upper] one-sided bounds. No verdict.

Decision days by as-of scarcity state: abundant 1041, ample 313, scarce 473, tight 41, unknown 0

## Sub-question 1: 2021-23

### c_two_part_new

| | grid CRPS | median bias | median MAE | width of 90% | coverage 90% | coverage 50% | var(y) |
|---|---|---|---|---|---|---|---|
| candidate | 0.927 | -0.882 | 1.340 | 4.487 | 0.729 | 0.311 | 5.535 |
| B1 | 0.711 | -0.014 | 0.843 | 6.062 | 0.882 | 0.589 | 5.535 |

Against B1 in 2021-23: -30.4% [-54.7%, -13.5%]; against B2: +37.4% [+20.5%, +54.7%].

Skill against B1 by year of the decision day, and by as-of scarcity state:

| cut | days | skill vs B1 |
|---|---|---|
| 2021 | 250 | -21.0% [-46.9%, +2.3%] |
| 2022 | 249 | -60.8% [-100.2%, -26.7%] |
| 2023 | 249 | +1.0% [-14.7%, +11.5%] |
| state abundant | 669 | -29.5% [-57.7%, -10.5%] |
| state ample | 79 | -35.9% [-68.5%, -6.4%] |
| state scarce | 0 | n/a |
| state tight | 0 | n/a |

PIT shares (bins ≤0.10, 0.10-0.25, 0.25-0.50, 0.50-0.75, 0.75-0.90, >0.90; expected 0.10 0.15 0.25 0.25 0.15 0.10):

| cut | cells | shares |
|---|---|---|
| 2021-23 | 3740 | 0.42 0.19 0.22 0.09 0.05 0.04 |
| all days | 9340 | 0.25 0.13 0.22 0.16 0.10 0.14 |
| 2021-23, abundant | 3345 | 0.40 0.19 0.23 0.09 0.05 0.04 |
| 2021-23, ample | 395 | 0.57 0.18 0.13 0.07 0.02 0.03 |
| 2021-23, scarce | 0 | n/a n/a n/a n/a n/a n/a |
| 2021-23, tight | 0 | n/a n/a n/a n/a n/a n/a |

Loss split on the window (hindsight counterfactuals; shift -0.341 bp, scale factor 1.0):

| part | mean CRPS difference (bp) |
|---|---|
| gap, S0 - B1 | +0.216 (lower bound +0.100) |
| level, S0 - S1 | +0.032 (lower bound -0.004) |
| dispersion, S1 - S2 | -0.000 (lower bound -0.000) |
| remainder, S2 - B1 | +0.184 (lower bound +0.087) |

S0 0.927, S1 0.895, S2 0.895, B1 0.711. Component named by the reading rule: **remainder**.

Remedies (post-hoc, causal, declared):

| remedy | window vs B1 | window vs unremedied | pooled vs B1 | pooled vs unremedied | reading |
|---|---|---|---|---|---|
| level | -32.2% [-52.8%, -15.5%] | -1.3% [-9.0%, +4.4%] | +20.1% [+10.9%, +39.1%] | -0.2% [-2.8%, +2.0%] | not closed |
| scale | -30.5% [-54.7%, -13.6%] | -0.0% [-0.1%, +0.0%] | +20.3% [+11.2%, +38.0%] | -0.0% [-0.1%, -0.0%] | not closed |
| shrink | +1.2% [-2.6%, +4.6%] | +24.2% [+15.5%, +34.6%] | +23.9% [+18.0%, +34.4%] | +4.5% [-2.5%, +9.1%] | closed (level with B1, interval includes 0) |

### gbm_funding

| | grid CRPS | median bias | median MAE | width of 90% | coverage 90% | coverage 50% | var(y) |
|---|---|---|---|---|---|---|---|
| candidate | 0.717 | -0.394 | 0.972 | 2.901 | 0.732 | 0.285 | 5.535 |
| B1 | 0.711 | -0.014 | 0.843 | 6.062 | 0.882 | 0.589 | 5.535 |

Against B1 in 2021-23: -0.9% [-17.8%, +10.1%]; against B2: +51.6% [+38.0%, +65.9%].

Skill against B1 by year of the decision day, and by as-of scarcity state:

| cut | days | skill vs B1 |
|---|---|---|
| 2021 | 250 | +5.9% [-28.5%, +30.5%] |
| 2022 | 249 | -15.5% [-46.2%, +6.2%] |
| 2023 | 249 | +12.5% [+6.6%, +21.4%] |
| state abundant | 669 | -1.3% [-21.1%, +11.3%] |
| state ample | 79 | +1.6% [-16.4%, +20.9%] |
| state scarce | 0 | n/a |
| state tight | 0 | n/a |

PIT shares (bins ≤0.10, 0.10-0.25, 0.25-0.50, 0.50-0.75, 0.75-0.90, >0.90; expected 0.10 0.15 0.25 0.25 0.15 0.10):

| cut | cells | shares |
|---|---|---|
| 2021-23 | 3740 | 0.33 0.26 0.17 0.11 0.05 0.08 |
| all days | 9340 | 0.26 0.16 0.17 0.14 0.10 0.17 |
| 2021-23, abundant | 3345 | 0.29 0.28 0.18 0.11 0.05 0.09 |
| 2021-23, ample | 395 | 0.65 0.12 0.08 0.07 0.04 0.04 |
| 2021-23, scarce | 0 | n/a n/a n/a n/a n/a n/a |
| 2021-23, tight | 0 | n/a n/a n/a n/a n/a n/a |

Loss split on the window (hindsight counterfactuals; shift -0.097 bp, scale factor 1.2):

| part | mean CRPS difference (bp) |
|---|---|
| gap, S0 - B1 | +0.006 (lower bound -0.070) |
| level, S0 - S1 | +0.006 (lower bound -0.002) |
| dispersion, S1 - S2 | +0.004 (lower bound -0.005) |
| remainder, S2 - B1 | -0.004 (lower bound -0.074) |

S0 0.717, S1 0.711, S2 0.707, B1 0.711. Component named by the reading rule: **level**.

Remedies (post-hoc, causal, declared):

| remedy | window vs B1 | window vs unremedied | pooled vs B1 | pooled vs unremedied | reading |
|---|---|---|---|---|---|
| level | -1.9% [-17.2%, +8.7%] | -1.0% [-2.8%, +0.7%] | +20.3% [+12.8%, +40.5%] | -0.5% [-1.5%, +0.4%] | not closed |
| scale | -0.9% [-17.8%, +10.1%] | -0.0% [-0.0%, +0.0%] | +20.7% [+13.3%, +40.0%] | -0.0% [-0.0%, -0.0%] | not closed |
| shrink | +8.3% [+2.2%, +13.5%] | +9.2% [+2.8%, +19.5%] | +20.9% [+14.5%, +38.1%] | +0.3% [-1.9%, +2.3%] | closed (beats B1) |

## Sub-question 2: the upper tail (twCRPS above 0 bp)

### c_two_part_new

| cut | days | vs B1 | vs B2 |
|---|---|---|---|
| pooled | 1868 | +35.7% [+26.5%, +51.7%] | +21.3% [+8.8%, +34.4%] |
| state abundant | 1041 | +39.7% [+23.5%, +63.2%] | -12.7% [-41.1%, +6.4%] |
| state ample | 313 | +48.5% [+29.0%, +64.1%] | +78.7% [+59.7%, +89.8%] |
| state scarce | 473 | +36.1% [+25.5%, +54.2%] | +16.0% [+4.8%, +30.0%] |
| state tight | 41 | +18.4% [-27.0%, +38.9%] | +39.4% [+24.9%, +59.5%] |
| day type month_end | 507 | +18.1% [+9.0%, +28.2%] | +35.6% [+21.7%, +50.7%] |
| day type ordinary | 1868 | +43.7% [+27.2%, +74.0%] | +21.9% [+12.7%, +31.4%] |
| day type quarter_end | 146 | +8.6% [-1.3%, +18.3%] | +11.8% [-44.6%, +59.7%] |
| day type tax_date | 214 | -2.7% [-10.0%, +2.3%] | +18.2% [-37.2%, +50.6%] |

| cut | cells above 0 bp | coverage q90 | coverage q95 | median PIT | share PIT > 0.5 | share beyond q99 | (y - q50)/(q95 - q50) |
|---|---|---|---|---|---|---|---|
| pooled | 1586 | 0.627 | 0.731 | 0.825 | 0.779 | 0.088 | 0.543 |
| state abundant | 51 | 0.216 | 0.314 | 0.982 | 0.961 | 0.373 | 1.355 |
| state ample | 75 | 0.333 | 0.520 | 0.925 | 0.987 | 0.160 | 0.853 |
| state scarce | 1356 | 0.662 | 0.759 | 0.775 | 0.751 | 0.067 | 0.513 |
| state tight | 104 | 0.587 | 0.721 | 0.875 | 0.913 | 0.163 | 0.572 |

Unconditional exceedance: q90 0.143 (nominal 0.10, lower bound 0.114); q95 0.095 (nominal 0.05, lower bound 0.075).

Reading rule: **under-dispersed**.

### gbm_funding

| cut | days | vs B1 | vs B2 |
|---|---|---|---|
| pooled | 1868 | +31.3% [+22.1%, +50.6%] | +15.9% [+3.8%, +29.2%] |
| state abundant | 1041 | +35.4% [+22.8%, +53.5%] | -20.7% [-42.8%, -5.2%] |
| state ample | 313 | +56.6% [+29.3%, +75.9%] | +82.0% [+60.1%, +94.1%] |
| state scarce | 473 | +31.7% [+21.3%, +53.8%] | +10.2% [-0.5%, +23.5%] |
| state tight | 41 | +6.9% [-14.1%, +23.8%] | +30.9% [+3.1%, +65.2%] |
| day type month_end | 507 | +2.0% [-11.5%, +16.5%] | +22.9% [+2.5%, +45.6%] |
| day type ordinary | 1868 | +41.6% [+26.2%, +77.6%] | +18.9% [+9.2%, +28.9%] |
| day type quarter_end | 146 | -11.7% [-50.8%, -2.4%] | -7.8% [-71.1%, +47.3%] |
| day type tax_date | 214 | -6.4% [-14.1%, -1.6%] | +15.3% [-29.5%, +51.0%] |

| cut | cells above 0 bp | coverage q90 | coverage q95 | median PIT | share PIT > 0.5 | share beyond q99 | (y - q50)/(q95 - q50) |
|---|---|---|---|---|---|---|---|
| pooled | 1586 | 0.599 | 0.682 | 0.825 | 0.731 | 0.142 | 0.537 |
| state abundant | 51 | 0.059 | 0.098 | 0.995 | 0.980 | 0.843 | 3.319 |
| state ample | 75 | 0.213 | 0.347 | 0.962 | 1.000 | 0.160 | 1.460 |
| state scarce | 1356 | 0.659 | 0.735 | 0.775 | 0.690 | 0.108 | 0.469 |
| state tight | 104 | 0.365 | 0.510 | 0.925 | 0.962 | 0.221 | 0.934 |

Unconditional exceedance: q90 0.173 (nominal 0.10, lower bound 0.147); q95 0.128 (nominal 0.05, lower bound 0.106).

Reading rule: **under-dispersed**.
