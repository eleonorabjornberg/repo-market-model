# Before and after #662 for `ofr-followup-result.md` (#692)

Eleonora's instruction on #692: re-run the screen unchanged apart from the data, and tabulate, for the rows that read the Fed repo take-up
columns, the committed figure beside the re-run with intervals, and say whether any ranking or conclusion moved. No published figure is edited;
this directory is new.

**Rows that read `fed_repo_*`:** the five `*_dealer_ofr` candidates (dealer-and-segment group of #477, which carries the six `fed_repo_*`
fields, plus the tri-party rate and its not-yet-published flag). The five passers, the minmax-scaled skew-t control and the three benchmarks do
not.

## Answer

* **This page reproduces exactly with the old data.** Committed -> old data under today's code: every paired difference, interval and onset
  count is identical (largest change 0.0000). So for this page the committed figures are comparable with the re-run, and every change below is
  #662's.
* **Verdicts: nothing moved from the data.** No candidate passes, before or after. (Tier cells of some verdicts differ between the committed
  tables and today's judge, for the same rows with the old data; that is the judge, see below.)
* **Ranking: it moved.** Ordered by the paired Brier difference averaged over h = 1 to 5, `risk_quantile_skewt_base_dealer_ofr` goes from
  4th to 2nd and its average changes sign (+0.0022 to -0.0001); `risk_gbm_dealer_ofr` goes 2nd to 4th and `risk_logistic_base_dealer_ofr` 3rd
  to 5th; `risk_gbm_base_dealer_ofr` stays first and `risk_logistic_dealer_ofr` last. The differences are small and most intervals include zero.
* **Paired Brier differences.** The largest change is 0.0074, for the skew-t candidate at h = 4 (+0.0055 *, now -0.0020 [-0.0050, +0.0009]).
  Four dealer cells change whether the interval excludes zero, all from "worse, excludes zero" to "includes zero": `risk_logistic_base_dealer_ofr`
  h = 1, `risk_logistic_dealer_ofr` h = 1, `risk_quantile_skewt_base_dealer_ofr` h = 2 and h = 4.
* **Conclusions of the page that moved.**
  1. "The missed years stay missed ... the five onsets of 2018 and the two of 2020 are in every denominator, and not one of the eleven models
     flags any of them; 2024 stays 0 of 2" no longer holds: `risk_logistic_base_dealer_ofr` flags 3 of the 5 onsets of 2018 (its total 15 to 18
     of 27, recall 0.577 to 0.692 [0.517, 0.844]) and `risk_quantile_skewt_base_dealer_ofr` flags 1 of the 2 onsets of 2024 (15 to 16 of 27).
     2020 stays 0 of 2 for every model.
  2. "Where an interval excludes zero it is mostly on the worse side: the two logistic forms at h = 1 to 2 ... and the skew-t form at h = 2 and
     4" becomes: the logistic forms at h = 2 (base form) and h = 2 to 5 (the other); at h = 1 the intervals now include zero; the skew-t
     form has no interval that excludes zero. The direction (no consistent gain from the added inputs) is unchanged.
  3. "The scaling alone changes nothing" still holds: `risk_quantile_skewt_base_minmax` equals `risk_quantile_skewt_base` in every onset cell and
     its paired rows are unchanged.
  4. The page's 2025 sentence (four of five candidates flag one or two more onsets than their passers) is unchanged: 5 of 5 for the gbm base,
     logistic and logistic base candidates and the skew-t candidate (the 2025 cells did not move).

## How this was produced

* **Panel.** Published panel `4ddc3882cd6d406b11e1088f8ff6195e16dde175a0ad6818abe40dd5bdac8999`, rebuilt from the tracked fixtures and checked with
  `verify-panel` (clean). Scratch panels are built by the chain on the result page's "Reproduce" section, on `main` at the commit this branch
  starts from. Development data only: scored days 2018-06-29 to 2025-12-31; no 2026 day is read (`docs/decisions/lockbox.md`);
  `repo_term_outstanding` stays off `FEATURE_FIELDS`; no declaration changed.
