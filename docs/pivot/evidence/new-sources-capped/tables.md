Ordinary days: 1469 of 1873 scored days, 82 above +5 bp, 6 onsets (2019-05-28, 2019-06-25, 2019-08-13, 2020-03-04, 2020-03-12, 2024-12-26), 24 pre-onset days against 1445 other ordinary days.

Table 1. The new series on ordinary days. AUROC of the +5 bp indicator against the other ordinary days (0.5 is no information), 90 % interval, lead 1 and lead 5; Spearman with the indicator and the spread change at lead 1; the pre-onset AUC (1 to 5 days before the six onsets on ordinary days) with interval; the partial rank correlation with the indicator after the scarcity state and the tail spread; the closest earlier series and its pooled Spearman; the cluster.

| series | AUROC l1 | 90 % | AUROC l5 | 90 % | rho ind. l1 | rho chg l1 | pre-onset AUC | 90 % | partial rho (raw) | closest held series | cluster (size) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `auc_accepted_bn` | 0.402 | [0.34, 0.46] | 0.391 | [0.33, 0.45] | -0.075 | +0.037 | 0.353 | [0.24, 0.46] | +0.000 [-0.05, 0.04] (-0.075) | `bank_total_assets` +0.41 | `auc_accepted_bn` (1) |
| `auc_cover` | 0.423 | [0.37, 0.49] | 0.360 | [0.30, 0.42] | -0.059 | -0.011 | 0.394 | [0.29, 0.51] | -0.072 [-0.12, -0.03] (-0.059) | `net_settlement_due_5d` -0.22 | `auc_cover` (1) |
| `auc_dealer_share` | 0.580 | [0.51, 0.66] | 0.517 | [0.45, 0.59] | +0.061 | -0.084 | 0.649 | [0.49, 0.79] | -0.071 [-0.13, -0.00] (+0.061) | `bank_total_assets` -0.53 | `auc_dealer_share` (1) |
| `auc_indirect_share` | 0.453 | [0.40, 0.52] | 0.491 | [0.43, 0.56] | -0.037 | +0.086 | 0.306 | [0.17, 0.44] | +0.078 [0.03, 0.13] (-0.037) | `bank_total_assets` +0.60 | `auc_indirect_share` (1) |
| `dts_debt_issues_bn` | 0.418 | [0.36, 0.47] | 0.373 | [0.32, 0.43] | -0.065 | +0.013 | 0.427 | [0.32, 0.53] | -0.002 [-0.05, 0.04] (-0.065) | `bank_total_assets` +0.32 | `dts_debt_issues_bn` (1) |
| `dts_debt_net_bn` | 0.468 | [0.42, 0.51] | 0.486 | [0.43, 0.53] | -0.025 | -0.058 | 0.456 | [0.36, 0.54] | -0.049 [-0.09, -0.01] (-0.025) | `tga_daily_change` +0.53 | `dts_debt_net_bn` (1) |
| `pd_fails_deliver_ust` | 0.527 | [0.46, 0.58] | 0.556 | [0.50, 0.62] | +0.021 | +0.015 | 0.364 | [0.26, 0.47] | +0.064 [0.01, 0.11] (+0.021) | `ofr_dvp_minus_bgcr_bp` -0.34 | `pd_fails_deliver_ust` (2) |
| `pd_fails_receive_ust` | 0.493 | [0.45, 0.55] | 0.507 | [0.45, 0.56] | -0.005 | +0.024 | 0.376 | [0.26, 0.50] | +0.053 [0.01, 0.09] (-0.005) | `on_rrp_sameday` +0.41 | `pd_fails_deliver_ust` (2) |
| `pd_repo_mbs` | 0.519 | [0.47, 0.56] | 0.521 | [0.48, 0.57] | +0.015 | -0.016 | 0.519 | [0.47, 0.57] | +0.022 [-0.01, 0.06] (+0.015) | `dealer_treasury_position` +0.86 | `bgcr_volume` (3) |
| `pd_repo_ust` | 0.451 | [0.40, 0.50] | 0.478 | [0.43, 0.53] | -0.039 | -0.016 | 0.498 | [0.44, 0.55] | +0.076 [0.03, 0.12] (-0.039) | `sofr_volume` +0.87 | `pd_repo_ust` (1) |
| `pd_reverse_repo_ust` | 0.418 | [0.37, 0.46] | 0.415 | [0.36, 0.47] | -0.065 | +0.006 | 0.419 | [0.34, 0.50] | +0.087 [0.05, 0.12] (-0.065) | `sofr_volume` +0.87 | `bank_total_assets` (3) |
| `rrp_counterparties` | 0.220 | [0.19, 0.25] | 0.230 | [0.21, 0.26] | -0.221 | +0.054 | 0.261 | [0.21, 0.31] | +0.066 [0.03, 0.10] (-0.221) | `on_rrp` +0.95 | `on_rrp` (6) |

