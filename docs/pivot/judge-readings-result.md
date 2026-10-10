# Tier 1 under the readings the forensic audit questioned (#523)

A scratch measurement. Four findings of the forensic audit say the tier 1 pass of the risk-date models may depend on how
the judge counts: #509 (warnings counted across all horizons, false alarms at one), #512 (the cut-off rule checks false
alarms on re-applied old forecasts), #514 (the weighted rule discounts alarms after an episode as much as alarms before
it) and #510 (the pass rests on 2018-19). This page reports tier 1 for the five risk-date passers and the six best-recall
rows of #461 under each reading, under the flat and under the weighted rule. It changes nothing the judge decides:
`metadata/pressure_judge.json`, `metadata/weighted_miss.json` and every decision record are unchanged, nothing is
published, and no 2026 day is read ([`lockbox.md`](../decisions/lockbox.md)). Scored days 2018-06-29 to 2025-12-31, h = 1
to 5, +5 bp primary, 90% stationary-bootstrap intervals, the judge's seed. **Which reading is the right one is
Eleonora's choice; this page does not make it.**

The rows, readings and what is reported were declared before any score in
[`metadata/judge_readings.json`](../../metadata/judge_readings.json). Reading (a) is the judge's own and is checked
against `judge` (its onsets warned, recall and worst false alarms per onset match on all thirteen rows, under both rules;
the script stops otherwise). The full tables are in [`evidence/judge-readings/`](evidence/judge-readings/).

## The readings

* **(a) as declared.** An onset is warned if any horizon 1 to 5 flags it; false alarms are counted at each horizon and the
  worst horizon's count per onset is the tier's.
* **(b) same horizon.** (b1) each horizon alone: onsets warned and false alarms at that one horizon. (b2) pooled: onsets
  warned at any horizon, false alarms counted over the days flagged at any horizon (a day flagged at two horizons is one
  false alarm). The climatology reference is matched to the pooled count.
* **(c) the training-window check beside the realised count.** For each refit, the cut-off in force applied to the
  training window's earlier forecasts, counted as the cut-off rule counts it, against the false alarms actually raised
  in the walk-forward flags.
* **(d) the weighted rule's discount for alarms before an episode only.** A false alarm weighs by its distance to the
  *next* pressure day alone (the bands of `metadata/weighted_miss.json` unchanged), and an alarm with no later pressure
  day known weighs 1; the cut-offs are chosen on that count. This is one reading of "discount only alarms before an
  episode"; the audit's third column uses the same distance. Weighted rule only.
* **(e) outside 2018-19.** The cut-offs of (a), scored on the days of the other calendar years (and, beside it, on 2018-19
  alone); the tier's three criteria applied to that subset, reported and not a tier. Where a subset has too few draws
  for the bootstrap, its interval is shown as `–` and the criterion that needs it fails.

## Result

Onsets warned (of 26) / false alarms per onset, as the rule counts them, and the verdict. The five passers, the best
weighted-rule row beside them (`ngboost_laplace`) and the best-recall row that stays a failure (`two_part_gbm`); all
thirteen rows are in the evidence.

**Flat rule** (cut-offs and limit on the flat count):

| row | (a) as declared | (b1) best single horizon | (b2) pooled | (e) outside 2018-19 |
|---|---|---|---|---|
| risk_gbm | 13 / 1.35 pass | 13 / 1.35 pass | 13 / 2.00 pass | 3 / 1.56 fail |
| risk_gbm_base | 14 / 1.50 pass | 13 / 1.50 pass | 14 / 2.04 fail | 4 / 2.00 fail |
| risk_logistic | 14 / 1.85 pass | 13 / 1.85 pass | 14 / 2.42 fail | 4 / 2.89 fail |
| risk_logistic_base | 13 / 1.77 pass | 13 / 1.77 pass | 13 / 2.04 fail | 3 / 2.33 fail |
| risk_quantile_skewt_base | 14 / 1.88 pass | 13 / 1.88 pass | 14 / 2.54 fail | 4 / 3.22 fail |
| ngboost_laplace | 15 / 2.54 fail | 10 / 1.69 fail | 15 / 4.38 fail | 4 / 0.33 fail |
| two_part_gbm | 15 / 2.46 fail | 9 / 0.23 fail | 15 / 4.12 fail | 3 / 0.44 fail |

**Weighted rule in force** (cut-offs and limit on the weighted count):

