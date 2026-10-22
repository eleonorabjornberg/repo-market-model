# The FOMC meeting columns on the calendar-aware variants (#1087, H5 step 3, calendar first)

**Development data, not a verdict.** Nothing is published or registered, and no published declaration, record or figure changes. Declaration: `metadata/fomc_variants_1087.json`, committed before any number was computed. Script: `scripts/fomc_variants_1087.py`. Design: `docs/research/fomc-variants-1087.md`. Figures: `docs/research/fomc-variants-1087/result.json` (the headline skills) and `score.json`; the full tables are `report.md` there. The walks ran on Eleonora's Mac and came back as a commit on this branch.

## What was run

One arm, `gbm_funding_cal_direct_fomc`: the #1027 direct variant `gbm_funding_cal_direct` plus `fomc_meeting_day` and `fomc_days_to_next_meeting` at every lead h = 1 to 5, read at the target day (`fomc_registry(h)`, #1038's calendar). It is scored against that variant and against the control `gbm_funding`, on the same 1855 decision days (first 2018-07-19, last 2025-12-23, targets to 2025-12-31), grid CRPS and upper-tail twCRPS, on the studentized stationary bootstrap (seed 1087, 10000 draws). The arm's walks were made from #1027's own scratch panel (digest `f9fae9dc…`); the published panel is `4ddc3882…`; the FOMC calendar digest is `cddbadfa…`.

**Not run: `gbm_funding_cal_aligned_fomc`.** The one-step guard (#947) refuses it until Eleonora admits it by an allow-list entry per lead. `walk` refuses and writes nothing; `score` lists it under `not_run`. The marked question in PR #1093 stands (default: not run).

## Result

Mean scores, pooled (lower is better):

| model | grid CRPS (23 levels) | upper-tail twCRPS (z > 0 bp) |
|---|---|---|
| gbm_funding | 1.8223 | 0.9515 |
| gbm_funding_cal_direct | 1.8683 | 0.9549 |
| gbm_funding_cal_direct_fomc | 1.8807 | 0.9553 |

Grid-CRPS skill of the arm over its #1027 variant (positive favours the arm; two-sided 90% interval):

| cut | days | skill | interval |
|---|---|---|---|
| all decision days | 1,855 | -0.7% | -1.5% to +0.1% |
| fomc_day | 120 | -1.2% | -3.0% to -0.2% |
| fomc_ordinary | 42 | -4.3% | -12.0% to +0.2% |
| ordinary_non_fomc | 806 | -0.7% | -1.7% to +0.3% |
| regime 2021-23 | 748 | -2.2% | -3.5% to -1.0% |
| regime 2024 | 250 | +0.4% | -0.6% to +1.6% |
| month_end | 150 | -2.0% | -4.3% to -0.3% |

Over `gbm_funding` the arm is -3.2% pooled (-8.8% to +2.1%), -0.7% on calendar days (-6.3% to +4.4%) and -7.8% on ordinary days (-17.3% to +0.8%). By regime it is -30.6% in 2021-23 and +17.9% in 2024, as the #1027 direct variant is; the columns add little to that. Upper-tail twCRPS pooled: -0.0% over the variant (-1.2% to +1.0%), -0.4% over `gbm_funding`. The `fomc_day` and `fomc_ordinary` cuts overlap the five exclusive target-day types.

## Reading (declared rules)

* **Helps on FOMC days over its variant: no.** The lower end of the interval on `fomc_day` is -3.0%, not above 0. The whole interval (-3.0% to -0.2%) lies below 0: on the 120 FOMC days the arm scores worse than the variant it extends, by about 1%.
* **Does not lose on ordinary non-FOMC days: met.** The interval's upper end, +0.3%, is 0 or more.
* **Over `gbm_funding` on calendar days: not shown to beat it** (lower bound -6.3%); it does not lose on ordinary days (upper end +0.8%).

On this development window the FOMC columns do not improve the direct calendar-aware variant, on FOMC days or elsewhere; the point estimates are slightly worse in most cuts (2024, 2025-26 and quarter-end are slightly positive, with intervals that include 0). Lens C's caveat applies: the lag-10 standard error behind the block length is noisy on this many days. Development days give no verdict, and whether the columns join a published declaration is Eleonora's question (#1046), which this page does not decide.

## Environment and what was not checked

The Mac run used `~/rmm-venv` at Python 3.11.17 (the paste stops on any other interpreter), at commit `f9f158d9`. The numpy and scikit-learn versions were printed to `~/1087.log` on the Mac, which was not committed, so they are **not recorded** here. Not checked: that `score.json` reproduces in the cloud (it needs #1027's `PUB.csv`, `AUG3.csv` and walks, which live on the Mac); the aligned arm; why the scratch panel digest differs from the one the cloud rebuild gave (noted in the PR body). Several upper-tail cells are undefined (for example the `tax_date` cut over `gbm_funding`); they are shown as such in `report.md`.
