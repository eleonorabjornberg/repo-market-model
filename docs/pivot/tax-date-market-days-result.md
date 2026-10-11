# The tax-date window counts market days (#538, of the ruling on #521)

A scratch measurement under the pressure-day judge. It writes nothing into `docs/runs/`, moves no published figure, and reads
no day after 2025-12-31 (`docs/decisions/lockbox.md`). The change is a rule, `data.tax_date_market_days`, and a switch,
`data.tax_window_on_market_days()`, that builds the `tax_date` column with it for one run. The published panel keeps the
DC-holiday window and its digest `4ddc3882…` until a publish pull request rebuilds it; the question of whether to do so is a
separate issue.

## The rule

Eleonora's ruling of 10 October 2026 on #521: the window counts market days, so DC Emancipation Day no longer pushes 16 April
out of it. The deadline stays on the DC rule (26 USC 7503). The two payment days after it are the next two weekdays not in
`metadata/market_holidays.json`. The decision record is drafted in `docs/decisions/calendar-columns.md` for her to merge.

The two rules differ on 11 days of the published panel, all around 16 April, and the rebuilt panel differs from the published
one in no other column (`metadata/tax_date_market_days.json`, `tests/test_tax_date_market_days.py`): 2019-04-16, 2019-04-18,
2020-04-16, 2020-04-20, 2021-04-16, 2021-04-20, 2024-04-16, 2024-04-18, 2025-04-16, 2026-04-16 and 2026-04-20.

## 2019-04-16

It is not one of the 26 onsets of the judge's grid, so tier 1 cannot move on it (the finding on #521 said the same). It is now a
risk date, and the passers give it a probability at every horizon; before they gave exactly 0.

| passer, P(spread above +5 bp on 2019-04-16) | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|
| risk_gbm, before | 0 | 0 | 0 | 0 | 0 |
| risk_gbm, after | 0.43 | 0.27 | 0.28 | 0.29 | 0.29 |
| risk_logistic, before | 0 | 0 | 0 | 0 | 0 |
| risk_logistic, after | 0.97 | 0.90 | 0.95 | 0.93 | 0.64 |

## What moved

Five risk-date passers and their `+every_day` and `+gate` variants (#506, #525, #532), re-scored on the market-day panel under
the judge in force (both the flat and the weighted miss rule), and set beside the same scoring on the published panel. The
published-panel scoring reproduces #532's committed `summary.md` byte for byte, so the comparison is like for like. Table: 
`docs/pivot/evidence/tax-date-market-days/delta.md` (`a -> b` where a cell moved), and the full tables, judge reports, pairings
by regime and day type, and readings (a), (b), (e) under the same directory.

- **The passers themselves hardly move.** Onsets flagged are unchanged for `risk_gbm` (13 of 26), `risk_logistic` (14 and 16) and
  `risk_logistic_base`; `risk_gbm_base` gains one onset under the weighted rule (14 to 15; 2025-09-15, a tax date) and
  `risk_quantile_skewt_base` is unchanged. Worst false alarms per onset move by at most 0.08 (`risk_gbm`, 0.80 to 0.88 weighted).
  Tier 1 stays met by every passer under both rules, and tiers 3 and 5 stay unmet.
- **The `+gate` rows move by one or two onsets, in both directions.** Under the weighted rule `risk_gbm+every_day+gate` stays at 17
  of 26 with false alarms 1.63 to 1.67, and `risk_gbm_base+every_day+gate` goes from 18 to 17 of 26 (1.62 to 1.68), losing
  2025-09-30. Tier 1 under the weighted rule is still met by both and still by `risk_quantile_skewt_base+every_day+gate`, which
  stays at exactly 2.00; tier 5 is still unmet on the gradient-boosted rows. No `+gate` row passes the full rule under either
  miss rule, as before.
- **Years.** No passer or `+gate` row changes on a 2018 or 2024 onset under either rule. On 2020, the only change among them is
  flat-rule: `risk_logistic+every_day+gate` now warns 2020-03-12. The other flips are 2025 onsets (2025-09-15, 2025-09-30,
  2025-10-15) and are listed in `compare.md` and `compare-weighted.md`, Table 5.
- **Small against the interval.** Every recall difference between the two scorings is one or two onsets of 26, well inside the
  width of the 90% intervals of `summary.md` (about 0.35 wide). This is not a result about the window's value: with 26 onsets,
  moving a day or two does not change what the passers can see.

Nothing here changes a verdict of #532 or #525.

## Reproduce

`/opt/rmm-venv`, `OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`. The published panel `PUB.csv` builds as in
`REPRODUCIBILITY.md`; the market-day one builds with the wrapper, and `verify-panel` accepts it against the digest declared in
`metadata/tax_date_market_days.json`.

```
PYTHONPATH=src python3 scripts/tax_date_market_days.py -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output NEW/PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
# then, for D in OLD (plain `python3`) and NEW (prefix every command with `python3 scripts/tax_date_market_days.py`), the pipeline of
# docs/pivot/risk-date-false-alarm-controls-result.md, "Reproduce", on D/PUB.csv
PYTHONPATH=src python3 scripts/tax_date_market_days_delta.py OLD/out/summary.md NEW/out/summary.md --output delta.md
```

## Not checked, or for Eleonora

- Whether the published panel is rebuilt with the market-day column (a new digest, and every record bound to `4ddc3882…`
  would then be re-scored and republished) is hers; see the "Publish?" issue linked from the pull request.
- The benchmarks (calendar climatology, persistence-logistic) were regenerated on the market-day panel, so their tax-date
  feature moves with the rule too; they are not reported separately.
- The announced-postponements part of her intended rule (`calendar-columns.md`) is not part of this change.
- 26 onsets; no multiple-testing correction over thirty rows and two rules.
