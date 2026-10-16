# Power by empirical replay and three test families: result (H1 step 3, #754)

<!-- generated: scripts/power_replay.py report; never hand-edited -->

The rule is [`power-replay-754.md`](power-replay-754.md) (committed before the study ran; sha256 `f74eff75765d…`). Development data only: 1868 decision days from 2018-06-29 to 2025-12-23, panel `4ddc3882…`; no day after 2025-12-31 is read. It is a design study: no verdict, nothing registered, no protocol code changed. Replay windows start every 5 days and overlap, so each share is shown with a 1000-draw moving-block bootstrap interval and the effective number of independent windows is given. Synthetic cells have 2000 paths; critical values are calibrated on 20000 windows.

## The pairs

A pair is known better only if its mean skill is at least the MME (3%) and the studentized bootstrap p-value is below 5%. P2 and P2r are the same noise in the two orientations (amendment in the rule).

| pair | days | mean skill against its benchmark | p-value | known better |
|---|---|---|---|---|
| P2 B2 vs B1 | 1868 | -9.2% | 0.710 | **no** |
| P2r B1 vs B2 | 1868 | 8.4% | 0.290 | **no** |
| P3 B3 vs B1 | 1868 | 21.8% | 0.000 | yes |

Only P3 is a known-better pair; a detection share on the others is not power.

Day-type cells (lead-1 target day): 1601 ordinary days and 267 pressure days of P2's 1868. Regime days: 2018-19 375, 2020-24 1249, 2025 244.

## Effective windows

Windows of `N` days every 5 days over the all-days series, and the effective number of independent windows (`(windows - 1) * 5 / N + 1`).

| pair | N | windows | effective |
|---|---|---|---|
| P2 B2 vs B1 | 60 | 362 | 31 |
| P2 B2 vs B1 | 125 | 349 | 15 |
| P2 B2 vs B1 | 250 | 324 | 7 |
| P2r B1 vs B2 | 60 | 362 | 31 |
| P2r B1 vs B2 | 125 | 349 | 15 |
| P2r B1 vs B2 | 250 | 324 | 7 |
| P3 B3 vs B1 | 60 | 362 | 31 |
| P3 B3 vs B1 | 125 | 349 | 15 |
| P3 B3 vs B1 | 250 | 324 | 7 |

## Replay: size and power on real forecast pairs

Each cell is the share of windows in which the family flags the candidate (the test alone; the MME-gated share is in the next table), with its interval. The real pair's share is power only for a known-better pair. E1 is the relabelled copy (always 0%; (a) and (b) are undefined there, because the two scores never differ), E2 the demeaned pair, E3 the block sign-flip.

### (a1) the current test, critical values from circular blocks

| pair | series | test, N=60 | test, N=125 | test, N=250 | gated, N=60 | gated, N=125 | gated, N=250 |
|---|---|---|---|---|---|---|---|
| P2 B2 vs B1 | real pair | 6% [1, 12] | 12% [2, 27] | 16% [0, 28] | 6% [1, 11] | 12% [2, 27] | 16% [0, 28] |
| P2 B2 vs B1 | E1 relabelled copy | 0% | 0% | 0% | 0% | 0% | 0% |
| P2 B2 vs B1 | E2 demeaned | 21% [12, 32] | 31% [13, 49] | 34% [3, 59] | 21% [11, 32] | 31% [12, 51] | 34% [3, 57] |
| P2 B2 vs B1 | E3 sign-flipped | 12% [9, 16] | 14% [8, 20] | 17% [13, 23] | 12% [9, 16] | 14% [8, 20] | 17% [13, 23] |
| P2r B1 vs B2 | real pair | 28% [16, 40] | 28% [13, 50] | 35% [18, 68] | 28% [15, 41] | 28% [13, 51] | 35% [18, 70] |
| P2r B1 vs B2 | E1 relabelled copy | 0% | 0% | 0% | 0% | 0% | 0% |
| P2r B1 vs B2 | E2 demeaned | 19% [8, 29] | 17% [5, 37] | 22% [2, 53] | 19% [8, 30] | 17% [4, 36] | 22% [3, 56] |
| P2r B1 vs B2 | E3 sign-flipped | 7% [4, 10] | 3% [1, 6] | 3% [2, 5] | 7% [4, 10] | 3% [1, 6] | 3% [2, 5] |
| P3 B3 vs B1 | real pair | 66% [52, 78] | 73% [51, 88] | 73% [43, 91] | 66% [52, 78] | 73% [51, 88] | 73% [43, 91] |
| P3 B3 vs B1 | E1 relabelled copy | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | E2 demeaned | 7% [1, 13] | 8% [0, 22] | 12% [0, 24] | 7% [1, 13] | 8% [0, 22] | 12% [0, 25] |
| P3 B3 vs B1 | E3 sign-flipped | 29% [24, 34] | 33% [28, 38] | 27% [21, 32] | 29% [24, 34] | 33% [28, 38] | 27% [21, 32] |

### (a2) the current test, critical values matched to the paths (stationary bootstrap)

| pair | series | test, N=60 | test, N=125 | test, N=250 | gated, N=60 | gated, N=125 | gated, N=250 |
|---|---|---|---|---|---|---|---|
| P2 B2 vs B1 | real pair | 5% [1, 11] | 10% [0, 23] | 11% [0, 20] | 5% [1, 10] | 10% [0, 23] | 11% [0, 21] |
| P2 B2 vs B1 | E1 relabelled copy | 0% | 0% | 0% | 0% | 0% | 0% |
| P2 B2 vs B1 | E2 demeaned | 17% [8, 27] | 24% [10, 43] | 30% [2, 56] | 17% [8, 26] | 24% [9, 42] | 30% [1, 57] |
| P2 B2 vs B1 | E3 sign-flipped | 10% [7, 13] | 11% [5, 16] | 14% [10, 18] | 10% [7, 13] | 11% [5, 16] | 14% [10, 18] |
| P2r B1 vs B2 | real pair | 22% [11, 36] | 24% [10, 45] | 31% [12, 63] | 22% [10, 36] | 24% [9, 45] | 31% [12, 63] |
| P2r B1 vs B2 | E1 relabelled copy | 0% | 0% | 0% | 0% | 0% | 0% |
| P2r B1 vs B2 | E2 demeaned | 15% [6, 27] | 14% [3, 31] | 19% [0, 50] | 15% [6, 27] | 14% [3, 31] | 19% [0, 49] |
| P2r B1 vs B2 | E3 sign-flipped | 4% [2, 7] | 2% [0, 5] | 2% [1, 3] | 4% [2, 7] | 2% [0, 5] | 2% [1, 3] |
| P3 B3 vs B1 | real pair | 65% [51, 78] | 72% [50, 87] | 73% [42, 91] | 65% [51, 78] | 72% [51, 87] | 73% [42, 92] |
| P3 B3 vs B1 | E1 relabelled copy | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | E2 demeaned | 6% [1, 12] | 7% [0, 21] | 11% [0, 23] | 6% [1, 12] | 7% [0, 21] | 11% [0, 23] |
| P3 B3 vs B1 | E3 sign-flipped | 27% [23, 31] | 31% [26, 35] | 26% [21, 31] | 27% [22, 31] | 31% [25, 35] | 26% [20, 31] |

