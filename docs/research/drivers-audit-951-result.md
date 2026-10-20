# Why do known repo-market drivers add nothing? Audit and re-run (#951, H5 step 4 and H2)

**Development data, not a verdict.** Nothing here is a confirmation, no lockbox day and no day after 2025-12-31 is scored, no published record is edited, and `gbm_funding`'s declaration is unchanged. The declaration is `metadata/drivers_audit_951.json`, committed before any number was computed; the script is `scripts/drivers_audit_951.py` (commands in its docstring). Panels: published panel digest `4ddc3882…`; the scratch panel is `AUG2D` of `scripts/spread_distribution_634.py` plus `scripts/net_settlement.py panel` (`AUG3`).

## Reading

1. **The ceiling is not a ceiling (suspect 1).** H2's reachable and ceiling fits are *aligned* (each target's design is read as of its own decision instant, so no calendar column is trained one day off); the ceiling differs from the reachable line in settings (400 rounds, 31 leaves, leaf 10 against 200, 15, 20) and in being cross-fitted on 159 correlated inputs over about 1,700 training rows per lead, with the blocks on both sides of the scored one. A fit that is more flexible, on more correlated inputs, can score worse out of sample; that is the explanation to test, by the nested lineup declared in section 3, not a finding.
   **What the nested lineup shows (section 3).** Cross-fitting the candidate's own nine inputs at the reachable settings scores far below the walk-forward `gbm_funding` on the same kind of target (+0.071 against +0.250 on ordinary days, vs B1; the day sets differ, so this is an observation and not a paired result): a cross-fit that trains on later and on other regimes' days is not an upper bound for a walk-forward fit, and in this study it is the weaker of the two. The best of the lineup is "candidate + other" (+0.208 [+0.073, +0.322]), whose extra columns are lagged spreads, realised volatility, nowcasts, day-of-week and maintenance-period columns and interaction terms, not the market drivers; no single driver family (reserves and TGA, rates and volumes, policy and facilities, net settlement, calendar) moves the candidate's skill beyond its interval. The family names are assigned by column-name prefix (`FAMILIES`). A paired headroom against the walk-forward reachable line on identical days is not computed here.

