# One model on every collected input (#479, of #374)

A scratch measurement under the pressure-day judge. It writes nothing into `docs/runs/`, moves no published figure, and
reads no day after 2025-12-31 (`docs/decisions/lockbox.md`; the script refuses a later panel and the near-blind and
blind tiers are not looked at). The inputs are off in every published declaration. Declared before any score in
`metadata/all_inputs.json` and, for the judge, in `metadata/pressure_judge/candidates/all_inputs_*+recalibrated.json`;
`scripts/all_inputs.py` refuses an uncommitted declaration.

## What was declared

* **Inputs.** The 77 series the source screen (#478) inventories as readable as-of (`docs/pivot/source-screen-result.md`): the 76
  panel series the as-of rule can read and the spread's own as-of lag. Each is listed with its availability in the declaration.
  Nothing is dropped or ranked by its scored performance. Eight series are the direct models' own design (the latest spread,
  the calendar, the two settlements, reserves, the TGA); the other 69 enter as a value, zero where not yet public, and an
  observed indicator. Six scheduled series (the Treasury settlements, the announced IORB change and its days to change) are public
  at a lead of 1 only and leave the inputs at h >= 2, as the screen found.
* **Candidates.** `all_inputs_logistic`: an L1 or L2 logistic of the onset label, the penalty and `C` chosen from a stated grid
  (penalty L1 or L2, `C` = 0.01, 0.03, 0.1, 0.3, 1). `all_inputs_gbm`: a gradient-boosted classifier with a depth limit of 2, 3 or 4,
  no monotone constraint. Both in the frame of the tier-1 passers: walk-forward, refit every 21 scored days, minimum history 61,
  the same fold grid, h = 1 to 5, +5 and +10 bp, recalibrated out of fold against the pressure-day outcome as the onset classifiers
  are (#409). The grid is searched on each refit's training pairs alone: four expanding blocks, an embargo of 5 pairs,
  pooled held-out log loss (`ml.select_all_inputs_setting`). No refit fell back to the default.

## Reproduce

Published panel `4ddc3882…` (`verify-panel` clean); the scratch panel is the screen's (`source-screen-result.md`, Reproduce).

```
PYTHONPATH=src python3 scripts/all_inputs.py declare --output metadata/all_inputs.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --output OUT/bench_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/risk_date_severity.py run --panel AUG2.csv --published PUBLISHED.csv --horizon $h --candidate risk_gbm --output OUT/risk_gbm_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/all_inputs.py run --panel SCREEN.csv --published PUBLISHED.csv --horizon $h --output OUT/ai_h$h.json
PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --output OUT/judge.json --markdown OUT/judge.md OUT/bench_h?.json OUT/risk_gbm_h?.json OUT/ai_h?.json
PYTHONPATH=src python3 scripts/pressure_judge.py table OUT/judge.json --output OUT/tables.md
PYTHONPATH=src python3 scripts/all_inputs.py compare --panel PUBLISHED.csv --output OUT/compare.json OUT/bench_h?.json OUT/risk_gbm_h?.json OUT/ai_h?.json
```

Set `OMP_NUM_THREADS=1` when several fits share a machine. Evidence: `docs/pivot/evidence/all-inputs/` (`judge.md` the judge's full
report, split by regime and day type; `tables.md` its tables; `compare.md` and `compare.json` the pairing against `risk_gbm`, the
episodes and what each refit chose).

## Result: neither candidate passes

Table 1. The judge's row at +5 bp (tiers 1, 3 and 5; 90% stationary-bootstrap intervals), `risk_gbm` and the benchmarks beside it.

| model | onsets flagged | recall [90%] | climatology recall, same false alarms | worst false alarms per onset (limit 2) | tier 3: calibrated regimes with pressure, h = 1 | tier 5 | pass |
|---|---|---|---|---|---|---|---|
| all_inputs_gbm | 15 of 26 | 0.577 [0.381, 0.769] | 0.231 | 3.54 | 2 of 4 | yes | fail (tier 1 no, tier 3 no, tier 5 yes) |
| all_inputs_logistic | 13 of 26 | 0.500 [0.333, 0.682] | 0.231 | 3.50 | 2 of 4 | yes | fail (tier 1 no, tier 3 no, tier 5 yes) |
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.115 | 1.35 | 2 of 4 | no | fail (tier 1 yes, tier 3 no, tier 5 no) |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.231 | 3.42 | 2 of 4 | no | fail |
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.00 | 1 of 4 | no | fail |

* **Tier 1.** Both meet the recall criterion (recall at least 0.5 with the lower end above climatology's recall at the same false alarms)
  but not the false-alarm limit: 3.5 per onset against 2. `risk_gbm` meets tier 1 at 1.35. Tier 3 fails by calibration by regime for both
  (the crying-wolf part, flags per year in the abundant regimes, is met: 0.2 and 0.5 at scarcity state 0). Tier 5 passes for both
  (calibrated and ahead of climatology), which `risk_gbm` does not. The scarce regime alone fails for both.
* **Paired against `risk_gbm`** (Brier score on the +5 bp outcome, positive favours the candidate; 90% interval, h = 1, all days):
  `all_inputs_logistic` -0.0103 [-0.0167, -0.0035], `all_inputs_gbm` -0.0073 [-0.0127, -0.0015]: both worse. Against persistence-logistic:
  -0.0117 [-0.0175, -0.0061] and -0.0087 [-0.0150, -0.0030]: both worse. Against calendar climatology: +0.0034 [+0.0005, +0.0061] and
  +0.0064 [+0.0030, +0.0098]: both better. By regime and by pressure-day type, Tables 2 and 3 of `tables.md` and Table 2 of `compare.md`.
* **Onsets flagged at some lead 1 to 5, paired against `risk_gbm`** (13 of 26): `all_inputs_logistic` 13 of 26, difference +0.000
  [-0.088, +0.095]; `all_inputs_gbm` 15 of 26, +0.077 [-0.046, +0.211]. The intervals include zero.

Table 2. Onset recall by year, at some lead 1 to 5 (the years the directive calls out in bold).

| year | onsets | risk_gbm | all_inputs_logistic | all_inputs_gbm |
|---|---|---|---|---|
| **2018** | 4 | 0/4 | 0/4 | 0/4 |
| 2019 | 13 | 10/13 | 11/13 | 13/13 |
| **2020** | 2 | 0/2 | 0/2 | 0/2 |
| **2024** | 2 | 0/2 | 0/2 | 0/2 |
| 2025 | 5 | 3/5 | 2/5 | 2/5 |

(2021 to 2023 have no onset.) The gain over `risk_gbm` is in 2019, on ordinary days (`all_inputs_gbm` 7 of 12 ordinary-day onsets against 4 of 12), and
it is paid back in 2025. By regime and day type with intervals: Table 1 of `compare.md`.

## Which previously missed episodes are warned

Using the post-mortem's table (`docs/pivot/episode-post-mortem-result.md`, 26 episodes; 11 missed by all five tier-1 passers). The full list
is Table 3 of `compare.md`.

* `all_inputs_gbm` newly warns **2019-05-28, 2019-06-25 and 2019-08-13**, all ordinary days of 2019 that the post-mortem classed "signal too
  late for the lead rule". `all_inputs_logistic` newly warns 2019-08-13 only.
* Neither warns any episode of 2018, 2020 or 2024, or 2025-09-15 and 2025-10-15. `all_inputs_gbm` also loses 2025-09-30, which `risk_gbm` warns;
  `all_inputs_logistic` loses 2025-12-26.

## Ceiling: the episodes with no signal in the panel

The post-mortem classes five episodes as "no signal in the panel": 2018-11-15, 2018-12-17, 2018-12-28, 2020-03-04 and 2024-09-30.
**Neither all-inputs model warns any of them.** Nor does either warn 2018-11-30 (signal present under the cut-off) or 2020-03-12 and
2024-12-26 (too late for the lead rule). Reading all 77 inputs at once adds three 2019 ordinary-day episodes and nothing in 2018, 2020 or 2024:
for those years the data held does not, with these two estimators, carry the signal. This is a statement about these two models on these inputs,
not about the data in general.

## What this does not say

* The cut-offs, penalties and depths are as declared; no other grid, no refit under another label, and no other estimator was tried.
* 26 onsets: one onset moves recall by about 0.04, and the year cells rest on 2 to 13.
* 69 inputs enter with an observed indicator, so the logistic sees about 150 columns on a few onsets a refit; the L1 penalty the
  refits chose most often is `C` = 0.1 to 0.3 (Table 4 of `compare.md`). No input was dropped for its score, so the model includes series the
  screen found to be functions of others.
* Pooled and paired figures use the judge's cut-offs chosen from each refit's training window; no multiple-testing correction.
* The 2026 days, the +10 bp tiers and the confirmation window are not looked at.

## For Eleonora

No candidate passes the full rule, so there is no publishing question and no "Publish?" issue; the inputs stay off in the published declaration.
Nothing here changes a rule or a published figure.
