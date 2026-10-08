# Settlement-timing probit and skew-t quantile regression (track T of #374, #379)

A scratch measurement under the judge of #375 as it stood when this was scored (the bar of the first ruling:
recall of at least 70%, at most one false alarm per true day, a win over calendar climatology at the same recall). It
writes nothing into `docs/runs/`, moves no published figure and logs nothing to the live record. Scored days are
2018-06-29 to 2025-12-31; no comparison scores a locked day (`docs/decisions/lockbox.md`). The judge is being rewritten to
the replacement bar, so this is rescored on it after the resync; the forecasts are bar-independent.

**Candidates** (declared in `metadata/pressure_judge.json` and `src/repo_model/settlement_timing.py` before any score
was read): a ridge probit of `spread > tau` at +5 and +10 bp, and linear quantile regressions of SOFR − IORB on a
13-quantile grid smoothed per day into an Azzalini-Capitanio skew-t in the Adrian, Boyarchenko & Giannone way, each on
three nested input sets: `timing` (spread, Treasury settlement size, coupon settlement, days to month end,
quarter-end, tax date), `scarcity` (adds reserves with every scheduled term times reserves, #115's state and the
TGA), `tga` (adds track D's `tga_daily` and `tga_daily_change`, #377). Settlement amounts leave the inputs at
horizons of 2 or more, as in pressure model v1. All are uncalibrated, with a declared flagging cut-off of 0.2 at both
thresholds. Walk-forward on the shared fold grid (minimum history 61, refit every 21 scored days), as-of rule on every read.

**Reproduce** (scratch panel digest `24dd9d41…`, published `4ddc3882…`):

```
PYTHONPATH=src python3 -m repo_model.cli build --raw-root tests/fixtures/snapshots/funding_inputs --output PUB.csv --build-cutoff 2026-09-08T21:31:42+00:00 --decision-time 16:00:00
PYTHONPATH=src python3 scripts/pressure_v1_1.py panel --output AUG.csv
PYTHONPATH=src python3 scripts/measurement_fields.py panel --panel AUG.csv --output AUG2.csv
PYTHONPATH=src python3 scripts/settlement_timing.py run --panel AUG2.csv --published PUB.csv --candidate NAME --horizon H --output OUT/NAME_hH.json
PYTHONPATH=src python3 scripts/pressure_judge.py forecasts --panel PUB.csv --horizon H --output OUT/bench_hH.json
PYTHONPATH=src python3 scripts/pressure_judge.py judge --panel PUB.csv --output OUT/judge.json --markdown OUT/judge.md OUT/*_h?.json
```

## What it shows

At +5 bp, h = 1, flagging at 0.2 (recall, precision; Brier difference against climatology with its 90% interval):

| Model | recall | precision | AUROC | ΔBrier vs climatology |
|---|---|---|---|---|
| calendar climatology | 0.22 | 0.16 | 0.59 | n/a |
| persistence-logistic | 0.51 | 0.44 | 0.88 | +0.0151 [+0.0094, +0.0211] |
| probit, timing | 0.51 | 0.40 | 0.87 | +0.0153 [+0.0100, +0.0212] |
| probit, scarcity | 0.68 | 0.38 | 0.92 | +0.0179 [+0.0082, +0.0278] |
| probit, tga | 0.69 | 0.38 | 0.92 | +0.0171 [+0.0078, +0.0272] |
| quantile, timing | 0.60 | 0.41 | 0.91 | +0.0190 [+0.0116, +0.0271] |
| quantile, scarcity | 0.76 | 0.45 | 0.93 | +0.0236 [+0.0143, +0.0334] |
| quantile, tga | 0.71 | 0.41 | 0.92 | +0.0200 [+0.0110, +0.0298] |

- **No candidate passes the first ruling's bar at any horizon.** The closest is the skew-t quantile regression on the
  scarcity inputs at h = 1: recall 0.76 (above 0.70), precision 0.45 and 1.24 false alarms per true day (the bar
  allows 1.0), and it wins over climatology on Brier and precision.
- **The scarcity state is what adds.** Reserves, the state and the TGA lift recall at h = 1 from 0.51 to 0.68 for the
  probit and from 0.60 to 0.76 for the quantile regression. Track D's daily TGA adds nothing beyond them (recall and
  AUROC are level or lower).
- **The quantile regression beats the probit on every input set** at h = 1 on Brier, and the skew-t exceedance ranks
  well at the upper tail (AUROC 0.93).
- **At h of 2 to 5 recall holds (0.38 to 0.73) but precision falls to 0.29 to 0.37.** The Brier gain over climatology
  has an interval above zero at every horizon for the two timing candidates and the quantile regression on the
  scarcity set; for the probit and the quantile regression on the scarcity and TGA sets it includes zero at some horizons.
