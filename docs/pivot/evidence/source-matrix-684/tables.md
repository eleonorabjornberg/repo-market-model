Table 1. Groups of redundant series (every pair |rho| >= 0.8, complete linkage), ordinary days pooled, lead 1. A series with no partner is not listed.

| representative | members | series |
|---|---|---|
| `sofr_p25` | 12 | `sofr_p75`, `tgcr`, `bgcr`, `tbill_4w`, `tbill_13w`, `effr`, `sofr_p1`, `sofr_p99`, `ofr_tri_rate`, `ofr_gcf_rate`, `ofr_dvp_rate` |
| `treasury_settlement` | 5 | `treasury_settlement_bills`, `treasury_settlement_soma`, `treasury_settlement@per_release`, `treasury_settlement_bills@per_release` |
| `tga@per_release` | 4 | `tga`, `tga_daily`, `tga_level` |
| `ofr_dvp_minus_bgcr_bp` | 3 | `dealer_treasury_position`, `ofr_dvp_minus_bgcr_bp_backfill` |
| `reserve_balances@per_release` | 3 | `reserve_balances`, `reserve_level` |
| `reserve_scarcity_state` | 3 | `on_rrp_below_100bn`, `reserve_scarcity_state@per_release` |
| `spread_bps` | 3 | `sofr_p75_iorb_bps`, `spread_nowcast_bps` |
| `bank_total_assets` | 2 | `policy_standing_repo_in_force` |
| `net_settlement` | 2 | `net_settlement_bills` |
| `on_rrp` | 2 | `on_rrp_sameday` |
| `satiation_dist_roll` | 2 | `satiation_distance` |
| `sofr_p99_iorb_bps` | 2 | `tail_spread_level` |
| `sofr_p99_p75_bps` | 2 | `dispersion_p99_p75` |
| `sofr_volume` | 2 | `bgcr_volume` |
| `srf_take_up` | 2 | `srf_take_up_positive` |
| `tga_change_5d` | 2 | `tga_change_10` |
| `tga_change_5d@per_release` | 2 | `tga_change_5` |
| `tga_daily_change` | 2 | `tga_change_x_reserves@per_release` |

32 series have no partner at this threshold; with the representatives, 50 series carry what the 87 do.

Table 2. Ordinary days, pooled: the 25 series with the largest absolute Spearman correlation with the +5 bp indicator over leads 1 to 10. Group representative in the last column.

