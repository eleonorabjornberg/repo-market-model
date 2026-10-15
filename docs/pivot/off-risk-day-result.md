# Skill on the days that are not risk dates (#624)

**Status: a measurement, not a record.** Step 1 is below and step 2 follows it; step 1 was committed before step 2 was declared. Nothing is published, no day after 2025-12-31 is scored (`docs/decisions/lockbox.md`), and the live record and pin do not move.
Every figure reads 2018-2025, so it describes that history and does not confirm anything (Eleonora's ruling of 11 October 2026 on #567).

**Hypothesis and step:** H2 (the data we hold carries signal for ordinary-day pressure), step #624. Exploration on development data (Eleonora's ruling of 12 October 2026 on #624): the judge tier verdicts below are reported but are not evidence for any hypothesis, and no follow-up +5 bp variant is queued from this result while +5 bp classification is paused.

**Restated against persistence-logistic (#681, finding #667).** CLAUDE.md requires a pressure probability to be stated against climatology *and* a
persistence-logistic model; steps 1 and 2 below were stated against the walk-forward climatology only. The section "Against persistence-logistic and
the raw as-of spread (#681)" at the end of this page pairs every row with it on the same days. In short: no row has skill on the days that are not
risk dates beyond persistence-logistic at lead 1; the day-level model `+offday` is ahead of it at leads 2, 3 and 5 over all days, and that gain is not
present inside 2018-19 (62 of the 82 pressure days) or 2025-26 (15 of 82); the raw as-of spread, ranked as it stands, has a higher AUROC than every row.
The figures in steps 1 and 2 are unchanged and were re-derived exactly (every cell of `step1.json` and `step2-off-risk-days.json`).

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
the cap or the floors, and part of what looks like skill pooled is the regime. A forecast that ranks days inside a regime is what step 2 builds. (Stated against persistence-logistic, the control's ranking is not an advantage: see
"Against persistence-logistic and the raw as-of spread (#681)" below. The sentence above was written against the climatology only.)
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

**The satiation distance was built per H.4.1 release, as #622 requires** (`scripts/off_risk_day_624.py panel`), and #623 has landed. The
build is the one `scripts/satiation_distance_598.py panel` now makes on this tree (the two files are identical, 0 rows differ), so the parent
`+dist_roll` is re-scored here on the same build as the variants: its forecasts (`satiation_distance_598.py run`) and every row the judge reads
were regenerated on this tree, not carried from #598. Its figures reproduce the merged pages at this head (`docs/pivot/evidence/satiation-distance/report.md`,
`docs/pivot/audit-fixes-623-result.md`): 15 of 26 onsets at 1.17 weighted (1.81 flat) false alarms per onset. Against the earlier version of this
page, which carried the parent on the old lag at 1.27 (1.85 flat), that figure and the tier-1 figures of the three variants have moved; the paired
differences against the parent on all days did not, because a variant keeps the parent's forecast on every risk date and the two differ only on the
days that are not risk dates.

### Under the judge in force

Tier 1 pooled over leads 1 to 5 and over leads 3 to 5 (onsets flagged, recall with its 90% interval, pooled false alarms per onset, limit 2), then
tiers 3 and 5, under the weighted rule in force with the flat rule beside it. The judge, its bar and its cut-offs are unchanged.

| row | rule | tier 1, leads 1 to 5: onsets flagged, recall [90%], pooled false alarms per onset (limit 2) | tier 1 | tier 1, leads 3 to 5: onsets flagged, recall [90%], pooled false alarms per onset | tier 3 | tier 5 | passes |
|---|---|---|---|---|---|---|---|
| risk_gbm+settle+h41 | flat | 14 of 26, 0.538 [0.353, 0.710], 2.00 | yes | 11 of 26, 0.423 [0.250, 0.607], 1.58 | no | no | no |
| risk_gbm+settle+h41 | weighted | 14 of 26, 0.538 [0.353, 0.710], 1.44 | yes | 11 of 26, 0.423 [0.250, 0.607], 1.23 | no | no | no |
| risk_gbm+settle+h41+dist_roll | flat | 15 of 26, 0.577 [0.400, 0.762], 1.81 | yes | 12 of 26, 0.462 [0.286, 0.643], 1.54 | no | no | no |
| risk_gbm+settle+h41+dist_roll | weighted | 15 of 26, 0.577 [0.400, 0.762], 1.17 | yes | 12 of 26, 0.462 [0.286, 0.643], 0.96 | no | no | no |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 | flat | 17 of 26, 0.654 [0.480, 0.818], 2.62 | no | 13 of 26, 0.500 [0.312, 0.692], 2.23 | no | no | no |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 | weighted | 18 of 26, 0.692 [0.522, 0.852], 1.88 | yes | 14 of 26, 0.538 [0.344, 0.731], 1.62 | no | no | no |
| risk_gbm+settle+h41+dist_roll+offday | flat | 16 of 26, 0.615 [0.429, 0.792], 3.69 | no | 12 of 26, 0.462 [0.292, 0.645], 3.08 | no | no | no |
| risk_gbm+settle+h41+dist_roll+offday | weighted | 17 of 26, 0.654 [0.476, 0.828], 2.47 | no | 14 of 26, 0.538 [0.355, 0.731], 2.04 | no | no | no |
| risk_gbm+settle+h41+dist_roll+offday_mono | flat | 17 of 26, 0.654 [0.474, 0.828], 4.50 | no | 14 of 26, 0.538 [0.350, 0.733], 3.69 | no | no | no |
| risk_gbm+settle+h41+dist_roll+offday_mono | weighted | 18 of 26, 0.692 [0.500, 0.862], 2.88 | no | 15 of 26, 0.577 [0.391, 0.767], 2.14 | no | no | no |
| risk_gbm+settle+h41+dist_roll+offday_rate | flat | 17 of 26, 0.654 [0.478, 0.824], 3.88 | no | 14 of 26, 0.538 [0.333, 0.733], 3.50 | yes | no | no |
| risk_gbm+settle+h41+dist_roll+offday_rate | weighted | 18 of 26, 0.692 [0.519, 0.864], 2.28 | no | 15 of 26, 0.577 [0.387, 0.769], 2.02 | yes | no | no |

Tier 1 per lead: flags (false alarms); onsets flagged of onsets; false alarms per onset, +5 bp, weighted rule.

Table 2. Flags at +5 bp, by horizon: flags (false alarms); onsets flagged of onsets; false alarms per onset.

| row | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|
| calendar_climatology | 258(174); 12/27; 6.44 | 213(144); 10/26; 5.54 | 213(145); 10/26; 5.58 | 213(146); 10/26; 5.62 | 213(147); 10/26; 5.65 |
| persistence_logistic | 286(183); 11/27; 6.78 | 215(124); 7/26; 4.77 | 243(154); 10/26; 5.92 | 222(140); 8/26; 5.38 | 199(118); 8/26; 4.54 |
| risk_gbm+every_day+gate+settle+h41+iorb+tailcap75 | 92(48); 14/27; 1.78 | 84(39); 12/26; 1.50 | 95(51); 11/26; 1.96 | 89(46); 12/26; 1.77 | 93(48); 14/26; 1.85 |
| risk_gbm+settle+h41+dist_roll | 75(33); 13/27; 1.22 | 61(23); 11/26; 0.88 | 72(32); 11/26; 1.23 | 58(22); 8/26; 0.85 | 56(19); 11/26; 0.73 |
| risk_gbm+settle+h41+dist_roll+offday | 229(128); 15/27; 4.74 | 196(108); 13/26; 4.15 | 171(97); 11/26; 3.73 | 177(103); 10/26; 3.96 | 184(105); 13/26; 4.04 |
| risk_gbm+settle+h41+dist_roll+offday_mono | 174(89); 15/27; 3.30 | 140(73); 10/26; 2.81 | 172(98); 12/26; 3.77 | 150(84); 11/26; 3.23 | 153(83); 13/26; 3.19 |
| risk_gbm+settle+h41+dist_roll+offday_rate | 205(114); 16/27; 4.22 | 200(113); 13/26; 4.35 | 207(118); 13/26; 4.54 | 191(110); 11/26; 4.23 | 193(112); 14/26; 4.31 |

Tier 3 per lead and tier 5 (calibration and the Brier difference against climatology) are in `docs/pivot/evidence/off-risk-day/calibration.md`:
tier 3 holds at every lead in both regimes for `+offday_rate` only; `+offday_mono` holds in 2018-19 at leads 3 and 4 only; `+offday` fails 2018-19
at every lead. Tier 5's calibration condition fails for all three (each under-forecasts: realised less predicted is +0.040, +0.030 and +0.035,
intervals above 0), and its Brier difference against climatology is +0.063 or +0.064 for each, against +0.048 for the parent.

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
`+tailcap75`: +0.0108 [+0.0038, +0.0189], +0.0078 [+0.0008, +0.0163] and +0.0089 [+0.0009, +0.0179] over all days. The tables for both references, by
regime and by pressure-day type, and under the flat rule, are `compare-distroll-*.md` and `compare-tailcap-*.md` in the evidence folder.

### Onsets kept and lost, by date (weighted rule, any lead 1 to 5)

Against `+dist_roll` (15 of 26): `+offday` gains 2019-05-28 and 2019-08-13; `+offday_mono` and `+offday_rate` gain those and 2019-06-25; none loses
an onset. Against `+tailcap75` (18 of 26): each gains 2025-10-15, each loses 2020-03-04, and `+offday` also loses 2019-06-25. The per-onset table is
`onsets-distroll-weighted.md` and `onsets-tailcap-weighted.md`.

### What step 2 says

* **None of the three passes the judge.** Each raises onset recall (17 or 18 of 26 against 15) and each fails tier 1 on the pooled false-alarm count
  (2.28 to 2.88 per onset against a limit of 2, weighted; 3.69 to 4.50 flat): a model that puts mass on every ordinary day flags many of them (flags
  at the first lead rise from 75 to 174 to 229). `+tailcap75` passes tier 1 under the weighted rule and none of the three does.
* **They do rank the days, which the constant floors did not (against the climatology; against persistence-logistic see the section below).** AUROC on the days that are not risk dates is 0.83 to 0.89 over all days, and 0.68 to
  0.79 inside 2018-19 with intervals above 0.5 at every lead for all three. Inside 2018-19 only `+offday` has a Brier skill whose interval excludes 0
  (leads 1 and 2: 0.146 [0.055, 0.231] and 0.081 [0.009, 0.142]); the other two have none there. So a gain in the mean is not a gain in skill at every
  lead: leads 3 to 5 inside 2018-19 are not better than the climatology for any of the three. The forecasts are over-spread (slope below 1, 0.32 to
  0.85, `+offday` nearest to 1).
* **A pass through the mean is reported as such.** `+offday_rate` passes tier 3 at every lead. Inside 2018-19 its Brier skill over the climatology
  is not distinguishable from 0 at any lead, so its tier 3 pass comes from the calibration of the mean (the trailing rate carries the level of a
  regime) and not from a gain in skill beyond the base rate there; it ranks the days (AUROC 0.68 to 0.74) without beating the base rate by Brier score.
  `+offday_mono` passes tier 3 in 2018-19 at leads 3 and 4, where its Brier skill is also not distinguishable from 0 (it is below 0 in point estimate).
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


## Against persistence-logistic and the raw as-of spread (#681)

**Hypothesis and step:** H2 and H5, finding #667 made a directive (#681). Exploration on development data, not a verdict (scoring protocol v1, #640).
Nothing here moves a published figure and no day after 2025-12-31 is scored.

CLAUDE.md requires a pressure probability to be stated against climatology and a persistence-logistic model. Steps 1 and 2 above used the walk-forward
climatology only. This section adds two reference rows on the same population (the scored days of 2018-06-29 to 2025-12-31 at each lead that are not
risk dates, the same outcome at +5 bp, the same walk-forward climatology, the same bootstrap), declared in `metadata/off_risk_day_681.json` before any
was scored:

* **`persistence_logistic`**: the judge's benchmark (`pressure_judge.py forecasts`), a probability, with every statistic of step 1.
* **`spread_bps_asof`**: the raw as-of spread in bp, read through the information rule at the decision instant of the day's own lead. It is a level, not a
  probability, so only its AUROC is a statistic; its Brier skill and reliability slope are not defined.

Every row of step 1 and step 2 is paired with `persistence_logistic` on the same days: the row less persistence, for the AUROC and for the Brier skill
against the climatology, with a 90% stationary-bootstrap interval from resamples the two rows share. Positive favours the row. The figures of the existing
rows are the ones above, re-derived exactly. `ROW` is `risk_gbm+every_day+gate+settle+h41+iorb`; `DR` is `risk_gbm+settle+h41+dist_roll`.

### The reference rows

| cell | lead | pressure days | persistence-logistic AUROC [90%] | Brier skill [90%] | slope [90%] | raw as-of spread AUROC [90%] |
|---|---|---|---|---|---|---|
| all | 1 | 82 | 0.897 [0.841, 0.933] | 0.196 [0.118, 0.263] | 1.016 [0.702, 1.433] | 0.941 [0.914, 0.961] |
| all | 2 | 82 | 0.832 [0.737, 0.893] | 0.097 [0.023, 0.161] | 0.966 [0.677, 1.396] | 0.926 [0.892, 0.951] |
| all | 3 | 82 | 0.793 [0.689, 0.865] | 0.056 [-0.006, 0.103] | 0.965 [0.604, 1.467] | 0.917 [0.881, 0.944] |
| all | 4 | 82 | 0.816 [0.726, 0.884] | 0.105 [0.048, 0.159] | 1.082 [0.774, 1.483] | 0.919 [0.885, 0.944] |
| all | 5 | 82 | 0.809 [0.705, 0.881] | 0.101 [0.051, 0.150] | 0.929 [0.534, 1.340] | 0.919 [0.882, 0.946] |
| regime 2018-19 | 1 | 62 | 0.768 [0.667, 0.851] | 0.162 [0.047, 0.240] | 0.593 | 0.832 [0.773, 0.882] |
| regime 2018-19 | 2 | 62 | 0.697 [0.579, 0.797] | 0.059 [-0.055, 0.130] | 0.498 | 0.784 [0.704, 0.851] |
| regime 2018-19 | 3 | 62 | 0.692 [0.573, 0.793] | 0.043 [-0.053, 0.100] | 0.406 | 0.762 [0.674, 0.833] |
| regime 2018-19 | 4 | 62 | 0.687 [0.575, 0.787] | 0.082 [0.031, 0.124] | 0.585 | 0.748 [0.647, 0.827] |
| regime 2018-19 | 5 | 62 | 0.676 [0.568, 0.772] | 0.063 [0.005, 0.101] | 0.339 | 0.732 [0.615, 0.817] |
| regime 2025-26 | 1 | 15 | 0.919 [0.838, 0.970] | 0.157 [-0.317, 0.294] | 0.919 | 0.923 [0.844, 0.973] |
| regime 2025-26 | 2 | 15 | 0.880 [0.761, 0.950] | 0.019 [-0.609, 0.190] | 0.754 | 0.885 [0.768, 0.954] |
| regime 2025-26 | 3 | 15 | 0.866 [0.736, 0.941] | 0.050 [-0.459, 0.179] | 1.007 | 0.871 [0.742, 0.944] |
| regime 2025-26 | 4 | 15 | 0.875 [0.757, 0.945] | 0.029 [-0.760, 0.228] | 0.822 | 0.879 [0.765, 0.948] |
| regime 2025-26 | 5 | 15 | 0.885 [0.783, 0.955] | 0.071 [-0.686, 0.231] | 0.899 | 0.889 [0.792, 0.958] |

Persistence-logistic is calibrated (slope 0.93 to 1.08 over all days) and has Brier skill 0.06 to 0.20 over the climatology, the interval excluding 0 at
every lead but 3. The raw as-of spread ranks the days better than persistence-logistic does in point estimate at every lead (0.92 to 0.94 against 0.79
to 0.90; not a paired test, and the intervals overlap at leads 1 and 2), and better than every row of steps 1 and 2.

### Every row paired against persistence-logistic

All days that are not risk dates:

| row | lead | pressure days | AUROC row | AUROC persistence_logistic | AUROC difference [90%] | Brier skill row | Brier skill persistence_logistic | Brier skill difference [90%] | slope row | slope persistence_logistic |
|---|---|---|---|---|---|---|---|---|---|---|
| `ROW+tailcap75` | 1 | 82 | 0.493 | 0.897 | -0.403 [-0.446, -0.344] | -0.005 | 0.196 | -0.200 [-0.323, -0.024] | 2.035 | 1.016 |
| `ROW+tailcap75` | 2 | 82 | 0.520 | 0.832 | -0.312 [-0.381, -0.221] | 0.000 | 0.097 | -0.097 [-0.206, +0.062] | 2.659 | 0.966 |
| `ROW+tailcap75` | 3 | 82 | 0.501 | 0.793 | -0.292 [-0.368, -0.185] | -0.014 | 0.056 | -0.071 [-0.182, +0.101] | 3.186 | 0.965 |
| `ROW+tailcap75` | 4 | 82 | 0.519 | 0.816 | -0.297 [-0.382, -0.193] | -0.003 | 0.105 | -0.108 [-0.218, +0.050] | 1.824 | 1.082 |
| `ROW+tailcap75` | 5 | 82 | 0.528 | 0.809 | -0.281 [-0.358, -0.177] | 0.010 | 0.101 | -0.092 [-0.193, +0.061] | 2.396 | 0.929 |
| `DR` | 1 | 82 | 0.500 | 0.897 | -0.397 [-0.433, -0.341] | -0.027 | 0.196 | -0.223 [-0.343, -0.050] | – | 1.016 |
| `DR` | 2 | 82 | 0.500 | 0.832 | -0.332 [-0.393, -0.237] | -0.025 | 0.097 | -0.122 [-0.237, +0.047] | – | 0.966 |
| `DR` | 3 | 82 | 0.500 | 0.793 | -0.293 [-0.365, -0.189] | -0.023 | 0.056 | -0.079 [-0.191, +0.100] | – | 0.965 |
| `DR` | 4 | 82 | 0.500 | 0.816 | -0.316 [-0.384, -0.226] | -0.021 | 0.105 | -0.126 [-0.236, +0.038] | – | 1.082 |
| `DR` | 5 | 82 | 0.500 | 0.809 | -0.309 [-0.381, -0.205] | -0.019 | 0.101 | -0.121 [-0.227, +0.036] | – | 0.929 |
| `DR+offday` | 1 | 82 | 0.887 | 0.897 | -0.009 [-0.065, +0.027] | 0.237 | 0.196 | +0.042 [-0.008, +0.111] | 0.829 | 1.016 |
| `DR+offday` | 2 | 82 | 0.867 | 0.832 | +0.035 [-0.005, +0.077] | 0.187 | 0.097 | +0.090 [+0.023, +0.176] | 0.853 | 0.966 |
| `DR+offday` | 3 | 82 | 0.855 | 0.793 | +0.062 [+0.021, +0.111] | 0.148 | 0.056 | +0.092 [+0.026, +0.194] | 0.800 | 0.965 |
| `DR+offday` | 4 | 82 | 0.849 | 0.816 | +0.033 [-0.002, +0.073] | 0.148 | 0.105 | +0.044 [-0.015, +0.129] | 0.778 | 1.082 |
| `DR+offday` | 5 | 82 | 0.845 | 0.809 | +0.036 [+0.007, +0.070] | 0.163 | 0.101 | +0.062 [+0.010, +0.147] | 0.791 | 0.929 |
| `DR+offday_mono` | 1 | 82 | 0.864 | 0.897 | -0.032 [-0.094, +0.007] | 0.167 | 0.196 | -0.029 [-0.123, +0.075] | 0.458 | 1.016 |
| `DR+offday_mono` | 2 | 82 | 0.853 | 0.832 | +0.022 [-0.020, +0.069] | 0.047 | 0.097 | -0.050 [-0.172, +0.082] | 0.387 | 0.966 |
| `DR+offday_mono` | 3 | 82 | 0.858 | 0.793 | +0.065 [+0.022, +0.117] | 0.017 | 0.056 | -0.039 [-0.165, +0.095] | 0.356 | 0.965 |
| `DR+offday_mono` | 4 | 82 | 0.843 | 0.816 | +0.027 [-0.007, +0.065] | 0.036 | 0.105 | -0.069 [-0.185, +0.051] | 0.367 | 1.082 |
| `DR+offday_mono` | 5 | 82 | 0.845 | 0.809 | +0.036 [+0.008, +0.072] | 0.072 | 0.101 | -0.030 [-0.122, +0.083] | 0.323 | 0.929 |
| `DR+offday_rate` | 1 | 82 | 0.861 | 0.897 | -0.036 [-0.107, +0.009] | 0.191 | 0.196 | -0.004 [-0.092, +0.083] | 0.732 | 1.016 |
| `DR+offday_rate` | 2 | 82 | 0.846 | 0.832 | +0.015 [-0.032, +0.058] | 0.139 | 0.097 | +0.042 [-0.062, +0.146] | 0.699 | 0.966 |
| `DR+offday_rate` | 3 | 82 | 0.843 | 0.793 | +0.050 [+0.005, +0.097] | 0.101 | 0.056 | +0.045 [-0.056, +0.163] | 0.671 | 0.965 |
| `DR+offday_rate` | 4 | 82 | 0.834 | 0.816 | +0.018 [-0.021, +0.055] | 0.100 | 0.105 | -0.004 [-0.111, +0.101] | 0.651 | 1.082 |
| `DR+offday_rate` | 5 | 82 | 0.828 | 0.809 | +0.019 [-0.017, +0.055] | 0.093 | 0.101 | -0.008 [-0.107, +0.089] | 0.643 | 0.929 |
| `ROW` | 1 | 82 | 0.736 | 0.897 | -0.160 [-0.218, -0.108] | 0.166 | 0.196 | -0.030 [-0.100, +0.055] | 0.487 | 1.016 |
| `ROW` | 2 | 82 | 0.735 | 0.832 | -0.096 [-0.180, -0.013] | 0.089 | 0.097 | -0.008 [-0.078, +0.078] | 0.566 | 0.966 |
| `ROW` | 3 | 82 | 0.704 | 0.793 | -0.089 [-0.192, +0.005] | 0.075 | 0.056 | +0.019 [-0.066, +0.122] | 0.445 | 0.965 |
| `ROW` | 4 | 82 | 0.747 | 0.816 | -0.069 [-0.138, -0.006] | 0.108 | 0.105 | +0.003 [-0.052, +0.074] | 0.648 | 1.082 |
| `ROW` | 5 | 82 | 0.744 | 0.809 | -0.065 [-0.140, +0.001] | 0.103 | 0.101 | +0.002 [-0.060, +0.082] | 0.559 | 0.929 |
| `ROW+tailcap75+floor` | 1 | 82 | 0.574 | 0.897 | -0.323 [-0.477, -0.197] | 0.015 | 0.196 | -0.181 [-0.254, -0.096] | 0.465 | 1.016 |
| `ROW+tailcap75+floor` | 2 | 82 | 0.574 | 0.832 | -0.258 [-0.407, -0.134] | 0.006 | 0.097 | -0.091 [-0.156, -0.019] | 0.385 | 0.966 |
| `ROW+tailcap75+floor` | 3 | 82 | 0.558 | 0.793 | -0.235 [-0.376, -0.114] | 0.001 | 0.056 | -0.056 [-0.103, +0.005] | 0.273 | 0.965 |
| `ROW+tailcap75+floor` | 4 | 82 | 0.564 | 0.816 | -0.252 [-0.393, -0.129] | 0.004 | 0.105 | -0.101 [-0.158, -0.045] | 0.398 | 1.082 |
| `ROW+tailcap75+floor` | 5 | 82 | 0.556 | 0.809 | -0.253 [-0.400, -0.131] | 0.005 | 0.101 | -0.096 [-0.148, -0.046] | 0.456 | 0.929 |
| `ROW+tailcap75+recent_floor` | 1 | 82 | 0.870 | 0.897 | -0.027 [-0.077, +0.021] | 0.154 | 0.196 | -0.042 [-0.122, +0.050] | 0.571 | 1.016 |
| `ROW+tailcap75+recent_floor` | 2 | 82 | 0.859 | 0.832 | +0.028 [-0.042, +0.106] | 0.136 | 0.097 | +0.040 [-0.044, +0.132] | 0.549 | 0.966 |
| `ROW+tailcap75+recent_floor` | 3 | 82 | 0.848 | 0.793 | +0.055 [-0.027, +0.149] | 0.131 | 0.056 | +0.075 [-0.009, +0.175] | 0.526 | 0.965 |
| `ROW+tailcap75+recent_floor` | 4 | 82 | 0.840 | 0.816 | +0.024 [-0.064, +0.113] | 0.132 | 0.105 | +0.028 [-0.064, +0.124] | 0.579 | 1.082 |
| `ROW+tailcap75+recent_floor` | 5 | 82 | 0.838 | 0.809 | +0.029 [-0.060, +0.115] | 0.130 | 0.101 | +0.029 [-0.061, +0.123] | 0.595 | 0.929 |
| `ROW+tailcap75+state_floor` | 1 | 82 | 0.639 | 0.897 | -0.258 [-0.374, -0.156] | 0.030 | 0.196 | -0.165 [-0.242, -0.082] | 0.725 | 1.016 |
| `ROW+tailcap75+state_floor` | 2 | 82 | 0.641 | 0.832 | -0.190 [-0.299, -0.091] | 0.021 | 0.097 | -0.076 [-0.149, -0.001] | 0.734 | 0.966 |
| `ROW+tailcap75+state_floor` | 3 | 82 | 0.627 | 0.793 | -0.166 [-0.272, -0.068] | 0.016 | 0.056 | -0.040 [-0.092, +0.023] | 0.627 | 0.965 |
| `ROW+tailcap75+state_floor` | 4 | 82 | 0.632 | 0.816 | -0.184 [-0.279, -0.091] | 0.019 | 0.105 | -0.086 [-0.145, -0.024] | 0.755 | 1.082 |
| `ROW+tailcap75+state_floor` | 5 | 82 | 0.615 | 0.809 | -0.194 [-0.305, -0.095] | 0.017 | 0.101 | -0.084 [-0.133, -0.035] | 0.758 | 0.929 |

Inside 2018-19 (62 of the 82 pressure days):

| row | lead | pressure days | AUROC row | AUROC persistence_logistic | AUROC difference [90%] | Brier skill row | Brier skill persistence_logistic | Brier skill difference [90%] | slope row | slope persistence_logistic |
|---|---|---|---|---|---|---|---|---|---|---|
| `ROW+tailcap75` | 1 | 62 | 0.486 | 0.768 | -0.281 [-0.367, -0.182] | -0.202 | 0.162 | -0.364 [-0.504, -0.168] | 1.389 | 0.593 |
| `ROW+tailcap75` | 2 | 62 | 0.500 | 0.697 | -0.197 [-0.314, -0.064] | -0.175 | 0.059 | -0.233 [-0.369, -0.049] | 2.305 | 0.498 |
| `ROW+tailcap75` | 3 | 62 | 0.474 | 0.692 | -0.218 [-0.333, -0.084] | -0.195 | 0.043 | -0.238 [-0.355, -0.063] | 2.314 | 0.406 |
| `ROW+tailcap75` | 4 | 62 | 0.505 | 0.687 | -0.182 [-0.300, -0.047] | -0.181 | 0.082 | -0.264 [-0.393, -0.111] | 0.185 | 0.585 |
| `ROW+tailcap75` | 5 | 62 | 0.519 | 0.676 | -0.157 [-0.254, -0.043] | -0.163 | 0.063 | -0.225 [-0.330, -0.082] | 1.581 | 0.339 |
| `DR` | 1 | 62 | 0.500 | 0.768 | -0.268 [-0.351, -0.167] | -0.218 | 0.162 | -0.380 [-0.515, -0.182] | – | 0.593 |
| `DR` | 2 | 62 | 0.500 | 0.697 | -0.197 [-0.297, -0.079] | -0.215 | 0.059 | -0.274 [-0.406, -0.076] | – | 0.498 |
| `DR` | 3 | 62 | 0.500 | 0.692 | -0.192 [-0.293, -0.073] | -0.213 | 0.043 | -0.257 [-0.369, -0.078] | – | 0.406 |
| `DR` | 4 | 62 | 0.500 | 0.687 | -0.187 [-0.287, -0.075] | -0.212 | 0.082 | -0.294 [-0.413, -0.140] | – | 0.585 |
| `DR` | 5 | 62 | 0.500 | 0.676 | -0.176 [-0.272, -0.068] | -0.211 | 0.063 | -0.273 [-0.386, -0.118] | – | 0.339 |
| `DR+offday` | 1 | 62 | 0.786 | 0.768 | +0.019 [+0.000, +0.043] | 0.146 | 0.162 | -0.016 [-0.064, +0.055] | 0.478 | 0.593 |
| `DR+offday` | 2 | 62 | 0.735 | 0.697 | +0.038 [-0.012, +0.092] | 0.081 | 0.059 | +0.023 [-0.052, +0.122] | 0.453 | 0.498 |
| `DR+offday` | 3 | 62 | 0.693 | 0.692 | +0.001 [-0.048, +0.054] | 0.019 | 0.043 | -0.024 [-0.078, +0.049] | 0.220 | 0.406 |
| `DR+offday` | 4 | 62 | 0.679 | 0.687 | -0.008 [-0.051, +0.034] | 0.008 | 0.082 | -0.074 [-0.122, -0.027] | 0.143 | 0.585 |
| `DR+offday` | 5 | 62 | 0.694 | 0.676 | +0.018 [-0.025, +0.059] | 0.039 | 0.063 | -0.024 [-0.058, +0.022] | 0.170 | 0.339 |
| `DR+offday_mono` | 1 | 62 | 0.791 | 0.768 | +0.023 [-0.025, +0.075] | 0.099 | 0.162 | -0.064 [-0.189, +0.050] | 0.314 | 0.593 |
| `DR+offday_mono` | 2 | 62 | 0.713 | 0.697 | +0.016 [-0.060, +0.093] | -0.060 | 0.059 | -0.119 [-0.291, +0.047] | 0.141 | 0.498 |
| `DR+offday_mono` | 3 | 62 | 0.690 | 0.692 | -0.002 [-0.066, +0.060] | -0.126 | 0.043 | -0.169 [-0.359, -0.019] | 0.098 | 0.406 |
| `DR+offday_mono` | 4 | 62 | 0.699 | 0.687 | +0.011 [-0.047, +0.078] | -0.116 | 0.082 | -0.198 [-0.394, -0.055] | 0.072 | 0.585 |
| `DR+offday_mono` | 5 | 62 | 0.707 | 0.676 | +0.031 [-0.024, +0.088] | -0.054 | 0.063 | -0.117 [-0.266, +0.010] | 0.091 | 0.339 |
| `DR+offday_rate` | 1 | 62 | 0.744 | 0.768 | -0.024 [-0.082, +0.025] | 0.069 | 0.162 | -0.093 [-0.223, +0.010] | 0.197 | 0.593 |
| `DR+offday_rate` | 2 | 62 | 0.714 | 0.697 | +0.017 [-0.043, +0.083] | 0.010 | 0.059 | -0.048 [-0.218, +0.087] | 0.059 | 0.498 |
| `DR+offday_rate` | 3 | 62 | 0.691 | 0.692 | -0.001 [-0.060, +0.060] | -0.053 | 0.043 | -0.096 [-0.266, +0.035] | -0.064 | 0.406 |
| `DR+offday_rate` | 4 | 62 | 0.682 | 0.687 | -0.005 [-0.074, +0.066] | -0.062 | 0.082 | -0.145 [-0.320, -0.031] | -0.132 | 0.585 |
| `DR+offday_rate` | 5 | 62 | 0.680 | 0.676 | +0.004 [-0.067, +0.071] | -0.063 | 0.063 | -0.126 [-0.310, -0.009] | -0.122 | 0.339 |
| `ROW` | 1 | 62 | 0.700 | 0.768 | -0.068 [-0.148, +0.016] | 0.093 | 0.162 | -0.069 [-0.163, +0.037] | 0.236 | 0.593 |
| `ROW` | 2 | 62 | 0.682 | 0.697 | -0.015 [-0.120, +0.099] | 0.003 | 0.059 | -0.056 [-0.158, +0.043] | 0.282 | 0.498 |
| `ROW` | 3 | 62 | 0.648 | 0.692 | -0.044 [-0.169, +0.080] | -0.037 | 0.043 | -0.081 [-0.190, +0.018] | 0.102 | 0.406 |
| `ROW` | 4 | 62 | 0.691 | 0.687 | +0.004 [-0.089, +0.097] | 0.029 | 0.082 | -0.053 [-0.121, +0.013] | 0.385 | 0.585 |
| `ROW` | 5 | 62 | 0.682 | 0.676 | +0.006 [-0.089, +0.098] | -0.013 | 0.063 | -0.075 [-0.158, +0.006] | 0.078 | 0.339 |
| `ROW+tailcap75+floor` | 1 | 62 | 0.659 | 0.768 | -0.109 [-0.222, -0.003] | 0.011 | 0.162 | -0.151 [-0.233, -0.040] | 0.120 | 0.593 |
| `ROW+tailcap75+floor` | 2 | 62 | 0.656 | 0.697 | -0.041 [-0.126, +0.050] | 0.010 | 0.059 | -0.049 [-0.120, +0.059] | -0.008 | 0.498 |
| `ROW+tailcap75+floor` | 3 | 62 | 0.648 | 0.692 | -0.044 [-0.119, +0.029] | 0.002 | 0.043 | -0.042 [-0.098, +0.050] | -0.051 | 0.406 |
| `ROW+tailcap75+floor` | 4 | 62 | 0.647 | 0.687 | -0.040 [-0.130, +0.042] | 0.006 | 0.082 | -0.077 [-0.120, -0.025] | 0.055 | 0.585 |
| `ROW+tailcap75+floor` | 5 | 62 | 0.658 | 0.676 | -0.018 [-0.092, +0.044] | 0.008 | 0.063 | -0.055 [-0.092, -0.000] | 0.121 | 0.339 |
| `ROW+tailcap75+recent_floor` | 1 | 62 | 0.684 | 0.768 | -0.084 [-0.162, +0.009] | 0.049 | 0.162 | -0.113 [-0.242, -0.018] | 0.132 | 0.593 |
| `ROW+tailcap75+recent_floor` | 2 | 62 | 0.681 | 0.697 | -0.016 [-0.082, +0.068] | 0.044 | 0.059 | -0.014 [-0.147, +0.092] | 0.077 | 0.498 |
| `ROW+tailcap75+recent_floor` | 3 | 62 | 0.683 | 0.692 | -0.009 [-0.062, +0.055] | 0.046 | 0.043 | +0.003 [-0.126, +0.105] | 0.073 | 0.406 |
| `ROW+tailcap75+recent_floor` | 4 | 62 | 0.687 | 0.687 | -0.000 [-0.054, +0.064] | 0.048 | 0.082 | -0.035 [-0.166, +0.057] | 0.129 | 0.585 |
| `ROW+tailcap75+recent_floor` | 5 | 62 | 0.676 | 0.676 | +0.000 [-0.055, +0.057] | 0.041 | 0.063 | -0.022 [-0.167, +0.072] | 0.150 | 0.339 |
| `ROW+tailcap75+state_floor` | 1 | 62 | 0.659 | 0.768 | -0.109 [-0.222, -0.003] | 0.011 | 0.162 | -0.151 [-0.233, -0.040] | 0.120 | 0.593 |
| `ROW+tailcap75+state_floor` | 2 | 62 | 0.656 | 0.697 | -0.041 [-0.126, +0.050] | 0.010 | 0.059 | -0.049 [-0.120, +0.059] | -0.008 | 0.498 |
| `ROW+tailcap75+state_floor` | 3 | 62 | 0.648 | 0.692 | -0.044 [-0.119, +0.029] | 0.002 | 0.043 | -0.042 [-0.098, +0.050] | -0.051 | 0.406 |
| `ROW+tailcap75+state_floor` | 4 | 62 | 0.647 | 0.687 | -0.040 [-0.130, +0.042] | 0.006 | 0.082 | -0.077 [-0.120, -0.025] | 0.055 | 0.585 |
| `ROW+tailcap75+state_floor` | 5 | 62 | 0.658 | 0.676 | -0.018 [-0.092, +0.044] | 0.008 | 0.063 | -0.055 [-0.092, -0.000] | 0.121 | 0.339 |

Inside 2025-26 (15 pressure days):

| row | lead | pressure days | AUROC row | AUROC persistence_logistic | AUROC difference [90%] | Brier skill row | Brier skill persistence_logistic | Brier skill difference [90%] | slope row | slope persistence_logistic |
|---|---|---|---|---|---|---|---|---|---|---|
| `ROW+tailcap75` | 1 | 15 | 0.500 | 0.919 | -0.419 [-0.470, -0.338] | -0.070 | 0.157 | -0.227 [-0.360, +0.545] | – | 0.919 |
| `ROW+tailcap75` | 2 | 15 | 0.500 | 0.880 | -0.380 [-0.450, -0.261] | -0.069 | 0.019 | -0.088 [-0.257, +0.861] | – | 0.754 |
| `ROW+tailcap75` | 3 | 15 | 0.500 | 0.866 | -0.366 [-0.441, -0.236] | -0.068 | 0.050 | -0.119 [-0.249, +0.684] | – | 1.007 |
| `ROW+tailcap75` | 4 | 15 | 0.500 | 0.875 | -0.375 [-0.445, -0.257] | -0.068 | 0.029 | -0.097 [-0.297, +0.988] | – | 0.822 |
| `ROW+tailcap75` | 5 | 15 | 0.495 | 0.885 | -0.390 [-0.462, -0.288] | -0.069 | 0.071 | -0.140 [-0.307, +0.888] | – | 0.899 |
| `DR` | 1 | 15 | 0.500 | 0.919 | -0.419 [-0.470, -0.338] | -0.070 | 0.157 | -0.227 [-0.360, +0.545] | – | 0.919 |
| `DR` | 2 | 15 | 0.500 | 0.880 | -0.380 [-0.450, -0.261] | -0.069 | 0.019 | -0.088 [-0.257, +0.861] | – | 0.754 |
| `DR` | 3 | 15 | 0.500 | 0.866 | -0.366 [-0.441, -0.236] | -0.068 | 0.050 | -0.119 [-0.249, +0.684] | – | 1.007 |
| `DR` | 4 | 15 | 0.500 | 0.875 | -0.375 [-0.445, -0.257] | -0.068 | 0.029 | -0.097 [-0.297, +0.988] | – | 0.822 |
| `DR` | 5 | 15 | 0.500 | 0.885 | -0.385 [-0.455, -0.283] | -0.068 | 0.071 | -0.139 [-0.307, +0.891] | – | 0.899 |
| `DR+offday` | 1 | 15 | 0.920 | 0.919 | +0.001 [-0.032, +0.053] | 0.150 | 0.157 | -0.007 [-0.180, +0.250] | 0.786 | 0.919 |
| `DR+offday` | 2 | 15 | 0.901 | 0.880 | +0.021 [-0.028, +0.100] | 0.052 | 0.019 | +0.033 [-0.160, +0.340] | 0.702 | 0.754 |
| `DR+offday` | 3 | 15 | 0.899 | 0.866 | +0.032 [-0.018, +0.120] | 0.055 | 0.050 | +0.005 [-0.230, +0.244] | 0.728 | 1.007 |
| `DR+offday` | 4 | 15 | 0.907 | 0.875 | +0.033 [-0.007, +0.112] | 0.101 | 0.029 | +0.072 [-0.101, +0.516] | 0.761 | 0.822 |
| `DR+offday` | 5 | 15 | 0.904 | 0.885 | +0.019 [-0.016, +0.081] | 0.068 | 0.071 | -0.002 [-0.132, +0.387] | 0.726 | 0.899 |
| `DR+offday_mono` | 1 | 15 | 0.860 | 0.919 | -0.059 [-0.125, +0.019] | -0.096 | 0.157 | -0.253 [-0.722, +0.133] | 0.325 | 0.919 |
| `DR+offday_mono` | 2 | 15 | 0.851 | 0.880 | -0.029 [-0.097, +0.038] | -0.222 | 0.019 | -0.241 [-1.056, +0.120] | 0.216 | 0.754 |
| `DR+offday_mono` | 3 | 15 | 0.878 | 0.866 | +0.012 [-0.016, +0.054] | -0.157 | 0.050 | -0.207 [-1.122, +0.104] | 0.265 | 1.007 |
| `DR+offday_mono` | 4 | 15 | 0.867 | 0.875 | -0.008 [-0.052, +0.057] | -0.094 | 0.029 | -0.123 [-0.328, +0.343] | 0.394 | 0.822 |
| `DR+offday_mono` | 5 | 15 | 0.834 | 0.885 | -0.051 [-0.107, +0.009] | -0.109 | 0.071 | -0.179 [-0.397, +0.174] | 0.213 | 0.899 |
| `DR+offday_rate` | 1 | 15 | 0.917 | 0.919 | -0.002 [-0.040, +0.050] | 0.141 | 0.157 | -0.016 [-0.235, +0.244] | 0.787 | 0.919 |
| `DR+offday_rate` | 2 | 15 | 0.897 | 0.880 | +0.017 [-0.039, +0.099] | 0.044 | 0.019 | +0.025 [-0.205, +0.308] | 0.706 | 0.754 |
| `DR+offday_rate` | 3 | 15 | 0.899 | 0.866 | +0.032 [-0.020, +0.125] | 0.058 | 0.050 | +0.007 [-0.281, +0.256] | 0.731 | 1.007 |
| `DR+offday_rate` | 4 | 15 | 0.905 | 0.875 | +0.030 [-0.012, +0.117] | 0.101 | 0.029 | +0.072 [-0.124, +0.495] | 0.758 | 0.822 |
| `DR+offday_rate` | 5 | 15 | 0.901 | 0.885 | +0.016 [-0.020, +0.080] | 0.062 | 0.071 | -0.009 [-0.155, +0.361] | 0.723 | 0.899 |
| `ROW` | 1 | 15 | 0.804 | 0.919 | -0.115 [-0.234, -0.013] | 0.089 | 0.157 | -0.068 [-0.222, -0.018] | 0.403 | 0.919 |
| `ROW` | 2 | 15 | 0.717 | 0.880 | -0.163 [-0.329, -0.072] | -0.090 | 0.019 | -0.109 [-0.328, -0.029] | 0.293 | 0.754 |
| `ROW` | 3 | 15 | 0.682 | 0.866 | -0.184 [-0.352, -0.077] | -0.060 | 0.050 | -0.111 [-0.436, +0.002] | 0.295 | 1.007 |
| `ROW` | 4 | 15 | 0.747 | 0.875 | -0.128 [-0.244, -0.056] | -0.078 | 0.029 | -0.107 [-0.617, -0.005] | 0.258 | 0.822 |
| `ROW` | 5 | 15 | 0.747 | 0.885 | -0.137 [-0.267, -0.057] | -0.029 | 0.071 | -0.099 [-0.524, -0.014] | 0.422 | 0.899 |
| `ROW+tailcap75+floor` | 1 | 15 | 0.350 | 0.919 | -0.568 [-0.857, -0.199] | 0.000 | 0.157 | -0.157 [-0.294, +0.317] | -11.273 | 0.919 |
| `ROW+tailcap75+floor` | 2 | 15 | 0.285 | 0.880 | -0.595 [-0.841, -0.276] | 0.000 | 0.019 | -0.019 [-0.190, +0.609] | -19.701 | 0.754 |
| `ROW+tailcap75+floor` | 3 | 15 | 0.218 | 0.866 | -0.648 [-0.850, -0.364] | 0.000 | 0.050 | -0.050 [-0.179, +0.459] | -31.221 | 1.007 |
| `ROW+tailcap75+floor` | 4 | 15 | 0.203 | 0.875 | -0.672 [-0.867, -0.390] | 0.000 | 0.029 | -0.029 [-0.228, +0.760] | -34.335 | 0.822 |
| `ROW+tailcap75+floor` | 5 | 15 | 0.202 | 0.885 | -0.683 [-0.862, -0.429] | -0.001 | 0.071 | -0.071 [-0.231, +0.684] | -34.415 | 0.899 |
| `ROW+tailcap75+recent_floor` | 1 | 15 | 0.745 | 0.919 | -0.173 [-0.408, +0.017] | 0.023 | 0.157 | -0.134 [-0.283, +0.417] | 0.886 | 0.919 |
| `ROW+tailcap75+recent_floor` | 2 | 15 | 0.698 | 0.880 | -0.182 [-0.457, +0.056] | -0.000 | 0.019 | -0.019 [-0.220, +0.794] | 0.814 | 0.754 |
| `ROW+tailcap75+recent_floor` | 3 | 15 | 0.650 | 0.866 | -0.216 [-0.499, +0.061] | -0.023 | 0.050 | -0.074 [-0.223, +0.584] | 0.725 | 1.007 |
| `ROW+tailcap75+recent_floor` | 4 | 15 | 0.607 | 0.875 | -0.268 [-0.533, +0.035] | -0.030 | 0.029 | -0.059 [-0.276, +0.862] | 0.729 | 0.822 |
| `ROW+tailcap75+recent_floor` | 5 | 15 | 0.601 | 0.885 | -0.283 [-0.536, -0.001] | -0.031 | 0.071 | -0.101 [-0.268, +0.804] | 0.703 | 0.899 |
| `ROW+tailcap75+state_floor` | 1 | 15 | 0.554 | 0.919 | -0.364 [-0.744, +0.014] | 0.087 | 0.157 | -0.070 [-0.246, +0.254] | 1.359 | 0.919 |
| `ROW+tailcap75+state_floor` | 2 | 15 | 0.534 | 0.880 | -0.346 [-0.745, +0.053] | 0.087 | 0.019 | +0.068 [-0.160, +0.569] | 1.352 | 0.754 |
| `ROW+tailcap75+state_floor` | 3 | 15 | 0.514 | 0.866 | -0.352 [-0.738, +0.058] | 0.087 | 0.050 | +0.037 [-0.161, +0.410] | 1.345 | 1.007 |
| `ROW+tailcap75+state_floor` | 4 | 15 | 0.500 | 0.875 | -0.375 [-0.740, +0.034] | 0.087 | 0.029 | +0.059 [-0.191, +0.729] | 1.341 | 0.822 |
| `ROW+tailcap75+state_floor` | 5 | 15 | 0.456 | 0.885 | -0.429 [-0.778, +0.004] | 0.070 | 0.071 | -0.001 [-0.186, +0.612] | 1.165 | 0.899 |

The other regimes (2020, 2021-23, 2024) and the split by as-of scarcity state are in `docs/pivot/evidence/off-risk-day/persistence-step1-paired.md`,
`persistence-step2-paired.md` and, with the intercepts, `persistence-step1.md` and `persistence-step2.md`; the full tables of this section are
`persistence-tables.md`. The regime 2021-23 has no pressure day, so it ranks nothing.

### What it says

* **Step 1's rows have no skill beyond persistence-logistic.** `ROW`, the one row whose own forecast ranked the days against the climatology, has a lower
  AUROC than persistence-logistic at leads 1, 2 and 4 (lead 1: -0.160 [-0.218, -0.108]), and a Brier skill that does not differ from it at any lead over
  all days or inside 2018-19. In 2025-26 it is below persistence on both statistics at leads 1, 2, 4 and 5.
  `+tailcap75` and the constant floors are below it on AUROC at every lead, over all days. `+recent_floor`, whose pooled skill over the climatology was
  the largest in step 1 (AUROC 0.84 to 0.87), does not differ from persistence over all days at any lead, and inside 2018-19 it is below it in Brier skill at lead 1 only: its pooled
  figure is no more than persistence-logistic's.
* **At lead 1 no row beats persistence-logistic.** `+offday`'s difference is -0.009 [-0.065, +0.027] in AUROC and +0.042 [-0.008, +0.111] in Brier skill.
  `+offday_mono` and `+offday_rate` are below it in point estimate on both, with intervals holding 0.
* **`+offday` is ahead over all days at leads 2, 3 and 5, and that does not hold where the pressure days are.** Over all days its Brier skill exceeds
  persistence's at lead 2 (+0.090 [+0.023, +0.176]), lead 3 (+0.092 [+0.026, +0.194]) and lead 5 (+0.062 [+0.010, +0.147]), and its AUROC at leads 3 and 5.
  Inside 2018-19, which holds 62 of the 82 pressure days, no Brier-skill difference is above 0 at any lead (the interval at lead 4 is below 0: -0.074
  [-0.122, -0.027]) and the only AUROC difference whose interval excludes 0 is lead 1 (+0.019 [+0.000, +0.043]); inside 2025-26 no interval excludes 0.
* **The near-empty cells, as #667 found.** The lead 3 and 5 gain is not repeated in any regime with 15 or more pressure days. The regimes 2020 and
  2024 hold 3 and 2 pressure days. There `+offday` has Brier skill 0.54 to 0.63 (2020) and 0.17 to 0.18 (2024) against persistence's -0.10 to 0.12 and
  -0.05 to 0.02, so the gain is absent from the regimes that hold 77 of the 82 pressure days and present only in the two that hold the other 5. **#667's finding holds.** (The AUROC of a
  cell with 2 or 3 pressure days is not informative; the intervals are as wide as the cell.) `+offday_rate` differs from persistence in AUROC at lead 3
  only, `+offday_mono` at leads 3 and 5, and neither in Brier skill over all days; both are below persistence in Brier skill inside 2018-19 at leads 4 and 5
  (`+offday_rate`) and leads 3 and 4 (`+offday_mono`).
