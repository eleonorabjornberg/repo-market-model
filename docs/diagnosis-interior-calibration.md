# Why the published distribution's interior is miscalibrated, and the fix

Directive #247, stage 1 of pressure model v2. Finding #243 reported that the published distribution's 50% band
(its 25th to 75th percentile) holds the outcome on about a third of days. This page says what is wrong, why, and
what #244 should build. It is descriptive: it changes no model, no published record and nothing the live record
logs.

Every figure here is read from `docs/runs/v1_interior_diagnosis.json`, made by `scripts/interior_diagnosis.py`
on the published panel (`4ddc3882…8999`). The published distribution is #169's gradient-boosted trees with
nested conformal PID, walked exactly as the final test walks it. Its per-day CRPS at h = 1 reproduces the
published CRPS record and `final_test_near_blind.json` exactly, on all 2,042 days. At h = 2 to 5, its mean CRPS
over the opened window also matches the final test's cells exactly.

**Windows.** The diagnosis uses 2018-06-29 to 2025-12-31 (1,873 days at h = 1). January to September 2026 is
opened history. It prompted #243, so it is shown separately and nothing is concluded from it alone. No day after
2026-09-03 is read (`docs/decisions/lockbox.md`).

**How coverage is counted.** A quantile's coverage is the share of outcomes below it. An outcome exactly on the
quantile counts one half. A band's coverage is the share of outcomes strictly inside it, with an outcome on an
edge counting one half. Every spread in the panel is a whole basis point, carried with float noise
(17.000000000000014), so two values within 1e-9 bp are treated as the same print.

## In short

- **The interior is too narrow, mostly on the low side.** At h = 1 the outcome falls below q25 on 41% of days
  (target 25%) and below q50 on 59% (target 50%). Only q75 is close (73%, target 75%). The 50% band covers 32%.
  The 90% band is fine (89%).
- **The trees cause it, not PID and not rounding.** Conformal PID never moves the interior. Whole-basis-point
  outcomes explain under 2 points of an 18-point shortfall.
- **The trees fit their training data much better than they forecast.** In sample, their 50% band covers 54%.
  Out of sample it covers 32%. No setting of the trees closes that gap.
- **Recommendation: (i), per-level online quantile tracking of the interior levels**, on top of v1's unchanged
  trees and PID. Over 2018–2025 it brings the interior to 24 / 49 / 73% (targets 25 / 50 / 75) and the 50% band to
  49%. It keeps the 90% band at 89% and does not worsen CRPS: +0.013 bp in its favour, 90% interval −0.003 to
  +0.029.

## 1. Calibration at each level

At h = 1, half-tie coverage in percent:

| Window | Days | q05 | q25 | q50 | q75 | q95 | 50% band | 90% band |
|---|---|---|---|---|---|---|---|---|
| 2018–2025 | 1873 | 5.1 | **41.0** | **59.0** | 73.1 | 93.9 | **32.1** | 88.8 |
| 2026 (opened, seen) | 169 | 4.1 | 47.3 | 55.0 | 67.5 | 97.0 | 20.1 | 92.9 |

The PIT histogram, over 2018–2025 at h = 1, has the same six bins as the quantile grid. Ties are randomised, and
the expectation of that randomisation is shown:

| PIT bin | 0–5 | 5–25 | 25–50 | 50–75 | 75–95 | 95–100 |
|---|---|---|---|---|---|---|
| Target, % | 5 | 20 | 25 | 25 | 20 | 5 |
| Observed, % | 5.1 | **36.0** | 17.9 | 14.1 | 20.7 | 6.1 |

Too many outcomes land between q05 and q25, and too few in the middle two bins. The outer edges are right.

**By horizon** (2018–2025), the pattern holds at every horizon, and the 50% band narrows a little further with
horizon: 32.1, 32.1, 29.9, 30.1 and 28.7% at h = 1 to 5. q25 covers 41 to 43% throughout.

**By regime** (h = 1, 2018–2025):

| Regime | Days | q25 | q50 | q75 | 50% band | Miss below q25 | Miss above q75 |
|---|---|---|---|---|---|---|---|
| 2018–19 | 375 | 28.3 | 42.9 | 62.9 | 34.7 | 28.3 | 37.1 |
| 2020 | 251 | 26.3 | 48.2 | 61.0 | 34.7 | 26.3 | 39.0 |
| 2021–23 | 748 | **58.5** | **77.7** | 88.2 | 29.7 | **59.2** | 11.8 |
| 2024 | 250 | 30.0 | 48.0 | 64.8 | 34.8 | 30.0 | 35.2 |
| 2025–26 | 249 | 33.7 | 49.0 | 63.9 | 30.1 | 33.7 | 36.1 |