Table 2. The 25 series with the largest distance of the ordinary-day AUROC from 0.5 (the larger of lead 1 and lead 5), new and held together. A series is a lead only if its interval excludes 0.5; the rank is by distance and is not a significance ranking.

| rank | series | new | lead | AUROC | 90 % | rho ind. | pre-onset AUC | 90 % | partial rho | cluster representative (size) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `sofr_p75_iorb_bps` | no | 1 | 0.944 | [0.92, 0.96] | +0.353 | 0.794 | [0.74, 0.84] | +0.112 | `sofr_p75_iorb_bps` (1) |
| 2 | `sofr_p99_iorb_bps` | no | 1 | 0.938 | [0.92, 0.95] | +0.349 | 0.814 | [0.74, 0.87] | - | `sofr_p99_iorb_bps` (1) |
| 3 | `spread_nowcast_bps` | no | 1 | 0.907 | [0.89, 0.92] | +0.323 | 0.792 | [0.74, 0.84] | +0.070 | `on_rrp` (6) |
| 4 | `reserve_balances` | no | 1 | 0.104 | [0.08, 0.13] | -0.315 | 0.162 | [0.10, 0.23] | -0.073 | `reserve_balances` (1) |
| 5 | `ofr_dvp_minus_bgcr_bp` | no | 5 | 0.894 | [0.85, 0.93] | +0.180 | 0.661 | [0.51, 0.79] | +0.073 | `dealer_treasury_position` (3) |
| 6 | `ofr_dvp_minus_bgcr_bp_backfill` | no | 5 | 0.894 | [0.84, 0.93] | +0.180 | 0.661 | [0.51, 0.81] | +0.073 | `dealer_treasury_position` (3) |
| 7 | `sofr_above_effr_share_20` | no | 1 | 0.877 | [0.85, 0.90] | +0.308 | 0.786 | [0.74, 0.83] | +0.108 | `sofr_above_effr_share_20` (1) |
| 8 | `sofr_p99_iorb_sd15_bps` | no | 1 | 0.875 | [0.85, 0.90] | +0.298 | 0.692 | [0.63, 0.75] | +0.164 | `sofr_p99_iorb_sd15_bps` (1) |
| 9 | `reserve_scarcity_state` | no | 1 | 0.862 | [0.84, 0.88] | +0.321 | 0.779 | [0.70, 0.85] | - | `None` (None) |
| 10 | `policy_reserve_management_in_force` | no | 5 | 0.212 | [0.17, 0.25] | -0.347 | 0.313 | [0.23, 0.40] | -0.146 | `policy_reserve_management_in_force` (1) |
| 11 | `ofr_gcf_rate` | no | 5 | 0.212 | [0.15, 0.27] | -0.305 | - | - | +0.034 | `bgcr` (13) |
| 12 | `on_rrp_below_100bn` | no | 5 | 0.786 | [0.77, 0.80] | +0.265 | 0.723 | [0.67, 0.78] | -0.073 | `on_rrp` (6) |
| 13 | `rrp_counterparties` | yes | 1 | 0.220 | [0.19, 0.25] | -0.221 | 0.261 | [0.21, 0.31] | +0.066 | `on_rrp` (6) |
| 14 | `on_rrp_sameday` | no | 5 | 0.236 | [0.21, 0.26] | -0.209 | 0.301 | [0.26, 0.33] | +0.102 | `on_rrp` (6) |
| 15 | `srf_take_up` | no | 5 | 0.759 | [0.63, 0.86] | +0.145 | 0.536 | [0.34, 0.73] | +0.053 | `fed_repo_accepted` (6) |
| 16 | `on_rrp` | no | 1 | 0.249 | [0.23, 0.27] | -0.200 | 0.297 | [0.26, 0.33] | +0.104 | `on_rrp` (6) |
| 17 | `dvp_volume_share` | no | 5 | 0.259 | [0.22, 0.30] | -0.192 | 0.414 | [0.31, 0.52] | -0.067 | `dvp_volume_share` (1) |
| 18 | `tga` | no | 5 | 0.271 | [0.22, 0.33] | -0.182 | 0.285 | [0.21, 0.37] | -0.150 | `tga` (2) |
| 19 | `effr_iorb_change_20_bps` | no | 1 | 0.713 | [0.65, 0.77] | +0.195 | 0.374 | [0.27, 0.50] | +0.140 | `effr_iorb_change_20_bps` (1) |
| 20 | `tga_daily` | no | 5 | 0.291 | [0.23, 0.34] | -0.167 | 0.264 | [0.19, 0.35] | -0.142 | `tga` (2) |
| 21 | `bank_total_assets` | no | 1 | 0.292 | [0.23, 0.36] | -0.166 | 0.276 | [0.19, 0.38] | +0.066 | `bank_total_assets` (3) |
| 22 | `policy_standing_repo_in_force` | no | 1 | 0.298 | [0.26, 0.34] | -0.189 | 0.285 | [0.22, 0.35] | +0.119 | `bank_total_assets` (3) |
| 23 | `sofr_tgcr_bps` | no | 1 | 0.688 | [0.64, 0.73] | +0.150 | 0.590 | [0.52, 0.65] | +0.016 | `sofr_tgcr_bps` (1) |
| 24 | `fed_repo_days_since_positive` | no | 5 | 0.673 | [0.61, 0.73] | +0.140 | 0.588 | [0.45, 0.70] | +0.021 | `fed_repo_accepted` (6) |
| 25 | `policy_debt_limit_reinstated` | no | 5 | 0.664 | [0.62, 0.71] | +0.209 | 0.591 | [0.51, 0.68] | +0.206 | `policy_debt_limit_reinstated` (1) |

