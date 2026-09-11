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

