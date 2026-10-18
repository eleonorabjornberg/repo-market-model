# H3 step 3: the nested test (#708), report

Decision days 1868 (2018-06-29 to 2025-12-23); draws 10000, seed 708. Cells: skill [one-sided 95% bounds] / lower bound of mean daily difference.

## Grid CRPS (bp), mean

| model | mean | vs B1 | vs B2 |
|---|---|---|---|
| candidate (`gbm_funding`) | 1.826 | +20.7% [+13.2%, +40.4%] / +0.2326 | +27.4% [+17.7%, +36.8%] / +0.4600 |
| + nyfed_pd_financing | 1.824 | +20.8% [+13.3%, +40.8%] / +0.2341 | +27.5% [+18.0%, +36.7%] / +0.4639 |
| + treasury_auction_results | 1.839 | +20.1% [+12.5%, +40.3%] / +0.2204 | +26.9% [+17.3%, +36.2%] / +0.4469 |
| + nyfed_on_rrp_counterparties | 1.817 | +21.1% [+13.8%, +40.4%] / +0.2428 | +27.7% [+17.9%, +37.2%] / +0.4676 |
| + treasury_dts_debt_cash | 1.842 | +20.0% [+12.3%, +40.6%] / +0.2166 | +26.7% [+17.3%, +36.1%] / +0.4458 |

B1: 2.302; B2: 2.514.

## Nested difference (candidate minus candidate + family), grid CRPS

| family | primary | upper-tail twCRPS | Holm p |
|---|---|---|---|
| + nyfed_pd_financing | +0.1% [-1.1%, +1.3%] / -0.0199 | +0.2% [-1.3%, +1.7%] / -0.0113 | 1.000 |
| + treasury_auction_results | -0.7% [-1.4%, -0.1%] / -0.0255 | +0.0% [-0.8%, +0.8%] / -0.0076 | 1.000 |
| + nyfed_on_rrp_counterparties | +0.5% [-0.1%, +1.1%] / -0.0007 | +0.3% [-0.3%, +1.0%] / -0.0023 | 0.260 |
| + treasury_dts_debt_cash | -0.9% [-1.6%, -0.3%] / -0.0273 | -0.6% [-1.4%, +0.1%] / -0.0123 | 1.000 |

## Reading (declared rule)

- `nyfed_pd_financing`: no improvement beyond its interval (skill +0.1%, lower bound of mean(d) -0.0199, Holm p 1.000).
- `treasury_auction_results`: no improvement beyond its interval (skill -0.7%, lower bound of mean(d) -0.0255, Holm p 1.000).
- `nyfed_on_rrp_counterparties`: no improvement beyond its interval (skill +0.5%, lower bound of mean(d) -0.0007, Holm p 0.260).
- `treasury_dts_debt_cash`: no improvement beyond its interval (skill -0.9%, lower bound of mean(d) -0.0273, Holm p 1.000).
- **H3 overall (development, not a verdict):** no family improves the candidate beyond its interval: the kill reading is met on development data.

## As-of scarcity state of the decision day

### high (n = 514)

| family | nested difference |
|---|---|
| + nyfed_pd_financing | +0.6% [-1.0%, +2.1%] / -0.0381 |
| + treasury_auction_results | +0.2% [-0.6%, +1.0%] / -0.0225 |
| + nyfed_on_rrp_counterparties | +0.3% [-0.3%, +1.0%] / -0.0088 |
| + treasury_dts_debt_cash | -0.9% [-1.9%, -0.1%] / -0.0667 |

### low (n = 1354)

| family | nested difference |
|---|---|
| + nyfed_pd_financing | -0.5% [-2.3%, +1.3%] / -0.0242 |
| + treasury_auction_results | -2.0% [-3.2%, -0.8%] / -0.0333 |
| + nyfed_on_rrp_counterparties | +0.8% [-0.3%, +2.0%] / -0.0031 |
| + treasury_dts_debt_cash | -0.8% [-1.7%, +0.1%] / -0.0184 |

## Pressure-day type of the target day

### month_end (n = 507)

| family | nested difference |
|---|---|
| + nyfed_pd_financing | +0.8% [-1.0%, +2.9%] / -0.0218 |
| + treasury_auction_results | -1.7% [-3.7%, -0.2%] / -0.0840 |
| + nyfed_on_rrp_counterparties | -0.1% [-1.0%, +0.7%] / -0.0218 |
| + treasury_dts_debt_cash | -1.8% [-3.0%, -0.6%] / -0.0750 |

### ordinary (n = 1868)

