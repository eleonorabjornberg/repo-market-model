# A scale-free primary score, calibrated on the series the paths use (#1013, H1 step 2 and H5)

**Development data, not a verdict.** A report that changes nothing: `scoring_protocol.CRITICAL_VALUES` and `docs/decisions/scoring-protocol.md` are only read. No day after 2025-12-31 and no lockbox day is scored. Everything is declared in `metadata/scaled_score_967.json` before any score and read from `docs/research/scaled-score-1013/result.json` by `scripts/scaled_score_1013.py report`. The series are development data seen before the declaration.

## Question for Eleonora (marked)

**Does the primary score change?** Replacing raw grid CRPS by the scaled score in the confirmation test is a section 13 decision and is hers. This page is its evidence: the scale's size and power, and whether it ranks the two candidates differently. It changes no protocol in code.

## The scale

The scale of a decision day is the median of B2's grid CRPS over the trailing year (252 pool positions, the last 6 left out so that every outcome in it was public at the instant) of cells whose target day has the same pressure-day type; a type with fewer than 20 cells takes the median of the whole window. A decision day's scaled score is the mean over its five leads of the cell over its scale. The pool is 1868 decision days from 2018-06-29 to 2025-12-23; the first scaled day is 2019-07-12; the designs below are read on the 1429 post-2020 days (from 2020-04-03).

## 1. Size and power of #733's six designs under the scale