Table 4. The series ranked by the rank correlation with the +5 bp indicator on ordinary days after the scarcity state and the tail spread are taken out (lead 1; interval only for the new series and the 12 held series with the largest value). This is the incremental check: a series that ranks high in Table 2 and low here tells the same story as the scarcity state or the tail spread.

| rank | series | new | partial rho | 90 % | raw rho | AUROC l1 | 90 % | pre-onset AUC | 90 % |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `policy_debt_limit_reinstated` | no | +0.206 | [0.14, 0.26] | +0.209 | 0.664 | [0.62, 0.71] | 0.591 | [0.51, 0.68] |
| 2 | `policy_slr_exclusion_in_force` | no | -0.176 | [-0.20, -0.15] | -0.095 | 0.430 | [0.42, 0.44] | 0.433 | [0.43, 0.44] |
| 3 | `sofr_p99_iorb_sd15_bps` | no | +0.164 | [0.13, 0.19] | +0.298 | 0.875 | [0.85, 0.90] | 0.692 | [0.63, 0.75] |
| 4 | `tga` | no | -0.150 | [-0.19, -0.11] | -0.176 | 0.279 | [0.23, 0.33] | 0.285 | [0.21, 0.37] |
| 5 | `policy_reserve_management_in_force` | no | -0.146 | [-0.22, -0.08] | -0.319 | 0.237 | [0.19, 0.29] | 0.313 | [0.23, 0.40] |
| 6 | `tga_daily` | no | -0.142 | [-0.18, -0.10] | -0.165 | 0.293 | [0.24, 0.35] | 0.264 | [0.19, 0.35] |
| 7 | `effr_iorb_change_20_bps` | no | +0.140 | [0.08, 0.20] | +0.195 | 0.713 | [0.65, 0.77] | 0.374 | [0.27, 0.50] |
| 8 | `sofr_volume` | no | +0.135 | [0.10, 0.18] | +0.057 | 0.572 | [0.52, 0.62] | 0.596 | [0.55, 0.64] |
| 9 | `bgcr_volume` | no | +0.128 | [0.10, 0.16] | +0.104 | 0.630 | [0.59, 0.67] | 0.620 | [0.58, 0.66] |
| 10 | `effr` | no | +0.126 | [0.11, 0.14] | +0.011 | 0.513 | [0.49, 0.54] | 0.467 | [0.42, 0.51] |
| 11 | `policy_qt_in_force` | no | +0.125 | [0.08, 0.16] | +0.059 | 0.563 | [0.52, 0.61] | 0.442 | [0.36, 0.51] |
| 12 | `tgcr` | no | +0.120 | [0.10, 0.14] | +0.017 | 0.522 | [0.50, 0.55] | 0.466 | [0.43, 0.51] |
| 13 | `bgcr` | no | +0.120 | - | +0.017 | 0.522 | [0.50, 0.55] | 0.467 | [0.42, 0.52] |
| 14 | `policy_standing_repo_in_force` | no | +0.119 | - | -0.189 | 0.298 | [0.26, 0.34] | 0.285 | [0.22, 0.35] |
| 15 | `sofr_p99` | no | +0.119 | - | +0.030 | 0.537 | [0.51, 0.57] | 0.468 | [0.42, 0.52] |
| 16 | `sofr_p25` | no | +0.116 | - | +0.017 | 0.521 | [0.50, 0.55] | 0.466 | [0.43, 0.51] |
| 17 | `sofr_p75` | no | +0.115 | - | +0.020 | 0.526 | [0.50, 0.55] | 0.466 | [0.43, 0.52] |
| 18 | `policy_days_since_known` | no | -0.112 | - | -0.118 | 0.352 | [0.31, 0.41] | 0.210 | [0.14, 0.27] |
| 19 | `sofr_p75_iorb_bps` | no | +0.112 | - | +0.353 | 0.944 | [0.92, 0.96] | 0.794 | [0.74, 0.84] |
| 20 | `sofr_p1` | no | +0.110 | - | +0.016 | 0.520 | [0.50, 0.55] | 0.470 | [0.42, 0.51] |
| 21 | `sofr_above_effr_share_20` | no | +0.108 | - | +0.308 | 0.877 | [0.85, 0.90] | 0.786 | [0.74, 0.83] |
| 22 | `policy_days_until_effective` | no | -0.107 | - | -0.121 | 0.402 | [0.36, 0.45] | 0.491 | [0.42, 0.55] |
| 23 | `on_rrp` | no | +0.104 | - | -0.200 | 0.249 | [0.23, 0.27] | 0.297 | [0.26, 0.33] |
| 24 | `on_rrp_sameday` | no | +0.102 | - | -0.198 | 0.249 | [0.22, 0.27] | 0.301 | [0.26, 0.33] |
| 25 | `tbill_4w` | no | +0.102 | - | -0.005 | 0.494 | [0.47, 0.52] | 0.457 | [0.41, 0.51] |

