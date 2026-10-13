# Forecast the spread, then apply the +5 bp threshold (#632)

A scratch measurement under the pressure-day judge. It writes nothing into `docs/runs/`, publishes nothing, moves no published figure, scores no day of 2026 and reads no day after
2025-12-31 (`docs/decisions/lockbox.md`; `require_unlocked`). No rule, threshold, onset definition or availability time changes. The model, its grid, its two structures and the references were
declared in `metadata/spread_distribution_632.json` and committed, with the model's code and tests, before any score. Step 1 (the distribution against its benchmarks,
`evidence/spread-distribution/distribution.md`) was committed before any judge score.

**The variants were built and scored on 2018-2025, so a pass here is not a confirmation (ruling of 11 October 2026 on #567). Nothing here joins a published declaration, so no "Publish?" question
arises. Whether either variant replaces a shortlist slot is Eleonora's decision, before the 2026 window opens.**

## Result in one paragraph

The model forecasts `spread_bps` at the scored day as a distribution (gradient-boosted quantiles at 13 levels, the hyperparameters of the risk-date classifier, none tuned) and reads P(spread > +5 bp) off the fitted law.
Variant (a) puts that on the risk dates only, as the passers do: it is the passer with a different estimator, and changes nothing the judge sees (no recall change against `risk_gbm+settle+h41+dist_roll`, Brier difference
indistinguishable from zero), and it fails tiers 1, 3 and 5. Variant (b), which adds a second spread-level model for the days that are not risk dates, ranks the ordinary days (AUROC 0.90 at h = 1) and warns 20 of 26 onsets
(recall 0.769 [0.600, 0.923]), against 15 and 18 for the two references, and it is the first row in these tables to meet tiers 3 and 5 together. It fails tier 1: its pooled false alarms are 5.35 per onset on the weighted count (limit 2). Its Brier score
is better than both references and than `persistence_logistic`, each with an interval above zero, but its ordinary-day reliability slope is 0.42 (1 is reliable), so its tier 3 and 5 pass is a pass on the mean, which
is what #616 says those tiers test; and most of its ordinary-day ranking is what `persistence_logistic` has already (AUROC 0.89). Variant (c) was not run: #629 and #631 had not merged.

## Step 1: the distribution, before any judge score

CRPS and mean pinball loss on the contract's five levels (0.05 to 0.95), in basis points, per scored day then averaged; the benchmarks are as-of persistence (the frozen CRPS test's side a, walked at each lead on the
panel cut at 2025-12-31) and the published distribution (`docs/runs/published_distribution_daily_h?.json`, days up to 2025-12-31 only). Differences are the benchmark's CRPS minus the variant's (positive: the variant is better), with 90% stationary-bootstrap
intervals. (a) has a law on the risk dates only and is compared on those days; (b) on every scored day on which its every-day inputs are public. Full tables, by regime and pressure-day type, are in `evidence/spread-distribution/distribution.md`.

| h | variant | days | CRPS: variant / persistence / published | persistence minus variant [90%] | published minus variant [90%] |
|---|---|---|---|---|---|
| 1 | (a) | 404 | 2.848 / 3.088 / 3.063 | +0.240 [-0.127, +0.605] | +0.215 [-0.006, +0.434] |
| 1 | (b) | 1871 | 1.671 / 2.084 / 1.660 | +0.413 [+0.111, +0.771] | -0.011 [-0.060, +0.040] |
| 3 | (a) | 398 | 2.992 / 3.330 / 3.247 | +0.337 [-0.023, +0.700] | +0.255 [-0.018, +0.566] |
| 3 | (b) | 1869 | 1.886 / 2.442 / 1.855 | +0.556 [+0.238, +0.970] | -0.030 [-0.098, +0.038] |
| 5 | (a) | 397 | 3.108 / 3.618 / 3.305 | +0.510 [+0.037, +0.990] | +0.197 [-0.108, +0.485] |
| 5 | (b) | 1867 | 1.990 / 2.568 / 1.943 | +0.578 [+0.253, +1.012] | -0.047 [-0.124, +0.027] |

**Reading.** (b) beats as-of persistence at every lead and is indistinguishable from the published distribution at every lead (the published distribution has the point lead at h = 2 to 5, by 0.03 to 0.05 bp, with
intervals that include zero). (a) is ahead of both on the risk dates by point estimates; its intervals include zero at h = 1 to 3 and exclude it against persistence at h = 4 and 5 (and against the published distribution at h = 4). Whatever the distribution's
quality, the question the judge asks is the exceedance of +5 bp, and the next sections are about that.

