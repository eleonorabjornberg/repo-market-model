# The OFR not-yet-published flag and the skew-t input scaling (#537, follow-up to #477 and PR #496)

A scratch measurement under the pressure-day judge as it stands on `main`. It writes nothing into `docs/runs/` and moves no published
figure (`docs/decisions/lockbox.md`: scored days 2018-06-29 to 2025-12-31 only; no later day is scored and the confirmation window is
not looked at). It closes the two gaps Eleonora accepted on PR #496 (ruling of 10 October 2026): the OFR series that start in
September 2020 were left out of the dealer-and-segment group, and `risk_quantile_skewt_base_dealer` did not solve at h = 1 and h = 5.
Declared before any score in `metadata/ofr_followup.json` and, for the judge, in the six files
`metadata/pressure_judge/candidates/risk_*_dealer_ofr.json` and `risk_quantile_skewt_base_minmax.json`; `scripts/unused_inputs.py`
refuses an uncommitted declaration, and the judge refuses an uncommitted candidate file. Nothing is named for the confirmation look, and
every input stays off in the published declaration.

## What was declared

* **A "not yet published" flag** (`repo_model.ofr_publication`, off in every published declaration). The OFR began publishing its
  repo-segment series in real time on 2020-09-09; earlier values were filled in after the fact and are not read (#508, #522). Per series
  there are two scratch columns: `<series>_not_yet_published`, 1.0 on a row dated before 2020-09-09 and 0.0 from it, and
  `<series>_filled`, the rate where the panel has it and 0.0 on a flagged row. **The flag is a function of the row's date alone**, never
  of whether a value exists, because the OFR GCF "observed" indicator is not an input (ruling of 10 October 2026 on #520). With the
  flag, a day before September 2020 keeps its place in the fit and in the comparison, so 2018 and 2020 stay in.
* **The tri-party rate enters; the GCF rate does not.** The tri-party rate has one empty row after 2020-09-09 (2022-06-17), which takes
  the row before it, older and never newer (the rule `measurement_fields.carry_one_row_holes` applies to SOFR's percentiles, here
  without looking at the row after). The GCF rate is empty on most days after publication (144 of 1325 scratch-panel rows hold a
  value). Reading it drops those days; filling them makes a value's existence an input, which the ruling on #520 refuses. Its flag and
  filled column are built and tested, and the GCF rate stays out of every candidate. **A fill for the GCF gaps is a design choice that
  is Eleonora's** (below).
* **The OFR look-ahead guard of #522** (`dvp_segment.require_ofr_public`) is called by `scripts/unused_inputs.py panel` and `run`: a
  panel holding an OFR value dated before 2020-09-09 raises `LookAheadError`. Both new column pairs draw on the OFR source's own
  fields, so the as-of rule reads them at that source's release lag (two business days after the reference date).
* **Five candidates**, each of the five tier-1 passers of #428 with the dealer-and-segment group of #477 plus `tri_rate_filled` and
  `tri_rate_not_yet_published` at every horizon (`risk_gbm_dealer_ofr`, `risk_gbm_base_dealer_ofr`, `risk_logistic_dealer_ofr`,
  `risk_logistic_base_dealer_ofr`, `risk_quantile_skewt_base_dealer_ofr`). Each passer is re-scored on the same scratch panel and fold
  grid as its control.
* **The input scaling** for the skew-t form: each column rescaled to [0, 1] on the fit's training pairs, then the linear programs
  (`ml.pressure_risk_date_exceedance(..., input_scaling="minmax")`). A linear quantile regression with an intercept is equivariant to
  the change, so the model is the same; only the solver's conditioning changes. It was chosen by whether the median's program returns a
  solution on the one design of #496 that failed (it did under every rescaling tried), not by any score. It applies to
  `risk_quantile_skewt_base_dealer_ofr` and to `risk_quantile_skewt_base_minmax`, the passer refitted with the same scaling so that the
  group's effect and the scaling's can be told apart. The other four passers and candidates keep the standardizer.
* **An amendment, before any score was read.** The first scoring pass refused a served day at h = 4 (2022-06-21) on the empty row of
  2022-06-17, which the first draft of the declaration left unfilled. The pass was stopped, its scores were not read, the one-row hole
  was declared carried (`metadata/ofr_followup.json`, `amendment`), and all five horizons were re-run from the start.

## Result: the scaling solves the fit, the flag keeps 2018 and 2020, and no candidate passes

The skew-t candidate now solves at every horizon, h = 1 and h = 5 included. No candidate passes the full pass rule: every one fails
tier 3 (calibration by regime) and tier 5 (week-ahead) (`evidence/ofr-followup/tables.md`, Table 1; `judge.md` is the full report).

Table 1. +5 bp onsets flagged / onsets at some lead 1 to 5, by year, under the judge's cut-offs. 2021 to 2023 have no +5 bp onset.

| model | 2018 | 2019 | 2020 | 2024 | 2025 | all |
|---|---|---|---|---|---|---|
| risk_gbm (passer) | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_gbm + dealer and tri-party rate | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_gbm_base (passer) | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_gbm_base + dealer and tri-party rate | 0/5 | 10/13 | 0/2 | 0/2 | 5/5 | 15/27 |
| risk_logistic (passer) | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_logistic + dealer and tri-party rate | 0/5 | 10/13 | 0/2 | 0/2 | 5/5 | 15/27 |
| risk_logistic_base (passer) | 0/5 | 10/13 | 0/2 | 0/2 | 3/5 | 13/27 |
| risk_logistic_base + dealer and tri-party rate | 0/5 | 10/13 | 0/2 | 0/2 | 5/5 | 15/27 |
| risk_quantile_skewt_base (passer) | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_quantile_skewt_base, scaled (control for the scaling) | 0/5 | 10/13 | 0/2 | 0/2 | 4/5 | 14/27 |
| risk_quantile_skewt_base + dealer and tri-party rate, scaled | 0/5 | 10/13 | 0/2 | 0/2 | 5/5 | 15/27 |

**The missed years stay missed.** With the flag, the five onsets of 2018 and the two of 2020 are in every denominator, and not one of
the eleven models flags any of them, at any lead; 2024 (two onsets) stays at 0 of 2. The only movement is in 2025, where four of the five
candidates flag one or two more of the five onsets than their passers (`risk_gbm_base` 4 to 5, `risk_logistic` 4 to 5,
`risk_logistic_base` 3 to 5, `risk_quantile_skewt_base` 4 to 5; `risk_gbm` stays at 3). That is one or two onsets in one year, inside the
intervals of the judge's Table 1 (onset recall 0.50 to 0.62, intervals overlapping).

**The scaling alone changes nothing.** `risk_quantile_skewt_base_minmax` flags the same onsets as `risk_quantile_skewt_base` in every
year, at every lead, and the candidate's paired differences against the scaled and the unscaled control agree to within 0.0001
(`evidence/ofr-followup/paired.md`). The skew-t candidate's differences are therefore the group's.

Table 2. Paired Brier difference at +5 bp, candidate minus its passer, all scored days (negative favours the candidate; 90%
stationary-bootstrap interval; * = interval excludes zero). The splits by regime and pressure-day type are in
`evidence/ofr-followup/paired.md`.

| candidate | h=1 | h=2 | h=3 | h=4 | h=5 |
|---|---|---|---|---|---|
| risk_gbm_dealer_ofr | +0.0006 [-0.0008, +0.0021] | -0.0007 [-0.0018, +0.0001] | +0.0003 [-0.0001, +0.0009] | +0.0003 [-0.0001, +0.0008] | -0.0002 [-0.0007, +0.0003] |
| risk_gbm_base_dealer_ofr | +0.0003 [-0.0016, +0.0023] | -0.0006 [-0.0018, +0.0004] | -0.0016 [-0.0031, -0.0001] * | +0.0009 [+0.0003, +0.0017] * | -0.0010 [-0.0026, +0.0000] |
| risk_logistic_dealer_ofr | +0.0034 [+0.0003, +0.0069] * | +0.0032 [+0.0007, +0.0061] * | +0.0011 [+0.0001, +0.0022] * | +0.0018 [+0.0003, +0.0036] * | +0.0020 [+0.0004, +0.0038] * |
| risk_logistic_base_dealer_ofr | +0.0027 [+0.0001, +0.0055] * | +0.0028 [+0.0008, +0.0051] * | +0.0008 [-0.0003, +0.0020] | +0.0012 [-0.0005, +0.0030] | +0.0012 [-0.0004, +0.0031] |
| risk_quantile_skewt_base_dealer_ofr | +0.0004 [-0.0026, +0.0033] | +0.0031 [+0.0000, +0.0064] * | +0.0014 [-0.0025, +0.0062] | +0.0055 [+0.0007, +0.0111] * | +0.0008 [-0.0028, +0.0044] |

* The differences are of the order of 0.001 to 0.005 in either direction, and most intervals include zero. Where an interval excludes
  zero it is mostly on the **worse** side: the two logistic forms at h = 1 to 2 (and the first at every horizon) and the skew-t form at
  h = 2 and 4. `risk_gbm_base_dealer_ofr` is better at h = 3 (-0.0016) and worse at h = 4 (+0.0009). With twenty-five comparisons a few
  intervals exclude zero by chance, and there is no consistent sign in favour of the added inputs.
* By regime at h = 1, gains and losses concentrate in 2020 (the logistic forms are worse by 0.012 to 0.016 there, four pressure days)
  and in 2018-19, where the differences are small and inside their intervals. The 2021 to 2023 regime has no pressure day and shows
  differences of zero to four decimals.
* Against #496's dealer group without the tri-party rate, the logistic forms' h = 1 loss is the same size (+0.0035 there, +0.0034 here
  for `risk_logistic`), so the tri-party rate does not change what the dealer group did. This page does not re-run #496's arms; the
  comparison is by the published paired table of that record.

Table 3. Judge row (tiers 1, 3, 5), +5 bp, h = 1 to 5 (`evidence/ofr-followup/tables.md`): ten of the eleven models meet tier 1 (all
but `risk_logistic_dealer_ofr`), and none passes tier 3 (calibrated regimes with
pressure at h = 1: 1 or 2 of 4) or tier 5. `risk_quantile_skewt_base_dealer_ofr` has the largest tier 3 flag rate in state 0 and in
2021 to 2023 (5.4 flags per 252 days).

## What did not run, and for Eleonora

* **The GCF rate is not an input.** It is empty on most days after publication, and no fill is neutral: any fill turns a value's
  existence into the input the ruling on #520 refuses. A fill that does not (the rate of another segment, a carried value, a model of
  the gaps) is a design choice for Eleonora; this page does not make it. The tri-party rate alone is in.
