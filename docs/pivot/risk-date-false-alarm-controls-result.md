# False-alarm controls on the every-day component of the risk-date passers (#532, of #374)

A scratch measurement under the pressure-day judge. It writes nothing into `docs/runs/`, moves no published figure, and reads
no day after 2025-12-31 (`docs/decisions/lockbox.md`; the script refuses a later panel, and the near-blind and blind tiers are
not looked at). No rule, threshold, onset definition, cut-off rule or availability time changes. The controls are off in every
published declaration. They were declared before any score in `metadata/risk_date_false_alarm_controls.json` (committed before
the first forecast was fitted) and, for the judge, in `metadata/pressure_judge/candidates/<parent>+every_day+<control>.json`;
`scripts/risk_date_false_alarm_controls.py` refuses an uncommitted declaration.

## What was declared

The base is the `+every_day` variant of [`risk-date-every-day-result.md`](risk-date-every-day-result.md) (#506, "the #525
variant"), refitted exactly as there for each of the five risk-date passers: on a risk date the forecast is the parent's, on any
other day it is a ridge logistic of `spread > tau` on the latest public spread and the previous day's SOFR 75th and 99th
percentiles above IORB. Four controls change only the forecast on a day that is not a risk date. Each reads that day's own
component forecast, forecasts already issued on earlier scored days, or the as-of reserve scarcity state, and nothing later
(`CausalityTests`, with a recorded mutation each for the two controls that read earlier forecasts). The curve across thresholds
is made non-increasing afterwards, as the parent's is. The judge's cut-off rule is unchanged and chooses each variant's cut-offs
from its own training window, one per threshold and horizon.

| control | rule on a day that is not a risk date | stated, not tuned |
|---|---|---|
| `+shrunk` | the component's probability times 0.5, a shrinkage toward the parent's 0 | weight 0.5 |
| `+scarce` | the component's probability only if the as-of `reserve_scarcity_state` is 1 (ample) or higher; below it, or unread, 0 | minimum state 1 |
| `+persist` | the smaller of today's component probability and the variant's forecast on the previous scored day; the first scored day is 0 | 2 days |
| `+gate` | the component's probability only if it is strictly above the 0.9 quantile of the component's forecasts on the non-risk days among the previous 250 scored days (at least 60 of them, else 0) | quantile 0.9, window 250, minimum 60 |

The directive's example of a separate cut-off chosen by the judge's own rule would be a change to the judge's rule. With one
cut-off per threshold for every day, `+shrunk` and `+gate` are the two ways here to hold the days the component serves to a
higher bar than the risk dates; they are stand-ins, not that rule.

Scored as the judge declares: tiers 1, 3 and 5, h = 1 to 5, +5 and +10 bp, under the flat and the weighted miss rule
(`--rule unweighted` and `--rule weighted`). Tier 1 is also read under readings (b) and (e) of
[`judge-readings-result.md`](judge-readings-result.md), under both rules.

## Reproduce

Published panel `4ddc3882…` (`verify-panel` clean); scratch panel as for #428 and #506 (`scripts/risk_date_severity.py`).
`/opt/rmm-venv` (numpy 2.4.6, scikit-learn 1.9.1), `OMP_NUM_THREADS=1`.

```
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
PYTHONPATH=src python3 scripts/risk_date_false_alarm_controls.py declare      # already committed; shown for the record
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --output OUT/bench_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/risk_date_severity.py run --panel AUG2.csv --published PUBLISHED.csv --horizon $h --output OUT/risk_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/risk_date_false_alarm_controls.py run --panel AUG2.csv --published PUBLISHED.csv --horizon $h --output OUT/fa_h$h.json
for r in weighted unweighted: PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule $r --output OUT/judge_$r.json --markdown OUT/judge_$r.md OUT/bench_h?.json OUT/risk_h?.json OUT/fa_h?.json
for r in weighted unweighted: PYTHONPATH=src python3 scripts/pressure_judge.py table OUT/judge_$r.json --output OUT/tables_$r.md
for r in weighted unweighted: PYTHONPATH=src python3 scripts/risk_date_false_alarm_controls.py compare --rule $r --panel PUBLISHED.csv --output OUT/compare_$r.json --markdown OUT/compare_$r.md OUT/bench_h?.json OUT/risk_h?.json OUT/fa_h?.json
PYTHONPATH=src python3 scripts/risk_date_false_alarm_controls.py readings --panel PUBLISHED.csv --output OUT/readings.json --markdown OUT/readings.md OUT/bench_h?.json OUT/risk_h?.json OUT/fa_h?.json
PYTHONPATH=src python3 scripts/risk_date_false_alarm_controls.py summary --flat OUT/judge_unweighted.json --weighted OUT/judge_weighted.json --output OUT/summary.md
```

Evidence: `docs/pivot/evidence/risk-date-false-alarm-controls/` (`summary.md` is Table 1 below for every row; `tables-*.md` and
`judge-*.md` the judge's tables and full reports, split by regime and day type; `compare.md` and `compare-weighted.md` the pairing
of every control against its parent and against the #525 variant with 90% intervals, by year, regime and pressure-day type, the
flags on and off the risk dates, the Brier pairing and the 26 episodes, with the cut-offs chosen under the flat and under the
weighted rule; `readings.md` tier 1 under readings (a), (b) and (e)). The parents' and the #525 variant's figures reproduce
those of #525 (for example `risk_gbm`, 13 of 26 at 1.35 false alarms per onset, and `risk_gbm+every_day`, 15 of 26 at 2.96, flat).

## Result: no variant passes the full rule

Table 1 (abridged to `risk_gbm`, `risk_gbm_base` and `risk_quantile_skewt_base`; all thirty rows are in `summary.md`). The judge's
row at +5 bp under each rule, 90% stationary-bootstrap intervals. "Worst false alarms per onset" is the highest of the five
horizons; the limit is 2. Flat counts every false alarm as 1; weighted counts it at its distance-weight
(`metadata/weighted_miss.json`, run with `--rule weighted`, a scratch reading).

| model | onsets flagged, flat / weighted | recall, flat [90%] | recall, weighted [90%] | worst false alarms per onset, flat | worst weighted false alarms per onset, weighted rule | tiers 1 / 3 / 5, flat | tiers 1 / 3 / 5, weighted |
|---|---|---|---|---|---|---|---|
| risk_gbm | 13/26 / 13/26 | 0.500 [0.310, 0.667] | 0.500 [0.310, 0.667] | 1.35 | 0.80 | yes / no / no | yes / no / no |
| risk_gbm+every_day (#525) | 15/26 / 17/26 | 0.577 [0.385, 0.760] | 0.654 [0.474, 0.812] | 2.96 | 2.18 | no / no / yes | no / no / yes |
| risk_gbm+every_day+shrunk | 13/26 / 16/26 | 0.500 [0.324, 0.682] | 0.615 [0.438, 0.800] | 1.38 | 2.07 | yes / no / no | no / no / no |
| risk_gbm+every_day+scarce | 16/26 / 17/26 | 0.615 [0.433, 0.792] | 0.654 [0.483, 0.818] | 2.96 | 2.17 | no / no / no | no / no / no |
| risk_gbm+every_day+persist | 15/26 / 16/26 | 0.577 [0.406, 0.750] | 0.615 [0.435, 0.800] | 2.96 | 2.23 | no / no / yes | no / no / yes |
| risk_gbm+every_day+gate | 16/26 / 17/26 | 0.615 [0.444, 0.778] | 0.654 [0.481, 0.818] | 2.96 | 1.63 | no / no / no | yes / no / no |
| risk_gbm_base | 14/26 / 14/26 | 0.538 [0.360, 0.719] | 0.538 [0.360, 0.719] | 1.50 | 0.97 | yes / no / no | yes / no / no |
| risk_gbm_base+every_day (#525) | 15/26 / 18/26 | 0.577 [0.389, 0.769] | 0.692 [0.520, 0.850] | 2.92 | 2.28 | no / no / yes | no / no / yes |
| risk_gbm_base+every_day+gate | 15/26 / 18/26 | 0.577 [0.400, 0.750] | 0.692 [0.517, 0.850] | 2.88 | 1.62 | no / no / no | yes / no / no |
| risk_quantile_skewt_base | 14/26 / 15/26 | 0.538 [0.360, 0.714] | 0.577 [0.391, 0.750] | 1.88 | 1.62 | yes / no / no | yes / no / no |
| risk_quantile_skewt_base+every_day (#525) | 15/26 / 16/26 | 0.577 [0.409, 0.750] | 0.615 [0.444, 0.792] | 2.46 | 2.63 | no / no / yes | no / no / yes |
| risk_quantile_skewt_base+every_day+gate | 15/26 / 17/26 | 0.577 [0.407, 0.741] | 0.654 [0.467, 0.824] | 3.15 | 2.00 | no / no / yes | yes / no / yes |

**No control, on any of the five parents, passes the full rule under either miss rule.** Tier 3 (calibration by regime and
the flag rate on abundant stretches) fails for every row, the parents and the #525 variant included, as it did in #525. Where
the controls differ is tier 1 and tier 5, and the two trade against each other.

* **Under the flat rule no control keeps the recall.** The worst false alarms per onset, across the five parents, are 1.4 to 2.9
  for `+shrunk`, 2.2 to 3.0 for `+scarce`, 1.8 to 3.5 for `+persist` and 2.9 to 3.2 for `+gate`, against the limit of 2. Two control
  rows pass tier 1, both at the parent's own recall: `risk_gbm+every_day+shrunk` (13 of 26 at 1.38; the parent 13 at 1.35) and
  `risk_logistic_base+every_day+persist` (13 of 26 at 1.81; the parent 13 at 1.77, and it also passes tier 5 and fails tier 3). The false
  alarms of `+shrunk` are cut by cutting the onsets the component found.
* **Under the weighted rule the gate cuts false alarms and keeps the #525 recall, on three rows.** `risk_gbm+every_day+gate`
  warns 17 of 26 at 1.63 weighted false alarms per onset (the parent: 13 at 0.80; the #525 variant: 17 at 2.18),
  `risk_gbm_base+every_day+gate` 18 at 1.62 (parent 14, #525 variant 18 at 2.28), and
  `risk_quantile_skewt_base+every_day+gate` 17 at exactly 2.00 (the limit is "at most 2"; parent 15, #525 variant 16 at 2.63).
  Against the parent the all-onset recall difference is +0.154 [+0.045, +0.280] for both gradient-boosted rows and +0.077
  [-0.095, +0.240] for the skew-t row; against the #525 variant it is +0.000 for both gradient-boosted rows (`compare-weighted.md`
  Table 2b). The gate passes tier 1 and **fails tier 5** on the two gradient-boosted rows: it is no longer calibrated and ahead of
  climatology over the week-ahead window, which the #525 variant was. The skew-t row passes tiers 1 and 5 and fails tier 3, the
  nearest any row comes to the full rule.
* **That tier 1 result does not survive the readings the audit questioned.** For the three gate rows, tier 1 is met as declared (a)
  and at h = 1 alone (b1), and fails pooled across horizons (b2: 3.67, 3.64 and 3.90 weighted false alarms per onset against a
  limit of 2) and outside 2018-19 (e: 4 of 26 onsets at 2.58, 5 at 2.61 and 4 at 3.22). The parents fail (e) too (1.61, 2.06, 3.81),
  and the two gradient-boosted parents pass (b2) (1.48, 1.59) where the gate rows do not (`readings.md`). The gate rows' tier 1
  pass is therefore a pass of reading (a) with the false alarms counted at the worst horizon, and of no other reading.
* **What the controls do to the flags.** On days that are not risk dates the #525 variant of `risk_gbm` raised 53 to 97 flags a
  horizon at the flat rule's cut-offs. `+shrunk` cuts them to 10 to 34, `+gate` to 23 to 89, `+persist` to 28 to 90, and `+scarce` hardly
  at all (52 to 102); this reading did not check why the scarcity state removes so little (`compare.md` Table 3). The judge's cut-off rule
  chooses each variant's cut-off from its own earlier forecasts, so a control moves the cut-off as well as the forecasts.
* **Paired against the parent and the #525 variant** (Brier score on the +5 bp outcome, all days, positive favours the variant;
  90% interval): the four controls keep the #525 variant's gain over the parent, for example `risk_gbm+every_day+gate` at h = 1,
  +0.0081 [+0.0013, +0.0160] against the parent and -0.0018 [-0.0050, +0.0008] against the #525 variant; at h = 5, +0.0060
  [+0.0002, +0.0131] and -0.0007 [-0.0038, +0.0023]. Against the #525 variant every interval for `+shrunk`, `+gate` and
  `+persist` at h = 1 includes zero for `risk_gbm`; `+scarce` is +0.0007 [+0.0003, +0.0012], too small to matter. Split by regime and by
  day type: Table 4 of `compare.md` (h = 1 and h = 5) and Tables 2 and 3 of `tables-*.md`.

Table 2. Onset recall by year at some lead 1 to 5, weighted-rule cut-offs (`compare-weighted.md`), for `risk_gbm` (the rows of the
other four parents are in the same file; the flat-rule cut-offs are in `compare.md`). The directive's years are in bold.

| year | onsets | parent | #525 variant | `+shrunk` | `+scarce` | `+persist` | `+gate` |
|---|---|---|---|---|---|---|---|
| **2018** | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2019 | 13 | 10 | 13 | 13 | 13 | 13 | 13 |
| **2020** | 2 | 0 | 1 | 0 | 1 | 0 | 1 |
| **2024** | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2025 | 5 | 3 | 3 | 3 | 3 | 3 | 3 |

**No control, on any parent, warns an onset of 2018 or of 2024, under either set of cut-offs; 2020 is warned (1 of 2) by some controls of
some parents, never twice.** The gain over the parent is in 2019, on ordinary days (`risk_gbm`, weighted: 8 of 12 ordinary-day
onsets for the #525 variant and the gate against 4 for the parent), as in #525.

## Which of the 11 all-five misses each variant warns

The 11 episodes that no parent warns at some lead 1 to 5 under the flat rule (`docs/pivot/episode-post-mortem-result.md`; the full
26-episode table is Table 5 of `compare.md` for flat cut-offs and of `compare-weighted.md` for weighted ones).

| variant, by cut-offs | warns of the 11 |
|---|---|
| `+shrunk` of `risk_gbm` or `risk_gbm_base`, flat | none |
| `+gate` of `risk_gbm`, flat | 2019-05-28, 2019-08-13, 2020-03-12 |
| `+gate` of `risk_gbm_base`, `+persist` of the two gradient-boosted rows, flat | 2019-05-28, 2019-08-13 |
| the other variants, flat | two to four of 2019-05-28, 2019-06-25, 2019-08-13, 2020-03-12 |
| every variant, weighted | 2019-05-28, 2019-06-25, 2019-08-13 and, except the six below, 2020-03-12 |

The six weighted variants that do not warn 2020-03-12 are `+shrunk` of `risk_gbm` and `risk_gbm_base`, and `+persist` of `risk_gbm`,
`risk_gbm_base`, `risk_logistic_base` and `risk_quantile_skewt_base`.

The episodes warned are the ones the #525 variant already warned, and all but one are ordinary days of 2019. **No variant warns any of
the four episodes of 2018 (2018-11-15, 2018-11-30, 2018-12-17, 2018-12-28), 2020-03-04, or the two of 2024 (2024-09-30,
2024-12-26)**, flat or weighted. (Under the weighted cut-offs the parent `risk_logistic` alone warns 2024-09-30.)

## What this does not say

* Four controls with one declared parameter set each. A different weight, a different persistence rule, a different quantile or
  window, a separate cut-off chosen by the judge's own rule, or a control built on the component's training fit was not tried, and
  this reading says nothing about them. Nothing was tuned: the parameters are stated, and the declaration was committed before the
  first score.
* The cut-offs are the judge's, chosen from each variant's own earlier forecasts. A control moves the forecasts, and the cut-off rule
  then moves the cut-off, so a control's effect on the flags is not the effect of a fixed cut-off on controlled forecasts.
* 26 onsets: one onset moves recall by about 0.04; the year cells rest on 2 to 13. Most recall differences against the parent have
  intervals that include zero; the table says where they do not.
* The weighted rule is the draft of `metadata/weighted_miss.json` as the judge applies it with `--rule weighted`, not a rule in force.
* No multiple-testing correction over thirty rows and two rules.
* The 2026 days, the +10 bp tiers' verdicts and the confirmation window are not looked at; +10 bp is scored by the judge as declared
  and reported in `judge-*.md`.

## For Eleonora

No variant passes the full rule, so there is no publishing question and no "Publish?" issue; the controls stay off in the published
declaration. Nothing here changes a rule, a threshold, an onset definition or a published figure. For information, the three gate
rows that pass tier 1 under the weighted rule as declared are the only rows that keep the #525 variant's recall inside the false-alarm
limit, and they lose tier 5 (or, for the skew-t row, pass it but fail tier 3 like every row); whether that trade is worth a further
reading is a judgement for her.
