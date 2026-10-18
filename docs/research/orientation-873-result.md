# Calibrated values in the candidate orientation: result (H1 step 4, #873)

**Development and simulated data only; no verdict, no lockbox day scored.** Every figure below is read from `docs/research/protocol-calibration-873/result.json`, `power-study-873/result.json` and `power-replay-873/result.json` by `scripts/orientation_873.py report`; the amendment that would put the new values in force is a draft decision record (`docs/decisions/scoring-protocol.md`) for Eleonora to merge, and `scoring_protocol.CRITICAL_VALUES` and `FUTILITY_CRITICAL_VALUES` are unchanged by this pull request.

## 1. The calibrated values, old and new

Same windows (125: 20,000, 250: 20,000, 60: 200,000 for the efficacy value, 20,000 for futility), block 10 and seed 1 as the record in force; only the orientation changes. The efficacy value is the `1 - level` quantile of the studentized mean of `d` over resampled windows; the daily `d` is skewed, so reversing its sign moves the quantile. The look-1 efficacy value does not exist (Q-B: look 1 checks futility only). The last two columns are the share of null paths (no true difference, 2,000 paths, first 250 days of a stationary-bootstrap resample of the full development history) detected by that day: the nominal overall size is 5%.

| value | days | old (in force) | new (draft) | old null detection | new null detection |
|---|---|---|---|---|---|
| efficacy, grid comparison (B2 against B1, 23 levels) | 125 | 3.419 | 2.548 | 0.2% | 1.3% |
| efficacy, grid comparison (B2 against B1, 23 levels) | 250 | 2.426 | 1.347 | 0.9% | 8.0% |
| efficacy, B3 against B1 (five levels) | 125 | 9.501 | 1.434 | 0.0% | 0.6% |
| efficacy, B3 against B1 (five levels) | 250 | 5.455 | 1.006 | 0.0% | 6.3% |
| futility (upper bound of skill, grid comparison) | 60 | 1.930 | 2.438 |  |  |
| futility (upper bound of skill, grid comparison) | 125 | 1.565 | 2.289 |  |  |
| futility (upper bound of skill, grid comparison) | 250 | 1.446 | 2.298 |  |  |

## 2. The power study of #769 and #791 re-run on the new values

`scripts/power_study_769.py run --values draft-873`: the rule, the paths (2,000 per cell, seed 76902307) and the four readings are #769's; only the critical values at looks 2 and 3 change (old 125: 3.419, 250: 2.426; new 125: 2.548, 250: 1.347). Each figure is a share of paths with ± 1.96 Monte Carlo standard errors. Size is the share of null paths detected by that look (the test without the MME gate); power is the gated share at a true skill of 3% and 10% against B1 (`NOISE` = 1). The B2 half of Supported is not simulated, so each power is an upper bound on the full rule's.

| reading | values | size 125 | size 250 | 3% (the MME) 125 | 3% 250 | 10% 125 | 10% 250 |
|---|---|---|---|---|---|---|---|
| (a) full history, circular blocks | old | 0.1% ± 0.2 | 0.5% ± 0.3 | 0.2% ± 0.2 | 0.8% ± 0.4 | 0.4% ± 0.3 | 2.1% ± 0.6 |
| (a) full history, circular blocks | new | 0.9% ± 0.4 | 5.9% ± 1.0 | 1.3% ± 0.5 | 8.7% ± 1.2 | 2.6% ± 0.7 | 15.8% ± 1.6 |
| (b) post-2020-04, circular blocks | old | 2.6% ± 0.7 | 6.1% ± 1.0 | 3.1% ± 0.8 | 7.8% ± 1.2 | 4.3% ± 0.9 | 11.9% ± 1.4 |
| (b) post-2020-04, circular blocks | new | 6.1% ± 1.0 | 20.2% ± 1.8 | 7.3% ± 1.1 | 24.3% ± 1.9 | 9.8% ± 1.3 | 33.7% ± 2.1 |
| (c) full history, stationary bootstrap | old | 0.4% ± 0.3 | 1.2% ± 0.5 | 0.5% ± 0.3 | 1.8% ± 0.6 | 0.9% ± 0.4 | 3.7% ± 0.8 |
| (c) full history, stationary bootstrap | new | 1.8% ± 0.6 | 9.4% ± 1.3 | 2.5% ± 0.7 | 11.8% ± 1.4 | 4.1% ± 0.9 | 20.7% ± 1.8 |
| (d) post-2020-04, stationary bootstrap | old | 4.6% ± 0.9 | 10.9% ± 1.4 | 5.8% ± 1.0 | 13.9% ± 1.5 | 7.7% ± 1.2 | 19.2% ± 1.7 |
| (d) post-2020-04, stationary bootstrap | new | 11.0% ± 1.4 | 26.6% ± 1.9 | 12.3% ± 1.4 | 30.8% ± 2.0 | 15.8% ± 1.6 | 39.8% ± 2.1 |

