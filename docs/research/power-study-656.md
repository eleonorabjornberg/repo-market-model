# Power study for scoring protocol v1: the reading rule (H5 groundwork G4, #656)

**Serves:** H5 (primary goal), groundwork G4; shared by every hypothesis that registers. Protocol v1 is
`docs/decisions/scoring-protocol.md` (§6: "a power study on development data, run before the first registration,
checks that 3% can be detected within 250 days. If it cannot, the study reports what can, and Eleonora then sets
the MME once, before any registration").

**This document is committed before the study runs.** `scripts/power_study.py` reads it as the rule; a result that
disagrees with this text is a defect in the script, not an amendment of the rule. Development data never gives a
verdict, and the study scores no day after 2026-09-03 (`PANEL_END`). The study decides nothing: the MME and the
power target are Eleonora's.

## 1. The question

Over how many confirmation days is a candidate with a true 3% CRPS skill against B1 detected, under the
protocol's own test and spending?

"Detected" is the protocol's *Supported* verdict (§6) at a checkpoint, restricted to its B1 half: the lower bound
of mean(d) against B1, read at the checkpoint's nominal level, is above zero **and** the point skill against B1 is
at least the MME. The B2 half is not simulated, so the power reported is an **upper bound** on the power of the full
rule (a candidate must also beat B2). Futility stopping is not simulated: it can only end a path early, never
turn a non-detection into a detection.

## 2. The development series

1. The published panel, built from the tracked fixtures (`REPRODUCIBILITY.md`), digest checked against
   `metadata/funding_panel_manifest.json`.
2. Decision days: every business day `t` of the panel from the first day with a full two-year window behind it
   (the first panel day plus two calendar years) whose five targets `t+1..t+5` are on or before 2026-09-03.
   The lockbox allows these days (the near-blind tier was opened, #151; the blind tier is after 2026-09-03).
3. For each decision day: B1 and B2 (`protocol_benchmarks.b1_forecast`, `b2_forecast`), and the primary score
   of each (`scoring_protocol.day_scores`, grid CRPS, mean over h = 1..5, outcomes the panel's own spreads).
   Write `S1_t`, `S2_t`.

## 3. The synthetic candidate

No candidate is registered, so the candidate is constructed. Its daily difference against B1 is

    d_t = DELTA * S1_t + NOISE * (e_t - mean(e)),      e_t = S1_t - S2_t,      DELTA = 0.03,

and its score is `C_t = S1_t - d_t`. By construction mean(d)/mean(S1) = DELTA exactly: the candidate has a true
skill of 3%. The day-to-day noise of d is borrowed from the one pair of forecasts we hold that differ materially
and honestly, B1 against B2, centred. Scale `NOISE` of 1 is the **primary** reading; 0.5 and 0.25 are reported as
sensitivity rows (a candidate that tracks B1 more closely has a quieter d and so more power). `C_t` is not clipped;
the count of days with `C_t < 0` is reported.

## 4. The simulated confirmation paths

A path is 250 consecutive days drawn as one stationary-bootstrap resample (`metrics.stationary_bootstrap_indices`,
mean block 10, over the pairs (`S1_t`, `d_t`) in date order; the scoring protocol's own block length). Checkpoints
are the protocol's 60, 125 and 250 days, on the path's first 60, 125 and 250 days.

At checkpoint `k` the test is the protocol's: `scoring_protocol.paired_test(S1, C, ...)` on the path's first
`n_k` days, 10,000 draws, mean block 10, the lower bound at `nominal_levels()[k-1]`, and the point skill against
`MME`. A path stops at its first detection. **Power at checkpoint k** is the share of paths detected at or before
it. `REPLICATIONS` = 400 paths per `NOISE`; the Monte Carlo standard error of a power is reported
(`sqrt(p(1-p)/REPLICATIONS)`). Seeds are fixed in the script before it runs.

**Look 1 is unresolvable as the protocol is written.** Its nominal level is below 1/10,000, so a 10,000-draw
bootstrap cannot read it (`UnresolvedLevel`). The study reports that as a result: the power at 60 days under the
protocol as written is zero, whatever the candidate. To show what the level would cost, look 1 is also read with
20,000 draws, labelled as a deviation and reported beside, never in place of, the as-written figure.

## 5. What is reported

For each `NOISE`: the power at 60, 125 and 250 days (as written, and for look 1 the 20,000-draw deviation); the
mean skill and the mean of d of the series; the days with `C_t < 0`.

**Days needed.** The smallest checkpoint whose cumulative power reaches **80%** (the conventional target; it is
not in the protocol and is **Eleonora's to confirm**). If no checkpoint reaches it, the study says 3% is not
detectable within 250 days, and reports what is: the smallest true skill, on a grid of 3%, 4%, 5%, 6%, 8% and
10%, whose cumulative power at 250 days reaches 80% (the same simulation with `DELTA` replaced).

**Cross-check.** The same quantity from the group-sequential normal approximation: `theta = mean(d) / sigma_LR`
with `sigma_LR` the Newey-West (lag 10) long-run standard deviation of d, drift `theta * sqrt(n)`, the protocol's
efficacy boundaries (`scoring_protocol.boundaries()`), 20,000 simulated paths.

## 6. The H7m information goalpost

The liquidity repository's H7m goalpost is 0.05 AUROC with at least 10 stress events. The study reports, on
development data, how many stress events the panel holds (a stress event is an onset of pressure, `repo_model.onset.onset_flags`, the
unit the pressure judge counted), the confirmation days in which 10 such events are to be expected at the
development base rate (days = 10 / events-per-day), and the AUROC standard error at that count under a
conservative Hanley-McNeil approximation with 10 events, for a stated number of non-events. It is an input to
that repository's registration, not a power calculation for it: the AUROC test is not the protocol's CRPS test
and is theirs to define.

## 7. Not decided here

The 80% target, the choice of `NOISE` = 1 as primary, the 400 paths, and whether look 1 should be given a finer
bound or more draws are readings this document makes. Each is listed as a question in the pull request.
