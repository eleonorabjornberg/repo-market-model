# H6 registration design and power (#1131, H6 step 2)

**Hypothesis and step:** H6 (the spread on known risk dates is forecastable), step 2, the registration design, ahead of H5 (Eleonora's ruling of 22 October 2026, option c on #1024). **A design and power page only: no registration is made** (registering is her own action) and every item under *Questions* is hers. **Development data, not a verdict** (scoring protocol v1, #640). The declaration is `metadata/h6_design_1131.json`, committed before any score; the script is `scripts/h6_design_1131.py`; every figure below is read from `docs/research/h6-design-1131/result.json`. Basis: Lens C of the five-lens review (#958, avenue B) and #963.

The ruling's reason: post-2020 autocorrelation leaves H5's 250-day window with a handful of independent windows (#963). H6 moves the unit of evidence from a day to an announced event: the strata below hold target days that the calendar names in advance, so a confirmation window of calendar years holds tens to a few hundred events.

## 1. The strata (all read from the calendar at the target day)

Target days: 1425 from 2020-04-13 to 2025-12-24 (5.7 years), the days all four forecasts cover with all five leads. A day may be in several strata; the union is the days in at least one. A stratum below 30 events is counted and not tested on its own.

| stratum | rule | events | per year | by calendar year | tested alone |
|---|---|---|---|---|---|
| coupon settlement | `treasury_settlement_coupons > 0` | 186 | 32.8 | 2020: 26, 2021: 35, 2022: 33, 2023: 31, 2024: 32, 2025: 29 | yes |
| large bill settlement | bill settlement at or above the 75th percentile of the trailing 252 rows' positive settlements | 245 | 43.6 | 2020: 35, 2021: 9, 2022: 21, 2023: 86, 2024: 53, 2025: 41 | yes |
| month-end turn | last business day of a month that is not a quarter's last, and the first of the next (#959) | 92 | 16.5 | 2020: 12, 2021: 16, 2022: 16, 2023: 16, 2024: 16, 2025: 16 | yes |
| quarter-end turn (Mar, Jun, Sep) | last business day of Mar, Jun, Sep and the first business day after (#959) | 34 | 6.5 | 2020: 4, 2021: 6, 2022: 6, 2023: 6, 2024: 6, 2025: 6 | yes |
| year-end | last business day of December and the first of January (#959) | 10 | 2.5 | 2020: 1, 2021: 2, 2022: 2, 2023: 2, 2024: 2, 2025: 1 | no (thin) |
| quarter-end and year-end | the two rows above together | 44 | 8.4 | 2020: 5, 2021: 8, 2022: 8, 2023: 8, 2024: 8, 2025: 7 | yes |
| tax date | the `tax_date` column, on a day that is no turn day | 71 | 12.5 | 2020: 12, 2021: 12, 2022: 12, 2023: 12, 2024: 12, 2025: 11 | yes |
| FOMC meeting day | both days of a meeting public at the longest lead's decision instant | 92 | 16.4 | 2020: 12, 2021: 16, 2022: 16, 2023: 16, 2024: 16, 2025: 16 | yes |
| IORB-change window (two days after a meeting) | first and second business day after a meeting's last day | 92 | 16.4 | 2020: 12, 2021: 16, 2022: 16, 2023: 16, 2024: 16, 2025: 16 | yes |
| union of the strata | any of the above | 589 | 103.8 | 2020: 81, 2021: 78, 2022: 91, 2023: 133, 2024: 106, 2025: 100 | yes |
| union without the bill stratum | any of the above but the large bill settlement | 413 | 72.8 | 2020: 55, 2021: 72, 2022: 75, 2023: 73, 2024: 69, 2025: 69 | yes |

The IORB-change window is the scheduled calendar's, because a change is announced at the meeting and so cannot define a stratum in advance. Ex post, 18 of the 18 IORB changes that took effect from 2020-04-03 to 2025-12-31 fell in it.

Days each benchmark covers (events with a forecast at all five leads). The risk-date calendar benchmark (#693) exists at a lead only where the target is a quarter-end, month-end, tax date or announced coupon settlement; the others cover every event.

| stratum | B1 | B1' | B2 | risk-date calendar (#693) |
|---|---|---|---|---|
| coupon settlement | 186 | 186 | 186 | 98 |
| large bill settlement | 245 | 245 | 245 | 37 |
| month-end turn | 92 | 92 | 92 | 46 |
| quarter-end turn (Mar, Jun, Sep) | 34 | 34 | 34 | 17 |
| year-end | 10 | 10 | 10 | 5 |
| quarter-end and year-end | 44 | 44 | 44 | 22 |
| tax date | 71 | 71 | 71 | 71 |
| FOMC meeting day | 92 | 92 | 92 | 26 |
| IORB-change window (two days after a meeting) | 92 | 92 | 92 | 30 |
| union of the strata | 589 | 589 | 589 | 167 |
| union without the bill stratum | 413 | 413 | 413 | 159 |

## 2. The candidate, the benchmarks, the score

- **Candidate.** H6 registers one primary candidate. It is not chosen here: H5's best (`gbm_funding` or `spread_mr_ctx`, step 5 of H5) is the natural one, and a risk-date-specialised variant is H6's own step 2. The power below uses `spread_mr_ctx` (#761) as a stand-in for the shape of a candidate's d series; `gbm_funding`'s walks are a long run and are not repeated here.
- **Benchmarks.** B1 and B1' are both reported (B1' is #960's calendar-aware persistence; B1 stays the protocol's benchmark), B2, and the risk-date calendar benchmark (#693): the trailing year's spreads of the target's risk type.
- **Score.** The H5 metric: grid CRPS averaged over leads 1 to 5, on the target day, primary; the upper-tail twCRPS (weight 1{z > 0 bp}) key secondary. Paired, positive favours the candidate; the interval is the studentized stationary bootstrap's (block 3 events, HAC lag 3, 10000 draws, seed 1131), two-sided 90%, so the lower end is the one-sided 95% lower bound.

## 3. Development skill on the strata, grid CRPS (paired, with the interval)

Skill of `spread_mr_ctx` over each benchmark, with ρ(1)/ρ(2)/ρ(3) of d between consecutive events. A stratum is the day-type split; the union is split by regime in the next table. Development data, not a verdict.

| stratum | benchmark | events | skill [90%] | ACF of d |
|---|---|---|---|---|
| coupon settlement | B1 | 186 | +8.6% [+0.8%, +15.5%] | +0.41 / +0.31 / +0.28 |
| coupon settlement | B1' | 186 | +4.2% [-4.2%, +11.5%] | +0.37 / +0.20 / +0.18 |
| coupon settlement | B2 | 186 | +40.1% [+27.1%, +50.2%] | +0.57 / +0.34 / +0.37 |
| coupon settlement | risk-date calendar (#693) | 98 | +34.3% [+14.5%, +48.9%] | +0.31 / +0.33 / +0.08 |
| large bill settlement | B1 | 245 | +11.6% [+3.7%, +19.8%] | +0.46 / +0.14 / -0.12 |
| large bill settlement | B1' | 245 | +4.3% [-3.6%, +11.2%] | +0.38 / +0.07 / -0.12 |
| large bill settlement | B2 | 245 | +38.7% [+26.4%, +50.7%] | +0.57 / +0.40 / +0.49 |
| large bill settlement | risk-date calendar (#693) | 37 | +44.4% [+21.3%, +68.4%] | +0.25 / +0.05 / +0.01 |
| month-end turn | B1 | 92 | +12.0% [+1.4%, +20.6%] | +0.33 / +0.20 / +0.11 |
| month-end turn | B1' | 92 | +5.6% [-4.7%, +14.1%] | +0.22 / +0.11 / -0.00 |
| month-end turn | B2 | 92 | +39.4% [+22.1%, +54.8%] | +0.67 / +0.44 / +0.23 |
| month-end turn | risk-date calendar (#693) | 46 | +31.0% [+11.0%, +48.5%] | +0.35 / -0.07 / -0.14 |
| quarter-end turn (Mar, Jun, Sep) | B1 | 34 | +5.7% [-1.3%, +11.9%] | +0.17 / +0.00 / -0.10 |
| quarter-end turn (Mar, Jun, Sep) | B1' | 34 | +4.4% [-3.7%, +11.0%] | +0.23 / +0.08 / -0.08 |
| quarter-end turn (Mar, Jun, Sep) | B2 | 34 | +23.6% [-41.0%, +50.2%] | +0.05 / +0.46 / -0.33 |
| quarter-end turn (Mar, Jun, Sep) | risk-date calendar (#693) | 17 | thin |  |
| quarter-end and year-end | B1 | 44 | +8.1% [+2.1%, +14.6%] | +0.16 / +0.11 / -0.04 |
| quarter-end and year-end | B1' | 44 | +7.7% [+0.4%, +15.8%] | +0.20 / +0.18 / -0.02 |
| quarter-end and year-end | B2 | 44 | +26.0% [-11.0%, +45.0%] | -0.01 / +0.40 / -0.38 |
| quarter-end and year-end | risk-date calendar (#693) | 22 | thin |  |
| tax date | B1 | 71 | -7.3% [-29.0%, +14.7%] | +0.26 / +0.31 / +0.38 |
| tax date | B1' | 71 | -15.6% [-34.4%, +4.6%] | -0.04 / +0.13 / +0.37 |
| tax date | B2 | 71 | +60.3% [+47.3%, +71.3%] | +0.52 / +0.28 / +0.14 |
| tax date | risk-date calendar (#693) | 71 | +60.3% [+47.3%, +71.3%] | +0.52 / +0.28 / +0.14 |
| FOMC meeting day | B1 | 92 | -0.8% [-14.3%, +13.2%] | +0.27 / -0.09 / -0.06 |
| FOMC meeting day | B1' | 92 | -8.8% [-22.0%, +4.4%] | +0.26 / -0.08 / -0.16 |
| FOMC meeting day | B2 | 92 | +38.2% [+18.6%, +52.8%] | +0.47 / +0.07 / +0.07 |
| FOMC meeting day | risk-date calendar (#693) | 26 | thin |  |
| IORB-change window (two days after a meeting) | B1 | 92 | -10.5% [-29.4%, +5.1%] | +0.49 / +0.21 / +0.04 |
| IORB-change window (two days after a meeting) | B1' | 92 | -24.8% [-44.3%, -10.6%] | +0.45 / +0.15 / +0.01 |
| IORB-change window (two days after a meeting) | B2 | 92 | +39.8% [+10.1%, +56.0%] | +0.56 / +0.18 / +0.11 |
| IORB-change window (two days after a meeting) | risk-date calendar (#693) | 30 | +48.2% [+31.1%, +57.6%] | +0.40 / -0.14 / -0.16 |
| union of the strata | B1 | 589 | +7.7% [+2.0%, +13.6%] | +0.50 / +0.27 / +0.15 |
| union of the strata | B1' | 589 | +1.2% [-4.7%, +7.0%] | +0.47 / +0.20 / +0.08 |
| union of the strata | B2 | 589 | +40.4% [+31.7%, +48.2%] | +0.69 / +0.52 / +0.44 |
| union of the strata | risk-date calendar (#693) | 167 | +42.4% [+27.2%, +54.7%] | +0.60 / +0.34 / +0.23 |
| union without the bill stratum | B1 | 413 | +4.0% [-2.9%, +10.4%] | +0.47 / +0.29 / +0.13 |
| union without the bill stratum | B1' | 413 | -1.6% [-8.8%, +5.2%] | +0.45 / +0.22 / -0.01 |
| union without the bill stratum | B2 | 413 | +41.3% [+30.8%, +50.5%] | +0.74 / +0.56 / +0.46 |
| union without the bill stratum | risk-date calendar (#693) | 159 | +42.8% [+27.1%, +55.4%] | +0.60 / +0.35 / +0.24 |

Union by regime of the target day:

| regime | events | B1 | B1' | B2 | risk-date calendar (#693) |
|---|---|---|---|---|---|
| 2020 | 81 | -17.5% [-29.1%, -8.2%] | -23.4% [-36.7%, -11.5%] | +52.9% [+30.9%, +73.3%] | thin |
| 2021-23 | 302 | -5.4% [-14.8%, +1.3%] | -10.2% [-18.7%, -3.5%] | +49.5% [+40.6%, +57.5%] | +54.5% [+42.4%, +63.6%] |
| 2024 | 106 | +19.4% [+12.3%, +27.8%] | +11.9% [+3.6%, +18.9%] | +11.5% [-5.3%, +22.8%] | thin |
| 2025-26 | 100 | +14.6% [+3.1%, +24.9%] | +8.1% [-3.9%, +18.2%] | +38.4% [+20.0%, +51.6%] | thin |

## 4. Power on contiguous windows of events (#963's method)

For a stratum's d series, every window of N consecutive events (none wrapping) gives a statistic: its mean over its Newey-West standard error at lag 3, relative to the series' mean. c is the 0.95 quantile of those statistics: the value at which the bound covers 95% of windows. *Size* is the share of null windows above the normal 1.645. *Power* at skill s is the share of windows that exceed c once the mean is moved to s times the benchmark's mean score on the stratum. N is the stratum's events in the window's years. *Independent* is n / N, an upper count of windows without overlap: a quantile of contiguous windows rests on that few stretches.

### Grid CRPS (primary)

**Against B1**

| stratum | window | N events | windows | independent | c | size | power at 3.0% | power at 5.0% | power at 10.0% | power at 15.0% | power at 20.0% |
|---|---|---|---|---|---|---|---|---|---|---|---|
| coupon settlement | 1 y | 33 | 154 | 5.6 | 3.39 | 26.0% | 14.3% | 20.8% | 42.2% | 50.0% | 67.5% |
| coupon settlement | 2 y | 66 | 121 | 2.8 | 3.28 | 19.0% | 7.4% | 11.6% | 36.4% | 61.2% | 69.4% |
| coupon settlement | 3 y | 98 | 89 | 1.9 | 2.39 | 14.6% | 14.6% | 23.6% | 49.4% | 64.0% | 69.7% |
| large bill settlement | 1 y | 44 | 202 | 5.6 | 1.00 | 0.0% | 10.9% | 11.9% | 60.4% | 79.2% | 83.7% |
| large bill settlement | 2 y | 87 | 159 | 2.8 | 0.94 | 0.0% | 15.7% | 23.3% | 76.1% | 88.7% | 100.0% |
| large bill settlement | 3 y | 131 | 115 | 1.9 | 0.69 | 0.0% | 23.5% | 33.9% | 79.1% | 100.0% | 100.0% |
| month-end turn | 1 y | 16 | 77 | 5.8 | 1.71 | 9.1% | 10.4% | 24.7% | 59.7% | 68.8% | 74.0% |
| month-end turn | 2 y | 33 | 60 | 2.8 | 1.56 | 3.3% | 25.0% | 48.3% | 63.3% | 73.3% | 73.3% |
| month-end turn | 3 y | 49 | 44 | 1.9 | 1.33 | 2.3% | 36.4% | 50.0% | 63.6% | 65.9% | 84.1% |
| quarter-end turn (Mar, Jun, Sep) | 1 y | 6 | 29 | 5.7 | 4.03 | 20.7% | 10.3% | 10.3% | 31.0% | 41.4% | 51.7% |
| quarter-end turn (Mar, Jun, Sep) | 2 y | 13 | 22 | 2.6 | 1.34 | 0.0% | 50.0% | 59.1% | 72.7% | 90.9% | 100.0% |
| quarter-end turn (Mar, Jun, Sep) | 3 y | 19 | 16 | | too few windows | |  |  |  |  |  |
| quarter-end and year-end | 1 y | 8 | 37 | 5.5 | 2.50 | 16.2% | 13.5% | 16.2% | 48.6% | 59.5% | 67.6% |
| quarter-end and year-end | 2 y | 17 | 28 | 2.6 | 1.38 | 0.0% | 28.6% | 50.0% | 67.9% | 85.7% | 96.4% |
| quarter-end and year-end | 3 y | 25 | 20 | 1.8 | 1.36 | 0.0% | 35.0% | 50.0% | 75.0% | 100.0% | 100.0% |
| tax date | 1 y | 13 | 59 | 5.5 | 3.20 | 40.7% | 20.3% | 25.4% | 30.5% | 37.3% | 37.3% |
| tax date | 2 y | 25 | 47 | 2.8 | 2.93 | 36.2% | 14.9% | 21.3% | 36.2% | 38.3% | 38.3% |
| tax date | 3 y | 38 | 34 | 1.9 | 2.94 | 14.7% | 11.8% | 11.8% | 14.7% | 17.6% | 17.6% |
| FOMC meeting day | 1 y | 16 | 77 | 5.8 | 2.92 | 27.3% | 18.2% | 29.9% | 32.5% | 33.8% | 40.3% |
| FOMC meeting day | 2 y | 33 | 60 | 2.8 | 2.87 | 15.0% | 13.3% | 13.3% | 31.7% | 50.0% | 51.7% |
| FOMC meeting day | 3 y | 49 | 44 | 1.9 | 1.81 | 9.1% | 18.2% | 31.8% | 52.3% | 68.2% | 84.1% |
| IORB-change window (two days after a meeting) | 1 y | 16 | 77 | 5.8 | 9.51 | 31.2% | 11.7% | 11.7% | 16.9% | 26.0% | 27.3% |
| IORB-change window (two days after a meeting) | 2 y | 33 | 60 | 2.8 | 5.95 | 15.0% | 6.7% | 11.7% | 11.7% | 11.7% | 15.0% |
| IORB-change window (two days after a meeting) | 3 y | 49 | 44 | 1.9 | 2.09 | 13.6% | 15.9% | 22.7% | 36.4% | 54.5% | 75.0% |
| union of the strata | 1 y | 104 | 486 | 5.7 | 2.23 | 15.2% | 10.3% | 14.8% | 53.7% | 72.2% | 78.4% |
| union of the strata | 2 y | 208 | 382 | 2.8 | 2.32 | 19.9% | 15.4% | 29.3% | 64.7% | 76.2% | 80.1% |
| union of the strata | 3 y | 311 | 279 | 1.9 | 2.03 | 11.1% | 20.8% | 37.6% | 63.8% | 77.8% | 100.0% |
| union without the bill stratum | 1 y | 73 | 341 | 5.7 | 3.33 | 25.2% | 13.2% | 25.8% | 33.4% | 34.3% | 63.0% |
| union without the bill stratum | 2 y | 146 | 268 | 2.8 | 2.69 | 26.5% | 23.1% | 28.4% | 62.7% | 73.5% | 78.0% |
| union without the bill stratum | 3 y | 218 | 196 | 1.9 | 2.39 | 22.4% | 26.5% | 37.2% | 64.8% | 73.5% | 87.2% |
| all target days (H5's unit, lag 10) | 1 y | 250 | 1176 | 5.7 | 1.91 | 13.0% | 12.8% | 19.9% | 36.5% | 53.2% | 71.0% |
| all target days (H5's unit, lag 10) | 2 y | 500 | 926 | 2.9 | 2.12 | 11.1% | 10.9% | 12.6% | 39.3% | 61.2% | 78.3% |
| all target days (H5's unit, lag 10) | 3 y | 750 | 676 | 1.9 | 1.67 | 5.5% | 15.1% | 17.6% | 46.2% | 69.7% | 100.0% |

**Against B1'**

| stratum | window | N events | windows | independent | c | size | power at 3.0% | power at 5.0% | power at 10.0% | power at 15.0% | power at 20.0% |
|---|---|---|---|---|---|---|---|---|---|---|---|
| coupon settlement | 1 y | 33 | 154 | 5.6 | 2.81 | 24.0% | 14.9% | 20.1% | 42.2% | 69.5% | 76.0% |
| coupon settlement | 2 y | 66 | 121 | 2.8 | 2.86 | 19.8% | 9.1% | 19.0% | 57.9% | 69.4% | 73.6% |
| coupon settlement | 3 y | 98 | 89 | 1.9 | 2.12 | 13.5% | 19.1% | 40.4% | 59.6% | 66.3% | 84.3% |
| large bill settlement | 1 y | 44 | 202 | 5.6 | 1.13 | 0.0% | 24.8% | 30.2% | 66.3% | 73.8% | 88.1% |
| large bill settlement | 2 y | 87 | 159 | 2.8 | 1.35 | 0.6% | 13.8% | 16.4% | 76.1% | 98.7% | 100.0% |
| large bill settlement | 3 y | 131 | 115 | 1.9 | 0.83 | 0.0% | 29.6% | 62.6% | 86.1% | 100.0% | 100.0% |
| month-end turn | 1 y | 16 | 77 | 5.8 | 1.90 | 7.8% | 13.0% | 19.5% | 51.9% | 54.5% | 58.4% |
| month-end turn | 2 y | 33 | 60 | 2.8 | 1.31 | 0.0% | 31.7% | 48.3% | 68.3% | 75.0% | 88.3% |
| month-end turn | 3 y | 49 | 44 | 1.9 | 1.23 | 0.0% | 27.3% | 50.0% | 65.9% | 86.4% | 100.0% |
| quarter-end turn (Mar, Jun, Sep) | 1 y | 6 | 29 | 5.7 | 4.13 | 17.2% | 6.9% | 10.3% | 20.7% | 34.5% | 48.3% |
| quarter-end turn (Mar, Jun, Sep) | 2 y | 13 | 22 | 2.6 | 1.40 | 0.0% | 31.8% | 54.5% | 68.2% | 86.4% | 100.0% |
| quarter-end turn (Mar, Jun, Sep) | 3 y | 19 | 16 | | too few windows | |  |  |  |  |  |
| quarter-end and year-end | 1 y | 8 | 37 | 5.5 | 2.97 | 18.9% | 8.1% | 10.8% | 35.1% | 45.9% | 64.9% |
| quarter-end and year-end | 2 y | 17 | 28 | 2.6 | 1.48 | 0.0% | 25.0% | 28.6% | 67.9% | 82.1% | 96.4% |
| quarter-end and year-end | 3 y | 25 | 20 | 1.8 | 1.29 | 0.0% | 35.0% | 45.0% | 65.0% | 90.0% | 100.0% |
| tax date | 1 y | 13 | 59 | 5.5 | 3.74 | 35.6% | 10.2% | 11.9% | 18.6% | 18.6% | 22.0% |
| tax date | 2 y | 25 | 47 | 2.8 | 2.39 | 34.0% | 27.7% | 29.8% | 38.3% | 38.3% | 40.4% |
| tax date | 3 y | 38 | 34 | 1.9 | 2.71 | 14.7% | 8.8% | 11.8% | 14.7% | 17.6% | 23.5% |
| FOMC meeting day | 1 y | 16 | 77 | 5.8 | 4.33 | 31.2% | 14.3% | 19.5% | 27.3% | 29.9% | 37.7% |
| FOMC meeting day | 2 y | 33 | 60 | 2.8 | 4.45 | 35.0% | 11.7% | 11.7% | 15.0% | 41.7% | 50.0% |
| FOMC meeting day | 3 y | 49 | 44 | 1.9 | 2.89 | 29.5% | 22.7% | 31.8% | 36.4% | 36.4% | 54.5% |
| IORB-change window (two days after a meeting) | 1 y | 16 | 77 | 5.8 | 9.62 | 33.8% | 9.1% | 11.7% | 16.9% | 24.7% | 24.7% |
| IORB-change window (two days after a meeting) | 2 y | 33 | 60 | 2.8 | 3.71 | 48.3% | 21.7% | 33.3% | 43.3% | 50.0% | 50.0% |
| IORB-change window (two days after a meeting) | 3 y | 49 | 44 | 1.9 | 4.35 | 36.4% | 11.4% | 18.2% | 29.5% | 31.8% | 45.5% |
| union of the strata | 1 y | 104 | 486 | 5.7 | 2.07 | 9.9% | 13.6% | 33.3% | 54.9% | 67.5% | 80.7% |
| union of the strata | 2 y | 208 | 382 | 2.8 | 1.92 | 11.5% | 26.2% | 52.6% | 76.2% | 81.2% | 92.9% |
| union of the strata | 3 y | 311 | 279 | 1.9 | 1.64 | 4.7% | 42.3% | 60.9% | 74.2% | 100.0% | 100.0% |
| union without the bill stratum | 1 y | 73 | 341 | 5.7 | 2.70 | 25.8% | 24.3% | 31.1% | 48.4% | 59.2% | 62.8% |
| union without the bill stratum | 2 y | 146 | 268 | 2.8 | 2.81 | 19.0% | 15.3% | 37.3% | 53.7% | 77.2% | 82.5% |
| union without the bill stratum | 3 y | 218 | 196 | 1.9 | 2.16 | 20.9% | 33.2% | 52.0% | 71.4% | 87.2% | 100.0% |
| all target days (H5's unit, lag 10) | 1 y | 250 | 1176 | 5.7 | 1.63 | 4.8% | 15.6% | 24.7% | 51.6% | 76.2% | 83.6% |
| all target days (H5's unit, lag 10) | 2 y | 500 | 926 | 2.9 | 1.82 | 9.4% | 16.2% | 28.9% | 60.9% | 78.8% | 100.0% |
| all target days (H5's unit, lag 10) | 3 y | 750 | 676 | 1.9 | 1.64 | 5.0% | 16.9% | 26.8% | 64.6% | 94.5% | 100.0% |

**Against B2**

| stratum | window | N events | windows | independent | c | size | power at 3.0% | power at 5.0% | power at 10.0% | power at 15.0% | power at 20.0% |
|---|---|---|---|---|---|---|---|---|---|---|---|
| coupon settlement | 1 y | 33 | 154 | 5.6 | 1.11 | 0.0% | 7.1% | 7.8% | 10.4% | 13.6% | 33.1% |
| coupon settlement | 2 y | 66 | 121 | 2.8 | 0.29 | 0.0% | 10.7% | 17.4% | 31.4% | 52.1% | 88.4% |
| coupon settlement | 3 y | 98 | 89 | 1.9 | -0.25 | 0.0% | 15.7% | 24.7% | 51.7% | 87.6% | 95.5% |
| large bill settlement | 1 y | 44 | 202 | 5.6 | 1.04 | 1.5% | 5.9% | 5.9% | 7.4% | 9.4% | 9.9% |
| large bill settlement | 2 y | 87 | 159 | 2.8 | 0.20 | 0.0% | 6.3% | 6.9% | 9.4% | 12.6% | 15.1% |
| large bill settlement | 3 y | 131 | 115 | 1.9 | -0.46 | 0.0% | 7.0% | 8.7% | 13.0% | 16.5% | 20.9% |
| month-end turn | 1 y | 16 | 77 | 5.8 | 0.44 | 0.0% | 9.1% | 11.7% | 15.6% | 18.2% | 29.9% |
| month-end turn | 2 y | 33 | 60 | 2.8 | -0.35 | 0.0% | 8.3% | 8.3% | 16.7% | 31.7% | 63.3% |
| month-end turn | 3 y | 49 | 44 | 1.9 | -0.24 | 0.0% | 6.8% | 6.8% | 6.8% | 25.0% | 56.8% |
| quarter-end turn (Mar, Jun, Sep) | 1 y | 6 | 29 | 5.7 | 3.30 | 27.6% | 6.9% | 10.3% | 10.3% | 13.8% | 24.1% |
| quarter-end turn (Mar, Jun, Sep) | 2 y | 13 | 22 | 2.6 | 2.18 | 22.7% | 13.6% | 22.7% | 31.8% | 45.5% | 72.7% |
| quarter-end turn (Mar, Jun, Sep) | 3 y | 19 | 16 | | too few windows | |  |  |  |  |  |
| quarter-end and year-end | 1 y | 8 | 37 | 5.5 | 3.09 | 13.5% | 8.1% | 8.1% | 8.1% | 24.3% | 27.0% |
| quarter-end and year-end | 2 y | 17 | 28 | 2.6 | 1.82 | 25.0% | 35.7% | 42.9% | 57.1% | 75.0% | 82.1% |
| quarter-end and year-end | 3 y | 25 | 20 | 1.8 | 1.70 | 15.0% | 30.0% | 55.0% | 80.0% | 80.0% | 80.0% |
| tax date | 1 y | 13 | 59 | 5.5 | 0.54 | 0.0% | 10.2% | 15.3% | 28.8% | 42.4% | 47.5% |
| tax date | 2 y | 25 | 47 | 2.8 | 0.42 | 0.0% | 10.6% | 14.9% | 34.0% | 36.2% | 40.4% |
| tax date | 3 y | 38 | 34 | 1.9 | 0.51 | 0.0% | 8.8% | 8.8% | 11.8% | 20.6% | 38.2% |
| FOMC meeting day | 1 y | 16 | 77 | 5.8 | 1.30 | 2.6% | 7.8% | 9.1% | 14.3% | 19.5% | 20.8% |
| FOMC meeting day | 2 y | 33 | 60 | 2.8 | 0.73 | 0.0% | 18.3% | 20.0% | 30.0% | 33.3% | 35.0% |
| FOMC meeting day | 3 y | 49 | 44 | 1.9 | 0.10 | 0.0% | 15.9% | 29.5% | 38.6% | 43.2% | 52.3% |
| IORB-change window (two days after a meeting) | 1 y | 16 | 77 | 5.8 | 1.05 | 0.0% | 13.0% | 15.6% | 22.1% | 36.4% | 44.2% |
| IORB-change window (two days after a meeting) | 2 y | 33 | 60 | 2.8 | 1.26 | 0.0% | 10.0% | 13.3% | 20.0% | 28.3% | 40.0% |
| IORB-change window (two days after a meeting) | 3 y | 49 | 44 | 1.9 | 0.45 | 0.0% | 20.5% | 38.6% | 43.2% | 50.0% | 56.8% |
| union of the strata | 1 y | 104 | 486 | 5.7 | 1.16 | 0.6% | 8.6% | 14.6% | 24.5% | 26.1% | 28.8% |
| union of the strata | 2 y | 208 | 382 | 2.8 | 0.13 | 0.0% | 14.1% | 17.8% | 32.7% | 35.9% | 40.1% |
| union of the strata | 3 y | 311 | 279 | 1.9 | -0.78 | 0.0% | 8.6% | 11.5% | 42.3% | 47.0% | 55.2% |
| union without the bill stratum | 1 y | 73 | 341 | 5.7 | 1.70 | 5.6% | 6.7% | 7.9% | 12.0% | 15.0% | 18.8% |
| union without the bill stratum | 2 y | 146 | 268 | 2.8 | 0.58 | 0.0% | 10.4% | 16.4% | 30.2% | 37.3% | 54.5% |
| union without the bill stratum | 3 y | 218 | 196 | 1.9 | -0.41 | 0.0% | 23.5% | 41.8% | 47.4% | 53.1% | 80.1% |
| all target days (H5's unit, lag 10) | 1 y | 250 | 1176 | 5.7 | 3.56 | 15.9% | 6.1% | 6.7% | 8.9% | 10.8% | 13.8% |
| all target days (H5's unit, lag 10) | 2 y | 500 | 926 | 2.9 | 1.56 | 3.1% | 11.9% | 24.9% | 29.3% | 32.0% | 34.6% |
| all target days (H5's unit, lag 10) | 3 y | 750 | 676 | 1.9 | 0.23 | 0.0% | 34.2% | 35.7% | 39.3% | 44.8% | 54.3% |

**Against risk-date calendar (#693)**

| stratum | window | N events | windows | independent | c | size | power at 3.0% | power at 5.0% | power at 10.0% | power at 15.0% | power at 20.0% |
|---|---|---|---|---|---|---|---|---|---|---|---|
| coupon settlement | 1 y | 17 | 82 | 5.8 | 1.24 | 2.4% | 8.5% | 13.4% | 18.3% | 31.7% | 45.1% |
| coupon settlement | 2 y | 35 | 64 | 2.8 | 1.01 | 0.0% | 12.5% | 15.6% | 23.4% | 56.2% | 75.0% |
| coupon settlement | 3 y | 52 | 47 | 1.9 | 0.21 | 0.0% | 23.4% | 42.6% | 59.6% | 78.7% | 89.4% |
| large bill settlement | 1 y | 7 | 31 | 5.3 | 0.77 | 0.0% | 6.5% | 6.5% | 6.5% | 9.7% | 16.1% |
| large bill settlement | 2 y | 13 | 25 | 2.8 | -0.04 | 0.0% | 12.0% | 12.0% | 16.0% | 20.0% | 32.0% |
| large bill settlement | 3 y | 20 | 18 | | too few windows | |  |  |  |  |  |
| month-end turn | 1 y | 8 | 39 | 5.8 | 0.68 | 0.0% | 10.3% | 12.8% | 17.9% | 20.5% | 38.5% |
| month-end turn | 2 y | 16 | 31 | 2.9 | -0.05 | 0.0% | 12.9% | 19.4% | 32.3% | 45.2% | 74.2% |
| month-end turn | 3 y | 25 | 22 | 1.8 | -0.31 | 0.0% | 9.1% | 13.6% | 31.8% | 59.1% | 86.4% |
| tax date | 1 y | 13 | 59 | 5.5 | 0.54 | 0.0% | 10.2% | 15.3% | 28.8% | 42.4% | 47.5% |
| tax date | 2 y | 25 | 47 | 2.8 | 0.42 | 0.0% | 10.6% | 14.9% | 34.0% | 36.2% | 40.4% |
| tax date | 3 y | 38 | 34 | 1.9 | 0.51 | 0.0% | 8.8% | 8.8% | 11.8% | 20.6% | 38.2% |
| IORB-change window (two days after a meeting) | 1 y | 5 | 26 | 6.0 | 0.98 | 3.8% | 7.7% | 19.2% | 19.2% | 26.9% | 42.3% |
| IORB-change window (two days after a meeting) | 2 y | 11 | 20 | 2.7 | 0.44 | 0.0% | 20.0% | 30.0% | 35.0% | 50.0% | 55.0% |
| IORB-change window (two days after a meeting) | 3 y | 16 | 15 | | too few windows | |  |  |  |  |  |
| union of the strata | 1 y | 29 | 139 | 5.8 | 0.82 | 0.0% | 7.2% | 12.9% | 25.2% | 33.8% | 47.5% |
| union of the strata | 2 y | 59 | 109 | 2.8 | 0.82 | 0.0% | 10.1% | 15.6% | 22.9% | 40.4% | 56.0% |
| union of the strata | 3 y | 88 | 80 | 1.9 | 0.11 | 0.0% | 12.5% | 22.5% | 43.8% | 50.0% | 75.0% |
| union without the bill stratum | 1 y | 28 | 132 | 5.7 | 0.82 | 0.0% | 12.1% | 15.2% | 24.2% | 36.4% | 49.2% |
| union without the bill stratum | 2 y | 56 | 104 | 2.8 | 0.89 | 0.0% | 10.6% | 15.4% | 21.2% | 35.6% | 53.8% |
| union without the bill stratum | 3 y | 84 | 76 | 1.9 | 0.14 | 0.0% | 9.2% | 21.1% | 44.7% | 53.9% | 71.1% |

### Upper-tail twCRPS (key secondary), the union only

**Against B1**

| stratum | window | N events | windows | independent | c | size | power at 3.0% | power at 5.0% | power at 10.0% | power at 15.0% | power at 20.0% |
|---|---|---|---|---|---|---|---|---|---|---|---|
| union of the strata | 1 y | 104 | 486 | 5.7 | 1.50 | 4.3% | 6.6% | 7.0% | 68.5% | 79.2% | 82.1% |
| union of the strata | 2 y | 208 | 382 | 2.8 | 1.60 | 4.5% | 7.9% | 8.4% | 72.0% | 78.5% | 80.1% |
| union of the strata | 3 y | 311 | 279 | 1.9 | 1.45 | 2.9% | 10.4% | 12.9% | 67.7% | 72.8% | 79.2% |
| union without the bill stratum | 1 y | 73 | 291 | 5.7 | 400.18 | 63.9% | 26.8% | 27.1% | 31.3% | 31.6% | 32.3% |
| union without the bill stratum | 2 y | 146 | 268 | 2.8 | 721.99 | 70.5% | 18.7% | 20.9% | 25.4% | 26.1% | 26.5% |
| union without the bill stratum | 3 y | 218 | 196 | 1.9 | 41.93 | 68.9% | 11.2% | 11.7% | 12.2% | 12.2% | 15.3% |

**Against B1'**

| stratum | window | N events | windows | independent | c | size | power at 3.0% | power at 5.0% | power at 10.0% | power at 15.0% | power at 20.0% |
|---|---|---|---|---|---|---|---|---|---|---|---|
| union of the strata | 1 y | 104 | 486 | 5.7 | 1.52 | 3.5% | 65.0% | 72.2% | 77.6% | 81.5% | 83.3% |
| union of the strata | 2 y | 208 | 382 | 2.8 | 1.65 | 5.2% | 59.4% | 70.9% | 78.8% | 80.1% | 84.0% |
| union of the strata | 3 y | 311 | 279 | 1.9 | 1.76 | 6.1% | 56.3% | 66.7% | 72.8% | 78.5% | 81.4% |
| union without the bill stratum | 1 y | 73 | 291 | 5.7 | 3117.38 | 64.6% | 16.8% | 16.8% | 17.2% | 17.5% | 17.5% |
| union without the bill stratum | 2 y | 146 | 268 | 2.8 | 5757.48 | 69.0% | 7.8% | 10.1% | 10.1% | 10.4% | 10.4% |
| union without the bill stratum | 3 y | 218 | 196 | 1.9 | 46.18 | 68.9% | 11.2% | 11.7% | 12.2% | 12.2% | 13.3% |

**Against B2**

| stratum | window | N events | windows | independent | c | size | power at 3.0% | power at 5.0% | power at 10.0% | power at 15.0% | power at 20.0% |
|---|---|---|---|---|---|---|---|---|---|---|---|
| union of the strata | 1 y | 104 | 486 | 5.7 | 0.26 | 0.0% | 5.1% | 5.3% | 6.0% | 6.6% | 7.4% |
| union of the strata | 2 y | 208 | 382 | 2.8 | -0.27 | 0.0% | 5.5% | 5.5% | 6.3% | 6.8% | 8.1% |
| union of the strata | 3 y | 311 | 279 | 1.9 | -0.20 | 0.0% | 5.7% | 6.5% | 6.8% | 7.5% | 9.0% |
| union without the bill stratum | 1 y | 73 | 291 | 5.7 | 0.05 | 0.0% | 5.2% | 5.5% | 5.5% | 5.8% | 6.9% |
| union without the bill stratum | 2 y | 146 | 268 | 2.8 | -0.73 | 0.0% | 5.6% | 5.6% | 6.0% | 6.0% | 7.5% |
| union without the bill stratum | 3 y | 218 | 196 | 1.9 | -0.08 | 0.0% | 5.6% | 5.6% | 6.1% | 6.1% | 7.1% |

**Against risk-date calendar (#693)**

| stratum | window | N events | windows | independent | c | size | power at 3.0% | power at 5.0% | power at 10.0% | power at 15.0% | power at 20.0% |
|---|---|---|---|---|---|---|---|---|---|---|---|
| union of the strata | 1 y | 29 | 104 | 5.8 | 0.61 | 0.0% | 5.8% | 5.8% | 6.7% | 6.7% | 7.7% |
| union of the strata | 2 y | 59 | 104 | 2.8 | -0.02 | 0.0% | 5.8% | 5.8% | 6.7% | 6.7% | 7.7% |
| union of the strata | 3 y | 88 | 80 | 1.9 | -0.41 | 0.0% | 7.5% | 7.5% | 8.8% | 8.8% | 10.0% |
| union without the bill stratum | 1 y | 28 | 103 | 5.7 | 0.57 | 0.0% | 5.8% | 6.8% | 6.8% | 6.8% | 7.8% |
| union without the bill stratum | 2 y | 56 | 103 | 2.8 | 0.00 | 0.0% | 5.8% | 5.8% | 6.8% | 6.8% | 7.8% |
| union without the bill stratum | 3 y | 84 | 76 | 1.9 | -0.36 | 0.0% | 7.9% | 7.9% | 7.9% | 9.2% | 10.5% |

## 5. Reading

- **The strata give more events per window, not more independent windows.** The history is 5.7 years, so a window of 1, 2 or 3 years leaves 5.7, 2.8 and 1.9 windows without overlap whatever the unit; H5's own unit on the same history has the same 5.7, 2.9 and 1.9. What the union buys is 208 events in a 2-year window, against 500 days.
- **The events are not close to independent.** The ACF of d between consecutive union events is +0.50 / +0.27 / +0.15 against B1 and +0.69 / +0.52 / +0.44 against B2 (lags 1, 2, 3). Lens C expected it near zero; it is not, so the standard error of a window of events has to carry the dependence (the Newey-West lag does), and the contiguous-window c is what sets the bar.
- **The contiguous c is above the normal value.** Against B1 the union's c is 2.23, 2.32 and 2.03 at 1, 2 and 3 years (size at the normal 1.645: 15.2%, 19.9%, 11.1%), against 1.91, 2.12 and 1.67 for all days. A test on events needs its own contiguous-calibrated value.
- **Power at the protocol's 3.0% MME is low for the union and for all days.** Against B1, the union's power at 3.0% is 10.3%, 15.4% and 20.8% at 1, 2 and 3 years; at 10.0% it is 53.7%, 64.7% and 63.8%. All days at the same skill: 10.9% and 39.3% at 2 years. Against B1' and B2 the power is in the same tables; a skill is a share of the benchmark's own mean score, so it is a larger shift against B2 than against B1.
- **The bill stratum carries part of the union's pooled skill over B1.** With it the union's skill over B1 is +7.7% [+2.0%, +13.6%]; without it, +4.0% [-2.9%, +10.4%]. The default below drops the stratum for want of a ruling on its size rule, not for this; both are in the tables.
- **The upper-tail twCRPS studentized on events is unstable.** In its union tables below c runs from -0.73 to 5757, with sizes at the normal value of up to 70.5%: a c of that size is what a window in which the two forecasts score nearly alike gives. The key secondary cannot be confirmed by this statistic on events as it stands; that is a statement about the statistic, not about the candidate.
- **The stand-in candidate's skill depends on the regime.** Over B1 on the union it is 2020: -17.5% [-29.1%, -8.2%], 2021-23: -5.4% [-14.8%, +1.3%], 2024: +19.4% [+12.3%, +27.8%], 2025-26: +14.6% [+3.1%, +24.9%]; pooled +7.7% [+2.0%, +13.6%]. Over B1' it is +1.2% [-4.7%, +7.0%] pooled and over B2 +40.4% [+31.7%, +48.2%]. A pooled figure alone is not a result.
- **Tax dates are B2's own pool.** B2 for a tax date and the risk-date calendar benchmark are the same trailing-year empirical distribution of tax-date spreads, so the two rows agree and the calendar benchmark adds nothing on that stratum.

## 6. Questions for Eleonora (marked; none is settled in code)

Each has a default that applies if she has not answered by the next 5 pm batch. No default changes what the project claims; a default is a draft for the registration PR.

1. **The unit of evidence.** (a) the union of the declared strata, one event per target day; (b) each stratum alone, with the thin ones pooled; (c) the union as the primary and the strata as reported cuts. **Default: (c).** The union is the largest sample; the strata say where the skill is.
2. **The strata, and the bill stratum.** Which rows of section 1 are in the union. The large bill stratum (245 events) rests on a stand-in size rule (the 75th percentile of the trailing 252 rows) with no ruling behind it, and it changes the union from 413 to 589 events. **Default: the union without the bill stratum** (146 events in a 2-year window against B1), until she rules on a bill-size rule.
3. **The month-end turn.** The strata use #959's turn label. #1135 drafts it as the one definition; this design stands on that draft, and the month-end rows are re-cut if she rules otherwise. **Default: #959's label.**
4. **The window length.** Against B1 the union's power at 10.0% skill is 53.7%, 64.7% and 63.8% at 1, 2 and 3 years (at 5.0% skill: 14.8%, 29.3% and 37.6%), while the windows left without overlap fall to 1.9. **Default: 2 years.** Windows longer than the history cannot be calibrated here.
5. **The minimum meaningful effect.** The protocol's 3.0% against B1 is below what these windows can detect (power 15.4% for the union at 2 years). Either H6's MME is larger, or the 3% stands and the registration states that it cannot be confirmed in the window. A new MME is a §13 change. **Default: keep 3% and state the power beside it; no new MME is proposed.**
6. **The benchmarks that must be beaten.** (a) B1 only, as the protocol; (b) B1 and B2; (c) all four, with B1' and the calendar benchmark reported beside the protocol's. **Default: B1 and B2 decisive, B1' and the calendar benchmark reported.** A candidate that does not beat B1' has learned nothing the calendar did not already say, so it is in the table either way.
7. **Multiplicity.** With the union as the primary, the strata are reported cuts and carry no correction; if she makes the strata the unit, Holm across them. **Default: none on reported cuts.**
8. **A stratum benchmark.** #693's calendar benchmark covers four risk types; the FOMC and IORB-change rows would need their own, a new benchmark (a §13 change). **Default: not added; those rows are compared with B1, B1' and B2 only.**
9. **The point-in-time reading of the settlement flags.** A coupon settlement is a risk date at a lead only where its announcement was public (#849). The strata read the panel's flag; the registration must read it as #849 does. **Default: as #849.**
10. **The critical value.** The normal 1.645 is not the bar (section 5). The registration would calibrate c on the contiguous windows of events, as #963 does for days, and print the independent-window count beside it. **Default: yes, on the final strata and window.**

## What this shows, and does not

- It gives the strata, their event counts, the development skill of one stand-in candidate on each, and the power of contiguous windows of events. It registers nothing, scores no confirmation day, and sets no rule.
- The power rests on one stand-in candidate's d, four benchmarks and one history. The d series of a stratum is a few dozen to a few hundred events, dependent; the windows overlap, so each quantile rests on the independent count shown. A skill is the share of the benchmark's mean score on the stratum, so the same percentage is a different shift for each benchmark.
- The first run of the script produced the strata, the union and the power tables; the union without the bill stratum and the all-days rows were added to the declaration afterwards and are in this record (the declaration says so).
- Not checked: `gbm_funding` on the strata (a long run); a stratum-specific calendar benchmark for the turn, FOMC and IORB rows; the per-lead point-in-time dating of the bill and coupon flags; B1' on a confirmation day; the fixed-b statistic on events.
