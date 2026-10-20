# Critical values on contiguous post-2020 windows, event strata and a fixed-b statistic (#963, H1 step 3 and H6 step 1)

**Development data, not a verdict.** A report that changes nothing: `scoring_protocol.CRITICAL_VALUES` and `docs/decisions/scoring-protocol.md` are only read. No day after 2025-12-31 and no lockbox day is scored. Everything is declared in `metadata/contiguous_calibration_963.json` before any score and read from `docs/research/contiguous-calibration-963/result.json` by `scripts/contiguous_calibration_963.py report`.

## Questions for Eleonora (marked)

1. **Does the 250-day confirmation window stay?** The reading rules below are Lens C's, declared as stated; the design is hers.
2. **Should H6 be registered ahead of H5?** The event-strata table gives how many events a year each stratum holds and what the candidates do on them; whether H6 moves ahead of H5 is hers.
3. **Should the window lengthen** (the 500-day rows)? The same.

## Series

d = S(B1) - S(candidate), lead-averaged grid CRPS, 1429 decision days 2020-04-03 to 2025-12-23 (the days all four forecasts cover; from 2020-04-03). B1' (#960) replaces B1 once #960 has merged; it has not, so this declaration runs B1 only and the PR says so. Reproduction: mean S(B2) - S(`gbm_funding`) over the walk's 1868 days is 0.688215, and #922's record gives 0.688215 over 1868.

| candidate | mean d | rho(1) | rho(5) | Politis-White block |
|---|---|---|---|---|
| B2 | -0.573 | 0.75 | 0.28 | 63.8 |
| spread_mr_ctx | 0.161 | 0.56 | 0.05 | 12.0 |
| gbm_funding | 0.152 | 0.58 | -0.08 | 10.2 |

## 1. Critical values by generator

c is the 0.95 quantile of the window statistics: the bound `mean - c * se` covers the series' mean on 95% of the generator's windows. Size is the share of the generator's windows above the value in force (125 days: 3.419; 250 days: 2.426; 500 days has none and is read at the 250-day value). Non-overlapping is n / days, the windows the series holds without overlap; the windows of a persistent series overlap in information, so it is an upper count of independent ones.

| candidate | days | non-overlapping | c contiguous | c stationary-10 | c circular-10 | size contiguous | size stationary-10 | size circular-10 |
|---|---|---|---|---|---|---|---|---|
| B2 | 125 | 11.4 | 6.58 | 3.57 | 2.91 | 41.5% | 5.8% | 3.0% |
| B2 | 250 | 5.7 | 7.19 | 3.10 | 2.44 | 49.6% | 9.6% | 5.1% |
| B2 | 500 | 2.9 | 6.52 | 2.74 | 2.20 | 55.8% | 7.1% | 3.7% |
| spread_mr_ctx | 125 | 11.4 | 1.99 | 1.46 | 1.36 | 0.0% | 0.0% | 0.0% |
| spread_mr_ctx | 250 | 5.7 | 1.92 | 1.49 | 1.38 | 0.8% | 0.3% | 0.1% |
| spread_mr_ctx | 500 | 2.9 | 2.12 | 1.56 | 1.42 | 3.4% | 0.3% | 0.2% |
| gbm_funding | 125 | 11.4 | 2.16 | 1.53 | 1.45 | 1.2% | 0.0% | 0.0% |
| gbm_funding | 250 | 5.7 | 2.07 | 1.57 | 1.45 | 1.4% | 0.2% | 0.2% |
| gbm_funding | 500 | 2.9 | 1.60 | 1.57 | 1.49 | 0.0% | 0.4% | 0.2% |

### Reading rules (declared)

- `B2`: the contiguous-window c at 250 days is 7.19, above 4.0: no 250-day pooled test can confirm anything short of a 20-30% skill.
- `spread_mr_ctx`: the contiguous-window c at 250 days is 1.92, below 3.0: the 250-day design survives.
- `gbm_funding`: the contiguous-window c at 250 days is 2.07, below 3.0: the 250-day design survives.

## 2. Event strata (H6 step 1)

