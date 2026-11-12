# Glossary

The terms the result pages use, each defined once. A page that uses one of them links here. Where a decision document sets the meaning, the entry names it, and that document wins over this page.

## What is forecast

**Spread.** SOFR minus IORB as first published, in basis points (bp). Every forecast and every score on these pages is about this number.

**Decision day and target day.** A forecast is made on the decision day, with what was public at the decision instant, for a later day: the target day. The decision instant is 18:00 New York time; it was 16:00 until the amendment of 29 October 2026, and older records keep their 16:00 label.

**Lead (h).** The number of business days from the decision day to the target day. The project scores leads 1 to 5, written h = 1-5.

**Cell.** One forecast that can be scored: one decision day at one lead. A day scored at five leads gives five cells.

**Quantile and band.** A forecast is a set of quantiles of the spread: q05 is the level the model expects the spread to fall below 5% of the time. The 90% band runs from q05 to q95.

**Grid.** The 23 quantile levels every model forecasts: 0.01, 0.025, 0.05, then every 0.05 up to 0.95, then 0.975 and 0.99.

## How a forecast is scored

**Grid CRPS.** The primary score, in bp: twice the mean pinball loss over the grid, averaged with equal weight over h = 1-5. It measures how far the whole forecast distribution sat from what happened. Lower is better.

**Upper-tail twCRPS.** The key secondary score, in bp: the same score computed with weight only where the spread is above 0 bp (SOFR above IORB), which is where funding pressure shows. Lower is better.

**Coverage.** The share of cells whose outcome fell inside a band. A 90% band that works covers 0.9 of them.

**Tail miss.** A cell whose outcome fell outside a quantile: "above q95" should happen in 5% of cells, "above q99" in 1%.

**Paired difference and mean d.** Two models are compared on the same cells, score against score. In a table against a benchmark, d is the benchmark's score minus the model's, so a positive mean d favors the model. Where a table says "arm minus candidate" for a CRPS, a negative figure favors the arm.

**Interval.** Every difference carries a two-sided 90% interval. Two methods are in use. The studentized stationary bootstrap resamples blocks of days (mean block 10 business days) and is the scoring protocol's method. The event-cluster interval resamples whole turn events, because the forecasts aimed at one quarter-end move together and are one observation, not ten.

**Improves beyond its interval.** The lower end of the 90% interval of the paired difference is above zero. An improvement whose interval includes zero does not count as one.

## What a forecast is compared with

**B1 (as-of persistence).** The last public value of the spread, plus the distribution of that lead's own changes over the trailing two years.

**B1' (calendar-aware persistence).** B1 anchored on the last ordinary-day spread, with changes pooled by the target day's type. It is a reference row, not a benchmark of the protocol.

**B2 (calendar climatology).** The distribution of the spread over the trailing year on days of the same type (quarter-end, month-end, tax date, ordinary).

**B3 (incumbent).** The best registered model at the time; at first, the published v1 funding declaration. It publishes five quantile levels, so it is scored on those five only, and a comparison with it is reported without a decision rule.

**Supported.** The protocol's word for a model whose lower bound of mean d is above zero against both B1 and B2.

## The models

**Candidate.** The one model the project currently proposes for the primary goal, written (s3c-ann-net): a mean-reverting model of the spread whose calendar terms are read at the target day, with Treasury settlement terms taken from the auction announcements, and each quantile capped at the Standing Repo Facility rate.

**Frozen.** The candidate has not changed since 2 November 2026. Studies run beside it; none of them alters it.

**Arm.** One variant tested beside the candidate in a study, identical to it except for the single change the study is about. Adopting an arm is Eleonora's decision and no result page does it.

**Refit.** The model is re-estimated on a schedule as the walk moves through time (every 21 decision days for the candidate), using only data available then.

**Direct pairs.** The way a model is trained: each row is paired with the spread of the target day itself, so a calendar column is learned on the day it describes.

## Days and periods

**Pressure-day type.** The label of a target day: `turn` (the last and first business day around a month-end that is not a quarter-end), `quarter_end_turn` (the last business day of March, June or September and the first after it), `year_end` (the last business day of December and the first of January), `tax_date`, or `ordinary`.

**Turn event.** One quarter-end or year-end, counted once: the two days of the turn and all forecasts at h = 1-5 aimed at them.

**Group.** In a study of an arm, the target days the arm changes. Everything outside the group is identical to the candidate.

**Regime.** A dated spell of the sample (2018-19, 2020, 2021-23, 2024, 2025-26). Results are split by regime because a pooled figure can hide a model that works in one spell only.

**Development window.** The decision days whose targets all fall on or before 2025-12-31. Results on it are development evidence: they guide the work and never give a verdict.

**2026 development days.** Targets from 2026-01-02 to 2026-09-03. They were locked until 5 October 2026 and are shown apart from the development window.

**Confirmation days.** Business days after a candidate's registration, forecast live before the outcome is public. Under the scoring protocol they are the only evidence for a verdict.

**Lockbox.** The rule that keeps later days unscored until Eleonora opens them (`docs/decisions/lockbox.md`).

## Rules a result is read under

**Declaration.** The file, committed before any score is computed, that fixes what a study will run and how its result will be read.

**Kill rule.** The condition, written in the declaration, under which an arm is dropped. For the two quarter-end studies it reads: the arm's 90% coverage on the group does not improve on the candidate's beyond its interval, or the arm's mean grid CRPS on the group is above the candidate's. "Not killed" means only that neither happened.

**Registration.** Eleonora's attested act of committing one candidate (code, configuration, inputs and training rule, fixed by hash) before its first confirmation day. Nothing about a registered candidate changes afterwards; a changed candidate is a new registration.

**Fourth amendment.** The fourth amendment to the scoring protocol, in force since 8 November 2026: a candidate must pass the coverage tests (a Kupiec test and an independence test on quantile hits, corrected with Holm at 5%) before it can be registered. The candidate currently fails them, which is why it is frozen and not registered.

**Provisional.** A result from a model that did not read calendar days at the target day, or learned them one row off. It stands until re-run and is listed in `provisional-calendar-register.md`.

## Record

Scoring protocol: `docs/decisions/scoring-protocol.md`. Information set and decision instant: `docs/decisions/information-set.md`. Lockbox: `docs/decisions/lockbox.md`. Candidate: `docs/research/h5-candidate.json`. Pressure-day labels: `src/repo_model/turn_days.py`. Kill rules: `metadata/qe_shrunk_scale_1531.json`, `metadata/qe_event_model_1548.json`. Written for #1574.
