# H9 step 2: the richer targets modelled with #634's model class (#706)

Development data only: **not a verdict** (scoring protocol v1 §1). Declared in `metadata/richer_targets_706.json` before any score.

## Pooled over decision days (grid CRPS, mean over leads 1 to 5)

| target | decision days | CRPS B1 | CRPS B2 | CRPS model | skill over B1 (lower 95%) | skill over B2 (lower 95%) | B1 over B2 |
|---|---|---|---|---|---|---|---|
| `bgcr_dispersion_bps` | 1846 | 8.197 | 6.517 | 5.500 | +0.329 (lower +0.271) | +0.156 (lower +0.080) | -0.258 (lower -0.468) |
| `on_rrp_change_bn` | 1845 | 22.563 | 14.119 | 15.572 | +0.310 (lower +0.286) | -0.103 (lower -0.142) | -0.598 (lower -0.662) |
| `sofr_dispersion_bps` | 1846 | 4.628 | 3.670 | 3.101 | +0.330 (lower +0.241) | +0.155 (lower +0.054) | -0.261 (lower -0.820) |
| (for scale) SOFR − IORB, #634 candidate (b) | - | - | - | - | +0.201 (lower +0.123) | +0.268 (lower +0.175) | - |

Skill is `mean(S(benchmark) − S(model)) / mean(S(benchmark))`; positive favours the model. The last row is #634's spread row: the same model class, inputs, leads and bootstrap for SOFR − IORB.

## By lead (skill over B1, lower 95% bound)

| target | lead 1 | lead 2 | lead 3 | lead 4 | lead 5 |
|---|---|---|---|---|---|
| `bgcr_dispersion_bps` | +0.278 (lower +0.198) | +0.343 (lower +0.285) | +0.326 (lower +0.261) | +0.327 (lower +0.258) | +0.362 (lower +0.300) |
| `on_rrp_change_bn` | +0.327 (lower +0.299) | +0.331 (lower +0.303) | +0.314 (lower +0.288) | +0.283 (lower +0.250) | +0.293 (lower +0.259) |
| `sofr_dispersion_bps` | +0.300 (lower +0.226) | +0.340 (lower +0.255) | +0.335 (lower +0.243) | +0.333 (lower +0.234) | +0.337 (lower +0.235) |

## By as-of scarcity state of the decision day (skill over B1)

| target | ample | scarce |
|---|---|---|
| `bgcr_dispersion_bps` | +0.293 (lower +0.233) (1356 days) | +0.404 (lower +0.279) (490 days) |
| `on_rrp_change_bn` | +0.303 (lower +0.279) (1356 days) | +0.400 (lower +0.291) (489 days) |
| `sofr_dispersion_bps` | +0.171 (lower +0.114) (1356 days) | +0.429 (lower +0.295) (490 days) |

## By day type of the target day (skill over B1)

| target | month_end | ordinary | quarter_end | tax_date |
|---|---|---|---|---|
| `bgcr_dispersion_bps` | +0.162 (lower -0.226) (495) | +0.385 (lower +0.302) (1846) | -0.067 (lower -0.194) (127) | +0.061 (lower -0.069) (210) |
| `on_rrp_change_bn` | +0.160 (lower +0.070) (495) | +0.326 (lower +0.301) (1845) | -0.260 (lower -0.375) (127) | +0.219 (lower +0.119) (210) |
| `sofr_dispersion_bps` | +0.144 (lower +0.073) (495) | +0.407 (lower +0.259) (1846) | -0.103 (lower -0.141) (127) | -0.052 (lower -0.194) (210) |

## Lead on the +5 bp episodes (pre-onset AUC at lead 1, within the as-of state)

| target | series | state | onsets | AUC | 90% interval |
|---|---|---|---|---|---|
| `bgcr_dispersion_bps` | as_of_value | ample | 4 | 0.653 | [0.563, 0.759] |
| `bgcr_dispersion_bps` | as_of_value | scarce | 23 | 0.406 | [0.361, 0.454] |
| `bgcr_dispersion_bps` | model_median | ample | 4 | 0.573 | [0.451, 0.642] |
| `bgcr_dispersion_bps` | model_median | scarce | 23 | 0.379 | [0.312, 0.444] |
| `on_rrp_change_bn` | as_of_value | ample | 4 | 0.543 | [0.380, 0.692] |
| `on_rrp_change_bn` | as_of_value | scarce | 23 | 0.465 | [0.426, 0.503] |
| `on_rrp_change_bn` | model_median | ample | 4 | 0.421 | [0.310, 0.526] |
| `on_rrp_change_bn` | model_median | scarce | 23 | 0.528 | [0.459, 0.598] |
| `sofr_dispersion_bps` | as_of_value | ample | 4 | 0.560 | [0.508, 0.593] |
| `sofr_dispersion_bps` | as_of_value | scarce | 23 | 0.410 | [0.348, 0.470] |
| `sofr_dispersion_bps` | model_median | ample | 4 | 0.489 | [0.457, 0.509] |
| `sofr_dispersion_bps` | model_median | scarce | 23 | 0.390 | [0.306, 0.468] |

## Reading against H9's kill criterion (development, not a verdict)

* `bgcr_dispersion_bps`: skill over persistence shown; lead on the episodes not shown. Beside it: against the climatology B2 the lower bound of the mean CRPS difference is +0.504 (above zero).
* `on_rrp_change_bn`: skill over persistence shown; lead on the episodes not shown. Beside it: against the climatology B2 the lower bound of the mean CRPS difference is -2.079 (not above zero).
* `sofr_dispersion_bps`: skill over persistence shown; lead on the episodes not shown. Beside it: against the climatology B2 the lower bound of the mean CRPS difference is +0.298 (above zero).

**Reading.** No chosen target shows both skill over persistence and a lead on the +5 bp episodes on development data. H9's kill criterion (`H9.md`: "No skill over the target's own persistence, and no nested gain for H5") cannot be assessed until step 3's nested test; this reading is not a verdict, and it rests on days that confirmation will not use.

