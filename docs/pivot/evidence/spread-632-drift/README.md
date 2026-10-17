# Why rebuilt #632 variants (a) and (b) drift from the tracked page (#843, finding #840)

Development data only, not a verdict. Days to 2025-12-31; no lockbox day is read. Nothing tracked is re-scored, republished or edited.

## Result

**`ml.py` is not the cause.** Rebuilt at the commit before #634's `ml.py` change, at #634's, at #635's two changes and on main, variants (a) and (b)
give the same probabilities (largest difference below 0.00005) and the same row. The drift comes from the **input panel**: the two columns
`satiation_dist_roll` and `satiation_hinge_roll`, which `scripts/satiation_distance_598.py panel` builds, changed when #622 put them on the per-release H.4.1 rule
(`distance_rule`, `distance_rows` in that script; a different print of `reserve_balances` on Fridays and Mondays). 1,592 of the panel's 1,935
`satiation_dist_roll` cells and 491 of its `satiation_hinge_roll` cells differ. Run `spread_distribution_632.py run` on the older columns and the tracked page's figures come back to the digit.

## Table (h = 1, 1,603 ordinary days, 101 above +5 bp; AUROC and the slope and intercept of `logit P(y = 1) = intercept + slope * logit(p)`)

| tree running `spread_distribution_632.py run` | panel columns | (a) AUROC | (b) AUROC | (b) slope, intercept |
|---|---|---|---|---|
| `011023cb` (the page's last commit), `ml.py` `cfd89531` | current | 0.5673 | 0.9072 | 0.497, -0.707 |
| `09640f5b`, before #634's `ml.py` change (`e56c4fb3`), `ml.py` `ddff8f33` | current | 0.5673 | 0.9072 | 0.497, -0.707 |
| `e56c4fb3`, #634's change | current | 0.5673 | 0.9072 | 0.497, -0.707 |
| `dbbe3d8d`, after #635's missing-column rule (`0e866e66` is between) | current | 0.5673 | 0.9072 | 0.497, -0.707 |
| main `0065b4e3` | current | 0.5673 | 0.9072 | 0.497, -0.707 |
| main `0065b4e3` | **`scripts/satiation_distance_598.py` of `011023cb`** | **0.5629** | **0.9029** | **0.463, -0.762** |
| tracked page, h = 1 | | 0.563 | 0.903 | 0.463, -0.762 |

The references on the same days: `persistence_logistic` 0.8889 (slope 1.046), `calendar_climatology` 0.5657 (they take no distance column, and reproduce).
The 0.9029 and 0.5629 of the issue are the last row at four places; the page's h = 1 slope and intercept (0.463, -0.762) are reproduced as well.
The pooled slope over h = 1 to 5 (0.425 tracked against 0.445) was not rebuilt here: only h = 1 was run, because the h = 1 row already returns the page's figures.

## What was and was not varied

- Each tree was run with `PYTHONPATH=src` in a `git worktree` at its commit, on the panel `AUG2D.csv` built once from main (`verify-panel` clean, digest `4ddc3882…`). So a row of the table varies the model code (`src/`, `scripts/`, `metadata/` at that commit) and holds the input panel fixed.
- The older panel was built by main's `pressure_v1_1.py`, `measurement_fields.py` and `satiation_distance_598.py` with only `scripts/satiation_distance_598.py` replaced by its version at `011023cb`; it is byte-identical to the panel the whole `011023cb` tree builds. Replacing only `src/repo_model/net_settlement.py` (#679, #738) by its older version changes no cell.
- The history in this clone has grafted roots, so `git bisect` between `011023cb` and `09640f5b` named `70a97755` (the first tree whose panel equals main's); that is a squashed commit and says only that the change is in that span. The file-level swap above is the stronger evidence.
- The references were not rebuilt per commit; they reproduce on main already (#829).
- Environment: `/opt/rmm-venv` (numpy 2.4.6, scikit-learn 1.9.1, Python 3.11.17), one thread (`OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`).

## Commands

```
# once, in the checkout of main
PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUBLISHED.csv \
  --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
PYTHONPATH=src python3 -m repo_model.cli verify-panel PUBLISHED.csv --manifest metadata/funding_panel_manifest.json
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
PYTHONPATH=src python3 scripts/satiation_distance_598.py panel --panel AUG2.csv --output AUG2D.csv
PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon 1 --output OUT/bench_h1.json
# older columns: the same three panel commands with scripts/satiation_distance_598.py from 011023cb, giving AUG2D_old.csv
git show 011023cb:scripts/satiation_distance_598.py > scripts/satiation_distance_598.py   # then git checkout it back
# one row of the table, in a worktree at the commit under test (git worktree add W <commit>), or in main for the last two
cd W && PYTHONPATH=src python3 scripts/spread_distribution_632.py run --panel AUG2D.csv --published PUBLISHED.csv --horizon 1 --output OUT/sd_<label>_h1.json
# score all of them on the ordinary days
PYTHONPATH=src python3 docs/pivot/evidence/spread-632-drift/score_h1.py SCRATCH <label>=OUT/sd_<label>_h1.json ...   # SCRATCH holds PUBLISHED.csv and o/bench_h1.json
```

## For Eleonora (a marked question, not settled here)

The tracked tables on `docs/pivot/spread-distribution-result.md` (rows (a) and (b), AUROC, slope, and the judge and distribution tables built on the same forecasts)
were computed on the pre-#622 distance columns; those columns have since been replaced by the per-release ones, so the page cannot be reproduced from today's tree.
The other pages built on `satiation_dist_roll` (the #598 rows, #631's page) may have the same history. Whether #632's tables are re-scored and published anew on the current columns,
or kept as the record of what was run, is hers. #829's per-regime figures are those of the rebuilt rows, that is of the current columns.
