# Decision: a locked final test period

**Status: decided by Eleonora, 2 October 2026. In force: merged in PR #93, 1 October 2026.**

## The rule

Two periods are held back from every model comparison: no candidate, declaration, feature or setting is chosen
on them.

- **The near-blind tier: 2026-01-01 to 2026-09-03**, the end of the current panel.
- **The blind tier: every day after 2026-09-03.** No record has scored these days.

A comparison scores only days before 2026-01-01. That covers a backtest that picks between models, an ablation, a
sensitivity run and a re-score. A model may still be trained on, and forecast, the days its as-of information set
allows. What it may not do is have a locked day count toward a choice.

## Opening

The locked periods are opened **once, by Eleonora, at a phase verdict**, for the candidates that verdict names. The
result is published whatever it shows, under the usual evidence rule: paired against the benchmarks, with a
bootstrap interval, and split by regime and pressure-day type. After opening, the opened days become ordinary
history, and a new blind tier starts from the day after the panel then ends.

## Why

Every day from 2018-04-03 to 2026-09-03 has been scored in published records. Each forecast is out of sample, but
the choice between models is not: every variant tried on the same window flatters the winner's measured edge. A
period that no choice has seen is the only honest estimate of how the chosen model does next.

## Why the near-blind tier starts on 2026-01-01

It trades test strength against what comparisons can learn from. On the published panel:

| Tier start | Locked days | Locked days > +5 bp | Locked days > +10 bp | 2025–26 days > +5 bp left for comparisons |
|---|---|---|---|---|
| 2025-09-04 | 250 | 34 | 17 | 0 |
| **2026-01-01** | **169** | **5** | **0** | **29** |
| 2026-03-01 | 130 | 2 | 0 | 32 |

A day counts as above a threshold when its spread, read on whole basis points, is strictly above it: a day exactly
on +5 bp is not a day above +5 bp (`docs/decisions/pressure-probability.md`, ruling of 2 October 2026 on #155). The
table was re-counted on that reading and no cell moved. Compared on the raw floating-point spread instead, a day on
the threshold is counted above it, and the counts above +5 and +10 bp come out higher.

A start of 2025-09-04 would lock every 2025–26 pressure day. Comparisons would then see no pressure in the 2025–26
regime, and the regime split would say nothing about it. It would not make that period blind either: the
October 2025 episode is already in published records and in `docs/advisor/evidence-pack/MEMO.md`. A start of
2026-01-01 keeps October 2025 for learning, and locks a period with few pressure days. The near-blind tier is
therefore a weak test above +10 bp until the blind tier adds to it.

## What it does not change

- **Published records stay as they are.** Records scored before this rule include near-blind days, and they are
  not edited in place. This is why that tier is called near-blind: its days have appeared inside published
  aggregates, though no choice was made on them by name.
- The as-of rule, the benchmarks and the evidence rule are unchanged.
- The event holdouts (`metadata/events.json`) are unchanged. They lie before both tiers.

## Amendment: the near-blind tier is opened (#151)

**Status: in force: merged in PR #236, 5 October 2026 (#151).** Drafted by the pull request that closes #151,
as that directive asks.

- **Opened once, on 2026-10-05, for the final test.** Eleonora gave the go ("GO #151", 4 October 2026, relayed on
  #151). The run that closes #151 opened the near-blind tier (2026-01-01 to 2026-09-03) in `metadata/lockbox.json`,
  with that ruling as the reference, and ran the frozen command of `docs/decisions/final-test-preregistration.md`
  once: the published distribution (#169's gbm with nested conformal PID) against as-of persistence, by CRPS, at
  h = 1. The test's other cells, for the frozen dynamic logit (#137) and the published distribution at h = 2 to 5,
  were scored in the same run and are reported only. The method for the h = 2 to 5 cells was
  chosen after the 2026 days were seen, because the lockbox was opened before one was declared (Eleonora's ruling of
  6 October 2026, #223, relayed). They are labelled so on the page and never change the test's verdict. The record is `docs/runs/final_test_near_blind.json`, published
  whatever it shows.
- **The near-blind tier is now ordinary history.** Its days may be scored by any comparison, like every day
  before 2026-01-01. A comparison that chooses a model on them can no longer claim a held-out test on them.
- **The blind tier stays locked.** Every day after 2026-09-03 is still held back from every comparison. It becomes
  the next test. The live record (#215) logs blind-tier days; scoring them waits on its own drafted amendment
  (`docs/decisions/drafts/lockbox-live-record.md`), and this amendment opens none of them.
