# Per-threshold recalibration of the current model (track C of #374, #380)

A scratch measurement under the judge of #375 as amended by #407 (the replacement bar of the ruling on #375, development
mode: each flag cut-off is chosen from the refit's training window alone; scored days 2018-06-29 to 2025-12-31). It writes nothing into `docs/runs/`, moves no published figure and logs nothing
to the live record. No comparison scores a locked day (`docs/decisions/lockbox.md`); the confirmation window is not
looked at.

**Question.** Is recalibrating the current model's exceedance probabilities, per threshold and horizon, enough to
clear the bar? The raw forecast is pressure model v1's `distributional_gbm` (the published funding declaration's gbm,
conformal PID with nested selection), before any recalibration.

**Candidates** (declared in `metadata/pressure_judge.json` and `src/repo_model/group_calibration.py`, committed before
any score was read; none declares a cut-off, the judge's declared rule chooses each one from the refit's training window):

- `recal_isotonic`: the CORP isotonic fit, out of fold, per threshold and horizon.
- `recal_platt`: Platt out of fold, per threshold and horizon. It is the published recalibration, rerun as the pooled
  control; its probabilities equal `published_v1`'s.
- `recal_platt_group`: Platt fitted per group, the group being the reserve-scarcity state band (0 and 1 ample, 2 and 3
  scarce) by day type (scheduled: quarter-end, month-end, tax date; otherwise ordinary), both read as of the decision
  instant. The pooled Platt curve stands in when a group holds fewer than 60 earlier pairs or 3 events.
- `recal_platt_weighted`: one Platt curve per target group on every earlier pair, the group's own pairs weighted 1 and
  all others 0.25 (a regime-weighted calibration after Barber et al.).

Every fit is walk-forward: a block's forecasts use only pairs whose scored day is at or before the block's last
training label, and nothing is fitted before 250 pairs with 5 events (the published recalibration's gate). Each
threshold is recalibrated on its own and the curve is made non-increasing in tau.

**Reproduce** (panel digest `4ddc3882…`, the published panel):

```
PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PANEL.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
PYTHONPATH=src /opt/rmm-venv/bin/python scripts/recalibration_track.py horizon --panel PANEL.csv --horizon H --output OUT/recal_hH.json
PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PANEL.csv --horizon H --output OUT/bench_hH.json
PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PANEL.csv --output OUT/judge.json --markdown OUT/judge.md OUT/bench_h?.json OUT/recal_h?.json
PYTHONPATH=src python3 scripts/recalibration_track.py compare --panel PANEL.csv --output OUT/paired.json OUT/recal_h?.json
```

Run with `OMP_NUM_THREADS=1` when several horizons run at once: the gbm's threads otherwise oversubscribe the cores.

## Result: no candidate passes; recalibration alone is not enough

Table 1 is the judge's own table (`pressure_judge.py table`), +5 bp, h = 1 to 5, tier 1 at a lead of at least 1 (26 onsets),
tier 3 at the worst horizon, tier 5. The flag cut-off of every row is the one the declared rule chose from the refit's
training window; an earlier version of this page flagged at a fixed 0.2, which the amended judge no longer allows, and
its recall figures (18 or 19 of 26 onsets) do not carry over.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes with pressure, h = 1 | tier 5: calibrated, beats clim. | pass | scarce regime alone (tiers 1 / 3 / 5) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.00 | 2.7 / 4.4 | 1 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.231 | 3.42 | 0.5 / 0.0 | 2 of 4 | yes, no | fail (tiers no / no / no) | fail (no / no / no) |
| published_v1 | 2 of 26 | 0.077 [0.000, 0.185] | 0.192 | 2.35 | 0.2 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| recal_isotonic | 3 of 26 | 0.115 [0.000, 0.231] | 0.192 | 2.42 | 0.0 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| recal_platt | 2 of 26 | 0.077 [0.000, 0.179] | 0.192 | 2.35 | 0.2 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| recal_platt_group | 5 of 26 | 0.192 [0.067, 0.333] | 0.231 | 2.77 | 0.2 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |
| recal_platt_weighted | 5 of 26 | 0.192 [0.069, 0.333] | 0.231 | 2.77 | 0.2 / 0.0 | 3 of 4 | no, yes | fail (tiers no / no / no) | fail (no / no / no) |

Under the chosen cut-offs the recalibrators flag few onsets (2 to 5 of 26) and none beats climatology's recall at the same
false alarms by more than the interval allows; the pooled Platt control reproduces `published_v1` exactly. Every
candidate fails tiers 1, 3 and 5. Tier 3's flag limit holds at every lead; what fails is calibration by regime (the
regimes with pressure days), and the week-ahead window is not calibrated.

