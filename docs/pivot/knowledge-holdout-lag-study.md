# Knowledge holdout and H.4.1 lag: two reported-only studies (#280)

Eleonora's ruling on #269, items 8 and 18. **Both studies decide nothing.** The live model keeps the
five-day H.4.1 lag, no published record is edited, and no headline moves. The data is
[`studies/knowledge_holdout_lag_study.json`](studies/knowledge_holdout_lag_study.json), written by
`scripts/knowledge_holdout_lag_study.py` (command below). No scored day is in a locked tier: the
knowledge-holdout windows are 2019-09-16 to 2019-09-20 and 2020-03-09 to 2020-03-20, and the lag study
scores through 2025-12-31 (`lockbox.require_unlocked` checks both).

```
PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output /tmp/funding_panel.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
PYTHONPATH=src /opt/rmm-venv/bin/python scripts/knowledge_holdout_lag_study.py --panel /tmp/funding_panel.csv --journal /tmp/kh/journal.jsonl --output /tmp/study.json
```

The panel is the published one (digest `4ddc3882…`). The lag pricing refits a gradient-boosted model on three
rolling grids and takes hours on a small machine; `--skip-lag-pricing` runs the knowledge holdout alone in seconds.

## 1. Knowledge holdout (item 18)

**Uncalibrated.** The models are the uncalibrated gbm on the two published feature sets (four features, as in
`exceedance_gbm.json`; nine, as in the funding declaration the calibrated model reads) and the three benchmarks
(climatology, calendar-type climatology, persistence-logistic). **No published (calibrated) model is held out from
these windows:** the published records train on every crisis day once it is in the past, and their calibration is
fitted on that history. Every table below is labelled uncalibrated for that reason, and none of it says anything about
the published calibrated model.

Each window is scored once per model, with the crisis stripped from training and the as-of rule on every read
(`event_eval.evaluate_event_window`). The 15 scored days are the two windows together. The contract's rule that a
single window gets no aggregate number holds for each window alone; this is the pooled evaluation `event_eval`'s
docstring says such a metric belongs to, reported separately and never averaged into a main table.

Paired difference is benchmark Brier minus model Brier, so positive favours the model, with a 90% stationary-bootstrap
interval (mean block length 2, 2000 replications). Pooled over the 15 days:

| Uncalibrated model vs benchmark | 5 bp | 10 bp | 20 bp | 50 bp |
|---|---|---|---|---|
| gbm, four features, vs climatology | +0.127 (−0.036 to +0.309) | +0.073 (−0.039 to +0.203) | +0.018 (−0.014 to +0.060) | +0.000 (−0.002 to +0.003) |
| gbm, four features, vs persistence-logistic | +0.041 (−0.044 to +0.136) | +0.017 (−0.017 to +0.053) | +0.075 (−0.006 to +0.191) | +0.062 (−0.002 to +0.184) |
| gbm, four features, vs calendar climatology | +0.091 (−0.053 to +0.235) | +0.067 (−0.039 to +0.189) | +0.027 (−0.011 to +0.074) | +0.001 (−0.002 to +0.006) |
| gbm, nine features, vs climatology | +0.133 (−0.035 to +0.312) | +0.063 (−0.039 to +0.184) | +0.020 (−0.005 to +0.054) | +0.000 (−0.002 to +0.003) |
| gbm, nine features, vs persistence-logistic | +0.046 (−0.028 to +0.127) | +0.007 (−0.037 to +0.050) | +0.078 (+0.002 to +0.199) | +0.062 (−0.002 to +0.185) |
| gbm, nine features, vs calendar climatology | +0.097 (−0.048 to +0.249) | +0.057 (−0.036 to +0.171) | +0.029 (−0.003 to +0.070) | +0.001 (−0.002 to +0.006) |
| persistence-logistic vs climatology | +0.086 (−0.101 to +0.273) | +0.056 (−0.048 to +0.189) | −0.058 (−0.174 to +0.014) | −0.062 (−0.185 to +0.000) |
| calendar climatology vs climatology | +0.036 (−0.009 to +0.089) | +0.006 (−0.010 to +0.023) | −0.009 (−0.018 to −0.002) | −0.001 (−0.002 to +0.000) |

The control holds: climatology against itself is exactly zero at every threshold. Days above each threshold in the 15:
8 at 5 bp, 6 at 10 bp, 4 at 20 bp, 1 at 50 bp.

**What it shows.** Every interval but one includes zero: the uncalibrated gbm's point estimates favour it over all
three benchmarks, and the one interval that excludes zero is the nine-feature gbm against persistence-logistic at
20 bp (+0.078, +0.002 to +0.199), an edge of its lower end. With 15 days from two episodes this cannot separate
the gbm from the benchmarks, and a 50 bp cell has one positive day. It is an extrapolation check, not evidence of skill.