- **Lead time at +5 bp:** 16 to 20 of 26 onsets are flagged by the six candidates, against 8 for the persistence-logistic
  and 10 for climatology.

Each cell of the judge's output (by regime, scarcity state, pressure-day type, knowledge holdouts, lead time and the
ex post recall-floor diagnostic) is in the table below. The cut-off was fixed in the declaration; the ex post
diagnostic never decides a pass.

## Judge output, first-ruling bar

Declaration `metadata/pressure_judge.json` sha256 `194dafa0ac82…`. Scored days 2018-06-29 to 2025-12-31. Bar: recall ≥ 0.7, false alarms per true day ≤ 1.0, and a win over calendar climatology at the same recall (paired, 90% stationary bootstrap) on Brier and on precision.

### calendar_climatology (benchmark): FAIL at +5 bp

| h | cut-off | recall | precision | false alarms per true | Brier | ΔBrier vs climatology | Δprecision at same recall | AUROC | usefulness | bar |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.2 | 0.221 | 0.155 | 5.452 | 0.0714 | – | – | 0.586 | 0.124 | fail |
| 2 | 0.2 | 0.223 | 0.154 | 5.484 | 0.0711 | – | – | 0.586 | 0.125 | fail |
| 3 | 0.2 | 0.225 | 0.153 | 5.516 | 0.0707 | – | – | 0.585 | 0.126 | fail |
| 4 | 0.2 | 0.225 | 0.153 | 5.548 | 0.0708 | – | – | 0.580 | 0.125 | fail |
| 5 | 0.2 | 0.232 | 0.158 | 5.344 | 0.0709 | – | – | 0.578 | 0.133 | fail |

Ex post, never a pass: the highest cut-off that reaches the recall floor, and its precision: h = 1: cut-off 0.070, precision 0.079, false alarms per true 11.622; h = 2: cut-off 0.068, precision 0.079, false alarms per true 11.718; h = 3: cut-off 0.068, precision 0.079, false alarms per true 11.709; h = 4: cut-off 0.068, precision 0.079, false alarms per true 11.709; h = 5: cut-off 0.068, precision 0.079, false alarms per true 11.709

Lead time at +5 bp: 10 of 26 onsets flagged, mean 1.92 days.

The bar by group at h = 1:

| grouping | group | days | events | recall | precision | ΔBrier vs climatology | Δprecision | bar |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.255 | 0.310 | – | – | – |
| regime | 2020 | 251 | 4 | 0.250 | 0.013 | – | – | – |
| regime | 2021-23 | 748 | 0 | – | 0.000 | – | – | – |
| regime | 2024 | 250 | 5 | 0.400 | 0.500 | – | – | – |
| regime | 2025-26 | 249 | 29 | 0.069 | 0.500 | – | – | – |
| scarcity_state | 0 | 1035 | 5 | 0.400 | 0.057 | – | – | – |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | – | – | – |
| scarcity_state | 2 | 41 | 17 | 0.059 | 1.000 | – | – | – |
| scarcity_state | 3 | 473 | 117 | 0.239 | 0.212 | – | – | – |
| day_type | month_end | 150 | 17 | 0.294 | 0.179 | – | – | – |
| day_type | ordinary | 1603 | 101 | 0.099 | 0.103 | – | – | – |
| day_type | quarter_end | 31 | 9 | 0.889 | 0.267 | – | – | – |
| day_type | tax_date | 89 | 13 | 0.615 | 0.178 | – | – | – |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 0.600 | 1.000 | 0.4822 | 0.4822 |
| mar-2020 | 10 | 3 | 0.000 | – | 0.2213 | 0.2213 |

### persistence_logistic (benchmark): FAIL at +5 bp

| h | cut-off | recall | precision | false alarms per true | Brier | ΔBrier vs climatology | Δprecision at same recall | AUROC | usefulness | bar |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.2 | 0.507 | 0.444 | 1.254 | 0.0563 | +0.0151 [+0.0094, +0.0211] | +0.3203 [+0.2126, +0.4292] | 0.876 | 0.456 | fail |
| 2 | 0.2 | 0.453 | 0.399 | 1.508 | 0.0611 | +0.0100 [+0.0056, +0.0146] | +0.2466 [+0.1489, +0.3469] | 0.817 | 0.398 | fail |
| 3 | 0.2 | 0.406 | 0.276 | 2.625 | 0.0644 | +0.0063 [+0.0029, +0.0095] | +0.1382 [+0.0609, +0.2334] | 0.765 | 0.321 | fail |
| 4 | 0.2 | 0.391 | 0.331 | 2.019 | 0.0624 | +0.0085 [+0.0049, +0.0123] | +0.1981 [+0.1055, +0.3023] | 0.788 | 0.328 | fail |
| 5 | 0.2 | 0.384 | 0.283 | 2.528 | 0.0634 | +0.0075 [+0.0038, +0.0116] | +0.1524 [+0.0656, +0.2544] | 0.772 | 0.307 | fail |

