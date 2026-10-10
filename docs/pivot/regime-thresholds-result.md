# A separate warning cut-off when the as-of scarcity state is at least 2 (#461)

A scratch measurement under the judge of #375 as amended by #407, unchanged. For the six best candidate rows of Table 1 of
`docs/pivot/judge-amendment-result.md`, the flag cut-off on days whose **as-of** reserve scarcity state is at least 2 is chosen
by the judge's own rule and limit (`cutoff_rule`: the highest onset recall whose false alarms per onset are at most 2) on the
refit's training days in that state alone. Days in a lower state, and days whose state is unknown, keep the cut-off chosen on all
training days, as the judge chooses it today. Scored days 2018-06-29 to 2025-12-31, h = 1 to 5, +5 bp primary; no day of the 2026
tiers is read (`docs/decisions/lockbox.md`). It writes nothing into `docs/runs/`, changes no published declaration, and
moves no published figure. The rows, the state threshold and what is reported are in `metadata/regime_thresholds.json`, and each
variant is a candidate file of its own (`metadata/pressure_judge/candidates/<row>+scarce_cutoff.json`), committed before any score.

## What was declared

* **Rows.** "The best six models of Table 1" is read as #429 read "best": the most onsets flagged at lead of at least 1, ties broken
  by the smaller worst false alarms per onset, then by name, the three reference rows left out. That gives #429's five
  (`two_part_gbm`, `ngboost_laplace`, `hierarchical_logistic`, `settlement_quantile_timing`, `scarcity_logistic_interactions`) and
  `scarcity_logistic` (13 of 26 onsets, 3.23 false alarms per onset; it ties `scarcity_logistic_regime_pooled` on both, and wins on
  name). `tests/test_regime_thresholds.py` re-derives the six from Table 1. *Marked question for Eleonora:* if "best six" meant
  another ordering, the sixth row is the one to change; the other five do not move.
* **Scarce cut-off.** `pressure_judge.choose_cutoffs(scarce_at_least=2)`. The state is the grid's `scarcity_state`, read as of each
  day's decision instant, for the training days and for the scored day alike. The scarce cut-off is chosen at each refit, from that
  refit's training window only; a window with no onset in that state flags nothing (`never_flag`, the rule's own default).
  A guard in `select_cutoff` refuses a window that reaches past the refit's training end; the recorded mutation is in
  `tests/test_pressure_judge.py` (`ScarceCutoffTests`).
* **The weighted-miss rule of #454** is reported beside the unweighted rule, forced on for a scratch run (the section "Under the weighted-miss rule" below).

## Reproduce

Published panel `4ddc3882…` (rebuilt from the tracked fixtures, `verify-panel` clean); scratch panels from `pressure_v1_1.py panel`
(`AUG.csv`, digest `4137d0ad…`) and `measurement_fields.py panel` (`AUG2.csv`). Run with `OMP_NUM_THREADS=1` and
`/opt/rmm-venv/bin/python`. Each row's forecasts come from its own script, unchanged, on main, at h = 1 to 5.

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
PYTHONPATH=src python3 scripts/regime_thresholds.py score --panel PUB.csv --bench 'OUT/bench_h{h}.json' \
    --row two_part_gbm='OUT/tp_h{h}.json' --row ngboost_laplace='OUT/q_h{h}.json' --row hierarchical_logistic='OUT/hl_h{h}.json' \
    --row settlement_quantile_timing='OUT/sqt_h{h}.json' --row scarcity_logistic_interactions='OUT/sli_h{h}.json' \
    --row scarcity_logistic='OUT/sl_h{h}.json' --output OUT/regime.json --markdown OUT/regime.md
