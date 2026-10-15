# H5: the spread distribution under scoring protocol v1, with the post-phase-2 inputs (#634)

Hypothesis and step: **H5** (primary goal, the SOFR − IORB distribution in bp), research steps 1 (phase 2 models re-scored under the protocol) and 2 (the inputs built since phase 2).

A scratch measurement under `docs/decisions/scoring-protocol.md` (version 1, #640). It writes nothing into `docs/runs/`, publishes nothing, moves no published figure, scores no day after 2025-12-31 (`docs/decisions/lockbox.md`) and changes no rule. Everything was declared in `metadata/spread_distribution_634.json` and committed before any score; one amendment (the announced IORB change is an input at h = 1 only, because the as-of rule refuses it at longer leads) was committed after the h = 1 walks and before any score. **Development days give a score and an interval, never a verdict (#46, protocol v1): nothing here supports, kills or registers a candidate.** B3, the published declaration, is scored on its own five levels as a secondary benchmark, never refitted or interpolated to the grid (Eleonora's ruling on #660, restated on #700 and #711).

## What was scored

Scorer `repo_model.scoring_protocol` (grid CRPS over 23 levels, averaged over h = 1 to 5, one number per decision day; upper-tail twCRPS with weight 1{y > 0 bp}) and benchmarks `repo_model.protocol_benchmarks` (B1 as-of persistence, B2 calendar climatology): the primary comparisons, on the grid. B3, the published funding declaration, is the secondary benchmark: it is scored on its own five levels (0.05, 0.25, 0.5, 0.75, 0.95), and every forecast it is paired with is read at the same five. Paired difference d = benchmark − candidate (positive favours the candidate), studentized stationary bootstrap (Newey-West at lag 10; ruling on #660, item 1), mean block 10, 10,000 draws, seed 634, one-sided 95%. 1,868 decision days, 2018-06-29 to 2025-12-23 (the first, 2018-06-28, has no B2; every target day is on or before 2025-12-31).

- (a) the published declaration (gbm, nested conformal PID, five levels) with the new inputs: on its own five levels against B3, and put on the grid by a linear law against B1 and B2 (Eleonora's ruling on #711), with its own five levels against B1 and B2 as a sensitivity;
- (b) gbm quantiles at the 23 levels with the new inputs;
- (c) the two-part form chosen from #632's step 1, at the 23 levels, with the new inputs;
- controls: the published declaration as it stands (B3; its walk reproduces the recorded daily forecasts exactly at h = 1 to 5) and the phase 2 gbm at the 23 levels on the published features.

New inputs: announcement-dated settlements and per-release H.4.1 (#541), the announced IORB change (#579, h = 1 only), the scarcity state read per leg (#571), the rolling satiation distance (#587, #598), the tail-spread level (#601) and the market-day tax-date window (#538, per the orchestrator's note under Eleonora's ruling on #554).

## Result

Full tables (by regime, by pressure-day type, pinball, coverage, upper tail): `evidence/spread-distribution-protocol/report.md`; the data: `score.json`. Cells: skill [one-sided 95% bounds] / lower bound of the mean daily difference.

| grid CRPS (bp), primary | mean | vs B1 | vs B2 |
|---|---|---|---|
| B1 as-of persistence | 2.302 | | |
| B2 calendar climatology | 2.514 | | |
| gbm, published features | 1.826 | +20.7% [+13.3%, +40.0%] | +27.4% [+17.4%, +36.6%] |
| (a) | 1.838 | +20.2% [+12.4%, +41.9%] | +26.9% [+17.6%, +36.0%] |
| (b) | 1.841 | +20.1% [+12.3%, +41.4%] | +26.8% [+17.5%, +36.0%] |
| (c) | 1.835 | +20.3% [+11.0%, +38.0%] | +27.0% [+18.0%, +36.0%] |

| CRPS on the five published levels (bp), secondary | mean | vs B3 |
|---|---|---|
| B1 as-of persistence | 2.319 | B3 ahead by +21.8% [+14.4%, +41.0%] |
| B2 calendar climatology | 2.498 | B3 ahead by +27.4% [+17.8%, +36.5%] |
| B3 published declaration | 1.814 | |
| gbm, published features | 1.830 | −0.9% [−2.7%, +0.8%] |
| (a) | 1.829 | −0.9% [−2.3%, +0.6%] |
| (b) | 1.850 | −2.0% [−4.4%, +0.2%] |
| (c) | 1.829 | −0.8% [−5.5%, +3.6%] |

| Sensitivity, not the headline: (a) on its own five levels | mean | vs B1 | vs B2 |
|---|---|---|---|
| (a), CRPS | 1.829 | +21.1% [+13.4%, +42.4%] | +26.8% [+17.5%, +35.8%] |
| (a), upper-tail twCRPS | 0.930 | +33.0% [+23.8%, +54.5%] | +17.7% [+6.5%, +29.8%] |

- **Phase 2 re-scored (step 1).** The published declaration and the phase 2 gbm both beat B1 and B2 on the primary score by about 21% and 27%, with the lower bound of the mean difference above zero (the published declaration on its own five levels, the gbm on the grid). This is development evidence only.
- **The new inputs do not improve the primary score.** Against the same model without them: (a) −0.9% [−2.3%, +0.6%] (on the five levels, against B3), (b) −0.8% [−2.3%, +0.6%] (on the grid, against the phase 2 gbm). None of the three variants beats B3 on the five levels (the lower bound is below zero for all).
- **Upper tail (key secondary).** (c) is the one variant ahead of B3 on twCRPS read at the five levels: +5.3% [+0.7%, +10.5%]; (a) +0.7% and (b) −1.2% are indistinguishable from B3. On the grid, (c) has the lowest Brier score for P(> +5 bp) (0.0486 against persistence-logistic 0.0599 and climatology 0.0701) and for P(> +10 bp) (0.0259 against 0.0298 and 0.0317), each with an interval above the two fitted benchmarks. B3 is not in the Brier table: a threshold probability is not a statistic of its five levels.
- **Where each loses.** In 2021-23, where every phase 2 gbm lost to persistence, none beats B1 on the grid (gbm −0.9%, (a) −10.3%, (b) −4.7%, (c) −30.4% [−54.0%, −13.6%]; B3 −1.4% on the five levels); (c) is worse than B3 there by 23.3% and (a) by 4.8% [−8.6%, −1.4%]. Against B3 in 2025-26 (c) gains 15.1% [+8.9%, +21.8%] and (a) and (b) lose 2.1% and 9.5%. On quarter-end and tax-date targets no model beats B1 with an interval above zero.
- **Median and tails.** At the 0.95 level (b) is worse than B3 (−11.3% [−19.9%, −4.2%]), (c) ahead of it by a small, unresolved amount (+2.9% [−2.1%, +8.2%]). The 50% and 90% intervals cover 0.30 to 0.38 and 0.67 to 0.89 against nominal 0.50 and 0.90: (a) and B3 are close to nominal at 90% only.

**Variant count.** Spread-forecast variants scored in development before this directive: three in phase 2 (gbm uncalibrated, gbm cross-conformal, the published declaration) and two in #632. This directive adds three declared variants and one re-fitted control, four new fits, nine in all.

## Not checked, or for Eleonora

- Variant (a)'s placement on the grid against B1 and B2 is Eleonora's ruling on #711 (the linear law of the gbm exceedance, `spread_distribution_632.quantile_at`); its own five levels against B1 and B2 are reported as a sensitivity only (`evidence/spread-distribution-protocol/report.md`, Table 1c).
- The intervals are main's studentized bootstrap (ruling on #660, item 1). This pull request's first version used the percentile bootstrap the scorer had then, so its bounds differ from these; the means and the walks are unchanged except for B3 and (a) read on five levels.
- The outcome is the panel's `spread_bps`, not re-derived from first-published vintages (protocol §11).
- Not run: the as-of scarcity-state split (§7); the ON RRP rate, SRF rate and H.8 inputs (liquidity repository); any 2026 day.
- The announced IORB change is absent at h = 2 to 5; the variants' h = 1 results include it.
- The regimes were drawn after the fact and are not a pass requirement.
- No candidate is registered or proposed. Nothing joins a published declaration, so no "Publish?" issue arises.
