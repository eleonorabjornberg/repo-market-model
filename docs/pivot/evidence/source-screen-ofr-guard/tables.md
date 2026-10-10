## Ranking by correlation with the pressure indicator

Scored days 2018-06-29 to 2025-12-31 (1873 days, 140 above +5 bp, 27 onsets). Spearman correlation of the series, read as of the decision instant, with the +5 bp pressure indicator of the scored day. The rank is by the largest absolute value over leads 1, 2, 3, 5, 10. `Read as` is how the as-of rule reads it: `observed` at the latest row public at the decision instant, `scheduled` (known in advance for the scored day itself, and public at a lead of 1 only) or `calendar` (known in advance). The last column lists the tier-1 passers that name the series as an input.

| rank | series | lead 1 | lead 2 | lead 3 | lead 5 | lead 10 | strongest | days at lead 1 | read as | used by tier-1 passers |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `sofr_p75_iorb_bps` | +0.395 | +0.385 | +0.379 | +0.374 | +0.381 | +0.395 at 1 | 1871 | observed | `risk_gbm`, `risk_logistic` |
| 2 | `spread_bps` | +0.393 | +0.379 | +0.370 | +0.368 | +0.380 | +0.393 at 1 | 1873 | observed | `risk_gbm`, `risk_gbm_base`, `risk_logistic`, `risk_logistic_base`, `risk_quantile_skewt_base` |
| 3 | `sofr_p99_iorb_bps` | +0.392 | +0.371 | +0.367 | +0.360 | +0.370 | +0.392 at 1 | 1873 | observed | `risk_gbm`, `risk_logistic` |
| 4 | `policy_reserve_management_in_force` | -0.359 | -0.364 | -0.368 | -0.377 | -0.389 | -0.389 at 10 | 1873 | observed | no |
| 5 | `ofr_gcf_rate` | -0.291 | -0.315 | -0.326 | -0.386 | -0.305 | -0.386 at 5 | 144 | observed | no |
| 6 | `reserve_scarcity_state` | +0.365 | +0.365 | +0.365 | +0.364 | +0.363 | +0.365 at 1 | 1873 | observed | `risk_gbm`, `risk_gbm_base`, `risk_logistic`, `risk_logistic_base`, `risk_quantile_skewt_base` |
| 7 | `sofr_above_effr_share_20` | +0.355 | +0.351 | +0.348 | +0.340 | +0.320 | +0.355 at 1 | 1873 | observed | no |
| 8 | `spread_nowcast_bps` | +0.351 | +0.340 | +0.319 | +0.320 | +0.341 | +0.351 at 1 | 1873 | observed | no |
| 9 | `reserve_balances` | -0.348 | -0.347 | -0.347 | -0.345 | -0.340 | -0.348 at 1 | 1873 | observed | `risk_gbm`, `risk_gbm_base`, `risk_logistic`, `risk_logistic_base`, `risk_quantile_skewt_base` |
| 10 | `sofr_p99_iorb_sd15_bps` | +0.316 | +0.301 | +0.296 | +0.311 | +0.283 | +0.316 at 1 | 1873 | observed | no |
| 11 | `on_rrp_below_100bn` | +0.301 | +0.305 | +0.305 | +0.305 | +0.301 | +0.305 at 2 | 1873 | observed | no |
| 12 | `on_rrp` | -0.233 | -0.241 | -0.247 | -0.227 | -0.231 | -0.247 at 3 | 1873 | observed | `risk_gbm`, `risk_logistic` |
| 13 | `on_rrp_sameday` | -0.233 | -0.231 | -0.242 | -0.237 | -0.234 | -0.242 at 3 | 1863 | observed | no |
| 14 | `srf_take_up` | +0.182 | +0.209 | +0.195 | +0.138 | +0.223 | +0.223 at 10 | 1102 | observed | no |
| 15 | `dvp_volume_share` | -0.205 | -0.215 | -0.221 | -0.222 | -0.210 | -0.222 at 5 | 1873 | observed | no |
| 16 | `ofr_dvp_minus_bgcr_bp` | +0.185 | +0.185 | +0.187 | +0.216 | +0.181 | +0.216 at 5 | 1246 | observed | no |
| 17 | `ofr_dvp_minus_bgcr_bp_backfill` | +0.185 | +0.185 | +0.187 | +0.216 | +0.181 | +0.216 at 5 | 1246 | observed | no |
| 18 | `policy_standing_repo_in_force` | -0.200 | -0.200 | -0.199 | -0.199 | -0.197 | -0.200 at 1 | 1873 | observed | no |
| 19 | `effr_iorb_change_20_bps` | +0.197 | +0.177 | +0.169 | +0.165 | +0.118 | +0.197 at 1 | 1873 | observed | no |
| 20 | `tga` | -0.181 | -0.183 | -0.183 | -0.185 | -0.192 | -0.192 at 10 | 1873 | observed | `risk_gbm`, `risk_gbm_base`, `risk_logistic`, `risk_logistic_base`, `risk_quantile_skewt_base` |
| 21 | `policy_debt_limit_reinstated` | +0.185 | +0.185 | +0.185 | +0.185 | +0.190 | +0.190 at 10 | 1873 | observed | no |
| 22 | `tga_daily` | -0.173 | -0.172 | -0.170 | -0.170 | -0.189 | -0.189 at 10 | 1873 | observed | `risk_gbm`, `risk_logistic` |
| 23 | `bank_total_assets` | -0.168 | -0.168 | -0.168 | -0.170 | -0.171 | -0.171 at 10 | 1873 | observed | no |
| 24 | `treasury_settlement_coupons` | +0.170 | - | - | - | - | +0.170 at 1 | 1873 | scheduled | `risk_gbm`, `risk_gbm_base`, `risk_logistic`, `risk_logistic_base`, `risk_quantile_skewt_base` |
| 25 | `policy_days_until_effective` | -0.161 | -0.149 | -0.138 | -0.131 | -0.111 | -0.161 at 1 | 1873 | observed | no |
| 26 | `sofr_tgcr_bps` | +0.156 | +0.132 | +0.132 | +0.145 | +0.158 | +0.158 at 10 | 1873 | observed | no |
| 27 | `policy_days_since_known` | -0.130 | -0.119 | -0.112 | -0.114 | -0.077 | -0.130 at 1 | 1873 | observed | no |
| 28 | `bgcr_volume` | +0.120 | +0.118 | +0.120 | +0.121 | +0.125 | +0.125 at 10 | 1873 | observed | no |
| 29 | `dealer_treasury_position` | +0.110 | +0.111 | +0.113 | +0.117 | +0.104 | +0.117 at 5 | 1873 | observed | no |
| 30 | `policy_slr_exclusion_in_force` | -0.111 | -0.111 | -0.111 | -0.111 | -0.111 | -0.111 at 1 | 1873 | observed | no |
| 31 | `iorb_announced_change_bps` | -0.108 | - | - | - | - | -0.108 at 1 | 1873 | scheduled | no |
| 32 | `policy_iorb_offset_bp` | -0.107 | -0.102 | -0.099 | -0.089 | -0.068 | -0.107 at 1 | 1873 | observed | no |
| 33 | `quarter_end` | +0.106 | +0.106 | +0.106 | +0.106 | +0.106 | +0.106 at 1 | 1873 | calendar | `risk_gbm`, `risk_gbm_base`, `risk_logistic`, `risk_logistic_base`, `risk_quantile_skewt_base` |
| 34 | `dvp_volume_share_chg20` | +0.062 | +0.061 | +0.070 | +0.075 | +0.106 | +0.106 at 10 | 1873 | observed | no |
| 35 | `fed_repo_days_since_positive` | +0.065 | +0.068 | +0.071 | +0.084 | +0.089 | +0.089 at 10 | 1873 | observed | no |
| 36 | `policy_pending_count` | +0.086 | +0.082 | +0.074 | +0.082 | +0.067 | +0.086 at 1 | 1873 | observed | no |
| 37 | `fed_repo_days_since_positive_sameday` | +0.049 | +0.065 | +0.067 | +0.074 | +0.076 | +0.076 at 10 | 1873 | observed | no |
| 38 | `net_settlement_due_5d` | +0.006 | +0.036 | +0.053 | +0.074 | -0.015 | +0.074 at 5 | 1873 | observed | no |
| 39 | `policy_qt_in_force` | +0.060 | +0.068 | +0.068 | +0.067 | +0.070 | +0.070 at 10 | 1873 | observed | no |
| 40 | `fed_repo_accepted_sameday` | +0.068 | +0.046 | +0.045 | +0.023 | +0.040 | +0.068 at 1 | 1873 | observed | no |
| 41 | `fed_repo_log_accepted_sameday` | +0.068 | +0.046 | +0.045 | +0.023 | +0.040 | +0.068 at 1 | 1873 | observed | no |
| 42 | `fed_repo_submitted_sameday` | +0.068 | +0.046 | +0.045 | +0.023 | +0.040 | +0.068 at 1 | 1873 | observed | no |
| 43 | `tga_change_5d` | +0.061 | +0.059 | +0.066 | +0.063 | +0.051 | +0.066 at 3 | 1873 | observed | no |
| 44 | `treasury_settlement` | +0.061 | - | - | - | - | +0.061 at 1 | 1873 | scheduled | `risk_gbm`, `risk_gbm_base`, `risk_logistic`, `risk_logistic_base`, `risk_quantile_skewt_base` |
| 45 | `tax_date` | +0.061 | +0.061 | +0.061 | +0.061 | +0.061 | +0.061 at 1 | 1873 | calendar | `risk_gbm`, `risk_gbm_base`, `risk_logistic`, `risk_logistic_base`, `risk_quantile_skewt_base` |
| 46 | `sofr_volume` | +0.060 | +0.054 | +0.049 | +0.046 | +0.049 | +0.060 at 1 | 1873 | observed | no |
| 47 | `tga_change_x_reserves` | +0.051 | +0.045 | +0.052 | +0.044 | +0.048 | +0.052 at 3 | 1873 | observed | no |
| 48 | `fed_repo_ops_sameday` | +0.047 | +0.033 | +0.029 | +0.012 | +0.024 | +0.047 at 1 | 1873 | observed | no |
| 49 | `treasury_settlement_soma` | -0.046 | - | - | - | - | -0.046 at 1 | 1873 | scheduled | no |
| 50 | `sofr_p99_p75_bps` | +0.046 | +0.007 | -0.003 | -0.015 | +0.018 | +0.046 at 1 | 1873 | observed | no |
| 51 | `fed_repo_accepted` | +0.045 | +0.044 | +0.037 | +0.008 | +0.016 | +0.045 at 1 | 1873 | observed | no |
| 52 | `fed_repo_log_accepted` | +0.045 | +0.044 | +0.037 | +0.008 | +0.016 | +0.045 at 1 | 1873 | observed | no |
| 53 | `fed_repo_submitted` | +0.045 | +0.044 | +0.037 | +0.008 | +0.016 | +0.045 at 1 | 1873 | observed | no |
| 54 | `srf_take_up_positive` | -0.023 | -0.007 | -0.007 | -0.036 | -0.000 | -0.036 at 5 | 1873 | observed | no |
| 55 | `fed_repo_log_accepted_change` | +0.035 | +0.008 | +0.004 | -0.032 | -0.020 | +0.035 at 1 | 1873 | observed | no |
| 56 | `fed_repo_log_accepted_change_sameday` | +0.023 | +0.035 | +0.008 | +0.028 | +0.024 | +0.035 at 2 | 1873 | observed | no |
| 57 | `net_settlement` | +0.027 | +0.034 | +0.019 | -0.014 | -0.007 | +0.034 at 2 | 1873 | observed | no |
| 58 | `fed_repo_ops` | +0.032 | +0.028 | +0.027 | -0.006 | +0.001 | +0.032 at 1 | 1873 | observed | no |
| 59 | `fed_repo_rate_iorb_bps_sameday` | -0.009 | +0.032 | +0.029 | +0.005 | +0.004 | +0.032 at 2 | 1873 | observed | no |
| 60 | `sofr_p99` | +0.031 | +0.023 | +0.022 | +0.023 | +0.029 | +0.031 at 1 | 1873 | observed | no |
| 61 | `fed_repo_rate_iorb_bps` | -0.009 | +0.031 | +0.028 | +0.004 | +0.004 | +0.031 at 2 | 1873 | observed | no |
| 62 | `net_settlement_bills` | -0.016 | -0.010 | -0.009 | -0.017 | -0.031 | -0.031 at 10 | 1873 | observed | no |
| 63 | `days_to_month_end` | -0.030 | -0.030 | -0.030 | -0.030 | -0.030 | -0.030 at 1 | 1873 | calendar | `risk_gbm`, `risk_gbm_base`, `risk_logistic`, `risk_logistic_base`, `risk_quantile_skewt_base` |
| 64 | `sofr_p75` | +0.024 | +0.022 | +0.019 | +0.022 | +0.029 | +0.029 at 10 | 1871 | observed | no |
| 65 | `tga_daily_change` | +0.018 | +0.009 | +0.016 | +0.018 | +0.029 | +0.029 at 10 | 1873 | observed | `risk_gbm`, `risk_logistic` |
| 66 | `sofr_p1` | +0.019 | +0.017 | +0.017 | +0.019 | +0.028 | +0.028 at 10 | 1873 | observed | no |
| 67 | `bgcr` | +0.021 | +0.019 | +0.018 | +0.021 | +0.027 | +0.027 at 10 | 1873 | observed | no |
| 68 | `tgcr` | +0.021 | +0.019 | +0.017 | +0.021 | +0.027 | +0.027 at 10 | 1873 | observed | no |
| 69 | `sofr_p25` | +0.021 | +0.019 | +0.017 | +0.020 | +0.027 | +0.027 at 10 | 1871 | observed | no |
| 70 | `bgcr_tgcr_bps` | -0.023 | +0.002 | +0.015 | -0.010 | -0.010 | -0.023 at 1 | 1873 | observed | no |
| 71 | `effr` | +0.014 | +0.014 | +0.015 | +0.017 | +0.022 | +0.022 at 10 | 1873 | observed | no |
| 72 | `tbill_13w` | -0.019 | -0.018 | -0.017 | -0.015 | -0.009 | -0.019 at 1 | 1873 | observed | no |
| 73 | `tbill_4w` | +0.003 | +0.003 | +0.003 | +0.006 | +0.012 | +0.012 at 10 | 1873 | observed | no |
| 74 | `ofr_dvp_rate` | -0.010 | -0.011 | -0.008 | -0.005 | +0.008 | -0.011 at 2 | 1246 | observed | no |
| 75 | `ofr_tri_rate` | -0.009 | -0.010 | -0.009 | -0.007 | +0.008 | -0.010 at 2 | 1321 | observed | no |
| 76 | `treasury_settlement_bills` | -0.007 | - | - | - | - | -0.007 at 1 | 1873 | scheduled | no |

