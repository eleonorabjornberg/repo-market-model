# The hurdle variants re-scored with settlements dated from the announcement and the H.4.1 read per release (#556, of #541)

A scratch measurement under the pressure-day judge. It writes nothing into `docs/runs/`, moves no published figure, and reads no day after
2025-12-31 (`docs/decisions/lockbox.md`; the script refuses a later panel). The live record and pin do not move. Both readings are **off in
every published declaration** (see [`settlement-h41-dating-result.md`](settlement-h41-dating-result.md)). The scoring is declared in
`metadata/hurdle_dating.json`, with the 60 judge candidate files `metadata/pressure_judge/candidates/<parent><variant>{+settle,+h41,+settle+h41}.json`,
all committed before the first forecast was fitted. Nothing is proposed for publication, so no "Publish?" issue is opened.

The rows are the twenty hurdle variants of [`risk-date-hurdle-result.md`](risk-date-hurdle-result.md) (#539: five risk-date passers x four variants), each under four
arms: `published` (re-run here, because #539's evidence keeps the pairing tables and not the forecasts), `settle`, `h41` and `both`. Each arm's row is
paired with the same variant under `published`.

## Which inputs each arm changes, read off the scores

A risk date keeps the parent's forecast; any other day is served the every-day hazard. Table 5 of `evidence/hurdle-dating/compare-*.md` counts, for each arm
row and horizon, the scored days on which its +5 bp forecast differs from the published row (by more than 1e-9), split by the day's status.

* **`settle`** moves exactly the days it should: at h = 1 nothing (the columns are the published panel's, row for row); at h >= 2 every difference is on a risk
  day, and every coupon-settlement day (124 at h = 2 for the gradient-boosted passers) becomes a risk day, so it is served the parent's forecast instead of the hazard.
  No ordinary day differs.
* **`h41`** moves the risk days only (the parent's reserve inputs); for example 377 of 404 risk days at h = 1. **No day outside the risk days differs, for any
  variant, including the two `state` variants** whose hazard reads `reserve_scarcity_state`: the state's as-of value is unchanged on every
  ordinary day. This is not what the directive expected ("`+h41` moves only the state variants"). The cause was not traced; the state is assembled from WRESBAL,
  the H.8 total assets and the ON RRP take-up and is observable once all three are, so a conjecture is that the H.8 read, whose release lag is longer, binds and
  the earlier H.4.1 print never decides the state. That is a conjecture, not a finding.
* **`both`** is the union: the `settle` differences plus the `h41` ones on risk days.

## Result

No row passes the full rule under either miss rule, under any arm, and no full-rule verdict changes (`evidence/hurdle-dating/summary.md`, Table 1 for every row; `judge-*.md`, the
judge's reports with tier 1 pooled and per lead, tiers 3 and 5, split by regime and day type).

* **Recall.** Of 237 recall-difference cells per rule (arm rows x cells), 2 under the flat rule and 1 under the weighted rule have a 90% interval that excludes zero, none
  of them the pooled flat cell, and the three that do are in the `+settle` arm (flat: `risk_logistic_base+hurdle_platt+settle` and `risk_logistic_base+hurdle_isotonic+settle` on ordinary days,
  +0.25; weighted: `risk_logistic_base+hurdle_isotonic+settle` pooled, +0.154). With 237 cells per rule that is about what chance gives. Pooled recall moves by at most four onsets of 26, both ways.
* **2018, 2020 and 2024.** No variant flags a 2018, 2020 or 2024 onset under any arm (0 of 4, 0 of 2, 0 of 2), as for the published rows.
* **The seven coupon-settlement onsets** (Table 4 of `compare-*.md`). The published variants warn at most one at a lead of 2 or more. `+settle` lets the coupon clause apply at h >= 2:
  the gradient-boosted and skew-t variants then warn 3 of 7 at a lead of 2 or more (the logistic ones 2 or 3), against 0 or 1. `+h41` does not move this.
* **Brier score and log loss against the published row** (Table 6, all days, +5 bp, 90% interval, 20 variants x 5 horizons = 100 pairs per arm). `+settle`: the Brier
  difference favours the arm in 70 of 100 and goes against it in none (log loss: 54 favour, 5 against); the gain is at h >= 2 and is of the order of 0.003 to 0.009, and is on
  coupon-settlement days that the published declaration serves the hazard. `+settle+h41` is the same (68 / 0; log loss 52 / 4). `+h41` alone: 0 favour, 6 against in Brier (5 in
  log loss), each of the order of -0.001.

Reading: the announcement dating improves the calibration of the hurdle variants on coupon-settlement days at h >= 2 (a better Brier score, a few more of the seven coupon onsets warned), and
moves neither the pass verdict nor the pooled recall; the H.4.1 reading moves the risk-day forecasts a little and no ordinary day.

## Reproduce

Published panel `4ddc3882…` (`verify-panel` clean, unchanged: neither reading edits a panel column); scratch panel as for #428, #532 and #541
(`pressure_v1_1.py panel`, then `measurement_fields.py panel`). `/opt/rmm-venv` (numpy 2.4.6, scikit-learn 1.9.1), `OMP_NUM_THREADS=1`.

```
PYTHONPATH=src python3 scripts/hurdle_dating_rescore.py declare      # already committed; shown for the record
for arm in published settle h41 both; for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/hurdle_dating_rescore.py run --arm $arm --panel AUG2.csv --published PUBLISHED.csv --horizon $h --output OUT/hd_${arm}_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --output OUT/bench_h$h.json
for r in weighted unweighted: PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule $r --output OUT/judge_$r.json --markdown OUT/judge_$r.md OUT/bench_h?.json OUT/hd_*_h?.json
PYTHONPATH=src python3 scripts/hurdle_dating_rescore.py summary --flat OUT/judge_unweighted.json --weighted OUT/judge_weighted.json --output OUT/summary.md
for r in weighted unweighted: PYTHONPATH=src python3 scripts/hurdle_dating_rescore.py compare --rule $r --panel PUBLISHED.csv --output OUT/compare_$r.json --markdown OUT/compare_$r.md OUT/bench_h?.json OUT/hd_*_h?.json
```

Evidence: `docs/pivot/evidence/hurdle-dating/` (`summary.md`, the judge's reports, and the pairing of every arm row against its published row).

## Not checked, or for Eleonora

* **Why `h41` leaves the `state` hazard unmoved** was not traced (conjecture above). If the state should move under the per-release reading, the state's own dating is the place to look.
* **The announcement instant (12:00)** is unverified, as on the #541 page.
* **#540** has no merged branch; it is not scored here.
* The sign convention of Table 6 here is the hurdle page's: a positive difference favours the arm. The #541 page's Table 5 note says the opposite for its own table; not looked at.
* 26 onsets; no multiple-testing correction over 60 arm rows and two rules; the +10 bp verdicts, the 2026 tiers and the confirmation window are not looked at.
* The scoring script reuses the machinery of `announcement_dating_rescore.py` and `risk_date_hurdle.py`; the tests pin its declaration, candidates and pairs, not a fit.

## Note of 12 October 2026 (#604): the #541 page's Table 5

The "Not checked" item above, that the #541 page's Table 5 note says the opposite sign convention, is resolved: the #541 header was wrong and this
page's Table 6 was right (a positive difference favours the arm). The #541 files were corrected in #604 (see the note at the end of
`settlement-h41-dating-result.md`). Nothing on this page changes.
