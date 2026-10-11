# The judge's rows re-scored under the rulings of 10 October 2026 (#536)

A scratch measurement under the pressure-day judge. It changes nothing the judge decides on its own authority: the amended
rules are a **draft decision record for Eleonora to review and merge**
([`judge-rulings-10-october.md`](../decisions/judge-rulings-10-october.md)); until she has merged it the judge's
declaration carries them but they are not in force. Nothing is written into `docs/runs/`, no published figure moves, no
2026 day is read and the confirmation tier is not opened ([`lockbox.md`](../decisions/lockbox.md)). Scored days 2018-06-29 to
2025-12-31, h = 1 to 5, +5 bp primary, 90% stationary-bootstrap intervals, the judge's seed.

The rows and what is reported were declared before any score in
[`metadata/judge_rulings_rescore.json`](../../metadata/judge_rulings_rescore.json): the five risk-date passers, the six
best-recall rows of #461 (among them `ngboost_laplace`), the five `+gate` rows of #534 and the two benchmarks. The rulings
(relayed by the orchestrating session on #509, #510, #514 and in the directive #536):

1. **Tier 1 counts false alarms the way it counts warnings (#509).** A day flagged at any horizon h >= 1 is one false alarm,
   and the limit of 2 per onset is read on that pooled count (weighted while the weighted rule is in force). Tier 1 is also
   reported at each lead alone, where the false alarms are those that horizon raises.
2. **The pass rule does not require a pass outside 2018-19 (#510).** Recall and false alarms inside and outside 2018-19
   are a line of their own, with an interval where the onset count allows one.
3. **Regime scoring.** Tier 3 checks calibration only in regimes with at least 20 pressure days; every table adds the recall
   averaged with equal weight over the regimes that have an onset.
4. **The weighted rule stays as adopted (#514).**

## Result

**Under the weighted rule in force, two rows pass tier 1 pooled: `risk_gbm` (13 of 26 onsets, 1.48 weighted false alarms per
onset) and `risk_gbm_base` (14 of 26, 1.59). Under the flat rule one does, `risk_gbm`, exactly at the limit (2.00).** The
other three risk-date passers fail pooled (weighted 2.55, 2.18 and 2.14; flat 2.42, 2.04 and 2.54), as does every other
row. Before the rulings all five passed.

**Per lead, tier 1 is met at h = 1 alone and almost nowhere else.** Under the weighted rule all five risk-date passers pass at
h = 1 (13 to 15 onsets, 0.80 to 1.74 weighted false alarms per onset), as do `ngboost_laplace` (15 of 26, 1.41) and the
`+gate` rows of `risk_gbm`, `risk_gbm_base` and `risk_quantile_skewt_base`. No row passes at h = 2, 3 or 4. At h = 5 two
`+gate` rows pass (`risk_logistic_base+every_day+gate`, `risk_quantile_skewt_base+every_day+gate`). Under the flat rule
the passers `risk_gbm`, `risk_gbm_base`, `risk_logistic`, `risk_logistic_base` and `risk_quantile_skewt_base` pass at h = 1
alone, and no other row passes at any lead.

**No row passes the full rule under either counting.** The two rows that pass tier 1 pooled fail tier 3 (their calibration
fails in 2018-19 and in 2025-26, the two regimes with 20 or more pressure days) and tier 5. Three rows pass tier 3
(`hierarchical_logistic`, `scarcity_logistic_interactions`, `scarcity_logistic`) and fail tier 1 (3.38, 3.01 and 2.87
weighted false alarms per onset). `settlement_quantile_timing` and the `risk_quantile_skewt_base+every_day+gate` row pass
tier 5 and fail the others.

**Outside 2018-19 no row warns half the onsets at a bearable false-alarm rate.** The two tier 1 passers warn 3 and 4 of 9
outside 2018-19 (recall 0.333 and 0.444, against 0.588 inside), at 3.11 and 3.31 weighted false alarms per onset
(interval [1.48, 7.57] and [1.48, 8.00]). Only `risk_logistic` reaches 6 of 9, at 6.03 false alarms per onset with no
interval. By the pass rule's own wording none of this matters: the ruling is that the pass rule does not require a pass outside
2018-19; the line is there to be read.

**Recall with equal weight per regime** (weighted-rule cut-offs) is below 0.5 for all but three rows: `risk_logistic` (0.522) and
the `+gate` rows of `risk_gbm_base` and `risk_logistic` (0.516). `risk_gbm` is 0.297 and `risk_gbm_base` 0.347. The regimes
with onsets are 2018-19 (17), 2020 (2), 2024 (2) and 2025-26 (5). Of the 2020 onsets the rows that warn one are
`two_part_gbm`, `settlement_quantile_timing`, `persistence_logistic` and the five `+gate` rows (1 of 2 each); of the 2024
onsets only `risk_logistic` warns one. The per-regime counts are in the table below.

**Tier 3 under the 20-day rule.** At h = 1 the regimes with at least 20 pressure days are 2018-19 (102) and 2025-26 (29);
2020 (4), 2021-23 (0) and 2024 (5) are reported and do not decide. The five passers fail tier 3 in both tested regimes, at
every horizon. This page does not re-score tier 3 under the earlier rule; by
[`setup-sensitivity-result.md`](setup-sensitivity-result.md) section 4, `hierarchical_logistic` and
`scarcity_logistic_interactions` failed it only in 2020, so for those two the 20-day threshold is what moves the verdict.

The tables are the weighted rule in force (below) and, for scale, the flat rule's pooled table. The per-lead, inside and
outside, equal-weight and tier 3 tables of the flat rule, and everything as JSON, are in
[`evidence/judge-rulings-rescore/`](evidence/judge-rulings-rescore/).

## Weighted rule in force

Tier 1 at lead of at least 1, pooled: a day flagged at any horizon is one false alarm. The limit reads the weighted count. Then tier 3 (calibration tested only in regimes with at least 20 pressure days), tier 5 and the full rule.

| row | onsets warned | recall [90%] | false alarms per onset, flat | weighted | tier 1 | tier 3 | tier 5 | full rule |
|---|---|---|---|---|---|---|---|---|
| **The five risk-date passers** | | | | | | | | |
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 2.12 | 1.48 | pass | fail | fail | fail |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 2.19 | 1.59 | pass | fail | fail | fail |
| risk_logistic | 16 of 26 | 0.615 [0.435, 0.800] | 3.31 | 2.55 | fail | fail | fail | fail |
| risk_logistic_base | 15 of 26 | 0.577 [0.391, 0.762] | 2.88 | 2.18 | fail | fail | fail | fail |
| risk_quantile_skewt_base | 15 of 26 | 0.577 [0.391, 0.750] | 2.88 | 2.14 | fail | fail | fail | fail |
| **The six best-recall rows (#461)** | | | | | | | | |
| two_part_gbm | 15 of 26 | 0.577 [0.400, 0.762] | 7.31 | 3.74 | fail | fail | fail | fail |
| ngboost_laplace | 17 of 26 | 0.654 [0.467, 0.826] | 5.31 | 2.34 | fail | fail | fail | fail |
| hierarchical_logistic | 15 of 26 | 0.577 [0.400, 0.750] | 7.15 | 3.38 | fail | pass | fail | fail |
| settlement_quantile_timing | 16 of 26 | 0.615 [0.444, 0.778] | 10.00 | 5.59 | fail | fail | pass | fail |
| scarcity_logistic_interactions | 14 of 26 | 0.538 [0.346, 0.731] | 6.54 | 3.01 | fail | pass | fail | fail |
| scarcity_logistic | 13 of 26 | 0.500 [0.320, 0.696] | 6.12 | 2.87 | fail | pass | fail | fail |
| **The `+gate` rows (#534)** | | | | | | | | |
| risk_gbm+every_day+gate | 17 of 26 | 0.654 [0.481, 0.818] | 7.35 | 3.67 | fail | fail | fail | fail |
| risk_gbm_base+every_day+gate | 18 of 26 | 0.692 [0.517, 0.850] | 7.27 | 3.64 | fail | fail | fail | fail |
| risk_logistic+every_day+gate | 18 of 26 | 0.692 [0.520, 0.857] | 8.00 | 4.12 | fail | fail | fail | fail |
| risk_logistic_base+every_day+gate | 17 of 26 | 0.654 [0.476, 0.815] | 8.04 | 4.12 | fail | fail | fail | fail |
| risk_quantile_skewt_base+every_day+gate | 17 of 26 | 0.654 [0.467, 0.824] | 7.69 | 3.90 | fail | fail | pass | fail |
| **The benchmarks** | | | | | | | | |
| calendar_climatology | 12 of 26 | 0.462 [0.286, 0.667] | 6.85 | 3.90 | fail | fail | fail | fail |
| persistence_logistic | 12 of 26 | 0.462 [0.273, 0.650] | 8.46 | 4.09 | fail | fail | fail | fail |

### Tier 1 at each lead alone

Onsets warned by that horizon alone / false alarms per onset that horizon raises (weighted count) and the tier 1 verdict at that lead.

| row | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|
| risk_gbm | 13 / 0.80 pass | 8 / 0.68 fail | 7 / 0.59 fail | 7 / 0.47 fail | 7 / 0.76 fail |
| risk_gbm_base | 14 / 0.97 pass | 8 / 0.64 fail | 7 / 0.91 fail | 7 / 0.66 fail | 7 / 0.76 fail |
| risk_logistic | 14 / 1.74 pass | 7 / 1.28 fail | 8 / 1.34 fail | 10 / 1.71 fail | 9 / 1.58 fail |
| risk_logistic_base | 14 / 1.65 pass | 8 / 1.22 fail | 7 / 1.16 fail | 7 / 1.01 fail | 8 / 1.47 fail |
| risk_quantile_skewt_base | 15 / 1.62 pass | 9 / 1.44 fail | 9 / 1.00 fail | 9 / 0.56 fail | 9 / 0.51 fail |
| two_part_gbm | 9 / 0.78 fail | 7 / 1.69 fail | 12 / 1.74 fail | 6 / 0.90 fail | 8 / 2.55 fail |
| ngboost_laplace | 15 / 1.41 pass | 7 / 1.42 fail | 9 / 1.29 fail | 9 / 1.60 fail | 10 / 1.73 fail |
| hierarchical_logistic | 13 / 2.31 fail | 11 / 1.75 fail | 11 / 1.62 fail | 11 / 2.06 fail | 13 / 2.91 fail |
| settlement_quantile_timing | 13 / 3.12 fail | 11 / 3.13 fail | 11 / 2.99 fail | 11 / 3.32 fail | 12 / 3.41 fail |
| scarcity_logistic_interactions | 14 / 2.39 fail | 11 / 1.75 fail | 11 / 1.62 fail | 11 / 2.04 fail | 11 / 2.09 fail |
| scarcity_logistic | 13 / 2.05 fail | 11 / 1.75 fail | 11 / 1.62 fail | 11 / 2.04 fail | 11 / 2.09 fail |
| risk_gbm+every_day+gate | 13 / 1.62 pass | 9 / 1.63 fail | 8 / 1.58 fail | 9 / 1.48 fail | 11 / 1.61 fail |
| risk_gbm_base+every_day+gate | 13 / 1.57 pass | 9 / 1.56 fail | 8 / 1.60 fail | 9 / 1.61 fail | 10 / 1.62 fail |
| risk_logistic+every_day+gate | 12 / 1.79 fail | 8 / 1.60 fail | 8 / 1.58 fail | 8 / 1.89 fail | 12 / 2.19 fail |
| risk_logistic_base+every_day+gate | 13 / 2.01 fail | 9 / 1.56 fail | 9 / 1.67 fail | 9 / 1.71 fail | 13 / 1.91 pass |
| risk_quantile_skewt_base+every_day+gate | 13 / 1.87 pass | 8 / 1.46 fail | 10 / 1.76 fail | 10 / 1.87 fail | 13 / 2.00 pass |
| calendar_climatology | 12 / 3.75 fail | 10 / 3.17 fail | 10 / 3.21 fail | 10 / 3.25 fail | 10 / 3.29 fail |
| persistence_logistic | 11 / 3.25 fail | 7 / 2.07 fail | 10 / 2.68 fail | 8 / 2.38 fail | 8 / 1.86 fail |

### Inside and outside 2018-19, and the recall with equal weight per regime

Reported, not part of the pass rule. Recall with its 90% interval; false alarms per onset (weighted) with its interval where the onset count allows one.

| row | inside: warned | recall [90%] | false alarms per onset [90%] | outside: warned | recall [90%] | false alarms per onset [90%] | equal-weight recall by regime |
|---|---|---|---|---|---|---|---|
| risk_gbm | 10 of 17 | 0.588 [0.364, 0.800] | 0.62 [0.32, 1.17] | 3 of 9 | 0.333 [0.000, 0.625] | 3.11 [1.48, 7.57] | 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5) |
| risk_gbm_base | 10 of 17 | 0.588 [0.364, 0.818] | 0.68 [0.31, 1.29] | 4 of 9 | 0.444 [0.125, 0.750] | 3.31 [1.48, 8.00] | 0.347 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 4/5) |
| risk_logistic | 10 of 17 | 0.588 [0.360, 0.818] | 0.71 [0.36, 1.34] | 6 of 9 | 0.667 (no interval) | 6.03 (no interval) | 0.522 (2018-19 10/17, 2020 0/2, 2024 1/2, 2025-26 5/5) |
| risk_logistic_base | 10 of 17 | 0.588 [0.375, 0.812] | 0.71 [0.35, 1.35] | 5 of 9 | 0.556 (no interval) | 4.97 (no interval) | 0.397 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 5/5) |
| risk_quantile_skewt_base | 10 of 17 | 0.588 [0.364, 0.810] | 0.53 [0.25, 0.97] | 5 of 9 | 0.556 (no interval) | 5.19 (no interval) | 0.397 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 5/5) |
| two_part_gbm | 12 of 17 | 0.706 [0.483, 0.923] | 3.46 [2.12, 5.38] | 3 of 9 | 0.333 (no interval) | 4.28 (no interval) | 0.401 (2018-19 12/17, 2020 1/2, 2024 0/2, 2025-26 2/5) |
| ngboost_laplace | 12 of 17 | 0.706 [0.500, 0.923] | 3.26 [2.04, 5.32] | 5 of 9 | 0.556 (no interval) | 0.58 (no interval) | 0.426 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 5/5) |
| hierarchical_logistic | 12 of 17 | 0.706 [0.500, 0.909] | 3.88 [2.40, 6.15] | 3 of 9 | 0.333 (no interval) | 2.42 (no interval) | 0.326 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 3/5) |
| settlement_quantile_timing | 14 of 17 | 0.824 [0.632, 1.000] | 3.65 [2.25, 5.73] | 2 of 9 | 0.222 (no interval) | 9.25 (no interval) | 0.381 (2018-19 14/17, 2020 1/2, 2024 0/2, 2025-26 1/5) |
| scarcity_logistic_interactions | 12 of 17 | 0.706 [0.500, 0.923] | 3.72 [2.21, 6.17] | 2 of 9 | 0.222 [0.000, 0.556] | 1.67 [0.58, 4.31] | 0.276 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 2/5) |
| scarcity_logistic | 10 of 17 | 0.588 [0.357, 0.833] | 3.51 [2.02, 5.88] | 3 of 9 | 0.333 (no interval) | 1.64 (no interval) | 0.297 (2018-19 10/17, 2020 0/2, 2024 0/2, 2025-26 3/5) |
| risk_gbm+every_day+gate | 13 of 17 | 0.765 [0.538, 1.000] | 2.13 [1.36, 3.32] | 4 of 9 | 0.444 (no interval) | 6.58 (no interval) | 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5) |
| risk_gbm_base+every_day+gate | 13 of 17 | 0.765 [0.529, 1.000] | 2.19 [1.42, 3.57] | 5 of 9 | 0.556 (no interval) | 6.39 (no interval) | 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5) |
| risk_logistic+every_day+gate | 13 of 17 | 0.765 [0.533, 1.000] | 2.75 [1.81, 4.17] | 5 of 9 | 0.556 (no interval) | 6.69 (no interval) | 0.516 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 4/5) |
| risk_logistic_base+every_day+gate | 13 of 17 | 0.765 [0.545, 1.000] | 2.75 [1.79, 4.25] | 4 of 9 | 0.444 (no interval) | 6.72 (no interval) | 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5) |
| risk_quantile_skewt_base+every_day+gate | 13 of 17 | 0.765 [0.538, 1.000] | 2.50 [1.63, 3.95] | 4 of 9 | 0.444 [0.167, 0.714] | 6.56 [3.89, 15.38] | 0.466 (2018-19 13/17, 2020 1/2, 2024 0/2, 2025-26 3/5) |
| calendar_climatology | 12 of 17 | 0.706 [0.500, 0.923] | 3.32 [2.03, 5.58] | 0 of 9 | 0.000 (no interval) | 5.00 (no interval) | 0.176 (2018-19 12/17, 2020 0/2, 2024 0/2, 2025-26 0/5) |
| persistence_logistic | 11 of 17 | 0.647 [0.400, 0.880] | 3.71 [2.21, 6.08] | 1 of 9 | 0.111 (no interval) | 4.81 (no interval) | 0.287 (2018-19 11/17, 2020 1/2, 2024 0/2, 2025-26 0/5) |

