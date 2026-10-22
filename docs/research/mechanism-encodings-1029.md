# gbm_funding's raw levels re-encoded as the mechanism acts on them, on #1027's direct calendar design (#1029, H5 step 3): design

**Status: design and declaration. Nothing is scored here.** The walks take hours and run on Eleonora's Mac (`needs-mac`, #46); the result page replaces this section once they have been scored. Development data, never a verdict. The declaration is `metadata/mechanism_encodings_1029.json`, committed before any number was computed; the encodings are `src/repo_model/mechanism_encodings.py`, the script is `scripts/mechanism_encodings_1029.py` (commands in its docstring), the tests are `tests/test_mechanism_encodings_1029.py` and `tests/test_mechanism_encodings_study_1029.py`.

## Why

Lens D of #958: `gbm_funding` reads raw levels whose meaning does not transfer across regimes. The 4-week bill level correlates +0.12 with the next-day spread in 2018 to 2019 and negative in 2024 and 2025 to 2026; reserves were $1.4 to 1.7tn in the 2019 stress and $2.8 to 3.5tn in the 2025 stress; `sofr_volume` tripled; the SOFR percentile levels track the policy rate. A tree fitted on them learns cut-points of one regime that do not recur. Each is replaced by the quantity the mechanism acts on.

## The variant

`gbm_funding_cal_direct_enc` is #1027's `gbm_funding_cal_direct` (direct pairs, the calendar and scheduled columns read from the target row, the observed net-settlement columns, leaf 5) with these replacements, in place, and nothing else changed:

| raw level | encoding | constituents |
|---|---|---|
| `tbill_4w`, `tbill_13w` | bill less IORB, bp | the bill, `iorb` |
| `sofr_p25` | SOFR less its 25th percentile, bp | `sofr`, `sofr_p25` |
| `sofr_p75` | its 75th percentile less SOFR, bp | `sofr_p75`, `sofr` |
| `sofr_volume` | over the median of the trailing year of panel rows | `sofr_volume` |
| `reserve_balances` | over the median of the trailing year of panel rows | `reserve_balances` |

`tga`, the lagged spread, `treasury_settlement` (lead 1), the target-row columns and the observed columns are unchanged. The trailing window is 250 panel rows ending at the row, the row included, at least 20 present (a larger minimum leaves the first fit's training window with no observed value of the column, which the fitter refuses).

## No new publication instant

Each encoding is a function of its own row and earlier rows, declared on the union of its constituents' source fields, so `asof.InformationRule` reads it at the latest row on which every constituent was public: the row of the slowest constituent. An earlier row is public before a later one, so the trailing median adds no instant. `InformationRule`, `contract.FEATURE_FIELDS` and the registry are unchanged; `mechanism_encodings.switched_on` adds the columns for one run, as `net_settlement.switched_on` does. The test pins each column's read row against its constituents' at every lead through the real rule and registry, runs both guards on every information set, and has a recorded mutation for the declaration, the causal window and the slower-leg case.

## Marked questions for Eleonora

1. **The reserves ratio's denominator.** Lens D's list says "reserves as the as-of ratio already built for H7", which divides by commercial banks' total assets (H.8). That adds the H.8 as a slower leg, about ten days back, whereas this directive asks for "the same publication instants". Default (declared): reserves over their own trailing-year median, which keeps the reserves' instant. Option 2: the H7 ratio to bank total assets, as a second arm after the first has been read (#634 variant (b) tried it without gain). Option 3: both in one declared variant.
2. **Which #1027 variant to build on.** Default (declared): the direct one. The aligned one-step variant needs an allow-list entry per changed regressor set in `one_step_guard.ONE_STEP_ALLOW_LIST` (Eleonora's; the #1027 entries carry an end date and name the raw levels). Option 2: admit entries for the encoded regressors and add the aligned arm.
3. **SOFR less its 25th percentile.** The directive lists p75 less SOFR; Lens D's list adds SOFR less p25. Declared: both, so that no raw percentile level stays among the inputs. Option 2: p75 only, and drop `sofr_p25` from the inputs.

## What the result page will report (criterion 3)

Paired grid CRPS and upper-tail twCRPS of the variant against `gbm_funding`, #1027's `gbm_funding_cal_direct` (re-walked on the same panel), B1, B1', B2 and `spread_mr_ctx`, pooled, by regime and by target day type (quarter-end, month-end, tax date, settlement, ordinary), on development days to 2025-12-31 only, on the studentized one-sided bound (ruling 1) with Lens C's caveat on the lag-10 standard error. The per-regime skill over `gbm_funding_cal_direct` is the table to read for the point of the encodings. Replacing the candidate is Eleonora's decision.
