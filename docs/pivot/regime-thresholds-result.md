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
* **The weighted-miss rule of #454** has not merged, so only the unweighted rule is reported.

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

## What was checked, and what was not

* Checked: the pooled rows equal Table 1 of the re-judge for all six rows; the scarce cut-off reads training days only (unit
  tests and a recorded mutation, `tests/test_pressure_judge.py`); no scored day is after 2025-12-31 and no confirmation day is read
  (the confirmation list `confirmation.candidates` is unchanged and empty).
* Not checked: the weighted-miss rule (#454 has not merged); a fallback to the pooled cut-off where the scarce window gives none;
  state thresholds other than 2 (a choice made after seeing a score would be tuning on the scored days).
* No variant passes tier 1, so no "Publish?" issue is opened.
