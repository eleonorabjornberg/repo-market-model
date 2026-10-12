# What separates the every-day part's onset warnings from its false alarms, and a cap on it (#601)

A scratch measurement under the pressure-day judge. It writes nothing into `docs/runs/`, publishes nothing, moves no published figure, scores no day of 2026 and reads no day after
2025-12-31 (`docs/decisions/lockbox.md`; `require_unlocked`). No rule, threshold, onset definition or availability time changes. Step 1 (the comparison) was declared in
`metadata/every_day_separation_601.json` and committed, with its readers and tests, before it was run; the declaration was amended once afterwards, before step 2 (see "Amendment"). Step 1's result
(`evidence/every-day-separation/`) was committed before the step 2 declaration `metadata/every_day_conditioning_601.json` and its two candidate files, which were committed before the first cap
was scored. Both scripts refuse an uncommitted declaration.

**Both steps read 2018-2025, and step 2 conditions on an input found there, so a pass is not a confirmation (ruling of 11 October 2026 on #567). A variant can replace a shortlist slot only by
Eleonora's decision, before the 2026 window opens. Nothing here joins a published declaration.**

## Result in one paragraph

Step 1: the row's every-day part flags 5 onset days and 131 false-alarm days. One input separates the two groups in the declared sense: the tail spread's level (the SOFR 99th percentile less
IORB), which is **lower** at the onset warnings (median 18 bp against 23 bp), AUROC 0.30 [0.16, 0.47]. It is the only one of 14 that does so both in the pooled comparison and in the comparison with the
false alarms of the onset years only (0.28 [0.09, 0.49]). The evidence is thin: the 5 warnings are onset days in 2019 and 2020 only, 14 inputs were examined, and both intervals end just below 0.5.
Step 2 conditions the part on that input with a cap. The cap at the upper quartile of the tail spread's trailing readings (`+tailcap75`) keeps 18 of the row's 19 onsets and brings the pooled weighted false alarms
per onset from 3.46 to 1.88, which passes tier 1 under the weighted rule in force (limit 2); under the flat rule it is 2.62 and does not. Tiers 3 and 5 still fail. The cap at the median
(`+tailcap50`) passes tier 1 under both rules, but it switches the part off: it keeps the same 14 onsets as `risk_gbm+settle+h41`.

## Step 1: what separates the onset warnings from the false alarms

The row `risk_gbm+every_day+gate+settle+h41+iorb` (PR #582) warns 19 of 26 onsets at leads 1 to 5. A flag at a lead where the day is not a risk date is the every-day part's. Of the 19, 14 are warned by the
risk-date part alone, and 5 by the every-day part: 2019-05-28, 2019-06-25, 2019-08-13, 2020-03-04 and 2020-03-12 (the same five that #595 lists). Its false alarms are 131 days (the 53 others are
the risk-date part's); 65 further days it flags are pressure days that are not onsets, and are left out of both groups and counted.

Each input is read through `asof.InformationRule` at the decision instant of the farthest lead that flags the day, at its own latest public row; a change over k market days is the latest public value
less the value k panel rows earlier in that decision's masked frame; the days to the next risk date read the calendar columns only (`LookAheadError` otherwise). Separation is the area under the ROC curve
for onset warnings against false alarms (0.5 none; above 0.5 the onset warnings read higher), with a 90% interval from 2000 resamples, the two groups resampled apart (the false alarms by the judge's
stationary bootstrap, block length 10). Full tables, for the pooled comparison, the comparison restricted to the years 2019 and 2020, and each lead alone, are in `evidence/every-day-separation/separation.md`.

| input | onset warnings: median | false alarms: median | AUROC [90%], all false alarms | AUROC [90%], false alarms of 2019-20 only |
|---|---|---|---|---|
| tail spread, level | 18.0 | 23.0 | 0.304 [0.16, 0.47] | 0.276 [0.09, 0.49] |
| tail spread, change over 1 / 5 / 10 days | 4.0 / 3.0 / 1.0 | 4.0 / 9.0 / 6.0 | 0.463 / 0.362 / 0.420, all straddle 0.5 | all straddle 0.5 |
| rolling satiation distance (#587) | 0.00 | -0.00 | 0.665 [0.42, 0.89] | 0.651 [0.39, 0.89] |
| reserve balances, change over 5 / 20 days | 16.2 / 10.1 | 2.7 / -25.3 | 0.627 / 0.662, both straddle 0.5 | both straddle 0.5 |
| market days to the next calendar risk date | 17 | 9 | 0.547 [0.30, 0.78] | 0.563 [0.28, 0.83] |
| TGA, level; change over 5 / 10 days | 323.8; -24.6 / -33.2 | 380.6; 0.3 / 2.6 | all straddle 0.5 | all straddle 0.5 |
| SOFR dispersion, 99th less 1st percentile | 0.18 | 0.24 | 0.318 [0.16, 0.49] | 0.309 [0.10, 0.52] |
| SOFR dispersion, 99th less 75th percentile | 0.08 | 0.07 | 0.492 [0.28, 0.71] | 0.372 [0.13, 0.63] |

**Reading.** Two intervals exclude 0.5 in the pooled comparison: the tail spread's level and the 99th-to-1st percentile dispersion; the dispersion does not survive the comparison within the onset
years, the level does. The direction is the opposite of what the component would use: at the days it warns correctly the tail spread is lower than at the days it warns wrongly, which is to say the false
alarms sit in stretches in which the tail has been high for a while (2019, 2025), and the warnings come as it begins to rise. No other input separates them, including the change in the tail spread, the
rolling satiation distance, the reserve trend, the days to the next risk date and the TGA path. Each lead alone has 1 to 4 onset warnings, fewer than the declared minimum of 5, so no per-lead cell is called a
separation (they are in the evidence file, for the record). With 14 inputs examined, about one in ten that do not separate would show an interval excluding 0.5 by chance: this is a description of
2018-2025, and five onset days in two years cannot carry more.

## Step 2: a cap on the every-day part by the tail spread's own trailing history

Step 1's rule triggers step 2 for one input, `tail_spread_level`, found lower. A term fitted for the probability of a pressure day is trained on all training days, where a higher tail spread goes with more pressure, so it is not expected to learn a fall (this was not tested), and the input conditions the
part as a gate, as the gate of #532 conditions it on its own forecast. On a day that is not a risk date at the lead, the row's forecast is kept only if the tail spread read at the lead's decision
instant is at or below the quantile (nearest rank) of the tail spread read on the previous 250 scored days (at least 60; else 0), each at its own earlier decision instant. Two strengths of one rule,
with round quantiles declared and not read from a score: `+tailcap75` (the upper quartile) and `+tailcap50` (the median). The risk-date part and the judge are the row's. Nothing is refitted.

Table 1. The judge's tier 1 (leads 1 to 5, and leads 3 to 5), tier 3 and tier 5; 90% intervals; the limit on false alarms per onset is 2, read on the pooled count. Full tables are in
`evidence/every-day-conditioning/judge-*.md` and `summary.md`; the split of tier 1 by lead is in each row's section of `judge-*.md`.

| row | rule | tier 1, leads 1 to 5: onsets flagged, recall [90%], pooled false alarms per onset (limit 2) | tier 1 | tier 1, leads 3 to 5 | tier 3 | tier 5 | passes |
|---|---|---|---|---|---|---|---|
| risk_gbm+settle+h41 | flat | 14 of 26, 0.538 [0.353, 0.710], 2.00 | yes | 11 of 26, 0.423 [0.250, 0.607], 1.58 | no | no | no |
| risk_gbm+settle+h41 | weighted | 14 of 26, 0.538 [0.353, 0.710], 1.44 | yes | 11 of 26, 0.423 [0.250, 0.607], 1.23 | no | no | no |
| the row | flat | 16 of 26, 0.615 [0.440, 0.786], 4.35 | no | 12 of 26, 0.462 [0.280, 0.652], 3.46 | no | no | no |
| the row | weighted | 19 of 26, 0.731 [0.560, 0.889], 3.46 | no | 15 of 26, 0.577 [0.385, 0.762], 2.62 | no | no | no |
| `+tailcap75` | flat | 17 of 26, 0.654 [0.480, 0.818], 2.62 | no | 13 of 26, 0.500 [0.312, 0.692], 2.23 | no | no | no |
| `+tailcap75` | weighted | 18 of 26, 0.692 [0.522, 0.852], 1.88 | **yes** | 14 of 26, 0.538 [0.344, 0.731], 1.62 | no | no | no |
| `+tailcap50` | flat | 14 of 26, 0.538 [0.360, 0.720], 1.96 | yes | 11 of 26, 0.423 [0.250, 0.609], 1.58 | no | no | no |
| `+tailcap50` | weighted | 14 of 26, 0.538 [0.360, 0.720], 1.48 | yes | 11 of 26, 0.423 [0.250, 0.609], 1.25 | no | no | no |

Table 2. Onsets flagged at some lead, paired against the row (weighted rule; the flat rule is `compare-row-unweighted.md`), recall difference with a 90% stationary-bootstrap interval, and against
`risk_gbm+settle+h41` (`compare-settle-weighted.md`).

| variant | flagged | recall difference vs the row | recall difference vs `risk_gbm+settle+h41` | lost against the row | gained |
|---|---|---|---|---|---|
| `+tailcap75` | 18 of 26 | -0.038 [-0.111, 0.000] | +0.154 [+0.042, +0.278] | 2020-03-12 | none |
| `+tailcap50` | 14 of 26 | -0.192 [-0.348, -0.050] | 0.000 | 2019-05-28, 2019-06-25, 2019-08-13, 2020-03-04, 2020-03-12 | none |

Every onset by date and lead, for the row, the variants and `risk_gbm+settle+h41`, is in `evidence/every-day-conditioning/onsets-weighted.md`. By regime, `+tailcap75` loses one onset against the row,
in 2020 (1 of 2 kept); 2018-19, 2024 (two onsets) and 2025-26 are unchanged. `+tailcap50` loses three of 2018-19 and both of 2020. By day type, the onsets `+tailcap75` keeps over `risk_gbm+settle+h41` are on ordinary days
(8 of 12 against 4).

Table 3. The pooled false alarms of each row, by source and year (weighted rule; `evidence/every-day-conditioning/diag-*.md`).

| row | onsets flagged | pooled false-alarm days | weighted | risk-date part | every-day part | per onset | 2019 | 2020 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|
| `risk_gbm+settle+h41` | 14 | 56 | 37.5 | 37.5 | none | 1.44 | | | | |
| the row | 19 | 184 | 90.0 | 35.0 | 55.0 | 3.46 | 90 | 26 | 13 | 50 |
| `+tailcap75` | 18 | 87 | 49.0 | 37.5 | 11.5 | 1.88 | 52 | 21 | 2 | 7 |
| `+tailcap50` | 14 | 57 | 38.5 | 37.5 | 1.0 | 1.48 | 22 | 21 | 2 | 7 |

Paired Brier difference at h = 1, +5 bp, against the row (negative favours the variant): `+tailcap75` -0.0073 [-0.0150, -0.0005] over all days, -0.0400 [-0.0716, -0.0116] in 2018-19, and worse by
+0.0072 in 2020 [0.0000, +0.0204] and +0.0072 in 2024 [+0.0009, +0.0162]; against `risk_gbm+settle+h41`, +0.0010 [-0.0002, +0.0024] (`compare-*.md`, Table 3).

## Reading

* The cap at the upper quartile cuts the every-day part's false alarms from 131 days to 31 and keeps four of its five onsets. Under the weighted rule in force that is a tier 1 pass with 18 onsets flagged,
  four more than the passer `risk_gbm+settle+h41`; under the flat rule it misses the limit (2.62). The gain over `risk_gbm+settle+h41` is +0.154 [+0.042, +0.278] in recall, and its Brier score is
  indistinguishable from that row's.
* The median cap is the same rule turned up: it leaves one every-day false alarm and no every-day onset, which is the risk-date part alone.
* What the cap costs is what it is: it switches the every-day part off whenever the tail spread is high against its own recent history. That removes most of the 2025 false alarms (50 days to 7), and
  also the 2020-03-12 onset, and it would do the same in any sustained stress in which the part might have warned. In 2025 the onsets were warned by the risk-date part either way (4 of 5).
* Tiers 3 and 5 fail for every row, as before; the cap does not touch them.
* The step 1 evidence that licenses the cap is the weakest link: five onset days in two years, one input of fourteen, the interval ending just below 0.5. The cap passes tier 1 because it removes
  false alarms in 2019 and 2025 that the tail level distinguishes in this history, and that is all it shows.

## Marked questions for Eleonora (not settled in code)

1. Whether the step 1 separation is credible enough to rest a variant on: it is a borderline result (see "Reading"), and the direction is one a fitted term is not expected to use. The cap was built because the declared
   trigger fired, not because the evidence is strong.
2. Whether `+tailcap75` replaces a shortlist slot (#567). It passes tier 1 under the weighted rule only, was built after seeing 2018-2025, and fails tiers 3 and 5, so this measurement does not suggest it.
   It does not ask to join a published declaration; no "Publish?" question arises.

## Amendment, and what was not checked

* **Amendment.** The step 1 declaration was amended once after its first run, before any step 2 declaration: a table cell with fewer than 5 onset warnings is reported and never called a separation, and
  an input triggers step 2 only if it separates in the pooled comparison and again, in the same direction, in the comparison with the false alarms of the onset years. The first run had printed intervals for per-lead
  cells of one to four onset warnings (a single warning makes the interval carry the false alarms' variability only). The amendment can only turn a "yes" into a "no"; the pooled tables were
  identical before and after it, and the trigger it adds picks the one input that already separated in both comparisons.
* No day of 2026 is scored. A result on 2018-2025 is not a confirmation.
* No quantile other than 0.75 and 0.5, no window other than the gate's 250, no input other than the tail spread's level, and no fitted form (interaction term) is tried; at most two variants.
* The unit of step 1 is the day, read at the decision instant of the farthest lead that flags it; days flagged at a nearer lead only are read at that lead. The per-lead tables use each flag as a unit.
* Inputs not in the panel (anything fetched) are not examined.

## Commands

Published panel `4ddc3882…` (`verify-panel` clean, unchanged); scratch panel `AUG2D` (`pressure_v1_1.py panel`, then `measurement_fields.py panel`, then `satiation_distance_598.py panel`). `/opt/rmm-venv`
(numpy 2.4.6, scikit-learn 1.9.1), `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`. In order: `pressure_judge.py forecasts` at h = 1 to 5; `announcement_dating_rescore.py run --arm both --model risk_gbm` at h = 1 to 5;
`iorb_every_day_579.py run` at h = 1 to 5; `every_day_separation_601.py declare` and `run`; `every_day_conditioning_601.py declare` and `cap`; `pressure_judge.py judge --rule weighted|unweighted`;
`every_day_conditioning_601.py pg diagnose|compare|onsets|summary` (the scoring commands of `pooled_gate_595.py` with this declaration and these two variants). The exact arguments are in the docstrings of the two scripts and of `pooled_gate_595.py`.
