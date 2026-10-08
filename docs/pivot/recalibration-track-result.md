# Per-threshold recalibration of the current model (track C of #374, #380)

A scratch measurement under the judge of #375 as merged (the replacement bar of the ruling on #375, development mode:
scored days 2018-06-29 to 2025-12-31). It writes nothing into `docs/runs/`, moves no published figure and logs nothing
to the live record. No comparison scores a locked day (`docs/decisions/lockbox.md`); the confirmation window is not
looked at.

**Question.** Is recalibrating the current model's exceedance probabilities, per threshold and horizon, enough to
clear the bar? The raw forecast is pressure model v1's `distributional_gbm` (the published funding declaration's gbm,
conformal PID with nested selection), before any recalibration.

**Candidates** (declared in `metadata/pressure_judge.json` and `src/repo_model/group_calibration.py`, committed before
any score was read; each flags at the declared 0.2 at both thresholds, as every other row does):

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

+5 bp, tier 1 at a lead of at least 1 (26 onsets), tier 3 at the worst horizon, tier 5:

| Model | onsets flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | tier 3 flags per 252 days (state 0 / 2021-23), worst h | calibrated by regime (h = 1) | tier 5 Brier gain over climatology, calibrated |
|---|---|---|---|---|---|---|---|
| calendar climatology | 10 of 26 | 0.385 [0.222, 0.556] | 0.385 | 6.62 | 9.0 / 11.1 | 1 of 5 | +0.0000 [+0.0000, +0.0000], yes |
| persistence-logistic | 8 of 26 | 0.308 [0.148, 0.500] | 0.269 | 5.65 | 1.0 / 0.0 | 2 of 5 | -0.0348 [-0.0510, -0.0203], yes |
| published v1 (Platt) | 19 of 26 | 0.731 [0.560, 0.882] | 0.423 | 8.54 | 1.0 / 0.0 | 3 of 5 | +0.0439 [+0.0302, +0.0598], no |
| Platt, rerun (control) | 19 of 26 | 0.731 [0.560, 0.882] | 0.423 | 8.54 | 1.0 / 0.0 | 3 of 5 | +0.0439 [+0.0301, +0.0594], no |
| isotonic | 19 of 26 | 0.731 [0.560, 0.889] | 0.423 | 9.96 | 5.1 / 0.3 | 3 of 5 | +0.0476 [+0.0331, +0.0647], no |
| Platt per group | 19 of 26 | 0.731 [0.577, 0.875] | 0.423 | 7.35 | 1.0 / 0.0 | 3 of 5 | +0.0477 [+0.0334, +0.0646], no |
| group-weighted Platt | 18 of 26 | 0.692 [0.519, 0.850] | 0.423 | 7.35 | 1.0 / 0.0 | 3 of 5 | +0.0464 [+0.0325, +0.0612], no |

Every recalibrator keeps the raw model's recall on onsets (18 or 19 of 26, above climatology's 0.423) and none cuts
its false alarms to the tier-1 limit of 2 per onset (the lowest is 7.35). Tier 3's flag limit holds for all of them at
every lead; what fails is calibration by regime (the 2020 and 2021-23 regimes, where the realised frequency is near
zero and the forecast is not), and the week-ahead window is not calibrated. Isotonic raises state-0 flags to 5.1 per
252 days and false alarms to 9.96 per onset.

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
changes a verdict.

## What it does not show

- The group definition (a four-cell scarcity band by day type) and the weights (60 pairs, 3 events, 0.25) were
  declared once and not searched. A different grouping could behave differently.
- "Conditional conformal" (Gibbs, Cherian & Candès) is read as its probability analogue: a calibration curve per group
  from a finite function class of group indicators. No conformal set is produced. The reading is flagged as a question
  on the pull request.
- The 2021-23 regime has no pressure day, so "calibrated by regime" cannot hold there for any model that forecasts
  above zero, and `recal_*` all fail it for that reason.
- Confirmation (the single look at 2026) is not run and no candidate is put forward for it.
