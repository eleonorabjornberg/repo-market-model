# The pressure judge under the weighted miss rule in force: the tier 1 rows re-run (#472)

The judge table of the risk-date severity candidates and the benchmarks, re-run with `judge --rule declared`, which is
now the weighted rule of [`docs/decisions/weighted-miss.md`](../decisions/weighted-miss.md) (`in_force: true` in
`metadata/weighted_miss.json`, adopted by Eleonora on #464). A scratch measurement: it writes nothing into `docs/runs/`.
Scored days 2018-06-29 to 2025-12-31, h = 1 to 5, +5 bp primary, 90% stationary-bootstrap intervals. No comparison
scores a locked day (`docs/decisions/lockbox.md`); the 2026 confirmation tier is not opened by this change.

The rule: a flag on a day that is not a pressure day is a false alarm of weight 0.25 within 2 trading days of the nearest
pressure day, 0.5 within 3 to 5, and 1 beyond. The limit stays at 2 per onset, and each refit chooses its flag cut-off on
the weighted count of its training window using only the pressure days known at the refit.

## Result

Table 1 is the judge's own table (full tables and the split by regime and pressure-day type in
[`evidence/weighted-miss-in-force/`](evidence/weighted-miss-in-force/)). Worst false alarms per onset are the flat count
at the worst horizon.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2) | tier 1 |
|---|---|---|---|---|---|
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 0.154 | 1.38 | pass |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 0.154 | 1.50 | pass |
| risk_logistic | 16 of 26 | 0.615 [0.435, 0.800] | 0.192 | 2.42 | pass |
| risk_logistic_base | 15 of 26 | 0.577 [0.391, 0.762] | 0.192 | 2.31 | pass |
| risk_quantile_skewt_base | 15 of 26 | 0.577 [0.391, 0.750] | 0.192 | 2.31 | pass |
| risk_quantile_skewt | 14 of 26 | 0.538 [0.360, 0.719] | 0.231 | 3.42 | fail |
| published_v1 | 14 of 26 | 0.538 [0.350, 0.720] | 0.269 | 5.73 | fail |
| persistence_logistic | 12 of 26 | 0.462 [0.273, 0.650] | 0.380 | 7.04 | fail |
| calendar_climatology | 12 of 26 | 0.462 [0.286, 0.667] | 0.358 | 6.69 | fail |

No candidate passes the pass rule: tier 3 (calibration by regime) and tier 5 fail for all nine, as in the unweighted
table of [`risk-date-severity-result.md`](risk-date-severity-result.md).

## Check against #463

Criterion 4 of #472 asked that the tier 1 rows of risk_gbm, risk_gbm_base, risk_logistic, risk_logistic_base and
risk_quantile_skewt_base match the weighted-rule figures of [`weighted-miss-result.md`](weighted-miss-result.md)
(`evidence/weighted-miss/table.md`). They do, on every column that table shows: onsets warned (13, 14, 16, 15, 15),
false alarms per onset (1.38, 1.50, 2.42, 2.31, 2.31) and the tier 1 verdict (pass). `risk_quantile_skewt` (14, 3.42,
fail), `published_v1` (14, 5.73, fail), `persistence_logistic` and `calendar_climatology` match too. The two runs share
the forecasts' code path, so a match is what the switch should give; this is the check that it does.

## Reproduce

Published panel `4ddc3882…` (`REPRODUCIBILITY.md`), the scratch panels as in `risk-date-severity-result.md`. Set
`OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1` and `MKL_NUM_THREADS=1` when running several fits at once. Each
`risk_date_severity.py run` took 11 to 16 minutes and each benchmark `forecasts` run about 6 minutes at one thread.

```
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/risk_date_severity.py run --panel AUG2.csv --published PUBLISHED.csv --horizon $h --output OUT/risk_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --published --output OUT/bench_h$h.json
PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --output OUT/judge.json --markdown OUT/judge.md OUT/bench_h?.json OUT/risk_h?.json
PYTHONPATH=src python3 scripts/pressure_judge.py table OUT/judge.json --output OUT/tables.md
```
