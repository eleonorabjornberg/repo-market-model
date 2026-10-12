# The scarcity state read at each leg's own latest public row (#586, Eleonora's ruling on #571)

A scratch measurement under the pressure-day judge. It writes nothing into `docs/runs/`, publishes nothing, moves no published
figure, scores no day of 2026 and reads no day after 2025-12-31 (`docs/decisions/lockbox.md`). No cut-point, threshold, onset
definition, cut-off rule or availability time changes; the only change is which row each of the state's three legs is read at.

> **Note of 12 October 2026 (#603): the verdicts and false-alarm counts below are on the earlier counting.** They were scored before the judge's
> pooled false-alarm count (ruling of 10 October 2026, #509) was merged into this branch, so tier 1 was read on the worst single lead. The same
> scoring under the judge in force is at the end of this page ("Note of 12 October 2026"), with its evidence in
> `evidence/own-leg-scarcity-pooled/`. Nothing below is edited.

> **Drafted decision record, not in force.** The amendment to `docs/decisions/information-set.md` that records the ruling is
> drafted by this pull request, for Eleonora to review. A decision is in force only once she has merged it.

## What changed

`reserve_scarcity_state` (`scarcity.py`, #115) is the sum of a reserves-ratio level and an ON RRP buffer level. It was read at the
one row where the reserves, the H.8 total assets and the day's ON RRP were all public, so the H.8's declared lag (twelve calendar
days) set the row all three were read at. It is now read from three reads, each at its own latest public row, each through
`InformationRule` and so both guards (`scarcity.own_leg_states`; `scarcity.own_leg_composition` for a model that takes the state as
an input). `asof.py` and `contract.py` are untouched: the final test's pipeline checksum covers both in full, the published
declaration, panel and pre-registered model are unchanged, and the published panel (`4ddc3882…`) verifies.

## How many days change state

Scored days 2018-06-29 to 2025-12-31, h = 1 (`days.json` has every horizon, by year, and every changed day):

| | days |
|---|---|
| scored | 1,873 |
| change state | 102 (54 up, 48 down) |
| by year | 2018: 3, 2020: 12, 2021: 13, 2023: 9, 2024: 1, 2025: 64 |
| enter the risky set (state >= 2) | 10 |
| leave the risky set | 5 |

The directive cites an audit of 105 to 110 days. This is 102 on the same grid; the difference is not reconciled (see the last section).
The 2025-09-15 onset now reads state 2 (it read 1 through 2025-09-23), and the move to state 3 on 2025-10-29 is seen the same day.
The other horizons change the same 102 days.

## Re-scored rows

Forecasts of every row that reads the state were refitted under each read from the same declarations and the same panels, five
horizons, and judged together under the judge in force (`metadata/pressure_judge.json`), flat and weighted. "Before" is the
same-row read; "after" is the own-leg read. Every `risk_*` parent takes the state as a model input, so every `risk_*` row
refits; `ngboost_laplace` does not read the state and changes only through the judge's risky set.

Judge tables, Table 1 (tier 1 pooled and per lead, tiers 3 and 5) and the full reports: `docs/pivot/evidence/own-leg-scarcity/`
(`tables-before-*`, `tables-after-*`, `judge-before-*`, `judge-after-*`). Side by side for the rows the directive names:
`table-weighted.md`, `table-unweighted.md`. Recall by calendar year at lead >= 1: `years-*`.

**Verdicts that change among the named rows.** Weighted rule: `risk_logistic_base+hurdle_state_isotonic+settle+h41` tier 1 no to
yes; `risk_quantile_skewt_base+hurdle_state_platt+settle+h41` tier 5 no to yes. Flat rule: the second only. No overall pass changes
anywhere. Across all rows judged, 11 tier verdicts change under the weighted rule and 4 under the flat rule, none of them a pass
(listed in `table-*.json` for the named rows; the rest are other `risk_*` variants whose inputs include the state).

**The three frozen candidates (#567).** Pooled tier 1 is unchanged for `risk_gbm+every_day+gate+settle+h41+iorb` and
`ngboost_laplace` under both rules and for `risk_gbm+settle+h41` under the weighted rule; under the flat rule
`risk_gbm+settle+h41` moves from 14 to 13 of 26 onsets (recall 0.538 to 0.500, still inside each other's interval), one 2025
onset fewer. No tier verdict of the three changes.

**#534's scarce control** (`risk_gbm+every_day+scarce`): 17 of 26 before and after, worst false alarms per onset 2.17 to 2.15
(weighted), tiers unchanged.

**The `hurdle_state` variants.** `risk_gbm+hurdle_state_*+settle+h41` fall from 16 to 14 of 26 onsets (weighted), both from 2019
(13 of 13 to 11 of 13); 2025 is unchanged at 3 of 5. See `table-weighted.md` for every variant.

### Recall by calendar year, lead >= 1, weighted rule (onsets flagged / onsets)

| row | read | 2018 | 2019 | 2020 | 2024 | 2025 | all |
|---|---|---|---|---|---|---|---|
| risk_gbm+settle+h41 | before | 0/4 | 10/13 | 0/2 | 0/2 | 4/5 | 14/26 |
| risk_gbm+settle+h41 | after | 0/4 | 10/13 | 0/2 | 0/2 | 4/5 | 14/26 |
| risk_gbm+every_day+gate+settle+h41+iorb | before | 0/4 | 13/13 | 2/2 | 0/2 | 4/5 | 19/26 |
| risk_gbm+every_day+gate+settle+h41+iorb | after | 0/4 | 13/13 | 2/2 | 0/2 | 4/5 | 19/26 |
| ngboost_laplace | before | 0/4 | 12/13 | 0/2 | 0/2 | 5/5 | 17/26 |
| ngboost_laplace | after | 0/4 | 12/13 | 0/2 | 0/2 | 5/5 | 17/26 |
| risk_gbm+every_day+scarce | before | 0/4 | 13/13 | 1/2 | 0/2 | 3/5 | 17/26 |
| risk_gbm+every_day+scarce | after | 0/4 | 13/13 | 1/2 | 0/2 | 3/5 | 17/26 |
| risk_gbm+hurdle_state_platt+settle+h41 | before | 0/4 | 13/13 | 0/2 | 0/2 | 3/5 | 16/26 |
| risk_gbm+hurdle_state_platt+settle+h41 | after | 0/4 | 11/13 | 0/2 | 0/2 | 3/5 | 14/26 |
| risk_gbm+hurdle_state_isotonic+settle+h41 | before | 0/4 | 13/13 | 0/2 | 0/2 | 3/5 | 16/26 |
| risk_gbm+hurdle_state_isotonic+settle+h41 | after | 0/4 | 11/13 | 0/2 | 0/2 | 3/5 | 14/26 |

2025 is called out: no frozen candidate's 2025 recall moves (`risk_gbm+settle+h41` 4/5, the iorb row 4/5, `ngboost_laplace` 5/5),
and the `hurdle_state` variants stay at 3/5. Why the earlier state reading of the 2025 onset does not move these rows' 2025 recall is not
traced here. The same table under the flat rule is in `years-*-unweighted.json`.

## Reproduce

Published panel `4ddc3882…` (`verify-panel` clean); scratch panel `AUG2` (`pressure_v1_1.py panel`, then
`measurement_fields.py panel`). `/opt/rmm-venv` (numpy 2.4.6, scikit-learn 1.9.1), `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`.

```
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
PYTHONPATH=src python3 scripts/own_leg_days.py --output OUT/days.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --output OUT/shared/bench_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_track_q.py forecasts --panel PUBLISHED.csv --horizon $h --output OUT/shared/q_h$h.json --distribution OUT/shared/qdist_h$h.json
# OUT/shared/ql_h$h.json is q_h$h.json with only the ngboost_laplace row (the judge refuses the undeclared rows)
for READ in own_leg same_row, for h in 1 2 3 4 5:
  W="PYTHONPATH=src python3 scripts/own_leg_rescore.py $READ"
  $W risk_date_severity run --panel AUG2.csv --published PUBLISHED.csv --horizon $h --output OUT/$READ/risk_h$h.json
  $W risk_date_false_alarm_controls run --panel AUG2.csv --published PUBLISHED.csv --horizon $h --output OUT/$READ/fa_h$h.json
  for arm in published settle h41 both: $W hurdle_dating_rescore run --arm $arm --panel AUG2.csv --published PUBLISHED.csv --horizon $h --output OUT/$READ/hd_${arm}_h$h.json
  $W announcement_dating_rescore run --arm both --model risk_gbm --panel AUG2.csv --published PUBLISHED.csv --horizon $h --output OUT/$READ/both_h$h.json
  $W iorb_every_day_579 run --panel AUG2.csv --published PUBLISHED.csv --horizon $h --parent OUT/$READ/both_h$h.json --output OUT/$READ/iorb_h$h.json
for READ in own_leg same_row, for r in weighted unweighted:
  PYTHONPATH=src python3 scripts/own_leg_rescore.py $READ pressure_judge judge --panel PUBLISHED.csv --rule $r --output OUT/$READ/judge_$r.json --markdown OUT/$READ/judge_$r.md OUT/shared/bench_h?.json OUT/shared/ql_h?.json OUT/$READ/{risk,fa,both,iorb}_h?.json OUT/$READ/hd_*_h?.json
  PYTHONPATH=src python3 scripts/pressure_judge.py table OUT/$READ/judge_$r.json --output OUT/$READ/tables_$r.md
for r in weighted unweighted:
  PYTHONPATH=src python3 scripts/own_leg_compare.py table --after OUT/own_leg/judge_$r.json --before OUT/same_row/judge_$r.json --output OUT/table_$r.md ROW...
  for READ in own_leg same_row: PYTHONPATH=src python3 scripts/own_leg_rescore.py $READ own_leg_compare years --rule $r --panel PUBLISHED.csv --output OUT/$READ/years_$r.json --rows ROW... -- OUT/shared/bench_h?.json OUT/shared/ql_h?.json OUT/$READ/{risk,fa,both,iorb}_h?.json OUT/$READ/hd_*_h?.json
```

`risk_date_hurdle.py` rows (`+hurdle_state_*` on the published timing) are the `hd_published` rows; they were not judged twice.

## Not checked, or for Eleonora

- Scripts that read the state through the rule but are not in this directive's list (`desk_outputs`, `onset_post_mortem`,
  `pressure_track_m`, `pressure_v1_1`, the calibrated stacks, `hierarchical_logistic` and the other judge candidates that list
  `reserve_scarcity_state`) still read the same-row column unless run through `scripts/own_leg_rescore.py own_leg`. They were not re-scored.
- Whether the own-leg read replaces the same-row read in `contract.py`/`asof.py`, which would move the final test's pipeline checksum
  (an owner-attested item), is not decided here. The published declaration is unchanged.
- The H.4.1 per-release dating of #541 is not part of the published registry; the `h41` arms apply it as before.
- The 102 against the audit's 105 to 110 is not reconciled: the audit's definition of "each leg's latest public value" was not available to this run.

## Note of 12 October 2026 (#603): the same scoring under the judge in force

The scoring above was run on the branch before it merged the judge's pooled false-alarm count (ruling of 10 October 2026, #509; merge
commit `62610793`), so the tier 1 verdicts and the "worst false alarms per onset" column are the earlier counting, the worst single lead.
The judge in force reads tier 1's limit on the false alarms pooled over the leads. The scoring was run again from the same declarations, the
same scratch panel and the same forecasts-producing commands as in "Reproduce" above, on `origin/main` at `5d88b50`, under both reads of the
state (own-leg and same-row) and both rules. Nothing else changed: the published declaration, the panel (`4ddc3882…`, `verify-panel` clean)
and the judge's declaration are the same, and no day of 2026 is scored. Evidence: `evidence/own-leg-scarcity-pooled/` (`judge-*`, `tables-*`
and `table-*` as in the folder above, now with both counts; recall by year is identical to `years-*` of the folder above for every row, so it
is not repeated). The table script prints the pooled count beside the worst single lead.

Tier 1 on the three frozen candidates (#567) and the scarce control, weighted rule (the rule in force). Onsets flagged of 26 at lead >= 1;
false alarms per onset, pooled (the count tier 1 reads; limit 2) and worst single lead (the earlier counting):

| row | read | flagged | pooled | worst single lead | tier 1 now | tier 1 as stored above |
|---|---|---|---|---|---|---|
| `risk_gbm+settle+h41` | same-row | 14 | 1.44 | 0.88 | yes | yes |
| `risk_gbm+settle+h41` | own-leg | 14 | 1.48 | 0.88 | yes | yes |
| `risk_gbm+every_day+gate+settle+h41+iorb` | same-row | 19 | 3.46 | 1.64 | **no** | yes |
| `risk_gbm+every_day+gate+settle+h41+iorb` | own-leg | 19 | 3.46 | 1.64 | **no** | yes |
| `ngboost_laplace` | same-row | 17 | 2.34 | 1.73 | **no** | yes |
| `ngboost_laplace` | own-leg | 17 | 2.34 | 1.73 | **no** | yes |
| `risk_gbm+every_day+scarce` | same-row | 17 | 3.60 | 2.17 | no | no |
| `risk_gbm+every_day+scarce` | own-leg | 17 | 3.49 | 2.15 | no | no |

Flat rule: `risk_gbm+settle+h41` is 14 of 26 with 2.00 pooled on the same-row read (tier 1 yes) and **13 of 26 with 2.04 pooled on the own-leg
read (tier 1 no)**; the other three rows fail tier 1 on both reads, as stored.

**Correction.** The statement above that "no tier verdict of the three changes" holds for the two reads only under the weighted rule. Under the
flat rule `risk_gbm+settle+h41` moves from tier 1 yes to no with the own-leg read (the pooled count passes the limit of 2 by 0.04). And the
stored absolute tier 1 verdicts "yes" for the iorb row and for `ngboost_laplace` (weighted rule) are on the earlier counting: under the pooled
count both fail tier 1 on either read, as does the iorb row's parent. The comparison of one read with the other, which this directive was
about, is not changed by the counting for those rows. No row passes the judge overall under either read, either rule, as before.

Across the 117 rows judged, the tier verdicts that change between the two reads are 9 under the weighted rule and 11 under the flat rule
(`table-*.json` lists the named rows); none is an overall pass. The set of changed verdicts is not the one listed above (2 and 1 among the named
rows). Verdicts of tier 3 and tier 5 also differ from the stored ones for some rows (listed in `evidence/own-leg-scarcity-pooled/table-*.json`
against `evidence/own-leg-scarcity/table-*.json`). Tiers 3 and 5 are not read on the pooled false-alarm count, so the counting is not the explanation; the branch merged the rest of `main` (including the start-up cut-off machinery of #584) after the scoring above, and this
re-score has not been split by which merged change moves which verdict. That is a finding for whoever reads those rows, not settled here.

Not checked: scripts that read the state outside this directive's list (as above), and any 2026 day.

