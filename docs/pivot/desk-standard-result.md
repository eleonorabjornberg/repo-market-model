# A desk standard for information use: when each input was truly public (#481)

A scratch diagnostic. It changes no model, declaration, panel column or published figure, writes nothing into `docs/runs/`,
and reads no day after 2025-12-31 (`docs/decisions/lockbox.md`). Every change to an availability declaration it points to is
listed for Eleonora at the end and not made. The code is `scripts/desk_standard_diagnostic.py`, the numbers are in
`docs/pivot/evidence/desk-standard/desk_standard.json`, `tests/test_desk_standard_diagnostic.py` pins them, and the primary
pages the timeline cites are saved as text, with the checksum of each page read, under
`docs/pivot/evidence/desk-standard/sources/`. They were fetched on 10 October 2026, one plain request each.

## Result in one paragraph

Our availability rules are later than the primary schedules in three places that matter, and in none of the secured-rate
cases. (1) A Treasury settlement date and its offering amount are fixed at the auction announcement, 4 to 5 panel days before
a bill settles and 5 to 14 before a coupon settles; the declaration prices them at 15:00 the panel day before, so the sentence
"a settlement is public one business day ahead and not earlier" describes the declaration and not the publication. (2) The
H.4.1 is read 2 panel days after the Thursday it prints on in an ordinary week, because the registry carries a constant five
calendar days. (3) The Desk's reverse-repo and repo-operation results are declared 1 panel day later than the day they were
written, an assumption the Desk neither confirms nor denies. A daily proxy for the weekly reserves, built only from public
daily series, does not track them. The two structural blind spots are exact: the five tier-1 passers cannot flag 6 of the 26
onsets at any horizon, and at h of 2 or more at most 12 of 26 at one horizon. The 27th onset is a scored-window start, and
the nowcast of #445 has no alignment, unit or availability defect, but has an estimator defect that explains most of its loss.

## Reproduce

Published panel `4ddc3882…`, rebuilt from the tracked fixtures (`docs/pivot/next-session.md`, `verify-panel` clean).

```
PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
for h in 1 2 3 4 5: PYTHONPATH=src /opt/rmm-venv/bin/python scripts/pressure_judge.py forecasts --panel PUB.csv --horizon $h --output OUT/bench_h$h.json
PYTHONPATH=src python3 scripts/desk_standard_diagnostic.py --panel PUB.csv --bench 'OUT/bench_h{h}.json' --output docs/pivot/evidence/desk-standard/desk_standard.json
```

The benchmark files are used for the scored days only. The script cuts every panel at 2025-12-31 on load, and refuses a
benchmark file with a scored day after it (`LookAheadError`).

## 1. The desk information timeline

For each input, the earliest public time the primary source states, against the time our declaration uses. "Later by" is
the number of panel days between the first 16:00 decision that can read the value under the true time and the first that
reads it under our declaration, over every reference day from 2018-04-03 to 2025-12-31 (a value public at exactly 16:00
is read by that day's decision, the registry's own `<=` test). A value public before 16:00 on the same day it is read at
a 16:00 decision costs nothing, so the secured rates, 15:00 against 08:00, are not late.

