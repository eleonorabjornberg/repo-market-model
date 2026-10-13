# Research log

One entry per scored experiment, newest last. The plan is [`plan.md`](plan.md); the format is the constant
`ENTRY_FORMAT` in `scripts/check_research_log.py`, which `python3 scripts/check_research_log.py check` enforces in
CI. The same format serves both repositories (`repo-market-liquidity` results arrive as a fenced `research-log`
block copied verbatim from that repository's pull request body).

Heading: `### YYYY-MM-DD [H#] step N · owner/repo#PR` (the date is Eastern time).
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

### 2026-10-13 [H3] step 1 · eleonorabjornberg/repo-market-model#696
- Directive: #680
- Step: 1
- Tier: development
- Pins: published panel `4ddc3882…`; base `09640f5`
- Tried: #630's screen re-run with the decided 13-day carry cap on the dealer financing columns, which #630 carried with no limit; the withheld (`*`) weeks counted per column. Variants: n/a (correction).
- Result: the export withholds 85 of 666 weekly dates of `pd_repo_ust` and 72 of `pd_reverse_repo_ust` (2022 to 2025), 3 of `pd_repo_mbs`, none of the fails series. Partial rank correlation with the +5 bp indicator on ordinary days: `pd_reverse_repo_ust` +0.112 → +0.087 [+0.05, +0.12], `pd_repo_ust` +0.104 → +0.076 [+0.03, +0.12]. Detail in `docs/pivot/new-sources-withheld-weeks.md`.
- Against kill: not applicable (H3's kill is not tested here; the two series lose rank, and neither was a lead beyond #630's own reading).
- Next: Eleonora decides whether the source is admitted given the withheld weeks.

### 2026-10-13 [H9] step 1 · eleonorabjornberg/repo-market-model#702
- Directive: #639
- Step: 1 (the screen of the richer targets; step 2, the model, is not done)
- Tier: development
- Pins: published panel `4ddc3882…`; screen panel `347f5afb…`; base `374fe3d4`
- Tried: 10 targets (SOFR 99th percentile − IORB and SOFR dispersion, TGCR and BGCR each minus IORB and their dispersion, EFFR − IORB, ON RRP level and change, standing repo facility take-up), as-of persistence B1 and calendar climatology B2 at leads 1, 2, 3, 5 and 10, the lead against the +5 bp episodes and the overlap with SOFR − IORB. Variants: 0 (nothing is fitted).
- Result: persistence beats the climatology for EFFR − IORB and the ON RRP level at every lead (skill +0.80 [+0.72, +0.86] and +0.89 [+0.87, +0.91] at lead 1), for TGCR/BGCR − IORB at lead 1 only (+0.22 [+0.04, +0.38]); the climatology beats it for the dispersions from lead 2, the ON RRP change and the facility take-up. The rate-level targets correlate +0.39 with the pressure indicator and read high before onsets (AUC 0.83) but not within the as-of scarcity state (scarce-state pre-onset AUC 0.47 to 0.52); TGCR/BGCR − IORB repeat SOFR − IORB (+0.95).
- Against kill: not testable in this step (no model, development data); no target shows a lead beyond the as-of scarcity state.
- Next: step 2, the model for at most three targets, once the target-choice rule and #634's model are settled.
