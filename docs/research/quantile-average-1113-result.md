# The quantile average of spread_mr_ctx and gbm_funding_cal_aligned (#1123, H5 step 3; avenue #1113): design

**Status: design and declaration. Nothing is scored here.** The scoring reads `gbm_funding_cal_aligned`'s and `gbm_funding`'s walks, which exist only on Eleonora's Mac (`~/rmm-1027/WALKS`, #1027), so it runs there (`needs-mac`, #46); the result page replaces this section when it has run. Development data, never a verdict. The declaration is `metadata/quantile_average_1113.json`, committed before any number was computed; the script is `scripts/quantile_average_1113.py` (commands in its docstring); the test is `tests/test_quantile_average_1113.py`.

`gbm_funding` stays the H5 candidate: this is a development arm, not a candidate change, and replacing the candidate is Eleonora's and waits for #1115 (ruling of 22 October 2026).

## The arm

For each decision day and each lead h = 1 to 5, the average's forecast is the 0.5 / 0.5 mean of the two parts' 23-level laws, level by level on the protocol grid, then sorted so it stays monotone. The parts:

| part | where its forecasts come from |
|---|---|
| `spread_mr_ctx` (#761) | computed from the published panel by the script (stdlib; no walk) |
| `gbm_funding_cal_aligned` (#1027) | the five walks of #1027's aligned variant, one per lead |

A lead a gbm walk does not carry stands in as B1, as #634 and #1027 fill it, so the average is of the forecasts as each part is scored.

## What the result page will report

Grid CRPS over h = 1 to 5 and upper-tail twCRPS of the average against both parts, `gbm_funding`, B1, B1′ (beside B1, Eleonora, 22 October 2026) and B2:

- pooled, by the five regimes (target day) and by target day type (quarter-end, month-end, tax date, settlement, ordinary), on development days to 2025-12-31 only;
- on the studentized stationary bootstrap at the protocol's block 10, with the Politis-White block of each pair's own loss differential beside it (the protocol's block is not changed);
- the 95th-percentile exceedance of every model under both hit rules, y > q and y >= q (the rule is an open question of Eleonora's; both are shown).

The declared reading rules say whether the average beats each part, and whether it beats `gbm_funding` on calendar days without losing on ordinary days. Lens C's caveat on the lag-10 standard error applies to every interval.

## How it is tested

`tests/test_quantile_average_1113.py` pins the average on hand cases (equal weights, sorting, refusal of mismatched or non-finite laws), the two hit rules and the float-noise tie, the Politis-White block, the reading rules, the committed declaration, and a whole `compute_result` run on a synthetic frame. The paste on the pull request was run end to end in a cloud session on walks of the published panel's first rows, with the figures unread.
