# H5: the spread distribution under scoring protocol v1, with the post-phase-2 inputs (#634)

Hypothesis and step: **H5** (primary goal, the SOFR − IORB distribution in bp), research steps 1 (phase 2 models re-scored under the protocol) and 2 (the inputs built since phase 2).

A scratch measurement under `docs/decisions/scoring-protocol.md` (version 1, #640). It writes nothing into `docs/runs/`, publishes nothing, moves no published figure, scores no day after 2025-12-31 (`docs/decisions/lockbox.md`) and changes no rule. Everything was declared in `metadata/spread_distribution_634.json` and committed before any score; one amendment (the announced IORB change is an input at h = 1 only, because the as-of rule refuses it at longer leads) was committed after the h = 1 walks and before any score. **Development days give a score and an interval, never a verdict (#46, protocol v1): nothing here supports, kills or registers a candidate. Whether the five-level published declaration is put on the 23-level grid by the linear law used here (B3 and variant a) is a question for Eleonora (#655).**

## What was scored

Scorer `repo_model.scoring_protocol` (grid CRPS over 23 levels, averaged over h = 1 to 5, one number per decision day; upper-tail twCRPS with weight 1{y > 0 bp}) and benchmarks `repo_model.protocol_benchmarks` (B1 as-of persistence, B2 calendar climatology), B3 the published funding declaration. Paired difference d = benchmark − candidate (positive favours the candidate), stationary bootstrap, mean block 10, 10,000 draws, seed 634, one-sided 95%. 1,868 decision days, 2018-06-29 to 2025-12-23 (the first, 2018-06-28, has no B2; every target day is on or before 2025-12-31).

- (a) the published declaration (gbm, nested conformal PID, five levels) with the new inputs, put on the grid by a linear law;
- (b) gbm quantiles at the 23 levels with the new inputs;
- (c) the two-part form chosen from #632's step 1, at the 23 levels, with the new inputs;
- controls: the published declaration as it stands (B3; its walk reproduces the recorded daily forecasts exactly, checked at h = 1) and the phase 2 gbm at the 23 levels on the published features.

New inputs: announcement-dated settlements and per-release H.4.1 (#541), the announced IORB change (#579, h = 1 only), the scarcity state read per leg (#571), the rolling satiation distance (#587, #598), the tail-spread level (#601) and the market-day tax-date window (#538, per the orchestrator's note under Eleonora's ruling on #554).

## Result

Full tables (by regime, by pressure-day type, pinball, coverage, upper tail): `evidence/spread-distribution-protocol/report.md`; the data: `score.json`. Cells: skill [one-sided 95% bounds] / lower bound of the mean daily difference.

| grid CRPS (bp) | mean | vs B1 | vs B2 | vs B3 |
|---|---|---|---|---|
| B1 as-of persistence | 2.302 | | | |
| B2 calendar climatology | 2.514 | | | |
| B3 published declaration | 1.823 | +20.8% [+11.5%, +29.0%] | +27.5% [+20.1%, +35.2%] | |
| gbm, published features | 1.826 | +20.7% [+11.3%, +28.9%] | +27.4% [+19.8%, +35.2%] | −0.2% [−1.7%, +1.5%] |
| (a) | 1.838 | +20.2% [+10.6%, +28.6%] | +26.9% [+19.5%, +34.4%] | −0.8% [−2.2%, +0.4%] |
| (b) | 1.841 | +20.1% [+10.4%, +28.5%] | +26.8% [+19.3%, +34.5%] | −1.0% [−3.1%, +1.0%] |
| (c) | 1.835 | +20.3% [+9.0%, +29.4%] | +27.0% [+19.9%, +34.3%] | −0.7% [−5.1%, +3.2%] |

- **Phase 2 re-scored (step 1).** The published declaration and the phase 2 gbm both beat B1 and B2 on the primary score by about 21% and 27%, with the lower bound of the mean difference above zero. This is development evidence only.
- **The new inputs do not improve the primary score.** Against the same model without them: (a) −0.8% [−2.2%, +0.4%], (b) −0.8% [−2.2%, +0.4%]. None of the three variants beats B3 on the primary score (the lower bound is below zero for all).
- **Upper tail (key secondary).** (c) is the one variant ahead of B3 on twCRPS: +5.6% [+1.5%, +10.9%]; (a) +0.6% and (b) −0.5% are indistinguishable from B3. (c) also has the lowest Brier score for P(> +5 bp) (0.0486 against B3 0.0521, persistence-logistic 0.0599, climatology 0.0701) and for P(> +10 bp) (0.0259 against 0.0285, 0.0298 and 0.0317), each with an interval above the two fitted benchmarks.
- **Where each loses.** In 2021-23, where every phase 2 gbm lost to persistence, none beats B1 (B3 −5.8%, gbm −0.9%, (a) −10.3%, (b) −4.7%, (c) −30.4% [−48.4%, −14.3%]); (c) is worse than B3 there by 23%. Against B3 in 2025-26 (c) gains 14.4% [+9.0%, +19.8%] and (a) and (b) lose 2.2% and 8.8%. On quarter-end and tax-date targets no model beats B1 with an interval above zero.
- **Median and tails.** At the 0.95 level (b) is worse than B3 (−11.3% [−19.4%, −4.8%]), (c) ahead of it by a small, unresolved amount. The 50% and 90% intervals cover 0.30 to 0.38 and 0.67 to 0.89 against nominal 0.50 and 0.90: (a) and B3 are close to nominal at 90% only.

**Variant count.** Spread-forecast variants scored in development before this directive: three in phase 2 (gbm uncalibrated, gbm cross-conformal, the published declaration) and two in #632. This directive adds three declared variants and one re-fitted control, four new fits, nine in all.

## Not checked, or for Eleonora

- **Question (hers, #655):** how the five-level published declaration is put on the 23-level grid. Read here by the linear law of the gbm exceedance (`spread_distribution_632.quantile_at`), for B3 and (a); another reading changes B3's score and every figure against it.
- The outcome is the panel's `spread_bps`, not re-derived from first-published vintages (protocol §11).
- Not run: the as-of scarcity-state split (§7); the ON RRP rate, SRF rate and H.8 inputs (liquidity repository); any 2026 day.
- The announced IORB change is absent at h = 2 to 5; the variants' h = 1 results include it.
- The regimes were drawn after the fact and are not a pass requirement.
- No candidate is registered or proposed. Nothing joins a published declaration, so no "Publish?" issue arises.