The H5 metric (grid CRPS, mean over leads 1-5 of the cells that target a day) on targets that are risk dates, d = S(benchmark) - S(candidate), paired by `scoring_protocol.paired_tests` (stationary bootstrap, mean block 3 events, HAC lag 3, one-sided 95% bounds [lower, upper] of mean d). The target days are 1425 post-2020 days with all five leads. Month-end is the month's last two business days and holds the turn of the month; #959's turn label has not merged, so the current one is used. The ACF is of d between consecutive events of the stratum, in date order.

| stratum | events | per year |
|---|---|---|
| month_end | 114 | 20.4 |
| quarter_end | 22 | 4.2 (thin: not tested) |
| tax_date | 71 | 12.5 |
| coupon_settlement | 186 | 32.8 |

| stratum | pair | events | mean d | [lower, upper] | rho(1) | rho(2) | rho(3) |
|---|---|---|---|---|---|---|---|
| month_end | B2 vs B1 | 114 | -0.646 | [-1.722, -0.018] | 0.60 | 0.29 | 0.22 |
| month_end | gbm_funding vs B1 | 114 | +0.086 | [-0.028, +0.193] | 0.01 | -0.14 | 0.04 |
| month_end | gbm_funding vs B2 | 114 | +0.733 | [+0.149, +1.718] | 0.64 | 0.37 | 0.25 |
| month_end | spread_mr_ctx vs B1 | 114 | +0.077 | [-0.197, +0.401] | 0.42 | 0.21 | 0.35 |
| month_end | spread_mr_ctx vs B2 | 114 | +0.723 | [+0.159, +2.129] | 0.64 | 0.35 | 0.19 |
| tax_date | B2 vs B1 | 71 | -2.112 | [-3.436, -1.220] | 0.62 | 0.32 | 0.14 |
| tax_date | gbm_funding vs B1 | 71 | +0.002 | [-0.518, +0.266] | 0.53 | 0.15 | 0.03 |
| tax_date | gbm_funding vs B2 | 71 | +2.114 | [+1.224, +3.826] | 0.70 | 0.46 | 0.25 |
| tax_date | spread_mr_ctx vs B1 | 71 | -0.090 | [-0.297, +0.165] | 0.26 | 0.31 | 0.38 |
| tax_date | spread_mr_ctx vs B2 | 71 | +2.021 | [+1.191, +3.301] | 0.52 | 0.28 | 0.14 |
| coupon_settlement | B2 vs B1 | 186 | -0.942 | [-1.586, -0.430] | 0.51 | 0.28 | 0.36 |
| coupon_settlement | gbm_funding vs B1 | 186 | -0.079 | [-0.212, +0.015] | 0.29 | -0.01 | -0.02 |
| coupon_settlement | gbm_funding vs B2 | 186 | +0.863 | [+0.373, +1.469] | 0.51 | 0.32 | 0.37 |
| coupon_settlement | spread_mr_ctx vs B1 | 186 | +0.154 | [-0.003, +0.355] | 0.41 | 0.31 | 0.28 |
| coupon_settlement | spread_mr_ctx vs B2 | 186 | +1.096 | [+0.599, +1.888] | 0.57 | 0.34 | 0.37 |

## 3. A fixed-b statistic

The mean of d over a window of 500 days over its Bartlett standard error of bandwidth b * T, b = 0.1 (M = 50), against the fixed-b critical value 1.826 (the 0.95 quantile on independent noise), beside the Newey-West (lag 10) statistic against the normal 1.645. The last window is the series' last 500 days. Size is the share of the series' contiguous windows of that length, centred at the series' mean, above the value.

| candidate | mean d, last 2 years | NW(10) t | fixed-b t | size NW(10) vs normal | size fixed-b |
|---|---|---|---|---|---|
| B2 | -0.095 | -0.38 | -0.25 | 61.9% | 57.6% |
| spread_mr_ctx | +0.520 | 4.13 | 3.53 | 11.3% | 7.8% |
| gbm_funding | +0.376 | 3.66 | 3.21 | 3.9% | 3.7% |

## Limits

The proxy and the series differ (Lens C's proxy was B1/B2; these are `gbm_funding`'s, `spread_mr_ctx`'s and B2's own d). The series are development data seen before the declaration. Contiguous windows overlap heavily, so a quantile of them rests on a handful of independent stretches; the non-overlapping count says how few. Nothing here is registered or changed.
