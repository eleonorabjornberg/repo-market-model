# The best tier-1 passer's tier 3 and tier 5 failures (#606)

A scratch measurement under the pressure-day judge. It writes nothing into `docs/runs/`, publishes nothing, moves no published
figure, scores no day of 2026 and reads no day after 2025-12-31 (`docs/decisions/lockbox.md`; the script refuses a later last day).

## Step 1: the diagnosis

`risk_gbm+settle+h41+dist_roll` (PR #605) and its parent `risk_gbm+settle+h41`, scored under the weighted rule in force, +5 bp,
h = 1 to 5. Committed before any step-2 declaration. The full tables, every regime at every lead, are in
[`evidence/dist-roll-diagnosis/diagnosis.md`](evidence/dist-roll-diagnosis/diagnosis.md) (and `diagnosis.json`);
`scripts/dist_roll_606.py diagnose` writes them from the judge's own output.

**Tier 3 fails in two regimes at every lead: 2018-19 and 2025-26.** The statistic is realised minus predicted rate of a pressure
day, with a 90% stationary-bootstrap interval; the threshold is that the interval covers zero. A regime is tested only with at
least 20 pressure days, which leaves these two (2020, 2024 and 2021-23 have 4, 5 and 0 pressure days and are reported only).

| row | regime | pressure days | predicted | realised | realised minus predicted [90% interval], h = 1 | margin at h = 1 | h = 2 to 5 |
|---|---|---|---|---|---|---|---|
| parent | 2018-19 | 102 | 0.0975 | 0.2720 | +0.1745 [+0.0952, +0.2540] | -0.0952 | fails at every lead |
| parent | 2025-26 | 29 | 0.0395 | 0.1165 | +0.0769 [+0.0142, +0.1585] | -0.0142 | fails at every lead |
| `+dist_roll` | 2018-19 | 102 | 0.0927 | 0.2720 | +0.1793 [+0.1046, +0.2532] | -0.1046 | fails at every lead |
| `+dist_roll` | 2025-26 | 29 | 0.0481 | 0.1165 | +0.0684 [+0.0051, +0.1500] | -0.0051 | fails at every lead |

The margin is the distance from the interval's nearer end to zero; negative means the interval excludes zero by that much. The
failing regimes are the under-forecast ones, as PR #602 found: 2018-19, not 2020 or 2025 alone. The input narrows 2025-26
(the interval's lower end at the first lead falls from 0.0142 to 0.0051 above zero) and does not close it.
For both rows the abundant-stretch half of tier 3 holds.

**Tier 5 fails on its calibration condition alone.** Beating climatology holds with room; calibration does not.

| row | decision days | weeks with a pressure day | mean forecast | calibrated: realised minus predicted [90% interval] | beats climatology (Brier, climatology minus row) [interval] |
|---|---|---|---|---|---|
| parent | 1869 | 284 | 0.0926 | +0.0594 [+0.0304, +0.0911] **fails**, lower end 0.0304 above zero | +0.0429 [+0.0308, +0.0563] holds, margin +0.0308 |
| `+dist_roll` | 1869 | 284 | 0.0903 | +0.0617 [+0.0342, +0.0931] **fails**, lower end 0.0342 above zero | +0.0474 [+0.0337, +0.0611] holds, margin +0.0337 |

**The misses do come from the risk-date part's zero forecast on days that are not risk dates.** The row forecasts exactly 0 on
a day that is neither a quarter-end, a month-end or a tax date nor a coupon-settlement day (`announcement_dating_rescore.risk_flag`;
the script refuses a non-zero forecast there). Pressure days at +5 bp, at h = 1, scored 2018-06-29 to 2025-12-31:

| row | regime | pressure days | of which not on a risk date | share of the shortfall carried by them |
|---|---|---|---|---|
| `+dist_roll` | all days | 140 | 82 | 91% |
| `+dist_roll` | 2018-19 (fails) | 102 | 62 | 92% |
| `+dist_roll` | 2025-26 (fails) | 29 | 15 | 88% |
| parent | all days | 140 | 82 | 92% |
| parent | 2018-19 (fails) | 102 | 62 | 95% |
| parent | 2025-26 (fails) | 29 | 15 | 78% |

At the other leads the counts are the same to within one or two days and the shares stay between 66% and 99% in the two failing
regimes (evidence table). For tier 5, the row forecasts exactly 0 for 740 of the 1869 decision days (no risk date among the next
five business days), and 74 of the 284 days with a pressure day are among them; those 74 carry 0.0396 of the 0.0617 mean
shortfall (64%). The input does not touch this: on a day that is not a risk date the row is 0 whatever the input says.

So the remedy has to put mass on the days the risk-date part does not model; a better risk-date forecast cannot. Step 2 is chosen
from this.

## Step 2: three recalibrations of the best row

**These variants were built after seeing 2018-2025, including the failures they are meant to cure. A pass here is not a confirmation
(ruling on #567). A variant can replace a shortlist slot only by Eleonora's decision, before the 2026 window opens.** Nothing is
published, no row joins the frozen shortlist, and no day of 2026 is scored.

Declared in [`metadata/dist_roll_606.json`](../../metadata/dist_roll_606.json) and the three judge candidates in
`metadata/pressure_judge/candidates/`, all committed after the step-1 page and before the first variant was scored;
`scripts/dist_roll_606.py` refuses an uncommitted declaration. Each variant recalibrates the best row's own forecasts (no refit of
the model) walk-forward on the judge's cadence, from the earlier pairs observable at each block's fit. The scarcity state is read as
of the decision instant; no hindsight regime label is used (ruling on #515).

| variant | row | rule |
|---|---|---|
| (a) floor | `risk_gbm+settle+h41+dist_roll+floor` | on a day that is not a risk date the forecast 0 is raised to the walk-forward rate of pressure days among the earlier such days (60 of them first) |
| (b) floor by state | `risk_gbm+settle+h41+dist_roll+state_floor` | as (a), the rate per as-of scarcity state once the state holds 60 such days and 3 pressure days |
| (c) state Platt | `risk_gbm+settle+h41+dist_roll+state_platt` | Platt per as-of scarcity state, the form that took tier 5 from no to yes in #602 |

### Result (weighted rule in force, +5 bp, h = 1 to 5)

| row | tier 1: onsets flagged / weighted false alarms per onset (limit 2) | tier 3: regimes calibrated (of the two tested), h = 1 | tier 5 | 2025 onsets warned | pass |
|---|---|---|---|---|---|
| best row (`+dist_roll`) | 15 of 26 / 1.27 | 0 of 2 | not met | 5 of 5 | no |
| (a) `+floor` | 18 of 26 / 2.94 | 1 of 2 (2025-26) | **met** | 5 of 5 | no |
| (b) `+state_floor` | 18 of 26 / 2.94 | 1 of 2 (2025-26) | **met** | 5 of 5 | no |
| (c) `+state_platt` | 14 of 26 / 3.22 | 1 of 2 (2025-26) | **met** | 3 of 5 | no |

- **No variant passes.** Each trades tier 1 for tier 5: the weighted false alarms per onset go from 1.27 to 2.94, 2.94 and 3.22, past the limit of 2, while
  tier 5's calibration condition now holds. The same gain does not reach tier 3's other regime.
- **Tier 5 is met by all three.** Week-ahead realised minus predicted, best row +0.0617 [+0.0342, +0.0931]; (a) -0.0114
  [-0.0436, +0.0225]; (b) -0.0125 [-0.0434, +0.0191]; (c) -0.0270 [-0.0633, +0.0125]. All three now over-forecast, mean forecast
  0.163 to 0.179 against a base rate of 0.152. Beating climatology on Brier holds for every row.
- **Tier 3 is calibrated in 2025-26 and still fails in 2018-19.** Realised minus predicted in 2025-26 at h = 1: (a) +0.0288
  [-0.0348, +0.1095]; (b) +0.0120 [-0.0435, +0.0837]; (c) +0.0365 [-0.0178, +0.1072], each covering zero (the best row: +0.0684
  [+0.0051, +0.1500]). In 2018-19 the interval still excludes zero for every variant: (a) +0.1059 [+0.0301, +0.1791]; (b) +0.1059
  [+0.0327, +0.1773]; (c) +0.1307 [+0.0552, +0.2078], against +0.1793 for the best row. 2018-19 is the first two years of the scored window, where a walk-forward rate has the least
  history; this measurement does not separate that from a model defect.
- **Where tier 1 fails.** The false alarms rise at every lead alone (Table 1b, lead 1 alone, weighted: 0.875 for the best row,
  2.587 for (a) and (b), 1.702 for (c)). It is a reading, not tested here, that a probability on every non-risk day moves more
  days over the judge's cut-off. Recall rises (15 to 18 of 26 for (a) and (b)), driven by 2019 (10 of 13
  to 13 of 13); (c) loses two 2025 onsets (3 of 5) and 14 of 26 overall.
- **Calibration over-corrects outside the failing regimes.** Predicted against realised at +5 bp, pooled over h = 1 to 5, 2021-23:
  best row 0.0007 against 0.0000; (a) and (b) 0.0703, (c) 0.0918: the high rate of the early years is carried into quiet ones. This does not
  matter for tier 3 (that regime has no pressure day and is not tested); it is a reading, not tested here, that it contributes to tier 1's false alarms.
- **Brier against the best row** (reference minus row, positive when the row is better), pooled, h = 1 / 5: (a) +0.0011 [-0.0032,
  +0.0065] / +0.0008 [-0.0036, +0.0058]; (b) +0.0018 [-0.0028, +0.0071] / +0.0014 [-0.0030, +0.0065]; (c) -0.0043 [-0.0095, +0.0013]
  / -0.0059 [-0.0098, -0.0015]. For (a) and (b) every interval includes zero; (c) is worse at h = 3 to 5, with intervals below zero.
  Onset recall difference against the best row, pooled: (a) and (b) +0.115 [0.000, 0.231]; (c) -0.038 [-0.158, +0.071] on 26 onsets.
- The three variants, one of which is a Platt curve, lose tier 1 alike. It is a reading, not tested here, that a remedy has to tell
  the non-risk days that are likely pressure days from the rest, which a constant per state cannot.

## Not checked, or for Eleonora

- **Whether any variant replaces a shortlist slot** (#567) is her decision, before the 2026 window opens. None passes the pass rule,
  and nothing here is a confirmation. No "Publish?" issue is raised: no input joins a published declaration.
- The 26 onsets are 17 in 2018-19, 2 in 2020, 2 in 2024 and 5 in 2025: a difference of one or two onsets is inside every interval.
- Only these three settings were tried; nothing was tuned on a scored day. The 2018-19 shortfall
  is a start-up problem (no earlier history for any as-of rule), which this measurement cannot separate from a model defect.
- Hindsight regime labels are not used, per the ruling on #515. The state is the as-of one in force on main (#586).

## Reproduce

Published panel `4ddc3882…` (`verify-panel` clean, unchanged); scratch panels `AUG`, `AUG2` and `AUG2D` as in
[`satiation-distance-result.md`](satiation-distance-result.md). `/opt/rmm-venv` (numpy 2.4.6, scikit-learn 1.9.1),
`OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`. The commands are the module docstring of `scripts/dist_roll_606.py`:
`diagnose` for step 1; `declare`, `run`, the judge under both rules, `compare` and `report` for step 2. The best row's forecasts are
those of `scripts/satiation_distance_598.py run`.

Evidence: [`evidence/dist-roll-diagnosis/`](evidence/dist-roll-diagnosis/) (`diagnosis.md`, `diagnosis.json`) and
[`evidence/dist-roll-recalibration/`](evidence/dist-roll-recalibration/) (`report.md`; `compare.json` and `compare.md`;
`judge-weighted.md` and `judge-unweighted.md`).
