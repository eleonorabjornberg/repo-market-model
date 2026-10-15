# Confirmation design study: size and power of six declared designs (H1 step 2, #733)

**Serves:** H1 (the scorer ranks forecasts of known quality correctly), step 2, and H5's registration and
confirmation (milestones M5 to M8). Protocol v1 is `docs/decisions/scoring-protocol.md`. The power study it extends is
`docs/research/power-study-656.md` and its addendum; the calibration is `docs/research/protocol-calibration/`.

**This document is committed before the study runs.** `scripts/confirmation_design.py` reads it as the rule; a result
that disagrees with this text is a defect in the script, not an amendment of the rule. The study is a design study on
synthetic and development data. It produces no verdict, registers nothing, changes no code of the protocol, and only
proposes: the choice, and any change to the MME, are Eleonora's. No day after 2025-12-31 is read (§2).

## 1. The question

Over a few declared confirmation designs, which one detects a true 3% CRPS skill against B1 (the MME) with useful
power while holding its size? And what is the smallest true skill each design detects with 80% power, so that any
change to the MME is an explicit choice?

"Detected" is the protocol's *Supported* verdict restricted to its B1 half, as in the earlier study: the lower bound
of the statistic is above zero at a look **and** the point skill is at least the MME. The B2 half and futility
stopping are not simulated, so every power figure is an **upper bound** on the power of the full rule.

## 2. The development pool

1. The published panel, built from the tracked fixtures (`REPRODUCIBILITY.md`), digest checked against
   `metadata/funding_panel_manifest.json`.
2. Decision days: every business day `t` from 2018-06-29 whose five targets `t+1..t+5` are on or before **2025-12-31**
   (`STUDY_END`). The study scores no later day and the script refuses to (a `LookAheadError`). Trailing windows are
   clipped at the panel's first day, as the protocol reads them.
