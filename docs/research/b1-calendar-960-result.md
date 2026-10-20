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

## The gbm_funding arms (added 2026-10-20 from commit 39f35d5a)

*Added 2026-10-20.* This section replaces "Not scored here: the gbm_funding arms". Commit 39f35d5a ("#960: gbm_funding pairs
scored from the Mac walks (needs-mac); evidence only") put the arms in `docs/pivot/evidence/b1-calendar-960/`. Every figure below is quoted
from `report.md` there (its table, or `score.json` at the key given); nothing is computed by hand. The same 1,855 decision days
(2018-07-19 to 2025-12-23) carry every model (`score.json`, `notes.gbm`: `gbm_days` 1855, `transparent_days` 1855,
`common_days` 1855). Development data, not a verdict.

Mean scores, pooled (`score.json`, `means.grid_crps` and `means.upper_tail_twcrps`; `report.md`, "Mean scores, pooled"):

| pooled, 1,855 decision days | grid CRPS, bp | upper-tail twCRPS, bp |
|---|---|---|
| B1 | 2.2889 | 1.3750 |
| B2 | 2.5184 | 1.1315 |
| B1′ | 1.9281 | 1.0648 |
| `spread_mr_ctx` (#761) | 1.7504 | 0.9077 |
| `gbm_funding` (#634) | 1.8223 | 0.9515 |

Grid CRPS skill of `gbm_funding` over each benchmark, positive favouring `gbm_funding`, two-sided 90% interval (`report.md`,
"grid CRPS (23 levels)"; `score.json`, `groups.<cut>.<group>.metrics.grid_crps.pairs["gbm_funding vs …"]`):

| | over `spread_mr_ctx` | over B1′ | over B1 | over B2 |
|---|---|---|---|---|
| pooled (`groups.pooled`) | −4.1% [−8.0%, −0.3%] | +5.5% [+1.3%, +11.7%] | +20.4% [+12.8%, +41.2%] | +27.6% [+17.9%, +37.2%] |
| ordinary targets, 1,590 days (`groups.target_type.ordinary`) | −2.2% [−6.9%, +2.7%] | +10.4% [+5.2%, +17.3%] | +28.1% [+15.8%, +62.5%] | +30.5% [+21.9%, +39.2%] |
| anchor day ordinary, 1,588 days (`groups.anchor_type.ordinary`) | −4.6% [−8.4%, −0.5%] | +7.8% [+3.3%, +14.0%] | +8.7% [+4.4%, +14.8%] | +28.0% [+16.5%, +38.5%] |
| anchor a month-end, 149 days | −9.5% [−21.3%, +1.1%] | −11.9% [−27.1%, −0.0%] | +29.4% [+20.0%, +44.3%] | +20.3% [+3.9%, +38.0%] |
| anchor a quarter-end, 29 days | +9.0% [−14.3%, +43.7%] | +9.4% [−9.5%, +23.1%] | +68.3% [+48.6%, +108.5%] | +17.0% [−108.0%, +57.1%] |
| anchor a tax date, 89 days | +7.3% [−25.2%, +43.2%] | −21.3% [−72.4%, −2.9%] | +69.6% [+21.7%, +193.6%] | +35.4% [+11.3%, +62.7%] |

Upper-tail twCRPS, pooled (`groups.pooled`, `metrics.upper_tail_twcrps`): `gbm_funding` over `spread_mr_ctx` −4.8% [−9.6%, +0.2%];
over B1′ +10.6% [+3.0%, +22.8%]; over B1 +30.8% [+21.4%, +51.6%]; over B2 +15.9% [+4.2%, +29.0%].

By regime of the target day (grid CRPS, `groups.regime`), `gbm_funding` over `spread_mr_ctx` / over B1′ / over B1 / over B2:

| regime (days) | over `spread_mr_ctx` | over B1′ | over B1 | over B2 |
|---|---|---|---|---|
| 2018-19 (361) | −10.0% [−17.8%, −2.7%] | +5.8% [−1.7%, +22.2%] | +29.8% [+18.8%, +59.5%] | +8.9% [−0.6%, +20.5%] |
| 2020 (251) | +14.9% [−1.4%, +26.3%] | +12.6% [−2.0%, +22.4%] | +14.6% [−0.9%, +23.2%] | +49.7% [+20.0%, +68.3%] |
| 2021-23 (748) | +1.5% [−13.0%, +13.5%] | −6.2% [−23.4%, +5.5%] | −1.4% [−18.9%, +10.3%] | +51.7% [+37.9%, +66.0%] |
| 2024 (250) | −9.8% [−16.3%, +0.3%] | +7.2% [+1.4%, +14.4%] | +14.5% [+9.1%, +21.8%] | +1.1% [−13.3%, +14.5%] |
| 2025-26 (249) | −6.3% [−15.3%, +3.2%] | +7.6% [+1.1%, +15.7%] | +15.6% [+9.2%, +24.4%] | +24.9% [+1.5%, +45.5%] |

The other cuts (target day type for month-end, quarter-end and tax-date targets; the upper-tail twCRPS by regime and day type) are
in `report.md`; cells where the studentization cannot resolve a comparison are marked undefined there, not filled.

### The two declared reading rules

Both are as declared in #960 (Lens C's kill conditions). The wording is the script's, from `score.json`, `reading_rules`. Each is
development data, not a verdict.

1. *Beyond the transparent model.* "The gbm is not shown to carry anything beyond the transparent model: its skill over
   spread_mr_ctx on ordinary targets is −2.2% with a one-sided 95% lower bound of −6.9%, below 0." The interval is
   `groups.target_type.ordinary`, `grid_crps`, `"gbm_funding vs spread_mr_ctx"`: −2.2% [−6.9%, +2.7%].
2. *The MME against B1′.* "gbm_funding's pooled skill over B1′ is +5.5%, not below the 3% of the MME as set." The interval is
   `groups.pooled`, `grid_crps`, `"gbm_funding vs B1_prime"`: +5.5% [+1.3%, +11.7%].

What the figures say, and no more: on these development days `gbm_funding` is ahead of B1, B2 and B1′ pooled, and behind
`spread_mr_ctx` pooled (−4.1%, the interval wholly below zero). Against B1′ it is ahead on ordinary targets and anchors and behind
on month-end and tax-date anchors, and its lead over B1′ is not shown in 2018-19, 2020 or 2021-23 (intervals include zero).
Neither reading rule is a verdict, and neither decides which candidate a registration can claim.

## For Eleonora (marked questions; not settled here)

1. Does B1′ replace B1 as a protocol benchmark? (A §13 change.) Her #741 ruling kept B1 and the MME unchanged.
2. If it does, is the MME re-set against it?

Development, not a verdict.
