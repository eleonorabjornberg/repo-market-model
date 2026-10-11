# The combined model: a passer, a calibrated ordinary-day logistic and a gate (#561, of #374)

A scratch measurement under the pressure-day judge. It writes nothing into `docs/runs/`, publishes nothing, moves no published
figure, scores no day of 2026 and reads no day after 2025-12-31 (`docs/decisions/lockbox.md`; the script refuses a later panel).
No rule, threshold, onset definition, cut-off rule or availability time changes. The combination was declared in
`metadata/combined_model_561.json` and the seven judge candidates in `metadata/pressure_judge/candidates/risk_*+combined*.json`,
all committed (822ab19) before the first forecast was fitted; `scripts/combined_model_561.py` refuses an uncommitted declaration.

**The combination was chosen after seeing the results of #539, #541, #542, #543, #545 and #534 on these same days (2018-06-29 to
2025-12-31). A pass here would not be a confirmation: only the 2026 confirmation window can confirm it, and it is not opened here.
No row is in the confirmation look.**

## What was declared

| part | what |
|---|---|
| risk dates | the passer `risk_gbm`, and `risk_logistic` as a second parent, scored with settlements dated from the announcement and the H.4.1 read per release (#541, arm `both`); a risk date keeps the passer's forecast |
| every other day | one walk-forward ridge logistic of `spread > tau` per threshold, then a Platt curve fitted walk-forward (the hurdle's, #539). Its inputs: the spread; the latent funding-stress factor's filtered level and its change over 5 rows at the forecast's anchor (#543); the four structural terms (#542); the projected-reserves distance at the scored day (#545) |
| calibration | Platt, declared, refit on the judge's cadence. It reads the as-of columns above only, never a hindsight regime label (ruling on #515) |
| gate | #532's `gate` (quantile 0.9 of the component's forecasts on earlier non-risk days, window 250, at least 60), the one of #534's four controls that passed tier 1 under the weighted rule in force; applied to the every-day component only |
| variants (4) | each parent with and without the gate: `risk_gbm+combined`, `risk_gbm+combined_nogate`, `risk_logistic+combined`, `risk_logistic+combined_nogate` |
| ablations (3) | `risk_gbm+combined` with the factor, the structural terms or the projected distance dropped (`_no_factor`, `_no_structural`, `_no_projected`); the gate is dropped by `_nogate`. Analysis rows of criterion 3, not a fifth variant |

The ordinary-day component is `ml.pressure_combined_ordinary_exceedance`. Its training pairs are the direct pairs of every training
day under the as-of rule (`ml._combined_pairs`), and the factor is read at each pair's own anchor row (a recorded mutation kills a read of
the row after it). The factor is filtered forward through each forecast's own as-of history and refuses a history that runs past its forecast
(`LookAheadError`; recorded mutation in `tests/test_ml.py`, `CombinedOrdinaryTests`). The component is scored on the published timing,
the one its inputs were built and scored on; the projected-reserves columns are built from the published H.4.1 lag, so the H.4.1 per-release
reading reaches the passer only.

## Reproduce

Published panel `4ddc3882…` (`verify-panel` clean, unchanged); scratch panel `AUG4` as for #545. `/opt/rmm-venv` (numpy 2.4.6,
scikit-learn 1.9.1), `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`.

