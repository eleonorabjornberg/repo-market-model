# The onset classifier (#409, track O of #374)

A scratch measurement under the pressure-day judge as amended by the pull request that closes #407. It writes nothing into
`docs/runs/` and moves no published figure (`docs/decisions/lockbox.md`: scored days 2018-06-29 to 2025-12-31 only; the
confirmation window is not looked at). Declared before any score in `metadata/onset_classifier.json` and, for the judge, in
`metadata/pressure_judge.json`; `scripts/onset_classifier.py` refuses an uncommitted declaration.

## What was declared

* **Target.** The bar scores onsets, so the label is an onset at the threshold (`pressure.onsets`): a day with SOFR - IORB above it
  and no such day on the five panel days before it. Every earlier track trained on all pressure days. The horizon-h file holds
  P(day t+h is an onset) read at the decision instant of day t, h = 1 to 5, at +5 and +10 bp. A training day with fewer than five
  panel days before it trains no pair, and the label reads only training rows (`ml._onset_labels`).
* **Within lead h.** An onset is flagged with lead h when its own horizon-h probability reached the cut-off; "lead at least h" is
  any horizon from h to 5. This is the judge's onset tier, so the per-day probabilities are in the judge's format
  (`pressure_judge.forecasts_from_horizon_document`). The five-day-window probability is the judge's week-ahead tier: the maximum of
  the five per-day probabilities, scored against the event "a pressure day in the next five business days".
