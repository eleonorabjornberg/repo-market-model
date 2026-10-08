# Re-judge of every #374 track under the amended judge (#407)

A scratch measurement under the judge as amended by the pull request that closes #407 (Eleonora's ruling of
8 October 2026 on #374): each flag cut-off is chosen from the refit's training window alone, calibration by regime
(tier 3) is tested only in regimes that had a pressure day, and a pass within the scarce regime alone is reported
beside the pass rule. Scored days 2018-06-29 to 2025-12-31, h = 1 to 5, +5 bp primary, 90% stationary-bootstrap
intervals. No comparison scores a locked day (`docs/decisions/lockbox.md`); the confirmation window is not looked at.
It writes nothing into `docs/runs/` and moves no published figure.

**What was scored.** Every candidate declared in `metadata/pressure_judge.json` on main (published v1, track S, track T),
and the candidates of the open track pull requests: #399 (hazard), #401 (tail), #402 (rare-event training), #403
(Markov switching), #404 (two-part), #406 (hierarchical logistic) and #413 (quantile regression forest and natural-gradient
boosting, with its gbm reference row). #392 (policy register) declares no model. Each track's forecasts were produced by that
track's own script at its pull request's head, unchanged; only the judge is the amended one. The two benchmarks and the published
v1 row come from `pressure_judge.py forecasts --published`.

**Reproduce** (panel `4ddc3882…`, the published panel; tracks S and H score on the scratch panel `pressure_v1_1.py panel`,
digest `4137d0ad…`, on the same scored days). For a track on its own branch, run its forecast script as that pull request
states, for h = 1 to 5. The judge needs the track's candidates in the declaration: copy
`docs/pivot/evidence/judge-amendment/pressure_judge_rejudge.json` (the declaration with every track's candidates added and no
other change) over `metadata/pressure_judge.json` in a scratch checkout of this branch and commit it there, because the script
refuses an uncommitted declaration. A forecast file written on the scratch panel names that panel's digest; give it the published
panel's (the judge refuses files from another panel) after checking that its dates are the grid's.

```
PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUB.csv --output OUT/judge.json --markdown OUT/judge.md IN/*_h?.json
PYTHONPATH=src python3 scripts/pressure_judge.py table OUT/judge.json --output OUT/tables.md
```

## Result: no model passes, under either reading

