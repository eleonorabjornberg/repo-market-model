### Gap 2: the declared forecast on onsets that are not risk dates

| onset | horizons at which it is not a risk date | forecasts read | largest forecast, either threshold |
|---|---|---|---|
| 2018-11-15 | 2, 3, 4, 5 | 40 | 0 |
| 2018-12-28 | 2, 3, 4, 5 | 40 | 0 |
| 2019-01-15 | 2, 3, 4, 5 | 40 | 0 |
| 2019-03-15 | 2, 3, 4, 5 | 40 | 0 |
| 2019-05-28 | 1, 2, 3, 4, 5 | 50 | 0 |
| 2019-06-25 | 1, 2, 3, 4, 5 | 50 | 0 |
| 2019-08-13 | 1, 2, 3, 4, 5 | 50 | 0 |
| 2019-10-15 | 2, 3, 4, 5 | 40 | 0 |
| 2020-03-04 | 1, 2, 3, 4, 5 | 50 | 0 |
| 2020-03-12 | 1, 2, 3, 4, 5 | 50 | 0 |
| 2024-12-26 | 1, 2, 3, 4, 5 | 50 | 0 |
| 2025-10-15 | 2, 3, 4, 5 | 40 | 0 |
| 2025-12-26 | 2, 3, 4, 5 | 40 | 0 |

### Gap 4: the declared fits through 2019

Per refit: risk-date training pairs, and the pressure (onset) labels among them at +5 and +10 bp.

risk_gbm_base, h = 1

| first served day | pairs | risk-date pairs | +5 bp events (onsets) | +10 bp events (onsets) | classifier |
|---|---|---|---|---|---|
| 2018-06-27 | 51 | 12 | 1 (1) | 0 (0) | constant (< 2 x min_samples_leaf) |
| 2018-07-27 | 72 | 16 | 3 (2) | 1 (1) | constant (< 2 x min_samples_leaf) |
| 2018-08-27 | 93 | 19 | 3 (2) | 1 (1) | constant (< 2 x min_samples_leaf) |
| 2018-09-26 | 114 | 25 | 3 (2) | 1 (1) | constant (< 2 x min_samples_leaf) |
| 2018-10-26 | 135 | 28 | 3 (2) | 1 (1) | constant (< 2 x min_samples_leaf) |
| 2018-11-28 | 156 | 33 | 4 (3) | 1 (1) | constant (< 2 x min_samples_leaf) |
| 2018-12-31 | 177 | 40 | 10 (6) | 4 (3) | can split |
| 2019-01-31 | 198 | 44 | 12 (8) | 5 (4) | can split |
| 2019-03-04 | 219 | 49 | 13 (9) | 6 (5) | can split |
| 2019-04-02 | 240 | 52 | 16 (11) | 7 (6) | can split |
| 2019-05-02 | 261 | 57 | 21 (11) | 8 (7) | can split |
| 2019-06-03 | 282 | 61 | 23 (11) | 10 (9) | can split |
| 2019-07-02 | 303 | 67 | 27 (12) | 11 (10) | can split |
| 2019-08-01 | 324 | 71 | 29 (12) | 13 (11) | can split |
| 2019-08-30 | 345 | 74 | 31 (13) | 13 (11) | can split |
| 2019-10-01 | 366 | 80 | 36 (13) | 17 (12) | can split |
| 2019-10-31 | 387 | 84 | 38 (14) | 19 (14) | can split |
| 2019-12-03 | 408 | 87 | 40 (15) | 19 (14) | can split |

risk_gbm_base, h = 5

