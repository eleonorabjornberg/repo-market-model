# Four model defects, measured on the five risk-date passers (#540)

A measurement, not a candidate. It writes nothing into `docs/runs/`, publishes nothing, changes no information-set rule and
moves no published figure (`docs/decisions/lockbox.md`: scored days 2018-06-29 to 2025-12-31 only; the confirmation window and the
blind tier are not looked at). The four changes, how each is built and the numbers in them were declared in
`metadata/model_defects_540.json` and the judge's candidate files `metadata/pressure_judge/candidates/*_540.json` **before any
score** (commits `58ebb76` and `a8655cc`; the three judge files for the `+leaf_540` rows of the estimators without a leaf floor came in `8fb2cbf`, still before the judge ran); `scripts/model_defects_540.py` refuses an uncommitted declaration. The parents are the five
tier-1 passers of `risk-date-severity-result.md` (`risk_gbm`, `risk_gbm_base`, `risk_logistic`, `risk_logistic_base`,
`risk_quantile_skewt_base`), unchanged except for the one change. The judge is the one in force on `origin/main` at `6237f17`
(`#536` had not merged); settlement dating and the H.4.1 timing are Eleonora's ruling of 10 October and the work of #541, not here.

Published panel `4ddc3882…` (rebuilt from the tracked fixtures; scratch panel built as for #428). Environment `/opt/rmm-venv`.

## Reproduce

```
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
for h in 1 2 3 4 5: scripts/risk_date_severity.py run ... --output OUT/risk_h$h.json     # the parents
for h in 1 2 3 4 5: scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --published --output OUT/bench_h$h.json
for h, v in leaf iorb added all, each parent: scripts/model_defects_540.py run --panel AUG2.csv --published PUBLISHED.csv \
    --variant $v --horizon $h --candidate $c --declared OUT/risk_h$h.json --output OUT/m540_${v}_${c}_h$h.json
for h: scripts/model_defects_540.py assemble --output OUT/m540_h$h.json OUT/m540_*_h$h.json
scripts/pressure_judge.py judge --panel PUBLISHED.csv --output OUT/judge.json --markdown OUT/judge.md OUT/bench_h?.json OUT/risk_h?.json OUT/m540_h?.json
scripts/pressure_judge.py table OUT/judge.json --output OUT/tables.md
scripts/model_defects_540.py compare --panel PUBLISHED.csv --output OUT/compare.json --markdown OUT/compare.md OUT/bench_h?.json OUT/risk_h?.json OUT/m540_h?.json
scripts/model_defects_540.py added --panel PUBLISHED.csv --output OUT/added.json OUT/m540_added_*_h?.json
scripts/model_defects_540.py refits --output OUT/refits.json OUT/m540_*_h?.json
scripts/model_defects_540.py nowcast --panel AUG2.csv --output OUT/nowcast.json
```

(`PYTHONPATH=src`, `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1`.) Evidence: `docs/pivot/evidence/model-defects/`
(`judge.md` the judge's full report with its splits by regime and pressure-day type, `judge-tables.md` its tables, `compare.md` each variant
beside its parent by year, regime and day type with paired intervals, `added.json`, `refits.json`, `nowcast.json`).

## What was changed

| change | built as |
|---|---|
| `leaf` | the gradient-boosted classifier's `min_samples_leaf` is `min(20, max(1, pairs // 4))` instead of 20. The logistic and the skew-t have no leaf floor: their `+leaf_540` row **is** the parent (copied, not refitted) |
| `iorb` | `iorb_announced_change_bps` is an input at h = 1 only (FOMC point-in-time rule, `announced_iorb.py`) |
| `added` | the risk-date set grows by the bill-settlement days (h = 1) and the business-day month-end and quarter-end window (all h); the added dates get **their own fit** (same estimator and inputs, trained on added-date pairs only); the original dates keep the declared fit |
| `all` | the three above together |
| nowcast cap | the nowcast's ridge target (the one-day spread change) is clipped to ±5 bp (`nowcast.walk_forward(target_cap_bp=)`); scoring is against the unclipped spread |

The nowcast is not an input of the risk-date models, so it is scored on its own error and is not in `all`.

## 1. The nowcast: capping fixes most of the loss, not all

Mean absolute error of the nowcast against the spread of the same row, 1873 scored days; paired difference from the naive nowcast
(the day-before spread), 90% stationary-bootstrap interval (the judge's block length 10, 2000 replications). Positive: worse than naive.

| nowcast | all days | pressure days (> 5 bp) | quarter-end days |
|---|---|---|---|
| naive | 1.825 | 10.80 | 8.13 |
| declared primary (reverse repo and settlement), uncapped | 3.463; +1.638 [+1.306, +1.994] | 10.57; −0.229 [−1.329, +0.747] | 10.08; +1.947 [−0.467, +4.959] |
| same, target capped at 20 bp | 2.201; +0.376 [+0.211, +0.537] | 9.87; −0.932 [−1.891, −0.111] | 8.67; +0.537 [−1.251, +2.545] |
| same, capped at 10 bp | 2.016; +0.191 [+0.079, +0.298] | 9.99; −0.817 [−1.504, −0.201] | 8.18; +0.055 [−1.225, +1.328] |
| **same, capped at 5 bp (the declared cap)** | **1.920; +0.095 [+0.017, +0.169]** | **10.17; −0.631 [−1.110, −0.212]** | **8.08; −0.048 [−0.699, +0.583]** |
| no same-day input, uncapped | 3.613; +1.788 [+1.460, +2.117] | 11.15; +0.350 [−0.801, +1.369] | 9.66; +1.532 [+0.768, +2.312] |
| no same-day input, capped at 5 bp | 1.872; +0.047 [−0.007, +0.094] | 10.53; −0.272 [−0.743, +0.134] | 8.29; +0.164 [+0.033, +0.322] |

The capped nowcast reproduces the figures of `desk-standard-result.md` §6 (1.920 and 1.872). Against the uncapped declared nowcast the cap
lowers the error by 1.543 bp [−1.853, −1.271] over all days. **It still loses to naive over all days** (+0.095 [+0.017, +0.169]); it is
closer than naive on pressure days (−0.631 bp [−1.110, −0.212]) and level on quarter-end days. The no-same-day-input control, capped, is a tie with naive over all days:
the same-day inputs do not earn their place on this reading. The cap of 5 bp is the one `desk-standard-result.md` read, so this is not an independent
choice (declared as such); the 10 and 20 bp rows are the other two it tried.

## 2. Constant early fits: the leaf floor removes them, and trades them for false alarms

Refits through 2019 whose +5 bp gradient-boosted fit is constant on its own training pairs (`refits.json`):

| | h = 1 | h ≥ 2 |
|---|---|---|
| declared (leaf 20) | 6 of 18 | 10 of 18 |
| scaled leaf floor | **0 of 18** | **0 of 18** |

The first refit has 12 original risk-date pairs (one event at +5 bp). In the `added` variant the original dates keep the declared floor, so its
original-date fit is constant on the same refits as the parent (the added-date fit is a second fit). `iorb` leaves the counts at 6 and 10.

Effect of the floor on the two GBMs (judge, +5 bp; compare, paired against the parent). Onsets flagged at some lead 1 to 5, of 26: `risk_gbm` 13 → 13,
`risk_gbm_base` 14 → 15 (difference +0.0385 [+0.0000, +0.1000]; the extra onset is 2018's, 0/4 → 1/4). False alarms per onset at h = 1 rise (`risk_gbm`
1.30 → 1.67, `risk_gbm_base` 1.44 → 1.63) and the judge's worst-lead figure rises (1.38 → 2.38 and 1.50 → 2.19, limit 2). Brier at h = 1 against the parent: `risk_gbm`
−0.0001 [−0.0014, +0.0010], `risk_gbm_base` +0.0001 [−0.0016, +0.0016]. **A floor that removes the constant fits does not change the Brier score, moves recall by at most one onset, and
costs false alarms.**

## 3. The announced IORB change at h = 1: nothing moves

`iorb` changes no onset flagged, no false alarm count at h ≥ 2 and, at h = 1, at most a handful of flags (`risk_logistic_base` 90 → 91 flags; every other model's
h = 1 flag counts are equal to the parent's or within one). Brier against the parent is +0.0000 [+0.0000, +0.0000] in every regime for the GBMs. The reason is structural: the
input is read on the declared risk dates only, and the one onset it could explain, 2020-03-04 (a −50 bp cut announced before the decision), is **not** a risk date
(`construction-gaps-result.md` §6), so the model never forecasts it. Using the input there needs a risk-date clause for a day with an announced change; that is a new
risk-date rule and not in this declaration.

## 4. Added risk dates modelled apart: more recall, too many false alarms

Added dates at h = 1: 669 days (from 404 original); at h ≥ 2: 106 to 108 (277 original). Onsets on each at the judge's grid, `added.json` (flagged / on the set):

| model | h = 1 original | h = 1 added | h ≥ 2 original (h = 2) | h ≥ 2 added (h = 2) | added dates unserved (h = 1) |
|---|---|---|---|---|---|
| risk_gbm | 12/21 | 0/5 | 8/13 | 0/1 | 30 |
| risk_gbm_base | 11/21 | 2/5 | 7/13 | 0/1 | 29 |
| risk_logistic | 10/21 | 3/5 | 6/13 | 0/1 | 30 |
| risk_logistic_base | 11/21 | 3/5 | 5/13 | 0/1 | 29 |
| risk_quantile_skewt_base | 9/21 | 0/5 | 7/13 | 0/1 | 109 |

(The skew-t's unserved count is its law's exact-zero tail on added days, as in `construction-gaps-result.md` §2.) At h ≥ 2, 12 of the 26 onsets are on no risk date, original or added, and only one is reached by the added set. At h = 1 one of 27 is on none.

Judge, +5 bp, pooled over leads (onsets flagged, recall with its 90% interval, worst false alarms per onset — limit 2, the judge's own pass column; all rows):

| model | onsets flagged | recall [90%] | worst false alarms per onset | tier 3: worst flags per 252 days, state 0 / 2021-23 | verdict (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 1.38 | 1.5 / 0.7 | fail (tiers yes / no / no) |
| risk_gbm+added_540 | 14 of 26 | 0.538 [0.364, 0.720] | 2.77 | 1.2 / 0.7 | fail (tiers yes / no / no) |
| risk_gbm+all_540 | 16 of 26 | 0.615 [0.429, 0.800] | 3.73 | 1.7 / 2.0 | fail (tiers no / no / no) |
| risk_gbm+iorb_540 | 13 of 26 | 0.500 [0.318, 0.680] | 1.38 | 1.5 / 0.7 | fail (tiers yes / no / no) |
| risk_gbm+leaf_540 | 13 of 26 | 0.500 [0.316, 0.684] | 2.38 | 1.5 / 1.0 | fail (tiers yes / no / no) |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 1.50 | 0.5 / 0.0 | fail (tiers yes / no / no) |
| risk_gbm_base+added_540 | 16 of 26 | 0.615 [0.435, 0.786] | 3.08 | 0.5 / 0.7 | fail (tiers yes / no / no) |
| risk_gbm_base+all_540 | 18 of 26 | 0.692 [0.517, 0.852] | 3.96 | 0.5 / 0.0 | fail (tiers no / no / no) |
| risk_gbm_base+iorb_540 | 14 of 26 | 0.538 [0.360, 0.714] | 1.50 | 0.5 / 0.0 | fail (tiers yes / no / no) |
| risk_gbm_base+leaf_540 | 15 of 26 | 0.577 [0.407, 0.750] | 2.19 | 0.5 / 0.0 | fail (tiers yes / no / no) |
| risk_logistic | 16 of 26 | 0.615 [0.435, 0.800] | 2.42 | 3.2 / 0.7 | fail (tiers yes / no / no) |
| risk_logistic+added_540 | 17 of 26 | 0.654 [0.471, 0.833] | 3.77 | 2.9 / 0.0 | fail (tiers no / no / no) |
| risk_logistic+all_540 | 17 of 26 | 0.654 [0.476, 0.833] | 3.81 | 2.9 / 0.0 | fail (tiers no / no / no) |
| risk_logistic+iorb_540 | 16 of 26 | 0.615 [0.440, 0.793] | 2.46 | 3.2 / 0.7 | fail (tiers yes / no / no) |
| risk_logistic+leaf_540 | 16 of 26 | 0.615 [0.429, 0.789] | 2.42 | 3.2 / 0.7 | fail (tiers yes / no / no) |
| risk_logistic_base | 15 of 26 | 0.577 [0.391, 0.762] | 2.31 | 1.5 / 0.0 | fail (tiers yes / no / no) |
| risk_logistic_base+added_540 | 16 of 26 | 0.615 [0.432, 0.792] | 3.88 | 0.7 / 0.0 | fail (tiers no / no / no) |
| risk_logistic_base+all_540 | 16 of 26 | 0.615 [0.423, 0.792] | 4.04 | 0.7 / 0.0 | fail (tiers no / no / no) |
| risk_logistic_base+iorb_540 | 15 of 26 | 0.577 [0.393, 0.767] | 2.31 | 1.5 / 0.0 | fail (tiers yes / no / no) |
| risk_logistic_base+leaf_540 | 15 of 26 | 0.577 [0.385, 0.760] | 2.31 | 1.5 / 0.0 | fail (tiers yes / no / no) |
| risk_quantile_skewt_base | 15 of 26 | 0.577 [0.391, 0.750] | 2.31 | 1.0 / 0.7 | fail (tiers yes / no / no) |
| risk_quantile_skewt_base+added_540 | 17 of 26 | 0.654 [0.467, 0.833] | 3.88 | 1.2 / 0.7 | fail (tiers no / no / yes) |
| risk_quantile_skewt_base+all_540 | 17 of 26 | 0.654 [0.474, 0.826] | 3.96 | 1.2 / 0.7 | fail (tiers no / no / yes) |
| risk_quantile_skewt_base+iorb_540 | 15 of 26 | 0.577 [0.400, 0.759] | 2.31 | 1.0 / 0.7 | fail (tiers yes / no / no) |
| risk_quantile_skewt_base+leaf_540 | 15 of 26 | 0.577 [0.387, 0.760] | 2.31 | 1.0 / 0.7 | fail (tiers yes / no / no) |

Every row fails the pass rule (tiers 3 and 5 fail for every parent and every variant, as for the parents before). On tier 1 the parents pass and `leaf` and `iorb`
rows keep that; the `added` and `all` rows raise recall (`risk_gbm_base` 14 → 16 and 18 of 26; `risk_logistic` 16 → 17; `risk_logistic_base` 15 → 16) but the worst false alarms per onset
rise to 2.77 to 4.04, above the limit, and tier 1 then fails for `risk_gbm+all`, `risk_gbm_base+all`, `risk_logistic+added`/`+all`, `risk_logistic_base+added`/`+all` and `risk_quantile_skewt_base+added`/`+all`. The skew-t with the added dates flags **fewer**
onsets at some lead than its parent in the paired reading (14 → 11 of 26, −0.1154 [−0.2174, −0.0285]), because its added days are largely unserved.

Tier-1 numbers per lead (onsets flagged / onsets, false alarms per onset, all days) are in `compare.md`, Table 2. Examples at h = 1, parent → `added`: `risk_gbm` 13/27, 1.30 → 12/27, 1.15;
`risk_gbm_base` 13/27, 1.44 → 13/27, 2.22; `risk_logistic` 13/27, 1.78 → 13/27, 2.63; `risk_logistic_base` 13/27, 1.70 → 14/27, 2.41; `risk_quantile_skewt_base` 13/27, 1.81 → 9/27, 1.41.

## Recall by year, with 2018, 2020 and 2024 called out

Onsets flagged at some lead 1 to 5 (`compare.md`). **2018 (4 onsets), 2020 (2) and 2024 (2): no parent and no variant flags any of them, except** `risk_gbm_base` with the
leaf floor (and with all three), which flags one of the four 2018 onsets (1/4). 2019 (13 onsets): the parents flag 10; `added` and `all` raise that to 12 or 13 for the GBM-base and the logistics
(`risk_logistic` 13/13, +0.2308 [+0.0000, +0.4444]) and lower it to 9 for the skew-t. 2025 (5): the parents flag 3 or 4; `added` and `all` flag 2 for every model except `risk_gbm` (3). The added
dates buy 2019 and cost 2025. The paired intervals for the splits by regime and pressure-day type are in `compare.md` (Table 1, recall) and its Table 3 (Brier at h = 1, positive favours the variant).
Against the parent the Brier score at h = 1 *improves* with the added dates for the GBM: `risk_gbm+added_540` +0.0061 [+0.0011, +0.0119] over all days (2018-19 +0.0242 [+0.0011, +0.0511];
ordinary days +0.0070 [+0.0014, +0.0134]; 2025-26 +0.0103 [−0.0000, +0.0228]). So the added fit is better calibrated on the dates it adds, while the cut-off the judge picks flags too many of them.

## Reading

* The nowcast cap removes most of the nowcast's loss (3.463 → 1.920 bp) and brings it level with naive on quarter-end days and ahead of it on pressure days, but it still loses to naive overall and the same-day inputs add nothing over the cap alone.
* The scaled leaf floor ends the constant early fits, with no change in Brier (differences of ±0.0001, intervals spanning zero) and one extra onset at most; the gradient-boosted models become less selective.
* The announced IORB change at h = 1 moves nothing, because the one onset it explains is not on a risk date.
* Modelling the added risk dates apart avoids the dilution of `construction-gaps-result.md` (the original-date fit is exactly the declared one, apart from the cut-offs, which the judge picks from the flags of both sets) but gives the false alarms back: the added dates are many and their own fit flags too often to meet tier 1's limit of two per onset. No variant passes the pass rule.

## Not checked

* Which of the 7 coupon-settlement onsets is warned: that is #541's, and settlement dating is unchanged here.
* The judge's pooled onsets-flagged count (`judge-tables.md`) and the comparison's "at some lead" count differ for some variants (`risk_gbm+all`: 16 against 14); the two use different flag sets and this run did not reconcile them. The comparison, which pairs variant with parent on one grid, is the one read above for differences.
* The `added` fit's own early refits (the added group has 10 pairs at the first refit) and the wide calendar window of `construction-gaps-result.md` (a size chosen after the onsets, not used).
* No change is selected, tuned or recommended for publication; no 2026 day and no published record is read or edited. Nothing is published and no "Publish?" question is raised: none of the four changes joins a published declaration.
