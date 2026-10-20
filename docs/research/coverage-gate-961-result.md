# A coverage gate on a simulated world (#961)

**Development data, not a verdict.** A simulation with known dynamics; nothing here is registered, published or in force, and the protocol's text and constants are only read. Hypothesis and step: H1 (the synthetic suite) and H5 step 5 (candidate choice). Declared in `metadata/coverage_gate_961.json`; produced by `scripts/coverage_gate_961.py`; the statistics are `repo_model.coverage_tests`.

## 1. The current rule against calibration

The world is an AR(1) (phi 0.9) with calm and stress blocks of 250 days (innovation sd 1.0 and 2.5), 5000 decision days, leads 1-5, seed 961. Forecasts are 23 Gaussian quantiles on the protocol's grid. The rule ranks by mean grid CRPS (smaller is better).

| rank | forecaster | mean grid CRPS | passes the gate | passes the pooled cells |
|---|---|---|---|---|
| 1 | ideal | 1.3489 | yes | yes |
| 2 | under_0.75 | 1.3822 | no | no |
| 3 | over_1.5 | 1.4156 | no | no |
| 4 | pooled | 1.4263 | no | no |
| 5 | under_0.5 | 1.4974 | no | no |
| 6 | persistence | 1.5365 | no | yes |
| 7 | climatology | 2.2220 | no | no |

With the ideal forecaster in the field the rule ranks it first, as propriety guarantees. A real field never holds the true law. Without it the rule ranks `under_0.75` first, which fails the gate (failing cells: calm/lead 1, calm/lead 2, calm/lead 3, calm/lead 4, calm/lead 5, stress/lead 1, stress/lead 2, stress/lead 3, stress/lead 4, stress/lead 5).

Paired against `under_0.5` (one-sided 95% lower bound of mean S(benchmark) - S(under_0.5), positive favours the under-dispersed forecast):

| benchmark (calibrated pooled) | mean difference | lower bound |
|---|---|---|
| climatology | +0.7246 | +0.6402 |
| persistence | +0.0390 | +0.0112 |
| pooled | -0.0711 | -0.0872 |

## 2. What the declared gate does

Per lead and regime: Kupiec at q05 and at q95 (fail below p = 0.01), Christoffersen independence at q95 (p < 0.01; decision days thinned to every h-th at lead h), and the 98% band's coverage within [0.95, 0.995]. A forecaster passes when every cell passes.

| forecaster | cells failing |
|---|---|
| ideal | none |
| under_0.75 | calm/lead 1, calm/lead 2, calm/lead 3, calm/lead 4, calm/lead 5, stress/lead 1, stress/lead 2, stress/lead 3, stress/lead 4, stress/lead 5 |
| over_1.5 | calm/lead 1, calm/lead 2, calm/lead 3, calm/lead 4, calm/lead 5, stress/lead 1, stress/lead 2, stress/lead 3, stress/lead 4, stress/lead 5 |
| pooled | calm/lead 1, calm/lead 2, calm/lead 3, calm/lead 4, calm/lead 5, stress/lead 1, stress/lead 2, stress/lead 3, stress/lead 4, stress/lead 5 |
| under_0.5 | calm/lead 1, calm/lead 2, calm/lead 3, calm/lead 4, calm/lead 5, stress/lead 1, stress/lead 2, stress/lead 3, stress/lead 4, stress/lead 5 |
| persistence | calm/lead 1, calm/lead 2, calm/lead 3, calm/lead 4, calm/lead 5, stress/lead 1, stress/lead 2, stress/lead 3, stress/lead 4, stress/lead 5 |
| climatology | calm/lead 1, calm/lead 2, calm/lead 3, calm/lead 4, calm/lead 5, stress/lead 1, stress/lead 2, stress/lead 3, stress/lead 4, stress/lead 5 |

The pooled forecasters (`pooled`, `persistence`, `climatology`) are calibrated over the whole path and fail by regime: over-wide in calm, too narrow in stress. A pooled pass is reported beside each result and decides nothing.

## 3. The gate's own size

The ideal forecaster is calibrated by construction. On 300 simulated paths of 2000 days (10 lead-and-regime cells, 4 tests each, every one at 1%) the declared gate fails it on 54.3% of paths. Share of paths on which each test fails at least one cell: band_98 0.0%, independence_q95 2.0%, kupiec_q05 31.7%, kupiec_q95 33.0%. By lead (any cell of the lead): lead 1 6.0%, lead 2 11.3%, lead 3 24.3%, lead 4 35.7%, lead 5 41.0%.

The failures are Kupiec's, and they grow with the lead. Kupiec assumes independent hits; the errors of an h-step forecast made on consecutive days overlap, so their hits are positively dependent, the hit count is more variable than Kupiec assumes, and a calibrated forecast is rejected too often. Independence is already read on thinned days in the declared gate; Kupiec is not. **Post hoc (not declared; seen after the first run):** thinning Kupiec to every h-th day as well gives a failure share of 19.7% on the same paths (lead 1 6.0%, lead 2 4.7%, lead 3 3.7%, lead 4 3.0%, lead 5 5.7%), which is still a family of forty tests at 1% and well above 1%. On the demonstration path the post-hoc variant ideal: passes; under_0.75: fails; over_1.5: fails; pooled: fails; under_0.5: fails; persistence: fails; climatology: fails.

## Questions for Eleonora

1. Whether a coverage gate becomes a registration requirement is a section 13 kind-(a) amendment, hers to decide. The demonstration above is the evidence, and it stands on the simulation alone (her #741 ruling).
2. If it does, the gate's size above says two things need deciding: whether Kupiec is read on thinned days at leads above 1, and whether the per-cell 1% levels get a family-wise correction (or fewer cells). Both are level choices and hers; the declared gate as written would reject a calibrated candidate about half the time at this sample size.
3. On a whole-bp target, is a hit `y > q` or `y >= q`? The world here is continuous, so the question does not move a number on this page.

## Not done here

The directive's criteria 2 and 3 (the candidate's per-day 23-level forecasts, and the gate applied to `gbm_funding`, B3 and the direct-pairs twin) need walks and are not in this run; see the pull request.
