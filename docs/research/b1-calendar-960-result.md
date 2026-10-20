# B1′, a calendar-aware persistence, on real data (#960)

**Hypothesis and step:** H5 (primary goal) step 5 (which candidate a registration can claim) and H1 step 3 (benchmarks).
**Development data, not a verdict** (scoring protocol v1, #640). The declaration is `metadata/b1_calendar_960.json`, committed
before any number was computed. The script is `scripts/b1_calendar_960.py`; the evidence is in
`docs/pivot/evidence/b1-calendar-960/` (`score.json`, `report.md`). Intervals are the studentized stationary bootstrap's
(ruling 1, #739), two-sided 90%, so the lower end is the one-sided 95% lower bound.

## What B1′ is

B1 with two changes and no parameter. The **anchor** is the spread of the last *ordinary* day at or before the as-of anchor.
The **changes** are `spread[e] − last_ordinary[e − h]` over B1's own two-year window, pooled by the target day's reporting day
type (30 changes at least, else every type). It is a reference row, not a benchmark of the protocol: B1 stays as ruled.

## The transparent arms (scored here)

1,855 decision days, 2018-07-19 to 2025-12-23 (last target 2025-12-31); the pooled grid CRPS of B1, B2 and `spread_mr_ctx`
reproduce #761's page (to 1e-9).

| pooled, 1,855 decision days | grid CRPS, bp | upper-tail twCRPS, bp |
|---|---|---|
| B1 | 2.289 | 1.375 |
| B2 | 2.518 | 1.132 |
| B1′ | 1.928 | 1.065 |
| `spread_mr_ctx` (#761) | 1.750 | 0.908 |

Grid CRPS skill, first model over the second (positive favours the first):

| | B1′ over B1 | B1′ over B2 | `spread_mr_ctx` over B1′ | `spread_mr_ctx` over B1 |
|---|---|---|---|---|
| pooled | +15.8% [+8.1%, +49.2%] | +23.4% [+12.1%, +33.7%] | +9.2% [+4.9%, +15.3%] | +23.5% [+16.5%, +40.8%] |
| ordinary targets (1,590 days; the headline cell) | +19.7% [+7.6%, +75.9%] | +22.4% [+9.6%, +33.2%] | +12.3% [+7.0%, +19.0%] | +29.6% [+18.9%, +57.1%] |
| anchor day ordinary (1,588 days) | +1.1% [+0.2%, +1.8%] | +21.9% [+9.3%, +33.3%] | +11.8% [+7.7%, +17.8%] | +12.8% [+8.8%, +18.5%] |
| anchor a month-end (149 days) | +37.0% [+24.0%, +53.4%] | +28.7% [+14.7%, +41.0%] | −2.2% [−10.2%, +5.7%] | +35.6% [+24.3%, +53.5%] |
| anchor a quarter-end (29 days) | +65.0% [+35.1%, +151.2%] | +8.4% [−101.5%, +74.7%] | +0.4% [−27.2%, +39.3%] | +65.2% [+36.9%, +104.8%] |
| anchor a tax date (89 days) | +74.9% [+42.0%, +204.7%] | +46.7% [+19.6%, +65.2%] | −30.7% [−95.1%, −11.4%] | +67.2% [+29.7%, +212.4%] |

By regime of the target day (grid CRPS, B1′ over B1 / `spread_mr_ctx` over B1′): 2018-19 +25.5% [+13.4%, +70.7%] / +14.4%
[+3.7%, +27.3%]; 2020 +2.3% [−7.8%, +8.5%] / −2.8% [−17.5%, +29.0%]; 2021-23 +4.5% [+2.6%, +6.7%] / **−7.8% [−13.6%, −2.4%]**;
2024 +7.9% [+4.2%, +12.6%] / +15.5% [+6.3%, +24.4%]; 2025-26 +8.6% [+4.7%, +13.2%] / +13.1% [+4.5%, +21.6%]. The upper-tail
twCRPS and the other cuts (target day type, all pairs) are in `report.md`. Cells where the studentization cannot resolve a
comparison are marked undefined there, not filled.

## What this shows, and does not

- A zero-parameter forecast that knows only the calendar beats B1 by +15.8% of grid CRPS pooled (lower bound +8.1%), against
  the 3% the MME sets for a candidate over B1. Nearly all of it is on decision days whose anchor is a month-end, quarter-end
  or tax date: with an ordinary anchor B1′ beats B1 by +1.1%. This agrees with Lens C's proxy (#958: +15.6% pooled, +1.1% on
  ordinary anchors); #741's `b1_recentred` row gives +14.8% on the same days.
- `spread_mr_ctx` beats B1′ by +9.2% pooled, and by +12.3% on ordinary targets, but **loses to it in 2021-23**
  (−7.8%, the interval wholly below zero) and does not beat it on month-end, quarter-end or tax-date anchors.

## Not scored here: the gbm_funding arms

`gbm_funding` against `spread_mr_ctx`, against B1′, against B1 and against B2, and the two declared reading rules, need
`gbm_funding`'s per-day forecasts. They are #634's walks, which take hours and run on Eleonora's Mac (the rule on long runs in
#46). #905 (#901), which was to commit them, is a draft that waits for the same run, so no `daily.json` exists. The
commands are in the pull request. Until they run, **nothing on this page says whether the gbm carries anything beyond
`spread_mr_ctx`, or whether the MME is reachable against B1′.** The two rules, as declared (Lens C's kill conditions), are
printed by the script from the numbers when the walks are given:

1. if `gbm_funding`'s grid-CRPS skill over `spread_mr_ctx` on ordinary targets has a one-sided 95% lower bound below 0, the gbm
   is not shown to carry anything beyond the transparent model;
2. if its pooled skill over B1′ is below 3%, the MME as set is not reachable by this candidate against B1′.

## For Eleonora (marked questions; not settled here)

1. Does B1′ replace B1 as a protocol benchmark? (A §13 change.) Her #741 ruling kept B1 and the MME unchanged.
2. If it does, is the MME re-set against it?

Development, not a verdict.
