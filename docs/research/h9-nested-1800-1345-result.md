# H9 step 3: the nested test on (s3c-ann-net), made at 18:00 (#1345)

**Development data, not a verdict** (scoring protocol v1). H9's kill clause is not read here; reading it is Eleonora's.

- Window: development (targets to 2025-12-31); decision instant 18:00; seed 1345.
- Published panel `4ddc3882...`; scratch panel (18:00) `0967f5c0...`.
- d = S(base) - S(base + target); positive favours the target's forecast. Cells: mean d [one-sided 95% lower bound], skill.

## Pooled, all decision days (1855 decision days)

| target | grid CRPS | upper-tail twCRPS | reading (grid CRPS) |
|---|---|---|---|
| bgcr_dispersion_bps | -0.0180 [-0.0402], skill -0.011 | -0.0081 [-0.0188], skill -0.010 | no improvement beyond its interval |
| on_rrp_change_bn | -0.0002 [-0.0010], skill -0.000 | -0.0000 [-0.0001], skill -0.000 | no improvement beyond its interval |
| sofr_dispersion_bps | -0.0177 [-0.0348], skill -0.011 | -0.0072 [-0.0177], skill -0.009 | no improvement beyond its interval |

## Pooled, excluding 2019-09-18 (1854 decision days)

| target | grid CRPS | upper-tail twCRPS | reading (grid CRPS) |
|---|---|---|---|
| bgcr_dispersion_bps | -0.0181 [-0.0405], skill -0.011 | -0.0081 [-0.0193], skill -0.010 | no improvement beyond its interval |
| on_rrp_change_bn | -0.0002 [-0.0010], skill -0.000 | -0.0000 [-0.0001], skill -0.000 | no improvement beyond its interval |
| sofr_dispersion_bps | -0.0180 [-0.0359], skill -0.011 | -0.0076 [-0.0183], skill -0.009 | no improvement beyond its interval |

## Holm across the targets (pooled, grid CRPS)

| group | target | p | Holm p |
|---|---|---|---|
| all decision days | bgcr_dispersion_bps | 0.982 | 1.000 |
| all decision days | on_rrp_change_bn | 0.721 | 1.000 |
| all decision days | sofr_dispersion_bps | 0.990 | 1.000 |
| excluding 2019-09-18 | bgcr_dispersion_bps | 0.982 | 1.000 |
| excluding 2019-09-18 | on_rrp_change_bn | 0.721 | 1.000 |
| excluding 2019-09-18 | sofr_dispersion_bps | 0.991 | 1.000 |

## By lead (grid CRPS)

| group | days | bgcr_dispersion_bps | on_rrp_change_bn | sofr_dispersion_bps |
|---|---|---|---|---|
| h=1 | 1855 | -0.0036 [-0.0135], skill -0.002 | -0.0001 [-0.0004], skill -0.000 | -0.0017 [-0.0093], skill -0.001 |
| h=1 (excluding 2019-09-18) | 1854 | -0.0037 [-0.0136], skill -0.003 | -0.0001 [-0.0004], skill -0.000 | -0.0025 [-0.0103], skill -0.002 |
| h=2 | 1855 | -0.0104 [-0.0261], skill -0.007 | -0.0003 [-0.0014], skill -0.000 | -0.0072 [-0.0218], skill -0.005 |
| h=2 (excluding 2019-09-18) | 1854 | -0.0103 [-0.0264], skill -0.007 | -0.0003 [-0.0015], skill -0.000 | -0.0075 [-0.0224], skill -0.005 |
| h=3 | 1855 | -0.0180 [-0.0419], skill -0.011 | +0.0001 [-0.0009], skill +0.000 | -0.0150 [-0.0347], skill -0.009 |
| h=3 (excluding 2019-09-18) | 1854 | -0.0181 [-0.0420], skill -0.011 | +0.0001 [-0.0009], skill +0.000 | -0.0158 [-0.0359], skill -0.010 |
| h=4 | 1855 | -0.0259 [-0.0545], skill -0.016 | -0.0004 [-0.0022], skill -0.000 | -0.0255 [-0.0546], skill -0.015 |
| h=4 (excluding 2019-09-18) | 1854 | -0.0259 [-0.0549], skill -0.016 | -0.0004 [-0.0022], skill -0.000 | -0.0257 [-0.0561], skill -0.016 |
| h=5 | 1855 | -0.0323 [-0.0844], skill -0.019 | -0.0004 [-0.0013], skill -0.000 | -0.0389 [-0.0899], skill -0.023 |
| h=5 (excluding 2019-09-18) | 1854 | -0.0323 [-0.0849], skill -0.019 | -0.0004 [-0.0013], skill -0.000 | -0.0387 [-0.0920], skill -0.023 |

