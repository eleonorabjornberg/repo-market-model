# Do repeat flags inflate the false alarms? A five-day cool-down on the best six rows (#459)

A scratch measurement. It writes nothing into `docs/runs/` and moves no published figure, declaration or live pin. Scored days are 2018-06-29 to 2025-12-31 only (`docs/decisions/lockbox.md`); the 2026 confirmation window is not looked at. The six rows, the cool-down length (5 trading days, not tuned) and the two forms were declared in `metadata/alarm_cooldown.json`, and each cooled row in a candidate file of its own under `metadata/pressure_judge/candidates/`, committed before anything was scored. The judge applies the rule to a candidate's flags (`pressure_judge.cooldown_flags`, the candidate's `alarm_rule`); `scripts/alarm_cooldown.py` assembles the inputs and writes the tables. Evidence: `docs/pivot/evidence/alarm_cooldown/` (`report.md` and `judge.md` for the unweighted rule, `report_weighted.md` and `judge_weighted.md` for the weighted rule).

## What was scored

* **Rows.** The six candidate rows of Table 1 of the re-judge (`docs/pivot/judge-amendment-result.md`) with the most onsets flagged at lead >= 1, ties broken by the smaller worst false alarms per onset and then by name (the rule of `metadata/onset_diagnostics.json`, six rows instead of five): `two_part_gbm`, `ngboost_laplace`, `hierarchical_logistic`, `settlement_quantile_timing`, `scarcity_logistic_interactions`, `scarcity_logistic`. The sixth place is a tie at Table 1's two decimals (`scarcity_logistic` and `scarcity_logistic_regime_pooled`, 13 onsets, 3.23); the name breaks it. Each base row reproduces its Table 1 line here (onsets flagged, recall and interval, worst false alarms per onset).
* **The rule.** A flag outside every earlier alarm's window raises an alarm. The window is the five days after it. A flag inside the window counts as one alarm with it (is dropped), unless a pressure day starts inside the window, in which case the repeats stay. A repeat never opens a window of its own. It is applied to the base row's flags at +5 bp at each horizon, before every use the judge makes of flags. The probabilities and the cut-offs are the base row's, unchanged: no refit and no new cut-off.
* **Two forms.** `with exception` is the rule as stated. Its exception reads the days after the flag, so it counts alarms on a scored record and is not a rule a forecaster could apply as the days arrive; it never drops the flag on an onset day, so it cannot lower recall. `strict` is the same rule without the exception, the form a live forecaster could apply; it can drop the flag that warns an onset when that flag falls in an earlier alarm's window.
* **Weighted misses.** #454 merged while this was open. Result 1 is under the unweighted rule (the judge on `main`; the weighted count of the same flags is shown in brackets beside the flat count). Result 4 re-scores every row under the weighted-miss rule of the draft record `docs/decisions/weighted-miss.md`, forced on for a scratch run (`pressure_judge.py judge --rule weighted`), which is not in force.

## Result 1: the tier-1 line

Tier 1 at lead >= 1, +5 bp, h = 1 to 5; 90% stationary-bootstrap interval on recall. Tier 3 and tier 5 are the judge's, for the same row.

