Table 1. What the onset rule treats as the event (tier 1, lead >= 1, +5 bp, forecasts and cut-offs as declared).
Onsets flagged at some horizon 1 to 5 / events; worst false alarms per onset; recall with its 90% interval.

| model | event | flagged / events | false alarms per onset | recall [90% interval] |
|---|---|---|---|---|
| risk_gbm | declared onsets | 13/26 | 1.35 | 0.500 [0.310, 0.667] |
| risk_gbm | each episode's largest day | 14/26 | 1.35 | 0.538 [0.348, 0.708] |
| risk_gbm | every day above +10 bp | 23/60 | 0.58 | 0.383 [0.275, 0.500] |
| risk_gbm_base | declared onsets | 14/26 | 1.50 | 0.538 [0.360, 0.719] |
| risk_gbm_base | each episode's largest day | 14/26 | 1.50 | 0.538 [0.375, 0.714] |
| risk_gbm_base | every day above +10 bp | 25/60 | 0.65 | 0.417 [0.308, 0.527] |
| risk_logistic | declared onsets | 14/26 | 1.85 | 0.538 [0.350, 0.724] |
| risk_logistic | each episode's largest day | 15/26 | 1.85 | 0.577 [0.406, 0.750] |
| risk_logistic | every day above +10 bp | 25/60 | 0.80 | 0.417 [0.311, 0.531] |
| risk_logistic_base | declared onsets | 13/26 | 1.77 | 0.500 [0.333, 0.680] |
| risk_logistic_base | each episode's largest day | 14/26 | 1.77 | 0.538 [0.360, 0.704] |
| risk_logistic_base | every day above +10 bp | 24/60 | 0.77 | 0.400 [0.290, 0.511] |
| risk_quantile_skewt_base | declared onsets | 14/26 | 1.88 | 0.538 [0.360, 0.714] |
| risk_quantile_skewt_base | each episode's largest day | 15/26 | 1.88 | 0.577 [0.400, 0.750] |
| risk_quantile_skewt_base | every day above +10 bp | 25/60 | 0.82 | 0.417 [0.318, 0.532] |

Table 2. Named days of the largest stress, under the declared onset rule.

| day | spread (bp) | an onset? | the episode it belongs to opens on | the episode's largest day? |
|---|---|---|---|---|
| 2019-09-16 | 33.0 | no | 2019-08-30 | no |
| 2019-09-17 | 315.0 | no | 2019-08-30 | yes |
| 2019-09-30 | 55.0 | no | 2019-08-30 | no |
| 2020-03-16 | 16.0 | no | 2020-03-12 | no |
| 2020-03-17 | 44.0 | no | 2020-03-12 | yes |

Table 3. The episodes: onset, its spread, the episode's largest day and its spread.

| onset | onset spread (bp) | event days | largest day | its spread (bp) |
|---|---|---|---|---|
| 2018-06-29 | 17.0 | 2 | 2018-06-29 | 17.0 |
| 2018-11-15 | 8.0 | 2 | 2018-11-15 | 8.0 |
| 2018-11-30 | 8.0 | 4 | 2018-12-06 | 14.0 |
| 2018-12-17 | 11.0 | 3 | 2018-12-18 | 12.0 |
| 2018-12-28 | 6.0 | 4 | 2019-01-02 | 75.0 |
| 2019-01-15 | 6.0 | 1 | 2019-01-15 | 6.0 |
| 2019-01-31 | 18.0 | 2 | 2019-01-31 | 18.0 |
| 2019-02-28 | 18.0 | 1 | 2019-02-28 | 18.0 |
| 2019-03-15 | 6.0 | 2 | 2019-03-20 | 7.0 |
| 2019-03-29 | 25.0 | 26 | 2019-04-30 | 36.0 |
| 2019-05-28 | 6.0 | 2 | 2019-05-31 | 14.0 |
| 2019-06-17 | 6.0 | 1 | 2019-06-17 | 6.0 |
| 2019-06-25 | 6.0 | 23 | 2019-07-05 | 24.0 |
| 2019-08-13 | 6.0 | 2 | 2019-08-15 | 8.0 |
| 2019-08-30 | 6.0 | 15 | 2019-09-17 | 315.0 |
| 2019-10-15 | 20.0 | 9 | 2019-10-16 | 25.0 |
| 2019-11-29 | 10.0 | 2 | 2019-11-29 | 10.0 |
| 2019-12-16 | 7.0 | 1 | 2019-12-16 | 7.0 |
| 2020-03-04 | 13.0 | 1 | 2020-03-04 | 13.0 |
| 2020-03-12 | 10.0 | 3 | 2020-03-17 | 44.0 |
| 2024-09-30 | 6.0 | 2 | 2024-10-01 | 15.0 |
| 2024-12-26 | 13.0 | 3 | 2024-12-26 | 13.0 |
| 2025-09-15 | 11.0 | 1 | 2025-09-15 | 11.0 |
| 2025-09-30 | 9.0 | 1 | 2025-09-30 | 9.0 |
| 2025-10-15 | 14.0 | 22 | 2025-10-31 | 32.0 |
| 2025-12-15 | 10.0 | 1 | 2025-12-15 | 10.0 |
| 2025-12-26 | 11.0 | 4 | 2025-12-31 | 22.0 |

