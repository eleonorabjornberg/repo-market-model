# Each leg of "Supported" in its own orientation, on post-2020-04 history (#929, H1; finding #913)

**Development data only; no verdict, no lockbox day scored, and no decided value moves.** `CRITICAL_VALUES` and `FUTILITY_CRITICAL_VALUES` are unchanged by this pull request; `B2_LEG_CRITICAL_VALUES` (new, empty) is where a per-leg value would be declared once Eleonora has merged the amendment. Every figure is read from `docs/research/per-leg-calibration-929/result.json` by `scripts/per_leg_calibration_929.py report`.

## Method

`verdict` passes "Supported" when the lower bound of mean(d) is above zero against B1 (d = S(B1) − S(candidate)) and against B2 (d = S(B2) − S(candidate), B2 the benchmark). Each leg's value is the 1 − level quantile of `scoring_protocol.window_t_statistics` of a centred series in that leg's orientation, at the protocol's level for the look (4.82% at 250 days, 0.56% at 125), 20,000 windows, seed 1. The calibration series stands a forecaster in for the candidate: B2 for the leg against B1 (d = S(B1) − S(B2), as #873 calibrated), B1 for the leg against B2 (d = S(B2) − S(B1), as #913 sized). Histories: `full` (decision days from 2018-06-29), `without 2019-09-18` (a diagnostic, the protocol never trims) and `post-2020-04` (decision days from 2020-04-03, where every confirmation day falls). ± is 1.96 Monte Carlo standard errors.

## 1. The calibrated values

| leg | history | series days | 250 days | 125 days |
|---|---|---|---|---|
| against B1 | full | 2037 | 1.347 | 2.548 |
| against B1 | without 2019-09-18 | 2036 | 1.875 | 3.364 |
| against B1 | post-2020-04 | 1598 | 2.438 | 4.727 |
| against B1 | post-2020-04 from 2020-04-01 | 1600 | 2.427 | 4.808 |
| against B2 | full | 2037 | 2.426 | 3.419 |
| against B2 | without 2019-09-18 | 2036 | 1.924 | 2.990 |
| against B2 | post-2020-04 | 1598 | 1.701 | 2.682 |
| against B2 | post-2020-04 from 2020-04-01 | 1600 | 1.685 | 2.670 |

For comparison, the value in force is 2.426 at 250 days and 3.419 at 125; #878's amended value (one value for both legs) is 1.347 and 2.548.

## 2. Row-checks

