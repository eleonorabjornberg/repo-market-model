# Skill on the days that are not risk dates (#624)

**Status: a measurement, not a record.** Step 1 is below and step 2 follows it; step 1 was committed before step 2 was declared. Nothing is published, no day after 2025-12-31 is scored (`docs/decisions/lockbox.md`), and the live record and pin do not move.
Every figure reads 2018-2025, so it describes that history and does not confirm anything (Eleonora's ruling of 11 October 2026 on #567).

## Step 1: do the every-day parts have skill beyond the base rate on those days?

The question (#616): tiers 3 and 5 check calibration on the mean only, so a constant floor can pass them without any skill. The measurement asks
of the part that serves the days that are not risk dates in five rows whether it ranks those days, and whether it beats the walk-forward
climatology, per lead 1 to 5, for a pressure day at +5 bp. `ROW` below is `risk_gbm+every_day+gate+settle+h41+iorb` (#579, PR #582),
`ROW+tailcap75` is the row capped by the tail spread's trailing history (#601, PR #609), and the three floors of #610 (PR #612) are in
the evidence file (`ROW+tailcap75+floor`, `+state_floor`, `+recent_floor`).

The declaration is `metadata/off_risk_day_624_step1.json` and the script `scripts/off_risk_day_624.py measure`; both were committed before the
first score. Statistics: AUROC (ties half); Brier skill, 1 less the row's Brier score over that of the walk-forward climatology (the pooled
rate of pressure days among the earlier days that were not risk dates, observable at the block's fit, once 60 such days exist); and the
reliability curve's slope and intercept, the logistic recalibration of the outcome on the logit of the forecast, on the days on which the
forecast is above 1e-4. Intervals are the judge's 90% stationary bootstrap (block length 10, 2000 replications, seed 624).

| row | lead | AUROC, all days [90%] | Brier skill, all days [90%] | slope, all days [90%] | AUROC, regime 2018-19 [90%] | Brier skill, regime 2018-19 [90%] |
|---|---|---|---|---|---|---|
| `ROW` | 1 | 0.736 [0.668, 0.788] | 0.166 [0.060, 0.270] | 0.487 [0.315, 0.878] | 0.700 [0.627, 0.764] | 0.093 [-0.052, 0.210] |
| `ROW` | 2 | 0.735 [0.649, 0.804] | 0.089 [-0.009, 0.196] | 0.566 [0.374, 0.950] | 0.682 [0.585, 0.759] | 0.003 [-0.127, 0.103] |
| `ROW` | 3 | 0.704 [0.601, 0.775] | 0.075 [-0.025, 0.179] | 0.445 [0.189, 1.090] | 0.648 [0.533, 0.730] | -0.037 [-0.180, 0.067] |
| `ROW` | 4 | 0.747 [0.664, 0.803] | 0.108 [0.019, 0.204] | 0.648 [0.387, 1.076] | 0.691 [0.597, 0.760] | 0.029 [-0.061, 0.102] |
| `ROW` | 5 | 0.744 [0.657, 0.807] | 0.103 [0.012, 0.203] | 0.559 [0.310, 0.983] | 0.682 [0.580, 0.769] | -0.013 [-0.128, 0.079] |
| `ROW+tailcap75` | 1 | 0.493 [0.473, 0.514] | -0.005 [-0.098, 0.139] | 2.035 [1.465, 5.860] | 0.486 [0.453, 0.514] | -0.202 [-0.283, -0.099] |
| `ROW+tailcap75` | 2 | 0.520 [0.481, 0.557] | 0.000 [-0.086, 0.135] | 2.659 [1.525, 7.542] | 0.500 [0.443, 0.555] | -0.175 [-0.260, -0.073] |
| `ROW+tailcap75` | 3 | 0.501 [0.470, 0.533] | -0.014 [-0.104, 0.123] | 3.186 [1.839, 8.704] | 0.474 [0.420, 0.525] | -0.195 [-0.283, -0.089] |
| `ROW+tailcap75` | 4 | 0.519 [0.482, 0.560] | -0.003 [-0.096, 0.139] | 1.824 [1.144, 3.889] | 0.505 [0.456, 0.556] | -0.181 [-0.279, -0.067] |
| `ROW+tailcap75` | 5 | 0.528 [0.494, 0.565] | 0.010 [-0.076, 0.143] | 2.396 [1.609, 4.642] | 0.519 [0.479, 0.565] | -0.163 [-0.248, -0.062] |
| `ROW+tailcap75+floor` | 1 | 0.574 [0.402, 0.715] | 0.015 [-0.002, 0.036] | 0.465 [-0.417, 1.283] | 0.659 [0.515, 0.779] | 0.011 [-0.007, 0.035] |
| `ROW+tailcap75+floor` | 2 | 0.574 [0.397, 0.720] | 0.006 [-0.003, 0.015] | 0.385 [-0.779, 1.423] | 0.656 [0.521, 0.773] | 0.010 [-0.006, 0.023] |
| `ROW+tailcap75+floor` | 3 | 0.558 [0.384, 0.705] | 0.001 [-0.006, 0.007] | 0.273 [-0.880, 1.303] | 0.648 [0.509, 0.768] | 0.002 [-0.010, 0.012] |
| `ROW+tailcap75+floor` | 4 | 0.564 [0.392, 0.718] | 0.004 [-0.002, 0.010] | 0.398 [-0.656, 1.438] | 0.647 [0.514, 0.766] | 0.006 [-0.004, 0.015] |
| `ROW+tailcap75+floor` | 5 | 0.556 [0.380, 0.704] | 0.005 [-0.001, 0.010] | 0.456 [-0.629, 1.458] | 0.658 [0.529, 0.772] | 0.008 [-0.001, 0.016] |
| `ROW+tailcap75+recent_floor` | 1 | 0.870 [0.805, 0.916] | 0.154 [0.066, 0.250] | 0.571 [0.329, 0.863] | 0.684 [0.556, 0.797] | 0.049 [-0.120, 0.163] |
| `ROW+tailcap75+recent_floor` | 2 | 0.859 [0.786, 0.913] | 0.136 [0.049, 0.231] | 0.549 [0.280, 0.851] | 0.681 [0.554, 0.795] | 0.044 [-0.122, 0.155] |
| `ROW+tailcap75+recent_floor` | 3 | 0.848 [0.764, 0.909] | 0.131 [0.043, 0.223] | 0.526 [0.234, 0.847] | 0.683 [0.559, 0.797] | 0.046 [-0.122, 0.157] |
| `ROW+tailcap75+recent_floor` | 4 | 0.840 [0.751, 0.910] | 0.132 [0.043, 0.230] | 0.579 [0.287, 0.895] | 0.687 [0.572, 0.796] | 0.048 [-0.109, 0.160] |
| `ROW+tailcap75+recent_floor` | 5 | 0.838 [0.746, 0.904] | 0.130 [0.040, 0.226] | 0.595 [0.318, 0.910] | 0.676 [0.551, 0.788] | 0.041 [-0.140, 0.155] |
| `ROW+tailcap75+state_floor` | 1 | 0.639 [0.501, 0.756] | 0.030 [0.004, 0.060] | 0.725 [0.068, 1.636] | 0.659 [0.515, 0.779] | 0.011 [-0.007, 0.035] |
| `ROW+tailcap75+state_floor` | 2 | 0.641 [0.499, 0.765] | 0.021 [-0.000, 0.045] | 0.734 [-0.243, 1.799] | 0.656 [0.521, 0.773] | 0.010 [-0.006, 0.023] |
| `ROW+tailcap75+state_floor` | 3 | 0.627 [0.484, 0.753] | 0.016 [-0.005, 0.040] | 0.627 [-0.350, 1.688] | 0.648 [0.509, 0.768] | 0.002 [-0.010, 0.012] |
| `ROW+tailcap75+state_floor` | 4 | 0.632 [0.492, 0.760] | 0.019 [-0.002, 0.041] | 0.755 [-0.136, 1.811] | 0.647 [0.514, 0.766] | 0.006 [-0.004, 0.015] |
| `ROW+tailcap75+state_floor` | 5 | 0.615 [0.462, 0.743] | 0.017 [0.000, 0.038] | 0.758 [-0.181, 1.759] | 0.658 [0.529, 0.772] | 0.008 [-0.001, 0.016] |

The full tables, with the intercepts and the split by regime and by as-of scarcity state at every lead, are in
`docs/pivot/evidence/off-risk-day/step1.md`.

### What step 1 says

Whether any of them has skill on these days beyond the base rate, stated plainly:

* **`ROW` (the uncapped control) ranks the days, and is the only row whose own forecast does.** Its AUROC is 0.70 to 0.75 over all days with an
  interval above 0.5 at every lead, and 0.65 to 0.70 inside 2018-19 (every one of those days is in as-of scarcity state 3, so the state does not
  separate them there). Its Brier skill over the walk-forward climatology has an interval that excludes 0 at leads 1, 4 and 5 and includes it at leads
  2 and 3; inside 2018-19 it includes 0 at every lead. The forecast is too spread out for its ranking: the reliability slope is 0.45 to 0.65, and
  the intercept is negative. On a day it forecasts exactly 0 (the gate), 33 to 40 of the 82 pressure days fall. By the rule declared before the
  first score (a Brier skill and an AUROC interval that both exclude their nulls from above) it has skill at leads 1, 4 and 5 over all days, and
  by neither measure inside 2018-19.
* **`ROW+tailcap75` has none.** Its AUROC is 0.49 to 0.53 and its Brier skill is 0.00 within an interval that holds 0, and inside 2018-19 it is
  worse than the climatology (skill about -0.2, interval below 0 at every lead). The cap, which took tier 5 from "not met" to "met" (#609), removes
  what ranking the control had and leaves a forecast that is 0 on nearly every day (73 to 79 of the 82 pressure days fall on a zero forecast).
* **The constant floors rank little.** `+floor` and `+state_floor` forecast one number per refit block, so what ranking they show (AUROC 0.56
  to 0.64, intervals that mostly hold 0.5) is the rate drifting up through 2018-19. Their Brier skill is 0.00 to 0.03; the only intervals that
  exclude 0 are `+state_floor` at lead 1 (0.030, [0.004, 0.060]) and, by 0.0002, at lead 5 (0.017). A floor that passes tiers 3 and 5 through the mean (#616) does so without skill.
* **`+recent_floor` (the rate over the 60 most recent earlier days that were not risk dates) is the largest pooled figure,** AUROC 0.84 to 0.87 and
  Brier skill 0.13 to 0.15 with intervals that exclude 0 at every lead, and nearly all of it is the split between a regime with many pressure days
  and the regimes with none: inside 2018-19 its AUROC is 0.68 (about 0.55 to 0.80) and its Brier skill about 0.05 with an interval that holds 0. A
  trailing rate tracks the regime; it does not rank the days within it.

The skill that exists on these days is therefore in the control's own inputs (the spread and the SOFR 75th and 99th percentiles above IORB), not in
the cap or the floors, and part of what looks like skill pooled is the regime. A forecast that ranks days inside a regime is what step 2 builds.
Five rows at five leads are read, so about one interval in ten that has no skill would exclude its null by chance.

### Reproduction

The forecast files are regenerated from the tracked fixtures with the commands of `scripts/satiation_distance_598.py` (the panels, the
benchmarks, the parents, `both_h?.json`, `dist_h?.json`), `scripts/iorb_every_day_579.py run` (`iorb_h?.json`),
`scripts/every_day_conditioning_601.py cap` (`cap_h?.json`) and `scripts/tailcap_floor_610.py run` on the branch of PR #612 (`v610_h?.json`).
The panel digest is `4ddc3882…` (`verify-panel` passes). Then:

```
PYTHONPATH=src python3 scripts/off_risk_day_624.py measure --panel PUBLISHED.csv --scratch AUG2.csv \
    --row 'risk_gbm+every_day+gate+settle+h41+iorb=OUT/iorb_h{h}.json' \
    --row 'risk_gbm+every_day+gate+settle+h41+iorb+tailcap75=OUT/cap_h{h}.json' \
    --row 'risk_gbm+every_day+gate+settle+h41+iorb+tailcap75+floor=OUT/v610_h{h}.json' \
    --row 'risk_gbm+every_day+gate+settle+h41+iorb+tailcap75+state_floor=OUT/v610_h{h}.json' \
    --row 'risk_gbm+every_day+gate+settle+h41+iorb+tailcap75+recent_floor=OUT/v610_h{h}.json' \
    --output OUT/step1.json --markdown OUT/step1.md
PYTHONPATH=src python3 scripts/off_risk_day_624.py summary --input OUT/step1.json --output OUT/step1_summary.md
```


## Step 2: a day-level model on those days, in place of the constant 0

**Declared before any score** in `metadata/off_risk_day_624.json` (and one candidate file per variant in `metadata/pressure_judge/candidates/`),
committed after step 1 and before any variant was run. Each variant replaces the constant 0 that `risk_gbm+settle+h41+dist_roll` forecasts on a
day that is not a risk date with a model fitted walk-forward on those days only (the judge's refit cadence; a block trains on the earlier such days
whose outcome was observable at its fit and serves the block's such days). A risk date keeps the parent's forecast. Inputs, each read at the day's
own decision instant through the as-of rule: the tail spread's level (SOFR 99th percentile less IORB) and its change over 5 scored days, the SOFR
dispersion (99th less 1st percentile), the rolling satiation distance, and the as-of reserve-scarcity state (each leg at its own latest row, #586).
No regime label enters a fit (ruling on #515) and no back-filled 2014-2018 history is used (#572).

* `+offday` (a): a ridge logistic on the four inputs, the state, and each input times the state.
* `+offday_mono` (b): the gradient-boosted classifier on the four inputs and the state, with a monotone constraint of +1 on the state.
* `+offday_rate` (c), chosen from step 1: as (a) with the trailing rate of pressure days over the 60 most recent earlier such days observable at the
  block's fit as one more input (the only row of step 1 whose pooled figures separate from the climatology at every lead).

**The satiation distance was built per H.4.1 release, as #622 requires** (`scripts/off_risk_day_624.py panel`); #623 had not landed. The build
differs from the old-lag build of `scripts/satiation_distance_598.py panel` on 1,592 rows, the count #622 gives. The parent
row's own forecasts (the risk-date part) are #598's and are unchanged, so the parent here is the row as it stands on main; the figures for it
(`+dist_roll`, `+tailcap75`) reproduce the merged pages (for example 15 of 26 onsets at 1.27 false alarms per onset for `+dist_roll`, and 18 of 26
at 1.88 for `+tailcap75`, weighted).

### Under the judge in force

Tier 1 pooled over leads 1 to 5 and over leads 3 to 5 (onsets flagged, recall with its 90% interval, pooled false alarms per onset, limit 2), then
tiers 3 and 5, under the weighted rule in force with the flat rule beside it. The judge, its bar and its cut-offs are unchanged.

| row | rule | tier 1, leads 1 to 5: onsets flagged, recall [90%], pooled false alarms per onset (limit 2) | tier 1 | tier 1, leads 3 to 5: onsets flagged, recall [90%], pooled false alarms per onset | tier 3 | tier 5 | passes |
|---|---|---|---|---|---|---|---|
| risk_gbm+settle+h41 | flat | 14 of 26, 0.538 [0.353, 0.710], 2.00 | yes | 11 of 26, 0.423 [0.250, 0.607], 1.58 | no | no | no |
| risk_gbm+settle+h41 | weighted | 14 of 26, 0.538 [0.353, 0.710], 1.44 | yes | 11 of 26, 0.423 [0.250, 0.607], 1.23 | no | no | no |
| risk_gbm+settle+h41+dist_roll | flat | 15 of 26, 0.577 [0.400, 0.762], 1.85 | yes | 12 of 26, 0.462 [0.286, 0.643], 1.35 | no | no | no |
| risk_gbm+settle+h41+dist_roll | weighted | 15 of 26, 0.577 [0.400, 0.762], 1.27 | yes | 12 of 26, 0.462 [0.286, 0.643], 0.87 | no | no | no |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 | flat | 17 of 26, 0.654 [0.480, 0.818], 2.62 | no | 13 of 26, 0.500 [0.312, 0.692], 2.23 | no | no | no |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 | weighted | 18 of 26, 0.692 [0.522, 0.852], 1.88 | yes | 14 of 26, 0.538 [0.344, 0.731], 1.62 | no | no | no |
| risk_gbm+settle+h41+dist_roll+offday | flat | 16 of 26, 0.615 [0.429, 0.792], 3.58 | no | 12 of 26, 0.462 [0.280, 0.667], 3.08 | no | no | no |
| risk_gbm+settle+h41+dist_roll+offday | weighted | 17 of 26, 0.654 [0.476, 0.828], 2.55 | no | 13 of 26, 0.500 [0.316, 0.700], 2.08 | no | no | no |
| risk_gbm+settle+h41+dist_roll+offday_mono | flat | 18 of 26, 0.692 [0.500, 0.862], 4.65 | no | 14 of 26, 0.538 [0.350, 0.733], 3.54 | no | no | no |
| risk_gbm+settle+h41+dist_roll+offday_mono | weighted | 18 of 26, 0.692 [0.500, 0.862], 2.88 | no | 14 of 26, 0.538 [0.350, 0.733], 2.09 | no | no | no |
| risk_gbm+settle+h41+dist_roll+offday_rate | flat | 17 of 26, 0.654 [0.478, 0.824], 3.85 | no | 14 of 26, 0.538 [0.333, 0.733], 3.50 | yes | no | no |
| risk_gbm+settle+h41+dist_roll+offday_rate | weighted | 18 of 26, 0.692 [0.519, 0.864], 2.42 | no | 14 of 26, 0.538 [0.333, 0.733], 2.08 | yes | no | no |

Tier 1 per lead: flags (false alarms); onsets flagged of onsets; false alarms per onset, +5 bp, weighted rule.

Table 2. Flags at +5 bp, by horizon: flags (false alarms); onsets flagged of onsets; false alarms per onset.

| row | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|
| calendar_climatology | 258(174); 12/27; 6.44 | 213(144); 10/26; 5.54 | 213(145); 10/26; 5.58 | 213(146); 10/26; 5.62 | 213(147); 10/26; 5.65 |
| persistence_logistic | 286(183); 11/27; 6.78 | 215(124); 7/26; 4.77 | 243(154); 10/26; 5.92 | 222(140); 8/26; 5.38 | 199(118); 8/26; 4.54 |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 | 92(48); 14/27; 1.78 | 84(39); 12/26; 1.50 | 95(51); 11/26; 1.96 | 89(46); 12/26; 1.77 | 93(48); 14/26; 1.85 |
| risk_gbm+settle+h41+dist_roll | 81(39); 13/27; 1.44 | 63(22); 12/26; 0.85 | 65(25); 9/26; 0.96 | 60(22); 10/26; 0.85 | 63(25); 11/26; 0.96 |
| risk_gbm+settle+h41+dist_roll+offday | 232(132); 15/27; 4.89 | 197(109); 14/26; 4.19 | 196(112); 10/26; 4.31 | 168(96); 11/26; 3.69 | 153(82); 12/26; 3.15 |
| risk_gbm+settle+h41+dist_roll+offday_mono | 178(93); 15/27; 3.44 | 140(72); 12/26; 2.77 | 180(103); 9/26; 3.96 | 153(85); 13/26; 3.27 | 153(84); 13/26; 3.23 |
| risk_gbm+settle+h41+dist_roll+offday_rate | 209(117); 16/27; 4.33 | 201(111); 15/26; 4.27 | 204(118); 10/26; 4.54 | 197(113); 13/26; 4.35 | 196(115); 14/26; 4.42 |

Tier 3 per lead and tier 5 (calibration and the Brier difference against climatology) are in `docs/pivot/evidence/off-risk-day/calibration.md`:
tier 3 holds at every lead in both regimes for `+offday_rate` only; `+offday_mono` holds in 2018-19 at leads 3 to 5 only; `+offday` fails 2018-19
at every lead. Tier 5's calibration condition fails for all three (each under-forecasts: realised less predicted is +0.037, +0.028 and +0.032,
intervals above 0), and its Brier difference against climatology is +0.063 for each, against +0.047 for the parent.

### On the days that are not risk dates

AUROC, Brier skill against the walk-forward climatology and the reliability slope, per lead, all days and inside 2018-19 (the full tables, by
regime and scarcity state, are in `docs/pivot/evidence/off-risk-day/step2-off-risk-days.md`). `risk_gbm+settle+h41+dist_roll` forecasts exactly 0
here, so it ranks nothing (AUROC 0.5) and sits below the climatology inside 2018-19.

| row | lead | AUROC, all days [90%] | Brier skill, all days [90%] | slope, all days [90%] | AUROC, regime 2018-19 [90%] | Brier skill, regime 2018-19 [90%] |
|---|---|---|---|---|---|---|
| `ROW+tailcap75` | 1 | 0.493 [0.473, 0.514] | -0.005 [-0.098, 0.139] | 2.035 [1.465, 5.860] | 0.486 [0.453, 0.514] | -0.202 [-0.283, -0.099] |
| `ROW+tailcap75` | 2 | 0.520 [0.481, 0.557] | 0.000 [-0.086, 0.135] | 2.659 [1.525, 7.542] | 0.500 [0.443, 0.555] | -0.175 [-0.260, -0.073] |
| `ROW+tailcap75` | 3 | 0.501 [0.470, 0.533] | -0.014 [-0.104, 0.123] | 3.186 [1.839, 8.704] | 0.474 [0.420, 0.525] | -0.195 [-0.283, -0.089] |
| `ROW+tailcap75` | 4 | 0.519 [0.482, 0.560] | -0.003 [-0.096, 0.139] | 1.824 [1.144, 3.889] | 0.505 [0.456, 0.556] | -0.181 [-0.279, -0.067] |
| `ROW+tailcap75` | 5 | 0.528 [0.494, 0.565] | 0.010 [-0.076, 0.143] | 2.396 [1.609, 4.642] | 0.519 [0.479, 0.565] | -0.163 [-0.248, -0.062] |
| `risk_gbm+settle+h41+dist_roll` | 1 | 0.500 [0.500, 0.500] | -0.027 [-0.117, 0.117] | – | 0.500 [0.500, 0.500] | -0.218 [-0.299, -0.112] |
| `risk_gbm+settle+h41+dist_roll` | 2 | 0.500 [0.500, 0.500] | -0.025 [-0.116, 0.119] | – | 0.500 [0.500, 0.500] | -0.215 [-0.296, -0.109] |
| `risk_gbm+settle+h41+dist_roll` | 3 | 0.500 [0.500, 0.500] | -0.023 [-0.115, 0.120] | – | 0.500 [0.500, 0.500] | -0.213 [-0.296, -0.106] |
| `risk_gbm+settle+h41+dist_roll` | 4 | 0.500 [0.500, 0.500] | -0.021 [-0.115, 0.125] | – | 0.500 [0.500, 0.500] | -0.212 [-0.300, -0.099] |
| `risk_gbm+settle+h41+dist_roll` | 5 | 0.500 [0.500, 0.500] | -0.019 [-0.111, 0.120] | – | 0.500 [0.500, 0.500] | -0.211 [-0.297, -0.099] |
| `risk_gbm+settle+h41+dist_roll+offday` | 1 | 0.887 [0.791, 0.944] | 0.237 [0.165, 0.323] | 0.829 [0.687, 1.027] | 0.786 [0.694, 0.866] | 0.146 [0.055, 0.231] |
| `risk_gbm+settle+h41+dist_roll+offday` | 2 | 0.867 [0.760, 0.931] | 0.187 [0.121, 0.274] | 0.853 [0.712, 1.070] | 0.735 [0.628, 0.822] | 0.081 [0.009, 0.142] |
| `risk_gbm+settle+h41+dist_roll+offday` | 3 | 0.855 [0.746, 0.920] | 0.148 [0.082, 0.237] | 0.800 [0.676, 0.974] | 0.693 [0.582, 0.785] | 0.019 [-0.059, 0.072] |
| `risk_gbm+settle+h41+dist_roll+offday` | 4 | 0.849 [0.744, 0.915] | 0.148 [0.087, 0.237] | 0.778 [0.650, 0.951] | 0.679 [0.568, 0.777] | 0.008 [-0.059, 0.054] |
| `risk_gbm+settle+h41+dist_roll+offday` | 5 | 0.845 [0.739, 0.912] | 0.163 [0.105, 0.251] | 0.791 [0.657, 0.989] | 0.694 [0.583, 0.792] | 0.039 [-0.014, 0.086] |
| `risk_gbm+settle+h41+dist_roll+offday_mono` | 1 | 0.864 [0.765, 0.923] | 0.167 [0.063, 0.276] | 0.458 [0.378, 0.562] | 0.791 [0.699, 0.858] | 0.099 [-0.069, 0.215] |
| `risk_gbm+settle+h41+dist_roll+offday_mono` | 2 | 0.853 [0.747, 0.919] | 0.047 [-0.074, 0.182] | 0.387 [0.303, 0.488] | 0.713 [0.607, 0.802] | -0.060 [-0.223, 0.071] |
| `risk_gbm+settle+h41+dist_roll+offday_mono` | 3 | 0.858 [0.755, 0.922] | 0.017 [-0.112, 0.150] | 0.356 [0.283, 0.450] | 0.690 [0.583, 0.782] | -0.126 [-0.331, 0.012] |
| `risk_gbm+settle+h41+dist_roll+offday_mono` | 4 | 0.843 [0.739, 0.909] | 0.036 [-0.086, 0.161] | 0.367 [0.285, 0.481] | 0.699 [0.595, 0.789] | -0.116 [-0.331, 0.034] |
| `risk_gbm+settle+h41+dist_roll+offday_mono` | 5 | 0.845 [0.741, 0.911] | 0.072 [-0.031, 0.191] | 0.323 [0.241, 0.432] | 0.707 [0.598, 0.797] | -0.054 [-0.219, 0.073] |
| `risk_gbm+settle+h41+dist_roll+offday_rate` | 1 | 0.861 [0.752, 0.926] | 0.191 [0.082, 0.300] | 0.732 [0.624, 0.859] | 0.744 [0.640, 0.831] | 0.069 [-0.118, 0.207] |
| `risk_gbm+settle+h41+dist_roll+offday_rate` | 2 | 0.846 [0.737, 0.912] | 0.139 [0.023, 0.255] | 0.699 [0.580, 0.833] | 0.714 [0.609, 0.805] | 0.010 [-0.194, 0.147] |
| `risk_gbm+settle+h41+dist_roll+offday_rate` | 3 | 0.843 [0.735, 0.906] | 0.101 [-0.016, 0.219] | 0.671 [0.559, 0.792] | 0.691 [0.582, 0.787] | -0.053 [-0.260, 0.085] |
| `risk_gbm+settle+h41+dist_roll+offday_rate` | 4 | 0.834 [0.727, 0.902] | 0.100 [-0.017, 0.215] | 0.651 [0.528, 0.788] | 0.682 [0.576, 0.779] | -0.062 [-0.257, 0.069] |
| `risk_gbm+settle+h41+dist_roll+offday_rate` | 5 | 0.828 [0.723, 0.896] | 0.093 [-0.017, 0.200] | 0.643 [0.517, 0.791] | 0.680 [0.560, 0.781] | -0.063 [-0.277, 0.067] |

### Paired against the parent and against `+tailcap75`

Paired Brier difference at +5 bp, h = 1, 90% stationary bootstrap, positive favours the variant (#604), weighted rule. Against
`+dist_roll`: `+offday` +0.0113 [+0.0042, +0.0194] over all days and +0.0494 [+0.0200, +0.0843] inside 2018-19; `+offday_mono` +0.0083
[+0.0012, +0.0164] and +0.0430 [+0.0106, +0.0792]; `+offday_rate` +0.0093 [+0.0018, +0.0185] and +0.0389 [+0.0048, +0.0821]. In 2025-26 none of
the three differs from the parent (intervals hold 0), and the quarter-end and tax-date days, which are risk dates, do not move at all. Against
`+tailcap75`: +0.0111 [+0.0042, +0.0192], +0.0081 [+0.0011, +0.0164] and +0.0091 [+0.0010, +0.0181] over all days. The tables for both references, by
regime and by pressure-day type, and under the flat rule, are `compare-distroll-*.md` and `compare-tailcap-*.md` in the evidence folder.

### Onsets kept and lost, by date (weighted rule, any lead 1 to 5)

Against `+dist_roll` (15 of 26): `+offday` gains 2019-05-28 and 2019-08-13; `+offday_mono` and `+offday_rate` gain those and 2019-06-25; none loses
an onset. Against `+tailcap75` (18 of 26): each gains 2025-10-15, each loses 2020-03-04, and `+offday` also loses 2019-06-25. The per-onset table is
`onsets-distroll-weighted.md` and `onsets-tailcap-weighted.md`.

### What step 2 says

* **None of the three passes the judge.** Each raises onset recall (17 or 18 of 26 against 15) and each fails tier 1 on the pooled false-alarm count
  (2.42 to 2.88 per onset against a limit of 2, weighted; 3.58 to 4.65 flat): a model that puts mass on every ordinary day flags many of them (flags
  at the first lead rise from 81 to 178 to 232). `+tailcap75` passes tier 1 under the weighted rule and none of the three does.
* **They do rank the days, which the constant floors did not.** AUROC on the days that are not risk dates is 0.83 to 0.89 over all days, and 0.68 to
  0.79 inside 2018-19 with intervals above 0.5 at every lead for all three. Inside 2018-19 only `+offday` has a Brier skill whose interval excludes 0
  (leads 1 and 2: 0.146 [0.055, 0.231] and 0.081 [0.009, 0.142]); the other two have none there. So a gain in the mean is not a gain in skill at every
  lead: leads 3 to 5 inside 2018-19 are not better than the climatology for any of the three. The forecasts are over-spread (slope below 1, 0.32 to
  0.85, `+offday` nearest to 1).
* **A pass through the mean is reported as such.** `+offday_rate` passes tier 3 at every lead. Inside 2018-19 its Brier skill over the climatology
  is not distinguishable from 0 at any lead, so its tier 3 pass comes from the calibration of the mean (the trailing rate carries the level of a
  regime) and not from a gain in skill beyond the base rate there; it ranks the days (AUROC 0.68 to 0.74) without beating the base rate by Brier score.
  `+offday_mono` passes tier 3 in 2018-19 at leads 3 to 5, where its Brier skill is also not distinguishable from 0 (it is below 0 in point estimate).
* **Tier 5 does not move.** Its calibration condition still fails for all three, and its Brier difference against climatology was already met.
* **A monotone constraint on the state did not help.** `+offday_mono` has the lowest Brier skill on the days that are not risk dates and the
  flattest reliability slope (0.32 to 0.46), against `+offday`.

### The ruling on #567

These variants were built after seeing 2018-2025: step 1 and the earlier directives (#601, #606, #610) read those years, and the variants and their
inputs were chosen from them. A pass here is therefore not a confirmation, and none passes in any case. A variant can replace a shortlist slot only
by Eleonora's decision, made before the 2026 window opens. Nothing here is published: no variant joins any published declaration, no 2026 day is
scored and the live record and pin do not move.

### Reproduction (step 2)

```
PYTHONPATH=src python3 scripts/off_risk_day_624.py declare            # already committed; the declaration is checked equal by the tests
PYTHONPATH=src python3 scripts/off_risk_day_624.py panel --panel AUG2.csv --output AUG2R.csv --compare-with AUG2D.csv
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/off_risk_day_624.py run --panel AUG2R.csv --published PUBLISHED.csv --horizon $h \
    --best OUT/dist_h$h.json --output OUT/v624_h$h.json
IN="OUT/bench_h?.json OUT/risk_h?.json OUT/ql_h?.json OUT/both_h?.json OUT/dist_h?.json OUT/iorb_h?.json OUT/cap_h?.json OUT/v624_h?.json"
for r in weighted unweighted: PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule $r \
    --output OUT/judge_$r.json --markdown OUT/judge_$r.md $IN
for ref in distroll tailcap: for r in weighted unweighted: PYTHONPATH=src python3 scripts/off_risk_day_624.py compare --rule $r \
    --reference $ref --panel PUBLISHED.csv --output OUT/compare-$ref-$r.json --markdown OUT/compare-$ref-$r.md $IN
for ref in distroll tailcap: PYTHONPATH=src python3 scripts/off_risk_day_624.py pg --row $ref onsets --rule weighted --panel PUBLISHED.csv \
    --output OUT/onsets-$ref-weighted.json --markdown OUT/onsets-$ref-weighted.md $IN
PYTHONPATH=src python3 scripts/off_risk_day_624.py pg summary --flat OUT/judge_unweighted.json --weighted OUT/judge_weighted.json --output OUT/summary.md
PYTHONPATH=src python3 scripts/off_risk_day_624.py calibration --judge OUT/judge_weighted.json --output OUT/calibration.md
PYTHONPATH=src python3 scripts/off_risk_day_624.py measure --panel PUBLISHED.csv --scratch AUG2R.csv \
    --row 'risk_gbm+settle+h41+dist_roll=OUT/dist_h{h}.json' --row 'risk_gbm+every_day+gate+settle+h41+iorb+tailcap75=OUT/cap_h{h}.json' \
    --row 'risk_gbm+settle+h41+dist_roll+offday=OUT/v624_h{h}.json' --row 'risk_gbm+settle+h41+dist_roll+offday_mono=OUT/v624_h{h}.json' \
    --row 'risk_gbm+settle+h41+dist_roll+offday_rate=OUT/v624_h{h}.json' --output OUT/step2_offrisk.json --markdown OUT/step2_offrisk.md
```

The off-risk-day statistics of step 2 use step 1's declaration for the bootstrap (the step 2 declaration names the same statistics and does not
repeat the bootstrap block).