### Tier 3: the regimes tested

Pressure days (+5 bp) in each regime at h = 1; a regime is tested when it has at least 20. "ok" is that the regime's calibration interval covers zero.

| row | tested (pressure days, ok) at h = 1 | reported only (pressure days) | tier 3 at each horizon |
|---|---|---|---|
| risk_gbm | 2018-19 (102, miscalibrated), 2025-26 (29, miscalibrated) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| risk_gbm_base | 2018-19 (102, miscalibrated), 2025-26 (29, miscalibrated) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| risk_logistic | 2018-19 (102, miscalibrated), 2025-26 (29, miscalibrated) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| risk_logistic_base | 2018-19 (102, miscalibrated), 2025-26 (29, miscalibrated) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| risk_quantile_skewt_base | 2018-19 (102, miscalibrated), 2025-26 (29, miscalibrated) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| two_part_gbm | 2018-19 (102, ok), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | pass / fail / fail / fail / fail |
| ngboost_laplace | 2018-19 (102, ok), 2025-26 (29, miscalibrated) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| hierarchical_logistic | 2018-19 (102, ok), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | pass / pass / pass / pass / pass |
| settlement_quantile_timing | 2018-19 (102, miscalibrated), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| scarcity_logistic_interactions | 2018-19 (102, ok), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | pass / pass / pass / pass / pass |
| scarcity_logistic | 2018-19 (102, ok), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | pass / pass / pass / pass / pass |
| risk_gbm+every_day+gate | 2018-19 (102, miscalibrated), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| risk_gbm_base+every_day+gate | 2018-19 (102, miscalibrated), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| risk_logistic+every_day+gate | 2018-19 (102, miscalibrated), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| risk_logistic_base+every_day+gate | 2018-19 (102, miscalibrated), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| risk_quantile_skewt_base+every_day+gate | 2018-19 (102, miscalibrated), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| calendar_climatology | 2018-19 (102, miscalibrated), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |
| persistence_logistic | 2018-19 (102, miscalibrated), 2025-26 (29, ok) | 2020 (4), 2021-23 (0), 2024 (5) | fail / fail / fail / fail / fail |