## By regime (grid CRPS)

| group | days | bgcr_dispersion_bps | on_rrp_change_bn | sofr_dispersion_bps |
|---|---|---|---|---|
| 2018-19 | 361 | -0.0437 [-0.1163], skill -0.012 | -0.0000 [-0.0000], skill -0.000 | -0.0440 [-0.1120], skill -0.012 |
| 2020 | 251 | -0.0124 [-0.0500], skill -0.008 | -0.0000 [-0.0001], skill -0.000 | -0.0350 [-0.1554], skill -0.024 |
| 2021-23 | 748 | -0.0191 [-0.0861], skill -0.030 | +0.0000 [-0.0013], skill +0.000 | -0.0071 [-0.0296], skill -0.011 |
| 2024 | 250 | +0.0011 [-0.0018], skill +0.001 | +0.0011 [-0.0016], skill +0.001 | +0.0016 [-0.0035], skill +0.001 |
| 2025-26 | 249 | -0.0031 [-0.0264], skill -0.001 | -0.0028 [-0.0065], skill -0.001 | -0.0136 [-0.0471], skill -0.006 |

## By pressure day type (grid CRPS)

| group | days | bgcr_dispersion_bps | on_rrp_change_bn | sofr_dispersion_bps |
|---|---|---|---|---|
| ordinary | 1591 | -0.0191 [-0.0462], skill -0.015 | -0.0007 [-0.0014], skill -0.001 | -0.0155 [-0.0339], skill -0.012 |
| quarter_end_turn | 44 | -0.0535 [-0.1261], skill -0.015 | +0.0048 [-0.0009], skill +0.001 | -0.0780 [-0.2551], skill -0.022 |
| tax_date | 89 | +0.0233 [-0.0247], skill +0.005 | +0.0029 [+0.0007], skill +0.001 | -0.0188 [-0.1344], skill -0.004 |
| turn | 120 | -0.0401 [-0.0913], skill -0.024 | +0.0009 [-0.0005], skill +0.001 | -0.0277 [-0.0628], skill -0.016 |
| year_end | 15 | n/a | n/a | n/a |

## The forecast in the fit

| arm | lead | share of cells with the term in the fit | mean effect (bp per unit) |
|---|---|---|---|
| (s3c-ann-net) + bgcr_dispersion_bps | 1 | 0.966 | -0.0255 |
| (s3c-ann-net) + bgcr_dispersion_bps | 2 | 0.966 | -0.0503 |
| (s3c-ann-net) + bgcr_dispersion_bps | 3 | 0.966 | -0.0526 |
| (s3c-ann-net) + bgcr_dispersion_bps | 4 | 0.966 | -0.0158 |
| (s3c-ann-net) + bgcr_dispersion_bps | 5 | 0.966 | +0.0022 |
| (s3c-ann-net) + on_rrp_change_bn | 1 | 0.966 | -0.0657 |
| (s3c-ann-net) + on_rrp_change_bn | 2 | 0.966 | -0.1571 |
| (s3c-ann-net) + on_rrp_change_bn | 3 | 0.966 | -0.2442 |
| (s3c-ann-net) + on_rrp_change_bn | 4 | 0.966 | -0.2895 |
| (s3c-ann-net) + on_rrp_change_bn | 5 | 0.966 | -0.0321 |
| (s3c-ann-net) + sofr_dispersion_bps | 1 | 0.966 | -0.0753 |
| (s3c-ann-net) + sofr_dispersion_bps | 2 | 0.966 | -0.1295 |
| (s3c-ann-net) + sofr_dispersion_bps | 3 | 0.966 | -0.1399 |
| (s3c-ann-net) + sofr_dispersion_bps | 4 | 0.966 | -0.0183 |
| (s3c-ann-net) + sofr_dispersion_bps | 5 | 0.966 | +0.0177 |

## Target walks read

```json
{
 "bgcr_dispersion_bps": {
  "forecasts": {
   "1": 1873,
   "2": 1872,
   "3": 1871,
   "4": 1870,
   "5": 1869
  },
  "leads": [
   1,
   2,
   3,
   4,
   5
  ]
 },
 "on_rrp_change_bn": {
  "forecasts": {
   "1": 1872,
   "2": 1871,
   "3": 1870,
   "4": 1869,
   "5": 1868
  },
  "leads": [
   1,
   2,
   3,
   4,
   5
  ]
 },
 "sofr_dispersion_bps": {
  "forecasts": {
   "1": 1873,
   "2": 1872,
   "3": 1871,
   "4": 1870,
   "5": 1869
  },
  "leads": [
   1,
   2,
   3,
   4,
   5
  ]
 }
}
```
