# H9 step 3: each richer target's forecast as an input of H5's candidate (#842)

A measurement on development data for hypothesis **H9** (the secondary goal), step 3 of `docs/research/hypotheses/H9.md`, milestone M4. It is not a record and **not a verdict**: development data never gives one
(`docs/decisions/scoring-protocol.md` §1). Nothing is published: no target joins any published declaration, no published figure moves, nothing is written into `docs/runs/`. No day after 2025-12-31 is read
(`docs/decisions/lockbox.md`; the script refuses a locked day). Every choice is in `metadata/h9_nested_842.json`, committed before any nested score. The full tables are in `docs/pivot/evidence/h9-nested-842/report.md`
and `score.json`.

## The test

H5's candidate `gbm_funding` (the published funding features, 23 levels, no calibration; Eleonora's ruling of 15 October 2026), walk-forward at leads 1 to 5, with and without one target's forecast as an extra input, one target at a time.
The forecast is the median of #706's walk-forward law of the target for the same target day, made at the same decision instant by a fit that used only what was public before it (`repo_model.target_forecasts`; the guard refuses a forecast whose
fit came after its decision day). The targets are the three #706 modelled: `bgcr_dispersion_bps`, `on_rrp_change_bn`, `sofr_dispersion_bps`. The base re-walks #634's `gbm_funding` and reproduces its recorded grid CRPS (1.8261 on 1868 days).
The plus walks start at the base's next refit block after their first forecast exists, so all variants are scored on the 1,848 decision days (2018-07-30 to 2025-12-23) that every walk covers.

## Result (grid CRPS, mean over leads 1 to 5; `d = S(base) − S(base + target)`, positive favours the target's forecast)

| target | CRPS base | CRPS with target | d (lower 95%) | skill (lower 95%) | Holm p | d without 2019-09-18 (lower 95%) |
|---|---|---|---|---|---|---|
| `bgcr_dispersion_bps` | 1.824 | 1.829 | −0.004 (−0.015) | −0.002 (−0.008) | 1.000 | −0.004 (−0.015) |
| `on_rrp_change_bn` | 1.824 | 1.825 | −0.000 (−0.009) | −0.000 (−0.005) | 1.000 | −0.000 (−0.009) |
| `sofr_dispersion_bps` | 1.824 | 1.818 | +0.006 (−0.005) | +0.003 (−0.003) | 0.517 | +0.006 (−0.004) |

Upper-tail twCRPS: d +0.005, +0.003 and +0.005, lower bounds −0.003 for all three, with and without 2019-09-18. Against the benchmarks the candidate keeps its phase 2 skill (+0.204 over B1, +0.276 over B2); with a target it reads +0.202, +0.204, +0.207
over B1 and +0.274, +0.275, +0.278 over B2, none distinguishable from the candidate's.

## Splits

By regime, as-of scarcity state, pressure-day type and lead (`report.md`), with and without 2019-09-18 where that day falls in the split. Of the splits read, two show a lower bound above zero, both for `sofr_dispersion_bps`:
regime 2025-26 (d +0.039, lower +0.014) and lead 5 (d +0.017, lower +0.002). The other targets show none. With about 40 cells read per target, two lower bounds above zero are within what the number of cells gives by chance;
neither survives pooling (pooled lower bound −0.005). The 2021–23 regime reads worse for all three (d −0.020, −0.009, −0.016; lower bounds −0.034, −0.021, −0.027 for BGCR dispersion, ON RRP change and SOFR dispersion).
Day 2019-09-18 moves no figure at the printed precision.

## Readings (development data, not a verdict)

* `bgcr_dispersion_bps`: does not improve the candidate beyond its interval, with or without 2019-09-18.
* `on_rrp_change_bn`: does not improve the candidate beyond its interval, with or without 2019-09-18.
* `sofr_dispersion_bps`: does not improve the candidate beyond its interval, with or without 2019-09-18; the point estimate is positive (skill +0.003).
* **H9 against its kill** ("no skill over the target's own persistence, and no nested gain for H5"): the nested part holds on development data, since no target improves the candidate beyond its interval. The first part was read in #706 and is not re-read here.
  Development data, not a verdict.

## What was not checked

* Only the median of each law was tried as the input; the declaration forbids other forms (width, tail level), so a gain in another form is not excluded.
* Targets were added one at a time; no combination was tried.
* The base was not re-tuned for the extra column (hyperparameters fixed at the candidate's).
* If the candidate moves to the direct twin of #825, the step is re-scored.
* Confirmation days: none read; nothing here is registered.
