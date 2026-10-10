# How episodes and passes are defined: four sensitivity readings of tier 1 (#486)

A scratch measurement. It writes nothing into `docs/runs/` and moves no published figure, declaration or live pin. The judge, the onset rule, the +5 bp threshold, the tiers and the cut-off rule are as declared (`metadata/pressure_judge.json`); nothing is selected and no rule is changed. Scored days are 2018-06-29 to 2025-12-31 only (`docs/decisions/lockbox.md`); the 2026 days are not read. Evidence: `docs/pivot/evidence/episode-sensitivity/` (`sensitivity.json`, `tables.md`); the script is `scripts/episode_sensitivity.py`.

## What was scored

The five tier-1 passers of the risk-date severity model (`docs/pivot/risk-date-severity-result.md`): `risk_gbm`, `risk_gbm_base`, `risk_logistic`, `risk_logistic_base`, `risk_quantile_skewt_base`. Their forecasts at h = 1 to 5 and their cut-offs (chosen refit by refit by the declared rule) are never re-fitted: each reading changes what counts as the event or how the pass is tested, and nothing else. The declared tier 1 is reproduced first and equals the judge's line for each row in `docs/pivot/evidence/risk-date-severity/tables.md` (onsets flagged, recall and interval, worst false alarms per onset).

**What the sensitivities cannot say.** The models were trained and their cut-offs chosen on the declared labels. Under another label they are scored, not refitted, so a model refitted to that label could do better or worse. Everything below is exploratory: no paired test against a benchmark is run here, and the +5 bp onset count is small (26 scored onsets at lead >= 1), so one onset moves recall by about 0.04.

## Reproduce

Published panel `4ddc3882…` (`verify-panel` clean); scratch panels from `pressure_v1_1.py panel`, then `measurement_fields.py panel`; forecasts as in the risk-date severity page.

```
PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --output OUT/bench_h$h.json
PYTHONPATH=src python3 scripts/risk_date_severity.py run --panel AUG2.csv --published PUBLISHED.csv --horizon $h --candidate $row --output OUT/risk_${row}_h$h.json
PYTHONPATH=src python3 scripts/episode_sensitivity.py report --panel PUBLISHED.csv --bench 'OUT/bench_h{h}.json' \
    --rows 'OUT/risk_h{h}.json' --output sensitivity.json --markdown tables.md
```

`risk_h{h}.json` is the five rows' forecasts at horizon h merged into one file (the `--candidate` runs write one row each). Set `OMP_NUM_THREADS=1` when running several fits at once: with the default thread counts the gradient-boosted fits slow by orders of magnitude.

## 1. The onset rule absorbs the largest stress days

An onset is a day above +5 bp with none in the 5 panel rows before it. The days the directive names are all inside episodes opened earlier on small days:

| day | spread (bp) | an onset? | episode opens on | episode's largest day |
|---|---|---|---|---|
| 2019-09-16 | 33 | no | 2019-08-30 (+6 bp) | no |
| 2019-09-17 | 315 | no | 2019-08-30 | yes |
| 2019-09-30 | 55 | no | 2019-08-30 | no |
| 2020-03-16 | 16 | no | 2020-03-12 (+10 bp) | no |
| 2020-03-17 | 44 | no | 2020-03-12 | yes |

The 2019-08-30 episode holds 15 event days and 2019-09-17 is its peak. Table 3 of `tables.md` lists every episode with its onset, its largest day and their spreads.

Tier 1, lead >= 1, as declared, with each episode's largest day, and with every day above +10 bp, as the event (forecasts and cut-offs unchanged; flagged / events, recall with its 90% interval; false alarms per onset is the same count over the same days, per event):