Table 4. Missed onsets that fell under the cut-off by less than 10% of it, by year (missed under the margin / missed in all / onsets). Any horizon: caught if flagged at some horizon 1 to 5; its margin is the smallest.

risk_gbm

| reading | 2018 | 2019 | 2020 | 2024 | 2025 | all |
|---|---|---|---|---|---|---|
| any horizon | 0 / 5 / 5 | 0 / 3 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 2 / 5 | 0 / 14 / 27 |
| h = 1 | 0 / 5 / 5 | 0 / 3 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 2 / 5 | 0 / 14 / 27 |
| h = 2 | 0 / 4 / 4 | 0 / 7 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 3 / 5 | 0 / 18 / 26 |
| h = 3 | 0 / 4 / 4 | 0 / 7 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 4 / 5 | 0 / 19 / 26 |
| h = 4 | 0 / 4 / 4 | 0 / 7 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 4 / 5 | 0 / 19 / 26 |
| h = 5 | 0 / 4 / 4 | 0 / 7 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 4 / 5 | 0 / 19 / 26 |
Of the 89 misses over the five horizons, 46 were at a probability of exactly 0.

risk_gbm_base

| reading | 2018 | 2019 | 2020 | 2024 | 2025 | all |
|---|---|---|---|---|---|---|
| any horizon | 0 / 5 / 5 | 0 / 3 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 1 / 5 | 0 / 13 / 27 |
| h = 1 | 0 / 5 / 5 | 0 / 3 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 2 / 5 | 0 / 14 / 27 |
| h = 2 | 0 / 4 / 4 | 0 / 7 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 3 / 5 | 0 / 18 / 26 |
| h = 3 | 0 / 4 / 4 | 0 / 7 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 4 / 5 | 0 / 19 / 26 |
| h = 4 | 0 / 4 / 4 | 0 / 7 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 4 / 5 | 0 / 19 / 26 |
| h = 5 | 0 / 4 / 4 | 0 / 7 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 4 / 5 | 0 / 19 / 26 |
Of the 89 misses over the five horizons, 46 were at a probability of exactly 0.

risk_logistic

| reading | 2018 | 2019 | 2020 | 2024 | 2025 | all |
|---|---|---|---|---|---|---|
| any horizon | 0 / 5 / 5 | 0 / 3 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 1 / 5 | 0 / 13 / 27 |
| h = 1 | 0 / 5 / 5 | 0 / 3 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 2 / 5 | 0 / 14 / 27 |
| h = 2 | 0 / 4 / 4 | 0 / 8 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 3 / 5 | 0 / 19 / 26 |
| h = 3 | 0 / 4 / 4 | 0 / 8 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 1 / 3 / 5 | 1 / 19 / 26 |
| h = 4 | 0 / 4 / 4 | 0 / 7 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 2 / 5 | 0 / 17 / 26 |
| h = 5 | 0 / 4 / 4 | 0 / 7 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 3 / 5 | 0 / 18 / 26 |
Of the 87 misses over the five horizons, 46 were at a probability of exactly 0.

risk_logistic_base

| reading | 2018 | 2019 | 2020 | 2024 | 2025 | all |
|---|---|---|---|---|---|---|
| any horizon | 0 / 5 / 5 | 0 / 3 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 2 / 5 | 0 / 14 / 27 |
| h = 1 | 0 / 5 / 5 | 0 / 3 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 2 / 5 | 0 / 14 / 27 |
| h = 2 | 0 / 4 / 4 | 0 / 8 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 4 / 5 | 0 / 20 / 26 |
| h = 3 | 0 / 4 / 4 | 0 / 8 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 4 / 5 | 0 / 20 / 26 |
| h = 4 | 0 / 4 / 4 | 0 / 8 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 3 / 5 | 0 / 19 / 26 |
| h = 5 | 0 / 4 / 4 | 0 / 7 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 3 / 5 | 0 / 18 / 26 |
Of the 91 misses over the five horizons, 46 were at a probability of exactly 0.

risk_quantile_skewt_base

| reading | 2018 | 2019 | 2020 | 2024 | 2025 | all |
|---|---|---|---|---|---|---|
| any horizon | 0 / 5 / 5 | 0 / 3 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 1 / 5 | 0 / 13 / 27 |
| h = 1 | 0 / 5 / 5 | 0 / 3 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 2 / 5 | 0 / 14 / 27 |
| h = 2 | 0 / 4 / 4 | 0 / 7 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 2 / 5 | 0 / 17 / 26 |
| h = 3 | 0 / 4 / 4 | 0 / 7 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 2 / 5 | 0 / 17 / 26 |
| h = 4 | 0 / 4 / 4 | 0 / 6 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 3 / 5 | 0 / 17 / 26 |
| h = 5 | 0 / 4 / 4 | 0 / 6 / 13 | 0 / 2 / 2 | 0 / 2 / 2 | 0 / 3 / 5 | 0 / 17 / 26 |
Of the 82 misses over the five horizons, 49 were at a probability of exactly 0.

