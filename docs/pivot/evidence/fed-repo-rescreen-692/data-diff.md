# Data control for the re-screens of #692: what #662 changed in the scratch panel, and nothing else

Development data only. The panel's last row is 2025-12-31; no 2026 day is read (`docs/decisions/lockbox.md`). Nothing here is
edited in place, and nothing is published.

Two scratch chains were built from the same tracked fixtures with the commands of `docs/pivot/source-screen-result.md`
("Reproduce", up to `fed_liquidity.py` and its `AUG5.csv`):

* **after:** the current tree, base `ee9366eb` (it contains #662, merge `0db0471d`).
* **before:** the same tree with the three files #662 changed and that the chain reads put back as they were in `0db0471d^1`
  (`7b8fd686`): `src/repo_model/fed_liquidity.py`, `src/repo_model/ingest.py`, `metadata/sources_measurement.json`. (The
  other files of #662 are test files and documents, which the chain does not read.) Nothing else differs between the two trees
  (`diff -rq` over `src/`, `scripts/` and `metadata/` shows exactly those three files).

```
PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
PYTHONPATH=src python3 -m repo_model.cli verify-panel PUB.csv --manifest metadata/funding_panel_manifest.json
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
PYTHONPATH=src python3 scripts/net_settlement.py panel --panel AUG2.csv --output AUG3.csv
PYTHONPATH=src python3 scripts/policy_features.py panel --panel AUG3.csv --output AUG4.csv
PYTHONPATH=src python3 scripts/fed_liquidity.py panel --panel AUG4.csv --output AUG5.csv
```

Each chain ran in about 20 seconds (`OMP_NUM_THREADS=1`).

## Digests (sha256)

| file | before (`0db0471d^1` readers) | after (current tree) | same |
|---|---|---|---|
| `PUB.csv` (the published panel) | `4ddc3882cd6d406b11e1088f8ff6195e16dde175a0ad6818abe40dd5bdac8999` | `4ddc3882cd6d406b11e1088f8ff6195e16dde175a0ad6818abe40dd5bdac8999` | yes |
| `PUB_point_in_time.csv` | `225f6f0a424b3e78121e8a569bc7fe77be5e686104cd58705ebd72001bbd3fe8` | `225f6f0a424b3e78121e8a569bc7fe77be5e686104cd58705ebd72001bbd3fe8` | yes |
| `AUG.csv` | `4137d0ad0ef82216deb011686bb03b17b8dc8fba11ae803221c9d735e29d4405` | `4137d0ad0ef82216deb011686bb03b17b8dc8fba11ae803221c9d735e29d4405` | yes |
| `AUG2.csv` | `5821868c174b44877348a7f34fdbafad25a4aead66ec84372b92ab734283547b` | `5821868c174b44877348a7f34fdbafad25a4aead66ec84372b92ab734283547b` | yes |
| `AUG3.csv` | `d1e99c6abf512b511a639e4f0869da1efa3447645daaa9699c796fa86065f0eb` | `d1e99c6abf512b511a639e4f0869da1efa3447645daaa9699c796fa86065f0eb` | yes |
| `AUG4.csv` | `35a16058c4ef22d3087d3ba642e252412242e39084a673d5b01426be35ea70a2` | `35a16058c4ef22d3087d3ba642e252412242e39084a673d5b01426be35ea70a2` | yes |
| `AUG5.csv` | `a86f751e5a9262084d8253bceefb5659639576dce798afc27d6fc12b44358d81` | `acd650bf4f3e1cab855d80fe95e3707f7ba12312d793670440602ad37359f4a7` | **no** |

The published panel and every stage before `fed_liquidity.py` are byte-identical; the first and only stage that differs is the
one that reads the Fed repo operations. Both `AUG5.csv` have 1,935 rows (2018-04-03 to 2025-12-31) and the same 62 columns in
the same order.

## Cell-by-cell comparison of `AUG5.csv`

Compared cell as text, row by row (the rows carry the same dates). **339 rows differ, all between 2018-05-09 and 2019-09-16, and
only in the 14 `fed_repo_*` columns below. The other 48 columns are identical on every row. All 1,570 rows from 2019-09-17
to 2025-12-31 are identical in every column, and so are the 26 rows before 2018-05-09.** (26 + 339 + 1,570 = 1,935.)

| column | rows that differ | dates | before | after |
|---|---|---|---|---|
| `fed_repo_accepted`, `fed_repo_submitted` | 6 | 2018-05-09, 2018-05-16, 2018-11-15, 2018-12-04, 2019-05-08, 2019-05-13 | 0.064, 0.065, 0.066, 0.066, 0.065, 0.065 | 0.0 |
| `fed_repo_ops` | 6 | the same six | 1.0 | 0.0 |
| `fed_repo_log_accepted` | 6 | the same six | 0.0620, 0.0630, 0.0639, 0.0639, 0.0630, 0.0630 | 0.0 |
| `fed_repo_rate_iorb_bps` | 6 | the same six | -4.625, -3.308, 7.652, 5.303, 7.338, 2.338 | 0.0 |
| `fed_repo_log_accepted_change` | 12 | the six and the next panel day: 2018-05-10, 2018-05-17, 2018-11-16, 2018-12-06, 2019-05-09, 2019-05-14 | +x on the test date, -x on the day after | 0.0 |
| `fed_repo_days_since_positive` | 339 | every panel row 2018-05-09 to 2019-09-16 | zero on a test date, then counting up (to 125 at most, restarting at each test) | 250 (the cap) on all 339 rows |
| `fed_repo_accepted_sameday`, `fed_repo_submitted_sameday` | 6 | the same six | as the next-day columns | 0.0 |
| `fed_repo_ops_sameday`, `fed_repo_log_accepted_sameday`, `fed_repo_rate_iorb_bps_sameday` | 6 each | the same six | as the next-day columns | 0.0 |
| `fed_repo_log_accepted_change_sameday` | 12 | the same twelve | as the next-day column | 0.0 |
| `fed_repo_days_since_positive_sameday` | 339 | 2018-05-09 to 2019-09-16 | as the next-day column | 250 |

(The day after 2018-12-04 is 2018-12-06: the panel has no 2018-12-05 row.) From 2019-09-17 the new `fed_repo_days_since_positive`
is 0 (the facility's first day), as before.

Reading: this is exactly the change `docs/pivot/fed-repo-data-meaning-result.md` states ("What moved in the data"): the take-up
columns on the six test dates, the change column on those and the day after, and `fed_repo_days_since_positive` on the rows from
2018-05-09 to 2019-09-16, held at its cap until the facility's first day. Nothing from 2019-09-17 on moves, and no column
outside the `fed_repo_*` family moves on any date. Every re-screen of #692 therefore differs from its committed version, on its
development data, only through these cells; a result that moves must trace to them.

## Reproduce the comparison

Build the two chains as above (the "before" tree restores the three files from `0db0471d^1` with `git show 0db0471d^1:<path>`),
then compare `AUG5.csv` of each cell by cell on `date`.