### (b) the self-normalised Diebold-Mariano test (fixed-b)

| pair | series | test, N=60 | test, N=125 | test, N=250 | gated, N=60 | gated, N=125 | gated, N=250 |
|---|---|---|---|---|---|---|---|
| P2 B2 vs B1 | real pair | 6% [2, 11] | 8% [0, 23] | 5% [0, 10] | 6% [2, 11] | 8% [0, 22] | 5% [0, 10] |
| P2 B2 vs B1 | E1 relabelled copy | 0% | 0% | 0% | 0% | 0% | 0% |
| P2 B2 vs B1 | E2 demeaned | 21% [12, 32] | 17% [5, 34] | 20% [0, 41] | 21% [12, 31] | 17% [6, 33] | 20% [0, 42] |
| P2 B2 vs B1 | E3 sign-flipped | 11% [7, 14] | 8% [3, 12] | 5% [3, 6] | 11% [7, 14] | 8% [4, 12] | 5% [3, 6] |
| P2r B1 vs B2 | real pair | 36% [22, 49] | 35% [17, 58] | 45% [25, 82] | 36% [23, 50] | 35% [18, 59] | 45% [22, 80] |
| P2r B1 vs B2 | E1 relabelled copy | 0% | 0% | 0% | 0% | 0% | 0% |
| P2r B1 vs B2 | E2 demeaned | 22% [10, 34] | 21% [7, 42] | 23% [4, 56] | 22% [11, 33] | 21% [7, 42] | 23% [3, 53] |
| P2r B1 vs B2 | E3 sign-flipped | 9% [6, 13] | 5% [3, 7] | 5% [3, 6] | 9% [6, 13] | 5% [3, 7] | 5% [3, 7] |
| P3 B3 vs B1 | real pair | 27% [16, 37] | 39% [19, 61] | 34% [4, 62] | 27% [16, 37] | 39% [18, 58] | 34% [5, 61] |
| P3 B3 vs B1 | E1 relabelled copy | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | E2 demeaned | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | E3 sign-flipped | 10% [7, 14] | 4% [2, 6] | 4% [1, 7] | 10% [7, 14] | 4% [2, 6] | 4% [1, 7] |

### (c1) the anytime-valid e-process, lead 1

| pair | series | test, N=60 | test, N=125 | test, N=250 | gated, N=60 | gated, N=125 | gated, N=250 |
|---|---|---|---|---|---|---|---|
| P2 B2 vs B1 | real pair | 0% | 0% | 0% | 0% | 0% | 0% |
| P2 B2 vs B1 | E1 relabelled copy | 0% | 0% | 0% | 0% | 0% | 0% |
| P2 B2 vs B1 | E2 demeaned | 0% | 0% | 0% | 0% | 0% | 0% |
| P2 B2 vs B1 | E3 sign-flipped | 0% | 0% | 0% | 0% | 0% | 0% |
| P2r B1 vs B2 | real pair | 0% | 0% | 0% | 0% | 0% | 0% |
| P2r B1 vs B2 | E1 relabelled copy | 0% | 0% | 0% | 0% | 0% | 0% |
| P2r B1 vs B2 | E2 demeaned | 0% | 0% | 0% | 0% | 0% | 0% |
| P2r B1 vs B2 | E3 sign-flipped | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | real pair | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | E1 relabelled copy | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | E2 demeaned | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | E3 sign-flipped | 0% | 0% | 0% | 0% | 0% | 0% |

### (c5) the anytime-valid e-process, mean of leads 1 to 5

| pair | series | test, N=60 | test, N=125 | test, N=250 | gated, N=60 | gated, N=125 | gated, N=250 |
|---|---|---|---|---|---|---|---|
| P2 B2 vs B1 | real pair | 0% | 0% | 0% | 0% | 0% | 0% |
| P2 B2 vs B1 | E1 relabelled copy | 0% | 0% | 0% | 0% | 0% | 0% |
| P2 B2 vs B1 | E2 demeaned | 0% | 0% | 0% | 0% | 0% | 0% |
| P2 B2 vs B1 | E3 sign-flipped | 0% | 0% | 0% | 0% | 0% | 0% |
| P2r B1 vs B2 | real pair | 0% | 0% | 0% | 0% | 0% | 0% |
| P2r B1 vs B2 | E1 relabelled copy | 0% | 0% | 0% | 0% | 0% | 0% |
| P2r B1 vs B2 | E2 demeaned | 0% | 0% | 0% | 0% | 0% | 0% |
| P2r B1 vs B2 | E3 sign-flipped | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | real pair | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | E1 relabelled copy | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | E2 demeaned | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | E3 sign-flipped | 0% | 0% | 0% | 0% | 0% | 0% |

## Replay: the pooled figure beside its splits

The test alone, by the regime of the window's last day and by day-type cell. `ordinary` and `pressure` cut the series (windows of `N` consecutive retained days); n/a is a cell with no windows.

### (a1) the current test, critical values from circular blocks

