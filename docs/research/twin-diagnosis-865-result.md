# Why the direct-pairs twin scores below gbm_funding (#865, H5): the shortfall is real, not a defect

Development data, a measurement and never a verdict (scoring protocol v1). Nothing is published or registered; the declared candidate stays one-step
`gbm_funding` (Eleonora's ruling on #825), no published model, declaration or figure moves, no day after 2025-12-31 and no locked day is scored.
Declaration (committed before any diagnostic score): `metadata/twin_diagnosis_865.json`. Script: `scripts/twin_diagnosis_865.py`. Evidence:
`docs/research/twin-diagnosis-865/score.json` and `alignment.json`.

## Answer

**No defect was found; the shortfall is real.** The twin is built as it should be (alignment below), and every difference between the arms other than the
training pairs is either intended or immaterial. The shortfall tracks how stale the training pairs are, and nothing else:

| lead | twin | training pairs one row fresher than the twin's | fresher still | control |
|---|---|---|---|---|
| 3 | k = 3 (twin): -5.5% vs control | k = 2: -3.2% [-7.2, +0.6] (43% of the gap closed) | k = 1: -0.5% [-3.4, +2.2] (91%) | 0 |
| 5 | k = 5 (twin): -7.0% vs control | k = 3: -3.0% [-8.2, +1.8] (57%) | k = 1: +0.9% [-2.0, +3.8] (113%) | 0 |

(Skills are of the arm over the control; k is the training lag, the as-of rule's horizon the training pairs are read at; the lead the arm is served at is
unchanged. `k = lead` is the twin. The control's training pairs are the freshest possible, one row before the target.) A model trained on pairs read as
stale as it is served does worse than one trained on fresher pairs, even though the fresher pairs mismatch the way it is served. That is a property of
this model on these days (the features are persistent levels, so a fresher pair is a cleaner example of the same map), not a bug in either arm.

## Triage (acceptance 1): every difference between the arms, read from the code at #825's merge commit

| difference | read from | verdict |
|---|---|---|
| training pairs: one-step (feature row = row before target) against direct (feature row = the as-of read at the target's decision instant, h + 1 rows before) | `ml.py` `_training_design`, `_direct_pairs` (about lines 2660 and 2769) | intended: the one thing under test |
| inputs and their lags: same regressors, same declared features (`live_record.published_features(h)`, spread_bps excluded); no spread-change lags (`spread_change_lags` unset), no volatility or ARX feature | `direct_twin_449.fitter`, `spread_distribution_634.walk_command`; the score refuses unequal `features` | intended (identical) |
| as-of rule per lead: serving reads `InformationRule(horizon=h)` for both arms; the twin trains with the same rule, the control trains on stored rows with no per-field rule (weekly reserves and TGA are the row's own value, not the stale read) | `baseline._fit_at_origin`, `ml.py` fit | intended: a consequence of the pairing, and the source of the training-lag effect above |
| lead 1 only: `treasury_settlement` is an input, announced a day ahead; the control trains it from the row before the target (the wrong day), the twin from the target's own row | `live_record.published_features`, `metadata/sources.json` | intended (a consequence of the pairing); the twin is ahead at lead 1 on month-end days |
| training window and sample: the twin trains no pair on the first h + 3 targets (no as-of read); the control does. Roughly 8 of 1,490 pairs at lead 5 | `ml._direct_pairs` | unclear, tested: arm `control_trim` (the control without those rows) scores +0.1% [-0.2, +0.6] against the control at lead 5: immaterial |
| refit grid, minimum history, seed, hyper-parameters, quantile grid, calibration (none), target alignment (the target is row t's spread at both) | `spread_distribution_634.walk` (21 days, 61 rows), `ml.fit_gradient_boosted_quantiles` defaults | intended (identical) |
| last training rows: the control's last one or two rows carry holes in the weekly fields (the frame is masked at the decision instant), imputed with the training mean; the twin reads older, complete values | `asof.InformationRule.frame` | intended; two rows of about 1,500 |

## Alignment (acceptance 2): named days

At every lead and on 2019-09-17, 2020-03-16, 2021-12-31, 2023-03-13 and 2025-12-12 the twin's pair for target d + h is read with its anchor h + 1 rows before the
target (the anchor is the last row whose spread the decision instant could see), both guards of `InformationRule.check` pass, and the only field read from a row
after the decision day is `treasury_settlement`, which is announced ahead (lead 1). The serving read is `information_set(dates, target)`, the same call that builds
the training pair. The table is at the end of this page; the script exits non-zero if any other field is read after the decision day.

## Where the shortfall is (acceptance 2)

By regime of the decision day, at the walked leads 2, 3 and 5 pooled: 2018-19 -5.9% [-11.5, -1.5], 2020 -8.8% [-29.6, +5.2], **2021-23 -20.1% [-30.9, -12.5]**, 2024 +9.8%
[-0.5, +19.6], 2025-26 -2.6% [-27.5, +13.8]. By half-year the twin is wholly below the control in 2019H2, 2021H1, 2021H2, 2022H1 and 2022H2 (2021H2: -38.6% [-53.9, -28.2]) and
wholly above it in 2024H2 (+13.6% [+4.4, +22.4]). By target-day type it loses on ordinary days and is level on month-ends (tables below). That is the pattern of #450 (the published
model against its twin) as well. The reproduction of #449's recorded per-lead skill is exact to rounding (first table).

## Remedy (acceptance 3)

None. There is no defect to fix, so no code of the models changed and no re-score of a fix is made. The twin is not a better candidate under any arm tried: no arm
that trains on pairs staler than the control's has a whole interval above the control's. The fresher arms (k = 1) are the control's equals, not better (+0.9% [-2.0, +3.8]).
Whether to do anything with the finding (for example to train gbm_funding on the freshest pairs deliberately and call that the design) is Eleonora's; the declared
candidate is unchanged (acceptance 5).

## The full tables

Skills are of the second forecast over the first named, positive favouring the second, with one-sided 95% bounds `[lower, upper]` from the studentized stationary bootstrap (block 10, seed 865; 10,000 draws on pooled and per-lead rows, 2,000 on splits). Pooled rows average leads 2, 3 and 5. Decision days 2018-06-29 to 2025-12-23 (1,868); panel `4ddc3882cd6d…`; grid CRPS in bp.

## Reproduction of #449

| lead | twin vs control here | recorded in #449 | difference |
|---|---|---|---|
| 2 | -5.8123% | -5.8123% | 5.90e-16 |
| 3 | -5.5162% | -5.5162% | -1.38e-15 |
| 5 | -7.0223% | -7.0223% | -9.71e-17 |

## all days

### Pooled over the walked leads and each lead alone

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 1868 | 1.863 | 1.978 | | -6.1% [-11.4, -1.5] | | | |
| 2 | 1868 | 1.768 | 1.871 | | -5.8% [-9.9, -2.3] | | | |
| 3 | 1868 | 1.859 | 1.962 | `gbm_funding_direct_k1` 1.869 | -5.5% [-10.7, -1.0] | -0.5% [-3.4, +2.2] | +4.7% [+2.5, +7.4] | 91% |
| 3 | 1868 | 1.859 | 1.962 | `gbm_funding_direct_k2` 1.918 | -5.5% [-10.7, -1.0] | -3.2% [-7.2, +0.6] | +2.2% [+0.7, +4.1] | 43% |
| 5 | 1868 | 1.962 | 2.100 | `gbm_funding_direct_k1` 1.945 | -7.0% [-14.2, -0.8] | +0.9% [-2.0, +3.8] | +7.4% [+3.8, +11.6] | 113% |
| 5 | 1868 | 1.962 | 2.100 | `gbm_funding_direct_k3` 2.022 | -7.0% [-14.2, -0.8] | -3.0% [-8.2, +1.8] | +3.7% [+1.5, +6.2] | 57% |
| 5 | 1868 | 1.962 | 2.100 | `gbm_funding_trim` 1.960 | -7.0% [-14.2, -0.8] | +0.1% [-0.2, +0.6] | +6.7% [+1.0, +12.6] | 102% |

### Target-day type: month_end

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 388 | 2.220 | 2.205 | | +0.6% [-9.4, +11.3] | | | |
| 2 | 149 | 2.053 | 2.068 | | -0.7% [-14.0, +13.0] | | | |
| 3 | 149 | 2.291 | 2.215 | `gbm_funding_direct_k1` 2.207 | +3.3% [-6.9, +16.6] | +3.7% [-2.9, +15.6] | +0.4% [-3.5, +4.2] | n/a |
| 3 | 149 | 2.291 | 2.215 | `gbm_funding_direct_k2` 2.184 | +3.3% [-6.9, +16.6] | +4.7% [-4.4, +19.1] | +1.4% [-1.8, +3.9] | n/a |
| 5 | 150 | 2.355 | 2.346 | `gbm_funding_direct_k1` 2.248 | +0.4% [-8.5, +14.9] | +4.6% [+0.6, +10.1] | +4.2% [-5.2, +9.5] | n/a |
| 5 | 150 | 2.355 | 2.346 | `gbm_funding_direct_k3` 2.286 | +0.4% [-8.5, +14.9] | +2.9% [-4.4, +13.6] | +2.6% [-2.0, +7.9] | n/a |
| 5 | 150 | 2.355 | 2.346 | `gbm_funding_trim` 2.355 | +0.4% [-8.5, +14.9] | +0.0% [-1.0, +1.0] | -0.4% [-18.4, +8.0] | n/a |

### Target-day type: ordinary

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 1868 | 1.540 | 1.662 | | -7.9% [-14.4, -2.0] | | | |
| 2 | 1601 | 1.424 | 1.516 | | -6.5% [-11.4, -1.8] | | | |
| 3 | 1601 | 1.494 | 1.600 | `gbm_funding_direct_k1` 1.510 | -7.1% [-13.3, -1.2] | -1.0% [-4.8, +2.5] | +5.6% [+2.7, +8.8] | 85% |
| 3 | 1601 | 1.494 | 1.600 | `gbm_funding_direct_k2` 1.559 | -7.1% [-13.3, -1.2] | -4.3% [-9.4, +0.7] | +2.5% [+0.5, +4.8] | 39% |
| 5 | 1599 | 1.591 | 1.733 | `gbm_funding_direct_k1` 1.585 | -8.9% [-17.1, -1.7] | +0.4% [-3.2, +3.8] | +8.5% [+4.6, +13.1] | 104% |
| 5 | 1599 | 1.591 | 1.733 | `gbm_funding_direct_k3` 1.658 | -8.9% [-17.1, -1.7] | -4.2% [-10.4, +1.5] | +4.4% [+1.7, +7.1] | 53% |
| 5 | 1599 | 1.591 | 1.733 | `gbm_funding_trim` 1.588 | -8.9% [-17.1, -1.7] | +0.2% [-0.3, +0.7] | +8.4% [+1.9, +15.0] | 102% |

### Target-day type: quarter_end

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 88 | 7.718 | 7.815 | | -1.3% [-7.0, +4.8] | | | |
| 2 | 29 | 6.969 | 7.698 | | too thin | | | |
| 3 | 29 | 7.796 | 7.904 | `gbm_funding_direct_k1` 7.823 | too thin | too thin | too thin | n/a |
| 3 | 29 | 7.796 | 7.904 | `gbm_funding_direct_k2` 7.882 | too thin | too thin | too thin | n/a |
| 5 | 30 | 8.366 | 7.843 | `gbm_funding_direct_k1` 7.966 | +6.2% [-4.0, +21.0] | +4.8% [+1.1, +10.1] | -1.6% [-16.0, +5.3] | n/a |
| 5 | 30 | 8.366 | 7.843 | `gbm_funding_direct_k3` 7.809 | +6.2% [-4.0, +21.0] | +6.7% [-1.8, +18.4] | +0.4% [-3.1, +2.5] | n/a |
| 5 | 30 | 8.366 | 7.843 | `gbm_funding_trim` 8.355 | +6.2% [-4.0, +21.0] | +0.1% [-0.5, +0.7] | -6.5% [-25.3, +3.8] | n/a |

### Target-day type: tax_date

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 179 | 5.738 | 6.147 | | -7.1% [-22.5, +2.6] | | | |
| 2 | 89 | 5.788 | 6.022 | | -4.0% [-9.8, +2.1] | | | |
| 3 | 89 | 5.774 | 6.122 | `gbm_funding_direct_k1` 5.834 | -6.0% [-16.6, +2.0] | -1.0% [-3.0, +1.9] | +4.7% [-1.8, +11.9] | 83% |
| 3 | 89 | 5.774 | 6.122 | `gbm_funding_direct_k2` 5.993 | -6.0% [-16.6, +2.0] | -3.8% [-9.7, +2.9] | +2.1% [-0.9, +5.2] | 37% |
| 5 | 89 | 5.806 | 6.345 | `gbm_funding_direct_k1` 5.862 | -9.3% [-26.3, +3.8] | -1.0% [-3.4, +1.1] | +7.6% [-4.1, +18.7] | 90% |
| 5 | 89 | 5.806 | 6.345 | `gbm_funding_direct_k3` 6.172 | -9.3% [-26.3, +3.8] | -6.3% [-17.3, +1.9] | +2.7% [-1.4, +7.9] | 32% |
| 5 | 89 | 5.806 | 6.345 | `gbm_funding_trim` 5.814 | -9.3% [-26.3, +3.8] | -0.1% [-0.3, +0.0] | +8.4% [-4.7, +21.8] | 98% |

### Regime of the decision day: 2018-19

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 375 | 4.041 | 4.278 | | -5.9% [-11.5, -1.5] | | | |
| 2 | 375 | 3.990 | 4.179 | | -4.7% [-9.7, -0.6] | | | |
| 3 | 375 | 4.056 | 4.286 | `gbm_funding_direct_k1` 4.106 | -5.7% [-11.2, -1.3] | -1.2% [-4.6, +1.7] | +4.2% [+1.7, +7.4] | 78% |
| 3 | 375 | 4.056 | 4.286 | `gbm_funding_direct_k2` 4.205 | -5.7% [-11.2, -1.3] | -3.7% [-8.2, +0.1] | +1.9% [-0.5, +4.9] | 35% |
| 5 | 375 | 4.076 | 4.369 | `gbm_funding_direct_k1` 4.114 | -7.2% [-15.1, -1.1] | -0.9% [-4.4, +2.0] | +5.8% [+1.7, +10.4] | 87% |
| 5 | 375 | 4.076 | 4.369 | `gbm_funding_direct_k3` 4.317 | -7.2% [-15.1, -1.1] | -5.9% [-12.1, -1.1] | +1.2% [-2.3, +4.3] | 18% |
| 5 | 375 | 4.076 | 4.369 | `gbm_funding_trim` 4.062 | -7.2% [-15.1, -1.1] | +0.3% [-0.3, +1.0] | +7.0% [+1.4, +13.6] | 105% |

### Regime of the decision day: 2020

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 251 | 1.447 | 1.574 | | -8.8% [-29.6, +5.2] | | | |
| 2 | 251 | 1.320 | 1.414 | | -7.2% [-25.3, +4.8] | | | |
| 3 | 251 | 1.429 | 1.559 | `gbm_funding_direct_k1` 1.388 | -9.1% [-30.6, +4.5] | +2.9% [-5.2, +8.4] | +11.0% [+3.4, +20.1] | 131% |
| 3 | 251 | 1.429 | 1.559 | `gbm_funding_direct_k2` 1.499 | -9.1% [-30.6, +4.5] | -4.9% [-20.9, +5.2] | +3.9% [-2.2, +9.6] | 46% |
| 5 | 251 | 1.593 | 1.749 | `gbm_funding_direct_k1` 1.534 | -9.8% [-33.0, +6.3] | +3.7% [-2.9, +8.3] | +12.3% [-0.3, +24.6] | 138% |
| 5 | 251 | 1.593 | 1.749 | `gbm_funding_direct_k3` 1.662 | -9.8% [-33.0, +6.3] | -4.3% [-23.0, +7.9] | +5.0% [-1.3, +12.4] | 56% |
| 5 | 251 | 1.593 | 1.749 | `gbm_funding_trim` 1.594 | -9.8% [-33.0, +6.3] | -0.1% [-0.9, +1.0] | +8.9% [-7.2, +26.5] | 99% |

### Regime of the decision day: 2021-23

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 748 | 0.732 | 0.879 | | -20.1% [-30.9, -12.5] | | | |
| 2 | 748 | 0.681 | 0.809 | | -18.8% [-28.9, -11.5] | | | |
| 3 | 748 | 0.724 | 0.855 | `gbm_funding_direct_k1` 0.811 | -18.2% [-29.6, -10.4] | -12.1% [-20.2, -6.4] | +5.2% [+0.3, +9.3] | 34% |
| 3 | 748 | 0.724 | 0.855 | `gbm_funding_direct_k2` 0.839 | -18.2% [-29.6, -10.4] | -16.0% [-25.8, -8.7] | +1.9% [-1.5, +4.6] | 12% |
| 5 | 748 | 0.791 | 0.973 | `gbm_funding_direct_k1` 0.863 | -23.0% [-34.2, -13.5] | -9.1% [-16.4, -3.5] | +11.3% [+6.6, +15.5] | 61% |
| 5 | 748 | 0.791 | 0.973 | `gbm_funding_direct_k3` 0.898 | -23.0% [-34.2, -13.5] | -13.5% [-23.8, -5.5] | +7.7% [+4.8, +11.0] | 41% |
| 5 | 748 | 0.791 | 0.973 | `gbm_funding_trim` 0.796 | -23.0% [-34.2, -13.5] | -0.6% [-1.6, +0.3] | +18.2% [+11.4, +25.0] | 97% |

### Regime of the decision day: 2024

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 250 | 1.454 | 1.312 | | +9.8% [-0.5, +19.6] | | | |
| 2 | 250 | 1.357 | 1.269 | | +6.5% [-1.6, +15.0] | | | |
| 3 | 250 | 1.470 | 1.305 | `gbm_funding_direct_k1` 1.345 | +11.2% [+1.6, +20.9] | +8.5% [+4.4, +13.6] | -3.1% [-10.4, +4.1] | n/a |
| 3 | 250 | 1.470 | 1.305 | `gbm_funding_direct_k2` 1.314 | +11.2% [+1.6, +20.9] | +10.6% [+2.8, +19.2] | -0.7% [-5.3, +3.7] | n/a |
| 5 | 250 | 1.534 | 1.361 | `gbm_funding_direct_k1` 1.381 | +11.3% [-3.3, +25.1] | +9.9% [+5.3, +17.1] | -1.5% [-12.2, +11.1] | n/a |
| 5 | 250 | 1.534 | 1.361 | `gbm_funding_direct_k3` 1.354 | +11.3% [-3.3, +25.1] | +11.7% [+2.4, +24.6] | +0.5% [-5.5, +6.7] | n/a |
| 5 | 250 | 1.534 | 1.361 | `gbm_funding_trim` 1.517 | +11.3% [-3.3, +25.1] | +1.1% [+0.4, +1.9] | -11.5% [-32.2, +5.2] | n/a |

### Regime of the decision day: 2025-26

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 244 | 2.833 | 2.908 | | -2.6% [-27.5, +13.8] | | | |
| 2 | 244 | 2.568 | 2.665 | | -3.8% [-19.8, +7.2] | | | |
| 3 | 244 | 2.808 | 2.871 | `gbm_funding_direct_k1` 2.706 | -2.3% [-26.3, +13.6] | +3.6% [-8.7, +12.4] | +5.7% [-1.3, +15.2] | 261% |
| 3 | 244 | 2.808 | 2.871 | `gbm_funding_direct_k2` 2.762 | -2.3% [-26.3, +13.6] | +1.6% [-16.2, +13.9] | +3.8% [-0.2, +9.5] | 173% |
| 5 | 244 | 3.123 | 3.186 | `gbm_funding_direct_k1` 2.925 | -2.0% [-35.4, +20.1] | +6.4% [-5.2, +15.4] | +8.2% [-5.7, +24.9] | 415% |
| 5 | 244 | 3.123 | 3.186 | `gbm_funding_direct_k3` 2.994 | -2.0% [-35.4, +20.1] | +4.1% [-18.2, +19.9] | +6.0% [-0.7, +15.0] | 305% |
| 5 | 244 | 3.123 | 3.186 | `gbm_funding_trim` 3.125 | -2.0% [-35.4, +20.1] | -0.0% [-1.2, +1.1] | +1.9% [-24.0, +27.7] | 98% |

### Half-year of the decision day: 2018H1

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 1 | 3.474 | 3.656 | | too thin | | | |
| 2 | 1 | 5.120 | 5.722 | | too thin | | | |
| 3 | 1 | 2.872 | 4.369 | `gbm_funding_direct_k1` 3.303 | too thin | too thin | too thin | n/a |
| 3 | 1 | 2.872 | 4.369 | `gbm_funding_direct_k2` 3.305 | too thin | too thin | too thin | n/a |
| 5 | 1 | 2.431 | 0.877 | `gbm_funding_direct_k1` 1.361 | too thin | too thin | too thin | n/a |
| 5 | 1 | 2.431 | 0.877 | `gbm_funding_direct_k3` 0.826 | too thin | too thin | too thin | n/a |
| 5 | 1 | 2.431 | 0.877 | `gbm_funding_trim` 3.312 | too thin | too thin | too thin | n/a |

### Half-year of the decision day: 2018H2

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 124 | 3.391 | 3.529 | | -4.1% [-19.0, +5.3] | | | |
| 2 | 124 | 3.367 | 3.427 | | -1.8% [-12.3, +5.3] | | | |
| 3 | 124 | 3.424 | 3.513 | `gbm_funding_direct_k1` 3.372 | -2.6% [-18.7, +8.6] | +1.5% [-6.0, +8.2] | +4.0% [-2.0, +12.2] | 158% |
| 3 | 124 | 3.424 | 3.513 | `gbm_funding_direct_k2` 3.453 | -2.6% [-18.7, +8.6] | -0.9% [-12.4, +7.4] | +1.7% [-2.5, +5.3] | 67% |
| 5 | 124 | 3.381 | 3.648 | `gbm_funding_direct_k1` 3.385 | -7.9% [-22.5, +3.5] | -0.1% [-8.1, +6.6] | +7.2% [+2.7, +11.7] | 98% |
| 5 | 124 | 3.381 | 3.648 | `gbm_funding_direct_k3` 3.586 | -7.9% [-22.5, +3.5] | -6.1% [-26.0, +7.3] | +1.7% [-3.3, +5.5] | 23% |
| 5 | 124 | 3.381 | 3.648 | `gbm_funding_trim` 3.345 | -7.9% [-22.5, +3.5] | +1.1% [+0.0, +3.0] | +8.3% [-2.1, +19.7] | 114% |

### Half-year of the decision day: 2019H1

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 124 | 2.959 | 3.236 | | -9.4% [-26.9, +6.3] | | | |
| 2 | 124 | 2.723 | 2.891 | | -6.1% [-18.9, +8.6] | | | |
| 3 | 124 | 2.970 | 3.165 | `gbm_funding_direct_k1` 3.010 | -6.6% [-21.5, +6.2] | -1.4% [-9.7, +7.5] | +4.9% [-2.3, +14.2] | 79% |
| 3 | 124 | 2.970 | 3.165 | `gbm_funding_direct_k2` 3.037 | -6.6% [-21.5, +6.2] | -2.2% [-13.1, +9.4] | +4.1% [-3.4, +15.3] | 66% |
| 5 | 124 | 3.184 | 3.653 | `gbm_funding_direct_k1` 3.188 | -14.7% [-43.7, +7.4] | -0.1% [-9.3, +8.6] | +12.7% [-2.1, +26.4] | 99% |
| 5 | 124 | 3.184 | 3.653 | `gbm_funding_direct_k3` 3.374 | -14.7% [-43.7, +7.4] | -6.0% [-25.6, +8.4] | +7.6% [-1.7, +13.8] | 59% |
| 5 | 124 | 3.184 | 3.653 | `gbm_funding_trim` 3.140 | -14.7% [-43.7, +7.4] | +1.4% [-0.4, +3.2] | +14.0% [-4.7, +32.2] | 109% |

### Half-year of the decision day: 2019H2

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 126 | 5.749 | 6.045 | | -5.1% [-9.4, -1.6] | | | |
| 2 | 126 | 5.841 | 6.175 | | -5.7% [-13.0, -0.1] | | | |
| 3 | 126 | 5.755 | 6.149 | `gbm_funding_direct_k1` 5.913 | -6.8% [-13.5, -1.0] | -2.7% [-7.2, +2.0] | +3.8% [+1.1, +7.5] | 60% |
| 3 | 126 | 5.755 | 6.149 | `gbm_funding_direct_k2` 6.101 | -6.8% [-13.5, -1.0] | -6.0% [-12.6, +0.2] | +0.8% [-1.6, +3.2] | 12% |
| 5 | 126 | 5.651 | 5.811 | `gbm_funding_direct_k1` 5.766 | -2.8% [-6.8, +1.3] | -2.0% [-6.9, +1.8] | +0.8% [-5.8, +6.7] | 28% |
| 5 | 126 | 5.651 | 5.811 | `gbm_funding_direct_k3` 5.992 | -2.8% [-6.8, +1.3] | -6.0% [-10.8, -1.7] | -3.1% [-10.4, +3.6] | -113% |
| 5 | 126 | 5.651 | 5.811 | `gbm_funding_trim` 5.682 | -2.8% [-6.8, +1.3] | -0.5% [-1.5, +0.2] | +2.2% [-2.3, +6.1] | 81% |

### Half-year of the decision day: 2020H1

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 125 | 2.133 | 2.323 | | -8.9% [-31.9, +8.7] | | | |
| 2 | 125 | 1.946 | 2.058 | | -5.8% [-25.0, +8.6] | | | |
| 3 | 125 | 2.099 | 2.303 | `gbm_funding_direct_k1` 2.021 | -9.7% [-30.4, +7.4] | +3.7% [-4.2, +10.2] | +12.2% [+1.6, +21.7] | 138% |
| 3 | 125 | 2.099 | 2.303 | `gbm_funding_direct_k2` 2.203 | -9.7% [-30.4, +7.4] | -5.0% [-20.6, +6.7] | +4.3% [-4.6, +12.1] | 49% |
| 5 | 125 | 2.354 | 2.609 | `gbm_funding_direct_k1` 2.286 | -10.8% [-40.2, +10.5] | +2.9% [-3.3, +8.5] | +12.4% [-4.8, +29.9] | 127% |
| 5 | 125 | 2.354 | 2.609 | `gbm_funding_direct_k3` 2.459 | -10.8% [-40.2, +10.5] | -4.5% [-22.6, +10.0] | +5.8% [-2.8, +16.8] | 59% |
| 5 | 125 | 2.354 | 2.609 | `gbm_funding_trim` 2.336 | -10.8% [-40.2, +10.5] | +0.8% [-0.6, +2.1] | +10.5% [-11.8, +32.3] | 107% |

### Half-year of the decision day: 2020H2

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 126 | 0.767 | 0.831 | | -8.3% [-52.9, +10.5] | | | |
| 2 | 126 | 0.699 | 0.775 | | -10.9% [-37.0, +4.5] | | | |
| 3 | 126 | 0.765 | 0.822 | `gbm_funding_direct_k1` 0.761 | -7.4% [-63.8, +13.5] | +0.6% [-14.0, +10.5] | +7.5% [-6.4, +27.0] | 108% |
| 3 | 126 | 0.765 | 0.822 | `gbm_funding_direct_k2` 0.801 | -7.4% [-63.8, +13.5] | -4.7% [-30.9, +11.2] | +2.6% [-6.5, +11.8] | 37% |
| 5 | 126 | 0.838 | 0.896 | `gbm_funding_direct_k1` 0.789 | -6.9% [-47.1, +14.6] | +5.9% [-8.0, +14.0] | +12.0% [-1.4, +27.8] | 185% |
| 5 | 126 | 0.838 | 0.896 | `gbm_funding_direct_k3` 0.871 | -6.9% [-47.1, +14.6] | -4.0% [-52.9, +15.0] | +2.8% [-2.8, +8.3] | 43% |
| 5 | 126 | 0.838 | 0.896 | `gbm_funding_trim` 0.858 | -6.9% [-47.1, +14.6] | -2.4% [-3.9, -0.8] | +4.3% [-18.7, +31.8] | 66% |

### Half-year of the decision day: 2021H1

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 124 | 0.755 | 1.002 | | -32.8% [-83.9, -3.5] | | | |
| 2 | 124 | 0.691 | 0.926 | | -34.1% [-80.7, -6.0] | | | |
| 3 | 124 | 0.733 | 0.998 | `gbm_funding_direct_k1` 0.888 | -36.1% [-93.0, -3.1] | -21.2% [-58.7, -0.8] | +11.0% [-8.4, +22.1] | 41% |
| 3 | 124 | 0.733 | 0.998 | `gbm_funding_direct_k2` 0.966 | -36.1% [-93.0, -3.1] | -31.8% [-85.4, -4.0] | +3.2% [-10.1, +9.1] | 12% |
| 5 | 124 | 0.841 | 1.083 | `gbm_funding_direct_k1` 0.954 | -28.9% [-74.0, +1.0] | -13.4% [-44.9, +7.2] | +12.0% [-4.1, +21.5] | 53% |
| 5 | 124 | 0.841 | 1.083 | `gbm_funding_direct_k3` 1.081 | -28.9% [-74.0, +1.0] | -28.6% [-73.7, +4.0] | +0.2% [-3.4, +4.0] | 1% |
| 5 | 124 | 0.841 | 1.083 | `gbm_funding_trim` 0.841 | -28.9% [-74.0, +1.0] | -0.0% [-2.1, +2.3] | +22.4% [+0.4, +42.3] | 100% |

### Half-year of the decision day: 2021H2

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 126 | 0.253 | 0.351 | | -38.6% [-53.9, -28.2] | | | |
| 2 | 126 | 0.252 | 0.328 | | -29.8% [-44.6, -17.0] | | | |
| 3 | 126 | 0.252 | 0.329 | `gbm_funding_direct_k1` 0.322 | -30.3% [-58.1, -11.4] | -27.4% [-42.4, -13.3] | +2.2% [-31.7, +23.1] | 10% |
| 3 | 126 | 0.252 | 0.329 | `gbm_funding_direct_k2` 0.328 | -30.3% [-58.1, -11.4] | -29.9% [-44.7, -17.1] | +0.3% [-34.2, +19.7] | 1% |
| 5 | 126 | 0.255 | 0.396 | `gbm_funding_direct_k1` 0.325 | -55.5% [-80.7, -31.7] | -27.6% [-42.7, -13.5] | +17.9% [-9.8, +33.2] | 50% |
| 5 | 126 | 0.255 | 0.396 | `gbm_funding_direct_k3` 0.331 | -55.5% [-80.7, -31.7] | -29.9% [-59.4, -11.7] | +16.5% [+4.2, +31.7] | 46% |
| 5 | 126 | 0.255 | 0.396 | `gbm_funding_trim` 0.255 | -55.5% [-80.7, -31.7] | +0.0% [-7.4, +5.1] | +35.7% [+26.5, +43.8] | 100% |

### Half-year of the decision day: 2022H1

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 124 | 1.200 | 1.519 | | -26.7% [-44.8, -7.9] | | | |
| 2 | 124 | 1.167 | 1.423 | | -22.0% [-42.2, -4.7] | | | |
| 3 | 124 | 1.200 | 1.481 | `gbm_funding_direct_k1` 1.390 | -23.4% [-39.1, -9.2] | -15.8% [-30.1, -2.2] | +6.1% [+2.1, +11.4] | 32% |
| 3 | 124 | 1.200 | 1.481 | `gbm_funding_direct_k2` 1.441 | -23.4% [-39.1, -9.2] | -20.1% [-38.6, -4.7] | +2.7% [-1.8, +6.5] | 14% |
| 5 | 124 | 1.232 | 1.655 | `gbm_funding_direct_k1` 1.420 | -34.3% [-59.5, -9.2] | -15.3% [-30.2, -2.4] | +14.2% [+6.7, +24.7] | 56% |
| 5 | 124 | 1.232 | 1.655 | `gbm_funding_direct_k3` 1.492 | -34.3% [-59.5, -9.2] | -21.1% [-36.5, -7.8] | +9.8% [+2.3, +18.1] | 38% |
| 5 | 124 | 1.232 | 1.655 | `gbm_funding_trim` 1.245 | -34.3% [-59.5, -9.2] | -1.0% [-3.5, +0.9] | +24.8% [+9.4, +38.1] | 97% |

### Half-year of the decision day: 2022H2

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 125 | 0.908 | 1.076 | | -18.5% [-43.2, -1.6] | | | |
| 2 | 125 | 0.832 | 1.009 | | -21.4% [-47.3, -3.8] | | | |
| 3 | 125 | 0.898 | 1.038 | `gbm_funding_direct_k1` 0.995 | -15.6% [-35.0, -2.9] | -10.9% [-35.4, +2.7] | +4.1% [-2.0, +10.1] | 31% |
| 3 | 125 | 0.898 | 1.038 | `gbm_funding_direct_k2` 1.048 | -15.6% [-35.0, -2.9] | -16.8% [-42.2, +1.2] | -1.0% [-7.3, +5.1] | -7% |
| 5 | 125 | 0.994 | 1.180 | `gbm_funding_direct_k1` 1.055 | -18.7% [-45.9, +1.6] | -6.1% [-29.2, +6.3] | +10.6% [+0.9, +16.8] | 67% |
| 5 | 125 | 0.994 | 1.180 | `gbm_funding_direct_k3` 1.089 | -18.7% [-45.9, +1.6] | -9.5% [-28.3, +3.6] | +7.7% [+2.2, +13.6] | 49% |
| 5 | 125 | 0.994 | 1.180 | `gbm_funding_trim` 1.001 | -18.7% [-45.9, +1.6] | -0.7% [-4.1, +1.9] | +15.2% [-1.0, +31.8] | 96% |

### Half-year of the decision day: 2023H1

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 124 | 0.503 | 0.528 | | -5.1% [-18.0, +7.6] | | | |
| 2 | 124 | 0.464 | 0.458 | | +1.1% [-6.1, +7.8] | | | |
| 3 | 124 | 0.492 | 0.486 | `gbm_funding_direct_k1` 0.492 | +1.0% [-9.9, +11.6] | -0.2% [-7.6, +6.2] | -1.2% [-8.6, +4.8] | n/a |
| 3 | 124 | 0.492 | 0.486 | `gbm_funding_direct_k2` 0.480 | +1.0% [-9.9, +11.6] | +2.3% [-5.8, +9.5] | +1.3% [-4.4, +9.1] | n/a |
| 5 | 124 | 0.553 | 0.640 | `gbm_funding_direct_k1` 0.548 | -15.6% [-41.5, +5.4] | +1.0% [-6.6, +9.6] | +14.4% [-0.5, +28.4] | 106% |
| 5 | 124 | 0.553 | 0.640 | `gbm_funding_direct_k3` 0.546 | -15.6% [-41.5, +5.4] | +1.2% [-11.8, +20.2] | +14.6% [+1.7, +25.7] | 108% |
| 5 | 124 | 0.553 | 0.640 | `gbm_funding_trim` 0.549 | -15.6% [-41.5, +5.4] | +0.7% [-1.8, +2.5] | +14.1% [-5.8, +30.0] | 105% |

### Half-year of the decision day: 2023H2

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 125 | 0.780 | 0.807 | | -3.5% [-20.4, +6.2] | | | |
| 2 | 125 | 0.688 | 0.719 | | -4.4% [-15.1, +5.3] | | | |
| 3 | 125 | 0.774 | 0.808 | `gbm_funding_direct_k1` 0.786 | -4.5% [-27.1, +7.2] | -1.6% [-11.5, +4.4] | +2.7% [-6.2, +11.8] | 64% |
| 3 | 125 | 0.774 | 0.808 | `gbm_funding_direct_k2` 0.779 | -4.5% [-27.1, +7.2] | -0.7% [-12.8, +7.6] | +3.6% [-1.5, +11.7] | 85% |
| 5 | 125 | 0.878 | 0.894 | `gbm_funding_direct_k1` 0.883 | -1.8% [-17.2, +10.9] | -0.6% [-7.2, +5.1] | +1.2% [-9.4, +9.6] | 67% |
| 5 | 125 | 0.878 | 0.894 | `gbm_funding_direct_k3` 0.856 | -1.8% [-17.2, +10.9] | +2.5% [-14.7, +14.2] | +4.2% [-2.3, +11.3] | 239% |
| 5 | 125 | 0.878 | 0.894 | `gbm_funding_trim` 0.892 | -1.8% [-17.2, +10.9] | -1.5% [-3.6, -0.2] | +0.3% [-14.8, +13.8] | 15% |

### Half-year of the decision day: 2024H1

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 124 | 0.700 | 0.717 | | -2.5% [-28.2, +19.5] | | | |
| 2 | 124 | 0.638 | 0.675 | | -5.7% [-32.8, +20.4] | | | |
| 3 | 124 | 0.692 | 0.722 | `gbm_funding_direct_k1` 0.667 | -4.4% [-28.1, +17.0] | +3.5% [-3.5, +10.4] | +7.6% [-9.0, +21.6] | 179% |
| 3 | 124 | 0.692 | 0.722 | `gbm_funding_direct_k2` 0.710 | -4.4% [-28.1, +17.0] | -2.7% [-25.9, +17.4] | +1.6% [-3.1, +5.8] | 38% |
| 5 | 124 | 0.770 | 0.755 | `gbm_funding_direct_k1` 0.733 | +2.0% [-26.3, +25.1] | +4.9% [-1.2, +12.1] | +3.0% [-19.2, +24.2] | n/a |
| 5 | 124 | 0.770 | 0.755 | `gbm_funding_direct_k3` 0.759 | +2.0% [-26.3, +25.1] | +1.4% [-16.9, +23.4] | -0.5% [-14.1, +8.7] | n/a |
| 5 | 124 | 0.770 | 0.755 | `gbm_funding_trim` 0.750 | +2.0% [-26.3, +25.1] | +2.6% [+0.5, +6.0] | +0.7% [-31.2, +26.4] | n/a |

### Half-year of the decision day: 2024H2

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 126 | 2.195 | 1.896 | | +13.6% [+4.4, +22.4] | | | |
| 2 | 126 | 2.065 | 1.854 | | +10.2% [+2.3, +18.8] | | | |
| 3 | 126 | 2.236 | 1.878 | `gbm_funding_direct_k1` 2.013 | +16.0% [+7.7, +24.5] | +10.0% [+6.2, +14.7] | -7.2% [-15.4, +0.7] | n/a |
| 3 | 126 | 2.236 | 1.878 | `gbm_funding_direct_k2` 1.908 | +16.0% [+7.7, +24.5] | +14.6% [+8.2, +21.6] | -1.6% [-8.2, +7.1] | n/a |
| 5 | 126 | 2.285 | 1.957 | `gbm_funding_direct_k1` 2.020 | +14.4% [-0.7, +27.5] | +11.6% [+7.2, +18.6] | -3.2% [-14.0, +10.8] | n/a |
| 5 | 126 | 2.285 | 1.957 | `gbm_funding_direct_k3` 1.940 | +14.4% [-0.7, +27.5] | +15.1% [+5.9, +27.1] | +0.9% [-5.5, +8.4] | n/a |
| 5 | 126 | 2.285 | 1.957 | `gbm_funding_trim` 2.271 | +14.4% [-0.7, +27.5] | +0.6% [-0.1, +1.3] | -16.1% [-36.5, +1.5] | n/a |

### Half-year of the decision day: 2025H1

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 123 | 2.352 | 2.076 | | +11.7% [-0.3, +24.0] | | | |
| 2 | 123 | 2.108 | 2.062 | | +2.2% [-8.1, +11.5] | | | |
| 3 | 123 | 2.307 | 2.097 | `gbm_funding_direct_k1` 2.117 | +9.1% [-2.2, +21.4] | +8.2% [-0.8, +16.2] | -1.0% [-6.8, +3.8] | n/a |
| 3 | 123 | 2.307 | 2.097 | `gbm_funding_direct_k2` 2.102 | +9.1% [-2.2, +21.4] | +8.9% [-2.6, +19.4] | -0.2% [-3.4, +2.7] | n/a |
| 5 | 123 | 2.642 | 2.070 | `gbm_funding_direct_k1` 2.299 | +21.7% [+6.2, +36.6] | +13.0% [+5.2, +19.4] | -11.1% [-28.8, +0.1] | n/a |
| 5 | 123 | 2.642 | 2.070 | `gbm_funding_direct_k3` 2.129 | +21.7% [+6.2, +36.6] | +19.4% [+7.3, +30.6] | -2.9% [-11.5, +2.1] | n/a |
| 5 | 123 | 2.642 | 2.070 | `gbm_funding_trim` 2.652 | +21.7% [+6.2, +36.6] | -0.4% [-2.3, +1.0] | -28.1% [-59.3, -5.5] | n/a |

### Half-year of the decision day: 2025H2

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 121 | 3.322 | 3.753 | | -13.0% [-47.3, +14.8] | | | |
| 2 | 121 | 3.036 | 3.279 | | -8.0% [-33.4, +11.0] | | | |
| 3 | 121 | 3.318 | 3.658 | `gbm_funding_direct_k1` 3.304 | -10.3% [-45.6, +16.8] | +0.4% [-17.5, +16.3] | +9.7% [-1.2, +21.5] | 104% |
| 3 | 121 | 3.318 | 3.658 | `gbm_funding_direct_k2` 3.432 | -10.3% [-45.6, +16.8] | -3.5% [-31.3, +17.4] | +6.2% [+0.1, +14.5] | 66% |
| 5 | 121 | 3.612 | 4.321 | `gbm_funding_direct_k1` 3.561 | -19.6% [-66.6, +15.9] | +1.4% [-14.0, +18.2] | +17.6% [+1.7, +37.4] | 107% |
| 5 | 121 | 3.612 | 4.321 | `gbm_funding_direct_k3` 3.873 | -19.6% [-66.6, +15.9] | -7.2% [-36.8, +19.6] | +10.4% [+0.7, +22.1] | 63% |
| 5 | 121 | 3.612 | 4.321 | `gbm_funding_trim` 3.605 | -19.6% [-66.6, +15.9] | +0.2% [-1.4, +2.2] | +16.6% [-14.3, +41.7] | 101% |

## without 2019-09-18

### Pooled over the walked leads and each lead alone

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 1867 | 1.862 | 1.976 | | -6.1% [-11.5, -1.5] | | | |
| 2 | 1867 | 1.768 | 1.872 | | -5.9% [-10.0, -2.3] | | | |
| 3 | 1867 | 1.858 | 1.963 | `gbm_funding_direct_k1` 1.869 | -5.6% [-10.9, -1.0] | -0.6% [-3.5, +2.2] | +4.8% [+2.5, +7.4] | 90% |
| 3 | 1867 | 1.858 | 1.963 | `gbm_funding_direct_k2` 1.919 | -5.6% [-10.9, -1.0] | -3.3% [-7.3, +0.5] | +2.2% [+0.7, +4.1] | 42% |
| 5 | 1867 | 1.960 | 2.095 | `gbm_funding_direct_k1` 1.942 | -6.9% [-14.1, -0.6] | +1.0% [-1.9, +3.8] | +7.3% [+3.7, +11.7] | 114% |
| 5 | 1867 | 1.960 | 2.095 | `gbm_funding_direct_k3` 2.017 | -6.9% [-14.1, -0.6] | -2.9% [-8.1, +2.0] | +3.7% [+1.4, +6.2] | 58% |
| 5 | 1867 | 1.960 | 2.095 | `gbm_funding_trim` 1.958 | -6.9% [-14.1, -0.6] | +0.1% [-0.2, +0.6] | +6.5% [+0.7, +12.6] | 102% |

### Target-day type: month_end

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 388 | 2.220 | 2.205 | | +0.6% [-9.4, +11.3] | | | |
| 2 | 149 | 2.053 | 2.068 | | -0.7% [-14.0, +13.0] | | | |
| 3 | 149 | 2.291 | 2.215 | `gbm_funding_direct_k1` 2.207 | +3.3% [-6.9, +16.6] | +3.7% [-2.9, +15.6] | +0.4% [-3.5, +4.2] | n/a |
| 3 | 149 | 2.291 | 2.215 | `gbm_funding_direct_k2` 2.184 | +3.3% [-6.9, +16.6] | +4.7% [-4.4, +19.1] | +1.4% [-1.8, +3.9] | n/a |
| 5 | 150 | 2.355 | 2.346 | `gbm_funding_direct_k1` 2.248 | +0.4% [-8.5, +14.9] | +4.6% [+0.6, +10.1] | +4.2% [-5.2, +9.5] | n/a |
| 5 | 150 | 2.355 | 2.346 | `gbm_funding_direct_k3` 2.286 | +0.4% [-8.5, +14.9] | +2.9% [-4.4, +13.6] | +2.6% [-2.0, +7.9] | n/a |
| 5 | 150 | 2.355 | 2.346 | `gbm_funding_trim` 2.355 | +0.4% [-8.5, +14.9] | +0.0% [-1.0, +1.0] | -0.4% [-18.4, +8.0] | n/a |

### Target-day type: ordinary

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 1867 | 1.539 | 1.660 | | -7.9% [-14.3, -2.1] | | | |
| 2 | 1600 | 1.423 | 1.517 | | -6.6% [-11.7, -1.9] | | | |
| 3 | 1600 | 1.493 | 1.600 | `gbm_funding_direct_k1` 1.509 | -7.2% [-13.9, -1.3] | -1.1% [-4.9, +2.6] | +5.7% [+2.8, +8.9] | 85% |
| 3 | 1600 | 1.493 | 1.600 | `gbm_funding_direct_k2` 1.559 | -7.2% [-13.9, -1.3] | -4.5% [-9.8, +0.4] | +2.6% [+0.5, +4.9] | 38% |
| 5 | 1598 | 1.589 | 1.726 | `gbm_funding_direct_k1` 1.581 | -8.7% [-17.0, -1.2] | +0.5% [-3.1, +3.9] | +8.4% [+4.1, +13.1] | 105% |
| 5 | 1598 | 1.589 | 1.726 | `gbm_funding_direct_k3` 1.651 | -8.7% [-17.0, -1.2] | -3.9% [-10.1, +1.8] | +4.4% [+1.7, +7.0] | 55% |
| 5 | 1598 | 1.589 | 1.726 | `gbm_funding_trim` 1.585 | -8.7% [-17.0, -1.2] | +0.2% [-0.3, +0.7] | +8.2% [+1.4, +14.9] | 103% |

### Target-day type: quarter_end

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 88 | 7.718 | 7.815 | | -1.3% [-7.0, +4.8] | | | |
| 2 | 29 | 6.969 | 7.698 | | too thin | | | |
| 3 | 29 | 7.796 | 7.904 | `gbm_funding_direct_k1` 7.823 | too thin | too thin | too thin | n/a |
| 3 | 29 | 7.796 | 7.904 | `gbm_funding_direct_k2` 7.882 | too thin | too thin | too thin | n/a |
| 5 | 30 | 8.366 | 7.843 | `gbm_funding_direct_k1` 7.966 | +6.2% [-4.0, +21.0] | +4.8% [+1.1, +10.1] | -1.6% [-16.0, +5.3] | n/a |
| 5 | 30 | 8.366 | 7.843 | `gbm_funding_direct_k3` 7.809 | +6.2% [-4.0, +21.0] | +6.7% [-1.8, +18.4] | +0.4% [-3.1, +2.5] | n/a |
| 5 | 30 | 8.366 | 7.843 | `gbm_funding_trim` 8.355 | +6.2% [-4.0, +21.0] | +0.1% [-0.5, +0.7] | -6.5% [-25.3, +3.8] | n/a |

### Target-day type: tax_date

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 179 | 5.738 | 6.147 | | -7.1% [-22.5, +2.6] | | | |
| 2 | 89 | 5.788 | 6.022 | | -4.0% [-9.8, +2.1] | | | |
| 3 | 89 | 5.774 | 6.122 | `gbm_funding_direct_k1` 5.834 | -6.0% [-16.6, +2.0] | -1.0% [-3.0, +1.9] | +4.7% [-1.8, +11.9] | 83% |
| 3 | 89 | 5.774 | 6.122 | `gbm_funding_direct_k2` 5.993 | -6.0% [-16.6, +2.0] | -3.8% [-9.7, +2.9] | +2.1% [-0.9, +5.2] | 37% |
| 5 | 89 | 5.806 | 6.345 | `gbm_funding_direct_k1` 5.862 | -9.3% [-26.3, +3.8] | -1.0% [-3.4, +1.1] | +7.6% [-4.1, +18.7] | 90% |
| 5 | 89 | 5.806 | 6.345 | `gbm_funding_direct_k3` 6.172 | -9.3% [-26.3, +3.8] | -6.3% [-17.3, +1.9] | +2.7% [-1.4, +7.9] | 32% |
| 5 | 89 | 5.806 | 6.345 | `gbm_funding_trim` 5.814 | -9.3% [-26.3, +3.8] | -0.1% [-0.3, +0.0] | +8.4% [-4.7, +21.8] | 98% |

### Regime of the decision day: 2018-19

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 374 | 4.040 | 4.277 | | -5.9% [-11.3, -1.6] | | | |
| 2 | 374 | 3.992 | 4.189 | | -4.9% [-9.8, -1.1] | | | |
| 3 | 374 | 4.056 | 4.295 | `gbm_funding_direct_k1` 4.111 | -5.9% [-11.1, -1.5] | -1.4% [-4.6, +1.5] | +4.3% [+1.7, +7.4] | 77% |
| 3 | 374 | 4.056 | 4.295 | `gbm_funding_direct_k2` 4.214 | -5.9% [-11.1, -1.5] | -3.9% [-8.3, -0.1] | +1.9% [-0.5, +4.9] | 34% |
| 5 | 374 | 4.072 | 4.348 | `gbm_funding_direct_k1` 4.105 | -6.8% [-14.8, -0.9] | -0.8% [-4.2, +2.1] | +5.6% [+1.6, +10.4] | 88% |
| 5 | 374 | 4.072 | 4.348 | `gbm_funding_direct_k3` 4.298 | -6.8% [-14.8, -0.9] | -5.5% [-11.7, -0.8] | +1.2% [-2.3, +4.4] | 18% |
| 5 | 374 | 4.072 | 4.348 | `gbm_funding_trim` 4.058 | -6.8% [-14.8, -0.9] | +0.3% [-0.2, +1.0] | +6.7% [+1.0, +13.4] | 105% |

### Regime of the decision day: 2020

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 251 | 1.447 | 1.574 | | -8.8% [-29.6, +5.2] | | | |
| 2 | 251 | 1.320 | 1.414 | | -7.2% [-25.3, +4.8] | | | |
| 3 | 251 | 1.429 | 1.559 | `gbm_funding_direct_k1` 1.388 | -9.1% [-30.6, +4.5] | +2.9% [-5.2, +8.4] | +11.0% [+3.4, +20.1] | 131% |
| 3 | 251 | 1.429 | 1.559 | `gbm_funding_direct_k2` 1.499 | -9.1% [-30.6, +4.5] | -4.9% [-20.9, +5.2] | +3.9% [-2.2, +9.6] | 46% |
| 5 | 251 | 1.593 | 1.749 | `gbm_funding_direct_k1` 1.534 | -9.8% [-33.0, +6.3] | +3.7% [-2.9, +8.3] | +12.3% [-0.3, +24.6] | 138% |
| 5 | 251 | 1.593 | 1.749 | `gbm_funding_direct_k3` 1.662 | -9.8% [-33.0, +6.3] | -4.3% [-23.0, +7.9] | +5.0% [-1.3, +12.4] | 56% |
| 5 | 251 | 1.593 | 1.749 | `gbm_funding_trim` 1.594 | -9.8% [-33.0, +6.3] | -0.1% [-0.9, +1.0] | +8.9% [-7.2, +26.5] | 99% |

### Regime of the decision day: 2021-23

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 748 | 0.732 | 0.879 | | -20.1% [-30.9, -12.5] | | | |
| 2 | 748 | 0.681 | 0.809 | | -18.8% [-28.9, -11.5] | | | |
| 3 | 748 | 0.724 | 0.855 | `gbm_funding_direct_k1` 0.811 | -18.2% [-29.6, -10.4] | -12.1% [-20.2, -6.4] | +5.2% [+0.3, +9.3] | 34% |
| 3 | 748 | 0.724 | 0.855 | `gbm_funding_direct_k2` 0.839 | -18.2% [-29.6, -10.4] | -16.0% [-25.8, -8.7] | +1.9% [-1.5, +4.6] | 12% |
| 5 | 748 | 0.791 | 0.973 | `gbm_funding_direct_k1` 0.863 | -23.0% [-34.2, -13.5] | -9.1% [-16.4, -3.5] | +11.3% [+6.6, +15.5] | 61% |
| 5 | 748 | 0.791 | 0.973 | `gbm_funding_direct_k3` 0.898 | -23.0% [-34.2, -13.5] | -13.5% [-23.8, -5.5] | +7.7% [+4.8, +11.0] | 41% |
| 5 | 748 | 0.791 | 0.973 | `gbm_funding_trim` 0.796 | -23.0% [-34.2, -13.5] | -0.6% [-1.6, +0.3] | +18.2% [+11.4, +25.0] | 97% |

### Regime of the decision day: 2024

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 250 | 1.454 | 1.312 | | +9.8% [-0.5, +19.6] | | | |
| 2 | 250 | 1.357 | 1.269 | | +6.5% [-1.6, +15.0] | | | |
| 3 | 250 | 1.470 | 1.305 | `gbm_funding_direct_k1` 1.345 | +11.2% [+1.6, +20.9] | +8.5% [+4.4, +13.6] | -3.1% [-10.4, +4.1] | n/a |
| 3 | 250 | 1.470 | 1.305 | `gbm_funding_direct_k2` 1.314 | +11.2% [+1.6, +20.9] | +10.6% [+2.8, +19.2] | -0.7% [-5.3, +3.7] | n/a |
| 5 | 250 | 1.534 | 1.361 | `gbm_funding_direct_k1` 1.381 | +11.3% [-3.3, +25.1] | +9.9% [+5.3, +17.1] | -1.5% [-12.2, +11.1] | n/a |
| 5 | 250 | 1.534 | 1.361 | `gbm_funding_direct_k3` 1.354 | +11.3% [-3.3, +25.1] | +11.7% [+2.4, +24.6] | +0.5% [-5.5, +6.7] | n/a |
| 5 | 250 | 1.534 | 1.361 | `gbm_funding_trim` 1.517 | +11.3% [-3.3, +25.1] | +1.1% [+0.4, +1.9] | -11.5% [-32.2, +5.2] | n/a |

### Regime of the decision day: 2025-26

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 244 | 2.833 | 2.908 | | -2.6% [-27.5, +13.8] | | | |
| 2 | 244 | 2.568 | 2.665 | | -3.8% [-19.8, +7.2] | | | |
| 3 | 244 | 2.808 | 2.871 | `gbm_funding_direct_k1` 2.706 | -2.3% [-26.3, +13.6] | +3.6% [-8.7, +12.4] | +5.7% [-1.3, +15.2] | 261% |
| 3 | 244 | 2.808 | 2.871 | `gbm_funding_direct_k2` 2.762 | -2.3% [-26.3, +13.6] | +1.6% [-16.2, +13.9] | +3.8% [-0.2, +9.5] | 173% |
| 5 | 244 | 3.123 | 3.186 | `gbm_funding_direct_k1` 2.925 | -2.0% [-35.4, +20.1] | +6.4% [-5.2, +15.4] | +8.2% [-5.7, +24.9] | 415% |
| 5 | 244 | 3.123 | 3.186 | `gbm_funding_direct_k3` 2.994 | -2.0% [-35.4, +20.1] | +4.1% [-18.2, +19.9] | +6.0% [-0.7, +15.0] | 305% |
| 5 | 244 | 3.123 | 3.186 | `gbm_funding_trim` 3.125 | -2.0% [-35.4, +20.1] | -0.0% [-1.2, +1.1] | +1.9% [-24.0, +27.7] | 98% |

### Half-year of the decision day: 2018H1

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 1 | 3.474 | 3.656 | | too thin | | | |
| 2 | 1 | 5.120 | 5.722 | | too thin | | | |
| 3 | 1 | 2.872 | 4.369 | `gbm_funding_direct_k1` 3.303 | too thin | too thin | too thin | n/a |
| 3 | 1 | 2.872 | 4.369 | `gbm_funding_direct_k2` 3.305 | too thin | too thin | too thin | n/a |
| 5 | 1 | 2.431 | 0.877 | `gbm_funding_direct_k1` 1.361 | too thin | too thin | too thin | n/a |
| 5 | 1 | 2.431 | 0.877 | `gbm_funding_direct_k3` 0.826 | too thin | too thin | too thin | n/a |
| 5 | 1 | 2.431 | 0.877 | `gbm_funding_trim` 3.312 | too thin | too thin | too thin | n/a |

### Half-year of the decision day: 2018H2

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 124 | 3.391 | 3.529 | | -4.1% [-19.0, +5.3] | | | |
| 2 | 124 | 3.367 | 3.427 | | -1.8% [-12.3, +5.3] | | | |
| 3 | 124 | 3.424 | 3.513 | `gbm_funding_direct_k1` 3.372 | -2.6% [-18.7, +8.6] | +1.5% [-6.0, +8.2] | +4.0% [-2.0, +12.2] | 158% |
| 3 | 124 | 3.424 | 3.513 | `gbm_funding_direct_k2` 3.453 | -2.6% [-18.7, +8.6] | -0.9% [-12.4, +7.4] | +1.7% [-2.5, +5.3] | 67% |
| 5 | 124 | 3.381 | 3.648 | `gbm_funding_direct_k1` 3.385 | -7.9% [-22.5, +3.5] | -0.1% [-8.1, +6.6] | +7.2% [+2.7, +11.7] | 98% |
| 5 | 124 | 3.381 | 3.648 | `gbm_funding_direct_k3` 3.586 | -7.9% [-22.5, +3.5] | -6.1% [-26.0, +7.3] | +1.7% [-3.3, +5.5] | 23% |
| 5 | 124 | 3.381 | 3.648 | `gbm_funding_trim` 3.345 | -7.9% [-22.5, +3.5] | +1.1% [+0.0, +3.0] | +8.3% [-2.1, +19.7] | 114% |

### Half-year of the decision day: 2019H1

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 124 | 2.959 | 3.236 | | -9.4% [-26.9, +6.3] | | | |
| 2 | 124 | 2.723 | 2.891 | | -6.1% [-18.9, +8.6] | | | |
| 3 | 124 | 2.970 | 3.165 | `gbm_funding_direct_k1` 3.010 | -6.6% [-21.5, +6.2] | -1.4% [-9.7, +7.5] | +4.9% [-2.3, +14.2] | 79% |
| 3 | 124 | 2.970 | 3.165 | `gbm_funding_direct_k2` 3.037 | -6.6% [-21.5, +6.2] | -2.2% [-13.1, +9.4] | +4.1% [-3.4, +15.3] | 66% |
| 5 | 124 | 3.184 | 3.653 | `gbm_funding_direct_k1` 3.188 | -14.7% [-43.7, +7.4] | -0.1% [-9.3, +8.6] | +12.7% [-2.1, +26.4] | 99% |
| 5 | 124 | 3.184 | 3.653 | `gbm_funding_direct_k3` 3.374 | -14.7% [-43.7, +7.4] | -6.0% [-25.6, +8.4] | +7.6% [-1.7, +13.8] | 59% |
| 5 | 124 | 3.184 | 3.653 | `gbm_funding_trim` 3.140 | -14.7% [-43.7, +7.4] | +1.4% [-0.4, +3.2] | +14.0% [-4.7, +32.2] | 109% |

### Half-year of the decision day: 2019H2

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 125 | 5.761 | 6.058 | | -5.2% [-9.7, -1.4] | | | |
| 2 | 125 | 5.862 | 6.219 | | -6.1% [-13.6, -0.4] | | | |
| 3 | 125 | 5.769 | 6.193 | `gbm_funding_direct_k1` 5.943 | -7.3% [-13.9, -1.2] | -3.0% [-7.5, +1.5] | +4.0% [+1.3, +7.8] | 59% |
| 3 | 125 | 5.769 | 6.193 | `gbm_funding_direct_k2` 6.142 | -7.3% [-13.9, -1.2] | -6.5% [-13.2, -0.1] | +0.8% [-1.6, +3.3] | 12% |
| 5 | 125 | 5.651 | 5.760 | `gbm_funding_direct_k1` 5.750 | -1.9% [-5.7, +2.3] | -1.8% [-6.9, +2.5] | +0.2% [-6.9, +6.0] | 9% |
| 5 | 125 | 5.651 | 5.760 | `gbm_funding_direct_k3` 5.947 | -1.9% [-5.7, +2.3] | -5.2% [-10.5, -0.6] | -3.2% [-11.2, +3.7] | -170% |
| 5 | 125 | 5.651 | 5.760 | `gbm_funding_trim` 5.682 | -1.9% [-5.7, +2.3] | -0.6% [-1.5, +0.2] | +1.4% [-3.4, +5.0] | 71% |

### Half-year of the decision day: 2020H1

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 125 | 2.133 | 2.323 | | -8.9% [-31.9, +8.7] | | | |
| 2 | 125 | 1.946 | 2.058 | | -5.8% [-25.0, +8.6] | | | |
| 3 | 125 | 2.099 | 2.303 | `gbm_funding_direct_k1` 2.021 | -9.7% [-30.4, +7.4] | +3.7% [-4.2, +10.2] | +12.2% [+1.6, +21.7] | 138% |
| 3 | 125 | 2.099 | 2.303 | `gbm_funding_direct_k2` 2.203 | -9.7% [-30.4, +7.4] | -5.0% [-20.6, +6.7] | +4.3% [-4.6, +12.1] | 49% |
| 5 | 125 | 2.354 | 2.609 | `gbm_funding_direct_k1` 2.286 | -10.8% [-40.2, +10.5] | +2.9% [-3.3, +8.5] | +12.4% [-4.8, +29.9] | 127% |
| 5 | 125 | 2.354 | 2.609 | `gbm_funding_direct_k3` 2.459 | -10.8% [-40.2, +10.5] | -4.5% [-22.6, +10.0] | +5.8% [-2.8, +16.8] | 59% |
| 5 | 125 | 2.354 | 2.609 | `gbm_funding_trim` 2.336 | -10.8% [-40.2, +10.5] | +0.8% [-0.6, +2.1] | +10.5% [-11.8, +32.3] | 107% |

### Half-year of the decision day: 2020H2

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 126 | 0.767 | 0.831 | | -8.3% [-52.9, +10.5] | | | |
| 2 | 126 | 0.699 | 0.775 | | -10.9% [-37.0, +4.5] | | | |
| 3 | 126 | 0.765 | 0.822 | `gbm_funding_direct_k1` 0.761 | -7.4% [-63.8, +13.5] | +0.6% [-14.0, +10.5] | +7.5% [-6.4, +27.0] | 108% |
| 3 | 126 | 0.765 | 0.822 | `gbm_funding_direct_k2` 0.801 | -7.4% [-63.8, +13.5] | -4.7% [-30.9, +11.2] | +2.6% [-6.5, +11.8] | 37% |
| 5 | 126 | 0.838 | 0.896 | `gbm_funding_direct_k1` 0.789 | -6.9% [-47.1, +14.6] | +5.9% [-8.0, +14.0] | +12.0% [-1.4, +27.8] | 185% |
| 5 | 126 | 0.838 | 0.896 | `gbm_funding_direct_k3` 0.871 | -6.9% [-47.1, +14.6] | -4.0% [-52.9, +15.0] | +2.8% [-2.8, +8.3] | 43% |
| 5 | 126 | 0.838 | 0.896 | `gbm_funding_trim` 0.858 | -6.9% [-47.1, +14.6] | -2.4% [-3.9, -0.8] | +4.3% [-18.7, +31.8] | 66% |

### Half-year of the decision day: 2021H1

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 124 | 0.755 | 1.002 | | -32.8% [-83.9, -3.5] | | | |
| 2 | 124 | 0.691 | 0.926 | | -34.1% [-80.7, -6.0] | | | |
| 3 | 124 | 0.733 | 0.998 | `gbm_funding_direct_k1` 0.888 | -36.1% [-93.0, -3.1] | -21.2% [-58.7, -0.8] | +11.0% [-8.4, +22.1] | 41% |
| 3 | 124 | 0.733 | 0.998 | `gbm_funding_direct_k2` 0.966 | -36.1% [-93.0, -3.1] | -31.8% [-85.4, -4.0] | +3.2% [-10.1, +9.1] | 12% |
| 5 | 124 | 0.841 | 1.083 | `gbm_funding_direct_k1` 0.954 | -28.9% [-74.0, +1.0] | -13.4% [-44.9, +7.2] | +12.0% [-4.1, +21.5] | 53% |
| 5 | 124 | 0.841 | 1.083 | `gbm_funding_direct_k3` 1.081 | -28.9% [-74.0, +1.0] | -28.6% [-73.7, +4.0] | +0.2% [-3.4, +4.0] | 1% |
| 5 | 124 | 0.841 | 1.083 | `gbm_funding_trim` 0.841 | -28.9% [-74.0, +1.0] | -0.0% [-2.1, +2.3] | +22.4% [+0.4, +42.3] | 100% |

### Half-year of the decision day: 2021H2

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 126 | 0.253 | 0.351 | | -38.6% [-53.9, -28.2] | | | |
| 2 | 126 | 0.252 | 0.328 | | -29.8% [-44.6, -17.0] | | | |
| 3 | 126 | 0.252 | 0.329 | `gbm_funding_direct_k1` 0.322 | -30.3% [-58.1, -11.4] | -27.4% [-42.4, -13.3] | +2.2% [-31.7, +23.1] | 10% |
| 3 | 126 | 0.252 | 0.329 | `gbm_funding_direct_k2` 0.328 | -30.3% [-58.1, -11.4] | -29.9% [-44.7, -17.1] | +0.3% [-34.2, +19.7] | 1% |
| 5 | 126 | 0.255 | 0.396 | `gbm_funding_direct_k1` 0.325 | -55.5% [-80.7, -31.7] | -27.6% [-42.7, -13.5] | +17.9% [-9.8, +33.2] | 50% |
| 5 | 126 | 0.255 | 0.396 | `gbm_funding_direct_k3` 0.331 | -55.5% [-80.7, -31.7] | -29.9% [-59.4, -11.7] | +16.5% [+4.2, +31.7] | 46% |
| 5 | 126 | 0.255 | 0.396 | `gbm_funding_trim` 0.255 | -55.5% [-80.7, -31.7] | +0.0% [-7.4, +5.1] | +35.7% [+26.5, +43.8] | 100% |

### Half-year of the decision day: 2022H1

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 124 | 1.200 | 1.519 | | -26.7% [-44.8, -7.9] | | | |
| 2 | 124 | 1.167 | 1.423 | | -22.0% [-42.2, -4.7] | | | |
| 3 | 124 | 1.200 | 1.481 | `gbm_funding_direct_k1` 1.390 | -23.4% [-39.1, -9.2] | -15.8% [-30.1, -2.2] | +6.1% [+2.1, +11.4] | 32% |
| 3 | 124 | 1.200 | 1.481 | `gbm_funding_direct_k2` 1.441 | -23.4% [-39.1, -9.2] | -20.1% [-38.6, -4.7] | +2.7% [-1.8, +6.5] | 14% |
| 5 | 124 | 1.232 | 1.655 | `gbm_funding_direct_k1` 1.420 | -34.3% [-59.5, -9.2] | -15.3% [-30.2, -2.4] | +14.2% [+6.7, +24.7] | 56% |
| 5 | 124 | 1.232 | 1.655 | `gbm_funding_direct_k3` 1.492 | -34.3% [-59.5, -9.2] | -21.1% [-36.5, -7.8] | +9.8% [+2.3, +18.1] | 38% |
| 5 | 124 | 1.232 | 1.655 | `gbm_funding_trim` 1.245 | -34.3% [-59.5, -9.2] | -1.0% [-3.5, +0.9] | +24.8% [+9.4, +38.1] | 97% |

### Half-year of the decision day: 2022H2

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 125 | 0.908 | 1.076 | | -18.5% [-43.2, -1.6] | | | |
| 2 | 125 | 0.832 | 1.009 | | -21.4% [-47.3, -3.8] | | | |
| 3 | 125 | 0.898 | 1.038 | `gbm_funding_direct_k1` 0.995 | -15.6% [-35.0, -2.9] | -10.9% [-35.4, +2.7] | +4.1% [-2.0, +10.1] | 31% |
| 3 | 125 | 0.898 | 1.038 | `gbm_funding_direct_k2` 1.048 | -15.6% [-35.0, -2.9] | -16.8% [-42.2, +1.2] | -1.0% [-7.3, +5.1] | -7% |
| 5 | 125 | 0.994 | 1.180 | `gbm_funding_direct_k1` 1.055 | -18.7% [-45.9, +1.6] | -6.1% [-29.2, +6.3] | +10.6% [+0.9, +16.8] | 67% |
| 5 | 125 | 0.994 | 1.180 | `gbm_funding_direct_k3` 1.089 | -18.7% [-45.9, +1.6] | -9.5% [-28.3, +3.6] | +7.7% [+2.2, +13.6] | 49% |
| 5 | 125 | 0.994 | 1.180 | `gbm_funding_trim` 1.001 | -18.7% [-45.9, +1.6] | -0.7% [-4.1, +1.9] | +15.2% [-1.0, +31.8] | 96% |

### Half-year of the decision day: 2023H1

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 124 | 0.503 | 0.528 | | -5.1% [-18.0, +7.6] | | | |
| 2 | 124 | 0.464 | 0.458 | | +1.1% [-6.1, +7.8] | | | |
| 3 | 124 | 0.492 | 0.486 | `gbm_funding_direct_k1` 0.492 | +1.0% [-9.9, +11.6] | -0.2% [-7.6, +6.2] | -1.2% [-8.6, +4.8] | n/a |
| 3 | 124 | 0.492 | 0.486 | `gbm_funding_direct_k2` 0.480 | +1.0% [-9.9, +11.6] | +2.3% [-5.8, +9.5] | +1.3% [-4.4, +9.1] | n/a |
| 5 | 124 | 0.553 | 0.640 | `gbm_funding_direct_k1` 0.548 | -15.6% [-41.5, +5.4] | +1.0% [-6.6, +9.6] | +14.4% [-0.5, +28.4] | 106% |
| 5 | 124 | 0.553 | 0.640 | `gbm_funding_direct_k3` 0.546 | -15.6% [-41.5, +5.4] | +1.2% [-11.8, +20.2] | +14.6% [+1.7, +25.7] | 108% |
| 5 | 124 | 0.553 | 0.640 | `gbm_funding_trim` 0.549 | -15.6% [-41.5, +5.4] | +0.7% [-1.8, +2.5] | +14.1% [-5.8, +30.0] | 105% |

### Half-year of the decision day: 2023H2

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 125 | 0.780 | 0.807 | | -3.5% [-20.4, +6.2] | | | |
| 2 | 125 | 0.688 | 0.719 | | -4.4% [-15.1, +5.3] | | | |
| 3 | 125 | 0.774 | 0.808 | `gbm_funding_direct_k1` 0.786 | -4.5% [-27.1, +7.2] | -1.6% [-11.5, +4.4] | +2.7% [-6.2, +11.8] | 64% |
| 3 | 125 | 0.774 | 0.808 | `gbm_funding_direct_k2` 0.779 | -4.5% [-27.1, +7.2] | -0.7% [-12.8, +7.6] | +3.6% [-1.5, +11.7] | 85% |
| 5 | 125 | 0.878 | 0.894 | `gbm_funding_direct_k1` 0.883 | -1.8% [-17.2, +10.9] | -0.6% [-7.2, +5.1] | +1.2% [-9.4, +9.6] | 67% |
| 5 | 125 | 0.878 | 0.894 | `gbm_funding_direct_k3` 0.856 | -1.8% [-17.2, +10.9] | +2.5% [-14.7, +14.2] | +4.2% [-2.3, +11.3] | 239% |
| 5 | 125 | 0.878 | 0.894 | `gbm_funding_trim` 0.892 | -1.8% [-17.2, +10.9] | -1.5% [-3.6, -0.2] | +0.3% [-14.8, +13.8] | 15% |

### Half-year of the decision day: 2024H1

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 124 | 0.700 | 0.717 | | -2.5% [-28.2, +19.5] | | | |
| 2 | 124 | 0.638 | 0.675 | | -5.7% [-32.8, +20.4] | | | |
| 3 | 124 | 0.692 | 0.722 | `gbm_funding_direct_k1` 0.667 | -4.4% [-28.1, +17.0] | +3.5% [-3.5, +10.4] | +7.6% [-9.0, +21.6] | 179% |
| 3 | 124 | 0.692 | 0.722 | `gbm_funding_direct_k2` 0.710 | -4.4% [-28.1, +17.0] | -2.7% [-25.9, +17.4] | +1.6% [-3.1, +5.8] | 38% |
| 5 | 124 | 0.770 | 0.755 | `gbm_funding_direct_k1` 0.733 | +2.0% [-26.3, +25.1] | +4.9% [-1.2, +12.1] | +3.0% [-19.2, +24.2] | n/a |
| 5 | 124 | 0.770 | 0.755 | `gbm_funding_direct_k3` 0.759 | +2.0% [-26.3, +25.1] | +1.4% [-16.9, +23.4] | -0.5% [-14.1, +8.7] | n/a |
| 5 | 124 | 0.770 | 0.755 | `gbm_funding_trim` 0.750 | +2.0% [-26.3, +25.1] | +2.6% [+0.5, +6.0] | +0.7% [-31.2, +26.4] | n/a |

### Half-year of the decision day: 2024H2

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 126 | 2.195 | 1.896 | | +13.6% [+4.4, +22.4] | | | |
| 2 | 126 | 2.065 | 1.854 | | +10.2% [+2.3, +18.8] | | | |
| 3 | 126 | 2.236 | 1.878 | `gbm_funding_direct_k1` 2.013 | +16.0% [+7.7, +24.5] | +10.0% [+6.2, +14.7] | -7.2% [-15.4, +0.7] | n/a |
| 3 | 126 | 2.236 | 1.878 | `gbm_funding_direct_k2` 1.908 | +16.0% [+7.7, +24.5] | +14.6% [+8.2, +21.6] | -1.6% [-8.2, +7.1] | n/a |
| 5 | 126 | 2.285 | 1.957 | `gbm_funding_direct_k1` 2.020 | +14.4% [-0.7, +27.5] | +11.6% [+7.2, +18.6] | -3.2% [-14.0, +10.8] | n/a |
| 5 | 126 | 2.285 | 1.957 | `gbm_funding_direct_k3` 1.940 | +14.4% [-0.7, +27.5] | +15.1% [+5.9, +27.1] | +0.9% [-5.5, +8.4] | n/a |
| 5 | 126 | 2.285 | 1.957 | `gbm_funding_trim` 2.271 | +14.4% [-0.7, +27.5] | +0.6% [-0.1, +1.3] | -16.1% [-36.5, +1.5] | n/a |

### Half-year of the decision day: 2025H1

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 123 | 2.352 | 2.076 | | +11.7% [-0.3, +24.0] | | | |
| 2 | 123 | 2.108 | 2.062 | | +2.2% [-8.1, +11.5] | | | |
| 3 | 123 | 2.307 | 2.097 | `gbm_funding_direct_k1` 2.117 | +9.1% [-2.2, +21.4] | +8.2% [-0.8, +16.2] | -1.0% [-6.8, +3.8] | n/a |
| 3 | 123 | 2.307 | 2.097 | `gbm_funding_direct_k2` 2.102 | +9.1% [-2.2, +21.4] | +8.9% [-2.6, +19.4] | -0.2% [-3.4, +2.7] | n/a |
| 5 | 123 | 2.642 | 2.070 | `gbm_funding_direct_k1` 2.299 | +21.7% [+6.2, +36.6] | +13.0% [+5.2, +19.4] | -11.1% [-28.8, +0.1] | n/a |
| 5 | 123 | 2.642 | 2.070 | `gbm_funding_direct_k3` 2.129 | +21.7% [+6.2, +36.6] | +19.4% [+7.3, +30.6] | -2.9% [-11.5, +2.1] | n/a |
| 5 | 123 | 2.642 | 2.070 | `gbm_funding_trim` 2.652 | +21.7% [+6.2, +36.6] | -0.4% [-2.3, +1.0] | -28.1% [-59.3, -5.5] | n/a |

### Half-year of the decision day: 2025H2

| lead | days | control | twin | arm | twin vs control | arm vs control | arm vs twin | gap closed |
|---|---|---|---|---|---|---|---|---|
| pooled | 121 | 3.322 | 3.753 | | -13.0% [-47.3, +14.8] | | | |
| 2 | 121 | 3.036 | 3.279 | | -8.0% [-33.4, +11.0] | | | |
| 3 | 121 | 3.318 | 3.658 | `gbm_funding_direct_k1` 3.304 | -10.3% [-45.6, +16.8] | +0.4% [-17.5, +16.3] | +9.7% [-1.2, +21.5] | 104% |
| 3 | 121 | 3.318 | 3.658 | `gbm_funding_direct_k2` 3.432 | -10.3% [-45.6, +16.8] | -3.5% [-31.3, +17.4] | +6.2% [+0.1, +14.5] | 66% |
| 5 | 121 | 3.612 | 4.321 | `gbm_funding_direct_k1` 3.561 | -19.6% [-66.6, +15.9] | +1.4% [-14.0, +18.2] | +17.6% [+1.7, +37.4] | 107% |
| 5 | 121 | 3.612 | 4.321 | `gbm_funding_direct_k3` 3.873 | -19.6% [-66.6, +15.9] | -7.2% [-36.8, +19.6] | +10.4% [+0.7, +22.1] | 63% |
| 5 | 121 | 3.612 | 4.321 | `gbm_funding_trim` 3.605 | -19.6% [-66.6, +15.9] | +0.2% [-1.4, +2.2] | +16.6% [-14.3, +41.7] | 101% |

## The alignment check on named days

The twin's lead-h training pair for target d + h, read by `asof.InformationRule(horizon=h)` and checked by both guards.

| decision day d | lead | target | anchor | rows from anchor to target | latest read | fields read after the decision day |
|---|---|---|---|---|---|---|
| 2019-09-17 | 1 | 2019-09-18 | 2019-09-16 | 2 | 2019-09-18 | treasury_settlement |
| 2020-03-16 | 1 | 2020-03-17 | 2020-03-13 | 2 | 2020-03-17 | treasury_settlement |
| 2021-12-31 | 1 | 2022-01-03 | 2021-12-30 | 2 | 2022-01-03 | treasury_settlement |
| 2023-03-13 | 1 | 2023-03-14 | 2023-03-10 | 2 | 2023-03-14 | treasury_settlement |
| 2025-12-12 | 1 | 2025-12-15 | 2025-12-11 | 2 | 2025-12-15 | treasury_settlement |
| 2019-09-17 | 2 | 2019-09-19 | 2019-09-16 | 3 | 2019-09-16 | none |
| 2020-03-16 | 2 | 2020-03-18 | 2020-03-13 | 3 | 2020-03-13 | none |
| 2021-12-31 | 2 | 2022-01-04 | 2021-12-30 | 3 | 2021-12-30 | none |
| 2023-03-13 | 2 | 2023-03-15 | 2023-03-10 | 3 | 2023-03-10 | none |
| 2025-12-12 | 2 | 2025-12-16 | 2025-12-11 | 3 | 2025-12-11 | none |
| 2019-09-17 | 3 | 2019-09-20 | 2019-09-16 | 4 | 2019-09-16 | none |
| 2020-03-16 | 3 | 2020-03-19 | 2020-03-13 | 4 | 2020-03-13 | none |
| 2021-12-31 | 3 | 2022-01-05 | 2021-12-30 | 4 | 2021-12-30 | none |
| 2023-03-13 | 3 | 2023-03-16 | 2023-03-10 | 4 | 2023-03-10 | none |
| 2025-12-12 | 3 | 2025-12-17 | 2025-12-11 | 4 | 2025-12-11 | none |
| 2019-09-17 | 4 | 2019-09-23 | 2019-09-16 | 5 | 2019-09-16 | none |
| 2020-03-16 | 4 | 2020-03-20 | 2020-03-13 | 5 | 2020-03-13 | none |
| 2021-12-31 | 4 | 2022-01-06 | 2021-12-30 | 5 | 2021-12-30 | none |
| 2023-03-13 | 4 | 2023-03-17 | 2023-03-10 | 5 | 2023-03-10 | none |
| 2025-12-12 | 4 | 2025-12-18 | 2025-12-11 | 5 | 2025-12-11 | none |
| 2019-09-17 | 5 | 2019-09-24 | 2019-09-16 | 6 | 2019-09-16 | none |
| 2020-03-16 | 5 | 2020-03-23 | 2020-03-13 | 6 | 2020-03-13 | none |
| 2021-12-31 | 5 | 2022-01-07 | 2021-12-30 | 6 | 2021-12-30 | none |
| 2023-03-13 | 5 | 2023-03-20 | 2023-03-10 | 6 | 2023-03-10 | none |
| 2025-12-12 | 5 | 2025-12-19 | 2025-12-11 | 6 | 2025-12-11 | none |
