# The corrected test on post-2020 resampled history: result (H1 step 5, #886)

**Development and simulated data only; no verdict, no lockbox day scored.** Every figure below is read from `docs/research/protocol-calibration-886/result.json`, `power-study-886/result.json`, `power-replay-886/result.json` and `confirmation-design-886/result.json` (with #878's records beside them) by `scripts/postcovid_886.py report`. `scoring_protocol.CRITICAL_VALUES` and `FUTILITY_CRITICAL_VALUES` and `docs/decisions/scoring-protocol.md` are unchanged by this step.

## 1. The calibrated values

Same looks, level, windows (125: 20,000, 250: 20,000 for the efficacy value, 20,000 for futility) and seed 1 as the records of #695 and #873. Only the history and the window generator change: the new column draws stationary bootstrap, mean block length scoring_protocol.BLOCK_LENGTH, on the post-2020 days (post-2020 series: 1,598 days for the grid comparison, 1,429 for B3's five levels; decision days from 2020-04-03). Every column is in the orientation `d = S(benchmark) - S(candidate), benchmark B1` except the first. Look 1 has no efficacy value (Q-B).

| value | days | in force (S(B2) - S(B1), circular, full history) | #878's draft (S(B1) - S(candidate), circular, full history) | new (S(B1) - S(candidate), stationary, post-2020) |
|---|---|---|---|---|
| efficacy, grid comparison (B2 against B1) | 125 | 3.419 | 2.548 | 5.710 |
| efficacy, grid comparison (B2 against B1) | 250 | 2.426 | 1.347 | 3.012 |
| efficacy, B3 against B1 (five levels) | 125 | 9.501 | 1.434 | 2.267 |
| efficacy, B3 against B1 (five levels) | 250 | 5.455 | 1.006 | 1.583 |
| futility (upper bound of skill, grid comparison) | 60 | 1.930 | 2.438 | 2.256 |
| futility (upper bound of skill, grid comparison) | 125 | 1.565 | 2.289 | 2.026 |
| futility (upper bound of skill, grid comparison) | 250 | 1.446 | 2.298 | 1.987 |

## 2. Size and power at the MME and at 10%

`scripts/power_study_769.py` (the rule, the paths and the four readings of #769; 2,000 paths per cell, seed 76902307) at the critical values at looks 2 and 3 (#878's: 125: 2.548, 250: 1.347; new: 125: 5.710, 250: 3.012). Size is the share of null paths detected by that look (the test without the MME gate); power is the MME-gated share at a true skill of 3% (the MME) and 10% against B1 (`NOISE` = 1). Each figure carries ± 1.96 Monte Carlo standard errors. The B2 half of Supported is not simulated, so each power is an upper bound.

| reading | values | size 125 | size 250 | 3% 125 | 3% 250 | 10% 125 | 10% 250 |
|---|---|---|---|---|---|---|---|
| (a) full history, circular blocks | #878's values | 0.9% ± 0.4 | 5.9% ± 1.0 | 1.3% ± 0.5 | 8.7% ± 1.2 | 2.6% ± 0.7 | 15.8% ± 1.6 |
| (a) full history, circular blocks | new values | 0.0% ± 0.0 | 0.1% ± 0.2 | 0.0% ± 0.0 | 0.2% ± 0.2 | 0.0% ± 0.0 | 0.5% ± 0.3 |
| (b) post-2020-04, circular blocks | #878's values | 6.1% ± 1.0 | 20.2% ± 1.8 | 7.3% ± 1.1 | 24.3% ± 1.9 | 9.8% ± 1.3 | 33.7% ± 2.1 |
| (b) post-2020-04, circular blocks | new values | 0.4% ± 0.3 | 2.1% ± 0.6 | 0.4% ± 0.3 | 2.6% ± 0.7 | 0.4% ± 0.3 | 5.0% ± 1.0 |
| (c) full history, stationary bootstrap | #878's values | 1.8% ± 0.6 | 9.4% ± 1.3 | 2.5% ± 0.7 | 11.8% ± 1.4 | 4.1% ± 0.9 | 20.7% ± 1.8 |
| (c) full history, stationary bootstrap | new values | 0.0% ± 0.0 | 0.2% ± 0.2 | 0.0% ± 0.0 | 0.6% ± 0.3 | 0.1% ± 0.1 | 1.2% ± 0.5 |
| (d) post-2020-04, stationary bootstrap | #878's values | 11.0% ± 1.4 | 26.6% ± 1.9 | 12.3% ± 1.4 | 30.8% ± 2.0 | 15.8% ± 1.6 | 39.8% ± 2.1 |
| (d) post-2020-04, stationary bootstrap | new values | 0.5% ± 0.3 | 5.0% ± 1.0 | 0.6% ± 0.3 | 6.1% ± 1.0 | 0.9% ± 0.4 | 9.6% ± 1.3 |

## 3. The replay of #754 and #792 at the corrected values

`scripts/power_replay_inforce_873.py`'s windows (250 days, slid every 5 days, no day after 2025-12-31), read at looks 60, 125, 250 at three sets of values for the grid comparison and, on P3 only, at the matching five-level values. Share of windows flagged (MME-gated in brackets), with a moving-block 95% interval for the test share. The windows overlap, so the effective number of independent windows is small (7 at 250 days): read the interval, not the share.

### Grid values: draft of #873 (878) (125: 2.548, 250: 1.347)

| pair | series | windows | effective | test (gated) [interval] |
|---|---|---|---|---|
| P2 B2 vs B1 | real pair | 324 | 7 | 15.4% (15.4%) [0.0%, 28.0%] |
| P2 B2 vs B1 | E1 relabelled copy | 324 | 7 | 0.0% (0.0%) [0.0%, 0.0%] |
| P2 B2 vs B1 | E2 demeaned | 324 | 7 | 34.0% (34.0%) [3.1%, 58.9%] |
| P2 B2 vs B1 | E3 sign-flipped | 324 | 7 | 16.7% (16.7%) [12.6%, 22.6%] |
| P2r B1 vs B2 (a reversed pair, a diagnostic) | real pair | 324 | 7 | 53.4% (53.4%) [31.4%, 92.6%] |
| P2r B1 vs B2 (a reversed pair, a diagnostic) | E1 relabelled copy | 324 | 7 | 0.0% (0.0%) [0.0%, 0.0%] |
| P2r B1 vs B2 (a reversed pair, a diagnostic) | E2 demeaned | 324 | 7 | 33.0% (33.0%) [9.7%, 70.6%] |
| P2r B1 vs B2 (a reversed pair, a diagnostic) | E3 sign-flipped | 324 | 7 | 18.5% (18.5%) [13.7%, 21.4%] |
| P3 B3 vs B1 | real pair | 324 | 7 | 59.0% (59.0%) [24.9%, 77.1%] |
| P3 B3 vs B1 | E1 relabelled copy | 324 | 7 | 0.0% (0.0%) [0.0%, 0.0%] |
| P3 B3 vs B1 | E2 demeaned | 324 | 7 | 2.8% (2.8%) [0.0%, 5.1%] |
| P3 B3 vs B1 | E3 sign-flipped | 324 | 7 | 14.2% (14.2%) [8.6%, 20.0%] |

### Grid values: in force today (125: 3.419, 250: 2.426)

| pair | series | windows | effective | test (gated) [interval] |
|---|---|---|---|---|
| P2 B2 vs B1 | real pair | 324 | 7 | 2.5% (2.5%) [0.0%, 4.6%] |
| P2 B2 vs B1 | E1 relabelled copy | 324 | 7 | 0.0% (0.0%) [0.0%, 0.0%] |
| P2 B2 vs B1 | E2 demeaned | 324 | 7 | 15.7% (15.7%) [0.0%, 32.6%] |
| P2 B2 vs B1 | E3 sign-flipped | 324 | 7 | 3.1% (3.1%) [1.4%, 6.0%] |
| P2r B1 vs B2 (a reversed pair, a diagnostic) | real pair | 324 | 7 | 35.8% (35.8%) [18.3%, 68.3%] |
| P2r B1 vs B2 (a reversed pair, a diagnostic) | E1 relabelled copy | 324 | 7 | 0.0% (0.0%) [0.0%, 0.0%] |
| P2r B1 vs B2 (a reversed pair, a diagnostic) | E2 demeaned | 324 | 7 | 23.8% (23.8%) [3.4%, 56.0%] |
| P2r B1 vs B2 (a reversed pair, a diagnostic) | E3 sign-flipped | 324 | 7 | 4.0% (4.0%) [2.6%, 5.7%] |
| P3 B3 vs B1 | real pair | 324 | 7 | 31.5% (31.5%) [4.0%, 57.7%] |
| P3 B3 vs B1 | E1 relabelled copy | 324 | 7 | 0.0% (0.0%) [0.0%, 0.0%] |
| P3 B3 vs B1 | E2 demeaned | 324 | 7 | 0.0% (0.0%) [0.0%, 0.0%] |
| P3 B3 vs B1 | E3 sign-flipped | 324 | 7 | 2.5% (2.5%) [0.0%, 5.1%] |

### Grid values: post-2020 stationary (886) (125: 5.710, 250: 3.012)

| pair | series | windows | effective | test (gated) [interval] |
|---|---|---|---|---|
| P2 B2 vs B1 | real pair | 324 | 7 | 1.2% (1.2%) [0.0%, 2.3%] |
| P2 B2 vs B1 | E1 relabelled copy | 324 | 7 | 0.0% (0.0%) [0.0%, 0.0%] |
| P2 B2 vs B1 | E2 demeaned | 324 | 7 | 5.9% (5.9%) [0.0%, 11.4%] |
| P2 B2 vs B1 | E3 sign-flipped | 324 | 7 | 1.2% (1.2%) [0.0%, 2.9%] |
| P2r B1 vs B2 (a reversed pair, a diagnostic) | real pair | 324 | 7 | 26.9% (26.9%) [8.3%, 58.0%] |
| P2r B1 vs B2 (a reversed pair, a diagnostic) | E1 relabelled copy | 324 | 7 | 0.0% (0.0%) [0.0%, 0.0%] |
| P2r B1 vs B2 (a reversed pair, a diagnostic) | E2 demeaned | 324 | 7 | 15.7% (15.7%) [0.0%, 42.0%] |
| P2r B1 vs B2 (a reversed pair, a diagnostic) | E3 sign-flipped | 324 | 7 | 1.2% (1.2%) [0.6%, 2.3%] |
| P3 B3 vs B1 | real pair | 324 | 7 | 12.7% (12.7%) [0.3%, 18.6%] |
| P3 B3 vs B1 | E1 relabelled copy | 324 | 7 | 0.0% (0.0%) [0.0%, 0.0%] |
| P3 B3 vs B1 | E2 demeaned | 324 | 7 | 0.0% (0.0%) [0.0%, 0.0%] |
| P3 B3 vs B1 | E3 sign-flipped | 324 | 7 | 0.6% (0.6%) [0.0%, 1.1%] |

### B3 five-level values: draft of #873 (878) (125: 1.434, 250: 1.006)

| pair | series | windows | effective | test (gated) [interval] |
|---|---|---|---|---|
| P3 B3 vs B1 | real pair | 324 | 7 | 72.8% (72.8%) [42.6%, 90.6%] |
| P3 B3 vs B1 | E1 relabelled copy | 324 | 7 | 0.0% (0.0%) [0.0%, 0.0%] |
| P3 B3 vs B1 | E2 demeaned | 324 | 7 | 11.7% (11.7%) [0.0%, 24.0%] |
| P3 B3 vs B1 | E3 sign-flipped | 324 | 7 | 26.2% (26.2%) [20.9%, 31.1%] |

### B3 five-level values: in force today (125: 9.501, 250: 5.455)

| pair | series | windows | effective | test (gated) [interval] |
|---|---|---|---|---|
| P3 B3 vs B1 | real pair | 324 | 7 | 0.0% (0.0%) [0.0%, 0.0%] |
| P3 B3 vs B1 | E1 relabelled copy | 324 | 7 | 0.0% (0.0%) [0.0%, 0.0%] |
| P3 B3 vs B1 | E2 demeaned | 324 | 7 | 0.0% (0.0%) [0.0%, 0.0%] |
| P3 B3 vs B1 | E3 sign-flipped | 324 | 7 | 0.0% (0.0%) [0.0%, 0.0%] |

### B3 five-level values: post-2020 stationary (886) (125: 2.267, 250: 1.583)

| pair | series | windows | effective | test (gated) [interval] |
|---|---|---|---|---|
| P3 B3 vs B1 | real pair | 324 | 7 | 49.4% (49.4%) [18.0%, 69.7%] |
| P3 B3 vs B1 | E1 relabelled copy | 324 | 7 | 0.0% (0.0%) [0.0%, 0.0%] |
| P3 B3 vs B1 | E2 demeaned | 324 | 7 | 0.0% (0.0%) [0.0%, 0.0%] |
| P3 B3 vs B1 | E3 sign-flipped | 324 | 7 | 11.4% (11.4%) [6.6%, 16.6%] |

## 4. #733's confirmation designs on the corrected test

`scripts/postcovid_886.py design` (20,000 windows per value, 2,000 paths per scenario, seeds of `scripts/confirmation_design.py`, panel `4ddc3882…`): each of #733's six designs, with its values at looks 2 and 3 recalibrated on the candidate-side series (`S(B1) - S(candidate)`), either on the full history with circular blocks (the reading #873 adopted) or on the post-2020 days with stationary-bootstrap windows (this step), then simulated under #733's scenarios and read by #733's rule (§7: admissible when size is at most 5% on both histories; recommended: the shortest design within one standard error of the best power at 3%).

### Values at looks 2 and 3

| design | values | look 2 / look 3 |
|---|---|---|
| D0 | #733 as published (largest across four orientations, full history, circular) | 9.36 / 5.49 |
| D0 | candidate orientation, full history, circular | 2.62 / 1.34 |
| D0 | candidate orientation, post-2020, stationary | 6.16 / 3.15 |
| D1 | #733 as published (largest across four orientations, full history, circular) | 8.77 / 5.28 |
| D1 | candidate orientation, full history, circular | 2.36 / 1.31 |
| D1 | candidate orientation, post-2020, stationary | 5.45 / 2.93 |
| D2 | #733 as published (largest across four orientations, full history, circular) | 8.32 / 5.29 |
| D2 | candidate orientation, full history, circular | 2.01 / 1.30 |
| D2 | candidate orientation, post-2020, stationary | 5.03 / 2.78 |
| D3 | #733 as published (largest across four orientations, full history, circular) | 8.44 / 4.63 |
| D3 | candidate orientation, full history, circular | 3.12 / 1.45 |
| D3 | candidate orientation, post-2020, stationary | 7.61 / 3.66 |
| D4 | #733 as published (largest across four orientations, full history, circular) | 6.24 / 2.59 |
| D4 | candidate orientation, full history, circular | 6.24 / 2.59 |
| D4 | candidate orientation, post-2020, stationary | 8.06 / 3.82 |
| D5 | #733 as published (largest across four orientations, full history, circular) | 5.07 / 2.29 |
| D5 | candidate orientation, full history, circular | 5.07 / 2.29 |
| D5 | candidate orientation, post-2020, stationary | 7.30 / 3.47 |

### Size and power: candidate orientation, full history, circular

| design | days | size, full | size, post-2020 | power at 3%, full | power at 10%, full | power at 3%, post-2020 | power at 10%, post-2020 | admissible |
|---|---|---|---|---|---|---|---|---|
| D0 | 250 | 7.9% | 26.4% | 9.3% | 18.0% | 31.6% | 39.7% | no |
| D1 | 375 | 9.0% | 25.9% | 10.0% | 20.0% | 30.6% | 40.1% | no |
| D2 | 500 | 8.5% | 26.4% | 10.8% | 21.0% | 31.9% | 42.1% | no |
| D3 | 250 | 8.3% | 26.2% | 9.2% | 15.8% | 30.2% | 37.9% | no |
| D4 | 250 | 8.4% | 13.1% | 11.0% | 14.2% | 14.4% | 19.4% | no |
| D5 | 375 | 9.9% | 13.4% | 12.6% | 16.5% | 16.2% | 23.2% | no |

Admissible: none. Recommended by §7: none.

### Size and power: candidate orientation, post-2020, stationary

| design | days | size, full | size, post-2020 | power at 3%, full | power at 10%, full | power at 3%, post-2020 | power at 10%, post-2020 | admissible |
|---|---|---|---|---|---|---|---|---|
| D0 | 250 | 0.1% | 3.9% | 0.3% | 0.4% | 5.9% | 9.1% | yes |
| D1 | 375 | 0.1% | 4.5% | 0.2% | 0.5% | 6.2% | 10.5% | yes |
| D2 | 500 | 0.1% | 4.5% | 0.4% | 0.4% | 6.4% | 11.2% | yes |
| D3 | 250 | 0.1% | 4.4% | 0.3% | 0.3% | 6.0% | 7.7% | yes |
| D4 | 250 | 2.2% | 5.0% | 4.1% | 5.3% | 6.0% | 8.0% | yes |
| D5 | 375 | 2.1% | 5.0% | 4.2% | 5.1% | 6.2% | 9.7% | yes |

Admissible: D0, D1, D2, D3, D4, D5. Recommended by §7: D4.

#733 as published: admissible D0, D1, D2, D3; recommended D3.