| pair | series | N | all windows | 2018-19 | 2020-24 | 2025 | ordinary days | pressure days |
|---|---|---|---|---|---|---|---|---|
| P2 B2 vs B1 | real pair | 60 | 6% [1, 12] | 2% [0, 4] | 6% [0, 14] | 10% [0, 30] | 11% [4, 20] | 0% |
| P2 B2 vs B1 | real pair | 125 | 12% [2, 27] | 4% [0, 8] | 3% [0, 8] | 65% [50, 100] | 15% [3, 27] | 0% |
| P2 B2 vs B1 | real pair | 250 | 16% [0, 28] | 50% [50, 50] | 0% | 78% [78, 78] | 23% [0, 32] | 0% |
| P2 B2 vs B1 | E2 demeaned | 60 | 21% [12, 32] | 8% [0, 14] | 22% [10, 36] | 31% [15, 60] | 18% [9, 29] | 14% [0, 38] |
| P2 B2 vs B1 | E2 demeaned | 125 | 31% [13, 49] | 18% [0, 29] | 25% [6, 48] | 71% [54, 100] | 25% [6, 40] | 0% |
| P2 B2 vs B1 | E2 demeaned | 250 | 34% [3, 59] | 65% [65, 65] | 18% [0, 33] | 94% [94, 94] | 31% [0, 48] | 0% |
| P2 B2 vs B1 | E3 sign-flipped | 60 | 12% [9, 16] | 8% [1, 15] | 14% [9, 18] | 10% [5, 17] | 17% [13, 23] | 2% [0, 6] |
| P2 B2 vs B1 | E3 sign-flipped | 125 | 14% [8, 20] | 0% | 16% [10, 23] | 18% [10, 20] | 15% [13, 19] | 3% [4, 4] |
| P2 B2 vs B1 | E3 sign-flipped | 250 | 17% [13, 23] | 15% [15, 15] | 18% [15, 25] | 10% [10, 10] | 20% [15, 25] | 0% |
| P2r B1 vs B2 | real pair | 60 | 28% [16, 40] | 6% [0, 19] | 36% [20, 55] | 14% [0, 23] | 23% [11, 36] | 71% [67, 100] |
| P2r B1 vs B2 | real pair | 125 | 28% [13, 50] | 0% | 39% [21, 66] | 0% | 22% [8, 43] | 76% [72, 88] |
| P2r B1 vs B2 | real pair | 250 | 35% [18, 68] | 0% | 46% [33, 82] | 0% | 30% [11, 68] | 100% |
| P2r B1 vs B2 | E2 demeaned | 60 | 19% [8, 29] | 0% | 25% [12, 42] | 12% [0, 18] | 19% [8, 31] | 0% |
| P2r B1 vs B2 | E2 demeaned | 125 | 17% [5, 37] | 0% | 24% [8, 49] | 0% | 18% [4, 40] | 0% |
| P2r B1 vs B2 | E2 demeaned | 250 | 22% [2, 53] | 0% | 28% [7, 66] | 0% | 23% [3, 59] | 0% |
| P2r B1 vs B2 | E3 sign-flipped | 60 | 7% [4, 10] | 2% [0, 6] | 8% [5, 13] | 6% [0, 17] | 6% [3, 10] | 10% [2, 12] |
| P2r B1 vs B2 | E3 sign-flipped | 125 | 3% [1, 6] | 2% [0, 4] | 4% [1, 7] | 2% [0, 4] | 3% [1, 6] | 3% [4, 4] |
| P2r B1 vs B2 | E3 sign-flipped | 250 | 3% [2, 5] | 0% | 4% [3, 6] | 4% [4, 4] | 2% [1, 4] | 0% |
| P3 B3 vs B1 | real pair | 60 | 66% [52, 78] | 80% [50, 97] | 57% [39, 72] | 98% [95, 100] | 70% [54, 81] | 10% [0, 15] |
| P3 B3 vs B1 | real pair | 125 | 73% [51, 88] | 98% [96, 97] | 62% [36, 80] | 100% | 72% [50, 87] | 0% |
| P3 B3 vs B1 | real pair | 250 | 73% [43, 91] | 100% | 65% [27, 84] | 100% | 72% [34, 93] | 0% |
| P3 B3 vs B1 | E2 demeaned | 60 | 7% [1, 13] | 31% [10, 56] | 0% | 10% [0, 15] | 8% [2, 16] | 2% [0, 2] |
| P3 B3 vs B1 | E2 demeaned | 125 | 8% [0, 22] | 31% [12, 39] | 5% [0, 7] | 0% | 9% [0, 23] | 0% |
| P3 B3 vs B1 | E2 demeaned | 250 | 12% [0, 24] | 58% [58, 58] | 8% [0, 11] | 6% [6, 6] | 11% [0, 19] | 0% |
| P3 B3 vs B1 | E3 sign-flipped | 60 | 29% [24, 34] | 27% [17, 33] | 29% [22, 35] | 35% [22, 45] | 32% [27, 38] | 12% [2, 27] |
| P3 B3 vs B1 | E3 sign-flipped | 125 | 33% [28, 38] | 29% [19, 33] | 34% [27, 39] | 33% [28, 36] | 31% [24, 35] | 0% |
| P3 B3 vs B1 | E3 sign-flipped | 250 | 27% [21, 32] | 19% [19, 19] | 26% [18, 33] | 35% [35, 35] | 28% [21, 31] | 0% |

### (a2) the current test, critical values matched to the paths (stationary bootstrap)

| pair | series | N | all windows | 2018-19 | 2020-24 | 2025 | ordinary days | pressure days |
|---|---|---|---|---|---|---|---|---|
| P2 B2 vs B1 | real pair | 60 | 5% [1, 11] | 2% [0, 4] | 5% [1, 12] | 10% [0, 28] | 9% [4, 17] | 0% |
| P2 B2 vs B1 | real pair | 125 | 10% [0, 23] | 0% | 2% [0, 5] | 61% [50, 96] | 11% [1, 25] | 0% |
| P2 B2 vs B1 | real pair | 250 | 11% [0, 20] | 19% [19, 19] | 0% | 63% [63, 63] | 20% [0, 29] | 0% |
| P2 B2 vs B1 | E2 demeaned | 60 | 17% [8, 27] | 6% [0, 12] | 19% [8, 33] | 20% [7, 48] | 14% [7, 26] | 14% [0, 38] |
| P2 B2 vs B1 | E2 demeaned | 125 | 24% [10, 43] | 4% [0, 8] | 19% [4, 38] | 71% [54, 100] | 19% [4, 35] | 0% |
| P2 B2 vs B1 | E2 demeaned | 250 | 30% [2, 56] | 46% [46, 46] | 17% [0, 30] | 86% [86, 86] | 29% [0, 47] | 0% |
| P2 B2 vs B1 | E3 sign-flipped | 60 | 10% [7, 13] | 6% [1, 14] | 11% [7, 15] | 10% [5, 17] | 15% [10, 20] | 2% [0, 8] |
| P2 B2 vs B1 | E3 sign-flipped | 125 | 11% [5, 16] | 0% | 12% [6, 19] | 12% [4, 16] | 11% [9, 16] | 3% [4, 4] |
| P2 B2 vs B1 | E3 sign-flipped | 250 | 14% [10, 18] | 15% [15, 15] | 14% [12, 21] | 8% [8, 8] | 15% [10, 19] | 0% |
| P2r B1 vs B2 | real pair | 60 | 22% [11, 36] | 0% | 30% [14, 48] | 12% [0, 18] | 19% [7, 33] | 79% [71, 100] |
| P2r B1 vs B2 | real pair | 125 | 24% [10, 45] | 0% | 34% [17, 62] | 0% | 20% [6, 44] | 83% [80, 92] |
| P2r B1 vs B2 | real pair | 250 | 31% [12, 63] | 0% | 41% [24, 79] | 0% | 24% [3, 60] | 100% |
| P2r B1 vs B2 | E2 demeaned | 60 | 15% [6, 27] | 0% | 21% [8, 38] | 6% [0, 8] | 15% [4, 29] | 2% [0, 6] |
| P2r B1 vs B2 | E2 demeaned | 125 | 14% [3, 31] | 0% | 20% [4, 45] | 0% | 15% [2, 38] | 0% |
| P2r B1 vs B2 | E2 demeaned | 250 | 19% [0, 50] | 0% | 25% [2, 63] | 0% | 23% [2, 58] | 0% |
| P2r B1 vs B2 | E3 sign-flipped | 60 | 4% [2, 7] | 2% [0, 4] | 5% [2, 9] | 4% [0, 13] | 4% [2, 7] | 10% [2, 12] |
| P2r B1 vs B2 | E3 sign-flipped | 125 | 2% [0, 5] | 0% | 3% [0, 6] | 0% | 3% [1, 5] | 10% [8, 12] |
| P2r B1 vs B2 | E3 sign-flipped | 250 | 2% [1, 3] | 0% | 2% [2, 4] | 2% [2, 2] | 2% [1, 4] | 0% |
| P3 B3 vs B1 | real pair | 60 | 65% [51, 78] | 80% [50, 97] | 55% [38, 70] | 98% [95, 100] | 68% [53, 81] | 10% [0, 15] |
| P3 B3 vs B1 | real pair | 125 | 72% [50, 87] | 98% [96, 97] | 61% [34, 77] | 100% | 72% [47, 89] | 0% |
| P3 B3 vs B1 | real pair | 250 | 73% [42, 91] | 100% | 65% [26, 85] | 100% | 71% [32, 93] | 0% |
| P3 B3 vs B1 | E2 demeaned | 60 | 6% [1, 12] | 25% [6, 49] | 0% | 10% [0, 13] | 6% [1, 12] | 2% [0, 2] |
| P3 B3 vs B1 | E2 demeaned | 125 | 7% [0, 21] | 27% [4, 36] | 5% [0, 7] | 0% | 8% [0, 23] | 0% |
| P3 B3 vs B1 | E2 demeaned | 250 | 11% [0, 23] | 58% [58, 58] | 7% [0, 8] | 6% [6, 6] | 10% [0, 16] | 0% |
| P3 B3 vs B1 | E3 sign-flipped | 60 | 27% [23, 31] | 25% [17, 29] | 28% [22, 34] | 27% [20, 38] | 29% [25, 35] | 10% [0, 21] |
| P3 B3 vs B1 | E3 sign-flipped | 125 | 31% [26, 35] | 29% [19, 33] | 32% [24, 37] | 31% [28, 36] | 27% [21, 31] | 0% |
| P3 B3 vs B1 | E3 sign-flipped | 250 | 26% [21, 31] | 19% [19, 19] | 25% [18, 32] | 35% [35, 35] | 26% [19, 29] | 0% |

