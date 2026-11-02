# One rule for the cap, the tail and the probabilities: the law the candidate emits (#1389)

**Development data, not a verdict.** Hypothesis H5 (primary goal), registration design (forecast object), step 3; part of the H5 registration priority on #46. The candidate, (s3c-ann-net), does not change, nothing is registered or published, no record in `docs/runs/` is edited, and the two rules below sit behind a flag that is off by default (`repo_model.capped_law`). Panel digest `4ddc3882cd6d406b11e1088f8ff6195e16dde175a0ad6818abe40dd5bdac8999`. Walked at the 18:00 decision instant as #1314 did; the mean grid CRPS of the capped vector equals #1314's record to 1e-9 in both windows.

The design note, `docs/research/cap-tail-rule-1389-design.md`, states the distribution the candidate emits today and what the cap does to each part of it. This page scores three readings of the same quantiles: the **status quo** (`spread_mean_reversion.exceedance` on the capped vector); **(a)** a bounded law with an atom at the line (the uncapped law clipped at the line: calibrate, then cap, then read every probability from the clipped law); **(b)** the capped percentiles with an explicitly unbounded completion (calibrate, cap the percentiles, then complete the capped percentiles: an atom at the line, the last 1% running on above it).

## What the quantile scores show

The grid CRPS (primary) and the upper-tail twCRPS (key secondary) read the quantile vector, which is the capped vector under every rule, and the study checks that each rule's law has it as its quantiles at all 23 levels. The three rules score alike on both, by construction: the cap changes the quantiles, and the rule only decides what is said beyond them.

| window | decision days | cells | cells at full allotment | cells where the cap binds | mean grid CRPS | mean upper-tail twCRPS |
|---|---|---|---|---|---|---|
| 2026 | 165 | 825 | 825 | 404 | 1.6685 | 0.5142 |
| development | 1855 | 9275 | 50 | 50 | 1.6012 | 0.8447 |

## 2026 days (targets 2026-01-02 to 2026-09-03), shown apart

