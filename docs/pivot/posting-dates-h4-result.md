# Does the 2014-2018 back-fill move the 2018-19 spread forecast? (#633, H4 step 3)

Exploration on development data, not a record. It writes nothing into `docs/runs/`, moves no published figure and
reads no day after 2025-12-31 (`docs/decisions/lockbox.md`). Under scoring protocol v1 (#640) development data never
gives a verdict; H4's kill rule is applied below as exploration, as the queue (#46) states it.

**Kill rule of H4 (#46), in words:** H4 is killed if no 2014-18 series has an established posting time, or if training
on the longer history moves the 2018-19 calibration by less than its own interval. Read here, as declared before any
score (`metadata/backfill_spread_633.json`): killed if the two-sided 90% interval of the 2018-19 change in the share of
outcomes inside the forecast's central 90% interval covers zero.

**Reading: H4 is not killed.** The first condition fails: the TGCR/BGCR/SOFR workbook has an established posting time,
17 May 2018, by Eleonora's ruling of 13 October 2026 (`posting-dates-due-diligence.md`). The second fails too: with the
history, 2018-19 coverage of the central 90% interval rises by +0.050 [+0.020, +0.082] for the declared model and by
+0.035 [+0.017, +0.054] for the workbook-only sensitivity. Both intervals exclude zero. What it does not fix: both
arms stay far below the nominal 0.90 in 2018-19, and the share of outcomes above the forecast's 95th percentile does not
move (0.167 → 0.174 declared, 0.191 → 0.191 workbook-only). The history widens the body of the forecast; the 2018-19
upper tail is still under-forecast. Not a confirmation: the protocol's prospective test (H4 step 4) is what would be.

## What was run

* **Model** (`scripts/backfill_spread_633.py`, declared in `metadata/backfill_spread_633.json` before any score): a
  gradient-boosted quantile regression of the spread (SOFR - IORB, bp) at the 23 levels of `scoring_protocol.GRID`,
  leads 1 to 5, the hyperparameters of #632's spread model (`ml.PRESSURE_CLASSIFIER_SETTINGS`), refitted every 21 decision
  days. Inputs read per field through `asof.InformationRule` at each lead, under both guards: the spread at the anchor and
  its 5-row change, TGCR and BGCR less IORB, the 4-week bill less IORB, reserve balances, the TGA, and the target day's
  calendar columns. Each training label is paired with what a forecast of it read at its own decision instant; a fit uses
  only labels observable at its block's decision instant.
* **Why not #632's model:** it reads inputs the back-fill does not carry (SOFR percentiles, settlement and H.4.1 timing,
  satiation distance), so a back-filled row would train no pair and the arms could not differ. This model is a scratch
  model chosen to isolate the history; it is not the H5 incumbent.
* **Arms:** *without*, on the published days only (from 2018-04-03); *with*, the same model on the extended panel of
  `scripts/backfill_history.py panel`, whose published rows reproduce the scratch panel cell for cell. Every block of the
  *with* arm passed `backfill.require_training_only` and `backfill.require_posting_established` with the declared
  instant; its first fit ends 2018-06-28, after 17 May 2018. Same decision days in both: 2018-06-29 to 2025-12-23 (the
  last whose lead-5 target is on or before 2025-12-31).
* **Scoring:** `scoring_protocol.day_scores` (grid CRPS, mean over leads) and `upper_tail_twcrps`, paired per decision
  day, `d = S(without) - S(with)` (positive: the history helps), `scoring_protocol.paired_tests` (stationary bootstrap,
  mean block 10, 10,000 draws, seed 633), shown as two-sided 90% intervals. Skill against B1 (as-of persistence,
  `protocol_benchmarks.b1_forecast` on the published days) for context. Calibration moves are means of paired daily
  differences with a two-sided 90% interval on the same bootstrap.
* **Workbook-only sensitivity**, declared after the first score was seen, so a robustness check rather than a fresh
  test: the same model without the bill rate, reserves and TGA, because the due-diligence table marks the 2014-17 bill
  rates not usable and did not establish the posting of the FRED reserve and TGA levels for those years. It reads only
  the ruled workbook, IORB (an administered rate) and the calendar.

## Results

Full tables: `evidence/posting-dates-h4/score.md` (declared) and `score_wb.md` (workbook-only), with the JSON beside them.

### CRPS, with against without (bp; d > 0 favours the history)

| group | declared: without → with | d [90%] | workbook-only: without → with | d [90%] |
|---|---|---|---|---|
| pooled | 1.865 → 1.784 | +0.081 [+0.035, +0.133] | 1.774 → 1.743 | +0.032 [−0.002, +0.072] |
| **2018-19** | 3.950 → 3.907 | +0.043 [−0.013, +0.101] | 3.939 → 3.875 | +0.064 [+0.009, +0.117] |
| 2020 | 1.575 → 1.470 | +0.106 [−0.030, +0.278] | 1.436 → 1.417 | +0.018 [−0.017, +0.055] |
| 2021-23 | 0.854 → 0.706 | +0.149 [+0.061, +0.257] | 0.763 → 0.730 | +0.033 [−0.041, +0.125] |
| 2024 | 1.149 → 1.142 | +0.007 [−0.011, +0.027] | 1.192 → 1.186 | +0.007 [−0.021, +0.039] |
| 2025 | 2.787 → 2.808 | −0.021 [−0.057, +0.015] | 2.491 → 2.476 | +0.015 [−0.009, +0.042] |
| ordinary days | 1.737 → 1.661 | +0.076 [+0.035, +0.123] | 1.648 → 1.623 | +0.025 [−0.002, +0.054] |
| month ends | 2.056 → 1.998 | +0.058 [+0.008, +0.110] | 1.940 → 1.942 | −0.002 [−0.065, +0.066] |
| tax dates | 3.292 → 3.088 | +0.204 [−0.058, +0.527] | 3.254 → 3.006 | +0.248 [−0.035, +0.634] |
| quarter ends | 3.527 → 3.463 | +0.064 [−0.030, +0.154] | 3.341 → 3.431 | −0.090 [−0.281, +0.099] |

The 2018-19 upper-tail twCRPS moves by +0.036 [−0.011, +0.084] (declared) and +0.058 [+0.011, +0.106] (workbook-only).
Day type is the lead-1 target's (`SplitDeclaration.reporting_day_type`). Both arms beat B1 in 2018-19 by a similar
margin (skill +0.31 without, +0.32 with, in both models).

### Calibration in 2018-19 (share of outcomes, mean over leads)

| measure | declared: without → with, move [90%] | workbook-only: without → with, move [90%] |
|---|---|---|
| inside the central 90% interval (nominal 0.90) | 0.725 → 0.775, +0.050 [+0.020, +0.082] | 0.743 → 0.779, +0.035 [+0.017, +0.054] |
| inside the central 50% interval (nominal 0.50) | 0.294 → 0.317, +0.023 [+0.001, +0.045] | 0.355 → 0.369, +0.014 [−0.004, +0.033] |
| above the 95th percentile (nominal 0.05) | 0.167 → 0.174, +0.006 [−0.009, +0.022] | 0.191 → 0.191, −0.000 [−0.012, +0.012] |

Every regime's 90%-interval coverage rises with the history in both models; the largest moves are in 2020 and 2021-23
(the scores' JSON has them).

## Not checked, or for Eleonora

* **Not the H5 models.** The phase 2 models and #632's read inputs the back-fill lacks; whether the history helps them
  needs those inputs before 2018, which the project does not hold. The nested test against the H5 incumbent (H4 step 3 as
  the manual words it) is therefore not run on the incumbent itself.
* **The declared model's other back-filled inputs** (bill rate, reserves, TGA) have no established posting for
  2014-17; the workbook-only sensitivity is the reading that rests on the ruling alone, and it agrees on the kill rule.
* The back-filled SOFR is an indicative series computed after the fact (the due-diligence table); IORB before 2021 is the
  IOER from FRED.
* Outcomes are the panel's values, not checked against first prints (protocol §11). No hyperparameter was tuned; one
  seed; one refit cadence.
* Whether H4 moves to registration (step 4) is hers: the prospective test is the evidence the protocol counts.

## Reproduce

```
PYTHONPATH=src python3 scripts/backfill_history.py panel --output EXT.csv --scratch SCRATCH.csv
for h in 1 2 3 4 5:
  PYTHONPATH=src python3 scripts/backfill_spread_633.py forecasts --panel SCRATCH.csv --arm without --horizon $h --output OUT/without_h$h.json
  PYTHONPATH=src python3 scripts/backfill_spread_633.py forecasts --panel EXT.csv --arm with --horizon $h --output OUT/with_h$h.json
  (the same with --inputs workbook and --output OUT/<arm>_h${h}_wb.json)
PYTHONPATH=src python3 scripts/backfill_spread_633.py score --scratch SCRATCH.csv --runs OUT --output OUT/score.json --markdown OUT/score.md
PYTHONPATH=src python3 scripts/backfill_spread_633.py score --suffix _wb --scratch SCRATCH.csv --runs OUT --output OUT/score_wb.json --markdown OUT/score_wb.md
```

Panels: scratch `4137d0ad…`, extended `f3acce04…` (workbook `1c889930…`). Use `OMP_NUM_THREADS=1` and the numpy 2.4.6 and
scikit-learn 1.9.1 of `/opt/rmm-venv`; each lead and arm takes about 25 minutes on one core.