**H5 and its measures (added at review).** This directive serves H5, the SOFR − IORB spread distribution in bp, in #46's research plan (the step of H5 that this directive carries); it is exploration only, so development days give no verdict under protocol v1 (#640). The ruling of 12 October on #632 makes the spread forecast the primary result, scored on CRPS, pinball loss, MAE of the median and 50% / 90% coverage. CRPS and pinball are above. MAE of the median (the contract's level 0.5, in basis points) and the central coverage (the 0.25–0.75 interval for 50%, the 0.05–0.95 interval for 90%) are below, on the same days and against the same two benchmarks. The MAE difference is the benchmark's minus the variant's (positive: the variant is better). The coverage difference is the variant's hit rate minus the benchmark's; the nominal rates are 0.50 and 0.90. Intervals are 90% stationary-bootstrap. Leads 2 and 4, and every cell by regime and pressure-day type, are in `evidence/spread-distribution/distribution.md`.

| h | variant | days | MAE: variant / persistence / published | persistence minus variant [90%] | published minus variant [90%] | 50% coverage: variant / persistence / published | 90% coverage: variant / persistence / published | variant minus persistence, 50% ; 90% | variant minus published, 50% ; 90% |
|---|---|---|---|---|---|---|---|---|---|
| 1 | (a) | 404 | 3.72 / 3.62 / 4.02 | -0.103 [-0.520, +0.300] | +0.293 [-0.061, +0.661] | 0.39 / 0.44 / 0.24 | 0.77 / 0.82 / 0.84 | -0.052 [-0.198, +0.084] ; -0.054 [-0.146, +0.037] | +0.153 [+0.082, +0.223] ; -0.072 [-0.141, -0.010] |
| 1 | (b) | 1871 | 2.31 / 2.52 / 2.27 | +0.208 [-0.091, +0.613] | -0.044 [-0.123, +0.037] | 0.40 / 0.55 / 0.32 | 0.74 / 0.86 / 0.89 | -0.152 [-0.221, -0.087] ; -0.129 [-0.187, -0.079] | +0.077 [+0.045, +0.108] ; -0.151 [-0.199, -0.108] |
| 3 | (a) | 398 | 3.91 / 3.85 / 4.16 | -0.057 [-0.460, +0.335] | +0.255 [-0.142, +0.650] | 0.42 / 0.45 / 0.24 | 0.77 / 0.80 / 0.83 | -0.038 [-0.168, +0.075] ; -0.023 [-0.116, +0.068] | +0.178 [+0.126, +0.231] ; -0.053 [-0.128, +0.023] |
| 3 | (b) | 1869 | 2.66 / 2.97 / 2.47 | +0.312 [-0.012, +0.738] | -0.185 [-0.294, -0.075] | 0.38 / 0.50 / 0.30 | 0.73 / 0.83 / 0.88 | -0.114 [-0.180, -0.050] ; -0.101 [-0.159, -0.045] | +0.084 [+0.052, +0.117] ; -0.158 [-0.205, -0.115] |
| 5 | (a) | 397 | 4.05 / 4.23 / 4.34 | +0.183 [-0.283, +0.646] | +0.293 [-0.132, +0.708] | 0.41 / 0.41 / 0.22 | 0.74 / 0.78 / 0.82 | -0.003 [-0.128, +0.118] ; -0.033 [-0.126, +0.063] | +0.189 [+0.113, +0.262] ; -0.076 [-0.139, -0.018] |
| 5 | (b) | 1867 | 2.72 / 3.13 / 2.58 | +0.411 [+0.054, +0.845] | -0.139 [-0.253, -0.022] | 0.38 / 0.46 / 0.29 | 0.71 / 0.82 / 0.88 | -0.081 [-0.146, -0.024] ; -0.114 [-0.170, -0.062] | +0.097 [+0.061, +0.132] ; -0.172 [-0.221, -0.129] |

