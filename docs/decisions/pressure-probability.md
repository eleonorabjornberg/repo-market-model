# Decision: the pressure probability comes from the best model

**Status: decided by Eleonora, 1 October 2026. In force once this record merges.** It replaces the stress-target
clause in `docs/process/AGENT_CONTRACT.md` that required the pressure probability to be an exceedance derived from the
predictive distribution.

## The rule

The headline pressure probability, P(SOFR − IORB > +5 bp) and P(> +10 bp) at 1–5 business days, is produced by
whichever candidate model wins. A candidate may be:

- **the distribution-derived exceedance** of the as-of predictive distribution;
- **a direct probability model** fitted to the exceedance label, such as a logistic model or a gradient-boosted
  classifier.

## How the winner is chosen

All candidates face the same test:

- **Same information.** Every candidate is scored under `information-set.md` on one shared fold grid, with labels at
  fixed bp thresholds, never a full-sample percentile.
- **Same benchmarks.** Every candidate is compared against calendar-type climatology and the persistence-logistic
  benchmark.
- **Same evidence.** The comparison is paired, with a stationary-bootstrap interval, and split by regime and by
  pressure-day type. Its metrics are Brier with its decomposition, CORP reliability, precision-recall and lead time.

The winner is the candidate that beats both benchmarks on that evidence and does best among those that do. A pooled
figure alone does not decide it. Choosing the winner is a published claim, so it is made in a scored record and put to
Eleonora, not settled in code.

## The event is strictly greater than

Amended by Eleonora, 1 October 2026, in her ruling on
[#73](https://github.com/eleonorabjornberg/repo-market-model/issues/73). The event is SOFR − IORB **strictly
greater than** the threshold, as the exceedance path, the `stress_gt_*` labels and the contract already score it.
This record said ≥ before. Both rates are quoted in whole basis points, so the two differ on every day that sits
exactly on the threshold, and this record now states what the code and the published records measure.

**Draft, for Eleonora's approval; not in force until she approves it.** 2 October 2026
([#155](https://github.com/eleonorabjornberg/repo-market-model/issues/155)): the records published before
#155's correction counted a day exactly on +5 or +10 bp as above it, so on those days they did not measure the
strict event; from the corrected publication ([#124](https://github.com/eleonorabjornberg/repo-market-model/issues/124))
every comparison reads the spread on whole basis points.

## The thresholds are fixed relative to IORB

Amended by Eleonora, 1 October 2026, in her ruling on
[#87](https://github.com/eleonorabjornberg/repo-market-model/pull/87). The +5 and +10 bp thresholds are fixed
distances above IORB. The headline labels are never re-anchored to a trailing median, a rolling percentile or any other
normalisation of the spread's own history. The spread is anchored to administered rates: the ON RRP rate below
it and the SRF minimum bid, IORB + 10 bp, above it. Both move with IORB. A trailing anchor would drift with the
regime it is meant to detect, and would label a scarce-reserves period as normal just when it matters (Nicholas
Beroud's argument, `docs/advisor/evidence-pack/MEMO.md`, Q1(a)). Per-regime distributions of the spread remain a
diagnostic, never the label.

This governs the headline labels. `metadata/stress_thresholds.json` still declares a `trailing_percentile`
`secondary_rule`, a leftover of the pre-pivot contract. Nothing computes a label from it. Directive
[#91](https://github.com/eleonorabjornberg/repo-market-model/issues/91) retires it.

## Headline thresholds, and thresholds reported event by event

**Decided by Eleonora, 2 October 2026 ([#130](https://github.com/eleonorabjornberg/repo-market-model/issues/130),
PR [#152](https://github.com/eleonorabjornberg/repo-market-model/pull/152)).**

- **The headline pressure claims are at +5 and +10 bp.**
- **At +20 and +50 bp a record carries no pooled skill claim and no bootstrap interval.** Those thresholds have too
  few positive days for a pooled figure to be validated, and at +50 bp the forecasts show no discrimination. The
  record carries an event list instead: for each day above the threshold, its date, the realised spread, and each
  model's forecast probabilities over the five scored business days before it and on the day. "Each model" is the
  scored candidate, the climatology reference and every benchmark the record pairs it with. Every day above the
  threshold is its own entry; days are not merged into episodes. At a listed threshold the record drops every pooled
  figure: the skill score and its interval, the Brier score, its decomposition, the reliability curve, average
  precision and the paired benchmark rows.
- **Every threshold's positive count is stated in the record**, as `positives`, so a reader sees what each figure
  rests on. The count lives in the record, never in an acceptance criterion or in page text.
- **The threshold-weighted CRPS keeps integrating over every declared threshold, +20 and +50 bp included.**

`exceedance-backtest --event-list 20 --event-list 50` writes such a record (`--event-lead-days` sets the five). The
records published before this rule are not edited in place: their +20 and +50 bp rows change at the next publish.

## Why

In scouting, the persistence-logistic benchmark beat every gradient-boosted classifier, and the gradient-boosted model
missed the onset of the October 2025 pressure. Fixing the method in advance would publish a weaker probability when a
stronger one is available. The guards that make a claim honest stay unchanged: the as-of rule, the benchmarks and the
paired, split evidence.

## What does not change

- The next-day distribution of SOFR − IORB stays a target, with its own benchmark (as-of persistence).
- Pressure is scored as state, not onset. Thresholds come from `metadata/stress_thresholds.json`.
- The > +50 bp tail stays out of the headline (plan §1).
