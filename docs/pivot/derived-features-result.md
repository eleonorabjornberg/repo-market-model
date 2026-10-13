# Derived features, interactions and lagged pressure, screened on ordinary days, and one model test (#631)

A scratch measurement. It writes nothing into `docs/runs/`, publishes nothing, moves no published figure, reads no day after 2025-12-31 and scores no day of a locked tier
(`docs/decisions/lockbox.md`; `require_unlocked`). The declaration of the features, interactions, leads, tests, ranking rule and the single model test,
`metadata/derived_features_631.json` (with the two candidate files in `metadata/pressure_judge/candidates/`), was committed before any number was computed; the script refuses an uncommitted
declaration. The screen reads 2018-2025, so a result describes that history and is not a confirmation (ruling of 11 October 2026 on #567). **Nothing here is selected into a model or joins a published declaration.**
Its companion for the sources we already hold is #629; the ranked list below is laid out so the two can be read side by side.

## Result in one paragraph

On ordinary days (days that are not known risk dates: `1469` scored days of 2018-06-29 to 2025-12-31) the +5 bp indicator is true on `82` days, and they are not spread over the years: 62 fall in 2018-19, 15 in 2025-26, 5 in 2020 and 2024, none in 2021-23,
and 80 fall while the reserve-scarcity state is scarce. So a pooled AUROC mostly measures "which regime", not timing: the scarcity state alone scores 0.862. Read that way, the screen finds that **nothing beats the persistence reference**. The latest public spread scores 0.941 [0.91, 0.96] at lead 1;
the best derived feature, `tail_x_scarcity`, scores 0.935 [0.90, 0.96], and it sits in one cluster with the spread itself (|rho| >= 0.8). The features that rank high are the ones that restate the spread's recent history (days since the last pressure day, the last public indicator and its lags,
the 20-day realised volatility, the run above the median); inside the scarce state, where 80 of the 82 pressure days are, they fall to 0.64 to 0.80 against the spread's 0.82. The rate-range features (distance from the trailing 20- and 60-day minimum and maximum, z-scores) separate pooled (0.7 to 0.8 for
the maximum distances) but not inside a regime or the scarce state. The calendar features (day of the week, business day of the month, days to month-end, day in the maintenance period) carry no signal (AUROC 0.48 to 0.52, every interval covers 0.5). Of the four interactions, one is the tail spread
times scarcity (no gain over the tail spread), one (TGA change x satiation distance) has no signal, the settlement-size interactions are weak and mostly regime, and tail x reserve trend points the other way with an interval that covers 0.5.
The single model test, lagged pressure added to the every-day part of `risk_gbm+settle+h41+dist_roll`, **does not help**: on ordinary days its AUROC at h = 1 is lower than the parent's (0.864 against 0.903; paired difference -0.039 [-0.077, -0.014]), at h = 2 to 5 the paired intervals cover zero, its reliability slope is
further from 1, onset recall is lower (17 against 19 of 26) and the pooled false alarms per onset are unchanged (3.51 against 3.49 under the weighted rule). Both fail tier 1 and pass tiers 3 and 5, as the every-day part alone does.

## What was done

* **Scope.** The lead-1 fold grid of `source_screen.py` (`asof.fold_grid`, minimum history 61), 2018-06-29 to 2025-12-31, restricted to ordinary days: `announcement_dating_rescore.risk_flag(splits, values, True)` false, a function of the calendar and the auction schedule. Pressure days: the spread strictly above +5 bp on whole basis points.
* **Reading.** Every series through `asof.InformationRule` at the 16:00 decision, at leads of 1, 2, 3, 5 and 10 panel days, per field, with both guards, under the "both" timing of #541 (settlements dated from the auction announcement, H.4.1 weeklies per release) and the OFR rates only from their real-time start (#508, #522).
  A derived column on a row uses only rows up to and including it (`repo_model.derived_features`: a `Causal` view that raises `LookAheadError` on a later index, and `check_columns_causal`, which rebuilds columns on the panel cut at a row), and is declared on the source fields of the series it reads, so it is public when they all are.
  A calendar feature is a function of the date, known in advance, and read on the scored day. An interaction is the product of its two factors, each read as of the decision instant at its own latest public row. The pressure-history features count an outcome only from its own row.
  The rolling satiation distance for the interaction is built under the release dating, the construction #622 asks for (the fix of #623 is not on main; the model rows below still use #598's column).
* **Per series and lead** (`101` series, 5 leads): Spearman with the indicator, the spread level and the one-day change; AUROC for pressure days against the other ordinary days with a 90% stationary-bootstrap interval (1000 resamples, block 10, seed 631); the pre-onset contrast on the ordinary-day onsets with a 90% interval.
  Splits: pooled, the declared regimes, and the scarcity state read as of the decision instant. Intervals for split cells are computed only where the pooled |AUROC - 0.5| at that lead is at least 0.05 (declared), so most split cells are point estimates.
* **Count.** `4040` series x lead x split cells; `12120` Spearman correlations (3 targets each); `1860` AUROC points of which `1425` carry an interval; `472` pre-onset contrasts; one model test, and a second comparison reported beside it for reference. **This is exploratory: nothing is corrected for multiplicity.** At a 10% two-sided interval about one in ten null cells would exclude 0.5 by chance.

## Ranked list of leads (beside #629's)