**By pressure-day type** (h = 1, 2018–2025):

| Day type | Days | q25 | q50 | q75 | 50% band |
|---|---|---|---|---|---|
| ordinary | 1595 | 42.0 | 60.6 | 75.9 | 33.8 |
| month-end | 158 | 35.8 | 51.9 | 62.0 | 26.3 |
| tax date | 89 | 37.6 | 49.4 | 55.1 | 17.4 |
| quarter-end | 31 | 25.8 | 38.7 | 41.9 | 16.1 |

The 50% band is short in every regime and every day type. On pressure days (month-end, tax date, quarter-end),
the outcome escapes mostly above the band.

## 2. Location or spread?

**Both, and the spread matters more.** Over 2018–2025 at h = 1:

- The outcome is below q50 on 58.9% of days and above it on 40.9%. The median gap is tiny (−0.01 bp), but the mean
  gap is +0.65 bp: many outcomes sit just under the median, and the ones above it are further away.
- The 50% band misses below on 41.3% of days and above on 26.9%: a 14.5-point asymmetry. Most of that comes from
  2021–23, when the spread sat flat at the floor and the band sat just above it. In every other regime, the
  band misses more often above than below.
- The band's mean width is 2.0 bp (median 1.5 bp). Even after re-centring it on the window's own median gap
  (which no forecast could know), the band would cover only 37.9%. Its half-widths would need to be about 1.4
  times wider to cover half the outcomes.

## 3. Over-fitting in the trees

The trees' own vector, before PID, at h = 1. "In sample" means each refit read on its own training pairs, pooled
over the 90 refits whose training ends by 2025-12-31.

| | q05 | q25 | q50 | q75 | q95 | 50% band | 90% band |
|---|---|---|---|---|---|---|---|
| In sample | 5.1 | 26.3 | 57.9 | 80.4 | 95.7 | **54.0** | 90.6 |
| Out of sample, 2018–2025 | 20.2 | 41.0 | 59.0 | 73.1 | 89.1 | **32.1** | 68.9 |

The gap is large: the trees are close to calibrated on the rows they were fitted on, and far from it on the next
day. Question 4 shows that tighter trees do not close the gap. It is therefore not mainly leaf-level
memorisation that regularisation would cure. The interior learned from the pooled training history is too
narrow for the day ahead, whatever the trees' complexity.

## 4. Sensitivity to the trees' settings

The features stay fixed, and one setting changes at a time. Each variant is refitted walk-forward on v1's fold
grid with the same refit cadence and the same nested PID. The figures are out of sample at h = 1 over 2018–2025.
The paired column is CRPS(v1) − CRPS(variant), so a positive value favours the variant; its interval is 90%.
scikit-learn's `HistGradientBoostingRegressor` has no row subsampling, so "subsampling" here means
`max_features`, the share of features each split may consider.

| Variant | CRPS | q25 | q50 | q75 | 50% band | 90% band | Paired vs v1 |
|---|---|---|---|---|---|---|---|
| v1 (min leaf 20, no depth limit, rate 0.1 × 100) | 1.659 | 41.0 | 59.0 | 73.1 | 32.1 | 88.8 | — |
| min samples per leaf 50 | 1.669 | 40.8 | 58.3 | 74.1 | 33.3 | 88.6 | −0.010 [−0.033, +0.013] |
| min samples per leaf 100 | 1.728 | 36.8 | 55.9 | 74.1 | 37.3 | 88.8 | −0.069 [−0.105, −0.036] |
| min samples per leaf 200 | 1.989 | 35.5 | 49.7 | 68.8 | 33.3 | 89.0 | −0.330 [−0.384, −0.278] |
| max depth 2 | 1.674 | 37.6 | 58.5 | 73.8 | 36.2 | 89.1 | −0.015 [−0.034, +0.003] |
| max depth 3 | 1.638 | 38.8 | 59.5 | 74.8 | 36.0 | 88.8 | +0.021 [+0.008, +0.034] |
| learning rate 0.05 × 100 trees | 1.664 | 40.8 | 60.6 | 76.2 | 35.4 | 88.5 | −0.005 [−0.015, +0.005] |
| learning rate 0.05 × 200 trees | 1.654 | 41.8 | 59.2 | 74.7 | 32.9 | 88.4 | +0.006 [−0.002, +0.013] |
| learning rate 0.02 × 250 trees | 1.667 | 43.1 | 60.7 | 75.8 | 32.7 | 88.4 | −0.008 [−0.020, +0.004] |
| features per split 0.8 | 1.660 | 38.5 | 57.4 | 72.5 | 34.0 | 88.8 | −0.001 [−0.012, +0.011] |
| features per split 0.5 | 1.667 | 38.1 | 56.1 | 71.6 | 33.5 | 88.4 | −0.007 [−0.021, +0.007] |