| row | (a) as declared | (b1) best single horizon | (b2) pooled | (d) before-episode discount | (e) outside 2018-19 |
|---|---|---|---|---|---|
| risk_gbm | 13 / 0.80 pass | 13 / 0.80 pass | 13 / 1.48 pass | 13 / 0.95 pass | 3 / 1.61 fail |
| risk_gbm_base | 14 / 0.97 pass | 14 / 0.97 pass | 14 / 1.59 pass | 14 / 1.08 pass | 4 / 2.06 fail |
| risk_logistic | 16 / 1.74 pass | 14 / 1.74 pass | 16 / 2.55 fail | 16 / 1.90 pass | 6 / 4.39 fail |
| risk_logistic_base | 15 / 1.65 pass | 14 / 1.65 pass | 15 / 2.18 fail | 14 / 1.78 pass | 5 / 3.67 fail |
| risk_quantile_skewt_base | 15 / 1.62 pass | 15 / 1.62 pass | 15 / 2.14 fail | 15 / 1.81 pass | 5 / 3.81 fail |
| ngboost_laplace | 17 / 1.73 pass | 15 / 1.41 pass | 17 / 2.34 fail | 16 / 2.23 fail | 5 / 0.50 fail |
| two_part_gbm | 15 / 2.55 fail | 12 / 1.74 fail | 15 / 3.74 fail | 15 / 2.22 fail | 3 / 2.89 fail |

What each reading does to the passers:

