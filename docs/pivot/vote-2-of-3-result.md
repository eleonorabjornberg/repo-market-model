# A two-of-three alarm on the pressure judge (#458)

A scratch measurement under the judge as it stands on main (#375, amended under #407). It changes no published declaration,
writes nothing into `docs/runs/` and moves no published figure. Scored days 2018-06-29 to 2025-12-31 only, h = 1 to 5, +5 bp
primary, 90% stationary-bootstrap intervals; no 2026 day is read (`docs/decisions/lockbox.md`).

## What was declared

`vote_2_of_3` (`metadata/pressure_judge/candidates/vote_2_of_3.json`, committed before any score) flags a day when at least two
of `two_part_gbm`, `ngboost_laplace` and `hierarchical_logistic` flag it. Each voter's flag is the judge's own: its
walk-forward probability at or above the cut-off chosen refit by refit from that voter's training window
(`pressure_judge.choose_cutoffs`). The vote has no cut-off of its own: its probability is the share of voters whose flag is up
(0, 1/3, 2/3 or 1) and its cut-off is 2/3. It uses the voters' existing walk-forward forecasts and refits nothing. The
tiers that read a probability (tier 3's calibration by regime, tier 5) therefore read that vote share, which is not a fitted
probability; they are reported but are a weak test of a vote.

The voters' declarations are not in `metadata/pressure_judge.json` on main; `scripts/vote_2_of_3.py` adds them in memory, for
the run only, from `docs/pivot/evidence/judge-amendment/pressure_judge_rejudge.json`. Their rows reproduce Table 1 of the
re-judge (`judge-amendment-result.md`): 15 of 26 onsets flagged and worst false alarms per onset 2.46, 2.54 and 3.65.

The weighted-miss rule (#454) has merged as a draft: its switch in `metadata/weighted_miss.json` is off, so the judge on main counts
every false alarm as 1. This run scores the vote under both rules, forced for the run (`--rule unweighted` and `--rule weighted`,
as `pressure_judge.py judge` does). Under the weighted rule every voter's cut-off is chosen again on the weighted count, so the
voters' rows differ from the unweighted ones; the vote is built from each voter's cut-offs under the same rule.

## Result under the unweighted rule: the vote fails tier 1 on false alarms by 0.19 per onset

Table 1 (the judge's row; the three voters and the two benchmarks beside it):

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset (limit 2) | pass |
|---|---|---|---|---|---|
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 0.269 | 5.00 | fail |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 0.231 | 3.42 | fail |
| two_part_gbm | 15 of 26 | 0.577 [0.400, 0.762] | 0.192 | 2.46 | fail |
| ngboost_laplace | 15 of 26 | 0.577 [0.400, 0.759] | 0.231 | 2.54 | fail |
| hierarchical_logistic | 15 of 26 | 0.577 [0.400, 0.750] | 0.231 | 3.65 | fail |
| **vote_2_of_3** | **15 of 26** | **0.577 [0.389, 0.750]** | **0.192** | **2.19** | **fail** |

* **Tier 1 (onsets warned at lead >= 1).** Recall 0.577 meets the 0.5 bar and its lower end (0.389) is above the climatology
  recall at the same false alarms (0.192). The false-alarm limit is missed: 2.19 per onset at h = 5 (1.38, 1.31, 1.42, 1.81 and
  2.19 at h = 1 to 5). The vote keeps all 15 onsets the voters flag and has fewer false alarms than any single voter
  (176, 233 and 382 across the five horizons; 211 for the vote), but the best voter's own count is lower than the vote's, so the
  vote improves on the average voter, not on `two_part_gbm`.
* **Tier 3 (no crying wolf).** No flags in the abundant stretches (state 0, 2021-23), so the flag-rate condition holds; the
  calibration condition fails at every lead, in 2025-26 at every lead and in 2018-19 at h = 2. Calibrated regimes with a pressure
  day at h = 1: 3 of 4.
* **Tier 5 (week-ahead).** Beats climatology on Brier (difference +0.048 [+0.032, +0.066]) but is not calibrated
  (realised minus predicted +0.057 [+0.030, +0.088]).
* **Scarce regime alone:** recall 0.652 [0.462, 0.840] on 23 onsets, worst false alarms 2.48 per onset: fail on tiers 1, 3 and 5.

Table 2. Share of the pressure days flagged at h = 1 (+5 bp), by regime and pressure-day type; pressure days in brackets.

| model | 2018-19 | 2020 | 2021-23 | 2024 | 2025-26 | month_end | ordinary | quarter_end | tax_date |
|---|---|---|---|---|---|---|---|---|---|
| two_part_gbm | 0.25 (102) | 0.25 (4) | – | 0.00 (5) | 0.21 (29) | 0.47 (17) | 0.16 (101) | 0.44 (9) | 0.38 (13) |
| ngboost_laplace | 0.55 (102) | 0.25 (4) | – | 0.20 (5) | 0.34 (29) | 0.59 (17) | 0.46 (101) | 0.67 (9) | 0.46 (13) |
| hierarchical_logistic | 0.68 (102) | 0.00 (4) | – | 0.00 (5) | 0.52 (29) | 0.71 (17) | 0.57 (101) | 0.56 (9) | 0.69 (13) |
| vote_2_of_3 | 0.53 (102) | 0.25 (4) | – | 0.00 (5) | 0.31 (29) | 0.59 (17) | 0.42 (101) | 0.56 (9) | 0.54 (13) |

The full row and the Brier-by-regime table are in `docs/pivot/evidence/vote-2-of-3/tables_unweighted.md` and `judge_unweighted.md`.

## How much the voters overlap (unweighted rule)

At +5 bp, h = 1 to 5 together (`docs/pivot/evidence/vote-2-of-3/overlap_unweighted.md`):

* **False alarms overlap little.** The voters raise 176, 233 and 382 false alarms (a day and horizon counted once); 545 distinct
  ones in all. Any two share about a fifth of their union (0.21, 0.21 and 0.23), 35 are raised by all three and 334 by one voter
  alone. The vote keeps the 211 raised by at least two.
* **Hits overlap a great deal.** Of the 26 onsets, each voter flags 15 and any two share 13 of the 17 they flag between them
  (0.76). Twelve onsets are flagged by all three and 3 by exactly one, which the vote then loses; the vote's 15 are the onsets at
  least two flag.

So the voters' errors are mostly different and their successes mostly the same, which is why the vote cuts false alarms (545
distinct to 211) without losing recall (15 of 26 for each voter and for the vote). The cut is not enough to bring h = 5 under
two false alarms per onset.

## Result under the weighted rule (the draft of #454, not in force)

Weights: 0.25 within 2 trading days of a pressure day, 0.5 within 3 to 5, 1 beyond; limit 2 per onset. The flat count is the unweighted one.

| model | onsets flagged | recall [90%] | clim. recall, same false alarms | worst false alarms per onset, flat | worst false alarms per onset, weighted | tier 1 | tier 3 | tier 5 | pass |
|---|---|---|---|---|---|---|---|---|---|
| two_part_gbm | 15 of 26 | 0.577 [0.400, 0.762] | 0.269 | 4.81 | 2.55 | fail | fail | fail | fail |
| ngboost_laplace | 17 of 26 | 0.654 [0.467, 0.826] | 0.231 | 4.08 | 1.73 | pass | fail | fail | fail |
| hierarchical_logistic | 15 of 26 | 0.577 [0.400, 0.750] | 0.319 | 6.23 | 2.91 | fail | fail | fail | fail |
| **vote_2_of_3** | **15 of 26** | **0.577 [0.389, 0.750]** | **0.235** | **4.27** | **1.80** | **pass** | **fail** | **pass** | **fail** |

* **Tier 1 is met by the vote** under the weighted rule: recall 0.577, lower end 0.389 above the climatology recall 0.235, and weighted false
  alarms per onset 0.77, 1.53, 1.36, 1.37 and 1.80 at h = 1 to 5 (limit 2). Flat, the same flags cost 2.15 to 4.27 per onset, so the pass depends on
  the draft weights. Only `ngboost_laplace` (17 of 26, weighted 1.73) also passes tier 1 under the weighted rule.
* **Tier 5 is met** (beats climatology on Brier, calibrated), read on the vote share.
* **Tier 3 fails**: no flags in the abundant stretches, but the vote is uncalibrated in 2018-19 at h = 1, 2, 3 and 5 and in 2020 at h = 1 and 5, and in
  2025-26 at h = 2 to 5. So the vote does not pass the pass rule.
* **Scarce regime alone:** recall 0.652 [0.462, 0.840]; tiers 1 and 3 fail, tier 5 is met.
* **Overlap under the weighted cut-offs** (`evidence/vote-2-of-3/overlap_weighted.md`): the voters raise 445, 460 and 634 false alarms; 844 distinct, 263 common to all three;
  pairs share 0.49, 0.40 and 0.47 of their union. Hits: any two voters share 14 of 18, 13 of 17 and 14 of 18 of the onsets they flag between them; 13 onsets are flagged by all three. The vote has 432 false
  alarms, fewer than any voter, and 15 onsets (one fewer than `ngboost_laplace`'s 17 at its weighted cut-off).

The full weighted row and regime split are in `evidence/vote-2-of-3/tables_weighted.md` and `judge_weighted.md`.

## Reproduce

Published panel `4ddc3882…` (`verify-panel` clean); scratch panel `pressure_v1_1.py panel` for the hierarchical logistic. Run with
`OMP_NUM_THREADS=1` and `/opt/rmm-venv/bin/python`.

```
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
for h in 1 2 3 4 5:
  PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUB.csv --horizon $h --output OUT/bench_h$h.json
  PYTHONPATH=src python3 scripts/hierarchical_logistic.py forecasts --panel AUG.csv --horizon $h --output OUT/hl_h$h.json
  PYTHONPATH=src python3 scripts/pressure_two_part.py horizon --panel PUB.csv --horizon $h --output OUT/tp_h$h.json
  PYTHONPATH=src python3 scripts/pressure_track_q.py forecasts --panel PUB.csv --horizon $h --output OUT/q_h$h.json --distribution OUT/qdist_h$h.json
for r in unweighted weighted:
  PYTHONPATH=src python3 scripts/vote_2_of_3.py judge --rule $r --panel PUB.csv --output OUT/vote_$r.json --markdown OUT/vote_$r.md --overlap OUT/overlap_$r.json OUT/bench_h?.json OUT/tp_h?.json OUT/q_h?.json OUT/hl_h?.json
  PYTHONPATH=src python3 scripts/pressure_judge.py table OUT/vote_$r.json --output OUT/tables_$r.md
```

The hierarchical logistic file carries the scratch panel's digest; `vote_2_of_3.py` accepts it because its days are the
benchmark's, and records the digest in the result's provenance.

## Publishing

The vote passes tier 1 under the draft weighted rule, so a "Publish?" question is open for Eleonora (linked from the pull request). Nothing is
added to `confirmation.candidates` and no published declaration changes.
