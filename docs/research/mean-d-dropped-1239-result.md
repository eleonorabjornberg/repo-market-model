# Mean d with the no-variance resamples dropped, on the rows of #1226 and #1196 (#1239)

**Development data, not a verdict** (scoring protocol v1, #640). **Hypothesis H5, step 3 (reporting); H1 (scorer).** Her ruling of 26 October 2026 (ledger item 57 on #1116, option 1 on finding #1236): when a resample of a row's daily difference has no long-run variance, drop it from the mean-d studentization and report how many were dropped. A row that has such resamples is re-read from the same seed and the same draws, the bound is taken from the rest, and the count of dropped resamples is printed beside it with the draws made. A row where every resample has none, or whose full series has none, stays "no reading", with the reason. `scoring_protocol.py` is unchanged; the rule is in `scripts/spread_mr_variants_761.py`.

## #1196: seed 1196, 10,000 draws, panel `4ddc3882…`

The study was re-scored on this tree against a re-score of main's tree without this change (the committed `result.json` no longer reproduces on main: its day counts differ, see below). 724 paired rows were compared. 720 had a mean-d bound before; 720 of them are unchanged to the last digit, and 0 moved. 4 were "no reading": 4 now have a bound by dropping, 0 have one without dropping, and 0 do not. Other differences outside the rows: 0.

The committed file differs from that baseline in 509 rows with a bound and 1174 other entries (for example `day_type_counts/month_end`, `day_type_counts/post_month_end_window`, `day_type_counts/quarter_end`, `day_type_counts/settlement`, `groups/lead/h=1/days`), so it is not the comparison for this change (main has since put the B2 thin-pool record in force, #1198, and changed the as-of order of a group's fields, #1060); the stale file is reported as a finding.

Rows that were "no reading" and now have a bound. d is the mean daily difference in score units (positive favours the candidate) with its 90% studentized interval from the draws that were kept. **No reading of better or worse is given for these rows**: the count beside each bound says how much of the stream was left out, and the reading is left for the page that uses it.

| row | days | mean d [90%] | dropped of draws |
|---|---|---|---|
| target_day_type / iorb_window / upper_tail_twcrps vs mr_cal_a_base / B1 | 78 | +2.6787 [-0.0806, +100.1219] | 1 of 10,000 (0.0%) |
| target_day_type / iorb_window / upper_tail_twcrps vs mr_cal_a_base / B1_prime | 78 | -0.3979 [-3.3624, +0.0050] | 1 of 10,000 (0.0%) |
| target_day_type / iorb_window / upper_tail_twcrps vs mr_cal_a_base / B2 | 78 | +0.4240 [-0.3289, +1.8115] | 1 of 10,000 (0.0%) |
| target_day_type / iorb_window / upper_tail_twcrps vs sc_s3_state / sc_s3_robust | 78 | +0.0039 [-0.0150, +0.0346] | 1 of 10,000 (0.0%) |

## #1226: seed 1226, 10,000 draws, panel `4ddc3882…`

The study was re-scored on this tree against its committed `result.json`. 724 paired rows were compared. 707 had a mean-d bound before; 707 of them are unchanged to the last digit, and 0 moved. 17 were "no reading": 17 now have a bound by dropping, 0 have one without dropping, and 0 do not. Other differences outside the rows: 0.

Rows that were "no reading" and now have a bound. d is the mean daily difference in score units (positive favours the candidate) with its 90% studentized interval from the draws that were kept. **No reading of better or worse is given for these rows**: the count beside each bound says how much of the stream was left out, and the reading is left for the page that uses it.

| row | days | mean d [90%] | dropped of draws |
|---|---|---|---|
| target_day_type / iorb_window / upper_tail_twcrps vs mr_cal_a_base / B1 | 78 | +2.6787 [-0.0625, +98.8141] | 2 of 10,000 (0.0%) |
| target_day_type / iorb_window / upper_tail_twcrps vs mr_cal_a_base / B1_prime | 78 | -0.3979 [-3.3186, +0.0160] | 2 of 10,000 (0.0%) |
| target_day_type / iorb_window / upper_tail_twcrps vs mr_cal_a_base / B2 | 78 | +0.4240 [-0.3228, +1.8073] | 2 of 10,000 (0.0%) |
| target_day_type / iorb_window / upper_tail_twcrps vs sc_s3_hw1 / B1 | 78 | +2.8374 [+0.1558, +37.5869] | 1 of 10,000 (0.0%) |
| target_day_type / iorb_window / upper_tail_twcrps vs sc_s3_hw1 / B1_prime | 78 | -0.2392 [-2.0048, +0.2733] | 1 of 10,000 (0.0%) |
| target_day_type / iorb_window / upper_tail_twcrps vs sc_s3_hw1 / B2 | 78 | +0.5828 [-0.3751, +2.9127] | 1 of 10,000 (0.0%) |
| target_day_type / iorb_window / upper_tail_twcrps vs sc_s3_hw1 / mr_cal_a_base | 78 | +0.1587 [-0.1032, +0.7241] | 3 of 10,000 (0.0%) |
| target_day_type / iorb_window / upper_tail_twcrps vs sc_s3_hw1 / sc_s3_robust | 78 | +0.0144 [-0.0405, +0.0790] | 3 of 10,000 (0.0%) |
| target_day_type / iorb_window / upper_tail_twcrps vs sc_s3_hw2 / B1 | 78 | +2.8189 [+0.1415, +38.8690] | 1 of 10,000 (0.0%) |
| target_day_type / iorb_window / upper_tail_twcrps vs sc_s3_hw2 / B1_prime | 78 | -0.2577 [-2.1557, +0.2471] | 1 of 10,000 (0.0%) |
| target_day_type / iorb_window / upper_tail_twcrps vs sc_s3_hw2 / B2 | 78 | +0.5642 [-0.3842, +2.7581] | 1 of 10,000 (0.0%) |
| target_day_type / iorb_window / upper_tail_twcrps vs sc_s3_hw2 / mr_cal_a_base | 78 | +0.1402 [-0.1061, +0.6772] | 3 of 10,000 (0.0%) |
| target_day_type / iorb_window / upper_tail_twcrps vs sc_s3_hw2 / sc_s3_robust | 78 | -0.0041 [-0.0574, +0.0323] | 3 of 10,000 (0.0%) |
| target_day_type / iorb_window / upper_tail_twcrps vs sc_s3_robust / B1 | 78 | +2.8230 [+0.1241, +41.1745] | 1 of 10,000 (0.0%) |
| target_day_type / iorb_window / upper_tail_twcrps vs sc_s3_robust / B1_prime | 78 | -0.2536 [-2.1456, +0.2186] | 1 of 10,000 (0.0%) |
| target_day_type / iorb_window / upper_tail_twcrps vs sc_s3_robust / B2 | 78 | +0.5683 [-0.3518, +2.6962] | 1 of 10,000 (0.0%) |
| target_day_type / iorb_window / upper_tail_twcrps vs sc_s3_robust / mr_cal_a_base | 78 | +0.1443 [-0.0737, +0.6894] | 3 of 10,000 (0.0%) |

## What this does not show

It scores nothing new: the tables above come from the same panel and seeds as the baselines they are compared with, and the committed pages are left as they are. A bound taken from the kept resamples is not the bound the full stream would give; the dropped resamples are those of a daily difference that is constant on the resample, so a row with a large count is a row whose difference is zero on most days. The pages of #1226 and #1196 and their `result.json` are not regenerated here; whether to regenerate them with these rows in place is hers.
