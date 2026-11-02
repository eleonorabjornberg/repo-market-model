# Data map

This is the data map for an academic exercise. Only the public layer below is
acquired, and it is acquired under each provider's own terms; raw responses are kept
out of Git and are not redistributed here. The restricted layer is recorded because a
serious treatment of this market would need it, and because naming what is missing is
part of stating what the public-data results can and cannot support — not because any
of it has been obtained.

Source, availability and revision behaviour for anything actually ingested are
declared in `metadata/sources.json` and enforced by the registry. This page is the
map; the registry is the authority.

## Public U.S. modeling layer

| Domain | Candidate source | Native frequency | Public resolution | Role |
|---|---|---:|---|---|
| Repo rates | New York Fed | Daily | Rate percentiles and volume | Targets and market state |
| Fed balance sheet | Federal Reserve H.4.1 / FRED | Daily or weekly | Aggregate | Reserves, TGA, ON RRP, assets |
| Policy rates | Federal Reserve / New York Fed | Daily/event | Aggregate | Corridor and outside options |
| Treasury issuance | Treasury Fiscal Data / auction data | Event/daily | Security/event | Financing and settlement pressure |
| Dealers | New York Fed primary-dealer statistics | Weekly | Aggregate/category | Inventory and intermediation proxies |
| Money funds | SEC Form N-MFP and OFR/Fed aggregates | Monthly/daily aggregate | Fund or aggregate, depending source | Cash-supply capacity |
| Treasury market | Treasury, Fed, exchanges/vendors | Intraday/daily | Mixed | Prices, volatility, liquidity and basis proxies |
| Calendar | Treasury/IRS/Fed calendars | Event | Public | Tax, auction, settlement and reporting effects |

## Restricted layer

| Dataset | Adds |
|---|---|
| FR 2052a | Legal-entity liquidity, funding maturity, prime brokerage and contingent flows |
| Fedwire Funds/Securities | Bank-level intraday payment and securities-settlement network |
| OFR/Fed repo microdata | Counterparties, terms, collateral, segment and lifecycle |
| CCP/clearing-bank data | Novation, margin, netting, settlement and rejected transactions |
| Internal dealer data | Limits, rejected RFQs, shadow balance-sheet prices and package identifiers |

## Required daily panel fields

The initial contract is intentionally small. Optional features may be absent, but the
target and policy anchor are required.

| Field | Required | Unit |
|---|---:|---|
| `date` | yes | ISO date |
| `sofr` | yes | percent |
| `iorb` | yes | percent |
| `sofr_volume` | no | USD billions |
| `sofr_p25` | no | percent |
| `sofr_p75` | no | percent |
| `tgcr` | no | percent |
| `bgcr` | no | percent |
| `reserve_balances` | no | USD billions |
| `tga` | no | USD billions |
| `on_rrp` | no | USD billions |
| `treasury_settlement` | no | USD billions |
| `treasury_settlement_bills` | no | USD billions |
| `treasury_settlement_coupons` | no | USD billions |
| `treasury_settlement_soma` | no | USD billions |
| `dealer_treasury_position` | no | USD billions |
| `mmf_assets` | no | USD billions |
| `tbill_4w` | no | percent, coupon equivalent |
| `tbill_13w` | no | percent, coupon equivalent |
| `quarter_end` | no | zero/one |
| `tax_date` | no | zero/one |
| `days_to_month_end` | no | calendar days, 0 on the last day of the month |

## The two missing percentile rows

In the published panel `sofr_p25` and `sofr_p75` are empty on two days, 2019-05-31 and 2021-08-05. On both the New York Fed
publishes SOFR with its percentiles marked `NA` (footnote 2), so the holes are the source's, counted and left empty, never
filled (METHODOLOGY.md, "Absence is typed").

Which scored forecasts touched them:

- The gradient-boosted records (`gbm_funding` and its calibrated variants, features including `sofr_p25` and `sofr_p75`) are the
  scored forecasts that read either column. For the published model (nested conformal PID), the forecast of 2019-06-04 reads the 2019-05-31 row, and its forecast of 2021-08-09 reads the
  2021-08-05 row, as the served feature (two panel rows before the scored day, the as-of rule's distance for these fields). Each is
  one scored forecast, at the 16:00 decision instant the published records were made at.
- Every scored forecast after a hole also holds that row in its training frame.
- Handling is the model's, in `src/repo_model/ml.py` and `baseline._raw_regressor`: a regressor carried as `None` takes its fitted
  imputation (the training mean), in the fit and in the served row. It is never `0.0` and never carried forward from the day before.
- No other scored forecast touches them. Persistence, climatology and the candidate (s3c-ann-net) read neither column
  (`scripts/vintage_timing_audit_1365.py`, `UNREAD_COLUMNS`).

The days were found by reading the as-of rule's reads over every day of `docs/runs/published_distribution_daily_h1.json`; no
published figure changes.

## Point-in-time rule

For any field `x`, the feature used to forecast date `t` must satisfy:

```text
available_at(x) <= forecast_created_at(t)
```

A weekly observation published on Thursday cannot be used as if known on the prior
Monday. Revisions are stored as vintages when the source permits.

## Missing-data rule

- Do not silently mean-fill.
- Add a missingness indicator for every imputed feature.
- Use an as-of carry only when economically meaningful and publication-safe.
- Preserve structural zeros.
- Fit imputers inside each training window.
- For networks and latent buffers, retain multiple posterior draws.

