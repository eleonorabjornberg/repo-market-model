# H5 step 3: why the models lose in 2021-23, and what the upper tail does (#707)

Hypothesis and step: **H5** (primary goal), development step 3 of `docs/research/hypotheses/H5.md`, milestone M4: two diagnoses, each its own logged sub-question. **Development data, not a verdict** (scoring protocol v1, #640; #46 top block): nothing here supports, kills or registers a candidate, publishes a figure or moves a declaration.

A scratch measurement. It fits no model: it reads the walk-forward laws of #634 unchanged (the same panels, folds and fits) and scores them with the protocol's scorer (`repo_model.scoring_protocol`, grid CRPS over 23 levels averaged over h = 1 to 5; upper-tail twCRPS above 0 bp), against B1 as-of persistence and B2 calendar climatology. The sub-questions, cuts, remedies and reading rules were committed in `metadata/h5_step3_707.json` before any number; two amendments were committed after that and still before any number (the tail rule restated as two flags, and percentile bounds where the scorer cannot studentize a series). Studentized stationary bootstrap, mean block 10, 10,000 draws, seed 707, one-sided 95%. The calibrated critical value of #695 is for confirmation windows (125 and 250 days) and is not applied to development days. No day after 2025-12-31 is read. 1,868 decision days, 748 of them in 2021-23; the 2021-23 window is a reporting cut only, never an input. Candidates: `gbm_funding` (the phase 2 gbm at 23 levels, the best pooled primary score of #634) and `c_two_part_new` (variant (c) of #634, the one ahead on the upper tail and the worst in 2021-23). Full tables: `evidence/h5-step3-707/report.md`; data: `score.json`. Cells below: skill [one-sided 95% bounds].

## Sub-question 1: 2021-23

In 2021-23 the two candidates are not alike. **(c) loses to B1: -30.4% [-54.7%, -13.5%]. The phase 2 gbm does not resolvably lose: -0.9% [-17.8%, +10.1%]**, so "every gbm loses to persistence" is not borne out for the gbm on this score; the loss is (c)'s.

| 2021-23 | CRPS (bp) | median bias | width of 90% | coverage of 90% | coverage of 50% |
|---|---|---|---|---|---|
| B1 | 0.711 | -0.014 | 6.06 | 0.882 | 0.589 |
| gbm | 0.717 | -0.394 | 2.90 | 0.732 | 0.285 |
| (c) | 0.927 | -0.882 | 4.49 | 0.729 | 0.311 |

Both candidates forecast too high and too narrow for a spread that barely moves (variance of the outcome 5.5 bp²). PIT shares at or below the 10th percentile are 0.42 for (c) and 0.33 for the gbm (expected 0.10); in the as-of "abundant" state 0.40 and 0.29. No decision day in the window has the "scarce" or "tight" state.

**Loss split** (a hindsight counterfactual on the window, not a remedy: S1 removes the window's median level error, S2 also takes the best constant scale; (c) shift -0.34 bp, scale 1.0; gbm shift -0.10 bp, scale 1.2):

| mean CRPS difference (bp) | gap, S0 − B1 | level | dispersion | remainder |
|---|---|---|---|---|
| (c) | +0.216 (lower bound +0.100) | +0.032 (-0.004) | -0.000 (-0.000) | +0.184 (+0.087) |
| gbm | +0.006 (-0.070) | +0.006 (-0.002) | +0.004 (-0.005) | -0.004 (-0.074) |

- **(c): the remainder accounts for most of the loss** (0.184 of 0.216, interval above 0). Neither a constant level correction nor a constant scale explains it; the level part is unresolved and the dispersion part is nil. By the reading rule the remainder is regime transfer (and the shape of the law). The second check supports it only partly: (c)'s skill against B1 by year is -21.0% [-46.9%, +2.3%] in 2021, **-60.8% [-100.2%, -26.7%] in 2022**, and +1.0% [-14.7%, +11.5%] in 2023. The loss is gone by 2023, as an expanding training window absorbing the new regime would give, but it peaks in 2022, not 2021, so this is consistent with transfer and does not establish it.
- **gbm: no cause is established**, because the gap itself is unresolved (+0.006, lower bound -0.070). The rule names "level" only because it is the largest of three parts that are each indistinguishable from 0.

**Remedies**, one per cause, causal (the last 250 cells resolved before the decision day, no regime label), applied to every day:

| remedy | (c): 2021-23 vs B1 | (c): pooled vs B1 | gbm: 2021-23 vs B1 | gbm: pooled vs B1 |
|---|---|---|---|---|
| level (shift by the trailing median error) | -32.2% [-52.8%, -15.5%] | +20.1% [+10.9%, +39.1%] | -1.9% [-17.2%, +8.7%] | +20.3% [+12.8%, +40.5%] |
| scale (best trailing scale in 0.5 to 1) | -30.5% [-54.7%, -13.6%] | +20.3% [+11.2%, +38.0%] | -0.9% [-17.8%, +10.1%] | +20.7% [+13.3%, +40.0%] |
| shrink (trailing weight on B1) | **+1.2% [-2.6%, +4.6%]** | **+23.9% [+18.0%, +34.4%]** | **+8.3% [+2.2%, +13.5%]** | +20.9% [+14.5%, +38.1%] |

Against the unremedied forecast, shrink gains +24.2% [+15.5%, +34.6%] for (c) in the window and +9.2% [+2.8%, +19.5%] for the gbm, and costs nothing pooled (+4.5% [-2.5%, +9.1%] for (c), +0.3% [-1.9%, +2.3%] for the gbm). The level and scale remedies close nothing (the scale remedy leaves the forecasts essentially unchanged: it picks 1.0 almost always).

**Cause, one line.** For (c) in 2021-23 the loss is the remainder, read as regime transfer (-30.4% [-54.7%, -13.5%] against B1); the shrink-to-persistence remedy closes the gap to level with B1 (+1.2% [-2.6%, +4.6%]) and the level and scale remedies do not. For the gbm there is no resolved loss to explain (-0.9% [-17.8%, +10.1%]); the shrink remedy there is ahead of B1 (+8.3% [+2.2%, +13.5%]) in the window, which is a remedy result on a declared grid and not a tuned one.

## Sub-question 2: the upper tail

twCRPS above 0 bp against B1 and B2 (skill [bounds]):

| cut | (c) vs B1 | (c) vs B2 | gbm vs B1 | gbm vs B2 |
|---|---|---|---|---|
| pooled | +35.7% [+26.5%, +51.7%] | +21.3% [+8.8%, +34.4%] | +31.3% [+22.1%, +50.6%] | +15.9% [+3.8%, +29.2%] |
| state abundant | +39.7% [+23.5%, +63.2%] | -12.7% [-41.1%, +6.4%] | +35.4% [+22.8%, +53.5%] | -20.7% [-42.8%, -5.2%] |
| state ample | +48.5% [+29.0%, +64.1%] | +78.7% [+59.7%, +89.8%] | +56.6% [+29.3%, +75.9%] | +82.0% [+60.1%, +94.1%] |
| state scarce | +36.1% [+25.5%, +54.2%] | +16.0% [+4.8%, +30.0%] | +31.7% [+21.3%, +53.8%] | +10.2% [-0.5%, +23.5%] |
| state tight (41 days) | +18.4% [-27.0%, +38.9%] | +39.4% [+24.9%, +59.5%] | +6.9% [-14.1%, +23.8%] | +30.9% [+3.1%, +65.2%] |
| month-end targets | +18.1% [+9.0%, +28.2%] | +35.6% [+21.7%, +50.7%] | +2.0% [-11.5%, +16.5%] | +22.9% [+2.5%, +45.6%] |
| quarter-end targets | +8.6% [-1.3%, +18.3%] | +11.8% [-44.6%, +59.7%] | -11.7% [-50.8%, -2.4%] | -7.8% [-71.1%, +47.3%] |
| tax-date targets | -2.7% [-10.0%, +2.3%] | +18.2% [-37.2%, +50.6%] | -6.4% [-14.1%, -1.6%] | +15.3% [-29.5%, +51.0%] |

The tail is ahead of both benchmarks pooled, but not everywhere: neither candidate beats B2 in the abundant state, and on quarter-end and tax-date targets neither has a resolved gain over B1.

| | exceedance of q90 (nominal 0.10) | exceedance of q95 (nominal 0.05) | cells above 0 bp: coverage q90 / q95 | median PIT | share beyond q99 |
|---|---|---|---|---|---|
| (c) | 0.143 (lower bound 0.114) | 0.095 (lower bound 0.075) | 0.627 / 0.731 | 0.825 | 0.088 |
| gbm | 0.173 (lower bound 0.147) | 0.128 (lower bound 0.106) | 0.599 / 0.682 | 0.825 | 0.142 |

**Cause, one line.** By the declared rule the upper tail is **under-dispersed** for both candidates, not mislocated pooled: the q95 exceedance rate has a lower bound above 0.05 (0.075 for (c), 0.106 for the gbm), while the median PIT on the 1,586 cells above 0 bp is 0.825, below the displacement cut of 0.9 (the whole law does not sit below the outcome). The coverage on cells above 0 bp is conditioned on the outcome and is below nominal by construction; it is shown as asked and is not the rule. In the two states with few such cells (abundant 51, ample 75, tight 104) the median PIT is 0.98, 0.93 and 0.88 for (c) and the share beyond q99 reaches 0.37 for (c) and 0.84 for the gbm in the abundant state: there the law is displaced as well, on few days.

## Variant count

Three post-hoc transforms (level, scale, shrink) applied to two candidates: **6 variants, no new fit**. Cumulative with the nine of #634: 15.

## Not checked, or for Eleonora

- Reliability and resolution in the strict sense were not computed; the loss split above is the calibration–sharpness split by counterfactual recalibration, a stand-in declared before scoring. It is fitted on the window it explains (hindsight) and is a diagnosis, not an estimate of what a deployable correction would gain; the remedies are the causal tests.
- The window cut is a reporting cut on the regime label in `metadata/evaluation_splits.json`, drawn after the fact; no regime label enters a forecast or a remedy.
- "Regime transfer" is read from the remainder and a by-year check; no model was refitted on window-only or floor-system data, so a transfer failure is not separated from a mis-shaped law.
- The shrink remedy's result is on development days and is a diagnosis; it is not a candidate, nothing is registered (#46: no registration until the confirmation design is decided, #733) and no "Publish?" issue arises because nothing joins a published declaration.
- The outcome is the panel's `spread_bps`, not re-derived from first-published vintages (protocol §11). The as-of scarcity state is read at lead 1 with each leg at its own latest public row (#586). The announced IORB change is absent at h = 2 to 5 in the (c) walk, as in #634.
- Two rows carry the stationary bootstrap's percentile bounds, marked `method: percentile` in `score.json`, because the scorer's studentized interval refuses a difference that is zero up to rounding: (c)'s dispersion part (the best scale is 1.0, so the forecasts differ only by floating-point error) and the gbm's scale remedy against the unremedied gbm. Both are differences of about 0 and say so.
