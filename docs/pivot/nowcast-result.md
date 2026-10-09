# A same-day nowcast of the unpublished day (#445)

A scratch measurement under the pressure-day judge (`metadata/pressure_judge.json`) and the published distribution
(`docs/runs/published_distribution_daily_h1.json`). It writes nothing into `docs/runs/` and moves no published
figure: scored days are 2018-06-29 to 2025-12-31 only (`docs/decisions/lockbox.md`), the 2026 window is not looked at, and
every new column is off in every published declaration. Declared before any score in `metadata/nowcast.json`
(committed first; its one amendment is described below and was committed before the variants it adds were scored).

## The question

A forecast for day `T` is made at 16:00 ET on `T-1`. The latest published SOFR is the one for `T-2`, so the published median
for `T` trails the actual spread by about two days. Can a nowcast of the unpublished day `T-1`, from inputs public before 16:00 ET
on `T-1`, shrink that lag?

## Result in one paragraph

On the scored days, the pre-declared nowcast does not shrink the lag. It is further from the actual spread than the naive nowcast
(the spread of `T-2`) by mean absolute error (3.46 against 1.82 bp), and a model that is fed it is no better than the published one. The cause is the nowcast, not the
idea: a perfect nowcast, shown only as an inadmissible ceiling, moves the median's best lag from 2 days to 1 and lowers the CRPS by a
tenth. No pressure-day verdict changes: every model, the benchmarks and the published classifier included, fails all three tiers at +5 bp.

## 1. The inputs, and when each is public

| Input | Reading | Used |
|---|---|---|
| Fed overnight reverse repo for `T-1` | Admitted for a day only if every record of the day was last written (`lastUpdated`) on that date at or before 15:00 ET. Of the 1997 operation dates with a reverse-repo operation from 2018-01-02 to 2025-12-31, 1985 qualify (median last write 13:15:52, latest admitted 14:43:00). 12 are left out: 10 were written again on a later date, 2 were last written after 15:00 (2018-02-16 and 2024-10-16). Declared as `nyfed_on_rrp_sameday`, 15:00 ET on the operation date. | yes |
| Treasury bill rates for `T-1` | Treasury's page says the quotes are obtained "at or near 3:30 PM each trading day" and states no posting time; no archived copy dates a first posting; the H.15 file is at 16:30 ET. Nothing shows a publication before 16:00 ET, so it is **excluded** and declared at the end of its own day (`treasury_bill_rates_sameday`). The page is saved with its checksum in `tests/fixtures/snapshots/treasury_bill_rates_page`. | no |
| Treasury auction and settlement calendar | The settlement of `T-1` is announced a panel day ahead, at 15:00 ET (`treasury_auctions.scheduled_availability`, already in force); no new declaration. | yes |
| Calendar columns | Always known. Used by one extra candidate only. | extra |
| SOFR − IORB of `T-2` and `T-3` | Public at 15:00 ET on `T-1`. | yes |

The reverse-repo reading rests on one assumption the Desk does not state and that cannot be checked from outside: that its API serves a
record from the moment it is written. The nowcast column is declared as the source `spread_nowcast` (15:00 ET on its own day,
the latest of its inputs); `tests/test_nowcast.py` changes every input and label from the nowcast row on and asks the nowcast
to stay the same. Availability tests carry one recorded mutation each, in their docstrings.

## 2. What was declared before any score

* **Six nowcast candidates**, all a ridge regression (penalty 1, refitted every 21 rows on pairs whose own spread was public at
  the row's decision, falling back to the naive nowcast where unfitted or an input is missing): `naive`, `published_only` (no same-day
  input: what mean reversion alone gives), `rrp`, `settlement`, `rrp_settlement` (**the primary, fixed before any score**) and
  `rrp_settlement_calendar` (extra, reported only).
* **Turning-point day**: a scored day whose spread moved by at least 2 bp into it and at least 2 bp the other way out of it
  (a peak or a trough). The label uses the next day's outcome to choose days to score and is never an input of a forecast.
* **Lag**: the integer `k` in −3..5 at which the correlation of the forecast median of day `T` with the actual spread of day `T-k` is
  highest, with the paired 90% stationary-bootstrap interval of the difference from the published model.
* **Distribution variant**: the published model, plus the primary nowcast as one more regressor. **Pressure variant** (`published_v1_nowcast`): the same, for the classifier.

## 3. The amendment, and why the declared variant could not work

