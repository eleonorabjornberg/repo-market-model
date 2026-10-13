# Before and after #662 for `unused-inputs-result.md` (#692)

Eleonora's instruction on #692: re-run the screen unchanged apart from the data, and tabulate, for the rows that read the Fed repo take-up
columns, the committed figure beside the re-run with intervals, and say whether any ranking or conclusion moved. No published figure is edited;
this directory is new.

**Rows that read `fed_repo_*`:** the "dealer" group (`dealer_treasury_position` plus the six `fed_repo_*` fields of #425) added to each passer:
`risk_gbm_dealer`, `risk_gbm_base_dealer`, `risk_logistic_dealer`, `risk_logistic_base_dealer` (and `risk_quantile_skewt_base_dealer`, which
does not solve at h = 1 and is dropped at every horizon, as on the page; with the new data it solves at h = 5, where it failed before, but
the judge needs all five). The settle and policy groups and the five passers do not read the columns.

## Answer

* **Verdicts: nothing moved.** All nineteen scored models fail the pass rule before and after, and no tier cell of any candidate's verdict
  moves because of the data. No candidate passes, so no "Publish?" issue is owed, as on the page.
* **Ranking: it moved, among rows that are all inside one another's intervals.** The order of the fourteen paired candidates by their Brier
  difference averaged over h = 1 to 5 changes only for `risk_gbm_base_dealer` (4th to 2nd) and the two it passes (`risk_gbm_base_policy`,
  `risk_logistic_policy`, each down one). The sign of every candidate's average is unchanged (section B of the first comparison).
* **Paired Brier differences:** the largest change in any dealer row is 0.0009. The excludes-zero verdict moves for three dealer cells:
  `risk_gbm_base_dealer` h = 4 (+0.0010 *, to +0.0009, no longer excludes zero), `risk_gbm_dealer` h = 4 (+0.0003, to +0.0006 *, now excludes zero), and
  `risk_logistic_base_dealer` h = 1 (+0.0027 *, to +0.0022, no longer excludes zero). The logistic-with-dealer forms are still worse than their
  passers at h = 1 to 5 for `risk_logistic_dealer` (every interval excludes zero before and after) and at h = 2 for the base form.
* **One sentence of the page's conclusion no longer holds.** "The missed years stay missed: in 2018 (0 of 5), 2020 and 2024 not one of the
  nineteen models flags an onset at any lead" is true for 2020 and 2024 but not for 2018: with the new data `risk_logistic_base_dealer` flags
  3 of the 5 onsets of 2018 (15 of 27 in all becomes 17 of 27; its 2025 count goes 5 to 4 of 5). `risk_logistic_dealer` 2025 goes 5 to 4 of 5
  (15 to 14 of 27). The page's "the dealer group moves 2025 up for three of the five passers" becomes two (`risk_gbm_base_dealer` 4 to 5,
  `risk_logistic_base_dealer` 3 to 4); `risk_logistic_dealer` is level with its passer (4 of 5). The 2018 change is the one the data change
  predicts: 2018-05 to 2019-09 is where the test operations were dropped and the days-since-positive column stopped restarting. It is three onsets
  in one regime and the recall interval of that row ([0.481, 0.810]) overlaps its passer's.
* **Judge Table 3 of the page:** "all nineteen models meet tier 1" is not reproduced by today's judge, with the old data as well as the new
  (see the drift section): that is a change to the judge since the page, not to the data.

## How this was produced

* **Panel.** Published panel `4ddc3882cd6d406b11e1088f8ff6195e16dde175a0ad6818abe40dd5bdac8999`, rebuilt from the tracked fixtures and checked with
  `verify-panel` (clean). Scratch panels are built by the chain on the result page's "Reproduce" section, on `main` at the commit this branch
  starts from. Development data only: scored days 2018-06-29 to 2025-12-31; no 2026 day is read (`docs/decisions/lockbox.md`);
  `repo_term_outstanding` stays off `FEATURE_FIELDS`; no declaration changed.