No correlation could be formed (a constant series, or too few days or pressure days): `iorb_days_to_announced_change`.

## Pre-onset window

The series read at lead 1 on the 1 to 5 panel days before each of the 27 onsets (130 scored days) against every other scored day. The difference is in units of the other days' standard deviation; the AUC is the share of (pre-onset, other) pairs with the pre-onset value higher.

| series | mean before onsets | mean other days | difference (sd) | AUC |
|---|---|---|---|---|
| `reserve_scarcity_state` | 2.608 | 0.8526 | +1.47 | 0.83 |
| `reserve_balances` | 2019 | 3029 | -1.34 | 0.17 |
| `sofr_above_effr_share_20` | 0.6273 | 0.2511 | +1.27 | 0.82 |
| `policy_reserve_management_in_force` | 0.4231 | 0.8577 | -1.24 | 0.28 |
| `on_rrp_below_100bn` | 0.9308 | 0.4016 | +1.08 | 0.76 |
| `bank_total_assets` | 1.914e+04 | 2.152e+04 | -0.99 | 0.33 |
| `ofr_dvp_minus_bgcr_bp` | 3.353 | -0.3589 | +0.87 | 0.79 |
| `ofr_dvp_minus_bgcr_bp_backfill` | 3.353 | -0.3589 | +0.87 | 0.79 |
| `on_rrp` | 24.5 | 709.5 | -0.82 | 0.26 |
| `on_rrp_sameday` | 25.24 | 709.6 | -0.82 | 0.25 |
| `dvp_volume_share` | 0.565 | 0.5955 | -0.79 | 0.29 |
| `policy_standing_repo_in_force` | 0.2692 | 0.6127 | -0.70 | 0.33 |
| `sofr_p75_iorb_bps` | 7.031 | -0.7949 | +0.60 | 0.84 |
| `spread_bps` | 1.054 | -5.03 | +0.57 | 0.82 |
| `ofr_tri_rate` | 4.239 | 2.991 | +0.56 | 0.55 |
| `ofr_dvp_rate` | 4.234 | 2.988 | +0.56 | 0.54 |
| `tga_daily` | 441.3 | 670.8 | -0.56 | 0.33 |
| `tga` | 440.1 | 666.5 | -0.55 | 0.34 |
| `spread_nowcast_bps` | 0.5219 | -4.653 | +0.55 | 0.76 |
| `sofr_p99_iorb_sd15_bps` | 15.26 | 5.764 | +0.54 | 0.77 |
| `policy_days_since_known` | 29.77 | 44.87 | -0.48 | 0.36 |
| `dealer_treasury_position` | 270.9 | 230.4 | +0.48 | 0.64 |
| `fed_repo_submitted_sameday` | 15.98 | 5.799 | +0.46 | 0.54 |
| `fed_repo_submitted` | 15.59 | 5.827 | +0.44 | 0.55 |
| `fed_repo_accepted_sameday` | 14.52 | 5.55 | +0.44 | 0.54 |

