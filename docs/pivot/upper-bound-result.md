# Upper-bound study: how much signal is in the data we hold, for the spread and for ordinary-day pressure (#635, H2 step 3)

A development measurement. It is never a claim and never a verdict for a hypothesis (scoring protocol v1, `docs/decisions/scoring-protocol.md` §1 and §9, "H2": a go/no-go for effort).
It writes nothing into `docs/runs/`, publishes nothing, moves no published figure, reads no day after 2025-12-31 and scores no day of a locked tier (`docs/decisions/lockbox.md`; `require_unlocked`).
Every choice, the reading rule included, is in `metadata/upper_bound_635.json`, committed before any number was computed; the script refuses an uncommitted declaration. The scoring sections of the
directive are superseded by protocol v1 wherever they differ (ruling of 12 October 2026 on #635): the metric is the 23-level grid CRPS averaged over leads 1 to 5, the benchmarks are B1 (as-of persistence) and B2
(calendar climatology), the interval is the stationary bootstrap (mean block 10, one-sided 95% test, 10,000 draws on the primary cells). **Nothing here joins a published declaration, so no "Publish?" question arises.**

Hypothesis and step: H2, step 3 (`docs/research/hypotheses/H2.md`). The matrices (#629) and the derived features (#631) have merged and the features are among the inputs.

## Verdict, under the reading rule committed first, as amended by the ruling of 13 October

Eleonora's ruling of 13 October 2026 on this PR's two marked questions (comment 6149433242) is applied as two **declared deviations** from the first declaration, committed before the re-run (`metadata/upper_bound_635.json`, key `deviations`): (1) the ceiling is **cross-fitted**
(ten contiguous blocks of days per lead, each scored by a fit that did not see it, with an embargo equal to the walk-forward's before the block and its mirror after it; `LookAheadError` otherwise), and the first declaration's in-sample fit is kept and reported beside it as **memorised**;
(2) the indicator's headline is read against **persistence-logistic** (AUROC difference and Brier skill, with 90% intervals); the 0.6 line is a secondary reading. Both are development readings, not verdicts.

**Spread (the primary target): partly reached, by a hair. Ordinary-day +5 bp indicator: data problem.** The one-line verdict is the primary target's: **partly reached**. Read the next section before using it.

| | ceiling (cross-fitted, generous settings) | reachable (walk-forward, reads public data only) | rule |
|---|---|---|---|
| spread, CRPS skill against B1, ordinary days (best model of the two) | +0.144 [+0.0002, +0.271] (gbm) | +0.192 [+0.007, +0.352] (gbm) | barely above if the lower end is at or below 0 |
| ordinary-day +5 bp, AUROC minus persistence-logistic (best model of the two) | -0.016 [-0.044, +0.015] (gbm) | +0.015 [-0.017, +0.058] (gbm) | barely above if the lower end is at or below 0, or the Brier-skill lower end is |
| ordinary-day +5 bp, Brier skill against persistence-logistic | -0.159 [-0.245, -0.059] (gbm) | -0.192 [-0.374, +0.034] (gbm) | (the second condition above) |
| secondary: AUROC averaged over leads 1 to 5 (the issue's 0.6 line) | 0.864 [0.821, 0.899] (persistence-logistic 0.880) | 0.905 [0.851, 0.938] (0.890) | under 0.6 is "barely above climatology"; decides nothing |

The memorised (in-sample) fit, for reference and carrying no reading: spread +0.781 [+0.747, +0.815] (gbm), ordinary-day AUROC 1.000 [1.000, 1.000].

## What the verdict does and does not say

1. **The cross-fitted ceiling is not above the reachable line.** It is a ceiling only in intent: on the 1,598 walk-forward days the cross-fitted gbm scores +0.162 [-0.009, +0.310] against B1 and the reachable gbm +0.192 [+0.007, +0.352]; the reachable-to-ceiling gap is -0.037 [-0.124, +0.049]. The ceiling uses
   later data to fit earlier days, and still does no better. On its own days (all 1,868 decision days) the cross-fitted gbm is +0.144 [+0.0002, +0.271] (bootstrap p 0.050, Diebold-Mariano p 0.075): the lower end clears 0 by 0.0002, so "partly reached" rests on a hair, and a different bootstrap draw could move it either way. The same cell on all days is +0.152 [+0.035, +0.246].
   Read plainly: there is signal for the spread beyond as-of persistence in the data we hold, it is modest (14 to 19% of CRPS), and a more flexible fit with more data does not extract more of it. The memorising in-sample fit (+0.781) says nothing about information: it fits 1,873 days of 159 inputs almost without error.
2. **The indicator: nothing beyond persistence-logistic.** Persistence-logistic alone scores AUROC 0.880 [0.841, 0.911] on the cross-fitted ordinary days. The cross-fitted gbm is level with it in AUROC (-0.016 [-0.044, +0.015]) and worse in Brier score (skill -0.159 [-0.245, -0.059]); the cross-fitted logistic is worse in both
   (AUROC -0.088 [-0.137, -0.036]). The reachable line reads the same way (+0.015 [-0.017, +0.058]; Brier skill -0.192 [-0.374, +0.034]). Under the amended rule both lines are barely above persistence-logistic, so the indicator reads **data problem**: effort for that target does not go to a better model of these inputs but to new data (H3, H4).
   The 0.6 line (secondary) is passed by persistence alone; reported, decides nothing.
3. **The pressure days on ordinary days are mostly one regime.** Of the 82 ordinary pressure days, #631 found 62 in 2018-19, 15 in 2025-26, 5 in 2020 and 2024 and none in 2021-23. A pooled AUROC measures "which regime" as much as timing. The regime split shows it: on the walk-forward days the cross-fitted gbm's AUROC is 0.536 [0.377, 0.675] in 2018-19 (persistence-logistic 0.749) and 0.884 [0.790, 0.942] in 2025-26 (0.889).
4. **The reachable spread result is marginal and uneven** (unchanged from the first run; the reachable fits reproduced it to the digit). The interval of the primary cell clears 0 by 0.007; the one-sided 95% lower bound of the mean CRPS difference is +0.010 bp, and the Diebold-Mariano p is 0.073 (the bootstrap p is 0.041).
   By regime, the reachable gbm is ahead of B1 in 2018-19, 2024 and 2025-26 and **behind it in 2021-23** (-0.318 [-0.529, -0.133] on ordinary days), the regime where phase 2's gbm also lost to persistence. On quarter-ends and tax dates it is level or behind. The regularised linear fit is unstable out of sample (below), and cross-fitted it is worse still (-1.158 [-1.682, -0.753]).

## The spread

Grid CRPS in basis points (twice the mean pinball loss over the 23 levels of protocol v1), averaged over leads 1 to 5 per decision day, on the 1,598 decision days of the walk-forward window (the first is 2019-07-31, the first block with the 250 training rows the declaration asks for).
"Ordinary" scores a decision day on those of its five targets that are ordinary days (a decision day with no ordinary target is dropped, none is on this window). Skill = (benchmark mean - candidate mean) / benchmark mean, positive favouring the candidate; the interval is the 5th to 95th percentile of the paired skill draws.
The full tables, with the one-sided 95% lower bounds, the bootstrap and Diebold-Mariano p-values, MAE of the median, the splits and every lead, are in `docs/pivot/evidence/upper-bound/tables.md`; every cell is in `score.json` there.

| walk-forward days, ordinary targets | B1 mean | candidate mean | skill against B1 [90%] | skill against B2 [90%] |
|---|---|---|---|---|
| reachable gbm | 1.718 | 1.388 | +0.192 [+0.007, +0.352] | +0.290 [+0.227, +0.351] |
| reachable ridge | 1.718 | 3.804 | -1.213 [-2.114, -0.620] | -0.947 [-1.421, -0.557] |
| ceiling gbm (cross-fitted) | 1.718 | 1.440 | +0.162 [-0.009, +0.310] | +0.263 [+0.176, +0.349] |
| ceiling ridge (cross-fitted) | 1.718 | 3.576 | -1.081 [-1.683, -0.634] | -0.830 [-1.109, -0.604] |
| memorised gbm (in-sample) | 1.718 | 0.372 | +0.784 [+0.740, +0.823] | +0.810 [+0.779, +0.838] |
| memorised ridge (in-sample) | 1.718 | 1.481 | +0.138 [-0.061, +0.295] | +0.242 [+0.131, +0.334] |

* **Where the reachable gbm beats persistence, and where it loses** (ordinary targets, against B1, 2000 draws): 2018-19 +0.598 [+0.053, +0.763]; 2020 +0.056 [-0.184, +0.237]; **2021-23 -0.318 [-0.529, -0.133]**; 2024 +0.272 [+0.162, +0.365]; 2025-26 +0.220 [+0.081, +0.339].
  By day type (all targets): ordinary +0.197 [+0.011, +0.357]; month-end +0.097 [-0.120, +0.250]; quarter-end -0.051 [-0.417, +0.147]; tax date -0.073 [-0.342, +0.019]. On risk-date targets it is level with B1 (+0.007 [-0.095, +0.097]). It beats B2 everywhere in the pooled cells.
* **By lead** (ordinary targets, against B1): +0.256 [+0.008, +0.445] at lead 1, +0.263 [+0.051, +0.440] at lead 2, +0.278 [+0.087, +0.435] at lead 3, +0.253 [+0.065, +0.411] at lead 4, +0.237 [+0.051, +0.388] at lead 5.
* **MAE of the median** (ordinary targets): the reachable gbm 1.95 bp against B1's 2.15 (skill +0.092 [-0.093, +0.256]), so the gain is in the width and tails of the distribution, not in the median.
* **The gap between the lines, on the same days:** the cross-fitted gbm is -0.037 [-0.124, +0.049] against the reachable gbm (skill relative to the reachable line; negative means the reachable line is the better), the cross-fitted ridge +0.060 [-0.185, +0.265] against the reachable ridge. The memorised gbm is +0.732 [+0.706, +0.758] and the memorised ridge +0.611 [+0.505, +0.699] better: memorisation, not information.
* **The regularised linear fit blows up out of sample.** Its reachable CRPS is 3.80 bp against B1's 1.72. The cause is traceable: at lead 1, in April 2020 its median reads +69 to +137 bp on six days (and -93 bp on 2020-04-01) when the spread was -7 to -9 bp (inputs far outside the training range, clipped at five standard deviations but still large against 250 to 500 training rows),
  and on 2019-09-17 it reads a 20 bp median against an observed 315 bp. It is stable in 2024 and 2025-26 (-0.125 [-0.416, +0.032] and +0.101 [-0.020, +0.198]). Read this as a property of the declared design (about 214 columns, a fixed penalty, no selection), not of linear models in general.
* **The ceiling window** (all 1,868 decision days, ordinary targets, against B1): cross-fitted gbm +0.144 [+0.0002, +0.271], cross-fitted ridge -1.158 [-1.682, -0.753]; memorised gbm +0.781 [+0.747, +0.815], memorised ridge +0.165 [+0.007, +0.294].
  By lead on the walk-forward days (ordinary targets, cross-fitted gbm against B1): +0.224 [+0.001, +0.404], +0.223 [+0.021, +0.396], +0.232 [+0.044, +0.389], +0.226 [+0.051, +0.374], +0.224 [+0.065, +0.363] at leads 1 to 5.

## The +5 bp indicator on ordinary days

1,469 ordinary scored days, 82 of them pressure days (140 pressure days in all). Trained on ordinary days only. AUROC and Brier skill are averaged over leads 1 to 5 with the stationary bootstrap (mean block 10, 1,000 draws) over the ordinary days in date order, one draw shared by every lead and model.
The walk-forward window is the reachable fits' served days: 1,271 ordinary days with 51 pressure days at leads 1 and 2, 1,254 and 37 at leads 3 to 5. The cross-fitted ceiling is scored on all 1,469 ordinary days (82 pressure days), and also on the walk-forward days.

| ordinary days | AUROC [90%] | AUROC minus persistence-logistic [90%] | Brier | Brier skill against climatology [90%] | Brier skill against persistence-logistic [90%] |
|---|---|---|---|---|---|
| ceiling gbm (cross-fitted, all days) | 0.864 [0.821, 0.899] | -0.016 [-0.044, +0.015] | 0.0576 | -0.039 [-0.138, +0.035] | -0.159 [-0.245, -0.059] |
| ceiling ridge (cross-fitted, all days) | 0.792 [0.737, 0.839] | -0.088 [-0.137, -0.036] | 0.1036 | -0.869 [-1.830, -0.355] | -1.072 [-1.965, -0.544] |
| persistence-logistic (cross-fitted, all days) | 0.880 [0.841, 0.911] | | 0.0497 | +0.103 [-0.002, +0.167] | |
| ceiling gbm (cross-fitted, walk-forward days) | 0.911 [0.856, 0.941] | +0.004 [-0.024, +0.033] | 0.0328 | +0.056 [+0.015, +0.150] | -0.122 [-0.227, +0.032] |
| reachable gbm (walk-forward days) | 0.905 [0.851, 0.938] | +0.015 [-0.017, +0.058] | 0.0355 | +0.037 [-0.139, +0.265] | -0.192 [-0.374, +0.034] |
| reachable ridge (logistic, walk-forward days) | 0.870 [0.805, 0.914] | -0.020 [-0.078, +0.044] | 0.0335 | +0.091 [-0.067, +0.277] | -0.122 [-0.309, +0.059] |
| persistence-logistic (walk-forward days) | 0.890 [0.821, 0.937] | | 0.0299 | +0.192 [+0.131, +0.276] | |
| climatology (training rate, walk-forward days) | | | 0.0370 | | |
| memorised gbm (in-sample, all days) | 1.000 [1.000, 1.000] | +0.075 [+0.053, +0.108] | 0.0000 | +1.000 [+1.000, +1.000] | +1.000 [+1.000, +1.000] |
| memorised ridge (in-sample, all days) | 0.992 [0.988, 0.996] | +0.068 [+0.048, +0.097] | 0.0152 | +0.711 [+0.643, +0.759] | +0.669 [+0.608, +0.716] |

By regime the reachable gbm's AUROC is 0.463 [0.349, 0.633] in 2018-19 and 0.871 [0.777, 0.939] in 2025-26 (persistence-logistic: 0.655 and 0.885); the cross-fitted gbm on the same walk-forward days 0.536 [0.377, 0.675] and 0.884 [0.790, 0.942]; the other regimes have under five pressure days at some leads or none, and AUROC is not formed there (`tables.md`).
By the as-of scarcity state, the reachable gbm scores 0.587 [0.469, 0.691] inside the scarce state, where 49 of the 51 pressure days are (persistence-logistic: 0.604; cross-fitted gbm 0.622 [0.524, 0.705], persistence-logistic 0.707). So the ranking the pooled figure shows is mostly "scarce state or not", which the last public spread already carries.

## Reading it for H2

* **The spread is a "partly reached" by a hair, and the ceiling gives no room above the reachable line.** Under the H2 outcome rule, a data problem would send effort to H3 and H4 and a model problem to H5's development steps. The primary target reads neither cleanly: the cross-fitted ceiling clears persistence by 0.0002 on its lower end and sits at or below the reachable line.
  What the study does show is the reachable line: a gradient-boosted spread law on the inputs held is ahead of as-of persistence on ordinary days by 19% of CRPS (marginal, behind in 2021-23, level on quarter-ends and tax dates) and ahead of calendar climatology by 29%, and a cross-fitted fit with more data does no better.
* **The indicator reads a data problem** under the amended rule: no fit adds to persistence-logistic. That points the indicator's effort at new data (H3, H4), not at more modelling of these inputs.
* **H5 is where the spread goes.** The result is the same kind of finding as phase 2's (`PLAN.md`; #632): a gbm beats persistence overall and loses in 2021-23 and on the upper tails. The inputs of #629 and #631 do not change that picture on ordinary days.

## What was not checked, and marked questions for Eleonora (not settled in code)

1. **The ruling's two items are applied; the operational form of item 2 is this PR's choice and is marked for Eleonora.** The ruling names the quantities (AUROC difference and Brier skill against persistence-logistic, with intervals) but not the decision form; the declaration reads "barely above" when the lower end of either 90% interval is at or below 0, and "clearly above" only when both are above 0, in the form of the spread's rule. A rule that read the AUROC difference alone would give the same verdict here (the cross-fitted interval already covers 0).
2. **The fold count of the cross-fitted ceiling (ten contiguous blocks per lead) is this PR's choice**, declared before the re-run on cost: the walk-forward's 21-day blocks need 92 fits per lead at the ceiling settings, which ran at a pace of about five hours in total, so that attempt was stopped after 125 of 905 tasks with nothing scored. The embargo is the ruling's. The reachable fits are unchanged and reproduce the first run's figures to the digit.
3. **Which model counts as "the ceiling" and "the reachable line".** The rule takes the better of the two families on the same days by the point estimate; that is a choice among two on development days. Here the gradient-boosted fit is the better in every case, so the choice does not move the verdict.
4. **The B3 incumbent was not scored here.** The directive asks for persistence (B1), and the protocol's B3 (the published v1 declaration on the 23-level grid) is a question for Eleonora (#655), so the published declaration is not a benchmark in this study.
5. **The first decision day (2018-06-28) has no B2**, because the year before it holds no quarter-end day; it is left out of every window. The walk-forward window starts at 2019-07-31 by the 250-row minimum, so the 2018-19 regime is scored on 104 decision days of its second year only.
6. **The new sources of #630 (H3) and the 2014-2018 back-fill (H4) are not inputs**; the six `nowcast_*` model columns are not inputs either (the as-of rule refuses them as undeclared); `spread_nowcast_bps` is one of the 159.
7. **Inputs are read once, at the project's "both" timing**; the unrevised-vintage questions (H.4.1 and TGA revisions) are the earlier directives'. Missing inputs are left missing for the gradient-boosted fits and imputed with the training mean for the linear ones.
8. **No setting was tuned.** The ceiling's settings are looser than the reachable ones (400 rounds and 31 leaves against 200 and 15; a ridge penalty of 1 against 30; a logistic inverse penalty of 1.0 against 0.05). That the reachable ridge is poor is not a reason to retune it here.
9. **The decision-day score on a subset** (ordinary, risk dates, a regime, a day type) is the mean over the leads whose target is in the subset, which is `scoring_protocol.day_scores` with the other outcomes withheld. A subset is reported, never a pass requirement (protocol v1 §7).
10. **Variants.** Two model families (a gradient-boosted and a regularised linear one) for each of two targets, each at two settings, and the ceiling settings fitted twice (cross-fitted, and in-sample as the memorised reference): twelve fitted rows and the indicator references, and no other. Nothing about a score was fed back into the declaration or the input list; the only changes after the first run are the two declared deviations and the fold count, all committed before the re-run.
11. **Not tested here**, because the directive does not ask for it: a weekly or monthly aggregation of the score, prospective logging (#656), and a power study of the 3% minimum effect (#656).

## Reproduce

Published panel `4ddc3882…` (`build` and `verify-panel` clean, unchanged); the scratch panel `DERIV.csv` (sha256 `08df8d19…`; rebuilt for the re-run in this session with the chain below, `satiation_distance_598.py panel` between `measurement_fields.py panel` and `net_settlement.py panel`, and the satiation columns placed as the declaration lists them; the sha256 matches) is built as in `docs/pivot/derived-features-result.md` (Reproduce: `pressure_v1_1.py panel` through `nowcast.py panel`,
`dvp_segment_inputs.py panel`, `early_warning_inputs.py panel`, `satiation_distance_598.py panel`, `source_screen.py panel`, `derived_features_631.py panel`). `/opt/rmm-venv` (numpy 2.4.6, scikit-learn 1.9.1), `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`.
The fit takes about two hours on four cores; the scoring a few minutes.

```
PYTHONPATH=src python3 scripts/upper_bound_635.py declare --panel DERIV.csv        # run once; metadata/upper_bound_635.json was committed before any number, and amended by the two deviations (own commits) before the re-run
PYTHONPATH=src python3 scripts/upper_bound_635.py fit --panel DERIV.csv --output OUT/fits.json
PYTHONPATH=src python3 scripts/upper_bound_635.py score --published PUB.csv --fits OUT/fits.json --output docs/pivot/evidence/upper-bound/score.json
PYTHONPATH=src python3 scripts/upper_bound_635.py report docs/pivot/evidence/upper-bound/score.json --output docs/pivot/evidence/upper-bound/tables.md
```