## 3. The replay of #792 at the values of the protocol

`scripts/power_replay_inforce_873.py run`: windows of 250 days slid every 5 days over the same real pairs and known-equal series as #792 (no day after 2025-12-31), each read at looks 60, 125, 250 at the protocol's grid-comparison values (the same two values for every pair), not at values calibrated on the pair itself. Shares of windows flagged (test; gated by the MME in brackets), with a moving-block 95% interval for the test share. Windows overlap, so the effective number of independent windows is small: read an interval, not the share.

### Values draft of #873 (calibrated on S(B1) - S(candidate))

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

### Values draft of #873, B3 five-level values (calibrated on S(B1) - S(B3))

| pair | series | windows | effective | test (gated) [interval] |
|---|---|---|---|---|
| P3 B3 vs B1 | real pair | 324 | 7 | 72.8% (72.8%) [42.6%, 90.6%] |
| P3 B3 vs B1 | E1 relabelled copy | 324 | 7 | 0.0% (0.0%) [0.0%, 0.0%] |
| P3 B3 vs B1 | E2 demeaned | 324 | 7 | 11.7% (11.7%) [0.0%, 24.0%] |
| P3 B3 vs B1 | E3 sign-flipped | 324 | 7 | 26.2% (26.2%) [20.9%, 31.1%] |

### Values in force today (calibrated on S(B2) - S(B1))

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

### Values in force today, B3 five-level values (calibrated on S(B3) - S(B1))

| pair | series | windows | effective | test (gated) [interval] |
|---|---|---|---|---|
| P3 B3 vs B1 | real pair | 324 | 7 | 0.0% (0.0%) [0.0%, 0.0%] |
| P3 B3 vs B1 | E1 relabelled copy | 324 | 7 | 0.0% (0.0%) [0.0%, 0.0%] |
| P3 B3 vs B1 | E2 demeaned | 324 | 7 | 0.0% (0.0%) [0.0%, 0.0%] |
| P3 B3 vs B1 | E3 sign-flipped | 324 | 7 | 0.0% (0.0%) [0.0%, 0.0%] |

### What #792's tables described

#792 labelled its families a1 and a2 "the current test". They are the test's *form* (the studentized mean at the spent levels) with each pair's critical values calibrated on that pair's own series at 250 days (circular blocks for a1, the path generator for a2). They are not the test in force, whose two values are the same for every pair (#833). Its 250-day figures on the same windows, relabelled:

| pair | per-pair a1, real | per-pair a2, real | per-pair a1, sign-flipped | per-pair a2, sign-flipped |
|---|---|---|---|---|
| P2 B2 vs B1 | 15.7% | 11.1% | 16.7% | 13.6% |
| P2r B1 vs B2 (a reversed pair, a diagnostic) | 35.5% | 31.2% | 3.4% | 1.9% |
| P3 B3 vs B1 | 72.8% | 72.8% | 26.5% | 25.9% |
