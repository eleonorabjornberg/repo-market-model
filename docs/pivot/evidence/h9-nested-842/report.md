# H9 step 3: the richer targets' forecasts as inputs of H5's candidate (#842)

A measurement on development data for hypothesis **H9** (the secondary goal), step 3 of `docs/research/hypotheses/H9.md`, milestone M4. It is not a record and **not a verdict**: development data never gives one (`docs/decisions/scoring-protocol.md` §1). Nothing is published: no target joins any published declaration, no published figure moves, nothing is written into `docs/runs/`. No day after 2025-12-31 is read (`docs/decisions/lockbox.md`; the script refuses a locked day). Every choice is in `metadata/h9_nested_842.json`, committed before any nested score.

**The test.** H5's candidate `gbm_funding` (the published funding features, 23 levels, no calibration), fitted walk-forward at leads 1 to 5, with and without one target's forecast as an extra input. The forecast is the median of #706's walk-forward law of the target for the same target day, made at the same decision instant from a fit that used only what was public before it. One target at a time; no combination.

Decision days: 1848 (2018-07-30 to 2025-12-23). Intervals: studentized stationary bootstrap, block 10, 10000 draws, seed 842, one-sided 95%. `d = S(base) − S(base + target)`; positive favours the target's forecast; skill = mean(d) / mean(S(base)).

## Nested difference on the primary score (grid CRPS, mean over leads 1 to 5)

| target | CRPS base | CRPS with target | d, all days | skill (lower 95%) | Holm p | d, without 2019-09-18 | Holm p, without |
|---|---|---|---|---|---|---|---|
| `bgcr_dispersion_bps` | 1.824 | 1.829 | -0.004 (lower -0.015) | -0.002 (lower -0.008) | 1.000 | -0.004 (lower -0.015) | 1.000 |
| `on_rrp_change_bn` | 1.824 | 1.825 | -0.000 (lower -0.009) | -0.000 (lower -0.005) | 1.000 | -0.000 (lower -0.009) | 1.000 |
| `sofr_dispersion_bps` | 1.824 | 1.818 | +0.006 (lower -0.005) | +0.003 (lower -0.003) | 0.517 | +0.006 (lower -0.004) | 0.516 |

## Against the benchmarks (skill over B1 and over B2, lower 95% bound)

| model | over B1 | over B2 |
|---|---|---|
| `base` | +0.204 (lower +0.126) | +0.276 (lower +0.176) |
| `plus_bgcr_dispersion_bps` | +0.202 (lower +0.123) | +0.274 (lower +0.176) |
| `plus_on_rrp_change_bn` | +0.204 (lower +0.126) | +0.275 (lower +0.176) |
| `plus_sofr_dispersion_bps` | +0.207 (lower +0.130) | +0.278 (lower +0.178) |

## Nested difference by split (d, lower 95% bound; days in brackets)