| family | nested difference |
|---|---|
| + nyfed_pd_financing | +0.2% [-1.3%, +1.7%] / -0.0189 |
| + treasury_auction_results | -0.6% [-1.5%, +0.2%] / -0.0219 |
| + nyfed_on_rrp_counterparties | +0.7% [+0.0%, +1.4%] / +0.0001 |
| + treasury_dts_debt_cash | -0.7% [-1.5%, +0.0%] / -0.0222 |

### quarter_end (n = 146)

| family | nested difference |
|---|---|
| + nyfed_pd_financing | +1.3% [+0.3%, +2.2%] / -0.0120 |
| + treasury_auction_results | -0.2% [-1.2%, +0.6%] / -0.0749 |
| + nyfed_on_rrp_counterparties | +0.5% [+0.0%, +1.1%] / -0.0015 |
| + treasury_dts_debt_cash | -0.5% [-1.7%, +0.5%] / -0.1103 |

### tax_date (n = 214)

| family | nested difference |
|---|---|
| + nyfed_pd_financing | -0.6% [-1.8%, +0.5%] / -0.0985 |
| + treasury_auction_results | -0.9% [-2.1%, +0.4%] / -0.0718 |
| + nyfed_on_rrp_counterparties | -0.2% [-0.5%, +0.2%] / -0.0380 |
| + treasury_dts_debt_cash | -0.9% [-3.1%, +1.1%] / -0.0943 |

## Provisional regimes (hindsight; reported only)

### 2018-19 (n = 375)

| family | nested difference |
|---|---|
| + nyfed_pd_financing | +0.7% [-1.0%, +2.3%] / -0.0387 |
| + treasury_auction_results | +0.5% [-0.2%, +1.5%] / -0.0047 |
| + nyfed_on_rrp_counterparties | +0.3% [-0.3%, +1.0%] / -0.0117 |
| + treasury_dts_debt_cash | -0.4% [-1.3%, +0.3%] / -0.0443 |

### 2020 (n = 251)

| family | nested difference |
|---|---|
| + nyfed_pd_financing | +5.2% [+0.7%, +11.6%] / +0.0167 |
| + treasury_auction_results | -0.8% [-2.4%, +0.6%] / -0.0328 |
| + nyfed_on_rrp_counterparties | +1.4% [-0.4%, +4.3%] / -0.0064 |
| + treasury_dts_debt_cash | -1.7% [-3.9%, +0.9%] / -0.0776 |

### 2021-23 (n = 748)

| family | nested difference |
|---|---|
| + nyfed_pd_financing | -4.7% [-8.2%, -1.6%] / -0.0596 |
| + treasury_auction_results | -4.6% [-7.0%, -2.7%] / -0.0510 |
| + nyfed_on_rrp_counterparties | +1.2% [-1.2%, +3.6%] / -0.0080 |
| + treasury_dts_debt_cash | -2.1% [-3.9%, -0.3%] / -0.0276 |

### 2024 (n = 250)

| family | nested difference |
|---|---|
| + nyfed_pd_financing | +1.1% [-1.0%, +3.4%] / -0.0133 |
| + treasury_auction_results | -1.5% [-2.7%, -0.3%] / -0.0459 |
| + nyfed_on_rrp_counterparties | -0.6% [-1.8%, +0.4%] / -0.0305 |
| + treasury_dts_debt_cash | -1.6% [-3.6%, +0.3%] / -0.0533 |

### 2025-26 (n = 244)

| family | nested difference |
|---|---|
| + nyfed_pd_financing | -0.4% [-3.3%, +2.1%] / -0.0930 |
| + treasury_auction_results | +0.2% [-2.0%, +2.1%] / -0.0525 |
| + nyfed_on_rrp_counterparties | +0.5% [-0.6%, +2.0%] / -0.0149 |
| + treasury_dts_debt_cash | -0.3% [-1.8%, +1.1%] / -0.0502 |

## By lead (mean grid CRPS, bp)

| model | h=1 | h=2 | h=3 | h=4 | h=5 |
|---|---|---|---|---|---|
| B1 as-of persistence | 2.029 | 2.228 | 2.353 | 2.424 | 2.478 |
| B2 calendar climatology | 2.480 | 2.503 | 2.518 | 2.528 | 2.544 |
| candidate (`gbm_funding`) | 1.636 | 1.768 | 1.859 | 1.905 | 1.962 |
| + nyfed_pd_financing | 1.652 | 1.773 | 1.854 | 1.893 | 1.947 |
| + treasury_auction_results | 1.645 | 1.784 | 1.874 | 1.915 | 1.978 |
| + nyfed_on_rrp_counterparties | 1.635 | 1.760 | 1.851 | 1.890 | 1.948 |
| + treasury_dts_debt_cash | 1.648 | 1.785 | 1.881 | 1.917 | 1.981 |