* **A one-row hole in the tri-party rate is carried** (2022-06-17), the one choice made beyond the directive's text, on the precedent
  of the SOFR percentiles. It is recorded as an amendment in the declaration, before any score was read.
* No candidate passes, so no "Publish?" issue is opened.

## Reproduce

Published panel `4ddc3882…`, scratch panel from the chain in the docstring of `scripts/unused_inputs.py`, with the one added step:

```
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
PYTHONPATH=src python3 scripts/net_settlement.py panel --panel AUG2.csv --output AUG3.csv
PYTHONPATH=src python3 scripts/fed_liquidity.py panel --panel AUG3.csv --output AUG4.csv
PYTHONPATH=src python3 scripts/policy_features.py panel --panel AUG4.csv --output AUG5.csv
PYTHONPATH=src python3 scripts/unused_inputs.py panel --panel AUG5.csv --output AUG6.csv
for h in 1 2 3 4 5: PYTHONPATH=src OMP_NUM_THREADS=1 python3 scripts/unused_inputs.py run --declaration metadata/ofr_followup.json --panel AUG6.csv --published PUBLISHED.csv --horizon $h --output OUT/ofr_h$h.json
for h in 1 2 3 4 5: PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUBLISHED.csv --horizon $h --published --output OUT/bench_h$h.json
PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUBLISHED.csv --output OUT/judge.json --markdown OUT/judge.md OUT/bench_h?.json OUT/ofr_h?.json
PYTHONPATH=src python3 scripts/pressure_judge.py table OUT/judge.json --output OUT/tables.md
PYTHONPATH=src python3 scripts/unused_inputs.py report --declaration metadata/ofr_followup.json --panel PUBLISHED.csv --output OUT/paired.json --markdown OUT/paired.md OUT/bench_h?.json OUT/ofr_h?.json
```
