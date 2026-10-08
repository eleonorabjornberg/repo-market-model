# A conditional predictor against climatology on the knowledge holdouts (#372)

**Reported only.** The test was declared before it was scored, in
[`conditional-vs-climatology-declaration.json`](conditional-vs-climatology-declaration.json), and it decides nothing.
No published figure and no record in `docs/runs/` moves, and the live record is not changed. The data is
[`studies/conditional_vs_climatology_holdout.json`](studies/conditional_vs_climatology_holdout.json), written by
`scripts/conditional_holdout.py`. The result file carries the declaration's sha256, and
`tests/test_conditional_holdout.py` fails if the declaration changes after it was scored.

```
PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output /tmp/funding_panel.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/conditional_holdout.py --panel /tmp/funding_panel.csv --journal /tmp/ch/journal.jsonl --output docs/pivot/studies/conditional_vs_climatology_holdout.json
```

The panel is the published one (digest `4ddc3882…`). The run takes seconds. No scored day is in a locked tier: the
windows are 2019-09-16 to 2019-09-20 and 2020-03-09 to 2020-03-20, and `lockbox.require_unlocked` checks them.

## What is scored

**Uncalibrated.** No published (calibrated) model is held out from these windows, because the published records
train on every crisis day once it is past. Every figure below is the uncalibrated conditional predictor, and none says
anything about the published model.

- **Predictors:** the gbm on the four features of `exceedance_gbm.json`, the gbm on the nine features of the funding
  declaration, and the frozen dynamic logit of #137 on its own features (no recalibration).
- **Benchmarks:** climatology and the persistence-logistic. For the leap, climatology is the pooled leap frequency
  among the training days, and the persistence-logistic is `onset.leap_persistence_logistic`, both declared.
- **Targets, at h = 1:** the +5 and +10 bp thresholds (whole basis points, strictly greater than) and the plain leap
  (a jump over the as-of anchor above 3 bp). A predictor's curve is requested at +5, +10 and each day's leap level, and
  read at the target's level.
- **Each window** is scored once per model with the crisis stripped from training and the as-of rule on every read
  (`event_eval.evaluate_event_window`). The 15 scored days are the two windows pooled, reported separately and never
  averaged into a main table.
- **Paired difference** is benchmark Brier minus predictor Brier, so positive favours the predictor, with a 90%
  stationary-bootstrap interval (mean block length 2, 2000 replications).
- **The declared rule** for a predictor at a target is met when the pooled interval is above zero against both
  benchmarks and no regime or pressure-day-type cell has its interval wholly below zero. It is not met when the pooled
  interval or such a cell is wholly below zero, and inconclusive otherwise. A cell with no interval is reported and does
  not count.

## Result, pooled over the 15 days

| Target | Predictor | Brier | Paired vs climatology | Paired vs persistence-logistic | Cells worse beyond their interval | Declared rule |
|---|---|---|---|---|---|---|
| +5 bp | gbm_published_4 | 0.215 | +0.127 (-0.038 to +0.304) | +0.041 (-0.039 to +0.135) | none | inconclusive |
| +5 bp | gbm_published_9 | 0.210 | +0.133 (-0.037 to +0.303) | +0.046 (-0.025 to +0.124) | none | inconclusive |
| +5 bp | dynamic_logit | 0.144 | +0.198 (+0.040 to +0.369) | +0.112 (+0.016 to +0.215) | none | met |
| +10 bp | gbm_published_4 | 0.271 | +0.073 (-0.045 to +0.202) | +0.017 (-0.018 to +0.055) | none | inconclusive |
| +10 bp | gbm_published_9 | 0.280 | +0.063 (-0.034 to +0.184) | +0.007 (-0.035 to +0.053) | 2020 vs climatology | not met |
| +10 bp | dynamic_logit | 0.207 | +0.136 (-0.012 to +0.297) | +0.081 (+0.002 to +0.174) | none | inconclusive |
| plain leap | gbm_published_4 | 0.407 | -0.080 (-0.131 to -0.031) | -0.047 (-0.077 to -0.017) | 2020 vs climatology; 2020 vs persistence-logistic; ordinary vs persistence-logistic | not met |
| plain leap | gbm_published_9 | 0.425 | -0.098 (-0.154 to -0.041) | -0.065 (-0.114 to -0.020) | 2020 vs climatology; 2020 vs persistence-logistic; ordinary vs persistence-logistic | not met |
| plain leap | dynamic_logit | 0.411 | -0.084 (-0.148 to -0.024) | -0.051 (-0.079 to -0.023) | 2020 vs persistence-logistic; ordinary vs persistence-logistic | not met |

Climatology and persistence-logistic Brier, by target (positive days of the 15):

| Target | Positive days | Climatology | Persistence-logistic |
|---|---|---|---|
| +5 bp | 8 of 15 | 0.343 | 0.256 |
| +10 bp | 6 of 15 | 0.343 | 0.288 |
| plain leap | 7 of 15 | 0.327 | 0.360 |

## What it shows

- **The frozen dynamic logit meets the declared rule at +5 bp, and nowhere else.** Its interval is above zero against both
  benchmarks at +5 bp, and it is above zero against the persistence-logistic at +10 bp, with the interval against
  climatology including zero there. This rests on 15 days from two episodes with 8 days above +5 bp. It is an
  extrapolation check, not evidence of skill, and the rule is not a publishing rule: the published model is not
  held out, so the holdout cannot be paired against the current published declaration on days before 2026-01-01.
  A separate issue carries the question of whether anything follows from it.
- **At +10 bp no predictor meets the rule.** The four-feature gbm and the dynamic logit are inconclusive. The nine-feature gbm
  trails climatology in the 2020 regime beyond its interval.
- **The gbm is inconclusive at +5 bp** against both benchmarks, as in #280: the point estimates favour it, the intervals
  include zero.
- **The plain leap fails for every predictor, against both benchmarks.** Every pooled interval is wholly below zero:
  the conditional predictors score worse than the pooled leap frequency and than the persistence-logistic, mostly in the
  2020 days and on ordinary days. Seven of the 15 days are leaps, in three bursts of consecutive days, which is a poor
  fit for a model trained on calm history.
- **The leap-onset group is empty.** The final test's leap-onset group is every day with no leap on the five previous
  panel days. The leaps in these windows come in runs, and no scored day in them is at risk of a leap onset by that
  definition (0 days, 0 events), so the group says nothing here. The +5 bp at-risk group (the onset group) holds one day
  and one event, and the one-day variant seven days and two events. Both are in the JSON and are descriptive.

The splits by regime and pressure-day type are in the JSON for every predictor, target and benchmark. The 2018-19 regime
(five days) and the tax-date day type (three days) have no bootstrap interval and are reported as means. The 2020 regime
and the ordinary day type are the cells with intervals.

## Not checked, or for Eleonora

- Whether the pass at +5 bp for the dynamic logit means anything for the published model. The published model is not
  held out from these windows, so this cannot be tested here.
- The 15 days are two episodes. Nothing here separates the predictors from the benchmarks beyond those episodes.
- A conditional model change comes after the diagnosis of why the exceedance curve flattens across thresholds (#373), not
  instead of it.
