# H9 step 3 re-run with aligned training pairs (#932, finding #915)

A measurement on development data for hypothesis **H9** (the secondary goal), step 3, milestone M4. It is not a record and **not a verdict**: development data never gives one (`docs/decisions/scoring-protocol.md` §1). Reading H9's kill clause ("no nested gain for H5") is Eleonora's; this page reads none. Nothing is published, no target joins any published declaration, nothing is written into `docs/runs/`, and no day after 2025-12-31 is read (`docs/decisions/lockbox.md`). Every choice is in `metadata/h9_nested_932.json`, committed before any score. #842's page (`docs/pivot/h9-nested-842-result.md`) stands unedited.

**What changed.** #842's plus walks fitted on one-step pairs: at a lead h >= 2 the model learned the forecast of T for day p + h against the spread of day p + 1, and was served the forecast for the day it predicts. Here the plus walks, and the `base_direct` walks they are compared with, are fitted on direct pairs (`training_pairs="direct"`): each label day t is paired with the row its own forecast reads, whose column is the forecast of T for day t. The candidate, the targets' forecasts, the panel, the days and the interval are #842's. `base` is #842's candidate on one-step pairs, re-walked.

Decision days: 1848 (2018-07-30 to 2025-12-23). Intervals: studentized stationary bootstrap, block 10, 10000 draws, seed 932, one-sided 95%. `d = S(base_direct) − S(plus_direct)`; positive favours the target's forecast; skill = mean(d) / mean(S(base_direct)).

## Nested difference on the primary score (grid CRPS, mean over leads 1 to 5), pairing held fixed

| target | CRPS base_direct | CRPS with target | d, all days | skill (lower 95%) | Holm p | d, without 2019-09-18 | Holm p, without |
|---|---|---|---|---|---|---|---|
| `bgcr_dispersion_bps` | 1.930 | 1.926 | +0.003 (lower -0.011) | +0.002 (lower -0.006) | 1.000 | +0.003 (lower -0.011) | 1.000 |
| `on_rrp_change_bn` | 1.930 | 1.932 | -0.002 (lower -0.011) | -0.001 (lower -0.006) | 1.000 | -0.002 (lower -0.011) | 1.000 |
| `sofr_dispersion_bps` | 1.930 | 1.942 | -0.012 (lower -0.025) | -0.006 (lower -0.014) | 1.000 | -0.012 (lower -0.026) | 1.000 |

## Beside #856's figures (misaligned pairs; its base was the one-step candidate)

#856's decision days: 1848. Its figures are read from `docs/pivot/evidence/h9-nested-842/score.json`, unedited. The last two columns of this page's table are the same comparison as #856's (the one-step base against the plus walk), now with the plus walk aligned.

| target | #856: skill (lower), all days | #856: without 2019-09-18 | here, aligned plus vs one-step `base`: skill (lower) | here, vs `base_direct`: skill (lower) |
|---|---|---|---|---|
| `bgcr_dispersion_bps` | -0.002 (lower -0.015) | -0.002 (lower -0.015) | -0.056 (lower -0.104) | +0.002 (lower -0.006) |
| `on_rrp_change_bn` | -0.000 (lower -0.009) | -0.000 (lower -0.009) | -0.059 (lower -0.106) | -0.001 (lower -0.006) |
| `sofr_dispersion_bps` | +0.003 (lower -0.005) | +0.003 (lower -0.004) | -0.064 (lower -0.111) | -0.006 (lower -0.014) |

The pairing alone, with no input added (`base` against `base_direct`): skill -0.058 (lower -0.105). A gain of an aligned plus walk over the one-step base is the pairing and the input together; the like-for-like column separates the input.

## Against the benchmarks (skill over B1 and over B2, lower 95% bound)

| model | over B1 | over B2 |
|---|---|---|
| `base` | +0.204 (lower +0.130) | +0.274 (lower +0.175) |
| `base_direct` | +0.158 (lower +0.065) | +0.232 (lower +0.139) |
| `plus_direct_bgcr_dispersion_bps` | +0.160 (lower +0.066) | +0.233 (lower +0.141) |
| `plus_direct_on_rrp_change_bn` | +0.157 (lower +0.063) | +0.231 (lower +0.140) |
| `plus_direct_sofr_dispersion_bps` | +0.153 (lower +0.059) | +0.227 (lower +0.136) |

## Nested difference by split, pairing held fixed (d, lower 95% bound; days in brackets)

