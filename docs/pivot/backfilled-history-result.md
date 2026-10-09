# Back-filled 2014-2018 repo-rate history as training history (#430)

A scratch measurement. It writes nothing into `docs/runs/` and moves no published figure. No comparison scores a
locked day (`docs/decisions/lockbox.md`); scored days are 2018-06-29 to 2025-12-31. The amendment it supports is a
draft in `docs/decisions/information-set.md`, for Eleonora to review.

## Source

| item | value |
|---|---|
| what | New York Fed workbook "Daily indicative TGCR, BGCR, and SOFR volume and rate data (Aug. 2014 - Mar. 2018)", linked from the Bank's additional-information page |
| URL | `https://www.newyorkfed.org/medialibrary/media/markets/Data%20Release.xlsx` |
| retrieved | 2026-10-08T20:53:55Z |
| sha256 | `1c889930bca90edb58c6fe6c4d219f1366261ab9b3e5e0ad54d9a7e62e102180` |
| snapshot | `tests/fixtures/snapshots/backfill_2014_2018/nyfed_repo_backfill/` (the workbook and its manifest) |
| coverage | daily, 2014-08-22 to 2018-03-29; rates in whole basis points; volumes; no percentiles |

## What is known of its publication date

- The file does not state a publication date.
- Its workbook properties say created 2018-05-01 and modified 2018-05-03.
- The host's `Last-Modified` header says 2022-09-15, which is a re-upload, not the first posting.
- **The Bank's original posting date is not established. Settling it, and so whether the workbook was public before the
  first scored decision instant, is Eleonora's call.** The amendment's guard does not depend on it: a back-filled row
  is training history only, and `repo_model.backfill.require_training_only` raises `LookAheadError` for a scored day or
  feature date before the API's first day, 2018-04-03.

## Result

The full tables (headline, onset recall by year, and the splits by pressure-day type, regime and scarcity state, each with 90%
stationary-bootstrap intervals and paired against climatology and persistence) are in the description of the pull request
that added this page. Scope, by Eleonora's ruling of 9 October 2026 on #430: the heavy models (`two_part_gbm`,
`ngboost_laplace`) are scored at h = 1 only; the light ones at h = 1 to 5.

Reading: the history moves little. It changes no pass: nothing passes with or without it. On onset recall the effect goes
both ways by row (for example `ngboost_laplace` 10 to 12 of 27 onsets at h = 1, `hierarchical_logistic` 15 to 13 of 26 over
h = 1 to 5); Brier moves in the fourth decimal. The cold start behind the plateau is not removed: the 2020 and 2024 onsets
are flagged by no row, with or without. The "without" `hierarchical_logistic` row reproduces the re-judge of #416.

## Reproduce

```
PYTHONPATH=src python3 scripts/backfill_history.py panel --output EXT.csv --scratch SCRATCH.csv
PYTHONPATH=src python3 scripts/backfill_history.py run --extended EXT.csv --script scripts/<script>.py -- <the script's own arguments>
PYTHONPATH=src python3 scripts/backfill_history.py judge --panel PUB.csv --output judge.json --markdown judge.md <forecast files>
```

Use `OMP_NUM_THREADS=1`; multi-threaded numerics made parallel runs about fifteen times slower.
