# Settlement-timing probit and skew-t quantile regression (track T of #374, #379)

A scratch measurement under the judge of #375 as merged (the replacement bar of the ruling on #375, development mode:
scored days 2018-06-29 to 2025-12-31). It writes nothing into `docs/runs/`, moves no published figure and logs nothing
to the live record. No comparison scores a locked day (`docs/decisions/lockbox.md`); the confirmation window is not
looked at.

**Candidates** (declared in `metadata/pressure_judge.json` and `src/repo_model/settlement_timing.py`, committed before
any score was read): a ridge probit of `spread > tau` at +5 and +10 bp, and linear quantile regressions of SOFR − IORB
on a 13-quantile grid smoothed per day into an Azzalini-Capitanio skew-t in the Adrian, Boyarchenko & Giannone way,
each on three nested input sets. `timing`: the spread, Treasury settlement size (total and coupons), days to month end,
quarter-end, tax date. `scarcity`: adds reserves (every scheduled term times reserves), #115's state and the TGA. `tga`:
adds track D's `tga_daily` and `tga_daily_change` (#377). Settlement amounts leave the inputs at horizons of 2 or more,
as in pressure model v1. All are uncalibrated, flagging at a declared 0.2 at both thresholds. Walk-forward on the shared
fold grid (minimum history 61, refit every 21 scored days), as-of rule on every read.

**Reproduce** (scratch panel digest `24dd9d41…`, published `4ddc3882…`):

```
PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
PYTHONPATH=src python3 scripts/settlement_timing.py run --panel AUG2.csv --published PUB.csv --candidate NAME --horizon H --output OUT/NAME_hH.json
PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUB.csv --horizon H --output OUT/bench_hH.json
PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUB.csv --output OUT/judge.json --markdown OUT/judge.md OUT/*_h?.json
```

The benchmark rows here omit `--published`; the published baseline row is then absent from this table.

## Result: no candidate passes; every one fails tier 1 on false alarms alone

+5 bp, tier 1 at lead of at least 1 (26 onsets), tier 3 at the worst horizon, tier 5:

| Model | onsets flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | tier 3 flags per 252 days (state 0 / 2021-23) | calibrated by regime (h = 1) | tier 5 Brier gain over climatology, calibrated |
|---|---|---|---|---|---|---|---|
| calendar climatology | 10 | 0.385 [0.222, 0.556] | 0.385 | 6.62 | 9.0 / 11.1 | 1 of 5 regimes | none (0), yes |
| persistence-logistic | 8 | 0.308 [0.148, 0.500] | 0.269 | 5.65 | 1.0 / 0.0 | not shown here | worse than climatology |
| probit, timing | 17 | 0.654 [0.500, 0.800] | 0.278 | 5.96 | 5.4 / 5.7 | 2 of 5 | +0.0209 [+0.0130, +0.0300], yes |
| probit, scarcity | 18 | 0.692 [0.524, 0.852] | 0.423 | 7.35 | 0.2 / 0.0 | 1 of 5 | +0.0476 [+0.0324, +0.0645], no |
| probit, tga | 18 | 0.692 [0.531, 0.850] | 0.406 | 6.88 | 0.7 / 0.0 | 2 of 5 | +0.0470 [+0.0318, +0.0634], no |
| quantile, timing | 16 | 0.615 [0.452, 0.765] | 0.269 | 4.65 | 5.6 / 6.1 | 2 of 5 | +0.0280 [+0.0163, +0.0425], yes |
| quantile, scarcity | 20 | 0.769 [0.609, 0.900] | 0.423 | 7.46 | 1.0 / 0.0 | 3 of 5 | +0.0521 [+0.0361, +0.0692], yes |
| quantile, tga | 18 | 0.692 [0.524, 0.846] | 0.423 | 7.88 | 1.0 / 0.0 | 3 of 5 | +0.0450 [+0.0248, +0.0667], yes |

- **Recall is met and beats climatology; false alarms are not.** All six candidates flag at least half the onsets at
  lead of at least 1, with a lower interval end above climatology's recall at the same false-alarm rate. None is
  within the limit of 2 false alarms per onset: the best is 4.65 (quantile, timing) and the worst 7.88.
- **Tier 3 fails on calibration by regime, not on alarm rate.** Every candidate flags at most 21 per 252 days in the
  abundant stretches (0 to 6.1) but no candidate is calibrated in the 2021-23 regime at h = 1, and only the
  quantile regressions on the scarcity and TGA sets are calibrated in 2018-19.
- **Tier 5 holds for the three quantile regressions and the timing probit** (calibrated, and a Brier gain over
  climatology with an interval above zero). The probit on the scarcity and TGA sets beats climatology but is not calibrated.
- **The scarcity state is what adds recall and ranking** (Brier gain over climatology at tier 5 roughly doubles from the
  timing to the scarcity set); track D's daily TGA adds nothing beyond it.
- **Tier 2 (reported only):** AUROC at lead 5 on scheduled risk dates in state at least 2 is 0.58 to 0.64 against 0.46
  for climatology; none meets 0.75; the probit on scarcity and TGA and the quantile on timing beat climatology with
  an interval above zero.

Full output of the judge follows (the declaration digest it names is the one in this branch).

