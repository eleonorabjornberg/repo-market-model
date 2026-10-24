# Three market findings (#1177)

**Hypothesis and step:** H5 (primary goal), context for the pages; not a step of the plan and not a test of any model.

**Development data, not a verdict.** Descriptive: no forecast is scored, no model is fitted or compared, no locked day is read (`lockbox.require_unlocked` runs on every row), and no published record moves. Every figure is read from `docs/research/market-findings-1177/result.json` (panel digest `4ddc3882`, 2018-04-03 to 2026-09-03) or from `docs/research/state-calendar-1145/result.json`, arm (s1), by `scripts/market_findings_1177.py`. The pages (`site/plain.html`, the explorer) render these figures and type none.

## 1. Stress lives on the turn

Mean spread in bp (SOFR - IORB), with the number of days; median and the share of days above +5 bp beside it. Months that end a quarter are left out, as the turn definition in force (#1135, #1161) treats them apart.

| Regime | Day | Days | Mean | Median | Share above +5 bp |
|---|---|---|---|---|---|
| 2018-19 | Last business day of the month | 14 | +11.5 | +9.0 | 71% |
| 2018-19 | First business day of the next month | 14 | +4.0 | +4.0 | 43% |
| 2018-19 | Second-last business day | 14 | +0.3 | -0.5 | 7% |
| 2018-19 | Ordinary mid-month day | 139 | +1.7 | +1.0 | 21% |
| 2020 | Last business day of the month | 8 | -1.6 | -1.0 | 0% |
| 2020 | First business day of the next month | 8 | -1.9 | -1.0 | 0% |
| 2020 | Second-last business day | 8 | -2.9 | -2.0 | 0% |
| 2020 | Ordinary mid-month day | 77 | -0.7 | -1.0 | 4% |
| 2021-23 | Last business day of the month | 24 | -9.2 | -9.5 | 0% |
| 2021-23 | First business day of the next month | 24 | -8.8 | -9.5 | 0% |
| 2021-23 | Second-last business day | 24 | -9.7 | -10.0 | 0% |
| 2021-23 | Ordinary mid-month day | 233 | -9.7 | -10.0 | 0% |
| 2024 | Last business day of the month | 8 | -5.5 | -6.0 | 0% |
| 2024 | First business day of the next month | 8 | -5.8 | -5.5 | 0% |
| 2024 | Second-last business day | 8 | -8.0 | -8.0 | 0% |
| 2024 | Ordinary mid-month day | 78 | -7.7 | -8.0 | 0% |
| 2025-26 | Last business day of the month | 14 | +3.5 | +1.0 | 14% |
| 2025-26 | First business day of the next month | 14 | +2.1 | -0.5 | 21% |
| 2025-26 | Second-last business day | 14 | -0.5 | -2.5 | 14% |
| 2025-26 | Ordinary mid-month day | 133 | -3.8 | -3.0 | 8% |
| all regimes | Last business day of the month | 68 | -1.0 | -3.0 | 18% |
| all regimes | First business day of the next month | 68 | -2.8 | -4.5 | 13% |
| all regimes | Second-last business day | 68 | -4.8 | -7.0 | 4% |
| all regimes | Ordinary mid-month day | 660 | -4.8 | -7.0 | 6% |

### The first business day over every month

The directive's first-day figure for 2018-19 is the first business day of every month, quarter-ends and the year-end included. Read that way it is +8.1 bp over 21 days, with a median of +6.0 bp; read on the definition above (months that do not end a quarter) it is +4.0 bp over 14 days, median +4.0 bp. The wider mean carries the year-end first day, which printed far above the rest. **Question for Eleonora (not settled here):** which reading do the pages quote? They quote the definition in force.

## 2. The calendar sets the date; reserve scarcity sets the size

Per-term effects of arm (s1) of #1145 (`sc_s1_standardised`), in bp, with the 90% interval over the refits.

| Regime | Month-end | Coupon settlement |
|---|---|---|
| 2018-19 | +5.8 [+4.4, +7.2] (36 days) | +8.5 [+7.2, +9.8] (46 days) |
| 2020 | +2.2 [+1.3, +3.0] (24 days) | +2.5 [+1.7, +3.4] (34 days) |
| 2021-23 | +0.3 [+0.1, +0.5] (72 days) | +0.5 [+0.3, +0.7] (99 days) |
| 2024 | +1.8 [+1.3, +2.2] (24 days) | +1.5 [+1.0, +2.0] (32 days) |
| 2025-26 | +4.3 [+3.5, +5.0] (24 days) | +3.8 [+2.8, +4.9] (29 days) |

The table shows how large the same date was in each period. That reserve scarcity is what sets the size is the project's reading of the pattern, not something this table tests.

## 3. Stress episodes begin on known calendar dates

An episode starts on a day with a spread strictly above +5 bp after more than 10 business days with none. Listed from 2020-04-01; the 12 earlier episodes are counted and not listed (the latest began 2020-03-04). A known date is a month-end or quarter-end turn, a tax date, or a coupon settlement from the 13th to the 19th; "near" is one business day either side of the start.

| Start | Spread, bp | Known date on or next to it |
|---|---|---|
| 2024-09-30 | +6.0 | quarter-end |
| 2024-12-26 | +13.0 | none |
| 2025-09-15 | +11.0 | tax date, mid-month settlement |
| 2025-09-30 | +9.0 | quarter-end |
| 2026-02-17 | +6.0 | mid-month settlement |
| 2026-04-15 | +7.0 | tax date, mid-month settlement |

5 of 6 listed episodes began near a known date. For scale, 37% of the 1605 business days from 2020-04-01 on sit on or next to one.

**Questions for Eleonora (not settled here):** (1) The claim reads "since 2020"; the pages say "since 2020-04-01", which leaves out the March 2020 episode. (2) 1 listed episode(s) have no known date within a business day: 2024-12-26. Whether 26 December (`turn_days.december_26`, flagged apart by Lens A) or the days around a year-end count as a known date is a data meaning, so the pages state the count the rule gives.

## What this does not show

It is a description of one panel. It says nothing about a model, ranks nothing, and a share of days near a known date is a base rate, not a test. No interval is given for a mean because nothing here is compared.
