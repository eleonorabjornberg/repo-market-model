# Decision (draft): the H5 confirmation design

**Status: a draft for Eleonora, not in force.** Drafted by the pull request that closes #1393, on her ruling of 2
November 2026 (chat, relayed): draft the record from the second outside review's proposal, with the defaults put to
her. It takes effect only once she merges it with her own `GO` and the attestation entry that `GO` makes (#256). For
this experiment it would replace the unresolved 60/125/250-day sequential design of
`docs/decisions/scoring-protocol.md`. **Serves** H5 (primary goal), registration design (confirmation).

Nothing here registers a candidate, opens a lockbox day, or moves a published figure. Rules 5 and 6 depend on the
size-and-power study (#1392); rules 3, 7 and 10 depend on #1360, #1361, #1388 and #1389. Where a rule leans on one of
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

**3. Baselines.** Mandatory: calendar-aware persistence with the corrected horizon (B1′*, #1388) and pooled calendar
climatology (B2*, pools and fallbacks frozen before registration). B4 (#1360, a plain quantile regression on reserves
and calendar days) joins the mandatory set if it is competitive before registration. Legacy B1 is reported. (s3c) and
the announced-flag arm are logged on every origin. If an SRF cap survives rule 10, the simple baselines get the same
policy information.
*Reason:* a model that does not beat a calendar-aware simple rule has not shown skill. Baselines that lack the
policy information the candidate has make the comparison easy by construction.

**4. Decision rule.** For baseline b, W_b = 0.97 S_b − S_C, with S the score of rule 2 (lower is better), S_C the
candidate's and 0.97 the 3% practical-meaning threshold (open, rule 10). *Pass:* the simultaneous one-sided 95% lower
bound on mean W_b is above zero for every mandatory baseline. *Fail at the threshold:* the upper bound is below zero
for at least one. Otherwise *inconclusive*. *B:* a one-sided 5% test of mean S(flag) − S(net), run only after A
passes.
*Reason:* a pass must beat every mandatory baseline by a margin that matters, not by noise. "Fail" and "inconclusive"
are kept apart so that lack of power is never reported as lack of skill.

**5. Inference.** A joint stationary block bootstrap of whole origin vectors (all baselines and the candidate resampled
together), mean block 50 origins, HAC/Bartlett lag 50, 50,000 replications, seed in the manifest. Mean blocks of 20
and 100 are declared sensitivities, never alternatives. Adopted only if the size-and-power study (#1392) supports it.
*Reason:* scores are serially dependent, and resampling whole vectors keeps the dependence between the models, which
the simultaneous bound needs. A fixed block length chosen before the data cannot be tuned afterwards.

**6. Length and stopping.** 500 eligible decision origins, at least 24 calendar months, and a 30-month ceiling, after
which the result is inconclusive or operationally incomplete. One final efficacy analysis. Operational checks at 60,
125 and 250 origins look at data quality and the contract (rule 8) only: no early pass and no efficacy stopping. A
250-origin pilot is named as the alternative she may choose instead (default: 500).
*Reason:* with strong serial dependence, interim efficacy looks spend error for little power. A single analysis at a
fixed length, spanning at least two seasons of calendar days, is simpler to defend. The checks remain, so a broken
pipeline is found early.

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

**10. Open, marked for her.** Each has a default that applies if she has not answered by the next 5 pm batch. No
default changes what the project claims.
1. *The SRF cap.* Wait for #1361 and #1389. Default: decide then; the record is not merged as a registration before.
2. *The 3% threshold* of rule 4. Default: 3%, the figure already used against persistence in the protocol.
3. *The tolerances* of rule 7. Default: as proposed.
4. *500 versus 250 origins* (rule 6). Default: 500.

## How this relates to what is in force

It supersedes, for the H5 confirmation only, the sequential 60/125/250-day checkpoint design and its critical values
in `docs/decisions/scoring-protocol.md`, and the open design questions of #733. The protocol's prospective-evidence
rule, the lockbox and the information set are unchanged. Each opening of a blind-tier day remains her own attested
action (`docs/decisions/lockbox.md`).

## What is not done

- No attestation entry. `metadata/owner_attestations.json` gets a `decisions` entry only from her `GO #1393`
  comment, which a session never posts. Until then the `owner-attested` check on this pull request waits on her.
- The size-and-power study (#1392), the baselines (#1360, #1388) and the cap rule (#1389) are separate directives.
  Rules 3, 5 and 10 are revised if they come back against this draft.