| row | form | onsets warned | recall [90%] | worst false alarms per onset, flat (weighted) | tier 1 | tier 3 | tier 5 | pass |
|---|---|---|---|---|---|---|---|---|
| two_part_gbm | base | 15 of 26 | 0.577 [0.400, 0.762] | 2.46 (1.07) | no | no | no | no |
| two_part_gbm | with exception | 15 of 26 | 0.577 [0.387, 0.759] | 1.15 (0.42) | yes | no | no | no |
| two_part_gbm | strict | 12 of 26 | 0.462 [0.278, 0.640] | 0.62 (0.26) | no | no | no | no |
| ngboost_laplace | base | 15 of 26 | 0.577 [0.400, 0.759] | 2.54 (1.03) | no | no | no | no |
| ngboost_laplace | with exception | 15 of 26 | 0.577 [0.393, 0.750] | 1.27 (0.44) | yes | no | no | no |
| ngboost_laplace | strict | 10 of 26 | 0.385 [0.217, 0.565] | 0.58 (0.21) | no | no | no | no |
| hierarchical_logistic | base | 15 of 26 | 0.577 [0.400, 0.750] | 3.65 (1.31) | no | no | no | no |
| hierarchical_logistic | with exception | 15 of 26 | 0.577 [0.400, 0.750] | 1.81 (0.65) | yes | no | no | no |
| hierarchical_logistic | strict | 12 of 26 | 0.462 [0.290, 0.647] | 0.96 (0.38) | no | no | no | no |
| settlement_quantile_timing | base | 15 of 26 | 0.577 [0.391, 0.750] | 3.65 (1.68) | no | no | yes | no |
| settlement_quantile_timing | with exception | 15 of 26 | 0.577 [0.400, 0.750] | 1.73 (1.13) | yes | no | yes | no |
| settlement_quantile_timing | strict | 13 of 26 | 0.500 [0.333, 0.667] | 1.38 (1.12) | yes | no | yes | no |
| scarcity_logistic_interactions | base | 14 of 26 | 0.538 [0.346, 0.731] | 3.23 (1.23) | no | no | no | no |
| scarcity_logistic_interactions | with exception | 14 of 26 | 0.538 [0.353, 0.722] | 1.54 (0.54) | yes | no | no | no |
| scarcity_logistic_interactions | strict | 12 of 26 | 0.462 [0.280, 0.652] | 0.88 (0.33) | no | no | no | no |
| scarcity_logistic | base | 13 of 26 | 0.500 [0.320, 0.696] | 3.23 (1.23) | no | no | no | no |
| scarcity_logistic | with exception | 13 of 26 | 0.500 [0.316, 0.692] | 1.42 (0.54) | yes | no | no | no |
| scarcity_logistic | strict | 12 of 26 | 0.462 [0.281, 0.640] | 0.81 (0.33) | no | no | no | no |

* **With the exception, every row's false alarms per onset fall to at most 1.81 and all six pass tier 1** (recall at least 0.5 and above climatology's at the same false alarms, false alarms at most 2 per onset). Onsets warned do not change, by construction. No row passes the full rule: tier 3 fails at one or more horizons for every row, as it did for the base rows, and tier 5 fails for five of six. The rule does not touch the probabilities, so the calibration conditions of both tiers do not move; the flags-per-year condition of tier 3 is met by base and cooled alike.
* **Strict, one row passes tier 1: `settlement_quantile_timing`** (13 of 26 warned, 0.500 [0.333, 0.667], worst false alarms per onset 1.38). The other five lose one to five onsets (10 to 12 of 26 warned) and fall below the recall limit: the warning they gave came as a repeat inside an earlier alarm's window.
* The pass of `settlement_quantile_timing` strict sits exactly on the recall limit (13 of 26 is 0.500), and the row fails tier 3 (calibration in 2018-19 and 2020).

## Result 2: false alarms per onset by horizon

| row | form | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|---|
| two_part_gbm | base | 0.23 | 1.15 | 1.58 | 1.35 | 2.46 |
| two_part_gbm | with exception | 0.15 | 0.77 | 0.81 | 0.62 | 1.15 |
| two_part_gbm | strict | 0.15 | 0.42 | 0.46 | 0.42 | 0.62 |
| ngboost_laplace | base | 1.69 | 1.73 | 1.42 | 2.54 | 1.58 |
| ngboost_laplace | with exception | 0.38 | 0.65 | 0.54 | 1.27 | 0.62 |
| ngboost_laplace | strict | 0.35 | 0.46 | 0.35 | 0.58 | 0.38 |
| hierarchical_logistic | base | 3.08 | 1.81 | 3.15 | 3.00 | 3.65 |
| hierarchical_logistic | with exception | 1.46 | 0.81 | 0.81 | 1.00 | 1.81 |
| hierarchical_logistic | strict | 0.81 | 0.38 | 0.50 | 0.62 | 0.96 |
| settlement_quantile_timing | base | 2.92 | 2.69 | 3.50 | 3.54 | 3.65 |
| settlement_quantile_timing | with exception | 1.42 | 1.15 | 1.69 | 1.62 | 1.73 |
| settlement_quantile_timing | strict | 1.38 | 1.00 | 1.19 | 1.27 | 1.23 |
| scarcity_logistic_interactions | base | 3.19 | 2.00 | 3.15 | 3.00 | 3.23 |
| scarcity_logistic_interactions | with exception | 1.54 | 0.77 | 0.81 | 1.00 | 1.42 |
| scarcity_logistic_interactions | strict | 0.88 | 0.35 | 0.50 | 0.62 | 0.81 |
| scarcity_logistic | base | 2.85 | 2.00 | 3.15 | 3.00 | 3.23 |
| scarcity_logistic | with exception | 1.38 | 0.77 | 0.81 | 1.00 | 1.42 |
| scarcity_logistic | strict | 0.77 | 0.35 | 0.50 | 0.62 | 0.81 |

