# The eight onsets no scored model warns (#560)

Published panel `4ddc3882…`; 26 onsets on the shared grid; 57 model rows of the directive's families scored, and 19 other rows (the references, the every-day rows and the unselected quantile form). Onsets warned by no model row (computed): 2018-11-15, 2018-11-30, 2018-12-17, 2018-12-28, 2020-03-04, 2024-12-26; the directive's list DIFFERS FROM it (declared: 2018-11-15, 2018-11-30, 2018-12-17, 2018-12-28, 2020-03-04, 2020-03-12, 2024-09-30, 2024-12-26). Warned by no row at all, other rows included: 2018-11-15, 2018-11-30, 2018-12-17, 2018-12-28, 2020-03-04, 2024-12-26.

## Table 1. Verdict per onset

Verdict as declared (every row's near-cut-off probabilities count) and with the directive's model families only.

| onset | regime | type | model rows warning it | verdict | verdict, model families only | named (input, lead, z) |
|---|---|---|---|---|---|---|
| 2018-11-15 | 2018-19 | ordinary | 0 of 57 | signal public and unused | signal public and unused | treasury_settlement_soma (lead 1, z +5.4) |
| 2018-11-30 | 2018-19 | month_end | 0 of 57 | signal public and unused | signal public and unused | treasury_settlement_soma (lead 1, z +3.9); net_settlement_ahead (lead 1, z +5.3); net_settlement_ahead (lead 2, z +4.3); net_settlement_ahead (lead 3, z +3.4) |
| 2018-12-17 | 2018-19 | tax_date | 0 of 57 | signal public and too weak | signal public and too weak | treasury_settlement_coupons (lead 1, z +3.6) |
| 2018-12-28 | 2018-19 | month_end | 0 of 57 | no public signal found | no public signal found | - |
| 2020-03-04 | 2020 | ordinary | 0 of 57 | signal public and unused | signal public and unused | iorb_announced_change_bps (lead 1, z -157.2) |
| 2020-03-12 | 2020 | ordinary | 6 of 57 (latent_factor, latent_factor_logit, latent_factor_resid, ...) | signal public and too weak | signal public and too weak | spread_bps (lead 5, z +3.5); sofr_p75_iorb_bps (lead 5, z +3.0) |
| 2024-09-30 | 2024 | quarter_end | 5 of 57 (risk_logistic, risk_logistic+settle, risk_logistic+settle+h41, ...) | signal public and too weak | signal public and too weak | treasury_settlement_coupons (lead 1, z +3.8) |
| 2024-12-26 | 2024 | ordinary | 0 of 57 | signal public and unused | signal public and unused | ofr_tri_rate (lead 1, z -3.2); sofr (lead 1, z -3.1); ofr_tri_rate (lead 2, z -3.3); sofr (lead 2, z -3.2) |
| 2025-09-30 (contrast) | 2025-26 | quarter_end | 35 of 57 (ngboost_laplace, risk_gbm, risk_gbm+h41, ...) | signal public and too weak | signal public and too weak | treasury_settlement_coupons (lead 1, z +4.2) |
| 2025-12-15 (contrast) | 2025-26 | tax_date | 47 of 57 (ngboost_laplace, risk_gbm, risk_gbm+effr_pooled, ...) | signal public and unused | signal public and unused | sofr (lead 1, z -3.9); dealer_treasury_position (lead 2, z +3.2); dealer_treasury_position (lead 3, z +3.2); dealer_treasury_position (lead 4, z +3.2) |
| 2025-12-26 (contrast) | 2025-26 | ordinary | 37 of 57 (ngboost_laplace, risk_gbm, risk_gbm+effr_pooled, ...) | signal public and unused | signal public and unused | sofr (lead 1, z -3.9); ofr_tri_rate (lead 1, z -3.9); ofr_tri_rate (lead 2, z -4.2); sofr (lead 2, z -3.9) |

## Table 2. How often the bars are crossed on ordinary days (the base rate)

Descriptive, for reading Table 1: on the scored days of the regime that are not pressure days, the share with at least one input at |z| >= the bar (and with one no row reads), by lead.

| regime / lead | ordinary days | any input over the bar | an unused input over the bar |
|---|---|---|---|
| 2018-19/lead 1 | 271 | 16% | 9% |
| 2018-19/lead 2 | 271 | 13% | 7% |
| 2018-19/lead 3 | 271 | 10% | 6% |
| 2018-19/lead 4 | 271 | 13% | 8% |
| 2018-19/lead 5 | 271 | 12% | 7% |
| 2020/lead 1 | 247 | 15% | 10% |
| 2020/lead 2 | 247 | 9% | 7% |
| 2020/lead 3 | 247 | 9% | 8% |
| 2020/lead 4 | 247 | 9% | 8% |
| 2020/lead 5 | 247 | 9% | 8% |
| 2021-23/lead 1 | 748 | 14% | 5% |
| 2021-23/lead 2 | 748 | 7% | 1% |
| 2021-23/lead 3 | 748 | 6% | 1% |
| 2021-23/lead 4 | 748 | 7% | 1% |
| 2021-23/lead 5 | 748 | 7% | 1% |
| 2024/lead 1 | 245 | 17% | 9% |
| 2024/lead 2 | 245 | 11% | 6% |
| 2024/lead 3 | 245 | 11% | 6% |
| 2024/lead 4 | 245 | 11% | 6% |
| 2024/lead 5 | 245 | 11% | 6% |
| 2025-26/lead 1 | 220 | 20% | 12% |
| 2025-26/lead 2 | 220 | 15% | 9% |
| 2025-26/lead 3 | 220 | 15% | 9% |
| 2025-26/lead 4 | 220 | 15% | 8% |
| 2025-26/lead 5 | 220 | 14% | 7% |

## Table 2b. Cells with no cut-off in force (the cut-off is infinite: no probability can flag)

| regime | model-row cells (row x lead x day) | share with no cut-off |
|---|---|---|
| 2018-19 | 105735 | 36% |
| 2020 | 71535 | 0% |
| 2021-23 | 213180 | 0% |
| 2024 | 71250 | 0% |
| 2025-26 | 70965 | 0% |

| onset | cells with no cut-off | highest probabilities among them |
|---|---|---|
| 2018-11-15 | 285 of 285 | risk_quantile_skewt_base+settle lead 4 0.96 (above 98% of the regime's ordinary days), risk_quantile_skewt_base lead 1 0.94 (above 98% of the regime's ordinary days), risk_quantile_skewt_base+hurdle_isotonic lead 1 0.94 (above 95% of the regime's ordinary days) |
| 2018-11-30 | 277 of 285 | risk_quantile_skewt_base+h41 lead 5 1.00 (above 99% of the regime's ordinary days), structural_liquidity lead 3 0.96 (above 92% of the regime's ordinary days), structural_liquidity lead 4 0.91 (above 93% of the regime's ordinary days) |
| 2018-12-17 | 277 of 285 | risk_quantile_skewt_base+settle lead 3 1.00 (above 97% of the regime's ordinary days), risk_quantile_skewt_base+settle+h41 lead 4 1.00 (above 99% of the regime's ordinary days), risk_quantile_skewt_base+settle+h41 lead 5 1.00 (above 97% of the regime's ordinary days) |
| 2018-12-28 | 277 of 285 | risk_quantile_skewt_base+settle lead 5 0.81 (above 94% of the regime's ordinary days), risk_quantile_skewt_base+settle+h41 lead 5 0.49 (above 93% of the regime's ordinary days), risk_quantile_skewt_base+settle lead 3 0.46 (above 93% of the regime's ordinary days) |
| 2020-03-04 | 0 of 285 | - |
| 2020-03-12 | 0 of 285 | - |
| 2024-09-30 | 0 of 285 | - |
| 2024-12-26 | 0 of 285 | - |
| 2025-09-30 | 0 of 285 | - |
| 2025-12-15 | 0 of 285 | - |
| 2025-12-26 | 0 of 285 | - |

## Table 3. The ten largest moves per onset and lead (z against the regime's ordinary days)

### 2018-11-15 (2018-19, ordinary)

* lead 1 (decision 2018-11-14): treasury_settlement_soma +5.4, treasury_settlement +4.0, treasury_settlement_coupons +3.8, treasury_settlement_bills +2.6, tga_change_x_reserves +1.7, dealer_treasury_position -1.0, sofr_volume -1.0, bank_total_assets -0.9, tbill_13w +0.9, reserve_balances +0.8
* lead 2 (decision 2018-11-13): tga_daily_change +1.2, dealer_treasury_position -1.0, bank_total_assets -0.9, sofr_volume -0.8, reserve_balances +0.8, tbill_13w +0.8, on_rrp -0.6, tga_change_x_reserves +0.4, iorb +0.4, tga_daily +0.4 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 3 (decision 2018-11-09): bank_total_assets -1.0, dealer_treasury_position -1.0, tga_change_x_reserves -0.9, sofr_volume -0.9, tga +0.8, tbill_13w +0.7, reserve_balances +0.7, on_rrp -0.4, sofr_p1 +0.4, iorb +0.4 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 4 (decision 2018-11-08): dealer_treasury_position -1.1, bank_total_assets -1.0, tga_change_x_reserves -1.0, sofr_volume -0.9, tga +0.8, tbill_13w +0.8, reserve_balances +0.7, sofr_p75_iorb_bps -0.6, spread_bps -0.5, tbill_4w +0.5 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 5 (decision 2018-11-07): tga_change_x_reserves -1.3, dealer_treasury_position -1.1, sofr_volume -1.0, bank_total_assets -1.0, tga +0.8, tbill_13w +0.8, reserve_balances +0.6, tbill_4w +0.5, sofr_p25 +0.4, tgcr +0.4 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]

### 2018-11-30 (2018-19, month_end)

* lead 1 (decision 2018-11-29): treasury_settlement_coupons +6.6, treasury_settlement_soma +3.9, treasury_settlement +1.9, tga_change_x_reserves +1.6, tbill_13w +0.9, tbill_4w +0.8, sofr_volume -0.7, treasury_settlement_bills -0.7, bank_total_assets -0.6, tga_daily +0.5
* lead 2 (decision 2018-11-28): tbill_13w +0.9, tbill_4w +0.8, sofr_volume -0.8, on_rrp -0.6, bank_total_assets -0.6, tga_daily_change +0.5, tga_daily +0.5, sofr_p1 +0.4, tga_change_x_reserves -0.4, reserve_balances +0.4 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 3 (decision 2018-11-27): tga_daily_change +1.1, tbill_13w +1.0, sofr_volume -0.6, bank_total_assets -0.6, on_rrp -0.5, sofr_p1 +0.4, tga_change_x_reserves -0.4, reserve_balances +0.4, iorb +0.4, sofr_p99_iorb_sd15_bps -0.4 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 4 (decision 2018-11-26): on_rrp +1.0, tbill_13w +0.9, sofr_volume -0.9, bank_total_assets -0.8, reserve_balances +0.6, tga_daily_change -0.5, tbill_4w +0.5, sofr_p1 +0.4, sofr_p25 +0.4, tgcr +0.4 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 5 (decision 2018-11-23): on_rrp +1.4, tbill_13w +0.9, sofr_volume -0.9, bank_total_assets -0.8, reserve_balances +0.6, spread_bps -0.5, tbill_4w +0.5, tga_change_x_reserves +0.5, sofr_p75_iorb_bps -0.5, dealer_treasury_position -0.4 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]

### 2018-12-17 (2018-19, tax_date)

* lead 1 (decision 2018-12-14): treasury_settlement_coupons +3.6, tbill_13w +1.0, tbill_4w +1.0, treasury_settlement +0.8, treasury_settlement_bills -0.7, on_rrp -0.6, bank_total_assets -0.5, tga_daily_change -0.5, iorb +0.4, sofr_p1 +0.4
* lead 2 (decision 2018-12-13): tbill_13w +1.0, tbill_4w +0.7, on_rrp -0.6, sofr_volume -0.5, bank_total_assets -0.5, tga_daily_change -0.4, iorb +0.4, sofr_p1 +0.4, effr +0.3, sofr_p75_iorb_bps -0.3 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 3 (decision 2018-12-12): tbill_13w +1.0, tga_change_x_reserves +0.8, tbill_4w +0.6, sofr_volume -0.6, on_rrp -0.5, bank_total_assets -0.5, iorb +0.4, tga_daily +0.4, tga_daily_change +0.4, effr +0.3 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 4 (decision 2018-12-11): tbill_13w +1.0, tbill_4w +0.8, bank_total_assets -0.5, iorb +0.4, on_rrp -0.4, effr +0.4, sofr_p1 +0.4, sofr_p25 +0.3, tgcr +0.3, bgcr +0.3 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 5 (decision 2018-12-10): tbill_13w +0.9, tbill_4w +0.8, spread_bps +0.8, bank_total_assets -0.7, sofr_p75_iorb_bps +0.6, sofr_p25 +0.6, tgcr +0.6, bgcr +0.6, sofr +0.6, sofr_p75 +0.6 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]

### 2018-12-28 (2018-19, month_end)

* lead 1 (decision 2018-12-27): sofr_p75 +1.2, sofr_p25 +1.1, tgcr +1.1, bgcr +1.1, tbill_4w +1.1, sofr +1.1, iorb +1.1, effr +1.1, sofr_p99 +1.1, tbill_13w +1.0
* lead 2 (decision 2018-12-26): sofr_p1 +1.2, tbill_4w +1.2, tga_change_x_reserves -1.1, iorb +1.1, tbill_13w +1.1, effr +1.1, sofr_p25 +1.0, tgcr +1.0, bgcr +1.0, sofr_p75 +1.0 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 3 (decision 2018-12-24): tga_daily_change -1.1, tbill_4w +1.1, iorb +1.1, effr +1.1, sofr_p1 +1.1, tbill_13w +0.9, sofr_p25 +0.8, tgcr +0.8, bgcr +0.8, sofr +0.8 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 4 (decision 2018-12-21): tbill_4w +1.2, iorb +1.1, tga_daily +1.1, effr +1.1, sofr_p1 +1.1, sofr_p25 +1.0, tgcr +1.0, bgcr +1.0, sofr_p75 +1.0, sofr +1.0 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 5 (decision 2018-12-20): tga_daily +1.2, tbill_13w +0.9, tbill_4w +0.9, spread_bps +0.8, sofr_p75_iorb_bps +0.7, sofr_p25 +0.6, tgcr +0.6, dealer_treasury_position +0.6, bgcr +0.6, tga_change_x_reserves +0.6 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]

### 2020-03-04 (2020, ordinary)

* lead 1 (decision 2020-03-03): iorb_announced_change_bps -157.2, sofr_volume +2.3, sofr_p99 +2.2, sofr_p1 +2.2, iorb +2.1, effr +2.1, bgcr +2.1, tgcr +2.1, sofr_p25 +2.1, sofr_p75 +2.1
* lead 2 (decision 2020-03-02): bgcr +2.1, tgcr +2.1, sofr_p25 +2.1, sofr_p75 +2.1, sofr +2.1, iorb +2.1, sofr_p1 +2.1, effr +2.1, sofr_p99 +2.1, tbill_4w +1.9 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 3 (decision 2020-02-28): tga_daily_change -2.4, tbill_4w +2.1, iorb +2.1, sofr_p1 +2.1, bgcr +2.1, tgcr +2.1, sofr_p25 +2.1, effr +2.1, sofr_p75 +2.1, sofr +2.1 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 4 (decision 2020-02-27): tbill_4w +2.1, sofr_p1 +2.1, iorb +2.1, tbill_13w +2.1, bgcr +2.1, tgcr +2.1, sofr_p25 +2.1, effr +2.0, sofr_p75 +2.0, sofr +2.0 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 5 (decision 2020-02-26): tbill_4w +2.1, sofr_p1 +2.1, iorb +2.0, tbill_13w +2.0, bgcr +2.0, tgcr +2.0, sofr_p25 +2.0, sofr +2.0, effr +2.0, sofr_p75 +2.0 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]

### 2020-03-12 (2020, ordinary)

* lead 1 (decision 2020-03-11): sofr_volume +2.1, reserve_scarcity_state +1.7, bank_total_assets -1.7, reserve_balances -1.7, tga_daily -1.6, tga -1.5, sofr_p75 +1.3, sofr_p1 +1.3, tgcr +1.3, bgcr +1.3
* lead 2 (decision 2020-03-10): sofr_volume +2.0, reserve_scarcity_state +1.7, bank_total_assets -1.6, reserve_balances -1.6, tga_daily -1.6, tga -1.5, tgcr +1.3, bgcr +1.3, sofr_p25 +1.3, sofr_p75 +1.3 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 3 (decision 2020-03-09): sofr_volume +2.3, reserve_balances -1.7, bank_total_assets -1.6, reserve_scarcity_state +1.6, tga_daily -1.6, tga -1.4, sofr_p75 +1.3, sofr_p1 +1.3, tgcr +1.2, bgcr +1.2 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 4 (decision 2020-03-06): sofr_volume +2.0, reserve_balances -1.7, bank_total_assets -1.6, reserve_scarcity_state +1.6, tga_daily -1.5, tga -1.4, tgcr +1.3, bgcr +1.3, sofr_p25 +1.3, sofr_p1 +1.3 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 5 (decision 2020-03-05): spread_bps +3.5, sofr_p75_iorb_bps +3.0, sofr_volume +2.0, dealer_treasury_position -1.8, reserve_balances -1.7, bank_total_assets -1.6, reserve_scarcity_state +1.6, tga_daily -1.5, tgcr +1.4, bgcr +1.4 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]

### 2024-09-30 (2024, quarter_end)

* lead 1 (decision 2024-09-27): treasury_settlement_coupons +3.8, sofr_p99_iorb_sd15_bps +1.6, sofr_volume +1.5, tbill_13w -1.4, sofr -1.2, sofr_p75 -1.2, ofr_tri_rate -1.2, sofr_p25 -1.2, sofr_p99 -1.2, iorb -1.2
* lead 2 (decision 2024-09-26): sofr_p99_iorb_sd15_bps +1.6, tbill_4w -1.5, tbill_13w -1.4, ofr_tri_rate -1.2, sofr_p1 -1.2, iorb -1.2, effr -1.2, sofr -1.2, sofr_p99 -1.2, sofr_p25 -1.2 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 3 (decision 2024-09-25): sofr_p99_iorb_sd15_bps +1.6, tbill_4w -1.6, tbill_13w -1.5, ofr_tri_rate -1.3, sofr_p1 -1.3, iorb -1.3, effr -1.3, sofr -1.2, sofr_p99 -1.2, sofr_p25 -1.2 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 4 (decision 2024-09-24): sofr_p99_iorb_sd15_bps +1.6, tbill_13w -1.4, tbill_4w -1.4, sofr_p99 -1.3, sofr_p1 -1.3, ofr_tri_rate -1.3, sofr -1.3, sofr_p75 -1.3, sofr_p25 -1.3, bgcr -1.3 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 5 (decision 2024-09-23): sofr_p99_iorb_sd15_bps +1.6, sofr_p99 -1.4, sofr_p75 -1.4, sofr_p1 -1.4, bgcr -1.3, tgcr -1.3, tbill_13w -1.3, tbill_4w -1.3, sofr -1.3, sofr_p25 -1.3 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]