| first served day | pairs | risk-date pairs | +5 bp events (onsets) | +10 bp events (onsets) | classifier |
|---|---|---|---|---|---|
| 2018-06-27 | 47 | 7 | 1 (1) | 0 (0) | constant (< 2 x min_samples_leaf) |
| 2018-07-27 | 68 | 9 | 2 (2) | 1 (1) | constant (< 2 x min_samples_leaf) |
| 2018-08-27 | 89 | 11 | 2 (2) | 1 (1) | constant (< 2 x min_samples_leaf) |
| 2018-09-26 | 110 | 17 | 2 (2) | 1 (1) | constant (< 2 x min_samples_leaf) |
| 2018-10-26 | 131 | 18 | 2 (2) | 1 (1) | constant (< 2 x min_samples_leaf) |
| 2018-11-28 | 152 | 22 | 2 (2) | 1 (1) | constant (< 2 x min_samples_leaf) |
| 2018-12-31 | 173 | 28 | 7 (4) | 4 (3) | constant (< 2 x min_samples_leaf) |
| 2019-01-31 | 194 | 31 | 8 (5) | 5 (4) | constant (< 2 x min_samples_leaf) |
| 2019-03-04 | 215 | 34 | 9 (6) | 6 (5) | constant (< 2 x min_samples_leaf) |
| 2019-04-02 | 236 | 35 | 10 (7) | 7 (6) | constant (< 2 x min_samples_leaf) |
| 2019-05-02 | 257 | 40 | 15 (7) | 8 (7) | can split |
| 2019-06-03 | 278 | 43 | 16 (7) | 9 (8) | can split |
| 2019-07-02 | 299 | 47 | 18 (8) | 10 (9) | can split |
| 2019-08-01 | 320 | 50 | 19 (8) | 11 (10) | can split |
| 2019-08-30 | 341 | 52 | 20 (9) | 11 (10) | can split |
| 2019-10-01 | 362 | 56 | 24 (9) | 15 (11) | can split |
| 2019-10-31 | 383 | 59 | 25 (9) | 16 (12) | can split |
| 2019-12-03 | 404 | 60 | 26 (10) | 16 (12) | can split |

Refits through 2019, by candidate and horizon: how many have fewer risk-date pairs than the leaf floor,

| model | h | refits | below the floor | first refit at or above it (pairs) | refits with no +5 bp event | refits with no +10 bp event |
|---|---|---|---|---|---|---|
| risk_gbm | 1 | 18 | 6 | 2018-12-31 (40) | 0 | 1 |
| risk_gbm | 2 | 18 | 10 | 2019-05-02 (42) | 0 | 1 |
| risk_gbm | 3 | 18 | 10 | 2019-05-02 (41) | 0 | 1 |
| risk_gbm | 4 | 18 | 10 | 2019-05-02 (40) | 0 | 1 |
| risk_gbm | 5 | 18 | 10 | 2019-05-02 (40) | 0 | 1 |
| risk_gbm_base | 1 | 18 | 6 | 2018-12-31 (40) | 0 | 1 |
| risk_gbm_base | 2 | 18 | 10 | 2019-05-02 (42) | 0 | 1 |
| risk_gbm_base | 3 | 18 | 10 | 2019-05-02 (41) | 0 | 1 |
| risk_gbm_base | 4 | 18 | 10 | 2019-05-02 (40) | 0 | 1 |
| risk_gbm_base | 5 | 18 | 10 | 2019-05-02 (40) | 0 | 1 |
| risk_logistic | 1 | 18 | 6 | 2018-12-31 (40) | 0 | 1 |
| risk_logistic | 2 | 18 | 10 | 2019-05-02 (42) | 0 | 1 |
| risk_logistic | 3 | 18 | 10 | 2019-05-02 (41) | 0 | 1 |
| risk_logistic | 4 | 18 | 10 | 2019-05-02 (40) | 0 | 1 |
| risk_logistic | 5 | 18 | 10 | 2019-05-02 (40) | 0 | 1 |
| risk_logistic_base | 1 | 18 | 6 | 2018-12-31 (40) | 0 | 1 |
| risk_logistic_base | 2 | 18 | 10 | 2019-05-02 (42) | 0 | 1 |
| risk_logistic_base | 3 | 18 | 10 | 2019-05-02 (41) | 0 | 1 |
| risk_logistic_base | 4 | 18 | 10 | 2019-05-02 (40) | 0 | 1 |
| risk_logistic_base | 5 | 18 | 10 | 2019-05-02 (40) | 0 | 1 |
| risk_quantile_skewt_base | 1 | 18 | 6 | 2018-12-31 (40) | - | - |
| risk_quantile_skewt_base | 2 | 18 | 10 | 2019-05-02 (42) | - | - |
| risk_quantile_skewt_base | 3 | 18 | 10 | 2019-05-02 (41) | - | - |
| risk_quantile_skewt_base | 4 | 18 | 10 | 2019-05-02 (40) | - | - |
| risk_quantile_skewt_base | 5 | 18 | 10 | 2019-05-02 (40) | - | - |

### Gap 1: the onset label

**+5 bp onsets flagged / onsets, false alarms per onset**

