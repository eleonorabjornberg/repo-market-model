# A calibrated every-day hazard for the risk-date passers: the hurdle model (#539, of #374)

A scratch measurement under the pressure-day judge. It writes nothing into `docs/runs/`, moves no published figure, and reads no
day after 2025-12-31 (`docs/decisions/lockbox.md`; the script refuses a later panel, and the near-blind and blind tiers are not
looked at). No rule, threshold, onset definition, cut-off rule or availability time changes. The variants are off in every
published declaration. They were declared before any score in `metadata/risk_date_hurdle.json` (committed before the first
forecast was fitted) and, for the judge, in `metadata/pressure_judge/candidates/<parent>+hurdle_*.json`;
`scripts/risk_date_hurdle.py` refuses an uncommitted declaration.

## What was declared

The five tier-1 passers of `metadata/risk_date_severity.json` are the parents, unchanged. Each gets four variants of one model,
`ml.pressure_risk_date_hurdle_exceedance`:

> P(pressure) = P(risk date) × the passer's own forecast + P(ordinary day) × an every-day hazard.

Whether a day is a risk date is a fact about the calendar known in advance, so P(risk date) is 1 on a risk date and 0 on any other
day. A risk date therefore keeps the parent's forecast exactly (`RiskDateHurdleTests.test_a_risk_date_keeps_the_risk_date_models_forecast`)
and every other day is served the hazard, which replaces the parent's exact 0.

* **The hazard** is a ridge logistic of `spread > tau` (`ml.PRESSURE_LOGISTIC_SETTINGS`), one per threshold, fitted on the direct
  pairs of every training day under the as-of rule, on `spread_bps` and SOFR's 99th and 75th percentiles above IORB
  (`docs/pivot/source-screen-result.md`). The two `state` variants add the as-of reserve scarcity state (0 to 3).
* **Calibration** is walk-forward and refit with the model, on the judge's 21-day cadence: a refit's training pairs, in date order,
  are cut into five blocks; the hazard fitted on blocks 0 to k-1 forecasts block k, and a Platt or isotonic curve is fitted on those
  out-of-sample forecasts and their labels. The final hazard, fitted on every training pair, is mapped through it. It is the identity
  until the out-of-sample pairs number 250 and hold 5 events, the bake-off's gate (#138).
* **A missing input** no longer forecasts 0. A day whose hazard inputs are not all public is served the hazard fitted without the
  missing ones (always including the spread), calibrated the same way
  (`test_a_day_missing_an_input_is_served_the_model_fitted_without_it`).

| variant | inputs | calibration |
|---|---|---|
| `+hurdle_platt` | spread, SOFR p75 − IORB, SOFR p99 − IORB | Platt |
| `+hurdle_isotonic` | the same | isotonic |
| `+hurdle_state_platt` | those three and the as-of reserve scarcity state | Platt |
| `+hurdle_state_isotonic` | the same four | isotonic |