```
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
PYTHONPATH=src python3 scripts/net_settlement.py panel --panel AUG2.csv --output AUG3.csv
PYTHONPATH=src python3 scripts/projected_reserves.py panel --panel AUG3.csv --output AUG4.csv
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --output OUT/bench_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/risk_date_severity.py run --panel AUG2.csv --published PUBLISHED.csv --horizon $h --output OUT/risk_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_track_q.py forecasts --panel PUBLISHED.csv --horizon $h --output OUT/q_h$h.json --distribution OUT/qdist_h$h.json
for h in 1 2 3 4 5: for m in risk_gbm risk_logistic: PYTHONPATH=src python3 scripts/announcement_dating_rescore.py run --arm both --model $m --panel AUG2.csv --published PUBLISHED.csv --horizon $h --output OUT/both_${m}_h$h.json   # the two merged into OUT/both_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/combined_model_561.py run --panel AUG4.csv --published PUBLISHED.csv --horizon $h --parents OUT/both_h$h.json --output OUT/cm_h$h.json
# OUT/ql_h$h.json is q_h$h.json with only the ngboost_laplace row (the judge refuses the undeclared rows)
for r in weighted unweighted: PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule $r --output OUT/judge_$r.json --markdown OUT/judge_$r.md OUT/bench_h?.json OUT/risk_h?.json OUT/ql_h?.json OUT/both_h?.json OUT/cm_h?.json
for r in weighted unweighted: PYTHONPATH=src python3 scripts/pressure_judge.py table OUT/judge_$r.json --output OUT/tables_$r.md
PYTHONPATH=src python3 scripts/combined_model_561.py compare --panel PUBLISHED.csv --bench 'OUT/bench_h{h}.json' --risk 'OUT/risk_h{h}.json' --reference 'OUT/ql_h{h}.json' --parents 'OUT/both_h{h}.json' --rows 'OUT/cm_h{h}.json' --output OUT/compare.json --markdown OUT/compare.md
PYTHONPATH=src python3 scripts/combined_model_561.py summary --flat OUT/judge_unweighted.json --weighted OUT/judge_weighted.json --output OUT/summary.md
PYTHONPATH=src python3 scripts/combined_model_561.py refits --output OUT/refits.json OUT/cm_h?.json
```

Evidence: `docs/pivot/evidence/combined-model/` (`summary.md` is Table 1 for every row; `tables-*.md` and `judge-*.md` the judge's tables and
full reports, with tier 1 pooled and per lead, tiers 3 and 5, split by regime and pressure-day type; `compare.md` and `compare.json` the
readings, the calendar-year recall, the Brier score and log loss, the predicted against the realised rate by regime, and every row paired
against every reference with 90% stationary-bootstrap intervals by regime and pressure-day type; `refits.json` each refit's training pairs and
calibrated fits). The control rows reproduce the earlier pages: `risk_gbm` 13 of 26 at 0.80 (weighted), and
`risk_gbm+every_day+gate+settle+h41` 18 of 26 weighted at 1.64, as in [`settlement-h41-dating-result.md`](settlement-h41-dating-result.md).

## Result: no row passes the full rule

Table 1. The judge's row at +5 bp, 90% intervals, tiers 1 / 3 / 5 under the weighted rule in force and, beside it, the flat rule. "Worst
false alarms per onset" is the highest of the five leads; the limit is 2. The full table is `summary.md`.

| row | onsets flagged, flat / weighted | recall, weighted [90%] | worst false alarms per onset, flat / weighted rule | tiers 1 / 3 / 5, weighted | tiers 1 / 3 / 5, flat |
|---|---|---|---|---|---|
| `risk_gbm+combined` | 10 / 10 of 26 | 0.385 [0.212, 0.571] | 1.08 / 1.07 | no / no / no | no / no / no |
| `risk_gbm+combined_nogate` | 11 / 13 of 26 | 0.500 [0.308, 0.684] | 1.38 / 1.74 | **yes** / no / **yes** | no / no / yes |
| `risk_logistic+combined` | 11 / 11 of 26 | 0.423 [0.258, 0.606] | 1.46 / 1.96 | no / no / no | no / no / no |
| `risk_logistic+combined_nogate` | 7 / 10 of 26 | 0.385 [0.226, 0.556] | 1.00 / 1.15 | no / no / no | no / no / no |
| `risk_gbm+combined_no_factor` | 10 / 10 of 26 | 0.385 [0.212, 0.571] | 1.08 / 1.09 | no / no / no | no / no / no |
| `risk_gbm+combined_no_structural` | 9 / 11 of 26 | 0.423 [0.242, 0.609] | 0.85 / 1.06 | no / no / no | no / no / no |
| `risk_gbm+combined_no_projected` | 10 / 10 of 26 | 0.385 [0.200, 0.571] | 1.08 / 1.07 | no / no / no | no / no / no |
| *control:* `risk_gbm+settle+h41` | 14 / 14 of 26 | 0.538 [0.353, 0.710] | 1.35 / 0.88 | yes / no / no | yes / no / no |
| *control:* `risk_gbm+every_day+gate+settle+h41` | 15 / 18 of 26 | 0.692 [0.524, 0.857] | 2.35 / 1.64 | yes / no / no | no / no / no |
| `risk_gbm` (published passer) | 13 / 13 of 26 | 0.500 [0.310, 0.667] | 1.35 / 0.80 | yes / no / no | yes / no / no |
| `ngboost_laplace` | 15 / 17 of 26 | 0.654 [0.467, 0.826] | 2.54 / 1.73 | yes / no / no | no / no / no |

