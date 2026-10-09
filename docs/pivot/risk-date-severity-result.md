# The risk-date severity model (#428, track V of #374)

A scratch measurement under the pressure-day judge as amended by the pull request that closes #407. It writes nothing into
`docs/runs/` and moves no published figure (`docs/decisions/lockbox.md`: scored days 2018-06-29 to 2025-12-31 only; the
confirmation window is not looked at). Declared before any score in `metadata/risk_date_severity.json` and, for the judge, in
`metadata/pressure_judge.json`; `scripts/risk_date_severity.py` refuses an uncommitted declaration.

## What was declared

* **Risk dates.** A scored day whose pressure-day type (`EvaluationSplits.day_type`: quarter-end, month-end, tax date) is not
  ordinary; at h = 1 also a day with a coupon settlement. The coupon clause is horizon 1 only because a settlement is public one
  business day ahead and not earlier (`information-set.md`). So at h >= 2 the set is the three calendar types.
* **Forecast.** Fitted on risk-date label days only (each label paired with what was public at its own decision instant);
  the probability on a risk date is the fit's, and on any other day exactly 0 at both thresholds. The judge's cut-off rule never
  picks 0, and `report` refuses a flag on a non-risk day (none occurred).
* **Inputs.** The previous day's spread, the calendar, reserves, the scarcity state (#115, ON RRP buffer inside it), the weekly TGA
  change, gross settlement (net cash need is not built). New: the ON RRP balance, daily TGA and its change (#377), and SOFR p75 and
  p99 above IORB in bp (`sofr_p75_iorb_bps` is added here to `measurement_fields`, off in every published declaration).
* **Estimators.** Logistic and gradient-boosted classifier of the pressure label; skew-t quantile regression of the spread (the
  severity). Each has a `_base` twin with the same estimator and no new input. No reweighting, no recalibration.

## Reproduce

Published panel `4ddc3882…`; scratch panel from `pressure_v1_1.py panel`, then `measurement_fields.py panel`.

```
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/risk_date_severity.py run --panel AUG2.csv --published PUBLISHED.csv --horizon $h --output OUT/risk_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --published --output OUT/bench_h$h.json
PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --output OUT/judge.json --markdown OUT/judge.md OUT/bench_h?.json OUT/risk_h?.json
PYTHONPATH=src python3 scripts/pressure_judge.py table OUT/judge.json --output OUT/tables.md
PYTHONPATH=src python3 scripts/risk_date_severity.py report --panel PUBLISHED.csv --output OUT/risk_dates.json OUT/bench_h?.json OUT/risk_h?.json
```

Evidence: `docs/pivot/evidence/risk-date-severity/` (`judge.md` is the judge's full report, split by regime and day type;
`tables.md` its tables; `risk_dates.json` the all-days and risk-dates-alone reading).

## Result: no risk-date model passes

All six fail tier 3 (calibration by regime) and tier 5 (week-ahead); the four logistic and classifier forms and the quantile twin
meet tier 1's recall (about half of the onsets, lower end of the interval above climatology's recall at the same false-alarm rate)
within two false alarms per onset; the skew-t quantile with the new inputs does not (worst 2.54). Scarce regime alone: the same.

Only 21 of the 27 h = 1 onsets and 13 of the 26 onsets at h >= 2 fall on the declared risk dates. The directive's "about 22 of 26"
holds at h = 1; at h >= 2 the coupon-only mid-month settlements are not risk dates, because a settlement is not public that early.
That caps recall at h >= 2 at one half.

Table 1. +5 bp, judge cut-offs, onsets flagged / onsets, false alarms per onset. "Risk dates" counts only onsets and false alarms on
risk dates; both columns use the same flags.

| model | h | all days | risk dates alone | risk-date Brier (climatology, persistence) | risk-date AUROC |
|---|---|---|---|---|---|
| risk_logistic | 1 | 13/27, 1.78 | 13/21, 2.29 | 0.0781 (0.1320, 0.1019) | 0.915 |
| risk_logistic_base | 1 | 13/27, 1.70 | 13/21, 2.19 | 0.0735 | 0.929 |
| risk_gbm | 1 | 13/27, 1.30 | 13/21, 1.67 | 0.0647 | 0.922 |
| risk_gbm_base | 1 | 13/27, 1.44 | 13/21, 1.86 | 0.0714 | 0.927 |
| risk_quantile_skewt | 1 | 13/27, 2.33 | 13/21, 3.00 | 0.0900 | 0.892 |
| risk_quantile_skewt_base | 1 | 13/27, 1.81 | 13/21, 2.33 | 0.0891 | 0.865 |
| risk_logistic | 5 | 8/26, 1.42 | 8/13, 2.85 | 0.1009 (0.1271, 0.1086) | 0.818 |
| risk_gbm | 5 | 7/26, 1.04 | 7/13, 2.08 | 0.1051 | 0.831 |
| risk_quantile_skewt | 5 | 7/26, 1.85 | 7/13, 3.69 | 0.0867 | 0.883 |

Reference rows at h = 1, all days: calendar climatology 9/27, 4.67; persistence-logistic 4/27, 2.67; published v1 2/27, 2.26.
Over any lead 1 to 5, `risk_logistic` flags 14 of 27 onsets (climatology 10 of 27).

Paired Brier difference on the risk dates, h = 1 (negative favours the model; 90% stationary-bootstrap interval):

* `risk_logistic` vs climatology -0.054 [-0.083, -0.030]; vs persistence-logistic -0.024 [-0.059, +0.005]; vs its twin without the
  new inputs +0.005 [-0.001, +0.012].
* `risk_gbm` vs climatology -0.067 [-0.099, -0.040]; vs persistence-logistic -0.037 [-0.072, -0.009]; vs its twin -0.007 [-0.017, +0.003].
* `risk_quantile_skewt` vs climatology -0.042 [-0.078, -0.011]; vs persistence -0.012 [-0.051, +0.024]; vs its twin +0.001 [-0.015, +0.017].

**The new inputs do not help.** No twin comparison excludes zero, and the `_base` twins are as good or better on recall and
false alarms. The gain over climatology and persistence on risk dates comes from restricting the model to risk dates and the calendar
and scarcity design, not from the dispersion, ON RRP or daily TGA inputs.

## For Eleonora

* The risk-date set (including month-end by `day_type`, and the coupon clause at h = 1 only) and the exact-zero forecast on other days
  are choices of this pull request. A different set (for example a calendar rule for mid-month settlement dates, or a late-December
  window) is a new declaration.
* Net cash need is gross settlement here; no net series was built.