The worst horizon is h = 5 for most rows, base and cooled. With the exception the cool-down roughly halves the worst false alarms per onset (by 50% to 56%); strict it cuts them by 62% to 77%.

## Result 3: where the alarms fall (h = 1; alarms, of them false alarms)

By regime:

| row | form | 2018-19 | 2020 | 2021-23 | 2024 | 2025-26 |
|---|---|---|---|---|---|---|
| two_part_gbm | base | 28 (2) | 2 (1) | 0 (0) | 0 (0) | 9 (3) |
| two_part_gbm | with exception | 19 (2) | 2 (1) | 0 (0) | 0 (0) | 6 (1) |
| two_part_gbm | strict | 19 (2) | 2 (1) | 0 (0) | 0 (0) | 3 (1) |
| ngboost_laplace | base | 97 (41) | 3 (2) | 0 (0) | 1 (0) | 11 (1) |
| ngboost_laplace | with exception | 27 (8) | 3 (2) | 0 (0) | 1 (0) | 7 (0) |
| ngboost_laplace | strict | 24 (7) | 3 (2) | 0 (0) | 1 (0) | 7 (0) |
| hierarchical_logistic | base | 136 (67) | 2 (2) | 0 (0) | 0 (0) | 26 (11) |
| hierarchical_logistic | with exception | 55 (33) | 2 (2) | 0 (0) | 0 (0) | 11 (3) |
| hierarchical_logistic | strict | 29 (16) | 2 (2) | 0 (0) | 0 (0) | 8 (3) |
| settlement_quantile_timing | base | 96 (36) | 23 (22) | 5 (5) | 3 (2) | 26 (11) |
| settlement_quantile_timing | with exception | 34 (7) | 21 (20) | 5 (5) | 2 (2) | 8 (3) |
| settlement_quantile_timing | strict | 31 (7) | 20 (19) | 5 (5) | 2 (2) | 8 (3) |
| scarcity_logistic_interactions | base | 137 (70) | 1 (1) | 0 (0) | 0 (0) | 26 (12) |
| scarcity_logistic_interactions | with exception | 59 (35) | 1 (1) | 0 (0) | 0 (0) | 11 (4) |
| scarcity_logistic_interactions | strict | 33 (18) | 1 (1) | 0 (0) | 0 (0) | 8 (4) |
| scarcity_logistic | base | 125 (61) | 2 (2) | 0 (0) | 0 (0) | 25 (11) |
| scarcity_logistic | with exception | 53 (32) | 2 (2) | 0 (0) | 0 (0) | 10 (2) |
| scarcity_logistic | strict | 29 (16) | 2 (2) | 0 (0) | 0 (0) | 7 (2) |

By pressure-day type:

| row | form | month_end | ordinary | quarter_end | tax_date |
|---|---|---|---|---|---|
| two_part_gbm | base | 10 (2) | 20 (4) | 4 (0) | 5 (0) |
| two_part_gbm | with exception | 10 (2) | 9 (2) | 3 (0) | 5 (0) |
| two_part_gbm | strict | 9 (2) | 8 (2) | 2 (0) | 5 (0) |
| ngboost_laplace | base | 15 (5) | 83 (37) | 6 (0) | 8 (2) |
| ngboost_laplace | with exception | 9 (2) | 22 (8) | 3 (0) | 4 (0) |
| ngboost_laplace | strict | 9 (2) | 20 (7) | 2 (0) | 4 (0) |
| hierarchical_logistic | base | 17 (5) | 125 (67) | 7 (2) | 15 (6) |
| hierarchical_logistic | with exception | 8 (3) | 48 (31) | 6 (2) | 6 (2) |
| hierarchical_logistic | strict | 2 (1) | 29 (18) | 5 (2) | 3 (0) |
| settlement_quantile_timing | base | 19 (8) | 107 (56) | 17 (10) | 10 (2) |
| settlement_quantile_timing | with exception | 15 (7) | 36 (19) | 14 (10) | 5 (1) |
| settlement_quantile_timing | strict | 15 (7) | 32 (18) | 14 (10) | 5 (1) |
| scarcity_logistic_interactions | base | 17 (4) | 127 (72) | 5 (1) | 15 (6) |
| scarcity_logistic_interactions | with exception | 9 (3) | 52 (34) | 4 (1) | 6 (2) |
| scarcity_logistic_interactions | strict | 3 (1) | 33 (21) | 3 (1) | 3 (0) |
| scarcity_logistic | base | 16 (4) | 114 (62) | 7 (2) | 15 (6) |
| scarcity_logistic | with exception | 9 (3) | 44 (29) | 6 (2) | 6 (2) |
| scarcity_logistic | strict | 3 (1) | 27 (17) | 5 (2) | 3 (0) |