| series | lead 1 | lead 2 | lead 3 | lead 5 | lead 10 | AUROC at lead 1 [90%] | days at lead 1 | group |
|---|---|---|---|---|---|---|---|---|
| `policy_reserve_management_in_force` | -0.319 | -0.325 | -0.332 | -0.345 | -0.364 | 0.24 [0.15, 0.34] | 1602 | `policy_reserve_management_in_force` |
| `sofr_p75_iorb_bps` | +0.340 | +0.329 | +0.323 | +0.319 | +0.322 | 0.94 [0.91, 0.96] | 1600 | `spread_bps` |
| `spread_bps` | +0.339 | +0.327 | +0.319 | +0.316 | +0.320 | 0.94 [0.91, 0.96] | 1602 | `spread_bps` |
| `sofr_p99_iorb_bps` | +0.338 | +0.325 | +0.325 | +0.317 | +0.319 | 0.94 [0.91, 0.96] | 1602 | `sofr_p99_iorb_bps` |
| `tail_spread_level` | +0.338 | +0.325 | +0.325 | +0.317 | +0.319 | 0.94 [0.91, 0.96] | 1602 | `sofr_p99_iorb_bps` |
| `spread_nowcast_bps` | +0.314 | +0.300 | +0.288 | +0.286 | +0.289 | 0.91 [0.87, 0.93] | 1602 | `spread_bps` |
| `reserve_balances@per_release` | -0.310 | -0.308 | -0.304 | -0.303 | -0.298 | 0.10 [0.06, 0.15] | 1602 | `reserve_balances@per_release` |
| `reserve_level` | -0.310 | -0.308 | -0.304 | -0.303 | -0.299 | 0.10 [0.06, 0.15] | 1602 | `reserve_balances@per_release` |
| `reserve_balances` | -0.305 | -0.304 | -0.303 | -0.302 | -0.297 | 0.11 [0.06, 0.16] | 1602 | `reserve_balances@per_release` |
| `satiation_hinge_roll` | +0.292 | +0.287 | +0.292 | +0.273 | +0.244 | 0.81 [0.74, 0.86] | 1602 | `satiation_hinge_roll` |
| `reserve_scarcity_state` | +0.286 | +0.284 | +0.285 | +0.286 | +0.285 | 0.84 [0.79, 0.88] | 1602 | `reserve_scarcity_state` |
| `reserve_scarcity_state@per_release` | +0.286 | +0.284 | +0.285 | +0.286 | +0.285 | 0.84 [0.79, 0.88] | 1602 | `reserve_scarcity_state` |
| `sofr_p99_iorb_sd15_bps` | +0.286 | +0.270 | +0.260 | +0.256 | +0.233 | 0.87 [0.82, 0.91] | 1602 | `sofr_p99_iorb_sd15_bps` |
| `sofr_above_effr_share_20` | +0.285 | +0.280 | +0.275 | +0.266 | +0.244 | 0.86 [0.81, 0.91] | 1602 | `sofr_above_effr_share_20` |
| `satiation_dist_roll` | -0.266 | -0.264 | -0.261 | -0.254 | -0.242 | 0.16 [0.11, 0.21] | 1602 | `satiation_dist_roll` |
| `satiation_distance` | -0.264 | -0.261 | -0.257 | -0.253 | -0.243 | 0.16 [0.11, 0.21] | 1602 | `satiation_dist_roll` |
| `on_rrp_below_100bn` | +0.232 | +0.238 | +0.233 | +0.233 | +0.231 | 0.76 [0.71, 0.80] | 1602 | `reserve_scarcity_state` |
| `policy_debt_limit_reinstated` | +0.210 | +0.210 | +0.210 | +0.210 | +0.218 | 0.66 [0.54, 0.77] | 1602 | `policy_debt_limit_reinstated` |
| `dispersion_p99_p1` | +0.207 | +0.201 | +0.203 | +0.167 | +0.175 | 0.77 [0.70, 0.82] | 1602 | `dispersion_p99_p1` |
| `effr_iorb_change_20_bps` | +0.193 | +0.188 | +0.179 | +0.164 | +0.128 | 0.72 [0.58, 0.82] | 1602 | `effr_iorb_change_20_bps` |
| `policy_standing_repo_in_force` | -0.193 | -0.193 | -0.193 | -0.192 | -0.190 | 0.29 [0.21, 0.39] | 1602 | `bank_total_assets` |
| `dvp_volume_share` | -0.174 | -0.183 | -0.187 | -0.183 | -0.169 | 0.27 [0.19, 0.39] | 1602 | `dvp_volume_share` |
| `srf_take_up` | +0.118 | +0.131 | +0.186 | +0.141 | +0.183 | 0.72 [0.59, 0.81] | 998 | `srf_take_up` |
| `tga_level` | -0.168 | -0.169 | -0.173 | -0.175 | -0.185 | 0.28 [0.17, 0.43] | 1602 | `tga@per_release` |
| `tga` | -0.173 | -0.176 | -0.177 | -0.179 | -0.184 | 0.28 [0.17, 0.42] | 1602 | `tga@per_release` |

Table 3. Ordinary days, pooled: the 12 series with the largest absolute Spearman correlation with the spread level and with the spread change, best lead of 1, 2, 3, 5, 10.