Ex post, never a pass: the highest cut-off that reaches the recall floor, and its precision: h = 1: cut-off 0.131, precision 0.298, false alarms per true 2.357; h = 2: cut-off 0.110, precision 0.206, false alarms per true 3.859; h = 3: cut-off 0.108, precision 0.184, false alarms per true 4.449; h = 4: cut-off 0.100, precision 0.185, false alarms per true 4.392; h = 5: cut-off 0.097, precision 0.184, false alarms per true 4.439

Lead time at +5 bp: 8 of 26 onsets flagged, mean 1.35 days.

The bar by group at h = 1:

| grouping | group | days | events | recall | precision | ΔBrier vs climatology | Δprecision | bar |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.520 | 0.434 | +0.0168 [-0.0029, +0.0375] | +0.0541 [-0.0137, +0.1213] | fail |
| regime | 2020 | 251 | 4 | 0.250 | 0.167 | +0.0235 [+0.0119, +0.0333] | 0.1507 (no interval) | fail |
| regime | 2021-23 | 748 | 0 | – | – | +0.0130 [+0.0113, +0.0148] | – (no interval) | fail |
| regime | 2024 | 250 | 5 | 0.200 | 0.250 | -0.0002 [-0.0064, +0.0046] | 0.1250 (no interval) | fail |
| regime | 2025-26 | 249 | 29 | 0.552 | 0.571 | +0.0256 [+0.0013, +0.0588] | 0.2381 (no interval) | fail |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | +0.0080 [+0.0059, +0.0100] | 0.2259 (no interval) | fail |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | +0.0206 [+0.0142, +0.0268] | 0.0000 (no interval) | fail |
| scarcity_state | 2 | 41 | 17 | 0.529 | 0.643 | 0.0897 (no interval) | 0.4429 (no interval) | fail |
| scarcity_state | 3 | 473 | 117 | 0.521 | 0.436 | +0.0203 [+0.0025, +0.0390] | +0.1464 [+0.0569, +0.2488] | fail |
| day_type | month_end | 150 | 17 | 0.471 | 0.571 | +0.0212 [+0.0029, +0.0432] | +0.4286 [+0.1567, +0.6648] | fail |
| day_type | ordinary | 1603 | 101 | 0.554 | 0.415 | +0.0125 [+0.0072, +0.0186] | +0.3037 [+0.1986, +0.4101] | fail |
| day_type | quarter_end | 31 | 9 | 0.444 | 1.000 | +0.0604 [-0.0434, +0.1602] | 0.7333 (no interval) | fail |
| day_type | tax_date | 89 | 13 | 0.231 | 0.429 | +0.0355 [+0.0122, +0.0577] | 0.3117 (no interval) | fail |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.1364 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.250 | 0.3171 | 0.2213 |

### settlement_probit_scarcity (candidate): FAIL at +5 bp

| h | cut-off | recall | precision | false alarms per true | Brier | ΔBrier vs climatology | Δprecision at same recall | AUROC | usefulness | bar |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.2 | 0.679 | 0.375 | 1.663 | 0.0535 | +0.0179 [+0.0082, +0.0278] | +0.2973 [+0.2213, +0.3820] | 0.923 | 0.587 | fail |
| 2 | 0.2 | 0.683 | 0.343 | 1.916 | 0.0622 | +0.0089 [-0.0016, +0.0188] | +0.2660 [+0.1849, +0.3464] | 0.905 | 0.578 | fail |
| 3 | 0.2 | 0.681 | 0.330 | 2.032 | 0.0640 | +0.0067 [-0.0043, +0.0174] | +0.2537 [+0.1763, +0.3436] | 0.899 | 0.571 | fail |
| 4 | 0.2 | 0.638 | 0.326 | 2.068 | 0.0646 | +0.0063 [-0.0050, +0.0166] | +0.2435 [+0.1646, +0.3258] | 0.900 | 0.533 | fail |
| 5 | 0.2 | 0.630 | 0.320 | 2.126 | 0.0655 | +0.0054 [-0.0046, +0.0151] | +0.2383 [+0.1584, +0.3296] | 0.885 | 0.524 | fail |

Ex post, never a pass: the highest cut-off that reaches the recall floor, and its precision: h = 1: cut-off 0.160, precision 0.356, false alarms per true 1.806; h = 2: cut-off 0.164, precision 0.318, false alarms per true 2.143; h = 3: cut-off 0.164, precision 0.308, false alarms per true 2.247; h = 4: cut-off 0.132, precision 0.298, false alarms per true 2.351; h = 5: cut-off 0.133, precision 0.303, false alarms per true 2.299

