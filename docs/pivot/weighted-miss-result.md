# Weighted miss criteria for the pressure judge: every candidate under both rules (#454)

A scratch measurement for the draft decision record [`docs/decisions/weighted-miss.md`](../decisions/weighted-miss.md),
which is **a draft for Eleonora's review and in force only once she merges it**. It writes nothing into `docs/runs/`
and moves no published figure: the switch in `metadata/weighted_miss.json` is off (`in_force` false), so the judge on
`main` counts every false alarm as 1. Scored days 2018-06-29 to 2025-12-31, h = 1 to 5, +5 bp primary, 90%
stationary-bootstrap intervals. No comparison scores a locked day (`docs/decisions/lockbox.md`); the 2026 confirmation
tier is not opened, and `scripts/pressure_judge.py judge` refuses to force the weighted rule on it.

**The rule under test** (the draft): a flag on a day that is not a pressure day is a false alarm of weight 0.25 within 2
trading days of the nearest pressure day, 0.5 within 3 to 5, and 1 beyond (or with none in reach). The limit stays at 2
per onset. Under it the flag cut-off of each refit is chosen on the weighted count of its training window, using the
pressure days known at the refit's first decision instant only; tier 1 reads the weighted count of the scored days
(a test-only reading of the full outcome record).

**What was scored.** Every candidate declared in `metadata/pressure_judge/candidates/` on `main` (#446's one-file layout),
benchmarks and the published baseline included. Each track's forecasts come from that track's own script on `main`,
unchanged. Candidates of open track pull requests that are not declared on `main` (the quantile regression forest and
the natural-gradient boosting rows of #413) are not scored. The unweighted run reproduces the re-judge of
[`judge-amendment-result.md`](judge-amendment-result.md) where the same candidates appear (for example
`hierarchical_logistic` warns 15 of 26 onsets at 3.65 false alarms per onset, `published_v1` 2 of 26 at 2.35).

## Result

Table 1. Tier 1 (onset warning, lead at least 1), tiers 3 and 5, for each candidate under each rule. False alarms per
onset are the worst horizon's, shown as flat count / weighted count; each rule chooses its own flag cut-offs. The pass
rule is tiers 1, 3 and 5 together.


| candidate | onsets | warned, unweighted rule | warned, weighted rule | FA/onset, unweighted rule (flat / weighted) | FA/onset, weighted rule (flat / weighted) | tier 1, unweighted | tier 1, weighted | tier 3 (unw. / w.) | tier 5 (unw. / w.) |
|---|---|---|---|---|---|---|---|---|---|
| balance_sheet_hierarchical_logistic | 26 | 12 | 15 | 2.15 / 0.84 | 5.08 / 2.24 | fail | fail | fail / fail | pass / pass |
| balance_sheet_scarcity_gbm | 26 | 10 | 13 | 2.15 / 0.77 | 5.27 / 2.35 | fail | fail | fail / fail | pass / pass |
| base_adaptive_offset | 26 | 4 | 5 | 0.85 / 0.41 | 1.19 / 0.56 | fail | fail | fail / fail | pass / pass |
| base_online_platt | 26 | 3 | 4 | 0.77 / 0.38 | 0.85 / 0.39 | fail | fail | fail / fail | pass / pass |
| calendar_climatology | 26 | 10 | 12 | 5.00 / 2.80 | 6.69 / 3.75 | fail | fail | fail / fail | fail / fail |
| extreme_value_tail | 26 | 9 | 11 | 2.31 / 0.75 | 5.04 / 2.23 | fail | fail | fail / fail | fail / fail |
| hierarchical_logistic | 26 | 15 | 15 | 3.65 / 1.31 | 6.23 / 2.91 | fail | fail | fail / fail | fail / fail |
| hierarchical_logistic_fed_repo | 26 | 14 | 15 | 3.73 / 1.56 | 5.65 / 2.68 | fail | fail | fail / fail | fail / fail |
| hierarchical_logistic_fed_repo_sameday | 26 | 15 | 15 | 3.85 / 1.58 | 5.92 / 2.81 | fail | fail | fail / fail | pass / pass |
| hierarchical_logistic_net | 26 | 14 | 15 | 3.38 / 1.27 | 5.46 / 2.51 | fail | fail | fail / fail | fail / fail |
| hierarchical_logistic_srf | 26 | 15 | 15 | 3.81 / 1.54 | 5.65 / 2.69 | fail | fail | fail / fail | fail / fail |
| hierarchical_logistic_srf_sameday | 26 | 15 | 15 | 4.08 / 1.75 | 5.69 / 2.72 | fail | fail | fail / fail | fail / fail |
| onset_gbm_class_weight+recalibrated | 26 | 8 | 9 | 3.42 / 1.82 | 4.65 / 2.74 | fail | fail | fail / fail | pass / pass |
| onset_gbm_class_weight_funding+recalibrated | 26 | 8 | 9 | 3.38 / 1.78 | 4.62 / 2.73 | fail | fail | fail / fail | pass / pass |
| onset_gbm_focal+recalibrated | 26 | 10 | 13 | 2.85 / 1.68 | 4.58 / 2.56 | fail | fail | fail / fail | pass / pass |
| onset_logistic+recalibrated | 26 | 11 | 14 | 3.54 / 1.80 | 5.77 / 3.28 | fail | fail | fail / fail | fail / fail |
| onset_logistic_class_weight+recalibrated | 26 | 6 | 10 | 0.81 / 0.30 | 2.92 / 1.58 | fail | fail | fail / fail | pass / pass |
| onset_logistic_class_weight_funding+recalibrated | 26 | 5 | 11 | 0.77 / 0.29 | 2.85 / 1.57 | fail | fail | fail / fail | pass / pass |
| onset_logistic_net+recalibrated | 26 | 11 | 13 | 2.81 / 1.40 | 5.27 / 2.84 | fail | fail | fail / fail | pass / pass |
| onset_logistic_policy+recalibrated | 26 | 15 | 17 | 3.23 / 1.53 | 6.12 / 3.21 | fail | fail | fail / fail | fail / fail |
| persistence_logistic | 26 | 7 | 12 | 3.42 / 1.17 | 7.04 / 3.25 | fail | fail | fail / fail | fail / fail |
| published_v1 | 26 | 2 | 14 | 2.35 / 0.79 | 5.73 / 2.38 | fail | fail | fail / fail | fail / fail |
| published_v1_nowcast | 26 | 4 | 13 | 2.38 / 0.83 | 5.46 / 2.28 | fail | fail | fail / fail | fail / fail |
| published_v1_nowcast_substituted | 26 | 6 | 10 | 2.96 / 1.24 | 5.96 / 2.90 | fail | fail | fail / fail | fail / fail |
| rare_gbm_balanced_bootstrap+recalibrated | 26 | 7 | 7 | 1.19 / 0.53 | 2.19 / 0.85 | fail | fail | fail / fail | pass / pass |
| rare_gbm_balanced_bootstrap_policy+recalibrated | 26 | 6 | 12 | 1.65 / 0.72 | 2.92 / 1.37 | fail | fail | fail / fail | pass / pass |
| rare_gbm_class_weight+recalibrated | 26 | 6 | 12 | 1.46 / 0.63 | 5.12 / 2.16 | fail | fail | fail / fail | pass / pass |
| rare_gbm_focal+recalibrated | 26 | 7 | 13 | 1.58 / 0.64 | 4.15 / 1.66 | fail | pass | fail / fail | pass / pass |
| rare_logistic_balanced_bootstrap+recalibrated | 26 | 3 | 4 | 0.65 / 0.35 | 0.96 / 0.42 | fail | fail | fail / fail | pass / pass |
| rare_logistic_class_weight+recalibrated | 26 | 3 | 5 | 0.77 / 0.38 | 0.96 / 0.42 | fail | fail | fail / fail | pass / pass |
| recal_isotonic | 26 | 3 | 13 | 2.42 / 0.85 | 5.69 / 2.42 | fail | fail | fail / fail | fail / fail |
| recal_platt | 26 | 2 | 14 | 2.35 / 0.79 | 5.73 / 2.38 | fail | fail | fail / fail | fail / fail |
| recal_platt_group | 26 | 5 | 15 | 2.77 / 0.93 | 5.62 / 2.35 | fail | fail | fail / fail | fail / fail |
| recal_platt_weighted | 26 | 5 | 14 | 2.77 / 0.93 | 5.92 / 2.61 | fail | fail | fail / fail | fail / fail |
| recency_decay_126+recalibrated | 26 | 4 | 4 | 0.35 / 0.09 | 0.88 / 0.29 | fail | fail | fail / fail | pass / pass |
| recency_decay_252+recalibrated | 26 | 4 | 4 | 0.54 / 0.19 | 1.08 / 0.38 | fail | fail | fail / fail | pass / pass |
| recency_decay_63+recalibrated | 26 | 3 | 4 | 0.38 / 0.12 | 0.58 / 0.22 | fail | fail | fail / fail | pass / pass |
| recency_window_252+recalibrated | 26 | 3 | 6 | 0.77 / 0.38 | 1.35 / 0.56 | fail | fail | fail / fail | pass / pass |
| recency_window_504+recalibrated | 26 | 3 | 6 | 0.81 / 0.38 | 1.62 / 0.62 | fail | fail | fail / fail | pass / pass |
| risk_gbm | 26 | 13 | 13 | 1.35 / 0.76 | 1.38 / 0.80 | pass | pass | fail / fail | fail / fail |
| risk_gbm_base | 26 | 14 | 14 | 1.50 / 0.97 | 1.50 / 0.97 | pass | pass | fail / fail | fail / fail |
| risk_logistic | 26 | 14 | 16 | 1.85 / 1.19 | 2.42 / 1.74 | pass | pass | fail / fail | fail / fail |
| risk_logistic_base | 26 | 13 | 15 | 1.77 / 1.16 | 2.31 / 1.65 | pass | pass | fail / fail | fail / fail |
| risk_quantile_skewt | 26 | 13 | 14 | 2.54 / 1.96 | 3.42 / 2.85 | fail | fail | fail / fail | fail / fail |
| risk_quantile_skewt_base | 26 | 14 | 15 | 1.88 / 1.25 | 2.31 / 1.62 | pass | pass | fail / fail | fail / fail |
| scarcity_gbm | 26 | 10 | 13 | 2.65 / 1.20 | 5.08 / 2.36 | fail | fail | fail / fail | fail / fail |
| scarcity_gbm_interactions | 26 | 10 | 13 | 2.65 / 1.20 | 5.08 / 2.36 | fail | fail | fail / fail | fail / fail |
| scarcity_logistic | 26 | 13 | 13 | 3.23 / 1.23 | 4.73 / 2.09 | fail | fail | fail / fail | fail / fail |
| scarcity_logistic_interactions | 26 | 14 | 14 | 3.23 / 1.23 | 5.50 / 2.39 | fail | fail | fail / fail | fail / fail |
| scarcity_logistic_regime_pooled | 26 | 13 | 13 | 3.23 / 1.22 | 5.19 / 2.54 | fail | fail | fail / fail | fail / fail |
| settlement_probit_scarcity | 26 | 8 | 11 | 1.58 / 0.57 | 3.42 / 1.48 | fail | fail | fail / fail | fail / fail |
| settlement_probit_tga | 26 | 9 | 11 | 1.73 / 0.70 | 2.81 / 1.19 | fail | fail | fail / fail | fail / fail |
| settlement_probit_timing | 26 | 13 | 16 | 3.46 / 1.97 | 5.42 / 3.11 | fail | fail | fail / fail | pass / pass |
| settlement_quantile_scarcity | 26 | 10 | 12 | 2.38 / 0.87 | 4.54 / 2.04 | fail | fail | fail / fail | pass / pass |
| settlement_quantile_tga | 26 | 9 | 12 | 2.27 / 1.09 | 4.88 / 2.57 | fail | fail | fail / fail | pass / pass |
| settlement_quantile_timing | 26 | 15 | 16 | 3.65 / 1.68 | 6.38 / 3.41 | fail | fail | fail / fail | pass / pass |
| stack_equal_average | 26 | 12 | 16 | 3.23 / 1.32 | 5.04 / 2.21 | fail | fail | fail / fail | fail / fail |
| stacked_ensemble | 26 | 15 | 16 | 3.27 / 1.23 | 5.42 / 2.31 | fail | fail | fail / fail | fail / fail |
| time_to_pressure_hazard | 26 | 7 | 9 | 2.19 / 0.75 | 3.77 / 1.58 | fail | fail | fail / fail | fail / fail |
| two_part_gbm | 26 | 15 | 15 | 2.46 / 1.07 | 4.81 / 2.55 | fail | fail | fail / fail | fail / fail |
| two_part_logistic | 26 | 10 | 14 | 2.00 / 0.73 | 3.96 / 1.68 | fail | pass | fail / fail | fail / fail |


Table 2. The same evidence split by regime for the candidates that pass tier 1 under either rule, plus
`calendar_climatology`, `published_v1` and `hierarchical_logistic`. The false-alarm cell is the worst horizon within the
regime (flat count / weighted count). 2021-23 had no onset. The full split for every candidate is in
[`evidence/weighted-miss/table.md`](evidence/weighted-miss/table.md).

| candidate | regime | onsets | warned, unweighted rule | warned, weighted rule | false alarms, unweighted rule (flat / weighted) | false alarms, weighted rule (flat / weighted) |
|---|---|---|---|---|---|---|
| calendar_climatology | 2018-19 | 17 | 10 | 12 | 96 / 39.75 | 132 / 56.50 |
| calendar_climatology | 2020 | 2 | 0 | 0 | 21 / 20.00 | 28 / 27.00 |
| calendar_climatology | 2021-23 | 0 | 0 | 0 | 13 / 13.00 | 14 / 14.00 |
| calendar_climatology | 2024 | 2 | 0 | 0 | 0 / 0.00 | 0 / 0.00 |
| calendar_climatology | 2025-26 | 5 | 0 | 0 | 0 / 0.00 | 0 / 0.00 |
| published_v1 | 2018-19 | 17 | 2 | 12 | 49 / 17.00 | 125 / 53.75 |
| published_v1 | 2020 | 2 | 0 | 0 | 2 / 0.50 | 3 / 2.00 |
| published_v1 | 2021-23 | 0 | 0 | 0 | 0 / 0.00 | 0 / 0.00 |
| published_v1 | 2024 | 2 | 0 | 0 | 1 / 0.50 | 3 / 1.00 |
| published_v1 | 2025-26 | 5 | 0 | 2 | 13 / 4.25 | 22 / 7.00 |
| rare_gbm_focal+recalibrated | 2018-19 | 17 | 7 | 12 | 41 / 16.75 | 108 / 43.25 |
| rare_gbm_focal+recalibrated | 2020 | 2 | 0 | 1 | 0 / 0.00 | 3 / 1.00 |
| rare_gbm_focal+recalibrated | 2021-23 | 0 | 0 | 0 | 0 / 0.00 | 0 / 0.00 |
| rare_gbm_focal+recalibrated | 2024 | 2 | 0 | 0 | 0 / 0.00 | 0 / 0.00 |
| rare_gbm_focal+recalibrated | 2025-26 | 5 | 0 | 0 | 0 / 0.00 | 2 / 0.75 |
| two_part_logistic | 2018-19 | 17 | 10 | 13 | 49 / 16.75 | 96 / 39.00 |
| two_part_logistic | 2020 | 2 | 0 | 0 | 3 / 2.25 | 6 / 4.50 |
| two_part_logistic | 2021-23 | 0 | 0 | 0 | 0 / 0.00 | 0 / 0.00 |
| two_part_logistic | 2024 | 2 | 0 | 0 | 0 / 0.00 | 0 / 0.00 |
| two_part_logistic | 2025-26 | 5 | 0 | 1 | 0 / 0.00 | 1 / 0.25 |
| risk_gbm | 2018-19 | 17 | 10 | 10 | 21 / 9.25 | 21 / 9.25 |
| risk_gbm | 2020 | 2 | 0 | 0 | 11 / 10.00 | 13 / 12.00 |
| risk_gbm | 2021-23 | 0 | 0 | 0 | 1 / 1.00 | 2 / 2.00 |
| risk_gbm | 2024 | 2 | 0 | 0 | 1 / 1.00 | 1 / 1.00 |
| risk_gbm | 2025-26 | 5 | 3 | 3 | 5 / 2.75 | 5 / 2.75 |
| risk_logistic | 2018-19 | 17 | 10 | 10 | 25 / 12.00 | 25 / 12.00 |
| risk_logistic | 2020 | 2 | 0 | 0 | 19 / 18.00 | 30 / 29.00 |
| risk_logistic | 2021-23 | 0 | 0 | 0 | 0 / 0.00 | 2 / 2.00 |
| risk_logistic | 2024 | 2 | 0 | 1 | 3 / 2.50 | 4 / 3.25 |
| risk_logistic | 2025-26 | 5 | 4 | 5 | 7 / 4.75 | 11 / 8.75 |
| hierarchical_logistic | 2018-19 | 17 | 12 | 12 | 91 / 32.50 | 146 / 64.75 |
| hierarchical_logistic | 2020 | 2 | 0 | 0 | 2 / 1.25 | 15 / 11.50 |
| hierarchical_logistic | 2021-23 | 0 | 0 | 0 | 0 / 0.00 | 0 / 0.00 |
| hierarchical_logistic | 2024 | 2 | 0 | 0 | 0 / 0.00 | 0 / 0.00 |
| hierarchical_logistic | 2025-26 | 5 | 3 | 3 | 11 / 3.25 | 13 / 3.75 |

## What the table says

* **No candidate passes the pass rule under either rule.** Tier 3 (no crying wolf, with calibration by regime) fails for
  every candidate under both, so a weighted false-alarm count alone does not let a model pass. The weighted rule moves
  tier 1 only.
* **Tier 1 under the weighted rule.** The risk-date severity models that already pass tier 1 under the unweighted rule
  still do. Two more pass under the weighted rule only: `rare_gbm_focal+recalibrated` and `two_part_logistic`.
* **The weighted rule loosens the cut-off rule more than it relaxes the tier.** The weighted count in a refit's training
  window is lower than the flat count, so the chosen cut-off is lower and more onsets are warned (for example
  `published_v1` from 2 to 14 of 26). The same flags then raise more false alarms on the scored days, and for many
  candidates the weighted count per onset at the worst horizon is above 2. The columns "FA/onset" show both counts under
  both rules.
* **Everything sits in 2018-19.** That regime holds the large majority of onsets and false alarms; later regimes have few
  onsets (2020: 2, 2024: 2, 2025-26: 5, 2021-23: none), so a regime split says little outside 2018-19.
* **Not checked:** the weighted rule at +10 bp, and the scarce-regime reading under the weighted rule (its distances are
  among that regime's days only). The weights are the draft's; other bands were not tried, because they are Eleonora's
  to set and trying them here would be choosing a weight on the scored days.

## Reproduce

Panel `4ddc3882…` (the published panel, from the tracked fixtures, `verify-panel` clean). Tracks that score on a
scratch panel use `pressure_v1_1.py panel` (`4137d0ad…`), then `measurement_fields.py panel`, `policy_features.py panel`,
`net_settlement.py panel`, `fed_liquidity.py panel` and `nowcast.py panel` as each track's page says. Each track's forecast
file is written by the command on its own result page (`docs/pivot/*-result.md`) for h = 1 to 5. A forecast file
written on a scratch panel names that panel's digest; give it the published panel's after checking that its dates are the
grid's (the judge refuses a file whose days are not the grid's). Candidates written by more than one track are identical
across the files (the largest difference between copies is 0). Then:

```
PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUB.csv --rule unweighted --output OUT/judge_unweighted.json IN/forecasts_h?.json
PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUB.csv --rule weighted --output OUT/judge_weighted.json IN/forecasts_h?.json
PYTHONPATH=src python3 scripts/weighted_miss.py table OUT/judge_unweighted.json OUT/judge_weighted.json --output OUT/table.md
```

`evidence/weighted-miss/tier1.json` holds each candidate's tier-1 evidence and verdict under both runs.