* **No row ranks the days better than the raw as-of spread.** Its AUROC, 0.92 to 0.94 over all days, is above every row's at every lead. The extra inputs
  of `+offday` (the tail spread, its dispersion, the satiation distance and the scarcity state) rank the days that are not risk dates no better than the
  spread read alone (a statement about AUROC; the raw spread is not a probability and has no Brier skill).
* **What this changes.** Steps 1 and 2 said the day-level models rank the days and have skill beyond the base rate. Against the benchmark CLAUDE.md
  requires, the ordinary-day ranking is not beyond persistence-logistic at lead 1 or inside 2018-19, and what remains over all days at leads 2, 3 and 5 is
  carried by two near-empty regimes. Whether H2's progress is judged against persistence-logistic, climatology or both is Eleonora's; this page reports
  both and settles nothing. The judge's tier verdicts above are unchanged and are not evidence for any hypothesis.

### Reproduction (#681)

The forecast files are those of "Reproduction" and "Reproduction (step 2)" above, plus `pressure_judge.py forecasts` for the persistence-logistic
benchmark (`OUT/bench_h?.json`). Run the single-threaded math libraries (`OMP_NUM_THREADS=1`): the gradient-boosted fits oversubscribe the cores
otherwise and take hours. The panel digest is `4ddc3882…`.

