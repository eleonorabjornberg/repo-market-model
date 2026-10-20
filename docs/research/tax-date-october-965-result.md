# 15 October as a tax date (#965; H5 step 2, H6 step 1, H8)

**Development data, not a verdict.** No verdict, no lockbox day scored (decision days with all targets on or before 2025-12-31), and no published declaration, record or decided value moves. Every figure is read from `docs/research/tax-date-october-965/result.json` by `scripts/tax_date_october_965.py report`. The declaration, `metadata/tax_date_october_965.json`, was committed before any number was computed.

**Questions for Eleonora (not settled here).** (1) Adopt 15 October in the `tax_date` definition? The definition is a data meaning (as #538 was), and adopting it for B2 is a section 13 question. (2) If the coupon control below matches the October result, should the label be a coupon-settlement label and not a tax-date label?

## What was measured

The alternative adds the 15th of October (rolled forward off weekends and DC holidays) and the two market days after it to the `tax_date` type (`repo_model.tax_date_october`); the published column is not changed. The control adds, in the same shape, the 15th of the months the published column leaves alone (January, February, March, May, July, August, November), rolled on the market calendar, so that a gain in October that the control also shows is the mid-month coupon settlement and not the tax deadline. B2 and H8's calendar ranker are unchanged apart from that label. Skill is mean(d) / mean(S(benchmark)) with d = S(benchmark) − S(candidate), positive favouring the candidate; the 90% interval is the studentized stationary bootstrap of ruling 1 (#739), seed 965, 10,000 draws. A group of fewer than 20 decision days is listed and not tested. By target group, a decision day's score is its mean over the leads whose target is in the group.

## The windows as a calendar (no score)

| target days to the last scored day | panel days | pressure days (> +5 bp) | mean spread (bp) | median (bp) |
|---|---|---|---|---|
| october window | 24 | 5 | -0.75 | -3.00 |
| control window | 159 | 14 | -4.47 | -8.00 |
| tax_date as is | 95 | 14 | -0.51 | -7.00 |
| other days | 1657 | 129 | -4.80 | -7.00 |

The October window by year (SOFR − IORB, bp):

- 2018: 2018-10-15 +1.0, 2018-10-16 -2.0, 2018-10-17 -2.0
- 2019: 2019-10-15 +20.0, 2019-10-16 +25.0, 2019-10-17 +15.0
- 2020: 2020-10-15 +0.0, 2020-10-16 -1.0, 2020-10-19 -1.0
- 2021: 2021-10-15 -10.0, 2021-10-18 -10.0, 2021-10-19 -12.0
- 2022: 2022-10-17 -10.0, 2022-10-18 -11.0, 2022-10-19 -11.0
- 2023: 2023-10-16 -9.0, 2023-10-17 -9.0, 2023-10-18 -10.0
- 2024: 2024-10-15 -4.0, 2024-10-16 -4.0, 2024-10-17 -5.0
- 2025: 2025-10-15 +14.0, 2025-10-16 +15.0, 2025-10-17 +3.0

A coupon settlement was positive on the deadline day for 8 of 8 October deadlines and for 53 of 53 control deadlines (`treasury_settlement_coupons` on the rolled 15th).

## (a) B2 with the alternative label against B2 as is

1908 decision days (2018-04-18 to 2025-12-23); 22 dropped for want of a sample of some lead's type in the trailing year, from every model.

### grid CRPS: B2 october against B2 as is (skill of B2 october)

| group | decision days | benchmark | candidate | skill [90%] | mean d [90%] | reading |
|---|---|---|---|---|---|---|
| pooled | 1908 | 2.511 | 2.505 | +0.3% [-0.2, +1.1] | +0.0064 [-0.0056, +0.0275] | no difference |
| regime 2018-19 | 415 | 4.170 | 4.144 | +0.6% [-0.3, +4.8] | +0.0261 [-0.0129, +0.1729] | no difference |
| regime 2020 | 251 | 2.786 | 2.798 | -0.4% [-2.0, +0.6] | -0.0116 [-0.0595, +0.0176] | no difference |
| regime 2021-23 | 748 | 1.481 | 1.480 | +0.1% [-0.6, +0.6] | +0.0013 [-0.0089, +0.0092] | no difference |
| regime 2024 | 250 | 1.378 | 1.375 | +0.2% [-0.1, +0.7] | +0.0030 [-0.0019, +0.0111] | no difference |
| regime 2025-26 | 244 | 3.724 | 3.713 | +0.3% [-1.0, +3.5] | +0.0107 [-0.0336, +0.1082] | no difference |
| target: control window | 371 | 1.991 | 1.989 | +0.1% [-0.7, +0.6] | +0.0017 [-0.0129, +0.0106] | no difference |
| target: october window | 56 | 4.010 | 3.341 | +16.7% [+2.8, +36.6] | +0.6697 [-0.1871, +2.6345] | candidate better |
| target: other days | 1908 | 2.176 | 2.171 | +0.2% [-0.3, +0.5] | +0.0048 [-0.0052, +0.0109] | no difference |
| target: tax_date as is | 222 | 7.052 | 7.171 | -1.7% [-4.7, +1.2] | -0.1188 [-0.3883, +0.1664] | no difference |

### grid CRPS: B2 control against B2 as is (skill of B2 control)

| group | decision days | benchmark | candidate | skill [90%] | mean d [90%] | reading |
|---|---|---|---|---|---|---|
| pooled | 1908 | 2.511 | 2.488 | +0.9% [+0.1, +2.0] | +0.0229 [+0.0024, +0.0491] | candidate better |
| regime 2018-19 | 415 | 4.170 | 4.124 | +1.1% [-0.4, +3.6] | +0.0459 [-0.0107, +0.1362] | no difference |
| regime 2020 | 251 | 2.786 | 2.717 | +2.5% [-1.2, +6.5] | +0.0695 [-0.0361, +0.2134] | no difference |
| regime 2021-23 | 748 | 1.481 | 1.474 | +0.5% [-0.6, +1.8] | +0.0069 [-0.0091, +0.0262] | no difference |
| regime 2024 | 250 | 1.378 | 1.374 | +0.3% [-0.9, +1.3] | +0.0040 [-0.0105, +0.0177] | no difference |
| regime 2025-26 | 244 | 3.724 | 3.719 | +0.1% [-1.3, +1.3] | +0.0046 [-0.0443, +0.0474] | no difference |
| target: control window | 371 | 1.991 | 2.066 | -3.8% [-17.5, +9.5] | -0.0756 [-0.3131, +0.1907] | no difference |
| target: october window | 56 | 4.010 | 3.997 | +0.3% [-1.8, +2.6] | +0.0132 [-0.0273, +0.0845] | no difference |
| target: other days | 1908 | 2.176 | 2.177 | -0.0% [-0.7, +0.6] | -0.0008 [-0.0142, +0.0120] | no difference |
| target: tax_date as is | 222 | 7.052 | 6.437 | +8.7% [-3.3, +18.7] | +0.6149 [+0.2389, +1.1786] | no difference |

### grid CRPS: B2 as is against B1, for the size of the gap

| group | decision days | benchmark | candidate | skill [90%] | mean d [90%] | reading |
|---|---|---|---|---|---|---|
| pooled | 1908 | 2.314 | 2.511 | -8.5% [-28.5, +21.6] | -0.1969 [-0.5338, +0.4597] | no difference |
| regime 2018-19 | 415 | 5.450 | 4.170 | +23.5% [+6.8, +56.9] | +1.2801 [+0.1470, +5.9074] | candidate better |
| regime 2020 | 251 | 1.644 | 2.786 | -69.5% [-176.7, +5.7] | -1.1422 [-2.8499, -0.2730] | no difference |
| regime 2021-23 | 748 | 0.711 | 1.481 | -108.4% [-168.7, -63.7] | -0.7703 [-1.1315, -0.4878] | candidate worse |
| regime 2024 | 250 | 1.683 | 1.378 | +18.1% [+1.3, +37.7] | +0.3051 [+0.0172, +0.9449] | candidate better |
| regime 2025-26 | 244 | 3.231 | 3.724 | -15.3% [-51.9, +9.4] | -0.4931 [-1.7796, +0.3249] | no difference |
| target: control window | 371 | 1.484 | 1.991 | -34.1% [-64.4, -9.7] | -0.5065 [-0.8572, -0.2248] | candidate worse |
| target: october window | 56 | 3.191 | 4.010 | -25.7% [-44.1, -3.0] | -0.8194 [-1.9260, -0.3307] | candidate worse |
| target: other days | 1908 | 2.057 | 2.176 | -5.8% [-26.6, +26.7] | -0.1192 [-0.4537, +0.5632] | no difference |
| target: tax_date as is | 222 | 4.787 | 7.052 | -47.3% [-119.5, +54.0] | -2.2657 [-3.7119, -1.3712] | no difference |

### upper-tail twCRPS: B2 october against B2 as is (skill of B2 october)

| group | decision days | benchmark | candidate | skill [90%] | mean d [90%] | reading |
|---|---|---|---|---|---|---|
| pooled | 1908 | 1.113 | 1.109 | +0.3% [-0.6, +2.3] | +0.0034 [-0.0070, +0.0235] | no difference |
| regime 2018-19 | 415 | 3.388 | 3.362 | +0.8% [-0.5, +6.4] | +0.0257 [-0.0129, +0.1802] | no difference |
| regime 2020 | 251 | 1.201 | 1.218 | -1.4% [-5.5, +1.2] | -0.0164 [-0.0679, +0.0141] | no difference |
| regime 2021-23 | 748 | 0.002 | 0.002 | -4.4% [-6.7, -2.7] | -0.0001 [-0.0002, -0.0000] | candidate worse |
| regime 2024 | 250 | 0.196 | 0.196 | undefined: a resampled benchmark scores zero; skill is undefined | -0.0000 | undefined |
| regime 2025-26 | 244 | 1.496 | 1.495 | +0.0% [-2.2, +5.3] | +0.0002 [-0.0310, +0.0405] | no difference |
| target: control window | 371 | 0.963 | 0.963 | +0.1% [-1.0, +0.9] | +0.0008 [-0.0091, +0.0072] | no difference |
| target: october window | 56 | 2.744 | 2.167 | undefined: a resampled skill has no long-run variance; it cannot be studentized | +0.5777 [+0.0471, +1.2078] (percentile, unstudentized) | undefined |
| target: other days | 1908 | 0.795 | 0.791 | +0.5% [-0.5, +1.2] | +0.0041 [-0.0031, +0.0086] | no difference |
| target: tax_date as is | 222 | 4.917 | 5.065 | -3.0% [-8.8, +1.7] | -0.1476 [-0.4411, +0.0457] | no difference |

### upper-tail twCRPS: B2 control against B2 as is (skill of B2 control)

| group | decision days | benchmark | candidate | skill [90%] | mean d [90%] | reading |
|---|---|---|---|---|---|---|
| pooled | 1908 | 1.113 | 1.097 | +1.4% [-0.3, +3.7] | +0.0152 [-0.0023, +0.0394] | no difference |
| regime 2018-19 | 415 | 3.388 | 3.352 | +1.0% [-0.6, +4.2] | +0.0355 [-0.0171, +0.1291] | no difference |
| regime 2020 | 251 | 1.201 | 1.143 | +4.8% [-3.6, +13.6] | +0.0578 [-0.0398, +0.1948] | no difference |
| regime 2021-23 | 748 | 0.002 | 0.003 | -39.9% [-88.2, -13.8] | -0.0009 [-0.0032, -0.0002] | candidate worse |
| regime 2024 | 250 | 0.196 | 0.196 | undefined: a resampled benchmark scores zero; skill is undefined | +0.0001 | undefined |
| regime 2025-26 | 244 | 1.496 | 1.494 | +0.1% [-3.6, +0.8] | +0.0019 [-0.0196, +0.0119] | no difference |
| target: control window | 371 | 0.963 | 0.995 | -3.3% [-30.9, +14.6] | -0.0314 [-0.2192, +0.1635] | no difference |
| target: october window | 56 | 2.744 | 2.749 | -0.2% [-2.5, +1.2] | -0.0046 [-0.0420, +0.0130] | no difference |
| target: other days | 1908 | 0.795 | 0.798 | -0.3% [-1.1, +0.4] | -0.0027 [-0.0100, +0.0029] | no difference |
| target: tax_date as is | 222 | 4.917 | 4.507 | +8.3% [-11.7, +27.0] | +0.4099 [+0.0802, +1.4036] | no difference |

### upper-tail twCRPS: B2 as is against B1, for the size of the gap

| group | decision days | benchmark | candidate | skill [90%] | mean d [90%] | reading |
|---|---|---|---|---|---|---|
| pooled | 1908 | 1.367 | 1.113 | +18.6% [+1.4, +49.4] | +0.2543 [-0.0009, +1.1469] | candidate better |
| regime 2018-19 | 415 | 4.733 | 3.388 | +28.4% [+11.2, +61.7] | +1.3454 [+0.2201, +6.6277] | candidate better |
| regime 2020 | 251 | 0.741 | 1.201 | -62.2% [-209.4, +110.2] | -0.4605 [-0.8484, +0.1197] | no difference |
| regime 2021-23 | 748 | 0.008 | 0.002 | +72.1% [+59.2, +89.2] | +0.0056 [+0.0022, +0.0242] | candidate better |
| regime 2024 | 250 | 0.322 | 0.196 | undefined: a resampled skill has no long-run variance; it cannot be studentized | +0.1254 [+0.0018, +0.2742] (percentile, unstudentized) | undefined |
| regime 2025-26 | 244 | 1.524 | 1.496 | +1.8% [-39.0, +21.4] | +0.0282 [-0.4203, +0.3005] | no difference |
| target: control window | 371 | 0.818 | 0.963 | -17.8% [-46.7, +4.2] | -0.1457 [-0.4244, -0.0021] | no difference |
| target: october window | 56 | 2.472 | 2.744 | -11.0% [-18.0, +2.2] | -0.2721 [-0.6962, -0.0370] | no difference |
| target: other days | 1908 | 1.115 | 0.795 | +28.6% [+6.4, +66.1] | +0.3191 [+0.0582, +1.2656] | candidate better |
| target: tax_date as is | 222 | 3.914 | 4.917 | -25.6% [-77.1, +16.7] | -1.0037 [-2.7755, -0.2458] | no difference |

## (b) H8's calendar ranker with the window in its set

1893 decision days (2018-04-18 to 2025-12-02), 20 leads each; precision over all windows and recall over the 473 windows with a pressure day; ties broken by date; mean block 20; the gain is the alternative's less the ranker as is (positive favours the alternative). The studentized scorer is used where it is defined, the percentile interval of the same draws otherwise.

### Calendar ranker with the october window against as is

| group | decision days | precision@3 gain [90%] | recall@3 gain [90%] | precision@5 gain [90%] | recall@5 gain [90%] |
|---|---|---|---|---|---|
| other windows | 595 (pressure: 165) | identical (0.134) | identical (0.311) | identical (0.123) | identical (0.498) |
| pooled | 1893 (pressure: 473) | +0.010 [+0.000, +0.022] candidate better | +0.015 [-0.004, +0.035] no difference | +0.006 [+0.000, +0.014] candidate better | +0.016 [-0.001, +0.036] no difference |
| regime 2018-19 | 415 (pressure: 326) | +0.023 [+0.000, +0.063] no difference | +0.010 [+0.000, +0.025] no difference | +0.016 [+0.000, +0.042] no difference | +0.011 [+0.000, +0.028] no difference |
| regime 2020 | 251 (pressure: 29) | identical (0.012) | identical (0.135) | identical (0.014) | identical (0.227) |
| regime 2021-23 | 748 (pressure: 0) | identical (0.000) | fewer than 20 days; not tested | identical (0.000) | fewer than 20 days; not tested |
| regime 2024 | 250 (pressure: 44) | -0.004 [-0.011, +0.000] no difference | -0.045 [-0.091, +0.000] no difference | -0.002 [-0.006, +0.000] no difference | -0.034 [-0.068, +0.000] no difference |
| regime 2025-26 | 229 (pressure: 74) | +0.048 [+0.000, +0.115] no difference | +0.076 [+0.003, +0.153] candidate better | +0.026 [+0.000, +0.064] no difference | +0.074 [+0.000, +0.152] no difference |
| windows holding a control window day | 1127 (pressure: 253) | identical (0.082) | identical (0.210) | identical (0.074) | identical (0.297) |
| windows holding an October window day | 176 (pressure: 55) | +0.112 [+0.021, +0.208] candidate better | +0.125 [+0.061, +0.188] candidate better | +0.068 [+0.011, +0.128] candidate better | +0.138 [+0.065, +0.209] candidate better |

### Calendar ranker with the control window against as is

| group | decision days | precision@3 gain [90%] | recall@3 gain [90%] | precision@5 gain [90%] | recall@5 gain [90%] |
|---|---|---|---|---|---|
| other windows | 595 (pressure: 165) | identical (0.134) | identical (0.311) | identical (0.123) | identical (0.498) |
| pooled | 1893 (pressure: 473) | +0.010 [-0.002, +0.024] no difference | +0.041 [-0.004, +0.093] no difference | +0.007 [-0.000, +0.015] no difference | +0.039 [-0.004, +0.088] no difference |
| regime 2018-19 | 415 (pressure: 326) | +0.042 [+0.001, +0.088] candidate better | +0.042 [-0.013, +0.109] no difference | +0.029 [+0.007, +0.054] candidate better | +0.045 [-0.008, +0.108] no difference |
| regime 2020 | 251 (pressure: 29) | +0.039 [+0.000, +0.093] no difference | +0.287 [+0.170, +0.408] candidate better | +0.021 [+0.000, +0.050] no difference | +0.244 [+0.129, +0.362] candidate better |
| regime 2021-23 | 748 (pressure: 0) | identical (0.000) | fewer than 20 days; not tested | identical (0.000) | fewer than 20 days; not tested |
| regime 2024 | 250 (pressure: 44) | -0.004 [-0.012, +0.000] no difference | -0.023 [-0.045, +0.000] no difference | -0.005 [-0.014, +0.000] no difference | -0.045 [-0.091, +0.000] no difference |
| regime 2025-26 | 229 (pressure: 74) | -0.028 [-0.068, +0.000] no difference | -0.023 [-0.047, -0.002] candidate worse | -0.013 [-0.033, +0.000] no difference | -0.018 [-0.038, +0.000] no difference |
| windows holding a control window day | 1127 (pressure: 253) | +0.017 [-0.004, +0.042] no difference | +0.076 [-0.001, +0.162] no difference | +0.012 [-0.001, +0.026] no difference | +0.072 [-0.001, +0.153] no difference |
| windows holding an October window day | 176 (pressure: 55) | identical (0.125) | identical (0.255) | identical (0.112) | identical (0.332) |

## What the tables show

- (grid CRPS) pooled, B2 october against B2 as is: skill +0.3% [-0.2, +1.1], no difference.
- (grid CRPS) on its own window, B2 october against B2 as is: skill +16.7% [+2.8, +36.6], candidate better.
- (grid CRPS) pooled, B2 control against B2 as is: skill +0.9% [+0.1, +2.0], candidate better.
- (grid CRPS) on its own window, B2 control against B2 as is: skill -3.8% [-17.5, +9.5], no difference.
- (upper-tail twCRPS) pooled, B2 october against B2 as is: skill +0.3% [-0.6, +2.3], no difference.
- (upper-tail twCRPS) on its own window, B2 october against B2 as is: undefined.
- (upper-tail twCRPS) pooled, B2 control against B2 as is: skill +1.4% [-0.3, +3.7], no difference.
- (upper-tail twCRPS) on its own window, B2 control against B2 as is: skill -3.3% [-30.9, +14.6], no difference.
- The October window holds a pressure day (> +5 bp) in 2 of its 8 years (2019, 2025); its gain rests on those years.
- (b) pooled, calendar ranker october against as is, precision@5: gain +0.0063 [+0.0001, +0.0136], candidate better.
- (b) pooled, calendar ranker october against as is, recall@5: gain +0.0160 [-0.0014, +0.0364], no difference.
- (b) pooled, calendar ranker control against as is, precision@5: gain +0.0070 [-0.0002, +0.0148], no difference.
- (b) pooled, calendar ranker control against as is, recall@5: gain +0.0387 [-0.0035, +0.0884], no difference.

Nothing here is a verdict for a hypothesis; adopting the label is Eleonora's (#965). Development data, not a verdict.
