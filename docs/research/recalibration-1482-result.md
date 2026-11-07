# Recalibrating the critical and futility values on (s3c-ann-net)'s loss differentials: result (H1 step 4, #1482)

**Development and simulated data, not a verdict.** No locked day is read: the origins end on 2025-12-23. Every figure is read from `docs/research/recalibration-1482/series.json`, `calibration.json` and `power.json` by `scripts/recalibration_1482.py report` (with the records of #878 and #886 beside them). `scoring_protocol.CRITICAL_VALUES`, `FUTILITY_CRITICAL_VALUES`, `B2_LEG_CRITICAL_VALUES` are unchanged by this step, and so is the record in force; `docs/decisions/scoring-protocol.md` gains only a marked draft, "Draft amendment 6", which is not in force until she merges it.

## 1. What was calibrated

Series are the candidate's own, in the orientation the test applies, `d = S(benchmark) - S(candidate)`, on the post-2020 decision days (from 2020-04-03; the cut of 2019-09-18 of #1022 falls before it, so no day is removed). Windows are drawn by the stationary bootstrap, mean block length scoring_protocol.BLOCK_LENGTH, on the post-2020 days (mean block 10, her ruling of 22 October 2026 on #1022), at #886's looks, levels (60 days has no efficacy value, Q-B), windows (20,000 per look; 20,000 for futility) and seed 1.

| leg | series | days | mean d | development skill against the benchmark | Politis-White block (in use: 10) |
|---|---|---|---|---|---|
| B1 | B1 leg: d = S(B1) - S(candidate), grid | 1,429 | 0.3399 | 25.0% | 58.9 |
| B2 | B2 leg: d = S(B2) - S(candidate), grid | 1,429 | 0.9040 | 47.0% | 65.2 |
| B3 | B3 leg: d = S(B3) - S(candidate), B3's five levels | 1,429 | 0.1797 | 15.0% | 13.4 |

## 2. The values, beside the ones in force

Each cell is the critical value `c` of the one-sided bound `mean - c * se` (efficacy) or `skill + c * se` (futility). "In force" is `scoring_protocol` today; "#878" and "#886" are the scratch records of those steps (the benchmarks' own series); "new" is this step.

| value | days | in force | #878 (circular, full history) | #886 (stationary, post-2020) | new (candidate's series) | changes? |
|---|---|---|---|---|---|---|
| efficacy, B1 leg | 125 | 3.419 | 2.548 | 5.710 | 2.431 | differs |
| efficacy, B1 leg | 250 | 2.426 | 1.347 | 3.012 | 1.610 | differs |
| efficacy, B2 leg | 125 | 3.419 | 2.548 | 5.710 | 3.337 | within 5% of the one in force |
| efficacy, B2 leg | 250 | 2.426 | 1.347 | 3.012 | 1.974 | differs |
| efficacy, B3 leg | 125 | 9.501 | 1.434 | 2.267 | 2.604 | differs |
| efficacy, B3 leg | 250 | 5.455 | 1.006 | 1.583 | 1.657 | differs |
| futility (upper bound of skill, B1 leg) | 60 | 1.930 | 2.438 | 2.256 | 3.324 | differs |
| futility (upper bound of skill, B1 leg) | 125 | 1.565 | 2.289 | 2.026 | 2.941 | differs |
| futility (upper bound of skill, B1 leg) | 250 | 1.446 | 2.298 | 1.987 | 2.744 | differs |

A value "differs" when it is more than 5% from the one in force; that threshold is this page's, not the protocol's. **At least one value differs, so the amendment is drafted for her merge** (section 6).

## 3. Size and power at the values in force and at the new ones

`scripts/power_study_769.py`'s rule and paths (2,000 per cell, seed 148204446), on the candidate's B1 leg: a path of 250 days is drawn from the history by the reading's generator, the candidate's skill is set to the stated value by shifting the mean of d (its noise is the candidate's own), and the bound is read at looks 125 and 250 at each set of values. Size is the share of null paths (skill 0) detected by that look; power is the MME-gated share (point skill against B1 at least 3%). The B2 half of Supported is not simulated, so each power is an upper bound. Each figure carries ± 1.96 Monte Carlo standard errors.

Values read: in force 3.419 / 2.426, new 2.431 / 1.610 (125 / 250 days).

| reading | values | size 125 | size 250 | 3% 125 | 3% 250 | 10% 125 | 10% 250 |
|---|---|---|---|---|---|---|---|
| (a) full, circular | in force | 0.0% ± 0.0 | 0.0% ± 0.0 | 0.0% ± 0.0 | 0.0% ± 0.0 | 0.0% ± 0.0 | 0.0% ± 0.0 |
| (a) full, circular | new | 0.0% ± 0.0 | 0.5% ± 0.3 | 0.0% ± 0.0 | 0.9% ± 0.4 | 0.1% ± 0.1 | 2.5% ± 0.7 |
| (b) post-2020-04, circular | in force | 0.0% ± 0.0 | 0.1% ± 0.2 | 0.0% ± 0.0 | 0.2% ± 0.2 | 0.0% ± 0.0 | 1.9% ± 0.6 |
| (b) post-2020-04, circular | new | 0.1% ± 0.1 | 3.0% ± 0.8 | 0.1% ± 0.1 | 5.2% ± 1.0 | 0.6% ± 0.3 | 17.4% ± 1.7 |
| (c) full, stationary | in force | 0.0% ± 0.0 | 0.0% ± 0.0 | 0.0% ± 0.0 | 0.0% ± 0.0 | 0.0% ± 0.0 | 0.1% ± 0.1 |
| (c) full, stationary | new | 0.0% ± 0.0 | 0.7% ± 0.4 | 0.0% ± 0.0 | 1.2% ± 0.5 | 0.3% ± 0.2 | 3.2% ± 0.8 |
| (d) post-2020-04, stationary | in force | 0.0% ± 0.0 | 0.4% ± 0.3 | 0.0% ± 0.0 | 0.6% ± 0.3 | 0.0% ± 0.0 | 2.6% ± 0.7 |
| (d) post-2020-04, stationary | new | 0.2% ± 0.2 | 4.2% ± 0.9 | 0.4% ± 0.3 | 7.0% ± 1.1 | 1.4% ± 0.5 | 18.8% ± 1.7 |

## 4. Power by skill, and the minimum meaningful effect

MME-gated power by 250 days (the confirmation test's last look) on reading (d), post-2020 days with stationary-bootstrap paths, which is the reading the confirmation days resemble, at each skill on the grid. The smallest skill that reaches 80% is shown for every reading.

| skill | power 250, in force | power 250, new | power 125, new |
|---|---|---|---|
| 2% | 0.5% ± 0.3 | 5.9% ± 1.0 | 0.4% ± 0.3 |
| 3% | 0.6% ± 0.3 | 7.0% ± 1.1 | 0.4% ± 0.3 |
| 4% | 0.8% ± 0.4 | 8.6% ± 1.2 | 0.4% ± 0.3 |
| 5% | 1.0% ± 0.4 | 9.8% ± 1.3 | 0.5% ± 0.3 |
| 6% | 1.4% ± 0.5 | 11.6% ± 1.4 | 0.5% ± 0.3 |
| 8% | 1.9% ± 0.6 | 15.2% ± 1.6 | 0.9% ± 0.4 |
| 10% | 2.6% ± 0.7 | 18.8% ± 1.7 | 1.4% ± 0.5 |
| 15% | 5.9% ± 1.0 | 29.5% ± 2.0 | 2.4% ± 0.7 |
| 20% | 11.6% ± 1.4 | 44.0% ± 2.2 | 4.7% ± 0.9 |
| 25% | 19.7% ± 1.7 | 57.5% ± 2.2 | 7.6% ± 1.2 |
| 30% | 30.2% ± 2.0 | 71.0% ± 2.0 | 12.0% ± 1.4 |

| reading | smallest skill on the grid with power at least 80% by 250 days, in force | new |
|---|---|---|
| (a) full, circular | none up to 30% | none up to 30% |
| (b) post-2020-04, circular | none up to 30% | none up to 30% |
| (c) full, stationary | none up to 30% | none up to 30% |
| (d) post-2020-04, stationary | none up to 30% | none up to 30% |

## 5. Marked question for Eleonora: the minimum meaningful effect (#1354, question 2)

**Marked question (protocol section 13; the default applies if she has not answered by the next 5 pm batch).** Her ruling of 6 November 2026 (#1354, question 2, option 2) sets the MME from the power study once the recalibration is in. The study cannot do that by its own rule: on reading (d) with the new values the test's power by 250 days is 7.0% ± 1.1 at 3%, 18.8% ± 1.7 at 10%, 44.0% ± 2.2 at 20%, 57.5% ± 2.2 at 25% and 71.0% ± 2.0 at 30%, so no skill on the grid reaches 80% power. The candidate's own development skill against B1 on these days is 25.0%. Options:

1. Keep 3% (protocol decision 5) and record that the recalibrated test, read as protocol v1 reads it, cannot reach 80% power at 3% by 250 days. Whether the confirmation is longer or read by another test is the confirmation design's (#1394, #1392), not this protocol's. **Recommended and default: changes no claim.**
2. Set the MME to a value she names from the table in section 4, accepting that its power by 250 days is the figure beside it.
3. Change the power target or the horizon of the rule (a different section 13 decision), then read the MME from the study again.

## 6. Draft amendment, and what is not decided

Nothing here is in force. Under protocol section 13 a different value is her decision; `scoring_protocol.py` is not edited by this PR, and the decision record gains only the marked draft below (draft amendment 6). If she adopts the new values, a follow-up directive sets `CRITICAL_VALUES`, `B2_LEG_CRITICAL_VALUES` and `FUTILITY_CRITICAL_VALUES` to the "new" column of section 2, and the amendment below is what she would merge.

> **DRAFT, for Eleonora's merge. Not in force.** Section 5 (critical values): the efficacy and futility values are calibrated on the loss differentials of the candidate `(s3c-ann-net)` against B1, B2 and B3, in the orientation d = S(benchmark) - S(candidate), on post-2020 stationary-bootstrap windows (mean block 10), and take the "new" column of section 2 of `docs/research/recalibration-1482-result.md`.

## 7. What this does not show

- One candidate, one walk. The candidate may change after the ablations; the values are re-run if it does (#1354, question 1).
- The B2 half of Supported and futility stopping are not simulated in section 3, as in #769 and #886. The B2 leg's and the B3 leg's values are calibrated, but their size and power are not simulated.
- The B3 leg uses the days on which the published record has all five leads, scored on B3's five levels with B1 and the candidate read at those levels.
- 2026 days are not read; no day of the lockbox is read.

## 8. Ruling recorded, 6 November 2026: the MME stays at 3% (#1498)

**Dated note, 6 November 2026.** Eleonora ruled on the marked question of section 5 (decision docket, 10:12 am ET, card mme-1490, option 1; relayed on #1482, comment 6688184333): keep the minimum meaningful effect at 3% (protocol decision 5). This note records it and changes nothing else.

- **Power at 3% by 250 days.** On reading (d) with the new values the test's power at 3% by 250 days is 7.0% ± 1.1, and 0.6% ± 0.3 at the values in force (section 4). No skill on the grid reaches 80% power, so 80% power at 3% is out of reach by 250 confirmation days.
- **Length or test.** Whether the confirmation is longer, or read by another test, is left to the confirmation design (#1392, #1394). This ruling does not decide it.
- **Unchanged.** No threshold, critical value or decision record is changed by this note.

## 9. The confirmation's own power governs the MME (#1506)

**Dated note, 7 November 2026 (#1506).** Beside the 250-day figure of section 8, which stays as written. Eleonora ruled (decision docket, 11:14 am ET, card f1504-h5-gate-power, option confirm-design; finding #1504): H1.M4 and the H5 registration are gated on the confirmation design's own size-and-power study (#1392, `docs/research/confirmation-size-power-1392-full-result.md`), not on the 60/125/250-day values of this page, and draft amendment 6 is parked.

- **Which power governs.** The H5 confirmation is read by `docs/decisions/h5-confirmation-design.md`, which supersedes the sequential 60/125/250-day checkpoint design and its critical values for the H5 confirmation only. The 7.0% of section 8 is the power of that superseded design.
- **The confirmation's figures** (rule 6 of the design; development data, not a verdict). At the 3% boundary the pass rate is at most 1.4%. At 10% skill with 500 origins, against B1′* binding with B2 as developed, power is about 32-35% (31.6% under the regime chain, 34.6% under block resampling).
- **The MME stays at 3%.** This ruling does not change it, or any threshold, critical value or block length.
- **Draft amendment 6 is parked,** not proposed for H5: it is marked so in `docs/decisions/scoring-protocol.md`, which she merges.