### 2024-12-26 (2024, ordinary)

* lead 1 (decision 2024-12-24): ofr_tri_rate -3.2, bank_total_assets +3.1, sofr_p1 -3.1, sofr -3.1, bgcr -3.1, tgcr -3.1, sofr_p99 -3.1, sofr_p25 -3.1, sofr_p75 -3.0, iorb -2.9
* lead 2 (decision 2024-12-23): ofr_tri_rate -3.3, sofr_p99 -3.2, sofr_p25 -3.2, bgcr -3.2, tgcr -3.2, sofr -3.2, sofr_p1 -3.2, sofr_p75 -3.1, iorb -3.0, effr -3.0 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 3 (decision 2024-12-20): tgcr -3.3, sofr_p25 -3.3, bgcr -3.3, sofr_p75 -3.3, sofr_p1 -3.3, sofr -3.3, iorb -3.1, effr -3.1, tbill_4w -2.7, sofr_p99 -2.6 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 4 (decision 2024-12-19): tbill_4w -2.7, sofr_p99 -2.3, sofr_p75 -2.3, sofr -2.3, sofr_p25 -2.3, tgcr -2.3, bgcr -2.3, ofr_tri_rate -2.2, bank_total_assets +2.2, tbill_13w -2.2 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 5 (decision 2024-12-18): tga_daily_change +4.1, tbill_4w -2.7, iorb -2.2, effr -2.2, sofr_p1 -2.2, bank_total_assets +2.2, sofr_p99 -2.2, tbill_13w -2.2, ofr_tri_rate -2.2, sofr_p25 -2.2 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]

### 2025-09-30 (2025-26, quarter_end)

* lead 1 (decision 2025-09-29): treasury_settlement_coupons +4.2, treasury_settlement +2.8, reserve_scarcity_state +1.4, treasury_settlement_bills +1.3, tbill_13w -1.3, treasury_settlement_soma +1.1, bank_total_assets +1.0, reserve_balances -1.0, effr -1.0, iorb -0.9
* lead 2 (decision 2025-09-26): reserve_scarcity_state +1.4, sofr_p75_iorb_bps +1.2, tbill_13w -1.2, on_rrp -1.1, bank_total_assets +1.0, spread_bps +1.0, reserve_balances -1.0, ofr_tri_rate -1.0, effr -1.0, sofr_volume +1.0 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 3 (decision 2025-09-25): reserve_scarcity_state +1.4, tbill_13w -1.3, ofr_tri_rate -1.2, on_rrp -1.1, bank_total_assets +1.0, reserve_balances -1.0, sofr -1.0, sofr_p99 -1.0, effr -1.0, sofr_p1 -1.0 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 4 (decision 2025-09-24): reserve_scarcity_state +1.4, tbill_13w -1.4, sofr_p99 -1.3, on_rrp -1.2, sofr_p1 -1.2, sofr_p25 -1.2, bgcr -1.2, tgcr -1.2, tga_daily +1.2, sofr -1.2 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 5 (decision 2025-09-23): reserve_scarcity_state +1.4, tbill_13w -1.4, on_rrp -1.3, ofr_tri_rate -1.1, tga_daily +1.1, bgcr -1.1, tgcr -1.1, sofr_p99 -1.1, effr -1.1, sofr -1.1 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]

### 2025-12-15 (2025-26, tax_date)

* lead 1 (decision 2025-12-12): tgcr -4.0, sofr_p25 -4.0, bgcr -4.0, sofr -3.9, sofr_p75 -3.9, sofr_p1 -3.9, effr -3.6, iorb -3.5, tbill_4w -3.2, sofr_p99 -2.9
* lead 2 (decision 2025-12-11): dealer_treasury_position +3.2, tbill_4w -3.2, tbill_13w -2.7, sofr_p99 -2.5, sofr_p25 -2.5, tgcr -2.5, bgcr -2.5, sofr -2.5, sofr_p75 -2.5, reserve_scarcity_state +2.4 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 3 (decision 2025-12-10): dealer_treasury_position +3.2, tbill_4w -3.2, tbill_13w -2.5, reserve_scarcity_state +2.4, sofr_p25 -2.4, tgcr -2.4, bgcr -2.4, sofr -2.4, sofr_p99 -2.4, ofr_tri_rate -2.4 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 4 (decision 2025-12-09): tbill_4w -3.2, dealer_treasury_position +3.2, ofr_tri_rate -2.6, tbill_13w -2.6, reserve_scarcity_state +2.5, iorb -2.4, reserve_balances -2.4, sofr -2.4, sofr_p25 -2.3, tgcr -2.3 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 5 (decision 2025-12-08): tbill_4w -3.4, dealer_treasury_position +3.2, ofr_tri_rate -3.0, tbill_13w -2.7, sofr_p25 -2.6, tgcr -2.6, bgcr -2.6, sofr -2.6, sofr_p99 -2.6, sofr_p75 -2.6 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]

### 2025-12-26 (2025-26, ordinary)

* lead 1 (decision 2025-12-24): sofr -3.9, ofr_tri_rate -3.9, sofr_p1 -3.9, sofr_p75 -3.8, tgcr -3.8, sofr_p25 -3.8, bgcr -3.8, sofr_p99 -3.8, effr -3.6, tbill_4w -3.6
* lead 2 (decision 2025-12-23): ofr_tri_rate -4.2, sofr -3.9, sofr_p1 -3.9, sofr_p25 -3.8, tgcr -3.8, bgcr -3.8, sofr_p75 -3.8, sofr_p99 -3.8, tbill_4w -3.6, effr -3.6 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 3 (decision 2025-12-22): ofr_tri_rate -4.4, sofr -4.2, sofr_p25 -4.2, tgcr -4.2, bgcr -4.2, sofr_p75 -4.1, sofr_p99 -4.1, sofr_p1 -4.1, tbill_4w -3.7, effr -3.7 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 4 (decision 2025-12-19): sofr -4.4, sofr_p1 -4.4, sofr_p99 -4.4, tgcr -4.4, sofr_p25 -4.4, bgcr -4.4, ofr_tri_rate -4.3, sofr_p75 -4.3, tbill_4w -3.9, effr -3.8 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]
* lead 5 (decision 2025-12-18): ofr_tri_rate -4.7, sofr -4.3, sofr_p1 -4.3, sofr_p25 -4.3, tgcr -4.3, bgcr -4.3, sofr_p75 -4.3, sofr_p99 -4.2, effr -4.0, iorb -3.9 [not public at this lead: treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, treasury_settlement_soma, iorb_announced_change_bps, iorb_days_to_announced_change]

## Table 4. Each model row's probability / cut-off at each lead (a flag is marked *)

### 2018-11-15

| row | family | lead 1 | lead 2 | lead 3 | lead 4 | lead 5 |
|---|---|---|---|---|---|---|
| calendar_climatology | reference | 0.02/inf | 0.02/inf | 0.02/inf | 0.02/inf | 0.02/inf |
| effr_pooled | pretraining | 0.05/inf | 0.05/inf | 0.07/inf | 0.03/inf | 0.09/inf |
| effr_pretrain_finetune | pretraining | 0.00/inf | 0.00/inf | 0.01/inf | 0.00/inf | 0.00/inf |
| effr_sofr_only | pretraining | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| latent_factor | stress_factor | 0.01/inf | 0.02/inf | 0.02/inf | 0.01/inf | 0.02/inf |
| latent_factor_logit | stress_factor | 0.03/inf | 0.02/inf | 0.02/inf | 0.03/inf | 0.01/inf |
| latent_factor_resid | stress_factor | 0.02/inf | 0.03/inf | 0.03/inf | 0.02/inf | 0.02/inf |
| ngboost_laplace | ngboost_laplace | 0.00/inf | 0.00/inf | 0.01/inf | 0.00/inf | 0.00/inf |
| persistence_logistic | reference | 0.02/inf | 0.02/inf | 0.02/inf | 0.02/inf | 0.00/inf |
| projected_reserves | projected_reserves | 0.01/inf | 0.01/inf | 0.01/inf | 0.01/inf | 0.00/inf |
| risk_gbm | passer | 0.11/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_gbm+effr_pooled | pretraining | 0.11/inf | 0.05/inf | 0.07/inf | 0.03/inf | 0.09/inf |
| risk_gbm+effr_pretrain_finetune | pretraining | 0.11/inf | 0.00/inf | 0.01/inf | 0.00/inf | 0.00/inf |
| risk_gbm+effr_sofr_only | pretraining | 0.11/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_gbm+h41 | timing | 0.11/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_gbm+hurdle_isotonic | hurdle | 0.11/inf | 0.02/inf | 0.02/inf | 0.03/inf | 0.00/inf |
| risk_gbm+hurdle_platt | hurdle | 0.11/inf | 0.02/inf | 0.02/inf | 0.03/inf | 0.00/inf |
| risk_gbm+hurdle_state_isotonic | hurdle | 0.11/inf | 0.00/inf | 0.01/inf | 0.01/inf | 0.00/inf |
| risk_gbm+hurdle_state_platt | hurdle | 0.11/inf | 0.00/inf | 0.01/inf | 0.01/inf | 0.00/inf |
| risk_gbm+latent_factor | stress_factor | 0.11/inf | 0.02/inf | 0.02/inf | 0.01/inf | 0.02/inf |
| risk_gbm+latent_factor_logit | stress_factor | 0.11/inf | 0.02/inf | 0.02/inf | 0.03/inf | 0.01/inf |
| risk_gbm+latent_factor_resid | stress_factor | 0.11/inf | 0.03/inf | 0.03/inf | 0.02/inf | 0.02/inf |
| risk_gbm+projected | projected_reserves | 0.11/inf | 0.01/inf | 0.01/inf | 0.01/inf | 0.00/inf |
| risk_gbm+settle | timing | 0.11/inf | 0.11/inf | 0.12/inf | 0.12/inf | 0.12/inf |
| risk_gbm+settle+h41 | timing | 0.11/inf | 0.11/inf | 0.12/inf | 0.12/inf | 0.12/inf |
| risk_gbm+structural | structural | 0.11/inf | 0.01/inf | 0.01/inf | 0.02/inf | 0.00/inf |
| risk_gbm_base | passer | 0.11/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_gbm_base+h41 | timing | 0.11/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_gbm_base+hurdle_isotonic | hurdle | 0.11/inf | 0.02/inf | 0.02/inf | 0.03/inf | 0.00/inf |
| risk_gbm_base+hurdle_platt | hurdle | 0.11/inf | 0.02/inf | 0.02/inf | 0.03/inf | 0.00/inf |
| risk_gbm_base+hurdle_state_isotonic | hurdle | 0.11/inf | 0.00/inf | 0.01/inf | 0.01/inf | 0.00/inf |
| risk_gbm_base+hurdle_state_platt | hurdle | 0.11/inf | 0.00/inf | 0.01/inf | 0.01/inf | 0.00/inf |
| risk_gbm_base+settle | timing | 0.11/inf | 0.11/inf | 0.12/inf | 0.12/inf | 0.12/inf |
| risk_gbm_base+settle+h41 | timing | 0.11/inf | 0.11/inf | 0.12/inf | 0.12/inf | 0.12/inf |
| risk_logistic | passer | 0.07/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_logistic+h41 | timing | 0.16/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_logistic+hurdle_isotonic | hurdle | 0.07/inf | 0.02/inf | 0.02/inf | 0.03/inf | 0.00/inf |
| risk_logistic+hurdle_platt | hurdle | 0.07/inf | 0.02/inf | 0.02/inf | 0.03/inf | 0.00/inf |
| risk_logistic+hurdle_state_isotonic | hurdle | 0.07/inf | 0.00/inf | 0.01/inf | 0.01/inf | 0.00/inf |
| risk_logistic+hurdle_state_platt | hurdle | 0.07/inf | 0.00/inf | 0.01/inf | 0.01/inf | 0.00/inf |
| risk_logistic+settle | timing | 0.07/inf | 0.04/inf | 0.09/inf | 0.15/inf | 0.00/inf |
| risk_logistic+settle+h41 | timing | 0.16/inf | 0.04/inf | 0.03/inf | 0.25/inf | 0.00/inf |
| risk_logistic_base | passer | 0.07/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_logistic_base+h41 | timing | 0.41/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_logistic_base+hurdle_isotonic | hurdle | 0.07/inf | 0.02/inf | 0.02/inf | 0.03/inf | 0.00/inf |
| risk_logistic_base+hurdle_platt | hurdle | 0.07/inf | 0.02/inf | 0.02/inf | 0.03/inf | 0.00/inf |
| risk_logistic_base+hurdle_state_isotonic | hurdle | 0.07/inf | 0.00/inf | 0.01/inf | 0.01/inf | 0.00/inf |
| risk_logistic_base+hurdle_state_platt | hurdle | 0.07/inf | 0.00/inf | 0.01/inf | 0.01/inf | 0.00/inf |
| risk_logistic_base+settle | timing | 0.07/inf | 0.07/inf | 0.22/inf | 0.21/inf | 0.00/inf |
| risk_logistic_base+settle+h41 | timing | 0.41/inf | 0.08/inf | 0.07/inf | 0.32/inf | 0.00/inf |
| risk_quantile_skewt_base | passer | 0.94/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_quantile_skewt_base+h41 | timing | 0.06/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_quantile_skewt_base+hurdle_isotonic | hurdle | 0.94/inf | 0.02/inf | 0.02/inf | 0.03/inf | 0.00/inf |
| risk_quantile_skewt_base+hurdle_platt | hurdle | 0.94/inf | 0.02/inf | 0.02/inf | 0.03/inf | 0.00/inf |
| risk_quantile_skewt_base+hurdle_state_isotonic | hurdle | 0.94/inf | 0.00/inf | 0.01/inf | 0.01/inf | 0.00/inf |
| risk_quantile_skewt_base+hurdle_state_platt | hurdle | 0.94/inf | 0.00/inf | 0.01/inf | 0.01/inf | 0.00/inf |
| risk_quantile_skewt_base+settle | timing | 0.94/inf | 0.61/inf | 0.02/inf | 0.96/inf | 0.00/inf |
| risk_quantile_skewt_base+settle+h41 | timing | 0.06/inf | 0.79/inf | 0.00/inf | 0.83/inf | 0.00/inf |
| structural_liquidity | structural | 0.01/inf | 0.01/inf | 0.01/inf | 0.02/inf | 0.00/inf |

### 2018-11-30

| row | family | lead 1 | lead 2 | lead 3 | lead 4 | lead 5 |
|---|---|---|---|---|---|---|
| calendar_climatology | reference | 0.07/inf | 0.10/inf | 0.10/inf | 0.10/inf | 0.10/inf |
| effr_pooled | pretraining | 0.11/inf | 0.13/inf | 0.18/inf | 0.30/inf | 0.07/inf |
| effr_pretrain_finetune | pretraining | 0.08/inf | 0.03/inf | 0.03/inf | 0.06/inf | 0.01/inf |
| effr_sofr_only | pretraining | 0.07/inf | 0.01/inf | 0.02/inf | 0.01/inf | 0.00/inf |
| latent_factor | stress_factor | 0.02/inf | 0.01/inf | 0.02/inf | 0.02/inf | 0.01/inf |
| latent_factor_logit | stress_factor | 0.05/inf | 0.03/inf | 0.02/inf | 0.02/inf | 0.02/inf |
| latent_factor_resid | stress_factor | 0.04/inf | 0.02/inf | 0.02/inf | 0.03/inf | 0.02/inf |
| ngboost_laplace | ngboost_laplace | 0.05/inf | 0.00/inf | 0.01/inf | 0.00/inf | 0.00/inf |
| persistence_logistic | reference | 0.04/inf | 0.02/inf | 0.02/inf | 0.01/inf | 0.00/inf |
| projected_reserves | projected_reserves | 0.23/inf | 0.08/inf | 0.06/inf | 0.04/inf | 0.01/inf |
| risk_gbm | passer | 0.12/inf | 0.10/inf | 0.11/inf | 0.11/inf | 0.11/inf |
| risk_gbm+effr_pooled | pretraining | 0.12/inf | 0.10/inf | 0.11/inf | 0.11/inf | 0.11/inf |
| risk_gbm+effr_pretrain_finetune | pretraining | 0.12/inf | 0.10/inf | 0.11/inf | 0.11/inf | 0.11/inf |
| risk_gbm+effr_sofr_only | pretraining | 0.12/inf | 0.10/inf | 0.11/inf | 0.11/inf | 0.11/inf |
| risk_gbm+h41 | timing | 0.12/inf | 0.10/inf | 0.11/inf | 0.11/inf | 0.11/inf |
| risk_gbm+hurdle_isotonic | hurdle | 0.12/inf | 0.10/inf | 0.11/inf | 0.11/inf | 0.11/inf |
| risk_gbm+hurdle_platt | hurdle | 0.12/inf | 0.10/inf | 0.11/inf | 0.11/inf | 0.11/inf |
| risk_gbm+hurdle_state_isotonic | hurdle | 0.12/inf | 0.10/inf | 0.11/inf | 0.11/inf | 0.11/inf |
| risk_gbm+hurdle_state_platt | hurdle | 0.12/inf | 0.10/inf | 0.11/inf | 0.11/inf | 0.11/inf |
| risk_gbm+latent_factor | stress_factor | 0.12/inf | 0.10/inf | 0.11/inf | 0.11/inf | 0.11/inf |
| risk_gbm+latent_factor_logit | stress_factor | 0.12/inf | 0.10/inf | 0.11/inf | 0.11/inf | 0.11/inf |
| risk_gbm+latent_factor_resid | stress_factor | 0.12/inf | 0.10/inf | 0.11/inf | 0.11/inf | 0.11/inf |
| risk_gbm+projected | projected_reserves | 0.12/inf | 0.10/inf | 0.11/inf | 0.11/inf | 0.11/inf |
| risk_gbm+settle | timing | 0.12/inf | 0.11/inf | 0.12/inf | 0.12/inf | 0.12/inf |
| risk_gbm+settle+h41 | timing | 0.12/inf | 0.11/inf | 0.12/inf | 0.12/inf | 0.12/inf |
| risk_gbm+structural | structural | 0.12/inf | 0.10/inf | 0.11/inf | 0.11/inf | 0.11/inf |
| risk_gbm_base | passer | 0.12/inf | 0.10/inf | 0.11/inf | 0.11/inf | 0.11/inf |
| risk_gbm_base+h41 | timing | 0.12/inf | 0.10/inf | 0.11/inf | 0.11/inf | 0.11/inf |
| risk_gbm_base+hurdle_isotonic | hurdle | 0.12/inf | 0.10/inf | 0.11/inf | 0.11/inf | 0.11/inf |
| risk_gbm_base+hurdle_platt | hurdle | 0.12/inf | 0.10/inf | 0.11/inf | 0.11/inf | 0.11/inf |
| risk_gbm_base+hurdle_state_isotonic | hurdle | 0.12/inf | 0.10/inf | 0.11/inf | 0.11/inf | 0.11/inf |
| risk_gbm_base+hurdle_state_platt | hurdle | 0.12/inf | 0.10/inf | 0.11/inf | 0.11/inf | 0.11/inf |
| risk_gbm_base+settle | timing | 0.12/inf | 0.11/inf | 0.12/inf | 0.12/inf | 0.12/inf |
| risk_gbm_base+settle+h41 | timing | 0.12/inf | 0.11/inf | 0.12/inf | 0.12/inf | 0.12/inf |
| risk_logistic | passer | 0.10/inf | 0.02/inf | 0.01/inf | 0.00/inf | 0.00/inf |
| risk_logistic+h41 | timing | 0.11/inf | 0.02/inf | 0.01/inf | 0.00/inf | 0.00/inf |
| risk_logistic+hurdle_isotonic | hurdle | 0.10/inf | 0.02/inf | 0.01/inf | 0.00/inf | 0.00/inf |
| risk_logistic+hurdle_platt | hurdle | 0.10/inf | 0.02/inf | 0.01/inf | 0.00/inf | 0.00/inf |
| risk_logistic+hurdle_state_isotonic | hurdle | 0.10/inf | 0.02/inf | 0.01/inf | 0.00/inf | 0.00/inf |
| risk_logistic+hurdle_state_platt | hurdle | 0.10/inf | 0.02/inf | 0.01/inf | 0.00/inf | 0.00/inf |
| risk_logistic+settle | timing | 0.10/inf | 0.02/inf | 0.01/inf | 0.01/inf | 0.00/inf |
| risk_logistic+settle+h41 | timing | 0.11/inf | 0.02/inf | 0.01/inf | 0.01/inf | 0.01/inf |
| risk_logistic_base | passer | 0.07/inf | 0.02/inf | 0.02/inf | 0.01/inf | 0.00/inf |
| risk_logistic_base+h41 | timing | 0.08/0.41 | 0.02/inf | 0.03/inf | 0.01/inf | 0.01/inf |
| risk_logistic_base+hurdle_isotonic | hurdle | 0.07/inf | 0.02/inf | 0.02/inf | 0.01/inf | 0.00/inf |
| risk_logistic_base+hurdle_platt | hurdle | 0.07/inf | 0.02/inf | 0.02/inf | 0.01/inf | 0.00/inf |
| risk_logistic_base+hurdle_state_isotonic | hurdle | 0.07/inf | 0.02/inf | 0.02/inf | 0.01/inf | 0.00/inf |
| risk_logistic_base+hurdle_state_platt | hurdle | 0.07/inf | 0.02/inf | 0.02/inf | 0.01/inf | 0.00/inf |
| risk_logistic_base+settle | timing | 0.07/inf | 0.03/inf | 0.03/inf | 0.02/inf | 0.00/inf |
| risk_logistic_base+settle+h41 | timing | 0.08/0.41 | 0.03/inf | 0.03/inf | 0.01/inf | 0.06/inf |
| risk_quantile_skewt_base | passer | 0.69/0.94 | 0.03/inf | 0.16/inf | 0.26/inf | 0.32/inf |
| risk_quantile_skewt_base+h41 | timing | 0.00/inf | 0.05/inf | 0.04/inf | 0.20/inf | 1.00/inf |
| risk_quantile_skewt_base+hurdle_isotonic | hurdle | 0.69/0.94 | 0.03/inf | 0.16/inf | 0.26/inf | 0.32/inf |
| risk_quantile_skewt_base+hurdle_platt | hurdle | 0.69/0.94 | 0.03/inf | 0.16/inf | 0.26/inf | 0.32/inf |
| risk_quantile_skewt_base+hurdle_state_isotonic | hurdle | 0.69/0.94 | 0.03/inf | 0.16/inf | 0.26/inf | 0.32/inf |
| risk_quantile_skewt_base+hurdle_state_platt | hurdle | 0.69/0.94 | 0.03/inf | 0.16/inf | 0.26/inf | 0.32/inf |
| risk_quantile_skewt_base+settle | timing | 0.69/0.94 | 0.30/inf | 0.00/inf | 0.37/inf | 0.36/inf |
| risk_quantile_skewt_base+settle+h41 | timing | 0.00/inf | 0.40/inf | 0.00/inf | 0.00/inf | 0.20/inf |
| structural_liquidity | structural | 0.10/inf | 0.89/inf | 0.96/inf | 0.91/inf | 0.02/inf |