**Reading.** On the median, (b) is ahead of as-of persistence by point estimates at every lead, with an interval above zero at h = 4 and 5 (h = 1 to 3: the interval includes zero), and it is behind the published distribution at h = 2 to 5 (intervals below zero), indistinguishable at h = 1. (a) is indistinguishable from persistence on the median and ahead of the published distribution by point estimates, with intervals that include zero (h = 1 to 5 as tabulated and in the evidence file). Coverage is the weaker side: both variants cover less often than nominal (50% interval: 0.35 to 0.42 against 0.50; 90% interval: 0.71 to 0.77 against 0.90), (b) covers less often than as-of persistence at both levels (every interval below zero), and less often than the published distribution at 90%. Against the published distribution (b) covers more often at 50%, where the published distribution is too narrow (0.29 to 0.32), and less often at 90%. So the CRPS result above, (b) level with the published distribution and ahead of persistence, comes with intervals that are too narrow at both levels.

## The judge: tiers 1, 3 and 5, pooled and per lead

Table 1. The judge's tiers at +5 bp, h = 1 to 5, weighted rule in force (the flat rule is `evidence/spread-distribution/judge-unweighted.md`, and in the report). Limit on pooled false alarms per onset: 2.

| row | onsets flagged | recall [90%] | pooled false alarms per onset, flat / weighted | tier 1 | tier 3 | tier 5 | passes |
|---|---|---|---|---|---|---|---|
| `risk_gbm+settle+h41` (control) | 14 of 26 | 0.538 [0.353, 0.710] | 2.15 / 1.44 | yes | no | no | no |
| `risk_gbm+settle+h41+dist_roll` | 15 of 26 | 0.577 [0.400, 0.762] | 1.96 / 1.27 | yes | no | no | no |
| `risk_gbm+every_day+gate+settle+h41+iorb+tailcap75` | 18 of 26 | 0.692 [0.522, 0.852] | 3.35 / 1.88 | yes | no | no | no |
| (a) `spread_q_gbm+settle+h41+dist_roll` | 15 of 26 | 0.577 [0.385, 0.758] | 3.00 / 2.23 | no | no | no | no |
| (b) `spread_q_gbm+two_part+settle+h41+dist_roll` | 20 of 26 | 0.769 [0.600, 0.923] | 9.73 / 5.35 | no | **yes** | **yes** | no |

