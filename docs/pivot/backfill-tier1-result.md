# Back-filled 2014–2018 history on the five tier-1 passers (#484)

A scratch measurement. It writes nothing into `docs/runs/` and moves no published figure. No comparison scores a locked day
(`docs/decisions/lockbox.md`): scored days are 2018-06-29 to 2025-12-31, and the back-filled rows (2014-08-22 to 2018-04-02)
are training history only, under the guard of `repo_model.backfill` (#430; the amendment of `information-set.md` that
allows it is a draft, not in force). Declared before any score in `metadata/backfill_tier1.json`; the five
`<model>+history` candidates are declared in `metadata/pressure_judge/candidates/` and were committed before they were scored.

## What was run

The five tier-1 passers of #428 (`risk_gbm`, `risk_gbm_base`, `risk_logistic`, `risk_logistic_base`,
`risk_quantile_skewt_base`), at h = 1 to 5, in two arms:

* **without:** `scripts/risk_date_severity.py run`, unchanged, on the published days' panel with the measurement columns, through
  `scripts/backfill_history.py run --control` (the same recorders read it).
* **with:** the same script, unchanged, through `scripts/backfill_history.py run` on the extended panel
  (`backfill_history.py panel`, then `augment`): the same rows from 2018-04-03 and 899 back-filled rows before them. `minimum_history`
  is raised by the 899, so the first scored origin, every refit block and every scored day are the ones of the arm without
  the history; each fit's training frame also holds the back-filled rows.

Both arms are judged together by `backfill_history.py judge` (the pressure-day judge, under the rule in force: the weighted miss
rule of `metadata/weighted_miss.json`), with the published benchmarks. **The arm without reproduces the record:** judged under the flat
(unweighted) count it gives exactly the false alarms per horizon of `docs/pivot/evidence/pressure-audit/score.json` for all five
models (for example `risk_gbm` 35, 28, 27, 23, 27 at h = 1 to 5).

## Missing inputs before 2018

Declared before scoring: no fill; a back-filled row whose read of a declared input is blank trains no pair (`ml._pressure_pairs`).

| input | back-filled value | who reads it |
|---|---|---|
| `sofr_p75_iorb_bps`, `sofr_p99_iorb_bps` | none: the workbook carries no percentiles | `risk_gbm`, `risk_logistic` |
| `tga_daily`, `tga_daily_change` | none: the daily TGA snapshot starts on the first published day | `risk_gbm`, `risk_logistic` |
| every other declared input (SOFR, IORB, calendar, reserves, scarcity state, weekly TGA, settlements, ON RRP) | present | all five |

So **`risk_gbm` and `risk_logistic` use no back-filled risk-date row** (Table 7). Their fits still differ slightly with the history, for
a reason the declaration did not foresee: ten published label days of April to June 2018 had no weekly-TGA history to form the TGA change
and trained no pair; with the back-filled rows before them they do (51 to 61 pairs in the first fit). The three `_base` models use
890 of the 899 back-filled label days (the other nine have no complete read); of those, 194 are risk dates at h = 1 and 132 at h >= 2,
which is what a risk-date model fits.

## Result

Full tables: `docs/pivot/evidence/backfill-tier1/tables.md`; the judge's full report is `judge.md` beside it.

**Reading.** The history changes no verdict. All ten rows pass tier 1 and fail tiers 3 and 5, with or without it. It does not remove the cold start where it
matters: no model flags a 2020 or 2024 onset more often with it. On recall it moves the models in both directions and no paired
difference excludes zero.

| model | onsets flagged without → with (of 26) | paired difference (with − without), 90% | worst weighted false alarms per onset |
|---|---|---|---|
| `risk_gbm` | 13 → 13 | +0.000 [+0.000, +0.000] | 0.80 → 0.84 |
| `risk_gbm_base` | 14 → 16 | +0.077 [+0.000, +0.167] | 0.97 → 1.68 |
| `risk_logistic` | 16 → 15 | −0.038 [−0.111, +0.000] | 1.74 → 1.74 |
| `risk_logistic_base` | 15 → 13 | −0.077 [−0.167, +0.000] | 1.65 → 1.41 |
| `risk_quantile_skewt_base` | 15 → 15 | +0.000 [−0.087, +0.087] | 1.62 → 1.36 |

* **2018, 2020 and 2024 (Table 3).** 2018: `risk_gbm_base` and `risk_quantile_skewt_base` flag one of the four 2018 onsets with the history and none without; the other three models flag none either way.
  2020: none of ten rows flags either onset. 2024: only `risk_logistic` without the history flags one of two, and loses it with the history.
  The other gain is in 2025 (`risk_gbm_base` 4 to 5 of 5), not in the years the cold start was meant to cure.