| target | series | best lead | rho | days |
|---|---|---|---|---|
| level | `spread_bps` | 1 | +0.915 | 1602 |
| level | `sofr_p75_iorb_bps` | 1 | +0.874 | 1600 |
| level | `spread_nowcast_bps` | 1 | +0.859 | 1602 |
| level | `reserve_scarcity_state` | 1 | +0.792 | 1602 |
| level | `reserve_scarcity_state@per_release` | 1 | +0.792 | 1602 |
| level | `on_rrp_below_100bn` | 1 | +0.788 | 1602 |
| level | `on_rrp_sameday` | 1 | -0.785 | 1592 |
| level | `sofr_p99_iorb_bps` | 1 | +0.785 | 1602 |
| level | `tail_spread_level` | 1 | +0.785 | 1602 |
| level | `on_rrp` | 5 | -0.784 | 1602 |
| level | `sofr_above_effr_share_20` | 1 | +0.733 | 1602 |
| level | `reserve_balances@per_release` | 1 | -0.688 | 1602 |
| change | `tail_spread_change_5` | 1 | -0.248 | 1602 |
| change | `sofr_p99_iorb_bps` | 1 | -0.225 | 1602 |
| change | `tail_spread_level` | 1 | -0.225 | 1602 |
| change | `sofr_p75_iorb_bps` | 1 | -0.218 | 1600 |
| change | `spread_bps` | 1 | -0.213 | 1602 |
| change | `net_settlement_due_5d` | 1 | +0.187 | 1602 |
| change | `spread_nowcast_bps` | 1 | -0.186 | 1602 |
| change | `days_to_month_end` | 1 | -0.170 | 1602 |
| change | `dispersion_p99_p1` | 1 | -0.169 | 1602 |
| change | `treasury_settlement@per_release` | 2 | +0.166 | 1602 |
| change | `treasury_settlement_bills@per_release` | 2 | +0.166 | 1602 |
| change | `treasury_settlement` | 1 | +0.165 | 1602 |

Table 4. Ordinary days, lead 1: the 15 series whose AUROC for pressure days is furthest from 0.5, with the 90% interval, pooled and by split. A split with too few pressure days is empty.

| series | period:2018-2025 | period:2026 | pooled | regime:2018-19 | regime:2020 | regime:2021-23 | regime:2024 | regime:2025-26 | scarcity:ample | scarcity:scarce | scarcity:unknown |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `sofr_p75_iorb_bps` | 0.94 [0.92, 0.96] | - | 0.94 [0.91, 0.96] | 0.84 [0.78, 0.89] | 0.88 [0.77, 0.95] | - | - | 0.91 [0.85, 0.96] | - | 0.85 [0.79, 0.89] | - |
| `spread_bps` | 0.94 [0.91, 0.96] | - | 0.94 [0.91, 0.96] | 0.83 [0.77, 0.88] | 0.77 [0.54, 0.90] | - | - | 0.92 [0.87, 0.96] | - | 0.85 [0.80, 0.89] | - |
| `sofr_p99_iorb_bps` | 0.94 [0.91, 0.96] | - | 0.94 [0.91, 0.96] | 0.86 [0.80, 0.90] | 0.95 [0.89, 0.98] | - | - | 0.92 [0.86, 0.96] | - | 0.86 [0.80, 0.90] | - |
| `tail_spread_level` | 0.94 [0.91, 0.96] | - | 0.94 [0.91, 0.96] | 0.86 [0.80, 0.90] | 0.95 [0.89, 0.98] | - | - | 0.92 [0.86, 0.96] | - | 0.86 [0.80, 0.90] | - |
| `spread_nowcast_bps` | 0.91 [0.87, 0.93] | - | 0.91 [0.87, 0.93] | 0.81 [0.74, 0.87] | 0.59 [0.48, 0.77] | - | - | 0.91 [0.85, 0.97] | - | 0.80 [0.75, 0.86] | - |
| `reserve_balances@per_release` | 0.10 [0.05, 0.16] | - | 0.10 [0.06, 0.15] | 0.21 [0.14, 0.30] | 0.16 [0.04, 0.32] | - | - | 0.15 [0.06, 0.25] | - | 0.26 [0.15, 0.40] | - |
| `reserve_level` | 0.10 [0.05, 0.16] | - | 0.10 [0.06, 0.15] | 0.21 [0.14, 0.30] | 0.16 [0.04, 0.32] | - | - | 0.15 [0.06, 0.25] | - | 0.26 [0.15, 0.40] | - |
| `reserve_balances` | 0.10 [0.06, 0.16] | - | 0.11 [0.06, 0.16] | 0.23 [0.15, 0.33] | 0.16 [0.04, 0.31] | - | - | 0.18 [0.06, 0.30] | - | 0.27 [0.16, 0.41] | - |
| `sofr_p99_iorb_sd15_bps` | 0.87 [0.83, 0.91] | - | 0.87 [0.82, 0.91] | 0.71 [0.60, 0.80] | 0.80 [0.64, 0.91] | - | - | 0.78 [0.57, 0.88] | - | 0.73 [0.64, 0.80] | - |
| `sofr_above_effr_share_20` | 0.88 [0.82, 0.92] | - | 0.86 [0.81, 0.91] | 0.63 [0.51, 0.74] | 0.69 [0.50, 0.83] | - | - | 0.92 [0.84, 0.97] | - | 0.68 [0.59, 0.76] | - |
| `ofr_dvp_minus_bgcr_bp` | 0.87 [0.74, 0.92] | - | 0.85 [0.77, 0.91] | - | - | - | - | 0.71 [0.63, 0.84] | - | 0.65 [0.56, 0.81] | - |
| `ofr_dvp_minus_bgcr_bp_backfill` | 0.87 [0.74, 0.92] | - | 0.85 [0.77, 0.91] | - | - | - | - | 0.71 [0.63, 0.84] | - | 0.65 [0.56, 0.81] | - |
| `satiation_dist_roll` | 0.15 [0.10, 0.20] | - | 0.16 [0.11, 0.21] | 0.35 [0.26, 0.45] | 0.13 [0.01, 0.27] | - | - | 0.08 [0.04, 0.19] | - | 0.29 [0.22, 0.37] | - |
| `satiation_distance` | 0.15 [0.10, 0.20] | - | 0.16 [0.11, 0.21] | 0.36 [0.27, 0.46] | 0.16 [0.04, 0.30] | - | - | 0.08 [0.03, 0.16] | - | 0.30 [0.23, 0.38] | - |
| `reserve_scarcity_state` | 0.86 [0.82, 0.90] | - | 0.84 [0.79, 0.88] | 0.50 [0.50, 0.51] | 0.86 [0.74, 0.94] | - | - | 0.68 [0.55, 0.83] | - | 0.51 [0.44, 0.58] | - |

