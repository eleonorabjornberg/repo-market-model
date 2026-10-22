# Block length of the loss differentials after April 2020, without 2019-09-18 (#1022, H1 step 3)

**Development data, not a verdict.** A report that changes nothing: `scoring_protocol.BLOCK_LENGTH` stays 10, `WINDOW_BLOCK` and `HAC_LAG` stay as decided, and `docs/decisions/scoring-protocol.md` section 5 is unchanged. No day after 2025-12-31 and no lockbox day is scored. Every figure is read from `docs/research/block-length-1022/result.json` by `scripts/block_length_1022.py report`.

## Question for Eleonora

**Marked question (section 13; the default applies if she has not answered by the next 5 pm batch).** Should the stationary bootstrap's mean block change from 10 business days, now that the post-2020 figures are recomputed? Options:

1. Keep 10 and change nothing now; carry this page and #980's into the confirmation-design decision. **Default.**
2. Move the block for the post-2020 confirmation tests only, to a value she names after reading the table below.
3. Keep the bootstrap's block and take the dependence into the test instead (a fixed-b statistic, or calibration on contiguous windows), as Lens C proposes; this needs its own directive.

## Method

d_t = S(B) - S(`gbm_funding`) on the grid CRPS, lead-averaged, with B = B1 and with B = B2, on the 1868 decision days 2018-06-29 to 2025-12-23 that #980 read (0 missing forecasts, filled by B1), from the same walks. The proxy S(B1) - S(B2) is the difference of the two legs, the series Lens C's `bench_scores.csv` held (B1 and B2 grid CRPS per decision day). Post-2020-04 is the decision days from 2020-04-03, as #886, #922 and #1014 read it. A day removed is dropped from the series (the series is then one day shorter, as #922 trims it). Three histories carry 2019-09-18 or not: the full one, the one without that decision day, and the one without that day and the 5 decision days whose five targets include it. The post-2020-04 history holds none of them, so with and without is one row there. The ACF is the sample autocorrelation about the mean; the automatic block is Politis and White's with the correction of Patton, Politis and White (2009), as in #980, and again with the cap on the truncation lag widened from ceil(sqrt N) + K_N to N / 4; the long-run ratio is Lens C's 1 + 2 sum (1 - k / (L + 1)) rho(k). A group under 120 days is not summarised, and a ratio at lag L needs 3 L days.

Reproduction of #980: the Politis-White block of the pooled full history is 4.8 against B1 and 73.2 against B2 over 1868 days here, and 4.8 and 73.2 over 1868 days in #980's record (equal to 1e-9; the run stops otherwise).

## d = S(B1) - S(gbm_funding), the B1 leg

### Autocorrelation

| group | days | mean d | rho(1) | rho(2) | rho(3) | rho(5) | rho(10) | rho(21) | rho(42) |
|---|---|---|---|---|---|---|---|---|---|
| full | 1868 | 0.476 | 0.16 | 0.01 | -0.02 | -0.01 | 0.01 | 0.02 | 0.01 |
| without 2019-09-18 | 1867 | 0.319 | 0.44 | 0.07 | -0.02 | -0.06 | 0.02 | 0.05 | 0.02 |
| without the decision days reaching 2019-09-18 | 1862 | 0.321 | 0.43 | 0.08 | -0.01 | -0.05 | 0.03 | 0.05 | 0.01 |
| post-2020-04 | 1429 | 0.152 | 0.58 | 0.23 | 0.11 | -0.08 | 0.05 | 0.08 | 0.00 |

### Block length and long-run ratio

| group | days | Politis-White block | block, cap widened to N / 4 | long-run ratio, lag 10 | lag 40 | lag 100 | lag-10 s.e. understates lag-100 by |
|---|---|---|---|---|---|---|---|
| full | 1868 | 4.8 | 4.8 | 1.3 | 1.6 | 1.7 | 1.1x |
| without 2019-09-18 | 1867 | 7.4 | 7.4 | 1.8 | 2.2 | 2.6 | 1.2x |
| without the decision days reaching 2019-09-18 | 1862 | 7.3 | 7.3 | 1.8 | 2.2 | 2.6 | 1.2x |
| post-2020-04 | 1429 | 10.2 | 10.2 | 2.4 | 3.3 | 4.2 | 1.3x |

### Within regime (post-2020-04 days from 2020-04-03; 2018-19 shown with and without 2019-09-18)