* **No row passes.** Every row fails tier 3. The only row that passes two tiers is `risk_gbm+combined_nogate` under the weighted rule
  (tiers 1 and 5), with worst weighted false alarms of 1.74 per onset; its flat count of false alarms at the weighted rule's cut-offs is 3.69
  per onset, and it passes tier 5 but not tier 1 under the flat rule. The `risk_logistic` parent does not improve on the GBM parent: gated, 11 of
  26 onsets against 10 (worst weighted false alarms 1.96 against 1.07); ungated, 10 against 13.
* **The gate lowers recall.** With it (`+combined`) the model flags 10 onsets, against 13 without (`_nogate`) and 14 for the passer alone with the
  new timing on. Why the declared cut removes onsets as well as false alarms is not diagnosed here.
* **Against the control built from the same parts**, `risk_gbm+every_day+gate+settle+h41` (the three-input component with the gate),
  `risk_gbm+combined_nogate` flags fewer onsets (13 against 18, weighted) at about the same worst weighted false alarms (1.74 against 1.64),
  and is level or worse on Brier (paired below). The control is as good or better on every figure of Table 1 that the judge reads.

Tier 1 per lead (flagged onsets / false alarms per onset, weighted; a lead passes with at least half of 26 flagged and at most 2):

| row | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|
| `risk_gbm+combined` | 8 / 0.39 | 8 / 1.07 | 9 / 0.79 | 9 / 1.05 | 9 / 1.02 |
| `risk_gbm+combined_nogate` | 13 / 1.35 **pass** | 11 / 0.80 | 11 / 1.74 | 9 / 1.23 | 10 / 0.49 |
| `risk_gbm+settle+h41` | 13 / 0.75 **pass** | 11 / 0.58 | 10 / 0.88 | 10 / 0.68 | 11 / 0.76 |
| `risk_gbm+every_day+gate+settle+h41` | 13 / 1.56 **pass** | 12 / 1.39 | 11 / 1.44 | 12 / 1.50 | 15 / 1.64 **pass** |

**Recall by calendar year** (onsets warned at lead 1 or more, any horizon, weighted rule; 2018, 2020 and 2024 are the called-out years):

| row | **2018** | 2019 | **2020** | **2024** | 2025 |
|---|---|---|---|---|---|
| `risk_gbm+combined` | 0 of 4 | 8 of 13 | 0 of 2 | 0 of 2 | 2 of 5 |
| `risk_gbm+combined_nogate` | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 3 of 5 |
| `risk_logistic+combined` | 0 of 4 | 7 of 13 | 0 of 2 | 1 of 2 | 3 of 5 |
| `risk_gbm+settle+h41` | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 4 of 5 |
| `risk_gbm+every_day+gate+settle+h41` | 0 of 4 | 13 of 13 | 1 of 2 | 0 of 2 | 4 of 5 |
| `ngboost_laplace` | 0 of 4 | 12 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |

No combined row flags a 2018 or a 2020 onset, and only `risk_logistic+combined` flags one of the two in 2024; the 2018, 2020 and 2024 onsets stay
unwarned. The `risk_gbm+every_day+gate+settle+h41` control, which has none of the new blocks, flags one of the two in 2020.

## Predicted against realised rate, by regime

Mean forecast of `spread > 5 bp` against the realised rate, pooled over h = 1 to 5 (`compare.md` has every row and the day-type cells). This
is the calibration tier 3 reads, and it is where the combination fails.

| regime | days | realised | `risk_gbm+combined_nogate` | `risk_gbm+combined` | `risk_gbm+every_day+gate+settle+h41` | `ngboost_laplace` |
|---|---|---|---|---|---|---|
| 2018-19 | 1865 | 0.2697 | 0.2972 | 0.0647 | 0.1652 | 0.2217 |
| 2020 | 1255 | 0.0159 | 0.1640 | 0.0071 | 0.0253 | 0.0456 |
| 2021-23 | 3740 | 0.0000 | 0.0354 | 0.0007 | 0.0056 | 0.0005 |
| 2024 | 1250 | 0.0200 | 0.0077 | 0.0001 | 0.0145 | 0.0021 |
| 2025-26 | 1245 | 0.1165 | 0.0433 | 0.0171 | 0.0871 | 0.0229 |

The ungated model is close in 2018-19 (0.297 against 0.270), over-forecasts 2020 and 2021-23 by a wide margin (0.164 against 0.016, 0.035 against
0) and under-forecasts 2025-26 (0.043 against 0.117). The gated model forecasts below the realised rate in every regime in which pressure
occurred. Why the ungated model over-forecasts 2020 is not diagnosed here; the calibration reads no regime label, by declaration.

## Paired against the references

Brier difference, reference minus row (positive: the row is better), 90% stationary-bootstrap interval, pooled, h = 1 / h = 3 / h = 5
(the regime and pressure-day-type cells are in `compare.md`):

| row | vs `risk_gbm` | vs `ngboost_laplace` | vs calendar climatology | vs persistence-logistic |
|---|---|---|---|---|
| `risk_gbm+combined_nogate` | +0.0072 [-0.0022, +0.0182] / +0.0089 [-0.0034, +0.0227] / +0.0068 [-0.0056, +0.0201] | -0.0043 [-0.0094, +0.0012] / +0.0018 [-0.0069, +0.0113] / +0.0009 [-0.0067, +0.0084] | +0.0209 [+0.0123, +0.0303] / +0.0129 [+0.0042, +0.0224] / +0.0081 [-0.0004, +0.0165] | +0.0058 [-0.0013, +0.0139] / +0.0066 [-0.0024, +0.0152] / +0.0006 [-0.0078, +0.0085] |
| `risk_gbm+combined` | -0.0023 [-0.0065, +0.0017] / +0.0005 [-0.0041, +0.0046] / +0.0052 [-0.0007, +0.0108] | -0.0138 [-0.0236, -0.0060] / -0.0066 [-0.0162, +0.0019] / -0.0007 [-0.0090, +0.0067] | +0.0114 [+0.0058, +0.0168] / +0.0045 [-0.0022, +0.0107] / +0.0065 [-0.0004, +0.0127] | -0.0037 [-0.0116, +0.0031] / -0.0018 [-0.0092, +0.0051] / -0.0010 [-0.0084, +0.0054] |