### 2018-12-17

| row | family | lead 1 | lead 2 | lead 3 | lead 4 | lead 5 |
|---|---|---|---|---|---|---|
| calendar_climatology | reference | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| effr_pooled | pretraining | 0.12/inf | 0.12/inf | 0.10/inf | 0.18/inf | 0.53/inf |
| effr_pretrain_finetune | pretraining | 0.01/inf | 0.01/inf | 0.01/inf | 0.01/inf | 0.00/inf |
| effr_sofr_only | pretraining | 0.01/inf | 0.01/inf | 0.01/inf | 0.01/inf | 0.00/inf |
| latent_factor | stress_factor | 0.01/inf | 0.02/inf | 0.02/inf | 0.03/inf | 0.04/inf |
| latent_factor_logit | stress_factor | 0.04/inf | 0.04/inf | 0.04/inf | 0.04/inf | 0.02/inf |
| latent_factor_resid | stress_factor | 0.02/inf | 0.03/inf | 0.03/inf | 0.04/inf | 0.05/inf |
| ngboost_laplace | ngboost_laplace | 0.05/inf | 0.04/inf | 0.05/inf | 0.04/inf | 0.04/inf |
| persistence_logistic | reference | 0.03/inf | 0.03/inf | 0.04/inf | 0.03/inf | 0.00/inf |
| projected_reserves | projected_reserves | 0.01/inf | 0.02/inf | 0.01/inf | 0.01/inf | 0.00/inf |
| risk_gbm | passer | 0.12/inf | 0.08/inf | 0.09/inf | 0.09/inf | 0.09/inf |
| risk_gbm+effr_pooled | pretraining | 0.12/inf | 0.08/inf | 0.09/inf | 0.09/inf | 0.09/inf |
| risk_gbm+effr_pretrain_finetune | pretraining | 0.12/inf | 0.08/inf | 0.09/inf | 0.09/inf | 0.09/inf |
| risk_gbm+effr_sofr_only | pretraining | 0.12/inf | 0.08/inf | 0.09/inf | 0.09/inf | 0.09/inf |
| risk_gbm+h41 | timing | 0.12/inf | 0.08/inf | 0.09/inf | 0.09/inf | 0.09/inf |
| risk_gbm+hurdle_isotonic | hurdle | 0.12/inf | 0.08/inf | 0.09/inf | 0.09/inf | 0.09/inf |
| risk_gbm+hurdle_platt | hurdle | 0.12/inf | 0.08/inf | 0.09/inf | 0.09/inf | 0.09/inf |
| risk_gbm+hurdle_state_isotonic | hurdle | 0.12/inf | 0.08/inf | 0.09/inf | 0.09/inf | 0.09/inf |
| risk_gbm+hurdle_state_platt | hurdle | 0.12/inf | 0.08/inf | 0.09/inf | 0.09/inf | 0.09/inf |
| risk_gbm+latent_factor | stress_factor | 0.12/inf | 0.08/inf | 0.09/inf | 0.09/inf | 0.09/inf |
| risk_gbm+latent_factor_logit | stress_factor | 0.12/inf | 0.08/inf | 0.09/inf | 0.09/inf | 0.09/inf |
| risk_gbm+latent_factor_resid | stress_factor | 0.12/inf | 0.08/inf | 0.09/inf | 0.09/inf | 0.09/inf |
| risk_gbm+projected | projected_reserves | 0.12/inf | 0.08/inf | 0.09/inf | 0.09/inf | 0.09/inf |
| risk_gbm+settle | timing | 0.12/inf | 0.12/inf | 0.13/inf | 0.13/inf | 0.13/inf |
| risk_gbm+settle+h41 | timing | 0.12/inf | 0.12/inf | 0.13/inf | 0.13/inf | 0.13/inf |
| risk_gbm+structural | structural | 0.12/inf | 0.08/inf | 0.09/inf | 0.09/inf | 0.09/inf |
| risk_gbm_base | passer | 0.12/inf | 0.08/inf | 0.09/inf | 0.09/inf | 0.09/inf |
| risk_gbm_base+h41 | timing | 0.12/inf | 0.08/inf | 0.09/inf | 0.09/inf | 0.09/inf |
| risk_gbm_base+hurdle_isotonic | hurdle | 0.12/inf | 0.08/inf | 0.09/inf | 0.09/inf | 0.09/inf |
| risk_gbm_base+hurdle_platt | hurdle | 0.12/inf | 0.08/inf | 0.09/inf | 0.09/inf | 0.09/inf |
| risk_gbm_base+hurdle_state_isotonic | hurdle | 0.12/inf | 0.08/inf | 0.09/inf | 0.09/inf | 0.09/inf |
| risk_gbm_base+hurdle_state_platt | hurdle | 0.12/inf | 0.08/inf | 0.09/inf | 0.09/inf | 0.09/inf |
| risk_gbm_base+settle | timing | 0.12/inf | 0.12/inf | 0.13/inf | 0.13/inf | 0.13/inf |
| risk_gbm_base+settle+h41 | timing | 0.12/inf | 0.12/inf | 0.13/inf | 0.13/inf | 0.13/inf |
| risk_logistic | passer | 0.01/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_logistic+h41 | timing | 0.01/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_logistic+hurdle_isotonic | hurdle | 0.01/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_logistic+hurdle_platt | hurdle | 0.01/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_logistic+hurdle_state_isotonic | hurdle | 0.01/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_logistic+hurdle_state_platt | hurdle | 0.01/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_logistic+settle | timing | 0.01/inf | 0.01/inf | 0.01/inf | 0.01/inf | 0.09/inf |
| risk_logistic+settle+h41 | timing | 0.01/inf | 0.01/inf | 0.01/inf | 0.01/inf | 0.08/inf |
| risk_logistic_base | passer | 0.02/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_logistic_base+h41 | timing | 0.02/0.41 | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_logistic_base+hurdle_isotonic | hurdle | 0.02/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_logistic_base+hurdle_platt | hurdle | 0.02/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_logistic_base+hurdle_state_isotonic | hurdle | 0.02/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_logistic_base+hurdle_state_platt | hurdle | 0.02/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_logistic_base+settle | timing | 0.02/inf | 0.01/inf | 0.01/inf | 0.01/inf | 0.02/inf |
| risk_logistic_base+settle+h41 | timing | 0.02/0.41 | 0.01/inf | 0.01/inf | 0.01/inf | 0.03/inf |
| risk_quantile_skewt_base | passer | 0.07/0.94 | 0.11/inf | 0.47/inf | 0.30/inf | 0.97/inf |
| risk_quantile_skewt_base+h41 | timing | 0.10/inf | 0.43/inf | 0.68/inf | 0.54/inf | 0.95/inf |
| risk_quantile_skewt_base+hurdle_isotonic | hurdle | 0.07/0.94 | 0.11/inf | 0.47/inf | 0.30/inf | 0.97/inf |
| risk_quantile_skewt_base+hurdle_platt | hurdle | 0.07/0.94 | 0.11/inf | 0.47/inf | 0.30/inf | 0.97/inf |
| risk_quantile_skewt_base+hurdle_state_isotonic | hurdle | 0.07/0.94 | 0.11/inf | 0.47/inf | 0.30/inf | 0.97/inf |
| risk_quantile_skewt_base+hurdle_state_platt | hurdle | 0.07/0.94 | 0.11/inf | 0.47/inf | 0.30/inf | 0.97/inf |
| risk_quantile_skewt_base+settle | timing | 0.07/0.94 | 0.34/inf | 1.00/inf | 1.00/inf | 1.00/inf |
| risk_quantile_skewt_base+settle+h41 | timing | 0.10/inf | 0.49/inf | 0.89/inf | 1.00/inf | 1.00/inf |
| structural_liquidity | structural | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |

### 2018-12-28

| row | family | lead 1 | lead 2 | lead 3 | lead 4 | lead 5 |
|---|---|---|---|---|---|---|
| calendar_climatology | reference | 0.04/inf | 0.04/inf | 0.04/inf | 0.04/inf | 0.04/inf |
| effr_pooled | pretraining | 0.20/inf | 0.09/inf | 0.07/inf | 0.09/inf | 0.46/inf |
| effr_pretrain_finetune | pretraining | 0.03/inf | 0.03/inf | 0.03/inf | 0.03/inf | 0.02/inf |
| effr_sofr_only | pretraining | 0.03/inf | 0.03/inf | 0.03/inf | 0.03/inf | 0.00/inf |
| latent_factor | stress_factor | 0.13/inf | 0.05/inf | 0.03/inf | 0.03/inf | 0.05/inf |
| latent_factor_logit | stress_factor | 0.12/inf | 0.03/inf | 0.04/inf | 0.04/inf | 0.02/inf |
| latent_factor_resid | stress_factor | 0.16/inf | 0.07/inf | 0.04/inf | 0.04/inf | 0.06/inf |
| ngboost_laplace | ngboost_laplace | 0.05/inf | 0.03/inf | 0.05/inf | 0.04/inf | 0.04/inf |
| persistence_logistic | reference | 0.03/inf | 0.03/inf | 0.04/inf | 0.03/inf | 0.00/inf |
| projected_reserves | projected_reserves | 0.02/inf | 0.02/inf | 0.05/inf | 0.04/inf | 0.01/inf |
| risk_gbm | passer | 0.12/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_gbm+effr_pooled | pretraining | 0.12/inf | 0.09/inf | 0.07/inf | 0.09/inf | 0.46/inf |
| risk_gbm+effr_pretrain_finetune | pretraining | 0.12/inf | 0.03/inf | 0.03/inf | 0.03/inf | 0.02/inf |
| risk_gbm+effr_sofr_only | pretraining | 0.12/inf | 0.03/inf | 0.03/inf | 0.03/inf | 0.00/inf |
| risk_gbm+h41 | timing | 0.12/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_gbm+hurdle_isotonic | hurdle | 0.12/inf | 0.03/inf | 0.04/inf | 0.03/inf | 0.00/inf |
| risk_gbm+hurdle_platt | hurdle | 0.12/inf | 0.03/inf | 0.04/inf | 0.03/inf | 0.00/inf |
| risk_gbm+hurdle_state_isotonic | hurdle | 0.12/inf | 0.02/inf | 0.02/inf | 0.02/inf | 0.00/inf |
| risk_gbm+hurdle_state_platt | hurdle | 0.12/inf | 0.02/inf | 0.02/inf | 0.02/inf | 0.00/inf |
| risk_gbm+latent_factor | stress_factor | 0.12/inf | 0.05/inf | 0.03/inf | 0.03/inf | 0.05/inf |
| risk_gbm+latent_factor_logit | stress_factor | 0.12/inf | 0.03/inf | 0.04/inf | 0.04/inf | 0.02/inf |
| risk_gbm+latent_factor_resid | stress_factor | 0.12/inf | 0.07/inf | 0.04/inf | 0.04/inf | 0.06/inf |
| risk_gbm+projected | projected_reserves | 0.12/inf | 0.02/inf | 0.05/inf | 0.04/inf | 0.01/inf |
| risk_gbm+settle | timing | 0.12/inf | 0.12/inf | 0.13/inf | 0.13/inf | 0.13/inf |
| risk_gbm+settle+h41 | timing | 0.12/inf | 0.12/inf | 0.13/inf | 0.13/inf | 0.13/inf |
| risk_gbm+structural | structural | 0.12/inf | 0.17/inf | 0.17/inf | 0.17/inf | 0.00/inf |
| risk_gbm_base | passer | 0.12/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_gbm_base+h41 | timing | 0.12/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_gbm_base+hurdle_isotonic | hurdle | 0.12/inf | 0.03/inf | 0.04/inf | 0.03/inf | 0.00/inf |
| risk_gbm_base+hurdle_platt | hurdle | 0.12/inf | 0.03/inf | 0.04/inf | 0.03/inf | 0.00/inf |
| risk_gbm_base+hurdle_state_isotonic | hurdle | 0.12/inf | 0.02/inf | 0.02/inf | 0.02/inf | 0.00/inf |
| risk_gbm_base+hurdle_state_platt | hurdle | 0.12/inf | 0.02/inf | 0.02/inf | 0.02/inf | 0.00/inf |
| risk_gbm_base+settle | timing | 0.12/inf | 0.12/inf | 0.13/inf | 0.13/inf | 0.13/inf |
| risk_gbm_base+settle+h41 | timing | 0.12/inf | 0.12/inf | 0.13/inf | 0.13/inf | 0.13/inf |
| risk_logistic | passer | 0.01/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_logistic+h41 | timing | 0.01/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_logistic+hurdle_isotonic | hurdle | 0.01/inf | 0.03/inf | 0.04/inf | 0.03/inf | 0.00/inf |
| risk_logistic+hurdle_platt | hurdle | 0.01/inf | 0.03/inf | 0.04/inf | 0.03/inf | 0.00/inf |
| risk_logistic+hurdle_state_isotonic | hurdle | 0.01/inf | 0.02/inf | 0.02/inf | 0.02/inf | 0.00/inf |
| risk_logistic+hurdle_state_platt | hurdle | 0.01/inf | 0.02/inf | 0.02/inf | 0.02/inf | 0.00/inf |
| risk_logistic+settle | timing | 0.01/inf | 0.01/inf | 0.01/inf | 0.00/inf | 0.03/inf |
| risk_logistic+settle+h41 | timing | 0.01/inf | 0.01/inf | 0.05/inf | 0.00/inf | 0.01/inf |
| risk_logistic_base | passer | 0.01/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_logistic_base+h41 | timing | 0.02/0.41 | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_logistic_base+hurdle_isotonic | hurdle | 0.01/inf | 0.03/inf | 0.04/inf | 0.03/inf | 0.00/inf |
| risk_logistic_base+hurdle_platt | hurdle | 0.01/inf | 0.03/inf | 0.04/inf | 0.03/inf | 0.00/inf |
| risk_logistic_base+hurdle_state_isotonic | hurdle | 0.01/inf | 0.02/inf | 0.02/inf | 0.02/inf | 0.00/inf |
| risk_logistic_base+hurdle_state_platt | hurdle | 0.01/inf | 0.02/inf | 0.02/inf | 0.02/inf | 0.00/inf |
| risk_logistic_base+settle | timing | 0.01/inf | 0.01/inf | 0.00/inf | 0.00/inf | 0.03/inf |
| risk_logistic_base+settle+h41 | timing | 0.02/0.41 | 0.01/inf | 0.01/inf | 0.00/inf | 0.03/inf |
| risk_quantile_skewt_base | passer | 0.00/0.94 | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_quantile_skewt_base+h41 | timing | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf | 0.00/inf |
| risk_quantile_skewt_base+hurdle_isotonic | hurdle | 0.00/0.94 | 0.03/inf | 0.04/inf | 0.03/inf | 0.00/inf |
| risk_quantile_skewt_base+hurdle_platt | hurdle | 0.00/0.94 | 0.03/inf | 0.04/inf | 0.03/inf | 0.00/inf |
| risk_quantile_skewt_base+hurdle_state_isotonic | hurdle | 0.00/0.94 | 0.02/inf | 0.02/inf | 0.02/inf | 0.00/inf |
| risk_quantile_skewt_base+hurdle_state_platt | hurdle | 0.00/0.94 | 0.02/inf | 0.02/inf | 0.02/inf | 0.00/inf |
| risk_quantile_skewt_base+settle | timing | 0.00/0.94 | 0.00/inf | 0.46/inf | 0.00/inf | 0.81/inf |
| risk_quantile_skewt_base+settle+h41 | timing | 0.00/inf | 0.00/inf | 0.11/inf | 0.03/inf | 0.49/inf |
| structural_liquidity | structural | 0.06/inf | 0.17/inf | 0.17/inf | 0.17/inf | 0.00/inf |

