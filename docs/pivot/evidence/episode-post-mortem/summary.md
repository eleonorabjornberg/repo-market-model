# Episode post-mortem (#474)

26 +5 bp episodes (onsets scored at every horizon h = 1 to 5), 2018-06-29 to 2025-12-31; published panel `4ddc3882…`. Descriptive only.

Table 1. Warned at lead >= 1 (a flag at some horizon h = 1 to 5 for the start day), by model, and the cause of each miss.

| model | warned | missed | signal present, under the cut-off | signal too late for the lead rule | no signal in the panel | missed while silent (probability 0) |
|---|---|---|---|---|---|---|
| risk_gbm | 13 of 26 | 13 | 0 | 5 | 8 | 6 |
| risk_gbm_base | 14 of 26 | 12 | 0 | 4 | 8 | 6 |
| risk_logistic | 14 of 26 | 12 | 1 | 4 | 7 | 6 |
| risk_logistic_base | 13 of 26 | 13 | 1 | 4 | 8 | 6 |
| risk_quantile_skewt_base | 14 of 26 | 12 | 2 | 5 | 5 | 6 |

Warned by at least one of the five: 15 of 26. Missed by all five: 11, by cause (best of the five): signal present, under the cut-off: 1; signal too late for the lead rule: 5; no signal in the panel: 5.

Table 2. Episodes by regime and pressure-day type: episodes, missed by all five, warned by each model.

| group | episodes | missed by all five | risk_gbm | risk_gbm_base | risk_logistic | risk_logistic_base | risk_quantile_skewt_base |
|---|---|---|---|---|---|---|---|
| regime: 2018-19 | 17 | 7 | 10 | 10 | 10 | 10 | 10 |
| regime: 2020 | 2 | 2 | 0 | 0 | 0 | 0 | 0 |
| regime: 2024 | 2 | 2 | 0 | 0 | 0 | 0 | 0 |
| regime: 2025-26 | 5 | 0 | 3 | 4 | 4 | 3 | 4 |
| day_type: month_end | 6 | 2 | 4 | 4 | 4 | 4 | 4 |
| day_type: ordinary | 12 | 7 | 4 | 5 | 4 | 4 | 4 |
| day_type: quarter_end | 3 | 1 | 2 | 2 | 2 | 2 | 2 |
| day_type: tax_date | 5 | 1 | 3 | 3 | 4 | 3 | 4 |

Table 3. Every episode: regime, pressure-day type, the models that warned (horizons flagged), and for a miss its cause.

