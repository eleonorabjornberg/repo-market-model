# The weighted miss rule in force: the judge table on main, re-run (#472)

Eleonora adopted the weighted miss rule on #464 on 9 October 2026 (her own comment, `performed_via_github_app` null), as the
tier 1 bar and for the 2026 confirmation tier ([`docs/decisions/weighted-miss.md`](../decisions/weighted-miss.md)). The pull
request that closes #472 puts it in force: `in_force` is true in `metadata/weighted_miss.json`, and the judge's default
(`pressure_judge.py judge --rule declared`) counts the weighted false alarms. `--rule unweighted` still counts every false alarm
as 1. This page is the judge table on `main` re-run under the rule in force, published as a new record beside the scratch
comparison of [`weighted-miss-result.md`](weighted-miss-result.md) (#454), which is not edited. It writes nothing into
`docs/runs/` and moves no published figure. Scored days 2018-06-29 to 2025-12-31, h = 1 to 5, +5 bp primary, 90%
stationary-bootstrap intervals; the weights apply at +5 and +10 bp, and the judge scores both. No comparison scores a locked
day (`docs/decisions/lockbox.md`): the 2026 confirmation tier is not opened by this change, and the judge refuses to force the
weighted rule on it.

**What was scored.** Every candidate declared in `metadata/pressure_judge/candidates/` on `main` whose forecasts a script on
`main` writes: 79 rows, benchmarks and the published baseline included, plus the `vote_2_of_3` row, which has its own judge
(`scripts/vote_2_of_3.py judge`). Each track's forecasts come from that track's own script, unchanged. Three rows that
forecast files carry are not declared on `main` (`gbm_reference`, `ngboost_normal`, `qrf`, from open track #413) and are not
scored. Where more than one track writes the same candidate the copies are identical (the largest difference is 0).

## Result

Table 1. The five rows the directive names as the check, tier 1 (onset warning, lead at least 1) at +5 bp. The "weighted rule"
columns are the rule in force; the figures are identical, cell for cell, to the same rows of Table 1 in
[`weighted-miss-result.md`](weighted-miss-result.md) (the figures of #463).

| candidate | onsets | warned, unweighted rule | warned, weighted rule | FA/onset, unweighted rule (flat / weighted) | FA/onset, weighted rule (flat / weighted) | tier 1, unweighted | tier 1, weighted | tier 3 (unw. / w.) | tier 5 (unw. / w.) |
|---|---|---|---|---|---|---|---|---|---|
| risk_gbm | 26 | 13 | 13 | 1.35 / 0.76 | 1.38 / 0.80 | pass | pass | fail / fail | fail / fail |
| risk_gbm_base | 26 | 14 | 14 | 1.50 / 0.97 | 1.50 / 0.97 | pass | pass | fail / fail | fail / fail |
| risk_logistic | 26 | 14 | 16 | 1.85 / 1.19 | 2.42 / 1.74 | pass | pass | fail / fail | fail / fail |
| risk_logistic_base | 26 | 13 | 15 | 1.77 / 1.16 | 2.31 / 1.65 | pass | pass | fail / fail | fail / fail |
| risk_quantile_skewt_base | 26 | 14 | 15 | 1.88 / 1.25 | 2.31 / 1.62 | pass | pass | fail / fail | fail / fail |

The same rows, split by regime (worst horizon's false alarms, flat / weighted count; 2021-23 had no onset), under the rule in
force:

| candidate | rule | regime | onsets | warned | false alarms (flat / weighted) |
|---|---|---|---|---|---|
| risk_gbm | weighted | 2018-19 | 17 | 10 | 21 / 9.25 |
| risk_gbm | weighted | 2020 | 2 | 0 | 13 / 12.00 |
| risk_gbm | weighted | 2021-23 | 0 | 0 | 2 / 2.00 |
| risk_gbm | weighted | 2024 | 2 | 0 | 1 / 1.00 |
| risk_gbm | weighted | 2025-26 | 5 | 3 | 5 / 2.75 |
| risk_gbm_base | weighted | 2018-19 | 17 | 10 | 21 / 10.00 |
| risk_gbm_base | weighted | 2020 | 2 | 0 | 18 / 17.00 |
| risk_gbm_base | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| risk_gbm_base | weighted | 2024 | 2 | 0 | 0 / 0.00 |
| risk_gbm_base | weighted | 2025-26 | 5 | 4 | 3 / 1.50 |
| risk_logistic | weighted | 2018-19 | 17 | 10 | 25 / 12.00 |
| risk_logistic | weighted | 2020 | 2 | 0 | 30 / 29.00 |
| risk_logistic | weighted | 2021-23 | 0 | 0 | 2 / 2.00 |
| risk_logistic | weighted | 2024 | 2 | 1 | 4 / 3.25 |
| risk_logistic | weighted | 2025-26 | 5 | 5 | 11 / 8.75 |
| risk_logistic_base | weighted | 2018-19 | 17 | 10 | 25 / 12.00 |
| risk_logistic_base | weighted | 2020 | 2 | 0 | 30 / 28.25 |
| risk_logistic_base | weighted | 2021-23 | 0 | 0 | 0 / 0.00 |
| risk_logistic_base | weighted | 2024 | 2 | 0 | 2 / 1.50 |
| risk_logistic_base | weighted | 2025-26 | 5 | 5 | 6 / 3.50 |
| risk_quantile_skewt_base | weighted | 2018-19 | 17 | 10 | 20 / 7.75 |
| risk_quantile_skewt_base | weighted | 2020 | 2 | 0 | 32 / 30.75 |
| risk_quantile_skewt_base | weighted | 2021-23 | 0 | 0 | 2 / 2.00 |
| risk_quantile_skewt_base | weighted | 2024 | 2 | 0 | 1 / 0.25 |
| risk_quantile_skewt_base | weighted | 2025-26 | 5 | 5 | 7 / 3.25 |

The split by pressure-day type, and tiers 3 and 5 by regime, are in [`evidence/weighted-miss-in-force/judge.md`](evidence/weighted-miss-in-force/judge.md);
every candidate's tiers are in [`evidence/weighted-miss-in-force/tables.md`](evidence/weighted-miss-in-force/tables.md) and its
tier 1 under both rules, with the regime split, in [`evidence/weighted-miss-in-force/table.md`](evidence/weighted-miss-in-force/table.md).

## What the table says

* **No candidate passes the pass rule under either rule.** Tier 3 (no crying wolf, with calibration by regime) fails for every
  candidate, as it did in #454, so the weighted count does not by itself let a model pass. Nothing joins the live record, and no
  `confirmation.candidates` entry or other published declaration changes, so there is no publishing question.
* **Tier 1.** Twelve rows pass it under the unweighted rule and fourteen under the rule in force. The five risk-date rows above
  pass under both. Three rows pass under the weighted rule only (`ngboost_laplace`, `rare_gbm_focal+recalibrated`,
  `two_part_logistic`), and `settlement_quantile_timing_cooldown5_strict` passes under the unweighted rule only. The
  `vote_2_of_3` row passes tier 1 under the weighted rule (15 of 26 onsets warned, 1.80 weighted false alarms per onset at the
  worst horizon; 4.27 flat) and not under the unweighted (2.19 flat), and fails the pass rule.
* **Unchanged against #454.** The 64 rows that #454 scored have the same figures in every column of Table 1 here; the 15 rows
  that are new to this table are the alarm cool-down rows (#459), `ngboost_laplace` (track Q) and the two window-onset rows (#460).
  The five rows named above reproduce #463 exactly, so no explanation is owed.
* **Everything still sits in 2018-19.** That regime holds most of the onsets and false alarms; the later regimes have too few
  onsets for a regime split to say much (2020: 2, 2024: 2, 2025-26: 5, 2021-23: none).
* **Not checked.** The 2026 confirmation tier (not opened; opening it is Eleonora's). Other weights, bands or limits (they are
  hers to set). The scarce-regime reading under the weighted rule keeps its distances among that regime's days only.

## Reproduce

Published panel `4ddc3882…` (built from the tracked fixtures; `verify-panel` clean). Tracks that score on a scratch panel
use `pressure_v1_1.py panel`, then `measurement_fields.py panel`, `policy_features.py panel`, `net_settlement.py panel`,
`fed_liquidity.py panel` and `nowcast.py panel` as each track's page says. Each track's forecast files are written by the
command on its own result page (`docs/pivot/*-result.md`) for h = 1 to 5, with `OMP_NUM_THREADS=1` and `/opt/rmm-venv/bin/python`.
A forecast file written on a scratch panel names that panel's digest; give it the published panel's after checking that its
dates are the grid's (the judge refuses a file whose days are not the grid's). The alarm cool-down rows are assembled from the
base rows by `alarm_cooldown.py assemble` as `alarm-cooldown-result.md` states. Then:

```
PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUB.csv --output OUT/judge_inforce.json --markdown OUT/judge.md IN/forecasts_h?.json
PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUB.csv --rule unweighted --output OUT/judge_unweighted.json IN/forecasts_h?.json
PYTHONPATH=src python3 scripts/weighted_miss.py table OUT/judge_unweighted.json OUT/judge_inforce.json --output OUT/table.md
PYTHONPATH=src python3 scripts/pressure_judge.py table OUT/judge_inforce.json --output OUT/tables.md
PYTHONPATH=src python3 scripts/vote_2_of_3.py judge --panel PUB.csv --output OUT/vote.json --markdown OUT/vote.md --overlap OUT/overlap.json OUT/bench_h?.json OUT/tp_h?.json OUT/q_h?.json OUT/hl_h?.json
```

The first command needs no `--rule`: the default is the rule in force. `evidence/weighted-miss-in-force/vote_judge.md` and
`vote_overlap.md` are the vote row's judge report and its overlap table.
