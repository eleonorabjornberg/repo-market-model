# Research plan

Decided by Eleonora on 12 October 2026 and taken from the top block of the queue issue
([#46](https://github.com/eleonorabjornberg/repo-market-model/issues/46)). This page records decisions she has
made. A change to it after the pull request that adds it is hers, or is a ruling she has relayed (cite the
ruling).

The log is [`log.md`](log.md). Each hypothesis has a manual in [`hypotheses/`](hypotheses/). The check that keeps
the plan, the log and the result pages in step is `scripts/check_research_log.py` (run in CI).

## Order

- **Primary goal: H5**, the SOFR − IORB spread distribution in bp.
- **Secondary goal: H9**, richer targets.
- H1–H4 support them. H6–H8 and H10 follow.
- +5 bp classification variants are paused until the upper-bound study (#635) reports.
- The scoring protocol (#640) gates all new scoring. Work already running finishes as exploration only: its
  results are logged, and none is a verdict.
- Model work comes before judge-rule and scoring-rule work (her standing order of 10 October).
- Split by aim ([#643](https://github.com/eleonorabjornberg/repo-market-model/issues/643), decided by her):
  `eleonorabjornberg/repo-market-liquidity` owns H7's estimator and H10, with its own queue. This repository owns
  everything else: H1–H6, H8, H9, H7's nested forecast test, all data ingestion, the scorer, the lockbox and the
  live record. The research log stays single, here.

## Every hypothesis follows the same steps

1. Question. 2. Groundwork. 3. Development (development days only, never a verdict). 4. Registration (her
attested action). 5. Confirmation (prospective days, at the protocol's checkpoints). 6. Verdict. A new directive
names its hypothesis and its step. Work that serves no step goes to the auditor's `avenue` list, not to the
queue. Changing a hypothesis's question or target creates a new hypothesis; its old log stays.

## Hypotheses

Status is one of `open`, `supported`, `killed`. All are `open` on 12 October 2026. Directives marked "not yet
queued" have no first directive yet.

## H1. The scorer ranks forecasts of known quality correctly

- **Test:** the synthetic suite the protocol requires ([#640](https://github.com/eleonorabjornberg/repo-market-model/issues/640)); [#636](https://github.com/eleonorabjornberg/repo-market-model/issues/636) covers the +5 bp judge, if she keeps it.
- **Kill or fix:** any pre-registered check fails. Every registration is blocked until it passes.
- **Next:** on pass, registrations may proceed. On fail, fix the scorer under the protocol's change control.
- **Status:** open. Manual: [`hypotheses/H1.md`](hypotheses/H1.md).

## H2. The data we hold carries signal for the spread and for ordinary-day pressure

- **Tests:** [#635](https://github.com/eleonorabjornberg/repo-market-model/issues/635) (upper bound), [#629](https://github.com/eleonorabjornberg/repo-market-model/issues/629), [#631](https://github.com/eleonorabjornberg/repo-market-model/issues/631).
- **Kill:** the ceiling is barely above the benchmark: ordinary-day AUROC below 0.6, or the spread's CRPS skill against persistence covers 0.
- **Next:** on kill, effort moves to H3 and H4. Otherwise it goes to H5's development steps.
- **Status:** open. Manual: [`hypotheses/H2.md`](hypotheses/H2.md).

## H3. New public data adds signal

- **Test:** [#630](https://github.com/eleonorabjornberg/repo-market-model/issues/630).
- **Kill:** no new series ranks above the held ones on ordinary days.
- **Next:** on kill, the held data is the data. Otherwise register the sources that pass as nested tests on H5.
- **Status:** open. Manual: [`hypotheses/H3.md`](hypotheses/H3.md).

## H4. Longer history fixes part of 2018–19

- **Test:** [#633](https://github.com/eleonorabjornberg/repo-market-model/issues/633).
- **Kill:** no 2014–18 series has an established posting time, or extended training moves 2018–19 calibration by less than its interval.
- **Next:** on kill, 2018–19 stays a known weakness and is reported as one. Otherwise release the series that pass.
- **Status:** open. Manual: [`hypotheses/H4.md`](hypotheses/H4.md).

## H5 (primary goal). The SOFR − IORB spread distribution in bp improves on phase 2 and beats classification

- **Open questions:** 2021–23 and the tails.
- **Tests:** [#634](https://github.com/eleonorabjornberg/repo-market-model/issues/634), [#632](https://github.com/eleonorabjornberg/repo-market-model/issues/632).
- **Kill:** no CRPS gain over the phase 2 models, and no ordinary-day ranking gain.
- **Next:** on kill, the phase 2 models stand and effort goes to H9. Otherwise register one primary candidate.
- **Status:** open. Manual: [`hypotheses/H5.md`](hypotheses/H5.md).

## H6. The spread on known risk dates is forecastable

- **Target:** the spread in bp on announced settlement, tax, quarter-end and month-end days, which number in the hundreds rather than 26 onsets.
- **Test:** not yet queued.
- **Kill:** no CRPS or MAE skill against as-of persistence and a risk-date calendar benchmark on those days.
- **Next:** on support, a risk-date severity calendar for desks.
- **Status:** open, not yet queued. Manual: [`hypotheses/H6.md`](hypotheses/H6.md).

## H7. Reserve scarcity can be tracked

- **Target:** the distance to the demand-curve kink and the scarcity state, estimated directly as a slow variable.
- **Owner of the estimator:** `eleonorabjornberg/repo-market-liquidity` (step 1 moves there from [#644](https://github.com/eleonorabjornberg/repo-market-model/issues/644)). The nested forecast test is here, under #640.
- **Kill:** the estimate does not predict later spread behaviour beyond the current scarcity state.
- **Next:** on support, it becomes an input to H5 and H6.
- **Status:** open, not yet queued here. Manual: [`hypotheses/H7.md`](hypotheses/H7.md).

## H8. Ranking beats calibrating for desk use

- **Target:** rank the next 20 business days by risk, scored on top-k precision and recall against climatology and persistence.
- **Test:** not yet queued.
- **Kill:** no ranking skill beyond the calendar of known risk dates.
- **Status:** open, not yet queued. Manual: [`hypotheses/H8.md`](hypotheses/H8.md).

## H9 (secondary goal). Richer targets carry more learnable signal

- **Targets:** the SOFR tail (99th percentile minus IORB, and dispersion), TGCR, BGCR and EFFR each minus IORB, ON RRP take-up, and standing repo facility take-up. Not SOFR − IORB itself, which is H5.
- **Test:** [#639](https://github.com/eleonorabjornberg/repo-market-model/issues/639) (uses #629 and #630).
- **Kill:** no forecast skill over persistence, or no lead on the +5 bp episodes.
- **Status:** open. Manual: [`hypotheses/H9.md`](hypotheses/H9.md).

## H10. Pressure episodes can be attributed to drivers

- **Target:** a post-hoc decomposition of each episode into settlement, TGA, reserves, quarter-end and residual.
- **Owner:** `eleonorabjornberg/repo-market-liquidity`.
- **Kill:** the residual dominates most episodes.
- **Next:** it tells H5–H9 which drivers to forecast.
- **Status:** open, not yet queued here. Manual: [`hypotheses/H10.md`](hypotheses/H10.md).

## Why

What 10–12 October showed, in her words and from the records:

- **The judge has defects.** Three audit findings on the +5 bp judge (#615, #616, #617) were left to her. The
  paired-Brier header and the pooled false-alarm count had to be corrected after results were already
  published (#604, #607, #613).
- **26 onsets are a small sample.** Every +5 bp verdict rests on 26 onset days, and eight of them are unwarned by
  any row (`docs/pivot/unwarned-onsets-result.md`, #560).
- **The ordinary-day gap.** The best tier-1 passer's every-day part raises most of its false alarms
  (`docs/pivot/pooled-gate-result.md`, #595) and the cap and floor variants did not close the 2018–19
  under-forecast (PRs #608 and #612).
- **Phase 2 already answered the spread.** The as-of records show the gbm models, uncalibrated and
  cross-conformal, and the funding declaration beating as-of persistence on CRPS, with paired intervals that
  exclude zero, except in 2021–23 and on quarter ends; the tail clause is measured and failing (`PLAN.md`,
  Phase 2 verdict, [#73](https://github.com/eleonorabjornberg/repo-market-model/issues/73)).

So the spread distribution in bp, scored by a protocol designed from scratch (#640), is the primary goal.
