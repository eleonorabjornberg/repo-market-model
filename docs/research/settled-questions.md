# Settled questions

**What this is.** One entry per question a study has already answered, so that a new directive starts from what is known and does not re-run it. Terms such as candidate, arm, kill rule, grid CRPS and B1 are defined in the [glossary](glossary.md).

**How to read it.** Every figure below is copied from the cited result page or log entry, development data on days already seen, never a verdict. An entry does not say a question can never be reopened; its last field says what would. A result from a model that did not read the calendar at the target day is provisional (`docs/research/provisional-calendar-register.md`), and the entry says so where it applies. Inside an entry a study is named in words; its issue number and its page are in the entry's Studies line.

**The four statuses** (Eleonora, 9 November 2026: "Those statuses carry different implications, and collapsing them is what made my original recommendations too broad"). A classified entry carries exactly one.

- **failed**: tried and lost, or killed, with the evidence.
- **parked**: she deferred it, with the condition that reopens it.
- **excluded**: she ruled it out, with the ruling.
- **untested**: never run.

A study that ran but read undecided, or covered only part of its question, fits none of the four cleanly. Those entries are in the last section, with no status, and the pull request that added them raised each as a question for her. This page does not settle them.

**Adding an entry.** Cite a page, not memory. Give the question in one sentence, the studies (issue and result page), the answer, and what would reopen it. If a page leaves the question open, say "open" and name what is missing. `tests/test_settled_questions_register.py` checks the statuses, the fields and that each entry cites an issue.

**Record.** Process, no hypothesis; the science is unchanged. Started by #1529 on Eleonora's ruling of 9 November 2026 (docket answer "both" on process-settled-1109); the `.claude/` rule that points directives here is a separate issue.

## Classified

### S1. A faster, dispersion-scaled or spell-switching scale removes the runs in the candidate's band misses

- **Status:** failed
- **Question:** Does a scale that reacts faster to recent errors, is read from SOFR's own dispersion, or switches between calm and stress spells remove the runs in the misses of the H5 candidate's 90% band?
- **Studies:** #1153 (`docs/research/faster-scale-1153-result.md`), #1175 (`docs/research/sofr-dispersion-1175-result.md`), #1182 (`docs/research/regime-spells-1182-result.md`). The observation that started the line is Lens D of the five-lens review of 19 October 2026 (`docs/reviews/2026-10-19-five-lens/lens-D-model-validator.md`): the published model's misses cluster and every record fails independence.
- **Answer:** No. Christoffersen independence of the 90% band's misses stays at p = 0.000 at every lead, under every hit rule, for the base and for every arm of all three studies. Mean run of misses (closed rule, five leads pooled), against 1.11 if misses at 10% were independent: the faster-scale study, base 2.205, best arms 1.96 to 2.00; the SOFR-dispersion study, base 2.083, arms 1.968 to 2.039; the regime-spells study, base 2.126, episode-state arms 1.891 and 1.903 (10.5% and 11.1% shorter), Markov-switching arms longer (2.283 and 2.233). The regime-spells study's kill rule is met (no arm leaves p = 0.000 at any lead and none cuts the mean run by more than 15%). Two caveats on the page: the faster-scale study's arms v1 to v3 read no calendar column, so they are provisional, and the regime-spells study's Markov arms have bands too narrow (miss rate above 0.15), so they are weaker evidence than the episode-state arms. The regime-spells study's page recommends reporting the clustering as a known limit and says adopting that is her decision.
- **Would reopen it:** A mechanism none of the three tried. The faster-scale study's page names a state variable for stress spells and a persistent scale shock; the regime-spells study has since tried a spell state. Or a result from the queued study of the test under the delay (#1528, open) showing that the independence reading itself misstates the clustering under the publication delay (see the entry on the lead-1 hit dependence below).

### S2. A residual scale for every pressure-day type at once, unshrunk

- **Status:** failed
- **Question:** Does multiplying the candidate's residual spread by a separate factor for each pressure-day type (turn, quarter-end turn, tax date, year end, ordinary) improve it?
- **Studies:** #1402 (`docs/research/day-type-scale-1402-result.md`), on the frozen candidate (s3c-ann-net), development window, 1855 decision days.
- **Answer:** No, pooled. The typed arm's pooled grid CRPS against the candidate is -1.1% [-2.3%, -0.1%], a loss on the mean-d bound. It gains on quarter_end_turn (+6.2% [+0.9%, +17.8%]; the 90% band's coverage there 0.586 to 0.718) and loses on turn (-3.5% [-10.3%, -1.1%]); it narrows ordinary days (coverage 0.890 to 0.819). The pooled-scale arm of the same page is a different question and is in the last section.
- **Would reopen it:** A variant that shrinks the type factors toward one (partial pooling) is a different arm; it is listed as untested below. A longer prospective record of quarter-end days.

