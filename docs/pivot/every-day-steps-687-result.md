# Why the fitted ordinary-day models rank worse than their own main input (#687)

**Status: a measurement, not a record.** Exploration on development data (scoring protocol v1, #640): nothing here is a verdict for any hypothesis, nothing is published, no day after 2025-12-31 is read (`docs/decisions/lockbox.md`), and no new +5 bp classification variant is proposed (paused).

**Hypothesis and step:** H2 (the data we hold carries signal for ordinary-day pressure) and H5, the diagnosis of avenue #674. The declaration is `metadata/every_day_steps_687.json`, committed before any score of a step row. The script is `scripts/every_day_steps_687.py`; the evidence is in `docs/pivot/evidence/every-day-steps/`.

**Population.** The scored days of 2018-06-29 to 2025-12-31 that are not risk dates, at each lead 1 to 5 (about 1,469 days at lead 1, 82 of them pressure days at +5 bp), with the statistics, the walk-forward climatology and the stationary bootstrap (block 10, 2,000 draws, seed 624, 90%) of #624 and #681. The page reproduces #681's figures: every one of the 200 cells of its step-1 evidence for the control row, its cap and the two reference rows is identical.

## What is taken apart

The every-day part of `risk_gbm+every_day+gate+settle+h41+iorb` (#579) is a ridge logistic of a pressure day on the spread, the SOFR 75th and 99th percentile less IORB and, at lead 1, the announced IORB change. Three steps sit on its forecast. `comp` is the logistic with none of them; each subset is applied in the order persist, gate, cap.

* `persist` (#532): the smaller of today's forecast and the previous scored day's.
* `gate` (#532, #595): kept only above the 0.9 quantile of the forecasts of the previous 250 ordinary days.
* `cap` (#601): kept only if the tail spread is at or below the 0.75 quantile of its readings over 250 days.

`comp+gate` is the published control row and `comp+gate+cap` its `+tailcap75`: the script reproduces both cell for cell (`check`). Separately, three day-level rows take #624's `+offday` apart: the four inputs alone, with the as-of scarcity state, and with the inputs times the state.

## Ordinary-day AUROC [90%] by step

| row | lead 1 | lead 3 | lead 5 |
|---|---|---|---|
| raw as-of spread (a level) | 0.941 [0.914, 0.961] | 0.917 [0.881, 0.944] | 0.919 [0.882, 0.946] |
| persistence-logistic | 0.897 [0.841, 0.933] | 0.793 [0.689, 0.865] | 0.809 [0.705, 0.881] |
| `comp` (no step) | 0.905 [0.860, 0.937] | 0.802 [0.709, 0.866] | 0.814 [0.714, 0.884] |
| `comp+persist` | 0.877 [0.817, 0.920] | 0.785 [0.698, 0.851] | 0.802 [0.708, 0.870] |
| `comp+gate` (published control) | 0.736 [0.668, 0.788] | 0.704 [0.601, 0.775] | 0.744 [0.657, 0.807] |
| `comp+cap` | 0.371 [0.292, 0.465] | 0.395 [0.316, 0.491] | 0.392 [0.305, 0.499] |
| `comp+gate+cap` (published cap) | 0.493 [0.473, 0.514] | 0.501 [0.470, 0.533] | 0.528 [0.494, 0.565] |
| `comp+persist+gate+cap` (all three) | 0.504 [0.474, 0.536] | 0.529 [0.492, 0.565] | 0.561 [0.521, 0.607] |
| `day:inputs` | 0.875 [0.778, 0.934] | 0.823 [0.709, 0.897] | 0.823 [0.714, 0.904] |
| `day:inputs+state+interactions` (#624 `+offday`) | 0.887 [0.791, 0.944] | 0.855 [0.746, 0.920] | 0.845 [0.739, 0.912] |

All eleven rows at all five leads, with Brier skill, slope and the reliability intercept, are in `ladder.md`; every row paired with persistence-logistic and with the full construction, pooled and by regime and scarcity state, is in `paired-persistence.md`, `paired-full.md` and the two `steps-vs-*.md` files.

## What each step costs

* **The component alone ranks as well as persistence-logistic.** `comp` less persistence-logistic, all days: AUROC +0.008 [−0.004, +0.027] at lead 1 and between +0.005 and +0.012 at leads 2 to 5, every interval covering 0; Brier skill against the climatology likewise covers 0. It does not reach the raw spread (0.905 against 0.941 at lead 1).
* **The gate costs the ranking.** `comp` to `comp+gate`: AUROC −0.17 at lead 1 (0.905 to 0.736). The gate puts 37 of the 82 ordinary pressure days on a forecast of exactly 0 at lead 1 (34 at lead 5), where the component itself puts none; the other 45 are ranked. Against persistence-logistic the gated row is −0.16 [−0.22, −0.11] in AUROC at lead 1. The gate was added for a tier-1 false-alarm budget of a judge since retired (#640).
* **The tail cap costs the rest, and more.** `comp+gate` to `comp+gate+cap`: 0.736 to 0.493 at lead 1, and the capped rows fall below 0.5 without the gate (`comp+cap` 0.371). A forecast that is kept only when the tail spread is low discards the days on which it is high, and those are the pressure days. 79 of 82 pressure days are on a forecast of 0 at lead 1. The cap's selection is anti-informative.
* **Persist is a small cost in AUROC and a gain in calibration.** `comp+persist` less `comp`: AUROC −0.03 at lead 1 and about −0.02 at leads 3 and 5. Brier skill rises at leads 3 to 5 (0.104 against 0.064 at lead 3, 0.130 against 0.085 at lead 5), and the reliability slope moves toward 1 (1.08 against 0.92 at lead 1). It zeroes 1 pressure day.
* **Leaving one step out of the full construction** (`paired-full.md`, AUROC difference of each row less `comp+persist+gate+cap`, all days, lead 1): without persist (`comp+gate+cap`) −0.011 [−0.035, +0.014]; without gate (`comp+persist+cap`) −0.133 [−0.204, −0.042]; without cap (`comp+persist+gate`) +0.240 [+0.156, +0.304]. Only removing the cap helps.
* **Inputs, state and interactions.** The four inputs alone (no spread) give 0.875 at lead 1, below the raw spread; the state adds 0.01 to 0.03 and the interactions add nothing visible (leads 3 and 5: 0.823, 0.858 to 0.855, 0.852 to 0.845). `day:inputs+state+interactions` less persistence-logistic: AUROC +0.062 [+0.021, +0.111] at lead 3 and +0.036 [+0.007, +0.070] at lead 5 over all days, and no difference inside 2018-19 or 2025-26 (as #681 found).

## Do the 21-day refits lower the pooled AUROC?

No. For every row the AUROC over the pairs inside a refit block (`blocks.md`) is *lower* than the pooled AUROC, not higher: the raw spread, which has no refit, is 0.941 pooled and 0.646 inside blocks at lead 1, and `comp` is 0.905 and 0.659 (within less pooled −0.246 [−0.350, −0.177]). The pooled ranking draws on pairs from different blocks, and those rank well because the level of the spread differs between periods. A level shift between refits would show as a positive difference; only the capped rows have one (`comp+cap` +0.100 [+0.007, +0.202] at lead 1), because they sit near 0.4 to 0.5 either way. The explanation of the gap to the raw spread is not the refit cadence.

## Conclusion

1. The step that costs the ranking is the **tail cap (#601)**, then the **gate (#532, #595)**. The ridge logistic under them ranks the ordinary days as well as persistence-logistic and below the raw spread.
2. An every-day part for #634(c) or #632(b) should **drop the cap and the gate**. It should keep a logistic or a distribution on the as-of spread and the SOFR percentiles; persist is optional (calibration up, ranking down a little). Neither step has a use once the +5 bp tier-1 false-alarm judge is retired.
3. What the day-level inputs add beyond the spread is small and sits at leads 2 to 5 over all days, not inside the two regimes that hold 77 of the 82 pressure days.

These are descriptions of 2018 to 2025 and say nothing about confirmation. Pairing is across five leads and about a dozen rows, so about one interval in ten that has no difference would exclude 0 by chance.

## Not checked, or for Eleonora

* **Reading of "the persist control".** It is not in the published row; it is the #532 control that was not chosen. The page includes it as a step because the directive names it. If "persist" meant something else, say what.
* **The cut-off.** "Pushed below the cut-off" is counted against the raw component's own walk-forward gate cut (`losses.md`, column "below cut"), not against the retired judge's cut-off.
* **Finding:** the gate and the cap name risk dates differently at one day. `every_day_conditioning_601.cap_command` reads the plain panel's settlement columns and the gate the announcement-dated ones; 2019-12-09 at lead 5 differs. The script follows each so as to reproduce the published rows.
* The day-level rows are the logistic form only; the gradient-boosted `+offday_mono` and the rate variant of #624 are not taken apart.
* Calibration rests on 62 and 15 pressure days in 2018-19 and 2025-26; the other regimes have 5 or fewer.

## Reproduction

Panels and forecast files as in "Reproduction" of `docs/pivot/off-risk-day-result.md` (`OMP_NUM_THREADS=1`; panel digest `4ddc3882…`, `verify-panel` passes). Then:

```
PYTHONPATH=src python3 scripts/every_day_steps_687.py declare     # already committed; the declaration is checked equal by the tests
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/every_day_steps_687.py run --panel AUG2.csv --day-panel AUG2R.csv --published PUBLISHED.csv --horizon $h --output OUT/steps_h$h.json
PYTHONPATH=src python3 scripts/every_day_steps_687.py check --input 'OUT/steps_h{h}.json' --iorb 'OUT/iorb_h{h}.json' --cap 'OUT/cap_h{h}.json'
ROWS: --row 'persistence_logistic=OUT/bench_h{h}.json' --row 'spread_bps_asof=asof:spread_bps' and, for each NAME of comp, comp+persist, comp+gate, comp+cap,
      comp+persist+gate, comp+persist+cap, comp+gate+cap, comp+persist+gate+cap, day:inputs, day:inputs+state, day:inputs+state+interactions: --row 'NAME=OUT/steps_h{h}.json'
PYTHONPATH=src python3 scripts/off_risk_day_624.py measure --panel PUBLISHED.csv --scratch AUG2.csv --declaration metadata/every_day_steps_687.json \
    --pair-with persistence_logistic $ROWS --output steps-vs-persistence.json --markdown steps-vs-persistence.md
PYTHONPATH=src python3 scripts/off_risk_day_624.py measure ... --pair-with comp+persist+gate+cap $ROWS --output steps-vs-full.json --markdown steps-vs-full.md
PYTHONPATH=src python3 scripts/every_day_steps_687.py losses --panel PUBLISHED.csv --scratch AUG2.csv --input 'OUT/steps_h{h}.json' --output losses.json
PYTHONPATH=src python3 scripts/every_day_steps_687.py blocks --panel PUBLISHED.csv --scratch AUG2.csv $BLOCKROWS --output blocks.json
PYTHONPATH=src python3 scripts/every_day_steps_687.py report --kind ladder|paired|blocks|losses --input X.json --output X.md
```