Table 5. Tier 1's "above climatology" test, as declared and paired (lead >= 1, declared onsets).
Declared: the lower bound of the recall interval above climatology's recall. Paired: the lower bound of the interval of the paired recall difference above zero.

| model | recall [lower] | climatology recall | declared test | recall difference [90% interval] | paired test |
|---|---|---|---|---|---|
| risk_gbm | 0.500 [0.310] | 0.115 | passes | 0.385 [0.214, 0.556] | passes |
| risk_gbm_base | 0.538 [0.360] | 0.154 | passes | 0.385 [0.208, 0.572] | passes |
| risk_logistic | 0.538 [0.350] | 0.192 | passes | 0.346 [0.167, 0.529] | passes |
| risk_logistic_base | 0.500 [0.333] | 0.192 | passes | 0.308 [0.150, 0.481] | passes |
| risk_quantile_skewt_base | 0.538 [0.360] | 0.192 | passes | 0.346 [0.167, 0.526] | passes |

Table 6. Onsets under other readings of the label.

| label | count | added | dropped |
|---|---|---|---|
| declared: whole basis points, strictly above +5 (round(spread) > 5) | 27 | none | none |
| float_5: the unrounded float spread, strictly above +5 | 25 | 2018-09-17 | 2019-01-15, 2019-10-15, 2025-12-15 |
| cut_4.5: the unrounded spread strictly above +4.5 | 27 | 2018-09-17, 2018-09-28, 2018-11-02, 2019-08-27, 2025-06-30 | 2019-01-15, 2019-08-30, 2019-10-15, 2020-03-12, 2025-12-15 |
| cut_5.5: the unrounded spread strictly above +5.5 | 27 | none | none |
| whole_bp_6: whole basis points, strictly above +6 (one whole basis point higher) | 29 | 2018-12-31, 2019-03-20, 2019-04-15, 2019-04-29, 2019-05-31, 2019-06-26, 2019-08-15, 2019-09-03, 2019-10-31, 2024-10-01, 2025-11-25 | 2018-12-28, 2019-01-15, 2019-03-15, 2019-05-28, 2019-06-17, 2019-06-25, 2019-08-13, 2019-08-30, 2024-09-30 |

Days not on a whole basis point: 0. Days at exactly +5 bp: 36 (by year {'2018': 4, '2019': 24, '2020': 1, '2025': 7}); at exactly +6 bp: 30 (by year {'2018': 2, '2019': 23, '2024': 2, '2025': 3}); days at +5 bp whose float spread is above 5: 18.

Table 7. Tier 1 under each label (forecasts and cut-offs kept; the +5 bp outcome and the onsets re-derived).

| model | label | flagged / onsets | false alarms per onset | recall [90% interval] |
|---|---|---|---|---|
| risk_gbm | float_5 | 10/24 | 1.46 | 0.417 [0.231, 0.600] |
| risk_gbm_base | float_5 | 11/24 | 1.62 | 0.458 [0.286, 0.652] |
| risk_logistic | float_5 | 11/24 | 2.00 | 0.458 [0.278, 0.650] |
| risk_logistic_base | float_5 | 10/24 | 1.92 | 0.417 [0.238, 0.600] |
| risk_quantile_skewt_base | float_5 | 11/24 | 2.04 | 0.458 [0.273, 0.636] |
| risk_gbm | cut_4.5 | 10/26 | 1.19 | 0.385 [0.212, 0.560] |
| risk_gbm_base | cut_4.5 | 11/26 | 1.35 | 0.423 [0.250, 0.607] |
| risk_logistic | cut_4.5 | 11/26 | 1.69 | 0.423 [0.250, 0.615] |
| risk_logistic_base | cut_4.5 | 10/26 | 1.62 | 0.385 [0.217, 0.562] |
| risk_quantile_skewt_base | cut_4.5 | 11/26 | 1.73 | 0.423 [0.240, 0.600] |
| risk_gbm | cut_5.5 | 13/26 | 1.35 | 0.500 [0.310, 0.667] |
| risk_gbm_base | cut_5.5 | 14/26 | 1.50 | 0.538 [0.360, 0.719] |
| risk_logistic | cut_5.5 | 14/26 | 1.85 | 0.538 [0.350, 0.724] |
| risk_logistic_base | cut_5.5 | 13/26 | 1.77 | 0.500 [0.333, 0.680] |
| risk_quantile_skewt_base | cut_5.5 | 14/26 | 1.88 | 0.538 [0.360, 0.714] |
| risk_gbm | whole_bp_6 | 16/28 | 1.46 | 0.571 [0.391, 0.742] |
| risk_gbm_base | whole_bp_6 | 17/28 | 1.61 | 0.607 [0.440, 0.769] |
| risk_logistic | whole_bp_6 | 17/28 | 1.93 | 0.607 [0.438, 0.775] |
| risk_logistic_base | whole_bp_6 | 16/28 | 1.86 | 0.571 [0.400, 0.739] |
| risk_quantile_skewt_base | whole_bp_6 | 17/28 | 1.96 | 0.607 [0.429, 0.778] |