### S3. Pooled walk-forward recalibration of the predictive quantiles

- **Status:** failed
- **Question:** Does a pooled, walk-forward correction of the predictive quantiles (a split-conformal correction of each of the 23 levels, or an online recentre or rescale from recent public errors) improve the scaled mean reversion?
- **Studies:** #1133 (`docs/research/walk-calibration-1133-result.md`; re-read on the mean-d bound in `docs/research/walk-calibration-1133-mean-d-1167-result.md`). Also the five online recentre and rescale rules of #1525, an open pull request whose page (`hit-dependence-1523-result.md`) is not on main at the time of writing; its pooled figures point the same way, and they count only once it merges.
- **Answer:** No. The walk-forward calibration study: pooled grid CRPS 1.525 for the base and 1.550 for the corrected law, skill -1.7% [-2.9%, -0.3%]; upper-tail twCRPS -2.2% [-5.0%, +2.0%], read as a loss on the mean-d bound. The base's 90% band already covered 0.890 pooled. The correction helps quarter-ends (90% coverage 0.608 to 0.669) and costs ordinary days. The base reads no calendar column, so every figure of the walk-forward calibration study is provisional under the calendar-first rule. The hit-dependence pull request (its body): every pooled point estimate of its five adjustments is a loss on grid CRPS.
- **Would reopen it:** A re-run of the walk-forward calibration study's arm on a calendar-aware base (the page says it is a function of a base's laws and can be re-run unchanged), or the merge of the hit-dependence pull request with a different reading.

### S4. A plain linear quantile regression as a wholesale replacement

- **Status:** failed
- **Question:** Does a parsimonious linear quantile regression on the same public reserve and calendar information (B4) beat the candidate?
- **Studies:** #1360 (`docs/research/b4-quantile-regression-1360-result.md`), development window, grid CRPS (primary).
- **Answer:** No. The candidate beats B4 by +23.8% [+15.2%, +32.2%] on grid CRPS, +10.1% [+2.4%, +18.7%] on upper-tail twCRPS and +12.0% [+3.0%, +20.4%] on the Brier score of P(> +5 bp), and on every lead. B4 is worse than B1' (-13.6% [-26.5%, -3.6%]) and better than B2 (+16.4% [+8.5%, +24.4%]). On the 2026 days the candidate against B4 is undecided on all three. Whether B4 is reported beside the decision rule or joins it is a separate question for her on that pull request, not part of this entry.
- **Would reopen it:** A change of the candidate's family, or a B4 variant with a different reserve measure (the page asks that as its second question).

### S5. Longer training history for the candidate

- **Status:** failed
- **Question:** Does training the candidate on all history, or on a trailing three-year window, instead of the trailing two-year window it uses, improve it?
- **Studies:** #1364 (`docs/research/h5-robustness-1364-result.md`), development window.
- **Answer:** No. Against the candidate as run, pooled grid CRPS: all history -2.0% [-4.2%, -0.3%], trailing three years -2.3% [-4.6%, -0.9%], both losses. No arm changes the pooled reading against B1, B1' or B2. The premise of the directive ("expanding history as now") was wrong: the code uses a trailing two-year window. The shorter window and the refit cadence are not part of this entry (last section).
- **Would reopen it:** A structural change that makes older rows relevant (a regime-aware weighting), or a longer back-filled history read the way #1444 reads it (`docs/research/s3c-ann-net-backfill-1444-result.md`: undecided pooled, a cost on ordinary days).

### S6. The as-of scarcity state read inside the candidate

