# The split test-trade rule and the take-up figures (#1456)

**Serves:** H9 (secondary goal; `srf_total_accepted`) and H5 inputs (the `fed_repo_*` columns). Exploration on development data only: no verdict (scoring protocol v1, #640). No spread, forecast or score is read; no locked day counts toward a choice. Nothing here edits an earlier record: `docs/pivot/desk-test-marks-933-result.md` and `docs/pivot/afternoon-test-trade-938-result.md` stand and the figures below are published anew beside them.

**The rule** (Eleonora, 4 November 2026, option (a) on finding #916): a `Repo` operation that accepted more than nothing and at most USD 35 million in total (`ingest.SPLIT_TEST_TOTAL_MAX`), split equally across the lines that accepted anything (at least two), is a Desk test trade, not take-up. It is read after the Desk-test marks and beside the rules of #802 and #938, by `ingest._effective_taken`. The date keeps a row, at zero.

## 1. The $10 mn / $0 / $10 mn days (13)

| date | operation | release | lines (mn) |
|---|---|---|---|
| 2024-09-16 | `RP 091624 2` | 13:30 | 10, 0, 10 |
| 2024-10-17 | `RP 101724 2` | 13:30 | 10, 0, 10 |
| 2024-10-28 | `RP 102824 2` | 13:30 | 10, 0, 10 |
| 2024-12-09 | `RP 120924 2` | 13:30 | 10, 0, 10 |
| 2025-08-25 | `RP 082525 1` | 08:15 | 10, 0, 10 |
| 2025-08-27 | `RP 082725 1` | 08:15 | 10, 0, 10 |
| 2025-10-06 | `RP 100625 3` | 13:30 | 10, 0, 10 |
| 2026-01-05 | `RP 010526 27` | 13:30 | 10, 0, 10 |
| 2026-02-09 | `RP 020926 27` | 13:30 | 10, 0, 10 |
| 2026-03-23 | `RP 032326 26` | 13:30 | 10, 0, 10 |
| 2026-05-04 | `RP 050426 27` | 13:30 | 10, 0, 10 |
| 2026-06-16 | `RP 061626 26` | 13:30 | 10, 0, 10 |
| 2026-07-27 | `RP 072726 26` | 13:30 | 10, 0, 10 |

## 2. Other equal splits the rule as ruled also reaches (7): MARKED QUESTION for Eleonora

These are not $10 mn / $0 / $10 mn operations, but they meet the ruled wording (total at most $35 mn, equal across the accepted lines). The rule as written reclassifies them; the earlier finding on #916 counted them as take-up.

| date | operation | release | total (mn) | lines (mn) |
|---|---|---|---|---|
| 2022-10-19 | `RP 101922 2` | 13:30 | 10 | 5, 0, 5 |
| 2024-09-23 | `RP 092324 2` | 13:30 | 15 | 5, 5, 5 |
| 2025-03-25 | `RP 032525 2` | 13:30 | 30 | 10, 10, 10 |
| 2025-09-22 | `RP 092225 3` | 13:30 | 30 | 10, 10, 10 |
| 2026-03-19 | `RP 031926 27` | 13:30 | 30 | 10, 10, 10 |
| 2026-05-26 | `RP 052626 26` | 13:30 | 30 | 15, 0, 15 |
| 2026-09-03 | `RP 090326 27` | 13:30 | 33 | 11, 11, 11 |

## 3. `fed_repo_days_since_positive`, longest value / take-up days, by year

| year | before | after |
|---|---|---|
| 2018 | 250 / 0 | 250 / 0 |
| 2019 | 250 / 72 | 250 / 72 |
| 2020 | 124 / 124 | 124 / 124 |
| 2021 | 250 / 0 | 250 / 0 |
| 2022 | 250 / 3 | 250 / 2 (moves) |
| 2023 | 63 / 14 | 63 / 14 |
| 2024 | 134 / 10 | 134 / 5 (moves) |
| 2025 | 61 / 44 | 86 / 39 (moves) |
| 2026 | 27 / 19 | 36 / 10 (moves) |

203 of 2104 panel dates change in `fed_repo_accepted` or `fed_repo_days_since_positive` (the dates are in `result.json`).

## 4. The Standing Repo Facility total (`srf_total_accepted`, USD bn)

| date | before | after |
|---|---|---|
| 2022-10-19 | 0.01 | 0.0 |
| 2024-09-16 | 0.02 | 0.0 |
| 2024-09-23 | 0.015 | 0.0 |
| 2024-10-17 | 0.02 | 0.0 |
| 2024-10-28 | 0.02 | 0.0 |
| 2024-12-09 | 0.02 | 0.0 |
| 2025-03-25 | 0.03 | 0.0 |
| 2025-08-25 | 0.02 | 0.0 |
| 2025-08-27 | 0.02 | 0.0 |
| 2025-09-22 | 0.03 | 0.0 |
| 2025-10-06 | 0.02 | 0.0 |
| 2026-01-05 | 0.02 | 0.0 |
| 2026-02-09 | 0.02 | 0.0 |
| 2026-03-19 | 0.03 | 0.0 |
| 2026-03-23 | 0.02 | 0.0 |
| 2026-05-04 | 0.02 | 0.0 |
| 2026-05-26 | 0.03 | 0.0 |
| 2026-06-16 | 0.02 | 0.0 |
| 2026-07-27 | 0.02 | 0.0 |
| 2026-09-03 | 0.033 | 0.0 |

Operation days with a positive total, 2021-07-29 to 2025-12-31: 71 before, 60 after (the recount that `docs/DATA_QUALITY_DECISIONS.md` states and `NyFedSrfAdapterTests` checks).

## Reproduce

```
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --end 2026-09-03 --output /tmp/AUG.csv
PYTHONPATH=src python3 scripts/split_test_trade_1456.py --panel /tmp/AUG.csv --write
```