Lead time at +5 bp: 18 of 26 onsets flagged, mean 3.08 days.

The bar by group at h = 1:

| grouping | group | days | events | recall | precision | ΔBrier vs climatology | Δprecision | bar |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.824 | 0.373 | +0.0285 [-0.0183, +0.0754] | -0.0247 [-0.0811, +0.0256] | fail |
| regime | 2020 | 251 | 4 | 0.250 | 0.091 | +0.0301 [+0.0175, +0.0409] | 0.0750 (no interval) | fail |
| regime | 2021-23 | 748 | 0 | – | – | +0.0138 [+0.0121, +0.0156] | – (no interval) | fail |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | +0.0042 [-0.0000, +0.0079] | 0.9459 (no interval) | fail |
| regime | 2025-26 | 249 | 29 | 0.310 | 0.562 | +0.0156 [+0.0003, +0.0349] | 0.3438 (no interval) | fail |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 1.000 | +0.0095 [+0.0078, +0.0111] | 0.9969 (no interval) | fail |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | +0.0302 [+0.0230, +0.0371] | – (no interval) | fail |
| scarcity_state | 2 | 41 | 17 | 0.118 | 1.000 | +0.0031 [-0.0233, +0.0585] | 0.8000 (no interval) | fail |
| scarcity_state | 3 | 473 | 117 | 0.786 | 0.368 | +0.0290 [-0.0085, +0.0671] | +0.0442 [-0.0209, +0.1078] | fail |
| day_type | month_end | 150 | 17 | 0.706 | 0.500 | +0.0419 [+0.0185, +0.0639] | +0.4030 [+0.2851, +0.5304] | pass |
| day_type | ordinary | 1603 | 101 | 0.673 | 0.332 | +0.0114 [+0.0009, +0.0220] | +0.2656 [+0.1847, +0.3560] | fail |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.667 | +0.1034 [+0.0501, +0.1522] | +0.4000 [+0.1875, +0.6300] | fail |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | +0.0650 [+0.0301, +0.1024] | 0.4795 (no interval) | fail |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0015 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2291 | 0.2213 |

### settlement_probit_tga (candidate): FAIL at +5 bp

| h | cut-off | recall | precision | false alarms per true | Brier | ΔBrier vs climatology | Δprecision at same recall | AUROC | usefulness | bar |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.2 | 0.693 | 0.375 | 1.670 | 0.0544 | +0.0171 [+0.0078, +0.0272] | +0.2960 [+0.2210, +0.3768] | 0.922 | 0.599 | fail |
| 2 | 0.2 | 0.683 | 0.347 | 1.884 | 0.0635 | +0.0076 [-0.0029, +0.0175] | +0.2698 [+0.1903, +0.3464] | 0.904 | 0.580 | fail |
| 3 | 0.2 | 0.667 | 0.341 | 1.935 | 0.0647 | +0.0060 [-0.0051, +0.0163] | +0.2550 [+0.1752, +0.3412] | 0.899 | 0.564 | fail |
| 4 | 0.2 | 0.609 | 0.339 | 1.952 | 0.0656 | +0.0052 [-0.0069, +0.0163] | +0.2596 [+0.1759, +0.3527] | 0.898 | 0.514 | fail |
| 5 | 0.2 | 0.587 | 0.331 | 2.025 | 0.0667 | +0.0043 [-0.0074, +0.0142] | +0.2541 [+0.1732, +0.3376] | 0.887 | 0.492 | fail |

Ex post, never a pass: the highest cut-off that reaches the recall floor, and its precision: h = 1: cut-off 0.192, precision 0.373, false alarms per true 1.684; h = 2: cut-off 0.179, precision 0.340, false alarms per true 1.939; h = 3: cut-off 0.162, precision 0.318, false alarms per true 2.144; h = 4: cut-off 0.105, precision 0.302, false alarms per true 2.309; h = 5: cut-off 0.111, precision 0.305, false alarms per true 2.278

Lead time at +5 bp: 18 of 26 onsets flagged, mean 2.73 days.

The bar by group at h = 1:

