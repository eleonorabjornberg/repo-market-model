# Always-flag reading of tier 1, option B (#685): summary

Re-score of `ngboost_laplace` and the benchmarks under Eleonora's ruling of 13 October 2026 on #666 (option B): a flag from an
always-flag block is not a tier 1 warning, but it still counts as a false alarm. Same panel (`4ddc3882…`), same forecasts, same
judge in force and the same scored days (2018-06-29 to 2025-12-31) as the #588 measurement in `docs/pivot/evidence/always-flag/`,
which is left as it was published. Exploration on development data: it gives no verdict, and the +5 bp judge is retired as a
decision rule (#640). Tables, per-lead figures, the always-flag blocks per row and horizon and the onsets lost are in `result.md`
(weighted rule in force, then the flat count). Declaration: `metadata/always_flag_685.json`. Command: the header of
`scripts/always_flag_685.py`.

Under the weighted rule in force, tier 1 at lead of at least 1, option off → on:

| row | onsets warned | pooled false alarms per onset (limit 2) | tier 1 |
|---|---|---|---|
| `ngboost_laplace` | 17 → 13 of 26 (recall 0.654 → 0.500, interval [0.316, 0.696] on) | 2.34 → 2.34 | fail → fail |
| `calendar_climatology` | 12 → 2 | 3.90 → 3.90 | fail → fail |
| `persistence_logistic` | 12 → 4 | 4.09 → 4.09 | fail → fail |
| `published_v1` | 14 → 8 | 3.06 → 3.06 | fail → fail |

The false alarms no longer move, so `ngboost_laplace` no longer passes (under the #588 draft it did, at 1.81). The figures for
`ngboost_laplace` are the ones #666 reproduced: 13 of 26 onsets, 2.34 false alarms per onset, fail; flags dropped from the warnings
by horizon 63, 63, 84, 105, 105; onsets lost 2019-01-15, 2019-01-31, 2019-06-25 and 2019-10-15.

Not re-scored: `risk_gbm` and the two `risk_gbm` variants of the #588 measurement, whose forecasts need the augmented panel. The #588
table shows the option left their warnings and their tier 1 verdict unchanged, and under option B their false alarms are the
option-off figures by construction, so their tier 1 rows are the option-off rows of that table. That is a reading of the #588 table,
not a new score.
