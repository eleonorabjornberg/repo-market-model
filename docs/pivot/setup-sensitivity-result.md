# How much four features of the evaluation setup shape the results (#482)

Four sensitivity readings on the pressure-day judge (#375, as amended under #407): 2018-19 dominance, the cut-off refit
cadence, the week-ahead combiner, and the regimes tier 3 checks. They change no rule, no declaration, no record and no
published figure, and they write nothing into `docs/runs/`. Scored days are 2018-06-29 to 2025-12-31 only; no day of the
2026 window is read (`docs/decisions/lockbox.md`). The rows, the down-weighting rule, the cadences and the combiners are in
`metadata/setup_sensitivity.json`, committed before anything was computed; `scripts/setup_sensitivity.py` refuses an
uncommitted declaration. The arithmetic is `src/repo_model/setup_sensitivity.py`. The full tables are in
`docs/pivot/evidence/setup-sensitivity/setup_sensitivity.md` (data: `setup_sensitivity.json`); the figures below are
read from them.

**The declared reading is reproduced first.** Under the unchanged judge, the five rows flag 15, 15, 15, 15 and 14 of the 26
onsets and have worst false alarms per onset of 2.46, 2.54, 3.65, 3.65 and 3.23, as Table 1 of
`docs/pivot/judge-amendment-result.md` has them; the two benchmarks match too. **The "five tier-1 passers" of the directive
are the five rows with the most onsets flagged. None passes tier 1 as declared**: all five meet the recall condition and
fail the false-alarm limit of 2 per onset, and none passes tier 3 either (see item 4). Only `settlement_quantile_timing`
passes tier 5.

> *Note, 10 October 2026 (#503).* The "five tier-1 passers of the directive" here are the five best-recall rows of the judge's declared
> candidates (`two_part_gbm`, `ngboost_laplace`, `hierarchical_logistic`, `settlement_quantile_timing`,
> `scarcity_logistic_interactions`), not the five risk-date severity models that pass tier 1 on the other diagnostic pages
> (`risk_gbm`, `risk_gbm_base`, `risk_logistic`, `risk_logistic_base`, `risk_quantile_skewt_base`). See `docs/pivot/diagnostics-reconciliation.md`, point 6.

## 1. 2018-19 dominance

* **The concentration.** 2018-19 holds 102 of the 140 scored pressure days and 17 of the 26 onsets (by calendar year of the
  flagged day: 2018: 4, 2019: 13, 2020: 2, 2024: 2, 2025: 5, none in 2021-23). Almost all of each row's false alarms fall in
  2019 as well (Table 2a of the evidence).
* **Down-weighting changes almost nothing.** With 2018-19 days weighted so that, in each refit's training window, they
  carry their share of all days (20.0%), the cut-offs move a little in some blocks and tier 1 is unchanged for every row:
  15, 15, 15, 15 and 14 onsets flagged, and worst false alarms per onset of 2.42, 2.54, 3.69, 3.65 and 3.23 (declared:
  2.46, 2.54, 3.65, 3.65, 3.23). Tier 3 by year (Tables 3a and 3b) is unchanged for the four rows other than `settlement_quantile_timing`, whose 2020 rate falls
  from 23 to 11 flags per 252 days. The reason is in
  the data: until 2020 every training window is nearly all 2018-19, so there is little to rebalance towards, and the
  rows' flags already fall almost wholly where the pressure is. This is a reading of the cut-off choice only; the rows'
  probabilities are not refitted (see "Not checked"). Weighting the period to its share of *all* days leaves the pooled
  calibration over the whole window unchanged by construction (the weights are 1); outside 2018-19 the rows over-predict
  (realised minus predicted of -0.02 to -0.03 for four rows at h = 1, +0.01 for two) and inside it they under-predict
  (+0.01 to +0.08), so 2018-19 and the rest of the window pull the pooled figure in opposite directions (Table 4).
* **By year.** Tier 1 is carried by 2019: 11 to 13 of its 13 onsets are flagged by each of the five rows. In 2018 the
  rows flag none or one of four (the first training window has no onset), in 2020 at most one of two, in 2024 none of two,
  in 2025 one to four of five (Table 2a). Tier 3's alarm rate is high only in 2019 (89 to 153 flags per 252 days, over
  the 21 limit, but 2019 is in scarcity state 3, which the tier 3 calibration check does not cover) and, in 2025, for `hierarchical_logistic`,
  `scarcity_logistic_interactions` (26 each) and `settlement_quantile_timing` (29), where scarcity states 2 and 3 hold 27% of days.
* **2024 behaves differently from 2018-19** (Table 5; its "scored days" are the days every horizon scores, its pressure shares are over the h = 1 days). 2018-19 is 99% scarcity state 3, with 102 pressure days (27% of
  scored days) in 32 episodes up to 12 days long, a spread whose 90th percentile is +11 bp and whose maximum is +315 bp.

  *Note, 10 October 2026 (#503).* "Episodes" in Table 5 are maximal runs of consecutive pressure days (the one-calm-day episode) on the
  h = 1 grid; the 17 onsets are the five-calm-day episodes on the shared grid. Over the whole window the runs are 47 on the h = 1 grid and
  46 on the shared grid (`setup-diagnostic-result.md` §3). The 375 days of 2018-19 in Table 10 are the h = 1 grid, the 371 of Table 5 the
  shared grid. See `docs/pivot/diagnostics-reconciliation.md`, points 2 and 8.
  2024 is 100% scarcity state 0 (reserve balances about 3.3 trillion dollars, as in 2021-23, against 1.6 trillion in
  2018-19), with 5 pressure days (2%) in 3 episodes of at most 2 days, a maximum of +15 bp and a 90th percentile of -4 bp.
  The inputs that moved most against 2018-19 are SOFR volume (median 2.0 trillion against 1.0 trillion), the dealer
  Treasury position (300 against 225 billion), the 13-week bill rate (5.4% against 2.2%) and reserves (3.3 against 1.6
  trillion). No row flags either of the 2 onsets of 2024 at any horizon, and the
  rows' false alarms in 2024 are 0 to 2 at one horizon. 2025 resembles 2018-19 more than 2024: 29 pressure days in 9 episodes of up to
  11 days, with 27% of days in scarcity states 2 and 3; there the rows flag between 1 and 4 of 5 onsets.

## 2. Refit cadence

The flag cut-off refitted every 10 or every 5 scored days instead of 21; the rows' probabilities, which their own scripts
refit every 21 scored days, are unchanged. Onsets flagged of 26 and worst false alarms per onset (Table 6):

| row | every 21 | every 10 | every 5 |
|---|---|---|---|
| two_part_gbm | 15 (2.46) | 13 (1.65) | 13 (1.65) |
| ngboost_laplace | 15 (2.54) | 15 (2.35) | 14 (2.19) |
| hierarchical_logistic | 15 (3.65) | 15 (3.42) | 15 (3.46) |
| settlement_quantile_timing | 15 (3.65) | 15 (3.62) | 15 (3.42) |
| scarcity_logistic_interactions | 14 (3.23) | 13 (3.31) | 13 (3.27) |

* Tier 1 by year is in Table 7. No row changes verdict: all five still exceed 2 false alarms per onset. `two_part_gbm`
  gets to 1.65 at a cost of two onsets (a recall of 13 of 26, exactly the 0.5 that tier 1 asks for, so a cadence of 5 or 10 would
  pass its false-alarm limit and just meet its recall condition; whether the interval's lower end clears the climatology
  recall is not read here).
* **The onsets whose warning changes** (Table 8) are few: `two_part_gbm` loses 2019-01-15 and 2019-02-28 at both cadences;
  `ngboost_laplace` loses 2019-02-28 at both and gains 2018-12-17 at 10; `scarcity_logistic_interactions` loses 2019-01-15
  at both; `hierarchical_logistic` and `settlement_quantile_timing` change none. All are 2018-19 onsets.

## 3. The week-ahead combiner

Tier 5 at +5 bp with the five horizons' probabilities combined by the maximum (declared) and by independence (Table 9):

| row | max: realised - predicted | max: tier 5 | independence: realised - predicted | independence: tier 5 |
|---|---|---|---|---|
| two_part_gbm | +0.043 [+0.012, +0.075] | fail | +0.000 [-0.031, +0.033] | pass |
| ngboost_laplace | +0.065 [+0.035, +0.100] | fail | +0.003 [-0.027, +0.036] | pass |
| hierarchical_logistic | +0.047 [+0.014, +0.083] | fail | -0.085 [-0.123, -0.047] | fail |
| settlement_quantile_timing | +0.014 [-0.018, +0.048] | pass | -0.088 [-0.117, -0.059] | fail |
| scarcity_logistic_interactions | +0.047 [+0.014, +0.084] | fail | -0.093 [-0.131, -0.053] | fail |
| calendar_climatology | -0.047 [-0.102, +0.012] | fail | -0.381 [-0.446, -0.306] | fail |
| persistence_logistic | +0.001 [-0.053, +0.060] | fail | -0.270 [-0.340, -0.195] | fail |

(The realised week-ahead frequency is 0.152. All five rows beat calendar climatology's Brier score under both combiners;
`persistence_logistic` does not.) **The combiner decides tier 5 for three of the five rows.** `two_part_gbm` and
`ngboost_laplace` pass under independence and fail under the maximum; `settlement_quantile_timing` is the reverse; the other two fail
under both. The benchmarks are the reason the combiner was changed: under independence calendar climatology predicts
0.87 for a window with a realised frequency of 0.15 (its daily probabilities are not independent), which makes the benchmark row
uninformative. The change after the benchmark rows' calibration was seen (the declaration's status note) thus decides which
rows pass tier 5.

## 4. Tier 3 coverage

Table 10 gives realised minus predicted frequency in every regime at h = 1 to 5, with a star where the 90% interval misses
zero (intervals in the JSON). The regimes with a pressure day, which the amended tier 3 checks, are 2018-19 (102 pressure
days), 2020 (4), 2024 (5) and 2025-26 (29); 2021-23 has none.

* **No row fails the alarm-rate limit**: in scarcity state 0 and in 2021-23 the highest rate of any row is about 2 flags per 252
  days (`settlement_quantile_timing`), against a limit of 21 (Table 3a shows the per-year rates). Tier 3 fails on calibration.
* **The failures concentrate in 2020**, which has four pressure days in 251: all five rows' intervals miss zero there at
  four or five leads (the rows over-predict, by 0.007 to 0.16 at h = 1 to 5). Two rows, `two_part_gbm` and `ngboost_laplace`, also miss zero
  in 2025-26 (they under-predict by 0.05 to 0.10 at every lead); `settlement_quantile_timing` also misses in 2018-19 at every
  lead (+0.08 to +0.12). `hierarchical_logistic` and `scarcity_logistic_interactions` fail only in 2020. In 2024 (5 pressure
  days) no candidate row misses zero.
* **2021-23, with no pressure day, fails for every row and benchmark at all five leads.** Realised is exactly 0 there, the bootstrap
  interval has zero width, and any positive mean prediction (0.0001 to 0.02) misses zero. That is why the amendment tests
  only regimes with a pressure day; the reported-only column for the others cannot be anything but a miss.

## Findings that would need a rule decision (for Eleonora)

None is acted on here.

1. **Tier 1 is failed on false alarms by every row, not on recall.** All five rows meet the recall condition (point recall 0.54
   to 0.58); each fails the limit of 2 per onset (worst 2.46 to 3.65). Cutting the cut-off's refit to 10 or 5 scored days would
   bring `two_part_gbm` within the limit (1.65) at a recall of exactly 0.5. Evidence: Tables 1 and 6.
2. **The week-ahead combiner decides tier 5 for three of five rows** (Table 9), and it was chosen after the benchmark rows'
   calibration was seen. Under independence two rows pass; under the maximum one passes. Whether tier 5 should use a combiner that
   takes the dependence between days into account (a window model rather than a combination of horizons) is a rule decision.
3. **The covers-zero test in a regime with no pressure day is mechanically unmeetable** (every row and benchmark misses zero in
   2021-23). The amended tier 3 already sets those regimes aside; the finding is that the reported-only column for them carries no information.
4. **2020 (four pressure days) is the regime that fails tier 3 for every row**; 2025-26 fails for two of them. With so few events a regime's
   test is close to a coin toss on a handful of days (the intervals are wide). Whether a regime with fewer than some number of pressure days is
   tested is a decision.
5. **The directive's "five tier-1 passers" is not a set that passes tier 1.** The five are the best rows by onsets flagged
   (`docs/pivot/onset-diagnostics-result.md`); none passes the bar.
6. **2018-19 down-weighting does not rescue or sink any row at this reading**, but it was applied to the cut-off choice only. A
   reading that refits the rows' own probabilities with the period down-weighted is a larger change (new fits, not a diagnostic).

## Reproduce

Published panel `4ddc3882…` (rebuilt from the tracked fixtures, `verify-panel` clean); scratch panels from
`pressure_v1_1.py panel` (`AUG.csv`) and `measurement_fields.py panel` (`AUG2.csv`). `OMP_NUM_THREADS=1`;
`/opt/rmm-venv/bin/python`. Each row's forecasts come from its own script, unchanged, h = 1 to 5, as
`docs/pivot/onset-diagnostics-result.md` lists:

```
for h in 1 2 3 4 5:
  PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUB.csv --horizon $h --output OUT/bench_h$h.json
  PYTHONPATH=src python3 scripts/hierarchical_logistic.py forecasts --panel AUG.csv --horizon $h --output OUT/hl_h$h.json
  PYTHONPATH=src python3 scripts/settlement_timing.py run --panel AUG2.csv --published PUB.csv --candidate settlement_quantile_timing --horizon $h --output OUT/sqt_h$h.json
  PYTHONPATH=src python3 scripts/scarcity_event_bar.py forecasts --panel AUG.csv --horizon $h --candidate scarcity_logistic_interactions --output OUT/sli_h$h.json
  PYTHONPATH=src python3 scripts/pressure_two_part.py horizon --panel PUB.csv --horizon $h --output OUT/tp_h$h.json
  PYTHONPATH=src python3 scripts/pressure_track_q.py forecasts --panel PUB.csv --horizon $h --output OUT/q_h$h.json --distribution OUT/qdist_h$h.json
PYTHONPATH=src python3 scripts/setup_sensitivity.py run --panel PUB.csv --bench 'OUT/bench_h{h}.json' \
    --row two_part_gbm='OUT/tp_h{h}.json' --row ngboost_laplace='OUT/q_h{h}.json' --row hierarchical_logistic='OUT/hl_h{h}.json' \
    --row settlement_quantile_timing='OUT/sqt_h{h}.json' --row scarcity_logistic_interactions='OUT/sli_h{h}.json' \
    --output docs/pivot/evidence/setup-sensitivity/setup_sensitivity.json --markdown docs/pivot/evidence/setup-sensitivity/setup_sensitivity.md
```

## Not checked, and for Eleonora

* The rows' own probabilities are not refitted with 2018-19 down-weighted, nor with the cut-off cadence changed: the diagnostic
  moves the cut-off choice, which is the judge's, and nothing inside the rows.
* `ngboost_laplace` is not named in the judge's declaration on main (it was scored by the pull request of #416 under a
  declaration that is not on main), so the script adds it in memory, with no features or calibration text, to run the judge's
  tier computations. No file under `metadata/pressure_judge/` is written and the declaration's digest is unchanged.
* The weighting uses 2018-19's share of all scored days, which includes days after a refit's training end. It is a sensitivity
  quantity, not a rule, and no cut-off reads a day after its training end (`select_cutoff_weighted` refuses one).
* The +10 bp threshold; intervals on the by-year readings (counts only); the confirmation window; any day of 2026.