| Input | Ours | Earliest public time, and source | Later by (panel days) |
|---|---|---|---|
| SOFR, TGCR, BGCR | 15:00, 1 business day after the date | about 08:00 ET the next business day; revisable at about 14:30 ([NY Fed SOFR page](evidence/desk-standard/sources/nyfed_sofr_page.txt)) | 0 |
| EFFR | 15:00 next business day (`nyfed_effr`); 16:15 on the Board's copy | about 09:00 ET the next business day ([NY Fed reference-rates page](evidence/desk-standard/sources/nyfed_reference_rates_info.txt)) | 0 |
| ON RRP results | 16:00, next business day | same day. The Desk states **no** time ([page](evidence/desk-standard/sources/nyfed_repo_reverse_repo_operations.txt)); the operation closes at 13:15 and 1985 of 1997 operation days were last written by 15:00 (#445) | **1**, inferred |
| Standing repo facility and repo operations | 16:00, next business day | same day; no time stated; `lastUpdated` a median 0.7 minutes after the close (#442) | **1**, inferred |
| Primary dealer statistics | 16:30, 6 business days after the Wednesday | Thursdays at about 16:15, the previous week's statistics ([NY Fed](evidence/desk-standard/sources/nyfed_primary_dealer_statistics.txt)) | 0 |
| H.4.1: reserves, TGA, reverse repo | 16:30, 5 calendar days after the Wednesday | Thursdays, generally 16:30; shifted to the next business day after a federal holiday ([Board](evidence/desk-standard/sources/fed_h41_release_page.txt)) | **2** on 321 of 396 Wednesdays, 1 on the other 75 |
| Daily Treasury Statement, TGA | 16:30, next business day | 16:00 the next business day (the registry's own provenance; Fiscal Data was not reachable on 10 October 2026, so not re-read) | 1 only if a value public at exactly 16:00 counts at a 16:00 decision |
| Treasury bill rates | 16:30, same date | quotes at about 15:30; the H.15 bulk file 16:30; no earlier posting shown | 0 |
| Treasury auction announcements: settlement date and offering amount | 15:00, the panel day before the settlement | at the announcement: bills Tuesday or Thursday before an issue the following Tuesday or Thursday; coupons in the half month before the auction ([schedule](evidence/desk-standard/sources/treasury_auction_schedule.txt), [how auctions work](evidence/desk-standard/sources/treasury_how_auctions_work.txt)); measured in section 2 | **3 to 4** (bills), **4 to 13** (coupons) |
| Treasury auction results and settlement amounts | 15:00, the panel day before the settlement | after the auction closes, on the auction date, which is 2 to 4 panel days before a bill settles; no clock time is stated (31 CFR 356.23(a), as the registry records) | 1 to 3 |
| OFR tri-party and GCF | 16:00, 2 business days | not established: the monitor is "refreshed daily" and states no time ([OFR](evidence/desk-standard/sources/ofr_short_term_funding_monitor.txt)); if next morning like the NY Fed's own tri-party rates, ours is 1 later | unknown, up to 1 |
| Tax-date and quarter-end calendars | always known | statutory or calendar dates, known in advance | 0 |
| IORB announcements | scheduled, one panel day ahead | the FOMC implementation note, before the effective date (`docs/decisions/iorb-availability.md`) | 0 |

Treasury announcement times are not shown to be before 16:00 by any document read, so section 2 gives both readings.

## 2. Settlements

The statement in `docs/pivot/risk-date-severity-result.md`, "a settlement is public one business day ahead and not earlier",
is not what Treasury's schedules say. It comes from `docs/decisions/information-set.md` rule 2: settlements are dated from
the auction results time, and the registry's declared instant (`treasury_auctions.scheduled_availability`) is 15:00 on the
panel day before, a floor taken from the auction data ("Treasury publishes no results time"). That is a conservative
declaration of the results, not a publication schedule: the announcement fixes the security, the offering amount, the
auction date and the issue date, and the schedule page gives the day of the week or month for every term.

Measured on the tracked auction snapshot, settlement dates from 2018-04-03 to 2025-12-31, leads in panel days from the
announcement's own day to the settlement (an announcement is read the day it is made):

| | settlement dates | lead of the first announcement | lead of the last announcement (amount complete) | share with a lead of 2 or more |
|---|---|---|---|---|
| bills | 793 | 4 for 155, 5 for 621; 6 to 7 for 3; 1 to 3 for 14 (cash management bills and holiday shifts) | 3 for 39, 4 for 154, 5 for 579; 1 to 2 for 19 | 0.997 |
| coupons (notes and bonds, including TIPS and FRNs) | 251 | 5 to 14 for 246; 1 to 3 for 5 | 5 to 12 for 245; 1 to 4 for 6 | 0.992 |

The auction itself, whose results the registry dates the settlement from, is also 2 or more panel days before settlement
for the last auction of 767 of 793 bill dates and 249 of 251 coupon dates. So the one-day floor is not binding even on
the results reading.

**The 26 onsets on a settlement date known at lead 2 to 5.** Onsets are the 26 scored at every horizon. "Known" is the
announcement of any auction settling on the day, read the day it is made; "next day" reads it only from the next panel day.
Under the declaration the count is 0 at every lead from 2 to 5 (and the same as the announced reading at lead 1).

| lead (h) | declared | any settlement, same day | any, next day | coupon, same day | coupon, next day | bill, same day | bill, next day |
|---|---|---|---|---|---|---|---|
| 2 | 0 | 25 | 25 | 20 | 20 | 13 | 13 |
| 3 | 0 | 25 | 25 | 20 | 20 | 13 | 13 |
| 4 | 0 | 25 | 23 | 20 | 20 | 13 | 9 |
| 5 | 0 | 23 | 18 | 20 | 18 | 9 | 0 |

Every onset but 2020-03-04 settles a bill or a note. A bill settles on most Tuesdays and Thursdays, so "any" is not
selective; the coupon column is. Seven of the 20 onsets on a coupon settlement are not already calendar risk dates
(2018-11-15, 2018-12-28, 2019-01-15, 2019-03-15, 2019-10-15, 2025-10-15, 2025-12-26): they are the days a coupon clause
would add to the risk-date models at h of 2 or more, if the settlement were priced from its announcement. This is a
description of the dates and not a test of whether the clause helps; that is a new declaration.

## 3. Reserves staleness

Around the 26 onsets (decision on the panel day h before the onset; reserves read as the registry's rule reads them, a
Wednesday level five calendar days later at 16:30, against the newest print public at that decision):

| h | age of the print read (days): min / median / max | age of the newest public print | onsets where a newer print was public and unread | mean (max) absolute change the unread print would show, USD billions |
|---|---|---|---|---|
| 1 | 6 / 8 / 12 | 2 / 6 / 8 | 12 | 20.2 (144.1) |
| 2 | 6 / 8 / 12 | 2 / 6.5 / 8 | 7 | 7.7 (71.1) |
| 3 | 6 / 8 / 12 | 2 / 6.5 / 8 | 9 | 10.7 (72.4) |
| 4 | 6 / 7.5 / 12 | 2 / 6 / 8 | 10 | 17.0 (80.9) |
| 5 | 6 / 8 / 12 | 2 / 6 / 9 | 11 | 16.4 (80.9) |

Across all 1874 decision days from 2018-06-28 on, a newer print was public and unread on 710 (`information-set.md` rule 1
counts 795 of 2042 on a different set of days). The five-day constant is the measured floor of the holiday-shifted
release (the week ending 2020-12-23 printed on 2020-12-28, `fred_macro_latest_vintage.field_release_lags.WRESBAL`); the
Board's release dates are published in advance, so a per-release availability would remove the two days in an
ordinary week. That is a change to the registry's shape and is listed below.

> *Correction, 10 October 2026 (#503).* The decision days that serve a scored day at h = 1 are 1,873 (2018-06-28 to 2025-12-30); the
> 1,874 includes the decision day 2025-12-31, whose scored day falls outside the window, so the 710 is over one day too many (the
> share moves by at most one day). The 2042 of `information-set.md` is the whole panel to 2026-09-03, a different scope. See `docs/pivot/diagnostics-reconciliation.md`, point 2.

**A daily proxy does not track weekly reserves.** For each Wednesday W the proxy is the print `k` weeks earlier less the
changes in the Daily Treasury Statement's closing TGA and in the Desk's reverse repo over the same weeks (the balance
sheet identity: a rise in either drains reserves). Both series are read by their reference date, 2018 to 2025:

| base | Wednesdays | correlation of changes | MAE of the proxy (USD billions) | MAE of carrying the print forward | proxy closer than carry | with the H.4.1's own TGA (a ceiling, not public daily): correlation / MAE |
|---|---|---|---|---|---|---|
| 1 week earlier | 393 | 0.28 | 65.0 | 53.3 | 175 of 393 | 0.44 / 50.0 |
| 2 weeks earlier | 390 | 0.35 | 81.7 | 84.9 | 206 of 390 | 0.46 / 68.6 |

In the 25 onset weeks with a Wednesday pair the proxy's mean absolute error is 37.2 billion at one week (the carried
print's is 32.5) and 46.6 at two (56.2). The proxy is no better than the stale print at the lag the declaration implies
most days, and the identity is loose even with the H.4.1's own TGA, because the Fed's other liabilities move reserves too.
The closing TGA of the Daily Treasury Statement also differs from the H.4.1's Wednesday TGA by a mean absolute 27.5 billion;
this was not diagnosed here.

## 4. Structural blind spots

> *Note, 10 October 2026 (#503).* "Blind spot" here has two causes: a risk-date model's probability of exactly 0 off a risk date (called
> *silent* on the post-mortem page) and a cut-off that is infinite because the training window holds no onset. The second is only the
> first branch of what `pressure-audit-result.md` calls blind (that page also counts a window with no cut-off within the limit, which is
> why it finds all four 2018 onsets blind where this section finds two). "Five tier-1 passers" is the same set on both pages. See `docs/pivot/diagnostics-reconciliation.md`, points 4 and 6.

The "five tier-1 passers" are read as the five risk-date severity models that pass tier 1 under the unweighted and the
weighted rule (`docs/pivot/weighted-miss-result.md`, Table 1): `risk_gbm`, `risk_gbm_base`, `risk_logistic`,
`risk_logistic_base` and `risk_quantile_skewt_base`. No model passes all three tiers; if the five were meant to be another
set, section 4's cut-off column applies to every model and its risk-date column to these. Two constructions hide onsets from
them, and neither reads a forecast.

* **Risk-date models: probability exactly 0 off a risk date** (`metadata/risk_date_severity.json`). The risk dates are a
  quarter-end, a month-end or a tax date, and at h = 1 a coupon settlement. Onsets off them cannot be flagged:

  | h | onsets off the risk dates |
  |---|---|
  | 1 (27 onsets) | 2019-05-28, 2019-06-25, 2019-08-13, 2020-03-04, 2020-03-12, 2024-12-26 |
  | 2 to 5 (26) | those six and 2018-11-15, 2018-12-28, 2019-01-15, 2019-03-15, 2019-10-15, 2025-10-15, 2025-12-26 |

* **The cut-off rule never flags before the first onset is in the training window** (`select_cutoff` returns infinity for a
  window with no onset). Reconstructing the judge's refit blocks (21 scored days, window up to the business day before the
  block's first decision): at h = 1 the first block, with the onset of 2018-06-29, flags nothing; at h of 2 to 5 five blocks do (the first five, to early December 2018), and the onsets 2018-11-15 and 2018-11-30 fall in them. This binds every model, benchmarks included.
  Windows with a single onset (2018-12-17 and 2018-12-28 at h of 2 or more) can flag in principle but rest on one onset.

Together, per horizon, the risk-date models cannot warn: h = 1, 7 of 27 (the six above and 2018-06-29); h of 2 to 5,
14 of 26 (the thirteen above and 2018-11-30). Because tier 1 at lead of 1 or more asks for a flag at some horizon, the
number that cannot be warned at any horizon is **6** (the six off-calendar onsets of h = 1): the best possible recall for these models is
20 of 26, 0.77. At a single horizon of 2 or more it is 12 of 26, 0.46, below tier 1's recall bar of one half. Of these, 2018-11-15 is blind to both constructions at every h of 2 or more. The data are in
`blind_spots` of the evidence file, per horizon, with the count of onsets in each onset's training window.

## 5. The count of onsets: 27 at h = 1, 26 elsewhere

The definition is the same at every horizon: SOFR − IORB strictly above +5 bp with no such day on the five panel days
before (`pressure.onsets`). What differs is the **scored window**. The first scored day is 2018-06-29 at h = 1 and 2018-07-02
at h = 2 (2018-07-03, 2018-07-05 and 2018-07-06 at h = 3 to 5), because the shared fold grid starts a day later for
each longer horizon. 2018-06-29 is an onset (a quarter-end with no pressure day in the five days before) and is scored only
at h = 1, so h = 1 has 27 onsets. The judge's tier 1 counts onsets on the days every horizon scores, hence 26.

## 6. The nowcast of #445

The check reproduces the published figures exactly (mean absolute error 1.825 bp for the naive nowcast and 3.463 bp for the
primary, over the same 1873 days). No defect was found in three places:

* **Alignment.** The nowcast of row r is compared with the spread of row r. The naive nowcast of every scored row equals the
  spread of the previous panel row, public at 15:00 on r. Consecutive panel rows are 1 to 4 calendar days apart (weekends and
  holidays only).
* **Units.** The Desk's same-day reverse repo, in USD billions, matches FRED's RRPONTSYD on all but 8 of 1985 admitted days
  (largest difference 5.05 billion; the cause was not looked into); the ridge reads it in trillions and the settlement in
  hundreds of billions, consistently with `metadata/nowcast.json`.
* **Availability.** 1985 operation days to 2025-12-31 are admitted (written on the day, by 15:00); 12 are not (10 written
  again later, 2 after 15:00). That the Desk's API serves a record when it is written is an assumption nothing here can test.

A defect was found in the **estimator**. The spread's one-day change is heavy tailed (median 1 bp, 99th percentile 19 bp,
maximum 282 bp, 16 days above 20 bp), and the ridge is fitted by squared error, so a few days set its weights; the control
with no same-day input is as bad as the candidates. Capping the training target at ±5 bp (training only; scoring unchanged)
moves the primary's mean absolute error from 3.46 to 1.92 bp, and the no-same-day-input control to 1.87:

| nowcast (scored days, bp) | MAE | MAE on pressure days | MAE on quarter-end days |
|---|---|---|---|
| naive (the spread of the previous day) | 1.825 | 10.80 | 8.13 |
| declared primary (reverse repo and settlement) | 3.463 | 10.57 | 10.08 |
| primary features, target capped at ±5 bp | 1.920 | 10.17 | 8.08 |
| no same-day input, capped at ±5 bp | 1.872 | 10.53 | 8.29 |
| same-day inputs only, capped at ±5 bp | 1.981 | 10.44 | 7.98 |

So the idea has not been shown to fail for the reason the headline suggests: most of the loss is the estimator. With that
removed, no variant tried here beats the naive nowcast by mean absolute error over all days, and the variants with the
same-day inputs are 0.05 to 0.1 bp above the no-same-day-input control, which does not support a gain from the
inputs either. On pressure days, where the nowcast matters, the capped primary is 0.6 bp closer than naive (10.17 against 10.80);
no interval was computed, so this is not a finding. These variants are diagnostics read on the scored days (2018-06-29 to
2025-12-31), not candidates; any estimator that should be tested for real (robust, quantile, or nonlinear in the level)
is a new declaration.

## For Eleonora: changes to availability declarations this points to, not made

1. **Date a Treasury settlement from its announcement** (`treasury_auctions.scheduled_availability`): bills 4 to 5 panel days
   ahead, coupons 5 to 14. This would let the settlement features and the coupon clause of the risk-date models be read at h of
   2 to 5. The announcement's clock time is not shown by any document read; the next-day reading is the safe one. The SOMA
   add-on is a result and stays at the results time.
2. **Price the H.4.1 per release** (the Board publishes its release dates) instead of five calendar days: two panel days
   earlier in an ordinary week.
3. **ON RRP, repo operations and the SRF**: one panel day earlier on the Desk's last-write evidence. The Desk states no
   time, so this stays an assumption she may not want to make; #445 and #442 already carry the same-day declarations
   as measurement-only.
4. **Daily Treasury Statement**: 16:00 against 16:30 matters only at a tie with the decision instant.
5. **The risk-date definition**: if (1) is made, the coupon clause is not a horizon-1 rule; that is a new declaration.

## What was not checked

* The announcement clock times (all announcements are read the day they are made, and the next day).
* The OFR's publication time for the tri-party and GCF series, and the Daily Treasury Statement page (unreachable).
* Whether pricing any of the above earlier moves a score. This run measures when things were public, not what a model does
  with them.
* The 2026 window and the blind tier.