The 25 largest by absolute difference; every series is in `screen.json`.

## By regime

The as-of reserve-scarcity state at the same lead (lead 1 shown for the day counts): ample (0 and 1) on 1359 days, scarce (2 and 3) on 514, no reading on 0. Spearman correlation with the pressure indicator, the 15 top-ranked series, at the lead of their strongest pooled correlation. A `-` has too few days or pressure days.

| series | lead | all | ample | scarce | unknown |
|---|---|---|---|---|---|
| `sofr_p75_iorb_bps` | 1 | +0.395 | +0.080 | +0.422 | - |
| `spread_bps` | 1 | +0.393 | +0.072 | +0.417 | - |
| `sofr_p99_iorb_bps` | 1 | +0.392 | +0.059 | +0.429 | - |
| `policy_reserve_management_in_force` | 10 | -0.389 | - | -0.112 | - |
| `ofr_gcf_rate` | 5 | -0.386 | - | +0.081 | - |
| `reserve_scarcity_state` | 1 | +0.365 | -0.011 | -0.103 | - |
| `sofr_above_effr_share_20` | 1 | +0.355 | +0.108 | +0.255 | - |
| `spread_nowcast_bps` | 1 | +0.351 | +0.058 | +0.302 | - |
| `reserve_balances` | 1 | -0.348 | -0.011 | -0.177 | - |
| `sofr_p99_iorb_sd15_bps` | 1 | +0.316 | +0.096 | +0.180 | - |
| `on_rrp_below_100bn` | 2 | +0.305 | +0.016 | +0.075 | - |
| `on_rrp` | 3 | -0.247 | -0.045 | -0.045 | - |
| `on_rrp_sameday` | 3 | -0.242 | -0.044 | -0.015 | - |
| `srf_take_up` | 10 | +0.223 | +0.106 | +0.045 | - |
| `dvp_volume_share` | 5 | -0.222 | +0.055 | +0.047 | - |

