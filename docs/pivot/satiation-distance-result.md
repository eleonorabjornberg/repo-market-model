# The rolling satiation distance in the tier-1 passers (#598, follow-up to #587)

A scratch measurement under the pressure-day judge. It writes nothing into `docs/runs/`, publishes nothing, moves no published
figure, scores no day of 2026 and reads no day after 2025-12-31 (`docs/decisions/lockbox.md`; the script refuses a later panel).
The published scarcity indicator and its 0.12 band are unchanged, and none of these rows is added to the frozen shortlist of #567.
The three variants and every setting were declared in [`metadata/satiation_distance_598.json`](../../metadata/satiation_distance_598.json)
and the three judge candidates in `metadata/pressure_judge/candidates/`, all committed before the first forecast was fitted;
`scripts/satiation_distance_598.py` refuses an uncommitted declaration. The rolling level is #587's, its quantile, window and
minimum read from `metadata/satiation_587.json` and not re-tuned.

**These variants were built after seeing 2018-2025, including the 2025 onsets they are meant to warn. A pass here is not a
confirmation (ruling on #567). A variant can replace a shortlist slot only by Eleonora's decision, before the 2026 window opens.**

## What was declared

| variant | row | rule |
|---|---|---|
| (a) input | `risk_gbm+settle+h41+dist_roll` | the passer of #541 with `satiation_dist_roll` (the as-of reserves ratio minus the rolling level) as one extra input |
| (b) gated input | `risk_gbm+settle+h41+hinge_roll` | as (a) with `satiation_hinge_roll`, the percentage points below the level, 0 at or above it |
| (c) | `risk_gbm_base+settle+h41+hinge_roll` | as (b) on `risk_gbm_base` |

Both columns are built from the same as-of ratio and the same rolling level as `satiation_roll`; each is public at 16:00 on its own
row's date (source `satiation_distance_columns`, zero lag, off in every published declaration), and
`satiation.check_distance_no_future` rebuilds a row from the panel cut at it and refuses a value that differs. The passers' risk dates,
other features, estimators and timing are the parents' (`both` arm of #541).

## Result (weighted rule in force, +5 bp, h = 1 to 5)

| row | tier 1: onsets flagged / weighted false alarms per onset (limit 2) | tier 3 worst flags per 252 days, state 0 / 2021-23 | tier 5 | 2025 onsets warned | pass |
|---|---|---|---|---|---|
| `risk_gbm+settle+h41` (parent) | 14 of 26 / 1.44 | 0.7 / 0.3 | fails | 4 of 5 | no |
| (a) `+dist_roll` | 15 of 26 / 1.27 | 2.2 / 0.7 | fails | 5 of 5 | no |
| (b) `+hinge_roll` | 15 of 26 / 1.38 | 1.2 / 0.3 | fails | 5 of 5 | no |
| `risk_gbm_base+settle+h41` (parent) | 14 of 26 / 1.26 | 0.2 / 0.0 | fails | 4 of 5 | no |
| (c) `risk_gbm_base+settle+h41+hinge_roll` | 15 of 26 / 1.32 | 0.5 / 0.0 | fails | 5 of 5 | no |

- **No tier or pass verdict changes.** Tier 1 passes for every row, parent and variant; tiers 3 and 5 fail for every row.
- **One more onset is warned in each variant, and none is lost**: 2025-10-15 for (a) and (b), 2025-09-15 for (c). 2019 is unchanged
  (10 of 13). Recall difference against the parent, pooled: 0.038 [0.000, 0.111] on 26 onsets in each pairing, so the interval
  excludes nothing but zero at its edge.
- **Brier against the parent** at +5 bp: the differences are 0.000 to 0.002 at every horizon and every interval includes zero
  (the full tables, by regime and pressure-day type, are in the report).
- **2025 is still under-forecast.** Predicted against realised rate in 2025-26: parent 0.030 against 0.117; (a) 0.042; (b) 0.036;
  (c) 0.038 against a base of 0.031. The input moves the forecast toward the realised rate but does not close the gap, and the
  risk-date part leaves the ordinary days at zero.
- **Tier 3 fails for every row, parent included**, with 0 of 2 calibrated regimes tested at h = 1 (the judge's Table 1). Within
  that, (a) raises the worst flags per 252 days in state 0 from 0.7 to 2.2; the hinge (b) to 1.2.

## Not checked, or for Eleonora

- **Whether any variant replaces a shortlist slot** (#567) is her decision, before the 2026 window opens. Nothing here is a
  confirmation.
- The 26 onsets are 17 in 2018-19, 2 in 2020, 2 in 2024 and 5 in 2025: a difference of one onset is inside every interval.
- #571's pull request is not part of this measurement; the scarcity state the judge's tiers use is the one in force on main.

## Reproduce

Published panel `4ddc3882…` (`verify-panel` clean, unchanged); scratch panels `AUG` and `AUG2` as in
[`combined-model-result.md`](combined-model-result.md), `AUG2D` adds the two columns. `/opt/rmm-venv` (numpy 2.4.6, scikit-learn 1.9.1),
`OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`. The commands are the module docstring of
`scripts/satiation_distance_598.py`: `panel`, the benchmarks and parents for h = 1 to 5, `run`, the judge under both rules,
`compare` and `report`.

Evidence: [`evidence/satiation-distance/`](evidence/satiation-distance/) (`report.md`; `compare.json` and `compare.md`;
`judge-weighted.md` and `judge-unweighted.md`).
