# Six construction gaps in the leading risk-date models (#485)

A sizing, not a candidate. It writes nothing into `docs/runs/`, changes no declared candidate and moves no published figure
(`docs/decisions/lockbox.md`: scored days 2018-06-29 to 2025-12-31 only; the confirmation window and the blind tier are not
looked at). The five models read are the tier-1 passers of the risk-date severity track (#428, `risk-date-severity-result.md`):
`risk_gbm`, `risk_gbm_base`, `risk_logistic`, `risk_logistic_base` and `risk_quantile_skewt_base`. Each gap is confirmed or
refuted against the code (read at `c14ab58`, the directive's base, and checked again at `be75ea0`; `ml.py` did not move, the judge's line numbers below are those of `be75ea0`), then sized by refitting the same model with that one thing changed, on the same folds and
the same inputs, under the judge's own cut-off rule (`pressure_judge.choose_cutoffs`). A reading is "+5 bp onsets flagged / onsets,
false alarms per onset", as in `risk-date-severity-result.md`. There is no interval: with 26 or 27 onsets, one onset is about four
percentage points, and a cell that moves by one or two onsets is inside what a change of fold or cut-off already moves.

## Reproduce

Published panel `4ddc3882…`; scratch panel as for #428. Every command is in the header of `scripts/construction_gaps_485.py`.

```
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
for h in 1 2 3 4 5; for v in declared onset_label calendar_bd calendar_wide (bill_days at h = 1 only):
    PYTHONPATH=src python3 scripts/construction_gaps_485.py run --panel AUG2.csv --published PUBLISHED.csv \
        --variant $v --horizon $h --candidate $c --output OUT/${v}_${c}_h$h.json
PYTHONPATH=src python3 scripts/construction_gaps_485.py report --panel PUBLISHED.csv --output OUT/report.json OUT/*.json
PYTHONPATH=src python3 scripts/construction_gaps_485.py onsets --panel AUG2.csv --output OUT/onsets.json
PYTHONPATH=src python3 scripts/construction_gaps_485.py tables --report OUT/report.json --onsets OUT/onsets.json \
    --output OUT/tables.md OUT/declared_*.json
PYTHONPATH=src python3 scripts/construction_gaps_485.py leaf-floor
```

Evidence: `docs/pivot/evidence/construction-gaps/` (`report.json` every reading, by year; `tables.md` the tables below and the
per-refit fits; `onsets.json` every onset with its calendar, settlement and rate facts and March 2020 day by day; `h41_20201228.*`
the fetched H.4.1 page, its checksum and the two lines read from it; `leaf_floor.json`).

**The control.** `declared` is the declared model run through the variant script. Its forecasts equal those of the declared
`scripts/risk_date_severity.py run` exactly, for all five models at all five horizons (`construction_gaps_485.py check`, no
difference in any forecast), so a difference below is the one change and not a different model. The scored days, the folds and the
flags are the declared ones: 27 onsets at h = 1 and 26 at h = 2 to 5.

## Summary

| # | gap | confirmed? | size on the five passers |
|---|---|---|---|
| 1 | trained on all pressure days, judged on onsets | yes, as described | no consistent direction; the GBMs flag fewer false alarms at h = 1 (1.30 → 0.56, 1.44 → 0.67) and one or two fewer onsets |
| 2 | bill-settlement days are never risk dates | yes; the four named onsets are forecast exactly 0 | larger risk set (404 → 1035 of 1873 days at h = 1) and fewer onsets flagged (13 → 8 to 11), about the same false alarms |
| 3 | month-end in calendar days, no year- or quarter-end window | yes; the four named onsets lie outside the set at h ≥ 2 | the set grows (277 → 385 or 445 days), onsets on it 13 → 14 or 17; flagged onsets fall in most cells and rise by at most one |
| 4 | early fits too small | yes | the first refit has 12 pairs and one event at h = 1; the GBM is a constant on 6 of 18 refits through 2019 at h = 1 and on 10 of 18 at h ≥ 2 |
| 5 | weekly averages read as Wednesday levels | yes; both series are week averages | a description and a staleness error; no leak |
| 6 | emergency-cut onsets | in part; 2020-03-16 is not an onset | one of two 2020 onsets is cut mechanics, the other funding stress |

## 1. Trained on all pressure days, judged on onsets

**Confirmed.** `ml.py:6025` labels every risk-date pair `spread > tau`. `pressure_judge.select_cutoff` (`:957-959`) counts only an
onset as a catch and only a day that is not a pressure day as a false alarm, so a continuation day is neither. In the scored days
there are 140 days above +5 bp and 27 of them are onsets (19%; the "about 80%" continuation share holds). On the risk dates at h = 1
it is 58 and 21 (36%); at +10 bp it is 61 and 25 (41%). At the last refit of `risk_gbm_base` (h = 1) the training window holds
55 pressure labels among 413 risk-date pairs, of which 21 are onsets.

**Sensitivity.** `onset_label`: the logistic and the GBM are fitted to "an onset" (`ml._onset_labels`, the rule of `pressure.onsets`,
the same label as the onset classifier of #409), on the same risk dates. The skew-t quantile fits the spread itself and has no label
to change, so it is not run.

| model | h=1 declared | h=1 onset label | h=2 declared | h=2 onset label | h=5 declared | h=5 onset label |
|---|---|---|---|---|---|---|
| risk_gbm | 13/27, 1.30 | 12/27, 0.56 | 8/26, 1.08 | 5/26, 1.15 | 7/26, 1.04 | 5/26, 1.08 |
| risk_gbm_base | 13/27, 1.44 | 11/27, 0.67 | 8/26, 0.96 | 7/26, 1.19 | 7/26, 1.08 | 5/26, 1.15 |
| risk_logistic | 13/27, 1.78 | 13/27, 1.67 | 7/26, 1.00 | 6/26, 1.00 | 8/26, 1.42 | 8/26, 1.27 |
| risk_logistic_base | 13/27, 1.70 | 13/27, 1.56 | 6/26, 1.00 | 5/26, 1.00 | 8/26, 1.15 | 8/26, 1.35 |

Horizons 3 and 4 are in `tables.md`. By year at h = 1, the onsets warned are the same except 2019 (10 of 13 to 9 of 13 for
`risk_gbm_base`) and 2025 (3 of 5 to 2 of 5 for the GBMs); all five models warn none of the five 2018 onsets and none of the 2020
or 2024 ones, with either label. Reading: the onset label makes the GBM more selective at h = 1 (fewer false alarms, one or two
fewer onsets) and moves the logistic by no more than that; at h ≥ 2 it loses one to three onsets for the GBMs and the false alarms
move both ways (by −0.35 to +0.23 per onset). It does not rescue the onsets the risk set never reaches (gap 2 and 3). The gap is real, its size is small and its
sign mixed.

## 2. Bill-settlement days are never risk dates

**Confirmed.** `_RiskDateDesign.member` (`ml.py:5940-5945`) reads only `treasury_settlement_coupons`, and the judge's
`_scheduled_risk_date` (`pressure_judge.py:2191-2201`) the same. The declared forecast is exactly 0 at both thresholds, at every
horizon and for all five models, on 2019-05-28, 2019-06-25, 2019-08-13 and 2024-12-26 (50 forecasts read on each, the largest 0;
`tables.md`, "Gap 2"). The same holds for 2020-03-12 (bills 78) and 2020-03-04 (no settlement at all). Six of the 27 onsets have no
coupon settlement; five of them have a bill settlement of 75 to 266 (USD billions), and a bill rule cannot reach 2020-03-04.

**Sensitivity.** `bill_days`: at h = 1 a day with any settlement is a risk date. A settlement is public one business day ahead and
no earlier (`information-set.md`), so nothing moves at h ≥ 2.

| model | h=1 declared | h=1 bill days |
|---|---|---|
| risk_gbm | 13/27, 1.30 | 9/27, 1.22 |
| risk_gbm_base | 13/27, 1.44 | 11/27, 1.44 |
| risk_logistic | 13/27, 1.78 | 9/27, 1.93 |
| risk_logistic_base | 13/27, 1.70 | 8/27, 1.56 |
| risk_quantile_skewt_base | 13/27, 1.81 | 9/27, 1.63 |

The set grows from 404 to 1035 of 1873 days, because some settlement falls on more than half of all days. Two of five models then warn
2019-05-28 and two warn 2019-06-25; none warns 2019-08-13 or 2024-12-26, and the declared warning of 2025-12-26 (5 of 5) falls to
2 of 5. The extra warnings are paid for by the dilution: a model fitted on about a fifth of the days is fitted on more than half of them. Two things limit the reading. For the skew-t, 84 of the added days carry a probability of exactly 0 (the law's
tail), so the added days are partly inert; for the models with the new inputs, one added day (2019-06-04) is not served because
`sofr_p75_iorb_bps` has a hole on 2019-05-31, the day it reads. Whether a settlement above some size, rather than any settlement,
is the right clause is a rule Eleonora would have to set; this sizing did not choose one.

## 3. Month-end in calendar days; no year-end or quarter-end window

**Confirmed.** `EvaluationSplits.day_type` uses `days_to_month_end <= 2` calendar days (`evaluation_splits.py:125`);
`reporting_day_type` uses the last two business days (`:131-140`, "a v2 candidate"); `data.quarter_end_window` exists (the quarter's
last business day and two either side, #140) but `_CALENDAR_INPUTS` (`ml.py:4164`) does not include it.

At h ≥ 2 the set is the three calendar types, and 13 of the 26 onsets lie on it. The onsets outside it:

| onset | why it is outside | what would reach it |
|---|---|---|
| 2018-12-28 | 3 calendar days from month-end; the second-last business day of December | last two business days; the quarter-end window |
| 2019-06-25, 2024-12-26, 2025-12-26 | 4th-last business day of a quarter-end month (5 calendar days) | neither; only a wider window (last five business days of March, June, September, December) |
| 2019-05-28 | 4th-last business day of May | neither |
| 2018-11-15, 2019-01-15, 2019-03-15, 2019-10-15, 2025-10-15 | mid-month coupon settlement, public only at h = 1 | a settlement clause (h = 1 only) |
| 2019-08-13, 2020-03-04, 2020-03-12 | ordinary days (gap 2 and 6) | nothing in the calendar |

The directive's four examples are right: 2018-12-28 is outside the declared set but inside both the business-day month-end and the
quarter-end window; 2024-12-26, 2025-12-26 and 2019-06-25 are each the fourth-last business day of a quarter-end month, which the
±2-business-day window does not reach.

**Sensitivity.** `calendar_bd`: also a risk date on the last two business days of any month and inside the quarter-end window.
`calendar_wide`: and the last five business days of March, June, September and December (a size chosen after the onsets above were
listed, so a sizing only).

| model | h=2 declared | h=2 business-day | h=2 wide | h=5 declared | h=5 business-day | h=5 wide |
|---|---|---|---|---|---|---|
| risk_gbm | 8/26, 1.08 | 6/26, 0.92 | 6/26, 1.19 | 7/26, 1.04 | 6/26, 1.15 | 8/26, 1.23 |
| risk_gbm_base | 8/26, 0.96 | 5/26, 1.15 | 6/26, 1.50 | 7/26, 1.08 | 6/26, 1.19 | 7/26, 1.35 |
| risk_logistic | 7/26, 1.00 | 5/26, 0.73 | 3/26, 0.92 | 8/26, 1.42 | 5/26, 1.04 | 5/26, 1.12 |
| risk_logistic_base | 6/26, 1.00 | 4/26, 0.81 | 5/26, 1.04 | 8/26, 1.15 | 3/26, 0.88 | 5/26, 0.88 |
| risk_quantile_skewt_base | 9/26, 1.65 | 5/26, 1.12 | 3/26, 0.50 | 9/26, 1.04 | 7/26, 1.08 | 7/26, 1.15 |

At h ≥ 2 the set grows from 277 to 385 days (business-day) or 445 (wide), and the onsets on it from 13 to 14 or 17. The extra onsets
are hardly warned: under the business-day set none of the added onsets is warned by any model at h = 2, and under the wide set one
model warns 2019-06-25 and one 2025-12-26; the onsets the declared model did warn are warned less often. At h = 1, where the coupon clause already
covers 2018-12-28 and 2025-12-26, the business-day set moves the five models between 9 and 13 onsets, and the wide set warns
2019-06-25 in all five (the onset it newly reaches at h = 1) and holds recall at 10 to 14. So a wider calendar window enlarges what the
model can in principle reach, but on this sample it raises recall by at most one onset (three models at h = 1 under the wide set) and
lowers it in most cells. The
horizons 3 and 4 and the by-year tables are in `tables.md`.

## 4. Early fits too small

**Confirmed.** The first scored day is 2018-06-27 (served by the refit with 61 training rows). `tables.md`, "Gap 4", lists every refit
through 2019 for `risk_gbm_base` at h = 1 and h = 5 and summarises the rest.

* The first refit has **12** risk-date training pairs at h = 1 (7 at h = 5), with **1** event at +5 bp and **0** at +10 bp. By
  November 2018 it is 33 pairs and 4 events at +5 bp, 1 at +10 bp (22 pairs and 2 events at h = 5).
* `min_samples_leaf = 20` (`ml.py:4056`) means the gradient-boosted classifier cannot split a training set of fewer than 40
  (`leaf_floor.json`: 39 pairs give one probability on 50 new rows, 40 give eight). On a smaller set `risk_gbm` and `risk_gbm_base` are
  a constant: the base rate of the training pairs. That is 6 of the 18 refits through 2019 at h = 1 (the first refit with 40 pairs is
  the one served from 2018-12-31) and 10 of 18 at h = 2 to 5 (the first is the one served from 2019-05-02). The logistic and the
  skew-t have no leaf floor but are fitted on the same few pairs.
* The single-class fallback (`ml.py:6026-6027`) fires only when a threshold has no event in the window: the +10 bp fit of the first
  refit, at every horizon and in every variant run here. At +5 bp it never fires.
* All five of the 2018 onsets are unwarned by every model at h = 1 (and the four of 2018 at h ≥ 2), as are the two 2020 onsets. That
  is consistent with fits on one to four events and with a cut-off chosen on a window that has few onsets (`select_cutoff` returns no
  flag when the window has none); it is a coincidence of timing as much as a finding, and this sizing did not separate the two.

## 5. Weekly averages read as Wednesday levels

**Confirmed, and the registry is right.** `metadata/sources_measurement.json` checks WTREGEN as the 7-calendar-day average of the daily
closing balances ending each Wednesday (451 Wednesdays, to within 0.0009 billion). WRESBAL is the same kind. The H.4.1 of 28 December
2020 (`www.federalreserve.gov/releases/h41/20201228/`, fetched in this run; `h41_20201228.fetch.json` has its checksum) gives each
line of Table 1 in two columns, "Averages of daily figures, week ended Dec 23, 2020" and "Wednesday Dec 23, 2020":

| line | week average | Wednesday level | the registry's 2020-12-23 value |
|---|---|---|---|
| Reserve balances with Federal Reserve Banks | 3,143,041 | 3,177,306 | WRESBAL 3143041 |
| U.S. Treasury, General Account | 1,602,407 | 1,583,308 | WTREGEN 1602407 |

Both published series are the week average (Thursday to Wednesday), dated to the Wednesday that closes the week and public in the
release of the following Thursday. They are not Wednesday levels. `WLRRAOL` is: `metadata/sources.json` says so, and its note is
right. The consequence for the models is small and one-sided: the average is complete on its Wednesday and public five days later, so
nothing leaks. But a value read "6 to 12 days old" describes its Wednesday, and its centre of mass is about three days earlier, so
the inputs are staler than the documents say and are smoother than a level.

**To correct** (documents and comments that call a weekly average a Wednesday level; none is changed here, to keep this diagnostic
to its scope): `docs/diagnosis-exceedance-flattening.md` lines 228-229; `src/repo_model/asof.py` lines 573-574 and 850-851;
`tests/test_asof.py` line 222; and `docs/decisions/information-set.md` line 18 ("Each Wednesday level is carried"). The H.8's `bank_total_assets`
(the other leg of the scarcity ratio) is a separate series whose definition was not checked.

## 6. Emergency-cut onsets

**In part.** `fed_iorb_announcements` is in the registry but not in any risk-date input (`metadata/risk_date_severity.json` lists
neither `iorb_announced_change_bps` nor `iorb_days_to_announced_change`). The 2020 onsets are 2020-03-04 and 2020-03-12 only.
2020-03-16 is not an onset: it is two panel days after 2020-03-12, inside the five quiet days that `pressure.onsets` requires, so it
is a continuation day of the 12 March episode. Day by day (`onsets.json`, `march_2020`; SOFR and IORB in percent, spread and the two
distribution measures in basis points above IORB):

| day | SOFR | IORB | spread | SOFR 75th | SOFR 99th | announced IORB change | |
|---|---|---|---|---|---|---|---|
| 2020-03-03 | 1.64 | 1.60 | +4 | +11 | +21 | 0 | |
| 2020-03-04 | 1.23 | 1.10 | +13 | +18 | +27 | −50 | onset |
| 2020-03-05 | 1.12 | 1.10 | +2 | +7 | +15 | 0 | |
| 2020-03-11 | 1.15 | 1.10 | +5 | +10 | +18 | 0 | |
| 2020-03-12 | 1.20 | 1.10 | +10 | +15 | +32 | 0 | onset |
| 2020-03-13 | 1.10 | 1.10 | 0 | +5 | +12 | 0 | |
| 2020-03-16 | 0.26 | 0.10 | +16 | +25 | +190 | 0 | continuation |
| 2020-03-17 | 0.54 | 0.10 | +44 | +64 | +90 | 0 | continuation |

* **2020-03-04: rate-cut mechanics.** IORB fell 50 bp that day (announced 10:00 on 3 March, before the 16:00 decision, so the h = 1
  forecast could have read it; the field is `-50` on the row) and SOFR fell 41. The spread is +13 against +4 the day before, and +2
  the day after. It is the administered rate moving faster than the market for one day, not a scarcity signal. No settlement is
  scheduled that day.
* **2020-03-12: funding stress.** No IORB change (it is unchanged since 4 March); the spread opens to +10 and the 99th percentile to
  +32 bp above IORB, with no rate move to explain either; it closes to 0 the next day.
* **2020-03-16 (not an onset)** is both: the 100 bp emergency cut was announced on Sunday 15 March at 17:00 and is invisible to any
  forecast made on the Friday (`announced_iorb.py` keys it on announcement time), SOFR fell 84 bp against IORB's 100, and the 99th
  percentile is 190 bp above IORB. The next day's +44 bp is stress.

So of the two 2020 onsets, one is the cut and one is stress. A cut announced a day ahead would be known to an h = 1 forecast; a Sunday
emergency cut would not, at any horizon. Neither onset is on a risk date, so the declared models forecast exactly 0 on both.

## 7. What each finding implies

*Model changes, for a later declared candidate* (each would be declared and scored under the judge before it is believed):

* Train the classifiers on the onset label, or on a mix, with the risk dates unchanged (gap 1). The reading above says do not expect
  a gain; it is the cut-off, not the label, that is tied to onsets.
* Add `iorb_announced_change_bps` as an h = 1 input, or an h = 1 risk-date clause for a day with an announced change (gap 6). It would
  have covered 2020-03-04 and nothing else in the sample.
* Start the models later, or pool the first year with a prior, so that no fit is a constant (gap 4), or give the GBM a leaf floor that
  scales with the pairs. The first six to ten refits through 2019 are constants for the GBMs.
* Serve an added risk date whose input has a hole by the model without that input, rather than as 0 (gaps 2 and 3, `sofr_p75_iorb_bps`
  on 2019-05-31).

*Rule or data-meaning changes, for Eleonora:*

* Whether a bill settlement, or a bill or coupon settlement above a size, is a risk date at h = 1 (gap 2). The judge's own
  `risky_dates` tier shares the coupon-only clause (`pressure_judge.py:2191-2201`), so that tier would move with it.
* Whether `reporting_day_type` (last two business days) replaces `day_type`'s calendar-day month-end (gap 3). The code calls it "a v2
  candidate"; `day_type` is part of the frozen model and of the scorecaster's window, so this is a decision about what is frozen.
* Whether `quarter_end_window` joins the calendar inputs, and whether the year-end and quarter-end window is wider than ±2 business
  days. The window was decided under #140; the four unreached onsets sit one to two business days outside it.
* Correcting the documents and comments that call WRESBAL and WTREGEN Wednesday levels (gap 5), and whether "hours observable" should
  count from the middle of the averaging week.

## Not checked

* No interval is computed on any sensitivity cell; the cells are counts of 26 or 27 onsets.
* The sizing is at +5 bp, the judge's primary threshold. The +10 bp event counts are reported only for the early fits.
* No variant is scored on a locked day, and none is a candidate: nothing is declared, and no variant was selected on what it showed.
* The horizons 3 and 4 and the skew-t's added-day behaviour are in the evidence files and not discussed above.
* The H.8 `bank_total_assets` definition, the DTS-based TGA check (it is the registry's) and the daily WRESBAL-like series were not re-fetched.
* Whether the dilution in gaps 2 and 3 would shrink if the added risk dates were modelled apart from the declared ones (a separate
  fit, or a flag input) was not tried.