### (b) the self-normalised Diebold-Mariano test (fixed-b)

| pair | series | N | all windows | 2018-19 | 2020-24 | 2025 | ordinary days | pressure days |
|---|---|---|---|---|---|---|---|---|
| P2 B2 vs B1 | real pair | 60 | 6% [2, 11] | 2% [0, 4] | 6% [0, 12] | 10% [3, 25] | 5% [1, 10] | 0% |
| P2 B2 vs B1 | real pair | 125 | 8% [0, 23] | 0% | 0% | 57% [46, 88] | 8% [0, 20] | 0% |
| P2 B2 vs B1 | real pair | 250 | 5% [0, 10] | 0% | 0% | 35% [35, 35] | 7% [0, 12] | 0% |
| P2 B2 vs B1 | E2 demeaned | 60 | 21% [12, 32] | 9% [1, 14] | 20% [7, 33] | 39% [23, 62] | 10% [4, 18] | 29% [0, 58] |
| P2 B2 vs B1 | E2 demeaned | 125 | 17% [5, 34] | 0% | 11% [2, 24] | 67% [52, 100] | 11% [0, 26] | 21% [12, 24] |
| P2 B2 vs B1 | E2 demeaned | 250 | 20% [0, 41] | 0% | 10% [0, 18] | 80% [80, 80] | 13% [0, 26] | 0% |
| P2 B2 vs B1 | E3 sign-flipped | 60 | 11% [7, 14] | 8% [1, 15] | 12% [8, 16] | 10% [5, 15] | 10% [5, 14] | 17% [17, 25] |
| P2 B2 vs B1 | E3 sign-flipped | 125 | 8% [3, 12] | 0% | 10% [5, 16] | 8% [0, 12] | 5% [4, 8] | 7% [8, 8] |
| P2 B2 vs B1 | E3 sign-flipped | 250 | 5% [3, 6] | 4% [4, 4] | 5% [2, 7] | 4% [4, 4] | 7% [3, 11] | 0% |
| P2r B1 vs B2 | real pair | 60 | 36% [22, 49] | 8% [0, 24] | 46% [31, 63] | 20% [0, 35] | 31% [16, 44] | 76% [71, 100] |
| P2r B1 vs B2 | real pair | 125 | 35% [17, 58] | 0% | 49% [33, 74] | 0% | 36% [18, 61] | 76% [72, 88] |
| P2r B1 vs B2 | real pair | 250 | 45% [25, 82] | 0% | 59% [47, 93] | 0% | 45% [25, 86] | 100% |
| P2r B1 vs B2 | E2 demeaned | 60 | 22% [10, 34] | 2% [0, 6] | 29% [13, 47] | 18% [0, 32] | 25% [12, 38] | 2% [0, 6] |
| P2r B1 vs B2 | E2 demeaned | 125 | 21% [7, 42] | 0% | 30% [13, 55] | 0% | 26% [11, 49] | 0% |
| P2r B1 vs B2 | E2 demeaned | 250 | 23% [4, 56] | 0% | 30% [6, 70] | 0% | 31% [12, 70] | 0% |
| P2r B1 vs B2 | E3 sign-flipped | 60 | 9% [6, 13] | 5% [0, 12] | 11% [7, 15] | 8% [0, 17] | 9% [5, 12] | 10% [2, 19] |
| P2r B1 vs B2 | E3 sign-flipped | 125 | 5% [3, 7] | 2% [0, 4] | 5% [3, 8] | 6% [4, 10] | 5% [3, 7] | 3% [4, 4] |
| P2r B1 vs B2 | E3 sign-flipped | 250 | 5% [3, 6] | 4% [4, 4] | 3% [2, 4] | 12% [12, 12] | 6% [4, 9] | 0% |
| P3 B3 vs B1 | real pair | 60 | 27% [16, 37] | 8% [0, 12] | 27% [13, 37] | 53% [25, 82] | 26% [15, 39] | 10% [0, 15] |
| P3 B3 vs B1 | real pair | 125 | 39% [19, 61] | 2% [0, 1] | 35% [13, 55] | 100% | 34% [13, 54] | 0% |
| P3 B3 vs B1 | real pair | 250 | 34% [4, 62] | 0% | 25% [1, 45] | 100% | 32% [2, 60] | 0% |
| P3 B3 vs B1 | E2 demeaned | 60 | 0% | 0% | 0% | 0% | 0% | 2% [0, 2] |
| P3 B3 vs B1 | E2 demeaned | 125 | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | E2 demeaned | 250 | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | E3 sign-flipped | 60 | 10% [7, 14] | 2% [0, 4] | 13% [9, 17] | 6% [2, 13] | 10% [7, 14] | 5% [0, 15] |
| P3 B3 vs B1 | E3 sign-flipped | 125 | 4% [2, 6] | 0% | 5% [2, 7] | 4% [0, 4] | 6% [3, 9] | 0% |
| P3 B3 vs B1 | E3 sign-flipped | 250 | 4% [1, 7] | 0% | 4% [2, 8] | 8% [8, 8] | 3% [2, 5] | 0% |

