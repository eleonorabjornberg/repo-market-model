# The latent factor by refit (#543)

## latent_factor, h = 1: 90 refits, 0 on the training-rate fallback

| series | loading min | median | max | sign changes between refits |
|---|---|---|---|---|
| sofr_p1_iorb_bps | 0.360 | 0.473 | 0.632 | 0 |
| sofr_p25_iorb_bps | 0.682 | 0.854 | 0.941 | 0 |
| sofr_p75_iorb_bps | 0.651 | 0.840 | 0.934 | 0 |
| sofr_p99_iorb_bps | 0.516 | 0.743 | 0.852 | 0 |
| tgcr_iorb_bps | 0.682 | 0.855 | 0.942 | 0 |
| bgcr_iorb_bps | 0.682 | 0.855 | 0.942 | 0 |
| effr_iorb_bps | -0.213 | 0.526 | 0.560 | 1 |
| sofr_p99_minus_p1_bps | 0.427 | 0.628 | 0.844 | 0 |
| log1p_on_rrp_bn | -0.387 | -0.252 | 0.448 | 3 |

Persistence phi: min 0.334, median 0.516, max 0.834. Mapping slope (bp per factor unit): 2.277 to 17.206. Most EM iterations in a refit: 100.

## latent_factor_resid, h = 1: 90 refits, 0 on the training-rate fallback

| series | loading min | median | max | sign changes between refits |
|---|---|---|---|---|
| sofr_p1_iorb_bps | 0.360 | 0.473 | 0.632 | 0 |
| sofr_p25_iorb_bps | 0.682 | 0.854 | 0.941 | 0 |
| sofr_p75_iorb_bps | 0.651 | 0.840 | 0.934 | 0 |
| sofr_p99_iorb_bps | 0.516 | 0.743 | 0.852 | 0 |
| tgcr_iorb_bps | 0.682 | 0.855 | 0.942 | 0 |
| bgcr_iorb_bps | 0.682 | 0.855 | 0.942 | 0 |
| effr_iorb_bps | -0.213 | 0.526 | 0.560 | 1 |
| sofr_p99_minus_p1_bps | 0.427 | 0.628 | 0.844 | 0 |
| log1p_on_rrp_bn | -0.387 | -0.252 | 0.448 | 3 |

Persistence phi: min 0.334, median 0.516, max 0.834. Mapping slope (bp per factor unit): 2.277 to 17.206. Most EM iterations in a refit: 100.

## latent_factor_logit, h = 1: 90 refits, 0 on the training-rate fallback

| series | loading min | median | max | sign changes between refits |
|---|---|---|---|---|
| sofr_p1_iorb_bps | 0.360 | 0.473 | 0.632 | 0 |
| sofr_p25_iorb_bps | 0.682 | 0.854 | 0.941 | 0 |
| sofr_p75_iorb_bps | 0.651 | 0.840 | 0.934 | 0 |
| sofr_p99_iorb_bps | 0.516 | 0.743 | 0.852 | 0 |
| tgcr_iorb_bps | 0.682 | 0.855 | 0.942 | 0 |
| bgcr_iorb_bps | 0.682 | 0.855 | 0.942 | 0 |
| effr_iorb_bps | -0.213 | 0.526 | 0.560 | 1 |
| sofr_p99_minus_p1_bps | 0.427 | 0.628 | 0.844 | 0 |
| log1p_on_rrp_bn | -0.387 | -0.252 | 0.448 | 3 |

Persistence phi: min 0.334, median 0.516, max 0.834. Mapping slope (bp per factor unit): 2.277 to 17.206. Most EM iterations in a refit: 100.

## Sign changes of any loading between refits, every horizon and variant

| variant | h | refits | fallback refits | series with a sign change | phi min–max |
|---|---|---|---|---|---|
| latent_factor | 1 | 90 | 0 | effr_iorb_bps, log1p_on_rrp_bn | 0.334–0.834 |
| latent_factor | 2 | 90 | 0 | effr_iorb_bps, log1p_on_rrp_bn | 0.334–0.834 |
| latent_factor | 3 | 90 | 0 | effr_iorb_bps, log1p_on_rrp_bn | 0.334–0.834 |
| latent_factor | 4 | 90 | 0 | effr_iorb_bps, log1p_on_rrp_bn | 0.334–0.834 |
| latent_factor | 5 | 89 | 0 | effr_iorb_bps, log1p_on_rrp_bn | 0.334–0.834 |
| latent_factor_resid | 1 | 90 | 0 | effr_iorb_bps, log1p_on_rrp_bn | 0.334–0.834 |
| latent_factor_resid | 2 | 90 | 0 | effr_iorb_bps, log1p_on_rrp_bn | 0.334–0.834 |
| latent_factor_resid | 3 | 90 | 0 | effr_iorb_bps, log1p_on_rrp_bn | 0.334–0.834 |
| latent_factor_resid | 4 | 90 | 0 | effr_iorb_bps, log1p_on_rrp_bn | 0.334–0.834 |
| latent_factor_resid | 5 | 89 | 0 | effr_iorb_bps, log1p_on_rrp_bn | 0.334–0.834 |
| latent_factor_logit | 1 | 90 | 0 | effr_iorb_bps, log1p_on_rrp_bn | 0.334–0.834 |
| latent_factor_logit | 2 | 90 | 0 | effr_iorb_bps, log1p_on_rrp_bn | 0.334–0.834 |
| latent_factor_logit | 3 | 90 | 0 | effr_iorb_bps, log1p_on_rrp_bn | 0.334–0.834 |
| latent_factor_logit | 4 | 90 | 0 | effr_iorb_bps, log1p_on_rrp_bn | 0.334–0.834 |
| latent_factor_logit | 5 | 89 | 0 | effr_iorb_bps, log1p_on_rrp_bn | 0.334–0.834 |

## The filtered factor at the last anchor before each onset (h = 1)

Mean of the filtered factor over all anchors: -0.107; standard deviation 1.638.

| onset | factor at the last anchor before it |
|---|---|
| 2018-06-29 | 0.475 |
| 2018-11-15 | 0.637 |
| 2018-11-30 | 2.436 |
| 2018-12-17 | 1.099 |
| 2018-12-28 | 2.453 |
| 2019-01-15 | 0.231 |
| 2019-01-31 | -0.138 |
| 2019-02-28 | -0.132 |
| 2019-03-15 | 0.226 |
| 2019-03-29 | 0.739 |
| 2019-05-28 | 0.108 |
| 2019-06-17 | -0.309 |
| 2019-06-25 | 0.738 |
| 2019-08-13 | 0.243 |
| 2019-08-30 | 0.243 |
| 2019-10-15 | 0.039 |
| 2019-11-29 | -0.370 |
| 2019-12-16 | -0.380 |
| 2020-03-04 | 0.129 |
| 2020-03-12 | 0.186 |
| 2024-09-30 | -0.058 |
| 2024-12-26 | 0.639 |
| 2025-09-15 | 0.788 |
| 2025-09-30 | 0.439 |
| 2025-10-15 | 0.955 |
| 2025-12-15 | 0.776 |
| 2025-12-26 | 0.648 |

