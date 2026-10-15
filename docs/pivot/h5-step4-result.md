# H5 step 4: is more model work worthwhile? H5's best candidate against H2's ceiling (#758)

Hypothesis and step: **H5** (primary goal), development step 4 (`docs/research/hypotheses/H5.md`): use H2's upper-bound result (#635) to decide whether more model work is worthwhile.

A development measurement. It is never a claim and never a verdict (scoring protocol v1, #46). It registers nothing, writes nothing into `docs/runs/`, moves no published figure, reads no day after 2025-12-31 and scores no day of a locked tier (`docs/decisions/lockbox.md`). Nothing here joins a published declaration, so no "Publish?" question arises.
Everything below was declared in `metadata/h5_step4_758.json` and committed before any score. One deviation (the reproduction tolerance, below) was declared after the first scoring attempt stopped at its own check and before any figure was read.

## Declared before any number

* **Candidates.** `gbm_funding`, the phase 2 gradient-boosted quantile model on the published features at the 23 levels (the best pooled grid CRPS of the five forecasts #634 scored), and `c_two_part_new`, #634's variant (c) (best of the new-input variants on the upper tail). The best candidate is the one with the lower mean grid CRPS on the pooled ordinary cell: `gbm_funding`. Their walks are #634's `walk`, run again.
* **Ceiling and reachable line.** H2's cross-fitted gradient-boosted fit ("ceiling gbm") and walk-forward gradient-boosted fit ("reachable gbm") of `docs/pivot/upper-bound-result.md`, with its declaration, inputs, settings and seeds unchanged. Their per-day laws are not tracked, so the fits were rerun (below).
* **Scale.** Grid CRPS (bp) averaged over leads 1 to 5 per decision day, skill against B1 (as-of persistence), B2 beside it. Window: H2's walk-forward decision days (2019-07-31 to 2025-12-23), ordinary targets for the headline, as in H2; all targets beside it.
* **Splits.** Pooled; regime (2018-19, 2020, 2021-23, 2024, 2025-26); pressure-day type of the target day; the upper tail (twCRPS above 0 bp).
* **Headroom** = skill(ceiling) - skill(candidate) in points of skill, with the 5th to 95th percentile of a paired stationary bootstrap (mean block 10, one resample shared by the three series, 10,000 draws pooled, 2,000 in the splits). Positive means the ceiling is ahead.
* **Reading rule.** Headroom is "shown" where the 90% interval's lower end is above 0 on at least 30 decision days. Shown pooled or in any split: continue model work, named by split. Shown nowhere: stop at the best available candidate and go to step 5. No adjustment for the number of cells read.

## The rerun does not reproduce H2 to the digit

H2 recorded +0.192 (reachable gbm) and +0.162 (ceiling gbm) against B1 on these days. The rerun gives **+0.196** and **+0.168**. The scratch panel could not be rebuilt byte-identically (digest `92bf10a4…` against `08df8d19…`); the chain of H2's Reproduce section was followed and the cause was not found. The declared check (tolerance 0.001) refused; the tolerance was set to 0.01 (deviation 1 in the declaration) and both sets of figures are in `score.json` (key `reproduction`). The differences are small against the intervals (about 0.15 wide), but this is a marked question below.

## Result (pooled, ordinary targets, 1,598 decision days)

| forecast | mean CRPS (bp) | skill vs B1 [90%] | skill vs B2 [90%] |
|---|---|---|---|
| B1 as-of persistence | 1.718 | | |
| reachable gbm (H2, rerun) | 1.381 | +0.196 [+0.019, +0.354] | +0.293 [+0.229, +0.353] |
| ceiling gbm (H2, cross-fitted, rerun) | 1.430 | +0.168 [+0.003, +0.316] | +0.268 [+0.182, +0.351] |
| `gbm_funding` (best candidate) | 1.276 | +0.257 [+0.114, +0.400] | +0.347 [+0.267, +0.421] |
| `c_two_part_new` | 1.333 | +0.224 [+0.052, +0.380] | +0.318 [+0.234, +0.393] |

**Headroom of the ceiling over the best candidate: -0.090 [-0.161, -0.019]; over the reachable line -0.061 [-0.119, -0.013].** The best candidate is ahead of the ceiling and of the reachable line, with intervals that exclude 0. With all targets the figures are the same in sign: headroom -0.053 [-0.115, +0.006]. The candidate is not above a bound: the ceiling is a cross-fitted fit on 159 inputs with a 250-row minimum, and the candidate is a smaller model trained from 61 days. So "no headroom" reads here as "this ceiling does not show a better forecast than the candidate", not as "nothing more is attainable".

## By split (headroom of the ceiling over `gbm_funding`, points of skill [90%]; full tables for both candidates in `evidence/h5-step4/report.md`)

| split | days | candidate skill vs B1 | ceiling skill vs B1 | headroom |
|---|---|---|---|---|
| regime 2018-19 | 101 | +0.660 [+0.240, +0.799] | +0.538 [+0.053, +0.711] | -0.123 [-0.272, +0.036] |
| regime 2020 | 251 | +0.148 [+0.033, +0.258] | +0.182 [+0.031, +0.309] | +0.035 [-0.059, +0.107] |
| regime 2021-23 | 751 | -0.007 [-0.129, +0.109] | -0.259 [-0.499, -0.058] | -0.252 [-0.465, -0.075] |
| **regime 2024** | 250 | +0.162 [+0.100, +0.225] | +0.271 [+0.147, +0.365] | **+0.110 [+0.027, +0.160]** |
| regime 2025-26 | 249 | +0.186 [+0.099, +0.265] | +0.074 [-0.082, +0.218] | -0.112 [-0.256, +0.031] |
| day type: ordinary | 1,598 | +0.252 [+0.114, +0.390] | +0.173 [+0.012, +0.314] | -0.079 [-0.145, -0.012] |
| day type: month-end | 433 | +0.075 [-0.007, +0.153] | +0.107 [-0.082, +0.272] | +0.032 [-0.127, +0.180] |
| day type: quarter-end | 126 | -0.174 [-0.248, -0.105] | +0.022 [-0.364, +0.246] | +0.196 [-0.131, +0.371] |
| day type: tax date | 185 | -0.029 [-0.147, +0.110] | -0.107 [-0.509, -0.013] | -0.078 [-0.397, -0.032] |
| upper tail (twCRPS), ordinary targets | 1,598 | +0.516 [+0.291, +0.665] | +0.459 [+0.232, +0.611] | -0.058 [-0.120, +0.027] |
| upper tail (twCRPS), all targets | 1,598 | +0.362 [+0.201, +0.486] | +0.336 [+0.176, +0.462] | -0.026 [-0.067, +0.030] |

* **Where the weakness H5 started from sits.** In 2021-23, where every phase 2 gbm lost to persistence, the candidate is level with B1 (-0.007 [-0.129, +0.109]) and the ceiling is behind it (-0.259): the ceiling shows no way out of that regime. The reachable gbm there is -0.312.
* **Upper tail.** The candidate's twCRPS skill against B1 is at or above the ceiling's; (c) is further ahead (+0.559 on ordinary targets).
* **Quarter-end and tax dates.** The candidate is behind B1 on both; the ceiling is not clearly ahead of the candidate (quarter-end +0.196 [-0.131, +0.371]); the cells are thin (126 and 185 days).
* **The one split with headroom shown is 2024** (250 days): +0.110 [+0.027, +0.160] for `gbm_funding`, +0.117 [+0.072, +0.171] for (c). The reachable gbm gets the same +0.27 there, so in 2024 the gap is one that a model with the 159 inputs reaches walk-forward. For (c), 2020 also shows headroom (+0.154 [+0.028, +0.361]), but (c) is not the best candidate.

## Reading it, under the declared rule

By the rule the reading cells are the best candidate's pooled cells, five regimes, four day types and the two upper-tail cells (13 cells, no adjustment). Headroom is shown in one of them, **regime 2024**. Pooled, in 2021-23 and in the upper tail it is not shown.

## Recommendation

**Stop model work and go to H5 step 5, the model-risk validation report for `gbm_funding`.** This reading was chosen by Eleonora's ruling of 15 October 2026 (comment on PR #775, Q1). The declared rule, applied mechanically, returns "continue model work, in 2024 only"; the ruling reads it as a whole: the single split with headroom (2024, +0.110 [+0.027, +0.160]) is one of 13, which multiplicity alone can give. The 2024 split is logged as an avenue, not a next step. Nothing is registered and no verdict is given (development data).

## Not checked, and rulings of 15 October 2026

1. **Reading (ruled, Q1):** stop and go to step 5, as above.
2. **Rerun of H2's fits (ruled, Q2):** the declared tolerance deviation, from 0.001 to 0.01, is accepted for this step by her ruling. The rerun differs from H2's recorded skills by +0.004 and +0.006, under 7% of the -0.090 headroom. The scratch panel digest difference (`92bf10a4...` against `08df8d19...`, cause not found) is a separate reproducibility finding: #813.
3. The ceiling is H2's cross-fitted fit, not a bound; the candidate scores above it pooled. Whether H2's ceiling should be restated against the walk-forward candidate is H2's question.
4. The step 3 diagnoses of #707 have not merged and are not read. The candidate is not changed by them.
5. The outcome is the panel's `spread_bps`, not re-derived from first-published vintages (protocol §11). The as-of scarcity-state split (§7) was not run. No 2026 day is read. The declaration's `regime: 2027` has no days and is not scored.
6. `c_two_part_new` has one missing law (filled by B1, 0.06% of the decision days). The walks were rerun for this directive on this tree's code; their laws are scratch and not tracked.

## Reproduce

Published panel `4ddc3882…` (`build` and `verify-panel` clean). `/opt/rmm-venv`, `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`. The fit takes about three hours on three cores, each walk 15 to 40 minutes. The commands are the docstring of `scripts/h5_step4_758.py`; the scoring takes about 12 minutes.

```
PYTHONPATH=src python3 scripts/h5_step4_758.py score --published PUB.csv --fits OUT/fits.json --walks OUT --tolerance 0.01 --output docs/pivot/evidence/h5-step4/score.json
PYTHONPATH=src python3 scripts/h5_step4_758.py report docs/pivot/evidence/h5-step4/score.json --output docs/pivot/evidence/h5-step4/report.md
```

Evidence: [`evidence/h5-step4/`](evidence/h5-step4/) (`report.md`, `score.json`).