**Splits.** By regime the windows are separate cells: 2018-19 is the five September 2019 days, 2020 the ten March 2020
days; the other regimes have no day. By pressure-day type the 15 days are 12 ordinary and 3 tax-date days; month-end
and quarter-end have none. No cell reaches a day count at which an interval means much. Where the split helper could
not bootstrap a cell it says so rather than discard replicates (`interval_unavailable`): that is the 2018-19 cell
(5 days) and the tax-date cell (3 days) at the thresholds read, and their means are reported without an interval. In
2020 the gbm trails climatology at 5 bp (−0.069, interval −0.141 to +0.010, four features) and at 10 bp (−0.039,
−0.076 to −0.002, nine features); in 2018-19 it leads by a wide margin at both. Those two cells decide the pooled sign
and cannot be pooled into one conclusion. Full splits at every threshold, and every day's curve beside the realized
spread, are in the JSON.

## 2. H.4.1 lag (item 8)

**What the five days rests on.** One measured case: the week ending 2020-12-23, first carried by the 2020-12-28
vintage (`metadata/sources.json`, `WRESBAL`, `WLRRAOL`, `WTREGEN` notes). **That case spans Christmas**, so it is a
holiday-shifted release, not a typical one.

**Further cases the tracked vintages allow.** First print of each Wednesday, from adjacent daily vintages under
`tests/fixtures/snapshots/alfred-h41-first-print/` (the same dates for `WRESBAL` and `WLRRAOL`):

| Week ending (Wednesday) | Vintage before | First vintage carrying it | Lag, calendar days | Why |
|---|---|---|---|---|
| 2020-12-23 | 2020-12-27 | 2020-12-28 | 5 | Christmas |
| 2025-11-26 | 2025-11-27 | 2025-11-28 | 2 | Thanksgiving |
| 2026-09-09 | 2026-09-09 | 2026-09-10 | 1 | ordinary Thursday release |

So the tracked evidence is three weeks, not one, and the lag is 1 on an ordinary week and 2 to 5 where a holiday
shifts the release. Other adjacent vintages are not in the tree; more cases would need further ALFRED fetches, which
this study did not make.

**Pricing a shorter lag against the declared five.** The published nine-feature funding declaration, uncalibrated gbm
(the calibrated model refits a 45-point grid and would multiply the run time), scored on the same rolling
grid, refit every 21 days, under a copy of the registry whose `WRESBAL` and `WTREGEN` carry the shorter lag. The
registry file is not edited. The shorter lag does move what the model reads: the row used for a scored day is 2 or 3
panel days back, against 4 to 6. Paired Brier difference, 5-day minus shorter-lag, with a 90% stationary-bootstrap
interval, so **positive favours the shorter lag**:

| Shorter lag | 5 bp | 10 bp | 20 bp | 50 bp |
|---|---|---|---|---|
| 1 day | −0.0003 (−0.0015 to +0.0009) | −0.0010 (−0.0018 to −0.0002) | +0.0002 (−0.0000 to +0.0005) | −0.0000 (−0.0000 to +0.0000) |
| 2 days | +0.0000 (−0.0009 to +0.0010) | −0.0007 (−0.0014 to −0.0001) | +0.0001 (−0.0001 to +0.0004) | −0.0000 (−0.0000 to +0.0000) |

At 10 bp, the one threshold with an interval clear of zero, the shorter lag is **worse**, by about 3% of the 10 bp Brier
score of 0.029. By regime that is almost all 2018-19 (−0.0049 at 1 day, −0.0037 at 2 days, both intervals below zero);
2021-23 is zero to four decimals at every threshold. By day type the 10 bp loss is on ordinary days (−0.0008 at 1 day,
interval −0.0016 to −0.0002) and tax dates (−0.0076, interval including zero). A lag that prices out as no better is
not a case for changing the live record: a shorter lag would be a new model version, so the live record keeps 5.

**Reading it.** This is a measurement of what would have been read, scored on one model and one grid. It does not say a
shorter lag is unsafe: the 1-day lag is the Board's ordinary schedule, and the tracked vintages show 2 and 5 days when a
holiday intervenes, so a 1-day declaration would sometimes read a value that was not yet published. The scoring above
does not model that; it is a reason the comparison flatters the shorter lag, and it still does not favour it.

## Not checked

- The calibrated published model was not priced for the lag, and was not held out from the windows (item 18 asks for
  the uncalibrated one, and says so).
- The study scores one decision time (16:00) and one model for the lag; other models that read the H.4.1 are not run.
- Further first-print cases need vintages that are not in the tree.
- Eleonora decides whether any of this is cited on a published page. Nothing here is.
