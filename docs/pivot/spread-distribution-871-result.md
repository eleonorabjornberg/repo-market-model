# #632 re-scored on the current distance columns (#871)

Development data only, not a verdict (scoring protocol v1, #640). Days 2018-06-29 to 2025-12-31; no day of 2026 is scored and no lockbox day is read (`docs/decisions/lockbox.md`; `require_unlocked` in the scoring scripts).
Serves H5, steps 1-2 (#632), as a re-score. It replaces no figure in place: [`spread-distribution-result.md`](spread-distribution-result.md) and `evidence/spread-distribution/` stay as scored, and this page and
`evidence/spread-distribution-871/` are new records beside them.

## Why

The tracked tables of #632 were scored on the version of `satiation_dist_roll` and `satiation_hinge_roll` built before #622 put them on the per-release H.4.1 rule. #847 isolated that as the cause of the drift in the rebuilt variants
(a) and (b); the model code (`ml.py`) is not the cause (`evidence/spread-632-drift/README.md`). On the published panel 1,592 of the 1,926 `satiation_dist_roll` cells and 491 of the 1,926 `satiation_hinge_roll` cells differ between the two builds
(mean absolute difference 0.0011 and 0.026; largest 0.019 and 1.1). This page re-runs #632's scoring exactly as its page and declaration describe, on the columns built today.

## What was run

Published panel `4ddc3882…` (`build` and `verify-panel` clean, digest unchanged), base commit `80b5ef0a` (the scoring commit; `metadata/spread_distribution_632.json`, the two candidate files and the judge declaration are as committed there),
`/opt/rmm-venv` (numpy 2.4.6, scikit-learn 1.9.1), one thread per process. The chain is the page's own (its "Reproduce" section and the docstring of `scripts/spread_distribution_632.py`): the scratch panels `AUG`, `AUG2`, `AUG2D`; for each of h = 1 to 5 the
benchmarks, `risk_date_severity.py run`, `pressure_track_q.py forecasts`, `announcement_dating_rescore.py run --arm both` for `risk_gbm` and `risk_gbm_base`, `satiation_587.py merge` and `reference`, `satiation_distance_598.py run`, `iorb_every_day_579.py run`,
then `every_day_conditioning_601.py cap`, `spread_distribution_632.py run` and `refs`; then `distribution`, the judge under both rules, `compare`, `ordinary` and `report`. The exact commands are in
[`evidence/spread-distribution-871/README.md`](evidence/spread-distribution-871/README.md). The tables of `evidence/spread-distribution-871/` are the files of the same names as `evidence/spread-distribution/`; `before_after.md`
(written by `before_after.py`) sets every headline cell beside its tracked value as `tracked → rebuilt`.

## Result

**No verdict of #632 changes, and no tier changes.** (a) still fails tiers 1, 3 and 5. (b) still meets tiers 3 and 5 together and fails tier 1 (pooled false alarms per onset on the weighted count 5.09, limit 2; 5.35 tracked). Every other row of the judge's
Table 1 keeps its verdict; the references move slightly (the comparator `risk_gbm+settle+h41+dist_roll` 1.27 to 1.17 weighted false alarms per onset, the figure #658 already found when it re-scored that row). Four readings of the page do move, all small:

- **(b) warns 19 of 26 onsets, not 20** (recall 0.731 [0.560, 0.889], tracked 0.769 [0.600, 0.923]). It loses 2020-03-04 (2020 recall 1 of 2, tracked 2 of 2), which it warned of before.
- **The onset recall difference of (b) against the `+tailcap75` row is no longer shown**: +0.038 [-0.048, +0.133], tracked +0.077 [0.000, +0.172]. Against the comparator it is +0.154 [+0.042, +0.286] (tracked +0.192 [+0.056, +0.356]) and against `persistence_logistic` +0.269 [+0.103, +0.455] (tracked +0.308 [+0.143, +0.484]), both still above zero.
- **(b)'s Brier difference against the comparator at h = 5 now includes zero** (+0.0070 [-0.0004, +0.0153]; tracked +0.0078 [+0.0006, +0.0161]); at h = 1 it is +0.0122 [+0.0026, +0.0231]. So the tracked sentence "Brier is better than both references and than `persistence_logistic`, each with an interval above zero" holds at h = 1 and, for the comparator, no longer at h = 5.
- **The ordinary-day figures of (a) and (b) are the rebuilt ones** that #786 already used: (b) AUROC 0.907 [0.855, 0.943] at h = 1 (tracked 0.903), pooled slope 0.44 (0.42), h = 1 slope 0.497 [0.303, 0.842] (0.463 [0.294, 0.883]); (a) 0.567 (0.563).

The distribution (step 1) moves by at most 0.03 bp of CRPS and keeps its reading: (b) beats as-of persistence at every lead (+0.411 [+0.109, +0.770] at h = 1) and is indistinguishable from the published distribution at every lead; (a) keeps intervals that include zero against persistence at
h = 1 to 3 (its h = 5 gain is +0.533 [+0.087, +0.997]).

### Step 1: CRPS (bp), tracked → rebuilt

| h | variant | days | CRPS (bp), variant | persistence CRPS | published CRPS | persistence minus variant [90%] | published minus variant [90%] |
|---|---|---|---|---|---|---|---|
| 1 | (a) | 404 | 2.848 → 2.860 | 3.088 | 3.063 | +0.240 [-0.127, +0.605] → +0.228 [-0.144, +0.595] | +0.215 [-0.006, +0.434] → +0.203 [-0.018, +0.422] |
| 1 | (b) | 1871 | 1.671 → 1.673 | 2.084 | 1.660 | +0.413 [+0.111, +0.771] → +0.411 [+0.109, +0.770] | -0.011 [-0.060, +0.040] → -0.013 [-0.062, +0.038] |
| 3 | (a) | 398 | 2.992 → 3.008 | 3.330 | 3.247 | +0.337 [-0.023, +0.700] → +0.322 [-0.032, +0.677] | +0.255 [-0.018, +0.566] → +0.239 [-0.020, +0.530] |
| 3 | (b) | 1869 | 1.886 → 1.889 | 2.442 | 1.855 | +0.556 [+0.238, +0.970] → +0.553 [+0.235, +0.967] | -0.030 [-0.098, +0.038] → -0.034 [-0.100, +0.033] |
| 5 | (a) | 397 | 3.108 → 3.086 | 3.618 | 3.305 | +0.510 [+0.037, +0.990] → +0.533 [+0.087, +0.997] | +0.197 [-0.108, +0.485] → +0.219 [-0.065, +0.492] |
| 5 | (b) | 1867 | 1.990 → 1.985 | 2.568 | 1.943 | +0.578 [+0.253, +1.012] → +0.582 [+0.259, +1.015] | -0.047 [-0.124, +0.027] → -0.043 [-0.119, +0.029] |

### The judge, weighted rule in force: Table 1, tracked → rebuilt

| model | onsets flagged | recall [90%] | false alarms per onset, flat / weighted | tier 3: worst flags per 252 days | calibrated regimes tested, h = 1 | tier 5 | pass |
|---|---|---|---|---|---|---|---|
| risk_gbm+settle+h41 | 14 of 26 | 0.538 [0.353, 0.710] | 2.15 flat / 1.44 weighted | 0.7 / 0.3 | 0 of 2 | no, yes | fail (tiers yes / no / no) |
| risk_gbm+settle+h41+dist_roll | 15 of 26 | 0.577 [0.400, 0.762] | 1.96 flat / 1.27 weighted → 1.81 flat / 1.17 weighted | 2.2 / 0.7 → 1.5 / 0.7 | 0 of 2 | no, yes | fail (tiers yes / no / no) |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 | 18 of 26 | 0.692 [0.522, 0.852] | 3.35 flat / 1.88 weighted | 0.7 / 0.3 | 0 of 2 | no, yes | fail (tiers yes / no / no) |
| spread_q_gbm+settle+h41+dist_roll | 15 of 26 | 0.577 [0.385, 0.758] | 3.00 flat / 2.23 weighted → 2.96 flat / 2.28 weighted | 2.9 / 2.7 → 3.1 / 3.4 | 0 of 2 | no, yes | fail (tiers no / no / no) |
| spread_q_gbm+two_part+settle+h41+dist_roll | 20 of 26 → 19 of 26 | 0.769 [0.600, 0.923] → 0.731 [0.560, 0.889] | 9.73 flat / 5.35 weighted → 9.38 flat / 5.09 weighted | 2.9 / 0.3 → 2.7 / 0.0 | 2 of 2 | yes, yes | fail (tiers no / yes / yes) |

### Against the references (+5 bp), tracked → rebuilt

| variant | reference | Brier difference h = 1 | Brier difference h = 5 | onset recall difference |
|---|---|---|---|---|
| (a) | `risk_gbm+settle+h41+dist_roll` | -0.0004 [-0.0026, +0.0020] → +0.0002 [-0.0022, +0.0027] | -0.0006 [-0.0024, +0.0013] → -0.0014 [-0.0032, +0.0003] | +0.000 [+0.000, +0.000] |
| (a) | `risk_gbm+every_day+gate+settle+h41+iorb+tailcap75` | -0.0005 [-0.0035, +0.0024] → -0.0003 [-0.0033, +0.0027] | -0.0014 [-0.0039, +0.0009] → -0.0013 [-0.0040, +0.0012] | -0.115 [-0.267, +0.000] |
| (b) | `risk_gbm+settle+h41+dist_roll` | +0.0117 [+0.0021, +0.0224] → +0.0122 [+0.0026, +0.0231] | +0.0078 [+0.0006, +0.0161] → +0.0070 [-0.0004, +0.0153] | +0.192 [+0.056, +0.356] → +0.154 [+0.042, +0.286] |
| (b) | `risk_gbm+every_day+gate+settle+h41+iorb+tailcap75` | +0.0115 [+0.0018, +0.0215] → +0.0118 [+0.0019, +0.0218] | +0.0071 [+0.0004, +0.0152] → +0.0072 [+0.0005, +0.0155] | +0.077 [+0.000, +0.172] → +0.038 [-0.048, +0.133] |
| (b) | `persistence_logistic` | +0.0109 [+0.0061, +0.0159] → +0.0112 [+0.0064, +0.0162] | +0.0126 [+0.0078, +0.0181] → +0.0126 [+0.0079, +0.0181] | +0.308 [+0.143, +0.484] → +0.269 [+0.103, +0.455] |
| (b) | `ngboost_laplace` | +0.0008 [-0.0028, +0.0047] → +0.0011 [-0.0026, +0.0049] | +0.0129 [+0.0057, +0.0216] → +0.0130 [+0.0058, +0.0216] | +0.115 [+0.000, +0.250] → +0.077 [+0.000, +0.171] |

### The ordinary days, tracked → rebuilt

| row | AUROC h = 1 | h = 3 | h = 5 | AUROC pooled h = 1 to 5 | slope, intercept pooled | slope [90%] h = 1 | intercept [90%] h = 1 |
|---|---|---|---|---|---|---|---|
| `risk_gbm+settle+h41+dist_roll` | 0.568 [0.534, 0.613] → 0.567 [0.533, 0.612] | 0.564 [0.533, 0.605] | 0.559 [0.531, 0.597] | 0.563 | 0.16, -0.71 | 0.163 [0.131, 1.262] → 0.165 [0.129, 0.209] | -0.694 [-1.204, 1.569] → -0.674 [-1.211, -0.250] |
| `risk_gbm+every_day+gate+settle+h41+iorb+tailcap75` | 0.563 [0.525, 0.608] | 0.566 [0.528, 0.611] | 0.583 [0.543, 0.631] | 0.575 | 0.12, -1.31 | 0.124 [-0.554, 0.212] → 0.124 [0.085, 0.168] | -1.247 [-2.364, -0.633] → -1.247 [-1.796, -0.824] |
| (a) | 0.563 [0.531, 0.603] → 0.567 [0.534, 0.609] | 0.559 [0.528, 0.599] → 0.564 [0.532, 0.603] | 0.559 [0.529, 0.597] → 0.558 [0.529, 0.597] | 0.561 → 0.563 | 0.11, -1.39 → 0.11, -1.36 | 0.113 [-0.363, 0.974] → 0.116 [0.080, 0.155] | -1.329 [-2.275, 1.698] → -1.299 [-1.925, -0.847] |
| (b) | 0.903 [0.847, 0.941] → 0.907 [0.855, 0.943] | 0.891 [0.850, 0.923] → 0.896 [0.856, 0.927] | 0.876 [0.826, 0.915] → 0.875 [0.825, 0.915] | 0.885 → 0.888 | 0.42, -0.86 → 0.44, -0.82 | 0.463 [0.294, 0.883] → 0.497 [0.303, 0.842] | -0.762 [-1.314, -0.114] → -0.707 [-1.287, -0.171] |
| `persistence_logistic` | 0.889 [0.840, 0.927] | 0.786 [0.690, 0.856] | 0.802 [0.705, 0.870] | 0.824 | 0.99, -0.40 | 1.046 [0.768, 1.426] | -0.188 [-1.076, 0.620] |
| `ngboost_laplace` | 0.921 [0.886, 0.948] | 0.886 [0.836, 0.925] | 0.855 [0.799, 0.904] | 0.883 | 0.41, -0.63 | 0.610 [0.490, 0.796] | -0.255 [-0.708, 0.142] |

The reliability intervals of the `+tailcap75` row, whose forecasts did not change, differ from the tracked ones in width, not in the point value (h = 1 slope 0.124 [-0.554, 0.212] tracked, 0.124 [0.085, 0.168] rebuilt): the interval code (`repo_model.reliability_regimes`, #725) changed after the page was scored, and the same holds for the comparator's and (a)'s intervals. This was not traced further.

The MAE and coverage, the onsets kept and lost, the recall by year and the calibration tables are in `evidence/spread-distribution-871/before_after.md`, and everything else in the files of that folder.

## Supersession

`docs/decisions/publish-rule.md` provides no mechanism that marks an old record as superseded, and `docs/pivot/spread-distribution-result.md` and `evidence/spread-distribution/` are research records (the page says it "writes nothing into `docs/runs/`"), so neither is edited here.
This page is the pointer from the new records to the old; whether the old page gets a note, and whether a rule is wanted for it, is Eleonora's (see the pull request). Nothing was written to `docs/runs/`: #632's scoring never produced a record there.

## The other pages that read `satiation_dist_roll`

#622 merged on 12 October 2026 (#647); a page scored after that reads the new columns.

| page | scored | reproduces or drifts | size |
|---|---|---|---|
| [`satiation-distance-result.md`](satiation-distance-result.md) (#598), row `risk_gbm+settle+h41+dist_roll` | before #622 | **drifts, slightly** | the row rebuilt here: 15 of 26 onsets as tracked; false alarms per onset 1.96 flat / 1.27 weighted → 1.81 / 1.17; ordinary AUROC h = 1 0.568 → 0.567. The page's own note and [`tailcap-floor-rebuild-658-result.md`](tailcap-floor-rebuild-658-result.md) already record this move. The hinge rows (b), (c) were not rebuilt |
| [`tailcap-floor-result.md`](tailcap-floor-result.md) (#610) | before #622 | **drifts, slightly; already re-scored in #658** | no verdict changes (page note); the comparator figure above |
| [`derived-features-result.md`](derived-features-result.md) (#631) | the model rows use #598's column on the older weekly lag (page text) | **drifts, slightly** | its control row is the comparator above. The two every-day rows rebuilt for #786 differ from Table M2 in two pooled slope cells: parent h = 3 0.91 against 0.98, lagpress h = 4 0.71 against 0.73 (`docs/research/log.md`); the rest of the page was not re-run |
| [`source-matrix-ordinary-days-result.md`](source-matrix-ordinary-days-result.md) (#629) | after #622 | **reproduces** (indicative) | its pooled AUROCs 0.15 (dist) and 0.80 (hinge). A lead-1 AUROC of each column against P(spread > +5 bp) over all scored days gives dist 0.139 → 0.135 and hinge 0.808 → 0.810 for the old and the current build; the screen was not re-run |
| [`off-risk-day-result.md`](off-risk-day-result.md) (#624), [`kinked-elasticity-result.md`](kinked-elasticity-result.md) (#626) | after #622 | **reproduces by construction** | both say the distance is built per H.4.1 release; not re-run |
| [`spread-distribution-protocol-result.md`](spread-distribution-protocol-result.md) (#634) | after #622 | **not re-run** | its input panel is rebuilt "with the chain below" in its own Reproduce section, on the current script; no figure was re-scored here |

None of these pages is re-published here. The drifting ones (#598, #610, #631) are marked questions in the pull request.

## Not checked, or for Eleonora

- Whether the old page and its evidence get a superseding note, and by what mechanism (`publish-rule.md` has none).
- Whether #598's hinge rows and #631's model rows are re-scored on the current columns: not done here.
- The per-regime reliability table added by #786 was built on the current columns. It was rebuilt here (`reliability_regimes_683.py spread632`, 2,000 replications) on this page's forecasts and its JSON is byte-identical to `evidence/reliability-regimes/spread-632.json`, so it reproduces; it is not copied into this folder.
- A development-data re-score: it gives no verdict under protocol v1, and the variants were built on these days, so a pass is not a confirmation (ruling on #567).
