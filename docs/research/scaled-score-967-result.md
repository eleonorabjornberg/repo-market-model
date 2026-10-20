# A scale-free primary score: size, power and the regime ranking (#967, H1 step 2 and H5)

**Development data, not a verdict.** A report that changes nothing: `scoring_protocol.CRITICAL_VALUES` and `docs/decisions/scoring-protocol.md` are only read. No day after 2025-12-31 and no lockbox day is scored. Everything is declared in `metadata/scaled_score_967.json` before any score and read from `docs/research/scaled-score-967/result.json` by `scripts/scaled_score_967.py report`. The series are development data seen before the declaration.

## Question for Eleonora (marked)

**Does the primary score change?** Replacing raw grid CRPS by the scaled score in the confirmation test is a section 13 decision and is hers. This page is its evidence: the scale's size and power, and whether it ranks the two candidates differently. It changes no protocol in code.

## The scale

The scale of a decision day is the median of B2's grid CRPS over the trailing year (252 pool positions, the last 6 left out so that every outcome in it was public at the instant) of cells whose target day has the same pressure-day type; a type with fewer than 20 cells takes the median of the whole window. A decision day's scaled score is the mean over its five leads of the cell over its scale. The pool is 1868 decision days from 2018-06-29 to 2025-12-23; the first scaled day is 2019-07-12; the designs below are read on the 1429 post-2020 days (from 2020-04-03).

## 1. Size and power of #733's six designs under the scale