| model | declared onsets | each episode's largest day | every day above +10 bp |
|---|---|---|---|
| risk_gbm | 13/26, 0.500 [0.310, 0.667] | 14/26, 0.538 [0.348, 0.708] | 23/60, 0.383 [0.275, 0.500] |
| risk_gbm_base | 14/26, 0.538 [0.360, 0.719] | 14/26, 0.538 [0.375, 0.714] | 25/60, 0.417 [0.308, 0.527] |
| risk_logistic | 14/26, 0.538 [0.350, 0.724] | 15/26, 0.577 [0.406, 0.750] | 25/60, 0.417 [0.311, 0.531] |
| risk_logistic_base | 13/26, 0.500 [0.333, 0.680] | 14/26, 0.538 [0.360, 0.704] | 24/60, 0.400 [0.290, 0.511] |
| risk_quantile_skewt_base | 14/26, 0.538 [0.360, 0.714] | 15/26, 0.577 [0.400, 0.750] | 25/60, 0.417 [0.318, 0.532] |

* **With each episode's largest day as the event, recall moves by at most one event (0 to +0.04) and every row still meets tier 1.** The peaks are no harder to warn than the onsets.
* **With every day above +10 bp as the event, recall falls to 0.38 to 0.42 and every row fails the recall criterion (0.5).** The false alarms per event fall (0.58 to 0.82) because the denominator is larger. This is a different question: it asks for a flag on each large day, not on the day a pressure episode opens, and a row is not designed to repeat its flag through an episode.

## 2. The cut-off sits at one past onset's probability

`select_cutoff` returns the probability at which the last onset in the training window was caught, so a test onset forecast just under that probability is missed by a hair. For each missed onset the margin is (cut-off − probability) / cut-off. Missed onsets under 10% of the cut-off, by year, per row and horizon, are in Table 4 of `tables.md`.

* **It almost never happens.** Over five rows, five horizons and 26 or 27 onsets each, one miss falls under the margin: `risk_logistic` at h = 3, in 2025. Read at any horizon (an onset flagged at some horizon is caught), none does, for any row or year.
* **Misses are far under the cut-off, or have none.** About half the misses are at a probability of exactly 0: a risk-date row forecasts 0 off its dates, so an onset on an ordinary day is a miss by 100%. The onsets of 2018 and the first of 2019 have no cut-off in the early refits (the declared rule flags nothing until a training window holds an onset caught within the limit): they are misses with no margin, counted apart in `sensitivity.json` (`no_cutoff`). Of the onsets missed at every horizon, the nearest to a cut-off miss it by 25% to 39% (`risk_logistic`, `risk_logistic_base`, `risk_quantile_skewt_base`, all 2025-10-15; `risk_quantile_skewt_base` also 2018-11-30 at 26%).
* So the placement of the cut-off at an onset's own probability does not cost these rows onsets by a hair. It does not say how often a different cut-off rule would choose differently.

## 3. Tier 1's "above climatology" test is not paired

Declared: the lower bound of the candidate's recall interval above climatology's recall point estimate. Paired: the lower bound of the interval of the paired recall difference above zero (computed in the same bootstrap and unused by the pass rule).

| model | recall [lower bound] | climatology recall | declared test | recall difference [90% interval] | paired test |
|---|---|---|---|---|---|
| risk_gbm | 0.500 [0.310] | 0.115 | passes | 0.385 [0.214, 0.556] | passes |
| risk_gbm_base | 0.538 [0.360] | 0.154 | passes | 0.385 [0.208, 0.572] | passes |
| risk_logistic | 0.538 [0.350] | 0.192 | passes | 0.346 [0.167, 0.529] | passes |
| risk_logistic_base | 0.500 [0.333] | 0.192 | passes | 0.308 [0.150, 0.481] | passes |
| risk_quantile_skewt_base | 0.538 [0.360] | 0.192 | passes | 0.346 [0.167, 0.526] | passes |

The two readings agree for all five rows, with a wide margin on both: climatology's recall is far below each row's lower bound, and the paired difference's lower bound is 0.15 to 0.21 above zero. Here the choice does not change a verdict.

## 4. The label flips on 1 bp

Whole-basis-point spreads: no scored day is off a whole basis point (to 1e-6), so a cut at +4.5 or +5.5 bp on the unrounded spread is a cut at whole +5 or +6 only through float noise. 36 days sit at exactly +5 bp (4 in 2018, 24 in 2019, 1 in 2020, 7 in 2025) and 30 at exactly +6 bp (2 in 2018, 23 in 2019, 2 in 2024, 3 in 2025). 18 of the 36 days at +5 bp have a float spread a hair above 5 (SOFR 2.00 less IORB 1.95 is 5.000000000000004 bp), so the raw float rule counts those and not the others.

