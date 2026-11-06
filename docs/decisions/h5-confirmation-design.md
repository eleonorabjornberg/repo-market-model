# Decision (draft): the H5 confirmation design

**Status: In force since 4 November 2026 (GO #1393, PR #1394).** Drafted by the pull request that closes #1393, on her ruling of 2
November 2026 (chat, relayed): draft the record from the second outside review's proposal, with the defaults put to
her. Revised on her rulings of 2 and 3 November 2026 (chat, relayed on #1394) and her ruling on #1399 of 4 November
2026 ("per baseline is fine, keep 500"). It takes effect only once she merges it with her own `GO` and the attestation entry that `GO` makes (#256). For
this experiment it would replace the unresolved 60/125/250-day sequential design of
`docs/decisions/scoring-protocol.md`. **Serves** H5 (primary goal), registration design (confirmation).

Nothing here registers a candidate, opens a lockbox day, or moves a published figure. Rules 5 and 6 rest on the
size-and-power study (#1392, full mode, `docs/research/confirmation-size-power-1392-full-result.md`, development data
and not a verdict); rules 3, 7 and 10 depend on #1360, #1361, #1388 and #1389. Where a rule leans on one of
them, it says so.

## The rules

**1. Claims.** *A (primary):* the frozen recipe has practically meaningful overall score skill against the
mandatory simple baselines. *B (gated secondary):* net sizing adds accuracy over the comparable announced-flag
recipe; it is tested only if A passes, and is descriptive otherwise.
*Reason:* one primary claim keeps one error rate. A multi-claim design splits the evidence and invites choosing the
claim after the data. The net-versus-flag question is real but is a refinement of a recipe that must first work.

**2. Score.** The protocol's 23-quantile score (twice the mean pinball loss on `scoring_protocol.GRID`), averaged
over h = 1 to 5 with equal weight per decision origin. It is named "23-quantile accuracy", not an integral CRPS. The
h = 1 score is reported beside it.
*Reason:* 23 quantiles approximate a CRPS but are not one, and the name should not claim more. Equal weight per origin
makes the unit of evidence the origin. h = 1 is the horizon desks use most, and an average over h can hide a loss
there.

**3. Baselines.** The confirmatory benchmarks are the capped baselines: calendar-aware persistence with the
corrected horizon (B1′*, #1388) and pooled calendar climatology (B2*, pools and fallbacks frozen before registration),
each with the same SRF cap and the same probability rule (b) as the candidate: B1′*-cap and B2*-cap. The uncapped
B1′* and B2* are reported beside them, never in their place. B4 (#1360, a plain quantile regression on reserves and
calendar days) is reported beside them and joins the confirmatory set only if it is competitive before registration.
Legacy B1 is reported. (s3c) and the announced-flag arm are logged on every origin. The cap and rule (b) are
frozen by rule 10, item 1; until then "capped" names the form and not a value.
*Reason:* a model that does not beat a calendar-aware simple rule has not shown skill. A baseline that lacks the
policy information the candidate has makes the comparison easy by construction, so the confirmatory benchmark gets
exactly the candidate's cap and rule; the uncapped version shows how much of any gap the cap accounts for.

**4. Decision rule.** The primary claim A is made against B1′*-cap alone. B2*-cap is reported beside it, with
the same statistic and the same bound, and is not a condition of the verdict. W_b = 0.97 S_b − S_C, with S the score
of rule 2 (lower is better), S_C the candidate's and 0.97 the 3% practical-meaning threshold (open, rule 10). *Pass:*
the one-sided 95% lower bound on mean W_b is above zero for b = B1′*-cap. *Fail at the threshold:* the one-sided 95%
upper bound on mean W_b is below zero for b = B1′*-cap. Each bound is per baseline, one-sided, with no multiplicity
adjustment (her ruling on #1399, Q1). Otherwise *inconclusive*. The same bounds are reported for B2*-cap and for the
uncapped B1′* and B2*; a failure of B2*-cap is reported plainly and does not change the verdict on A. *B:* a one-sided
5% test of mean S(flag) − S(net), run only after A passes.
*Reason:* one primary baseline keeps one error rate, and the size-and-power study (#1392) shows why. With both
baselines required at the threshold, power at 10% skill with 500 origins was 6.6% (block) and 3.4% (regime) and no
tested length reached 80%. With B1′* binding and B2 as developed it was 34.6% and 31.6%. A pass must still beat the
strongest simple rule by a margin that matters, not by noise. "Fail" and "inconclusive" are kept apart so that lack
of power is never reported as lack of skill. A per-baseline fail bound calls a fail more easily than a pass; the
fail is a label of what the data say and ends nothing.

**5. Inference.** A joint stationary block bootstrap of whole origin vectors (all baselines and the candidate resampled
together), mean block 50 origins, HAC/Bartlett lag 50, 50,000 replications, seed in the manifest. Mean blocks of 20
and 100 are declared sensitivities, never alternatives. The size-and-power study (#1392, full mode) is the evidence for the block length; it is development data, and
what it shows about size and power is stated in rule 6.
*Reason:* scores are serially dependent, and resampling whole vectors keeps the dependence between the models, so
that every comparison of rule 4 is paired. A fixed block length chosen before the data cannot be tuned afterwards.

**6. Length and stopping.** 500 eligible decision origins, at least 24 calendar months, and a 30-month ceiling, after
which the result is inconclusive or operationally incomplete. One final efficacy analysis. Operational checks at 60,
125 and 250 origins look at data quality and the contract (rule 8) only: no early pass and no efficacy stopping.
*Power, stated as it is* (#1392, full mode, 500 simulated data sets per cell, development data, not a verdict):
- Against B1′* binding, with B2 as developed, a true skill of 10% is passed in 34.6% of data sets at 500 origins under
  block resampling (Monte Carlo SE 2.1) and 31.6% under the regime chain (SE 2.1). 80% is first reached at 2,500
  origins (85.8% and 87.0%). 500 origins is therefore short of 80% power at 10% skill.
- With both baselines at 10%, power at 500 origins is 6.6% and 3.4%, and no tested length up to 1,500 reaches 80%.
  This is why rule 4 makes the claim against B1′*-cap alone.
- At the 3% boundary the pass rate is at most 1.4% with both baselines at 3%. With B1′* at 3% and B2 as developed it
  is 6.2% (block) and 6.4% (regime) at 500 origins, and up to 10.8% (regime, 250 origins) and 8.6% (block, 750
  origins) at other lengths, against a nominal 5%: the size is conservative when both baselines bind and somewhat
  above nominal when one does.
- Claim B's rejection rate at 0% net-over-flag skill is 15.0% (block, SE 1.6) and 6.4% (regime, SE 1.1) at 500 origins,
  against a nominal 5%: B can be over-sized under dependence and is read as descriptive.
- These rates come from a bootstrap with far fewer draws than the 50,000 of rule 5 and from schemes that resample 2018
  to 2026 origins; a regime the pool does not contain is outside them. B2 stands in for B2*, and the capped baselines
  are not built, so the rates describe the test and are not a forecast of this candidate's result.
A confirmation that is inconclusive at 500 origins is reported as inconclusive with this power beside it, never as
lack of skill.
*Reason:* with strong serial dependence, interim efficacy looks spend error for little power. A single analysis at a
fixed length, spanning at least two seasons of calendar days, is simpler to defend. The checks remain, so a broken
pipeline is found early. She ruled to keep 500 and state the power; the longer length that reaches 80% is a data
collection of years and is not adopted.

**7. Calibration** is a separate verdict, not part of A. It uses randomized PIT and band hits by lead and by
declared day group, on the frozen distribution (the cap rule comes from #1389). Proposed equivalence tolerances at
h = 1: 50% band within ±5 points, 90% band within ±3 points (**proposals**, open, rule 10). Quarter-end and year-end
days are listed one by one and never certified.
*Reason:* a forecast can win on score and still mislead through its bands. Few quarter- and year-end days exist, so a
certificate would claim more than the data can give.

**8. Contract.**
- Forecasts are made at 18:00 New York time, are immutable, and are digested before any outcome exists. No backfill.
- Outcome = first-published SOFR minus the administered reserve rate. Revisions are archived apart.
- A candidate outage uses the registered baseline fallback, is counted, and has a 5% ceiling.
- Missing outcomes are excluded for all models under one rule.
- A shakeout of 10 to 20 operating days before the start counts as development.

*Reason:* each line closes a way for the record to be edited, filled in or selected after the fact. A rule that
treats all models alike on missing data keeps the paired comparison paired.

**9. Amendments.** Any change to information, target, parameters, cap or calibration starts a new named version and a
new count of origins. Old evidence stays visible.
*Reason:* a changed recipe is a different forecast. Carrying its count across would let the sample absorb the fix.

**10. Open, marked for her.** Items 1 to 3 have a default that applies if she has not answered by the next 5 pm batch. No default changes what the
project claims. Settled by her rulings and no longer open: 500 origins (rule 6), the claim against B1′*-cap alone with
B2*-cap beside it (rule 4), the capped baselines as the confirmatory benchmarks (rule 3), and the per-baseline fail
bound (rule 4).
1. *The SRF cap.* Wait for #1361 and #1389. Default: decide then; the record is not merged as a registration before. The capped baselines of rule 3
take whatever cap and rule (b) this settles.
2. *The 3% threshold* of rule 4. Default: 3%, the figure already used against persistence in the protocol.
3. *The tolerances* of rule 7. Default: as proposed.

## How this relates to what is in force

It supersedes, for the H5 confirmation only, the sequential 60/125/250-day checkpoint design and its critical values
in `docs/decisions/scoring-protocol.md`, and the open design questions of #733. The protocol's prospective-evidence
rule, the lockbox and the information set are unchanged. Each opening of a blind-tier day remains her own attested
action (`docs/decisions/lockbox.md`).

## What is not done

- No attestation entry. `metadata/owner_attestations.json` gets a `decisions` entry only from her `GO #1393`
  comment, which a session never posts. Until then the `owner-attested` check on this pull request waits on her.
- The baselines (#1360, #1388) and the cap rule (#1389) are separate directives, and the capped baselines are not built
  yet. Rules 3 and 10 are revised if they come back against this draft.
- The size-and-power study stands in B2 for B2*, built no capped baseline, and is not split by regime or day type
  beyond its two schemes. It is evidence about the test, not about the candidate.