* **Re-run = "new data".** Every command of the page's "Reproduce" section, unchanged, on today's `main` (which carries #662). The files next to
  this one (`judge.md`, `tables.md`, `paired.md`, `paired.json`, and `inventory.md`) are that run's output.
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
| risk_gbm_base_dealer | 1 | +0.0002 [-0.0017, +0.0022] | -0.0007 [-0.0024, +0.0008] | -0.0009 | no |
| risk_gbm_base_dealer | 2 | -0.0008 [-0.0022, +0.0004] | -0.0008 [-0.0019, +0.0000] | -0.0000 | no |
| risk_gbm_base_dealer | 3 | -0.0016 [-0.0032, -0.0001] * | -0.0021 [-0.0038, -0.0007] * | -0.0006 | no |
| risk_gbm_base_dealer | 4 | +0.0010 [+0.0003, +0.0019] * | +0.0009 [-0.0000, +0.0020] | -0.0001 | **yes** |
| risk_gbm_base_dealer | 5 | -0.0009 [-0.0023, +0.0000] | -0.0004 [-0.0018, +0.0006] | +0.0005 | no |
| risk_gbm_dealer | 1 | +0.0007 [-0.0006, +0.0022] | +0.0008 [-0.0002, +0.0020] | +0.0001 | no |
| risk_gbm_dealer | 2 | -0.0006 [-0.0015, +0.0002] | -0.0005 [-0.0014, +0.0003] | +0.0001 | no |
| risk_gbm_dealer | 3 | +0.0003 [-0.0001, +0.0008] | -0.0001 [-0.0006, +0.0003] | -0.0005 | no |
| risk_gbm_dealer | 4 | +0.0003 [-0.0001, +0.0008] | +0.0006 [+0.0000, +0.0014] * | +0.0003 | **yes** |
| risk_gbm_dealer | 5 | -0.0002 [-0.0007, +0.0003] | -0.0002 [-0.0006, +0.0002] | -0.0000 | no |
| risk_logistic_base_dealer | 1 | +0.0027 [+0.0001, +0.0055] * | +0.0022 [-0.0001, +0.0047] | -0.0005 | **yes** |
| risk_logistic_base_dealer | 2 | +0.0027 [+0.0007, +0.0049] * | +0.0019 [+0.0002, +0.0039] * | -0.0008 | no |
| risk_logistic_base_dealer | 3 | +0.0008 [-0.0003, +0.0020] | +0.0009 [-0.0002, +0.0021] | +0.0001 | no |
| risk_logistic_base_dealer | 4 | +0.0013 [-0.0004, +0.0032] | +0.0013 [-0.0003, +0.0031] | -0.0001 | no |
| risk_logistic_base_dealer | 5 | +0.0014 [-0.0002, +0.0033] | +0.0007 [-0.0003, +0.0019] | -0.0007 | no |
| risk_logistic_dealer | 1 | +0.0035 [+0.0004, +0.0070] * | +0.0030 [+0.0002, +0.0060] * | -0.0005 | no |
| risk_logistic_dealer | 2 | +0.0032 [+0.0007, +0.0061] * | +0.0028 [+0.0003, +0.0055] * | -0.0004 | no |
| risk_logistic_dealer | 3 | +0.0011 [+0.0000, +0.0022] * | +0.0016 [+0.0004, +0.0029] * | +0.0005 | no |
| risk_logistic_dealer | 4 | +0.0019 [+0.0003, +0.0037] * | +0.0021 [+0.0005, +0.0041] * | +0.0003 | no |
| risk_logistic_dealer | 5 | +0.0021 [+0.0005, +0.0040] * | +0.0012 [+0.0001, +0.0025] * | -0.0009 | no |

* Largest absolute change in a paired difference: reading candidates 0.0009; non-reading candidates 0.0000.
* Reading candidates whose excludes-zero verdict moved: risk_gbm_base_dealer h=4, risk_gbm_dealer h=4, risk_logistic_base_dealer h=1.
* Non-reading candidates whose excludes-zero verdict moved: none.

### B. Ranking of the candidates by the paired Brier difference averaged over h = 1 to 5 (best first)

| rank | old data | new data |
|---|---|---|
| 1 | risk_logistic_base_policy (-0.0007) | risk_logistic_base_policy (-0.0007) |
| 2 | risk_gbm_base_policy (-0.0005) | risk_gbm_base_dealer (-0.0006) |
| 3 | risk_logistic_policy (-0.0005) | risk_gbm_base_policy (-0.0005) |
| 4 | risk_gbm_base_dealer (-0.0004) | risk_logistic_policy (-0.0005) |
| 5 | risk_gbm_settle (-0.0003) | risk_gbm_settle (-0.0003) |
| 6 | risk_quantile_skewt_base_settle (-0.0002) | risk_quantile_skewt_base_settle (-0.0002) |
| 7 | risk_gbm_base_settle (-0.0002) | risk_gbm_base_settle (-0.0002) |
| 8 | risk_gbm_policy (-0.0000) | risk_gbm_policy (-0.0000) |
| 9 | risk_gbm_dealer (+0.0001) | risk_gbm_dealer (+0.0001) |
| 10 | risk_logistic_base_settle (+0.0002) | risk_logistic_base_settle (+0.0002) |
| 11 | risk_logistic_settle (+0.0002) | risk_logistic_settle (+0.0002) |
| 12 | risk_logistic_base_dealer (+0.0018) | risk_logistic_base_dealer (+0.0014) |
| 13 | risk_logistic_dealer (+0.0024) | risk_logistic_dealer (+0.0021) |
| 14 | risk_quantile_skewt_base_policy (+0.0036) | risk_quantile_skewt_base_policy (+0.0036) |

* Order identical: no. Positions that changed: risk_gbm_base_policy 2->3, risk_logistic_policy 3->4, risk_gbm_base_dealer 4->2.
* Sign of the average difference identical for every candidate: yes.

### C. +5 bp onsets flagged / onsets at some lead 1 to 5, by year (old data -> new data)

| model | reads | 2018 | 2019 | 2020 | 2024 | 2025 | all |
|---|---|---|---|---|---|---|---|
| risk_gbm | - | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_gbm_base | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_gbm_base_dealer | R | 0/5 | 10/13 | 0/2 | 0/2 | 5/5 | 15/27 |
| risk_gbm_base_policy | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_gbm_base_settle | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_gbm_dealer | R | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_gbm_policy | - | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_gbm_settle | - | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_logistic | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_logistic_base | - | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_logistic_base_dealer | R | 0/5 -> **3/5** | 10/13 | 0/2 | 0/2 | 5/5 -> **4/5** | 15/27 -> **17/27** |
| risk_logistic_base_policy | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_logistic_base_settle | - | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_logistic_dealer | R | 0/5 | 10/13 | 0/2 | 0/2 | 5/5 -> **4/5** | 15/27 -> **14/27** |
| risk_logistic_policy | - | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_logistic_settle | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_quantile_skewt_base | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_quantile_skewt_base_policy | - | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_quantile_skewt_base_settle | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |

* Cells that moved: risk_logistic_base_dealer 2018, risk_logistic_base_dealer 2025, risk_logistic_dealer 2025.

### D. Judge row at +5 bp (tiers 1, 3, 5) and AUROC per horizon (old data -> new data)

AUROC is the judge's point value for the +5 bp probability at each horizon (the judge gives it no interval; the interval-carrying comparison is A). The pass verdict is the judge's: tiers 1 / 3 / 5.

| model | reads | onsets flagged | recall [90%] | false alarms per onset | verdict (tiers 1 / 3 / 5) | AUROC h=1..5 |
|---|---|---|---|---|---|---|
| calendar_climatology | - | 12 of 26 | 0.462 [0.286, 0.667] | 6.85 flat / 3.90 weighted | fail (tiers no / no / no) | 0.586 / 0.586 / 0.585 / 0.580 / 0.578 |
| persistence_logistic | - | 12 of 26 | 0.462 [0.273, 0.650] | 8.46 flat / 4.09 weighted | fail (tiers no / no / no) | 0.876 / 0.817 / 0.765 / 0.788 / 0.772 |
| published_v1 | - | 14 of 26 | 0.538 [0.350, 0.720] | 7.38 flat / 3.06 weighted | fail (tiers no / yes / no) | 0.898 / 0.881 / 0.887 / 0.871 / 0.876 |
| risk_gbm | - | 13 of 26 | 0.500 [0.310, 0.667] | 2.12 flat / 1.48 weighted | fail (tiers yes / no / no) | 0.642 / 0.578 / 0.579 / 0.579 / 0.577 |
| risk_gbm_base | - | 14 of 26 | 0.538 [0.360, 0.719] | 2.19 flat / 1.59 weighted | fail (tiers yes / no / no) | 0.643 / 0.578 / 0.579 / 0.579 / 0.576 |
| risk_gbm_base_dealer | R | 15 of 26 | 0.577 [0.394, 0.757] | 2.19 flat / 1.54 weighted -> **2.04 flat / 1.41 weighted** | fail (tiers yes / no / no) | 0.642 -> **0.643** / 0.578 / 0.580 / 0.579 / 0.576 |
| risk_gbm_base_policy | - | 14 of 26 | 0.538 [0.357, 0.714] | 1.88 flat / 1.31 weighted | fail (tiers yes / no / no) | 0.643 / 0.578 / 0.580 / 0.580 / 0.577 |
| risk_gbm_base_settle | - | 15 of 26 | 0.577 [0.391, 0.760] | 2.38 flat / 1.72 weighted | fail (tiers yes / no / no) | 0.643 / 0.577 / 0.579 / 0.579 / 0.578 |
| risk_gbm_dealer | R | 13 of 26 | 0.500 [0.320, 0.667] | 2.12 flat / 1.43 weighted -> **2.00 flat / 1.38 weighted** | fail (tiers yes / no / no) | 0.642 -> **0.643** / 0.578 / 0.579 / 0.579 / 0.577 |
| risk_gbm_policy | - | 13 of 26 | 0.500 [0.333, 0.677] | 1.96 flat / 1.38 weighted | fail (tiers yes / no / no) | 0.642 / 0.578 / 0.580 / 0.579 / 0.578 |
| risk_gbm_settle | - | 13 of 26 | 0.500 [0.333, 0.680] | 2.31 flat / 1.64 weighted | fail (tiers yes / no / no) | 0.642 / 0.578 / 0.579 / 0.580 / 0.578 |
| risk_logistic | - | 16 of 26 | 0.615 [0.435, 0.800] | 3.31 flat / 2.55 weighted | fail (tiers no / no / no) | 0.642 / 0.579 / 0.579 / 0.578 / 0.577 |
| risk_logistic_base | - | 15 of 26 | 0.577 [0.391, 0.762] | 2.88 flat / 2.18 weighted | fail (tiers no / no / no) | 0.643 / 0.579 / 0.579 / 0.578 / 0.577 |
| risk_logistic_base_dealer | R | 15 of 26 -> **17 of 26** | 0.577 [0.400, 0.759] -> **0.654 [0.481, 0.810]** | 3.35 flat / 2.62 weighted -> **3.27 flat / 2.54 weighted** | fail (tiers no / no / no) | 0.643 / 0.578 / 0.579 / 0.578 / 0.578 |
| risk_logistic_base_policy | - | 15 of 26 | 0.577 [0.394, 0.758] | 3.69 flat / 2.93 weighted | fail (tiers no / no / no) | 0.643 / 0.579 / 0.580 / 0.579 / 0.578 |
| risk_logistic_base_settle | - | 15 of 26 | 0.577 [0.389, 0.750] | 3.04 flat / 2.28 weighted | fail (tiers no / no / no) | 0.643 / 0.579 / 0.579 / 0.577 / 0.577 |
| risk_logistic_dealer | R | 15 of 26 | 0.577 [0.400, 0.759] | 3.73 flat / 2.97 weighted -> **3.77 flat / 3.01 weighted** | fail (tiers no / no / no) | 0.641 -> **0.642** / 0.577 -> **0.578** / 0.578 -> **0.579** / 0.577 -> **0.578** / 0.576 -> **0.577** |
| risk_logistic_policy | - | 16 of 26 | 0.615 [0.429, 0.792] | 3.65 flat / 2.89 weighted | fail (tiers no / no / no) | 0.642 / 0.579 / 0.580 / 0.580 / 0.577 |
| risk_logistic_settle | - | 16 of 26 | 0.615 [0.429, 0.792] | 3.62 flat / 2.86 weighted | fail (tiers no / no / no) | 0.642 / 0.579 / 0.579 / 0.577 / 0.577 |
| risk_quantile_skewt_base | - | 15 of 26 | 0.577 [0.391, 0.750] | 2.88 flat / 2.14 weighted | fail (tiers no / no / no) | 0.635 / 0.582 / 0.585 / 0.586 / 0.585 |
| risk_quantile_skewt_base_policy | - | 15 of 26 | 0.577 [0.389, 0.750] | 3.04 flat / 2.32 weighted | fail (tiers no / no / no) | 0.644 / 0.566 / 0.586 / 0.578 / 0.580 |
| risk_quantile_skewt_base_settle | - | 14 of 26 | 0.538 [0.361, 0.720] | 2.92 flat / 2.22 weighted | fail (tiers no / no / no) | 0.645 / 0.577 / 0.583 / 0.581 / 0.586 |

* Overall pass/fail moved for: none (all fail in both).
* Any tier cell of the verdict moved for: none.


## 2. Committed -> re-run (the directive's before/after; includes drift on `main`)

### A. Paired Brier difference at +5 bp, candidate minus its passer, all scored days (committed / re-run)

Negative favours the candidate; 90% stationary-bootstrap interval; * = interval excludes zero. Rows of candidates that read `fed_repo_*` are all shown; rows of candidates that do not are summarised below the table.

| candidate (reads `fed_repo_*`) | h | committed | re-run | change | excludes-zero verdict moved |
|---|---|---|---|---|---|
| risk_gbm_base_dealer | 1 | +0.0002 [-0.0017, +0.0022] | -0.0007 [-0.0024, +0.0008] | -0.0009 | no |
| risk_gbm_base_dealer | 2 | -0.0008 [-0.0022, +0.0004] | -0.0008 [-0.0019, +0.0000] | -0.0000 | no |
| risk_gbm_base_dealer | 3 | -0.0016 [-0.0032, -0.0001] * | -0.0021 [-0.0038, -0.0007] * | -0.0006 | no |
| risk_gbm_base_dealer | 4 | +0.0010 [+0.0003, +0.0019] * | +0.0009 [-0.0000, +0.0020] | -0.0001 | **yes** |
| risk_gbm_base_dealer | 5 | -0.0009 [-0.0023, +0.0000] | -0.0004 [-0.0018, +0.0006] | +0.0005 | no |
| risk_gbm_dealer | 1 | +0.0007 [-0.0006, +0.0022] | +0.0008 [-0.0002, +0.0020] | +0.0001 | no |
| risk_gbm_dealer | 2 | -0.0006 [-0.0015, +0.0002] | -0.0005 [-0.0014, +0.0003] | +0.0001 | no |
| risk_gbm_dealer | 3 | +0.0003 [-0.0001, +0.0008] | -0.0001 [-0.0006, +0.0003] | -0.0005 | no |
| risk_gbm_dealer | 4 | +0.0003 [-0.0001, +0.0008] | +0.0006 [+0.0000, +0.0014] * | +0.0003 | **yes** |
| risk_gbm_dealer | 5 | -0.0002 [-0.0007, +0.0003] | -0.0002 [-0.0006, +0.0002] | -0.0000 | no |
| risk_logistic_base_dealer | 1 | +0.0027 [+0.0001, +0.0055] * | +0.0022 [-0.0001, +0.0047] | -0.0005 | **yes** |
| risk_logistic_base_dealer | 2 | +0.0027 [+0.0007, +0.0049] * | +0.0019 [+0.0002, +0.0039] * | -0.0008 | no |
| risk_logistic_base_dealer | 3 | +0.0008 [-0.0003, +0.0020] | +0.0009 [-0.0002, +0.0021] | +0.0001 | no |
| risk_logistic_base_dealer | 4 | +0.0013 [-0.0004, +0.0032] | +0.0013 [-0.0003, +0.0031] | -0.0001 | no |
| risk_logistic_base_dealer | 5 | +0.0014 [-0.0002, +0.0033] | +0.0007 [-0.0003, +0.0019] | -0.0007 | no |
| risk_logistic_dealer | 1 | +0.0035 [+0.0004, +0.0070] * | +0.0030 [+0.0002, +0.0060] * | -0.0005 | no |
| risk_logistic_dealer | 2 | +0.0032 [+0.0007, +0.0061] * | +0.0028 [+0.0003, +0.0055] * | -0.0004 | no |
| risk_logistic_dealer | 3 | +0.0011 [+0.0000, +0.0022] * | +0.0016 [+0.0004, +0.0029] * | +0.0005 | no |
| risk_logistic_dealer | 4 | +0.0019 [+0.0003, +0.0037] * | +0.0021 [+0.0005, +0.0041] * | +0.0003 | no |
| risk_logistic_dealer | 5 | +0.0021 [+0.0005, +0.0040] * | +0.0012 [+0.0001, +0.0025] * | -0.0009 | no |

* Largest absolute change in a paired difference: reading candidates 0.0009; non-reading candidates 0.0020.
* Reading candidates whose excludes-zero verdict moved: risk_gbm_base_dealer h=4, risk_gbm_dealer h=4, risk_logistic_base_dealer h=1.
* Non-reading candidates whose excludes-zero verdict moved: risk_gbm_settle h=5, risk_logistic_base_settle h=4, risk_logistic_base_settle h=5, risk_logistic_settle h=2, risk_logistic_settle h=4.

### B. Ranking of the candidates by the paired Brier difference averaged over h = 1 to 5 (best first)

| rank | committed | re-run |
|---|---|---|
| 1 | risk_logistic_base_policy (-0.0007) | risk_logistic_base_policy (-0.0007) |
| 2 | risk_gbm_base_policy (-0.0005) | risk_gbm_base_dealer (-0.0006) |
| 3 | risk_logistic_policy (-0.0005) | risk_gbm_base_policy (-0.0005) |
| 4 | risk_gbm_base_dealer (-0.0004) | risk_logistic_policy (-0.0005) |
| 5 | risk_gbm_policy (-0.0000) | risk_gbm_settle (-0.0003) |
| 6 | risk_gbm_base_settle (+0.0001) | risk_quantile_skewt_base_settle (-0.0002) |
| 7 | risk_gbm_dealer (+0.0001) | risk_gbm_base_settle (-0.0002) |
| 8 | risk_gbm_settle (+0.0001) | risk_gbm_policy (-0.0000) |
| 9 | risk_quantile_skewt_base_settle (+0.0006) | risk_gbm_dealer (+0.0001) |
| 10 | risk_logistic_base_settle (+0.0010) | risk_logistic_base_settle (+0.0002) |
| 11 | risk_logistic_settle (+0.0011) | risk_logistic_settle (+0.0002) |
| 12 | risk_logistic_base_dealer (+0.0018) | risk_logistic_base_dealer (+0.0014) |
| 13 | risk_logistic_dealer (+0.0024) | risk_logistic_dealer (+0.0021) |
| 14 | risk_quantile_skewt_base_policy (+0.0036) | risk_quantile_skewt_base_policy (+0.0036) |

* Order identical: no. Positions that changed: risk_gbm_base_policy 2->3, risk_logistic_policy 3->4, risk_gbm_base_dealer 4->2, risk_gbm_policy 5->8, risk_gbm_base_settle 6->7, risk_gbm_dealer 7->9, risk_gbm_settle 8->5, risk_quantile_skewt_base_settle 9->6.
* Sign of the average difference identical for every candidate: no.

### C. +5 bp onsets flagged / onsets at some lead 1 to 5, by year (committed -> re-run)

| model | reads | 2018 | 2019 | 2020 | 2024 | 2025 | all |
|---|---|---|---|---|---|---|---|
| risk_gbm | - | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_gbm_base | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_gbm_base_dealer | R | 0/5 | 10/13 | 0/2 | 0/2 | 5/5 | 15/27 |
| risk_gbm_base_policy | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_gbm_base_settle | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_gbm_dealer | R | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_gbm_policy | - | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_gbm_settle | - | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_logistic | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_logistic_base | - | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_logistic_base_dealer | R | 0/5 -> **3/5** | 10/13 | 0/2 | 0/2 | 5/5 -> **4/5** | 15/27 -> **17/27** |
| risk_logistic_base_policy | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_logistic_base_settle | - | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_logistic_dealer | R | 0/5 | 10/13 | 0/2 | 0/2 | 5/5 -> **4/5** | 15/27 -> **14/27** |
| risk_logistic_policy | - | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_logistic_settle | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_quantile_skewt_base | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_quantile_skewt_base_policy | - | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_quantile_skewt_base_settle | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |

* Cells that moved: risk_logistic_base_dealer 2018, risk_logistic_base_dealer 2025, risk_logistic_dealer 2025.

### D. Judge row at +5 bp (tiers 1, 3, 5) and AUROC per horizon (committed -> re-run)

AUROC is the judge's point value for the +5 bp probability at each horizon (the judge gives it no interval; the interval-carrying comparison is A). The pass verdict is the judge's: tiers 1 / 3 / 5.

| model | reads | onsets flagged | recall [90%] | false alarms per onset | verdict (tiers 1 / 3 / 5) | AUROC h=1..5 |
|---|---|---|---|---|---|---|
| calendar_climatology | - | 10 of 26 -> **12 of 26** | 0.385 [0.208, 0.588] -> **0.462 [0.286, 0.667]** | 5.00 -> **6.85 flat / 3.90 weighted** | fail (tiers no / no / no) | 0.586 / 0.586 / 0.585 / 0.580 / 0.578 |
| persistence_logistic | - | 7 of 26 -> **12 of 26** | 0.269 [0.111, 0.444] -> **0.462 [0.273, 0.650]** | 3.42 -> **8.46 flat / 4.09 weighted** | fail (tiers no / no / no) | 0.876 / 0.817 / 0.765 / 0.788 / 0.772 |
| published_v1 | - | 2 of 26 -> **14 of 26** | 0.077 [0.000, 0.185] -> **0.538 [0.350, 0.720]** | 2.35 -> **7.38 flat / 3.06 weighted** | fail (tiers no / no / no) -> **fail (tiers no / yes / no)** | 0.898 / 0.881 / 0.887 / 0.871 / 0.876 |
| risk_gbm | - | 13 of 26 | 0.500 [0.310, 0.667] | 1.35 -> **2.12 flat / 1.48 weighted** | fail (tiers yes / no / no) | 0.642 / 0.578 / 0.579 / 0.579 / 0.577 |
| risk_gbm_base | - | 14 of 26 | 0.538 [0.360, 0.719] | 1.50 -> **2.19 flat / 1.59 weighted** | fail (tiers yes / no / no) | 0.643 / 0.578 / 0.579 / 0.579 / 0.576 |
| risk_gbm_base_dealer | R | 15 of 26 | 0.577 [0.394, 0.757] | 1.19 -> **2.04 flat / 1.41 weighted** | fail (tiers yes / no / no) | 0.642 -> **0.643** / 0.578 / 0.580 / 0.579 / 0.576 |
| risk_gbm_base_policy | - | 14 of 26 | 0.538 [0.357, 0.714] | 1.19 -> **1.88 flat / 1.31 weighted** | fail (tiers yes / no / no) | 0.643 / 0.578 / 0.580 / 0.580 / 0.577 |
| risk_gbm_base_settle | - | 14 of 26 -> **15 of 26** | 0.538 [0.357, 0.714] -> **0.577 [0.391, 0.760]** | 1.35 -> **2.38 flat / 1.72 weighted** | fail (tiers yes / no / no) | 0.642 -> **0.643** / 0.577 / 0.579 / 0.579 / 0.577 -> **0.578** |
| risk_gbm_dealer | R | 13 of 26 | 0.500 [0.320, 0.667] | 1.12 -> **2.00 flat / 1.38 weighted** | fail (tiers yes / no / no) | 0.642 -> **0.643** / 0.578 / 0.579 / 0.579 / 0.577 |
| risk_gbm_policy | - | 13 of 26 | 0.500 [0.333, 0.677] | 1.12 -> **1.96 flat / 1.38 weighted** | fail (tiers yes / no / no) | 0.642 / 0.578 / 0.580 / 0.579 / 0.578 |
| risk_gbm_settle | - | 13 of 26 | 0.500 [0.333, 0.680] | 1.54 -> **2.31 flat / 1.64 weighted** | fail (tiers yes / no / no) | 0.642 / 0.578 / 0.580 -> **0.579** / 0.579 -> **0.580** / 0.577 -> **0.578** |
| risk_logistic | - | 14 of 26 -> **16 of 26** | 0.538 [0.350, 0.724] -> **0.615 [0.435, 0.800]** | 1.85 -> **3.31 flat / 2.55 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.642 / 0.579 / 0.579 / 0.578 / 0.577 |
| risk_logistic_base | - | 13 of 26 -> **15 of 26** | 0.500 [0.333, 0.680] -> **0.577 [0.391, 0.762]** | 1.77 -> **2.88 flat / 2.18 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.643 / 0.579 / 0.579 / 0.578 / 0.577 |
| risk_logistic_base_dealer | R | 15 of 26 -> **17 of 26** | 0.577 [0.400, 0.759] -> **0.654 [0.481, 0.810]** | 2.00 -> **3.27 flat / 2.54 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.643 / 0.578 / 0.579 / 0.578 / 0.578 |
| risk_logistic_base_policy | - | 14 of 26 -> **15 of 26** | 0.538 [0.367, 0.719] -> **0.577 [0.394, 0.758]** | 1.77 -> **3.69 flat / 2.93 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.643 / 0.579 / 0.580 / 0.579 / 0.578 |
| risk_logistic_base_settle | - | 13 of 26 -> **15 of 26** | 0.500 [0.320, 0.667] -> **0.577 [0.389, 0.750]** | 1.92 -> **3.04 flat / 2.28 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.643 / 0.579 / 0.579 / 0.578 -> **0.577** / 0.577 |
| risk_logistic_dealer | R | 15 of 26 | 0.577 [0.400, 0.759] | 2.00 -> **3.77 flat / 3.01 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.641 -> **0.642** / 0.577 -> **0.578** / 0.578 -> **0.579** / 0.577 -> **0.578** / 0.576 -> **0.577** |
| risk_logistic_policy | - | 13 of 26 -> **16 of 26** | 0.500 [0.321, 0.679] -> **0.615 [0.429, 0.792]** | 1.81 -> **3.65 flat / 2.89 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.642 / 0.579 / 0.580 / 0.580 / 0.577 |
| risk_logistic_settle | - | 14 of 26 -> **16 of 26** | 0.538 [0.353, 0.714] -> **0.615 [0.429, 0.792]** | 1.81 -> **3.62 flat / 2.86 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.642 / 0.579 / 0.579 / 0.578 -> **0.577** / 0.575 -> **0.577** |
| risk_quantile_skewt_base | - | 14 of 26 -> **15 of 26** | 0.538 [0.360, 0.714] -> **0.577 [0.391, 0.750]** | 1.88 -> **2.88 flat / 2.14 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.635 / 0.582 / 0.585 / 0.586 / 0.585 |
| risk_quantile_skewt_base_policy | - | 13 of 26 -> **15 of 26** | 0.500 [0.333, 0.682] -> **0.577 [0.389, 0.750]** | 1.96 -> **3.04 flat / 2.32 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.644 / 0.566 / 0.586 / 0.578 / 0.580 |
| risk_quantile_skewt_base_settle | - | 14 of 26 | 0.538 [0.361, 0.720] | 1.69 -> **2.92 flat / 2.22 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.638 -> **0.645** / 0.579 -> **0.577** / 0.586 -> **0.583** / 0.586 -> **0.581** / 0.584 -> **0.586** |

* Overall pass/fail moved for: none (all fail in both).
* Any tier cell of the verdict moved for: published_v1, risk_logistic, risk_logistic_base, risk_logistic_base_dealer, risk_logistic_base_policy, risk_logistic_base_settle, risk_logistic_dealer, risk_logistic_policy, risk_logistic_settle, risk_quantile_skewt_base, risk_quantile_skewt_base_policy, risk_quantile_skewt_base_settle.


## 3. Drift on `main` that is not #662: committed -> old data under today's code

Dealer (reading) rows do not move at all here (largest change 0.0000 in the paired differences, same onsets). The rows that move are the settle
group, whose columns `net_settlement` rebuilt after the page was published (#618, #620, `e6bcf5ba`), and the judge's tier columns (the judge now
decides tier 1 on a pooled false-alarm count and reports tier 3 and 5 differently from the page). None of this involves the Fed repo columns.

### A. Paired Brier difference at +5 bp, candidate minus its passer, all scored days (committed / old data, today's code)

Negative favours the candidate; 90% stationary-bootstrap interval; * = interval excludes zero. Rows of candidates that read `fed_repo_*` are all shown; rows of candidates that do not are summarised below the table.

| candidate (reads `fed_repo_*`) | h | committed | old data, today's code | change | excludes-zero verdict moved |
|---|---|---|---|---|---|
| risk_gbm_base_dealer | 1 | +0.0002 [-0.0017, +0.0022] | +0.0002 [-0.0017, +0.0022] | +0.0000 | no |
| risk_gbm_base_dealer | 2 | -0.0008 [-0.0022, +0.0004] | -0.0008 [-0.0022, +0.0004] | +0.0000 | no |
| risk_gbm_base_dealer | 3 | -0.0016 [-0.0032, -0.0001] * | -0.0016 [-0.0032, -0.0001] * | +0.0000 | no |
| risk_gbm_base_dealer | 4 | +0.0010 [+0.0003, +0.0019] * | +0.0010 [+0.0003, +0.0019] * | +0.0000 | no |
| risk_gbm_base_dealer | 5 | -0.0009 [-0.0023, +0.0000] | -0.0009 [-0.0023, +0.0000] | +0.0000 | no |
| risk_gbm_dealer | 1 | +0.0007 [-0.0006, +0.0022] | +0.0007 [-0.0006, +0.0022] | +0.0000 | no |
| risk_gbm_dealer | 2 | -0.0006 [-0.0015, +0.0002] | -0.0006 [-0.0015, +0.0002] | +0.0000 | no |
| risk_gbm_dealer | 3 | +0.0003 [-0.0001, +0.0008] | +0.0003 [-0.0001, +0.0008] | +0.0000 | no |
| risk_gbm_dealer | 4 | +0.0003 [-0.0001, +0.0008] | +0.0003 [-0.0001, +0.0008] | +0.0000 | no |
| risk_gbm_dealer | 5 | -0.0002 [-0.0007, +0.0003] | -0.0002 [-0.0007, +0.0003] | +0.0000 | no |
| risk_logistic_base_dealer | 1 | +0.0027 [+0.0001, +0.0055] * | +0.0027 [+0.0001, +0.0055] * | +0.0000 | no |
| risk_logistic_base_dealer | 2 | +0.0027 [+0.0007, +0.0049] * | +0.0027 [+0.0007, +0.0049] * | +0.0000 | no |
| risk_logistic_base_dealer | 3 | +0.0008 [-0.0003, +0.0020] | +0.0008 [-0.0003, +0.0020] | +0.0000 | no |
| risk_logistic_base_dealer | 4 | +0.0013 [-0.0004, +0.0032] | +0.0013 [-0.0004, +0.0032] | +0.0000 | no |
| risk_logistic_base_dealer | 5 | +0.0014 [-0.0002, +0.0033] | +0.0014 [-0.0002, +0.0033] | +0.0000 | no |
| risk_logistic_dealer | 1 | +0.0035 [+0.0004, +0.0070] * | +0.0035 [+0.0004, +0.0070] * | +0.0000 | no |
| risk_logistic_dealer | 2 | +0.0032 [+0.0007, +0.0061] * | +0.0032 [+0.0007, +0.0061] * | +0.0000 | no |
| risk_logistic_dealer | 3 | +0.0011 [+0.0000, +0.0022] * | +0.0011 [+0.0000, +0.0022] * | +0.0000 | no |
| risk_logistic_dealer | 4 | +0.0019 [+0.0003, +0.0037] * | +0.0019 [+0.0003, +0.0037] * | +0.0000 | no |
| risk_logistic_dealer | 5 | +0.0021 [+0.0005, +0.0040] * | +0.0021 [+0.0005, +0.0040] * | +0.0000 | no |

* Largest absolute change in a paired difference: reading candidates 0.0000; non-reading candidates 0.0020.
* Reading candidates whose excludes-zero verdict moved: none.
* Non-reading candidates whose excludes-zero verdict moved: risk_gbm_settle h=5, risk_logistic_base_settle h=4, risk_logistic_base_settle h=5, risk_logistic_settle h=2, risk_logistic_settle h=4.

### B. Ranking of the candidates by the paired Brier difference averaged over h = 1 to 5 (best first)

| rank | committed | old data, today's code |
|---|---|---|
| 1 | risk_logistic_base_policy (-0.0007) | risk_logistic_base_policy (-0.0007) |
| 2 | risk_gbm_base_policy (-0.0005) | risk_gbm_base_policy (-0.0005) |
| 3 | risk_logistic_policy (-0.0005) | risk_logistic_policy (-0.0005) |
| 4 | risk_gbm_base_dealer (-0.0004) | risk_gbm_base_dealer (-0.0004) |
| 5 | risk_gbm_policy (-0.0000) | risk_gbm_settle (-0.0003) |
| 6 | risk_gbm_base_settle (+0.0001) | risk_quantile_skewt_base_settle (-0.0002) |
| 7 | risk_gbm_dealer (+0.0001) | risk_gbm_base_settle (-0.0002) |
| 8 | risk_gbm_settle (+0.0001) | risk_gbm_policy (-0.0000) |
| 9 | risk_quantile_skewt_base_settle (+0.0006) | risk_gbm_dealer (+0.0001) |
| 10 | risk_logistic_base_settle (+0.0010) | risk_logistic_base_settle (+0.0002) |
| 11 | risk_logistic_settle (+0.0011) | risk_logistic_settle (+0.0002) |
| 12 | risk_logistic_base_dealer (+0.0018) | risk_logistic_base_dealer (+0.0018) |
| 13 | risk_logistic_dealer (+0.0024) | risk_logistic_dealer (+0.0024) |
| 14 | risk_quantile_skewt_base_policy (+0.0036) | risk_quantile_skewt_base_policy (+0.0036) |

* Order identical: no. Positions that changed: risk_gbm_policy 5->8, risk_gbm_base_settle 6->7, risk_gbm_dealer 7->9, risk_gbm_settle 8->5, risk_quantile_skewt_base_settle 9->6.
* Sign of the average difference identical for every candidate: no.

### C. +5 bp onsets flagged / onsets at some lead 1 to 5, by year (committed -> old data, today's code)

| model | reads | 2018 | 2019 | 2020 | 2024 | 2025 | all |
|---|---|---|---|---|---|---|---|
| risk_gbm | - | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_gbm_base | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_gbm_base_dealer | R | 0/5 | 10/13 | 0/2 | 0/2 | 5/5 | 15/27 |
| risk_gbm_base_policy | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_gbm_base_settle | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_gbm_dealer | R | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_gbm_policy | - | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_gbm_settle | - | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_logistic | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_logistic_base | - | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_logistic_base_dealer | R | 0/5 | 10/13 | 0/2 | 0/2 | 5/5 | 15/27 |
| risk_logistic_base_policy | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_logistic_base_settle | - | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_logistic_dealer | R | 0/5 | 10/13 | 0/2 | 0/2 | 5/5 | 15/27 |
| risk_logistic_policy | - | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_logistic_settle | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_quantile_skewt_base | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_quantile_skewt_base_policy | - | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_quantile_skewt_base_settle | - | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |

* Cells that moved: none.

### D. Judge row at +5 bp (tiers 1, 3, 5) and AUROC per horizon (committed -> old data, today's code)

AUROC is the judge's point value for the +5 bp probability at each horizon (the judge gives it no interval; the interval-carrying comparison is A). The pass verdict is the judge's: tiers 1 / 3 / 5.

| model | reads | onsets flagged | recall [90%] | false alarms per onset | verdict (tiers 1 / 3 / 5) | AUROC h=1..5 |
|---|---|---|---|---|---|---|
| calendar_climatology | - | 10 of 26 -> **12 of 26** | 0.385 [0.208, 0.588] -> **0.462 [0.286, 0.667]** | 5.00 -> **6.85 flat / 3.90 weighted** | fail (tiers no / no / no) | 0.586 / 0.586 / 0.585 / 0.580 / 0.578 |
| persistence_logistic | - | 7 of 26 -> **12 of 26** | 0.269 [0.111, 0.444] -> **0.462 [0.273, 0.650]** | 3.42 -> **8.46 flat / 4.09 weighted** | fail (tiers no / no / no) | 0.876 / 0.817 / 0.765 / 0.788 / 0.772 |
| published_v1 | - | 2 of 26 -> **14 of 26** | 0.077 [0.000, 0.185] -> **0.538 [0.350, 0.720]** | 2.35 -> **7.38 flat / 3.06 weighted** | fail (tiers no / no / no) -> **fail (tiers no / yes / no)** | 0.898 / 0.881 / 0.887 / 0.871 / 0.876 |
| risk_gbm | - | 13 of 26 | 0.500 [0.310, 0.667] | 1.35 -> **2.12 flat / 1.48 weighted** | fail (tiers yes / no / no) | 0.642 / 0.578 / 0.579 / 0.579 / 0.577 |
| risk_gbm_base | - | 14 of 26 | 0.538 [0.360, 0.719] | 1.50 -> **2.19 flat / 1.59 weighted** | fail (tiers yes / no / no) | 0.643 / 0.578 / 0.579 / 0.579 / 0.576 |
| risk_gbm_base_dealer | R | 15 of 26 | 0.577 [0.394, 0.757] | 1.19 -> **2.19 flat / 1.54 weighted** | fail (tiers yes / no / no) | 0.642 / 0.578 / 0.580 / 0.579 / 0.576 |
| risk_gbm_base_policy | - | 14 of 26 | 0.538 [0.357, 0.714] | 1.19 -> **1.88 flat / 1.31 weighted** | fail (tiers yes / no / no) | 0.643 / 0.578 / 0.580 / 0.580 / 0.577 |
| risk_gbm_base_settle | - | 14 of 26 -> **15 of 26** | 0.538 [0.357, 0.714] -> **0.577 [0.391, 0.760]** | 1.35 -> **2.38 flat / 1.72 weighted** | fail (tiers yes / no / no) | 0.642 -> **0.643** / 0.577 / 0.579 / 0.579 / 0.577 -> **0.578** |
| risk_gbm_dealer | R | 13 of 26 | 0.500 [0.320, 0.667] | 1.12 -> **2.12 flat / 1.43 weighted** | fail (tiers yes / no / no) | 0.642 / 0.578 / 0.579 / 0.579 / 0.577 |
| risk_gbm_policy | - | 13 of 26 | 0.500 [0.333, 0.677] | 1.12 -> **1.96 flat / 1.38 weighted** | fail (tiers yes / no / no) | 0.642 / 0.578 / 0.580 / 0.579 / 0.578 |
| risk_gbm_settle | - | 13 of 26 | 0.500 [0.333, 0.680] | 1.54 -> **2.31 flat / 1.64 weighted** | fail (tiers yes / no / no) | 0.642 / 0.578 / 0.580 -> **0.579** / 0.579 -> **0.580** / 0.577 -> **0.578** |
| risk_logistic | - | 14 of 26 -> **16 of 26** | 0.538 [0.350, 0.724] -> **0.615 [0.435, 0.800]** | 1.85 -> **3.31 flat / 2.55 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.642 / 0.579 / 0.579 / 0.578 / 0.577 |
| risk_logistic_base | - | 13 of 26 -> **15 of 26** | 0.500 [0.333, 0.680] -> **0.577 [0.391, 0.762]** | 1.77 -> **2.88 flat / 2.18 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.643 / 0.579 / 0.579 / 0.578 / 0.577 |
| risk_logistic_base_dealer | R | 15 of 26 | 0.577 [0.400, 0.759] | 2.00 -> **3.35 flat / 2.62 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.643 / 0.578 / 0.579 / 0.578 / 0.578 |
| risk_logistic_base_policy | - | 14 of 26 -> **15 of 26** | 0.538 [0.367, 0.719] -> **0.577 [0.394, 0.758]** | 1.77 -> **3.69 flat / 2.93 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.643 / 0.579 / 0.580 / 0.579 / 0.578 |
| risk_logistic_base_settle | - | 13 of 26 -> **15 of 26** | 0.500 [0.320, 0.667] -> **0.577 [0.389, 0.750]** | 1.92 -> **3.04 flat / 2.28 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.643 / 0.579 / 0.579 / 0.578 -> **0.577** / 0.577 |
| risk_logistic_dealer | R | 15 of 26 | 0.577 [0.400, 0.759] | 2.00 -> **3.73 flat / 2.97 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.641 / 0.577 / 0.578 / 0.577 / 0.576 |
| risk_logistic_policy | - | 13 of 26 -> **16 of 26** | 0.500 [0.321, 0.679] -> **0.615 [0.429, 0.792]** | 1.81 -> **3.65 flat / 2.89 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.642 / 0.579 / 0.580 / 0.580 / 0.577 |
| risk_logistic_settle | - | 14 of 26 -> **16 of 26** | 0.538 [0.353, 0.714] -> **0.615 [0.429, 0.792]** | 1.81 -> **3.62 flat / 2.86 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.642 / 0.579 / 0.579 / 0.578 -> **0.577** / 0.575 -> **0.577** |
| risk_quantile_skewt_base | - | 14 of 26 -> **15 of 26** | 0.538 [0.360, 0.714] -> **0.577 [0.391, 0.750]** | 1.88 -> **2.88 flat / 2.14 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.635 / 0.582 / 0.585 / 0.586 / 0.585 |
| risk_quantile_skewt_base_policy | - | 13 of 26 -> **15 of 26** | 0.500 [0.333, 0.682] -> **0.577 [0.389, 0.750]** | 1.96 -> **3.04 flat / 2.32 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.644 / 0.566 / 0.586 / 0.578 / 0.580 |
| risk_quantile_skewt_base_settle | - | 14 of 26 | 0.538 [0.361, 0.720] | 1.69 -> **2.92 flat / 2.22 weighted** | fail (tiers yes / no / no) -> **fail (tiers no / no / no)** | 0.638 -> **0.645** / 0.579 -> **0.577** / 0.586 -> **0.583** / 0.586 -> **0.581** / 0.584 -> **0.586** |

* Overall pass/fail moved for: none (all fail in both).
* Any tier cell of the verdict moved for: published_v1, risk_logistic, risk_logistic_base, risk_logistic_base_dealer, risk_logistic_base_policy, risk_logistic_base_settle, risk_logistic_dealer, risk_logistic_policy, risk_logistic_settle, risk_quantile_skewt_base, risk_quantile_skewt_base_policy, risk_quantile_skewt_base_settle.