### 2020-03-04

| row | family | lead 1 | lead 2 | lead 3 | lead 4 | lead 5 |
|---|---|---|---|---|---|---|
| calendar_climatology | reference | 0.20/0.22 | 0.20/0.27 | 0.20/0.27 | 0.20/0.27 | 0.20/0.27 |
| effr_pooled | pretraining | 0.13/0.28 | 0.16/0.42 | 0.20/0.43 | 0.16/0.41 | 0.17/0.39 |
| effr_pretrain_finetune | pretraining | 0.10/0.25 | 0.14/0.34 | 0.20/0.39 | 0.15/0.40 | 0.17/0.37 |
| effr_sofr_only | pretraining | 0.17/0.37 | 0.18/0.42 | 0.21/0.43 | 0.19/0.45 | 0.20/0.42 |
| latent_factor | stress_factor | 0.41/0.42 | 0.44/0.45 | 0.44/0.45 | 0.45/0.46 | 0.45/0.46 |
| latent_factor_logit | stress_factor | 0.10/0.17 | 0.19/0.20 | 0.18/0.20 | 0.21/0.24 | 0.19/0.21 |
| latent_factor_resid | stress_factor | 0.41/0.42 | 0.44/0.45 | 0.44/0.45 | 0.45/0.46 | 0.45/0.46 |
| ngboost_laplace | ngboost_laplace | 0.00/0.33 | 0.01/0.30 | 0.05/0.28 | 0.08/0.34 | 0.10/0.44 |
| persistence_logistic | reference | 0.15/0.19 | 0.19/0.23 | 0.21/0.24 | 0.18/0.21 | 0.19/0.22 |
| projected_reserves | projected_reserves | 0.21/0.52 | 0.23/0.41 | 0.27/0.45 | 0.33/0.45 | 0.37/0.58 |
| risk_gbm | passer | 0.00/0.08 | 0.00/0.08 | 0.00/0.09 | 0.00/0.09 | 0.00/0.09 |
| risk_gbm+effr_pooled | pretraining | 0.13/0.28 | 0.16/0.40 | 0.20/0.48 | 0.16/0.34 | 0.17/0.39 |
| risk_gbm+effr_pretrain_finetune | pretraining | 0.10/0.30 | 0.14/0.34 | 0.20/0.39 | 0.15/0.34 | 0.17/0.37 |
| risk_gbm+effr_sofr_only | pretraining | 0.17/0.33 | 0.18/0.40 | 0.21/0.43 | 0.19/0.45 | 0.20/0.42 |
| risk_gbm+h41 | timing | 0.00/0.08 | 0.00/0.08 | 0.00/0.09 | 0.00/0.09 | 0.00/0.09 |
| risk_gbm+hurdle_isotonic | hurdle | 0.27/0.64 | 0.30/0.58 | 0.29/0.56 | 0.30/0.66 | 0.31/0.45 |
| risk_gbm+hurdle_platt | hurdle | 0.28/0.52 | 0.30/0.40 | 0.30/0.43 | 0.30/0.45 | 0.31/0.39 |
| risk_gbm+hurdle_state_isotonic | hurdle | 0.29/0.64 | 0.31/0.57 | 0.30/0.56 | 0.30/0.66 | 0.31/0.45 |
| risk_gbm+hurdle_state_platt | hurdle | 0.30/0.51 | 0.31/0.40 | 0.31/0.49 | 0.31/0.46 | 0.31/0.42 |
| risk_gbm+latent_factor | stress_factor | 0.41/0.64 | 0.44/0.46 | 0.44/0.46 | 0.45/0.46 | 0.45/0.54 |
| risk_gbm+latent_factor_logit | stress_factor | 0.10/0.18 | 0.19/0.23 | 0.18/0.24 | 0.21/0.24 | 0.19/0.23 |
| risk_gbm+latent_factor_resid | stress_factor | 0.41/0.64 | 0.44/0.46 | 0.44/0.46 | 0.45/0.46 | 0.45/0.54 |
| risk_gbm+projected | projected_reserves | 0.21/0.62 | 0.23/0.38 | 0.27/0.45 | 0.33/0.40 | 0.37/0.45 |
| risk_gbm+settle | timing | 0.00/0.08 | 0.00/0.11 | 0.00/0.12 | 0.00/0.12 | 0.00/0.12 |
| risk_gbm+settle+h41 | timing | 0.00/0.08 | 0.00/0.11 | 0.00/0.12 | 0.00/0.12 | 0.00/0.12 |
| risk_gbm+structural | structural | 0.16/0.64 | 0.17/0.24 | 0.26/0.56 | 0.30/0.34 | 0.29/0.39 |
| risk_gbm_base | passer | 0.00/0.08 | 0.00/0.08 | 0.00/0.09 | 0.00/0.09 | 0.00/0.09 |
| risk_gbm_base+h41 | timing | 0.00/0.08 | 0.00/0.08 | 0.00/0.09 | 0.00/0.09 | 0.00/0.09 |
| risk_gbm_base+hurdle_isotonic | hurdle | 0.27/0.48 | 0.30/0.58 | 0.29/0.46 | 0.30/0.45 | 0.31/0.52 |
| risk_gbm_base+hurdle_platt | hurdle | 0.28/0.33 | 0.30/0.40 | 0.30/0.43 | 0.30/0.45 | 0.31/0.39 |
| risk_gbm_base+hurdle_state_isotonic | hurdle | 0.29/0.48 | 0.31/0.57 | 0.30/0.46 | 0.30/0.45 | 0.31/0.64 |
| risk_gbm_base+hurdle_state_platt | hurdle | 0.30/0.48 | 0.31/0.45 | 0.31/0.46 | 0.31/0.45 | 0.31/0.42 |
| risk_gbm_base+settle | timing | 0.00/0.08 | 0.00/0.11 | 0.00/0.12 | 0.00/0.12 | 0.00/0.12 |
| risk_gbm_base+settle+h41 | timing | 0.00/0.08 | 0.00/0.11 | 0.00/0.12 | 0.00/0.12 | 0.00/0.12 |
| risk_logistic | passer | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 |
| risk_logistic+h41 | timing | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 |
| risk_logistic+hurdle_isotonic | hurdle | 0.27/0.78 | 0.30/0.52 | 0.29/0.60 | 0.30/0.50 | 0.31/0.52 |
| risk_logistic+hurdle_platt | hurdle | 0.28/0.39 | 0.30/0.49 | 0.30/0.43 | 0.30/0.45 | 0.31/0.39 |
| risk_logistic+hurdle_state_isotonic | hurdle | 0.29/0.78 | 0.31/0.52 | 0.30/0.61 | 0.30/0.50 | 0.31/0.67 |
| risk_logistic+hurdle_state_platt | hurdle | 0.30/0.39 | 0.31/0.45 | 0.31/0.49 | 0.31/0.46 | 0.31/0.42 |
| risk_logistic+settle | timing | 0.00/0.00 | 0.00/0.01 | 0.00/0.01 | 0.00/0.00 | 0.00/0.00 |
| risk_logistic+settle+h41 | timing | 0.00/0.00 | 0.00/0.01 | 0.00/0.01 | 0.00/0.00 | 0.00/0.00 |
| risk_logistic_base | passer | 0.00/0.01 | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 |
| risk_logistic_base+h41 | timing | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 |
| risk_logistic_base+hurdle_isotonic | hurdle | 0.27/0.80 | 0.30/0.58 | 0.29/0.51 | 0.30/0.52 | 0.31/0.52 |
| risk_logistic_base+hurdle_platt | hurdle | 0.28/0.33 | 0.30/0.49 | 0.30/0.43 | 0.30/0.41 | 0.31/0.39 |
| risk_logistic_base+hurdle_state_isotonic | hurdle | 0.29/0.81 | 0.31/0.57 | 0.30/0.51 | 0.30/0.52 | 0.31/0.55 |
| risk_logistic_base+hurdle_state_platt | hurdle | 0.30/0.51 | 0.31/0.45 | 0.31/0.49 | 0.31/0.41 | 0.31/0.42 |
| risk_logistic_base+settle | timing | 0.00/0.01 | 0.00/0.01 | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 |
| risk_logistic_base+settle+h41 | timing | 0.00/0.00 | 0.00/0.01 | 0.00/0.01 | 0.00/0.00 | 0.00/0.00 |
| risk_quantile_skewt_base | passer | 0.00/0.00 | 0.00/0.00 | 0.00/0.14 | 0.00/0.26 | 0.00/0.32 |
| risk_quantile_skewt_base+h41 | timing | 0.00/0.00 | 0.00/0.05 | 0.00/0.04 | 0.00/0.00 | 0.00/0.29 |
| risk_quantile_skewt_base+hurdle_isotonic | hurdle | 0.27/0.68 | 0.30/0.58 | 0.29/0.47 | 0.30/0.47 | 0.31/0.47 |
| risk_quantile_skewt_base+hurdle_platt | hurdle | 0.28/0.48 | 0.30/0.43 | 0.30/0.43 | 0.30/0.41 | 0.31/0.39 |
| risk_quantile_skewt_base+hurdle_state_isotonic | hurdle | 0.29/0.48 | 0.31/0.57 | 0.30/0.57 | 0.30/0.47 | 0.31/0.47 |
| risk_quantile_skewt_base+hurdle_state_platt | hurdle | 0.30/0.48 | 0.31/0.53 | 0.31/0.47 | 0.31/0.41 | 0.31/0.42 |
| risk_quantile_skewt_base+settle | timing | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 | 0.00/0.24 | 0.00/0.00 |
| risk_quantile_skewt_base+settle+h41 | timing | 0.00/0.00 | 0.00/0.25 | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 |
| structural_liquidity | structural | 0.16/0.27 | 0.17/0.44 | 0.26/0.64 | 0.30/0.59 | 0.29/0.45 |

### 2020-03-12

| row | family | lead 1 | lead 2 | lead 3 | lead 4 | lead 5 |
|---|---|---|---|---|---|---|
| calendar_climatology | reference | 0.19/0.22 | 0.19/0.27 | 0.19/0.27 | 0.19/0.27 | 0.20/0.27 |
| effr_pooled | pretraining | 0.12/0.28 | 0.11/0.31 | 0.21/0.43 | 0.19/0.41 | 0.30/0.39 |
| effr_pretrain_finetune | pretraining | 0.10/0.25 | 0.10/0.34 | 0.21/0.39 | 0.19/0.40 | 0.30/0.37 |
| effr_sofr_only | pretraining | 0.11/0.37 | 0.11/0.42 | 0.21/0.43 | 0.20/0.45 | 0.25/0.42 |
| latent_factor | stress_factor | 0.43/0.42* | 0.43/0.44 | 0.44/0.45 | 0.44/0.46 | 0.45/0.46 |
| latent_factor_logit | stress_factor | 0.17/0.17 | 0.17/0.19 | 0.19/0.20 | 0.22/0.24 | 0.35/0.21* |
| latent_factor_resid | stress_factor | 0.43/0.42* | 0.43/0.44 | 0.44/0.45 | 0.44/0.46 | 0.45/0.46 |
| ngboost_laplace | ngboost_laplace | 0.06/0.33 | 0.06/0.30 | 0.15/0.24 | 0.10/0.30 | 0.32/0.44 |
| persistence_logistic | reference | 0.18/0.19 | 0.17/0.23 | 0.21/0.24 | 0.21/0.21 | 0.32/0.22* |
| projected_reserves | projected_reserves | 0.13/0.52 | 0.12/0.41 | 0.20/0.45 | 0.19/0.45 | 0.23/0.58 |
| risk_gbm | passer | 0.00/0.08 | 0.00/0.08 | 0.00/0.09 | 0.00/0.09 | 0.00/0.09 |
| risk_gbm+effr_pooled | pretraining | 0.12/0.28 | 0.11/0.40 | 0.21/0.48 | 0.19/0.32 | 0.30/0.39 |
| risk_gbm+effr_pretrain_finetune | pretraining | 0.10/0.30 | 0.10/0.34 | 0.21/0.39 | 0.19/0.34 | 0.30/0.37 |
| risk_gbm+effr_sofr_only | pretraining | 0.11/0.33 | 0.11/0.36 | 0.21/0.36 | 0.20/0.45 | 0.25/0.42 |
| risk_gbm+h41 | timing | 0.00/0.08 | 0.00/0.08 | 0.00/0.09 | 0.00/0.09 | 0.00/0.09 |
| risk_gbm+hurdle_isotonic | hurdle | 0.25/0.64 | 0.27/0.58 | 0.27/0.56 | 0.26/0.66 | 0.46/0.45* |
| risk_gbm+hurdle_platt | hurdle | 0.29/0.52 | 0.29/0.40 | 0.28/0.43 | 0.30/0.45 | 0.33/0.39 |
| risk_gbm+hurdle_state_isotonic | hurdle | 0.25/0.64 | 0.29/0.57 | 0.29/0.56 | 0.28/0.66 | 0.45/0.45* |
| risk_gbm+hurdle_state_platt | hurdle | 0.31/0.51 | 0.30/0.40 | 0.29/0.49 | 0.31/0.46 | 0.33/0.42 |
| risk_gbm+latent_factor | stress_factor | 0.43/0.64 | 0.43/0.46 | 0.44/0.46 | 0.44/0.46 | 0.45/0.54 |
| risk_gbm+latent_factor_logit | stress_factor | 0.17/0.18 | 0.17/0.23 | 0.19/0.24 | 0.22/0.24 | 0.35/0.23* |
| risk_gbm+latent_factor_resid | stress_factor | 0.43/0.64 | 0.43/0.46 | 0.44/0.46 | 0.44/0.46 | 0.45/0.54 |
| risk_gbm+projected | projected_reserves | 0.13/0.33 | 0.12/0.37 | 0.20/0.45 | 0.19/0.40 | 0.23/0.45 |
| risk_gbm+settle | timing | 0.00/0.08 | 0.00/0.11 | 0.00/0.12 | 0.00/0.12 | 0.00/0.12 |
| risk_gbm+settle+h41 | timing | 0.00/0.08 | 0.00/0.11 | 0.00/0.12 | 0.00/0.12 | 0.00/0.12 |
| risk_gbm+structural | structural | 0.15/0.64 | 0.14/0.24 | 0.16/0.56 | 0.15/0.30 | 0.24/0.39 |
| risk_gbm_base | passer | 0.00/0.08 | 0.00/0.08 | 0.00/0.09 | 0.00/0.09 | 0.00/0.09 |
| risk_gbm_base+h41 | timing | 0.00/0.08 | 0.00/0.08 | 0.00/0.09 | 0.00/0.09 | 0.00/0.09 |
| risk_gbm_base+hurdle_isotonic | hurdle | 0.25/0.48 | 0.27/0.58 | 0.27/0.46 | 0.26/0.45 | 0.46/0.52 |
| risk_gbm_base+hurdle_platt | hurdle | 0.29/0.33 | 0.29/0.40 | 0.28/0.43 | 0.30/0.45 | 0.33/0.39 |
| risk_gbm_base+hurdle_state_isotonic | hurdle | 0.25/0.48 | 0.29/0.57 | 0.29/0.46 | 0.28/0.45 | 0.45/0.64 |
| risk_gbm_base+hurdle_state_platt | hurdle | 0.31/0.48 | 0.30/0.45 | 0.29/0.46 | 0.31/0.45 | 0.33/0.42 |
| risk_gbm_base+settle | timing | 0.00/0.08 | 0.00/0.11 | 0.00/0.12 | 0.00/0.12 | 0.00/0.12 |
| risk_gbm_base+settle+h41 | timing | 0.00/0.08 | 0.00/0.11 | 0.00/0.12 | 0.00/0.12 | 0.00/0.12 |
| risk_logistic | passer | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 |
| risk_logistic+h41 | timing | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 |
| risk_logistic+hurdle_isotonic | hurdle | 0.25/0.78 | 0.27/0.52 | 0.27/0.60 | 0.26/0.50 | 0.46/0.52 |
| risk_logistic+hurdle_platt | hurdle | 0.29/0.39 | 0.29/0.40 | 0.28/0.43 | 0.30/0.45 | 0.33/0.39 |
| risk_logistic+hurdle_state_isotonic | hurdle | 0.25/0.78 | 0.29/0.52 | 0.29/0.61 | 0.28/0.50 | 0.45/0.67 |
| risk_logistic+hurdle_state_platt | hurdle | 0.31/0.39 | 0.30/0.45 | 0.29/0.49 | 0.31/0.46 | 0.33/0.42 |
| risk_logistic+settle | timing | 0.00/0.00 | 0.00/0.01 | 0.00/0.01 | 0.00/0.00 | 0.00/0.00 |
| risk_logistic+settle+h41 | timing | 0.00/0.00 | 0.00/0.01 | 0.00/0.01 | 0.00/0.00 | 0.00/0.00 |
| risk_logistic_base | passer | 0.00/0.01 | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 |
| risk_logistic_base+h41 | timing | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 |
| risk_logistic_base+hurdle_isotonic | hurdle | 0.25/0.80 | 0.27/0.58 | 0.27/0.51 | 0.26/0.52 | 0.46/0.52 |
| risk_logistic_base+hurdle_platt | hurdle | 0.29/0.33 | 0.29/0.38 | 0.28/0.43 | 0.30/0.41 | 0.33/0.39 |
| risk_logistic_base+hurdle_state_isotonic | hurdle | 0.25/0.81 | 0.29/0.57 | 0.29/0.51 | 0.28/0.52 | 0.45/0.55 |
| risk_logistic_base+hurdle_state_platt | hurdle | 0.31/0.51 | 0.30/0.45 | 0.29/0.49 | 0.31/0.41 | 0.33/0.42 |
| risk_logistic_base+settle | timing | 0.00/0.01 | 0.00/0.01 | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 |
| risk_logistic_base+settle+h41 | timing | 0.00/0.00 | 0.00/0.01 | 0.00/0.01 | 0.00/0.00 | 0.00/0.00 |
| risk_quantile_skewt_base | passer | 0.00/0.00 | 0.00/0.00 | 0.00/0.14 | 0.00/0.26 | 0.00/0.32 |
| risk_quantile_skewt_base+h41 | timing | 0.00/0.00 | 0.00/0.05 | 0.00/0.04 | 0.00/0.00 | 0.00/0.29 |
| risk_quantile_skewt_base+hurdle_isotonic | hurdle | 0.25/0.48 | 0.27/0.43 | 0.27/0.47 | 0.26/0.47 | 0.46/0.47 |
| risk_quantile_skewt_base+hurdle_platt | hurdle | 0.29/0.48 | 0.29/0.43 | 0.28/0.43 | 0.30/0.41 | 0.33/0.39 |
| risk_quantile_skewt_base+hurdle_state_isotonic | hurdle | 0.25/0.48 | 0.29/0.43 | 0.29/0.47 | 0.28/0.47 | 0.45/0.47 |
| risk_quantile_skewt_base+hurdle_state_platt | hurdle | 0.31/0.48 | 0.30/0.43 | 0.29/0.47 | 0.31/0.41 | 0.33/0.42 |
| risk_quantile_skewt_base+settle | timing | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 | 0.00/0.24 | 0.00/0.00 |
| risk_quantile_skewt_base+settle+h41 | timing | 0.00/0.00 | 0.00/0.25 | 0.00/0.00 | 0.00/0.00 | 0.00/0.00 |
| structural_liquidity | structural | 0.15/0.27 | 0.14/0.44 | 0.16/0.64 | 0.15/0.59 | 0.24/0.45 |

