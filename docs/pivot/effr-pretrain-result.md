# Pre-training on 2008–2018 EFFR − IOER, fine-tuned on the SOFR era (#544, of #374)

A scratch measurement under the pressure-day judge. It writes nothing into `docs/runs/`, moves no published figure, and reads no day
after 2025-12-31 (`docs/decisions/lockbox.md`; the script refuses a later window). No rule, threshold, onset definition, cut-off rule or
availability time changes. Declared before any score in `metadata/effr_pretrain.json` (committed before the first fit) and, for the judge,
in `metadata/pressure_judge/candidates/` (`effr_*.json` and `risk_gbm+effr_*.json`); `scripts/effr_pretrain.py` refuses an uncommitted
declaration. The pre-2018 rows are training data only and are never scored.

**Only the pattern transfers.** Fed funds is the unsecured market and SOFR is secured Treasury repo; fed funds traded below IOER
throughout 2008-12-16 to 2018-04-02, so the source has no +5 bp event at all.

## What was declared

* **Design.** A ridge logistic of `spread > tau` (`ml.PRESSURE_LOGISTIC_SETTINGS`), one per threshold, every day, on the inputs the source
  has: the latest spread, the calendar, reserves and the weekly TGA change (pressure model v1's design without the Treasury settlement,
  which the history does not carry; nothing built after 2018 is read). Each source label is paired with what was public at its own decision
  instant, under the as-of rule and its independent check; a source label not public before a fit's last training day raises `LookAheadError`.
* **Source labels.** EFFR − IOER above a whole-basis-point threshold matched to the SOFR-era event rate: **−7 bp for the +5 bp event and
  −5 bp for the +10 bp event** (the share of source rows above it is the closest to the share of published-panel days before 2026-01-01 above
  +5 and +10 bp; `derive_source_thresholds`, re-derived by every run). Using the 2018 days alone gives the same two numbers.
* **(a) `effr_pooled`.** One fit on the SOFR pairs (weight 1) and the source pairs (weight 0.25, stated, not tuned) with a source indicator;
  columns standardised on the SOFR pairs.
* **(b) `effr_pretrain_finetune`.** A fit on the source alone; then the walk-forward SOFR-era refit with its L2 penalty centred on the
  pre-trained slopes (same `C` = 1, free intercept). A refit whose SOFR window holds no event is served the pre-trained model.
* **Control.** `effr_sofr_only`: the same design and estimator on the SOFR-era pairs alone.
* **Combined rows.** `risk_gbm+effr_*`: the rule of #506 — on a risk date the passer's forecast, on any other day the model's. The hurdle
  of #539 had not merged, so its code is not used; all three (control and both variants) are combined, so no row is chosen on a score.

Scored as the judge declares: tiers 1, 3 and 5, h = 1 to 5, +5 and +10 bp, flat and weighted rule, the cut-off rule unchanged. Paired against
the control (or the passer), `risk_gbm`, calendar climatology and persistence-logistic, 90% stationary-bootstrap intervals.

## Reproduce

Published panel `4ddc3882…` (`verify-panel` clean).

```
PYTHONPATH=src python3 scripts/effr_pretrain.py declare --panel PUBLISHED.csv        # already committed; shown for the record
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --output OUT/bench_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/risk_date_severity.py run --panel AUG2.csv --published PUBLISHED.csv --horizon $h --candidate risk_gbm --output OUT/risk_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/effr_pretrain.py run --panel PUBLISHED.csv --horizon $h --output OUT/effr_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/effr_pretrain.py combine --panel PUBLISHED.csv --risk OUT/risk_h$h.json --transfer OUT/effr_h$h.json --output OUT/comb_h$h.json
for r in weighted unweighted: PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --rule $r --output OUT/judge_$r.json --markdown OUT/judge_$r.md OUT/bench_h?.json OUT/risk_h?.json OUT/effr_h?.json OUT/comb_h?.json
for r in weighted unweighted: PYTHONPATH=src python3 scripts/pressure_judge.py table OUT/judge_$r.json --output OUT/tables_$r.md
PYTHONPATH=src python3 scripts/effr_pretrain.py compare --panel PUBLISHED.csv --output OUT/compare.json --markdown OUT/compare.md OUT/bench_h?.json OUT/risk_h?.json OUT/effr_h?.json OUT/comb_h?.json
```