| grouping | group | days | events | recall | precision | ΔBrier vs climatology | Δprecision | bar |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.833 | 0.370 | +0.0233 [-0.0217, +0.0719] | -0.0285 [-0.0874, +0.0255] | fail |
| regime | 2020 | 251 | 4 | 0.250 | 0.111 | +0.0309 [+0.0195, +0.0416] | 0.0952 (no interval) | fail |
| regime | 2021-23 | 748 | 0 | – | – | +0.0138 [+0.0120, +0.0157] | – (no interval) | fail |
| regime | 2024 | 250 | 5 | 0.200 | 1.000 | +0.0046 [+0.0005, +0.0091] | 0.9459 (no interval) | fail |
| regime | 2025-26 | 249 | 29 | 0.345 | 0.526 | +0.0160 [+0.0009, +0.0374] | 0.2763 (no interval) | fail |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.333 | +0.0095 [+0.0078, +0.0113] | 0.3303 (no interval) | fail |
| scarcity_state | 1 | 324 | 1 | 0.000 | – | +0.0302 [+0.0233, +0.0370] | – (no interval) | fail |
| scarcity_state | 2 | 41 | 17 | 0.176 | 1.000 | 0.0020 (no interval) | 0.6250 (no interval) | fail |
| scarcity_state | 3 | 473 | 117 | 0.795 | 0.368 | +0.0258 [-0.0111, +0.0659] | +0.0437 [-0.0229, +0.1085] | fail |
| day_type | month_end | 150 | 17 | 0.765 | 0.542 | +0.0435 [+0.0219, +0.0679] | +0.4373 [+0.3128, +0.5808] | pass |
| day_type | ordinary | 1603 | 101 | 0.673 | 0.327 | +0.0099 [-0.0002, +0.0208] | +0.2613 [+0.1805, +0.3519] | fail |
| day_type | quarter_end | 31 | 9 | 0.778 | 0.583 | +0.1101 [+0.0580, +0.1656] | +0.3167 [+0.1515, +0.5129] | pass |
| day_type | tax_date | 89 | 13 | 0.692 | 0.600 | +0.0689 [+0.0341, +0.1062] | 0.4795 (no interval) | fail |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0013 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.500 | 0.2648 | 0.2213 |

### settlement_probit_timing (candidate): FAIL at +5 bp

| h | cut-off | recall | precision | false alarms per true | Brier | ΔBrier vs climatology | Δprecision at same recall | AUROC | usefulness | bar |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.2 | 0.514 | 0.396 | 1.528 | 0.0562 | +0.0153 [+0.0100, +0.0212] | +0.2756 [+0.2130, +0.3275] | 0.865 | 0.451 | fail |
| 2 | 0.2 | 0.388 | 0.335 | 1.981 | 0.0606 | +0.0104 [+0.0069, +0.0138] | +0.2012 [+0.1361, +0.2620] | 0.819 | 0.327 | fail |
| 3 | 0.2 | 0.384 | 0.255 | 2.925 | 0.0643 | +0.0064 [+0.0035, +0.0095] | +0.1231 [+0.0668, +0.1838] | 0.781 | 0.295 | fail |
| 4 | 0.2 | 0.391 | 0.342 | 1.926 | 0.0614 | +0.0095 [+0.0069, +0.0123] | +0.2086 [+0.1378, +0.2707] | 0.806 | 0.331 | fail |
| 5 | 0.2 | 0.406 | 0.331 | 2.018 | 0.0620 | +0.0089 [+0.0062, +0.0117] | +0.1946 [+0.1263, +0.2562] | 0.790 | 0.341 | fail |

Ex post, never a pass: the highest cut-off that reaches the recall floor, and its precision: h = 1: cut-off 0.127, precision 0.328, false alarms per true 2.051; h = 2: cut-off 0.104, precision 0.211, false alarms per true 3.737; h = 3: cut-off 0.102, precision 0.159, false alarms per true 5.289; h = 4: cut-off 0.094, precision 0.183, false alarms per true 4.474; h = 5: cut-off 0.086, precision 0.167, false alarms per true 5.000

Lead time at +5 bp: 17 of 26 onsets flagged, mean 2.15 days.

The bar by group at h = 1:

| grouping | group | days | events | recall | precision | ΔBrier vs climatology | Δprecision | bar |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.520 | 0.570 | +0.0381 [+0.0210, +0.0566] | +0.1904 [+0.1186, +0.2686] | fail |
| regime | 2020 | 251 | 4 | 0.250 | 0.030 | -0.0066 [-0.0152, +0.0015] | +0.0144 [-0.0091, +0.0432] | fail |
| regime | 2021-23 | 748 | 0 | – | 0.000 | +0.0100 [+0.0088, +0.0112] | +0.0000 [+0.0000, +0.0000] | fail |
| regime | 2024 | 250 | 5 | 0.400 | 0.250 | +0.0035 [+0.0011, +0.0064] | 0.1250 (no interval) | fail |
| regime | 2025-26 | 249 | 29 | 0.552 | 0.516 | +0.0304 [+0.0058, +0.0624] | 0.2661 (no interval) | fail |
| scarcity_state | 0 | 1035 | 5 | 0.400 | 0.091 | +0.0073 [+0.0060, +0.0086] | +0.0694 [+0.0000, +0.1351] | fail |
| scarcity_state | 1 | 324 | 1 | 1.000 | 0.029 | -0.0018 [-0.0075, +0.0040] | +0.0294 [+0.0000, +0.0833] | fail |
| scarcity_state | 2 | 41 | 17 | 0.471 | 0.667 | 0.1008 (no interval) | 0.4667 (no interval) | fail |
| scarcity_state | 3 | 473 | 117 | 0.521 | 0.535 | +0.0369 [+0.0210, +0.0540] | +0.2452 [+0.1744, +0.3114] | fail |
| day_type | month_end | 150 | 17 | 0.647 | 0.379 | +0.0236 [-0.0009, +0.0497] | +0.2323 [+0.0942, +0.3692] | fail |
| day_type | ordinary | 1603 | 101 | 0.436 | 0.419 | +0.0133 [+0.0086, +0.0184] | +0.3124 [+0.2250, +0.3876] | fail |
| day_type | quarter_end | 31 | 9 | 0.889 | 0.381 | -0.0068 [-0.0802, +0.0609] | +0.1143 [+0.0468, +0.2000] | fail |
| day_type | tax_date | 89 | 13 | 0.692 | 0.333 | +0.0444 [+0.0272, +0.0647] | +0.2208 [+0.1073, +0.3608] | fail |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0499 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2673 | 0.2213 |