| start | regime | type | risk_gbm | risk_gbm_base | risk_logistic | risk_logistic_base | risk_quantile_skewt_base |
|---|---|---|---|---|---|---|---|
| 2018-11-15 | 2018-19 | ordinary | missed: no signal in the panel | missed: no signal in the panel | missed: no signal in the panel | missed: no signal in the panel | missed: no signal in the panel |
| 2018-11-30 | 2018-19 | month_end | missed: no signal in the panel | missed: no signal in the panel | missed: no signal in the panel | missed: no signal in the panel | missed: signal present, under the cut-off |
| 2018-12-17 | 2018-19 | tax_date | missed: no signal in the panel | missed: no signal in the panel | missed: no signal in the panel | missed: no signal in the panel | missed: no signal in the panel |
| 2018-12-28 | 2018-19 | month_end | missed: no signal in the panel | missed: no signal in the panel | missed: no signal in the panel | missed: no signal in the panel | missed: no signal in the panel |
| 2019-01-15 | 2018-19 | ordinary | warned h=1 | warned h=1 | warned h=1 | warned h=1 | warned h=1 |
| 2019-01-31 | 2018-19 | month_end | warned h=1 | warned h=1 | warned h=1 | warned h=1 | warned h=1,3,4,5 |
| 2019-02-28 | 2018-19 | month_end | warned h=1,2,3,4,5 | warned h=1,2,3,4,5 | warned h=1,4,5 | warned h=1,5 | warned h=1,2,4,5 |
| 2019-03-15 | 2018-19 | ordinary | warned h=1 | warned h=1 | warned h=1 | warned h=1 | warned h=1 |
| 2019-03-29 | 2018-19 | quarter_end | warned h=1,2,3,4,5 | warned h=1,2,3,4,5 | warned h=1,2,3,4,5 | warned h=1,2,3,4,5 | warned h=1,2,3,4,5 |
| 2019-05-28 | 2018-19 | ordinary | missed: signal too late for the lead rule (silent) | missed: signal too late for the lead rule (silent) | missed: signal too late for the lead rule (silent) | missed: signal too late for the lead rule (silent) | missed: signal too late for the lead rule (silent) |
| 2019-06-17 | 2018-19 | tax_date | warned h=1,2,3,4,5 | warned h=1,2,3,4,5 | warned h=1,2,3,4,5 | warned h=1,2,3,4,5 | warned h=1,2,3,4,5 |
| 2019-06-25 | 2018-19 | ordinary | missed: signal too late for the lead rule (silent) | missed: signal too late for the lead rule (silent) | missed: signal too late for the lead rule (silent) | missed: signal too late for the lead rule (silent) | missed: signal too late for the lead rule (silent) |
| 2019-08-13 | 2018-19 | ordinary | missed: signal too late for the lead rule (silent) | missed: signal too late for the lead rule (silent) | missed: signal too late for the lead rule (silent) | missed: signal too late for the lead rule (silent) | missed: signal too late for the lead rule (silent) |
| 2019-08-30 | 2018-19 | month_end | warned h=1,2,3,4,5 | warned h=1,2,3,4,5 | warned h=1,2,3,4,5 | warned h=1,2,3,4,5 | warned h=1,2,3,4,5 |
| 2019-10-15 | 2018-19 | ordinary | warned h=1 | warned h=1 | warned h=1 | warned h=1 | warned h=1 |
| 2019-11-29 | 2018-19 | month_end | warned h=1,2,3,4,5 | warned h=1,2,3,4,5 | warned h=1,2,3,4,5 | warned h=1,2,3,4,5 | warned h=1,2,3,4,5 |
| 2019-12-16 | 2018-19 | tax_date | warned h=1,2,3,4,5 | warned h=1,2,3,4,5 | warned h=1,2,3,4,5 | warned h=1,2,3,4,5 | warned h=1,2,3,4,5 |
| 2020-03-04 | 2020 | ordinary | missed: no signal in the panel (silent) | missed: no signal in the panel (silent) | missed: no signal in the panel (silent) | missed: no signal in the panel (silent) | missed: no signal in the panel (silent) |
| 2020-03-12 | 2020 | ordinary | missed: signal too late for the lead rule (silent) | missed: signal too late for the lead rule (silent) | missed: signal too late for the lead rule (silent) | missed: signal too late for the lead rule (silent) | missed: signal too late for the lead rule (silent) |
| 2024-09-30 | 2024 | quarter_end | missed: no signal in the panel | missed: no signal in the panel | missed: no signal in the panel | missed: no signal in the panel | missed: no signal in the panel |
| 2024-12-26 | 2024 | ordinary | missed: no signal in the panel (silent) | missed: no signal in the panel (silent) | missed: no signal in the panel (silent) | missed: no signal in the panel (silent) | missed: signal too late for the lead rule (silent) |
| 2025-09-15 | 2025-26 | tax_date | missed: signal too late for the lead rule | missed: no signal in the panel | warned h=4 | missed: no signal in the panel | warned h=2,3 |
| 2025-09-30 | 2025-26 | quarter_end | warned h=1,2 | warned h=2 | warned h=1,2,3,4,5 | warned h=1,2,4,5 | warned h=1,2,3,4,5 |
| 2025-10-15 | 2025-26 | ordinary | missed: no signal in the panel | warned h=1 | missed: signal present, under the cut-off | missed: signal present, under the cut-off | missed: signal present, under the cut-off |
| 2025-12-15 | 2025-26 | tax_date | warned h=1,2,3,4,5 | warned h=1,2,3,4,5 | warned h=1,2,3,4,5 | warned h=1,3,4,5 | warned h=1,2,3,4,5 |
| 2025-12-26 | 2025-26 | ordinary | warned h=1 | warned h=1 | warned h=1 | warned h=1 | warned h=1 |

Table 4. Missed episodes: panel inputs that moved in the 10 scored days before the start (as-of values; |change| >= 2 trailing sd of 10-day changes), and inputs whose start-day level lies outside the range over the false alarms of the same regime (flagged non-pressure days at h = 1 by any of the five); the count expected by chance beside it.

| start | regime | missed by | false alarms (regime) | inputs that moved | inputs outside the false alarms' range | expected by chance |
|---|---|---|---|---|---|---|
| 2018-11-15 | 2018-19 | 5 of 5 | 25 | – | treasury_settlement | 1.2 |
| 2018-11-30 | 2018-19 | 5 of 5 | 25 | tbill_4w | treasury_settlement_coupons | 1.2 |
| 2018-12-17 | 2018-19 | 5 of 5 | 25 | – | – | 1.2 |
| 2018-12-28 | 2018-19 | 5 of 5 | 25 | sofr_volume, tgcr, tbill_4w | tgcr | 1.2 |
| 2019-05-28 | 2018-19 | 5 of 5 | 25 | – | – | 1.2 |
| 2019-06-25 | 2018-19 | 5 of 5 | 25 | tbill_4w | on_rrp | 1.2 |
| 2019-08-13 | 2018-19 | 5 of 5 | 25 | tgcr | tga_daily | 1.2 |
| 2020-03-04 | 2020 | 5 of 5 | 32 | sofr_volume, tbill_4w | sofr_volume, sofr_p99_iorb_bps | 0.9 |
| 2020-03-12 | 2020 | 5 of 5 | 32 | sofr_volume, tbill_4w | spread_bps, sofr_volume, sofr_p75_iorb_bps | 0.9 |
| 2024-09-30 | 2024 | 5 of 5 | 2 | sofr_volume, tgcr, tbill_4w | – | – |
| 2024-12-26 | 2024 | 5 of 5 | 2 | spread_bps, tgcr | – | – |
| 2025-09-15 | 2025-26 | 3 of 5 | 7 | – | – | 3.8 |
| 2025-10-15 | 2025-26 | 4 of 5 | 7 | treasury_settlement | tga_daily | 3.8 |
