# Why (s3c-ann-net) loses three times: a diagnosis of #1288's record (#1319)

**Hypothesis and step:** H5 (the SOFR - IORB spread distribution), step 3, the candidate (s3c-ann-net). Development tier: a diagnosis of a record that exists, never a verdict. Nothing is registered or published, no arm, record or declaration changes, and no lockbox day is scored. Her ruling of 30 October 2026 (ledger item 79). The findings are #1316; #1316, #1317 and #1318 stay open.

**What was done.** #1288's frames, walks and forecasts were rebuilt exactly as merged (`scripts/s3c_announced_settlement_1288.py`, no new fit) on the published panel `4ddc3882...`, and every pooled, lead and regime mean of (s3c), (s3c-ann) and (s3c-ann-net), on all three scores, was checked equal to #1288's record to 1e-9 (the study refuses to write otherwise). The tables are declared in `metadata/s3c_ann_net_diagnosis_1319.json`, committed before any table was computed. Intervals are 90% stationary-bootstrap intervals (mean block 10, 2000 replications, seed 1319) over days in date order: a diagnostic interval on mean d, not scoring protocol v1's studentized test. A difference d is the arm less the reference, so **a positive d is a loss for the arm**. Every reading is taken from the development window (targets to 2025-12-31); the 2026 days are shown at the end and decide nothing. Cells are (decision day, lead) pairs; 'days' are the units the interval resamples.

**Amendments to the declaration** (recorded after a scratch run of the tables; none changes a figure):

- Recorded after the first run of the tables (a scratch run, kept only to write the page; no figure was changed by any item and the declared run was repeated from the committed file). 1. Table 1's net-to-gross classes: a sixth class, 'mixed legs' (one settling leg below half of gross and another at or above it), holds the cells that match none of the five declared classes; the five are unchanged.
- 2. Table 2's reading of H-a is coded as supported when the interval of g + m lies above zero (the condition on the net-only form's mean squared residual not being below the full form's is always met, the net-only form being nested in the full one); not supported when the interval of g + m lies below zero, or contains zero while the interval of mse(gross only) - mse(net only) lies above zero; otherwise undecided.
- 3. Table 4's reading of H-b is coded as: the interval of the 2020 bias less the 2018-19 bias lies below zero, the highest-third-size group at states 1 to 2 (state 0 has too few days) reads a loss on grid CRPS, and no other group of states 0 and 1 to 2 with at least 20 days reads a loss on grid CRPS; not supported when that interval lies above zero or the highest-third group reads a gain; otherwise undecided. The dating is read as ruled out when the 2020 loss with the immediate-release days left out still reads a loss on grid CRPS.
- 4. The settlement-day bias difference of 2020 and 2018-19 is bootstrapped over all decision days of the window in date order (the regimes resampled together), not over the two regimes' days alone.
- 5. Table 2 is also computed on the 2026 days, which the page does not print.

## Answers: why does it do this?

Each reading below is computed from the intervals by the declared rule; the mechanisms are the orchestrating session's hypotheses, tested here, not established.

