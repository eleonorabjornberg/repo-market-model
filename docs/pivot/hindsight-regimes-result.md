# What the hindsight regime labels contribute to the calibrated stack and the per-regime recalibration (#515, of #524)

A scratch measurement under the pressure-day judge. It writes nothing into `docs/runs/`, moves no published figure and changes no rule, threshold,
onset definition or availability time. Scored days 2018-06-29 to 2025-12-31 only; no 2026 day is read (`docs/decisions/lockbox.md`). The question comes from
finding #515: the calibrated stack (#475) and the per-regime recalibration (#471) read the regime label of `metadata/evaluation_splits.json`
(2018-19 | 2020 | 2021-23 | 2024 | 2025-26), whose boundaries were drawn after the fact. On the dates the labels switch (2020-01-01, 2021-01-01, 2024-01-01,
2025-01-01) a forecaster could not have known a new regime had begun. The guard `group_calibration.require_regimes_asof` checks only that a label matches
the calendar table, not when the boundaries were set.

**Whether regime labels may be inputs at all is a question about the information set, and it is Eleonora's.** This page does not settle it; it measures what the labels contribute.

## What was declared

Before any variant was scored, in `metadata/hindsight_regimes.json` and one judge candidate file per variant
(`metadata/pressure_judge/candidates/<name>+no_regime.json`, `+scarcity.json`, `<base>+regime_recal_none.json`, `+regime_recal_scarcity.json`), committed first.

* **The controls** are the stack and the recalibration as declared (`metadata/calibrated_stack.json`, `metadata/regime_recalibration.json`), unchanged, re-scored in the
  same run on the same panel and cut-off rule.
* **Variant 1, the regime term removed.** The stack has no regime indicator; the recalibration has no group (one pooled Platt curve per threshold and horizon).
* **Variant 2, the regime term replaced by the as-of reserve-scarcity state** (0 to 3, or none), the state the judge's own splits use (`pressure_judge._scarcity_states`), read at each
  forecast's decision instant. The stack gets one indicator per state, the recalibration one Platt curve per state.
* Members, ridge, clip, refit blocks, fallbacks, gates and Platt constants are the controls'; no constant is searched. The judge's cut-off rule is unchanged.

## Reproduce

Published panel `4ddc3882…` (`verify-panel` clean); scratch panel as for #471 (`pressure_v1_1.py panel`, then `measurement_fields.py panel`).

```
for h in 1 2 3 4 5: PYTHONPATH=src /opt/rmm-venv/bin/python scripts/regime_recalibration.py run --panel AUG2.csv --published PUB.csv --horizon $h --output OUT/regime_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src /opt/rmm-venv/bin/python scripts/regime_recalibration.py run --panel AUG2.csv --published PUB.csv --horizon $h --groupings none,scarcity --output OUT/variants_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src /opt/rmm-venv/bin/python scripts/pressure_judge.py forecasts --panel PUB.csv --horizon $h --published --output OUT/bench_h$h.json
for m in declared none scarcity; for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/calibrated_stack.py forecasts --panel PUB.csv --horizon $h --regime-term $m --output OUT/stack_${m}_h$h.json OUT/regime_h$h.json
for r in unweighted weighted: PYTHONPATH=src /opt/rmm-venv/bin/python scripts/pressure_judge.py judge --panel PUB.csv --rule $r --output OUT/judge_$r.json OUT/bench_h?.json OUT/regime_h?.json OUT/variants_h?.json OUT/stack_*_h?.json
PYTHONPATH=src python3 scripts/hindsight_regimes.py report --panel PUB.csv --judge-flat OUT/judge_unweighted.json --judge-weighted OUT/judge_weighted.json --output OUT/hindsight.json --markdown OUT/hindsight.md OUT/bench_h?.json OUT/regime_h?.json OUT/variants_h?.json OUT/stack_*_h?.json
```