```
PYTHONPATH=src python3 scripts/off_risk_day_624.py declare-persistence        # already committed; the declaration is checked equal by the tests
PYTHONPATH=src python3 scripts/off_risk_day_624.py measure --panel PUBLISHED.csv --scratch AUG2.csv --declaration metadata/off_risk_day_681.json \
    --pair-with persistence_logistic --row 'persistence_logistic=OUT/bench_h{h}.json' --row 'spread_bps_asof=asof:spread_bps' \
    --row 'risk_gbm+every_day+gate+settle+h41+iorb=OUT/iorb_h{h}.json' --row 'risk_gbm+every_day+gate+settle+h41+iorb+tailcap75=OUT/cap_h{h}.json' \
    --row 'risk_gbm+every_day+gate+settle+h41+iorb+tailcap75+floor=OUT/v610_h{h}.json' \
    --row 'risk_gbm+every_day+gate+settle+h41+iorb+tailcap75+state_floor=OUT/v610_h{h}.json' \
    --row 'risk_gbm+every_day+gate+settle+h41+iorb+tailcap75+recent_floor=OUT/v610_h{h}.json' \
    --title 'Step 1 against persistence-logistic and the raw as-of spread (#681)' --output OUT/persistence-step1.json --markdown OUT/persistence-step1.md
PYTHONPATH=src python3 scripts/off_risk_day_624.py measure --panel PUBLISHED.csv --scratch AUG2R.csv --declaration metadata/off_risk_day_681.json \
    --pair-with persistence_logistic --row 'persistence_logistic=OUT/bench_h{h}.json' --row 'spread_bps_asof=asof:spread_bps' \
    --row 'risk_gbm+settle+h41+dist_roll=OUT/dist_h{h}.json' --row 'risk_gbm+every_day+gate+settle+h41+iorb+tailcap75=OUT/cap_h{h}.json' \
    --row 'risk_gbm+settle+h41+dist_roll+offday=OUT/v624_h{h}.json' --row 'risk_gbm+settle+h41+dist_roll+offday_mono=OUT/v624_h{h}.json' \
    --row 'risk_gbm+settle+h41+dist_roll+offday_rate=OUT/v624_h{h}.json' \
    --title 'Step 2 against persistence-logistic and the raw as-of spread (#681)' --output OUT/persistence-step2.json --markdown OUT/persistence-step2.md
PYTHONPATH=src python3 scripts/off_risk_day_624.py paired --input OUT/persistence-step1.json --output OUT/persistence-step1-paired.md
PYTHONPATH=src python3 scripts/off_risk_day_624.py paired --input OUT/persistence-step2.json --output OUT/persistence-step2-paired.md
PYTHONPATH=src python3 scripts/off_risk_day_624.py tables --input OUT/persistence-step2.json --input OUT/persistence-step1.json \
    --cell all --cell 'regime 2018-19' --cell 'regime 2025-26' --output OUT/persistence-tables.md
```

