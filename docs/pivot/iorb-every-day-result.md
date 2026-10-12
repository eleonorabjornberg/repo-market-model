# The announced IORB change in the control row's every-day component (#579, from #560)

A scratch measurement under the pressure-day judge. It writes nothing into `docs/runs/`, publishes nothing, moves no published figure, scores no day of 2026 and reads
no day after 2025-12-31 (`docs/decisions/lockbox.md`; the script refuses a later last day). No rule, threshold, onset definition or availability time changes. The
row was declared in `metadata/iorb_every_day_579.json` and `metadata/pressure_judge/candidates/risk_gbm+every_day+gate+settle+h41+iorb.json`, both committed
(9519463) before the first forecast was fitted; `scripts/iorb_every_day_579.py` refuses an uncommitted declaration.

**The input was picked after #560 found it on these same days (2018-06-29 to 2025-12-31), so a result here is not a confirmation. The row is not in the confirmation
look. The input does not join any published declaration; no figure on any published page moves.**

## What was declared

| part | what |
|---|---|
| parent | the control `risk_gbm+every_day+gate+settle+h41` of PR #563: the risk-date gradient-boosted model on a risk date; on any other day a ridge logistic on `spread_bps`, `sofr_p75_iorb_bps` and `sofr_p99_iorb_bps`, then the gate of #532; settlements dated from the auction announcement and the H.4.1 weeklies read per release (#541) |
| new row | `risk_gbm+every_day+gate+settle+h41+iorb`: the parent with `iorb_announced_change_bps` added to that logistic's inputs, and to nothing else. The risk-date model, the gate, the timing and the estimators are the parent's |
| the input | the IORB change in basis points that takes effect after the previous panel day's decision instant and on or before the scored day, from the notes announced at or before that instant (`repo_model.announced_iorb`, `docs/decisions/fomc-point-in-time.md`) |
| horizons | the input is public one panel day ahead only (`metadata/sources.json`), so it is read at h = 1. At h = 2 to 5 the as-of rule refuses it, as for the `iorb` variant of #540, and the row's forecasts are the parent's, copied. The row differs from its parent at h = 1 alone |