The declared rule: a series is a candidate if its pooled AUROC interval excludes 0.5 at two or more leads; it is ranked by the checks it passes (the interval excludes 0.5 at three or more leads; its direction agrees in every regime with at least 5 pressure days; its pre-onset AUC interval excludes 0.5 the same way at lead 1;
it is the best of its cluster), then by |AUROC - 0.5|. Noise risk is low at 4 checks, medium at 2 or 3, high below. Only `6` of the 27 onsets fall on ordinary days (the 24 pre-onset days are few), and two regimes hold the pressure days, so the checks are weak ones: read "low" as "passes the declared checks", not as evidence of a usable signal.

| rank | series | direction | best lead | AUROC at best lead | leads excluding 0.5 | checks passed | noise risk | reason |
|---|---|---|---|---|---|---|---|---|
| 1 | `tail_x_scarcity` | higher series, more pressure | 1 | 0.935 | 5 | 4 of 4 | low | passes three_leads, regimes_agree, pre_onset, not_redundant; fails none; also in its cluster: spread_lag1, spread_lag5, spread_lag2 |
| 2 | `days_since_pressure` | lower series, more pressure | 1 | 0.068 | 5 | 4 of 4 | low | passes three_leads, regimes_agree, pre_onset, not_redundant; fails none |
| 3 | `spread_rv20` | higher series, more pressure | 1 | 0.893 | 5 | 4 of 4 | low | passes three_leads, regimes_agree, pre_onset, not_redundant; fails none; also in its cluster: spread_rv5 |
| 4 | `sofr_p99_max_dist_60` | higher series, more pressure | 10 | 0.817 | 5 | 4 of 4 | low | passes three_leads, regimes_agree, pre_onset, not_redundant; fails none; also in its cluster: sofr_p75_max_dist_60, sofr_p99_max_dist_20, tgcr_max_dist_20, bgcr_max_dist_20, sofr_p25_max_dist_20, sofr_p75_max_dist_20, sofr_p75_z_60, tgcr_z_60, sofr_p25_z_60, bgcr_z_60, sofr_z_60, tgcr_max_dist_60, bgcr_max_dist_60, sofr_max_dist_60, sofr_p25_max_dist_60, sofr_max_dist_20, sofr_p1_max_dist_20, sofr_p1_max_dist_60, sofr_p1_z_60, ofr_tri_rate_max_dist_60, ofr_tri_rate_max_dist_20, ofr_tri_rate_z_60 |
| 5 | `pressure_lag1` | higher series, more pressure | 1 | 0.755 | 5 | 4 of 4 | low | passes three_leads, regimes_agree, pre_onset, not_redundant; fails none |
| 6 | `effr_max_dist_60` | higher series, more pressure | 1 | 0.746 | 5 | 4 of 4 | low | passes three_leads, regimes_agree, pre_onset, not_redundant; fails none |
| 7 | `pressure_lag2` | higher series, more pressure | 3 | 0.728 | 5 | 4 of 4 | low | passes three_leads, regimes_agree, pre_onset, not_redundant; fails none |
| 8 | `effr_max_dist_20` | higher series, more pressure | 2 | 0.705 | 5 | 4 of 4 | low | passes three_leads, regimes_agree, pre_onset, not_redundant; fails none |
| 9 | `settle_x_scarcity` | higher series, more pressure | 1 | 0.693 | 4 | 4 of 4 | low | passes three_leads, regimes_agree, pre_onset, not_redundant; fails none |
| 10 | `above_median_run` | higher series, more pressure | 1 | 0.791 | 5 | 3 of 4 | medium | passes three_leads, regimes_agree, not_redundant; fails pre_onset |
| 11 | `pressure_last` | higher series, more pressure | 1 | 0.790 | 5 | 3 of 4 | medium | passes three_leads, regimes_agree, not_redundant; fails pre_onset |
| 12 | `pressure_lag5` | higher series, more pressure | 1 | 0.705 | 5 | 3 of 4 | medium | passes three_leads, regimes_agree, not_redundant; fails pre_onset |
| 13 | `bgcr_min_dist_20` | higher series, more pressure | 10 | 0.705 | 5 | 3 of 4 | medium | passes three_leads, regimes_agree, not_redundant; fails pre_onset; also in its cluster: tgcr_min_dist_20, sofr_p25_min_dist_20, sofr_p99_min_dist_20, sofr_p75_min_dist_20, sofr_min_dist_20 |
| 14 | `effr_min_dist_20` | higher series, more pressure | 1 | 0.674 | 5 | 3 of 4 | medium | passes three_leads, regimes_agree, not_redundant; fails pre_onset |
| 15 | `sofr_p1_min_dist_20` | higher series, more pressure | 10 | 0.652 | 3 | 3 of 4 | medium | passes three_leads, regimes_agree, not_redundant; fails pre_onset |
| 16 | `netsettle_x_scarcity` | higher series, more pressure | 2 | 0.613 | 2 | 2 of 4 | medium | passes regimes_agree, not_redundant; fails three_leads, pre_onset |
| 17 | `ofr_tri_rate_min_dist_20` | higher series, more pressure | 5 | 0.717 | 2 | 1 of 4 | high | passes not_redundant; fails three_leads, regimes_agree, pre_onset |

The reading that matters is the split table: at lead 1, by regime and by the scarce state, with the persistence reference at the bottom.

