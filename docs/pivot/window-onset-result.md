# Training on "an onset in the next five days" (#460, track W of #374)

A scratch measurement under the pressure-day judge. It writes nothing into `docs/runs/` and moves no published figure
(`docs/decisions/lockbox.md`: scored days 2018-06-29 to 2025-12-31 only; the 2026 tier is not opened). Declared before any score
in `metadata/window_onset.json` and in two candidate files under `metadata/pressure_judge/candidates/`; the script
`scripts/window_onset.py` refuses an uncommitted declaration.

## What was declared

* **Target.** An onset at the threshold (`pressure.onsets`: a day above it with five quiet panel days before it) on any of the next
  five panel days. One probability per decision day. The label of a training pair reads training rows t to t + 4; a pair whose window
  reaches past the last training row trains nothing, and `ml._window_onset_labels` raises `LookAheadError` for it.
* **Learners.** The gradient-boosted classifier on the inputs of `two_part_gbm` (`window_onset_gbm`) and the hierarchical logistic
  (`window_onset_hierarchical_logistic`), both unweighted. *A reading for Eleonora:* `two_part_gbm` fits the spread's own law (a
  spike classifier and a size model), which has no window label, so its classifier part and inputs stand for it.
* **Mapping to day-level warnings.** The judge reads five horizon files. The file for horizon h holds, for target day D, the window
  probability made h business days before D, so each decision day's probability covers the five days it opens, the week-ahead maximum
  is that probability itself, and a day is flagged at lead h when the window probability made h days earlier reached the cut-off
  (chosen by the judge's `cutoff_rule`).
* **Calibration.** Platt out of fold against "a pressure day in the next five panel days" (the tier 5 event), on windows that had
  ended by each refit's training end.
* **Weighted-miss rule.** #454 has not merged, so only the unweighted rule is reported.

## Result

Both learners pass tier 5 and fail tiers 1 and 3 (the scarce regime alone fails all three). Training on the window target does give
a well-calibrated week-ahead probability that beats climatology, which the published model does not, but it does not give day-level
warnings: recall of +5 bp onsets at lead of at least 1 is 0.385 for both, below the 0.5 the bar asks, and the gradient-boosted
classifier raises 2.42 false alarms per onset against a limit of 2. Neither beats `calendar_climatology`'s 0.385 recall.

Table 1. Judge rows at +5 bp, h = 1 to 5; 90% stationary-bootstrap intervals (full tables: `evidence/window-onset/tables.md`, report `judge.md`).

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2) | tier 3: worst flags per 252 days, state 0 / 2021-23 | calibrated regimes with pressure, h = 1 | tier 5: calibrated, beats clim. | pass |
|---|---|---|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.00 | 2.7 / 4.4 | 1 of 4 | yes, no | fail |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.231 | 3.42 | 0.5 / 0.0 | 2 of 4 | yes, no | fail |
| published_v1 | 2 of 26 | 0.077 [0.000, 0.185] | 0.192 | 2.35 | 0.2 / 0.0 | 3 of 4 | no, yes | fail |
| window_onset_gbm+recalibrated | 10 of 26 | 0.385 [0.214, 0.567] | 0.192 | 2.42 | 0.0 / 0.0 | 3 of 4 | yes, yes | fail (tiers no / no / yes) |
| window_onset_hierarchical_logistic+recalibrated | 10 of 26 | 0.385 [0.222, 0.559] | 0.258 | 4.46 | 0.0 / 0.0 | 2 of 4 | yes, yes | fail (tiers no / no / yes) |

Table 2. Tier 5 (week ahead, 1869 decision days, base rate 0.152), paired against calendar climatology.

| model | Brier difference vs climatology [90%] (positive: better) | realised minus predicted [90%] |
|---|---|---|
| window_onset_gbm | +0.0147 [+0.0022, +0.0273] | -0.0046 [-0.0466, +0.0403] |
| window_onset_hierarchical_logistic | +0.0199 [+0.0032, +0.0383] | +0.0082 [-0.0337, +0.0509] |
| published_v1 | +0.0439 [+0.0302, +0.0598] | +0.0422 [+0.0127, +0.0756] (not calibrated) |

By regime (Brier difference against climatology, h = 1, `tables.md` Table 3): both learners are worse than climatology in 2018-19
(-0.056 and -0.039) and 2020 (-0.097 and -0.110), where most pressure days fall, and better in 2021-23; the share of 2018-19 pressure
days flagged at h = 1 is 0.14 for the classifier and 0.54 for the logistic. By pressure-day type the classifier flags 0.08 of ordinary
days and the logistic 0.42.

## Reproduce

Published panel `4ddc3882…`; scratch panel from `pressure_v1_1.py panel`. Run with `OMP_NUM_THREADS=1`.

```
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/window_onset.py run --panel AUG.csv --published PUBLISHED.csv --outdir OUT
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --published --output OUT/bench_h$h.json
PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --output OUT/judge.json --markdown OUT/judge.md OUT/bench_h?.json OUT/window_h?.json
PYTHONPATH=src python3 scripts/pressure_judge.py table OUT/judge.json --output OUT/tables.md
```
