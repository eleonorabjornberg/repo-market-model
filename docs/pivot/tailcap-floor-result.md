# `+tailcap75` with the off-risk-date floor (#610)

A scratch measurement under the pressure-day judge. It writes nothing into `docs/runs/`, publishes nothing, moves no published figure, scores no
day of 2026 and reads no day after 2025-12-31 (`docs/decisions/lockbox.md`; the scripts refuse a later last day).

## Step 1: why `+tailcap75` under-forecasts in 2018-19

Committed before any step-2 declaration. Row `risk_gbm+every_day+gate+settle+h41+iorb+tailcap75` (PR #609), +5 bp. Tables for every lead and every
refit block: [`evidence/tailcap-floor-diagnosis/`](evidence/tailcap-floor-diagnosis/) (`diagnosis.md`, `diagnosis.json`);
`scripts/tailcap_floor_610.py diagnose` writes them.

At the first lead the 2018-19 scored days (375 days, 102 pressure days) have predicted 0.1071 against realised 0.2720: realised minus predicted
+0.1649 [+0.0956, +0.2417] (90% stationary bootstrap). At h = 2 to 5 it is +0.1591, +0.1523, +0.1582 and +0.1571, each interval above zero.

| source | what was measured | result at h = 1 |
|---|---|---|
| days that are not risk dates | the share of the shortfall carried by pressure days on them | 94% (62 of 102 pressure days; 0.1557 of 0.1649); 94% to 99% at h = 2 to 5 |
| the floor's own warm-up | pressure days on the 2018-19 off-risk days on which the floor cannot yet be fitted (fewer than 60 earlier observable off-risk pairs: the first 68 off-risk days, to October 2018) | none: 0 pressure days fall there at any lead. The floor is fitted from the 2018-10-30 refit on; the warm-up carries none of the shortfall |
| the floor's lag, once fitted | pooled floor against the block's realised off-risk rate | the floor rises from 0.00 to 0.22 over the year while the realised off-risk rate is 0.0 to 0.82 by block (refits of 2019-04 to 2019-10: floor 0.06 to 0.22, realised 0.41 to 0.82 in five of the seven). A rate over all earlier days follows a rate that is itself rising slowly |
| the length of the training window | the same row run on a later stretch of exactly 375 scored days (2024-07-01 to 2025-12-31), each refit trained on as many days as the matching 2018-19 refit (61 to 418) | later stretch +0.0570 [+0.0144, +0.1121]; 2018-19 less later +0.1079 [+0.0209, +0.1972]. A short training window under-forecasts in both (the later stretch's interval also excludes zero), about a third of the 2018-19 figure. The remainder, 0.108, is specific to the years, not to the window |
| the scarcity state | shortfall by the as-of state, each leg at its own latest public row (#586) | every 2018-19 day is in state 3 (375 of 375): the state does not split the shortfall at all, so a floor by state is the pooled floor |

Reading, stated plainly:

- **Part of the shortfall is a warm-up effect no input can fix, and part is not.** About a third (0.057 of 0.165) is what the same row does on any
  stretch with the same short training window; the stretch has 34 pressure days against 102, so this is a lower bound on what the window alone does.
  The rest (+0.108 [+0.021, +0.197]) is not the window's length, nor the floor's start-up, nor the state.
- **The floor's warm-up is not the cause.** The days before the floor can be fitted have no pressure day.
- **The state variant cannot differ from the pooled floor in 2018-19.** All 375 days are in one state.
- **What the floor does follow is slow.** A rate over every earlier off-risk day lags a rate that rises within the year. This is a reading from the
  block table, not a tested cause; step 2 (c) tests one remedy chosen from it.

Not tested here: whether a different training design would close the rest, because it needs a later stretch with as many pressure days; none exists
before 2026.
