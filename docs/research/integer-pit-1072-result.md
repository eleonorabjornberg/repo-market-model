# The randomised PIT for a whole-basis-point outcome (#1072, H5 step 3)

**Development data, not a verdict.** A correction to a diagnostic of #970 (PR #984), not a result about a new model: nothing is published or registered, no published declaration or record changes, and #984's page (`docs/research/randomised-pit-970-result.md`) and its record are not edited; this page cites them. Declaration: `metadata/integer_pit_1072.json`, committed before any number was computed. Script: `scripts/integer_pit_1072.py`. Figures: `docs/research/integer-pit-1072/result.json` and the table `docs/research/integer-pit-1072/report.md`.

## Why

The target is a whole number of basis points. #970's randomised PIT draws uniformly inside the bracket of grid levels around the outcome `y` (`pit_bracket`), so it differs from the midpoint PIT of #707 only when a quantile ties `y` exactly (finding #1069). The proper randomised PIT for an integer-valued outcome (Czado, Gneiting and Held, 2009) treats the law as a forecast of the rounded value and draws uniformly in `(F(y - 1/2), F(y + 1/2))`, with `F` the law's distribution function. `F` is read off the 23 quantiles: linear between neighbouring quantiles, right-continuous, the largest level at a tie, and the mass beyond the end quantiles placed at those quantiles. A law narrower than one basis point that lies entirely in `(y, y + 1/2]` gets a PIT of about 0 from the version of #970 and a uniform draw over `(0, 1)` from the proper one; `tests/test_integer_pit_1072.py` shows both, and shows that the proper PIT of a perfect forecast of a rounded outcome has 10% of its values at or below 0.10 where #970's has far more.

## What was run

Lead 1 only. The walks are `gbm_funding` (#634's walk) and the two variants of #1027 (`gbm_funding_cal_aligned`, `gbm_funding_cal_direct`), each walked with its script and read unchanged, on the published panel `4ddc3882cd6d…` (the variants on #951's scratch panel). #1027 left the choice between its variants to Eleonora, so both are read, beside the control. The cells are the target days every walk has a law for, to 2025-12-31; the decision day is the business day before the target and the regime is that of the decision day. Seed 1072, one draw per cell in (decision day, target day) order, then 20 further seeds (1073 to 1092). The old `gbm_funding` reading at all five leads was provisional under calendar first; this page does not replace it.

## Result

Share of PIT at or below 0.10 (0.10 for a calibrated forecast), three versions side by side; the cell counts and the six bin shares of each version are in `report.md` and `result.json`.

| candidate | cut | midpoint (#707) | #970 | proper (#1072) |
|---|---|---|---|---|
| gbm_funding | all days | 0.245 | 0.236 | 0.194 |
| gbm_funding | 2018-19 | 0.205 | 0.205 | 0.191 |
| gbm_funding | 2020 | 0.195 | 0.195 | 0.207 |
| gbm_funding | **2021-23** | 0.330 | 0.314 | **0.211** |
| gbm_funding | 2024 | 0.156 | 0.156 | 0.144 |
| gbm_funding | 2025-26 | 0.190 | 0.190 | 0.161 |
| gbm_funding_cal_aligned | all days | 0.308 | 0.296 | 0.221 |
| gbm_funding_cal_aligned | 2018-19 | 0.231 | 0.231 | 0.229 |
| gbm_funding_cal_aligned | 2020 | 0.235 | 0.235 | 0.223 |
| gbm_funding_cal_aligned | **2021-23** | 0.455 | 0.425 | **0.267** |
| gbm_funding_cal_aligned | 2024 | 0.152 | 0.152 | 0.152 |
| gbm_funding_cal_aligned | 2025-26 | 0.210 | 0.210 | 0.185 |
| gbm_funding_cal_direct | all days | 0.289 | 0.282 | 0.209 |
| gbm_funding_cal_direct | 2018-19 | 0.210 | 0.210 | 0.215 |
| gbm_funding_cal_direct | 2020 | 0.199 | 0.199 | 0.215 |
| gbm_funding_cal_direct | **2021-23** | 0.471 | 0.451 | **0.271** |
| gbm_funding_cal_direct | 2024 | 0.120 | 0.120 | 0.112 |
| gbm_funding_cal_direct | 2025-26 | 0.125 | 0.125 | 0.129 |

Under 20 further seeds the proper 2021-23 share stays in a narrow band: `gbm_funding` 0.187 to 0.221, `gbm_funding_cal_aligned` 0.241 to 0.267, `gbm_funding_cal_direct` 0.235 to 0.271.

## Reading

**The 2021-23 low-PIT share moves.** On the version of #970 it is 0.31 to 0.45 for the three candidates, close to the midpoint PIT; on the proper PIT it is 0.21 to 0.27. The excess over 0.10 falls by about half for each of the three candidates. Outside 2021-23 the three versions agree to within about 0.03 (the proper one is lower on all days mainly through 2021-23), so #970's remark that ties moved the share by 0.02 at most was a statement about the bracket, not about the discreteness: its draw barely randomises.

**By the declared rule (#970's, unchanged) the 2021-23 reading still stands** for all three candidates: the proper share is above 0.15 and no seed brings it to 0.10 or below. It stands at a smaller size. For `gbm_funding` the proper share (0.21) is near the 0.15 line the rule uses; for the two variants it is 0.27. So 2021-23 remains the regime where the lead-1 laws put too much mass in the lowest tenth, but about half of the size #970 reported was a discretisation artefact. The variants' extra low-PIT mass in 2021-23 over `gbm_funding` (0.27 against 0.21) is the same direction as their weakness there in #1027's score.

## What this does not show

Lead 1 only, as the directive asks: the other leads are not re-read. The tails of `F` are a convention (a point mass at the end quantiles), which matters only for a law narrower than its own end quantiles; the bin shares at 0.10 and 0.90 are the ones it touches. The proper PIT treats each law as a forecast of the rounded value; whether the scored laws should be read that way is a modelling statement of the diagnostic, not a rule. Development days only, no locked day, no verdict. Whether this changes H5's diagnosis of the floor regime, or the order of #707's avenues, is Eleonora's call.
