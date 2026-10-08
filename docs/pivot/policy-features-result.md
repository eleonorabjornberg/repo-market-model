# Policy-register features on the best classifiers (#412, track P of #374)

A scratch measurement under the pressure-day judge as amended by the pull request that closes #407. It writes nothing into
`docs/runs/` and moves no published figure (`docs/decisions/lockbox.md`: scored days 2018-06-29 to 2025-12-31 only; the
confirmation window is not looked at). Declared before any score in `metadata/policy_features.json` and, for the judge, in
`metadata/pressure_judge.json`; `scripts/policy_features.py` refuses an uncommitted declaration.

## What was declared

* **The register as columns.** Nine columns from the point-in-time register of #376 (`repo_model.policy_features`), each read at
  its own row's 16:00 decision instant from the entries announced by then, never from the effective date: days since the latest
  known announcement, days until the earliest known entry takes effect (both capped at 90), the count of known entries not yet
  in force, the IORB offset from the bottom of the target range, and five in-force indicators (balance-sheet runoff, the standing
  repo facility, the supplementary-leverage-ratio exclusion, reserve-management operations, the debt limit reinstated). All nine
  enter at every horizon: the register is public at the decision instant, so nothing leaves at h = 2 to 5. The source is
  `policy_register` in `metadata/sources_measurement.json`; nothing is added to `metadata/sources.json` or `contract.py`.