**A marked question for Eleonora, not settled here.** The directive asks for "regime and scarcity-state inputs already admitted". The
regime labels of `metadata/evaluation_splits.json` were drawn after the fact (`metadata/hindsight_regimes.json`: "whether regime labels
may be inputs at all is Eleonora's decision"). I did not use them as an input. The as-of reserve scarcity state is the regime-like input
in the `state` variants. If she wants the labels in the hazard, that is a separate decision and a separate directive.

Scored as the judge declares: tiers 1, 3 and 5, h = 1 to 5, +5 and +10 bp, under the flat and the weighted miss rule; the cut-off
rule is unchanged and chooses each variant's cut-offs from its own training window. Everything is paired against the parent,
calendar climatology and persistence-logistic. Four variants of five parents is twenty candidates.

## Reproduce

Published panel `4ddc3882…` (`verify-panel` clean); scratch panel as for #428 (`scripts/risk_date_severity.py`).
`/opt/rmm-venv` (numpy 2.4.6, scikit-learn 1.9.1), `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`.

```
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
PYTHONPATH=src python3 scripts/risk_date_hurdle.py declare      # already committed; shown for the record
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --output OUT/bench_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/risk_date_severity.py run --panel AUG2.csv --published PUBLISHED.csv --horizon $h --output OUT/risk_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/risk_date_hurdle.py run --panel AUG2.csv --published PUBLISHED.csv --horizon $h --output OUT/hurdle_h$h.json
for r in weighted unweighted: PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule $r --output OUT/judge_$r.json --markdown OUT/judge_$r.md OUT/bench_h?.json OUT/risk_h?.json OUT/hurdle_h?.json
for r in weighted unweighted: PYTHONPATH=src python3 scripts/pressure_judge.py table OUT/judge_$r.json --output OUT/tables_$r.md
for r in weighted unweighted: PYTHONPATH=src python3 scripts/risk_date_hurdle.py compare --rule $r --panel PUBLISHED.csv --output OUT/compare_$r.json --markdown OUT/compare_$r.md OUT/bench_h?.json OUT/risk_h?.json OUT/hurdle_h?.json
PYTHONPATH=src python3 scripts/risk_date_hurdle.py readings --panel PUBLISHED.csv --output OUT/readings.json --markdown OUT/readings.md OUT/bench_h?.json OUT/risk_h?.json OUT/hurdle_h?.json
PYTHONPATH=src python3 scripts/risk_date_hurdle.py summary --flat OUT/judge_unweighted.json --weighted OUT/judge_weighted.json --output OUT/summary.md
```

Evidence: `docs/pivot/evidence/risk-date-hurdle/` (`summary.md` is Table 1 for every row; `tables-*.md` and `judge-*.md` the judge's
tables and full reports, split by regime and day type; `compare.md` and `compare-weighted.md` the pairing of every variant against
its parent with 90% intervals by year, regime and pressure-day type, the flags on and off the risk dates, the Brier and log-loss
pairing, the predicted and realised rates and the 26 episodes, with the cut-offs chosen under the flat and under the weighted rule
(`compare.json` is the flat one); `readings.md` tier 1 under readings (a), (b) and (e); `tables.md` the tables below for all five
parents). The parents' figures reproduce those of #525 and #532 (for example `risk_gbm`, 13 of 26 at 1.35 false alarms per onset, flat).

## Result: no variant passes the full rule

Table 1 (abridged to `risk_gbm`, `risk_gbm_base` and `risk_logistic_base`; all twenty-five rows are in `summary.md`). The judge's row at
+5 bp under each rule, 90% stationary-bootstrap intervals. "Worst false alarms per onset" is the highest of the five horizons; the limit is 2.

| model | onsets flagged, flat / weighted rule | recall, flat [90%] | recall, weighted [90%] | worst false alarms per onset, flat | worst weighted false alarms per onset, weighted rule | tiers 1 / 3 / 5, flat | tiers 1 / 3 / 5, weighted | passes the full rule, flat / weighted |
|---|---|---|---|---|---|---|---|---|
| risk_gbm | 13/26 / 13/26 | 0.500 [0.310, 0.667] | 0.500 [0.310, 0.667] | 1.35 | 0.80 | yes / no / no | yes / no / no | no / no |
| risk_gbm+hurdle_platt | 15/26 / 15/26 | 0.577 [0.385, 0.760] | 0.577 [0.385, 0.760] | 3.08 | 2.23 | no / no / yes | no / no / yes | no / no |
| risk_gbm+hurdle_isotonic | 15/26 / 16/26 | 0.577 [0.389, 0.783] | 0.615 [0.437, 0.808] | 2.62 | 2.13 | no / no / yes | no / no / yes | no / no |
| risk_gbm+hurdle_state_platt | 15/26 / 15/26 | 0.577 [0.375, 0.760] | 0.577 [0.375, 0.760] | 3.54 | 2.14 | no / no / yes | no / no / yes | no / no |
| risk_gbm+hurdle_state_isotonic | 15/26 / 16/26 | 0.577 [0.385, 0.774] | 0.615 [0.424, 0.800] | 2.46 | 2.11 | no / no / yes | no / no / yes | no / no |
| risk_gbm_base | 14/26 / 14/26 | 0.538 [0.360, 0.719] | 0.538 [0.360, 0.719] | 1.50 | 0.97 | yes / no / no | yes / no / no | no / no |
| risk_gbm_base+hurdle_platt | 15/26 / 15/26 | 0.577 [0.375, 0.769] | 0.577 [0.375, 0.769] | 3.04 | 2.15 | no / no / yes | no / no / yes | no / no |
| risk_gbm_base+hurdle_isotonic | 15/26 / 15/26 | 0.577 [0.385, 0.767] | 0.577 [0.385, 0.767] | 2.54 | 2.18 | no / no / yes | no / no / yes | no / no |
| risk_gbm_base+hurdle_state_platt | 15/26 / 15/26 | 0.577 [0.387, 0.769] | 0.577 [0.387, 0.769] | 3.58 | 2.12 | no / no / yes | no / no / yes | no / no |
| risk_gbm_base+hurdle_state_isotonic | 13/26 / 15/26 | 0.500 [0.304, 0.700] | 0.577 [0.385, 0.778] | 2.69 | 2.10 | no / no / yes | no / no / yes | no / no |
| risk_logistic_base | 13/26 / 15/26 | 0.500 [0.333, 0.680] | 0.577 [0.391, 0.762] | 1.77 | 1.65 | yes / no / no | yes / no / no | no / no |
| risk_logistic_base+hurdle_platt | 11/26 / 12/26 | 0.423 [0.250, 0.600] | 0.462 [0.281, 0.650] | 2.85 | 2.13 | no / no / yes | no / no / yes | no / no |
| risk_logistic_base+hurdle_isotonic | 8/26 / 12/26 | 0.308 [0.158, 0.471] | 0.462 [0.286, 0.636] | 2.00 | 2.12 | no / no / yes | no / no / yes | no / no |
| risk_logistic_base+hurdle_state_platt | 13/26 / 14/26 | 0.500 [0.320, 0.690] | 0.538 [0.364, 0.719] | 2.96 | 2.61 | no / no / yes | no / no / yes | no / no |
| risk_logistic_base+hurdle_state_isotonic | 11/26 / 14/26 | 0.423 [0.250, 0.611] | 0.538 [0.370, 0.720] | 2.46 | 2.45 | no / no / yes | no / no / yes | no / no |

Table 2. Detail for the gradient-boosted and logistic passers, flat rule.

**Tier 1 per lead** (flat rule, +5 bp): onsets flagged at that lead alone of 26 / false alarms per onset.

| model | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|
| risk_gbm | 13 / 1.30 | 8 / 1.08 | 7 / 1.04 | 7 / 0.88 | 7 / 1.04 |
| risk_gbm+hurdle_platt | 12 / 1.44 | 7 / 3.04 | 10 / 2.58 | 9 / 2.38 | 8 / 3.08 |
| risk_gbm+hurdle_isotonic | 13 / 1.48 | 6 / 2.62 | 9 / 2.50 | 8 / 1.96 | 7 / 2.19 |
| risk_gbm+hurdle_state_platt | 13 / 2.04 | 8 / 3.04 | 10 / 3.54 | 9 / 2.73 | 9 / 3.12 |
| risk_gbm+hurdle_state_isotonic | 14 / 2.15 | 6 / 1.92 | 9 / 2.46 | 9 / 2.00 | 7 / 2.27 |
| risk_logistic_base | 13 / 1.70 | 6 / 1.00 | 6 / 1.00 | 7 / 1.12 | 8 / 1.15 |
| risk_logistic_base+hurdle_platt | 5 / 1.44 | 6 / 1.73 | 7 / 1.73 | 7 / 1.85 | 7 / 2.85 |
| risk_logistic_base+hurdle_isotonic | 5 / 0.96 | 4 / 1.35 | 5 / 1.88 | 4 / 1.65 | 5 / 2.00 |
| risk_logistic_base+hurdle_state_platt | 7 / 2.56 | 4 / 1.65 | 7 / 2.85 | 6 / 1.77 | 8 / 2.96 |
| risk_logistic_base+hurdle_state_isotonic | 8 / 2.37 | 4 / 1.19 | 5 / 1.92 | 4 / 1.69 | 7 / 2.38 |

**Recall by year** (onsets flagged at some lead 1 to 5 / onsets in the year, flat rule).

| model | all | 2018 (4) | 2019 (13) | 2020 (2) | 2024 (2) | 2025 (5) |
|---|---|---|---|---|---|---|
| risk_gbm | 13 | 0 | 10 | 0 | 0 | 3 |
| risk_gbm+hurdle_platt | 15 | 0 | 13 | 0 | 0 | 2 |
| risk_gbm+hurdle_isotonic | 15 | 0 | 13 | 0 | 0 | 2 |
| risk_gbm+hurdle_state_platt | 15 | 0 | 13 | 0 | 0 | 2 |
| risk_gbm+hurdle_state_isotonic | 15 | 0 | 13 | 0 | 0 | 2 |
| risk_gbm_base | 14 | 0 | 10 | 0 | 0 | 4 |
| risk_gbm_base+hurdle_platt | 15 | 0 | 13 | 0 | 0 | 2 |
| risk_gbm_base+hurdle_isotonic | 15 | 0 | 13 | 0 | 0 | 2 |
| risk_gbm_base+hurdle_state_platt | 15 | 0 | 13 | 0 | 0 | 2 |
| risk_gbm_base+hurdle_state_isotonic | 13 | 0 | 11 | 0 | 0 | 2 |
| risk_logistic | 14 | 0 | 10 | 0 | 0 | 4 |
| risk_logistic+hurdle_platt | 13 | 0 | 11 | 0 | 0 | 2 |
| risk_logistic+hurdle_isotonic | 13 | 0 | 11 | 0 | 0 | 2 |
| risk_logistic+hurdle_state_platt | 14 | 0 | 12 | 0 | 0 | 2 |
| risk_logistic+hurdle_state_isotonic | 12 | 0 | 11 | 0 | 0 | 1 |
| risk_logistic_base | 13 | 0 | 10 | 0 | 0 | 3 |
| risk_logistic_base+hurdle_platt | 11 | 0 | 9 | 0 | 0 | 2 |
| risk_logistic_base+hurdle_isotonic | 8 | 0 | 8 | 0 | 0 | 0 |
| risk_logistic_base+hurdle_state_platt | 13 | 0 | 12 | 0 | 0 | 1 |
| risk_logistic_base+hurdle_state_isotonic | 11 | 0 | 11 | 0 | 0 | 0 |
| risk_quantile_skewt_base | 14 | 0 | 10 | 0 | 0 | 4 |
| risk_quantile_skewt_base+hurdle_platt | 13 | 0 | 12 | 0 | 0 | 1 |
| risk_quantile_skewt_base+hurdle_isotonic | 12 | 0 | 12 | 0 | 0 | 0 |
| risk_quantile_skewt_base+hurdle_state_platt | 13 | 0 | 12 | 0 | 0 | 1 |
| risk_quantile_skewt_base+hurdle_state_isotonic | 12 | 0 | 12 | 0 | 0 | 0 |

**Predicted against realised pressure rate (+5 bp), h = 1, by regime** (mean forecast / realised frequency over the regime's scored days).

| model | all | 2018-19 | 2020 | 2021-23 | 2024 | 2025-26 |
|---|---|---|---|---|---|---|
| risk_gbm | 0.027 / 0.075 | 0.096 / 0.272 | 0.015 / 0.016 | 0.001 / 0.000 | 0.003 / 0.020 | 0.039 / 0.116 |
| risk_gbm+hurdle_platt | 0.108 / 0.075 | 0.283 / 0.272 | 0.200 / 0.016 | 0.036 / 0.000 | 0.012 / 0.020 | 0.067 / 0.116 |
| risk_gbm+hurdle_isotonic | 0.105 / 0.075 | 0.312 / 0.272 | 0.192 / 0.016 | 0.016 / 0.000 | 0.007 / 0.020 | 0.068 / 0.116 |
| risk_gbm+hurdle_state_platt | 0.093 / 0.075 | 0.280 / 0.272 | 0.165 / 0.016 | 0.014 / 0.000 | 0.004 / 0.020 | 0.068 / 0.116 |
| risk_gbm+hurdle_state_isotonic | 0.095 / 0.075 | 0.314 / 0.272 | 0.142 / 0.016 | 0.009 / 0.000 | 0.003 / 0.020 | 0.070 / 0.116 |
| risk_gbm_base | 0.028 / 0.075 | 0.097 / 0.272 | 0.025 / 0.016 | 0.000 / 0.000 | 0.002 / 0.020 | 0.035 / 0.116 |
| risk_gbm_base+hurdle_platt | 0.109 / 0.075 | 0.284 / 0.272 | 0.211 / 0.016 | 0.036 / 0.000 | 0.011 / 0.020 | 0.064 / 0.116 |
| risk_gbm_base+hurdle_isotonic | 0.106 / 0.075 | 0.313 / 0.272 | 0.203 / 0.016 | 0.016 / 0.000 | 0.006 / 0.020 | 0.065 / 0.116 |
| risk_gbm_base+hurdle_state_platt | 0.094 / 0.075 | 0.281 / 0.272 | 0.175 / 0.016 | 0.014 / 0.000 | 0.003 / 0.020 | 0.065 / 0.116 |
| risk_gbm_base+hurdle_state_isotonic | 0.096 / 0.075 | 0.316 / 0.272 | 0.152 / 0.016 | 0.009 / 0.000 | 0.003 / 0.020 | 0.067 / 0.116 |
| risk_logistic | 0.031 / 0.075 | 0.107 / 0.272 | 0.031 / 0.016 | 0.000 / 0.000 | 0.006 / 0.020 | 0.033 / 0.116 |
| risk_logistic+hurdle_platt | 0.112 / 0.075 | 0.294 / 0.272 | 0.216 / 0.016 | 0.036 / 0.000 | 0.015 / 0.020 | 0.062 / 0.116 |
| risk_logistic+hurdle_isotonic | 0.109 / 0.075 | 0.323 / 0.272 | 0.208 / 0.016 | 0.016 / 0.000 | 0.010 / 0.020 | 0.063 / 0.116 |
| risk_logistic+hurdle_state_platt | 0.097 / 0.075 | 0.291 / 0.272 | 0.181 / 0.016 | 0.014 / 0.000 | 0.007 / 0.020 | 0.063 / 0.116 |
| risk_logistic+hurdle_state_isotonic | 0.100 / 0.075 | 0.326 / 0.272 | 0.158 / 0.016 | 0.009 / 0.000 | 0.007 / 0.020 | 0.065 / 0.116 |
| risk_logistic_base | 0.030 / 0.075 | 0.108 / 0.272 | 0.029 / 0.016 | 0.000 / 0.000 | 0.003 / 0.020 | 0.031 / 0.116 |
| risk_logistic_base+hurdle_platt | 0.112 / 0.075 | 0.295 / 0.272 | 0.215 / 0.016 | 0.036 / 0.000 | 0.012 / 0.020 | 0.060 / 0.116 |
| risk_logistic_base+hurdle_isotonic | 0.108 / 0.075 | 0.324 / 0.272 | 0.207 / 0.016 | 0.016 / 0.000 | 0.007 / 0.020 | 0.061 / 0.116 |
| risk_logistic_base+hurdle_state_platt | 0.097 / 0.075 | 0.292 / 0.272 | 0.179 / 0.016 | 0.014 / 0.000 | 0.004 / 0.020 | 0.060 / 0.116 |
| risk_logistic_base+hurdle_state_isotonic | 0.099 / 0.075 | 0.326 / 0.272 | 0.156 / 0.016 | 0.009 / 0.000 | 0.003 / 0.020 | 0.063 / 0.116 |
| risk_quantile_skewt_base | 0.040 / 0.075 | 0.120 / 0.272 | 0.047 / 0.016 | 0.003 / 0.000 | 0.012 / 0.020 | 0.051 / 0.116 |
| risk_quantile_skewt_base+hurdle_platt | 0.121 / 0.075 | 0.307 / 0.272 | 0.232 / 0.016 | 0.039 / 0.000 | 0.021 / 0.020 | 0.079 / 0.116 |
| risk_quantile_skewt_base+hurdle_isotonic | 0.118 / 0.075 | 0.336 / 0.272 | 0.224 / 0.016 | 0.018 / 0.000 | 0.016 / 0.020 | 0.081 / 0.116 |
| risk_quantile_skewt_base+hurdle_state_platt | 0.106 / 0.075 | 0.304 / 0.272 | 0.197 / 0.016 | 0.016 / 0.000 | 0.013 / 0.020 | 0.080 / 0.116 |
| risk_quantile_skewt_base+hurdle_state_isotonic | 0.108 / 0.075 | 0.338 / 0.272 | 0.174 / 0.016 | 0.012 / 0.000 | 0.013 / 0.020 | 0.083 / 0.116 |

**Brier score and log loss the parent loses to the variant** (positive favours the variant; +5 bp, all scored days, 90% interval).

| model | h | Brier vs parent | log loss vs parent |
|---|---|---|---|
| risk_gbm+hurdle_platt | 1 | +0.0016 [-0.0072, +0.0110] | +0.447 [+0.236, +0.685] |
| risk_gbm+hurdle_platt | 5 | -0.0032 [-0.0121, +0.0061] | +0.525 [+0.285, +0.803] |
| risk_gbm+hurdle_isotonic | 1 | -0.0029 [-0.0138, +0.0079] | +0.389 [+0.186, +0.624] |
| risk_gbm+hurdle_isotonic | 5 | -0.0032 [-0.0120, +0.0057] | +0.509 [+0.280, +0.764] |
| risk_gbm+hurdle_state_platt | 1 | +0.0042 [-0.0044, +0.0147] | +0.465 [+0.260, +0.717] |
| risk_gbm+hurdle_state_platt | 5 | +0.0003 [-0.0080, +0.0101] | +0.547 [+0.306, +0.825] |
| risk_gbm+hurdle_state_isotonic | 1 | -0.0023 [-0.0137, +0.0087] | +0.364 [+0.171, +0.594] |
| risk_gbm+hurdle_state_isotonic | 5 | -0.0039 [-0.0142, +0.0058] | +0.443 [+0.209, +0.696] |
| risk_gbm_base+hurdle_platt | 1 | +0.0016 [-0.0069, +0.0114] | +0.447 [+0.236, +0.691] |
| risk_gbm_base+hurdle_platt | 5 | -0.0032 [-0.0118, +0.0065] | +0.525 [+0.279, +0.805] |
| risk_gbm_base+hurdle_isotonic | 1 | -0.0029 [-0.0133, +0.0080] | +0.389 [+0.189, +0.627] |
| risk_gbm_base+hurdle_isotonic | 5 | -0.0032 [-0.0120, +0.0063] | +0.509 [+0.275, +0.785] |
| risk_gbm_base+hurdle_state_platt | 1 | +0.0042 [-0.0043, +0.0139] | +0.465 [+0.253, +0.692] |
| risk_gbm_base+hurdle_state_platt | 5 | +0.0003 [-0.0087, +0.0101] | +0.547 [+0.314, +0.815] |
| risk_gbm_base+hurdle_state_isotonic | 1 | -0.0023 [-0.0135, +0.0094] | +0.364 [+0.164, +0.590] |
| risk_gbm_base+hurdle_state_isotonic | 5 | -0.0039 [-0.0145, +0.0063] | +0.443 [+0.208, +0.707] |
| risk_logistic+hurdle_platt | 1 | +0.0016 [-0.0073, +0.0114] | +0.447 [+0.235, +0.692] |
| risk_logistic+hurdle_platt | 5 | -0.0032 [-0.0117, +0.0066] | +0.525 [+0.298, +0.820] |
| risk_logistic+hurdle_isotonic | 1 | -0.0029 [-0.0128, +0.0080] | +0.389 [+0.186, +0.635] |
| risk_logistic+hurdle_isotonic | 5 | -0.0032 [-0.0119, +0.0063] | +0.509 [+0.281, +0.791] |
| risk_logistic+hurdle_state_platt | 1 | +0.0042 [-0.0045, +0.0143] | +0.465 [+0.251, +0.699] |
| risk_logistic+hurdle_state_platt | 5 | +0.0003 [-0.0085, +0.0101] | +0.547 [+0.303, +0.823] |
| risk_logistic+hurdle_state_isotonic | 1 | -0.0023 [-0.0141, +0.0090] | +0.364 [+0.159, +0.591] |
| risk_logistic+hurdle_state_isotonic | 5 | -0.0039 [-0.0140, +0.0064] | +0.443 [+0.215, +0.699] |
| risk_logistic_base+hurdle_platt | 1 | +0.0016 [-0.0069, +0.0111] | +0.447 [+0.234, +0.702] |
| risk_logistic_base+hurdle_platt | 5 | -0.0032 [-0.0119, +0.0061] | +0.525 [+0.293, +0.815] |
| risk_logistic_base+hurdle_isotonic | 1 | -0.0029 [-0.0136, +0.0080] | +0.389 [+0.191, +0.612] |
| risk_logistic_base+hurdle_isotonic | 5 | -0.0032 [-0.0118, +0.0063] | +0.509 [+0.280, +0.775] |
| risk_logistic_base+hurdle_state_platt | 1 | +0.0042 [-0.0047, +0.0142] | +0.465 [+0.249, +0.707] |
| risk_logistic_base+hurdle_state_platt | 5 | +0.0003 [-0.0083, +0.0101] | +0.547 [+0.307, +0.816] |
| risk_logistic_base+hurdle_state_isotonic | 1 | -0.0023 [-0.0139, +0.0091] | +0.364 [+0.165, +0.588] |
| risk_logistic_base+hurdle_state_isotonic | 5 | -0.0039 [-0.0139, +0.0061] | +0.443 [+0.214, +0.700] |
| risk_quantile_skewt_base+hurdle_platt | 1 | +0.0016 [-0.0071, +0.0109] | +0.447 [+0.233, +0.681] |
| risk_quantile_skewt_base+hurdle_platt | 5 | -0.0032 [-0.0124, +0.0062] | +0.525 [+0.275, +0.807] |
| risk_quantile_skewt_base+hurdle_isotonic | 1 | -0.0029 [-0.0133, +0.0076] | +0.389 [+0.189, +0.623] |
| risk_quantile_skewt_base+hurdle_isotonic | 5 | -0.0032 [-0.0120, +0.0062] | +0.509 [+0.274, +0.759] |
| risk_quantile_skewt_base+hurdle_state_platt | 1 | +0.0042 [-0.0049, +0.0145] | +0.465 [+0.250, +0.700] |
| risk_quantile_skewt_base+hurdle_state_platt | 5 | +0.0003 [-0.0088, +0.0099] | +0.547 [+0.300, +0.802] |
| risk_quantile_skewt_base+hurdle_state_isotonic | 1 | -0.0023 [-0.0142, +0.0093] | +0.364 [+0.150, +0.610] |
| risk_quantile_skewt_base+hurdle_state_isotonic | 5 | -0.0039 [-0.0138, +0.0060] | +0.443 [+0.201, +0.698] |


## Reading

* **No variant passes the full rule, under either miss rule, on any parent.** Tier 1 fails on false alarms: the worst horizon sits at 2.0
  to 3.8 per onset flat and 2.1 to 2.9 weighted (the limit is 2), and the one row at the limit, `risk_logistic_base+hurdle_isotonic` (2.00 flat),
  reaches it by losing recall (8 of 26 against the parent's 13). Tier 1 is passed by the parents and by no hurdle variant. Tier 3 fails for every
  row, as for the parents and the #525 variant.
* **Tier 5 is passed by 19 of the 20 variants under the flat rule** (the parents all fail it); `risk_quantile_skewt_base+hurdle_platt` is the
  exception. That is the one gain that is new compared with the parents, and it was already the #525 variant's (`risk-date-false-alarm-controls-result.md`).
* **The under-forecast in 2018-19 closes; the one in 2025 does not, and two regimes are now over-forecast.** At h = 1, `risk_gbm` forecasts
  0.096 against a realised 0.272 in 2018-19; `+hurdle_platt` forecasts 0.283 (realised 0.272). In 2025-26 the parent forecasts 0.039
  against 0.117 and the variants 0.067 to 0.070. In 2020 the variants forecast 0.14 to 0.20 against 0.016 and in 2021-23 0.009 to
  0.036 against 0 (for `risk_gbm`; the other parents are alike, Table 2). The hazard is calibrated to the pooled history, which is
  dominated by 2018-19, so it carries that regime's rate into the quiet ones. This is why tier 3, the calibration-by-regime tier, still
  fails: 3 of 4 tested regimes are calibrated for 12 of the 20 variants at h = 1 against at most 2 of 4 for the parents, and 4 of 4 for none.
* **Recall by year: 2018, 2020 and 2024 are not recovered.** Under the flat rule no variant, on any parent, warns any of the 4 onsets of 2018,
  the 2 of 2020 or the 2 of 2024. (Under the weighted rule, `risk_gbm+hurdle_isotonic` and `+hurdle_state_isotonic` warn one of the two of 2020.)
  The gain over `risk_gbm` is in 2019 (10 to 13 of 13; 8 to 12 for `risk_logistic_base`), as for the #525 variant, and 2025 loses one onset (3 to 2). The best overall
  is 15 of 26 against 13; the all-onset recall difference for `risk_gbm+hurdle_platt` is +0.077 [-0.042, +0.217], an interval that
  includes zero. The hazard does not reach the onsets that the directive set out to reach: the signal ranks the missed years best but
  the calibrated probability on those days does not clear the cut-off the judge chooses from the training window.
* **Of the 11 episodes that no parent warns,** every hurdle variant warns 2 or 3 under the flat rule (3 for all of the gradient-boosted and skew-t parents); `compare.md` Table 6.
* **Brier does not improve, log loss does.** The Brier difference against the parent has an interval that includes zero in all 100 horizon-by-variant cells
  (for example `risk_gbm+hurdle_platt`, h = 1, +0.0016 [-0.0072, +0.0110]; h = 5, -0.0032 [-0.0121, +0.0061]). The log loss improves
  by 0.36 to 0.57 nats per day, with an interval above zero in all 100 horizon-by-variant cells, but that is mostly the parent's exact 0 on a pressure day costing the
  declared floor of 1e-6 (`ln` of a million): it measures the removal of the zero, not discrimination. The hazard adds no ranking skill
  over the parent that a squared error can see.
* **Against the #525 variant** (`risk_gbm+every_day`: 15 of 26 at 2.96 false alarms per onset flat, tier 5 passed, tiers 1 and 3
  failed) the hurdle variants are equal in recall (15 of 26) and no better on false alarms (2.5 to 3.5 for `risk_gbm`). Platt or isotonic
  recalibration of the same inputs, and a missing-input fallback, did not change the verdict of #525 and #532: the model still fails tiers 1
  and 3. This is a measurement; nothing here proposes publishing or changing a rule.
* **Isotonic against Platt, and the scarcity state.** Flat, the worst false alarms per onset are 2.0 to 2.7 for the isotonic variants and
  2.9 to 3.6 for the Platt ones on the gradient-boosted and logistic-base parents (for `risk_gbm` 2.46 and 2.62 against 3.08 and 3.54). Isotonic
  pays in recall on the logistics: its step function maps low forecasts to exactly 0 (742 of 1873 scored days at h = 1 for
  `risk_logistic_base+hurdle_isotonic`, in a spot check of the first run), and `risk_logistic_base+hurdle_isotonic` warns 8 of 26. Adding the
  scarcity state moves the tier 3 regime count from 3 of 4 on 4 of 10 variants to 3 of 4 on 8 of 10, and moves the false alarms either way.

## Not checked, or for Eleonora

* The regime labels are not an input (see the marked question above).
* Nothing is published and no rule changes. No 2026 day is scored; the two runs of the judge report only days to 2025-12-31.
* The calibrator is the identity until 250 out-of-sample pairs and 5 events exist, which for the state variants (whose complete-input pairs
  start later) may be a longer stretch; how many fits were calibrated is in the forecast files' `declarations`, which are not committed, and
  only the first fold's count is recorded there, so this reading does not say how long the stretch was.
* The hazard was fitted for `spread > tau` at +5 and +10 bp; only +5 bp is the judge's primary threshold. +10 bp is in the judge reports.
* The `features_read` line was narrowed to the inputs a fit actually reads after the forecasts were produced (so the conformance suite,
  whose frame has no SOFR percentile columns, passes). It changes no forecast.