The pass rule is tier 1 (onset warning at lead of at least 1), tier 3 (no crying wolf, at every lead) and tier 5 (week-ahead
window). No model passes, and none passes within the scarce regime alone. Tier 1's false-alarm limit (at most 2 per onset)
is met by nine models, and every one of the nine flags fewer than half of the onsets.
Tier 3 still fails on calibration by regime: with the regimes that had no pressure day dropped from the test, nearly every
model is uncalibrated in at least one of the four regimes that had one (2018-19, 2020, 2024 and 2025-26; 2021-23 had none), at
every lead.

Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals. The pass rule is tier 1 at lead >= 1, tier 3 at every lead and tier 5.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes with pressure, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.00 | 2.7 / 4.4 | 1 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| extreme_value_tail | 9 of 26 | 0.346 [0.174, 0.530] | 0.192 | 2.31 | 0.0 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| gbm_reference | 7 of 26 | 0.269 [0.130, 0.423] | 0.192 | 2.19 | 0.0 / 0.0 | 2 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| hierarchical_logistic | 15 of 26 | 0.577 [0.400, 0.750] | 0.231 | 3.65 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| markov_k2 | 4 of 26 | 0.154 [0.033, 0.308] | 0.192 | 2.42 | 2.9 / 4.0 | 0 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| markov_k3 | 9 of 26 | 0.346 [0.182, 0.526] | 0.231 | 4.19 | 6.3 / 7.7 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| markov_k3_scarcity | 9 of 26 | 0.346 [0.174, 0.522] | 0.269 | 4.77 | 7.8 / 10.8 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_laplace | 15 of 26 | 0.577 [0.400, 0.759] | 0.231 | 2.54 | 0.2 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| ngboost_normal | 10 of 26 | 0.385 [0.222, 0.545] | 0.192 | 1.96 | 0.0 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.231 | 3.42 | 0.5 / 0.0 | 2 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| published_v1 | 2 of 26 | 0.077 [0.000, 0.185] | 0.192 | 2.35 | 0.2 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| qrf | 12 of 26 | 0.462 [0.273, 0.652] | 0.231 | 2.85 | 0.0 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| rare_gbm_balanced_bootstrap+recalibrated | 7 of 26 | 0.269 [0.105, 0.438] | 0.115 | 1.19 | 0.0 / 0.0 | 2 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| rare_gbm_class_weight+recalibrated | 6 of 26 | 0.231 [0.088, 0.375] | 0.154 | 1.46 | 0.0 / 0.0 | 3 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| rare_gbm_focal+recalibrated | 7 of 26 | 0.269 [0.111, 0.444] | 0.154 | 1.58 | 0.0 / 0.0 | 2 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| rare_logistic_balanced_bootstrap+recalibrated | 3 of 26 | 0.115 [0.000, 0.227] | 0.096 | 0.65 | 0.0 / 0.0 | 2 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| rare_logistic_class_weight+recalibrated | 3 of 26 | 0.115 [0.000, 0.226] | 0.115 | 0.77 | 0.0 / 0.0 | 2 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| scarcity_gbm | 10 of 26 | 0.385 [0.208, 0.576] | 0.231 | 2.65 | 0.0 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| scarcity_gbm_interactions | 10 of 26 | 0.385 [0.200, 0.576] | 0.231 | 2.65 | 0.0 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| scarcity_logistic | 13 of 26 | 0.500 [0.320, 0.696] | 0.231 | 3.23 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| scarcity_logistic_interactions | 14 of 26 | 0.538 [0.346, 0.731] | 0.231 | 3.23 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| scarcity_logistic_regime_pooled | 13 of 26 | 0.500 [0.320, 0.692] | 0.231 | 3.23 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| settlement_probit_scarcity | 8 of 26 | 0.308 [0.160, 0.469] | 0.154 | 1.58 | 0.2 / 0.0 | 1 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| settlement_probit_tga | 9 of 26 | 0.346 [0.200, 0.519] | 0.192 | 1.73 | 0.2 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| settlement_probit_timing | 13 of 26 | 0.500 [0.308, 0.680] | 0.231 | 3.46 | 1.5 / 1.7 | 2 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| settlement_quantile_scarcity | 10 of 26 | 0.385 [0.226, 0.542] | 0.192 | 2.38 | 0.5 / 0.0 | 3 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| settlement_quantile_tga | 9 of 26 | 0.346 [0.192, 0.520] | 0.192 | 2.27 | 0.2 / 0.0 | 3 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| settlement_quantile_timing | 15 of 26 | 0.577 [0.391, 0.750] | 0.231 | 3.65 | 2.2 / 2.0 | 2 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| time_to_pressure_hazard | 7 of 26 | 0.269 [0.129, 0.423] | 0.192 | 2.19 | 0.0 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| two_part_gbm | 15 of 26 | 0.577 [0.400, 0.762] | 0.192 | 2.46 | 0.0 / 0.0 | 4 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| two_part_logistic | 10 of 26 | 0.385 [0.226, 0.560] | 0.192 | 2.00 | 0.0 / 0.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.70 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.53 (17) | 0.50 (101) | 0.44 (9) | 0.62 (13) |
| extreme_value_tail | 0.67 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.47 (17) | 0.49 (101) | 0.44 (9) | 0.62 (13) |
| gbm_reference | 0.55 (102) | 0.00 (4) | – | 0.00 (5) | 0.38 (29) | 0.71 (17) | 0.47 (101) | 0.33 (9) | 0.38 (13) |
| hierarchical_logistic | 0.68 (102) | 0.00 (4) | – | 0.00 (5) | 0.52 (29) | 0.71 (17) | 0.57 (101) | 0.56 (9) | 0.69 (13) |
| markov_k2 | 0.00 (102) | 0.00 (4) | – | 0.00 (5) | 0.00 (29) | 0.00 (17) | 0.00 (101) | 0.00 (9) | 0.00 (13) |
| markov_k3 | 0.26 (102) | 0.00 (4) | – | 0.00 (5) | 0.41 (29) | 0.35 (17) | 0.30 (101) | 0.22 (9) | 0.08 (13) |
| markov_k3_scarcity | 0.26 (102) | 0.00 (4) | – | 0.00 (5) | 0.00 (29) | 0.18 (17) | 0.22 (101) | 0.11 (9) | 0.08 (13) |
| ngboost_laplace | 0.55 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.46 (101) | 0.67 (9) | 0.46 (13) |
| ngboost_normal | 0.57 (102) | 0.25 (4) | – | 0.00 (5) | 0.21 (29) | 0.53 (17) | 0.47 (101) | 0.33 (9) | 0.46 (13) |
| persistence_logistic | 0.45 (102) | 0.25 (4) | – | 0.00 (5) | 0.48 (29) | 0.41 (17) | 0.48 (101) | 0.33 (9) | 0.23 (13) |
| published_v1 | 0.51 (102) | 0.00 (4) | – | 0.00 (5) | 0.34 (29) | 0.41 (17) | 0.47 (101) | 0.33 (9) | 0.38 (13) |
| qrf | 0.56 (102) | 0.25 (4) | – | 0.00 (5) | 0.07 (29) | 0.35 (17) | 0.47 (101) | 0.22 (9) | 0.38 (13) |
| rare_gbm_balanced_bootstrap+recalibrated | 0.22 (102) | 0.00 (4) | – | 0.00 (5) | 0.07 (29) | 0.24 (17) | 0.16 (101) | 0.33 (9) | 0.08 (13) |
| rare_gbm_class_weight+recalibrated | 0.12 (102) | 0.00 (4) | – | 0.00 (5) | 0.14 (29) | 0.24 (17) | 0.10 (101) | 0.22 (9) | 0.00 (13) |
| rare_gbm_focal+recalibrated | 0.22 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.29 (17) | 0.15 (101) | 0.22 (9) | 0.08 (13) |
| rare_logistic_balanced_bootstrap+recalibrated | 0.15 (102) | 0.00 (4) | – | 0.00 (5) | 0.10 (29) | 0.18 (17) | 0.09 (101) | 0.33 (9) | 0.23 (13) |
| rare_logistic_class_weight+recalibrated | 0.13 (102) | 0.00 (4) | – | 0.00 (5) | 0.10 (29) | 0.18 (17) | 0.07 (101) | 0.33 (9) | 0.23 (13) |
| scarcity_gbm | 0.58 (102) | 0.00 (4) | – | 0.00 (5) | 0.52 (29) | 0.53 (17) | 0.55 (101) | 0.22 (9) | 0.54 (13) |
| scarcity_gbm_interactions | 0.58 (102) | 0.00 (4) | – | 0.00 (5) | 0.52 (29) | 0.53 (17) | 0.55 (101) | 0.22 (9) | 0.54 (13) |
| scarcity_logistic | 0.63 (102) | 0.00 (4) | – | 0.00 (5) | 0.48 (29) | 0.71 (17) | 0.51 (101) | 0.56 (9) | 0.69 (13) |
| scarcity_logistic_interactions | 0.66 (102) | 0.00 (4) | – | 0.00 (5) | 0.48 (29) | 0.76 (17) | 0.54 (101) | 0.44 (9) | 0.69 (13) |
| scarcity_logistic_regime_pooled | 0.68 (102) | 0.00 (4) | – | 0.00 (5) | 0.52 (29) | 0.71 (17) | 0.57 (101) | 0.56 (9) | 0.69 (13) |
| settlement_probit_scarcity | 0.45 (102) | 0.00 (4) | – | 0.20 (5) | 0.10 (29) | 0.35 (17) | 0.32 (101) | 0.56 (9) | 0.54 (13) |
| settlement_probit_tga | 0.46 (102) | 0.00 (4) | – | 0.20 (5) | 0.10 (29) | 0.35 (17) | 0.32 (101) | 0.56 (9) | 0.62 (13) |
| settlement_probit_timing | 0.64 (102) | 0.25 (4) | – | 0.20 (5) | 0.31 (29) | 0.59 (17) | 0.52 (101) | 0.67 (9) | 0.54 (13) |
| settlement_quantile_scarcity | 0.58 (102) | 0.25 (4) | – | 0.20 (5) | 0.41 (29) | 0.71 (17) | 0.47 (101) | 0.67 (9) | 0.62 (13) |
| settlement_quantile_tga | 0.56 (102) | 0.00 (4) | – | 0.00 (5) | 0.38 (29) | 0.65 (17) | 0.45 (101) | 0.44 (9) | 0.62 (13) |
| settlement_quantile_timing | 0.59 (102) | 0.25 (4) | – | 0.20 (5) | 0.52 (29) | 0.65 (17) | 0.50 (101) | 0.78 (9) | 0.62 (13) |
| time_to_pressure_hazard | 0.61 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.47 (17) | 0.43 (101) | 0.44 (9) | 0.62 (13) |
| two_part_gbm | 0.25 (102) | 0.25 (4) | – | 0.00 (5) | 0.21 (29) | 0.47 (17) | 0.16 (101) | 0.44 (9) | 0.38 (13) |
| two_part_logistic | 0.63 (102) | 0.00 (4) | – | 0.00 (5) | 0.07 (29) | 0.35 (17) | 0.48 (101) | 0.44 (9) | 0.62 (13) |

