# A calibrated stack of the five tier-1 passers (#475)

A scratch measurement for track #374: does a stronger model beat the five tier-1 passers if their probabilities are stacked
and calibrated? It writes nothing into `docs/runs/` and moves no published figure. Scored days 2018-06-29 to 2025-12-31, h = 1
to 5, +5 bp primary (+10 bp reported), 90% stationary-bootstrap intervals. No comparison scores a locked day
(`docs/decisions/lockbox.md`): the 2026 confirmation tier is not opened and the stacks are not named in
`confirmation.candidates`.

**Declared before any score** (commit `da9cf1d`, the declaration `metadata/calibrated_stack.json` and the two candidate files in
`metadata/pressure_judge/candidates/`): two candidates.

* `calibrated_stack_logistic`: a logistic regression of the pressure day on the logits of the five passers' probabilities
  (`risk_gbm`, `risk_gbm_base`, `risk_logistic`, `risk_logistic_base`, `risk_quantile_skewt_base`) and the as-of regime (one
  indicator per regime label), refitted every 21 scored days on the refit's training window alone. The ridge pulls the member
  weights to the equal-weight pool and the regime coefficients to 0.
* `calibrated_stack_isotonic`: the same stack followed by the CORP isotonic recalibration of the outcome on the stack's
  probability, fitted on the same training window.

**Leakage.** The stack is fitted on out-of-sample base forecasts only: each member probability it reads is a walk-forward
forecast made at that day's own decision instant, and the window is the judge's own training window (days whose outcome was
public at the refit's first decision instant, `stacking.training_window`). The isotonic step is fitted on the stack's
walk-forward probabilities for those days, never on its in-sample fit. The guard and its recorded mutations are in
`tests/test_calibrated_stack.py`.

## Result: neither stack passes

Rule in force: weighted miss criteria, adopted by Eleonora on #464 (her attested comment of 9 October 2026; the judge is run
with `--rule weighted`, since `in_force` in `metadata/weighted_miss.json` is still false in the tree). The unweighted rule is
reported beside it.

Table 1. Tiers 1, 3 and 5 at +5 bp, weighted rule. Tier 1 is onsets warned at lead of at least 1, with the worst false alarms
per onset over h = 1 to 5 (flat / weighted; the weighted count must be at most 2). Tier 3 counts the horizons that pass, and
names the regimes with a pressure day whose calibration fails. The members reproduce the weighted-miss run exactly
([`weighted-miss-result.md`](weighted-miss-result.md), Table 1).

| row | tier 1 | warned | FA/onset worst (flat / weighted) | tier 3 horizons passing | regimes not calibrated (h = 1 / h = 5) | tier 5 | pass rule |
|---|---|---|---|---|---|---|---|
| calibrated_stack_logistic | fail | 15 of 26 | 5.12 / 2.50 | 0 of 5 | 2018-19, 2020, 2025-26 / 2018-19, 2020, 2025-26 | fail (beats climatology, not calibrated) | fail |
| calibrated_stack_isotonic | fail | 12 of 26 | 4.62 / 2.05 | 0 of 5 | 2020, 2025-26 / 2020, 2025-26 | fail (beats climatology, not calibrated) | fail |
| risk_gbm | pass | 13 of 26 | 1.38 / 0.80 | 0 of 5 | 2018-19, 2025-26 / 2018-19, 2025-26 | fail (beats climatology, not calibrated) | fail |
| risk_gbm_base | pass | 14 of 26 | 1.50 / 0.97 | 0 of 5 | 2018-19, 2025-26 / 2018-19, 2025-26 | fail (beats climatology, not calibrated) | fail |
| risk_logistic | pass | 16 of 26 | 2.42 / 1.74 | 0 of 5 | 2018-19, 2025-26 / 2018-19, 2025-26 | fail (beats climatology, not calibrated) | fail |
| risk_logistic_base | pass | 15 of 26 | 2.31 / 1.65 | 0 of 5 | 2018-19, 2025-26 / 2018-19, 2025-26 | fail (beats climatology, not calibrated) | fail |
| risk_quantile_skewt_base | pass | 15 of 26 | 2.31 / 1.62 | 0 of 5 | 2018-19, 2020, 2025-26 / 2018-19, 2025-26 | fail (beats climatology, not calibrated) | fail |
| calendar_climatology | fail | 12 of 26 | 6.69 / 3.75 | 0 of 5 | 2018-19, 2020, 2024 / 2018-19, 2020, 2024 | fail (does not beat climatology, calibrated) | fail |
| persistence_logistic | fail | 12 of 26 | 7.04 / 3.25 | 0 of 5 | 2018-19, 2020 / 2018-19, 2020 | fail (does not beat climatology, calibrated) | fail |


