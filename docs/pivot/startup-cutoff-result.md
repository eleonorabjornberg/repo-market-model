# A start-up cut-off for the judge: what it changes for the three frozen rows (#584, from #560)

A scratch measurement under the pressure-day judge. It changes no rule in force, publishes nothing, moves no published figure, writes nothing into `docs/runs/`, scores no day of 2026 and reads no day after 2025-12-31 (`docs/decisions/lockbox.md`; the script refuses a later last day). The judge as declared (`metadata/pressure_judge.json`, its in-force version) is the `declared` row of every table. The two start-up rules were declared in `metadata/startup_cutoff_584.json`, and the code and tests committed (e0e1aeb4), before any score was computed under them. The code is `scripts/startup_cutoff_584.py` and `pressure_judge.StartupRule`; the numbers are `docs/pivot/evidence/startup-cutoff/` (`tables.md` is the full set, `startup.json` the data).

**The rows were frozen on these same days and the rules were chosen after #560 found the gap here, so a result is not a confirmation** (Eleonora's ruling of 11 October 2026 on #567). Nothing here joins `confirmation.candidates`.

## What was done

The judge picks each refit block's cut-off from the forecast's own earlier probabilities and the outcomes known at the block's first decision instant; a block whose window holds no onset flags nothing. The same forecasts of the three frozen rows (`risk_gbm+every_day+gate+settle+h41+iorb`, `risk_gbm+settle+h41`, `ngboost_laplace`) and the two benchmarks were re-judged three times, at h = 1 to 5, +5 and +10 bp, under the weighted rule in force and the flat rule beside it:

| rule | what a block with no onset in its window uses | reads |
|---|---|---|
| declared | nothing: flags nothing (cut-off infinite) | |
| A, climatology rate | the share of the window's scored days that are pressure days; a window with none flags nothing | the window's pressure-day labels, all known at the refit; `startup_cutoff` refuses (`LookAheadError`) a later day |
| B, fixed 0.2 | the constant 0.2, the judge's first placeholder (#375) | nothing |

The 2014-2018 history is not used for B: the guard of #572 (merged in #590 after this branch was cut) refuses every fit that trains on a back-filled value while `posting_instant` in `metadata/backfill_posting.json` is null, and it is null; so the directive's alternative is not allowed and B comes from the rule alone. The forecasts are the rows' own, regenerated with the repository's scripts on the published panel (`verify-panel` digest `4ddc3882…`); the declared column reproduces the onsets flagged and the recalls of the earlier pages (19, 14 and 17 of 26, weighted).

## Result

**Under the weighted rule in force, neither rule changes a verdict; under the flat rule, both take one row out of tier 1.** The judge here is main's at the time of the run (e61471ab, with the rulings of 10 October on #509, #510 and regime scoring, #550): tier 1 limits the false alarms **pooled over the leads**, so the columns below differ from the pages written before it (for example 19 of 26 at 1.64, the worst single lead, is now 19 of 26 at 3.46 pooled, and tier 1 fails for that row). The onsets flagged and the recalls reproduce those pages exactly. Under the weighted rule, `risk_gbm+settle+h41` passes tier 1 and the other two rows do not, under all three start-up rules. Under the flat rule, `risk_gbm+settle+h41` passes the declared judge at exactly 2.00 and fails under A (2.54) and under B (2.12): the false alarms the rule adds in 2018 are pooled into the count. Tiers 3 and 5 fail for every row, benchmarks included, under every rule. Only 2018 moves; every refit block of 2019 and later has an onset in its window and is the declared judge's.

Table 1. Tier 1 pooled over leads 1 to 5, +5 bp: onsets flagged of 26, recall [90%], false alarms per onset pooled over the leads (the figure the tier reads; limit 2).

| row | rule | weighted rule | flat rule |
|---|---|---|---|
| `…+iorb` | declared | 19, 0.731 [0.560, 0.889], 3.46 (fails) | 16, 0.615 [0.440, 0.786], 4.35 (fails) |
| | A | 21, 0.808 [0.667, 0.933], 3.94 (fails) | 18, 0.692 [0.533, 0.846], 4.88 (fails) |
| | B | 19, 0.731 [0.560, 0.889], 3.58 (fails) | 16, 0.615 [0.440, 0.786], 4.46 (fails) |
| `risk_gbm+settle+h41` | declared | 14, 0.538 [0.353, 0.710], 1.44 (passes) | 14, 0.538 [0.353, 0.710], 2.00 (passes) |
| | A | 16, 0.615 [0.435, 0.774], 1.92 (passes) | 16, 0.615 [0.435, 0.774], 2.54 (**fails**) |
| | B | 14, 0.538 [0.353, 0.710], 1.56 (passes) | 14, 0.538 [0.353, 0.710], 2.12 (**fails**) |
| `ngboost_laplace` | declared | 17, 0.654 [0.467, 0.826], 2.34 (fails) | 15, 0.577 [0.400, 0.759], 4.38 (fails) |
| | A | 17, 0.654 [0.467, 0.826], 2.91 (fails) | 15, 0.577 [0.400, 0.759], 4.96 (fails) |
| | B | 17, 0.654 [0.467, 0.826], 2.34 (fails) | 15, 0.577 [0.400, 0.759], 4.38 (fails) |

Leads 3 to 5 pooled are identical under all three rules for every row. Per lead (`tables.md`, "Tier 1 per lead"): the only cell recall moves in is **h = 2 under A**, where the two risk-date rows go from 12 to 14 and from 11 to 13 onsets (2018: 0 of 4 to 2 of 4), and `ngboost_laplace` stays at 7 of 26; the weighted false alarms per onset at h = 2 go from 1.39 to 1.91, from 0.58 to 1.10, and from 1.42 to 2.00. Under B no cell's recall moves; its false alarms per onset rise by 0.07 to 0.16 at h = 2 to 5, and the pooled count by about 0.1 (Table 1).

