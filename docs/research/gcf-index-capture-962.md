# DTCC GCF Repo Index: forward capture (#962)

**Capture and groundwork, not a result.** Serves H5 (primary goal), groundwork G3 (prospective logging), and
the lead-1 anchor of H5 steps 2 and 3 (Lens E of #958). No figure on this page is a score; no history is read as
an input.

## What is captured

The DTCC GCF Repo Index is the par-weighted overnight rate, and the par volume, of the GCF Repo trades that clear at
FICC, for U.S. Treasury and for agency MBS collateral. DTCC's fact sheet states that the day's value is posted "at
approximately 3:30 p.m. EST" (quoted in #962, not re-read here: see "What was and was not checked"). If so it is the
only public repo rate for day T that exists at T's 16:00 ET decision instant, half an hour after it is posted;
SOFR for T prints at 08:00 ET on the next business day.

The capture is a Mac job, not a GitHub Actions workflow (Eleonora's ruling of 27 October 2026 on #1281). DTCC's
Terms of Use forbid redistributing the content and compiling it into a database, and this repository is public, so
the store is private and **no DTCC data is kept in this repository**. `scripts/gcf_index_capture.py` is code only. A
launchd job (`scripts/launchd/org.rmm.gcf-index-capture.plist`) runs it every five minutes on her Mac; the script reads
the ET clock and fetches only on a business day from 15:30 to 16:00 ET (one request per run, to one URL,
`https://cms-prod.dtcc.com/data/gcfindex.csv?v=<epoch ms>`, the file the index page itself loads), and once after
16:00 ET to record the day missed. It appends one file per business day, `gcf/<date>.json`, to a private directory
outside any checkout, `~/rmm-private/gcf-index/` by default, and refuses a directory inside a git checkout
(`gcf_index_capture.require_private`). The live record, `live-log.yml` and the live pin are not touched. The
`needs-mac:` comment on the pull request carries the install paste.

| Day's outcome | What is stored |
|---|---|
| `captured` | the response text as fetched, its SHA-256, the fetch instant in UTC and in ET, the window and the decision instant, the URL, and the day's Treasury rate (percent) and par volume (USD) read off the response |
| `missed`, `fetched_after_decision` | no value: the hash of the response, the fetch instant, and the reason. The row was there, but not before 16:00 ET |
| `missed`, `no_posting` | no value: the file had no row for the day after 16:00 ET; the latest row date it did have |
| `missed`, `unreadable_response` | no value: the hash of what was returned |
| `missed`, `no_run` | no value, no fetch: a business day after the store's first day on which no run kept anything |

A day's file is written once and never overwritten; a missed day is never back-filled. A run in the window that finds
no row for the day writes nothing and leaves it to a later run. The capture starts on the first business day after
the job is installed; there is no earlier file. A Mac that is asleep through the window misses the day, and the day
is recorded missed, never back-filled.

**History.** Her history files (the 12-month CSV and DTCC's 2005-2024 workbook) go in the same private directory,
under `history/`, and never into the repository. Nothing here reads them; rulings (a) and (b) on #1280 stand.

**The guard.** `gcf_index.check_record` raises `LookAheadError` for a captured record fetched after the day's 16:00 ET
decision instant, and `gcf_index.read_value` raises it for a value fetched after the reader's instant. A reader takes the private directory as an argument. Both run when a
record is built, written and read back. The recorded mutations are in `tests/test_gcf_index_capture.py`.

**The declaration.** `dtcc_gcf_repo_index` in `metadata/sources_measurement.json`: `basis: ref_date`, `days: 0`,
`available_time: 15:30`, with `availability_provenance` citing the fact sheet and stating what was and was not read.
It is off in every published declaration, and no column reads it.

## What was and was not checked (27 October 2026)

Checked, from this environment:

* The index page, `https://www.dtcc.com/market-index-data/charts/dtcc-gcf-repo-index`, is client-rendered. It names
  the data file `/data/gcfindex.csv` on `cms-prod.dtcc.com`, which answers HTTP 200 with about a year of daily rows:
  `Date`, then par volume (USD) and weighted-average rate (percent) for MBS and for Treasury, and a `TRAILER` line that
  counts the rows. The first row is a year before the fetch.
* The file is served through a CDN with `cache-control: public, max-age=604800`. A request without a query string
  returned a copy 2.2 days old (it lacked the Monday row). The page's own request adds `?v=<epoch ms>`, and so does
  the capture. A capture without it would read a stale file and could take yesterday's file for today's.
* The file's `Last-Modified` header read 15:12:23 ET on Friday 23 October and 15:12:42 ET on Monday 26 October: on
  both days the row was in the file before 15:30. On Tuesday 27 October no row for the day was in the file at 16:18
  ET, so that day would be recorded `missed`, `no_posting`. Two days and one miss are not a distribution of posting
  times; the file keeps no per-day posting record.
* The index page shows about 12 months, which answers the question of how much history the website holds.

Not checked:

* **The fact sheet.** The link on the index page is on `files.dtcc.com`, which this environment refuses (HTTP 403 at
  the proxy's CONNECT), and the URL the directive gave returns 404. So "approximately 3:30 p.m. EST" is quoted from
  #962, not re-read, and `availability_provenance` says so.
* **The pre-2025 history.** The page links a historical workbook, also on `files.dtcc.com`. Not fetched.
* **Whether a value is revised after it is posted.** The file keeps no vintages, which is the reason to capture it
  at the time.

## The question to Eleonora

Separate issue, labelled `needs-eleonora`, linked from the pull request: (a) whether the fact sheet's general "about
3:30 p.m." establishes the publication instant for the history under #630's rule; (b) the pre-2025 history request,
which she has approved and is sending herself; (c) DTCC's terms of use (ruled 27 October 2026: the store is her Mac). The terms (`https://www.dtcc.com/terms`,
last updated 11 March 2026, section "Use of Content") are quoted there, with what they would mean for an automated
daily fetch and for storing the bytes on a public branch. None of it is settled in code.