The one code change is `component_inputs` on `ml.pressure_risk_date_variant_exceedance` (default: the component of #506, forecast for forecast).

## Result at +5 bp

Table 1. The judge's tier 1 (leads 1 to 5, and leads 3 to 5), tier 3 and tier 5, under the flat rule and the weighted rule in force. 90% intervals. The limit on false alarms per onset is 2. Full tables, split by regime and pressure-day type, are in `evidence/iorb-every-day/tables-*.md` and `judge-*.md`.

| row | rule | onsets flagged at leads 1 to 5, recall [90%], worst false alarms per onset | tier 1 | leads 3 to 5, flagged, recall [90%] | tier 3 | tier 5 | passes |
|---|---|---|---|---|---|---|---|
| parent | flat | 15 of 26, 0.577 [0.417, 0.741], 2.35 | no | 12 of 26, 0.462 [0.286, 0.650] | no | no | no |
| parent | weighted | 18 of 26, 0.692 [0.524, 0.857], 1.64 | yes | 15 of 26, 0.577 [0.393, 0.767] | no | no | no |
| `+iorb` | flat | 16 of 26, 0.615 [0.440, 0.786], 2.35 | no | 12 of 26, 0.462 [0.280, 0.652] | no | no | no |
| `+iorb` | weighted | 19 of 26, 0.731 [0.560, 0.889], 1.64 | yes | 15 of 26, 0.577 [0.385, 0.762] | no | no | no |

The parent reproduces the earlier pages (18 of 26 weighted at 1.64, [`combined-model-result.md`](combined-model-result.md)). No verdict changes: tier 1 is as before under each rule, and tiers 3 and 5 still fail.

Table 2. Onsets flagged at some lead, paired against the parent (weighted rule; the flat rule is `compare-unweighted.md`). Difference in recall, 90% stationary-bootstrap interval.

| cell | onsets | parent | row | recall difference |
|---|---|---|---|---|
| all | 26 | 18 | 19 | +0.038 [0.000, +0.111] |
| 2018 | 4 | 0 | 0 | 0 |
| 2019 | 13 | 13 | 13 | 0 |
| **2020** | 2 | 1 | 2 | +0.500 (two onsets, no interval) |
| **2024** | 2 | 0 | 0 | 0 |
| 2025 | 5 | 4 | 4 | 0 |
| regime 2018-19 / 2020 / 2024 / 2025-26 | 17 / 2 / 2 / 5 | 13 / 1 / 0 / 4 | 13 / 2 / 0 / 4 | 0 / +0.500 / 0 / 0 |
| day type ordinary / month-end / quarter-end / tax date | 12 / 6 / 3 / 5 | 8 / 4 / 2 / 4 | 9 / 4 / 2 / 4 | +0.083 [0.000, +0.222] / 0 / 0 / 0 |

The whole gain is one onset, **2020-03-04**, flagged at lead 1 with probability 1.0 where the parent gave 0.0: the cut announced on 2020-03-03 (−50 bp) is in the input. 2018 (four onsets, all in the hiking cycle) and 2024 (two onsets) gain nothing.

Table 3. Paired Brier difference against the parent at h = 1, +5 bp (negative favours the row), 90% interval: all days +0.0001 [−0.0014, +0.0017]; regime 2018-19 +0.0022 [−0.0011, +0.0073]; 2020 +0.0041 [0.0000, +0.0111]; 2024 −0.0043 [−0.0113, 0.0000]; 2025-26 −0.0021 [−0.0045, 0.0000]; ordinary days +0.0002 [−0.0017, +0.0020]. Every interval covers or touches zero. At h = 2 to 5 the rows are identical.

## The false alarms the input adds, by announcement day

An announcement day is a scored day on which the input is not 0: 26 of them, 2018 to 2025 (`evidence/iorb-every-day/days-weighted.json`, with the flag and probability of each row on each day, at h = 1 and the judge's cut-offs). Six were pressure days: 2019-05-02, 2019-08-01, 2019-09-19, 2019-10-31, 2020-03-04, 2025-10-30.

| | flags added by the input | of which false alarms | onsets | flags dropped | of which false alarms |
|---|---|---|---|---|---|
| weighted rule | 8 | 5 | 1 (2020-03-04) | 2 | 1 |
| flat rule | 3 | 1 | 1 (2020-03-04) | 0 | 0 |

Under the weighted rule the added flags on announcement days are 2019-08-01 (a pressure day), 2020-03-04 (the onset), and four false alarms: **2024-09-19** (−50 bp), **2024-12-19**, **2025-09-18** and **2025-12-11** (each −25 bp). Two more flags are added on days with no announcement (2019-04-03, a pressure day, and 2019-06-13, a false alarm), and two are dropped (2025-11-12, a pressure day, and 2025-12-10). The parent flagged 3 of the 26 announcement days; the row flags 9. Net at h = 1: 6 more flags, 4 more false alarms, 1 more onset.

Under the flat rule the input adds the same 2019-08-01, 2020-03-04 and 2024-09-19.

## Reading, and what is not claimed

* The input moves a ridge logistic's forecast on a handful of days; the 26 announcement days hold one added onset.
* All four cuts of 2019 (2019-05-02, 08-01, 09-19, 10-31) fell on pressure days, which is consistent with the row having learned "a cut announced is a pressure day" (the coefficient was not inspected). The cuts of 2024 and 2025 (2024-09-19, 12-19, 2025-09-18, 12-11) were not pressure days, and are where the added false alarms sit. Whether 2020-03-04 is the same signal or the 2019 pattern carried over is not settled by 26 days.
* A measurement only. Whether the input joins any declaration is Eleonora's; the directive asks for none, so no "Publish?" issue is opened and no published figure moves.

## What was not checked

* The five construction fixes of #578 (#566, #568, #574, #575, #577) had not merged when this was scored (PR #580 was open). None of the first four is read by this row: its every-day inputs are `spread_bps`, `sofr_p75_iorb_bps`, `sofr_p99_iorb_bps` and the new input, and its passer's features carry no net-settlement, structural, projected-reserves or latent-factor column. #577 changes which false-alarm count the shared judge table prints; Table 1 here is built from the judge's JSON, with the flat and the weighted count each labelled, not from that table's column. The parent reproduces PR #563's figures.
* No 2026 day. No other input, row or horizon. Nothing was tuned: the row was declared once.

## Reproduce

Published panel `4ddc3882…` (`verify-panel` clean, unchanged); scratch panel `AUG2` (`pressure_v1_1.py panel`, then `measurement_fields.py panel`). `/opt/rmm-venv` (numpy 2.4.6, scikit-learn 1.9.1), `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`. The commands are in the docstring of `scripts/iorb_every_day_579.py`; in order: `pressure_judge.py forecasts` at h = 1 to 5, `announcement_dating_rescore.py run --arm both --model risk_gbm` at h = 1 to 5, `iorb_every_day_579.py run`, `pressure_judge.py judge --rule weighted|unweighted` and `table`, `iorb_every_day_579.py compare`, `days` and `summary`.

## Note of 12 October 2026 (#604): the sign of Table 3

The header of Table 3 above says "negative favours the row". That is the wrong way round. The statistic is the judge's
(`pressure_judge._paired_vectors`): the parent's squared error minus the row's, so **positive favours the row**. The figures are unchanged
(`evidence/iorb-every-day/compare-*.md` and `.json` were regenerated by `iorb_every_day_579.py compare` and differ from the earlier files in the
header line only). Read the right way, Table 3 says: the row is slightly better on all days (+0.0001), in 2018-19 (+0.0022) and in 2020
(+0.0041, whose interval touches zero at 0.0000: the 2020-03-04 onset) and worse in 2024 (−0.0043) and in 2025-26 (−0.0021), the intervals of
those two touching zero from below; on ordinary days the difference is +0.0002. The page's verdict, that every interval covers or touches
zero, is unchanged; no other reading on this page used the sign. The state-conditioned recalibration page (#589) already used the right sign.
