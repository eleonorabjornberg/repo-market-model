# H9 step 2 on #941's scaled mean reversion, with and without decision day 2019-09-18 (#902)

**Hypothesis and step:** H9 (secondary goal), step 2. **This page is development data, not a verdict** (scoring protocol v1 §1). Panel `26c51093…`, declared in `metadata/richer_targets_902.json` before any score.

**Provisional.** The model is `spread_mr_fhs_mad20_f0.5`, the H5 candidate of 22 October 2026, fitted on each target's own history. It reads no calendar column, so under calendar first (`docs/research/provisional-calendar-register.md`) this page closes no question in either direction.

Cells are skill over the benchmark, `mean(S(benchmark) − S(model)) / mean(S(benchmark))`, with the one-sided 95% lower bound (the lower end of the two-sided 90% interval) in brackets; positive favours the model. B1' is #960's calendar-aware persistence, a reference row beside B1, which stays the protocol's benchmark. 'With' is every scored decision day; 'without' leaves out decision day 2019-09-18 from every cut (#798, Eleonora's ruling, option (b)).

## Pooled, skill over B1

| target | days with / without | with | without |
|---|---|---|---|
| `bgcr_dispersion_bps` | 1836 / 1835 | +0.320 (lower +0.261) | +0.295 (lower +0.239) |
| `on_rrp_change_bn` | 1832 / 1831 | +0.336 (lower +0.315) | +0.336 (lower +0.315) |
| `sofr_dispersion_bps` | 1836 / 1835 | +0.364 (lower +0.285) | +0.317 (lower +0.243) |

## Pooled, skill over B2

| target | days with / without | with | without |
|---|---|---|---|
| `bgcr_dispersion_bps` | 1836 / 1835 | +0.145 (lower +0.035) | +0.145 (lower +0.037) |
| `on_rrp_change_bn` | 1832 / 1831 | -0.061 (lower -0.091) | -0.061 (lower -0.092) |
| `sofr_dispersion_bps` | 1836 / 1835 | +0.199 (lower +0.082) | +0.201 (lower +0.085) |

## Pooled, skill over B1'

| target | days with / without | with | without |
|---|---|---|---|
| `bgcr_dispersion_bps` | 1836 / 1835 | +0.179 (lower +0.112) | +0.180 (lower +0.113) |
| `on_rrp_change_bn` | 1832 / 1831 | +0.297 (lower +0.278) | +0.297 (lower +0.278) |
| `sofr_dispersion_bps` | 1836 / 1835 | +0.175 (lower +0.101) | +0.177 (lower +0.104) |

## By as-of scarcity state, skill over B1

| target | state | days with / without | with | without |
|---|---|---|---|---|
| `bgcr_dispersion_bps` | ample | 1356 / 1356 | +0.261 (lower +0.195) | +0.261 (lower +0.195) |
| `bgcr_dispersion_bps` | scarce | 480 / 479 | +0.446 (lower +0.324) | +0.378 (lower +0.225) |
| `on_rrp_change_bn` | ample | 1356 / 1356 | +0.331 (lower +0.310) | +0.331 (lower +0.310) |
| `on_rrp_change_bn` | scarce | 476 / 475 | +0.405 (lower +0.285) | +0.405 (lower +0.285) |
| `sofr_dispersion_bps` | ample | 1356 / 1356 | +0.218 (lower +0.171) | +0.218 (lower +0.171) |
| `sofr_dispersion_bps` | scarce | 480 / 479 | +0.456 (lower +0.320) | +0.387 (lower +0.219) |

## By as-of scarcity state, skill over B2

| target | state | days with / without | with | without |
|---|---|---|---|---|
| `bgcr_dispersion_bps` | ample | 1356 / 1356 | +0.171 (lower +0.021) | +0.171 (lower +0.021) |
| `bgcr_dispersion_bps` | scarce | 480 / 479 | +0.059 (lower -0.024) | +0.062 (lower -0.018) |
| `on_rrp_change_bn` | ample | 1356 / 1356 | -0.071 (lower -0.101) | -0.071 (lower -0.101) |
| `on_rrp_change_bn` | scarce | 476 / 475 | +0.072 (lower -0.025) | +0.072 (lower -0.025) |
| `sofr_dispersion_bps` | ample | 1356 / 1356 | +0.345 (lower +0.268) | +0.345 (lower +0.268) |
| `sofr_dispersion_bps` | scarce | 480 / 479 | -0.001 (lower -0.087) | +0.002 (lower -0.080) |

## By as-of scarcity state, skill over B1'

