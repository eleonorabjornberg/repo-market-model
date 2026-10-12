# State-conditioned recalibration of the best row (#589)

A scratch measurement under the pressure-day judge. It writes nothing into `docs/runs/`, publishes nothing, moves no published
figure, scores no day of 2026 and reads no day after 2025-12-31 (`docs/decisions/lockbox.md`). The declaration is
`metadata/state_recalibration_589.json`, committed before any score.

> **The ruling on #567.** The two variants below were built after seeing 2018 to 2025. A pass here would not be a confirmation, and a
> variant can replace a shortlist slot only by Eleonora's decision, before the 2026 window opens. None passes.

## What was measured

The parent is `risk_gbm+every_day+gate+settle+h41+iorb` (#579, PR #582), refitted with the own-leg scarcity state of #586 (its `risk_gbm`
inputs include `reserve_scarcity_state`). Its forecasts are recalibrated walk-forward on the judge's cadence (a refit every 21 scored
days, each block from the earlier pairs whose scored day is at or before the block's last training label; identity until 250 pairs and
5 events), keyed on the scarcity state read as of the forecast's decision instant, each leg at its own latest public row. No hindsight
regime label is used (ruling on #515).

| variant | row | what |
|---|---|---|
| (a) | `…+iorb+state_platt` | Platt (declared in place of isotonic) per state, on that state's own earlier pairs; pooled Platt while the state holds fewer than 60 pairs or 3 events |
| (b) | not run | (a) plus #587's time-varying satiation distance as a covariate, "if #587 has merged": its pull request was open, so it is declared and not scored |
| (c) | `…+iorb+state_shrunk` | the pooled Platt slope with one intercept offset per state, shrunk toward zero by a ridge penalty of precision 1.0 (a hierarchical intercept) |

The constants are #380's (60 pairs, 3 events) and one new one, the precision, declared before any score; none was tuned.

## The judge in force

Scored under the judge as in force on `main` (the rulings of 10 October 2026: false alarms per onset pooled across the horizons for
tier 1, tier 3 from 20 pressure days, the split-years line), both rules, and the earlier counting alongside (the worst single lead).
**The in-force figure comes first.**

| row | rule | onsets flagged at lead ≥ 1, recall [90%] | false alarms per onset, pooled (limit 2) | worst single lead (earlier counting) | tier 1 | tier 3 | tier 5 |
|---|---|---|---|---|---|---|---|
| parent | flat | 16 of 26, 0.615 [0.440, 0.786] | 4.38 | 2.35 | no | no | no |
| parent | weighted | 19 of 26, 0.731 [0.560, 0.889] | 3.46 | 1.64 | no | no | no |
| (a) state_platt | flat | 14 of 26, 0.538 [0.364, 0.720] | 3.38 | 1.77 | no | no | **yes** |
| (a) state_platt | weighted | 18 of 26, 0.692 [0.518, 0.852] | 3.23 | 2.32 | no | no | **yes** |
| (c) state_shrunk | flat | 14 of 26, 0.538 [0.360, 0.714] | 3.54 | 2.08 | no | no | no |
| (c) state_shrunk | weighted | 18 of 26, 0.692 [0.519, 0.857] | 2.88 | 1.87 | no | no | no |

No variant passes tier 1, tier 3 or the overall pass under either rule. The one verdict that changes is **tier 5 for (a), no to yes
under both rules**, on its `calibrated` criterion (weighted run: mean predicted 0.175 against a base rate of 0.152, where the parent
forecasts 0.123 and (c) 0.117); the Brier-above-climatology criterion holds for all three. Tier 5 is not the whole pass.

**The directive's premise does not reproduce.** It reads the parent as passing tier 1 and failing tiers 3 and 5 because 2020 is
over-forecast "about 0.16 against 0.016" and 2025 under-forecast "about 0.04 against 0.12". Under the judge in force the parent
**fails tier 1** (pooled 3.46 weighted, 4.38 flat, against a limit of 2; it passes only on the earlier counting, 1.64 weighted), 2020 is
predicted 0.028 against 0.016 at h = 1, and 2025–26 is **calibrated** (0.089 against 0.116, interval covering zero). The regime that
fails tier 3 for the parent is 2018–19, **under**-forecast (0.172 against 0.272, +0.100 [+0.045, +0.157]); the variants do not repair it
(0.186 against 0.272 for both).

## Predicted against realised, per regime (h = 1, +5 bp, flat rule; all horizons in `tables-by-regime.md`)

| regime | days | pressure days | parent predicted | (a) predicted | (c) predicted | realised |
|---|---|---|---|---|---|---|
| 2018–19 | 375 | 102 | 0.172 | 0.186 | 0.186 | 0.272 |
| **2020** | 251 | 4 | 0.028 | **0.140** | 0.080 | 0.016 |
| 2021–23 | 748 | 0 | 0.004 | 0.069 | 0.012 | 0.000 |
| 2024 | 250 | 5 | 0.018 | 0.053 | 0.005 | 0.020 |
| **2025–26** | 249 | 29 | 0.089 | 0.092 | 0.086 | 0.116 |

The recalibration **worsens 2020**: (a) over-forecasts it by 0.124 [0.108, 0.140] (the parent by 0.012) and (c) by 0.064. (a) also pushes 2024 into over-forecast
(0.053 against 0.020) and 2021–23 to 0.069 against 0.
2025–26 does not move (0.089 to 0.092 and 0.086; calibrated before and after).

## Paired against the parent (`paired-*.md`)

Brier difference at +5 bp, h = 1: the parent's squared error minus the variant's, so **positive favours the variant** (90% stationary
bootstrap; the Brier does not depend on the rule). `scripts/iorb_every_day_579.py`'s table header says the opposite; the sign stated here is the
one the statistic has (see the last section).

| cell | days | (a) state_platt | (c) state_shrunk |
|---|---|---|---|
| all | 1,873 | −0.0029 [−0.0062, +0.0008] | +0.0029 [−0.0001, +0.0062] |
| 2018–19 | 375 | +0.0050 [−0.0056, +0.0174] | +0.0050 [−0.0056, +0.0180] |
| 2020 | 251 | **−0.0157 [−0.0235, −0.0060]** | −0.0043 [−0.0128, +0.0043] |
| 2021–23 | 748 | **−0.0084 [−0.0102, −0.0067]** | −0.0002 [−0.0006, +0.0001] |
| 2024 | 250 | +0.0007 [−0.0046, +0.0073] | **+0.0066 [+0.0003, +0.0157]** |
| 2025–26 | 249 | **+0.0112 [+0.0019, +0.0220]** | **+0.0128 [+0.0033, +0.0247]** |
| month-end | 150 | **−0.0160 [−0.0269, −0.0052]** | −0.0042 [−0.0155, +0.0076] |
| ordinary | 1,603 | −0.0011 [−0.0039, +0.0022] | **+0.0040 [+0.0012, +0.0068]** |
| quarter-end | 31 | −0.0167 [−0.0444, +0.0106] | −0.0131 [−0.0431, +0.0145] |
| tax date | 89 | −0.0085 [−0.0275, +0.0122] | +0.0018 [−0.0159, +0.0222] |

Neither variant is better than the parent overall: (a) is worse in point value with an interval that covers zero, and (c) is better
in point value with an interval that just covers zero. Both **improve 2025–26**, the regime the directive names (interval above zero for
each). (a) is **significantly worse in 2020 and 2021–23** and on month-ends, which is what its calibration gaps above show (0.140 and 0.069
predicted against 0.016 and 0.000 realised). (c) is better on ordinary days and in 2024 and loses nothing significant anywhere.

## Recall by year (onsets flagged at some lead 1 to 5)

| rule | row | 2018 | 2019 | 2020 | 2024 | **2025** | all |
|---|---|---|---|---|---|---|---|
| weighted | parent | 0/4 | 13/13 | **2/2** | 0/2 | **4/5** | 19/26 |
| weighted | (a), (c) | 0/4 | 13/13 | 2/2 | 0/2 | 3/5 | 18/26 |
| flat | parent | 0/4 | 11/13 | **2/2** | 0/2 | **3/5** | 16/26 |
| flat | (a), (c) | 0/4 | 11/13 | 1/2 | 0/2 | 2/5 | 14/26 |

2020 and 2025 are the two years called out: each variant loses one 2025 onset under both rules and, under the flat rule, one of the two
2020 onsets. The paired recall differences (`paired-*.md`) have no interval where the cell holds two or five onsets.

## Result

No variant passes tier 1, tier 3 or the overall pass, and neither repairs the regime that fails tier 3 (2018–19, under-forecast). The
gain is in 2025–26, where both variants have a better Brier than the parent by a margin whose interval excludes zero; the cost is
recall (one 2025 onset under both rules, and under the flat rule one 2020 onset). (a) buys tier 5 (`calibrated`) at the price of a
2020 and 2021–23 over-forecast that is itself significant; (c) is the safer of the two (no significant loss in any cell, 2024 and 2025–26
better) and passes no tier the parent does not. Whether the state curves are fitted mostly on 2018–19 and carry its rate into 2020 was
not traced here.

## Reproduce

Published panel `4ddc3882…` (`verify-panel` clean); scratch panel built by `pressure_v1_1.py panel` then `measurement_fields.py panel`;
`/opt/rmm-venv` (numpy 2.4.6, scikit-learn 1.9.1), `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`. The exact commands are in the
docstring of `scripts/state_recalibration_589.py`. The parent's forecasts are the `own_leg` re-score of `announcement_dating_rescore.py`
(arm `both`) and `iorb_every_day_579.py` at each horizon.

## Not checked, or for Eleonora

- The judge was run on the benchmarks, the parent and the two variants only. Tier 5's risky set and some verdicts depend on which rows are
  judged together (tier 1's figures for the parent reproduce #586's exactly, 19 of 26 and 1.64 weighted), so a run with every row of
  #586 may differ in a verdict.
- #586's stored tier 1 verdicts for the iorb row ("yes") are on the earlier counting (worst single lead); under the judge in force the same
  row fails tier 1. That page and its evidence are not edited here.
- Variant (b) is not run (#587 is unmerged). Whether any variant joins the shortlist is hers (ruling on #567).
- Isotonic was not scored; Platt was declared.
- The paired-Brier table header in `scripts/iorb_every_day_579.py` says negative favours the row; the statistic is the reference's squared
  error minus the candidate's, so positive does. The same header is in `docs/pivot/iorb-every-day-result.md` and the compare tables of `docs/pivot/evidence/iorb-every-day/` and
  `docs/pivot/evidence/announcement-dating/` (same `announcement_dating_rescore.py compare` statistic); those pages are not edited here (a finding).
