# `backfilled-history-result.md` re-run for #692: no result moves, because none of its forecasts reads a `fed_repo_*` column

Development data only; scored days are 2018-06-29 to 2025-12-31 (`docs/decisions/lockbox.md`). Nothing is edited in place and
nothing is published. Companion control: `docs/pivot/evidence/fed-repo-rescreen-692/data-diff.md`.

## What the record's forecasts read

The record (#430, #431) scores `hierarchical_logistic`, `calendar_climatology`, `persistence_logistic`, `published_v1`,
`two_part_gbm` and `ngboost_laplace`, with and without the back-filled 2014-2018 history. Every one is run **unchanged** on a
panel: the extended scratch panel (`scripts/backfill_history.py panel`), or the scratch panel and the published panel for the
arm without history. Which columns a forecast can read is therefore the panel's columns.

* The extended panel is the scratch panel of `pressure_v1_1.py panel` (the published panel's columns, `on_rrp`,
  `bank_total_assets`, `effr` and the scarcity state) with the back-filled months before 2018-04-03 added. It has 26 columns, and
  **none begins `fed_`** (checked on the built file). The Fed repo operations (`fed_repo_*`) are added by
  `scripts/fed_liquidity.py panel`, which `backfill_history.py panel` never calls.
* `backfill_history.py augment` joins whichever panel it is given onto the extended one. The record's reproduce block does not
  use it; `backfill-tier1-result.md` does, and gives it the `measurement_fields.py` panel (`SCRATCH_AUG.csv`), which is
  `AUG2.csv` of the data-control chain, byte-identical before and after #662.
* `grep` for `fed_repo`, `fed_liquidity` and `FED_REPO` over `scripts/*.py` and `src/repo_model/*.py` finds only
  `fed_liquidity.py` itself, its readers (`source_screen.py`, `source_matrix_629.py`, `desk_standard_diagnostic.py`,
  `unused_inputs.py`), `cli_data.py` and `ingest.py` (the fetch and the series), and `backfill.py` (the string
  `nyfed_repo_backfill`, a different source). None of the six forecasts' scripts or `ml.py` names a `fed_repo` column.

## Commands (current tree, base `ee9366eb`, and the same tree with the #662 files from `0db0471d^1`)

```
PYTHONPATH=src OMP_NUM_THREADS=1 python3 scripts/backfill_history.py panel --output EXT.csv --scratch SCRATCH.csv
```

Run once in each tree: about 14 seconds each, both exit 0.

| file | before (`0db0471d^1` readers) | after (current tree) | same |
|---|---|---|---|
| `SCRATCH.csv` (scratch panel) | `4137d0ad0ef82216deb011686bb03b17b8dc8fba11ae803221c9d735e29d4405` | `4137d0ad0ef82216deb011686bb03b17b8dc8fba11ae803221c9d735e29d4405` | yes |
| `EXT.csv` (extended panel, 2,834 rows, 899 back-filled, 2014-08-22 to 2025-12-31) | `f3acce045b700eec08af5a09204e7df255fd3a3860d04192a35ec841d8536285` | `f3acce045b700eec08af5a09204e7df255fd3a3860d04192a35ec841d8536285` | yes (`cmp` byte-identical) |
| workbook | `1c889930bca90edb58c6fe6c4d219f1366261ab9b3e5e0ad54d9a7e62e102180` | the same | yes |

The published panel (`PUB.csv`, `4ddc3882…`) is also identical in both trees (data control).

## Does the extended panel's `fed_repo` content differ at all?

It has none. The question the directive raised, whether the 2018-05 to 2019-09 overlap with the original panel's start matters,
therefore has the answer no: the changed rows (2018-05-09 to 2019-09-16) are published-panel rows, and in the extended panel
those rows carry no `fed_repo_*` cell in either tree. The back-filled rows (2014-08-22 to 2018-03-29) lie wholly before the
changed range (which starts 2018-05-09), and carry no `fed_repo_*` cell.

## Before and after, row by row

| row of the record | reads `fed_repo_*` | input panel before / after | result before / after |
|---|---|---|---|
| `hierarchical_logistic`, with and without history | no | identical | identical (same inputs, same code, deterministic) |
| `calendar_climatology` | no | identical | identical |
| `persistence_logistic` | no | identical | identical |
| `published_v1` | no | identical | identical |
| `two_part_gbm` (h = 1) | no | identical | identical |
| `ngboost_laplace` (h = 1) | no | identical | identical |

**No ranking, count or conclusion of the record moves.** The scores were not recomputed: with byte-identical input panels and
code that does not read the changed columns, the forecasts and their scores are the same by construction, and recomputing
them would reproduce the record's numbers, which are in a PR description that this tree does not hold.

## Not done, and why

* The forecasts and the judge were not re-run. The record's full tables live in the description of the pull request that added
  it, not in a tracked file, so a before/after of scores has no tracked "before" to compare to; the argument above (identical input
  panel, no `fed_repo` reader) is what the control rests on. If Eleonora wants a recomputed table anyway, note that the `with`-history
  rows can no longer be produced: `repo_model.backfill.require_posting_established` (#583) refuses any fit trained on
  back-filled values while `metadata/backfill_posting.json` declares no posting instant, as the record's own note says.
* The record's own note stands unchanged: its `with` rows are not evidence until the workbook's posting date is established.