### Strongest within each regime

The 8 series with the largest absolute correlation inside the regime, over leads 1, 2, 3, 5, 10. A series that is constant inside a regime, or has too few days there, is not ranked.

| regime | rank | series | strongest | days | pressure days |
|---|---|---|---|---|---|
| ample | 1 | `quarter_end` | +0.235 at 10 | 1359 | 7 |
| ample | 2 | `treasury_settlement_coupons` | +0.109 at 1 | 1359 | 6 |
| ample | 3 | `sofr_above_effr_share_20` | +0.108 at 1 | 1359 | 6 |
| ample | 4 | `srf_take_up` | +0.106 at 10 | 1035 | 7 |
| ample | 5 | `srf_take_up_positive` | +0.101 at 10 | 1359 | 7 |
| ample | 6 | `sofr_p99_iorb_sd15_bps` | +0.098 at 2 | 1359 | 6 |
| ample | 7 | `fed_repo_accepted_sameday` | +0.098 at 10 | 1359 | 7 |
| ample | 8 | `fed_repo_log_accepted_sameday` | +0.098 at 10 | 1359 | 7 |
| scarce | 1 | `sofr_p99_iorb_bps` | +0.429 at 1 | 514 | 134 |
| scarce | 2 | `sofr_p75_iorb_bps` | +0.422 at 1 | 513 | 134 |
| scarce | 3 | `spread_bps` | +0.417 at 1 | 514 | 134 |
| scarce | 4 | `sofr_p99` | +0.368 at 10 | 514 | 133 |
| scarce | 5 | `sofr_p1` | +0.366 at 10 | 514 | 133 |
| scarce | 6 | `sofr_p75` | +0.366 at 10 | 513 | 132 |
| scarce | 7 | `bgcr` | +0.364 at 10 | 514 | 133 |
| scarce | 8 | `tgcr` | +0.363 at 10 | 514 | 133 |

