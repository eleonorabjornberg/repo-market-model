# Quarter-ends: why v2 misses them, and what a remedy can and cannot do (#327)

Status: a diagnosis and a reported-only look, by the pull request that closes #327. It changes no published
record and does not change v2. Whether a remedy joins v2 is Eleonora's decision, asked in the "Publish?" issue
linked from that pull request. Every figure is on days through 2025-12-31 (`docs/decisions/lockbox.md`); the code
is `scripts/quarter_end_remedy.py`, the figures are in `docs/pivot/evidence/quarter-end-remedy/`.

## Diagnosis (v2 at h = 1, quarter-end days, 2018-06-29 to 2025-12-31)

`diagnosis.json`, one row per group of quarter-end days. The bands are v2's, an outcome on an edge counting one
half inside. "Median bias" is the median of y - q50 in basis points. The last two columns are ex-post
counterfactuals that read the group's own outcomes, so they are diagnostics and not remedies: the 50% band's
coverage if every vector were shifted by the group's median bias, and if it were also widened by the factor that
makes its 50% band exact.

| Group | Days | 50% band | 90% band | Above q95 | Median bias | Median half-IQR | Shift only: 50% | Shift and width: factor, 50% |
|---|---|---|---|---|---|---|---|---|
| all | 31 | 25.8% | 77.4% | 22.6% | +1.99 bp | 1.17 bp | 12.9% | x3.12, 41.9% |
| 2018-19 | 7 | 14.3% | 57.1% | 42.9% | +20.98 bp | 2.86 bp | 28.6% | x4.67, 42.9% |
| 2020 | 4 | 25.0% | 100.0% | 0.0% | -1.48 bp | 1.16 bp | 50.0% | x1.70, 75.0% |
| 2021-23 | 12 | 41.7% | 100.0% | 0.0% | -0.02 bp | 0.44 bp | 41.7% | x2.49, 50.0% |
| 2024 | 4 | 25.0% | 75.0% | 25.0% | +4.86 bp | 1.32 bp | 0.0% | x2.73, 50.0% |
| 2025 | 4 | 0.0% | 25.0% | 75.0% | +8.20 bp | 4.13 bp | 75.0% | x1.00, 75.0% |

Every cell above has under 20 days except "all", so no interval is given for it ("too few days"); the counts
are descriptions, not tests.

What this says:

1. **Both a level shift and a band that is too narrow, and neither is constant.** The quarter-end outcome sits
   above v2's median in 2018-19 (+21 bp, 43% of days above q95), within 1.5 bp of it in 2020-23, and above
   it again in 2024-25 (+5 and +8 bp). A shift by the group's median repairs the 2025 cell (0% to 75%) and breaks
   the 2024 one (25% to 0%): the shift that is right for one regime is the wrong sign or size for the next.
2. **The band is too narrow in every regime.** Even after centring, the 50% band needs to be 1.7 to 4.7 times wider
   in all but 2025 to be right (x3.12 over all 31 days), and 90% bands after widening cover 90.3% of all days.
   The quarter-end outcomes are far more dispersed than v2's band for them.
3. **The 90% band misses by being too narrow on the high side**: 22.6% of quarter-end outcomes are above q95 (5% is
   right), against 0% in 2020-23. The misses are in the pressure regimes (2018-19, 2024-25).
4. **The quarter-end bias changes sign with the regime**, which is why a location term estimated across all earlier
   quarter-ends carries one regime's bias into the next (below).

The per-quarter-end rows are in `diagnosis.json` (`per_quarter_end`).

## Remedies, declared before scoring

