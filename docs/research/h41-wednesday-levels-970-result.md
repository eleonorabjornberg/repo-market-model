# H.4.1 Wednesday levels beside the week averages, and what they do to the scarcity state (#970, H5)

**Development data, not a verdict.** A measurement: nothing is published or registered, no published declaration, panel or record changes,
and every column and field below is off in every published declaration. Which read the scarcity state should use is Eleonora's; this page
decides nothing. Declaration: `metadata/h41_wednesday_levels_970.json`. Script: `scripts/h41_wednesday_levels_970.py`.

## What was measured

The panel's `reserve_balances` is FRED's `WRESBAL` and its `tga` is `WTREGEN`: the **averages** over the week ending Wednesday, although
`docs/decisions/information-set.md`, `asof.py` and `docs/diagnosis-exceedance-flattening.md` call them Wednesday levels (finding #485,
item 5). The H.4.1 also publishes the Wednesday levels, `WRBWFRBL` (reserve balances) and `WDTGAL` (the Treasury General Account), in the
same release. They were fetched on 19 October 2026 (latest vintage, `tests/fixtures/snapshots/h41_wednesday_levels/`, checksums in the
declaration) and substituted, value for value, into the measurement panel's long rows in place of the averages of the same weeks: the declared
instant (the registry's 16:30 New York, five calendar days after the Wednesday), the vintage id and the source of every row are the average's
own, so a level is read at the print of its own release and not before ("same release, same instant"; `substitute()` keeps them and a test
checks it). All 1,203 Wednesdays of each series to 2025-12-31 were replaced and none dropped; the 35 later weeks keep their averages and are
read by no scored decision.

## The Wednesday level less the week average (USD billions)

| series | Wednesdays | mean | mean abs | 5th | median | 95th |
|---|---|---|---|---|---|---|
| WDTGAL less its week average (USD bn) | 1203 | 0.10 | 15.82 | -35.74 | -0.55 | 48.67 |
| WRBWFRBL less its week average (USD bn) | 1203 | -0.04 | 24.10 | -63.39 | 1.96 | 49.54 |

Over the 1,203 Wednesdays the two differ by 24 bn on average in absolute terms for reserves and 16 bn for the TGA, centred on zero: the average
is a different quantity from the level, not a noisy copy of it. The scarcity state reads reserves only; the TGA is reported for the record.

## The scarcity state formed from each

The own-leg read (#586, each leg at its own latest public row), every scored day 2018-06-29 to 2025-12-31, at each horizon, from the week average
(as now) and from the Wednesday level. The cut-points, the H.8 leg and the ON RRP leg are unchanged.

| horizon | scored days | change state | up | down | enter risky set | leave risky set |
|---|---|---|---|---|---|---|
| 1 | 1873 | 34 | 19 | 15 | 0 | 5 |
| 2 | 1872 | 33 | 19 | 14 | 0 | 5 |
| 3 | 1871 | 33 | 19 | 14 | 0 | 5 |
| 4 | 1870 | 33 | 19 | 14 | 0 | 5 |
| 5 | 1869 | 33 | 19 | 14 | 0 | 5 |

Changed days at horizon 1 by year: 2020: 5, 2023: 14, 2025: 15.

Movement is small: no day enters the risky set (state of 2 or more) and five leave it, at every horizon. The changed days fall in 2020, 2023 and
2025 (horizon 1).

## The pressure onsets

Pressure onsets (> 5 bp, horizon 1): 27; state changes at 0.

| onset | state, week average | state, Wednesday level |
|---|---|---|
| 2018-06-29 | 3.0 | 3.0 |
| 2018-11-15 | 3.0 | 3.0 |
| 2018-11-30 | 3.0 | 3.0 |
| 2018-12-17 | 3.0 | 3.0 |
| 2018-12-28 | 3.0 | 3.0 |
| 2019-01-15 | 3.0 | 3.0 |
| 2019-01-31 | 3.0 | 3.0 |
| 2019-02-28 | 3.0 | 3.0 |
| 2019-03-15 | 3.0 | 3.0 |
| 2019-03-29 | 3.0 | 3.0 |
| 2019-05-28 | 3.0 | 3.0 |
| 2019-06-17 | 3.0 | 3.0 |
| 2019-06-25 | 3.0 | 3.0 |
| 2019-08-13 | 3.0 | 3.0 |
| 2019-08-30 | 3.0 | 3.0 |
| 2019-10-15 | 3.0 | 3.0 |
| 2019-11-29 | 3.0 | 3.0 |
| 2019-12-16 | 3.0 | 3.0 |
| 2020-03-04 | 3.0 | 3.0 |
| 2020-03-12 | 3.0 | 3.0 |
| 2024-09-30 | 0.0 | 0.0 |
| 2024-12-26 | 0.0 | 0.0 |
| 2025-09-15 | 2.0 | 2.0 |
| 2025-09-30 | 2.0 | 2.0 |
| 2025-10-15 | 2.0 | 2.0 |
| 2025-12-15 | 3.0 | 3.0 |
| 2025-12-26 | 3.0 | 3.0 |

The onset list is the panel's own (a strict exceedance of 5 bp after the quiet days, `pressure.onsets`, descriptive here and not a decision rule: the
+5 bp judge is retired as a decision rule). It has 27 onsets over the scored days of horizon 1, where the earlier pages count 26; the difference is not
reconciled here. No onset's state changes.

## Reading

The kill condition (no movement anywhere) is **not** met: 34 scored days change state at horizon 1 (19 up, 15 down), and the same 33 or 34 at the
others. It is met at the onsets: none moves, so the state each pressure onset was read in is the same under either read. Reading the state from the Wednesday level is therefore a change to 34 of 1,873 days and to none of the onsets. Whether
to switch the read is Eleonora's.

## Not checked

- **Never revised.** Not re-verified. The directive asks for two ALFRED vintages of each series. `alfred.stlouisfed.org` is refused by this
  environment's proxy, and `fred.stlouisfed.org/graph/fredgraph.csv` ignores `vintage_date` (it returned the latest vintage). The values read are
  the latest vintage, as for the averages they sit beside. To check it, fetch two ALFRED vintages of each series
  (`https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=WRBWFRBL&vintage_date=2019-09-16`, and one after the 2025 data, likewise for `WDTGAL`) into a
  new directory and run `python3 scripts/alfred_vintages.py <files>`, which exits 1 on any restated observation.
- The effect on any forecast: no model is refitted here.
