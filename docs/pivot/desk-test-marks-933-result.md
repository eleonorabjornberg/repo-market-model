# The Desk-test marks and the take-up figures (#933)

**Serves:** H5 (the test-trade rule on Fed repo take-up as an input, #743) and H9 step 1 (standing repo facility take-up, #659). Exploration on development data only: no verdict (scoring protocol v1, #640). No spread, forecast or score is read; no locked day counts toward a choice. Nothing here edits an earlier record: `docs/pivot/test-trade-802-result.md` and the #908 counts stand and the figures below are published anew beside them.

**The rule** (Eleonora, 19 October 2026, ruling on #916): a `Repo` operation whose id ends " 99", or whose `operationLimit` is at most $250 mn, is a Desk test (small-value exercise), like one whose `note` says so. It is dropped before the test-trade rule of #802.

## 1. Repo operations the marks drop and the note did not

| date | operation | term | limit | accepted | mark |
|---|---|---|---|---|---|
| 2020-06-17 | `RP 061720 99` | Overnight | none | $53 mn | id ends 99 |
| 2020-10-07 | `RP 100720 99` | Overnight | none | $59 mn | id ends 99 |
| 2021-05-26 | `RP 052621 99` | Overnight | none | $46 mn | id ends 99 |
| 2023-03-08 | `RP 030823 1` | Term | $75 mn | $56 mn | limit <= 250 mn |
| 2023-05-23 | `RP 052323 99` | Overnight | $100 mn | $76 mn | id ends 99 |
| 2024-09-24 | `RP 092424 1` | Term | $75 mn | $57 mn | limit <= 250 mn |

## 2. `fed_repo_days_since_positive`, longest value / take-up days, by year

| year | note only (before) | marks (in force) |
|---|---|---|
| 2018 | 250 / 0 | 250 / 0 |
| 2019 | 250 / 72 | 250 / 72 |
| 2020 | 66 / 125 | 124 / 124 (moves) |
| 2021 | 156 / 1 | 250 / 0 (moves) |
| 2022 | 250 / 3 | 250 / 3 |
| 2023 | 39 / 16 | 63 / 14 (moves) |
| 2024 | 50 / 24 | 50 / 23 (moves) |
| 2025 | 32 / 55 | 32 / 55 |
| 2026 | 17 / 27 | 17 / 27 |

453 of 2104 panel dates change in `fed_repo_accepted` or `fed_repo_days_since_positive` (counts by year; the dates are in `result.json`): 2020: 59, 2021: 250, 2022: 99, 2023: 41, 2024: 4.

## 3. The Standing Repo Facility total (`srf_total_accepted`, USD bn)

| date | before | after |
|---|---|---|
| 2023-05-23 | 0.076 | 0.0 |

## 4. Not ruled, unchanged

The $10 mn / $0 / $10 mn split pattern (a $20 mn operation) appears on 13 days and is counted as take-up exactly as before; it is open for Eleonora (#916): 2024-09-16, 2024-10-17, 2024-10-28, 2024-12-09, 2025-08-25, 2025-08-27, 2025-10-06, 2026-01-05, 2026-02-09, 2026-03-23, 2026-05-04, 2026-06-16, 2026-07-27.

## Reproduce

```
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --end 2026-09-03 --output /tmp/AUG.csv
PYTHONPATH=src python3 scripts/desk_test_marks_933.py --panel /tmp/AUG.csv --write
```