| split | `bgcr_dispersion_bps` | `on_rrp_change_bn` | `sofr_dispersion_bps` |
|---|---|---|---|
| lead:1 (1848) | -0.008 (lower -0.020) | -0.011 (lower -0.025) | -0.004 (lower -0.017) |
| lead:1 without_2019-09-18 (1847) | -0.008 (lower -0.020) | -0.011 (lower -0.025) | -0.004 (lower -0.017) |
| lead:2 (1848) | -0.007 (lower -0.019) | -0.002 (lower -0.013) | +0.005 (lower -0.007) |
| lead:2 without_2019-09-18 (1847) | -0.007 (lower -0.019) | -0.003 (lower -0.013) | +0.005 (lower -0.007) |
| lead:3 (1848) | -0.002 (lower -0.016) | -0.005 (lower -0.017) | +0.008 (lower -0.005) |
| lead:3 without_2019-09-18 (1847) | -0.002 (lower -0.016) | -0.006 (lower -0.017) | +0.008 (lower -0.005) |
| lead:4 (1848) | -0.003 (lower -0.018) | +0.007 (lower -0.007) | +0.006 (lower -0.008) |
| lead:4 without_2019-09-18 (1847) | -0.003 (lower -0.018) | +0.007 (lower -0.006) | +0.006 (lower -0.007) |
| lead:5 (1848) | -0.000 (lower -0.014) | +0.009 (lower -0.002) | +0.017 (lower +0.002) |
| lead:5 without_2019-09-18 (1847) | -0.000 (lower -0.014) | +0.009 (lower -0.002) | +0.017 (lower +0.002) |
| regime:2018-19 (355) | +0.033 (lower -0.010) | +0.020 (lower -0.005) | +0.024 (lower -0.019) |
| regime:2018-19 without_2019-09-18 (354) | +0.033 (lower -0.009) | +0.020 (lower -0.005) | +0.024 (lower -0.018) |
| regime:2020 (251) | -0.005 (lower -0.023) | -0.007 (lower -0.045) | +0.024 (lower -0.002) |
| regime:2021-23 (748) | -0.020 (lower -0.034) | -0.009 (lower -0.021) | -0.016 (lower -0.027) |
| regime:2024 (250) | -0.010 (lower -0.027) | -0.000 (lower -0.015) | -0.000 (lower -0.016) |
| regime:2025-26 (244) | -0.002 (lower -0.025) | +0.003 (lower -0.023) | +0.039 (lower +0.014) |
| state:ample (1359) | -0.012 (lower -0.021) | -0.004 (lower -0.012) | -0.000 (lower -0.010) |
| state:scarce (489) | +0.018 (lower -0.014) | +0.010 (lower -0.015) | +0.025 (lower -0.007) |
| state:scarce without_2019-09-18 (488) | +0.018 (lower -0.015) | +0.010 (lower -0.015) | +0.025 (lower -0.007) |
| type:month_end (502) | -0.006 (lower -0.035) | +0.003 (lower -0.028) | -0.015 (lower -0.055) |
| type:ordinary (1848) | -0.003 (lower -0.014) | -0.001 (lower -0.010) | +0.008 (lower -0.003) |
| type:ordinary without_2019-09-18 (1847) | -0.003 (lower -0.014) | -0.001 (lower -0.010) | +0.008 (lower -0.003) |
| type:quarter_end (146) | +0.046 (lower -0.039) | +0.019 (lower -0.045) | +0.035 (lower -0.082) |
| type:tax_date (214) | -0.010 (lower -0.039) | -0.008 (lower -0.042) | +0.015 (lower -0.018) |

## Upper-tail twCRPS (weight 1{y > 0 bp}): d, lower 95% bound

| target | all days | without 2019-09-18 |
|---|---|---|
| `bgcr_dispersion_bps` | +0.005 (lower -0.003) | +0.005 (lower -0.003) |
| `on_rrp_change_bn` | +0.003 (lower -0.003) | +0.003 (lower -0.003) |
| `sofr_dispersion_bps` | +0.005 (lower -0.003) | +0.005 (lower -0.003) |

## Reproduction of the candidate

The base re-walks #634's `gbm_funding`: grid CRPS 1.8261 on 1868 days here; 1.8261 on 1868 days recorded in `docs/pivot/evidence/spread-distribution-protocol/score.json`. On the days every walk covers (the plus walks start at a later refit block) the base reads 1.8245.

## Readings (development data, not a verdict)

* `bgcr_dispersion_bps`: does not improve the candidate beyond its interval (skill -0.002, lower bound of d -0.015); without 2019-09-18 it does not improve it. Development data, not a verdict. Split cells read: 14; cells showing a gain: none.
* `on_rrp_change_bn`: does not improve the candidate beyond its interval (skill -0.000, lower bound of d -0.009); without 2019-09-18 it does not improve it. Development data, not a verdict. Split cells read: 14; cells showing a gain: none.
* `sofr_dispersion_bps`: does not improve the candidate beyond its interval (skill +0.003, lower bound of d -0.005); without 2019-09-18 it does not improve it. Development data, not a verdict. Split cells read: 14; cells showing a gain: regime:2025-26.
* H9 against its kill ("no nested gain for H5"): no target improves the candidate beyond its interval on development data. Development data, not a verdict. Nothing is registered, and no target joins a published declaration.