The declared variant was scored first (CRPS gain −0.010 [−0.022, +0.002], no lag change). An *oracle* column holding the
nowcast row's own actual spread, put in its place, reproduces the published forecasts **exactly, on every day**. The published gbm is fitted on one-step pairs: a training
target's design row is the row before it, whatever lag the as-of rule gives each field when the model predicts. A regressor added to the design is
therefore learned at the same lag as the spread regressor, and at prediction time is read one day fresher; fed the target's own previous spread it duplicates the
spread regressor in every pair, and the fit ignores it. No nowcast, however good, can be carried by this variant.

The directive says the day-`T` forecast is *built from* the nowcast, so `metadata/nowcast.json` was amended (committed before any
score of what it adds): the **substituted** variant is the published model, fitted exactly as published, whose feature row at prediction carries the nowcast of `T-1`
as its latest spread instead of the published spread of `T-2`. The nowcast is a declared feature of the as-of rule, so its read passes the leakage and staleness guards, and
it is not a regressor of the fit. Two checks fix the mechanism: fed the naive nowcast, the substituted model reproduces the published forecasts exactly
(every day); fed the oracle, it is the ceiling below. The nowcast, its candidates and its setting were not touched by the amendment. Both variants are reported.

## 4. The nowcast's own accuracy (scored days; basis points)

| Nowcast | MAE | RMSE | Closer than naive (absolute error), 90% interval |
|---|---|---|---|
| naive (the spread of `T-2`) | 1.82 | 9.88 | |
| published_only | 3.61 | 9.42 | −1.79 [−1.95, −1.63] |
| rrp | 3.36 | 9.58 | −1.54 [−1.73, −1.36] |
| settlement | 3.70 | 9.39 | −1.87 [−2.05, −1.70] |
| **rrp_settlement (primary)** | 3.46 | 9.56 | −1.64 [−1.84, −1.45] |
| rrp_settlement_calendar | 3.56 | 9.48 | −1.73 [−1.93, −1.55] |

Negative means the candidate is further from the actual spread than the naive nowcast. The primary is closer in squared error only through the
largest days (RMSE 9.56 against 9.88; the paired squared-error difference is +6.4 with interval [−12.9, +37.9]). By split, the primary's
absolute-error difference from naive is: 2018–19 +0.17 [−0.20, +0.63] (no difference); 2020 −3.53; 2021–23 −2.04; 2024 −1.82; 2025–26 −1.07 (all worse than naive); pressure days (> +5 bp) +0.27 [−0.71, +1.43]
(no difference); other days −1.79 [−1.98, −1.61]. The no-same-day-input control (`published_only`) is as far from naive as the candidates that add the reverse repo
and the settlement, and every ridge carries a regime-dependent bias that the naive nowcast does not: mean signed error (nowcast − actual) is about 0 for naive in every regime, against +2.74 (2020) and +3.77 (2021–23) for `published_only` and +4.17 (2020) and +2.40 (2024) for the primary (`accuracy.json`). So
the loss is not from the same-day inputs, and nothing in this run shows whether they carry information a better estimator could use. Full table by regime and pressure-day type: `docs/pivot/evidence/nowcast/accuracy.json`.

## 5. The published distribution at h = 1 (CRPS in bp; lower is better)

| Model | Mean CRPS | Gain over the published model (positive: better), 90% interval | Best lag |
|---|---|---|---|
| as-of persistence | 2.086 | −0.427 [−0.767, −0.183] | 2 |
| **published** | 1.659 | — | 2 |
| declared variant (nowcast as a regressor) | 1.669 | −0.010 [−0.022, +0.002] | 2 |
| **substituted variant (primary nowcast)** | 1.952 | −0.293 [−0.346, −0.243] | 2 |
| ceiling: substituted, fed the actual spread (inadmissible) | 1.469 | +0.191 [+0.162, +0.223] | 1 |

The published model beats as-of persistence on these days (+0.427 [+0.183, +0.767]). The substituted variant is
worse than the published model in every regime and every pressure-day type but the turning-point days, where it is level (+0.010 [−0.164, +0.193]). Gain by split, in the same order
(declared variant / substituted variant / ceiling): turning-point days −0.020 [−0.098, +0.057] / +0.010 [−0.164, +0.193] / +0.289 [−0.066, +0.663];
pressure days (> +5 bp) +0.022 [−0.058, +0.103] / −0.449 [−0.651, −0.255] / +0.519 [+0.250, +0.811]; regimes 2018–19, 2020, 2021–23, 2024, 2025–26 for the
substituted variant: −0.073, −0.851, −0.201, −0.234, −0.396 (all intervals exclude 0). The ceiling is better in every regime and loses only on quarter-ends (31 days). All splits: `docs/pivot/evidence/nowcast/score.json`.

## 6. The lag

Correlation of the forecast median of day `T` with the actual spread of day `T-k`, 1870 scored days:

