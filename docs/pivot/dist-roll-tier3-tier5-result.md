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
