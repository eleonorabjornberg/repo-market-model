# Forecasting U.S. Treasury Repo-Market Pressure: A Reproducible Model-Risk Case Study

The figures behind every claim here live in [`README.md`](../README.md)'s key-findings block,
generated from the run records in [`docs/runs/`](runs) rather than typed into this page.

## Business question

Can pressure in the U.S. repurchase-agreement market be forecast as a *distribution* — not a
point estimate — from public data alone, and can that forecast's stated uncertainty be trusted
on the days that matter?

## Why the problem matters

Banks, money funds and corporate treasuries fund themselves overnight against Treasury
collateral. Most days that market is dull. On a few — September 2019, March 2020 — the cost of
overnight cash jumps far enough to change what a treasurer does that morning. The people
exposed to those days do not need a better guess at tomorrow's rate. They need to know how bad
tomorrow could plausibly be, and whether the warning can be relied on.

That reframes the evaluation: a model accurate on average and quietly overconfident about its
range fails precisely when it is consulted. The test is whether the uncertainty holds, in the
middle of the distribution and in the tail.

## Data and controls

Public sources only, each stored as an immutable checksummed snapshot carrying the moment its
values first became observable: the New York Fed's secured reference rates, FRED administered
rates checked against ALFRED vintages, Treasury auction and bill-rate data, and SEC Form N-MFP
money-fund filings.

Declared is not the same as available, and this repository keeps the difference visible. A
source can be registered, priced for its release lag and still contribute no observations —
because its snapshot was never taken, or because its rows do not carry the availability stamp
the contract requires. The build records which columns it produced, which it refused and why,
and which are a hole on every row; the scored models read a deliberately small subset of what
is declared, and the records say which.

Five controls hold the evidence together:

- **Point-in-time availability.** Every field declares its own release lag and, where the
  instant is earlier than the end-of-day convention, the evidence for it. An earlier instant is
  the only direction the declaration can leak in, so it is the one that must carry provenance.
- **A derived purge.** The gap between training and scored data is computed from the declared
  lags of the features in use, never chosen by hand — which means the forecast is made from a
  feature row several business days before the day it is scored on, not from yesterday's close.
- **Typed absence.** A missing value, a declared structural zero, an excluded cross-section and
  a withheld field are four different things, each carrying its reason into the record.
- **Guards proven to fire.** Each has a recorded mutation that breaks the behaviour it
  protects and names the exception the test caught. An unproven guard is treated as no guard.
- **Generated figures.** Documents quote results only through blocks regenerated from the run
  records; a test fails the build if a page and its record disagree.

## Analytical approach

Models are scored by purged rolling-origin backtesting: train on an expanding window, forecast
across the derived gap, score, advance. September 2019 and March 2020 are frozen as knowledge
holdouts, so no model is tuned on the episodes it exists to warn about.

Five model families sit behind one interface — persistence, ARX, threshold regression,
rolling-residual intervals, and gradient-boosted quantile regression, the last with
split-conformal and cross-conformal calibration. Scoring is probabilistic throughout: CRPS,
pinball loss, interval coverage, Brier skill and CORP reliability at pre-declared stress
thresholds, with paired differences intervalled by stationary bootstrap to respect the overlap
between folds.

## My contribution

I defined the research question, designed the data model and its validation rules, set the
point-in-time and model-risk controls, and specified the evaluation protocol and the staged
plan. I make the methodological decisions this repository records: what may count as a zero,
what a purge must guarantee, which calibration is adopted, and whether a phase has met its exit
criterion. AI coding agents implemented much of the code inside a machine-checked contract I
wrote, in separate worktrees, reviewed before anything lands. Nicholas Beroud advises on the
funding market itself — which public series carry its mechanics and what they mean — and is not
a co-owner of the code.

## Results and limitations

**The machine-learning model beats the benchmark on average.** Gradient-boosted quantile
regression scores a better CRPS than persistence across thousands of scored days, with the
paired difference clear of zero. Autoregressive, regime-switching and volatility-feature
challengers did not.

**Calibration did not have to cost that edge.** The uncalibrated model's intervals are far too
narrow. Split-conformal calibration repairs the coverage and surrenders the accuracy win.
Cross-conformal calibration, which keeps the whole fitted model, holds the stated coverage and
keeps a distinguishable win.

**The tail is where it fails, and that is the finding.** Scored against a climatology at
pre-declared stress thresholds, the model has skill at the smallest threshold and is beaten at
the larger ones, each interval clear of zero. The part of the score that comes from
distinguishing one day from another falls to nothing at the largest, and at that threshold the
record reports no log score at all, because the forecast assigned probability zero to an event
that occurred and the record refuses to replace an infinite loss with a finite one somebody
chose.

**The cause is structural, and was measured rather than argued.** The same flattening appears
in a linear autoregression scored identically, so it is a property of this target at these
thresholds and not of the learner. Reading the fitted predictive law's own knots back, fold by
fold, shows why: above its highest fitted quantile the law is a single straight segment running
to the largest residual it has ever seen, and every declared stress threshold is read inside
that segment on the great majority of folds. A straight line carries no shape, so the
probabilities it returns barely move with the inputs. Where the model should discriminate, it
is interpolating.

Nothing here is live forward performance: every result is a backtest on a frozen panel, and no
part of this is a basis for a decision about money.

## Skills demonstrated

Probabilistic forecasting and its evaluation; point-in-time data engineering from primary
financial sources, including documenting errors found in them; leakage-safe backtest design;
calibration and tail-risk assessment; model-risk controls and the discipline of proving a
control works; reproducibility and provenance; directing AI coding agents under written rules;
and writing for two audiences — records a reviewer can verify, and summaries a decision-maker
can act on.

**Stack.** Python with a dependency-free standard-library core, numpy and scikit-learn behind
an optional extra, a CLI for every step, `unittest` with mutation-tested guards, GitHub
Actions, and Git worktrees under a machine-checked contract.

## Where to look

- **The repository** — [github.com/eleonorabjornberg/repo-market-model](https://github.com/eleonorabjornberg/repo-market-model): the README carries the current figures, generated from the run records.
- **The project page** — [eleonorabjornberg.com](https://eleonorabjornberg.com): the same work in plain English, with its live status.
- **The evidence** — [`docs/runs/`](runs) holds one record per scored run, each naming the commit and the data digest it was produced under.