### (c1) the anytime-valid e-process, lead 1

| pair | series | N | all windows | 2018-19 | 2020-24 | 2025 | ordinary days | pressure days |
|---|---|---|---|---|---|---|---|---|
| P2 B2 vs B1 | real pair | 60 | 0% | 0% | 0% | 0% | 0% | 0% |
| P2 B2 vs B1 | real pair | 125 | 0% | 0% | 0% | 0% | 0% | 0% |
| P2 B2 vs B1 | real pair | 250 | 0% | 0% | 0% | 0% | 0% | 0% |
| P2 B2 vs B1 | E2 demeaned | 60 | 0% | 0% | 0% | 0% | 0% | 0% |
| P2 B2 vs B1 | E2 demeaned | 125 | 0% | 0% | 0% | 0% | 0% | 0% |
| P2 B2 vs B1 | E2 demeaned | 250 | 0% | 0% | 0% | 0% | 0% | 0% |
| P2 B2 vs B1 | E3 sign-flipped | 60 | 0% | 0% | 0% | 0% | 0% | 2% [0, 6] |
| P2 B2 vs B1 | E3 sign-flipped | 125 | 0% | 0% | 0% | 0% | 0% | 7% [8, 8] |
| P2 B2 vs B1 | E3 sign-flipped | 250 | 0% | 0% | 0% | 0% | 0% | 25% [25, 25] |
| P2r B1 vs B2 | real pair | 60 | 0% | 0% | 0% | 0% | 0% | 7% [0, 19] |
| P2r B1 vs B2 | real pair | 125 | 0% | 0% | 0% | 0% | 0% | 55% [48, 64] |
| P2r B1 vs B2 | real pair | 250 | 0% | 0% | 0% | 0% | 0% | 100% |
| P2r B1 vs B2 | E2 demeaned | 60 | 0% | 0% | 0% | 0% | 0% | 0% |
| P2r B1 vs B2 | E2 demeaned | 125 | 0% | 0% | 0% | 0% | 0% | 0% |
| P2r B1 vs B2 | E2 demeaned | 250 | 0% | 0% | 0% | 0% | 0% | 0% |
| P2r B1 vs B2 | E3 sign-flipped | 60 | 0% | 0% | 0% | 0% | 0% | 0% |
| P2r B1 vs B2 | E3 sign-flipped | 125 | 0% | 0% | 0% | 0% | 0% | 0% |
| P2r B1 vs B2 | E3 sign-flipped | 250 | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | real pair | 60 | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | real pair | 125 | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | real pair | 250 | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | E2 demeaned | 60 | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | E2 demeaned | 125 | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | E2 demeaned | 250 | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | E3 sign-flipped | 60 | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | E3 sign-flipped | 125 | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | E3 sign-flipped | 250 | 0% | 0% | 0% | 0% | 0% | 0% |

### (c5) the anytime-valid e-process, mean of leads 1 to 5

| pair | series | N | all windows | 2018-19 | 2020-24 | 2025 | ordinary days | pressure days |
|---|---|---|---|---|---|---|---|---|
| P2 B2 vs B1 | real pair | 60 | 0% | 0% | 0% | 0% | 0% | 0% |
| P2 B2 vs B1 | real pair | 125 | 0% | 0% | 0% | 0% | 0% | 0% |
| P2 B2 vs B1 | real pair | 250 | 0% | 0% | 0% | 0% | 0% | 0% |
| P2 B2 vs B1 | E2 demeaned | 60 | 0% | 0% | 0% | 0% | 0% | 0% |
| P2 B2 vs B1 | E2 demeaned | 125 | 0% | 0% | 0% | 0% | 0% | 14% [4, 16] |
| P2 B2 vs B1 | E2 demeaned | 250 | 0% | 0% | 0% | 0% | 0% | 0% |
| P2 B2 vs B1 | E3 sign-flipped | 60 | 0% | 0% | 0% | 0% | 0% | 10% [0, 23] |
| P2 B2 vs B1 | E3 sign-flipped | 125 | 0% | 0% | 0% | 0% | 0% | 28% [28, 32] |
| P2 B2 vs B1 | E3 sign-flipped | 250 | 0% | 0% | 0% | 0% | 0% | 50% [50, 50] |
| P2r B1 vs B2 | real pair | 60 | 0% | 0% | 0% | 0% | 0% | 43% [4, 79] |
| P2r B1 vs B2 | real pair | 125 | 0% | 0% | 0% | 0% | 0% | 79% [76, 92] |
| P2r B1 vs B2 | real pair | 250 | 0% | 0% | 0% | 0% | 0% | 100% |
| P2r B1 vs B2 | E2 demeaned | 60 | 0% | 0% | 0% | 0% | 0% | 2% [0, 6] |
| P2r B1 vs B2 | E2 demeaned | 125 | 0% | 0% | 0% | 0% | 0% | 7% [8, 8] |
| P2r B1 vs B2 | E2 demeaned | 250 | 0% | 0% | 0% | 0% | 0% | 0% |
| P2r B1 vs B2 | E3 sign-flipped | 60 | 0% | 0% | 0% | 0% | 0% | 2% [0, 6] |
| P2r B1 vs B2 | E3 sign-flipped | 125 | 0% | 0% | 0% | 0% | 0% | 14% [8, 16] |
| P2r B1 vs B2 | E3 sign-flipped | 250 | 0% | 0% | 0% | 0% | 0% | 25% [25, 25] |
| P3 B3 vs B1 | real pair | 60 | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | real pair | 125 | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | real pair | 250 | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | E2 demeaned | 60 | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | E2 demeaned | 125 | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | E2 demeaned | 250 | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | E3 sign-flipped | 60 | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | E3 sign-flipped | 125 | 0% | 0% | 0% | 0% | 0% | 0% |
| P3 B3 vs B1 | E3 sign-flipped | 250 | 0% | 0% | 0% | 0% | 0% | 0% |

## Synthetic: size and power by gain

Paths drawn by the stationary bootstrap from the P2 full history; the candidate has true mean skill `delta` against B1. Each cell is `test / gated` (standard error at most 1.1 points). The `delta = 0` row is size.

### (a1) the current test, critical values from circular blocks

