| input | source | in the published declaration | as-of availability | declared candidates reading it today |
|---|---|---|---|---|
| `bgcr` | nyfed_bgcr | yes | nyfed_bgcr: 1 business day after the ref_date at 15:00 | none |
| `dealer_treasury_position` (this directive) | nyfed_fr2004 | yes | nyfed_fr2004: 6 business days after the ref_date at 16:30 | balance_sheet_hierarchical_logistic, balance_sheet_scarcity_gbm |
| `effr` | nyfed_effr | yes | nyfed_effr: 1 business day after the ref_date at 15:00 | none |
| `fed_repo_accepted` | nyfed_repo_ops | no | nyfed_repo_ops: 1 business day after the ref_date at 16:00 | none |
| `fed_repo_accepted_sameday` | nyfed_repo_ops_sameday | no | nyfed_repo_ops_sameday: 0 business days after the ref_date at 16:00 | none |
| `fed_repo_days_since_positive` (this directive) | nyfed_repo_ops | no | nyfed_repo_ops: 1 business day after the ref_date at 16:00 | hierarchical_logistic_fed_repo, hierarchical_logistic_srf |
| `fed_repo_days_since_positive_sameday` | nyfed_repo_ops_sameday | no | nyfed_repo_ops_sameday: 0 business days after the ref_date at 16:00 | hierarchical_logistic_fed_repo_sameday, hierarchical_logistic_srf_sameday |
| `fed_repo_log_accepted` (this directive) | nyfed_repo_ops | no | nyfed_repo_ops: 1 business day after the ref_date at 16:00 | hierarchical_logistic_fed_repo, hierarchical_logistic_srf |
| `fed_repo_log_accepted_change` (this directive) | nyfed_repo_ops | no | nyfed_repo_ops: 1 business day after the ref_date at 16:00 | hierarchical_logistic_fed_repo, hierarchical_logistic_srf |
| `fed_repo_log_accepted_change_sameday` | nyfed_repo_ops_sameday | no | nyfed_repo_ops_sameday: 0 business days after the ref_date at 16:00 | hierarchical_logistic_fed_repo_sameday, hierarchical_logistic_srf_sameday |
| `fed_repo_log_accepted_sameday` | nyfed_repo_ops_sameday | no | nyfed_repo_ops_sameday: 0 business days after the ref_date at 16:00 | hierarchical_logistic_fed_repo_sameday, hierarchical_logistic_srf_sameday |
| `fed_repo_ops` (this directive) | nyfed_repo_ops | no | nyfed_repo_ops: 1 business day after the ref_date at 16:00 | hierarchical_logistic_fed_repo |
| `fed_repo_ops_sameday` | nyfed_repo_ops_sameday | no | nyfed_repo_ops_sameday: 0 business days after the ref_date at 16:00 | hierarchical_logistic_fed_repo_sameday |
| `fed_repo_rate_iorb_bps` (this directive) | fred_macro_latest_vintage, nyfed_repo_ops | no | fred_macro_latest_vintage: snapshot_retrieved_at; nyfed_repo_ops: 1 business day after the ref_date at 16:00 | hierarchical_logistic_fed_repo |
| `fed_repo_rate_iorb_bps_sameday` | fred_macro_latest_vintage, nyfed_repo_ops_sameday | no | fred_macro_latest_vintage: snapshot_retrieved_at; nyfed_repo_ops_sameday: 0 business days after the ref_date at 16:00 | hierarchical_logistic_fed_repo_sameday |
| `fed_repo_submitted` (this directive) | nyfed_repo_ops | no | nyfed_repo_ops: 1 business day after the ref_date at 16:00 | hierarchical_logistic_fed_repo |
| `fed_repo_submitted_sameday` | nyfed_repo_ops_sameday | no | nyfed_repo_ops_sameday: 0 business days after the ref_date at 16:00 | hierarchical_logistic_fed_repo_sameday |
| `iorb` | fred_macro_latest_vintage | yes | fred_macro_latest_vintage: snapshot_retrieved_at | none |
| `iorb_announced_change_bps` | fed_iorb_announcements | yes | fed_iorb_announcements: 0 calendar days after the record_date at 23:59 | none |
| `iorb_days_to_announced_change` | fed_iorb_announcements | yes | fed_iorb_announcements: 0 calendar days after the record_date at 23:59 | none |
| `mmf_assets` | sec_nmfp | yes | sec_nmfp: snapshot_retrieved_at | none |
| `net_settlement` (this directive) | treasury_auction_net_settlement | no | treasury_auction_net_settlement: 0 business days after the ref_date at 12:00 | hierarchical_logistic_net, onset_logistic_net+recalibrated |
| `net_settlement_bills` (this directive) | treasury_auction_net_settlement | no | treasury_auction_net_settlement: 0 business days after the ref_date at 12:00 | hierarchical_logistic_net, onset_logistic_net+recalibrated |
| `net_settlement_due_5d` (this directive) | treasury_auction_net_settlement | no | treasury_auction_net_settlement: 0 business days after the ref_date at 12:00 | hierarchical_logistic_net, onset_logistic_net+recalibrated |
| `ofr_gcf_rate` | ofr_stfm_repo_segments | no | ofr_stfm_repo_segments: 2 business days after the ref_date at 16:00 | onset_gbm_class_weight_funding+recalibrated, onset_logistic_class_weight_funding+recalibrated |
| `ofr_tri_rate` | ofr_stfm_repo_segments | no | ofr_stfm_repo_segments: 2 business days after the ref_date at 16:00 | onset_gbm_class_weight_funding+recalibrated, onset_logistic_class_weight_funding+recalibrated |
| `on_rrp` | fred_macro_latest_vintage | yes | fred_macro_latest_vintage: snapshot_retrieved_at | risk_gbm, risk_logistic, risk_quantile_skewt |
| `policy_days_since_known` (this directive) | policy_register | no | policy_register: 0 business days after the ref_date at 16:00 | onset_logistic_policy+recalibrated, rare_gbm_balanced_bootstrap_policy+recalibrated |
| `policy_days_until_effective` (this directive) | policy_register | no | policy_register: 0 business days after the ref_date at 16:00 | onset_logistic_policy+recalibrated, rare_gbm_balanced_bootstrap_policy+recalibrated |
| `policy_debt_limit_reinstated` (this directive) | policy_register | no | policy_register: 0 business days after the ref_date at 16:00 | onset_logistic_policy+recalibrated, rare_gbm_balanced_bootstrap_policy+recalibrated |
| `policy_iorb_offset_bp` (this directive) | policy_register | no | policy_register: 0 business days after the ref_date at 16:00 | onset_logistic_policy+recalibrated, rare_gbm_balanced_bootstrap_policy+recalibrated |
| `policy_pending_count` (this directive) | policy_register | no | policy_register: 0 business days after the ref_date at 16:00 | onset_logistic_policy+recalibrated, rare_gbm_balanced_bootstrap_policy+recalibrated |
| `policy_qt_in_force` (this directive) | policy_register | no | policy_register: 0 business days after the ref_date at 16:00 | onset_logistic_policy+recalibrated, rare_gbm_balanced_bootstrap_policy+recalibrated |
| `policy_reserve_management_in_force` (this directive) | policy_register | no | policy_register: 0 business days after the ref_date at 16:00 | onset_logistic_policy+recalibrated, rare_gbm_balanced_bootstrap_policy+recalibrated |
| `policy_slr_exclusion_in_force` (this directive) | policy_register | no | policy_register: 0 business days after the ref_date at 16:00 | onset_logistic_policy+recalibrated, rare_gbm_balanced_bootstrap_policy+recalibrated |
| `policy_standing_repo_in_force` (this directive) | policy_register | no | policy_register: 0 business days after the ref_date at 16:00 | onset_logistic_policy+recalibrated, rare_gbm_balanced_bootstrap_policy+recalibrated |
| `reserve_balances` | fred_macro_latest_vintage | yes | fred_macro_latest_vintage: snapshot_retrieved_at | base_adaptive_offset, base_online_platt, extreme_value_tail, onset_gbm_class_weight+recalibrated, onset_gbm_class_weight_funding+recalibrated, onset_gbm_focal+recalibrated and 43 more |
| `sofr` | nyfed_sofr | yes | nyfed_sofr: 1 business day after the ref_date at 15:00 | none |
| `sofr_p1` | nyfed_sofr | no | nyfed_sofr: 1 business day after the ref_date at 15:00 | none |
| `sofr_p25` | nyfed_sofr | yes | nyfed_sofr: 1 business day after the ref_date at 15:00 | published_v1, published_v1_blend_equal, published_v1_calendar_switch, published_v1_nowcast, published_v1_nowcast_substituted, published_v1_predicted_turn_switch and 4 more |
| `sofr_p75` | nyfed_sofr | yes | nyfed_sofr: 1 business day after the ref_date at 15:00 | published_v1, published_v1_blend_equal, published_v1_calendar_switch, published_v1_nowcast, published_v1_nowcast_substituted, published_v1_predicted_turn_switch and 4 more |
| `sofr_p75_iorb_bps` | fred_macro_latest_vintage, nyfed_sofr | no | fred_macro_latest_vintage: snapshot_retrieved_at; nyfed_sofr: 1 business day after the ref_date at 15:00 | risk_gbm, risk_logistic, risk_quantile_skewt |
| `sofr_p99` | nyfed_sofr | no | nyfed_sofr: 1 business day after the ref_date at 15:00 | none |
| `sofr_p99_iorb_bps` | fred_macro_latest_vintage, nyfed_sofr | no | fred_macro_latest_vintage: snapshot_retrieved_at; nyfed_sofr: 1 business day after the ref_date at 15:00 | risk_gbm, risk_logistic, risk_quantile_skewt |
| `sofr_p99_iorb_sd15_bps` | fred_macro_latest_vintage, nyfed_sofr | no | fred_macro_latest_vintage: snapshot_retrieved_at; nyfed_sofr: 1 business day after the ref_date at 15:00 | none |
| `sofr_volume` | nyfed_sofr | yes | nyfed_sofr: 1 business day after the ref_date at 15:00 | published_v1, published_v1_blend_equal, published_v1_calendar_switch, published_v1_nowcast, published_v1_nowcast_substituted, published_v1_predicted_turn_switch and 4 more |
| `tbill_13w` | treasury_bill_rates | yes | treasury_bill_rates: 0 calendar days after the record_date at 16:30 | published_v1, published_v1_blend_equal, published_v1_calendar_switch, published_v1_nowcast, published_v1_nowcast_substituted, published_v1_predicted_turn_switch and 4 more |
| `tbill_4w` | treasury_bill_rates | yes | treasury_bill_rates: 0 calendar days after the record_date at 16:30 | published_v1, published_v1_blend_equal, published_v1_calendar_switch, published_v1_nowcast, published_v1_nowcast_substituted, published_v1_predicted_turn_switch and 4 more |
| `tga` | fred_macro_latest_vintage | yes | fred_macro_latest_vintage: snapshot_retrieved_at | base_adaptive_offset, base_online_platt, extreme_value_tail, onset_gbm_class_weight+recalibrated, onset_gbm_class_weight_funding+recalibrated, onset_gbm_focal+recalibrated and 39 more |
| `tga_change_x_reserves` | fred_macro_latest_vintage, treasury_dts_tga | no | fred_macro_latest_vintage: snapshot_retrieved_at; treasury_dts_tga: 1 business day after the ref_date at 16:30 | none |
| `tga_daily` | treasury_dts_tga | no | treasury_dts_tga: 1 business day after the ref_date at 16:30 | onset_gbm_class_weight+recalibrated, onset_gbm_class_weight_funding+recalibrated, onset_gbm_focal+recalibrated, onset_logistic+recalibrated, onset_logistic_class_weight+recalibrated, onset_logistic_class_weight_funding+recalibrated and 7 more |
| `tga_daily_change` | treasury_dts_tga | no | treasury_dts_tga: 1 business day after the ref_date at 16:30 | onset_gbm_class_weight+recalibrated, onset_gbm_class_weight_funding+recalibrated, onset_gbm_focal+recalibrated, onset_logistic+recalibrated, onset_logistic_class_weight+recalibrated, onset_logistic_class_weight_funding+recalibrated and 7 more |
| `tgcr` | nyfed_tgcr | yes | nyfed_tgcr: 1 business day after the ref_date at 15:00 | none |
| `treasury_settlement` | treasury_auctions | yes | treasury_auctions: 0 calendar days after the record_date at 23:59 | balance_sheet_hierarchical_logistic, balance_sheet_scarcity_gbm, base_adaptive_offset, base_online_platt, hierarchical_logistic, hierarchical_logistic_fed_repo and 51 more |
| `treasury_settlement_bills` | treasury_auctions | yes | treasury_auctions: 0 calendar days after the record_date at 23:59 | none |
| `treasury_settlement_coupons` | treasury_auctions | yes | treasury_auctions: 0 calendar days after the record_date at 23:59 | risk_gbm, risk_gbm_base, risk_logistic, risk_logistic_base, risk_quantile_skewt, risk_quantile_skewt_base and 10 more |
| `treasury_settlement_soma` | treasury_auctions | yes | treasury_auctions: 0 calendar days after the record_date at 23:59 | none |
