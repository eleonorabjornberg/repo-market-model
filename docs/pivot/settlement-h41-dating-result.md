# Settlements dated from the announcement and the H.4.1 read per release: the five risk-date passers re-scored (#541, of #374)

A scratch measurement under the pressure-day judge. It writes nothing into `docs/runs/`, moves no published figure, and reads no
day after 2025-12-31 (`docs/decisions/lockbox.md`; the script refuses a later panel). The live record and pin do not move. Both
readings are **off in every published declaration**: `metadata/sources.json` is frozen by the final-test pre-registration (bytes),
so the registry is not edited. They are declared in `metadata/settlement_announcement_dating.json` and `metadata/h41_release_dating.json`,
and the scoring in `metadata/announcement_dating.json`, all committed before the first forecast was fitted.

The rulings are Eleonora's of 10 October 2026, relayed by the orchestrating session on #541: (1) a Treasury settlement is dated
from the auction announcement, not the auction results; (2) the H.4.1 is read per release, at the release's own publication
instant. The amendment to `docs/decisions/information-set.md` is a **draft for her to merge** and is not in force until she does.

## What was built

* **Settlements** (`settlement_dating`, basis `auction_announcement`): a settlement's amount is public from 12:00 New York time on
  its auction's `announcemt_date`. Treasury publishes no clock time for an announcement (the TreasuryDirect page states only that its
  list of upcoming auctions is updated Fridays by 10:45), so the 12:00 rests on the usual late-morning announcement plus an hour, as
  `metadata/net_settlement.json` (#426) does, and was **not verified against a published clock time**. Any instant from 11:00 to
  15:59 gives the same sums at the 16:00 decision. At h = 1 the columns are the published panel's, row for row
  (`test_at_horizon_one_the_settle_arm_reads_the_published_columns`). The coupon clause of the risk-date rule then applies at h >= 2.
* **H.4.1** (`h41_release`, `asof.release_instant`): a Wednesday level is first observable at the print of its own release,
  Thursday 16:30 New York time, or the actual date when the Board moved it. Fifteen weeks from 2018 to 2025 are moved; each is
  evidenced by the Board's own release page (`evidence/settlement-h41-dating/h41_release_pages.json`). A forecast reads a level from
  the first decision at or after the print, so a Wednesday level is read two panel days earlier in an ordinary week than under the
  five-calendar-day lag (`tests/test_announcement_dating.py`). The staleness and leakage guards still hold there.

## Reproduce

Published panel `4ddc3882…` (`verify-panel` clean, unchanged: neither reading edits a panel column); scratch panel as for #428 and #532
(`pressure_v1_1.py panel`, then `measurement_fields.py panel`). `/opt/rmm-venv` (numpy 2.4.6, scikit-learn 1.9.1), `OMP_NUM_THREADS=1`.

```
PYTHONPATH=src python3 scripts/announcement_dating_rescore.py declare      # already committed; shown for the record
for arm in published settle h41 both; for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/announcement_dating_rescore.py run --arm $arm --panel AUG2.csv --published PUBLISHED.csv --horizon $h --output OUT/${arm}_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --output OUT/bench_h$h.json
for r in weighted unweighted: PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule $r --output OUT/judge_$r.json --markdown OUT/judge_$r.md OUT/bench_h?.json OUT/published_h?.json OUT/settle_h?.json OUT/h41_h?.json OUT/both_h?.json
PYTHONPATH=src python3 scripts/announcement_dating_rescore.py summary --flat OUT/judge_unweighted.json --weighted OUT/judge_weighted.json --output OUT/summary.md
for r in weighted unweighted: PYTHONPATH=src python3 scripts/announcement_dating_rescore.py compare --rule $r --panel PUBLISHED.csv --output OUT/compare_$r.json --markdown OUT/compare_$r.md OUT/bench_h?.json OUT/published_h?.json OUT/settle_h?.json OUT/h41_h?.json OUT/both_h?.json
```

The `published` rows reproduce #532's (for example `risk_gbm` 13 of 26 at 1.35 false alarms per onset and `risk_gbm+every_day+gate` 17 of 26 at 1.63
weighted). Evidence: `docs/pivot/evidence/announcement-dating/` (`summary.md` is Table 1 for every row; `judge-*.md` the judge's full reports,
with tier 1 pooled and per lead, tiers 3 and 5, split by regime and day type; `compare*.md` the pairing of every arm row against its
published row with 90% stationary-bootstrap intervals, by year, regime and pressure-day type, flags per horizon and the Brier pairing).

## Result: no row passes the full rule, and no verdict changes