Table 3. Brier difference against calendar climatology at h = 1 (+5 bp), by regime and pressure-day type (positive: better than climatology; 90% interval).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] | +0.0000 [+0.0000, +0.0000] |
| extreme_value_tail | +0.0378 [+0.0106, +0.0698] | +0.0354 [+0.0268, +0.0441] | +0.0138 [+0.0121, +0.0157] | +0.0022 [-0.0016, +0.0054] | +0.0094 [+0.0013, +0.0191] | +0.0290 [+0.0188, +0.0400] | +0.0142 [+0.0082, +0.0211] | +0.1148 [+0.0604, +0.1722] | +0.0629 [+0.0363, +0.0926] |
| gbm_reference | +0.0327 [-0.0044, +0.0758] | +0.0295 [+0.0159, +0.0410] | +0.0115 [+0.0098, +0.0133] | +0.0008 [-0.0027, +0.0032] | +0.0327 [+0.0009, +0.0728] | +0.0353 [+0.0062, +0.0674] | +0.0148 [+0.0059, +0.0250] | +0.1113 [+0.0291, +0.1974] | +0.0473 [+0.0209, +0.0769] |
| hierarchical_logistic | +0.0265 [+0.0024, +0.0512] | +0.0181 [+0.0037, +0.0311] | +0.0137 [+0.0120, +0.0155] | +0.0013 [-0.0036, +0.0053] | +0.0382 [+0.0069, +0.0750] | +0.0440 [+0.0227, +0.0682] | +0.0128 [+0.0065, +0.0202] | +0.0754 [+0.0169, +0.1274] | +0.0569 [+0.0308, +0.0829] |
| markov_k2 | +0.0235 [-0.0000, +0.0530] | +0.0156 [+0.0096, +0.0223] | +0.0055 [-0.0003, +0.0099] | -0.0393 [-0.0574, -0.0215] | -0.0159 [-0.0523, +0.0288] | -0.0009 [-0.0165, +0.0168] | -0.0012 [-0.0100, +0.0087] | +0.0829 [-0.0061, +0.1800] | +0.0281 [+0.0022, +0.0530] |
| markov_k3 | +0.0293 [+0.0034, +0.0563] | +0.0380 [+0.0284, +0.0470] | -0.0006 [-0.0107, +0.0077] | +0.0017 [-0.0033, +0.0051] | +0.0203 [-0.0055, +0.0529] | +0.0213 [+0.0041, +0.0411] | +0.0109 [+0.0030, +0.0195] | +0.0655 [-0.0312, +0.1616] | +0.0317 [+0.0044, +0.0580] |
| markov_k3_scarcity | +0.0293 [+0.0048, +0.0555] | +0.0321 [+0.0215, +0.0421] | -0.0008 [-0.0118, +0.0083] | +0.0008 [-0.0060, +0.0053] | +0.0214 [-0.0044, +0.0571] | +0.0193 [+0.0005, +0.0403] | +0.0103 [+0.0022, +0.0192] | +0.0655 [-0.0329, +0.1684] | +0.0281 [+0.0040, +0.0514] |
| ngboost_laplace | +0.0543 [+0.0271, +0.0844] | +0.0329 [+0.0235, +0.0419] | +0.0138 [+0.0121, +0.0157] | +0.0041 [+0.0006, +0.0072] | +0.0287 [+0.0113, +0.0503] | +0.0481 [+0.0291, +0.0671] | +0.0187 [+0.0123, +0.0262] | +0.1308 [+0.0495, +0.2125] | +0.0670 [+0.0493, +0.0861] |
| ngboost_normal | +0.0378 [-0.0037, +0.0819] | +0.0051 [-0.0111, +0.0179] | +0.0136 [+0.0119, +0.0154] | +0.0045 [+0.0008, +0.0082] | +0.0345 [+0.0113, +0.0636] | +0.0433 [+0.0215, +0.0677] | +0.0130 [+0.0035, +0.0233] | +0.0828 [+0.0025, +0.1649] | +0.0610 [+0.0408, +0.0844] |
| persistence_logistic | +0.0168 [-0.0027, +0.0376] | +0.0235 [+0.0133, +0.0333] | +0.0130 [+0.0114, +0.0148] | -0.0002 [-0.0064, +0.0045] | +0.0256 [+0.0003, +0.0575] | +0.0212 [+0.0029, +0.0434] | +0.0125 [+0.0072, +0.0187] | +0.0604 [-0.0440, +0.1631] | +0.0355 [+0.0130, +0.0568] |
| published_v1 | +0.0460 [+0.0127, +0.0833] | +0.0328 [+0.0266, +0.0391] | +0.0127 [+0.0111, +0.0144] | +0.0010 [-0.0043, +0.0050] | +0.0229 [-0.0053, +0.0574] | +0.0421 [+0.0202, +0.0713] | +0.0169 [+0.0088, +0.0259] | +0.0922 [+0.0137, +0.1746] | +0.0534 [+0.0285, +0.0795] |
| qrf | +0.0471 [+0.0197, +0.0797] | +0.0315 [+0.0202, +0.0416] | +0.0138 [+0.0120, +0.0157] | +0.0035 [-0.0002, +0.0061] | +0.0177 [+0.0057, +0.0338] | +0.0373 [+0.0208, +0.0551] | +0.0169 [+0.0103, +0.0247] | +0.0947 [+0.0240, +0.1682] | +0.0613 [+0.0412, +0.0823] |
| rare_gbm_balanced_bootstrap+recalibrated | -0.0221 [-0.0739, +0.0258] | +0.0314 [+0.0235, +0.0393] | +0.0136 [+0.0120, +0.0155] | +0.0018 [-0.0023, +0.0051] | +0.0255 [+0.0079, +0.0479] | +0.0380 [+0.0172, +0.0604] | +0.0016 [-0.0109, +0.0124] | +0.1263 [+0.0343, +0.2181] | +0.0503 [+0.0322, +0.0691] |
| rare_gbm_class_weight+recalibrated | -0.0121 [-0.0611, +0.0361] | +0.0299 [+0.0212, +0.0385] | +0.0134 [+0.0117, +0.0153] | +0.0017 [-0.0026, +0.0051] | +0.0205 [+0.0059, +0.0387] | +0.0359 [+0.0153, +0.0561] | +0.0040 [-0.0074, +0.0146] | +0.1071 [+0.0197, +0.1934] | +0.0382 [+0.0138, +0.0582] |
| rare_gbm_focal+recalibrated | +0.0199 [-0.0172, +0.0584] | +0.0306 [+0.0221, +0.0381] | +0.0135 [+0.0118, +0.0154] | +0.0015 [-0.0033, +0.0052] | +0.0122 [+0.0011, +0.0279] | +0.0378 [+0.0208, +0.0558] | +0.0093 [+0.0009, +0.0179] | +0.1064 [+0.0236, +0.1946] | +0.0541 [+0.0390, +0.0702] |
| rare_logistic_balanced_bootstrap+recalibrated | -0.0497 [-0.1269, +0.0227] | +0.0359 [+0.0276, +0.0442] | +0.0138 [+0.0121, +0.0157] | +0.0049 [+0.0005, +0.0094] | +0.0306 [+0.0067, +0.0598] | +0.0322 [-0.0009, +0.0619] | -0.0038 [-0.0222, +0.0121] | +0.1638 [+0.0993, +0.2249] | +0.0639 [+0.0252, +0.1040] |
| rare_logistic_class_weight+recalibrated | -0.0539 [-0.1350, +0.0214] | +0.0350 [+0.0264, +0.0432] | +0.0138 [+0.0121, +0.0156] | +0.0049 [+0.0008, +0.0096] | +0.0298 [+0.0076, +0.0579] | +0.0313 [+0.0016, +0.0604] | -0.0046 [-0.0225, +0.0121] | +0.1613 [+0.0959, +0.2286] | +0.0583 [+0.0220, +0.0983] |
| scarcity_gbm | +0.0253 [+0.0036, +0.0493] | +0.0277 [+0.0171, +0.0376] | +0.0137 [+0.0119, +0.0156] | +0.0003 [-0.0052, +0.0046] | +0.0336 [+0.0038, +0.0708] | +0.0366 [+0.0184, +0.0581] | +0.0146 [+0.0083, +0.0218] | +0.0734 [-0.0270, +0.1663] | +0.0449 [+0.0297, +0.0610] |
| scarcity_gbm_interactions | +0.0253 [+0.0021, +0.0488] | +0.0277 [+0.0164, +0.0380] | +0.0137 [+0.0120, +0.0157] | +0.0002 [-0.0052, +0.0044] | +0.0338 [+0.0039, +0.0714] | +0.0365 [+0.0187, +0.0584] | +0.0146 [+0.0079, +0.0216] | +0.0729 [-0.0284, +0.1636] | +0.0447 [+0.0299, +0.0613] |
| scarcity_logistic | +0.0280 [+0.0063, +0.0536] | +0.0171 [+0.0033, +0.0296] | +0.0137 [+0.0120, +0.0155] | +0.0013 [-0.0040, +0.0053] | +0.0380 [+0.0067, +0.0757] | +0.0443 [+0.0233, +0.0694] | +0.0126 [+0.0064, +0.0198] | +0.0957 [+0.0480, +0.1406] | +0.0563 [+0.0325, +0.0826] |
| scarcity_logistic_interactions | +0.0243 [+0.0022, +0.0477] | +0.0179 [+0.0050, +0.0296] | +0.0136 [+0.0117, +0.0154] | +0.0013 [-0.0038, +0.0053] | +0.0346 [+0.0037, +0.0735] | +0.0438 [+0.0240, +0.0678] | +0.0123 [+0.0065, +0.0189] | +0.0462 [-0.0256, +0.1140] | +0.0556 [+0.0324, +0.0801] |
| scarcity_logistic_regime_pooled | +0.0267 [+0.0044, +0.0531] | +0.0191 [+0.0048, +0.0319] | +0.0137 [+0.0120, +0.0155] | +0.0037 [+0.0002, +0.0065] | +0.0394 [+0.0081, +0.0797] | +0.0450 [+0.0229, +0.0707] | +0.0129 [+0.0066, +0.0205] | +0.0997 [+0.0463, +0.1541] | +0.0585 [+0.0325, +0.0886] |
| settlement_probit_scarcity | +0.0285 [-0.0131, +0.0771] | +0.0301 [+0.0185, +0.0415] | +0.0138 [+0.0121, +0.0158] | +0.0042 [-0.0001, +0.0076] | +0.0156 [+0.0008, +0.0359] | +0.0419 [+0.0201, +0.0654] | +0.0114 [+0.0018, +0.0224] | +0.1034 [+0.0496, +0.1529] | +0.0650 [+0.0296, +0.1032] |
| settlement_probit_tga | +0.0233 [-0.0225, +0.0717] | +0.0309 [+0.0201, +0.0412] | +0.0138 [+0.0121, +0.0157] | +0.0046 [+0.0006, +0.0087] | +0.0160 [+0.0007, +0.0369] | +0.0435 [+0.0208, +0.0656] | +0.0099 [-0.0001, +0.0206] | +0.1101 [+0.0557, +0.1601] | +0.0689 [+0.0346, +0.1082] |
| settlement_probit_timing | +0.0381 [+0.0209, +0.0559] | -0.0066 [-0.0152, +0.0020] | +0.0100 [+0.0088, +0.0113] | +0.0035 [+0.0012, +0.0065] | +0.0304 [+0.0059, +0.0624] | +0.0236 [-0.0011, +0.0520] | +0.0133 [+0.0087, +0.0187] | -0.0068 [-0.0726, +0.0583] | +0.0444 [+0.0274, +0.0639] |
| settlement_quantile_scarcity | +0.0504 [+0.0145, +0.0914] | +0.0237 [+0.0104, +0.0359] | +0.0136 [+0.0118, +0.0156] | +0.0019 [-0.0032, +0.0055] | +0.0350 [+0.0060, +0.0722] | +0.0513 [+0.0192, +0.0837] | +0.0174 [+0.0089, +0.0271] | +0.0652 [-0.0038, +0.1266] | +0.0753 [+0.0330, +0.1188] |
| settlement_quantile_tga | +0.0405 [+0.0038, +0.0837] | +0.0107 [-0.0133, +0.0304] | +0.0136 [+0.0119, +0.0156] | +0.0024 [-0.0024, +0.0056] | +0.0352 [+0.0072, +0.0689] | +0.0425 [+0.0081, +0.0787] | +0.0141 [+0.0056, +0.0238] | +0.0629 [-0.0058, +0.1227] | +0.0726 [+0.0320, +0.1167] |
| settlement_quantile_timing | +0.0522 [+0.0263, +0.0803] | +0.0049 [-0.0050, +0.0149] | +0.0093 [+0.0083, +0.0105] | -0.0011 [-0.0082, +0.0038] | +0.0320 [+0.0001, +0.0721] | +0.0337 [+0.0033, +0.0676] | +0.0165 [+0.0096, +0.0247] | -0.0228 [-0.0831, +0.0330] | +0.0523 [+0.0344, +0.0732] |
| time_to_pressure_hazard | +0.0265 [-0.0081, +0.0667] | +0.0338 [+0.0237, +0.0442] | +0.0138 [+0.0121, +0.0157] | +0.0019 [-0.0027, +0.0053] | +0.0036 [-0.0037, +0.0115] | +0.0209 [+0.0056, +0.0349] | +0.0119 [+0.0047, +0.0203] | +0.0928 [+0.0465, +0.1330] | +0.0565 [+0.0216, +0.0945] |
| two_part_gbm | +0.0459 [+0.0147, +0.0821] | +0.0338 [+0.0187, +0.0466] | +0.0138 [+0.0121, +0.0157] | +0.0016 [-0.0029, +0.0052] | +0.0185 [-0.0013, +0.0446] | +0.0499 [+0.0247, +0.0784] | +0.0149 [+0.0077, +0.0231] | +0.1213 [+0.0296, +0.2096] | +0.0672 [+0.0447, +0.0923] |
| two_part_logistic | +0.0463 [+0.0111, +0.0810] | +0.0297 [+0.0176, +0.0403] | +0.0138 [+0.0121, +0.0157] | +0.0027 [-0.0007, +0.0055] | +0.0090 [+0.0010, +0.0201] | +0.0301 [+0.0096, +0.0506] | +0.0155 [+0.0080, +0.0234] | +0.0930 [+0.0431, +0.1368] | +0.0648 [+0.0325, +0.0969] |

Table 1 is the judge's own verdicts. "Worst flags per 252 days" is the largest over the leads. "Calibrated regimes with pressure"
is at h = 1: the number of regimes with a pressure day whose interval for realised minus predicted covers zero, out of those
regimes. In Table 2 a cell is the share of the group's pressure days that were flagged, and the bracket is how many pressure days
the group has. 2021-23 had none.