| split | `bgcr_dispersion_bps` | `on_rrp_change_bn` | `sofr_dispersion_bps` |
|---|---|---|---|
| lead:1 (1848) | -0.006 (lower -0.025) | -0.003 (lower -0.015) | -0.017 (lower -0.029) |
| lead:1 without_2019-09-18 (1847) | -0.006 (lower -0.024) | -0.002 (lower -0.014) | -0.017 (lower -0.028) |
| lead:2 (1848) | +0.007 (lower -0.013) | -0.003 (lower -0.017) | -0.033 (lower -0.053) |
| lead:2 without_2019-09-18 (1847) | +0.007 (lower -0.013) | -0.003 (lower -0.017) | -0.033 (lower -0.052) |
| lead:3 (1848) | +0.000 (lower -0.022) | +0.006 (lower -0.010) | -0.015 (lower -0.037) |
| lead:3 without_2019-09-18 (1847) | +0.000 (lower -0.022) | +0.006 (lower -0.010) | -0.015 (lower -0.037) |
| lead:4 (1848) | +0.003 (lower -0.021) | -0.003 (lower -0.019) | -0.007 (lower -0.025) |
| lead:4 without_2019-09-18 (1847) | +0.003 (lower -0.021) | -0.004 (lower -0.020) | -0.007 (lower -0.025) |
| lead:5 (1848) | +0.013 (lower -0.009) | -0.008 (lower -0.030) | +0.012 (lower -0.012) |
| lead:5 without_2019-09-18 (1847) | +0.013 (lower -0.009) | -0.008 (lower -0.031) | +0.012 (lower -0.013) |
| regime:2018-19 (355) | +0.012 (lower -0.048) | +0.017 (lower -0.006) | +0.019 (lower -0.037) |
| regime:2018-19 without_2019-09-18 (354) | +0.012 (lower -0.047) | +0.017 (lower -0.006) | +0.019 (lower -0.037) |
| regime:2020 (251) | +0.019 (lower +0.002) | -0.015 (lower -0.033) | +0.004 (lower -0.021) |
| regime:2021-23 (748) | -0.004 (lower -0.025) | -0.019 (lower -0.027) | -0.022 (lower -0.038) |
| regime:2024 (250) | +0.012 (lower -0.006) | +0.023 (lower +0.005) | -0.010 (lower -0.028) |
| regime:2025-26 (244) | -0.011 (lower -0.042) | +0.009 (lower -0.038) | -0.043 (lower -0.085) |
| state:ample (1359) | +0.002 (lower -0.011) | -0.005 (lower -0.014) | -0.019 (lower -0.031) |
| state:scarce (489) | +0.006 (lower -0.035) | +0.007 (lower -0.019) | +0.008 (lower -0.034) |
| state:scarce without_2019-09-18 (488) | +0.006 (lower -0.035) | +0.006 (lower -0.020) | +0.008 (lower -0.034) |
| type:month_end (502) | -0.014 (lower -0.044) | -0.016 (lower -0.054) | -0.038 (lower -0.071) |
| type:ordinary (1848) | +0.006 (lower -0.008) | -0.000 (lower -0.009) | -0.009 (lower -0.022) |
| type:ordinary without_2019-09-18 (1847) | +0.006 (lower -0.008) | -0.000 (lower -0.010) | -0.009 (lower -0.022) |
| type:quarter_end (146) | +0.027 (lower -0.103) | -0.029 (lower -0.114) | +0.005 (lower -0.070) |
| type:tax_date (214) | -0.026 (lower -0.088) | +0.014 (lower -0.025) | +0.005 (lower -0.034) |

## Upper-tail twCRPS (weight 1{y > 0 bp}): d, lower 95% bound

| target | all days | without 2019-09-18 |
|---|---|---|
| `bgcr_dispersion_bps` | +0.000 (lower -0.009) | +0.000 (lower -0.008) |
| `on_rrp_change_bn` | +0.001 (lower -0.005) | +0.001 (lower -0.005) |
| `sofr_dispersion_bps` | +0.003 (lower -0.005) | +0.003 (lower -0.005) |

## Reproduction of the candidate

`base` re-walks #634's `gbm_funding`: grid CRPS 1.8298 on 1869 days here; 1.8261 on 1868 days recorded in `docs/pivot/evidence/spread-distribution-protocol/score.json`. On the days every walk covers the base reads 1.8245.

## Readings (development data, not a verdict; reading H9's kill clause is Eleonora's)

* `bgcr_dispersion_bps`: on the like-for-like pairing its forecast does not improve the candidate beyond its interval (skill +0.002, lower bound of d -0.011); without 2019-09-18 it does not improve it. Split cells read: 14; cells showing a gain: regime:2020.
* `on_rrp_change_bn`: on the like-for-like pairing its forecast does not improve the candidate beyond its interval (skill -0.001, lower bound of d -0.011); without 2019-09-18 it does not improve it. Split cells read: 14; cells showing a gain: regime:2024.
* `sofr_dispersion_bps`: on the like-for-like pairing its forecast does not improve the candidate beyond its interval (skill -0.006, lower bound of d -0.025); without 2019-09-18 it does not improve it. Split cells read: 14; cells showing a gain: none.
