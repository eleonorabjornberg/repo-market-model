# Stacked ensemble of the track forecasts (#410, track X of #374)

A scratch measurement under the pressure-day judge as amended by #407 (each flag cut-off chosen from the refit's training
window alone). Scored days 2018-06-29 to 2025-12-31, h = 1 to 5, +5 bp primary, 90% stationary-bootstrap intervals. No
comparison scores a locked day (`docs/decisions/lockbox.md`); the confirmation window is not looked at. It writes nothing
into `docs/runs/` and moves no published figure. Declared before any score in `metadata/pressure_stack.json`
(commit `070f39f`, before any member forecast was stacked).

**The stack.** A logistic regression of the +5 / +10 bp pressure label on the logits of five members' probabilities, refitted
at the judge's blocks (every 21 scored days) on the earlier blocks' days whose outcome was public at the block's first decision
instant (the cut-off rule's training end, `pressure_judge.choose_cutoffs`), with a ridge penalty pulling the weights towards the
equal-weight logit pool (penalty 1.0, intercept free); the equal-weight pool is also the fallback while the window holds fewer
than 126 days or fewer than 5 days of either class (the first 7 blocks). Members: `ngboost_laplace`, `hierarchical_logistic` and
`qrf` (the best onset recall at the amended cut-offs in #416's table, besides the hurdle and settlement-quantile rows), plus the
merged `time_to_pressure_hazard` and `extreme_value_tail`. Comparison row: `stack_equal_average`, the arithmetic mean of the five,
no fit. The members are the open track pull requests' candidates (#413, #406) and the merged hazard and tail tracks; each member's
forecasts were produced by that track's own script at its head, unchanged (reproduce below). Not stacked: the rare-event and policy
tracks (no merged forecast file), the hurdle and Markov-switching tracks (pull requests still open when this was declared).

## Result: the stack does not pass, and the fitted weights do not beat the plain average

The pass rule is tier 1 (onset warning at lead of at least 1), tier 3 (no crying wolf) and tier 5 (week-ahead). The stack fails
all three, as every member does.

Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes with pressure, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.00 | 2.7 / 4.4 | 1 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| extreme_value_tail | 9 of 26 | 0.346 [0.174, 0.530] | 0.192 | 2.31 | 0.0 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| hierarchical_logistic | 15 of 26 | 0.577 [0.400, 0.750] | 0.231 | 3.65 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_laplace | 15 of 26 | 0.577 [0.400, 0.759] | 0.231 | 2.54 | 0.2 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.231 | 3.42 | 0.5 / 0.0 | 2 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| qrf | 12 of 26 | 0.462 [0.273, 0.652] | 0.231 | 2.85 | 0.0 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| stack_equal_average | 12 of 26 | 0.462 [0.278, 0.655] | 0.231 | 3.23 | 0.0 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| stacked_ensemble | 15 of 26 | 0.577 [0.393, 0.750] | 0.231 | 3.27 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| time_to_pressure_hazard | 7 of 26 | 0.269 [0.129, 0.423] | 0.192 | 2.19 | 0.0 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |

Table 2 and 3 (by regime and day type, and Brier against climatology by regime and day type), the stack's per-horizon figures and the judge's
full report are in `docs/pivot/evidence/stacked-ensemble/` (`tables.md`, `perh.md`, `judge.md`).

Share of the pressure days flagged at h = 1 (+5 bp), the stack against its members:

| model | regime: 2018-19 | regime: 2020 | regime: 2024 | regime: 2025-26 | month_end | ordinary | quarter_end | tax_date |
|---|---|---|---|---|---|---|---|---|
| extreme_value_tail | 0.67 (102) | 0.00 (4) | 0.00 (5) | 0.03 (29) | 0.47 (17) | 0.49 (101) | 0.44 (9) | 0.62 (13) |
| hierarchical_logistic | 0.68 (102) | 0.00 (4) | 0.00 (5) | 0.52 (29) | 0.71 (17) | 0.57 (101) | 0.56 (9) | 0.69 (13) |
| ngboost_laplace | 0.55 (102) | 0.25 (4) | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.46 (101) | 0.67 (9) | 0.46 (13) |
| qrf | 0.56 (102) | 0.25 (4) | 0.00 (5) | 0.07 (29) | 0.35 (17) | 0.47 (101) | 0.22 (9) | 0.38 (13) |
| stack_equal_average | 0.66 (102) | 0.00 (4) | 0.00 (5) | 0.14 (29) | 0.59 (17) | 0.49 (101) | 0.44 (9) | 0.62 (13) |
| stacked_ensemble | 0.63 (102) | 0.00 (4) | 0.00 (5) | 0.31 (29) | 0.71 (17) | 0.51 (101) | 0.44 (9) | 0.38 (13) |
| time_to_pressure_hazard | 0.61 (102) | 0.00 (4) | 0.00 (5) | 0.03 (29) | 0.47 (17) | 0.43 (101) | 0.44 (9) | 0.62 (13) |

(2021-23 had no pressure day.) The number in brackets is the group's pressure days.

Brier and AUROC per horizon, with the paired gain over climatology and persistence:

| h | model | Brier | AUROC | recall | precision | dBrier vs climatology [90%] | dBrier vs persistence [90%] |
|---|---|---|---|---|---|---|---|
| 1 | ngboost_laplace | 0.0462 | 0.928 | 0.486 | 0.607 | +0.0252 [+0.0186, +0.0323] | +0.0101 [+0.0050, +0.0152] |
| 1 | hierarchical_logistic | 0.0530 | 0.880 | 0.600 | 0.512 | +0.0184 [+0.0114, +0.0260] | +0.0034 [-0.0007, +0.0073] |
| 1 | qrf | 0.0494 | 0.921 | 0.429 | 0.488 | +0.0220 [+0.0156, +0.0293] | +0.0069 [+0.0020, +0.0116] |
| 1 | time_to_pressure_hazard | 0.0553 | 0.915 | 0.450 | 0.568 | +0.0161 [+0.0088, +0.0243] | +0.0010 [-0.0058, +0.0079] |
| 1 | extreme_value_tail | 0.0520 | 0.921 | 0.493 | 0.535 | +0.0194 [+0.0134, +0.0262] | +0.0043 [-0.0017, +0.0101] |
| 1 | stack_equal_average | 0.0476 | 0.927 | 0.507 | 0.526 | +0.0238 [+0.0175, +0.0311] | +0.0088 [+0.0043, +0.0136] |
| 1 | stacked_ensemble | 0.0508 | 0.926 | 0.521 | 0.462 | +0.0207 [+0.0136, +0.0286] | +0.0056 [+0.0008, +0.0102] |
| 1 | calendar_climatology | 0.0714 | 0.586 | 0.514 | 0.364 | +0.0000 [+0.0000, +0.0000] | -0.0151 [-0.0211, -0.0097] |
| 1 | persistence_logistic | 0.0563 | 0.876 | 0.436 | 0.459 | +0.0151 [+0.0094, +0.0214] | +0.0000 [+0.0000, +0.0000] |
| 2 | ngboost_laplace | 0.0568 | 0.899 | 0.129 | 0.286 | +0.0143 [+0.0086, +0.0201] | +0.0043 [-0.0009, +0.0092] |
| 2 | hierarchical_logistic | 0.0589 | 0.847 | 0.317 | 0.484 | +0.0121 [+0.0066, +0.0178] | +0.0021 [-0.0016, +0.0061] |
| 2 | qrf | 0.0567 | 0.892 | 0.230 | 0.432 | +0.0143 [+0.0088, +0.0201] | +0.0043 [-0.0005, +0.0088] |
| 2 | time_to_pressure_hazard | 0.0576 | 0.907 | 0.367 | 0.500 | +0.0135 [+0.0066, +0.0206] | +0.0035 [-0.0036, +0.0103] |
| 2 | extreme_value_tail | 0.0554 | 0.909 | 0.324 | 0.446 | +0.0157 [+0.0101, +0.0222] | +0.0057 [-0.0004, +0.0121] |
| 2 | stack_equal_average | 0.0545 | 0.900 | 0.331 | 0.511 | +0.0166 [+0.0116, +0.0223] | +0.0066 [+0.0018, +0.0118] |
| 2 | stacked_ensemble | 0.0569 | 0.906 | 0.439 | 0.459 | +0.0142 [+0.0087, +0.0199] | +0.0042 [-0.0009, +0.0093] |
| 2 | calendar_climatology | 0.0711 | 0.586 | 0.496 | 0.352 | +0.0000 [+0.0000, +0.0000] | -0.0100 [-0.0146, -0.0054] |
| 2 | persistence_logistic | 0.0611 | 0.817 | 0.583 | 0.476 | +0.0100 [+0.0056, +0.0146] | +0.0000 [+0.0000, +0.0000] |
| 3 | ngboost_laplace | 0.0595 | 0.892 | 0.159 | 0.373 | +0.0112 [+0.0046, +0.0169] | +0.0049 [-0.0008, +0.0100] |
| 3 | hierarchical_logistic | 0.0607 | 0.834 | 0.493 | 0.453 | +0.0100 [+0.0053, +0.0146] | +0.0037 [-0.0001, +0.0076] |
| 3 | qrf | 0.0569 | 0.886 | 0.152 | 0.309 | +0.0138 [+0.0089, +0.0190] | +0.0075 [+0.0032, +0.0116] |
| 3 | time_to_pressure_hazard | 0.0595 | 0.902 | 0.348 | 0.471 | +0.0112 [+0.0043, +0.0179] | +0.0049 [-0.0023, +0.0115] |
| 3 | extreme_value_tail | 0.0564 | 0.904 | 0.355 | 0.485 | +0.0142 [+0.0085, +0.0205] | +0.0079 [+0.0019, +0.0142] |
| 3 | stack_equal_average | 0.0558 | 0.894 | 0.290 | 0.388 | +0.0149 [+0.0099, +0.0196] | +0.0086 [+0.0043, +0.0132] |
| 3 | stacked_ensemble | 0.0578 | 0.903 | 0.413 | 0.416 | +0.0129 [+0.0081, +0.0183] | +0.0066 [+0.0020, +0.0113] |
| 3 | calendar_climatology | 0.0707 | 0.585 | 0.493 | 0.347 | +0.0000 [+0.0000, +0.0000] | -0.0063 [-0.0098, -0.0028] |
| 3 | persistence_logistic | 0.0644 | 0.765 | 0.341 | 0.392 | +0.0063 [+0.0030, +0.0098] | +0.0000 [+0.0000, +0.0000] |
| 4 | ngboost_laplace | 0.0615 | 0.873 | 0.261 | 0.353 | +0.0093 [+0.0028, +0.0154] | +0.0008 [-0.0050, +0.0062] |
| 4 | hierarchical_logistic | 0.0603 | 0.833 | 0.478 | 0.458 | +0.0105 [+0.0057, +0.0154] | +0.0020 [-0.0023, +0.0062] |
| 4 | qrf | 0.0592 | 0.879 | 0.246 | 0.354 | +0.0116 [+0.0064, +0.0169] | +0.0032 [-0.0015, +0.0076] |
| 4 | time_to_pressure_hazard | 0.0594 | 0.899 | 0.341 | 0.452 | +0.0114 [+0.0049, +0.0187] | +0.0030 [-0.0041, +0.0100] |
| 4 | extreme_value_tail | 0.0558 | 0.906 | 0.326 | 0.536 | +0.0150 [+0.0092, +0.0210] | +0.0066 [+0.0003, +0.0130] |
| 4 | stack_equal_average | 0.0566 | 0.891 | 0.391 | 0.409 | +0.0143 [+0.0096, +0.0191] | +0.0058 [+0.0012, +0.0105] |
| 4 | stacked_ensemble | 0.0593 | 0.897 | 0.377 | 0.456 | +0.0116 [+0.0065, +0.0165] | +0.0031 [-0.0017, +0.0078] |
| 4 | calendar_climatology | 0.0708 | 0.580 | 0.486 | 0.342 | +0.0000 [+0.0000, +0.0000] | -0.0085 [-0.0120, -0.0048] |
| 4 | persistence_logistic | 0.0624 | 0.788 | 0.428 | 0.418 | +0.0085 [+0.0047, +0.0121] | +0.0000 [+0.0000, +0.0000] |
| 5 | ngboost_laplace | 0.0637 | 0.862 | 0.130 | 0.305 | +0.0072 [-0.0004, +0.0140] | -0.0003 [-0.0076, +0.0060] |
| 5 | hierarchical_logistic | 0.0608 | 0.827 | 0.457 | 0.399 | +0.0101 [+0.0050, +0.0151] | +0.0026 [-0.0020, +0.0071] |
| 5 | qrf | 0.0594 | 0.848 | 0.355 | 0.398 | +0.0115 [+0.0071, +0.0163] | +0.0040 [-0.0006, +0.0082] |
| 5 | time_to_pressure_hazard | 0.0599 | 0.895 | 0.246 | 0.459 | +0.0110 [+0.0050, +0.0172] | +0.0035 [-0.0033, +0.0098] |
| 5 | extreme_value_tail | 0.0564 | 0.905 | 0.275 | 0.469 | +0.0145 [+0.0092, +0.0203] | +0.0070 [+0.0010, +0.0132] |
| 5 | stack_equal_average | 0.0573 | 0.879 | 0.442 | 0.421 | +0.0137 [+0.0092, +0.0185] | +0.0061 [+0.0014, +0.0111] |
| 5 | stacked_ensemble | 0.0605 | 0.881 | 0.420 | 0.411 | +0.0104 [+0.0039, +0.0165] | +0.0029 [-0.0034, +0.0090] |
| 5 | calendar_climatology | 0.0709 | 0.578 | 0.478 | 0.337 | +0.0000 [+0.0000, +0.0000] | -0.0075 [-0.0114, -0.0036] |
| 5 | persistence_logistic | 0.0634 | 0.772 | 0.391 | 0.425 | +0.0075 [+0.0036, +0.0114] | +0.0000 [+0.0000, +0.0000] |

Mean fitted weights over the refits that were fitted (not the equal-weight fallback), per horizon and threshold:

| h | threshold | refits fitted / equal | ngboost_laplace | hierarchical_logistic | qrf | time_to_pressure_hazard | extreme_value_tail | mean intercept |
|---|---|---|---|---|---|---|---|---|
| 1 | +5 bp | 83 / 7 | 0.47 | 0.12 | 0.10 | -0.38 | 0.59 | +0.29 |
| 1 | +10 bp | 83 / 7 | 0.52 | 0.26 | -0.26 | -0.15 | 0.52 | +0.20 |
| 2 | +5 bp | 83 / 7 | 0.40 | -0.03 | -0.40 | -0.06 | 0.73 | -0.29 |
| 2 | +10 bp | 83 / 7 | 0.04 | -0.21 | -0.07 | -0.01 | 1.02 | -0.96 |
| 3 | +5 bp | 83 / 7 | 0.03 | -0.29 | 0.23 | -0.01 | 0.65 | -0.51 |
| 3 | +10 bp | 83 / 7 | 0.06 | -0.06 | 0.04 | -0.18 | 0.99 | -0.62 |
| 4 | +5 bp | 83 / 7 | -0.14 | -0.27 | 0.17 | 0.03 | 0.86 | -0.61 |
| 4 | +10 bp | 83 / 7 | 0.10 | 0.04 | 0.09 | -0.37 | 1.11 | -0.34 |
| 5 | +5 bp | 82 / 7 | -0.22 | -0.05 | 0.11 | -0.05 | 0.78 | -0.54 |
| 5 | +10 bp | 82 / 7 | 0.04 | -0.10 | -0.08 | -0.04 | 0.82 | -0.96 |

## What this says

- **The stack catches as many onsets as the best member, and no more.** It flags 15 of 26 onsets one day ahead or more (recall 0.577
  [0.393, 0.750]), the same as `ngboost_laplace` and `hierarchical_logistic` alone, but with 3.27 false alarms per onset against 2.54
  for `ngboost_laplace` (limit 2). Climatology at the same false alarms catches 0.231.
- **The fitted weights do not beat the plain average.** The equal average has the better Brier at every horizon (h = 1: 0.0476
  against 0.0508) and a better paired gain over climatology at every horizon; at h = 1 the stack's Brier is also worse than
  `ngboost_laplace` alone (0.0462). The stack's AUROC is level with the average's. The stack gains recall at h = 1 to 3 (0.521 against
  0.507 at h = 1; 0.439 against 0.331 at h = 2) at the cost of precision. The stack's Brier differences from the average and from the
  best member are not tested pairwise here.
- **The weights are unstable and mostly not convex.** The mean weights swing in sign across horizons and thresholds (negative on
  the hazard and on `qrf` at some, above 1.0 on the tail at +10 bp at h = 2 and h = 4). With 140 pressure days at +5 bp in all
  (61 at +10 bp), five correlated members cannot be weighted reliably, and the penalty (1.0, against a log-loss summed over
  hundreds of days) is weak. A stronger penalty or a convex (non-negative) form is a
  different declaration; it was not tried.
- **Calibration and scarce regime.** Tier 3 still fails on calibration by regime (3 of the 4 regimes that had a pressure day are
  calibrated at h = 1), and the scarce-regime pass fails. Tier 5 (week-ahead window) fails on calibration.
- **Reproduces #416.** The member rows (onsets flagged, recall, false alarms per onset) equal those in #416's re-judge for the
  members scored there: `ngboost_laplace` 15, `hierarchical_logistic` 15, `qrf` 12, `time_to_pressure_hazard` 7,
  `extreme_value_tail` 9 of 26.

## Not checked, or for Eleonora

- No pairwise bootstrap of the stack against the equal average or against `ngboost_laplace` (the judge reports each against
  climatology and persistence only).
- The hurdle (#404), Markov-switching (#403), rare-event (#402) and probit/quantile settlement members were not stacked, nor were
  other member sets or penalties tried; the declared set and penalty were run once. A different declaration is a separate run.
- Members' forecasts were produced from open pull requests' heads (#413, #406): if those change before they merge, the members change.
  The `hierarchical_logistic` forecasts are scored on the scratch panel `pressure_v1_1.py panel` (digest `4137d0ad…`), the others on the
  published panel (`4ddc3882…`), on the same scored days.
- Confirmation tier (2026-01-01 on): not scored.
- Nothing publishes: no published declaration, record or figure moves. `docs/pivot/evidence/stacked-ensemble/pressure_judge_declaration_used.json`
  is the declaration the judge ran under (this branch's declaration plus the open pull requests' member candidates, as #416's re-judge did);
  `metadata/pressure_judge.json` on this branch gains only the stack's two candidates.

## Reproduce

Panels: the published panel (`4ddc3882…`) and the scratch panel, as `docs/pivot/judge-amendment-result.md` says. Members, each at the head of
its pull request or on this branch, with `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1` (several processes at once oversubscribe the cores):

```
# #413 head: qrf, ngboost_laplace, ngboost_normal and the gbm reference
PYTHONPATH=src python3 scripts/pressure_track_q.py forecasts --panel PUB.csv --horizon H --output OUT/q_hH.json --distribution OUT/qd_hH.json
# #406 head (scratch panel AUG.csv)
PYTHONPATH=src python3 scripts/hierarchical_logistic.py forecasts --panel AUG.csv --horizon H --output OUT/h_hH.json
# this branch
PYTHONPATH=src python3 scripts/pressure_hazard.py forecasts --panel PUB.csv --horizon H --output OUT/z_hH.json
PYTHONPATH=src python3 scripts/pressure_tail.py forecasts --panel PUB.csv --horizon H --output OUT/e_hH.json
PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUB.csv --published --horizon H --output OUT/b_hH.json
PYTHONPATH=src python3 scripts/pressure_stack.py forecasts --panel PUB.csv --scratch-panel AUG.csv --horizon H --output OUT/stack_hH.json OUT/q_hH.json OUT/h_hH.json OUT/z_hH.json OUT/e_hH.json
PYTHONPATH=src python3 scripts/pressure_stack.py weights --output OUT/weights.md OUT/stack_h?.json
```

The judge refuses a declaration that is not committed and a forecast file scored on another panel: in a scratch checkout of this branch, copy
`docs/pivot/evidence/stacked-ensemble/pressure_judge_declaration_used.json` over `metadata/pressure_judge.json`, commit it there, and give the
`hierarchical_logistic` files the published panel's digest (after checking that the dates are the grid's). Then:

```
PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUB.csv --output OUT/judge.json --markdown OUT/judge.md OUT/b_h?.json OUT/q_h?.json OUT/h_h?.json OUT/z_h?.json OUT/e_h?.json OUT/stack_h?.json
PYTHONPATH=src python3 scripts/pressure_judge.py table OUT/judge.json --output OUT/tables.md
```
