# Published figures that used the reversed values (H1 step 4, #873)

**Re-scores nothing.** The values in force (`scoring_protocol.CRITICAL_VALUES`, `FUTILITY_CRITICAL_VALUES`) were
calibrated on S(B2) − S(B1) and, for futility, with B2 as the benchmark (#830). The protocol applies
d = S(B1) − S(candidate) (§5). This page lists each published H-step figure that read a critical or futility value, or a
power or size computed at one, and gives its reading under the values drafted in
`docs/research/protocol-calibration-873/result.json`: **unchanged** or **changes**. No verdict was ever reached with the
values in force (nothing is registered, and no confirmation day is scored), so no verdict changes. A changed reading is a
marked question for Eleonora; none of them is settled here.

| # | published figure | what it read | reading under the corrected values |
|---|---|---|---|
| 1 | `docs/research/protocol-calibration/result.json`, and the null false-detection rates in the log entry for #737 | the values themselves, and their rates on the development history | **changes.** Efficacy 2.55 and 1.35 at 125 and 250 days (grid), 1.43 and 1.01 (B3, five levels); futility 2.44, 2.29 and 2.30 at 60, 125 and 250 days. Null false detections by 250 days become 8.0% (grid) and 6.3% (B3) against 0.9% and 0.0%. Side by side on `orientation-873-result.md`, section 1. |
| 2 | `docs/research/power-study-769-result.md` (#769, PR #791) and its log entry | size and power of the test in force at 125 and 250 days, four readings | **changes.** Re-run on `power-study-873/result.json` (section 2 of the result page). Power at a true 3% by 250 days rises from 0.8% / 7.8% / 1.8% / 13.9% to 8.7% / 24.3% / 11.8% / 30.8% in readings (a) to (d), and size rises with it (0.5% to 5.9% in (a); 10.9% to 26.6% in (d)). Its sentence that "the test as designed is conservative" holds only for the values in force. |
| 3 | `docs/research/power-replay-754-result.md` (#754, PR #792): families a1 and a2, headed "the current test" | power and size by replay and by simulation | **changes (label), figures unchanged as what they are.** a1 and a2 calibrate each pair's values on that pair's own series (#833), so they are not the test in force; its 73% for B3 against B1 is not the power of the test in force. Replayed at the protocol's values instead (section 3 of the result page): B3 against B1 is flagged on 59.0% of windows at the draft grid values and 31.5% at those in force (0.0% at the in-force B3 five-level values, 72.8% at the draft's), and sign-flipped windows are flagged on 14.2% against 2.5%. |
| 4 | `docs/pivot/backfill-h5-726-result.md` (#726): the column "lower (c = 2.426)" | the lower bound of mean d at the 250-day value in force | **unchanged for the headline, changes for six cells.** None of the comparisons of CRPS with and without the history changes sign at c = 1.347. Six of the 40 cells with a lower bound change sign, all of them skill against B1 (2018-19 with and without; 2020 without; 2021-23 with; ordinary days with; tax dates with). Derived from the stored mean and bound (`lower = mean − c · se`); nothing re-scored. |
| 5 | `docs/pivot/h5-splits-805-result.md` (#805 and the finding #798) | c in both orientations, with and without 2019-09-18 | **unchanged.** It already reports both orientations and says the values in force are the B2 − B1 ones; the draft's values are its S(B1) − S(B2) column. |
| 6 | `docs/research/confirmation-design-733-result.md`, `-addendum.md` and `confirmation-design-733.md` (#733) | power and size of each design at the largest-across-pairs value, and in reading (b) at the "B1-B2" entry, which is S(B2) − S(B1) | **changes.** Both readings simulate at values of the reversed orientation (the largest across the four series, and S(B2) − S(B1) alone), so its power and size tables are not those of the test the protocol applies. Not re-run here. |
| 7 | `docs/research/log.md`, entries for #737, #791 and #792 | the figures above, copied | **changes**, as rows 1 to 3; the entries are published records and are not edited. The entry for #873 carries the corrected figures. |
| 8 | `docs/research/power-study-656/` and `power-study-656-addendum.md` (the test before ruling 5) | the old test, which read no calibrated value | **unchanged.** |

## Marked questions for Eleonora

1. **Apply the draft amendment?** `docs/decisions/scoring-protocol.md` carries a draft amendment to ruling 5 and Q-C with the
   new values. It is in force only once she merges it, and `scoring_protocol.py` is then changed by a follow-up directive.
2. **The size of the corrected test.** At the corrected values the test is close to its nominal size under the generator it
   was calibrated on (5.9% by 250 days, reading (a)), but not elsewhere: 9.4% on stationary-bootstrap paths of the full history,
   20% to 27% on the post-2020 history (every confirmation day falls after 2020), and 14% to 26% of sign-flipped windows in the
   replay. Whether the calibration should be revisited, and on which history and generator, is hers (#751, #830).
3. **Rows 3 and 6.** Whether #754 and #733 are re-run on the corrected test is hers; their designs were chosen on a
   test that is not the one the protocol applies.
