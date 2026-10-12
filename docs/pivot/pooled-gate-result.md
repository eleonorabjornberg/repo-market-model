# The best row's pooled false alarms: where they come from, and three gates on its every-day part (#595)

A scratch measurement under the pressure-day judge. It writes nothing into `docs/runs/`, publishes nothing, moves no published figure, scores no day of 2026 and reads
no day after 2025-12-31 (`docs/decisions/lockbox.md`; the script refuses a later last day). No rule, threshold, onset definition or availability time changes. The
three variants were declared in `metadata/pooled_gate_595.json` and their candidate files, committed (4b5b3ac) before the first variant was fitted; one correction to
variant (c) was committed before any (c) score (the design refuses to run without `spread_bps`, so (c) keeps it; the run had stopped on that error and produced no score).
`scripts/pooled_gate_595.py` refuses an uncommitted declaration.

**The variants were built after seeing 2018-2025 (the diagnosis below reads the onsets they target), so a pass here would not be a confirmation (ruling of 11 October 2026
on #567). A variant can replace a shortlist slot only by Eleonora's decision, before the 2026 window opens. None passes. Nothing here joins a published declaration.**

**Re-run on main at 0adb032.** The whole pipeline was re-run on the tree after the merge of the own-leg scarcity reading (#586) and the state recalibration (#589), with the declaration and the candidate files unchanged. Every figure on this page is the same: the forecasts of the rows, the onsets flagged and lost, the pooled false alarms, the paired comparisons and the diagnosis reproduce byte for byte. What moved is only the judge's tier 3 detail that reads the scarcity state (`evidence/pooled-gate/judge-*.md`: the days in each state and the flags per 252 days by state), and the declaration digest that report prints. No tier verdict changed.

## Result in one paragraph

None of the three variants passes tier 1 under the judge in force. The best, (a) `+leadgate`, brings the pooled weighted false alarms per onset from 3.46 to 2.69
(limit 2) and keeps 18 of the row's 19 onsets; (b) and (c) stay near 3.3. The excess is the every-day part: it raises 131 of the row's 184 pooled false-alarm days (55.0 of 90.0
weighted), for five added onsets. The risk-date part alone (`risk_gbm+settle+h41`) is at 1.44. A rule that conditions a nearer lead on farther leads cannot remove lead-5 flags,
and lead 5 alone is already at 1.64 weighted per onset: the pooled count has a floor above the other leads' reductions.

## Step 1: where the pooled false alarms come from

The row `risk_gbm+every_day+gate+settle+h41+iorb` (PR #582) warns 19 of 26 onsets at leads 1 to 5 and has 184 pooled false-alarm days: 3.46 weighted per onset, 7.08 flat
(`evidence/pooled-gate/diag-weighted.md`; the 19 of 26 and the 3.46 reproduce #591 and #594). A day counts once however many leads flag it.

| source of the flag | false-alarm days | weighted | per onset (26) |
|---|---|---|---|
| a risk date (every lead that flags it) | 53 | 35.0 | 1.35 |
| the every-day part (every lead that flags it) | 131 | 55.0 | 2.12 |
| both parts, at different leads | 0 | 0 | 0 |
| IORB-announcement days (included in the every-day line) | 5 | 3.25 | 0.13 |

| year | 2018 | 2019 | 2020 | 2021 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| false-alarm days | 2 | 90 | 26 | 2 | 1 | 13 | 50 |
| weighted | 2.0 | 32.25 | 20.5 | 2.0 | 1.0 | 9.5 | 22.75 |

| leads that flag the day | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| false-alarm days | 78 | 30 | 18 | 31 | 27 |

Each lead alone raises 85 to 96 false-alarm flags (36 to 43 weighted, 1.4 to 1.6 per onset), which is why the worst single lead was 1.64. The union is 184 days because 78 days
are flagged at one lead only (28 at lead 1, 8 at lead 2, 12 at lead 3, 12 at lead 4, 18 at lead 5). Of the every-day part's 131 days, 57 are flagged at one lead.

**The every-day part drives the excess.** It adds five onsets (2019-05-28, 2019-06-25, 2019-08-13, 2020-03-04 and 2020-03-12; the 2020-03-04 one through the IORB term, at lead 1 only)
for 131 false-alarm days, 2019 (68), 2025 (43), 2024 (12) and 2020 (8). The IORB term adds 5 false-alarm days (3.25 weighted) and the onset of 2020-03-04. The onsets the part adds
and its false alarms look alike on the level inputs: in 2019 both sit at a SOFR 99th percentile 14 to 21 bp above IORB (the median day is 5), the median false-alarm day at 16.

## Step 2: the three variants

All three act on the every-day part only; the risk-date model, the timing arm and the judge are the row's.

* **(a) `+leadgate`**, one gate across leads. Read literally, the text has a day's lead-2-to-5 forecast read the day's lead-1 forecast; that forecast is issued one panel day before
  the day, after the decision instant of every farther lead, and `docs/decisions/information-set.md` forbids reading it. It is run in the form no forecast contradicts: on a day that
  is not a risk date, the forecast at lead h is kept only if the gate was also cleared at every farther lead h' > h. **Marked question for Eleonora below.**
* **(b) `+gate95`**, a stricter gate: the quantile 0.95 in place of 0.9 (one value, the next round number, declared, not chosen on a score).
* **(c) `+tail`**, the every-day part on the signal the diagnosis names: `spread_bps` (a direct pressure model always reads it) and `sofr_p99_iorb_bps`, with `iorb_announced_change_bps` at
  h = 1 (zero on every day but an announced-change day, so its term acts on those days only); it drops `sofr_p75_iorb_bps`.

Harness check: the refit with the row's component and the gate at 0.9 reproduces the row's forecasts at every lead exactly (`gate_hH.json` against `iorb_hH.json`, difference 0).

Table 1. The judge's tier 1 (leads 1 to 5, and leads 3 to 5), tier 3 and tier 5, flat rule and the weighted rule in force; 90% intervals; the limit on false alarms per onset is 2,
read on the pooled count. Full tables, split by regime and day type, are in `evidence/pooled-gate/judge-*.md` and `compare-*`.

| row | rule | tier 1, leads 1 to 5: onsets flagged, recall [90%], pooled false alarms per onset (limit 2) | tier 1 | tier 1, leads 3 to 5: onsets flagged, recall [90%], pooled false alarms per onset | tier 3 | tier 5 | passes |
|---|---|---|---|---|---|---|---|
| risk_gbm+settle+h41 | flat | 14 of 26, 0.538 [0.353, 0.710], 2.00 | yes | 11 of 26, 0.423 [0.250, 0.607], 1.58 | no | no | no |
| risk_gbm+settle+h41 | weighted | 14 of 26, 0.538 [0.353, 0.710], 1.44 | yes | 11 of 26, 0.423 [0.250, 0.607], 1.23 | no | no | no |
| risk_gbm+every_day+gate+settle+h41 | flat | 15 of 26, 0.577 [0.417, 0.741], 4.31 | no | 12 of 26, 0.462 [0.286, 0.650], 3.46 | no | no | no |
| risk_gbm+every_day+gate+settle+h41 | weighted | 18 of 26, 0.692 [0.524, 0.857], 3.39 | no | 15 of 26, 0.577 [0.393, 0.767], 2.62 | no | no | no |
| risk_gbm+every_day+gate+settle+h41+iorb | flat | 16 of 26, 0.615 [0.440, 0.786], 4.35 | no | 12 of 26, 0.462 [0.280, 0.652], 3.46 | no | no | no |
| risk_gbm+every_day+gate+settle+h41+iorb | weighted | 19 of 26, 0.731 [0.560, 0.889], 3.46 | no | 15 of 26, 0.577 [0.385, 0.762], 2.62 | no | no | no |
| risk_gbm+every_day+gate+settle+h41+iorb+leadgate | flat | 15 of 26, 0.577 [0.409, 0.739], 3.88 | no | 12 of 26, 0.462 [0.267, 0.636], 3.38 | no | no | no |
| risk_gbm+every_day+gate+settle+h41+iorb+leadgate | weighted | 18 of 26, 0.692 [0.524, 0.853], 2.69 | no | 15 of 26, 0.577 [0.391, 0.759], 2.49 | no | no | no |
| risk_gbm+every_day+gate+settle+h41+iorb+gate95 | flat | 15 of 26, 0.577 [0.400, 0.739], 4.35 | no | 11 of 26, 0.423 [0.250, 0.607], 3.23 | no | no | no |
| risk_gbm+every_day+gate+settle+h41+iorb+gate95 | weighted | 16 of 26, 0.615 [0.433, 0.778], 3.27 | no | 12 of 26, 0.462 [0.273, 0.652], 2.28 | no | no | no |
| risk_gbm+every_day+gate+settle+h41+iorb+tail | flat | 17 of 26, 0.654 [0.474, 0.818], 4.12 | no | 13 of 26, 0.500 [0.318, 0.680], 3.31 | no | no | no |
| risk_gbm+every_day+gate+settle+h41+iorb+tail | weighted | 19 of 26, 0.731 [0.556, 0.889], 3.25 | no | 15 of 26, 0.577 [0.393, 0.750], 2.50 | no | no | no |

`risk_gbm+settle+h41` passes tier 1 (14 of 26, 1.44 weighted, 2.00 flat); every row with an every-day part fails it, the variants included. Tiers 3 and 5 fail for every row, as before.

Table 2. Onsets flagged at some lead, paired against the row (weighted rule; the flat rule is `compare-row-unweighted.md`), recall difference with a 90% stationary-bootstrap interval.

| variant | flagged | recall difference vs the row | pooled weighted false alarms per onset | lost against the row | gained |
|---|---|---|---|---|---|
| `+leadgate` | 18 of 26 | -0.038 [-0.111, 0.000] | 2.69 | 2020-03-04 | none |
| `+gate95` | 16 of 26 | -0.115 [-0.231, -0.029] | 3.27 | 2019-05-28, 2019-08-13, 2020-03-12 | none |
| `+tail` | 19 of 26 | 0.000 [0.000, 0.000] | 3.25 | none | none |

Against `risk_gbm+settle+h41` (14 of 26): `+leadgate` +0.154 [+0.042, +0.286], `+gate95` +0.077 [0.000, +0.167], `+tail` +0.192 [+0.059, +0.348] (`compare-settle-weighted.md`). Every onset by date and lead,
for the row, the variants and `risk_gbm+settle+h41`, is in `evidence/pooled-gate/onsets-weighted.md`. By regime: the 2018-19 and 2020 cells carry every change; 2024 (two onsets) and 2025-26 are unchanged
for all three variants. By day type: the change is in ordinary days (`+gate95`: 9 to 6 of 12).

Table 3. The pooled false alarms of each row, by source (weighted rule; `evidence/pooled-gate/diag-*.md`). The risk-date part moves a little between rows because the judge chooses each row's flag cut-offs on the row's own forecasts.

| row | onsets flagged | pooled false-alarm days | weighted | risk-date part | every-day part | per onset |
|---|---|---|---|---|---|---|
| `risk_gbm+settle+h41` | 14 | 56 | 37.5 | 37.5 | none | 1.44 |
| the row | 19 | 184 | 90.0 | 35.0 | 55.0 | 3.46 |
| `+leadgate` | 18 | 134 | 70.0 | 36.5 | 33.5 | 2.69 |
| `+gate95` | 16 | 165 | 85.0 | 34.5 | 50.5 | 3.27 |
| `+tail` | 19 | 177 | 84.5 | 34.5 | 50.0 | 3.25 |

Table 4. False alarms at each lead alone, +5 bp, flat count (flags that are false alarms; per onset). The pooled count cannot fall below the worst lead's.

| row | h = 1 | h = 2 | h = 3 | h = 4 | h = 5 |
|---|---|---|---|---|---|
| the row | 96 (3.56) | 85 (3.27) | 89 (3.42) | 90 (3.46) | 91 (3.50) |
| `+leadgate` | 58 (2.15) | 59 (2.27) | 78 (3.00) | 86 (3.31) | 91 (3.50) |
| `+gate95` | 78 (2.89) | 65 (2.50) | 70 (2.69) | 67 (2.58) | 66 (2.54) |
| `+tail` | 93 (3.44) | 85 (3.27) | 80 (3.08) | 91 (3.50) | 89 (3.42) |

## Reading

* A gate that reads only farther leads leaves lead 5 as it is. Lead 5 alone raises 91 flat false alarms (3.50 per onset flat, 1.64 weighted), so `+leadgate` cannot reach 2 pooled however
  consistent it makes the nearer leads: the weighted budget is 52 (2 x 26) and the risk-date part already uses 36.5 of it, leaving 15.5 for the every-day part, which `+leadgate` still spends at 33.5.
* Raising the gate to 0.95 removes 19 of the row's pooled false-alarm days (3.46 to 3.27 weighted) and loses three of the five added onsets: the added onsets are not stronger than the false alarms in the component's own ranking.
* Restricting the inputs to the tail signal moves almost nothing (19 of 26, 3.25): the false-alarm days and the added onsets share one signature, so no level rule separates them in this history.
* Fitting the every-day part inside the budget would mean cutting its false-alarm days to roughly a third of 131, for a part whose value is five onsets; whether that is worth a slot is her call, not this measurement's.

## Marked questions for Eleonora (not settled in code)

1. **Variant (a) as written reads the nearest lead's forecast at the farther leads.** That is a look-ahead under `docs/decisions/information-set.md`, so it was run in the form in which a lead conditions on farther leads
   only. If a different reading was meant (for example a gate computed on pooled forecasts of all leads, or the judge counting the flag at the nearest lead only), say which and a later directive can run it.
2. Whether any of these rows replaces a shortlist slot (#567): none passes tier 1, so this measurement does not suggest it.

## Not checked

* No day of 2026 is scored. A result on 2018-2025 is not a confirmation.
* No value other than 0.95 for the gate, no input set other than the one declared for (c), and no other reading of (a).
* Other estimators for the every-day part, and a pooled-lead gate, are not tried (at most three variants).

## Commands

Published panel `4ddc3882…` (`verify-panel` clean, unchanged); scratch panel `AUG2` (`pressure_v1_1.py panel`, then `measurement_fields.py panel`). `/opt/rmm-venv` (numpy 2.4.6, scikit-learn 1.9.1),
`OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`. In order: `pressure_judge.py forecasts` at h = 1 to 5; `announcement_dating_rescore.py run --arm both --model risk_gbm` at h = 1 to 5;
`iorb_every_day_579.py run` at h = 1 to 5; `pooled_gate_595.py diagnose`; `pooled_gate_595.py run --variant gate|tail` at h = 1 to 5; `pooled_gate_595.py leadgate`; `pressure_judge.py judge --rule weighted|unweighted`;
`pooled_gate_595.py compare --reference row|settle`, `onsets` and `summary`. The exact arguments are in the docstring of `scripts/pooled_gate_595.py`.
