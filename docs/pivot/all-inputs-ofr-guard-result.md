# The all-inputs candidates and the source screen with the OFR look-ahead removed (#522, of #508)

A measurement and a correction, beside `docs/pivot/all-inputs-result.md` (#479) and `docs/pivot/source-screen-result.md` (#478),
which stay as they were published and carry a dated note. It writes nothing into `docs/runs/`, changes no rule, moves no published
figure, and reads no day after 2025-12-31 (`docs/decisions/lockbox.md`; both scripts refuse a later panel). The inputs stay off in
every published declaration, and `metadata/all_inputs.json` and the candidate declarations are unchanged.

## What was wrong, and the guard

The OFR filled in its repo-segment history after it began publishing in real time on 2020-09-09. Two columns of the scratch panel
(`ofr_dvp_rate`, `ofr_dvp_minus_bgcr_bp_backfill`) held those later values on 566 of the 610 rows before that date, and both candidates and
the screen read them (finding #508). `ofr_dvp_minus_bgcr_bp`, `ofr_tri_rate` and `ofr_gcf_rate` were already empty before 2020-09-09.

* `repo_model.dvp_segment.require_ofr_public(rows)` raises `LookAheadError` for any value in an `ofr_*` column on a row dated before
  `OFR_REAL_TIME_START` (2020-09-09, `repo_model.ingest.OFR_STFM_REAL_TIME_START`, the date `metadata/sources_measurement.json` and
  `metadata/sources.json` record for the OFR's real-time publication). It covers every `ofr_*` column, so a column added later is covered too.
  `scripts/source_screen.py run` and `scripts/all_inputs.py run` call it, so the leaked panel of #478 and #479 is now refused.
* `dvp_segment.blank_ofr_before_real_time` blanks those columns; `scripts/source_screen.py panel` applies it when it merges the extra panels.
  Nothing else in the scratch panel changes: the blanked panel has sha256 `4de66765…` (the old one, `d1bb988f…`, rebuilds unchanged
  from the old script, which fixes the comparison below).
* Tests: `tests/test_dvp_segment.py` (`OfrRealTimeGuardTests`), `tests/test_source_screen.py` and `tests/test_all_inputs.py`, each with its
  recorded mutation in the docstring.

## Reproduce

Published panel `4ddc3882…` (`verify-panel` clean). Steps as in `docs/pivot/source-screen-result.md` (Reproduce) and `docs/pivot/all-inputs-result.md`;
the only change is that `source_screen.py panel` now blanks the pre-publication OFR values:

```
PYTHONPATH=src python3 scripts/source_screen.py panel --panel AUG6.csv --extra DVP.csv EW.csv --output SCREEN.csv
PYTHONPATH=src python3 scripts/source_screen.py run --panel SCREEN.csv --output OUT/screen.json
PYTHONPATH=src python3 scripts/source_screen.py report OUT/screen.json --tables OUT/screen_tables.md --heatmap OUT/heatmap.svg
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --output OUT/bench_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/risk_date_severity.py run --panel AUG2.csv --published PUBLISHED.csv --horizon $h --candidate risk_gbm --output OUT/risk_gbm_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/all_inputs.py run --panel SCREEN.csv --published PUBLISHED.csv --horizon $h --output OUT/ai_h$h.json
PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --output OUT/judge.json --markdown OUT/judge.md OUT/bench_h?.json OUT/risk_gbm_h?.json OUT/ai_h?.json
PYTHONPATH=src python3 scripts/pressure_judge.py table OUT/judge.json --output OUT/tables.md
PYTHONPATH=src python3 scripts/all_inputs.py compare --panel PUBLISHED.csv --output OUT/compare.json OUT/bench_h?.json OUT/risk_gbm_h?.json OUT/ai_h?.json > OUT/compare.md
```

Set `OMP_NUM_THREADS=1` when several fits share a machine. Evidence: `docs/pivot/evidence/all-inputs-ofr-guard/` (`judge.md`, `tables.md`,
`compare.md`, `compare.json`) and `docs/pivot/evidence/source-screen-ofr-guard/` (`screen.json`, `tables.md`).

**Determinism check.** The benchmarks and `risk_gbm` do not read an OFR column; their re-run reproduces `docs/pivot/evidence/all-inputs/compare.json`
in every cell outside the `all_inputs_*` rows. The old leaked panel, run again through the old script, reproduces #479's counts, recall by
year and episode table exactly; its paired Brier figures differ from the committed ones in the fourth decimal for the logistic candidate only, and its
logistic selection counts by one or two fits (the L1 solver), so differences of that size below are not read.

## Result: the 2019 gain does not come from the leak

Table 1. The judge's row at +5 bp (tiers 1, 3 and 5; 90% stationary-bootstrap intervals), as published in #479 and with the OFR blanked
before it was public.

| model | onsets flagged | recall [90%] | climatology recall, same false alarms | worst false alarms per onset (limit 2) | tier 3: calibrated regimes with pressure, h = 1 | tier 5 | pass |
|---|---|---|---|---|---|---|---|
| all_inputs_gbm, as published (#479) | 15 of 26 | 0.577 [0.381, 0.769] | 0.231 | 3.54 | 2 of 4 | yes | fail (tier 1 no, tier 3 no, tier 5 yes) |
| **all_inputs_gbm, OFR blanked** | 16 of 26 | 0.615 [0.423, 0.806] | 0.231 | 3.54 | 2 of 4 | yes | fail (tier 1 no, tier 3 no, tier 5 yes) |
| all_inputs_logistic, as published (#479) | 13 of 26 | 0.500 [0.333, 0.682] | 0.231 | 3.50 | 2 of 4 | yes | fail (tier 1 no, tier 3 no, tier 5 yes) |
| **all_inputs_logistic, OFR blanked** | 13 of 26 | 0.500 [0.333, 0.682] | 0.231 | 3.54 | 1 of 4 | yes | fail (tier 1 no, tier 3 no, tier 5 yes) |
| risk_gbm (unchanged) | 13 of 26 | 0.500 [0.310, 0.667] | 0.115 | 1.35 | 2 of 4 | no | fail (tier 1 yes, tier 3 no, tier 5 no) |

No verdict moves. Both candidates still fail tier 1 on the false-alarm limit (3.54 per onset against 2) and tier 3.

* **Paired against `risk_gbm`** (Brier score on the +5 bp outcome, h = 1, all days, positive favours the candidate; 90% interval):
  `all_inputs_logistic` -0.0097 [-0.0163, -0.0026] (published -0.0103), `all_inputs_gbm` -0.0075 [-0.0129, -0.0017] (published -0.0073): both worse,
  as published. Against persistence-logistic: -0.0111 [-0.0169, -0.0057] and -0.0089 [-0.0154, -0.0032] (published -0.0117, -0.0087). Against calendar
  climatology: +0.0040 [+0.0009, +0.0069] and +0.0061 [+0.0026, +0.0097] (published +0.0034, +0.0064). By regime and day type: Tables 2 and 3 of
  `tables.md` and Table 2 of `compare.md`.
* **Onsets flagged at some lead 1 to 5, paired against `risk_gbm`** (13 of 26): `all_inputs_logistic` 13 of 26, difference +0.000 [-0.088, +0.095];
  `all_inputs_gbm` 16 of 26, +0.115 [+0.000, +0.261] (published 15 of 26, +0.077 [-0.046, +0.211]). The gbm's interval now has a lower end of exactly zero.

Table 2. Onset recall by year, at some lead 1 to 5.

| year | onsets | risk_gbm | all_inputs_logistic | all_inputs_gbm, as published | all_inputs_gbm, OFR blanked |
|---|---|---|---|---|---|
| 2018 | 4 | 0/4 | 0/4 | 0/4 | 0/4 |
| **2019** | 13 | 10/13 | 11/13 | 13/13 | **13/13** |
| 2020 | 2 | 0/2 | 0/2 | 0/2 | 0/2 |
| 2024 | 2 | 0/2 | 0/2 | 0/2 | 0/2 |
| 2025 | 5 | 3/5 | 2/5 | 2/5 | 3/5 |

* **The three 2019 onsets are still newly warned.** `all_inputs_gbm` warns 2019-05-28, 2019-06-25 and 2019-08-13 with the OFR blanked, as it did with the leak,
  and `all_inputs_logistic` warns 2019-08-13 as before. The OFR columns are empty on every 2019 row in this run, so the 2019 gain does not come from them.
  What it does come from is not shown by this measurement.
* **What moved is in 2025.** `all_inputs_gbm` now warns 2025-10-15, which no model in the table warned (`risk_gbm` and the logistic do not), and one more
  ordinary-day onset overall (8 of 12 against 7 of 12; `risk_gbm` 4 of 12). It still loses 2025-09-30, which `risk_gbm` warns; `all_inputs_logistic`
  still loses 2025-12-26. The 2024, 2020 and 2018 episodes stay unwarned.
* **Each refit chose different settings** (Table 4 of `compare.md`): with 2019 inputs removed the penalty and depth choices shift, and a gbm refit
  with a different depth changes later onsets. One onset moves recall by about 0.04 and the year cells rest on 2 to 13, so the 2025 change is within
  what a changed input set can do by chance; it is not read as a gain.

## The source screen

The screen reads the OFR series with the guard on. Of the 77 series, two change; every other series' cells in `screen.json` are identical (the panel's hash is the one field that differs). Ranks around the two shift,
and nothing else.

Table 3. Spearman correlation with the +5 bp pressure indicator, pooled, by lead (days at lead 1).

| series | | lead 1 | lead 2 | lead 3 | lead 5 | lead 10 | days at lead 1 | rank |
|---|---|---|---|---|---|---|---|---|
| `ofr_dvp_minus_bgcr_bp_backfill` | published | +0.105 | +0.100 | +0.100 | +0.139 | +0.095 | 1778 | 26 |
| | **guard on** | +0.185 | +0.185 | +0.187 | +0.216 | +0.181 | 1246 | 17 |
| `ofr_dvp_rate` | published | +0.017 | +0.014 | +0.019 | +0.020 | +0.025 | 1778 | 70 |
| | **guard on** | -0.010 | -0.011 | -0.008 | -0.005 | +0.008 | 1246 | 74 |

With the pre-publication days removed, the backfilled column is the real-time column (`ofr_dvp_minus_bgcr_bp`, unchanged, 1246 days, +0.185 at
lead 1), so the two columns and their pre-onset and level rows are now identical, and the raw rate has no correlation with a pressure day
(AUC 0.54 before onsets). The DVP − BGCR spread is correlated with pressure days at +0.19 on the 1246 days it was public (2020-09-09 to 2025-12-31); the
earlier +0.105 pooled that with 532 pre-publication days. The statement in `source-screen-result.md` that every series is read as of the
decision instant now holds for these two columns. `ofr_tri_rate` and `ofr_gcf_rate` were not affected.

## Every other place the tree reads an OFR series

Searched with `git grep` over the whole tree (code, declarations, pages, tests and the evidence under `docs/pivot/evidence/`), and over the open branch
of #477 (PR #496).

| reader | OFR series | affected? |
|---|---|---|
| #479 all-inputs candidates (`metadata/all_inputs.json`, `all_inputs_*+recalibrated.json`) | all five | **yes**; re-scored above, page `all-inputs-result.md` noted |
| #478 source screen (`screen.json`) | all five | **yes**, the two columns in Table 3; `source-screen-result.md` noted |
| `ofr_dvp_minus_bgcr_bp` (`dvp_segment.build_columns`, #187) | DVP rate less BGCR | no: `None` before 2020-09-09 by construction (`tests/test_dvp_segment.py`) |
| `ofr_dvp_minus_bgcr_bp@backfill` sensitivities in `dvp_segment.SENSITIVITIES` | the same, backfilled | not a look-ahead in a result: it is labelled "sensitivity: pre-publication backfill, not admissible under the information-set rule", sits outside the win-rule family and chooses nothing; no merged page reports it (nothing in `docs/pivot/` or `docs/runs/` does) |
| `ofr_tri_rate`, `ofr_gcf_rate` (`measurement_fields.py`, #377) | tri-party and GCF | no: set to `None` before 2020-09-09 when the panel is built (`measurement_fields.py`), 0 values before it in the panel above |
| `onset_*_class_weight_funding+recalibrated` (`metadata/onset_classifier.json`, `onset-classifier-result.md`) | tri-party and GCF | no, for the same reason |
| the stacked ensemble (`docs/pivot/evidence/stacked-ensemble/pressure_judge_declaration_used.json`) | tri-party and GCF | no, for the same reason |
| #477, PR #496 (`unused_inputs`) | none read: `ofr_tri_rate` and `ofr_gcf_rate` are left out of its dealer group, and it adds no DVP column | no; nothing to change |
| open PRs #500 and #431, `docs/runs/` records, published declarations | none | no |

A branch for #477, #475 or #476 that carries a panel with the leaked columns is now refused by `all_inputs.py run` and `source_screen.py run`.
The guard is not wired into the other scoring scripts, which read no OFR column; one that does must call `dvp_segment.require_ofr_public`.

## What this does not say

* A re-score of two candidates on the same grid and declarations, with one change to the data. No other grid, estimator or input was tried.
* 26 onsets: one onset moves recall by about 0.04; the year cells rest on 2 to 13.
* Intervals are the judge's and the comparison's own, with no multiple-testing correction.
* The 2026 days, the +10 bp tiers and the confirmation window are not looked at.

## For Eleonora

No candidate passes, so there is no publishing question. Nothing here changes a rule or a published figure, and the pre-registered tests are untouched.
