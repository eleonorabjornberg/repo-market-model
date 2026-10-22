# The afternoon test-trade rule and the take-up figures (#938)

**Serves:** H5 (the test-trade rule on Fed repo take-up as an input, #743; finding #860) and H3 groundwork G1 (data quality of the Fed repo take-up recency input, #872 / PR #884). **Development data, not a verdict:** no spread, forecast or score is read; no locked day counts toward a choice (scoring protocol v1, #640). Nothing here edits an earlier record: `docs/pivot/test-trade-802-result.md`, `docs/pivot/repo-test-trades-872-result.md` and `docs/pivot/desk-test-marks-933-result.md` stand and the figures below are published anew beside them.

**The rule** (Eleonora, ruling on #860 of 19 October 2026, read by her ruling on #938 of 20 October 2026). An overnight `Repo` operation with no note is a test trade, not take-up, if it was released at 13:29 or 13:30, its main line (the largest accepted line) is $90-130 mn, and every other line that accepted anything is under $10 mn. It reads only the operation's own results release (`ingest._is_afternoon_test_trade`). The two 08:15 operations are regular operations (#884 section 2) and stay take-up. The operation still happened, so its date keeps a row, at zero.

## 1. The 35 un-noted operations of PR #884 and what catches them

The rule catches 32 of 35. The Desk marks of #933 (id ends " 99", or limit at most $250 mn) catch 0 of them; both rules catch 0; neither catches 3.

| date | id | release | method | lines ($ mn) | rate (%) | accepted ($ mn) | caught by |
|---|---|---|---|---|---|---|---|
| 2024-02-22 | `RP 022224 2` | 13:29 | Multiple Price | 102, 2, 2 | 5.5 | 106 | pattern (#938) |
| 2024-03-07 | `RP 030724 2` | 13:30 | Multiple Price | 110 | 5.5 | 110 | pattern (#938) |
| 2024-04-18 | `RP 041824 2` | 13:30 | Multiple Price | 112, 1 | 5.5 | 113 | pattern (#938) |
| 2024-05-16 | `RP 051624 2` | 13:30 | Multiple Price | 100 | 5.5 | 100 | pattern (#938) |
| 2024-06-05 | `RP 060524 2` | 13:30 | Multiple Price | 104, 2 | 5.5 | 106 | pattern (#938) |
| 2024-06-13 | `RP 061324 2` | 13:30 | Multiple Price | 100 | 5.5 | 100 | pattern (#938) |
| 2024-07-09 | `RP 070924 2` | 13:30 | Multiple Price | 97 | 5.5 | 97 | pattern (#938) |
| 2024-07-11 | `RP 071124 2` | 13:30 | Multiple Price | 102 | 5.5 | 102 | pattern (#938) |
| 2024-08-08 | `RP 080824 2` | 13:30 | Multiple Price | 101 | 5.5 | 101 | pattern (#938) |
| 2024-09-10 | `RP 091024 2` | 13:30 | Multiple Price | 102, 1 | 5.5 | 103 | pattern (#938) |
| 2024-10-03 | `RP 100324 2` | 13:30 | Multiple Price | 102 | 5.0 | 102 | pattern (#938) |
| 2024-11-06 | `RP 110624 2` | 13:30 | Multiple Price | 101 | 5.0 | 101 | pattern (#938) |
| 2024-12-10 | `RP 121024 2` | 13:30 | Multiple Price | 100 | 4.75 | 100 | pattern (#938) |
| 2025-02-11 | `RP 021125 2` | 13:30 | Multiple Price | 100 | 4.5 | 100 | pattern (#938) |
| 2025-02-12 | `RP 021225 2` | 13:30 | Multiple Price | 100 | 4.5 | 100 | pattern (#938) |
| 2025-03-11 | `RP 031125 2` | 13:30 | Multiple Price | 100 | 4.5 | 100 | pattern (#938) |
| 2025-04-08 | `RP 040825 2` | 13:30 | Multiple Price | 100 | 4.5 | 100 | pattern (#938) |
| 2025-04-30 | `RP 043025 2` | 13:30 | Multiple Price | 10, 100 | 4.5 | 110 | neither |
| 2025-05-06 | `RP 050625 2` | 13:30 | Multiple Price | 100 | 4.5 | 100 | pattern (#938) |
| 2025-06-10 | `RP 061025 2` | 13:30 | Multiple Price | 102, 1, 2 | 4.5 | 105 | pattern (#938) |
| 2025-07-08 | `RP 070825 3` | 13:29 | Multiple Price | 100 | 4.5 | 100 | pattern (#938) |
| 2025-08-12 | `RP 081225 3` | 13:30 | Multiple Price | 101 | 4.5 | 101 | pattern (#938) |
| 2025-09-09 | `RP 090925 3` | 13:30 | Multiple Price | 100, 1 | 4.5 | 101 | pattern (#938) |
| 2025-10-03 | `RP 100325 3` | 13:30 | Multiple Price | 105 | 4.25 | 105 | pattern (#938) |
| 2025-12-09 | `RP 120925 27` | 13:30 | Multiple Price | 102 | 4.0 | 102 | pattern (#938) |
| 2026-01-13 | `RP 011326 27` | 13:30 | Full Allotment | 102 | none stated | 102 | pattern (#938) |
| 2026-02-10 | `RP 021026 27` | 13:30 | Full Allotment | 100 | none stated | 100 | pattern (#938) |
| 2026-03-10 | `RP 031026 27` | 13:30 | Full Allotment | 102, 2 | none stated | 104 | pattern (#938) |
| 2026-04-08 | `RP 040826 25` | 08:15 | Full Allotment | 100 | none stated | 100 | neither |
| 2026-05-12 | `RP 051226 26` | 13:30 | Full Allotment | 101 | none stated | 101 | pattern (#938) |
| 2026-06-09 | `RP 060926 27` | 13:30 | Full Allotment | 101 | none stated | 101 | pattern (#938) |
| 2026-07-14 | `RP 071426 27` | 13:30 | Full Allotment | 100 | none stated | 100 | pattern (#938) |
| 2026-07-15 | `RP 071526 25` | 08:15 | Full Allotment | 100 | none stated | 100 | neither |
| 2026-08-11 | `RP 081126 27` | 13:30 | Full Allotment | 100 | none stated | 100 | pattern (#938) |
| 2026-08-27 | `RP 082726 27` | 13:30 | Full Allotment | 100 | none stated | 100 | pattern (#938) |

Not caught by either: `RP 043025 2` (2025-04-30, 13:30, lines 10, 100), `RP 040826 25` (2026-04-08, 08:15, lines 100), `RP 071526 25` (2026-07-15, 08:15, lines 100). Two are 08:15 regular operations; the third has a $10 mn accompanying line, which is not under $10 mn.

## 2. Marked questions for Eleonora

* **The count.** The ruling comment says "31 of 35"; the rule as the comment words it catches 32. Reading "under $10 mn" as "up to $10 mn" would catch 33. The rule is implemented as worded (strictly under $10 mn, 13:29 and 13:30 both). Which reading produced 31 is not known here.
* **13:29 releases** (the ruling says 13:29-13:30, so they are caught): `RP 022224 2`, `RP 070825 3`.
* **A $10 mn accompanying line** (not caught, being not under $10 mn): `RP 043025 2`.
* **"Single rate" on Full Allotment rows.** 8 caught operations are Full Allotment and state no rate. The rule counts a main line with no stated rate as having one rate (only a main line whose own low and high rate differ is excluded). Whether a missing rate should count is hers.
* **The band edges.** The caught main lines run from $97 mn to $112 mn; operations within $3 mn of $90 mn or $130 mn: none.

## 3. `fed_repo_days_since_positive`, longest value / take-up days, by year

| year | before (#933 marks) | this rule | the 35 listed (the 17 October list reading, PR #884) |
|---|---|---|---|
| 2018 | 250 / 0 | 250 / 0 | 250 / 0 |
| 2019 | 250 / 72 | 250 / 72 | 250 / 72 |
| 2020 | 124 / 124 | 124 / 124 | 124 / 124 |
| 2021 | 250 / 0 | 250 / 0 | 250 / 0 |
| 2022 | 250 / 3 | 250 / 3 | 250 / 3 |
| 2023 | 63 / 14 | 63 / 14 | 63 / 14 |
| 2024 | 50 / 23 | 134 / 10 (moves) | 134 / 10 |
| 2025 | 32 / 55 | 61 / 44 (moves) | 62 / 43 |
| 2026 | 17 / 27 | 27 / 19 (moves) | 27 / 17 |
| 2024-01 to 2026-09 | 50 / 105 | 134 / 73 | |

317 of 2104 panel dates change in `fed_repo_accepted` or `fed_repo_days_since_positive` (counts by year; the dates are in `result.json`): 2024: 171, 2025: 94, 2026: 52.

## 4. The Standing Repo Facility total (`srf_total_accepted`, USD bn)

| date | before | after |
|---|---|---|
| 2024-02-22 | 0.106 | 0.0 |
| 2024-03-07 | 0.11 | 0.0 |
| 2024-04-18 | 0.113 | 0.0 |
| 2024-05-16 | 0.1 | 0.0 |
| 2024-06-05 | 0.106 | 0.0 |
| 2024-06-13 | 0.1 | 0.0 |
| 2024-07-09 | 0.097 | 0.0 |
| 2024-07-11 | 0.102 | 0.0 |
| 2024-08-08 | 0.101 | 0.0 |
| 2024-09-10 | 0.103 | 0.0 |
| 2024-10-03 | 0.102 | 0.0 |
| 2024-11-06 | 0.101 | 0.0 |
| 2024-12-10 | 0.1 | 0.0 |
| 2025-02-11 | 0.1 | 0.0 |
| 2025-02-12 | 0.1 | 0.0 |
| 2025-03-11 | 0.1 | 0.0 |
| 2025-04-08 | 0.1 | 0.0 |
| 2025-05-06 | 0.1 | 0.0 |
| 2025-06-10 | 0.105 | 0.0 |
| 2025-07-08 | 0.1 | 0.0 |
| 2025-08-12 | 0.101 | 0.0 |
| 2025-09-09 | 0.101 | 0.0 |
| 2025-10-03 | 0.105 | 0.0 |
| 2025-12-09 | 0.102 | 0.0 |
| 2026-01-13 | 0.102 | 0.0 |
| 2026-02-10 | 0.1 | 0.0 |
| 2026-03-10 | 0.104 | 0.0 |
| 2026-05-12 | 0.101 | 0.0 |
| 2026-06-09 | 0.101 | 0.0 |
| 2026-07-14 | 0.1 | 0.0 |
| 2026-08-11 | 0.1 | 0.0 |
| 2026-08-27 | 0.1 | 0.0 |

Dates with a positive total: 122 before, 90 after.

## Not re-run

The ordinary-day AUROC and 2018-warning matrices of `docs/pivot/test-trade-802-result.md` (the retired +5 bp judge, the `ml` extra, five horizons by several arms) are not re-run here; the PR says so and proposes it as a `needs-mac` step if Eleonora wants it.

## Reproduce

```
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --end 2026-09-03 --output /tmp/AUG.csv
PYTHONPATH=src python3 scripts/afternoon_test_trade_938.py --panel /tmp/AUG.csv --write
```
