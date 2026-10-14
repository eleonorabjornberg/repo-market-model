# Confirmation design study: result (H1 step 2, #733)

<!-- generated: scripts/confirmation_design.py report; never hand-edited -->

The rule is [`confirmation-design-733.md`](confirmation-design-733.md) (committed before the study ran, sha256 `c5ae19422e5d…`). Development data only: 1868 decision days from 2018-06-29 to 2025-12-23 (1429 from 2020-04-03), panel `4ddc3882…`; no day after 2025-12-31 is read. It is a design study: no verdict, nothing registered. Power figures are upper bounds (the B2 half and futility stopping are not simulated). Paths per scenario: 2000; calibration windows per pair and per N: 20000.

## Designs, size and power

Size is the false-detection share by the last look under no true difference, without the MME gate. Power is the gated detection share by the last look. Intervals are Monte Carlo (one standard error shown).

| design | days | leads | scale | c at look 2 / 3 | size, full | size, post-2020 | power at 3% | power at 10% | smallest skill at 80% | admissible |
|---|---|---|---|---|---|---|---|---|---|---|
| D0 | 250 | 1 to 5 | raw | 9.36 / 5.49 | 0.0% | 0.2% | 0.0% ± 0.0% | 0.0% | none on the grid | yes |
| D1 | 375 | 1 to 5 | raw | 8.77 / 5.28 | 0.0% | 0.1% | 0.0% ± 0.0% | 0.0% | none on the grid | yes |
| D2 | 500 | 1 to 5 | raw | 8.32 / 5.29 | 0.0% | 0.1% | 0.0% ± 0.0% | 0.0% | none on the grid | yes |
| D3 | 250 | 1 | raw | 8.44 / 4.63 | 0.0% | 1.7% | 0.1% ± 0.1% | 0.1% | none on the grid | yes |
| D4 | 250 | 1 to 5 | standardized | 6.24 / 2.59 | 8.4% | 13.1% | 11.0% ± 0.7% | 14.2% | none on the grid | no |
| D5 | 375 | 1 to 5 | standardized | 5.07 / 2.29 | 9.9% | 13.4% | 12.6% ± 0.7% | 16.5% | none on the grid | no |

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

## Smallest true skill detected with 80% power (Full history, gated, last look)

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

## Question for Eleonora (marked; this page decides nothing)

Do you want to change the confirmation design, or the MME, and if so which? If the recommended design stands, a draft decision record is the next step; it would be a protocol change under §13 of `docs/decisions/scoring-protocol.md`, motivated by this synthetic demonstration and by no candidate's result. Whether a design that does not reach 80% power at 3% is acceptable, or the MME should rise to the smallest skill each design detects, is yours.