**No setting fixes the interior on its own.** The best 50% band is 37.3%, and q25 stays at 35% or more
everywhere. A maximum depth of 3 improves CRPS measurably but leaves the band at 36%. In-sample 50% coverage stays
between 53% and 56% for every variant, so the in-sample/out-of-sample gap is about 20 points under every setting.

## 5. The discreteness effect

Every outcome is a whole basis point. The trees' interior quantiles almost never are: 0.7% of them at h = 1. The
outcome lands on a 50% band edge on 1.5% of days. At h = 1, over 2018–2025, the 50% band covers:

| Closed (edges in) | Open (edges out) | Half-edge | Outcome jittered uniformly within ±0.5 bp |
|---|---|---|---|
| 32.9% | 31.3% | 32.1% | 31.4% |

Counting ties one way or the other moves the band by under 2 points, and randomising the outcome within its
basis point does not raise it. **The shortfall is real miscalibration, not a measurement artefact.**

## 6. Interaction with the outer-edge calibration

- **PID does not touch the interior.** It moved no interior quantile on any day at any horizon. The 50% band is
  32.1% before PID and 32.1% after. PID does what it is for: it lifts the trees' own 90% band from 68.9% to 88.8%.
- **The interior is miscalibrated before PID**, so PID neither causes it nor makes it worse.
- **The published vector never crosses.** q05 ≤ q25 ≤ q50 ≤ q75 ≤ q95 held on every issued day. The five
  separate tree fits do cross before they are sorted: on 853 of 1,873 days at h = 1, and on 835 days at each
  of h = 2 to 5. Sorting repairs that, as `src/repo_model/ml.py` intends.

## 7. Other model forms

Each candidate is scored on v1's walk at h = 1. The paired column is CRPS(v1) − CRPS(candidate), with a 90%
stationary-bootstrap interval (block length 2), so a positive value favours the candidate.

- **(i) Interior tracking.** v1's issued vector, with each of q25, q50 and q75 moved by its own online
  quantile tracker. The trackers learn only from labels observable at the day's anchor. The step is chosen by
  nested walk-forward selection over 0.01, 0.05, 0.1 and 0.2 bp, as PID's constants are.
- **(ii) Re-regularised trees.** The question 4 variant with the lowest CRPS, since none meets the bar: a maximum
  depth of 3.
- **(iii) Residual law.** v1's median, plus the empirical quantiles of its last 250 out-of-fold residuals
  observable at the anchor. **(iii, scaled)** first divides each residual by the trailing 20-day volatility of
  daily spread changes.
- **(iv)** is (ii) combined with (i).

| Candidate, 2018–2025 | CRPS | Paired vs v1 | q05 | q25 | q50 | q75 | q95 | 50% band | 90% band | 50% width | 90% width |
|---|---|---|---|---|---|---|---|---|---|---|---|
| v1 | 1.659 | — | 5.1 | 41.0 | 59.0 | 73.1 | 93.9 | 32.1 | 88.8 | 2.00 | 10.75 |
| **(i) interior tracking** | 1.647 | +0.013 [−0.003, +0.029] | 4.5 | 24.1 | 49.1 | 73.0 | 94.0 | 48.9 | 89.4 | 2.86 | 10.84 |
| (ii) max depth 3 | 1.638 | +0.021 [+0.008, +0.033] | 5.3 | 38.8 | 59.5 | 74.8 | 94.1 | 36.0 | 88.8 | 2.06 | 10.80 |
| (iii) residual law | 1.672 | −0.013 [−0.038, +0.013] | 6.5 | 25.3 | 49.0 | 74.2 | 92.6 | 48.9 | 86.2 | 2.56 | 8.88 |
| (iii) scaled | 1.830 | −0.171 [−0.279, −0.077] | 6.7 | 26.4 | 49.6 | 73.9 | 93.9 | 47.5 | 87.2 | 4.07 | 14.52 |
| (iv) = (ii) + (i) | 1.644 | +0.015 [−0.005, +0.035] | 4.5 | 22.2 | 48.7 | 76.1 | 94.5 | 53.8 | 90.0 | 2.82 | 10.94 |

