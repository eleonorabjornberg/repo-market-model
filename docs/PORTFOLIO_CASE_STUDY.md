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
  ([`pivot/lag-assessment.md`](pivot/lag-assessment.md)). The feature set was fixed without
  re-measuring that assessment's verdicts; re-scoring them belongs with next-version research.
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
what a purge must guarantee, which calibration is adopted, and whether a phase has reached its exit
criterion. AI coding agents implement much of the code, one session per pull request, and nothing
lands on `main` without CI and my review. Nicholas Beroud advises on the
funding market itself — which public series carry its mechanics and what they mean — and is not
a co-owner of the code.

## Results and limitations

The results are not restated on this page, apart from the correction note below: a copy here is a
copy that the next re-score leaves behind. They are generated from the run records into `README.md`, and the verdict lives in
`PLAN.md`.

- **[Key findings](../README.md#key-findings).** Gradient-boosted quantile regression,
  uncalibrated and cross-conformal, against as-of persistence on CRPS and on interval coverage,
  each difference paired with a stationary-bootstrap interval and split by regime and by type of
  day.
- **[The tail clause, measured](../README.md#the-tail-clause-measured).** The pressure
  probabilities at the pre-declared stress thresholds, against calendar-type climatology and
  the persistence-logistic benchmark. Where a forecast assigns probability zero to an event
  that occurs, the record reports no log score, because it refuses to replace an infinite loss
  with a finite one somebody chose.
- **The verdict** on Phase 2's exit criterion, which asks for out-of-sample performance against
  persistence and calibration in the tails, is in [`PLAN.md`](../PLAN.md). Which candidate may
  supply the headline pressure probability is decided under
  [`decisions/pressure-probability.md`](decisions/pressure-probability.md).

The earlier diagnosis of why the tail flattens, read from the fitted law's knots, was made on
the archived records and has not been re-measured under the as-of rule.

Nothing here is live forward performance: every result is a backtest on a frozen panel, and no
part of this is a basis for a decision about money.

## Correction note, 2 October 2026

**What was wrong.** The exceedance records published before
[#155](https://github.com/eleonorabjornberg/repo-market-model/issues/155)'s correction counted a day whose SOFR − IORB
spread sat exactly on +5 or +10 bp as above the threshold. The event is the spread strictly above it
([`decisions/pressure-probability.md`](decisions/pressure-probability.md)), so on those days the records did not
measure it. Every comparison now reads the spread on whole basis points.

**Why the window changed.** The corrected records score 2018-06-29 to 2025-12-31. The records they replace scored
through 2026-09-03, but days from 2026-01-01 are held back from every comparison
([`decisions/lockbox.md`](decisions/lockbox.md)), so no record could be re-scored on the old window. Old and new
figures below therefore differ by window as well as by labels.

**What else the same publication changed** ([#124](https://github.com/eleonorabjornberg/repo-market-model/issues/124)):
the published funding declaration is calibrated by conformal PID with nested selection of its constants
(#136; record: [`runs/exceedance_gbm_conformal_pid_nested_funding.json`](runs/exceedance_gbm_conformal_pid_nested_funding.json)) instead of CV+; pressure model v1 is
published at horizons 1 to 5 (#134; records: [`runs/pressure_model_v1_h1.json`](runs/pressure_model_v1_h1.json) to
[`runs/pressure_model_v1_h5.json`](runs/pressure_model_v1_h5.json)); and at
+20 and +50 bp each record lists every day above the threshold instead of a pooled figure
(#130; rule: [`decisions/pressure-probability.md`](decisions/pressure-probability.md)).

**The superseded records** are archived, unedited: the five pre-correction exceedance records in
[`runs/archive/pre-whole-bp/`](runs/archive/pre-whole-bp) ("#155: pre-correction labels"), and the CV+ funding
records in [`runs/archive/cross-conformal-funding/`](runs/archive/cross-conformal-funding).

Two sets of figures behind the wording below are in no record, so this page links to them rather than restating
them: the onset-day comparisons ([#160](https://github.com/eleonorabjornberg/repo-market-model/issues/160)'s method,
for both models, in [#169](https://github.com/eleonorabjornberg/repo-market-model/pull/169)), and pressure model v1's
earlier measurement on the old labels ([#134](https://github.com/eleonorabjornberg/repo-market-model/issues/134)).

<!-- generated: correction -->
<!-- Generated by scripts/emit_results.py from docs/runs/. Do not edit by hand. -->

**What the results now say**, in Eleonora's wording (her ruling of 2 October 2026 on #169), quoted from the records that carry it:

- at +5 bp, "It beats the persistence-logistic by a small margin. The previous published model (CV+) tied it. The gain comes mainly from the switch to nested-selection calibration (#136); the #155 correction removed 18 threshold days." (`exceedance_gbm_conformal_pid_nested_funding.json` and the records beside it)
- "At +10 bp it beats calendar climatology by a small margin but not the persistence-logistic." (`exceedance_gbm_conformal_pid_nested_funding.json` and the records beside it)
- "On onset days it does not beat the persistence-logistic: it trails at +10 bp, and at +5 bp the two cannot be told apart." Onset days are scored days whose previous panel day was not above +5 bp (#160); the paired figures are in no record; they are in the pull request that published this record (#169). (`exceedance_gbm_conformal_pid_nested_funding.json` and the records beside it)
- "Beats the persistence-logistic at +5 bp one to five days ahead; at +10 bp, a small gain two days ahead only." (`pressure_model_v1_h1.json` and the records beside it)

**Which figures moved.** Each paired cell is the benchmark's Brier score minus the model's, with its 90% stationary-bootstrap interval; a positive value favours the model. Old is the superseded record, archived unedited; new is the record that replaced it.

| Old record → new record | Threshold | Brier, old → new | vs calendar-type climatology, old → new | vs persistence-logistic, old → new |
|---|---|---|---|---|
| `archive/cross-conformal-funding/exceedance_gbm_cross_conformal_funding.json` → `exceedance_gbm_conformal_pid_nested_funding.json` | 5 bp | 0.0524 → 0.0496 | +0.0248 (+0.0187 to +0.0314), beats it → +0.0218 (+0.0153 to +0.0287), beats it | +0.0017 (-0.0009 to +0.0044), not distinguishable → +0.0067 (+0.0030 to +0.0105), beats it |
| `archive/cross-conformal-funding/exceedance_gbm_cross_conformal_funding.json` → `exceedance_gbm_conformal_pid_nested_funding.json` | 10 bp | 0.0307 → 0.0286 | +0.0041 (+0.0008 to +0.0076), beats it → +0.0041 (+0.0010 to +0.0077), beats it | +0.0000 (-0.0021 to +0.0021), not distinguishable → +0.0008 (-0.0013 to +0.0033), not distinguishable |
| `archive/pre-whole-bp/exceedance_gbm.json` → `exceedance_gbm.json` | 5 bp | 0.0534 → 0.0525 | +0.0238 (+0.0172 to +0.0311), beats it → +0.0189 (+0.0117 to +0.0266), beats it | +0.0008 (-0.0024 to +0.0042), not distinguishable → +0.0038 (-0.0004 to +0.0088), not distinguishable |
| `archive/pre-whole-bp/exceedance_gbm.json` → `exceedance_gbm.json` | 10 bp | 0.0310 → 0.0301 | +0.0038 (+0.0006 to +0.0073), beats it → +0.0026 (-0.0008 to +0.0061), not distinguishable | -0.0002 (-0.0022 to +0.0019), not distinguishable → -0.0006 (-0.0027 to +0.0018), not distinguishable |
| `archive/pre-whole-bp/exceedance_gbm_cross_conformal.json` → `exceedance_gbm_cross_conformal.json` | 5 bp | 0.0562 → 0.0551 | +0.0210 (+0.0146 to +0.0283), beats it → +0.0163 (+0.0092 to +0.0241), beats it | -0.0021 (-0.0053 to +0.0013), not distinguishable → +0.0012 (-0.0030 to +0.0061), not distinguishable |
| `archive/pre-whole-bp/exceedance_gbm_cross_conformal.json` → `exceedance_gbm_cross_conformal.json` | 10 bp | 0.0332 → 0.0323 | +0.0016 (-0.0018 to +0.0053), not distinguishable → +0.0004 (-0.0032 to +0.0045), not distinguishable | -0.0024 (-0.0048 to +0.0001), not distinguishable → -0.0028 (-0.0053 to +0.0001), not distinguishable |
| `archive/pre-whole-bp/exceedance_climatology.json` → `exceedance_climatology.json` | 5 bp | 0.0765 → 0.0708 | +0.0007 (-0.0012 to +0.0026), not distinguishable → +0.0006 (-0.0015 to +0.0026), not distinguishable | -0.0224 (-0.0280 to -0.0172), loses to it → -0.0145 (-0.0190 to -0.0103), loses to it |
| `archive/pre-whole-bp/exceedance_climatology.json` → `exceedance_climatology.json` | 10 bp | 0.0340 → 0.0319 | +0.0008 (-0.0012 to +0.0026), not distinguishable → +0.0008 (-0.0012 to +0.0027), not distinguishable | -0.0033 (-0.0053 to -0.0015), loses to it → -0.0024 (-0.0041 to -0.0008), loses to it |
| `archive/pre-whole-bp/exceedance_persistence_logistic.json` → `exceedance_persistence_logistic.json` | 5 bp | 0.0542 → 0.0563 | +0.0231 (+0.0175 to +0.0290), beats it → +0.0151 (+0.0102 to +0.0200), beats it | — → — |
| `archive/pre-whole-bp/exceedance_persistence_logistic.json` → `exceedance_persistence_logistic.json` | 10 bp | 0.0307 → 0.0295 | +0.0040 (+0.0015 to +0.0068), beats it → +0.0032 (+0.0007 to +0.0058), beats it | — → — |
| `archive/pre-whole-bp/exceedance_calendar_climatology.json` → `exceedance_calendar_climatology.json` | 5 bp | 0.0772 → 0.0714 | — → — | — → — |
| `archive/pre-whole-bp/exceedance_calendar_climatology.json` → `exceedance_calendar_climatology.json` | 10 bp | 0.0348 → 0.0327 | — → — | — → — |

**The tail clause** (`exceedance_gbm`, Brier skill against climatology, with its 90% interval):

| Threshold | Old | New |
|---|---|---|
| 5 bp | +0.303 (+0.234 to +0.370) | +0.258 (+0.169 to +0.339) |
| 10 bp | +0.089 (+0.004 to +0.158) | +0.056 (-0.039 to +0.129) |

**Pressure model v1 by horizon.** The probability read from the published funding declaration's distribution and recalibrated out of fold (`docs/runs/pressure_model_v1_h*.json`), scored at each horizon in business days and paired day by day with both benchmarks. Each cell is the benchmark's Brier score minus the model's, with its 90% stationary-bootstrap interval; a positive value favours the model.

| Horizon | Scored days | vs calendar-type climatology, 5 bp | vs persistence-logistic, 5 bp | vs calendar-type climatology, 10 bp | vs persistence-logistic, 10 bp |
|---|---|---|---|---|---|
| 1 | 1873 | +0.0219 (+0.0158 to +0.0282), beats it | +0.0068 (+0.0031 to +0.0107), beats it | +0.0039 (+0.0015 to +0.0065), beats it | +0.0007 (-0.0010 to +0.0024), not distinguishable |
| 2 | 1872 | +0.0180 (+0.0120 to +0.0247), beats it | +0.0080 (+0.0037 to +0.0125), beats it | +0.0030 (+0.0004 to +0.0056), beats it | +0.0028 (+0.0006 to +0.0053), beats it |
| 3 | 1871 | +0.0166 (+0.0104 to +0.0235), beats it | +0.0103 (+0.0053 to +0.0153), beats it | +0.0024 (-0.0003 to +0.0053), not distinguishable | +0.0018 (-0.0003 to +0.0040), not distinguishable |
| 4 | 1870 | +0.0141 (+0.0082 to +0.0206), beats it | +0.0057 (+0.0013 to +0.0105), beats it | +0.0019 (-0.0008 to +0.0047), not distinguishable | -0.0003 (-0.0022 to +0.0018), not distinguishable |
| 5 | 1869 | +0.0136 (+0.0075 to +0.0204), beats it | +0.0060 (+0.0011 to +0.0114), beats it | +0.0017 (-0.0009 to +0.0043), not distinguishable | -0.0003 (-0.0021 to +0.0015), not distinguishable |

<!-- end generated: correction -->

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
