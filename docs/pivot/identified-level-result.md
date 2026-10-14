# Identified estimators for the satiation level (#689, finding #671)

**Serves** H5's structural model and the model side of H7's nested forecast test (`docs/research/hypotheses/H7.md`, step 1: the
as-of estimator, starting from #597's kinked elasticity and #621's critique). The H7 estimator itself belongs to
`eleonorabjornberg/repo-market-liquidity` (#22 there) and is not duplicated here. **Development data, exploratory, no verdict** under
scoring protocol v1 (#640): nothing here is a pre-registered test, and a pass would not be a confirmation (ruling on #567).

A scratch measurement. It writes nothing into `docs/runs/`, publishes nothing, moves no published figure, scores no day of 2026 and reads no
day after 2025-12-31 (`docs/decisions/lockbox.md`; the scripts refuse a later panel). The published scarcity indicator and its 0.12 band are
unchanged and none of these rows joins the frozen shortlist of #567. Everything was declared in
[`metadata/identified_level_689.json`](../../metadata/identified_level_689.json) (commit `3deedc9c`) before the first forecast was fitted, and
`scripts/identified_level_689.py` refuses to run on a declaration that is not committed and unchanged.

## The problem (#671)

`satiation.fit_level` picks the kink of the structural model by least squares of the spread *level* on a hinge. The logistic the level feeds
is fitted to the +5 bp *label*, so the two objectives differ, and the least-squares surface has several minima. On these days the fitted
level moves by 0.0625 between consecutive refits at the largest and by 0.01 or more at nine of 80 refits (h = 1); it runs between 0.09 (2019 to 2021) and
0.185 (2021 and 2022) (the path below). #626's null result for the fitted level therefore describes the estimator as much as the kink.

## What was declared

| row | level of the kinked curve `e = exp(max(0, level - ratio) / 0.01)` |
|---|---|
| `structural_liquidity+h41` (control) | the unkinked curve, 0.12, reserves read per H.4.1 release |
| `structural_kinked_fitted` (reference, #626) | the least-squares kink of #587 |
| `structural_kinked_rolling` (reference, #626) | the rolling 10th percentile of the as-of ratios (#587) |
| **`structural_kinked_profile` (a)** | at each refit, the level on the 0.0025 grid of 0.08 to 0.20 that minimises **the ridge logistic's own objective**, fitted on the training pairs' +5 bp labels (the profile). The same level serves the +5 and +10 bp fits |
| **`structural_kinked_slow` (b)** | the same profile, but the level minimises (objective − its minimum) / pairs + 0.001 · ((level − previous level) / 0.01)², starting from 0.12 |

Two variants were tried (#567's count: +2 rows, both exploratory). The directive's optional (c), fitting the level on the pressure label
itself, is what (a) already profiles on and is not a separate row. Its alternative form of (b), a level per regime as of each decision, was not
scored: a regime label is a hindsight label (ruling on #515). **The penalty 0.001 is mine, written down once before any score and not tuned;
it is a judgement for Eleonora (below).** Every other term of the structural model, the refit cadence (every 21 rows, 61 rows minimum history) and
the scored days (2018-06-29 to 2025-12-31) are #626's, and its two kinked rows were re-run on the same panel so every pair is on one run.
The reserves leg is read per H.4.1 release (#541, #622).

## Result 1: the refit path and its stability

The level at each refit. h = 1 here; h = 2 to 5 are in [`evidence/identified-level-689/report.md`](evidence/identified-level-689/report.md).

| estimator | fitted refits | distinct levels | mean abs change | largest change | changes of 0.01 or more | sd | last level |
|---|---|---|---|---|---|---|---|
| least squares (`kinked_fitted`, #587) | 80 | 21 | 0.0037 | 0.0625 | 9 | 0.0249 | 0.145 |
| rolling (`kinked_rolling`) | 90 | 56 | 0.0014 | 0.0343 | 1 | 0.0226 | 0.123 |
| **profile (a)** | 80 | 18 | **0.0097** | 0.1000 | **20** | 0.0193 | 0.195 |
| **slow (b)** | 80 | 7 | 0.0002 | 0.0025 | 0 | 0.0047 | 0.1375 |

Range of the level by year, h = 1:

| estimator | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| least squares | 0.12 | 0.09 to 0.12 | 0.09 to 0.117 | 0.092 to 0.185 | 0.135 to 0.185 | 0.133 | 0.133 | 0.13 to 0.145 |
| rolling | 0.103 to 0.12 | 0.085 to 0.097 | 0.085 | 0.086 to 0.093 | 0.097 to 0.143 | 0.133 to 0.137 | 0.133 | 0.123 to 0.137 |
| profile (a) | 0.12 | 0.12 to 0.193 | 0.092 to 0.20 | 0.165 to 0.195 | 0.193 to 0.20 | 0.193 to 0.20 | 0.193 to 0.20 | 0.193 to 0.20 |
| slow (b) | 0.12 | 0.12 to 0.125 | 0.125 to 0.138 | 0.138 | 0.138 | 0.138 | 0.138 | 0.138 |

- **The profile does not make the level more stable; it moves more than the least-squares level** (20 changes of 0.01 or more against nine, h = 1; 16
  to 18 against three at h = 3 to 5, where the least-squares level is calmer). What changed is the objective, and the surface it picks from is still flat.
- **The slow form is stable by construction.** It moves at most one grid step (0.0025) per refit and has sat at 0.138 since 2021. That is the penalty
  holding it there, not evidence for 0.138: see Result 2.

## Result 2: the kink is not identified by the logistic's own objective

For (a), the interval of levels within 1.92 nats of the profile's minimum (the likelihood-ratio 95% region on one degree of freedom, applied to the
penalised objective), at every fitted refit:

| h | median width of the interval | refits whose interval reaches the grid maximum 0.20 | refits whose interval reaches the grid minimum 0.08 | profile level at the grid maximum | refits with several local minima | median excess of the fixed 0.12, nats |
|---|---|---|---|---|---|---|
| 1 | 0.0850 | 100% | 5% | 11% | 69% | 0.90 |
| 2 | 0.0825 | 100% | 0% | 16% | 100% | 1.25 |
| 3 | 0.0800 | 100% | 0% | 16% | 57% | 1.73 |
| 4 | 0.0825 | 100% | 0% | 9% | 51% | 1.11 |
| 5 | 0.0850 | 100% | 0% | 10% | 46% | 0.94 |

At every refit at every horizon the interval reaches 0.20, a level above the highest reserves ratio ever observed in these data (0.192, in 2021), where the
kinked curve is the unkinked exponential up to a constant that the logistic's standardisation removes. **The data never reject "no kink inside the
observed range"**, and from 2022 the profile sits there (0.193 to 0.20; 0.165 to 0.195 in 2021). The interval is also wide (about 0.08 of the 0.12 grid span), has several local
minima at 46% to 100% of refits, and the fixed 0.12 is within 2 nats of the minimum at a median refit (the interval's cut-off is 1.92). The surface that
made the least-squares level jump is therefore a property of the problem, not only of the least-squares objective: replacing the objective with the
logistic's own removes the jumps' *source* (the mismatch) but not the flatness.

## Result 3: ordinary-day forecasts

On days that are not scheduled risk dates, +5 bp, h = 1 to 5 (1,566 to 1,568 days, 87 above +5 bp), with 90% stationary-bootstrap intervals
(the judge's block length and replications). AUROC and Brier skill against the calendar climatology (1 − Brier / Brier of the climatology); the
reliability line `logit P(y = 1) = intercept + slope · logit(p)` (calibrated: 0 and 1).

| h | row | AUROC | Brier skill | intercept | slope |
|---|---|---|---|---|---|
| 1 | control `structural_liquidity+h41` | 0.883 [0.832, 0.922] | 0.137 [-0.011, 0.266] | -1.37 | 0.59 |
| 1 | `structural_kinked_fitted` | 0.876 [0.825, 0.917] | 0.110 [-0.053, 0.246] | -1.42 | 0.57 |
| 1 | `structural_kinked_rolling` | 0.882 [0.829, 0.921] | 0.172 [0.023, 0.286] | -0.86 | 0.74 |
| 1 | **`structural_kinked_profile`** | 0.881 [0.829, 0.921] | 0.142 [-0.004, 0.270] | -1.37 | 0.59 |
| 1 | **`structural_kinked_slow`** | 0.881 [0.829, 0.921] | 0.143 [-0.003, 0.271] | -1.36 | 0.59 |
| 3 | control | 0.801 [0.728, 0.860] | 0.024 [-0.150, 0.162] | -1.94 | 0.40 |
| 3 | `structural_kinked_fitted` | 0.800 [0.726, 0.859] | 0.028 [-0.144, 0.164] | -1.93 | 0.41 |
| 3 | `structural_kinked_rolling` | 0.785 [0.699, 0.847] | 0.053 [-0.111, 0.173] | -1.52 | 0.54 |
| 3 | **`structural_kinked_profile`** | 0.801 [0.727, 0.860] | 0.032 [-0.140, 0.168] | -1.93 | 0.41 |
| 3 | **`structural_kinked_slow`** | 0.800 [0.726, 0.859] | 0.031 [-0.141, 0.168] | -1.93 | 0.41 |
| 5 | control | 0.813 [0.726, 0.874] | 0.019 [-0.150, 0.177] | -1.78 | 0.45 |
| 5 | `structural_kinked_fitted` | 0.812 [0.725, 0.873] | 0.026 [-0.143, 0.183] | -1.78 | 0.45 |
| 5 | `structural_kinked_rolling` | 0.805 [0.714, 0.872] | 0.115 [0.025, 0.209] | -0.71 | 0.85 |
| 5 | **`structural_kinked_profile`** | 0.813 [0.725, 0.874] | 0.028 [-0.141, 0.185] | -1.78 | 0.45 |
| 5 | **`structural_kinked_slow`** | 0.812 [0.725, 0.873] | 0.027 [-0.142, 0.184] | -1.78 | 0.45 |

(h = 2 and 4 in the evidence page.) Paired differences, new row minus reference, on shared resamples:

| h | row | AUROC minus `kinked_fitted` | AUROC minus `kinked_rolling` | Brier skill minus `kinked_fitted` | Brier skill minus `kinked_rolling` |
|---|---|---|---|---|---|
| 1 | profile | +0.005 [0.000, 0.011] | -0.001 [-0.017, 0.017] | +0.032 [-0.025, 0.128] | -0.030 [-0.149, 0.112] |
| 1 | slow | +0.004 [0.000, 0.011] | -0.001 [-0.017, 0.017] | +0.033 [-0.025, 0.129] | -0.029 [-0.148, 0.113] |
| 2 | profile | +0.008 [0.001, 0.016] | +0.008 [-0.015, 0.031] | +0.059 [-0.023, 0.185] | -0.024 [-0.168, 0.136] |
| 3 | profile | +0.001 [-0.001, 0.004] | +0.016 [-0.024, 0.056] | +0.005 [0.000, 0.011] | -0.020 [-0.172, 0.151] |
| 4 | profile | +0.001 [-0.000, 0.004] | +0.007 [-0.015, 0.029] | +0.002 [0.000, 0.005] | -0.060 [-0.188, 0.053] |
| 5 | profile | +0.001 [-0.000, 0.002] | +0.008 [-0.018, 0.037] | +0.002 [0.000, 0.004] | -0.088 [-0.207, 0.024] |

- **Both new rows forecast almost what the control forecasts.** Their AUROC is within 0.002 and their Brier skill within 0.008 of the control's at every
  horizon (the profile level sits above the observed ratios from 2022, where the kink is inactive).
- **Against `structural_kinked_fitted`:** AUROC up by +0.005 (h = 1) and +0.008 (h = 2), intervals that just clear zero; nothing at h = 3 to 5. Brier skill
  up by 0.032 to 0.059 at h = 1 and 2 with intervals that include 0; at h = 3 to 5 the gains of 0.001 to 0.005 have intervals touching 0. That is the
  least-squares level's cost, removed; it is not skill over the control.
- **Against `structural_kinked_rolling`:** AUROC differences between −0.001 and +0.016 with intervals that include 0 at every horizon, and Brier skill
  differences of −0.02 to −0.09 with intervals that include 0 at every horizon. The rolling level keeps the best Brier skill and the reliability nearest
  to calibrated (slope 0.74 to 0.85 at h = 1, 4, 5), and the profile and slow rows cannot be separated from it. As #626 and #621 said, that level is a
  two-year reserves low, not an estimate of a kink.
- **Within regime** (Brier skill; reliability intercept and slope) only 2018-19 and 2025-26 have the 10 events a line needs. h = 1, 2018-19: control
  −0.021, profile −0.010, slow −0.010, fitted +0.020, rolling +0.140. h = 1, 2025-26: control, fitted, profile and slow all +0.210 (slope 1.21), rolling
  +0.326. At h = 2 to 5 in 2025-26 the control, fitted, profile and slow rows agree to 0.001; in 2018-19 the profile and slow rows sit with
  `kinked_fitted` (h = 3: −0.107 each) and a little above the control (−0.122).

## Result 4: the 2025 onsets

Five +5 bp onsets in 2025 (2025-09-15, 09-30, 10-15, 12-15, 12-26), all on scheduled risk dates. "Warned" here is only a description: the row's
forecast on the onset day is above the as-of 90th percentile of its own forecasts over the 252 scored days before it. It is not the judge's cut-off
rule, which is retired as a decision rule.

| h | control | `kinked_fitted` | `kinked_rolling` | profile (a) | slow (b) |
|---|---|---|---|---|---|
| 1 | 3 of 5 | 3 of 5 | 4 of 5 | 3 of 5 | 3 of 5 |
| 2 | 3 of 5 | 3 of 5 | 4 of 5 | 3 of 5 | 3 of 5 |
| 3 | 3 of 5 | 3 of 5 | 4 of 5 | 3 of 5 | 3 of 5 |
| 4 | 2 of 5 | 2 of 5 | 4 of 5 | 2 of 5 | 2 of 5 |
| 5 | 4 of 5 | 4 of 5 | 4 of 5 | 4 of 5 | 4 of 5 |

The profile and slow rows warn exactly the onsets the control warns, with the same forecasts (for example 0.072, 0.073, 0.059, 0.112, 0.078 at h = 1).
The rolling row warns one more and forecasts much higher on the onset days (0.74 and 0.95 on 2025-09-15 and 09-30). The full forecasts are in the evidence page.

## Is the demand-curve route closed or still open?

**For this form, closed on development evidence.** A kinked elasticity of the structural logistic whose level is estimated from the pressure label,
by the least-squares objective of #587 (#626), by the logistic's own profile (a), or by the profile held to move slowly (b), does not beat the unkinked
control on ordinary days at any horizon, and the profile never rejects "no kink" in the observed ratio range. The route is stalled by identification,
not by the objective's mismatch alone: a training sample that grows to 26 onsets does not place a scalar kink.

**Still open for H7's estimator in the liquidity repository.** Nothing here tests an estimator that does not use the +5 bp label (the direct estimate
of the distance to the kink, `eleonorabjornberg/repo-market-liquidity#22`), and nothing here is a verdict under the protocol. What this page gives
that work: a flat profile with its interval (the table in Result 2 is the benchmark a label-free estimator has to beat in width), a level path to
compare stability against (Result 1), and the ordinary-day AUROC and Brier skill the unkinked control already reaches (0.88 and 0.14 at h = 1).
A note to that queue (`eleonorabjornberg/repo-market-liquidity#24`) says so.

## Not checked, or for Eleonora

- **The penalty of (b), 0.001 nats per pair per squared percentage point.** My choice, declared before any score, not tuned. With a larger
  penalty the path would be flatter still; with a smaller one it would approach (a). A different value is a new declaration, not a re-run.
- **The profile is on the penalised objective** (summed log loss plus the ridge penalty) and its interval uses the 1.92-nat cut-off of an
  unpenalised likelihood: an approximation, stated in the module.
- **The profile is on the +5 bp label and applies to the +10 bp fit.** The +10 bp threshold has too few events to profile alone.
- **Within-regime lines exist only for 2018-19 and 2025-26** (10 events needed). 2020, 2021-23 and 2024 have too few ordinary-day events.
- **The "warned" rule is a description** I chose (as-of 90th percentile of 252 days); it is not the judge's rule and not a decision rule.
- **The profile fit is a ridge logistic with the structural model's fixed C = 1 and standardised columns;** a different penalty would give a different surface.
- No "Publish?" issue: nothing joins any published declaration and no published figure moves.

## Reproduce

Published panel `4ddc3882…` (`verify-panel` clean, unchanged); scratch panel `AUG5` as in [`kinked-elasticity-result.md`](kinked-elasticity-result.md)
(digest `52cb519e…`). `/opt/rmm-venv`, `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`. The commands are the module docstring of
`scripts/identified_level_689.py`; one horizon's `run` takes about four minutes and the `report` about two.

Evidence: [`evidence/identified-level-689/`](evidence/identified-level-689/) (`report.md` all five horizons; `report.json`; `refits.json` every refit's level,
interval and local minima, and the two panels' digests).
