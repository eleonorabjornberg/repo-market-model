# Decision: a locked final test period

**Status: decided by Eleonora, 2 October 2026. In force once this record merges.**

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