| model | h=1 declared | h=1 onset_label | h=2 declared | h=2 onset_label | h=3 declared | h=3 onset_label | h=4 declared | h=4 onset_label | h=5 declared | h=5 onset_label |
|---|---|---|---|---|---|---|---|---|---|---|
| risk_gbm | 13/27, 1.30 | 12/27, 0.56 | 8/26, 1.08 | 5/26, 1.15 | 7/26, 1.04 | 6/26, 0.69 | 7/26, 0.88 | 6/26, 0.73 | 7/26, 1.04 | 5/26, 1.08 |
| risk_gbm_base | 13/27, 1.44 | 11/27, 0.67 | 8/26, 0.96 | 7/26, 1.19 | 7/26, 1.27 | 5/26, 1.31 | 7/26, 1.12 | 6/26, 1.04 | 7/26, 1.08 | 5/26, 1.15 |
| risk_logistic | 13/27, 1.78 | 13/27, 1.67 | 7/26, 1.00 | 6/26, 1.00 | 7/26, 1.19 | 7/26, 1.12 | 9/26, 1.54 | 8/26, 1.31 | 8/26, 1.42 | 8/26, 1.27 |
| risk_logistic_base | 13/27, 1.70 | 13/27, 1.56 | 6/26, 1.00 | 5/26, 1.00 | 6/26, 1.00 | 7/26, 1.08 | 7/26, 1.12 | 8/26, 1.42 | 8/26, 1.15 | 8/26, 1.35 |

**h = 1, onsets flagged by year**

| model | variant | 2018 | 2019 | 2020 | 2024 | 2025 |
|---|---|---|---|---|---|---|
| risk_gbm | declared | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 |
| risk_gbm | onset_label | 0/5 | 10/13 | 0/2 | 0/2 | 2/5 |
| risk_gbm_base | declared | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 |
| risk_gbm_base | onset_label | 0/5 | 9/13 | 0/2 | 0/2 | 2/5 |
| risk_logistic | declared | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 |
| risk_logistic | onset_label | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 |
| risk_logistic_base | declared | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 |
| risk_logistic_base | onset_label | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 |
| risk_quantile_skewt_base | declared | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 |

### Gap 2: bill settlements as risk dates (h = 1)

**+5 bp onsets flagged / onsets, false alarms per onset**

| model | h=1 declared | h=1 bill_days |
|---|---|---|
| risk_gbm | 13/27, 1.30 | 9/27, 1.22 |
| risk_gbm_base | 13/27, 1.44 | 11/27, 1.44 |
| risk_logistic | 13/27, 1.78 | 9/27, 1.93 |
| risk_logistic_base | 13/27, 1.70 | 8/27, 1.56 |
| risk_quantile_skewt_base | 13/27, 1.81 | 9/27, 1.63 |

**h = 1, onsets flagged by year**

| model | variant | 2018 | 2019 | 2020 | 2024 | 2025 |
|---|---|---|---|---|---|---|
| risk_gbm | declared | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 |
| risk_gbm | bill_days | 0/5 | 7/13 | 0/2 | 0/2 | 2/5 |
| risk_gbm_base | declared | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 |
| risk_gbm_base | bill_days | 0/5 | 8/13 | 0/2 | 0/2 | 3/5 |
| risk_logistic | declared | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 |
| risk_logistic | bill_days | 0/5 | 9/13 | 0/2 | 0/2 | 0/5 |
| risk_logistic_base | declared | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 |
| risk_logistic_base | bill_days | 0/5 | 7/13 | 0/2 | 0/2 | 1/5 |
| risk_quantile_skewt_base | declared | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 |
| risk_quantile_skewt_base | bill_days | 0/5 | 8/13 | 0/2 | 0/2 | 1/5 |

### Gap 3: business-day month-end, quarter-end window

**calendar_bd: +5 bp onsets flagged / onsets, false alarms per onset**

| model | h=1 declared | h=1 calendar_bd | h=2 declared | h=2 calendar_bd | h=3 declared | h=3 calendar_bd | h=4 declared | h=4 calendar_bd | h=5 declared | h=5 calendar_bd |
|---|---|---|---|---|---|---|---|---|---|---|
| risk_gbm | 13/27, 1.30 | 9/27, 0.56 | 8/26, 1.08 | 6/26, 0.92 | 7/26, 1.04 | 7/26, 1.19 | 7/26, 0.88 | 8/26, 0.96 | 7/26, 1.04 | 6/26, 1.15 |
| risk_gbm_base | 13/27, 1.44 | 9/27, 0.59 | 8/26, 0.96 | 5/26, 1.15 | 7/26, 1.27 | 6/26, 1.15 | 7/26, 1.12 | 7/26, 1.35 | 7/26, 1.08 | 6/26, 1.19 |
| risk_logistic | 13/27, 1.78 | 13/27, 1.81 | 7/26, 1.00 | 5/26, 0.73 | 7/26, 1.19 | 5/26, 0.92 | 9/26, 1.54 | 7/26, 1.04 | 8/26, 1.42 | 5/26, 1.04 |
| risk_logistic_base | 13/27, 1.70 | 13/27, 1.56 | 6/26, 1.00 | 4/26, 0.81 | 6/26, 1.00 | 5/26, 0.96 | 7/26, 1.12 | 4/26, 0.92 | 8/26, 1.15 | 3/26, 0.88 |
| risk_quantile_skewt_base | 13/27, 1.81 | 13/27, 1.70 | 9/26, 1.65 | 5/26, 1.12 | 9/26, 1.50 | 6/26, 1.38 | 9/26, 1.12 | 8/26, 1.19 | 9/26, 1.04 | 7/26, 1.08 |