All are turn layers on v2's own vectors, on quarter-end days only, estimated across every earlier quarter-end
whose label was public at the day's anchor (no trees, no new panel column). The candidates, declared in
commits before any was scored: `qe_shift` (location, the median past bias), `turn_pool` (that shift pooled with the
month-end turns, a size term), `qe_shift_width` (the shift and a width factor), `qe_empirical` (a separate small
model: the earlier quarter-ends' empirical residual quantiles), and, added after reading this diagnosis and before
any candidate was scored, `qe_shift_recent` and `qe_shift_width_recent` (the same on the last four quarter-ends
only). "Days to quarter-end on the market calendar" as a panel column was declared and not built: it is a new
panel digest, her decision.

The rule (`SELECTION`): a candidate is eligible if its paired CRPS gain over v2 on the inner block (2018-06-29 to
2022-12-31) is above 0; the lowest inner CRPS leads, and a simpler eligible candidate wins if its paired difference
against the leader has a 90% interval including 0; if none is eligible, v2 stays as it is.

## The choice, on 2018-2022 only (`choice.json`)

Every remedy has a negative paired CRPS gain on the inner block (the best, `turn_pool`, -0.017 [-0.041, +0.009]
bp; the worst, `qe_shift_width`, -0.052 [-0.095, -0.012]), so **none is eligible and the choice is v2 without a
remedy** (`CHOSEN_REMEDY = "base"`). On the 19 inner quarter-ends the shift remedies move the 50% band from 31.6%
to 0-5%: the median of earlier quarter-ends is the wrong location for the next one, because of the sign change
in the diagnosis.

## The labelled look at 2023-2025 (`report.json`)

Not a test: the remedy was chosen on 2018-2022 and those days chose nothing, but 2023-2025 was read by every
earlier look at v2 and by the diagnosis above, so these figures are exploratory (selection-adjusted uncertainty
not computed). Paired gain = CRPS(v2) - CRPS(v2 with the remedy), per day; a positive mean favours the remedy.
Cells under 20 days carry no interval ("too few days"); persistence's CRPS is as-of persistence at h = 1.

| Cell (2023-2025) | Days | v2: 50% / 90% band | v2 CRPS | `qe_shift_recent`: 50% / 90%, CRPS | `qe_shift_width_recent`: 50% / 90%, CRPS | Persistence CRPS |
|---|---|---|---|---|---|---|
| Quarter-end | 12 | 16.7% / 66.7% | 3.75 | 33.3% / 91.7%, 2.50 | 50.0% / 91.7%, 2.78 | 3.70 |
| Year-end | 3 | 33.3% / 66.7% | 3.85 | 66.7% / 100%, 2.81 | 66.7% / 100%, 2.81 | |
| Tax-date | 35 | 48.6% / 85.7% | 1.65 | unchanged | unchanged | |
| Month-end | 64 | 54.7% / 84.4% | 1.78 | unchanged | unchanged | |
| Ordinary | 637 | 50.2% / 91.5% | 1.22 | unchanged | unchanged | |
| All | 748 | 50.0% / 90.2% | 1.326 | 50.3% / 90.6%, 1.306 | 50.5% / 90.6%, 1.311 | 1.636 |

Pooled paired CRPS gain over v2 (90% interval, stationary bootstrap, mean block 2): `qe_shift_recent` +0.020
[+0.006, +0.039], `qe_shift_width_recent` +0.016 [+0.003, +0.033], `qe_shift` +0.015 [+0.005, +0.027],
`turn_pool` +0.012 [+0.004, +0.022], `qe_empirical` +0.009 [0.000, +0.023], `qe_shift_width` +0.004
[-0.007, +0.016]. The gain is carried by the twelve quarter-end days (the tax-date, month-end and ordinary cells
are identical by construction), mostly by the four of 2025, where the bias was +8 bp and the recent remedies had
learned it from the 2024 quarter-ends. By regime (quarter-end days only, four each): the remedies are unchanged in 2021-23, gain
+0.47 (`qe_shift_recent`) in 2024 and +3.28 in 2025.

## What this does and does not show

- **The inner block, which chose, says no remedy helps.** The look at 2023-2025 says the recent-window ones would
  have, on twelve days in two pressure years. Both are true: a remedy that tracks the last year's quarter-end bias
  helps when the regime persists (2024-25) and hurts at a regime change (2020-22 after 2018-19), and the inner
  block, which contains the changes, penalises it. The look cannot settle which regime comes next.
- **None of this is evidence for v2.** The look is exploratory and the days are few. Only a live record could show
  that a remedy is better. The 90% band's quarter-end miss (above q95 in 22.6% of days) is not repaired by a
  location term alone: the width factor is what lifts the 90% band, and it is the term the inner block liked
  least.
- **v2 and every published record are unchanged.** No remedy is in the published declaration.