Most of the false alarms removed are in 2018-19, which holds most of the pressure days (102 of the 140 in Table 2 of the re-judge): the repeats sit beside the pressure days, as `docs/pivot/onset-diagnostics-result.md` found. `settlement_quantile_timing` keeps 19 or 20 of its 22 false alarms in 2020 under either form: they are single flags, not repeats.

## Result 4: the same rows under the weighted-miss rule (#454, a draft, forced on)

Under the draft rule a false alarm within 2 trading days of a pressure day counts 0.25, within 3 to 5 days 0.5, and 1 beyond; the limit stays at 2 per onset, and each row's flag cut-offs are chosen on the weighted count of the training window. The cool-down is applied to the flags as before, then the weights. Cells: flat false alarms per onset (weighted).

| row | form | onsets warned | recall [90%] | worst false alarms per onset, flat (weighted) | tier 1 | tier 3 | tier 5 | pass |
|---|---|---|---|---|---|---|---|---|
| two_part_gbm | base | 15 of 26 | 0.577 [0.400, 0.762] | 4.81 (2.55) | no | no | no | no |
| two_part_gbm | with exception | 15 of 26 | 0.577 [0.387, 0.759] | 2.00 (0.83) | yes | no | no | no |
| two_part_gbm | strict | 11 of 26 | 0.423 [0.235, 0.600] | 1.12 (0.56) | no | no | no | no |
| ngboost_laplace | base | 17 of 26 | 0.654 [0.467, 0.826] | 4.08 (1.73) | yes | no | no | no |
| ngboost_laplace | with exception | 17 of 26 | 0.654 [0.474, 0.828] | 1.73 (0.61) | yes | no | no | no |
| ngboost_laplace | strict | 11 of 26 | 0.423 [0.250, 0.609] | 0.85 (0.42) | no | no | no | no |
| hierarchical_logistic | base | 15 of 26 | 0.577 [0.400, 0.750] | 6.23 (2.91) | no | no | no | no |
| hierarchical_logistic | with exception | 15 of 26 | 0.577 [0.400, 0.750] | 2.46 (0.90) | yes | no | no | no |
| hierarchical_logistic | strict | 10 of 26 | 0.385 [0.217, 0.560] | 1.12 (0.52) | no | no | no | no |
| settlement_quantile_timing | base | 16 of 26 | 0.615 [0.444, 0.778] | 6.38 (3.41) | no | no | yes | no |
| settlement_quantile_timing | with exception | 16 of 26 | 0.615 [0.448, 0.778] | 2.85 (1.80) | yes | no | yes | no |
| settlement_quantile_timing | strict | 10 of 26 | 0.385 [0.217, 0.548] | 2.19 (1.72) | no | no | yes | no |
| scarcity_logistic_interactions | base | 14 of 26 | 0.538 [0.346, 0.731] | 5.50 (2.39) | no | no | no | no |
| scarcity_logistic_interactions | with exception | 14 of 26 | 0.538 [0.353, 0.722] | 2.04 (0.71) | yes | no | no | no |
| scarcity_logistic_interactions | strict | 9 of 26 | 0.346 [0.185, 0.524] | 1.15 (0.48) | no | no | no | no |
| scarcity_logistic | base | 13 of 26 | 0.500 [0.320, 0.696] | 4.73 (2.09) | no | no | no | no |
| scarcity_logistic | with exception | 13 of 26 | 0.500 [0.316, 0.692] | 1.85 (0.66) | yes | no | no | no |
| scarcity_logistic | strict | 10 of 26 | 0.385 [0.217, 0.556] | 0.92 (0.40) | no | no | no | no |