## By year

Spearman correlation with the pressure indicator, the same series and leads. Years 2018, 2020 and 2024 are in bold; the first row is the number of pressure days in the year.

| series | lead | **2018** | 2019 | **2020** | 2021 | 2022 | 2023 | **2024** | 2025 |
|---|---|---|---|---|---|---|---|---|---|
| pressure days | | 13 | 89 | 4 | 0 | 0 | 0 | 5 | 29 |
| `sofr_p75_iorb_bps` | 1 | +0.216 | +0.384 | +0.186 | - | - | - | +0.116 | +0.457 |
| `spread_bps` | 1 | +0.236 | +0.364 | +0.153 | - | - | - | +0.103 | +0.469 |
| `sofr_p99_iorb_bps` | 1 | +0.276 | +0.417 | +0.201 | - | - | - | +0.135 | +0.450 |
| `policy_reserve_management_in_force` | 10 | - | -0.250 | - | - | - | - | - | - |
| `ofr_gcf_rate` | 5 | - | - | - | - | - | - | - | -0.511 |
| `reserve_scarcity_state` | 1 | -0.289 | - | +0.205 | - | - | - | - | +0.482 |
| `sofr_above_effr_share_20` | 1 | +0.208 | +0.043 | +0.095 | - | - | - | +0.182 | +0.462 |
| `spread_nowcast_bps` | 1 | +0.326 | +0.275 | +0.062 | - | - | - | +0.085 | +0.463 |
| `reserve_balances` | 1 | -0.279 | -0.233 | -0.148 | - | - | - | -0.083 | -0.441 |
| `sofr_p99_iorb_sd15_bps` | 1 | +0.239 | +0.134 | +0.143 | - | - | - | +0.184 | +0.232 |
| `on_rrp_below_100bn` | 2 | - | - | +0.023 | - | - | - | +0.444 | +0.362 |
| `on_rrp` | 3 | -0.081 | -0.047 | +0.075 | - | - | - | -0.141 | -0.467 |
| `on_rrp_sameday` | 3 | -0.114 | -0.031 | +0.140 | - | - | - | -0.129 | -0.455 |
| `srf_take_up` | 10 | - | - | - | - | - | - | +0.153 | +0.287 |
| `dvp_volume_share` | 5 | +0.218 | -0.073 | +0.025 | - | - | - | +0.079 | +0.082 |

