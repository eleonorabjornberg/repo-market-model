# Posting dates of the 2014-2018 back-fill: due diligence (#633)

Serves H4 (longer history fixes part of 2018-19), step 1 of #633. The table below was committed before any
`posting_instant` was set, as the directive asks.

> **Update, 13 October 2026: the workbook is usable, public from 17 May 2018.** Eleonora ruled (PR #661, comment
> [6146010089](https://github.com/eleonorabjornberg/repo-market-model/pull/661#issuecomment-6146010089), relayed by the
> orchestrating session) that every value in the TGCR/BGCR/SOFR back-fill workbook (22 Aug 2014 – 29 Mar 2018, today's
> `Data Release.xlsx`) is public from **17 May 2018**: one `posting_instant` for all three series, with the research
> comment [6145957978](https://github.com/eleonorabjornberg/repo-market-model/pull/661#issuecomment-6145957978) as its
> source. No value is read as of a decision before that date, and the pre-May-2018 vintages are not used.
> `metadata/backfill_posting.json` now declares `2018-05-17T00:00:00` (no announcement gives a time of day, so the
> start of that day), and `backfill.require_posting_established` refuses every fit whose training ends before it
> (`tests/test_backfill.py`, `TheRuledPostingInstant`). The first fit that trains on the back-fill in the measurements
> so far ends on 2018-06-27, so every scored day from 2018-06-29 may train on it. The measurement is
> [`posting-dates-h4-measurement.md`](posting-dates-h4-measurement.md). The other rows of the table are unchanged.

Rule used (the directive's): a series is usable only if the instant it became public is established from a source that
is cited here. Where the evidence is ambiguous it is marked not usable and listed for Eleonora. No pattern is inferred.

## Table

| series (snapshot under `tests/fixtures/snapshots/backfill_2014_2018/`) | what the held bytes show | when public: established? | first print or revision? | gaps and breaks | verdict |
|---|---|---|---|---|---|
| `nyfed_repo_backfill` (TGCR, BGCR, indicative SOFR, 2014-08-22 to 2018-03-29) | one workbook, retrieved 2026-10-08 from `https://www.newyorkfed.org/medialibrary/media/markets/Data%20Release.xlsx`; sha256 `1c889930...`. Properties: created 2018-05-01, modified 2018-05-03. Host `Last-Modified` 2022-09-15 | **Yes, by Eleonora's ruling of 13 October 2026: public from 17 May 2018** (see the update above). Before it: no. The Bank's additional-information page (`https://www.newyorkfed.org/markets/reference-rates/additional-information-about-reference-rates`, fetched 2026-10-13) lists the workbook as "Daily indicative TGCR, BGCR, and SOFR volume and rate data (Aug. 2014 - Mar. 2018)" and states no posting date. The property dates are file-creation dates and the header is a re-upload. The Bank's dated announcement pages could not be reached from this environment (the 2018 operating-policy URL I tried redirects to a 404). | Not a first print in any sense: the rates are computed after the fact on the SOFR method ("indicative"), rounded to whole bp. No vintages exist. | SOFR starts 2018-04-02; the workbook's SOFR is a stand-in built from the same method, which is a modelling choice and not a published rate. Rates are whole bp; no percentiles. | **Usable with a posting-instant rule**: every value public from 2018-05-17 (ruling of 13 October 2026). Training history only. |
| `nyfed_on_rrp` (ON RRP operation results, 2014-2017, NY Fed API `markets.newyorkfed.org/api/rp/results/search.json`) | per-operation results with `operationDate`, `settlementDate` and a `lastUpdated` field per operation | **No, for the history.** An operation's result is posted on its own operation day in the live feed, but the held bytes were fetched in 2026 and `lastUpdated` carries later dates; nothing held shows the first posting of each 2014-2017 result. | Possibly revised: `lastUpdated` differs from the operation date, which I could not reconcile from the held bytes. | Fixed-rate full-allotment operations only; the rate is administered, not market-determined. | **Not usable** until the first-posting rule is sourced (listed for Eleonora). |
| `frb_h8` (H.8 total assets, weekly, first print, 209 releases 2014-01-03 to 2017-12-29) | the Board's own `releaseDates.json` and each release page; `release_date` and `public_on` agree on every row (0 disagree); values are the first print from each release | **Yes, to the day**, from the Board's release dates (`https://www.federalreserve.gov/releases/h8/releaseDates.json`, retrieved 2026-10-08, sha256 `29da53cb...`). The hour is stated on each release (`stated_release_time`). | First print, by construction (each value is read from the release that first carried it). Later H.8 revisions and benchmark breaks are not in the held series. | weekly, not daily; benchmark revisions to the underlying levels are not captured. | **Usable with a posting-instant rule**: the value of week ending W is public from its own release's date and stated time. Not an input of `risk_gbm+settle+h41+dist_roll` as it stands. |
| `treasury_bill_rates` (Daily Treasury Bill Rates, 2014-2017) | CSV per year from `home.treasury.gov`, retrieved 2026-10-08 | **No.** No source held or fetched here states when each day's rates first appeared. | Unknown whether the CSV carries later corrections. No vintage archive is held. | none found in the held bytes | **Not usable.** Listed for Eleonora. |
| `treasury_auctions` (Treasury securities auctions data, issue dates 2014-01-02 to 2017-01-02) | Fiscal Data API; `auction_date` and `issue_date` per row | **Partly.** An auction's result is public on its auction date by Treasury practice, but this page cites no source for the hour. | Unknown. | The held extract ends 2017-01-02. | **Not usable** until a source for the posting rule is cited. |
| H.4.1 (reserve balances, TGA) | not held in this back-fill | **Not applicable here.** The Board's H.4.1 release dates are the source, but no 2014-2017 H.4.1 series is in this snapshot. | | | Out of scope until a series is held. |
| DTS (Daily Treasury Statement) | not held in this back-fill | Not applicable here. | | | Out of scope until a series is held. |
| OFR (short-term funding monitor) | not held in this back-fill | Real-time from 2020-09-09 only (#522); earlier values are not usable. | | | Not usable before 2020-09-09. |

## What this does and does not settle

- The TGCR/BGCR/SOFR workbook is usable as training history with one instant, 17 May 2018, for all three series
  (Eleonora's ruling above). Its SOFR before 2018-04-02 remains an indicative series computed after the fact.
- Only the H.8 total-assets series otherwise meets the rule, and the guard reads one workbook-level instant. Whether
  other series get their own instants was not asked by the ruling and is not done here.
- The ON RRP results, bill rates and Treasury auctions of 2014-2017 keep their verdicts (not usable). The extended
  panel of `scripts/backfill_history.py panel` still carries them on back-filled rows; a model that reads them trains on
  values whose posting is not established. The H4 measurement reads none of them.

## For Eleonora

1. **Posting date of the workbook.** Answered by the ruling of 13 October 2026.
2. **Per-series instants.** Answered for the workbook: one instant for all three series.
3. **The other 2014-2017 series** (ON RRP results, bill rates, auctions) stay not usable until their posting is
   sourced.
