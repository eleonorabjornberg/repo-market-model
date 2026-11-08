# Registration (draft): H5, (s3c-ann-net)

**Status: a draft for Eleonora, not registered.** Hypothesis and step: H5 (primary goal), milestone M5 (candidate registered), #1510. Registering the candidate is her own GitHub action: a `GO #1510` comment, an entry in `metadata/owner_attestations.json` citing it, and her merge. A relayed ruling does not register it, and a session never posts the `GO`. Until then nothing here is in force. Pattern: `docs/decisions/final-test-preregistration.md` and section 2 of `docs/decisions/scoring-protocol.md`. Development data and a design, not a verdict.

The record is `metadata/registrations/h5_s3c_ann_net.json`. This page is its reader. Both change no threshold, critical value, MME, block length or design rule, no model, and no pin; both score no day. Her rulings of 7 November 2026 (decision docket): queue this registration; keep the confirmation as designed.

## What is registered

**The primary candidate** is (s3c-ann-net), `sc_s3c_ann_net` (`docs/research/h5-candidate.json`), frozen as ruled on 2 November 2026:

- the Standing Repo Facility cap is kept (margin 0 bp);
- probability rule (b) applies (`open_tail`: capped percentiles, open completion above the line);
- the uncapped version is reported as a secondary result, beside the capped candidate and never in its place.

**Every other frozen choice** is in the manifest, `metadata/h5_registration_manifest.json` (#1391; reader `docs/research/h5-registration-manifest.md`), taken as it stands with its search inventory of every model, arm and variant tried on the way. Each choice has a value and the one place it lives, and `tests/test_h5_registration_manifest_1391.py` fails when the code or a declaration no longer says what the manifest says. The development variant count is the generated figure of `python3 scripts/emit_progress.py` on the commit she names.

**The validation report** is `docs/model/validation.md` (#1442, H5.M5a), attached with its known limits. It documents what exists and gives no verdict.

**The code freeze** is the commit she names with her `GO` (question Q3). This pull request changes no code.

## The confirmation design, as in force

`docs/decisions/h5-confirmation-design.md` (in force since 4 November 2026, GO #1393), stated here and not restated as a new rule:

- **Claim A** is made against B1'*-cap alone (calendar-aware persistence with the corrected horizon, with the candidate's own cap and rule (b)). B2*-cap is reported beside it, and B4 too; the uncapped B1'* and B2* and legacy B1 are reported. Neither is a condition of the verdict (Q1 and Q7).
- **Rule.** W_b = 0.97 S_b - S_C on the 23-quantile score averaged over h = 1 to 5, equal weight per origin. Pass: the one-sided 95% lower bound on mean W_b above zero. Fail at the threshold: the one-sided 95% upper bound below zero. Otherwise inconclusive.
- **Length.** 500 eligible decision origins, at least 24 calendar months, a 30-month ceiling, and one final efficacy analysis. Operational checks at 60, 125 and 250 origins read data quality and the contract only.
- **Inference.** A joint stationary block bootstrap of whole origin vectors, mean block 50 origins, 50,000 replications; mean blocks of 20 and 100 are declared sensitivities.
- **Claim B** (net sizing over the announced-flag arm) is tested only if A passes and is descriptive otherwise.

## The power, beside the design

From #1392 (full mode, `docs/research/confirmation-size-power-1392-full-result.md`), the pass rate of claim A at 500 origins, in percent. Development data, not a verdict.

| bootstrap | 10% skill, B1'* binding, B2 as developed | 10% skill, both baselines | development-level skill, both baselines as developed |
|---|---|---|---|
| block resampling | 34.6 | 6.6 | 55.8 |
| regime chain | 31.6 | 3.4 | 68.6 |

500 origins is short of 80% power at 10% skill; 80% is first reached at 2,500 origins (85.8% block, 87.0% regime). A confirmation that is inconclusive at 500 origins is reported as inconclusive with this power beside it, never as lack of skill. These rates come from far fewer bootstrap draws than 50,000, from schemes that resample 2018 to 2026 origins, and from the uncapped B1'* with B2 standing in for B2*: the capped baselines are not in that study. The figures in the record are recomputed from the study's cells by `tests/test_h5_registration_1510.py`.

## Lockbox and live pin

The blind tier stays locked and this draft scores no day. Confirmation days are the business days after the registration, scored by the live pipeline at its checkpoint; each opening of a blind-tier day is her own attested action (`docs/decisions/lockbox.md`). `metadata/live_pin.json` and the pin code are not touched.

## Questions for Eleonora (marked; each default changes no claim)

Each has numbered options; the default applies if she has not answered.

- **Q1. B1'* or B1'*-cap?** The issue says the claim is against B1'* alone; the design in force says B1'*-cap. Options: 1. B1'*-cap, as the design says (default); 2. the uncapped B1'*, which needs a new decision record.
- **Q2. The attestation line.** The line in `metadata/` that a registration needs is an entry in `metadata/owner_attestations.json` with the id of her own `GO` comment, which does not exist yet. Options: 1. none now; the registering change appends it after her `GO #1510` (default); 2. a placeholder entry (the owner-attested check would fail on it). This is why that check waits on her.
- **Q3. Which commit is the code freeze?** Options: 1. the commit she names in her `GO` (default); 2. origin/main at the drafting base, b0a09d2a508eb669def3e1495aafb0316d5f32bd; 3. the merge commit of this pull request.
- **Q4. The MME.** The design records the 3% practical threshold and says the MME is set later from the power study (#1354, question 2). Options: 1. the registration carries the 3% threshold and states that no MME is set apart from it (default); 2. she sets an MME with her `GO`; 3. registration waits for an MME.
- **Q5. The bootstrap seed.** Section 2 fixes it at registration and the manifest holds none. Options: 1. she names it with her `GO` (default); 2. 1393, an arbitrary number that moves no figure but the Monte Carlo error.
- **Q6. Secondary candidates.** Options: 1. none; (s3c) and the announced-flag arm are logged on every origin and not registered (default); 2. the announced-flag arm; 3. (s3c).
- **Q7. Does B4 join the confirmatory set?** Rule 3 says only if it is competitive before registration. Options: 1. no; reported beside the claim (default, as the issue says); 2. yes, which changes the power above.
- **Q8. The coverage report.** Amendment 4 of the scoring protocol makes coverage tests (Kupiec and Christoffersen, by lead and regime, both hit rules) a registration requirement; `COVERAGE_REQUIREMENT_IN_FORCE` is still False, and #1363's page reports coverage with intervals, not those tests. Options: 1. the report is built first by a separate directive and registration waits on it (default); 2. #1363's page stands as the report; 3. she waives it for this registration.

## What was not checked

No score was run and no figure is new. Whether the validation report's own status line about the confirmation design is current is finding #1473, left alone. The capped baselines are not in the power study.

## How to check it

```
PYTHONPATH=src:tests python3 -B -m unittest test_h5_registration_1510 test_h5_registration_manifest_1391
```