## Flat rule (for scale)

Tier 1 at lead of at least 1, pooled: a day flagged at any horizon is one false alarm. The limit reads the flat count. Then tier 3 (calibration tested only in regimes with at least 20 pressure days), tier 5 and the full rule.

| row | onsets warned | recall [90%] | false alarms per onset, flat | weighted | tier 1 | tier 3 | tier 5 | full rule |
|---|---|---|---|---|---|---|---|---|
| **The five risk-date passers** | | | | | | | | |
| risk_gbm | 13 of 26 | 0.500 [0.310, 0.667] | 2.00 | 1.37 | pass | fail | fail | fail |
| risk_gbm_base | 14 of 26 | 0.538 [0.360, 0.719] | 2.04 | 1.43 | fail | fail | fail | fail |
| risk_logistic | 14 of 26 | 0.538 [0.350, 0.724] | 2.42 | 1.75 | fail | fail | fail | fail |
| risk_logistic_base | 13 of 26 | 0.500 [0.333, 0.680] | 2.04 | 1.41 | fail | fail | fail | fail |
| risk_quantile_skewt_base | 14 of 26 | 0.538 [0.360, 0.714] | 2.54 | 1.80 | fail | fail | fail | fail |
| **The six best-recall rows (#461)** | | | | | | | | |
| two_part_gbm | 15 of 26 | 0.577 [0.400, 0.762] | 4.12 | 1.73 | fail | fail | fail | fail |
| ngboost_laplace | 15 of 26 | 0.577 [0.400, 0.759] | 4.38 | 1.84 | fail | fail | fail | fail |
| hierarchical_logistic | 15 of 26 | 0.577 [0.400, 0.750] | 5.27 | 2.05 | fail | pass | fail | fail |
| settlement_quantile_timing | 15 of 26 | 0.577 [0.391, 0.750] | 7.04 | 3.38 | fail | fail | pass | fail |
| scarcity_logistic_interactions | 14 of 26 | 0.538 [0.346, 0.731] | 4.92 | 1.90 | fail | pass | fail | fail |
| scarcity_logistic | 13 of 26 | 0.500 [0.320, 0.696] | 4.54 | 1.77 | fail | pass | fail | fail |
| **The `+gate` rows (#534)** | | | | | | | | |
| risk_gbm+every_day+gate | 16 of 26 | 0.615 [0.444, 0.778] | 5.65 | 2.56 | fail | fail | fail | fail |
| risk_gbm_base+every_day+gate | 15 of 26 | 0.577 [0.400, 0.750] | 5.77 | 2.58 | fail | fail | fail | fail |
| risk_logistic+every_day+gate | 14 of 26 | 0.538 [0.370, 0.720] | 5.35 | 2.44 | fail | fail | fail | fail |
| risk_logistic_base+every_day+gate | 14 of 26 | 0.538 [0.368, 0.714] | 4.96 | 2.14 | fail | fail | fail | fail |
| risk_quantile_skewt_base+every_day+gate | 15 of 26 | 0.577 [0.407, 0.741] | 5.00 | 2.22 | fail | fail | pass | fail |
| **The benchmarks** | | | | | | | | |
| calendar_climatology | 10 of 26 | 0.385 [0.208, 0.588] | 5.38 | 2.98 | fail | fail | fail | fail |
| persistence_logistic | 7 of 26 | 0.269 [0.111, 0.444] | 5.73 | 2.23 | fail | fail | fail | fail |

## Cross-check against readings (b) and (e) of #523

Where the new rules coincide with readings (b1) (each horizon alone), (b2) (pooled) and (e) (onsets warned and recall outside 2018-19), the figures reproduce. 546 of 546 compared figures agree to 1e-6 over the 13 rows both pages score, under both rules.

## What this does and does not show

* The rulings take the tier 1 pass of the risk-date passers from five rows to two (weighted) or one (flat), and every row's
  full-rule verdict stays a fail. The verdicts of the rest of the judge are the declared bar's, unchanged.
* The scores are walk-forward on days up to 2025-12-31. Nothing here is a statement about the 2026 days, which this page does
  not read.
* The equal-weight recall line has no interval; the per-regime onset counts are 17, 2, 2 and 5, so a single onset moves a
  regime's recall by 0.06 to 0.5.
* Whether the per-lead readings should become tiers of their own, and whether the equal-weight line needs an interval, are not
  ruled (the record lists both as open).

## Not checked

* Tiers 2 and 4, which the pass rule does not read, are in the full judge output of each row but are not tabulated here.
* The climatology reference of every pooled cell is matched to the pooled flat count of false alarms, with the climatology
  of the first horizon; the subset cells (inside and outside 2018-19) use the whole window's matching, held across resamples.
  Intervals on the subsets resample the whole window and draw few outside onsets, so some are wide or absent.
* The cut-off rule is unchanged and still chooses each horizon's cut-off on that horizon's own false alarms per onset in the
  training window; whether it should aim at the pooled count is not ruled.
* The `+gate` rows are scored on the forecasts of `risk_date_false_alarm_controls.py run`, refitted here; the judge's
  candidate files for them are those of #534, unchanged.

## Reproduce

Published panel `4ddc3882…` (`REPRODUCIBILITY.md`), scratch panels as in
[`judge-readings-result.md`](judge-readings-result.md) and
[`risk-date-false-alarm-controls-result.md`](risk-date-false-alarm-controls-result.md). `/opt/rmm-venv`, with
`OMP_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1` and `MKL_NUM_THREADS=1`. The forecasts are the commands of those two pages,
unchanged, h = 1 to 5 (about two hours in all on four cores); the scoring then takes about fifteen minutes per rule.

```
for h in 1 2 3 4 5:
  PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUB.csv --horizon $h --published --output OUT/bench_h$h.json
  PYTHONPATH=src python3 scripts/risk_date_severity.py run --panel AUG2.csv --published PUB.csv --horizon $h --output OUT/risk_h$h.json
  PYTHONPATH=src python3 scripts/pressure_two_part.py horizon --panel PUB.csv --horizon $h --output OUT/tp_h$h.json
  PYTHONPATH=src python3 scripts/pressure_track_q.py forecasts --panel PUB.csv --horizon $h --output OUT/q_h$h.json --distribution OUT/qdist_h$h.json
  PYTHONPATH=src python3 scripts/hierarchical_logistic.py forecasts --panel AUG.csv --horizon $h --output OUT/hl_h$h.json
  PYTHONPATH=src python3 scripts/settlement_timing.py run --panel AUG2.csv --published PUB.csv --candidate settlement_quantile_timing --horizon $h --output OUT/sqt_h$h.json
  PYTHONPATH=src python3 scripts/scarcity_event_bar.py forecasts --panel AUG.csv --horizon $h --candidate scarcity_logistic_interactions --output OUT/sli_h$h.json
  PYTHONPATH=src python3 scripts/scarcity_event_bar.py forecasts --panel AUG.csv --horizon $h --candidate scarcity_logistic --output OUT/sl_h$h.json
  PYTHONPATH=src python3 scripts/risk_date_false_alarm_controls.py run --panel AUG2.csv --published PUB.csv --horizon $h --output OUT/fa_h$h.json
for rule in weighted unweighted:
  PYTHONPATH=src python3 scripts/judge_rulings_rescore.py score --panel PUB.csv --rule $rule --output OUT/rescore_$rule.json OUT/*_h?.json
PYTHONPATH=src python3 scripts/judge_rulings_rescore.py render --weighted OUT/rescore_weighted.json --unweighted OUT/rescore_unweighted.json \
    --readings docs/pivot/evidence/judge-readings/readings.json --markdown OUT/rescore.md
```