Pressure days and ordinary days per split, lead 1: period:2018-2025 82 of 1469; period:2026 2 of 133; pooled 84 of 1602; regime:2018-19 62 of 294; regime:2020 3 of 195; regime:2021-23 0 of 586; regime:2024 2 of 197; regime:2025-26 17 of 330; scarcity:ample 2 of 1065; scarcity:scarce 82 of 537; scarcity:unknown 0 of 0.

The `period:2026` column (#684) is the days of the opened near-blind tier, 2026-01-01 to 2026-09-03, which this screen now reads; `period:2018-2025` is the days the earlier page read. The 2026 column holds 2 pressure days on ordinary days, so its intervals are wide: read it as a check on what changed after reserve-management purchases began, not as evidence. These are development days: nothing here is a verdict and none of it is out-of-sample evidence for a registered candidate (scoring protocol v1, #640).

Table 5. Pre-onset contrast on ordinary days, lead 1: the 15 series whose pre-onset AUROC is furthest from 0.5. 6 of the 30 onsets fall on ordinary days; 24 pre-onset days (1 to 5 panel days before them).

| series | pre-onset days | AUROC [90%] | std. diff. [90%] |
|---|---|---|---|
| `reserve_balances` | 24 | 0.16 [0.05, 0.35] | -1.51 [-2.10, -0.74] |
| `reserve_balances@per_release` | 24 | 0.17 [0.05, 0.36] | -1.50 [-2.10, -0.73] |
| `reserve_level` | 24 | 0.17 [0.05, 0.36] | -1.50 [-2.10, -0.73] |
| `sofr_p99_iorb_bps` | 24 | 0.82 [0.68, 0.90] | +0.26 [0.08, 0.69] |
| `tail_spread_level` | 24 | 0.82 [0.68, 0.90] | +0.26 [0.08, 0.69] |
| `policy_days_since_known` | 24 | 0.19 [0.09, 0.33] | -1.00 [-1.31, -0.63] |
| `spread_nowcast_bps` | 24 | 0.79 [0.66, 0.88] | +0.59 [0.26, 1.05] |
| `sofr_p75_iorb_bps` | 24 | 0.78 [0.64, 0.88] | +0.50 [0.17, 1.02] |
| `policy_iorb_offset_bp` | 24 | 0.22 [0.12, 0.37] | -0.96 [-1.43, -0.43] |
| `sofr_above_effr_share_20` | 24 | 0.76 [0.64, 0.88] | +0.92 [0.33, 1.52] |
| `spread_bps` | 24 | 0.76 [0.59, 0.88] | +0.50 [0.14, 1.09] |
| `reserve_scarcity_state` | 24 | 0.76 [0.56, 0.88] | +1.09 [0.30, 1.61] |
| `reserve_scarcity_state@per_release` | 24 | 0.76 [0.56, 0.88] | +1.09 [0.30, 1.61] |
| `tga_daily` | 24 | 0.25 [0.09, 0.44] | -0.78 [-1.14, -0.32] |
| `tga@per_release` | 24 | 0.25 [0.10, 0.42] | -0.77 [-1.13, -0.34] |

Table 6. Incremental: Spearman with the +5 bp indicator on ordinary days, raw and after the as-of scarcity state and the tail spread are taken out, for the top series, by lead.

| series | lead 1 raw / partial | lead 2 raw / partial | lead 3 raw / partial | lead 5 raw / partial | lead 10 raw / partial |
|---|---|---|---|---|---|
| `policy_reserve_management_in_force` | -0.32 / -0.18 | -0.33 / -0.19 | -0.33 / -0.20 | -0.35 / -0.22 | -0.36 / -0.24 |
| `sofr_p75_iorb_bps` | +0.34 / +0.10 | +0.33 / +0.10 | +0.32 / +0.08 | +0.32 / +0.09 | +0.32 / +0.09 |
| `tail_spread_level` | +0.34 / - | +0.33 / - | +0.32 / - | +0.32 / - | +0.32 / - |
| `spread_nowcast_bps` | +0.31 / +0.08 | +0.30 / +0.06 | +0.29 / +0.04 | +0.29 / +0.04 | +0.29 / +0.05 |
| `reserve_balances@per_release` | -0.31 / -0.09 | -0.31 / -0.09 | -0.30 / -0.09 | -0.30 / -0.09 | -0.30 / -0.08 |
| `reserve_level` | -0.31 / -0.09 | -0.31 / -0.09 | -0.30 / -0.09 | -0.30 / -0.09 | -0.30 / -0.08 |
| `reserve_balances` | -0.30 / -0.08 | -0.30 / -0.09 | -0.30 / -0.09 | -0.30 / -0.09 | -0.30 / -0.08 |
| `satiation_hinge_roll` | +0.29 / +0.18 | +0.29 / +0.18 | +0.29 / +0.18 | +0.27 / +0.17 | +0.24 / +0.13 |
| `reserve_scarcity_state@per_release` | +0.29 / - | +0.28 / - | +0.28 / - | +0.29 / - | +0.28 / - |
| `sofr_p99_iorb_sd15_bps` | +0.29 / +0.15 | +0.27 / +0.14 | +0.26 / +0.12 | +0.26 / +0.12 | +0.23 / +0.10 |
| `sofr_above_effr_share_20` | +0.29 / +0.09 | +0.28 / +0.09 | +0.27 / +0.08 | +0.27 / +0.07 | +0.24 / +0.04 |
| `satiation_dist_roll` | -0.27 / -0.14 | -0.26 / -0.14 | -0.26 / -0.13 | -0.25 / -0.13 | -0.24 / -0.12 |
| `satiation_distance` | -0.26 / -0.14 | -0.26 / -0.14 | -0.26 / -0.13 | -0.25 / -0.13 | -0.24 / -0.12 |
| `on_rrp_below_100bn` | +0.23 / -0.08 | +0.24 / -0.05 | +0.23 / -0.06 | +0.23 / -0.06 | +0.23 / -0.07 |
| `policy_debt_limit_reinstated` | +0.21 / +0.21 | +0.21 / +0.21 | +0.21 / +0.21 | +0.21 / +0.21 | +0.22 / +0.22 |

Table 7. Ordinary days, lead 1: Spearman with the +5 bp indicator in each split, for the top series of Table 6. A split with under 30 days or 3 pressure days is empty. The first row gives the pressure days in the split.

| series | period:2018-2025 | period:2026 | pooled | regime:2018-19 | regime:2020 | regime:2021-23 | regime:2024 | regime:2025-26 | scarcity:ample | scarcity:scarce | scarcity:unknown |
|---|---|---|---|---|---|---|---|---|---|---|---|
| pressure days | 82 | 2 | 84 | 62 | 3 | 0 | 2 | 17 | 2 | 82 | 0 |
| `policy_reserve_management_in_force` | -0.32 | - | -0.32 | -0.03 | - | - | - | - | - | -0.17 | - |
| `sofr_p75_iorb_bps` | +0.35 | - | +0.34 | +0.48 | +0.16 | - | - | +0.32 | - | +0.43 | - |
| `tail_spread_level` | +0.35 | - | +0.34 | +0.50 | +0.19 | - | - | +0.32 | - | +0.44 | - |
| `spread_nowcast_bps` | +0.32 | - | +0.31 | +0.44 | +0.04 | - | - | +0.32 | - | +0.38 | - |
| `reserve_balances@per_release` | -0.32 | - | -0.31 | -0.41 | -0.14 | - | - | -0.27 | - | -0.30 | - |
| `reserve_level` | -0.32 | - | -0.31 | -0.41 | -0.14 | - | - | -0.27 | - | -0.30 | - |
| `reserve_balances` | -0.32 | - | -0.30 | -0.39 | -0.15 | - | - | -0.24 | - | -0.29 | - |
| `satiation_hinge_roll` | +0.31 | - | +0.29 | +0.20 | - | - | - | +0.34 | - | +0.26 | - |
| `reserve_scarcity_state@per_release` | +0.32 | - | +0.29 | +0.03 | +0.19 | - | - | +0.14 | - | +0.03 | - |
| `sofr_p99_iorb_sd15_bps` | +0.30 | - | +0.29 | +0.30 | +0.13 | - | - | +0.22 | - | +0.28 | - |
| `sofr_above_effr_share_20` | +0.31 | - | +0.29 | +0.19 | +0.08 | - | - | +0.32 | - | +0.22 | - |
| `satiation_dist_roll` | -0.28 | - | -0.27 | -0.21 | -0.16 | - | - | -0.32 | - | -0.26 | - |
| `satiation_distance` | -0.28 | - | -0.26 | -0.19 | -0.15 | - | - | -0.32 | - | -0.25 | - |
| `on_rrp_below_100bn` | +0.26 | - | +0.23 | - | +0.02 | - | - | +0.16 | - | +0.05 | - |
| `policy_debt_limit_reinstated` | +0.21 | - | +0.21 | +0.37 | - | - | - | -0.15 | - | +0.35 | - |

Table 8. Due diligence, one row per source group.

| source | publisher | start of history | frequency | publication instant used | vintages and revisions | gaps after the start | caveats |
|---|---|---|---|---|---|---|---|
| NY Fed SOFR, with percentiles and volume | Federal Reserve Bank of New York | 2018-04-03 to 2018-04-23, by column | business daily | `nyfed_sofr`: 15:00 ET, reference date + 1 day | first published about 08:00 ET on the next business day and may be revised about 14:30 ET that day; the registry dates a value at the finalized 15:00 ET. The snapshot is one retrieval, so a later revision is not tracked | 2 of 2104 rows (`sofr_p75_iorb_bps`) | panel history starts at the first publication, 2018-04-03; the back-filled 2014-18 history is not read while its posting instant is null (#572, guarded by PR #590; the posting dates are now #633) |
| NY Fed TGCR and BGCR, with percentiles and volume | Federal Reserve Bank of New York | 2018-04-03 | business daily | `nyfed_tgcr`: 15:00 ET, reference date + 1 day; `nyfed_bgcr`: 15:00 ET, reference date + 1 day | first published on the next business day; 15:00 ET is the conservative finalized instant the adapter uses for all the secured rates | none | same start and the same back-fill posting question as SOFR (#572) |
| NY Fed EFFR | Federal Reserve Bank of New York | 2018-04-03 to 2018-05-01, by column | business daily | `nyfed_effr`: 15:00 ET, reference date + 1 day | first published about 09:00 ET on the next business day; 15:00 ET is declared. Taken from the New York Fed as published, not from FRED's DFF copy | none | EFFR less IORB is a different market and target from SOFR less IORB (registry note on frb_ddp, #129) |
| FRED: reserve balances (WRESBAL) and Treasury General Account (WTREGEN), weekly | Federal Reserve Bank of St. Louis FRED | 2018-04-03 to 2018-04-10, by column | mixed daily and weekly | `fred_macro_latest_vintage`: snapshot retrieved at | FRED serves the latest revised vintage only; observations inherit the snapshot's retrieval instant, so a re-fetch does not reproduce an old snapshot's bytes. The published reading applies a declared weekly lag; the `@per_release` reading dates each Wednesday level at its H.4.1 release (#541) | none | the per-release calendar assumed a Thursday print for any week not in its exception list and ignored its declared coverage (#576, guarded by PR #590; coverage now runs through 2026-09-03, #625); ALFRED pulls exist at a few dates as revision studies, not as a daily series |
| H.8 total assets and the reserve-scarcity state | Board of Governors of the Federal Reserve System | 2018-04-03 | weekly | `frb_h8`: 16:15 ET, reference date + 12 days | the H.8 is revised after its first print; the first print of a week is used, released the second Friday after the week ends at 16:15 ET | none | the scarcity state is reserves over total assets against a published 0.12 band, so it carries the weekly steps of both legs |
| NY Fed overnight reverse repo (ON RRP) | Federal Reserve Bank of New York | 2018-04-03 | business daily | `nyfed_on_rrp`: 16:00 ET, reference date + 1 day; `nyfed_on_rrp_sameday`: 15:00 ET, reference date + 0 days | the sum of amounts accepted over the day's operations; dated at 16:00 ET on the next business day because the Desk states no publication time. The same-day reading (#445) carries a value only on dates whose records were last written on the day itself before 15:00 | 10 of 2104 rows (`on_rrp_sameday`) | an amount accepted that day, not the balance outstanding (registry note on nyfed_on_rrp); the same-day column has holes on dates without evidence |
| NY Fed standing repo facility and repo operations | Federal Reserve Bank of New York | 2018-04-03 to 2021-07-29, by column | business daily | `nyfed_srf`: 16:00 ET, reference date + 1 day; `nyfed_repo_ops`: 16:00 ET, reference date + 1 day; `nyfed_repo_ops_sameday`: 16:00 ET, reference date + 0 days | results are dated at 16:00 ET on the next business day: the Desk states no publication time and `lastUpdated` is a write time that was rewritten days later. The same-day sensitivity (#442) withholds the dates written after their own 16:00 | none | `srf_take_up` starts with the facility's first operation on 2021-07-29, the `fed_repo_*` columns are present from the start of the panel; a day on which nothing was taken is 0.0 |
| Treasury auctions: gross settlements | U.S. Department of the Treasury Fiscal Data | 2018-04-03 | event | `treasury_auctions`: 23:59 ET, reference date + 0 days | dated from the settlement by the published registry; the `@per_release` reading dates each settlement from the auction announcement at 12:00 ET (#541). Records carry no revision history | none | one aggregate across security types; SOMA add-ons are not in it; an auction with 'null' total_accepted at retrieval has no result instant; `treasury_settlement_soma` is a hole under announcement dating |
| Treasury auctions: net settlement | U.S. Department of the Treasury, Bureau of the Fiscal Service | 2018-04-03 | business daily | `treasury_auction_net_settlement`: 12:00 ET, reference date + 0 days | counts the auctions announced on or before the day, at 12:00 ET; the announcement clock time is declared conservatively, not verified | none | the maturing amount is an estimate of the publicly held share (registry limitation) |
| Treasury daily bill rates | U.S. Department of the Treasury | 2018-04-03 | business daily | `treasury_bill_rates`: 16:30 ET, reference date + 0 days | one export per year; the quote date is the record date and availability is declared at 16:30 ET on it | none | the export header is not stable across years (17-week from 2022, 6-week from 2025); the page's quote time is the subject of #445, and a same-day reading is excluded |
| Treasury Daily Treasury Statement: TGA close | U.S. Department of the Treasury, Bureau of the Fiscal Service | 2018-04-03 to 2018-04-04, by column | business daily | `treasury_dts_tga`: 16:30 ET, reference date + 1 day | the statement for a business day is published at 4:00 PM ET on the next business day; 16:30 ET that day is declared. The API keeps no vintages | none | a daily series beside FRED's weekly WTREGEN; the two are near-duplicates in the matrix |
| OFR short-term funding monitor: DVP, tri-party and GCF repo rates | Office of Financial Research | 2018-04-03 to 2020-10-23, by column | business daily | `ofr_stfm_repo`: 16:00 ET, reference date + 2 days; `ofr_stfm_repo_segments`: 16:00 ET, reference date + 2 days | the API states no publication time and keeps no vintages; its one timestamp is a last-write time. A day's value is dated at 16:00 ET two business days after it | 1257 of 1463 rows (`ofr_gcf_rate`) | history before 2020-09-09 was filled in after the OFR began publishing in real time and is blanked by a guard (#508, #522), so these series start in September 2020; the `_backfill` column therefore equals the real-time one here |
| NY Fed primary dealer statistics (FR 2004) | Federal Reserve Bank of New York | 2018-04-03 | weekly | `nyfed_fr2004`: 16:30 ET, reference date + 6 days | weekly, dated six days after the as-of date at 16:30 ET. The lag rests on the published release schedule and not on the snapshot | none | a '*' marks a figure withheld for confidentiality and yields no observation; the tracked export mixes as-of dates, so no date is taken from the file as a whole |
| Fed IORB implementation notes | Board of Governors of the Federal Reserve System | 2018-04-04 to 2018-06-14, by column | event | `fed_iorb_announcements`: 23:59 ET, reference date + 0 days | an event table of every note that changed the rate since 2018-04; each note is read only at or after its announcement instant. No revisions | 2026 of 2053 rows (`iorb_days_to_announced_change`) | scheduled: public at lead 1 only, a hole at longer leads; `iorb_days_to_announced_change` is a hole on days with no change scheduled, so its gaps are by design; a 0.0 change is a computed value, not a missing one |
| Policy register (hand-kept) | Board of Governors of the Federal Reserve System; Federal Reserve Bank of New York; U.S. Congress | 2018-04-03 | event | `policy_register`: 16:00 ET, reference date + 0 days | computed from `metadata/policy_events.json` entries announced at or before 16:00 ET on the row's own date; no vintages | none | a register built by hand, not fetched; the in-force flags are step functions of the calendar, so a correlation with them is also a correlation with the period (this screen's reading, Tables 6 and 7) |
| Constructed from the sources above (no source of their own) | Board of Governors of the Federal Reserve System (H.4.1, H.8), as read through the registry; U.S. Department of the Treasury, Bureau of the Fiscal Service; repo-market-model | 2018-04-03 to 2018-04-16, by column | business daily | `spread_nowcast`: 15:00 ET, reference date + 0 days; `satiation_columns`: 16:00 ET, reference date + 0 days; `satiation_distance_columns`: 16:00 ET, reference date + 0 days; `projected_reserves_columns`: 16:00 ET, reference date + 0 days | zero lag by construction: each row uses only reads the as-of rule allows at 16:00 ET on that day. The calendar columns are known in advance | none | the rolling satiation level works as a two-year reserves low and its hinge is on in 2022-23 (#621); the distance columns read reserves on the old weekly lag, one release behind the `+h41` rows they join (#622); the nowcast is the naive previous spread wherever its model is not fitted |
| sec_nmfp | - | not read | - | - | - | - | monthly as-filed bulk extracts with the extract's retrieval instant as availability; no panel column is built from it (`metadata/sec_nmfp_archives.json`) |
| frb_ddp | - | not read | - | - | - | - | not a panel source: read only by the pre-SOFR history study (#129) |
| treasury_bill_rates_sameday | - | not read | - | - | - | - | excluded: no publication time before 16:00 ET is evidenced (#445) |
| back-filled 2014-18 history | - | not read | - | - | - | - | stamped as public in real time from 2014 although its posting instant is null; not read (#572, guarded by PR #590; the posting dates are now #633) |

Table 9. Tests run. None is corrected for the number of tests.

| quantity | computed |
|---|---|
| series | 87 |
| pairwise Spearman cells (series pairs, in each of 9 matrices) | 33669 |
| Spearman cells against a target (series x leads x targets x splits) | 14355 |
| AUROC cells with a bootstrap interval (series x leads x splits) | 4785 |
| pre-onset cells with a bootstrap interval (series x splits, lead 1) | 957 |
| partial-correlation cells (top series x leads x targets) | 225 |