- **Status:** failed
- **Question:** Does reading the as-of scarcity state (reserves, bank assets and ON RRP, each at its latest public row) improve the candidate's net settlement terms?
- **Studies:** #1350 (`docs/research/h41-per-release-1350-result.md`), and its row in the family ablation #1483 (`docs/research/family-ablation-1483-result.md`).
- **Answer:** No. Candidate with the state read against the candidate: grid CRPS -1.0% [-1.7%, -0.4%] on the development window and -3.5% [-5.7%, -1.1%] on the 2026 days, both losses; upper-tail twCRPS undecided on the development window and a loss on the 2026 days (-11.2% [-16.7%, -7.0%]). Reading the H.4.1 weeklies per release instead of five calendar days after the Wednesday changes the state on a few Thursday and Friday decisions only and moves no score beyond rounding. This is the scarcity state as an input to the H5 candidate; the estimator of the state is H7, below.
- **Would reopen it:** A better-measured state (H7's estimator, if it becomes eligible), or a change in the reserve regime that the development window does not hold.

### S7. H7m, a tracked scarcity estimate that improves H5

- **Status:** failed
- **Question:** Can the distance to the demand-curve kink and the scarcity state be estimated directly, as a slow variable, well enough to be registered (H7m)?
- **Studies:** repo-market-liquidity#191, the stage verdict (`repo-market-liquidity:docs/stages/h7m-verdict.md`), and the steps before it; her ruling of 26 October 2026 on repo-market-liquidity#181, option (a). The plan's rule is `docs/research/plan.md` (H7).
- **Answer:** "Not testable as stated." No candidate is eligible after steps 2 to 5: estimators B and V1 to V6 fail goalpost 1 (a worst real-time gap of 2.00 to 8.75 points against the limit of 0.5), C fails goalpost 2 (median width 3.46 points against the bar of 3), and CV1, CV2 and CV4 are not scorable (CV3 fails on goalpost 1, unreadable on development data). Beside the rule, no interval against R+S lies at or above the MME of 0.05 and every gain against S alone is negative. The plan's consequence is that effort goes to H7f with R+S alone.
- **Would reopen it:** An estimator that holds both goalposts on the development walk-forward (the measurement protocol's eligibility rule), or her decision to change the goalposts.

### S8. The B2* upper-tail blend

- **Status:** parked
- **Question:** Does a walk-forward blend of the candidate with B2*-cap (calendar climatology, two-year lookback, minimum pool 10, the candidate's SRF cap) in the upper half of the quantile grid improve the upper tail?
- **Studies:** #1436 (the avenue), on the evidence of #1420 (`docs/research/b2-star-1420-result.md`, the mean-score table at its lines 285 to 292) and #1434 (`docs/research/capped-baselines-b2star-1434-result.md`).
- **Answer:** Not run. Her ruling of 5 November 2026 on #1436 (comment 6651114701, relayed): "Hold until after registration. This avenue stays open and parked; it is not queued as a development arm before the H5 registration." The evidence that prompted it: on the 2026 days uncapped B2* has lower upper-tail twCRPS (0.493 against 0.514) and Brier P(> +5 bp) (0.0269 against 0.0352) than the candidate, with much worse grid CRPS (2.650 against 1.669).
- **Would reopen it:** The H5 registration, by her ruling. It cannot change the registered candidate.

### S9. Reading calendar columns one row off (the one-step fit)

- **Status:** excluded
- **Question:** May a spread model train on one-step pairs (row p against the spread of p + 1) while reading a calendar or scheduled column?
- **Studies:** #914 (the finding), #947 (the guard; `docs/pivot/one-step-guard-947.md`), and the list of results this makes provisional (`docs/research/provisional-calendar-register.md`).
- **Answer:** No. `asof` rule 2 serves a calendar column from the target row, so a one-step fit learns it a day off. Her ruling: she approved the guard on 19 October 2026 (relayed, on the fixed-income reviews of main at 362df84) and ruled "calendar first" on 20 October 2026 (`CLAUDE.md`). `repo_model.one_step_guard` makes such a fit raise `ValueError`; the only exemptions are the frozen declarations in `ONE_STEP_ALLOW_LIST`. A new spread model reads the calendar at the target day, on direct pairs. A result from a model that did not is provisional until re-run.
- **Would reopen it:** Only her decision. Adding to the allow-list is hers.

### S10. Conformal layers (ACI, PID, by-day-type) on the current candidate

- **Status:** untested
- **Question:** Does an adaptive or day-type conformal calibration layer improve the current candidate (s3c-ann-net)?
- **Studies:** none on the candidate. The earlier work is on the gradient-boosted model at h = 1 and on its interior band only: #243 (`docs/interior_calibration_243.md`) and its 2026 confirmation #408 (`docs/interior_confirmation_408.md`); conformal_aci did not meet the declared test on the development days (+0.014 [-0.004, +0.033]), conformal_pid_calendar, conformal_by_day_type and conformal_group_regime met it on both windows. The arithmetic for the online and group-conditional methods is `src/repo_model/recalibration.py` (#116). #1366 (`docs/research/calibration-masking-candidate-1366-result.md`) found that the candidate has no calibration subfit.
- **Answer:** Never run on the candidate. The gradient-boosted evidence does not transfer: a different model, h = 1 only, the interior band only. The pooled split-conformal correction of the walk-forward calibration study (#1133, S3) is a different layer and lost.
- **Would reopen it:** Nothing needs to; it is open to a directive. The natural form is the delayed-feedback one below, since the hit-dependence pull request (#1525) shows the forecast reads the spread only to the day before.

### S11. A quantile correction around the forecast

- **Status:** untested
- **Question:** Does a correction applied to the candidate's quantiles around its forecast (as opposed to a rescaling of its residual pool) improve it?
- **Studies:** none found. Searched on 9 November 2026 by text in `docs/research/` pages and log entries; the modules `src/repo_model/recalibration.py` (CV+ and online conformal on the gradient-boosted model, #116) and `src/repo_model/group_calibration.py` (group-conditional recalibration of a pressure probability, #380) were identified from their docstrings only and are not studies of this question. The nearest studies are S2 (#1402) and S3 (#1133), which rescale or shift pooled levels.
- **Answer:** Never run.
- **Would reopen it:** Nothing needs to; it is open to a directive.

### S12. Recency-weighted residuals for the candidate

- **Status:** untested
- **Question:** Does weighting the residual pool of the candidate toward recent rows improve its bands?
- **Studies:** none found for the candidate. Recency weights were tried on the pressure classifiers (#411, `metadata/recency_adaptive_training.json`), and a trailing-window rescale is one of #1525's adjustments (an open pull request); neither weights the candidate's residuals.
- **Answer:** Never run.
- **Would reopen it:** Nothing needs to; it is open to a directive. The faster-scale study (#1153, S1) already shows that a faster scale alone does not remove the runs.

### S13. Partially pooled day-type shapes

- **Status:** untested
- **Question:** Does shrinking each pressure-day type's residual shape toward the pooled shape (partial pooling) improve the candidate where the types differ?
- **Studies:** none found. #1402 (S2) measured the all-types-unshrunk scale and one pooled factor for the non-ordinary types, and only scale; #1525 reports that the tails move in opposite directions on some days (dom_19_23), a level or skew that a scale cannot carry.
- **Answer:** Never run.
- **Would reopen it:** Nothing needs to; it is open to a directive.

### S14. Delayed-feedback conformal on the candidate

- **Status:** untested
- **Question:** Does a conformal update that uses only outcomes already public at the decision instant (a feedback delayed by the publication lag) calibrate the candidate?
- **Studies:** none found. #1525 (open) measures why the delay matters: a forecast for D + h reads the spread to D - 1.
- **Answer:** Never run.
- **Would reopen it:** Nothing needs to; it is open to a directive. The queued study of the test under the delay (#1528, open) decides how the coverage it would be judged on is read.

### S15. Signed net settlement and the IORB sign

- **Status:** untested
- **Question:** Do the signed net settlement size, the announced IORB change with its sign, and the net-by-scarcity interaction improve the candidate?
- **Studies:** #1273 (`docs/research/s3c-net-settlement-1273-result.md`), #1321 (`docs/research/s3c-flagnet-gross-1321-result.md`), #1227 (`docs/research/s3-iorbs-1227-result.md`), and the IORB row of #1483 (`docs/research/family-ablation-1483-result.md`).
- **Answer:** The net by scarcity interaction is untested. Eleonora ruled so on 10 November 2026; the 30 October scope decision was not a verdict. The parts that ran: the net-settlement study: net in place of gross, 2026 days +0.5% [+0.0%, +1.0%] (a gain), development window -0.1% [-0.2%, +0.1%] (undecided), with a loss on upper-tail twCRPS and Brier on the development window. The flag-plus-net study: flag-plus-net against (s3c-ann-net) +0.6% [-0.4%, +1.4%] (undecided); the gross-sized arm +0.4% [-0.4%, +1.5%] on the development window and -3.5% [-8.9%, -0.9%] on the 2026 days. The signed-IORB study: signed IORB change d +0.001 [-0.002, +0.005] against (s3), undecided, one regime loss (2024). The family ablation: IORB terms undecided in both windows. The interaction was left out of the flag-plus-net study by her ruling of 30 October 2026 ("the net x scarcity interaction in #1318 is not part of this ruling; leave it out"), a scope decision.
- **Would reopen it:** Nothing needs to; it is open to a directive. The narrower reading of the signed IORB change (target row alone, lead 1 only) was not tried (the signed-IORB study). The net by scarcity interaction was never run as its own arm; the H.4.1 per-release study (#1350) built an (s3c-ann-net x state) arm for its H.4.1 comparison only, and S6 covers the state alone.

### S16. The cash management bill term

- **Status:** failed
- **Question:** Does giving the cash management bill its own term, read from the announcement, remove the candidate's 2020 loss against (s3c) and improve it?
- **Studies:** #1356 (`docs/research/s3c-ann-net-cmb-1356-result.md`), development window and 2026 days.
- **Answer:** No. It did not remove the 2020 loss on the mean-d bound, and pooled it was undecided. Pooled grid CRPS against the candidate: flag form +0.0% [-0.2%, +0.6%] and size form +0.0% [-0.2%, +0.4%], both undecided, and undecided on the 2026 days. In 2020 against (s3c) the flag form is -1.4% [-3.2%, +0.4%] and the size form -1.5% [-3.1%, +0.0%], both still read as a loss on the mean-d bound. Both are read worse than the candidate in 2024.
- **Would reopen it:** A different handling of the bill days than the announced term. The page ends with her question whether a form replaces the candidate (default no).

## Awaiting her classification

Each entry below ran, but read undecided or covered only part of its question. Eleonora's ruling of 9 November 2026 says these are raised as questions, not settled. They carry no status until she classifies them. Q5 and Q6 were classified on 10 November 2026 and are S15 and S16; she ruled Q3 stays awaiting. "Open" names what is missing.

### Q1. The coverage test's size and power under the publication delay

- **Question:** What are the size and power of amendment 4's coverage requirement under the real one-day publication delay, read at spacing h and at spacing h + 1?
- **Studies:** #1156 (`docs/research/coverage-size-1156-result.md`: AR(1) data, no delay), #1516 (`docs/research/coverage-size-1516-result.md`: bootstrap of the candidate's own PIT ranks, no delay), #1525 (open pull request: one regime, normal errors, the delay), #1528 (queued, pull request #1535 open).
- **Answer so far:** The AR(1) coverage-size study: a calibrated forecaster fails the requirement on 100.0% of paths under `strict` and `tie_counts` and on 2.3% [1.7%, 3.1%] under the randomised tie rule. The bootstrap coverage-size study: in the iid control the design rejects a calibrated forecaster in 1.7% of draws; a world that keeps the candidate's own dependence rejects in every draw, through the independence tests. The hit-dependence pull request (its body): with the delay, a calibrated AR(1) forecaster is rejected in 83% to 100% of paths at spacing h and in 4% to 8% at spacing h + 1.
- **Open:** Volatility clustering and calendar effects together with the delay, and power at spacing h + 1; both are the queued study of the test under the delay. Until it reports, the size of the test under the delay is not established.

### Q2. Is the candidate's lead-1 hit dependence a model defect?

- **Question:** Does the serial dependence of (s3c-ann-net)'s quantile hits, which fails amendment 4's independence reading, point to a defect the model can be changed to remove?
- **Studies:** #1363 (`docs/research/candidate-calibration-1363-result.md`), #1400 (`docs/research/clustering-thinned-1400-result.md`), #1516 (`docs/research/coverage-size-1516-result.md`), #1523 and its pull request #1525 (open; its page is not on main). The runs-of-misses fixes are S1.
- **Answer so far:** The candidate calibration study: every one of the candidate's hit sequences at every lead reads as serially dependent, inside regimes too, as do those of B1, B1' and B2. The thinned-clustering study: on the thinned reading the sequences still cluster at every lead over the whole window, mainly in 2021-23, and not on the 2026 days. The bootstrap coverage-size study: 11 rejections under the iid Kupiec family, 10 under HAC. The hit-dependence pull request (pull request body, in review with changes requested): most of the lag-1 dependence is not a defect the candidate can be changed to remove, since two forecasts the design keeps h days apart share one unknown innovation; at spacing h + 1 the independence rejections go from 10 to 0; what remains is a miss rate that moves in time.
- **Open:** The merge of the hit-dependence pull request and her answer to its question on which model change, if any, is next; and the queued study of the test under the delay (#1528), which fixes how the test is judged.

### Q3. The pooled-scale arm for non-ordinary days

- **Question:** Does one residual-scale factor for the four non-ordinary pressure-day types together (ordinary days left as the candidate) improve the candidate?
- **Studies:** #1402 (`docs/research/day-type-scale-1402-result.md`). The all-types-unshrunk arm of the same page is S2.
- **Answer so far:** Pooled grid CRPS +0.8% [-0.2%, +2.8%], undecided. It gains on quarter_end_turn (+7.6% [+4.4%, +11.0%]), is undecided on turn, tax_date and on all non-ordinary days together (+2.7% [-0.0%, +6.8%]) and equals the candidate on ordinary days. On the 2026 days both arms lose on the non-ordinary target days.
- **Open:** She ruled on 10 November 2026 that this stays awaiting. A reading on prospective quarter-end days; the 2026 days are too few to decide, and the page ends with her question on whether the result enters the registration's known limits.

### Q4. A shorter training window and a different refit cadence

- **Question:** Does a trailing one-year window, or refitting every 5 or every 63 decision days instead of every 21, improve the candidate?
- **Studies:** #1364 (`docs/research/h5-robustness-1364-result.md`). The longer windows are S5.
- **Answer so far:** Trailing one year: grid CRPS +0.9% [-0.2%, +2.0%], undecided, with a gain on upper-tail twCRPS (+0.9% [+0.0%, +1.9%]); refit every 63 loses slightly (about 0.6%); refit every 5 undecided on grid CRPS. None replaces the candidate. Where readings against the benchmarks change, it is by group (the one-year window most, in 2020 and 2021-23), with some chance flags.
- **Open:** Her answer to the page's question on which reading of "expanding" she meant, and a prospective reading; the one-year window's gain sits on days already seen.

### Q7. The candidate's 2020 losses against (s3c)

- **Question:** Why does (s3c-ann-net) lose to (s3c) in 2020, and what removes it?
- **Studies:** #1319 (`docs/research/s3c-ann-net-diagnosis-1319-result.md`), #1321 (`docs/research/s3c-flagnet-gross-1321-result.md`), #1344 (`docs/research/s3c-flagnet-diagnosis-1344-result.md`), #1356 (S16).
- **Answer so far:** The first 2020 diagnosis: both announced arms lose to (s3c) in 2020 (-4.1% flag, -2.0% net on grid CRPS), mostly March to June; the net arm's cash-management-bill dating is not ruled out (those days carry 67.5% of its 2020 loss, and without them it is -0.9%, undecided). The flag-plus-net diagnosis, for the flag-plus-net arm: the 2020 loss (-3.2%) is not an over-shift of the settlement term (the fitted +1.38 bp against a realised premium of +0.28 bp [-0.37, +1.16], bias interval containing zero) and stays with the immediate-release cash management bill days left out. The cash-management-bill study (S16) did not remove it.
- **Open:** The cause. Three hypotheses were tested and none supported or rejected cleanly (over-shift, bill dating, the cash management bill term). What is missing is a reading that separates March to June 2020 from the rest of the year.

### Q8. H10, the residual dominating the attribution of pressure episodes

- **Question:** Can pressure episodes be attributed to named drivers (settlement, TGA, reserves, quarter-end), or does the residual dominate?
- **Studies:** repo-market-liquidity#73 (step 2) and repo-market-liquidity#78 (step 3), page `repo-market-liquidity:docs/research/h10-development-table.md`, with the sensitivity runs of repo-market-liquidity#88 and repo-market-liquidity#90. The plan's kill rule is `docs/research/plan.md` (H10). The prospective job is #1322 and #1426 (`docs/research/log/2026-10-30-model-01322-H10-step3.md`).
- **Answer so far:** The development table reads "residual dominates": 4 of 31 onsets under the residual bar (6% to 26%), 14 of 31 beating the null (31% to 60%), 4 of 31 on both; the median residual share is 0.78 (0.66 to 0.85). Two sensitivity runs read the same. The page says this describes the development table and is not a verdict.
- **Open:** The prospective confirmation. The method was registered by Eleonora on 3 November 2026 and the live job is pinned (#1426); no verdict exists. Whether a development reading that meets the plan's kill rule makes this failed, before the prospective days, is hers.