| series | pooled | 2018-19 | 2025-26 | scarce state | ample state |
|---|---|---|---|---|---|
| `tail_x_scarcity` | 0.935 [0.90, 0.96] | 0.857 [0.81, 0.90] | 0.916 [0.83, 0.97] | 0.791 [0.71, 0.86] | - |
| `days_since_pressure` | 0.068 [0.04, 0.10] | 0.190 [0.13, 0.25] | 0.091 [0.04, 0.19] | 0.201 [0.15, 0.26] | - |
| `spread_rv20` | 0.893 [0.85, 0.93] | 0.643 [0.52, 0.75] | 0.882 [0.79, 0.96] | 0.644 [0.54, 0.74] | - |
| `sofr_p99_max_dist_60` | 0.800 [0.72, 0.86] | 0.477 [0.33, 0.61] | 0.738 [0.58, 0.90] | 0.507 [0.39, 0.62] | - |
| `pressure_lag1` | 0.755 [0.69, 0.81] | 0.697 [0.62, 0.76] | 0.695 [0.55, 0.80] | 0.687 [0.62, 0.74] | - |
| `effr_max_dist_60` | 0.746 [0.66, 0.82] | 0.603 [0.49, 0.71] | 0.700 [0.50, 0.88] | 0.547 [0.43, 0.66] | - |
| `pressure_lag2` | 0.727 [0.66, 0.77] | 0.659 [0.58, 0.72] | 0.687 [0.54, 0.81] | 0.648 [0.58, 0.70] | - |
| `effr_max_dist_20` | 0.702 [0.64, 0.77] | 0.582 [0.47, 0.68] | 0.655 [0.51, 0.83] | 0.518 [0.42, 0.61] | - |
| `settle_x_scarcity` | 0.693 [0.65, 0.73] | 0.557 [0.52, 0.60] | 0.745 [0.69, 0.83] | 0.568 [0.52, 0.61] | - |
| `above_median_run` | 0.791 [0.72, 0.85] | 0.703 [0.59, 0.80] | 0.894 [0.77, 0.97] | 0.705 [0.62, 0.79] | - |
| `pressure_last` | 0.790 [0.73, 0.84] | 0.756 [0.70, 0.81] | 0.739 [0.60, 0.86] | 0.735 [0.68, 0.78] | - |
| `pressure_lag5` | 0.705 [0.63, 0.76] | 0.634 [0.54, 0.71] | 0.717 [0.61, 0.83] | 0.631 [0.56, 0.70] | - |
| `bgcr_min_dist_20` | 0.694 [0.63, 0.75] | 0.611 [0.52, 0.70] | 0.677 [0.54, 0.78] | 0.627 [0.55, 0.70] | - |
| `effr_min_dist_20` | 0.674 [0.60, 0.74] | 0.644 [0.53, 0.75] | 0.891 [0.80, 0.98] | 0.651 [0.55, 0.74] | - |
| `sofr_p1_min_dist_20` | 0.647 [0.56, 0.72] | 0.631 [0.54, 0.73] | 0.705 [0.57, 0.83] | 0.635 [0.54, 0.72] | - |
| `netsettle_x_scarcity` | 0.594 [0.54, 0.66] | 0.535 [0.48, 0.60] | 0.696 [0.63, 0.76] | 0.548 [0.50, 0.61] | - |
| `ofr_tri_rate_min_dist_20` | 0.593 [0.41, 0.70] | - | 0.575 [0.33, 0.76] | 0.535 [0.34, 0.69] | - |
| `spread_bps` | 0.941 [0.91, 0.96] | 0.832 [0.77, 0.88] | 0.923 [0.85, 0.97] | 0.817 [0.76, 0.86] | - |
| `spread_lag1` | 0.926 [0.90, 0.95] | 0.784 [0.71, 0.85] | 0.885 [0.78, 0.95] | 0.772 [0.70, 0.83] | - |

Pressure days on ordinary days by split: pooled 82 of 1469, regime:2018-19 62 of 294, regime:2020 3 of 195, regime:2021-23 0 of 586, regime:2024 2 of 197, regime:2025-26 15 of 197, state:ample 2 of 1065, state:scarce 80 of 404.

**Reading.** The list is dominated by the spread's own history (`days_since_pressure`, `pressure_last`, `pressure_lag1`/`2`/`5`, `spread_rv20`, `above_median_run`, `tail_x_scarcity`), none distinguishable above the persistence reference in any split (the intervals overlap). They are not new information; they are the persistence benchmark restated.
The pre-onset check is not independent of the regime for these: the pre-onset days are in 2019-20 and 2024, and the other ordinary days include 2021-23, in which no pressure day occurred (so `days_since_pressure` is large there and small in the active regimes).
The ranges of the rates (`sofr_p99_max_dist_60` and its cluster, `effr_max_dist_60`, `bgcr_min_dist_20`) are the only candidates not made of the spread, and their AUROC in the scarce state is 0.51 to 0.65: `sofr_p99_max_dist_60` 0.51 [0.39, 0.62] and `effr_max_dist_60` 0.55 [0.43, 0.66] cover 0.5, `bgcr_min_dist_20` 0.63 [0.55, 0.70] and `effr_min_dist_20` 0.65 [0.55, 0.74] do not. `effr_min_dist_20` is 0.89 [0.80, 0.98] in 2025-26 on 15 pressure days.
They are leads for a next declared test **conditional on persistence and the scarcity state** (a partial or incremental screen was not declared here, so it was not run), not for a model as they stand.

## The tables

Every series, with all five leads, is in `evidence/derived-features/screen-tables.md`; the full cells (Spearman with the three targets, AUROC with intervals, every split, the pre-onset contrast) are in `evidence/derived-features/screen.json`.

### Derived features (selected rows)

