# An every-day component and no constant early fits for the risk-date passers (#506, of #374)

A scratch measurement under the pressure-day judge. It writes nothing into `docs/runs/`, moves no published figure, and
reads no day after 2025-12-31 (`docs/decisions/lockbox.md`; the script refuses a later panel, and the near-blind and
blind tiers are not looked at). No rule, threshold, onset definition, cut-off rule or availability time changes. The new
inputs and the variants are off in every published declaration. Declared before any score in
`metadata/risk_date_every_day.json` (committed before the first variant was fitted) and, for the judge, in
`metadata/pressure_judge/candidates/<parent>+every_day.json`, `+early_prior.json` and `+every_day+early_prior.json`;
`scripts/risk_date_every_day.py` refuses an uncommitted declaration.

## What was declared

The five tier-1 passers of `metadata/risk_date_severity.json` (`risk_gbm`, `risk_gbm_base`, `risk_logistic`,
`risk_logistic_base`, `risk_quantile_skewt_base`) are the parents, unchanged. Each has three variants.

* **(a) `+every_day`.** A ridge logistic of `spread > tau` (the declared `ml.PRESSURE_LOGISTIC_SETTINGS`: L2, `C` = 1,
  standardised), one per threshold, on the latest public spread (the spread's own state) and the previous day's SOFR 75th
  and 99th percentiles above IORB in basis points. It is fitted on the direct pairs of every training day, each label paired
  with what was public at its own decision instant, and both guards of the information rule read its inputs.
  **One combination rule:** on a risk date the forecast is the parent's, unchanged; on any other day it is the component's.
  So the component serves exactly the days the parent leaves at exactly 0. The test
  `RiskDateVariantTests.test_a_risk_date_keeps_the_risk_date_models_forecast` and the run (no risk-date forecast differs
  from the parent's, all parents, all horizons) check it.
* **(b) `+early_prior`.** On a refit whose risk-date training window holds fewer than 40 pairs (twice the gradient-boosted
  classifier's `min_samples_leaf`, below which it cannot split and is a constant, `construction-gaps-result.md` gap 4), the
  risk-date forecast is a day-type prior instead of the estimator, for every estimator: the window's rate of `spread > tau`
  among pairs of the scored day's type (quarter-end, month-end, tax date, or none of them, the coupon-settlement dates),
  shrunk toward the window's pooled rate by two pairs at that rate. At 40 pairs or more the parent's estimator runs as
  before. The 40 and the 2 are stated, not tuned. The same rule is applied to the logistic and the skew-t, which are not
  constants but are fitted on a handful of pairs there.
* **(c) `+every_day+early_prior`.** Both.

Scored as the judge declares: tiers 1, 3 and 5, h = 1 to 5, +5 and +10 bp, each under the flat and the weighted miss
rule (`--rule unweighted` and `--rule weighted` of the judge on `main`); the cut-off rule is unchanged and chooses each
variant's cut-offs from its own training window. Everything is paired against the parent, calendar climatology and
persistence-logistic.

## Reproduce

Published panel `4ddc3882…` (`verify-panel` clean); scratch panel as for #428 (`scripts/risk_date_severity.py`).

```
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
PYTHONPATH=src python3 scripts/risk_date_every_day.py declare        # already committed; shown for the record
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --output OUT/bench_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/risk_date_severity.py run --panel AUG2.csv --published PUBLISHED.csv --horizon $h --output OUT/risk_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/risk_date_every_day.py run --panel AUG2.csv --published PUBLISHED.csv --horizon $h --output OUT/ed_h$h.json
for r in weighted unweighted: PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule $r --output OUT/judge_$r.json --markdown OUT/judge_$r.md OUT/bench_h?.json OUT/risk_h?.json OUT/ed_h?.json
for r in weighted unweighted: PYTHONPATH=src python3 scripts/pressure_judge.py table OUT/judge_$r.json --output OUT/tables_$r.md
PYTHONPATH=src python3 scripts/risk_date_every_day.py compare --panel PUBLISHED.csv --output OUT/compare.json --markdown OUT/compare.md OUT/bench_h?.json OUT/risk_h?.json OUT/ed_h?.json
```

Set `OMP_NUM_THREADS=1` when several fits share a machine. Evidence: `docs/pivot/evidence/risk-date-every-day/`
(`summary.md` Table 1 below; `tables-unweighted`/`tables-weighted` the judge's tables for every row; `judge-*.md` the judge's full
reports, split by regime and day type; `compare.md` and `compare.json` the pairing against each parent, the flags on and off
the risk dates, onset recall by year, regime and day type, and the 26 episodes). The parents' figures reproduce #428's and
#479's (for example `risk_gbm`, 13 of 26, 1.35 false alarms per onset, flat).

## Result: no variant passes

Table 1. The judge's row at +5 bp under each rule (90% stationary-bootstrap intervals). The flat rule counts every false alarm as 1; the
weighted rule counts a false alarm at its distance-weight (`metadata/weighted_miss.json`, run with `--rule weighted`, a scratch reading).
"Worst false alarms per onset" is the highest of the five horizons; the limit is 2.

| model | onsets flagged, flat / weighted rule | recall, flat [90%] | recall, weighted [90%] | worst false alarms per onset, flat | worst weighted false alarms per onset, weighted rule | tiers 1 / 3 / 5, flat | tiers 1 / 3 / 5, weighted |
|---|---|---|---|---|---|---|---|
| risk_gbm | 13/26 / 13/26 | 0.500 [0.310, 0.667] | 0.500 [0.310, 0.667] | 1.35 | 0.80 | yes / no / no | yes / no / no |
| risk_gbm+early_prior | 13/26 / 13/26 | 0.500 [0.320, 0.677] | 0.500 [0.320, 0.677] | 1.35 | 1.17 | yes / no / no | yes / no / no |
| risk_gbm+every_day | 15/26 / 17/26 | 0.577 [0.385, 0.760] | 0.654 [0.474, 0.812] | 2.96 | 2.18 | no / no / yes | no / no / yes |
| risk_gbm+every_day+early_prior | 15/26 / 17/26 | 0.577 [0.375, 0.767] | 0.654 [0.478, 0.824] | 3.08 | 2.20 | no / no / yes | no / no / yes |
| risk_gbm_base | 14/26 / 14/26 | 0.538 [0.360, 0.719] | 0.538 [0.360, 0.719] | 1.50 | 0.97 | yes / no / no | yes / no / no |
| risk_gbm_base+early_prior | 14/26 / 14/26 | 0.538 [0.348, 0.727] | 0.538 [0.348, 0.727] | 1.62 | 1.19 | yes / no / no | yes / no / no |
| risk_gbm_base+every_day | 15/26 / 18/26 | 0.577 [0.389, 0.769] | 0.692 [0.520, 0.850] | 2.92 | 2.28 | no / no / yes | no / no / yes |
| risk_gbm_base+every_day+early_prior | 15/26 / 17/26 | 0.577 [0.364, 0.762] | 0.654 [0.464, 0.821] | 3.19 | 2.34 | no / no / yes | no / no / yes |
| risk_logistic | 14/26 / 16/26 | 0.538 [0.350, 0.724] | 0.615 [0.435, 0.800] | 1.85 | 1.74 | yes / no / no | yes / no / no |
| risk_logistic+early_prior | 14/26 / 16/26 | 0.538 [0.364, 0.714] | 0.615 [0.444, 0.792] | 1.54 | 1.38 | yes / no / no | yes / no / no |
| risk_logistic+every_day | 13/26 / 17/26 | 0.500 [0.333, 0.667] | 0.654 [0.480, 0.826] | 2.69 | 2.28 | no / no / yes | no / no / yes |
| risk_logistic+every_day+early_prior | 15/26 / 17/26 | 0.577 [0.400, 0.750] | 0.654 [0.476, 0.815] | 3.15 | 2.38 | no / no / yes | no / no / yes |
| risk_logistic_base | 13/26 / 15/26 | 0.500 [0.333, 0.680] | 0.577 [0.391, 0.762] | 1.77 | 1.65 | yes / no / no | yes / no / no |
| risk_logistic_base+early_prior | 13/26 / 14/26 | 0.500 [0.333, 0.680] | 0.538 [0.364, 0.714] | 1.46 | 1.37 | yes / no / no | yes / no / no |
| risk_logistic_base+every_day | 11/26 / 13/26 | 0.423 [0.259, 0.593] | 0.500 [0.321, 0.679] | 2.31 | 2.26 | no / no / yes | no / no / yes |
| risk_logistic_base+every_day+early_prior | 14/26 / 16/26 | 0.538 [0.360, 0.706] | 0.615 [0.429, 0.778] | 3.15 | 2.36 | no / no / yes | no / no / yes |
| risk_quantile_skewt_base | 14/26 / 15/26 | 0.538 [0.360, 0.714] | 0.577 [0.391, 0.750] | 1.88 | 1.62 | yes / no / no | yes / no / no |
| risk_quantile_skewt_base+early_prior | 14/26 / 15/26 | 0.538 [0.364, 0.714] | 0.577 [0.400, 0.750] | 1.81 | 1.52 | yes / no / no | yes / no / no |
| risk_quantile_skewt_base+every_day | 15/26 / 16/26 | 0.577 [0.409, 0.750] | 0.615 [0.444, 0.792] | 2.46 | 2.63 | no / no / yes | no / no / yes |
| risk_quantile_skewt_base+every_day+early_prior | 13/26 / 17/26 | 0.500 [0.316, 0.677] | 0.654 [0.469, 0.821] | 3.19 | 2.59 | no / no / yes | no / no / yes |

No variant passes under either rule. The decision turns on the false alarms.

* **The every-day component finds more onsets and pays for them in false alarms.** Under the flat rule the (a) and (c) variants
  flag 11 to 15 of 26 onsets against 13 or 14 for their parents (the 90% interval of the all-onset difference includes zero for every
  (a) and (c) variant, `compare.md` Table 1); under the weighted rule 13 to 18, against 13 to 16. Their worst false alarms per onset are 2.3 to 3.2 (flat) and
  2.2 to 2.6 (weighted) against a limit of 2, so tier 1 fails for all of them. The parents' own 1.35 to 1.88 (flat) is within it.
  On days that are not risk dates the component raises 22 to 98 flags a horizon at h = 1 to 5 (`compare.md`, Table 2); between
  a third and a half of them fall on a pressure day (the rest are false alarms by the judge's definition), and at any one horizon they
  catch at most 3 of the 13 onsets that fall on days that are not risk dates (6 at h = 1). **The recall gain from the component is not worth the false alarms it adds
  under the declared limit; it does not lift recall without raising them.**
* **Tier 5 now passes, tier 3 still fails.** The (a) and (c) variants are calibrated and ahead of climatology over the week-ahead window
  (tier 5 yes), which no parent is; calibration by regime (tier 3) fails for every row, parents included.
* **Paired against the parent** (Brier score on the +5 bp outcome, all days, positive favours the variant; 90% interval): h = 1,
  +0.0099 [+0.0018, +0.0194] for `risk_gbm+every_day`, and +0.0097 to +0.0122 with intervals above zero for the other (a) and (c)
  variants. At h = 3 and h = 5 the intervals include zero. This is largely arithmetic: the parent forecasts exactly 0 on a non-risk day and
  the component forecasts a small positive probability there. Against calendar climatology the (a) and (c) variants are better at every
  horizon shown (+0.0077 to +0.0236, intervals above zero); against persistence-logistic better at h = 1 (+0.0032 to +0.0085, one interval
  includes zero) and indistinguishable at h = 5. Split by regime and by day type: Table 3 of `compare.md` (h = 1 and h = 5) and Tables 2
  and 3 of `tables-*.md`.
* **The early-fit prior does nothing to the headline.** (b) changes the risk-date forecasts of the first refits only: 26 to 27 risk-date
  days at h = 1 (through 2018-12-31) and 31 at h = 2 to 5 (through 2019-04-30), the days served by a window of fewer than 40 pairs
  (`construction-gaps-result.md`, gap 4). No onset of 2018 is warned by any variant, before or after (0 of 4), nor of 2020 (0 of 2) or 2024
  (0 of 2). Its flags differ from the parent's later by a few days because the cut-off rule chooses each cut-off from the earlier forecasts.
  Recall at some lead 1 to 5 is identical to the parent's under the flat rule in every (b) row, and within one onset under the weighted rule.
  The gap the diagnostics found is real (the gradient-boosted fit was a constant there), but replacing the constant does not warn an
  onset: the judge's cut-off rule never flags while its training window holds no onset (`no_onsets: never_flag`), and this reading did not
  separate that from the fits being poor on a few pairs, as gap 4 already said.

Table 2. Onset recall by year, at some lead 1 to 5, flat rule (the years the directive calls out in bold). Parent, then `+every_day`
and `+every_day+early_prior`; `+early_prior` equals the parent in every cell shown. Full table with intervals: `compare.md`, Table 1.

| year | onsets | risk_gbm | +every_day | +every_day+early_prior | risk_logistic | +every_day | +every_day+early_prior | risk_quantile_skewt_base | +every_day | +every_day+early_prior |
|---|---|---|---|---|---|---|---|---|---|---|
| **2018** | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2019 | 13 | 10 | 13 | 13 | 10 | 11 | 13 | 10 | 12 | 12 |
| **2020** | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| **2024** | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2025 | 5 | 3 | 2 | 2 | 4 | 2 | 2 | 4 | 2 | 1 |

(2021 to 2023 have no onset.) The `_base` twins are in `compare.md`; their pattern is the same. The gain is in 2019, on ordinary days
(`risk_gbm+every_day`: 7 of 12 ordinary-day onsets against 4 of 12); it is paid back in 2025, where the component's cut-off displaces the
parent's, and quarter-end onsets fall from 2 of 3 to 1 of 3. By regime and day type, with intervals: `compare.md`.

## Which of the 11 missed episodes are now warned

Using the post-mortem's table (`docs/pivot/episode-post-mortem-result.md`; 26 episodes, 11 missed by all five parents, none of which any
parent warns at some lead 1 to 5). Flat-rule cut-offs, as `compare.md` Table 4 gives for all 26.

| variant | newly warned of the 11 |
|---|---|
| `risk_gbm+every_day`, `risk_gbm_base+every_day`, and both `+every_day+early_prior` | 2019-05-28, 2019-06-25, 2019-08-13 |
| `risk_logistic+every_day` | 2019-06-25, 2019-08-13 |
| `risk_logistic+every_day+early_prior`, `risk_logistic_base+every_day+early_prior` | 2019-05-28, 2019-06-25, 2019-08-13 |
| `risk_logistic_base+every_day` | 2019-05-28, 2019-08-13 |
| `risk_quantile_skewt_base+every_day` | 2019-05-28, 2019-06-25, 2019-08-13 and 2020-03-12 |
| `risk_quantile_skewt_base+every_day+early_prior` | 2019-05-28, 2019-06-25, 2019-08-13 |
| every `+early_prior` | none |

Every episode newly warned is an ordinary day of 2019 (the three the all-inputs gradient-boosted model also reaches, `all-inputs-result.md`), plus
2020-03-12 once, by one variant. **Nothing warns an episode of 2018, 2020-03-04, or the two of 2024** (2024-09-30 and 2024-12-26); five of the eleven are classed "no signal in the panel" by the post-mortem and stay out of reach of any
reading of these inputs.

## What this does not say

* The component, the combination rule, the minimum of 40 and the prior weight of 2 are single declared choices. A component fitted on
  more inputs, one with its own cut-off, a different combination (a maximum, a product), or another small-window estimator was not tried,
  and this reading says nothing about them. The "(a) works at a different false-alarm price" reading is for this component and this cut-off rule
  only: one cut-off per threshold serves risk dates and other days alike, and a separate cut-off for the days the component serves
  would be a rule change.
* 26 onsets: one onset moves recall by about 0.04; the year cells rest on 2 to 13. Recall differences against the parent have intervals that
  include zero, except where the table says otherwise.
* The cut-offs are the judge's, chosen from each variant's own earlier forecasts; the weighted rule is the draft of `metadata/weighted_miss.json`
  as the judge applies it with `--rule weighted`, not a rule in force.
* No multiple-testing correction over 15 variants.
* The 2026 days, the +10 bp tiers and the confirmation window are not looked at.

## For Eleonora

No variant passes the full rule, so there is no publishing question and no "Publish?" issue; the inputs and the variants stay off in the
published declaration. Nothing here changes a rule, a threshold, an onset definition or a published figure.