(`AUG2.csv` as for #428: `pressure_v1_1.py panel`, then `measurement_fields.py panel`.) Set `OMP_NUM_THREADS=1`. Evidence:
`docs/pivot/evidence/effr-pretrain/` (`compare.md` and `compare.json`: recall by year, regime and day type, flags on and off the risk dates, Brier
score and log loss paired, the 26 episodes, the coefficients; `tables-*` and `judge-*` the judge's tables and full reports).

## Result: pre-training does not help, and no model passes

Table 1. The judge's row at +5 bp (90% intervals). "Worst false alarms per onset" is the highest of the five horizons; the limit is 2.

| model | onsets flagged, flat / weighted | recall, flat [90%] | worst false alarms per onset, flat / weighted | tiers 1 / 3 / 5, flat |
|---|---|---|---|---|
| risk_gbm (passer) | 13/26 / 13/26 | 0.500 [0.310, 0.667] | 1.35 / 1.38 | yes / no / no |
| effr_sofr_only (control) | 7/26 / 9/26 | 0.269 [0.128, 0.429] | 1.96 / 3.31 | no / no / no |
| effr_pooled | 5/26 / 11/26 | 0.192 [0.062, 0.333] | 1.50 / 4.15 | no / no / no |
| effr_pretrain_finetune | 7/26 / 11/26 | 0.269 [0.129, 0.433] | 1.96 / 4.19 | no / no / no |
| risk_gbm+effr_sofr_only | 11/26 / 13/26 | 0.423 [0.240, 0.619] | 2.27 / 4.35 | no / no / no |
| risk_gbm+effr_pooled | 11/26 / 13/26 | 0.423 [0.250, 0.618] | 2.08 / 3.96 | no / no / no |
| risk_gbm+effr_pretrain_finetune | 11/26 / 15/26 | 0.423 [0.238, 0.607] | 2.12 / 3.92 | no / no / no |

Tier 3 and tier 5 fail for every row, the passer included (tier 5: not calibrated at the week-ahead; `tables-*.md`, Table 1). Under the weighted
rule the standalone models flag 9 to 11 of 26 onsets and the combined rows 13 to 15, at 3.3 to 4.4 weighted false alarms per onset, against a
limit of 2; the passer's 13 of 26 comes at 1.38.

* **Recall in 2018 and in 2020: no change.** The 2018 onsets (4) and the 2020 onsets (2), and the 2024 onsets (2), are warned by **no** model, the
  passer, the control and both variants alike (`compare.md`, Table 1: 0 of 4, 0 of 2, 0 of 2 in every column). The difference against the control is exactly 0 in
  those cells. Pre-training does not warn a 2018 onset, though the first 2018 fits are the case it was meant for: the judge's cut-off rule never
  flags while its training window holds no onset, and the pre-trained forecasts do not change that rule.
* **Pooled loses recall; fine-tuning matches the control.** All onsets at some lead: control 7/26, pooled 5/26 (difference −0.077 [−0.177, 0.000]),
  fine-tuned 7/26 (0.000). Under the combined rule all three are 11/26, identical recall difference 0.000.
* **Calibration: no measurable gain over the control.** Brier score against the control (positive favours the variant): pooled +0.0009 to +0.0019 and
  fine-tuned −0.0011 to +0.0018 across h = 1 to 5, every 90% interval includes zero (`compare.md`, Table 3). Log loss: pooled −0.0104 to +0.0079 and
  fine-tuned −0.0062 to +0.0044, every interval includes zero. Against calendar climatology the control and both variants are better on Brier at
  every horizon (+0.0090 to +0.0179, intervals above zero); against persistence-logistic indistinguishable. Against `risk_gbm` the variants are better on
  Brier at h = 2 and h = 5 (+0.0099 to +0.0112, intervals above zero) and on log loss at every horizon (+0.46 to +0.59), because the passer forecasts
  exactly 0 off its risk dates (probabilities clipped at 1e-6 for the log loss): arithmetic, as for #506.
* **The combined rows.** Putting any of the three under `risk_gbm` as its every-day component does not raise recall: 11 of 26 against the passer's 13 under
  the flat rule (difference −0.077 [−0.211, +0.056]), 13 to 15 against 13 under the weighted rule. It raises false alarms per onset to 2.1 to 2.3
  (flat), over the limit of 2, against the passer's 1.35. The variants' recall difference from the control combined row is 0.000 in every cell, and
  their Brier and log-loss differences are within noise except `risk_gbm+effr_pretrain_finetune` at h = 5 on log loss (+0.0054 [+0.0006, +0.0105]).
  This is #506's finding again: the every-day component's flags cost more false alarms than the onsets they find, pre-trained or not.
* **How the pre-trained coefficients differ from the SOFR-era fit** (`compare.md`, Table 5; SOFR window's standardised units, 90 refits at +5 bp, h = 1).
  The mean absolute gap in the non-intercept slopes is 1.37 between the pre-trained and the SOFR-era fit, and 0.45 between the fine-tuned and the
  SOFR-era fit: the prior pulls the fit most of the way back. The largest gap is the spread's own state: pre-trained +8.1 at the last refit against
  +1.4 SOFR-era (+1.7 fine-tuned) — in the source the previous day's spread is a much stronger predictor of pressure than in the SOFR era — and
  reserves (−1.6 against −0.9). The calendar slopes agree in sign (month-end, tax date positive; the scarcity interactions negative). The intercepts
  differ (−3.0 against −3.9 at the last refit); the first refits' pre-trained intercept (+0.67) is a base rate far above the SOFR window's.
* **Why it does not move recall.** The source's 2009 events are concentrated in a short period at low reserves; the fitted spread slope is
  large there and does not describe a SOFR-era onset, which the judge asks to be flagged at an ordinary-day cut-off that the training window sets.
  This reading is a hypothesis, not tested here.

## What was not checked

* The source weight (0.25) and the prior strength (`C` = 1) are stated, not tuned; other values were not scored. The source thresholds are
  rate-matched to the pre-2026 published panel (a rate, not a model choice); a different matching rule was not scored.
* The GBM form was not declared, so was not run. The settlement columns and the post-2018 inputs are left out of both markets' design.
* Source labels at a threshold other than the rate-matched one, other down-weights, and a 2008-2018 source with the period before 2012 dropped.
* The hurdle of #539 as the combining rule (not merged). The combined rows use #506's rule.
* No day on or after 2026-01-01 was scored.