| target | state | days with / without | with | without |
|---|---|---|---|---|
| `bgcr_dispersion_bps` | ample | 1356 / 1356 | +0.164 (lower +0.077) | +0.164 (lower +0.077) |
| `bgcr_dispersion_bps` | scarce | 480 / 479 | +0.218 (lower +0.070) | +0.221 (lower +0.075) |
| `on_rrp_change_bn` | ample | 1356 / 1356 | +0.292 (lower +0.272) | +0.292 (lower +0.272) |
| `on_rrp_change_bn` | scarce | 476 / 475 | +0.372 (lower +0.294) | +0.373 (lower +0.295) |
| `sofr_dispersion_bps` | ample | 1356 / 1356 | +0.145 (lower +0.093) | +0.145 (lower +0.093) |
| `sofr_dispersion_bps` | scarce | 480 / 479 | +0.201 (lower +0.038) | +0.205 (lower +0.045) |

## By day type of the target day, skill over B1

| target | day type | decision days with / without | with | without |
|---|---|---|---|---|
| `bgcr_dispersion_bps` | month_end | 495 / 495 | +0.179 (lower -0.179) | +0.179 (lower -0.179) |
| `bgcr_dispersion_bps` | ordinary | 1836 / 1835 | +0.364 (lower +0.283) | +0.338 (lower +0.270) |
| `bgcr_dispersion_bps` | quarter_end | 127 / 127 | +0.050 (lower -0.067) | +0.050 (lower -0.067) |
| `bgcr_dispersion_bps` | tax_date | 210 / 210 | +0.086 (lower -0.140) | +0.086 (lower -0.140) |
| `on_rrp_change_bn` | month_end | 493 / 493 | +0.241 (lower +0.160) | +0.241 (lower +0.160) |
| `on_rrp_change_bn` | ordinary | 1832 / 1831 | +0.338 (lower +0.315) | +0.338 (lower +0.315) |
| `on_rrp_change_bn` | quarter_end | 127 / 127 | -0.004 (lower -0.202) | -0.004 (lower -0.202) |
| `on_rrp_change_bn` | tax_date | 210 / 210 | +0.253 (lower +0.207) | +0.253 (lower +0.207) |
| `sofr_dispersion_bps` | month_end | 495 / 495 | +0.170 (lower +0.100) | +0.170 (lower +0.100) |
| `sofr_dispersion_bps` | ordinary | 1836 / 1835 | +0.438 (lower +0.307) | +0.387 (lower +0.297) |
| `sofr_dispersion_bps` | quarter_end | 127 / 127 | +0.040 (lower -0.071) | +0.040 (lower -0.071) |
| `sofr_dispersion_bps` | tax_date | 210 / 210 | -0.015 (lower -0.265) | -0.015 (lower -0.265) |

## By day type of the target day, skill over B2

| target | day type | decision days with / without | with | without |
|---|---|---|---|---|
| `bgcr_dispersion_bps` | month_end | 495 / 495 | +0.200 (lower -0.049) | +0.200 (lower -0.049) |
| `bgcr_dispersion_bps` | ordinary | 1836 / 1835 | +0.133 (lower +0.001) | +0.134 (lower -0.001) |
| `bgcr_dispersion_bps` | quarter_end | 127 / 127 | +0.082 (lower -1.546) | +0.082 (lower -1.546) |
| `bgcr_dispersion_bps` | tax_date | 210 / 210 | +0.267 (lower -0.201) | +0.267 (lower -0.201) |
| `on_rrp_change_bn` | month_end | 493 / 493 | -0.065 (lower -0.164) | -0.065 (lower -0.164) |
| `on_rrp_change_bn` | ordinary | 1832 / 1831 | -0.041 (lower -0.063) | -0.041 (lower -0.063) |
| `on_rrp_change_bn` | quarter_end | 127 / 127 | -0.570 (lower -1.277) | -0.570 (lower -1.277) |
| `on_rrp_change_bn` | tax_date | 210 / 210 | +0.078 (lower -0.006) | +0.078 (lower -0.006) |
| `sofr_dispersion_bps` | month_end | 495 / 495 | +0.202 (lower +0.064) | +0.202 (lower +0.064) |
| `sofr_dispersion_bps` | ordinary | 1836 / 1835 | +0.207 (lower +0.134) | +0.209 (lower +0.133) |
| `sofr_dispersion_bps` | quarter_end | 127 / 127 | +0.112 (lower -0.640) | +0.112 (lower -0.640) |
| `sofr_dispersion_bps` | tax_date | 210 / 210 | +0.220 (lower -0.572) | +0.220 (lower -0.572) |

## By day type of the target day, skill over B1'