| true skill | N=60 | N=125 | N=250 | N=500 |
|---|---|---|---|---|
| 0% | 7% / 7% | 8% / 8% | 9% / 9% | 8% / 8% |
| 3% | 9% / 9% | 10% / 10% | 10% / 10% | 12% / 12% |
| 5% | 11% / 11% | 12% / 12% | 13% / 13% | 14% / 14% |
| 7.5% | 10% / 10% | 13% / 13% | 15% / 15% | 18% / 18% |
| 10% | 11% / 11% | 16% / 16% | 19% / 19% | 22% / 22% |
| 15% | 15% / 15% | 19% / 19% | 25% / 25% | 33% / 33% |
| 20% | 18% / 18% | 24% / 24% | 30% / 30% | 42% / 42% |
| 30% | 22% / 22% | 33% / 33% | 45% / 45% | 62% / 62% |
| 40% | 27% / 27% | 42% / 42% | 56% / 56% | 76% / 76% |
| 50% | 31% / 31% | 50% / 50% | 69% / 69% | 88% / 88% |

### (a2) the current test, critical values matched to the paths (stationary bootstrap)

| true skill | N=60 | N=125 | N=250 | N=500 |
|---|---|---|---|---|
| 0% | 5% / 5% | 6% / 6% | 6% / 6% | 5% / 5% |
| 3% | 6% / 6% | 7% / 7% | 8% / 8% | 8% / 8% |
| 5% | 8% / 8% | 8% / 8% | 9% / 9% | 10% / 10% |
| 7.5% | 7% / 7% | 9% / 9% | 10% / 10% | 13% / 13% |
| 10% | 9% / 9% | 12% / 12% | 13% / 13% | 16% / 16% |
| 15% | 11% / 11% | 14% / 14% | 18% / 18% | 27% / 27% |
| 20% | 14% / 14% | 18% / 18% | 23% / 23% | 35% / 35% |
| 30% | 17% / 17% | 26% / 26% | 37% / 37% | 55% / 55% |
| 40% | 22% / 22% | 35% / 35% | 48% / 48% | 70% / 70% |
| 50% | 26% / 26% | 43% / 43% | 62% / 62% | 84% / 84% |

### (b) the self-normalised Diebold-Mariano test (fixed-b)

| true skill | N=60 | N=125 | N=250 | N=500 |
|---|---|---|---|---|
| 0% | 8% / 8% | 5% / 5% | 3% / 3% | 2% / 2% |
| 3% | 8% / 8% | 5% / 5% | 3% / 3% | 2% / 2% |
| 5% | 10% / 10% | 6% / 6% | 4% / 4% | 3% / 3% |
| 7.5% | 10% / 10% | 7% / 7% | 5% / 5% | 4% / 4% |
| 10% | 12% / 12% | 9% / 9% | 6% / 6% | 6% / 6% |
| 15% | 16% / 16% | 11% / 11% | 10% / 10% | 10% / 10% |
| 20% | 18% / 18% | 14% / 14% | 12% / 12% | 15% / 15% |
| 30% | 22% / 22% | 21% / 21% | 22% / 22% | 29% / 29% |
| 40% | 28% / 28% | 30% / 30% | 31% / 31% | 43% / 43% |
| 50% | 32% / 32% | 37% / 37% | 40% / 40% | 57% / 57% |

### (c1) the anytime-valid e-process, lead 1

| true skill | N=60 | N=125 | N=250 | N=500 |
|---|---|---|---|---|
| 0% | 0% / 0% | 0% / 0% | 0% / 0% | 0% / 0% |
| 3% | 0% / 0% | 0% / 0% | 0% / 0% | 0% / 0% |
| 5% | 0% / 0% | 0% / 0% | 0% / 0% | 0% / 0% |
| 7.5% | 0% / 0% | 0% / 0% | 0% / 0% | 0% / 0% |
| 10% | 0% / 0% | 0% / 0% | 0% / 0% | 0% / 0% |
| 15% | 0% / 0% | 0% / 0% | 0% / 0% | 0% / 0% |
| 20% | 0% / 0% | 0% / 0% | 0% / 0% | 0% / 0% |
| 30% | 0% / 0% | 0% / 0% | 0% / 0% | 0% / 0% |
| 40% | 0% / 0% | 0% / 0% | 0% / 0% | 0% / 0% |
| 50% | 0% / 0% | 0% / 0% | 0% / 0% | 0% / 0% |

### (c5) the anytime-valid e-process, mean of leads 1 to 5

| true skill | N=60 | N=125 | N=250 | N=500 |
|---|---|---|---|---|
| 0% | 0% / 0% | 0% / 0% | 0% / 0% | 0% / 0% |
| 3% | 0% / 0% | 0% / 0% | 0% / 0% | 0% / 0% |
| 5% | 0% / 0% | 0% / 0% | 0% / 0% | 0% / 0% |
| 7.5% | 0% / 0% | 0% / 0% | 0% / 0% | 0% / 0% |
| 10% | 0% / 0% | 0% / 0% | 0% / 0% | 0% / 0% |
| 15% | 0% / 0% | 0% / 0% | 0% / 0% | 0% / 0% |
| 20% | 0% / 0% | 0% / 0% | 0% / 0% | 0% / 0% |
| 30% | 0% / 0% | 0% / 0% | 0% / 0% | 0% / 0% |
| 40% | 0% / 0% | 0% / 0% | 0% / 0% | 0% / 0% |
| 50% | 0% / 0% | 0% / 0% | 0% / 0% | 0% / 0% |

### Synthetic by regime and day type

Test / gated at `N` = 60, 125 and 250 for a path drawn from one regime's days or one day-type cell (critical values of (a) still calibrated on the full history).

#### (a1) the current test, critical values from circular blocks

| history | N | size (0%) | 3% skill | 10% skill |
|---|---|---|---|---|
| full | 60 | 7% / 7% | 9% / 9% | 11% / 11% |
| full | 125 | 8% / 8% | 10% / 10% | 16% / 16% |
| full | 250 | 9% / 9% | 10% / 10% | 19% / 19% |
| 2018-19 | 60 | 0% / 0% | 0% / 0% | 0% / 0% |
| 2018-19 | 125 | 1% / 1% | 2% / 2% | 3% / 3% |
| 2018-19 | 250 | 3% / 3% | 5% / 5% | 10% / 10% |
| 2020-24 | 60 | 31% / 31% | 32% / 32% | 36% / 36% |
| 2020-24 | 125 | 32% / 32% | 33% / 33% | 38% / 38% |
| 2020-24 | 250 | 29% / 29% | 31% / 31% | 38% / 38% |
| 2025 | 60 | 21% / 21% | 22% / 22% | 28% / 28% |
| 2025 | 125 | 25% / 25% | 29% / 29% | 37% / 37% |
| 2025 | 250 | 25% / 25% | 29% / 29% | 41% / 41% |
| ordinary | 60 | 4% / 4% | 5% / 5% | 7% / 7% |
| ordinary | 125 | 4% / 4% | 7% / 7% | 10% / 10% |
| ordinary | 250 | 6% / 6% | 8% / 8% | 14% / 14% |
| pressure | 60 | 18% / 18% | 19% / 19% | 23% / 23% |
| pressure | 125 | 17% / 17% | 21% / 21% | 32% / 32% |
| pressure | 250 | 16% / 16% | 21% / 21% | 39% / 39% |