Table 1 (the judge's row at +5 bp, 90% intervals; `published` is the unsuffixed row). `+settle` is settlements from the announcement,
`+h41` the H.4.1 per release, `+settle+h41` both. "Worst false alarms per onset" is the highest of the five horizons; the limit is 2.

| row | onsets flagged, flat / weighted | recall, flat [90%] | worst false alarms per onset, flat | worst weighted, weighted rule | tiers 1 / 3 / 5, flat | tiers 1 / 3 / 5, weighted |
|---|---|---|---|---|---|---|
| risk_gbm | 13/26 / 13/26 | 0.500 [0.310, 0.667] | 1.35 | 0.80 | yes / no / no | yes / no / no |
| risk_gbm+settle | 14/26 / 14/26 | 0.538 [0.355, 0.708] | 1.35 | 0.89 | yes / no / no | yes / no / no |
| risk_gbm+h41 | 13/26 / 13/26 | 0.500 [0.323, 0.667] | 1.35 | 0.75 | yes / no / no | yes / no / no |
| risk_gbm+settle+h41 | 14/26 / 14/26 | 0.538 [0.353, 0.710] | 1.35 | 0.88 | yes / no / no | yes / no / no |
| risk_gbm+every_day+gate | 16/26 / 17/26 | 0.615 [0.444, 0.778] | 2.96 | 1.63 | no / no / no | yes / no / no |
| risk_gbm+every_day+gate+settle | 14/26 / 18/26 | 0.538 [0.364, 0.719] | 2.27 | 1.62 | no / no / no | yes / no / no |
| risk_gbm+every_day+gate+h41 | 15/26 / 17/26 | 0.577 [0.391, 0.762] | 2.92 | 1.64 | no / no / no | yes / no / no |
| risk_gbm+every_day+gate+settle+h41 | 15/26 / 18/26 | 0.577 [0.417, 0.741] | 2.35 | 1.64 | no / no / no | yes / no / no |
| risk_gbm_base | 14/26 / 14/26 | 0.538 [0.360, 0.719] | 1.50 | 0.97 | yes / no / no | yes / no / no |
| risk_gbm_base+settle | 13/26 / 14/26 | 0.500 [0.333, 0.677] | 1.50 | 0.99 | yes / no / no | yes / no / no |
| risk_gbm_base+h41 | 14/26 / 15/26 | 0.538 [0.368, 0.720] | 1.19 | 0.86 | yes / no / no | yes / no / no |
| risk_gbm_base+settle+h41 | 14/26 / 14/26 | 0.538 [0.353, 0.720] | 1.23 | 1.08 | yes / no / no | yes / no / no |
| risk_gbm_base+every_day+gate | 15/26 / 18/26 | 0.577 [0.400, 0.750] | 2.88 | 1.62 | no / no / no | yes / no / no |
| risk_gbm_base+every_day+gate+settle | 13/26 / 17/26 | 0.500 [0.318, 0.690] | 2.50 | 1.68 | no / no / yes | yes / no / yes |
| risk_gbm_base+every_day+gate+h41 | 14/26 / 17/26 | 0.538 [0.348, 0.731] | 2.96 | 1.61 | no / no / no | yes / no / no |
| risk_gbm_base+every_day+gate+settle+h41 | 13/26 / 17/26 | 0.500 [0.316, 0.684] | 2.54 | 1.75 | no / no / no | yes / no / no |
| risk_logistic | 14/26 / 16/26 | 0.538 [0.350, 0.724] | 1.85 | 1.74 | yes / no / no | yes / no / no |
| risk_logistic+settle | 16/26 / 16/26 | 0.615 [0.433, 0.808] | 1.88 | 2.12 | yes / no / no | no / no / no |
| risk_logistic+h41 | 13/26 / 15/26 | 0.500 [0.333, 0.682] | 1.73 | 1.70 | yes / no / no | yes / no / no |
| risk_logistic+settle+h41 | 15/26 / 16/26 | 0.577 [0.391, 0.760] | 1.81 | 2.12 | yes / no / no | no / no / no |
| risk_logistic+every_day+gate | 14/26 / 18/26 | 0.538 [0.370, 0.720] | 3.00 | 2.19 | no / no / no | no / no / no |
| risk_logistic+every_day+gate+settle | 14/26 / 17/26 | 0.538 [0.364, 0.708] | 2.96 | 2.12 | no / no / yes | no / no / yes |
| risk_logistic+every_day+gate+h41 | 15/26 / 17/26 | 0.577 [0.391, 0.762] | 2.96 | 1.99 | no / no / no | yes / no / no |
| risk_logistic+every_day+gate+settle+h41 | 14/26 / 18/26 | 0.538 [0.351, 0.708] | 2.69 | 2.05 | no / no / yes | no / no / yes |
| risk_logistic_base | 13/26 / 15/26 | 0.500 [0.333, 0.680] | 1.77 | 1.65 | yes / no / no | yes / no / no |
| risk_logistic_base+settle | 13/26 / 14/26 | 0.500 [0.333, 0.677] | 1.77 | 1.86 | yes / no / no | yes / no / no |
| risk_logistic_base+h41 | 13/26 / 15/26 | 0.500 [0.320, 0.680] | 1.69 | 1.57 | yes / no / no | yes / no / no |
| risk_logistic_base+settle+h41 | 13/26 / 15/26 | 0.500 [0.333, 0.684] | 1.69 | 1.69 | yes / no / no | yes / no / no |
| risk_logistic_base+every_day+gate | 14/26 / 17/26 | 0.538 [0.368, 0.714] | 2.88 | 2.01 | no / no / no | no / no / no |
| risk_logistic_base+every_day+gate+settle | 14/26 / 17/26 | 0.538 [0.353, 0.715] | 2.54 | 2.08 | no / no / yes | no / no / yes |
| risk_logistic_base+every_day+gate+h41 | 14/26 / 17/26 | 0.538 [0.375, 0.714] | 2.69 | 1.93 | no / no / no | yes / no / no |
| risk_logistic_base+every_day+gate+settle+h41 | 14/26 / 17/26 | 0.538 [0.357, 0.714] | 2.23 | 1.93 | no / no / yes | yes / no / yes |
| risk_quantile_skewt_base | 14/26 / 15/26 | 0.538 [0.360, 0.714] | 1.88 | 1.62 | yes / no / no | yes / no / no |
| risk_quantile_skewt_base+settle | 13/26 / 15/26 | 0.500 [0.318, 0.667] | 1.88 | 1.74 | yes / no / yes | yes / no / yes |
| risk_quantile_skewt_base+h41 | 14/26 / 16/26 | 0.538 [0.350, 0.731] | 2.27 | 2.23 | no / no / no | no / no / no |
| risk_quantile_skewt_base+settle+h41 | 15/26 / 16/26 | 0.577 [0.393, 0.750] | 2.27 | 2.23 | no / no / yes | no / no / yes |
| risk_quantile_skewt_base+every_day+gate | 15/26 / 17/26 | 0.577 [0.407, 0.741] | 3.15 | 2.00 | no / no / yes | yes / no / yes |
| risk_quantile_skewt_base+every_day+gate+settle | 12/26 / 16/26 | 0.462 [0.300, 0.632] | 2.31 | 1.87 | no / no / yes | yes / no / yes |
| risk_quantile_skewt_base+every_day+gate+h41 | 13/26 / 18/26 | 0.500 [0.320, 0.679] | 3.19 | 2.32 | no / no / yes | no / no / yes |
| risk_quantile_skewt_base+every_day+gate+settle+h41 | 15/26 / 18/26 | 0.577 [0.405, 0.743] | 2.69 | 2.43 | no / no / yes | no / no / yes |

* **Settlements** move the passers most where the coupon clause now applies. Recall at some lead gains at most one or two onsets
  (`risk_gbm` 13 to 14 of 26, `risk_logistic` 14 to 16), none of the paired differences excludes zero, and the gradient-boosted and skew-t
  gate rows lose recall (for example `risk_quantile_skewt_base+every_day+gate`, 15 to 12).   the tier verdicts that change are in Table 1 (tier 5 is gained by the settle arm of the skew-t passer and of several gate rows, and tier 1 or 3 is lost by
  `risk_logistic+settle` under the weighted rule); the full-rule verdict of no row changes.
* **The H.4.1 per release** moves almost nothing: recall differences are 0 or one onset either way, and the false-alarm ceilings move by a few hundredths,
  with `risk_quantile_skewt_base` the one passer whose ceiling rises above 2 (1.88 to 2.27), so it loses tier 1.
* **2018, 2020 and 2024.** No row flags a 2018 or a 2024 onset under any arm (0 of 4 and 0 of 2). Of the two 2020 onsets, the published
  `risk_gbm+every_day+gate` and `risk_quantile_skewt_base+every_day+gate` flag one; under `+settle` neither does, and under `+h41` only the first
  does (also under both). Every recall gain is in 2019 and 2025.

## The seven coupon-settlement onsets

The seven onsets of [`desk-standard-result.md`](desk-standard-result.md) §2 that settle a coupon and are not calendar risk dates. Cell: the leads
(h) at which the row flags that onset, under the judge's cut-offs (flat rule); `-` if it flags at none. The last column counts onsets flagged at a lead of 2 or more.

| row | 2018-11-15 | 2018-12-28 | 2019-01-15 | 2019-03-15 | 2019-10-15 | 2025-10-15 | 2025-12-26 | warned at h >= 2 |
|---|---|---|---|---|---|---|---|---|
| risk_gbm | - | - | h1 | h1 | h1 | - | h1 | 0 of 7 |
| risk_gbm+settle | - | - | h1 | h1,2,3,4,5 | h1,2,3,4,5 | - | h1,2,3,4,5 | 3 of 7 |
| risk_gbm+settle+h41 | - | - | h1 | h1,2,3,4,5 | h1,2,3,4,5 | - | h1,2,3,4,5 | 3 of 7 |
| risk_gbm_base | - | - | h1 | h1 | h1 | h1 | h1 | 0 of 7 |
| risk_gbm_base+settle | - | - | h1 | h1,2,3,4,5 | h1,2,3,4,5 | h1 | h1,2,3,4,5 | 3 of 7 |
| risk_gbm_base+settle+h41 | - | - | h1 | h1,2,3,4,5 | h1,2,3,4,5 | h1 | h1,2,3,4,5 | 3 of 7 |
| risk_logistic | - | - | h1 | h1 | h1 | - | h1 | 0 of 7 |
| risk_logistic+settle | - | - | h1,2,3,4,5 | h1,2,5 | h1,2,3,4,5 | h2,3,5 | h1,2,3,4,5 | 5 of 7 |
| risk_logistic+settle+h41 | - | - | h1,2,4,5 | h1,2 | h1,2,3,4,5 | h2,3,5 | h1,2,3,4,5 | 5 of 7 |
| risk_logistic_base | - | - | h1 | h1 | h1 | - | h1 | 0 of 7 |
| risk_logistic_base+settle | - | - | h1,2,3,4,5 | h1,2,4,5 | h1,2,3,4,5 | - | h1,3,4,5 | 4 of 7 |
| risk_logistic_base+settle+h41 | - | - | h1,2,3,4 | h1,2,3 | h1,2,3,4,5 | - | h1,2,3,4,5 | 4 of 7 |
| risk_quantile_skewt_base | - | - | h1 | h1 | h1 | - | h1 | 0 of 7 |
| risk_quantile_skewt_base+settle | - | - | h1,2,3,4,5 | h1,3,4,5 | h1,2,3,4,5 | - | h1,2,3,4,5 | 4 of 7 |
| risk_quantile_skewt_base+settle+h41 | - | - | h1,2,3,4,5 | h1,3 | h1,2,3,4,5 | h1 | h1,2,3,4,5 | 4 of 7 |

Under the published declaration none of the seven is warned at a lead of 2 or more by any passer. Under the announcement, three of them are
warned by the gradient-boosted passers (2019-03-15, 2019-10-15, 2025-12-26), and four or five by the logistic and skew-t ones. The H.4.1 reading
changes none of this.

## Not checked, or for Eleonora

* **The announcement instant (12:00)** rests on no published clock time. It does not change any sum at the 16:00 decision. Whether the declaration needs
  a better-evidenced instant is hers.
* **The release calendar** was fetched for holiday and holiday-adjacent weeks; ordinary weeks were spot-checked, not each fetched. A week the Board moved
  for another reason would be missed. 16:30 is the registry's own instant; the Board's pages state a date and no clock time.
* **#539 and #540.** #540 has no pull request. #539 merged while this was scored, and its hurdle variants (five parents, four variants) are not re-scored here: that is 300 rolling backtests and 60 judge candidates on top of this page's, and is queued as #556, to start once this has merged.
* **Turning either reading on in the published declaration** needs a change to `metadata/sources.json`, which the final-test pre-registration freezes by its bytes
  (owner-attested, #256). This pull request does not make it; no "Publish?" issue is opened because the readings are off and no published figure moves.
* The scoring script was written before its tests (the dating modules were test-first); the tests pin its inputs and its risk-date rule.
* 26 onsets; most recall differences have intervals that include zero, and no multiple-testing correction runs over forty rows and two rules.
* The +10 bp verdicts, the 2026 tiers and the confirmation window are not looked at.

## Note of 12 October 2026 (#604): the sign of Table 5

Table 5 of `evidence/announcement-dating/compare_*.md` (the paired Brier difference against the published row) said "negative favours the
arm". It is the other way round: the statistic is the published row's squared error minus the arm's (`pressure_judge._paired_vectors`), so
**positive favours the arm**. The two files were regenerated by `announcement_dating_rescore.py compare` and differ from the earlier files in the
header line only; no figure moved. No sentence on this page reads which arm is better from Table 5 (the readings above are of recall, false
alarms and the tier verdicts), so none inverts. Read the right way, the `+h41` and `+settle+h41` rows at h = 1 (differences of −0.0002 to −0.0003, intervals
covering zero) are, in point estimate, marginally worse than the published row on Brier, not better.
