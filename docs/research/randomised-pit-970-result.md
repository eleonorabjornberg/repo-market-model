# The randomised PIT beside the midpoint PIT (#970, H5 step 3)

**Development data, not a verdict.** A correction to a diagnostic of #707, not a new result about a model: nothing is published or registered, no
published declaration or record changes, and the old page (`docs/pivot/h5-step3-diagnoses-result.md` and its evidence) stands. Declaration:
`metadata/randomised_pit_970.json`. Script: `scripts/randomised_pit_970.py`.

## Why

The target is a whole number of basis points, so a forecast's 23 quantiles often tie with the outcome. The PIT of #707 takes the midpoint of the
level bracket the outcome falls in (a tie takes the midpoint of the tied levels), which is not uniform even for a perfect forecast of an integer
outcome: a test in `tests/test_randomised_pit_970.py` shows a simulated perfect forecast putting 20% of its midpoint PITs at or below 0.10 and
10% of its randomised ones. The randomised PIT (Czado, Gneiting and Held, 2009) draws the value uniformly in the bracket
(`[lo, hi]`: the largest grid level whose quantile is below the outcome, and the smallest whose quantile is above it; with no tie it is the bracket the
midpoint uses). The question, declared before any number: does the 2021-23 low-PIT share that #707 reported survive?

## What was run

The same cells as #707, rebuilt from the same 25 walks of #634 (five variants, five leads; the walks took about an hour on four cores in the
cloud, so no `needs-mac` step): 1,868 decision days to 2025-12-23, leads 1 to 5, a missing lead filled by B1, the 2021-23 window by the regime of
the decision day (748 days, 3,740 cells). Published panel `4ddc3882cd6d…`. The midpoint bins reproduce #707's report to the digit
(`docs/pivot/evidence/h5-step3-707/report.md`: 0.42 0.19 0.22 0.09 0.05 0.04 for `c_two_part_new`, 0.33 0.26 0.17 0.11 0.05 0.08 for `gbm_funding`).
Seed 970, one draw per cell in (decision day, target day) order; then 20 further seeds (971 to 990).

## Result

The first column of "bins" is strictly below 0.10 (as in #707); "≤0.10" counts a value of exactly 0.10 too, which only the midpoint PIT takes.

| candidate | cut | cells | midpoint PIT ≤0.10 | randomised PIT ≤0.10 | midpoint bins | randomised bins |
|---|---|---|---|---|---|---|
| c_two_part_new | 2021-23 | 3740 | 0.438 | 0.421 | 0.42 0.19 0.22 0.09 0.05 0.04 | 0.42 0.18 0.22 0.09 0.05 0.04 |
| c_two_part_new | all days | 9340 | 0.253 | 0.247 | 0.25 0.13 0.22 0.16 0.10 0.14 | 0.25 0.13 0.22 0.16 0.11 0.14 |
| gbm_funding | 2021-23 | 3740 | 0.364 | 0.343 | 0.33 0.26 0.17 0.11 0.05 0.08 | 0.34 0.25 0.17 0.11 0.05 0.08 |
| gbm_funding | all days | 9340 | 0.268 | 0.258 | 0.26 0.16 0.17 0.14 0.10 0.17 | 0.26 0.16 0.17 0.14 0.10 0.17 |

Under 20 further seeds the 2021-23 randomised share at or below 0.10 stays in a narrow band:

- c_two_part_new: min 0.419, max 0.425; reading: **stands**
- gbm_funding: min 0.333, max 0.347; reading: **stands**

## Reading

By the declared rule the #707 reading **stands**: in 2021-23 the randomised share of PIT at or below 0.10 is 0.42 for `c_two_part_new` and 0.34 for
`gbm_funding` against 0.10 for a calibrated forecast, and no seed of the 20 brings it to 0.10 or below. The ties moved the share by 0.02 at most
(0.438 to 0.421 and 0.364 to 0.343); the six-bin picture is the same either way. Both laws sit too high in 2021-23, more than the ties explain. This
is a diagnosis on development days, not a verdict, and it changes no number on the old page.