#### (a2) the current test, critical values matched to the paths (stationary bootstrap)

| history | N | size (0%) | 3% skill | 10% skill |
|---|---|---|---|---|
| full | 60 | 5% / 5% | 6% / 6% | 9% / 9% |
| full | 125 | 6% / 6% | 7% / 7% | 12% / 12% |
| full | 250 | 6% / 6% | 8% / 8% | 13% / 13% |
| 2018-19 | 60 | 0% / 0% | 0% / 0% | 0% / 0% |
| 2018-19 | 125 | 1% / 1% | 1% / 1% | 1% / 1% |
| 2018-19 | 250 | 2% / 2% | 3% / 3% | 6% / 6% |
| 2020-24 | 60 | 27% / 27% | 29% / 29% | 31% / 31% |
| 2020-24 | 125 | 28% / 28% | 29% / 29% | 33% / 33% |
| 2020-24 | 250 | 26% / 26% | 28% / 28% | 34% / 34% |
| 2025 | 60 | 18% / 18% | 18% / 18% | 24% / 24% |
| 2025 | 125 | 21% / 21% | 24% / 24% | 31% / 31% |
| 2025 | 250 | 23% / 23% | 25% / 25% | 37% / 37% |
| ordinary | 60 | 3% / 3% | 3% / 3% | 5% / 5% |
| ordinary | 125 | 3% / 3% | 4% / 4% | 7% / 7% |
| ordinary | 250 | 4% / 4% | 5% / 5% | 10% / 10% |
| pressure | 60 | 15% / 15% | 15% / 15% | 19% / 19% |
| pressure | 125 | 13% / 13% | 17% / 17% | 27% / 27% |
| pressure | 250 | 13% / 13% | 17% / 17% | 33% / 33% |

#### (b) the self-normalised Diebold-Mariano test (fixed-b)

| history | N | size (0%) | 3% skill | 10% skill |
|---|---|---|---|---|
| full | 60 | 8% / 8% | 8% / 8% | 12% / 12% |
| full | 125 | 5% / 5% | 5% / 5% | 9% / 9% |
| full | 250 | 3% / 3% | 3% / 3% | 6% / 6% |
| 2018-19 | 60 | 0% / 0% | 0% / 0% | 0% / 0% |
| 2018-19 | 125 | 0% / 0% | 0% / 0% | 1% / 1% |
| 2018-19 | 250 | 1% / 1% | 1% / 1% | 2% / 2% |
| 2020-24 | 60 | 28% / 28% | 29% / 29% | 34% / 34% |
| 2020-24 | 125 | 21% / 21% | 23% / 23% | 26% / 26% |
| 2020-24 | 250 | 15% / 15% | 17% / 17% | 21% / 21% |
| 2025 | 60 | 20% / 20% | 21% / 21% | 27% / 27% |
| 2025 | 125 | 18% / 18% | 20% / 20% | 27% / 27% |
| 2025 | 250 | 14% / 14% | 16% / 16% | 26% / 26% |
| ordinary | 60 | 4% / 4% | 5% / 5% | 8% / 8% |
| ordinary | 125 | 2% / 2% | 3% / 3% | 5% / 5% |
| ordinary | 250 | 1% / 1% | 2% / 2% | 4% / 4% |
| pressure | 60 | 17% / 17% | 17% / 17% | 22% / 22% |
| pressure | 125 | 10% / 10% | 13% / 13% | 22% / 22% |
| pressure | 250 | 8% / 8% | 11% / 11% | 23% / 23% |

#### (c1) the anytime-valid e-process, lead 1

| history | N | size (0%) | 3% skill | 10% skill |
|---|---|---|---|---|
| full | 60 | 0% / 0% | 0% / 0% | 0% / 0% |
| full | 125 | 0% / 0% | 0% / 0% | 0% / 0% |
| full | 250 | 0% / 0% | 0% / 0% | 0% / 0% |
| 2018-19 | 60 | 0% / 0% | 0% / 0% | 0% / 0% |
| 2018-19 | 125 | 0% / 0% | 0% / 0% | 0% / 0% |
| 2018-19 | 250 | 0% / 0% | 0% / 0% | 0% / 0% |
| 2020-24 | 60 | 0% / 0% | 0% / 0% | 0% / 0% |
| 2020-24 | 125 | 0% / 0% | 0% / 0% | 0% / 0% |
| 2020-24 | 250 | 0% / 0% | 0% / 0% | 0% / 0% |
| 2025 | 60 | 0% / 0% | 0% / 0% | 0% / 0% |
| 2025 | 125 | 9% / 9% | 11% / 11% | 14% / 14% |
| 2025 | 250 | 22% / 22% | 24% / 24% | 35% / 35% |
| ordinary | 60 | 0% / 0% | 0% / 0% | 0% / 0% |
| ordinary | 125 | 0% / 0% | 0% / 0% | 0% / 0% |
| ordinary | 250 | 0% / 0% | 0% / 0% | 0% / 0% |
| pressure | 60 | 0% / 0% | 0% / 0% | 0% / 0% |
| pressure | 125 | 0% / 0% | 1% / 1% | 2% / 2% |
| pressure | 250 | 4% / 4% | 7% / 7% | 16% / 16% |

#### (c5) the anytime-valid e-process, mean of leads 1 to 5

| history | N | size (0%) | 3% skill | 10% skill |
|---|---|---|---|---|
| full | 60 | 0% / 0% | 0% / 0% | 0% / 0% |
| full | 125 | 0% / 0% | 0% / 0% | 0% / 0% |
| full | 250 | 0% / 0% | 0% / 0% | 0% / 0% |
| 2018-19 | 60 | 0% / 0% | 0% / 0% | 0% / 0% |
| 2018-19 | 125 | 0% / 0% | 0% / 0% | 0% / 0% |
| 2018-19 | 250 | 0% / 0% | 0% / 0% | 0% / 0% |
| 2020-24 | 60 | 0% / 0% | 0% / 0% | 0% / 0% |
| 2020-24 | 125 | 0% / 0% | 0% / 0% | 0% / 0% |
| 2020-24 | 250 | 0% / 0% | 0% / 0% | 0% / 0% |
| 2025 | 60 | 0% / 0% | 0% / 0% | 0% / 0% |
| 2025 | 125 | 7% / 7% | 7% / 7% | 12% / 12% |
| 2025 | 250 | 21% / 21% | 23% / 23% | 34% / 34% |
| ordinary | 60 | 0% / 0% | 0% / 0% | 0% / 0% |
| ordinary | 125 | 0% / 0% | 0% / 0% | 0% / 0% |
| ordinary | 250 | 0% / 0% | 0% / 0% | 0% / 0% |
| pressure | 60 | 1% / 1% | 2% / 2% | 4% / 4% |
| pressure | 125 | 9% / 9% | 12% / 12% | 23% / 23% |
| pressure | 250 | 17% / 17% | 22% / 22% | 39% / 39% |