## Reliability within regimes (added 13 October 2026, #683, finding #670)

> *Note, 13 October 2026 (#683).* The slopes in the tables above, and "0.78 to 0.85" and "0.45 to 0.65" in the text, are **pooled across regimes**
> and must not be read as calibration. 2021-23 has no pressure day and forecasts near 0; it adds a long, well-ordered stretch at the bottom of the
> curve and raises the pooled slope. Inside 2018-19 the same forecasts are badly over-spread (`+offday`: 0.48 at h = 1, 0.14 to 0.22 at h = 3 to 5).
> A row is not "nearly calibrated" on a pooled slope. Why, and how to read it: `docs/pivot/diagnostics-reconciliation.md`, point 11.

The slope of each row inside each regime, from the tracked evidence of this page (`evidence/off-risk-day/step1.json` and `step2-off-risk-days.json`; no
forecast is rebuilt, and those files carry points without an interval for a regime's slope; tabulated by `scripts/reliability_regimes_683.py tracked`;
`evidence/reliability-regimes/tracked-step1.md` and `tracked-step2.md`). 1 is reliable; `undefined` is a regime with no pressure day; `–` a regime in
which the forecast is constant or the fit is not formed; `unstable` a near-separated fit (a slope beyond 25 in size); `†` a cell with fewer than 5
pressure days, whose slope is a handful of events' worth. Development data, not a verdict.

### Step 1 rows

#### `risk_gbm+every_day+gate+settle+h41+iorb`

| lead | all days (pooled) | regime 2018-19 | regime 2020 | regime 2021-23 | regime 2024 | regime 2025-26 |
|---|---|---|---|---|---|---|
| 1 | 0.49 | 0.24 | – | undefined | – | 0.40 |
| 2 | 0.57 | 0.28 | – | undefined | – | 0.29 |
| 3 | 0.45 | 0.10 | – | undefined | – | 0.30 |
| 4 | 0.65 | 0.38 | – | undefined | – | 0.26 |
| 5 | 0.56 | 0.08 | – | undefined | – | 0.42 |

#### `risk_gbm+every_day+gate+settle+h41+iorb+tailcap75`

| lead | all days (pooled) | regime 2018-19 | regime 2020 | regime 2021-23 | regime 2024 | regime 2025-26 |
|---|---|---|---|---|---|---|
| 1 | 2.03 | 1.39 | – | undefined | – | – |
| 2 | 2.66 | 2.31 | – | undefined | – | – |
| 3 | 3.19 | 2.31 | – | undefined | – | – |
| 4 | 1.82 | 0.19 | – | undefined | – | – |
| 5 | 2.40 | 1.58 | – | undefined | – | – |

#### `risk_gbm+every_day+gate+settle+h41+iorb+tailcap75+floor`

| lead | all days (pooled) | regime 2018-19 | regime 2020 | regime 2021-23 | regime 2024 | regime 2025-26 |
|---|---|---|---|---|---|---|
| 1 | 0.46 | 0.12 | 6.20† | undefined | unstable | -11.27 |
| 2 | 0.38 | -0.01 | 6.92† | undefined | unstable | -19.70 |
| 3 | 0.27 | -0.05 | 6.66† | undefined | unstable | unstable |
| 4 | 0.40 | 0.05 | 6.39† | undefined | unstable | unstable |
| 5 | 0.46 | 0.12 | 7.09† | undefined | unstable | unstable |

#### `risk_gbm+every_day+gate+settle+h41+iorb+tailcap75+recent_floor`

| lead | all days (pooled) | regime 2018-19 | regime 2020 | regime 2021-23 | regime 2024 | regime 2025-26 |
|---|---|---|---|---|---|---|
| 1 | 0.57 | 0.13 | 0.41† | undefined | – | 0.89 |
| 2 | 0.55 | 0.08 | -0.69† | undefined | – | 0.81 |
| 3 | 0.53 | 0.07 | -0.70† | undefined | – | 0.72 |
| 4 | 0.58 | 0.13 | -0.70† | undefined | – | 0.73 |
| 5 | 0.59 | 0.15 | 0.06† | undefined | – | 0.70 |

#### `risk_gbm+every_day+gate+settle+h41+iorb+tailcap75+state_floor`

| lead | all days (pooled) | regime 2018-19 | regime 2020 | regime 2021-23 | regime 2024 | regime 2025-26 |
|---|---|---|---|---|---|---|
| 1 | 0.73 | 0.12 | 6.20† | undefined | unstable | 1.36 |
| 2 | 0.73 | -0.01 | 6.92† | undefined | unstable | 1.35 |
| 3 | 0.63 | -0.05 | 6.66† | undefined | unstable | 1.35 |
| 4 | 0.75 | 0.05 | 6.39† | undefined | unstable | 1.34 |
| 5 | 0.76 | 0.12 | 7.09† | undefined | unstable | 1.17 |

### Step 2 rows

#### `risk_gbm+every_day+gate+settle+h41+iorb+tailcap75`

| lead | all days (pooled) | regime 2018-19 | regime 2020 | regime 2021-23 | regime 2024 | regime 2025-26 |
|---|---|---|---|---|---|---|
| 1 | 2.03 | 1.39 | – | undefined | – | – |
| 2 | 2.66 | 2.31 | – | undefined | – | – |
| 3 | 3.19 | 2.31 | – | undefined | – | – |
| 4 | 1.82 | 0.19 | – | undefined | – | – |
| 5 | 2.40 | 1.58 | – | undefined | – | – |

#### `risk_gbm+settle+h41+dist_roll`

| lead | all days (pooled) | regime 2018-19 | regime 2020 | regime 2021-23 | regime 2024 | regime 2025-26 |
|---|---|---|---|---|---|---|
| 1 | – | – | – | undefined | – | – |
| 2 | – | – | – | undefined | – | – |
| 3 | – | – | – | undefined | – | – |
| 4 | – | – | – | undefined | – | – |
| 5 | – | – | – | undefined | – | – |

#### `risk_gbm+settle+h41+dist_roll+offday`

| lead | all days (pooled) | regime 2018-19 | regime 2020 | regime 2021-23 | regime 2024 | regime 2025-26 |
|---|---|---|---|---|---|---|
| 1 | 0.83 | 0.48 | 0.61† | undefined | 0.77† | 0.79 |
| 2 | 0.85 | 0.45 | 0.91† | undefined | 2.82† | 0.70 |
| 3 | 0.80 | 0.22 | 1.10† | undefined | -0.35† | 0.73 |
| 4 | 0.78 | 0.14 | 0.98† | undefined | 1.76† | 0.76 |
| 5 | 0.79 | 0.17 | 1.16† | undefined | 1.62† | 0.73 |

#### `risk_gbm+settle+h41+dist_roll+offday_mono`

| lead | all days (pooled) | regime 2018-19 | regime 2020 | regime 2021-23 | regime 2024 | regime 2025-26 |
|---|---|---|---|---|---|---|
| 1 | 0.46 | 0.31 | 0.01† | undefined | -0.69† | 0.32 |
| 2 | 0.39 | 0.14 | 0.37† | undefined | 0.17† | 0.22 |
| 3 | 0.36 | 0.10 | 0.21† | undefined | 0.26† | 0.27 |
| 4 | 0.37 | 0.07 | 0.43† | undefined | – | 0.39 |
| 5 | 0.32 | 0.09 | 0.21† | undefined | 0.39† | 0.21 |

#### `risk_gbm+settle+h41+dist_roll+offday_rate`

| lead | all days (pooled) | regime 2018-19 | regime 2020 | regime 2021-23 | regime 2024 | regime 2025-26 |
|---|---|---|---|---|---|---|
| 1 | 0.73 | 0.20 | 0.66† | undefined | 0.90† | 0.79 |
| 2 | 0.70 | 0.06 | 0.67† | undefined | 2.76† | 0.71 |
| 3 | 0.67 | -0.06 | 0.74† | undefined | 0.39† | 0.73 |
| 4 | 0.65 | -0.13 | 0.70† | undefined | 1.71† | 0.76 |
| 5 | 0.64 | -0.12 | 0.79† | undefined | 1.64† | 0.72 |

## The 2026 extension (#684)

**Development data, exploration only.** Steps 1 and 2 of this page and the comparison with persistence-logistic (#681) were re-run on a panel that runs to 2026-09-03, the opened near-blind tier. Nothing here is a verdict or out-of-sample evidence for a registered candidate (scoring protocol v1, #640); the blind tier stays shut. Eleonora's ruling of 13 October 2026 on PR #710: the re-runs use a separate scratch scored span (`metadata/exploration_684.json`, `--end` on each scoring command, checked by `repo_model.exploration.panel_end`), the published pressure-judge declaration does not move, and the 3-pressure-day minimum stays. Evidence: `docs/pivot/evidence/off-risk-day-684/`.

* **Reproduction.** The `period 2018-2025` cell of every row at every lead is equal, to the digit, to the `all` cell of `docs/pivot/evidence/off-risk-day/persistence-step1.json` and `persistence-step2.json` (days, pressure days, AUROC).
* **The 2026 column is empty**, for the reason on #629's page: 133 ordinary days and 2 pressure days (2026-01-02, 2026-02-18), under the minimum of 3. It is not read. The pooled cell (`all`) now holds 84 pressure days on 1,602 ordinary days, against 82 on 1,469, and no AUROC in it moves by more than 0.02 (for example persistence-logistic at lead 1, 0.897 to 0.894; the raw as-of spread, 0.941 to 0.938; the day-level `offday` variant, 0.887 to 0.878).
* **The earlier reading is not changed.** At lead 1 the day-level variants are not above persistence-logistic on the pooled days (for `offday`, AUROC difference -0.016 [-0.068, +0.017]); at leads 2, 3 and 5 some intervals exclude 0, as on the earlier page, where the regime split showed that to be carried by near-empty regimes. The control, its cap and the every-day row are no better than before. See `persistence-step1-paired.md`, `persistence-step2-paired.md` and `persistence-tables.md`; the 2026 days (2 pressure days) are too few to move that reading.
* **Not re-run:** the three floor rows of step 1 (the forecasts of `scripts/tailcap_floor_610.py`, which gates on the judge's declared window and has no `--end` yet), the judge's own tiers and the `compare` and `pg` outputs of step 2 (the judge is not run on 2026 days). The over-forecast and false-alarm check after reserve-management purchases began needs a 2026 column, which these two days cannot give.

### Reproduction (#684)

With the forecast files built to the same day (`--end 2026-09-03` on `pressure_judge.py forecasts`, `announcement_dating_rescore.py run`, `satiation_distance_598.py run`, `iorb_every_day_579.py run`, `every_day_conditioning_601.py cap` and `off_risk_day_624.py panel` and `run`), and the scratch panels built with `--end 2026-09-03`:

```
PYTHONPATH=src python3 scripts/off_risk_day_624.py measure --panel PUBLISHED.csv --scratch AUG2.csv --declaration metadata/off_risk_day_681.json \
    --pair-with persistence_logistic --row 'persistence_logistic=OUT/bench_h{h}.json' --row 'spread_bps_asof=asof:spread_bps' \
    --row 'risk_gbm+every_day+gate+settle+h41+iorb=OUT/iorb_h{h}.json' --row 'risk_gbm+every_day+gate+settle+h41+iorb+tailcap75=OUT/cap_h{h}.json' \
    --end 2026-09-03 --output OUT/persistence-step1.json --markdown OUT/persistence-step1.md
PYTHONPATH=src python3 scripts/off_risk_day_624.py measure --panel PUBLISHED.csv --scratch AUG2R.csv --declaration metadata/off_risk_day_681.json \
    --pair-with persistence_logistic --row 'persistence_logistic=OUT/bench_h{h}.json' --row 'spread_bps_asof=asof:spread_bps' \
    --row 'risk_gbm+settle+h41+dist_roll=OUT/dist_h{h}.json' --row 'risk_gbm+every_day+gate+settle+h41+iorb+tailcap75=OUT/cap_h{h}.json' \
    --row 'risk_gbm+settle+h41+dist_roll+offday=OUT/v624_h{h}.json' --row 'risk_gbm+settle+h41+dist_roll+offday_mono=OUT/v624_h{h}.json' \
    --row 'risk_gbm+settle+h41+dist_roll+offday_rate=OUT/v624_h{h}.json' --end 2026-09-03 --output OUT/persistence-step2.json --markdown OUT/persistence-step2.md
```