### Strongest within the called-out years

The same ranking inside 2018, 2020 and 2024, the years with the fewest pressure days to rest on. Read these as anecdotes: the days are in the first row of the table above.

| year | rank | series | strongest | days | pressure days |
|---|---|---|---|---|---|
| 2018 | 1 | `policy_days_until_effective` | -0.425 at 1 | 125 | 13 |
| 2018 | 2 | `bank_total_assets` | +0.423 at 2 | 125 | 13 |
| 2018 | 3 | `treasury_settlement_coupons` | +0.415 at 1 | 125 | 13 |
| 2018 | 4 | `dealer_treasury_position` | +0.388 at 3 | 125 | 13 |
| 2018 | 5 | `fed_repo_accepted_sameday` | +0.374 at 1 | 125 | 13 |
| 2018 | 6 | `fed_repo_log_accepted_sameday` | +0.374 at 1 | 125 | 13 |
| 2018 | 7 | `fed_repo_ops_sameday` | +0.374 at 1 | 125 | 13 |
| 2018 | 8 | `fed_repo_submitted_sameday` | +0.374 at 1 | 125 | 13 |
| 2020 | 1 | `iorb_announced_change_bps` | -0.356 at 1 | 251 | 4 |
| 2020 | 2 | `policy_days_until_effective` | -0.346 at 1 | 251 | 4 |
| 2020 | 3 | `policy_pending_count` | +0.346 at 1 | 251 | 4 |
| 2020 | 4 | `fed_repo_rate_iorb_bps` | -0.239 at 1 | 251 | 4 |
| 2020 | 5 | `fed_repo_rate_iorb_bps_sameday` | -0.239 at 1 | 251 | 4 |
| 2020 | 6 | `fed_repo_accepted_sameday` | +0.221 at 1 | 251 | 4 |
| 2020 | 7 | `fed_repo_log_accepted_sameday` | +0.221 at 1 | 251 | 4 |
| 2020 | 8 | `fed_repo_submitted_sameday` | +0.218 at 1 | 251 | 4 |
| 2024 | 1 | `on_rrp_below_100bn` | +0.444 at 2 | 250 | 5 |
| 2024 | 2 | `quarter_end` | +0.437 at 1 | 250 | 5 |
| 2024 | 3 | `effr` | -0.267 at 3 | 250 | 5 |
| 2024 | 4 | `policy_days_since_known` | -0.242 at 5 | 250 | 5 |
| 2024 | 5 | `bgcr_volume` | +0.218 at 10 | 250 | 5 |
| 2024 | 6 | `ofr_dvp_rate` | -0.217 at 3 | 231 | 5 |
| 2024 | 7 | `tbill_4w` | -0.215 at 3 | 250 | 5 |
| 2024 | 8 | `sofr_p1` | -0.214 at 3 | 250 | 5 |

