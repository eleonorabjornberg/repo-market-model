# What the two month-end readings do to the ordinary-day headlines (#883)

**Hypothesis and step.** H5 (primary goal), groundwork G1 and step 3 (`docs/research/hypotheses/H5.md`); also read by H6 and H8. **Development data, not a verdict** (scoring protocol v1, #640). Nothing is scored for a verdict, no day after 2025-12-31 is read, no lockbox day is scored (`docs/decisions/lockbox.md`). **This page recommends nothing.** No definition, no caller's default and nothing in `src/repo_model/risk_dates.py` changes, and no earlier page or record is edited.

## The two readings

* **Window** (`SplitDeclaration.day_type`): a day is a month-end when `days_to_month_end` is at most the declared window (2 calendar days). The frozen model and `risk_dates.is_risk_date` without `reporting_on` read it.
* **Reporting** (`SplitDeclaration.reporting_day_type`, `risk_dates.is_risk_date(reporting_on=...)`): a day is a month-end when it is one of the month's last two business days on the market calendar.

Which one is shared is Eleonora's open ruling (#800).

## The days on which they disagree

Every panel day from 2018-04-27 to 2025-12-31 (the file is `evidence/month-end-readings-883/days.json`: date, which reading calls the day a month-end, spread, and whether it is a pressure day, here a spread above +5 bp on whole basis points). There are 70 such days: 31 are month-ends only under the reporting reading (a business day too far from the month's end to be inside two calendar days, for instance a Friday before a Monday month-end), and 39 only under the window (a weekend or holiday lies between the day and the month's end). They split evenly by year (7 to 10 a year). Five fall on a pressure day: 2018-12-28, 2019-06-27 and 2025-11-26 (reporting only), 2025-10-29 and 2025-12-29 (window only). Of the days the headline pages score as targets, H2's fits (#635) flag 58 of 1,873 as differently ordinary under the two readings (1,469 ordinary days under the window, 1,487 under the reporting).

## What was re-run, and the control

Each page's own script was run twice on the same walks and panel, once as it is and once with `SplitDeclaration.reporting_day_type` returning the window reading (`scripts/month_end_readings_883_shim/sitecustomize.py`, switched by `MONTH_END_READING`; nothing in `src/` changes). Every comparison is paired within a reading: the same days for a candidate and its benchmark, with the interval the page uses.

| page | script | the page's own reading | control (under that reading) |
|---|---|---|---|
| #805 (the page of #820) | `h5_splits_805.py score` | reporting | reproduces `evidence/h5-splits-805/score.json` to 1e-9 on every number |
| #761 (the pages of #815) | `spread_mr_variants_761.py score` | reporting | reproduces `evidence/spread-mr-variants/score.json` to 1e-9 |
| #849 (the page of #857) | `risk_date_leadflag_849.py run` | reporting | reproduces `docs/research/evidence/risk-date-leadflag-849.json` to 1e-9 (the script's own control also reproduces #693 and #739) |
| #694 (the pages of #819, #770) | `ranking_694.py score` | reporting | reproduces `evidence/ranking-770/score.json` to 1e-9 |
| #758 (the page of #775) | `h5_step4_758.py score` on H2's rerun fits | window | **does not reproduce byte for byte**, see below |

**#775 does not reproduce exactly.** Its scratch panel cannot be rebuilt to the digest the page recorded (`92bf10a4…`; #811 explains the drift); the fit was rerun on the tree of #775's merge and gives digest `69be91b6…`. The candidates' skills against B1 on the pooled ordinary targets are identical to the page's (grid CRPS +25.7% and +22.4%; upper-tail twCRPS +51.6% and +55.9%), the reachable and ceiling lines differ by 0.002 (grid CRPS +19.4% and +16.6% against +19.6% and +16.8%), inside the declared tolerance of 0.01. The reading comparison below uses this rerun under both readings, so it is internally consistent, but it is not a reproduction of the published figures.

The ordinary flag of #775 comes from H2's fits (`upper_bound_635.py fit`: not a risk date under `risk_dates.NON_ORDINARY`, without `reporting_on`), so it is the window reading. The laws are the same under both readings; only the `ordinary` list is re-read (`month_end_readings_883.py fits`), and its window version equals the fit's own flag on every day.

## Result

All figures are in `evidence/month-end-readings-883/figures.md` (generated, with the data in `figures.json`); the full outputs of every run are beside it. The reading changes:

* **Pooled figures: not at all, or by about a tenth of a point at most** (#805's pooled rows are identical; #761's pooled skills move by at most 0.11 points). The pooled day sets do not read the month-end part; #761's models do, through their ordinary levels.
* **Ordinary groups: by at most 0.8 points of skill; the interval ends of the widest intervals move by up to 4.5 points.** For example #761's mean reversion on ordinary target days: +28.6% [+17.9%, +59.2%] (1,590 days) under the reporting reading, +28.7% [+18.0%, +59.5%] (1,582 days) under the window; #805's `gbm_funding` on ordinary anchors: +9.0% [+4.6%, +14.9%] (1,599 days) against +8.8% [+4.4%, +14.9%] (1,592 days) in grid CRPS; #775's pooled ordinary headline: +25.9% [+11.7%, +40.1%] against +25.7% [+11.4%, +40.0%] (the page's own reading) for `gbm_funding`. No ordinary-group skill changes sign, and no interval's lower end crosses zero.
* **Month-end groups: by up to 5.5 points** (#805's upper-tail twCRPS of `c_two_part_new` on month-end anchors; #761's upper-tail twCRPS on month-end anchors up to 3.7 points), because the group is a different set of days (150 against 157 decision days, 150 against 158 target days). One sign differs: #761's variant (iii) on month-end target days (+2.2% [-19.6%, +18.4%] against -0.1% [-19.8%, +15.6%]), where both intervals contain zero.
* **H6's risk-date set (#849): 17 more risk-type cells under the window at lead 1, 7 or 8 more at leads 2 to 5, and 400 against 382 scored decision days.** The first candidate's grid CRPS skill against B1 is +2.2% [-1.4%, +5.7%] under the reporting and +1.9% [-2.0%, +5.1%] under the window; the studentized (#739) reading's kill outcome is the same under both (met on the declared reading, not met on the weaker one).
* **H8's calendar ranker (#694):** the calendar ranker's own precision (10.5% at k = 3, 9.4% at k = 5) does not move, because it reads the scheduled risk dates, which exclude month-ends. The probability ranker's gain over the calendar is the same to the interval at both readings (precision@5 -1.6 points either way); its gains over climatology move by up to 0.7 points of precision and 2.3 points of recall (the cause is not isolated here).

## Marked question for Eleonora (#800)

Which reading is the shared definition of a month-end for H2, H5, H6 and H8? The evidence is the tables above: the choice moves the ordinary-day headlines by under a point of skill and the month-end groups by up to 5.5 points; it flips no ordinary-group sign and changes no kill outcome shown here. Nothing was changed on this page's account, and the question is not settled here.

## Not checked

* Only the headlines named in the directive were re-run (#805, #815's mean-reversion pages through #761, #775, #857, and #819's ranker). Other pages that read a day type (for instance the H2 ceiling's own ordinary-day AUROCs, H9's screen, the judge) were not re-run.
* #775 is not a byte reproduction (see above); its control is within tolerance but not equal.
* The H8 calendar ranker's day set was re-run only through `ranking_694.py score`; the page of #819 has other splits (by regime and year) that are in the evidence files but are not in `figures.md`.
* The 70 days are panel days to 2025-12-31; days of 2026 are not read.

## Reproduce

Published panel `4ddc3882…` (`build` of `REPRODUCIBILITY.md`), the walk panel and the twenty-five walks as in the docstring of `scripts/spread_distribution_634.py`, the exceedance files (`spread_distribution_634.py exceedance`), and H2's fits on `DERIV.csv` built by `docs/pivot/evidence/panel-trace-811/chain.sh` from a worktree at the merge of #775. `/opt/rmm-venv`, one thread each.

```
export PYTHONPATH=src:scripts/month_end_readings_883_shim
python3 scripts/month_end_readings_883.py days --published PUB.csv --output days.json
for R in reporting window:
  MONTH_END_READING=$R python3 scripts/spread_mr_variants_761.py score --panel PUB.csv --output 761/score_$R.json --markdown 761/report_$R.md
  MONTH_END_READING=$R python3 scripts/ranking_694.py score --panel PUB.csv --output 694/score_$R.json
  MONTH_END_READING=$R python3 scripts/risk_date_leadflag_849.py run --panel PUB.csv --output 849/result_$R.json
  MONTH_END_READING=$R python3 scripts/h5_splits_805.py score --published PUB.csv --walks OUT --output 805/score_$R.json
python3 scripts/month_end_readings_883.py fits --panel DERIV.csv --fits OUT758/fits.json --reading window --output OUT758/fits_window.json
python3 scripts/month_end_readings_883.py fits --panel DERIV.csv --fits OUT758/fits.json --reading reporting --output OUT758/fits_reporting.json
# in a worktree at 75316016 (#775's merge), for R in window reporting:
python3 scripts/h5_step4_758.py score --published PUB.csv --fits OUT758/fits_$R.json --walks OUT --tolerance 0.01 --output 758/score_$R.json
python3 scripts/month_end_readings_883.py report --results evidence/month-end-readings-883 --days days.json --figures figures.json --markdown figures.md
```