**1. Lead 1, against (s3c).** The loss is on the Brier score of P(> +5 bp) (-6.5%, d +0.003 [+0.001, +0.004] **loss**), and it is not where hypothesis H-a puts it. On the highest third of maturing share (the days where netting removes most of the gross) (s3c-ann-net) is a **gain** (+1.9%, d -0.026 [-0.046, -0.007] **gain**); the Brier loss sits on days with the lowest maturing share (-28.8%, d +0.011 [+0.002, +0.023] **loss**) and on days with no settlement at all (-5.0%, d +0.002 [+0.001, +0.003] **loss**; grid CRPS -1.7%, d +0.019 [+0.008, +0.031] **loss**). On days with no settlement both arms add nothing for settlement, so that loss comes from the rest of the refit, not from how a settlement is sized. By realised event, the net arm gives a lower probability on the days the spread went above +5 bp (mean 0.561 against the flag's 0.604, on 134 cells) and nearly the same on the others, so it is a little less sharp on pressure days.

**H-a (gross, not net), the regression.** On coupon settlement days the maturing amount does not offset the gross amount one for one: g + m at lead 1 is +1.59 bp per USD 100 bn [+0.81, +2.67], **supported**; at lead 3 +1.31 [+0.53, +2.31], **supported**. For the bill leg it is **undecided** at lead 1 (-0.51 [-1.46, +0.23]) and **undecided** at lead 3 (-0.53 [-1.83, +0.50]). So: supported for the coupon leg, undecided for the bill leg, and not a reason for the lead-1 loss, which is not on the large-maturing days.

**2. 2020, against (s3c).** Both announced arms lose on grid CRPS ((s3c-ann) -4.1%, d +0.060 [+0.016, +0.120] **loss**; (s3c-ann-net) -2.0%, d +0.029 [+0.002, +0.064] **loss**), and the loss is mostly March to June (shares +81.7% and +78.6%): the rest of 2020 is undecided for both. In 2020 the realised spread on settlement target days is +0.28 bp above the others [-0.39, +1.12], against a fitted settlement shift of +0.95 bp for the flag and +0.49 bp for the net: both arms still add a settlement premium that 2020 did not pay. **H-b: (s3c-ann) supported, (s3c-ann-net) undecided.** For the flag arm the loss sits on the highest third of settlement size at states 1 to 2 (loss) and nowhere else at states 0 to 2; for the net arm that cell is undecided and another cell of states 0 to 2 is a loss. The scarcity state the model reads was almost never 0 in 2020 (nearly all settlement cells are at states 1 to 3), so the 'abundant reserves' reading of 2020 cannot be tested on that state. **The dating is ruled out as the cause for the flag arm** (2020 without the immediate-release days: -4.0%, d +0.059 [+0.019, +0.104] **loss**) **and not ruled out for the net arm** (without them -0.9%, d +0.013 [-0.011, +0.037] **undecided**; those days carry +67.5% of the net arm's 2020 loss, +29.4% of the flag arm's).

**3. Net against flag.** The net arm loses on the Brier score at every lead (-6.5%, -4.5%, -4.5%, -3.7%, -3.8% at h = 1..5, all losses on the interval) and the loss is on the days the spread went above +5 bp: at h = 3 the Brier difference summed over those 136 cells is +3.75, over the other 1719 cells -0.007; the net arm gives those days a probability of 0.513 against the flag's 0.554. In 2018-19, where it loses on all three scores (-1.7%, d +0.061 [+0.009, +0.113] **loss**), the realised settlement-day premium was +6.0 bp [+3.3, +9.3], the flag arm's fitted shift +2.02 bp and the net arm's +0.48 bp: netting shrinks the regressor, so the fitted size effect buys a fraction of what the flag buys when pressure is large and settlement-driven. That is H-a's direction (netting understates the squeeze), shown on the regime where the settlement premium was large; the maturing amounts are not separated from the shrinkage here. In 2020, 2024 and 2025-26 the net arm is ahead of the flag on grid CRPS (gains on the interval).

## Table 1. Where the lead-1 loss of (s3c-ann-net) against (s3c) sits (development window)

At lead 1 the flag arm is (s3c) cell for cell, and the net arm is #1273's (s3c-net). One cell per decision day.

### All lead-1 cells and by target-day type

| group | cells | days | share of the loss | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|---|---|
| all lead-1 cells | 1855 | 1855 | +100.0% | -0.3%, d +0.005 [-0.010, +0.019] **undecided** | -1.4%, d +0.011 [-0.000, +0.023] **undecided** | -6.5%, d +0.003 [+0.001, +0.004] **loss** |
| bill settlement day | 775 | 775 | +81.6% | -0.5%, d +0.009 [-0.009, +0.029] **undecided** | -0.5%, d +0.005 [-0.006, +0.018] **undecided** | -1.8%, d +0.001 [-0.001, +0.003] **undecided** |
| bill settlement day with a cash management bill | 352 | 352 | +25.2% | -0.7%, d +0.006 [-0.015, +0.034] **undecided** | -3.3%, d +0.005 [-0.000, +0.011] **undecided** | -4.3%, d +0.000 [+0.000, +0.001] **loss** |
| bill settlement day without one | 423 | 423 | +56.4% | -0.5%, d +0.012 [-0.017, +0.038] **undecided** | -0.3%, d +0.005 [-0.015, +0.027] **undecided** | -1.6%, d +0.001 [-0.002, +0.005] **undecided** |
| coupon settlement day | 240 | 240 | -45.4% | +0.9%, d -0.017 [-0.141, +0.121] **undecided** | -2.9%, d +0.036 [-0.052, +0.136] **undecided** | -37.2%, d +0.017 [+0.001, +0.038] **loss** |
| neither settles | 912 | 912 | +200.5% | -1.7%, d +0.019 [+0.008, +0.031] **loss** | -4.8%, d +0.022 [+0.011, +0.033] **loss** | -5.0%, d +0.002 [+0.001, +0.003] **loss** |

### By the net-to-gross class of the target day, as announced at the decision

| class | cells | days | share of the loss | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|---|---|
| mixed legs | 17 | 17 | +73.4% | -30.1%, d +0.378 not read **not read** | -64.4%, d +0.340 not read **not read** | -329.5%, d +0.029 not read **not read** |
| net at or above half of gross | 130 | 130 | -125.2% | +5.2%, d -0.084 [-0.215, +0.034] **undecided** | +5.3%, d -0.047 [-0.153, +0.039] **undecided** | -24.0%, d +0.012 [-0.002, +0.031] **undecided** |
| net at or below zero | 348 | 348 | -86.5% | +1.6%, d -0.022 [-0.049, +0.006] **undecided** | +1.3%, d -0.009 [-0.025, +0.009] **undecided** | +6.1%, d -0.002 [-0.004, -0.000] **gain** |
| net below half of gross | 448 | 448 | +37.9% | -0.3%, d +0.007 [-0.016, +0.035] **undecided** | -0.6%, d +0.010 [-0.009, +0.033] **undecided** | -10.0%, d +0.004 [+0.001, +0.009] **loss** |
| no settlement | 912 | 912 | +200.5% | -1.7%, d +0.019 [+0.008, +0.031] **loss** | -4.8%, d +0.022 [+0.011, +0.033] **loss** | -5.0%, d +0.002 [+0.001, +0.003] **loss** |

### By maturing share of gross (thirds fixed on the development window's settlement target days; cuts 0.828 and 1.000)

| group | cells | days | share of the loss | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|---|---|
| highest third | 315 | 315 | -91.8% | +1.9%, d -0.026 [-0.046, -0.007] **gain** | +2.6%, d -0.017 [-0.030, -0.006] **gain** | +6.5%, d -0.003 [-0.005, -0.001] **gain** |
| lowest third of maturing share | 314 | 314 | +1.3% | -0.0%, d +0.000 [-0.076, +0.082] **undecided** | -2.2%, d +0.022 [-0.032, +0.080] **undecided** | -28.8%, d +0.011 [+0.002, +0.023] **loss** |
| middle third | 314 | 314 | -10.0% | +0.1%, d -0.003 [-0.024, +0.022] **undecided** | +0.1%, d -0.002 [-0.016, +0.016] **undecided** | -2.6%, d +0.001 [-0.001, +0.004] **undecided** |

## Table 2. H-a: gross, maturing or net on the settlement target days (development window)

Residual r = y - median of the flag arm's forecast at that lead, in bp, on the target days where the leg settles with its class fully announced at the decision. r = a + g gross + m maturing + o other-leg-settles; gross and maturing in USD 100 bn. If netting were the whole story m = -g and g + m = 0. The last-but-one column is the in-sample mean squared residual of the gross-only, net-only and both forms. Intervals: stationary bootstrap over target days, refitting at every resample.


### Lead 1, coupon leg

| scarcity state | target days | gross g | maturing m | g + m | net alone n | mean squared residual: gross only / net only / both | H-a |
|---|---|---|---|---|---|---|---|
| 0 (abundant) | 135 | +1.25 [+0.03, +2.81] | -0.63 [-2.40, +0.61] | +0.62 [+0.13, +1.03] | +1.42 [+0.18, +2.99] | 3.90 / 3.97 / 3.87 | **supported** |
| 1 to 2 | 47 | -1.09 [-2.13, +0.68] | +3.03 [+0.68, +5.88] | +1.94 [+0.67, +4.53] | -0.32 [-1.19, +1.63] | 15.18 / 15.29 / 14.71 | **supported** |
| 3 (scarce) | 58 | +15.22 [+8.89, +25.83] | -11.00 [-19.67, -5.26] | +4.22 [+1.61, +8.53] | +17.22 [+9.88, +28.82] | 88.28 / 88.64 / 85.49 | **supported** |
| no state | 0 | not fitted: fewer than 20 target days |  |  |  |  |  |
| pooled | 240 | +0.61 [-0.98, +2.71] | +0.98 [-1.39, +3.17] | +1.59 [+0.81, +2.67] | +1.11 [-0.40, +3.25] | 30.27 / 30.79 / 30.21 | **supported** |

### Lead 1, bill leg

| scarcity state | target days | gross g | maturing m | g + m | net alone n | mean squared residual: gross only / net only / both | H-a |
|---|---|---|---|---|---|---|---|
| 0 (abundant) | 440 | +0.29 [-0.19, +0.75] | -0.10 [-0.72, +0.59] | +0.19 [-0.11, +0.46] | +0.20 [-0.36, +0.72] | 5.08 / 5.10 / 5.08 | **undecided** |
| 1 to 2 | 159 | +1.60 [+0.80, +2.56] | -0.34 [-2.10, +1.03] | +1.26 [-0.03, +2.36] | +0.95 [-0.17, +2.34] | 7.48 / 7.96 / 7.47 | **undecided** |
| 3 (scarce) | 176 | -3.25 [-13.61, +3.25] | +1.55 [-3.98, +12.25] | -1.70 [-3.26, +1.71] | -2.53 [-12.82, +3.36] | 626.67 / 627.48 / 626.61 | **undecided** |
| no state | 0 | not fitted: fewer than 20 target days |  |  |  |  |  |
| pooled | 775 | -0.16 [-1.54, +1.05] | -0.34 [-1.37, +0.67] | -0.51 [-1.46, +0.23] | +0.05 [-1.06, +1.08] | 147.80 / 147.89 / 147.80 | **undecided** |

### Lead 3, coupon leg

| scarcity state | target days | gross g | maturing m | g + m | net alone n | mean squared residual: gross only / net only / both | H-a |
|---|---|---|---|---|---|---|---|
| 0 (abundant) | 131 | +1.55 [+0.16, +3.26] | -1.05 [-3.03, +0.49] | +0.50 [-0.01, +0.92] | +1.65 [+0.27, +3.31] | 5.35 / 5.33 / 5.27 | **undecided** |
| 1 to 2 | 47 | -2.07 [-3.16, -0.32] | +4.54 [+1.74, +6.66] | +2.47 [+0.93, +3.73] | -0.95 [-1.93, +0.67] | 12.50 / 12.46 / 11.38 | **supported** |
| 3 (scarce) | 59 | +15.95 [+8.94, +27.88] | -12.95 [-23.60, -5.81] | +3.00 [-0.01, +7.55] | +17.25 [+9.94, +29.93] | 110.19 / 108.12 / 106.51 | **undecided** |
| no state | 0 | not fitted: fewer than 20 target days |  |  |  |  |  |
| pooled | 237 | +0.80 [-0.84, +3.08] | +0.52 [-2.10, +2.69] | +1.31 [+0.53, +2.31] | +1.18 [-0.34, +3.44] | 35.04 / 35.42 / 35.02 | **supported** |

### Lead 3, bill leg

| scarcity state | target days | gross g | maturing m | g + m | net alone n | mean squared residual: gross only / net only / both | H-a |
|---|---|---|---|---|---|---|---|
| 0 (abundant) | 439 | +0.30 [-0.39, +0.95] | -0.01 [-0.85, +0.91] | +0.29 [-0.12, +0.69] | +0.19 [-0.59, +0.90] | 6.02 / 6.05 / 6.02 | **undecided** |
| 1 to 2 | 155 | +3.19 [+1.99, +4.56] | -1.43 [-3.04, -0.04] | +1.76 [+0.25, +2.94] | +2.27 [+1.13, +3.88] | 6.91 / 7.60 / 6.66 | **supported** |
| 3 (scarce) | 173 | -2.55 [-10.46, +3.61] | +0.43 [-4.78, +8.12] | -2.12 [-4.35, +0.76] | -1.54 [-9.23, +3.88] | 617.96 / 619.23 / 617.96 | **undecided** |
| no state | 0 | not fitted: fewer than 20 target days |  |  |  |  |  |
| pooled | 767 | +0.39 [-1.01, +1.52] | -0.92 [-1.92, -0.03] | -0.53 [-1.83, +0.50] | +0.59 [-0.40, +1.51] | 145.50 / 145.54 / 145.44 | **undecided** |

## Table 3. (s3c-ann-net) against (s3c-ann) (development window)

### By lead

| lead | cells | days | share of the loss | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|---|---|
| h=1 | 1855 | 1855 | +100.0% | -0.3%, d +0.005 [-0.010, +0.019] **undecided** | -1.4%, d +0.011 [-0.000, +0.023] **undecided** | -6.5%, d +0.003 [+0.001, +0.004] **loss** |
| h=2 | 1855 | 1855 | +100.0% | -0.2%, d +0.002 [-0.011, +0.016] **undecided** | -1.1%, d +0.009 [-0.003, +0.020] **undecided** | -4.5%, d +0.002 [+0.000, +0.004] **loss** |
| h=3 | 1855 | 1855 | +100.0% | +0.2%, d -0.003 [-0.016, +0.010] **undecided** | -0.7%, d +0.006 [-0.005, +0.017] **undecided** | -4.5%, d +0.002 [+0.001, +0.004] **loss** |
| h=4 | 1855 | 1855 | +100.0% | +0.3%, d -0.005 [-0.019, +0.009] **undecided** | -0.4%, d +0.003 [-0.010, +0.015] **undecided** | -3.7%, d +0.002 [+0.000, +0.003] **loss** |
| h=5 | 1855 | 1855 | +100.0% | +0.4%, d -0.007 [-0.022, +0.008] **undecided** | -0.2%, d +0.002 [-0.011, +0.014] **undecided** | -3.8%, d +0.002 [+0.000, +0.003] **loss** |

### By regime of the target day (the five leads averaged per target day, as #1288 groups it)

| regime | cells | days | share of the loss | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|---|---|
| 2018-19 | 1795 | 361 | +100.0% | -1.7%, d +0.061 [+0.009, +0.113] **loss** | -1.7%, d +0.054 [+0.007, +0.103] **loss** | -7.5%, d +0.012 [+0.006, +0.017] **loss** |
| 2020 | 1255 | 251 | +100.0% | +2.0%, d -0.031 [-0.069, -0.001] **gain** | +3.9%, d -0.024 [-0.065, +0.009] **undecided** | +4.9%, d -0.001 [-0.004, +0.001] **undecided** |
| 2021-23 | 3740 | 748 | +100.0% | +0.5%, d -0.003 [-0.007, +0.000] **undecided** | +1.1%, d -0.000 [-0.000, +0.000] **undecided** | -0.0%, d +0.000 [-0.000, +0.000] **undecided** |
| 2024 | 1250 | 250 | +100.0% | +1.6%, d -0.017 [-0.032, -0.003] **gain** | +1.6%, d -0.003 [-0.007, +0.000] **undecided** | +2.6%, d -0.000 [-0.001, +0.000] **undecided** |
| 2025-26 | 1235 | 249 | +100.0% | +1.8%, d -0.041 [-0.067, -0.016] **gain** | +0.5%, d -0.005 [-0.017, +0.008] **undecided** | -0.1%, d +0.000 [-0.002, +0.002] **undecided** |

### By realised event: the probability of a spread above +5 bp

| lead | event frequency | set | cells | mean probability, net | mean probability, flag | Brier difference summed | per cell |
|---|---|---|---|---|---|---|---|
| h=1 | 0.072 | not above +5 bp | 1721 | 0.055 | 0.054 | +0.635 | +0.0004 |
| h=1 | 0.072 | target spread above +5 bp | 134 | 0.561 | 0.604 | +4.122 | +0.0308 |
| h=2 | 0.073 | not above +5 bp | 1720 | 0.059 | 0.059 | -0.288 | -0.0002 |
| h=2 | 0.073 | target spread above +5 bp | 135 | 0.532 | 0.569 | +3.858 | +0.0286 |
| h=3 | 0.073 | not above +5 bp | 1719 | 0.061 | 0.061 | -0.007 | -0.0000 |
| h=3 | 0.073 | target spread above +5 bp | 136 | 0.513 | 0.554 | +3.748 | +0.0276 |
| h=4 | 0.074 | not above +5 bp | 1718 | 0.063 | 0.062 | +0.256 | +0.0001 |
| h=4 | 0.074 | target spread above +5 bp | 137 | 0.513 | 0.550 | +2.901 | +0.0212 |
| h=5 | 0.074 | not above +5 bp | 1717 | 0.065 | 0.063 | +1.050 | +0.0006 |
| h=5 | 0.074 | target spread above +5 bp | 138 | 0.515 | 0.545 | +2.240 | +0.0162 |

### Lead 1: the flag set and an announced drain or none

| group | cells | days | share of the loss | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|---|---|
| flag set, every settling leg net at or below zero | 321 | 321 | -96.1% | +1.9%, d -0.026 [-0.046, -0.008] **gain** | +2.8%, d -0.018 [-0.030, -0.007] **gain** | +7.2%, d -0.003 [-0.005, -0.001] **gain** |
| flag set, some leg net above zero | 622 | 622 | -4.4% | +0.0%, d -0.001 [-0.040, +0.042] **undecided** | -0.8%, d +0.011 [-0.020, +0.044] **undecided** | -15.7%, d +0.006 [+0.001, +0.013] **loss** |

### Lead 1: by target-day type

| group | cells | days | share of the loss | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|---|---|
| bill settlement day | 775 | 775 | +81.6% | -0.5%, d +0.009 [-0.009, +0.029] **undecided** | -0.5%, d +0.005 [-0.006, +0.018] **undecided** | -1.8%, d +0.001 [-0.001, +0.003] **undecided** |
| bill settlement day with a cash management bill | 352 | 352 | +25.2% | -0.7%, d +0.006 [-0.015, +0.034] **undecided** | -3.3%, d +0.005 [-0.000, +0.011] **undecided** | -4.3%, d +0.000 [+0.000, +0.001] **loss** |
| bill settlement day without one | 423 | 423 | +56.4% | -0.5%, d +0.012 [-0.017, +0.038] **undecided** | -0.3%, d +0.005 [-0.015, +0.027] **undecided** | -1.6%, d +0.001 [-0.002, +0.005] **undecided** |
| coupon settlement day | 240 | 240 | -45.4% | +0.9%, d -0.017 [-0.141, +0.121] **undecided** | -2.9%, d +0.036 [-0.052, +0.136] **undecided** | -37.2%, d +0.017 [+0.001, +0.038] **loss** |
| neither settles | 912 | 912 | +200.5% | -1.7%, d +0.019 [+0.008, +0.031] **loss** | -4.8%, d +0.022 [+0.011, +0.033] **loss** | -5.0%, d +0.002 [+0.001, +0.003] **loss** |

### Lead 1: by net-to-gross class

| class | cells | days | share of the loss | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|---|---|
| mixed legs | 17 | 17 | +73.4% | -30.1%, d +0.378 not read **not read** | -64.4%, d +0.340 not read **not read** | -329.5%, d +0.029 not read **not read** |
| net at or above half of gross | 130 | 130 | -125.2% | +5.2%, d -0.084 [-0.215, +0.034] **undecided** | +5.3%, d -0.047 [-0.153, +0.039] **undecided** | -24.0%, d +0.012 [-0.002, +0.031] **undecided** |
| net at or below zero | 348 | 348 | -86.5% | +1.6%, d -0.022 [-0.049, +0.006] **undecided** | +1.3%, d -0.009 [-0.025, +0.009] **undecided** | +6.1%, d -0.002 [-0.004, -0.000] **gain** |
| net below half of gross | 448 | 448 | +37.9% | -0.3%, d +0.007 [-0.016, +0.035] **undecided** | -0.6%, d +0.010 [-0.009, +0.033] **undecided** | -10.0%, d +0.004 [+0.001, +0.009] **loss** |
| no settlement | 912 | 912 | +200.5% | -1.7%, d +0.019 [+0.008, +0.031] **loss** | -4.8%, d +0.022 [+0.011, +0.033] **loss** | -5.0%, d +0.002 [+0.001, +0.003] **loss** |

### Lead 3: the flag set and an announced drain or none

| group | cells | days | share of the loss | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|---|---|
| flag set, every settling leg net at or below zero | 322 | 322 | +227.5% | +2.3%, d -0.035 [-0.063, -0.008] **gain** | +3.6%, d -0.026 [-0.046, -0.008] **gain** | +5.6%, d -0.003 [-0.005, -0.000] **gain** |
| flag set, some leg net above zero | 610 | 610 | +175.2% | +0.6%, d -0.014 [-0.052, +0.029] **undecided** | +0.0%, d -0.001 [-0.033, +0.033] **undecided** | -8.4%, d +0.004 [-0.001, +0.010] **undecided** |

### Lead 3: by target-day type

| group | cells | days | share of the loss | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|---|---|
| bill settlement day | 776 | 776 | +55.5% | +0.2%, d -0.004 [-0.021, +0.014] **undecided** | +0.6%, d -0.007 [-0.019, +0.006] **undecided** | -0.6%, d +0.000 [-0.001, +0.002] **undecided** |
| bill settlement day with a cash management bill | 352 | 352 | +71.0% | +1.0%, d -0.010 [-0.026, +0.008] **undecided** | +3.9%, d -0.007 [-0.018, +0.002] **undecided** | -2.0%, d +0.000 [-0.000, +0.001] **undecided** |
| bill settlement day without one | 424 | 424 | -15.5% | -0.1%, d +0.002 [-0.027, +0.029] **undecided** | +0.4%, d -0.007 [-0.028, +0.013] **undecided** | -0.5%, d +0.000 [-0.003, +0.003] **undecided** |
| coupon settlement day | 241 | 241 | +220.6% | +2.2%, d -0.045 [-0.172, +0.086] **undecided** | -0.2%, d +0.003 [-0.091, +0.100] **undecided** | -18.9%, d +0.010 [-0.004, +0.028] **undecided** |
| neither settles | 911 | 911 | -284.6% | -1.2%, d +0.015 [+0.003, +0.028] **loss** | -4.2%, d +0.021 [+0.010, +0.032] **loss** | -5.2%, d +0.002 [+0.001, +0.004] **loss** |

### Lead 3: by net-to-gross class

| class | cells | days | share of the loss | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|---|---|
| a class partly announced | 1 | 1 | -6.0% | -6.6%, d +0.299 not read **not read** | -6.5%, d +0.290 not read **not read** | -47.1%, d +0.069 not read **not read** |
| mixed legs | 16 | 16 | -85.6% | -20.4%, d +0.265 not read **not read** | -40.2%, d +0.213 not read **not read** | -460.6%, d +0.020 not read **not read** |
| net at or above half of gross | 115 | 115 | +290.5% | +6.5%, d -0.125 [-0.252, -0.002] **gain** | +5.4%, d -0.056 [-0.155, +0.025] **undecided** | -11.9%, d +0.007 [-0.006, +0.025] **undecided** |
| net at or below zero | 350 | 350 | +193.0% | +1.7%, d -0.027 [-0.066, +0.011] **undecided** | +2.2%, d -0.017 [-0.043, +0.008] **undecided** | +5.7%, d -0.003 [-0.006, +0.000] **undecided** |
| net below half of gross | 450 | 450 | +10.9% | +0.1%, d -0.001 [-0.023, +0.024] **undecided** | -0.0%, d +0.000 [-0.022, +0.022] **undecided** | -6.4%, d +0.003 [-0.000, +0.008] **undecided** |
| no settlement | 923 | 923 | -302.8% | -1.3%, d +0.016 [+0.003, +0.030] **loss** | -4.3%, d +0.021 [+0.010, +0.033] **loss** | -5.3%, d +0.002 [+0.001, +0.004] **loss** |

## Table 4. H-b: the 2020 loss against (s3c) (development window)


### 4a. (s3c-ann), the flag: 2020 by period and month (target days, five leads averaged)

| group | cells | days | share of the loss | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|---|---|
| 2020 target days | 1255 | 251 | +100.0% | -4.1%, d +0.060 [+0.016, +0.120] **loss** | -7.2%, d +0.040 [+0.003, +0.092] **loss** | -6.1%, d +0.001 [-0.000, +0.004] **undecided** |
| March to June | 425 | 85 | +81.7% | -5.5%, d +0.145 [+0.028, +0.289] **loss** | -7.7%, d +0.091 [-0.010, +0.218] **undecided** | -6.3%, d +0.004 [-0.002, +0.011] **undecided** |
| the rest of 2020 | 830 | 166 | +18.3% | -2.0%, d +0.017 [-0.006, +0.039] **undecided** | -6.1%, d +0.015 [-0.001, +0.031] **undecided** | -4.9%, d +0.000 [-0.000, +0.001] **undecided** |

| month | cells | days | share of the loss | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|---|---|
| 2020-01 | 105 | 21 | -0.4% | +0.3%, d -0.003 [-0.062, +0.056] **undecided** | -4.9%, d +0.017 [-0.030, +0.062] **undecided** | -7.3%, d +0.000 [-0.001, +0.002] **undecided** |
| 2020-02 | 95 | 19 | -5.0% | +6.1%, d -0.040 not read **not read** | -21.9%, d +0.031 not read **not read** | +1.2%, d -0.000 not read **not read** |
| 2020-03 | 110 | 22 | +68.4% | -7.1%, d +0.471 [-0.104, +1.072] **undecided** | -8.3%, d +0.355 [-0.123, +0.855] **undecided** | -7.8%, d +0.017 [-0.010, +0.044] **undecided** |
| 2020-04 | 105 | 21 | -9.6% | +4.6%, d -0.070 [-0.168, +0.027] **undecided** | +18.9%, d -0.033 [-0.066, -0.001] **gain** | +25.5%, d -0.003 [-0.006, -0.000] **gain** |
| 2020-05 | 100 | 20 | +9.8% | -5.4%, d +0.074 [+0.044, +0.105] **loss** | -0.1%, d +0.000 [-0.002, +0.002] **undecided** | +4.8%, d -0.000 [-0.000, +0.000] **undecided** |
| 2020-06 | 110 | 22 | +13.2% | -9.7%, d +0.091 [+0.051, +0.132] **loss** | -26.2%, d +0.026 [+0.001, +0.052] **loss** | -18.3%, d +0.000 [-0.000, +0.001] **undecided** |
| 2020-07 | 110 | 22 | -2.6% | +1.9%, d -0.018 [-0.076, +0.033] **undecided** | +6.0%, d -0.036 [-0.073, -0.002] **gain** | +15.0%, d -0.001 [-0.001, -0.000] **gain** |
| 2020-08 | 105 | 21 | +0.7% | -0.7%, d +0.005 [-0.033, +0.045] **undecided** | +2.3%, d -0.003 [-0.013, +0.007] **undecided** | +16.0%, d -0.000 [-0.000, -0.000] **gain** |
| 2020-09 | 105 | 21 | +6.6% | -6.0%, d +0.047 [+0.022, +0.074] **loss** | -24.9%, d +0.010 [+0.002, +0.017] **loss** | +10.2%, d -0.000 [-0.000, -0.000] **gain** |
| 2020-10 | 105 | 21 | +2.2% | -2.2%, d +0.016 [-0.012, +0.045] **undecided** | -11.4%, d +0.020 [-0.002, +0.042] **undecided** | -1.9%, d +0.000 [-0.000, +0.001] **undecided** |
| 2020-11 | 95 | 19 | +10.9% | -7.5%, d +0.086 not read **not read** | -21.8%, d +0.074 not read **not read** | -22.7%, d +0.002 not read **not read** |
| 2020-12 | 110 | 22 | +5.9% | -5.0%, d +0.041 [+0.005, +0.077] **loss** | -9.1%, d +0.016 [-0.008, +0.045] **undecided** | -6.7%, d +0.000 [-0.000, +0.001] **undecided** |

### 4a. (s3c-ann-net), the net: 2020 by period and month (target days, five leads averaged)

| group | cells | days | share of the loss | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|---|---|
| 2020 target days | 1255 | 251 | +100.0% | -2.0%, d +0.029 [+0.002, +0.064] **loss** | -3.0%, d +0.017 [+0.000, +0.034] **loss** | -0.9%, d +0.000 [-0.000, +0.001] **undecided** |
| March to June | 425 | 85 | +78.6% | -2.6%, d +0.068 [+0.001, +0.149] **loss** | -2.7%, d +0.032 [-0.004, +0.074] **undecided** | -0.7%, d +0.000 [-0.001, +0.002] **undecided** |
| the rest of 2020 | 830 | 166 | +21.4% | -1.1%, d +0.009 [-0.013, +0.033] **undecided** | -3.7%, d +0.009 [-0.009, +0.027] **undecided** | -2.1%, d +0.000 [-0.000, +0.001] **undecided** |

| month | cells | days | share of the loss | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|---|---|
| 2020-01 | 105 | 21 | -14.6% | +5.5%, d -0.051 [-0.082, -0.020] **gain** | +13.9%, d -0.047 [-0.065, -0.029] **gain** | +20.9%, d -0.001 [-0.002, -0.001] **gain** |
| 2020-02 | 95 | 19 | -10.1% | +6.0%, d -0.039 not read **not read** | +10.1%, d -0.014 not read **not read** | +15.7%, d -0.000 not read **not read** |
| 2020-03 | 110 | 22 | +40.5% | -2.0%, d +0.135 [-0.040, +0.319] **undecided** | -1.6%, d +0.069 [-0.080, +0.224] **undecided** | -0.2%, d +0.000 [-0.006, +0.007] **undecided** |
| 2020-04 | 105 | 21 | +27.5% | -6.3%, d +0.096 [-0.015, +0.210] **undecided** | -0.4%, d +0.001 [-0.006, +0.008] **undecided** | +3.3%, d -0.000 [-0.001, +0.000] **undecided** |
| 2020-05 | 100 | 20 | +4.1% | -1.1%, d +0.015 [-0.019, +0.049] **undecided** | -3.2%, d +0.000 [+0.000, +0.001] **loss** | -2.3%, d +0.000 [+0.000, +0.000] **loss** |
| 2020-06 | 110 | 22 | +6.4% | -2.3%, d +0.022 [-0.032, +0.078] **undecided** | -54.5%, d +0.055 [+0.016, +0.094] **loss** | -64.6%, d +0.002 [+0.000, +0.003] **loss** |
| 2020-07 | 110 | 22 | +1.4% | -0.5%, d +0.005 [-0.028, +0.034] **undecided** | +1.9%, d -0.011 [-0.038, +0.015] **undecided** | +8.9%, d -0.000 [-0.001, -0.000] **gain** |
| 2020-08 | 105 | 21 | -0.4% | +0.2%, d -0.001 [-0.027, +0.025] **undecided** | +0.3%, d -0.000 [-0.011, +0.010] **undecided** | +2.0%, d -0.000 [-0.000, +0.000] **undecided** |
| 2020-09 | 105 | 21 | +11.2% | -5.0%, d +0.039 [-0.007, +0.086] **undecided** | -70.9%, d +0.028 [+0.005, +0.052] **loss** | -23.6%, d +0.000 [+0.000, +0.000] **loss** |
| 2020-10 | 105 | 21 | -7.1% | +3.5%, d -0.025 [-0.043, -0.007] **gain** | -1.2%, d +0.002 [-0.025, +0.030] **undecided** | +3.9%, d -0.000 [-0.001, +0.000] **undecided** |
| 2020-11 | 95 | 19 | +17.3% | -5.8%, d +0.067 not read **not read** | -20.5%, d +0.070 not read **not read** | -29.2%, d +0.002 not read **not read** |
| 2020-12 | 110 | 22 | +23.7% | -9.8%, d +0.079 [+0.027, +0.132] **loss** | -27.5%, d +0.049 [+0.011, +0.089] **loss** | -24.0%, d +0.001 [+0.000, +0.002] **loss** |

### 4b. The settlement terms against the realised spread, by regime (leads 2 to 5)

Bias: mean of y - median on settlement target cells less that on the others (negative: forecast too high on settlement days). Shift: the arm's fitted settlement contribution in bp on settlement cells. Premium: the realised mean spread on settlement target days less the others. Intervals over decision days.

| regime | arm | settlement cells | bias | shift | realised premium |
|---|---|---|---|---|---|
| 2018-19 | (s3c) | 676 | +4.52 [+2.04, +7.70] | +0.00 [+0.00, +0.00] | +5.99 [+3.26, +9.32] |
| 2018-19 | (s3c-ann), the flag | 676 | +2.76 [+0.42, +5.84] | +2.02 [+1.58, +2.49] | +5.99 [+3.26, +9.32] |
| 2018-19 | (s3c-ann-net), the net | 676 | +4.15 [+1.70, +7.29] | +0.48 [+0.34, +0.65] | +5.99 [+3.26, +9.32] |
| 2020 | (s3c) | 544 | +0.17 [-0.51, +1.01] | +0.00 [+0.00, +0.00] | +0.28 [-0.39, +1.12] |
| 2020 | (s3c-ann), the flag | 544 | -0.66 [-1.40, +0.17] | +0.95 [+0.72, +1.24] | +0.28 [-0.39, +1.12] |
| 2020 | (s3c-ann-net), the net | 544 | -0.26 [-1.00, +0.62] | +0.49 [+0.35, +0.64] | +0.28 [-0.39, +1.12] |
| 2021-23 | (s3c) | 1552 | +0.11 [-0.01, +0.22] | +0.00 [+0.00, +0.00] | +0.12 [-0.06, +0.27] |
| 2021-23 | (s3c-ann), the flag | 1552 | -0.01 [-0.15, +0.12] | +0.13 [+0.09, +0.18] | +0.12 [-0.06, +0.27] |
| 2021-23 | (s3c-ann-net), the net | 1552 | +0.08 [-0.03, +0.20] | +0.03 [+0.01, +0.05] | +0.12 [-0.06, +0.27] |
| 2024 | (s3c) | 504 | +1.20 [+0.55, +1.96] | +0.00 [+0.00, +0.00] | +1.37 [+0.65, +2.23] |
| 2024 | (s3c-ann), the flag | 504 | +0.83 [+0.23, +1.54] | +0.41 [+0.33, +0.49] | +1.37 [+0.65, +2.23] |
| 2024 | (s3c-ann-net), the net | 504 | +0.94 [+0.35, +1.63] | +0.31 [+0.22, +0.41] | +1.37 [+0.65, +2.23] |
| 2025-26 | (s3c) | 503 | +1.81 [+1.18, +2.45] | +0.00 [+0.00, +0.00] | +2.40 [+1.61, +3.27] |
| 2025-26 | (s3c-ann), the flag | 503 | +0.83 [+0.21, +1.46] | +1.14 [+0.92, +1.42] | +2.40 [+1.61, +3.27] |
| 2025-26 | (s3c-ann-net), the net | 503 | +1.25 [+0.62, +1.86] | +0.78 [+0.59, +1.00] | +2.40 [+1.61, +3.27] |

The bias of 2020 less that of 2018-19: (s3c-ann), the flag [-6.58, -0.93], (s3c-ann-net), the net [-7.66, -1.81] (both below zero, mostly because (s3c) itself under-forecast settlement days by about +4.5 bp in 2018-19).

### 4c. 2020, leads 2 to 5, by scarcity state of the decision day and settlement size (highest third: gross of at least USD 200 bn)


(s3c-ann), the flag against (s3c)

| group | cells | days | share of the loss | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|---|---|
| all 2020 cells at h = 2 to 5 | 1004 | 254 | +100.0% | -5.1%, d +0.077 [+0.025, +0.144] **loss** | -8.8%, d +0.050 [+0.008, +0.108] **loss** | -7.3%, d +0.002 [-0.000, +0.004] **undecided** |
| state 0 (abundant), highest third of settlement size | 2 | 1 | -0.1% | +3.0%, d -0.051 not read **not read** | +14.7%, d -0.008 not read **not read** | +15.3%, d -0.000 not read **not read** |
| state 0 (abundant), no settlement | 1 | 1 | +0.1% | -10.4%, d +0.098 not read **not read** | +22.3%, d -0.013 not read **not read** | +20.7%, d -0.000 not read **not read** |
| state 0 (abundant), other settlement days | 1 | 1 | +1.6% | -127.4%, d +1.235 not read **not read** | -103.6%, d +0.074 not read **not read** | -165.7%, d +0.004 not read **not read** |
| state 1 to 2, highest third of settlement size | 103 | 79 | +21.7% | -15.3%, d +0.203 [+0.009, +0.439] **loss** | -88.9%, d +0.222 [+0.063, +0.403] **loss** | -96.4%, d +0.009 [+0.001, +0.018] **loss** |
| state 1 to 2, no settlement | 339 | 183 | +9.8% | -1.9%, d +0.018 [-0.016, +0.054] **undecided** | +16.4%, d -0.028 [-0.038, -0.017] **gain** | +26.1%, d -0.001 [-0.001, -0.000] **gain** |
| state 1 to 2, other settlement days | 308 | 163 | +16.5% | -4.9%, d +0.044 [-0.009, +0.099] **undecided** | -8.5%, d +0.019 [-0.008, +0.047] **undecided** | -2.6%, d +0.000 [-0.001, +0.001] **undecided** |
| state 3 (scarce), highest third of settlement size | 3 | 3 | +30.3% | -40.8%, d +7.637 not read **not read** | -73.5%, d +7.360 not read **not read** | -18.0%, d +0.148 not read **not read** |
| state 3 (scarce), no settlement | 120 | 62 | -22.4% | +9.5%, d -0.208 [-0.490, +0.033] **undecided** | +14.3%, d -0.137 [-0.296, +0.002] **undecided** | +15.1%, d -0.009 [-0.023, +0.002] **undecided** |
| state 3 (scarce), other settlement days | 127 | 64 | +42.5% | -6.3%, d +0.207 [-0.030, +0.528] **undecided** | -8.3%, d +0.169 [+0.035, +0.335] **loss** | -13.5%, d +0.011 [-0.002, +0.030] **undecided** |

(s3c-ann-net), the net against (s3c)

| group | cells | days | share of the loss | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|---|---|
| all 2020 cells at h = 2 to 5 | 1004 | 254 | +100.0% | -3.0%, d +0.045 [+0.010, +0.083] **loss** | -4.5%, d +0.026 [+0.006, +0.047] **loss** | -1.4%, d +0.000 [-0.000, +0.001] **undecided** |
| state 0 (abundant), highest third of settlement size | 2 | 1 | +0.8% | -8.6%, d +0.148 not read **not read** | -11.4%, d +0.006 not read **not read** | -11.1%, d +0.000 not read **not read** |
| state 0 (abundant), no settlement | 1 | 1 | -0.0% | +1.1%, d -0.010 not read **not read** | +12.9%, d -0.007 not read **not read** | +13.2%, d -0.000 not read **not read** |
| state 0 (abundant), other settlement days | 1 | 1 | -0.0% | +2.0%, d -0.019 not read **not read** | +13.2%, d -0.009 not read **not read** | +8.4%, d -0.000 not read **not read** |
| state 1 to 2, highest third of settlement size | 103 | 79 | +46.8% | -17.6%, d +0.234 [-0.011, +0.525] **undecided** | -108.6%, d +0.272 [+0.081, +0.496] **loss** | -114.1%, d +0.010 [+0.003, +0.019] **loss** |
| state 1 to 2, no settlement | 339 | 183 | +2.6% | -0.1%, d +0.001 [-0.012, +0.014] **undecided** | +7.8%, d -0.013 [-0.018, -0.008] **gain** | +14.6%, d -0.000 [-0.001, -0.000] **gain** |
| state 1 to 2, other settlement days | 308 | 163 | +36.4% | -4.0%, d +0.036 [+0.001, +0.075] **loss** | -5.3%, d +0.012 [-0.006, +0.032] **undecided** | +0.1%, d -0.000 [-0.000, +0.000] **undecided** |
| state 3 (scarce), highest third of settlement size | 3 | 3 | +31.1% | -21.5%, d +4.030 not read **not read** | -37.5%, d +3.753 not read **not read** | -13.2%, d +0.109 not read **not read** |
| state 3 (scarce), no settlement | 120 | 62 | -15.8% | +3.7%, d -0.080 [-0.191, +0.011] **undecided** | +6.6%, d -0.063 [-0.142, +0.005] **undecided** | +8.1%, d -0.005 [-0.012, +0.001] **undecided** |
| state 3 (scarce), other settlement days | 127 | 64 | -1.7% | +0.2%, d -0.006 [-0.068, +0.069] **undecided** | +1.4%, d -0.028 [-0.068, +0.008] **undecided** | +2.2%, d -0.002 [-0.004, -0.000] **gain** |

### 4d. The immediate-release days (an auction with no stated release time settles on the target; metadata/announcement_release_times_1301.json)


(s3c-ann), the flag against (s3c), target days

| group | cells | days | share of the loss | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|---|---|
| 2020 with those days left out | 910 | 182 | +70.6% | -4.0%, d +0.059 [+0.019, +0.104] **loss** | -3.8%, d +0.025 [-0.002, +0.056] **undecided** | -5.1%, d +0.001 [-0.001, +0.004] **undecided** |
| 2020, all target days | 1255 | 251 | +100.0% | -4.1%, d +0.060 [+0.016, +0.120] **loss** | -7.2%, d +0.040 [+0.003, +0.092] **loss** | -6.1%, d +0.001 [-0.000, +0.004] **undecided** |
| an auction with no stated release time settles on the target | 345 | 69 | +29.4% | -4.4%, d +0.064 [-0.023, +0.208] **undecided** | -25.2%, d +0.081 [-0.003, +0.225] **undecided** | -10.3%, d +0.002 [-0.000, +0.005] **undecided** |
| such a cash management bill settles on the target | 345 | 69 | +29.4% | -4.4%, d +0.064 [-0.023, +0.208] **undecided** | -25.2%, d +0.081 [-0.003, +0.225] **undecided** | -10.3%, d +0.002 [-0.000, +0.005] **undecided** |

(s3c-ann-net), the net against (s3c), target days

| group | cells | days | share of the loss | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|---|---|
| 2020 with those days left out | 910 | 182 | +32.5% | -0.9%, d +0.013 [-0.011, +0.037] **undecided** | -0.4%, d +0.003 [-0.019, +0.023] **undecided** | +2.2%, d -0.001 [-0.002, +0.000] **undecided** |
| 2020, all target days | 1255 | 251 | +100.0% | -2.0%, d +0.029 [+0.002, +0.064] **loss** | -3.0%, d +0.017 [+0.000, +0.034] **loss** | -0.9%, d +0.000 [-0.000, +0.001] **undecided** |
| an auction with no stated release time settles on the target | 345 | 69 | +67.5% | -5.0%, d +0.072 [-0.019, +0.196] **undecided** | -17.0%, d +0.055 [+0.002, +0.130] **loss** | -13.0%, d +0.002 [+0.000, +0.005] **loss** |
| such a cash management bill settles on the target | 345 | 69 | +67.5% | -5.0%, d +0.072 [-0.019, +0.196] **undecided** | -17.0%, d +0.055 [+0.002, +0.130] **loss** | -13.0%, d +0.002 [+0.000, +0.005] **loss** |

## The 2026 days (targets 2026-01-02 to 2026-09-03; descriptive, decides nothing)

### Lead 1: (s3c-ann-net) against (s3c)

| group | cells | days | share of the loss | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|---|---|
| all lead-1 cells | 165 | 165 | +100.0% | +2.9%, d -0.044 [-0.082, -0.002] **gain** | +5.2%, d -0.026 [-0.060, +0.009] **undecided** | +10.9%, d -0.004 [-0.008, -0.001] **gain** |
| bill settlement day | 70 | 70 | +69.5% | +4.7%, d -0.071 [-0.130, -0.013] **gain** | +10.6%, d -0.052 [-0.123, +0.014] **undecided** | +20.2%, d -0.008 [-0.016, +0.000] **undecided** |
| bill settlement day with a cash management bill | 1 | 1 | -0.0% | -0.2%, d +0.001 not read **not read** | n/a, d +0.000 not read **not read** | n/a, d +0.000 not read **not read** |
| bill settlement day without one | 69 | 69 | +69.5% | +4.7%, d -0.073 [-0.132, -0.014] **gain** | +10.6%, d -0.053 [-0.129, +0.009] **undecided** | +20.2%, d -0.008 [-0.017, +0.000] **undecided** |
| coupon settlement day | 23 | 23 | +98.1% | +17.6%, d -0.307 [-0.499, -0.119] **gain** | +22.8%, d -0.244 [-0.403, -0.085] **gain** | +24.3%, d -0.032 [-0.048, -0.016] **gain** |
| neither settles | 77 | 77 | -27.1% | -1.7%, d +0.025 [+0.010, +0.042] **loss** | -6.0%, d +0.024 [+0.014, +0.035] **loss** | -3.1%, d +0.001 [+0.000, +0.001] **loss** |

### (s3c-ann-net) against (s3c-ann), by lead

| lead | cells | days | share of the loss | grid CRPS | upper-tail twCRPS | Brier P(> +5 bp) |
|---|---|---|---|---|---|---|
| h=1 | 165 | 165 | +100.0% | +2.9%, d -0.044 [-0.082, -0.002] **gain** | +5.2%, d -0.026 [-0.060, +0.009] **undecided** | +10.9%, d -0.004 [-0.008, -0.001] **gain** |
| h=2 | 165 | 165 | +100.0% | +2.8%, d -0.048 [-0.082, -0.016] **gain** | +6.9%, d -0.038 [-0.071, -0.009] **gain** | +13.4%, d -0.006 [-0.010, -0.002] **gain** |
| h=3 | 165 | 165 | +100.0% | +2.3%, d -0.040 [-0.072, -0.011] **gain** | +6.8%, d -0.038 [-0.069, -0.012] **gain** | +14.5%, d -0.006 [-0.010, -0.002] **gain** |
| h=4 | 165 | 165 | +100.0% | +2.2%, d -0.038 [-0.069, -0.008] **gain** | +6.4%, d -0.036 [-0.065, -0.008] **gain** | +12.9%, d -0.005 [-0.009, -0.002] **gain** |
| h=5 | 165 | 165 | +100.0% | +2.1%, d -0.038 [-0.069, -0.007] **gain** | +5.8%, d -0.033 [-0.063, -0.005] **gain** | +10.5%, d -0.004 [-0.008, -0.001] **gain** |

## What this does and does not show

- It is a diagnosis on days already seen: every interval is a development interval, the group-of-days intervals keep the current method (#1221, #1228), and no reading here is a verdict or changes a claim.
- The fits, the walks and the arms are #1288's and are unchanged. The mechanisms (a refit that moves the non-settlement terms; netting shrinking the size regressor) are stated as the reading of the tables, and no arm was run to test them.
- H-a is tested through the residual against the flag arm's own median: the gross and maturing amounts are the announced ones (a class announced in part is left out), the regression is in sample, and the bill leg is dominated by a few very large residuals in the scarce state.
- The 'abundant reserves' reading of H-b needs a state that was 0 in 2020; the model's state was not. Settlement size, the realised premium and the settlement-day bias are the nearest tests available here.
- The immediate-release dating check rests on the 12:00 announcement instant and on the days' own release rule; a cash management bill with no stated release time could have been announced after the 16:00 decision, which would count it too early.

## Questions for Eleonora (marked; defaults change no claim)

**Question 1. #1316: what to record about the three losses.** The page's answers are development readings on seen days. Recording them is her call.

**Options** (the default applies if you have not answered by the next 5 pm batch):

1. **Record the three losses as open questions** on the candidate's pages, with this page's readings, and change no claim (default). Recommended.
2. **Widen #1314** (the 18:00 re-run) so its table also carries the lead-1, 2020 and net-against-flag splits of this page, so the question is re-asked at the new instant.

**Question 2. #1318: which arm to queue next.** The flag and the net win in different places; the coupon leg's regression supports gross over net (H-a), and the net's Brier loss is on pressure days.

**Options** (the default applies if you have not answered by the next 5 pm batch):

1. **Queue nothing yet** (default): leave #1318 open until #1314 has re-run the candidate at 18:00.
2. **Queue the flag-plus-net arm of #1318** on #1288's script, beside the flag and the net, as one development run. Recommended if she wants a next step now.
3. **Queue a gross-sized arm** (the coupon gross as a size, the bill as a flag), since H-a is supported for the coupon leg and undecided for the bill leg.

**Question 3. #1317: the dating's documents.** Nothing on this page changes what #1317 asks. One fact bears on it: the net arm's 2020 loss is not separable from the immediate-release cash management bills (page, 4d).

**Options** (the default applies if you have not answered by the next 5 pm batch):

1. **Leave #1317 as it is** (default).
2. **Add the 2020 immediate-release finding to #1317's list** of what the documents should say about the dating's evidence. Recommended.
