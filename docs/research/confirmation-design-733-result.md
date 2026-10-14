# Confirmation design study: result (H1 step 2, #733)

<!-- generated: scripts/confirmation_design.py report; never hand-edited -->

The rule is [`confirmation-design-733.md`](confirmation-design-733.md) (committed before the study ran, sha256 `c5ae19422e5d…`). Development data only: 1868 decision days from 2018-06-29 to 2025-12-23 (1429 from 2020-04-03), panel `4ddc3882…`; no day after 2025-12-31 is read. It is a design study: no verdict, nothing registered. Power figures are upper bounds (the B2 half and futility stopping are not simulated). Paths per scenario: 2000; calibration windows per pair and per N: 20000.

## Designs, size and power

Size is the false-detection share by the last look under no true difference, without the MME gate. Power is the gated detection share by the last look. Every share is shown with its Monte Carlo standard error.

| design | days | leads | scale | c at look 2 / 3 | size, full | size, post-2020 | power at 3%, full | power at 10%, full | power at 3%, post-2020 | power at 10%, post-2020 | smallest skill at 80% | admissible |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D0 | 250 | 1 to 5 | raw | 9.36 / 5.49 | 0.0% ± 0.0% | 0.2% ± 0.1% | 0.0% ± 0.0% | 0.0% ± 0.0% | 0.3% ± 0.1% | 0.7% ± 0.2% | none on the grid | yes |
| D1 | 375 | 1 to 5 | raw | 8.77 / 5.28 | 0.0% ± 0.0% | 0.1% ± 0.1% | 0.0% ± 0.0% | 0.0% ± 0.0% | 0.2% ± 0.1% | 0.6% ± 0.2% | none on the grid | yes |
| D2 | 500 | 1 to 5 | raw | 8.32 / 5.29 | 0.0% ± 0.0% | 0.1% ± 0.1% | 0.0% ± 0.0% | 0.0% ± 0.0% | 0.2% ± 0.1% | 0.5% ± 0.2% | none on the grid | yes |
| D3 | 250 | 1 | raw | 8.44 / 4.63 | 0.0% ± 0.0% | 1.7% ± 0.3% | 0.1% ± 0.1% | 0.1% ± 0.0% | 2.6% ± 0.4% | 3.9% ± 0.4% | none on the grid | yes |
| D4 | 250 | 1 to 5 | standardized | 6.24 / 2.59 | 8.4% ± 0.6% | 13.1% ± 0.8% | 11.0% ± 0.7% | 14.2% ± 0.8% | 14.4% ± 0.8% | 19.4% ± 0.9% | none on the grid | no |
| D5 | 375 | 1 to 5 | standardized | 5.07 / 2.29 | 9.9% ± 0.7% | 13.4% ± 0.8% | 12.6% ± 0.7% | 16.5% ± 0.8% | 16.2% ± 0.8% | 23.2% ± 0.9% | none on the grid | no |

## Power by look

Gated detection share by each look (look 1 is never read), with the mean days to first detection.

| design | scenario | look 2 | look 3 | mean days to detection |
|---|---|---|---|---|
| D0 | 3%, full | 0.0% | 0.0% | none |
| D0 | 3%, post-2020 | 0.0% | 0.3% | 250 |
| D0 | 10%, full | 0.0% | 0.0% | none |
| D0 | 10%, post-2020 | 0.1% | 0.7% | 232 |
| D0 | 3%, full, noise 0.5 | 0.0% | 0.0% | none |
| D0 | 10%, full, noise 0.5 | 0.0% | 0.0% | none |
| D1 | 3%, full | 0.0% | 0.0% | none |
| D1 | 3%, post-2020 | 0.0% | 0.2% | 375 |
| D1 | 10%, full | 0.0% | 0.0% | none |
| D1 | 10%, post-2020 | 0.1% | 0.6% | 359 |
| D1 | 3%, full, noise 0.5 | 0.0% | 0.0% | none |
| D1 | 10%, full, noise 0.5 | 0.0% | 0.0% | none |
| D2 | 3%, full | 0.0% | 0.0% | none |
| D2 | 3%, post-2020 | 0.0% | 0.2% | 500 |
| D2 | 10%, full | 0.0% | 0.0% | none |
| D2 | 10%, post-2020 | 0.0% | 0.5% | 500 |
| D2 | 3%, full, noise 0.5 | 0.0% | 0.0% | none |
| D2 | 10%, full, noise 0.5 | 0.0% | 0.0% | none |
| D3 | 3%, full | 0.0% | 0.1% | 250 |
| D3 | 3%, post-2020 | 0.4% | 2.6% | 233 |
| D3 | 10%, full | 0.0% | 0.1% | 250 |
| D3 | 10%, post-2020 | 0.3% | 3.9% | 240 |
| D3 | 3%, full, noise 0.5 | 0.0% | 0.1% | 250 |
| D3 | 10%, full, noise 0.5 | 0.0% | 0.0% | none |
| D4 | 3%, full | 1.1% | 11.0% | 238 |
| D4 | 3%, post-2020 | 2.3% | 14.4% | 230 |
| D4 | 10%, full | 1.6% | 14.2% | 236 |
| D4 | 10%, post-2020 | 2.5% | 19.4% | 234 |
| D4 | 3%, full, noise 0.5 | 1.6% | 12.6% | 234 |
| D4 | 10%, full, noise 0.5 | 2.1% | 22.1% | 238 |
| D5 | 3%, full | 1.8% | 12.6% | 347 |
| D5 | 3%, post-2020 | 2.4% | 16.2% | 348 |
| D5 | 10%, full | 1.7% | 16.5% | 356 |
| D5 | 10%, post-2020 | 3.6% | 23.2% | 346 |
| D5 | 3%, full, noise 0.5 | 2.0% | 14.5% | 349 |
| D5 | 10%, full, noise 0.5 | 3.1% | 27.9% | 354 |