### Does conditioning help? Brier at +5 bp, paired against the pooled Platt control

Brier of pooled Platt minus Brier of the recalibrator (positive = recalibrator better), 90% stationary bootstrap
(block length 10, 2000 replications, the judge's seed), all scored days:

| comparison (Brier of pooled Platt minus Brier of X; positive = X better) | h=1 | h=2 | h=3 | h=4 | h=5 |
|---|---|---|---|---|---|
| +5 bp recal_isotonic | -0.0006 [-0.0024, +0.0010] | -0.0002 [-0.0021, +0.0015] | -0.0000 [-0.0018, +0.0018] | +0.0001 [-0.0015, +0.0019] | +0.0017 [-0.0004, +0.0044] |
| +5 bp recal_platt_group | +0.0017 [+0.0006, +0.0029] | +0.0021 [+0.0003, +0.0044] | +0.0033 [+0.0012, +0.0060] | +0.0034 [+0.0013, +0.0063] | +0.0035 [+0.0014, +0.0064] |
| +5 bp recal_platt_weighted | +0.0014 [+0.0009, +0.0020] | +0.0017 [+0.0007, +0.0029] | +0.0022 [+0.0013, +0.0035] | +0.0026 [+0.0016, +0.0039] | +0.0027 [+0.0016, +0.0039] |
| +10 bp recal_isotonic | +0.0010 [-0.0008, +0.0028] | +0.0001 [-0.0003, +0.0006] | -0.0001 [-0.0011, +0.0011] | +0.0004 [-0.0003, +0.0012] | +0.0002 [-0.0005, +0.0009] |
| +10 bp recal_platt_group | +0.0002 [-0.0002, +0.0008] | +0.0011 [-0.0001, +0.0026] | +0.0015 [+0.0002, +0.0031] | +0.0018 [+0.0003, +0.0038] | +0.0019 [+0.0003, +0.0038] |
| +10 bp recal_platt_weighted | +0.0006 [+0.0003, +0.0010] | +0.0011 [+0.0003, +0.0020] | +0.0010 [+0.0004, +0.0018] | +0.0012 [+0.0005, +0.0022] | +0.0014 [+0.0005, +0.0024] |

Fitting the curve per group lowers Brier at every horizon at +5 bp (intervals above zero at all five) and at +10 bp from
h = 3. The group-weighted curve does so at every horizon at both thresholds. Isotonic does not beat pooled Platt at any
horizon. The gain is in the all-days Brier, which is the measure `docs/decisions/pressure-probability.md`'s earlier gate
used and the replacement bar does not use: it moves recall, false alarms and week-ahead calibration by nothing that
changes a verdict (flag counts: Table 1).

## What it does not show

- The group definition (a four-cell scarcity band by day type) and the weights (60 pairs, 3 events, 0.25) were
  declared once and not searched. A different grouping could behave differently.
- "Conditional conformal" (Gibbs, Cherian & Candès) is read as its probability analogue: a calibration curve per group
  from a finite function class of group indicators. No conformal set is produced. The reading is flagged as a question
  on the pull request.
- The 2021-23 regime has no pressure day, so "calibrated by regime" cannot hold there for any model that forecasts
  above zero, and `recal_*` all fail it for that reason.
- Confirmation (the single look at 2026) is not run and no candidate is put forward for it.
