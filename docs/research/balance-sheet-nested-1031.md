# The balance-sheet days on the turn days, nested into the calendar-aware candidate (#1031, H5 step 2 / H6 step 1): design

**Development data, not a verdict. Status: design and declaration; the result is on `docs/research/balance-sheet-nested-1031-result.md`.** The walks were long and ran on Eleonora's Mac (`needs-mac`, #46); the tables are `docs/research/balance-sheet-nested-1031/report.md`, the scores `docs/research/balance-sheet-nested-1031/score.json`. The declaration is `metadata/balance_sheet_nested_1031.json`, committed before any number was computed; the script is `scripts/balance_sheet_nested_1031.py` (commands in its docstring); the tests are `tests/test_balance_sheet_nested_1031.py`.

**Questions for Eleonora (not settled here), each with a default.**

1. Adopt the turn relabel for the balance-sheet flags, and so for any published declaration that carries them? The definition is a data meaning (#959, criterion 4). *Default: no. The relabel stays off in every published declaration, and this page reads with and without it.*
2. Should the December turn carry `foreign_bank_quarter_end` as well as `gsib_year_end`? *Default: both, as here, because the quarter-end rule names December among its four quarters; the alternative is `gsib_year_end` alone on the December turn, which would make the quarter flag fire on the March, June and September turns only.*

## Why

Lens A of the five-lens review (#958): the flags of `balance_sheet_days` (#427) sit on run-up days that the published panel shows are cold (the 2nd- and 3rd-last business days of a quarter-end average −4.6 and −3.9 bp), while the hot days are the last business day and the first after it (#959's table). Nested as coded, the flags fail for the wrong reason. #959 relabelled the turn (`repo_model.turn_days`); this directive moves the flags onto it and nests them.

## The arms

Both are #1027's direct-pairs candidate, `gbm_funding_cal_direct` (the published inputs at the lead, the calendar columns at the target day, `treasury_settlement` at lead 1, leaf 5, direct pairs), plus three flag columns and nothing else. The flags are the three rules of `balance_sheet_days`, with their sources and `public_from` gates unchanged.

| rule | as coded (`bs_coded_*`) | on the turn days (`bs_turn_*`) |
|---|---|---|
| `foreign_bank_quarter_end` | the last 3 business days of March, June, September, December | the quarter's last business day and the first business day after it, for the same four months |
| `foreign_bank_month_end` | the last business day of a month that is not a quarter's last | that day and the first business day after it |
| `gsib_year_end` | the last 5 business days of December | the last business day of December and the first business day of January |

The penultimate and run-up days return to ordinary in the second column. 26 December is flagged by no relabelled rule (the coded `gsib_year_end` window held it) and is reported as its own row.

## Calendar first

Each flag is a function of the row's own date and `metadata/market_holidays.json`: scheduled, known in advance, written about the target day. So it is declared in `repo_model.target_day_columns`, which `repo_model.one_step_guard` reads (a one-step fit on any of the six columns raises `ValueError`); `asof` rule 2 serves it from the scored row at every lead h = 1 to 5; and a direct pair trains it from its own target row. `TargetRowTests` shows each of the three on the real `ml.fit_gradient_boosted_quantiles`, and `FlagDatesTests` pins every flag's dates for a whole calendar year by hand, with the holiday rolls (Labor Day, 1 January) and the cases that change between the two sets. Neither arm uses the allow-list of the one-step guard.

## What the result page will report

Paired grid CRPS and upper-tail twCRPS of each arm against the base (`gbm_funding_cal_direct`), B2 as it is, B1 and `gbm_funding` (the H5 candidate in force, Eleonora, 21 October 2026, on #1027), and of the turn arm against the coded arm, on development days to 2025-12-31 only, on the studentized bound (ruling 1, #739) with Lens C's caveat on the lag-10 standard error. Pooled, by regime (2018-19, 2020, 2021-23, 2024, 2025-26), by target day type on the turn labels, and on the groups the directive names: the turn days (which are the relabelled flags' days), the as-coded flag days, the days neither set flags, the penultimate days and 26 December, each with its day count and interval width. A group with fewer than 20 target days is listed and not tested.

The declared reading rule: an arm beats the base on its flagged days when the lower end of its skill interval there is above zero, and loses elsewhere only if its interval on the days neither set flags lies wholly below zero. The relabel's own effect is the turn arm over the coded arm. Nothing here decides adoption.

## Not done here

No walk was run in this session (the base's own walks took hours on the Mac, and a long run is not run in a cloud session). The base and control walks are #1027's and exist only on her Mac. The aligned one-step variant of #1027 is not nested: it runs under an allow-list entry with an end date (`one_step_guard.ONE_STEP_ALLOW_LIST`), and the flags would be a new regressor set for it.
