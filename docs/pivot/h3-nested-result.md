# H3 step 3: does new public data improve H5's candidate? The nested test (#708)

Hypothesis and step: **H3** (new public data adds signal), step 3 of `docs/research/hypotheses/H3.md`, milestone M3: each usable source family of #630 added to H5's candidate, one at a time, scored as the nested difference. **Development data, not a verdict** (scoring protocol v1, #640; #46 top block): nothing here supports, kills or registers a candidate, publishes a figure or moves a declaration.

A scratch measurement. The candidate is `gbm_funding`, #634's gradient-boosted quantile regression at the protocol's 23 levels on the published funding features alone (Eleonora's ruling of 15 October 2026 on PR #763). Each family's columns are added to its features, one family per run, with the same settings, folds and seed; each column is read at its registered availability under the as-of rule and is off in every published declaration. Scored with the protocol's scorer (`repo_model.scoring_protocol`: grid CRPS over 23 levels, equal weight over h = 1 to 5, one number per decision day), against B1 as-of persistence and B2 calendar climatology.

## Declared before any number

* **Declaration: `metadata/h3_nested_708_gbm.json`**, committed (commit `2a4b0472`) before any walk. It is the declaration this page reads, under Eleonora's ruling of 17 October 2026. `metadata/h3_nested_708.json` is the earlier plan (candidate: #634's variant (b), the same model with #634's new inputs). It is left untouched and **was not scored**; no table below reads it.
* **Reading rule** (from the declaration): a family improves the candidate when the one-sided 95% lower bound of the mean daily difference on the primary score is above zero. H3's kill reading: no family improves the candidate beyond its interval.
* **Interval:** studentized stationary bootstrap (Newey-West lag 10, mean block 10, 10,000 draws, seed 708), one-sided 95%. Holm-adjusted p-values beside it for the four families (nothing is a claim).
* **Window:** 1,868 decision days, 2018-06-29 to 2025-12-23 (fifth target day on or before 2025-12-31); no 2026 day is read and no locked day is scored (`docs/decisions/lockbox.md`).
* **Pins:** published panel `4ddc3882…` (built from the tracked fixtures, `REPRODUCIBILITY.md`); scratch panel `a1cb8bcd…` (#634's chain, then `scripts/new_sources.py panel`); base `507a2fd0`; seed 708.

## Result

The base reproduces #634's `gbm_funding` row on the same days (1.826 bp, +20.7% against B1, +27.4% against B2).

| model | grid CRPS (bp) | skill vs B1 [one-sided 95%] | skill vs B2 [one-sided 95%] |
|---|---|---|---|
| B1 as-of persistence | 2.302 | | |
| B2 calendar climatology | 2.514 | | |
| candidate (`gbm_funding`) | 1.826 | +20.7% [+13.2%, +40.4%] | +27.4% [+17.7%, +36.8%] |
| + nyfed_pd_financing | 1.824 | +20.8% [+13.3%, +40.8%] | +27.5% [+18.0%, +36.7%] |
| + treasury_auction_results | 1.839 | +20.1% [+12.5%, +40.3%] | +26.9% [+17.3%, +36.2%] |
| + nyfed_on_rrp_counterparties | 1.817 | +21.1% [+13.8%, +40.4%] | +27.7% [+17.9%, +37.2%] |
| + treasury_dts_debt_cash | 1.842 | +20.0% [+12.3%, +40.6%] | +26.7% [+17.3%, +36.1%] |

Nested difference (candidate minus candidate + family; positive favours the family), skill and one-sided 95% bounds:

| family | primary (grid CRPS) | upper-tail twCRPS | Holm p | reading |
|---|---|---|---|---|
| nyfed_pd_financing | +0.1% [-1.1%, +1.3%] | +0.2% [-1.3%, +1.7%] | 1.000 | no improvement beyond its interval |
| treasury_auction_results | -0.7% [-1.4%, -0.1%] | +0.0% [-0.8%, +0.8%] | 1.000 | no improvement; worse beyond its interval |
| nyfed_on_rrp_counterparties | +0.5% [-0.1%, +1.1%] | +0.3% [-0.3%, +1.0%] | 0.260 | no improvement beyond its interval (lower bound of mean(d) -0.0007 bp) |
| treasury_dts_debt_cash | -0.9% [-1.6%, -0.3%] | -0.6% [-1.4%, +0.1%] | 1.000 | no improvement; worse beyond its interval |

**H3 overall (development, not a verdict): no family improves the candidate beyond its interval on the pooled primary score; the kill reading is met on development data.** Two families (`treasury_auction_results`, `treasury_dts_debt_cash`) make the pooled score worse beyond the interval.

## Splits (reported, no pass requirement; `evidence/h3-nested-708/report.md` has every cell)

* **Ordinary targets** (the kill criterion's wording, "on ordinary days"): `nyfed_on_rrp_counterparties` is +0.7% [+0.0%, +1.4%], lower bound of the mean daily difference +0.0001 bp; the other three families' bounds are below zero. This is one cell of many, unadjusted for the splits, and the pooled and Holm readings above do not support it. Not a claim; flagged as a question below.
* **Quarter-end targets** (n = 146): `nyfed_pd_financing` +1.3% [+0.3%, +2.2%], and `nyfed_on_rrp_counterparties` +0.5% [+0.0%, +1.1%], by the skill bounds; the lower bounds of the mean difference are both below zero.
* **Regimes** (hindsight): `nyfed_pd_financing` +5.2% [+0.7%, +11.6%] in 2020 and -4.7% [-8.2%, -1.6%] in 2021-23; `treasury_auction_results` -4.6% [-7.0%, -2.7%] in 2021-23.
* **As-of scarcity state:** `treasury_auction_results` -2.0% [-3.2%, -0.8%] in the low state; none improves in the high state.
* **By lead:** only `nyfed_on_rrp_counterparties` has a lower mean grid CRPS than the candidate at every lead (by 0.001 to 0.015 bp); `nyfed_pd_financing` is worse at h = 1 and 2 and better at h = 3 to 5; `treasury_auction_results` and `treasury_dts_debt_cash` are worse at every lead.

## What was not checked

* Combinations of families, tuning of any family, #634's new inputs on top of the base, and the two-part form as a base (all declared out).
* A confirmation: development data never gives a verdict, and no registration follows from this page.
* The ON RRP offering rate, the SRF rate, H.8 bank groups and SLR headroom (liquidity repository).

## Question for Eleonora (marked; not settled here)

Does the `nyfed_on_rrp_counterparties` reading on ordinary and quarter-end targets (a lower bound of 0.0000 to 0.0001 bp, one split of many) warrant a follow-up under the confirmation design, or does the pooled reading (no family improves) stand as H3's step 3 outcome? No family's lower bound on the primary score is above zero, so no "Publish?" issue is opened and no column joins any declaration.