| series | lead 1 | lead 2 | lead 3 | lead 5 | lead 10 | Spearman with the indicator, lead 1 | pre-onset AUC, lead 1 |
|---|---|---|---|---|---|---|---|
| `above_median_run` | 0.791 [0.72, 0.85] | 0.790 [0.72, 0.85] | 0.783 [0.71, 0.85] | 0.789 [0.73, 0.85] | 0.759 [0.68, 0.83] | +0.255 | 0.56 [0.42, 0.73] |
| `bday_of_month` | 0.484 [0.40, 0.55] | 0.484 [0.40, 0.56] | 0.484 [0.41, 0.56] | 0.484 [0.39, 0.56] | 0.484 [0.41, 0.56] | -0.013 | 0.57 [0.41, 0.75] |
| `bgcr_z_60` | 0.407 [0.30, 0.50] | 0.388 [0.29, 0.48] | 0.377 [0.29, 0.47] | 0.369 [0.28, 0.46] | 0.377 [0.28, 0.48] | -0.074 | 0.19 [0.09, 0.31] |
| `days_since_pressure` | 0.068 [0.04, 0.10] | 0.080 [0.05, 0.12] | 0.087 [0.06, 0.13] | 0.085 [0.06, 0.12] | 0.088 [0.06, 0.13] | -0.344 | 0.16 [0.09, 0.25] |
| `days_to_month_end` | 0.522 [0.44, 0.60] | 0.522 [0.45, 0.61] | 0.522 [0.45, 0.60] | 0.522 [0.44, 0.61] | 0.522 [0.45, 0.61] | +0.018 | 0.46 [0.29, 0.61] |
| `dow` | 0.520 [0.47, 0.57] | 0.520 [0.47, 0.58] | 0.520 [0.47, 0.58] | 0.520 [0.47, 0.57] | 0.520 [0.47, 0.58] | +0.017 | 0.49 [0.46, 0.51] |
| `effr_max_dist_60` | 0.746 [0.66, 0.82] | 0.742 [0.66, 0.82] | 0.730 [0.64, 0.81] | 0.715 [0.61, 0.80] | 0.709 [0.61, 0.80] | +0.217 | 0.83 [0.76, 0.88] |
| `effr_z_60` | 0.441 [0.30, 0.57] | 0.434 [0.30, 0.56] | 0.446 [0.31, 0.57] | 0.445 [0.31, 0.57] | 0.441 [0.30, 0.58] | -0.047 | 0.17 [0.09, 0.31] |
| `maint_period_day` | 0.509 [0.46, 0.55] | 0.509 [0.46, 0.55] | 0.509 [0.46, 0.55] | 0.509 [0.46, 0.55] | 0.509 [0.46, 0.55] | +0.007 | 0.58 [0.46, 0.68] |
| `ofr_gcf_rate_z_60` | - | - | - | - | - | - | - |
| `ofr_tri_rate_z_60` | 0.163 [0.06, 0.23] | 0.172 [0.05, 0.26] | 0.169 [0.06, 0.25] | 0.166 [0.08, 0.24] | 0.153 [0.09, 0.26] | -0.155 | 0.15 |
| `sofr_p99_max_dist_60` | 0.800 [0.72, 0.86] | 0.804 [0.74, 0.86] | 0.817 [0.76, 0.87] | 0.812 [0.75, 0.86] | 0.817 [0.76, 0.87] | +0.240 | 0.84 [0.76, 0.90] |
| `sofr_p99_z_20` | 0.483 [0.42, 0.55] | 0.446 [0.37, 0.51] | 0.438 [0.35, 0.51] | 0.440 [0.34, 0.52] | 0.473 [0.40, 0.54] | -0.013 | 0.21 [0.13, 0.33] |
| `sofr_p99_z_60` | 0.483 [0.38, 0.57] | 0.459 [0.36, 0.54] | 0.458 [0.37, 0.55] | 0.439 [0.33, 0.52] | 0.453 [0.35, 0.55] | -0.014 | 0.26 [0.16, 0.39] |
| `spread_rv20` | 0.893 [0.85, 0.93] | 0.889 [0.84, 0.92] | 0.885 [0.84, 0.92] | 0.880 [0.84, 0.92] | 0.859 [0.81, 0.91] | +0.313 | 0.79 [0.67, 0.88] |
| `spread_rv5` | 0.855 [0.81, 0.89] | 0.829 [0.78, 0.87] | 0.825 [0.77, 0.87] | 0.827 [0.77, 0.88] | 0.831 [0.78, 0.88] | +0.283 | 0.84 [0.77, 0.89] |
| `tgcr_max_dist_20` | 0.774 [0.71, 0.84] | 0.759 [0.70, 0.83] | 0.764 [0.71, 0.83] | 0.768 [0.70, 0.83] | 0.760 [0.69, 0.83] | +0.223 | 0.82 [0.71, 0.90] |

### Interactions, and the sources they are made of

