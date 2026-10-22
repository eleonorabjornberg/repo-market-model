# The #1027 direct variant with settlements dated from the auction announcement at leads 2 to 5 (#1124, H5 step 3): design

**Status: design and declaration. Nothing is scored here.** The walks take hours and run on Eleonora's Mac (`needs-mac`, #46); the result page replaces this section when they have been scored. Development data, never a verdict. The declaration is `metadata/aligned_announcement_1124.json`, committed before any number was computed; the script is `scripts/aligned_announcement_1124.py` (commands in its docstring); the test is `tests/test_aligned_announcement_1124.py`. The avenue is #1114; Eleonora's ruling of 22 October 2026, relayed by the orchestrating session, was "queue them now".

## What is measured

`gbm_funding_cal_direct` of #1027 reads the calendar columns at the target day at every lead and the Treasury settlement columns at lead 1 only: the published declaration (`metadata/sources.json`, `treasury_auctions`) dates a settlement one panel day ahead, so at leads 2 to 5 rule 2 of `docs/decisions/information-set.md` refuses it. `metadata/settlement_announcement_dating.json` (#541) measures the alternative that a settlement is public from its auction announcement, at 12:00 on the announcement date. That dating is **not in force**. This study asks what the model gains at leads 2 to 5 if it were.

| arm | adds at leads 2 to 5 | why |
|---|---|---|
| `gbm_funding_cal_direct_ann` | `treasury_settlement`, `treasury_settlement_coupons`, `treasury_settlement_bills` | the gross aggregate and its two legs |
| `gbm_funding_cal_direct_ann_coupons` | `treasury_settlement_coupons` | the coupon leg read apart from the gross aggregate: through it alone a day on which only bills settle looks like a day with no settlement (Lens A of #958) |

At lead 1 the dated column is the published panel's column on every panel day (the dating file's own rule), so both arms are `gbm_funding_cal_direct` there; `score` checks that their lead-1 walks agree and says so on the page.

## The scratch-only path

Nothing published changes: `metadata/sources.json`, the published declaration, `docs/decisions/information-set.md` and the dating file itself are untouched. The script's `arm_inputs` dates the settlement columns of the scratch panel with `settlement_dating.known_columns`, checks them with `check_known_columns` (it raises `LookAheadError` for a column that counts an auction not yet announced and `StaleReadError` for one that leaves out an announced auction), and declares them to `InformationRule` as a scheduled field available h panel days ahead in a *copy* of the registry (`result_dated_registry`). The copy is read by this script's walks and by nothing else. `tests/test_aligned_announcement_1124.py` shows that the published registry still refuses each settlement column at leads 2 to 5, that the live record's published features carry none beyond lead 1, and that building the arm's inputs leaves both so.

## The #947 guard: direct pairs, no allow-list entry

The arms train on direct pairs (`training_pairs="direct"`), which the one-step guard does not check, so no entry is added to `one_step_guard.ONE_STEP_ALLOW_LIST`. The aligned one-step design (`gbm_funding_cal_aligned`) with these columns at leads 2 to 5 would be refused by the guard and would need allow-list entries, which are Eleonora's decision; today's ruling did not admit aligned arms (#1093, #1098, #1109). It is not run. `gbm_funding_cal_aligned` is scored as a comparator only, from #1027's walks, which its existing entries admit until their end date. **The comparison is therefore across pairings** (aligned one-step against direct): `gbm_funding_cal_direct`, the same pairing and inputs without the settlement columns at leads 2 to 5, is the matched control that isolates the dating.

## What the result page will report

Paired grid CRPS and upper-tail twCRPS of each arm against `gbm_funding_cal_aligned`, `gbm_funding_cal_direct`, `gbm_funding`, B1, B1′ and B2 (and the coupon-leg arm against the aggregate arm), pooled, by regime and by target day type, on development days to 2025-12-31 only, on the studentized one-sided bound (ruling 1) with Lens C's caveat on the lag-10 standard error. Two windows: the mean over leads 1 to 5 (the protocol's figure) and the mean over leads 2 to 5 (where the arms differ). Settlement days are split into **coupon** (a coupon settles, with or without a bill) and **bill-only**, beside quarter-end, month-end, tax date and ordinary days. The declared reading rules are in the declaration: an arm helps on coupon (bill-only) settlement days when the lower end of its skill interval over the matched control is above 0, and does not lose on ordinary days. Whether the announcement dating is put in force is Eleonora's decision; this study does not make it.

## Provisional register

The script fits through `ml.fit_gradient_boosted_quantiles` on direct pairs and reads the calendar columns at the target day, so it is listed in `docs/research/provisional-calendar-register.md` as class `aligned`, not provisional (`metadata/provisional/producers/aligned_announcement_1124.json`).
