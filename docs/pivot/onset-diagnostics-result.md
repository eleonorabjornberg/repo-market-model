# Where the onset bar's false alarms fall, and what 26 onsets can prove (#429)

Two reported-only diagnostics on the onset tier of the pressure-day judge (#375, as amended under #407). They change
no bar, no declaration, no record and no published figure, and they write nothing into `docs/runs/`
(`docs/decisions/lockbox.md`: scored days 2018-06-29 to 2025-12-31 only; no day of the 2026 window is read). The
rows, the buckets and the power settings are in `metadata/onset_diagnostics.json`, committed before anything was
computed; `scripts/onset_diagnostics.py` refuses an uncommitted declaration. The one choice the declaration got wrong
before any score (the fifth row, see below) was corrected in a commit before the script was run.

## What was declared

* **The five best rows of Table 1 of the re-judge** (`docs/pivot/judge-amendment-result.md`). "Best" is not defined by the
  directive; it is read as the most onsets flagged at lead of at least 1, ties broken by the smaller worst false alarms per
  onset and then by name, over the candidate rows (the three reference rows are left out). A test
  (`tests/test_onset_diagnostics.py`) re-derives the five from Table 1: `two_part_gbm`, `ngboost_laplace`,
  `hierarchical_logistic`, `settlement_quantile_timing` (all with 15 of 26 onsets flagged) and
  `scarcity_logistic_interactions` (14 of 26).
* **Flags** are the judge's own: a probability at or above the cut-off chosen refit by refit from the training window
  (`pressure_judge.choose_cutoffs`), at +5 bp, at each horizon h = 1 to 5. A **false alarm** is a flag on a day that is
  not a pressure day, on the days every horizon scores, as tier 1 counts them; the day is the flagged (target) day t + h.
  The script's counts reproduce Table 1 for every row (onsets flagged, and the worst false alarms per onset), so the
  splits below sum to the figures Table 1 reports.
* **Three splits**, as the directive lists: the flagged day's realised spread on whole basis points (+4 to +5, +1 to +3, 0 or
  below), its distance in panel days to the nearest pressure day (1, 2 to 5, 6 to 20, 21 or more), and its day type. The regime
  split is reported beside them. The distance is read on the days to 2025-12-31 only (`nearest_pressure_distance` raises
  `LookAheadError` otherwise).
* **Power.** How often a model whose true onset recall is 55%, 60%, 70% or 80% meets tier 1's recall conditions as the judge
  applies them (point recall at least 0.5; the lower end of the 90% stationary-bootstrap interval above the climatology
  recall), for the development window's 26 onsets at their real positions, and for the confirmation window with 1 to 5 onsets.
  500 experiments per cell; each onset is flagged independently with the true recall; the climatology recall is a constant, taken
  as the lowest (0.115), a typical (0.231) and the highest (0.269) of Table 1. The false-alarm limit is not simulated.
  The confirmation window is a parameter, not a count: 169 days, of which the lockbox record gives 5 above +5 bp, so at most 5
  onsets.

## Reproduce

Published panel `4ddc3882…` (rebuilt from the tracked fixtures, `verify-panel` clean); scratch panels from
`pressure_v1_1.py panel` (`AUG.csv`, digest `4137d0ad…`) and `measurement_fields.py panel` (`AUG2.csv`). Run with
`OMP_NUM_THREADS=1`. Each row's forecasts come from its own script, unchanged, at h = 1 to 5. Two of the five rows are on
open track pull requests, so their scripts are read at those heads: `pressure_two_part.py` at #404's head `7d5169a`
and `pressure_track_q.py` at #413's head `d8b9c41` (both on the published panel).

```
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
for h in 1 2 3 4 5:
  PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUB.csv --horizon $h --output OUT/bench_h$h.json
  PYTHONPATH=src python3 scripts/hierarchical_logistic.py forecasts --panel AUG.csv --horizon $h --output OUT/hl_h$h.json
  PYTHONPATH=src python3 scripts/settlement_timing.py run --panel AUG2.csv --published PUB.csv --candidate settlement_quantile_timing --horizon $h --output OUT/sqt_h$h.json
  PYTHONPATH=src python3 scripts/scarcity_event_bar.py forecasts --panel AUG.csv --horizon $h --candidate scarcity_logistic_interactions --output OUT/sli_h$h.json
  (at #404's head) PYTHONPATH=src python3 scripts/pressure_two_part.py horizon --panel PUB.csv --horizon $h --output OUT/tp_h$h.json
  (at #413's head) PYTHONPATH=src python3 scripts/pressure_track_q.py forecasts --panel PUB.csv --horizon $h --output OUT/q_h$h.json --distribution OUT/qdist_h$h.json
PYTHONPATH=src python3 scripts/onset_diagnostics.py false-alarms --panel PUB.csv --bench 'OUT/bench_h{h}.json' \
    --row two_part_gbm='OUT/tp_h{h}.json' --row ngboost_laplace='OUT/q_h{h}.json' --row hierarchical_logistic='OUT/hl_h{h}.json' \
    --row settlement_quantile_timing='OUT/sqt_h{h}.json' --row scarcity_logistic_interactions='OUT/sli_h{h}.json' \
    --output OUT/false_alarms.json --markdown OUT/false_alarms.md
PYTHONPATH=src python3 scripts/onset_diagnostics.py power --panel PUB.csv --bench 'OUT/bench_h{h}.json' --output OUT/power.json --markdown OUT/power.md
```

The scripts are run with `/opt/rmm-venv/bin/python`. A forecast file scored on a scratch panel carries that panel's digest; the script
accepts it when its days are the benchmark's and records the digest (`forecast_panels` in `false_alarms.json`), as the re-judge
did. The evidence is in `docs/pivot/evidence/onset-diagnostics/`.