Against the control with the three-input component and the gate (`risk_gbm+every_day+gate+settle+h41`), the ungated combination is level at
h = 1 and h = 3 (-0.0007 [-0.0069, +0.0057], -0.0008 [-0.0088, +0.0073]) and worse at h = 5 (-0.0089 [-0.0165, -0.0013]), and it warns fewer
onsets (recall difference -0.1923 [-0.3333, -0.0667]). The gated combination is worse than that control at every lead
(-0.0102 [-0.0181, -0.0029] at h = 1) and warns fewer onsets (-0.3077 [-0.4615, -0.1538]).
Against `ngboost_laplace` the gated combination is worse at h = 1 and its recall is lower (-0.2692 [-0.4349, -0.1070]); the ungated one is level on Brier and lower on recall (-0.1538 [-0.3077, +0.0000]).
Against `risk_gbm+settle+h41` (the base it is built on) the gated model warns fewer onsets (-0.1538 [-0.3043, -0.0385]).
By regime at h = 1, `risk_gbm+combined_nogate` against that base is better in 2018-19 (+0.0465 [+0.0002, +0.0980]) and 2025-26 (+0.0056 [+0.0006, +0.0120]) and
worse in 2020 (-0.0161 [-0.0232, -0.0096]) and 2021-23 (-0.0013 [-0.0019, -0.0008]).

## Ablation: what each block contributes

Each block dropped in turn from `risk_gbm+combined` (the gated model under `risk_gbm`), paired against it. Brier difference, reference
(the full model) minus row, pooled, h = 1 / h = 3 / h = 5, and the recall difference; the gate is dropped by `_nogate`.

| dropped | judge, weighted: flagged / worst weighted false alarms | Brier, h = 1 / 3 / 5 | recall difference, row minus full |
|---|---|---|---|
| factor (`_no_factor`) | 10 / 1.09 | +0.0000 [-0.0002, +0.0002] / +0.0003 [-0.0002, +0.0009] / +0.0001 [-0.0000, +0.0003] | +0.0000 [+0.0000, +0.0000] |
| structural terms (`_no_structural`) | 11 / 1.06 | -0.0002 [-0.0027, +0.0022] / +0.0012 [-0.0017, +0.0047] / +0.0003 [-0.0031, +0.0040] | +0.0385 [+0.0000, +0.1154] |
| projected distance (`_no_projected`) | 10 / 1.07 | +0.0006 [-0.0001, +0.0014] / -0.0007 [-0.0019, +0.0002] / -0.0000 [-0.0015, +0.0012] | +0.0000 [+0.0000, +0.0000] |
| gate (`risk_gbm+combined_nogate`) | 13 / 1.74 | not paired; pooled Brier 0.0505 / 0.0577 / 0.0628 without the gate, 0.0601 / 0.0661 / 0.0644 with it | 13 of 26 flagged, against 10 |

Under the gate, none of the three data blocks changes the Brier score beyond its interval or the recall by an onset in either direction beyond one
(the structural block's removal flags one more onset). **The gate is the only element that moves the result, and it moves it against the recall.**
One reading, not tested here, is that the spread, which every version reads, carries most of the signal at these leads. This does not say the
blocks are useless, only that on these days, with these 26 onsets, nothing separates them under the gate.

## Not checked, or for Eleonora

* **Nothing here is a confirmation.** The combination and its gate were chosen after seeing the parts' results on the same days; the 2026
  confirmation window is untouched and no row is in the confirmation look. Whether any row joins a published declaration is not asked here.
* The ordinary-day component is scored on the published timing: the projected-reserves columns use the published H.4.1 lag and the structural
  terms read the published reserve level. The announcement-dated settlements and the H.4.1 per-release reading apply to the passer only. A
  version of the columns built under the per-release reading is not scored.
* The calibration is Platt only (declared); isotonic is not scored. The gate is #532's, with its parameters; no other gate or quantile is scored.
* The mean-forecast-against-realised table pools five leads; the realised rate repeats each day at each lead, so its days are not independent.
* The ablation drops one block at a time from the gated model; it does not drop two, and it is run under `risk_gbm` only.
* Calibrated fits: Platt was applied on 154 of 179 fits at h = 1 to 4, and 152 of 177 at h = 5 (the rest had fewer than 250 out-of-sample pairs
  or 5 events, so the curve was the identity); the same counts hold for all four components.