| group | days | mean d | rho(1) | rho(2) | rho(3) | rho(5) | rho(10) | rho(21) | rho(42) |
|---|---|---|---|---|---|---|---|---|---|
| 2020 | 187 | 0.186 | 0.55 | 0.42 | 0.29 | 0.03 | -0.06 | 0.08 | 0.04 |
| 2021-23 | 748 | -0.006 | 0.78 | 0.50 | 0.27 | -0.03 | -0.09 | -0.01 | 0.01 |
| 2024 | 250 | 0.272 | 0.43 | 0.09 | 0.01 | -0.09 | 0.15 | 0.12 | 0.07 |
| 2025-26 | 244 | 0.489 | 0.52 | 0.11 | -0.03 | -0.14 | 0.03 | 0.06 | -0.05 |
| 2018-19 (with 2019-09-18) | 375 | 1.734 | 0.14 | -0.01 | -0.03 | -0.01 | 0.00 | 0.01 | -0.00 |
| 2018-19 (without 2019-09-18) | 374 | 0.953 | 0.44 | 0.05 | -0.06 | -0.06 | 0.01 | 0.03 | -0.00 |

| group | days | Politis-White block | block, cap widened to N / 4 | long-run ratio, lag 10 | lag 40 | lag 100 | lag-10 s.e. understates lag-100 by |
|---|---|---|---|---|---|---|---|
| 2020 | 187 | 7.3 | 7.3 | 3.2 | 3.7 | n/a | n/a |
| 2021-23 | 748 | 11.0 | 11.0 | 3.5 | 3.1 | 2.8 | 0.9x |
| 2024 | 250 | 3.8 | 3.8 | 1.8 | 2.4 | n/a | n/a |
| 2025-26 | 244 | 4.0 | 4.0 | 1.6 | 2.0 | n/a | n/a |
| 2018-19 (with 2019-09-18) | 375 | 2.7 | 2.7 | 1.2 | 1.2 | 0.9 | 0.9x |
| 2018-19 (without 2019-09-18) | 374 | 4.3 | 4.3 | 1.6 | 1.5 | 0.9 | 0.7x |

## d = S(B2) - S(gbm_funding), the B2 leg

### Autocorrelation

| group | days | mean d | rho(1) | rho(2) | rho(3) | rho(5) | rho(10) | rho(21) | rho(42) |
|---|---|---|---|---|---|---|---|---|---|
| full | 1868 | 0.688 | 0.87 | 0.76 | 0.66 | 0.55 | 0.47 | 0.36 | 0.19 |
| without 2019-09-18 | 1867 | 0.687 | 0.87 | 0.76 | 0.66 | 0.56 | 0.48 | 0.36 | 0.19 |
| without the decision days reaching 2019-09-18 | 1862 | 0.687 | 0.87 | 0.76 | 0.67 | 0.56 | 0.48 | 0.37 | 0.19 |
| post-2020-04 | 1429 | 0.725 | 0.90 | 0.79 | 0.71 | 0.65 | 0.55 | 0.48 | 0.25 |

### Block length and long-run ratio

| group | days | Politis-White block | block, cap widened to N / 4 | long-run ratio, lag 10 | lag 40 | lag 100 | lag-10 s.e. understates lag-100 by |
|---|---|---|---|---|---|---|---|
| full | 1868 | 73.2 | 100.7 | 7.5 | 19.3 | 29.9 | 2.0x |
| without 2019-09-18 | 1867 | 73.2 | 100.5 | 7.6 | 19.4 | 29.9 | 2.0x |
| without the decision days reaching 2019-09-18 | 1862 | 73.1 | 100.3 | 7.6 | 19.4 | 30.0 | 2.0x |
| post-2020-04 | 1429 | 64.9 | 89.1 | 8.2 | 22.5 | 35.3 | 2.1x |

### Within regime (post-2020-04 days from 2020-04-03; 2018-19 shown with and without 2019-09-18)

| group | days | mean d | rho(1) | rho(2) | rho(3) | rho(5) | rho(10) | rho(21) | rho(42) |
|---|---|---|---|---|---|---|---|---|---|
| 2020 | 187 | 1.248 | 0.96 | 0.90 | 0.84 | 0.72 | 0.48 | 0.31 | 0.11 |
| 2021-23 | 748 | 0.764 | 0.95 | 0.91 | 0.87 | 0.82 | 0.80 | 0.70 | 0.53 |
| 2024 | 250 | -0.033 | 0.58 | 0.21 | 0.14 | 0.12 | 0.07 | 0.10 | -0.07 |
| 2025-26 | 244 | 0.982 | 0.88 | 0.72 | 0.61 | 0.56 | 0.49 | 0.47 | 0.17 |
| 2018-19 (with 2019-09-18) | 375 | 0.371 | 0.75 | 0.59 | 0.41 | 0.16 | 0.12 | -0.02 | -0.03 |
| 2018-19 (without 2019-09-18) | 374 | 0.364 | 0.74 | 0.59 | 0.41 | 0.18 | 0.13 | -0.01 | -0.04 |

