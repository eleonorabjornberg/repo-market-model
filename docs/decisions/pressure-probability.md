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

2 October 2026
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

## Onset view and small-leap targets

**Decided by Eleonora on 2 October 2026 (#139), in force once the pull request that adds it merges.** It records her
request of 2 October 2026, as widened and amended that day, and she approved the wording below as drafted.

**Why.** The +5 and +10 bp stress targets hold too few events in calm periods to settle a model comparison: 2026 has
no day above +10 bp. The model's value is at onset and in the tail, and an average over every scored day hides both.

**The targets, in order:**

1. **The +5 and +10 bp stress targets** stay the project's headline.
2. **Small leaps and leap onsets**, an additional target with more events.
3. **The CRPS of the full distribution**, with the threshold-weighted CRPS (weight 1{y > +5 bp}, Gneiting & Ranjan
   2011) reported beside the plain CRPS.

**Every report shows the +5 and +10 bp results**, ties included, next to any leap result.

**The day groups.** Every pressure-probability and distribution comparison reports three groups: all scored days;
scheduled-pressure days (month end, quarter end, tax date, Treasury coupon settlement); and onset days, the first day
with SOFR − IORB above +5 bp after at least five consecutive business days at or below it. For onset days each model's
probabilities on the five scored days before the onset are listed. Onset figures rest on few events, the record states
the count, and they are descriptive, not tests.

**The leap, defined as-of.** For a forecast of day *t* at horizon *h*, the jump is *x_t = s_t − s_a(t)*, where *s* is
SOFR − IORB in whole basis points and *a(t)* is that forecast's as-of anchor: the latest spread public at its decision
instant under `information-set.md`. It is never the day before *t*. A leap is *x_t > J_h*, strictly. *J_h* is the 90th
percentile (linear interpolation) of the signed jumps at horizon *h* over every scored day of the published fold grid
from 2018-06-29 to 2025-12-31, excluding days with no admissible anchor, stored to 2 decimal places and never
recomputed from later data. A leap onset is a leap with no leap on any of the five previous business days. A pressure
leap is a leap that also ends above IORB, and is reported next to the leap.

**A leap is a different question from a stress warning.** "Will the spread jump" is not "will there be a stress day".
No page or record presents a leap result as a stress-warning result. The claim wording for a leap result is: "the model
forecasts as-of jumps in SOFR − IORB better than [the named baselines]". It never says "warns of stress".

**The leap baselines**, both fitted walk-forward: the calendar climatology (the leap frequency before *t* by day type)
and the persistence-logistic (a logistic of the leap on the latest as-of jump and the latest as-of spread). A leap claim
must beat both, paired, with the 90% interval excluding 0. Beating only one is reported as exactly that.

**The interval.** Paired differences use 90% stationary-bootstrap intervals, the project's standard for every
published comparison, fixed in advance and not chosen for this target. A Diebold–Mariano test with a HAC variance is
reported for the all-days group only.

**Too few events means inconclusive.** Below a target's pre-declared minimum event count, the result is reported as
inconclusive, and is read as neither a pass nor a fail. Decided by Eleonora on 2 October 2026: the minimum is 20 events in the
all-days group (`onset.MINIMUM_EVENTS`).

**The target was not chosen blind to 2026.** `lockbox.md` already publishes how few 2026 days exceed +5 and +10 bp,
and public Fed commentary describes 2026 as calm. The leap target was therefore added with knowledge of the locked
period's character, though no model was scored on it.

## Why

In scouting, the persistence-logistic benchmark beat every gradient-boosted classifier, and the gradient-boosted model
missed the onset of the October 2025 pressure. Fixing the method in advance would publish a weaker probability when a
stronger one is available. The guards that make a claim honest stay unchanged: the as-of rule, the benchmarks and the
paired, split evidence.

## What does not change

- The next-day distribution of SOFR − IORB stays a target, with its own benchmark (as-of persistence).
- Pressure is scored as state, not onset. Thresholds come from `metadata/stress_thresholds.json`.
- The > +50 bp tail stays out of the headline (plan §1).