3. Per decision day: B1 and B2 (`protocol_benchmarks.b1_forecast`, `b2_forecast`) scored per lead by grid CRPS
   (`scoring_protocol.grid_crps`, 23 levels); B1 and B3 (the published declaration's daily forecasts) scored per lead
   by CRPS on B3's five levels (`scoring_protocol.level_crps`), on the days where all five leads of B3 exist.
4. Two histories. **Full:** every decision day of the pool. **Post-2020:** decision days from 2020-04-03 (two years
   after the panel's first day, the earlier study's history).

The per-day score used by a design is the mean over its leads (`HORIZONS` = 1 to 5, or lead 1 alone for D3).

## 3. The synthetic candidate

As in `power-study-656.md` §3, written on the design's own score scale. A design turns each day's B1 and B2 scores
into a benchmark score `b_t` and a difference `e_t = b_t - (B2's score on the same scale)`. Its candidate's daily
difference against B1 is

    x_t = DELTA * b_t + NOISE * (e_t - mean(e)),

so mean(x)/mean(b) = DELTA exactly: a true skill of DELTA on that scale. `NOISE` = 1 is primary; 0.5 is a sensitivity
row. The day-to-day noise is borrowed from B1 against B2, the one pair of honest forecasts we hold that differ
materially. Under DELTA = 0, mean(x) = 0 exactly, so the series has no true difference.

## 4. The six designs (a closed list)

| id | days N | looks | leads | statistic | scale |
|---|---|---|---|---|---|
| D0 | 250 | 60, 125, 250 | mean of leads 1 to 5 | mean difference | raw CRPS |
| D1 | 375 | 90, 188, 375 | mean of leads 1 to 5 | mean difference | raw CRPS |
| D2 | 500 | 120, 250, 500 | mean of leads 1 to 5 | mean difference | raw CRPS |
| D3 | 250 | 60, 125, 250 | lead 1 alone | mean difference | raw CRPS |
| D4 | 250 | 60, 125, 250 | mean of leads 1 to 5 | mean difference | standardized |
| D5 | 375 | 90, 188, 375 | mean of leads 1 to 5 | mean difference | standardized |

- **D0 is the design now in force** (protocol v1 with the ruling of 13 October 2026, item 5), re-run here on the
  pool of §2 so that it is compared like for like. The protocol's statistic already pools leads 1 to 5 into one number
  per day. D3 is the control for that axis, not a new proposal: it shows what pooling buys over the single lead.
- **Looks** are the protocol's 24%, 50% and 100% of N, rounded half up, with Lan-DeMets O'Brien-Fleming spending
  scaled to match (`scoring_protocol.nominal_levels(checkpoints)`).
- **Standardized** (D4, D5) divides each day's scores by `m_t`, the mean of B1's pooled score over the 60 decision days
  that end six pool positions before `t`, so every lead of every day in `m_t` has a published outcome at the decision
  instant. The first 65 pool days have no `m_t` and are not in the standardized series. Standardizing makes the
  statistic a mean of relative differences, which a single spike day no longer dominates; the MME gate is then read on
  the standardized scale (mean(x)/mean(b) with both standardized). The aim is a smaller calibrated critical value.
- 3% stays the MME in every design. Nothing here moves it.

## 5. The test

At look `k` (N_k days of a path, or of a window) the bound is

    mean(x) - c * se,

`se` the Newey-West standard error at lag 10 (`scoring_protocol._standard_error`), and `c` the design's calibrated
critical value at that look. Detected at look `k`: the bound is above zero and mean(x)/mean(b) is at least the MME.
The path stops at its first detection.

**Calibration**, per design and per look, follows the ruling of 13 October 2026 (item 5) exactly:
- windows of N_k days built from circular blocks of 10 consecutive days drawn from the design's pool (§2, Full), at
  uniform random starts; `WINDOWS` = 20,000 per pair and per N; the windows of one N are shared by its looks 2 and 3
  (a look reads the window's first N_k days); seed 1;
- the statistic of a window is `(mean_w - mean(series)) / se_w`; `c` is its `1 - level` quantile at the look's
  nominal level (`scoring_protocol._bound`);
- the pairs are B2 - B1 on the 23-level grid and B3 - B1 on B3's five levels, each in both orientations, on the
  design's lead set and scale, and the design's `c` is the **largest** of the four;
- **look 1 is not read in any design**, as in the protocol as it stands (its level cannot be calibrated from the
  windows the history gives). It spends its small share of the level and never detects.

## 6. Null and alternatives

Each scenario is a set of `PATHS` = 2,000 paths. A path is the first N days of one stationary-bootstrap resample
(`metrics.stationary_bootstrap_indices`, mean block 10) of the pairs (`b_t`, `e_t`) of a history, in date order; the
candidate's `x` is built from the history's own series (§3). Seeds: path `i` of scenario `s` uses
`random.Random(733 * 100003 + s * 1000003 + i)`, with `s` the scenario's index in the order below.

- **Size:** DELTA = 0, NOISE = 1, on the Full and on the Post-2020 history. Reported: the false-detection share by
  each look and by the last, without the MME gate (the test's own size) and with it.
- **Power:** DELTA = 3% and 10%, NOISE = 1, on both histories; and NOISE = 0.5 on the Full history. Reported: the
  gated detection share by each look and by the last, and the days to first detection among detected paths.
- **Smallest skill at 80% power:** DELTA on the grid 3%, 5%, 7.5%, 10%, 15%, 20% and 30%, NOISE = 1, Full history. The
  smallest grid value whose gated power by the last look is at least 80%; if none, "none on the grid".

The calibrated `c` is fixed by the Full pool in every scenario (the protocol calibrates once on the whole
development history); the Post-2020 rows therefore show what that fixed value does on the quieter subperiod.
The Monte Carlo standard error `sqrt(p(1-p)/PATHS)` is reported beside every share.

## 7. The reading rule

1. A design is **admissible** if its size without the MME gate, by its last look, is at most 5% on **both**
   histories (point estimate; the 95% upper bound is shown and a design whose bound exceeds 5% is flagged, not
   excluded).
2. The **recommended** design is the admissible one with the highest gated power at DELTA = 3% on the Full history by
   its last look. Designs within one Monte Carlo standard error of the top are tied, and a tie goes to the design
   with the fewest days. If no admissible design reaches 80% power at 3%, the page says so and gives each design's
   smallest skill at 80% power; whether to change the MME, or the number of days, is then Eleonora's choice.
3. The page ends with the recommended design and a one-line trade-off against D0 (days, power at 3% and 10%,
   smallest skill at 80% power, size). It carries a marked question for Eleonora. It changes no protocol in code; a
   protocol change is a draft decision record for her to merge (§13 of the protocol: the evidence is a synthetic
   demonstration, not any candidate's result).

## 8. What this study does not do

- It reads no day after 2025-12-31 and decides no verdict. The 2026 days that the earlier study scored are not read,
  and the protocol's published critical values (calibrated on a history that includes them) are not used: D0 is
  calibrated again on the pool of §2.
- It does not simulate the B2 half of *Supported* or futility stopping, so its power is an upper bound.
- It does not simulate a candidate of the quality H5 is likely to produce; the noise is borrowed from B1 against B2,
  as in the earlier study. A candidate that tracks B1 more closely has quieter differences and more power.
- The pooled mean over leads 1 to 5 is the protocol's own statistic, so D0 to D2 and D4, D5 already pool horizons.
  The request to compare pooling "instead of scoring each lead" therefore reduces to D3 against the others. Scoring
  each lead separately is not a design: five tests of one forecast are not five independent confirmations.
- The 80% target, the choice of designs, the 2,000 paths and the six-design limit are readings this document makes;
  each is a question in the pull request.
