# Decision: refusing a tail fit clamped at the lower shape bound

**Status: decided. Implementation is in flight; no verdict on Phase 2's tail clause is recorded on
the strength of it, and `PLAN.md` is deliberately unchanged until the rule is implemented and
re-scored end to end.**

## The rule

If a fitted generalised Pareto tail hits the **lower** end of `GPD_SHAPE_BOUNDS` — a shape at or
below minus one half — the fit is refused for that fold and the estimator falls back, exactly as it
already falls back when there are too few excesses.

## The failure it removes

A negative fitted shape puts a hard upper endpoint on the tail, beyond which the survival function
is exactly zero. `GPD_SHAPE_BOUNDS` names this in its own docstring: it is "the same zero this
repair exists to remove, arrived at the long way round". Where that endpoint falls below a declared
threshold, the model assigns probability zero at that threshold, and a logarithmic score is then
unavailable on any day the event occurred.

## Why this rule rather than the obvious one

The rule first proposed was to refuse any fit whose absolute ceiling falls at or below the largest
declared threshold. Measured over the full fold set, that refuses an order of magnitude more folds
and fixes exactly the same days — every candidate cutoff refuses the same event folds, and raising
the cutoff only adds folds on which nothing happened.

A clamp at the lower bound is the better criterion for a reason that is not merely arithmetic: it
means the estimator wanted an even steeper cutoff and collided with its own guardrail, so the
endpoint is an artefact of the bound rather than of the sample. It refuses the smallest set that
contains the failures.

One arithmetic correction is embedded in the comparison and is worth stating, because getting it
wrong changes the answer. The quantity the estimator records is an **excess above the top declared
quantile**, not a level. The absolute ceiling is that quantile plus the excess. Comparing the bare
excess to a threshold compares two different things, and on this sample it refuses a materially
different set of folds.

The rule is stated on the shape and not on the existing clamp flag, because that flag is also raised
at the upper bound, where there is no endpoint and the concern is a different one — an infinite
variance rather than a structural zero. The two coincide on the current evidence and the shape form
stays correct when they stop coinciding.

## What the measurement also showed, and why the verdict waits

Two things in the same measurement bear on Phase 2's tail clause and neither is settled by this rule.

Most folds never receive a fitted tail at all: the large majority fall back or have no excesses, and
among those that are fitted, most have a non-negative shape and therefore no endpoint. And fitted
tails appear only in the later part of the sample — across the two stress episodes the project holds
out as events, the fitted tail is inert.

The evidence is in the re-score record under `docs/block-runner/rescore/`, which is unpublished
working material rather than a published record. A verdict on the exit criterion waits on the rule
being implemented, the set being re-scored, and the result being published. Recording a pass whose
justification is a guard that has not been built would put a claim in `PLAN.md` that no record
supports.