### 2024-09-30

| row | family | lead 1 | lead 2 | lead 3 | lead 4 | lead 5 |
|---|---|---|---|---|---|---|
| calendar_climatology | reference | 0.20/0.27 | 0.20/0.29 | 0.20/0.29 | 0.20/0.29 | 0.20/0.29 |
| effr_pooled | pretraining | 0.01/0.28 | 0.01/0.31 | 0.01/0.43 | 0.02/0.41 | 0.02/0.39 |
| effr_pretrain_finetune | pretraining | 0.00/0.25 | 0.00/0.34 | 0.00/0.39 | 0.00/0.40 | 0.00/0.37 |
| effr_sofr_only | pretraining | 0.00/0.37 | 0.00/0.42 | 0.00/0.43 | 0.00/0.45 | 0.00/0.42 |
| latent_factor | stress_factor | 0.12/0.42 | 0.16/0.44 | 0.17/0.45 | 0.17/0.46 | 0.17/0.46 |
| latent_factor_logit | stress_factor | 0.01/0.17 | 0.03/0.19 | 0.04/0.20 | 0.04/0.24 | 0.03/0.21 |
| latent_factor_resid | stress_factor | 0.12/0.42 | 0.16/0.44 | 0.17/0.45 | 0.17/0.46 | 0.17/0.46 |
| ngboost_laplace | ngboost_laplace | 0.03/0.33 | 0.19/0.30 | 0.20/0.24 | 0.03/0.30 | 0.05/0.32 |
| persistence_logistic | reference | 0.02/0.19 | 0.03/0.23 | 0.05/0.24 | 0.03/0.21 | 0.03/0.22 |
| projected_reserves | projected_reserves | 0.03/0.52 | 0.03/0.41 | 0.03/0.45 | 0.03/0.45 | 0.04/0.58 |
| risk_gbm | passer | 0.00/0.08 | 0.00/0.08 | 0.00/0.09 | 0.00/0.09 | 0.00/0.09 |
| risk_gbm+effr_pooled | pretraining | 0.00/0.28 | 0.00/0.40 | 0.00/0.48 | 0.00/0.32 | 0.00/0.39 |
| risk_gbm+effr_pretrain_finetune | pretraining | 0.00/0.30 | 0.00/0.34 | 0.00/0.39 | 0.00/0.34 | 0.00/0.35 |
| risk_gbm+effr_sofr_only | pretraining | 0.00/0.33 | 0.00/0.36 | 0.00/0.36 | 0.00/0.36 | 0.00/0.42 |
| risk_gbm+h41 | timing | 0.00/0.08 | 0.00/0.08 | 0.00/0.09 | 0.00/0.09 | 0.00/0.09 |
| risk_gbm+hurdle_isotonic | hurdle | 0.00/0.64 | 0.00/0.58 | 0.00/0.56 | 0.00/0.66 | 0.00/0.45 |
| risk_gbm+hurdle_platt | hurdle | 0.00/0.52 | 0.00/0.40 | 0.00/0.43 | 0.00/0.45 | 0.00/0.39 |
| risk_gbm+hurdle_state_isotonic | hurdle | 0.00/0.64 | 0.00/0.57 | 0.00/0.56 | 0.00/0.66 | 0.00/0.45 |
| risk_gbm+hurdle_state_platt | hurdle | 0.00/0.51 | 0.00/0.40 | 0.00/0.49 | 0.00/0.46 | 0.00/0.42 |
| risk_gbm+latent_factor | stress_factor | 0.00/0.43 | 0.00/0.46 | 0.00/0.46 | 0.00/0.46 | 0.00/0.46 |
| risk_gbm+latent_factor_logit | stress_factor | 0.00/0.64 | 0.00/0.23 | 0.00/0.24 | 0.00/0.24 | 0.00/0.23 |
| risk_gbm+latent_factor_resid | stress_factor | 0.00/0.43 | 0.00/0.46 | 0.00/0.46 | 0.00/0.46 | 0.00/0.46 |
| risk_gbm+projected | projected_reserves | 0.00/0.33 | 0.00/0.37 | 0.00/0.45 | 0.00/0.40 | 0.00/0.45 |
| risk_gbm+settle | timing | 0.00/0.08 | 0.00/0.11 | 0.00/0.12 | 0.00/0.12 | 0.00/0.12 |
| risk_gbm+settle+h41 | timing | 0.00/0.08 | 0.00/0.11 | 0.00/0.12 | 0.00/0.12 | 0.00/0.12 |
| risk_gbm+structural | structural | 0.00/0.64 | 0.00/0.25 | 0.00/0.26 | 0.00/0.30 | 0.00/0.39 |
| risk_gbm_base | passer | 0.00/0.08 | 0.00/0.08 | 0.00/0.09 | 0.00/0.09 | 0.01/0.09 |
| risk_gbm_base+h41 | timing | 0.00/0.08 | 0.00/0.08 | 0.00/0.09 | 0.00/0.09 | 0.00/0.09 |
| risk_gbm_base+hurdle_isotonic | hurdle | 0.00/0.48 | 0.00/0.58 | 0.00/0.46 | 0.00/0.45 | 0.01/0.46 |
| risk_gbm_base+hurdle_platt | hurdle | 0.00/0.33 | 0.00/0.40 | 0.00/0.43 | 0.00/0.45 | 0.01/0.39 |
| risk_gbm_base+hurdle_state_isotonic | hurdle | 0.00/0.48 | 0.00/0.57 | 0.00/0.46 | 0.00/0.45 | 0.01/0.45 |
| risk_gbm_base+hurdle_state_platt | hurdle | 0.00/0.48 | 0.00/0.45 | 0.00/0.46 | 0.00/0.45 | 0.01/0.42 |
| risk_gbm_base+settle | timing | 0.00/0.08 | 0.00/0.11 | 0.00/0.26 | 0.00/0.12 | 0.00/0.12 |
| risk_gbm_base+settle+h41 | timing | 0.00/0.08 | 0.00/0.11 | 0.00/0.12 | 0.00/0.27 | 0.00/0.27 |
| risk_logistic | passer | 0.02/0.04 | 0.01/0.37 | 0.03/0.08 | 0.04/0.02* | 0.02/0.12 |
| risk_logistic+h41 | timing | 0.03/0.05 | 0.01/0.40 | 0.03/0.05 | 0.03/0.08 | 0.01/0.18 |
| risk_logistic+hurdle_isotonic | hurdle | 0.02/0.78 | 0.01/0.52 | 0.03/0.60 | 0.04/0.50 | 0.02/0.46 |
| risk_logistic+hurdle_platt | hurdle | 0.02/0.39 | 0.01/0.49 | 0.03/0.43 | 0.04/0.45 | 0.02/0.39 |
| risk_logistic+hurdle_state_isotonic | hurdle | 0.02/0.78 | 0.01/0.52 | 0.03/0.61 | 0.04/0.50 | 0.02/0.45 |
| risk_logistic+hurdle_state_platt | hurdle | 0.02/0.39 | 0.01/0.45 | 0.03/0.49 | 0.04/0.46 | 0.02/0.42 |
| risk_logistic+settle | timing | 0.02/0.04 | 0.04/0.04 | 0.08/0.04* | 0.10/0.11 | 0.09/0.03* |
| risk_logistic+settle+h41 | timing | 0.03/0.05 | 0.04/0.04* | 0.08/0.03* | 0.07/0.09 | 0.06/0.03* |
| risk_logistic_base | passer | 0.01/0.07 | 0.01/0.33 | 0.01/0.37 | 0.01/0.36 | 0.01/0.43 |
| risk_logistic_base+h41 | timing | 0.02/0.08 | 0.01/0.02 | 0.01/0.35 | 0.01/0.33 | 0.01/0.50 |
| risk_logistic_base+hurdle_isotonic | hurdle | 0.01/0.80 | 0.01/0.58 | 0.01/0.60 | 0.01/0.52 | 0.01/0.46 |
| risk_logistic_base+hurdle_platt | hurdle | 0.01/0.33 | 0.01/0.38 | 0.01/0.43 | 0.01/0.45 | 0.01/0.39 |
| risk_logistic_base+hurdle_state_isotonic | hurdle | 0.01/0.81 | 0.01/0.57 | 0.01/0.61 | 0.01/0.52 | 0.01/0.45 |
| risk_logistic_base+hurdle_state_platt | hurdle | 0.01/0.51 | 0.01/0.45 | 0.01/0.49 | 0.01/0.46 | 0.01/0.42 |
| risk_logistic_base+settle | timing | 0.01/0.07 | 0.01/0.07 | 0.01/0.19 | 0.01/0.11 | 0.02/0.10 |
| risk_logistic_base+settle+h41 | timing | 0.02/0.08 | 0.01/0.08 | 0.01/0.07 | 0.01/0.12 | 0.02/0.06 |
| risk_quantile_skewt_base | passer | 0.13/0.15 | 0.02/0.11 | 0.04/0.14 | 0.05/0.26 | 0.05/0.32 |
| risk_quantile_skewt_base+h41 | timing | 0.18/0.10* | 0.05/0.33 | 0.06/0.17 | 0.04/0.20 | 0.03/0.29 |
| risk_quantile_skewt_base+hurdle_isotonic | hurdle | 0.13/0.68 | 0.02/0.58 | 0.04/0.57 | 0.05/0.55 | 0.05/0.52 |
| risk_quantile_skewt_base+hurdle_platt | hurdle | 0.13/0.48 | 0.02/0.43 | 0.04/0.43 | 0.05/0.45 | 0.05/0.47 |
| risk_quantile_skewt_base+hurdle_state_isotonic | hurdle | 0.13/0.48 | 0.02/0.57 | 0.04/0.57 | 0.05/0.55 | 0.05/0.60 |
| risk_quantile_skewt_base+hurdle_state_platt | hurdle | 0.13/0.48 | 0.02/0.45 | 0.04/0.47 | 0.05/0.46 | 0.05/0.42 |
| risk_quantile_skewt_base+settle | timing | 0.13/0.15 | 0.13/0.30 | 0.16/0.38 | 0.18/0.24 | 0.17/0.36 |
| risk_quantile_skewt_base+settle+h41 | timing | 0.18/0.10* | 0.12/0.25 | 0.14/0.11* | 0.16/0.13* | 0.19/0.18* |
| structural_liquidity | structural | 0.02/0.27 | 0.03/0.44 | 0.04/0.64 | 0.02/0.59 | 0.03/0.38 |

### 2024-12-26

| row | family | lead 1 | lead 2 | lead 3 | lead 4 | lead 5 |
|---|---|---|---|---|---|---|
| calendar_climatology | reference | 0.06/0.27 | 0.06/0.27 | 0.06/0.27 | 0.06/0.27 | 0.06/0.27 |
| effr_pooled | pretraining | 0.00/0.28 | 0.00/0.31 | 0.00/0.43 | 0.00/0.32 | 0.00/0.39 |
| effr_pretrain_finetune | pretraining | 0.00/0.25 | 0.00/0.34 | 0.00/0.39 | 0.00/0.35 | 0.00/0.37 |
| effr_sofr_only | pretraining | 0.00/0.33 | 0.00/0.42 | 0.00/0.43 | 0.00/0.45 | 0.00/0.42 |
| latent_factor | stress_factor | 0.08/0.42 | 0.12/0.44 | 0.14/0.45 | 0.16/0.46 | 0.17/0.46 |
| latent_factor_logit | stress_factor | 0.01/0.17 | 0.01/0.19 | 0.01/0.20 | 0.04/0.24 | 0.05/0.21 |
| latent_factor_resid | stress_factor | 0.09/0.42 | 0.13/0.44 | 0.14/0.45 | 0.16/0.46 | 0.17/0.46 |
| ngboost_laplace | ngboost_laplace | 0.00/0.33 | 0.00/0.30 | 0.00/0.24 | 0.00/0.30 | 0.00/0.32 |
| persistence_logistic | reference | 0.02/0.18 | 0.02/0.23 | 0.03/0.24 | 0.03/0.21 | 0.06/0.22 |
| projected_reserves | projected_reserves | 0.00/0.52 | 0.00/0.41 | 0.00/0.45 | 0.00/0.45 | 0.01/0.58 |
| risk_gbm | passer | 0.00/0.08 | 0.00/0.08 | 0.00/0.09 | 0.00/0.09 | 0.00/0.09 |
| risk_gbm+effr_pooled | pretraining | 0.00/0.28 | 0.00/0.31 | 0.00/0.48 | 0.00/0.32 | 0.00/0.32 |
| risk_gbm+effr_pretrain_finetune | pretraining | 0.00/0.30 | 0.00/0.34 | 0.00/0.34 | 0.00/0.34 | 0.00/0.35 |
| risk_gbm+effr_sofr_only | pretraining | 0.00/0.33 | 0.00/0.36 | 0.00/0.36 | 0.00/0.34 | 0.00/0.37 |
| risk_gbm+h41 | timing | 0.00/0.08 | 0.00/0.08 | 0.00/0.09 | 0.00/0.09 | 0.00/0.09 |
| risk_gbm+hurdle_isotonic | hurdle | 0.00/0.64 | 0.00/0.58 | 0.00/0.56 | 0.00/0.66 | 0.00/0.45 |
| risk_gbm+hurdle_platt | hurdle | 0.01/0.52 | 0.00/0.40 | 0.00/0.43 | 0.00/0.45 | 0.01/0.39 |
| risk_gbm+hurdle_state_isotonic | hurdle | 0.00/0.64 | 0.00/0.57 | 0.00/0.56 | 0.00/0.66 | 0.00/0.45 |
| risk_gbm+hurdle_state_platt | hurdle | 0.00/0.51 | 0.00/0.40 | 0.00/0.49 | 0.00/0.46 | 0.00/0.42 |
| risk_gbm+latent_factor | stress_factor | 0.08/0.43 | 0.12/0.46 | 0.14/0.46 | 0.16/0.46 | 0.17/0.46 |
| risk_gbm+latent_factor_logit | stress_factor | 0.01/0.18 | 0.01/0.23 | 0.01/0.24 | 0.04/0.24 | 0.05/0.23 |
| risk_gbm+latent_factor_resid | stress_factor | 0.09/0.43 | 0.13/0.46 | 0.14/0.46 | 0.16/0.46 | 0.17/0.46 |
| risk_gbm+projected | projected_reserves | 0.00/0.33 | 0.00/0.37 | 0.00/0.38 | 0.00/0.40 | 0.01/0.45 |
| risk_gbm+settle | timing | 0.00/0.08 | 0.00/0.11 | 0.00/0.12 | 0.00/0.12 | 0.00/0.12 |
| risk_gbm+settle+h41 | timing | 0.00/0.08 | 0.00/0.11 | 0.00/0.12 | 0.00/0.12 | 0.00/0.12 |
| risk_gbm+structural | structural | 0.01/0.64 | 0.02/0.24 | 0.03/0.26 | 0.02/0.26 | 0.04/0.39 |
| risk_gbm_base | passer | 0.00/0.08 | 0.00/0.08 | 0.00/0.09 | 0.00/0.09 | 0.00/0.09 |
| risk_gbm_base+h41 | timing | 0.00/0.08 | 0.00/0.08 | 0.00/0.09 | 0.00/0.09 | 0.00/0.09 |
| risk_gbm_base+hurdle_isotonic | hurdle | 0.00/0.48 | 0.00/0.58 | 0.00/0.46 | 0.00/0.45 | 0.00/0.46 |
| risk_gbm_base+hurdle_platt | hurdle | 0.01/0.33 | 0.00/0.40 | 0.00/0.43 | 0.00/0.45 | 0.01/0.39 |
| risk_gbm_base+hurdle_state_isotonic | hurdle | 0.00/0.48 | 0.00/0.57 | 0.00/0.46 | 0.00/0.45 | 0.00/0.45 |
| risk_gbm_base+hurdle_state_platt | hurdle | 0.00/0.48 | 0.00/0.45 | 0.00/0.46 | 0.00/0.45 | 0.00/0.42 |
| risk_gbm_base+settle | timing | 0.00/0.08 | 0.00/0.11 | 0.00/0.12 | 0.00/0.12 | 0.00/0.12 |
| risk_gbm_base+settle+h41 | timing | 0.00/0.08 | 0.00/0.11 | 0.00/0.12 | 0.00/0.13 | 0.00/0.13 |
| risk_logistic | passer | 0.00/0.02 | 0.00/0.37 | 0.00/0.03 | 0.00/0.02 | 0.00/0.02 |
| risk_logistic+h41 | timing | 0.00/0.03 | 0.00/0.40 | 0.00/0.03 | 0.00/0.08 | 0.00/0.01 |
| risk_logistic+hurdle_isotonic | hurdle | 0.00/0.78 | 0.00/0.52 | 0.00/0.60 | 0.00/0.50 | 0.00/0.46 |
| risk_logistic+hurdle_platt | hurdle | 0.01/0.39 | 0.00/0.49 | 0.00/0.43 | 0.00/0.45 | 0.01/0.39 |
| risk_logistic+hurdle_state_isotonic | hurdle | 0.00/0.78 | 0.00/0.52 | 0.00/0.61 | 0.00/0.50 | 0.00/0.45 |
| risk_logistic+hurdle_state_platt | hurdle | 0.00/0.39 | 0.00/0.45 | 0.00/0.49 | 0.00/0.46 | 0.00/0.42 |
| risk_logistic+settle | timing | 0.00/0.02 | 0.00/0.04 | 0.00/0.04 | 0.00/0.10 | 0.00/0.03 |
| risk_logistic+settle+h41 | timing | 0.00/0.03 | 0.00/0.04 | 0.00/0.03 | 0.00/0.07 | 0.00/0.03 |
| risk_logistic_base | passer | 0.00/0.07 | 0.00/0.02 | 0.00/0.37 | 0.00/0.36 | 0.00/0.01 |
| risk_logistic_base+h41 | timing | 0.00/0.08 | 0.00/0.02 | 0.00/0.35 | 0.00/0.33 | 0.00/0.50 |
| risk_logistic_base+hurdle_isotonic | hurdle | 0.00/0.80 | 0.00/0.58 | 0.00/0.51 | 0.00/0.52 | 0.00/0.46 |
| risk_logistic_base+hurdle_platt | hurdle | 0.01/0.33 | 0.00/0.38 | 0.00/0.43 | 0.00/0.45 | 0.01/0.39 |
| risk_logistic_base+hurdle_state_isotonic | hurdle | 0.00/0.81 | 0.00/0.57 | 0.00/0.51 | 0.00/0.52 | 0.00/0.45 |
| risk_logistic_base+hurdle_state_platt | hurdle | 0.00/0.51 | 0.00/0.45 | 0.00/0.49 | 0.00/0.46 | 0.00/0.42 |
| risk_logistic_base+settle | timing | 0.00/0.07 | 0.00/0.07 | 0.00/0.19 | 0.00/0.11 | 0.00/0.10 |
| risk_logistic_base+settle+h41 | timing | 0.00/0.08 | 0.00/0.08 | 0.00/0.07 | 0.00/0.12 | 0.00/0.06 |
| risk_quantile_skewt_base | passer | 0.00/0.13 | 0.00/0.11 | 0.00/0.14 | 0.00/0.26 | 0.00/0.32 |
| risk_quantile_skewt_base+h41 | timing | 0.00/0.10 | 0.00/0.33 | 0.00/0.17 | 0.00/0.20 | 0.00/0.29 |
| risk_quantile_skewt_base+hurdle_isotonic | hurdle | 0.00/0.48 | 0.00/0.43 | 0.00/0.47 | 0.00/0.55 | 0.00/0.46 |
| risk_quantile_skewt_base+hurdle_platt | hurdle | 0.01/0.48 | 0.00/0.43 | 0.00/0.43 | 0.00/0.45 | 0.01/0.39 |
| risk_quantile_skewt_base+hurdle_state_isotonic | hurdle | 0.00/0.48 | 0.00/0.43 | 0.00/0.47 | 0.00/0.47 | 0.00/0.47 |
| risk_quantile_skewt_base+hurdle_state_platt | hurdle | 0.00/0.48 | 0.00/0.43 | 0.00/0.47 | 0.00/0.41 | 0.00/0.42 |
| risk_quantile_skewt_base+settle | timing | 0.00/0.13 | 0.00/0.13 | 0.00/0.16 | 0.00/0.18 | 0.00/0.17 |
| risk_quantile_skewt_base+settle+h41 | timing | 0.00/0.10 | 0.00/0.12 | 0.00/0.11 | 0.00/0.13 | 0.00/0.18 |
| structural_liquidity | structural | 0.01/0.27 | 0.02/0.44 | 0.03/0.64 | 0.02/0.59 | 0.04/0.38 |

