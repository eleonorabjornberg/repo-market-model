# Skill on the days that are not risk dates (#624)

**Status: a measurement, not a record.** Step 1 is below; step 2 is added in a later commit of the same pull request, after step 1 was
committed. Nothing is published, no day after 2025-12-31 is scored (`docs/decisions/lockbox.md`), and the live record and pin do not move.
Every figure reads 2018-2025, so it describes that history and does not confirm anything (Eleonora's ruling of 11 October 2026 on #567).

## Step 1: do the every-day parts have skill beyond the base rate on those days?

The question (#616): tiers 3 and 5 test calibration on the mean, so a constant floor can pass them without any skill. The measurement asks
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
