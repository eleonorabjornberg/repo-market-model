# Before and after #662 for `weighted-miss-result.md` (#692)

Eleonora's instruction on #692: re-run the screen unchanged apart from the data, and tabulate, for the rows that read the Fed repo take-up
columns, the committed figure beside the re-run, and say whether any ranking or conclusion moved. No published figure is edited; this
directory is new.

**Which rows read `fed_repo_*`.** The page's inputs are forecast files written by the commands of other result pages. Of the candidates in
its Table 1 (64 rows), four read the columns, all from `docs/pivot/fed-liquidity-result.md` and its same-day page
(`fed-liquidity-sameday-result.md`): `hierarchical_logistic_fed_repo`, `hierarchical_logistic_fed_repo_sameday`,
`hierarchical_logistic_srf`, `hierarchical_logistic_srf_sameday`. They are written by one command (`scripts/fed_liquidity.py forecasts`, h = 1 to
5). No other candidate declared on `main` reads them (checked: every candidate file and script that names a `fed_repo_*` column is in that
list or in the `*_dealer` rows of the unused-inputs page, which this page does not score). The other 60 rows are not re-run. The control rows
re-run here (`hierarchical_logistic`, `calendar_climatology`, `persistence_logistic`, `published_v1`) are for the check below, not for the answer.
`weighted-miss-in-force-result.md` scores only the `risk_*` candidates and the benchmarks, none of which reads the columns, so it is not
re-run.

**Reuse of `evidence/fed-repo-data-meaning/`.** #659's re-score is the judge in force on the four candidates of #425/#442 at the same forecast
files, but it is a report under the declared (weighted) rule only; it does not hold the flat-rule run, the `weighted_miss.py` table or the regime
split this page is built from. So the four candidates' forecasts are regenerated here with the same command, and the judge is run under both
rules. As a consistency check, the weighted-rule rows here match #659's `tables.md` (same forecast command, same panel).

## Answer

* **No pass/fail verdict moved.** Tier 1 fails for all four candidates under both rules, before and after; no candidate passes the pass rule.
  "No candidate passes the pass rule under either rule" and "the weighted rule moves tier 1 only" (for the rows that matter there:
  `rare_gbm_focal+recalibrated` and `two_part_logistic`, which do not read the columns) are untouched.
* **Cells that moved because of the data** (old data -> new data; same code and judge): for all four candidates the flat false alarms per
  onset rise (`..._fed_repo` 3.73 to 4.23 and 5.65 to 6.38 under the unweighted and weighted rule, `..._fed_repo_sameday` 3.85 to 4.38 and
  5.92 to 6.50, `..._srf` 3.81 to 4.08 and 5.65 to 6.38, `..._srf_sameday` 4.08 to 4.19 and 5.69 to 6.27; the weighted counts move by smaller
  amounts and not always up, see the table); the onsets warned change by one in three cells
  (`..._fed_repo` unweighted 14 to 15; `..._fed_repo_sameday` unweighted 15 to 14 and weighted 15 to 16); tier 3 goes from fail to pass for all four
  (at h = 3 and more, the 2018-19 regime is now calibrated); and tier 5 goes from pass to fail for `..._fed_repo_sameday`. Per-horizon detail is in
  `tier1.json` and the regime split below.
* **Conclusion of the page that moved.** "Tier 3 ... fails for every candidate under both [rules]" is not reproduced by today's judge for the four
  rows (data) nor for `hierarchical_logistic` and `published_v1`, which do not read the columns (judge drift; see below). It does not change who
  passes, because tier 1 still fails for all of them.
* **Ranking.** The page ranks no candidates, only passes them or not. By warned count the four stay within one of `hierarchical_logistic`
  (15 of 26 under both rules).

## How this was produced