## Judge output

Mode: development. Declaration `metadata/pressure_judge.json` sha256 `e5053b86f250…`. Scored days 2018-06-29 to 2025-12-31. Pass rule: tier 1 (onset warning) at lead >= 1, tier 3 (no crying wolf) at every lead, and tier 5 (week-ahead window), at +5 bp; 90% stationary bootstrap intervals.

### calendar_climatology (benchmark): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no.

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 10 | 0.385 [0.222, 0.556] | 0.385 | 6.62 | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.217, 0.563] | 0.385 | 6.62 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.2 | 200 | 0.221 | 0.155 | 0.0714 | +0.0000 [+0.0000, +0.0000] | -0.0151 [-0.0211, -0.0097] | 0.586 | 0.124 | no |
| 2 | 0.2 | 201 | 0.223 | 0.154 | 0.0711 | +0.0000 [+0.0000, +0.0000] | -0.0100 [-0.0146, -0.0054] | 0.586 | 0.125 | no |
| 3 | 0.2 | 202 | 0.225 | 0.153 | 0.0707 | +0.0000 [+0.0000, +0.0000] | -0.0063 [-0.0098, -0.0028] | 0.585 | 0.126 | no |
| 4 | 0.2 | 203 | 0.225 | 0.153 | 0.0708 | +0.0000 [+0.0000, +0.0000] | -0.0085 [-0.0120, -0.0048] | 0.580 | 0.125 | no |
| 5 | 0.2 | 203 | 0.232 | 0.158 | 0.0709 | +0.0000 [+0.0000, +0.0000] | -0.0075 [-0.0114, -0.0036] | 0.578 | 0.133 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 8.5 over 1035 days; regime_2021-23: 11.1 over 748 days. Calibrated: 2018-19 no, 2020 no, 2021-23 no, 2024 no, 2025-26 yes.
- h = 2: scarcity_state_0: 8.8 over 1035 days; regime_2021-23: 11.1 over 748 days. Calibrated: 2018-19 no, 2020 no, 2021-23 no, 2024 no, 2025-26 yes.
- h = 3: scarcity_state_0: 8.8 over 1035 days; regime_2021-23: 11.1 over 748 days. Calibrated: 2018-19 no, 2020 no, 2021-23 no, 2024 no, 2025-26 yes.
- h = 4: scarcity_state_0: 8.8 over 1035 days; regime_2021-23: 11.1 over 748 days. Calibrated: 2018-19 no, 2020 no, 2021-23 no, 2024 no, 2025-26 yes.
- h = 5: scarcity_state_0: 9.0 over 1035 days; regime_2021-23: 11.1 over 748 days. Calibrated: 2018-19 no, 2020 no, 2021-23 no, 2024 no, 2025-26 yes.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.457 (climatology 0.457, difference +0.0000 [+0.0000, +0.0000]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1757, ΔBrier vs climatology +0.0000 [+0.0000, +0.0000], realised minus predicted -0.0470 [-0.1017, +0.0117]; calibrated yes, beats_climatology_brier no.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.255 | 0.310 | 0.1327 | 0.2720 | +0.0000 [+0.0000, +0.0000] |
| regime | 2020 | 251 | 4 | 0.250 | 0.013 | 0.1992 | 0.0159 | +0.0000 [+0.0000, +0.0000] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.1084 | 0.0000 | +0.0000 [+0.0000, +0.0000] |
| regime | 2024 | 250 | 5 | 0.400 | 0.500 | 0.0707 | 0.0200 | +0.0000 [+0.0000, +0.0000] |
| regime | 2025-26 | 249 | 29 | 0.069 | 0.500 | 0.0645 | 0.1165 | +0.0000 [+0.0000, +0.0000] |
| scarcity_state | 0 | 1035 | 5 | 0.400 | 0.057 | 0.0907 | 0.0048 | +0.0000 [+0.0000, +0.0000] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.1572 | 0.0031 | +0.0000 [+0.0000, +0.0000] |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | 0.0728 | 0.4146 | 0.0000 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.239 | 0.212 | 0.1413 | 0.2474 | +0.0000 [+0.0000, +0.0000] |
| day_type | month_end | 150 | 17 | 0.294 | 0.179 | 0.1364 | 0.1133 | +0.0000 [+0.0000, +0.0000] |
| day_type | ordinary | 1603 | 101 | 0.099 | 0.103 | 0.1006 | 0.0630 | +0.0000 [+0.0000, +0.0000] |
| day_type | quarter_end | 31 | 9 | 0.889 | 0.267 | 0.4089 | 0.2903 | +0.0000 [+0.0000, +0.0000] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.178 | 0.2274 | 0.1461 | +0.0000 [+0.0000, +0.0000] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4822 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2213 | 0.2213 |

### persistence_logistic (benchmark): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no.

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 8 | 0.308 [0.148, 0.500] | 0.269 | 5.65 | recall no, recall_above_climatology no, false_alarms no |
| lead_at_least_3 | 26 | 7 | 0.269 [0.115, 0.448] | 0.269 | 5.65 | reported only; meets far recall: no |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.2 | 160 | 0.507 | 0.444 | 0.0563 | +0.0151 [+0.0094, +0.0214] | +0.0000 [+0.0000, +0.0000] | 0.876 | 0.456 | no |
| 2 | 0.2 | 158 | 0.453 | 0.399 | 0.0611 | +0.0100 [+0.0056, +0.0146] | +0.0000 [+0.0000, +0.0000] | 0.817 | 0.398 | no |
| 3 | 0.2 | 203 | 0.406 | 0.276 | 0.0644 | +0.0063 [+0.0030, +0.0098] | +0.0000 [+0.0000, +0.0000] | 0.765 | 0.321 | no |
| 4 | 0.2 | 163 | 0.391 | 0.331 | 0.0624 | +0.0085 [+0.0047, +0.0121] | +0.0000 [+0.0000, +0.0000] | 0.788 | 0.328 | no |
| 5 | 0.2 | 187 | 0.384 | 0.283 | 0.0634 | +0.0075 [+0.0036, +0.0114] | +0.0000 [+0.0000, +0.0000] | 0.772 | 0.307 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated: 2018-19 no, 2020 no, 2021-23 no, 2024 yes, 2025-26 yes.
- h = 2: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated: 2018-19 no, 2020 no, 2021-23 no, 2024 yes, 2025-26 yes.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated: 2018-19 no, 2020 no, 2021-23 no, 2024 no, 2025-26 yes.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated: 2018-19 no, 2020 no, 2021-23 no, 2024 yes, 2025-26 yes.
- h = 5: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated: 2018-19 no, 2020 no, 2021-23 no, 2024 yes, 2025-26 yes.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.477 (climatology 0.457, difference +0.0203 [-0.0817, +0.1399]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1642, ΔBrier vs climatology -0.0348 [-0.0510, -0.0203], realised minus predicted +0.0011 [-0.0528, +0.0600]; calibrated yes, beats_climatology_brier no.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.520 | 0.434 | 0.1679 | 0.2720 | +0.0168 [-0.0027, +0.0376] |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | 0.1313 | 0.0159 | +0.0235 [+0.0133, +0.0333] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0237 | 0.0000 | +0.0130 [+0.0114, +0.0148] |
| regime | 2024 | 250 | 5 | 0.200 | 0.250 | 0.0309 | 0.0200 | -0.0002 [-0.0064, +0.0045] |
| regime | 2025-26 | 249 | 29 | 0.552 | 0.571 | 0.0978 | 0.1165 | +0.0256 [+0.0003, +0.0575] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0233 | 0.0048 | +0.0080 [+0.0059, +0.0100] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0891 | 0.0031 | +0.0206 [+0.0144, +0.0267] |
| scarcity_state | 2 | 41 | 17 | 0.529 | 0.643 | 0.2311 | 0.4146 | 0.0897 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.521 | 0.436 | 0.1759 | 0.2474 | +0.0203 [+0.0030, +0.0386] |
| day_type | month_end | 150 | 17 | 0.471 | 0.571 | 0.0778 | 0.1133 | +0.0212 [+0.0029, +0.0434] |
| day_type | ordinary | 1603 | 101 | 0.554 | 0.415 | 0.0774 | 0.0630 | +0.0125 [+0.0072, +0.0187] |
| day_type | quarter_end | 31 | 9 | 0.444 | 1.000 | 0.0845 | 0.2903 | +0.0604 [-0.0440, +0.1631] |
| day_type | tax_date | 89 | 13 | 0.231 | 0.429 | 0.0819 | 0.1461 | +0.0355 [+0.0130, +0.0568] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1364 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.250 | 0.3171 | 0.2213 |

### published_v1 (baseline): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no. Not scored at horizons [2, 3, 4, 5].

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 27 | 10 | 0.370 [0.200, 0.542] | 0.368 | 6.81 | recall no, recall_above_climatology no, false_alarms no (partial horizons) |
| lead_at_least_3 | – | – | not scored at any horizon from 3 | | | |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.2 | 289 | 0.750 | 0.363 | 0.0496 | +0.0219 [+0.0139, +0.0309] | +0.0068 [+0.0022, +0.0122] | 0.898 | 0.644 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated: 2018-19 yes, 2020 no, 2021-23 no, 2024 yes, 2025-26 yes.

Tier 2 (reported only): not scored at h = 5

Tier 5 (week-ahead window): not scored at horizons [2, 3, 4, 5]

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.843 | 0.376 | 0.2612 | 0.2720 | +0.0460 [+0.0127, +0.0833] |
| regime | 2020 | 251 | 4 | 0.250 | 0.067 | 0.0935 | 0.0159 | +0.0328 [+0.0266, +0.0391] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0320 | 0.0000 | +0.0127 [+0.0111, +0.0144] |
| regime | 2024 | 250 | 5 | 0.200 | 0.250 | 0.0255 | 0.0200 | +0.0010 [-0.0043, +0.0050] |
| regime | 2025-26 | 249 | 29 | 0.586 | 0.415 | 0.1116 | 0.1165 | +0.0229 [-0.0053, +0.0574] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0287 | 0.0048 | +0.0080 [+0.0061, +0.0097] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0638 | 0.0031 | +0.0250 [+0.0189, +0.0303] |
| scarcity_state | 2 | 41 | 17 | 0.471 | 0.571 | 0.1980 | 0.4146 | +0.0840 [-0.0308, +0.2028] |
| scarcity_state | 3 | 473 | 117 | 0.821 | 0.366 | 0.2559 | 0.2474 | +0.0446 [+0.0172, +0.0763] |
| day_type | month_end | 150 | 17 | 0.941 | 0.615 | 0.1021 | 0.1133 | +0.0421 [+0.0202, +0.0713] |
| day_type | ordinary | 1603 | 101 | 0.752 | 0.323 | 0.0934 | 0.0630 | +0.0169 [+0.0088, +0.0259] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.1348 | 0.2903 | +0.0922 [+0.0137, +0.1746] |
| day_type | tax_date | 89 | 13 | 0.538 | 0.368 | 0.1164 | 0.1461 | +0.0534 [+0.0285, +0.0795] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1018 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2480 | 0.2213 |

### settlement_probit_scarcity (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no.

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 18 | 0.692 [0.524, 0.852] | 0.423 | 7.35 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 16 | 0.615 [0.438, 0.794] | 0.423 | 7.35 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.2 | 253 | 0.679 | 0.375 | 0.0535 | +0.0179 [+0.0089, +0.0281] | +0.0028 [-0.0047, +0.0106] | 0.923 | 0.587 | no |
| 2 | 0.2 | 277 | 0.683 | 0.343 | 0.0622 | +0.0089 [-0.0014, +0.0186] | -0.0011 [-0.0107, +0.0080] | 0.905 | 0.578 | no |
| 3 | 0.2 | 285 | 0.681 | 0.330 | 0.0640 | +0.0067 [-0.0038, +0.0165] | +0.0004 [-0.0095, +0.0100] | 0.899 | 0.571 | no |
| 4 | 0.2 | 270 | 0.638 | 0.326 | 0.0646 | +0.0063 [-0.0047, +0.0165] | -0.0022 [-0.0128, +0.0077] | 0.900 | 0.533 | no |
| 5 | 0.2 | 272 | 0.630 | 0.320 | 0.0655 | +0.0054 [-0.0053, +0.0154] | -0.0021 [-0.0124, +0.0074] | 0.885 | 0.524 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated: 2018-19 no, 2020 no, 2021-23 no, 2024 yes, 2025-26 no.
- h = 2: scarcity_state_0: 0.2 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated: 2018-19 no, 2020 no, 2021-23 no, 2024 yes, 2025-26 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated: 2018-19 no, 2020 no, 2021-23 no, 2024 yes, 2025-26 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated: 2018-19 yes, 2020 no, 2021-23 no, 2024 yes, 2025-26 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated: 2018-19 yes, 2020 no, 2021-23 no, 2024 yes, 2025-26 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.636 (climatology 0.457, difference +0.1787 [+0.0535, +0.2779]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0819, ΔBrier vs climatology +0.0476 [+0.0324, +0.0645], realised minus predicted +0.0380 [+0.0089, +0.0683]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.824 | 0.373 | 0.3490 | 0.2720 | +0.0285 [-0.0131, +0.0771] |
| regime | 2020 | 251 | 4 | 0.250 | 0.091 | 0.0427 | 0.0159 | +0.0301 [+0.0185, +0.0415] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0000 | 0.0000 | +0.0138 [+0.0121, +0.0158] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0027 | 0.0200 | +0.0042 [-0.0001, +0.0076] |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.562 | 0.0378 | 0.1165 | +0.0156 [+0.0008, +0.0359] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | 0.0013 | 0.0048 | +0.0095 [+0.0079, +0.0112] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0007 | 0.0031 | +0.0302 [+0.0233, +0.0371] |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | 0.0341 | 0.4146 | 0.0031 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.786 | 0.368 | 0.3144 | 0.2474 | +0.0290 [-0.0056, +0.0683] |
| day_type | month_end | 150 | 17 | 0.706 | 0.500 | 0.0967 | 0.1133 | +0.0419 [+0.0201, +0.0654] |
| day_type | ordinary | 1603 | 101 | 0.673 | 0.332 | 0.0736 | 0.0630 | +0.0114 [+0.0018, +0.0224] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | 0.2752 | 0.2903 | +0.1034 [+0.0496, +0.1529] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1210 | 0.1461 | +0.0650 [+0.0296, +0.1032] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0015 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2291 | 0.2213 |

### settlement_probit_tga (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 no.

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 18 | 0.692 [0.531, 0.850] | 0.406 | 6.88 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 13 | 0.500 [0.320, 0.682] | 0.395 | 6.85 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.2 | 259 | 0.693 | 0.375 | 0.0544 | +0.0171 [+0.0079, +0.0271] | +0.0020 [-0.0059, +0.0101] | 0.922 | 0.599 | no |
| 2 | 0.2 | 274 | 0.683 | 0.347 | 0.0635 | +0.0076 [-0.0037, +0.0177] | -0.0024 [-0.0126, +0.0073] | 0.904 | 0.580 | no |
| 3 | 0.2 | 270 | 0.667 | 0.341 | 0.0647 | +0.0060 [-0.0050, +0.0163] | -0.0004 [-0.0107, +0.0096] | 0.899 | 0.564 | no |
| 4 | 0.2 | 248 | 0.609 | 0.339 | 0.0656 | +0.0052 [-0.0062, +0.0159] | -0.0032 [-0.0147, +0.0072] | 0.898 | 0.514 | no |
| 5 | 0.2 | 245 | 0.587 | 0.331 | 0.0667 | +0.0043 [-0.0075, +0.0150] | -0.0033 [-0.0150, +0.0070] | 0.887 | 0.492 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated: 2018-19 no, 2020 yes, 2021-23 no, 2024 yes, 2025-26 no.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated: 2018-19 no, 2020 yes, 2021-23 no, 2024 yes, 2025-26 no.
- h = 3: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated: 2018-19 no, 2020 yes, 2021-23 no, 2024 yes, 2025-26 no.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated: 2018-19 yes, 2020 yes, 2021-23 no, 2024 yes, 2025-26 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated: 2018-19 yes, 2020 yes, 2021-23 no, 2024 yes, 2025-26 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.640 (climatology 0.457, difference +0.1830 [+0.0459, +0.2979]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0825, ΔBrier vs climatology +0.0470 [+0.0318, +0.0634], realised minus predicted +0.0364 [+0.0071, +0.0664]; calibrated no, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.833 | 0.370 | 0.3571 | 0.2720 | +0.0233 [-0.0225, +0.0717] |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | 0.0354 | 0.0159 | +0.0309 [+0.0201, +0.0412] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0001 | 0.0000 | +0.0138 [+0.0121, +0.0157] |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | 0.0034 | 0.0200 | +0.0046 [+0.0006, +0.0087] |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.526 | 0.0403 | 0.1165 | +0.0160 [+0.0007, +0.0369] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | 0.0020 | 0.0048 | +0.0095 [+0.0079, +0.0112] |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | 0.0002 | 0.0031 | +0.0302 [+0.0230, +0.0373] |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0338 | 0.4146 | 0.0020 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.795 | 0.368 | 0.3175 | 0.2474 | +0.0258 [-0.0092, +0.0650] |
| day_type | month_end | 150 | 17 | 0.765 | 0.542 | 0.1000 | 0.1133 | +0.0435 [+0.0208, +0.0656] |
| day_type | ordinary | 1603 | 101 | 0.673 | 0.327 | 0.0742 | 0.0630 | +0.0099 [-0.0001, +0.0206] |
| day_type | quarter_end | 31 | 9 | 0.778 | 0.583 | 0.2874 | 0.2903 | +0.1101 [+0.0557, +0.1601] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | 0.1231 | 0.1461 | +0.0689 [+0.0346, +0.1082] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0013 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2648 | 0.2213 |

### settlement_probit_timing (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes.

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 17 | 0.654 [0.500, 0.800] | 0.278 | 5.96 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.222, 0.556] | 0.278 | 5.96 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.2 | 182 | 0.514 | 0.396 | 0.0562 | +0.0153 [+0.0100, +0.0216] | +0.0002 [-0.0042, +0.0043] | 0.865 | 0.451 | no |
| 2 | 0.2 | 161 | 0.388 | 0.335 | 0.0606 | +0.0104 [+0.0069, +0.0140] | +0.0004 [-0.0016, +0.0025] | 0.819 | 0.327 | no |
| 3 | 0.2 | 208 | 0.384 | 0.255 | 0.0643 | +0.0064 [+0.0032, +0.0095] | +0.0001 [-0.0021, +0.0022] | 0.781 | 0.295 | no |
| 4 | 0.2 | 158 | 0.391 | 0.342 | 0.0614 | +0.0095 [+0.0069, +0.0124] | +0.0010 [-0.0011, +0.0032] | 0.806 | 0.331 | no |
| 5 | 0.2 | 169 | 0.406 | 0.331 | 0.0620 | +0.0089 [+0.0063, +0.0119] | +0.0014 [-0.0007, +0.0036] | 0.790 | 0.341 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 5.4 over 1035 days; regime_2021-23: 5.7 over 748 days. Calibrated: 2018-19 no, 2020 no, 2021-23 no, 2024 yes, 2025-26 yes.
- h = 2: scarcity_state_0: 1.7 over 1035 days; regime_2021-23: 1.3 over 748 days. Calibrated: 2018-19 no, 2020 no, 2021-23 no, 2024 yes, 2025-26 yes.
- h = 3: scarcity_state_0: 4.4 over 1035 days; regime_2021-23: 5.4 over 748 days. Calibrated: 2018-19 no, 2020 no, 2021-23 no, 2024 yes, 2025-26 yes.
- h = 4: scarcity_state_0: 1.2 over 1035 days; regime_2021-23: 1.3 over 748 days. Calibrated: 2018-19 no, 2020 no, 2021-23 no, 2024 yes, 2025-26 yes.
- h = 5: scarcity_state_0: 1.5 over 1035 days; regime_2021-23: 1.3 over 748 days. Calibrated: 2018-19 no, 2020 no, 2021-23 no, 2024 yes, 2025-26 yes.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.476 (climatology 0.457, difference +0.0188 [-0.0490, +0.0882]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1085, ΔBrier vs climatology +0.0209 [+0.0130, +0.0300], realised minus predicted +0.0095 [-0.0290, +0.0508]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.520 | 0.570 | 0.1678 | 0.2720 | +0.0381 [+0.0209, +0.0559] |
| regime | 2020 | 251 | 4 | 0.250 | 0.030 | 0.1515 | 0.0159 | -0.0066 [-0.0152, +0.0020] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0292 | 0.0000 | +0.0100 [+0.0088, +0.0113] |
| regime | 2024 | 250 | 5 | 0.400 | 0.250 | 0.0353 | 0.0200 | +0.0035 [+0.0012, +0.0065] |
| regime | 2025-26 | 249 | 29 | 0.552 | 0.516 | 0.0915 | 0.1165 | +0.0304 [+0.0059, +0.0624] |
| scarcity_state | 0 | 1035 | 5 | 0.400 | 0.091 | 0.0278 | 0.0048 | +0.0073 [+0.0060, +0.0086] |
| scarcity_state | 1 | 324 | 1 | 1.000 | 0.029 | 0.1096 | 0.0031 | -0.0018 [-0.0076, +0.0041] |
| scarcity_state | 2 | 41 | 17 | 0.471 | 0.667 | 0.1910 | 0.4146 | 0.1008 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.521 | 0.535 | 0.1740 | 0.2474 | +0.0369 [+0.0213, +0.0539] |
| day_type | month_end | 150 | 17 | 0.647 | 0.379 | 0.1376 | 0.1133 | +0.0236 [-0.0011, +0.0520] |
| day_type | ordinary | 1603 | 101 | 0.436 | 0.419 | 0.0641 | 0.0630 | +0.0133 [+0.0087, +0.0187] |
| day_type | quarter_end | 31 | 9 | 0.889 | 0.381 | 0.4897 | 0.2903 | -0.0068 [-0.0726, +0.0583] |
| day_type | tax_date | 89 | 13 | 0.692 | 0.333 | 0.1783 | 0.1461 | +0.0444 [+0.0274, +0.0639] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0499 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2673 | 0.2213 |

### settlement_quantile_scarcity (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes.

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 20 | 0.769 [0.609, 0.900] | 0.423 | 7.46 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 17 | 0.654 [0.500, 0.800] | 0.423 | 7.46 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.2 | 237 | 0.757 | 0.447 | 0.0478 | +0.0236 [+0.0148, +0.0337] | +0.0085 [+0.0025, +0.0152] | 0.931 | 0.682 | no |
| 2 | 0.2 | 274 | 0.662 | 0.336 | 0.0588 | +0.0122 [+0.0045, +0.0199] | +0.0022 [-0.0044, +0.0087] | 0.893 | 0.557 | no |
| 3 | 0.2 | 297 | 0.732 | 0.340 | 0.0594 | +0.0112 [+0.0029, +0.0192] | +0.0049 [-0.0030, +0.0123] | 0.905 | 0.619 | no |
| 4 | 0.2 | 287 | 0.703 | 0.338 | 0.0586 | +0.0123 [+0.0047, +0.0203] | +0.0038 [-0.0034, +0.0115] | 0.894 | 0.593 | no |
| 5 | 0.2 | 272 | 0.645 | 0.327 | 0.0575 | +0.0134 [+0.0061, +0.0207] | +0.0059 [-0.0014, +0.0132] | 0.892 | 0.539 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated: 2018-19 yes, 2020 no, 2021-23 no, 2024 yes, 2025-26 yes.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated: 2018-19 yes, 2020 no, 2021-23 no, 2024 yes, 2025-26 yes.
- h = 3: scarcity_state_0: 0.7 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated: 2018-19 yes, 2020 no, 2021-23 no, 2024 yes, 2025-26 yes.
- h = 4: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated: 2018-19 yes, 2020 no, 2021-23 no, 2024 yes, 2025-26 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated: 2018-19 yes, 2020 no, 2021-23 no, 2024 yes, 2025-26 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.603 (climatology 0.457, difference +0.1461 [-0.0273, +0.2957]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0773, ΔBrier vs climatology +0.0521 [+0.0361, +0.0692], realised minus predicted +0.0170 [-0.0082, +0.0413]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.833 | 0.472 | 0.3012 | 0.2720 | +0.0504 [+0.0145, +0.0914] |
| regime | 2020 | 251 | 4 | 0.250 | 0.059 | 0.0629 | 0.0159 | +0.0237 [+0.0104, +0.0359] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0027 | 0.0000 | +0.0136 [+0.0118, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0119 | 0.0200 | +0.0019 [-0.0032, +0.0055] |
| regime | 2025-26 | 249 | 29 | 0.655 | 0.514 | 0.0961 | 0.1165 | +0.0350 [+0.0060, +0.0722] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0060 | 0.0048 | +0.0088 [+0.0070, +0.0105] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0216 | 0.0031 | +0.0280 [+0.0219, +0.0343] |
| scarcity_state | 2 | 41 | 17 | 0.588 | 0.625 | 0.2780 | 0.4146 | +0.1264 [+0.0034, +0.2642] |
| scarcity_state | 3 | 473 | 117 | 0.812 | 0.448 | 0.2813 | 0.2474 | +0.0442 [+0.0138, +0.0788] |
| day_type | month_end | 150 | 17 | 0.941 | 0.552 | 0.1283 | 0.1133 | +0.0513 [+0.0192, +0.0837] |
| day_type | ordinary | 1603 | 101 | 0.723 | 0.406 | 0.0705 | 0.0630 | +0.0174 [+0.0089, +0.0271] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3063 | 0.2903 | +0.0652 [-0.0038, +0.1266] |
| day_type | tax_date | 89 | 13 | 0.846 | 0.647 | 0.1794 | 0.1461 | +0.0753 [+0.0330, +0.1188] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0127 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2641 | 0.2213 |

### settlement_quantile_tga (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes.

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 18 | 0.692 [0.524, 0.846] | 0.423 | 7.88 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 15 | 0.577 [0.412, 0.750] | 0.423 | 7.88 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.2 | 242 | 0.714 | 0.413 | 0.0514 | +0.0200 [+0.0113, +0.0300] | +0.0049 [-0.0011, +0.0118] | 0.919 | 0.632 | no |
| 2 | 0.2 | 280 | 0.612 | 0.304 | 0.0653 | +0.0058 [-0.0040, +0.0152] | -0.0042 [-0.0138, +0.0044] | 0.884 | 0.499 | no |
| 3 | 0.2 | 293 | 0.623 | 0.294 | 0.0670 | +0.0037 [-0.0074, +0.0133] | -0.0026 [-0.0130, +0.0066] | 0.888 | 0.504 | no |
| 4 | 0.2 | 271 | 0.645 | 0.328 | 0.0645 | +0.0064 [-0.0037, +0.0160] | -0.0021 [-0.0121, +0.0071] | 0.895 | 0.540 | no |
| 5 | 0.2 | 285 | 0.696 | 0.337 | 0.0636 | +0.0073 [-0.0044, +0.0177] | -0.0002 [-0.0114, +0.0100] | 0.886 | 0.586 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 1.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated: 2018-19 yes, 2020 no, 2021-23 no, 2024 yes, 2025-26 yes.
- h = 2: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated: 2018-19 yes, 2020 no, 2021-23 no, 2024 yes, 2025-26 yes.
- h = 3: scarcity_state_0: 0.5 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated: 2018-19 yes, 2020 no, 2021-23 no, 2024 yes, 2025-26 yes.
- h = 4: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated: 2018-19 yes, 2020 no, 2021-23 no, 2024 yes, 2025-26 no.
- h = 5: scarcity_state_0: 0.0 over 1035 days; regime_2021-23: 0.0 over 748 days. Calibrated: 2018-19 yes, 2020 no, 2021-23 no, 2024 yes, 2025-26 no.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.619 (climatology 0.457, difference +0.1618 [-0.0236, +0.3351]); meets 0.75: no, beats climatology: no.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.0845, ΔBrier vs climatology +0.0450 [+0.0248, +0.0667], realised minus predicted +0.0064 [-0.0228, +0.0363]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.775 | 0.454 | 0.3001 | 0.2720 | +0.0405 [+0.0038, +0.0837] |
| regime | 2020 | 251 | 4 | 0.250 | 0.037 | 0.0866 | 0.0159 | +0.0107 [-0.0133, +0.0304] |
| regime | 2021-23 | 748 | 0 | – | – | 0.0028 | 0.0000 | +0.0136 [+0.0119, +0.0156] |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | 0.0112 | 0.0200 | +0.0024 [-0.0024, +0.0056] |
| regime | 2025-26 | 249 | 29 | 0.655 | 0.500 | 0.0956 | 0.1165 | +0.0352 [+0.0072, +0.0689] |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | 0.0061 | 0.0048 | +0.0089 [+0.0071, +0.0106] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0438 | 0.0031 | +0.0169 [-0.0012, +0.0302] |
| scarcity_state | 2 | 41 | 17 | 0.588 | 0.625 | 0.2645 | 0.4146 | 0.1292 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.761 | 0.436 | 0.2782 | 0.2474 | +0.0370 [+0.0070, +0.0725] |
| day_type | month_end | 150 | 17 | 0.941 | 0.552 | 0.1375 | 0.1133 | +0.0425 [+0.0081, +0.0787] |
| day_type | ordinary | 1603 | 101 | 0.663 | 0.362 | 0.0732 | 0.0630 | +0.0141 [+0.0056, +0.0238] |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | 0.3041 | 0.2903 | +0.0629 [-0.0058, +0.1227] |
| day_type | tax_date | 89 | 13 | 0.846 | 0.647 | 0.1746 | 0.1461 | +0.0726 [+0.0320, +0.1167] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0086 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2670 | 0.2213 |

### settlement_quantile_timing (candidate): FAIL at +5 bp

Tier 1 no, tier 3 no, tier 5 yes.

| tier 1 | onsets | flagged | recall [90%] | climatology recall at same false alarms | worst false alarms per onset | criteria |
|---|---|---|---|---|---|---|
| lead_at_least_1 | 26 | 16 | 0.615 [0.452, 0.765] | 0.269 | 4.65 | recall yes, recall_above_climatology yes, false_alarms no |
| lead_at_least_3 | 26 | 10 | 0.385 [0.238, 0.550] | 0.266 | 4.50 | reported only; meets far recall: yes |

| h | cut-off | flags | recall | precision | Brier | ΔBrier vs climatology | ΔBrier vs persistence (tier 4) | AUROC | usefulness | tier 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.2 | 206 | 0.600 | 0.408 | 0.0524 | +0.0190 [+0.0117, +0.0277] | +0.0039 [-0.0008, +0.0091] | 0.914 | 0.530 | no |
| 2 | 0.2 | 183 | 0.482 | 0.366 | 0.0583 | +0.0128 [+0.0074, +0.0188] | +0.0028 [-0.0001, +0.0063] | 0.887 | 0.415 | no |
| 3 | 0.2 | 178 | 0.478 | 0.371 | 0.0602 | +0.0105 [+0.0059, +0.0160] | +0.0042 [+0.0009, +0.0079] | 0.874 | 0.414 | no |
| 4 | 0.2 | 169 | 0.377 | 0.308 | 0.0619 | +0.0089 [+0.0047, +0.0137] | +0.0005 [-0.0024, +0.0033] | 0.854 | 0.309 | no |
| 5 | 0.2 | 171 | 0.391 | 0.316 | 0.0622 | +0.0087 [+0.0043, +0.0136] | +0.0012 [-0.0017, +0.0041] | 0.840 | 0.324 | no |

Tier 3 detail (flags per 252 business days in the abundant stretches; calibration by regime):

- h = 1: scarcity_state_0: 5.6 over 1035 days; regime_2021-23: 6.1 over 748 days. Calibrated: 2018-19 no, 2020 no, 2021-23 no, 2024 yes, 2025-26 yes.
- h = 2: scarcity_state_0: 3.4 over 1035 days; regime_2021-23: 2.4 over 748 days. Calibrated: 2018-19 no, 2020 no, 2021-23 no, 2024 yes, 2025-26 yes.
- h = 3: scarcity_state_0: 3.7 over 1035 days; regime_2021-23: 2.4 over 748 days. Calibrated: 2018-19 no, 2020 no, 2021-23 no, 2024 yes, 2025-26 yes.
- h = 4: scarcity_state_0: 5.4 over 1035 days; regime_2021-23: 3.7 over 748 days. Calibrated: 2018-19 no, 2020 no, 2021-23 no, 2024 yes, 2025-26 yes.
- h = 5: scarcity_state_0: 5.1 over 1035 days; regime_2021-23: 3.7 over 748 days. Calibrated: 2018-19 no, 2020 no, 2021-23 no, 2024 yes, 2025-26 yes.

Tier 2 (reported only): h = 5, 81 risky dates in scarcity state >= 2, AUROC 0.579 (climatology 0.457, difference +0.1214 [+0.0387, +0.2067]); meets 0.75: no, beats climatology: yes.

Tier 5 (week-ahead window): 1869 decision days, base rate 0.152, Brier 0.1015, ΔBrier vs climatology +0.0280 [+0.0163, +0.0425], realised minus predicted +0.0144 [-0.0178, +0.0483]; calibrated yes, beats_climatology_brier yes.

By group at h = 1:

| grouping | group | days | events | recall | precision | mean predicted | realised | ΔBrier vs climatology |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.608 | 0.559 | 0.1923 | 0.2720 | +0.0522 [+0.0263, +0.0803] |
| regime | 2020 | 251 | 4 | 0.250 | 0.037 | 0.1024 | 0.0159 | +0.0049 [-0.0050, +0.0149] |
| regime | 2021-23 | 748 | 0 | – | 0.000 | 0.0197 | 0.0000 | +0.0093 [+0.0083, +0.0105] |
| regime | 2024 | 250 | 5 | 0.400 | 0.286 | 0.0289 | 0.0200 | -0.0011 [-0.0082, +0.0038] |
| regime | 2025-26 | 249 | 29 | 0.655 | 0.442 | 0.1179 | 0.1165 | +0.0320 [+0.0001, +0.0721] |
| scarcity_state | 0 | 1035 | 5 | 0.400 | 0.087 | 0.0209 | 0.0048 | +0.0056 [+0.0034, +0.0073] |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | 0.0726 | 0.0031 | +0.0068 [+0.0010, +0.0130] |
| scarcity_state | 2 | 41 | 17 | 0.647 | 0.579 | 0.3122 | 0.4146 | 0.1245 (no interval) |
| scarcity_state | 3 | 473 | 117 | 0.607 | 0.514 | 0.1927 | 0.2474 | +0.0475 [+0.0250, +0.0713] |
| day_type | month_end | 150 | 17 | 0.765 | 0.481 | 0.1291 | 0.1133 | +0.0337 [+0.0033, +0.0676] |
| day_type | ordinary | 1603 | 101 | 0.545 | 0.417 | 0.0600 | 0.0630 | +0.0165 [+0.0096, +0.0247] |
| day_type | quarter_end | 31 | 9 | 0.889 | 0.276 | 0.5501 | 0.2903 | -0.0228 [-0.0831, +0.0330] |
| day_type | tax_date | 89 | 13 | 0.615 | 0.444 | 0.1846 | 0.1461 | +0.0523 [+0.0344, +0.0732] |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0541 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2841 | 0.2213 |

