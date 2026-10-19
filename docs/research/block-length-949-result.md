# Block length and the autocorrelation of H5's loss differentials (#949, H1 step 3)

**Development data, not a verdict.** A report that changes nothing: `scoring_protocol.BLOCK_LENGTH` stays 10 and `docs/decisions/scoring-protocol.md` section 5 is unchanged. No day after 2025-12-31 and no lockbox day is scored. Every figure is read from `docs/research/block-length-949/result.json` by `scripts/block_length_949.py report`.

## Question for Eleonora

**Marked question.** Should the stationary bootstrap's mean block change from 10 business days? This page reports what the loss differentials of `gbm_funding` against B1 and against B2 look like; it does not decide it. The block is hers to change (a section 13 matter).

## Method

d_t = S(B) - S(`gbm_funding`) on the grid CRPS, with B = B1 and with B = B2, on the 1868 decision days 2018-06-29 to 2025-12-23 whose five targets are in `gbm_funding`'s walks and on or before 2025-12-31 (the days of #922; 0 missing forecasts, filled by B1). The lead-averaged d_t is the series the protocol tests. The ACF is the sample autocorrelation; the block length is Politis and White's automatic choice for the stationary bootstrap, with the correction of Patton, Politis and White (2009); both are checked on white noise and on AR(1) series of known answer in `tests/test_block_length_949.py`. The interval is `scoring_protocol.paired_tests` (studentized stationary bootstrap, HAC lag 10, seed 1, 10,000 draws pooled and 4,000 per split), a one-sided 95% lower and upper bound of mean(d) at mean block 5, 10 and 20. Regime and day type are those of the decision day (`metadata/evaluation_splits.json`). A day type's days are not consecutive, so only its interval is given. Groups under 60 days are not tested.

Reproduction: mean S(B2) - S(`gbm_funding`) over the same days is 0.688215 (1868 days) here and 0.688215 (1868 days) in #922's record.

## d_t = S(B1) - S(gbm_funding)

### Autocorrelation and automatic block length, pooled

| series | days | mean d | rho(1) | rho(2) | rho(3) | rho(4) | rho(5) | rho(10) | Politis-White block |
|---|---|---|---|---|---|---|---|---|---|
| lead 1 | 1868 | 0.393 | 0.09 | -0.01 | -0.02 | -0.01 | 0.02 | -0.01 | 3.5 |
| lead 2 | 1868 | 0.460 | 0.18 | -0.03 | -0.05 | -0.02 | 0.00 | 0.01 | 5.1 |
| lead 3 | 1868 | 0.493 | 0.17 | -0.02 | -0.02 | -0.04 | -0.06 | 0.02 | 5.0 |
| lead 4 | 1868 | 0.519 | 0.16 | 0.04 | -0.00 | -0.04 | -0.01 | 0.02 | 4.8 |
| lead 5 | 1868 | 0.516 | 0.19 | 0.04 | -0.01 | -0.01 | -0.00 | 0.01 | 5.2 |
| lead-averaged | 1868 | 0.476 | 0.16 | 0.01 | -0.02 | -0.02 | -0.01 | 0.01 | 4.8 |

### By regime (lead-averaged)

| regime | days | rho(1) | rho(2) | rho(5) | rho(10) | Politis-White block |
|---|---|---|---|---|---|---|
| 2018-19 | 375 | 0.14 | -0.01 | -0.01 | 0.00 | 2.7 |
| 2020 | 251 | 0.21 | -0.04 | -0.10 | -0.06 | 2.8 |
| 2021-23 | 748 | 0.78 | 0.50 | -0.03 | -0.09 | 11.0 |
| 2024 | 250 | 0.43 | 0.09 | -0.09 | 0.15 | 3.8 |
| 2025-26 | 244 | 0.52 | 0.11 | -0.14 | 0.03 | 4.0 |

### Paired interval by mean block (lead-averaged; one-sided 95% bounds of mean d, [lower, upper])

| group | days | mean d | block 5 | block 10 (protocol) | block 20 |
|---|---|---|---|---|---|
| all | 1868 | +0.476 | [+0.241, +1.414] | [+0.236, +1.500] | [+0.226, +1.541] |
| regime 2018-19 | 375 | +1.734 | [+0.625, +8.356] | [+0.576, +9.018] | [+0.605, +9.509] |
| regime 2020 | 251 | +0.227 | [+0.046, +0.521] | [+0.040, +0.469] | [+0.025, +0.439] |
| regime 2021-23 | 748 | -0.006 | [-0.116, +0.074] | [-0.121, +0.071] | [-0.123, +0.068] |
| regime 2024 | 250 | +0.272 | [+0.140, +0.619] | [+0.129, +0.672] | [+0.119, +0.730] |
| regime 2025-26 | 244 | +0.489 | [+0.247, +0.955] | [+0.239, +0.980] | [+0.221, +1.034] |
| day type month_end | 149 | +0.033 | [-0.111, +0.158] | [-0.128, +0.156] | [-0.130, +0.142] |
| day type ordinary | 1600 | +0.356 | [+0.228, +0.609] | [+0.224, +0.621] | [+0.216, +0.657] |
| day type quarter_end | 30 | too thin | | | |
| day type tax_date | 89 | +3.539 | [-0.590, +71.758] | [-0.309, +64.119] | [+0.456, +52.443] |

