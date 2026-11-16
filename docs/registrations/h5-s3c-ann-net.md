# Registration (draft): H5, (s3c-ann-net)

**Status: a draft for Eleonora, not registered.** Hypothesis and step: H5 (primary goal), milestone M5 (candidate registered), #1510. Registering the candidate is her own GitHub action: a `GO #1510` comment, an entry in `metadata/owner_attestations.json` citing it, and her merge. A relayed ruling does not register it, and a session never posts the `GO`. `GO #1510` is not asked for until the coverage report of directive #1512 is merged (Q8). Until then nothing here is in force. Pattern: `docs/decisions/final-test-preregistration.md` and section 2 of `docs/decisions/scoring-protocol.md`. Development data and a design, not a verdict.

The record is `metadata/registrations/h5_s3c_ann_net.json`. This page is its reader. Both change no threshold, critical value, MME, block length or design rule, no model, and no pin; both score no day. Her rulings of 7 November 2026 (decision docket): queue this registration; keep the confirmation as designed.

## What is registered

**The primary candidate** is (s3c-ann-net), `sc_s3c_ann_net` (`docs/research/h5-candidate.json`), frozen as ruled on 2 November 2026:

- the Standing Repo Facility cap is kept (margin 0 bp);
- probability rule (b) applies (`open_tail`: capped percentiles, open completion above the line);
- the uncapped version is reported as a secondary result, beside the capped candidate and never in its place.

**Every other frozen choice** is in the manifest, `metadata/h5_registration_manifest.json` (#1391; reader `docs/research/h5-registration-manifest.md`), taken as it stands with its search inventory of every model, arm and variant tried on the way. Each choice has a value and the one place it lives, and `tests/test_h5_registration_manifest_1391.py` fails when the code or a declaration no longer says what the manifest says. The development variant count is the generated figure of `python3 scripts/emit_progress.py` on the commit she names.

**The validation report** is `docs/model/validation.md` (#1442, H5.M5a), attached with its known limits. It documents what exists and gives no verdict.

**The code freeze** is this pull request's merge commit (her ruling on Q3). This pull request changes no code.

## The confirmation design, as in force

`docs/decisions/h5-confirmation-design.md` (in force since 4 November 2026, GO #1393), stated here and not restated as a new rule:

- **Claim A** is made against B1'*-cap alone (calendar-aware persistence with the corrected horizon, with the candidate's own cap and rule (b)). B2*-cap is reported beside it, and B4 too; the uncapped B1'* and B2* and legacy B1 are reported. Neither is a condition of the verdict (Q1 and Q7, settled).
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

## Her rulings on the marked questions (decision docket, 7 November 2026, relayed on the pull request)

- **Q1.** The claim is against B1'*-cap, as the design in force says.
- **Q2.** The `metadata/owner_attestations.json` entry is added only after she posts `GO #1510`.
- **Q3.** The code freeze is this pull request's merge commit.
- **Q4.** The 3% threshold is registered; no separate MME is set.
- **Q5.** The bootstrap seed is 1393.
- **Q6.** No secondary candidates; (s3c) and the announced-flag arm are logged only.
- **Q7.** B4 is reported beside the claim and is not in the confirmatory set.
- **Q8.** Registration waits on the amendment 4 coverage report, built by directive #1512 (pending). `GO #1510` is not asked for until that report is merged.

## Known limits

The validation report's known limits (`docs/model/validation.md`) travel with this record, and this one is added to them by directive #1618. It changes nothing: the candidate, the design and every threshold stand, and every figure below is copied from the merged page, `docs/research/qe-vs-calendar-gbm-1593-result.md` (#1593, pull request #1599; S17 of `docs/research/settled-questions.md`, failed). Development data on days already seen, no verdict.

**Quarter-end turns and year-ends against the calendar-aware GBM.** The question was whether the calendar-aware gradient-boosted model on direct pairs (`gbm_funding_cal_direct`) forecasts these days better than (s3c-ann-net), so that it could take the candidate's place on them. Her ruling of 13 November 2026 (option (a), relayed on #1593): swapping it in is not supported, the quarter-end family keeps the frozen candidate, and no GBM or combination arm is opened. Fixing the candidate's band on these days stays with Q9. d is the GBM minus the candidate on the same cells, with 90% event-cluster intervals; positive favours the candidate on the scores.

- **Quarter-end turns, 22 events and 220 cells.** The 90% band covers 0.586 for the candidate and 0.500 for the GBM (d -0.086 [-0.245, +0.077]). Above q95 the candidate is exceeded 0.336 of the time and the GBM 0.255 (nominal 0.050). Grid CRPS 3.512 against 4.141 (d +0.629 [-0.087, +1.413]); upper-tail twCRPS 2.136 against 2.422 (d +0.286 [-0.342, +0.982]). The score and coverage intervals hold zero.
- **Year-ends, 8 events and 71 cells.** The 90% band covers 0.648 for the candidate and 0.577 for the GBM (d -0.070 [-0.141, +0.000]). Grid CRPS 8.469 against 11.507 (d +3.038 [+0.525, +6.576]); upper-tail twCRPS 7.771 against 10.316 (d +2.545 [+0.065, +6.160]).

The candidate's own band still covers far less than 90% on these days, which is the quarter-end limit that was already listed. The GBM's walks were made at the 16:00 instant and the candidate's at the 18:00 decision instant, so the GBM forecast with two hours less public information; that favours the candidate by an amount not measured. Several regime cells rest on fewer than five events, and the regimes are not tested against one another.

## What was not checked

No score was run and no figure is new. The coverage report of amendment 4 is pending (#1512). Whether the validation report's own status line about the confirmation design is current is finding #1473, left alone. The capped baselines are not in the power study.

## How to check it

```
PYTHONPATH=src:tests python3 -B -m unittest test_h5_registration_1510 test_h5_registration_manifest_1391
```

## Dated note, 2026-11-16 (finding #1625, directive #1629)

Written at 2026-11-16T11:42:44-05:00 (the commit time of the commit that adds it), before any outcome of the days it names is read. Her ruling of 16 November 2026 (docket card `f1625-registered-1116`, option (a), relayed by the orchestrating session on #1629):

- **The registration stands from her merge of #1511**, `cf21d52fe12590f619f62a932104ea09abf3c290`, merged 15 November 2026 at 19:40 New York time.
- **Confirmation counts from the first business day the pinned live record carries the candidate's forecast.** That day is not known yet: it follows from her own `GO` on the pin, which the pull request that closes #1629 asks for.
- **The unused band runs from 16 November 2026 to the business day before that day.** Those days are unused, not missing: they are not scored and not counted under section 11 of `docs/decisions/scoring-protocol.md`.
- **No outcome of the unused band has been read.**
