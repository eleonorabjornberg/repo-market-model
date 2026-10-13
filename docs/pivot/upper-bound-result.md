# Upper-bound study: how much signal is in the data we hold, for the spread and for ordinary-day pressure (#635, H2 step 3)

A development measurement. It is never a claim and never a verdict for a hypothesis (scoring protocol v1, `docs/decisions/scoring-protocol.md` §1 and §9, "H2": a go/no-go for effort).
It writes nothing into `docs/runs/`, publishes nothing, moves no published figure, reads no day after 2025-12-31 and scores no day of a locked tier (`docs/decisions/lockbox.md`; `require_unlocked`).
Every choice, the reading rule included, is in `metadata/upper_bound_635.json`, committed before any number was computed; the script refuses an uncommitted declaration. The scoring sections of the
directive are superseded by protocol v1 wherever they differ (ruling of 12 October 2026 on #635): the metric is the 23-level grid CRPS averaged over leads 1 to 5, the benchmarks are B1 (as-of persistence) and B2
(calendar climatology), the interval is the stationary bootstrap (mean block 10, one-sided 95% test, 10,000 draws on the primary cells). **Nothing here joins a published declaration, so no "Publish?" question arises.**

Hypothesis and step: H2, step 3 (`docs/research/hypotheses/H2.md`). The matrices (#629) and the derived features (#631) have merged and the features are among the inputs.

## Verdict, under the reading rule committed first

**Spread (the primary target): partly reached. Ordinary-day +5 bp indicator: partly reached.** The one-line verdict is the primary target's: **partly reached**. Read the next section before using it: both lines come with a caveat about what the rule can and cannot see.

| | ceiling (in-sample, generous) | reachable (walk-forward, reads public data only) | rule |
|---|---|---|---|
| spread, CRPS skill against B1, ordinary days (best model of the two) | +0.781 [+0.747, +0.815] (gbm) | +0.192 [+0.007, +0.352] (gbm) | barely above if the lower end is at or below 0 |
| ordinary-day +5 bp, AUROC averaged over leads 1 to 5 (best model of the two) | 1.000 [1.000, 1.000] (gbm) | 0.905 [0.851, 0.938] (gbm) | barely above if under 0.6 |

## What the verdict does and does not say

1. **The in-sample gradient-boosted ceiling memorises the data; it is not a measure of information.** Its in-sample CRPS on ordinary days is 0.43 bp against B1's 1.97, and its ordinary-day AUROC is exactly 1.000 at every lead.
   A tree ensemble with 400 rounds and 31 leaves fits 1,873 days of 159 inputs almost without error. So the rule as written ("the ceiling is barely above the benchmark" means an AUROC under 0.6, or a skill interval that covers 0) cannot return "data problem"
   for a flexible model, whatever the inputs hold. The in-sample **regularised linear** ceiling is the more informative one: skill against B1 on ordinary days +0.165 [+0.007, +0.294] on all in-sample days (+0.138 [-0.061, +0.295] on the walk-forward days),
   AUROC 0.992 (0.996 on the walk-forward days). **The ceiling is therefore an upper bound on a bound; it cannot tell a data problem from a model problem here.** The reachable line is the number that carries information.
   **Marked question 1 for Eleonora, not settled in code:** should the ceiling be a cross-fitted one (blocked folds, scored on rows the fit did not see, but not walk-forward) so that it can be low? That is a change to the committed reading, so it is hers; it was not run.
2. **The AUROC line of 0.6 is far below the benchmark's own AUROC.** The persistence-logistic model, which reads the last public spread alone, scores 0.890 [0.821, 0.937] on the walk-forward ordinary days (0.925 in-sample). A model that adds nothing to persistence is "clearly above" 0.6.
   Against that benchmark the reachable models are not ahead: AUROC minus persistence-logistic is +0.015 [-0.017, +0.058] (gbm) and -0.020 [-0.078, +0.044] (ridge); the Brier skill against persistence-logistic is -0.192 [-0.374, +0.034] (gbm) and -0.122 [-0.309, +0.059] (ridge);
   against climatology it is +0.037 [-0.139, +0.265] (gbm), while persistence-logistic alone is +0.192 [+0.131, +0.276]. Read against persistence-logistic, which is what CLAUDE.md names as the pressure-probability benchmark, the indicator would be "barely above".
   The pre-registered line is the directive's (an AUROC under 0.6) and is applied as written; the other reading is reported, not substituted. **Marked question 2 for Eleonora:** which benchmark line the rule should use for the indicator.
3. **The pressure days on ordinary days are mostly one regime.** Of the 82 ordinary pressure days, #631 found 62 in 2018-19, 15 in 2025-26, 5 in 2020 and 2024 and none in 2021-23. A pooled AUROC measures "which regime" as much as timing. The regime split below shows it: the reachable gbm's AUROC is 0.46 in 2018-19 (below a coin) and 0.87 in 2025-26.
4. **The reachable spread result is marginal and uneven.** The interval of the primary cell clears 0 by 0.007; the one-sided 95% lower bound of the mean CRPS difference is +0.010 bp, and the Diebold-Mariano p is 0.073 (the bootstrap p is 0.041).
   By regime, the reachable gbm is ahead of B1 in 2018-19, 2024 and 2025-26 and **behind it in 2021-23** (-0.318 [-0.529, -0.133] on ordinary days), the regime where phase 2's gbm also lost to persistence. On quarter-ends and tax dates it is level or behind. The regularised linear fit is unstable out of sample (below).

## The spread

Grid CRPS in basis points (twice the mean pinball loss over the 23 levels of protocol v1), averaged over leads 1 to 5 per decision day, on the 1,598 decision days of the walk-forward window (the first is 2019-07-31, the first block with the 250 training rows the declaration asks for).
"Ordinary" scores a decision day on those of its five targets that are ordinary days (a decision day with no ordinary target is dropped, none is on this window). Skill = (benchmark mean - candidate mean) / benchmark mean, positive favouring the candidate; the interval is the 5th to 95th percentile of the paired skill draws.
The full tables, with the one-sided 95% lower bounds, the bootstrap and Diebold-Mariano p-values, MAE of the median, the splits and every lead, are in `docs/pivot/evidence/upper-bound/tables.md`; every cell is in `score.json` there.

| walk-forward days, ordinary targets | B1 mean | candidate mean | skill against B1 [90%] | skill against B2 [90%] |
|---|---|---|---|---|
| reachable gbm | 1.718 | 1.388 | +0.192 [+0.007, +0.352] | +0.290 [+0.227, +0.351] |
| reachable ridge | 1.718 | 3.804 | -1.213 [-2.114, -0.620] | -0.947 [-1.421, -0.557] |
| ceiling gbm (in-sample) | 1.718 | 0.372 | +0.784 [+0.740, +0.823] | +0.810 [+0.779, +0.838] |
| ceiling ridge (in-sample) | 1.718 | 1.481 | +0.138 [-0.061, +0.295] | +0.242 [+0.131, +0.334] |

* **Where the reachable gbm beats persistence, and where it loses** (ordinary targets, against B1, 2000 draws): 2018-19 +0.598 [+0.053, +0.763]; 2020 +0.056 [-0.184, +0.237]; **2021-23 -0.318 [-0.529, -0.133]**; 2024 +0.272 [+0.162, +0.365]; 2025-26 +0.220 [+0.081, +0.339].
  By day type (all targets): ordinary +0.197 [+0.011, +0.357]; month-end +0.097 [-0.120, +0.250]; quarter-end -0.051 [-0.417, +0.147]; tax date -0.073 [-0.342, +0.019]. On risk-date targets it is level with B1 (+0.007 [-0.095, +0.097]). It beats B2 everywhere in the pooled cells.
* **By lead** (ordinary targets, against B1): +0.256 [+0.008, +0.445] at lead 1, +0.263 [+0.051, +0.440] at lead 2, +0.278 [+0.087, +0.435] at lead 3, +0.253 [+0.065, +0.411] at lead 4, +0.237 [+0.051, +0.388] at lead 5.
* **MAE of the median** (ordinary targets): the reachable gbm 1.95 bp against B1's 2.15 (skill +0.092 [-0.093, +0.256]), so the gain is in the width and tails of the distribution, not in the median.
* **The gap between the lines, on the same days:** the in-sample gbm is +0.732 [+0.706, +0.758] better than the reachable gbm (skill relative to the reachable line); the in-sample ridge +0.611 [+0.505, +0.699] better than the reachable ridge. These gaps are mostly the memorisation of point 1.
* **The regularised linear fit blows up out of sample.** Its reachable CRPS is 3.80 bp against B1's 1.72. The cause is traceable: at lead 1, in April 2020 its median reads +69 to +137 bp on six days (and -93 bp on 2020-04-01) when the spread was -7 to -9 bp (inputs far outside the training range, clipped at five standard deviations but still large against 250 to 500 training rows),
  and on 2019-09-17 it reads a 20 bp median against an observed 315 bp. It is stable in 2024 and 2025-26 (-0.125 [-0.416, +0.032] and +0.101 [-0.020, +0.198]). Read this as a property of the declared design (about 214 columns, a fixed penalty, no selection), not of linear models in general.
* **The ceiling window** (all 1,868 in-sample decision days, ordinary targets): gbm +0.781 [+0.747, +0.815], ridge +0.165 [+0.007, +0.294] against B1.

## The +5 bp indicator on ordinary days

1,469 ordinary scored days, 82 of them pressure days (140 pressure days in all). Trained on ordinary days only. AUROC and Brier skill are averaged over leads 1 to 5 with the stationary bootstrap (mean block 10, 1,000 draws) over the ordinary days in date order, one draw shared by every lead and model.
The walk-forward window is the reachable fits' served days: 1,271 ordinary days with 51 pressure days at leads 1 and 2, 1,254 and 37 at leads 3 to 5.

| walk-forward ordinary days | AUROC [90%] | AUROC minus persistence-logistic [90%] | Brier | Brier skill against climatology [90%] | Brier skill against persistence-logistic [90%] |
|---|---|---|---|---|---|
| reachable gbm | 0.905 [0.851, 0.938] | +0.015 [-0.017, +0.058] | 0.0355 | +0.037 [-0.139, +0.265] | -0.192 [-0.374, +0.034] |
| reachable ridge (logistic) | 0.870 [0.805, 0.914] | -0.020 [-0.078, +0.044] | 0.0335 | +0.091 [-0.067, +0.277] | -0.122 [-0.309, +0.059] |
| persistence-logistic | 0.890 [0.821, 0.937] | | 0.0299 | +0.192 [+0.131, +0.276] | |
| climatology (training rate) | | | 0.0370 | | |
| ceiling gbm (in-sample) | 1.000 [1.000, 1.000] | +0.063 [+0.039, +0.110] | 0.0000 | | |
| ceiling ridge (in-sample) | 0.996 [0.992, 0.998] | +0.059 [+0.036, +0.104] | 0.0089 | +0.726 [+0.637, +0.781] | +0.682 [+0.603, +0.736] |

By regime the reachable gbm's AUROC is 0.463 [0.349, 0.633] in 2018-19 and 0.871 [0.777, 0.939] in 2025-26 (persistence-logistic: 0.655 and 0.885); the other regimes have under five pressure days at some leads or none, and AUROC is not formed there (`tables.md`).
By the as-of scarcity state, the reachable gbm scores 0.587 [0.469, 0.691] inside the scarce state, where 49 of the 51 pressure days are (persistence-logistic: 0.604). So the ranking the pooled figure shows is mostly "scarce state or not", which the last public spread already carries.

## Reading it for H2

* **Not a data problem, under the rule as written** (the reachable line is clearly above the benchmark on the spread: the interval, by a hair, and the indicator's AUROC well above 0.6). Under the H2 outcome rule, effort does not move to new data (H3, H4) on this evidence alone.
* **The gap is not interpretable from this study** (points 1 and 2): the in-sample gbm ceiling is inflated by memorisation, and the AUROC line of 0.6 is passed by persistence alone. What the study does show is the reachable line: a gradient-boosted spread law on the inputs held is ahead of as-of persistence on ordinary days by 19% of CRPS
  (marginal, behind in 2021-23, level on quarter-ends and tax dates), is ahead of calendar climatology by 29%, and adds nothing to persistence-logistic for the +5 bp indicator.
* **H5 is where this goes.** The spread result is the same kind of finding as phase 2's (`PLAN.md`; #632): a gbm beats persistence overall and loses in 2021-23 and on the upper tails. The inputs of #629 and #631 do not change that picture on ordinary days.

## What was not checked, and marked questions for Eleonora (not settled in code)

1. **Marked question 1 (the ceiling).** Whether to replace the in-sample ceiling with a cross-fitted one so that it can be low (point 1). Not run.
2. **Marked question 2 (the indicator's benchmark line).** Whether the rule's AUROC line for the indicator should be persistence-logistic's AUROC and not 0.6 (point 2). The numbers for both readings are above.
3. **Which model counts as "the ceiling" and "the reachable line".** The rule takes the better of the two families on the same days by the point estimate; that is a choice among two on development days. Here the gradient-boosted fit is the better in every case, so the choice does not move the verdict.
4. **The B3 incumbent was not scored here.** The directive asks for persistence (B1), and the protocol's B3 (the published v1 declaration on the 23-level grid) is a question for Eleonora (#655), so the published declaration is not a benchmark in this study.
5. **The first decision day (2018-06-28) has no B2**, because the year before it holds no quarter-end day; it is left out of every window. The walk-forward window starts at 2019-07-31 by the 250-row minimum, so the 2018-19 regime is scored on 104 decision days of its second year only.
6. **The new sources of #630 (H3) and the 2014-2018 back-fill (H4) are not inputs**; the six `nowcast_*` model columns are not inputs either (the as-of rule refuses them as undeclared); `spread_nowcast_bps` is one of the 159.
7. **Inputs are read once, at the project's "both" timing**; the unrevised-vintage questions (H.4.1 and TGA revisions) are the earlier directives'. Missing inputs are left missing for the gradient-boosted fits and imputed with the training mean for the linear ones.
8. **No setting was tuned.** The ceiling's settings are looser than the reachable ones (400 rounds and 31 leaves against 200 and 15; a ridge penalty of 1 against 30; a logistic inverse penalty of 1.0 against 0.05). That the reachable ridge is poor is not a reason to retune it here.
9. **The decision-day score on a subset** (ordinary, risk dates, a regime, a day type) is the mean over the leads whose target is in the subset, which is `scoring_protocol.day_scores` with the other outcomes withheld. A subset is reported, never a pass requirement (protocol v1 §7).
10. **Variants.** Two model families (a gradient-boosted and a regularised linear one) for each of two targets, each at two settings: eight fitted rows and the two indicator references, and no other. Nothing about a score was fed back into the declaration or the input list.
11. **Not tested here**, because the directive does not ask for it: a weekly or monthly aggregation of the score, prospective logging (#656), and a power study of the 3% minimum effect (#656).

## Reproduce

Published panel `4ddc3882…` (`build` and `verify-panel` clean, unchanged); the scratch panel `DERIV.csv` (sha256 `08df8d19…`) is built as in `docs/pivot/derived-features-result.md` (Reproduce: `pressure_v1_1.py panel` through `nowcast.py panel`,
`dvp_segment_inputs.py panel`, `early_warning_inputs.py panel`, `satiation_distance_598.py panel`, `source_screen.py panel`, `derived_features_631.py panel`). `/opt/rmm-venv` (numpy 2.4.6, scikit-learn 1.9.1), `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`.
The fit takes about an hour on four cores; the scoring a few minutes.

```
PYTHONPATH=src python3 scripts/upper_bound_635.py declare --panel DERIV.csv        # run once; metadata/upper_bound_635.json was committed before any number
PYTHONPATH=src python3 scripts/upper_bound_635.py fit --panel DERIV.csv --output OUT/fits.json
PYTHONPATH=src python3 scripts/upper_bound_635.py score --published PUB.csv --fits OUT/fits.json --output docs/pivot/evidence/upper-bound/score.json
PYTHONPATH=src python3 scripts/upper_bound_635.py report docs/pivot/evidence/upper-bound/score.json --output docs/pivot/evidence/upper-bound/tables.md
```