## Result 1: the false alarms sit beside the pressure days

All five rows keep the judge's flags; none is re-tuned. Table 1 of the re-judge counts false alarms at the worst horizon; the
splits pool the five horizons (Table A gives each horizon). The full tables, with the base of non-pressure days a flag could
fall on, are in `docs/pivot/evidence/onset-diagnostics/false_alarms.md`; the headline figures are:

* **Most false alarms are within five panel days of a pressure day.** 81% to 95% of each row's false alarms (90%, 92%, 95%, 81%,
  94% for the rows in the order above), against 15% of all non-pressure days. About a third are on the day next to one (33% to
  39%). Days 21 or more panel days from any pressure day, 76% of the days a flag could fall on, hold 0% to 2% of the false alarms
  for four rows and 14% for `settlement_quantile_timing` (61 flags).
* **Many are near-misses on the spread.** Non-pressure days with a realised spread of +4 to +5 bp are 4% of the days a flag could
  fall on and hold 27% to 40% of the false alarms; days at +1 to +3 bp are 7% and hold 28% to 42%. Flagged days with a spread
  of at least +1 bp are 55%, 70%, 80%, 64% and 82% of each row's false alarms (same order); the remaining 18% to 44% fall on days at
  0 bp or below. `two_part_gbm` is the row with the most false alarms on quiet days (44%) and the fewest overall.
* **Day type does not explain them.** Ordinary days hold 77% to 91% of the false alarms against 87% of the days; month-ends, tax
  dates and quarter-ends are small. The exception is `settlement_quantile_timing` on quarter-ends (12% against 1%).
* **Regime.** 60% to 99% of the false alarms are in 2018-19, which holds 16% of the non-pressure days and most of the pressure
  days (102 of the 140 in Table 2 of the re-judge). 2021-23 (no pressure day) holds none of them for four rows and 6% for
  `settlement_quantile_timing`.
* **Per horizon**, the worst horizon is h = 5 for `two_part_gbm`, `hierarchical_logistic`, `settlement_quantile_timing` and
  `scarcity_logistic_interactions`, and h = 4 for `ngboost_laplace`; `two_part_gbm` raises 6 at h = 1.

## Result 2: what 26 onsets can prove

The full tables are `docs/pivot/evidence/onset-diagnostics/power.md`. The development window, with 26 onsets over 1,869 days:

| true recall | point recall at least 0.5 (exact) | (simulated) | interval unavailable | lower end above climatology recall 0.115 / 0.231 / 0.269 | both conditions, any of those three |
|---|---|---|---|---|---|
| 0.55 | 0.762 | 0.774 | 0.000 | 0.996 / 0.930 / 0.878 | 0.774 |
| 0.60 | 0.892 | 0.902 | 0.000 | 1.000 / 0.986 / 0.960 | 0.902 |
| 0.70 | 0.991 | 0.994 | 0.000 | 1.000 / 1.000 / 1.000 | 0.994 |
| 0.80 | 1.000 | 1.000 | 0.000 | 1.000 / 1.000 / 1.000 | 1.000 |

* With 26 onsets the recall conditions are not the hard part. A model that flags 55% of onsets passes them about three times in
  four, 60% nine times in ten, 70% almost always. The point condition (at least 13 of 26) is the binding one; once it holds the
  interval's lower end clears every climatology recall in Table 1 in nearly every experiment. A model near 50% true recall is a
  coin toss on the point condition alone. What fails the models in the re-judge is the false-alarm limit and tiers 3 and 5, not the
  number of onsets.
* **The confirmation window cannot meet the recall condition under the judge's rule.** The bootstrap never drops a replicate, and
  a resample of 169 days with 1 to 4 onsets draws no onset in at least one of 2,000 replications almost every time, so the
  interval is unavailable in 99.8% to 100% of experiments and the condition is not met: 0% of experiments pass at any true
  recall (at most 0.2%, at 4 onsets). With 5 onsets (every pressure day its own onset, the most the lockbox record allows) the interval is
  unavailable in 65% to 71% of experiments and the recall conditions are met in 8% to 33% of them (8% at a true recall of 55%
  and climatology recall 0.269, 33% at 80% and 0.115). The point condition alone, at 1 to 5 onsets, is met in 56% to 97% of experiments; it is the interval that cannot be
  formed. The honest reading of a 2026 look under the declared interval rule is a count and a
  point recall, not a pass.
* Caveats: onsets are flagged independently in the simulation, but real flags cluster by regime (most pressure days are in
  2018-19), which makes the real figure less favourable than the table; the climatology recall is a constant; the
  confirmation onsets are evenly spaced, and placement matters little for the undefined-replicate result.

## Not checked, and for Eleonora

* **Which five rows.** The directive says "the five best rows" without a measure. The measure here is onsets flagged, ties by
  fewer worst false alarms per onset. Ranked by fewest false alarms instead, the five would be different rows; say if that is wanted.
* **Whether the confirmation look can be run as declared.** The never-drop rule makes tier 1's recall condition unmeetable in a
  window with at most 5 onsets (Result 2). Changing the rule, or reading the 2026 look without an interval, is a change to the
  bar and is hers; this page changes nothing. It is raised as a finding.
* **What counts as a false alarm.** The bar is unchanged: a flag next to an episode is a false alarm here, as in Table 1. The
  directive's remedies on near-misses are separate directives.
* Not checked: the +10 bp threshold; the dependence of true flags across onsets in the power simulation; any day of the 2026 window.
