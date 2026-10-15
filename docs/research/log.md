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

### 2026-10-13 [H1] step 1 · eleonorabjornberg/repo-market-model#737
- Directive: #655 (follow-up: Eleonora's answers to Q-E, Q-B and Q-C on PR #695, comment 6159852603)
- Step: 1
- Tier: development
- Pins: published panel `4ddc3882…`; base `e9ce416`
- Tried: each comparison read at its own calibrated critical value instead of the largest across pairs; look 1 futility only; futility one-sided at 0.05 at every look, non-binding, at a calibrated upper bound of skill.
- Result: the verdict reads the grid comparison's values, 2.43 at 250 days and 3.42 at 125 (B3 − B1 on five levels: 5.45 and 9.50); null false detections on the full development history 0.85% and 0.25% by 250 and 125 days (B3 − B1: 0.0%). Futility values 1.93, 1.56 and 1.45 at 60, 125 and 250 days. Power at these values stays low (14% for a 3% skill by 250 days), and the confirmation design goes to a separate study.
- Against kill: the second check passes at the grid comparison's value; no registration until the confirmation-design study is decided.
- Next: the confirmation-design study (horizon, statistic, MME).

### 2026-10-14 [H1] step 2 · eleonorabjornberg/repo-market-model#751
- Directive: #733 (a design study for the confirmation test; no verdict, nothing registered)
- Step: 2
- Tier: development
- Pins: published panel `4ddc3882…`; base `6114a8e`; rule `docs/research/confirmation-design-733.md`, committed before the study ran
- Tried: six declared designs (the in-force test at 250 days; 375 and 500 days; lead 1 alone; a standardized statistic at 250 and 375 days), each calibrated afresh on decision days to 2025-12-31 (no later day read) and simulated for size and for power at 3% and 10% skill (2,000 paths per scenario). A post-hoc addendum re-reads them at the critical value calibrated on the one comparison S(B2) − S(B1) (PR #695, Q-E (b)). Variants: 6 designs, 2 readings.
- Result: at the critical value in force (the largest across four comparisons) no design has power: D0 to D2 under 1% at 3% and at 10% even on the post-2020 history, D3 2.6% and 3.9% there; the standardized D4 reaches 14.4% and 19.4% on the post-2020 history but fails size (8% to 13%). At reading (b) D0 reproduces PR #695's Q-E table on the post-2020 history (14.3% and 19.7% against 14.0% and 19.25%) with size 11.5%; every design fails size on that history. No design reaches 80% power at 3% or at 30% skill. The §7 rule's pick (D3) is the least bad of the admissible, not a useful design.
- Against kill: not applicable (H1 is a validity check, not a gain claim); the page's reading is that the confirmation design cannot confirm the 3% MME in 500 days as the test stands.
- Next: Eleonora decides the reading of the critical value (Q-E) and whether to change the MME or the days; a change is a draft decision record under §13.

### 2026-10-14 [H7] step 1 · eleonorabjornberg/repo-market-model#749
- Directive: #747
- Step: 1 (model-repo side: the tie fix in `satiation.fit_level`, gating liquidity H7 step 2)
- Tier: development
- Pins: published panel `4ddc3882…`; scratch panels as in `scripts/satiation_587.py`; base `e9ce416d`
- Tried: no forecast variant. The tie rule of the fitted kink (relative tolerance 1e-9, "not identified" when the tied set spans more than one grid step) and a count of the walk-forward refits of the fitted-level rows of #587 and #626 (four rows, horizons 1 to 5) under old and new rule. Variants: 0.
- Result: no refit in any row, year or horizon is "not identified" and no level moves, so no earlier figure moves; the old rule reproduces the recorded levels for the structural and combined rows exactly (the projected row differs in 47 refits for a later feature change, not the tie). At a tolerance of 1e-4, 44 refits of each structural and combined row would be tied; none at 1e-6. Detail in `docs/pivot/satiation-ties-747-result.md`.
- Against kill: not applicable (no verdict; development data).
- Next: the liquidity repo bumps its parent pin to the merge commit and proceeds to H7 step 2 (eleonorabjornberg/repo-market-liquidity#41).

### 2026-10-14 [H9] step 2 · eleonorabjornberg/repo-market-model#774
- Directive: #706
- Step: 2
- Tier: development
- Pins: scratch panel `26c51093…`; base `c0c45259`; declaration `metadata/richer_targets_706.json`; stacked on #711 (#634)
- Tried: the three targets chosen by Eleonora's rule of 13 October on step 1's tables (BGCR 99th − 1st percentile, ON RRP daily change, SOFR 99th − 1st percentile) modelled with #634's candidate (b) (gradient-boosted 23-level quantiles, same inputs, the target's own lag), leads 1 to 5, scored by the protocol's grid CRPS against each target's own B1 and B2. Variants: 1 model, 3 targets.
- Result: skill over B1 +0.329 [lower +0.271], +0.310 [+0.286], +0.330 [+0.241]; over B2 +0.156 [+0.080], −0.103 [−0.142], +0.155 [+0.054]; the spread (#634 b) +0.201 over B1 and +0.268 over B2. Negative on quarter-end target days for all three. No lead on the +5 bp episodes in the scarce state (pre-onset AUC of the modelled median 0.38, 0.53, 0.39, intervals not above one half). Detail in `docs/pivot/richer-targets-706-result.md`.
- Against kill: no chosen target shows both skill over persistence and a lead on the +5 bp episodes, so the criterion as worded in the queue is met on development data; not a verdict, and the wording ("or" in the queue, "and" in `H9.md`) is Eleonora's call.
- Next: the nested test with H5's best candidate (H9 step 3), after #634 merges.

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
