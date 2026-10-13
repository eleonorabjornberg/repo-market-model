# H9 step 1: forecastability, lead and overlap of the richer targets (#639)

An exploratory screen on development data for hypothesis **H9** (the secondary goal: richer targets carry more learnable signal), step 1 of `docs/research/hypotheses/H9.md`. It is not a record, not a model and
**not a verdict**: development data never gives one (`docs/decisions/scoring-protocol.md` §1, ruling of Eleonora on #639, 12 October 2026). Nothing is fitted, selected into a model or published, no published figure moves, nothing
is written into `docs/runs/`. No day after 2025-12-31 is read (the script refuses a panel past it; `docs/decisions/lockbox.md`), no hindsight regime label is used (ruling on #515: the regimes are the as-of scarcity state and the
day type, both known at the decision instant), and every value is read as of the decision instant with the as-of rule (`repo_model.asof.InformationRule`, `docs/decisions/information-set.md`). The choices are in
`metadata/richer_targets_639.json`, committed before any score; `scripts/richer_targets_639.py` refuses to run unless that file is committed and unchanged and the panel's digest is the declared one.

**Caution.** Ten targets, five leads, several splits and three questions, and no correction for any of it. A cell that stands out is a candidate for step 2's declared test, not evidence. The 26 onsets are few: split by regime a cell
rests on a handful of them, and the table says how many.

## What was screened

Ten targets (`repo_model.richer_targets.TARGETS`), each as published and as of each decision instant:

| target | unit | definition |
|---|---|---|
| `sofr_p99_iorb_bps` | bp | SOFR 99th percentile − IORB |
| `sofr_dispersion_bps` | bp | SOFR 99th − 1st percentile |
| `tgcr_iorb_bps`, `bgcr_iorb_bps` | bp | TGCR − IORB, BGCR − IORB |
| `tgcr_dispersion_bps`, `bgcr_dispersion_bps` | bp | TGCR and BGCR 99th − 1st percentile (published with each rate; read from the tracked snapshots under the rate's own declared lag) |
| `effr_iorb_bps` | bp | EFFR − IORB |
| `on_rrp_bn`, `on_rrp_change_bn` | USD bn | ON RRP take-up, level and change from the previous panel day (the Desk's operation results, #45) |
| `srf_take_up_bn` | USD bn | standing repo facility take-up (operation results, #127; the facility's first operation is 2021-07-29, so 1,035 of the 1,873 scored days enter its lead-1 cells, #659) |

The standing repo facility series is usable but short: it starts in 2021 and 34 of the 140 pressure days and 7 of the 26 onsets fall inside it. It is screened, with that limit stated on every cell.

## Method, in short

* **Days.** The 1,873 scored days of the lead-1 fold grid, 2018-06-29 to 2025-12-31, of which 140 are above +5 bp (strictly, on whole basis points), and the 26 onsets of the grid every horizon scores (`repo_model.pressure.onsets`).
* **Forecastability.** At leads of 1, 2, 3, 5 and 10 panel days, B1 (the last public value plus the empirical distribution of the lead's own changes over the trailing two years) and B2 (the trailing year's values on days of the scored
  day's type): the benchmarks of scoring protocol v1 §4, generalised from the spread to each series (`richer_targets.b1_quantiles`, `b2_quantiles`, using `protocol_benchmarks`' window, interpolation and look-ahead guard). Scored by the protocol's grid
  CRPS and by the absolute error of the median; the error of the last value is shown beside them. B1's skill over B2 is `mean(S(B2) − S(B1)) / mean(S(B2))`: positive when persistence beats the calendar climatology. Intervals: the
  protocol's stationary bootstrap (`scoring_protocol.paired_test`, mean block 10, 10,000 draws), two-sided 90% here. **No model is scored in this step**: these are the yardsticks a step 2 model has to beat, and B1 against B2 says where a
  target is persistent and where it is not.
* **Lead.** The target's as-of value at each lead against the +5 bp indicator of the scored day (Spearman, with a stationary-bootstrap interval on full-sample ranks); and the pre-onset contrast, the value read at lead 1 on the 1 to 5 panel
  days before each onset against every other scored day (the difference in the other days' standard deviations and the AUC), with an interval from resampling whole onsets. The +5 bp indicator is the definition of an episode here, as in
  the screens of #478 and #629; the judge it served is retired as a decision rule (protocol §10).
* **Overlap.** Spearman of the target with SOFR − IORB on the same day, in level and in the change from the day before.

## Forecastability (Table 1; the other leads, the splits and every cell are in the evidence folder)

Skill of B1 over B2, all scored days, with a two-sided 90% interval (leads 1, 5 and 10; mean CRPS in the target's unit).

| target | lead | days | CRPS B1 | CRPS B2 | skill of B1 over B2 | MAE B1 | MAE B2 | MAE last value |
|---|---|---|---|---|---|---|---|---|
| `sofr_p99_iorb_bps` | 1 | 1865 | 4.066 | 3.931 | -0.035 [-0.222, +0.175] | 4.741 | 5.531 | 4.739 |
| `sofr_p99_iorb_bps` | 5 | 1862 | 5.020 | 4.063 | -0.236 [-0.504, +0.007] | 5.924 | 5.686 | 5.924 |
| `sofr_p99_iorb_bps` | 10 | 1852 | 4.992 | 4.130 | -0.209 [-0.519, +0.042] | 5.949 | 5.791 | 5.945 |
| `sofr_dispersion_bps` | 1 | 1865 | 4.156 | 3.641 | -0.142 [-0.332, +0.063] | 4.835 | 4.923 | 4.835 |
| `sofr_dispersion_bps` | 5 | 1862 | 4.976 | 3.758 | -0.324 [-0.603, -0.073] | 5.865 | 5.056 | 5.865 |
| `sofr_dispersion_bps` | 10 | 1852 | 5.069 | 3.810 | -0.330 [-0.667, -0.066] | 6.011 | 5.120 | 6.005 |
| `tgcr_iorb_bps` | 1 | 1865 | 1.842 | 2.351 | +0.216 [+0.039, +0.380] | 2.228 | 3.498 | 2.228 |
| `tgcr_iorb_bps` | 5 | 1862 | 2.197 | 2.418 | +0.092 [-0.082, +0.248] | 2.714 | 3.564 | 2.714 |
| `tgcr_iorb_bps` | 10 | 1852 | 2.248 | 2.478 | +0.093 [-0.088, +0.250] | 2.818 | 3.620 | 2.817 |
| `tgcr_dispersion_bps` | 1 | 1865 | 6.318 | 6.065 | -0.042 [-0.183, +0.089] | 7.139 | 8.146 | 7.139 |
| `tgcr_dispersion_bps` | 5 | 1862 | 7.859 | 6.220 | -0.264 [-0.413, -0.121] | 8.942 | 8.285 | 8.936 |
| `tgcr_dispersion_bps` | 10 | 1852 | 8.131 | 6.325 | -0.285 [-0.462, -0.124] | 9.215 | 8.402 | 9.209 |
| `bgcr_iorb_bps` | 1 | 1865 | 1.847 | 2.348 | +0.213 [+0.036, +0.377] | 2.236 | 3.488 | 2.236 |
| `bgcr_iorb_bps` | 5 | 1862 | 2.196 | 2.414 | +0.091 [-0.084, +0.248] | 2.713 | 3.555 | 2.713 |
| `bgcr_iorb_bps` | 10 | 1852 | 2.248 | 2.474 | +0.091 [-0.090, +0.248] | 2.817 | 3.614 | 2.817 |
| `bgcr_dispersion_bps` | 1 | 1865 | 7.278 | 6.432 | -0.131 [-0.297, +0.022] | 8.232 | 8.584 | 8.231 |
| `bgcr_dispersion_bps` | 5 | 1862 | 8.893 | 6.584 | -0.351 [-0.528, -0.189] | 10.135 | 8.731 | 10.134 |
| `bgcr_dispersion_bps` | 10 | 1852 | 9.031 | 6.684 | -0.351 [-0.558, -0.168] | 10.268 | 8.852 | 10.249 |
| `effr_iorb_bps` | 1 | 1865 | 0.198 | 0.963 | +0.795 [+0.721, +0.858] | 0.221 | 1.496 | 0.221 |
| `effr_iorb_bps` | 5 | 1862 | 0.361 | 1.006 | +0.641 [+0.520, +0.745] | 0.419 | 1.535 | 0.419 |
| `effr_iorb_bps` | 10 | 1852 | 0.470 | 1.046 | +0.551 [+0.420, +0.663] | 0.545 | 1.573 | 0.545 |
| `on_rrp_bn` | 1 | 1865 | 20.243 | 185.373 | +0.891 [+0.873, +0.905] | 27.995 | 302.310 | 27.797 |
| `on_rrp_bn` | 5 | 1862 | 29.510 | 194.956 | +0.849 [+0.823, +0.870] | 42.101 | 313.106 | 41.674 |
| `on_rrp_bn` | 10 | 1852 | 39.997 | 205.443 | +0.805 [+0.770, +0.833] | 57.942 | 324.397 | 56.228 |
| `on_rrp_change_bn` | 1 | 1865 | 22.936 | 14.050 | -0.633 [-0.697, -0.569] | 31.701 | 19.917 | 31.642 |
| `on_rrp_change_bn` | 5 | 1861 | 22.245 | 14.137 | -0.574 [-0.650, -0.498] | 31.012 | 20.027 | 30.986 |
| `on_rrp_change_bn` | 10 | 1851 | 22.959 | 14.232 | -0.613 [-0.700, -0.533] | 31.914 | 20.141 | 31.887 |
| `srf_take_up_bn` | 1 | 1035 | 0.466 | 0.355 | -0.316 [-0.813, -0.073] | 0.483 | 0.386 | 0.483 |
| `srf_take_up_bn` | 5 | 1028 | 0.578 | 0.360 | -0.608 [-1.367, -0.243] | 0.600 | 0.388 | 0.600 |
| `srf_take_up_bn` | 10 | 1018 | 0.476 | 0.365 | -0.305 [-0.957, +0.020] | 0.489 | 0.392 | 0.489 |

* **Persistence beats the calendar climatology** (interval above zero at every lead shown) for `effr_iorb_bps` (+0.80 at lead 1, +0.55 at lead 10) and for the ON RRP level (+0.89 to +0.81). For TGCR − IORB and BGCR − IORB it does at lead 1 only
  (+0.22 and +0.21); from lead 2 the interval includes zero.
* **The calendar climatology beats persistence** (interval below zero) for the three dispersions from lead 2 on, for the ON RRP daily change at every lead, and for the facility take-up at leads 1 to 5.
* **`sofr_p99_iorb_bps`** is in between: persistence and climatology are not separated at any lead (the intervals include zero).
* **By state** (Table 2, lead 1): persistence beats the climatology in the as-of ample state for the SOFR 99th percentile (+0.28), TGCR and BGCR (+0.51 and +0.50), but not in the scarce state (−0.27, −0.03 and −0.03). The ON RRP level and EFFR are persistent in both.

| target | ample | scarce | ordinary | month end | tax date | quarter end |
|---|---|---|---|---|---|---|
| `sofr_p99_iorb_bps` | +0.28 [+0.16, +0.40] (1356) | -0.27 [-0.55, +0.03] (509) | -0.17 [-0.52, +0.13] (1603) | +0.19 [+0.02, +0.38] (150) | +0.30 [+0.16, +0.66] (89) | - |
| `sofr_dispersion_bps` | +0.25 [+0.15, +0.35] (1356) | -0.66 [-1.08, -0.36] (509) | -0.34 [-0.74, -0.01] (1603) | +0.15 [+0.00, +0.29] (150) | +0.28 [+0.14, +0.62] (89) | - |
| `tgcr_iorb_bps` | +0.51 [+0.41, +0.60] (1356) | -0.03 [-0.28, +0.22] (509) | +0.19 [-0.05, +0.37] (1603) | +0.30 [+0.13, +0.51] (150) | +0.28 [+0.17, +0.67] (89) | - |
| `tgcr_dispersion_bps` | +0.03 [-0.12, +0.17] (1356) | -0.37 [-0.61, -0.12] (509) | -0.15 [-0.33, +0.01] (1603) | +0.12 [-0.09, +0.35] (150) | +0.39 [+0.15, +0.67] (89) | - |
| `bgcr_iorb_bps` | +0.50 [+0.40, +0.59] (1356) | -0.03 [-0.28, +0.22] (509) | +0.18 [-0.05, +0.37] (1603) | +0.30 [+0.12, +0.50] (150) | +0.28 [+0.17, +0.68] (89) | - |
| `bgcr_dispersion_bps` | +0.01 [-0.14, +0.16] (1356) | -0.58 [-0.92, -0.25] (509) | -0.28 [-0.53, -0.07] (1603) | +0.12 [-0.09, +0.33] (150) | +0.33 [+0.13, +0.66] (89) | - |
| `effr_iorb_bps` | +0.87 [+0.83, +0.90] (1356) | +0.75 [+0.64, +0.84] (509) | +0.80 [+0.73, +0.87] (1603) | +0.78 [+0.67, +0.87] (150) | +0.75 [+0.61, +0.95] (89) | - |
| `on_rrp_bn` | +0.90 [+0.88, +0.91] (1356) | +0.61 [+0.37, +0.73] (509) | +0.89 [+0.88, +0.91] (1603) | +0.90 [+0.84, +0.92] (150) | +0.89 [+0.85, +0.90] (89) | - |
| `on_rrp_change_bn` | -0.64 [-0.71, -0.58] (1356) | -0.53 [-0.86, -0.29] (509) | -0.70 [-0.77, -0.62] (1603) | -0.27 [-0.43, -0.10] (150) | -0.48 [-0.66, -0.31] (89) | - |
| `srf_take_up_bn` | -1.08 [-2.13, -0.50] (968) | -0.28 [-0.61, -0.05] (67) | -0.71 [-1.66, -0.29] (890) | +0.09 [-0.96, +0.27] (85) | -0.75 [-4.03, -0.04] (48) | - |

## Lead (Tables 3 and 5)

Spearman of the target's as-of value with the +5 bp indicator of the scored day, all scored days.

| target | lead 1 | lead 2 | lead 3 | lead 5 | lead 10 | pressure days at lead 1 |
|---|---|---|---|---|---|---|
| `sofr_p99_iorb_bps` | +0.39 [+0.33, +0.45] | +0.37 [+0.31, +0.43] | +0.37 [+0.30, +0.42] | +0.36 [+0.29, +0.42] | +0.37 [+0.31, +0.42] | 140 |
| `sofr_dispersion_bps` | +0.23 [+0.16, +0.29] | +0.19 [+0.13, +0.26] | +0.17 [+0.11, +0.24] | +0.16 [+0.10, +0.23] | +0.19 [+0.13, +0.25] | 140 |
| `tgcr_iorb_bps` | +0.39 [+0.32, +0.45] | +0.38 [+0.31, +0.43] | +0.37 [+0.30, +0.43] | +0.37 [+0.30, +0.42] | +0.38 [+0.31, +0.43] | 140 |
| `tgcr_dispersion_bps` | +0.10 [+0.04, +0.16] | +0.09 [+0.03, +0.15] | +0.07 [+0.01, +0.13] | +0.05 [-0.01, +0.11] | +0.07 [+0.02, +0.12] | 140 |
| `bgcr_iorb_bps` | +0.39 [+0.32, +0.45] | +0.38 [+0.31, +0.43] | +0.37 [+0.30, +0.43] | +0.37 [+0.30, +0.42] | +0.38 [+0.31, +0.43] | 140 |
| `bgcr_dispersion_bps` | +0.21 [+0.15, +0.27] | +0.19 [+0.13, +0.24] | +0.17 [+0.11, +0.23] | +0.15 [+0.09, +0.20] | +0.18 [+0.13, +0.23] | 140 |
| `effr_iorb_bps` | +0.35 [+0.27, +0.42] | +0.34 [+0.27, +0.41] | +0.34 [+0.26, +0.41] | +0.34 [+0.26, +0.41] | +0.33 [+0.25, +0.40] | 140 |
| `on_rrp_bn` | -0.23 [-0.30, -0.18] | -0.24 [-0.30, -0.18] | -0.25 [-0.31, -0.19] | -0.23 [-0.29, -0.17] | -0.23 [-0.29, -0.18] | 140 |
| `on_rrp_change_bn` | -0.00 [-0.03, +0.02] | -0.02 [-0.04, +0.00] | -0.04 [-0.06, -0.02] | -0.03 [-0.05, -0.01] | -0.02 [-0.04, +0.00] | 140 |
| `srf_take_up_bn` | +0.18 [+0.06, +0.27] | +0.21 [+0.12, +0.28] | +0.20 [+0.11, +0.26] | +0.14 [+0.04, +0.22] | +0.22 [+0.14, +0.29] | 34 |

The pre-onset contrast at lead 1 (all scored days; the splits by state are in the evidence folder).

| target | split | onsets | std. difference | AUC |
|---|---|---|---|---|
| `sofr_p99_iorb_bps` | all | 26 | +0.24 [+0.20, +0.29] | +0.83 [+0.79, +0.86] |
| `sofr_dispersion_bps` | all | 26 | -0.03 [-0.07, +0.02] | +0.59 [+0.54, +0.63] |
| `tgcr_iorb_bps` | all | 26 | +0.53 [+0.44, +0.62] | +0.83 [+0.78, +0.86] |
| `tgcr_dispersion_bps` | all | 26 | -0.20 [-0.24, -0.16] | +0.48 [+0.44, +0.52] |
| `bgcr_iorb_bps` | all | 26 | +0.53 [+0.44, +0.62] | +0.83 [+0.78, +0.86] |
| `bgcr_dispersion_bps` | all | 26 | -0.13 [-0.16, -0.09] | +0.59 [+0.56, +0.63] |
| `effr_iorb_bps` | all | 26 | +0.98 [+0.69, +1.22] | +0.78 [+0.70, +0.85] |
| `on_rrp_bn` | all | 26 | -0.82 [-0.84, -0.79] | +0.26 [+0.23, +0.29] |
| `on_rrp_change_bn` | all | 26 | +0.01 [-0.03, +0.05] | +0.46 [+0.43, +0.49] |
| `srf_take_up_bn` | all | 7 | -0.07 [-0.12, +0.02] | +0.67 [+0.62, +0.73] |

* **The rate-level targets correlate with pressure to the extent the spread's own lag does** (+0.39 for `sofr_p99_iorb_bps`, `tgcr_iorb_bps` and `bgcr_iorb_bps`; `docs/pivot/source-screen-result.md` has +0.393 for the spread's as-of lag on the same
  days), and they read high before onsets (AUC 0.83). The EFFR is at +0.35 and AUC 0.78. The ON RRP level is the mirror image (−0.23, AUC 0.26: low before onsets).
* **Almost all of that lead is the state, not a signal within it.** Within the as-of ample state the correlation with pressure is +0.06 to +0.07 for these targets and within the scarce state about +0.4 (Table 4 in the evidence folder), and in the scarce
  state, where 23 of the 26 onsets have a pre-onset day, the pre-onset AUC is 0.47 to 0.52 for the rate-level targets and 0.41 to 0.43 for the dispersions: no higher than on the other scarce days.
* **The dispersions lead weakly** (+0.23 for SOFR, +0.10 for TGCR, +0.21 for BGCR at lead 1), and read about the same before onsets as on other days (AUC 0.48 to 0.59 over all days). The ON RRP change and the facility take-up have no lead the interval separates
  from zero in a way that survives the state split; the facility series has 34 pressure days and 7 onsets to rest on.

## Overlap with SOFR − IORB (Table 6)

| target | level, all | level, ordinary days | level, ample | level, scarce | change, all | change, ordinary days |
|---|---|---|---|---|---|---|
| `sofr_p99_iorb_bps` | +0.83 [+0.77, +0.88] | +0.82 [+0.76, +0.88] | +0.61 [+0.48, +0.73] | +0.92 [+0.89, +0.94] | +0.65 [+0.60, +0.69] | +0.62 [+0.56, +0.67] |
| `sofr_dispersion_bps` | +0.06 [-0.09, +0.21] | +0.04 [-0.12, +0.21] | -0.33 [-0.48, -0.14] | +0.61 [+0.51, +0.71] | +0.37 [+0.30, +0.43] | +0.31 [+0.24, +0.38] |
| `tgcr_iorb_bps` | +0.95 [+0.93, +0.96] | +0.95 [+0.93, +0.96] | +0.88 [+0.84, +0.91] | +0.97 [+0.96, +0.98] | +0.80 [+0.76, +0.83] | +0.78 [+0.74, +0.82] |
| `tgcr_dispersion_bps` | -0.16 [-0.29, -0.03] | -0.19 [-0.32, -0.04] | -0.43 [-0.56, -0.28] | +0.57 [+0.45, +0.67] | +0.25 [+0.19, +0.30] | +0.21 [+0.15, +0.26] |
| `bgcr_iorb_bps` | +0.95 [+0.93, +0.96] | +0.95 [+0.93, +0.96] | +0.88 [+0.84, +0.91] | +0.97 [+0.96, +0.98] | +0.79 [+0.75, +0.83] | +0.78 [+0.73, +0.81] |
| `bgcr_dispersion_bps` | +0.03 [-0.11, +0.18] | +0.01 [-0.15, +0.18] | -0.35 [-0.50, -0.16] | +0.57 [+0.45, +0.68] | +0.35 [+0.30, +0.40] | +0.31 [+0.25, +0.36] |
| `effr_iorb_bps` | +0.63 [+0.55, +0.70] | +0.64 [+0.55, +0.72] | +0.19 [-0.00, +0.35] | +0.50 [+0.32, +0.66] | +0.22 [+0.16, +0.29] | +0.21 [+0.14, +0.28] |
| `on_rrp_bn` | -0.81 [-0.84, -0.77] | -0.81 [-0.85, -0.77] | -0.77 [-0.84, -0.69] | +0.05 [-0.12, +0.23] | -0.05 [-0.10, -0.00] | -0.08 [-0.12, -0.03] |
| `on_rrp_change_bn` | -0.10 [-0.13, -0.06] | -0.09 [-0.13, -0.05] | -0.09 [-0.13, -0.05] | +0.02 [-0.05, +0.09] | -0.02 [-0.06, +0.01] | -0.04 [-0.08, -0.00] |
| `srf_take_up_bn` | +0.31 [+0.23, +0.40] | +0.31 [+0.22, +0.39] | +0.22 [+0.16, +0.29] | +0.74 [+0.65, +0.81] | +0.12 [+0.05, +0.19] | +0.09 [+0.01, +0.16] |

* **TGCR − IORB and BGCR − IORB repeat the spread** (+0.95 in level, +0.80 in change), the SOFR 99th percentile nearly so (+0.83), and the ON RRP level is its mirror (−0.81). These carry little that SOFR − IORB does not already say.
* **The dispersions are close to unrelated to the spread in the pooled sample** (+0.06, −0.16, +0.03) because the relation changes sign with the state: negative in the ample state (−0.33 to −0.43) and positive in the scarce state (+0.57 to +0.61).
  The EFFR (+0.63) and the facility take-up (+0.31) are in between; the ON RRP change (−0.10) is close to unrelated.

## What this does and does not say about H9

* H9's kill criterion is "no forecast skill over persistence, or no lead on the +5 episodes". **This step cannot meet or fail it**: it fits no model and development data gives no verdict. It gives the benchmarks a step 2 model has to beat (Table 1)
  and the lead each target has before any model (Tables 3 to 5).
* On the evidence of this screen alone, no target shows a lead on the onsets that is not the as-of scarcity state (Table 5 and the state splits), and the targets with the clearest lead are those that repeat SOFR − IORB (Table 6).
* **Not done: step 2** (the model, at most three targets, one form each, scored against as-of persistence and paired, and the nested test against #634's row). Choosing the targets is the open question in the pull request; the model of #634 is not on main.

## Reproduce

```
PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
PYTHONPATH=src python3 scripts/early_warning_inputs.py panel --panel PUB.csv --output EW.csv
PYTHONPATH=src python3 scripts/richer_targets_639.py panel --panel AUG2.csv --extra EW.csv --output H9.csv
PYTHONPATH=src python3 scripts/richer_targets_639.py run --panel H9.csv --output OUT/screen.json
PYTHONPATH=src python3 scripts/richer_targets_639.py report OUT/screen.json --output OUT/tables.md
```

The panel's digest is `347f5afb…` (declared in `metadata/richer_targets_639.json`; `run` refuses another). Evidence: `docs/pivot/evidence/richer-targets-639/` (`screen.json`, every cell; `tables.md`, all six tables).
Scratch panels are gitignored, so this is not a test; the tested parts are `tests/test_richer_targets.py` (the target columns, the as-of reads, the benchmarks and their guards, the rank statistics).