Series whose ordinary-day AUROC interval excludes 0.5 at lead 1 or 5: 53 of 87; of the new series: `rrp_counterparties`, `auc_cover`, `dts_debt_issues_bn`, `auc_accepted_bn`, `pd_reverse_repo_ust`, `auc_dealer_share`, `pd_fails_deliver_ust`.

Table 3. Redundant groups (pooled lead-1 Spearman, |rho| >= 0.8, each member within the threshold of the representative) that hold a new series.

| representative | members |
|---|---|
| `on_rrp` | `on_rrp`, `on_rrp_below_100bn`, `on_rrp_sameday`, `rrp_counterparties`, `spread_bps`, `spread_nowcast_bps` |
| `bank_total_assets` | `bank_total_assets`, `pd_reverse_repo_ust`, `policy_standing_repo_in_force` |
| `bgcr_volume` | `bgcr_volume`, `pd_repo_mbs`, `sofr_volume` |
| `pd_fails_deliver_ust` | `pd_fails_deliver_ust`, `pd_fails_receive_ust` |
| `auc_accepted_bn` | `auc_accepted_bn` |
| `auc_cover` | `auc_cover` |
| `auc_dealer_share` | `auc_dealer_share` |
| `auc_indirect_share` | `auc_indirect_share` |
| `dts_debt_issues_bn` | `dts_debt_issues_bn` |
| `dts_debt_net_bn` | `dts_debt_net_bn` |
| `pd_repo_ust` | `pd_repo_ust` |

Tests run (none corrected for multiplicity): auroc 994, inter source 11075, partial 170, pre onset 257, spearman 4016; 16512 in all.