* **"Best" classifier.** Fixed before scoring, from each track's own table on main under the amended judge: the row that flags the
  most onsets at lead of at least 1, a tie going to the lower worst false alarms per onset. Track W (#381): the gradient-boosted
  classifier with balanced bootstraps (7 of 26 onsets, tied with the focal gbm, 1.19 false alarms per onset against 1.58). Track O
  (#409): the unweighted onset logistic (11 of 26).
* **Controls.** The same two classifiers, re-fitted here on the same panel and fold grid with the inputs their own tracks declared.
  Their rows reproduce the figures of `docs/pivot/judge-amendment-result.md` and `docs/pivot/onset-classifier-result.md` exactly.
* **Calibration and flags.** Unchanged: Platt out of fold against the pressure-day outcome, and the judge's cut-off rule from each
  refit's training window.

## Reproduce

Published panel `4ddc3882…`; scratch panel from `pressure_v1_1.py panel`, then `measurement_fields.py panel`, then
`policy_features.py panel`. Run with `OMP_NUM_THREADS=1` when several horizons run at once.

```
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
PYTHONPATH=src python3 scripts/policy_features.py panel --panel AUG2.csv --output AUG3.csv
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/policy_features.py run --panel AUG3.csv --published PUBLISHED.csv --horizon $h --output OUT/policy_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --output OUT/bench_h$h.json
PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --output OUT/judge.json --markdown OUT/judge.md OUT/bench_h?.json OUT/policy_h?.json
PYTHONPATH=src python3 scripts/pressure_judge.py table OUT/judge.json --output OUT/tables.md
PYTHONPATH=src python3 scripts/onset_classifier.py leads --panel PUBLISHED.csv --output OUT/leads.json OUT/bench_h?.json OUT/policy_h?.json
PYTHONPATH=src python3 scripts/policy_features.py pair --panel PUBLISHED.csv --output OUT/pair.json OUT/bench_h?.json OUT/policy_h?.json
```

The published v1 row is not re-scored here (about 6 CPU-hours per horizon); the benchmarks are `pressure_judge.py forecasts` without
`--published`. The judge's full report is `evidence/policy-features/judge.md`, its tables `tables.md`, the per-lead figures
`leads.json`, the paired differences `pair.json`.

## Result: neither classifier passes with the register

The pass rule is tier 1 (onset warning at lead of at least 1), tier 3 (no crying wolf) and tier 5 (week-ahead window). Both
classifiers fail tiers 1 and 3 with and without the register, within the scarce regime alone as well. This is reported as a failing
track under the blanket ruling of 8 October 2026 on #374.

Table 1. Tiers at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals, as the judge reports them. Each control is followed by its
register twin.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes with pressure, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.00 | 2.7 / 4.4 | 1 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| onset_logistic+recalibrated | 11 of 26 | 0.423 [0.250, 0.586] | 0.231 | 3.54 | 0.2 / 0.3 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| onset_logistic_policy+recalibrated | 15 of 26 | 0.577 [0.406, 0.742] | 0.231 | 3.23 | 0.5 / 1.0 | 2 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.231 | 3.42 | 0.5 / 0.0 | 2 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| rare_gbm_balanced_bootstrap+recalibrated | 7 of 26 | 0.269 [0.105, 0.438] | 0.115 | 1.19 | 0.0 / 0.0 | 2 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |
| rare_gbm_balanced_bootstrap_policy+recalibrated | 6 of 26 | 0.231 [0.087, 0.375] | 0.154 | 1.65 | 0.0 / 0.0 | 3 of 4 | yes, yes | fail (tiers no / no / yes) | fail (no / no / yes) |

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; the number of pressure days in the group in brackets.

Table 2. Onset recall and false alarms per onset at each lead, +5 bp, under the judge's own cut-offs: onsets flagged at exactly that
horizon / onsets (share), then false alarms (flags on days that are not pressure days) per onset.

| model | h=1 | h=2 | h=3 | h=4 | h=5 |
|---|---|---|---|---|---|
| calendar_climatology | 9/27 (0.33), 4.67 | 10/26 (0.38), 4.88 | 10/26 (0.38), 4.92 | 10/26 (0.38), 4.96 | 10/26 (0.38), 5.00 |
| onset_logistic+recalibrated | 11/27 (0.41), 3.41 | 6/26 (0.23), 2.35 | 8/26 (0.31), 2.81 | 5/26 (0.19), 2.35 | 7/26 (0.27), 1.35 |
| onset_logistic_policy+recalibrated | 13/27 (0.48), 3.11 | 10/26 (0.38), 2.77 | 7/26 (0.27), 1.96 | 8/26 (0.31), 1.88 | 8/26 (0.31), 1.42 |
| persistence_logistic | 4/27 (0.15), 2.67 | 6/26 (0.23), 3.42 | 6/26 (0.23), 2.81 | 6/26 (0.23), 3.15 | 5/26 (0.19), 2.81 |
| rare_gbm_balanced_bootstrap+recalibrated | 6/27 (0.22), 1.07 | 1/26 (0.04), 0.62 | 1/26 (0.04), 0.23 | 2/26 (0.08), 0.96 | 2/26 (0.08), 1.19 |
| rare_gbm_balanced_bootstrap_policy+recalibrated | 5/27 (0.19), 1.59 | 2/26 (0.08), 0.50 | 1/26 (0.04), 0.65 | 2/26 (0.08), 0.69 | 2/26 (0.08), 1.23 |

Table 3. The register's paired effect on the pressure-day Brier score, +5 bp: the control's Brier minus its register twin's, per
horizon, on the same days and resamples (the judge's stationary bootstrap, 90% interval). Positive: the classifier with the
register scores better. This table is descriptive and was added after the scores were computed; it reads the same forecasts the
judge reads.

| classifier with the register, against its control | h=1 | h=2 | h=3 | h=4 | h=5 |
|---|---|---|---|---|---|
| onset_logistic_policy vs onset_logistic | +0.0050 [+0.0028, +0.0074] | +0.0032 [+0.0012, +0.0055] | +0.0039 [+0.0017, +0.0064] | +0.0035 [+0.0014, +0.0059] | +0.0021 [-0.0001, +0.0044] |
| rare_gbm_balanced_bootstrap_policy vs rare_gbm_balanced_bootstrap | -0.0013 [-0.0074, +0.0046] | +0.0019 [-0.0056, +0.0090] | +0.0028 [-0.0034, +0.0095] | +0.0039 [-0.0019, +0.0095] | +0.0028 [-0.0016, +0.0077] |

Table 4. Share of the +5 bp pressure days flagged at h = 1, by regime and pressure-day type; the number of pressure days in the group
in brackets (judge `tables.md`, Table 2).

| model | regime: 2018-19 | regime: 2020 | regime: 2021-23 | regime: 2024 | regime: 2025-26 | day_type: month_end | day_type: ordinary | day_type: quarter_end | day_type: tax_date |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.70 (102) | 0.00 (4) | – | 0.00 (5) | 0.03 (29) | 0.53 (17) | 0.50 (101) | 0.44 (9) | 0.62 (13) |
| onset_logistic+recalibrated | 0.52 (102) | 0.00 (4) | – | 0.20 (5) | 0.07 (29) | 0.47 (17) | 0.36 (101) | 0.67 (9) | 0.46 (13) |
| onset_logistic_policy+recalibrated | 0.48 (102) | 0.75 (4) | – | 0.20 (5) | 0.28 (29) | 0.59 (17) | 0.39 (101) | 0.56 (9) | 0.54 (13) |
| persistence_logistic | 0.45 (102) | 0.25 (4) | – | 0.00 (5) | 0.48 (29) | 0.41 (17) | 0.48 (101) | 0.33 (9) | 0.23 (13) |
| rare_gbm_balanced_bootstrap+recalibrated | 0.22 (102) | 0.00 (4) | – | 0.00 (5) | 0.07 (29) | 0.24 (17) | 0.16 (101) | 0.33 (9) | 0.08 (13) |
| rare_gbm_balanced_bootstrap_policy+recalibrated | 0.14 (102) | 0.00 (4) | – | 0.00 (5) | 0.14 (29) | 0.29 (17) | 0.10 (101) | 0.22 (9) | 0.08 (13) |

Table 5. h = 1, +5 bp: descriptive measures at the judge's chosen cut-off (judge `judge.md`) and the knowledge holdouts
(`metadata/events.json`), pressure days flagged of those in the window.

| model | cut-off | flags | recall | precision | Brier | AUROC | Sep 2019 (5 pressure days) | Mar 2020 (3 pressure days) |
|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 0.286 | 198 | 0.514 | 0.364 | 0.0714 | 0.586 | 5 of 5 | 0 of 3 |
| persistence_logistic | 0.285 | 133 | 0.436 | 0.459 | 0.0563 | 0.876 | 5 of 5 | 1 of 3 |
| onset_logistic+recalibrated | 0.377 | 148 | 0.400 | 0.378 | 0.0623 | 0.686 | 2 of 5 | 0 of 3 |
| onset_logistic_policy+recalibrated | 0.305 | 145 | 0.436 | 0.421 | 0.0573 | 0.776 | 2 of 5 | 3 of 3 |
| rare_gbm_balanced_bootstrap+recalibrated | 0.644 | 53 | 0.171 | 0.453 | 0.0625 | 0.853 | 0 of 5 | 0 of 3 |
| rare_gbm_balanced_bootstrap_policy+recalibrated | 0.715 | 61 | 0.129 | 0.295 | 0.0638 | 0.835 | 0 of 5 | 0 of 3 |

## What this says

* **The register helps the onset logistic and does nothing for the gbm.** With the register the onset logistic flags 15 of 26 onsets
  at lead of at least 1 (recall 0.577 [0.406, 0.742]) against 11 (0.423 [0.250, 0.586]), and its pressure-day Brier improves at
  every horizon, with an interval above zero at h = 1 to 4 (Table 3). The gbm with balanced bootstraps flags 6 of 26 against 7, and
  its Brier difference has an interval across zero at every horizon.
* **It does not pass.** The onset logistic's worst false alarms per onset fall from 3.54 to 3.23, still above the limit of 2, so
  tier 1 fails: recall clears one half and the false-alarm condition does not. Tier 3 still fails on calibration by regime (2018-19
  and 2020 stay uncalibrated at h = 1). Tier 5 fails for both onset rows, which are not calibrated on the week-ahead window.
* **Where the gain sits.** The onset logistic's flags at lead 2 rise from 6 to 10 of 26 and its share of 2020 and 2025-26 pressure days
  flagged at h = 1 from 0.00 and 0.07 to 0.75 and 0.28 (Tables 2 and 4); 2018-19, which holds most of the pressure days, is
  unchanged (0.52 to 0.48). Four 2020 pressure days and 29 in 2025-26 are small groups; no interval is given for these shares.
* **The knowledge holdouts** do not move together: the onset logistic with the register flags all three March 2020 pressure days (without it,
  none) and two of five in September 2019 (as without it); the gbm flags none of either, with or without the register. Descriptive,
  from windows too short for an interval.
* **Reading the register.** Several columns are constant over long stretches (the standing repo facility from July 2021, the debt
  limit reinstated for two stretches) and the register holds 104 entries, against 26 onsets, so what each column adds cannot be told
  apart here. In Table 5 the onset logistic's AUROC at h = 1 rises from 0.686 to 0.776 and its chosen cut-off falls from 0.377 to
  0.305; the gbm's AUROC falls from 0.853 to 0.835.
* **Not checked:** no variant of the nine columns (a subset, other caps, other kinds of entry) was tried, by design; the +10 bp
  threshold is scored by the judge (`judge.md`) but is not the pass condition; the unrecalibrated fits are kept in the forecast files
  as an ablation and are not judged; the published v1 row is not re-scored; no confirmation-window look was taken.
