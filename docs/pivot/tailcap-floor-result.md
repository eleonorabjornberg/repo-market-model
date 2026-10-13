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

## Step 2: three floors on `+tailcap75`

**These variants were built after seeing 2018-2025, including the failures they are meant to cure. A pass here is not a confirmation (ruling on
#567). A variant can replace a shortlist slot only by Eleonora's decision, before the 2026 window opens.** Nothing is published, no row joins the
frozen shortlist, and no day of 2026 is scored.

Declared in [`metadata/tailcap_floor_610.json`](../../metadata/tailcap_floor_610.json) and three judge candidates in `metadata/pressure_judge/candidates/`,
committed after the step-1 evidence and before the first variant was scored; `scripts/tailcap_floor_610.py` refuses an uncommitted declaration. Each
variant floors the forecasts of `+tailcap75` (no refit), walk-forward on the judge's cadence, from the earlier pairs observable at each block's fit.

| variant | row | rule |
|---|---|---|
| (a) floor | `...+tailcap75+floor` | on a day that is not a risk date the forecast is raised to the walk-forward rate of pressure days among the earlier such days (60 of them first): #606's floor |
| (b) floor by state | `...+tailcap75+state_floor` | as (a), the rate per as-of scarcity state once the state holds 60 such days and 3 pressure days |
| (c) recent floor | `...+tailcap75+recent_floor` | as (a), the rate taken over the most recent 60 earlier such days only. Chosen from step 1: the pooled floor lags a rate that rises within the year, and neither the start-up nor the state carries the shortfall. The window, 60, is the floor's own minimum, not searched |

### Result (weighted rule in force, flat rule beside it, +5 bp, h = 1 to 5)

| row | rule | tier 1: onsets flagged, recall [90%], pooled false alarms per onset (limit 2) | tier 1 | tier 3 | tier 5 |
|---|---|---|---|---|---|
| `risk_gbm+settle+h41+dist_roll` | weighted / flat | 15 of 26, 0.577 [0.400, 0.762], 1.27 / 1.85 | yes / yes | no | no |
| `+tailcap75` | weighted / flat | 18 of 26, 0.692 [0.522, 0.852], 1.88 / 2.62 | yes / no | no | no |
| (a) `+floor` | weighted / flat | 18 of 26, 0.692 [0.529, 0.850], 2.76 / 4.04 | no / no | no | **yes** |
| (b) `+state_floor` | weighted / flat | 18 of 26, 0.692 [0.522, 0.850], 2.76 / 4.04 | no / no | no | **yes** |
| (c) `+recent_floor` | weighted / flat | 18 of 26, 0.692 [0.514, 0.857], 2.60 / 3.31 | no / no | no | no |

**No variant passes.** (a) and (b) meet tier 5 and lose tier 1; (c) loses tier 1 and does not meet tier 5. No variant meets tier 3 at every lead.

- **Onsets kept and lost.** Each variant flags the same 18 onsets as `+tailcap75` (none lost, none gained; by date in
  [`evidence/tailcap-floor/onsets-weighted.md`](evidence/tailcap-floor/onsets-weighted.md)). Against `risk_gbm+settle+h41+dist_roll` the 18 against 15 is
  +0.115 [0.000, +0.267] for (a) (the interval for (b) is [0.000, +0.250] and for (c) [-0.030, +0.259]). The 2025 onsets: 4 of 5 for every variant, 2025-10-15
  never warned.
- **Where tier 1 fails.** False alarms rise at every lead: pooled weighted false alarms per onset 1.88 (`+tailcap75`) to 2.76, 2.76 and 2.60. It is a reading,
  not tested here, that a probability on every off-risk day moves more days over the judge's cut-off.
- **Tier 3, 2018-19 and 2025-26, h = 1** (realised minus predicted [90%]; predicted 0.1071 and 0.0395 for `+tailcap75`):

  | row | 2018-19 | 2025-26 |
  |---|---|---|
  | `+tailcap75` | +0.1649 [+0.0895, +0.2453], fails | +0.0769 [+0.0131, +0.1578], fails |
  | (a) `+floor` | +0.0966 [+0.0239, +0.1683], fails | +0.0373 [-0.0251, +0.1132], calibrated |
  | (b) `+state_floor` | +0.0966 [+0.0200, +0.1723], fails | +0.0205 [-0.0347, +0.0928], calibrated |
  | (c) `+recent_floor` | +0.0262 [-0.0505, +0.1066], **calibrated** | +0.0575 [-0.0005, +0.1351], calibrated |

  (a) and (b) are calibrated in 2025-26 at every lead and fail 2018-19 at every lead. (c) is calibrated in 2018-19 at every lead, and in 2025-26 only at h = 1
  (its lower end is 0.0005 below zero); at h = 2 to 5 it fails 2025-26. The two regimes are therefore never both calibrated at one lead by one variant.
  The floors over-forecast the quiet years: predicted against realised, 2021-23 (no pressure day), `+tailcap75` 0.0027, (a) and (b) 0.0698, (c) 0.0027;
  2020 (4 pressure days), (a) and (b) 0.1532 against 0.0159, (c) 0.0590. By pressure-day type the ordinary days are over-forecast by (a) and (b)
  (-0.0342 and -0.0367, intervals below zero) and calibrated by (c) (+0.0046 [-0.0139, +0.0252]).
- **Tier 5.** Realised minus predicted: `+tailcap75` +0.0537 [+0.0225, +0.0854]; (a) -0.0144 [-0.0480, +0.0190]; (b) -0.0157 [-0.0459, +0.0190]; (c) +0.0347
  [+0.0062, +0.0665]. Every row beats climatology on Brier. Full tables: [`evidence/tailcap-floor/calibration.md`](evidence/tailcap-floor/calibration.md).
- **Paired Brier difference** (the reference's squared error less the row's, so positive favours the row, #604), h = 1, +5 bp, 90% interval, all days, against
  `+tailcap75`: (a) +0.0008 [-0.0035, +0.0059]; (b) +0.0015 [-0.0031, +0.0069]; (c) +0.0068 [-0.0002, +0.0151]. All three cover zero over all days. By regime
  the floors help in 2018-19, where calibration improves: (a) +0.0289 [+0.0109, +0.0494], (c) +0.0340 [+0.0001, +0.0720]; and hurt in the quiet years: (a) in 2020
  -0.0201 [-0.0245, -0.0150] and 2021-23 -0.0064 [-0.0073, -0.0056]; (c) in 2020 -0.0057 [-0.0119, -0.0012]. Against `risk_gbm+settle+h41+dist_roll`: (a) +0.0010
  [-0.0036, +0.0065]; (c) +0.0069 [-0.0007, +0.0153]. All pairings by regime and pressure-day type are in `evidence/tailcap-floor/compare-*.md`.

### What this says, and does not

- The shortfall of 2018-19 is not closed by an input. Step 1 puts about a third of it on the short training window; the rest is not the window, the floor's
  start-up or the state. A floor that follows the recent rate (c) closes it at h = 1, at the price of tier 1 and of tier 3 in 2025-26 at h = 2 to 5.
- The combination of the two partial gains does not pass: `+tailcap75`'s tier 1 does not survive a floor, because the floor puts a probability on every
  off-risk day and the judge's cut-off then flags more of them.

## Not checked, or for Eleonora

- Whether any variant replaces a shortlist slot (#567) is her decision, before the 2026 window opens. None passes the pass rule and nothing here is a
  confirmation. No input or setting joins a published declaration, so no "Publish?" issue is raised.
- The 26 onsets are 17 in 2018-19, 2 in 2020, 2 in 2024 and 5 in 2025-26: a difference of one or two onsets is inside every interval.
- Only these three settings were tried; nothing was tuned on a scored day. The later-stretch comparison of step 1 is one stretch of 375 days with 34 pressure days.
- The interval for `+tailcap75`'s 2018-19 shortfall is [+0.0956, +0.2417] in step 1 (own bootstrap, seed 610) and [+0.0895, +0.2453] in the judge's table (the
  judge's seed); both exclude zero.
- Hindsight regime labels are not used (ruling on #515). The back-filled 2014-2018 history is not used (#572).

## Reproduce

Published panel `4ddc3882…` (`verify-panel` clean, unchanged); scratch panels `AUG`, `AUG2` and `AUG2D` as in
[`satiation-distance-result.md`](satiation-distance-result.md). `/opt/rmm-venv` (numpy 2.4.6, scikit-learn 1.9.1),
`OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`. The forecasts of `+tailcap75` are those of `scripts/every_day_conditioning_601.py cap`; the
commands are the docstring of `scripts/tailcap_floor_610.py` (`slice` and `diagnose` for step 1; `declare`, `run`, the judge under both rules,
`compare --reference tailcap|distroll`, `pg onsets`, `pg summary` and `calibration` for step 2).