Contiguous calibration (#963): the critical value of a look is the quantile of every contiguous post-2020 window of that length, on e = S(B1) - S(B2) alone, the series the paths are built on (reading (b), her ruling on PR #695, Q-E), at the look's nominal level. Size is the false-detection share by the last look under no true difference, without the MME gate, on stationary-bootstrap paths of the same history (2000 paths a scenario); power is the gated share. D4 and D5 use this study's scale; D4old and D5old use #733's (the trailing 60-day mean of B1); D0t and D4t are the trapezoid companion (#259) on the raw and the scaled 250-day design. Every share carries its Monte Carlo standard error.

| design | days | scale | score | c at look 2 / 3 (contiguous) | c at look 2 / 3 (stationary-10) | size | size, circular | power at 3% | power at 10% | smallest skill at 80% |
|---|---|---|---|---|---|---|---|---|---|---|
| D0 | 250 | raw | grid | 11.43 / 7.28 | 6.16 / 3.15 | 0.1% ± 0.0% | 0.0% | 0.1% ± 0.0% | 0.2% ± 0.1% | none on the grid |
| D1 | 375 | raw | grid | 6.97 / 7.29 | 5.45 / 2.93 | 0.1% ± 0.1% | 0.0% | 0.0% ± 0.0% | 0.2% ± 0.1% | none on the grid |
| D2 | 500 | raw | grid | 8.21 / 6.52 | 5.03 / 2.78 | 0.0% ± 0.0% | 0.0% | 0.1% ± 0.0% | 0.1% ± 0.1% | none on the grid |
| D3 | 250 | raw | grid | 13.30 / 8.98 | 7.61 / 3.66 | 0.1% ± 0.1% | 0.0% | 0.1% ± 0.1% | 0.2% ± 0.1% | none on the grid |
| D4 | 250 | new | grid | 12.67 / 2.69 | 3.45 / 1.96 | 1.1% ± 0.2% | 0.1% | 2.0% ± 0.3% | 3.4% ± 0.4% | none on the grid |
| D5 | 375 | new | grid | 3.39 / 2.48 | 3.14 / 1.94 | 2.0% ± 0.3% | 0.5% | 3.1% ± 0.4% | 6.7% ± 0.6% | none on the grid |
| D4old | 250 | old | grid | 9.01 / 7.80 | 8.06 / 3.82 | 0.5% ± 0.2% | 0.1% | 0.4% ± 0.1% | 1.1% ± 0.2% | none on the grid |
| D5old | 375 | old | grid | 9.93 / 8.81 | 7.30 / 3.47 | 0.1% ± 0.0% | 0.1% | 0.1% ± 0.1% | 0.5% ± 0.2% | none on the grid |
| D0t | 250 | raw | trapezoid | 11.60 / 7.72 | 6.44 / 3.23 | 0.1% ± 0.0% | 0.0% | 0.1% ± 0.0% | 0.2% ± 0.1% | none on the grid |
| D4t | 250 | new | trapezoid | 13.45 / 2.85 | 3.65 / 2.05 | 1.1% ± 0.2% | 0.1% | 1.8% ± 0.3% | 2.9% ± 0.4% | none on the grid |

### Gated power by true skill (last look)

| design | 3.0% | 5.0% | 7.5% | 10.0% | 15.0% | 20.0% | 30.0% |
|---|---|---|---|---|---|---|---|
| D0 | 0.1% | 0.0% | 0.1% | 0.2% | 0.2% | 0.2% | 0.1% |
| D1 | 0.0% | 0.1% | 0.2% | 0.2% | 0.3% | 0.4% | 0.4% |
| D2 | 0.1% | 0.0% | 0.1% | 0.1% | 0.2% | 0.2% | 0.8% |
| D3 | 0.1% | 0.0% | 0.1% | 0.2% | 0.1% | 0.2% | 0.1% |
| D4 | 2.0% | 1.7% | 2.7% | 3.4% | 5.8% | 8.9% | 17.2% |
| D5 | 3.1% | 3.5% | 5.5% | 6.7% | 10.4% | 15.4% | 31.3% |
| D4old | 0.4% | 0.6% | 0.9% | 1.1% | 1.1% | 1.0% | 1.9% |
| D5old | 0.1% | 0.0% | 0.1% | 0.5% | 0.4% | 0.4% | 0.4% |
| D0t | 0.1% | 0.0% | 0.1% | 0.2% | 0.1% | 0.2% | 0.1% |
| D4t | 1.8% | 1.5% | 2.6% | 2.9% | 5.0% | 8.2% | 15.2% |

### Kill rule (declared): the scale buys nothing

Fires when D4's gated power at 10% true skill on the post-2020 history is below 20%, or its size is above 5%.

D4: power at 10% 3.4%, size 1.1%. **The rule fires: the scale buys nothing** (power below 20.0%: yes; size above 5.0%: no).

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

## Against #999 (calibrated on -e)

#999 (`docs/research/scaled-score-967-result.md`, which stands) built its paths on `e` = S(B1) - S(B2) and calibrated on `-e` (finding #1000). This page calibrates on `e`, as the ruling of 19 October 2026 on #913 puts each leg in its own orientation. Contiguous critical values at the last two looks and the gated figures, #999 then this page. Nothing else differs: the declaration, scale, generator, seeds, paths and windows are #999's.

| design | c at look 2 / 3, #999 | c at look 2 / 3, here | stationary-10, #999 | stationary-10, here | size, #999 | size, here | power at 10%, #999 | power at 10%, here |
|---|---|---|---|---|---|---|---|---|
| D0 | 16.61 / 4.45 | 11.43 / 7.28 | 3.49 / 2.03 | 6.16 / 3.15 | 1.1% | 0.1% | 1.4% | 0.2% |
| D1 | 8.05 / 3.55 | 6.97 / 7.29 | 3.21 / 2.01 | 5.45 / 2.93 | 2.5% | 0.1% | 5.5% | 0.2% |
| D2 | 5.08 / 2.67 | 8.21 / 6.52 | 3.15 / 2.03 | 5.03 / 2.78 | 5.6% | 0.0% | 13.4% | 0.1% |
| D3 | 14.74 / 3.94 | 13.30 / 8.98 | 3.33 / 1.95 | 7.61 / 3.66 | 4.5% | 0.1% | 5.3% | 0.2% |
| D4 | 15.66 / 4.32 | 12.67 / 2.69 | 3.88 / 2.33 | 3.45 / 1.96 | 0.0% | 1.1% | 0.1% | 3.4% |
| D5 | 6.60 / 3.62 | 3.39 / 2.48 | 3.60 / 2.30 | 3.14 / 1.94 | 0.1% | 2.0% | 0.7% | 6.7% |
| D4old | 12.26 / 5.42 | 9.01 / 7.80 | 3.34 / 2.02 | 8.06 / 3.82 | 1.4% | 0.5% | 2.6% | 1.1% |
| D5old | 8.87 / 4.51 | 9.93 / 8.81 | 3.20 / 2.04 | 7.30 / 3.47 | 1.9% | 0.1% | 4.5% | 0.5% |
| D0t | 17.18 / 4.52 | 11.60 / 7.72 | 3.54 / 2.05 | 6.44 / 3.23 | 1.4% | 0.1% | 1.7% | 0.2% |
| D4t | 15.43 / 4.27 | 13.45 / 2.85 | 3.87 / 2.30 | 3.65 / 2.05 | 0.0% | 1.1% | 0.1% | 2.9% |

### Row check: this script under the old orientation

D0 and D4 calibrated on `-e` again, same seeds and paths. The row check passes: both reproduce #999 exactly.

| design | figure | #999 | re-run on -e |
|---|---|---|---|
| D0 | size | 1.1% | 1.1% |
| D0 | power_3 | 1.3% | 1.3% |
| D0 | power_10 | 1.4% | 1.4% |
| D4 | size | 0.0% | 0.0% |
| D4 | power_3 | 0.0% | 0.0% |
| D4 | power_10 | 0.1% | 0.1% |

### Declared readings, #999 then here

- The scale buys nothing: #999 fires (D4 power at 10% 0.1%, size 0.0%); here fires (D4 power at 10% 3.4%, size 1.1%).
- The misranking demonstration: #999 holds; here holds. The regime split uses no critical value, so it is #999's.


## Limits

The history is development data seen before the declaration, so a result is exploration. The paths resample one history, so power is an upper bound (the B2 half of Supported and futility stopping are not simulated), and contiguous calibration rests on a handful of independent stretches (#963). The Full history is not simulated; the scaled series starts when a full trailing year exists. Nothing is registered, published or changed.
