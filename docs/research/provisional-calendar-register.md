# Provisional register: results from a model that did not read calendar days at the target day (#1028)

**Development data, not a verdict, and nothing here edits a result.** Eleonora, 20 October 2026: a repo-market model that does not read
calendar days at the target day is wrong, and every result produced before the calendar fix (#1027) by a model without calendar inputs,
or trained on calendar or scheduled columns one day off (the #914 class), is **provisional until re-run**. This page lists those
results, one row each, and orders their re-runs by the research plan. A registered result stays as it was published (`docs/runs/` and
every result page are untouched); the results page marks its figures "provisional: calendar not read at the target day" and links here.
Each row of the three tables is its own file under `metadata/provisional/` (`producers/<script stem>.json`,
`results/pr_<pull request>.json`, `cleared/<declaration stem>.json`), and the tables are generated from those files by
`scripts/provisional_register.py`; the prose is hand-written. A directive that adds a producer or a result adds its own file and runs
`python3 scripts/provisional_register.py` (CI runs it with `--check`); it does not edit the tables by hand. A result file's `order` is a
sort key (the table numbers the rows in its order), so a new result takes a free key and renumbers no other file.
`tests/test_provisional_register.py` fails if the tree outgrows the files.

## The two classes, and how a row was classified

- **Class a: no calendar day-type input.** The model's inputs name none of `quarter_end`, `days_to_month_end`, `tax_date` or a
  settlement or scheduled-IORB column at the target day. `gbm_funding`'s nine inputs are `reserve_balances`, `sofr_p25`, `sofr_p75`,
  `sofr_volume`, `spread_bps`, `tbill_13w`, `tbill_4w`, `tga` and `treasury_settlement`.
- **Class b: a calendar or scheduled column trained one day off.** Rule 2 of `src/repo_model/asof.py` serves such a column from the
  target row. A one-step pair (`training_pairs` unset, the default of the two gradient-boosted quantile fitters in `src/repo_model/ml.py`)
  pairs the spread of row p + 1 with the row p, so the column is learned from the day before the target and served from the target's own day.
- **Class a+b:** both. **Class series:** the result reads the series of such a model as data (a scorer or calibration study); its
  conclusion is about a test, and it is marked because its numbers come from a series that will change.
  **Class aligned (not provisional):** the script's one-step fit runs on a frame whose calendar and scheduled columns were moved
  up one row, so they are read at the target day; it is listed only because it calls a one-step fitter (#1027's aligned variant).

A row is in the class when the script that produced its series calls one of those fitters without `training_pairs="direct"` (the
producers table below is the complete list of scripts that call them, and the tests fail on a new one without its own producer file). A declaration that names a
calendar or scheduled column and is **not** in the class is in the third table, with the reason. The pressure models of `ml.py`
(`pressure_*`) train on direct pairs (`_pressure_pairs`, `_combined_pairs`: each label with the row its own forecast would read), so
they read the target day's columns; the benchmarks and risk-date laws read the target row by definition.
Starting point: the table of `docs/research/drivers-audit-951-result.md` §1, extended to every result merged since and to the results
before it that read the same series.

## The guard (#947), and its exemptions

`src/repo_model/one_step_guard.py` refuses a calendar or scheduled regressor in a one-step fit, so a new fit cannot be class b. It
exempts two frozen declarations whose figures must reproduce: `published_distribution_crps` (the published distribution: the final
test's frozen command and the live record) and `gbm_funding_634` (the control of `metadata/spread_distribution_634.json`). Both are
class a+b at lead 1 and are the first rows of the results table. A third, `pressure_model_v2` (depth-3 trees on the same
inputs, logged in the live record), is exempt only until the live record's first scoring date (Eleonora, 20 October 2026,
on PR #1042); its producer, `scripts/pressure_model_v2.py`, is class a+b below. Two more, `aligned_calendar_1027_h1` and
`aligned_calendar_1027_h2_to_h5`, admit #1027's aligned variant (`scripts/aligned_calendar_1027.py`), whose one-step pairs read the
calendar and scheduled columns from the target row, so it is neither class a nor class b; the script refuses a frame that is not so
aligned, and both entries carry an end date (Eleonora, 21 October 2026, on PR #1036). The guard names the fitters and makes no fit, so it is not a
producer. Rows in the tables below whose fit the guard would now refuse (the one-step calendar arms and variants (a) and (b)) are
the results of a fit that can no longer be repeated unchanged; their figures stand as published and are marked.

## Marked questions for Eleonora

- **Does class a reach the paused +5 bp pressure program?** The old H2 and risk-date models for the +5 bp event (the `pressure_*`
  declarations in the third table) train on direct pairs, so none is class b. Some model ordinary days with no calendar input by design.
  This register does not register them, because the directive starts from #951's table and the +5 bp program is paused; whether they are
  provisional too is hers.
- **Design results.** Class `series` rows (the scorer's calibration and power studies, #873 and after) quote real forecast pairs of
  `gbm_funding` or of the published model. Their conclusions are about the test; whether they must be re-run on the rebuilt candidate
  (#1027), or only checked for a change in the series, is hers. They are listed last in the re-run order.
- **The published model.** The published v1 declaration (`docs/runs/`, the final test's incumbent) is class a+b at lead 1. It is not
  edited. The results page marks the incumbent's figures; whether the incumbent changes is hers (#1027's page).

## 1. Producers: scripts that call a one-step-capable fitter

<!-- generated: register:producers -->
<!-- Generated by scripts/provisional_register.py from metadata/provisional/producers/. Do not edit by hand: add or change a file there and run `python3 scripts/provisional_register.py`. -->
| Script | Declaration | Model | Calendar or scheduled inputs | Pairing | Class |
|---|---|---|---|---|---|
| `scripts/aligned_announcement_1124.py` | `metadata/aligned_announcement_1124.json` | the aligned_calendar_1027 direct variant with the Treasury settlement columns dated from the auction announcement at leads 2 to 5 (the aggregate with its coupon and bill legs; the coupon leg alone). Direct pairs only: no one-step arm is run, and none is admitted by the one-step guard | quarter_end, days_to_month_end, tax_date at every lead; treasury_settlement and its parts at lead 1 as published and at leads 2 to 5 as announced (the #541 announcement dating, measured and not in force); all from the target row | one_step+direct | aligned |
| `scripts/aligned_calendar_1027.py` | `metadata/aligned_calendar_1027.json` | gbm_funding with calendar and scheduled columns read at the target day: one-step pairs on the aligned frame (i), direct pairs (ii) | quarter_end, days_to_month_end, tax_date at every lead; treasury_settlement and its parts at lead 1; all from the target row | one_step+direct | aligned |
| `scripts/aligned_pairs_931.py` | `metadata/aligned_pairs_931.json` | the control and the arm with treasury_settlement from the target row | treasury_settlement at lead 1 (control); the arm reads it at the target day and has no day-type input | one_step+direct | a+b |
| `scripts/backfill_h5_726.py` | `metadata/backfill_h5_726.json` | `gbm_funding` with and without the back-filled rows | treasury_settlement at lead 1 | one_step | a+b |
| `scripts/calibration_masking_effect.py` | none | the published declaration, calibration masking on and off | treasury_settlement at lead 1 | one_step | a+b |
| `scripts/calibration_rediagnosis.py` | none | the published declaration, CV+ against conformal PID and Mondrian CV+ | treasury_settlement at lead 1 | one_step | a+b |
| `scripts/direct_twin_449.py` | `metadata/direct_twin_449.json` | `gbm_funding` and its twin on direct pairs | treasury_settlement at lead 1 (control) | one_step+direct | a+b |
| `scripts/dom_level_term_1032.py` | `metadata/dom_level_term_1032.json` | gbm_funding_cal_direct of #1027 plus a day-of-month bucket of the target day, on direct pairs only (the producers table's pairing values have no direct-only entry) | dom_bucket at every lead, plus #1027's: quarter_end, days_to_month_end, tax_date at every lead; treasury_settlement and its parts at lead 1; all from the target row | one_step+direct | aligned |
| `scripts/drivers_audit_951.py` | `metadata/drivers_audit_951.json`, `metadata/drivers_audit_951_fits.json` | the nested ceiling lineup and five arms; `onestep_cal_leaf20` trains the calendar inputs one-step | quarter_end, tax_date, days_to_month_end (the one-step calendar arm); treasury_settlement at lead 1 | one_step+direct | a+b |
| `scripts/final_test_preregistration.py` | none | the six candidates of the final-test pre-registration (the gbm on the published features) | treasury_settlement at lead 1 | one_step | a+b |
| `scripts/fomc_variants_1087.py` | `metadata/fomc_variants_1087.json` | the two aligned_calendar_1027 variants with the FOMC meeting columns added: one-step pairs on the aligned frame (the aligned arm, not run unless the allow-list admits it), direct pairs (the direct arm) | fomc_meeting_day and fomc_days_to_next_meeting at every lead, with quarter_end, days_to_month_end, tax_date at every lead and the settlement columns at lead 1; all from the target row | one_step+direct | aligned |
| `scripts/h3_nested_708.py` | `metadata/h3_nested_708.json` | the nested families added to `gbm_funding` | treasury_settlement at lead 1 | one_step | a+b |
| `scripts/h9_nested_842.py` | `metadata/h9_nested_842.json` | `gbm_funding` with a richer target's forecast as an input | treasury_settlement at lead 1 | one_step | a+b |
| `scripts/onrrp_distance_948.py` | `metadata/onrrp_distance_948.json` | `gbm_funding` on SOFR minus the ON RRP rate; the control is one-step | treasury_settlement aligned at lead 1 in the arm, one-step in the control; no day-type input | one_step+direct | a+b |
| `scripts/pid_constant_selection.py` | none | the published declaration, nested selection of the PID constants | treasury_settlement at lead 1 | one_step | a+b |
| `scripts/pressure_model_v2.py` | none | pressure model v2: trees of depth 3 on v1's features, with calendar columns in some arms | quarter_end, tax_date, days_to_month_end in the calendar arms; treasury_settlement at lead 1 | one_step | a+b |
| `scripts/richer_targets_706.py` | `metadata/richer_targets_706.json` | candidate (b) of #634 fitted on each richer target | tax_date, treasury_settlement and the announced-IORB columns of `new_features(h)` | one_step | a+b |
| `scripts/spread_distribution_634.py` | `metadata/spread_distribution_634.json` | `gbm_funding` (control); (a) the published declaration and (b) gbm with the new inputs; (c) the two-part form is direct (cleared) | treasury_settlement at lead 1 in the control; tax_date, treasury_settlement and the announced-IORB columns in (a) and (b) | one_step | a+b |
| `scripts/twin_diagnosis_865.py` | `metadata/twin_diagnosis_865.json` | the control and five remedy arms | treasury_settlement at lead 1 (control) | one_step+direct | a+b |
| `src/repo_model/cli_eval.py` | none | `--model gbm`: the phase 2 gbm and the published v1 funding declaration | treasury_settlement at lead 1 | one_step | a+b |
<!-- end generated: register:producers -->

## 2. Registered results, in the order of their re-run

Order: H5 first (the primary goal), then H9, then the other hypotheses; design results (class `series`) last. Every re-run waits for
#1027, which rebuilds the candidate on aligned pairs. "On the page" names the research-log entry files whose figures carry the mark (and
`incumbent` for the figures at the top of the results page).

<!-- generated: register:results -->
<!-- Generated by scripts/provisional_register.py from metadata/provisional/results/. Do not edit by hand: add or change a file there and run `python3 scripts/provisional_register.py`. -->
| Order | Directive | Pull request | Hypothesis | Result | Declaration | Model | Pairing | Class | On the page | What it concluded |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | #73 | #73 | H5 | Phase 2 and the v1 funding declaration against as-of persistence (`docs/runs/`) | none | the phase 2 gbm, uncalibrated and cross-conformal, and the published v1 declaration | one_step | a+b | 0001-2026-10-05-model-00073-H5-step3, incumbent | Beats as-of persistence on CRPS by its interval, not uniformly: every gbm loses in 2021-23 and the uncalibrated gbm on quarter ends; the tail clause fails. |
| 2 | #634 | #711 | H5 | The spread distribution re-scored under protocol v1 | `metadata/spread_distribution_634.json` | `gbm_funding`, (a), (b) and the published declaration | one_step | a+b | 0026-2026-10-13-model-00711-H5-step1 | The new inputs add nothing on the primary score; no variant beats B3 on its five levels; only the two-part form (c, direct, not provisional) leads on the upper tail. |
| 3 | #758 | #775 | H5 | The best candidate against H2's ceiling | `metadata/h5_step4_758.json` | `gbm_funding`; H2's reachable and ceiling fits are aligned and not provisional | one_step | b | 0056-2026-10-14-model-00775-H5-step4 | `gbm_funding` +0.257 against B1 on ordinary targets, above the ceiling's +0.168 (headroom negative). |
| 4 | #707 | #756 | H5 | Diagnoses of 2021-23 and of the upper tail | `metadata/h5_step3_707.json` | the phase 2 gbm and (c); (c) is aligned | one_step | a+b | 0043-2026-10-14-model-00756-H5-step3, 0044-2026-10-14-model-00756-H5-step3 | The gbm does not resolvably lose to B1 in 2021-23 and is under-dispersed above 0 bp. |
| 5 | #805 | #820 | H5 | Scores by anchor type and without 2019-09-18 | none | the phase 2 gbm and (c) | one_step | a+b | 0078-2026-10-15-model-00820-H5-step3 | The gain concentrates on days after a calendar spike. |
| 6 | #844 | #853 | H5 | Ordinary-day P(spread above 5 bp) from four models | `metadata/exploration_844.json` | mean reversion, (i), (c) and `gbm_funding` | one_step | b | 2026-10-17-model-00853-H5-step3 | Mean reversion, (i) and `gbm_funding` rank ordinary days above persistence-logistic in AUROC at lead 1. |
| 7 | #845 | #852 | H5 | Calibration after reserve-management purchases | `metadata/exploration_845.json` | mean reversion, (i), (c), `gbm_funding` and persistence-logistic | one_step | b | 0096-2026-10-16-model-00852-H5-step3 | Every law over-forecasts the +5 bp share; the over-forecast sits in the residual pool. |
| 8 | #882 | #898 | H5 | Results of steps 2 to 4 without 2019-09-18 | none | the candidates of #761, #688 and #758 | one_step | b | 2026-10-17-model-00898-H5-step3 | Without the day the candidates' ordinary skill falls by about 9 points and stays above zero. |
| 9 | #883 | #907 | H5 | Month-end readings of the ordinary-day headlines | none | the controls of #805, #761, #849, #694 and #775 | one_step | b | 2026-10-17-model-00907-H5-G2 | Pooled skills move by about 0.1 points at most; kill outcomes do not change. |
| 10 | #934 | #945 | H5 | Per-regime AUROC difference of four models | none | `gbm_funding` among four models, read from the committed score | one_step | b | 2026-10-19-model-00945-H5-step3 | By regime and lead `gbm_funding` has one cell above zero and one below of 15; no pooled gain is claimed. |
| 11 | #449 | #825 | H5 | `gbm_funding` against its direct-pairs twin | `metadata/direct_twin_449.json` | `gbm_funding` (control) and the twin | one_step | a+b | 2026-10-15-model-00825-H5-step1 | The twin is behind the control pooled and in 2021-23. |
| 12 | #865 | #885 | H5 | Diagnosis of the twin's shortfall | `metadata/twin_diagnosis_865.json` | the control and five remedy arms | one_step | a+b | 2026-10-17-model-00885-H5-step2 | No defect: the pairs are aligned and the shortfall falls as the training pairs get fresher. |
| 13 | #931 | #957 | H5 | Aligned settlement pairs at lead 1 | `metadata/aligned_pairs_931.json` | `gbm_funding` (control) and the aligned arm | one_step | a+b | 2026-10-19-model-00957-H5-step3 | The aligned arm beats `gbm_funding` by +2.8% pooled and +13.8% on month-end targets. |
| 14 | #951 | #978 | H5 | Drivers audit and re-run | `metadata/drivers_audit_951.json`, `metadata/drivers_audit_951_fits.json` | the ceiling lineup and five arms; the one-step calendar arm is class b | one_step | a+b | 2026-10-19-model-00978-H5-step4 | The calendar inputs carry signal on aligned pairs; the direct pairing costs skill on ordinary days and in 2021-23. |
| 15 | #948 | #991 | H5 | `gbm_funding` fit on SOFR minus the ON RRP rate | `metadata/onrrp_distance_948.json` | `gbm_funding` (control, one-step) and the arm (no day-type input) | one_step | a+b | 2026-10-20-model-00991-H5-step3 | Fit on the distance, the arm is measured against `gbm_funding` at every lead. |
| 16 | #992 | #997 | H5 | The `gbm_funding` arms of #960 | `metadata/b1_calendar_960.json` | `gbm_funding` and B1' | one_step | b | 2026-10-20-model-00997-H5-step5 | The `gbm_funding` arms are quoted beside B1' from #960's evidence. |
| 17 | #970 | #984 | H5 | Randomised PIT beside the midpoint PIT | `metadata/randomised_pit_970.json` | `gbm_funding` and (c) | one_step | b | 2026-10-19-model-00984-H5-step3 | The randomised PIT reproduces the midpoint bins' reading in 2021-23. |
| 18 | #969 | #982 | H5 | Live-monitoring thresholds replayed on the published model | `metadata/live_monitoring_969.json` | the published model's daily forecasts at lead 1 | one_step | a+b | 2026-10-19-model-00982-H5-G3 | The proposed thresholds do not discriminate: a flag is set on most days. |
| 19 | #841 | #846 | H5 | The model-risk validation report (`docs/model/validation.md`) | none | `gbm_funding`; the report is a document and is not edited in place | one_step | a+b | 2026-10-16-model-00846-H5-step6 | The report cites development results of `gbm_funding` by issue and page; it is re-issued after the re-run. |
| 20 | #1030 | #1085 | H5 | The per-episode stress replay of the published model | none | the published distribution as a series (`docs/runs/published_distribution_daily_h1.json`), beside B1, B2 and B1′ | one_step | series | 2026-10-21-model-01030-H5-step6 | The published q95 sat below the print on most replayed days and the band widened after the first miss; development data, a replay of a calendar-blind series. |
| 21 | #1072 | #1091 | H5 | The randomised PIT for whole-bp outcomes, `gbm_funding` rows only | none | `gbm_funding` as a series (the lead-1 walk); the rows of #1027's two variants are not provisional | one_step | series | 2026-10-21-model-01091-H5-step3 | The 2021-23 share of PIT at or below 0.10 moves from 0.314 to 0.211 for `gbm_funding`; the 2021-23 reading stands at a smaller size. |
| 22 | #706 | #774 | H9 | The richer targets modelled with #634's candidate (b) | `metadata/richer_targets_706.json` | candidate (b) of #634 fitted on each target | one_step | a+b | 0082-2026-10-14-model-00774-H9-step2 | Skill over B1 for all three targets; no lead on the +5 bp episodes in the scarce state. |
| 23 | #842 | #856 | H9 | The nested test of the richer targets against `gbm_funding` | `metadata/h9_nested_842.json` | `gbm_funding` with a target's forecast as an input | one_step | a+b | 2026-10-17-model-00856-H9-step3 | No target improves the candidate beyond its interval; the input is trained against the wrong day at the longer leads, which biases the test toward no gain. |
| 24 | #708 | #763 | H3 | The nested test of four source families against `gbm_funding` | `metadata/h3_nested_708.json` | `gbm_funding` with each family added | one_step | a+b | 2026-10-17-model-00763-H3-step3 | No family improves the candidate beyond its interval; two make it worse. |
| 25 | #968 | #988 | H3 | The OFR cleared-repo series at the lag the OFR states | none | `gbm` on the published funding features plus `ofr_dvp_minus_bgcr_bp`, against the same without it (#187's paired test) | one_step | b | 2026-10-19-model-00988-H3-step1 | No change: the paired test is no effect at both lags; `treasury_settlement` is trained one row off at lead 1 in both arms. |
| 26 | #1016 | #1035 | H3 | The OFR cleared-repo lag counted on government-open days | none | `gbm` on the published funding features plus `ofr_dvp_minus_bgcr_bp@1d`, against the same without it (#187's paired test, `docs/research/ofr-cleared-holidays-1016/gbm.json`) | one_step | b | 2026-10-20-model-01035-H3-step1 | The lookahead on three market days is closed; the paired test is no effect; `treasury_settlement` is trained one row off at lead 1 in both arms. |
| 27 | #726 | #726 | H4 | The back-fill against H5's candidate | `metadata/backfill_h5_726.json` | `gbm_funding` with and without the back-filled rows | one_step | a+b | 0046-2026-10-14-model-00726-H4-step3 | The back-fill makes 2018-19 grid CRPS worse and moves the other regimes within their intervals. |
| 28 | #655 | #737 | H1 | Critical values calibrated on the real difference series, B3 minus B1 included | none | the published model (B3) as a series | one_step | series | 0041-2026-10-13-model-00737-H1-step1 | The verdict reads the grid comparison's calibrated values; power for a 3% skill stays low. |
| 29 | #754 | #792 | H1 | Power tested by replay on real forecast pairs | none | B3 against B1 as a series | one_step | series | 0061-2026-10-15-model-00792-H1-step3 | Only B3 against B1 is a known-better pair; the current test's size on a symmetric null is far above 5%. |
| 30 | #873 | #878 | H1 | Critical and futility values recalibrated in the candidate orientation | none | the published model (B3) and `gbm_funding` as series | one_step | series | 2026-10-17-model-00878-H1-step4 | Draft values and the power at them, as a draft amendment. |
| 31 | #886 | #911 | H1 | Values recalibrated on post-2020 stationary-bootstrap windows | none | the published model (B3) as a series | one_step | series | 2026-10-17-model-00911-H1-step5 | Size by 250 days is 5.0% at the new values; power for a 3% skill falls to 6.1%. |
| 32 | #922 | #923 | H1 | Size of the B2 leg of "Supported" for B1 and `gbm_funding` | none | `gbm_funding` as a series | one_step | series | 2026-10-19-model-00923-H1-step4 | The share of windows whose B2-leg bound is above zero with no skill is reported. |
| 33 | #949 | #980 | H1 | The block-length report | none | `gbm_funding` as a series | one_step | series | 2026-10-19-model-00980-H1-step3 | The block stays 10: against B1 the automatic block is 4.8 days and against B2 it is 73.2. |
| 34 | #963 | #985 | H1 | Contiguous-window calibration and event strata | `metadata/contiguous_calibration_963.json` | `gbm_funding` and `spread_mr_ctx` as series | one_step | series | 2026-10-19-model-00985-H1-step3, 2026-10-19-model-00985-H6-step1 | Contiguous critical values for the candidates; both beat B2 on three strata and neither is clear of B1. |
| 35 | #967 | #999 | H1 | The scaled-score study | `metadata/scaled_score_967.json` | `gbm_funding` as a series | one_step | series | 2026-10-20-model-00999-H1-step2 | The scale buys nothing under the orientation used then. |
| 36 | #1013 | #1025 | H1 | The scaled-score study on the series its paths use | none | `gbm_funding` as a series | one_step | series | 2026-10-20-model-01025-H1-step2 | The corrected calibration is set beside #999's. |
| 37 | #1015 | #1024 | H1 | The B2 leg of "Supported" under #963's rules | `metadata/b2_leg_contiguous_1015.json` | `gbm_funding` and `spread_mr_ctx` as series | one_step | series | 2026-10-20-model-01024-H1-step3 | At 250 days the B1 leg survives and the B2 leg is between 3.0 and 4.0 for both. |
| 38 | #1022 | #1108 | H1 | The block length after April 2020, without 2019-09-18 | none | `gbm_funding` as a series | one_step | series | 2026-10-22-model-01022-H1-step3 | The block stays 10: post-2020-04 the automatic block is 10.2 against B1 and 64.9 against B2. |
<!-- end generated: register:results -->

## 3. Declarations that name a calendar or scheduled column and are not in the class

Each is read at the target day (`as_of_read`: the benchmark, law or ranker reads the target row's own calendar columns), trained on
direct pairs (`direct`: an `ml.pressure_*` model, or an estimator built on `InformationRule.observation`), or is no model (`none`:
data, dating, holidays and panel declarations). None of their scripts calls a one-step-capable fitter (the test checks this).

<!-- generated: register:cleared -->
<!-- Generated by scripts/provisional_register.py from metadata/provisional/cleared/. Do not edit by hand: add or change a file there and run `python3 scripts/provisional_register.py`. -->
| Declaration | Script | Pairing | Why |
|---|---|---|---|
| `metadata/all_inputs.json` | `scripts/all_inputs.py` | direct | `ml.pressure_all_inputs_exceedance`, direct pairs |
| `metadata/announcement_dating.json` | `scripts/announcement_dating_rescore.py` | direct | a re-score of pressure models under announcement-dated settlements |
| `metadata/backfill_spread_633.json` | `scripts/backfill_spread_633.py` | direct | its own quantile estimator on pairs read through `InformationRule.observation` at each target's decision instant |
| `metadata/balance_sheet_nested_1031.json` | `scripts/balance_sheet_nested_1031.py` | direct | both arms fit #1027's gbm_funding_cal_direct on direct pairs (`training_pairs="direct"`) and read the calendar columns, treasury_settlement at lead 1 and their three balance-sheet flag columns from the target row |
| `metadata/calendar_mr_1115.json` | `scripts/calendar_mr_1115.py` | direct | scaled mean reversion with additive calendar, scheduled and FOMC terms read from the target row on direct pairs (repo_model.spread_mr_calendar, guarded by one_step_guard with no allow-list entry); no gradient-boosted fit is called |
| `metadata/combined_model_561.json` | `scripts/combined_model_561.py` | direct | `_combined_pairs`, direct pairs |
| `metadata/derived_features_631.json` | `scripts/derived_features_631.py` | direct | pressure models on direct pairs |
| `metadata/effr_pretrain.json` | `scripts/effr_pretrain.py` | direct | pressure models on direct pairs |
| `metadata/evaluation_splits.json` | none | none | the regime and day-type splits: a declaration, no model |
| `metadata/every_day_steps_687.json` | `scripts/every_day_steps_687.py` | direct | the every-day part, direct pairs |
| `metadata/fhs_scale_941.json` | `scripts/fhs_scale_941.py` | none | mean reversion with volatility-scaled residuals: no gradient-boosted fit and no calendar column trained or read as an input (the day types only split the report); a development study whose figures are provisional under the calendar-first rule as #686's are, and the classification is Eleonora's (the pull request asks) |
| `metadata/funding_panel_manifest.json` | none | none | the panel manifest: data |
| `metadata/h6_design_1131.json` | `scripts/h6_design_1131.py` | none | a design and power page: it fits no gradient-boosted model and trains no calendar column. It reads the strata from the calendar at the target day and scores the existing `spread_mr_ctx` (#761, cleared above) as a stand-in series for the shape of a candidate's d; the registered H6 candidate is not chosen here, and a candidate registered later reads the calendar columns on direct pairs |
| `metadata/iorb_every_day_579.json` | `scripts/iorb_every_day_579.py` | direct | pressure models on direct pairs |
| `metadata/market_holidays.json` | none | none | the holiday table: data |
| `metadata/model_defects_540.json` | `scripts/model_defects_540.py` | direct | pressure models on direct pairs |
| `metadata/near_threshold_688.json` | `scripts/near_threshold_688.py` | direct | pressure models on direct pairs |
| `metadata/net_settlement.json` | `scripts/net_settlement.py` | direct | the net settlement columns, read in pressure models on direct pairs |
| `metadata/nowcast.json` | `scripts/nowcast.py` | direct | pressure models on direct pairs |
| `metadata/ofr_followup.json` | none | none | a 'not yet published' flag for OFR values: data dating |
| `metadata/onset_classifier.json` | `scripts/onset_classifier.py` | direct | pressure models on direct pairs |
| `metadata/onset_diagnostics.json` | `scripts/onset_diagnostics.py` | direct | pressure models on direct pairs |
| `metadata/pooled_gate_595.json` | `scripts/pooled_gate_595.py` | direct | pressure models on direct pairs |
| `metadata/pressure_audit.json` | `scripts/pressure_audit.py` | direct | pressure models on direct pairs |
| `metadata/pressure_hazard.json` | `scripts/pressure_hazard.py` | direct | pressure models on direct pairs |
| `metadata/pressure_tail.json` | `scripts/pressure_tail.py` | direct | pressure models on direct pairs |
| `metadata/pressure_track_q.json` | `scripts/pressure_track_q.py` | direct | pressure models on direct pairs |
| `metadata/projected_reserves.json` | `scripts/projected_reserves.py` | direct | pressure models on direct pairs |
| `metadata/ranking_694.json` | `scripts/ranking_694.py` | as_of_read | the calendar ranker reads the target's day type |
| `metadata/ranking_765.json` | `scripts/ranking_765.py` | as_of_read | the calendar ranker reads the target's day type |
| `metadata/rare_event_training.json` | `scripts/rare_event_training.py` | direct | pressure models on direct pairs |
| `metadata/recency_adaptive_training.json` | `scripts/recency_adaptive_training.py` | direct | pressure models on direct pairs |
| `metadata/risk_date_severity.json` | `scripts/risk_date_severity.py` | direct | pressure models on direct pairs |
| `metadata/risk_date_spread_693.json` | `scripts/risk_date_spread_693.py` | as_of_read | the risk-date laws read the target row's calendar columns (#951 §1: no) |
| `metadata/settlement_announcement_dating.json` | none | none | when each settlement is public: dating |
| `metadata/settlement_result_dating.json` | `scripts/settlement_result_dating.py` | direct | a re-score of pressure models under result-dated settlements |
| `metadata/setup_diagnostic.json` | `scripts/setup_diagnostic.py` | direct | pressure models on direct pairs |
| `metadata/source_matrix_629.json` | `scripts/source_matrix_629.py` | direct | the source screen: pressure models on direct pairs |
| `metadata/sources.json` | none | none | the availability registry: data |
| `metadata/sources_measurement.json` | none | none | the measurement sources registry, which declares the `fomc_calendar` columns: data. A fit on them is refused on one-step pairs by `repo_model.one_step_guard` (#1070) |
| `metadata/spread_distribution_761.json` | none | as_of_read | mean reversion with residuals pooled by the target day's context |
| `metadata/state_calendar_1145.json` | `scripts/state_calendar_1145.py` | direct | scaled mean reversion with calendar and scheduled terms read from the target row on direct pairs, in standardised units, alone or interacted with the as-of scarcity state of the decision (repo_model.spread_mr_state_calendar, guarded by one_step_guard with no allow-list entry); no gradient-boosted fit is called |
| `metadata/structural_liquidity.json` | `scripts/structural_liquidity.py` | direct | the structural model, pressure models on direct pairs |
| `metadata/tax_date_market_days.json` | `scripts/tax_date_market_days.py` | direct | the tax-date window on market days, in pressure models on direct pairs |
| `metadata/tax_date_october_965.json` | `scripts/tax_date_october_965.py` | as_of_read | B2 and the calendar ranker with an alternative label read at the target day |
| `metadata/turn_day_labels_959.json` | `scripts/turn_day_labels_959.py` | as_of_read | B2's pools and the mean-reversion level by the target day's label |
| `metadata/turning_point_variant.json` | `scripts/turning_point_variant.py` | direct | pressure models on direct pairs (`training_pairs="direct"`) |
| `metadata/unused_inputs.json` | `scripts/unused_inputs.py` | direct | the unused-input screen: pressure models on direct pairs |
| `metadata/unwarned_onsets.json` | `scripts/unwarned_onsets.py` | direct | the onset diagnostic: pressure models on direct pairs |
| `metadata/upper_bound_635.json` | `scripts/upper_bound_635.py` | direct | H2's cross-fitted ceiling and reachable fits on aligned reads (#951 §1: no) |
| `metadata/walk_calibration_1133.json` | `scripts/walk_calibration_1133.py` | none | a walk-forward recalibration of #941's mean-reversion law: no gradient-boosted fit, and no calendar column trained or read as an input; the base reads no calendar column, so every figure is provisional under the calendar-first rule as #941's are, and the classification is Eleonora's (the pull request asks) |
| `metadata/window_onset.json` | `scripts/window_onset.py` | direct | pressure models on direct pairs |
<!-- end generated: register:cleared -->

## What this page does not do

- It changes no result, record, declaration or published figure. `docs/runs/` is untouched.
- It does not decide that a result is wrong: it says the model did not read the calendar at the target day, so the figure is provisional
  until the re-run in #1027 and its successors. Whether a re-run replaces anything is Eleonora's.
- It was built from declarations and scripts, not by re-running anything: the pairing of each fit is read from the script that makes it
  (`training_pairs` unset or `"direct"`), and the pressure models' direct pairing from `src/repo_model/ml.py`. A row whose pairing a
  re-run shows otherwise is corrected by a later pull request, as a new row.