### 2025-09-30

| row | family | lead 1 | lead 2 | lead 3 | lead 4 | lead 5 |
|---|---|---|---|---|---|---|
| calendar_climatology | reference | 0.24/0.27 | 0.24/0.27 | 0.24/0.27 | 0.24/0.27 | 0.24/0.27 |
| effr_pooled | pretraining | 0.18/0.28 | 0.18/0.31 | 0.14/0.43 | 0.23/0.31 | 0.24/0.32 |
| effr_pretrain_finetune | pretraining | 0.22/0.23 | 0.21/0.34 | 0.17/0.39 | 0.30/0.35 | 0.33/0.35 |
| effr_sofr_only | pretraining | 0.18/0.33 | 0.17/0.36 | 0.14/0.36 | 0.22/0.36 | 0.23/0.37 |
| latent_factor | stress_factor | 0.20/0.42 | 0.21/0.44 | 0.16/0.45 | 0.15/0.46 | 0.16/0.46 |
| latent_factor_logit | stress_factor | 0.09/0.14 | 0.16/0.19 | 0.07/0.19 | 0.05/0.24 | 0.06/0.21 |
| latent_factor_resid | stress_factor | 0.20/0.42 | 0.21/0.44 | 0.16/0.45 | 0.15/0.46 | 0.16/0.46 |
| ngboost_laplace | ngboost_laplace | 0.62/0.33* | 0.35/0.27* | 0.36/0.23* | 0.37/0.30* | 0.35/0.32* |
| persistence_logistic | reference | 0.09/0.18 | 0.13/0.23 | 0.06/0.24 | 0.05/0.21 | 0.07/0.22 |
| projected_reserves | projected_reserves | 0.27/0.33 | 0.27/0.37 | 0.24/0.45 | 0.25/0.40 | 0.23/0.58 |
| risk_gbm | passer | 0.20/0.08* | 0.29/0.08* | 0.01/0.09 | 0.02/0.09 | 0.01/0.09 |
| risk_gbm+effr_pooled | pretraining | 0.20/0.28 | 0.29/0.31 | 0.01/0.31 | 0.02/0.32 | 0.01/0.32 |
| risk_gbm+effr_pretrain_finetune | pretraining | 0.20/0.23 | 0.29/0.34 | 0.01/0.34 | 0.02/0.34 | 0.01/0.30 |
| risk_gbm+effr_sofr_only | pretraining | 0.20/0.33 | 0.29/0.36 | 0.01/0.36 | 0.02/0.34 | 0.01/0.37 |
| risk_gbm+h41 | timing | 0.60/0.08* | 0.03/0.08 | 0.01/0.02 | 0.01/0.03 | 0.00/0.04 |
| risk_gbm+hurdle_isotonic | hurdle | 0.20/0.64 | 0.29/0.58 | 0.01/0.56 | 0.02/0.66 | 0.01/0.45 |
| risk_gbm+hurdle_platt | hurdle | 0.20/0.52 | 0.29/0.40 | 0.01/0.43 | 0.02/0.45 | 0.01/0.39 |
| risk_gbm+hurdle_state_isotonic | hurdle | 0.20/0.64 | 0.29/0.40 | 0.01/0.56 | 0.02/0.66 | 0.01/0.45 |
| risk_gbm+hurdle_state_platt | hurdle | 0.20/0.51 | 0.29/0.40 | 0.01/0.49 | 0.02/0.46 | 0.01/0.42 |
| risk_gbm+latent_factor | stress_factor | 0.20/0.43 | 0.29/0.46 | 0.01/0.46 | 0.02/0.46 | 0.01/0.46 |
| risk_gbm+latent_factor_logit | stress_factor | 0.20/0.17* | 0.29/0.23* | 0.01/0.21 | 0.02/0.24 | 0.01/0.23 |
| risk_gbm+latent_factor_resid | stress_factor | 0.20/0.43 | 0.29/0.46 | 0.01/0.46 | 0.02/0.46 | 0.01/0.46 |
| risk_gbm+projected | projected_reserves | 0.20/0.32 | 0.29/0.37 | 0.01/0.38 | 0.02/0.40 | 0.01/0.37 |
| risk_gbm+settle | timing | 0.20/0.08* | 0.94/0.11* | 0.21/0.12* | 0.01/0.12 | 0.03/0.12 |
| risk_gbm+settle+h41 | timing | 0.60/0.08* | 0.79/0.11* | 0.06/0.12 | 0.01/0.12 | 0.01/0.12 |
| risk_gbm+structural | structural | 0.20/0.64 | 0.29/0.23* | 0.01/0.26 | 0.02/0.26 | 0.01/0.39 |
| risk_gbm_base | passer | 0.03/0.03* | 0.25/0.08* | 0.03/0.05 | 0.05/0.09 | 0.07/0.09 |
| risk_gbm_base+h41 | timing | 0.11/0.02* | 0.03/0.08 | 0.01/0.09 | 0.06/0.09 | 0.01/0.09 |
| risk_gbm_base+hurdle_isotonic | hurdle | 0.03/0.48 | 0.25/0.58 | 0.03/0.46 | 0.05/0.45 | 0.07/0.46 |
| risk_gbm_base+hurdle_platt | hurdle | 0.03/0.33 | 0.25/0.40 | 0.03/0.43 | 0.05/0.45 | 0.07/0.39 |
| risk_gbm_base+hurdle_state_isotonic | hurdle | 0.03/0.48 | 0.25/0.57 | 0.03/0.46 | 0.05/0.45 | 0.07/0.45 |
| risk_gbm_base+hurdle_state_platt | hurdle | 0.03/0.48 | 0.25/0.45 | 0.03/0.46 | 0.05/0.45 | 0.07/0.42 |
| risk_gbm_base+settle | timing | 0.03/0.03* | 0.02/0.11 | 0.02/0.12 | 0.03/0.12 | 0.01/0.12 |
| risk_gbm_base+settle+h41 | timing | 0.11/0.02* | 0.03/0.11 | 0.01/0.12 | 0.01/0.12 | 0.02/0.12 |
| risk_logistic | passer | 0.43/0.04* | 0.57/0.04* | 0.27/0.03* | 0.58/0.02* | 0.64/0.02* |
| risk_logistic+h41 | timing | 0.46/0.03* | 0.51/0.04* | 0.23/0.03* | 0.33/0.08* | 0.51/0.07* |
| risk_logistic+hurdle_isotonic | hurdle | 0.43/0.78 | 0.57/0.52* | 0.27/0.60 | 0.58/0.50* | 0.64/0.46* |
| risk_logistic+hurdle_platt | hurdle | 0.43/0.39* | 0.57/0.37* | 0.27/0.37 | 0.58/0.45* | 0.64/0.39* |
| risk_logistic+hurdle_state_isotonic | hurdle | 0.43/0.78 | 0.57/0.52* | 0.27/0.61 | 0.58/0.50* | 0.64/0.45* |
| risk_logistic+hurdle_state_platt | hurdle | 0.43/0.39* | 0.57/0.45* | 0.27/0.49 | 0.58/0.46* | 0.64/0.42* |
| risk_logistic+settle | timing | 0.43/0.04* | 0.60/0.04* | 0.47/0.08* | 0.60/0.10* | 0.74/0.03* |
| risk_logistic+settle+h41 | timing | 0.46/0.03* | 0.60/0.04* | 0.44/0.05* | 0.43/0.07* | 0.72/0.03* |
| risk_logistic_base | passer | 0.39/0.04* | 0.50/0.02* | 0.31/0.05* | 0.49/0.06* | 0.49/0.01* |
| risk_logistic_base+h41 | timing | 0.46/0.03* | 0.48/0.02* | 0.26/0.05* | 0.27/0.04* | 0.34/0.03* |
| risk_logistic_base+hurdle_isotonic | hurdle | 0.39/0.80 | 0.50/0.58 | 0.31/0.51 | 0.49/0.52 | 0.49/0.46* |
| risk_logistic_base+hurdle_platt | hurdle | 0.39/0.33* | 0.50/0.38* | 0.31/0.37 | 0.49/0.41* | 0.49/0.39* |
| risk_logistic_base+hurdle_state_isotonic | hurdle | 0.39/0.81 | 0.50/0.57 | 0.31/0.51 | 0.49/0.52 | 0.49/0.45* |
| risk_logistic_base+hurdle_state_platt | hurdle | 0.39/0.51 | 0.50/0.45* | 0.31/0.49 | 0.49/0.41* | 0.49/0.42* |
| risk_logistic_base+settle | timing | 0.39/0.04* | 0.43/0.04* | 0.32/0.07* | 0.61/0.11* | 0.48/0.03* |
| risk_logistic_base+settle+h41 | timing | 0.46/0.03* | 0.50/0.04* | 0.29/0.07* | 0.43/0.12* | 0.38/0.06* |
| risk_quantile_skewt_base | passer | 0.62/0.13* | 0.62/0.11* | 0.46/0.14* | 0.48/0.16* | 0.56/0.17* |
| risk_quantile_skewt_base+h41 | timing | 0.65/0.10* | 0.63/0.13* | 0.43/0.06* | 0.46/0.15* | 0.54/0.15* |
| risk_quantile_skewt_base+hurdle_isotonic | hurdle | 0.62/0.48* | 0.62/0.43* | 0.46/0.47 | 0.48/0.47* | 0.56/0.46* |
| risk_quantile_skewt_base+hurdle_platt | hurdle | 0.62/0.48* | 0.62/0.40* | 0.46/0.43* | 0.48/0.41* | 0.56/0.39* |
| risk_quantile_skewt_base+hurdle_state_isotonic | hurdle | 0.62/0.48* | 0.62/0.43* | 0.46/0.47 | 0.48/0.47* | 0.56/0.45* |
| risk_quantile_skewt_base+hurdle_state_platt | hurdle | 0.62/0.48* | 0.62/0.43* | 0.46/0.47 | 0.48/0.41* | 0.56/0.42* |
| risk_quantile_skewt_base+settle | timing | 0.62/0.13* | 0.70/0.13* | 0.57/0.16* | 0.57/0.17* | 0.65/0.12* |
| risk_quantile_skewt_base+settle+h41 | timing | 0.65/0.10* | 0.73/0.12* | 0.55/0.11* | 0.58/0.13* | 0.65/0.18* |
| structural_liquidity | structural | 0.08/0.27 | 0.09/0.24 | 0.05/0.64 | 0.04/0.30 | 0.05/0.38 |

### 2025-12-15

| row | family | lead 1 | lead 2 | lead 3 | lead 4 | lead 5 |
|---|---|---|---|---|---|---|
| calendar_climatology | reference | 0.13/0.27 | 0.13/0.27 | 0.13/0.27 | 0.13/0.27 | 0.13/0.27 |
| effr_pooled | pretraining | 0.05/0.23 | 0.05/0.31 | 0.05/0.31 | 0.07/0.30 | 0.05/0.30 |
| effr_pretrain_finetune | pretraining | 0.05/0.22 | 0.05/0.34 | 0.04/0.34 | 0.07/0.35 | 0.05/0.33 |
| effr_sofr_only | pretraining | 0.06/0.33 | 0.06/0.36 | 0.05/0.36 | 0.08/0.36 | 0.06/0.37 |
| latent_factor | stress_factor | 0.17/0.42 | 0.18/0.44 | 0.18/0.45 | 0.18/0.46 | 0.17/0.46 |
| latent_factor_logit | stress_factor | 0.06/0.14 | 0.07/0.19 | 0.12/0.19 | 0.15/0.24 | 0.12/0.21 |
| latent_factor_resid | stress_factor | 0.17/0.42 | 0.18/0.44 | 0.18/0.45 | 0.18/0.46 | 0.17/0.46 |
| ngboost_laplace | ngboost_laplace | 0.52/0.33* | 0.10/0.27 | 0.10/0.23 | 0.13/0.30 | 0.14/0.32 |
| persistence_logistic | reference | 0.10/0.18 | 0.09/0.23 | 0.12/0.24 | 0.17/0.21 | 0.13/0.22 |
| projected_reserves | projected_reserves | 0.23/0.32 | 0.25/0.37 | 0.23/0.45 | 0.28/0.40 | 0.23/0.58 |
| risk_gbm | passer | 0.98/0.08* | 0.40/0.08* | 0.85/0.09* | 0.99/0.02* | 0.29/0.09* |
| risk_gbm+effr_pooled | pretraining | 0.98/0.23* | 0.40/0.29* | 0.85/0.31* | 0.99/0.26* | 0.29/0.30 |
| risk_gbm+effr_pretrain_finetune | pretraining | 0.98/0.23* | 0.40/0.29* | 0.85/0.34* | 0.99/0.34* | 0.29/0.30 |
| risk_gbm+effr_sofr_only | pretraining | 0.98/0.25* | 0.40/0.36* | 0.85/0.36* | 0.99/0.34* | 0.29/0.37 |
| risk_gbm+h41 | timing | 0.98/0.08* | 0.18/0.03* | 0.91/0.02* | 0.99/0.03* | 0.83/0.04* |
| risk_gbm+hurdle_isotonic | hurdle | 0.98/0.64* | 0.40/0.40* | 0.85/0.56* | 0.99/0.66* | 0.29/0.45 |
| risk_gbm+hurdle_platt | hurdle | 0.98/0.52* | 0.40/0.40* | 0.85/0.43* | 0.99/0.45* | 0.29/0.39 |
| risk_gbm+hurdle_state_isotonic | hurdle | 0.98/0.64* | 0.40/0.40* | 0.85/0.56* | 0.99/0.66* | 0.29/0.45 |
| risk_gbm+hurdle_state_platt | hurdle | 0.98/0.51* | 0.40/0.40* | 0.85/0.49* | 0.99/0.46* | 0.29/0.42 |
| risk_gbm+latent_factor | stress_factor | 0.98/0.43* | 0.40/0.46 | 0.85/0.46* | 0.99/0.46* | 0.29/0.46 |
| risk_gbm+latent_factor_logit | stress_factor | 0.98/0.17* | 0.40/0.23* | 0.85/0.21* | 0.99/0.24* | 0.29/0.23* |
| risk_gbm+latent_factor_resid | stress_factor | 0.98/0.43* | 0.40/0.46 | 0.85/0.46* | 0.99/0.46* | 0.29/0.46 |
| risk_gbm+projected | projected_reserves | 0.98/0.32* | 0.40/0.37* | 0.85/0.38* | 0.99/0.34* | 0.29/0.37 |
| risk_gbm+settle | timing | 0.98/0.08* | 0.58/0.11* | 0.94/0.12* | 1.00/0.12* | 0.95/0.03* |
| risk_gbm+settle+h41 | timing | 0.98/0.08* | 0.42/0.11* | 0.90/0.06* | 1.00/0.12* | 0.99/0.12* |
| risk_gbm+structural | structural | 0.98/0.20* | 0.40/0.23* | 0.85/0.25* | 0.99/0.25* | 0.29/0.29* |
| risk_gbm_base | passer | 0.99/0.03* | 0.21/0.08* | 0.51/0.03* | 0.83/0.05* | 0.11/0.07* |
| risk_gbm_base+h41 | timing | 0.60/0.02* | 0.21/0.01* | 0.66/0.09* | 0.95/0.06* | 0.71/0.09* |
| risk_gbm_base+hurdle_isotonic | hurdle | 0.99/0.48* | 0.21/0.40 | 0.51/0.46* | 0.83/0.45* | 0.11/0.46 |
| risk_gbm_base+hurdle_platt | hurdle | 0.99/0.33* | 0.21/0.40 | 0.51/0.43* | 0.83/0.45* | 0.11/0.39 |
| risk_gbm_base+hurdle_state_isotonic | hurdle | 0.99/0.48* | 0.21/0.57 | 0.51/0.46* | 0.83/0.45* | 0.11/0.45 |
| risk_gbm_base+hurdle_state_platt | hurdle | 0.99/0.48* | 0.21/0.45 | 0.51/0.46* | 0.83/0.45* | 0.11/0.42 |
| risk_gbm_base+settle | timing | 0.99/0.03* | 0.92/0.02* | 0.95/0.12* | 1.00/0.12* | 0.89/0.12* |
| risk_gbm_base+settle+h41 | timing | 0.60/0.02* | 0.84/0.03* | 0.99/0.06* | 1.00/0.12* | 0.96/0.12* |
| risk_logistic | passer | 0.37/0.02* | 0.14/0.02* | 0.52/0.03* | 0.60/0.02* | 0.17/0.02* |
| risk_logistic+h41 | timing | 0.29/0.03* | 0.12/0.02* | 0.49/0.03* | 0.69/0.03* | 0.27/0.01* |
| risk_logistic+hurdle_isotonic | hurdle | 0.37/0.78 | 0.14/0.52 | 0.52/0.60 | 0.60/0.50* | 0.17/0.46 |
| risk_logistic+hurdle_platt | hurdle | 0.37/0.39 | 0.14/0.37 | 0.52/0.37* | 0.60/0.45* | 0.17/0.39 |
| risk_logistic+hurdle_state_isotonic | hurdle | 0.37/0.78 | 0.14/0.52 | 0.52/0.61 | 0.60/0.50* | 0.17/0.39 |
| risk_logistic+hurdle_state_platt | hurdle | 0.37/0.39 | 0.14/0.45 | 0.52/0.49* | 0.60/0.46* | 0.17/0.39 |
| risk_logistic+settle | timing | 0.37/0.02* | 0.41/0.04* | 0.68/0.04* | 0.81/0.05* | 0.52/0.03* |
| risk_logistic+settle+h41 | timing | 0.29/0.03* | 0.40/0.04* | 0.67/0.04* | 0.85/0.06* | 0.58/0.03* |
| risk_logistic_base | passer | 0.36/0.04* | 0.22/0.02* | 0.47/0.02* | 0.56/0.06* | 0.28/0.01* |
| risk_logistic_base+h41 | timing | 0.31/0.02* | 0.20/0.02* | 0.46/0.03* | 0.63/0.04* | 0.39/0.03* |
| risk_logistic_base+hurdle_isotonic | hurdle | 0.36/0.80 | 0.22/0.50 | 0.47/0.51 | 0.56/0.49* | 0.28/0.43 |
| risk_logistic_base+hurdle_platt | hurdle | 0.36/0.33* | 0.22/0.38 | 0.47/0.37* | 0.56/0.41* | 0.28/0.39 |
| risk_logistic_base+hurdle_state_isotonic | hurdle | 0.36/0.81 | 0.22/0.50 | 0.47/0.51 | 0.56/0.49* | 0.28/0.43 |
| risk_logistic_base+hurdle_state_platt | hurdle | 0.36/0.39 | 0.22/0.38 | 0.47/0.49 | 0.56/0.41* | 0.28/0.42 |
| risk_logistic_base+settle | timing | 0.36/0.04* | 0.42/0.04* | 0.69/0.06* | 0.75/0.06* | 0.55/0.03* |
| risk_logistic_base+settle+h41 | timing | 0.31/0.02* | 0.41/0.04* | 0.69/0.06* | 0.77/0.05* | 0.59/0.03* |
| risk_quantile_skewt_base | passer | 0.28/0.13* | 0.24/0.11* | 0.32/0.14* | 0.43/0.16* | 0.22/0.17* |
| risk_quantile_skewt_base+h41 | timing | 0.26/0.10* | 0.22/0.13* | 0.33/0.06* | 0.43/0.15* | 0.29/0.15* |
| risk_quantile_skewt_base+hurdle_isotonic | hurdle | 0.28/0.48 | 0.24/0.43 | 0.32/0.46 | 0.43/0.47 | 0.22/0.46 |
| risk_quantile_skewt_base+hurdle_platt | hurdle | 0.28/0.48 | 0.24/0.40 | 0.32/0.43 | 0.43/0.41* | 0.22/0.39 |
| risk_quantile_skewt_base+hurdle_state_isotonic | hurdle | 0.28/0.48 | 0.24/0.43 | 0.32/0.46 | 0.43/0.47 | 0.22/0.45 |
| risk_quantile_skewt_base+hurdle_state_platt | hurdle | 0.28/0.48 | 0.24/0.43 | 0.32/0.46 | 0.43/0.41* | 0.22/0.42 |
| risk_quantile_skewt_base+settle | timing | 0.28/0.13* | 0.27/0.12* | 0.48/0.10* | 0.69/0.10* | 0.38/0.12* |
| risk_quantile_skewt_base+settle+h41 | timing | 0.26/0.10* | 0.27/0.12* | 0.46/0.09* | 0.76/0.13* | 0.51/0.12* |
| structural_liquidity | structural | 0.10/0.27 | 0.08/0.24 | 0.10/0.26 | 0.14/0.30 | 0.11/0.29 |

