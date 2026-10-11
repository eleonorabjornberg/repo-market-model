# A latent funding-stress factor (#543, of #374)

> **Correction of 11 October 2026 (#578).** The tables and prose below are the first scoring of 11 October. The model was re-scored after the factor was carried one row short of the scored day (#575), with the shared judge table now printing both false-alarm counts (#577). The re-score is in `docs/pivot/evidence/latent-factor/`; the figures below are not updated. The before-and-after figures are in [`audit-fixes-578-result.md`](audit-fixes-578-result.md).

A scratch measurement under the pressure-day judge. It writes nothing into `docs/runs/`, publishes nothing, moves no published
figure, scores no day of 2026 and reads no day after 2025-12-31 (`docs/decisions/lockbox.md`; the scripts refuse a later panel).
No rule, threshold, onset definition, cut-off rule or availability time changes. The model was declared in
`metadata/latent_factor.json` and committed before the first forecast was fitted; `scripts/latent_factor.py` refuses an uncommitted
declaration. One declared row was added after a first look (below).

## What was declared

One hidden stress factor drives nine daily series, each read as of the decision instant through the information rule: the SOFR 1st,
25th, 75th and 99th percentiles, TGCR, BGCR and EFFR above IORB (basis points), the SOFR 99th-minus-1st dispersion, and the log of
ON RRP take-up. The factor is an AR(1) with unit innovation variance; each series has its own mean, loading and idiosyncratic noise.
Fitted by maximum likelihood (EM with a scalar Kalman smoother and parameter expansion) on the training frame of each refit block of
the judge's 21-day cadence, then filtered forward through each forecast's own as-of history (the filter never smooths; a series that
is a hole on a day informs nothing that day and is never filled). The factor is signed so the SOFR 99th percentile loads positively.
The OFR series are not used, so the guard of #522 is not needed.

The probability of a pressure day at T+h comes from the factor carried h rows ahead, by three declared mappings to the spread:

| row | mapping |
|---|---|
| `latent_factor` | the directive's: an OLS of the spread on the filtered factor, and the tail of the carried factor above the level that mapping puts at the +5 bp point |
| `latent_factor_resid` | the same with the OLS residual variance added to the spread's predictive variance |
| `latent_factor_logit` | **added after a first look**: a ridge logistic of `spread > tau` on the carried factor mean, one fit per threshold |

The third row was added because the first two, run once at h = 1, had a Brier score worse than a constant's: with the innovation
variance fixed at 1 the one-day factor move is wide, so the Gaussian mapping is over-dispersed. That look at h = 1, and no other, led to
the third row; nothing else changed after it, and all three rows are reported. Each also appears as the every-day component under the
risk-date passer `risk_gbm`, by the rule of #506 (the passer's forecast on a risk date, the model's on any other day). That is
the structure of the hurdle of #539 with this model in place of its every-day hazard, but without the hurdle's Platt or isotonic
calibration of the hazard: #539 merged while this was being scored, after the declaration was committed, and its code was not used.

## Result

Scored 2018-06-29 to 2025-12-31 as the judge declares, under the weighted miss rule in force and, beside it, the flat rule. Tier 1
is onset warning at lead 1 or more (26 onsets), as (a) of [`judge-readings-result.md`](judge-readings-result.md): onsets flagged / worst
false alarms per onset. The bar is recall at least 0.5 with the interval above climatology and at most 2 false alarms per onset.

| row | tier 1, weighted | tier 1, flat | tier 3 | tier 5 |
|---|---|---|---|---|
| `latent_factor` | 14 / 3.38 fail | 11 / 5.46 fail | fail | fail |
| `latent_factor_resid` | 14 / 3.34 fail | 11 / 5.46 fail | fail | fail |
| `latent_factor_logit` | 12 / 3.37 fail | 11 / 4.65 fail | fail | pass |
| `risk_gbm+latent_factor` | 13 / 3.09 fail | 12 / 3.50 fail | fail | fail |
| `risk_gbm+latent_factor_resid` | 13 / 3.09 fail | 12 / 3.50 fail | fail | fail |
| `risk_gbm+latent_factor_logit` | 15 / 2.15 fail | 12 / 2.54 fail | fail | pass |
| `risk_gbm` | 13 / 0.80 pass | 13 / 1.35 pass | fail | fail |
| `ngboost_laplace` | 17 / 1.73 pass | 15 / 2.54 fail | fail | fail |
| calendar climatology | 12 / 3.75 fail | 10 / 5.00 fail | fail | fail |
| persistence-logistic | 12 / 3.25 fail | 7 / 3.42 fail | fail | fail |

**No latent-factor row passes the judge.** None clears tier 1's limit on false alarms under either rule, none passes tier 3, and
the only rows that pass tier 5 are the two logistic-link ones. Under readings (b) and (e) of the readings page, no latent-factor row passes
either (`evidence/latent-factor/compare.md`).

**Probability quality.** Brier score and log loss at +5 bp, pooled, h = 1 / h = 3 / h = 5:

| row | h = 1 | h = 3 | h = 5 |
|---|---|---|---|
| `latent_factor` | 0.0840 / 0.332 | 0.1091 / 0.402 | 0.1145 / 0.403 |
| `latent_factor_logit` | 0.0529 / 0.194 | 0.0617 / 0.228 | 0.0626 / 0.227 |
| `risk_gbm+latent_factor_logit` | 0.0465 / 0.183 | 0.0593 / 0.221 | 0.0623 / 0.231 |
| `ngboost_laplace` | 0.0462 / 0.168 | 0.0595 / 0.225 | 0.0637 / 0.267 |
| `risk_gbm` | 0.0577 / 0.660 | 0.0667 / 0.789 | 0.0696 / 0.804 |
| calendar climatology | 0.0714 / 0.296 | 0.0707 / 0.294 | 0.0709 / 0.296 |

The Gaussian rows are worse than climatology at every horizon, in 2020 (-0.091 [-0.101, -0.080] Brier difference to climatology at h = 1),
2021-23 and 2024. The logistic row is better than climatology in every regime at h = 1 (the interval includes 0 in 2018-19, 2024 and 2025-26) and trails `ngboost_laplace` at h = 1 by 0.007 [0.002, 0.012] Brier and is level with it from h = 2 (intervals that include 0). Against `risk_gbm`, Brier
difference (reference minus row; positive: the row is better), pooled: `latent_factor_logit` 0.005 [-0.005, 0.015] at h = 1 and 0.010
[0.001, 0.019] at h = 2; `risk_gbm+latent_factor_logit` 0.011 [0.002, 0.022] at h = 1 and 0.009 [0.001, 0.019] at h = 2. By regime
the gain over `risk_gbm` is in 2018-19; in 2020 the combined row is worse (-0.012 [-0.024, -0.004] at h = 1). All of it, with
`ngboost_laplace`, climatology and persistence as references and the split by regime and pressure-day type, is in
`evidence/latent-factor/compare.md`.

**Onset recall** (lead 1 or more, any horizon; weighted rule), pooled recall difference to `risk_gbm`, row minus reference, 90% interval:
`risk_gbm+latent_factor_logit` +0.115 [0.000, 0.250]; `latent_factor_logit` -0.038 [-0.250, 0.179]. Onsets warned by year:

| row | 2018 | 2019 | 2020 | 2024 | 2025 |
|---|---|---|---|---|---|
| `latent_factor` | 0 of 4 | 13 of 13 | 1 of 2 | 0 of 2 | 0 of 5 |
| `latent_factor_logit` | 0 of 4 | 11 of 13 | 1 of 2 | 0 of 2 | 0 of 5 |
| `risk_gbm+latent_factor_logit` | 0 of 4 | 11 of 13 | 1 of 2 | 0 of 2 | 3 of 5 |
| `risk_gbm` | 0 of 4 | 10 of 13 | 0 of 2 | 0 of 2 | 3 of 5 |
| `ngboost_laplace` | 0 of 4 | 12 of 13 | 0 of 2 | 0 of 2 | 5 of 5 |

2018, 2020 and 2024 are the years the model needs most, and it warns none of 2018 and 2024's onsets; its one 2020 hit is at the longest
lead. The Gaussian rows warn every 2019 onset only by flagging a large share of all days (the cut-off flags every day at roughly a tenth of their refits).
`latent_factor_logit` warns four onsets (2019-05-28, 2019-06-25, 2019-08-13, 2020-03-12) that none of the five risk-date passers warns.

**The factor** (`evidence/latent-factor/factor.md`, `factor.svg`). Persistence is low and moves: phi runs from 0.33 to 0.83 across refits
(median 0.52). The loadings are of one sign, stable across refits, for seven of the nine series (all the SOFR percentiles, TGCR, BGCR and
the dispersion). Two are not: **EFFR above IORB changes sign once and ON RRP take-up three times** across refits. The factor is
therefore driven by the SOFR/TGCR/BGCR complex, the segment the spread itself is made of, and the stability the directive asks for does
not hold for EFFR and ON RRP. The EM reached its iteration cap at one refit. At the last anchor before each onset the filtered
factor is near its average for most of 2019 and 2020 (standard deviation 1.64 across anchors); it is high before the end-2018 onsets and
modestly high before the 2025 ones, which is the pattern in `factor.svg`.

## Reading

The latent factor carries the information the percentile series carry, and no more than a recalibrated direct model on them: with a
calibrated link it matches `ngboost_laplace` on Brier and log loss, and under `risk_gbm` it improves the Brier score. It does not
improve the warning of onsets. Its daily factor has little memory, so a one-day-ahead factor forecast is nearly a draw from its stationary
law, and the spread's spikes, which are rare and one-sided, are not well described by a Gaussian factor. Nothing here is a verdict or
a request to publish; no `needs-eleonora` question is raised.

## Not checked

* The factor model passed through the calibration step of #539's hurdle (`ml.pressure_risk_date_hurdle_exceedance`), which merged
  after this was declared and scored. The combined rows here have the hurdle's structure but not its calibration.
* A second factor, a factor with the spread among its series, and an innovation variance that is not fixed; none was declared.
* The settlement and H.4.1 timing of #541 (it has not merged); the inputs are read as the information-set rules read them today.
* Any day after 2025-12-31.

## Reproduce

Published panel `4ddc3882…` (`verify-panel` clean), scratch panels as for #428 (`scripts/risk_date_severity.py`). `/opt/rmm-venv`
(numpy 2.4.6, scikit-learn 1.9.1), `OMP_NUM_THREADS=1`.

```
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --output OUT/bench_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/risk_date_severity.py run --panel AUG2.csv --published PUBLISHED.csv --horizon $h --output OUT/risk_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_track_q.py forecasts --panel PUBLISHED.csv --horizon $h --output OUT/q_h$h.json --distribution OUT/qdist_h$h.json
    (keep only the ngboost_laplace column of each q file as OUT/ngb_h$h.json)
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/latent_factor.py run --panel AUG2.csv --published PUBLISHED.csv --horizon $h --risk OUT/risk_h$h.json --output OUT/lf_h$h.json
for r in weighted unweighted: PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule $r --output OUT/judge_$r.json --markdown OUT/judge_$r.md OUT/bench_h?.json OUT/risk_h?.json OUT/ngb_h?.json OUT/lf_h?.json
for r in weighted unweighted: PYTHONPATH=src python3 scripts/pressure_judge.py table OUT/judge_$r.json --output OUT/tables_$r.md
PYTHONPATH=src python3 scripts/latent_factor.py compare --panel PUBLISHED.csv --bench 'OUT/bench_h{h}.json' --risk 'OUT/risk_h{h}.json' --reference 'OUT/ngb_h{h}.json' --rows 'OUT/lf_h{h}.json' --output OUT/compare.json --markdown OUT/compare.md
PYTHONPATH=src python3 scripts/latent_factor.py factor --compare-input 'OUT/lf_h{h}.json' --panel PUBLISHED.csv --output OUT/factor.json --markdown OUT/factor.md --svg OUT/factor.svg
```

Evidence: `docs/pivot/evidence/latent-factor/` (`compare.md` and `compare.json` the readings, years, degenerate refits, Brier and log loss
and the paired comparisons; `tables-*.md` and `judge-*.md` the judge's tables and full reports; `factor.md`, `factor.json`, `factor.svg`
the loadings by refit and the filtered factor against the onsets).
