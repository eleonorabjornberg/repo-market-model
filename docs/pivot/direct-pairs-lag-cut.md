# The direct-pairs twin re-scored with the lag series cut at 2025-12-31 (#470)

Follows #457. `scripts/direct_pairs_twin.py` built its lag series from the whole panel, so the lag at k = −3 for the last three scored
days of 2025, and the turning-point flag of 2025-12-31 itself, read 2026 spreads that `docs/decisions/lockbox.md` holds back. The
series is now cut at 2025-12-31 (`cut_series`), as `scripts/turning_point_variant.py` already does, and the last three scored days are
left out of the lag (`lag_members`), which is the only place they would need a 2026 spread.

The result in `direct-pairs-result.md` and `evidence/direct_pairs/score.json` is **not edited**. The re-score is published beside it as
`evidence/direct_pairs/score_lag_cut.json` (same declaration, same panel `4ddc3882…`, same walks re-run, same seed).

## How the figures moved

* **No verdict changed, and no published figure.** Every CRPS cell, the primary test (twin gain −0.045 bp, 90% interval
  [−0.080, −0.011], "twin worse"), the calibration table and every best lag are the same as before.
* **The lag tables** use 1870 days instead of 1873 (the last three scored days are dropped): the published model's correlation at k = 2 is 0.679
  instead of 0.680, the twin's 0.626 instead of 0.627; the best lag is still 2 for both.
* **One sentence of the old note no longer holds as written:** the twin's correlation at k = 0 is lower than the published model's by −0.0075, with
  interval [−0.0138, +0.0001], which now just reaches zero (it was [−0.0138, −0.0001]). At k = 1 and 2 the intervals are still below zero.
* **Turning-point days** are 99, not 100: 2025-12-31 was flagged using the 2026-01-02 spread and is now unflagged. The twin's gain over the published
  model there is +0.557 [+0.293, +0.824] (was +0.537 [+0.275, +0.801]); the median is closer by 0.691 [+0.349, +1.049] (was 0.655). Verdicts unchanged.
