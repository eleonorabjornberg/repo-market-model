# Re-running the seven records that read the Fed repo take-up columns (#692)

**Serves:** H2, H3 and H9 inputs (data work after #659). **Exploration on development data only:** no verdict for any hypothesis under
scoring protocol v1 (#640). No 2026 day is read (`docs/decisions/lockbox.md`), nothing is published, `repo_term_outstanding` stays off
`FEATURE_FIELDS`, and no earlier record is edited: the figures below are published anew and supersede the older ones where they differ.

**Why.** #659 (PR #662) changed the Fed repo take-up columns: the six test operations before 2019-09-17 are no longer counted, and
`fed_repo_days_since_positive` no longer restarts at each test. `docs/pivot/fed-repo-data-meaning-result.md` listed seven records that read
these columns and were not re-scored. Eleonora's instruction on #692 was to re-run them unchanged, apart from the data.

**Control: what the data change touches** (`evidence/fed-repo-rescreen-692/data-diff.md`). Panel `4ddc3882…` is identical before and after. In the
scratch panel only 14 `fed_repo_*` columns differ, on 339 rows from 2018-05-09 to 2019-09-16; the other columns, and every row from 2019-09-17,
are identical. Where a re-run below also differs from the committed figure on a row that does not read these columns, the cause is other
changes on main since the record (named in each `before-after.md`), not #662. Each re-run was also made with the three pre-#662 files
(`fed_liquidity.py`, `ingest.py`, `sources_measurement.json`) restored, which isolates #662 alone ("old data" control).

| record | evidence (before/after tables with intervals in `before-after.md`) | did a ranking or conclusion move? |
|---|---|---|
| `source-screen-result.md` | `evidence/source-screen-692/` | No. Table 1 is the same 12 series in the same order. `fed_repo_days_since_positive` pooled correlation with a pressure day +0.065 to +0.129 at lead 1; its rank 35 to 27 of 76, far below the cut-off at rank 12. The 2018 cells of the `fed_repo_*` series are now empty (constant after #662); before, they showed the test operations. |
| `source-matrix-ordinary-days-result.md` | `evidence/source-matrix-692/` | No. Redundancy groups identical; Table 2 is the same 25 series. Pressure AUROC of `fed_repo_days_since_positive` on ordinary days, lead 1: 0.58 [0.43, 0.72] to 0.64 [0.48, 0.79]; lead 10: 0.61 [0.45, 0.75] to 0.68 [0.51, 0.82]. Rest of the family moves by at most 0.02. Two of 505 uncorrected cells newly exclude 0.5 (lower bounds at leads 5 and 10). |
| `unused-inputs-result.md` | `evidence/unused-inputs-692/` | Verdicts: no. Every model fails the pass rule before and after. Ranking among overlapping rows: `risk_gbm_base_dealer` 4th to 2nd by averaged paired Brier difference. Sentences that no longer hold: "the missed years stay missed" (`risk_logistic_base_dealer` now flags 3 of 5 onsets of 2018, 15 to 17 of 27 in total, 2025 5 to 4 of 5); three paired-Brier cells change whether the interval excludes zero (largest change in a dealer row 0.0009). |
| `ofr-followup-result.md` | `evidence/ofr-followup-692/` | Verdicts: no. Ranking: `risk_quantile_skewt_base_dealer_ofr` 4th to 2nd and its average changes sign (+0.0022 to -0.0001); `risk_logistic_base_dealer_ofr` flags 3 of 5 onsets of 2018 (recall 0.577 to 0.692 [0.517, 0.844], overlapping the passers'); four paired-Brier cells stop excluding zero. With the old data this record reproduces exactly, so all of these changes are #662's. |
| `weighted-miss-result.md` | `evidence/weighted-miss-692/` | Four of its 64 rows read the columns (`hierarchical_logistic_fed_repo`, `_fed_repo_sameday`, `_srf`, `_srf_sameday`). Tier 1 still fails for all four under both rules. Tier 3 goes fail to pass for all four and tier 5 pass to fail for `_fed_repo_sameday`; flat false alarms per onset rise (e.g. `_fed_repo` 3.73 to 4.23 unweighted). |
| `backfilled-history-result.md` | `evidence/backfilled-history-692/` | No. The extended panel has no `fed_repo_*` column and is byte-identical in both trees (`f3acce04…`); no forecast there reads one. |
| `new-sources-due-diligence.md` | `evidence/fed-repo-rescreen-692/due-diligence-check.md` | No. A table of sources, not a scored screen; no statement or figure depends on the take-up values. |

`weighted-miss-in-force-result.md` scores only models that do not read the columns and was not re-run.

## Findings that are not #662's (for Eleonora)

* The committed unused-inputs and OFR tables show tier 1 as met for rows that read "no" under today's judge (it decides tier 1 on a pooled
  false-alarm count), with the old data as well as the new. "All nineteen models meet tier 1" (unused-inputs) is stale; so is "tier 3 fails for
  every candidate" (weighted-miss: the non-reading rows `hierarchical_logistic` and `published_v1` also flip with the old data).
* Source-screen and source-matrix: a few non-Fed series differ from the committed figures because of changes on main since (the OFR real-time
  guard #522 for the two DVP series; the net-settlement fixes #618/#620 and the satiation columns). Rebuilding at the records' own commits
  reproduces both committed JSONs byte for byte, so these are real changes, not drift in the harness.
* `source_matrix_629.py run` refuses any panel whose sha256 is not the declared `8299bac3…`, so a corrected panel cannot be run through it
  unmodified. The re-run used an uncommitted scratch wrapper that swaps the rebuilt panel's own sha256 into that one check; the re-run
  JSON records `scope.panel_sha256 = a6f14260…`. How a published re-run should handle this pin is Eleonora's call.

## Not checked, or for Eleonora

* Whether to amend the stale sentences on the older pages (none is edited here).
* The judge gives AUROC no interval, so the interval-carrying comparison for the judged records is the paired Brier difference; the source
  screen draws no intervals by design (the matrix gives AUROC intervals for the same columns).
* The original forecast JSONs of the judged records were not kept, so "before" is the committed evidence files.
* Settle-group rows in unused-inputs move by up to 0.0020 for reasons attributed to #618/#620 by date, not bisected.

## Reproduce

Each directory's `before-after.md` lists its commands; they are the "Reproduce" commands of the record, unchanged. The control is
`evidence/fed-repo-rescreen-692/data-diff.md`.