| group | days | Politis-White block | block, cap widened to N / 4 | long-run ratio, lag 10 | lag 40 | lag 100 | lag-10 s.e. understates lag-100 by |
|---|---|---|---|---|---|---|---|
| 2020 | 187 | 18.8 | 29.1 | 8.8 | 19.9 | n/a | n/a |
| 2021-23 | 748 | 47.5 | 102.2 | 9.6 | 31.1 | 59.5 | 2.5x |
| 2024 | 250 | 5.8 | 5.8 | 3.2 | 4.0 | n/a | n/a |
| 2025-26 | 244 | 23.2 | 40.4 | 7.4 | 20.2 | n/a | n/a |
| 2018-19 (with 2019-09-18) | 375 | 16.1 | 16.1 | 4.8 | 6.6 | 4.1 | 0.9x |
| 2018-19 (without 2019-09-18) | 374 | 16.3 | 16.3 | 4.9 | 6.8 | 4.1 | 0.9x |

## d = S(B1) - S(B2), the proxy Lens C read

### Autocorrelation

| group | days | mean d | rho(1) | rho(2) | rho(3) | rho(5) | rho(10) | rho(21) | rho(42) |
|---|---|---|---|---|---|---|---|---|---|
| full | 1868 | -0.212 | 0.19 | 0.05 | 0.04 | 0.05 | 0.04 | 0.04 | 0.02 |
| without 2019-09-18 | 1867 | -0.368 | 0.55 | 0.27 | 0.18 | 0.13 | 0.15 | 0.14 | 0.07 |
| without the decision days reaching 2019-09-18 | 1862 | -0.367 | 0.55 | 0.27 | 0.19 | 0.13 | 0.15 | 0.15 | 0.07 |
| post-2020-04 | 1429 | -0.573 | 0.75 | 0.51 | 0.40 | 0.28 | 0.30 | 0.30 | 0.17 |

### Block length and long-run ratio

| group | days | Politis-White block | block, cap widened to N / 4 | long-run ratio, lag 10 | lag 40 | lag 100 | lag-10 s.e. understates lag-100 by |
|---|---|---|---|---|---|---|---|
| full | 1868 | 5.2 | 5.2 | 1.7 | 2.8 | 3.5 | 1.4x |
| without 2019-09-18 | 1867 | 64.8 | 64.8 | 3.4 | 6.9 | 10.2 | 1.7x |
| without the decision days reaching 2019-09-18 | 1862 | 64.9 | 64.9 | 3.4 | 7.0 | 10.3 | 1.7x |
| post-2020-04 | 1429 | 63.8 | 97.9 | 5.2 | 12.8 | 20.9 | 2.0x |

### Within regime (post-2020-04 days from 2020-04-03; 2018-19 shown with and without 2019-09-18)

| group | days | mean d | rho(1) | rho(2) | rho(3) | rho(5) | rho(10) | rho(21) | rho(42) |
|---|---|---|---|---|---|---|---|---|---|
| 2020 | 187 | -1.062 | 0.95 | 0.91 | 0.86 | 0.78 | 0.58 | 0.37 | 0.10 |
| 2021-23 | 748 | -0.770 | 0.89 | 0.75 | 0.65 | 0.50 | 0.43 | 0.41 | 0.40 |
| 2024 | 250 | 0.305 | 0.52 | 0.16 | 0.07 | -0.01 | 0.13 | 0.13 | -0.02 |
| 2025-26 | 244 | -0.493 | 0.67 | 0.34 | 0.17 | 0.09 | 0.18 | 0.24 | 0.07 |
| 2018-19 (with 2019-09-18) | 375 | 1.363 | 0.14 | 0.00 | -0.01 | 0.02 | 0.01 | 0.01 | -0.00 |
| 2018-19 (without 2019-09-18) | 374 | 0.589 | 0.44 | 0.12 | 0.02 | 0.02 | 0.04 | 0.05 | -0.00 |