Brier scores (lower is better) are means of decision-day means over the group's cells. The difference is the status quo's score less the rule's, so a positive difference favours the rule; its interval is scoring protocol v1's studentized stationary bootstrap on mean d (seed 1389, 10000 draws), read as `gain`, `loss` or `undecided` from whether it excludes zero. A group of fewer than 20 decision days is not tested. † marks a bound taken from the resamples that have a long-run variance (#1239); the others are on all of them. Differences are shown in scientific notation because they are tiny.

**Brier P(> +5 bp)**

| group | cells | decision days | status quo | (a) | (b) | (a): status quo less rule | (b): status quo less rule |
|---|---|---|---|---|---|---|---|
| all cells | 825 | 165 | 0.035154 | 0.035154 | 0.035154 | -1.05e-09 [-1.92e-09, -2.06e-10]: loss † | +1.02e-07 [+5.69e-08, +1.71e-07]: gain |
| target days at full allotment | 825 | 165 | 0.035154 | 0.035154 | 0.035154 | -1.05e-09 [-1.92e-09, -2.06e-10]: loss † | +1.02e-07 [+5.69e-08, +1.71e-07]: gain |
| the cap binds (the uncapped q99 is above the line) | 404 | 112 | 0.065825 | 0.065825 | 0.065825 | -1.54e-09 [-2.79e-09, -3.10e-10]: loss † | +1.76e-07 [+1.67e-08, +2.76e-07]: gain |

**Brier P(> +10 bp)**

| group | cells | decision days | status quo | (a) | (b) | (a): status quo less rule | (b): status quo less rule |
|---|---|---|---|---|---|---|---|
| all cells | 825 | 165 | 0.000006 | 0.000000 | 0.000007 | +5.98e-06 [+3.45e-06, +1.01e-05]: gain | -1.18e-06 [-3.49e-06, -3.84e-07]: loss |
| target days at full allotment | 825 | 165 | 0.000006 | 0.000000 | 0.000007 | +5.98e-06 [+3.45e-06, +1.01e-05]: gain | -1.18e-06 [-3.49e-06, -3.84e-07]: loss |
| the cap binds (the uncapped q99 is above the line) | 404 | 112 | 0.000013 | 0.000000 | 0.000015 | +1.29e-05 [+8.00e-06, +1.95e-05]: gain | -1.88e-06 [-4.55e-06, -7.08e-07]: loss |

**Brier P(> line)**

| group | cells | decision days | status quo | (a) | (b) | (a): status quo less rule | (b): status quo less rule |
|---|---|---|---|---|---|---|---|
| all cells | 825 | 165 | 0.000006 | 0.000000 | 0.000007 | +5.98e-06 [+3.45e-06, +1.01e-05]: gain | -1.18e-06 [-3.49e-06, -3.84e-07]: loss |
| target days at full allotment | 825 | 165 | 0.000006 | 0.000000 | 0.000007 | +5.98e-06 [+3.45e-06, +1.01e-05]: gain | -1.18e-06 [-3.49e-06, -3.84e-07]: loss |
| the cap binds (the uncapped q99 is above the line) | 404 | 112 | 0.000013 | 0.000000 | 0.000015 | +1.29e-05 [+8.00e-06, +1.95e-05]: gain | -1.88e-06 [-4.55e-06, -7.08e-07]: loss |

**Exceedances: outcomes above the threshold against the sum of the probabilities** (calibration in the large; shown, not tested)

| event | cells | outcomes above | status quo | (a) | (b) |
|---|---|---|---|---|---|
| above +5 bp, all cells | 825 | 21 | 73.847 | 73.847 | 73.847 |
| above +5 bp, at full allotment | 825 | 21 | 73.847 | 73.847 | 73.847 |
| above +10 bp, all cells | 825 | 0 | 0.889 | 0.000 | 1.108 |
| above +10 bp, at full allotment | 825 | 0 | 0.889 | 0.000 | 1.108 |
| above the line, at full allotment | 825 | 0 | 0.889 | 0.000 | 1.108 |
| above the line, the cap binds | 404 | 0 | 0.650 | 0.000 | 0.869 |

**The cells by the number of upper levels the cap changes** (cells at full allotment; the status quo's probability depends on this number, which is the incoherence the design note describes)

| levels changed | cells | share of outcomes above +10 bp | mean P(> +10 bp): status quo | (a) | (b) | cells where the status quo's P(> +10 bp) is under 1e-6 | mean tail above the line (bp): status quo | (a) | (b) |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 421 | 0.0000 | 0.00057 | 0.00000 | 0.00057 | 355 | 0.1979 | 0.0000 | 0.1979 |
| 1 | 184 | 0.0000 | 0.00353 | 0.00000 | 0.00353 | 60 | 0.9198 | 0.0000 | 0.9198 |
| 2-3 | 166 | 0.0000 | 0.00000 | 0.00000 | 0.00132 | 166 | 0.0000 | 0.0000 | 0.4763 |
| 4+ | 54 | 0.0000 | 0.00000 | 0.00000 | 0.00000 | 54 | 0.0000 | 0.0000 | 0.2039 |

**Randomized PIT** on the cells at full allotment (whole-basis-point outcomes, one draw per cell from `random.Random(1389)`), cells per tenth of [0, 1]; a calibrated law is flat. Shown, not tested.

| rule | 0.0-0.1 | 0.1-0.2 | 0.2-0.3 | 0.3-0.4 | 0.4-0.5 | 0.5-0.6 | 0.6-0.7 | 0.7-0.8 | 0.8-0.9 | 0.9-1.0 |
|---|---|---|---|---|---|---|---|---|---|---|
| status quo (the candidate as run) | 101 | 118 | 81 | 74 | 77 | 79 | 75 | 87 | 77 | 56 |
| (a) bounded, atom at the line | 106 | 110 | 94 | 79 | 63 | 84 | 72 | 91 | 68 | 58 |
| (b) capped percentiles, open tail | 103 | 122 | 83 | 61 | 79 | 85 | 62 | 104 | 69 | 57 |

**By regime and by pressure-day type of the target day: Brier P(> +10 bp)**

| group | cells | decision days | status quo | (a) | (b) | (a): status quo less rule | (b): status quo less rule |
|---|---|---|---|---|---|---|---|
| 2025-26 | 825 | 165 | 0.000006 | 0.000000 | 0.000007 | +5.98e-06 [+3.45e-06, +1.01e-05]: gain | -1.18e-06 [-3.49e-06, -3.84e-07]: loss |
| ordinary | 717 | 165 | 0.000006 | 0.000000 | 0.000007 | +6.00e-06 [+3.25e-06, +1.02e-05]: gain | -1.35e-06 [-4.53e-06, -4.25e-07]: loss |
| quarter_end_turn | 20 | 12 | 0.000006 | 0.000000 | 0.000007 | not tested | not tested |
| tax_date | 30 | 15 | 0.000008 | 0.000000 | 0.000011 | not tested | not tested |
| turn | 57 | 34 | 0.000004 | 0.000000 | 0.000004 | +3.58e-06 [-4.71e-07, +1.48e-05]: undecided † | -5.07e-08 [-9.90e-08, -3.33e-10]: loss † |
| year_end | 1 | 1 | 0.000000 | 0.000000 | 0.000000 | not tested | not tested |

**By regime and by pressure-day type of the target day: Brier P(> +5 bp)**

| group | cells | decision days | status quo | (a) | (b) | (a): status quo less rule | (b): status quo less rule |
|---|---|---|---|---|---|---|---|
| 2025-26 | 825 | 165 | 0.035154 | 0.035154 | 0.035154 | -1.05e-09 [-1.92e-09, -2.06e-10]: loss † | +1.02e-07 [+5.69e-08, +1.71e-07]: gain |
| ordinary | 717 | 165 | 0.025984 | 0.025984 | 0.025984 | -1.91e-09 [-6.39e-09, -1.33e-10]: loss † | +1.04e-07 [+5.32e-08, +1.86e-07]: gain |
| quarter_end_turn | 20 | 12 | 0.047126 | 0.047126 | 0.047125 | not tested | not tested |
| tax_date | 30 | 15 | 0.189637 | 0.189637 | 0.189637 | not tested | not tested |
| turn | 57 | 34 | 0.062822 | 0.062822 | 0.062822 | identical | +3.90e-08 [-6.06e-07, +2.10e-07]: undecided |
| year_end | 1 | 1 | 0.393637 | 0.393637 | 0.393638 | not tested | not tested |

## Development window (targets up to 2025-12-31; the near-blind tier is not in it)

Brier scores (lower is better) are means of decision-day means over the group's cells. The difference is the status quo's score less the rule's, so a positive difference favours the rule; its interval is scoring protocol v1's studentized stationary bootstrap on mean d (seed 1389, 10000 draws), read as `gain`, `loss` or `undecided` from whether it excludes zero. A group of fewer than 20 decision days is not tested. † marks a bound taken from the resamples that have a long-run variance (#1239); the others are on all of them. Differences are shown in scientific notation because they are tiny.

**Brier P(> +5 bp)**

| group | cells | decision days | status quo | (a) | (b) | (a): status quo less rule | (b): status quo less rule |
|---|---|---|---|---|---|---|---|
| all cells | 9275 | 1855 | 0.046102 | 0.046102 | 0.046102 | identical | +7.30e-10 [-3.26e-10, +3.56e-09]: undecided † |
| target days at full allotment | 50 | 10 | 0.128748 | 0.128748 | 0.128748 | not tested | not tested |
| the cap binds (the uncapped q99 is above the line) | 50 | 10 | 0.128748 | 0.128748 | 0.128748 | not tested | not tested |

**Brier P(> +10 bp)**

| group | cells | decision days | status quo | (a) | (b) | (a): status quo less rule | (b): status quo less rule |
|---|---|---|---|---|---|---|---|
| all cells | 9275 | 1855 | 0.027009 | 0.027009 | 0.027008 | identical | +7.15e-07 [-1.18e-07, +9.84e-04]: undecided † |
| target days at full allotment | 50 | 10 | 0.160000 | 0.160000 | 0.159867 | not tested | not tested |
| the cap binds (the uncapped q99 is above the line) | 50 | 10 | 0.160000 | 0.160000 | 0.159867 | not tested | not tested |

**Brier P(> line)**

| group | cells | decision days | status quo | (a) | (b) | (a): status quo less rule | (b): status quo less rule |
|---|---|---|---|---|---|---|---|
| all cells | 9275 | 10 | 0.160000 | 0.160000 | 0.159867 | not tested | not tested |
| target days at full allotment | 50 | 10 | 0.160000 | 0.160000 | 0.159867 | not tested | not tested |
| the cap binds (the uncapped q99 is above the line) | 50 | 10 | 0.160000 | 0.160000 | 0.159867 | not tested | not tested |

**Exceedances: outcomes above the threshold against the sum of the probabilities** (calibration in the large; shown, not tested)

| event | cells | outcomes above | status quo | (a) | (b) |
|---|---|---|---|---|---|
| above +5 bp, all cells | 9275 | 680 | 880.313 | 880.313 | 880.313 |
| above +5 bp, at full allotment | 50 | 13 | 18.850 | 18.850 | 18.850 |
| above +10 bp, all cells | 9275 | 293 | 388.998 | 388.998 | 389.005 |
| above +10 bp, at full allotment | 50 | 8 | 0.000 | 0.000 | 0.006 |
| above the line, at full allotment | 50 | 8 | 0.000 | 0.000 | 0.006 |
| above the line, the cap binds | 50 | 8 | 0.000 | 0.000 | 0.006 |

**The cells by the number of upper levels the cap changes** (cells at full allotment; the status quo's probability depends on this number, which is the incoherence the design note describes)

| levels changed | cells | share of outcomes above +10 bp | mean P(> +10 bp): status quo | (a) | (b) | cells where the status quo's P(> +10 bp) is under 1e-6 | mean tail above the line (bp): status quo | (a) | (b) |
|---|---|---|---|---|---|---|---|---|---|
| 2-3 | 3 | 0.0000 | 0.00000 | 0.00000 | 0.00000 | 3 | 0.0000 | 0.0000 | 0.1923 |
| 4+ | 47 | 0.1702 | 0.00000 | 0.00000 | 0.00014 | 47 | 0.0000 | 0.0000 | 0.2250 |

**Randomized PIT** on the cells at full allotment (whole-basis-point outcomes, one draw per cell from `random.Random(1389)`), cells per tenth of [0, 1]; a calibrated law is flat. Shown, not tested.

| rule | 0.0-0.1 | 0.1-0.2 | 0.2-0.3 | 0.3-0.4 | 0.4-0.5 | 0.5-0.6 | 0.6-0.7 | 0.7-0.8 | 0.8-0.9 | 0.9-1.0 |
|---|---|---|---|---|---|---|---|---|---|---|
| status quo (the candidate as run) | 0 | 0 | 2 | 7 | 6 | 11 | 11 | 4 | 0 | 9 |
| (a) bounded, atom at the line | 0 | 0 | 2 | 9 | 6 | 10 | 9 | 6 | 0 | 8 |
| (b) capped percentiles, open tail | 0 | 0 | 4 | 6 | 8 | 10 | 8 | 6 | 0 | 8 |

**By regime and by pressure-day type of the target day: Brier P(> +10 bp)**

| group | cells | decision days | status quo | (a) | (b) | (a): status quo less rule | (b): status quo less rule |
|---|---|---|---|---|---|---|---|
| 2018-19 | 1795 | 361 | 0.087520 | 0.087520 | 0.087520 | identical | identical |
| 2020 | 1255 | 255 | 0.014518 | 0.014518 | 0.014518 | identical | identical |
| 2021-23 | 3740 | 752 | 0.000031 | 0.000031 | 0.000031 | identical | identical |
| 2024 | 1250 | 254 | 0.009632 | 0.009632 | 0.009632 | identical | identical |
| 2025-26 | 1235 | 249 | 0.050935 | 0.050935 | 0.050930 | identical | +5.33e-06 [-1.27e-06, +7.47e-03]: undecided † |
| ordinary | 7939 | 1855 | 0.023592 | 0.023592 | 0.023592 | identical | -5.31e-10 [-7.04e-10, +8.67e-11]: undecided † |
| quarter_end_turn | 220 | 132 | 0.086011 | 0.086011 | 0.086011 | identical | identical |
| tax_date | 445 | 214 | 0.040200 | 0.040200 | 0.040200 | identical | identical |
| turn | 600 | 360 | 0.039758 | 0.039758 | 0.039758 | identical | identical |
| year_end | 71 | 43 | 0.086571 | 0.086571 | 0.086416 | identical | +1.54e-04 [-1.34e-05, +1.54e-04]: undecided † |

**By regime and by pressure-day type of the target day: Brier P(> +5 bp)**

| group | cells | decision days | status quo | (a) | (b) | (a): status quo less rule | (b): status quo less rule |
|---|---|---|---|---|---|---|---|
| 2018-19 | 1795 | 361 | 0.165071 | 0.165071 | 0.165071 | identical | identical |
| 2020 | 1255 | 255 | 0.022464 | 0.022464 | 0.022464 | identical | identical |
| 2021-23 | 3740 | 752 | 0.000169 | 0.000169 | 0.000169 | identical | identical |
| 2024 | 1250 | 254 | 0.018146 | 0.018146 | 0.018146 | identical | identical |
| 2025-26 | 1235 | 249 | 0.064501 | 0.064501 | 0.064501 | identical | +5.44e-09 [-2.52e-09, +2.60e-08]: undecided † |
| ordinary | 7939 | 1855 | 0.045267 | 0.045267 | 0.045267 | identical | +6.39e-10 [-4.05e-10, +2.98e-09]: undecided † |
| quarter_end_turn | 220 | 132 | 0.095039 | 0.095039 | 0.095039 | identical | identical |
| tax_date | 445 | 214 | 0.055237 | 0.055237 | 0.055237 | identical | +1.19e-08 [-2.97e-09, +4.20e-08]: undecided † |
| turn | 600 | 360 | 0.038925 | 0.038925 | 0.038925 | identical | identical |
| year_end | 71 | 43 | 0.058271 | 0.058271 | 0.058271 | identical | identical |

## What it shows, and what it does not

- The three rules score alike on the grid and the upper-tail scores because they share the quantiles. They differ in what they say beyond the line, and the Brier scores on the events beyond it are close to zero under every rule: the differences above are of the order of a hundred-thousandth, far below the Brier score of P(> +5 bp). The choice of rule is not decided by these scores.
- The status quo's probability above the line depends on how many upper levels the cap changed (the table of cells by levels changed): one level leaves a probability of a few thousandths, two or more leave almost none. Rules (a) and (b) do not.
- (a) says nothing lies above the line. (b) says at most 1% does, and where the cap changes four or more levels its tail above the line runs a fraction of a basis point, so that on whole basis points its P(> +10 bp) is also almost zero. A tail that matters at the line would need a tail scale published with the percentiles; (b) as built has none.
- On the development window the cells at full allotment are few and come from a short stretch of days; outcomes above the line occur there and every rule gives them almost no probability. On the 2026 days none does. Neither window carries a rate that could be read as a verdict, and the 2026 days have been seen.
- Not done: the live-record hook, the registration text, any change to the cap, to `s3c_candidate` or to the published scoring of the candidate. Walked at the 18:00 instant only.

## Question for Eleonora

**Which rule does the registration freeze for the candidate's quantiles, probabilities and PIT?** Her ruling is needed; nothing here is settled in code.

1. **(b), the capped percentiles with an open completion** (the recommendation). The registration states: the quantiles are capped at the line on target days at full allotment, calibration comes before the cap, and every probability and PIT is read from the capped percentiles with an atom at the line and the last 1% running on above it. No claim that the tail beyond the line is impossible.
2. **(a), the bounded law with an atom at the line.** The same order, with the uncapped law clipped at the line, so P(> line) is zero by rule. It claims that nothing lies above the facility's minimum bid; outcomes above it have occurred in the development window.
3. **(b) with a published tail scale.** As 1, with the scale of the completion above the line registered beside the percentiles (as built, it is a fraction of a basis point where the cap changes four or more levels). A later directive would design it.
4. **Keep the status quo.** No rule is frozen; the probabilities stay as the published code reads them, and the incoherence stays.

**Default if she has not answered by the next 5 pm batch: 1.** It follows #1361's result as it stands: [the candidate without the cap, scored beside the candidate](https://github.com/eleonorabjornberg/repo-market-model/pull/1376) is an open pull request whose description reports that the uncapped version loses to the candidate on the 2026 days (grid CRPS and upper-tail twCRPS) and is undecided on the development window, so the uncapped law is not shown to be no worse and the recommendation, (b), holds. The default is re-read when that pull request is merged or changes. It changes no flag and no claim: both rules stay off.