| k | −1 | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|---|
| published | 0.590 | 0.601 | 0.644 | **0.679** | 0.648 | 0.614 |
| declared variant | 0.587 | 0.600 | 0.641 | **0.677** | 0.644 | 0.608 |
| substituted variant | 0.562 | 0.570 | 0.614 | **0.629** | 0.569 | 0.566 |
| ceiling | 0.600 | 0.628 | **0.673** | 0.655 | 0.625 | 0.594 |
| as-of persistence | 0.390 | 0.424 | 0.552 | **1.000** | 0.552 | 0.424 |

The best lag stays at 2 for the published model and the declared variant in every regime, and for the substituted variant in every regime but 2021–23, where it is 3. The ceiling is the only row at 1 (all days and every regime; paired
interval for the difference from the published model [−3, 0]). The published median is not a copy of the spread of `T-2` here (correlation 0.68 at k = 2; persistence is exactly 1): the lag is real but its sharpness
in 2018–2025 is far less than the directive reports for 2026, a window not looked at. By-regime and by-pressure-day-type tables, with the paired intervals of the
correlation at k = 0 and k = 2: `score.json`.

**Turning-point days** (99 scored days at 2 bp; mean absolute error of the median): the substituted variant is further from the actual spread than the published model by 0.052 [−0.314, +0.211] (no difference); the ceiling is closer by 0.428 [+0.117, +0.759].

## 7. Pressure days: the judge at +5 bp

The classifier `published_v1` (the published distribution recalibrated out of fold) against the same classifier fed the nowcast, tiers 1, 3 and 5 of the
judge's pass rule, h = 1 to 5, scored days 2018-06-29 to 2025-12-31:

| Classifier | Tier 1 (onset warning) | Tier 3 (no crying wolf) | Tier 5 (week ahead) | Onsets flagged | Brier gain over `published_v1`, h = 1, 90% interval |
|---|---|---|---|---|---|
| published_v1 | fail | fail | fail | 2 of 26 | — |
| published_v1_nowcast (declared) | fail | fail | fail | 4 of 26 | +0.00024 [−0.00042, +0.00095] |
| published_v1_nowcast_substituted | fail | fail | fail | 6 of 26 | −0.00441 [−0.00682, −0.00201] |

Calendar climatology and the persistence-logistic benchmark fail all three as well. **No verdict changes.** The substituted classifier flags more onsets (6 of 26 against 2) at the
cost of worse Brier scores at every horizon at +5 bp (h = 1 to 5: −0.0044, −0.0032, −0.0047, −0.0034, −0.0022, every interval below zero). The judge's report and
tables, split by regime and pressure-day type, are in `docs/pivot/evidence/nowcast/judge.md` and `tables.md`; the paired Brier differences in `pair.json`.

## What was not checked, and what is for Eleonora

* **The Desk's API writes and serves together.** The same-day reverse-repo reading rests on `lastUpdated` and on an unstated assumption about when a written record is served (above).
  Whether any availability declaration should change is the question of the "Publish?" issue; this run changes none (`metadata/sources.json` is byte-identical).
* **The nowcast is one linear model.** A ridge on the change of the spread is pulled by the level, which differs by regime, and loses to naive by mean absolute error. This run does not show that
  same-day inputs carry nothing: it shows this pre-declared nowcast does not use them better than the last published value. A better estimator (robust to the level, or nonlinear) is a new
  declaration, not a retuning of this one. The ceiling above says what a good nowcast could be worth.
* Only h = 1 for the distribution; the pressure classifier at h = 1 to 5. The 2026 window and the blind tier are not looked at.
* The declared variant and the amendment: the declared variant was scored before the amendment was written, so the substituted variant's declaration followed one set of scores. The nowcast itself did not change.

## Reproduce

Published panel `4ddc3882…`; scratch panel from `scripts/nowcast.py panel`. The commands are at the top of `scripts/nowcast.py`; for the substituted variant add
`--design substitute` to `walk` and `pressure` (for `walk`, `--which variant|oracle|naive`).

```
PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
PYTHONPATH=src python3 scripts/nowcast.py panel --panel PUB.csv --output NC.csv --summary OUT/panel.json
PYTHONPATH=src python3 scripts/nowcast.py accuracy --panel NC.csv --output OUT/accuracy.json
OMP_NUM_THREADS=1 PYTHONPATH=src /opt/rmm-venv/bin/python scripts/nowcast.py walk --panel NC.csv --which control --output OUT/walk_control.json
PYTHONPATH=src python3 scripts/nowcast.py score --panel NC.csv --output OUT/score.json OUT/walk_*.json
```

Evidence: `docs/pivot/evidence/nowcast/` (`accuracy.json`, `score.json`, `panel.json`, `pair.json`, `judge.md`, `tables.md`).