## What matching the null generator changes

Critical values of (a) at looks 2 and 3 on the P2 full history, and synthetic size and power at 3% skill.

| N | critical value, a1 (look 2 / 3) | a2 (look 2 / 3) | synthetic size, a1 → a2 | synthetic gated power at 3%, a1 → a2 |
|---|---|---|---|---|
| 60 | 5.66 / 1.98 | 7.45 / 2.18 | 7% → 5% | 9% → 6% |
| 125 | 3.17 / 1.51 | 3.76 / 1.73 | 8% → 6% | 10% → 7% |
| 250 | 2.62 / 1.34 | 2.88 / 1.52 | 9% → 6% | 10% → 8% |
| 500 | 2.01 / 1.30 | 2.49 / 1.42 | 8% → 5% | 12% → 8% |

## The smallest detectable gain at 80% power

The smallest `delta` on the grid (3% to 50%) at which the synthetic gated power is at least 80%; `none` means none on the grid.

| family | 125 days | 250 days | 500 days |
|---|---|---|---|
| (a1) the current test, critical values from circular blocks | none (test alone: none) | none (test alone: none) | 50% (test alone: 50%) |
| (a2) the current test, critical values matched to the paths (stationary bootstrap) | none (test alone: none) | none (test alone: none) | 50% (test alone: 50%) |
| (b) the self-normalised Diebold-Mariano test (fixed-b) | none (test alone: none) | none (test alone: none) | none (test alone: none) |
| (c1) the anytime-valid e-process, lead 1 | none (test alone: none) | none (test alone: none) | none (test alone: none) |
| (c5) the anytime-valid e-process, mean of leads 1 to 5 | none (test alone: none) | none (test alone: none) | none (test alone: none) |

## The e-process scale (post-hoc description, rule §9)

Over each pair's whole series. `mean / scale` is the daily average of the bounded bet; the last column is the day the e-process first reaches 20 when run from the first day.

| pair | reading | scale C (max abs d) | mean d | sd d | mean / C | mean / sd | first crossing (of 1868) |
|---|---|---|---|---|---|---|---|
| P2r B1 vs B2 | lead1 | 288 | 0.451 | 7.61 | 0.0016 | 0.06 | never |
| P2r B1 vs B2 | lead5 | 291 | 0.212 | 7.54 | 0.00073 | 0.03 | never |
| P2 B2 vs B1 | lead1 | 288 | -0.451 | 7.61 | -0.0016 | -0.06 | never |
| P2 B2 vs B1 | lead5 | 291 | -0.212 | 7.54 | -0.00073 | -0.03 | never |
| P3 B3 vs B1 | lead1 | 295 | 0.415 | 7.39 | 0.0014 | 0.06 | never |
| P3 B3 vs B1 | lead5 | 295 | 0.506 | 7.39 | 0.0017 | 0.07 | never |

### The arithmetic behind it

With independent days and a known standard deviation, a one-sided 5% test has 80% power when `n = (2.486 / s)^2`, `s` being the mean over the standard deviation of the daily difference. This is a calculation from the whole-series figures above, not a simulation; serial dependence and a studentized statistic need more days.

| pair | s (mean / sd, leads 1 to 5) | days at the pair's own gain | days if the gain were the 3% MME |
|---|---|---|---|
| P2 B2 vs B1 | -0.028 | the pair is worse than its benchmark | n/a |
| P2r B1 vs B2 | 0.028 | 7,831 days | 61,803 days |
| P3 B3 vs B1 | 0.068 | 1,320 days | 69,702 days |

## Reading (§7)

| family | size at most 5% everywhere | largest size among the seven checks | synthetic gated power at 3%, 250 days |
|---|---|---|---|
| (a2) the current test, critical values matched to the paths (stationary bootstrap) | no | 30% | 8% |
| (b) the self-normalised Diebold-Mariano test (fixed-b) | no | 23% | 3% |
| (c1) the anytime-valid e-process, lead 1 | yes | 0% | 0% |

Families holding the size limit: c1.

**Recommended by the rule: c1** ((c1) the anytime-valid e-process, lead 1).

Trade-off against the current design (a1, 250 days): synthetic gated power at 3% 10% → 0%; synthetic size 9% → 0%.

Smallest detectable gain at 250 days at 80% power: none on the grid (up to 50%).

**The pick has no useful power:** its synthetic gated power at 3% is 0%. It holds the size limit because it almost never flags anything, which is not a recommendation of a test that can confirm the MME.

## Sources read, and what they say

Read as abstracts only, on arXiv, on 15 October 2026; the full texts were not read, so what follows is limited to the abstracts.

- Henzi and Ziegel, *Valid sequential inference on probability forecast performance* (arXiv 2103.08402): the abstract is about **probability forecasts for binary events**, and its e-values are for score differences of such forecasts. It does not say that they cover the CRPS of a distribution forecast, so family (c) here is a betting e-process of the same kind applied to a CRPS difference, not their construction.
- Choe and Ramdas, *Comparing sequential forecasters* (arXiv 2110.00115): the abstract says the main theorems apply to **bounded scores**, with alternative methods for unbounded ones, and that the procedures test a weak null (better on average). Family (c) takes a declared bound `C` (the largest absolute difference in the development history) and a plug-in bet; it is not their variance-adaptive confidence sequence.
- Diebold and Mariano (1995), Giacomini and White (2006), Kiefer and Vogelsang: not fetched. The fixed-b value of (b) is simulated here on standard-normal series at the same lag, not taken from their tables.

## Questions for Eleonora (this page decides nothing)

1. **Is a confirmation test with no power at the MME acceptable to carry forward?** No family reaches 80% power at any gain up to 30% in 250 days, and (a) reaches it only at a 50% gain in 500 days. The arithmetic above says why: per day the signal is a small fraction of the noise, even for the 22% gain of B3. Whether to change the MME, the days or the target is hers; #769 re-runs the power study on the test in force.
2. **Is the current test's size acceptable?** Its per-comparison critical value is calibrated on a skewed series, so on a symmetric null (E3, the sign-flipped B3 pair) it flags 27% to 33% of windows, with the matched generator (a2) as well as without it. A symmetrised or recentred null would be a change to the protocol: a draft decision record, not code.
3. **Should family (c) be studied with a variance-adaptive confidence sequence?** As declared (a bound set by the largest difference in history) its bets are too small to cross in the whole history; a different construction is a different test, and one more step.
4. **The only known-better pair is B3 on development days.** The replay's power is for a gain of 22%, not 3%. Pairs with a known gain near the MME do not exist in the data held.
