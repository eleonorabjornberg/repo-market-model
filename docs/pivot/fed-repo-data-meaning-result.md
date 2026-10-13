# Fed repo data meaning: what changed, and what it does to the records that read it (#659)

**Serves:** H9 groundwork (the standing repo facility's take-up is a target, #639) and H5 inputs; data work. **Exploration on
development data only:** the tables here are not a verdict for any hypothesis under scoring protocol v1 (#640). No 2026 day is
scored (`docs/decisions/lockbox.md`), nothing is published, and every field stays off in the published declaration.

## What changed (data meaning decided by Nicholas Beroud, eleonorabjornberg/repo-market-liquidity#1)

1. **Before 2019-09-17** (`ingest.REPO_FACILITY_START`, the facility marker) the six operations of $64-66 million
   (2018-05-09 to 2019-05-13) are test operations and are left out. The structural zero stands.
2. **2019-09-17 to 2021-07-28:** a panel date with no operation reads as **missing** (`None`), not zero. The Desk operated on
   every business day of the tracked snapshots from 2019-09-17, so no tracked date is missing; `tests/test_fed_liquidity.py`
   pins that. The rule is a guard for other coverage. From 2021-07-29 a date with no operation is zero, as before.
3. **Labels.** `repo_accepted` and `repo_submitted` are declared as take-up demand signals (`field_meanings` in
   `metadata/sources_measurement.json`). A new fifth series, `repo_term_outstanding` (USD billions of term repos with settlement
   <= d < maturity, rebuilt across the snapshot files), is the cash outstanding. It is off the panel columns and off
   `FEATURE_FIELDS`.
4. **#654.** A panel date after `coverage_end` (2025-12-31, declared) is refused with `StaleReadError`, never read as zero.

The material-use dates ($1 billion or more accepted) are unchanged on every date through 2025-12-31; a test pins their digest.

## What moved in the data

Against the module before this change, on the scratch panel: the take-up columns differ on the six test dates, the change
column on those and the day after, and `fed_repo_days_since_positive` on the rows from 2018-05-09 to 2019-09-16 (it stays at
its cap until the facility's first day, instead of restarting at each test). Nothing from 2019-09-17 on moves.

## Records that read these columns

Re-scored here, on the published panel `4ddc3882…` (commands of `docs/pivot/fed-liquidity-result.md`, the current judge, h = 1
to 5): the candidates of #425 and their same-day versions of #442. Evidence: `docs/pivot/evidence/fed-repo-data-meaning/`
(`judge.md`, `tables.md`, `paired.md`). The judge in force now reports the weighted and flat false-alarm counts, so the tables
are not row-for-row the committed ones. The reading is unchanged: no candidate passes, and none beats the control with an
interval that excludes zero in the pooled Brier comparison at any horizon.

**Not re-scored** (they read these columns among many inputs; the change is confined to the 2018-05 to 2019-09 rows above):
`source-screen-result.md`, `source-matrix-ordinary-days-result.md`, `unused-inputs-result.md`, `ofr-followup-result.md`,
`backfilled-history-result.md`, `weighted-miss-result.md`, `new-sources-due-diligence.md`. They are development-data
screens; whether to re-run them is Eleonora's call. No record is edited in place.
