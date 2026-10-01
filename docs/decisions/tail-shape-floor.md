# Decision: the fitted tail shape is never negative

**Status: decided by Eleonora, 1 October 2026, in her ruling on
[#63](https://github.com/eleonorabjornberg/repo-market-model/issues/63). A session drafted this record to
record her decision. It is in force once she, or the reviewer routine under "Delegated review" in `workflow.md`,
has merged it. It supersedes [`tail-refusal.md`](tail-refusal.md).**

## The ruling

In her words, on #63:

> repo pressure has no hard ceiling. The Standing Repo Facility is a soft cap, not a bound. The fitted GPD shape is
> therefore constrained to be non-negative: a negative fit is treated as zero, so the tail never assigns zero
> probability above a level.

## What it means in the model

- **The floor.** In `ml._fit_gpd_pwm`, a fit with at least `GPD_MINIMUM_EXCESSES` excesses whose raw
  probability-weighted-moment shape is negative takes `xi = 0` and `sigma = a_0`, the sample's mean excess. That is
  the exponential the fallback already uses. It keeps the fit's first moment equal to the sample mean. Every
  negative shape is floored, including one at or below `-0.5`. The lower end of `GPD_SHAPE_BOUNDS` is `0.0`.
- **Unchanged:** the upper clamp at `0.5`, `GPD_MINIMUM_EXCESSES`, the plotting offset and the threshold quantile.
- **The record says so.** A floored fold is recorded as `floored`, with `sigma`, `excesses` and the raw negative
  estimate as `xi_estimate`, and no `xi`. A reader can therefore count floored folds apart from shapes fitted
  non-negative.
- **What new runs stop producing.** They no longer produce `refused`, the state `tail-refusal.md` introduced, or
  `upper_endpoint_excess`, a fitted tail's ceiling. Both stay readable, because published records carry them.

## Why

A negative shape puts a hard ceiling `sigma / -xi` above the threshold, and beyond it the model assigns
probability exactly zero. Repo pressure has no such ceiling, and the Standing Repo Facility does not supply one.
On about thirty excesses per fold the sign of the fitted shape also changed with the scikit-learn version (#63), so
a fold's ceiling depended on a fitter's version as much as on the data.

## What it replaces

`tail-refusal.md` refused a shape at the lower clamp of `-0.5` and kept an interior negative shape with its
ceiling. The floor covers both cases.

The published `--tail gpd` record was scored under the earlier rule. It is re-scored once, under this one, by the
re-score that follows (#27). It is not edited in place.
