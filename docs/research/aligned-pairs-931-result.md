# Training `treasury_settlement` from the target's own row, at lead 1 (#931, H5)

**Development data, not a verdict.** A measurement under scoring protocol v1: nothing is published or registered; the declared candidate,
the published model and every published figure are as they were. Whether the candidate changes is Eleonora's. Declaration:
`metadata/aligned_pairs_931.json`.

Decision days 2018-06-29 to 2025-12-23 (1868), lead 1 only; no day after
2025-12-31 and no locked day is scored. Panel `4ddc3882cd6d…`. Grid CRPS in bp (lower is better). A skill cell is the skill of the second
forecast over the first named (positive favours the second), with the one-sided 95% lower and upper bounds of skill from the studentized stationary
bootstrap, as `[lower, upper]` (block 10, seed 931; 10,000 draws on the pooled row, 2,000 on splits).

## The three arms

- `gbm_funding`: training pairs unset (one-step)
- `gbm_funding_aligned`: training pairs unset (one-step)
- `gbm_funding_direct`: training pairs direct

`gbm` is the declared `gbm_funding` (one-step pairs). `aligned` is `gbm_funding` with `treasury_settlement` alone trained from the target's own row
(row p + 1 for the pair (p, p + 1)), every other field one-step, same fit, seed and folds. `twin` is the direct-pairs twin of #449, which also reads every
other field at the as-of read, staler than the one-step pair. The score reproduces #449's recorded twin-over-gbm skill at lead 1 (-2.0152% against -2.0152% recorded).

## The alignment, read from the as-of rule (acceptance 1)

| target day | served from | one-step trains from | aligned trains from | settlement on the day (USD bn) | the day before (USD bn) |
|---|---|---|---|---|---|
| 2019-09-16 | 2019-09-16 | 2019-09-13 | 2019-09-16 | 78.0 | 0.0 |
| 2019-09-30 | 2019-09-30 | 2019-09-27 | 2019-09-30 | 125.0 | 18.0 |
| 2020-03-16 | 2020-03-16 | 2020-03-13 | 2020-03-16 | 78.0 | 0.0 |
| 2021-12-31 | 2021-12-31 | 2021-12-30 | 2021-12-31 | 230.0 | 145.0 |
| 2023-03-13 | 2023-03-13 | 2023-03-10 | 2023-03-13 | 0.0 | 0.0 |
| 2023-03-31 | 2023-03-31 | 2023-03-30 | 2023-03-31 | 214.0 | 135.0 |
| 2025-12-12 | 2025-12-12 | 2025-12-11 | 2025-12-12 | 0.0 | 238.0 |

The one-step pair trains the field from the day before the target; serving reads it from the target's own row; the aligned arm trains it from that row.

