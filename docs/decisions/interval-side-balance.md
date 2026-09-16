# Decision: which side the intervals miss on, and what the asymmetric variant corrects

**Status: measured and published. The four records are in `docs/runs/`; the reading is emitted by
`scripts/emit_interval_sides.py` and is not transcribed here.**

## The question

Realized coverage is a two-sided number, and two-sided coverage cannot tell a band that misses its
declared share evenly from one that misses almost everything on one side. Those are different
defects. The second is the one an asymmetric conformal calibration exists to correct: it fits the
two tails separately rather than assuming the residual law is symmetric about the point forecast.

So the question is not "is coverage close to the declared band" but **which side do the misses fall
on, is the difference distinguishable from noise, and does the asymmetric variant move it.**

## What was measured

Every backtest record carries a per-origin `side` of `inside`, `below` or `above` under
`metrics.interval_calibration`, so the question is answerable from records already on disk. No new
estimator and no change to `src/` was needed; the one cell that had never been run was scored.

Four cells, each the same panel, the same 61-day minimum history, the same 16:00 decision time and
the same declared features, differing only in calibration:

- `docs/runs/backtest_gbm_conformal_share035_mh61.json`
- `docs/runs/backtest_gbm_conformal_asymmetric_share035_mh61.json`
- `docs/runs/backtest_gbm_cross_conformal_mh61.json`
- `docs/runs/backtest_gbm_cross_conformal_asymmetric_mh61.json`

Each side's miss rate carries a stationary-block-bootstrap interval, and the imbalance -- below
minus above -- is taken **from the same resample**, because the two rates are computed over one set
of origins and resampling them independently would destroy the pairing the difference is taken
across. `scripts/emit_interval_sides.py` asserts that all four records share an identical origin
sequence and refuses to print if they do not: an unpaired difference is not a difference.

## The pairing, and why it is not across shares

Split conformal is compared at one calibration share against itself, and cross-conformal at one
fold count against itself. The calibration share moves realized coverage by several points on its
own, so pairing an asymmetric run at one share against a symmetric run at another would charge the
share's effect to the asymmetry. That comparison was available and is deliberately not the one made.

## What it shows

Read the emitted table; the records carry the numbers. In words:

**Under split conformal the imbalance is large and its interval excludes zero.** The band misses
far more often below the forecast than above it, which is the defect the asymmetric variant was
built for, and the asymmetric variant reduces it substantially -- though not to a point where the
remaining imbalance's interval covers zero.

**Under cross-conformal the imbalance is already indistinguishable from zero**, and the asymmetric
variant moves it by an amount well inside its own interval. There is no imbalance there for the
asymmetry to correct.

The factual consequence, stated without a verdict on any exit criterion: on the calibration the
model work uses, `conformal_asymmetric` addresses a defect that is not present. Whether that retires
the variant, or leaves it as the right default for split conformal, is not decided here.

**A second fact the same table carries, and it is not the one the question asked.** Both
cross-conformal cells miss *under* the declared share on both sides at once. A band that misses less
often than it declared is not calibrated in its interval either -- it is too wide rather than
misplaced -- and that is a different complaint from the one an asymmetric calibration answers.
Nothing here decides what to do about it.

## How to re-run it

    python scripts/emit_interval_sides.py

The seed, mean block length, replication count and interval level are module constants, so the
intervals reproduce. A record that changes without this reading changing is a contradiction the
records will show.
