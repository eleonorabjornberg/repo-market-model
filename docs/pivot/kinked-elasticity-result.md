# A kinked elasticity in the structural model (#626, ruling on #597)

A scratch measurement under the pressure-day judge. It writes nothing into `docs/runs/`, publishes nothing, moves no published
figure, scores no day of 2026 and reads no day after 2025-12-31 (`docs/decisions/lockbox.md`; the scripts refuse a later panel).
The published scarcity indicator and its 0.12 band are unchanged, and none of these rows is added to the frozen shortlist of #567.
The variants and every constant were declared in [`metadata/kinked_626.json`](../../metadata/kinked_626.json) and the three new judge
candidates in `metadata/pressure_judge/candidates/` (`structural_kinked_fitted`, `structural_kinked_rolling`,
`structural_liquidity+h41`), committed (338be31) before the first forecast was fitted; `scripts/kinked_626.py` refuses an uncommitted
declaration.

**The variants were built after #569 and #587 showed what the fixed 0.12 does on these same days (2018-06-29 to 2025-12-31), and the
2025 onsets are among the days scored. A pass here is not a confirmation (ruling on #567): only the 2026 confirmation window can
confirm anything, it is not opened here, and nothing on this page joins the frozen shortlist.**

## What was declared

| row | elasticity | level |
|---|---|---|
| `structural_liquidity` (control, as on main) | `exp(-(ratio - level) / 0.01)` | 0.12; the reserves read on the earlier weekly lag |
| `structural_liquidity+h41` (like-for-like control) | as above | 0.12; the reserves read per H.4.1 release |
| `structural_kinked_fitted` (a) | `exp(max(0, level - ratio) / 0.01)`: 1 at and above the level | the fitted kink of #587 form (b), one per refit |
| `structural_kinked_rolling` (b) | as (a) | the rolling level of #587 form (a), `satiation_roll`, constants unchanged |

Every other term (drain, TGA rise, tax-date and window terms, the ridge logistic) is the control's.

**Question for Eleonora: the sign of the exponent.** The directive writes the kinked curve as `exp(-max(0, level - ratio) / 0.01)`. Read
literally that is at most 1 and falls as reserves fall below satiation, the reverse of "exponential below it" and of the demand curve's
meaning. The declared curve has the positive exponent below the level, which equals `max(1, the control's e)`. The literal sign was not
scored. If she meant the literal one, the rows need a re-run; the declaration records the reading.

**Dating.** The reserves leg of the ratio, `satiation_roll` and the distance columns are read per H.4.1 release, as #622 requires
(`metadata/h41_release_dating.json`). #623 had not merged; the construction here is this directive's own and does not depend on it, and
#618 and #620 (open in #623) are not applied to the structural drain. The comparator `risk_gbm+settle+h41+dist_roll` is re-built here
with its distance column per release, so its figures are not those of #598's page (which reads the earlier lag).

## Result (weighted rule in force, +5 bp, h = 1 to 5)

Tier 1 pooled (lead >= 1; 26 onsets; weighted false alarms per onset, limit 2), then tiers 3 and 5 from the judge's Table 1
(full tables, tier 1 at each lead alone and the paired intervals by regime, pressure-day type and scarcity state:
[`evidence/kinked/report.md`](evidence/kinked/report.md)):

| row | onsets flagged | recall [90%] | weighted false alarms per onset | tiers 1 / 3 / 5 | 2025 onsets | 2019 |
|---|---|---|---|---|---|---|
| `structural_liquidity` (as on main) | 11 | 0.423 [0.250, 0.613] | 1.69 | no / yes / yes | 0 of 5 | 11 of 13 |
| `structural_liquidity+h41` | 10 | 0.385 [0.208, 0.556] | 1.48 | no / no / yes | 0 of 5 | 10 of 13 |
| `structural_kinked_fitted` | 10 | 0.385 [0.219, 0.571] | 2.12 | no / no / yes | 0 of 5 | 10 of 13 |
| `structural_kinked_rolling` | 15 | 0.577 [0.400, 0.762] | 4.64 | no / no / yes | 4 of 5 | 10 of 13 |
| `risk_gbm+settle+h41` (comparator parent) | 14 | 0.538 [0.353, 0.710] | 1.44 | yes / no / no | 4 of 5 | 10 of 13 |
| `risk_gbm+settle+h41+dist_roll` (comparator) | 15 | 0.577 [0.400, 0.762] | 1.17 | yes / no / no | 5 of 5 | 10 of 13 |

Recall by year for the structural rows is 0 of 4 in 2018 and 0 of 2 in 2024 in every row; 2020 is 0 of 2 except `structural_kinked_rolling`
(1 of 2).

- **Variant (a), the fitted level, does what #587 said a kink would need to: the level now moves the forecast.** The forecasts differ
  from the like-for-like control's (`tests/test_satiation.py`, `test_a_fitted_level_changes_the_kinked_forecasts_and_not_the_unkinked_ones`).
  But it does not help. Onsets flagged are the control's 10 of 26 with the same recall, the false alarms rise from 1.48 to 2.12 and past
  the limit of 2, and it warns no 2025 onset. Against the like-for-like control, the pooled onset-recall difference is 0.000 [0.000,
  0.000] and the Brier difference includes 0 at every pooled horizon (h = 1: -0.003 [-0.007, +0.001]). In 2025-26 it flags 0.07 of the
  pressure days at h = 1, where the control flags 0.34 (Table 2).
- **Variant (b), the rolling level, warns the 2025 onsets (4 of 5) and pays for it.** Recall 0.577, the onset-recall difference against
  the like-for-like control +0.192 [0.000, 0.391] on 26 onsets, but the weighted false alarms per onset are 4.64, past the limit of 2,
  and tier 3 loses a calibrated regime (1 of 2 tested). The Brier difference against the control includes 0 pooled at every horizon
  (h = 1: -0.001 [-0.009, +0.006]; h = 5: +0.006 [-0.011, +0.022]). By regime it is better in 2018-19 (h = 5: +0.065 [0.012, 0.121]) and
  2025-26 (h = 1: +0.023 [0.007, 0.042]) and worse in 2020 (h = 1: -0.050 [-0.093, -0.019]).
- **No tier 1 verdict changes and no pass changes.** Every structural row fails tier 1 pooled, as the control does. The comparator
  passes tier 1; no structural row reaches it, and the difference in recall between `structural_kinked_rolling` and the comparator is
  0.000 [-0.161, +0.174] with Brier differences whose intervals include 0.
- **The per-release reading alone moves the control.** `structural_liquidity+h41` against `structural_liquidity` loses tier 3 and
  moves forecasts by up to 0.76 in a probability on a day; the exponential curve is sensitive to a one-release difference in reserves.
  That is a finding about the control, not about the kink.

### Share of days on which the kink is active, by year (h = 1 decision rows)

| level | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| rolling level (b) | 74% | 66% | 0% | 0% | 30% | 19% | 2% | 53% |
| fitted level (a) | 100% | 100% | 9% | 8% | 88% | 15% | 2% | 33% |
| fixed 0.12 (reference) | 100% | 100% | 26% | 0% | 0% | 0% | 0% | 16% |

The rolling row matches #621's shares to within a few points (it is read per release here). The fitted level was 0.17 to 0.185 from
late 2021 through 2022, when the ratio was far above any pressure (`evidence/kinked/report.md` and `refits` in the run files), so the
kink is on for 88% of 2022 in variant (a): its flat region above the level is then empty. The rolling level is on for 19% to 30% of 2022-23,
years with no pressure days, which is #621's point: it is a two-year reserves low.

### On the days that are not risk dates (the scheduled risk-date rule; 1568 days, 87 above +5 bp at h = 1)

AUROC and the reliability line `logit P(y = 1) = intercept + slope * logit(p)` of the outcome on the forecast (#616; calibrated: intercept 0,
slope 1), 90% stationary-bootstrap intervals; h = 1 here, h = 2 to 5 in `evidence/kinked/extras.md`:

| row | AUROC | AUROC minus the like-for-like control | intercept | slope |
|---|---|---|---|---|
| `structural_liquidity` | 0.876 [0.822, 0.918] | -0.006 [-0.017, 0.003] | -1.26 [-1.97, -0.48] | 0.64 [0.45, 0.92] |
| `structural_liquidity+h41` | 0.883 [0.832, 0.922] | – | -1.37 [-2.11, -0.55] | 0.59 [0.40, 0.89] |
| `structural_kinked_fitted` | 0.876 [0.825, 0.917] | -0.006 [-0.013, -0.001] | -1.42 [-2.15, -0.68] | 0.57 [0.39, 0.83] |
| `structural_kinked_rolling` | 0.882 [0.829, 0.921] | -0.001 [-0.018, 0.014] | -0.86 [-1.72, 0.00] | 0.74 [0.52, 1.04] |
| `persistence_logistic` | 0.898 [0.848, 0.935] | +0.015 [0.000, 0.030] | -0.37 [-1.26, 0.49] | 1.05 [0.73, 1.43] |
| `risk_gbm+settle+h41+dist_roll` | 0.498 [0.472, 0.531] | -0.385 | -2.41 | 0.03 |

The structural rows rank the ordinary days about as well as persistence does (0.88) and no variant improves on the control's AUROC
(differences are -0.02 to +0.01 at every horizon, intervals include 0 except fitted at h = 1 and 2). All are over-confident and biased
high: the slope is 0.4 to 0.7 and the intercept is negative, i.e. the forecasts run high and too spread out; the rolling form is nearest
to calibrated (slope 0.74 at h = 1), which comes with its extra false alarms. The risk-date passers forecast almost 0 on these days and so
have no ranking (AUROC 0.50), as designed.

## The ruling on #567

**A pass here is not a confirmation.** These variants were built, and their level fitted or chosen, after the 2018-2025 days (including the
2025 onsets) had been scored, so a better 2025 is not evidence for the 2026 window. No variant here passes the full rule or tier 1; none is
added to the frozen shortlist. Only Eleonora can replace a shortlist slot, before the 2026 window opens.

## Not checked, or for Eleonora

- **The sign of the exponent** (above): the declared reading is the economically sensible one; the literal one was not scored.
- **Whether a kinked structural row is worth carrying at all.** Variant (a) is a null result; variant (b) trades 2025 recall for false alarms
  past the limit, as the unkinked rolling level of #587 did.
- **#618 and #620** (the structural drain at h = 2 to 5 and partly announced classes) are in #623 and are not applied: the structural rows
  here carry the drain as on main. A re-score after #623 would move them.
- **The 26 onsets are 17 in 2018-19, 2 in 2020, 2 in 2024 and 5 in 2025:** a difference of one onset is inside every interval.
- **Not risk dates** is the calendar rule of the judge's grid (`risk_date` grouping), not each passer's own rule at h >= 2.
- #571's pull request is not merged on main; the scarcity state the judge's tiers use is the one in force on main.

## Reproduce

Published panel `4ddc3882…` (`verify-panel` clean, unchanged); scratch panels `AUG` to `AUG4` as in
[`satiation-result.md`](satiation-result.md), `AUG5` adds `satiation_roll`, `satiation_dist_roll` and `satiation_hinge_roll` per release
(`scripts/kinked_626.py panel`). `/opt/rmm-venv` (numpy 2.4.6, scikit-learn 1.9.1), `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`.
The commands are the module docstring of `scripts/kinked_626.py`.

Evidence: [`evidence/kinked/`](evidence/kinked/) (`report.md` the tables above and more; `compare.json` and `compare.md`; `extras.json` and
`extras.md`).