## Size by look

| design | scenario | gate | look 2 | look 3 |
|---|---|---|---|---|
| D0 | size, full | none | 0.0% | 0.0% |
| D0 | size, full | MME | 0.0% | 0.0% |
| D0 | size, post-2020 | none | 0.1% | 0.2% |
| D0 | size, post-2020 | MME | 0.1% | 0.2% |
| D1 | size, full | none | 0.0% | 0.0% |
| D1 | size, full | MME | 0.0% | 0.0% |
| D1 | size, post-2020 | none | 0.0% | 0.1% |
| D1 | size, post-2020 | MME | 0.0% | 0.1% |
| D2 | size, full | none | 0.0% | 0.0% |
| D2 | size, full | MME | 0.0% | 0.0% |
| D2 | size, post-2020 | none | 0.0% | 0.1% |
| D2 | size, post-2020 | MME | 0.0% | 0.1% |
| D3 | size, full | none | 0.0% | 0.0% |
| D3 | size, full | MME | 0.0% | 0.0% |
| D3 | size, post-2020 | none | 0.2% | 1.7% |
| D3 | size, post-2020 | MME | 0.2% | 1.7% |
| D4 | size, full | none | 0.6% | 8.4% |
| D4 | size, full | MME | 0.6% | 8.4% |
| D4 | size, post-2020 | none | 1.8% | 13.1% |
| D4 | size, post-2020 | MME | 1.8% | 13.1% |
| D5 | size, full | none | 0.5% | 9.9% |
| D5 | size, full | MME | 0.5% | 9.9% |
| D5 | size, post-2020 | none | 2.4% | 13.4% |
| D5 | size, post-2020 | MME | 2.4% | 13.4% |

## Gated power by true skill (Full history, last look); the smallest skill with 80% power is the first cell at or above 80%

| design | 3.0% | 5.0% | 7.5% | 10.0% | 15.0% | 20.0% | 30.0% |
|---|---|---|---|---|---|---|---|
| D0 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| D1 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| D2 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.1% |
| D3 | 0.1% | 0.1% | 0.1% | 0.1% | 0.2% | 0.2% | 0.3% |
| D4 | 11.0% | 11.2% | 13.1% | 14.2% | 17.3% | 19.7% | 28.2% |
| D5 | 12.6% | 12.8% | 16.0% | 16.5% | 20.5% | 27.2% | 35.9% |

## Reading (§7)

Admissible designs (size at most 5% on both histories): D0, D1, D2, D3.
Admissible designs with 80% power at 3%: none.

**Recommended design: D3** (250 days).

Trade-off against D0 (now in force, 250 days): power at 3% 0.0% → 0.1%, at 10% 0.0% → 0.1%; size on the full history 0.0% → 0.0%; days 250 → 250.

**No admissible design reaches 80.0% power at 3%.** The pick above is the highest power among the admissible designs (0.1%), not a design with useful power; on the rule's own reading no design on the list can confirm the MME.

## Rulings on the questions this page asked (this page decides nothing)