```

The pooled rows reproduce Table 1 of the re-judge exactly (onsets flagged, intervals and worst false alarms per onset for all six).
The judge's full tables, with the variants beside the baseline, are in `docs/pivot/evidence/regime-thresholds/tables.md`; a compact
JSON of the by-year and scarce-cut-off figures and the verdicts is `summary.json` there.

## Result: no model's pass changes, and the years that no model warns stay unwarned

Table 1 of the judge (full rows in the evidence file): for each of the six rows the variant flags the same number of onsets as the
baseline (15, 15, 15, 15, 14 and 13 of 26), at the same worst false alarms per onset (2.46, 2.54, 3.65, 3.65, 3.23, 3.23); the
intervals move in the third decimal at most. Tier 1 stays failed for all six: every row's worst false alarms per onset (2.46 to 3.65) is over the limit of 2, under the
pooled and the scarce-state cut-off alike. The tier 3 and tier 5 verdicts are unchanged for every row. No variant passes.

Table A. Onsets flagged at lead of at least 1, by calendar year, pooled cut-off / scarce-state cut-off (onsets in the year in
the header).

| model | 2018 (4) | 2019 (13) | 2020 (2) | 2024 (2) | 2025 (5) | all (26) |
|---|---|---|---|---|---|---|
| two_part_gbm | 0 / 0 | 12 / 12 | 1 / 1 | 0 / 0 | 2 / 2 | 15 / 15 |
| ngboost_laplace | 0 / 0 | 11 / 11 | 0 / 0 | 0 / 0 | 4 / 4 | 15 / 15 |
| hierarchical_logistic | 0 / 0 | 12 / 12 | 0 / 0 | 0 / 0 | 3 / 3 | 15 / 15 |
| settlement_quantile_timing | 1 / 1 | 13 / 13 | 0 / 0 | 0 / 0 | 1 / 1 | 15 / 15 |
| scarcity_logistic_interactions | 0 / 0 | 12 / 12 | 0 / 0 | 0 / 0 | 2 / 2 | 14 / 14 |
| scarcity_logistic | 0 / 0 | 10 / 10 | 0 / 0 | 0 / 0 | 3 / 3 | 13 / 13 |

* **2018, 2020 and 2024 are not helped.** In 2024 none of the six warns either episode, under either cut-off. In 2020 only
  `two_part_gbm` warns one of two, under both. In 2018 only `settlement_quantile_timing` warns one of four, under both.
  (The directive's premise that no model warns any episode of these years today holds for all but those two cases.)
* **The scarce-state cut-off is almost the pooled one.** 24 of the onsets fall on days in state 2 or above (Table B, h = 1), so the
  all-state training window is already mostly the state-2 window; the cut-off chosen on state-2 days alone lands on the same
  value in nearly every block. Where it differs it moves a handful of flags: `settlement_quantile_timing` gains 6, 1, 3, 1 and 0
  flags on the scarce days at h = 1 to 5, `two_part_gbm` loses 0, 0, 2, 1, 0, the other four rows by 0 or 1. Table 2 of the judge shows one change by regime: `settlement_quantile_timing` flags 0.62 of 2025-26's pressure days at h = 1, up from 0.52 (29 days).
* **Early refits have no state-2 onsets.** In 5 to 10 of the 25 to 26 refit blocks that contain a scarce-state day, the scarce
  cut-off flags nothing (Table B, column "of them, flag nothing"): the training window held no onset in the state yet, or none was
  reachable within the false-alarm limit. This is the declared rule's `never_flag`; a fallback to the pooled cut-off would be a
  different rule and was not scored (a choice for Eleonora, below).

Table B. The scarce-state cut-off, h = 1 (the other horizons are in `tables.md`, Table 5): scored days, days in state 2 or above,
their pressure days and onsets, refit blocks with such a day, those whose scarce cut-off flags nothing, and the flags on the scarce
days under each cut-off.

| model | scored days | scarce days | scarce pressure days | scarce onsets | blocks | flag nothing | flags: pooled | flags: scarce |
|---|---|---|---|---|---|---|---|---|
| two_part_gbm | 1873 | 514 | 134 | 24 | 26 | 7 | 39 | 39 |
| ngboost_laplace | 1873 | 514 | 134 | 24 | 26 | 7 | 111 | 110 |
| hierarchical_logistic | 1873 | 514 | 134 | 24 | 26 | 7 | 164 | 164 |
| settlement_quantile_timing | 1873 | 514 | 134 | 24 | 26 | 5 | 129 | 135 |
| scarcity_logistic_interactions | 1873 | 514 | 134 | 24 | 26 | 6 | 164 | 163 |
| scarcity_logistic | 1873 | 514 | 134 | 24 | 26 | 7 | 152 | 152 |

(Table B's onset count is the h = 1 grid's own; Table A counts onsets on the days every horizon scores.)

## Under the weighted-miss rule of #454 (draft, not in force)

#454 has merged, so the criterion's second half is answered here. The draft rule (`metadata/weighted_miss.json`, `in_force: false`)
counts a false alarm 0.25 within 2 trading days of a pressure day, 0.5 within 5 and 1 beyond; the judge's cut-off rule and tier 1
then count the weighted false alarms against the same limit of 2 per onset. It is forced on for this scratch run only
(`regime_thresholds.py score --rule weighted`, the way `docs/pivot/alarm-cooldown-result.md` forced it); the pooled and the
scarce-state cut-offs are both chosen on the weighted count of the training window. No published figure moves, the 2026 tiers are
not read, and `--rule unweighted` reproduces `tables.md` exactly (the same run as above). The judge's full weighted tables are in
`docs/pivot/evidence/regime-thresholds/tables_weighted.md`, the figures below in `summary_weighted.json`.

Table C. Each row under both rules and both cut-offs, h = 1 to 5, tier 1 at lead >= 1. "Flat" counts every false alarm as 1,
"weighted" by the draft weights; the weighted-rule rows are the ones the cut-off was chosen on. Tiers are yes/no; the last
column is the number of onsets warned in 2018, 2020 and 2024.

| row | cut-off | onsets warned | worst FA/onset, flat | worst FA/onset, weighted | tier 1 | tier 3 | tier 5 | 2018 / 2020 / 2024 warned |
|---|---|---|---|---|---|---|---|---|
| two_part_gbm | unweighted, pooled | 15 of 26 | 2.46 | 1.07 | no | no | no | 0 / 1 / 0 |
| two_part_gbm | unweighted, scarce-state | 15 of 26 | 2.46 | 1.07 | no | no | no | 0 / 1 / 0 |
| two_part_gbm | weighted, pooled | 15 of 26 | 4.81 | 2.55 | no | no | no | 0 / 1 / 0 |
| two_part_gbm | weighted, scarce-state | 15 of 26 | 4.81 | 2.55 | no | no | no | 0 / 1 / 0 |
| ngboost_laplace | unweighted, pooled | 15 of 26 | 2.54 | 1.03 | no | no | no | 0 / 0 / 0 |
| ngboost_laplace | unweighted, scarce-state | 15 of 26 | 2.54 | 1.03 | no | no | no | 0 / 0 / 0 |
| ngboost_laplace | weighted, pooled | 17 of 26 | 4.08 | 1.73 | yes | no | no | 0 / 0 / 0 |
| ngboost_laplace | weighted, scarce-state | 17 of 26 | 4.08 | 1.73 | yes | no | no | 0 / 0 / 0 |
| hierarchical_logistic | unweighted, pooled | 15 of 26 | 3.65 | 1.31 | no | no | no | 0 / 0 / 0 |
| hierarchical_logistic | unweighted, scarce-state | 15 of 26 | 3.65 | 1.31 | no | no | no | 0 / 0 / 0 |
| hierarchical_logistic | weighted, pooled | 15 of 26 | 6.23 | 2.91 | no | no | no | 0 / 0 / 0 |
| hierarchical_logistic | weighted, scarce-state | 15 of 26 | 6.08 | 2.86 | no | no | no | 0 / 0 / 0 |
| settlement_quantile_timing | unweighted, pooled | 15 of 26 | 3.65 | 1.68 | no | no | yes | 1 / 0 / 0 |
| settlement_quantile_timing | unweighted, scarce-state | 15 of 26 | 3.65 | 1.68 | no | no | yes | 1 / 0 / 0 |
| settlement_quantile_timing | weighted, pooled | 16 of 26 | 6.38 | 3.41 | no | no | yes | 1 / 1 / 0 |
| settlement_quantile_timing | weighted, scarce-state | 19 of 26 | 6.81 | 3.49 | no | no | yes | 1 / 1 / 0 |
| scarcity_logistic_interactions | unweighted, pooled | 14 of 26 | 3.23 | 1.23 | no | no | no | 0 / 0 / 0 |
| scarcity_logistic_interactions | unweighted, scarce-state | 14 of 26 | 3.23 | 1.23 | no | no | no | 0 / 0 / 0 |
| scarcity_logistic_interactions | weighted, pooled | 14 of 26 | 5.50 | 2.39 | no | no | no | 0 / 0 / 0 |
| scarcity_logistic_interactions | weighted, scarce-state | 14 of 26 | 5.50 | 2.39 | no | no | no | 0 / 0 / 0 |
| scarcity_logistic | unweighted, pooled | 13 of 26 | 3.23 | 1.23 | no | no | no | 0 / 0 / 0 |
| scarcity_logistic | unweighted, scarce-state | 13 of 26 | 3.23 | 1.23 | no | no | no | 0 / 0 / 0 |
| scarcity_logistic | weighted, pooled | 13 of 26 | 4.73 | 2.09 | no | no | no | 0 / 0 / 0 |
| scarcity_logistic | weighted, scarce-state | 13 of 26 | 4.73 | 2.09 | no | no | no | 0 / 0 / 0 |

Table D. Onsets flagged at lead of at least 1 by calendar year under the weighted rule, pooled / scarce-state cut-off.

| model | 2018 (4) | 2019 (13) | 2020 (2) | 2024 (2) | 2025 (5) | all (26) |
|---|---|---|---|---|---|---|
| two_part_gbm | 0 / 0 | 12 / 12 | 1 / 1 | 0 / 0 | 2 / 2 | 15 / 15 |
| ngboost_laplace | 0 / 0 | 12 / 12 | 0 / 0 | 0 / 0 | 5 / 5 | 17 / 17 |
| hierarchical_logistic | 0 / 0 | 12 / 12 | 0 / 0 | 0 / 0 | 3 / 3 | 15 / 15 |
| settlement_quantile_timing | 1 / 1 | 13 / 13 | 1 / 1 | 0 / 0 | 1 / 4 | 16 / 19 |
| scarcity_logistic_interactions | 0 / 0 | 12 / 12 | 0 / 0 | 0 / 0 | 2 / 2 | 14 / 14 |
| scarcity_logistic | 0 / 0 | 10 / 10 | 0 / 0 | 0 / 0 | 3 / 3 | 13 / 13 |

* **No row passes.** Under the weighted rule the cut-offs loosen: every row warns the same number of onsets or more (up to 17 of 26 for
  `ngboost_laplace`) and its flat false alarms per onset rise to 4.08 to 6.81, so the weighted count is what stays near the limit.
  `ngboost_laplace` passes tier 1 (weighted worst 1.73), under both cut-offs; it fails tiers 3 and 5, as before. No variant or
  baseline passes the pass rule, under either rule.
* **The scarce-state cut-off still changes little.** Only `settlement_quantile_timing` moves (16 to 19 onsets warned, 2025 from 1 to 4), at
  a worst weighted 3.49 against 3.41, still over the limit of 2; `hierarchical_logistic` gains nothing on warnings. The other four rows are identical to
  the pooled cut-off in every column.
* **2018, 2020 and 2024.** Under the weighted rule `settlement_quantile_timing` warns one of four 2018 onsets and one of two 2020 onsets
  and `two_part_gbm` one of two 2020 onsets; no row warns either 2024 onset. The weighted rule does not help 2024.

## What was checked, and what was not

* Checked: the pooled rows equal Table 1 of the re-judge for all six rows; the scarce cut-off reads training days only (unit
  tests and a recorded mutation, `tests/test_pressure_judge.py`); no scored day is after 2025-12-31 and no confirmation day is read
  (the confirmation list `confirmation.candidates` is unchanged and empty).
* Not checked: a fallback to the pooled cut-off where the scarce window gives none;
  state thresholds other than 2 (a choice made after seeing a score would be tuning on the scored days).
* No variant passes the pass rule, under either rule, so no "Publish?" issue is opened.
