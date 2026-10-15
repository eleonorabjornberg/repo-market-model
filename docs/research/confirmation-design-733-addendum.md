# Confirmation design study (#733): a post-hoc addendum

**This is post-hoc.** It was written after `confirmation-design-733.md` was run and its figures were seen, and it is
labelled so wherever it is quoted. It changes none of that document's rule or results, and the recommendation of the
page's §7 reading stays the one that rule gives. The addendum adds two diagnostics that the first figures made
necessary. `scripts/confirmation_design.py addendum` writes `docs/research/confirmation-design-733/addendum.json`, and
`report` renders it below the main result, under a heading that says it is post-hoc.

## Why

1. **The critical value in force is the largest of four orientations, and with it the design in force has almost no
   power.** The first figures put D0 (the design in force) at no power for a true 3% or 10% skill. The directive that
   asked for this study quotes 14% and 19%; those are the figures of PR #695's reading (b), where the critical value is
   the one calibrated on the comparison B2 - B1 alone (2.43 at 250 days), not the largest across pairs (5.45) that
   `scoring_protocol.CRITICAL_VALUES` holds. The two readings are different designs of the same test. The addendum
   re-reads every design of the closed list at reading (b), so that the page shows both and the difference between them
   is not hidden.
2. **Two designs fail size, and the calibration's generator differs from the paths' generator.** D4 and D5 hold their
   size when the null series is drawn the way the critical value was calibrated (circular blocks of 10 days), and
   fail it when drawn by the stationary bootstrap (geometric blocks, mean 10) that the earlier power study used for
   its paths. The addendum measures every design's size under both generators, so that the failure is attributed.

## What it does

- **Reading (b).** The same designs, scenarios, paths (`PATHS`), seeds and gate as the main study, with the critical
  value at looks 2 and 3 replaced by the one calibrated on the pair S(B2) - S(B1) alone, that is the `B1-B2` entry
  of the design's calibration (daily scores `S1 - S2` negated). Nothing is recalibrated. The §7 rule is applied to it
  and its result is reported, with "(reading (b))" in its name.
- **Circular generator.** Size only (DELTA = 0, NOISE = 1, both histories), under the main study's calibrated values,
  with each path built from circular blocks of 10 consecutive days at uniform random starts, cut to N days, as the
  calibration builds its windows. The seeds are the main study's, scenario by scenario.

## What it does not do

It does not change the protocol, the main study's recommendation or any critical value in code. Which of the two
readings the protocol should use is Eleonora's; the question is hers and is asked on the result page.
