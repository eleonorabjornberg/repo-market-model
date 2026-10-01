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
- **An as-of information rule.** Each input is read at its latest value public at the decision
  instant, field by field, with leakage and staleness guards both holding. It replaced a derived
  purge that made every forecast from a feature row several business days old: the published
  forecasts were about a week stale. That was a finding, not a feature. Every figure here is
  re-scored under the as-of rule, and the earlier records are archived
  ([`pivot/lag-assessment.md`](pivot/lag-assessment.md)).
- **Typed absence.** A missing value, a declared structural zero, an excluded cross-section and
  a withheld field are four different things, each carrying its reason into the record.
- **Guards proven to fire.** Each has a recorded mutation that breaks the behaviour it
  protects and names the exception the test caught. An unproven guard is treated as no guard.
- **Generated figures.** Documents quote results only through blocks regenerated from the run
  records; a test fails the build if a page and its record disagree.

## Analytical approach

Models are scored by as-of rolling-origin backtesting: train on an expanding window of what was
public at each decision instant, forecast the next business day, score, advance, refitting every
21 scored days on one shared fold grid. September 2019 and March 2020 are frozen as knowledge
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
criterion. AI coding agents implement much of the code, one session per pull request, and nothing
lands on `main` without CI and my review. Nicholas Beroud advises on the
funding market itself — which public series carry its mechanics and what they mean — and is not
a co-owner of the code.

## Results and limitations

**The machine-learning model beats the benchmark on average.** Gradient-boosted quantile
regression scores a better CRPS than as-of persistence across thousands of scored days, with the
paired difference clear of zero, uncalibrated and cross-conformal alike. The win is not uniform:
every variant loses to persistence in 2021-23, and the uncalibrated model loses on quarter ends.

**Calibration is a trade, not a free repair.** The uncalibrated model's intervals are far too
narrow. Cross-conformal calibration, which keeps the whole fitted model, widens them past the
stated coverage and keeps a smaller but distinguishable win over persistence.

**The tail is where it fails, and that is the finding.** Against a climatology at pre-declared
stress thresholds, the model has skill at the two smaller thresholds and is beaten at the two
larger ones, each interval clear of zero. Against the harder benchmark, a persistence-logistic
model on the latest public spread, it is not distinguishable at either threshold the two are
compared on, so it does not earn the headline pressure probability. At several thresholds the record reports no log score
at all, because the forecast assigned probability zero to an event that occurred and the record
refuses to replace an infinite loss with a finite one somebody chose.

**The verdict.** The exit criterion — beat persistence out of sample and stay calibrated in the
tails — is met on the first half and fails on the second, on the as-of records
([`../PLAN.md`](../PLAN.md)). The earlier diagnosis of why the tail flattens, read from the
fitted law's knots, was made on the archived records and has not been re-measured under the
as-of rule.

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
Actions, and pull requests gated by CI.

## Where to look

- **The repository** — [github.com/eleonorabjornberg/repo-market-model](https://github.com/eleonorabjornberg/repo-market-model): the README carries the current figures, generated from the run records.
- **The project page** — [eleonorabjornberg.com](https://eleonorabjornberg.com): the same work in plain English, with its live status.
- **The evidence** — [`docs/runs/`](runs) holds one record per scored run, each naming the commit and the data digest it was produced under.