| series | lead 1 | lead 2 | lead 3 | lead 5 | lead 10 | Spearman with the indicator, lead 1 | pre-onset AUC, lead 1 |
|---|---|---|---|---|---|---|---|
| `netsettle_x_scarcity` | 0.594 [0.54, 0.66] | 0.613 [0.56, 0.67] | 0.570 [0.50, 0.65] | 0.544 [0.47, 0.62] | 0.482 [0.40, 0.57] | +0.104 | 0.51 [0.42, 0.61] |
| `reserve_change_5` | 0.409 [0.34, 0.48] | 0.429 [0.36, 0.50] | 0.428 [0.36, 0.50] | 0.424 [0.36, 0.50] | 0.461 [0.40, 0.53] | -0.072 | 0.62 [0.54, 0.67] |
| `reserve_scarcity_state` | 0.862 [0.82, 0.90] | 0.861 [0.81, 0.90] | 0.861 [0.82, 0.90] | 0.862 [0.82, 0.90] | 0.860 [0.82, 0.90] | +0.321 | 0.78 [0.59, 0.91] |
| `satiation_dist_roll` | 0.147 [0.10, 0.20] | 0.150 [0.10, 0.20] | 0.154 [0.11, 0.21] | 0.162 [0.12, 0.22] | 0.177 [0.13, 0.24] | -0.281 | 0.35 [0.22, 0.49] |
| `settle_x_scarcity` | 0.693 [0.65, 0.73] | 0.692 [0.66, 0.73] | 0.688 [0.65, 0.73] | 0.636 [0.60, 0.67] | 0.500 [0.50, 0.50] | +0.226 | 0.58 [0.52, 0.63] |
| `sofr_p99_iorb_bps` | 0.938 [0.91, 0.96] | 0.920 [0.88, 0.95] | 0.922 [0.89, 0.95] | 0.914 [0.88, 0.94] | 0.914 [0.87, 0.95] | +0.349 | 0.81 [0.70, 0.91] |
| `spread_bps` | 0.941 [0.91, 0.96] | 0.926 [0.89, 0.95] | 0.917 [0.88, 0.95] | 0.919 [0.88, 0.94] | 0.920 [0.89, 0.95] | +0.352 | 0.77 [0.61, 0.89] |
| `tail_x_reservetrend` | 0.399 [0.29, 0.51] | 0.431 [0.32, 0.54] | 0.424 [0.31, 0.54] | 0.406 [0.30, 0.52] | 0.427 [0.34, 0.53] | -0.081 | 0.71 [0.58, 0.80] |
| `tail_x_scarcity` | 0.935 [0.90, 0.96] | 0.924 [0.89, 0.95] | 0.918 [0.88, 0.95] | 0.915 [0.88, 0.94] | 0.913 [0.87, 0.95] | +0.381 | 0.79 [0.62, 0.92] |
| `tga_change_5d` | 0.590 [0.52, 0.65] | 0.587 [0.52, 0.66] | 0.585 [0.52, 0.65] | 0.583 [0.52, 0.64] | 0.579 [0.52, 0.64] | +0.072 | 0.36 [0.29, 0.45] |
| `tgachg_x_satdist` | 0.489 [0.42, 0.55] | 0.484 [0.42, 0.54] | 0.470 [0.41, 0.53] | 0.457 [0.40, 0.52] | 0.500 [0.45, 0.55] | -0.009 | 0.52 [0.41, 0.64] |

The tail spread times the scarcity state is the tail spread at the scarcity state's scale: 0.935 against 0.938 for the tail spread alone and 0.941 for the spread, and it is clustered with both. TGA change times the satiation distance has no signal at any lead (0.46 to 0.50, intervals cover 0.5). The gross settlement interaction is 0.69 pooled and 0.57 in the scarce state;
the net settlement interaction is weaker. Tail x reserve trend is 0.40 [0.29, 0.51]: the interval covers 0.5. At lead 10 `settle_x_scarcity` is constant (0.500 [0.50, 0.50]).

### Lagged pressure as inputs

| series | lead 1 | lead 2 | lead 3 | lead 5 | lead 10 | Spearman with the indicator, lead 1 | pre-onset AUC, lead 1 |
|---|---|---|---|---|---|---|---|
| `pressure_lag1` | 0.755 [0.69, 0.81] | 0.727 [0.66, 0.78] | 0.727 [0.65, 0.78] | 0.705 [0.63, 0.77] | 0.699 [0.63, 0.76] | +0.435 | 0.61 [0.53, 0.68] |
| `pressure_lag2` | 0.727 [0.66, 0.77] | 0.727 [0.65, 0.79] | 0.728 [0.65, 0.79] | 0.696 [0.62, 0.75] | 0.709 [0.65, 0.77] | +0.378 | 0.63 [0.54, 0.71] |
| `pressure_lag5` | 0.705 [0.63, 0.76] | 0.696 [0.62, 0.75] | 0.686 [0.63, 0.74] | 0.677 [0.61, 0.74] | 0.639 [0.59, 0.69] | +0.355 | 0.57 [0.47, 0.65] |
| `pressure_last` | 0.790 [0.73, 0.84] | 0.755 [0.69, 0.80] | 0.727 [0.66, 0.78] | 0.728 [0.65, 0.80] | 0.677 [0.60, 0.74] | +0.511 | 0.55 [0.49, 0.60] |
| `spread_bps` | 0.941 [0.91, 0.96] | 0.926 [0.89, 0.95] | 0.917 [0.88, 0.95] | 0.919 [0.88, 0.94] | 0.920 [0.89, 0.95] | +0.352 | 0.77 [0.61, 0.89] |
| `spread_lag1` | 0.926 [0.90, 0.95] | 0.917 [0.88, 0.94] | 0.919 [0.89, 0.94] | 0.918 [0.89, 0.94] | 0.909 [0.88, 0.94] | +0.339 | 0.81 [0.68, 0.90] |
| `spread_lag2` | 0.917 [0.89, 0.95] | 0.919 [0.89, 0.94] | 0.919 [0.88, 0.95] | 0.915 [0.88, 0.94] | 0.905 [0.87, 0.93] | +0.332 | 0.84 [0.73, 0.91] |
| `spread_lag5` | 0.918 [0.89, 0.94] | 0.915 [0.88, 0.94] | 0.919 [0.89, 0.94] | 0.920 [0.89, 0.95] | 0.894 [0.86, 0.92] | +0.333 | 0.82 [0.72, 0.90] |

The last public indicator and the spread at lags 1, 2 and 5 are all near the persistence reference (0.89 to 0.94 for the spread and its lags) and fall off a little with the lag; the indicator versions (0.68 to 0.79) throw away the level and score lower. This is what the persistence benchmark reads, restated.

### Clusters at |rho| >= 0.8