* Panel `4ddc3882...` (rebuilt from the tracked fixtures, `verify-panel` clean). Scratch panels: `pressure_v1_1.py panel` (`4137d0ad...`), then
  `fed_liquidity.py panel`; forecasts by `fed_liquidity.py forecasts --panel AUG_F.csv --published PUB.csv --horizon H` and
  `hierarchical_logistic.py forecasts --panel AUG.csv --horizon H` (the control, written on `4137d0ad...`; its digest field was set to the published
  panel's after checking that its days are the grid's, as the page's Reproduce paragraph says), plus the benchmarks from
  `pressure_judge.py forecasts --published`. Then the page's commands: `pressure_judge.py judge --rule unweighted` and `--rule weighted`, and
  `weighted_miss.py table`. Files: `table.md` (this run), `tier1.json`, `old-data-control/table.md`.
* **Old-data control.** Same commands on a scratch copy of `main` with `fed_liquidity.py`, `ingest.py` and `sources_measurement.json` put back to
  before #662. The scratch panels differ in `fed_repo_*` on the 339 rows 2018-05-09 to 2019-09-16 only.
* The committed table is the existing `evidence/weighted-miss/table.md` (read-only).

## Table 1 and regime split

## 1. Table 1 rows, `committed -> same code and judge with the old data -> re-run (new data)`

Each cell is `committed >> old data under today's judge >> new data`; a single value means all three agree. `R` marks a candidate that reads `fed_repo_*`.

| candidate | reads | warned, unweighted | warned, weighted | FA/onset unweighted (flat / weighted) | FA/onset weighted (flat / weighted) | tier 1 unw. | tier 1 w. | tier 3 (unw. / w.) | tier 5 (unw. / w.) |
|---|---|---|---|---|---|---|---|---|---|
| calendar_climatology | - | 10 | 12 | 5.00 / 2.80 | 6.69 / 3.75 | fail | fail | fail / fail | fail / fail |
| hierarchical_logistic | - | 15 | 15 | 3.65 / 1.31 | 6.23 / 2.91 | fail | fail | fail / fail >> pass / pass >> pass / pass | fail / fail |
| hierarchical_logistic_fed_repo | R | 14 >> 14 >> 15 | 15 | 3.73 / 1.56 >> 3.73 / 1.56 >> 4.23 / 1.71 | 5.65 / 2.68 >> 5.65 / 2.68 >> 6.38 / 2.94 | fail | fail | fail / fail >> fail / fail >> pass / pass | fail / fail |
| hierarchical_logistic_fed_repo_sameday | R | 15 >> 15 >> 14 | 15 >> 15 >> 16 | 3.85 / 1.58 >> 3.85 / 1.58 >> 4.38 / 1.68 | 5.92 / 2.81 >> 5.92 / 2.81 >> 6.50 / 2.99 | fail | fail | fail / fail >> fail / fail >> pass / pass | pass / pass >> pass / pass >> fail / fail |
| hierarchical_logistic_srf | R | 15 | 15 | 3.81 / 1.54 >> 3.81 / 1.54 >> 4.08 / 1.48 | 5.65 / 2.69 >> 5.65 / 2.69 >> 6.38 / 2.94 | fail | fail | fail / fail >> fail / fail >> pass / pass | fail / fail |
| hierarchical_logistic_srf_sameday | R | 15 | 15 | 4.08 / 1.75 >> 4.08 / 1.75 >> 4.19 / 1.65 | 5.69 / 2.72 >> 5.69 / 2.72 >> 6.27 / 2.89 | fail | fail | fail / fail >> fail / fail >> pass / pass | fail / fail |
| persistence_logistic | - | 7 | 12 | 3.42 / 1.17 | 7.04 / 3.25 | fail | fail | fail / fail | fail / fail |
| published_v1 | - | 2 | 14 | 2.35 / 0.79 | 5.73 / 2.38 | fail | fail | fail / fail >> pass / pass >> pass / pass | fail / fail |

* old data under today's judge -> new data (the data change alone): rows with any Table 1 cell different: reading rows ['hierarchical_logistic_fed_repo', 'hierarchical_logistic_fed_repo_sameday', 'hierarchical_logistic_srf', 'hierarchical_logistic_srf_sameday']; other rows none.
* committed -> old data under today's judge (everything except the data: judge and code on `main`): rows with any Table 1 cell different: reading rows none; other rows ['hierarchical_logistic', 'published_v1'].
* committed -> new data (the directive's before/after): rows with any Table 1 cell different: reading rows ['hierarchical_logistic_fed_repo', 'hierarchical_logistic_fed_repo_sameday', 'hierarchical_logistic_srf', 'hierarchical_logistic_srf_sameday']; other rows ['hierarchical_logistic', 'published_v1'].

## 2. By regime (worst horizon, flat / weighted false alarms), reading rows

| candidate | rule | regime | onsets | warned: committed >> old data >> new | false alarms (flat / weighted): committed >> old data >> new |
|---|---|---|---|---|---|
| hierarchical_logistic_fed_repo | unweighted | 2018-19 | 17 | 11 >> 11 >> 12 | 93 / 38.50 >> 93 / 38.50 >> 102 / 39.00 |
| hierarchical_logistic_fed_repo | unweighted | 2020 | 2 | 0 | 2 / 1.25 >> 2 / 1.25 >> 4 / 4.00 |
| hierarchical_logistic_fed_repo | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| hierarchical_logistic_fed_repo | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| hierarchical_logistic_fed_repo | unweighted | 2025-26 | 5 | 3 | 11 / 3.50 |
| hierarchical_logistic_fed_repo | weighted | 2018-19 | 17 | 12 | 131 / 59.75 >> 131 / 59.75 >> 146 / 64.75 |
| hierarchical_logistic_fed_repo | weighted | 2020 | 2 | 0 | 7 / 7.00 >> 7 / 7.00 >> 8 / 7.50 |
| hierarchical_logistic_fed_repo | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| hierarchical_logistic_fed_repo | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| hierarchical_logistic_fed_repo | weighted | 2025-26 | 5 | 3 | 14 / 4.50 >> 14 / 4.50 >> 12 / 4.25 |
| hierarchical_logistic_fed_repo_sameday | unweighted | 2018-19 | 17 | 12 | 92 / 38.50 >> 92 / 38.50 >> 102 / 38.50 |
| hierarchical_logistic_fed_repo_sameday | unweighted | 2020 | 2 | 0 | 2 / 0.50 >> 2 / 0.50 >> 5 / 3.25 |
| hierarchical_logistic_fed_repo_sameday | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| hierarchical_logistic_fed_repo_sameday | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| hierarchical_logistic_fed_repo_sameday | unweighted | 2025-26 | 5 | 3 >> 3 >> 2 | 14 / 4.50 >> 14 / 4.50 >> 11 / 3.75 |
| hierarchical_logistic_fed_repo_sameday | weighted | 2018-19 | 17 | 12 | 131 / 60.00 >> 131 / 60.00 >> 146 / 64.75 |
| hierarchical_logistic_fed_repo_sameday | weighted | 2020 | 2 | 0 >> 0 >> 1 | 9 / 7.75 >> 9 / 7.75 >> 10 / 8.25 |
| hierarchical_logistic_fed_repo_sameday | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| hierarchical_logistic_fed_repo_sameday | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| hierarchical_logistic_fed_repo_sameday | weighted | 2025-26 | 5 | 3 | 16 / 5.25 >> 16 / 5.25 >> 13 / 4.75 |
| hierarchical_logistic_srf | unweighted | 2018-19 | 17 | 12 | 97 / 39.50 >> 97 / 39.50 >> 96 / 34.75 |
| hierarchical_logistic_srf | unweighted | 2020 | 2 | 0 | 1 / 0.25 >> 1 / 0.25 >> 2 / 2.00 |
| hierarchical_logistic_srf | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| hierarchical_logistic_srf | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| hierarchical_logistic_srf | unweighted | 2025-26 | 5 | 3 | 11 / 3.25 >> 11 / 3.25 >> 10 / 3.75 |
| hierarchical_logistic_srf | weighted | 2018-19 | 17 | 12 | 131 / 59.75 >> 131 / 59.75 >> 146 / 64.75 |
| hierarchical_logistic_srf | weighted | 2020 | 2 | 0 | 7 / 7.00 >> 7 / 7.00 >> 10 / 7.25 |
| hierarchical_logistic_srf | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| hierarchical_logistic_srf | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| hierarchical_logistic_srf | weighted | 2025-26 | 5 | 3 | 11 / 3.25 >> 11 / 3.25 >> 15 / 5.00 |
| hierarchical_logistic_srf_sameday | unweighted | 2018-19 | 17 | 12 | 97 / 40.50 >> 97 / 40.50 >> 97 / 37.50 |
| hierarchical_logistic_srf_sameday | unweighted | 2020 | 2 | 0 | 3 / 3.00 >> 3 / 3.00 >> 2 / 2.00 |
| hierarchical_logistic_srf_sameday | unweighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| hierarchical_logistic_srf_sameday | unweighted | 2024 | 2 | 0 | 0 / 0.00 |
| hierarchical_logistic_srf_sameday | unweighted | 2025-26 | 5 | 3 | 7 / 2.00 >> 7 / 2.00 >> 10 / 3.50 |
| hierarchical_logistic_srf_sameday | weighted | 2018-19 | 17 | 12 | 132 / 60.50 >> 132 / 60.50 >> 146 / 64.75 |
| hierarchical_logistic_srf_sameday | weighted | 2020 | 2 | 0 | 7 / 7.00 |
| hierarchical_logistic_srf_sameday | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| hierarchical_logistic_srf_sameday | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| hierarchical_logistic_srf_sameday | weighted | 2025-26 | 5 | 3 | 9 / 3.25 >> 9 / 3.25 >> 14 / 5.00 |

## Drift on `main` that is not #662

Committed -> old data under today's code: the four reading rows are identical in every cell, so for them the committed figures are comparable and
every difference above is the data's. The rows that do not read the columns differ only in the tier 3 cell: `hierarchical_logistic` and
`published_v1` go from fail to pass at tier 3 under both rules (flags, warned counts and false alarms per onset are identical). That is the judge
changing between the page and today (its table now reports "calibrated regimes tested" out of 2 where the page's counted 4), not #662; I
did not trace which change. It means the page's "tier 3 fails for every
candidate" statement is stale for reasons outside this directive; it is flagged here and not settled.