* With the exception, all six rows pass tier 1 under the weighted rule too. `ngboost_laplace`'s base row already passes tier 1 under the weighted rule (17 of 26 warned), so for it the cool-down is not what makes tier 1 pass.
* **Strict, no row passes tier 1 under the weighted rule.** The weighted cut-offs are lower and flag more often; the strict form drops the warning of many onsets that arrive as repeats (9 to 11 of 26 warned for every row). `settlement_quantile_timing`, the one strict pass under the unweighted rule, falls to 10 of 26.
* No row passes the full pass rule: tier 3 fails for every row.
* The tables by horizon, regime and pressure-day type are in `docs/pivot/evidence/alarm_cooldown/report_weighted.md`; the judge's full output is `judge_weighted.md`.

## What this does not show

* **The exception is not available live.** Every pass of tier 1 with the exception rests on a rule that reads whether a pressure day starts in the next five days. The only form a forecaster could apply as the days arrive is the strict one, and it passes tier 1 for one row, at the recall limit.
* **26 onsets.** A recall of 13 of 26 against a limit of 13 of 26 is a coin toss in the sense of `docs/pivot/onset-diagnostics-result.md`; one onset moves the verdict. The confirmation window cannot test it under the declared interval rule.
* **The cut-offs were chosen for the uncooled flags.** A cut-off chosen on the cooled false alarms of the training window would admit more flags per onset and could raise recall; that is a different candidate and was not scored.
* **The window length is 5 and not tuned.** The tables do not show whether 3 or 10 days would do better, and are not meant to.
* **Tiers 3 and 5 do not move on calibration and the week-ahead window**, so the pass rule is not met by any row.

## Reproduce

Published panel `4ddc3882…` (rebuilt from the tracked fixtures); scratch panels `AUG.csv` (`pressure_v1_1.py panel`, digest `4137d0ad…`) and `AUG2.csv` (`measurement_fields.py panel`). Run with `OMP_NUM_THREADS=1` and `/opt/rmm-venv/bin/python`.

```
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
for h in 1 2 3 4 5:
  PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUB.csv --horizon $h --output OUT/bench_h$h.json
  PYTHONPATH=src python3 scripts/hierarchical_logistic.py forecasts --panel AUG.csv --horizon $h --output OUT/hl_h$h.json
  PYTHONPATH=src python3 scripts/settlement_timing.py run --panel AUG2.csv --published PUB.csv --candidate settlement_quantile_timing --horizon $h --output OUT/sqt_h$h.json
  PYTHONPATH=src python3 scripts/scarcity_event_bar.py forecasts --panel AUG.csv --horizon $h --candidate scarcity_logistic_interactions --output OUT/sli_h$h.json
  PYTHONPATH=src python3 scripts/scarcity_event_bar.py forecasts --panel AUG.csv --horizon $h --candidate scarcity_logistic --output OUT/sl_h$h.json
  PYTHONPATH=src python3 scripts/pressure_two_part.py horizon --panel PUB.csv --horizon $h --output OUT/tp_h$h.json
  PYTHONPATH=src python3 scripts/pressure_track_q.py forecasts --panel PUB.csv --horizon $h --output OUT/q_h$h.json --distribution OUT/qdist_h$h.json
PYTHONPATH=src python3 scripts/alarm_cooldown.py assemble --panel PUB.csv --bench 'OUT/bench_h{h}.json' \
    --row two_part_gbm='OUT/tp_h{h}.json' --row ngboost_laplace='OUT/q_h{h}.json' --row hierarchical_logistic='OUT/hl_h{h}.json' \
    --row settlement_quantile_timing='OUT/sqt_h{h}.json' --row scarcity_logistic_interactions='OUT/sli_h{h}.json' \
    --row scarcity_logistic='OUT/sl_h{h}.json' --output 'OUT/cd_h{h}.json'
PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUB.csv --output OUT/judge.json --markdown OUT/judge.md OUT/cd_h?.json
PYTHONPATH=src python3 scripts/alarm_cooldown.py report OUT/judge.json --output OUT/report.json --markdown OUT/report.md
PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUB.csv --rule weighted --output OUT/judge_w.json --markdown OUT/judge_w.md OUT/cd_h?.json
PYTHONPATH=src python3 scripts/alarm_cooldown.py report OUT/judge_w.json --output OUT/report_w.json --markdown OUT/report_w.md
```