Under the unweighted rule (Table 1 of `evidence/calibrated-stack/tables_unweighted.md`) the stacks warn 14 and 11 of 26 onsets
at 3.88 and 3.04 false alarms per onset, so tier 1 fails there as well; no row passes tier 3 or tier 5.

* **Tier 1 fails for both stacks.** The logistic stack warns 15 of 26 onsets, as many as the best members, but at a worst 2.50
  weighted false alarms per onset against the limit of 2. The isotonic stack removes false alarms (2.05 weighted) and loses
  onsets (12 of 26). Every member passes tier 1 on its own; stacking worsens it.
* **Tier 3 fails for every row at every horizon,** the stacks included. The logistic stack is miscalibrated in 2018-19, 2020 and
  2025-26; the isotonic step repairs 2018-19 and leaves 2020 and 2025-26.
* **Tier 5 fails for both:** each beats climatology's Brier and neither is calibrated (the week-ahead mean predicted
  probability is below the realised frequency for both: by 0.077 for the logistic stack and by 0.033 for the isotonic).
* **The probability improves, the alarm does not.** Against climatology the logistic stack's Brier gain is positive at every
  horizon with an interval that excludes 0 (Table 2 of `evidence/calibrated-stack/tables_weighted.md`; members' gains at
  h >= 2 do not exclude 0). Against persistence-logistic neither stack's interval excludes 0 at any horizon, so neither is shown better than
  persistence.

Table 2. Paired against the best single passer (`risk_logistic` under the weighted rule: the most onsets warned in tier 1; `risk_gbm_base` under the unweighted
rule), Brier gain at +5 bp per day, 90% interval, and onset recall by year (an onset is warned if flagged at some h >= 1).

Best single passer (weighted rule): `risk_logistic`. Onsets 26 (warned at some h >= 1).

| row | warned | 2018 (of 4) | 2019 (of 13) | 2020 (of 2) | 2024 (of 2) | 2025 (of 5) |
|---|---|---|---|---|---|---|
| risk_gbm | 13 | 0 | 10 | 0 | 0 | 3 |
| risk_gbm_base | 14 | 0 | 10 | 0 | 0 | 4 |
| risk_logistic | 16 | 0 | 10 | 0 | 1 | 5 |
| risk_logistic_base | 15 | 0 | 10 | 0 | 0 | 5 |
| risk_quantile_skewt_base | 15 | 0 | 10 | 0 | 0 | 5 |
| calibrated_stack_logistic | 15 | 0 | 13 | 0 | 0 | 2 |
| calibrated_stack_isotonic | 12 | 0 | 12 | 0 | 0 | 0 |

Brier gain over `risk_logistic` at +5 bp (mean per day, 90% stationary-bootstrap interval; positive: the stack is better).

| candidate | h=1 | h=2 | h=3 | h=4 | h=5 | onsets warned minus best |
|---|---|---|---|---|---|---|
| calibrated_stack_logistic | +0.0055 [+0.0006, +0.0111] | +0.0059 [+0.0001, +0.0126] | +0.0082 [+0.0015, +0.0159] | +0.0086 [+0.0028, +0.0154] | +0.0096 [+0.0037, +0.0164] | -1 |
| calibrated_stack_isotonic | +0.0013 [-0.0074, +0.0104] | +0.0040 [-0.0056, +0.0150] | +0.0082 [-0.0023, +0.0199] | +0.0058 [-0.0034, +0.0161] | +0.0061 [-0.0047, +0.0186] | -4 |

Unweighted rule:

Best single passer (unweighted rule): `risk_gbm_base`. Onsets 26 (warned at some h >= 1).

| row | warned | 2018 (of 4) | 2019 (of 13) | 2020 (of 2) | 2024 (of 2) | 2025 (of 5) |
|---|---|---|---|---|---|---|
| risk_gbm | 13 | 0 | 10 | 0 | 0 | 3 |
| risk_gbm_base | 14 | 0 | 10 | 0 | 0 | 4 |
| risk_logistic | 14 | 0 | 10 | 0 | 0 | 4 |
| risk_logistic_base | 13 | 0 | 10 | 0 | 0 | 3 |
| risk_quantile_skewt_base | 14 | 0 | 10 | 0 | 0 | 4 |
| calibrated_stack_logistic | 14 | 0 | 13 | 0 | 0 | 1 |
| calibrated_stack_isotonic | 11 | 0 | 11 | 0 | 0 | 0 |