| group | days | Politis-White block | block, cap widened to N / 4 | long-run ratio, lag 10 | lag 40 | lag 100 | lag-10 s.e. understates lag-100 by |
|---|---|---|---|---|---|---|---|
| 2020 | 187 | 19.5 | 30.5 | 9.2 | 22.7 | n/a | n/a |
| 2021-23 | 748 | 45.7 | 99.3 | 7.3 | 20.2 | 38.7 | 2.3x |
| 2024 | 250 | 4.0 | 4.0 | 2.4 | 3.0 | n/a | n/a |
| 2025-26 | 244 | 6.3 | 6.3 | 3.6 | 7.9 | n/a | n/a |
| 2018-19 (with 2019-09-18) | 375 | 2.6 | 2.6 | 1.4 | 1.6 | 1.1 | 0.9x |
| 2018-19 (without 2019-09-18) | 374 | 4.3 | 4.3 | 2.2 | 2.7 | 1.7 | 0.9x |

## Against Lens C's figures (#958)

Lens C's figures are on a proxy built outside the repository, post-2020-04. The first row is what it reports; the others are this study's, on the same history.

| series | days | rho(1) | rho(2) | rho(3) | rho(5) | rho(10) | rho(21) | rho(42) | Politis-White | ratio lag 10 / 40 / 100 |
|---|---|---|---|---|---|---|---|---|---|---|
| Lens C (its proxy) | | 0.726 | 0.484 | 0.363 | 0.249 | 0.278 | 0.307 | 0.162 | 108 | 4.9 / 11.9 / 19.3 |
| this study, d = S(B1) - S(gbm_funding), the B1 leg | 1429 | 0.578 | 0.231 | 0.108 | -0.083 | 0.045 | 0.077 | 0.001 | 10.2 (10.2 widened) | 2.4 / 3.3 / 4.2 |
| this study, d = S(B2) - S(gbm_funding), the B2 leg | 1429 | 0.904 | 0.793 | 0.713 | 0.646 | 0.553 | 0.484 | 0.253 | 64.9 (89.1 widened) | 8.2 / 22.5 / 35.3 |
| this study, d = S(B1) - S(B2), the proxy Lens C read | 1429 | 0.748 | 0.511 | 0.399 | 0.278 | 0.304 | 0.303 | 0.165 | 63.8 (97.9 widened) | 5.2 / 12.8 / 20.9 |

Lens C's Politis-White block for 2021-23 is 114 days; the proxy here gives 45.7 (99.3 with the widened cap). #980's pooled figures were 4.8 against B1 and 73.2 against B2 on the full history.

## Reading

Development data; nothing here is a verdict and no constant moves.

1. **Without 2019-09-18, the B1 leg's block moves from 4.8 to 7.4 and the B2 leg's does not move (73.2 to 73.2).** The day is one observation in 1868, but it is B1's one large loss, and it hides B1's dependence; dropping the 5 decision days whose targets include it changes nothing further. Post-2020-04 holds none of them.
2. **Post-2020-04, the B1 leg's block is 10.2, close to the protocol's 10; the B2 leg's is 64.9 (89.1 with the cap widened).** #980's pooled ~10 was an average over the two legs of a number that was 4.8 against B1 and 73.2 against B2 on the full history; it does not describe the B2 leg. The long-run ratio at lag 100 is 35.3 for the B2 leg and 4.2 for the B1 leg: the lag-10 standard error understates the lag-100 one by 2.1x for the B2 leg.
3. **By regime** the B2 leg's block is 18.8 in 2020, 47.5 in 2021-23 (102.2 widened), 5.8 in 2024 and 23.2 in 2025-26; the B1 leg's is 7.3, 11.0, 3.8 and 4.0. The slow dependence is a 2020 to 2023 feature (the B2 leg's rho(21) is 0.70 in 2021-23 and 0.10 in 2024).
4. **Lens C's figures.** Its autocorrelations are reproduced by the proxy S(B1) - S(B2) post-2020-04 (rho(1) 0.748 against 0.726, rho(10) 0.304 against 0.278, rho(42) 0.165 against 0.162) and its long-run ratios nearly so (5.2 / 12.8 / 20.9 against 4.9 / 11.9 / 19.3). Its Politis-White block of 108 is not reproduced exactly: the proxy gives 63.8 with the published cap on the truncation lag and 97.9 with it widened to N / 4, so the figure of 108 lies in the same range and depends on that cap (and on the unseen proxy file); the order of magnitude, tens of days, is confirmed. The refutation is of #980's ~10 as a description of the series the protocol tests against B2, not of Lens C's number. Lens C's proxy is S(B1) - S(B2), which is not either leg; for the legs, the B1 leg is near 10 and the B2 leg near 65 to 90.
5. **What stays open.** The Politis-White rule picks the block for the mean of a series; the protocol's interval is for the mean of a lead-averaged d_t, studentized, so the right block for the test is a question of coverage, which this page does not measure. #980 measured the interval at blocks 5, 10 and 20 and that is not repeated. The block choice is the marked question above and stays Eleonora's.