| figure | here | reference | holds |
|---|---|---|---|
| B1 leg, without 2019-09-18, 250 days: value | 1.8748 | 1.8750 | yes |
| B1 leg, without 2019-09-18, 125 days: value | 3.3642 | 3.3640 | yes |
| B1 leg, post-2020-04 from 2020-04-01, 250 days: value | 2.4269 | 2.4270 | yes |
| B1 leg, post-2020-04 from 2020-04-01, 125 days: value | 4.8077 | 4.8080 | yes |
| B1 leg, full, 250 days: value (#878's amended value) | 1.3468 | 1.3468 | yes |
| B1 leg, full, 125 days: value (#878's amended value) | 2.5476 | 2.5476 | yes |
| B2 leg, B1, full, 250 days: size at the amended value | 0.2455 | 0.2455 | yes |
| B2 leg, B1, full, 250 days: size at the earlier value | 0.0483 | 0.0483 | yes |
| B2 leg, B1, full, 125 days: size at the amended value | 0.0345 | 0.0345 | yes |
| B2 leg, B1, full, 125 days: size at the earlier value | 0.0056 | 0.0056 | yes |
| B2 leg, B1, without 2019-09-18, 250 days: size at the amended value | 0.1359 | 0.1359 | yes |
| B2 leg, B1, without 2019-09-18, 250 days: size at the earlier value | 0.0169 | 0.0169 | yes |
| B2 leg, B1, without 2019-09-18, 125 days: size at the amended value | 0.0139 | 0.0139 | yes |
| B2 leg, B1, without 2019-09-18, 125 days: size at the earlier value | 0.0020 | 0.0020 | yes |
| B2 leg, B1, post-2020-04, 250 days: size at the amended value | 0.0992 | 0.0992 | yes |
| B2 leg, B1, post-2020-04, 250 days: size at the earlier value | 0.0075 | 0.0075 | yes |
| B2 leg, B1, post-2020-04, 125 days: size at the amended value | 0.0080 | 0.0080 | yes |
| B2 leg, B1, post-2020-04, 125 days: size at the earlier value | 0.0006 | 0.0006 | yes |
| B2 leg, gbm_funding, full, 250 days: size at the amended value | 0.0959 | 0.0959 | yes |
| B2 leg, gbm_funding, full, 250 days: size at the earlier value | 0.0085 | 0.0085 | yes |
| B2 leg, gbm_funding, full, 125 days: size at the amended value | 0.0063 | 0.0063 | yes |
| B2 leg, gbm_funding, full, 125 days: size at the earlier value | 0.0008 | 0.0008 | yes |
| B2 leg, gbm_funding, without 2019-09-18, 250 days: size at the amended value | 0.0959 | 0.0959 | yes |
| B2 leg, gbm_funding, without 2019-09-18, 250 days: size at the earlier value | 0.0071 | 0.0071 | yes |
| B2 leg, gbm_funding, without 2019-09-18, 125 days: size at the amended value | 0.0060 | 0.0060 | yes |
| B2 leg, gbm_funding, without 2019-09-18, 125 days: size at the earlier value | 0.0005 | 0.0005 | yes |
| B2 leg, gbm_funding, post-2020-04, 250 days: size at the amended value | 0.0916 | 0.0916 | yes |
| B2 leg, gbm_funding, post-2020-04, 250 days: size at the earlier value | 0.0076 | 0.0076 | yes |
| B2 leg, gbm_funding, post-2020-04, 125 days: size at the amended value | 0.0057 | 0.0057 | yes |
| B2 leg, gbm_funding, post-2020-04, 125 days: size at the earlier value | 0.0004 | 0.0004 | yes |

The leg against B1 reproduces #913's calibration table to three decimals and #878's full-history values; the leg against B2 at the amended and earlier values reproduces #922's sizes exactly (same function, series and seed). All hold.

## 3. The size of each leg

Share of windows in which the leg passes when the candidate has no skill against the leg's benchmark (nominal: 4.8% at 250 days, 0.56% at 125). New values are the post-2020-04 values of section 1.

| leg | candidate | history | days | series days | new value | amended value | earlier value |
|---|---|---|---|---|---|---|---|
| against B1 | B2 | full | 250 | 2037 | 0.2% ± 0.1 | 4.8% ± 0.3 | 0.3% ± 0.1 |
| against B1 | B2 | full | 125 | 2037 | 0.0% ± 0.0 | 0.6% ± 0.1 | 0.1% ± 0.0 |
| against B1 | B2 | without 2019-09-18 | 250 | 2036 | 1.5% ± 0.2 | 12.2% ± 0.5 | 1.6% ± 0.2 |
| against B1 | B2 | without 2019-09-18 | 125 | 2036 | 0.0% ± 0.0 | 2.4% ± 0.2 | 0.5% ± 0.1 |
| against B1 | B2 | post-2020-04 | 250 | 1598 | 4.8% ± 0.3 | 16.8% ± 0.5 | 4.9% ± 0.3 |
| against B1 | B2 | post-2020-04 | 125 | 1598 | 0.6% ± 0.1 | 6.6% ± 0.3 | 2.6% ± 0.2 |
| against B1 | gbm_funding | full | 250 | 1868 | 0.0% ± 0.0 | 0.9% ± 0.1 | 0.0% ± 0.0 |
| against B1 | gbm_funding | full | 125 | 1868 | 0.0% ± 0.0 | 0.0% ± 0.0 | 0.0% ± 0.0 |
| against B1 | gbm_funding | without 2019-09-18 | 250 | 1867 | 0.0% ± 0.0 | 2.9% ± 0.2 | 0.0% ± 0.0 |
| against B1 | gbm_funding | without 2019-09-18 | 125 | 1867 | 0.0% ± 0.0 | 0.0% ± 0.0 | 0.0% ± 0.0 |
| against B1 | gbm_funding | post-2020-04 | 250 | 1429 | 0.1% ± 0.1 | 6.4% ± 0.3 | 0.2% ± 0.1 |
| against B1 | gbm_funding | post-2020-04 | 125 | 1429 | 0.0% ± 0.0 | 0.1% ± 0.0 | 0.0% ± 0.0 |
| against B2 | B1 | full | 250 | 2037 | 16.1% ± 0.5 | 24.6% ± 0.6 | 4.8% ± 0.3 |
| against B2 | B1 | full | 125 | 2037 | 2.6% ± 0.2 | 3.5% ± 0.3 | 0.6% ± 0.1 |
| against B2 | B1 | without 2019-09-18 | 250 | 2036 | 7.5% ± 0.4 | 13.6% ± 0.5 | 1.7% ± 0.2 |
| against B2 | B1 | without 2019-09-18 | 125 | 2036 | 1.0% ± 0.1 | 1.4% ± 0.2 | 0.2% ± 0.1 |
| against B2 | B1 | post-2020-04 | 250 | 1598 | 4.8% ± 0.3 | 9.9% ± 0.4 | 0.7% ± 0.1 |
| against B2 | B1 | post-2020-04 | 125 | 1598 | 0.6% ± 0.1 | 0.8% ± 0.1 | 0.1% ± 0.0 |
| against B2 | gbm_funding | full | 250 | 1868 | 4.9% ± 0.3 | 9.6% ± 0.4 | 0.9% ± 0.1 |
| against B2 | gbm_funding | full | 125 | 1868 | 0.4% ± 0.1 | 0.6% ± 0.1 | 0.1% ± 0.0 |
| against B2 | gbm_funding | without 2019-09-18 | 250 | 1867 | 4.7% ± 0.3 | 9.6% ± 0.4 | 0.7% ± 0.1 |
| against B2 | gbm_funding | without 2019-09-18 | 125 | 1867 | 0.4% ± 0.1 | 0.6% ± 0.1 | 0.1% ± 0.0 |
| against B2 | gbm_funding | post-2020-04 | 250 | 1429 | 4.5% ± 0.3 | 9.2% ± 0.4 | 0.8% ± 0.1 |
| against B2 | gbm_funding | post-2020-04 | 125 | 1429 | 0.4% ± 0.1 | 0.6% ± 0.1 | 0.0% ± 0.0 |

## 4. What the tables show

On post-2020-04 history at 250 days, with the new values (2.438 against B1, 1.701 against B2), the leg against B1 passes in 4.8% ± 0.3 of windows for the stand-in B2 and 0.1% ± 0.1 for `gbm_funding`; the leg against B2 passes in 4.8% ± 0.3 for the stand-in B1 and 4.5% ± 0.3 for `gbm_funding`. At 125 days the same cells are 0.6% ± 0.1, 0.0% ± 0.0, 0.6% ± 0.1 and 0.4% ± 0.1. A leg's size on its own calibration series (the stand-in candidate, post-2020-04 history) is its nominal level by construction; the rows for `gbm_funding` and for the other histories show how far it holds elsewhere. This page draws circular blocks (`window_t_statistics`, as the directive says) from the decision days from 2020-04-03, where #886 drew stationary-bootstrap windows. #913's post-2020-04 row cuts two decision days earlier, at 2020-04-01; the last rows of section 1 show that cut moves the leg against B1 from 2.438 / 4.727 to 2.427 / 4.808 (and reproduces #913's table). Which cut is used is Eleonora's.

Nothing here is a verdict for a hypothesis; the choice of values is Eleonora's (#913, ruling of 19 October 2026).