## d_t = S(B2) - S(gbm_funding)

### Autocorrelation and automatic block length, pooled

| series | days | mean d | rho(1) | rho(2) | rho(3) | rho(4) | rho(5) | rho(10) | Politis-White block |
|---|---|---|---|---|---|---|---|---|---|
| lead 1 | 1868 | 0.844 | 0.54 | 0.40 | 0.39 | 0.37 | 0.38 | 0.29 | 72.1 |
| lead 2 | 1868 | 0.734 | 0.56 | 0.41 | 0.37 | 0.37 | 0.39 | 0.33 | 73.0 |
| lead 3 | 1868 | 0.658 | 0.54 | 0.41 | 0.36 | 0.34 | 0.36 | 0.30 | 73.2 |
| lead 4 | 1868 | 0.623 | 0.55 | 0.43 | 0.34 | 0.30 | 0.34 | 0.28 | 73.0 |
| lead 5 | 1868 | 0.582 | 0.58 | 0.44 | 0.33 | 0.30 | 0.31 | 0.27 | 72.8 |
| lead-averaged | 1868 | 0.688 | 0.87 | 0.76 | 0.66 | 0.59 | 0.55 | 0.47 | 73.2 |

### By regime (lead-averaged)

| regime | days | rho(1) | rho(2) | rho(5) | rho(10) | Politis-White block |
|---|---|---|---|---|---|---|
| 2018-19 | 375 | 0.75 | 0.59 | 0.16 | 0.12 | 16.1 |
| 2020 | 251 | 0.95 | 0.88 | 0.68 | 0.48 | 21.7 |
| 2021-23 | 748 | 0.95 | 0.91 | 0.82 | 0.80 | 47.5 |
| 2024 | 250 | 0.58 | 0.21 | 0.12 | 0.07 | 5.8 |
| 2025-26 | 244 | 0.88 | 0.72 | 0.56 | 0.49 | 23.2 |

### Paired interval by mean block (lead-averaged; one-sided 95% bounds of mean d, [lower, upper])

| group | days | mean d | block 5 | block 10 (protocol) | block 20 |
|---|---|---|---|---|---|
| all | 1868 | +0.688 | [+0.485, +0.941] | [+0.458, +0.984] | [+0.417, +1.051] |
| regime 2018-19 | 375 | +0.371 | [+0.018, +0.797] | [+0.007, +0.841] | [+0.034, +0.842] |
| regime 2020 | 251 | +1.369 | [+0.634, +2.544] | [+0.586, +2.950] | [+0.553, +3.496] |
| regime 2021-23 | 748 | +0.764 | [+0.531, +1.059] | [+0.485, +1.147] | [+0.424, +1.318] |
| regime 2024 | 250 | -0.033 | [-0.274, +0.148] | [-0.287, +0.157] | [-0.295, +0.163] |
| regime 2025-26 | 244 | +0.982 | [+0.121, +2.276] | [+0.002, +2.660] | [-0.165, +3.319] |
| day type month_end | 149 | +0.743 | [+0.402, +1.298] | [+0.437, +1.254] | [+0.476, +1.161] |
| day type ordinary | 1600 | +0.659 | [+0.441, +0.920] | [+0.406, +0.963] | [+0.379, +1.034] |
| day type quarter_end | 30 | too thin | | | |
| day type tax_date | 89 | +1.115 | [+0.424, +2.182] | [+0.340, +2.358] | [+0.327, +2.337] |

## Reading

Against B1, the lead-averaged differentials are close to uncorrelated beyond lag 1 (rho(1) 0.16, rho(2) 0.01) and Politis and White ask for a block of 4.8 days pooled; the protocol's 10 is longer than that. Against B2 the differentials are strongly persistent (rho(1) 0.87, rho(10) 0.47) and the automatic block is 73.2 days pooled, well above 10. That persistence is mostly a slow change of level from regime to regime (the regime rows give the within-regime figures), so the pooled automatic block may overstate the dependence a resample sees within a regime; the automatic rule assumes a stationary series, which these are not across regimes.

What the block changes in the interval: pooled against B1 the one-sided 95% lower bound of mean(d) is +0.241, +0.236 and +0.226 at mean block 5, 10 and 20; against B2 it is +0.485, +0.458 and +0.417. A longer block widens the interval where the differentials are persistent. Whether a group's lower bound changes sign between block 10 and block 20 is visible in the tables above.

The block stays 10. Whether it changes is Eleonora's decision (the marked question above); nothing here is a verdict for a hypothesis.
