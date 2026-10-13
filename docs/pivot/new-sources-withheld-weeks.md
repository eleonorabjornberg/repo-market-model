# Withheld weeks in the primary dealer financing series, and the carry cap (#680)

**Serves:** H3 (new public data adds signal), step 1 (#630's sources). An exploratory measurement, not a record and not a verdict: the columns stay
off every published declaration, so no published figure moves. No day after 2025-12-31 is read (`docs/decisions/lockbox.md`).

## What was wrong

#630 (PR #646) read the New York Fed's primary dealer export, skipped each withheld (`*`) value without a trace, carried each weekly value forward on the panel with
no limit (up to 90 days in the tracked extract), and said in three places that the series have "no gap". That broke the decided rule: a weekly carry stops after
`data.WEEKLY_CARRY_MAX_STALENESS_DAYS` (13 days, `docs/decisions/weekly-carry.md`) and the cell is then a hole.

## The withheld weeks

From `docs/pivot/evidence/new-sources-capped/withheld.json` (`python3 scripts/new_sources.py withheld`), over the tracked extract up to 2025-12-31:

| column | weekly dates | withheld | longest run (weeks) | years withheld |
|---|---|---|---|---|
| `pd_repo_ust` | 666 | 85 | 12 (2025-01-08 to 2025-03-26) | 2022: 15, 2023: 16, 2024: 21, 2025: 33 |
| `pd_reverse_repo_ust` | 666 | 72 | 9 (2025-04-16 to 2025-06-11) | 2022: 17, 2023: 13, 2024: 16, 2025: 26 |
| `pd_repo_mbs` | 666 | 3 | 1 (2022-08-03) | 2022: 1, 2024: 1, 2025: 1 |
| `pd_fails_deliver_ust` | 666 | 0 | 0 | none |
| `pd_fails_receive_ust` | 666 | 0 | 0 | none |

One missed print is bridged by the 13-day rule; two in a row leave holes. With the cap, `pd_repo_ust` has a value on 1,682 of the 1,935 panel days and
`pd_reverse_repo_ust` on 1,736; the other three columns have a value on every panel day, as before.

## What changed in the code

* `new_sources.parse_pd_suppressed` returns the withheld dates per column, as the FR 2004 reader in `ingest.py` records a withheld cell as `suppressed`;
  `parse_pd_export` still yields no value for them. `new_sources.summarise_suppressed` gives the count, the longest run and the count by year.
* `new_sources.add_columns` stops carrying a weekly value `WEEKLY_CARRY_MAX_STALENESS_DAYS` after its as-of date, through the constant of `data.py`.
  The guard has one recorded mutation (`tests/test_new_sources.py`, `AddColumnsTests.test_a_weekly_value_is_not_carried_beyond_the_declared_staleness`).

## Re-screen

`docs/pivot/evidence/new-sources-capped/` holds #630's screen re-run with the cap (`screen.json`, `tables.md`, the inter-source matrices, `heatmap.svg`),
`uncapped_subset.json` (the same screen without the cap, for the two series, on the same scratch panel) and `comparison.md`. The scratch panel was rebuilt from the
tracked fixtures as `scripts/source_screen.py` describes, so the uncapped numbers differ slightly from #630's published tables where an upstream scratch column
has moved since. Summary (`comparison.md` has every lead):

| series | partial rho, before | after | ordinary days with a value, before | after | scarce-band AUROC at lead 1, before | after |
|---|---|---|---|---|---|---|
| `pd_reverse_repo_ust` | +0.112 | +0.087 | 1,469 | 1,330 | 0.656 | 0.648 |
| `pd_repo_ust` | +0.104 | +0.076 | 1,469 | 1,282 | 0.647 | 0.616 |

Both remain inside the "within 0.12 of zero" finding of #630; neither series gains. Their rank among the screened series by partial correlation falls from 20th and
24th to 28th and 31st (82 ranked in both runs).

## Later model rows

No model row, script or test reads these columns (`git grep -l 'pd_repo_ust\|pd_reverse_repo_ust'` finds only #630's screen, its evidence, its registry entry and its
tests), so no row from #624 (PR #652) onward needs a re-run.

## For Eleonora

Whether to admit the source given the withheld weeks, which hit the two series #630 ranked 4th and 5th, is hers. This page changes no published figure.