Eleonora ruled on 14 October 2026 on this page's two questions. The reading of the critical value is already decided: reading (b), the value calibrated on each comparison (her ruling on PR #695, Q-E, 13 October); the largest-across-comparisons value that `scoring_protocol.CRITICAL_VALUES` holds on main is in force only until #737 applies reading (b) there. The side-by-side table of the two readings below stays. Whether a design that does not reach 80% power at 3% is acceptable, and the MME, are superseded: she has asked for power to be tested a different way, an empirical replay on real forecast pairs with three test families and a matched null generator, in #754 (H1 step 3). This page remains a study of the six declared designs and answers neither question.

## Post-hoc addendum (written after the figures above were seen)

Rule: [`confirmation-design-733-addendum.md`](confirmation-design-733-addendum.md) (sha256 `9517b4c4f713…`). It changes none of the figures above and not the recommendation above.

### Reading (b): the critical value calibrated on S(B2) - S(B1) alone

Same designs, paths, seeds and gate. The value at looks 2 and 3 is the one calibrated on that single comparison (PR #695, Q-E (b)), not the largest across the four.

| design | days | c at look 2 / 3 | size, full | size, post-2020 | power at 3%, full | power at 10%, full | power at 3%, post-2020 | power at 10%, post-2020 | smallest skill at 80% | admissible |
|---|---|---|---|---|---|---|---|---|---|---|
| D0 | 250 | 3.43 / 2.50 | 0.2% ± 0.1% | 11.5% ± 0.7% | 1.1% ± 0.2% | 2.8% ± 0.4% | 14.3% ± 0.8% | 19.7% ± 0.9% | none on the grid | no |
| D1 | 375 | 3.35 / 2.55 | 0.4% ± 0.1% | 9.1% ± 0.6% | 0.4% ± 0.1% | 1.9% ± 0.3% | 11.6% ± 0.7% | 17.2% ± 0.8% | none on the grid | no |
| D2 | 500 | 3.38 / 2.62 | 0.2% ± 0.1% | 6.9% ± 0.6% | 0.7% ± 0.2% | 1.0% ± 0.2% | 9.0% ± 0.6% | 15.8% ± 0.8% | none on the grid | no |
| D3 | 250 | 3.16 / 2.33 | 1.9% ± 0.3% | 16.9% ± 0.8% | 2.7% ± 0.4% | 5.1% ± 0.5% | 21.8% ± 0.9% | 25.9% ± 1.0% | none on the grid | no |
| D4 | 250 | 2.61 / 1.76 | 23.8% ± 1.0% | 26.7% ± 1.0% | 27.0% ± 1.0% | 32.9% ± 1.1% | 30.2% ± 1.0% | 38.7% ± 1.1% | none on the grid | no |
| D5 | 375 | 2.64 / 1.79 | 20.1% ± 0.9% | 23.3% ± 0.9% | 24.3% ± 1.0% | 30.9% ± 1.0% | 25.7% ± 1.0% | 36.4% ± 1.1% | none on the grid | no |

Check against PR #695's Q-E table (reading (b), post-2020 history, 250 days, D0's rule): PR #695 reports 14.0% power at 3%, 19.2% at 10% and 11.7% false detections; this study's D0 gives 14.3%, 19.7% and 11.5% (a different pool: it ends on 2025-12-31 and PR #695's on 2026-09-03). The full-history columns differ from the post-2020 ones because the full history holds one September 2019 day that the post-2020 history does not.

Admissible at reading (b): none. With 80% power at 3%: none. The rule of §7 applied to reading (b) recommends: none.

### Size under the calibration's own generator

False-detection share by the last look under no true difference, without the MME gate, under the main study's calibrated values. Stationary: geometric blocks (the paths above). Circular: fixed blocks of 10 days, as the calibration's windows.

| design | stationary, full | circular, full | stationary, post-2020 | circular, post-2020 |
|---|---|---|---|---|
| D0 | 0.0% | 0.0% | 0.2% | 0.2% |
| D1 | 0.0% | 0.0% | 0.1% | 0.0% |
| D2 | 0.0% | 0.0% | 0.1% | 0.1% |
| D3 | 0.0% | 0.0% | 1.7% | 0.9% |
| D4 | 8.4% | 4.2% | 13.1% | 7.3% |
| D5 | 9.9% | 4.8% | 13.4% | 7.2% |

### Ruling on the post-hoc question

Decided, not asked: reading (b) is the reading confirmation uses (Eleonora's ruling on PR #695, Q-E, 13 October 2026), and #737 applies it to `CRITICAL_VALUES`; the largest-across-comparisons value is in force on main only until #737 merges. The first holds size and has almost no power at any skill on the grid; the second has the power shown above and the size shown above.
