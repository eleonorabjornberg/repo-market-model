# Power study of the test in force: result (H1, #769)

**Development data; no verdict.** The rule is `docs/research/power-study-769.md`, committed before the run. The data
is `docs/research/power-study-769/result.json` (`python3 scripts/power_study_769.py check --out docs/research/power-study-769`
reads it back). The test is protocol v1 after ruling 5: calibrated critical values 3.42 at 125 days and 2.43 at 250,
look 1 futility only, the MME gate on the point skill. The B2 half of Supported is not simulated, so every figure is
an upper bound on the full rule's power. 2,000 paths per cell; the Monte Carlo standard error of a share is at most 1
point.

## Power of a true 3% skill against B1 (gated; `NOISE` = 1)

| reading | history | paths drawn by | 125 days | 250 days | size (no true skill), 125 / 250 days |
|---|---|---|---|---|---|
| (a) | full, from 2018-06-29 | circular blocks of 10 (the calibration's own) | 0.2% | 0.8% | 0.2% / 0.5% |
| (b) | post-2020-04 | circular blocks of 10 | 3.1% | 7.8% | 2.7% / 6.1% |
| (c) | full | stationary bootstrap | 0.5% | 1.8% | 0.4% / 1.3% |
| (d) | post-2020-04 (#656's own) | stationary bootstrap | 5.8% | 13.9% | 4.6% / 10.9% |

Reading (d) is the one the committed #656 study used; it reproduces the figures quoted from PR #737 (6.0% by 125 days,
14.0% by 250) within Monte Carlo error (other seeds). No reading reaches the 80% target at either look, so `days_needed`
is `null` in all four.

## Power by true skill, with Monte Carlo intervals, beside #656's figures for the old test

Seed 76902307 (path *i* of every cell is seeded `seed + i`), 2,000 paths per cell in this study; #656's committed study used seed 656 and 400 paths. Each figure is a share of paths; ± is 1.96 × the Monte Carlo standard error `sqrt(p(1-p)/paths)`, so the interval is the share ± that. All cells are `NOISE` = 1. "Old test" is #656's committed result (`docs/research/power-study-656/result.json`, the test as written before ruling 5, reading (d)'s history and generator); it is untouched. Gated power; the B2 half of Supported is not simulated, so each is an upper bound.

| true skill | old test (#656), 125 / 250 days | (a), 125 / 250 | (b), 125 / 250 | (c), 125 / 250 | (d), 125 / 250 |
|---|---|---|---|---|---|
| 3% | 16.2% ± 3.6 / 29.2% ± 4.5 | 0.2% ± 0.2 / 0.8% ± 0.4 | 3.1% ± 0.8 / 7.8% ± 1.2 | 0.5% ± 0.3 / 1.8% ± 0.6 | 5.8% ± 1.0 / 13.9% ± 1.5 |
| 4% | 16.5% ± 3.6 / 30.2% ± 4.5 | 0.2% ± 0.2 / 0.9% ± 0.4 | 3.4% ± 0.8 / 8.6% ± 1.2 | 0.5% ± 0.3 / 2.0% ± 0.6 | 6.0% ± 1.0 / 14.5% ± 1.5 |
| 5% | 17.0% ± 3.7 / 30.5% ± 4.5 | 0.2% ± 0.2 / 1.1% ± 0.5 | 3.5% ± 0.8 / 9.0% ± 1.3 | 0.5% ± 0.3 / 2.2% ± 0.6 | 6.2% ± 1.1 / 15.2% ± 1.6 |
| 6% | 17.8% ± 3.7 / 32.2% ± 4.6 | 0.2% ± 0.2 / 1.4% ± 0.5 | 3.6% ± 0.8 / 9.3% ± 1.3 | 0.6% ± 0.3 / 2.6% ± 0.7 | 6.6% ± 1.1 / 15.8% ± 1.6 |
| 8% | 19.5% ± 3.9 / 35.8% ± 4.7 | 0.3% ± 0.2 / 1.7% ± 0.6 | 4.0% ± 0.9 / 10.5% ± 1.3 | 0.7% ± 0.4 / 3.1% ± 0.8 | 7.0% ± 1.1 / 17.0% ± 1.6 |
| 10% | 19.8% ± 3.9 / 37.2% ± 4.7 | 0.4% ± 0.3 / 2.1% ± 0.6 | 4.3% ± 0.9 / 11.9% ± 1.4 | 0.9% ± 0.4 / 3.7% ± 0.8 | 7.7% ± 1.2 / 19.2% ± 1.7 |

The old test's 60-day look is absent from the new rule (look 1 is futility only), so only 125 and 250 days are compared; the old test's figure at 60 days was 0% (look 1 unresolvable as written). In every reading and at every effect size the new test's power is below the old test's: at 3% and 250 days, 0.8% / 7.8% / 1.8% / 13.9% in (a)-(d) against the old 29.2%. The 6.0% / 14.0% quoted from PR #737 are the new test's, not #656's committed figures for the old test (16.25% by 125 days, 29.25% by 250).

## What can be detected

At `NOISE` = 1 no skill on the grid (3% to 10%) reaches 80% by 250 days in any reading. The best is reading (d) at a
true 10%: 7.7% by 125 days and 19.2% by 250. With a quieter candidate (`NOISE` = 0.25, a candidate that tracks B1 closely)
a true 3% reaches 20.7% by 250 days in reading (d), 14.2% in (b), 4.8% in (c), 2.4% in (a). So the smallest skill
detected within 250 days at the target power is `null` in every reading: the study reports that nothing on the grid can
be.

## What the readings show

1. **The test as designed is conservative.** Under the generator it is calibrated on (a), the test fires on 0.5% of null
   paths by 250 days against the nominal 5%, and detects a true 3% on 0.8%. Its power is low largely because its size is
   far below 5%.
2. **Size depends on the history.** On the post-2020-04 history the same values give 6.1% (circular) and 10.9%
   (stationary) false detections by 250 days, against nominal 5%. The values are calibrated on windows of the full history;
   this study does not test why they do not transfer to the later one (a candidate cause is the 2018-19 days, which
   only the full history holds). This is the size question of #751, now recorded for the test in force.
3. **Power barely depends on the true skill.** Moving the true skill from 3% to 10% adds under 6 points of power in the
   best reading. The spread of `d` (the B1 − B2 daily noise) is large next to a 3% mean shift, which is why the
   critical values, not the skill, decide the outcome.
4. **The gate did not bind.** Gated and ungated shares are equal in every cell: every simulated detection also had a
   point skill of at least 3%.

## Not checked

- The B2 half of Supported, B3's five-level comparison, and futility stopping (non-binding, so it cannot change a
  detection). The 60-day look is futility only and detects nothing by construction.
- Any history before 2018-06-29, and any day after 2026-09-03.
- A candidate with the structure of a real forecaster: `d` is borrowed from B1 − B2, as in #656.

## For Eleonora

Settled after this result, not before (her ruling on #769): the MME, B3's verdict rule (#768), and the confirmation
design (#754, #733). Which reading is the test's power (a calibration generator on the full history, or the replay on
the post-2020 history), the 80% target, and whether item 5's calibration should be revisited given the size in (b)
and (d) are hers; nothing here changes the protocol, and a change needs §13 evidence and her attested action.