### settlement_quantile_scarcity (candidate): FAIL at +5 bp

| h | cut-off | recall | precision | false alarms per true | Brier | ΔBrier vs climatology | Δprecision at same recall | AUROC | usefulness | bar |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.2 | 0.757 | 0.447 | 1.236 | 0.0478 | +0.0236 [+0.0143, +0.0334] | +0.3756 [+0.3044, +0.4435] | 0.931 | 0.682 | fail |
| 2 | 0.2 | 0.662 | 0.336 | 1.978 | 0.0588 | +0.0122 [+0.0050, +0.0193] | +0.2498 [+0.1806, +0.3258] | 0.893 | 0.557 | fail |
| 3 | 0.2 | 0.732 | 0.340 | 1.941 | 0.0594 | +0.0112 [+0.0025, +0.0193] | +0.2626 [+0.1918, +0.3434] | 0.905 | 0.619 | fail |
| 4 | 0.2 | 0.703 | 0.338 | 1.959 | 0.0586 | +0.0123 [+0.0044, +0.0199] | +0.2630 [+0.1933, +0.3422] | 0.894 | 0.593 | fail |
| 5 | 0.2 | 0.645 | 0.327 | 2.056 | 0.0575 | +0.0134 [+0.0062, +0.0207] | +0.2440 [+0.1698, +0.3211] | 0.892 | 0.539 | fail |

Ex post, never a pass: the highest cut-off that reaches the recall floor, and its precision: h = 1: cut-off 0.230, precision 0.456, false alarms per true 1.194; h = 2: cut-off 0.180, precision 0.331, false alarms per true 2.020; h = 3: cut-off 0.205, precision 0.332, false alarms per true 2.010; h = 4: cut-off 0.206, precision 0.340, false alarms per true 1.938; h = 5: cut-off 0.192, precision 0.344, false alarms per true 1.907

Lead time at +5 bp: 20 of 26 onsets flagged, mean 3.23 days.

The bar by group at h = 1:

| grouping | group | days | events | recall | precision | ΔBrier vs climatology | Δprecision | bar |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.833 | 0.472 | +0.0504 [+0.0118, +0.0918] | +0.1157 [+0.0593, +0.1766] | fail |
| regime | 2020 | 251 | 4 | 0.250 | 0.059 | +0.0237 [+0.0104, +0.0363] | 0.0429 (no interval) | fail |
| regime | 2021-23 | 748 | 0 | – | – | +0.0136 [+0.0119, +0.0155] | – (no interval) | fail |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | +0.0019 [-0.0031, +0.0055] | 0.3228 (no interval) | fail |
| regime | 2025-26 | 249 | 29 | 0.655 | 0.514 | +0.0350 [+0.0071, +0.0703] | +0.2339 [+0.0814, +0.3999] | fail |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | +0.0088 [+0.0069, +0.0105] | 0.2477 (no interval) | fail |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | +0.0280 [+0.0217, +0.0341] | -0.0036 (no interval) | fail |
| scarcity_state | 2 | 41 | 17 | 0.588 | 0.625 | 0.1264 (no interval) | 0.1806 (no interval) | fail |
| scarcity_state | 3 | 473 | 117 | 0.812 | 0.448 | +0.0442 [+0.0119, +0.0783] | +0.1467 [+0.0935, +0.1976] | fail |
| day_type | month_end | 150 | 17 | 0.941 | 0.552 | +0.0513 [+0.0192, +0.0860] | +0.4430 [+0.3111, +0.5732] | pass |
| day_type | ordinary | 1603 | 101 | 0.723 | 0.406 | +0.0174 [+0.0082, +0.0271] | +0.3463 [+0.2571, +0.4296] | fail |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | +0.0652 [-0.0064, +0.1262] | +0.2788 [+0.0988, +0.4928] | fail |
| day_type | tax_date | 89 | 13 | 0.846 | 0.647 | +0.0753 [+0.0309, +0.1199] | +0.5266 [+0.3265, +0.7519] | pass |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0127 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2641 | 0.2213 |

