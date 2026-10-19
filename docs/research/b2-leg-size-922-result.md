# The size of the B2 leg of "Supported" (#922, H1; finding #913)

**Development data only; no verdict, no lockbox day scored, and no decided value moves.** `CRITICAL_VALUES`, `scoring_protocol.py` and `docs/decisions/scoring-protocol.md` are unchanged by this pull request. Every figure is read from `docs/research/b2-leg-size-922/result.json` by `scripts/b2_leg_size_922.py report`. Whether and how the critical value is recalibrated is Eleonora's (#913, ruling 5, the #878 amendment); this page gives her the number.

## Method

`verdict` passes the leg against B2 when `against_b2.lower_bound(critical) > 0`, with d = S(B2) − S(candidate). With no true skill against B2, the share of windows that pass is the leg's size. Each cell is the share of 20,000 windows (seed 1) of the stated length, from `scoring_protocol.window_t_statistics` of the centred d, whose studentized mean is above the value; ± is 1.96 Monte Carlo standard errors. The nominal size of the 250-day value is 4.8% and of the 125-day value 0.56%. The amended values are 1.347 at 250 days and 2.548 at 125 (the record of #873); the earlier ones 2.426 and 3.419 (the values in force). Histories: `full` (decision days from 2018-06-29), `without 2019-09-18` (a diagnostic, the protocol never trims) and `post-2020-04` (decision days from 2020-04-03, where every confirmation day falls). `B1` runs to 2026-09-03 as #913's does; `B1 (walk days)` and `gbm_funding` are on the days `gbm_funding`'s walks cover (fifth target on or before 2025-12-31), its missing forecasts (0 decision days) filled by B1.

## 1. Row (a) reproduces #913

#913 states no seed, so its figures are an independent draw of the same number of windows: "within the Monte Carlo error" is 1.96 × √2 standard errors of one estimate (plus 0.05 points for #913's rounding).

| history | days | value | here | #913 | within the Monte Carlo error of two draws |
|---|---|---|---|---|---|
| full | 250 | amended | 24.6% ± 0.6 | 24.50% | yes |
| full | 250 | earlier | 4.8% ± 0.3 | 4.85% | yes |
| full | 125 | amended | 3.5% ± 0.3 | 3.10% | yes |
| full | 125 | earlier | 0.6% ± 0.1 | 0.55% | yes |
| without 2019-09-18 | 250 | amended | 13.6% ± 0.5 | 13.00% | yes |
| without 2019-09-18 | 250 | earlier | 1.7% ± 0.2 | 1.60% | yes |

Row (a) reproduces #913's figures.

## 2. The size of the B2 leg

| candidate | history | days | series days | amended value | earlier value |
|---|---|---|---|---|---|
| B1 | full | 250 | 2037 | 24.6% ± 0.6 | 4.8% ± 0.3 |
| B1 | full | 125 | 2037 | 3.5% ± 0.3 | 0.6% ± 0.1 |
| B1 | without 2019-09-18 | 250 | 2036 | 13.6% ± 0.5 | 1.7% ± 0.2 |
| B1 | without 2019-09-18 | 125 | 2036 | 1.4% ± 0.2 | 0.2% ± 0.1 |
| B1 | post-2020-04 | 250 | 1598 | 9.9% ± 0.4 | 0.7% ± 0.1 |
| B1 | post-2020-04 | 125 | 1598 | 0.8% ± 0.1 | 0.1% ± 0.0 |
| B1 (walk days) | full | 250 | 1868 | 25.5% ± 0.6 | 5.5% ± 0.3 |
| B1 (walk days) | full | 125 | 1868 | 3.7% ± 0.3 | 0.5% ± 0.1 |
| B1 (walk days) | without 2019-09-18 | 250 | 1867 | 13.2% ± 0.5 | 1.7% ± 0.2 |
| B1 (walk days) | without 2019-09-18 | 125 | 1867 | 1.4% ± 0.2 | 0.1% ± 0.1 |
| B1 (walk days) | post-2020-04 | 250 | 1429 | 9.8% ± 0.4 | 0.9% ± 0.1 |
| B1 (walk days) | post-2020-04 | 125 | 1429 | 0.7% ± 0.1 | 0.1% ± 0.0 |
| gbm_funding | full | 250 | 1868 | 9.6% ± 0.4 | 0.9% ± 0.1 |
| gbm_funding | full | 125 | 1868 | 0.6% ± 0.1 | 0.1% ± 0.0 |
| gbm_funding | without 2019-09-18 | 250 | 1867 | 9.6% ± 0.4 | 0.7% ± 0.1 |
| gbm_funding | without 2019-09-18 | 125 | 1867 | 0.6% ± 0.1 | 0.1% ± 0.0 |
| gbm_funding | post-2020-04 | 250 | 1429 | 9.2% ± 0.4 | 0.8% ± 0.1 |
| gbm_funding | post-2020-04 | 125 | 1429 | 0.6% ± 0.1 | 0.0% ± 0.0 |

## 3. What the table shows

At the amended values, for a candidate with no skill against B2, the B2 leg passes in 24.6% ± 0.6 of 250-day windows when the candidate is B1 and in 9.6% ± 0.4 when it is `gbm_funding`, on the full history; on post-2020-04 history they are 9.9% ± 0.4 and 9.2% ± 0.4. At the earlier values the same cells are 4.8% ± 0.3, 0.9% ± 0.1, 0.7% ± 0.1 and 0.8% ± 0.1. The size depends on the candidate's own series of d; the two candidates' rows differ.

Nothing here is a verdict for a hypothesis; the choice of critical value is Eleonora's (#913).