(The variants run does not repeat the raw bases; its raw forecasts were checked equal to the declared run's.) Evidence: `docs/pivot/evidence/hindsight-regimes/hindsight.md` and `hindsight.json`.
The controls reproduce the earlier pages: the stack's flat and weighted worst false alarms per onset (3.88 / 2.50 and 3.04 / 2.05), its mean regime coefficients
(2018-19 +1.88, 2020 -0.47, 2021-23 -1.26, 2024 -0.09, 2025-26 -0.05), and the recalibration's Table 5 (`regime-recalibration-result.md`, as corrected). The "5.12 flat false alarms per onset" of
`calibrated-stack-result.md` is the flat count at the weighted run's cut-offs (the mislabel of #519, below); the flat run's own count is 3.88.

## Result

Onsets flagged of 26 at some horizon 1 to 5 (+5 bp), worst false alarms per onset (limit 2; the weighted column is the weighted count that decides tier 1 under that rule), tiers 1 / 3 / 5,
and onsets flagged by year of the onset (flat rule). Full tables with every row: `evidence/hindsight-regimes/hindsight.md`.

Table 1. The calibrated stack.

| form | flagged, flat | FA/onset, flat | tiers 1 / 3 / 5, flat | flagged, weighted | FA/onset, weighted | tiers 1 / 3 / 5, weighted | 2019 | 2025 |
|---|---|---|---|---|---|---|---|---|
| logistic / declared regime | 14 | 3.88 | fail / fail / fail | 15 | 2.50 | fail / fail / fail | 13 of 13 | 1 of 5 |
| logistic / no regime term | 16 | 4.65 | fail / fail / pass | 16 | 3.54 | fail / fail / pass | 13 of 13 | 3 of 5 |
| logistic / as-of scarcity state | 16 | 3.88 | fail / fail / fail | 16 | 2.65 | fail / fail / fail | 13 of 13 | 3 of 5 |
| isotonic / declared regime | 11 | 3.04 | fail / fail / fail | 12 | 2.05 | fail / fail / fail | 11 of 13 | 0 of 5 |
| isotonic / no regime term | 12 | 3.04 | fail / fail / pass | 13 | 2.20 | fail / fail / pass | 11 of 13 | 1 of 5 |
| isotonic / as-of scarcity state | 11 | 3.04 | fail / fail / pass | 12 | 2.12 | fail / fail / pass | 11 of 13 | 0 of 5 |

Table 2. The per-regime recalibration of each passer (worst false alarms per onset under the weighted rule, and its tier 1 verdict under it; the flat figures and the years are in the evidence file).

| passer | raw | declared regime | no group (pooled Platt) | as-of scarcity state |
|---|---|---|---|---|
| risk_gbm | 0.80 pass | 2.67 fail | 3.37 fail | 3.17 fail |
| risk_gbm_base | 0.97 pass | 1.87 pass | 2.70 fail | 2.69 fail |
| risk_logistic | 1.74 pass | 2.42 fail | 2.90 fail | 2.91 fail |
| risk_logistic_base | 1.65 pass | 1.88 pass | 2.31 fail | 2.31 fail |
| risk_quantile_skewt_base | 1.62 pass | 1.79 pass | 2.45 fail | 2.47 fail |

Onsets flagged in 2019 (of 13): raw 10 for every passer; every recalibrated form 11, with the declared regime, with no group and with the scarcity state alike. In 2025 (of 5) the
declared regime keeps 2 or 3 where the raw passers have 3 or 4, and the other groupings keep 0 to 2.

## What the hindsight labels contributed

* **In 2018-19 the regime term does nothing, in the stack or the recalibration.** The stack's regime coefficients are 0 (below 1e-16) on all 11 fitted refits before 2020
  (`evidence`, `largest_absolute_coefficient_before_2020`): in a window that holds one regime the indicator is collinear with the intercept and the ridge sets it to 0. The stack flags the same
  13 of 13 onsets of 2019 with no regime term at all, and the same 13 of 13 with the scarcity state. The gain of the recalibrated passers in 2019 (10 to 11 of 13) is the same
  with no group as with the declared regime, so it comes from the pooled Platt curve, not from the labels. The stack's 2019 recall is not a hindsight effect.
* **From 2020 the labels act, and they trade recall for false alarms.** The declared regime lowers the stack's false alarms (logistic, flat 4.65 to 3.88, weighted 3.54 to 2.50) and costs it onsets in 2025
  (3 of 5 to 1 of 5; 16 to 14 flagged). The as-of scarcity state recovers the 2025 onsets (3 of 5) at the declared regime's flat false-alarm count (3.88) and a weighted count of 2.65, against 2.50. No stack passes tier 1
  in any form or the full rule; the one verdict the labels move is the logistic stack's tier 5, which it fails with the declared regime and meets without it.
* **The recalibration's tier 1 under the weighted rule does depend on them.** With the declared regime, three of the five passers keep tier 1 (weighted counts 1.87, 1.88, 1.79). With no group or with the as-of
  scarcity state, none does (2.31 to 3.37). The labels know that 2021-23 is calm and 2018-19 is not; the scarcity state is 99% state 3 in 2018-19 and 100% state 0 in 2024 (`setup-sensitivity-result.md`), and the pooled curve carries 2018-19's rate into the calm years (`regime-recalibration-result.md`). That the declared form passes tier 1
  where the as-of forms fail is the size of what the hindsight labels contribute to the recalibration. It is also the part that cannot be had live: the regime changes on 2020-01-01, 2021-01-01, 2024-01-01
  and 2025-01-01 were not known on those dates.
* **Nothing here passes the full rule.** Every form fails tier 3 (calibration by regime); the recalibrated forms meet tier 5. So there is no verdict to publish and no "Publish?" issue.

## What this does not say

* **Whether regime labels may be inputs at all is not decided here.** The as-of scarcity state is one replacement, not a proposal; a policy-date regime or another as-of state is a new declaration.
* The scarcity-state grouping is the declared one only: the finer group of #380 (scarcity band by day type) was not run. 26 onsets: one onset moves recall by about 0.04, and the years rest on 2 to 13 onsets.
  No interval is put on the differences between a control and its variant beyond the judge's own for the pooled rows (`hindsight.md` carries counts); no multiple-testing correction.
* The +10 bp threshold, the confirmation window and every 2026 day are not looked at.