* **False alarms (Tables 4 and 5).** For `risk_gbm_base` the history raises the worst-horizon weighted false alarms per onset from 0.97 to 1.68 and the 2020 figure from 8.50 to 13.62
  per onset (two onsets); `risk_logistic_base` falls in both 2020 and 2024, `risk_quantile_skewt_base` falls in 2020 and rises in 2024 (0.12 to 1.25). All stay inside tier 1's limit of 2 under the weighted rule in force.
* **Brier (Table 2).** `risk_quantile_skewt_base` improves at h = 1 to 4 (for example +0.0060 [+0.0026, +0.0098] at h = 1, positive: the history helps); `risk_gbm_base` is worse at h = 1
  (−0.0022 [−0.0040, −0.0004]); the rest cover zero. Twenty-five cells were read, so isolated intervals that exclude zero are not a finding.
* **Training history at each 2018 onset (Table 6).** The cold start is only partly removed. At the first refit (training end 2018-06-27): 61 rows, 3 pressure days and 1 onset without the back-fill;
  960 rows, 8 pressure days and 4 onsets with it, of which 5 pressure days are on risk dates (1 without). By the November 2018 refits: 5 → 10 pressure days, 2 → 5 onsets.
  The fit has seen a few more episodes, and no model flags more than one of the four 2018 onsets.

Counting conventions are those of `diagnostics-reconciliation.md`: 26 onsets on the shared grid of h = 1 to 5 (four in 2018); Table 6 reads the five 2018 onsets on the h = 1 grid and the
four on the h = 5 grid, so the first onset (2018-06-29) has no h = 5 row.

## Not checked, or for Eleonora

* **The workbook's original posting date** is still not established (`backfilled-history-result.md`), so whether the back-fill was public before the first scored decision instant is hers to settle. This page uses it as training history only.
* Whether any of this changes the use of the back-fill (the amendment is a draft) is her call; the measurement shows no change of verdict.
* The percentiles and the daily TGA are not back-filled; a source for them before 2018 would change what `risk_gbm` and `risk_logistic` can learn from the history. Not tried.
* Only the declared five models, the declared arms and the rule in force were scored; the unweighted-rule judge row of the arm with the history was not run.

## Reproduce

```
PYTHONPATH=src python3 scripts/backfill_history.py panel --output EXT.csv --scratch SCRATCH.csv
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel SCRATCH.csv --output SCRATCH_AUG.csv
PYTHONPATH=src python3 scripts/backfill_history.py augment --extended EXT.csv --augmented SCRATCH_AUG.csv --output EXT_AUG.csv
# published panel: the build and verify commands of REPRODUCIBILITY.md -> PUB.csv
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUB.csv --horizon $h --published --output OUT/bench_h$h.json
for m in <the five models>, h in 1 2 3 4 5:
  PYTHONPATH=src python3 scripts/backfill_history.py run --control --extended SCRATCH_AUG.csv --script scripts/risk_date_severity.py \
    --folds-output OUT/without_${m}_h$h.folds.json --pairs-output OUT/without_${m}_h$h.pairs.json -- \
    run --panel SCRATCH_AUG.csv --published PUB.csv --horizon $h --candidate $m --output OUT/without_${m}_h$h.raw.json
  PYTHONPATH=src python3 scripts/backfill_history.py run --extended EXT_AUG.csv --script scripts/risk_date_severity.py \
    --folds-output OUT/with_${m}_h$h.folds.json --pairs-output OUT/with_${m}_h$h.pairs.json -- \
    run --panel EXT_AUG.csv --published PUB.csv --horizon $h --candidate $m --output OUT/with_${m}_h$h.raw.json
for h in 1 2 3 4 5:
  PYTHONPATH=src python3 scripts/backfill_history.py relabel --suffix "" --output OUT/without_h$h.json OUT/without_*_h$h.raw.json
  PYTHONPATH=src python3 scripts/backfill_history.py relabel --suffix +history --output OUT/with_h$h.json OUT/with_*_h$h.raw.json
PYTHONPATH=src python3 scripts/backfill_history.py judge --panel PUB.csv --output OUT/judge.json --markdown OUT/judge.md OUT/bench_h?.json OUT/without_h?.json OUT/with_h?.json
PYTHONPATH=src python3 scripts/backfill_tier1_report.py --judge OUT/judge.json --runs OUT --published PUB.csv --extended EXT_AUG.csv --output OUT/tables.md --json OUT/training.json
```

Use `OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1` and `MKL_NUM_THREADS=1`; the numpy 2.4.6 and scikit-learn 1.9.1 of `/opt/rmm-venv`. The judge run over all eleven models takes about twelve minutes.