**calendar_wide: +5 bp onsets flagged / onsets, false alarms per onset**

| model | h=1 declared | h=1 calendar_wide | h=2 declared | h=2 calendar_wide | h=3 declared | h=3 calendar_wide | h=4 declared | h=4 calendar_wide | h=5 declared | h=5 calendar_wide |
|---|---|---|---|---|---|---|---|---|---|---|
| risk_gbm | 13/27, 1.30 | 14/27, 1.30 | 8/26, 1.08 | 6/26, 1.19 | 7/26, 1.04 | 7/26, 1.08 | 7/26, 0.88 | 7/26, 0.81 | 7/26, 1.04 | 8/26, 1.23 |
| risk_gbm_base | 13/27, 1.44 | 10/27, 0.74 | 8/26, 0.96 | 6/26, 1.50 | 7/26, 1.27 | 6/26, 1.12 | 7/26, 1.12 | 5/26, 1.04 | 7/26, 1.08 | 7/26, 1.35 |
| risk_logistic | 13/27, 1.78 | 14/27, 1.74 | 7/26, 1.00 | 3/26, 0.92 | 7/26, 1.19 | 5/26, 0.85 | 9/26, 1.54 | 6/26, 1.08 | 8/26, 1.42 | 5/26, 1.12 |
| risk_logistic_base | 13/27, 1.70 | 14/27, 1.63 | 6/26, 1.00 | 5/26, 1.04 | 6/26, 1.00 | 5/26, 1.04 | 7/26, 1.12 | 6/26, 1.23 | 8/26, 1.15 | 5/26, 0.88 |
| risk_quantile_skewt_base | 13/27, 1.81 | 13/27, 2.07 | 9/26, 1.65 | 3/26, 0.50 | 9/26, 1.50 | 4/26, 1.04 | 9/26, 1.12 | 7/26, 1.15 | 9/26, 1.04 | 7/26, 1.15 |

**h = 2, calendar_bd, onsets flagged by year**

| model | variant | 2018 | 2019 | 2020 | 2024 | 2025 |
|---|---|---|---|---|---|---|
| risk_gbm | declared | 0/4 | 6/13 | 0/2 | 0/2 | 2/5 |
| risk_gbm | calendar_bd | 0/4 | 5/13 | 0/2 | 0/2 | 1/5 |
| risk_gbm_base | declared | 0/4 | 6/13 | 0/2 | 0/2 | 2/5 |
| risk_gbm_base | calendar_bd | 0/4 | 5/13 | 0/2 | 0/2 | 0/5 |
| risk_logistic | declared | 0/4 | 5/13 | 0/2 | 0/2 | 2/5 |
| risk_logistic | calendar_bd | 0/4 | 4/13 | 0/2 | 0/2 | 1/5 |
| risk_logistic_base | declared | 0/4 | 5/13 | 0/2 | 0/2 | 1/5 |
| risk_logistic_base | calendar_bd | 0/4 | 4/13 | 0/2 | 0/2 | 0/5 |
| risk_quantile_skewt_base | declared | 0/4 | 6/13 | 0/2 | 0/2 | 3/5 |
| risk_quantile_skewt_base | calendar_bd | 0/4 | 4/13 | 0/2 | 0/2 | 1/5 |

Risk dates and onsets on them, by variant (h = 2; days scored, risk dates, onsets, onsets on risk dates):

| variant | days | risk dates | onsets | onsets on risk dates |
|---|---|---|---|---|
| declared | 1872 | 277 | 26 | 13 |
| calendar_bd | 1872 | 385 | 26 | 14 |
| calendar_wide | 1872 | 445 | 26 | 17 |