Missing laws (the day takes B1's law): gbm_funding 0 (0.0%), gbm_funding_aligned 0 (0.0%), gbm_funding_direct 0 (0.0%).

## The aligned arm against gbm_funding, in one place

- pooled (1868 days): +2.8% [+1.7, +3.8] over gbm_funding's mean grid CRPS of 1.64 bp
- mid_month_coupon (115 days): +13.8% [+8.6, +21.5] over gbm_funding's mean grid CRPS of 1.77 bp
- month_end (149 days): +13.8% [+11.1, +16.6] over gbm_funding's mean grid CRPS of 1.92 bp
- ordinary (1486 days): -0.2% [-1.9, +1.3] over gbm_funding's mean grid CRPS of 1.25 bp
- quarter_end (29 days): too thin
- tax_date (89 days): +2.4% [-1.0, +7.4] over gbm_funding's mean grid CRPS of 5.77 bp

Skills above are all days; the same table without 2019-09-18 follows. Intervals are one-sided 95% bounds `[lower, upper]`.

## all days

| group | days | B1 | B2 | gbm | aligned | twin | gbm vs B1 | aligned vs B1 | gbm vs B2 | aligned vs B2 | **aligned vs gbm** | twin vs gbm | aligned vs twin |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pooled | 1868 | 2.03 | 2.48 | 1.64 | 1.59 | 1.67 | +19.4% [+11.1, +38.8] | +21.6% [+13.8, +39.2] | +34.0% [+22.6, +42.9] | +35.9% [+24.2, +44.4] | +2.8% [+1.7, +3.8] | -2.0% [-4.5, +0.4] | -4.9% [-7.3, -2.6] |

### By target-day type

| group | days | B1 | B2 | gbm | aligned | twin | gbm vs B1 | aligned vs B1 | gbm vs B2 | aligned vs B2 | **aligned vs gbm** | twin vs gbm | aligned vs twin |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mid_month_coupon | 115 | 1.62 | 2.72 | 1.77 | 1.53 | 1.66 | -9.8% [-21.1, -2.0] | +5.3% [-8.4, +16.5] | +34.8% [+22.7, +50.2] | +43.8% [+33.8, +55.4] | +13.8% [+8.6, +21.5] | +6.3% [-1.0, +16.6] | -8.7% [-14.1, -3.2] |
| month_end | 149 | 2.11 | 2.91 | 1.92 | 1.66 | 1.72 | +8.9% [-0.4, +21.7] | +21.4% [+12.4, +34.9] | +33.8% [+14.8, +52.0] | +42.9% [+26.7, +58.2] | +13.8% [+11.1, +16.6] | +10.4% [+4.0, +16.2] | -3.9% [-8.8, +1.4] |
| ordinary | 1486 | 1.77 | 2.02 | 1.25 | 1.25 | 1.32 | +29.3% [+14.6, +71.7] | +29.2% [+14.2, +71.2] | +38.2% [+29.9, +46.6] | +38.1% [+30.1, +46.2] | -0.2% [-1.9, +1.3] | -5.6% [-9.7, -1.9] | -5.4% [-9.1, -2.0] |
| quarter_end | 29 | 6.14 | 7.28 | 6.75 | 6.48 | 6.85 | too thin | too thin | too thin | too thin | too thin | too thin | too thin |
| tax_date | 89 | 5.47 | 7.56 | 5.77 | 5.63 | 5.74 | -5.4% [-15.5, +2.1] | -2.9% [-15.8, +6.3] | +23.8% [-20.8, +48.3] | +25.5% [-22.9, +48.6] | +2.4% [-1.0, +7.4] | +0.5% [-8.2, +7.8] | -1.9% [-6.2, +1.8] |

### By regime of the decision day

| group | days | B1 | B2 | gbm | aligned | twin | gbm vs B1 | aligned vs B1 | gbm vs B2 | aligned vs B2 | **aligned vs gbm** | twin vs gbm | aligned vs twin |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2018-19 | 375 | 5.37 | 4.35 | 3.80 | 3.66 | 3.85 | +29.2% [+18.1, +59.9] | +31.8% [+22.0, +57.7] | +12.5% [+1.3, +24.5] | +15.7% [+2.6, +28.6] | +3.7% [+1.1, +5.8] | -1.4% [-4.4, +1.7] | -5.3% [-8.9, -2.3] |
| 2020 | 251 | 1.35 | 2.74 | 1.24 | 1.21 | 1.26 | +8.5% [-11.3, +22.0] | +10.4% [-9.2, +25.3] | +54.9% [+21.1, +72.0] | +55.9% [+23.5, +71.7] | +2.2% [-1.4, +4.9] | -2.0% [-11.2, +6.4] | -4.2% [-12.7, +2.5] |
| 2021-23 | 748 | 0.52 | 1.45 | 0.63 | 0.62 | 0.72 | -21.3% [-58.8, -4.5] | -20.2% [-58.8, -3.3] | +56.8% [+44.1, +68.7] | +57.2% [+44.3, +69.4] | +1.0% [-1.1, +2.9] | -14.5% [-21.1, -9.2] | -15.6% [-22.6, -10.0] |
| 2024 | 250 | 1.50 | 1.37 | 1.20 | 1.19 | 1.12 | +20.0% [+15.2, +26.0] | +21.0% [+16.6, +26.2] | +12.3% [+2.2, +22.4] | +13.5% [+2.6, +23.8] | +1.3% [-1.3, +3.5] | +7.3% [+3.0, +11.7] | +6.1% [+2.7, +9.8] |
| 2025-26 | 244 | 2.77 | 3.64 | 2.26 | 2.19 | 2.21 | +18.6% [+13.7, +24.3] | +21.1% [+15.3, +26.9] | +38.0% [+19.6, +53.2] | +39.8% [+22.7, +54.1] | +3.0% [-0.4, +6.5] | +1.9% [-6.8, +7.9] | -1.2% [-7.5, +4.3] |

## without 2019-09-18

| group | days | B1 | B2 | gbm | aligned | twin | gbm vs B1 | aligned vs B1 | gbm vs B2 | aligned vs B2 | **aligned vs gbm** | twin vs gbm | aligned vs twin |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pooled | 1867 | 1.87 | 2.48 | 1.64 | 1.59 | 1.67 | +12.6% [+7.5, +18.5] | +15.0% [+9.7, +20.7] | +34.0% [+22.3, +42.8] | +35.8% [+23.8, +44.3] | +2.8% [+1.7, +3.8] | -2.0% [-4.5, +0.4] | -4.9% [-7.3, -2.6] |

### By target-day type

| group | days | B1 | B2 | gbm | aligned | twin | gbm vs B1 | aligned vs B1 | gbm vs B2 | aligned vs B2 | **aligned vs gbm** | twin vs gbm | aligned vs twin |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mid_month_coupon | 115 | 1.62 | 2.72 | 1.77 | 1.53 | 1.66 | -9.8% [-21.1, -2.0] | +5.3% [-8.4, +16.5] | +34.8% [+22.7, +50.2] | +43.8% [+33.8, +55.4] | +13.8% [+8.6, +21.5] | +6.3% [-1.0, +16.6] | -8.7% [-14.1, -3.2] |
| month_end | 149 | 2.11 | 2.91 | 1.92 | 1.66 | 1.72 | +8.9% [-0.4, +21.7] | +21.4% [+12.4, +34.9] | +33.8% [+14.8, +52.0] | +42.9% [+26.7, +58.2] | +13.8% [+11.1, +16.6] | +10.4% [+4.0, +16.2] | -3.9% [-8.8, +1.4] |
| ordinary | 1485 | 1.57 | 2.02 | 1.25 | 1.25 | 1.32 | +20.4% [+13.4, +29.3] | +20.3% [+13.1, +29.3] | +38.1% [+29.9, +46.1] | +38.0% [+30.0, +45.9] | -0.2% [-1.9, +1.3] | -5.6% [-9.6, -1.8] | -5.4% [-8.9, -2.0] |
| quarter_end | 29 | 6.14 | 7.28 | 6.75 | 6.48 | 6.85 | too thin | too thin | too thin | too thin | too thin | too thin | too thin |
| tax_date | 89 | 5.47 | 7.56 | 5.77 | 5.63 | 5.74 | -5.4% [-15.5, +2.1] | -2.9% [-15.8, +6.3] | +23.8% [-20.8, +48.3] | +25.5% [-22.9, +48.6] | +2.4% [-1.0, +7.4] | +0.5% [-8.2, +7.8] | -1.9% [-6.2, +1.8] |

### By regime of the decision day

| group | days | B1 | B2 | gbm | aligned | twin | gbm vs B1 | aligned vs B1 | gbm vs B2 | aligned vs B2 | **aligned vs gbm** | twin vs gbm | aligned vs twin |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2018-19 | 374 | 4.59 | 4.33 | 3.80 | 3.67 | 3.86 | +17.1% [+8.8, +28.1] | +20.2% [+10.7, +30.3] | +12.2% [-0.2, +24.9] | +15.4% [+0.9, +29.1] | +3.7% [+1.3, +5.8] | -1.4% [-4.4, +1.8] | -5.2% [-9.0, -2.1] |
| 2020 | 251 | 1.35 | 2.74 | 1.24 | 1.21 | 1.26 | +8.5% [-11.3, +22.0] | +10.4% [-9.2, +25.3] | +54.9% [+21.1, +72.0] | +55.9% [+23.5, +71.7] | +2.2% [-1.4, +4.9] | -2.0% [-11.2, +6.4] | -4.2% [-12.7, +2.5] |
| 2021-23 | 748 | 0.52 | 1.45 | 0.63 | 0.62 | 0.72 | -21.3% [-58.8, -4.5] | -20.2% [-58.8, -3.3] | +56.8% [+44.1, +68.7] | +57.2% [+44.3, +69.4] | +1.0% [-1.1, +2.9] | -14.5% [-21.1, -9.2] | -15.6% [-22.6, -10.0] |
| 2024 | 250 | 1.50 | 1.37 | 1.20 | 1.19 | 1.12 | +20.0% [+15.2, +26.0] | +21.0% [+16.6, +26.2] | +12.3% [+2.2, +22.4] | +13.5% [+2.6, +23.8] | +1.3% [-1.3, +3.5] | +7.3% [+3.0, +11.7] | +6.1% [+2.7, +9.8] |
| 2025-26 | 244 | 2.77 | 3.64 | 2.26 | 2.19 | 2.21 | +18.6% [+13.7, +24.3] | +21.1% [+15.3, +26.9] | +38.0% [+19.6, +53.2] | +39.8% [+22.7, +54.1] | +3.0% [-0.4, +6.5] | +1.9% [-6.8, +7.9] | -1.2% [-7.5, +4.3] |

## Question for Eleonora (marked; this PR settles nothing)

Does the declared candidate train `treasury_settlement` from the target's row at lead 1? The measurement above is development evidence, not a verdict,
and changes no published model, declaration or figure.
