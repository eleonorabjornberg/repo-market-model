# The published model against its direct-pairs twin (#450)

A scratch measurement. It writes nothing into `docs/runs/` and moves no published figure, declaration or live pin. Scored days are
2018-06-29 to 2025-12-31 only (`docs/decisions/lockbox.md`): the panel is cut at 2025-12-31 before any fit and the 2026 window is not
looked at. The twin, the test, the splits and the statistics were declared in `metadata/direct_pairs_twin.json`, committed before any
score (`scripts/direct_pairs_twin.py`, `docs/pivot/evidence/direct_pairs/score.json`).

## The question

Finding #449: the published gbm is fitted on one-step pairs (a target's design row is the row before it) but is handed, at prediction, the
as-of row, whose latest spread is two rows before the target. Does training on the pairs the model is used on
(`training_pairs="direct"`) remove the two-day lag of the median, and does it improve the forecast?

## Result in one paragraph

**No.** Under the declared test the twin is slightly **worse** than the published model: mean CRPS 1.704 against 1.659 bp, a paired difference
of −0.045 bp with 90% interval [−0.080, −0.011]. The best lag stays at 2 days for both. It helps on turning-point days and month-ends and
hurts on ordinary days and in 2021–23. The two-day lag is not removed by this change of training; the 0.19 bp ceiling of #449 needs the
actual spread of the day before, which no training choice supplies. Nothing here changes a published figure, and since the twin is not
better, no "Publish?" issue is opened.

## 1. The twin

`published_gbm_direct` is the published side of `final_test_preregistration.CRPS_COMMAND` with one added flag, `--training-pairs-b direct`:
same features, quantile levels, `conformal_pid_nested` calibration, minimum history and refit schedule. The walk confirms the fitted model
reports `training_pairs: direct` and the published side names no such setting. The published walk reproduces
`docs/runs/published_distribution_daily_h1.json` exactly on every scored day.

## 2. CRPS at h = 1 (bp; lower is better)

Gain = CRPS(first) − CRPS(second) per day; positive favours the second; 90% stationary-bootstrap interval (block length 2, 2000 replications).

| Cell | Days | Persistence | Published | Twin | Twin gain over published | Verdict |
|---|---|---|---|---|---|---|
| **All scored days** | 1873 | 2.086 | 1.659 | 1.704 | −0.045 [−0.080, −0.011] | **twin worse** |
| regime 2018–19 | 375 | 5.470 | 3.821 | 3.907 | −0.085 [−0.210, +0.038] | no difference |
| regime 2020 | 251 | 1.352 | 1.279 | 1.275 | +0.004 [−0.069, +0.087] | no difference |
| regime 2021–23 | 748 | 0.589 | 0.672 | 0.756 | −0.084 [−0.110, −0.060] | twin worse |
| regime 2024 | 250 | 1.433 | 1.168 | 1.115 | +0.053 [−0.008, +0.115] | no difference |
| regime 2025–26 | 249 | 2.883 | 2.244 | 2.257 | −0.013 [−0.129, +0.104] | no difference |
| ordinary days | 1603 | 1.796 | 1.310 | 1.378 | −0.068 [−0.101, −0.035] | twin worse |
| month-end | 150 | 2.203 | 1.866 | 1.715 | +0.151 [+0.030, +0.277] | twin better |
| tax date | 89 | 5.499 | 5.866 | 5.787 | +0.079 [−0.191, +0.298] | no difference |
| quarter-end | 31 | 6.742 | 6.631 | 6.764 | −0.132 [−0.430, +0.179] | no difference |
| pressure days (> +5 bp) | 140 | 12.009 | 9.196 | 9.123 | +0.073 [−0.229, +0.363] | no difference |
| other days | 1733 | 1.284 | 1.050 | 1.105 | −0.054 [−0.083, −0.025] | twin worse |
| turning-point days | 100 | 10.209 | 9.323 | 8.786 | +0.537 [+0.275, +0.801] | twin better |

**Against as-of persistence** (gain of the model over persistence, positive favours the model): published +0.427 [+0.185, +0.760]; twin
+0.382 [+0.135, +0.707]. On pressure days (> +5 bp): published +2.813 [+0.235, +7.094], twin +2.886 [+0.281, +7.070]. Both beat persistence
overall; the twin's edge over persistence is smaller than the published model's by the 0.045 above.

## 3. The lag

Correlation of the forecast median of day `T` with the actual spread of day `T−k`, all 1873 days:

| k | −1 | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|---|
| as-of persistence | 0.392 | 0.426 | 0.553 | **1.000** | 0.552 | 0.424 |
| published | 0.592 | 0.604 | 0.645 | **0.680** | 0.649 | 0.613 |
| twin | 0.584 | 0.596 | 0.611 | **0.627** | 0.612 | 0.585 |

The best lag is 2 for the published model and for the twin; the paired difference in best lag (twin − published) is 0 [−2, +1]. The twin's
correlation is lower than the published model's at k = 0, 1 and 2 (paired differences −0.008, −0.033, −0.053, every interval below zero), and its
profile over k is flatter. By regime the best lag is 2 for both in every regime. Split by day type or +5 bp outcome the best lag moves around
for both models (for example −1 on ordinary days, 5 on month-ends and tax dates for the twin) because the correlation profile is nearly flat
there; the tables are in `score.json` and carry no claim.

**Median error on turning-point days** (100 scored days, mean absolute error of the median, bp): published 11.784, twin 11.130; the twin is closer by
0.655 [+0.307, +1.023]. Over all days the twin's median is further from the actual spread than the published one's: 2.380 against 2.265, further
by 0.115 [0.057, 0.174].

## 4. Calibration

Share of scored days whose actual spread lies in the band (nominal 0.50 and 0.90):

| Cell | Published 50% | Twin 50% | Published 90% | Twin 90% |
|---|---|---|---|---|
| all | 0.318 | 0.385 | 0.887 | 0.876 |
| 2018–19 | 0.347 | 0.352 | 0.861 | 0.843 |
| 2020 | 0.347 | 0.422 | 0.896 | 0.896 |
| 2021–23 | 0.290 | 0.360 | 0.910 | 0.894 |
| 2024 | 0.348 | 0.444 | 0.844 | 0.868 |
| 2025–26 | 0.301 | 0.418 | 0.892 | 0.859 |

Neither model's 50% band covers anywhere near half the days (the published model's covers under a third); the twin's is closer to nominal
in every regime, and its 90% band is slightly below the published one's in three regimes, equal in one (2020) and above in one (2024). That is a property of the published
model's bands, not something the twin fixes: the 50% band remains well short in every regime.

## What was not checked, and what is for Eleonora

* One twin, one horizon (h = 1). Horizons 2 to 5, and the pressure classifier fitted on direct pairs, are not scored.
* No other training-pair choice, and no tuning: the twin is the fitter's existing `direct` option as it stands.
* The turning-point definition is the one declared in #445 (PR #447), restated in the declaration because that branch is not on `main`.
* The twin is not better under the declared test, so there is no adoption question. If she wants the mixed result read otherwise (the gains on
  turning-point days and month-ends, the nearer 50% coverage), that is a new declaration, not a reading of this one.

## Reproduce

Published panel `4ddc3882…`; the commands are at the top of `scripts/direct_pairs_twin.py`.