* **Features.** The calendar (days to month end, quarter end, tax date), Treasury settlement at h = 1 only (not public earlier),
  reserves and the reserve-scarcity state (#115, 0 to 3; reserves multiply every scheduled term, as in #379), the weekly TGA change,
  and from #377 the daily TGA balance and its change. Two candidates add the OFR tri-party and GCF overnight rates, entered with an
  observed indicator and a zero where not yet public (`ml._PressureDesign`, `optional`): the tri-party rate is real-time only from
  2020-09-09 (1324 of 1935 panel rows) and the GCF rate is present on 144 rows. They could not enter as required columns without
  dropping the 2018-19 days, which hold most of the pressure days.
* **Weighting.** `ml.PRESSURE_RARE_EVENT_SETTINGS` (#381): balanced class weights inside each fit, or the focal loss; one
  unweighted logistic is the reference row.
* **Calibration and flags.** Each fit is recalibrated out of fold against the pressure-day outcome (Platt,
  `pressure.recalibrated`), which is the judged form because the judge calibrates against pressure days. The monotone
  curve across thresholds that the exceedance-curve interface requires is kept. The flag cut-off is the judge's `cutoff_rule`,
  chosen from each refit's training window; none is declared here.
* **Candidates.** `onset_logistic`, `onset_logistic_class_weight`, `onset_gbm_class_weight`, `onset_gbm_focal`, and the two
  `_funding` variants (logistic and classifier with class weights).

## Reproduce

Published panel `4ddc3882…`; scratch panel from `pressure_v1_1.py panel` then `measurement_fields.py panel`. Run with
`OMP_NUM_THREADS=1` when several horizons run at once.

```
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/onset_classifier.py run --panel AUG2.csv --published PUBLISHED.csv --horizon $h --output OUT/onset_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --published --output OUT/bench_h$h.json
PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --output OUT/judge.json --markdown OUT/judge.md OUT/bench_h?.json OUT/onset_h?.json
PYTHONPATH=src python3 scripts/pressure_judge.py table OUT/judge.json --output OUT/tables.md
PYTHONPATH=src python3 scripts/onset_classifier.py leads --panel PUBLISHED.csv --output OUT/leads.json OUT/bench_h?.json OUT/onset_h?.json
```

The judge's full report is `docs/pivot/evidence/onset-classifier/judge.md`; its tables are `tables.md` there, and the per-lead
figures `leads.json`.

## Result: no onset classifier passes

The pass rule is tier 1 (onset warning at lead of at least 1), tier 3 (no crying wolf) and tier 5 (week-ahead window). All six
fail tier 1 and tier 3, within the scarce regime alone as well. Training on the onset label does not give a classifier that flags
half the onsets inside the false-alarm limit: the class-weighted logistics keep the false alarms down (under one per onset) by
flagging few onsets, and the other four flag more onsets with more false alarms than the limit allows. Five of the six pass
tier 5, the week-ahead window (calibrated and better than climatology on Brier); the published model does not.

Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals, as the judge reports them.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes with pressure, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.00 | 2.7 / 4.4 | 1 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| onset_gbm_class_weight+recalibrated | 8 of 26 | 0.308 [0.143, 0.482] | 0.231 | 3.42 | 0.5 / 0.0 | 2 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| onset_gbm_class_weight_funding+recalibrated | 8 of 26 | 0.308 [0.143, 0.500] | 0.231 | 3.38 | 0.2 / 0.0 | 2 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| onset_gbm_focal+recalibrated | 10 of 26 | 0.385 [0.208, 0.565] | 0.231 | 2.85 | 0.2 / 0.3 | 2 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / no) |
| onset_logistic+recalibrated | 11 of 26 | 0.423 [0.250, 0.586] | 0.231 | 3.54 | 0.2 / 0.3 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| onset_logistic_class_weight+recalibrated | 6 of 26 | 0.231 [0.091, 0.381] | 0.115 | 0.81 | 0.0 / 0.0 | 3 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| onset_logistic_class_weight_funding+recalibrated | 5 of 26 | 0.192 [0.062, 0.333] | 0.115 | 0.77 | 0.0 / 0.0 | 3 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.231 | 3.42 | 0.5 / 0.0 | 2 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| published_v1 | 2 of 26 | 0.077 [0.000, 0.185] | 0.192 | 2.35 | 0.2 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |

Table 2. Onset recall and false alarms per onset at each lead, +5 bp, under the judge's own cut-offs: onsets flagged at exactly
that horizon / onsets (share), then false alarms (flags on days that are not pressure days) per onset. The onset count at h = 1
is one more than in Table 1 because Table 1 counts the onsets every horizon scores.

| model | h=1 | h=2 | h=3 | h=4 | h=5 |
|---|---|---|---|---|---|
| calendar_climatology | 9/27 (0.33), 4.67 | 10/26 (0.38), 4.88 | 10/26 (0.38), 4.92 | 10/26 (0.38), 4.96 | 10/26 (0.38), 5.00 |
| onset_gbm_class_weight+recalibrated | 8/27 (0.30), 3.30 | 2/26 (0.08), 1.73 | 4/26 (0.15), 2.27 | 6/26 (0.23), 1.62 | 4/26 (0.15), 3.00 |
| onset_gbm_class_weight_funding+recalibrated | 8/27 (0.30), 3.26 | 2/26 (0.08), 1.73 | 4/26 (0.15), 2.27 | 6/26 (0.23), 1.62 | 4/26 (0.15), 3.00 |
| onset_gbm_focal+recalibrated | 8/27 (0.30), 2.74 | 1/26 (0.04), 1.54 | 4/26 (0.15), 1.88 | 6/26 (0.23), 1.92 | 2/26 (0.08), 2.15 |
| onset_logistic+recalibrated | 11/27 (0.41), 3.41 | 6/26 (0.23), 2.35 | 8/26 (0.31), 2.81 | 5/26 (0.19), 2.35 | 7/26 (0.27), 1.35 |
| onset_logistic_class_weight+recalibrated | 5/27 (0.19), 0.78 | 1/26 (0.04), 0.35 | 2/26 (0.08), 0.23 | 2/26 (0.08), 0.08 | 2/26 (0.08), 0.15 |
| onset_logistic_class_weight_funding+recalibrated | 4/27 (0.15), 0.74 | 1/26 (0.04), 0.35 | 2/26 (0.08), 0.23 | 2/26 (0.08), 0.08 | 2/26 (0.08), 0.15 |
| persistence_logistic | 4/27 (0.15), 2.67 | 6/26 (0.23), 3.42 | 6/26 (0.23), 2.81 | 6/26 (0.23), 3.15 | 5/26 (0.19), 2.81 |
| published_v1 | 2/27 (0.07), 2.26 | 0/26 (0.00), 1.54 | 0/26 (0.00), 1.19 | 2/26 (0.08), 1.27 | 2/26 (0.08), 1.46 |

Table 3. h = 1, +5 bp: descriptive measures at the chosen cut-offs (AUROC, average precision, Brier, precision and recall).

| model | AUROC | average precision | Brier | precision at the cut-off | recall at the cut-off | false alarms per pressure day |
|---|---|---|---|---|---|---|
| onset_gbm_class_weight+recalibrated | 0.525 | 0.176 | 0.0706 | 0.346 | 0.336 | 1.89 |
| onset_gbm_class_weight_funding+recalibrated | 0.531 | 0.177 | 0.0706 | 0.348 | 0.336 | 1.87 |
| onset_gbm_focal+recalibrated | 0.650 | 0.185 | 0.0681 | 0.302 | 0.229 | 2.31 |
| onset_logistic+recalibrated | 0.686 | 0.298 | 0.0623 | 0.378 | 0.400 | 1.64 |
| onset_logistic_class_weight+recalibrated | 0.826 | 0.341 | 0.0658 | 0.382 | 0.093 | 1.62 |
| onset_logistic_class_weight_funding+recalibrated | 0.832 | 0.347 | 0.0649 | 0.394 | 0.093 | 1.54 |
| calendar_climatology | 0.586 | 0.143 | 0.0714 | 0.364 | 0.514 | 1.75 |
| persistence_logistic | 0.876 | 0.397 | 0.0563 | 0.459 | 0.436 | 1.18 |
| published_v1 | 0.898 | 0.492 | 0.0496 | 0.504 | 0.443 | 0.98 |

Table 4. The knowledge holdouts (`metadata/events.json`), h = 1, +5 bp: pressure days flagged of those in the window, and false
alarms. Descriptive: a window holds too few days for an interval.

| model | March 2020 (3 pressure days): flagged, false alarms | September 2019 (5 pressure days): flagged, false alarms |
|---|---|---|
| onset_gbm_class_weight+recalibrated | 0 of 3, 0 | 2 of 5, 0 |
| onset_gbm_class_weight_funding+recalibrated | 0 of 3, 0 | 2 of 5, 0 |
| onset_gbm_focal+recalibrated | 0 of 3, 0 | 2 of 5, 0 |
| onset_logistic+recalibrated | 0 of 3, 0 | 2 of 5, 0 |
| onset_logistic_class_weight+recalibrated | 0 of 3, 0 | 0 of 5, 0 |
| onset_logistic_class_weight_funding+recalibrated | 0 of 3, 0 | 0 of 5, 0 |
| calendar_climatology | 0 of 3, 0 | 5 of 5, 0 |
| persistence_logistic | 1 of 3, 2 | 5 of 5, 0 |
| published_v1 | 0 of 3, 2 | 5 of 5, 0 |

## What this says

* Trained on onsets, the class-weighted logistic ranks days well (AUROC at h = 1 well above the unweighted one's and the
  climatology's, see Table 3) but its recalibrated probabilities seldom reach a cut-off that the false-alarm limit allows, so it
  flags few onsets. The ranking is not turned into flags by the judge's cut-off rule on these probabilities.
* The classifiers do not beat the persistence-logistic benchmark or the published model on Brier or AUROC at h = 1 (Table 3);
  the onset label alone does not add what the latest spread already carries.
* The tri-party and GCF rates add nothing visible (the two `_funding` rows are within noise of their parents), consistent with
  the gaps in those series.
* Not checked: the +10 bp threshold is scored by the judge (see `judge.md`) but is not the pass condition; the unrecalibrated
  onset-rate fits are kept in the forecast files as an ablation and not judged; no confirmation-window look was taken.
