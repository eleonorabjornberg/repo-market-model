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

## Why

In scouting, the persistence-logistic benchmark beat every gradient-boosted classifier, and the gradient-boosted model
missed the onset of the October 2025 pressure. Fixing the method in advance would publish a weaker probability when a
stronger one is available. The guards that make a claim honest stay unchanged: the as-of rule, the benchmarks and the
paired, split evidence.

## What does not change

- The next-day distribution of SOFR − IORB stays a target, with its own benchmark (as-of persistence).
- Pressure is scored as state, not onset. Thresholds come from `metadata/stress_thresholds.json`.
- The > +50 bp tail stays out of the headline (plan §1).
