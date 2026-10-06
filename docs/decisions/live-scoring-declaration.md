# Decision: how the live record is scored

**Status: a draft for Eleonora (#276), in force once she merges it.** Drafted by the pull request that
closes #276, which states decisions she has already made (her ruling of 6 October 2026, #269 items 4, 7
and 14). It declares how the live record (#215) is scored before any 2027 outcome exists. Nothing here
opens a lockbox tier: the opening is `docs/decisions/lockbox.md`'s, and this record changes none of it.

## Regimes

Each calendar year from 2027 is its own regime. The scorer (`scripts/live_score.py`, `_regime`) labels a
target day with the regime `metadata/evaluation_splits.json` declares, and a day that file does not cover
with its calendar year when that year is 2027 or later. A day before 2027 that no regime covers stays
"undeclared".

**The version of the splits file.** The scorer reads `metadata/evaluation_splits.json` as it stands when
this record merges: git blob `772a47cc859854c487c7097b9d2ea8fd83cfdf7d`, SHA-256
`d92d48f17aef1475d3773406d2dfb6c650cbe470fd4f9e8074e965c37a23bc96`. The file's last declared regime ends
at the end of 2026, so the 2027 regimes live in the scorer's rule, not in the file, and the file is not edited.

**How that relates to each record's hash.** Every live record stores `inputs.splits_sha256`, the SHA-256 of
the file's bytes on the day the record was written. A record whose hash differs from the one above was
written under a different version of the file. The scorer reports it and does not re-split on it. Editing
the file after this merges would change both hashes above, so it needs a new decision that names the new
version.

## Intervals

"Percentile" is the declared construction of every interval the live scorer reports: the 5th and 95th
percentiles of the stationary bootstrap's replicates, as `metrics.stationary_bootstrap_interval` computes
them. That function already does this, so the declaration fixes the wording, not the method. No figure
moves.

## Benchmark

As-of persistence keeps its one-step residual law. Every live record already freezes its persistence
quantiles on the day it is written (`distributions.persistence.quantiles_bps`), so the law cannot change
after the fact for any record since logging began. This is stated plainly so that no reader takes the
benchmark to be re-fitted at scoring time.

There is no second comparator, unless one can be computed later from what the records already hold.

## Turn days

Quarter-end, month-end, year-end and tax-date days get no special treatment. They are scored as they
come, in the pooled figure and in the by-day-type split. ("Post-turn prints" appear nowhere in the code.)

## Robustness

The robustness block of #260 (leave-two-out, win share, Diebold-Mariano, by-window) is **reported only**.
It decides nothing: the primary result is the CRPS cell at h = 1 under the final test's pass rule, as the
lockbox amendment drafts it.

## Minimum cell size

A regime or day-type cell gets an interval by a fixed rule, not by whether a bootstrap replicate happens to
miss it. A cell with fewer than `live_score.MINIMUM_CELL_DAYS` days reports its mean and "too few days",
with no interval, in the CRPS cells and in the Brier cells. The pooled figure is not a cell and is
unaffected. The first scoring date comes after every published record, so no published record is edited;
records adopt the rule at their next publish.

> **Question for Eleonora (marked; the number is hers).** I propose **20 days**, the minimum the final
> test's pages already use (`onset.MINIMUM_EVENTS`, there a count of events, here a count of days). It is
> the one number the project already defends, and below it a mean of paired losses has too few independent
> blocks for a stationary bootstrap of block length 2 to 6 to say anything. The cost: a month-end,
> quarter-end or tax-date cell is likely to stay below 20 days for most of the first year, so those cells
> will read "too few days" and carry only a mean. Her number replaces 20 in one constant; the tests read
> the constant.