* **(b) Same horizon (#509).** Pooled, the flat false alarms per onset are 2.00 (`risk_gbm`, exactly the limit), 2.04,
  2.42, 2.04 and 2.54: one passer stays at the limit and four exceed it. Under the weighted rule the pooled count is 1.48
  and 1.59 for the two gbm rows (pass) and 2.55, 2.18 and 2.14 for the three logistic and skew-t rows (fail). Read at a
  single horizon, every passer passes at h = 1 alone (13 onsets at 1.35 to 1.88 flat false alarms per onset), and under
  the flat rule no later horizon alone warns more than 9 (`evidence/judge-readings/readings.md`, (b1)). `risk_gbm`
  pooled is exactly at the limit, so it passes on the rule's count `<= 2`.
* **(c) Training check against realised (#512).** For the passers the realised count (1.35 to 1.88 flat) is *below* the
  check at the last refit (1.92 to 2.00), so the mechanism does not inflate their tier 1 count. For the six best-recall
  rows the realised count (2.46 to 3.65 flat) is well above a check that is at most 2 at every refit (last refit 1.71 to
  2.00; the median check is 1.11 to 1.95): the rule's own check does not aim at the count tier 1 scores. This is the
  mechanism #512 describes, now measured on those rows. The verdict is the realised count's, as in (a).
* **(d) Discount before an episode only (#514).** The five passers still pass (0.95, 1.08, 1.90, 1.78, 1.81, all at most
  2). `ngboost_laplace`, which passes tier 1 under the weighted rule as declared (17 of 26, 1.73), fails here (2.23). The
  discount raises the passers' weighted count by 0.11 to 0.19 and `calendar_climatology`'s by 0.80 (3.75 to 4.55); it
  barely moves `persistence_logistic` (3.25 to 3.23).
* **(e) Outside 2018-19 (#510).** In 2018-19 all five pass (10 of 17 onsets warned, 0.46 to 0.71 weighted false alarms
  per onset). Outside it none of the thirteen rows meets tier 1: the passers warn 3 to 6 of 9 onsets, and their false
  alarms per onset are 1.56 to 3.22 flat, 1.61 to 4.39 weighted. The 2018-19 / outside split of onsets is 17 / 9.

### The scarcity state of the 2020 false-alarm days (#510)

Every false-alarm day of 2020 at the five passers falls in an as-of scarcity state of 1 or higher, none in state 0, which
is the only scarcity state tier 3 checks for false alarms (`metadata/pressure_judge.json`, `tiers.no_crying_wolf`, with
the 2021-23 regime). At the worst horizon the flat counts are
11, 15, 19, 17 and 24 (`risk_gbm`, `risk_gbm_base`, `risk_logistic`, `risk_logistic_base`, `risk_quantile_skewt_base`),
as the audit found; by state:

| row | worst horizon | false alarms there | state 1 | state 2 | state 3 | flagged at any horizon |
|---|---|---|---|---|---|---|
| risk_gbm | 2 | 11 | 5 | 1 | 5 | 21 |
| risk_gbm_base | 1 | 15 | 8 | 0 | 7 | 25 |
| risk_logistic | 4 | 19 | 10 | 2 | 7 | 25 |
| risk_logistic_base | 1 | 17 | 9 | 0 | 8 | 24 |
| risk_quantile_skewt_base | 1 | 24 | 17 | 0 | 7 | 36 |

(Flat rule; the weighted rule's counts are in the evidence.)

### The ceiling at lead of at least 2 (#511)

The judge's own onset-warning rows report lead of at least 1 and at least 3. At lead of at least 3 the passers warn 7 to
10 of 26 onsets under the flat rule (7, 7, 9, 8, 10). Their forecast is exactly 0 off the risk dates at h >= 2, so the
ceiling is the number of onsets with a forecast above 0 at some h >= 2: **13 of 26** for all five passers, as the audit's
rebuild found. They flag 8 to 10 of those 13 at h >= 2 (flat rule), all on a risk date. The other eight rows forecast above
0 on 25 or 26 onsets, and flag 7 to 13 onsets at h >= 2. (The grid's own risk-date label counts 20 of 26 onsets,
because it includes coupon settlement days, which the passers use at h = 1 only.)

## What this does and does not show

* The passers' tier 1 pass depends on the reading. Under the flat rule it holds as declared and at h = 1 alone, and
  survives pooling only for `risk_gbm`, at the limit. Under the weighted rule it holds as declared, at h = 1 alone and
  under the discount before an episode only; pooling takes away three of five. It does not hold outside 2018-19 under
  any reading.
* `ngboost_laplace` passes tier 1 as declared under the weighted rule in force, which neither the
  weighted-miss comparison (#463) nor the page that put the rule in force (#472) lists; it fails pooling and the
  before-episode discount. It does not pass the pass
  rule (tiers 3 and 5 are not scored here).
* The choice between the readings, and whether any of them changes the bar, is Eleonora's. Nothing here was run on a day
  of the 2026 tiers.

## Not checked

* Tiers 3 and 5, which this page does not re-run: only tier 1 is read, in the readings above.
* The six best-recall rows are the rows of #461 as declared there; the reading "best six" was not revisited.
* The climatology reference is matched, as the judge matches it, to the *flat* count of false alarms raised, in every
  reading; under (b2) it is matched to the pooled count with the h = 1 climatology.
* Reading (d) is one interpretation of "discount only alarms before an episode". Its cut-offs are re-chosen on that count
  at each refit, with the pressure days known at the refit.
* Reading (e) uses the cut-offs chosen on the whole expanding window, as the judge does; it does not re-choose them
  for the subset. Intervals on nine onsets are wide and sometimes undefined.

## Reproduce

Published panel `4ddc3882…` (`REPRODUCIBILITY.md`), scratch panels as in
[`regime-thresholds-result.md`](regime-thresholds-result.md) and
[`risk-date-severity-result.md`](risk-date-severity-result.md). Set `OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1` and
`MKL_NUM_THREADS=1`. The forecasts are those two pages' commands, unchanged, at h = 1 to 5 (benchmarks with `--published`);
the scoring then takes about sixteen minutes.

```
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
for h in 1 2 3 4 5:
  PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUB.csv --horizon $h --published --output OUT/bench_h$h.json
  PYTHONPATH=src python3 scripts/risk_date_severity.py run --panel AUG2.csv --published PUB.csv --horizon $h --output OUT/risk_h$h.json
  PYTHONPATH=src python3 scripts/pressure_two_part.py horizon --panel PUB.csv --horizon $h --output OUT/tp_h$h.json
  PYTHONPATH=src python3 scripts/pressure_track_q.py forecasts --panel PUB.csv --horizon $h --output OUT/q_h$h.json --distribution OUT/qdist_h$h.json
  PYTHONPATH=src python3 scripts/hierarchical_logistic.py forecasts --panel AUG.csv --horizon $h --output OUT/hl_h$h.json
  PYTHONPATH=src python3 scripts/settlement_timing.py run --panel AUG2.csv --published PUB.csv --candidate settlement_quantile_timing --horizon $h --output OUT/sqt_h$h.json
  PYTHONPATH=src python3 scripts/scarcity_event_bar.py forecasts --panel AUG.csv --horizon $h --candidate scarcity_logistic_interactions --output OUT/sli_h$h.json
  PYTHONPATH=src python3 scripts/scarcity_event_bar.py forecasts --panel AUG.csv --horizon $h --candidate scarcity_logistic --output OUT/sl_h$h.json
PYTHONPATH=src python3 scripts/judge_readings.py score --panel PUB.csv --bench 'OUT/bench_h{h}.json' --risk 'OUT/risk_h{h}.json' \
    --row two_part_gbm='OUT/tp_h{h}.json' --row ngboost_laplace='OUT/q_h{h}.json' --row hierarchical_logistic='OUT/hl_h{h}.json' \
    --row settlement_quantile_timing='OUT/sqt_h{h}.json' --row scarcity_logistic_interactions='OUT/sli_h{h}.json' \
    --row scarcity_logistic='OUT/sl_h{h}.json' --output OUT/readings.json --markdown OUT/readings.md
```
