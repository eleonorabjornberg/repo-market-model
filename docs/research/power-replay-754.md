# Power by empirical replay and three test families (H1 step 3, #754)

**Serves:** H1 (the scorer ranks forecasts of known quality correctly), step 3, and H5's registration and
confirmation (milestones M5 to M8). Protocol v1 is `docs/decisions/scoring-protocol.md`. The studies it follows are
`docs/research/confirmation-design-733.md` (PR #751) and `docs/research/power-study-656.md`.

**This document is committed before the study runs.** `scripts/power_replay.py` reads it as the rule; a result that
disagrees with this text is a defect in the script, not an amendment of the rule. The study is a design study on
development data. It produces no verdict, registers nothing, changes no protocol code, and only proposes: the
choice of test, and any change to the MME, are Eleonora's. No day after 2025-12-31 is read (§2). The list below is
closed: there is no search over tests, windows or generators.

## 1. The question

The synthetic power of #695 and #733 may understate what the data allow, because the noise is borrowed from B1
against B2, the critical value is calibrated as the largest statistic across windows of the whole history (so regime
shifts set it), and the null generator differs from the path generator. This study measures size and power in two
other ways, beside the current one:

1. **Empirical replay.** Slide windows through real development days on real forecast pairs whose ordering is known,
   and on pairs that are equal by construction. No synthetic noise is involved.
2. **Synthetic, with the null matched to the path generator.** The #733 machinery, with a family's critical value
   calibrated on the generator that draws its paths.

For each of three test families it reports size, power, and the smallest true gain detected with 80% power.

## 2. The development pool

The pool of `confirmation-design-733.md` §2, unchanged and built by the same code: the published panel from the
tracked fixtures (digest checked), decision days from 2018-06-29 whose five targets are on or before **2025-12-31**
(`STUDY_END`). The script refuses any later day (a `LookAheadError`). Per decision day: B1 and B2 grid CRPS per lead;
and, where all five leads of the published declaration's daily forecasts exist, B1 and B3 five-level CRPS per lead.

## 3. The series and the pairs

A score series is the daily difference `d_t = S(B1)_t - S(candidate)_t` (positive when the candidate is better) and the
benchmark series `b_t = S(B1)_t`. The *reading* of a series is the mean over leads 1 to 5 (the in-force design, D0),
except where a family says lead 1.

| pair | candidate against B1 | score | days |
|---|---|---|---|
| **P2** | B2 | grid CRPS | all decision days |
| **P3** | B3, the published model's daily forecasts | five-level CRPS | the days B3 covers |

A pair is **known better** only if its full-history mean skill `mean(d) / mean(b)` is at least the MME (3%) and the
one-sided p-value of the studentized stationary-bootstrap test (`scoring_protocol.paired_test`, 10,000 draws, seed 754)
is below 0.05. A pair that does not meet this is reported as not known better, and its detection share is then shown as
"detection on a pair that is not known better", not as power.

Three **known-equal** series, built from each pair:

- **E1, the relabelled copy.** `d_t = 0` for every day (a forecast against a renamed copy of itself). Every family must
  return "not detected"; a family that cannot even evaluate it is reported as undefined.
- **E2, the demeaned pair.** `d_t - mean(d)` over the pair's full series: the pair's own noise, volatility clustering and
  regime structure with a zero overall mean. Local means in a window are not zero, so the share flagged is the size
  the regime structure alone produces.
- **E3, the block sign-flip.** In each window the series is cut into blocks of 20 consecutive days, and each block's
  sign is flipped by an independent fair coin (seed fixed by the window's start day). The window's mean is zero in
  expectation, with the pair's own magnitudes and clustering.

The study has no "two seeds of one model" pair: no seeded model is held for the scored declaration, and this is
reported, not substituted.

## 4. The three families

Let `N` be the window length in days (60, 125 and 250 in the replay; 60, 125, 250 and 500 in the synthetic study).

**(a) The current test.** The stationary-bootstrap-calibrated studentized test of the protocol: at the looks
`checkpoints(N)` (24%, 50% and 100% of `N`, rounded half up; look 1 is never read), the statistic is the mean of the
first `n` days over its Newey-West standard error (`scoring_protocol.HAC_LAG`), and the window is detected if it
exceeds the **per-comparison critical value** at look 2 or look 3 (Eleonora's Q-E (b) ruling, applied by #737). The
critical value is the `1 - nominal level` quantile (`scoring_protocol.nominal_levels`) of 20,000 simulated windows of
the one comparison's own series. Two generators draw those windows:

- **(a1) as in force:** circular blocks of 10 days (`confirmation_design.window_statistics`);
- **(a2) matched to the paths:** the stationary bootstrap of mean block length 10 (`scoring_protocol.BLOCK_LENGTH`), the
  generator that draws the synthetic paths of §6.

**(b) The self-normalised Diebold-Mariano test.** One read, at the window's end, of the statistic `mean(d)` over its
Bartlett (Newey-West) standard error at lag `M = round(0.1 N)` (6, 12, 25 and 50 days for `N` = 60, 125, 250 and 500).
Detected if it exceeds the one-sided 5% critical value of the same statistic computed on 20,000 independent
standard-normal series of length `N` at the same lag (seed 1). This is the fixed-b critical value (Kiefer and
Vogelsang): it depends on `M / N` and on nothing in the history.

**(c) The anytime-valid sequential test.** A betting e-process on the mean difference. With `C` the largest absolute
daily difference of the series over the development history (so `x_t = d_t / C` lies in [-1, 1]),
`K_t = prod_{s <= t} (1 + lambda_s x_s)`, where `lambda_s = min(1/2, sqrt(2 ln(1/alpha) / (v_s * s * ln(1 + s))))`,
`alpha = 0.05` and `v_s = (1/4 + sum_{r < s} x_r^2) / s`, which uses only days before `s`. By Ville's inequality,
`P(sup_t K_t >= 1/alpha) <= alpha` under "the candidate is no better", for a series whose conditional mean given the
past is at most zero. The window is detected if `K_t >= 20` on **any** day `t <= N`: it can be read every day, with no
looks. It is run on **(c1) lead 1 alone** (the one-step difference; the overlapping five-lead mean has serial
dependence that the guarantee does not cover) and on **(c5) the mean over leads 1 to 5**, to show what that dependence
does to its size.

**The MME gate.** Every family is also read with the protocol's skill gate: detected and the window's mean skill
`mean(d) / mean(b)` (over the days read) at least 3%. For (c) the days read are those up to the first day `K_t >= 20`.
Tables show the family's test alone ("test") and with the gate ("gated"). The gated figure is the one comparable to the
*Supported* verdict's B1 half, and is an upper bound on the full rule's power (the B2 half and futility stopping are not
simulated).

## 5. The empirical replay

For each series (the two pairs, and E1 to E3 built from each), each `N` in {60, 125, 250} and each family, windows of
`N` consecutive days of the series start every 5th day and are read as if each were the prospective period. The share
detected is the share of windows. A window belongs to a **regime** by its last day: 2018-19, 2020-24 or 2025. It
belongs to a **day type** cell by the series it is cut from:

- **all days**, the series as built;
- **ordinary days**, the series with every day whose lead-1 target is not `ordinary` removed
  (`SplitDeclaration.reporting_day_type`), windows of `N` consecutive days of what remains;
- **pressure days**, the days that were removed, windows likewise (a cell with fewer than `N + 5` days is empty and
  said to be).

Intervals on a share are 95% moving-block bootstrap intervals over the windows (blocks of `ceil(N / 5)` consecutive
windows, 1,000 resamples, seed 754). Neighbouring windows overlap, so the interval counts the effective number of
independent windows, which is far smaller than the number of windows; the table gives both. The pooled figure is shown
beside its splits and is not a result on its own.

## 6. The synthetic study

The #733 candidate: on a history, `x_t = delta * b_t + (e_t - mean(e))` (noise 1) with `e_t` the P2 difference and
`b_t` its benchmark, so its mean skill against B1 is `delta`. Paths of `N` days are drawn by the stationary bootstrap
of mean block length 10 (`metrics.stationary_bootstrap_indices`), 2,000 paths per cell, seed 754 and the cell's
index. Histories: **full** (all days), the three regimes (**2018-19, 2020-24, 2025**), and the **ordinary-day** and
**pressure-day** series of §5. `delta` in {0 (size), 0.03, 0.05, 0.075, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50} on the full
history and `N` in {60, 125, 250, 500}; `delta` in {0, 0.03, 0.10} on each other history and `N` in {60, 125, 250}.
Family (a)'s critical values are calibrated on the full P2 series; (a1) and (a2) differ only in the generator.
Monte Carlo standard errors are binomial.

The **smallest detectable gain at 80% power** of a family at `N` is the smallest `delta` on the full-history grid at
which its gated power is at least 80%, or "none on the grid".

## 7. Reading and the result page

The result page reports, in this order: the declaration and what was run; for each family a table of replay size and
power by `N`, regime and day type (pooled beside the splits, with the effective number of independent windows); the
synthetic size and power by `N`, history and `delta`; the effect of matching the null generator (a2 against a1); the
smallest detectable gain at 80% power at 125, 250 and 500 days.

It ends with **one recommended confirmation test**, chosen by this rule and by nothing else: among the families
(a2, b, c1; c5 and a1 are shown only as comparisons) those whose size on **both** E2 and E3 (all days, `N` = 250,
both pairs) and in the synthetic study (full history, `N` = 250) is at most 5%, the one with the highest gated
synthetic power at 3% and `N` = 250. If none holds the size limit it says so and recommends none. It gives the
one-line trade-off against the current design (a1 at 250 days) and the smallest detectable gain at 250 days, followed
by marked questions for Eleonora. A change to the protocol is a draft decision record for her to merge, not code.

Where a family does not behave as the cited source says it should, the page says so and continues with the declared
families. The cited sources are named in the directive and are cited only after reading them; the page states which
could be read.

## 8. What the study does not do

It registers nothing and gives no verdict for any hypothesis. It does not simulate the B2 half or futility stopping.
It reads no day after 2025-12-31 and compares nothing on a locked day (`docs/decisions/lockbox.md`). Every figure is
development data, so none is a statement about 2026.