Single linkage on the lead-1 Spearman matrix over ordinary days (all screened series and their sources); the matrix is in `evidence/derived-features/matrix.csv` and `.json`, the heatmap in `matrix.svg`. One representative per cluster is the member with the largest summed |rho| to the others, chosen without the outcome.

| representative | members |
|---|---|
| `sofr_p75_z_60` | `bgcr_max_dist_20`, `bgcr_max_dist_60`, `bgcr_min_dist_60`, `bgcr_z_60`, `effr_min_dist_60`, `effr_z_60`, `ofr_tri_rate_max_dist_20`, `ofr_tri_rate_max_dist_60`, `ofr_tri_rate_min_dist_60`, `ofr_tri_rate_z_60`, `sofr_max_dist_20`, `sofr_max_dist_60`, `sofr_min_dist_60`, `sofr_p1_max_dist_20`, `sofr_p1_max_dist_60`, `sofr_p1_min_dist_60`, `sofr_p1_z_60`, `sofr_p25_max_dist_20`, `sofr_p25_max_dist_60`, `sofr_p25_min_dist_60`, `sofr_p25_z_60`, `sofr_p75_max_dist_20`, `sofr_p75_max_dist_60`, `sofr_p75_min_dist_60`, `sofr_p75_z_60`, `sofr_p99_max_dist_20`, `sofr_p99_max_dist_60`, `sofr_p99_min_dist_60`, `sofr_p99_z_60`, `sofr_z_60`, `tgcr_max_dist_20`, `tgcr_max_dist_60`, `tgcr_min_dist_60`, `tgcr_z_60` |
| `sofr_p25` | `bgcr`, `effr`, `ofr_gcf_rate`, `ofr_tri_rate`, `sofr`, `sofr_p1`, `sofr_p25`, `sofr_p75`, `sofr_p99`, `tgcr` |
| `spread_bps` | `reserve_scarcity_state`, `sofr_p75_iorb_bps`, `sofr_p99_iorb_bps`, `spread_bps`, `spread_lag1`, `spread_lag2`, `spread_lag5`, `tail_x_scarcity` |
| `sofr_p75_z_20` | `bgcr_z_20`, `sofr_p1_z_20`, `sofr_p25_z_20`, `sofr_p75_z_20`, `sofr_z_20`, `tgcr_z_20` |
| `tgcr_min_dist_20` | `bgcr_min_dist_20`, `sofr_min_dist_20`, `sofr_p25_min_dist_20`, `sofr_p75_min_dist_20`, `sofr_p99_min_dist_20`, `tgcr_min_dist_20` |
| `bday_of_month` | `bday_of_month`, `days_to_month_end` |
| `spread_rv20` | `spread_rv20`, `spread_rv5` |

The inter-feature and feature-to-source structure is a few large blocks: the rate-level block (all ten rates, one cluster), a large block of the 60-day ranges and z-scores of the rates with their 20-day maximum distances, the 20-day minimum distances (one), the 20-day z-scores (one), the spread block (the spread, the tail and 75th-percentile spreads above IORB,
the scarcity state, the spread lags and `tail_x_scarcity`), the two realised-volatility windows, and `bday_of_month` with `days_to_month_end`. A screened rate-range feature is therefore, at the 0.8 threshold, mostly one of a few blocks rather than an independent reading.

## The model test: lagged pressure in the every-day part of `risk_gbm+settle+h41+dist_roll`

Declared: the control `risk_gbm+settle+h41+dist_roll` forecasts exactly 0 on a day that is not a risk date, so it has no every-day part. The test therefore adds the every-day component of #506 (a ridge logistic of spread > tau on `spread_bps`, `sofr_p75_iorb_bps`, `sofr_p99_iorb_bps`; no gate) to the control
to make the parent `risk_gbm+settle+h41+dist_roll+every_day`, and adds `pressure_last`, `pressure_lag1`, `pressure_lag2`, `pressure_lag5` to that component for the test `...+every_day+lagpress`. The single declared test is the test against the parent; the control is shown for reference. This reading of "the every-day part of" the row is marked as a question below.
Scored by the judge in force (`metadata/pressure_judge.json`, unchanged), walk-forward, a refit every 21 scored days from 61 days of history, h = 1 to 5, +5 and +10 bp, 2018-06-29 to 2025-12-31.