### settlement_quantile_tga (candidate): FAIL at +5 bp

| h | cut-off | recall | precision | false alarms per true | Brier | ΔBrier vs climatology | Δprecision at same recall | AUROC | usefulness | bar |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.2 | 0.714 | 0.413 | 1.420 | 0.0514 | +0.0200 [+0.0110, +0.0298] | +0.3362 [+0.2659, +0.4052] | 0.919 | 0.632 | fail |
| 2 | 0.2 | 0.612 | 0.304 | 2.294 | 0.0653 | +0.0058 [-0.0041, +0.0155] | +0.2234 [+0.1560, +0.2993] | 0.884 | 0.499 | fail |
| 3 | 0.2 | 0.623 | 0.294 | 2.407 | 0.0670 | +0.0037 [-0.0070, +0.0136] | +0.2126 [+0.1468, +0.2861] | 0.888 | 0.504 | fail |
| 4 | 0.2 | 0.645 | 0.328 | 2.045 | 0.0645 | +0.0064 [-0.0045, +0.0157] | +0.2452 [+0.1716, +0.3235] | 0.895 | 0.540 | fail |
| 5 | 0.2 | 0.696 | 0.337 | 1.969 | 0.0636 | +0.0073 [-0.0046, +0.0175] | +0.2625 [+0.1887, +0.3417] | 0.886 | 0.586 | fail |

Ex post, never a pass: the highest cut-off that reaches the recall floor, and its precision: h = 1: cut-off 0.216, precision 0.426, false alarms per true 1.347; h = 2: cut-off 0.151, precision 0.295, false alarms per true 2.388; h = 3: cut-off 0.170, precision 0.298, false alarms per true 2.361; h = 4: cut-off 0.171, precision 0.315, false alarms per true 2.175; h = 5: cut-off 0.199, precision 0.338, false alarms per true 1.959

Lead time at +5 bp: 18 of 26 onsets flagged, mean 2.96 days.

The bar by group at h = 1:

| grouping | group | days | events | recall | precision | ΔBrier vs climatology | Δprecision | bar |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.775 | 0.454 | +0.0405 [+0.0013, +0.0806] | +0.0920 [+0.0325, +0.1525] | fail |
| regime | 2020 | 251 | 4 | 0.250 | 0.037 | +0.0107 [-0.0121, +0.0302] | 0.0211 (no interval) | fail |
| regime | 2021-23 | 748 | 0 | – | – | +0.0136 [+0.0119, +0.0155] | – (no interval) | fail |
| regime | 2024 | 250 | 5 | 0.200 | 0.333 | +0.0024 [-0.0024, +0.0057] | 0.2793 (no interval) | fail |
| regime | 2025-26 | 249 | 29 | 0.655 | 0.500 | +0.0352 [+0.0071, +0.0717] | +0.2297 [+0.0309, +0.4136] | fail |
| scarcity_state | 0 | 1035 | 5 | 0.200 | 0.250 | +0.0089 [+0.0072, +0.0105] | 0.2472 (no interval) | fail |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | +0.0169 [+0.0002, +0.0303] | -0.0036 (no interval) | fail |
| scarcity_state | 2 | 41 | 17 | 0.588 | 0.625 | 0.1292 (no interval) | 0.1806 (no interval) | fail |
| scarcity_state | 3 | 473 | 117 | 0.761 | 0.436 | +0.0370 [+0.0050, +0.0696] | +0.1333 [+0.0712, +0.1946] | fail |
| day_type | month_end | 150 | 17 | 0.941 | 0.552 | +0.0425 [+0.0084, +0.0816] | +0.4433 [+0.3189, +0.5716] | pass |
| day_type | ordinary | 1603 | 101 | 0.663 | 0.362 | +0.0141 [+0.0057, +0.0235] | +0.2982 [+0.2193, +0.3784] | fail |
| day_type | quarter_end | 31 | 9 | 0.667 | 0.545 | +0.0629 [-0.0099, +0.1250] | +0.2788 [+0.0943, +0.4897] | fail |
| day_type | tax_date | 89 | 13 | 0.846 | 0.647 | +0.0726 [+0.0325, +0.1161] | +0.5266 [+0.3276, +0.7812] | pass |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0086 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2670 | 0.2213 |

### settlement_quantile_timing (candidate): FAIL at +5 bp

