# The H5 candidate's registration manifest (draft)

**Hypothesis and step:** H5 (primary goal), registration design, identity (#1391). **A draft for Eleonora's review.** Freezing it is the registration, her own `GO`; until then nothing here is in force, no figure changes, and no choice is made on it. Development, not a verdict.

The data is in [`metadata/h5_registration_manifest.json`](../../metadata/h5_registration_manifest.json). This page is the reader's guide to it.

## What the manifest is for

The candidate, (s3c-ann-net), is a recipe spread over several historical declarations. The outside reviews asked for one place that says, for every frozen choice, what its value is and which code implements it, and for the list of everything that was tried on the way. The manifest has three parts.

1. **Choices.** Each has a value, a plain statement of what it fixes, and one place where it lives: a constant in a `repo_model` module (`code`), a field of a tracked declaration (`json`), or a rule that is written in code with no constant to compare (`text`, with the line that holds it). A test, `tests/test_h5_registration_manifest_1391.py`, fails when the code, a declaration or a quoted line no longer says what the manifest says. So a change to a frozen choice cannot happen quietly after the freeze.
2. **The inventory.** Every model, arm and variant tried on the way to the candidate, each with its issue, pull request, merge date, result page, declaration, what it changed against its parent, and what came of it. The outcome text condenses the research log entry of the study; every figure in it is a development figure on days that were already seen. A row is marked `in_candidate` when its idea is in the candidate's code, `tried_not_adopted` when it was tried and is not, `incumbent_replaced` for the model the candidate replaced, and `side_check` for a check that changed nothing.
3. **The genealogy.** The chain of adopted steps from persistence to the candidate.

## The recipe, in order

The candidate forecasts the SOFR minus IORB spread at leads 1 to 5 business days, as 23 quantiles, at 18:00 New York time on the last panel day before the target.

1. **Centre.** The level is the median of the last ten ordinary-day spreads; the forecast centre is the level plus phi to the power of the horizon (the lead plus the anchor's lag in rows) times the last public spread's distance from the level. One phi, common to the five leads, is chosen on a grid from 0 to 1 by least squares on the trailing two years of pairs, refitted every 21 decision days, with at least 60 pairs.
2. **Scale.** Each pair's residual is divided by the scale at its origin: 1.4826 times the median absolute daily change over the last 20 rows, floored at 0.5 bp. A forecast is multiplied by the scale at the anchor.
3. **Terms.** The standardised residual is regressed, by a Huber fit with a ridge of 5, on seven additive terms read at the target day on direct pairs: month-end, quarter-end, tax date, coupon settlement, bill settlement, the 19th to 23rd, and the first three market days. A term with fewer than three flagged training pairs is left out of that lead's fit. There is no FOMC-day term, no IORB-window term and no scarcity interaction.
4. **Settlement sizes.** The two settlement terms are the signed net of each class, in units of USD 100 bn, read at every lead from the auction's announcement (12:00 New York on its announcement date). A class announced only in part reads zero until it is fully announced; a cash management bill counts only from its own announcement.
5. **Residual pool.** The quantiles of what is left of the standardised residuals, interpolated linearly at the 23 grid levels, give the law: centre plus scale times (term shift plus pool quantile).
6. **Cap.** From the day the facility is at full allotment (read from the policy register, as announced by the decision instant), every quantile is clipped at the Standing Repo Facility line, the minimum bid rate less IORB, with a margin of zero.
7. **Probability.** P(spread > +5 bp) is read off the 23 quantiles with a linear distribution function through them, continued at the outer slopes, at the cut of 5.5 bp (the event is strict and on whole basis points).

## Open items the manifest records and does not settle

- The study scripts take the decision instant from the environment variable `RMM_DECISION_TIME`, whose default is now the library constant, 18:00 (her ruling of 2 November 2026, #1397). Historical records and declarations keep the instant they were made at, and a re-run of an old record sets `RMM_DECISION_TIME=16:00` explicitly. Settled; listed here so a reader sees it moved.
- `repo_model.srf_line.DECISION_TIME` is still the 16:00 of the dated declarations of #1241 and #1252, kept as a legacy constant (#1312). The cap reads the instant the walk passes. Re-declaring the cap's availability at 18:00 is a later directive.
- #1389 asks for one coherent rule for the cap, the tail completion and the probabilities. The manifest records the code as it stands on main; if that rule changes any of them, the manifest and its test change with it, in that pull request.
- Inference settings (the number of origins, the minimum skill, the bootstrap) belong to the confirmation design (#1393) and are not part of the candidate's identity.

## What was corrected with the manifest

The candidate's metadata (`docs/research/h5-candidate.json`) and the prose of its modules still said that the decision instant is 16:00. They now name the decision instant (`repo_model.decision_instant`, 18:00 since #1312). The historical declarations, which record the instant they were made at, are not edited.

## How to check it

```
PYTHONPATH=src:tests python3 -B -m unittest test_h5_registration_manifest_1391
```
