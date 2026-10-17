# Research log

One entry per scored experiment, newest last. The plan is [`plan.md`](plan.md); the format is the constant
`ENTRY_FORMAT` in `scripts/check_research_log.py`, which `python3 scripts/check_research_log.py check` enforces in
CI. The same format serves both repositories (`repo-market-liquidity` results arrive as a fenced `research-log`
block copied verbatim from that repository's pull request body).

Heading: `### YYYY-MM-DD [H#] step N · owner/repo#PR` (the date is Eastern time). Groundwork (G1 to G5 in a
hypothesis manual, kept apart from the six steps) has its own heading,
`### YYYY-MM-DD [H#] groundwork G<n> · owner/repo#PR`; an item that covers two pieces of groundwork has one entry each.
Lines: Directive, Step, Tier (`development` or `confirmation`), Pins, Tried, Result, Against kill, Next.

**Backfill, 12 October 2026.** The entries from 10 to 12 October were written after the fact from the pull request
bodies and result pages; every figure is copied as published and nothing is recomputed. They predate the
hypotheses, so the `[H#]` tag and the step are assigned retrospectively (these are the +5 bp classification
experiments that the plan pauses). The "variants" count is the count in that pull request only: no running
count existed before the progress page (#637). Every one of them is development evidence, none is a verdict.
Pull requests #612 and #647 are open and are not backfilled.

### 2026-10-05 [H5] step 3 · eleonorabjornberg/repo-market-model#73
- Directive: #73 (Phase 2 verdict)
- Step: 3 (summary of Phases 0 to 2 from `PLAN.md`)
- Tier: development
- Pins: as-of records in `docs/runs/`; published panel `4ddc3882…`
- Tried: Phases 0 and 1 (reproducible foundation; public dataset, Milestone A met). Phase 2: persistence, gbm uncalibrated and cross-conformal, the v1 funding declaration, each paired against as-of persistence; exceedance probabilities against climatology and the persistence-logistic model. Variants: n/a (summary).
- Result: criterion met on the interval evidence for beating as-of persistence on CRPS (paired intervals exclude zero); not uniform: every gbm loses to persistence in 2021-23 and the uncalibrated gbm loses on quarter ends. The tail clause is measured and failing: at the upper thresholds every gbm's exceedance probabilities are beaten by climatology.
- Against kill: phase 2 closed for now by Eleonora on 5 October 2026 with two items open (`PLAN.md`, Phase 2).
- Next: spread distribution re-scored under the protocol (H5, #634), 2021-23 and the tails.

### 2026-10-11 [H2] step 3 · eleonorabjornberg/repo-market-model#548
- Directive: #539
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; base `6237f171`
- Tried: 4 variants (`+hurdle_platt`, `+hurdle_isotonic`, `+hurdle_state_platt`, `+hurdle_state_isotonic`) on the five risk-date passers; a calibrated every-day hazard for the days that are not risk dates.
- Result: no variant passes the full rule under either miss rule. `risk_gbm` h = 1: 13/26 onsets, worst false alarms 1.35; variants 15/26 with 2.46 to 3.54. Brier against the parent: interval includes zero in all 100 horizon-by-variant cells.
- Against kill: not applicable (no verdict; hypotheses postdate it).
- Next: re-score under announcement dating (#556).

### 2026-10-11 [H2] step 3 · eleonorabjornberg/repo-market-model#549
- Directive: #544
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; base `74d44625`
- Tried: pre-train on 2008-2018 EFFR − IOER, fine-tune on the SOFR era; two forms (pooled with a source indicator, pre-train then refit); six judge candidates.
- Result: no model passes (flat rule, +5 bp). Onsets flagged of 26: `risk_gbm` 13 (recall 0.500 [0.310, 0.667], worst false alarms 1.35), `effr_pretrain_finetune` 7, `effr_pooled` 5, SOFR-only control 7; combined with `risk_gbm` 11 each. Recall in 2018, 2020 and 2024 unchanged from the parent: no model warns any of them. Against the control, Brier and log loss intervals include zero at every horizon.
- Against kill: not applicable.
- Next: the combined row (#561).

### 2026-10-11 [H2] step 3 · eleonorabjornberg/repo-market-model#552
- Directive: #543
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; base `74d4462`
- Tried: a latent funding-stress factor (dynamic factor model), nine series, three mappings; variants: 3 rows plus a combined row.
- Result: no latent-factor row passes the judge. Tier 1 weighted, onsets flagged / worst false alarms per onset: `latent_factor` 14 / 3.38, `latent_factor_logit` 12 / 3.37, `risk_gbm+latent_factor_logit` 15 / 2.15, against `risk_gbm` 13 / 0.80. Brier gain under `risk_gbm` at h = 1: 0.011 [0.002, 0.022]; recall difference +0.115 [0.000, 0.250]; it warns none of the 2018 or 2024 onsets.
- Against kill: not applicable.
- Next: combined model (#561).

### 2026-10-11 [H2] step 3 · eleonorabjornberg/repo-market-model#558
- Directive: #545
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; base `1b3568d`
- Tried: projected reserves on the scored day (known flows to T+h against the demand-curve kink); alone and as the every-day part of the hurdle under `risk_gbm`.
- Result: alone it warns 12 of 26 onsets (weighted rule), the calendar climatology's number, and misses every 2018, 2020, 2024 and 2025 onset; it fails tier 1 on recall. As the every-day part under `risk_gbm` it warns 12 of 26 at h = 2 and 3 and fails tier 1 on false alarms.
- Against kill: not applicable.
- Next: combined model (#561).

### 2026-10-11 [H2] step 3 · eleonorabjornberg/repo-market-model#559
- Directive: #540
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; base `6237f17`
- Tried: four model defects on the five risk-date passers (nowcast target cap, leaf floor, announced IORB at h = 1, added risk dates); 4 changes plus all three together.
- Result: nowcast MAE 3.463 → 1.920 bp, −1.543 [−1.853, −1.271] against the declared nowcast, still behind naive over all days (+0.095 [+0.017, +0.169]). `risk_gbm_base+all`: 18 of 26, worst false alarms 3.96. No parent and no variant passes the pass rule.
- Against kill: not applicable.
- Next: dating re-score (#556).

### 2026-10-11 [H2] step 3 · eleonorabjornberg/repo-market-model#562
- Directive: #556
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; base `7d8ce19e`
- Tried: the hurdle variants re-scored under announcement-dated settlements and per-release H.4.1; arms `settle`, `h41`, `both`; 60 judge candidate files.
- Result: no row passes the full rule under either miss rule and no verdict changes. `+settle` improves Brier at h >= 2 (70 of 100 variant-horizon pairs favour it, none go against).
- Against kill: not applicable.
- Next: combined model (#561).

### 2026-10-11 [H2] step 3 · eleonorabjornberg/repo-market-model#563
- Directive: #561
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; base `7d8ce19`
- Tried: passer plus calibrated ordinary-day logistic and gate; 7 judge candidate files.
- Result: no row passes the full rule. `risk_gbm+combined_nogate` 11 / 13 of 26 onsets flagged (flat / weighted), recall 0.500 [0.308, 0.684], worst weighted false alarms 1.74, tiers 1 / 3 / 5 yes / no / yes. The control `risk_gbm+every_day+gate+settle+h41` flags 18 of 26 at 1.64. The combination does not beat the control.
- Against kill: not applicable.
- Next: diagnose the unwarned onsets (#560).

### 2026-10-11 [H2] step 3 · eleonorabjornberg/repo-market-model#564
- Directive: #560
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; base `7d8ce19e`
- Tried: a diagnostic of the eight unwarned onsets (2018, 2020, 2024): was anything public before the decision instant? No new model.
- Result: under the weighted rule six of the eight are warned by no model row. The four 2018 onsets cannot be warned by any row: the judge has no cut-off in force for almost all model rows on those days (36 percent of all 2018-19 model-row cells). 2020-03-04 was public and unused (the announced IORB cut).
- Against kill: not applicable.
- Next: audit fixes (#578) and the announced IORB row (#579).

### 2026-10-11 [H2] step 3 · eleonorabjornberg/repo-market-model#580
- Directive: #578
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; base `1a41626`
- Tried: construction fixes #566, #568, #574, #575, #577 and a re-score of the affected rows. Variants: n/a (correction).
- Result: before and after tables for every re-scored row in `docs/pivot/audit-fixes-578-result.md`.
- Against kill: not applicable.
- Next: further audit fixes (#623).

### 2026-10-11 [H2] step 3 · eleonorabjornberg/repo-market-model#582
- Directive: #579
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; base `1a416264`
- Tried: 1 row: the announced IORB change in the control row's every-day component.
- Result: no verdict changes under either rule. The gain is one onset, 2020-03-04 (recall in 2020 1 of 2 to 2 of 2); 2018 and 2024 gain nothing. Paired Brier differences all cover or touch zero. The input was picked from #560's diagnosis on the same days; not a confirmation.
- Against kill: not applicable.
- Next: the pooled count of false alarms (#595).

### 2026-10-11 [H2] step 3 · eleonorabjornberg/repo-market-model#599
- Directive: #586
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; base `8b32ea96`
- Tried: the scarcity state's legs (reserves, H.8 total assets, ON RRP) each read at its own latest public row. Variants: n/a (a construction change, with a decision record drafted for her).
- Result: 102 of 1,873 days change state at h = 1 (54 up, 48 down); 64 of the 102 are in 2025. The re-score under the pooled count is #611.
- Against kill: not applicable.
- Next: re-score under the pooled false-alarm count (#607).

### 2026-10-11 [H2] step 3 · eleonorabjornberg/repo-market-model#596
- Directive: #587
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; base `e61471ab`
- Tried: a time-varying satiation level for the reserve-demand terms: rolling (a) and fitted (b) forms, in the structural, projected and combined rows.
- Result: no tier 1 verdict changes; no row passes the full rule. Structural with the rolling level: 14 onsets, weighted false alarms 3.12 (limit 2), 5 of 5 onsets warned in 2025, against 11 and 1.69 with the fixed 0.12 level. The page later describes the rolling level as a two-year reserves low (dated note, #623).
- Against kill: not applicable.
- Next: rolling distance in the tier-1 passers (#598).

### 2026-10-11 [H2] step 3 · eleonorabjornberg/repo-market-model#602
- Directive: #589
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; base `84b25d14`
- Tried: 2 variants: state-conditioned recalibration of the best row, keyed on the as-of scarcity state.
- Result: no variant passes tier 1, tier 3 or the overall pass. Tier 5 goes no to yes for `state_platt` under both rules. Neither repairs 2018-19. The parent fails tier 1 at 3.46 weighted pooled (limit 2).
- Against kill: not applicable.
- Next: the pooled false-alarm excess (#595).

### 2026-10-12 [H2] step 3 · eleonorabjornberg/repo-market-model#605
- Directive: #598
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; base the merge of #596
- Tried: 3 variants: rolling satiation distance in the tier-1 passers (`+dist_roll`, `+hinge_roll`, and one on `risk_gbm_base`).
- Result: one more 2025 onset warned per variant (15 of 26 against 14), no verdict changes. Recall difference against the parent 0.038 [0.000, 0.111]. 2025-26 predicted rate 0.030 to 0.042 against 0.117 realised.
- Against kill: not applicable.
- Next: the tier 3 and tier 5 failures (#606).

### 2026-10-12 [H2] step 3 · eleonorabjornberg/repo-market-model#600
- Directive: #595
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; base `0adb032`
- Tried: 3 declared gates on the every-day part of the best row (`+leadgate`, `+gate95`, `+tail`).
- Result: none passes tier 1 under the pooled count (limit 2): the row 19 of 26 at 3.46; `+leadgate` 18 of 26 at 2.69; `+gate95` 16 of 26 at 3.27; `+tail` 19 of 26 at 3.25. The every-day part raises 131 of the row's 184 pooled false-alarm days.
- Against kill: not applicable.
- Next: what separates onset warnings from false alarms (#601).

### 2026-10-12 [H2] step 3 · eleonorabjornberg/repo-market-model#608
- Directive: #606
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; base `9f24027`
- Tried: diagnosis of the best row's tier 3 and tier 5 failures, then 3 recalibrations (a floor under the days that are not risk dates).
- Result: tier 3 fails in 2018-19 and 2025-26 at every lead. Best row h = 1: 2018-19 predicted 0.0927 against 0.2720 realised, difference +0.1793 [+0.1046, +0.2532]; 2025-26 0.0481 against 0.1165, +0.0684 [+0.0051, +0.1500]. None of the three passes.
- Against kill: not applicable.
- Next: tail cap with the floor (#610, PR #612, open).

### 2026-10-12 [H1] step 3 · eleonorabjornberg/repo-market-model#611
- Directive: #607
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; base `5d88b50`
- Tried: #586 re-scored under the pooled false-alarm count; the paired Brier header corrected so a positive difference favours the candidate (#603, #604). Variants: n/a (correction).
- Result: under the pooled count, `risk_gbm+every_day+gate+settle+h41+iorb` has 3.46 (worst single lead 1.64) and `ngboost_laplace` 2.34 (1.73), tier 1 no where it was stored as yes. `risk_gbm+settle+h41` 1.44 / 1.48 (same-row / own-leg), tier 1 yes.
- Against kill: the old judge's counting was wrong in a way that changed tier 1 verdicts; consistent with H1's concern (the plan's Why section).
- Next: construction fixes (#623).

### 2026-10-12 [H2] step 3 · eleonorabjornberg/repo-market-model#609
- Directive: #601
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; base `9f24027ab61c6d16325f3c32ab928b8b77396f7f`
- Tried: step 1 compares the every-day part's onset warnings with its false alarms on 14 inputs; step 2 scores 2 caps on the every-day part by the tail spread's own trailing history.
- Result: one input separates them, the tail spread's level, lower at the onset warnings: AUROC 0.304 [0.16, 0.47] over all, in the same direction against the 2019-20 false alarms. Step 2, weighted rule: `+tailcap75` 18 of 26 onsets, recall 0.692 [0.522, 0.852], pooled false alarms 1.88 (tier 1 yes, tiers 3 and 5 no); `+tailcap50` 14 of 26 at 1.48. Paired Brier of `+tailcap75` against the row: −0.0073 [−0.0150, −0.0005] over all days. Detail in `docs/pivot/every-day-separation-result.md`; the paired-Brier header on this page was later corrected (dated note, #623).
- Against kill: not applicable.
- Next: cap with floor (#610).

### 2026-10-13 [H5] step 3 · eleonorabjornberg/repo-market-model#697
- Directive: #637
- Step: 3 (progress tracking; no new scoring)
- Tier: development
- Pins: published panel `4ddc3882…`; base `09640f5bb4063da150e09a285d242cd28db1c136`
- Tried: no variants. `scripts/emit_progress.py` copies committed evidence into `docs/pivot/progress.md` and `docs/research/progress.json`; the running count it starts is 358 candidate files and 1 spread-forecast declaration (3 variants).
- Result: no new figure; a page that shows each candidate's spread CRPS difference, ordinary-day AUROC, Brier difference, calibration and judge tiers, with "not measured" where the evidence has none.
- Against kill: not applicable (no verdict; infrastructure).
- Next: #645 reads `docs/research/progress.json` for the hypothesis sections.

### 2026-10-13 [H3] step 1 · eleonorabjornberg/repo-market-model#696
- Directive: #680
- Step: 1
- Tier: development
- Pins: published panel `4ddc3882…`; base `09640f5`
- Tried: #630's screen re-run with the decided 13-day carry cap on the dealer financing columns, which #630 carried with no limit; the withheld (`*`) weeks counted per column. Variants: n/a (correction).
- Result: the export withholds 85 of 666 weekly dates of `pd_repo_ust` and 72 of `pd_reverse_repo_ust` (2022 to 2025), 3 of `pd_repo_mbs`, none of the fails series. Partial rank correlation with the +5 bp indicator on ordinary days: `pd_reverse_repo_ust` +0.112 → +0.087 [+0.05, +0.12], `pd_repo_ust` +0.104 → +0.076 [+0.03, +0.12]. Detail in `docs/pivot/new-sources-withheld-weeks.md`.
- Against kill: not applicable (H3's kill is not tested here; the two series lose rank, and neither was a lead beyond #630's own reading).
- Next: Eleonora decides whether the source is admitted given the withheld weeks.

### 2026-10-13 [H2] step 2 · eleonorabjornberg/repo-market-model#709
- Directive: #682
- Step: 2 (groundwork)
- Tier: development
- Pins: published panel `4ddc3882…`; base `374fe3d4`
- Tried: one shared risk-date function with two named definitions; counts per lead under both. Variants: n/a.
- Result: at h = 1 the ordinary set is 1568 days with 87 pressure days (`scheduled`) or 1469 with 82 (`non_ordinary`); the 99 month-ends that are not quarter-ends are the difference. No figure moves.
- Against kill: not applicable.
- Next: ruled 14 October 2026 (relayed): H2, H5 and #637 use the shared `risk_dates` definition, under which announced coupon settlements count as risk dates, from their next step on; past pages keep theirs and are not re-scored. Both named definitions count coupon settlements, so which of the two is still to be named by Eleonora.

### 2026-10-13 [H2] step 3 · eleonorabjornberg/repo-market-model#712
- Directive: #679
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; base `374fe3d`
- Tried: the partly announced bill class of the net settlement columns audited against the completed day's net (#665's 117 day-lead cases reproduce; #647's 238 groups do not), and the class left out until fully announced; the structural, projected-reserves and combined models re-scored. Variants: n/a (correction).
- Result: leaving the class out has the smallest mean absolute error at leads 4 and 5 (32.8 and 35.9 bn, against 49.1 and 51.7 for the old rule and 87.7 and 87.5 for #647's) and overall (37.2 against 50.6 and 85.7); at lead 2 (2 cases) and lead 3 (10 cases) another rule is nearer. Re-scored: no tier or pass changes; `risk_gbm+structural` stays at 15 of 26 onsets (tier 3 yes), `structural_liquidity` 11 to 12 of 26, `projected_reserves` 12 to 11 of 26; none of the rows passes.
- Against kill: not applicable (a data correction; no hypothesis is tested).
- Next: re-run the other evidence that reads the net settlement columns (listed in `docs/pivot/partly-announced-679-audit.md`).

### 2026-10-13 [H2] step 3 · eleonorabjornberg/repo-market-model#714
- Directive: #681
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; base `374fe3d`
- Tried: #624's off-risk-day measurement re-stated against persistence-logistic (finding #667) and the raw as-of spread, on the same population, every row paired with persistence-logistic. Variants: n/a (reference rows added, none new).
- Result: over all days at lead 1 no row beats persistence-logistic (AUROC 0.897, Brier skill 0.196; `+offday` −0.009 [−0.065, +0.027] and +0.042 [−0.008, +0.111]). `+offday` is ahead at leads 2, 3 and 5 over all days (Brier skill +0.090, +0.092, +0.062, intervals above 0) and not inside 2018-19 (62 of 82 pressure days) or 2025-26; the gain sits in 2020 and 2024 (3 and 2 pressure days). The raw as-of spread has AUROC 0.92 to 0.94, above every row. Detail in `docs/pivot/off-risk-day-result.md`.
- Against kill: not tested (H2's kill is on the ceiling, #635); consistent with the ordinary-day ranking being no more than the as-of spread's.
- Next: Eleonora decides which benchmark H2 progress is judged against.

### 2026-10-13 [H9] step 1 · eleonorabjornberg/repo-market-model#702
- Directive: #639
- Step: 1 (the screen of the richer targets; step 2, the model, is not done)
- Tier: development
- Pins: published panel `4ddc3882…`; screen panel `347f5afb…`; base `374fe3d4`
- Tried: 10 targets (SOFR 99th percentile − IORB and SOFR dispersion, TGCR and BGCR each minus IORB and their dispersion, EFFR − IORB, ON RRP level and change, standing repo facility take-up), as-of persistence B1 and calendar climatology B2 at leads 1, 2, 3, 5 and 10, the lead against the +5 bp episodes and the overlap with SOFR − IORB. Variants: 0 (nothing is fitted).
- Result: persistence beats the climatology for EFFR − IORB and the ON RRP level at every lead (skill +0.80 [+0.72, +0.86] and +0.89 [+0.87, +0.91] at lead 1), for TGCR/BGCR − IORB at lead 1 only (+0.22 [+0.04, +0.38]); the climatology beats it for the dispersions from lead 2, the ON RRP change and the facility take-up. The rate-level targets correlate +0.39 with the pressure indicator and read high before onsets (AUC 0.83) but not within the as-of scarcity state (scarce-state pre-onset AUC 0.47 to 0.52); TGCR/BGCR − IORB repeat SOFR − IORB (+0.95).
- Against kill: not testable in this step (no model, development data); no target shows a lead beyond the as-of scarcity state.
- Next: step 2, the model for at most three targets, once the target-choice rule and #634's model are settled.

### 2026-10-13 [H5] step 1 · eleonorabjornberg/repo-market-model#711
- Directive: #634
- Step: 1
- Tier: development
- Pins: published panel `4ddc3882…`; base `09640f5`, re-scored after merging main at `a69f6b94`
- Tried: the phase 2 gbm and the published declaration re-scored under protocol v1 (grid CRPS, h = 1 to 5, against B1 and B2; against B3 on its own five levels), and 3 variants with the post-phase-2 inputs (published declaration, gbm, two-part). Variants: 3 new plus 1 re-fitted control; 9 spread-forecast variants in all with phase 2 (3) and #632 (2).
- Result: published declaration 1.814 bp on its five levels, +21.8% [+14.4%, +41.0%] against B1 and +27.4% [+17.8%, +36.5%] against B2 there; phase 2 gbm on the grid +20.7% [+13.3%, +40.0%] and +27.4% [+17.4%, +36.6%]. The new inputs add nothing on the primary score (ablation −0.9% [−2.3%, +0.6%] for the published declaration, −0.8% [−2.3%, +0.6%] for the gbm); no variant beats B3 on its five levels. Upper-tail twCRPS: only the two-part form is ahead of B3, +5.3% [+0.7%, +10.5%]. In 2021-23 no variant beats persistence.
- Against kill: not applicable (development days give no verdict); no CRPS gain over the phase 2 models on the primary score.
- Next: the 2021-23 and upper-tail diagnoses (H5 step 3); B3 is scored on its own five levels by Eleonora's ruling (#660, #700); variant (a) stays on the grid against B1 and B2 by her ruling on #711, with its own five levels as a sensitivity (+21.1% and +26.8%).

### 2026-10-13 [H5] step 2 · eleonorabjornberg/repo-market-model#713
- Directive: #686
- Step: 2
- Tier: development
- Pins: published panel `4ddc3882…`; scoring protocol v1 scorer and benchmarks B1, B2; seed 686
- Tried: 1 variant, `spread_mr_level10`: persistence with partial mean reversion toward the median of the last 10 ordinary days, phi on a grid, empirical residual quantiles, refitted every 21 decision days. Variants: 1 (the declaration `metadata/spread_distribution_686.json` is the second spread-forecast declaration on main, after #632).
- Result: grid CRPS 1.778 bp over 1,855 decision days to 2025-12-31: skill +22.3% [+13.7%, +29.5%] against B1 and +29.4% [+21.4%, +37.3%] against B2; upper-tail twCRPS +32.4% and +17.8%. Against the published distribution on five levels: +1.2% [-2.3%, +4.8%], a tie. Weak spots: 2021-23 (-2.6% vs B1) and quarter-end days. It narrows B1's over-forecast of P(> +5 bp) on ordinary days (2018-19 -0.113 to -0.071, 2025-26 -0.049 to -0.028) without closing it.
- Against kill: not applicable (no verdict; development data). It does not beat the published distribution, so it adds nothing over the incumbent on CRPS.
- Next: Eleonora decides whether a reverting level is worth adding to #634's candidates; #707 diagnoses 2021-23 and the upper tail.

### 2026-10-13 [H8] step 1 · eleonorabjornberg/repo-market-model#722
- Directive: #694
- Step: 1 (the target, the benchmarks and a development score)
- Tier: development
- Pins: published panel `4ddc3882…`; scoring protocol v1 scorer for the bootstrap; base `bd7f573`; seed 694
- Tried: 2 rankers of the next 20 business days, from the mean-reverting spread distribution of #686 extended to 20 leads (read as P(spread > +5 bp) and as the predicted median), against persistence (B1), climatology by day type and the calendar of known risk dates. Variants: 2 (the declaration `metadata/ranking_694.json`; nothing is fitted to the +5 bp event).
- Result: top-5 precision of the probability ranker 7.9% against 13.0% for the calendar, gain -5.2 pp [-7.7 pp, -3.0 pp] over 1,825 decision days to 2025-12-31; against climatology by day type -1.7 pp [-2.8, -0.6]; against persistence +0.1 pp [-0.3, +0.6]. The median ranker is lower still. The model's top 5 are scheduled risk dates 16% of the time (calendar 64%); the calendar holds 36% of the pressure days. Sensitivity (ruling of 13 October 2026, item 2): with the protocol's mean block of 10 days in place of the declared 20, the same gain's interval is [-7.2 pp, -3.4 pp], so the reading is unchanged. Detail in `docs/pivot/ranking-result.md`.
- Against kill: the kill condition (no ranking skill beyond the calendar of known risk dates) is met on development data, as exploration and not a verdict: the model carries no calendar information and the calendar alone out-ranks it in every year with pressure days.
- Next: step 2, accepted by Eleonora on 13 October 2026: rank by tail probability combined with the day type (a directive for it is hers to queue).

### 2026-10-13 [H2] step 3 · eleonorabjornberg/repo-market-model#721
- Directive: #687
- Step: 3 (diagnosis of avenue #674)
- Tier: development
- Pins: published panel `4ddc3882…`; base `53338b4`; bootstrap seed 624
- Tried: the every-day part of the control row taken apart one construction step at a time (persist, gate, tail cap, all eight subsets) and #624's `+offday` taken apart (inputs, state, interactions), 11 rows, against persistence-logistic and the full construction, plus pooled against within-refit-block AUROC. Variants: n/a (diagnosis, no new variant).
- Result: the ungated logistic ranks the ordinary days as well as persistence-logistic (AUROC 0.905 against 0.897 at lead 1, difference +0.008 [-0.004, +0.027]) and below the raw spread (0.941). The gate takes it to 0.736 (37 of 82 pressure days on a forecast of 0) and the tail cap to 0.493; removing only the cap from the full construction gains +0.240 [+0.156, +0.304]. Refits do not lower the pooled AUROC: within-block AUROC is lower (0.659 against 0.905).
- Against kill: not applicable (no verdict; development data).
- Next: an every-day part for #634(c) or #632(b) drops the cap and the gate; Eleonora confirms the reading of "persist".

### 2026-10-13 [H7] step 1 · eleonorabjornberg/repo-market-model#715
- Directive: #689
- Step: 1 (the as-of estimator of the kink, model side; the label-free estimator is in the liquidity repository)
- Tier: development
- Pins: published panel `4ddc3882…`; scratch panel `52cb519e…`; base `e2b1f397`
- Tried: 2 variants (`structural_kinked_profile`, the level that minimises the ridge logistic's own objective over the level grid at each refit; `structural_kinked_slow`, the same with a penalty on the move from the previous refit's level), against `structural_kinked_fitted` and `structural_kinked_rolling` of #626, at h = 1 to 5.
- Result: the interval of levels within 1.92 nats of the profile's minimum reaches the grid maximum 0.20, above every observed ratio, at every refit at every horizon (width about 0.08, several local minima at 46% to 100% of refits): the logistic never rejects "no kink". The profile level moves more than the least-squares one (20 changes of 0.01 or more against 9 at h = 1); the slow level is held at 0.1375 by its penalty. Ordinary days, h = 1: AUROC 0.881 [0.829, 0.921] for both, against 0.883 for the unkinked control; AUROC minus `kinked_fitted` +0.005 [0.000, 0.011], minus `kinked_rolling` -0.001 [-0.017, 0.017].
- Against kill: not testable (no registered test; development data). The demand-curve route is closed for a kinked logistic whose level is estimated from the pressure label, and open for H7's label-free estimator.
- Next: the liquidity repository's estimator (its #22) is the next test of the kink.

### 2026-10-13 [H5] step 6 · eleonorabjornberg/repo-market-model#718
- Directive: #717
- Step: 6 (new: the validation report rewritten for the chosen candidate; plan amendment, nothing scored)
- Tier: development
- Pins: published panel `4ddc3882…`; no score, no panel built; base `bd7f573`
- Tried: plan: validation report added. `docs/research/hypotheses/H5.md` gains step 6 and milestone M5a (the report is a rewrite of `docs/model/validation.md`, goes to Eleonora with the registration, and is updated at each checkpoint). Variants: 0.
- Result: not applicable (a plan edit; no experiment).
- Against kill: not applicable.
- Next: the step is carried out once step 5 has chosen the primary candidate.

### 2026-10-13 [H6] step 1 · eleonorabjornberg/repo-market-model#719
- Directive: #693
- Step: 1
- Tier: development
- Pins: published panel `4ddc3882…`; scoring protocol v1 scorer and benchmark B1; seed 693
- Tried: 2 candidates on 383 risk target days (quarter-end, month-end, tax and coupon-settlement days) to 2025-12-31: the mean-reverting H5 row of #686 read on those days, and 1 new day-type × scarcity-state model (the trailing two years' spreads on days of the type and state group). Benchmarks: as-of persistence B1 and the trailing year's spreads on days of the same risk type. Variants: 1 (the declaration `metadata/risk_date_spread_693.json`).
- Result: grid CRPS 3.139 bp for the H5 row against 3.243 for B1 and 4.289 for the calendar benchmark: skill +3.2% [+0.0%, +6.6%] against B1 (lower bound +0.03%) and +26.8% [+13.8%, +44.7%] against the calendar; MAE of the median has no skill against B1 (+0.7% [-3.2%, +3.6%]). By regime its skill against B1 is +4.4% in 2018-19, -1.8% in 2020-24 and +5.7% in 2025-26. The type × state model is worse than the calendar benchmark on CRPS (-7.1% [-16.6%, -0.8%]).
- Against kill: not killed on the declared reading (the H5 row has CRPS skill against both benchmarks), narrowly and from the regimes outside 2020-24; development data, not a verdict.
- Next: Eleonora decides the size threshold and the announcement timing of coupon settlements (marked questions in the declaration); the day set moves to #682's function once it merges.

### 2026-10-13 [H3] step 1 · eleonorabjornberg/repo-market-model#716
- Directive: #690
- Step: 1
- Tier: development
- Pins: published panel `4ddc3882…`; base `ee9366eb`; the scratch panel of `scripts/new_sources.py panel`
- Tried: 0 model variants; a re-screen of 3 columns (`auc_dealer_share`, `auc_indirect_share`, `auc_cover`) after the Fed's rollover (SOMA) was left out of their denominators and the cover took Treasury's definition; no other series moved.
- Result: `auc_dealer_share` is no longer clear of 0.5 on ordinary days (AUROC 0.566 [0.49, 0.64] at lead 1, was 0.580 [0.51, 0.66]; scarce band 0.491 [0.41, 0.56]). `auc_cover` on Treasury's definition is now the auction series clear of 0.5, on the low side (ordinary days 0.365 [0.31, 0.43] at lead 1 and 0.297 [0.25, 0.35] at lead 5; partial rho -0.10 [-0.15, -0.06]). Exploratory, unadjusted for multiplicity.
- Against kill: not applicable (no verdict; development data).
- Next: whether `auc_cover` enters the nested test of H3 step 3 (#708); not decided here.

### 2026-10-13 [H2] step 3 · eleonorabjornberg/repo-market-model#703
- Directive: #635
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; base `09640f5`; scratch panel `DERIV.csv` `08df8d19…`
- Tried: the upper bound on 159 inputs for the spread (23-level grid CRPS over leads 1 to 5, against B1 and B2) and the +5 bp indicator on ordinary days: a gradient-boosted and a regularised linear family, each fitted cross-fitted with generous settings (the ceiling, ten blocked folds per lead with a walk-forward embargo; Eleonora's ruling of 13 October) and walk-forward every 21 scored days (the reachable line); the first in-sample fit is kept as a labelled reference. Variants: 12 fitted rows (2 families x 2 targets x 3 fits).
- Result: spread, ordinary days, against B1: cross-fitted gbm +0.144 [+0.0002, +0.271], reachable gbm +0.192 [+0.007, +0.352] (behind in 2021-23, -0.318 [-0.529, -0.133]); the cross-fitted ceiling is not above the reachable line (-0.037 [-0.124, +0.049] on the same days); both ridge fits are worse than persistence. Indicator, read against persistence-logistic: cross-fitted gbm AUROC difference -0.016 [-0.044, +0.015], Brier skill -0.159 [-0.245, -0.059]; reachable +0.015 [-0.017, +0.058] and -0.192 [-0.374, +0.034]. The in-sample gbm (AUROC 1.000) is a reference only.
- Against kill: not applicable as a verdict (development). Under the amended reading rule: spread partly reached, by a hair; indicator data problem.
- Next: H5's development steps on the spread (#634); the indicator's effort goes to new data (H3, H4).

### 2026-10-13 [H2] step 3 · eleonorabjornberg/repo-market-model#691
- Directive: #691
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; base `660a72b`
- Tried: 0 model variants; the eight candidate declarations of the satiation (#587) and kinked (#626) rows corrected to name `net_settlement_ahead_h` and `ahead_{h-1}` at h >= 2 (finding #673), and both pages re-scored on the current code (#618, #679). Variants: n/a (correction).
- Result: no tier and no pass of any row changes. `structural_rolling` flags 18 of 26 onsets (was 14) with tier-3 flags per 252 days 2.9 / 3.4 (was 1.2 / 1.3); `structural_liquidity` and `structural_fitted` 12 of 26 (was 11); `structural_kinked_rolling` 17 (was 16); `structural_kinked_fitted` stays at 11 with fewer false alarms (1.21 against 1.69). Detail in `docs/pivot/declarations-691-result.md`.
- Against kill: not applicable (a record correction; no hypothesis is tested).
- Next: none from this directive; the pages keep their original prose with a dated note.

### 2026-10-13 [H4] step 3 · eleonorabjornberg/repo-market-model#661
- Directive: #633
- Step: 3 (steps 1 and 2 in the same pull request: the due-diligence table, and the workbook released from 17 May 2018 by Eleonora's ruling)
- Tier: development
- Pins: scratch panel `4137d0ad…`, extended panel `f3acce04…`, workbook `1c889930…`; base `09640f5b`; declaration `metadata/backfill_spread_633.json`
- Tried: one scratch quantile model of the spread (23 levels, leads 1 to 5) trained without and with the 899 back-filled rows, scored by the protocol's scorer from 2018-06-29 to 2025-12-31; a workbook-only sensitivity declared after the first score. Variants: 1 model, 2 input sets, 2 arms each.
- Result: 2018-19 coverage of the central 90% interval rises +0.050 [+0.020, +0.082] (declared) and +0.035 [+0.017, +0.054] (workbook-only); 2018-19 CRPS d +0.043 [−0.013, +0.101] and +0.064 [+0.009, +0.117]; the share above the 95th percentile does not move (0.167 → 0.174, 0.191 → 0.191). Detail in `docs/pivot/posting-dates-h4-result.md`.
- Against kill: not killed, as exploration: a posting time is established, and the 2018-19 calibration move's interval excludes zero in both input sets. The 2018-19 upper tail stays under-forecast.
- Next: whether to register (step 4) is Eleonora's; the H5 models cannot use the history without pre-2018 inputs the project does not hold.

### 2026-10-13 [H2] step 3 · eleonorabjornberg/repo-market-model#692
- Directive: #692
- Step: 3 (data rework: re-run the seven records that read the Fed repo take-up columns after #659)
- Tier: development
- Pins: published panel `4ddc3882…`; base `e2b1f397`; data change confined to 339 panel rows, 2018-05-09 to 2019-09-16
- Tried: no new variant. Re-ran the record's own commands, unchanged apart from the data: source screen, source matrix, unused inputs, OFR follow-up, weighted-miss rows that read the columns; backfilled history and the due-diligence table checked. Variants: 0.
- Result: no ranking, redundancy group or pass/fail verdict moved. Figures moved for the Fed repo columns only (e.g. `fed_repo_days_since_positive` ordinary-day pressure AUROC at lead 1 0.58 [0.43, 0.72] to 0.64 [0.48, 0.79]); in the judged records the dealer candidates flag more 2018 onsets (OFR logistic 15 to 18 of 27, recall 0.577 to 0.692 [0.517, 0.844]) and some paired-Brier intervals change whether they exclude zero. Detail in `docs/pivot/fed-repo-rescreen-692-result.md`.
- Against kill: not applicable (no verdict; development data). The ceiling statements of H2 are unchanged: the Fed repo columns stay far below the cut-off of the source screen.
- Next: Eleonora decides whether to amend the stale sentences named in the result page.

### 2026-10-13 [H1] step 1 · eleonorabjornberg/repo-market-model#695
- Directive: #655 (scorer, benchmarks and synthetic suite merged in PR #660; this pull request applies Eleonora's rulings on its questions)
- Step: 1
- Tier: development
- Pins: published panel `4ddc3882…`; base `09640f5`
- Tried: the synthetic suite of protocol v1 (perfect, persistence, climatology, shifted, dispersed, lead-misaligned and noisy-truth forecasts) against the scorer; the interval's coverage on the resampled real B2 − B1 daily difference series and on an iid normal control, at 250 days, first with the percentile and then with the studentized stationary bootstrap.
- Result: the first check passes: every stated order is recovered under grid CRPS and the upper-tail twCRPS. The second check fails: the one-sided 95% bound covers 0.802 (percentile) and 0.825 (studentized) of 1,500 replications on the real series, against 0.937 and 0.941 on the control; 0.831 at 10,000 draws. The real series' left tail drives it (0.929 with its one September 2019 day removed).
- Calibration (Eleonora's ruling on PR #695, a §13 change): the critical value calibrated on the development history, largest across B2 − B1 and B3 − B1, is 5.45 at 250 days (9.50 at 125; none at 60), against 1.66 uncalibrated. Out of sample the bound then covers 1.000 of B2 − B1 windows, 0.951 of B3 − B1 windows and 1.000 of the control's; under no true difference (#699's size check) it detects on 0.3% of paths by 250 days, against 23.3% uncalibrated.
- Against kill: the second check failed as first written, and passes with the calibrated value; per Eleonora's ruling no candidate is registered until #656's power study confirms coverage.
- Next: prospective logging and the power study (#656).

### 2026-10-13 [H5] step 3 · eleonorabjornberg/repo-market-model#723
- Directive: #683
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; base `374fe3d`
- Tried: the reliability slope of earlier result pages read inside regimes and not pooled: a shared helper with bootstrap intervals, the per-regime slopes already in #624's tracked evidence, dated notes on the pages that reported pooled slopes. Variants: n/a (correction).
- Result: `+offday` of #624 at h = 1 has a pooled slope of 0.83, 0.48 inside 2018-19 and 0.79 inside 2025-26; at h = 3 to 5, 0.14 to 0.22 inside 2018-19 against a pooled 0.78 to 0.80. #626's rows have no per-regime slope yet.
- Against kill: not applicable (a correction to how step 3 figures are read).
- Next: the per-regime slopes for #626's kinked page, and an account of why its rebuild never finishes, move to the follow-up directive #753 (Eleonora's ruling of 14 October 2026 on this pull request); any reliability-shape test (#628) is read within regimes.

### 2026-10-13 [H2] step 1 · eleonorabjornberg/repo-market-model#710
- Directive: #684
- Step: 1
- Tier: development
- Pins: published panel `4ddc3882…`; base `a69f6b9`
- Tried: #629's source screen and #631's derived-feature screen re-run unchanged on a panel that runs to 2026-09-03 (the opened near-blind tier), with a 2026 column; one shared end date, `repo_model.exploration.EXPLORATORY_END`. Then, on the scratch scored span ruled on #710 (no published declaration moves), #631's model test (ordinary-day AUROC of the parent and the lagged-pressure test) and #624's steps 1 and 2 against persistence-logistic and the raw as-of spread, re-run to the same day, rows that reproduce on main only. Variants: n/a (re-run).
- Result: the 2026 column is empty on both screens: 133 ordinary days and 2 pressure days (2026-01-02, 2026-02-18), under the declared minimum of 3. The 2018-2025 column reproduces the earlier page (82 pressure days on 1,469 ordinary days). #629 has 87 series, not 101: the 14 `fed_repo_*` series cannot be read in 2026 (the repo-operations snapshot ends 2025-12-31). #631's ranked leads move by one entry (`spread_rv5` enters, `days_since_pressure` becomes redundant). The 2018-2025 cells of #631's model test and of #624's steps 1 and 2 reproduce the earlier pages to the digit; the 2026 days (2 pressure days) move no AUROC by more than 0.02, and the conclusions stand: lagged pressure does not help (h = 1 difference -0.040 [-0.078, -0.013]), and the ordinary-day ranking is not beyond persistence-logistic or the raw as-of spread. The 2026 cell stays empty below the 3-pressure-day minimum. #624's three floor rows are not re-run, and the judge is not run on 2026 days.
- Against kill: not applicable (H2's kill is not tested here; development data never gives a verdict).
- Next: a 2026 repo-operations snapshot would restore the 14 series; nothing here is a verdict.

### 2026-10-13 [H1] step 1 · eleonorabjornberg/repo-market-model#737
- Directive: #655 (follow-up: Eleonora's answers to Q-E, Q-B and Q-C on PR #695, comment 6159852603)
- Step: 1
- Tier: development
- Pins: published panel `4ddc3882…`; base `e9ce416`
- Tried: each comparison read at its own calibrated critical value instead of the largest across pairs; look 1 futility only; futility one-sided at 0.05 at every look, non-binding, at a calibrated upper bound of skill.
- Result: the verdict reads the grid comparison's values, 2.43 at 250 days and 3.42 at 125 (B3 − B1 on five levels: 5.45 and 9.50); null false detections on the full development history 0.85% and 0.25% by 250 and 125 days (B3 − B1: 0.0%). Futility values 1.93, 1.56 and 1.45 at 60, 125 and 250 days. Power at these values stays low (14% for a 3% skill by 250 days), and the confirmation design goes to a separate study.
- Against kill: the second check passes at the grid comparison's value; no registration until the confirmation-design study is decided.
- Next: the confirmation-design study (horizon, statistic, MME).

### 2026-10-14 [H4] step 2 · eleonorabjornberg/repo-market-model#748
- Directive: #734
- Step: 2 (milestone M2, "Guard updated": the back-fill amendment of `docs/decisions/information-set.md` put in force)
- Tier: development
- Pins: published panel `4ddc3882…`; base `e9ce416`; posting instant from `metadata/backfill_posting.json` (2018-05-17)
- Tried: no experiment and no new variant. A decision-record change for Eleonora to merge: the "Proposed" banner and sentence removed, the established posting instant recorded. Variants: 0.
- Result: none scored. No code, declaration or published figure changes.
- Against kill: not applicable (no result).
- Next: step 3 follows Eleonora's decision on whether to register (step 4); the H5 models still need pre-2018 inputs the project does not hold.

### 2026-10-14 [H5] step 3 · eleonorabjornberg/repo-market-model#756
- Directive: #707 (sub-question 1: 2021-23)
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; scratch panel `da1412d0…`; the walks of #634 (PR #711), read unchanged; declaration `metadata/h5_step3_707.json`
- Tried: 6 variants, no new fit: three causal post-hoc transforms (shift by the trailing median error, best trailing scale, trailing shrink weight on B1) applied to 2 candidates (the phase 2 gbm and variant (c) of #634), on 748 decision days in 2021-23 of 1,868 (to 2025-12-23). Variants: 6, cumulative 15.
- Result: (c) loses to B1 in 2021-23, -30.4% [-54.7%, -13.5%]; the phase 2 gbm does not resolvably (-0.9% [-17.8%, +10.1%]). For (c) the remainder after a constant level and scale correction is 0.184 of the 0.216 bp gap (lower bound +0.087), read as regime transfer: the loss is -60.8% in 2022 and +1.0% in 2023. Shrink toward B1 closes the gap (+1.2% [-2.6%, +4.6%]); the level and scale remedies do not.
- Against kill: not applicable (no verdict; development data).
- Next: whether a shrink weight belongs in H5's candidate is for the choice of candidate (step 5); not decided here.

### 2026-10-14 [H5] step 3 · eleonorabjornberg/repo-market-model#756
- Directive: #707 (sub-question 2: the upper tail)
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; scratch panel `da1412d0…`; the walks of #634 (PR #711), read unchanged; declaration `metadata/h5_step3_707.json`
- Tried: 0 new variants; twCRPS above 0 bp of 2 candidates against B1 and B2 by as-of scarcity state and day type, with the coverage of the 90th and 95th percentile forecasts on days above 0 bp.
- Result: twCRPS skill pooled is +35.7% [+26.5%, +51.7%] against B1 and +21.3% [+8.8%, +34.4%] against B2 for (c) (+31.3% and +15.9% for the gbm); neither beats B2 in the abundant state, and neither has a resolved gain over B1 on quarter-end or tax-date targets. The q95 exceedance rate is 0.095 for (c) and 0.128 for the gbm (lower bounds 0.075 and 0.106, nominal 0.05) with a median PIT of 0.825 on days above 0 bp: under-dispersed, not mislocated pooled.
- Against kill: not applicable (no verdict; development data).
- Next: a state-dependent tail scale is not tested here; whether it is, is for the step 5 choice.

### 2026-10-14 [H1] step 2 · eleonorabjornberg/repo-market-model#751
- Directive: #733 (a design study for the confirmation test; no verdict, nothing registered)
- Step: 2
- Tier: development
- Pins: published panel `4ddc3882…`; base `6114a8e`; rule `docs/research/confirmation-design-733.md`, committed before the study ran
- Tried: six declared designs (the in-force test at 250 days; 375 and 500 days; lead 1 alone; a standardized statistic at 250 and 375 days), each calibrated afresh on decision days to 2025-12-31 (no later day read) and simulated for size and for power at 3% and 10% skill (2,000 paths per scenario). A post-hoc addendum re-reads them at the critical value calibrated on the one comparison S(B2) − S(B1) (PR #695, Q-E (b)). Variants: 6 designs, 2 readings.
- Result: at the critical value in force (the largest across four comparisons) no design has power: D0 to D2 under 1% at 3% and at 10% even on the post-2020 history, D3 2.6% and 3.9% there; the standardized D4 reaches 14.4% and 19.4% on the post-2020 history but fails size (8% to 13%). At reading (b) D0 reproduces PR #695's Q-E table on the post-2020 history (14.3% and 19.7% against 14.0% and 19.25%) with size 11.5%; every design fails size on that history. No design reaches 80% power at 3% or at 30% skill. The §7 rule's pick (D3) is the least bad of the admissible, not a useful design.
- Against kill: not applicable (H1 is a validity check, not a gain claim); the page's reading is that the confirmation design cannot confirm the 3% MME in 500 days as the test stands.
- Next: Eleonora decides the reading of the critical value (Q-E) and whether to change the MME or the days; a change is a draft decision record under §13.

### 2026-10-14 [H4] step 3 · eleonorabjornberg/repo-market-model#726
- Directive: #726
- Step: 3 (development nested test of the back-fill against H5's candidate, #634's gbm_funding; steps 1 and 2 were done in #661)
- Tier: development
- Pins: published panel `4ddc3882…`; extended panel `1e09ae43…`; base `49ff40d9`; declaration `metadata/backfill_h5_726.json`; resynced and re-scored on main at `31774b83` (the 250-day reference is now the grid comparison's calibrated value, #737; every other figure unchanged)
- Tried: the candidate trained without and with the 899 back-filled rows (only SOFR, IORB, volume, TGCR, BGCR and calendar columns carried, the rest blank and imputed by the fitter), 23 levels, leads 1 to 5, scored by the protocol's scorer on 1869 decision days. Variants: 1 new (the with arm), 5 fits.
- Result: 2018-19 grid CRPS 4.005 → 4.119, d −0.114 [−0.168, −0.061] (worse); all days d −0.001 [−0.038, +0.040]; 2018-19 90% coverage 0.688 → 0.659 (−0.029 [−0.064, +0.007]); 2024 and 2025-26 slightly worse, 2020 and 2021-23 better with intervals covering zero. Detail in `docs/pivot/backfill-h5-726-result.md`.
- Against kill: no development gain beyond the interval, so H4 is not supported by this test, as exploration only; the test is narrow, since the candidate's other inputs are imputed on back-filled rows.
- Next: step 4 is Eleonora's; which candidate and which reading of the blank inputs are her questions on the PR.

### 2026-10-14 [H7] step 1 · eleonorabjornberg/repo-market-model#749
- Directive: #747
- Step: 1 (model-repo side: the tie fix in `satiation.fit_level`, gating liquidity H7 step 2)
- Tier: development
- Pins: published panel `4ddc3882…`; scratch panels as in `scripts/satiation_587.py`; base `e9ce416d`
- Tried: no forecast variant. The tie rule of the fitted kink (relative tolerance 1e-9, "not identified" when the tied set spans more than one grid step) and a count of the walk-forward refits of the fitted-level rows of #587 and #626 (four rows, horizons 1 to 5) under old and new rule. Variants: 0.
- Result: no refit in any row, year or horizon is "not identified" and no level moves, so no earlier figure moves; the old rule reproduces the recorded levels for the structural and combined rows exactly (the projected row differs in 47 refits for a later feature change, not the tie). At a tolerance of 1e-4, 44 refits of each structural and combined row would be tied; none at 1e-6. Detail in `docs/pivot/satiation-ties-747-result.md`.
- Against kill: not applicable (no verdict; development data).
- Next: the liquidity repo bumps its parent pin to the merge commit and proceeds to H7 step 2 (eleonorabjornberg/repo-market-liquidity#41).

### 2026-10-14 [H5] step 2 · eleonorabjornberg/repo-market-model#731
- Directive: #688
- Step: 2
- Tier: development
- Pins: published panel `4ddc3882…`; base `49b5413`, origin/main merged at `9c749c60`
- Tried: 2 variants, each added to the every-day part of the two-part spread distribution of #632 (refitted at the protocol's 23 levels; the control): the announced bill settlement beside the as-of spread (#676), and a flag for the first three market days of the month (#677); a screen on the ordinary days with the as-of spread and scarcity state as controls (60 cells).
- Result: grid CRPS against the control, 1,868 decision days: bill settlement −0.10% [−0.49%, +0.28%]; window +1.03% [+0.50%, +1.61%], at h = 3 to 5 (+1.30%, +1.74%, +1.69%, each interval above zero), none at h = 1 and 2, and only in 2021-23 by regime (a regime with no ordinary pressure day); upper-tail twCRPS inside its interval for both. The screen's near-threshold bill contrast reproduces (13/44 against 5/60 at lead 1, none of it plain persistence) but does not carry into the distribution; the window's lead-1 rise is plain persistence. Detail in `docs/pivot/near-threshold-688-result.md`.
- Against kill: not applicable (H5's kill is by the protocol's futility rule; development days give no verdict).
- Next: whether the window flag belongs in #634's model after #634 lands (H5 step 2); the bill input's product form and bridged persistence are Eleonora's.

### 2026-10-14 [H5] step 3 · eleonorabjornberg/repo-market-model#773
- Directive: #755
- Step: 3 (reading only: distribution forecasts under regime change, for the 2021–23 and upper-tail diagnoses of #707)
- Tier: development
- Pins: none (no data, model or score); base `c0c4525`
- Tried: no forecast variant. A refresh of the literature scan of 30 September, read on 14 October 2026: regime-switching and time-varying quantile models, combination with time-varying weights, online and conformal recalibration newer than the recalibration track, and tail modelling for a bounded spread. Variants: 0.
- Result: `docs/research/literature-2026-10.md`. Nothing found that fits a short-horizon spread directly; five leads, three for H5 (quantile-wise combination, tail calibration with twCRPS, conformal with a state predictor). No similar public SOFR − IORB forecasting project dated after 30 September was found.
- Against kill: not applicable (reading only; development).
- Next: Eleonora or the orchestrator decides whether any lead is queued, in plan order.

### 2026-10-14 [H1] step 3 · eleonorabjornberg/repo-market-model#773
- Directive: #755
- Step: 3 (reading only: the power of forecast comparisons, for #754's three families)
- Tier: development
- Pins: none (no data, model or score); base `c0c4525`
- Tried: no variant. Tests of equal predictive accuracy with serial dependence and heavy tails, anytime-valid sequential comparisons, and how confirmation periods are sized, read on 14 October 2026.
- Result: `docs/research/literature-2026-10.md`. Power at 60 to 125 days depends mainly on the dependence and tail weight of the CRPS differences, which no test choice changes; the sequential tests need a declared cap and are weakest at horizons above 1. No source sizes a confirmation period for a CRPS comparison, and none quantifies a sign test under dependence: gaps.
- Against kill: not applicable (reading only; development).
- Next: #754 starts after #733 and #737 merge; leads 3 and 4 of the page bear on it.

### 2026-10-14 [H5] step 2 · eleonorabjornberg/repo-market-model#767
- Directive: #761
- Step: 2
- Tier: development
- Pins: published panel `4ddc3882…`; scoring protocol v1 scorer and benchmarks B1, B2; seed 761; base as in the pull request
- Tried: 3 variants of `spread_mr_level10`: (i) residuals pooled by the target day's context, (ii) a quantile average with B2 whose weight is chosen at each refit on trailing scored days, (iii) both; B1 re-centred on the last ordinary day as a reference row. Variants: 3 (declaration `metadata/spread_distribution_761.json`).
- Result: grid CRPS 1.737 / 1.780 / 1.745 bp against mean reversion's 1.778 over 1,855 decision days to 2025-12-31; gain over mean reversion, studentized 90%: (i) +2.3% [+1.0%, +3.6%], (ii) -0.1% [-4.5%, +3.1%], (iii) +1.9% [-2.7%, +5.2%]. Upper-tail twCRPS (i) +4.1% [+2.4%, +5.8%]. (i) loses in 2020 (-5.9%) and 2021-23 (-0.3%); (ii) loses after a risk day (-4.3%). Calm ordinary-day P(> +5 bp) error: mean reversion -0.046, (i) -0.021, (iii) -0.006. Detail in `docs/pivot/spread-mr-variants-result.md`.
- Against kill: not applicable (no verdict; development data). Only (i) has an interval above zero against mean reversion.
- Next: whether (i) joins #634's candidates is Eleonora's.

### 2026-10-14 [H1] step 3 · eleonorabjornberg/repo-market-model#762
- Directive: #762
- Step: 3 (is each benchmark computed as specified: B1, B2 and `richer_targets.b1_quantiles` on a simulated panel with known dynamics; finding #744)
- Tier: development
- Pins: no panel (simulated data only); simulator `tests/benchmark_simulation.py`, seeds 762000 to 762199; base `c0c4525`
- Tried: an AR(1) spread with day-type levels on the market calendar, run through the benchmarks under the registry's availability declarations. Alignment asserted on a ramp, on level-only and on AR(1) panels; central 90% coverage measured against the known conditional law, not asserted. Variants: 1 process.
- Result: the ruled alignment holds (anchor = last public row; B1 adds h-row changes; B2 = same-type trailing-year climatology), and three recorded mutations fail it. Coverage of the central 90% is below 0.90 at every lead: B1 0.804 [0.802, 0.805] at lead 1 to 0.889 [0.887, 0.890] at lead 3; B2 0.863 to 0.870. B1's shortfall is the one-row gap between its anchor and h-row changes; B2's sits in the rare day types. Detail in `docs/research/benchmark-simulation-762.md`.
- Against kill: no pre-registered check failed; coverage is reported, not a check. B1's definition is Eleonora's, so the departure is a marked question.
- Next: Eleonora's answer on B1's change span and on whether the coverage matters to protocol v1.

### 2026-10-15 [H1] step 3 · eleonorabjornberg/repo-market-model#784
- Directive: #741
- Step: 3 (are the benchmarks right: does a forecaster that only declines to copy a calendar spike beat B1 by the MME; finding #741)
- Tier: development
- Pins: simulated data only for the test (`tests/benchmark_simulation.py`, seeds 741000 to 741199); published panel `4ddc3882…` for the H5 page split; base `9674324`
- Tried: B1 with its anchor replaced by the last ordinary-day spread at or before the anchor (no parameter, no ordinary-day skill, B1 exactly on ordinary anchors), on #762's AR(1)-plus-day-type-levels process, 200 panels, and on a no-spike control. Variants: 1 forecaster. And the split of #686's page by the type of the anchor.
- Result: on the declared process the forecaster beats B1 by +17.58% [+17.33%, +17.84%] pooled, every panel at or above the 3% MME, all of it from spike anchors (ordinary 0.00%; month-end +52.3%, tax date +32.6%, quarter-end +84.5%); with no spikes it has no gain (-1.27% [-1.54%, -1.01%]). Candidate evidence (a) for a §13 change; B1, B2, B3 and the MME unchanged. #686's candidate against B1 by anchor type on the development days: pooled +22.3% [+13.7%, +29.5%], ordinary anchors +11.2% [+6.9%, +15.9%], month-end +34.2%, tax date +67.5%, quarter-end +65.9%. Detail in `docs/research/spike-blind-741.md`.
- Against kill: not applicable (H1's checks are pre-registered; none failed, none run).
- Next: the auditor's confirmation of the candidate evidence and Eleonora's decision on §13; H5 pages still in open pull requests take the anchor split when they merge.

### 2026-10-13 [H5] groundwork G3 · eleonorabjornberg/repo-market-model#699
- Directive: #656
- Step: groundwork G3 (prospective logging)
- Tier: development
- Pins: published panel `4ddc3882…`; base `09640f5`
- Tried: record version 3 with a protocol block (B1, B2, B3 note, candidates, H7m hook). Variants: n/a.
- Result: no figure; the prospective log carries the protocol block (copied from the fenced block of PR #699, which the log could not hold until #701).
- Against kill: not applicable (groundwork).
- Next: Eleonora's decisions on the MME and the test's size; the auditor's check of §12 items 1-3.

### 2026-10-13 [H5] groundwork G4 · eleonorabjornberg/repo-market-model#699
- Directive: #656
- Step: groundwork G4 (power study)
- Tier: development
- Pins: published panel `4ddc3882…`; base `09640f5`
- Tried: a power study of the 3% MME under the protocol's test and spending. Variants: n/a.
- Result: 3% is not detected within 250 days (power 0.16 at 125, 0.29 at 250 against a 0.80 target); look 1 (60 days) cannot be read with 10,000 draws; post-hoc, the test fires on 21.75% of paths with no true difference by 250 days.
- Against kill: not applicable (groundwork).
- Next: Eleonora's decisions on the MME and the test's size; the auditor's check of §12 items 1-3.

### 2026-10-14 [H5] step 4 · eleonorabjornberg/repo-market-model#775
- Directive: #758
- Step: 4 (the best candidate against H2's ceiling; stacked on #634)
- Tier: development
- Pins: published panel `4ddc3882…`; scratch panels `92bf10a4…` (ceiling fits) and as in `scripts/spread_distribution_634.py`; base `1bbee114`; declaration `metadata/h5_step4_758.json`
- Tried: no new model. H2's cross-fitted and reachable gradient-boosted fits rerun, and #634's `gbm_funding` and variant (c) walks rerun, scored on H2's 1,598 walk-forward days by the protocol's grid CRPS against B1. Variants: 0.
- Result: best candidate `gbm_funding` +0.257 [+0.114, +0.400] against B1 on ordinary targets, ceiling +0.168 [+0.003, +0.316], reachable line +0.196 [+0.019, +0.354]; headroom of the ceiling −0.090 [−0.161, −0.019]. Shown in one of 13 cells: regime 2024 (+0.110 [+0.027, +0.160]). The rerun differs from H2's recorded skills by 0.004 to 0.006. Detail in `docs/pivot/h5-step4-result.md`.
- Against kill: not applicable (no verdict; development data).
- Next: step 5, the model-risk validation report for `gbm_funding` (Eleonora's ruling of 15 October 2026: stop model work); the 2024 split is an avenue, not a next step.

### 2026-10-14 [H5] step 5 · eleonorabjornberg/repo-market-model#732
- Directive: #732
- Step: 5 (the running variant count that every registration publishes, §2 of the protocol)
- Tier: development
- Pins: no panel (counting and a declaration check only); base `978dbcd`
- Tried: no forecast variant. The progress page's variant count now reads every `metadata/*.json` that has a `variants` block (top level, or under `model`), by content and not by file name (ruling of 14 October 2026); a CI test refuses a model declaration with no `hypothesis` key or no `variants` block, with the 23 declarations that predate the rule listed as exempt.
- Result: the count moves from 2 declarations and 4 variants (the files named `spread_distribution_*`) to 19 declarations and 55 variants. `near_threshold_688.json`, the case that found the gap, is now seen (3 variants, under `model`). The 55 include the pre-pivot +5 bp classification variants as well as spread-forecast ones, because the ruling counts by content.
- Against kill: not applicable (no verdict; a count, not a score).
- Next: Eleonora's call on converting the exempt declarations to carry `hypothesis`, and on whether the page should show the count by hypothesis.

### 2026-10-14 [H5] step 5 · eleonorabjornberg/repo-market-model#776
- Directive: #740
- Step: 5 (goal G3, prospective logging; Eleonora's ruling that a block is written and committed before 23:59 ET on its decision day)
- Tier: development
- Pins: no panel and no scoring; tracked fixtures only; base `b0da43a`
- Tried: a write-time guard at 23:59 ET on the decision day (`require_written_by_decision_day_end`), `written_at` stored in every block, and `filled_candidate` refusing a stored `written_at` or commit time past the cut-off. Variants: n/a (a guard, no model).
- Result: the oracle block of the finding, written the evening after its decision day, is now refused; two recorded mutations kill the guard and the commit-time check. Nothing published moves and no registration is made.
- Against kill: not applicable (no hypothesis test).
- Next: the registration waits on the confirmation design (#733); no candidate is logged yet.

### 2026-10-15 [H3] step 1 · eleonorabjornberg/repo-market-model#788
- Directive: #743
- Step: 1 (screening; data meaning of the Fed repo take-up columns, after #692/#727)
- Tier: development
- Pins: published panel `4ddc3882…`; base `9674324b`
- Tried: one take-up floor ($0.1 bn accepted, every era) for the Fed repo columns; the two #727 results re-run on the rebuilt column (the source matrix, and `risk_logistic_base_dealer` at h = 1 to 5, with the column present and removed). Variants: 1 (the floor).
- Result: the ordinary-day pressure AUROC of `fed_repo_days_since_positive` falls from 0.64 [0.48, 0.79] to 0.50 [0.35, 0.65] at lead 1 and from 0.68 [0.51, 0.82] to 0.54 [0.39, 0.67] at lead 10, all intervals containing 0.5. The 2018 warnings of `risk_logistic_base_dealer` (3 of 5 onsets) are the same with the floor and with the column removed, so they do not rest on it.
- Against kill: not applicable (no verdict; development data).
- Next: Eleonora's answer on whether the floor applies to `srf_total_accepted` (a "Publish?" issue); H5 step 2 inputs.

### 2026-10-15 [H1] groundwork G1 · eleonorabjornberg/repo-market-model#810
- Directive: #795
- Step: groundwork G1 (research-log infrastructure, #638; the hypothesis tag is the nearest fit and is a question in the PR)
- Tier: development
- Pins: no panel and no scoring; base `6871c94`
- Tried: `check_research_log.py check` now refuses a git conflict marker (a line starting `<<<<<<< ` or `>>>>>>> `, or exactly `=======`) and names the line, in the log and in every tracked Markdown file. Variants: n/a (a check, no model).
- Result: the conflict block that reached main on 15 October (#794) would now fail the check; the tracked Markdown has none.
- Against kill: not applicable (groundwork).
- Next: none for this item.

### 2026-10-15 [H1] step 3 · eleonorabjornberg/repo-market-model#792
- Directive: #754 (power tested a different way; a design study, no verdict, nothing registered)
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; base `801d4e7a`; rule `docs/research/power-replay-754.md`, committed before the study ran
- Tried: windows of 60, 125 and 250 days slid every 5 days over real forecast pairs (B3 against B1; B2 against B1 and the reverse) and over three known-equal series (a relabelled copy, the demeaned pair, block sign-flips), and bootstrap paths of 60 to 500 days at true skill 0 to 50%; three test families (the current test with its critical value calibrated on circular blocks and on the path generator, a fixed-b Diebold-Mariano test, a betting e-process on lead 1 and on leads 1 to 5). Days after 2025-12-31 are not read. Variants: 5 families, 4 series.
- Result: only B3 against B1 is a known-better pair (skill 21.8%); B2 scores worse than B1. At that gain the current test flags 66% to 73% of windows but flags 26% to 33% of sign-flipped B3 windows, so its size on a symmetric null is far above 5%; the fixed-b test flags 27% to 34% of the real windows and 4% to 10% of the sign-flipped. Synthetic gated power at a 3% gain, 250 days: 10% (current), 8% (matched null), 3% (fixed-b), 0% (e-process, whose bounded bets never grow on these scores). No family reaches 80% power at any gain up to 50% in 250 days; the current test does at 50% in 500 days. By normal-theory arithmetic the daily signal-to-noise of B3's 22% gain needs about 1,300 days. The rule's pick (the e-process on lead 1) holds the size limit with 0% power.
- Against kill: not applicable (H1 is a validity check; development).
- Next: Eleonora's questions on the page (a test with no power at the MME, the current test's size on a symmetric null, a variance-adaptive sequential test); #769 re-runs the power study on the test in force.

### 2026-10-13 [H7] groundwork G5 · eleonorabjornberg/repo-market-liquidity#44
- Directive: #27 (L3, SLR headroom, with answer 16), step 1 only
- Step: groundwork G5 for H7m, before step 2 candidate D
- Tier: development
- Pins: parent repo-market-model 09640f5; panel 4ddc3882cd6d406b11e1088f8ff6195e16dde175a0ad6818abe40dd5bdac8999
- Tried: read four quarters of the FFIEC CDR Call Report bulk files (2018-03-31, 2021-03-31, 2023-06-30, 2025-12-31) for the nine G-SIB depository subsidiaries and all filers, against the filing deadline
- Result: first-filed figures are not recoverable from the public bulk files; for most G-SIB subsidiaries the file holds an amended figure last updated 30 to 1,611 days after quarter-end. No input built, nothing scored
- Against kill: no goalpost is tested here; this is an input question
- Next: the overlay, declaration, tests and snapshot of #27 under reading 2 (a new directive), and the archive (#46)

### 2026-10-14 [H10] step 1 · eleonorabjornberg/repo-market-liquidity#66
- Directive: eleonorabjornberg/repo-market-liquidity#62
- Step: H10 method amended before step 2 (finding #52)
- Tier: development
- Pins: model 09640f5, panel digest none (synthetic series only), snapshot none
- Tried: a selection-aware null and ON RRP as a driver, on synthetic episodes; variant count 1
- Result: method amended, nothing scored
- Against kill: not applicable
- Next: H10 step 2 once the record is merged

### 2026-10-14 [H7] groundwork G5 · eleonorabjornberg/repo-market-liquidity#67
- Directive: #63 (L14, SLR headroom as a labelled latest-filed input), steps 2 to 6 of #27
- Step: groundwork G5 for H7m, before step 2 candidate D
- Tier: development
- Pins: parent repo-market-model 09640f5; panel 4ddc3882cd6d406b11e1088f8ff6195e16dde175a0ad6818abe40dd5bdac8999
- Tried: built the overlay, declaration, guards and snapshot for the latest-filed SLR headroom of nine G-SIB depository subsidiaries from 34 CDR bulk quarters, 2018-03-31 to 2026-06-30
- Result: inputs built, nothing scored; 277 of 306 bank-quarters in the extract, the rest listed with reasons; headroom blank from 2026-04-01 (requirement not set in row 16); State Street's filed exposure not credible
- Against kill: no goalpost is tested here; this is an input
- Next: Eleonora's answers to Q1 to Q3; then H7 step 2 candidate D may read this snapshot

### 2026-10-14 [H7] groundwork G5 · eleonorabjornberg/repo-market-liquidity#72
- Directive: #71 (her decision on #69)
- Step: groundwork G5 for H7m candidate D: the SLR requirement table (draft), State Street as a labelled sensitivity, the day-after rule
- Tier: development
- Pins: parent 09640f5; panel digest unchanged (4ddc3882…); slr_headroom 998c5aa1… to 09c138ad…
- Tried: read the requirement from the OCC rule text (eCFR as of 2018-01-01, 2026-03-31, 2026-10-01); made the headroom read a per-period table; re-cut the snapshot with a measure column
- Result: inputs revised, nothing scored; no figure moved; the headroom stays blank from 2026-04-01 pending her answer to open question 1
- Against kill: not applicable; nothing scored
- Next: H7 step 2 (#41), after #43 and #65, once she has ruled on the draft

### 2026-10-14 [H10] step 2 · eleonorabjornberg/repo-market-liquidity#73
- Directive: eleonorabjornberg/repo-market-liquidity#70, H10 step 2: record her section 9d answers, then apply the declared method to the development onsets.
- Step: 2 of 3 (apply it to every development onset, once, at a pin).
- Tier: development
- Pins: parent 53e61af9b4175e854c196908d3c76b228c039667; panel version 1 acb77874e0ca2c9eeee1c33a229f5e12745e65bb1224088d52c391dbf54be2ab; seed 20261013; 31 onsets to 2026-09-03.
- Tried: the leave-neighbourhood-out regression with Shapley shares over five drivers (ON RRP included), 10,000 bootstrap draws per episode, 20 placebo windows, the reserves-only benchmark, and the N1 selection-aware null (1,000 draws, 95th percentile bar 0.234).
- Result: under the residual bar 4 of 31 (6% to 26%); beating the null 14 of 31 (31% to 60%); both 4 of 31 (6% to 26%). Median residual share 0.78 (0.66 to 0.85); explained share above reserves alone 0.23 (0.13 to 0.37); placebo gap -0.39 (-0.62 to -0.19). The development table reads residual dominates.
- Against kill: the plan's outcome rule needs more than half the episodes under the bar; the development table has 4 of 31. Development data never gives a verdict; this is not one.
- Next: step 3 (publish the table) after her review; the ON RRP interaction sensitivity of answer 5.

### 2026-10-15 [H10] step 3 · eleonorabjornberg/repo-market-liquidity#78
- Directive: eleonorabjornberg/repo-market-liquidity#77, H10 step 3: publish the development table, with the ON RRP interaction sensitivity.
- Step: 3 of 3 (publish the table).
- Tier: development
- Pins: parent 53e61af9b4175e854c196908d3c76b228c039667; panel version 1 acb77874e0ca2c9eeee1c33a229f5e12745e65bb1224088d52c391dbf54be2ab; seed 20261013; 31 onsets to 2026-09-03; method record sha256 cae658c6d9a895d4db8f6427c81a11f7310fc79377528d71806e9f209c28f126.
- Tried: rendered the step 2 record unchanged as a generated page; re-ran the step 2 application with ON RRP as on_rrp x 1(on_rrp < 100 bn) in place of its window change, as a sensitivity (the abundant regime has 2 onsets).
- Result: what the development table shows: under the residual bar 4 of 31 (6% to 26%), beating the null 14 of 31 (31% to 60%), both 4 of 31 (6% to 26%); reads residual dominates. Sensitivity (labelled as such): 5 of 31 (8% to 30%), 16 of 31 (37% to 66%), both 5 of 31 (8% to 30%); also reads residual dominates.
- Against kill: the plan's rule needs more than half the episodes under the bar; the development table has 4 of 31. Development data never gives a verdict; this is not one.
- Next: her review; registering the frozen method is her attested action.

### 2026-10-15 [H1] step 1 · eleonorabjornberg/repo-market-model#791
- Directive: #769
- Step: 1 (the power study re-run on the test in force after ruling 5)
- Tier: development
- Pins: calibration record `docs/research/protocol-calibration/result.json`; base `31774b83`
- Tried: #656's power study re-run at the calibrated critical values (3.42 at 125 days, 2.43 at 250, look 1 futility only, MME gate) under four readings: the full or the post-2020-04 history, and circular-block or stationary-bootstrap paths. Variants: 4 readings, 9 cells each.
- Result: a true 3% skill is detected on 0.8% (full history, circular), 7.8% (post-2020-04, circular), 1.8% (full, stationary) and 13.9% (post-2020-04, stationary, #656's own) of paths by 250 days; none reaches 80% at either look, so days needed and the smallest skill detected at target power are null in every reading. Size with no true skill by 250 days: 0.5%, 6.1%, 1.3% and 10.9%. Detail in `docs/research/power-study-769-result.md`.
- Against kill: not applicable (groundwork; development data gives no verdict).
- Next: Eleonora settles the MME, B3's verdict rule (#768) and the confirmation design (#754, #733) after this result.

### 2026-10-15 [H6] step 1 · eleonorabjornberg/repo-market-model#783
- Directive: #739
- Step: 1 (the re-read of #693's development kill rule on the studentized bootstrap of protocol ruling 1; Eleonora's ruling on #739)
- Tier: development
- Pins: published panel `4ddc3882…`; scoring protocol v1 scorer and benchmark B1, unchanged (ruling 6); seed 693; base `9674324`
- Tried: no new model. #693's 2 candidates on the same 383 risk target days, benchmarks and seed, with the interval read as skill − q·se on the studentized draws instead of the percentile of the draws. The calibrated critical value is not used (it belongs to checkpoints). Variants: 0.
- Result: no development skill. The H5 mean-reverting row's pooled CRPS skill against B1 is +3.18% [−0.90%, +6.03%] (the percentile lower bound was +0.03%); its MAE skill against B1 is +0.70% [−3.00%, +3.12%]. Against the calendar benchmark CRPS skill is +26.80% [−2.58%, +46.79%]. By regime, CRPS skill against B1 is +4.45% in 2018-19, −1.82% in 2020-24 and +5.70% in 2025-26, every interval covering zero. Detail in `docs/research/risk-date-reread-739.md`. The entry of #719 is not edited.
- Against kill: killed on the declared development rule (skill against both benchmarks on CRPS or MAE: none). H6 stays open: its kill is by futility on prospective days.
- Next: #724 (H6 step 2) is out of the queue until H5 step 5 (ruling on #739).

### 2026-10-15 [H5] step 2 · eleonorabjornberg/repo-market-model#822
- Directive: #804 (re-score of #688/#731 on the studentized interval of ruling 1)
- Step: 2 (the same two inputs and control; no new variant)
- Tier: development
- Pins: published panel `4ddc3882…`; base `8474e69`; walks refitted from the declared `metadata/near_threshold_688.json`, screen byte-identical to the earlier record
- Tried: no new forecast variant. #731's score used the percentile bootstrap that ruling 1 replaced; the 15 walks were refitted and scored with the scorer's studentized bounds at both ends, and a pair the scorer cannot studentize now carries no interval instead of stopping the run. Variants: 0 new (2 re-scored).
- Result: grid CRPS against the control, the window flag +1.03% [+0.44%, +1.64%] (was [+0.50%, +1.61%]), still above zero at h = 3 to 5 (+1.30% [+0.39%, +2.18%], +1.74% [+0.80%, +2.65%], +1.69% [+0.88%, +2.53%]); bill settlement −0.10% [−0.54%, +0.28%] (was [−0.49%, +0.28%]). One cell crosses zero: the window's pinball loss at 0.05, +1.09% [−0.03%, +2.23%]. Against B1 the control is +19.26% [+10.55%, +39.09%] (was [+8.36%, +28.35%]). Quarter-end days: identical forecasts; tax-date days: no interval. Point values unchanged. Detail in `docs/pivot/near-threshold-688-result.md`, section "Re-score on the ruled interval (#804)".
- Against kill: not applicable (development days give no verdict).
- Next: none for this item; the window flag's place in #634's model stays an H5 step 2 question for Eleonora.

### 2026-10-13 [H2] step 3 · eleonorabjornberg/repo-market-model#728
- Directive: #685
- Step: 3 (judge hygiene for an exploratory tier report; no model is scored)
- Tier: development
- Pins: published panel `4ddc3882…`; base `fa333ae7`; the judge in force, unchanged
- Tried: 0 model variants; the always-flag reading of tier 1 amended to option B (a flag from an always-flag block is not a warning but still a false alarm, Eleonora's ruling of 13 October 2026 on #666), and `ngboost_laplace` and the three benchmarks re-scored with it off and on.
- Result: `ngboost_laplace` 17 to 13 of 26 onsets warned, 2.34 false alarms per onset in both readings, tier 1 fails (the #588 draft passed it at 1.81 only because the dropped flags also left the false alarms). The benchmarks lose most of their 2019 warnings (calendar climatology 12 to 2, persistence-logistic 12 to 4, `published_v1` 14 to 8) and fail either way.
- Against kill: not applicable (no verdict; the +5 bp judge is retired as a decision rule, #640).
- Next: Eleonora decides whether the amended draft record `docs/decisions/always-flag-blocks.md` merges.

### 2026-10-15 [H5] step 2 · eleonorabjornberg/repo-market-model#815
- Directive: #799
- Step: 2 (the re-score of #761's variants after the as-of fix; finding #799)
- Tier: development
- Pins: published panel `4ddc3882…`; scoring protocol v1 scorer and benchmarks B1, B2; seed 761; declaration `metadata/spread_distribution_761.json` unchanged
- Tried: `spread_mr_ctx` and `spread_mr_ctx_b2` re-scored with the target's and the previous row's coupon settlement counted only where the registry makes it public at the decision instant (`asof.declared_availability`: the panel day before, 15:00), in the pools and in the forecast. Variants: 3 (the same as #767; no new variant).
- Result: grid CRPS 1.750 / 1.780 / 1.759 bp against mean reversion's 1.778; gain over mean reversion, studentized 90%: (i) +1.6% [+0.2%, +2.9%] (was +2.3% [+1.0%, +3.6%]), (ii) -0.1% [-4.5%, +3.1%] (unchanged), (iii) +1.1% [-3.4%, +4.5%] (was +1.9% [-2.7%, +5.2%]). Upper-tail twCRPS (i) +2.4% [+0.2%, +4.3%] (was +4.1% [+2.4%, +5.8%]). (i) in 2020: -6.7% [-9.8%, -3.7%] (was -5.9% [-10.7%, +0.8%]). Detail in `docs/pivot/spread-mr-variants-result.md`.
- Against kill: not applicable (no verdict; development data). (i) keeps an interval above zero against mean reversion; part of the earlier gain came from the read that bypassed the as-of rule.
- Next: whether (i) joins #634's candidates is Eleonora's, on these figures.

### 2026-10-15 [H2] step 3 · eleonorabjornberg/repo-market-model#828
- Directive: #811
- Step: 3 (a record trace: why H5 step 4's rerun of H2's ceiling did not rebuild H2's declared panel)
- Tier: development
- Pins: published panel `4ddc3882…`; H2 tree `ec534758`; base `09f2409c`; scratch panels `08df8d19…` (H2's declaration), `92bf10a4…` (H5 step 4), `69be91b6…` (main today)
- Tried: 0 new model variants; rebuilt the scratch panel at H2's tree and at main with #679 and #743 each left out, and re-fitted H2's ceiling and reachable fits on H2's two panel orderings with current main code
- Result: the difference is in the build, not the inputs. `08df8d19…` rebuilds exactly (two satiation columns placed as declared); `92bf10a4…` is main without #743; its only value difference from H2's is `net_settlement_due_5d` (#679). Both controls reproduce H2's recorded skill against B1 (reachable +0.192 [+0.007, +0.352], ceiling +0.162 [-0.009, +0.310]) to every digit; H5 step 4's panel gives +0.196 [+0.019, +0.354] and +0.168 [+0.003, +0.316]. No published figure moves
- Against kill: not applicable (a reproducibility trace; no hypothesis is tested)
- Next: Eleonora's two marked questions on the page (which ceiling stands for H5 step 4; the ceiling interval that now excludes 0); a fit on today's main panel is not made

### 2026-10-15 [H5] step 2 · eleonorabjornberg/repo-market-model#827
- Directive: #725 (the three reliability-slope helpers call the shared fit)
- Step: 2 (groundwork; no forecast scored)
- Tier: development
- Pins: base `028ab0a`; no panel read
- Tried: no new variant. `off_risk_day_624.py`, `kinked_626.py` and `spread_distribution_632.py` call `reliability_regimes.fit` instead of their own Newton loops. Variants: 0.
- Result: the helpers agree with the old ones to 4e-13 (624), exactly (632) and within 5e-3 in small samples (626) on 1,840 synthetic cells; a cell on which the shared fit does not converge now reads undefined, which happened in 137 cells with forecasts far below the event rate. The published panels are not tracked, so no page was re-run.
- Against kill: not applicable (groundwork; development data gives no verdict).
- Next: Eleonora decides whether the shared fit gets a line search (question in the PR).

### 2026-10-15 [H5] step 3 · eleonorabjornberg/repo-market-model#817
- Directive: #801
- Step: 3 (calibration diagnosis of the kinked and #624 rows; per-regime reliability slopes, #683)
- Tier: development
- Pins: no panel and no scoring; tracked evidence of #624 only; base `8474e69f`
- Tried: the per-regime slope tables now mark `†` by the pressure days in the fit (those on forecasts above 1e-4) and read a regime that forecasts zero on every pressure day as `uncalibrated: zero on all N`; no fit re-run; variants: n/a (reporting).
- Result: no slope or other figure moves; 66 table cells change their mark only (24 in step 1, 42 in step 2) (for example `+tailcap75` at h = 1 in 2018-19: 1.39 now carries `†`, 2 events in the fit of 62 pressure days). The regime convention (three or five regimes) is left to Eleonora.
- Against kill: not applicable (no hypothesis test).
- Next: Eleonora's answer on the regime convention; the #624 slopes are not re-fitted on all days unless she asks.

### 2026-10-14 [H5] step 3 · eleonorabjornberg/repo-market-model#760
- Directive: #753
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; stacked on #723 (the shared reliability helper), with origin/main merged at `53e61af`
- Tried: #626's rows (the fixed and fitted-kink structural forms, the rolling form, the best tier-1 row) and the two references, rebuilt and tabulated for the reliability slope inside 2018-19, 2020-24 and 2025-26 and inside each as-of scarcity state, 90% bootstrap intervals. Variants: 0 new models.
- Result: inside 2018-19 (63 of 87 pressure days) the structural rows read 0.18 to 0.27 (fixed and fitted kink) and 0.30 to 0.47 (rolling) at h = 1 to 5, intervals below 1; inside 2025-26, 0.98 to 1.51, intervals including 1; the pooled 0.39 to 0.74 is a mean of the two. The rolling form is nearer 1 than the other two only in 2018-19, and `persistence_logistic` is nearer than it at h = 1 to 4. Slow step found: the five-horizon rebuild of what the table reads is 16 minutes; the slow steps are `risk_date_severity.py` (a skew-t fit, about 0.6 s a day, not needed for this table) and the single-process bootstrap (about 26 minutes on four processes).
- Against kill: not applicable (a correction to how step 3 figures are read; development data, not a verdict).
- Next: #631's and #632's per-regime slopes need their own forecast chains rebuilt (not done here); any reliability-shape test (#628) is read within regimes.

### 2026-10-15 [H8] step 1 · eleonorabjornberg/repo-market-model#819
- Directive: #770
- Step: 1 (correction to the development score of #694: the calendar benchmark read a coupon settlement before it was announced)
- Tier: development
- Pins: published panel `4ddc3882…`; base `9eaecfb5`; seed 694; declaration `metadata/ranking_694.json` unchanged
- Tried: the calendar ranker counts a coupon settlement only at leads where its column is declared observable at the decision instant (ruling on #720, point 2), so at lead 1 under the published declaration; the model and the other benchmarks are untouched. Variants: 0 (a correction, no new candidate).
- Result: the calendar's top-5 precision falls from 13.0% to 9.4% (recall@5 from 56.8% to 37.7%); the probability ranker's top-5 precision gain over it moves from -5.2 pp [-7.7 pp, -3.0 pp] to -1.6 pp [-2.9 pp, -0.3 pp] over 1,825 decision days to 2025-12-31. Gains over persistence and climatology do not move. Detail in `docs/pivot/ranking-770-result.md`.
- Against kill: the kill condition (no ranking skill beyond the calendar of known risk dates) is still met on development data, as exploration and not a verdict: the interval still lies wholly below zero, by a third of the earlier gap.
- Next: step 2 (#765) reads the corrected calendar.

### 2026-10-15 [H5] step 3 · eleonorabjornberg/repo-market-model#820
- Directive: #805
- Step: 3 (the splits the headline pages of #634 and #707 lacked: by the anchor's day type, without decision day 2019-09-18, and the upper-tail Brier claims by regime and pressure-day type; no new model)
- Tier: development
- Pins: published panel `4ddc3882…`; base `06801bbd`; script `scripts/h5_splits_805.py`
- Tried: #634's 25 walks re-run on the rebuilt panels and scored with the protocol's scorer, all pooled figures reproduced exactly; then cut by anchor day type, without 2019-09-18 (real walk scores that day), by regime and target-day type for the Brier claims, and c at 125 and 250 days with and without the day. Variants: 0 new (re-score of the existing nine and #707's six transforms).
- Result: grid CRPS skill against B1, pooled → ordinary-anchor days → without 2019-09-18: gbm +20.7% [+13.3%, +40.0%] → +9.0% [+4.6%, +14.9%] → +14.9% [+10.3%, +21.3%]; (c) +20.3% [+11.0%, +38.0%] → +9.0% [+2.9%, +15.8%] → +14.5% [+7.7%, +22.2%]. The gain concentrates on days after a calendar spike. (c)'s Brier gain at +5 bp holds pooled (+19.0% [+13.7%, +23.7%] against persistence-logistic) and in 2018-19 and 2025-26, not in 2020; 2021-23 has no events. Detail in `docs/pivot/h5-splits-805-result.md`.
- Against kill: not applicable (no verdict; development data). H5's kill, no CRPS gain over phase 2 and no ordinary-day ranking gain, is not assessed here; the ordinary-anchor gain is resolved and about +9%.
- Next: #741 (does avoiding calendar spikes alone reach the pooled figure); the critical value and the MME are Eleonora's.

### 2026-10-15 [H5] groundwork G1 · eleonorabjornberg/repo-market-model#821
- Directive: #800 (the shared "not a risk date" function, asked by the code merged after #709)
- Step: groundwork G1 (the ordinary-day population across H2, H5, H6 and H8; no step of H5 itself)
- Tier: development
- Pins: published panel `4ddc3882…`; base `06801bbd`
- Tried: H5's `spread_mr_variants.is_risk_day` and H6's `risk_date_spread.risk_day_type` now decide through `risk_dates.is_risk_date` (`reporting_on=` reads the reporting day type); compared with the old answers on all 1873 scored days. Variants: none (no model).
- Result: no figure moves. H5's 386 risk days and H6's 386 (every type) are identical before and after. The shared definition read the calendar-day month-end window has 404; the two readings disagree on 58 days (20 only in the business-day reading, 38 only in the calendar-day one).
- Against kill: not applicable (groundwork).
- Next: Eleonora's question: which month-end window is the shared definition. The by-type groupings (H8 climatology, #707, #688, #639) stay as they are.

### 2026-10-14 [H4] step 2 · eleonorabjornberg/repo-market-model#777
- Directive: #742
- Step: 2 (milestone M2, guard updated: a per-series admitted list)
- Tier: development
- Pins: scratch panel `4137d0ad…`, extended panel `f3acce04…`, workbook `1c889930…`; base `978dbcd`
- Tried: no forecast variant and no new score. A guard that admits only listed series (TGCR, BGCR, SOFR, each from 2018-05-17), applied to the refits of #633's script and to `backfill_history.py run`; the recorded figures of #633 re-read by which series each rests on. Variants: 0.
- Result: the declared model of #633 reads the bill rate, reserves and the TGA from the back-filled rows and is now refused (`LookAheadError`); its pooled (+0.081 [+0.035, +0.133]) and 2021-23 (+0.149 [+0.061, +0.257]) CRPS gains rest on series that are not admitted. The workbook-only variant passes: pooled +0.032 [−0.002, +0.072], 2021-23 +0.033 [−0.041, +0.125], 2018-19 central-90% coverage +0.035 [+0.017, +0.054]. Detail in `docs/pivot/posting-dates-h4-result.md`.
- Against kill: not killed on the workbook-only variant (a posting time is established; the 2018-19 calibration move's interval excludes zero).
- Next: the Liberty Street copy as tracked evidence (fetch blocked here); whether IORB needs its own admitted instant (Eleonora); #726 against H5's candidate uses the workbook-only variant.

### 2026-10-15 [H5] step 5 · eleonorabjornberg/repo-market-model#824
- Directive: #803
- Step: 5 (variant count by content; groundwork for the registration's record of what was tried, #567)
- Tier: development
- Pins: no panel and no scoring; tracked fixtures only; base `06801bb`
- Tried: `scripts/emit_progress.py` reads every `metadata/*.json` for arms named `candidates` or `arms` (top level or under `model`), counts them apart from the `variants` figure, and lists declarations whose arms it cannot read; `tests/test_model_declarations.py` now checks every such file (`PRE_803` freezes the 44 that predate the rule). Variants: n/a (a count, no model).
- Result: the page still reads 22 declarations with a `variants` block, 65 variants. Beside it, 18 more files name 72 arms as `candidates` or `arms`, and 33 declarations carry no block the count can read. These are not added to the 65: what counts as a variant is Eleonora's question in the PR.
- Against kill: not applicable (no hypothesis test).
- Next: Eleonora's reading of what counts as a variant under protocol section 2.
- Next: Eleonora's two marked questions on the page (which ceiling stands for H5 step 4; the ceiling interval that now excludes 0); a fit on today's main panel is not made

### 2026-10-14 [H9] step 2 · eleonorabjornberg/repo-market-model#774
- Directive: #706
- Step: 2
- Tier: development
- Pins: scratch panel `26c51093…`; base `c0c45259`; declaration `metadata/richer_targets_706.json`; stacked on #711 (#634)
- Tried: the three targets chosen by Eleonora's rule of 13 October on step 1's tables (BGCR 99th − 1st percentile, ON RRP daily change, SOFR 99th − 1st percentile) modelled with #634's candidate (b) (gradient-boosted 23-level quantiles, same inputs, the target's own lag), leads 1 to 5, scored by the protocol's grid CRPS against each target's own B1 and B2. Variants: 1 model, 3 targets.
- Result: skill over B1 +0.329 [lower +0.271], +0.310 [+0.286], +0.330 [+0.241]; over B2 +0.156 [+0.080], −0.103 [−0.142], +0.155 [+0.054]; the spread (#634 b) +0.201 over B1 and +0.268 over B2. Negative on quarter-end target days for all three. No lead on the +5 bp episodes in the scarce state (pre-onset AUC of the modelled median 0.38, 0.53, 0.39, intervals not above one half). Detail in `docs/pivot/richer-targets-706-result.md`.
- Against kill: `H9.md`'s wording ("no skill over the target's own persistence, and no nested gain for H5", Eleonora's ruling of 15 October 2026) cannot be assessed until step 3's nested test; on development data skill over persistence is shown for all three targets and a lead on the +5 bp episodes for none. Not a verdict.
- Next: the nested test with H5's best candidate (H9 step 3), after #634 merges.

### 2026-10-15 [H4] step 2 · eleonorabjornberg/repo-market-model#790
- Directive: #781
- Step: 2 (milestone M2, evidence for the posting instant: the Liberty Street copy)
- Tier: development
- Pins: none (no panel read, no score); base `236d175`
- Tried: no forecast variant and no new score. The Liberty Street post on the revised broad Treasuries financing rate fetched, tracked with its sha256 and cited on the posting-dates page. Variants: 0.
- Result: the page's editor's note dates a correction of the linked historical-rates file to May 17, 2018 and gives no time of day; it does not state a first posting.
- Against kill: not applicable (evidence for the posting-instant ruling; no figure moves).
- Next: Eleonora's read of whether the correction note supports the 17 May 2018 ruling; whether the linked data file is fetched too.

### 2026-10-15 [H5] step 2 · eleonorabjornberg/repo-market-model#779
- Directive: #738
- Step: 2 (the settlement family of inputs: a cash management bill is unknown until its own announcement)
- Tier: development
- Pins: no panel; tracked Treasury auctions fixture `20261008T205048Z_568c69347867`, decision days 2018-01-01 to 2026-09-03; base `68574916`
- Tried: 1 rule change (a CMB counts toward a bill class's partial status only from its own announcement), compared with the rule of #679 on the (day, lead 1-5) cases, split by declared regime; the ahead columns rebuilt both ways. Variants: 1.
- Result: 38 of 4,972 cases change. On them the mean absolute error against the completed net falls from 71.6 to 42.2 bn (2020: 96.9 to 47.3 on 22 cases; 2025-26: 36.0 to 50.0 on 2); over all cases 1.9 to 1.6. 68 `ahead_columns` cells move, 43 of them in 2020. No published figure moves. Detail in `docs/pivot/evidence/cmb-point-in-time-738/result.md`.
- Against kill: not applicable (an input-timing correction; development data gives no verdict).
- Next: H5 step 2 and H6 read the corrected settlement columns.

### 2026-10-14 [H7] step 1 · eleonorabjornberg/repo-market-model#772
- Directive: #766
- Step: 1, groundwork (liquidity G6 input; ingestion only; the repo-operation snapshots extended to 2026-09-03 for liquidity goalpost 3, eleonorabjornberg/repo-market-liquidity#75)
- Tier: development
- Pins: published panel `4ddc3882…`; base `fefc608`
- Tried: no forecast variant. One fetch of the Desk's repo-operation results for 2026-01-01 to 2026-09-03 with `PYTHONPATH=src python3 -m repo_model.cli fetch repo-ops --start 2026-01-01 --end 2026-09-03`, saved beside the eight yearly snapshots; `coverage_end` of `nyfed_repo_ops` and `nyfed_repo_ops_sameday` moved to 2026-09-03. Variants: 0.
- Result: 510 operations on 169 operation dates, 2026-01-02 to 2026-09-03. Rows before 2026-01-01 read identically with and without the new file (both readings), the eight earlier files and manifests are byte-for-byte unchanged, and a date after 2026-09-03 is still refused. The published panel digest does not move.
- Against kill: not applicable (no verdict; nothing scored on a 2026 day).
- Next: the liquidity repo bumps its parent pin to the merge commit and reads the 2026 labels.

### 2026-10-16 [H5] step 3 · eleonorabjornberg/repo-market-model#829
- Directive: #786
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; base `62009b23`
- Tried: #632's rows (the passer, the two #598 and #601 controls, variants (a) and (b)) and the references (`risk_gbm`, `ngboost_laplace`, `calendar_climatology`, `persistence_logistic`), rebuilt at h = 1 to 5 and tabulated for the reliability slope on the ordinary days inside 2018-19, 2020-24 and 2025-26 and inside each as-of scarcity state, 90% bootstrap intervals (2,000 replications). Variants: 0 new models.
- Result: inside 2018-19 (73 or 74 of 100 or 101 pressure days) (b) reads 0.07 to 0.60 at h = 1 to 5, intervals below 1; `persistence_logistic` reads 0.32 to 0.58, so its pooled 0.89 to 1.08 ("the better calibrated of the two") holds only in 2025-26 (0.82 to 1.07). In 2025-26 (b) reads 0.30 to 0.90 with intervals including 1. The rebuilt rows (a) and (b) differ slightly from the page's first run (AUROC 0.9072 against 0.9029 at h = 1 for (b)); references reproduce.
- Against kill: not applicable (a correction to how step 3 figures are read; development data, not a verdict).
- Next: #785 does the same for #631's page; any reliability-shape test (#628) is read within regimes; the drift of (a) and (b) is not traced to a change in `ml.py`.

### 2026-10-14 [H7] groundwork G6 · eleonorabjornberg/repo-market-liquidity#76
- Directive: eleonorabjornberg/repo-market-liquidity#74
- Step: H7m groundwork G6 (goalpost module and power study)
- Tier: development
- Pins: model 53e61af9b4175e854c196908d3c76b228c039667, panel digest acb77874e0ca2c9eeee1c33a229f5e12745e65bb1224088d52c391dbf54be2ab, snapshot none
- Tried: R plus a planted signal on 9 target gains, replayed over 60-, 125- and 250-day windows; variant count 0 (no candidate)
- Result: MME 0.05 detectable in 10 of 13 250-day windows that reach 10 events (power 15% over all 67 windows; 41% to 2020, 6% 2021-24); events are the constraint (221 in 1,570 days)
- Against kill: not applicable (no candidate scored); docs/decisions/measurement-protocol.md §5 and §9 unchanged
- Next: Eleonora sets the MME and the event floor (Q2); step 2 (candidate C) continues in plan order

### 2026-10-15 [H7] groundwork G1 · eleonorabjornberg/repo-market-liquidity#84
- Directive: eleonorabjornberg/repo-market-liquidity#83 (L18, finding #80)
- Step: groundwork G1 for H7m: align the research-log check with the model repo's format
- Tier: development
- Pins: parent 53e61af9b4175e854c196908d3c76b228c039667; panel digest unchanged; snapshot none
- Tried: copied the model repo's heading and field rules into scripts/check_log_entry.py, test first; converted the six merged entries
- Result: log check aligned, nothing scored
- Against kill: not applicable
- Next: the model repo copies the six converted entries in its next log PR

### 2026-10-15 [H10] step 3 · eleonorabjornberg/repo-market-liquidity#90
- Directive: eleonorabjornberg/repo-market-liquidity#86 (L20, finding #79)
- Step: step 3 sensitivity: ON RRP as two regime-specific terms, regime fixed by the baseline mean, replacing the superseded interaction sensitivity
- Tier: development
- Pins: parent 53e61af9b4175e854c196908d3c76b228c039667; panel version 1, digest unchanged; snapshot none; seed 20261013
- Tried: re-ran the step 2 application with depleted and abundant ON RRP terms, each with its own coefficient; 31 onsets, 10,000 draws, null of 1,000 draws
- Result: sensitivity only: 3 of 31 under the residual bar (4% to 22%), 13 of 31 beat the null (29% to 57%), 3 counted, against 4, 14, 4 published; outcome still residual dominates; the abundant regime has 2 onsets
- Against kill: not applicable; development evidence, no verdict
- Next: Eleonora decides the day-level definition for the selection null and whether the page stands; the placebo-floor amendment (#85) may move these counts

### 2026-10-15 [H7] groundwork G4 · eleonorabjornberg/repo-market-liquidity#91
- Directive: eleonorabjornberg/repo-market-liquidity#89, relabel the saved-page SHA-256 as a fetch hash and add a re-derivable content hash (finding #40).
- Step: groundwork G4 and G5 (H.4.1 and H.8 provenance for the H7m inputs).
- Tier: development
- Pins: parent 53e61af9b4175e854c196908d3c76b228c039667; panel version 1 acb77874e0ca2c9eeee1c33a229f5e12745e65bb1224088d52c391dbf54be2ab; snapshot agency_securities 9a5c4eafb04e85d4676c97bfc94a047ee6a7ad384345f977fff30d3f01681e58.
- Tried: relabelled page_sha256 as fetch_sha256 in the three H.4.1 extracts, the agency-securities snapshot and the H.8 releases record; added content_sha256 per release; variant count 1.
- Result: provenance relabelled, no value changed, nothing scored.
- Against kill: not applicable.
- Next: Eleonora's rulings on Q1 and Q2 above; then H7m G6 resumes.

### 2026-10-16 [H5] step 3 · eleonorabjornberg/repo-market-model#830
- Directive: #785
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; base `dfbbc03`
- Tried: #631's two every-day rows (`+every_day` and `+every_day+lagpress`) rebuilt at h = 1 to 5 and tabulated for the reliability slope on the ordinary days inside 2018-19, 2020-24 and 2025-26 and inside each as-of scarcity state, 90% bootstrap intervals (2,000 replications). Variants: 0 new models.
- Result: inside 2018-19 (62 of 82 pressure days) the parent reads 0.32 to 0.61 at h = 1 to 5 and lagged pressure 0.21 to 0.51, intervals below 1 from h = 2; the pooled 0.85 to 1.00 is not calibration by regime. In 2025-26 the rows read 0.62 to 0.94 with intervals including 1. Two pooled cells differ from Table M2 (parent h = 3: 0.91 against 0.98; lagpress h = 4: 0.71 against 0.73), the fit definition being #725's.
- Against kill: not applicable (a correction to how step 3 figures are read; development data, not a verdict).
- Next: any reliability-shape test (#628) is read within regimes; the two moved cells are not traced to the fit or to `ml.py`.

### 2026-10-16 [H5] step 3 · eleonorabjornberg/repo-market-model#847
- Directive: #843 (finding #840)
- Step: 3
- Tier: development
- Pins: published panel `4ddc3882…`; base `0065b4e3`
- Tried: rebuilt #632's variants (a) and (b) at h = 1 in trees at `011023cb`, `09640f5b`, `e56c4fb3`, `dbbe3d8d` and main, then on main with the older `satiation_distance_598.py`. Variants: 0 new models.
- Result: `ml.py` is not the cause: all five trees give the same rows ((a) AUROC 0.5673, (b) 0.9072, slope 0.497). The cause is the two distance columns, rebuilt per H.4.1 release since #622: with the older columns the page's 0.5629, 0.9029 and slope 0.463 return to the digit. Development data, no verdict.
- Against kill: not applicable.
- Next: whether #632's tracked tables are re-scored and published anew is Eleonora's (marked question in the PR); the other pages on `satiation_dist_roll` may have the same history.

### 2026-10-16 [H5] step 3 · eleonorabjornberg/repo-market-model#852
- Directive: #845
- Step: 3 (calibration in the regime where the confirmation days fall: H5's laws on ordinary target days after reserve-management purchases began)
- Tier: development
- Pins: published panel `4ddc3882…`; base `0065b4e3`; declaration `metadata/exploration_845.json`; seed 845; target days to 2026-09-03 (`EXPLORATORY_END`), no locked day read
- Tried: mean reversion (#686), #761's variant (i), #634's (c) and `gbm_funding` (their 10 walks re-run to 2026-09-03) and `persistence_logistic`, by lead, mean P(spread > +5 bp) against the realised share for 2025-12-12 to 2026-09-03 and 2019-10-15 to 2020-02-28, with the error split into a level part and a residual-pool part. No model changed; variants: 0 new.
- Result: on ordinary target days from 2025-12-12 (6 pressure days of 152 to 155 cells per lead) every law over-forecasts: lead 1 mean P 0.086 mean reversion, 0.070 (i), 0.077 (c), 0.057 gbm_funding, 0.085 persistence-logistic against 0.039 realised; lead 5 0.117, 0.090, 0.123, 0.067, 0.095. In 2019-10-15 to 2020-02-28 (9 pressure days of 80) lead 1 is 0.232, 0.201, 0.159, 0.160, 0.224 against 0.113. The level part is 0.001 to 0.025 of an error of 0.02 to 0.09: the over-forecast sits in the residual pool, not the centre. Detail in `docs/pivot/calibration-reserve-mgmt-845-result.md`.
- Against kill: not applicable (calibration in the large of existing laws; development data, not a verdict).
- Next: a residual pool conditioned on the as-of policy register would be a later declared variant; whether calibration in the large may be reported under the 3-pressure-day minimum is Eleonora's (question in the pull request).