## Against the spread: the level and the next-day change

The same series against the spread level and against the change in the spread over the scored day, pooled, by lead; the 15 series with the largest absolute correlation with the level at lead 1.

| series | target | lead 1 | lead 2 | lead 3 | lead 5 | lead 10 |
|---|---|---|---|---|---|---|
| `spread_bps` | level | +0.918 | +0.889 | +0.870 | +0.841 | +0.833 |
| `spread_bps` | change | -0.131 | -0.097 | -0.069 | -0.045 | -0.042 |
| `sofr_p75_iorb_bps` | level | +0.875 | +0.851 | +0.835 | +0.810 | +0.807 |
| `sofr_p75_iorb_bps` | change | -0.128 | -0.097 | -0.066 | -0.049 | -0.043 |
| `spread_nowcast_bps` | level | +0.858 | +0.845 | +0.832 | +0.818 | +0.824 |
| `spread_nowcast_bps` | change | -0.114 | -0.060 | -0.056 | -0.017 | -0.021 |
| `on_rrp_sameday` | level | -0.808 | -0.805 | -0.805 | -0.805 | -0.798 |
| `on_rrp_sameday` | change | +0.008 | +0.025 | +0.010 | +0.018 | +0.017 |
| `on_rrp` | level | -0.805 | -0.805 | -0.806 | -0.803 | -0.796 |
| `on_rrp` | change | +0.025 | +0.012 | +0.013 | +0.023 | +0.021 |
| `reserve_scarcity_state` | level | +0.793 | +0.791 | +0.788 | +0.783 | +0.768 |
| `reserve_scarcity_state` | change | -0.024 | -0.022 | -0.023 | -0.022 | -0.020 |
| `on_rrp_below_100bn` | level | +0.781 | +0.780 | +0.780 | +0.779 | +0.774 |
| `on_rrp_below_100bn` | change | -0.006 | -0.010 | -0.014 | -0.011 | -0.022 |
| `sofr_p99_iorb_bps` | level | +0.758 | +0.729 | +0.709 | +0.671 | +0.664 |
| `sofr_p99_iorb_bps` | change | -0.142 | -0.099 | -0.066 | -0.051 | -0.034 |
| `sofr_above_effr_share_20` | level | +0.741 | +0.737 | +0.734 | +0.729 | +0.720 |
| `sofr_above_effr_share_20` | change | -0.044 | -0.045 | -0.043 | -0.037 | -0.029 |
| `reserve_balances` | level | -0.659 | -0.655 | -0.653 | -0.649 | -0.655 |
| `reserve_balances` | change | +0.035 | +0.035 | +0.033 | +0.033 | +0.024 |
| `policy_standing_repo_in_force` | level | -0.623 | -0.622 | -0.620 | -0.618 | -0.613 |
| `policy_standing_repo_in_force` | change | +0.023 | +0.022 | +0.022 | +0.022 | +0.022 |
| `ofr_dvp_minus_bgcr_bp` | level | +0.597 | +0.584 | +0.580 | +0.570 | +0.582 |
| `ofr_dvp_minus_bgcr_bp` | change | -0.075 | -0.017 | +0.000 | +0.012 | -0.036 |
| `ofr_dvp_minus_bgcr_bp_backfill` | level | +0.597 | +0.584 | +0.580 | +0.570 | +0.582 |
| `ofr_dvp_minus_bgcr_bp_backfill` | change | -0.075 | -0.017 | +0.000 | +0.012 | -0.036 |
| `policy_reserve_management_in_force` | level | -0.524 | -0.526 | -0.528 | -0.531 | -0.538 |
| `policy_reserve_management_in_force` | change | +0.034 | +0.032 | +0.034 | +0.039 | +0.042 |
| `policy_pending_count` | level | +0.463 | +0.462 | +0.459 | +0.457 | +0.444 |
| `policy_pending_count` | change | +0.014 | +0.009 | +0.002 | +0.008 | -0.016 |