Split by regime, (i)'s paired CRPS gain is positive in all five, and its interval excludes 0 in 2025–26
(+0.035 [+0.015, +0.056]). Split by day type, its gain is about zero on ordinary days, and clearly positive on
month-ends (+0.053), tax dates (+0.101) and quarter-ends (+0.207, 31 days). The full splits are in the record.

**2026, opened history, seen data, not evidence:**

| Candidate | CRPS | Paired vs v1 | q25 | q50 | q75 | 50% band | 90% band |
|---|---|---|---|---|---|---|---|
| v1 | 1.659 | — | 47.3 | 55.0 | 67.5 | 20.1 | 92.9 |
| (i) interior tracking | 1.614 | +0.045 [+0.021, +0.069] | 34.3 | 54.4 | 79.9 | 45.6 | 92.9 |
| (ii) max depth 3 | 1.645 | +0.014 [−0.033, +0.058] | 39.1 | 52.7 | 72.8 | 33.7 | 91.7 |
| (iii) residual law | 1.669 | −0.010 [−0.062, +0.042] | 29.0 | 56.8 | 85.2 | 56.2 | 94.7 |
| (iii) scaled | 1.728 | −0.069 [−0.128, −0.014] | 32.5 | 56.2 | 82.2 | 49.7 | 86.4 |
| (iv) | 1.644 | +0.015 [−0.030, +0.058] | 38.5 | 55.6 | 76.3 | 37.9 | 91.7 |

## The recommendation

The selection rule was declared in `scripts/interior_diagnosis.py` (`SELECTION_RULE`, `COMPLEXITY`,
`select_candidate`) and committed before any candidate was scored:

1. A candidate is eligible when its coverage at 25, 50 and 75% is each within 5 points of target, and its 90% band
   covers 87–93%, over 2018–2025 at h = 1.
2. The leader is the eligible candidate with the lowest CRPS.
3. A simpler eligible candidate is preferred to the leader when their paired CRPS difference has a 90% interval
   that includes 0. Simplicity ranks by the layers added to v1, then by fixing the trees before patching the
   output.

Three candidates are eligible: (i), (iii) scaled and (iv). (iv) has the lowest CRPS. (i) is simpler, one layer
against two, and (i) against (iv) is −0.002 bp, 90% interval −0.016 to +0.011, which includes 0.

**Recommended: (i), per-level online quantile tracking of the interior levels, on v1's unchanged trees and
nested PID.** (ii) would fix the cause, but it misses the bar: no setting of the trees brings the interior within 5
points on its own (question 4).

### What #244 should build

Pressure model v2 is v1's distribution, unchanged, with one online layer after nested PID:

- **Levels.** q25, q50 and q75 each carry an offset θ, starting at 0. q05 and q95 stay PID's.
- **Update.** Before a day's vector is issued, every earlier scored day whose label is observable at the day's
  anchor updates, in date order: θ_τ += step × (τ − below(y, q_τ)). Here `below` counts a tie as one half, and
  q_τ is the vector that was issued for that earlier day.
- **Step.** Each candidate step in 0.01, 0.05, 0.1 and 0.2 bp runs its own trackers. At the first scored day of
  each block of 21, the step with the least pooled CRPS over the observable days is chosen; 0.05 is used while
  there are none. This is the nested walk-forward selection PID already uses (#125).
- **Issue.** The offset vector, sorted (the rearrangement `ml.py` already uses), so that the quantiles never cross.

The reference implementation is `interior_tracking` in `scripts/interior_diagnosis.py`, which the record's
figures come from. It needs only the standard library: no new package.

The candidate's 2026 figures are seen data. #244's own 2026 gate and v2's live record are the tests.

## What this does not show

- It does not prove why the trees' out-of-sample interior is narrow beyond what is measured above. The gap
  survives every regularisation tried. Whether it comes from training on pooled regimes or from something else
  in the design is not established here.
- Candidates were scored at h = 1 only. At h = 2 to 5 the fault is the same (question 1), and #244 should check
  that the fix carries over.
- Interior tracking reacts to recent misses, so it lags a regime change. In 2026, q25 still covers 34%.