* **Re-run = "new data".** Every command of the page's "Reproduce" section, unchanged, on today's `main` (which carries #662). The files next to
  this one (`judge.md`, `tables.md`, `paired.md`, `paired.json`) are that run's output.
* **Control = "old data".** The same commands, same judge, same scripts, on a scratch copy of `main` in which only the three files #662 changed
  (`src/repo_model/fed_liquidity.py`, `src/repo_model/ingest.py`, `metadata/sources_measurement.json`) are put back to their state before
  #662 (parent `7b8fd686` of merge `0db0471d`). Its outputs are in `old-data-control/`. The two scratch panels differ in `fed_repo_*` columns
  only, on the 339 rows 2018-05-09 to 2019-09-16 (checked cell by cell), and nowhere else. This isolates the data change: **old data -> new data
  differs by #662 alone.**
* **Committed = "committed".** The figures in the existing evidence directory, written when the page was published. The judge, the net
  settlement columns and other code on `main` have changed since for reasons unrelated to #662, so "committed -> new data" mixes the data change
  with those; "committed -> old data" is that other drift alone (section "Drift on `main` that is not #662"). Where the two differ, trust the
  old-data -> new-data comparison for what #662 did.
* Intervals are the pages' own: 90% stationary-bootstrap, as `scripts/unused_inputs.py report` and the judge compute them. `*` marks an interval
  that excludes zero.

## 1. Data change alone: old data -> new data (same code, same judge)

### A. Paired Brier difference at +5 bp, candidate minus its passer, all scored days (old data / new data)

Negative favours the candidate; 90% stationary-bootstrap interval; * = interval excludes zero. Rows of candidates that read `fed_repo_*` are all shown; rows of candidates that do not are summarised below the table.

| candidate (reads `fed_repo_*`) | h | old data | new data | change | excludes-zero verdict moved |
|---|---|---|---|---|---|
| risk_gbm_base_dealer_ofr | 1 | +0.0003 [-0.0016, +0.0023] | -0.0005 [-0.0020, +0.0009] | -0.0008 | no |
| risk_gbm_base_dealer_ofr | 2 | -0.0006 [-0.0018, +0.0004] | -0.0009 [-0.0021, +0.0000] | -0.0003 | no |
| risk_gbm_base_dealer_ofr | 3 | -0.0016 [-0.0031, -0.0001] * | -0.0022 [-0.0041, -0.0005] * | -0.0006 | no |
| risk_gbm_base_dealer_ofr | 4 | +0.0009 [+0.0003, +0.0017] * | +0.0010 [+0.0001, +0.0021] * | +0.0001 | no |
| risk_gbm_base_dealer_ofr | 5 | -0.0010 [-0.0026, +0.0000] | -0.0006 [-0.0022, +0.0006] | +0.0004 | no |
| risk_gbm_dealer_ofr | 1 | +0.0006 [-0.0008, +0.0021] | +0.0006 [-0.0004, +0.0017] | -0.0000 | no |
| risk_gbm_dealer_ofr | 2 | -0.0007 [-0.0018, +0.0001] | -0.0005 [-0.0014, +0.0002] | +0.0002 | no |
| risk_gbm_dealer_ofr | 3 | +0.0003 [-0.0001, +0.0009] | -0.0000 [-0.0004, +0.0004] | -0.0004 | no |
| risk_gbm_dealer_ofr | 4 | +0.0003 [-0.0001, +0.0008] | +0.0005 [-0.0002, +0.0012] | +0.0001 | no |
| risk_gbm_dealer_ofr | 5 | -0.0002 [-0.0007, +0.0003] | -0.0004 [-0.0010, +0.0001] | -0.0002 | no |
| risk_logistic_base_dealer_ofr | 1 | +0.0027 [+0.0001, +0.0055] * | +0.0020 [-0.0003, +0.0046] | -0.0007 | **yes** |
| risk_logistic_base_dealer_ofr | 2 | +0.0028 [+0.0008, +0.0051] * | +0.0020 [+0.0002, +0.0039] * | -0.0008 | no |
| risk_logistic_base_dealer_ofr | 3 | +0.0008 [-0.0003, +0.0020] | +0.0007 [-0.0003, +0.0019] | -0.0001 | no |
| risk_logistic_base_dealer_ofr | 4 | +0.0012 [-0.0005, +0.0030] | +0.0010 [-0.0005, +0.0027] | -0.0002 | no |
| risk_logistic_base_dealer_ofr | 5 | +0.0012 [-0.0004, +0.0031] | +0.0005 [-0.0005, +0.0018] | -0.0006 | no |
| risk_logistic_dealer_ofr | 1 | +0.0034 [+0.0003, +0.0069] * | +0.0027 [-0.0001, +0.0058] | -0.0007 | **yes** |
| risk_logistic_dealer_ofr | 2 | +0.0032 [+0.0007, +0.0061] * | +0.0028 [+0.0003, +0.0055] * | -0.0004 | no |
| risk_logistic_dealer_ofr | 3 | +0.0011 [+0.0001, +0.0022] * | +0.0014 [+0.0004, +0.0027] * | +0.0003 | no |
| risk_logistic_dealer_ofr | 4 | +0.0018 [+0.0003, +0.0036] * | +0.0020 [+0.0004, +0.0039] * | +0.0002 | no |
| risk_logistic_dealer_ofr | 5 | +0.0020 [+0.0004, +0.0038] * | +0.0011 [+0.0000, +0.0024] * | -0.0009 | no |
| risk_quantile_skewt_base_dealer_ofr | 1 | +0.0004 [-0.0026, +0.0033] | -0.0020 [-0.0053, +0.0008] | -0.0024 | no |
| risk_quantile_skewt_base_dealer_ofr | 2 | +0.0031 [+0.0000, +0.0064] * | +0.0010 [-0.0013, +0.0036] | -0.0021 | **yes** |
| risk_quantile_skewt_base_dealer_ofr | 3 | +0.0014 [-0.0025, +0.0062] | +0.0007 [-0.0032, +0.0055] | -0.0007 | no |
| risk_quantile_skewt_base_dealer_ofr | 4 | +0.0055 [+0.0007, +0.0111] * | -0.0020 [-0.0050, +0.0009] | -0.0074 | **yes** |
| risk_quantile_skewt_base_dealer_ofr | 5 | +0.0008 [-0.0028, +0.0044] | +0.0019 [-0.0008, +0.0050] | +0.0011 | no |
| risk_quantile_skewt_base_dealer_ofr vs risk_quantile_skewt_base_minmax | 1 | +0.0004 [-0.0026, +0.0033] | -0.0020 [-0.0053, +0.0008] | -0.0024 | no |
| risk_quantile_skewt_base_dealer_ofr vs risk_quantile_skewt_base_minmax | 2 | +0.0031 [+0.0000, +0.0064] * | +0.0010 [-0.0013, +0.0036] | -0.0021 | **yes** |
| risk_quantile_skewt_base_dealer_ofr vs risk_quantile_skewt_base_minmax | 3 | +0.0013 [-0.0025, +0.0062] | +0.0007 [-0.0032, +0.0055] | -0.0007 | no |
| risk_quantile_skewt_base_dealer_ofr vs risk_quantile_skewt_base_minmax | 4 | +0.0055 [+0.0007, +0.0111] * | -0.0020 [-0.0050, +0.0009] | -0.0074 | **yes** |
| risk_quantile_skewt_base_dealer_ofr vs risk_quantile_skewt_base_minmax | 5 | +0.0008 [-0.0027, +0.0044] | +0.0020 [-0.0007, +0.0051] | +0.0011 | no |

* Largest absolute change in a paired difference: reading candidates 0.0074; non-reading candidates 0.0000.
* Reading candidates whose excludes-zero verdict moved: risk_logistic_base_dealer_ofr h=1, risk_logistic_dealer_ofr h=1, risk_quantile_skewt_base_dealer_ofr h=2, risk_quantile_skewt_base_dealer_ofr h=4, risk_quantile_skewt_base_dealer_ofr vs risk_quantile_skewt_base_minmax h=2, risk_quantile_skewt_base_dealer_ofr vs risk_quantile_skewt_base_minmax h=4.
* Non-reading candidates whose excludes-zero verdict moved: none.

### B. Ranking of the candidates by the paired Brier difference averaged over h = 1 to 5 (best first)

| rank | old data | new data |
|---|---|---|
| 1 | risk_gbm_base_dealer_ofr (-0.0004) | risk_gbm_base_dealer_ofr (-0.0006) |
| 2 | risk_gbm_dealer_ofr (+0.0001) | risk_quantile_skewt_base_dealer_ofr (-0.0001) |
| 3 | risk_logistic_base_dealer_ofr (+0.0017) | risk_quantile_skewt_base_dealer_ofr vs risk_quantile_skewt_base_minmax (-0.0001) |
| 4 | risk_quantile_skewt_base_dealer_ofr (+0.0022) | risk_gbm_dealer_ofr (+0.0000) |
| 5 | risk_quantile_skewt_base_dealer_ofr vs risk_quantile_skewt_base_minmax (+0.0022) | risk_logistic_base_dealer_ofr (+0.0012) |
| 6 | risk_logistic_dealer_ofr (+0.0023) | risk_logistic_dealer_ofr (+0.0020) |

* Order identical: no. Positions that changed: risk_gbm_dealer_ofr 2->4, risk_logistic_base_dealer_ofr 3->5, risk_quantile_skewt_base_dealer_ofr 4->2, risk_quantile_skewt_base_dealer_ofr vs risk_quantile_skewt_base_minmax 5->3.
* Sign of the average difference identical for every candidate: no.

### C. +5 bp onsets flagged / onsets at some lead 1 to 5, by year (old data -> new data)

| model | reads | 2018 | 2019 | 2020 | 2024 | 2025 | all |
|---|---|---|---|---|---|---|---|
| risk_gbm | - | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_gbm_base | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_gbm_base_dealer_ofr | R | 0/5 | 10/13 | 0/2 | 0/2 | 5/5 | 15/27 |
| risk_gbm_dealer_ofr | R | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_logistic | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_logistic_base | - | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_logistic_base_dealer_ofr | R | 0/5 -> **3/5** | 10/13 | 0/2 | 0/2 | 5/5 | 15/27 -> **18/27** |
| risk_logistic_dealer_ofr | R | 0/5 | 10/13 | 0/2 | 0/2 | 5/5 | 15/27 |
| risk_quantile_skewt_base | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_quantile_skewt_base_dealer_ofr | R | 0/5 | 10/13 | 0/2 | 0/2 -> **1/2** | 5/5 | 15/27 -> **16/27** |
| risk_quantile_skewt_base_minmax | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |

* Cells that moved: risk_logistic_base_dealer_ofr 2018, risk_quantile_skewt_base_dealer_ofr 2024.

### D. Judge row at +5 bp (tiers 1, 3, 5) and AUROC per horizon (old data -> new data)

AUROC is the judge's point value for the +5 bp probability at each horizon (the judge gives it no interval; the interval-carrying comparison is A). The pass verdict is the judge's: tiers 1 / 3 / 5.

| model | reads | onsets flagged | recall [90%] | false alarms per onset | verdict (tiers 1 / 3 / 5) | AUROC h=1..5 |
|---|---|---|---|---|---|---|
| calendar_climatology | - | 12 of 26 | 0.462 [0.286, 0.667] | 6.85 flat / 3.90 weighted | fail (tiers no / no / no) | 0.586 / 0.586 / 0.585 / 0.580 / 0.578 |
| persistence_logistic | - | 12 of 26 | 0.462 [0.273, 0.650] | 8.46 flat / 4.09 weighted | fail (tiers no / no / no) | 0.876 / 0.817 / 0.765 / 0.788 / 0.772 |
| published_v1 | - | 14 of 26 | 0.538 [0.350, 0.720] | 7.38 flat / 3.06 weighted | fail (tiers no / yes / no) | 0.898 / 0.881 / 0.887 / 0.871 / 0.876 |
| risk_gbm | - | 13 of 26 | 0.500 [0.310, 0.667] | 2.12 flat / 1.48 weighted | fail (tiers yes / no / no) | 0.642 / 0.578 / 0.579 / 0.579 / 0.577 |
| risk_gbm_base | - | 14 of 26 | 0.538 [0.360, 0.719] | 2.19 flat / 1.59 weighted | fail (tiers yes / no / no) | 0.643 / 0.578 / 0.579 / 0.579 / 0.576 |
| risk_gbm_base_dealer_ofr | R | 15 of 26 | 0.577 [0.391, 0.760] | 2.23 flat / 1.58 weighted -> **2.08 flat / 1.42 weighted** | fail (tiers yes / no / no) | 0.642 / 0.578 / 0.580 / 0.579 / 0.576 |
| risk_gbm_dealer_ofr | R | 13 of 26 | 0.500 [0.321, 0.678] | 2.19 flat / 1.51 weighted -> **2.04 flat / 1.41 weighted** | fail (tiers yes / no / no) | 0.642 -> **0.643** / 0.578 / 0.579 / 0.579 / 0.577 -> **0.578** |
| risk_logistic | - | 16 of 26 | 0.615 [0.435, 0.800] | 3.31 flat / 2.55 weighted | fail (tiers no / no / no) | 0.642 / 0.579 / 0.579 / 0.578 / 0.577 |
| risk_logistic_base | - | 15 of 26 | 0.577 [0.391, 0.762] | 2.88 flat / 2.18 weighted | fail (tiers no / no / no) | 0.643 / 0.579 / 0.579 / 0.578 / 0.577 |
| risk_logistic_base_dealer_ofr | R | 15 of 26 -> **18 of 26** | 0.577 [0.394, 0.750] -> **0.692 [0.517, 0.844]** | 3.35 flat / 2.62 weighted -> **3.27 flat / 2.54 weighted** | fail (tiers no / no / no) | 0.643 / 0.578 / 0.579 / 0.578 -> **0.579** / 0.578 |
| risk_logistic_dealer_ofr | R | 16 of 26 | 0.615 [0.429, 0.800] | 3.81 flat / 3.05 weighted -> **3.58 flat / 2.82 weighted** | fail (tiers no / no / no) | 0.642 / 0.577 -> **0.578** / 0.578 -> **0.579** / 0.578 / 0.577 |
| risk_quantile_skewt_base | - | 15 of 26 | 0.577 [0.391, 0.750] | 2.88 flat / 2.14 weighted | fail (tiers no / no / no) | 0.635 / 0.582 / 0.585 / 0.586 / 0.585 |
| risk_quantile_skewt_base_dealer_ofr | R | 15 of 26 -> **16 of 26** | 0.577 [0.400, 0.750] -> **0.615 [0.429, 0.789]** | 4.19 flat / 3.45 weighted | fail (tiers no / no / no) | 0.648 -> **0.644** / 0.580 / 0.585 / 0.580 -> **0.582** / 0.588 -> **0.586** |
| risk_quantile_skewt_base_minmax | - | 15 of 26 | 0.577 [0.400, 0.759] | 2.88 flat / 2.14 weighted | fail (tiers no / no / no) | 0.636 / 0.582 / 0.585 / 0.586 / 0.585 |

* Overall pass/fail moved for: none (all fail in both).
* Any tier cell of the verdict moved for: none.


## 2. Committed -> re-run (the directive's before/after)

### A. Paired Brier difference at +5 bp, candidate minus its passer, all scored days (committed / re-run)

Negative favours the candidate; 90% stationary-bootstrap interval; * = interval excludes zero. Rows of candidates that read `fed_repo_*` are all shown; rows of candidates that do not are summarised below the table.

| candidate (reads `fed_repo_*`) | h | committed | re-run | change | excludes-zero verdict moved |
|---|---|---|---|---|---|
| risk_gbm_base_dealer_ofr | 1 | +0.0003 [-0.0016, +0.0023] | -0.0005 [-0.0020, +0.0009] | -0.0008 | no |
| risk_gbm_base_dealer_ofr | 2 | -0.0006 [-0.0018, +0.0004] | -0.0009 [-0.0021, +0.0000] | -0.0003 | no |
| risk_gbm_base_dealer_ofr | 3 | -0.0016 [-0.0031, -0.0001] * | -0.0022 [-0.0041, -0.0005] * | -0.0006 | no |
| risk_gbm_base_dealer_ofr | 4 | +0.0009 [+0.0003, +0.0017] * | +0.0010 [+0.0001, +0.0021] * | +0.0001 | no |
| risk_gbm_base_dealer_ofr | 5 | -0.0010 [-0.0026, +0.0000] | -0.0006 [-0.0022, +0.0006] | +0.0004 | no |
| risk_gbm_dealer_ofr | 1 | +0.0006 [-0.0008, +0.0021] | +0.0006 [-0.0004, +0.0017] | -0.0000 | no |
| risk_gbm_dealer_ofr | 2 | -0.0007 [-0.0018, +0.0001] | -0.0005 [-0.0014, +0.0002] | +0.0002 | no |
| risk_gbm_dealer_ofr | 3 | +0.0003 [-0.0001, +0.0009] | -0.0000 [-0.0004, +0.0004] | -0.0004 | no |
| risk_gbm_dealer_ofr | 4 | +0.0003 [-0.0001, +0.0008] | +0.0005 [-0.0002, +0.0012] | +0.0001 | no |
| risk_gbm_dealer_ofr | 5 | -0.0002 [-0.0007, +0.0003] | -0.0004 [-0.0010, +0.0001] | -0.0002 | no |
| risk_logistic_base_dealer_ofr | 1 | +0.0027 [+0.0001, +0.0055] * | +0.0020 [-0.0003, +0.0046] | -0.0007 | **yes** |
| risk_logistic_base_dealer_ofr | 2 | +0.0028 [+0.0008, +0.0051] * | +0.0020 [+0.0002, +0.0039] * | -0.0008 | no |
| risk_logistic_base_dealer_ofr | 3 | +0.0008 [-0.0003, +0.0020] | +0.0007 [-0.0003, +0.0019] | -0.0001 | no |
| risk_logistic_base_dealer_ofr | 4 | +0.0012 [-0.0005, +0.0030] | +0.0010 [-0.0005, +0.0027] | -0.0002 | no |
| risk_logistic_base_dealer_ofr | 5 | +0.0012 [-0.0004, +0.0031] | +0.0005 [-0.0005, +0.0018] | -0.0006 | no |
| risk_logistic_dealer_ofr | 1 | +0.0034 [+0.0003, +0.0069] * | +0.0027 [-0.0001, +0.0058] | -0.0007 | **yes** |
| risk_logistic_dealer_ofr | 2 | +0.0032 [+0.0007, +0.0061] * | +0.0028 [+0.0003, +0.0055] * | -0.0004 | no |
| risk_logistic_dealer_ofr | 3 | +0.0011 [+0.0001, +0.0022] * | +0.0014 [+0.0004, +0.0027] * | +0.0003 | no |
| risk_logistic_dealer_ofr | 4 | +0.0018 [+0.0003, +0.0036] * | +0.0020 [+0.0004, +0.0039] * | +0.0002 | no |
| risk_logistic_dealer_ofr | 5 | +0.0020 [+0.0004, +0.0038] * | +0.0011 [+0.0000, +0.0024] * | -0.0009 | no |
| risk_quantile_skewt_base_dealer_ofr | 1 | +0.0004 [-0.0026, +0.0033] | -0.0020 [-0.0053, +0.0008] | -0.0024 | no |
| risk_quantile_skewt_base_dealer_ofr | 2 | +0.0031 [+0.0000, +0.0064] * | +0.0010 [-0.0013, +0.0036] | -0.0021 | **yes** |
| risk_quantile_skewt_base_dealer_ofr | 3 | +0.0014 [-0.0025, +0.0062] | +0.0007 [-0.0032, +0.0055] | -0.0007 | no |
| risk_quantile_skewt_base_dealer_ofr | 4 | +0.0055 [+0.0007, +0.0111] * | -0.0020 [-0.0050, +0.0009] | -0.0074 | **yes** |
| risk_quantile_skewt_base_dealer_ofr | 5 | +0.0008 [-0.0028, +0.0044] | +0.0019 [-0.0008, +0.0050] | +0.0011 | no |
| risk_quantile_skewt_base_dealer_ofr vs risk_quantile_skewt_base_minmax | 1 | +0.0004 [-0.0026, +0.0033] | -0.0020 [-0.0053, +0.0008] | -0.0024 | no |
| risk_quantile_skewt_base_dealer_ofr vs risk_quantile_skewt_base_minmax | 2 | +0.0031 [+0.0000, +0.0064] * | +0.0010 [-0.0013, +0.0036] | -0.0021 | **yes** |
| risk_quantile_skewt_base_dealer_ofr vs risk_quantile_skewt_base_minmax | 3 | +0.0013 [-0.0025, +0.0062] | +0.0007 [-0.0032, +0.0055] | -0.0007 | no |
| risk_quantile_skewt_base_dealer_ofr vs risk_quantile_skewt_base_minmax | 4 | +0.0055 [+0.0007, +0.0111] * | -0.0020 [-0.0050, +0.0009] | -0.0074 | **yes** |
| risk_quantile_skewt_base_dealer_ofr vs risk_quantile_skewt_base_minmax | 5 | +0.0008 [-0.0027, +0.0044] | +0.0020 [-0.0007, +0.0051] | +0.0011 | no |

* Largest absolute change in a paired difference: reading candidates 0.0074; non-reading candidates 0.0000.
* Reading candidates whose excludes-zero verdict moved: risk_logistic_base_dealer_ofr h=1, risk_logistic_dealer_ofr h=1, risk_quantile_skewt_base_dealer_ofr h=2, risk_quantile_skewt_base_dealer_ofr h=4, risk_quantile_skewt_base_dealer_ofr vs risk_quantile_skewt_base_minmax h=2, risk_quantile_skewt_base_dealer_ofr vs risk_quantile_skewt_base_minmax h=4.
* Non-reading candidates whose excludes-zero verdict moved: none.

### B. Ranking of the candidates by the paired Brier difference averaged over h = 1 to 5 (best first)

| rank | committed | re-run |
|---|---|---|
| 1 | risk_gbm_base_dealer_ofr (-0.0004) | risk_gbm_base_dealer_ofr (-0.0006) |
| 2 | risk_gbm_dealer_ofr (+0.0001) | risk_quantile_skewt_base_dealer_ofr (-0.0001) |
| 3 | risk_logistic_base_dealer_ofr (+0.0017) | risk_quantile_skewt_base_dealer_ofr vs risk_quantile_skewt_base_minmax (-0.0001) |
| 4 | risk_quantile_skewt_base_dealer_ofr (+0.0022) | risk_gbm_dealer_ofr (+0.0000) |
| 5 | risk_quantile_skewt_base_dealer_ofr vs risk_quantile_skewt_base_minmax (+0.0022) | risk_logistic_base_dealer_ofr (+0.0012) |
| 6 | risk_logistic_dealer_ofr (+0.0023) | risk_logistic_dealer_ofr (+0.0020) |

* Order identical: no. Positions that changed: risk_gbm_dealer_ofr 2->4, risk_logistic_base_dealer_ofr 3->5, risk_quantile_skewt_base_dealer_ofr 4->2, risk_quantile_skewt_base_dealer_ofr vs risk_quantile_skewt_base_minmax 5->3.
* Sign of the average difference identical for every candidate: no.

### C. +5 bp onsets flagged / onsets at some lead 1 to 5, by year (committed -> re-run)

| model | reads | 2018 | 2019 | 2020 | 2024 | 2025 | all |
|---|---|---|---|---|---|---|---|
| risk_gbm | - | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_gbm_base | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_gbm_base_dealer_ofr | R | 0/5 | 10/13 | 0/2 | 0/2 | 5/5 | 15/27 |
| risk_gbm_dealer_ofr | R | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_logistic | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_logistic_base | - | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_logistic_base_dealer_ofr | R | 0/5 -> **3/5** | 10/13 | 0/2 | 0/2 | 5/5 | 15/27 -> **18/27** |
| risk_logistic_dealer_ofr | R | 0/5 | 10/13 | 0/2 | 0/2 | 5/5 | 15/27 |
| risk_quantile_skewt_base | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_quantile_skewt_base_dealer_ofr | R | 0/5 | 10/13 | 0/2 | 0/2 -> **1/2** | 5/5 | 15/27 -> **16/27** |
| risk_quantile_skewt_base_minmax | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |

* Cells that moved: risk_logistic_base_dealer_ofr 2018, risk_quantile_skewt_base_dealer_ofr 2024.

### D. Judge row at +5 bp (tiers 1, 3, 5) and AUROC per horizon (committed -> re-run)

AUROC is the judge's point value for the +5 bp probability at each horizon (the judge gives it no interval; the interval-carrying comparison is A). The pass verdict is the judge's: tiers 1 / 3 / 5.

| model | reads | onsets flagged | recall [90%] | false alarms per onset | verdict (tiers 1 / 3 / 5) | AUROC h=1..5 |
|---|---|---|---|---|---|---|
| calendar_climatology | - | 12 of 26 | 0.462 [0.286, 0.667] | 6.69 -> **6.85 flat / 3.90 weighted** | fail (tiers no / no / no) | 0.586 / 0.586 / 0.585 / 0.580 / 0.578 |
| persistence_logistic | - | 12 of 26 | 0.462 [0.273, 0.650] | 7.04 -> **8.46 flat / 4.09 weighted** | fail (tiers no / no / no) | 0.876 / 0.817 / 0.765 / 0.788 / 0.772 |
| published_v1 | - | 14 of 26 | 0.538 [0.350, 0.720] | 5.73 -> **7.38 flat / 3.06 weighted** | fail (tiers no / no / no) -> **fail (tiers no / yes / no)** | 0.898 / 0.881 / 0.887 / 0.871 / 0.876 |
| risk_gbm | - | 13 of 26 | 0.500 [0.310, 0.667] | 1.38 -> **2.12 flat / 1.48 weighted** | fail (tiers yes / no / no) | 0.642 / 0.578 / 0.579 / 0.579 / 0.577 |
| risk_gbm_base | - | 14 of 26 | 0.538 [0.360, 0.719] | 1.50 -> **2.19 flat / 1.59 weighted** | fail (tiers yes / no / no) | 0.643 / 0.578 / 0.579 / 0.579 / 0.576 |
| risk_gbm_base_dealer_ofr | R | 15 of 26 | 0.577 [0.391, 0.760] | 1.27 -> **2.08 flat / 1.42 weighted** | fail (tiers yes / no / no) | 0.642 / 0.578 / 0.580 / 0.579 / 0.576 |
| risk_gbm_dealer_ofr | R | 13 of 26 | 0.500 [0.321, 0.678] | 1.35 -> **2.04 flat / 1.41 weighted** | fail (tiers yes / no / no) | 0.642 -> **0.643** / 0.578 / 0.579 / 0.579 / 0.577 -> **0.578** |
| risk_logistic | - | 16 of 26 | 0.615 [0.435, 0.800] | 2.42 -> **3.31 flat / 2.55 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.642 / 0.579 / 0.579 / 0.578 / 0.577 |
| risk_logistic_base | - | 15 of 26 | 0.577 [0.391, 0.762] | 2.31 -> **2.88 flat / 2.18 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.643 / 0.579 / 0.579 / 0.578 / 0.577 |
| risk_logistic_base_dealer_ofr | R | 15 of 26 -> **18 of 26** | 0.577 [0.394, 0.750] -> **0.692 [0.517, 0.844]** | 2.31 -> **3.27 flat / 2.54 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.643 / 0.578 / 0.579 / 0.578 -> **0.579** / 0.578 |
| risk_logistic_dealer_ofr | R | 16 of 26 | 0.615 [0.429, 0.800] | 2.62 -> **3.58 flat / 2.82 weighted** | fail (tiers no / no / no) | 0.642 / 0.577 -> **0.578** / 0.578 -> **0.579** / 0.578 / 0.577 |
| risk_quantile_skewt_base | - | 15 of 26 | 0.577 [0.391, 0.750] | 2.31 -> **2.88 flat / 2.14 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.635 / 0.582 / 0.585 / 0.586 / 0.585 |
| risk_quantile_skewt_base_dealer_ofr | R | 15 of 26 -> **16 of 26** | 0.577 [0.400, 0.750] -> **0.615 [0.429, 0.789]** | 2.69 -> **4.19 flat / 3.45 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.648 -> **0.644** / 0.580 / 0.585 / 0.580 -> **0.582** / 0.588 -> **0.586** |
| risk_quantile_skewt_base_minmax | - | 15 of 26 | 0.577 [0.400, 0.759] | 2.31 -> **2.88 flat / 2.14 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.636 / 0.582 / 0.585 / 0.586 / 0.585 |

* Overall pass/fail moved for: none (all fail in both).
* Any tier cell of the verdict moved for: published_v1, risk_logistic, risk_logistic_base, risk_logistic_base_dealer_ofr, risk_quantile_skewt_base, risk_quantile_skewt_base_dealer_ofr, risk_quantile_skewt_base_minmax.


## 3. Drift on `main` that is not #662: committed -> old data under today's code

### A. Paired Brier difference at +5 bp, candidate minus its passer, all scored days (committed / old data, today's code)

Negative favours the candidate; 90% stationary-bootstrap interval; * = interval excludes zero. Rows of candidates that read `fed_repo_*` are all shown; rows of candidates that do not are summarised below the table.

| candidate (reads `fed_repo_*`) | h | committed | old data, today's code | change | excludes-zero verdict moved |
|---|---|---|---|---|---|
| risk_gbm_base_dealer_ofr | 1 | +0.0003 [-0.0016, +0.0023] | +0.0003 [-0.0016, +0.0023] | +0.0000 | no |
| risk_gbm_base_dealer_ofr | 2 | -0.0006 [-0.0018, +0.0004] | -0.0006 [-0.0018, +0.0004] | +0.0000 | no |
| risk_gbm_base_dealer_ofr | 3 | -0.0016 [-0.0031, -0.0001] * | -0.0016 [-0.0031, -0.0001] * | +0.0000 | no |
| risk_gbm_base_dealer_ofr | 4 | +0.0009 [+0.0003, +0.0017] * | +0.0009 [+0.0003, +0.0017] * | +0.0000 | no |
| risk_gbm_base_dealer_ofr | 5 | -0.0010 [-0.0026, +0.0000] | -0.0010 [-0.0026, +0.0000] | +0.0000 | no |
| risk_gbm_dealer_ofr | 1 | +0.0006 [-0.0008, +0.0021] | +0.0006 [-0.0008, +0.0021] | +0.0000 | no |
| risk_gbm_dealer_ofr | 2 | -0.0007 [-0.0018, +0.0001] | -0.0007 [-0.0018, +0.0001] | +0.0000 | no |
| risk_gbm_dealer_ofr | 3 | +0.0003 [-0.0001, +0.0009] | +0.0003 [-0.0001, +0.0009] | +0.0000 | no |
| risk_gbm_dealer_ofr | 4 | +0.0003 [-0.0001, +0.0008] | +0.0003 [-0.0001, +0.0008] | +0.0000 | no |
| risk_gbm_dealer_ofr | 5 | -0.0002 [-0.0007, +0.0003] | -0.0002 [-0.0007, +0.0003] | +0.0000 | no |
| risk_logistic_base_dealer_ofr | 1 | +0.0027 [+0.0001, +0.0055] * | +0.0027 [+0.0001, +0.0055] * | +0.0000 | no |
| risk_logistic_base_dealer_ofr | 2 | +0.0028 [+0.0008, +0.0051] * | +0.0028 [+0.0008, +0.0051] * | +0.0000 | no |
| risk_logistic_base_dealer_ofr | 3 | +0.0008 [-0.0003, +0.0020] | +0.0008 [-0.0003, +0.0020] | +0.0000 | no |
| risk_logistic_base_dealer_ofr | 4 | +0.0012 [-0.0005, +0.0030] | +0.0012 [-0.0005, +0.0030] | +0.0000 | no |
| risk_logistic_base_dealer_ofr | 5 | +0.0012 [-0.0004, +0.0031] | +0.0012 [-0.0004, +0.0031] | +0.0000 | no |
| risk_logistic_dealer_ofr | 1 | +0.0034 [+0.0003, +0.0069] * | +0.0034 [+0.0003, +0.0069] * | +0.0000 | no |
| risk_logistic_dealer_ofr | 2 | +0.0032 [+0.0007, +0.0061] * | +0.0032 [+0.0007, +0.0061] * | +0.0000 | no |
| risk_logistic_dealer_ofr | 3 | +0.0011 [+0.0001, +0.0022] * | +0.0011 [+0.0001, +0.0022] * | +0.0000 | no |
| risk_logistic_dealer_ofr | 4 | +0.0018 [+0.0003, +0.0036] * | +0.0018 [+0.0003, +0.0036] * | +0.0000 | no |
| risk_logistic_dealer_ofr | 5 | +0.0020 [+0.0004, +0.0038] * | +0.0020 [+0.0004, +0.0038] * | +0.0000 | no |
| risk_quantile_skewt_base_dealer_ofr | 1 | +0.0004 [-0.0026, +0.0033] | +0.0004 [-0.0026, +0.0033] | +0.0000 | no |
| risk_quantile_skewt_base_dealer_ofr | 2 | +0.0031 [+0.0000, +0.0064] * | +0.0031 [+0.0000, +0.0064] * | +0.0000 | no |
| risk_quantile_skewt_base_dealer_ofr | 3 | +0.0014 [-0.0025, +0.0062] | +0.0014 [-0.0025, +0.0062] | +0.0000 | no |
| risk_quantile_skewt_base_dealer_ofr | 4 | +0.0055 [+0.0007, +0.0111] * | +0.0055 [+0.0007, +0.0111] * | +0.0000 | no |
| risk_quantile_skewt_base_dealer_ofr | 5 | +0.0008 [-0.0028, +0.0044] | +0.0008 [-0.0028, +0.0044] | +0.0000 | no |
| risk_quantile_skewt_base_dealer_ofr vs risk_quantile_skewt_base_minmax | 1 | +0.0004 [-0.0026, +0.0033] | +0.0004 [-0.0026, +0.0033] | +0.0000 | no |
| risk_quantile_skewt_base_dealer_ofr vs risk_quantile_skewt_base_minmax | 2 | +0.0031 [+0.0000, +0.0064] * | +0.0031 [+0.0000, +0.0064] * | +0.0000 | no |
| risk_quantile_skewt_base_dealer_ofr vs risk_quantile_skewt_base_minmax | 3 | +0.0013 [-0.0025, +0.0062] | +0.0013 [-0.0025, +0.0062] | +0.0000 | no |
| risk_quantile_skewt_base_dealer_ofr vs risk_quantile_skewt_base_minmax | 4 | +0.0055 [+0.0007, +0.0111] * | +0.0055 [+0.0007, +0.0111] * | +0.0000 | no |
| risk_quantile_skewt_base_dealer_ofr vs risk_quantile_skewt_base_minmax | 5 | +0.0008 [-0.0027, +0.0044] | +0.0008 [-0.0027, +0.0044] | +0.0000 | no |

* Largest absolute change in a paired difference: reading candidates 0.0000; non-reading candidates 0.0000.
* Reading candidates whose excludes-zero verdict moved: none.
* Non-reading candidates whose excludes-zero verdict moved: none.

### B. Ranking of the candidates by the paired Brier difference averaged over h = 1 to 5 (best first)

| rank | committed | old data, today's code |
|---|---|---|
| 1 | risk_gbm_base_dealer_ofr (-0.0004) | risk_gbm_base_dealer_ofr (-0.0004) |
| 2 | risk_gbm_dealer_ofr (+0.0001) | risk_gbm_dealer_ofr (+0.0001) |
| 3 | risk_logistic_base_dealer_ofr (+0.0017) | risk_logistic_base_dealer_ofr (+0.0017) |
| 4 | risk_quantile_skewt_base_dealer_ofr (+0.0022) | risk_quantile_skewt_base_dealer_ofr (+0.0022) |
| 5 | risk_quantile_skewt_base_dealer_ofr vs risk_quantile_skewt_base_minmax (+0.0022) | risk_quantile_skewt_base_dealer_ofr vs risk_quantile_skewt_base_minmax (+0.0022) |
| 6 | risk_logistic_dealer_ofr (+0.0023) | risk_logistic_dealer_ofr (+0.0023) |

* Order identical: yes.
* Sign of the average difference identical for every candidate: yes.

### C. +5 bp onsets flagged / onsets at some lead 1 to 5, by year (committed -> old data, today's code)

| model | reads | 2018 | 2019 | 2020 | 2024 | 2025 | all |
|---|---|---|---|---|---|---|---|
| risk_gbm | - | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_gbm_base | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_gbm_base_dealer_ofr | R | 0/5 | 10/13 | 0/2 | 0/2 | 5/5 | 15/27 |
| risk_gbm_dealer_ofr | R | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_logistic | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_logistic_base | - | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_logistic_base_dealer_ofr | R | 0/5 | 10/13 | 0/2 | 0/2 | 5/5 | 15/27 |
| risk_logistic_dealer_ofr | R | 0/5 | 10/13 | 0/2 | 0/2 | 5/5 | 15/27 |
| risk_quantile_skewt_base | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_quantile_skewt_base_dealer_ofr | R | 0/5 | 10/13 | 0/2 | 0/2 | 5/5 | 15/27 |
| risk_quantile_skewt_base_minmax | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |

* Cells that moved: none.

### D. Judge row at +5 bp (tiers 1, 3, 5) and AUROC per horizon (committed -> old data, today's code)

AUROC is the judge's point value for the +5 bp probability at each horizon (the judge gives it no interval; the interval-carrying comparison is A). The pass verdict is the judge's: tiers 1 / 3 / 5.

| model | reads | onsets flagged | recall [90%] | false alarms per onset | verdict (tiers 1 / 3 / 5) | AUROC h=1..5 |
|---|---|---|---|---|---|---|
| calendar_climatology | - | 12 of 26 | 0.462 [0.286, 0.667] | 6.69 -> **6.85 flat / 3.90 weighted** | fail (tiers no / no / no) | 0.586 / 0.586 / 0.585 / 0.580 / 0.578 |
| persistence_logistic | - | 12 of 26 | 0.462 [0.273, 0.650] | 7.04 -> **8.46 flat / 4.09 weighted** | fail (tiers no / no / no) | 0.876 / 0.817 / 0.765 / 0.788 / 0.772 |
| published_v1 | - | 14 of 26 | 0.538 [0.350, 0.720] | 5.73 -> **7.38 flat / 3.06 weighted** | fail (tiers no / no / no) -> **fail (tiers no / yes / no)** | 0.898 / 0.881 / 0.887 / 0.871 / 0.876 |
| risk_gbm | - | 13 of 26 | 0.500 [0.310, 0.667] | 1.38 -> **2.12 flat / 1.48 weighted** | fail (tiers yes / no / no) | 0.642 / 0.578 / 0.579 / 0.579 / 0.577 |
| risk_gbm_base | - | 14 of 26 | 0.538 [0.360, 0.719] | 1.50 -> **2.19 flat / 1.59 weighted** | fail (tiers yes / no / no) | 0.643 / 0.578 / 0.579 / 0.579 / 0.576 |
| risk_gbm_base_dealer_ofr | R | 15 of 26 | 0.577 [0.391, 0.760] | 1.27 -> **2.23 flat / 1.58 weighted** | fail (tiers yes / no / no) | 0.642 / 0.578 / 0.580 / 0.579 / 0.576 |
| risk_gbm_dealer_ofr | R | 13 of 26 | 0.500 [0.321, 0.678] | 1.35 -> **2.19 flat / 1.51 weighted** | fail (tiers yes / no / no) | 0.642 / 0.578 / 0.579 / 0.579 / 0.577 |
| risk_logistic | - | 16 of 26 | 0.615 [0.435, 0.800] | 2.42 -> **3.31 flat / 2.55 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.642 / 0.579 / 0.579 / 0.578 / 0.577 |
| risk_logistic_base | - | 15 of 26 | 0.577 [0.391, 0.762] | 2.31 -> **2.88 flat / 2.18 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.643 / 0.579 / 0.579 / 0.578 / 0.577 |
| risk_logistic_base_dealer_ofr | R | 15 of 26 | 0.577 [0.394, 0.750] | 2.31 -> **3.35 flat / 2.62 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.643 / 0.578 / 0.579 / 0.578 / 0.578 |
| risk_logistic_dealer_ofr | R | 16 of 26 | 0.615 [0.429, 0.800] | 2.62 -> **3.81 flat / 3.05 weighted** | fail (tiers no / no / no) | 0.642 / 0.577 / 0.578 / 0.578 / 0.577 |
| risk_quantile_skewt_base | - | 15 of 26 | 0.577 [0.391, 0.750] | 2.31 -> **2.88 flat / 2.14 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.635 / 0.582 / 0.585 / 0.586 / 0.585 |
| risk_quantile_skewt_base_dealer_ofr | R | 15 of 26 | 0.577 [0.400, 0.750] | 2.69 -> **4.19 flat / 3.45 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.648 / 0.580 / 0.585 / 0.580 / 0.588 |
| risk_quantile_skewt_base_minmax | - | 15 of 26 | 0.577 [0.400, 0.759] | 2.31 -> **2.88 flat / 2.14 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.636 / 0.582 / 0.585 / 0.586 / 0.585 |

* Overall pass/fail moved for: none (all fail in both).
* Any tier cell of the verdict moved for: published_v1, risk_logistic, risk_logistic_base, risk_logistic_base_dealer_ofr, risk_quantile_skewt_base, risk_quantile_skewt_base_dealer_ofr, risk_quantile_skewt_base_minmax.