Brier gain over `risk_gbm_base` at +5 bp (mean per day, 90% stationary-bootstrap interval; positive: the stack is better).

| candidate | h=1 | h=2 | h=3 | h=4 | h=5 | onsets warned minus best |
|---|---|---|---|---|---|---|
| calibrated_stack_logistic | +0.0041 [+0.0001, +0.0087] | +0.0073 [+0.0017, +0.0140] | +0.0071 [+0.0016, +0.0136] | +0.0066 [+0.0009, +0.0130] | +0.0103 [+0.0045, +0.0168] | +0 |
| calibrated_stack_isotonic | -0.0002 [-0.0085, +0.0083] | +0.0055 [-0.0043, +0.0170] | +0.0070 [-0.0038, +0.0187] | +0.0038 [-0.0058, +0.0144] | +0.0067 [-0.0043, +0.0193] | -3 |

* **Against the best single passer the logistic stack's Brier gain excludes 0 at every horizon** (+0.0055 to +0.0096 per day),
  but it warns fewer onsets in 2025 (2 against 5) and more in 2019 (13 against 10): the stack trades the recent regime for the
  old one. The isotonic stack's Brier gain does not exclude 0, and it warns more onsets than the best passer in 2019 (12 against 10)
  and fewer in 2024 and 2025 (none, against 1 and 5).
* **Regime and pressure-day type.** The full split by regime and by day type, for both stacks and the five members, against
  climatology and persistence-logistic with intervals, is Table 3 of `evidence/calibrated-stack/tables_weighted.md`; the judge's
  own report is `judge_weighted.md`. The logistic stack's largest per-day gains over climatology are in 2020 and on quarter-end and tax-date days; in
  2025-26, where the recent onsets fall, its gain over persistence-logistic is not distinguishable from 0 (h = 1: -0.0137,
  interval -0.0437 to +0.0101).

**What the stack learned.** Mean fitted weights at h = 1 and +5 bp (83 fitted refits, 7 equal-weight): `risk_gbm` 0.31,
`risk_gbm_base` -0.32, `risk_logistic` -0.07, `risk_logistic_base` 0.18, `risk_quantile_skewt_base` 0.07, regime coefficients
2018-19 +1.88, 2020 -0.47, 2021-23 -1.26, 2024 -0.09, 2025-26 -0.05. The members are close substitutes (their weights offset),
and most of the fit is the regime term: the stack learns that 2018-19 was a high-pressure regime, which does not carry to
2025-26.

**Not checked.** +10 bp under the tiers (reported in the judge report only); the scarce-regime reading is in the judge report,
reported only; other ridge strengths, other regime encodings and other recalibrators (each would be choosing a setting on the
scored days); the two other tier-1 passers of the weighted run (`rare_gbm_focal+recalibrated`, `two_part_logistic`) as members;
the 2026 confirmation tier.

No candidate passes the pass rule, so there is no "Publish?" question.

## Reproduce

Panel `4ddc3882…` (the published panel from the tracked fixtures, `verify-panel` clean) and the scratch panel from
`pressure_v1_1.py panel` then `measurement_fields.py panel`, as in
[`risk-date-severity-result.md`](risk-date-severity-result.md). Run single-threaded (`OMP_NUM_THREADS=1`).

```
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --output OUT/bench_h$h.json
for h in 1 2 3 4 5, for c in risk_gbm risk_gbm_base risk_quantile_skewt_base risk_logistic risk_logistic_base:
    PYTHONPATH=src python3 scripts/risk_date_severity.py run --panel AUG2.csv --published PUBLISHED.csv --horizon $h --candidate $c --output OUT/risk_${c}_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/calibrated_stack.py forecasts --panel PUBLISHED.csv --horizon $h --output OUT/stack_h$h.json OUT/risk_risk_*_h$h.json
for rule in weighted unweighted:
    PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule $rule --output OUT/judge_$rule.json --markdown OUT/judge_$rule.md OUT/bench_h?.json OUT/risk_risk_*_h?.json OUT/stack_h?.json
    PYTHONPATH=src python3 scripts/calibrated_stack.py pair --panel PUBLISHED.csv --rule $rule --judge OUT/judge_$rule.json --output OUT/pair_$rule.json --markdown OUT/pair_$rule.md OUT/bench_h?.json OUT/risk_risk_*_h?.json OUT/stack_h?.json
    PYTHONPATH=src python3 scripts/calibrated_stack.py table OUT/judge_$rule.json --output OUT/tables_$rule.md
```

Evidence: `docs/pivot/evidence/calibrated-stack/`.
