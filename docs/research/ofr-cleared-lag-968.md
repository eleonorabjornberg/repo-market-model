# The OFR cleared-repo series at the lag the OFR states (#968)

**Serves:** H3 (new public data adds signal), step 1 (the segment screen); H5 step 2 if anything survives. Lens E of the five-lens review (#958). Development data, never a verdict (scoring protocol v1). No published declaration, panel, record or figure changes.

## Answer

**Nothing in the screen's verdict changes.** Read one business day after its date at 15:00, as the OFR's data-release page states, instead of two business days at 16:00, the cleared-repo series (DVP and GCF) carry the same signal for the same days.

* **The screen** (#478, extended to 2026-09-03 by #684). The DVP rate minus BGCR keeps its Spearman correlation with the +5 bp indicator (+0.175 declared, +0.177 stated at lead 1) and stays outside the twelve strongest series (rank 16 of 62 declared, 20 of 62 stated, by the strongest lead). The pre-onset AUC moves from 0.784 to 0.762. The DVP rate moves by 0.001 at lead 1; the GCF rate, which holds a value on 206 days only, from -0.059 to -0.078, both with far too few pressure days to rank. No other series moves, to the last digit.
* **The paired test of #187** for `ofr_dvp_minus_bgcr_bp`, re-run at both lags on the same days: **no effect** at both, on the win rule's own reading. No paired Brier difference differs between the two readings by more than 0.00011 (+5 bp against the persistence-logistic at h = 1), and none changes sign. Six of the 40 Brier comparisons change whether their interval includes zero, each with a bound within 0.0006 of zero. Nothing survives a correction at either lag, and the rate is not better than its benchmarks in the 2018-19 regime, which the OFR window does not hold.
* **Kill (#968 criterion 4): no change in the screen's verdict.**

Whether any OFR series joins a published declaration is Eleonora's decision, and this page does not ask it.

## What changed

* `metadata/sources_measurement.json`: a new source `ofr_stfm_repo_cleared` declares the OFR's preliminary DVP and GCF rates (`REPO-DVP_AR_OO-P`, `REPO-GCF_AR_OO-P`) at one business day, 15:00 ET. Its `availability_provenance` quotes the OFR's page, fetched on 19 October 2026: "The preliminary release is published daily at 3 p.m.", "Data for centrally cleared repo markets are generally made available with a one-day lag", "Data for tri-party repo are generally made available with a two-day lag". Tri-party stays at two days in `ofr_stfm_repo_segments`, which is unchanged, as is `ofr_stfm_repo` in the frozen `metadata/sources.json`. Every record already scored therefore reads what it read.
* `repo_model.dvp_segment`: `CLEARED_COLUMN_FIELDS` (`ofr_dvp_rate_1d`, `ofr_dvp_minus_bgcr_bp_1d`, `ofr_gcf_rate_1d`: the same values as their two-day originals, read a day earlier) and `add_cleared_columns`. Off in every published declaration. The guard that refuses an OFR value from before 2020-09-09 covers them (their names start `ofr_`).
* `tests/test_dvp_segment.py`, `OfrClearedLagTests`: Tuesday's rate is the latest read at Wednesday's 16:00 decision and is refused at a 14:00 one, with one recorded mutation.
* `scripts/source_screen.py panel` adds the three columns; `scripts/dvp_segment_inputs.py` runs `ofr_dvp_minus_bgcr_bp@1d`; `scripts/ofr_cleared_lag_968.py` tabulates both.

## The screen, each column at both lags

Both lags are read in one screen of the scratch panel (sha256 `3cad385a9a51…`, 2,042 scored days from 2018-06-29 to 2026-09-03, 145 above +5 bp), so the data, the days and the reading rules are the same and only the lag differs. A copy read at lead L equals its original at lead L - 1 in every cell, and the 63 other series are identical to the same screen without the copies; the script refuses to write if either fails.

### Table 1. Spearman correlation with the +5 bp indicator, pooled, by lead

| series | reading | lead 1 | lead 2 | lead 3 | lead 5 | lead 10 | days at lead 1 | rank at the strongest lead |
|---|---|---|---|---|---|---|---|---|
| `ofr_dvp_minus_bgcr_bp` | declared (2 days) | +0.175 | +0.175 | +0.173 | +0.200 | +0.163 | 1415 | 16 of 62 |
| `ofr_dvp_minus_bgcr_bp_1d` | stated (1 day) | +0.177 | +0.175 | +0.175 | +0.184 | +0.182 | 1416 | 20 of 62 |
| `ofr_dvp_rate` | declared (2 days) | +0.016 | +0.015 | +0.017 | +0.021 | +0.029 | 1415 | 49 of 62 |
| `ofr_dvp_rate_1d` | stated (1 day) | +0.015 | +0.016 | +0.015 | +0.019 | +0.031 | 1416 | 48 of 62 |
| `ofr_gcf_rate` | declared (2 days) | -0.059 | -0.047 | -0.076 | -0.052 | -0.015 | 205 | 37 of 62 |
| `ofr_gcf_rate_1d` | stated (1 day) | -0.078 | -0.059 | -0.047 | -0.080 | -0.046 | 206 | 36 of 62 |

### Table 2. Lead 1 in detail

| series | reading | level | change | ample days (pressure) | scarce days (pressure) | pre-onset AUC | pre-onset mean diff / sd |
|---|---|---|---|---|---|---|---|
| `ofr_dvp_minus_bgcr_bp` | declared | +0.629 | -0.090 | +0.016 (4) | +0.127 (33) | 0.784 | +0.84 |
| `ofr_dvp_minus_bgcr_bp_1d` | stated | +0.661 | -0.103 | +0.021 (4) | +0.132 (33) | 0.762 | +0.79 |
| `ofr_dvp_rate` | declared | +0.095 | -0.008 | +0.025 (4) | +0.425 (33) | 0.542 | +0.47 |
| `ofr_dvp_rate_1d` | stated | +0.097 | -0.030 | +0.026 (4) | +0.421 (33) | 0.539 | +0.47 |
| `ofr_gcf_rate` | declared | -0.430 | +0.035 | - (0) | +0.442 (16) | 0.404 | -0.11 |
| `ofr_gcf_rate_1d` | stated | -0.422 | -0.108 | - (0) | +0.411 (17) | 0.409 | -0.10 |

### Checks

* Every cell of every other series is identical to the same screen without the `_1d` columns.
* A `_1d` column at lead L equals its original at lead L - 1 in every cell (the same row is read), for every lead both were computed at.

The twelve strongest series (largest absolute pooled correlation over the leads) are the same with the declared and with the stated lag, and none of the three cleared-repo columns is among them: `policy_reserve_management_in_force`, `sofr_p99_iorb_bps`, `sofr_p75_iorb_bps`, `spread_bps`, `spread_nowcast_bps`, `reserve_balances`, `sofr_above_effr_share_20`, `reserve_scarcity_state`, `sofr_p99_iorb_sd15_bps`, `on_rrp_below_100bn`, `srf_take_up`, `on_rrp`. Exploratory, unadjusted for multiplicity.

## The paired test, at both lags

`scripts/dvp_segment_inputs.py` (#187), `ofr_dvp_minus_bgcr_bp` on the OFR window (2020-09-09 onward; first scored day 2020-12-09), against pressure model v1 and the persistence-logistic, at +5 and +10 bp, horizons 1 to 5, pooled and on onset days, and the CRPS at h = 1. Both readings use the same control runs, fold grid, seeds and bootstrap. The Holm correction runs over each reading's own 41 comparisons, not over #187's family of every group (the other groups are not re-scored here), so the outcome compares the two readings with each other and is not #187's own outcome.

### Table 3. #187's paired test for `ofr_dvp_minus_bgcr_bp`, at both lags (OFR window)

Paired Brier difference, benchmark minus candidate (positive favours the input), 90% stationary-bootstrap interval, and the one-sided p for improvement. ✓ = survives Holm over that reading's own 41 comparisons; ✗ = significantly worse after it.

#### Brier, all scored days

| reading | h | +5 vs v1 | p | +5 vs persistence-logistic | p | +10 vs v1 | p | +10 vs persistence-logistic | p |
|---|---|---|---|---|---|---|---|---|---|
| declared (2 days) | 1 | -0.0001 [-0.0004, +0.0001] | 0.7693 | -0.0025 [-0.0058, +0.0002] | 0.9080 | -0.0000 [-0.0002, +0.0001] | 0.6551 | +0.0002 [-0.0010, +0.0016] | 0.3713 |
| declared (2 days) | 2 | +0.0003 [+0.0000, +0.0007] | 0.0797 | +0.0003 [-0.0030, +0.0036] | 0.4391 | +0.0004 [+0.0001, +0.0009] | 0.0473 | +0.0011 [+0.0002, +0.0021] | 0.0485 |
| declared (2 days) | 3 | +0.0004 [+0.0001, +0.0007] | 0.0350 | +0.0020 [-0.0010, +0.0056] | 0.1418 | +0.0002 [+0.0000, +0.0004] | 0.0822 | +0.0011 [+0.0002, +0.0021] | 0.0517 |
| declared (2 days) | 4 | +0.0003 [+0.0001, +0.0006] | 0.0532 | +0.0022 [-0.0003, +0.0052] | 0.1045 | +0.0000 [-0.0000, +0.0001] | 0.2223 | +0.0012 [+0.0003, +0.0023] | 0.0449 |
| declared (2 days) | 5 | +0.0005 [+0.0001, +0.0009] | 0.0490 | +0.0013 [-0.0008, +0.0038] | 0.1786 | +0.0000 [-0.0000, +0.0001] | 0.1678 | +0.0015 [+0.0002, +0.0034] | 0.0805 |
| stated (1 day) | 1 | -0.0002 [-0.0005, -0.0000] | 0.9204 | -0.0026 [-0.0059, +0.0003] | 0.9150 | -0.0001 [-0.0003, +0.0001] | 0.7447 | +0.0002 [-0.0011, +0.0015] | 0.3866 |
| stated (1 day) | 2 | +0.0003 [+0.0000, +0.0007] | 0.0783 | +0.0003 [-0.0030, +0.0034] | 0.4403 | +0.0004 [+0.0001, +0.0009] | 0.0481 | +0.0010 [+0.0002, +0.0021] | 0.0502 |
| stated (1 day) | 3 | +0.0004 [+0.0001, +0.0007] | 0.0384 | +0.0020 [-0.0010, +0.0054] | 0.1440 | +0.0002 [-0.0000, +0.0006] | 0.0929 | +0.0011 [+0.0002, +0.0023] | 0.0486 |
| stated (1 day) | 4 | +0.0003 [+0.0001, +0.0006] | 0.0525 | +0.0022 [-0.0004, +0.0053] | 0.1050 | +0.0000 [-0.0001, +0.0001] | 0.3765 | +0.0012 [+0.0003, +0.0022] | 0.0463 |
| stated (1 day) | 5 | +0.0005 [+0.0001, +0.0009] | 0.0506 | +0.0013 [-0.0008, +0.0041] | 0.1785 | +0.0000 [-0.0000, +0.0001] | 0.1660 | +0.0015 [+0.0002, +0.0033] | 0.0802 |

#### Brier, onset days (#160)

| reading | h | +5 vs v1 | p | +5 vs persistence-logistic | p | +10 vs v1 | p | +10 vs persistence-logistic | p |
|---|---|---|---|---|---|---|---|---|---|
| declared (2 days) | 1 | -0.0000 [-0.0002, +0.0001] | 0.7692 | -0.0007 [-0.0018, +0.0003] | 0.8646 | -0.0000 [-0.0001, +0.0000] | 0.8658 | -0.0000 [-0.0002, +0.0002] | 0.5251 |
| declared (2 days) | 2 | +0.0001 [-0.0001, +0.0005] | 0.2208 | +0.0007 [-0.0006, +0.0021] | 0.2063 | -0.0000 [-0.0001, +0.0000] | 0.8256 | +0.0002 [-0.0001, +0.0006] | 0.1440 |
| declared (2 days) | 3 | +0.0001 [+0.0000, +0.0002] | 0.0879 | +0.0023 [-0.0000, +0.0051] | 0.0938 | -0.0000 [-0.0001, +0.0000] | 0.8975 | +0.0006 [-0.0000, +0.0014] | 0.0920 |
| declared (2 days) | 4 | +0.0001 [-0.0000, +0.0003] | 0.1209 | +0.0023 [-0.0000, +0.0053] | 0.0937 | -0.0000 [-0.0000, +0.0000] | 0.6157 | +0.0007 [-0.0000, +0.0016] | 0.0993 |
| declared (2 days) | 5 | +0.0002 [+0.0000, +0.0005] | 0.0829 | +0.0018 [-0.0000, +0.0044] | 0.0992 | +0.0000 [+0.0000, +0.0001] | 0.0668 | +0.0013 [+0.0001, +0.0032] | 0.1106 |
| stated (1 day) | 1 | -0.0001 [-0.0002, +0.0000] | 0.9015 | -0.0007 [-0.0018, +0.0002] | 0.8768 | -0.0001 [-0.0001, -0.0000] | 0.9615 | -0.0000 [-0.0002, +0.0002] | 0.6240 |
| stated (1 day) | 2 | +0.0001 [-0.0001, +0.0005] | 0.2113 | +0.0007 [-0.0006, +0.0021] | 0.2031 | -0.0000 [-0.0001, +0.0001] | 0.7263 | +0.0002 [-0.0001, +0.0006] | 0.1477 |
| stated (1 day) | 3 | +0.0001 [-0.0000, +0.0002] | 0.1110 | +0.0023 [-0.0000, +0.0051] | 0.0957 | -0.0001 [-0.0002, -0.0000] | 0.9062 | +0.0006 [-0.0000, +0.0014] | 0.0953 |
| stated (1 day) | 4 | +0.0001 [-0.0000, +0.0002] | 0.1595 | +0.0023 [-0.0000, +0.0053] | 0.0954 | -0.0000 [-0.0001, +0.0000] | 0.7493 | +0.0007 [-0.0000, +0.0016] | 0.1012 |
| stated (1 day) | 5 | +0.0002 [+0.0000, +0.0005] | 0.0824 | +0.0019 [+0.0000, +0.0044] | 0.0992 | +0.0000 [+0.0000, +0.0001] | 0.0794 | +0.0013 [+0.0000, +0.0032] | 0.1113 |

#### CRPS, horizon 1: control minus candidate, bp

| reading | CRPS control | CRPS candidate | difference | p improve | p worse |
|---|---|---|---|---|---|
| declared (2 days) | 1.0775 | 1.0672 | +0.0103 [-0.0031, +0.0242] | 0.1006 | 0.8994 |
| stated (1 day) | 1.0775 | 1.0674 | +0.0101 [-0.0044, +0.0243] | 0.1189 | 0.8812 |

#### The win rule (#187, items 3-5), as `dvp_segment.classify` reads it

| reading | outcome | +5 bp | +10 bp |
|---|---|---|---|
| declared (2 days) | **no effect** | no effect; survives at h=–; misses a, b, c | no effect; survives at h=–; misses a, b, c |
| stated (1 day) | **no effect** | no effect; survives at h=–; misses a, b, c | no effect; survives at h=–; misses a, b, c |

## Not checked, or for Eleonora

* **Whether the cleared columns replace the two-day ones in the records.** `ofr_gcf_rate`, `ofr_dvp_rate` and `ofr_dvp_minus_bgcr_bp` stay at two days everywhere they are read. Moving a column to the stated lag would change what a published or registered record reads, which is her decision; this page only shows that the screen does not change.
* **The 15:00 instant is the page's statement, not a measured first print.** The API keeps no vintages and states no publication time. The page says "generally": a day the release slips would be read a few hours early. The stale text in `ofr_stfm_repo` and `ofr_stfm_repo_segments` ("a one-business-day reading is reported as a sensitivity only") is left as it is.
* **#187's own outcome is not reproduced.** The win rule's Holm family covers every group and sensitivity of #187, whose runs are not repeated here. The two readings are compared under one narrower family.
* **The final series and the volumes** are not declared at the page's lag; only the two preliminary rates are.
* **The matrix of #629** (ordinary-day AUROC with intervals) is not re-run: its declaration is bound to panel `6a8388fb…`, which no longer rebuilds on main because merged directives changed three columns (`net_settlement_due_5d` by #738, `srf_take_up` and `srf_take_up_positive` by the test-trade rule). The panel used here is `8bc473d6…` without the copies, `3cad385a…` with them; none of the three changed columns is an OFR column.

## Reproduce

Published panel `4ddc3882…` rebuilds from the tracked fixtures (`REPRODUCIBILITY.md`); `OUT` is any scratch directory.

```
PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv --end 2026-09-03
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv --end 2026-09-03
PYTHONPATH=src python3 scripts/net_settlement.py panel --panel AUG2.csv --output AUG3.csv --end 2026-09-03
PYTHONPATH=src python3 scripts/policy_features.py panel --panel AUG3.csv --output AUG4.csv
PYTHONPATH=src python3 scripts/nowcast.py panel --panel AUG4.csv --output AUG6.csv --summary OUT/nowcast_panel.json --end 2026-09-03
PYTHONPATH=src python3 scripts/dvp_segment_inputs.py panel --panel PUB.csv --output DVP.csv --end 2026-09-03
PYTHONPATH=src python3 scripts/early_warning_inputs.py panel --panel PUB.csv --output EW.csv --end 2026-09-03
PYTHONPATH=src python3 scripts/satiation_distance_598.py panel --panel AUG6.csv --output AUG2D.csv --end 2026-09-03
PYTHONPATH=src python3 scripts/source_screen.py panel --panel AUG6.csv --extra DVP.csv EW.csv AUG2D.csv --output SCREEN.csv     # sha256 3cad385a…
PYTHONPATH=src python3 scripts/source_screen.py run --panel SCREEN.csv --output OUT/screen.json
PYTHONPATH=src python3 scripts/ofr_cleared_lag_968.py compare OUT/screen.json --output OUT/screen_compare.json --markdown OUT/screen_compare.md
# the paired test: the scoring panel is dvp_segment_inputs.py's, to 2025-12-31 (sha256 608f872d…)
PYTHONPATH=src python3 scripts/dvp_segment_inputs.py panel --panel PUB.csv --output DVP25.csv
for H in 1 2 3 4 5; do for RUN in control@ofr persistence_logistic@ofr ofr_dvp_minus_bgcr_bp ofr_dvp_minus_bgcr_bp@1d; do
  PYTHONPATH=src python3 scripts/dvp_segment_inputs.py run --panel DVP25.csv --run $RUN --horizon $H --output OUT/runs/${RUN}_h$H.pickle; done; done
for H in 1 2 3 4 5; do for RUN in ofr_dvp_minus_bgcr_bp ofr_dvp_minus_bgcr_bp@1d; do
  PYTHONPATH=src python3 scripts/dvp_segment_inputs.py pair --panel DVP25.csv --runs OUT/runs --run $RUN --horizon $H; done; done
for RUN in ofr_dvp_minus_bgcr_bp ofr_dvp_minus_bgcr_bp@1d; do
  PYTHONPATH=src python3 scripts/dvp_segment_inputs.py crps --panel DVP25.csv --run $RUN --output OUT/runs/crps_$RUN.json; done
PYTHONPATH=src python3 scripts/ofr_cleared_lag_968.py gbm --runs OUT/runs --output OUT/gbm.json --markdown OUT/gbm.md
```

Evidence: `docs/research/ofr-cleared-lag-968/` (`screen_compare.json` every compared cell, `gbm.json` every paired comparison). Nothing is written into `docs/runs/`. Each run of the paired test takes about a minute and a half on four cores; the whole set under an hour.