| target | day type | decision days with / without | with | without |
|---|---|---|---|---|
| `bgcr_dispersion_bps` | month_end | 495 / 495 | +0.183 (lower -0.183) | +0.183 (lower -0.183) |
| `bgcr_dispersion_bps` | ordinary | 1836 / 1835 | +0.209 (lower +0.142) | +0.209 (lower +0.141) |
| `bgcr_dispersion_bps` | quarter_end | 127 / 127 | +0.043 (lower -0.077) | +0.043 (lower -0.077) |
| `bgcr_dispersion_bps` | tax_date | 210 / 210 | +0.136 (lower -0.119) | +0.136 (lower -0.119) |
| `on_rrp_change_bn` | month_end | 493 / 493 | +0.231 (lower +0.128) | +0.231 (lower +0.128) |
| `on_rrp_change_bn` | ordinary | 1832 / 1831 | +0.301 (lower +0.283) | +0.301 (lower +0.282) |
| `on_rrp_change_bn` | quarter_end | 127 / 127 | -0.006 (lower -0.205) | -0.006 (lower -0.205) |
| `on_rrp_change_bn` | tax_date | 210 / 210 | +0.197 (lower +0.117) | +0.197 (lower +0.117) |
| `sofr_dispersion_bps` | month_end | 495 / 495 | +0.139 (lower +0.055) | +0.139 (lower +0.055) |
| `sofr_dispersion_bps` | ordinary | 1836 / 1835 | +0.219 (lower +0.159) | +0.222 (lower +0.163) |
| `sofr_dispersion_bps` | quarter_end | 127 / 127 | +0.029 (lower -0.089) | +0.029 (lower -0.089) |
| `sofr_dispersion_bps` | tax_date | 210 / 210 | +0.041 (lower -0.001) | +0.041 (lower -0.001) |

## Pre-onset AUC at lead 1 within the as-of state (90% interval)

The AUC of the model's lead-1 median on the 1 to 5 panel days before each +5 bp onset against every other scored day of the state, and of the target's as-of value beside it.

| target | series | state | onsets with / without | with | without |
|---|---|---|---|---|---|
| `bgcr_dispersion_bps` | model_median | ample | 4 / 4 | 0.682 [0.587, 0.755] | 0.682 [0.587, 0.755] |
| `bgcr_dispersion_bps` | model_median | scarce | 23 / 23 | 0.416 [0.343, 0.489] | 0.417 [0.344, 0.490] |
| `bgcr_dispersion_bps` | as_of_value | ample | 4 / 4 | 0.653 [0.563, 0.759] | 0.653 [0.563, 0.759] |
| `bgcr_dispersion_bps` | as_of_value | scarce | 23 / 23 | 0.406 [0.361, 0.454] | 0.407 [0.362, 0.455] |
| `on_rrp_change_bn` | model_median | ample | 4 / 4 | 0.484 [0.420, 0.530] | 0.484 [0.420, 0.530] |
| `on_rrp_change_bn` | model_median | scarce | 23 / 23 | 0.499 [0.433, 0.565] | 0.499 [0.433, 0.565] |
| `on_rrp_change_bn` | as_of_value | ample | 4 / 4 | 0.543 [0.380, 0.692] | 0.543 [0.380, 0.692] |
| `on_rrp_change_bn` | as_of_value | scarce | 23 / 23 | 0.465 [0.426, 0.503] | 0.465 [0.426, 0.503] |
| `sofr_dispersion_bps` | model_median | ample | 4 / 4 | 0.574 [0.506, 0.634] | 0.574 [0.506, 0.634] |
| `sofr_dispersion_bps` | model_median | scarce | 23 / 23 | 0.428 [0.337, 0.514] | 0.429 [0.338, 0.515] |
| `sofr_dispersion_bps` | as_of_value | ample | 4 / 4 | 0.560 [0.508, 0.593] | 0.560 [0.508, 0.593] |
| `sofr_dispersion_bps` | as_of_value | scarce | 23 / 23 | 0.410 [0.348, 0.470] | 0.411 [0.349, 0.472] |

## The day, 2019-09-18

| target | grid CRPS of the model | grid CRPS of B1' | mean of the model over all days |
|---|---|---|---|
| `bgcr_dispersion_bps` | 17.243 | 10.786 | 5.591 |
| `on_rrp_change_bn` | 3.799 | 3.457 | 15.078 |
| `sofr_dispersion_bps` | 24.033 | 12.748 | 2.948 |

## Interval bounds that change sign

* `bgcr_dispersion_bps`, day type ordinary, over B2: lower bound +0.001 with the day, -0.001 without

## What this does not show

* It is not a reading against H9's kill criterion; that reading is a question for Eleonora (see the pull request).
* The model is calendar-blind and the scale floor of 0.5 is #941's bp figure, kept as declared for `on_rrp_change_bn` (USD bn).
* It uses development days only and no locked day.

