# Power study of the test in force (H1, #769)

**Serves:** H1 (the scorer and the confirmation design), after #656 and before #768. Protocol v1 is
`docs/decisions/scoring-protocol.md`; the test in force is its §5/§6 as amended by ruling 5 (a §13 change, PR #695).
Eleonora ruled on 14 October 2026 (relayed on #769): re-run the power study on the test in force; the MME and B3's
verdict rule (#768) are settled after this result, not before.

**This document is committed before the study runs.** `scripts/power_study_769.py` reads it as the rule; a result that
disagrees with this text is a defect in the script. It supersedes nothing: `docs/research/power-study-656.md` and its
result stay as published (they are of the test before ruling 5). Development data never gives a verdict, and the study
scores no day after 2026-09-03. It decides nothing: the MME, the power target and the confirmation design are Eleonora's.

## 1. The test

Exactly `scoring_protocol`'s, read from the module and the calibration record, not re-implemented:

- Looks at 60, 125 and 250 days. Look 1 checks futility only. Looks 2 and 3 are **detected** when
  `mean(d) - c * se > 0`, with `se` the Newey-West standard error at lag 10 and `c` the grid comparison's calibrated
  value (`CRITICAL_VALUES["B2-B1"]`, which must equal `docs/research/protocol-calibration/result.json`).
- Detection also requires the point skill against B1 to be at least `MME`. Both figures are reported, with and
  without that gate; the gated one is the primary (it is Supported's B1 half).
- The B2 half is not simulated, so power is an upper bound on the power of the full rule. Futility is non-binding and
  Supported is read first, so futility never turns a detection into a non-detection and is not simulated.
- A path stops at its first detection; power at a look is the share detected at or before it.

## 2. The candidate

As #656 §3: `d_t = DELTA * S1_t + NOISE * (e_t - mean(e))`, `e_t = S1_t - S2_t`. True skill against B1 is `DELTA`
exactly. Primary: `DELTA` = 0.03, `NOISE` = 1. Reported grid: `DELTA` in 0.03, 0.04, 0.05, 0.06, 0.08, 0.10 at
`NOISE` = 1; `NOISE` in 0.5 and 0.25 at `DELTA` = 0.03; and the null, `DELTA` = 0.

## 3. Histories and generators (the part #656 did not vary)

The critical values are calibrated on circular blocks of 10 over the **full** development history (from 2018-06-29).
#656's paths were stationary-bootstrap resamples (mean block 10) of the **post-2020-04** history. The study crosses
both, so the result shows what the power depends on:

| reading | history | path generator |
|---|---|---|
| (a) | full (from 2018-06-29) | circular blocks of 10, the calibration's own |
| (b) | post-2020-04 (from two years after the panel's first row) | circular blocks of 10 |
| (c) | full | stationary bootstrap, mean block 10 |
| (d) | post-2020-04 | stationary bootstrap, mean block 10, #656's own |

Reading (a) is the one under which the critical values are calibrated, so its null rate is the test's size as
designed; the others show the departure. Nothing here chooses a reading as the answer: that is Eleonora's.

## 4. What is reported

Per reading and cell: power at 125 and 250 days (gated and ungated), the Monte Carlo standard error
`sqrt(p(1-p)/paths)`, the series' skill against B1 and mean d. Per reading: the null's false-detection share at 125
and 250 days (size, against the nominal 0.05 overall); **days needed**, the smallest of 125 and 250 whose cumulative
gated power reaches **80%** (not in the protocol; Eleonora's to confirm), else `null`; and the smallest `DELTA` on the
grid whose gated power at 250 days reaches 80%, else `null`. Paths per cell: 2,000. Seeds are fixed in the script.

## 5. Not decided here

The 80% target, the primary reading, the paths, and whether the MME or the verdict rule changes (#768). Each is a
question in the pull request.