### 2025-12-26

| row | family | lead 1 | lead 2 | lead 3 | lead 4 | lead 5 |
|---|---|---|---|---|---|---|
| calendar_climatology | reference | 0.06/0.27 | 0.06/0.27 | 0.06/0.27 | 0.06/0.27 | 0.06/0.27 |
| effr_pooled | pretraining | 0.02/0.23 | 0.02/0.31 | 0.01/0.31 | 0.01/0.30 | 0.02/0.30 |
| effr_pretrain_finetune | pretraining | 0.04/0.22 | 0.03/0.34 | 0.02/0.34 | 0.02/0.35 | 0.02/0.33 |
| effr_sofr_only | pretraining | 0.04/0.33 | 0.03/0.36 | 0.02/0.36 | 0.02/0.36 | 0.03/0.37 |
| latent_factor | stress_factor | 0.21/0.41 | 0.21/0.44 | 0.17/0.45 | 0.17/0.46 | 0.17/0.46 |
| latent_factor_logit | stress_factor | 0.10/0.14 | 0.15/0.19 | 0.09/0.19 | 0.09/0.24 | 0.13/0.21 |
| latent_factor_resid | stress_factor | 0.21/0.41 | 0.21/0.44 | 0.18/0.45 | 0.17/0.46 | 0.17/0.46 |
| ngboost_laplace | ngboost_laplace | 0.47/0.33* | 0.11/0.27 | 0.09/0.23 | 0.11/0.30 | 0.10/0.32 |
| persistence_logistic | reference | 0.10/0.18 | 0.13/0.23 | 0.10/0.24 | 0.10/0.21 | 0.15/0.22 |
| projected_reserves | projected_reserves | 0.05/0.31 | 0.04/0.37 | 0.05/0.45 | 0.05/0.40 | 0.06/0.58 |
| risk_gbm | passer | 0.87/0.08* | 0.00/0.08 | 0.00/0.09 | 0.00/0.02 | 0.00/0.09 |
| risk_gbm+effr_pooled | pretraining | 0.87/0.23* | 0.02/0.29 | 0.01/0.31 | 0.01/0.26 | 0.02/0.30 |
| risk_gbm+effr_pretrain_finetune | pretraining | 0.87/0.23* | 0.03/0.29 | 0.02/0.34 | 0.02/0.34 | 0.02/0.30 |
| risk_gbm+effr_sofr_only | pretraining | 0.87/0.25* | 0.03/0.36 | 0.02/0.36 | 0.02/0.34 | 0.03/0.37 |
| risk_gbm+h41 | timing | 0.87/0.08* | 0.00/0.03 | 0.00/0.02 | 0.00/0.03 | 0.00/0.04 |
| risk_gbm+hurdle_isotonic | hurdle | 0.87/0.64* | 0.02/0.40 | 0.03/0.56 | 0.02/0.66 | 0.03/0.45 |
| risk_gbm+hurdle_platt | hurdle | 0.87/0.52* | 0.04/0.40 | 0.02/0.43 | 0.03/0.45 | 0.04/0.39 |
| risk_gbm+hurdle_state_isotonic | hurdle | 0.87/0.64* | 0.16/0.40 | 0.16/0.56 | 0.16/0.66 | 0.16/0.45 |
| risk_gbm+hurdle_state_platt | hurdle | 0.87/0.51* | 0.14/0.40 | 0.12/0.49 | 0.12/0.46 | 0.13/0.42 |
| risk_gbm+latent_factor | stress_factor | 0.87/0.43* | 0.21/0.46 | 0.17/0.46 | 0.17/0.46 | 0.17/0.46 |
| risk_gbm+latent_factor_logit | stress_factor | 0.87/0.17* | 0.15/0.23 | 0.09/0.21 | 0.09/0.24 | 0.13/0.23 |
| risk_gbm+latent_factor_resid | stress_factor | 0.87/0.43* | 0.21/0.46 | 0.18/0.46 | 0.17/0.46 | 0.17/0.46 |
| risk_gbm+projected | projected_reserves | 0.87/0.32* | 0.04/0.37 | 0.05/0.38 | 0.05/0.34 | 0.06/0.37 |
| risk_gbm+settle | timing | 0.87/0.08* | 0.99/0.11* | 0.51/0.12* | 0.82/0.12* | 0.81/0.03* |
| risk_gbm+settle+h41 | timing | 0.87/0.08* | 0.99/0.11* | 0.38/0.06* | 0.80/0.12* | 0.94/0.12* |
| risk_gbm+structural | structural | 0.87/0.20* | 0.10/0.23 | 0.07/0.25 | 0.07/0.25 | 0.11/0.29 |
| risk_gbm_base | passer | 0.92/0.03* | 0.00/0.08 | 0.00/0.03 | 0.00/0.05 | 0.00/0.07 |
| risk_gbm_base+h41 | timing | 0.97/0.02* | 0.00/0.01 | 0.00/0.09 | 0.00/0.06 | 0.00/0.09 |
| risk_gbm_base+hurdle_isotonic | hurdle | 0.92/0.48* | 0.02/0.40 | 0.03/0.46 | 0.02/0.45 | 0.03/0.46 |
| risk_gbm_base+hurdle_platt | hurdle | 0.92/0.33* | 0.04/0.40 | 0.02/0.43 | 0.03/0.45 | 0.04/0.39 |
| risk_gbm_base+hurdle_state_isotonic | hurdle | 0.92/0.48* | 0.16/0.57 | 0.16/0.46 | 0.16/0.45 | 0.16/0.45 |
| risk_gbm_base+hurdle_state_platt | hurdle | 0.92/0.48* | 0.14/0.45 | 0.12/0.46 | 0.12/0.45 | 0.13/0.42 |
| risk_gbm_base+settle | timing | 0.92/0.03* | 0.99/0.02* | 0.96/0.12* | 0.97/0.12* | 0.79/0.12* |
| risk_gbm_base+settle+h41 | timing | 0.97/0.02* | 0.99/0.03* | 0.97/0.06* | 0.99/0.12* | 0.96/0.12* |
| risk_logistic | passer | 0.24/0.02* | 0.00/0.02 | 0.00/0.03 | 0.00/0.02 | 0.00/0.02 |
| risk_logistic+h41 | timing | 0.23/0.03* | 0.00/0.02 | 0.00/0.03 | 0.00/0.03 | 0.00/0.01 |
| risk_logistic+hurdle_isotonic | hurdle | 0.24/0.78 | 0.02/0.52 | 0.03/0.60 | 0.02/0.50 | 0.03/0.46 |
| risk_logistic+hurdle_platt | hurdle | 0.24/0.37 | 0.04/0.37 | 0.02/0.37 | 0.03/0.45 | 0.04/0.39 |
| risk_logistic+hurdle_state_isotonic | hurdle | 0.24/0.78 | 0.16/0.52 | 0.16/0.61 | 0.16/0.50 | 0.16/0.39 |
| risk_logistic+hurdle_state_platt | hurdle | 0.24/0.37 | 0.14/0.45 | 0.12/0.49 | 0.12/0.46 | 0.13/0.39 |
| risk_logistic+settle | timing | 0.24/0.02* | 0.34/0.04* | 0.21/0.04* | 0.19/0.05* | 0.46/0.03* |
| risk_logistic+settle+h41 | timing | 0.23/0.03* | 0.33/0.04* | 0.19/0.04* | 0.30/0.06* | 0.49/0.03* |
| risk_logistic_base | passer | 0.21/0.04* | 0.00/0.02 | 0.00/0.02 | 0.00/0.06 | 0.00/0.01 |
| risk_logistic_base+h41 | timing | 0.20/0.02* | 0.00/0.02 | 0.00/0.03 | 0.00/0.04 | 0.00/0.03 |
| risk_logistic_base+hurdle_isotonic | hurdle | 0.21/0.80 | 0.02/0.50 | 0.03/0.51 | 0.02/0.49 | 0.03/0.43 |
| risk_logistic_base+hurdle_platt | hurdle | 0.21/0.33 | 0.04/0.38 | 0.02/0.37 | 0.03/0.41 | 0.04/0.39 |
| risk_logistic_base+hurdle_state_isotonic | hurdle | 0.21/0.81 | 0.16/0.50 | 0.16/0.51 | 0.16/0.49 | 0.16/0.43 |
| risk_logistic_base+hurdle_state_platt | hurdle | 0.21/0.36 | 0.14/0.38 | 0.12/0.49 | 0.12/0.41 | 0.13/0.42 |
| risk_logistic_base+settle | timing | 0.21/0.04* | 0.35/0.04* | 0.30/0.06* | 0.26/0.06* | 0.37/0.03* |
| risk_logistic_base+settle+h41 | timing | 0.20/0.02* | 0.34/0.04* | 0.26/0.06* | 0.36/0.05* | 0.49/0.03* |
| risk_quantile_skewt_base | passer | 0.28/0.13* | 0.00/0.11 | 0.00/0.14 | 0.00/0.16 | 0.00/0.17 |
| risk_quantile_skewt_base+h41 | timing | 0.29/0.10* | 0.00/0.13 | 0.00/0.06 | 0.00/0.15 | 0.00/0.15 |
| risk_quantile_skewt_base+hurdle_isotonic | hurdle | 0.28/0.48 | 0.02/0.43 | 0.03/0.46 | 0.02/0.47 | 0.03/0.46 |
| risk_quantile_skewt_base+hurdle_platt | hurdle | 0.28/0.48 | 0.04/0.40 | 0.02/0.43 | 0.03/0.41 | 0.04/0.39 |
| risk_quantile_skewt_base+hurdle_state_isotonic | hurdle | 0.28/0.48 | 0.16/0.43 | 0.16/0.46 | 0.16/0.47 | 0.16/0.45 |
| risk_quantile_skewt_base+hurdle_state_platt | hurdle | 0.28/0.48 | 0.14/0.43 | 0.12/0.46 | 0.12/0.41 | 0.13/0.42 |
| risk_quantile_skewt_base+settle | timing | 0.28/0.13* | 0.53/0.12* | 0.34/0.10* | 0.30/0.10* | 0.49/0.12* |
| risk_quantile_skewt_base+settle+h41 | timing | 0.29/0.10* | 0.53/0.12* | 0.30/0.09* | 0.35/0.13* | 0.52/0.12* |
| structural_liquidity | structural | 0.08/0.27 | 0.10/0.24 | 0.07/0.26 | 0.07/0.30 | 0.11/0.29 |

## Table 5. Scheduled events known at the decision (lead 1 and lead 5)

### 2018-11-15

* lead 1 (origin 2018-11-14): target-day calendar {'days_to_month_end': 15.0, 'quarter_end': 0.0, 'tax_date': 0.0}; origin-day calendar {'days_to_month_end': 16.0, 'quarter_end': 0.0, 'tax_date': 0.0}; settlement due on the target day (bills, coupons, SOMA; public then only at lead 1) {'treasury_settlement': 247.0, 'treasury_settlement_bills': 164.0, 'treasury_settlement_coupons': 83.0, 'treasury_settlement_soma': 16.9262542}; announced net settlement of the next 1 to 5 days [5.314000000000007, 5.314000000000007, 5.314000000000007, 5.314000000000007, 5.314000000000007]; FOMC statement days ['2018-11-08']; register entries announced in the 10 days before []; pending ['debt_ceiling-20180209r']; in force [('balance_sheet', 'qt_start', '2017-10-01'), ('debt_ceiling', 'suspension', '2018-02-09'), ('iorb_rate', 'set_rate', '2018-09-27')]
* lead 5 (origin 2018-11-07): target-day calendar {'days_to_month_end': 15.0, 'quarter_end': 0.0, 'tax_date': 0.0}; origin-day calendar {'days_to_month_end': 23.0, 'quarter_end': 0.0, 'tax_date': 0.0}; settlement due on the target day (bills, coupons, SOMA; public then only at lead 1) {'treasury_settlement': None, 'treasury_settlement_bills': None, 'treasury_settlement_coupons': None, 'treasury_settlement_soma': None}; announced net settlement of the next 1 to 5 days [37.035, 37.035, 37.035, 37.035, 11.346999999999994]; FOMC statement days ['2018-11-08']; register entries announced in the 10 days before []; pending ['debt_ceiling-20180209r']; in force [('balance_sheet', 'qt_start', '2017-10-01'), ('debt_ceiling', 'suspension', '2018-02-09'), ('iorb_rate', 'set_rate', '2018-09-27')]

### 2018-11-30

* lead 1 (origin 2018-11-29): target-day calendar {'days_to_month_end': 0.0, 'quarter_end': 0.0, 'tax_date': 0.0}; origin-day calendar {'days_to_month_end': 1.0, 'quarter_end': 0.0, 'tax_date': 0.0}; settlement due on the target day (bills, coupons, SOMA; public then only at lead 1) {'treasury_settlement': 140.0, 'treasury_settlement_bills': 0.0, 'treasury_settlement_coupons': 140.0, 'treasury_settlement_soma': 12.2940816}; announced net settlement of the next 1 to 5 days [70.843, 70.843, 70.843, 11.838000000000008, 11.838000000000008]; FOMC statement days []; register entries announced in the 10 days before []; pending ['debt_ceiling-20180209r']; in force [('balance_sheet', 'qt_start', '2017-10-01'), ('debt_ceiling', 'suspension', '2018-02-09'), ('iorb_rate', 'set_rate', '2018-09-27')]
* lead 5 (origin 2018-11-23): target-day calendar {'days_to_month_end': 0.0, 'quarter_end': 0.0, 'tax_date': 0.0}; origin-day calendar {'days_to_month_end': 7.0, 'quarter_end': 0.0, 'tax_date': 0.0}; settlement due on the target day (bills, coupons, SOMA; public then only at lead 1) {'treasury_settlement': None, 'treasury_settlement_bills': None, 'treasury_settlement_coupons': None, 'treasury_settlement_soma': None}; announced net settlement of the next 1 to 5 days [0.0, 0.0, 0.0, -62.998999999999995, 7.844000000000008]; FOMC statement days []; register entries announced in the 10 days before []; pending ['debt_ceiling-20180209r']; in force [('balance_sheet', 'qt_start', '2017-10-01'), ('debt_ceiling', 'suspension', '2018-02-09'), ('iorb_rate', 'set_rate', '2018-09-27')]

### 2018-12-17

* lead 1 (origin 2018-12-14): target-day calendar {'days_to_month_end': 14.0, 'quarter_end': 0.0, 'tax_date': 1.0}; origin-day calendar {'days_to_month_end': 17.0, 'quarter_end': 0.0, 'tax_date': 0.0}; settlement due on the target day (bills, coupons, SOMA; public then only at lead 1) {'treasury_settlement': 78.0, 'treasury_settlement_bills': 0.0, 'treasury_settlement_coupons': 78.0, 'treasury_settlement_soma': 0.0}; announced net settlement of the next 1 to 5 days [30.012, 25.013999999999996, 25.013999999999996, 10.013999999999996, 10.013999999999996]; FOMC statement days []; register entries announced in the 10 days before []; pending ['debt_ceiling-20180209r']; in force [('balance_sheet', 'qt_start', '2017-10-01'), ('debt_ceiling', 'suspension', '2018-02-09'), ('iorb_rate', 'set_rate', '2018-09-27')]
* lead 5 (origin 2018-12-10): target-day calendar {'days_to_month_end': 14.0, 'quarter_end': 0.0, 'tax_date': 1.0}; origin-day calendar {'days_to_month_end': 21.0, 'quarter_end': 0.0, 'tax_date': 0.0}; settlement due on the target day (bills, coupons, SOMA; public then only at lead 1) {'treasury_settlement': None, 'treasury_settlement_bills': None, 'treasury_settlement_coupons': None, 'treasury_settlement_soma': None}; announced net settlement of the next 1 to 5 days [-5.102000000000004, -5.102000000000004, -20.10900000000001, -20.10900000000001, 9.902999999999992]; FOMC statement days []; register entries announced in the 10 days before []; pending ['debt_ceiling-20180209r']; in force [('balance_sheet', 'qt_start', '2017-10-01'), ('debt_ceiling', 'suspension', '2018-02-09'), ('iorb_rate', 'set_rate', '2018-09-27')]