Contiguous calibration (#963): the critical value of a look is the quantile of every contiguous post-2020 window of that length, on S(B2) - S(B1) alone (reading (b), her ruling on PR #695, Q-E), at the look's nominal level. Size is the false-detection share by the last look under no true difference, without the MME gate, on stationary-bootstrap paths of the same history (2000 paths a scenario); power is the gated share. D4 and D5 use this study's scale; D4old and D5old use #733's (the trailing 60-day mean of B1); D0t and D4t are the trapezoid companion (#259) on the raw and the scaled 250-day design. Every share carries its Monte Carlo standard error.

| design | days | scale | score | c at look 2 / 3 (contiguous) | c at look 2 / 3 (stationary-10) | size | size, circular | power at 3% | power at 10% | smallest skill at 80% |
|---|---|---|---|---|---|---|---|---|---|---|
| D0 | 250 | raw | grid | 16.61 / 4.45 | 3.49 / 2.03 | 1.1% ± 0.2% | 0.3% | 1.3% ± 0.3% | 1.4% ± 0.3% | none on the grid |
| D1 | 375 | raw | grid | 8.05 / 3.55 | 3.21 / 2.01 | 2.5% ± 0.3% | 0.8% | 3.0% ± 0.4% | 5.5% ± 0.5% | none on the grid |
| D2 | 500 | raw | grid | 5.08 / 2.67 | 3.15 / 2.03 | 5.6% ± 0.5% | 1.6% | 8.4% ± 0.6% | 13.4% ± 0.8% | none on the grid |
| D3 | 250 | raw | grid | 14.74 / 3.94 | 3.33 / 1.95 | 4.5% ± 0.5% | 1.5% | 4.2% ± 0.5% | 5.3% ± 0.5% | none on the grid |
| D4 | 250 | new | grid | 15.66 / 4.32 | 3.88 / 2.33 | 0.0% ± 0.0% | 0.0% | 0.0% ± 0.0% | 0.1% ± 0.1% | none on the grid |
| D5 | 375 | new | grid | 6.60 / 3.62 | 3.60 / 2.30 | 0.1% ± 0.1% | 0.0% | 0.2% ± 0.1% | 0.7% ± 0.2% | none on the grid |
| D4old | 250 | old | grid | 12.26 / 5.42 | 3.34 / 2.02 | 1.4% ± 0.3% | 0.3% | 1.7% ± 0.3% | 2.6% ± 0.4% | none on the grid |
| D5old | 375 | old | grid | 8.87 / 4.51 | 3.20 / 2.04 | 1.9% ± 0.3% | 0.2% | 2.5% ± 0.4% | 4.5% ± 0.5% | none on the grid |
| D0t | 250 | raw | trapezoid | 17.18 / 4.52 | 3.54 / 2.05 | 1.4% ± 0.3% | 0.3% | 1.5% ± 0.3% | 1.7% ± 0.3% | none on the grid |
| D4t | 250 | new | trapezoid | 15.43 / 4.27 | 3.87 / 2.30 | 0.0% ± 0.0% | 0.0% | 0.1% ± 0.0% | 0.1% ± 0.1% | none on the grid |

### Gated power by true skill (last look)

| design | 3.0% | 5.0% | 7.5% | 10.0% | 15.0% | 20.0% | 30.0% |
|---|---|---|---|---|---|---|---|
| D0 | 1.3% | 0.8% | 1.4% | 1.4% | 2.4% | 3.5% | 5.4% |
| D1 | 3.0% | 3.6% | 5.0% | 5.5% | 6.1% | 8.6% | 14.9% |
| D2 | 8.4% | 9.7% | 10.7% | 13.4% | 16.8% | 23.5% | 36.0% |
| D3 | 4.2% | 4.9% | 5.3% | 5.3% | 6.7% | 9.1% | 10.3% |
| D4 | 0.0% | 0.0% | 0.0% | 0.1% | 0.4% | 0.4% | 1.8% |
| D5 | 0.2% | 0.0% | 0.4% | 0.7% | 0.9% | 1.7% | 5.7% |
| D4old | 1.7% | 2.1% | 1.7% | 2.6% | 3.8% | 3.8% | 6.3% |
| D5old | 2.5% | 3.3% | 3.1% | 4.5% | 6.2% | 7.0% | 11.6% |
| D0t | 1.5% | 1.0% | 1.6% | 1.7% | 2.5% | 3.6% | 5.5% |
| D4t | 0.1% | 0.0% | 0.2% | 0.1% | 0.7% | 0.7% | 2.1% |

### Kill rule (declared): the scale buys nothing

Fires when D4's gated power at 10% true skill on the post-2020 history is below 20%, or its size is above 5%.

D4: power at 10% 0.1%, size 0.0%. **The rule fires: the scale buys nothing** (power below 20.0%: yes; size above 5.0%: no).

## 2. The regime ranking of the two candidates

d = S(B1) - S(candidate) on the 1611 decision days from 2019-07-12 to 2025-12-23 on which B1 and both candidates have a forecast and the scale exists, split by the regime of the decision day (the declared regimes). The scaled d divides each cell by its scale before averaging; a positive d favours the candidate. Means only: this is an ordering demonstration, not a test.

| regime | days | gbm_funding raw | spread_mr_ctx raw | first, raw | gbm_funding scaled | spread_mr_ctx scaled | first, scaled | order changes |
|---|---|---|---|---|---|---|---|---|
| 2018-19 | 118 | +3.705 | +3.774 | spread_mr_ctx | +2.3306 | +2.2357 | gbm_funding | yes |
| 2020 | 251 | +0.227 | -0.009 | gbm_funding | +0.1171 | +0.0373 | gbm_funding | no |
| 2021-23 | 748 | -0.006 | -0.016 | gbm_funding | +0.0316 | +0.0316 | spread_mr_ctx | yes |
| 2024 | 250 | +0.272 | +0.399 | spread_mr_ctx | +0.5681 | +0.8238 | spread_mr_ctx | no |
| 2025-26 | 244 | +0.489 | +0.642 | spread_mr_ctx | +0.3782 | +0.3932 | spread_mr_ctx | no |

### Kill rule (declared): the misranking demonstration fails

The regimes read (at least 60 days): 2018-19, 2020, 2021-23, 2024, 2025-26. The order changes in: 2018-19, 2021-23. **The demonstration holds: the scaled score ranks the candidates differently in at least one regime.**

## Limits

The history is development data seen before the declaration, so a result is exploration. The paths resample one history, so power is an upper bound (the B2 half of Supported and futility stopping are not simulated), and contiguous calibration rests on a handful of independent stretches (#963). The Full history is not simulated; the scaled series starts when a full trailing year exists. Nothing is registered, published or changed.