Under the flat rule (b) flags 19 of 26 (0.731 [0.560, 0.889]) with 6.85 pooled false alarms per onset (3.30 weighted), tier 1 no, tiers 3 and 5 yes. Tier 1 at each lead alone, weighted, for (b): lead 1 2.80 [1.64, 4.70]
weighted false alarms per onset (recall 0.577), lead 2 2.15, lead 3 1.80 (pass), lead 4 2.14, lead 5 2.00 (pass); the per-lead tables of every row are in `evidence/spread-distribution/report.md` ("Tier 1 at each lead alone").
(a) and (b) are the only two rows whose tier 1 fails among these five; `+tailcap75` meets tier 1 on the weighted count only (the row of #601).

The tier 1 verdict of (b) is therefore the cost: it flags the ordinary days that the passers leave at 0, and its false alarms are 5 per onset where the limit is 2. No gate, floor or cap was added (the directive's variants do not have one).

## Against the two references (+5 bp, paired, 90% intervals)

Brier difference, reference minus row (positive: the row is better), pooled over days; recall difference, row minus reference, any horizon. Full tables by regime and pressure-day type for each reference are in `evidence/spread-distribution/report.md`.

| variant | reference | Brier difference h = 1 | Brier difference h = 5 | onset recall difference |
|---|---|---|---|---|
| (a) | `risk_gbm+settle+h41+dist_roll` | -0.0004 [-0.0026, +0.0020] | -0.0006 [-0.0024, +0.0013] | 0.000 [0.000, 0.000] |
| (a) | `+tailcap75` row | -0.0005 [-0.0035, +0.0024] | -0.0014 [-0.0039, +0.0009] | -0.115 [-0.267, 0.000] |
| (b) | `risk_gbm+settle+h41+dist_roll` | +0.0117 [+0.0021, +0.0224] | +0.0078 [+0.0006, +0.0161] | +0.192 [+0.056, +0.356] |
| (b) | `+tailcap75` row | +0.0115 [+0.0018, +0.0215] | +0.0071 [+0.0004, +0.0152] | +0.077 [0.000, +0.172] |
| (b) | `persistence_logistic` | +0.0109 [+0.0061, +0.0159] | +0.0126 [+0.0078, +0.0181] | +0.308 [+0.143, +0.484] |
| (b) | `ngboost_laplace` | +0.0008 [-0.0028, +0.0047] | +0.0129 [+0.0057, +0.0216] | +0.115 [0.000, +0.250] |

By regime, (b) against `risk_gbm+settle+h41+dist_roll` at h = 1: better in 2018-19 (+0.0513 [+0.0112, +0.0948]) and 2025-26 (+0.0254 [+0.0013, +0.0562]), worse in 2020 (-0.0097 [-0.0184, -0.0027]) and in 2021-23 (-0.0004
[-0.0006, -0.0002]), indistinguishable in 2024. By pressure-day type the gain is on the ordinary days (+0.0139 [+0.0034, +0.0263]); the risk-date types are indistinguishable. The gain is in two regimes and the loss in two; a pooled figure alone is not the result.

## Onsets kept and lost, by date

Any horizon 1 to 5, lead at least 1, weighted rule (the lists for every pair are in `evidence/spread-distribution/report.md`).

| variant | against | warned by both | gained | lost |
|---|---|---|---|---|
| (a) | `risk_gbm+settle+h41+dist_roll` | 15 of 26 | none | none |
| (a) | `+tailcap75` row | 14 of 26 | 2025-10-15 | 2019-05-28, 2019-06-25, 2019-08-13, 2020-03-04 |
| (b) | `risk_gbm+settle+h41+dist_roll` | 15 of 26 | 2019-05-28, 2019-06-25, 2019-08-13, 2020-03-04, 2020-03-12 | none |
| (b) | `+tailcap75` row | 18 of 26 | 2020-03-12, 2025-10-15 | none |

Recall by calendar year, any horizon (onsets warned of onsets):

| row | 2018 | 2019 | 2020 | 2024 | 2025 |
|---|---|---|---|---|---|
| `risk_gbm+settle+h41+dist_roll` | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| `+tailcap75` row | 0 of 4 | 13 of 13 | 1 of 2 | 0 of 2 | 4 of 5 |
| (a) | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |
| (b) | 0 of 4 | 13 of 13 | 2 of 2 | 0 of 2 | 5 of 5 |

The six onsets neither (b) nor the references warn are the four of 2018 and the two of 2024.

## The ordinary days: AUROC and reliability (#616)

Days whose pressure-day type is ordinary (1,603 days, 101 of them pressure days, at h = 1). AUROC of the +5 bp probability with a 90% stationary-bootstrap interval; the reliability slope and intercept are those of the logistic fit of the outcome on
logit(p) (1 and 0 for a reliable forecast). All rows are in `evidence/spread-distribution/ordinary.json` and the report.

| row | AUROC h = 1 | h = 3 | h = 5 | AUROC pooled h = 1 to 5 | slope, intercept pooled | slope [90%] h = 1 | intercept [90%] h = 1 |
|---|---|---|---|---|---|---|---|
| `risk_gbm+settle+h41+dist_roll` | 0.568 [0.534, 0.613] | 0.564 [0.533, 0.605] | 0.559 [0.531, 0.597] | 0.563 | 0.16, -0.71 | 0.163 [0.131, 1.262] | -0.694 [-1.204, 1.569] |
| `+tailcap75` row | 0.563 [0.525, 0.608] | 0.566 [0.528, 0.611] | 0.583 [0.543, 0.631] | 0.575 | 0.12, -1.31 | 0.124 [-0.554, 0.212] | -1.247 [-2.364, -0.633] |
| (a) | 0.563 [0.531, 0.603] | 0.559 [0.528, 0.599] | 0.559 [0.529, 0.597] | 0.561 | 0.11, -1.39 | 0.113 [-0.363, 0.974] | -1.329 [-2.275, 1.698] |
| (b) | 0.903 [0.847, 0.941] | 0.891 [0.850, 0.923] | 0.876 [0.826, 0.915] | 0.885 | 0.42, -0.86 | 0.463 [0.294, 0.883] | -0.762 [-1.314, -0.114] |
| `persistence_logistic` | 0.889 [0.840, 0.927] | 0.786 [0.690, 0.856] | 0.802 [0.705, 0.870] | 0.824 | 0.99, -0.40 | 1.046 [0.768, 1.426] | -0.188 [-1.076, 0.620] |
| `ngboost_laplace` | 0.921 [0.886, 0.948] | 0.886 [0.836, 0.925] | 0.855 [0.799, 0.904] | 0.883 | 0.41, -0.63 | 0.610 [0.490, 0.796] | -0.255 [-0.708, 0.142] |

**Reading.** (a) ranks only the ordinary days that are risk dates (those settling a coupon) and is exactly 0 on the rest, so its AUROC is the references'. (b) ranks them: AUROC 0.90 at h = 1, 0.88 at h = 5, against 0.56
for the references. That is the gap the directive asked about, and the spread-level model is what closes it. The same figure is `persistence_logistic`'s at h = 1 (0.89, interval overlapping) and above it at h = 3 to 5, so a large part of what is
gained is the information in the latest spread that a persistence model already uses; this measurement does not separate the two. The reliability slope of (b) is 0.42 pooled (0.46 [0.29, 0.88] at h = 1): the forecasts are more spread out than the outcomes support,
and the intercept is negative. The row that passes tiers 3 and 5 does so on the mean (#616); a test on the curve's shape would not pass it, and `persistence_logistic` (slope 0.99) is the better calibrated of the two.

## Calibration of (b) (predicted against realised, +5 bp, pooled over h = 1 to 5)

| cell | days | predicted | realised |
|---|---|---|---|
| all | 9,355 | 0.0701 | 0.0741 |
| ordinary days | 8,009 | 0.0615 | 0.0627 |
| 2018-19 | 1,865 | 0.2168 | 0.2697 |
| 2020 | 1,255 | 0.0569 | 0.0159 |
| 2021-23 | 3,740 | 0.0084 | 0.0000 |
| 2024 | 1,250 | 0.0203 | 0.0200 |
| 2025-26 | 1,245 | 0.0992 | 0.1165 |

It under-forecasts the two stress regimes and over-forecasts 2020 and 2021-23 (a regime with no pressure day, never calibration-tested because it has fewer than 20). It passes tier 3 and tier 5 because the regimes
that are tested (those with enough pressure days) cover zero on the mean, not because the shape is right.

## Not checked, or for Eleonora

- **A pass is not a confirmation (ruling on #567).** Both variants were declared after reading 2018-2025 and scored on it; the 26 onsets are 17 in 2018-19, 2 in 2020, 2 in 2024 and 5 in 2025, and a difference of one or two onsets is inside every interval.
  (b) is not a candidate for the 2026 window by anything in this measurement: it fails tier 1 by a wide margin. Whether it, or any variant, replaces a shortlist slot is her decision.
- **Variant (c) was not run.** #629 and #631 had not merged when the declaration was made (both open).
- **No gate, floor or cap on (b).** The directive asked for the spread-level model, not a false-alarm control. Whether to put one on it (the gate of #532, or the cap of #601) is a further variant, outside this directive's three.
- **The directive's `+tailcap75`** names no parent row. It is read as the only row of that suffix in the tree, `risk_gbm+every_day+gate+settle+h41+iorb+tailcap75` (#601), the row that meets tier 1 on the weighted count. If another row was meant, the pairing is to be re-run.
- **Step 1 at each lead** uses the frozen CRPS test's persistence walked at h = 1 to 5 and the published daily forecasts as committed; the benchmark's pinball loss is on the days each variant has a law, so (a)'s benchmark figures are on 404 risk dates and (b)'s on 1,871 days.
  The CRPS is on the contract's five levels, a coarse grid; (b)'s CRPS on its own 13 levels is reported beside it and is lower (1.59 at h = 1).
- **Intervals for AUROC and the reliability slope** are 90% stationary-bootstrap intervals (block length 10, 2000 replications); where the forecast is constant on a resample the interval is not reported.
- **Reading of the law between the grid's outer quantiles and 0 and 1** is the linear continuation of `ml.exceedance_from_quantiles`; no other smoother (the skew-t of #379) was tried.
- No day of 2026 is scored; the published records, the judge and its declaration are unchanged.

## Reproduce

Published panel `4ddc3882…` (`verify-panel` clean, unchanged); scratch panels `AUG`, `AUG2` and `AUG2D` as in [`satiation-distance-result.md`](satiation-distance-result.md). `/opt/rmm-venv`
(numpy 2.4.6, scikit-learn 1.9.1), `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`. The references' forecasts are those of `satiation_distance_598.py run`, `iorb_every_day_579.py run` and
`every_day_conditioning_601.py cap` at h = 1 to 5; the commands of this measurement are the module docstring of `scripts/spread_distribution_632.py` (`run`, `refs`, `distribution`, the judge under both rules, `compare`, `ordinary`, `report`).

Evidence: [`evidence/spread-distribution/`](evidence/spread-distribution/) (`distribution.md` and `.json`, with the MAE of the median and the 50% / 90% coverage; `report.md`; `compare.json` and `compare.md`; `judge-weighted.md` and `judge-unweighted.md`; `ordinary.json`).