2. **Calendar and scheduled inputs trained one day off (suspect 2): real, but not where the "no gain" results were decided.** `gbm_funding` at lead 1 (through `treasury_settlement`) and variants a and b of #634 at every lead (`tax_date`, `treasury_settlement`) are one day off; so are #708/#763's nested families at lead 1, #726 and the published model at lead 1. H2's ceiling and reachable fits, `c_two_part_new`, H6's laws (#693, #739) and the readings of #853 are aligned. Section 1 lists every fit with its evidence.
3. **Rare-day splits (suspect 3): quarter-ends are too few for `min_samples_leaf=20` for most of the walk.** Only about a third of the refits have 20 quarter-end days in the training window (median 16); month-ends and tax dates reach 20 in most refits. A smaller leaf did not help, though: at leaf 5 the arms are worse pooled (below).
4. **Dilution (suspect 4) and the re-run.** On aligned (direct) pairs, adding the calendar and net-settlement inputs improves the grid CRPS everywhere pooled, on calendar days and on ordinary days (key comparison `direct_base_leaf5 -> direct_cal_leaf5`: skill +0.075 [+0.054, +0.098] pooled, +0.104 [+0.061, +0.160] on calendar days, +0.072 on ordinary days; by regime positive in 2018–19, 2024 and 2025–26 and not seen in 2020 and 2021–23). The same pair at the default leaf (`direct_base_leaf20 -> direct_cal_leaf20`) gives +0.053 [+0.037, +0.071] pooled. **Against the real control, `gbm_funding`, the picture is smaller:** direct pairs alone cost skill (`gbm_funding -> direct_base_leaf20` −0.054 [−0.098, −0.015] pooled, as #449 found for its twin), and the calendar inputs on direct pairs bring the arm back to the control pooled (`direct_cal_leaf20`: +0.001 [−0.042, +0.043]; `direct_cal_leaf5`: −0.024 [−0.076, +0.023]), with a gain only on calendar days (`direct_cal_leaf20`: +0.051 [−0.000, +0.114]; `direct_cal_leaf5`: +0.068 [+0.002, +0.141]). On the 750 decision days with a calendar target, `gbm_funding` is no better than B1 (−0.037 [−0.071, +0.001]) while `direct_cal_leaf5` is +0.033 [−0.047, +0.124] against B1 and +0.266 against B2; those intervals are wide (width 0.17–0.30), so the calendar-day test has little power against B1.
   So: the calendar and net-settlement inputs do carry signal once trained on aligned pairs, and the pooled test dilutes it (calendar days are a minority of days). But the direct pairing has its own cost on ordinary days and in 2021–23, so the whole-model comparison against `gbm_funding` is flat pooled. Whether that reopens the 15 October ruling is Eleonora's decision.

5. **The ruled one-step arm `onestep_cal_leaf20` (Eleonora's ruling of 19 October 2026, a named amendment made after 0189ba27 and before any score of the arm): the misalignment did not make the calendar inputs hurt here.** The arm is `direct_cal_leaf20` trained on the current one-step pairs. Against the real control it is **better**, not worse: `gbm_funding -> onestep_cal_leaf20` is +0.031 [+0.019, +0.045] pooled, +0.062 [+0.032, +0.107] on calendar days, +0.022 [+0.011, +0.033] on ordinary days and +0.095 [+0.043, +0.140] on quarter-ends, with no regime negative beyond its interval (2021-23 −0.011 [−0.030, +0.007]); only tax-date targets are slightly worse (−0.008 [−0.026, −0.002]). So the "calendar makes it worse" reading is **not reproduced**: reading the calendar inputs misaligned still beats `gbm_funding`. Alignment alone, with the calendar inputs fixed (`onestep_cal_leaf20 -> direct_cal_leaf20`), is −0.031 [−0.072, +0.008] pooled and −0.012 [−0.054, +0.025] on calendar days: not seen, and if anything the direct pairing costs skill, as the control comparison above showed (2018-19 −0.046 [−0.104, −0.010]; 2021-23 −0.174 [−0.253, −0.111]; 2024 +0.170 [+0.084, +0.235] in favour of direct; 2025-26 +0.056 [−0.069, +0.177]). The gain of the one-step arm over the control comes with the calendar inputs, whichever way they are paired; the leaf size is not what separates the arms. Whether the mechanism of #914 is harmless for these particular columns, or is masked by the other inputs, is not decided by this design: the arms differ in pairing only, one seed, one leaf size. Development data, not a verdict.

Limits of this reading: one candidate family (`gbm_funding`'s gbm), five arms, one seed of the stationary bootstrap, a leaf of 5 against 20 only, one set of calendar and net-settlement inputs (`quarter_end`, `tax_date`, `days_to_month_end`, `net_settlement`, `net_settlement_due_5d`), and no arm combining direct pairs with `treasury_settlement` aligned separately.

## 1. Which fits train a calendar or scheduled column one day off (suspect 2)

Rule 2 of `src/repo_model/asof.py` serves calendar columns and scheduled fields from the target row. A one-step fit pairs the target of row p + 1 with row p, so it learns such a column one day off. `net_settlement*` are observed columns (dated at their own day), not scheduled.

| result | fit | pairing | calendar or scheduled columns in it | trained one day off |
|---|---|---|---|---|
| #775/#758 (H2 #635) | reachable gbm | as_of_read | quarter_end, tax_date, days_to_month_end, treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, iorb_announced_change_bps, iorb_days_to_announced_change | no |
| #775/#758 (H2 #635) | ceiling gbm (cross-fitted) | as_of_read | quarter_end, tax_date, days_to_month_end, treasury_settlement, treasury_settlement_bills, treasury_settlement_coupons, iorb_announced_change_bps, iorb_days_to_announced_change | no |
| #634/#758 | gbm_funding, h=1 | one_step | treasury_settlement | treasury_settlement |
| #634/#758 | gbm_funding, h=2..5 | one_step | none | no |
| #634 | published (frozen CRPS command), h=1 | one_step | treasury_settlement | treasury_settlement |
| #634 | a_published_new, every lead | one_step | tax_date, treasury_settlement | tax_date, treasury_settlement |
| #634 | b_gbm_new, every lead | one_step | tax_date, treasury_settlement | tax_date, treasury_settlement |
| #634/#758 | c_two_part_new, every lead | direct | days_to_month_end, quarter_end, tax_date, treasury_settlement, treasury_settlement_coupons | no |
| #708/#763 | nested families (base and plus_*), h=1 | one_step | treasury_settlement | treasury_settlement |
| #708/#763 | nested families (base and plus_*), h=2..5 | one_step | none | no |
| #726 | gbm_funding on backfilled history, h=1 | one_step | treasury_settlement | treasury_settlement |
| #693/#739 (H6) | spread mean reversion and risk-date calendar/type-state laws | as_of_read | quarter_end, tax_date, days_to_month_end | no |
| #853 | reads P(>5 bp) off existing walks | as_of_read | none | no |

## 2. Rare days in each refit's training window (suspect 3)

Refits of the walk-forward (every 21 scored days, minimum history 61). A tree can put only the days of a group on one side of a split when the training window holds at least `min_samples_leaf` of them; below that the group is always mixed with ordinary days. Cells: refits whose window holds at least that many.

| lead | group | refits | days at first / median / last refit | with at least 20 | with at least 10 | with at least 5 |
|---|---|---|---|---|---|---|
| 1 | month_end | 90 | 2 / 34 / 65 | 65 | 80 | 85 |
| 1 | quarter_end | 90 | 0 / 16 / 30 | 33 | 63 | 78 |
| 1 | tax_date | 90 | 6 / 48 / 96 | 75 | 84 | 90 |
| 5 | month_end | 89 | 2 / 33 / 65 | 64 | 79 | 84 |
| 5 | quarter_end | 89 | 0 / 15 / 30 | 32 | 62 | 77 |
| 5 | tax_date | 89 | 6 / 48 / 93 | 74 | 83 | 89 |

## 3. The nested ceiling (suspect 1)

Cross-fitted as H2's ceiling is (10 contiguous blocks per lead, the walk-forward embargo), spread gbm at the reachable settings, scored on the ordinary-day targets of 1869 decision days against B1. The ceiling read is the best of the lineup, so it cannot score below the candidate's own inputs (best: candidate + other; at least the candidate's inputs: True).

| lineup entry | mean CRPS | skill against B1 [90%] |
|---|---|---|
| all inputs, reachable settings | 1.639 | +0.167 [+0.019, +0.287] |
| candidate + calendar | 1.719 | +0.126 [-0.035, +0.255] |
| candidate + net settlement | 1.736 | +0.118 [-0.043, +0.249] |
| candidate + other | 1.558 | +0.208 [+0.073, +0.322] |
| candidate + policy and facilities | 1.732 | +0.120 [-0.038, +0.245] |
| candidate + rates and volumes | 1.759 | +0.106 [-0.049, +0.236] |
| candidate + reserves and TGA | 1.880 | +0.045 [-0.137, +0.191] |
| candidate inputs | 1.829 | +0.071 [-0.100, +0.210] |

## 4. The declared re-run: tables

Development data, not a verdict. Skill = (mean S(first) - mean S(second)) / mean S(first) of the grid CRPS; positive favours the second arm; 90% interval of the stationary bootstrap (5th to 95th percentile).
Decision days: 1868 (2018-06-29 to 2025-12-23). `n` below is the number of decision days with at least one target in the cut.

### day type: calendar days

n = 750 decision days.

| first -> second | mean first | mean second | skill [90%] | interval width |
|---|---|---|---|---|
| B1 -> direct_base_leaf20 | 3.531 | 3.712 | -0.051 [-0.108, +0.008] | 0.117 |
| B1 -> direct_base_leaf5 | 3.531 | 3.810 | -0.079 [-0.147, -0.017] | 0.130 |
| B1 -> direct_cal_leaf20 | 3.531 | 3.476 | +0.016 [-0.053, +0.100] | 0.152 |
| B1 -> direct_cal_leaf5 | 3.531 | 3.414 | +0.033 [-0.047, +0.124] | 0.171 |
| B1 -> gbm_funding | 3.531 | 3.662 | -0.037 [-0.071, +0.001] | 0.072 |
| B1 -> onestep_cal_leaf20 | 3.531 | 3.435 | +0.027 [-0.017, +0.090] | 0.107 |
| B2 -> direct_base_leaf20 | 4.650 | 3.712 | +0.202 [+0.077, +0.362] | 0.284 |
| B2 -> direct_base_leaf5 | 4.650 | 3.810 | +0.181 [+0.058, +0.340] | 0.282 |
| B2 -> direct_cal_leaf20 | 4.650 | 3.476 | +0.252 [+0.129, +0.410] | 0.281 |
| B2 -> direct_cal_leaf5 | 4.650 | 3.414 | +0.266 [+0.151, +0.416] | 0.265 |
| B2 -> gbm_funding | 4.650 | 3.662 | +0.213 [+0.080, +0.381] | 0.301 |
| B2 -> onestep_cal_leaf20 | 4.650 | 3.435 | +0.261 [+0.133, +0.425] | 0.293 |
| direct_base_leaf20 -> direct_base_leaf5 | 3.712 | 3.810 | -0.026 [-0.050, -0.010] | 0.040 |
| direct_base_leaf20 -> direct_cal_leaf20 | 3.712 | 3.476 | +0.064 [+0.033, +0.110] | 0.077 |
| direct_base_leaf5 -> direct_cal_leaf5 | 3.810 | 3.414 | +0.104 [+0.061, +0.160] | 0.099 |
| direct_cal_leaf20 -> direct_cal_leaf5 | 3.476 | 3.414 | +0.018 [-0.016, +0.048] | 0.064 |
| gbm_funding -> direct_base_leaf20 | 3.662 | 3.712 | -0.014 [-0.056, +0.025] | 0.081 |
| gbm_funding -> direct_base_leaf5 | 3.662 | 3.810 | -0.041 [-0.093, +0.001] | 0.095 |
| gbm_funding -> direct_cal_leaf20 | 3.662 | 3.476 | +0.051 [-0.000, +0.114] | 0.114 |
| gbm_funding -> direct_cal_leaf5 | 3.662 | 3.414 | +0.068 [+0.002, +0.141] | 0.139 |
| gbm_funding -> onestep_cal_leaf20 | 3.662 | 3.435 | +0.062 [+0.032, +0.107] | 0.075 |
| onestep_cal_leaf20 -> direct_cal_leaf20 | 3.435 | 3.476 | -0.012 [-0.054, +0.025] | 0.079 |

### day type: coupon settlement

n = 1012 decision days.

| first -> second | mean first | mean second | skill [90%] | interval width |
|---|---|---|---|---|
| B1 -> direct_cal_leaf5 | 2.844 | 2.611 | +0.082 [-0.016, +0.167] | 0.183 |
| B1 -> gbm_funding | 2.844 | 2.966 | -0.043 [-0.089, +0.001] | 0.089 |
| B2 -> gbm_funding | 3.834 | 2.966 | +0.226 [+0.125, +0.328] | 0.202 |
| direct_base_leaf20 -> direct_base_leaf5 | 2.982 | 3.044 | -0.021 [-0.046, +0.003] | 0.049 |
| direct_base_leaf20 -> direct_cal_leaf20 | 2.982 | 2.673 | +0.104 [+0.072, +0.135] | 0.063 |
| direct_base_leaf5 -> direct_cal_leaf5 | 3.044 | 2.611 | +0.142 [+0.096, +0.183] | 0.087 |
| direct_cal_leaf20 -> direct_cal_leaf5 | 2.673 | 2.611 | +0.023 [-0.017, +0.060] | 0.077 |
| gbm_funding -> direct_base_leaf20 | 2.966 | 2.982 | -0.005 [-0.048, +0.035] | 0.084 |
| gbm_funding -> direct_cal_leaf5 | 2.966 | 2.611 | +0.120 [+0.053, +0.181] | 0.128 |
| gbm_funding -> onestep_cal_leaf20 | 2.966 | 2.705 | +0.088 [+0.065, +0.113] | 0.048 |
| onestep_cal_leaf20 -> direct_cal_leaf20 | 2.705 | 2.673 | +0.012 [-0.032, +0.053] | 0.084 |

### day type: month_end

n = 507 decision days.

| first -> second | mean first | mean second | skill [90%] | interval width |
|---|---|---|---|---|
| B1 -> direct_cal_leaf5 | 2.220 | 1.810 | +0.185 [+0.055, +0.297] | 0.243 |
| B1 -> gbm_funding | 2.220 | 2.150 | +0.032 [-0.034, +0.104] | 0.138 |
| B2 -> gbm_funding | 2.875 | 2.150 | +0.252 [+0.115, +0.379] | 0.264 |
| direct_base_leaf20 -> direct_base_leaf5 | 2.063 | 2.173 | -0.053 [-0.089, -0.017] | 0.072 |
| direct_base_leaf20 -> direct_cal_leaf20 | 2.063 | 1.917 | +0.070 [+0.020, +0.114] | 0.094 |
| direct_base_leaf5 -> direct_cal_leaf5 | 2.173 | 1.810 | +0.167 [+0.112, +0.212] | 0.101 |
| direct_cal_leaf20 -> direct_cal_leaf5 | 1.917 | 1.810 | +0.056 [+0.004, +0.108] | 0.104 |
| gbm_funding -> direct_base_leaf20 | 2.150 | 2.063 | +0.041 [-0.037, +0.109] | 0.146 |
| gbm_funding -> direct_cal_leaf5 | 2.150 | 1.810 | +0.158 [+0.047, +0.257] | 0.210 |
| gbm_funding -> onestep_cal_leaf20 | 2.150 | 1.912 | +0.110 [+0.051, +0.158] | 0.107 |
| onestep_cal_leaf20 -> direct_cal_leaf20 | 1.912 | 1.917 | -0.003 [-0.066, +0.064] | 0.130 |

### day type: ordinary

n = 1868 decision days.

| first -> second | mean first | mean second | skill [90%] | interval width |
|---|---|---|---|---|
| B1 -> direct_cal_leaf5 | 1.995 | 1.585 | +0.205 [+0.062, +0.334] | 0.272 |
| B1 -> gbm_funding | 1.995 | 1.496 | +0.250 [+0.133, +0.365] | 0.231 |
| B2 -> gbm_funding | 2.151 | 1.496 | +0.305 [+0.235, +0.372] | 0.137 |
| direct_base_leaf20 -> direct_base_leaf5 | 1.611 | 1.707 | -0.060 [-0.089, -0.034] | 0.055 |
| direct_base_leaf20 -> direct_cal_leaf20 | 1.611 | 1.524 | +0.054 [+0.035, +0.072] | 0.037 |
| direct_base_leaf5 -> direct_cal_leaf5 | 1.707 | 1.585 | +0.072 [+0.049, +0.095] | 0.046 |
| direct_cal_leaf20 -> direct_cal_leaf5 | 1.524 | 1.585 | -0.040 [-0.068, -0.013] | 0.055 |
| gbm_funding -> direct_base_leaf20 | 1.496 | 1.611 | -0.077 [-0.130, -0.029] | 0.100 |
| gbm_funding -> direct_cal_leaf5 | 1.496 | 1.585 | -0.060 [-0.124, -0.003] | 0.121 |
| gbm_funding -> onestep_cal_leaf20 | 1.496 | 1.462 | +0.022 [+0.011, +0.033] | 0.022 |
| onestep_cal_leaf20 -> direct_cal_leaf20 | 1.462 | 1.524 | -0.042 [-0.093, +0.004] | 0.098 |

### day type: quarter_end

n = 146 decision days.

| first -> second | mean first | mean second | skill [90%] | interval width |
|---|---|---|---|---|
| B1 -> direct_cal_leaf5 | 6.745 | 6.818 | -0.011 [-0.254, +0.152] | 0.406 |
| B1 -> gbm_funding | 6.745 | 7.639 | -0.133 [-0.212, -0.083] | 0.129 |
| B2 -> gbm_funding | 7.382 | 7.639 | -0.035 [-0.379, +0.345] | 0.723 |
| direct_base_leaf20 -> direct_base_leaf5 | 7.630 | 7.839 | -0.027 [-0.067, -0.009] | 0.058 |
| direct_base_leaf20 -> direct_cal_leaf20 | 7.630 | 6.755 | +0.115 [+0.027, +0.226] | 0.199 |
| direct_base_leaf5 -> direct_cal_leaf5 | 7.839 | 6.818 | +0.130 [-0.002, +0.261] | 0.263 |
| direct_cal_leaf20 -> direct_cal_leaf5 | 6.755 | 6.818 | -0.009 [-0.109, +0.052] | 0.162 |
| gbm_funding -> direct_base_leaf20 | 7.639 | 7.630 | +0.001 [-0.069, +0.042] | 0.111 |
| gbm_funding -> direct_cal_leaf5 | 7.639 | 6.818 | +0.107 [-0.081, +0.245] | 0.326 |
| gbm_funding -> onestep_cal_leaf20 | 7.639 | 6.910 | +0.095 [+0.043, +0.140] | 0.097 |
| onestep_cal_leaf20 -> direct_cal_leaf20 | 6.910 | 6.755 | +0.022 [-0.074, +0.123] | 0.198 |

### day type: tax_date

n = 214 decision days.

| first -> second | mean first | mean second | skill [90%] | interval width |
|---|---|---|---|---|
| B1 -> direct_cal_leaf5 | 4.919 | 5.412 | -0.100 [-0.329, +0.004] | 0.332 |
| B1 -> gbm_funding | 4.919 | 5.196 | -0.056 [-0.192, +0.039] | 0.231 |
| B2 -> gbm_funding | 7.162 | 5.196 | +0.275 [+0.134, +0.614] | 0.480 |
| direct_base_leaf20 -> direct_base_leaf5 | 5.531 | 5.590 | -0.010 [-0.047, +0.008] | 0.054 |
| direct_base_leaf20 -> direct_cal_leaf20 | 5.531 | 5.396 | +0.024 [-0.001, +0.090] | 0.091 |
| direct_base_leaf5 -> direct_cal_leaf5 | 5.590 | 5.412 | +0.032 [+0.008, +0.102] | 0.093 |
| direct_cal_leaf20 -> direct_cal_leaf5 | 5.396 | 5.412 | -0.003 [-0.032, +0.019] | 0.050 |
| gbm_funding -> direct_base_leaf20 | 5.196 | 5.531 | -0.065 [-0.195, -0.032] | 0.163 |
| gbm_funding -> direct_cal_leaf5 | 5.196 | 5.412 | -0.042 [-0.137, -0.012] | 0.125 |
| gbm_funding -> onestep_cal_leaf20 | 5.196 | 5.239 | -0.008 [-0.026, -0.002] | 0.024 |
| onestep_cal_leaf20 -> direct_cal_leaf20 | 5.239 | 5.396 | -0.030 [-0.106, -0.001] | 0.105 |

### pooled: all

n = 1868 decision days.

| first -> second | mean first | mean second | skill [90%] | interval width |
|---|---|---|---|---|
| B1 -> direct_base_leaf20 | 2.302 | 1.925 | +0.164 [+0.051, +0.258] | 0.207 |
| B1 -> direct_base_leaf5 | 2.302 | 2.023 | +0.121 [-0.001, +0.222] | 0.223 |
| B1 -> direct_cal_leaf20 | 2.302 | 1.824 | +0.208 [+0.103, +0.296] | 0.194 |
| B1 -> direct_cal_leaf5 | 2.302 | 1.871 | +0.187 [+0.073, +0.283] | 0.210 |
| B1 -> gbm_funding | 2.302 | 1.826 | +0.207 [+0.114, +0.289] | 0.175 |
| B1 -> onestep_cal_leaf20 | 2.302 | 1.769 | +0.232 [+0.143, +0.311] | 0.168 |
| B2 -> direct_base_leaf20 | 2.514 | 1.925 | +0.234 [+0.163, +0.310] | 0.147 |
| B2 -> direct_base_leaf5 | 2.514 | 2.023 | +0.195 [+0.119, +0.276] | 0.157 |
| B2 -> direct_cal_leaf20 | 2.514 | 1.824 | +0.275 [+0.205, +0.348] | 0.143 |
| B2 -> direct_cal_leaf5 | 2.514 | 1.871 | +0.256 [+0.184, +0.332] | 0.148 |
| B2 -> gbm_funding | 2.514 | 1.826 | +0.274 [+0.198, +0.353] | 0.155 |
| B2 -> onestep_cal_leaf20 | 2.514 | 1.769 | +0.296 [+0.222, +0.374] | 0.152 |
| direct_base_leaf20 -> direct_base_leaf5 | 1.925 | 2.023 | -0.051 [-0.074, -0.029] | 0.045 |
| direct_base_leaf20 -> direct_cal_leaf20 | 1.925 | 1.824 | +0.053 [+0.037, +0.071] | 0.034 |
| direct_base_leaf5 -> direct_cal_leaf5 | 2.023 | 1.871 | +0.075 [+0.054, +0.098] | 0.044 |
| direct_cal_leaf20 -> direct_cal_leaf5 | 1.824 | 1.871 | -0.026 [-0.050, -0.004] | 0.046 |
| gbm_funding -> direct_base_leaf20 | 1.826 | 1.925 | -0.054 [-0.098, -0.015] | 0.083 |
| gbm_funding -> direct_base_leaf5 | 1.826 | 2.023 | -0.108 [-0.159, -0.063] | 0.096 |
| gbm_funding -> direct_cal_leaf20 | 1.826 | 1.824 | +0.001 [-0.042, +0.043] | 0.086 |
| gbm_funding -> direct_cal_leaf5 | 1.826 | 1.871 | -0.024 [-0.076, +0.023] | 0.098 |
| gbm_funding -> onestep_cal_leaf20 | 1.826 | 1.769 | +0.031 [+0.019, +0.045] | 0.025 |
| onestep_cal_leaf20 -> direct_cal_leaf20 | 1.769 | 1.824 | -0.031 [-0.072, +0.008] | 0.080 |

### regime: 2018-19

n = 375 decision days.

| first -> second | mean first | mean second | skill [90%] | interval width |
|---|---|---|---|---|
| B1 -> direct_cal_leaf5 | 5.727 | 4.131 | +0.279 [+0.082, +0.408] | 0.326 |
| B1 -> gbm_funding | 5.727 | 3.993 | +0.303 [+0.140, +0.420] | 0.279 |
| B2 -> gbm_funding | 4.364 | 3.993 | +0.085 [+0.009, +0.181] | 0.172 |
| direct_base_leaf20 -> direct_base_leaf5 | 4.190 | 4.459 | -0.064 [-0.115, -0.029] | 0.085 |
| direct_base_leaf20 -> direct_cal_leaf20 | 4.190 | 4.032 | +0.038 [+0.021, +0.059] | 0.038 |
| direct_base_leaf5 -> direct_cal_leaf5 | 4.459 | 4.131 | +0.074 [+0.040, +0.118] | 0.078 |
| direct_cal_leaf20 -> direct_cal_leaf5 | 4.032 | 4.131 | -0.025 [-0.072, +0.014] | 0.086 |
| gbm_funding -> direct_base_leaf20 | 3.993 | 4.190 | -0.049 [-0.102, -0.012] | 0.089 |
| gbm_funding -> direct_cal_leaf5 | 3.993 | 4.131 | -0.035 [-0.105, +0.020] | 0.125 |
| gbm_funding -> onestep_cal_leaf20 | 3.993 | 3.855 | +0.034 [+0.020, +0.059] | 0.039 |
| onestep_cal_leaf20 -> direct_cal_leaf20 | 3.855 | 4.032 | -0.046 [-0.104, -0.010] | 0.093 |

### regime: 2020

n = 251 decision days.

| first -> second | mean first | mean second | skill [90%] | interval width |
|---|---|---|---|---|
| B1 -> direct_cal_leaf5 | 1.644 | 1.526 | +0.072 [-0.161, +0.246] | 0.407 |
| B1 -> gbm_funding | 1.644 | 1.417 | +0.138 [+0.011, +0.250] | 0.239 |
| B2 -> gbm_funding | 2.786 | 1.417 | +0.491 [+0.316, +0.626] | 0.310 |
| direct_base_leaf20 -> direct_base_leaf5 | 1.534 | 1.524 | +0.007 [-0.039, +0.058] | 0.096 |
| direct_base_leaf20 -> direct_cal_leaf20 | 1.534 | 1.571 | -0.024 [-0.073, +0.019] | 0.092 |
| direct_base_leaf5 -> direct_cal_leaf5 | 1.524 | 1.526 | -0.001 [-0.037, +0.036] | 0.073 |
| direct_cal_leaf20 -> direct_cal_leaf5 | 1.571 | 1.526 | +0.029 [-0.012, +0.081] | 0.093 |
| gbm_funding -> direct_base_leaf20 | 1.417 | 1.534 | -0.082 [-0.222, +0.020] | 0.242 |
| gbm_funding -> direct_cal_leaf5 | 1.417 | 1.526 | -0.077 [-0.235, +0.059] | 0.293 |
| gbm_funding -> onestep_cal_leaf20 | 1.417 | 1.435 | -0.013 [-0.048, +0.017] | 0.065 |
| onestep_cal_leaf20 -> direct_cal_leaf20 | 1.435 | 1.571 | -0.095 [-0.268, +0.034] | 0.302 |

### regime: 2021-23

n = 748 decision days.

| first -> second | mean first | mean second | skill [90%] | interval width |
|---|---|---|---|---|
| B1 -> direct_cal_leaf5 | 0.711 | 0.913 | -0.285 [-0.478, -0.115] | 0.363 |
| B1 -> gbm_funding | 0.711 | 0.717 | -0.009 [-0.134, +0.103] | 0.237 |
| B2 -> gbm_funding | 1.481 | 0.717 | +0.516 [+0.405, +0.616] | 0.211 |
| direct_base_leaf20 -> direct_base_leaf5 | 0.858 | 0.918 | -0.069 [-0.128, -0.011] | 0.117 |
| direct_base_leaf20 -> direct_cal_leaf20 | 0.858 | 0.852 | +0.008 [-0.014, +0.031] | 0.045 |
| direct_base_leaf5 -> direct_cal_leaf5 | 0.918 | 0.913 | +0.005 [-0.013, +0.024] | 0.036 |
| direct_cal_leaf20 -> direct_cal_leaf5 | 0.852 | 0.913 | -0.072 [-0.135, -0.015] | 0.120 |
| gbm_funding -> direct_base_leaf20 | 0.717 | 0.858 | -0.197 [-0.278, -0.134] | 0.144 |
| gbm_funding -> direct_cal_leaf5 | 0.717 | 0.913 | -0.273 [-0.394, -0.180] | 0.214 |
| gbm_funding -> onestep_cal_leaf20 | 0.717 | 0.725 | -0.011 [-0.030, +0.007] | 0.036 |
| onestep_cal_leaf20 -> direct_cal_leaf20 | 0.725 | 0.852 | -0.174 [-0.253, -0.111] | 0.142 |

### regime: 2024

n = 250 decision days.

| first -> second | mean first | mean second | skill [90%] | interval width |
|---|---|---|---|---|
| B1 -> direct_cal_leaf5 | 1.683 | 1.158 | +0.312 [+0.188, +0.395] | 0.207 |
| B1 -> gbm_funding | 1.683 | 1.411 | +0.162 [+0.092, +0.216] | 0.124 |
| B2 -> gbm_funding | 1.378 | 1.411 | -0.024 [-0.167, +0.128] | 0.295 |
| direct_base_leaf20 -> direct_base_leaf5 | 1.277 | 1.362 | -0.066 [-0.157, -0.009] | 0.149 |
| direct_base_leaf20 -> direct_cal_leaf20 | 1.277 | 1.138 | +0.109 [+0.061, +0.166] | 0.105 |
| direct_base_leaf5 -> direct_cal_leaf5 | 1.362 | 1.158 | +0.150 [+0.095, +0.222] | 0.127 |
| direct_cal_leaf20 -> direct_cal_leaf5 | 1.138 | 1.158 | -0.017 [-0.058, +0.010] | 0.068 |
| gbm_funding -> direct_base_leaf20 | 1.411 | 1.277 | +0.095 [-0.018, +0.161] | 0.179 |
| gbm_funding -> direct_cal_leaf5 | 1.411 | 1.158 | +0.179 [+0.092, +0.239] | 0.147 |
| gbm_funding -> onestep_cal_leaf20 | 1.411 | 1.372 | +0.028 [+0.007, +0.057] | 0.050 |
| onestep_cal_leaf20 -> direct_cal_leaf20 | 1.372 | 1.138 | +0.170 [+0.084, +0.235] | 0.152 |

### regime: 2025-26

n = 244 decision days.

| first -> second | mean first | mean second | skill [90%] | interval width |
|---|---|---|---|---|
| B1 -> direct_cal_leaf5 | 3.231 | 2.419 | +0.251 [+0.094, +0.376] | 0.282 |
| B1 -> gbm_funding | 3.231 | 2.742 | +0.151 [+0.078, +0.216] | 0.138 |
| B2 -> gbm_funding | 3.724 | 2.742 | +0.264 [+0.056, +0.392] | 0.336 |
| direct_base_leaf20 -> direct_base_leaf5 | 2.783 | 2.861 | -0.028 [-0.059, +0.007] | 0.067 |
| direct_base_leaf20 -> direct_cal_leaf20 | 2.783 | 2.372 | +0.148 [+0.115, +0.185] | 0.070 |
| direct_base_leaf5 -> direct_cal_leaf5 | 2.861 | 2.419 | +0.155 [+0.119, +0.197] | 0.078 |
| direct_cal_leaf20 -> direct_cal_leaf5 | 2.372 | 2.419 | -0.020 [-0.040, +0.004] | 0.044 |
| gbm_funding -> direct_base_leaf20 | 2.742 | 2.783 | -0.015 [-0.173, +0.121] | 0.294 |
| gbm_funding -> direct_cal_leaf5 | 2.742 | 2.419 | +0.118 [-0.020, +0.249] | 0.269 |
| gbm_funding -> onestep_cal_leaf20 | 2.742 | 2.512 | +0.084 [+0.054, +0.115] | 0.061 |
| onestep_cal_leaf20 -> direct_cal_leaf20 | 2.512 | 2.372 | +0.056 [-0.069, +0.177] | 0.246 |