Table M1. The judge in force (tiers 1, 3 and 5; the weighted rule is the one in force, the flat rule is reported beside it). Tier 1: onsets flagged at some lead 1 to 5, recall [90%], the pooled false alarms per onset (a false alarm counted once however many leads flag it; limit 2, #550); tier 1 also needs the recall conditions at each lead.

| row | rule | onsets flagged | recall [90%] | pooled false alarms per onset | tier 1 | tier 3 | tier 5 | passes |
|---|---|---|---|---|---|---|---|---|
| `risk_gbm+settle+h41` | weighted | 14 of 26 | 0.538 [0.353, 0.710] | 1.44 | yes | no | no | no |
| `risk_gbm+settle+h41` | flat | 14 of 26 | 0.538 [0.353, 0.710] | 2.00 | yes | no | no | no |
| `risk_gbm+settle+h41+dist_roll` | weighted | 15 of 26 | 0.577 [0.400, 0.762] | 1.27 | yes | no | no | no |
| `risk_gbm+settle+h41+dist_roll` | flat | 15 of 26 | 0.577 [0.400, 0.762] | 1.85 | yes | no | no | no |
| `risk_gbm+settle+h41+dist_roll+every_day` | weighted | 19 of 26 | 0.731 [0.556, 0.889] | 3.49 | no | yes | yes | no |
| `risk_gbm+settle+h41+dist_roll+every_day` | flat | 17 of 26 | 0.654 [0.476, 0.826] | 5.62 | no | yes | yes | no |
| `risk_gbm+settle+h41+dist_roll+every_day+lagpress` | weighted | 17 of 26 | 0.654 [0.461, 0.826] | 3.51 | no | yes | yes | no |
| `risk_gbm+settle+h41+dist_roll+every_day+lagpress` | flat | 16 of 26 | 0.615 [0.429, 0.790] | 4.92 | no | yes | yes | no |

Table M2. On ordinary days at +5 bp: the forecast's AUROC for pressure days [90%], and the reliability intercept and slope (logistic of the outcome on logit(forecast); `-` where the forecast is constant or the fit is not formed). The control forecasts exactly 0 there.

| row | h | days | pressure days | mean forecast | realised | AUROC [90%] | intercept | slope |
|---|---|---|---|---|---|---|---|---|
| `risk_gbm+settle+h41+dist_roll` | 1 | 1469 | 82 | 0.0000 | 0.0558 | 0.500 (constant) | - | - |
| `risk_gbm+settle+h41+dist_roll` | 2 | 1469 | 82 | 0.0000 | 0.0558 | 0.500 (constant) | - | - |
| `risk_gbm+settle+h41+dist_roll` | 3 | 1469 | 82 | 0.0000 | 0.0558 | 0.500 (constant) | - | - |
| `risk_gbm+settle+h41+dist_roll` | 4 | 1468 | 82 | 0.0000 | 0.0559 | 0.500 (constant) | - | - |
| `risk_gbm+settle+h41+dist_roll` | 5 | 1467 | 82 | 0.0000 | 0.0559 | 0.500 (constant) | - | - |
| `risk_gbm+settle+h41+dist_roll+every_day` | 1 | 1469 | 82 | 0.0811 | 0.0558 | 0.903 [0.86, 0.94] | -0.51 | 1.00 |
| `risk_gbm+settle+h41+dist_roll+every_day` | 2 | 1469 | 82 | 0.0828 | 0.0558 | 0.844 [0.78, 0.90] | -0.61 | 0.94 |
| `risk_gbm+settle+h41+dist_roll+every_day` | 3 | 1469 | 82 | 0.0981 | 0.0558 | 0.802 [0.72, 0.87] | -0.72 | 0.98 |
| `risk_gbm+settle+h41+dist_roll+every_day` | 4 | 1468 | 82 | 0.0866 | 0.0559 | 0.827 [0.73, 0.89] | -0.57 | 0.99 |
| `risk_gbm+settle+h41+dist_roll+every_day` | 5 | 1467 | 82 | 0.0866 | 0.0559 | 0.814 [0.73, 0.88] | -0.83 | 0.85 |
| `risk_gbm+settle+h41+dist_roll+every_day+lagpress` | 1 | 1469 | 82 | 0.0840 | 0.0558 | 0.864 [0.79, 0.92] | -0.68 | 0.96 |
| `risk_gbm+settle+h41+dist_roll+every_day+lagpress` | 2 | 1469 | 82 | 0.0839 | 0.0558 | 0.799 [0.70, 0.88] | -0.95 | 0.79 |
| `risk_gbm+settle+h41+dist_roll+every_day+lagpress` | 3 | 1469 | 82 | 0.0900 | 0.0558 | 0.779 [0.68, 0.87] | -1.09 | 0.75 |
| `risk_gbm+settle+h41+dist_roll+every_day+lagpress` | 4 | 1468 | 82 | 0.0830 | 0.0559 | 0.786 [0.69, 0.87] | -1.03 | 0.73 |
| `risk_gbm+settle+h41+dist_roll+every_day+lagpress` | 5 | 1467 | 82 | 0.0854 | 0.0559 | 0.818 [0.71, 0.89] | -0.97 | 0.79 |

Table M3. Paired on ordinary days: the AUROC of the test less the parent's, 90% stationary-bootstrap interval.

| h | difference [90%] |
|---|---|
| 1 | -0.039 [-0.077, -0.014] |
| 2 | -0.045 [-0.100, +0.006] |
| 3 | -0.022 [-0.083, +0.033] |
| 4 | -0.040 [-0.098, +0.010] |
| 5 | +0.004 [-0.044, +0.052] |

Paired against the parent, with 90% stationary-bootstrap intervals (`evidence/derived-features/model-test-compare.md`; Table 3 of that file is the paired Brier difference at h = 1, positive favours the test):

Table 3. Paired Brier difference against the parent, +5 bp (the parent's squared error minus the row's, so positive favours the row), 90% interval, h = 1: all days, by regime and by pressure-day type.

| cell | days | difference |
|---|---|---|
| all | 1873 | +0.0015 [-0.0007, +0.0039] |
| regime 2018-19 | 375 | +0.0006 [-0.0097, +0.0117] |
| regime 2020 | 251 | +0.0064 [+0.0037, +0.0093] |
| regime 2021-23 | 748 | -0.0002 [-0.0003, -0.0000] |
| regime 2024 | 250 | +0.0015 [+0.0004, +0.0031] |
| regime 2025-26 | 249 | +0.0029 [-0.0024, +0.0087] |
| day_type month_end | 150 | +0.0023 [+0.0002, +0.0056] |
| day_type ordinary | 1603 | +0.0015 [-0.0010, +0.0043] |
| day_type quarter_end | 31 | +0.0000 [+0.0000, +0.0000] |
| day_type tax_date | 89 | +0.0000 [+0.0000, +0.0000] |

* **Judge.** Tier 1 fails for both (pooled false alarms per onset about 3.5 against a limit of 2; the parent flags 19 of 26 onsets and the test 17 of 26). Tiers 3 and 5 pass for both. Neither row passes the full rule. The control passes tier 1 and fails tiers 3 and 5, as before.
* **Ordinary days.** The parent's AUROC for pressure days is 0.903 [0.86, 0.94] at h = 1, 0.80 to 0.84 at h = 2 to 5; with lagged pressure it is 0.864 [0.79, 0.92] at h = 1 and 0.78 to 0.82 after. The paired difference is -0.039 [-0.077, -0.014] at h = 1 and covers zero at h = 2 to 5. The reliability slope, 0.85 to 1.00 for the parent, is 0.73 to 0.96 with lagged pressure (further from 1), and the intercept is more negative (the forecast is on the high side where the realised rate is lower).
  The control has no variation on these days (AUROC 0.5, calibration not formed).
* **Brier.** The paired Brier difference favours the test by +0.0015 [-0.0007, +0.0039] at h = 1, which does not exclude zero; the gain is concentrated in 2020 and 2024, the regimes with two onsets each, and 2021-23 is slightly worse.
* **Why (a likely reason, not tested).** `spread_bps` is already an input of the component, and the ridge logistic standardises it; the indicator at lags 0, 1, 2 and 5 are thresholdings of the same recent spreads, so the component gains parameters, not information, and with 82 pressure days on ordinary days in two regimes that costs ranking at h = 1.

## What was not checked, and marked questions for Eleonora (not settled in code)

1. **The maintenance-period anchor.** `maint_period_day` uses the 14-day Thursday-to-Wednesday grid anchored on the period that began Thursday 2019-04-25, read from the Federal Reserve Bank of Philadelphia's weekly maintenance calendar (a web listing, not a tracked Board table). It carries no signal here, so nothing turns on it; if the feature is wanted later, a tracked schedule is a data-meaning decision.
2. **The reading of "the every-day part of the row".** The row has none; the test builds it as in #506 (no gate). A different reading (the every-day part of `risk_gbm+every_day+gate+settle+h41+iorb`, with the gate and the IORB input) is a different test. The result above is for the reading declared.
3. **Not run, because not declared:** a partial or incremental screen of the rate-range features after the spread and the scarcity state are taken out (their own signal is mostly a regime read); a screen on risk dates; any lead beyond 10; a cluster-representative-only re-screen. They are the natural next declaration.
* **The satiation distance.** The screen's interaction reads the distance built under the release dating (#622). The model rows use #598's column on the older weekly lag, as the control row is defined; the fix of #623 is not on main, so the two are not the same column and the model test is not affected by the screen's version.
* **Persistence is not removed from the pooled numbers.** The pooled AUROCs are dominated by episodes and regimes. Nothing here says a feature predicts timing within an episode.
* **Pre-onset.** Six of the 27 onsets fall on ordinary days (2019-05-28, 2019-06-25, 2019-08-13, 2020-03-04, 2020-03-12, 2024-12-26), 24 pre-onset days; the intervals are wide and the cluster resampling of six onsets is coarse.
* **2026 and the live record.** No day of 2026 is read or scored, the live record, the pin, and every published declaration are unchanged. No "Publish?" question arises: nothing is proposed for the published declaration.
* **Comparison with #629.** #629's result page was not on main when this was written; the list is built to the same targets, leads and splits and can be laid beside it.

## Commands

Published panel `4ddc3882…` (`build` and `verify-panel` clean, unchanged); scratch panels as in `scripts/source_screen.py`'s docstring (`pressure_v1_1.py panel` through `nowcast.py panel`, `dvp_segment_inputs.py panel`, `early_warning_inputs.py panel`, `source_screen.py panel`) and `AUG2D` (`satiation_distance_598.py panel`).
`/opt/rmm-venv` (numpy 2.4.6, scikit-learn 1.9.1), `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`.

```
PYTHONPATH=src python3 scripts/derived_features_631.py declare
PYTHONPATH=src python3 scripts/derived_features_631.py panel --panel SCREEN.csv --output DERIV.csv
PYTHONPATH=src python3 scripts/derived_features_631.py run --panel DERIV.csv --output OUT/screen.json
PYTHONPATH=src python3 scripts/derived_features_631.py report OUT/screen.json --output-dir docs/pivot/evidence/derived-features
# the model test's forecasts, as in scripts/satiation_distance_598.py's docstring for the benchmarks, parents and control, then
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/derived_features_631.py model --panel AUG2D.csv --published PUB.csv --horizon $h --output OUT/v631_h$h.json
for r in weighted unweighted: PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUB.csv --rule $r --output OUT/judge_$r.json --markdown OUT/judge_$r.md OUT/bench_h?.json OUT/risk_h?.json OUT/ql_h?.json OUT/both_h?.json OUT/dist_h?.json OUT/v631_h?.json
PYTHONPATH=src python3 scripts/derived_features_631.py compare --rule weighted --panel PUB.csv --output OUT/compare.json --markdown OUT/compare.md OUT/bench_h?.json OUT/risk_h?.json OUT/ql_h?.json OUT/both_h?.json OUT/dist_h?.json OUT/v631_h?.json
PYTHONPATH=src python3 scripts/derived_features_631.py ordinary --panel PUB.csv --output OUT/ordinary.json 'OUT/dist_h{h}.json' 'OUT/v631_h{h}.json'
PYTHONPATH=src python3 scripts/derived_features_631.py model-report --weighted OUT/judge_weighted.json --unweighted OUT/judge_unweighted.json --ordinary OUT/ordinary.json --output OUT/model.md
```