| h | cut-off | recall | precision | false alarms per true | Brier | ΔBrier vs climatology | Δprecision at same recall | AUROC | usefulness | bar |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.2 | 0.600 | 0.408 | 1.452 | 0.0524 | +0.0190 [+0.0116, +0.0271] | +0.3199 [+0.2497, +0.3752] | 0.914 | 0.530 | fail |
| 2 | 0.2 | 0.482 | 0.366 | 1.731 | 0.0583 | +0.0128 [+0.0074, +0.0186] | +0.2247 [+0.1498, +0.2862] | 0.887 | 0.415 | fail |
| 3 | 0.2 | 0.478 | 0.371 | 1.697 | 0.0602 | +0.0105 [+0.0057, +0.0157] | +0.2314 [+0.1669, +0.2902] | 0.874 | 0.414 | fail |
| 4 | 0.2 | 0.377 | 0.308 | 2.250 | 0.0619 | +0.0089 [+0.0047, +0.0140] | +0.1785 [+0.1106, +0.2446] | 0.854 | 0.309 | fail |
| 5 | 0.2 | 0.391 | 0.316 | 2.167 | 0.0622 | +0.0087 [+0.0044, +0.0135] | +0.1828 [+0.1164, +0.2470] | 0.840 | 0.324 | fail |

Ex post, never a pass: the highest cut-off that reaches the recall floor, and its precision: h = 1: cut-off 0.159, precision 0.387, false alarms per true 1.582; h = 2: cut-off 0.136, precision 0.324, false alarms per true 2.091; h = 3: cut-off 0.107, precision 0.249, false alarms per true 3.010; h = 4: cut-off 0.092, precision 0.229, false alarms per true 3.371; h = 5: cut-off 0.101, precision 0.237, false alarms per true 3.216

Lead time at +5 bp: 16 of 26 onsets flagged, mean 2.04 days.

The bar by group at h = 1:

| grouping | group | days | events | recall | precision | ΔBrier vs climatology | Δprecision | bar |
|---|---|---|---|---|---|---|---|---|
| regime | 2018-19 | 375 | 102 | 0.608 | 0.559 | +0.0522 [+0.0264, +0.0802] | +0.1829 [+0.1093, +0.2535] | fail |
| regime | 2020 | 251 | 4 | 0.250 | 0.037 | +0.0049 [-0.0057, +0.0150] | +0.0211 [-0.0088, +0.0617] | fail |
| regime | 2021-23 | 748 | 0 | – | 0.000 | +0.0093 [+0.0082, +0.0104] | +0.0000 [+0.0000, +0.0000] | fail |
| regime | 2024 | 250 | 5 | 0.400 | 0.286 | -0.0011 [-0.0079, +0.0038] | 0.1948 (no interval) | fail |
| regime | 2025-26 | 249 | 29 | 0.655 | 0.442 | +0.0320 [+0.0014, +0.0702] | 0.0530 (no interval) | fail |
| scarcity_state | 0 | 1035 | 5 | 0.400 | 0.087 | +0.0056 [+0.0036, +0.0072] | +0.0822 [+0.0000, +0.1636] | fail |
| scarcity_state | 1 | 324 | 1 | 0.000 | 0.000 | +0.0068 [+0.0008, +0.0127] | -0.0037 [-0.0123, +0.0000] | fail |
| scarcity_state | 2 | 41 | 17 | 0.647 | 0.579 | +0.1245 [-0.0218, +0.2774] | 0.3789 (no interval) | fail |
| scarcity_state | 3 | 473 | 117 | 0.607 | 0.514 | +0.0475 [+0.0248, +0.0714] | +0.2115 [+0.1368, +0.2796] | fail |
| day_type | month_end | 150 | 17 | 0.765 | 0.481 | +0.0337 [+0.0025, +0.0696] | +0.3704 [+0.2224, +0.5186] | fail |
| day_type | ordinary | 1603 | 101 | 0.545 | 0.417 | +0.0165 [+0.0094, +0.0238] | +0.3432 [+0.2580, +0.4123] | fail |
| day_type | quarter_end | 31 | 9 | 0.889 | 0.276 | -0.0228 [-0.0780, +0.0326] | +0.0092 [+0.0000, +0.0278] | fail |
| day_type | tax_date | 89 | 13 | 0.615 | 0.444 | +0.0523 [+0.0346, +0.0721] | +0.3240 [+0.1006, +0.5113] | fail |

Knowledge holdouts at h = 1 (descriptive):

| window | days | events | recall | precision | Brier | climatology Brier |
|---|---|---|---|---|---|---|
| sep-2019 | 5 | 5 | 1.000 | 1.000 | 0.0541 | 0.4822 |
| mar-2020 | 10 | 3 | 0.333 | 0.333 | 0.2841 | 0.2213 |