### 2018-12-28

* lead 1 (origin 2018-12-27): target-day calendar {'days_to_month_end': 3.0, 'quarter_end': 0.0, 'tax_date': 0.0}; origin-day calendar {'days_to_month_end': 4.0, 'quarter_end': 0.0, 'tax_date': 0.0}; settlement due on the target day (bills, coupons, SOMA; public then only at lead 1) {'treasury_settlement': 18.0, 'treasury_settlement_bills': 0.0, 'treasury_settlement_coupons': 18.0, 'treasury_settlement_soma': 0.0}; announced net settlement of the next 1 to 5 days [18.0, 68.82, 68.818, 59.836, 59.836]; FOMC statement days ['2018-12-19']; register entries announced in the 10 days before ['iorb-20181219', 'on_rrp-20181219']; pending ['debt_ceiling-20180209r']; in force [('balance_sheet', 'qt_start', '2017-10-01'), ('debt_ceiling', 'suspension', '2018-02-09'), ('iorb_rate', 'set_rate', '2018-12-20')]
* lead 5 (origin 2018-12-20): target-day calendar {'days_to_month_end': 3.0, 'quarter_end': 0.0, 'tax_date': 0.0}; origin-day calendar {'days_to_month_end': 11.0, 'quarter_end': 0.0, 'tax_date': 0.0}; settlement due on the target day (bills, coupons, SOMA; public then only at lead 1) {'treasury_settlement': None, 'treasury_settlement_bills': None, 'treasury_settlement_coupons': None, 'treasury_settlement_soma': None}; announced net settlement of the next 1 to 5 days [0.0, 0.0, -4.998000000000005, -19.992000000000004, -1.9920000000000044]; FOMC statement days ['2018-12-19']; register entries announced in the 10 days before ['iorb-20181219', 'on_rrp-20181219']; pending ['debt_ceiling-20180209r']; in force [('balance_sheet', 'qt_start', '2017-10-01'), ('debt_ceiling', 'suspension', '2018-02-09'), ('iorb_rate', 'set_rate', '2018-12-20')]

### 2020-03-04

* lead 1 (origin 2020-03-03): target-day calendar {'days_to_month_end': 27.0, 'quarter_end': 0.0, 'tax_date': 0.0}; origin-day calendar {'days_to_month_end': 28.0, 'quarter_end': 0.0, 'tax_date': 0.0}; settlement due on the target day (bills, coupons, SOMA; public then only at lead 1) {'treasury_settlement': 0.0, 'treasury_settlement_bills': 0.0, 'treasury_settlement_coupons': 0.0, 'treasury_settlement_soma': 0.0}; announced net settlement of the next 1 to 5 days [0.0, 5.007000000000005, 5.007000000000005, 5.007000000000005, 15.297000000000011]; FOMC statement days []; register entries announced in the 10 days before ['iorb-20200303', 'on_rrp-20200303']; pending ['debt_ceiling-20190802r', 'iorb-20200303', 'on_rrp-20200303']; in force [('balance_sheet', 'qt_end', '2019-08-01'), ('debt_ceiling', 'suspension', '2019-08-02'), ('reserve_management', 'bill_purchases_and_repo', '2019-10-15'), ('iorb_rate', 'set_rate', '2020-01-30')]
* lead 5 (origin 2020-02-26): target-day calendar {'days_to_month_end': 27.0, 'quarter_end': 0.0, 'tax_date': 0.0}; origin-day calendar {'days_to_month_end': 3.0, 'quarter_end': 0.0, 'tax_date': 0.0}; settlement due on the target day (bills, coupons, SOMA; public then only at lead 1) {'treasury_settlement': None, 'treasury_settlement_bills': None, 'treasury_settlement_coupons': None, 'treasury_settlement_soma': None}; announced net settlement of the next 1 to 5 days [-0.6650000000000063, 25.334999999999994, 56.589, 71.91, 71.91]; FOMC statement days []; register entries announced in the 10 days before []; pending ['debt_ceiling-20190802r']; in force [('balance_sheet', 'qt_end', '2019-08-01'), ('debt_ceiling', 'suspension', '2019-08-02'), ('reserve_management', 'bill_purchases_and_repo', '2019-10-15'), ('iorb_rate', 'set_rate', '2020-01-30')]

### 2020-03-12

* lead 1 (origin 2020-03-11): target-day calendar {'days_to_month_end': 19.0, 'quarter_end': 0.0, 'tax_date': 0.0}; origin-day calendar {'days_to_month_end': 20.0, 'quarter_end': 0.0, 'tax_date': 0.0}; settlement due on the target day (bills, coupons, SOMA; public then only at lead 1) {'treasury_settlement': 78.0, 'treasury_settlement_bills': 78.0, 'treasury_settlement_coupons': 0.0, 'treasury_settlement_soma': 3.346}; announced net settlement of the next 1 to 5 days [-42.655, -42.655, -12.504999999999999, -5.839999999999993, -5.839999999999993]; FOMC statement days []; register entries announced in the 10 days before ['iorb-20200303', 'on_rrp-20200303']; pending ['debt_ceiling-20190802r']; in force [('balance_sheet', 'qt_end', '2019-08-01'), ('debt_ceiling', 'suspension', '2019-08-02'), ('reserve_management', 'bill_purchases_and_repo', '2019-10-15'), ('iorb_rate', 'set_rate', '2020-03-04')]
* lead 5 (origin 2020-03-05): target-day calendar {'days_to_month_end': 19.0, 'quarter_end': 0.0, 'tax_date': 0.0}; origin-day calendar {'days_to_month_end': 26.0, 'quarter_end': 0.0, 'tax_date': 0.0}; settlement due on the target day (bills, coupons, SOMA; public then only at lead 1) {'treasury_settlement': None, 'treasury_settlement_bills': None, 'treasury_settlement_coupons': None, 'treasury_settlement_soma': None}; announced net settlement of the next 1 to 5 days [0.0, 0.0, 10.290000000000006, 10.290000000000006, -32.364999999999995]; FOMC statement days []; register entries announced in the 10 days before ['iorb-20200303', 'on_rrp-20200303']; pending ['debt_ceiling-20190802r']; in force [('balance_sheet', 'qt_end', '2019-08-01'), ('debt_ceiling', 'suspension', '2019-08-02'), ('reserve_management', 'bill_purchases_and_repo', '2019-10-15'), ('iorb_rate', 'set_rate', '2020-03-04')]

### 2024-09-30

* lead 1 (origin 2024-09-27): target-day calendar {'days_to_month_end': 0.0, 'quarter_end': 1.0, 'tax_date': 0.0}; origin-day calendar {'days_to_month_end': 3.0, 'quarter_end': 0.0, 'tax_date': 0.0}; settlement due on the target day (bills, coupons, SOMA; public then only at lead 1) {'treasury_settlement': 213.0, 'treasury_settlement_bills': 0.0, 'treasury_settlement_coupons': 213.0, 'treasury_settlement_soma': 4.3970638}; announced net settlement of the next 1 to 5 days [23.198000000000008, 30.217000000000013, 30.217000000000013, 37.22999999999999, 37.22999999999999]; FOMC statement days ['2024-09-18']; register entries announced in the 10 days before ['iorb-20240918', 'on_rrp-20240918', 'standing_repo-20240918']; pending ['debt_ceiling-20230603r']; in force [('reserve_management', 'bill_purchases_and_repo', '2019-10-15'), ('slr', 'exclusion_expiry', '2021-04-01'), ('debt_ceiling', 'suspension', '2023-06-03'), ('balance_sheet', 'qt_taper', '2024-06-01'), ('iorb_rate', 'set_rate', '2024-09-19'), ('standing_repo', 'change', '2024-09-19')]
* lead 5 (origin 2024-09-23): target-day calendar {'days_to_month_end': 0.0, 'quarter_end': 1.0, 'tax_date': 0.0}; origin-day calendar {'days_to_month_end': 7.0, 'quarter_end': 0.0, 'tax_date': 0.0}; settlement due on the target day (bills, coupons, SOMA; public then only at lead 1) {'treasury_settlement': None, 'treasury_settlement_bills': None, 'treasury_settlement_coupons': None, 'treasury_settlement_soma': None}; announced net settlement of the next 1 to 5 days [-19.966000000000008, -19.966000000000008, -28.958, -0.9579999999999984, 22.24000000000001]; FOMC statement days ['2024-09-18']; register entries announced in the 10 days before ['iorb-20240918', 'on_rrp-20240918', 'standing_repo-20240918']; pending ['debt_ceiling-20230603r']; in force [('reserve_management', 'bill_purchases_and_repo', '2019-10-15'), ('slr', 'exclusion_expiry', '2021-04-01'), ('debt_ceiling', 'suspension', '2023-06-03'), ('balance_sheet', 'qt_taper', '2024-06-01'), ('iorb_rate', 'set_rate', '2024-09-19'), ('standing_repo', 'change', '2024-09-19')]

### 2024-12-26

* lead 1 (origin 2024-12-24): target-day calendar {'days_to_month_end': 5.0, 'quarter_end': 0.0, 'tax_date': 0.0}; origin-day calendar {'days_to_month_end': 7.0, 'quarter_end': 0.0, 'tax_date': 0.0}; settlement due on the target day (bills, coupons, SOMA; public then only at lead 1) {'treasury_settlement': 266.0, 'treasury_settlement_bills': 266.0, 'treasury_settlement_coupons': 0.0, 'treasury_settlement_soma': 3.9358655}; announced net settlement of the next 1 to 5 days [-43.976, -15.975999999999999, -15.975999999999999, -80.91299999999997, -80.91299999999997]; FOMC statement days ['2024-12-18']; register entries announced in the 10 days before ['iorb-20241218', 'on_rrp-20241218', 'standing_repo-20241218']; pending ['debt_ceiling-20230603r']; in force [('reserve_management', 'bill_purchases_and_repo', '2019-10-15'), ('slr', 'exclusion_expiry', '2021-04-01'), ('debt_ceiling', 'suspension', '2023-06-03'), ('balance_sheet', 'qt_taper', '2024-06-01'), ('iorb_rate', 'set_rate', '2024-12-19'), ('standing_repo', 'change', '2024-12-19')]
* lead 5 (origin 2024-12-18): target-day calendar {'days_to_month_end': 5.0, 'quarter_end': 0.0, 'tax_date': 0.0}; origin-day calendar {'days_to_month_end': 13.0, 'quarter_end': 0.0, 'tax_date': 1.0}; settlement due on the target day (bills, coupons, SOMA; public then only at lead 1) {'treasury_settlement': None, 'treasury_settlement_bills': None, 'treasury_settlement_coupons': None, 'treasury_settlement_soma': None}; announced net settlement of the next 1 to 5 days [-7.979000000000013, -7.979000000000013, -7.979000000000013, -33.96000000000001, -33.96000000000001]; FOMC statement days ['2024-12-18']; register entries announced in the 10 days before ['iorb-20241218', 'on_rrp-20241218', 'standing_repo-20241218']; pending ['debt_ceiling-20230603r', 'iorb-20241218', 'on_rrp-20241218', 'standing_repo-20241218']; in force [('reserve_management', 'bill_purchases_and_repo', '2019-10-15'), ('slr', 'exclusion_expiry', '2021-04-01'), ('debt_ceiling', 'suspension', '2023-06-03'), ('balance_sheet', 'qt_taper', '2024-06-01'), ('iorb_rate', 'set_rate', '2024-11-08'), ('standing_repo', 'change', '2024-11-08')]

### 2025-09-30

* lead 1 (origin 2025-09-29): target-day calendar {'days_to_month_end': 0.0, 'quarter_end': 1.0, 'tax_date': 0.0}; origin-day calendar {'days_to_month_end': 1.0, 'quarter_end': 0.0, 'tax_date': 0.0}; settlement due on the target day (bills, coupons, SOMA; public then only at lead 1) {'treasury_settlement': 465.0, 'treasury_settlement_bills': 250.0, 'treasury_settlement_coupons': 215.0, 'treasury_settlement_soma': 12.5828329}; announced net settlement of the next 1 to 5 days [-23.322000000000003, -23.322000000000003, -13.295000000000016, -13.295000000000016, -13.295000000000016]; FOMC statement days []; register entries announced in the 10 days before []; pending ['slr-20250627']; in force [('reserve_management', 'bill_purchases_and_repo', '2019-10-15'), ('slr', 'exclusion_expiry', '2021-04-01'), ('balance_sheet', 'qt_taper', '2025-04-01'), ('debt_ceiling', 'increase', '2025-07-04'), ('iorb_rate', 'set_rate', '2025-09-18'), ('standing_repo', 'change', '2025-09-18')]
* lead 5 (origin 2025-09-23): target-day calendar {'days_to_month_end': 0.0, 'quarter_end': 1.0, 'tax_date': 0.0}; origin-day calendar {'days_to_month_end': 7.0, 'quarter_end': 0.0, 'tax_date': 0.0}; settlement due on the target day (bills, coupons, SOMA; public then only at lead 1) {'treasury_settlement': None, 'treasury_settlement_bills': None, 'treasury_settlement_coupons': None, 'treasury_settlement_soma': None}; announced net settlement of the next 1 to 5 days [0.0, 11.007000000000005, 39.007000000000005, 39.007000000000005, 15.685000000000002]; FOMC statement days []; register entries announced in the 10 days before ['iorb-20250917', 'on_rrp-20250917', 'standing_repo-20250917']; pending ['slr-20250627']; in force [('reserve_management', 'bill_purchases_and_repo', '2019-10-15'), ('slr', 'exclusion_expiry', '2021-04-01'), ('balance_sheet', 'qt_taper', '2025-04-01'), ('debt_ceiling', 'increase', '2025-07-04'), ('iorb_rate', 'set_rate', '2025-09-18'), ('standing_repo', 'change', '2025-09-18')]

### 2025-12-15

* lead 1 (origin 2025-12-12): target-day calendar {'days_to_month_end': 16.0, 'quarter_end': 0.0, 'tax_date': 1.0}; origin-day calendar {'days_to_month_end': 19.0, 'quarter_end': 0.0, 'tax_date': 0.0}; settlement due on the target day (bills, coupons, SOMA; public then only at lead 1) {'treasury_settlement': 119.0, 'treasury_settlement_bills': 0.0, 'treasury_settlement_coupons': 119.0, 'treasury_settlement_soma': 0.0}; announced net settlement of the next 1 to 5 days [39.001999999999995, 3.0130000000000194, 3.0130000000000194, -3.992999999999981, -3.992999999999981]; FOMC statement days []; register entries announced in the 10 days before ['iorb-20251210', 'on_rrp-20251210', 'reserve_management-20251210', 'standing_repo-20251210']; pending ['slr-20250627', 'slr-20251125']; in force [('slr', 'exclusion_expiry', '2021-04-01'), ('debt_ceiling', 'increase', '2025-07-04'), ('balance_sheet', 'qt_end', '2025-12-01'), ('iorb_rate', 'set_rate', '2025-12-11'), ('reserve_management', 'bill_purchases', '2025-12-11'), ('standing_repo', 'change', '2025-12-11')]
* lead 5 (origin 2025-12-08): target-day calendar {'days_to_month_end': 16.0, 'quarter_end': 0.0, 'tax_date': 1.0}; origin-day calendar {'days_to_month_end': 23.0, 'quarter_end': 0.0, 'tax_date': 0.0}; settlement due on the target day (bills, coupons, SOMA; public then only at lead 1) {'treasury_settlement': None, 'treasury_settlement_bills': None, 'treasury_settlement_coupons': None, 'treasury_settlement_soma': None}; announced net settlement of the next 1 to 5 days [-30.976, -30.976, -37.97399999999999, -37.97399999999999, 1.0280000000000058]; FOMC statement days []; register entries announced in the 10 days before []; pending ['slr-20250627', 'slr-20251125']; in force [('reserve_management', 'bill_purchases_and_repo', '2019-10-15'), ('slr', 'exclusion_expiry', '2021-04-01'), ('debt_ceiling', 'increase', '2025-07-04'), ('balance_sheet', 'qt_end', '2025-12-01'), ('iorb_rate', 'set_rate', '2025-10-30'), ('standing_repo', 'change', '2025-10-30')]

### 2025-12-26

* lead 1 (origin 2025-12-24): target-day calendar {'days_to_month_end': 5.0, 'quarter_end': 0.0, 'tax_date': 0.0}; origin-day calendar {'days_to_month_end': 7.0, 'quarter_end': 0.0, 'tax_date': 0.0}; settlement due on the target day (bills, coupons, SOMA; public then only at lead 1) {'treasury_settlement': 316.0, 'treasury_settlement_bills': 288.0, 'treasury_settlement_coupons': 28.0, 'treasury_settlement_soma': 13.2394617}; announced net settlement of the next 1 to 5 days [23.01600000000002, 23.01600000000002, -7.964999999999975, -51.34499999999997, -61.339999999999975]; FOMC statement days []; register entries announced in the 10 days before []; pending ['slr-20250627', 'slr-20251125']; in force [('slr', 'exclusion_expiry', '2021-04-01'), ('debt_ceiling', 'increase', '2025-07-04'), ('balance_sheet', 'qt_end', '2025-12-01'), ('iorb_rate', 'set_rate', '2025-12-11'), ('reserve_management', 'bill_purchases', '2025-12-11'), ('standing_repo', 'change', '2025-12-11')]
* lead 5 (origin 2025-12-18): target-day calendar {'days_to_month_end': 5.0, 'quarter_end': 0.0, 'tax_date': 0.0}; origin-day calendar {'days_to_month_end': 13.0, 'quarter_end': 0.0, 'tax_date': 0.0}; settlement due on the target day (bills, coupons, SOMA; public then only at lead 1) {'treasury_settlement': None, 'treasury_settlement_bills': None, 'treasury_settlement_coupons': None, 'treasury_settlement_soma': None}; announced net settlement of the next 1 to 5 days [0.0, 0.0, -40.99400000000003, -40.99400000000003, -17.97800000000001]; FOMC statement days []; register entries announced in the 10 days before ['iorb-20251210', 'on_rrp-20251210', 'reserve_management-20251210', 'standing_repo-20251210']; pending ['slr-20250627', 'slr-20251125']; in force [('slr', 'exclusion_expiry', '2021-04-01'), ('debt_ceiling', 'increase', '2025-07-04'), ('balance_sheet', 'qt_end', '2025-12-01'), ('iorb_rate', 'set_rate', '2025-12-11'), ('reserve_management', 'bill_purchases', '2025-12-11'), ('standing_repo', 'change', '2025-12-11')]

