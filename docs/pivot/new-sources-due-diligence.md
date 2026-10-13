# Due diligence on candidate new data sources, before any fetch (#630)

Step 1 of #630, written and committed **before** any request is made for it. It is a screen of what could be a new input for
the ordinary-day gap, not a result: nothing here is selected into a model, joins the published panel or a published
declaration, or moves a published figure. No day after 2025-12-31 is read or scored (`docs/decisions/lockbox.md`).

The verdicts rest on the repository's own records (the registries, the tracked snapshots and their manifests, findings
#508, #522, #572 and #576, and `docs/pivot/evidence/desk-standard/`) and on each publisher's published schedule as those
records quote it. Nothing in the table was fetched for this step. Where a verdict depends on a fact that only a request can
establish, the verdict says which fact, and step 2 settles it in the open.

## The checklist

Each candidate is assessed on: publisher and URL; public and free, terms of use, reachability from the session; start of
history; frequency; **publication instant** (when each observation became public, and whether a real-time history or posting
dates exist: a back-filled history is not usable, #508, #522, #572); revisions and vintages; gaps; format and whether the
standard library parses it (`src/` is stdlib-only); overlap with what is already held.

Verdicts: **use** (step 2 takes a snapshot and writes a reader), **do not use** (with the reason), **blocked** (cannot be
established from this session; reported, not worked around).

## The table

| # | Candidate | Publisher, URL | Already held? | Publication instant and history | Verdict | Reason |
|---|---|---|---|---|---|---|
| 1 | Standing repo facility, daily take-up and propositions | NY Fed, `markets.newyorkfed.org/api/rp/results` | **Yes.** `nyfed_srf` (`srf_total_accepted`) in `sources.json`; `nyfed_repo_ops` (`repo_accepted`, `repo_submitted`, `repo_rate`, `repo_ops_accepting`) in `sources_measurement.json` | Operation results the day of the operation; the registry's declared lags apply | **Do not use** | Take-up and propositions (amounts submitted) are carried; a second copy would only repeat them. |
| 2 | ON RRP: take-up, counterparties, award rate distribution | NY Fed, same API | **Partly.** Total accepted is held (`nyfed_on_rrp`, `nyfed_on_rrp_sameday`). The tracked snapshot `tests/fixtures/snapshots/on_rrp_inputs/nyfed_on_rrp/` already holds, per operation, `participatingCpty`, `acceptedCpty`, `totalAmtSubmitted`, the accepted amount by counterparty type (`bank`, `gse`, `mmf`, `pd`) and `percentAwardRate`; no reader uses them | Same release as the held total, so the held declaration's lag applies; the operations carry `releaseTime` and `lastUpdated` | **Use** | New information (who takes the facility, and at what rate) on bytes already tracked; no fetch is needed. The sameday release rule of the held total is the one to use. |
| 3 | NY Fed reference-rate volumes and percentiles | NY Fed, `markets.newyorkfed.org/api/rates` | **Yes, for SOFR, BGCR and TGCR** (rate, 1st, 25th, 75th and 99th percentiles, volume). EFFR carries the rate and the same percentiles but **not its volume** | Same release as the held fields | **Use, for the EFFR volume only** | The tracked EFFR snapshots hold `volumeInBillions`; no reader carries it. Everything else in this candidate is already in the panel: dropped. |
| 4 | Primary dealer statistics (weekly): Treasury positions, repo and reverse repo financing, fails | NY Fed, `newyorkfed.org/markets/counterparties/primary-dealers-statistics`, `markets.newyorkfed.org/api/pd` | **Partly.** Positions are held (`nyfed_fr2004`, `PDPOS…`). Financing (`PDSORA`, `PDSIRRA` families) and fails (`PDFT…`) are not read; the tracked `nyfed-primary-dealer/latest.csv` holds only the latest value of each, with no history | Same weekly release as the held positions (the held declaration's lag applies to the whole release). No vintages are published: a later print can restate (the held positions are in the same position) | **Use, subject to one fact step 2 settles:** that the API serves the financing and fails series back to 2018 | It is the one weekly view of dealer financing and fails, the plumbing around the days when repo is tight. Risk: a restatement is invisible without vintages, as for the held positions. |
| 5 | OFR Short-term Funding Monitor: tri-party by collateral, DVP and GCF volumes and rates | OFR, `data.financialresearch.gov/v1` | **Partly.** DVP rate and volume (`ofr_stfm_repo`); tri-party and GCF rate and volume (`ofr_stfm_repo_segments`). The collateral breakdown of tri-party is not held | Real-time only from 2020-09-09 (#508, #522); earlier values were filled in later and may not be read. The metadata endpoint states the start of real-time publication per mnemonic | **Use, read only from the real-time start, behind the existing guard** | A collateral breakdown is new. If the metadata does not show a real-time start per series, the series is not used. |
| 6 | OFR money market fund monitor (monthly; repo holdings by counterparty) | OFR, `financialresearch.gov/money-market-funds` | **Yes** in substance: `sec_nmfp` (N-MFP, `mmf_repo_holdings` and the other `mmf_*` fields) is the filings the monitor is built from | Monthly, from filings public some weeks after the month ends | **Do not use** | The monitor repeats the filings already held, monthly and weeks late. The counterparty split cannot help a daily forecast at that lag. |
| 7 | OFR U.S. Repo Markets data release | OFR, `financialresearch.gov/short-term-funding-monitor` | **Yes** in substance: it publishes the STFM segments of row 5 (with DTCC and Fed series) | Back-filled history; no posting dates | **Do not use** | It repeats row 5 and has no real-time history (the #508 case). |
| 8 | DTCC: FICC sponsored repo and GCF volumes (public pages) | DTCC, `dtcc.com` | **Partly.** GCF volume and rate come through the OFR segments (`ofr_stfm_repo_segments`, `REPO-GCF_*`), which are the DTCC data | Not established: the public pages state no posting time and keep no vintages, and the page terms are not read here | **Blocked** | No publication instant can be established from the pages, and a download would be a snapshot with no real-time history. Reported, not used (#630: "If a source's publication instant cannot be established, it is reported and not used"). |
| 9 | Treasury auction results: size, bid-to-cover, dealer take-down | Treasury Fiscal Data, `api.fiscaldata.treasury.gov/…/auctions_query` | **Offering amounts only** are read (`treasury_auctions`). The tracked snapshot `tests/fixtures/snapshots/treasury_auctions/auctions_2018_present.json` holds the results fields for the same rows (`bid_to_cover_ratio`, `primary_dealer_accepted`, `indirect_bidder_accepted`, `direct_bidder_accepted`, `total_accepted`, `high_yield`, `avg_med_yield`, and the closing times) | Auction results are public at the auction close (`closing_time_comp`); the table serves the current rows and keeps no vintages, and a result is not restated | **Use** | Dealer take-down and bid-to-cover are new information on bytes already tracked; no fetch is needed. The result is public on the auction day after the close, before a 16:00 decision. |
| 10 | Treasury bill issuance calendar beyond the settlement modules | Treasury Fiscal Data | **Yes.** Announcement date, auction date, issue date and offering amount feed `treasury_settlement*` and `net_settlement*` | Fixed at the announcement | **Do not use** | Nothing is left beyond what the settlement modules read. |
| 11 | Daily Treasury Statement detail beyond the balance (deposits and withdrawals of operating cash) | Treasury Fiscal Data, `api.fiscaldata.treasury.gov/…/accounting/dts/deposits_withdrawals_operating_cash` | **Balance only** (`treasury_dts_tga`, `TGA_CLOSE`). The deposits and withdrawals table is the same statement, not held | Same release as the held balance: the next business day at 4:00 PM ET. The held declaration's instant (16:30 ET) applies. The API keeps no vintages | **Use, subject to one fact step 2 settles:** the table's start and that its line names are stable | TGA flows by kind (taxes, debt cash issues and redemptions) show what moves the balance, which the level does not. |
| 12 | Federal Reserve H.4.1 detail: foreign official repo pool, discount window lending, foreign official reverse repos | Federal Reserve Board and FRED (`WLRRAFOIAL`, `WLCFLPCL`) | **Partly.** `WLRRAOL` (other reverse repos) and the total assets are held (`fred_macro_latest_vintage`). The foreign official line (`WLRRAFOIAL`) was studied as an ALFRED vintage pull only (`docs/pivot/source-screen-result.md`) and is not a field | Thursday 4:30 PM ET for the week ended the previous Wednesday; the held declaration carries five calendar days, measured on first prints (`WLRRAOL`). FRED serves the latest vintage; ALFRED serves vintages | **Use, on the held five-day lag, with the discount window line as a second candidate** | Both lines are small in an ample-reserves year and can be large in a stress year. Risk: only the latest vintage is snapshotted, as for the held H.4.1 lines. |
| 13 | Quarter- and month-end bank balance-sheet signals (FR Y-15, G-SIB indicators) | Federal Reserve Board, FR Y-15 public data | No | Quarterly, public after a lag of months | **Do not use** | One observation a quarter, published months late: it cannot say anything about a decision day. |
| 14 | MBS settlement calendar (SIFMA class dates) | SIFMA | No (the calendar columns hold SIFMA holidays only, `docs/decisions/calendar-columns.md`) | The dates are fixed in advance and published a year ahead | **Blocked** | The SIFMA settlement-date tables are published as documents whose terms of use and reachability from this session are not established here, and a hand-typed table is not a source. Reported, not used. |

## What step 2 does with the verdicts

* Rows 2, 3 (EFFR volume) and 9 are **readers over bytes already in the tree**. Their snapshots carry digests in their
  manifests; the PR lists them and the command that checks them.
* Rows 4, 5, 11 and 12 need a dated snapshot. Each is fetched by one plain request, on its own, to the host the directive
  names. A request that is refused is reported and that source stops there.
* Rows 8 and 14 are reported as blocked.
* Every reader refuses, with `LookAheadError`, a value that would be read before its publication instant, and every guard has a
  recorded mutation.

## What step 2 found (written after the snapshots)

The table above is unchanged: it is the record of what was decided before any fetch. Step 2 changed the following, each with the
reason.

* **Row 2, ON RRP counterparties: narrowed.** The tracked records carry the amount accepted by counterparty type (`propositions`), but
  the Desk's FAQ says those are added each month with data lagged by one month (`tests/test_registry.py`, A45, item 3), so the split was
  not public on the operation date: it fails the publication-instant test and is **not read**. What is read is `participatingCpty`,
  the number of counterparties, which sits in the record the held amount accepted already reads, and only for a record the Desk did
  not rewrite on a later day (`lastUpdated`). The award rate was dropped: it is the facility's offering rate, fixed by policy, and
  repeats the policy register.
* **Row 3, EFFR volume: not taken.** The tracked EFFR snapshots are the rate responses (`type=rate`), which do not carry the volume;
  a snapshot would need a further request for each of nine years. It was judged not worth that for an unsecured-market volume that
  the secured volumes already held cover, and it is left as a lead for a later directive, not a verdict against the source.
* **Row 4, primary dealer financing and fails: confirmed.** The full export (`api/pd/get/all/timeseries.csv`) carries the financing
  (`PDSORA`, `PDSIRRA`) and fails (`PDFTD`, `PDFTR`) series weekly from 2013-04-03. **Corrected by #680: that line said "no gap", and it was wrong for three of the five series.** The New York Fed withholds ('*') some weeks of the financing series: 85 of 666 weekly dates for `pd_repo_ust` (2022-01-12 onward; 15 in 2022, 16 in 2023, 21 in 2024, 33 in 2025; longest run 12 weeks, 2025-01-08 to 2025-03-26), 72 for `pd_reverse_repo_ust` (2022-07-13 onward; 17, 13, 16 and 26 in 2022 to 2025; longest run 9 weeks, 2025-04-16 to 2025-06-11) and 3 for `pd_repo_mbs` (one each in 2022, 2024 and 2025); `pd_fails_deliver_ust` and `pd_fails_receive_ust` have none. Counts and longest runs are in `docs/pivot/new-sources-withheld-weeks.md`. The tri-party and
  GCF financing sub-series start only in 2022; they are not read.
* **Row 5, OFR collateral breakdown: not taken.** The metadata endpoint lists the tri-party series by collateral (`REPO-TRI_AR_T-F`,
  `REPO-TRI_TV_T-F` and the agency, corporate and other siblings), so the series exist. Their real-time start was not read from the
  metadata endpoint in this PR, and the existing fetch function takes the held mnemonics only; the series are not used until that
  start is established, as the verdict required.
* **Row 11, Daily Treasury Statement detail: narrowed to the debt cash lines.** The deposits-and-withdrawals table has the
  same release as the held balance, but its line names changed between 2018 and 2024 for taxes and agencies (`(Table III-B)` became
  `(Table IIIB)` for the debt lines in 2022; the tax lines were renamed more widely). Only the two debt lines
  (`Public Debt Cash Issues`, `Public Debt Cash Redemp.`) are stable across the sample, and only those are read.
* **Row 12, H.4.1 detail: not taken.** The held H.4.1 lines each carry first-print revision evidence from ALFRED vintages
  (`metadata/sources.json`, `WLRRAOL`). The foreign official and discount window lines would need the same before they can be declared,
  and fetching those vintages is a task of its own. Left as a lead.
* **Rows 8 and 14, blocked,** as stated: DTCC and the SIFMA settlement tables were not requested.
* **Row 9, auction results: confirmed on the tracked bytes.** 3,557 of the 3,562 rows in the tracked table carry a result. Every
  auction with a result closes its competitive bids at 14:30 ET or earlier (two bills at 14:30, most at 11:30 or 13:00).