Table 2. Onsets flagged at some lead in 2018 (of 4) and false alarms added in 2018, weighted rule, flags added against the declared judge over h = 1 to 5 (of which not pressure days; onsets).

| row | declared | A: 2018 onsets | A: flags added | B: 2018 onsets | B: flags added |
|---|---|---|---|---|---|
| `…+iorb` | 0 | 2 (+0.500, two onsets of four: no interval) | 17 (15; 2), all at h = 2 | 0 | 13 (13; 0) |
| `risk_gbm+settle+h41` | 0 | 2 | 17 (15; 2), all at h = 2 | 0 | 13 (13; 0) |
| `ngboost_laplace` | 0 | 0 | 15 (15; 0), all at h = 2 | 0 | 0 |
| `calendar_climatology` | 0 | 2 | 61 (58; 2) | 0 | 22 (22; 0) |
| `persistence_logistic` | 0 | 2 | 71 (68; 2) | 0 | 9 (9; 0) |

The two onsets rule A warns are **2018-11-15 and 2018-11-30**, at h = 2, for the two risk-date rows (probability 0.111 on each against a cut-off of 0.0122); the other two 2018 onsets (2018-12-17, 2018-12-28) stay unwarned. Recall difference from the declared judge, all 26 onsets: +0.077 [0.000, +0.185] (A, the two risk-date rows), 0.000 (A, `ngboost_laplace`; B, all three). By regime the whole of it is 2018-19: +0.118 [0.000, +0.278]; by day type, month-end +0.167 (one onset of six) and ordinary +0.083 [0.000, +0.250]; 2020, 2024 and 2025-26 are unchanged (`tables.md`).

## What it says

1. **Rule A applies at one horizon, on one pressure day.** Its blocks are served only at h = 2 (four blocks, 2018-08-01 to 2018-11-30). The reason is a single day: 2018-07-02 is a pressure day that is not an onset on the h = 2 grid (the grid starts there; at h = 1 the first day is an onset and the declared rule already has one), so the "rate" is 1 day in 19, a cut-off of 0.053 falling to 0.012 as the window grows. At h = 1 and h = 3 to 5 the window has no pressure day and the rule flags nothing, as now. The gain is the product of that one day.
2. **The gain is not specific to the rows.** Under A, `calendar_climatology` and `persistence_logistic` flag the same two onsets, with 61 and 71 flags added of which 58 and 68 are false. Against those benchmarks the recall advantage of the two risk-date rows is unchanged (+0.269 [+0.115, +0.440] for the first row against climatology under both the declared judge and A), and the advantage of `ngboost_laplace` against climatology shrinks, +0.192 [0.000, +0.367] to +0.115 [-0.107, +0.346], because the benchmarks gain 2018 onsets it does not.
3. **Rule B is inert on the onsets and costs false alarms.** At 0.2 it adds 2 to 4 flags per horizon for the two risk-date rows, none of them pressure days, and warns no onset: where it applies, the rows' probability on an onset is under 0.2 (0.111 on 2018-11-15 and 2018-11-30 at h = 2; #560 gives 0.07 to 0.11 at lead 1 for the passers).
4. **Neither rule solves the 2018 problem.** The four 2018 onsets are missed by every row, by construction, because the early blocks hold no onset; a rate read from one day, or a constant, gives a cut-off that is not matched to the model's scale. The 2018 recall under either rule is not evidence about a model.

## For Eleonora

The draft amendment is [`docs/decisions/drafts/judge-startup-cutoff.md`](../decisions/drafts/judge-startup-cutoff.md). It is for her own attested action and does not change `metadata/pressure_judge.json`. The result suggests, and does not settle, that neither option is worth adopting as drafted; the alternative the draft lists (treating 2018 as "no cut-off available" and out of tier 1's recall) is hers to weigh.

## Reproduce

Published panel `4ddc3882…` and scratch panels as for #579; `/opt/rmm-venv` (numpy 2.4.6, scikit-learn 1.9.1), `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`. The forecasts took about an hour on four cores; the judging passes about 20 minutes.

```
PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
for h in 1 2 3 4 5:
  PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUB.csv --horizon $h --published --output OUT/bench_h$h.json
  PYTHONPATH=src python3 scripts/announcement_dating_rescore.py run --arm both --model risk_gbm --panel AUG2.csv --published PUB.csv --horizon $h --output OUT/both_h$h.json
  PYTHONPATH=src python3 scripts/iorb_every_day_579.py run --panel AUG2.csv --published PUB.csv --horizon $h --parent OUT/both_h$h.json --output OUT/iorb_h$h.json
  PYTHONPATH=src python3 scripts/pressure_track_q.py forecasts --panel PUB.csv --horizon $h --output OUT/q_h$h.json --distribution OUT/qdist_h$h.json
PYTHONPATH=src python3 scripts/startup_cutoff_584.py run --panel PUB.csv --output OUT/startup.json --markdown OUT/startup.md OUT/bench_h?.json OUT/both_h?.json OUT/iorb_h?.json OUT/q_h?.json
```

## Not checked

* No 2026 day is scored and the confirmation window is not looked at. The rules were not tried on any other threshold than the two declared (+5 and +10 bp; +10 bp is in the evidence).
* No value other than 0.2 was tried for B, and no other quantile for A, by declaration.
* The 2014-2018 back-filled history was not used (the guard of #572 refuses it until Eleonora establishes the posting instant).