| reading of "a day above the threshold" | onsets | added | dropped |
|---|---|---|---|
| declared: whole basis points, round(spread) > 5 | 27 | | |
| the unrounded float spread > 5 | 25 | 2018-09-17 | 2019-01-15, 2019-10-15, 2025-12-15 |
| the unrounded spread > 4.5 (days at +5 count) | 27 | 2018-09-17, 2018-09-28, 2018-11-02, 2019-08-27, 2025-06-30 | 2019-01-15, 2019-08-30, 2019-10-15, 2020-03-12, 2025-12-15 |
| the unrounded spread > 5.5 | 27 | none | none |
| whole basis points > 6 (one whole bp higher) | 29 | 11 days (Table 6 of `tables.md`) | 2018-12-28, 2019-01-15, 2019-03-15, 2019-05-28, 2019-06-17, 2019-06-25, 2019-08-13, 2019-08-30, 2024-09-30 |

2019-10-15 is an onset only because the days before it sat at exactly +5: with those days counted as events (a cut at +4.5, or the float rule on the days with noise above 5) it is not. The cut at +5.5 is the declared rule, because spreads are whole basis points.

Tier 1, lead >= 1, under each reading (forecasts and cut-offs unchanged; the +5 bp outcome and the onsets are re-derived; flagged / onsets, recall [90%], worst false alarms per onset):

| model | declared | float > 5 | > 4.5 | whole bp > 6 |
|---|---|---|---|---|
| risk_gbm | 13/26, 0.500, 1.35 | 10/24, 0.417 [0.231, 0.600], 1.46 | 10/26, 0.385 [0.212, 0.560], 1.19 | 16/28, 0.571 [0.391, 0.742], 1.46 |
| risk_gbm_base | 14/26, 0.538, 1.50 | 11/24, 0.458 [0.286, 0.652], 1.62 | 11/26, 0.423 [0.250, 0.607], 1.35 | 17/28, 0.607 [0.440, 0.769], 1.61 |
| risk_logistic | 14/26, 0.538, 1.85 | 11/24, 0.458 [0.278, 0.650], 2.00 | 11/26, 0.423 [0.250, 0.615], 1.69 | 17/28, 0.607 [0.438, 0.775], 1.93 |
| risk_logistic_base | 13/26, 0.500, 1.77 | 10/24, 0.417 [0.238, 0.600], 1.92 | 10/26, 0.385 [0.217, 0.562], 1.62 | 16/28, 0.571 [0.400, 0.739], 1.86 |
| risk_quantile_skewt_base | 14/26, 0.538, 1.88 | 11/24, 0.458 [0.273, 0.636], 2.04 | 11/26, 0.423 [0.240, 0.600], 1.73 | 17/28, 0.607 [0.429, 0.778], 1.96 |

* **The tier-1 verdict depends on the label.** Under the float spread and under the +4.5 cut every row falls under 0.5 recall and fails the recall criterion (and `risk_quantile_skewt_base` also exceeds 2 false alarms per onset under the float spread); one whole basis point higher, every row passes with a higher recall. The rows sit at 13 or 14 of 26 against a limit of 13: the verdict is a one-onset margin at the declared label.

## For Eleonora

Nothing here changes a rule or a published figure. Findings that would need a rule change:

1. **Episode definition.** The onset rule credits September 2019 and March 2020 to small days that opened the episodes. Scoring the episode's largest day instead moves no verdict. Scoring every day above +10 bp is a different (harder) question; whether either is a second headline reading is hers.
2. **Pairing.** Tier 1's "above climatology" test could use the paired recall difference. No verdict changes for these five rows; it would only matter for a row close to climatology.
3. **The label.** Whether the event is read on whole basis points or on the float spread, and whether +5 or +6 is the cut, moves the number of onsets by two to eleven and the tier-1 verdict of every row at once. The declared reading is whole basis points strictly above +5 (`docs/decisions/pressure-probability.md`, ruling of 2 October 2026 on #155); this page does not propose changing it.
4. **Cut-off placement.** Not a finding against these rows (above).
