# H4 step 3: the back-fill against H5's candidate, development days (#726)

Hypothesis and step: **H4** step 3 (development nested test, reported for 2018–19 and overall), done against H5's candidate. Step 4 (registration) is Eleonora's and rides H5's registration.

A scratch measurement under `docs/decisions/scoring-protocol.md` (version 1, #640). Development data only: it gives a score and an interval, never a verdict. It writes nothing into `docs/runs/`, publishes nothing, moves no published figure, scores no day after 2025-12-31 (`docs/decisions/lockbox.md`) and changes no rule. Everything was declared in `metadata/backfill_h5_726.json` and committed before any score.

## What was run

- **Candidate.** #634's `gbm_funding`: the phase 2 gradient-boosted quantile model on the published features, at the 23 levels of the grid, h = 1 to 5, refit every 21 decision days. Why this one: #634 names no single best candidate (none of its variants beat the published declaration on the primary score), this is the lowest-scoring 23-level model without the new inputs, and the variants read columns no back-filled row carries. **Question for Eleonora below.**
- **Arms.** `without`: the published panel (digest `4ddc3882…`), exactly #634's control. `with`: the same candidate, folds and days, with the 899 back-filled rows (2014-08-22 to 2018-03-29) in every training frame (panel `1e09ae43…`). Every fit passes `backfill.require_posting_established` with the instant of `metadata/backfill_posting.json` (2018-05-17) and the scored folds pass `backfill.require_training_only`.
- **What a back-filled row carries.** Only what was established: SOFR, IORB, SOFR volume, TGCR, BGCR and the calendar columns. Every other cell (reserve balances, TGA, settlements, bill rates, SOFR percentiles) is blank, because #661 established the posting instant of the three rates only. The fitter reads a blank cell through its fitted imputation.
- **Scoring.** Grid CRPS over h = 1 to 5, one number per decision day, paired; d = CRPS(without) − CRPS(with), positive when the history helps; stationary bootstrap, mean block 10, 10,000 draws, seed 726. The calibrated critical values of #695 are defined for confirmation windows of 60, 125 and 250 days, not for a development sample of this length, so the one-sided bound is the bootstrap's; the bound at the 250-day value (5.455) is shown beside it.

## Result

Decision days 2018-06-28 to 2025-12-23 (1869; the first has its lead-1 target on 2018-06-29, the first scored target; none dropped). Full tables, including the pressure-day types, the upper-tail twCRPS and the coverage moves: `evidence/backfill-h5-726/score.md`, data in `score.json`.

| group | days | CRPS without | CRPS with | mean d | one-sided 95% lower | 90% interval | skill vs B1 without → with |
|---|---|---|---|---|---|---|---|
| all days | 1869 | 1.830 | 1.831 | −0.001 | −0.037 | [−0.038, +0.040] | +20.6% → +20.6% |
| **2018–19** | 376 | 4.005 | 4.119 | **−0.114** | −0.180 | [−0.168, −0.061] | +30.2% → +28.2% |
| 2020 | 251 | 1.417 | 1.317 | +0.100 | −0.024 | [−0.020, +0.257] | +13.8% → +19.9% |
| 2021–23 | 748 | 0.717 | 0.670 | +0.047 | −0.018 | [−0.022, +0.131] | −0.9% → +5.7% |
| 2024 | 250 | 1.411 | 1.442 | −0.030 | −0.077 | [−0.064, −0.001] | +16.2% → +14.4% |
| 2025–26 | 244 | 2.742 | 2.791 | −0.048 | −0.088 | [−0.083, −0.015] | +15.1% → +13.6% |

2018–19 coverage of the central 90% interval, with minus without: 0.688 → 0.659, a move of −0.029 [−0.064, +0.007]; of the central 50% interval 0.343 → 0.289 (−0.054 [−0.084, −0.024]); the share above q0.95 0.161 → 0.192 (+0.031 [+0.007, +0.057]). Upper-tail twCRPS, 2018–19: d −0.064 [−0.100, −0.027].

## The answer, in words (development, not a verdict)

- **Does the back-fill move H5's 2018–19 score beyond its interval?** Yes, but the wrong way: with the history, the candidate's 2018–19 grid CRPS is worse by 0.114 bp [0.061, 0.168], and the interval excludes zero. The one-sided lower bound for a gain is −0.180, so there is no gain beyond the interval.
- **Does it cost anything elsewhere?** Slightly: 2024 (−0.030) and 2025–26 (−0.048) are worse with the interval below zero. 2020 and 2021–23 look better with it, but their intervals cover zero. Over all days the two arms are the same (−0.001 [−0.038, +0.040]).
- **H4's kill rule, read in words.** "No development gain beyond the interval" holds for this candidate and this way of carrying the history, so on development data H4 is not supported by this test. This is labelled exploration. It conflicts with #633's finding on a scratch model (2018–19 coverage up, CRPS unchanged), which used inputs the back-filled rows carry.

## Why the result is narrower than it reads

The candidate reads reserve balances, TGA, settlements and bill rates, which no back-filled row may carry. A back-filled training row therefore carries the spread's own history and the SOFR volume and the fitter's imputation for every other input. The test says what longer history does to this candidate when most of its inputs are imputed in the extra rows. It does not say what longer history with its inputs would do, and it cannot, until the posting dates of the 2014–17 reserve, TGA and bill-rate series are established. The imputation itself may be what moves the 2018–19 score (the first fits train mostly on imputed rows).

## Not checked, or for Eleonora

- **Question (hers): which candidate is "H5's best candidate".** #634 names none. This test used `gbm_funding` (reason above). If she names another, the same script and declaration rerun for it; variants (a) to (c) cannot read the back-filled rows at all.
- **Question (hers): the way blank cells are read.** The fitter's own imputation was used, as declared. A different reading (drop the unestablished inputs from the candidate in both arms, as #633 did on a scratch model) is a different candidate and a separate decision.
- Nothing joins a published declaration. The amendment of `information-set.md` for the back-fill (#734) has not merged, so the back-filled rows stay off in every published declaration. No "Publish?" issue arises.
- Not run: the as-of scarcity-state split; any 2026 day; the outcomes are the panel's `spread_bps`, not re-derived from first-published vintages (protocol §11).
- Variant count: one new fit per lead (the with arm, five fits); the without arm re-runs #634's control.
